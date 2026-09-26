<!-- translated-from: docs/museum/collection.md -->
<!-- source-sha: b8b1fd38fa78d0e1b0cffeed2d18bb37d220051047b0c38d4b2670fe1e8bb90d -->

# Die erste Sammlung aufbauen

Ein Museum, das Kiekmap übernimmt, beginnt mit einem Archiv: ein paar hundert oder ein paar tausend
Scans, auf einer Festplatte, in Ordner sortiert. Diese Seite bringt sie in das Gerät.

Es ist die einmalige Arbeit. Einzelne Fotos später hinzuzufügen steht in der
[Anleitung für das Museumsteam](usermanual.md) — der überwachte Ordner oder der Upload im
Verwaltungsbereich. Beides ist nicht für dreitausend Dateien gebaut, und deshalb läuft die erste
Befüllung auf der Kommandozeile.

Das Gerät an den Ort anzupassen kommt davor: Karte, Ortsindex und Einstellungen stehen in
[Für einen anderen Ort einrichten](adaption.md). Diese Seite beginnt, wo jene endet.

---

## Vor allem anderen: eine Kopie

Zwei Befehle auf dieser Seite löschen die Sammlung, und zurück bringt sie nur eine Kopie. Legen Sie
sie vorher an:

```bash
cp -a data/ ~/kiekmap-data-backup/
```

**Mitsamt den Dateien `-wal` und `-shm` neben `data/kiekmap.db`.** SQLite schreibt dort hinein und
überträgt den Inhalt später; eine Kopie ohne sie steht auf dem Stand des letzten Checkpoints, und
der Unterschied fällt erst auf, wenn jemand sie zurückspielt.

Auf einem Gerät, das schon läuft, ist die Sicherung im Verwaltungsbereich der bessere Weg — sie
steht in der [Anleitung für das Museumsteam](usermanual.de.md#sicherung-auf-einen-usb-stick).

---

## Wo ein Befehl läuft

**Auf dem Entwicklungsrechner**, auf dem die Karte gebaut wurde, in der virtuellen Umgebung des
Backends:

```bash
cd backend && .venv/bin/python -m app.cli stats
```

**Auf dem Gerät gibt es keine virtuelle Umgebung.** Der Pi trägt die Software als Image, nicht als
Python-Installation, und derselbe Befehl läuft dort im Container:

```bash
cd /opt/kiekmap && docker compose -f deploy/docker-compose.yml --env-file .env \
    run --rm backend python -m app.cli stats
```

Aus `/opt/kiekmap` und mit `--env-file`, nie aus `deploy/` — der Grund steht im
[Betriebshandbuch](operations.de.md#einstellungen-im-containerbetrieb), und er gilt für jeden
`docker compose`-Befehl auf dem Gerät.

**Beide füllen ein anderes `data/`**, und das entscheidet, wo die Arbeit stattfindet. Die Sammlung
auf dem Entwicklungsrechner aufzubauen und das Ergebnis hinüberzubringen ist der einfachere Weg:
Dort liegt das Archiv, die Umwandlung braucht Rechenzeit, und ein Fehler kostet nichts auf einem
Rechner, auf den niemand wartet. Die fertige Sammlung erreicht das Gerät dann wie jede Sicherung —
auf einen USB-Stick schreiben und dort zurückspielen, siehe
[Eine Sicherung zurückspielen](usermanual.de.md#eine-sicherung-zurückspielen).

Direkt auf dem Pi zu importieren funktioniert. Für ein paar tausend Scans dauert es Stunden, und
das Museum kann das Gerät währenddessen nicht benutzen.

---

## Die Reihenfolge der Schritte

### 1. Karte, Ortsindex, Einstellungen

```bash
make tiles     # Karte, Schriften und Sprites für die Region
make places    # Ortsindex bauen und einlesen
```

Beides braucht das Internet und steht in
[Für einen anderen Ort einrichten](adaption.de.md#2-kartendaten-und-ortsindex-bauen). Der Ortsindex
zählt auch für den Import, nicht nur für die Karte: **Ein Ordnername verortet ein Foto nur dort, wo
der Ortsindex die Straße kennt.**

Die Import-Einstellungen gehören vor das erste Foto in die `.env`, nicht danach:
`KIEKMAP_EXIF_DATE_MAX_YEAR`, `KIEKMAP_IMPORT_TAGS`, `KIEKMAP_IMPORT_CREDIT`,
`KIEKMAP_IMPORT_PROVENANCE`. Was jede davon tut, steht in
[Schritt 5 der Übernahme](adaption.de.md#5-sammlungsspezifisches-prüfen). Sie wirken im Augenblick
des Imports; sie danach zu ändern ändert nichts an den Fotos, die schon drin sind.

### 2. Die Beispielsammlung entfernen

Eine frische Installation trägt die erfundene Beispielsammlung, damit das Gerät etwas zeigt, bevor
es etwas enthält. Sie geht, bevor das echte Archiv kommt:

```bash
make empty
```

Der Befehl nennt, was er zerstören wird, und **verlangt, die Zahl der Fotos einzutippen**. Eine
Frage, die man mit „j" beantwortet, beantwortet man ungelesen; eine Zahl nicht.

### 3. Alles wird JPEG

Museumsarchive sind gemischt: Scans als TIFF, ein Bildschirmfoto als PNG, ein Bild von einer
Webseite als WEBP. Die Sammlung besteht durchgehend aus JPEG, und nicht der Ordnung wegen — **ein
Browser kann kein TIFF anzeigen.** Der Kiosk würde ein Vorschaubild zeigen und ein Original
herausgeben, das nichts öffnet.

```bash
python3 tools/to_jpeg.py ~/Archiv ~/Archiv-Import/Straßen
```

Der Baum wird kopiert, die Quelle bleibt, wie das Museum sie geschickt hat. Der Lauf meldet:

```text
2431 files looked at:
  copied     1840
  converted  588
  skipped    3
```

`skipped` ist alles, was kein Bild ist — eine Textdatei, eine Tabelle. `failed` erscheint nur, wenn
eine Datei nicht gelesen werden konnte, und nennt jede einzelne.

**Der Name des Zielordners ist Teil der Herkunft.** `KIEKMAP_IMPORT_PROVENANCE` wird dem Pfad darin
vorangestellt, damit die Herkunft eines Fotos zurück zur Datei im eigenen Archiv des Museums führt.
Wählen Sie den Namen entsprechend.

### 4. Der Import

```bash
cd backend && .venv/bin/python -m app.cli import ~/Archiv-Import/Straßen
```

Die Originale bleiben liegen; der Import kopiert, was er aufnimmt. Er meldet:

```text
588 files looked at:
  taken in    571
  duplicates  14
  rejected    3
    ! Kein lesbares Bild: cannot identify image file '/home/museum/Archiv-Import/Straßen/Mühlenweg/12/scan-0043.jpg'
```

- **taken in** — in der Sammlung, mit Vorschaubild, im Verwaltungsbereich sichtbar.
- **duplicates** — diese Datei war schon da, erkannt an ihrem Inhalt. Nichts wurde geändert.
- **rejected** — nicht aufgenommen, mit einem Grund je Datei. Meist eine kaputte Datei oder ein
  Format, das die Sammlung nicht führt. Die Gründe erscheinen in der Sprache, auf die das Gerät
  eingestellt ist; die Beschriftungen darum herum sind englisch.

Ein abgewiesenes Foto steht auch im Importprotokoll des Verwaltungsbereichs, es geht also nichts
verloren, wenn man daran vorbeiscrollt.

### 5. Prüfen

```bash
cd backend && .venv/bin/python -m app.cli stats
```

```text
Photos in total       1284
  on the map          1102
  without a place     182
  without a year      766

85 % have a place and are therefore on the map.
```

**Ohne Jahr ist der Normalfall** und kein Fehler des Imports — die meisten historischen Fotografien
tragen kein Datum. Dafür gibt es die Mitmach-Spalte: Besucher füllen die Lücken, und das Museum
bestätigt sie. Ein Foto **ohne Ort** liegt nicht auf der Karte, und das ist die Zahl, an der zu
arbeiten sich lohnt.

Danach die Bilder, die zweimal hereinkamen, ohne dieselbe Datei zu sein:

```bash
cd backend && .venv/bin/python -m app.cli duplicates
```

```text
5 groups, 11 photos, distance up to 40

--- group 1 (2 photos) ---
  photo   502  3543x3543  ----  Mühlenweg 3                Gasthof Petersen
  photo  1235  3366x3366  1928  Mühlenweg 3                Gasthof Petersen
```

Der Import erkennt eine Dublette **allein am Inhalt der Datei**. Dasselbe Bild ein zweites Mal
gescannt, neu kodiert oder mit anderen Metadaten gespeichert ist eine andere Datei und kommt erneut
herein. Dieser Befehl findet solche Paare nachträglich, indem er die Bilder selbst vergleicht.
`--distance` sagt, wie verschieden zwei Bilder sein dürfen und trotzdem als Paar erscheinen; 40 von
256 Bit ist die Voreinstellung, eine kleinere Zahl findet weniger und sicherere Paare.

Was bleibt, entscheidet ein Mensch. Das größte Bild ist der übliche Kandidat und nicht immer der
richtige — eine Bildunterschrift kann an der kleineren Fassung hängen. Gelöscht wird im
Verwaltungsbereich.

### 6. Erschließen

Der Rest ist keine Arbeit für ein Programm. Fotos ohne Beschreibung, ohne Titel, ohne Ort schreibt,
wer das Bild ansieht und den Ort kennt. Der Verwaltungsbereich führt hinein: Seine Übersicht nennt
die Lücken, und jede davon öffnet die Liste dahinter.

---

## Was der Import liest und was nicht

**Ein EXIF-Datum auf einem Scan ist das Datum des Scans.** Eine Fotografie von 1928, im Jahr 2019
gescannt, trägt 2019 in der Datei. Als Aufnahmedatum genommen läge sie am rechten Ende des
Zeitreglers, zählte als datiert und würde keinem Besucher je zur Korrektur angeboten.
`KIEKMAP_EXIF_DATE_MAX_YEAR` zieht die Grenze: Ein Datum von diesem Jahr an datiert ein Foto nicht.
Wo die Datei ihr Gerät nennt, stellt sich die Frage nicht — ein Scanner datiert nie, eine Kamera
immer.

**Ein Ordnername verortet ein Foto**, wenn der Ortsindex die Straße kennt. `Mühlenweg/12/` legt
jedes Bild darunter an den Mühlenweg 12. Ein nach Straße und Hausnummer sortiertes Archiv verortet
sich selbst; ein anders sortiertes bleibt einfach unberührt, und gemeldet wird dafür nichts.

**Eine Koordinate in der Datei wird gelesen, und eine Hausnummer aus dem Ordner sticht sie.**
Eine EXIF-Koordinate sieht wie eine Messung aus und ist oft keine: In der ersten Sammlung
teilten 278 von 413 solcher Fotos ihre Koordinate mit einem anderen — eingetippte Werte, keine
gemessenen. Ein Ordner, der Straße und Hausnummer nennt, ist die bessere Aussage, und der
Import behandelt ihn als solche.

**Eine Dublette wird am Inhalt der Datei erkannt.** Zwei Dateien mit gleichem Inhalt sind dasselbe
Foto, wie immer sie heißen. Zwei Dateien mit gleichem Bild und anderen Metadaten sind zwei Fotos,
und der Befehl `duplicates` ist die Antwort darauf — siehe oben.

---

## Alle Befehle

Die Befehle von `python -m app.cli`. Auf dem Entwicklungsrechner mit `.venv/bin/python` davor, auf
dem Gerät im Container — siehe [oben](#wo-ein-befehl-läuft).

<!-- cli-table -->

| Befehl | Argumente | Was er tut | Ändert die Sammlung |
|---|---|---|---|
| `import` | `<path>` | Nimmt ein Verzeichnis auf. Die Originale bleiben liegen. | ja |
| `scan` | | Durchsucht den überwachten Ordner einmal, so wie der Dienst es von selbst tut. | ja |
| `stats` | | Wie viel in der Sammlung ist und was ihr fehlt. | nein |
| `duplicates` | `--distance N` | Dasselbe Bild mehrfach, gefunden durch Bildvergleich. | nein |
| `places` | | Liest den Ortsindex erneut ein, nach `make places` oder einer neuen `places.json`. | ja |
| `pin` | | Fragt zweimal nach einer PIN und gibt die Zeile für die `.env` aus. | nein |
| `seed-export` | | Schreibt die Sammlung nach `seed/`. **Nur für die Entwicklung.** | nein |
| `seed-load` | | Löscht die Sammlung und baut sie aus `seed/` neu auf. **Nur für die Entwicklung.** | ja |
| `empty` | `--yes` | Löscht die ganze Sammlung. Fragt vorher. | ja |

`seed-export` und `seed-load` dienen der Entwicklung: Sie tragen die erfundene Beispielsammlung, mit
der dieses Projekt getestet wird. Ein Museum braucht keinen von beiden, und `seed-load` würde sein
Archiv wegwerfen.

Jeder Befehl beantwortet `--help`, und jeder ihrer Namen ebenso:
`python -m app.cli import --help`.

---

## Was nicht rückgängig zu machen ist, und was sich verweigert

**`empty` löscht die Sammlung und setzt nichts an ihre Stelle.** Datensätze, Originale und
Vorschaubilder, alle. Karte, Ortsindex und Einstellungen bleiben. Der Befehl zeigt zuerst die Zahlen
und verlangt, die Zahl der Fotos einzutippen. `--yes` überspringt die Frage und ist für Skripte
gedacht; an einer Tastatur ist es die falsche Antwort.

**`seed-load` leert die Sammlung ebenfalls** und setzt die erfundene Beispielsammlung an ihre
Stelle. Auf dem Rechner eines Museums ist das derselbe Verlust.

**Ein schreibender Befehl verweigert sich, solange eine Sicherung zurückgespielt wird.** Das
Zurückspielen tauscht die Datenbank unter einem laufenden Import aus, und die währenddessen
geschriebenen Datensätze stünden in gar keiner Sammlung. Der Befehl bemerkt es und endet, ohne etwas
zu tun:

```text
A restore is running. Nothing was changed.
```

Führen Sie ihn erneut aus, wenn das Zurückspielen fertig ist. Welche Befehle schreiben, steht in der
Tabelle oben.
