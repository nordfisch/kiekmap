# SPDX-FileCopyrightText: 2026 Kalle Erlhoff
# SPDX-License-Identifier: Apache-2.0

"""Access to the admin area: PIN, sessions, and a lock against guessing.

A PIN rather than a password, because the only input device in the museum is a touchscreen with
no keyboard. That makes the secret short, so it needs a counterweight: four digits are ten
thousand combinations, which a script would be through in seconds. ``AttemptGuard`` turns that
into years.

The PIN itself is never stored -- ``admin_pin_hash`` in the settings holds a PBKDF2 digest, which
``python -m app.cli pin`` produces.
"""

import hashlib
import hmac
import logging
import secrets
import threading
import time
from dataclasses import dataclass

log = logging.getLogger(__name__)

ALGORITHM = "pbkdf2_sha256"
#: Deliberately slow. It costs a tenth of a second on the Pi -- once, at login.
ROUNDS = 200_000

MIN_PIN_LENGTH = 4
MAX_PIN_LENGTH = 12

#: How long a session survives without a request. Sliding: every call pushes it back, so nobody
#: is thrown out mid-edit, but a login forgotten in the evening is closed by morning.
SESSION_LIFETIME_S = 30 * 60

#: Wrong attempts before the pad locks, and for how long.
MAX_ATTEMPTS = 5
LOCKOUT_S = 60

#: How long a download ticket is good for. Only long enough to click the link it was made for.
TICKET_LIFETIME_S = 60


# --- the PIN ----------------------------------------------------------------


def hash_pin(pin: str) -> str:
    """``algorithm$rounds$salt$digest`` -- one line, ready for the .env file."""
    return _encode(pin, secrets.token_bytes(16), ROUNDS)


def _encode(pin: str, salt: bytes, rounds: int) -> str:
    digest = hashlib.pbkdf2_hmac("sha256", pin.encode("utf-8"), salt, rounds)
    return f"{ALGORITHM}${rounds}${salt.hex()}${digest.hex()}"


def verify_pin(pin: str, stored: str) -> bool:
    try:
        algorithm, rounds, salt, _ = stored.split("$")
        if algorithm != ALGORITHM:
            raise ValueError(f"unknown algorithm {algorithm!r}")
        candidate = _encode(pin, bytes.fromhex(salt), int(rounds))
    except ValueError as error:
        # Not an exception the caller should handle: a broken hash means the device was set up
        # wrongly, and nobody gets in until that is fixed. Say so in the log rather than silently
        # rejecting every PIN.
        log.error("admin_pin_hash unusable (%s) -- create one with: python -m app.cli pin", error)
        return False

    # Constant-time comparison: a fast "no" would betray how far the digest matched.
    return hmac.compare_digest(candidate, stored)


def is_valid_pin(pin: str) -> bool:
    """Digits only -- the pad has no letters, so a PIN with any would be unenterable."""
    return pin.isdigit() and MIN_PIN_LENGTH <= len(pin) <= MAX_PIN_LENGTH


# --- sessions ---------------------------------------------------------------


@dataclass(frozen=True)
class AdminSession:
    token: str
    #: Remaining seconds, not a point in time.
    #:
    #: The Pi has no real-time clock and no network, so its wall clock can be off by years after
    #: a power cut. A countdown works regardless -- and the admin area can show it honestly.
    expires_in_s: int


class SessionStore:
    """Valid tokens, in memory.

    Not in the database on purpose: restarting the service should end every session. On a device
    that reboots into the kiosk every morning, that is the cheapest way to guarantee no login
    survives the night.
    """

    def __init__(self, lifetime_s: int = SESSION_LIFETIME_S) -> None:
        self._lifetime_s = lifetime_s
        self._expiry: dict[str, float] = {}
        # FastAPI runs synchronous endpoints in a thread pool, so two requests really can be in
        # here at the same time.
        self._lock = threading.Lock()

    def issue(self) -> AdminSession:
        token = secrets.token_urlsafe(32)
        with self._lock:
            self._forget_expired()
            self._expiry[token] = time.monotonic() + self._lifetime_s
        return AdminSession(token, self._lifetime_s)

    def renew(self, token: str) -> AdminSession | None:
        """Check the token and push its expiry back. ``None`` means: log in again."""
        with self._lock:
            deadline = self._expiry.get(token)
            if deadline is None or deadline <= time.monotonic():
                self._expiry.pop(token, None)
                return None
            self._expiry[token] = time.monotonic() + self._lifetime_s
        return AdminSession(token, self._lifetime_s)

    def revoke(self, token: str) -> None:
        with self._lock:
            self._expiry.pop(token, None)

    def clear(self) -> None:
        with self._lock:
            self._expiry.clear()

    def _forget_expired(self) -> None:
        now = time.monotonic()
        for token in [t for t, deadline in self._expiry.items() if deadline <= now]:
            del self._expiry[token]


class TicketStore:
    """One-shot permits for the one thing a header cannot reach: a browser download.

    Everything in the admin area authenticates with ``X-Admin-Token``. A download does not go
    through our code -- the browser fetches it -- and a browser cannot be told to send a header.
    The short way would be to hang the session token in the URL, and it is the wrong one: URLs end
    up in history, in bookmarks, in proxy logs, and that token opens the whole admin area for half
    an hour.

    A ticket is the opposite of that: it buys exactly one download, it is forgotten the moment it
    is used, and it is worthless a minute later. Like the sessions it lives in memory -- a restart
    is allowed to invalidate it.
    """

    def __init__(self, lifetime_s: int = TICKET_LIFETIME_S) -> None:
        self._lifetime_s = lifetime_s
        self._expiry: dict[str, float] = {}
        self._lock = threading.Lock()

    def issue(self) -> tuple[str, int]:
        """A fresh ticket and how many seconds it is good for."""
        ticket = secrets.token_urlsafe(32)
        with self._lock:
            self._forget_expired()
            self._expiry[ticket] = time.monotonic() + self._lifetime_s
        return ticket, self._lifetime_s

    def redeem(self, ticket: str) -> bool:
        """True exactly once per ticket -- using it is what spends it."""
        with self._lock:
            deadline = self._expiry.pop(ticket, None)
        return deadline is not None and deadline > time.monotonic()

    def clear(self) -> None:
        with self._lock:
            self._expiry.clear()

    def _forget_expired(self) -> None:
        now = time.monotonic()
        for ticket in [t for t, deadline in self._expiry.items() if deadline <= now]:
            del self._expiry[ticket]


# --- guessing ---------------------------------------------------------------


class AttemptGuard:
    """Counts wrong PINs and locks the pad for a while.

    Counted for the device as a whole, not per caller. The kiosk has exactly one screen, so
    there is nobody to lock out unfairly -- and counting per IP would be worthless anyway, since
    everything comes through nginx from the same address.
    """

    def __init__(self, max_attempts: int = MAX_ATTEMPTS, lockout_s: int = LOCKOUT_S) -> None:
        self._max_attempts = max_attempts
        self._lockout_s = lockout_s
        self._failures = 0
        self._locked_until = 0.0
        self._lock = threading.Lock()

    def locked_for(self) -> int:
        """Remaining seconds of the lock, 0 when the pad is open."""
        with self._lock:
            return max(0, round(self._locked_until - time.monotonic()))

    def record_failure(self) -> int:
        """Count one wrong PIN. Returns the seconds now locked, 0 while attempts remain."""
        with self._lock:
            self._failures += 1
            if self._failures >= self._max_attempts:
                self._failures = 0
                self._locked_until = time.monotonic() + self._lockout_s
                log.warning("Admin login locked for %ss after too many attempts", self._lockout_s)
                return self._lockout_s
            return 0

    def reset(self) -> None:
        with self._lock:
            self._failures = 0
            self._locked_until = 0.0


#: One store and one guard for the process. Both hold no state worth persisting.
sessions = SessionStore()
attempts = AttemptGuard()
tickets = TicketStore()
