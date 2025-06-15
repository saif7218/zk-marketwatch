"""
Tests for data collection components.
"""

import os
import json
import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from agents.data_collection.collector import collect_data, save_data
from agents.data_collection.utils import (
    atomic_write,
    get_latest_snapshot,
    validate_product_data,
    cleanup_old_snapshots
)
from agents.data_collection.scheduler import SmartScheduler

@pytest.fixture
def sample_product_data():
    return {
        "name": "Fresh Milk",
        "price": 85.0,
        "currency": "BDT",
        "in_stock": True,
        "url": "https://example.com/milk",
        "category": "dairy",
        "competitor": "shwapno",
        "promotion": None,
        "unit": "1L",
        "brand": "Fresh"
    }

@pytest.fixture
def sample_products(sample_product_data):
    return [
        sample_product_data,
        {
            "name": "Premium Rice",
            "price": 75.0,
            "currency": "BDT",
            "in_stock": True,
            "url": "https://example.com/rice",
            "category": "rice",
            "competitor": "shwapno",
            "promotion": "10% off",
            "unit": "1kg",
            "brand": "Pran"
        }
    ]

def test_validate_product_data_valid(sample_product_data):
    """Test product data validation with valid data."""
    assert validate_product_data(sample_product_data) is True

def test_validate_product_data_invalid():
    """Test product data validation with invalid data."""
    invalid_data = {
        "name": "Test Product",
        "price": -10,  # Invalid negative price
        "currency": "BDT",
        "in_stock": True,
        "url": "invalid-url",  # Invalid URL format
        "category": "test",
        "competitor": "test"
    }
    assert validate_product_data(invalid_data) is False

def test_atomic_write(tmp_path, sample_products):
    """Test atomic file writing."""
    output_file = tmp_path / "test_output.json"
    
    # Test successful write
    assert atomic_write({"products": sample_products}, str(output_file)) is True
    assert output_file.exists()
    
    # Verify content
    with open(output_file) as f:
        saved_data = json.load(f)
        assert len(saved_data["products"]) == 2
        assert saved_data["products"][0]["name"] == "Fresh Milk"

def test_get_latest_snapshot(tmp_path, sample_products):
    """Test retrieving latest snapshot."""
    # Create test snapshots
    older = tmp_path / "shwapno_dairy_20250101_000000.json"
    newer = tmp_path / "shwapno_dairy_20250102_000000.json"
    
    with open(older, "w") as f:
        json.dump({"products": [sample_products[0]]}, f)
    with open(newer, "w") as f:
        json.dump({"products": sample_products}, f)
        
    latest = get_latest_snapshot(str(tmp_path), "shwapno", "dairy")
    assert latest is not None
    assert len(latest["products"]) == 2

@patch("agents.data_collection.collector.COMPETITOR_MAP")
def test_collect_data(mock_competitor_map, sample_products):
    """Test data collection with mocked competitor."""
    mock_scraper = Mock()
    mock_scraper.scrape_category.return_value = sample_products
    mock_competitor_map.get.return_value = mock_scraper
    
    data = collect_data("shwapno", "dairy")
    assert len(data) == 2
    assert data[0]["name"] == "Fresh Milk"
    mock_scraper.scrape_category.assert_called_once_with("dairy")

def test_save_data(tmp_path, sample_products):
    """Test saving collected data."""
    output_path = str(tmp_path)
    saved_path = save_data(sample_products, output_path, "shwapno", "dairy")
    
    assert saved_path is not None
    assert os.path.exists(saved_path)
    
    with open(saved_path) as f:
        data = json.load(f)
        assert "metadata" in data
        assert data["metadata"]["competitor"] == "shwapno"
        assert data["metadata"]["category"] == "dairy"
        assert len(data["products"]) == 2

def test_cleanup_old_snapshots(tmp_path):
    """Test cleanup of old snapshots."""
    # Create test files with different creation times
    old_file = tmp_path / "old_snapshot.json"
    new_file = tmp_path / "new_snapshot.json"
    
    old_file.touch()
    new_file.touch()
    
    # Mock file creation times
    old_time = datetime(2024, 1, 1).timestamp()
    new_time = datetime(2025, 6, 1).timestamp()
    
    os.utime(old_file, (old_time, old_time))
    os.utime(new_file, (new_time, new_time))
    
    cleanup_old_snapshots(str(tmp_path), keep_days=30)
    
    assert not old_file.exists()
    assert new_file.exists()

def test_smart_scheduler():
    """Test scheduler configuration and job management."""
    config = {
        "jobs": [
            {
                "competitor": "test",
                "category": "test",
                "schedule": {
                    "type": "interval",
                    "params": {"minutes": 5}
                }
            }
        ],
        "retry_limit": 3,
        "backoff_base": 5
    }
    
    with patch("agents.data_collection.scheduler.SmartScheduler._load_config", return_value=config):
        scheduler = SmartScheduler("dummy_path")
        
        # Add a test job
        job_id = scheduler.add_collection_job("test", "test", config["jobs"][0]["schedule"])
        assert job_id == "test_test"
        
        # Verify job was added
        jobs = scheduler.get_jobs()
        assert len(jobs) == 1
        assert jobs[0]["id"] == "test_test"
