import ssl
from celery import Celery
from app.config import settings
from app.workers.queue_runner import run_due_queue
from celery import shared_task
from celery.schedules import crontab

celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=None  # ⛔ disable result backend to save reads
)

# ✅ SSL settings for rediss://
if settings.REDIS_URL.startswith("rediss://"):
    celery_app.conf.broker_use_ssl = {
        "ssl_cert_reqs": ssl.CERT_REQUIRED
    }

# ✅ Celery settings (auto task, timeout, no excessive read, beat)
celery_app.conf.update(
    task_track_started=True,
    task_time_limit=60,  # ⏱️ 1 minute timeout
    broker_connection_retry_on_startup=True,
    worker_prefetch_multiplier=1,
    accept_content=["json"],
    task_serializer="json",
        # throttle Redis polling to once a minute
    broker_transport_options={
        "socket_timeout": 60,        # BLPOP will block up to 60s
        "visibility_timeout": 3600,  # how long to hide a reserved task
    },
    beat_schedule={
        "run-queue-every-minute": {
            "task": "app.workers.queue_runner.run_due_queue",
            # you can pick the hour/minute you like; here it’s midnight UTC
            "schedule": crontab(hour=0, minute=0),  
        },
    },
)

# 📦 Register tasks
celery_app.autodiscover_tasks([
    "app.workers.queue_runner",
    "app.workers.token_manager",
    "app.workers.scan_sellers",
])

# ✅ Task wrapper
@shared_task(name="app.workers.queue_runner.run_due_queue")
def run_due_queue_task():
    run_due_queue()
