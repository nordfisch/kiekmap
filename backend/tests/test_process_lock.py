"""The lock that lets exactly one backend process run on a data directory.

Sessions, the PIN lockout, the backup job and ``DatabaseGate`` live in the memory of one process.
A second worker beside the first would split them without a sound. See ``app.db.process_lock``.
"""

import subprocess
import sys
import textwrap

import pytest
from fastapi.testclient import TestClient

from app.db import BackendAlreadyRunning, collection_lock, process_lock


class TestTheLock:
    def test_a_second_process_lock_is_refused_while_the_first_is_held(self, settings):
        with process_lock(settings):
            with pytest.raises(BackendAlreadyRunning) as refusal, process_lock(settings):
                pass

        assert "Another Kiekmap backend is already running" in str(refusal.value)
        assert str(settings.data_dir) in str(refusal.value)

    def test_the_lock_is_released_when_the_block_ends(self, settings):
        with process_lock(settings):
            pass

        with process_lock(settings):
            pass

    def test_the_lock_is_not_the_collection_lock(self, settings):
        """An exclusive lock on ``kiekmap.lock`` for the backend's life would refuse the CLI."""
        assert settings.process_lock_path != settings.lock_path

        with process_lock(settings):
            with collection_lock(settings, exclusive=False):
                pass

    def test_a_lock_held_by_another_process_refuses_this_one(self, settings):
        holder = subprocess.Popen(
            [
                sys.executable,
                "-c",
                textwrap.dedent(
                    f"""
                    import fcntl, os, time
                    fd = os.open({str(settings.process_lock_path)!r}, os.O_RDONLY | os.O_CREAT)
                    fcntl.flock(fd, fcntl.LOCK_EX)
                    print("locked", flush=True)
                    time.sleep(60)
                    """
                ),
            ],
            stdout=subprocess.PIPE,
            text=True,
        )
        try:
            assert holder.stdout is not None
            assert holder.stdout.readline().strip() == "locked"

            with pytest.raises(BackendAlreadyRunning), process_lock(settings):
                pass
        finally:
            holder.kill()
            holder.wait()

        with process_lock(settings):
            pass


class TestTheService:
    def test_a_second_service_on_the_same_data_directory_stops_at_startup(self, client, settings):
        from app.main import app as fastapi_app

        with pytest.raises(BackendAlreadyRunning), TestClient(fastapi_app):
            pass

    def test_a_service_that_stopped_releases_the_lock(self, session, settings):
        from app.main import app as fastapi_app

        with TestClient(fastapi_app):
            pass

        with process_lock(settings):
            pass

    def test_a_refused_service_starts_no_watcher(self, session, settings, monkeypatch):
        from app import main

        started: list[bool] = []
        monkeypatch.setattr(main.IncomingWatcher, "start", lambda self: started.append(True))

        with process_lock(settings):
            with pytest.raises(BackendAlreadyRunning), TestClient(main.app):
                pass

        assert started == []


class TestTheCommandLine:
    def test_a_writing_command_runs_while_the_service_holds_the_lock(self, session, settings):
        from app import cli

        with process_lock(settings):
            assert cli.main(["places"]) == 0

    def test_a_writing_command_is_still_refused_during_a_restore(self, session, settings, capsys):
        from app import cli

        with process_lock(settings):
            with collection_lock(settings, exclusive=True):
                assert cli.main(["places"]) == 1

        assert "A restore is running" in capsys.readouterr().err
