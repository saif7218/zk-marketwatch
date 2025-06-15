import requests
from bs4 import BeautifulSoup
import re
import random
from urllib.parse import urlparse
from fake_useragent import UserAgent
from typing import List, Dict, Any, Optional
import json
import os
from pathlib import Path

class GroceryScraper:
    def __init__(self, use_proxy: bool = True):
        self.ua = UserAgent()
        self.use_proxy = use_proxy
        self.proxies = self._get_free_proxies()
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
    def _get_free_proxies(self) -> list:
        """Get a list of free proxies"""
        return [
            "http://45.79.189.142:80",
            "http://190.64.18.177:80",
            "http://45.79.189.143:80",
            "http://45.79.189.144:80"
        ]
    
    def _get_random_headers(self) -> dict:
        """Generate random headers to avoid bot detection"""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def _make_request(self, url: str, max_retries: int = 3) -> Optional[requests.Response]:
        """Make HTTP request with retries and proxy rotation"""
        headers = self._get_random_headers()
        
        for attempt in range(max_retries):
            try:
                proxy = {"http": random.choice(self.proxies), "https": random.choice(self.proxies)} \
                    if self.use_proxy else None
                
                response = requests.get(
                    url, 
                    headers=headers, 
                    proxies=proxy,
                    timeout=10
                )
                response.raise_for_status()
                return response
                
            except (requests.RequestException, ConnectionError) as e:
                print(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    print(f"Failed to fetch {url} after {max_retries} attempts")
                    return None
    
    def scrape_grocery_prices(self, url: str) -> List[Dict[str, Any]]:
        """Scrape grocery prices from a given URL"""
        print(f"Scraping {url}...")
        response = self._make_request(url)
        if not response:
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        domain = urlparse(url).netloc
        
        # Common patterns for grocery items
        item_patterns = [
            r'\b(?:egg|noodle|rice|flour|pasta|oil|sugar|salt|milk|bread|butter|cheese|yogurt|chicken|beef|fish|vegetable|fruit|apple|banana|orange)\b',
            r'\b(?:potato|tomato|onion|garlic|ginger|chili|meat|fish|juice|water|soda|coffee|tea|biscuit|chocolate|snack|cereal|noodle|soup|sauce|spice|herb)\b'
        ]
        
        results = []
        seen = set()
        
        # Look for product containers
        product_containers = soup.find_all(['div', 'li', 'article', 'section'], class_=re.compile(r'(?i)(product|item|card|container)'))
        
        for container in product_containers:
            text = container.get_text(' ', strip=True)
            
            # Skip if no relevant text
            if not any(re.search(pattern, text, re.IGNORECASE) for pattern in item_patterns):
                continue
                
            # Extract product name (simplified)
            name_elem = container.find(['h1', 'h2', 'h3', 'h4', 'div'], class_=re.compile(r'(?i)(title|name|product)'))
            name = name_elem.get_text(strip=True) if name_elem else 'Unknown Product'
            
            # Skip if we've already seen this product
            if name in seen:
                continue
                
            seen.add(name)
            
            # Extract price
            price_match = re.search(r'\$\s*\d+(?:\.\d{2})?|\d+(?:\.\d{2})?\s*(?:USD|BDT|\$)', text)
            price = price_match.group() if price_match else 'Price not found'
            
            # Extract image if available
            img = container.find('img')
            image_url = img['src'] if img and 'src' in img.attrs else ''
            
            results.append({
                'name': name,
                'price': price,
                'source': domain,
                'image': image_url,
                'timestamp': str(datetime.datetime.utcnow())
            })
        
        return results
    
    def save_results(self, results: List[Dict[str, Any]], filename: str = 'scraped_products.json') -> str:
        """Save scraped results to a JSON file"""
        filepath = self.data_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        return str(filepath)
    
    def load_results(self, filename: str = 'scraped_products.json') -> List[Dict[str, Any]]:
        """Load previously scraped results"""
        filepath = self.data_dir / filename
        if not filepath.exists():
            return []
            
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

if __name__ == "__main__":
    import datetime
    
    # Example usage
    scraper = GroceryScraper()
    test_urls = [
        "https://www.walmart.com/cp/food/976759",
        "https://www.target.com/c/grocery/-/N-5xt1a"
    ]
    
    all_results = []
    for url in test_urls:
        try:
            results = scraper.scrape_grocery_prices(url)
            all_results.extend(results)
            print(f"Found {len(results)} products on {url}")
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
    
    if all_results:
        output_file = scraper.save_results(all_results)
        print(f"Saved {len(all_results)} products to {output_file}")
