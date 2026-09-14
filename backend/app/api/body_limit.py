"""An upper limit for the request body of the upload, enforced before anything is read.

**It has to be middleware.** Starlette parses a multipart body before any endpoint or dependency
runs, and spools every file part to a temporary file while it does. A check in ``import_upload``
would come after the disk had already taken the whole body -- and so would the PIN check: a body
sent without a token was written out in full before the 401.

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

#: The routes that take files. Every other body is small JSON.
LIMITED_PATHS = frozenset({"/api/admin/upload"})


class BodyLimit:
    """Refuse an upload over ``MAX_UPLOAD_BYTES`` with 413.

    Two ways to find out. ``Content-Length`` answers before a byte is read. A body sent without
    it -- chunked -- is counted while it arrives, and the request is broken off at the limit.

    The count raises ``HTTPException`` and nothing else. FastAPI reads the body inside a handler
    that turns any other exception into a 400 "error parsing the body", and passes this one on.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or scope["path"] not in LIMITED_PATHS:
            await self.app(scope, receive, send)
            return

        # Read at call time rather than at startup, so that a test can lower it.
        limit = MAX_UPLOAD_BYTES
        declared = dict(scope["headers"]).get(b"content-length")
        if declared is not None and declared.isdigit() and int(declared) > limit:
            await _refuse(send, limit)
            return

        received = 0

        async def counting_receive() -> Message:
            nonlocal received
            message = await receive()
            if message["type"] == "http.request":
                received += len(message.get("body", b""))
                if received > limit:
                    raise HTTPException(413, _message(limit))
            return message

        await self.app(scope, counting_receive, send)


def _message(limit: int) -> str:
    return texts().imports.upload_too_large(texts().backup.size(limit))


async def _refuse(send: Send, limit: int) -> None:
    body = json.dumps({"detail": _message(limit)})
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
