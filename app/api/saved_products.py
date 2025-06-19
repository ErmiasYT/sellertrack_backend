from fastapi import APIRouter, Depends
from db.supabase import get_supabase_client
from auth.supabase_jwt import get_current_user_id
from models.schemas import SavedProductIn, SavedProductOut
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=list[SavedProductOut])
def get_saved_products(user_id: str = Depends(get_current_user_id)):
    supabase = get_supabase_client()
    response = supabase.table("saved_products").select("*").eq("user_id", user_id).order("saved_at", desc=True).execute()
    return response.data or []

@router.post("/")
def save_product(payload: SavedProductIn, user_id: str = Depends(get_current_user_id)):
    supabase = get_supabase_client()
    result = supabase.table("saved_products").insert({
        "user_id": user_id,
        "asin": payload.asin,
        "note": payload.note,
        "saved_at": datetime.utcnow().isoformat()
    }).execute()
    return {"status": "success", "id": result.data[0]["id"]}

@router.delete("/{asin}")
def delete_saved_product(asin: str, user_id: str = Depends(get_current_user_id)):
    supabase = get_supabase_client()
    supabase.table("saved_products").delete().eq("user_id", user_id).eq("asin", asin).execute()
    return {"status": "deleted", "asin": asin}