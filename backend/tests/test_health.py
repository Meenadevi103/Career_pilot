"""Unit tests for the /health endpoint."""

from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from app.db.session import get_db
from app.main import app


@pytest.mark.asyncio
async def test_health_check_database_connected(async_client: AsyncClient):
    """Test /health returns 200 and connected status when database is reachable."""
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock()

    async def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db
    try:
        response = await async_client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "database": "connected"}
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_health_check_database_disconnected(async_client: AsyncClient):
    """Test /health returns 503 and error payload when database connection fails."""
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(
        side_effect=ConnectionRefusedError("PostgreSQL connection refused")
    )

    async def override_get_db_failure():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db_failure
    try:
        response = await async_client.get("/health")
        assert response.status_code == 503
        assert response.json() == {"status": "error", "database": "disconnected"}
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_root_endpoint(async_client: AsyncClient):
    """Test root endpoint provides API info."""
    response = await async_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "CareerPilot AI API" in data["message"]
    assert data["docs"] == "/docs"
