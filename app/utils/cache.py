import json
import threading
from cachetools import TTLCache
from app.config import settings
import redis

# Connect to Redis
r = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

# In-memory cache: max 1,000 items, 60 s TTL
_local_cache = TTLCache(maxsize=1000, ttl=3600)
_lock = threading.Lock()

def cache_get(key: str):
    # 1) Check local cache first
    with _lock:
        if key in _local_cache:
            return _local_cache[key]

    # 2) Miss → hit Redis
    value = r.get(key)
    if value is None:
        return None
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        parsed = value

    # 3) Populate local cache
    with _lock:
        _local_cache[key] = parsed
    return parsed

def cache_set(key: str, value, ttl: int = 60):
    # 1) Write through to Redis
    try:
        r.set(key, json.dumps(value), ex=ttl)
    except Exception as e:
        print(f"Cache set error: {e}")

    # 2) Also prime local cache
    with _lock:
        _local_cache[key] = value

def cache_delete(key: str):
    # Evict from both
    try:
        r.delete(key)
    except Exception as e:
        print(f"Cache delete error: {e}")
    with _lock:
        _local_cache.pop(key, None)
