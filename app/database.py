"""Database engine and session factory using SQLAlchemy async."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

settings = get_settings()

# ── Engine ─────────────────────────────────────────────────────────────────────
engine = create_async_engine(
    settings.database_url,
    echo=settings.is_development,  # Log SQL queries trong dev
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Kiểm tra connection còn sống trước khi dùng
)

# ── Session Factory ────────────────────────────────────────────────────────────
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Tránh lazy loading sau commit
    autocommit=False,
    autoflush=False,
)


# ── Declarative Base ───────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    """Base class cho tất cả SQLAlchemy models."""

    pass


# ── Helper ─────────────────────────────────────────────────────────────────────
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Async generator tạo database session cho mỗi request.
    Tự động đóng session sau khi request hoàn thành.
    Dùng với FastAPI Depends().
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
