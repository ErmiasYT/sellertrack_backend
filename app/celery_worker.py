import app.sitecustomize
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

# throttle Redis polling: block up to 1 hour per process
#celery_app.conf.broker_transport_options = {
 #   "socket_timeout": 3600,       # BLPOP will wait up to 3600 s
 #   "visibility_timeout": 3600,   # how long a reserved task is hidden
#}


# ✅ Celery settings (auto task, timeout, no excessive read, beat)
celery_app.conf.update(
    # throttle Redis polling to once a minute
    celery_app.conf.broker_transport_options = {
        "polling_interval": 60,   # worker sleeps 60 s between loops
        "brpop_timeout"  : 60,    # Redis blocks 60 s when queue is empty
        "visibility_timeout": 3600,
        "retry_on_timeout": True,
    }

    task_track_started=True,
    task_time_limit=60,  # ⏱️ 1 minute timeout
    broker_connection_retry_on_startup=True,
    # enforce a single worker process so there's only one BLPOP
    worker_concurrency=1,
    worker_prefetch_multiplier=1,
    
    accept_content=["json"],
    task_serializer="json",

    # ───── DISABLE UNNEEDED EVENTS ─────
    worker_send_task_events=False,
    worker_enable_remote_control=False,
    
    beat_schedule={
        "run-queue-every-minute": {
            "task": "app.workers.queue_runner.run_due_queue",
            # you can pick the hour/minute you like; here it’s midnight UTC
            "schedule": crontab(minute="*"),  # every minute  
        },
    },
)

from kombu import Queue

celery_app.conf.task_queues = (
    Queue('celery', routing_key='celery'),  # Only use this one
)

celery_app.conf.task_default_queue = 'celery'
celery_app.conf.task_default_exchange = 'celery'
celery_app.conf.task_default_routing_key = 'celery'


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
