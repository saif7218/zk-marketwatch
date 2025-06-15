"""
Agora-specific scraping implementation.
"""

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import logging
from typing import List, Dict, Any

BASE_URL = "https://www.agorasuperstores.com"

def scrape_category(category: str) -> List[Dict[str, Any]]:
    """
    Scrape specific category from Agora.
    
    Args:
        category: Product category to scrape (e.g., 'dairy', 'snacks')
        
    Returns:
        List of product dictionaries with standardized fields
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        
        try:
            page = context.new_page()
            url = urljoin(BASE_URL, f"category/{category}")
            logging.info(f"Scraping Agora URL: {url}")
            
            page.goto(url, timeout=60000)
            page.wait_for_selector(".product-grid-item", state="attached", timeout=15000)
            
            # Infinite scroll handling
            page.evaluate("""async () => {
                await new Promise(resolve => {
                    let totalHeight = 0;
                    const distance = 100;
                    const timer = setInterval(() => {
                        const scrollHeight = document.body.scrollHeight;
                        window.scrollBy(0, distance);
                        totalHeight += distance;
                        if(totalHeight >= scrollHeight){
                            clearInterval(timer);
                            resolve();
                        }
                    }, 100);
                });
            }""")
            
            content = page.content()
            return parse_products(content, category)
            
        except Exception as e:
            logging.error(f"Error scraping Agora category {category}: {str(e)}")
            return []
            
        finally:
            context.close()
            browser.close()

def parse_products(html: str, category: str) -> List[Dict[str, Any]]:
    """
    Parse product data from Agora HTML.
    
    Args:
        html: Raw HTML content
        category: Product category being scraped
        
    Returns:
        List of standardized product dictionaries
    """
    soup = BeautifulSoup(html, "html.parser")
    products = []
    
    for item in soup.select(".product-grid-item"):
        try:
            # Extract basic product data
            name = item.select_one(".product-title").get_text(strip=True)
            price_text = item.select_one(".product-price").get_text(strip=True)
            price = float(re.search(r"[\d,]+\.?\d+", price_text)[0].replace(",", ""))
            
            # Check stock status
            stock_elem = item.select_one(".stock-status")
            in_stock = stock_elem is None or "out of stock" not in stock_elem.text.lower()
            
            # Get product URL
            link = item.select_one("a.product-link")["href"]
            full_url = urljoin(BASE_URL, link)
            
            # Extract any promotions
            promo_elem = item.select_one(".discount-badge")
            promotion = promo_elem.get_text(strip=True) if promo_elem else None
            
            # Build standardized product record
            products.append({
                "name": name,
                "price": price,
                "currency": "BDT",
                "in_stock": in_stock,
                "url": full_url,
                "category": category,
                "competitor": "agora",
                "promotion": promotion,
                "unit": extract_unit(name),
                "brand": extract_brand(name)
            })
            
        except Exception as e:
            logging.error(f"Error parsing Agora product: {str(e)}")
            continue
            
    return products

def extract_unit(name: str) -> str:
    """Extract unit information from product name."""
    unit_patterns = [
        r'(\d+)\s*(kg|g|ml|l|pcs|pack)',
        r'(\d+)\s*(কেজি|গ্রাম|মিলি|লিটার|পিস|প্যাক)'
    ]
    
    for pattern in unit_patterns:
        match = re.search(pattern, name, re.IGNORECASE)
        if match:
            return match.group(0)
    return None

def extract_brand(name: str) -> str:
    """Extract brand name from product name."""
    # Add known brand patterns here
    brand_patterns = [
        'Fresh', 'Pran', 'Aarong', 'Milk Vita', 'Igloo', 'Danish',
        'ফ্রেশ', 'প্রাণ', 'আরং', 'মিল্কভিটা', 'ইগলু', 'ড্যানিশ'
    ]
    
    for brand in brand_patterns:
        if brand.lower() in name.lower():
            return brand
    return None
