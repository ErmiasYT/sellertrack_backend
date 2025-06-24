from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.auth.supabase_jwt import verify_jwt_token
from app.auth.supabase_jwt import get_current_user_id  
from app.api import auth, user, seller, alerts, saved_products, summary
from app.config import settings
print(">>> DEBUG CORS_ORIGINS =", settings.CORS_ORIGINS)


app = FastAPI()

# CORS settings (adjust if frontend is hosted elsewhere)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.middleware("http")(verify_jwt_token)  # Validates Supabase JWT for all requests

# Register route groups
app.include_router(auth.router, prefix="/api/auth")
app.include_router(user.router, prefix="/api/user")
app.include_router(seller.router, prefix="/api")  # ✅ to allow /api/track-seller
app.include_router(alerts.router, prefix="/api/alerts")
app.include_router(saved_products.router, prefix="/api/saved")  # ✅ good short route
app.include_router(summary.router, prefix="/api/summary")

@app.get("/")
def root():
    return {"message": "Amazon Seller Tracker API running"}
