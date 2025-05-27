from fastapi import Depends
from typing import Annotated
import os
from supabase import create_client, Client
from app.logging import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Supabase credentials - fallback to local development settings if not in env
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

logger.info(f"Initializing Supabase client with URL: {supabase_url}")

def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    logger.info("Creating Supabase client")
    return create_client(supabase_url, supabase_key)

# Create FastAPI dependency
SupabaseDep = Annotated[Client, Depends(get_supabase_client)]
