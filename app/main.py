from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.supabase_jwt import verify_jwt_token
from app.auth.supabase_jwt import get_current_user_id  
from app.api import auth, user, seller, alerts, saved_products, summary

app = FastAPI()

# Middleware
app.middleware("http")(verify_jwt_token)  # Validates Supabase JWT for all requests

# CORS settings (adjust if frontend is hosted elsewhere)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or ["https://yourfrontend.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route groups
app.include_router(auth.router, prefix="/auth")
app.include_router(user.router, prefix="/user")
app.include_router(seller.router, prefix="/seller")
app.include_router(alerts.router, prefix="/alerts")
app.include_router(saved_products.router, prefix="/saved")
app.include_router(summary.router, prefix="/summary")

@app.get("/")
def root():
    return {"message": "Amazon Seller Tracker API running"}
