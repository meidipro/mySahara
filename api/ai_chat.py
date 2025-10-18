"""
AI Chat API endpoints for conversational health assistant.
"""

import time
from fastapi import APIRouter, HTTPException
from typing import List, Dict
from loguru import logger

from models.requests import ChatRequest
from models.responses import ChatResponse
from services.ai_service import AIService
from utils.helpers import detect_language

router = APIRouter()
ai_service = AIService()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send message to AI health assistant and get response.

    Args:
        request: ChatRequest with message and conversation history

    Returns:
        ChatResponse with AI response and metadata

    Raises:
        HTTPException: If chat processing fails
    """
    start_time = time.time()

    try:
        logger.info(f"Processing chat request - Language: {request.language}")

        # Auto-detect language if needed
        language = request.language
        if language == "auto" or not language:
            language = detect_language(request.message)
            logger.info(f"Detected language: {language}")

        # Prepare conversation history
        conversation_history = request.conversation_history or []

        # Add context if provided
        context = request.context

        # Call AI service
        result = await ai_service.chat(
            message=request.message,
            language=language,
            conversation_history=conversation_history,
            use_medical_mode=request.use_medical_mode,
            context=context
        )

        processing_time = time.time() - start_time

        if result["success"]:
            # Generate follow-up suggestions
            suggestions = _generate_suggestions(request.message, language)

            return ChatResponse(
                success=True,
                message=result.get("message"),
                language=result.get("language", language),
                model_used=result.get("model_used"),
                confidence=0.9,  # Could be calculated based on response quality
                suggestions=suggestions,
                processing_time=processing_time
            )
        else:
            return ChatResponse(
                success=False,
                error=result.get("error", "Chat processing failed"),
                processing_time=processing_time
            )

    except Exception as e:
        logger.error(f"Chat processing error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Chat processing failed: {str(e)}"
        )


@router.post("/chat-stream")
async def chat_stream(request: ChatRequest):
    """
    Stream AI chat response (for future implementation).

    Args:
        request: ChatRequest with message

    Returns:
        Streaming response
    """
    raise HTTPException(
        status_code=501,
        detail="Streaming not yet implemented"
    )


@router.post("/translate")
async def translate_message(
    message: str,
    source_language: str = "en",
    target_language: str = "bn"
):
    """
    Translate message between English and Bangla.

    Args:
        message: Message to translate
        source_language: Source language code
        target_language: Target language code

    Returns:
        Translated message
    """
    try:
        logger.info(f"Translating from {source_language} to {target_language}")

        # Use AI service for translation
        prompt = f"Translate the following {source_language} text to {target_language}. Only provide the translation, nothing else:\n\n{message}"

        result = await ai_service.chat(
            message=prompt,
            language=target_language,
            use_medical_mode=False
        )

        if result["success"]:
            return {
                "success": True,
                "original": message,
                "translated": result["message"],
                "source_language": source_language,
                "target_language": target_language
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Translation failed")
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Translation failed: {str(e)}"
        )


@router.post("/explain-medical-term")
async def explain_medical_term(
    term: str,
    language: str = "en",
    simple_explanation: bool = True
):
    """
    Explain medical terminology in simple language.

    Args:
        term: Medical term to explain
        language: Language for explanation
        simple_explanation: Whether to use simple language

    Returns:
        Explanation of the medical term
    """
    try:
        logger.info(f"Explaining medical term: {term}")

        # Build prompt
        if simple_explanation:
            prompt = f"Explain the medical term '{term}' in simple, easy-to-understand language that a non-medical person can understand."
        else:
            prompt = f"Explain the medical term '{term}' in detail."

        # Get explanation
        result = await ai_service.chat(
            message=prompt,
            language=language,
            use_medical_mode=True
        )

        if result["success"]:
            return {
                "success": True,
                "term": term,
                "explanation": result["message"],
                "language": language
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Explanation failed")
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Medical term explanation error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Explanation failed: {str(e)}"
        )


@router.get("/conversation-starters")
async def get_conversation_starters(language: str = "en"):
    """
    Get conversation starter suggestions.

    Args:
        language: Language code

    Returns:
        List of conversation starters
    """
    if language == "bn":
        starters = [
            "আমার স্বাস্থ্য সম্পর্কে কিছু জানতে চাই",
            "ডায়াবেটিস সম্পর্কে জানতে চাই",
            "কীভাবে সুস্থ থাকব?",
            "মাথাব্যথার কারণ কী হতে পারে?",
            "উচ্চ রক্তচাপ কীভাবে নিয়ন্ত্রণ করব?"
        ]
    else:
        starters = [
            "What are the symptoms of diabetes?",
            "How can I improve my health?",
            "Tell me about high blood pressure",
            "What causes headaches?",
            "How to maintain a healthy diet?"
        ]

    return {
        "success": True,
        "language": language,
        "starters": starters
    }


def _generate_suggestions(message: str, language: str) -> List[str]:
    """
    Generate follow-up suggestions based on the message.

    Args:
        message: User message
        language: Language code

    Returns:
        List of suggestion strings
    """
    # This is a simple implementation
    # Could be enhanced with AI-generated suggestions

    if language == "bn":
        default_suggestions = [
            "আরও বিস্তারিত জানতে চান?",
            "অন্য কিছু জানতে চান?"
        ]
    else:
        default_suggestions = [
            "Would you like more details?",
            "Do you have any other questions?"
        ]

    # Check for specific keywords to provide context-aware suggestions
    message_lower = message.lower()

    if language == "en":
        if "diabetes" in message_lower:
            return [
                "Tell me about diabetes prevention",
                "What are diabetes management tips?",
                "Explain diabetes complications"
            ]
        elif "blood pressure" in message_lower or "hypertension" in message_lower:
            return [
                "How to lower blood pressure naturally?",
                "What foods help with blood pressure?",
                "Explain blood pressure readings"
            ]
        elif "symptom" in message_lower:
            return [
                "Should I see a doctor?",
                "What are the treatment options?",
                "Are there home remedies?"
            ]
    else:  # Bangla
        if "ডায়াবেটিস" in message or "diabetes" in message_lower:
            return [
                "ডায়াবেটিস প্রতিরোধ সম্পর্কে জানুন",
                "ডায়াবেটিস নিয়ন্ত্রণের উপায়",
                "ডায়াবেটিসের জটিলতা"
            ]

    return default_suggestions
