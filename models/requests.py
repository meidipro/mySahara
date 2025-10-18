"""
Pydantic request models for API endpoints.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime


class OCRRequest(BaseModel):
    """
    Request model for OCR processing.
    """
    image_base64: Optional[str] = Field(None, description="Base64 encoded image")
    image_url: Optional[str] = Field(None, description="URL to image")
    language: str = Field(default="en", description="Language code (en, bn)")
    extract_medical_data: bool = Field(default=False, description="Extract structured medical data")

    @validator('image_base64', 'image_url')
    def validate_image_source(cls, v, values):
        if not values.get('image_base64') and not v:
            raise ValueError('Either image_base64 or image_url must be provided')
        return v


class MedicalDocumentRequest(BaseModel):
    """
    Request model for medical document OCR processing.
    """
    image_base64: Optional[str] = Field(None, description="Base64 encoded image")
    image_url: Optional[str] = Field(None, description="URL to image")
    document_type: str = Field(default="prescription", description="Type of medical document")
    language: str = Field(default="en", description="Language code (en, bn)")


class ChatRequest(BaseModel):
    """
    Request model for AI chat.
    """
    message: str = Field(..., description="User message", min_length=1)
    language: str = Field(default="en", description="Language code (en, bn)")
    conversation_history: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description="Previous conversation messages"
    )
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional context (user health data, etc.)"
    )
    use_medical_mode: bool = Field(
        default=True,
        description="Use medical assistant system prompt"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message": "What are the symptoms of diabetes?",
                "language": "en",
                "conversation_history": [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi! How can I help you today?"}
                ],
                "use_medical_mode": True
            }
        }


class SymptomAnalysisRequest(BaseModel):
    """
    Request model for symptom analysis.
    """
    symptoms: List[str] = Field(..., description="List of symptoms", min_items=1)
    duration: Optional[str] = Field(None, description="Duration of symptoms")
    severity: Optional[str] = Field(None, description="Severity level (mild, moderate, severe)")
    age: Optional[int] = Field(None, description="Patient age", ge=0, le=150)
    gender: Optional[str] = Field(None, description="Patient gender")
    existing_conditions: Optional[List[str]] = Field(
        default=None,
        description="Existing medical conditions"
    )
    medications: Optional[List[str]] = Field(
        default=None,
        description="Current medications"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "symptoms": ["fever", "cough", "fatigue"],
                "duration": "3 days",
                "severity": "moderate",
                "age": 35,
                "gender": "male"
            }
        }


class HealthTipsRequest(BaseModel):
    """
    Request model for health tips.
    """
    category: Optional[str] = Field(None, description="Health category (nutrition, exercise, mental)")
    language: str = Field(default="en", description="Language code (en, bn)")
    personalized: bool = Field(default=False, description="Get personalized tips")
    user_profile: Optional[Dict[str, Any]] = Field(
        default=None,
        description="User profile for personalization"
    )


class AINutritionFitnessRequest(BaseModel):
    """
    Request model for the AI Nutrition & Fitness Coach.
    """
    age: int = Field(..., description="User's age", ge=1, le=120)
    gender: str = Field(..., description="User's gender (e.g., 'male', 'female', 'other')")
    height_cm: float = Field(..., description="User's height in centimeters", ge=50, le=300)
    weight_kg: float = Field(..., description="User's weight in kilograms", ge=20, le=500)
    activity_level: str = Field(..., description="e.g., 'sedentary', 'lightly active', 'moderately active', 'very active'")
    goal: str = Field(..., description="User's primary goal (e.g., 'weight_loss', 'muscle_gain', 'maintenance', 'improve_fitness')")
    dietary_preferences: Optional[List[str]] = Field(default=None, description="e.g., 'vegetarian', 'vegan', 'gluten-free'")
    available_local_foods: Optional[str] = Field(default=None, description="A text description of locally available foods and cuisine style.")
    equipment: str = Field(..., description="e.g., 'none', 'basic_home', 'full_gym'")
    workout_time_minutes: int = Field(..., description="Available time for workout in minutes per day", ge=10, le=180)
    
    class Config:
        json_schema_extra = {
            "example": {
                "age": 30,
                "gender": "male",
                "height_cm": 175,
                "weight_kg": 80,
                "activity_level": "moderately active",
                "goal": "weight_loss",
                "dietary_preferences": ["vegetarian"],
                "available_local_foods": "Rice, lentils, seasonal vegetables like spinach and carrots, chicken, and fish are commonly available.",
                "equipment": "basic_home",
                "workout_time_minutes": 45
            }
        }


class PredictiveHealthRequest(BaseModel):
    """
    Request model for predictive health intelligence.
    """
    health_metrics: Dict[str, Any] = Field(..., description="Health metrics data")
    medical_history: Optional[List[str]] = Field(
        default=None,
        description="Medical history"
    )
    lifestyle_factors: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Lifestyle factors (diet, exercise, sleep)"
    )
    family_history: Optional[List[str]] = Field(
        default=None,
        description="Family medical history"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "health_metrics": {
                    "blood_pressure": "140/90",
                    "blood_sugar": "180",
                    "bmi": "28.5"
                },
                "medical_history": ["hypertension"],
                "lifestyle_factors": {
                    "exercise": "2 times per week",
                    "diet": "high carb",
                    "sleep": "5-6 hours"
                }
            }
        }
