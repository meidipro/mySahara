"""
API endpoints for logging health data.
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Optional
from supabase import Client

from services.log_service import LogService
from models.log_requests import DailyHealthLogRequest, ExerciseLogRequest
from utils.helpers import get_supabase_client # Assuming you have a helper to get supabase client

router = APIRouter()

async def get_user_id(
    authorization: Optional[str] = Header(None),
    db: Client | None = Depends(get_supabase_client)
) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    if db is None:
        # If DB isn't configured, we can't validate the token; reject explicitly
        raise HTTPException(status_code=503, detail="Auth not available: database not configured")

    try:
        scheme, token = authorization.split(" ", 1)
        if scheme.lower() != "bearer" or not token:
            raise ValueError("Malformed Authorization header")

        # Validate the access token and get the user
        user_resp = db.auth.get_user(token)
        if not user_resp or not getattr(user_resp, 'user', None):
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        return user_resp.user.id
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")

@router.post("/daily", status_code=201)
async def log_daily_health_entry(
    log_data: DailyHealthLogRequest,
    user_id: str = Depends(get_user_id),
    db: Client = Depends(get_supabase_client)
):
    service = LogService(db)
    result = await service.log_daily_health(user_id, log_data)
    if not result['success']:
        raise HTTPException(status_code=500, detail=result.get('error'))
    return result['data']

@router.post("/exercise", status_code=201)
async def log_exercise_entry(
    log_data: ExerciseLogRequest,
    user_id: str = Depends(get_user_id),
    db: Client = Depends(get_supabase_client)
):
    service = LogService(db)
    result = await service.log_exercise(user_id, log_data)
    if not result['success']:
        raise HTTPException(status_code=500, detail=result.get('error'))
    return result['data']
