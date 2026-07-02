"""Pydantic schemas for URL endpoints."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl, field_validator


class ShortenRequest(BaseModel):
    """Request body for POST /v1/shorten."""

    long_url: HttpUrl = Field(
        ...,
        description="URL gốc cần rút gọn (phải bắt đầu bằng http:// hoặc https://)",
        examples=["https://www.example.com/very/long/path?param=value"],
    )
    custom_alias: str | None = Field(
        default=None,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="Alias tùy chỉnh (3-50 ký tự, chỉ gồm chữ, số, gạch dưới, gạch ngang)",
        examples=["my-article"],
    )
    expires_in_days: int | None = Field(
        default=None,
        ge=1,
        le=3650,
        description="Số ngày tồn tại (1-3650). Để trống = không hết hạn",
        examples=[30],
    )

    @field_validator("long_url", mode="before")
    @classmethod
    def validate_not_localhost(cls, v: str) -> str:
        """Ngăn SSRF — không cho phép URL trỏ đến localhost hoặc internal IP."""
        url_str = str(v).lower()

        # XSS basic prevention
        if url_str.startswith(("javascript:", "vbscript:", "data:")):
            raise ValueError("URL scheme không được phép (nguy cơ XSS).")

        blocked = ["localhost", "127.0.0.1", "0.0.0.0", "::1"]
        # Chặn private IP ranges
        private_prefixes = [
            "192.168.",
            "10.",
            "172.16.",
            "172.17.",
            "172.18.",
            "172.19.",
            "172.2",
            "172.3",
            "172.4",
            "172.5",
            "172.6",
            "172.7",
            "172.8",
            "172.9",
            "172.30",
            "172.31",
        ]
        for blocked_host in blocked:
            if blocked_host in url_str:
                raise ValueError("URL trỏ đến địa chỉ nội bộ không được phép.")
        for prefix in private_prefixes:
            if prefix in url_str:
                raise ValueError("URL trỏ đến địa chỉ IP nội bộ không được phép.")

        # Domain blacklist check
        from app.config import get_settings

        settings = get_settings()
        for domain in settings.blacklisted_domains:
            if domain in url_str:
                raise ValueError(f"URL chứa domain không được phép: {domain}")

        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "long_url": "https://www.example.com/very/long/path/to/article?param=value",
                "custom_alias": "my-article",
                "expires_in_days": 30,
            }
        }
    }


class ShortenResponse(BaseModel):
    """Response body for POST /v1/shorten."""

    short_code: str
    short_url: str
    long_url: str
    expires_at: datetime | None = None
    created_at: datetime

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "short_code": "my-article",
                "short_url": "http://localhost:8000/my-article",
                "long_url": "https://www.example.com/very/long/path",
                "expires_at": None,
                "created_at": "2025-01-16T08:30:00Z",
            }
        },
    }


class URLDetailResponse(ShortenResponse):
    """Detailed URL response including metadata."""

    id: uuid.UUID
    title: str | None = None
    is_active: bool
    user_id: uuid.UUID | None = None

    model_config = {"from_attributes": True}


class URLListResponse(BaseModel):
    """Paginated list of URLs."""

    items: list[URLDetailResponse]
    total: int
    page: int
    page_size: int
    has_next: bool
