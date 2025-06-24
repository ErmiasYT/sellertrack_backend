from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
import uuid

from app.db.supabase import get_supabase_client
from app.auth.supabase_jwt import get_current_user_id
from app.models.schemas import TrackSellerIn

router = APIRouter(prefix="", tags=["seller"])     # ← no global deps

# ------------------------------------------------------------------------
@router.get("/", summary="Get user's tracked sellers")
def get_tracked_sellers(user_id: str = Depends(get_current_user_id)):
    supabase = get_supabase_client()
    result = (
        supabase.table("tracked_sellers")
        .select("*,sellers(*)")
        .eq("user_id", user_id)
        .execute()
        .data
        or []
    )
    return [
        {
            "seller_id": item["seller_id"],
            "seller_name": item["sellers"]["seller_name"],
            "product_count": len(item["sellers"]["asin_snapshot"]),
            "last_checked": item["sellers"]["last_checked"],
        }
        for item in result
    ]

# ------------------------------------------------------------------------
@router.post("/track-seller", summary="Track a new seller")
def track_seller(
    payload: TrackSellerIn,
    user_id: str = Depends(get_current_user_id),
):
    supabase = get_supabase_client()
    seller_id = payload.seller_id

    # create seller globally if it doesn’t exist
    if not supabase.table("sellers").select("*").eq("seller_id", seller_id).execute().data:
        supabase.table("sellers").insert(
            {
                "id": str(uuid.uuid4()),
                "seller_id": seller_id,
                "seller_name": payload.seller_name,
                "asin_snapshot": [],
                "last_checked": None,
            }
        ).execute()

    # link user → seller (ignore duplicates)
    supabase.table("tracked_sellers").upsert(
        {
            "user_id": user_id,
            "seller_id": seller_id,
            "created_at": datetime.utcnow().isoformat(),
        }
    ).execute()

    # enqueue for scanning
    supabase.table("queue").insert(
        {
            "seller_id": seller_id,
            "scheduled_at": datetime.utcnow().isoformat(),
            "retry_count": 0,
            "status": "queued",
        }
    ).execute()

    return {"status": "tracking", "seller_id": seller_id}

# ------------------------------------------------------------------------
@router.delete("/{seller_id}", summary="Untrack a seller")
def untrack_seller(
    seller_id: str,
    user_id: str = Depends(get_current_user_id),
):
    supabase = get_supabase_client()

    # unlink user
    supabase.table("tracked_sellers").delete().eq("user_id", user_id).eq("seller_id", seller_id).execute()

    # if nobody else tracking, remove seller + queue entry
    remaining = (
        supabase.table("tracked_sellers")
        .select("*")
        .eq("seller_id", seller_id)
        .execute()
        .data
    )
    if not remaining:
        supabase.table("sellers").delete().eq("seller_id", seller_id).execute()
        supabase.table("queue").delete().eq("seller_id", seller_id).execute()

    return {"status": "untracked", "seller_id": seller_id}
