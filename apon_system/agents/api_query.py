import logging
import numpy as np
from datetime import datetime
from typing import Dict, List

logger = logging.getLogger('APIQuery')

def query_price_apis(product: Dict) -> List[Dict]:
    """Mock API price comparison data."""
    api_data = []
    api_sources = ['PriceTracker BD', 'Market Monitor', 'Price Compare']
    for source in api_sources:
        base_price = product['target_price']
        api_price = round(base_price * np.random.uniform(0.85, 1.15), 2)
        api_data.append({
            'product_name': product['name'],
            'price': api_price,
            'source': source,
            'timestamp': datetime.now().isoformat(),
            'confidence': float(np.random.uniform(0.7, 0.95))
        })
    logger.info(f"Retrieved {len(api_data)} API price points for {product['name']}")
    return api_data
