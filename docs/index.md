# Documentation

Each file in this folder answers a different question. Which question that is stands in the first
column of the tables below; beside it, who the file is written for.

**The repository speaks English.** German is kept as a translation and carries the suffix to say
so: `operations.de.md` is the German half of `operations.md`, and
[`tools/check_translations.py`](../tools/check_translations.py) reports when one of the two halves
has drifted. One file has no English version and needs none: `history.de.md` is closed.

## Setting Kiekmap up and running it

| File | Question | For whom |
|---|---|---|
| [usermanual.md](usermanual.md) · [de](usermanual.de.md) | How do I add photos and back the collection up? | the museum team, to print out |
| [operations.md](operations.md) · [de](operations.de.md) | How do I set the Pi up, and what do I do when it does not start? | whoever keeps the device running |
| [adaption.md](adaption.md) · [de](adaption.de.md) | How do I set this up for **another place**? | a second museum |
| [licensing.md](licensing.md) · [de](licensing.de.md) | What may be passed on, and under which conditions? | whoever publishes or takes it over |

`usermanual` is the operation, `operations` the technology behind it — they part along
responsibility, not along difficulty. `adaption` and `licensing` address a second museum setting up
a device of its **own**; that is what the project is built for.

> **None of it has been tried on a Pi.** Everything under `deploy/pi/` was built without a device.
> The first real setup is also the acceptance test — see
> [#18](https://github.com/nordfisch/kiekmap/issues/18). The **containers** are verified, if only
> on a Mac: what could not be checked there is the USB path of the backup and the behaviour after
> a power cut.

## Understanding the system and changing it

| File | Question | For whom |
|---|---|---|
| [architecture.md](architecture.md) | *What* is there, and how does it fit together? | whoever is starting out |
| [development.md](development.md) | *How* is it worked on? — setup, the language rule, tests, pitfalls | developers |
| [decisions.md](decisions.md) | *Why* is it this way and not another? — every decision with its reason | whoever wants to change something |
| [archive/history.de.md](archive/history.de.md) | *How* did it come about? — and the number register | whoever wants to know whether an idea has been here before |

`decisions.md` is read **before** a change, `history.de.md` when something looks inexplicable. The
history is German, ends with v0.8.0 and is not continued: what the work teaches becomes a decision,
and how it went is in the commits and the closed issues. Its **number register** resolves the
citations of the form "Punkt N".

What is open is in the [issues](https://github.com/nordfisch/kiekmap/issues) and in no file. For
coding agents [../CLAUDE.md](../CLAUDE.md) comes on top — the same rules, cut to what is needed,
with the three things you can get wrong here at the front.

## Outside `docs/`

| File | Content |
|---|---|
| [../README.md](../README.md) · [de](../README.de.md) | The way in: what the whole thing is, how to start it |
| [../CHANGELOG.md](../CHANGELOG.md) · [de](../CHANGELOG.de.md) | What the program can do, sorted by Keep a Changelog |
| [../CLAUDE.md](../CLAUDE.md) | The rules of this repository, for coding agents |
| [../CONTRIBUTING.md](../CONTRIBUTING.md) | How to take part — and what to expect, and what not |
| [../SECURITY.md](../SECURITY.md) | What counts as a vulnerability here, what is by design, and where to send it |
| [../CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md) | How people deal with one another, kept short |
| [../AUTHORS](../AUTHORS) | Who built it |
| [../seed/README.md](../seed/README.md) | The sample collection: what `make seed` produces and why its gaps are deliberate |
| [../LICENSE](../LICENSE), [../NOTICE](../NOTICE) | Apache-2.0 in full, and the attribution that travels with it |

`CHANGELOG.md` and `history.de.md` both describe what was built. One lists **what**, the other
tells **how and why**: whoever is looking for whether a feature exists takes the changelog;
whoever wants to know why it looks the way it does takes the history.
