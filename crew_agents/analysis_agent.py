from crewai import Agent, Tool
from langchain.tools import BaseTool
from langchain.memory import RedisVectorStoreMemory
from langchain.embeddings import HuggingFaceEmbeddings
from prophet import Prophet
import pandas as pd
import json
from typing import Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

class ProphetForecastTool(BaseTool):
    name = "prophet_forecast"
    description = "Generates price trend predictions using Prophet"

    def _run(self, price_history: str) -> str:
        """Generate price forecasts using Prophet"""
        try:
            # Parse price history
            history = pd.read_json(price_history)
            
            # Prepare data for Prophet
            df = pd.DataFrame({
                'ds': history['timestamp'],
                'y': history['price']
            })
            
            # Initialize and fit model
            model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=True
            )
            model.fit(df)
            
            # Create future dates
            future = model.make_future_dataframe(periods=7)  # 7-day forecast
            
            # Make predictions
            forecast = model.predict(future)
            
            # Format results
            results = {
                'trend': forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(7).to_dict('records'),
                'seasonality': {
                    'yearly': model.seasonality_features().to_dict(),
                    'weekly': model.seasonality_matrix().to_dict()
                }
            }
            
            return json.dumps(results)
        except Exception as e:
            return json.dumps({"error": str(e)})

    async def _arun(self, price_history: str) -> str:
        return self._run(price_history)

class AnalysisAgent(Agent):
    def __init__(self):
        super().__init__(
            role="Pricing Analyst",
            goal="Generate 7-day price forecasts and trend analysis",
            tools=[ProphetForecastTool()],
            memory=RedisVectorStoreMemory(
                redis_url=os.getenv("REDIS_URL"),
                embeddings=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            ),
            verbose=True
        )

    def analyze(self, price_history: str) -> Dict[str, Any]:
        """Analyze price history and generate forecasts"""
        result = super().execute(price_history)
        
        # Store analysis in Redis
        redis_client = redis.Redis.from_url(os.getenv("REDIS_URL"))
        key = f"analysis:{datetime.now().strftime('%Y-%m-%d')}"
        redis_client.setex(key, 604800, json.dumps(result))  # 7-day TTL
        
        return result

if __name__ == "__main__":
    # Example usage
    agent = AnalysisAgent()
    result = agent.analyze('{"timestamp": ["2025-06-01", "2025-06-02"], "price": [100, 105]}')
    print(result)
