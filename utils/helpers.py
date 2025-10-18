"""
Utility functions for the mySahara backend.
"""

from supabase import create_client, Client
from config import settings
import base64
from typing import Any, Dict
import re

_supabase_client: Client | None = None

def get_supabase_client() -> Client | None:
    """
    Returns a singleton instance of the Supabase client.
    """
    global _supabase_client
    if _supabase_client is None:
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            # Return None when Supabase is not configured; callers should handle gracefully
            return None
        _supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    return _supabase_client


def validate_base64_image(data: str) -> bool:
    """
    Validate a base64-encoded image string. Returns True if decodable.

    Accepts optional data URL prefix and strips it before decoding.
    """
    try:
        if not data:
            return False
        # Strip data URL prefix if present
        if "," in data and data.strip().startswith("data:"):
            data = data.split(",", 1)[1]
        # Validate by decoding
        base64.b64decode(data, validate=True)
        return True
    except Exception:
        return False


def create_response(success: bool, **kwargs: Any) -> Dict[str, Any]:
    """
    Create a standard JSON response dict.
    """
    payload: Dict[str, Any] = {"success": success}
    payload.update(kwargs)
    return payload


def detect_language(text: str) -> str:
    """
    Very lightweight language detector between English and Bangla.
    Returns 'bn' if Bengali characters are detected, otherwise 'en'.
    """
    if not text:
        return 'en'
    bengali_pattern = re.compile(r"[\u0980-\u09FF]")
    return 'bn' if bengali_pattern.search(text) else 'en'