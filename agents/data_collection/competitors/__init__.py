"""
Competitor-specific scraper implementations.
Each competitor module must implement the scrape_category(category: str) -> List[Dict] interface.
"""

from . import shwapno, agora, daraz

# Map competitor names to their scraper modules
COMPETITOR_MAP = {
    'shwapno': shwapno,
    'agora': agora,
    'daraz': daraz
}
