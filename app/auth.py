import jwt
from datetime import datetime, timedelta, timezone
from fastapi import Header, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings

security = HTTPBearer()

def verify_api_key(x_api_key: str = Header(None)):
    if not x_api_key or x_api_key != settings.agent_api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key. Include header: X-API-Key: <key>"
        )
    return x_api_key[:8]

def create_access_token(user_id: str):
    expires_delta = timedelta(minutes=60)
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"sub": user_id, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm="HS256")
    return encoded_jwt

async def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

def get_current_user(
    x_api_key: str = Header(None),
    token: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False))
):
    # Support both API Key and JWT
    if x_api_key:
        return verify_api_key(x_api_key)
    if token:
        try:
            payload = jwt.decode(token.credentials, settings.jwt_secret, algorithms=["HS256"])
            return payload.get("sub")
        except:
            raise HTTPException(status_code=401, detail="Invalid session token")
    
    raise HTTPException(status_code=401, detail="Authentication required")
