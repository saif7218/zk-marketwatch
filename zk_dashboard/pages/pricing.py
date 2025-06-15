"""
Pricing analysis page for ZK MarketWatch dashboard.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
from datetime import datetime, timedelta

def show():
    st.title("💰 Pricing Analysis")
    
    # Load latest insights
    insights = load_insights()
    
    if not insights:
        st.warning("No data available. Please run data collection first.")
        return
    
    # Competitor selector
    competitors = get_unique_competitors(insights)
    selected_competitor = st.selectbox(
        "Select Competitor",
        competitors,
        index=0 if competitors else None
    )
    
    if not selected_competitor:
        st.warning("No competitor data available.")
        return
    
    # Category analysis for selected competitor
    st.subheader(f"Category Analysis - {selected_competitor}")
    
    if insights.get('trends', {}).get(selected_competitor):
        categories = insights['trends'][selected_competitor]
        
        # Create category comparison
        cat_data = []
        for category, stats in categories.items():
            cat_data.append({
                'Category': category,
                'Average Price': stats['avg_price'],
                'Min Price': stats['min_price'],
                'Max Price': stats['max_price'],
                'Price Std': stats.get('price_std', 0),
                'Product Count': stats['product_count'],
                'Trend': stats.get('trend_direction', 'stable')
            })
        
        df = pd.DataFrame(cat_data)
        
        # Price range chart
        fig = go.Figure()
        
        for idx, row in df.iterrows():
            fig.add_trace(go.Box(
                name=row['Category'],
                y=[row['Min Price'], row['Average Price'], row['Max Price']],
                boxpoints=False,
                marker_color=get_trend_color(row['Trend'])
            ))
        
        fig.update_layout(
            title="Price Ranges by Category",
            yaxis_title="Price (BDT)",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed category metrics
        st.subheader("Category Metrics")
        for category, stats in categories.items():
            with st.expander(f"📊 {category}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Average Price", f"৳{stats['avg_price']:.2f}")
                    st.metric("Product Count", stats['product_count'])
                
                with col2:
                    if stats.get('trend_direction'):
                        trend_icon = "📈" if stats['trend_direction'] == 'increasing' else "📉"
                        st.metric(
                            "Price Trend",
                            stats['trend_direction'].title(),
                            delta=f"{stats.get('trend_magnitude', 0):.2f}"
                        )
                    
                    if stats.get('predicted_price_7d'):
                        st.metric(
                            "7-Day Forecast",
                            f"৳{stats['predicted_price_7d']:.2f}"
                        )
    
    # Anomaly detection
    st.subheader("🚨 Price Anomalies")
    competitor_anomalies = [
        a for a in insights.get('anomalies', [])
        if a['competitor'] == selected_competitor
    ]
    
    if competitor_anomalies:
        anomaly_df = pd.DataFrame(competitor_anomalies)
        
        fig = px.scatter(
            anomaly_df,
            x='price',
            y='avg_category_price',
            color='category',
            title="Price Anomalies vs Category Average",
            labels={
                'price': 'Product Price',
                'avg_category_price': 'Category Average Price'
            }
        )
        
        # Add diagonal line for reference
        fig.add_trace(
            go.Scatter(
                x=[0, anomaly_df['price'].max()],
                y=[0, anomaly_df['price'].max()],
                mode='lines',
                name='Price = Average',
                line=dict(dash='dash', color='gray')
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # List anomalies
        for anomaly in competitor_anomalies:
            with st.expander(f"{anomaly['product_name']} ({anomaly['category']})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Price:** ৳{anomaly['price']:.2f}")
                    st.write(f"**Category Average:** ৳{anomaly['avg_category_price']:.2f}")
                with col2:
                    st.write(f"**Deviation:** ৳{anomaly['deviation']:.2f}")
                    st.write(f"**Detected:** {format_datetime(anomaly['detected_at'])}")
    else:
        st.info("No price anomalies detected for this competitor.")

def get_unique_competitors(insights):
    """Get list of unique competitors from insights"""
    if not insights or 'trends' not in insights:
        return []
    return list(insights['trends'].keys())

def get_trend_color(trend):
    """Get color based on trend direction"""
    return {
        'increasing': 'red',
        'decreasing': 'green',
        'stable': 'gray'
    }.get(trend, 'gray')

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
