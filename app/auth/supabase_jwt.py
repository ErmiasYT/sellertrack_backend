# app/auth/supabase_jwt.py
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer
from jose import jwt, JWTError
from app.config import settings

# This is *the* dependency your routes import:
def get_current_user_id(request: Request) -> str:
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user_id

# Middleware to decode and stash `user_id` on each request
bearer_scheme = HTTPBearer(auto_error=False)

async def verify_jwt_token(request: Request, call_next):
    credentials = await bearer_scheme(request)
    if credentials:
        token = credentials.credentials
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
            request.state.user_id = payload.get("sub")
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
    else:
        request.state.user_id = None  # allow public routes
    return await call_next(request)
