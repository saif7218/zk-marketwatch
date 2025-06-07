"""
Daraz-specific scraping implementation.
"""

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import logging
import json
from typing import List, Dict, Any

BASE_URL = "https://www.daraz.com.bd"

def scrape_category(category: str) -> List[Dict[str, Any]]:
    """
    Scrape specific category from Daraz.
    
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
            url = urljoin(BASE_URL, f"products/{category}")
            logging.info(f"Scraping Daraz URL: {url}")
            
            page.goto(url, timeout=60000)
            page.wait_for_selector(".product-card", state="attached", timeout=15000)
            
            # Handle lazy loading by scrolling
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
            
            # Wait for dynamic content to load
            page.wait_for_timeout(2000)
            
            # Extract product data from script tags (Daraz uses SSR with hydration)
            scripts = page.eval_on_selector_all("script[type='application/ld+json']", """
                elements => elements.map(el => el.textContent)
            """)
            
            products = []
            for script in scripts:
                try:
                    data = json.loads(script)
                    if isinstance(data, dict) and data.get("@type") == "Product":
                        products.extend(parse_product_json(data, category))
                except json.JSONDecodeError:
                    continue
            
            # Fallback to HTML parsing if JSON extraction fails
            if not products:
                content = page.content()
                products = parse_products(content, category)
            
            return products
            
        except Exception as e:
            logging.error(f"Error scraping Daraz category {category}: {str(e)}")
            return []
            
        finally:
            context.close()
            browser.close()

def parse_product_json(data: Dict[str, Any], category: str) -> List[Dict[str, Any]]:
    """Parse product data from JSON-LD script tags."""
    try:
        price = float(data.get("offers", {}).get("price", 0))
        availability = data.get("offers", {}).get("availability", "")
        in_stock = "InStock" in availability
        
        return [{
            "name": data.get("name", ""),
            "price": price,
            "currency": "BDT",
            "in_stock": in_stock,
            "url": data.get("url", ""),
            "category": category,
            "competitor": "daraz",
            "promotion": None,  # Extract from offers if available
            "unit": extract_unit(data.get("name", "")),
            "brand": data.get("brand", {}).get("name") or extract_brand(data.get("name", ""))
        }]
    except Exception as e:
        logging.error(f"Error parsing Daraz product JSON: {str(e)}")
        return []

def parse_products(html: str, category: str) -> List[Dict[str, Any]]:
    """
    Parse product data from Daraz HTML (fallback method).
    
    Args:
        html: Raw HTML content
        category: Product category being scraped
        
    Returns:
        List of standardized product dictionaries
    """
    soup = BeautifulSoup(html, "html.parser")
    products = []
    
    for item in soup.select(".product-card"):
        try:
            # Extract basic product data
            name = item.select_one(".product-title").get_text(strip=True)
            price_text = item.select_one(".product-price").get_text(strip=True)
            price = float(re.search(r"[\d,]+\.?\d+", price_text)[0].replace(",", ""))
            
            # Check stock status (Daraz shows "Sold out" badge)
            stock_elem = item.select_one(".sold-out-badge")
            in_stock = stock_elem is None
            
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
                "competitor": "daraz",
                "promotion": promotion,
                "unit": extract_unit(name),
                "brand": extract_brand(name)
            })
            
        except Exception as e:
            logging.error(f"Error parsing Daraz product: {str(e)}")
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
