import os
from kombu.transport.redis import Channel

BRPOP_TIMEOUT = 60 #sec
    
# make sure we only patch once
if not getattr(Channel, "_long_poll_patched", False):

    def drain_events_long_poll(self, connection, timeout=None):
        # Ignore Celery’s 1-second timeout and always block BRPOP_TIMEOUT
        return self._brpop(connection, timeout=BRPOP_TIMEOUT)

    Channel.drain_events = drain_events_long_poll
    Channel._long_poll_patched = True
    print(f"[✅ PATCH LOADED] Redis BRPOP timeout → {BRPOP_TIMEOUT}s")
