from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re
from typing import Dict, Any, List
import time
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class ShawpnoScraper:
    def __init__(self, headless=True):
        self.base_url = "https://www.shwapno.com"  # Updated URL
        options = Options()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
    def scrape_category(self, category: str) -> List[Dict[str, Any]]:
        try:
            # Updated category URLs
            category_mapping = {
                'meat': '/fresh-meat',
                'eggs': '/fresh-eggs',
                'fruits': '/fresh-fruits'
            }
            
            url = f"{self.base_url}{category_mapping.get(category, f'/search?q={category}')}"  # Fixed missing quotes
            logger.info(f"Scraping Shwapno URL: {url}")
            
            self.driver.get(url)
            time.sleep(5)  # Extended wait for dynamic content
            
            # Scroll multiple times to load lazy content
            for _ in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            products = []
            # Updated selectors for current Shwapno website
            product_elements = self.driver.find_elements("css selector", ".product-item, .grid-product__content")
            
            for element in product_elements:
                try:
                    name = element.find_element("css selector", ".product-item__title, .grid-product__title").text.strip()
                    price_elem = element.find_element("css selector", ".money, .grid-product__price")
                    price_text = price_elem.text.strip()
                    
                    # Handle both ৳ and Tk symbols and clean up price
                    price_text = price_text.replace('৳', '').replace('Tk', '').replace(',', '').strip()
                    try:
                        price = float(re.search(r'\d+\.?\d*', price_text)[0])
                        products.append({
                            'product_name': name,
                            'price': price,
                            'store': 'Shwapno'
                        })
                        logger.info(f"Found Shwapno product: {name} at ৳{price}")
                    except (ValueError, TypeError, AttributeError) as e:
                        logger.error(f"Error parsing Shwapno price {price_text}: {e}")
                        continue
                        
                except Exception as e:
                    logger.error(f"Error processing Shwapno product: {e}")
                    continue
            
            return products
            
        except Exception as e:
            logger.error(f"Error scraping Shwapno: {e}")
            return []

    def close(self):
        if self.driver:
            self.driver.quit()

class MeenaBazarScraper:
    def __init__(self, headless=True):
        self.base_url = "https://meenabazar.com.bd"  # Updated URL
        options = Options()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
    def scrape_category(self, category: str) -> List[Dict[str, Any]]:
        try:
            # Updated category URLs
            category_mapping = {
                'meat': '/meat-poultry',
                'eggs': '/dairy-eggs',
                'fruits': '/fruits-vegetables'
            }
            
            url = f"{self.base_url}{category_mapping.get(category, f'/catalogsearch/result/?q={category}')}"  # Fixed missing quote
            logger.info(f"Scraping Meena Bazar URL: {url}")
            
            try:
                self.driver.get(url)
            except Exception as e:
                logger.error(f"Error accessing URL {url}: {e}")
                return []
                
            time.sleep(5)  # Extended wait for dynamic content
            
            # Scroll multiple times to load lazy content
            for _ in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            products = []
            # Updated selectors for current Meena Bazar website
            product_elements = self.driver.find_elements("css selector", ".product-item-info, .product-item")
            
            for element in product_elements:
                try:
                    name = element.find_element("css selector", ".product-item-link, .product-name").text.strip()
                    price_elem = element.find_element("css selector", ".price, .special-price .price")
                    price_text = price_elem.text.strip()
                    
                    # Handle both ৳ and Tk symbols and clean up price
                    price_text = price_text.replace('৳', '').replace('Tk', '').replace(',', '').strip()
                    try:
                        price = float(re.search(r'\d+\.?\d*', price_text)[0])
                        products.append({
                            'product_name': name,
                            'price': price,
                            'store': 'Meena Bazar'
                        })
                        logger.info(f"Found Meena Bazar product: {name} at ৳{price}")
                    except (ValueError, TypeError, AttributeError) as e:
                        logger.error(f"Error parsing Meena Bazar price {price_text}: {e}")
                        continue
                        
                except Exception as e:
                    logger.error(f"Error processing Meena Bazar product: {e}")
                    continue
            
            return products
            
        except Exception as e:
            logger.error(f"Error scraping Meena Bazar: {e}")
            return []
        
    def close(self):
        if self.driver:
            self.driver.quit()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index_tailwind.html", {"request": request})

@app.get("/api/compare/{category}")
async def compare_prices(category: str):
    shwapno_scraper = ShawpnoScraper(headless=True)
    meena_bazar_scraper = MeenaBazarScraper(headless=True)
    
    try:
        # Get products from both stores
        shwapno_products = shwapno_scraper.scrape_category(category)
        meena_bazar_products = meena_bazar_scraper.scrape_category(category)
        
        # Match and compare products
        comparisons = []
        for s_product in shwapno_products:
            s_name = s_product['product_name'].lower()
            
            # Find matching product in Meena Bazar
            m_product = next(
                (p for p in meena_bazar_products 
                 if similar_product_names(p['product_name'].lower(), s_name)),
                None
            )
            
            if m_product:
                diff = s_product['price'] - m_product['price']
                diff_percent = (diff / m_product['price']) * 100
                
                comparisons.append({
                    'name': s_product['product_name'],
                    'shwapno_price': s_product['price'],
                    'meena_bazar_price': m_product['price'],
                    'difference': round(diff, 2),
                    'difference_percentage': round(diff_percent, 1)
                })
        
        return {
            'category': category,
            'products': sorted(comparisons, key=lambda x: abs(x['difference_percentage']), reverse=True)
        }
    
    finally:
        shwapno_scraper.close()
        meena_bazar_scraper.close()

def similar_product_names(name1: str, name2: str) -> bool:
    """Compare product names and return True if they are similar enough"""
    # Clean and split names into words
    words1 = set(re.findall(r'\w+', name1.lower()))
    words2 = set(re.findall(r'\w+', name2.lower()))
    
    # Calculate similarity score
    common_words = words1 & words2
    total_words = words1 | words2
    
    if not total_words:
        return False
        
    similarity = len(common_words) / len(total_words)
    return similarity > 0.3  # Adjust threshold as needed