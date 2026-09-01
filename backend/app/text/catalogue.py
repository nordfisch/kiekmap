"""The shape every language has to fill.

Frozen dataclasses rather than dictionaries, and that is the whole point of the construction: a
missing entry is a ``TypeError`` when ``en.py`` is imported, which happens at startup. A dict would
raise a ``KeyError`` at the moment somebody plugs in a USB stick, in a museum, in the one language
nobody tested.

It is the counterpart of ``type Texts = typeof de`` in the frontend, where ``tsc`` refuses to
build. Here the check comes one step later, but still before the first visitor.

Parameterised texts are functions, not templates with placeholders. Word order differs between
languages -- "3 of 12" and "3 von 12" agree, but a sentence that puts the number last in one
language and first in the other cannot be a format string with the same holes.
"""

from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class AdminTexts:
    session_expired: str
    no_pin_configured: str
    too_many_attempts: Callable[[int], str]
    wrong_pin: str
    no_such_date: str
    no_such_entry: Callable[[int], str]
    not_from_a_visitor: str
    already_taken_back: str
    edited_by_hand: str
    a_newer_statement_exists: str
    street_gone_from_the_index: str


@dataclass(frozen=True)
class PhotoTexts:
    no_such_photo: Callable[[int], str]
    thumbnail_missing: str
    original_missing: str


@dataclass(frozen=True)
class PlaceTexts:
    no_such_place: Callable[[int], str]


@dataclass(frozen=True)
class ContributeTexts:
    outside_the_map: str
    already_stated: str
    already_more_precise: str
    housenumber_unknown: str
    housenumber_wrong_street: str


@dataclass(frozen=True)
class BackupTexts:
    #: The API refuses.
    stick_gone: str
    busy: str
    file_gone_from_inbox: str
    not_a_complete_backup: str
    folder_gone_from_stick: str
    link_expired: str

    #: What stands on the progress bar.
    preparing: str
    saving_the_records: str
    first_the_records: str
    saving_photo: Callable[[int, int], str]
    fetching_photo: Callable[[int, int], str]
    setting_the_old_state_aside: str
    bringing_the_schema_forward: str

    #: How it ends.
    backup_done: Callable[[int, str | None], str]
    restore_done: Callable[[int, str], str]
    archive_done: Callable[[str, str], str]

    #: A size as it stands in a sentence: "3,4 MB" in German, "3.4 MB" in English. A number
    #: format is part of the language, and the two messages below put it into a sentence.
    size: Callable[[int], str]

    #: What goes wrong.
    no_backup_on_the_stick: str
    no_room_on_the_stick: Callable[[str, str], str]
    no_room_here: Callable[[str, str], str]
    backup_is_newer: Callable[[str], str]
    unexpected_entry: str
    something_went_wrong: Callable[[str], str]


@dataclass(frozen=True)
class ImportTexts:
    unreadable_file: Callable[[str], str]
    same_content_as: Callable[[int, str], str]
    no_readable_image: Callable[[str], str]
    unknown_format: str
    format_not_allowed: Callable[[str, str], str]
    imported: Callable[[bool, bool], str]
    reading_photo: Callable[[int, int], str]
    stick_summary: Callable[[int, int, int], str]


@dataclass(frozen=True)
class DateTexts:
    """The dating as it stands under a photo.

    Formatters rather than month names alone, because the parts are not assembled the same way:
    "22. März 2014" against "22 March 2014", "1930er" against "the 1930s". Handing out the names
    and letting the caller build the sentence would put German word order into the caller.
    """

    #: Twelve, January first. Indexed by month, so the order carries meaning.
    month_names: tuple[str, ...]
    year_unknown: str
    day: Callable[[int, int, int], str]
    month: Callable[[int, int], str]
    decade: Callable[[int], str]
    span: Callable[[int, int], str]


@dataclass(frozen=True)
class Texts:
    admin: AdminTexts
    photos: PhotoTexts
    places: PlaceTexts
    contribute: ContributeTexts
    backup: BackupTexts
    imports: ImportTexts
    dates: DateTexts
