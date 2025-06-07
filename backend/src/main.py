from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from redis import Redis
from bullmq import Queue
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Apon Family Mart AI Backend")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis connection
redis_client = Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

# BullMQ queues
price_queue = Queue("price-monitor", { connection: redis_client })
alert_queue = Queue("alert-generator", { connection: redis_client })
report_queue = Queue("report-generator", { connection: redis_client })

@app.get("/api/price-trends")
async def get_price_trends():
    """Get price trends from Redis"""
    trends = redis_client.get("price:trends")
    return {
        "status": "success",
        "data": json.loads(trends) if trends else []
    }

@app.get("/api/alerts")
async def get_alerts():
    """Get recent alerts"""
    alerts = redis_client.lrange("alerts:recent", 0, -1)
    return {
        "status": "success",
        "data": [json.loads(alert) for alert in alerts]
    }

@app.get("/api/competitor-status")
async def get_competitor_status():
    """Get competitor monitoring status"""
    status = redis_client.hgetall("competitors:status")
    return {
        "status": "success",
        "data": status
    }

@app.websocket("/ws/monitor")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_text()
            # Handle WebSocket messages
            await websocket.send_json({
                "type": "status",
                "data": "connected"
            })
    except:
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
