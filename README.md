# Apon AI - Grocery Price Monitor

AI-Powered Grocery Price Monitoring System

## Overview

Apon AI is an open-source grocery price monitoring system that helps you track and analyze grocery prices across multiple online retailers. The system uses AI-powered web scraping to collect price data, perform analysis, and provide insights through an interactive dashboard.

## Features

- **Automated Price Scraping**: Scrapes grocery prices from multiple online retailers
- **AI-Powered Analysis**: Uses LangChain and LLMs for intelligent price analysis
- **Real-time Monitoring**: Tracks price changes and trends over time
- **Interactive Dashboard**: Next.js based dashboard for visualizing price data
- **Multi-language Support**: Built with internationalization (i18n) support
- **Free & Open Source**: No paid APIs required

## Project Structure

```
apon-ai/
├── apps/
│   └── web/                  # Next.js frontend application
│       ├── src/
│       │   ├── app/         # Next.js app router
│       │   ├── components/   # React components
│       │   └── lib/         # Utility functions
│       └── public/          # Static assets
├── scrapers/
│   ├── grocery_scraper.py  # Web scraper for grocery prices
│   ├── langchain_agent.py   # AI-powered analysis agent
│   └── api.py              # Flask API for the backend
├── data/                   # Scraped data storage
└── run.py                  # Main entry point
```

## Prerequisites

- Python 3.9+
- Node.js 18+
- npm or yarn
- Ollama (for local LLM) or HuggingFace API key

## Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/apon-ai.git
   cd apon-ai
   ```

2. Set up Python environment and install dependencies:
   ```bash
   # Create and activate virtual environment
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Unix/MacOS

   # Install Python dependencies
   pip install -r scrapers/requirements.txt
   ```

3. Install Node.js dependencies:
   ```bash
   cd apps/web
   npm install
   cd ../..
   ```

4. Install Ollama (for local LLM):
   ```bash
   # Download and install from https://ollama.ai/
   # Then run:
   ollama pull mistral
   ```

5. Run the application:
   ```bash
   python run.py
   ```

   This will:
   - Start the Flask backend API on port 5000
   - Start the Next.js frontend on port 3000
   - Open your default browser to http://localhost:3000

## Usage

1. **Scrape Prices**:
   - Enter a grocery store URL in the dashboard
   - The system will scrape prices for grocery items
   - View results in the dashboard

2. **Price Analysis**:
   - The system uses AI to analyze price trends
   - View price history and comparisons
   - Get alerts for significant price changes

3. **API Endpoints**:
   - `POST /api/scrape`: Scrape a website for prices
   - `GET /api/prices`: Get latest scraped prices
   - `POST /api/query`: Query the AI agent

## Configuration

Create a `.env` file in the project root with the following variables:

```bash
# For HuggingFace (alternative to Ollama)
# HUGGINGFACEHUB_API_TOKEN=your_token_here

# Backend configuration
FLASK_ENV=development
FLASK_APP=scrapers/api.py

# Frontend configuration
NEXT_PUBLIC_API_URL=http://localhost:5000
```

## Development

### Frontend Development

```bash
cd apps/web
npm run dev
```

### Backend Development

```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Unix/MacOS

# Run Flask development server
python scrapers/api.py
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with Next.js, React, Flask, and LangChain
- Uses Ollama and HuggingFace for AI capabilities
- Inspired by the need for affordable price monitoring solutions

This project is proprietary and confidential.

## Contact

For support or inquiries, please contact the development team.
