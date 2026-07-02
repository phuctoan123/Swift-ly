"""Core business logic for URL shortening operations."""

import secrets
import string
from datetime import UTC, datetime, timedelta

import httpx
import redis.asyncio as aioredis
import structlog
from bs4 import BeautifulSoup
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.url import URL

log = structlog.get_logger()
settings = get_settings()

# Base62 character set: a-z, A-Z, 0-9
BASE62_CHARS = string.ascii_letters + string.digits  # 62 ký tự


# ── Short Code Generation ──────────────────────────────────────────────────────


def generate_short_code(length: int | None = None) -> str:
    """
    Sinh chuỗi ngẫu nhiên Base62 với độ dài cho trước.

    Dùng secrets.choice() thay random.choice() để đảm bảo
    cryptographic randomness — quan trọng cho security.

    Args:
        length: Số ký tự (mặc định lấy từ settings).

    Returns:
        Chuỗi Base62 ngẫu nhiên.

    Examples:
        >>> code = generate_short_code()
        >>> len(code) == 7
        True
        >>> all(c in BASE62_CHARS for c in code)
        True
    """
    if length is None:
        length = settings.short_code_length
    return "".join(secrets.choice(BASE62_CHARS) for _ in range(length))


def validate_url(url: str) -> bool:
    """
    Kiểm tra URL có hợp lệ không (http hoặc https scheme).

    Args:
        url: URL string cần kiểm tra.

    Returns:
        True nếu hợp lệ, False nếu không.
    """
    url_stripped = url.strip()
    return url_stripped.startswith(("http://", "https://")) and len(url_stripped) > 10


# ── Background Tasks ───────────────────────────────────────────────────────────


async def fetch_page_title(short_code: str, long_url: str) -> None:
    """Fetch trang gốc để lấy thẻ <title> lưu vào DB."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(long_url, follow_redirects=True)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                title_tag = soup.find("title")
                if title_tag and title_tag.string:
                    title = title_tag.string.strip()[:255]
                    # Lưu vào DB
                    from app.database import AsyncSessionLocal

                    async with AsyncSessionLocal() as session:
                        stmt = select(URL).where(URL.short_code == short_code)
                        result = await session.execute(stmt)
                        url_record = result.scalar_one_or_none()
                        if url_record:
                            url_record.title = title
                            await session.commit()
    except Exception as e:
        log.warning(
            "fetch_title_failed", short_code=short_code, url=long_url, error=str(e)
        )


# ── Database Operations ────────────────────────────────────────────────────────


async def get_url_by_code(
    db: AsyncSession,
    redis: aioredis.Redis,
    short_code: str,
) -> URL | None:
    """
    Tra cứu URL theo short_code.
    Tích hợp Redis cache:
    1. Trả về ngay nếu có cache (hit).
    2. Trả về None nếu có negative cache.
    3. Query DB nếu miss, sau đó lưu cache.
    """
    cache_key = f"url:{short_code}"

    # 1. Thử đọc từ cache
    try:
        cached = await redis.get(cache_key)
        if cached == "NOT_FOUND":
            return None
        if cached:
            # Mock lại một object URL từ cache string (vì router chỉ cần long_url)
            # Tuy nhiên, ta trả ra một dummy URL để tiện, hoặc return dict.
            # Tốt nhất là serialize/deserialize đúng chuẩn.
            # Dành cho MVP, ta trả về dummy URL chỉ chứa long_url.
            return URL(short_code=short_code, long_url=cached)
    except Exception as e:
        log.warning("redis_cache_read_error", error=str(e))

    # 2. Query DB
    now = datetime.now(UTC)
    stmt = select(URL).where(
        URL.short_code == short_code,
        URL.is_active.is_(True),
        (URL.expires_at.is_(None)) | (URL.expires_at > now),
    )
    result = await db.execute(stmt)
    url_record = result.scalar_one_or_none()

    # 3. Lưu cache
    try:
        if url_record:
            await redis.setex(
                cache_key, settings.redis_ttl_seconds, url_record.long_url
            )
        else:
            await redis.setex(
                cache_key, settings.redis_negative_ttl_seconds, "NOT_FOUND"
            )
    except Exception as e:
        log.warning("redis_cache_write_error", error=str(e))

    return url_record


async def create_short_url(
    db: AsyncSession,
    long_url: str,
    custom_alias: str | None = None,
    expires_in_days: int | None = None,
    user_id=None,
) -> URL:
    """
    Tạo URL ngắn mới trong database.

    Chiến lược:
    - Nếu custom_alias được cung cấp: kiểm tra conflict và dùng nó.
    - Nếu không: sinh short_code ngẫu nhiên, retry tối đa MAX_RETRIES lần
      nếu gặp IntegrityError (collision).

    Args:
        db: Database session.
        long_url: URL gốc cần rút gọn.
        custom_alias: Alias tùy chỉnh (None = tự động sinh).
        expires_in_days: Số ngày tồn tại (None = không hết hạn).
        user_id: UUID của user sở hữu URL (None = anonymous).

    Returns:
        URL record vừa được tạo.

    Raises:
        ValueError: Nếu custom_alias đã tồn tại.
        RuntimeError: Nếu không thể sinh short_code sau MAX_RETRIES lần.
    """
    # Tính expires_at
    expires_at: datetime | None = None
    if expires_in_days is not None:
        expires_at = datetime.now(UTC) + timedelta(days=expires_in_days)

    # ── Case 1: Custom alias ───────────────────────────────────────────────────
    if custom_alias:
        # Kiểm tra alias chưa bị dùng
        existing = await db.execute(select(URL).where(URL.short_code == custom_alias))
        if existing.scalar_one_or_none() is not None:
            log.warning("custom_alias_conflict", alias=custom_alias)
            raise ValueError(f"Custom alias '{custom_alias}' đã được sử dụng.")

        url_record = URL(
            short_code=custom_alias,
            long_url=long_url,
            user_id=user_id,
            custom_alias=custom_alias,
            expires_at=expires_at,
        )
        db.add(url_record)
        await db.commit()
        await db.refresh(url_record)
        log.info("url_created", short_code=custom_alias, custom_alias=True)
        return url_record

    # ── Case 2: Auto-generated short code với collision retry ──────────────────
    max_retries = settings.short_code_max_retries
    code_length = settings.short_code_length

    for attempt in range(max_retries):
        # Tăng độ dài nếu collision liên tục (hệ thống đang gần đầy)
        current_length = code_length if attempt < 3 else code_length + 1
        short_code = generate_short_code(length=current_length)

        url_record = URL(
            short_code=short_code,
            long_url=long_url,
            user_id=user_id,
            expires_at=expires_at,
        )

        try:
            db.add(url_record)
            await db.commit()
            await db.refresh(url_record)
            log.info(
                "url_created",
                short_code=short_code,
                attempt=attempt + 1,
                custom_alias=False,
            )
            return url_record
        except IntegrityError:
            await db.rollback()
            log.warning(
                "short_code_collision",
                short_code=short_code,
                attempt=attempt + 1,
            )
            continue

    raise RuntimeError(
        f"Không thể tạo short code sau {max_retries} lần thử. Vui lòng thử lại sau."
    )


async def deactivate_url(
    db: AsyncSession,
    redis: aioredis.Redis,
    short_code: str,
    user_id=None,
) -> URL | None:
    """Soft delete: đánh dấu URL là inactive."""
    stmt = select(URL).where(URL.short_code == short_code, URL.is_active.is_(True))
    if user_id is not None:
        stmt = stmt.where(URL.user_id == user_id)

    result = await db.execute(stmt)
    url_record = result.scalar_one_or_none()

    if url_record is None:
        return None

    url_record.is_active = False
    await db.commit()
    await db.refresh(url_record)

    # Invalidate cache
    try:
        await redis.delete(f"url:{short_code}")
    except Exception as e:
        log.warning("redis_cache_delete_error", error=str(e))

    log.info("url_deactivated", short_code=short_code)
    return url_record


async def get_user_urls(
    db: AsyncSession, user_id: str, limit: int = 50, offset: int = 0
) -> tuple[list[URL], int]:
    """Lấy danh sách URL của user có phân trang."""
    # Count
    from sqlalchemy import func

    count_stmt = select(func.count(URL.id)).where(
        URL.user_id == user_id, URL.is_active.is_(True)
    )
    total = await db.scalar(count_stmt) or 0

    # Fetch items
    stmt = (
        select(URL)
        .where(URL.user_id == user_id, URL.is_active.is_(True))
        .order_by(URL.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    items = list(result.scalars().all())

    return items, total
