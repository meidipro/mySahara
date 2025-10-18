"""
Pydantic response models for API endpoints.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class OCRResponse(BaseModel):
    """
    Response model for OCR processing.
    """
    success: bool = Field(..., description="Processing success status")
    text: Optional[str] = Field(None, description="Extracted text")
    confidence: Optional[float] = Field(None, description="OCR confidence score")
    language: Optional[str] = Field(None, description="Detected language")
    error: Optional[str] = Field(None, description="Error message if failed")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "text": "Prescription details...",
                "confidence": 0.95,
                "language": "en",
                "processing_time": 1.23
            }
        }


class MedicalDocumentResponse(BaseModel):
    """
    Response model for medical document OCR.
    """
    success: bool = Field(..., description="Processing success status")
    document_type: Optional[str] = Field(None, description="Type of document")
    extracted_data: Optional[Dict[str, Any]] = Field(
        None,
        description="Structured medical data"
    )
    raw_text: Optional[str] = Field(None, description="Raw extracted text")
    confidence: Optional[float] = Field(None, description="Overall confidence score")
    error: Optional[str] = Field(None, description="Error message if failed")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "document_type": "prescription",
                "extracted_data": {
                    "doctor_name": "Dr. Smith",
                    "hospital": "City Hospital",
                    "date": "2025-10-12",
                    "patient_name": "John Doe",
                    "medications": [
                        {
                            "name": "Amoxicillin",
                            "dosage": "500mg",
                            "frequency": "3 times daily",
                            "duration": "7 days"
                        }
                    ],
                    "diagnosis": "Upper respiratory infection"
                },
                "raw_text": "Dr. Smith...",
                "confidence": 0.92
            }
        }


class ChatResponse(BaseModel):
    """
    Response model for AI chat.
    """
    success: bool = Field(..., description="Processing success status")
    message: Optional[str] = Field(None, description="AI response message")
    language: Optional[str] = Field(None, description="Response language")
    model_used: Optional[str] = Field(None, description="AI model used")
    confidence: Optional[float] = Field(None, description="Response confidence")
    suggestions: Optional[List[str]] = Field(
        None,
        description="Follow-up suggestions"
    )
    error: Optional[str] = Field(None, description="Error message if failed")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Diabetes symptoms include increased thirst, frequent urination...",
                "language": "en",
                "model_used": "llama-3.1-70b",
                "confidence": 0.95,
                "suggestions": [
                    "Would you like to know about diabetes prevention?",
                    "Should I explain diabetes management?"
                ],
                "processing_time": 0.87
            }
        }


class HealthAnalysisResponse(BaseModel):
    """
    Response model for health analysis.
    """
    success: bool = Field(..., description="Analysis success status")
    analysis: Optional[str] = Field(None, description="Health analysis text")
    risk_level: Optional[str] = Field(None, description="Risk level (low, medium, high)")
    recommendations: Optional[List[str]] = Field(
        None,
        description="Health recommendations"
    )
    possible_conditions: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Possible conditions with probability"
    )
    urgent_care_needed: Optional[bool] = Field(
        None,
        description="Whether urgent care is recommended"
    )
    disclaimer: Optional[str] = Field(
        None,
        description="Medical disclaimer"
    )
    error: Optional[str] = Field(None, description="Error message if failed")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "analysis": "Based on symptoms, possible respiratory infection...",
                "risk_level": "medium",
                "recommendations": [
                    "Rest and hydration",
                    "Monitor temperature",
                    "Consult doctor if symptoms worsen"
                ],
                "possible_conditions": [
                    {"condition": "Common Cold", "probability": 0.7},
                    {"condition": "Flu", "probability": 0.3}
                ],
                "urgent_care_needed": False,
                "disclaimer": "This is not medical advice. Please consult a healthcare professional."
            }
        }


class HealthTipsResponse(BaseModel):
    """
    Response model for health tips.
    """
    success: bool = Field(..., description="Success status")
    tips: Optional[List[Dict[str, str]]] = Field(
        None,
        description="Health tips list"
    )
    category: Optional[str] = Field(None, description="Category of tips")
    personalized: Optional[bool] = Field(None, description="Whether tips are personalized")
    error: Optional[str] = Field(None, description="Error message if failed")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "tips": [
                    {
                        "title": "Stay Hydrated",
                        "description": "Drink at least 8 glasses of water daily",
                        "icon": "water_drop"
                    }
                ],
                "category": "general",
                "personalized": False
            }
        }


class AINutritionFitnessResponse(BaseModel):
    """
    Response model for the AI Nutrition & Fitness Coach.
    """
    success: bool = Field(..., description="Request success status")
    nutrition_plan: Optional[Dict[str, Any]] = Field(None, description="Structured daily nutrition plan.")
    supplement_plan: Optional[Dict[str, Any]] = Field(None, description="Structured supplement recommendations.")
    exercise_plan: Optional[Dict[str, Any]] = Field(None, description="Structured weekly exercise plan.")
    disclaimer: Optional[str] = Field(None, description="Important disclaimer about consulting professionals.")
    error: Optional[str] = Field(None, description="Error message if the request failed.")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "nutrition_plan": {
                    "daily_calories": 2200,
                    "macronutrients": {"protein_g": 150, "carbs_g": 250, "fat_g": 60},
                    "daily_plans": [
                        {
                            "day": "Monday",
                            "meals": [
                                {"meal": "Breakfast", "food": "2 boiled eggs, 2 chapatis, 1 banana", "calories": 400, "alternatives": "Oatmeal with milk and nuts"},
                                {"meal": "Lunch", "food": "1 cup rice, 100g fish curry, mixed vegetables", "calories": 600, "alternatives": "Quinoa with grilled chicken and salad"},
                                {"meal": "Dinner", "food": "Grilled chicken, sautéed spinach, ½ cup rice", "calories": 700, "alternatives": "Lentil soup (dal) with brown rice"}
                            ]
                        }
                    ]
                },
                "supplement_plan": {
                    "recommendations": [
                        {"supplement": "Whey Protein", "dosage": "1 scoop post-workout", "reason": "To support muscle repair and growth."},
                        {"supplement": "Vitamin D", "dosage": "2000 IU daily", "reason": "For bone health and immune support, especially if sun exposure is limited."}
                    ]
                },
                "exercise_plan": {
                    "weekly_schedule": [
                        {
                            "day": "Monday", 
                            "activity": "Full Body HIIT", 
                            "duration_minutes": 45,
                            "exercises": ["Jumping Jacks", "Burpees", "High Knees", "Squats", "Push-ups"]
                        },
                        {
                            "day": "Tuesday", 
                            "activity": "Upper Body Strength", 
                            "duration_minutes": 60,
                            "exercises": ["Dumbbell Bench Press", "Dumbbell Rows", "Overhead Press", "Bicep Curls"]
                        }
                    ],
                    "progression_advice": "Try to increase the number of reps or the weight for strength exercises each week. For cardio, you can increase the duration or intensity."
                },
                "disclaimer": "This is an AI-generated plan. Consult with a qualified healthcare provider and fitness professional before making any changes to your diet or exercise routine."
            }
        }


class PredictiveHealthResponse(BaseModel):
    """
    Response model for predictive health intelligence.
    """
    success: bool = Field(..., description="Prediction success status")
    predictions: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Health predictions"
    )
    risk_factors: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Identified risk factors"
    )
    preventive_measures: Optional[List[str]] = Field(
        None,
        description="Preventive measures"
    )
    timeline: Optional[str] = Field(None, description="Prediction timeline")
    confidence: Optional[float] = Field(None, description="Prediction confidence")
    error: Optional[str] = Field(None, description="Error message if failed")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "predictions": [
                    {
                        "condition": "Type 2 Diabetes",
                        "risk": "high",
                        "probability": 0.65,
                        "timeframe": "5-10 years"
                    }
                ],
                "risk_factors": [
                    {"factor": "High BMI", "impact": "high"},
                    {"factor": "Sedentary lifestyle", "impact": "medium"}
                ],
                "preventive_measures": [
                    "Increase physical activity to 150 minutes per week",
                    "Reduce sugar intake",
                    "Regular health checkups"
                ],
                "confidence": 0.75
            }
        }
