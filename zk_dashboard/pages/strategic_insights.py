"""
Strategic insights page for ZK MarketWatch dashboard.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
from datetime import datetime, timedelta

def show():
    st.title("🎯 Strategic Insights")
    
    # Load latest insights
    insights = load_insights()
    
    if not insights:
        st.warning("No data available. Please run data collection first.")
        return
    
    # Market overview
    st.subheader("Market Overview")
    
    if insights.get('trends'):
        # Create market summary
        market_data = []
        for competitor, categories in insights['trends'].items():
            for category, stats in categories.items():
                market_data.append({
                    'Competitor': competitor,
                    'Category': category,
                    'Average Price': stats['avg_price'],
                    'Product Count': stats['product_count'],
                    'Price Trend': stats.get('trend_direction', 'stable'),
                    'Price Volatility': stats.get('price_std', 0)
                })
        
        df = pd.DataFrame(market_data)
        
        # Market share visualization
        fig = px.treemap(
            df,
            path=['Competitor', 'Category'],
            values='Product Count',
            color='Average Price',
            title="Market Composition and Pricing",
            color_continuous_scale='RdYlBu_r'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Price trends heatmap
        pivot_df = df.pivot(
            index='Competitor',
            columns='Category',
            values='Average Price'
        ).fillna(0)
        
        fig = go.Figure(data=go.Heatmap(
            z=pivot_df.values,
            x=pivot_df.columns,
            y=pivot_df.index,
            colorscale='RdYlBu_r'
        ))
        
        fig.update_layout(
            title="Price Positioning Heatmap",
            xaxis_title="Category",
            yaxis_title="Competitor"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Strategic recommendations
    st.subheader("Strategic Recommendations")
    
    if insights.get('recommendations'):
        # Filter and group recommendations
        urgent_recs = []
        high_recs = []
        other_recs = []
        
        for rec in insights['recommendations']:
            if rec['priority'] == 'urgent':
                urgent_recs.append(rec)
            elif rec['priority'] == 'high':
                high_recs.append(rec)
            else:
                other_recs.append(rec)
        
        # Display recommendations by priority
        if urgent_recs:
            st.error("🚨 Urgent Actions Required")
            for rec in urgent_recs:
                with st.expander(f"🔴 {rec['type'].replace('_', ' ').title()}"):
                    show_recommendation_details(rec)
        
        if high_recs:
            st.warning("⚠️ High Priority Recommendations")
            for rec in high_recs:
                with st.expander(f"🟡 {rec['type'].replace('_', ' ').title()}"):
                    show_recommendation_details(rec)
        
        if other_recs:
            st.info("💡 Strategic Opportunities")
            for rec in other_recs:
                with st.expander(f"🟢 {rec['type'].replace('_', ' ').title()}"):
                    show_recommendation_details(rec)
    
    # Competitive analysis
    st.subheader("Competitive Analysis")
    
    if insights.get('trends'):
        # Analyze competitive positioning
        comp_analysis = analyze_competitive_position(insights['trends'])
        
        # Display competitor strengths
        for competitor, analysis in comp_analysis.items():
            with st.expander(f"📊 {competitor}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Strong Categories:**")
                    for cat in analysis['strong_categories']:
                        st.write(f"- {cat}")
                
                with col2:
                    st.write("**Price Position:**")
                    st.write(f"- Average: {analysis['price_position']}")
                    st.write(f"- Trend: {analysis['trend']}")
                
                if analysis.get('opportunities'):
                    st.write("**Opportunities:**")
                    for opp in analysis['opportunities']:
                        st.write(f"- {opp}")

def show_recommendation_details(rec):
    """Display detailed recommendation information"""
    st.write(rec['message'])
    
    details = []
    if 'competitor' in rec:
        details.append(f"**Competitor:** {rec['competitor']}")
    if 'category' in rec:
        details.append(f"**Category:** {rec['category']}")
    if 'product' in rec:
        details.append(f"**Product:** {rec['product']}")
    
    if details:
        st.write(" | ".join(details))

def analyze_competitive_position(trends):
    """Analyze competitive positioning from trends data"""
    analysis = {}
    
    for competitor, categories in trends.items():
        strong_categories = []
        total_price = 0
        price_count = 0
        trend_direction = {'increasing': 0, 'decreasing': 0, 'stable': 0}
        
        for category, stats in categories.items():
            # Check if this is a strong category
            if stats['product_count'] > 10 and stats.get('price_std', float('inf')) < 20:
                strong_categories.append(category)
            
            # Track price positioning
            total_price += stats['avg_price']
            price_count += 1
            
            # Track trend direction
            if 'trend_direction' in stats:
                trend_direction[stats['trend_direction']] += 1
        
        # Determine overall price position
        avg_price = total_price / price_count if price_count > 0 else 0
        price_position = 'premium' if avg_price > 100 else 'mid-range' if avg_price > 50 else 'value'
        
        # Determine overall trend
        trend = max(trend_direction.items(), key=lambda x: x[1])[0]
        
        analysis[competitor] = {
            'strong_categories': strong_categories,
            'price_position': price_position,
            'trend': trend,
            'opportunities': generate_opportunities(categories, price_position, trend)
        }
    
    return analysis

def generate_opportunities(categories, price_position, trend):
    """Generate strategic opportunities based on analysis"""
    opportunities = []
    
    # Price position based opportunities
    if price_position == 'premium' and trend == 'decreasing':
        opportunities.append("Consider maintaining premium positioning through value-added services")
    elif price_position == 'value' and trend == 'increasing':
        opportunities.append("Potential to move upmarket while maintaining value perception")
    
    # Category specific opportunities
    for category, stats in categories.items():
        if stats.get('trend_direction') == 'increasing' and stats.get('price_std', 0) < 10:
            opportunities.append(f"Strong pricing power in {category} - consider premium offerings")
    
    return opportunities

def load_insights():
    """Load latest insights from file"""
    try:
        with open('data/processed/latest_insights.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None
