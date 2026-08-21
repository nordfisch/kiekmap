# SPDX-FileCopyrightText: 2026 Kalle Erlhoff
# SPDX-License-Identifier: Apache-2.0

"""Which comments are written in which language.

The rule is in CLAUDE.md: identifiers and comments in English, test files entirely in German.
Held only in part for a long time -- 338 German comments sat in 52 production files next to 687
English ones, and nobody could say whether that was getting better or worse.

Deliberately a script and **not a test**. The detection is a word-list heuristic; a test that
cries wolf over a technical term gets switched off within a month, and then nothing is watched
at all. Run it when you want an answer:

    python tools/language_check.py           only what breaks the rule
    python tools/language_check.py --all     every file with its counts
"""

import argparse
import ast
import io
import re
import subprocess
import sys
import tokenize
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Function words, not vocabulary: they are what tells the two languages apart in a sentence that
# is otherwise full of identifiers, file names and English technical terms.
GERMAN = set(
    "der die das den dem des und nicht ist sind ein eine einen einem wird werden dass wenn weil"
    " fuer für sich sonst damit aber noch nur dann kann muss man auch schon nach vom von zum zur"
    " beim mit ohne wie was wer wo hat haben hier dort jede jeder jedes keine kein nichts als sie"
    " es im in am an auf steht stehen liegt heisst heißt gibt macht laesst lässt waere wäre"
    " haette hätte wuerde würde".split()
)
ENGLISH = set(
    "the of is a an and that not it to in on for with this these those there here what which when"
    " where who does do has have was were be been are as by from or if then than can may must"
    " should would could its their our your all any each no nothing only just also still"
    " even".split()
)


#: Quoted material: examples, values, messages. Not the prose being judged.
#:
#: A German example inside an English comment is explicitly wanted (CLAUDE.md), and a German
#: setting value is not a sentence somebody wrote in German -- it is the thing the sentence is
#: about. Without this the checker reported a violation on config.py that could only have been
#: fixed by falsifying the example.
QUOTED = re.compile("``.*?``|\"[^\"]*\"|„[^“]*“|'[^']*'", re.S)


def language(text: str) -> str | None:
    """ "de", "en", or None when the text carries no function words either way."""
    words = re.findall(r"[a-zA-ZäöüÄÖÜß]+", QUOTED.sub(" ", text).lower())
    german = sum(1 for w in words if w in GERMAN)
    english = sum(1 for w in words if w in ENGLISH)
    if german == english:
        return None
    return "de" if german > english else "en"


def python_texts(path: Path) -> list[str]:
    source = path.read_text(encoding="utf-8")
    found = []
    try:
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef):
                if doc := ast.get_docstring(node):
                    found.append(doc)
    except SyntaxError:
        pass
    try:
        for token in tokenize.generate_tokens(io.StringIO(source).readline):
            if token.type == tokenize.COMMENT and not token.string.startswith("#!"):
                found.append(token.string)
    except (tokenize.TokenError, IndentationError):
        pass
    return found


def typescript_texts(path: Path) -> list[str]:
    source = path.read_text(encoding="utf-8")
    found = [m.group(1) for m in re.finditer(r"/\*\*?(.*?)\*/", source, re.S)]
    # Line comments only outside block comments, or every line of a JSDoc block counts twice.
    without_blocks = re.sub(r"/\*.*?\*/", "", source, flags=re.S)
    for line in without_blocks.split("\n"):
        # The lookbehind keeps "https://" and other URLs out.
        match = re.search(r"(?<!:)//\s*(.+)", line)
        if match and not line.strip().startswith("import"):
            found.append(match.group(1))
    return found


def is_test(path: str) -> bool:
    return "/tests/" in path or ".test." in path or Path(path).name.startswith("test_")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--all", action="store_true", help="jede Datei zeigen, nicht nur Verstoesse"
    )
    args = parser.parse_args()

    listed = subprocess.run(
        ["git", "ls-files"], capture_output=True, text=True, cwd=ROOT
    ).stdout.split("\n")
    files = [f for f in listed if f.endswith((".py", ".ts", ".tsx")) and "node_modules" not in f]

    breaks: list[tuple[str, int, int]] = []
    total = {"de": 0, "en": 0}

    for name in sorted(files):
        path = ROOT / name
        if not path.is_file():
            continue
        texts = python_texts(path) if name.endswith(".py") else typescript_texts(path)
        counted = {"de": 0, "en": 0}
        for text in texts:
            if found := language(text):
                counted[found] += 1
                total[found] += 1
        # A test file should be German throughout, everything else English.
        wrong = counted["en"] if is_test(name) else counted["de"]
        if wrong:
            breaks.append((name, wrong, counted["de"] + counted["en"]))
        if args.all and any(counted.values()):
            print(f"  {name:56} {counted['de']:4} deutsch  {counted['en']:4} englisch")

    if args.all:
        print()
    print(f"Kommentare insgesamt: {total['de']} deutsch, {total['en']} englisch")

    if not breaks:
        print("Keine Datei bricht die Sprachregelung.")
        return 0

    print(f"\n{len(breaks)} Dateien brechen die Regel ({sum(b[1] for b in breaks)} Kommentare):")
    for name, wrong, all_of_them in sorted(breaks, key=lambda b: -b[1]):
        richtung = "englisch in einer Testdatei" if is_test(name) else "deutsch im Produktivcode"
        print(f"  {name:56} {wrong:4} von {all_of_them:4}   {richtung}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
