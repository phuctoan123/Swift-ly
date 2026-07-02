"""SQLAlchemy User model."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    """
    Bảng users — lưu tài khoản người dùng.

    Columns:
        id              : UUID primary key (auto-generated)
        email           : Email duy nhất, dùng để đăng nhập
        username        : Username duy nhất, hiển thị công khai
        hashed_password : Mật khẩu đã hash bằng bcrypt
        is_active       : Tài khoản còn hoạt động không
        is_verified     : Email đã xác thực chưa
        created_at      : Thời điểm tạo
        updated_at      : Thời điểm cập nhật lần cuối
    """

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="UUID primary key",
    )
    email: Mapped[str] = mapped_column(
        String(320),
        nullable=False,
        unique=True,
        index=True,
        comment="Email address (unique)",
    )
    username: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
        comment="Public username (unique)",
    )
    hashed_password: Mapped[str] = mapped_column(
        String,
        nullable=False,
        comment="bcrypt hashed password",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="Account is active",
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Email has been verified",
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
        return f"<User id={self.id} username={self.username!r}>"
