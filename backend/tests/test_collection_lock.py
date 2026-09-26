"""The lock file that keeps a restore and the writing CLI commands apart.

The CLI runs in a process of its own, which ``DatabaseGate`` cannot reach. Without the lock a
command wrote through a restore into the database that was set aside, and reported success. The
restore side is tested in ``test_backup.py``; see ``app.db.collection_lock``.
"""

import subprocess
import sys
import textwrap

import pytest
from sqlalchemy import func, select

from app.db import CollectionLocked, collection_lock

WRITING_COMMANDS = [
    ["import", "{fixtures}"],
    ["scan"],
    ["places"],
    ["seed-load"],
    ["empty", "--yes"],
]
READING_COMMANDS = [["stats"], ["duplicates"], ["seed-export"]]


def _run(argv: list[str], fixtures_dir) -> int:
    from app import cli

    return cli.main([part.format(fixtures=fixtures_dir) for part in argv])


class TestTheLock:
    def test_a_restore_is_refused_while_a_command_holds_the_lock(self, settings):
        with collection_lock(settings, exclusive=False):
            with pytest.raises(CollectionLocked), collection_lock(settings, exclusive=True):
                pass

    def test_a_command_is_refused_while_a_restore_holds_the_lock(self, settings):
        with collection_lock(settings, exclusive=True):
            with pytest.raises(CollectionLocked), collection_lock(settings, exclusive=False):
                pass

    def test_two_commands_do_not_exclude_each_other(self, settings):
        with collection_lock(settings, exclusive=False), collection_lock(settings, exclusive=False):
            pass

    def test_the_lock_is_released_when_the_block_ends(self, settings):
        with collection_lock(settings, exclusive=False):
            pass

        with collection_lock(settings, exclusive=True):
            pass

    def test_a_lock_of_a_killed_process_does_not_block_the_next_restore(self, settings):
        """The reason for flock over a marker file: a crash or a power cut leaves nothing behind."""
        holder = subprocess.Popen(  # noqa: S603 -- this interpreter, a literal list, no shell
            [
                sys.executable,
                "-c",
                textwrap.dedent(
                    f"""
                    import fcntl, os, sys, time
                    fd = os.open({str(settings.lock_path)!r}, os.O_RDONLY | os.O_CREAT, 0o644)
                    fcntl.flock(fd, fcntl.LOCK_SH)
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

            with pytest.raises(CollectionLocked), collection_lock(settings, exclusive=True):
                pass
        finally:
            holder.kill()
            holder.wait()

        with collection_lock(settings, exclusive=True):
            pass


class TestTheCommandLine:
    @pytest.mark.parametrize("argv", WRITING_COMMANDS, ids=lambda argv: argv[0])
    def test_a_writing_command_refuses_during_a_restore(
        self, argv, session, settings, fixtures_dir, capsys
    ):
        with collection_lock(settings, exclusive=True):
            code = _run(argv, fixtures_dir)

        assert code == 1
        assert "A restore is running" in capsys.readouterr().err

    def test_an_import_during_a_restore_writes_nothing(self, session, settings, fixtures_dir):
        from app.models import Photo

        with collection_lock(settings, exclusive=True):
            _run(["import", "{fixtures}"], fixtures_dir)

        assert session.scalar(select(func.count()).select_from(Photo)) == 0
        assert not any(path.is_file() for path in settings.photos_dir.rglob("*"))
        assert not any(path.is_file() for path in settings.thumbs_dir.rglob("*"))

    def test_an_import_holds_the_lock_while_it_writes(
        self, session, settings, fixtures_dir, monkeypatch
    ):
        """The restore must see the command for its whole run, not only at its start."""
        from app import cli

        seen: list[bool] = []

        def import_directory(*args, **kwargs):
            try:
                with collection_lock(settings, exclusive=True):
                    seen.append(False)
            except CollectionLocked:
                seen.append(True)
            return []

        monkeypatch.setattr(cli, "import_directory", import_directory)

        assert _run(["import", "{fixtures}"], fixtures_dir) == 0
        assert seen == [True]

    @pytest.mark.parametrize("argv", READING_COMMANDS, ids=lambda argv: argv[0])
    def test_a_reading_command_runs_during_a_restore(self, argv, session, settings, fixtures_dir):
        # seed-export writes beside the temporary data directory, not into the repository.
        with collection_lock(settings, exclusive=True):
            assert _run(argv, fixtures_dir) == 0
