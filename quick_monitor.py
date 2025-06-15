from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re
import logging
from typing import Optional, List, Dict
import json
from datetime import datetime
import concurrent.futures
from apon_system.agents.ai_price_scraper import fetch_products

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="Quick Price Monitor")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Store prices in memory for quick access
price_cache = {}

# Common price patterns
PRICE_PATTERNS = [
    r'৳\s*(\d+\.?\d*)',
    r'Tk\.?\s*(\d+\.?\d*)',
    r'"price"\s*:\s*"?([\d.]+)',
    r'price-amount[^>]*>([\d.]+)',
    r'product-price[^>]*>([\d.]+)',
    r'data-price="([\d.]+)"',
    r'class="price"[^>]*>([\d.]+)'
]

async def extract_price(html: str) -> Optional[float]:
    """Quick price extraction using common patterns"""
    for pattern in PRICE_PATTERNS:
        match = re.search(pattern, html)
        if match:
            try:
                return float(match.group(1).replace(',', ''))
            except:
                continue
    return None

async def get_product_price(url: str, session: aiohttp.ClientSession) -> Dict:
    """Get product price with caching and timeout"""
    if url in price_cache:
        cache_time = price_cache[url]['timestamp']
        if (datetime.now() - cache_time).seconds < 300:  # 5 minutes cache
            return price_cache[url]['data']

    try:
        async with session.get(url, timeout=5) as response:  # Reduced timeout to 5 seconds
            if response.status != 200:
                return {'title': 'Error', 'price': None, 'url': url, 'error': f'HTTP {response.status}'}
            
            html = await response.text()
            price = await extract_price(html)
            soup = BeautifulSoup(html, 'html.parser')
            title = soup.title.string.strip() if soup.title else "Product"
            
            result = {
                'title': title,
                'price': price,
                'url': url,
                'timestamp': datetime.now().strftime('%H:%M:%S')
            }
            
            price_cache[url] = {
                'data': result,
                'timestamp': datetime.now()
            }
            return result
    except asyncio.TimeoutError:
        return {'title': 'Timeout', 'price': None, 'url': url, 'error': 'Request timed out'}
    except Exception as e:
        logger.error(f"Error fetching {url}: {str(e)}")
        return {'title': 'Error', 'price': None, 'url': url, 'error': str(e)}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("quick_monitor.html", {
        "request": request,
        "products": list(price_cache.values())
    })

@app.post("/monitor")
async def monitor_products(urls: str = Form(...)):
    """Monitor multiple products at once with the scraper."""
    url_list = [url.strip() for url in urls.split('\n') if url.strip()]
    results = []

    for url in url_list:
        category_name = url.split('/')[-1]  # Extract category from URL
        products = fetch_products(category_name)
        results.extend([{
            'title': product.title,
            'price': product.price,
            'url': product.url,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        } for product in products])

    return JSONResponse({
        "message": f"Monitored {len(results)} products",
        "results": results
    })

# Create the template file with improved UI
with open("templates/quick_monitor.html", "w", encoding="utf-8") as f:
    f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>Quick Price Monitor</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        async function monitorPrices() {
            const urls = document.getElementById('urls').value;
            const button = document.getElementById('monitorButton');
            const results = document.getElementById('results');
            
            button.disabled = true;
            button.textContent = 'Monitoring...';
            results.innerHTML = '<div class="text-center py-4">Loading...</div>';
            
            try {
                const response = await fetch('/monitor', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                    body: `urls=${encodeURIComponent(urls)}`
                });
                const data = await response.json();
                
                results.innerHTML = data.results.map(product => `
                    <div class="bg-white p-4 rounded-lg shadow mb-4">
                        <h3 class="font-bold text-lg">${product.title}</h3>
                        <p class="text-gray-600 text-sm break-all">${product.url}</p>
                        ${product.price ? 
                            `<p class="text-green-600 font-bold mt-2">৳${product.price}</p>` :
                            `<p class="text-red-600 mt-2">${product.error || 'Price not found'}</p>`
                        }
                        <p class="text-gray-500 text-sm mt-1">Last checked: ${product.timestamp}</p>
                    </div>
                `).join('');
            } catch (error) {
                results.innerHTML = `<div class="text-red-600 text-center py-4">Error: ${error.message}</div>`;
            }
            
            button.disabled = false;
            button.textContent = 'Monitor Prices';
        }
    </script>
</head>
<body class="bg-gray-100">
    <div class="container mx-auto px-4 py-8">
        <h1 class="text-3xl font-bold mb-8 text-center">Quick Price Monitor</h1>
        
        <div class="mb-8 bg-white p-6 rounded-lg shadow">
            <div class="mb-4">
                <label class="block text-gray-700 mb-2">Enter Product URLs (one per line):</label>
                <textarea id="urls" rows="4" class="w-full p-2 border rounded" 
                    placeholder="https://example.com/product1&#10;https://example.com/product2"></textarea>
            </div>
            <button id="monitorButton" onclick="monitorPrices()" 
                class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
                Monitor Prices
            </button>
        </div>

        <div id="results" class="grid gap-4">
            {% for product in products %}
            <div class="bg-white p-4 rounded-lg shadow">
                <h3 class="font-bold text-lg">{{ product.data.title }}</h3>
                <p class="text-gray-600 text-sm break-all">{{ product.data.url }}</p>
                {% if product.data.price %}
                <p class="text-green-600 font-bold mt-2">৳{{ product.data.price }}</p>
                {% else %}
                <p class="text-red-600 mt-2">{{ product.data.error or 'Price not found' }}</p>
                {% endif %}
                <p class="text-gray-500 text-sm mt-1">Last checked: {{ product.data.timestamp }}</p>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
''')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "quick_monitor:app", 
        host="127.0.0.1", 
        port=8000,
        reload=True,
        workers=1,
        ssl_keyfile=None,  # Disable SSL
        ssl_certfile=None  # Disable SSL
    )