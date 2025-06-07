import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import os
from typing import Dict, List, Any
import json
from datetime import datetime

def analyze_competition(raw_data: pd.DataFrame) -> Dict[str, Any]:
    """
    Performs competitive analysis on scraped product data.
    
    Args:
        raw_data: DataFrame containing product data
        
    Returns:
        Dictionary containing various analysis results
    """
    if raw_data.empty:
        return {
            "error": "No data available for analysis",
            "timestamp": datetime.now().isoformat()
        }
    
    analysis = {
        "timestamp": datetime.now().isoformat(),
        "total_products": len(raw_data),
        "competitors_analyzed": raw_data['competitor'].unique().tolist()
    }
    
    # Price analysis by category and competitor
    price_comparison = raw_data.groupby(['category', 'competitor'])['price'].agg([
        'mean', 'min', 'max', 'count'
    ]).round(2).unstack()
    
    # Stock availability analysis
    stock_analysis = raw_data.groupby('competitor')['in_stock'].agg([
        'mean', 'count'
    ]).round(2)
    
    # Price clustering
    price_data = raw_data[['price']].copy()
    kmeans = KMeans(n_clusters=3, n_init='auto')
    raw_data['price_cluster'] = kmeans.fit_predict(price_data)
    
    # Save visualizations
    os.makedirs('analysis', exist_ok=True)
    
    # Price comparison plot
    plt.figure(figsize=(12, 6))
    price_comparison['mean'].plot(kind='bar', title='Average Price Comparison by Category')
    plt.tight_layout()
    plt.savefig('analysis/price_comparison.png')
    plt.close()
    
    # Price distribution plot
    plt.figure(figsize=(10, 6))
    for competitor in raw_data['competitor'].unique():
        competitor_data = raw_data[raw_data['competitor'] == competitor]
        plt.hist(competitor_data['price'], alpha=0.5, label=competitor, bins=30)
    plt.title('Price Distribution by Competitor')
    plt.xlabel('Price')
    plt.ylabel('Count')
    plt.legend()
    plt.tight_layout()
    plt.savefig('analysis/price_distribution.png')
    plt.close()
    
    # Prepare analysis results
    analysis.update({
        "price_analysis": {
            "by_category": price_comparison['mean'].to_dict(),
            "overall": raw_data.groupby('competitor')['price'].mean().to_dict()
        },
        "stock_analysis": stock_analysis.to_dict(),
        "price_clusters": {
            "centers": kmeans.cluster_centers_.tolist(),
            "distribution": raw_data.groupby(['competitor', 'price_cluster']).size().to_dict()
        },
        "plots": {
            "price_comparison": "analysis/price_comparison.png",
            "price_distribution": "analysis/price_distribution.png"
        }
    })
    
    # Save analysis to JSON
    os.makedirs('analysis', exist_ok=True)
    with open('analysis/latest_analysis.json', 'w') as f:
        json.dump(analysis, f, indent=2)
    
    return analysis

if __name__ == "__main__":
    # Example usage
    try:
        df = pd.read_csv('data/latest_collection.csv')
        results = analyze_competition(df)
        print("\nAnalysis complete. Results saved to analysis/latest_analysis.json")
        print("\nKey findings:")
        print(f"- Analyzed {results['total_products']} products")
        print(f"- Competitors: {', '.join(results['competitors_analyzed'])}")
        print("- Generated visualizations in analysis/")
    except Exception as e:
        print(f"Error running analysis: {str(e)}")
