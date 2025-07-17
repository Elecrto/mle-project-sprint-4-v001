from model_utils import suggestion_system, activity_tracker, track_df, find_similar_items
from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("uvicorn.info")

@asynccontextmanager
async def service_lifecycle(app: FastAPI):
    logger.info("Initializing service components")
    
    suggestion_system.refresh_data(
        rec_type="custom",
        columns=["user_id", "track_id", "score"]
    )
    suggestion_system.refresh_data(
        rec_type="general",
        columns=["track_id", "popularity_weighted"]
    )
    
    yield
    
    logger.info("Terminating service")

app = FastAPI(
    title="Track Suggestion API",
    lifespan=service_lifecycle
)

@app.post("/suggestions")
async def generate_suggestions(user_id: int, limit: int = 100):
    offline_suggestions = suggestion_system.fetch_suggestions(user_id, limit)
    online_suggestions = await generate_realtime_suggestions(user_id, limit)
    
    combined = []
    for o, r in zip(offline_suggestions, online_suggestions):
        combined.extend([r, o])
    
    unique_suggestions = []
    for item in combined + offline_suggestions + online_suggestions:
        if item not in unique_suggestions:
            unique_suggestions.append(item)
    
    return {"suggestions": unique_suggestions[:limit]}

@app.post("/realtime_suggestions")
async def generate_realtime_suggestions(user_id: int, limit: int = 100):
    recent_actions = activity_tracker.retrieve_history(user_id, 10)
    
    similar_items = []
    for action in recent_actions:
        items, _ = await find_similar_items(action)
        similar_items.extend(items)
    
    return {"suggestions": list(dict.fromkeys(similar_items))[:limit]}

@app.post("/log_action")
async def log_user_action(user_id: int, item_id: int):
    activity_tracker.record_event(user_id, item_id)
    return {"status": "success"}

@app.get("/user_actions")
async def get_user_actions(user_id: int, count: int = 10):
    return {"history": activity_tracker.retrieve_history(user_id, count)}

@app.get("/refresh_suggestions")
async def refresh_suggestions(rec_type: str):
    suggestion_system.refresh_data(rec_type)
    return {"status": "refreshed"}

@app.get("/system_metrics")
async def get_system_metrics():
    return suggestion_system.get_metrics()