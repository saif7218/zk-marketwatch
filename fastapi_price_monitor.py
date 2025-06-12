from fastapi import FastAPI, Request, Form, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests
from bs4 import BeautifulSoup
import re
from typing import Optional, Dict, Any, List
import threading
import time
from pydantic import BaseModel
import os
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import uvicorn
import asyncio
import aiohttp
from datetime import datetime
import json
import logging
from urllib.parse import urljoin, urlparse
import random
import backoff
from aiohttp import ClientTimeout
import asyncio
from concurrent.futures import ThreadPoolExecutor
import importlib

# Set up logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- CONFIG ---
DB_PATH = 'data/monitor.db'
EMAIL_ALERTS = True
EMAIL_FROM = 'your_email@gmail.com'
EMAIL_PASSWORD = 'your_password'
EMAIL_SMTP = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_TO = 'alert_recipient@gmail.com'

# --- APP INIT ---
app = FastAPI(title="Apon Family Mart – Price Monitor")
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)
os.makedirs("data", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- DB INIT ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products (
        url TEXT PRIMARY KEY,
        title TEXT,
        price REAL,
        last_price REAL,
        lang TEXT DEFAULT 'bn',
        last_checked TEXT
    )''')
    conn.commit()
    conn.close()
init_db()

# --- EMAIL ALERT ---
def send_email_alert(title, url, old_price, new_price):
    if not EMAIL_ALERTS:
        return
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = EMAIL_TO
        msg['Subject'] = f"Price Alert: {title}"
        body = f"Price changed for {title}\nURL: {url}\nOld Price: {old_price}\nNew Price: {new_price}"
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP(EMAIL_SMTP, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"Email alert failed: {e}")

# --- SCRAPER ---
def extract_price(html: str) -> Optional[float]:
    patterns = [r'৳\s*(\d+\.?\d*)', r'Tk\.?\s*(\d+\.?\d*)', r'"price"\s*:\s*"?([\d.]+)']
    for pattern in patterns:
        match = re.findall(pattern, html)
        if match:
            try:
                return float(match[0].replace(',', ''))
            except:
                continue
    return None

def get_product_info(url: str) -> Dict[str, Any]:
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=15)
        res.raise_for_status()
        html = res.text
        price = extract_price(html)
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.title.string.strip() if soup.title else "Unnamed Product"
        return {"title": title, "price": price, "url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to scrape: {e}")

# --- DB HELPERS ---
def save_product(info, lang='bn'):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT price FROM products WHERE url=?', (info['url'],))
    row = c.fetchone()
    last_price = row[0] if row else None
    c.execute('''INSERT OR REPLACE INTO products (url, title, price, last_price, lang, last_checked) VALUES (?, ?, ?, ?, ?, datetime('now'))''',
        (info['url'], info['title'], info['price'], last_price, lang))
    conn.commit()
    conn.close()
    return last_price

def get_all_products(lang='bn'):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT url, title, price, last_price, last_checked FROM products WHERE lang=?', (lang,))
    rows = c.fetchall()
    conn.close()
    return [
        {"url": url, "title": title, "price": price, "last_price": last_price, "last_checked": last_checked}
        for url, title, price, last_price, last_checked in rows
    ]

# --- AGENT ---
def price_monitor_agent():
    while True:
        products = get_all_products()
        for prod in products:
            try:
                info = get_product_info(prod['url'])
                last_price = prod['price']
                if info['price'] is not None and last_price is not None and info['price'] != last_price:
                    send_email_alert(info['title'], info['url'], last_price, info['price'])
                save_product(info)
            except Exception as e:
                print(f"Monitor error: {e}")
        import time; time.sleep(60)  # Fast re-check

threading.Thread(target=price_monitor_agent, daemon=True).start()

# --- API & UI ---
class ProductRequest(BaseModel):
    url: str
    interval: Optional[int] = 300
    lang: Optional[str] = 'bn'

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, lang: str = 'bn'):
    products = get_all_products(lang)
    return templates.TemplateResponse("index_tailwind.html", {"request": request, "products": products, "lang": lang})

def crawl_for_products(main_url: str, max_products: int = 20) -> list:
    """Crawl the main site for product links and return a list of product URLs."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(main_url, headers=headers, timeout=15)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        product_links = set()
        # Heuristic: look for <a> tags with href containing 'product' or similar
        for a in soup.find_all('a', href=True):
            href = a['href']
            if any(x in href.lower() for x in ['product', 'item', 'sku', 'goods', 'shop', 'details']):
                # Make absolute URL
                if href.startswith('http'): url = href
                elif href.startswith('/'): url = main_url.rstrip('/') + href
                else: url = main_url.rstrip('/') + '/' + href
                product_links.add(url)
            if len(product_links) >= max_products:
                break
        return list(product_links)
    except Exception as e:
        print(f"Crawl error: {e}")
        return []

@app.post("/monitor")
async def monitor_product(
    url: str = Form(...),
    lang: str = Form('bn'),
    interval: int = Form(300)
):
    # If the URL is a main site, crawl for product links
    if not any(x in url.lower() for x in ['product', 'item', 'sku', 'goods', 'shop', 'details']):
        product_urls = crawl_for_products(url)
        results = []
        for purl in product_urls:
            try:
                info = get_product_info(purl)
                save_product(info, lang=lang)
                results.append(info)
            except Exception as e:
                results.append({'url': purl, 'error': str(e)})
        return {"message": f"Crawled and monitoring {len(results)} products.", "data": results}
    # Otherwise, treat as a single product
    info = get_product_info(url)
    save_product(info, lang=lang)
    return {"message": "Monitoring started", "data": info}

@app.get("/switch-lang/{lang}", response_class=RedirectResponse)
async def switch_lang(lang: str):
    return RedirectResponse(f"/?lang={lang}", status_code=303)

# Minimal dashboard template for demonstration
with open("templates/dashboard.html", "w", encoding="utf-8") as f:
    f.write('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Price Monitor Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f4f4f9; margin: 0; padding: 0; }
        .container { max-width: 700px; margin: 40px auto; background: #fff; border-radius: 10px; box-shadow: 0 2px 8px #0001; padding: 30px; }
        h1 { text-align: center; color: #4f46e5; }
        form { display: flex; gap: 10px; margin-bottom: 30px; }
        input, button { padding: 10px; border-radius: 5px; border: 1px solid #ddd; }
        button { background: #4f46e5; color: #fff; border: none; cursor: pointer; }
        button:hover { background: #3730a3; }
        .product { border-bottom: 1px solid #eee; padding: 15px 0; display: flex; align-items: center; gap: 15px; }
        .product img { width: 60px; height: 60px; object-fit: contain; border-radius: 8px; background: #fafafa; }
        .product-info { flex: 1; }
        .product-title { font-weight: bold; color: #333; }
        .product-url { font-size: 0.9em; color: #888; }
        .product-price { color: #22c55e; font-size: 1.2em; font-weight: bold; }
        .product-error { color: #ef4444; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Price Monitor Dashboard</h1>
        <form method="post" action="/monitor">
            <input type="url" name="url" placeholder="Product URL" required style="flex:2">
            <input type="number" name="interval" value="300" min="60" style="width:100px" title="Interval (seconds)">
            <button type="submit">Monitor</button>
        </form>
        {% for product in products %}
        <div class="product">
            {% if product.image_url %}<img src="{{ product.image_url }}" alt="Product Image">{% endif %}
            <div class="product-info">
                <div class="product-title">{{ product.title }}</div>
                <div class="product-url"><a href="{{ product.url }}" target="_blank">{{ product.url }}</a></div>
                {% if product.price %}
                <div class="product-price">৳{{ '%.2f' % product.price }}</div>
                {% elif product.error %}
                <div class="product-error">Error: {{ product.error }}</div>
                {% else %}
                <div class="product-error">Price not found</div>
                {% endif %}
                <div style="font-size:0.8em;color:#888;">Last checked: {{ product.last_checked }}</div>
            </div>
        </div>
        {% endfor %}
    </div>
</body>
</html>
''')

# Email configuration
EMAIL_CONFIG = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "",  # Add your email here
    "sender_password": "",  # Add your app password here
    "recipient_email": ""  # Add recipient email here
}

# Rate limiting configuration
RATE_LIMIT = {
    "requests_per_second": 2,
    "delay_between_requests": 0.5,
    "max_retries": 3,
    "retry_delay": 1
}

# Store monitored products with persistence
PRODUCTS_FILE = "monitored_products.json"

def load_monitored_products():
    """Load monitored products from file."""
    try:
        if os.path.exists(PRODUCTS_FILE):
            with open(PRODUCTS_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading monitored products: {str(e)}")
    return {}

def save_monitored_products():
    """Save monitored products to file."""
    try:
        with open(PRODUCTS_FILE, 'w') as f:
            json.dump(monitored_products, f)
    except Exception as e:
        logger.error(f"Error saving monitored products: {str(e)}")

# Initialize monitored products
monitored_products = load_monitored_products()

def is_valid_url(url: str) -> bool:
    """Check if URL is valid and has a scheme."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def normalize_url(url: str) -> str:
    """Normalize URL by adding scheme if missing."""
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url

@backoff.on_exception(backoff.expo, Exception, max_tries=3)
async def send_email_alert(product_url: str, old_price: float, new_price: float):
    """Send email alert for price changes with retry logic."""
    if not all([EMAIL_CONFIG["sender_email"], EMAIL_CONFIG["sender_password"], EMAIL_CONFIG["recipient_email"]]):
        logger.warning("Email configuration is incomplete. Skipping email alert.")
        return

    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG["sender_email"]
        msg['To'] = EMAIL_CONFIG["recipient_email"]
        msg['Subject'] = f"Price Alert: {product_url}"

        body = f"""
        Price change detected!
        
        Product URL: {product_url}
        Old Price: ${old_price:.2f}
        New Price: ${new_price:.2f}
        Change: ${new_price - old_price:.2f}
        
        Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"]) as server:
            server.starttls()
            server.login(EMAIL_CONFIG["sender_email"], EMAIL_CONFIG["sender_password"])
            server.send_message(msg)
            
        logger.info(f"Email alert sent for {product_url}")
    except Exception as e:
        logger.error(f"Failed to send email alert: {str(e)}")
        raise

async def fetch_with_retry(session: aiohttp.ClientSession, url: str, headers: dict) -> Optional[str]:
    """Fetch URL with retry logic."""
    for attempt in range(RATE_LIMIT["max_retries"]):
        try:
            async with session.get(url, headers=headers, timeout=ClientTimeout(total=30)) as response:
                if response.status == 200:
                    return await response.text()
                elif response.status == 429:  # Too Many Requests
                    wait_time = int(response.headers.get('Retry-After', RATE_LIMIT["retry_delay"]))
                    logger.warning(f"Rate limited. Waiting {wait_time} seconds.")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Failed to fetch {url}: Status {response.status}")
                    await asyncio.sleep(RATE_LIMIT["retry_delay"])
        except Exception as e:
            logger.error(f"Error fetching {url} (attempt {attempt + 1}): {str(e)}")
            if attempt < RATE_LIMIT["max_retries"] - 1:
                await asyncio.sleep(RATE_LIMIT["retry_delay"])
    return None

async def extract_product_links(url: str, session: aiohttp.ClientSession) -> list:
    """Extract product links from a website with improved error handling."""
    try:
        # Try simple HTTP request first
        async with session.get(url, timeout=30) as response:
            if response.status == 200:
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
                product_patterns = [
                    r'/product/', r'/item/', r'/p/', r'/products/', r'/shop/', r'/catalog/', r'/buy/', r'/store/', r'/goods/'
                ]
                product_links = set()
                base_domain = urlparse(url).netloc
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    full_url = urljoin(url, href)
                    if (urlparse(full_url).netloc == base_domain and any(pattern in full_url.lower() for pattern in product_patterns)):
                        product_links.add(full_url)
                logger.info(f"Found {len(product_links)} product links on {url}")
                return list(product_links)
    except Exception as e:
        logger.error(f"Error in HTTP request: {str(e)}")
    
    # If HTTP request fails, try Playwright
    try:
        playwright = importlib.import_module('playwright.async_api')
        async with playwright.async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )
            page = await context.new_page()
            await page.goto(url, timeout=30000, wait_until='domcontentloaded')
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            product_links = set()
            base_domain = urlparse(url).netloc
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(url, href)
                if (urlparse(full_url).netloc == base_domain and any(pattern in full_url.lower() for pattern in product_patterns)):
                    product_links.add(full_url)
            await browser.close()
            logger.info(f"[Playwright] Found {len(product_links)} product links on {url}")
            return list(product_links)
    except Exception as e:
        logger.error(f"[Playwright] Error: {str(e)}")
        return []

async def monitor_price(url: str) -> float:
    """Monitor product price with improved error handling."""
    try:
        # Try simple HTTP request first
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=30) as response:
                if response.status == 200:
                    content = await response.text()
                    price_patterns = [
                        r'\$\d+\.?\d*', r'\d+\.?\d*\s*€', r'\d+\.?\d*\s*£',
                        r'price["\']?\s*:?\s*["\']?\$?\d+\.?\d*', r'data-price=["\']?\$?\d+\.?\d*',
                        r'class=["\']?price["\']?[^>]*>\s*\$?\d+\.?\d*', r'itemprop=["\']?price["\']?[^>]*>\s*\$?\d+\.?\d*'
                    ]
                    for pattern in price_patterns:
                        price_match = re.search(pattern, content)
                        if price_match:
                            price_str = re.search(r'\d+\.?\d*', price_match.group())
                            if price_str:
                                return float(price_str.group())
    except Exception as e:
        logger.error(f"Error in HTTP request: {str(e)}")
    
    # If HTTP request fails, try Playwright
    try:
        playwright = importlib.import_module('playwright.async_api')
        async with playwright.async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )
            page = await context.new_page()
            await page.goto(url, timeout=30000, wait_until='domcontentloaded')
            content = await page.content()
            price_patterns = [
                r'\$\d+\.?\d*', r'\d+\.?\d*\s*€', r'\d+\.?\d*\s*£',
                r'price["\']?\s*:?\s*["\']?\$?\d+\.?\d*', r'data-price=["\']?\$?\d+\.?\d*',
                r'class=["\']?price["\']?[^>]*>\s*\$?\d+\.?\d*', r'itemprop=["\']?price["\']?[^>]*>\s*\$?\d+\.?\d*'
            ]
            for pattern in price_patterns:
                price_match = re.search(pattern, content)
                if price_match:
                    price_str = re.search(r'\d+\.?\d*', price_match.group())
                    if price_str:
                        price = float(price_str.group())
                        await browser.close()
                        return price
            await browser.close()
            return None
    except Exception as e:
        logger.error(f"[Playwright] Error: {str(e)}")
        return None

async def monitor_website(url: str):
    """Monitor all products on a website."""
    try:
        url = normalize_url(url)
        if not is_valid_url(url):
            logger.error(f"Invalid URL: {url}")
            return

        async with aiohttp.ClientSession() as session:
            product_links = await extract_product_links(url, session)
            
            if not product_links:
                logger.warning(f"No product links found on {url}")
                return

            # Monitor each product with rate limiting
            for product_url in product_links:
                await monitor_price(product_url)
                await asyncio.sleep(RATE_LIMIT["delay_between_requests"])

    except Exception as e:
        logger.error(f"Error monitoring website {url}: {str(e)}")

@app.post("/monitor")
async def start_monitoring(url: str = Form(...)):
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    
    url = normalize_url(url)
    if not is_valid_url(url):
        raise HTTPException(status_code=400, detail="Invalid URL")
    
    # Start monitoring in background
    asyncio.create_task(monitor_website(url))
    return {"message": "Monitoring started"}

@app.get("/api/products")
async def get_products():
    return monitored_products

if __name__ == "__main__":
    # Create templates directory if it doesn't exist
    os.makedirs("templates", exist_ok=True)
    
    # Create static directory if it doesn't exist
    os.makedirs("static", exist_ok=True)
    
    # Run the server
    uvicorn.run(app, host="127.0.0.1", port=8081)  # Changed port to 8081 