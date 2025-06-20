import ssl
from celery import Celery
from app.config import settings
from app.workers.queue_runner import run_due_queue
from celery import shared_task

# Create Celery instance
celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=None  # ⛔ disable result backend to avoid extra Redis writes
)

# ✅ Add SSL options if using rediss://
if settings.REDIS_URL.startswith("rediss://"):
    celery_app.conf.broker_use_ssl = {
        "ssl_cert_reqs": ssl.CERT_REQUIRED
    }

# Celery config (optional)
celery_app.conf.update(
    task_track_started=True,
    task_time_limit=300,
    broker_connection_retry_on_startup=True
)

# Register tasks from modules
celery_app.autodiscover_tasks([
    "app.workers.queue_runner",
    "app.workers.token_manager",
    "app.workers.scan_sellers",
])

# ✅ Celery task wrapper
@shared_task(name="app.workers.queue_runner.run_due_queue")
def run_due_queue_task():
    run_due_queue()  # <-- Don't call with comma, just the function
