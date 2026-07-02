"""Rate limiting dependency using Redis."""

import structlog
from fastapi import Request, HTTPException, status
import redis.asyncio as aioredis

from app.dependencies import get_redis_client

log = structlog.get_logger()

class RateLimiter:
    """
    Fixed window rate limiter using Redis.
    """
    def __init__(self, times: int, seconds: int):
        self.times = times
        self.seconds = seconds

    async def __call__(self, request: Request):
        try:
            redis: aioredis.Redis = await get_redis_client()
        except Exception as e:
            log.warning("rate_limit_redis_failed", error=str(e))
            return  # Fail open if Redis is down
            
        # Get client IP or user ID if authenticated
        client_ip = request.client.host if request.client else "127.0.0.1"
        user_id = "anon"
        if hasattr(request.state, "user") and request.state.user:
            user_id = str(request.state.user.id)
            
        key = f"rate_limit:{request.url.path}:{user_id}:{client_ip}"
        
        try:
            current = await redis.incr(key)
            if current == 1:
                await redis.expire(key, self.seconds)
                
            if current > self.times:
                ttl = await redis.ttl(key)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={"error": "RATE_LIMIT_EXCEEDED", "message": "Quá nhiều request, vui lòng thử lại sau."},
                    headers={"Retry-After": str(ttl if ttl > 0 else self.seconds)},
                )
        except HTTPException:
            raise
        except Exception as e:
            log.warning("rate_limit_error", error=str(e))
            # Fail open
