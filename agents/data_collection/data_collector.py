import os
from playwright.sync_api import sync_playwright
import pandas as pd
from typing import List, Dict, Any

COMPETITOR_URLS = {
    "Shwapno": "https://www.shwapno.com",
    "Agora": "https://www.agora-supermarket.com",
    "Meena Bazar": "https://www.meenaclick.com"
}

def collect_competitor_data(competitors: List[str], categories: List[str]) -> pd.DataFrame:
    """
    Collects product data from specified competitors and categories using Playwright.
    
    Args:
        competitors: List of competitor names to scrape
        categories: List of product categories to track
        
    Returns:
        DataFrame containing collected product data
    """
    results = {}
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        
        for competitor in competitors:
            if competitor not in COMPETITOR_URLS:
                print(f"Warning: No URL configured for competitor {competitor}")
                continue
                
            competitor_data = []
            context = browser.new_context()
            
            try:
                for category in categories:
                    page = context.new_page()
                    try:
                        url = f"{COMPETITOR_URLS[competitor]}/{category}"
                        print(f"Scraping {url}...")
                        
                        page.goto(url)
                        page.wait_for_selector('.product-item', timeout=15000)
                        
                        products = page.query_selector_all('.product-item')
                        for product in products:
                            try:
                                name = product.query_selector('.product-name').inner_text()
                                price = float(product.query_selector('.price')
                                           .inner_text()
                                           .replace('৳', '')
                                           .strip())
                                in_stock = "Out of Stock" not in product.inner_text()
                                
                                competitor_data.append({
                                    "name": name,
                                    "price": price,
                                    "category": category,
                                    "in_stock": in_stock,
                                    "competitor": competitor,
                                    "url": url,
                                    "timestamp": pd.Timestamp.now()
                                })
                            except Exception as e:
                                print(f"Error processing product in {url}: {str(e)}")
                                continue
                                
                    except Exception as e:
                        print(f"Error scraping category {category} for {competitor}: {str(e)}")
                    finally:
                        page.close()
                        
            except Exception as e:
                print(f"Error processing competitor {competitor}: {str(e)}")
            finally:
                context.close()
                
            results[competitor] = competitor_data
            
        browser.close()
    
    # Convert all results to DataFrame
    df = pd.DataFrame([
        item for sublist in results.values() 
        for item in sublist
    ])
    
    if df.empty:
        print("Warning: No data collected!")
        return pd.DataFrame()
        
    return df

if __name__ == "__main__":
    # Example usage
    competitors = ["Shwapno", "Agora", "Meena Bazar"]
    categories = ["dairy", "snacks", "beverages"]
    
    df = collect_competitor_data(competitors, categories)
    print(f"\nCollected {len(df)} products:")
    print(df.head())
    
    # Save to CSV for analysis
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/latest_collection.csv', index=False)
    print("\nData saved to data/latest_collection.csv")
