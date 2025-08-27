"""
Tests for health endpoints
"""

from fastapi.testclient import TestClient
from app.main import app


def test_health_check():
    """Test basic health check"""
    client = TestClient(app)
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") == "healthy"


def test_database_health_check():
    """Test database health check"""
    client = TestClient(app)
    resp = client.get("/api/v1/health/db")
    assert resp.status_code == 200
    data = resp.json()
    assert "database" in data


def test_full_health_check():
    """Test full health check"""
    client = TestClient(app)
    resp = client.get("/api/v1/health/full")
    assert resp.status_code == 200
    data = resp.json()
    assert "checks" in data
    assert "api" in data["checks"]
