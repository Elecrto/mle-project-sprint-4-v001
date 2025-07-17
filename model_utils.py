import os
import io
import logging
import pandas as pd
from dotenv import load_dotenv
import boto3
from implicit.als import AlternatingLeastSquares

load_dotenv()
logger = logging.getLogger("uvicorn.info")

s3_session = boto3.session.Session()
s3_client = s3_session.client(
    service_name="s3",
    endpoint_url=os.getenv("S3_ENDPOINT"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
)
S3_BUCKET = os.getenv("S3_BUCKET_NAME")

ml_model = AlternatingLeastSquares(
    factors=50, 
    iterations=50, 
    regularization=0.05, 
    random_state=42
)
model_data = s3_client.get_object(
    Bucket=S3_BUCKET, 
    Key=os.getenv("MODEL_KEY")
)
ml_model = ml_model.load(io.BytesIO(model_data["Body"].read()))

track_meta = s3_client.get_object(
    Bucket=S3_BUCKET, 
    Key=os.getenv("TRACKS_META_KEY")
)
track_df = pd.read_parquet(io.BytesIO(track_meta["Body"].read()))

class SuggestionEngine:
    def __init__(self):
        self.suggestion_cache = {"custom": None, "general": None}
        self.usage_metrics = {"custom_requests": 0, "general_requests": 0}

    def refresh_data(self, rec_type: str, **kwargs):
        logger.info(f"Refreshing {rec_type} suggestions")
        env_key = "CUSTOM_RECS_KEY" if rec_type == "custom" else "TOP_RECS_KEY"
        
        data_object = s3_client.get_object(
            Bucket=S3_BUCKET, 
            Key=os.getenv(env_key)
        )
        df = pd.read_parquet(io.BytesIO(data_object["Body"].read()), **kwargs)
        
        if rec_type == "custom":
            df = df.set_index("user_id")
        self.suggestion_cache[rec_type] = df
        logger.info("Refresh completed")

    def fetch_suggestions(self, user_id: int, limit: int = 100):
        try:
            suggestions = self.suggestion_cache["custom"].loc[user_id]["track_id"].tolist()[:limit]
            self.usage_metrics["custom_requests"] += 1
            logger.info(f"Custom suggestions found: {len(suggestions)}")
        except KeyError:
            suggestions = self.suggestion_cache["general"]["track_id"].tolist()[:limit]
            self.usage_metrics["general_requests"] += 1
            logger.info(f"Using general suggestions: {len(suggestions)}")
        
        return suggestions or []

    def get_metrics(self):
        return self.usage_metrics.copy()

class UserActivityTracker:
    def __init__(self, max_history: int = 15):
        self.user_history = {}
        self.max_history = max_history

    def record_event(self, user_id: int, item_id: int):
        history = self.user_history.get(user_id, [])
        updated_history = [item_id] + history[:self.max_history-1]
        self.user_history[user_id] = updated_history

    def retrieve_history(self, user_id: int, limit: int):
        return self.user_history.get(user_id, [])[:limit]

suggestion_system = SuggestionEngine()
activity_tracker = UserActivityTracker()

async def find_similar_items(track_id: int, count: int = 5):
    track_data = track_df[track_df["track_id"] == track_id]
    if track_data.empty:
        return [], []
    
    encoded_id = track_data["track_id_enc"].values[0]
    similar = ml_model.similar_items(encoded_id, N=count+1)
    
    enc_ids, scores = similar[0][1:count+1], similar[1][1:count+1]
    similar_tracks = track_df[
        track_df["track_id_enc"].isin(enc_ids)
    ]["track_id"].tolist()
    
    return similar_tracks, scores