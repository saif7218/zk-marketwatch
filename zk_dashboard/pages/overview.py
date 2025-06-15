"""
Overview page for ZK MarketWatch dashboard.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
from datetime import datetime, timedelta

def show():
    st.title("📊 Market Overview")
    
    # Load latest insights
    insights = load_insights()
    
    if not insights:
        st.warning("No data available. Please run data collection first.")
        return
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Products Tracked",
            insights['summary']['total_products_tracked'],
            delta=None
        )
    
    with col2:
        st.metric(
            "Competitors Monitored",
            insights['summary']['competitors_monitored'],
            delta=None
        )
    
    with col3:
        st.metric(
            "Categories Tracked",
            insights['summary']['categories_tracked'],
            delta=None
        )
    
    with col4:
        st.metric(
            "Anomalies Detected",
            insights['summary']['anomalies_detected'],
            delta=None
        )
    
    # Market pulse
    st.subheader("Market Pulse")
    
    if insights.get('trends'):
        # Create trend visualization
        trend_data = []
        for competitor, categories in insights['trends'].items():
            for category, stats in categories.items():
                trend_data.append({
                    'Competitor': competitor,
                    'Category': category,
                    'Average Price': stats['avg_price'],
                    'Min Price': stats['min_price'],
                    'Max Price': stats['max_price'],
                    'Product Count': stats['product_count']
                })
        
        df = pd.DataFrame(trend_data)
        
        # Price comparison chart
        fig = px.bar(df, x='Category', y='Average Price', color='Competitor',
                    title="Average Prices by Category and Competitor")
        st.plotly_chart(fig, use_container_width=True)
        
        # Product count distribution
        fig2 = px.pie(df, values='Product Count', names='Competitor',
                     title="Product Distribution by Competitor")
        st.plotly_chart(fig2, use_container_width=True)
    
    # Recent activity
    st.subheader("Recent Activity")
    
    if insights.get('anomalies'):
        st.write("### 🚨 Recent Anomalies")
        for anomaly in insights['anomalies'][-5:]:  # Show last 5
            with st.expander(f"{anomaly['competitor']} - {anomaly['product_name']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Price:** ৳{anomaly['price']:.2f}")
                    st.write(f"**Category:** {anomaly['category']}")
                with col2:
                    st.write(f"**Average Price:** ৳{anomaly['avg_category_price']:.2f}")
                    st.write(f"**Deviation:** ৳{anomaly['deviation']:.2f}")
    
    # Recommendations preview
    if insights.get('recommendations'):
        st.subheader("🎯 Top Recommendations")
        for rec in insights['recommendations'][:3]:  # Show top 3
            priority_color = {"urgent": "🔴", "high": "🟡", "medium": "🟢"}.get(rec['priority'], "⚪")
            st.info(f"{priority_color} **{rec['type'].replace('_', ' ').title()}**: {rec['message']}")

def load_insights():
    """Load latest insights from file"""
    try:
        with open('data/processed/latest_insights.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None
