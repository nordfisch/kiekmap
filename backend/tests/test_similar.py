"""Dasselbe Bild zweimal finden -- ``services/similar.py``.

Der SHA-256 erkennt eine Kopie der *Datei*. Er erkennt nicht denselben Papierabzug, zweimal
gescannt, und nicht denselben Scan, einmal gross und einmal klein gespeichert. Genau davon ist ein
gewachsenes Archiv voll: 1324 Fotos des Holmer Bestands enthielten 44 solcher Gruppen.

Der Fingerabdruck darf deshalb **ungenau** sein -- er soll Helligkeit, Farbstich und Verkleinerung
ertragen. Was er nicht darf, ist zwei verschiedene Bilder zusammenwerfen.
"""

import pytest
from PIL import Image, ImageEnhance

from app.models import Photo, PhotoStatus
from app.services.similar import candidate_groups, distance, fingerprint
from app.services.storage import THUMBNAIL_SIZES, thumbnail_path


@pytest.fixture
def haus(tmp_path):
    """Ein Bild mit Struktur -- eine Flaeche allein hat keinen Fingerabdruck."""
    bild = Image.new("RGB", (400, 300), (200, 205, 215))
    for x in range(60, 340):
        for y in range(120, 260):
            bild.putpixel((x, y), (150 - (x % 40), 90, 70))
    for x in range(100, 300, 60):
        for y in range(150, 200):
            for dx in range(30):
                bild.putpixel((x + dx, y), (250, 250, 230))
    pfad = tmp_path / "haus.png"
    bild.save(pfad)
    return pfad


class TestFingerabdruck:
    def test_dieselbe_datei_ergibt_denselben_abdruck(self, haus):
        assert fingerprint(haus) == fingerprint(haus)

    def test_die_kleine_kopie_bleibt_nah(self, haus, tmp_path):
        """Der haeufigste Fall im Bestand: derselbe Scan, einmal gross und einmal klein."""
        klein = tmp_path / "klein.png"
        Image.open(haus).resize((160, 120), Image.Resampling.LANCZOS).save(klein)

        assert distance(fingerprint(haus), fingerprint(klein)) <= 40

    def test_heller_und_farbstichig_bleibt_nah(self, haus, tmp_path):
        """Zwei Durchgaenge desselben Papierabzugs unterscheiden sich genau so."""
        anders = tmp_path / "anders.png"
        bild = ImageEnhance.Brightness(Image.open(haus)).enhance(1.4)
        ImageEnhance.Color(bild).enhance(0.2).save(anders)

        assert distance(fingerprint(haus), fingerprint(anders)) <= 40

    def test_ein_anderes_bild_bleibt_fern(self, haus, tmp_path):
        """Die Gegenprobe. Ohne sie taete es auch ein Abdruck, der immer dasselbe sagt."""
        anderes = tmp_path / "anderes.png"
        bild = Image.new("RGB", (400, 300), (240, 240, 235))
        for x in range(400):
            for y in range(x % 7, 300, 11):
                bild.putpixel((x, y), (30, 80, 40))
        bild.save(anderes)

        assert distance(fingerprint(haus), fingerprint(anderes)) > 40


class TestGruppen:
    def _foto(self, session, settings, haus, wandeln=lambda bild: bild) -> Photo:
        from app.services.storage import sha256_of_file

        nummer = len(session.query(Photo).all()) + 1
        bild = wandeln(Image.open(haus).convert("RGB"))
        foto = Photo(
            sha256=f"{nummer:064x}",
            original_filename=f"{nummer}.jpg",
            mime="image/jpeg",
            bytes=1,
            width=bild.width,
            height=bild.height,
            date_precision="unknown",
            status=PhotoStatus.PUBLISHED,
        )
        session.add(foto)
        session.flush()
        ziel = thumbnail_path(settings.thumbs_dir, foto.sha256, min(THUMBNAIL_SIZES))
        ziel.parent.mkdir(parents=True, exist_ok=True)
        bild.save(ziel, "WEBP")
        assert sha256_of_file(ziel)
        return foto

    def test_beide_fotos_stehen_in_der_gruppe(self, session, settings, haus):
        """Der Fehler, den diese Zeile schon einmal hatte.

        Beim Zusammenfassen ueber eine Union-Find-Struktur ist ein Foto die Wurzel seiner Gruppe.
        Wer nur die Nicht-Wurzeln einsammelt, verliert aus **jeder** Gruppe ein Foto -- und ein
        Paar schrumpft damit auf eines und faellt aus der Meldung. Am Bestand sah das aus wie
        "keine Dubletten gefunden".
        """
        gross = self._foto(session, settings, haus)
        klein = self._foto(
            session, settings, haus, lambda b: b.resize((160, 120), Image.Resampling.LANCZOS)
        )
        session.commit()

        gruppen = candidate_groups(session, settings)

        assert len(gruppen) == 1
        assert {f.id for f in gruppen[0]} == {gross.id, klein.id}

    def test_das_groesste_steht_vorn(self, session, settings, haus):
        self._foto(session, settings, haus, lambda b: b.resize((160, 120)))
        gross = self._foto(session, settings, haus)
        session.commit()

        assert candidate_groups(session, settings)[0][0].id == gross.id

    def test_ein_herausgenommenes_foto_kommt_nicht_wieder_vor(self, session, settings, haus):
        """Sonst legte der Befehl beim naechsten Lauf dieselbe Dublette erneut vor."""
        self._foto(session, settings, haus)
        raus = self._foto(session, settings, haus, lambda b: b.resize((160, 120)))
        raus.status = PhotoStatus.DELETED
        session.commit()

        assert candidate_groups(session, settings) == []
