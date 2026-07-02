"""Health check router."""

import time
from datetime import UTC, datetime

import structlog
from fastapi import APIRouter, Depends, Response
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_async_session
from app.dependencies import get_redis_client
from app.schemas.common import HealthResponse

router = APIRouter()
log = structlog.get_logger()

# Thời điểm app khởi động (để tính uptime)
_start_time = time.time()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description=(
        "Kiểm tra trạng thái hoạt động của API và các dependency (DB, Redis).\n\n"
        "Dùng bởi load balancer để xác định instance có sẵn sàng nhận traffic."
    ),
    responses={
        200: {"description": "Service is healthy"},
        503: {"description": "Service is degraded"},
    },
)
async def health_check(
    response: Response,
    db: AsyncSession = Depends(get_async_session),
) -> HealthResponse:
    """
    Kiểm tra kết nối tới Database và Redis.
    Trả về status tổng thể và trạng thái từng dependency.
    """
    dependencies: dict[str, str] = {}
    overall_healthy = True

    # ── Database check ─────────────────────────────────────────────────────────
    try:
        await db.execute(text("SELECT 1"))
        dependencies["database"] = "healthy"
    except Exception as e:
        log.error("health_check_db_failed", error=str(e))
        dependencies["database"] = "unhealthy"
        overall_healthy = False

    # ── Redis check ────────────────────────────────────────────────────────────
    try:
        redis = await get_redis_client()
        await redis.ping()
        dependencies["redis"] = "healthy"
    except Exception as e:
        log.warning("health_check_redis_failed", error=str(e))
        dependencies["redis"] = "unhealthy"
        # Redis không available không làm crash app (degraded state)

    settings = get_settings()

    response.status_code = 200 if overall_healthy else 503
    
    return HealthResponse(
        status="healthy" if overall_healthy else "degraded",
        version=settings.app_version,
        timestamp=datetime.now(UTC),
        uptime_seconds=round(time.time() - _start_time, 2),
        dependencies=dependencies,
    )
