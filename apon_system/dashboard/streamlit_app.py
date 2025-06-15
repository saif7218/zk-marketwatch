import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sqlite3

def load_latest_analyses():
    db_path = os.path.join('apon_intelligence.db')
    if not os.path.exists(db_path):
        return pd.DataFrame()
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT * FROM analyses", conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()

def load_latest_report():
    path = os.path.join('data', 'latest_report.md')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    return "No report found. Run the pipeline first."

def fetch_price_data():
    """Fetch price data from the database."""
    conn = sqlite3.connect('apon_intelligence.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT product_name, competitor, price, availability, timestamp
        FROM price_data
        ORDER BY timestamp DESC
        LIMIT 50
    ''')
    data = cursor.fetchall()
    conn.close()
    return data

st.set_page_config(page_title="Apon Family Mart Dashboard", layout="wide")
st.title("Apon Family Mart Intelligence Dashboard")

# Add custom CSS for greenish-red theme
st.markdown(
    """
    <style>
    body {
        background-color: #f0f5f0;
        color: #2c3e50;
    }
    .stButton>button {
        background-color: #27ae60;
        color: white;
        border-radius: 5px;
    }
    .stButton>button:hover {
        background-color: #c0392b;
    }
    </style>
    """,
    unsafe_allow_html=True
)

menu = ["Home Dashboard", "Product Management", "Price Monitoring", "Competitor Analysis", "Reports", "Settings"]
choice = st.sidebar.selectbox("Navigation", menu)

if choice == "Home Dashboard":
    st.header("📊 Overview")
    df = load_latest_analyses()
    if not df.empty:
        st.write("Products analyzed:", df['product_name'].nunique())
        st.write("Latest analyses:")
        st.dataframe(df.tail(10))
    else:
        st.info("No analysis data found. Run the pipeline first.")

elif choice == "Product Management":
    st.header("🛒 Product Management")
    st.write("Upload or edit your product list CSV.")
    uploaded = st.file_uploader("Upload products CSV", type=["csv"])
    if uploaded:
        df = pd.read_csv(uploaded)
        st.dataframe(df)
        save_path = os.path.join('data', 'uploaded_products.csv')
        df.to_csv(save_path, index=False)
        st.success(f"File saved to {save_path}")

elif choice == "Price Monitoring":
    st.header("💰 Price Monitoring")
    data = fetch_price_data()
    if data:
        st.write("Latest Price Data:")
        st.table(data)
    else:
        st.info("No price data available. Run the scraper to fetch data.")

elif choice == "Competitor Analysis":
    st.header("🏪 Competitor Analysis")
    df = load_latest_analyses()
    if not df.empty:
        st.write("Competitor analysis is in development. Displaying raw analysis:")
        st.dataframe(df)
    else:
        st.info("No competitor data found. Run the pipeline first.")

elif choice == "Reports":
    st.header("📑 Reports")
    report = load_latest_report()
    st.markdown(report)

elif choice == "Settings":
    st.header("⚙️ Settings")
    st.write("Edit config in config/settings.py and restart the app to apply changes.")
