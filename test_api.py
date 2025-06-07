import requests
import json
import time

def test_api():
    base_url = "http://localhost:5000"
    
    print("Testing API endpoints...")
    print("=======================\n")
    
    # Test health check
    print("1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/api/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}\n")
    except Exception as e:
        print(f"Error: {e}\n")
    
    # Test scraping
    test_url = "https://www.walmart.com/cp/food/976759"
    print(f"2. Testing scraping with URL: {test_url}")
    try:
        response = requests.post(
            f"{base_url}/api/scrape",
            json={"url": test_url},
            headers={"Content-Type": "application/json"}
        )
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Scraped {result.get('results_count', 0)} products")
            if 'data' in result and len(result['data']) > 0:
                print("Sample product:")
                print(json.dumps(result['data'][0], indent=2))
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n3. Testing getting latest prices...")
    try:
        response = requests.get(f"{base_url}/api/prices")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if 'data' in result and len(result['data']) > 0:
                print(f"Found {len(result['data'])} products")
                print("Sample product:")
                print(json.dumps(result['data'][0], indent=2))
            else:
                print("No price data available")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test querying the AI agent
    print("\n4. Testing AI agent query...")
    try:
        response = requests.post(
            f"{base_url}/api/query",
            json={"query": "What's the average price of eggs?"},
            headers={"Content-Type": "application/json"}
        )
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("AI Response:")
            print(json.dumps(result.get('response', 'No response'), indent=2))
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Apon AI - API Test Script")
    print("==========================\n")
    
    print("Make sure the backend API is running before testing.")
    print("You can start it by running: python scrapers/api.py\n")
    
    input("Press Enter to start testing...")
    print()
    
    test_api()
    
    print("\nTest completed. Press Enter to exit...")
    input()
