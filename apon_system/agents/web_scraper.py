import logging
import numpy as np
import requests
from datetime import datetime
from typing import Dict, List
from bs4 import BeautifulSoup

logger = logging.getLogger('WebScraper')

def scrape_competitor_prices(product: Dict) -> List[Dict]:
    """Scrape prices from Shawpno and Meena Bazar."""
    scraped_prices = []

    # Shawpno scraping
    try:
        shawpno_url = f"https://www.shawpno.com.bd/search?q={product['name']}"
        response = requests.get(shawpno_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        for item in soup.select('.product-item'):  # Update selector based on Shawpno's structure
            price = float(item.select_one('.price').text.strip().replace('৳', ''))
            availability = item.select_one('.availability').text.strip()
            scraped_prices.append({
                'product_name': product['name'],
                'competitor': 'Shawpno',
                'price': price,
                'currency': 'BDT',
                'timestamp': datetime.now().isoformat(),
                'source': shawpno_url,
                'availability': availability
            })
    except Exception as e:
        logger.error(f"Error scraping Shawpno: {e}")

    # Meena Bazar scraping
    try:
        meena_url = f"https://www.meenabazar.com.bd/search?q={product['name']}"
        response = requests.get(meena_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        for item in soup.select('.product-item'):  # Update selector based on Meena Bazar's structure
            price = float(item.select_one('.price').text.strip().replace('৳', ''))
            availability = item.select_one('.availability').text.strip()
            scraped_prices.append({
                'product_name': product['name'],
                'competitor': 'Meena Bazar',
                'price': price,
                'currency': 'BDT',
                'timestamp': datetime.now().isoformat(),
                'source': meena_url,
                'availability': availability
            })
    except Exception as e:
        logger.error(f"Error scraping Meena Bazar: {e}")

    logger.info(f"Scraped {len(scraped_prices)} price points for {product['name']}")
    return scraped_prices
