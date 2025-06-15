import os
import random
from playwright.sync_api import sync_playwright, Page, TimeoutError
from typing import List, Dict, Any, Optional
from .utils import get_logger, generate_user_agent
import time

logger = get_logger(__name__)

class MultiSiteScraper:
    def __init__(self):
        self.proxies = os.getenv("PROXY_LIST", "").split(',')
        self.user_agents = [
            generate_user_agent() for _ in range(20)
        ]
        self.playwright = None

    def _get_page_content(self, page: Page, url: str) -> Optional[str]:
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            return page.content()
        except TimeoutError:
            logger.error(f"Page load timeout for {url}")
            return None
        except Exception as e:
            logger.error(f"Error navigating to {url}: {e}", exc_info=True)
            return None

    def scrape_site(self, site_name: str, site_url: str, products_to_scrape: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        scraped_data = []
        with sync_playwright() as p:
            browser_args = []
            if self.proxies and os.getenv("USE_PROXIES") == "true":
                proxy_server = random.choice(self.proxies).strip()
                logger.debug(f"Using proxy: {proxy_server}")
                browser_args.append(f'--proxy-server={proxy_server}')

            browser = p.chromium.launch(
                headless=True,
                args=browser_args
            )
            context = browser.new_context(
                user_agent=random.choice(self.user_agents),
                viewport={"width": 1280, "height": 1024}
            )
            page = context.new_page()

            for product_info in products_to_scrape:
                product_name_query = product_info["name"]
                product_url = product_info.get("url")

                if product_url:
                    search_url = product_url
                else:
                    if site_name == "shwapno":
                        search_url = f"https://www.shwapno.com/search?search={product_name_query}"
                    elif site_name == "agora":
                        search_url = f"https://www.agorasuperstores.com/search?q={product_name_query}"
                    elif site_name == "chaldal":
                        search_url = f"https://www.chaldal.com/search/{product_name_query}"
                    elif site_name == "daraz":
                        search_url = f"https://www.daraz.com.bd/catalog/?q={product_name_query}"
                    else:
                        logger.warning(f"No specific search URL handler for {site_name}. Skipping product {product_name_query}.")
                        continue

                logger.info(f"Navigating to {search_url} to scrape {product_name_query} from {site_name}")
                content = self._get_page_content(page, search_url)

                if content:
                    extracted_data = self._parse_content(site_name, content, product_name_query)
                    if extracted_data:
                        extracted_data.update({
                            "product_query": product_name_query,
                            "site_name": site_name,
                            "scraped_url": search_url,
                            "timestamp": time.time()
                        })
                        scraped_data.append(extracted_data)
                    else:
                        logger.warning(f"Could not extract data for '{product_name_query}' from {site_name} at {search_url}")
                else:
                    logger.error(f"Failed to get content for '{product_name_query}' from {site_name} at {search_url}")

            browser.close()
        return scraped_data

    def _parse_content(self, site_name: str, html_content: str, product_name_query: str) -> Optional[Dict[str, Any]]:
        # Dummy logic for demonstration. Replace with BeautifulSoup or Playwright selectors for real extraction.
        if site_name == "shwapno":
            logger.info(f"Parsing content for {site_name} (dummy data for now). Product: {product_name_query}")
            return {
                "product_name": product_name_query,
                "price": random.uniform(50, 100),
                "stock_status": "In Stock" if random.random() > 0.1 else "Out of Stock",
                "delivery_time": "Within 24 hours" if random.random() > 0.3 else "1-2 days"
            }
        elif site_name == "agora":
            logger.info(f"Parsing content for {site_name} (dummy data for now). Product: {product_name_query}")
            return {
                "product_name": product_name_query,
                "price": random.uniform(60, 110),
                "stock_status": "Available",
                "delivery_time": "Next day"
            }
        elif site_name == "chaldal":
            logger.info(f"Parsing content for {site_name} (dummy data for now). Product: {product_name_query}")
            return {
                "product_name": product_name_query,
                "price": random.uniform(45, 95),
                "stock_status": "In Stock",
                "delivery_time": "Same day"
            }
        elif site_name == "daraz":
            logger.info(f"Parsing content for {site_name} (dummy data for now). Product: {product_name_query}")
            return {
                "product_name": product_name_query,
                "price": random.uniform(55, 105),
                "stock_status": "Available",
                "delivery_time": "3-5 days"
            }
        logger.warning(f"No parsing logic defined for site: {site_name}")
        return None
