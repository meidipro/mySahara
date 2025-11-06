"""
mySahara Health Application - FastAPI Backend
Main application entry point with CORS middleware and route configuration.
"""

import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from loguru import logger

# Load environment variables from parent directory
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)
logger.add(
    "logs/backend.log",
    rotation="500 MB",
    retention="10 days",
    level="DEBUG"
)

# Import API routes
from api import ocr, ai_chat, health, nutrition_fitness, logs, progress, family_insights, notifications

# Initialize FastAPI app
app = FastAPI(
    title="mySahara Health API",
    description="Backend API for mySahara health application with OCR, AI chat, and health analysis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware configuration for Flutter web
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:5000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:5000",
        "*"  # Allow all origins for development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(ocr.router, prefix="/api/ocr", tags=["OCR"])
app.include_router(ai_chat.router, prefix="/api/ai", tags=["AI Chat"])
app.include_router(health.router, prefix="/api/health", tags=["Health Analysis"])
app.include_router(nutrition_fitness.router, prefix="/api/nutrition-fitness", tags=["AI Nutrition & Fitness"])
app.include_router(family_insights.router, prefix="/api/family", tags=["Family Health Insights"])
app.include_router(logs.router, prefix="/api/logs", tags=["Logging"])
app.include_router(progress.router, prefix="/api/progress", tags=["Progress"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])


@app.get("/")
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": "Welcome to mySahara Health API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify API is running.

    Returns:
        dict: Health status and environment information
    """
    try:
        # Check environment variables
        env_vars_status = {
            "GROQ_API_KEY": bool(os.getenv("GROQ_API_KEY")),
            "GEMINI_API_KEY": bool(os.getenv("GEMINI_API_KEY")),
            "GOOGLE_APPLICATION_CREDENTIALS": bool(os.getenv("GOOGLE_APPLICATION_CREDENTIALS")),
            "SUPABASE_URL": bool(os.getenv("SUPABASE_URL")),
            "SUPABASE_ANON_KEY": bool(os.getenv("SUPABASE_ANON_KEY"))
        }

        return {
            "status": "healthy",
            "message": "mySahara Health API is running",
            "environment_variables": env_vars_status,
            "endpoints": {
                "ocr": "/api/ocr",
                "ai_chat": "/api/ai",
                "health_analysis": "/api/health"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unavailable")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors.

    Args:
        request: The request that caused the error
        exc: The exception that was raised

    Returns:
        JSONResponse: Error response with details
    """
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "type": type(exc).__name__
        }
    )


@app.on_event("startup")
async def startup_event():
    """
    Startup event - Initialize scheduler for automated notifications
    """
    try:
        from services.scheduler_service import initialize_scheduler
        await initialize_scheduler()
        logger.info("Scheduler initialized successfully")
    except Exception as e:
        logger.warning(f"Scheduler initialization failed (non-critical): {e}")


if __name__ == "__main__":
    import uvicorn

    # Get port from environment or use default
    port = int(os.getenv("PORT", 8000))

    logger.info(f"Starting mySahara Health API on port {port}")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
