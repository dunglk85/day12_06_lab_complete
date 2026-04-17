import redis
from datetime import datetime
from fastapi import HTTPException
from app.config import settings

r = redis.from_url(settings.redis_url)

def check_budget(user_id: str, cost_to_add: float = 0.0):
    # Determine current month for monthly spending
    month_key = datetime.now().strftime("%Y-%m")
    key = f"budget:{user_id}:{month_key}"
    
    # Check spending (default to 0.0 if not exists)
    current_spent = float(r.get(key) or 0.0)
    
    # In config, we have daily_budget_usd
    limit = settings.daily_budget_usd
    
    # Raise HTTPException(402) if exceeded
    if current_spent + cost_to_add > limit:
        raise HTTPException(
            status_code=402, 
            detail=f"Budget exhausted. Limit: ${limit}."
        )
    
    # Add new cost to the budget if requested
    if cost_to_add > 0:
        r.incrbyfloat(key, cost_to_add)
        r.expire(key, 32 * 24 * 3600)  # 32 days TTL
        
    return True
