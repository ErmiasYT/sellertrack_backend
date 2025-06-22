from kombu.transport.redis import Channel

def custom_drain_events(self, connection, timeout=60):
    print("[✅ HARD PATCH] BRPOP now throttled to 60s")
    return self._brpop(connection, timeout=timeout)

Channel.drain_events = custom_drain_events
print("[🚀 sitecustomize loaded: Celery BRPOP patched]")
