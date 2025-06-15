"""
Tests for competitor-specific scrapers.
"""

import pytest
from unittest.mock import Mock, patch
from bs4 import BeautifulSoup

from agents.data_collection.competitors import shwapno, agora, daraz

@pytest.fixture
def sample_shwapno_html():
    return """
    <div class="product-item">
        <h3 class="product-name">Fresh Milk 1L</h3>
        <div class="price">৳85.00</div>
        <a href="/products/fresh-milk">View</a>
    </div>
    <div class="product-item">
        <h3 class="product-name">Premium Rice 1kg</h3>
        <div class="price">৳75.00</div>
        <div class="out-of-stock">Out of stock</div>
        <a href="/products/premium-rice">View</a>
    </div>
    """

@pytest.fixture
def sample_agora_html():
    return """
    <div class="product-grid-item">
        <h3 class="product-title">Fresh Milk 1L</h3>
        <div class="product-price">৳85.00</div>
        <a class="product-link" href="/products/fresh-milk">View</a>
    </div>
    <div class="product-grid-item">
        <h3 class="product-title">Premium Rice 1kg</h3>
        <div class="product-price">৳75.00</div>
        <div class="stock-status">Out of stock</div>
        <a class="product-link" href="/products/premium-rice">View</a>
    </div>
    """

@pytest.fixture
def sample_daraz_html():
    return """
    <div class="product-card">
        <h3 class="product-title">Fresh Milk 1L</h3>
        <div class="product-price">৳85.00</div>
        <a class="product-link" href="/products/fresh-milk">View</a>
    </div>
    <div class="product-card">
        <h3 class="product-title">Premium Rice 1kg</h3>
        <div class="product-price">৳75.00</div>
        <div class="sold-out-badge">Sold out</div>
        <a class="product-link" href="/products/premium-rice">View</a>
    </div>
    """

def test_shwapno_parse_products(sample_shwapno_html):
    """Test Shwapno product parsing."""
    products = shwapno.parse_products(sample_shwapno_html, "dairy")
    assert len(products) == 2
    
    milk = products[0]
    assert milk["name"] == "Fresh Milk 1L"
    assert milk["price"] == 85.0
    assert milk["in_stock"] is True
    assert milk["url"].startswith("https://www.shwapno.com")
    assert milk["category"] == "dairy"
    assert milk["competitor"] == "shwapno"
    
    rice = products[1]
    assert rice["name"] == "Premium Rice 1kg"
    assert rice["in_stock"] is False

def test_agora_parse_products(sample_agora_html):
    """Test Agora product parsing."""
    products = agora.parse_products(sample_agora_html, "dairy")
    assert len(products) == 2
    
    milk = products[0]
    assert milk["name"] == "Fresh Milk 1L"
    assert milk["price"] == 85.0
    assert milk["in_stock"] is True
    assert milk["url"].startswith("https://www.agorasuperstores.com")
    assert milk["category"] == "dairy"
    assert milk["competitor"] == "agora"
    
    rice = products[1]
    assert rice["name"] == "Premium Rice 1kg"
    assert rice["in_stock"] is False

def test_daraz_parse_products(sample_daraz_html):
    """Test Daraz product parsing."""
    products = daraz.parse_products(sample_daraz_html, "grocery")
    assert len(products) == 2
    
    milk = products[0]
    assert milk["name"] == "Fresh Milk 1L"
    assert milk["price"] == 85.0
    assert milk["in_stock"] is True
    assert milk["url"].startswith("https://www.daraz.com.bd")
    assert milk["category"] == "grocery"
    assert milk["competitor"] == "daraz"
    
    rice = products[1]
    assert rice["name"] == "Premium Rice 1kg"
    assert rice["in_stock"] is False

@patch("agents.data_collection.competitors.shwapno.sync_playwright")
def test_shwapno_scrape_category(mock_playwright):
    """Test Shwapno category scraping with mocked browser."""
    mock_browser = Mock()
    mock_page = Mock()
    mock_page.content.return_value = "<html>Test content</html>"
    mock_browser.new_page.return_value = mock_page
    mock_playwright.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser
    
    shwapno.scrape_category("dairy")
    mock_page.goto.assert_called_once()
    mock_page.wait_for_selector.assert_called_once_with(".product-item", state="attached", timeout=15000)

def test_extract_unit():
    """Test unit extraction from product names."""
    test_cases = [
        ("Fresh Milk 1L", "1L"),
        ("Premium Rice 5kg", "5kg"),
        ("Snacks 100g", "100g"),
        ("Water 500ml", "500ml"),
        ("Eggs 12pcs", "12pcs"),
        ("চাল ৫ কেজি", "৫ কেজি"),
        ("No unit here", None)
    ]
    
    for name, expected in test_cases:
        assert shwapno.extract_unit(name) == expected
        assert agora.extract_unit(name) == expected
        assert daraz.extract_unit(name) == expected

def test_extract_brand():
    """Test brand extraction from product names."""
    test_cases = [
        ("Fresh Milk 1L", "Fresh"),
        ("Pran Juice 1L", "Pran"),
        ("Aarong Butter 200g", "Aarong"),
        ("No brand here", None),
        ("প্রাণ জুস ১ লিটার", "প্রাণ")
    ]
    
    for name, expected in test_cases:
        assert shwapno.extract_brand(name) == expected
        assert agora.extract_brand(name) == expected
        assert daraz.extract_brand(name) == expected
