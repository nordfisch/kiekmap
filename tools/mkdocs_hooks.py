"""Two link forms that mean one thing in the repository and another on the site.

The documents point at 61 files that are not pages -- ``../LICENSE``, ``../CLAUDE.md``,
``../deploy/docker-compose.yml``, ``../frontend/src/text/``. On GitHub those links work, because
the reader is standing in the repository. On the site they lead nowhere, and ``--strict`` says so.

The alternative was to write 61 absolute URLs into the markdown by hand, in both languages, and to
keep them in step for ever. A rule applied at build time is the cheaper half of that trade: the
files stay readable in the repository, which is where most people meet them.

The second form is a link into ``docs/archive/``, which is excluded from the site for the same
reason -- the history is a repository file here, not a page.

The third form is a link to a German half. ``usermanual.de.md`` is what a reader on GitHub has
to click; here the same page lives at ``/kiekmap/de/usermanual/``. Only English pages need the
rewrite -- a German page linking to a German neighbour is already pointing at its own tree, and
MkDocs resolves it on its own.

``KIEKMAP_DOCS_REF`` says which ref the outward links point at -- the workflow sets the tag it
built from, so a link out of the site for v0.9.0 lands on the files of v0.9.0.
"""

import os
import re
from urllib.parse import urlsplit

REPOSITORY = "https://github.com/nordfisch/kiekmap"

#: A link target one level above ``docs/``, with an optional anchor: ``../NOTICE``,
#: ``../CLAUDE.md#writing-rules``, ``../frontend/src/text/``.
OUTWARD = re.compile(r"\]\(\.\./([^)#]+)(#[^)]*)?\)")

#: A link to the German half of a document, from a document beside it: ``licensing.de.md``.
GERMAN_HALF = re.compile(r"\]\(([A-Za-z0-9_-]+)\.de\.md(#[^)]*)?\)")

#: A link into ``docs/archive/``, which is kept out of the site and stays a repository file.
ARCHIVED = re.compile(r"\]\((?:\.\./)?(archive/[^)#]+)(#[^)]*)?\)")


def _target(match: re.Match[str], ref: str, under: str = "") -> str:
    path, anchor = under + match.group(1), match.group(2) or ""
    # GitHub serves a directory under /tree/ and a file under /blob/. A trailing slash is the
    # only thing that tells them apart here, and every directory link in the docs carries one.
    kind = "tree" if path.endswith("/") else "blob"
    return f"]({REPOSITORY}/{kind}/{ref}/{path.rstrip('/')}{anchor})"


def on_page_markdown(markdown: str, page, config, **_: object) -> str:  # noqa: ANN001
    ref = os.environ.get("KIEKMAP_DOCS_REF", "develop")
    markdown = OUTWARD.sub(lambda m: _target(m, ref), markdown)
    markdown = ARCHIVED.sub(lambda m: _target(m, ref, "docs/"), markdown)

    if not page.file.src_path.endswith(".de.md"):
        base = urlsplit(config["site_url"]).path or "/"
        markdown = GERMAN_HALF.sub(
            lambda m: f"]({base}de/{m.group(1)}/{m.group(2) or ''})", markdown
        )
    return markdown
