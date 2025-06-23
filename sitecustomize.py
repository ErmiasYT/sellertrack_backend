# sitecustomize.py  (project root)
import os
from kombu.transport.redis import Channel

BRPOP_TIMEOUT = int(os.getenv("CELERY_BRPOP_TIMEOUT", "60"))

# Only patch once
if not getattr(Channel, "_patch_drain", False):
    _orig = Channel.drain_events

    def drain_events_long_poll(self, connection, timeout=None):
        # ignore the timeout Celery passes, use our long block
        return _orig(self, connection, timeout=BRPOP_TIMEOUT)

    Channel.drain_events = drain_events_long_poll
    Channel._patch_drain = True
    print(f"[✅ PATCH LOADED] Redis drain_events timeout → {BRPOP_TIMEOUT}s")
