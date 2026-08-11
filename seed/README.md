# Beispielbestand

Ein kleiner Fotobestand zum Entwickeln und Ausprobieren. Er ersetzt das, was vorher jeder für sich
von Hand in `data/` zusammengeklickt hat — und was niemand sonst hatte.

```bash
make seed        # Bestand aus diesem Ordner herstellen (loescht den vorhandenen!)
make seed-save   # den laufenden Bestand hierher sichern
```

## Alles hier ist erfunden

> **Die Bilder sind gezeichnet, die Menschen ausgedacht.** Familie Wendt, Gasthof Petersen,
> Ladengeschäft Rohlf, „Foto: A. Brahms" — nichts davon hat es gegeben. Ebenso die Bildnachweise,
> die Herkunftsangaben und die Besucherbeiträge.

**Echt sind nur die Straßennamen und die Koordinaten**, und das muss so sein: Die Punkte müssen in
der `bbox` aus `tiles/region.json` liegen, sonst zeigt die Karte nichts, und `place_name` muss zum
gebauten Ortsindex passen, sonst findet die Ortssuche im „Hilf mit"-Bereich nichts — und genau die
ist das Herzstück der Vorführung. Straßen und Koordinaten sind ohnehin öffentliche Geografie aus
OpenStreetMap, die mit `make places` in jedes Gerät wandert.

**Ein Personenbezug entstünde erst dadurch, Namen an Adressen zu binden — und diese Bindung ist
frei erfunden.**

Der Grund für den Aufwand: Die echten Aufnahmen gehören dem Heimatmuseum. Sie in einem Repo
mitzuliefern, das jemand klonen kann, ist etwas anderes, als sie im Museum zu zeigen. Dasselbe gilt
für das Ortswappen — siehe [decisions.md](../docs/decisions.md), Punkt 21.

## Was hier liegt

| | |
|---|---|
| `fotos/` | die Bilddateien |
| `seed.json` | alles Übrige: Titel, Datierung, Ort, Schlagwörter, Bildnachweis, Herkunft, Status — und die Besucherbeiträge, die zu jedem Foto gehören |

Beides erzeugt [`tools/build_seed.py`](../tools/build_seed.py) aus einer Tabelle im Skript. Wer den
Bestand ändern will, ändert die Tabelle und lässt das Skript laufen — nicht die Dateien hier:

```bash
python3 tools/build_seed.py
```

Der Lauf ist **deterministisch**: derselbe Aufruf erzeugt denselben Bestand, Byte für Byte.

**Bilder und JSON statt eines Datenbankabzugs**, und das ist die eigentliche Entscheidung: Ein
Abzug ist wertlos, sobald eine Spalte dazukommt. Hier kostet eine neue Spalte eine Zeile je Foto,
und der Bestand muss nicht neu kuratiert werden. Ausserdem geht `make seed` durch die echte
Import-Pipeline — es erzeugt also die Vorschaubilder, füllt das Import-Protokoll und prüft den
Import gleich mit.

Was **nicht** in `seed.json` steht, steht mit Absicht nicht darin: Dateigröße, Abmessungen und
MIME-Typ werden beim Einlesen aus dem Bild gelesen. Eine Kopie davon könnte nur veralten. Der
SHA-256 ist die einzige Ausnahme — er dient allein der Warnung, falls sich eine Datei seit dem
Erzeugen geändert hat.

## Der Bestand ist absichtlich lückenhaft

Ein Bestand, in dem alles vollständig ist, prüft die Hälfte des Programms nicht. Deshalb stehen
darin Fotos ohne Jahr, Fotos ohne Ort und eines ohne beides — sonst hätte der „Hilf mit"-Bereich
nichts vorzulegen:

| | |
|---|---|
| ohne Jahr | 3 |
| ohne Ort | 2 — davon **eines ohne beides** |
| nur straßengenau | 2 — für die Nachschärf-Frage |
| gelöscht | 2, für die Liste, die es dafür gibt |
| Besucherbeiträge | 8, davon **2 zurückgenommen** |
| ohne Bildnachweis | 1 |

**Warum es bei den straßengenauen zwei sind und nicht eines:** Die Nummernauswahl hat zwei Wege,
und ein einziges Foto prüfte immer nur einen davon. „Gasthof Petersen mit Kastanie" liegt an der
Hauptstraße (76 Adressen, 39 Knöpfe nach dem Zusammenfassen) — dort kommt der Abschnittsschritt
davor. „Schulstraße, heutiger Zustand" liegt an der Schulstraße (26 Adressen, 11 Knöpfe) — dort
fällt er weg und die Nummern stehen sofort da.

Die beiden unterscheiden sich auch in der **Quelle**: das eine kommt von einem Besucher, der
„Reicht so — die Straße genügt" gedrückt hat, das andere vom Kurator. Dass auch eine
Kuratorenangabe nachgeschärft werden darf, ist die Aufweichung aus
[decisions.md](../docs/decisions.md), Punkt 32 — sie gehört im Bestand sichtbar.

Dazu unterschiedlich lange Beschreibungen, Hoch- und Querformate und ein paar unaufgeräumte
Dateinamen. `build_seed.py` zählt diese Lücken nach jedem Lauf und **bricht ab, wenn eine fehlt.**
Sie sind kein Versäumnis.

## Für die Entwicklung mit echten Fotos

Wer einen echten Bestand hat, sichert ihn mit `make seed-save` hierher — **aber committet ihn
nicht.** Der erfundene Bestand ist Teil des Repos; ihn durch echte Aufnahmen zu ersetzen ist genau
der Weg, auf dem Museumsfotos doch noch veröffentlicht würden. `make seed-save` sagt das bei jedem
Lauf.
