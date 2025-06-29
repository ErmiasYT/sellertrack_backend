
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.auth.supabase_jwt import verify_jwt_token   # your JWT middleware
from app.config import settings
from app.api import auth, user, seller, alerts, saved_products, summary


# 2) Log the secret on startup
logging.debug(f"[STARTUP] JWT_SECRET={settings.JWT_SECRET!r}")

app = FastAPI()


# ── CORS FIRST ──────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,      # e.g. ["https://seller-spotlight-alerts.vercel.app"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 4) JWT layer via add_middleware
class JWTMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # allow preflight through
        if request.method == "OPTIONS":
            return await call_next(request)

        # perform your JWT verification
        return await verify_jwt_token(request, call_next)

app.add_middleware(JWTMiddleware)


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
