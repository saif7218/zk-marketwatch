# Price Monitor Service

A microservice for scraping and extracting grocery item prices from competitor websites using FastAPI and LangChain with local LLM (Ollama).

## Prerequisites

- Python 3.9+
- Docker (optional, for containerized deployment)
- Ollama with a model installed (e.g., `ollama pull llama3`)

## Setup

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Ensure Ollama is running**:
   ```bash
   ollama serve
   ```
   In another terminal, pull the model:
   ```bash
   ollama pull llama3
   ```

## Running the Service

### Development Mode

```bash
uvicorn main:app --reload
```

The service will be available at `http://localhost:8000`

### Using Docker

1. Build the Docker image:
   ```bash
   docker build -t price-monitor .
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 price-monitor
   ```

## API Endpoints

- `POST /price-monitor/scrape` - Scrape a website for grocery items and prices
  - Request body: `{"url": "https://example.com/groceries"}`
  - Response: `{"items": [{"item": "Product Name", "price": 9.99}]}`

- `GET /health` - Health check endpoint
  - Response: `{"status": "healthy"}`

## Environment Variables

- `OLLAMA_MODEL`: The name of the Ollama model to use (default: "llama3")
- `LOG_LEVEL`: Logging level (default: "info")

## Development

### Testing

```bash
# Install test dependencies
pip install pytest httpx

# Run tests
pytest
```

### Linting

```bash
pip install black isort flake8
black .
isort .
flake8
```

## License

MIT
