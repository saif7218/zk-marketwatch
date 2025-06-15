import logging
from datetime import datetime
from apon_system.agents.keyword_enricher import enrich_keywords
from apon_system.agents.database_manager import init_database, save_price_data, save_analysis
from apon_system.agents.data_validator import validate_and_clean_data
from apon_system.agents.api_query import query_price_apis

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('IntegrationTest')

def run_integration_test():
    logger.info("Starting integration test...")
    
    # 1. Initialize database
    logger.info("Initializing database...")
    init_database()
    
    # 2. Test with sample product data
    test_product = {
        'name': 'Premium Basmati Rice',
        'category': 'rice',
        'keywords': ['rice', 'premium'],
        'target_price': 120.00
    }
    
    # 3. Test keyword enrichment
    logger.info("Testing keyword enrichment...")
    enriched_product = enrich_keywords(test_product)
    logger.info(f"Enriched keywords: {enriched_product.get('enriched_keywords')}")
    
    # 4. Test API queries
    logger.info("Testing API queries...")
    api_data = query_price_apis(test_product)
    logger.info(f"Retrieved {len(api_data)} price points")
    
    # 5. Validate and clean the data
    logger.info("Testing data validation...")
    cleaned_data = validate_and_clean_data(api_data)
    logger.info(f"Validated {len(cleaned_data)} records")
    
    # 6. Save price data to database
    logger.info("Testing database operations...")
    save_success = save_price_data(cleaned_data)
    
    # 7. Save analysis
    sample_analysis = {
        'product_name': test_product['name'],
        'analysis_data': {
            'price_points': len(cleaned_data),
            'avg_price': sum(d['price'] for d in cleaned_data) / len(cleaned_data),
            'confidence': sum(d['confidence'] for d in cleaned_data) / len(cleaned_data)
        },
        'analysis_timestamp': datetime.now().isoformat()
    }
    analysis_saved = save_analysis(sample_analysis)
    
    # Final status
    logger.info("Integration test completed!")
    logger.info(f"Database operations successful: {save_success and analysis_saved}")

if __name__ == "__main__":
    run_integration_test()