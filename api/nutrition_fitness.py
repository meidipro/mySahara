"""
API endpoints for the AI Nutrition & Fitness Coach.
"""

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from models.requests import AINutritionFitnessRequest
from models.responses import AINutritionFitnessResponse
from services.ai_service import AIService, get_ai_service

router = APIRouter()

@router.post("/plan", response_model=AINutritionFitnessResponse)
async def get_nutrition_fitness_plan(
    request: AINutritionFitnessRequest,
    ai_service: AIService = Depends(get_ai_service)
):
    """
    Generate a personalized nutrition, supplement, and exercise plan.
    """
    try:
        logger.info(f"Received nutrition & fitness plan request for user aged {request.age}")
        plan = await ai_service.create_nutrition_fitness_plan(request)
        # If AI failed, return proper error status so clients can handle it
        if not plan.get("success", False):
            raise HTTPException(status_code=502, detail=plan.get("error", "Plan generation failed"))
        return plan
    except Exception as e:
        logger.error(f"Error generating nutrition & fitness plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))
