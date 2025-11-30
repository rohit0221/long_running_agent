from typing import List

class AnalyticsEngine:
    def __init__(self):
        self.data = []

    def track_event(self, event_name: str, properties: dict = None):
        if not event_name:
            raise ValueError("Event name cannot be empty")
        self.data.append({"name": event_name, "properties": properties or {}})

    def get_events(self, event_name: str) -> List[dict]:
        return [e for e in self.data if e["name"] == event_name]

    def clear(self):
        self.data = []
