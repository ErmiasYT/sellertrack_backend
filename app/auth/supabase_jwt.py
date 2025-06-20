# app/auth/supabase_jwt.py
from fastapi import HTTPException, Security, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.config import settings

bearer_scheme = HTTPBearer(auto_error=False)

async def verify_jwt_token(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    request: Request = None,
):
    if credentials:
        try:
            payload = jwt.decode(credentials.credentials, settings.JWT_SECRET, algorithms=["HS256"])
            request.state.user_id = payload.get("sub")
        except JWTError:
            raise HTTPException(401, "Invalid token")
    else:
        request.state.user_id = None
    # no need to call_next here if you switch to a dependency-based approach
