"""
Configuration settings for mySahara Health Backend.
Loads settings from environment variables.
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from parent directory
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """

    # Application
    APP_NAME: str = "mySahara Health API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    PORT: int = 8000

    # Security
    SECRET_KEY: Optional[str] = None
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database - Supabase
    SUPABASE_URL: Optional[str] = None
    SUPABASE_ANON_KEY: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None

    # Redis (for caching/celery)
    REDIS_URL: Optional[str] = None
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    # AI Services
    GROQ_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    GOOGLE_CLOUD_VISION_CREDENTIALS: Optional[str] = None

    # API Configuration
    MAX_REQUEST_SIZE: int = 10 * 1024 * 1024  # 10 MB
    RATE_LIMIT_PER_MINUTE: int = 60

    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:5000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:5000",
    ]

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/backend.log"

    # OCR Settings
    OCR_MAX_IMAGE_SIZE: tuple = (1920, 1080)
    OCR_SUPPORTED_FORMATS: list = ["jpg", "jpeg", "png", "pdf"]
    OCR_COMPRESSION_QUALITY: int = 85

    # AI Settings
    AI_DEFAULT_MODEL: str = "llama-3.3-70b-versatile"
    AI_MAX_TOKENS: int = 1024
    AI_TEMPERATURE: float = 0.7
    AI_TIMEOUT: int = 30  # seconds

    # Health Analysis
    EMERGENCY_SYMPTOMS: list = [
        "chest pain",
        "difficulty breathing",
        "severe bleeding",
        "loss of consciousness",
        "seizure",
        "stroke symptoms",
        "severe allergic reaction"
    ]

    class Config:
        env_file = str(env_path)
        case_sensitive = True


# Create global settings instance
settings = Settings()


def get_settings() -> Settings:
    """
    Get application settings.

    Returns:
        Settings instance
    """
    return settings


def validate_settings() -> dict:
    """
    Validate that required settings are configured.

    Returns:
        Dict with validation results
    """
    issues = []
    warnings = []

    # Check critical API keys
    if not settings.GROQ_API_KEY and not settings.GEMINI_API_KEY:
        issues.append("No AI API keys configured (GROQ_API_KEY or GEMINI_API_KEY)")

    if not settings.GOOGLE_APPLICATION_CREDENTIALS:
        warnings.append("Google Cloud Vision credentials not configured")

    if not settings.SUPABASE_URL:
        warnings.append("Supabase URL not configured")

    if not settings.SECRET_KEY:
        warnings.append("SECRET_KEY not configured")

    # Check file paths
    if settings.GOOGLE_APPLICATION_CREDENTIALS:
        if not os.path.exists(settings.GOOGLE_APPLICATION_CREDENTIALS):
            issues.append(f"Google credentials file not found: {settings.GOOGLE_APPLICATION_CREDENTIALS}")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings
    }


def print_settings_summary():
    """
    Print summary of current settings (for debugging).
    """
    print("\n" + "=" * 60)
    print("mySahara Health Backend - Configuration")
    print("=" * 60)

    print(f"\nApplication:")
    print(f"  Name: {settings.APP_NAME}")
    print(f"  Version: {settings.APP_VERSION}")
    print(f"  Port: {settings.PORT}")
    print(f"  Debug: {settings.DEBUG}")

    print(f"\nAI Services:")
    print(f"  Groq API: {'✓ Configured' if settings.GROQ_API_KEY else '✗ Not configured'}")
    print(f"  Gemini API: {'✓ Configured' if settings.GEMINI_API_KEY else '✗ Not configured'}")
    print(f"  Google Cloud Vision: {'✓ Configured' if settings.GOOGLE_APPLICATION_CREDENTIALS else '✗ Not configured'}")

    print(f"\nDatabase:")
    print(f"  Supabase: {'✓ Configured' if settings.SUPABASE_URL else '✗ Not configured'}")

    print(f"\nCache:")
    print(f"  Redis: {'✓ Configured' if settings.REDIS_URL else '✗ Not configured'}")

    # Validate
    validation = validate_settings()

    if validation["issues"]:
        print(f"\n⚠️  Issues:")
        for issue in validation["issues"]:
            print(f"  - {issue}")

    if validation["warnings"]:
        print(f"\n⚠️  Warnings:")
        for warning in validation["warnings"]:
            print(f"  - {warning}")

    if validation["valid"] and not validation["warnings"]:
        print(f"\n✓ Configuration is valid")

    print("=" * 60 + "\n")


if __name__ == "__main__":
    # Print settings when run directly
    print_settings_summary()
