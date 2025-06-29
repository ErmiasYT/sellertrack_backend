from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.auth.supabase_jwt import verify_jwt_token   # your JWT middleware
from app.config import settings
from app.api import auth, user, seller, alerts, saved_products, summary

app = FastAPI()


# ── CORS FIRST ──────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,      # e.g. ["https://seller-spotlight-alerts.vercel.app"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── JWT / other middleware AFTER CORS ───────────────────────────────────
app.middleware("http")(verify_jwt_token)
# ────────────────────────────────────────────────────────────────────────

# Route groups (router files have no global dependencies)
app.include_router(auth.router,          prefix="/api/auth")
app.include_router(user.router,          prefix="/api/user")
app.include_router(seller.router,        prefix="/api")            # /api/track-seller
app.include_router(alerts.router,        prefix="/api/alerts")
app.include_router(saved_products.router, prefix="/api/saved")
app.include_router(summary.router,       prefix="/api/summary")

# Simple root check
@app.get("/")
def root():
    return {"message": "Amazon Seller Tracker API running"}
