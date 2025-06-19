from celery import Celery
from workers.queue_runner import run_due_queue
from utils.logger import logger

# Celery app (imported from celery_worker.py)
from celery_worker import celery_app

@celery_app.task(name="scan_due_sellers")
def scan_due_sellers():
    """
    Celery task to process queued sellers.
    """
    logger.info("🔁 Starting seller queue scan")
    run_due_queue()
    logger.info("✅ Queue scan completed")
