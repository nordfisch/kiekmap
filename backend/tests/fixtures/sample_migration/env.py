"""Runs the *real* ``alembic/env.py``.

The point of the sample is to check that file -- an environment of its own with its own copy of the
foreign-key rule would only confirm itself. So nothing is rebuilt here; the original is executed,
and the sample contributes only the ``versions`` directory beside it.
"""

from pathlib import Path

_real_environment = Path(__file__).resolve().parents[3] / "alembic" / "env.py"
exec(compile(_real_environment.read_text(encoding="utf-8"), str(_real_environment), "exec"))  # noqa: S102
