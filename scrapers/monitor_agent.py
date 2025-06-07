import time
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import requests
from dataclasses import dataclass, asdict, field
import schedule
import pytz
from grocery_scraper import GroceryScraper

# Configuration
CONFIG = {
    "monitoring_interval_minutes": 60,  # How often to check for price changes
    "price_change_threshold_percent": 5.0,  # Minimum price change to trigger notification
    "data_retention_days": 30,  # How long to keep historical data
    "max_products_per_retailer": 100,  # Maximum number of products to track per retailer
    "timezone": "Asia/Dhaka"  # Timezone for notifications
}

@dataclass
class PriceEntry:
    price: float
    timestamp: str
    url: str

@dataclass
class Product:
    id: str
    name: str
    current_price: float
    retailer: str
    url: str
    image_url: str = ""
    price_history: List[PriceEntry] = field(default_factory=list)
    last_updated: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    price_change_24h: float = 0.0
    price_change_7d: float = 0.0
    lowest_price_30d: Optional[float] = None
    highest_price_30d: Optional[float] = None

class MonitorAgent:
    def __init__(self, data_dir: str = "data/monitoring"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.products_file = self.data_dir / "products.json"
        self.scraper = GroceryScraper(use_proxy=True)
        self.products: Dict[str, Product] = self._load_products()
        self.timezone = pytz.timezone(CONFIG["timezone"])
    
    def _load_products(self) -> Dict[str, Product]:
        """Load existing products from disk"""
        if not self.products_file.exists():
            return {}
        
        with open(self.products_file, 'r') as f:
            data = json.load(f)
            
        products = {}
        for product_id, product_data in data.items():
            # Convert price history entries to PriceEntry objects
            price_history = [
                PriceEntry(entry['price'], entry['timestamp'], entry['url'])
                for entry in product_data.get('price_history', [])
            ]
            
            # Create Product instance
            product = Product(
                id=product_data['id'],
                name=product_data['name'],
                current_price=product_data['current_price'],
                retailer=product_data['retailer'],
                url=product_data['url'],
                image_url=product_data.get('image_url', ''),
                price_history=price_history,
                last_updated=product_data.get('last_updated'),
                price_change_24h=product_data.get('price_change_24h', 0.0),
                price_change_7d=product_data.get('price_change_7d', 0.0),
                lowest_price_30d=product_data.get('lowest_price_30d'),
                highest_price_30d=product_data.get('highest_price_30d')
            )
            products[product_id] = product
            
        return products
    
    def save_products(self):
        """Save products to disk"""
        # Convert products to serializable format
        serializable = {
            pid: {
                **asdict(product),
                'price_history': [asdict(entry) for entry in product.price_history]
            }
            for pid, product in self.products.items()
        }
        
        # Save to file atomically
        temp_file = self.products_file.with_suffix('.tmp')
        with open(temp_file, 'w') as f:
            json.dump(serializable, f, indent=2)
        temp_file.replace(self.products_file)
    
    def generate_product_id(self, name: str, retailer: str) -> str:
        """Generate a unique ID for a product"""
        import hashlib
        return hashlib.md5(f"{name}_{retailer}".encode()).hexdigest()
    
    def add_product(self, url: str, name: str, price: float, retailer: str, image_url: str = "") -> str:
        """Add a new product to monitor"""
        product_id = self.generate_product_id(name, retailer)
        
        if product_id in self.products:
            return product_id  # Already tracking this product
        
        # Create price history entry
        price_entry = PriceEntry(
            price=price,
            timestamp=datetime.utcnow().isoformat(),
            url=url
        )
        
        # Create new product
        product = Product(
            id=product_id,
            name=name,
            current_price=price,
            retailer=retailer,
            url=url,
            image_url=image_url,
            price_history=[price_entry],
            lowest_price_30d=price,
            highest_price_30d=price
        )
        
        self.products[product_id] = product
        self.save_products()
        return product_id
    
    def update_product_price(self, product_id: str, new_price: float, url: str) -> bool:
        """Update a product's price and return True if the price changed significantly"""
        if product_id not in self.products:
            return False
        
        product = self.products[product_id]
        old_price = product.current_price
        
        # Calculate price change percentage
        if old_price > 0:
            price_change_pct = ((new_price - old_price) / old_price) * 100
        else:
            price_change_pct = 0.0
        
        # Only update if price changed
        if abs(price_change_pct) >= 0.01:  # At least 0.01% change
            # Add to price history
            price_entry = PriceEntry(
                price=new_price,
                timestamp=datetime.utcnow().isoformat(),
                url=url
            )
            product.price_history.append(price_entry)
            
            # Update product data
            product.current_price = new_price
            product.last_updated = datetime.utcnow().isoformat()
            
            # Update price statistics
            self._update_price_statistics(product)
            
            # Clean up old price history
            self._cleanup_old_entries(product)
            
            self.save_products()
            return True
            
        return False
    
    def _update_price_statistics(self, product: Product):
        """Update price change statistics for a product"""
        now = datetime.utcnow()
        prices_24h = []
        prices_7d = []
        prices_30d = []
        
        for entry in product.price_history:
            entry_time = datetime.fromisoformat(entry.timestamp.replace('Z', '+00:00'))
            age = now - entry_time
            
            if age <= timedelta(days=1):
                prices_24h.append(entry.price)
            if age <= timedelta(days=7):
                prices_7d.append(entry.price)
            if age <= timedelta(days=30):
                prices_30d.append(entry.price)
        
        # Calculate price changes
        if prices_24h and len(prices_24h) > 1:
            product.price_change_24h = ((prices_24h[-1] - prices_24h[0]) / prices_24h[0]) * 100
        
        if prices_7d and len(prices_7d) > 1:
            product.price_change_7d = ((prices_7d[-1] - prices_7d[0]) / prices_7d[0]) * 100
        
        # Update 30-day high/low
        if prices_30d:
            product.lowest_price_30d = min(prices_30d)
            product.highest_price_30d = max(prices_30d)
    
    def _cleanup_old_entries(self, product: Product):
        """Remove price history entries older than 30 days"""
        cutoff = datetime.utcnow() - timedelta(days=30)
        product.price_history = [
            entry for entry in product.price_history
            if datetime.fromisoformat(entry.timestamp.replace('Z', '+00:00')) >= cutoff
        ]
    
    def check_price_changes(self, url: str) -> List[dict]:
        """Check for price changes on a retailer's page"""
        print(f"Checking for price changes: {url}")
        
        try:
            # Scrape the page
            results = self.scraper.scrape_grocery_prices(url)
            if not results:
                print(f"No products found on {url}")
                return []
            
            # Extract domain for retailer name
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            
            changes = []
            
            # Process each product
            for product_data in results[:CONFIG["max_products_per_retailer"]]:
                try:
                    # Extract price (handle different price formats)
                    price_str = ''.join(c for c in product_data['price'] if c.isdigit() or c == '.')
                    if not price_str:
                        continue
                        
                    price = float(price_str)
                    
                    # Generate product ID
                    product_id = self.generate_product_id(product_data['name'], domain)
                    
                    # Add or update product
                    if product_id not in self.products:
                        self.add_product(
                            url=url,
                            name=product_data['name'],
                            price=price,
                            retailer=domain,
                            image_url=product_data.get('image_url', '')
                        )
                        changes.append({
                            'product_id': product_id,
                            'name': product_data['name'],
                            'type': 'new_product',
                            'price': price,
                            'retailer': domain,
                            'url': url
                        })
                    else:
                        # Check for price changes
                        if self.update_product_price(product_id, price, url):
                            product = self.products[product_id]
                            changes.append({
                                'product_id': product_id,
                                'name': product.name,
                                'type': 'price_change',
                                'old_price': product.price_history[-2].price if len(product.price_history) > 1 else price,
                                'new_price': price,
                                'change_percent': ((price - product.price_history[-2].price) / product.price_history[-2].price * 100) 
                                                  if len(product.price_history) > 1 else 0,
                                'retailer': domain,
                                'url': url
                            })
                except Exception as e:
                    print(f"Error processing product: {e}")
                    continue
            
            return changes
            
        except Exception as e:
            print(f"Error checking {url}: {e}")
            return []
    
    def monitor_urls(self, urls: List[str]):
        """Monitor a list of URLs for price changes"""
        all_changes = []
        
        for url in urls:
            changes = self.check_price_changes(url)
            all_changes.extend(changes)
            
            # Add a small delay between requests
            time.sleep(2)
        
        return all_changes
    
    def schedule_monitoring(self, urls: List[str], interval_minutes: int = None):
        """Schedule periodic monitoring of URLs"""
        interval = interval_minutes or CONFIG["monitoring_interval_minutes"]
        
        def job():
            print(f"\n=== Running scheduled check at {datetime.now().isoformat()} ===")
            changes = self.monitor_urls(urls)
            
            if changes:
                print(f"\n=== Found {len(changes)} changes ===")
                for change in changes:
                    if change['type'] == 'price_change':
                        print(f"Price change: {change['name']} - {change['change_percent']:.2f}%")
                    else:
                        print(f"New product: {change['name']} - ${change['price']:.2f}")
            else:
                print("No changes detected.")
            
            print("=" * 50)
        
        # Run immediately
        job()
        
        # Then schedule periodic checks
        schedule.every(interval).minutes.do(job)
        
        print(f"Monitoring {len(urls)} URLs every {interval} minutes...")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping monitoring...")
            self.save_products()

# Example usage
if __name__ == "__main__":
    # Example URLs to monitor
    urls_to_monitor = [
        "https://www.walmart.com/cp/food/976759",
        "https://www.target.com/c/grocery/-/N-5xt1a"
    ]
    
    # Create and start monitoring
    monitor = MonitorAgent()
    monitor.schedule_monitoring(urls_to_monitor, interval_minutes=60)
