from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.auth.supabase_jwt import verify_jwt_token
from app.auth.supabase_jwt import get_current_user_id  
from app.api import auth, user, seller, alerts, saved_products, summary
from app.config import settings

# Debug: Print the actual CORS origins being used
print(">>> DEBUG CORS_ORIGINS =", settings.CORS_ORIGINS)
print(">>> DEBUG CORS_ORIGINS type =", type(settings.CORS_ORIGINS))

app = FastAPI()

# CORS settings using the config - apply FIRST
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# JWT middleware applied AFTER CORS
app.middleware("http")(verify_jwt_token)

# Register route groups
app.include_router(auth.router, prefix="/api/auth")
app.include_router(user.router, prefix="/api/user")
app.include_router(seller.router, prefix="/api")  # This creates /api/track-seller
app.include_router(alerts.router, prefix="/api/alerts")
app.include_router(saved_products.router, prefix="/api/saved")  # ✅ good short route
app.include_router(summary.router, prefix="/api/summary")

@app.get("/")
def root():
    return {"message": "Amazon Seller Tracker API running"}

@app.get("/debug/routes")
def debug_routes():
    """Debug endpoint to see all registered routes"""
    routes = []
    for route in app.routes:
        if hasattr(route, 'path'):
            routes.append({
                "path": route.path,
                "methods": getattr(route, 'methods', []),
                "name": getattr(route, 'name', 'Unknown')
            })
    return {"routes": routes}

@app.post("/api/track-seller")
def direct_track_seller():
    """Direct route for track-seller to test if router is the issue"""
    return {"message": "Direct track-seller endpoint works", "status": "success"}

@app.post("/api/test-track-seller")
def test_track_seller():
    """Test endpoint to verify routing"""
    return {"message": "Test track-seller endpoint works", "status": "success"}

@app.options("/{full_path:path}")
async def options_handler(request):
    """Handle OPTIONS requests explicitly"""
    return {"message": "OK"}
