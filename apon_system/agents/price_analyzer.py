import logging
import pandas as pd
from datetime import datetime
from typing import List, Dict

logger = logging.getLogger('PriceAnalyzer')

def analyze_price_trends(price_data: List[Dict]) -> Dict:
    """Analyze price trends and generate insights."""
    if not price_data:
        return {}
    df = pd.DataFrame(price_data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    analysis = {
        'product_name': price_data[0]['product_name'],
        'analysis_timestamp': datetime.now().isoformat(),
        'total_data_points': len(price_data),
        'price_statistics': {
            'min_price': df['price'].min(),
            'max_price': df['price'].max(),
            'avg_price': df['price'].mean(),
            'median_price': df['price'].median(),
            'std_deviation': df['price'].std()
        },
        'competitor_analysis': {},
        'insights': []
    }
    for competitor in df['competitor'].unique():
        comp_data = df[df['competitor'] == competitor]
        analysis['competitor_analysis'][competitor] = {
            'avg_price': comp_data['price'].mean(),
            'data_points': len(comp_data),
            'availability_rate': (comp_data['availability'] == 'In Stock').mean() * 100 if 'availability' in comp_data.columns else 0
        }
    if analysis['competitor_analysis']:
        min_competitor = min(analysis['competitor_analysis'].items(), key=lambda x: x[1]['avg_price'])
        max_competitor = max(analysis['competitor_analysis'].items(), key=lambda x: x[1]['avg_price'])
        analysis['insights'] = [
            f"Lowest average price: {min_competitor[0]} at {min_competitor[1]['avg_price']:.2f} BDT",
            f"Highest average price: {max_competitor[0]} at {max_competitor[1]['avg_price']:.2f} BDT",
            f"Price range: {analysis['price_statistics']['max_price'] - analysis['price_statistics']['min_price']:.2f} BDT",
            f"Market average: {analysis['price_statistics']['avg_price']:.2f} BDT"
        ]
    logger.info(f"Completed price analysis for {analysis['product_name']}")
    return analysis
