import time
import uuid
import redis
from fastapi import HTTPException
from app.config import settings

# Initialize Redis connection (fallback to None if no URL)
r = redis.from_url(settings.redis_url) if settings.redis_url else None

def check_rate_limit(user_id: str):
    if not r:
        return # Skip rate limit if Redis is not configured
    now = time.time()
    window_start = now - 60  # 60s sliding window
    key = f"rate_limit:{user_id}"
    
    pipe = r.pipeline()
    
    # Implementing sliding window with Redis Sorted Set
    pipe.zremrangebyscore(key, 0, window_start) # Remove old requests
    pipe.zcard(key)                             # Count requests in window
    
    request_id = str(uuid.uuid4())
    pipe.zadd(key, {request_id: now})           # Add current request
    pipe.expire(key, 60)                        # Set expiration for the whole set
    
    results = pipe.execute()
    request_count = results[1]
    
    # Raise HTTPException(429) if exceeded
    if request_count >= settings.rate_limit_per_minute:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded: {settings.rate_limit_per_minute} req/min",
            headers={"Retry-After": "60"}
        )
