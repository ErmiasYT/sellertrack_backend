from services.keepa_service import fetch_seller_asins, fetch_product_details
from services.product_service import upsert_products, product_exists
from services.alert_service import create_alerts_for_users
from db.supabase import get_supabase_client
from datetime import datetime

def scan_seller_and_detect_new_asins(seller_id: str):
    supabase = get_supabase_client()

    # Get current ASINs from Keepa
    new_asins = fetch_seller_asins(seller_id)

    if not new_asins:
        print(f"No ASINs found for seller {seller_id}")
        return

    # Get existing snapshot
    seller_row = supabase.table("sellers").select("*").eq("seller_id", seller_id).single().execute().data
    if not seller_row:
        print(f"Seller {seller_id} not found in DB.")
        return

    old_snapshot = seller_row.get("asin_snapshot", [])
    seller_name = seller_row.get("seller_name")

    # Diff ASINs
    new_only = list(set(new_asins) - set(old_snapshot))
    print(f"{len(new_only)} new ASINs found for seller {seller_id}")

    # Update seller asin_snapshot + last_checked
    supabase.table("sellers").update({
        "asin_snapshot": new_asins,
        "last_checked": datetime.utcnow().isoformat()
    }).eq("seller_id", seller_id).execute()

    if not new_only:
        return

    # Fetch product details
    product_data = fetch_product_details(new_only)
    upsert_products(product_data)

    # Get all users tracking this seller
    trackers = supabase.table("tracked_sellers").select("user_id").eq("seller_id", seller_id).execute()
    user_ids = [t["user_id"] for t in trackers.data or []]

    # Fire alerts
    for product in product_data:
        create_alerts_for_users(
            asin=product["asin"],
            seller_id=seller_id,
            seller_name=seller_name,
            user_ids=user_ids
        )