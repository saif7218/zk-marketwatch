from datetime import datetime
from fpdf import FPDF
import os
import json
from typing import Dict, Any

class CompetitiveReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'ZK MarketWatch - Daily Intelligence Report', 0, 1, 'C')
        self.set_font('Arial', '', 10)
        self.cell(0, 10, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_daily_report(analysis: Dict[str, Any]) -> str:
    """
    Generates a PDF report from the competitive analysis results.
    
    Args:
        analysis: Dictionary containing analysis results
        
    Returns:
        Path to the generated PDF report
    """
    pdf = CompetitiveReport()
    pdf.add_page()
    
    # Summary section
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Executive Summary', 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 10, (
        f"Analysis of {analysis['total_products']} products across "
        f"{len(analysis['competitors_analyzed'])} competitors "
        f"({', '.join(analysis['competitors_analyzed'])})."
    ))
    pdf.ln(5)
    
    # Price Analysis
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Price Analysis', 0, 1)
    pdf.set_font('Arial', '', 10)
    
    # Overall price comparison
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Overall Average Prices', 0, 1)
    pdf.set_font('Arial', '', 10)
    for competitor, price in analysis['price_analysis']['overall'].items():
        pdf.cell(0, 10, f"{competitor}: ৳{price:.2f}", 0, 1)
    pdf.ln(5)
    
    # Category-wise analysis
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Category-wise Price Analysis', 0, 1)
    pdf.set_font('Arial', '', 10)
    for category_comp, price in analysis['price_analysis']['by_category'].items():
        category, competitor = category_comp
        pdf.cell(0, 10, f"{category} - {competitor}: ৳{price:.2f}", 0, 1)
    pdf.ln(5)
    
    # Stock Analysis
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Stock Availability', 0, 1)
    pdf.set_font('Arial', '', 10)
    for competitor, stats in analysis['stock_analysis'].items():
        availability = stats['mean'] * 100
        pdf.cell(0, 10, 
                f"{competitor}: {availability:.1f}% products in stock", 
                0, 1)
    pdf.ln(5)
    
    # Add visualizations
    if os.path.exists(analysis['plots']['price_comparison']):
        pdf.add_page()
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Price Comparison Visualization', 0, 1)
        pdf.image(analysis['plots']['price_comparison'], 
                 x=10, 
                 y=pdf.get_y(), 
                 w=190)
    
    if os.path.exists(analysis['plots']['price_distribution']):
        pdf.add_page()
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Price Distribution Analysis', 0, 1)
        pdf.image(analysis['plots']['price_distribution'], 
                 x=10, 
                 y=pdf.get_y(), 
                 w=190)
    
    # Save report
    os.makedirs('reports', exist_ok=True)
    filename = f"reports/daily_report_{datetime.now().strftime('%Y%m%d')}.pdf"
    pdf.output(filename)
    return filename

if __name__ == "__main__":
    try:
        # Load latest analysis
        with open('analysis/latest_analysis.json', 'r') as f:
            analysis = json.load(f)
            
        # Generate report
        report_path = generate_daily_report(analysis)
        print(f"\nReport generated successfully: {report_path}")
    except Exception as e:
        print(f"Error generating report: {str(e)}")
