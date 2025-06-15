import requests
import json
import time

# Test the FastAPI endpoint
def test_scrape_endpoint():
    url = "http://localhost:8000/price-monitor/scrape"
    test_urls = [
        # Add test URLs here
        # Example: "https://www.walmart.com/ip/Great-Value-Large-White-Eggs-12-Count-24-Oz/145087678"
    ]
    
    if not test_urls:
        test_url = input("Enter a URL to test: ")
        test_urls = [test_url]
    
    for test_url in test_urls:
        try:
            print(f"\nTesting URL: {test_url}")
            start_time = time.time()
            
            response = requests.post(
                url,
                json={"url": test_url},
                timeout=60  # 60 seconds timeout
            )
            
            response.raise_for_status()
            data = response.json()
            
            print(f"Status: {response.status_code}")
            print(f"Time taken: {time.time() - start_time:.2f} seconds")
            
            if 'items' in data:
                print(f"\nFound {len(data['items'])} items:")
                for i, item in enumerate(data['items'][:10], 1):  # Show first 10 items
                    print(f"{i}. {item['item']} - ${item['price']}")
                if len(data['items']) > 10:
                    print(f"... and {len(data['items']) - 10} more items")
            else:
                print("No items found or error occurred:")
                print(json.dumps(data, indent=2))
                
        except requests.exceptions.RequestException as e:
            print(f"Error testing {test_url}:")
            print(str(e))
        except json.JSONDecodeError as e:
            print(f"Invalid JSON response from server:")
            print(response.text[:500])  # Print first 500 chars of response
        except Exception as e:
            print(f"Unexpected error:")
            print(str(e))

if __name__ == "__main__":
    print("Starting price monitor service test...")
    test_scrape_endpoint()
