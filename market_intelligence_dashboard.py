import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

def generate_sample_data(num_rows=100):
    """Generate sample product data"""
    np.random.seed(42)
    
    categories = ['Electronics', 'Clothing', 'Home', 'Beauty', 'Sports']
    competitors = ['Amazon', 'Walmart', 'Target', 'Best Buy', 'eBay']
    
    data = {
        'product': [f'Product {i+1}' for i in range(num_rows)],
        'category': np.random.choice(categories, num_rows),
        'competitor': np.random.choice(competitors, num_rows),
        'price': np.random.uniform(10, 1000, num_rows).round(2),
        'stock': np.random.choice([True, False], num_rows, p=[0.7, 0.3]),
        'last_updated': pd.Timestamp.now() - pd.to_timedelta(np.random.randint(1, 30, num_rows), unit='d')
    }
    
    return pd.DataFrame(data)

def main():
    st.set_page_config(
        page_title="Market Intelligence Dashboard",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("Market Intelligence Dashboard")
    
    # Data loading
    uploaded_file = st.sidebar.file_uploader("Upload your CSV file", type=["csv"])
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    else:
        df = generate_sample_data()
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Category filter
    categories = ['All'] + sorted(df['category'].unique().tolist())
    selected_category = st.sidebar.selectbox('Category', categories, index=0)
    
    # Competitor filter
    competitors = ['All'] + sorted(df['competitor'].unique().tolist())
    selected_competitor = st.sidebar.selectbox('Competitor', competitors, index=0)
    
    # Price range filter
    min_price = float(df['price'].min())
    max_price = float(df['price'].max())
    price_range = st.sidebar.slider(
        'Price Range',
        min_value=min_price,
        max_value=max_price,
        value=(min_price, max_price)
    )
    
    # Apply filters
    filtered = df.copy()
    if selected_category != 'All':
        filtered = filtered[filtered['category'] == selected_category]
    if selected_competitor != 'All':
        filtered = filtered[filtered['competitor'] == selected_competitor]
    filtered = filtered[
        (filtered['price'] >= price_range[0]) & 
        (filtered['price'] <= price_range[1])
    ]
    
    # Display metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Products", len(filtered))
    with col2:
        st.metric("Average Price", f"${filtered['price'].mean():.2f}")
    
    # Show data table
    st.subheader("Data Table")
    st.dataframe(filtered.reset_index(drop=True), use_container_width=True)
    
    # Chart
    st.subheader("Price Distribution")
    fig = px.histogram(filtered, x="price", nbins=20, title="Price Histogram")
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
