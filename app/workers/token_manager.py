from db.supabase import get_supabase_client
from datetime import datetime, timedelta
from config import settings
from utils.logger import logger

def update_token_usage(tokens_used: int):
    """
    Adds token usage and updates rolling 24h total + remaining.
    """
    supabase = get_supabase_client()
    now = datetime.utcnow()
    status = supabase.table("token_status").select("*").single().execute().data

    if not status:
        # First time init
        supabase.table("token_status").insert({
            "id": 1,
            "token_remaining": settings.DAILY_TOKEN_LIMIT - tokens_used,
            "tokens_used_last_24h": tokens_used,
            "last_updated": now.isoformat()
        }).execute()
        return

    # Enforce 24h window by resetting each day
    last_updated = datetime.fromisoformat(status["last_updated"])
    if (now - last_updated).total_seconds() > 86400:
        used = tokens_used
    else:
        used = status["tokens_used_last_24h"] + tokens_used

    remaining = max(settings.DAILY_TOKEN_LIMIT - used, 0)

    supabase.table("token_status").update({
        "token_remaining": remaining,
        "tokens_used_last_24h": used,
        "last_updated": now.isoformat()
    }).eq("id", 1).execute()

    logger.info(f"🔋 Tokens used: {used} / {settings.DAILY_TOKEN_LIMIT} — remaining: {remaining}")