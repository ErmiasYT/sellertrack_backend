from celery import shared_task
from services.seller_service import scan_seller_and_detect_new_asins
from db.supabase import get_supabase_client
from datetime import datetime, timedelta
from models.enums import QueueStatus
from utils.logger import logger



def run_due_queue():
    """
    Celery task: Processes all sellers in the queue whose next_attempt_at is now or past.
    """
    supabase = get_supabase_client()
    now = datetime.utcnow().isoformat()

    try:
        response = supabase.table("queue").select("*").lte("next_attempt_at", now).eq("status", QueueStatus.QUEUED).execute()
        due_entries = response.data or []
    except Exception as e:
        logger.error(f"Failed to fetch due queue entries: {e}")
        return

    for entry in due_entries:
        seller_id = entry["seller_id"]
        queue_id = entry["id"]
        retry_count = entry.get("retry_count", 0)

        logger.info(f"Processing queue entry: seller {seller_id}")

        try:
            scan_seller_and_detect_new_asins(seller_id)

            supabase.table("queue").update({
                "status": QueueStatus.DONE,
                "processed_at": datetime.utcnow().isoformat(),
            }).eq("id", queue_id).execute()

        except Exception as e:
            logger.error(f"Scan failed for seller {seller_id}: {e}")

            next_retry = datetime.utcnow() + timedelta(hours=1)

            supabase.table("queue").update({
                "retry_count": retry_count + 1,
                "next_attempt_at": next_retry.isoformat(),
                "status": QueueStatus.QUEUED,
            }).eq("id", queue_id).execute()

@shared_task
def test_task():
    print("✅ It works.")
    return "success"
