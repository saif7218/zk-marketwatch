import logging
from typing import Dict

logger = logging.getLogger('KeywordEnricher')

def enrich_keywords(product: Dict) -> Dict:
    """Enrich product keywords with synonyms and variations."""
    base_keywords = product['keywords']
    enriched_keywords = set(base_keywords)
    # Add name words
    enriched_keywords.update(product['name'].lower().split())
    # Add category-based keywords
    category_mappings = {
        'rice': ['basmati', 'aromatic', 'grain', 'chaal'],
        'milk': ['dairy', 'fresh', 'liquid', 'dudh'],
        'oil': ['cooking', 'edible', 'tel'],
        'soap': ['bathing', 'cleaning', 'sabun'],
        'tea': ['beverage', 'drink', 'cha']
    }
    for category, additional in category_mappings.items():
        if category in product['category'].lower():
            enriched_keywords.update(additional)
    product['enriched_keywords'] = list(enriched_keywords)
    logger.info(f"Enriched keywords for {product['name']} ({len(enriched_keywords)})")
    return product
