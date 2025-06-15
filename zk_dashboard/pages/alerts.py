"""
Alerts page for ZK MarketWatch dashboard.
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta

def show():
    st.title("🚨 Market Alerts")
    
    # Load latest insights
    insights = load_insights()
    
    if not insights:
        st.warning("No data available. Please run data collection first.")
        return
    
    # Alert filters
    st.sidebar.subheader("Filter Alerts")
    
    # Get unique competitors and categories
    competitors = list({a['competitor'] for a in insights.get('anomalies', [])})
    categories = list({a['category'] for a in insights.get('anomalies', [])})
    
    selected_competitors = st.sidebar.multiselect(
        "Competitors",
        competitors,
        default=competitors
    )
    
    selected_categories = st.sidebar.multiselect(
        "Categories",
        categories,
        default=categories
    )
    
    priority_filter = st.sidebar.multiselect(
        "Priority",
        ["urgent", "high", "medium", "low"],
        default=["urgent", "high"]
    )
    
    # Filter alerts
    filtered_anomalies = [
        a for a in insights.get('anomalies', [])
        if a['competitor'] in selected_competitors
        and a['category'] in selected_categories
    ]
    
    filtered_recommendations = [
        r for r in insights.get('recommendations', [])
        if r['priority'] in priority_filter
        and r.get('competitor') in selected_competitors
        and r.get('category') in selected_categories
    ]
    
    # Display alerts
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Price Anomalies")
        if filtered_anomalies:
            for anomaly in filtered_anomalies:
                show_anomaly_card(anomaly)
        else:
            st.info("No price anomalies match the current filters.")
    
    with col2:
        st.subheader("Recommendations")
        if filtered_recommendations:
            for rec in filtered_recommendations:
                show_recommendation_card(rec)
        else:
            st.info("No recommendations match the current filters.")
    
    # Alert statistics
    st.subheader("Alert Statistics")
    
    stats_col1, stats_col2, stats_col3 = st.columns(3)
    
    with stats_col1:
        st.metric(
            "Total Anomalies",
            len(filtered_anomalies),
            delta=f"{len(filtered_anomalies) - len(insights.get('anomalies', []))}"
        )
    
    with stats_col2:
        urgent_count = sum(1 for r in filtered_recommendations if r['priority'] == 'urgent')
        st.metric("Urgent Recommendations", urgent_count)
    
    with stats_col3:
        categories_affected = len({a['category'] for a in filtered_anomalies})
        st.metric("Categories Affected", categories_affected)
    
    # Historical trend
    if insights.get('trends'):
        st.subheader("Alert Trend")
        alert_trend = calculate_alert_trend(insights)
        
        st.line_chart(alert_trend)

def show_anomaly_card(anomaly):
    """Display an anomaly alert card"""
    with st.expander(f"🔍 {anomaly['product_name']} ({anomaly['competitor']})"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Price:** ৳{anomaly['price']:.2f}")
            st.write(f"**Category:** {anomaly['category']}")
            st.write(f"**Competitor:** {anomaly['competitor']}")
        
        with col2:
            st.write(f"**Category Average:** ৳{anomaly['avg_category_price']:.2f}")
            st.write(f"**Deviation:** ৳{anomaly['deviation']:.2f}")
            st.write(f"**Detected:** {format_datetime(anomaly['detected_at'])}")
        
        # Calculate percentage difference
        pct_diff = (anomaly['price'] - anomaly['avg_category_price']) / anomaly['avg_category_price'] * 100
        
        # Show visual indicator
        if abs(pct_diff) > 20:
            st.error(f"⚠️ Price is {abs(pct_diff):.1f}% {'above' if pct_diff > 0 else 'below'} category average")
        elif abs(pct_diff) > 10:
            st.warning(f"⚠️ Price is {abs(pct_diff):.1f}% {'above' if pct_diff > 0 else 'below'} category average")

def show_recommendation_card(rec):
    """Display a recommendation card"""
    priority_colors = {
        "urgent": "🔴",
        "high": "🟡",
        "medium": "🟢",
        "low": "⚪"
    }
    
    with st.expander(f"{priority_colors.get(rec['priority'], '⚪')} {rec['type'].replace('_', ' ').title()}"):
        st.write(rec['message'])
        
        if 'competitor' in rec:
            st.write(f"**Competitor:** {rec['competitor']}")
        if 'category' in rec:
            st.write(f"**Category:** {rec['category']}")
        if 'product' in rec:
            st.write(f"**Product:** {rec['product']}")

def calculate_alert_trend(insights):
    """Calculate historical alert trend"""
    if not insights.get('anomalies'):
        return pd.DataFrame()
    
    # Convert anomalies to DataFrame
    df = pd.DataFrame(insights['anomalies'])
    df['detected_at'] = pd.to_datetime(df['detected_at'])
    
    # Group by date and count anomalies
    daily_counts = df.groupby(df['detected_at'].dt.date).size().reset_index()
    daily_counts.columns = ['date', 'count']
    
    return daily_counts.set_index('date')

def format_datetime(dt_str):
    """Format datetime string for display"""
    try:
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return dt_str

def load_insights():
    """Load latest insights from file"""
    try:
        with open('data/processed/latest_insights.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None
