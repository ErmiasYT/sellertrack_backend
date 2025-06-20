from fastapi import APIRouter, Depends
from app.db.supabase import get_supabase_client
from app.auth.supabase_jwt import get_current_user_id
from app.models.schemas import UserInfo

router = APIRouter()

@router.get("/me", response_model=UserInfo)
def get_user_info(user_id: str = Depends(get_current_user_id)):
    supabase = get_supabase_client()

    # Fetch user record
    user = supabase.table("users").select("*").eq("id", user_id).single().execute().data or {}

    # Fetch plan limits
    limits = supabase.table("user_limits").select("*").eq("user_id", user_id).single().execute().data or {}

    return UserInfo(
        email=user.get("email", "unknown"),
        plan_tier=limits.get("plan_tier", "free"),
        max_sellers=limits.get("max_sellers", 5),
        current_count=limits.get("current_count", 0)
    )
