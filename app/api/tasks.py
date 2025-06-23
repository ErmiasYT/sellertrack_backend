import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from app.workers.queue_runner import run_due_queue

router = APIRouter()
api_key_header = APIKeyHeader(name="X-API-Key")  # header you’ll send from Cron

@router.post("/tasks/run-queue", status_code=204)
def trigger_run_queue(x_api_key: str = Depends(api_key_header)):
    # secure it—only your Cron knows this key
    if x_api_key != os.getenv("YOUR_CRON_KEY"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    # this calls your existing logic directly (no Celery enqueuing)
    run_due_queue()
    return
