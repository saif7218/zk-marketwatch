import logging
from typing import List, Dict

logger = logging.getLogger('DataValidator')

def validate_and_clean_data(raw_data: List[Dict]) -> List[Dict]:
    """Validate and clean scraped/API data."""
    cleaned_data = []
    for item in raw_data:
        # Validate required fields
        if not all(key in item for key in ['product_name', 'price', 'timestamp']):
            logger.warning(f"Skipping invalid data item: {item}")
            continue
        try:
            price = float(item['price'])
            if price <= 0 or price > 10000:
                logger.warning(f"Suspicious price {price} for {item['product_name']}")
                continue
        except Exception:
            logger.warning(f"Invalid price format: {item['price']}")
            continue
        cleaned_item = {
            'product_name': item['product_name'].strip(),
            'price': round(price, 2),
            'competitor': item.get('competitor', 'Unknown').strip(),
            'source': item.get('source', 'Unknown').strip(),
            'timestamp': item['timestamp'],
            'availability': item.get('availability', 'Unknown'),
            'confidence': item.get('confidence', 1.0)
        }
        cleaned_data.append(cleaned_item)
    logger.info(f"Validated {len(cleaned_data)}/{len(raw_data)} data points")
    return cleaned_data
