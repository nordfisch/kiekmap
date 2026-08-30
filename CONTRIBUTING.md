# Mitwirken

Kiekmap ist ein Touchscreen-Kiosk für das Heimatmuseum in Holm: historische Ortsfotos auf einer
Karte, offline auf einem Raspberry Pi. Es ist ausdrücklich dafür gebaut, dass ein **zweites Museum
es übernimmt** — ohne Fork, nur mit eigener `region.json` und `.env`.

## Was hier zu erwarten ist, und was nicht

Ehrlich vorweg, damit eine Veröffentlichung keine stille Zusage wird:

**Ein Betreuer, nebenher.** Es gibt keine zugesagte Antwortzeit, keine Gewährleistung, keinen
Support. Eine Meldung kann Wochen liegen bleiben. Ein Beitrag kann abgelehnt werden, weil er nicht
zum Zweck des Geräts passt — das ist keine Kritik an der Arbeit.

**Was am meisten hilft**, in dieser Reihenfolge:

1. **Ein zweites Museum, das es aufsetzt und berichtet.** [adaption.md](docs/adaption.md) ist ohne
   Gerät geschrieben worden; jeder Stolperstein daraus ist wertvoller als jede Funktion.
2. **Fehlerberichte vom echten Betrieb** — vom Pi, vom Touchscreen, aus dem Museum. Alles unter
   `deploy/pi/` ist bis heute ungeprüft.
3. **Verständlichere Dokumentation.** Wer sie zum ersten Mal liest, sieht die Lücken, die der
   Autor nicht mehr sieht.
4. Code.

## Einrichten

```bash
make dev          # Backend auf 8000, Frontend auf 5173, beide mit Hot Reload
make seed         # den erfundenen Beispielbestand herstellen
```

Ausführlich in [development.md](docs/development.md). Für den Verwaltungsbereich braucht es eine
PIN: `cd backend && .venv/bin/python -m app.cli pin` erzeugt die Zeile für die `.env`.

## Die Regeln dieses Repos

Sie stehen vollständig in [CLAUDE.md](CLAUDE.md) und in [development.md](docs/development.md).
Das Wichtigste:

- **`make check` vor jedem Commit.** Stil, sechs Prüfungen, alle Tests. Der Hook unter `.githooks/`
  nimmt einem die schnellen davon ab: `git config core.hooksPath .githooks`.
- **Sprachregelung nach Publikum.** Jeder Text existiert einmal, in der Sprache seiner Leser.
  Deutsch: Oberfläche, CLI, Doku für Museum und Betrieb, Issues, Testdateien. Englisch:
  Bezeichner, Kommentare, Entwicklerdoku und Commit-Nachrichten. Umlaute in deutschen Texten für
  Menschen normal, im Quelltext umschrieben.
- **Jede fachliche Entscheidung bekommt einen Test, der den Fehlerfall beschreibt.** Die
  wertvollsten Tests hier decken Fehler ab, die *still* passieren würden.
- **Nichts Ortsspezifisches in den Code.** Keine Koordinate, kein Ortsname, keine
  sammlungsabhängige Zahl — das kommt nach `region.json` oder in die Einstellungen. Testdaten
  sind ausgenommen.
- **Keine Namen aus dem echten Bestand**, auch nicht im Kommentar. Der Beispielbestand stellt
  einen erfundenen Kader; er steht in [development.md](docs/development.md).
- **Ein erledigter Punkt wird an drei Stellen vermerkt**, nicht an neun: CHANGELOG, `history.md`,
  `backlog.md` — dazu `decisions.md`, wenn eine Entscheidung herauskam.

## Eine Idee oder ein Fehler

Erst in [backlog.md](docs/backlog.md) nachsehen, ob es den Punkt schon gibt, und in
[history.md](docs/history.md), ob die Sache schon einmal versucht wurde. Dann eine Meldung
aufmachen; die Vorlagen fragen nach dem Nötigen.

**Backlogpunkte tragen feste Nummern**, unter denen sie zitiert werden („Punkt 15"). Nummern
werden nie neu vergeben, auch nicht nach dem Erledigen. `tools/check_numbers.py` rechnet das nach.

## Der Weg eines Beitrags

1. **Fork**, dann ein Branch pro Thema: `feature/kurzer-name` oder `fix/kurzer-name`.
2. Arbeiten, `make check` grün bekommen. Conventional Commits (`feat:`, `fix:`, `docs:` …) —
   daran halten sich hier über 99 Prozent der Commits. **Neue Commit-Nachrichten sind englisch**;
   alles vor dem 30. August 2026 ist deutsch und bleibt es.
3. **Pull Request gegen `develop`**, nicht gegen `main`. `main` ist der Stand, der im Museum läuft,
   und bekommt nur Merges aus `develop`. Näheres in [development.md](docs/development.md).
4. Gemerged wird mit einem **Merge-Commit**. Squash und Rebase sind für dieses Repo abgeschaltet:
   Die Dokumentation zitiert einzelne Commits mit Hash, ein Squash vernichtet sie, und ein Rebase
   schreibt sie neu und wirft dabei die Signaturen weg.

## Lizenz der Beiträge

Das Projekt steht unter der [Apache-Lizenz 2.0](LICENSE). Nach ihrem **§5** steht jeder Beitrag,
den jemand hier einreicht, automatisch unter derselben Lizenz — eine gesonderte Vereinbarung
(CLA) gibt es nicht und braucht es nicht. Wer eine Datei ändert, kennzeichnet sie als geändert
(**§4.2**); der Kopf jeder Quelldatei trägt dafür zwei SPDX-Zeilen. Näheres in
[licensing.md](docs/licensing.md).

Wer möchte, trägt sich in [AUTHORS](AUTHORS) ein.
