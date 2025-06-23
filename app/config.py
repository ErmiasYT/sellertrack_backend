import os
from dotenv import load_dotenv

load_dotenv()  # Load from .env file at root (if present)

class Settings:
    KEEPPA_API_KEY: str = os.getenv("KEEPPA_API_KEY")
    SUPABASE_URL: str = os.getenv("SUPABASE_URL")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "")  # Optional override if needed

    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    DAILY_TOKEN_LIMIT: int = int(os.getenv("DAILY_TOKEN_LIMIT", "1440"))
    TOKENS_PER_SELLER_SCAN: int = int(os.getenv("TOKENS_PER_SELLER_SCAN", "50"))

    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

settings = Settings()
