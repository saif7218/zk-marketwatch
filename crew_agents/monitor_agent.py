from crewai import Agent, Tool
from langchain.tools import BaseTool
from langchain.utilities import GoogleSheetsAPIWrapper
from langchain.memory import RedisVectorStoreMemory
from langchain.embeddings import HuggingFaceEmbeddings
from typing import Dict, Any
import redis
import json
import os
from dotenv import load_dotenv

load_dotenv()

class PuppeteerTool(BaseTool):
    name = "puppeteer_scraping"
    description = "Scrapes competitor websites for price data"

    def __init__(self, browser=None):
        super().__init__()
        self.browser = browser

    def _run(self, query: str) -> str:
        """Scrape competitor websites for price data"""
        competitors = {
            "priyoshop": {
                "url": "https://www.priyoshop.com",
                "selectors": {
                    "price": "[data-price]",
                    "name": "[data-product-name]"
                }
            },
            "chaldal": {
                "url": "https://www.chaldal.com",
                "selectors": {
                    "price": ".product-price",
                    "name": ".product-name"
                }
            },
            "daraz": {
                "url": "https://www.daraz.com.bd",
                "selectors": {
                    "price": ".c-price",
                    "name": ".c-title"
                }
            }
        }

        results = {}
        for name, config in competitors.items():
            try:
                page = self.browser.new_page()
                page.goto(config["url"])
                
                # Wait for dynamic content
                page.wait_for_load_state("networkidle")
                
                # Extract prices
                prices = page.evaluate("() => {
                    const elements = document.querySelectorAll(arguments[0]);
                    return Array.from(elements).map(el => el.textContent.trim());
                }", config["selectors"]["price"])
                
                results[name] = {
                    "prices": prices,
                    "timestamp": str(datetime.now())
                }
                
                page.close()
            except Exception as e:
                results[name] = {"error": str(e)}

        return json.dumps(results)

    async def _arun(self, query: str) -> str:
        return self._run(query)

class CheerioParserTool(BaseTool):
    name = "cheerio_parser"
    description = "Parses HTML content using Cheerio"

    def _run(self, query: str) -> str:
        """Parse HTML content using Cheerio"""
        # Implementation for Cheerio parsing
        return "Parsed data"

    async def _arun(self, query: str) -> str:
        return self._run(query)

class MonitorAgent(Agent):
    def __init__(self, product_id: str):
        super().__init__(
            role="Competitor Intelligence Specialist",
            goal="Identify price changes on key competitor sites",
            tools=[PuppeteerTool(), CheerioParserTool()],
            memory=RedisVectorStoreMemory(
                redis_url=os.getenv("REDIS_URL"),
                embeddings=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            )
        )
        self.product_id = product_id

    def execute(self, task: str) -> Dict[str, Any]:
        """Execute monitoring task"""
        result = super().execute(task)
        
        # Store in Redis with TTL
        redis_client = redis.Redis.from_url(os.getenv("REDIS_URL"))
        key = f"monitor:{self.product_id}:{datetime.now().strftime('%Y-%m-%d')}"
        redis_client.setex(key, 604800, json.dumps(result))  # 7-day TTL
        
        return result

if __name__ == "__main__":
    # Example usage
    agent = MonitorAgent("product_123")
    result = agent.execute("Monitor competitors for product 123")
    print(result)
