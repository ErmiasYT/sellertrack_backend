from app.db.supabase import get_supabase_client
from datetime import datetime
from typing import List, Dict

def upsert_products(products: List[Dict]):
    """
    Upserts product metadata into the 'products' table.
    Each product is expected to have: asin, title, brand, buybox_price, seller_count
    """
    supabase = get_supabase_client()
    now = datetime.utcnow().isoformat()

    for product in products:
        asin = product["asin"]

        # Add last_updated timestamp
        product["last_updated"] = now

        # Upsert (insert or update if exists)
        supabase.table("products").upsert(product, on_conflict=["asin"]).execute()

def product_exists(asin: str) -> bool:
    """
    Checks if the given ASIN already exists in the global products table.
    """
    supabase = get_supabase_client()
    response = supabase.table("products").select("asin").eq("asin", asin).execute()
    return bool(response.data)
