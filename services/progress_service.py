"""
Service for calculating user progress and generating motivation.
"""
from typing import Dict, Any, List, Optional
from supabase import Client
from datetime import date, timedelta

class ProgressService:
    def __init__(self, db: Optional[Client]):
        self.db = db

    def _get_motivational_message(self, progress_percentage: Optional[float], current_weight: float, target_weight: float) -> str:
        if progress_percentage is None:
            return "Start logging your weight to see your progress!"
        
        if progress_percentage >= 100:
            return f"Congratulations! You've reached your goal of {target_weight} kg! Keep up the great work maintaining it."
        if progress_percentage >= 75:
            return f"You're so close! Only {abs(current_weight - target_weight):.1f} kg to go. You can do this!"
        if progress_percentage >= 50:
            return "You're halfway there! Your consistency is paying off. Keep pushing!"
        if progress_percentage >= 10:
            return "Great start! Every step forward is a victory. Keep making healthy choices."
        if progress_percentage > 0:
            return "The journey of a thousand miles begins with a single step. You've taken it!"
        
        return "Let's get started on your goal! Log your meals and workouts to make progress."

    async def get_progress_summary(self, user_id: str) -> Dict[str, Any]:
        if self.db is None:
            return {"motivational_message": "Connect database to enable progress tracking.", "weight_history": []}

        # 1. Get user's target weight
        try:
            user_response = self.db.table('users').select('target_weight', 'created_at').eq('id', user_id).single().execute()
        except Exception:
            # If table missing or query fails, return friendly default
            return {"motivational_message": "Set a target weight in your profile to start tracking progress!", "weight_history": []}

        if not user_response or not user_response.data:
            return {"motivational_message": "Set a target weight in your profile to start tracking progress!", "weight_history": []}
        
        target_weight = user_response.data.get('target_weight')
        if not target_weight:
            return {"motivational_message": "Set a target weight in your profile to start tracking progress!", "weight_history": []}

        # 2. Get all weight logs for the user
        try:
            log_response = self.db.table('daily_health_logs').select('date', 'weight_kg').eq('user_id', user_id).order('date', desc=False).execute()
        except Exception:
            return {"motivational_message": "Log your weight to start seeing your progress chart!", "weight_history": []}
        
        weight_history = [
            {"date": log['date'], "value": log['weight_kg']}
            for log in log_response.data if log.get('weight_kg') is not None
        ]

        if not weight_history:
            return {"motivational_message": "Log your weight to start seeing your progress chart!", "weight_history": []}

        # 3. Calculate progress
        start_weight = weight_history[0]['value']
        current_weight = weight_history[-1]['value']
        progress_percentage = None

        initial_diff = abs(start_weight - target_weight)
        current_diff = abs(current_weight - target_weight)

        if initial_diff > 0:
            progress_percentage = ((initial_diff - current_diff) / initial_diff) * 100

        # 4. Get motivational message
        message = self._get_motivational_message(progress_percentage, current_weight, target_weight)

        return {
            "start_weight": start_weight,
            "current_weight": current_weight,
            "target_weight": target_weight,
            "progress_percentage": progress_percentage,
            "motivational_message": message,
            "weight_history": weight_history
        }
