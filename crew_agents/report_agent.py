from crewai import Agent, Tool
from langchain.tools import BaseTool
from pdfkit import from_string
import chart.js as Chart
import pandas as pd
from datetime import datetime, timedelta
import json
from typing import Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

class PDFReportTool(BaseTool):
    name = "pdf_report"
    description = "Generates PDF reports with price analysis"

    def _run(self, analysis_data: str) -> str:
        """Generate PDF report"""
        data = json.loads(analysis_data)
        
        # Create HTML template
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Price Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .header {{ text-align: center; padding: 20px; }}
                .section {{ margin: 20px 0; }}
                .chart {{ width: 100%; height: 400px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Price Analysis Report</h1>
                <p>Date: {datetime.now().strftime('%Y-%m-%d')}</p>
            </div>

            <div class="section">
                <h2>Price Trends</h2>
                <div class="chart" id="priceChart"></div>
            </div>

            <div class="section">
                <h2>Competitor Movement</h2>
                <table>
                    <tr>
                        <th>Competitor</th>
                        <th>Price Change</th>
                        <th>Movement Score</th>
                    </tr>
                    {self._generate_competitor_table(data)}
                </table>
            </div>

            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <script>
                const ctx = document.getElementById('priceChart').getContext('2d');
                new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        labels: {json.dumps(data['trend']['ds'])},
                        datasets: [{
                            label: 'Price Trend',
                            data: {json.dumps(data['trend']['yhat'])},
                            borderColor: 'rgb(75, 192, 192)',
                            tension: 0.1
                        }]
                    }}
                }});
            </script>
        </body>
        </html>
        """
        
        # Generate PDF
        pdf = from_string(html, False)
        
        # Save to file
        filename = f"price_report_{datetime.now().strftime('%Y%m%d')}.pdf"
        with open(os.path.join(os.getenv("REPORT_DIR", "reports"), filename), 'wb') as f:
            f.write(pdf)
        
        return json.dumps({"status": "success", "filename": filename})

    def _generate_competitor_table(self, data: Dict[str, Any]) -> str:
        """Generate HTML table for competitor movement"""
        rows = []
        for competitor, movement in data["competitors"].items():
            rows.append(f"""
                <tr>
                    <td>{competitor}</td>
                    <td>{movement['change']}%</td>
                    <td>{movement['score']}</td>
                </tr>
            """)
        return "\n".join(rows)

    async def _arun(self, analysis_data: str) -> str:
        return self._run(analysis_data)

class ReportAgent(Agent):
    def __init__(self):
        super().__init__(
            role="Report Generator",
            goal="Create daily price analysis reports",
            tools=[PDFReportTool()],
            verbose=True
        )

    def generate_report(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate daily price analysis report"""
        # Add competitor movement analysis
        competitors = analysis_data.get("competitors", {})
        movement_analysis = self._analyze_competitor_movement(competitors)
        
        # Update data with movement analysis
        analysis_data["competitor_movement"] = movement_analysis
        
        # Generate PDF report
        result = self.execute(json.dumps(analysis_data), tool_name="pdf_report")
        
        return json.loads(result)

    def _analyze_competitor_movement(self, competitors: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze competitor price movements"""
        analysis = {}
        
        for competitor, data in competitors.items():
            # Calculate movement score based on price changes
            score = abs(data.get("change", 0)) * 100  # Simplified scoring
            
            analysis[competitor] = {
                "change": data.get("change", 0),
                "score": round(score, 2)
            }
        
        return analysis

if __name__ == "__main__":
    # Example usage
    agent = ReportAgent()
    result = agent.generate_report({
        "trend": {
            "ds": ["2025-06-01", "2025-06-02"],
            "yhat": [100, 105]
        },
        "competitors": {
            "priyoshop": {"change": 5},
            "chaldal": {"change": 3},
            "daraz": {"change": -2}
        }
    })
    print(result)
