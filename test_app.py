import streamlit as st

st.set_page_config(
    page_title="Test App",
    page_icon="✅",
    layout="wide"
)

st.title("🚀 Streamlit Test App")
st.write("If you can see this, Streamlit is working correctly!")

# Add some sample data
import pandas as pd
import numpy as np

# Sample data
data = pd.DataFrame({
    'Product': ['A', 'B', 'C', 'D', 'E'],
    'Price': [10, 20, 15, 25, 30],
    'Stock': [100, 50, 75, 120, 80]
})

# Display the data
st.subheader("Sample Data")
st.dataframe(data)

# Add a simple chart
st.subheader("Price Distribution")
st.bar_chart(data.set_index('Product')['Price'])

st.success("✅ App is running successfully!")
