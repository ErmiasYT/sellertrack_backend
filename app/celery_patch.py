# app/celery_patch.py
from kombu.transport.redis import Channel

# Patch drain_events to use longer BRPOP timeout
def custom_drain_events(self, connection, timeout=60):
    return self._brpop(connection, timeout=timeout)  # override to 60s

Channel.drain_events = custom_drain_events
