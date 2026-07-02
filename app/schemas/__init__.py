"""Pydantic schemas package."""

from app.schemas.common import ErrorResponse, HealthResponse
from app.schemas.url import (
    ShortenRequest,
    ShortenResponse,
    URLDetailResponse,
    URLListResponse,
)

__all__ = [
    "ErrorResponse",
    "HealthResponse",
    "ShortenRequest",
    "ShortenResponse",
    "URLDetailResponse",
    "URLListResponse",
]
