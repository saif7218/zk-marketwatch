# FastAPI Price Monitor

A production-ready FastAPI service for monitoring product prices with DNS resilience, connection pooling, and automatic fallback to browser rendering.

## Features

- 🚀 FastAPI-based REST API
- 🔄 Dual fetching strategy (aiohttp + Playwright fallback)
- 🛡️ DNS resilience with Google/Cloudflare nameservers
- 🔌 Connection pooling and keep-alive
- ⚡ Performance metrics and Prometheus integration
- 🛑 Circuit breaker pattern
- 📊 Structured logging
- 🐳 Docker support
- ✅ Comprehensive test suite

## Setup

1. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

3. Configure environment variables (optional):
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

## Running

### Development
```bash
uvicorn main:app --reload --workers 2 --timeout-keep-alive 30
```

### Production
```bash
uvicorn main:app --host 0.0.0.0 --port 80 --workers 2
```

### Docker
```bash
docker build -t price-monitor .
docker run -p 80:80 price-monitor
```

## API Endpoints

### GET /price
Fetch product price from URL.

Query Parameters:
- `url`: Product page URL (required)

Response:
```json
{
    "url": "https://example.com/product",
    "price": "£51.77",
    "method": "aiohttp",
    "elapsed_seconds": 0.123
}
```

### GET /health
Check service health and circuit breaker status.

Response:
```json
{
    "status": "ok",
    "circuit": "closed",
    "failures": 0,
    "uptime_seconds": 3600
}
```

### GET /metrics
Prometheus metrics endpoint.

### POST /circuit/reset
Reset circuit breaker after failures.

## Configuration

Environment variables in `.env`:

- `DNS_SERVERS`: Comma-separated DNS server IPs
- `HTTP_TIMEOUT_TOTAL`: Total request timeout in seconds
- `HTTP_TIMEOUT_CONNECT`: Connection timeout in seconds
- `POOL_LIMIT`: Connection pool size
- `MAX_RETRIES`: Maximum retry attempts
- `RETRY_BACKOFF_BASE`: Retry backoff multiplier
- `SEMAPHORE_LIMIT`: Maximum concurrent requests
- `CIRCUIT_BREAKER_THRESHOLD`: Failures before circuit opens
- `PLAY_FALLBACK`: Enable/disable Playwright fallback

## Testing

Run tests:
```bash
pytest tests/
```

## Monitoring

The service exposes Prometheus metrics at `/metrics`:

- `price_requests_total`: Request count by method and status
- `price_request_latency_seconds`: Request latency histogram
- `circuit_breaker_state`: Circuit breaker state changes

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License 