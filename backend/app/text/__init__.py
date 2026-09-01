"""Which language the device speaks, resolved per call.

    from app.text import texts
    raise HTTPException(404, texts().photos.no_such_photo(photo_id))

Per call, not once at import: the setting is read through ``get_settings()``, which is cached, so
the lookup costs a dictionary access. Resolving at import would freeze the language into the
module and make every test that switches it a lie.

What does **not** come from here: log lines, CLI output, and API messages that only a hand-written
request can provoke. Those are English in place. The rule of thumb is in CLAUDE.md -- can it appear
in the visitor view or the admin view? Then it belongs in the catalogue.
"""

from app.config import get_settings
from app.text.catalogue import Texts
from app.text.de import de
from app.text.en import en

CATALOGUES: dict[str, Texts] = {"de": de, "en": en}


def texts() -> Texts:
    return CATALOGUES[get_settings().language]


__all__ = ["CATALOGUES", "Texts", "texts"]
