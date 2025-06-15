import logging
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import List, Dict
import socket
import pandas as pd
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AIPriceScraper")

# Product structure
class Product:
    def __init__(self, title: str, price: float, url: str, store: str):
        self.title = title
        self.price = price
        self.url = url
        self.store = store
        self.timestamp = datetime.now().isoformat()

    def __repr__(self):
        return f"Product(title={self.title}, price={self.price}, store={self.store})"

# Update base URLs for Shawpno, Meena Bazar, and Unimart
BASE_URLS = {
    "shawpno": "https://www.shawpno.com/search?q=",
    "meena_bazar": "https://www.meenabazar.com.bd/search?q=",
    "unimart": "https://unimart.com.bd/search?q="
}

STORE_SELECTORS = {
    "shawpno": {
        "product_card": ".product-card",
        "title": ".product-title",
        "price": ".product-price"
    },
    "meena_bazar": {
        "product_card": ".product-item",
        "title": ".product-name",
        "price": ".price"
    },
    "unimart": {
        "product_card": ".product-grid-item",
        "title": ".product-title",
        "price": ".price"
    }
}

# Validate and normalize URLs
def validate_url(url: str) -> bool:
    try:
        socket.gethostbyname(url.split('/')[2])
        return True
    except socket.gaierror:
        logger.error(f"DNS resolution failed for {url}")
        return False

# Clean and convert price to float
def clean_price(price_text: str) -> float:
    return float(''.join(filter(str.isdigit, price_text.replace(',', ''))))

# Fetch products using Selenium
def fetch_with_selenium(url: str, store: str) -> List[Product]:
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)
    products = []

    try:
        driver.get(url)
        selectors = STORE_SELECTORS[store]
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selectors["product_card"]))
        )
        
        elements = driver.find_elements(By.CSS_SELECTOR, selectors["product_card"])
        for element in elements:
            try:
                title = element.find_element(By.CSS_SELECTOR, selectors["title"]).text.strip()
                price_text = element.find_element(By.CSS_SELECTOR, selectors["price"]).text.strip()
                price = clean_price(price_text)
                url = element.find_element(By.TAG_NAME, "a").get_attribute("href")
                products.append(Product(title, price, url, store))
            except Exception as e:
                logger.warning(f"Error processing product element: {e}")
                continue

    except Exception as e:
        logger.error(f"Selenium error for {store}: {e}")
    finally:
        driver.quit()

    logger.info(f"Selenium: Found {len(products)} products from {store}")
    return products

# Main API function
def fetch_products(category_name: str, stores=None) -> List[Product]:
    if stores is None:
        stores = ["shawpno", "meena_bazar", "unimart"]
    
    all_products = []
    for store in stores:
        url = BASE_URLS.get(store) + category_name
        if not validate_url(url):
            continue
        products = fetch_with_selenium(url, store)
        all_products.extend(products)
    
    return all_products

# Generate price report
def generate_price_report(categories: List[str]) -> pd.DataFrame:
    all_products = []
    for category in categories:
        products = fetch_products(category)
        all_products.extend(products)
    
    df = pd.DataFrame([{
        'Category': p.title.split()[0],  # Simple categorization
        'Product': p.title,
        'Price': p.price,
        'Store': p.store,
        'Timestamp': p.timestamp,
        'URL': p.url
    } for p in all_products])
    
    return df

# Example usage
if __name__ == "__main__":
    categories = ["egg", "milk", "meat", "chicken"]
    df = generate_price_report(categories)
    df.to_csv("price_report.csv", index=False)
    print(df.groupby(['Category', 'Store'])['Price'].agg(['mean', 'min', 'max']))