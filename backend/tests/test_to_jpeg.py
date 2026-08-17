"""Die Umwandlung des Archivs nach JPEG -- ``tools/to_jpeg.py``.

Die Zusage, an der alles haengt: **Dieselbe Datei ergibt zweimal denselben SHA-256.** Der Import
erkennt eine Dublette am Hash der Datei. Wer die Qualitaet hier nachjustiert, bekommt aus
demselben Scan andere Bytes -- und beim naechsten Archivstand kaeme jedes schon vorhandene Bild
ein zweites Mal herein, ohne dass jemand etwas merkt. Das ist kein Schoenheitsfehler, sondern der
teuerste stille Fehler, den dieses Werkzeug haben kann.

Das Werkzeug liegt ausserhalb des Backends, weil es vor dem Import laeuft, auf dem Archivordner.
Deshalb der Pfadeintrag -- der einzige Test, der ihn braucht.
"""

import hashlib
import sys
from pathlib import Path

import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))

import to_jpeg as werkzeug  # noqa: E402


@pytest.fixture
def scan(tmp_path: Path) -> Path:
    """Ein TIFF voller feiner Struktur -- der unbequemste Fall, absichtlich.

    Ein Foto laesst sich bei Qualitaet 92 auf etwa ein Drittel Byte je Bildpunkt zusammendruecken;
    dieses hier braucht mehr als ein ganzes. Genau daran scheitert die Umwandlung ohne den
    groesseren ``MAXBLOCK`` -- siehe ``to_jpeg``.
    """
    bild = Image.new("RGB", (400, 300))
    for x in range(400):
        for y in range(0, 300, 3):
            bild.putpixel((x, y), (x % 256, (x * y) % 256, y % 256))
    pfad = tmp_path / "Scan.TIF"
    bild.save(pfad, "TIFF")
    return pfad


def _umgewandelt(scan: Path, name: str) -> bytes:
    ziel = scan.parent / name
    werkzeug.to_jpeg(scan, ziel)
    return ziel.read_bytes()


def test_zweimal_umgewandelt_ergibt_denselben_hash(scan: Path) -> None:
    """Sonst kaeme dasselbe Foto beim naechsten Archivstand noch einmal herein."""
    erst = hashlib.sha256(_umgewandelt(scan, "erst.jpg")).hexdigest()
    dann = hashlib.sha256(_umgewandelt(scan, "dann.jpg")).hexdigest()
    assert erst == dann


def test_eine_andere_qualitaet_ergibt_andere_bytes(scan: Path, monkeypatch) -> None:
    """Die Gegenprobe zum vorigen Test: der Hash haengt wirklich an der Einstellung.

    Ohne sie liesse sich die Zusage auch mit einem Werkzeug halten, das jede Einstellung
    ignoriert -- und die Zusage waere nichts wert.
    """
    vorher = _umgewandelt(scan, "vorher.jpg")
    monkeypatch.setattr(
        werkzeug, "JPEG_OPTIONS", {"quality": 90, "subsampling": 0, "optimize": True}
    )
    assert _umgewandelt(scan, "nachher.jpg") != vorher


def test_ein_kleines_bild_voller_details_bricht_nicht_ab(scan: Path) -> None:
    """Pillow raet den Puffer aus der Bildgroesse und liegt bei solchen Bildern daneben.

    Der Abbruch heisst "broken data stream when writing image file" und traefe genau die
    Vorlagen, die ein Archiv nebenbei mitschickt -- Karten, Zeitungsausschnitte, Bildschirmfotos.
    """
    ziel = scan.parent / "eng.jpg"
    werkzeug.to_jpeg(scan, ziel)
    assert Image.open(ziel).size == (400, 300)


def test_die_gemessene_einstellung_steht_fest() -> None:
    """Qualitaet 92, 4:4:4, optimize -- am Erstbestand nachgemessen, nicht gewaehlt.

    Siehe den Docstring von ``tools/to_jpeg.py``: vier von 19 Dateien kommen damit bitgleich
    heraus, achtzehn pixelgleich. Mit Qualitaet 90 keine einzige.
    """
    assert werkzeug.JPEG_OPTIONS == {"quality": 92, "subsampling": 0, "optimize": True}


def test_durchsichtiges_png_bekommt_weissen_grund(tmp_path: Path) -> None:
    """JPEG kennt keine Transparenz, und ein Scan liegt auf Papier, nicht im Nichts.

    Auf schwarzem Grund waere der durchsichtige Rand eines freigestellten Scans ein Trauerrand.
    """
    bild = Image.new("RGBA", (20, 20), (255, 0, 0, 0))
    pfad = tmp_path / "frei.png"
    bild.save(pfad)

    werkzeug.to_jpeg(pfad, tmp_path / "frei.jpg")
    assert Image.open(tmp_path / "frei.jpg").convert("RGB").getpixel((10, 10)) == (255, 255, 255)


def test_der_baum_wird_kopiert_und_die_quelle_nicht_angefasst(tmp_path: Path) -> None:
    """Was das Museum geschickt hat, bleibt, wie es geschickt wurde."""
    quelle = tmp_path / "Archiv" / "Hauptstraße" / "14 Museum"
    quelle.mkdir(parents=True)
    Image.new("RGB", (10, 10)).save(quelle / "scan.tif")
    Image.new("RGB", (10, 10)).save(quelle / "foto.jpg")
    (quelle / "Notiz.txt").write_text("keine Bilddatei")
    vorher = sorted(p.name for p in quelle.iterdir())

    ziel = tmp_path / "Kopie"
    zaehler = werkzeug.build(tmp_path / "Archiv", ziel)

    assert zaehler["umgewandelt"] == 1
    assert zaehler["kopiert"] == 1
    assert zaehler["uebergangen"] == 1
    assert (ziel / "Hauptstraße" / "14 Museum" / "scan.jpg").exists()
    assert (ziel / "Hauptstraße" / "14 Museum" / "foto.jpg").exists()
    assert not (ziel / "Hauptstraße" / "14 Museum" / "Notiz.txt").exists()
    assert sorted(p.name for p in quelle.iterdir()) == vorher


def test_das_ziel_darf_nicht_in_der_quelle_liegen(tmp_path: Path) -> None:
    """Sonst laeuft die Umwandlung ueber ihre eigene Ausgabe -- und zwar endlos."""
    (tmp_path / "Archiv").mkdir()
    assert werkzeug.main([str(tmp_path / "Archiv"), str(tmp_path / "Archiv" / "Kopie")]) == 1
