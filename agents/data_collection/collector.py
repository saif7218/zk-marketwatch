"""
Core collection logic for ZK MarketWatch.
Handles dispatching to competitor-specific collectors and data saving.
"""

import os
import json
import time
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from .competitors import COMPETITOR_MAP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("agents/data_collection/logs/collection.log"),
        logging.StreamHandler()
    ]
)

def collect_data(competitor: str, category: str) -> List[Dict[str, Any]]:
    """
    Dispatch to competitor-specific collector and handle errors.
    
    Args:
        competitor: Name of the competitor (e.g., 'shwapno', 'agora')
        category: Product category to scrape
        
    Returns:
        List of product dictionaries with standardized fields
    """
    try:
        scraper = COMPETITOR_MAP.get(competitor.lower())
        if not scraper:
            raise ValueError(f"No scraper configured for competitor: {competitor}")
            
        logging.info(f"Starting collection for {competitor}/{category}")
        start_time = time.time()
        
        data = scraper.scrape_category(category)
        
        duration = time.time() - start_time
        logging.info(f"Collection completed: {competitor}/{category} - {len(data)} items in {duration:.2f}s")
        
        return data
        
    except Exception as e:
        logging.error(f"Collection failed: {competitor}/{category} - {str(e)}")
        return []

def save_data(data: List[Dict[str, Any]], 
              output_path: str, 
              competitor: str, 
              category: str) -> Optional[str]:
    """
    Save collected data with atomic write for crash safety.
    
    Args:
        data: List of product dictionaries to save
        output_path: Directory to save the data file
        competitor: Name of the competitor
        category: Product category
        
    Returns:
        Path to the saved file, or None if save failed
    """
    try:
        os.makedirs(output_path, exist_ok=True)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{competitor}_{category}_{timestamp}.json"
        temp_path = os.path.join(output_path, f".tmp_{filename}")
        final_path = os.path.join(output_path, filename)
        
        # Save to temporary file first
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump({
                "metadata": {
                    "competitor": competitor,
                    "category": category,
                    "collected_at": timestamp,
                    "item_count": len(data)
                },
                "products": data
            }, f, ensure_ascii=False, indent=2)
        
        # Atomic rename
        os.rename(temp_path, final_path)
        logging.info(f"Saved {len(data)} items to {final_path}")
        return final_path
        
    except Exception as e:
        logging.error(f"Failed to save data: {str(e)}")
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass
        return None

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="ZK MarketWatch Data Collector")
    parser.add_argument("--competitor", required=True, help="Competitor name (e.g., shwapno, agora)")
    parser.add_argument("--category", required=True, help="Product category to scrape")
    parser.add_argument("--output", default="data/raw", help="Output directory for data files")
    args = parser.parse_args()
    
    logging.info(f"Starting collection: {args.competitor}/{args.category}")
    start_time = time.time()
    
    try:
        data = collect_data(args.competitor, args.category)
        if data:
            save_data(data, args.output, args.competitor, args.category)
        logging.info(f"Collection completed in {time.time()-start_time:.2f}s")
    except Exception as e:
        logging.exception("Fatal error during collection")
