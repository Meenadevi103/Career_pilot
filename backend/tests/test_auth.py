"""Integration tests for user authentication and cookie lifecycle with test DB."""

import pytest
from httpx import AsyncClient

from app.core.config import settings

REGISTER_URL = "/api/auth/register"
LOGIN_URL = "/api/auth/login"
LOGOUT_URL = "/api/auth/logout"
ME_URL = "/api/auth/me"


@pytest.mark.asyncio
async def test_register_success(async_client: AsyncClient):
    """Test user registration returns 201, sets cookie, and excludes password_hash."""
    payload = {
        "name": "Meena Student",
        "email": "meena@university.edu",
        "password": "SecurePassword123!",
    }
    response = await async_client.post(REGISTER_URL, json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Meena Student"
    assert data["email"] == "meena@university.edu"
    assert data["role"] == "student"
    assert data["is_active"] is True
    assert "password_hash" not in data
    assert "password" not in data

    # Verify session cookie is set
    assert settings.COOKIE_NAME in response.cookies
    cookie = response.cookies.get(settings.COOKIE_NAME)
    assert cookie is not None


@pytest.mark.asyncio
async def test_register_duplicate_email_rejected_case_insensitive(
    async_client: AsyncClient,
):
    """Test registration rejects duplicate email regardless of uppercase/lowercase."""
    payload1 = {
        "name": "First User",
        "email": "student@college.edu",
        "password": "Password123!",
    }
    res1 = await async_client.post(REGISTER_URL, json=payload1)
    assert res1.status_code == 201

    payload2 = {
        "name": "Second User",
        "email": "STUDENT@COLLEGE.EDU",
        "password": "Password456!",
    }
    res2 = await async_client.post(REGISTER_URL, json=payload2)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"].lower()


@pytest.mark.asyncio
async def test_register_short_password_rejected(async_client: AsyncClient):
    """Test passwords under 8 characters are rejected with validation error 422."""
    payload = {
        "name": "Short Password",
        "email": "short@college.edu",
        "password": "short",
    }
    response = await async_client.post(REGISTER_URL, json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success_sets_httponly_cookie(async_client: AsyncClient):
    """Test valid credentials set the access_token httpOnly cookie."""
    # Register first
    await async_client.post(
        REGISTER_URL,
        json={
            "name": "Login User",
            "email": "loginuser@college.edu",
            "password": "Password123!",
        },
    )

    # Login
    response = await async_client.post(
        LOGIN_URL,
        json={"email": "loginuser@college.edu", "password": "Password123!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "loginuser@college.edu"
    assert "password_hash" not in data
    assert settings.COOKIE_NAME in response.cookies


@pytest.mark.asyncio
async def test_login_wrong_password_rejected(async_client: AsyncClient):
    """Test incorrect password receives 400 with generic error message."""
    await async_client.post(
        REGISTER_URL,
        json={
            "name": "Wrong Password User",
            "email": "wrongpwd@college.edu",
            "password": "CorrectPassword123!",
        },
    )

    response = await async_client.post(
        LOGIN_URL,
        json={"email": "wrongpwd@college.edu", "password": "IncorrectPassword!"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid email or password"


@pytest.mark.asyncio
async def test_login_wrong_email_gives_same_generic_error(
    async_client: AsyncClient,
):
    """Test non-existent email returns same error as wrong password (no enumeration)."""
    response = await async_client.post(
        LOGIN_URL,
        json={"email": "nonexistent@college.edu", "password": "SomePassword123!"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid email or password"


@pytest.mark.asyncio
async def test_me_without_cookie_returns_401(async_client: AsyncClient):
    """Test /api/auth/me rejects unauthenticated requests with 401."""
    response = await async_client.get(ME_URL)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_with_cookie_returns_user(async_client: AsyncClient):
    """Test /api/auth/me returns user profile when authenticated cookie is present."""
    # Register to obtain cookie
    reg_res = await async_client.post(
        REGISTER_URL,
        json={
            "name": "Profile User",
            "email": "profile@college.edu",
            "password": "Password123!",
        },
    )
    assert reg_res.status_code == 201

    # Request /me (cookies persist in the httpx client instance)
    me_res = await async_client.get(ME_URL)
    assert me_res.status_code == 200
    data = me_res.json()
    assert data["name"] == "Profile User"
    assert data["email"] == "profile@college.edu"
    assert "password_hash" not in data


@pytest.mark.asyncio
async def test_logout_clears_cookie(async_client: AsyncClient):
    """Test logout invalidates authentication cookie and subsequent /me returns 401."""
    # Register and get session
    await async_client.post(
        REGISTER_URL,
        json={
            "name": "Logout User",
            "email": "logout@college.edu",
            "password": "Password123!",
        },
    )

    # Logout
    logout_res = await async_client.post(LOGOUT_URL)
    assert logout_res.status_code == 200

    # Ensure /me now fails
    me_res = await async_client.get(ME_URL)
    assert me_res.status_code == 401


@pytest.mark.asyncio
async def test_password_hash_never_appears_in_responses(
    async_client: AsyncClient,
):
    """Test that password_hash is never exposed across register, login, or /me."""
    reg = await async_client.post(
        REGISTER_URL,
        json={
            "name": "Leak Check",
            "email": "leak@college.edu",
            "password": "Password123!",
        },
    )
    assert "password_hash" not in reg.text

    login = await async_client.post(
        LOGIN_URL,
        json={"email": "leak@college.edu", "password": "Password123!"},
    )
    assert "password_hash" not in login.text

    me = await async_client.get(ME_URL)
    assert "password_hash" not in me.text
