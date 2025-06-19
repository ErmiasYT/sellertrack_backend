from fastapi import APIRouter, Depends
from db.supabase import get_supabase_client
from auth.supabase_jwt import get_current_user_id
from models.schemas import AlertOut

router = APIRouter()

@router.get("/", response_model=list[AlertOut])
def get_user_alerts(user_id: str = Depends(get_current_user_id)):
    supabase = get_supabase_client()

    # Fetch alerts for user
    alerts_response = supabase.table("alerts").select("*").eq("user_id", user_id).order("found_at", desc=True).execute()
    alerts = alerts_response.data if alerts_response.data else []

    # Join alerts with product metadata
    product_asins = [alert["asin"] for alert in alerts]
    products_response = supabase.table("products").select("*").in_("asin", product_asins).execute()
    product_map = {p["asin"]: p for p in products_response.data} if products_response.data else {}

    enriched_alerts = []
    for alert in alerts:
        asin = alert["asin"]
        product = product_map.get(asin, {})
        enriched_alerts.append({
            "asin": asin,
            "product_title": product.get("title"),
            "brand": product.get("brand"),
            "buybox_price": product.get("buybox_price"),
            "seller_count": product.get("seller_count"),
            "found_at": alert["found_at"],
            "seller_name": alert.get("seller_name"),
            "seller_id": alert["seller_id"],
            "product_url": f"https://www.amazon.com/dp/{asin}",
            "seller_url": f"https://www.amazon.com/sp?seller={alert['seller_id']}",
            "is_new": alert.get("is_new", True),
        })

    return enriched_alerts