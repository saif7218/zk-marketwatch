import pytest
from unittest.mock import patch, Mock
from scrapers import scrape_shwapno, scrape_meenabazar, scrape_unimart

@pytest.fixture
def mock_response():
    mock = Mock()
    mock.text = """
    <div class="product-card">
        <div class="product-title">Test Product</div>
        <div class="price">৳100</div>
    </div>
    """
    mock.status_code = 200
    return mock

def test_scrape_shwapno_success(mock_response):
    with patch('requests.get', return_value=mock_response):
        result = scrape_shwapno("test product")
        assert result["name"] == "Test Product"
        assert result["price"] == "৳100"
        assert result["store"] == "Shwapno"

def test_scrape_meenabazar_success(mock_response):
    with patch('requests.get', return_value=mock_response):
        result = scrape_meenabazar("test product")
        assert result["name"] == "Test Product"
        assert result["price"] == "৳100"
        assert result["store"] == "Meena Bazar"

def test_scrape_unimart_success(mock_response):
    with patch('requests.get', return_value=mock_response):
        result = scrape_unimart("test product")
        assert result["name"] == "Test Product"
        assert result["price"] == "৳100"
        assert result["store"] == "Unimart"

def test_scrape_error():
    with patch('requests.get', side_effect=Exception("Network error")):
        result = scrape_shwapno("test product")
        assert "error" in result
        assert "Network error" in result["error"] 