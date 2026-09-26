# Host app prerelease — AT28C write-path fix, `lock-status`, and report provenance

**Version:** `3.0.0b23` — read via `gh release list --repo henols/firestarter_app --limit 8` at 2026-08-21T17:15:00Z.
Cut by `beta-release.yml` from merge commit `8f2e8d7de709bf58c5e20daea34b17c073ee59b9` (PR #53), target commit
`86f85d77d8102b633da82aef4b5601947f6cc80b`. PyPI upload verified **independently of GitHub**, via a direct read of
`https://pypi.org/pypi/firestarter/json`, because this project has had GitHub carrying betas past PyPI before, and
that pattern is live again on the *stable* channel right now: GitHub carries a stable release, `2.0.8`, that PyPI's
own `info.version` does not yet report (still `2.0.7`, re-measured 2026-08-21T17:15:10Z) — so
`firestarter-3.0.0b23-py3-none-any.whl` and the matching `.tar.gz` being present on PyPI is checked directly against
the registry, which shows both uploaded at 2026-08-21T17:07:09Z, 26 s after this release published. Nothing in this
document should be read as claiming `2.0.8`, or any other GitHub-only release, is installable via `pip` — only what
PyPI's own `info.version` reports is actually pip-installable. The matching firmware release is `3.0.0b20`, read the
same way from `henols/firestarter`, cut by `beta-build.yml` (a different workflow file from the app's
`beta-release.yml`, merge commit `a1f474b5b3acd2f6fb246ec14ad6774dc52ced3f`, PR #53) — the two repositories version
independently, so the two numbers will not agree and are not expected to.

`pip install --pre --upgrade firestarter`

This GitHub release page carries no attached files — it is a tag-and-marker page only. PyPI is the
distribution channel for the host app; the command above pulls it. The matching firmware for this
release is published separately, and its `.hex` files are what `firestarter fw --install` pulls
when you update your board — a reader upgrading one half without the other should know which half
does what before doing so. That matters more than usual this time: the write-path fix described
below lives in the firmware, not the host, so installing this app update on its own does not pick
it up.

## What's new

### `lock-status` — the refusal is the feature

`firestarter dev lock-status <chip>` either reports a real protection state read back from the
chip, or refuses and names an actionable, specific reason — never a guess. On this chip family the
honest answer is usually the refusal, and that is the feature working as designed, not a
limitation of it: measured through the live classifier, 665 of the chip database's 746 rows
resolve to a refusal class, and only 81 are read-permitted. A feature description that led with
"reports your chip's protection state" would be wrong for most chips a reader actually tries it
against.

`lock-status` is **beta-channel only right now**, and it needs **matched firmware**: install the
pre-release (`pip install --pre --upgrade firestarter`) and run `firestarter fw --install` against
a board running `3.0.0b20` or later. Against older firmware the host reports the firmware as
out of date rather than recognizing the command at all — it is a new command entirely, not an
existing one that changed shape. The one exploratory run this milestone made, against a W29C020 on
the bench, was a **probe**, never a validation — it exercised the command's mechanics on one part
that is not from the family this thread is about, and it should not be read as evidence about any
other chip.

*Corrected 2026-08-21, after this body was first published: this paragraph originally named that part a
`W29C040`. No `W29C040` was available on the bench and none was ever seated — the part actually run was a
`W29C020`. The misattribution came from this milestone's own planning record, not from the bench log, which
had it right. Nothing else in these notes depended on it, and neither part belongs to the AT28C family this
release is about.*

### The write path no longer blank-checks before writing

On the two protocols that auto-erase per page during the write — `0x0D` (the 28C/EEPROM-parallel
family this thread is about) and `0x05` — `write` no longer performs a pre-write blank check. On
this silicon a page write already erases internally as part of the write itself, so the check was
never actually protecting anything; it was a precondition that made a non-blank part unwritable at
all unless an override flag was passed. The standalone blank-check step is unaffected and still
exists on its own, exactly as before.

### Standalone erase, on the 28C protocol

A standalone `erase` step now exists on protocol `0x0D`, implemented with the manufacturer's own
software six-byte chip-erase sequence rather than the hardware chip-erase path some datasheets in
this family also document. The software path was the deliberate choice: the hardware path drives a
programming voltage onto a pin of this pinout, and this project does not put a programming voltage
on a pin of a 5 V part.

### Report provenance, and numeric database values

`firestarter dev test <chip>` reports now name the firmware they ran on. A report that cannot say
which firmware produced it cannot be root-caused — there is no way to tell a host-side failure from
a board-side one without it. Separately, voltage and timing fields in the chip database are now
integers, in millivolts and microseconds, rather than the mixed representations used before.

## Removed

`firestarter dev sdp <chip> enable|disable` is gone.

- **`disable` is gone because it is genuinely redundant.** `write` already auto-unlocks on every
  protocol-`0x0D` write by default (declinable via `--skip-sdp-unlock`), so `dev sdp disable` was
  sending a command sequence `write` already sends on its own.
- **`enable` is withdrawn, with no replacement in this release — for a second release now.** There
  is currently no supported way to deliberately protect an SDP part. On this chip family the
  protection bit cannot be read back afterward either, so even if a replacement existed today there
  would be no way to confirm the result. `write --sdp-relock` is withdrawn — tracked as Backlog
  999.28 — and no version is promised for it here.

The previous app pre-release, `3.0.0b14` (2026-07-30), announced: *"An opt-in re-lock after a write
is deliberately not part of this release."* Read plainly today, that sentence promises less than
what actually happened: it reads as a small, near-term, opt-in omission from one release, not what
this has actually become — a gap that has now spanned a second release, with no committed version
and no code written toward closing it, tracked only as Backlog 999.28. The `b14` body is not
edited — it is historical and stays published exactly as written — so this paragraph, in the new
notes, is where the correction lives instead.

## What is established, and what is not

**Established:**

- The retired `dev sdp <chip> enable|disable` command surface is gone, `write`'s automatic unlock
  behaviour (and its `--skip-sdp-unlock` opt-out) is unchanged, and the corrected mapping above
  matches the shipped CLI's `--help` text.
- `lock-status` ships on the beta channel, against matched firmware, and its eight-class refusal
  logic is exercised end to end in this project's own test environment.
- The write-path policy change (no pre-write blank check on protocols `0x0D` and `0x05`) and the
  new standalone `erase` step on `0x0D` both match the shipped CLI's behaviour and are exercised in
  this project's own test environment.
- Report provenance (naming the firmware a `dev test` run used) and the integer millivolt/
  microsecond database fields are both in place and match the shipped CLI output.

**Not established:**

- **This ships software-proven and unvalidated on silicon.** No AT28C part was tested at any point in v1.32 — not in writing the erase sequence, not in choosing the SDP-disable prefix, not in any test.
- **Protocol `0x0D` stays UNVERIFIED in PROTOCOL-LEDGER.** Nothing in this release moves it out of
  that status, and no chip's support classification changed — the chip database is otherwise
  byte-unchanged by this milestone's firmware and host work.
- **The three open community threads about this chip family stay open.** A code fix is not a
  validation.
- **The erase-cycle timing constant is an Atmel-family maximum**, applied to an 84-row algorithm
  bucket that spans other vendors. A part with a longer actual erase-cycle time than that maximum
  could read non-blank right after an erase that looked like it had succeeded, and nothing in the
  test suite would catch that.
- **No test in this project can prove the erase wait is actually honoured on real hardware.** The
  native test stubs this project runs record no elapsed time at all, so that particular assertion
  is structural, not temporal.
- **The database's advisory `protect_on_after` field has no runtime consumer in this release**,
  because `write --sdp-relock` is withdrawn. Its presence on a row should not be read as meaning
  deliberate protection is honoured by anything that runs today.

## The ask

If you have an AT28C part, or a part from any of the other chip families `lock-status` covers, both
halves need to be in place before either shows anything new: `pip install --pre --upgrade
firestarter` for the host, and `firestarter fw --install` for the matching firmware. Either outcome
from a report is useful — a `lock-status` refusal named correctly and specifically is a working
command doing exactly what it is designed to do, not a failed one, and a `write`/`erase`/`verify`
run against a real part is the only way any of this milestone's AT28C work becomes more than
software-proven and unvalidated on silicon.
