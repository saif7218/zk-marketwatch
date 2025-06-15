from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from scrapers import scrape_shwapno, scrape_meenabazar, scrape_unimart
import logging
from typing import Dict, List
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Mart Price Tracker API",
    description="API for comparing product prices across different marts in Bangladesh",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {
        "name": "Mart Price Tracker API",
        "version": "1.0.0",
        "endpoints": {
            "/compare": "Compare prices across marts",
            "/health": "Health check endpoint"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.get("/compare")
async def compare_prices(product: str = Query(..., description="Product name to search")):
    """
    Compare prices for a product across different marts.
    
    Args:
        product (str): The product name to search for
        
    Returns:
        dict: Price comparison results from all marts
    """
    try:
        # Run scrapers concurrently
        results = await asyncio.gather(
            asyncio.to_thread(scrape_shwapno, product),
            asyncio.to_thread(scrape_meenabazar, product),
            asyncio.to_thread(scrape_unimart, product)
        )
        
        return {
            "product": product,
            "results": {
                "shwapno": results[0],
                "meena_bazar": results[1],
                "unimart": results[2]
            }
        }
    except Exception as e:
        logger.error(f"Error comparing prices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 