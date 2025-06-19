from services.seller_service import scan_seller_and_detect_new_asins
from db.supabase import get_supabase_client
from datetime import datetime, timedelta
from models.enums import QueueStatus
from utils.logger import logger

def run_due_queue():
    """
    Processes all sellers in the queue whose next_attempt_at is now or past.
    """
    supabase = get_supabase_client()
    now = datetime.utcnow().isoformat()

    # Fetch due queue entries
    response = supabase.table("queue").select("*").lte("next_attempt_at", now).eq("status", QueueStatus.QUEUED).execute()
    due_entries = response.data or []

    for entry in due_entries:
        seller_id = entry["seller_id"]
        queue_id = entry["id"]

        logger.info(f"Processing queue entry: seller {seller_id}")

        try:
            # Run scan
            scan_seller_and_detect_new_asins(seller_id)

            # Mark as done
            supabase.table("queue").update({
                "status": QueueStatus.DONE,
            }).eq("id", queue_id).execute()

        except Exception as e:
            logger.error(f"Scan failed for seller {seller_id}: {e}")

            # Retry logic
            supabase.table("queue").update({
                "retry_count": entry["retry_count"] + 1,
                "next_attempt_at": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
                "status": QueueStatus.QUEUED,
            }).eq("id", queue_id).execute()