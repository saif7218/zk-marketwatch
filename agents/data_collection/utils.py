"""
Utility functions for data collection and file handling.
"""

import os
import json
import shutil
import logging
from datetime import datetime
from typing import Dict, Any, Optional

def ensure_directory(path: str) -> None:
    """
    Ensure directory exists, create if not.
    
    Args:
        path: Directory path to ensure exists
    """
    os.makedirs(path, exist_ok=True)

def atomic_write(data: Dict[str, Any], filepath: str) -> bool:
    """
    Write data to file with atomic operation to prevent data corruption.
    
    Args:
        data: Data to write
        filepath: Target file path
        
    Returns:
        True if write succeeded, False otherwise
    """
    temp_path = f"{filepath}.tmp"
    try:
        # Write to temporary file first
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # Atomic rename
        shutil.move(temp_path, filepath)
        return True
        
    except Exception as e:
        logging.error(f"Failed to write file {filepath}: {str(e)}")
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass
        return False

def get_latest_snapshot(directory: str, competitor: str, category: str) -> Optional[Dict[str, Any]]:
    """
    Get most recent data snapshot for given competitor and category.
    
    Args:
        directory: Base directory containing snapshots
        competitor: Competitor name
        category: Product category
        
    Returns:
        Latest snapshot data or None if not found
    """
    pattern = f"{competitor}_{category}_*.json"
    try:
        files = [f for f in os.listdir(directory) if f.startswith(f"{competitor}_{category}_")]
        if not files:
            return None
            
        latest = max(files)
        with open(os.path.join(directory, latest), 'r', encoding='utf-8') as f:
            return json.load(f)
            
    except Exception as e:
        logging.error(f"Failed to read latest snapshot: {str(e)}")
        return None

def generate_snapshot_path(base_dir: str, competitor: str, category: str) -> str:
    """
    Generate path for new snapshot file.
    
    Args:
        base_dir: Base directory for snapshots
        competitor: Competitor name
        category: Product category
        
    Returns:
        Full path for new snapshot file
    """
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"{competitor}_{category}_{timestamp}.json"
    return os.path.join(base_dir, filename)

def cleanup_old_snapshots(directory: str, keep_days: int = 30) -> None:
    """
    Remove snapshots older than specified days.
    
    Args:
        directory: Directory containing snapshots
        keep_days: Number of days of snapshots to keep
    """
    try:
        cutoff = datetime.utcnow().timestamp() - (keep_days * 24 * 60 * 60)
        
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.getctime(filepath) < cutoff:
                try:
                    os.remove(filepath)
                    logging.info(f"Removed old snapshot: {filename}")
                except Exception as e:
                    logging.error(f"Failed to remove old snapshot {filename}: {str(e)}")
                    
    except Exception as e:
        logging.error(f"Error during snapshot cleanup: {str(e)}")

def validate_product_data(data: Dict[str, Any]) -> bool:
    """
    Validate product data against expected schema.
    
    Args:
        data: Product data dictionary to validate
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = {
        "name": str,
        "price": (int, float),
        "currency": str,
        "in_stock": bool,
        "url": str,
        "category": str,
        "competitor": str
    }
    
    try:
        for field, expected_type in required_fields.items():
            if field not in data:
                logging.error(f"Missing required field: {field}")
                return False
            
            if not isinstance(data[field], expected_type):
                logging.error(f"Invalid type for {field}: expected {expected_type}, got {type(data[field])}")
                return False
        
        # Additional validation
        if data["price"] <= 0:
            logging.error("Invalid price: must be positive")
            return False
            
        if not data["url"].startswith(("http://", "https://")):
            logging.error("Invalid URL format")
            return False
            
        return True
        
    except Exception as e:
        logging.error(f"Error during data validation: {str(e)}")
        return False
