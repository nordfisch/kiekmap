#!/usr/bin/env python3

"""Does the documented command line still match the one that exists?

    python3 tools/check_cli.py

``docs/museum/collection.md`` is the page a second museum works from when it fills its collection
for the first time, and its heart is a table of every command. A table is a second copy of what
``backend/app/cli.py`` already says, and the module docstring of that file is a third. Three copies
of one list, and two of them are read by people who cannot see the code.

The failure this prevents is the one ``check_settings.py`` was written for as well: nothing breaks.
A command renamed in ``cli.py`` leaves 400 green tests behind it, a page that names something which
no longer exists, and a volunteer typing it at two in the afternoon with the museum waiting.

Three sources, one question -- does every command appear in all of them?

  1. ``main()`` in ``backend/app/cli.py``: every ``add_parser`` and the ``add_argument`` calls that
     belong to it. This is the truth; the other two are checked against it.
  2. The module docstring of the same file, which lists the commands for ``--help``.
  3. The table in the documentation page, in the German half as well -- command names are English
     in both, because they are what gets typed.

**The table is marked, not guessed.** An HTML comment above it says which table is meant:

    <!-- cli-table -->

Without the marker the check would have to recognise a command table by its shape, and the first
settings table with a backtick in its left column would be read as one. The same carrier as in
``check_translations.py``, and for the same reason: GitHub and MkDocs both render it as nothing.

Deliberately a script and not a test, like its neighbours here: it reads documentation, and it runs
on a plain ``python3``. ``ast`` rather than importing ``app.cli`` -- that would need the backend's
virtual environment, and it would execute the module to read a list.
"""

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CLI = ROOT / "backend/app/cli.py"
PAGES = ("docs/museum/collection.md", "docs/museum/collection.de.md")

#: The comment that says the next table is the command reference.
TABLE_MARKER = "<!-- cli-table -->"

#: A line of the docstring that offers a command: four spaces, the call, the command.
DOCSTRING_COMMAND = re.compile(r"^\s+python -m app\.cli\s+(\S+)", re.M)

#: Everything between backticks.
CODE_SPAN = re.compile(r"`([^`]+)`")


def normalised(token: str) -> str:
    """The bare name of an argument, as ``argparse`` knows it.

    The page writes a positional in angle brackets and may put a placeholder behind a switch --
    ``<path>``, ``--distance N``. Both are the same argument the code declares as ``path`` and
    ``--distance``.
    """
    return token.split()[0].strip("<>[]").rstrip("…").strip() if token.split() else ""


def from_code() -> dict[str, set[str]]:
    """Every command of ``main()`` with the arguments it declares.

    Read from the assignments rather than from a list: ``p_import = commands.add_parser("import")``
    names the command, and ``p_import.add_argument("path")`` below it names its argument. The
    variable is what ties the two together, which is why the walk keeps it.
    """
    tree = ast.parse(CLI.read_text(encoding="utf-8"))
    main = next(
        (node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "main"),
        None,
    )
    if main is None:
        raise SystemExit(f"No function main() in {CLI.relative_to(ROOT)}.")

    by_variable: dict[str, str] = {}
    commands: dict[str, set[str]] = {}

    for node in ast.walk(main):
        call = node.value if isinstance(node, ast.Assign | ast.Expr) else None
        if not isinstance(call, ast.Call) or not isinstance(call.func, ast.Attribute):
            continue
        if not call.args or not isinstance(call.args[0], ast.Constant):
            continue
        name = call.args[0].value
        if not isinstance(name, str):
            continue

        if call.func.attr == "add_parser" and isinstance(node, ast.Assign):
            target = node.targets[0]
            if isinstance(target, ast.Name):
                by_variable[target.id] = name
                commands[name] = set()
        elif call.func.attr == "add_argument" and isinstance(call.func.value, ast.Name):
            if command := by_variable.get(call.func.value.id):
                commands[command].add(normalised(name))

    return commands


def from_docstring() -> set[str]:
    """The commands the module docstring offers, which is what ``--help`` prints."""
    return set(DOCSTRING_COMMAND.findall(ast.get_docstring(ast.parse(CLI.read_text())) or ""))


def from_page(path: Path) -> dict[str, set[str]]:
    """The commands of the marked table, with the arguments its second column names.

    The table is the block of ``|`` lines after the marker; the first blank line ends it. Header
    and separator carry no code span in their first cell and fall out by themselves.
    """
    if not path.is_file():
        raise SystemExit(f"{path.relative_to(ROOT)} does not exist.")
    text = path.read_text(encoding="utf-8")
    if TABLE_MARKER not in text:
        raise SystemExit(f"{path.relative_to(ROOT)} carries no {TABLE_MARKER}.")

    rows: dict[str, set[str]] = {}
    for line in text.split(TABLE_MARKER, 1)[1].splitlines():
        if not line.strip():
            if rows:
                break
            continue
        if not line.lstrip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        named = CODE_SPAN.findall(cells[0])
        if not named:
            continue
        arguments = {normalised(span) for span in CODE_SPAN.findall(cells[1])}
        rows[normalised(named[0])] = {argument for argument in arguments if argument}
    return rows


def main() -> int:
    code = from_code()
    problems: list[str] = []

    if missing := sorted(code.keys() - from_docstring()):
        problems.append(
            "The docstring of cli.py, which is what --help prints, does not list:"
            "\n    " + "\n    ".join(missing)
        )
    if unknown := sorted(from_docstring() - code.keys()):
        problems.append(
            "The docstring of cli.py names commands that do not exist:\n    "
            + "\n    ".join(unknown)
        )

    for name in PAGES:
        page = from_page(ROOT / name)
        if missing := sorted(code.keys() - page.keys()):
            problems.append(f"{name} has no row for:\n    " + "\n    ".join(missing))
        if unknown := sorted(page.keys() - code.keys()):
            problems.append(
                f"{name} names commands that do not exist (a volunteer would type them):"
                "\n    " + "\n    ".join(unknown)
            )
        for command in sorted(code.keys() & page.keys()):
            if gap := sorted(code[command] - page[command]):
                problems.append(
                    f"{name}, row {command}: the code declares arguments the row does not name:"
                    "\n    " + "\n    ".join(gap)
                )
            if extra := sorted(page[command] - code[command]):
                problems.append(
                    f"{name}, row {command}: the row names arguments the code does not declare:"
                    "\n    " + "\n    ".join(extra)
                )

    arguments = sum(len(names) for names in code.values())
    print(f"  cli.py          {len(code)} commands, {arguments} arguments")
    print(f"  pages           {len(PAGES)} tables read")

    if not problems:
        print("The documented command line matches the one that exists.")
        return 0
    print()
    for problem in problems:
        print(f"  {problem}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
