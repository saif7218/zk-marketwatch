import requests
from bs4 import BeautifulSoup
import logging
from typing import Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def scrape_shwapno(product_name: str) -> Dict:
    """Scrape product information from Shwapno."""
    url = f"https://www.shwapno.com/search?q={product_name}"
    try:
        logger.info(f"Scraping Shwapno for: {product_name}")
        r = requests.get(url, headers=BASE_HEADERS, timeout=10)
        r.raise_for_status()
        
        soup = BeautifulSoup(r.text, "html.parser")
        item = soup.select_one(".product-card")
        
        if not item:
            return {"error": "Product not found on Shwapno"}
            
        name = item.select_one(".product-title")
        price = item.select_one(".price")
        
        if not name or not price:
            return {"error": "Could not extract product details from Shwapno"}
            
        return {
            "name": name.text.strip(),
            "price": price.text.strip(),
            "store": "Shwapno"
        }
    except Exception as e:
        logger.error(f"Error scraping Shwapno: {str(e)}")
        return {"error": f"Shwapno fetch failed: {str(e)}"}

def scrape_meenabazar(product_name: str) -> Dict:
    """Scrape product information from Meena Bazar."""
    url = f"https://www.meenaclick.com/search?q={product_name}"
    try:
        logger.info(f"Scraping Meena Bazar for: {product_name}")
        r = requests.get(url, headers=BASE_HEADERS, timeout=10)
        r.raise_for_status()
        
        soup = BeautifulSoup(r.text, "html.parser")
        item = soup.select_one(".product-card")
        
        if not item:
            return {"error": "Product not found on Meena Bazar"}
            
        name = item.select_one(".title")
        price = item.select_one(".price")
        
        if not name or not price:
            return {"error": "Could not extract product details from Meena Bazar"}
            
        return {
            "name": name.text.strip(),
            "price": price.text.strip(),
            "store": "Meena Bazar"
        }
    except Exception as e:
        logger.error(f"Error scraping Meena Bazar: {str(e)}")
        return {"error": f"Meena Bazar fetch failed: {str(e)}"}

def scrape_unimart(product_name: str) -> Dict:
    """Scrape product information from Unimart."""
    url = f"https://www.unimart.online/search?q={product_name}"
    try:
        logger.info(f"Scraping Unimart for: {product_name}")
        r = requests.get(url, headers=BASE_HEADERS, timeout=10)
        r.raise_for_status()
        
        soup = BeautifulSoup(r.text, "html.parser")
        item = soup.select_one(".product-item")
        
        if not item:
            return {"error": "Product not found on Unimart"}
            
        name = item.select_one(".title")
        price = item.select_one(".price")
        
        if not name or not price:
            return {"error": "Could not extract product details from Unimart"}
            
        return {
            "name": name.text.strip(),
            "price": price.text.strip(),
            "store": "Unimart"
        }
    except Exception as e:
        logger.error(f"Error scraping Unimart: {str(e)}")
        return {"error": f"Unimart fetch failed: {str(e)}"} 