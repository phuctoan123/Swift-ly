"""Analytics API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as aioredis
import json

from app.database import get_async_session
from app.dependencies import get_current_user, get_redis_client
from app.models.url import URL, URLStats, ClickEvent
from app.models.user import User

router = APIRouter(prefix="/v1/urls", tags=["Analytics"])


from app.dependencies import get_optional_user

@router.get("/{short_code}/stats", summary="Lấy thống kê URL")
async def get_url_stats(
    short_code: str,
    db: AsyncSession = Depends(get_async_session),
    redis: aioredis.Redis = Depends(get_redis_client),
    user: User | None = Depends(get_optional_user),
):
    """
    Trả về thống kê click cho URL.
    - URL ẩn danh: Ai cũng xem được.
    - URL có chủ sở hữu: Chỉ owner mới xem được.
    """
    # 1. Verify ownership
    stmt = select(URL).where(URL.short_code == short_code)
    result = await db.execute(stmt)
    url_record = result.scalar_one_or_none()
    
    if not url_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "URL_NOT_FOUND", "message": "Không tìm thấy URL"},
        )
        
    if url_record.user_id is not None:
        if not user or url_record.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": "UNAUTHORIZED", "message": "Không có quyền truy cập thống kê của URL này"},
            )
        
    # 2. Lấy cache statistics (tuỳ chọn MVP)
    # Vì MVP ta sẽ đếm trực tiếp từ db
    
    # Tổng clicks
    count_stmt = select(func.count(ClickEvent.id)).where(ClickEvent.short_code == short_code)
    total_clicks = await db.scalar(count_stmt) or 0
    
    # Gom nhóm theo thiết bị
    device_stmt = select(ClickEvent.device_type, func.count(ClickEvent.id)).where(ClickEvent.short_code == short_code).group_by(ClickEvent.device_type)
    device_result = await db.execute(device_stmt)
    devices = {str(k): v for k, v in device_result.all()}
    
    # Gom nhóm theo quốc gia
    country_stmt = select(ClickEvent.country_code, func.count(ClickEvent.id)).where(ClickEvent.short_code == short_code).group_by(ClickEvent.country_code)
    country_result = await db.execute(country_stmt)
    countries = {str(k): v for k, v in country_result.all() if k}
    
    return {
        "short_code": short_code,
        "total_clicks": total_clicks,
        "devices": devices,
        "countries": countries,
    }
