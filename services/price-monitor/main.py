from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl, Field
import requests
from bs4 import BeautifulSoup
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_extraction_chain
import re
import json
import time
import logging
import httpx
from typing import List, Dict, Any, Optional, Literal
from enum import Enum
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Available LLM models
class ModelName(str, Enum):
    DEEPSEEK_R1 = "deepseek-r1:latest"  # Using the available model
    QWEN_CODER = "qwen2.5-coder:1.5b"
    DEEPSEEK_CODER = "deepseek-coder:1.3b"

# Initialize FastAPI with CORS
app = FastAPI(title="APON AI Price Monitor", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Schema for product extraction
PRODUCT_SCHEMA = {
    "properties": {
        "name": {"type": "string"},
        "price": {"type": "number"},
        "currency": {"type": "string", "default": "BDT"},
        "category": {"type": "string", "enum": ["egg", "noodle", "grocery", "other"]},
        "unit": {"type": "string", "default": "piece"},
        "in_stock": {"type": "boolean", "default": True}
    },
    "required": ["name", "price"]
}

class OllamaClient:
    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.available_models = []
        self._check_connection()
    
    def _check_connection(self):
        """Check Ollama connection and get available models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models_data = response.json()
                self.available_models = [model['name'] for model in models_data.get('models', [])]
                logger.info(f"Connected to Ollama. Available models: {self.available_models}")
            else:
                logger.warning("Ollama is running but couldn't fetch models")
        except Exception as e:
            logger.warning(f"Could not connect to Ollama: {e}")
    
    def get_model(self, model_name: str = None):
        """Get an instance of the specified model"""
        if not model_name and self.available_models:
            model_name = self.available_models[0]
        
        try:
            return Ollama(model=model_name, temperature=0.2, timeout=60)
        except Exception as e:
            logger.error(f"Failed to initialize model {model_name}: {e}")
            if self.available_models and model_name != self.available_models[0]:
                return self.get_model(self.available_models[0])  # Fallback to first available model
            return None

# Initialize Ollama client
ollama_client = OllamaClient()

# Get the default model
default_model = ModelName.DEEPSEEK_R1 if ollama_client.available_models else None
llm = ollama_client.get_model(ModelName.DEEPSEEK_R1) if default_model else None

# Create extraction chain
def create_extraction_chain(model_name: str = None):
    model = ollama_client.get_model(model_name) if model_name else llm
    if not model:
        return None
    
    prompt = ChatPromptTemplate.from_template("""
    Extract product information from the following website content.
    Focus on grocery items, especially eggs and noodles.
    
    Website content:
    {text}
    
    Extract the following information for each product:
    - name: Product name
    - price: Price as a number
    - currency: Currency code (BDT, USD, etc.)
    - category: Product category (egg, noodle, grocery, other)
    - unit: Unit of measurement (piece, kg, g, L, etc.)
    - in_stock: Whether the product is in stock (true/false)
    
    Return only a valid JSON array of product objects.
    If no products found, return an empty array [].
    """)
    
    return create_extraction_chain(PRODUCT_SCHEMA, model, prompt=prompt)

app = FastAPI()

class ScrapeRequest(BaseModel):
    url: HttpUrl
    use_llm: bool = True
    model_name: Optional[str] = Field(
        default=None,
        description="Name of the Ollama model to use. If not provided, uses the default model."
    )
    timeout: int = Field(
        default=30,
        ge=10,
        le=120,
        description="Timeout in seconds for the scraping operation"
    )

class ProductItem(BaseModel):
    name: str
    price: float
    currency: str = "BDT"
    category: Optional[str] = None
    unit: str = "piece"
    in_stock: bool = True
    source_url: Optional[HttpUrl] = None
    extracted_at: str = Field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))

class ScrapeResponse(BaseModel):
    url: str
    status: Literal["success", "partial", "error"]
    items: List[ProductItem]
    extraction_method: Literal["llm", "regex", "hybrid"]
    processing_time: float
    model_used: Optional[str] = None
    error: Optional[str] = None

def extract_items_with_llm(text_content: str, max_retries: int = 2) -> List[Dict[str, Any]]:
    """Extract items and prices using the LLM."""
    if not chain:
        logger.warning("LLM chain not available, falling back to regex")
        return extract_items_with_regex(text_content)
    
    for attempt in range(max_retries + 1):
        try:
            # Truncate text to avoid context window issues
            truncated_text = text_content[:6000]  # Conservative limit
            
            # Get LLM response
            llm_response = chain.run(text_content=truncated_text)
            
            # Clean up the response
            llm_response = llm_response.strip()
            
            # Try to extract JSON from markdown code blocks if present
            if '```json' in llm_response:
                llm_response = llm_response.split('```json')[1].split('```')[0].strip()
            elif '```' in llm_response:
                llm_response = llm_response.split('```')[1].split('```')[0].strip()
            
            # Parse the JSON response
            try:
                items = json.loads(llm_response)
                if not isinstance(items, list):
                    raise ValueError("Expected a list of items")
                
                # Validate and clean the items
                valid_items = []
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    
                    item_name = item.get('item', '')
                    price = item.get('price', 0)
                    
                    # Skip invalid items
                    if not item_name or not price:
                        continue
                    
                    # Clean price if it's a string
                    if isinstance(price, str):
                        price = clean_price(price)
                    
                    # Skip if price is still invalid
                    if not isinstance(price, (int, float)) or price <= 0:
                        continue
                    
                    valid_items.append({
                        'item': str(item_name)[:200],  # Limit length
                        'price': round(float(price), 2)
                    })
                
                logger.info(f"Extracted {len(valid_items)} items using LLM")
                return valid_items
                
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"Failed to parse LLM response (attempt {attempt + 1}): {e}")
                if attempt == max_retries:
                    logger.warning(f"LLM response was: {llm_response[:500]}...")
                
        except Exception as e:
            logger.error(f"Error in LLM extraction (attempt {attempt + 1}): {str(e)}")
            if attempt == max_retries:
                logger.exception("Max retries reached with LLM extraction")
            
            # Exponential backoff before retry
            if attempt < max_retries:
                wait_time = (2 ** attempt) * 0.5  # 0.5s, 1s, 2s, etc.
                time.sleep(wait_time)
    
    # Fall back to regex if LLM fails
    logger.info("Falling back to regex extraction after LLM failure")
    return extract_items_with_regex(text_content)

def extract_items_with_regex(text: str) -> List[Dict[str, Any]]:
    """Fallback method to extract items using regex patterns."""
    items = []
    
    # Common price patterns (supports $4.99, 4.99$, USD 4.99, etc.)
    price_patterns = [
        r'\$\s*(\d+\.?\d{0,2})',  # $4.99
        r'(\d+\.?\d{0,2})\s*\$',  # 4.99$
        r'(?i)usd\s*(\d+\.?\d{0,2})',  # USD 4.99
        r'(?i)price\s*:\s*\$?(\d+\.?\d{0,2})',  # Price: $4.99
    ]
    
    # Common item patterns (look for text around prices)
    item_patterns = [
        r'([A-Z][^\n$]{5,30}?)\s*\$?(\d+\.?\d{0,2})',  # Item name then price
        r'\$?(\d+\.?\d{0,2})\s*([A-Z][^\n$]{5,30})',  # Price then item name
    ]
    
    # First try to find item-price pairs
    for pattern in item_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            try:
                if len(match.groups()) >= 2:
                    item = match.group(1).strip()
                    price = match.group(2).strip()
                    
                    # Clean up the item name
                    item = re.sub(r'[^\w\s\-()]', ' ', item).strip()
                    item = ' '.join(item.split())  # Remove extra spaces
                    
                    # Clean and convert price
                    price = clean_price(price)
                    
                    if item and price > 0:
                        items.append({
                            'item': item[:100],  # Limit item length
                            'price': price
                        })
            except Exception as e:
                logger.warning(f"Error processing match: {e}")
                continue
    
    # If no items found with patterns, try to find any prices with surrounding text
    if not items:
        price_matches = re.finditer(r'([A-Z][^\n$]{5,30}?)\s*\$?(\d+\.?\d{0,2})', 
                                 text, re.IGNORECASE | re.MULTILINE)
        for match in price_matches:
            try:
                item = match.group(1).strip()
                price = match.group(2).strip()
                price = clean_price(price)
                
                if price > 0:
                    items.append({
                        'item': item[:100],
                        'price': price
                    })
            except Exception as e:
                logger.warning(f"Error in fallback extraction: {e}")
                continue
    
    logger.info(f"Extracted {len(items)} items using regex")
    return items

def clean_price(price_str: str) -> float:
    """Convert price string to float, handling various formats."""
    if not price_str:
        return 0.0
        
    # Remove all non-numeric characters except decimal point and comma
    price_str = re.sub(r'[^\d.,]', '', str(price_str))
    
    # Handle cases with both comma and period
    if ',' in price_str and '.' in price_str:
        # If comma is before period, it's a thousand separator
        if price_str.find(',') < price_str.find('.'):
            price_str = price_str.replace(',', '')
        else:
            # Comma is decimal separator
            price_str = price_str.replace('.', '').replace(',', '.')
    # Handle comma as decimal separator (e.g., 4,99)
    elif ',' in price_str and (len(price_str.split(',')[-1]) == 2 or price_str.count(',') == 1):
        price_str = price_str.replace(',', '.')
    # Handle comma as thousand separator (e.g., 1,000)
    elif ',' in price_str:
        price_str = price_str.replace(',', '')
    
    try:
        return round(float(price_str), 2)
    except (ValueError, TypeError):
        return 0.0

@app.post("/price-monitor/scrape")
async def scrape_website(request: ScrapeRequest) -> ScrapeResponse:
    """Scrape a website and extract product information."""
    start_time = time.time()
    
    try:
        logger.info(f"Scraping URL: {request.url}")
        
        # Set headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        
        # Fetch the webpage with retries
        max_retries = 2
        response = None
        
        for attempt in range(max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=request.timeout) as client:
                    response = await client.get(
                        str(request.url),
                        headers=headers,
                        follow_redirects=True
                    )
                    response.raise_for_status()
                    break  # Success, exit retry loop
                    
            except (httpx.HTTPError, httpx.TimeoutException) as e:
                if attempt == max_retries:
                    error_msg = f"Failed to fetch URL after {max_retries + 1} attempts: {str(e)}"
                    logger.error(error_msg)
                    return ScrapeResponse(
                        url=str(request.url),
                        status="error",
                        items=[],
                        extraction_method="none",
                        processing_time=time.time() - start_time,
                        error=error_msg
                    )
                
                # Exponential backoff before retry
                wait_time = (2 ** attempt) * 1  # 1s, 2s, 4s, etc.
                logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
        
        if not response:
            raise HTTPException(status_code=500, detail="Failed to fetch URL")
        
        # Parse HTML and extract text
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Clean up the HTML
        for element in soup(["script", "style", "nav", "footer", "header", "iframe"]):
            element.decompose()
        
        # Extract text content with context
        text_content = "\n".join(
            element.get_text(strip=True)
            for element in soup.find_all(['p', 'div', 'span', 'h1', 'h2', 'h3', 'li', 'a'])
            if element.get_text(strip=True)
        )
        
        if not text_content.strip():
            text_content = soup.get_text('\n', strip=True)
        
        logger.info(f"Extracted {len(text_content)} characters of text content")
        
        # Initialize response variables
        items = []
        extraction_method = "none"
        model_used = None
        
        # Try LLM extraction if enabled and models are available
        if request.use_llm and llm:
            try:
                extraction_chain = create_extraction_chain(request.model_name)
                if extraction_chain:
                    logger.info("Using LLM for extraction")
                    result = await extraction_chain.ainvoke({"text": text_content[:8000]})  # Limit input size
                    items = result.get("text", [])
                    extraction_method = "llm"
                    model_used = request.model_name or default_model
                    logger.info(f"LLM extracted {len(items)} items")
            except Exception as e:
                logger.error(f"LLM extraction failed: {e}")
        
        # Fall back to regex if LLM extraction failed or wasn't used
        if not items:
            logger.info("Falling back to regex extraction")
            items = extract_items_with_regex(response.text)
            extraction_method = "regex"
        
        # Process and validate items
        processed_items = []
        for item in items:
            try:
                # Convert to ProductItem with validation
                if isinstance(item, dict):
                    # Ensure price is a number
                    if "price" in item and isinstance(item["price"], str):
                        try:
                            item["price"] = float(re.sub(r"[^\d.]", "", item["price"]))
                        except (ValueError, TypeError):
                            continue
                    
                    # Set default values
                    if "in_stock" not in item:
                        item["in_stock"] = True
                    
                    # Create the product item
                    product = ProductItem(
                        name=item.get("name", "Unnamed Product"),
                        price=item.get("price", 0),
                        currency=item.get("currency", "BDT"),
                        category=item.get("category"),
                        unit=item.get("unit", "piece"),
                        in_stock=item.get("in_stock", True),
                        source_url=request.url
                    )
                    processed_items.append(product)
            except Exception as e:
                logger.warning(f"Error processing item: {e}")
        
        # Determine status
        status = "success"
        if not processed_items:
            status = "error"
        elif len(processed_items) < len(items):
            status = "partial"
        
        processing_time = time.time() - start_time
        logger.info(f"Extracted {len(processed_items)} products in {processing_time:.2f} seconds")
        
        return ScrapeResponse(
            url=str(request.url),
            status=status,
            items=processed_items,
            extraction_method=extraction_method,
            processing_time=processing_time,
            model_used=model_used,
            error=None if processed_items else "No valid products found"
        )
        
    except Exception as e:
        logger.exception("Unexpected error in scrape_website")
        return ScrapeResponse(
            url=str(request.url) if 'request' in locals() else "unknown",
            status="error",
            items=[],
            extraction_method="none",
            processing_time=time.time() - start_time,
            error=f"An unexpected error occurred: {str(e)}"
        )

@app.get("/health", response_model=dict)
async def health_check():
    """Health check endpoint"""
    ollama_status = "connected" if ollama_client.available_models else "disconnected"
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "ollama_status": ollama_status,
        "available_models": ollama_client.available_models,
        "default_model": default_model
    }

@app.get("/models", response_model=dict)
async def get_models():
    """Get available Ollama models"""
    return {
        "available_models": ollama_client.available_models,
        "default_model": default_model,
        "status": "connected" if ollama_client.available_models else "disconnected"
    }

@app.post("/price-monitor/scrape", response_model=ScrapeResponse)
async def scrape_endpoint(request: ScrapeRequest):
    """
    Scrape a website and extract product information.
    
    - **url**: The URL of the website to scrape
    - **use_llm**: Whether to use LLM for extraction (default: True)
    - **model_name**: Specific Ollama model to use (optional)
    - **timeout**: Request timeout in seconds (default: 30)
    """
    return await scrape_website(request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
