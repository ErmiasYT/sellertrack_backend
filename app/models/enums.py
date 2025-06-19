from enum import Enum

# 🔐 Plan levels
class PlanTier(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"

# 🕒 Queue statuses
class QueueStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    ERROR = "error"
    DONE = "done"

# 🧮 Token usage categories (optional for tracking/debugging)
class TokenEvent(str, Enum):
    SELLER_SCAN = "seller_scan"
    PRODUCT_LOOKUP = "product_lookup"
    MANUAL_REFRESH = "manual_refresh"