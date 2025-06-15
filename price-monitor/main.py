import os
import time
import asyncio
from typing import Tuple, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseSettings, AnyHttpUrl
import aiohttp
from aiohttp.resolver import AsyncResolver
from playwright.async_api import async_playwright, BrowserContext
from bs4 import BeautifulSoup
from loguru import logger
from tenacity import (
    AsyncRetrying, stop_after_attempt, wait_exponential, retry_if_exception_type
)
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# ----------------------------
#   CONFIGURATION
# ----------------------------
class Settings(BaseSettings):
    dns_servers: Tuple[str, ...] = ("8.8.8.8", "1.1.1.1")
    user_agent: str = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/125.0.0.0 Safari/537.36")
    http_timeout_total: int = 10
    http_timeout_connect: int = 2
    pool_limit: int = 100
    max_retries: int = 3
    retry_backoff_base: float = 0.5
    semaphore_limit: int = 20
    play_fallback: bool = True
    circuit_breaker_threshold: int = 5

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

# ----------------------------
#   METRICS
# ----------------------------
REQUEST_COUNTER = Counter(
    "price_requests_total", "Total number of price requests", ["method", "status"]
)
REQUEST_LATENCY = Histogram(
    "price_request_latency_seconds", "Latency of price requests", ["method"]
)
CIRCUIT_BREAKER_STATE = Counter(
    "circuit_breaker_state", "Circuit breaker state changes", ["state"]
)

# ----------------------------
#   APP & MIDDLEWARE
# ----------------------------
app = FastAPI(title="🔍 Price Monitor API", version="1.0.0")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"→ {request.method} {request.url}")
    start = time.monotonic()
    try:
        response = await call_next(request)
        return response
    finally:
        elapsed = (time.monotonic() - start) * 1000
        logger.info(f"← {request.method} {request.url} completed in {elapsed:.1f}ms")

# ----------------------------
#   GLOBAL RESOURCES
# ----------------------------
session: Optional[aiohttp.ClientSession] = None
play_context: Optional[BrowserContext] = None
_semaphore = asyncio.Semaphore(settings.semaphore_limit)
_circuit_open = False
_circuit_failures = 0
_startup_time = datetime.now()

@app.on_event("startup")
async def startup():
    global session, play_context
    logger.info("Initializing application...")
    
    # Configure DNS resolver with reliable nameservers
    resolver = AsyncResolver(nameservers=list(settings.dns_servers))
    connector = aiohttp.TCPConnector(
        limit=settings.pool_limit,
        resolver=resolver,
        force_close=False,
        ssl=False
    )
    timeout = aiohttp.ClientTimeout(
        total=settings.http_timeout_total,
        connect=settings.http_timeout_connect
    )
    
    session = aiohttp.ClientSession(
        connector=connector,
        timeout=timeout,
        headers={"User-Agent": settings.user_agent}
    )

    if settings.play_fallback:
        logger.info("Initializing Playwright...")
        pw = await async_playwright().start()
        browser = await pw.chromium.launch(headless=True)
        play_context = await browser.new_context()
    
    logger.info("Application startup complete!")

@app.on_event("shutdown")
async def shutdown():
    logger.info("Shutting down application...")
    if session:
        await session.close()
    if play_context:
        await play_context.close()
    logger.info("Application shutdown complete!")

# ----------------------------
#   HELPERS
# ----------------------------
async def _extract_price(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    tag = soup.find("p", class_="price_color")
    if not tag:
        raise ValueError("Price element not found")
    return tag.get_text().strip()

async def _fetch_with_aiohttp(url: str) -> Tuple[str, float]:
    start = time.monotonic()
    async with session.get(url) as resp:
        resp.raise_for_status()
        text = await resp.text()
    price = await _extract_price(text)
    elapsed = time.monotonic() - start
    return price, elapsed

async def _fetch_with_playwright(url: str) -> Tuple[str, float]:
    start = time.monotonic()
    page = await play_context.new_page()
    try:
        await page.goto(url, timeout=settings.http_timeout_total * 1000)
        content = await page.content()
    finally:
        await page.close()
    price = await _extract_price(content)
    elapsed = time.monotonic() - start
    return price, elapsed

# Retry strategy for aiohttp path
retryer = AsyncRetrying(
    reraise=True,
    stop=stop_after_attempt(settings.max_retries),
    wait=wait_exponential(multiplier=settings.retry_backoff_base),
    retry=retry_if_exception_type(aiohttp.ClientError)
)

# ----------------------------
#   ENDPOINTS
# ----------------------------
@app.get("/price")
async def get_price(url: AnyHttpUrl):
    global _circuit_open, _circuit_failures

    if _circuit_open:
        raise HTTPException(503, "Circuit is open; too many failures")

    async with _semaphore:
        # Try aiohttp with retries
        try:
            async for attempt in retryer:
                with attempt:
                    price, elapsed = await _fetch_with_aiohttp(str(url))
            method = "aiohttp"
            _circuit_failures = 0  # Reset on success
        except Exception as http_err:
            REQUEST_COUNTER.labels(method="aiohttp", status="failure").inc()
            logger.warning(f"aiohttp path failed: {http_err}")
            
            # Fallback to playwright
            try:
                price, elapsed = await _fetch_with_playwright(str(url))
                method = "playwright"
                _circuit_failures = 0  # Reset on success
            except Exception as play_err:
                REQUEST_COUNTER.labels(method="playwright", status="failure").inc()
                logger.error(f"playwright path failed: {play_err}")
                
                # Update circuit breaker
                _circuit_failures += 1
                if _circuit_failures >= settings.circuit_breaker_threshold:
                    _circuit_open = True
                    CIRCUIT_BREAKER_STATE.labels(state="open").inc()
                    logger.error("Circuit breaker opened due to repeated failures")
                
                raise HTTPException(
                    500, f"Both fetch methods failed: aiohttp({http_err}), playwright({play_err})"
                )
        
        # Record metrics
        REQUEST_COUNTER.labels(method=method, status="success").inc()
        REQUEST_LATENCY.labels(method=method).observe(elapsed)
        
        return {
            "url": str(url),
            "price": price,
            "method": method,
            "elapsed_seconds": round(elapsed, 3)
        }

@app.get("/metrics")
async def metrics():
    data = generate_latest()
    return JSONResponse(data, media_type=CONTENT_TYPE_LATEST)

@app.get("/health")
def health():
    uptime = datetime.now() - _startup_time
    return {
        "status": "ok",
        "circuit": "open" if _circuit_open else "closed",
        "failures": _circuit_failures,
        "uptime_seconds": uptime.total_seconds()
    }

@app.post("/circuit/reset")
def reset_circuit():
    global _circuit_open, _circuit_failures
    _circuit_open = False
    _circuit_failures = 0
    CIRCUIT_BREAKER_STATE.labels(state="closed").inc()
    return {"status": "Circuit breaker reset"} 