import streamlit as st
import os
import sys
import pandas as pd
import json
from datetime import datetime

# Add parent directory to path to import from agents
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="ZK MarketWatch",
    page_icon="🛒",
    layout="wide"
)

def load_latest_data():
    """Load the latest collected data and analysis results."""
    try:
        # Try to load from the sample data file
        data = pd.read_csv('sample_data.csv')
        
        # Create a simple analysis dictionary
        analysis = {
            'total_products': len(data),
            'average_price': data['price'].mean(),
            'total_stock': data['stock'].sum(),
            'last_updated': data['last_updated'].iloc[0]
        }
        return data, analysis
    except Exception as e:
        st.warning(f"Using sample data. Error loading original data: {str(e)}")
        
        # Return sample data if the file doesn't exist
        sample_data = pd.DataFrame({
            'product': ['Product A', 'Product B', 'Product C'],
            'price': [99.99, 149.99, 199.99],
            'stock': [10, 5, 8],
            'competitor_price': [95.99, 145.99, 195.99],
            'last_updated': ['2025-06-07'] * 3
        })
        
        analysis = {
            'total_products': 3,
            'average_price': sample_data['price'].mean(),
            'total_stock': sample_data['stock'].sum(),
            'last_updated': '2025-06-07'
        }
        return sample_data, analysis

def show_overview():
    """Display the overview dashboard."""
    st.title("ZK MarketWatch Overview")
    
    data, analysis = load_latest_data()
    if data is None or analysis is None:
        return
    
    # Key metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Products", len(data))
    with col2:
        st.metric("Competitors", len(data['competitor'].unique()))
    with col3:
        st.metric("Categories", len(data['category'].unique()))
    
    # Price comparison
    st.subheader("Price Comparison")
    if os.path.exists('../analysis/price_comparison.png'):
        st.image('../analysis/price_comparison.png')
    
    # Stock availability
    st.subheader("Stock Availability")
    stock_data = pd.DataFrame([
        {"Competitor": comp, "Availability": stats['mean'] * 100}
        for comp, stats in analysis['stock_analysis'].items()
    ])
    st.bar_chart(stock_data.set_index('Competitor'))
    
    # Recent data
    st.subheader("Latest Product Updates")
    st.dataframe(data.sort_values('timestamp', ascending=False).head(10))

def show_pricing():
    """Display the pricing analysis dashboard."""
    st.title("Pricing Analysis")
    
    data, analysis = load_latest_data()
    if data is None or analysis is None:
        return
    
    # Price distribution
    st.subheader("Price Distribution")
    if os.path.exists('../analysis/price_distribution.png'):
        st.image('../analysis/price_distribution.png')
    
    # Price clusters
    st.subheader("Price Clusters")
    clusters = pd.DataFrame(analysis['price_clusters']['centers'], 
                          columns=['Price Range'])
    st.write("Price Cluster Centers:")
    st.dataframe(clusters)
    
    # Category analysis
    st.subheader("Category-wise Analysis")
    categories = data['category'].unique()
    selected_category = st.selectbox("Select Category", categories)
    
    cat_data = data[data['category'] == selected_category]
    st.write(f"Average prices in {selected_category}:")
    st.bar_chart(cat_data.groupby('competitor')['price'].mean())

def show_alerts():
    """Display the alert system dashboard."""
    st.title("Alert System")
    
    data, analysis = load_latest_data()
    if data is None or analysis is None:
        return
    
    # Alert settings
    st.subheader("Alert Configuration")
    col1, col2 = st.columns(2)
    with col1:
        price_threshold = st.slider("Price Change Threshold (%)", 0, 50, 10)
    with col2:
        stock_alert = st.checkbox("Alert on Stock Changes", value=True)
    
    # Sample alerts (replace with actual alert logic)
    st.subheader("Recent Alerts")
    alerts = [
        {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "type": "Price Change",
            "product": "Fresh Milk",
            "competitor": "Shwapno",
            "details": "Price dropped by 15%"
        },
        {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "type": "Stock Alert",
            "product": "Mineral Water",
            "competitor": "Agora",
            "details": "Out of stock"
        }
    ]
    
    for alert in alerts:
        with st.expander(f"{alert['type']}: {alert['product']} ({alert['competitor']})"):
            st.write(f"Time: {alert['timestamp']}")
            st.write(f"Details: {alert['details']}")
            if st.button("Investigate", key=f"investigate_{alert['product']}"):
                st.info("Investigation feature coming soon!")

# Sidebar navigation
st.sidebar.title("ZK MarketWatch")
st.sidebar.caption("AI-Powered Competitive Intelligence")

# Add logo if available
logo_path = "assets/zk_logo.png"
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, width=200)

page = st.sidebar.radio("Navigation", ["Overview", "Pricing Analysis", "Alert System"])

# Page routing
if page == "Overview":
    show_overview()
elif page == "Pricing Analysis":
    show_pricing()
elif page == "Alert System":
    show_alerts()

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M"))
