# Beispielbestand

Ein kleiner Fotobestand zum Entwickeln und Ausprobieren. Er ersetzt das, was vorher jeder für sich
von Hand in `data/` zusammengeklickt hat — und was niemand sonst hatte.

```bash
make seed        # Bestand aus diesem Ordner herstellen (loescht den vorhandenen!)
make seed-save   # den laufenden Bestand hierher sichern
```

## Was hier liegt

| | |
|---|---|
| `fotos/` | die Bilddateien unter ihren ursprünglichen Namen |
| `seed.json` | alles Übrige: Titel, Datierung, Ort, Schlagwörter, Bildnachweis, Herkunft, Status — und die Besucherbeiträge, die zu jedem Foto gehören |

**Bilder und JSON statt eines Datenbankabzugs**, und das ist die eigentliche Entscheidung: Ein
Abzug ist wertlos, sobald eine Spalte dazukommt. Hier kostet eine neue Spalte eine Zeile je Foto,
und der Bestand muss nicht neu kuratiert werden. Ausserdem geht `make seed` durch die echte
Import-Pipeline — es erzeugt also die Vorschaubilder, füllt das Import-Protokoll und prüft den
Import gleich mit.

Was **nicht** hier steht, steht mit Absicht nicht hier: SHA-256, Dateigröße, Abmessungen und
MIME-Typ werden beim Einlesen aus dem Bild gelesen. Eine Kopie davon könnte nur veralten. Der
SHA-256 in `seed.json` ist die einzige Ausnahme — er dient allein der Warnung, falls sich eine
Datei seit dem Sichern geändert hat.

## Warum der Ordner leer sein kann

**Die Bilder sind nicht im Repo.** Es sind echte historische Aufnahmen aus Holm; sie gehören dem
Heimatmuseum, und ob sie mitgeliefert werden dürfen und sollen, ist noch nicht entschieden —
siehe [docs/backlog.md](../docs/backlog.md), Abschnitt *Versionierung, Releaseprozess und
Veröffentlichung des Codes*.

Bis das geklärt ist, gilt: `make seed` sagt im Klartext, dass hier nichts liegt, und wer einen
eigenen Bestand hat, sichert ihn mit `make seed-save` hierher.

## Der Bestand ist absichtlich lückenhaft

Ein Bestand, in dem alles vollständig ist, prüft die Hälfte des Programms nicht. Deshalb stehen
darin Fotos ohne Jahr, Fotos ohne Ort und eines ohne beides — sonst hätte der „Hilf mit"-Bereich
nichts vorzulegen. Ebenso: unterschiedlich lange Beschreibungen, Hoch- und Querformate, gelöschte
Fotos für die entsprechende Liste und ein paar Besucherbeiträge, von denen einer zurückgenommen
ist.

Wer den Bestand ändert, sollte diese Lücken erhalten. Sie sind kein Versäumnis.
