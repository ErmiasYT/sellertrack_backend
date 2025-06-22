from kombu.transport.redis import Channel

def custom_drain_events(self, connection, timeout=60):
    print("[✅ PATCH LOADED] Monkey patch for BRPOP applied")
    return self._brpop(connection, timeout=timeout)

Channel.drain_events = custom_drain_events
