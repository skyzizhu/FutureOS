"""Bound chunked and declared request bodies before JSON parsing, without logging bytes."""

from uuid import uuid4

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send


class BodyLimitMiddleware:
    def __init__(self, app: ASGIApp, max_bytes: int = 1_048_576) -> None:
        self.app, self.max_bytes = app, max_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or scope.get("method") in {"GET", "HEAD", "OPTIONS"}:
            await self.app(scope, receive, send)
            return
        chunks = []
        size = 0
        while True:
            event = await receive()
            if event["type"] == "http.disconnect":
                return
            body = event.get("body", b"")
            size += len(body)
            if size > self.max_bytes:
                identifier = str(scope.get("state", {}).get("request_id") or uuid4())
                response = JSONResponse(
                    {
                        "schema_version": "1.0",
                        "code": "PAYLOAD_TOO_LARGE",
                        "message": "请求超过本地安全上限",
                        "request_id": identifier,
                        "details": {"retryable": False},
                    },
                    status_code=413,
                    headers={"Cache-Control": "no-store", "X-Request-ID": identifier},
                )
                await response(scope, receive, send)
                return
            chunks.append(body)
            if not event.get("more_body", False):
                break
        sent = False

        async def replay() -> Message:
            nonlocal sent
            if sent:
                return await receive()
            sent = True
            return {"type": "http.request", "body": b"".join(chunks), "more_body": False}

        await self.app(scope, replay, send)
