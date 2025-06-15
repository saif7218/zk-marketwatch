import logging
from agents import product_loader, keyword_enricher, web_scraper, api_query, data_validator, price_analyzer, report_generator, slack_notifier, database_manager
from config import settings
import os

def run_pipeline(products_csv: str):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('Orchestrator')
    database_manager.init_database()
    logger.info(f"Running full pipeline for {products_csv}")
    # Step 1: Load products
    products = product_loader.load_products_from_csv(products_csv)
    if not products:
        logger.error("No products loaded - aborting pipeline")
        return
    all_analyses = []
    # Step 2-6: Process each product
    for product in products:
        logger.info(f"Processing product: {product['name']}")
        # Enrich keywords
        enriched_product = keyword_enricher.enrich_keywords(product)
        # Gather price data
        scraped_prices = web_scraper.scrape_competitor_prices(enriched_product)
        api_prices = api_query.query_price_apis(enriched_product)
        # Combine and validate data
        all_price_data = scraped_prices + api_prices
        validated_data = data_validator.validate_and_clean_data(all_price_data)
        if validated_data:
            # Analyze prices
            analysis = price_analyzer.analyze_price_trends(validated_data)
            all_analyses.append(analysis)
            # Save to database
            database_manager.save_price_data(validated_data)
            database_manager.save_analysis(analysis)
    # Step 7: Generate report
    report = report_generator.generate_markdown_report(all_analyses)
    report_path = os.path.join(settings.DATA_DIR, 'latest_report.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    logger.info(f"Report saved to {report_path}")
    # Step 8: Send notifications
    slack_notifier.send_alert(f"Apon Family Mart market report generated. Products analyzed: {len(all_analyses)}.")
    logger.info("Pipeline complete.")
