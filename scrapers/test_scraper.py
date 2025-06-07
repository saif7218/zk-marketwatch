import sys
import os
import json
from pathlib import Path
from grocery_scraper import GroceryScraper

def test_scraper(url: str, use_proxy: bool = True):
    """Test the grocery scraper with a given URL"""
    print(f"Testing scraper with URL: {url}")
    print(f"Using proxy: {use_proxy}")
    
    # Initialize the scraper
    scraper = GroceryScraper(use_proxy=use_proxy)
    
    # Scrape the website
    print("\nScraping website...")
    results = scraper.scrape_grocery_prices(url)
    
    if not results:
        print("\nNo results found. The website might be blocking our requests or the structure doesn't match our patterns.")
        return
    
    # Print summary
    print(f"\nFound {len(results)} products:")
    for i, product in enumerate(results[:5], 1):  # Show first 5 products
        print(f"{i}. {product.get('name', 'No name')}: {product.get('price', 'No price')}")
    
    if len(results) > 5:
        print(f"... and {len(results) - 5} more products")
    
    # Save results
    output_file = scraper.save_results(results, f"test_scrape_{len(results)}_products.json")
    print(f"\nResults saved to: {output_file}")
    
    return results

if __name__ == "__main__":
    # Default test URL (Walmart grocery)
    test_url = "https://www.walmart.com/cp/food/976759"
    
    # Use URL from command line if provided
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
    
    # Test with and without proxy to see which works better
    use_proxy = True
    if len(sys.argv) > 2 and sys.argv[2].lower() == 'noproxy':
        use_proxy = False
    
    print(f"Testing with URL: {test_url}")
    print(f"Using proxy: {use_proxy}")
    
    try:
        results = test_scraper(test_url, use_proxy)
        if not results and use_proxy:
            print("\nTrying again without proxy...")
            test_scraper(test_url, use_proxy=False)
    except Exception as e:
        print(f"\nError during scraping: {str(e)}")
        if use_proxy:
            print("Trying again without proxy...")
            try:
                test_scraper(test_url, use_proxy=False)
            except Exception as e2:
                print(f"Error during second attempt: {str(e2)}")
