import sitecustomize        # PATCH FIRST
import ssl
from celery import Celery
from app.config import settings
from celery.schedules import crontab
from app.workers.queue_runner import run_due_queue
from celery import shared_task

celery_app = Celery("worker",
    broker=settings.REDIS_URL,
    backend=None)

# SSL for rediss://
if settings.REDIS_URL.startswith("rediss://"):
    celery_app.conf.broker_use_ssl = {"ssl_cert_reqs": ssl.CERT_REQUIRED}

# ⬇️  transport options FIRST (stand-alone assignment)
celery_app.conf.broker_transport_options = {
    "polling_interval": 60,     # worker sleeps 60 s when idle
    "brpop_timeout":   60,      # Redis blocks 60 s
    "visibility_timeout": 3600,
    "retry_on_timeout": True,
}

# now the normal bulk config
celery_app.conf.update(
    task_track_started=True,
    task_time_limit=60,
    broker_connection_retry_on_startup=True,
    worker_concurrency=1,
    worker_prefetch_multiplier=1,
    accept_content=["json"],
    task_serializer="json",
    worker_send_task_events=False,
    worker_enable_remote_control=False,
    beat_schedule={
        "run-queue-every-minute": {
            "task": "app.workers.queue_runner.run_due_queue",
            "schedule": crontab(minute="*"),
        },
    },
)

celery_app.conf.beat_schedule = {
    "run-due-queue-every-minute": {
        "task": "app.workers.queue_runner.run_due_queue",
        "schedule": crontab(minute="*"),   # every minute
    },

# Optional: single queue declaration (fine to keep)
from kombu import Queue
celery_app.conf.task_queues = (Queue("celery", routing_key="celery"),)
celery_app.conf.task_default_queue = "celery"
celery_app.conf.task_default_exchange = "celery"
celery_app.conf.task_default_routing_key = "celery"

# Discover & wrapper
celery_app.autodiscover_tasks([
    "app.workers.queue_runner",
    "app.workers.token_manager",
    "app.workers.scan_sellers",
])

@shared_task(name="app.workers.queue_runner.run_due_queue")
def run_due_queue_task():
    run_due_queue()
