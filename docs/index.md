# Dokumentation

In diesem Ordner liegen acht Dateien, und jede beantwortet eine andere Frage. Welche das ist, steht
in der ersten Spalte der Tabellen unten; daneben, für wen die Datei geschrieben ist und in welcher
Sprache.

Die Sprache richtet sich nach den Lesern. Alles, was Besucher, Museumsteam und Betreiber angeht,
ist deutsch; alles, was beim Arbeiten am Code gebraucht wird, englisch. 

## Kiekmap einrichten und betreiben

| Datei | Frage | Für wen | Sprache |
|---|---|---|---|
| [usermanual.md](usermanual.md) | Wie füge ich Fotos hinzu und sichere den Bestand? | das Museumsteam, zum Ausdrucken | Deutsch |
| [operations.md](operations.md) | Wie richte ich den Pi ein, und was tue ich, wenn er nicht startet? | wer das Gerät am Laufen hält | Deutsch |
| [adaption.md](adaption.md) | Wie richte ich das für **einen anderen Ort** ein? | ein zweites Museum | Deutsch |
| [licensing.md](licensing.md) | Was darf weitergegeben werden, und unter welchen Bedingungen? | wer veröffentlicht oder übernimmt | Deutsch |

`usermanual.md` ist die Bedienung, `operations.md` die Technik dahinter — sie trennen sich nach
Zuständigkeit, nicht nach Schwierigkeit. `adaption.md` und `licensing.md` richten sich an ein
zweites Museum, das ein **eigenes** Gerät aufsetzt; dafür ist das Projekt gebaut.

> **Was darin steht, ist auf keinem Pi erprobt.** Alles unter `deploy/pi/` wurde ohne Gerät gebaut.
> Der erste echte Aufbau ist zugleich die Abnahme — siehe
> [#18](https://github.com/nordfisch/kiekmap/issues/18). Die **Container** sind geprüft, wenn
> auch nur auf einem Mac: Was dort nicht zu prüfen war, sind der USB-Weg der Sicherung und das
> Verhalten nach einem Stromausfall.

## Das System verstehen und anpassen

| Datei | Frage | Für wen | Sprache |
|---|---|---|---|
| [architecture.md](architecture.md) | *Was* gibt es, und wie greift es ineinander? | wer einsteigt | Englisch |
| [development.md](development.md) | *Wie* arbeitet man daran? — Einrichtung, Sprachregelung, Tests, Fallstricke | Entwickler | Englisch |
| [decisions.md](decisions.md) | *Warum* ist es so und nicht anders? — jede Entscheidung mit Begründung | wer etwas ändern will | Englisch |
| [history.md](history.md) | *Wie* ist es dazu gekommen? — dazu das Nummernregister | wer wissen will, ob eine Idee schon einmal da war | Deutsch, abgeschlossen |

`decisions.md` liest man **vor** einer Änderung, `history.md` dann, wenn etwas unerklärlich
aussieht. Die Historie endet mit v0.8.0 und wird nicht fortgeschrieben: Was die Arbeit lehrt, wird
eine Entscheidung, und wie sie verlief, steht in den Commits und den geschlossenen Issues. Ihr
**Nummernregister** löst die Zitate der Form „Punkt N" auf.

Was offen ist, steht in den [Issues](https://github.com/nordfisch/kiekmap/issues) und in keiner
Datei. Für Coding-Agents kommt [../CLAUDE.md](../CLAUDE.md) dazu — dieselben Regeln, auf das
Nötigste gekürzt, mit den drei Dingen vorneweg, die man hier falsch machen kann.

## Außerhalb von `docs/`

| Datei | Inhalt | Sprache |
|---|---|---|
| [../README.md](../README.md) | Der Einstieg: was das Ganze ist, wie man es startet | Deutsch |
| [../CHANGELOG.md](../CHANGELOG.md) | Was das Programm kann, nach Keep a Changelog sortiert | Deutsch |
| [../CLAUDE.md](../CLAUDE.md) | Die Regeln dieses Repos, für Coding-Agents | Englisch |
| [../CONTRIBUTING.md](../CONTRIBUTING.md) | Wie man mitwirkt — und was man erwarten darf, und was nicht | Englisch |
| [../SECURITY.md](../SECURITY.md) | Was hier eine Schwachstelle ist, was Entwurf, und wohin damit | Deutsch |
| [../CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md) | Der Umgangston, kurz gehalten | Deutsch |
| [../AUTHORS](../AUTHORS) | Wer daran gebaut hat | Deutsch |
| [../seed/README.md](../seed/README.md) | Der Beispielbestand: was `make seed` herstellt und warum seine Lücken Absicht sind | Deutsch |
| [../LICENSE](../LICENSE), [../NOTICE](../NOTICE) | Apache-2.0 im Wortlaut, und die Namensnennung, die mitreist | Englisch, Deutsch |

`CHANGELOG.md` und `history.md` beschreiben beide Gebautes. Der eine listet **was**, die andere
erzählt **wie und warum**: Wer sucht, ob eine Funktion existiert, nimmt den CHANGELOG; wer wissen
will, warum sie so aussieht, die Historie.
