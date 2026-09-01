<!-- translated-from: docs/licensing.md -->
<!-- source-sha: 714667e177249fc72553255bec21ad8739c5b0a31fd17c4994158e96d9201369 -->

# Weitergabe

Was weitergegeben werden darf, und unter welchen Bedingungen. Diese Datei liest, wer das Projekt
**veröffentlicht**, wer es für einen anderen Ort **übernimmt** oder wer gefragt wird, unter welchem
Recht der Bestand im Museum steht.

> Eine technische Bestandsaufnahme, keine Rechtsberatung. Wo unten deutsches Recht vorkommt, ist es
> Orientierung; für eine verbindliche Auskunft gehört jemand mit Zulassung gefragt.

## Kiekmap selbst

**Apache-Lizenz 2.0**, Copyright 2026 Kalle Erlhoff. Der Text steht in
[../LICENSE](../LICENSE), die Namensnennung in [../NOTICE](../NOTICE). Beide gelten für Code,
Dokumentation und die erfundenen Beispielbilder unter `seed/` — eine Lizenz für alles, ohne
Abgrenzungsfragen. Warum diese und nicht MIT: [decisions.md](decisions.md), Punkt 62.

Der Lizenztext ist **wörtlich der von apache.org** und wird nicht angefasst. Der Platzhalter
`Copyright [yyyy] [name of copyright owner]` in seinem Anhang ist die Vorlage für Dateiköpfe, kein
Feld zum Ausfüllen — ein geänderter Text wird von den üblichen Erkennungswerkzeugen nicht mehr als
Apache-2.0 erkannt.

## Die Wege, auf denen etwas weggeht

Die Pflichten hängen nicht am Projekt, sondern daran, **was jemand in die Hand bekommt**:

| Weg | Was darin steckt | Was mitgehen muss |
|---|---|---|
| **Das Repo** | eigener Code, Doku, Beispielbilder | `LICENSE`, `NOTICE` — liegen an der Wurzel |
| **Die Container-Abbilder** | dazu 37 npm- und 26 Python-Pakete, Schriften, Symbole | `THIRD-PARTY.txt` je Abbild, die Lizenzdateien unter `basemaps/` |
| **Der Update-Stick** | dazu Kartendatei und Ortsindex | zusätzlich der ODbL-Hinweis |
| **Der Bildschirm im Museum** | die laufende Karte | „© OpenStreetMap-Mitwirkende, ODbL" — steht unten rechts |
| **Die Doku-Website** | die Dateien unter `docs/`, dazu MkDocs Material | die Fußzeile nennt beide Lizenzen; sonst reist nichts mit |

## Die Abhängigkeiten, alle permissiv

Gemessen am 20. August 2026 an den **installierten** Paketen, nicht an den Manifestdateien.

| | Pakete | Lizenzen |
|---|---|---|
| Python, ganzes venv | 39 | MIT, BSD-2, BSD-3, Apache-2.0, MIT-CMU (HPND), PSF-2.0 |
| Python, davon im Backend-Abbild | 26 | dieselben |
| npm, ganzer Baum | 128 | 99 × MIT, 16 × ISC, 6 × BSD-3, 3 × Apache-2.0, 2 × BSD-2, 1 × „MIT OR Apache-2.0", 1 × CC-BY-4.0 |
| npm, davon im Frontend-Bundle | 37 | MIT, ISC, BSD-2/3, „MIT OR Apache-2.0" |

**Kein Copyleft.** Die einzige Nicht-Software-Lizenz ist `caniuse-lite` (CC-BY-4.0) — eine
Bauzeit-Datenbank von browserslist, die in keinem Artefakt landet. Nichts schränkt die Wahl der
eigenen Lizenz ein, und nichts steht einer Veröffentlichung im Weg.

**Die Namen und ihre Lizenztexte stehen in `THIRD-PARTY.txt`**, erzeugt von
[../tools/build_notices.py](../tools/build_notices.py) und eingecheckt wie eine Sperrdatei. Warum
erzeugt und nicht gepflegt: Eine handgeschriebene Liste ist in drei Monaten falsch, und zwar in der
Richtung, die niemand prüft. `make notices` schreibt sie, `make check` merkt, wenn sie veraltet
ist.

**Für das Backend kommt die Liste seit dem 25. August 2026 aus `backend/requirements.lock`**, weil
das Abbild genau daraus installiert. Vorher lief das Werkzeug die Abhängigkeiten von
`pyproject.toml` aus selbst ab, mit einer handgeschriebenen Ergänzung für das, was
`uvicorn[standard]` nachzieht — ein nachgebauter Auflöser, der still veraltet wäre. **Ein Paket
fehlte bereits:** `greenlet`, das SQLAlchemy auf Linux mitbringt, stand in keiner Hinweisdatei,
weil es auf dem Entwicklungs-Mac gar nicht installiert wird. Die Umgebungsmarker der Lockdatei
werden jetzt gegen **beide Zielplattformen** ausgewertet, aarch64 und x86_64.

Drei npm-Pakete nennen ihre Lizenz nur in der `package.json` und legen keinen Text bei
(`@protomaps/basemaps`, `pmtiles`, `murmurhash-js`). Sie bekommen die Standardfassung ihrer
Kennung, **mit einem Vermerk, dass der Text nicht aus dem Paket stammt**. Ein Paket ganz ohne
Angabe bricht den Lauf ab.

## Die Karte: hier sitzen die eigentlichen Pflichten

| Bestandteil | Herkunft | Lizenz |
|---|---|---|
| `map.pmtiles` | `build.protomaps.com`, aus OpenStreetMap | **ODbL 1.0** |
| `places.json` und die Tabelle `places` | Overpass-API, aus OpenStreetMap | **ODbL 1.0** |
| Schriften | Noto über `protomaps/basemaps-assets` | OFL 1.1 |
| Symbole | tangrams/icons über dasselbe Archiv | MIT |
| Kartenstil | `@protomaps/basemaps` | BSD-3-Clause |

`tiles/build-tiles.sh` legt die Lizenztexte neben die Dateien, für die sie gelten — unter
`frontend/public/basemaps/`.

**Die Tabelle `places` ist die Stelle, die man übersieht.** Sie steht in `kiekmap.db` und damit in
jeder Sicherung. Für den Museumsbetrieb folgenlos; wer die Datenbank an Dritte weitergibt, gibt
ODbL-Material mit und muss es kenntlich machen. Derselbe Satz steht in
[usermanual.de.md](usermanual.de.md).

## Was **nicht** von der Lizenz erfasst ist

**Der Fotobestand.** Eine Softwarelizenz lizenziert das Programm, nicht die Daten, die es
verarbeitet: Ein Foto in der Datenbank wird kein abgeleitetes Werk des Programms. Das gilt für die
Apache-Lizenz wie für jede andere — auch die GPL zöge Daten nicht hinein. Die Fotos liegen unter
`data/` und sind nicht im Repo.

Die Rechte an ihnen liegen beim Museum und seinen Geberinnen und Gebern, **je Foto einzeln**, und
das System ist dafür gebaut: `credit` ist der Bildnachweis, der neben dem Bild steht, `provenance`
die interne Notiz zu Herkunft und Freigabe. Ein Bestand aus gemischten Rechtelagen ist der
Normalfall, nicht die Ausnahme.

Ob das Museum seine Fotos irgendwann selbst unter eine Lizenz stellt, ist eine davon unabhängige
Entscheidung.

**Das Gemeindewappen.** Urheberrechtlich gemeinfrei (§ 5 Abs. 1 UrhG), in der *Führung* aber als
Hoheitszeichen beschränkt. Deshalb liegt im Repo ein gezeichneter Platzhalter und nicht das Wappen.
Ausführlich in [decisions.md](decisions.md), Punkt 21, und in [adaption.de.md](adaption.de.md).

## Basis-Abbilder und der Verbreitungsweg

`python:3.12-slim` und `nginx:1.27-alpine` bringen Debian- bzw. Alpine-Userland mit und darin
**GPL-lizenzierte Binärprogramme**. Das berührt die Lizenz des eigenen Codes nicht — er läuft
darauf, er ist nicht damit verbunden. Es begründet aber Pflichten für den, der ein **fertiges
Abbild** weitergibt.

**Deshalb: Dockerfiles veröffentlichen, keine gebauten Abbilder.** Dann baut jeder Betreiber
selbst, und die Pflichten bleiben, wo sie hingehören. Der Weg über `images.tar` in
`deploy/pi/update.sh` bleibt für das eigene Gerät richtig; er gehört nur nicht in ein Release.

## Wie das Projekt entstanden ist

Eine Person hat Kiekmap zusammen mit einem Sprachmodell gebaut; die Commits tragen es als
`Co-Authored-By`. Das ist hier vermerkt, weil Verschweigen der schlechtere Umgang damit wäre.

Für die Rechtslage folgt daraus wenig und nichts Überraschendes: Rein maschinell Erzeugtes ist
keine persönliche geistige Schöpfung (§ 2 Abs. 2 UrhG) und damit nicht geschützt; geschützt ist die
Auswahl-, Anordnungs- und Bearbeitungsleistung. Die liegt in diesem Repo offen zutage — in
[decisions.md](decisions.md) stehen die Entscheidungen mit ihren Begründungen, in
[archive/history.de.md](archive/history.de.md) die Fälle, in denen der erste Vorschlag verworfen wurde.

Praktisch heißt das nur eines: **den Anspruch nicht übertreiben.** Die Copyright-Zeile ist
richtig; ein Satz, jede Zeile sei eigenes Werk, wäre es nicht. Wo einzelne Zeilen keine
Schöpfungshöhe erreichen — was für Standardcode ohnehin gilt, mit oder ohne Modell —, hängt an
ihnen keine Lizenz. Sie sind dann freier als der Rest, nicht ungültig.

## Haftung

Abschnitt 7 und 8 der Lizenz schließen Gewährleistung und Haftung aus, so weit das geht. Weiter
als das Recht erlaubt, geht keine Lizenz: § 276 Abs. 3 BGB lässt einen Erlass der Haftung für
Vorsatz nicht zu, und § 309 Nr. 7 BGB begrenzt Freizeichnungen.

Was das Risiko klein hält, ist deshalb nicht die Klausel, sondern die **Unentgeltlichkeit** — wer
verschenkt, haftet im Kern nur für Vorsatz und grobe Fahrlässigkeit. Daraus folgt eine einzige
Verhaltensregel: **keine Zusicherungen machen.** Nicht versprechen, dass der Bestand sicher ist,
dass die Sicherung funktioniert, dass das Gerät durchläuft. Was das Programm kann, steht im
Änderungsprotokoll; was ungeprüft ist, steht in den [Issues](https://github.com/nordfisch/kiekmap/issues) und in
[index.de.md](index.de.md).
