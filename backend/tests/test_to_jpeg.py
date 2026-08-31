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

from app.services.exif import read_image_info  # noqa: E402


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


class TestMetadatenWandernMit:
    """Was die Quelldatei ueber sich sagt, muss die Kopie auch sagen.

    Gemessen wird mit dem Leser des Imports, nicht mit einem eigenen: Gefragt ist nicht, ob die
    Bytes mitgewandert sind, sondern ob das Programm hinterher dasselbe sieht.

    **Es hat einmal nicht gestimmt.** Die Umwandlung reichte nur Farbprofil und Aufloesung durch;
    zwoelf Fotos des neueren Archivstands verloren dabei ihren Fotografen ("Hubert Wulf"), eine
    Beschreibung und eine Datierung -- und trugen danach den Standardnachweis der Sammlung, was
    schlimmer ist als gar keiner: eine falsche Zuschreibung sieht aus wie eine Auskunft.
    """

    def _tiff_mit_iptc(self, pfad: Path, felder: dict[tuple[int, int], bytes]) -> None:
        """Ein TIFF, wie das Archiv es liefert: IPTC roh im Tag 33723.

        Von Hand zusammengesetzt und nicht mit dem Code erzeugt, den dieser Test prueft -- sonst
        pruefte er sich selbst. Das Format ist IPTC-IIM: je Feld ein 0x1C, Record, Dataset, zwei
        Byte Laenge, Inhalt.

        **Tag 33723 und nicht der Photoshop-Block:** In einem TIFF liest Pillow das IPTC nur von
        dort, und zwar an seinem eigenen verstuemmelten Wert vorbei direkt aus den Rohbytes. Im
        JPEG steht derselbe Inhalt dann in ``APP13``, hinter der Marke "Photoshop 3.0" -- zwei
        Ablagen fuer dieselbe Sache, und die Umwandlung fuehrt von der einen in die andere.
        """
        from PIL import TiffImagePlugin

        records = b"".join(
            bytes((0x1C, record, dataset)) + len(wert).to_bytes(2, "big") + wert
            for (record, dataset), wert in sorted(felder.items())
        )
        ordner = TiffImagePlugin.ImageFileDirectory_v2()
        ordner[33723] = records
        ordner.tagtype[33723] = 1  # BYTE
        Image.new("RGB", (40, 30), (200, 180, 160)).save(pfad, "TIFF", tiffinfo=ordner)

    def test_fotograf_und_beschreibung_ueberleben(self, tmp_path: Path) -> None:
        quelle = tmp_path / "scan.tif"
        self._tiff_mit_iptc(
            quelle,
            {
                (2, 80): b"Hubert Wulf",  # By-line, der Fotograf
                (2, 120): b"Collage aus der Niederstrasse",  # Caption
            },
        )

        ziel = tmp_path / "scan.jpg"
        werkzeug.to_jpeg(quelle, ziel)

        gelesen = read_image_info(ziel)
        assert gelesen.credit == "Hubert Wulf"
        assert gelesen.description == "Collage aus der Niederstrasse"

    def test_die_koordinate_ueberlebt(self, tmp_path: Path) -> None:
        """Eine Datei des neuen Archivstands traegt GPS -- und ging beim Umwandeln verloren."""
        exif = Image.Exif()
        exif[0x8825] = {
            1: "N",
            2: (53.0, 37.0, 9.0),
            3: "E",
            4: (9.0, 40.0, 28.0),
        }
        quelle = tmp_path / "foto.png"
        Image.new("RGB", (40, 30)).save(quelle, "PNG", exif=exif.tobytes())

        ziel = tmp_path / "foto.jpg"
        werkzeug.to_jpeg(quelle, ziel)

        gelesen = read_image_info(ziel)
        assert gelesen.lat is not None and gelesen.lon is not None
        assert abs(gelesen.lat - 53.6191) < 0.001
        assert abs(gelesen.lon - 9.6744) < 0.001

    def test_zwei_laeufe_bleiben_auch_mit_metadaten_gleich(self, tmp_path: Path) -> None:
        """Die Zusage aus Punkt 46 gilt weiter -- Metadatenbloecke duerfen nicht wackeln."""
        quelle = tmp_path / "scan.tif"
        self._tiff_mit_iptc(quelle, {(2, 80): b"Hubert Wulf", (2, 25): b"Gebaeude"})

        erst, dann = tmp_path / "a.jpg", tmp_path / "b.jpg"
        werkzeug.to_jpeg(quelle, erst)
        werkzeug.to_jpeg(quelle, dann)

        assert hashlib.sha256(erst.read_bytes()).hexdigest() == (
            hashlib.sha256(dann.read_bytes()).hexdigest()
        )
