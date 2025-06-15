import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from main import app

client = TestClient(app)

@pytest.fixture
def mock_html():
    return """
    <html>
        <body>
            <p class="price_color">£51.77</p>
        </body>
    </html>
    """

@pytest.mark.asyncio
async def test_extract_price(mock_html):
    from main import _extract_price
    price = await _extract_price(mock_html)
    assert price == "£51.77"

@pytest.mark.asyncio
async def test_fetch_with_aiohttp():
    with patch("main.session") as mock_session:
        mock_response = AsyncMock()
        mock_response.text.return_value = """
        <html>
            <body>
                <p class="price_color">£51.77</p>
            </body>
        </html>
        """
        mock_session.get.return_value.__aenter__.return_value = mock_response
        
        from main import _fetch_with_aiohttp
        price, elapsed = await _fetch_with_aiohttp("https://example.com")
        assert price == "£51.77"
        assert isinstance(elapsed, float)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "circuit" in data
    assert "failures" in data
    assert "uptime_seconds" in data

def test_circuit_reset():
    # First, ensure circuit is closed
    response = client.post("/circuit/reset")
    assert response.status_code == 200
    assert response.json()["status"] == "Circuit breaker reset"
    
    # Verify health endpoint shows circuit as closed
    health = client.get("/health")
    assert health.json()["circuit"] == "closed" 