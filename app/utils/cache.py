import redis
import json
from app.config import settings

# Connect to Redis
r = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

def cache_get(key: str):
    """
    Get a value from cache by key.
    """
    value = r.get(key)
    if value:
        try:
            return json.loads(value)
        except:
            return value
    return None

def cache_set(key: str, value, ttl: int = 60):
    """
    Set a value in cache with optional TTL (default 60s).
    """
    try:
        r.set(key, json.dumps(value), ex=ttl)
    except Exception as e:
        print(f"Cache set error: {e}")

def cache_delete(key: str):
    """
    Delete a key from cache.
    """
    try:
        r.delete(key)
    except Exception as e:
        print(f"Cache delete error: {e}")
