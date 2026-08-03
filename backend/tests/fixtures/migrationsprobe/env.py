"""Faehrt die *echte* ``alembic/env.py``.

Der Sinn der Probe ist, jene Datei zu pruefen -- eine eigene Umgebung mit einer eigenen Kopie der
Fremdschluessel-Regel wuerde nur sich selbst bestaetigen. Deshalb wird hier nichts nachgebaut,
sondern das Original ausgefuehrt; von der Probe kommt allein das ``versions``-Verzeichnis daneben.
"""

from pathlib import Path

_echte_umgebung = Path(__file__).resolve().parents[3] / "alembic" / "env.py"
exec(compile(_echte_umgebung.read_text(encoding="utf-8"), str(_echte_umgebung), "exec"))  # noqa: S102
