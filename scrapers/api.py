from flask import Flask, request, jsonify
from langchain_agent import run_agent
from grocery_scraper import GroceryScraper
import os
from pathlib import Path
from datetime import datetime
import json

app = Flask(__name__)
scraper = GroceryScraper(use_proxy=True)

# Ensure data directory exists
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

def get_latest_scraped_data():
    """Get the most recently scraped data file"""
    json_files = list(data_dir.glob("scraped_*.json"))
    if not json_files:
        return None
    
    latest_file = max(json_files, key=os.path.getmtime)
    with open(latest_file, 'r', encoding='utf-8') as f:
        return json.load(f)

@app.route('/api/scrape', methods=['POST'])
def scrape_website():
    """API endpoint to scrape a website for grocery prices"""
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({"error": "URL is required"}), 400
    
    try:
        results = scraper.scrape_grocery_prices(url)
        if not results:
            return jsonify({"error": "No products found on the page"}), 404
        
        # Save the results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"scraped_{timestamp}.json"
        filepath = scraper.save_results(results, filename)
        
        return jsonify({
            "status": "success",
            "results_count": len(results),
            "saved_to": filepath,
            "data": results[:10]  # Return first 10 items
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/query', methods=['POST'])
def query_agent():
    """API endpoint to query the LangChain agent"""
    data = request.get_json()
    query = data.get('query')
    
    if not query:
        return jsonify({"error": "Query is required"}), 400
    
    try:
        result = run_agent(query)
        return jsonify({
            "status": "success",
            "response": result
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/prices', methods=['GET'])
def get_prices():
    """API endpoint to get the latest scraped prices"""
    try:
        data = get_latest_scraped_data()
        if not data:
            return jsonify({"error": "No price data available"}), 404
            
        return jsonify({
            "status": "success",
            "count": len(data),
            "data": data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    # Create data directory if it doesn't exist
    data_dir.mkdir(exist_ok=True, parents=True)
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
