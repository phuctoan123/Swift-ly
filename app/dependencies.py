"""Dependency injection functions for FastAPI."""

from collections.abc import AsyncGenerator
from typing import Annotated

import redis.asyncio as aioredis
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.database import get_async_session

# ── Type Aliases ───────────────────────────────────────────────────────────────
DBSession = Annotated[AsyncSession, Depends(get_async_session)]
AppSettings = Annotated[Settings, Depends(get_settings)]

# ── Redis ──────────────────────────────────────────────────────────────────────
_redis_client: aioredis.Redis | None = None


async def get_redis_client() -> aioredis.Redis:
    """
    Trả về Redis client dùng chung (singleton).
    Client được tạo lần đầu khi gọi, sau đó tái dùng.
    """
    global _redis_client
    if _redis_client is None:
        settings = get_settings()
        _redis_client = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis_client


async def close_redis_client() -> None:
    """Đóng Redis connection khi app shutdown."""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None


RedisClient = Annotated[aioredis.Redis, Depends(get_redis_client)]


# ── DB Session (re-export for convenience) ─────────────────────────────────────
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Alias của get_async_session — dùng trong Depends()."""
    async with __import__("app.database", fromlist=["AsyncSessionLocal"]).AsyncSessionLocal() as session:  # noqa: E501
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ── Auth ───────────────────────────────────────────────────────────────────────
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException
from jose import jwt, JWTError
import uuid

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login", auto_error=False)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_session),
    settings: Settings = Depends(get_settings),
) -> __import__("app.models.user").models.user.User:
    if not token:
        raise HTTPException(status_code=401, detail={"error": "NOT_AUTHENTICATED", "message": "Vui lòng đăng nhập"})
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail={"error": "INVALID_TOKEN", "message": "Token không hợp lệ"})
    except JWTError:
        raise HTTPException(status_code=401, detail={"error": "INVALID_TOKEN", "message": "Token không hợp lệ hoặc đã hết hạn"})
    
    from app.models.user import User
    from sqlalchemy import select
    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalars().first()
    if user is None:
        raise HTTPException(status_code=401, detail={"error": "USER_NOT_FOUND", "message": "Tài khoản không tồn tại"})
    if not user.is_active:
        raise HTTPException(status_code=400, detail={"error": "INACTIVE_USER", "message": "Tài khoản đã bị khoá"})
    return user


async def get_optional_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_session),
    settings: Settings = Depends(get_settings),
) -> __import__("app.models.user").models.user.User | None:
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        return None
        
    from app.models.user import User
    from sqlalchemy import select
    try:
        result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
        user = result.scalars().first()
        if user and user.is_active:
            return user
    except Exception:
        pass
    return None
