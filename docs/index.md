# Dokumentation

Neun Dateien, jede mit genau einer Frage. Wer hier landet und nicht weiß, wohin: **Die erste
Spalte sagt, was drinsteht, die zweite, für wen, die dritte, in welcher Sprache.**

Die Sprache folgt dem Publikum: Deutsch für Besucher, Museumsteam und Betreiber, Englisch für
Entwickler. Jeder Text existiert genau einmal, nichts steht doppelt. „Wird englisch" heißt, dass
die Übersetzung noch aussteht — die Regel gilt seit dem 30. August 2026, siehe
[decisions.md](decisions.md), Punkt 68.

## Das System verstehen

| Datei | Frage | Für wen | Sprache |
|---|---|---|---|
| [architecture.md](architecture.md) | *Was* gibt es, und wie greift es ineinander? | wer einsteigt | Englisch |
| [decisions.md](decisions.md) | *Warum* ist es so und nicht anders? — jede Entscheidung mit Begründung | wer etwas ändern will | Englisch |
| [history.md](history.md) | *Wie* ist es dazu gekommen? — und was dabei anders kam als geplant | wer wissen will, ob eine Idee schon einmal da war | Deutsch, eingefroren |

`decisions.md` ist die Datei, die man **vor** einer Änderung liest; `history.md` die, die man liest,
wenn etwas unerklärlich aussieht. Meist steht dort, warum.

`history.md` endet mit v0.8.0 am 25. August 2026 und wird nicht fortgeschrieben. An ihre Stelle
tritt keine zweite Datei: Was die Arbeit lehrt, wird eine Entscheidung in `decisions.md`, und wie
sie verlief, steht in den Commits und den geschlossenen Issues.

## Daran arbeiten

| Datei | Frage | Für wen | Sprache |
|---|---|---|---|
| [development.md](development.md) | *Wie* arbeitet man daran? — Einrichtung, Sprachregelung, Tests, Fallstricke | Entwickler | Englisch |
| [backlog.md](backlog.md) | Was fehlt noch? — nach Bereich geordnet, jeder Punkt mit Nummer, Art und Einordnung | wer etwas aufgreifen will | Deutsch |

Für Coding-Agents kommt [../CLAUDE.md](../CLAUDE.md) dazu — dieselben Regeln, auf das Nötigste
gekürzt, mit den drei Dingen vorneweg, die man hier falsch machen kann.

## Es übernehmen

| Datei | Frage | Für wen | Sprache |
|---|---|---|---|
| [adaption.md](adaption.md) | Wie richte ich das für **einen anderen Ort** ein? | ein zweites Museum | Deutsch |
| [licensing.md](licensing.md) | Was darf weitergegeben werden, und unter welchen Bedingungen? | wer veröffentlicht oder übernimmt | Deutsch |

Diese beiden standen bis zum 21. August 2026 unter „Daran arbeiten" und waren dort falsch
einsortiert: Sie richten sich nicht an jemanden, der *dieses* Gerät weiterbaut, sondern an
jemanden, der ein **eigenes** aufsetzt. Das sind zwei verschiedene Leute mit zwei verschiedenen
Fragen, und die zweite Frage ist der eigentliche Zweck des Projekts.

## Das Gerät betreiben

| Datei | Frage | Für wen | Sprache |
|---|---|---|---|
| [operations.md](operations.md) | Wie richte ich den Pi ein, und was tue ich, wenn er nicht startet? | wer das Gerät am Laufen hält | Deutsch |
| [usermanual.md](usermanual.md) | Wie füge ich Fotos hinzu und sichere den Bestand? | das Museumsteam, zum Ausdrucken | Deutsch |

Die beiden trennen sich nach Zuständigkeit, nicht nach Schwierigkeit: `usermanual.md` ist die
Bedienung, `operations.md` die Technik dahinter.

> **Was darin steht, ist auf keinem Pi erprobt.** Alles unter `deploy/pi/` wurde ohne Gerät
> gebaut. Der erste echte Aufbau ist zugleich die Abnahme — siehe [backlog.md](backlog.md).
> Die **Container** sind seit dem 14. August 2026 geprüft, wenn auch auf einem Mac: Was dort nicht
> zu prüfen war, sind der USB-Weg der Sicherung und das Verhalten nach einem Stromausfall.

## Ausserhalb von `docs/`

| Datei | Inhalt | Sprache |
|---|---|---|
| [../README.md](../README.md) | Der Einstieg: was das Ganze ist, wie man es startet | Deutsch |
| [../CHANGELOG.md](../CHANGELOG.md) | Was das Programm kann, nach Keep a Changelog sortiert | Deutsch |
| [../CLAUDE.md](../CLAUDE.md) | Die Regeln dieses Repos, für Coding-Agents | Englisch |
| [../seed/README.md](../seed/README.md) | Der Beispielbestand: was `make seed` herstellt und warum seine Lücken Absicht sind | Deutsch |
| [../CONTRIBUTING.md](../CONTRIBUTING.md) | Wie man mitwirkt — und was man erwarten darf, und was nicht | Englisch |
| [../SECURITY.md](../SECURITY.md) | Was hier eine Schwachstelle ist, was Entwurf, und wohin damit | Deutsch |
| [../CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md) | Der Umgangston, kurz gehalten | Deutsch |
| [../AUTHORS](../AUTHORS) | Wer daran gebaut hat — und wie das Projekt entstanden ist | Deutsch |
| [../LICENSE](../LICENSE), [../NOTICE](../NOTICE) | Apache-2.0 im Wortlaut, und die Namensnennung, die mitreist | Englisch, Deutsch |

`CHANGELOG.md` und `history.md` beschreiben beide Gebautes und sind trotzdem beide da: Der eine
listet **was**, die andere erzählt **wie und warum**. Wer sucht, ob eine Funktion existiert, nimmt
den CHANGELOG; wer wissen will, warum sie so aussieht, die Historie.
