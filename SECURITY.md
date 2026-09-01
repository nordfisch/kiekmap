# Security

## What this device is

A kiosk standing **offline** in a museum room. It offers no service on a network: the Pi hangs on
no internet connection, the map lies on the device as a file, and there is no sign-in except a PIN
in front of the admin area. That shapes what counts as a vulnerability here and what does not.

## What is deliberate

This is the design, not a finding:

- **The visitor view has no sign-in.** Whoever stands in front of the device may look at photos
  and add what is missing. That is exactly what it is set up for.
- **Contributions are taken without review**, but only into empty fields; curated statements are
  untouchable, and every change is in the change log and can be taken back.
- **There is no rate limit on the contribution path.** In a supervised room that has no
  consequence. For operation on a network it does — which is why that case lies as
  [issue #22](https://github.com/nordfisch/kiekmap/issues/22), with a sign-in in front of the whole
  application as its way.
- **The photo collection is not encrypted.** It lies as files on the device and on the backup
  stick. A museum that needs otherwise encrypts the medium.

## What is worth reporting

Anything somebody can reach **standing at the device** or **with a USB stick** that is not listed
above: a way past the PIN, an import that breaks out of its directory, a restore that touches files
outside the collection, a contribution that overwrites curated statements. Likewise anything that
comes along inside one of the dependencies.

Whoever puts the device on a network does so outside its intended operation — the open points above
then apply, and they are known.

## Reporting

**Not as a public issue.** Through GitHub's private report — in the repository's "Security" tab,
"Report a vulnerability". It goes only to the maintainer and becomes visible only once the matter
is fixed.

There is one maintainer, on the side. No response time is promised; a report will be read. What
gets fixed appears afterwards in the [CHANGELOG](CHANGELOG.md) and, with the reasoning, in
[history.de.md](docs/archive/history.de.md).

## Which version is maintained

Only the most recent one. There are no branches for older states.
