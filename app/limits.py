import threading


class FixtureBudget:
    """Count the entire ASGI response, including streaming and background tasks."""

    def __init__(self, app):
        self.app = app
        self.lock = threading.Lock()
        self.active = 0
        self.used = 0

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        headers = scope.get("headers", [])
        if (
            len(headers) > 64
            or sum(len(key) + len(value) for key, value in headers) > 16384
            or len(scope.get("query_string", b"")) > 8192
        ):
            await send({"type": "http.response.start", "status": 431, "headers": []})
            await send({"type": "http.response.body", "body": b"fixture metadata cap"})
            return None
        with self.lock:
            admitted = self.active < 2 and self.used < 100
            if admitted:
                self.active += 1
                self.used += 1
        if not admitted:
            await send({"type": "http.response.start", "status": 429, "headers": []})
            await send({"type": "http.response.body", "body": b"fixture budget reached"})
            return None
        try:
            return await self.app(scope, receive, send)
        finally:
            with self.lock:
                self.active -= 1
