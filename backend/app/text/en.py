"""The English version. A translation of ``de.py``, which is the source text.

Written to the same rules as everything else here: one thought per sentence, active voice, no
hedging. These lines stand on a museum device in front of visitors, so they are not a by-product.
"""

from app.text.catalogue import (
    AdminTexts,
    BackupTexts,
    ContributeTexts,
    DateTexts,
    ImportTexts,
    PhotoTexts,
    PlaceTexts,
    Texts,
)

MONTH_NAMES = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)


def _imported(needs_place: bool, needs_date: bool) -> str:
    wanted = (("a place", needs_place), ("a year", needs_date))
    missing = [label for label, empty in wanted if empty]
    return "Taken in" + (f", still missing: {' and '.join(missing)}" if missing else "")


def _stick_summary(imported: int, duplicates: int, rejected: int) -> str:
    parts = [f"{imported} photos taken in"]
    if duplicates:
        was = "was" if duplicates == 1 else "were"
        parts.append(f"{duplicates} {was} already there")
    if rejected:
        parts.append(f"{rejected} rejected")
    return ", ".join(parts) + ". The stick can be removed now."


def _size(size: int) -> str:
    for unit, factor in (("GB", 1000**3), ("MB", 1000**2), ("kB", 1000)):
        if size >= factor:
            return f"{size / factor:.1f} {unit}"
    return f"{size} bytes"


def _backup_done(photos: int, written: str | None) -> str:
    added = f"Newly added: {written}." if written else "There were no new pictures."
    return f"{photos} photos and all records saved. {added} The stick can be removed now."


en = Texts(
    admin=AdminTexts(
        session_expired="The session has expired. Please sign in again.",
        no_pin_configured=(
            "No PIN has been set up yet. It is set on the computer, with: python -m app.cli pin"
        ),
        too_many_attempts=lambda seconds: f"Too many attempts. Please wait {seconds} seconds.",
        wrong_pin="That PIN is not right.",
        no_such_date="There is no such date.",
        no_such_entry=lambda change_id: f"No entry with the number {change_id}",
        not_from_a_visitor="This did not come from a visitor and therefore stays.",
        already_taken_back="That has already been done.",
        edited_by_hand="This statement has since been edited by hand and therefore stays.",
        a_newer_statement_exists=(
            "There is a newer statement for this photo. Please take that one back first."
        ),
        street_gone_from_the_index=(
            "The street from this statement is no longer in the gazetteer. "
            "The place therefore stays."
        ),
    ),
    photos=PhotoTexts(
        no_such_photo=lambda photo_id: f"No photo with the number {photo_id}",
        thumbnail_missing="The thumbnail is missing",
        original_missing="The original file is missing",
    ),
    places=PlaceTexts(
        no_such_place=lambda place_id: f"No place with the number {place_id}",
    ),
    contribute=ContributeTexts(
        outside_the_map="This place lies outside the map.",
        already_stated="This photo has since been given a statement. Thank you all the same!",
        already_more_precise=(
            "This photo has since been given a more precise statement. Thank you all the same!"
        ),
        housenumber_unknown="This house number is not in the gazetteer.",
        housenumber_wrong_street="This house number does not belong to this street.",
    ),
    backup=BackupTexts(
        stick_gone="This stick is gone. Please plug it in again.",
        busy="Something is already under way. Please wait until it is finished.",
        file_gone_from_inbox="This file is no longer in the inbox folder.",
        not_a_complete_backup="This file is not a complete backup.",
        folder_gone_from_stick="This folder is no longer on the stick.",
        link_expired="This link has expired. Please download it again.",
        preparing="Getting ready",
        saving_the_records="The records are being saved",
        first_the_records="The records come first",
        saving_photo=lambda done, total: f"Saving photo {done} of {total}",
        fetching_photo=lambda done, total: f"Fetching photo {done} of {total}",
        setting_the_old_state_aside="The previous state is being set aside",
        bringing_the_schema_forward="The schema is being brought forward",
        backup_done=_backup_done,
        restore_done=lambda photos, folder: (
            f"{photos} photos and all records are back. The previous state is in the folder "
            f"{folder} and can go once everything is right."
        ),
        archive_done=lambda message, folder: (
            f"{message} The file that was read in now lies in the folder {folder} and can go too."
        ),
        size=_size,
        no_backup_on_the_stick="There is no backup on this stick, or it is not complete.",
        no_room_on_the_stick=lambda needed, free: (
            f"There is not enough room on the stick. {needed} is needed, {free} is free."
        ),
        no_room_here=lambda needed, free: (
            f"There is not enough room here. {needed} is needed, {free} is free."
        ),
        backup_is_newer=lambda revision: (
            f"This backup belongs to a newer version of the program (schema {revision}). "
            "Please update the program first, then read the backup in. "
            "Nothing on the device was changed."
        ),
        unexpected_entry="The file holds an unexpected entry.",
        something_went_wrong=lambda reason: f"Something went wrong: {reason}",
    ),
    imports=ImportTexts(
        unreadable_file=lambda reason: f"File not readable: {reason}",
        same_content_as=lambda photo_id, filename: f"Same content as photo {photo_id} ({filename})",
        no_readable_image=lambda reason: f"No readable image: {reason}",
        unknown_format="unknown",
        format_not_allowed=lambda found, allowed: (
            f"Format {found} does not fit (allowed are: {allowed})"
        ),
        imported=_imported,
        reading_photo=lambda done, total: f"Reading photo {done} of {total}",
        stick_summary=_stick_summary,
    ),
    dates=DateTexts(
        month_names=MONTH_NAMES,
        year_unknown="Year unknown",
        day=lambda day, month, year: f"{day} {MONTH_NAMES[month - 1]} {year}",
        month=lambda month, year: f"{MONTH_NAMES[month - 1]} {year}",
        decade=lambda year: f"{year}s",
        span=lambda start, end: f"{start}–{end}",
    ),
)
