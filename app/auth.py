from fastapi import Header, HTTPException
from app.config import settings

def verify_api_key(x_api_key: str = Header(...)):
    # Verify against settings.AGENT_API_KEY
    if not x_api_key or x_api_key != settings.agent_api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key. Include header: X-API-Key: <key>"
        )
    
    # Return a user_id based on the token
    user_id = x_api_key[:8]
    return user_id
