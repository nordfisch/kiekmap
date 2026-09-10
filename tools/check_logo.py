#!/usr/bin/env python3

"""Does this commit carry the real coat of arms?

    python3 tools/check_logo.py

``frontend/public/logo.png`` is a placeholder, drawn by ``tools/build_logo.py``. Setting a device
up replaces it with the municipal coat of arms, and from then on it is a modified tracked file that
rides along with the next ``git add -A``.

**That is a legal problem, not an untidy one.** A municipal coat of arms is free of copyright as an
official work, but its *use* is governed by the municipality -- permission for the local museum is
not permission for everybody who clones a public repository. See ``docs/developer/decisions.md``,
point 21.

**It happened twice before this check existed:** once cleared up in ``6d47d36``, and again on
8 September 2026, when the file had to be taken back out of a commit that was already pushed. A
warning in ``docs/museum/adaption.md`` prevented neither.

**This reads the index, not the working tree**, and that distinction is the whole design. On a
machine that sets a device up, the working tree *should* hold the real crest -- ``make release``
bakes it into the frontend image from there. A check on the working tree would refuse every commit
on that machine, and would be switched off within the day.

**The way past it needs no exception:** a staged change is allowed when ``tools/build_logo.py`` is
staged with it. That is the one legitimate reason for the placeholder to change -- somebody
improved the generator -- and it leaves nothing to keep in step, no recorded hash and no
environment variable to remember. It guards against the accident, not against somebody determined;
``git commit --no-verify`` was always there.

Hook only. It needs an index, so it is not part of ``make check``: that answers whether the tree is
right, this answers what a commit carries.
"""

import subprocess
import sys

LOGO = "frontend/public/logo.png"
GENERATOR = "tools/build_logo.py"


def staged() -> list[str] | None:
    """The paths this commit changes. ``None`` when there is no repository to ask."""
    try:
        done = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return done.stdout.split()


def main() -> int:
    paths = staged()
    if paths is None:
        print("  no repository to ask -- nothing checked")
        return 0

    if LOGO not in paths:
        print(f"  {LOGO} untouched by this commit")
        return 0

    if GENERATOR in paths:
        print(f"  {LOGO} changed together with {GENERATOR} -- a new placeholder")
        return 0

    print(f"{LOGO} is staged, and {GENERATOR} is not.", file=sys.stderr)
    print(file=sys.stderr)
    print(
        "That file is a placeholder. A real coat of arms must not go into this repository:\n"
        "  it is free of copyright, but the municipality governs its use, and permission for\n"
        "  one museum is not permission for everybody who clones this.\n"
        "\n"
        "  Keep the crest in the working tree -- that is where `make release` takes it from --\n"
        "  and out of the commit:\n"
        "\n"
        f"      git restore --staged {LOGO}\n"
        "\n"
        f"  Changing the placeholder itself is fine: stage {GENERATOR} with it.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
