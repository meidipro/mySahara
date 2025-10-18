"""
Pydantic models for progress summary.
"""
from typing import Optional, List
from pydantic import BaseModel, Field

class ProgressDataPoint(BaseModel):
    date: str
    value: float

class ProgressSummaryResponse(BaseModel):
    start_weight: Optional[float] = Field(None)
    current_weight: Optional[float] = Field(None)
    target_weight: Optional[float] = Field(None)
    progress_percentage: Optional[float] = Field(None, description="Percentage of goal achieved.")
    motivational_message: str
    weight_history: List[ProgressDataPoint] = []
