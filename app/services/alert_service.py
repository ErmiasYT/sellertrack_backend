from db.supabase import get_supabase_client
from datetime import datetime
from typing import List

def create_alerts_for_users(asin: str, seller_id: str, seller_name: str, user_ids: List[str]):
    """
    Creates alert entries for each user tracking the seller who got a new ASIN.
    """
    supabase = get_supabase_client()
    found_at = datetime.utcnow().isoformat()

    for user_id in user_ids:
        supabase.table("alerts").insert({
            "user_id": user_id,
            "seller_id": seller_id,
            "asin": asin,
            "found_at": found_at,
            "is_new": True,
            "seller_name": seller_name,
        }).execute()

def get_alerts_for_user(user_id: str):
    """
    Returns enriched alert objects for a given user (joins with products).
    """
    supabase = get_supabase_client()

    alerts_resp = supabase.table("alerts").select("*").eq("user_id", user_id).order("found_at", desc=True).execute()
    alerts = alerts_resp.data or []

    if not alerts:
        return []

    asins = list({a["asin"] for a in alerts})
    products_resp = supabase.table("products").select("*").in_("asin", asins).execute()
    product_map = {p["asin"]: p for p in products_resp.data or []}

    enriched = []
    for alert in alerts:
        product = product_map.get(alert["asin"], {})
        enriched.append({
            "asin": alert["asin"],
            "product_title": product.get("title"),
            "brand": product.get("brand"),
            "buybox_price": product.get("buybox_price"),
            "seller_count": product.get("seller_count"),
            "found_at": alert["found_at"],
            "seller_name": alert.get("seller_name"),
            "seller_id": alert["seller_id"],
            "product_url": f"https://www.amazon.com/dp/{alert['asin']}",
            "seller_url": f"https://www.amazon.com/sp?seller={alert['seller_id']}",
            "is_new": alert.get("is_new", True),
        })

    return enriched