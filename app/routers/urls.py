"""URL router — shorten, redirect, and management endpoints."""

import redis.asyncio as aioredis
import structlog
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.rate_limit import RateLimiter
from app.database import get_async_session
from app.dependencies import get_current_user, get_optional_user, get_redis_client
from app.models.user import User
from app.schemas.common import ErrorResponse
from app.schemas.url import (
    ShortenRequest,
    ShortenResponse,
    URLListResponse,
)
from app.services import url_service

router = APIRouter()
log = structlog.get_logger()
settings = get_settings()

shorten_rate_limit = RateLimiter(times=50, seconds=3600)  # 50 req/hour


# ── POST /v1/shorten ───────────────────────────────────────────────────────────
@router.post(
    "/v1/shorten",
    response_model=ShortenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo URL ngắn",
    dependencies=[Depends(shorten_rate_limit)],
    description=(
        "Nhận URL dài và trả về URL ngắn tương ứng.\n\n"
        "- Không cần đăng nhập (anonymous users được phép).\n"
        "- Hỗ trợ custom alias và expiration date.\n"
        "- Nếu custom alias bị trùng → trả về 409 Conflict."
    ),
    responses={
        201: {"description": "URL created successfully"},
        409: {
            "description": "Custom alias already taken",
            "model": ErrorResponse,
        },
        422: {
            "description": "Invalid URL or request body",
            "model": ErrorResponse,
        },
    },
)
async def shorten_url(
    request_body: ShortenRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_session),
    redis: aioredis.Redis = Depends(get_redis_client),
    user: User | None = Depends(get_optional_user),
) -> ShortenResponse:
    """
    Tạo URL ngắn mới.

    Luồng xử lý:
    1. Validate URL (Pydantic HttpUrl + SSRF check)
    2. Nếu custom_alias → check conflict
    3. Sinh short_code Base62 (retry nếu collision)
    4. Lưu vào PostgreSQL
    5. Trả về ShortenResponse với short_url đầy đủ
    """
    long_url = str(request_body.long_url)

    try:
        url_record = await url_service.create_short_url(
            db=db,
            long_url=long_url,
            custom_alias=request_body.custom_alias,
            expires_in_days=request_body.expires_in_days,
            user_id=user.id if user else None,
        )

        # Warm cache
        try:
            await redis.setex(
                f"url:{url_record.short_code}",
                settings.redis_ttl_seconds,
                url_record.long_url,
            )
        except Exception as e:
            log.warning("redis_cache_write_error", error=str(e))

        # Add background task
        background_tasks.add_task(
            url_service.fetch_page_title, url_record.short_code, long_url
        )
    except ValueError as e:
        # Custom alias conflict
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "ALIAS_CONFLICT",
                "message": str(e),
            },
        ) from e
    except RuntimeError as e:
        log.error("short_code_generation_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "SERVICE_UNAVAILABLE",
                "message": str(e),
            },
        ) from e

    short_url = f"{settings.base_url}/{url_record.short_code}"

    log.info(
        "url_shortened",
        short_code=url_record.short_code,
        request_id=getattr(request.state, "request_id", None),
    )

    return ShortenResponse(
        short_code=url_record.short_code,
        short_url=short_url,
        long_url=url_record.long_url,
        expires_at=url_record.expires_at,
        created_at=url_record.created_at,
    )


# ── GET /{short_code} ──────────────────────────────────────────────────────────
@router.get(
    "/{short_code}",
    summary="Redirect tới URL gốc",
    description=(
        "Tra cứu short_code và redirect HTTP 302 về URL gốc.\n\n"
        "- Đây là endpoint hot nhất — được tối ưu cho < 100ms latency.\n"
        "- Phase 2: sẽ thêm Redis cache lookup trước DB.\n"
        "- Click event được ghi async (Phase 2)."
    ),
    response_class=RedirectResponse,
    responses={
        302: {"description": "Redirect to original URL"},
        404: {
            "description": "Short code not found or expired",
            "model": ErrorResponse,
        },
    },
    include_in_schema=True,
)
async def redirect_url(
    short_code: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_session),
    redis: aioredis.Redis = Depends(get_redis_client),
) -> RedirectResponse:
    """
    Redirect đến URL gốc.
    """
    url_record = await url_service.get_url_by_code(
        db=db, redis=redis, short_code=short_code
    )

    if url_record is None:
        log.info(
            "url_not_found",
            short_code=short_code,
            request_id=getattr(request.state, "request_id", None),
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "URL_NOT_FOUND",
                "message": "URL ngắn không tồn tại hoặc đã hết hạn.",
            },
        )

    # Publish click event to Redis Stream async
    try:
        import json
        from datetime import UTC, datetime

        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        referer = request.headers.get("referer")

        event_data = {
            "short_code": short_code,
            "ip_address": client_ip or "",
            "user_agent": user_agent or "",
            "referer": referer or "",
            "clicked_at": datetime.now(UTC).isoformat(),
        }
        await redis.xadd("url_click_stream", {"data": json.dumps(event_data)})
    except Exception as e:
        log.warning("redis_stream_publish_error", error=str(e))

    log.info(
        "url_redirected",
        short_code=short_code,
        cache_hit=False,  # Phase 2: True khi dùng Redis
        request_id=getattr(request.state, "request_id", None),
    )

    return RedirectResponse(
        url=url_record.long_url,
        status_code=status.HTTP_302_FOUND,
    )


# ── GET /v1/urls ───────────────────────────────────────────────────────────────
@router.get(
    "/v1/urls",
    response_model=URLListResponse,
    summary="Danh sách URLs của user",
)
async def list_urls(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_user),
):
    """Lấy danh sách URL đã tạo của người dùng."""
    items, total = await url_service.get_user_urls(db, str(user.id), limit, offset)
    return {
        "items": items,
        "total": total,
        "page": (offset // limit) + 1 if limit > 0 else 1,
        "page_size": limit,
        "has_next": offset + limit < total,
    }


# ── DELETE /v1/urls/{short_code} ───────────────────────────────────────────────
@router.delete(
    "/v1/urls/{short_code}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xoá URL",
)
async def delete_url(
    short_code: str,
    db: AsyncSession = Depends(get_async_session),
    redis: aioredis.Redis = Depends(get_redis_client),
    user: User = Depends(get_current_user),
):
    """Xoá URL (Soft delete) và xoá cache."""
    record = await url_service.deactivate_url(db, redis, short_code, str(user.id))
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "URL_NOT_FOUND",
                "message": "URL không tìm thấy hoặc bạn không có quyền",
            },
        )
