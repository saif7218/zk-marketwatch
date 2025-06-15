import re
import httpx
from bs4 import BeautifulSoup
from typing import List, Tuple
from urllib.parse import urljoin

PRODUCT_URL_REGEX = re.compile(r"^https://www\.shwapno\.com/product/[^/]+$")
CATEGORY_URL_REGEX = re.compile(r"^https://www\.shwapno\.com/(?:[a-zA-Z0-9\-]+)$")

async def crawl_for_products(seed_url: str, max_products: int = 20, max_depth: int = 2) -> List[str]:
    """
    Crawl the given seed URL and return only real Shwapno product URLs.
    Follows category links up to max_depth.
    """
    product_urls = set()
    visited = set()
    queue = [(seed_url, 0)]  # (url, depth)

    async with httpx.AsyncClient(timeout=10) as client:
        while queue and len(product_urls) < max_products:
            current_url, depth = queue.pop(0)
            if current_url in visited:
                continue
                
            visited.add(current_url)
            try:
                response = await client.get(current_url)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                for a in soup.find_all("a", href=True):
                    href = urljoin(current_url, a['href'])
                    if href not in visited:
                        if PRODUCT_URL_REGEX.match(href):
                            product_urls.add(href)
                            if len(product_urls) >= max_products:
                                break
                        elif CATEGORY_URL_REGEX.match(href) and depth < max_depth:
                            queue.append((href, depth + 1))
            except Exception as e:
                logger.error(f"Error crawling {current_url}: {e}")

    return sorted(product_urls)

def extract_price(html: str) -> float:
    soup = BeautifulSoup(html, "html.parser")
    price_tag = (
        soup.find("span", class_="product-price")
        or soup.find("div", class_="product-price")
        or soup.find("span", class_="price")
        or soup.find("div", class_="price")
    )
    if not price_tag:
        meta = soup.find("meta", {"property": "product:price:amount"})
        if meta and meta.get("content"):
            try:
                return float(meta["content"])
            except ValueError:
                return 0.0
        return 0.0
    text = price_tag.get_text(strip=True)
    cleaned = re.sub(r"[^0-9.]", "", text)
    try:
        return float(cleaned)
    except ValueError:
        return 0.0

async def fetch_price_and_stock(url: str) -> Tuple[float, str]:
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            html = resp.text
        except Exception:
            from playwright.async_api import async_playwright
            async with async_playwright() as pw:
                browser = await pw.chromium.launch()
                page = await browser.new_page()
                await page.goto(url, timeout=15000)
                html = await page.content()
                await browser.close()
    price = extract_price(html)
    stock = "In Stock" if price > 0 else "Out of Stock"
    return price, stock
