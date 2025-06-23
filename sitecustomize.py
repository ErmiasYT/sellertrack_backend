# app/sitecustomize.py  ← loads automatically
import os
from kombu.transport.redis import Channel

BRPOP_TIMEOUT = int(os.getenv("CELERY_BRPOP_TIMEOUT", "60"))

if not getattr(Channel, "_patched_brpop", False):
    _orig_brpop = Channel.brpop

    def brpop_long_poll(self, *queues, **kwargs):
        # Kombu ≤5.2 passes (queues, timeout); ≥5.3 packs (queues,) then kw
        kwargs["timeout"] = BRPOP_TIMEOUT
        return _orig_brpop(self, *queues, **kwargs)

    Channel.brpop = brpop_long_poll
    Channel._patched_brpop = True
    print(f"[✅ PATCH LOADED] Redis BRPOP timeout → {BRPOP_TIMEOUT}s")
