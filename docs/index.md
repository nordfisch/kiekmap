# Dokumentation

Acht Dateien, jede mit genau einer Frage. Wer hier landet und nicht weiß, wohin: **Die erste
Spalte sagt, was drinsteht, die zweite, für wen.**

## Das System verstehen

| Datei | Frage | Für wen |
|---|---|---|
| [architecture.md](architecture.md) | *Was* gibt es, und wie greift es ineinander? | wer einsteigt |
| [decisions.md](decisions.md) | *Warum* ist es so und nicht anders? — jede Entscheidung mit Begründung | wer etwas ändern will |
| [history.md](history.md) | *Wie* ist es dazu gekommen? — und was dabei anders kam als geplant | wer wissen will, ob eine Idee schon einmal da war |

`decisions.md` ist die Datei, die man **vor** einer Änderung liest; `history.md` die, die man liest,
wenn etwas unerklärlich aussieht. Meist steht dort, warum.

## Daran arbeiten

| Datei | Frage | Für wen |
|---|---|---|
| [development.md](development.md) | *Wie* arbeitet man daran? — Einrichtung, Sprachregelung, Tests, Fallstricke | Entwickler |
| [backlog.md](backlog.md) | Was fehlt noch? — nach Bereich geordnet, jeder Punkt mit Nummer, Art und Einordnung | wer etwas aufgreifen will |
| [adaption.md](adaption.md) | Wie richte ich das für **einen anderen Ort** ein? | ein zweites Museum |

Für Coding-Agents kommt [../CLAUDE.md](../CLAUDE.md) dazu — dieselben Regeln, auf das Nötigste
gekürzt, mit den drei Dingen vorneweg, die man hier falsch machen kann.

## Das Gerät betreiben

| Datei | Frage | Für wen |
|---|---|---|
| [operations.md](operations.md) | Wie richte ich den Pi ein, und was tue ich, wenn er nicht startet? | wer das Gerät am Laufen hält |
| [usermanual.md](usermanual.md) | Wie füge ich Fotos hinzu und sichere den Bestand? | das Museumsteam, zum Ausdrucken |

Die beiden trennen sich nach Zuständigkeit, nicht nach Schwierigkeit: `usermanual.md` ist die
Bedienung, `operations.md` die Technik dahinter.

> **Was darin steht, ist auf keinem Pi erprobt.** Alles unter `deploy/pi/` wurde ohne Gerät
> gebaut. Der erste echte Aufbau ist zugleich die Abnahme — siehe [backlog.md](backlog.md).
> Die **Container** sind seit dem 14. August 2026 geprüft, wenn auch auf einem Mac: Was dort nicht
> zu prüfen war, sind der USB-Weg der Sicherung und das Verhalten nach einem Stromausfall.

## Ausserhalb von `docs/`

| Datei | Inhalt |
|---|---|
| [../README.md](../README.md) | Der Einstieg: was das Ganze ist, wie man es startet |
| [../CHANGELOG.md](../CHANGELOG.md) | Was das Programm kann, nach Keep a Changelog sortiert |
| [../CLAUDE.md](../CLAUDE.md) | Die Regeln dieses Repos, für Coding-Agents |
| [../seed/README.md](../seed/README.md) | Der Beispielbestand: was `make seed` herstellt und warum seine Lücken Absicht sind |

`CHANGELOG.md` und `history.md` beschreiben beide Gebautes und sind trotzdem beide da: Der eine
listet **was**, die andere erzählt **wie und warum**. Wer sucht, ob eine Funktion existiert, nimmt
den CHANGELOG; wer wissen will, warum sie so aussieht, die Historie.
