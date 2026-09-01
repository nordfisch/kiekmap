"""Tests of signing in to the admin view.

The core point: a PIN is a short secret. Four digits are ten thousand possibilities, which a
script would have tried in seconds. What makes up for that is the lockout after a few failed
attempts -- which is why it stands at the centre here and the hashing does not.
"""

import pytest

from app.services import auth


class TestPin:
    def test_a_wrong_pin_is_rejected(self):
        stored = auth.hash_pin("4711")

        assert not auth.verify_pin("4712", stored)

    def test_the_right_pin_is_recognised(self):
        stored = auth.hash_pin("4711")

        assert auth.verify_pin("4711", stored)

    def test_the_same_pin_gives_different_hashes(self):
        """Salt. Otherwise a glance at two .env files would reveal that both hold the same PIN."""
        assert auth.hash_pin("4711") != auth.hash_pin("4711")

    def test_a_broken_hash_lets_nobody_in(self):
        """A mistyped entry in the .env must not turn into an open door by accident."""
        for unusable in ("", "4711", "pbkdf2_sha256$abc", "md5$1$aa$bb"):
            assert not auth.verify_pin("4711", unusable)

    def test_a_pin_has_to_be_digits(self):
        """The keypad on the museum device has no letters."""
        assert auth.is_valid_pin("4711")
        assert not auth.is_valid_pin("47a1")
        assert not auth.is_valid_pin("471")
        assert not auth.is_valid_pin("4" * 13)


class TestSessions:
    def test_an_unknown_token_is_not_valid(self):
        store = auth.SessionStore()

        assert store.renew("invented") is None

    def test_a_signed_out_token_is_no_longer_valid(self):
        store = auth.SessionStore()
        session = store.issue()

        store.revoke(session.token)

        assert store.renew(session.token) is None

    def test_a_session_expires(self, monkeypatch: pytest.MonkeyPatch):
        """A login forgotten in the evening must not stay open overnight."""
        clock = [1000.0]
        monkeypatch.setattr(auth.time, "monotonic", lambda: clock[0])
        store = auth.SessionStore(lifetime_s=60)
        session = store.issue()

        clock[0] += 61

        assert store.renew(session.token) is None

    def test_every_request_pushes_the_expiry_back(self, monkeypatch: pytest.MonkeyPatch):
        """Otherwise somebody would be thrown out mid-edit, only because typing takes time."""
        clock = [1000.0]
        monkeypatch.setattr(auth.time, "monotonic", lambda: clock[0])
        store = auth.SessionStore(lifetime_s=60)
        session = store.issue()

        for _ in range(10):
            clock[0] += 30
            assert store.renew(session.token) is not None

        # 300 seconds have passed in total, the session lasts 60 -- and is still alive.
        assert clock[0] == 1300.0


class TestAttemptGuard:
    def test_locks_after_too_many_failed_attempts(self):
        guard = auth.AttemptGuard(max_attempts=3, lockout_s=60)

        assert guard.record_failure() == 0
        assert guard.record_failure() == 0
        assert guard.record_failure() == 60
        assert guard.locked_for() == 60

    def test_the_lockout_expires_on_its_own(self, monkeypatch: pytest.MonkeyPatch):
        clock = [1000.0]
        monkeypatch.setattr(auth.time, "monotonic", lambda: clock[0])
        guard = auth.AttemptGuard(max_attempts=1, lockout_s=60)
        guard.record_failure()

        clock[0] += 61

        assert guard.locked_for() == 0

    def test_a_successful_sign_in_resets_the_counter(self):
        """Otherwise typing errors would add up over months into a lockout."""
        guard = auth.AttemptGuard(max_attempts=3, lockout_s=60)
        guard.record_failure()
        guard.record_failure()

        guard.reset()

        assert guard.record_failure() == 0
        assert guard.locked_for() == 0
