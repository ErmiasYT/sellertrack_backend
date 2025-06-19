from celery import Celery
from config import settings

# Create Celery instance
celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

# Celery config (optional)
celery_app.conf.update(
    task_track_started=True,
    task_time_limit=300,  # 5 min timeout
)

# Import task modules to register them
celery_app.autodiscover_tasks([
    "workers.scan_sellers",
    "workers.token_manager",
    "workers.queue_runner",
])