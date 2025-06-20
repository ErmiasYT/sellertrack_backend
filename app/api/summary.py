from fastapi import APIRouter, Depends
from app.db.supabase import get_supabase_client
from app.auth.supabase_jwt import get_current_user_id
from app.models.schemas import UserSummary
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/", response_model=UserSummary)
def get_user_summary(user_id: str = Depends(get_current_user_id)):
    supabase = get_supabase_client()

    # Tracked sellers count
    sellers_count = supabase.table("tracked_sellers").select("id").eq("user_id", user_id).execute()
    tracked_count = len(sellers_count.data or [])

    # Saved products count
    saved_count = supabase.table("saved_products").select("id").eq("user_id", user_id).execute()
    saved = len(saved_count.data or [])

    # New alerts today
    start_of_day = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    new_alerts = supabase.table("alerts").select("id").eq("user_id", user_id).gte("found_at", start_of_day).execute()
    alerts_today = len(new_alerts.data or [])

    return UserSummary(
        tracked_sellers=tracked_count,
        saved_products=saved,
        new_products_today=alerts_today
    )
