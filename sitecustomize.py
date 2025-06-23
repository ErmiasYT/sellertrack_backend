# sitecustomize.py  (project root)
import os
from kombu.transport.redis import Channel

BRPOP_TIMEOUT = int(os.getenv("CELERY_BRPOP_TIMEOUT", "60"))

# Only patch once
if not getattr(Channel, "_patched_brpop", False):
    _orig = Channel._brpop  # the underlying kombu hook

    def _brpop_long_poll(self, *args, **kwargs):
        # force every BRPOP to block for BRPOP_TIMEOUT seconds
        kwargs["timeout"] = BRPOP_TIMEOUT
        return _orig(self, *args, **kwargs)

    Channel._brpop = _brpop_long_poll
    Channel._patched_brpop = True
    print(f"[✅ PATCH LOADED] Redis BRPOP timeout → {BRPOP_TIMEOUT}s")
