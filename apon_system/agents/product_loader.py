import csv
import logging
from typing import List, Dict

logger = logging.getLogger('ProductLoader')

def load_products_from_csv(file_path: str) -> List[Dict]:
    """Load products from a CSV file."""
    products = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                products.append({
                    'name': row.get('name', ''),
                    'category': row.get('category', ''),
                    'keywords': [kw.strip() for kw in row.get('keywords', '').split(',')],
                    'target_price': float(row.get('target_price', 0)),
                    'competitors': [c.strip() for c in row.get('competitors', '').replace('|', ',').split(',')]
                })
        logger.info(f"Loaded {len(products)} products from {file_path}")
    except Exception as e:
        logger.error(f"Error loading products from {file_path}: {e}")
    return products
