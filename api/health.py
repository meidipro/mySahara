"""
Health Analysis API endpoints for symptom analysis, health tips, and predictions.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from loguru import logger

from models.requests import (
    SymptomAnalysisRequest,
    HealthTipsRequest,
    PredictiveHealthRequest
)
from models.responses import (
    HealthAnalysisResponse,
    HealthTipsResponse,
    PredictiveHealthResponse
)
from services.ai_service import AIService

router = APIRouter()
ai_service = AIService()


@router.post("/analyze-symptoms", response_model=HealthAnalysisResponse)
async def analyze_symptoms(request: SymptomAnalysisRequest):
    """
    Analyze symptoms and provide health insights.

    Args:
        request: SymptomAnalysisRequest with symptoms and patient info

    Returns:
        HealthAnalysisResponse with analysis and recommendations

    Raises:
        HTTPException: If analysis fails
    """
    try:
        logger.info(f"Analyzing symptoms: {', '.join(request.symptoms)}")

        # Prepare additional info
        additional_info = {}

        if request.age:
            additional_info["age"] = request.age

        if request.gender:
            additional_info["gender"] = request.gender

        if request.existing_conditions:
            additional_info["existing_conditions"] = request.existing_conditions

        if request.medications:
            additional_info["current_medications"] = request.medications

        # Call AI service
        result = await ai_service.analyze_symptoms(
            symptoms=request.symptoms,
            duration=request.duration,
            severity=request.severity,
            additional_info=additional_info
        )

        if result["success"]:
            # Parse response to extract structured data
            analysis_text = result.get("analysis", "")

            # Determine risk level (simplified - could be enhanced with NLP)
            risk_level = _determine_risk_level(request.symptoms, request.severity)

            # Extract possible conditions (simplified)
            possible_conditions = _extract_conditions(analysis_text)

            # Generate recommendations
            recommendations = _generate_recommendations(
                request.symptoms,
                request.severity,
                risk_level
            )

            # Determine if urgent care needed
            urgent_care = _check_urgent_care(request.symptoms, request.severity)

            return HealthAnalysisResponse(
                success=True,
                analysis=analysis_text,
                risk_level=risk_level,
                recommendations=recommendations,
                possible_conditions=possible_conditions,
                urgent_care_needed=urgent_care,
                disclaimer="This is not medical advice. Please consult a healthcare professional for proper diagnosis and treatment."
            )
        else:
            return HealthAnalysisResponse(
                success=False,
                error=result.get("error", "Analysis failed")
            )

    except Exception as e:
        logger.error(f"Symptom analysis error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Symptom analysis failed: {str(e)}"
        )


@router.get("/tips", response_model=HealthTipsResponse)
async def get_health_tips(
    category: str = None,
    language: str = "en",
    personalized: bool = False
):
    """
    Get health tips and recommendations.

    Args:
        category: Health category (nutrition, exercise, mental, sleep, etc.)
        language: Language code
        personalized: Whether to get personalized tips

    Returns:
        HealthTipsResponse with health tips
    """
    try:
        logger.info(f"Getting health tips - Category: {category}")

        # Call AI service
        result = await ai_service.generate_health_tips(
            category=category,
            language=language,
            personalized=personalized
        )

        if result["success"]:
            # Parse tips from response
            tips_text = result.get("message", "")
            tips = _parse_health_tips(tips_text)

            return HealthTipsResponse(
                success=True,
                tips=tips,
                category=category or "general",
                personalized=personalized
            )
        else:
            return HealthTipsResponse(
                success=False,
                error=result.get("error", "Failed to generate tips")
            )

    except Exception as e:
        logger.error(f"Health tips error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get health tips: {str(e)}"
        )


@router.post("/predict", response_model=PredictiveHealthResponse)
async def predict_health_risks(request: PredictiveHealthRequest):
    """
    Predict potential health risks based on metrics and history.

    Args:
        request: PredictiveHealthRequest with health data

    Returns:
        PredictiveHealthResponse with risk predictions

    Raises:
        HTTPException: If prediction fails
    """
    try:
        logger.info("Generating health risk predictions")

        # Call AI service
        result = await ai_service.predict_health_risks(
            health_metrics=request.health_metrics,
            medical_history=request.medical_history,
            lifestyle_factors=request.lifestyle_factors
        )

        if result["success"]:
            # Parse prediction response
            prediction_text = result.get("message", "")

            # Extract predictions
            predictions = _extract_predictions(prediction_text)

            # Extract risk factors
            risk_factors = _extract_risk_factors(
                request.health_metrics,
                request.medical_history,
                request.lifestyle_factors
            )

            # Generate preventive measures
            preventive_measures = _generate_preventive_measures(predictions)

            return PredictiveHealthResponse(
                success=True,
                predictions=predictions,
                risk_factors=risk_factors,
                preventive_measures=preventive_measures,
                timeline="5-10 years",
                confidence=0.7
            )
        else:
            return PredictiveHealthResponse(
                success=False,
                error=result.get("error", "Prediction failed")
            )

    except Exception as e:
        logger.error(f"Health prediction error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Health prediction failed: {str(e)}"
        )


@router.get("/categories")
async def get_health_categories(language: str = "en"):
    """
    Get available health categories.

    Args:
        language: Language code

    Returns:
        List of health categories
    """
    if language == "bn":
        categories = [
            {"id": "nutrition", "name": "পুষ্টি", "icon": "restaurant"},
            {"id": "exercise", "name": "ব্যায়াম", "icon": "fitness_center"},
            {"id": "mental", "name": "মানসিক স্বাস্থ্য", "icon": "psychology"},
            {"id": "sleep", "name": "ঘুম", "icon": "bedtime"},
            {"id": "hydration", "name": "পানি পান", "icon": "water_drop"},
            {"id": "general", "name": "সাধারণ", "icon": "health_and_safety"}
        ]
    else:
        categories = [
            {"id": "nutrition", "name": "Nutrition", "icon": "restaurant"},
            {"id": "exercise", "name": "Exercise", "icon": "fitness_center"},
            {"id": "mental", "name": "Mental Health", "icon": "psychology"},
            {"id": "sleep", "name": "Sleep", "icon": "bedtime"},
            {"id": "hydration", "name": "Hydration", "icon": "water_drop"},
            {"id": "general", "name": "General", "icon": "health_and_safety"}
        ]

    return {
        "success": True,
        "categories": categories
    }


@router.get("/emergency-symptoms")
async def get_emergency_symptoms(language: str = "en"):
    """
    Get list of emergency symptoms that require immediate medical attention.

    Args:
        language: Language code

    Returns:
        List of emergency symptoms
    """
    if language == "bn":
        symptoms = [
            "বুকে ব্যথা বা চাপ",
            "শ্বাসকষ্ট",
            "হঠাৎ মাথা ঘোরা বা অজ্ঞান হয়ে যাওয়া",
            "তীব্র মাথাব্যথা",
            "অস্পষ্ট কথা বা দুর্বলতা",
            "তীব্র পেট ব্যথা",
            "অতিরিক্ত রক্তপাত",
            "খিঁচুনি"
        ]
    else:
        symptoms = [
            "Chest pain or pressure",
            "Difficulty breathing",
            "Sudden dizziness or fainting",
            "Severe headache",
            "Slurred speech or weakness",
            "Severe abdominal pain",
            "Excessive bleeding",
            "Seizures"
        ]

    return {
        "success": True,
        "emergency_symptoms": symptoms,
        "message": "If experiencing any of these symptoms, seek immediate medical attention."
    }


# Helper functions

def _determine_risk_level(symptoms: List[str], severity: str = None) -> str:
    """Determine risk level based on symptoms and severity."""
    # Simplified risk determination
    emergency_symptoms = [
        "chest pain", "difficulty breathing", "severe bleeding",
        "loss of consciousness", "seizure", "stroke symptoms"
    ]

    symptoms_lower = [s.lower() for s in symptoms]

    if any(em in ' '.join(symptoms_lower) for em in emergency_symptoms):
        return "high"

    if severity == "severe":
        return "high"
    elif severity == "moderate" or len(symptoms) > 3:
        return "medium"
    else:
        return "low"


def _extract_conditions(text: str) -> List[Dict[str, Any]]:
    """Extract possible conditions from analysis text."""
    # Simplified extraction - could be enhanced with NLP
    conditions = []

    # Common condition keywords
    condition_keywords = [
        "common cold", "flu", "infection", "diabetes", "hypertension",
        "migraine", "allergy", "gastritis", "anxiety", "depression"
    ]

    text_lower = text.lower()

    for condition in condition_keywords:
        if condition in text_lower:
            conditions.append({
                "condition": condition.title(),
                "probability": 0.5  # Placeholder
            })

    return conditions[:5]  # Return top 5


def _generate_recommendations(
    symptoms: List[str],
    severity: str = None,
    risk_level: str = "low"
) -> List[str]:
    """Generate health recommendations."""
    recommendations = []

    if risk_level == "high":
        recommendations.append("Seek immediate medical attention")
        recommendations.append("Do not delay consulting a healthcare professional")
    elif risk_level == "medium":
        recommendations.append("Consult a doctor soon")
        recommendations.append("Monitor symptoms closely")
    else:
        recommendations.append("Rest and stay hydrated")
        recommendations.append("Monitor symptoms for changes")

    # Add general recommendations
    recommendations.append("Maintain a healthy diet")
    recommendations.append("Get adequate sleep")
    recommendations.append("Track your symptoms")

    return recommendations


def _check_urgent_care(symptoms: List[str], severity: str = None) -> bool:
    """Check if urgent care is needed."""
    emergency_keywords = [
        "chest pain", "severe", "difficulty breathing", "bleeding",
        "unconscious", "seizure", "stroke"
    ]

    symptoms_text = ' '.join(symptoms).lower()

    return (
        any(keyword in symptoms_text for keyword in emergency_keywords) or
        severity == "severe"
    )


def _parse_health_tips(text: str) -> List[Dict[str, str]]:
    """Parse health tips from text."""
    tips = []

    # Split by newlines and look for numbered items
    lines = text.split('\n')

    for line in lines:
        line = line.strip()
        if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
            # Remove numbering
            tip_text = line.lstrip('0123456789.-•) ').strip()

            if tip_text:
                # Try to split into title and description
                if ':' in tip_text:
                    parts = tip_text.split(':', 1)
                    tips.append({
                        "title": parts[0].strip(),
                        "description": parts[1].strip(),
                        "icon": "health_and_safety"
                    })
                else:
                    tips.append({
                        "title": tip_text[:50],
                        "description": tip_text,
                        "icon": "health_and_safety"
                    })

    # If no tips found, create from full text
    if not tips:
        tips.append({
            "title": "Health Tip",
            "description": text,
            "icon": "health_and_safety"
        })

    return tips[:10]  # Limit to 10 tips


def _extract_predictions(text: str) -> List[Dict[str, Any]]:
    """Extract health predictions from text."""
    # Simplified extraction
    predictions = []

    # Common conditions to look for
    conditions = [
        "diabetes", "heart disease", "hypertension", "stroke",
        "obesity", "cancer", "arthritis"
    ]

    text_lower = text.lower()

    for condition in conditions:
        if condition in text_lower:
            predictions.append({
                "condition": condition.title(),
                "risk": "medium",
                "probability": 0.5,
                "timeframe": "5-10 years"
            })

    return predictions[:5]


def _extract_risk_factors(
    health_metrics: Dict[str, Any],
    medical_history: List[str] = None,
    lifestyle_factors: Dict[str, Any] = None
) -> List[Dict[str, Any]]:
    """Extract risk factors from health data."""
    risk_factors = []

    # Check health metrics
    if health_metrics:
        # BMI check
        bmi = health_metrics.get("bmi")
        if bmi and isinstance(bmi, (int, float)):
            if bmi > 30:
                risk_factors.append({
                    "factor": "High BMI (Obesity)",
                    "impact": "high"
                })
            elif bmi > 25:
                risk_factors.append({
                    "factor": "Overweight",
                    "impact": "medium"
                })

        # Blood pressure
        bp = health_metrics.get("blood_pressure")
        if bp and "/" in str(bp):
            systolic = int(str(bp).split("/")[0])
            if systolic > 140:
                risk_factors.append({
                    "factor": "High Blood Pressure",
                    "impact": "high"
                })

    # Check medical history
    if medical_history:
        for condition in medical_history:
            risk_factors.append({
                "factor": f"History of {condition}",
                "impact": "medium"
            })

    # Check lifestyle factors
    if lifestyle_factors:
        if lifestyle_factors.get("smoking"):
            risk_factors.append({
                "factor": "Smoking",
                "impact": "high"
            })

        exercise = lifestyle_factors.get("exercise", "")
        if "sedentary" in str(exercise).lower() or "none" in str(exercise).lower():
            risk_factors.append({
                "factor": "Sedentary Lifestyle",
                "impact": "medium"
            })

    return risk_factors


def _generate_preventive_measures(predictions: List[Dict[str, Any]]) -> List[str]:
    """Generate preventive measures based on predictions."""
    measures = [
        "Maintain a healthy, balanced diet",
        "Exercise regularly (150 minutes per week)",
        "Get regular health checkups",
        "Manage stress through relaxation techniques",
        "Get adequate sleep (7-8 hours)",
        "Stay hydrated",
        "Avoid smoking and excessive alcohol",
        "Monitor your health metrics regularly"
    ]

    return measures[:5]
