# Apon AI Rival Price Monitor Agent

## Overview
This agent monitors prices and stock status across multiple e-commerce sites, storing snapshots and triggering alerts via your FastAPI backend. It is modular, robust, and ready for production.

## Directory Structure
- `agent.py` — Main loop, orchestrates scraping and change detection
- `scraper.py` — Multi-site Playwright-based scraper
- `tracker.py` — Compares snapshots and detects changes
- `alert.py` — Sends alerts to backend (WebSocket/email/SMS handled by backend)
- `utils.py` — Logging, config loading, user-agent generation
- `config.json` — Configuration for sites and backend
- `requirements.txt` — Python dependencies

## Setup
1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   playwright install
   ```
2. Configure `config.json` as needed (add your backend URL, sites, products).
3. Ensure your FastAPI backend is running.
4. Run the agent:
   ```sh
   python agent.py
   ```

## Notes
- To use proxies, set `USE_PROXIES` and `PROXY_LIST` in `config.json`.
- The agent is ready to be run as a service or scheduled task.
- For production, implement real CSS selectors in `scraper.py` for each site.

---
