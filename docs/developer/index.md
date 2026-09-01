# Documentation for whoever works on the project

The documentation is split by audience, and only one half is published. **This half is read in the
repository**, beside the code it describes. The other half —
[`docs/museum/`](../museum/index.md) — is what a museum needs in order to use, run, adapt and pass
on the device, and it is delivered as a website at
[nordfisch.github.io/kiekmap](https://nordfisch.github.io/kiekmap/).

**The repository speaks English.** German is kept as a translation and carries the suffix to say
so: `operations.de.md` is the German half of `operations.md`, and
[`tools/check_translations.py`](../../tools/check_translations.py) reports when one of the two has
drifted. This half has no translations: it is English throughout, and `history.de.md` is the one
German original, closed and not continued.

## In this folder

| File | Question | For whom |
|---|---|---|
| [architecture.md](architecture.md) | *What* is there, and how does it fit together? | whoever is starting out |
| [development.md](development.md) | *How* is it worked on? — setup, the language rule, tests, pitfalls | developers |
| [decisions.md](decisions.md) | *Why* is it this way and not another? — every decision with its reason | whoever wants to change something |
| [archive/history.de.md](archive/history.de.md) | *How* did it come about? — and the number register | whoever wants to know whether an idea has been here before |

`decisions.md` is read **before** a change, the history when something looks inexplicable. The
history is German, ends with v0.8.0 and is not continued: what the work teaches becomes a
decision, and how it went is in the commits and the closed issues. Its **number register**
resolves the citations of the form "Punkt N". It sits under `archive/` because it is closed, not
because it is old.

## The museum half

| File | Question |
|---|---|
| [museum/usermanual.md](../museum/usermanual.md) | How do I add photos and back the collection up? |
| [museum/operations.md](../museum/operations.md) | How do I set the Pi up, and what do I do when it does not start? |
| [museum/adaption.md](../museum/adaption.md) | How do I set this up for another place? |
| [museum/licensing.md](../museum/licensing.md) | What may be passed on, and under which conditions? |

Each of them has a `.de.md` beside it, and `docs/museum/` is the whole of what the site publishes.
Changing anything there changes the site with the next tag.

## Outside `docs/`

| File | Content |
|---|---|
| [../../README.md](../../README.md) · [de](../../README.de.md) | The way in: what the whole thing is, how to start it |
| [../../CHANGELOG.md](../../CHANGELOG.md) · [de](../../CHANGELOG.de.md) | What the program can do, sorted by Keep a Changelog |
| [../../CLAUDE.md](../../CLAUDE.md) | The rules of this repository, for coding agents |
| [../../CONTRIBUTING.md](../../CONTRIBUTING.md) | How to take part — and what to expect, and what not |
| [../../SECURITY.md](../../SECURITY.md) | What counts as a vulnerability here, what is by design, and where to send it |
| [../../CODE_OF_CONDUCT.md](../../CODE_OF_CONDUCT.md) | How people deal with one another, kept short |
| [../../AUTHORS](../../AUTHORS) | Who built it |
| [../../seed/README.md](../../seed/README.md) | The sample collection: what `make seed` produces and why its gaps are deliberate |
| [../../LICENSE](../../LICENSE), [../../NOTICE](../../NOTICE) | Apache-2.0 in full, and the attribution that travels with it |

What is open is in the [issues](https://github.com/nordfisch/kiekmap/issues) and in no file. For
coding agents [../../CLAUDE.md](../../CLAUDE.md) comes on top — the same rules, cut to what is
needed, with the three things you can get wrong here at the front.

`CHANGELOG.md` and the history both describe what was built. One lists **what**, the other tells
**how and why**: whoever is looking for whether a feature exists takes the changelog; whoever
wants to know why it looks the way it does takes the history.
