"""Which comments are written in which language -- and whether the prose spells its umlauts.

The rule is in CLAUDE.md: identifiers, comments and test files in English.
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


#: Formats whose comments start at a ``#`` and run to the end of the line.
#:
#: Nothing exotic among them, and that is the point: every one of these survived the switch of
#: August 2026 in German, because the checker read only ``.py``, ``.ts`` and ``.tsx``. The gap was
#: found on 31 August 2026, by a person reading the repository rather than by any check.
HASH_COMMENT = (
    ".conf",
    ".dockerignore",
    ".gitignore",
    ".ini",
    ".sh",
    ".toml",
    ".yml",
    "Dockerfile",
    "docker-entrypoint.sh",
    "pre-commit",
    "Makefile",
)

#: Formats whose comments are ``/* … */``. CSS carries more prose than one would think: the kiosk
#: layout is explained in the stylesheet, because that is where the grid stands.
BLOCK_COMMENT = (".css",)


def hash_comment_texts(path: Path) -> list[str]:
    """Comment blocks of a ``#`` format -- consecutive lines are one text.

    Per block rather than per line: one line rarely carries enough function words to tell the
    languages apart, and ``language`` returns None on a tie. The shebang is skipped, and so is a
    line that only draws a rule.
    """
    found: list[str] = []
    block: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("#") and not stripped.startswith("#!"):
            text = stripped.lstrip("#").strip()
            if text and set(text) - set("-=_ "):
                block.append(text)
            continue
        if block:
            found.append(" ".join(block))
            block = []
    if block:
        found.append(" ".join(block))
    return found


def block_comment_texts(path: Path) -> list[str]:
    source = path.read_text(encoding="utf-8")
    return [m.group(1) for m in re.finditer(r"/\*(.*?)\*/", source, re.S)]


def texts_of(name: str, path: Path) -> list[str] | None:
    """Every comment of a file, or None when this is not a format we can read."""
    if name.endswith(".py"):
        return python_texts(path)
    if name.endswith((".ts", ".tsx")):
        return typescript_texts(path)
    if name.endswith(BLOCK_COMMENT):
        return block_comment_texts(path)
    if name.endswith(HASH_COMMENT):
        return hash_comment_texts(path)
    return None


def is_test(path: str) -> bool:
    return "/tests/" in path or ".test." in path or Path(path).name.startswith("test_")


#: Test files that have not made the switch to English yet -- checked in neither language.
#:
#: Until 31 August 2026 the rule was the other way round: test files had to be German throughout,
#: because a test name here is a sentence of specification. Point 71 reverses that; the sentence
#: stays a sentence, it is only English now. **The tuple is empty, and that is the point** -- it
#: is kept so that the next conversion has somewhere to put its files.
TESTS_IN_TRANSITION: tuple[str, ...] = ()


#: Transcriptions that are never a German word in their own right. Deliberately short: the
#: checker runs in the commit hook, and one false alarm is enough for somebody to switch it off.
#: "neue", "Quelle", "dauert", "Feuerwehr" carry a real ``ue`` and are not in here.
TRANSCRIBED = re.compile(
    r"\b\w*(fuer|ueber|waere|haette|koenn|moeglich|naechst|zurueck|gehoert|laeuft|laesst"
    r"|muess|duerf|schliess|heisst|weiss|gross|groess|strass|dreissig|zaehl|aender|waehrend"
    r"|faellt|haeng|spaet|erklaer|vollstaendig|gemaess|pruef|fuenf|zurueck)\w*",
    re.I,
)

#: Which files are prose for people rather than source.
#:
#: **Not** ``.github/workflows/``. A workflow is closer to a shell script than to a manual -- and
#: shell scripts transcribe their umlauts. ``.github/`` as a whole stood here until the first
#: workflow arrived and the checker rightly complained about it.
PROSE_DIRECTORIES = ("docs/", ".github/ISSUE_TEMPLATE/")
PROSE_FILES = (
    ".github/pull_request_template.md",
    "AUTHORS",
    "CHANGELOG.md",
    "CLAUDE.md",
    "CODE_OF_CONDUCT.md",
    "CONTRIBUTING.md",
    "README.md",
    "SECURITY.md",
    "seed/README.md",
)

#: Prose that has not made the switch yet -- checked in neither language while it is half of each.
#:
#: This is the to-do list of the change of 31 August 2026, and it has to reach empty. Every entry
#: removed is one file that from then on is checked in its target language. See issue #31.
IN_TRANSITION = (
    "CHANGELOG.md",
    "docs/adaption.md",
    "docs/index.md",
    "docs/licensing.md",
    "docs/operations.md",
    "docs/usermanual.md",
)


def is_prose(path: str) -> bool:
    if path.startswith(IN_TRANSITION):
        return False
    if path.startswith(PROSE_DIRECTORIES):
        return path.endswith((".md", ".yml"))
    # A translation beside a prose file is prose as well. Named by the suffix rather than by a
    # second entry in the list: ``README.de.md`` would otherwise be checked in no language at all,
    # which is exactly the state the suffix rule exists to prevent.
    if path.endswith(".de.md"):
        return path[: -len(".de.md")] + ".md" in PROSE_FILES
    return path in PROSE_FILES


def prose_language(path: str) -> str:
    """Which language a prose file has to be written in. **The file name says it.**

    ``operations.de.md`` is German, ``operations.md`` is English. Until 31 August 2026 this was two
    hand-kept lists, and a new file belonged to whichever one somebody remembered to add it to. A
    suffix cannot be forgotten: it is in the name.

    Each side needs its own check. Transcribed umlauts betray a German text written like source
    code; leftover German paragraphs betray an English text that was never finished. One list with
    a flag would not do -- an English file passes the umlaut check for the wrong reason, because it
    has nothing German that could be transcribed, so silence there proves nothing.
    """
    return "de" if path.endswith(".de.md") else "en"


def transcribed_in_prose(path: Path) -> list[tuple[int, str]]:
    """Lines of German prose that spell an umlaut out -- ``ue`` where ``ü`` belongs.

    The rule (CLAUDE.md): umlauts are written normally in texts for people, transcribed in source
    code, shell scripts and commit messages. Documentation is a text for people, and this used to
    be nobody's job to check -- by 21 August 2026, ``decisions.md`` and the history had drifted to
    900 transcribed words between them while every other file stayed clean.

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

    The other half of the suffix rule: ``prose_language`` says English, this asks whether the file
    is. Judged per paragraph, not per line: one line rarely carries enough function words to tell
    the languages apart, and ``language`` returns None on a tie.

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
        "--all", action="store_true", help="show every file, not only the offenders"
    )
    args = parser.parse_args()

    listed = subprocess.run(
        ["git", "ls-files"], capture_output=True, text=True, cwd=ROOT
    ).stdout.split("\n")
    # Prose is judged elsewhere, by its file name, and a file still being converted is judged
    # nowhere. Without this a .yml under docs/ or in the issue templates would be counted twice
    # and reported in two different ways.
    files = [
        f
        for f in listed
        if "node_modules" not in f and not is_prose(f) and not f.startswith(IN_TRANSITION)
    ]

    breaks: list[tuple[str, int, int]] = []
    total = {"de": 0, "en": 0}

    for name in sorted(files):
        path = ROOT / name
        if not path.is_file():
            continue
        texts = texts_of(name, path)
        if texts is None:
            continue
        counted = {"de": 0, "en": 0}
        for text in texts:
            if found := language(text):
                counted[found] += 1
                total[found] += 1
        # English throughout, tests included -- except what is still being converted.
        wrong = 0 if is_test(name) and name.startswith(TESTS_IN_TRANSITION) else counted["de"]
        if wrong:
            breaks.append((name, wrong, counted["de"] + counted["en"]))
        if args.all and any(counted.values()):
            print(f"  {name:56} {counted['de']:4} German  {counted['en']:4} English")

    if args.all:
        print()
    print(f"Comments in total: {total['de']} German, {total['en']} English")

    prose = sorted(f for f in listed if is_prose(f) and (ROOT / f).is_file())

    transcribed = [
        (name, hits)
        for name in prose
        if prose_language(name) == "de" and (hits := transcribed_in_prose(ROOT / name))
    ]

    still_german = [
        (name, hits)
        for name in prose
        if prose_language(name) == "en" and (hits := german_in_english_prose(ROOT / name))
    ]

    if not breaks and not transcribed and not still_german:
        print("No file breaks the language rule.")
        return 0

    if breaks:
        comments = sum(b[1] for b in breaks)
        print(f"\n{len(breaks)} files break the rule ({comments} comments):")
        for name, wrong, all_of_them in sorted(breaks, key=lambda b: -b[1]):
            where = "German in a test file" if is_test(name) else "German in code"
            print(f"  {name:56} {wrong:4} of {all_of_them:4}   {where}")

    if transcribed:
        lines = sum(len(h) for _, h in transcribed)
        print(f"\n{lines} lines of prose transcribe an umlaut, in {len(transcribed)} files:")
        for name, hits in transcribed:
            for number, words in hits[:5]:
                print(f"  {name}:{number}  {words}")
            if len(hits) > 5:
                print(f"  {name}  … and {len(hits) - 5} more lines")
        print("\n  German documentation writes its umlauts instead of transcribing them -- these")
        print("  are texts for people. Code, identifiers and quotations are exempt.")

    if still_german:
        paragraphs = sum(len(h) for _, h in still_german)
        print(
            f"\n{paragraphs} paragraphs stand in German inside an English file, in "
            f"{len(still_german)} files:"
        )
        for name, hits in still_german:
            for number, beginning in hits[:5]:
                print(f"  {name}:{number}  {beginning} …")
            if len(hits) > 5:
                print(f"  {name}  … and {len(hits) - 5} more paragraphs")
        print("\n  The repository speaks English; a German translation carries .de.md in its")
        print("  name. What stands here is a leftover of the switch.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
