from celery import Celery
from app.config import settings

# Create Celery instance
celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

# ✅ Add SSL options if using rediss://
if settings.REDIS_URL.startswith("rediss://"):
    celery_app.conf.broker_use_ssl = {
        "ssl_cert_reqs": "none"
    }
    celery_app.conf.redis_backend_use_ssl = {
        "ssl_cert_reqs": "none"
    }

# Celery config (optional)
celery_app.conf.update(
    task_track_started=True,
    task_time_limit=300,  # 5 min timeout
)

# Import task modules to register them
celery_app.autodiscover_tasks([
    "app.workers.scan_sellers",
    "app.workers.token_manager",
    "app.workers.queue_runner",
])
