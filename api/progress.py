"""
API endpoints for progress tracking.
"""
from fastapi import APIRouter, Depends, HTTPException
from supabase import Client

from services.progress_service import ProgressService
from models.progress_models import ProgressSummaryResponse
from utils.helpers import get_supabase_client
from api.logs import get_user_id # Re-using the dependency from logs api

router = APIRouter()

@router.get("/summary", response_model=ProgressSummaryResponse)
async def get_progress_summary(
    user_id: str = Depends(get_user_id),
    db: Client | None = Depends(get_supabase_client)
):
    service = ProgressService(db)
    summary = await service.get_progress_summary(user_id)
    return summary
