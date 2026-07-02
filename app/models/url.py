"""SQLAlchemy models for URL, ClickEvent, and URLStats."""

import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class URL(Base):
    """
    Bảng urls — bảng trung tâm lưu trữ URL.

    Đây là bảng hot nhất trong hệ thống.
    short_code lookup phải cực kỳ nhanh → UNIQUE index.
    """

    __tablename__ = "urls"

    # NOTE: CheckConstraint và partial index dùng PostgreSQL syntax (~, NOW())
    # được định nghĩa trong Alembic migration thay vì model
    # để tránh lỗi khi chạy tests với SQLite.
    # Validation short_code được thực hiện ở Pydantic layer (ShortenRequest).
    __table_args__ = ()

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    short_code: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        unique=True,
        index=True,
        comment="Short URL code (e.g. 'x7Kp2m')",
    )
    long_url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Original long URL",
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Owner user ID (NULL for anonymous)",
    )
    custom_alias: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Custom alias requested by user",
    )
    title: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Auto-fetched page title",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="URL is active (soft delete flag)",
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Expiration timestamp (NULL = never expires)",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"<URL short_code={self.short_code!r} long_url={self.long_url[:50]!r}>"


class ClickEvent(Base):
    """
    Bảng click_events — raw analytics data.

    Lưu từng lượt click riêng lẻ.
    Trong Phase 4 sẽ chuyển sang TimescaleDB hypertable.
    """

    __tablename__ = "click_events"

    __table_args__ = (
        Index(
            "idx_click_events_short_code",
            "short_code",
            "clicked_at",
            postgresql_ops={"clicked_at": "DESC"},
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )
    short_code: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Short code that was clicked",
    )
    clicked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    ip_address: Mapped[str | None] = mapped_column(
        String(45),   # IPv4 max 15 chars, IPv6 max 45 chars
        nullable=True,
    )
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    referer: Mapped[str | None] = mapped_column(Text, nullable=True)
    country_code: Mapped[str | None] = mapped_column(String(2), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    device_type: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="mobile | desktop | tablet",
    )
    browser: Mapped[str | None] = mapped_column(String(50), nullable=True)
    os: Mapped[str | None] = mapped_column(String(50), nullable=True)

    def __repr__(self) -> str:
        return f"<ClickEvent short_code={self.short_code!r} at={self.clicked_at}>"


class URLStats(Base):
    """
    Bảng url_stats — aggregated statistics.

    Tổng hợp click data theo ngày để tăng tốc dashboard queries.
    Thay vì aggregate trực tiếp trên click_events (chậm),
    cron job chạy hằng ngày để tính toán và lưu vào đây.
    """

    __tablename__ = "url_stats"

    __table_args__ = (
        Index(
            "idx_url_stats_short_code",
            "short_code",
            "stat_date",
            postgresql_ops={"stat_date": "DESC"},
        ),
    )

    short_code: Mapped[str] = mapped_column(
        String(20),
        primary_key=True,
        comment="Short code reference",
    )
    stat_date: Mapped[datetime] = mapped_column(
        Date,
        primary_key=True,
        comment="Date of aggregation (YYYY-MM-DD)",
    )
    total_clicks: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0
    )
    unique_ips: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0
    )
    mobile_clicks: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0
    )
    desktop_clicks: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0
    )
    top_countries: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        comment='{"VN": 150, "US": 80}',
    )
    top_referers: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        comment='{"google.com": 200}',
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"<URLStats short_code={self.short_code!r} date={self.stat_date}>"
