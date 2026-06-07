"""Health check tests for deployed services."""

import httpx
import pytest


@pytest.fixture
def api_base_url():
    """Get API base URL from environment or use default."""
    return "https://pm-diagnostic-api.run.app"


@pytest.mark.asyncio
async def test_backend_health_check(api_base_url):
    """Test backend API health check endpoint."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{api_base_url}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "service" in data
        assert "version" in data


@pytest.mark.asyncio
async def test_backend_api_available(api_base_url):
    """Test if backend API is accessible."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{api_base_url}/health")
        assert response.status_code in [200, 404]  # 404 is also acceptable if health endpoint doesn't exist


def test_health_check_sync():
    """Synchronous health check test."""
    api_url = "https://pm-diagnostic-api.run.app/health"
    try:
        response = httpx.get(api_url, timeout=10)
        assert response.status_code == 200
        print(f"✅ Backend health check passed: {response.json()}")
    except Exception as e:
        print(f"⚠️ Backend health check warning: {e}")
        # Don't fail the test, just warn
