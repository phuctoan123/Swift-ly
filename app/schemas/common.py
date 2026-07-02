"""Common Pydantic schemas shared across the application."""

from datetime import datetime

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Standard error response format for all endpoints."""

    error: str
    message: str
    field: str | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "error": "URL_NOT_FOUND",
                "message": "URL ngắn không tồn tại hoặc đã hết hạn.",
            }
        }
    }


class DependencyStatus(BaseModel):
    """Status of a single dependency."""

    status: str  # "healthy" | "unhealthy"
    latency_ms: float | None = None
    error: str | None = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    timestamp: datetime
    uptime_seconds: float | None = None
    dependencies: dict[str, str]

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "healthy",
                "version": "0.1.0",
                "timestamp": "2025-01-16T08:30:00Z",
                "dependencies": {
                    "database": "healthy",
                    "redis": "healthy",
                },
            }
        }
    }
