"""Do the settings of ``config.py`` reach the container?

The check exists because of a failure that produced no error message at all. Until 14 August 2026
``deploy/docker-compose.yml`` listed four values under ``environment:``, and the rest fell back to
their defaults inside the container. It hit the import: photos arrived without their keyword,
without their credit line and without their provenance. Nothing failed, nothing was logged, and
393 green tests stood beside it -- a compose file is touched by no test.

The fix was ``env_file: ../.env``. **This script is what keeps it there.** Delete that line and
every test stays green; here the run turns red and names the settings that would go silent.

Four questions, and only the first is about the compose file:

  1. Does every ``KIEKMAP_*`` setting reach the backend container -- through ``env_file`` or
     because ``environment:`` sets it by name?
  2. Does ``environment:`` name only settings that actually exist? A typo there does nothing at
     all, quietly: ``KIEKMAP_CORS_ORIGIN`` is not ``KIEKMAP_CORS_ORIGINS``.
  3. Same for ``deploy/.env.example``, including the commented-out lines -- it is the template
     every new installation starts from, so a typo in it travels.
  4. **And the same for the real ``.env``**, when there is one. It is not versioned, so it is the
     one file nobody reviews -- and a key that leads nowhere there is invisible in exactly the way
     the others are. The rename of 15 August 2026 is what put this question here: every setting
     carried a new prefix afterwards, and an untouched ``.env`` would have gone on being read
     without a word, with the whole configuration silently on its defaults.

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
#: Not versioned, and therefore the file nobody ever reviews. Checked when it is there.
ENV_LOCAL = ROOT / ".env"

#: Variables that belong to Compose itself, not to the application.
#:
#: ``KIEKMAP_VERSION`` picks the image tag, ``KIEKMAP_PROD_DATA`` the data directory of the Mac
#: overlay. Both are read by Compose before a container exists, so ``config.py`` knows neither --
#: and without this list they would be reported as typos.
COMPOSE_ONLY = {"KIEKMAP_VERSION", "KIEKMAP_PROD_DATA"}


def settings_names() -> set[str]:
    """The environment variable of every field of ``Settings``.

    ``env_prefix = "KIEKMAP_"`` in the model config, so the name is the field in upper case.
    """
    tree = ast.parse(CONFIG.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "Settings":
            return {
                f"KIEKMAP_{item.target.id.upper()}"
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
    """Every ``KIEKMAP_*`` mentioned on the left of a colon or an equals sign.

    Commented-out lines count too: in the template they are documentation, and a typo in them is
    read by whoever sets up the next device.
    """
    return set(re.findall(r"^\s*#?\s*(KIEKMAP_[A-Z_]+)\s*[:=]", text, re.M))


def all_names(text: str) -> set[str]:
    """Every key in an env file, whatever its prefix."""
    return set(re.findall(r"^\s*#?\s*([A-Z][A-Z0-9_]*)\s*=", text, re.M))


def strayed(names: set[str], allowed: set[str]) -> list[str]:
    """Keys that name a setting we know -- under a prefix we no longer use.

    Deliberately narrow. A ``.env`` may hold whatever else its owner put there, and complaining
    about that would be noise. But ``…_IMPORT_TAGS`` under a foreign prefix is not someone else's
    variable: it is ours, misspelled, and it does nothing.
    """
    suffixes = {name.split("_", 1)[1] for name in allowed if "_" in name}
    return sorted(
        name for name in names - allowed if "_" in name and name.split("_", 1)[1] in suffixes
    )


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

    # 4. The unversioned .env -- the one file nobody else reviews.
    if ENV_LOCAL.is_file():
        local = all_names(ENV_LOCAL.read_text(encoding="utf-8"))
        allowed = known | COMPOSE_ONLY
        bekannt = len(local & allowed)
        print(f"  .env            vorhanden, {bekannt} von {len(local)} Schluesseln bekannt")
        if verirrt := strayed(local, allowed):
            problems.append(
                "In der .env stehen Einstellungen unter einem Praefix, den es nicht mehr gibt. "
                "Sie werden gelesen wie Luft, und alles faellt still auf seine Vorgabe "
                "zurueck:\n    " + "\n    ".join(verirrt)
            )
        ours = {name for name in local if name.startswith("KIEKMAP_")}
        if unknown := sorted(ours - allowed):
            problems.append(
                "In der .env stehen Namen mit richtigem Praefix, die keine Einstellung sind "
                "(Tippfehler wirkt folgenlos):\n    " + "\n    ".join(unknown)
            )
    else:
        print("  .env            nicht vorhanden -- uebersprungen")

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
