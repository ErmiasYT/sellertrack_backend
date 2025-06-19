import keepa
from config import settings
from typing import List, Dict, Optional

# Initialize Keepa client
keepa_api = keepa.Keepa(settings.KEEPPA_API_KEY)

def fetch_seller_asins(seller_id: str) -> List[str]:
    """
    Gets all ASINs currently listed by the seller using Keepa partial paging.
    """
    try:
        response = keepa_api.query(
            seller_id=seller_id,
            domain='US',
            product_code='SELLER',
            history=False,
            update=True,
            buybox=False,
            stats=False,
            offers=False,
            rating=False,
            page=0
        )

        asins = []
        while response:
            current_page_asins = [p["asin"] for p in response["products"]]
            asins.extend(current_page_asins)

            if response.get("nextPageToken"):
                response = keepa_api.query(
                    seller_id=seller_id,
                    domain='US',
                    product_code='SELLER',
                    history=False,
                    update=True,
                    buybox=False,
                    stats=False,
                    offers=False,
                    rating=False,
                    pageToken=response["nextPageToken"]
                )
            else:
                break

        return list(set(asins))  # Deduplicate

    except Exception as e:
        print(f"Error fetching ASINs for seller {seller_id}: {e}")
        return []

def fetch_product_details(asin_list: List[str]) -> List[Dict]:
    """
    Fetches product metadata (title, brand, price, seller count) for given ASINs.
    """
    try:
        response = keepa_api.query(asin_list, domain='US')
        products = []

        for p in response["products"]:
            title = p.get("title")
            brand = p.get("brand")
            buybox_price = (
                p["buyBoxPriceHistory"][-1] / 100 if p.get("buyBoxPriceHistory") else None
            )
            seller_count = (
                p["sellerCountHistory"][-1] if p.get("sellerCountHistory") else None
            )

            products.append({
                "asin": p["asin"],
                "title": title,
                "brand": brand,
                "buybox_price": buybox_price,
                "seller_count": seller_count,
            })

        return products

    except Exception as e:
        print(f"Error fetching product details: {e}")
        return []