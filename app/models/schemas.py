from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# 📦 For POST /saved (save product)
class SavedProductIn(BaseModel):
    asin: str
    note: Optional[str] = None

# 📦 For GET /saved (saved product list)
class SavedProductOut(BaseModel):
    id: int
    asin: str
    note: Optional[str]
    saved_at: datetime

# 🧾 For POST /seller/track
class TrackSellerIn(BaseModel):
    seller_id: str
    seller_name: str

# 📊 For GET /summary
class UserSummary(BaseModel):
    tracked_sellers: int
    saved_products: int
    new_products_today: int

# 🙋 For GET /user/me
class UserInfo(BaseModel):
    email: str
    plan_tier: str
    max_sellers: int
    current_count: int  # ← removed the comma here

class AlertOut(BaseModel):
    asin: str
    product_title: Optional[str]
    brand: Optional[str]
    buybox_price: Optional[float]
    seller_count: Optional[int]
    found_at: datetime
    seller_name: Optional[str]
    seller_id: str
    product_url: str
    seller_url: str
    is_new: bool
