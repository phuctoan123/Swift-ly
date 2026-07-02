"""Authentication and User management service."""

from datetime import UTC, datetime, timedelta
from typing import Any

import structlog
from fastapi import HTTPException
from jose import jwt
import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.user import User
from app.schemas.auth import UserCreate

log = structlog.get_logger()
settings = get_settings()

def get_password_hash(password: str) -> str:
    # bcrypt requires bytes
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_bytes.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), 
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False


def create_access_token(
    subject: str | Any, expires_delta: timedelta | None = None
) -> str:
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def create_refresh_token(
    subject: str | Any, expires_delta: timedelta | None = None
) -> str:
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalars().first()


async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    # Check if user exists
    if await get_user_by_email(db, email=user_in.email):
        raise HTTPException(
            status_code=400,
            detail={"error": "EMAIL_EXISTS", "message": "Email đã được sử dụng"},
        )
    if await get_user_by_username(db, username=user_in.username):
        raise HTTPException(
            status_code=400,
            detail={"error": "USERNAME_EXISTS", "message": "Username đã được sử dụng"},
        )

    db_obj = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    
    log.info("user_created", user_id=str(db_obj.id), username=db_obj.username)
    return db_obj
