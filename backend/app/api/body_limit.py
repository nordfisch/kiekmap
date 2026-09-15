"""Upper limits for request bodies, enforced before anything is read.

**It has to be middleware.** Starlette parses a multipart body before any endpoint or dependency
runs, and spools every file part to a temporary file while it does. A check in ``import_upload``
would come after the disk had already taken the whole body -- and so would the PIN check: a body
sent without a token was written out in full before the 401.

A JSON body is not spooled but read into memory whole, before validation. Every route other than
the upload therefore gets a limit of its own, far smaller than the upload's.

nginx limits the body as well, with ``client_max_body_size`` in ``frontend/nginx.conf``. That
limit does not exist in development, and it answers with an HTML page the admin area cannot show.
"""

import json

from fastapi import HTTPException
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.text import texts

#: Per request. The admin area sends one file per request, so in practice this is per photo.
#:
#: Just below nginx's ``client_max_body_size 128m`` (134,217,728 bytes), so that this answer, which
#: the admin area can put into words, comes first.
MAX_UPLOAD_BYTES = 128_000_000

#: The routes that take files.
UPLOAD_PATHS = frozenset({"/api/admin/upload"})

#: Every other ``/api/`` route. Their bodies are small JSON.
#:
#: The largest legitimate one is a photo edit. ``PhotoUpdate`` holds at most 8,800 characters of
#: text: ``LONG_TEXT_MAX`` twice, plus title, credit and place name. Even with every character
#: escaped as a surrogate pair, twelve bytes each, that makes 105.6 kB. A megabyte is ten times
#: that, which leaves room for the keyword list.
MAX_BODY_BYTES = 1_000_000


def _limit(path: str) -> tuple[int, bool] | None:
    """The limit for this path, and whether it is an upload -- or None for no limit at all."""
    if path in UPLOAD_PATHS:
        return MAX_UPLOAD_BYTES, True
    if path.startswith("/api/"):
        return MAX_BODY_BYTES, False
    return None


class BodyLimit:
    """Refuse a body over the limit of its route with 413.

    Two ways to find out. ``Content-Length`` answers before a byte is read. A body sent without
    it -- chunked -- is counted while it arrives, and the request is broken off at the limit.

    The count raises ``HTTPException`` and nothing else. FastAPI reads the body inside a handler
    that turns any other exception into a 400 "error parsing the body", and passes this one on.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        found = _limit(scope["path"]) if scope["type"] == "http" else None
        if found is None:
            await self.app(scope, receive, send)
            return

        # Looked up at call time rather than at startup, so that a test can lower the limits.
        limit, upload = found
        declared = dict(scope["headers"]).get(b"content-length")
        if declared is not None and declared.isdigit() and int(declared) > limit:
            await _refuse(send, _message(limit, upload))
            return

        received = 0

        async def counting_receive() -> Message:
            nonlocal received
            message = await receive()
            if message["type"] == "http.request":
                received += len(message.get("body", b""))
                if received > limit:
                    raise HTTPException(413, _message(limit, upload))
            return message

        await self.app(scope, counting_receive, send)


def _message(limit: int, upload: bool) -> str:
    size = texts().backup.size(limit)
    return texts().imports.upload_too_large(size) if upload else texts().admin.body_too_large(size)


async def _refuse(send: Send, message: str) -> None:
    body = json.dumps({"detail": message})
    await send(
        {
            "type": "http.response.start",
            "status": 413,
            "headers": [
                (b"content-type", b"application/json"),
                (b"content-length", str(len(body.encode())).encode()),
                # The rest of the body is not read; the connection must not be reused for it.
                (b"connection", b"close"),
            ],
        }
    )
    await send({"type": "http.response.body", "body": body.encode()})
