from fastapi import APIRouter, Depends, HTTPException
from app.db.supabase import get_supabase_client
from app.auth.supabase_jwt import get_current_user_id
from app.models.schemas import TrackSellerIn
from datetime import datetime
import uuid

router = APIRouter(
    prefix="/seller",
    tags=["seller"],
    dependencies=[Security(verify_jwt_token)],  # ○ apply to all endpoints in this router
)

@router.get("/", summary="Get user's tracked sellers")
def get_tracked_sellers(user_id: str = Depends(get_current_user_id)):
    supabase = get_supabase_client()

    result = supabase.table("tracked_sellers").select("*,sellers(*)").eq("user_id", user_id).execute()
    data = result.data or []

    # Flatten to return combined seller data
    return [{
        "seller_id": item["seller_id"],
        "seller_name": item["sellers"]["seller_name"],
        "product_count": len(item["sellers"]["asin_snapshot"]),
        "last_checked": item["sellers"]["last_checked"]
    } for item in data]

@router.post("/track", summary="Track a new seller")
def track_seller(payload: TrackSellerIn, user_id: str = Depends(get_current_user_id)):
    supabase = get_supabase_client()
    seller_id = payload.seller_id

    # Check if seller exists globally
    existing = supabase.table("sellers").select("*").eq("seller_id", seller_id).execute().data
    if not existing:
        # Create new global seller entry with empty ASIN snapshot
        supabase.table("sellers").insert({
            "id": str(uuid.uuid4()),
            "seller_id": seller_id,
            "seller_name": payload.seller_name,
            "asin_snapshot": [],
            "last_checked": None
        }).execute()

    # Link this user to the seller
    supabase.table("tracked_sellers").insert({
        "user_id": user_id,
        "seller_id": seller_id,
        "created_at": datetime.utcnow().isoformat()
    }).execute()

    # Add to queue
    supabase.table("queue").insert({
        "seller_id": seller_id,
        "scheduled_at": datetime.utcnow().isoformat(),
        "retry_count": 0,
        "status": "queued"
    }).execute()

    return {"status": "tracking", "seller_id": seller_id}

@router.delete("/{seller_id}", summary="Untrack a seller")
def untrack_seller(seller_id: str, user_id: str = Depends(get_current_user_id)):
    supabase = get_supabase_client()

    # Remove link
    supabase.table("tracked_sellers").delete().eq("user_id", user_id).eq("seller_id", seller_id).execute()

    # Check if other users still tracking
    remaining = supabase.table("tracked_sellers").select("*").eq("seller_id", seller_id).execute().data
    if not remaining:
        # Remove seller + queue entry if nobody else tracking
        supabase.table("sellers").delete().eq("seller_id", seller_id).execute()
        supabase.table("queue").delete().eq("seller_id", seller_id).execute()

    return {"status": "untracked", "seller_id": seller_id}
