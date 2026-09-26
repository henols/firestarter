# Firmware prerelease — 28C write-path policy, standalone erase, page-size seam, protection read

**Version:** `3.0.0b20` — read via `gh release list --repo henols/firestarter --limit 8` at
2026-08-21T17:15:00Z, the newest pre-release cut this run. Cut by `beta-build.yml` (a different
workflow file from the host app's `beta-release.yml`) from merge commit
`a1f474b5b3acd2f6fb246ec14ad6774dc52ced3f` (PR #53), which landed this milestone's work on `beta`;
the release's own target commit is `88d204a5a023bcad6f708b33150502ba90fdec2b`, the SHA that same
workflow's version-bump auto-commit produced immediately after the merge. The matching host release is
`3.0.0b23`, read the same way from `henols/firestarter_app` (PR #53, merge commit
`8f2e8d7de709bf58c5e20daea34b17c073ee59b9`), and confirmed present on PyPI (`info.version` for the
*stable* channel there is still `2.0.7`, unrelated to this pre-release) — the two repositories version
independently, so the two numbers will not agree and are not expected to.

Four images are published, one per board target:

- `firestarter_leonardo.hex` (75961 B) — targets Leonardo-class controllers.
- `firestarter_uno.hex` (70120 B) — targets the Uno.
- `firestarter_uno328pb.hex` (70246 B) — targets the 328PB-class Uno.
- `firestarter_py32f071.hex` (79047 B) — targets the PY32F071 ARM port. Standing non-claim: no
  PY32F071 circuit board exists anywhere in this project, and nothing in that port has run on any
  silicon.

`firestarter fw --install` flashes **the board it finds attached**; it does not read a `--board`
choice and cannot be pointed at a different target than the one plugged in.

## Before you plug anything in

The write-path change described below lives entirely in this firmware image. Installing the matching
host release on its own does not deliver it — both halves need to be in place, in either order, before
either shows the new behaviour.

The standalone erase step added on the 28C protocol uses the manufacturer's **software** six-byte
chip-erase sequence, never the datasheet's alternative hardware path. That alternative path drives a
programming voltage onto a pin of this part family's pinout, and this project does not put a
programming voltage on a pin of a 5 V part. The control that actually guards this hazard on the tree is
`firestarter/scripts/check_erase_no_vpp.py`, a source scan of the handler body itself: it fails on a
planted violation and leaves a legitimate same-pin low-voltage write alone.

## What's new

- **The pre-write blank check is gone** on the two protocols that already auto-erase per page during
  the write itself — `0x0D` (the 28C/EEPROM-parallel family) and `0x05`. On this silicon a page write
  auto-erases internally and every page is read back and verified anyway, so the check was never
  actually a safety net: it was a precondition that made a non-blank part unwritable at all unless an
  override flag was passed. The override flag is consequently unread on these two protocols now, and
  must not be restored on the grounds that it looks orphaned — the comment left in the handler says so
  directly. The standalone blank-check step itself is unaffected and still exists on its own.
- **A standalone erase command arm now exists on the 28C protocol.** It dispatches the manufacturer's
  own software six-byte chip-erase sequence, cited in the tree as Atmel Application Note "Software Chip
  Erase," Rev. 0544B-10/98, and it waits out that application note's erase-cycle timing constant before
  reporting completion.
- **The page value delivered over the wire now comes from the chip database, not a compiled-in
  constant** — a seam, not a behaviour change. The load-bearing non-claim travels with it: for the part
  central to this family's community reports, the value the wire now delivers is identical to the old
  constant, so nothing about that part's behaviour changes and this seam explains nothing about those
  reports.
- **A protection-read command (`CMD_LOCK_STATUS`) now exists on the wire**, which the host's
  `lock-status` command uses. It is **beta-channel only** in this release and needs matched firmware in
  both directions: a beta-channel host talking to firmware without it gets an "outdated firmware"
  answer rather than a recognized command, and firmware carrying it talking to an older host is simply
  never asked for it.

## The size picture

Two numbers matter here, and they are not the same number.

The `leonardo` image measures **27630 B** of its device's 32768 B flash. The Caterina USB-bootloader
boundary sits at **28672 B**, leaving **1042 B** (28672 − 27630 = 1042) before a future build would be
linked over the bootloader itself — and that boundary is **UNGUARDED**: `board_upload.maximum_size` in
`platformio.ini` is set to 32768, the device's real flash size, not a bootloader-protecting figure, so
the linker no longer refuses a build that would overwrite Caterina. A future firmware build that grows
past this boundary would brick the USB bootloader on every already-flashed Leonardo-class board that
tries to receive it.

Separately — and this is a *different* number — the recorded size-band headroom against this
project's baseline is **0 B**: the measured delta on `leonardo` against the recorded baseline is
**+724 B**, exactly equal to the summed allowance of four named exemptions (96 + 210 + 288 + 130 = 724).
The band held only because every byte of growth this milestone was individually funded and admitted; it
did not hold with room to spare.

Relieving the Caterina boundary — a split or trimmed firmware build — is not planned, queued, or on any
roadmap. It stands as an unaddressed constraint on the record.

## The withdrawal

`write --sdp-relock` is withdrawn — tracked as Backlog **999.28**. The command exists in this firmware
image, but no host surface reaches it in this release, so there is currently no supported way to
deliberately protect a part on this chip family. On this same family the protection bit cannot be read
back afterward either, so even a host surface that reached the command today would have no way to
confirm the result.

## What is established

- The pre-write blank check's removal on protocols `0x0D` and `0x05`, and the standalone erase arm on
  `0x0D`, both match the shipped firmware's behaviour and are exercised in this project's own test
  environment.
- The page-size wire seam is in place and matches the shipped firmware's behaviour.
- `CMD_LOCK_STATUS` ships on the beta channel and is exercised end to end in this project's own test
  environment.
- The deferred protection command named above (Backlog 999.28) has no host-reachable surface in this
  release; the retired `dev sdp enable`/`disable` command pair remains gone.

## What this release does not establish

- **This ships software-proven and unvalidated on silicon.**
  No AT28C part was tested at any point in v1.32 — not in writing the erase sequence, not in choosing
  the SDP-disable prefix, not in any test.
- **Protocol `0x0D` stays UNVERIFIED in PROTOCOL-LEDGER.** Nothing in this release moves it out of that
  status, and no chip's support classification changed.
- **The erase-cycle timing constant this release waits out is an Atmel-family maximum**, applied to an
  84-row algorithm bucket that spans other vendors. A part with a longer actual erase-cycle time than
  that maximum could read non-blank right after an erase that looked like it had succeeded, and nothing
  in this project's test suite would catch that.
- **No test in this project can prove the erase wait is actually honoured on real hardware.** The
  native test stubs this project runs do not stub the delay call and record no elapsed time at all, so
  that assertion is structural, not temporal — a test can prove the wait was requested, never that it
  was observed.
- **The database's advisory field describing post-write protection has no runtime consumer in this
  release**, because `write --sdp-relock` is withdrawn. Its presence on a row should not be read as
  meaning deliberate protection is honoured by anything that runs today.

## The capability boundary, and what would help

Today's position is: the write path no longer refuses a non-blank part on this family before writing
it, a standalone erase exists using the hazard-free path, and a protection-read command exists on the
wire and reaches the beta-channel host. It is not: a claim that any of this has been checked against a
real part of the family this thread is about, or a claim that the erase-cycle wait has been observed to
matter on real hardware rather than only requested.

If you have a part from the family this milestone's write-path work concerns, both halves of the
install need to be in place before either shows anything new: the matching host release, and
`firestarter fw --install` against this firmware. Either outcome from a run is useful — a clean result
would mean this write path has held up against real silicon for the first time, and a failure comes
with a firmware identity attached, so it is something that can actually be root-caused instead of
guessed at.
