"""Links that mean one thing in the repository and another on the site.

The site is ``docs/museum/`` and nothing else. Every link that leaves that directory points at a
file in the repository -- ``../../LICENSE``, ``../developer/decisions.md``,
``../../frontend/src/text/``. On GitHub those work, because the reader is standing in the
repository. Here they lead nowhere, and ``--strict`` says so.

Writing the absolute URLs into the markdown by hand was the alternative: some sixty of them, in
two languages, to be kept in step for ever. A rule applied at build time is the cheaper half of
that trade, and it leaves the files readable where most people meet them.

``KIEKMAP_DOCS_REF`` says which ref the links point at -- the workflow sets the tag it built from,
so a link out of the site for v0.9.0 lands on the files of v0.9.0.
"""

import os
import posixpath
import re

REPOSITORY = "https://github.com/nordfisch/kiekmap"

#: Where the published documents live, so a link out of them can be resolved against the root.
PUBLISHED = "docs/museum"

#: A link that climbs out of the published directory, with an optional anchor.
OUTWARD = re.compile(r"\]\((\.\./[^)#]+)(#[^)]*)?\)")


def _target(match: re.Match[str], ref: str) -> str:
    path = posixpath.normpath(posixpath.join(PUBLISHED, match.group(1)))
    # GitHub serves a directory under /tree/ and a file under /blob/. A trailing slash is the only
    # thing that tells them apart here, and normpath eats it -- hence the test on the match.
    kind = "tree" if match.group(1).endswith("/") else "blob"
    return f"]({REPOSITORY}/{kind}/{ref}/{path}{match.group(2) or ''})"


def on_page_markdown(markdown: str, **_: object) -> str:
    ref = os.environ.get("KIEKMAP_DOCS_REF", "develop")
    return OUTWARD.sub(lambda m: _target(m, ref), markdown)
