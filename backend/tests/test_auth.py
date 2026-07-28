"""Tests der Anmeldung am Admin-Bereich.

Der Kernpunkt: eine PIN ist ein kurzes Geheimnis. Vier Ziffern sind zehntausend Moeglichkeiten,
die ein Skript in Sekunden durchprobiert haette. Was das aufwiegt, ist die Sperre nach wenigen
Fehlversuchen -- deshalb steht sie hier im Mittelpunkt und nicht das Hashen.
"""

import pytest

from app.services import auth


class TestPin:
    def test_falsche_pin_wird_abgewiesen(self):
        gespeichert = auth.hash_pin("4711")

        assert not auth.verify_pin("4712", gespeichert)

    def test_richtige_pin_wird_erkannt(self):
        gespeichert = auth.hash_pin("4711")

        assert auth.verify_pin("4711", gespeichert)

    def test_gleiche_pin_ergibt_verschiedene_hashes(self):
        """Salz. Sonst verriete ein Blick in zwei .env-Dateien, dass beide dieselbe PIN haben."""
        assert auth.hash_pin("4711") != auth.hash_pin("4711")

    def test_kaputter_hash_laesst_niemanden_hinein(self):
        """Ein vertippter Eintrag in der .env darf nicht zufaellig zur offenen Tuer werden."""
        for unbrauchbar in ("", "4711", "pbkdf2_sha256$abc", "md5$1$aa$bb"):
            assert not auth.verify_pin("4711", unbrauchbar)

    def test_pin_muss_aus_ziffern_bestehen(self):
        """Auf dem Tastenfeld im Museum gibt es keine Buchstaben."""
        assert auth.is_valid_pin("4711")
        assert not auth.is_valid_pin("47a1")
        assert not auth.is_valid_pin("471")
        assert not auth.is_valid_pin("4" * 13)


class TestSitzungen:
    def test_unbekanntes_token_gilt_nicht(self):
        store = auth.SessionStore()

        assert store.renew("ausgedacht") is None

    def test_abgemeldetes_token_gilt_nicht_mehr(self):
        store = auth.SessionStore()
        sitzung = store.issue()

        store.revoke(sitzung.token)

        assert store.renew(sitzung.token) is None

    def test_sitzung_laeuft_ab(self, monkeypatch: pytest.MonkeyPatch):
        """Ein am Abend vergessener Login darf nicht ueber Nacht offen bleiben."""
        uhr = [1000.0]
        monkeypatch.setattr(auth.time, "monotonic", lambda: uhr[0])
        store = auth.SessionStore(lifetime_s=60)
        sitzung = store.issue()

        uhr[0] += 61

        assert store.renew(sitzung.token) is None

    def test_jede_anfrage_schiebt_den_ablauf_hinaus(self, monkeypatch: pytest.MonkeyPatch):
        """Sonst floege jemand mitten aus dem Bearbeiten heraus, nur weil das Tippen dauert."""
        uhr = [1000.0]
        monkeypatch.setattr(auth.time, "monotonic", lambda: uhr[0])
        store = auth.SessionStore(lifetime_s=60)
        sitzung = store.issue()

        for _ in range(10):
            uhr[0] += 30
            assert store.renew(sitzung.token) is not None

        # Insgesamt 300 Sekunden vergangen, die Sitzung haelt 60 -- und lebt trotzdem noch.
        assert uhr[0] == 1300.0


class TestVersuchssperre:
    def test_sperrt_nach_zu_vielen_fehlversuchen(self):
        guard = auth.AttemptGuard(max_attempts=3, lockout_s=60)

        assert guard.record_failure() == 0
        assert guard.record_failure() == 0
        assert guard.record_failure() == 60
        assert guard.locked_for() == 60

    def test_sperre_laeuft_von_selbst_ab(self, monkeypatch: pytest.MonkeyPatch):
        uhr = [1000.0]
        monkeypatch.setattr(auth.time, "monotonic", lambda: uhr[0])
        guard = auth.AttemptGuard(max_attempts=1, lockout_s=60)
        guard.record_failure()

        uhr[0] += 61

        assert guard.locked_for() == 0

    def test_erfolgreiche_anmeldung_setzt_den_zaehler_zurueck(self):
        """Sonst summierten sich Vertipper ueber Monate zu einer Sperre."""
        guard = auth.AttemptGuard(max_attempts=3, lockout_s=60)
        guard.record_failure()
        guard.record_failure()

        guard.reset()

        assert guard.record_failure() == 0
        assert guard.locked_for() == 0
