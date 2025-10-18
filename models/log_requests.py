"""
Pydantic models for logging requests.
"""
from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field
import datetime as dt

class DailyHealthLogRequest(BaseModel):
    date: dt.date = Field(..., description="The date of the log entry.")
    weight_kg: Optional[float] = Field(None, description="User's weight in kilograms.")
    body_fat_percentage: Optional[float] = Field(None, description="User's body fat percentage.")
    calorie_intake: Optional[int] = Field(None, description="User's daily calorie intake.")
    water_intake_ml: Optional[int] = Field(None, description="User's daily water intake in milliliters.")

class ExerciseLogRequest(BaseModel):
    date: dt.date = Field(..., description="The date of the exercise.")
    exercise_name: str = Field(..., description="The name of the exercise.")
    sets: Optional[int] = Field(None)
    reps: Optional[int] = Field(None)
    weight_kg: Optional[float] = Field(None)
    duration_minutes: Optional[int] = Field(None)
