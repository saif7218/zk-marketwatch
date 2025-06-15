import logging
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from datetime import datetime
import re
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CATEGORIES = ["eggs", "meat", "fruits"]

class BaseScraper:
    def __init__(self, base_url, headless=True):
        self.base_url = base_url
        self.headless = headless
        self.driver = self._init_driver()

    def _init_driver(self):
        options = Options()
        if self.headless:
            options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(10)
        return driver

    def close(self):
        if self.driver:
            self.driver.quit()

class ShwapnoScraper(BaseScraper):
    def __init__(self, headless=True):
        super().__init__("https://www.shwapno.com", headless)

    def scrape_category(self, category):
        url_map = {
            "eggs": "/fresh-eggs",
            "meat": "/fresh-meat",
            "fruits": "/fresh-fruits"
        }
        url = self.base_url + url_map.get(category, f"/search?q={category}")
        logger.info(f"Scraping Shwapno: {url}")
        self.driver.get(url)
        time.sleep(5)
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        products = []
        for card in soup.select('.product-item, .grid-product__content, .product-card, .product'):
            name = card.select_one('.product-item-link, .product-name, .title, h2, h3')
            price = card.select_one('.price, .special-price .price, .product-price, .amount')
            if name and price:
                price_val = re.sub(r'[^\d.]', '', price.get_text())
                try:
                    price_val = float(price_val)
                except:
                    continue
                products.append({
                    'product_name': name.get_text(strip=True),
                    'price': price_val,
                    'store': 'Shwapno',
                    'category': category
                })
        return products

class MeenaBazarScraper(BaseScraper):
    def __init__(self, headless=True):
        # Try both main domains
        super().__init__("https://www.meenaclick.com", headless)

    def scrape_category(self, category):
        url_map = {
            "eggs": "/dairy-eggs",
            "meat": "/meat-poultry",
            "fruits": "/fruits-vegetables"
        }
        url = self.base_url + url_map.get(category, f"/search?q={category}")
        logger.info(f"Scraping MeenaBazar: {url}")
        self.driver.get(url)
        time.sleep(5)
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        products = []
        for card in soup.select('.product-item, .product-card, .product, .item'):
            name = card.select_one('.product-item-link, .product-name, .title, h2, h3')
            price = card.select_one('.price, .special-price .price, .product-price, .amount')
            if name and price:
                price_val = re.sub(r'[^\d.]', '', price.get_text())
                try:
                    price_val = float(price_val)
                except:
                    continue
                products.append({
                    'product_name': name.get_text(strip=True),
                    'price': price_val,
                    'store': 'MeenaBazar',
                    'category': category
                })
        return products

def compare_products(shwapno, meena):
    # Simple name-based join
    df1 = pd.DataFrame(shwapno)
    df2 = pd.DataFrame(meena)
    if df1.empty or df2.empty:
        print("No products found for comparison.")
        return
    merged = pd.merge(df1, df2, on=['product_name', 'category'], how='outer', suffixes=('_shwapno', '_meena'))
    merged['diff'] = merged['price_shwapno'] - merged['price_meena']
    print(merged[['product_name', 'category', 'price_shwapno', 'price_meena', 'diff']].to_string(index=False))

if __name__ == "__main__":
    shwapno_scraper = ShwapnoScraper(headless=True)
    meena_scraper = MeenaBazarScraper(headless=True)
    try:
        for category in CATEGORIES:
            print(f"\n{'='*30}\nCategory: {category.title()}\n{'='*30}")
            shwapno_products = shwapno_scraper.scrape_category(category)
            meena_products = meena_scraper.scrape_category(category)
            compare_products(shwapno_products, meena_products)
    finally:
        shwapno_scraper.close()
        meena_scraper.close()
