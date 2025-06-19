from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

# 📄 users
class User(BaseModel):
    id: str
    email: str
    created_at: datetime

# 📄 user_limits
class UserLimit(BaseModel):
    user_id: str
    plan_tier: str
    max_sellers: int
    current_count: int

# 📄 sellers
class Seller(BaseModel):
    id: str
    seller_id: str
    seller_name: str
    asin_snapshot: List[str]
    last_checked: Optional[datetime]

# 📄 tracked_sellers
class TrackedSeller(BaseModel):
    id: int
    user_id: str
    seller_id: str
    created_at: datetime

# 📄 products
class Product(BaseModel):
    asin: str
    title: Optional[str]
    brand: Optional[str]
    buybox_price: Optional[float]
    seller_count: Optional[int]
    last_updated: Optional[datetime]

# 📄 alerts
class Alert(BaseModel):
    id: int
    user_id: str
    seller_id: str
    asin: str
    found_at: datetime
    is_new: bool

# 📄 saved_products
class SavedProduct(BaseModel):
    id: int
    user_id: str
    asin: str
    note: Optional[str]
    saved_at: datetime

# 📄 token_status
class TokenStatus(BaseModel):
    id: int
    token_remaining: int
    tokens_used_last_24h: int
    last_updated: datetime

# 📄 queue
class QueueEntry(BaseModel):
    id: int
    seller_id: str
    scheduled_at: datetime
    retry_count: int
    next_attempt_at: Optional[datetime]
    status: str  # e.g. "queued", "error", "processing"