"""Both languages, and the promise that neither has a hole in it.

The construction is the point: ``Texts`` is a frozen dataclass, so a missing entry in ``en.py`` is
a ``TypeError`` when the module is imported -- at startup, not in a museum. These tests prove that
the import happens and that the setting really reaches the text.
"""

import pytest
from fastapi.testclient import TestClient

from app.text import CATALOGUES


def test_both_languages_are_there() -> None:
    assert set(CATALOGUES) == {"de", "en"}


@pytest.mark.parametrize("language", ["de", "en"])
def test_no_entry_is_empty(language: str) -> None:
    """A forgotten translation is more likely to be an empty string than a missing field.

    The dataclass catches what is absent. What it cannot catch is a placeholder somebody left
    behind, and an empty message on a museum screen looks like a bug in the program.
    """
    catalogue = CATALOGUES[language]
    for group_name in catalogue.__dataclass_fields__:
        group = getattr(catalogue, group_name)
        for field in group.__dataclass_fields__:
            value = getattr(group, field)
            if isinstance(value, str):
                assert value.strip(), f"{language}.{group_name}.{field} is empty"


@pytest.mark.parametrize("language", ["de", "en"])
def test_every_function_returns_something(language: str) -> None:
    """Called with plausible arguments, so a mistyped f-string shows up here."""
    catalogue = CATALOGUES[language]
    arguments = {1: (7,), 2: (3, 12), 3: (3, 12, 1955)}

    for group_name in catalogue.__dataclass_fields__:
        group = getattr(catalogue, group_name)
        for field in group.__dataclass_fields__:
            value = getattr(group, field)
            if not callable(value):
                continue
            count = value.__code__.co_argcount
            result = value(*arguments[count][:count])
            assert isinstance(result, str) and result.strip(), f"{language}.{group_name}.{field}"


def test_the_month_names_are_twelve() -> None:
    for language, catalogue in CATALOGUES.items():
        assert len(catalogue.dates.month_names) == 12, language


def test_the_setting_decides_what_an_error_says(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The whole point of the stage, in one assertion.

    ``/photos/999999`` exists in no collection, so both languages answer with 404 -- and the text
    beside it is what the visitor reads.
    """
    from app.config import get_settings

    assert "Kein Foto" in client.get("/api/photos/999999").json()["detail"]

    monkeypatch.setenv("KIEKMAP_LANGUAGE", "en")
    get_settings.cache_clear()

    assert "No photo" in client.get("/api/photos/999999").json()["detail"]


def test_the_date_label_follows_the_setting(monkeypatch: pytest.MonkeyPatch) -> None:
    """``docs/adaption.md`` named the server-side formatting as the obstacle to a second language.

    It was right while the backend had no notion of one. This is the assertion that removed the
    premise.
    """
    from datetime import date

    from app.config import get_settings
    from app.models import DatePrecision
    from app.services.dates import format_label

    day = (date(1955, 6, 3), date(1955, 6, 3), DatePrecision.DAY)
    assert format_label(*day) == "3. Juni 1955"

    monkeypatch.setenv("KIEKMAP_LANGUAGE", "en")
    get_settings.cache_clear()

    assert format_label(*day) == "3 June 1955"
    assert format_label(None, None, DatePrecision.YEAR) == "Year unknown"
    assert format_label(date(1920, 1, 1), date(1929, 12, 31), DatePrecision.DECADE) == "1920s"
