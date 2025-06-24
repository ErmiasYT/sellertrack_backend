import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings  # ✅ NEW import
from typing import List

load_dotenv()

class Settings(BaseSettings):
    KEEPPA_API_KEY: str
    SUPABASE_URL: str
    SUPABASE_KEY: str
    JWT_SECRET: str = ""
    REDIS_URL: str = "redis://localhost:6379/0"
    DAILY_TOKEN_LIMIT: int = 1440
    TOKENS_PER_SELLER_SCAN: int = 50
    CORS_ORIGINS: List[str] = ["*"]

    class Config:
        env_file = ".env"

settings = Settings()
