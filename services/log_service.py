"""
Service for handling health and exercise logs.
"""
from typing import Dict, Any
from supabase import Client
from models.log_requests import DailyHealthLogRequest, ExerciseLogRequest

class LogService:
    def __init__(self, db: Client):
        self.db = db

    async def log_daily_health(self, user_id: str, log_data: DailyHealthLogRequest) -> Dict[str, Any]:
        data_to_upsert = log_data.dict()
        data_to_upsert['user_id'] = user_id

        response = self.db.table('daily_health_logs').upsert(data_to_upsert, on_conflict='user_id,date').execute()
        
        if response.data:
            return {"success": True, "data": response.data[0]}
        return {"success": False, "error": "Failed to save daily log."}

    async def log_exercise(self, user_id: str, log_data: ExerciseLogRequest) -> Dict[str, Any]:
        data_to_insert = log_data.dict()
        data_to_insert['user_id'] = user_id

        response = self.db.table('exercise_logs').insert(data_to_insert).execute()

        if response.data:
            return {"success": True, "data": response.data[0]}
        return {"success": False, "error": "Failed to save exercise log."}
