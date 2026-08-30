# Lessons

What the plan did not know. One entry per surprise that would otherwise happen a second time.

This file continues [history.md](history.md), which ends with version 0.8.0 on 25 August 2026, and
it is deliberately not the same kind of file. The history was a work diary and recorded every step.
This one records less: an entry exists only if, without it, the same mistake would happen again.
Everything else lives in the commits, the pull requests and the closed issues, where it is written
down anyway.

Newest last. Every entry names its date and the commit or issue it came out of.

---

## 30 August 2026 · Two numbering sequences share one word

[decisions.md](decisions.md) and [backlog.md](backlog.md) both number their points, both are cited
as "Punkt N", and the two sequences are independent of each other. The backlog stood at 66, so the
plan called the next decision 67. That number had belonged to a decision since 25 August.

`tools/check_numbers.py` caught it, which is why it cost a minute instead of a day. The trap comes
back in stage 6 of the documentation cleanup, where the backlog turns into a number register while
the decisions keep counting. **Read the last heading of the file a point goes into, before writing
the point.**

Commit `6c485ef`.

## 30 August 2026 · A count written in prose goes stale in silence

Four files said this repository has "five checks" and then listed six of them. `set_version.py
--check` became the sixth on 25 August; nothing counts the checks, so nothing complained. One of
the four files already said "six" in a second place, three sections further down -- the drift was
visible inside a single file and still nobody saw it.

Numbers in prose age like documentation, not like code. The register in `history.md` and the
package list in `NOTICE` are generated for exactly this reason. A count of six is too small to
generate, so the cheaper rule applies: **do not write a number that something else already
states.** The lists were there all along; the count in front of them said nothing the reader could
not see.

Surfaced in commit `6c485ef`, where the number was first corrected and then dropped.
