# app/auth/supabase_jwt.py
from fastapi import Request, HTTPException, Response
from fastapi.security import HTTPBearer
from jose import jwt, JWTError
from app.config import settings

bearer_scheme = HTTPBearer(auto_error=False)


async def verify_jwt_token(request: Request, call_next):
    # --- allow CORS pre-flight to pass straight through -------------
    if request.method == "OPTIONS":
        return Response(status_code=200)
    # ---------------------------------------------------------------

    credentials = await bearer_scheme(request)
    if credentials:
        token = credentials.credentials

        # —— DEBUG: dump the secret and token ——
        logging.debug(f"JWT_SECRET (len={len(settings.JWT_SECRET)}): {settings.JWT_SECRET!r}")
        logging.debug(f"Incoming token (len={len(token)}): {token!r}")
        
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
            request.state.user_id = payload.get("sub")
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
    else:
        request.state.user_id = None  # allow unauthenticated access to public routes

    return await call_next(request)


def get_current_user_id(request: Request) -> str:
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user_id
