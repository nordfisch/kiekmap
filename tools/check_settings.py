"""Do the settings of ``config.py`` reach the container?

The check exists because of a failure that produced no error message at all. Until 14 August 2026
``deploy/docker-compose.yml`` listed four values under ``environment:``, and the rest fell back to
their defaults inside the container. It hit the import: photos arrived without their keyword,
without their credit line and without their provenance. Nothing failed, nothing was logged, and
393 green tests stood beside it -- a compose file is touched by no test.

The fix was ``env_file: ../.env``. **This script is what keeps it there.** Delete that line and
every test stays green; here the run turns red and names the settings that would go silent.

Three questions, and the second and third are worth as much as the first:

  1. Does every ``PHOTOMAP_*`` setting reach the backend container -- through ``env_file`` or
     because ``environment:`` sets it by name?
  2. Does ``environment:`` name only settings that actually exist? A typo there does nothing at
     all, quietly: ``PHOTOMAP_CORS_ORIGIN`` is not ``PHOTOMAP_CORS_ORIGINS``.
  3. Same for ``deploy/.env.example``, including the commented-out lines -- it is the template
     every new installation starts from, so a typo in it travels.

Deliberately a script and not a test, like its two neighbours in this folder: it reads files the
tests never see, and it is run by hand before a commit.

    python3 tools/check_settings.py

Two things it does *not* do, on purpose. It does not import ``app.config`` -- that would need the
backend's virtual environment, while the other tools here run on a plain ``python3``; the fields
are read with ``ast`` instead. And it does not parse YAML -- there is no PyYAML in the system
Python, and this is one file of our own with a known shape, so a targeted reader is honest here
and would not be for a stranger's file.
"""

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CONFIG = ROOT / "backend/app/config.py"
COMPOSE = ROOT / "deploy/docker-compose.yml"
ENV_EXAMPLE = ROOT / "deploy/.env.example"

#: Variables that belong to Compose itself, not to the application.
#:
#: ``PHOTOMAP_VERSION`` picks the image tag, ``PHOTOMAP_PROD_DATA`` the data directory of the Mac
#: overlay. Both are read by Compose before a container exists, so ``config.py`` knows neither --
#: and without this list they would be reported as typos.
COMPOSE_ONLY = {"PHOTOMAP_VERSION", "PHOTOMAP_PROD_DATA"}


def settings_names() -> set[str]:
    """The environment variable of every field of ``Settings``.

    ``env_prefix = "PHOTOMAP_"`` in the model config, so the name is the field in upper case.
    """
    tree = ast.parse(CONFIG.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "Settings":
            return {
                f"PHOTOMAP_{item.target.id.upper()}"
                for item in node.body
                if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name)
            }
    raise SystemExit(f"Keine Klasse Settings in {CONFIG.relative_to(ROOT)} gefunden.")


def backend_service() -> str:
    """The lines of the ``backend:`` service, up to the next one at the same indent."""
    text = COMPOSE.read_text(encoding="utf-8")
    match = re.search(r"^  backend:\n(.*?)(?=^  \w+:|\Z)", text, re.M | re.S)
    if match is None:
        raise SystemExit(f"Kein Dienst backend: in {COMPOSE.relative_to(ROOT)} gefunden.")
    return match.group(1)


def env_names(text: str) -> set[str]:
    """Every ``PHOTOMAP_*`` mentioned on the left of a colon or an equals sign.

    Commented-out lines count too: in the template they are documentation, and a typo in them is
    read by whoever sets up the next device.
    """
    return set(re.findall(r"^\s*#?\s*(PHOTOMAP_[A-Z_]+)\s*[:=]", text, re.M))


def main() -> int:
    known = settings_names()
    service = backend_service()
    has_env_file = re.search(r"^\s+env_file:", service, re.M) is not None
    in_environment = env_names(service)

    problems: list[str] = []

    # 1. Reachable?
    if has_env_file:
        print("  env_file        vorhanden -- die ganze .env erreicht den Container")
    else:
        unreachable = sorted(known - in_environment)
        print("  env_file        FEHLT")
        if unreachable:
            problems.append(
                "Ohne env_file fallen diese Einstellungen im Container still auf ihre "
                "Vorgabe zurueck:\n    " + "\n    ".join(unreachable)
            )

    # 2. and 3. Names that lead nowhere.
    for label, names, allowed in (
        ("docker-compose.yml", in_environment, known),
        (".env.example", env_names(ENV_EXAMPLE.read_text(encoding="utf-8")), known | COMPOSE_ONLY),
    ):
        if unknown := sorted(names - allowed):
            problems.append(
                f"In {label} stehen Namen, die keine Einstellung sind (Tippfehler wirkt "
                "folgenlos):\n    " + "\n    ".join(unknown)
            )

    print(f"  Einstellungen   {len(known)} in config.py, {len(in_environment)} fest gesetzt")

    if not problems:
        print("Jede Einstellung erreicht den Container.")
        return 0
    print()
    for problem in problems:
        print(f"  {problem}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
