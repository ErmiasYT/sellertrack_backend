from celery import Celery
from celery.schedules import crontab
from app.config import settings

celery_beat = Celery(
    "beat",
    broker=settings.REDIS_URL,
    backend=None  # set to None if you don't need task results
    #backend=settings.REDIS_URL
)

celery_beat.conf.beat_schedule = {
    "run-due-queue-every-minute": {
        "task": "app.workers.queue_runner.run_due_queue",
        "schedule": crontab(minute="*"),
    },
}

celery_beat.conf.timezone = "UTC"
