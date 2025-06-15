"""
Knowledge base query page for ZK MarketWatch dashboard.
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
import plotly.express as px

def show():
    st.title("🔍 Knowledge Base Query")
    
    # Load insights for historical context
    insights = load_insights()
    
    # Query interface
    st.subheader("Market Intelligence Query")
    
    query_type = st.selectbox(
        "Select Query Type",
        [
            "Price Trends",
            "Competitor Analysis",
            "Category Performance",
            "Historical Anomalies",
            "Custom Query"
        ]
    )
    
    if query_type == "Price Trends":
        show_price_trends_query(insights)
    elif query_type == "Competitor Analysis":
        show_competitor_analysis_query(insights)
    elif query_type == "Category Performance":
        show_category_performance_query(insights)
    elif query_type == "Historical Anomalies":
        show_historical_anomalies_query(insights)
    else:
        show_custom_query(insights)

def show_price_trends_query(insights):
    """Interface for querying price trends"""
    if not insights or not insights.get('trends'):
        st.warning("No trend data available.")
        return
    
    # Query parameters
    col1, col2 = st.columns(2)
    
    with col1:
        competitors = list(insights['trends'].keys())
        selected_competitor = st.selectbox(
            "Select Competitor",
            competitors
        )
    
    with col2:
        if selected_competitor:
            categories = list(insights['trends'][selected_competitor].keys())
            selected_category = st.selectbox(
                "Select Category",
                categories
            )
    
    if selected_competitor and selected_category:
        stats = insights['trends'][selected_competitor][selected_category]
        
        # Display trend analysis
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Average Price",
                f"৳{stats['avg_price']:.2f}",
                delta=None
            )
        
        with col2:
            if 'trend_direction' in stats:
                st.metric(
                    "Price Trend",
                    stats['trend_direction'].title(),
                    delta=f"{stats.get('trend_magnitude', 0):.2f}"
                )
        
        with col3:
            st.metric(
                "Products Tracked",
                stats['product_count']
            )
        
        # Show price distribution if available
        if 'price_std' in stats:
            price_range = {
                'min': stats['min_price'],
                'avg': stats['avg_price'],
                'max': stats['max_price'],
                'std': stats['price_std']
            }
            
            fig = px.box(
                x=['Price'],
                y=[price_range['min'], price_range['avg'], price_range['max']],
                title=f"Price Distribution - {selected_category}"
            )
            st.plotly_chart(fig, use_container_width=True)

def show_competitor_analysis_query(insights):
    """Interface for querying competitor analysis"""
    if not insights or not insights.get('trends'):
        st.warning("No competitor data available.")
        return
    
    # Competitor selection
    competitors = list(insights['trends'].keys())
    selected_competitors = st.multiselect(
        "Select Competitors to Compare",
        competitors,
        default=competitors[:2] if len(competitors) >= 2 else competitors
    )
    
    if len(selected_competitors) > 0:
        # Prepare comparison data
        comparison_data = []
        for competitor in selected_competitors:
            comp_data = insights['trends'][competitor]
            for category, stats in comp_data.items():
                comparison_data.append({
                    'Competitor': competitor,
                    'Category': category,
                    'Average Price': stats['avg_price'],
                    'Product Count': stats['product_count'],
                    'Price Trend': stats.get('trend_direction', 'stable')
                })
        
        df = pd.DataFrame(comparison_data)
        
        # Visualize comparison
        st.subheader("Competitor Comparison")
        
        # Price comparison
        fig = px.bar(
            df,
            x='Category',
            y='Average Price',
            color='Competitor',
            barmode='group',
            title="Price Comparison by Category"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Market share
        fig = px.pie(
            df,
            values='Product Count',
            names='Competitor',
            title="Product Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed metrics
        st.subheader("Detailed Metrics")
        st.dataframe(df)

def show_category_performance_query(insights):
    """Interface for querying category performance"""
    if not insights or not insights.get('trends'):
        st.warning("No category data available.")
        return
    
    # Get unique categories
    categories = set()
    for competitor in insights['trends'].values():
        categories.update(competitor.keys())
    
    selected_category = st.selectbox(
        "Select Category",
        sorted(list(categories))
    )
    
    if selected_category:
        # Collect category data across competitors
        category_data = []
        for competitor, comp_data in insights['trends'].items():
            if selected_category in comp_data:
                stats = comp_data[selected_category]
                category_data.append({
                    'Competitor': competitor,
                    'Average Price': stats['avg_price'],
                    'Product Count': stats['product_count'],
                    'Price Trend': stats.get('trend_direction', 'stable'),
                    'Price Volatility': stats.get('price_std', 0)
                })
        
        df = pd.DataFrame(category_data)
        
        # Category overview
        st.subheader(f"{selected_category} Overview")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Average Category Price",
                f"৳{df['Average Price'].mean():.2f}"
            )
        
        with col2:
            st.metric(
                "Total Products",
                df['Product Count'].sum()
            )
        
        # Price positioning
        fig = px.scatter(
            df,
            x='Average Price',
            y='Product Count',
            size='Price Volatility',
            color='Competitor',
            title="Price Positioning Matrix"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed competitor comparison
        st.dataframe(df)

def show_historical_anomalies_query(insights):
    """Interface for querying historical anomalies"""
    if not insights or not insights.get('anomalies'):
        st.warning("No anomaly data available.")
        return
    
    # Filter controls
    col1, col2 = st.columns(2)
    
    with col1:
        competitors = list({a['competitor'] for a in insights['anomalies']})
        selected_competitors = st.multiselect(
            "Select Competitors",
            competitors,
            default=competitors
        )
    
    with col2:
        categories = list({a['category'] for a in insights['anomalies']})
        selected_categories = st.multiselect(
            "Select Categories",
            categories,
            default=categories
        )
    
    # Filter anomalies
    filtered_anomalies = [
        a for a in insights['anomalies']
        if a['competitor'] in selected_competitors
        and a['category'] in selected_categories
    ]
    
    if filtered_anomalies:
        # Convert to DataFrame for analysis
        df = pd.DataFrame(filtered_anomalies)
        df['detected_at'] = pd.to_datetime(df['detected_at'])
        
        # Anomaly timeline
        st.subheader("Anomaly Timeline")
        
        fig = px.scatter(
            df,
            x='detected_at',
            y='price',
            color='competitor',
            size='deviation',
            hover_data=['product_name', 'category'],
            title="Price Anomalies Over Time"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Anomaly details
        st.subheader("Anomaly Details")
        st.dataframe(
            df[[
                'product_name', 'competitor', 'category',
                'price', 'avg_category_price', 'deviation'
            ]]
        )

def show_custom_query(insights):
    """Interface for custom queries"""
    st.write("Build a custom market intelligence query:")
    
    # Query builder
    metrics = st.multiselect(
        "Select Metrics",
        [
            "Average Price",
            "Price Trend",
            "Product Count",
            "Price Volatility",
            "Market Share",
            "Anomaly Count"
        ]
    )
    
    dimensions = st.multiselect(
        "Group By",
        [
            "Competitor",
            "Category",
            "Time Period"
        ]
    )
    
    if metrics and dimensions:
        st.info("Custom query builder is a placeholder. Implementation would depend on specific business requirements.")

def load_insights():
    """Load latest insights from file"""
    try:
        with open('data/processed/latest_insights.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None
