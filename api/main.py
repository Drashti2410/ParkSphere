from fastapi import FastAPI
from api.db import get_recent_events, get_occupancy_stats

app = FastAPI(title="ParkSphere API")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/history")
def history(limit: int = 50):
    return get_recent_events(limit)

@app.get("/stats")
def stats():
    return get_occupancy_stats()
