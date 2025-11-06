"""
Supabase Client Service
Provides a singleton Supabase client for database operations
"""
import os
from supabase import create_client, Client
from loguru import logger

_supabase_client: Client = None


def get_supabase_client() -> Client:
    """
    Get or create Supabase client instance

    Returns:
        Client: Supabase client instance

    Raises:
        ValueError: If Supabase credentials are not configured
    """
    global _supabase_client

    if _supabase_client is not None:
        return _supabase_client

    # Get credentials from environment
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_ANON_KEY")

    if not supabase_url or not supabase_key:
        error_msg = "Supabase credentials not configured. Set SUPABASE_URL and SUPABASE_KEY in .env"
        logger.error(error_msg)
        raise ValueError(error_msg)

    # Create client
    _supabase_client = create_client(supabase_url, supabase_key)
    logger.info("Supabase client initialized successfully")

    return _supabase_client


def reset_supabase_client():
    """
    Reset the Supabase client (useful for testing)
    """
    global _supabase_client
    _supabase_client = None
