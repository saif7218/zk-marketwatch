import asyncio
import logging
from fastapi_price_monitor import extract_product_links, monitor_price, normalize_url
import aiohttp
import time
from typing import List, Tuple
from aiohttp import TCPConnector, ClientTimeout
import sys
import socket
import dns.resolver

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure timeouts and connection settings
TIMEOUT = ClientTimeout(total=10)  # Reduced timeout to 10 seconds
CONNECTOR = TCPConnector(
    limit=10,
    ttl_dns_cache=300,
    force_close=True,
    enable_cleanup_closed=True
)

# Increase recursion limit
sys.setrecursionlimit(1000)

async def resolve_dns(hostname: str) -> str:
    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = 2
        resolver.lifetime = 2
        answers = resolver.resolve(hostname, 'A')
        return str(answers[0])
    except Exception as e:
        logger.warning(f"DNS resolution failed for {hostname}: {str(e)}")
        return hostname

async def test_product(url: str, session: aiohttp.ClientSession) -> Tuple[bool, float]:
    start_time = time.time()
    try:
        logger.info(f"Testing: {url}")
        
        # Pre-resolve DNS
        hostname = url.split('//')[1].split('/')[0]
        ip = await resolve_dns(hostname)
        if ip != hostname:
            url = url.replace(hostname, ip)
        
        price = await asyncio.wait_for(monitor_price(url), timeout=10)
        end_time = time.time()
        duration = end_time - start_time
        
        if price:
            logger.info(f"✓ Price: {price} (took {duration:.2f}s)")
            return True, duration
        else:
            logger.warning(f"✗ No price found (took {duration:.2f}s)")
            return False, duration
    except asyncio.TimeoutError:
        end_time = time.time()
        duration = end_time - start_time
        logger.error(f"✗ Timeout after {duration:.2f}s")
        return False, duration
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        logger.error(f"✗ Error: {str(e)} (took {duration:.2f}s)")
        return False, duration

async def quick_test() -> List[Tuple[int, int, float]]:
    test_urls = [
        "https://shop.shwapno.com/product/milk-fresh-1-ltr",
        "https://shop.shwapno.com/product/eggs-farm-12-pcs",
        "https://shop.shwapno.com/product/banana-local-1-kg"
    ]
    
    results = []
    
    # Create a single session for all runs
    async with aiohttp.ClientSession(
        timeout=TIMEOUT,
        connector=CONNECTOR,
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
    ) as session:
        for run in range(5):
            logger.info(f"\n=== Starting Test Run {run + 1}/5 ===")
            
            # Run all tests concurrently with semaphore to limit concurrent requests
            sem = asyncio.Semaphore(3)  # Limit to 3 concurrent requests
            
            async def bounded_test(url):
                async with sem:
                    return await test_product(url, session)
            
            tasks = [bounded_test(url) for url in test_urls]
            run_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            success_count = sum(1 for r in run_results if isinstance(r, tuple) and r[0] is True)
            total_time = sum(r[1] for r in run_results if isinstance(r, tuple))
            avg_time = total_time / len(test_urls)
            
            results.append((run + 1, success_count, avg_time))
            
            logger.info(f"Run {run + 1} Summary:")
            logger.info(f"- Success: {success_count}/{len(test_urls)} products")
            logger.info(f"- Average time: {avg_time:.2f}s")
            
            # Check for slow responses
            slow_responses = [(url, r[1]) for url, r in zip(test_urls, run_results) 
                            if isinstance(r, tuple) and r[1] > 5]  # Reduced threshold to 5s
            if slow_responses:
                logger.warning("Slow responses detected:")
                for url, duration in slow_responses:
                    logger.warning(f"- {url}: {duration:.2f}s")
            
            # Add a small delay between runs to prevent overwhelming the server
            await asyncio.sleep(1)
    
    return results

if __name__ == "__main__":
    logger.info("Starting optimized test...")
    start_total = time.time()
    results = asyncio.run(quick_test())
    end_total = time.time()
    
    # Print final summary
    logger.info("\n=== Final Test Summary ===")
    total_success = sum(r[1] for r in results)
    total_runs = len(results) * 3
    avg_time = sum(r[2] for r in results) / len(results)
    total_duration = end_total - start_total
    
    logger.info(f"Total Success Rate: {total_success}/{total_runs} products")
    logger.info(f"Average Response Time: {avg_time:.2f}s")
    logger.info(f"Total Test Duration: {total_duration:.2f}s")
    
    if avg_time > 5:  # Reduced threshold to 5s
        logger.warning("⚠️ Overall average response time is above 5 seconds!")
    
    logger.info("Test completed!") 