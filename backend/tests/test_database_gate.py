"""The gate that closes the database for the seconds a restore swaps its file.

What it guards against is silent: a request during the swap writes into the file that was just set
aside, answers 200, and its statement is gone. See ``app.db.DatabaseGate`` and the restore tests in
``test_backup.py``.
"""

import threading
import time

import pytest

from app.db import DatabaseClosed, DatabaseGate, DatabaseInUse


def test_a_closed_gate_refuses_a_new_session():
    gate = DatabaseGate()

    with gate.closed(timeout_s=1), pytest.raises(DatabaseClosed), gate.use():
        pass


def test_closing_waits_for_the_session_in_use():
    gate = DatabaseGate()
    left = threading.Event()

    def finish_the_request():
        with gate.use():
            time.sleep(0.1)
        left.set()

    worker = threading.Thread(target=finish_the_request)
    with gate.use():
        worker.start()
    time.sleep(0.02)

    with gate.closed(timeout_s=2):
        assert left.is_set(), "closed while a session was still in use"
    worker.join()


def test_a_session_that_stays_in_use_opens_the_gate_again():
    """A refused restore must not leave the service answering 503."""
    gate = DatabaseGate()

    with gate.use():
        with pytest.raises(DatabaseInUse), gate.closed(timeout_s=0.05):
            pass

    with gate.use():
        pass


def test_the_api_answers_503_while_the_gate_is_closed(client, database):
    with database.gate.closed(timeout_s=1):
        response = client.get("/api/photos/tags")

    assert response.status_code == 503
    assert response.headers["retry-after"]
    assert client.get("/api/photos/tags").status_code == 200


def test_the_readiness_probe_is_not_ready_while_the_gate_is_closed(client, database):
    with database.gate.closed(timeout_s=1):
        assert client.get("/api/health").status_code == 503


def test_the_inbox_waits_while_the_gate_is_closed(session, database, settings, fixtures_dir):
    from app.services.watcher import IncomingWatcher

    (settings.incoming_dir / "scan.jpg").write_bytes(
        (fixtures_dir / "scan_ohne_exif.jpg").read_bytes()
    )
    watcher = IncomingWatcher(settings, interval=0)
    watcher.scan_once()

    with database.gate.closed(timeout_s=1):
        assert watcher.scan_once() == 0

    assert (settings.incoming_dir / "scan.jpg").is_file(), "the file waits in the inbox"
    assert watcher.scan_once() == 1, "and comes in at the next look"
