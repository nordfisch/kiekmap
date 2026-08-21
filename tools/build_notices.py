#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Kalle Erlhoff
# SPDX-License-Identifier: Apache-2.0

"""Build the notice files that have to travel with each built artefact.

    python3 tools/build_notices.py          write them
    python3 tools/build_notices.py --check  fail if they are out of date

MIT and BSD ask for the same thing in almost the same words: the copyright notice and the licence
text go along with *every* copy, source or binary. A bundled ``index-*.js`` is a copy, and so is a
container image. Measured on 20 August 2026, the 1.4 MB frontend bundle carried exactly two
licence banners for the 35 packages inside it -- that is the gap this closes.

**Generated, not maintained.** A hand-written list is wrong three months later, and wrong in the
direction nobody checks. It is committed all the same, like a lock file: every build context stays
self-contained, and a dependency bump shows up in a diff where somebody sees it.

**One file per artefact, and it carries everything.** ``frontend/`` and ``backend/`` are separate
Docker build contexts, so neither can reach the LICENSE at the root of the repository. Rather than
move the contexts, each notice file opens with Kiekmap's own licence and NOTICE and continues with
the third parties. That satisfies section 4 of the Apache licence on its own.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FRONTEND = ROOT / "frontend"
BACKEND = ROOT / "backend"

TARGETS = {
    "Frontend": FRONTEND / "public" / "THIRD-PARTY.txt",
    "Backend": BACKEND / "THIRD-PARTY.txt",
}

#: Names a package may give its licence file. Matched against the start of the whole name, which
#: is why "LICENSE-MIT" and "COPYING.txt" both land.
LICENCE_FILE = re.compile(r"^(licen[cs]e|copying|notice)", re.I)

#: Canonical texts for packages that declare a licence but ship no file -- three of them today
#: (@protomaps/basemaps, pmtiles, murmurhash-js). Every use is marked as such in the output:
#: claiming a text came out of the package when it did not would be the same quiet untruth this
#: file exists against.
CANONICAL = {
    "MIT": """Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.""",
    "BSD-3-Clause": """Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors
   may be used to endorse or promote products derived from this software
   without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.""",
}


class Missing(Exception):
    """A package whose licence cannot be established at all. Never silently skipped."""


def licence_from_dir(folder: Path) -> str | None:
    """The licence text a package ships, or None.

    Searched recursively because Python wheels have moved it around: most put it under
    ``dist-info/licenses/``, some leave it directly in ``dist-info/``.
    """
    files = sorted(p for p in folder.rglob("*") if p.is_file() and LICENCE_FILE.match(p.name))
    if not files:
        return None
    return "\n\n".join(p.read_text(encoding="utf-8", errors="replace").strip() for p in files)


def resolve(name: str, version: str, spdx: str, folder: Path) -> tuple[str, bool]:
    """(licence text, whether it had to be reconstructed). Raises when neither is possible."""
    if (text := licence_from_dir(folder)) is not None:
        return text, False
    for key, canonical in CANONICAL.items():
        if spdx and key.lower() in spdx.lower():
            return canonical, True
    raise Missing(f"{name} {version}: weder Lizenzdatei noch bekannte Kennung ({spdx or '?'})")


# --- the two sides ----------------------------------------------------------


def npm_packages() -> list[tuple[str, str, str, Path]]:
    """Everything that ends up in the bundle -- production dependencies, transitively."""
    result = subprocess.run(
        ["npm", "ls", "--omit=dev", "--all", "--parseable"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        check=False,
    )
    found = []
    for line in sorted(set(result.stdout.split("\n"))):
        folder = Path(line)
        if "node_modules" not in line or not (folder / "package.json").is_file():
            continue
        data = json.loads((folder / "package.json").read_text(encoding="utf-8"))
        spdx = data.get("license") or ""
        if isinstance(spdx, dict):
            spdx = spdx.get("type", "")
        found.append((data["name"], data.get("version", ""), spdx, folder))
    if not found:
        raise Missing("frontend/node_modules fehlt -- bitte zuerst 'make deps'")
    return found


def site_packages() -> Path:
    candidates = sorted((BACKEND / ".venv" / "lib").glob("python3.*/site-packages"))
    if not candidates:
        raise Missing("backend/.venv fehlt -- bitte zuerst 'make venv'")
    return candidates[-1]


def requirement_name(requirement: str) -> str:
    """The bare name out of a dependency line.

    One place for it, because the two callers get the same string in different disguises:
    ``uvicorn[standard]>=0.32`` from the pyproject, ``pydantic!=1.8,>=1.7.4`` from a METADATA
    header. Splitting on a handful of separators looked right and quietly lost ten packages --
    ``!=`` breaks at the ``=`` and leaves ``pydantic!``, which matches nothing.
    """
    match = re.match(r"\s*([A-Za-z0-9][A-Za-z0-9._-]*)", requirement)
    return match.group(1) if match else ""


def metadata_of(dist_info: Path) -> dict:
    """The headers of a dist-info METADATA file. Repeated keys are collected."""
    fields: dict[str, list[str]] = {}
    for line in (dist_info / "METADATA").read_text(encoding="utf-8", errors="replace").split("\n"):
        if not line.strip():
            break  # the free-text description follows the headers
        if ": " in line and not line.startswith(" "):
            key, value = line.split(": ", 1)
            fields.setdefault(key, []).append(value.strip())
    return fields


def python_packages() -> list[tuple[str, str, str, Path]]:
    """Everything the backend image installs -- runtime dependencies, transitively.

    Walked from ``pyproject.toml`` rather than read off the venv, which also holds pytest and
    ruff. The image runs ``pip install .``, so only what that pulls in may appear here.
    """
    installed = {}
    for folder in site_packages().glob("*.dist-info"):
        fields = metadata_of(folder)
        name = fields["Name"][0]
        installed[name.lower().replace("_", "-")] = (name, fields, folder)

    text = (BACKEND / "pyproject.toml").read_text(encoding="utf-8")
    # Up to the ``]`` that starts a line -- not the first one anywhere. The first ``]`` in the
    # block sits inside ``uvicorn[standard]``, and cutting there left the list one entry long.
    block = re.search(r"^dependencies = \[(.*?)^\]", text, re.S | re.M).group(1)
    # The quoted entries, not the commas: "uvicorn[standard]>=0.32" carries a bracket and a
    # comparison, and splitting the block on commas leaves the quotes attached to the name.
    pending = [requirement_name(entry) for entry in re.findall(r'"([^"]+)"', block)]
    # uvicorn[standard] pulls these in; the extra marker hides them from Requires-Dist below.
    pending += ["uvloop", "httptools", "websockets", "python-dotenv", "watchfiles", "PyYAML"]

    seen, found = set(), []
    while pending:
        key = pending.pop().lower().replace("_", "-")
        if not key or key in seen or key not in installed:
            continue
        seen.add(key)
        name, fields, folder = installed[key]
        spdx = (fields.get("License-Expression") or fields.get("License") or [""])[0]
        if not spdx or len(spdx) > 60:
            klass = [c for c in fields.get("Classifier", []) if c.startswith("License ::")]
            spdx = "; ".join(k.split(":: ")[-1] for k in klass) or spdx[:60]
        found.append((name, fields["Version"][0], spdx, folder))
        for req in fields.get("Requires-Dist", []):
            if ";" in req and "extra" in req.split(";", 1)[1]:
                continue
            pending.append(requirement_name(req))
    return sorted(found, key=lambda row: row[0].lower())


# --- putting it together ----------------------------------------------------

RULE = "=" * 98
THIN = "-" * 98


def render(side: str, packages: list[tuple[str, str, str, Path]]) -> str:
    parts = [
        RULE,
        f"  Kiekmap -- Lizenzen der mitgelieferten Bestandteile ({side})",
        RULE,
        "",
        "Erzeugt von tools/build_notices.py. Nicht von Hand bearbeiten.",
        "",
        (ROOT / "NOTICE").read_text(encoding="utf-8").strip(),
        "",
        RULE,
        "  Kiekmap selbst: Apache License 2.0",
        RULE,
        "",
        (ROOT / "LICENSE").read_text(encoding="utf-8").strip(),
        "",
        RULE,
        f"  Software Dritter -- {len(packages)} Pakete",
        RULE,
    ]

    for name, version, spdx, folder in packages:
        text, reconstructed = resolve(name, version, spdx, folder)
        parts += ["", THIN, f"{name} {version}    {spdx or 'Kennung fehlt'}", THIN, ""]
        if reconstructed:
            parts += [
                "[Dieses Paket liefert keinen Lizenztext mit. Der folgende Text ist die",
                f" Standardfassung von {spdx}; die Kennung stammt aus seiner package.json.]",
                "",
            ]
        parts.append(text.strip())

    return "\n".join(parts).rstrip() + "\n"


def main() -> int:
    pruefen = "--check" in sys.argv
    veraltet = 0
    try:
        for side, target in TARGETS.items():
            packages = npm_packages() if side == "Frontend" else python_packages()
            content = render(side, packages)
            previous = target.read_text(encoding="utf-8") if target.is_file() else ""
            if previous != content:
                veraltet += 1
                if not pruefen:
                    target.write_text(content, encoding="utf-8")
            stand = "unveraendert" if previous == content else ("VERALTET" if pruefen else "neu")
            print(f"  {str(target.relative_to(ROOT)):40} {len(packages):3} Pakete  {stand}")
    except Missing as fehler:
        print(f"  {fehler}")
        return 1

    if pruefen and veraltet:
        print("Die Lizenzhinweise sind veraltet -- bitte 'make notices' laufen lassen.")
        return 1
    print("Jedes mitgelieferte Paket nennt seine Lizenz.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
