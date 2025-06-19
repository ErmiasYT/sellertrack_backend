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