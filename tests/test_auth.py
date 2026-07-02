import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    response = await client.post(
        "/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_user(client: AsyncClient):
    # Register first
    await client.post(
        "/v1/auth/register",
        json={
            "email": "dup@example.com",
            "username": "dupuser",
            "password": "password123",
        },
    )

    # Try again
    response = await client.post(
        "/v1/auth/register",
        json={
            "email": "dup@example.com",
            "username": "dupuser",
            "password": "password123",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"]["error"] == "EMAIL_EXISTS"


@pytest.mark.asyncio
async def test_login_user(client: AsyncClient):
    await client.post(
        "/v1/auth/register",
        json={
            "email": "login@example.com",
            "username": "loginuser",
            "password": "password123",
        },
    )

    response = await client.post(
        "/v1/auth/login",
        data={"username": "login@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
