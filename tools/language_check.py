# SPDX-FileCopyrightText: 2026 Kalle Erlhoff
# SPDX-License-Identifier: Apache-2.0

"""Which comments are written in which language -- and whether the prose spells its umlauts.

The rule is in CLAUDE.md: identifiers and comments in English, test files entirely in German.
Held only in part for a long time -- 338 German comments sat in 52 production files next to 687
English ones, and nobody could say whether that was getting better or worse.

Deliberately a script and **not a test**. The detection is a word-list heuristic; a test that
cries wolf over a technical term gets switched off within a month, and then nothing is watched
at all. Run it when you want an answer:

    python tools/language_check.py           only what breaks the rule
    python tools/language_check.py --all     every file with its counts

Two more questions concern the prose, and both went unwatched far longer. German documentation
writes its umlauts out; nothing read the documentation, so nothing noticed when two files drifted
to 900 transcribed words. English documentation must be free of German left over from the switch
of August 2026. See ``transcribed_in_prose`` and ``german_in_english_prose``.
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

#: A German opening quote closed with a straight mark -- the form this project actually uses.
#: ``QUOTED`` expects „…“ and would otherwise pair the straight mark with the *next* one, leaving
#: the quote itself bare. Stripped before ``QUOTED`` everywhere quoted material has to disappear.
GERMAN_QUOTE = re.compile('„[^“”"]*[“”"]')


def strip_quoted(text: str) -> str:
    """Text with every quotation and code span removed -- what is left is the prose itself."""
    return QUOTED.sub(" ", GERMAN_QUOTE.sub(" ", text))


def language(text: str) -> str | None:
    """ "de", "en", or None when the text carries no function words either way."""
    words = re.findall(r"[a-zA-ZäöüÄÖÜß]+", strip_quoted(text).lower())
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


#: Transcriptions that are never a German word in their own right. Deliberately short: the
#: checker runs in the commit hook, and one false alarm is enough for somebody to switch it off.
#: "neue", "Quelle", "dauert", "Feuerwehr" carry a real ``ue`` and are not in here.
TRANSCRIBED = re.compile(
    r"\b\w*(fuer|ueber|waere|haette|koenn|moeglich|naechst|zurueck|gehoert|laeuft|laesst"
    r"|muess|duerf|schliess|heisst|weiss|gross|groess|strass|dreissig|zaehl|aender|waehrend"
    r"|faellt|haeng|spaet|erklaer|vollstaendig|gemaess|pruef|fuenf|zurueck)\w*",
    re.I,
)

#: Prose for people, split by its readers: German for visitors, the museum team and operators,
#: English for developers. Each side needs a different check -- transcribed umlauts on the German
#: side, leftover German on the English side.
#:
#: **Not** ``.github/workflows/``. A workflow is closer to a shell script than to a manual -- and
#: shell scripts transcribe their umlauts. ``.github/`` as a whole stood here until the first
#: workflow arrived and the checker rightly complained about it.
#:
#: The five developer documents at the end move to ``ENGLISH_PROSE`` once they are translated. A
#: file being converted right now belongs in neither list: it is half of each, and both checks
#: would be right to complain.
GERMAN_PROSE = (
    "docs/adaption.md",
    "docs/history.md",
    "docs/index.md",
    "docs/licensing.md",
    "docs/operations.md",
    "docs/usermanual.md",
    ".github/ISSUE_TEMPLATE/",
    ".github/pull_request_template.md",
    "README.md",
    "CHANGELOG.md",
    "SECURITY.md",
    "CODE_OF_CONDUCT.md",
    "AUTHORS",
)

#: One list with a flag would not do here: an English file passes the German check for the wrong
#: reason -- it has no transcription because it has no German -- so silence there proves nothing.
ENGLISH_PROSE: tuple[str, ...] = (
    "docs/architecture.md",
    "docs/decisions.md",
    "docs/development.md",
    "CLAUDE.md",
    "CONTRIBUTING.md",
)


def transcribed_in_prose(path: Path) -> list[tuple[int, str]]:
    """Lines of German prose that spell an umlaut out -- ``ue`` where ``ü`` belongs.

    The rule (CLAUDE.md): umlauts are written normally in texts for people, transcribed in source
    code, shell scripts and commit messages. Documentation is a text for people, and this used to
    be nobody's job to check -- by 21 August 2026, ``decisions.md`` and ``history.md`` had drifted
    to 900 transcribed words between them while every other file stayed clean.

    Three things are not prose and are skipped: fenced blocks and inline code, where identifiers
    and commands live and the transcription is correct; and quoted material, because CLAUDE.md
    quotes a transcribed message as its own example of the rule.
    """
    hits, fenced = [], False
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        bare = strip_quoted(re.sub(r"`[^`]*`", " ", line))
        if found := TRANSCRIBED.findall(bare):
            hits.append((number, ", ".join(sorted({f for f in found}))))
    return hits


def german_in_english_prose(path: Path) -> list[tuple[int, str]]:
    """Paragraphs of an English document that are still German -- a leftover of the switch.

    The other half of the language map, and the reason ``GERMAN_PROSE`` and ``ENGLISH_PROSE`` are
    two lists. Judged per paragraph, not per line: one line rarely carries enough function words
    to tell the languages apart, and ``language`` returns None on a tie.

    Fenced blocks, inline code and quoted material are skipped for the same reason as above --
    a German example inside an English text is the subject, not the prose.
    """
    text = path.read_text(encoding="utf-8")
    hits: list[tuple[int, str]] = []
    paragraph: list[str] = []
    fenced, start = False, 0

    def flush() -> None:
        if paragraph and language(" ".join(paragraph)) == "de":
            hits.append((start, " ".join(paragraph)[:60].strip()))
        paragraph.clear()

    # The trailing empty line closes the last paragraph without repeating the flush after the loop.
    for number, line in enumerate(text.splitlines() + [""], 1):
        if line.lstrip().startswith("```"):
            flush()
            fenced = not fenced
        elif fenced or not line.strip():
            flush()
        else:
            if not paragraph:
                start = number
            paragraph.append(re.sub(r"`[^`]*`", " ", line))
    return hits


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

    umschrieben = [
        (name, hits)
        for name in sorted(
            f
            for f in listed
            if f.startswith(GERMAN_PROSE) and f.endswith((".md", ".yml", "AUTHORS"))
        )
        if (ROOT / name).is_file() and (hits := transcribed_in_prose(ROOT / name))
    ]

    deutsch_geblieben = [
        (name, hits)
        for name in sorted(f for f in listed if f.startswith(ENGLISH_PROSE) and f.endswith(".md"))
        if (ROOT / name).is_file() and (hits := german_in_english_prose(ROOT / name))
    ]

    if not breaks and not umschrieben and not deutsch_geblieben:
        print("Keine Datei bricht die Sprachregelung.")
        return 0

    if breaks:
        kommentare = sum(b[1] for b in breaks)
        print(f"\n{len(breaks)} Dateien brechen die Regel ({kommentare} Kommentare):")
        for name, wrong, all_of_them in sorted(breaks, key=lambda b: -b[1]):
            richtung = (
                "englisch in einer Testdatei" if is_test(name) else "deutsch im Produktivcode"
            )
            print(f"  {name:56} {wrong:4} von {all_of_them:4}   {richtung}")

    if umschrieben:
        zeilen = sum(len(h) for _, h in umschrieben)
        print(f"\n{zeilen} Zeilen Prosa schreiben einen Umlaut aus, in {len(umschrieben)} Dateien:")
        for name, hits in umschrieben:
            for number, woerter in hits[:5]:
                print(f"  {name}:{number}  {woerter}")
            if len(hits) > 5:
                print(f"  {name}  … und {len(hits) - 5} weitere Zeilen")
        print("\n  In deutscher Doku werden Umlaute geschrieben, nicht umschrieben -- das")
        print("  sind Texte fuer Menschen. Code, Bezeichner und Zitate sind ausgenommen.")

    if deutsch_geblieben:
        absaetze = sum(len(h) for _, h in deutsch_geblieben)
        print(
            f"\n{absaetze} Absaetze stehen deutsch in einer englischen Datei, in "
            f"{len(deutsch_geblieben)} Dateien:"
        )
        for name, hits in deutsch_geblieben:
            for number, anfang in hits[:5]:
                print(f"  {name}:{number}  {anfang} …")
            if len(hits) > 5:
                print(f"  {name}  … und {len(hits) - 5} weitere Absaetze")
        print("\n  Entwicklerdoku ist englisch, Doku fuer Museum und Betrieb deutsch. Was hier")
        print("  steht, ist ein Rest der Umstellung.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
