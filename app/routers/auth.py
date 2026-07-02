"""Authentication router."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from app.database import get_async_session
from app.schemas.auth import Token, UserCreate, UserResponse
from app.services import auth_service

router = APIRouter(prefix="/v1/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_async_session),
) -> Any:
    """Đăng ký tài khoản mới."""
    user = await auth_service.create_user(db, user_in)
    return user


@router.post("/login", response_model=Token)
async def login(
    db: AsyncSession = Depends(get_async_session),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    Đăng nhập lấy JWT access token và refresh token.
    OAuth2PasswordRequestForm mặc định nhận 'username' nhưng ta có thể dùng nó như email.
    """
    # Tìm user qua email hoặc username
    user = await auth_service.get_user_by_email(db, email=form_data.username)
    if not user:
        user = await auth_service.get_user_by_username(db, username=form_data.username)
        
    if not user:
        raise HTTPException(
            status_code=400,
            detail={"error": "INVALID_CREDENTIALS", "message": "Sai tài khoản hoặc mật khẩu"},
        )
        
    if not auth_service.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=400,
            detail={"error": "INVALID_CREDENTIALS", "message": "Sai tài khoản hoặc mật khẩu"},
        )
        
    if not user.is_active:
        raise HTTPException(
            status_code=400,
            detail={"error": "INACTIVE_USER", "message": "Tài khoản đã bị khoá"},
        )

    return {
        "access_token": auth_service.create_access_token(user.id),
        "refresh_token": auth_service.create_refresh_token(user.id),
        "token_type": "bearer",
    }
