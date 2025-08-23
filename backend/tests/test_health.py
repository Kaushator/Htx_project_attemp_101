"""
Tests for health endpoints
"""

import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_health_check():
    """Test basic health check"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_database_health_check():
    """Test database health check"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/health/db")
        assert response.status_code == 200
        data = response.json()
        assert "database" in data


@pytest.mark.asyncio
async def test_full_health_check():
    """Test full health check"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/health/full")
        assert response.status_code == 200
        data = response.json()
        assert "checks" in data
        assert "api" in data["checks"]
