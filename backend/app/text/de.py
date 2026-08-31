"""The German version. It is the source text; ``en.py`` is the translation.

This docstring is English like every other one -- the rule is about comments, not about values.
The German lives in the strings below.

Umlauts there are transcribed, as in every German text inside source code, and the sentences are
built so that they need as few as possible: not "Sie koennen den Stick abziehen" but "Der Stick
kann abgezogen werden". Month names are the exception, because "Maerz" would simply be wrong --
they are data, not prose. See CLAUDE.md.
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
    "Januar",
    "Februar",
    "März",
    "April",
    "Mai",
    "Juni",
    "Juli",
    "August",
    "September",
    "Oktober",
    "November",
    "Dezember",
)


def _imported(needs_place: bool, needs_date: bool) -> str:
    missing = [label for label, empty in (("Ort", needs_place), ("Jahr", needs_date)) if empty]
    return "Aufgenommen" + (f", es fehlt noch: {' und '.join(missing)}" if missing else "")


def _stick_summary(imported: int, duplicates: int, rejected: int) -> str:
    parts = [f"{imported} Fotos aufgenommen"]
    if duplicates:
        were = "war" if duplicates == 1 else "waren"
        parts.append(f"{duplicates} {were} schon da")
    if rejected:
        parts.append(f"{rejected} abgewiesen")
    return ", ".join(parts) + ". Der Stick kann jetzt abgezogen werden."


def _size(size: int) -> str:
    for unit, factor in (("GB", 1000**3), ("MB", 1000**2), ("kB", 1000)):
        if size >= factor:
            return f"{size / factor:.1f}".replace(".", ",") + f" {unit}"
    return f"{size} Bytes"


def _backup_done(photos: int, written: str | None) -> str:
    added = f"Neu dazugekommen: {written}." if written else "Neue Bilder gab es nicht."
    return (
        f"{photos} Fotos und alle Angaben gesichert. {added} Der Stick kann jetzt abgezogen werden."
    )


de = Texts(
    admin=AdminTexts(
        session_expired="Die Anmeldung ist abgelaufen. Bitte noch einmal anmelden.",
        no_pin_configured=(
            "Es ist noch keine PIN eingerichtet. Sie wird am Rechner gesetzt, "
            "mit: python -m app.cli pin"
        ),
        too_many_attempts=lambda seconds: f"Zu viele Versuche. Bitte {seconds} Sekunden warten.",
        wrong_pin="Die PIN stimmt nicht.",
        no_such_date="Dieses Datum gibt es nicht.",
        no_such_entry=lambda change_id: f"Kein Eintrag mit der Nummer {change_id}",
        not_from_a_visitor="Das ist keine Angabe von Besuchern und bleibt daher stehen.",
        already_taken_back="Das ist bereits geschehen.",
        edited_by_hand=(
            "Die Angabe ist inzwischen von Hand bearbeitet worden und bleibt daher stehen."
        ),
        a_newer_statement_exists=(
            "Zu diesem Foto gibt es eine neuere Angabe. Bitte diese zuerst zuruecknehmen."
        ),
        street_gone_from_the_index=(
            "Die Strasse aus dieser Angabe steht nicht mehr im Ortsverzeichnis. "
            "Der Ort bleibt daher stehen."
        ),
    ),
    photos=PhotoTexts(
        no_such_photo=lambda photo_id: f"Kein Foto mit der Nummer {photo_id}",
        thumbnail_missing="Vorschaubild fehlt",
        original_missing="Originaldatei fehlt",
    ),
    places=PlaceTexts(
        no_such_place=lambda place_id: f"Kein Ort mit der Nummer {place_id}",
    ),
    contribute=ContributeTexts(
        outside_the_map="Dieser Ort liegt ausserhalb der Karte.",
        already_stated=(
            "Dieses Foto hat inzwischen schon eine Angabe bekommen. Vielen Dank trotzdem!"
        ),
        already_more_precise=(
            "Dieses Foto hat inzwischen schon eine genauere Angabe bekommen. Vielen Dank trotzdem!"
        ),
        housenumber_unknown="Diese Hausnummer steht nicht im Ortsverzeichnis.",
        housenumber_wrong_street="Diese Hausnummer gehoert nicht zu dieser Strasse.",
    ),
    backup=BackupTexts(
        stick_gone="Dieser Stick ist nicht mehr da. Bitte neu einstecken.",
        busy="Es ist schon etwas im Gange. Bitte warten, bis es fertig ist.",
        file_gone_from_inbox="Diese Datei liegt nicht mehr im Eingangsordner.",
        not_a_complete_backup="Diese Datei ist keine vollstaendige Sicherung.",
        folder_gone_from_stick="Diesen Ordner gibt es auf dem Stick nicht mehr.",
        link_expired="Dieser Link ist abgelaufen. Bitte noch einmal herunterladen.",
        preparing="Wird vorbereitet",
        saving_the_records="Die Angaben werden gesichert",
        first_the_records="Zuerst kommen die Angaben",
        saving_photo=lambda done, total: f"Sichere Foto {done} von {total}",
        fetching_photo=lambda done, total: f"Hole Foto {done} von {total}",
        setting_the_old_state_aside="Der bisherige Stand wird beiseitegelegt",
        bringing_the_schema_forward="Der Schemastand wird nachgezogen",
        backup_done=_backup_done,
        restore_done=lambda photos, folder: (
            f"{photos} Fotos und alle Angaben sind wieder da. Der bisherige Stand liegt im Ordner "
            f"{folder} und kann weg, sobald alles stimmt."
        ),
        archive_done=lambda message, folder: (
            f"{message} Die eingespielte Datei liegt jetzt im Ordner {folder} "
            "und kann ebenfalls weg."
        ),
        size=_size,
        no_backup_on_the_stick=(
            "Auf diesem Stick fehlt eine Sicherung, oder sie ist nicht komplett."
        ),
        no_room_on_the_stick=lambda needed, free: (
            f"Auf dem Stick ist zu wenig Platz. Gebraucht werden {needed}, frei sind {free}."
        ),
        no_room_here=lambda needed, free: (
            f"Hier ist zu wenig Platz. Gebraucht werden {needed}, frei sind {free}."
        ),
        backup_is_newer=lambda revision: (
            f"Diese Sicherung gehoert zu einer neueren Programmversion (Schemastand {revision}). "
            "Bitte erst das Programm aktualisieren, dann die Sicherung einspielen. "
            "Auf dem Geraet wurde nichts veraendert."
        ),
        unexpected_entry="Die Datei enthaelt einen unerwarteten Eintrag.",
        something_went_wrong=lambda reason: f"Es ist etwas schiefgegangen: {reason}",
    ),
    imports=ImportTexts(
        unreadable_file=lambda reason: f"Datei nicht lesbar: {reason}",
        same_content_as=lambda photo_id, filename: (
            f"Inhaltsgleich mit Foto {photo_id} ({filename})"
        ),
        no_readable_image=lambda reason: f"Kein lesbares Bild: {reason}",
        unknown_format="unbekannt",
        format_not_allowed=lambda found, allowed: (
            f"Format {found} passt nicht (erlaubt sind: {allowed})"
        ),
        imported=_imported,
        reading_photo=lambda done, total: f"Lese Foto {done} von {total}",
        stick_summary=_stick_summary,
    ),
    dates=DateTexts(
        month_names=MONTH_NAMES,
        year_unknown="Jahr unbekannt",
        day=lambda day, month, year: f"{day}. {MONTH_NAMES[month - 1]} {year}",
        month=lambda month, year: f"{MONTH_NAMES[month - 1]} {year}",
        decade=lambda year: f"{year}er",
        span=lambda start, end: f"{start}–{end}",
    ),
)
