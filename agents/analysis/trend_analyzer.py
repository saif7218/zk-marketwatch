"""
Trend analyzer for market data analysis.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import IsolationForest
from prophet import Prophet
import json
import glob
import logging
import os

logger = logging.getLogger(__name__)

class TrendAnalyzer:
    def __init__(self):
        self.data = None
        self.trends = {}
        self.anomalies = []
    
    def load_data(self, data_path="data/raw/*.json"):
        """Load all collected data"""
        all_data = []
        
        for file_path in glob.glob(data_path):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        all_data.extend(data)
                    else:
                        all_data.append(data)
            except Exception as e:
                logger.warning(f"Error loading {file_path}: {e}")
        
        if all_data:
            self.data = pd.DataFrame(all_data)
            self.data['collected_at'] = pd.to_datetime(self.data['collected_at'])
            logger.info(f"Loaded {len(self.data)} data points")
        else:
            logger.warning("No data loaded")
            self.data = pd.DataFrame()
    
    def analyze_price_trends(self):
        """Analyze price trends by competitor and category"""
        if self.data.empty:
            return {}
        
        trends = {}
        
        for competitor in self.data['competitor'].unique():
            trends[competitor] = {}
            comp_data = self.data[self.data['competitor'] == competitor]
            
            for category in comp_data['category'].unique():
                cat_data = comp_data[comp_data['category'] == category]
                
                # Calculate basic statistics
                price_stats = {
                    'avg_price': cat_data['price'].mean(),
                    'min_price': cat_data['price'].min(),
                    'max_price': cat_data['price'].max(),
                    'price_std': cat_data['price'].std(),
                    'product_count': len(cat_data),
                    'last_updated': cat_data['collected_at'].max().isoformat()
                }
                
                # Time series analysis if enough data points
                if len(cat_data) > 5:
                    price_stats.update(self._time_series_analysis(cat_data))
                
                trends[competitor][category] = price_stats
        
        self.trends = trends
        return trends
    
    def _time_series_analysis(self, data):
        """Perform time series analysis on price data"""
        try:
            # Prepare data for Prophet
            ts_data = data.groupby('collected_at')['price'].mean().reset_index()
            ts_data.columns = ['ds', 'y']
            
            if len(ts_data) < 3:
                return {'trend': 'insufficient_data'}
            
            # Fit Prophet model
            model = Prophet(daily_seasonality=False, yearly_seasonality=False)
            model.fit(ts_data)
            
            # Make future predictions
            future = model.make_future_dataframe(periods=7, freq='H')
            forecast = model.predict(future)
            
            # Calculate trend
            recent_trend = forecast['trend'].iloc[-7:].mean() - forecast['trend'].iloc[-14:-7].mean()
            
            return {
                'trend_direction': 'increasing' if recent_trend > 0 else 'decreasing',
                'trend_magnitude': abs(recent_trend),
                'predicted_price_7d': forecast['yhat'].iloc[-1]
            }
            
        except Exception as e:
            logger.warning(f"Time series analysis failed: {e}")
            return {'trend': 'analysis_failed'}
    
    def detect_anomalies(self):
        """Detect price anomalies using Isolation Forest"""
        if self.data.empty:
            return []
        
        anomalies = []
        
        for competitor in self.data['competitor'].unique():
            comp_data = self.data[self.data['competitor'] == competitor]
            
            for category in comp_data['category'].unique():
                cat_data = comp_data[comp_data['category'] == category]
                
                if len(cat_data) < 10:  # Need minimum data for anomaly detection
                    continue
                
                # Prepare features for anomaly detection
                features = cat_data[['price']].values
                
                # Detect anomalies
                iso_forest = IsolationForest(contamination=0.1, random_state=42)
                anomaly_labels = iso_forest.fit_predict(features)
                
                # Get anomalous products
                anomaly_indices = np.where(anomaly_labels == -1)[0]
                
                for idx in anomaly_indices:
                    anomaly_data = cat_data.iloc[idx]
                    anomalies.append({
                        'competitor': competitor,
                        'category': category,
                        'product_name': anomaly_data['name'],
                        'price': anomaly_data['price'],
                        'avg_category_price': cat_data['price'].mean(),
                        'deviation': abs(anomaly_data['price'] - cat_data['price'].mean()),
                        'detected_at': datetime.now().isoformat()
                    })
        
        self.anomalies = anomalies
        logger.info(f"Detected {len(anomalies)} anomalies")
        return anomalies
    
    def generate_insights(self):
        """Generate actionable insights from analysis"""
        insights = {
            'summary': {
                'total_products_tracked': len(self.data) if not self.data.empty else 0,
                'competitors_monitored': len(self.data['competitor'].unique()) if not self.data.empty else 0,
                'categories_tracked': len(self.data['category'].unique()) if not self.data.empty else 0,
                'anomalies_detected': len(self.anomalies),
                'analysis_timestamp': datetime.now().isoformat()
            },
            'trends': self.trends,
            'anomalies': self.anomalies,
            'recommendations': self._generate_recommendations()
        }
        
        return insights
    
    def _generate_recommendations(self):
        """Generate strategic recommendations"""
        recommendations = []
        
        # Price-based recommendations
        if self.trends:
            for competitor, categories in self.trends.items():
                for category, stats in categories.items():
                    if stats.get('trend_direction') == 'decreasing':
                        recommendations.append({
                            'type': 'pricing_opportunity',
                            'priority': 'high',
                            'message': f"{competitor} is lowering prices in {category}. Consider competitive response.",
                            'category': category,
                            'competitor': competitor
                        })
        
        # Anomaly-based recommendations
        for anomaly in self.anomalies:
            if anomaly['price'] < anomaly['avg_category_price'] * 0.8:
                recommendations.append({
                    'type': 'price_alert',
                    'priority': 'urgent',
                    'message': f"Significant price drop detected: {anomaly['product_name']} by {anomaly['competitor']}",
                    'product': anomaly['product_name'],
                    'competitor': anomaly['competitor']
                })
        
        return recommendations

def run_analysis():
    """Run complete trend analysis"""
    analyzer = TrendAnalyzer()
    analyzer.load_data()
    analyzer.analyze_price_trends()
    analyzer.detect_anomalies()
    insights = analyzer.generate_insights()
    
    # Save insights
    os.makedirs('data/processed', exist_ok=True)
    with open('data/processed/latest_insights.json', 'w') as f:
        json.dump(insights, f, indent=2)
    
    return insights

if __name__ == "__main__":
    insights = run_analysis()
    print(f"Analysis complete. Found {len(insights['anomalies'])} anomalies and {len(insights['recommendations'])} recommendations.")
