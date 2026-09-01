<!-- translated-from: docs/index.md -->
<!-- source-sha: 021e53654f2b1a5b2f7429cba2010d3c61701878953aa67fbff95dbf393b62e0 -->

# Dokumentation

Jede Datei in diesem Ordner beantwortet eine andere Frage. Welche das ist, steht in der ersten
Spalte der Tabellen unten; daneben, für wen die Datei geschrieben ist.

**Das Repository spricht Englisch.** Deutsch wird als Übersetzung geführt und trägt das Suffix, das
es sagt: `operations.de.md` ist die deutsche Hälfte von `operations.md`, und
[`tools/check_translations.py`](../tools/check_translations.py) meldet, wenn eine der beiden
Hälften auseinandergelaufen ist. Eine Datei hat keine englische Fassung und braucht keine:
`history.de.md` ist abgeschlossen.

## Kiekmap einrichten und betreiben

| Datei | Frage | Für wen |
|---|---|---|
| [usermanual.de.md](usermanual.de.md) · [en](usermanual.md) | Wie füge ich Fotos hinzu und sichere den Bestand? | das Museumsteam, zum Ausdrucken |
| [operations.de.md](operations.de.md) · [en](operations.md) | Wie richte ich den Pi ein, und was tue ich, wenn er nicht startet? | wer das Gerät am Laufen hält |
| [adaption.de.md](adaption.de.md) · [en](adaption.md) | Wie richte ich das für **einen anderen Ort** ein? | ein zweites Museum |
| [licensing.de.md](licensing.de.md) · [en](licensing.md) | Was darf weitergegeben werden, und unter welchen Bedingungen? | wer veröffentlicht oder übernimmt |

`usermanual` ist die Bedienung, `operations` die Technik dahinter — sie trennen sich nach
Zuständigkeit, nicht nach Schwierigkeit. `adaption` und `licensing` richten sich an ein zweites
Museum, das ein **eigenes** Gerät aufsetzt; dafür ist das Projekt gebaut.

> **Nichts davon ist auf einem Pi erprobt.** Alles unter `deploy/pi/` wurde ohne Gerät gebaut. Der
> erste echte Aufbau ist zugleich die Abnahme — siehe
> [#18](https://github.com/nordfisch/kiekmap/issues/18). Die **Container** sind geprüft, wenn auch
> nur auf einem Mac: Was dort nicht zu prüfen war, sind der USB-Weg der Sicherung und das Verhalten
> nach einem Stromausfall.

## Das System verstehen und anpassen

| Datei | Frage | Für wen |
|---|---|---|
| [architecture.md](architecture.md) | *Was* gibt es, und wie greift es ineinander? | wer einsteigt |
| [development.md](development.md) | *Wie* arbeitet man daran? — Einrichtung, Sprachregelung, Tests, Fallstricke | Entwickler |
| [decisions.md](decisions.md) | *Warum* ist es so und nicht anders? — jede Entscheidung mit Begründung | wer etwas ändern will |
| [archive/history.de.md](archive/history.de.md) | *Wie* ist es dazu gekommen? — dazu das Nummernregister | wer wissen will, ob eine Idee schon einmal da war |

`decisions.md` liest man **vor** einer Änderung, `history.de.md` dann, wenn etwas unerklärlich
aussieht. Die Historie ist deutsch, endet mit v0.8.0 und wird nicht fortgeschrieben: Was die Arbeit
lehrt, wird eine Entscheidung, und wie sie verlief, steht in den Commits und den geschlossenen
Issues. Ihr **Nummernregister** löst die Zitate der Form „Punkt N" auf.

Was offen ist, steht in den [Issues](https://github.com/nordfisch/kiekmap/issues) und in keiner
Datei. Für Coding-Agents kommt [../CLAUDE.md](../CLAUDE.md) dazu — dieselben Regeln, auf das
Nötigste gekürzt, mit den drei Dingen vorneweg, die man hier falsch machen kann.

## Außerhalb von `docs/`

| Datei | Inhalt |
|---|---|
| [../README.de.md](../README.de.md) · [en](../README.md) | Der Einstieg: was das Ganze ist, wie man es startet |
| [../CHANGELOG.de.md](../CHANGELOG.de.md) · [en](../CHANGELOG.md) | Was das Programm kann, nach Keep a Changelog sortiert |
| [../CLAUDE.md](../CLAUDE.md) | Die Regeln dieses Repos, für Coding-Agents |
| [../CONTRIBUTING.md](../CONTRIBUTING.md) | Wie man mitwirkt — und was man erwarten darf, und was nicht |
| [../SECURITY.md](../SECURITY.md) | Was hier eine Schwachstelle ist, was Entwurf, und wohin damit |
| [../CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md) | Der Umgangston, kurz gehalten |
| [../AUTHORS](../AUTHORS) | Wer daran gebaut hat |
| [../seed/README.md](../seed/README.md) | Der Beispielbestand: was `make seed` herstellt und warum seine Lücken Absicht sind |
| [../LICENSE](../LICENSE), [../NOTICE](../NOTICE) | Apache-2.0 im Wortlaut, und die Namensnennung, die mitgeht |

`CHANGELOG.md` und `history.de.md` beschreiben beide Gebautes. Der eine listet **was**, die andere
erzählt **wie und warum**: Wer sucht, ob eine Funktion existiert, nimmt den CHANGELOG; wer wissen
will, warum sie so aussieht, die Historie.
