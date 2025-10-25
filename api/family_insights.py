"""
Family Health Insights API endpoints for family-wide health analysis.
Supports Phase 5-7 features: Family stats, chronic diseases, health reports.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from loguru import logger
from pydantic import BaseModel

from services.ai_service import AIService

router = APIRouter()
ai_service = AIService()


# Request/Response Models
class FamilyMember(BaseModel):
    """Family member data model"""
    id: Optional[str] = None
    name: str
    relationship: str
    age: Optional[int] = None
    gender: Optional[str] = None
    chronic_diseases: Optional[List[str]] = []


class FamilyHealthInsightRequest(BaseModel):
    """Request for family-wide health insights"""
    family_members: List[FamilyMember]
    focus_areas: Optional[List[str]] = ["general"]  # general, diet, exercise, prevention
    language: str = "en"


class FamilyHealthInsightResponse(BaseModel):
    """Response with family health insights"""
    success: bool
    insights: Optional[List[Dict[str, Any]]] = None
    summary: Optional[str] = None
    recommendations: Optional[List[str]] = None
    risk_assessment: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class FamilyHealthReportRequest(BaseModel):
    """Request for comprehensive family health report"""
    family_members: List[FamilyMember]
    total_records: int = 0
    total_events: int = 0
    include_ai_analysis: bool = True
    language: str = "en"


class FamilyHealthReportResponse(BaseModel):
    """Response with generated family health report"""
    success: bool
    report_data: Optional[Dict[str, Any]] = None
    ai_summary: Optional[str] = None
    key_metrics: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@router.post("/generate-insights", response_model=FamilyHealthInsightResponse)
async def generate_family_insights(request: FamilyHealthInsightRequest):
    """
    Generate AI-powered health insights for the entire family.

    This endpoint analyzes chronic conditions across family members and provides:
    - Personalized recommendations for each member
    - Family-wide health patterns
    - Preventive care suggestions
    - Risk assessments

    Args:
        request: FamilyHealthInsightRequest with family member data

    Returns:
        FamilyHealthInsightResponse with insights and recommendations

    Raises:
        HTTPException: If insight generation fails
    """
    try:
        logger.info(f"Generating insights for {len(request.family_members)} family members")

        # Build context from family data
        family_context = _build_family_context(request.family_members)

        # Prepare prompt for AI
        prompt = _create_insight_prompt(
            family_context,
            request.focus_areas,
            request.language
        )

        # Call AI service
        result = await ai_service.chat(
            message=prompt,
            language=request.language,
            use_medical_mode=True,
            conversation_history=[]
        )

        if result["success"]:
            ai_response = result.get("message", "")

            # Parse AI response into structured insights
            insights = _parse_insights(ai_response, request.family_members)
            summary = _extract_summary(ai_response)
            recommendations = _extract_recommendations(ai_response)
            risk_assessment = _assess_family_risks(request.family_members)

            return FamilyHealthInsightResponse(
                success=True,
                insights=insights,
                summary=summary,
                recommendations=recommendations,
                risk_assessment=risk_assessment
            )
        else:
            return FamilyHealthInsightResponse(
                success=False,
                error=result.get("error", "Failed to generate insights")
            )

    except Exception as e:
        logger.error(f"Family insights generation error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate family insights: {str(e)}"
        )


@router.post("/generate-report", response_model=FamilyHealthReportResponse)
async def generate_family_report(request: FamilyHealthReportRequest):
    """
    Generate comprehensive family health report.

    Supports Phase 7 health report feature with:
    - Family statistics (members, records, events, conditions)
    - AI-powered health summary
    - Key health metrics and trends
    - Exportable data structure

    Args:
        request: FamilyHealthReportRequest with family data

    Returns:
        FamilyHealthReportResponse with report data

    Raises:
        HTTPException: If report generation fails
    """
    try:
        logger.info(f"Generating health report for {len(request.family_members)} members")

        # Calculate key metrics
        key_metrics = {
            "total_members": len(request.family_members),
            "total_records": request.total_records,
            "total_events": request.total_events,
            "members_with_conditions": sum(
                1 for m in request.family_members
                if m.chronic_diseases and len(m.chronic_diseases) > 0
            ),
            "unique_conditions": len(set(
                disease
                for member in request.family_members
                if member.chronic_diseases
                for disease in member.chronic_diseases
            )),
            "average_age": (
                sum(m.age for m in request.family_members if m.age) /
                len([m for m in request.family_members if m.age])
            ) if any(m.age for m in request.family_members) else None
        }

        # Build report data structure
        report_data = {
            "report_date": None,  # Frontend will add timestamp
            "family_summary": {
                "members": [
                    {
                        "name": m.name,
                        "relationship": m.relationship,
                        "conditions": m.chronic_diseases or []
                    }
                    for m in request.family_members
                ],
                "statistics": key_metrics
            },
            "health_records": {
                "total": request.total_records,
                "per_member": request.total_records / max(len(request.family_members), 1)
            },
            "medical_events": {
                "total": request.total_events,
                "per_member": request.total_events / max(len(request.family_members), 1)
            }
        }

        # Generate AI summary if requested
        ai_summary = None
        if request.include_ai_analysis and len(request.family_members) > 0:
            summary_prompt = _create_report_summary_prompt(
                request.family_members,
                key_metrics,
                request.language
            )

            ai_result = await ai_service.chat(
                message=summary_prompt,
                language=request.language,
                use_medical_mode=True,
                conversation_history=[]
            )

            if ai_result["success"]:
                ai_summary = ai_result.get("message", "")

        return FamilyHealthReportResponse(
            success=True,
            report_data=report_data,
            ai_summary=ai_summary,
            key_metrics=key_metrics
        )

    except Exception as e:
        logger.error(f"Family report generation error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate family report: {str(e)}"
        )


# Helper functions
def _build_family_context(family_members: List[FamilyMember]) -> Dict[str, Any]:
    """Build context dictionary from family member data"""
    return {
        "total_members": len(family_members),
        "members": [
            {
                "name": m.name,
                "relationship": m.relationship,
                "age": m.age,
                "gender": m.gender,
                "conditions": m.chronic_diseases or []
            }
            for m in family_members
        ],
        "all_conditions": list(set(
            disease
            for member in family_members
            if member.chronic_diseases
            for disease in member.chronic_diseases
        ))
    }


def _create_insight_prompt(
    family_context: Dict[str, Any],
    focus_areas: List[str],
    language: str
) -> str:
    """Create AI prompt for family health insights"""
    conditions_list = ", ".join(family_context["all_conditions"]) if family_context["all_conditions"] else "None"

    prompt = f"""As a family health advisor, analyze this family's health profile:

Family Members: {family_context['total_members']}
Chronic Conditions in Family: {conditions_list}

Focus Areas: {", ".join(focus_areas)}

Please provide:
1. Key health insights for the family
2. Personalized recommendations for managing existing conditions
3. Preventive care suggestions
4. Lifestyle modifications that benefit the whole family
5. Warning signs to watch for

Keep recommendations practical, family-friendly, and culturally sensitive."""

    return prompt


def _create_report_summary_prompt(
    family_members: List[FamilyMember],
    metrics: Dict[str, Any],
    language: str
) -> str:
    """Create prompt for AI report summary"""
    members_summary = "\n".join([
        f"- {m.name} ({m.relationship}): {', '.join(m.chronic_diseases) if m.chronic_diseases else 'No chronic conditions'}"
        for m in family_members
    ])

    prompt = f"""Generate a professional health report summary for this family:

Family Overview:
{members_summary}

Statistics:
- Total Members: {metrics['total_members']}
- Members with Conditions: {metrics['members_with_conditions']}
- Unique Conditions: {metrics['unique_conditions']}

Provide a concise, professional summary (2-3 paragraphs) suitable for:
- Sharing with healthcare providers
- Family health planning
- Insurance purposes

Include key health patterns and overall family health status."""

    return prompt


def _parse_insights(ai_response: str, family_members: List[FamilyMember]) -> List[Dict[str, Any]]:
    """Parse AI response into structured insights"""
    # Simple parsing - can be enhanced with more sophisticated NLP
    insights = []

    # Create general insight
    insights.append({
        "type": "general",
        "title": "Family Health Overview",
        "description": ai_response[:500] if len(ai_response) > 500 else ai_response,
        "priority": "high"
    })

    # Add condition-specific insights if family has chronic diseases
    all_conditions = set(
        disease
        for member in family_members
        if member.chronic_diseases
        for disease in member.chronic_diseases
    )

    for condition in all_conditions:
        insights.append({
            "type": "condition",
            "title": f"{condition} Management",
            "description": f"Family members with {condition} should monitor regularly and follow treatment plans.",
            "priority": "medium"
        })

    return insights


def _extract_summary(ai_response: str) -> str:
    """Extract summary from AI response"""
    # Take first paragraph or first 200 characters
    paragraphs = ai_response.split("\n\n")
    return paragraphs[0] if paragraphs else ai_response[:200]


def _extract_recommendations(ai_response: str) -> List[str]:
    """Extract recommendations from AI response"""
    recommendations = []

    # Simple extraction - look for numbered lists or bullet points
    lines = ai_response.split("\n")
    for line in lines:
        line = line.strip()
        if line and (line[0].isdigit() or line.startswith("-") or line.startswith("•")):
            # Remove numbering/bullets
            clean_line = line.lstrip("0123456789.-•  ")
            if clean_line:
                recommendations.append(clean_line)

    # If no numbered lists found, provide general recommendations
    if not recommendations:
        recommendations = [
            "Maintain regular health check-ups for all family members",
            "Keep medical records organized and up-to-date",
            "Monitor chronic conditions as prescribed",
            "Promote healthy lifestyle habits across the family"
        ]

    return recommendations[:5]  # Limit to top 5


def _assess_family_risks(family_members: List[FamilyMember]) -> Dict[str, Any]:
    """Assess health risks based on family data"""
    all_conditions = set(
        disease.lower()
        for member in family_members
        if member.chronic_diseases
        for disease in member.chronic_diseases
    )

    # Simple risk assessment
    risk_factors = []
    risk_level = "low"

    high_risk_conditions = ["diabetes", "heart disease", "cancer", "stroke", "hypertension"]
    medium_risk_conditions = ["asthma", "arthritis", "allergies", "obesity"]

    for condition in high_risk_conditions:
        if any(condition in c for c in all_conditions):
            risk_factors.append(condition.title())
            risk_level = "high"

    if risk_level == "low":
        for condition in medium_risk_conditions:
            if any(condition in c for c in all_conditions):
                risk_factors.append(condition.title())
                risk_level = "medium"

    return {
        "risk_level": risk_level,
        "risk_factors": risk_factors,
        "recommendation": "Regular monitoring and preventive care recommended" if risk_level != "low" else "Maintain healthy lifestyle"
    }
