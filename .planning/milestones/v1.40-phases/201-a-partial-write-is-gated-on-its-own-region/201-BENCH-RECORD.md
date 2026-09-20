# Phase 201 Plan 06: Bench Record — Non-Erasable Silicon Proof of Criterion 1

**Measured:** 2026-09-20, meta-repo sha `accbe825930a1a862314b94af28bcb1d72ae0965`

**Status: EVIDENCE — not a test, not a CI leg, cannot re-run automatically.**

This record captures a bench session on real Arduino/RURP hardware and real EPROM parts. It
proves that criterion 1 of Phase 201 (a write into a blank region of a non-blank, non-erasable
part succeeds) holds on silicon. It is not a software test, it does not gate any CI leg, and it
cannot be re-run without a human physically seating and removing chips at a bench.

## Session setup

**Serial port, probed fresh this session (never inherited from a prior session — port numbering
shuffles across replug):**

- Device path: `/dev/ttyACM0`
- Enumerated candidates: `/dev/ttyACM0` only (`/dev/ttyUSB*` absent). `pyserial`'s
  `list_ports.comports()` reported it as `Arduino Leonardo`, `VID:PID=2341:8036`.
- Identity confirmed by driving the firestarter CLI against the port:
  - `firestarter -p /dev/ttyACM0 fw` → `Current firmware version: 3.0.0b33, for controller:
    leonardo on port /dev/ttyACM0`. The command's own up-to-date check reported "Firmware is
    already up to date (version 3.0.0b33 for leonardo)" and performed no install.
  - `firestarter -p /dev/ttyACM0 hw` → `Hardware revision: Rev 2.0-class, Override HW: Rev
    2.0-class`. This is the firmware-reported `hw_revision` field. It is recorded here as what
    the board reports, and it is explicitly NOT a substitute for the operator's silkscreen
    reading below — the firmware-reported field cannot distinguish Rev 2.2 from Rev 2.0 from a
    modified Rev 0.
- Board type: Arduino Leonardo (ATmega32U4).
- Firmware currently on the board at session start: `3.0.0b33`.

**Images built locally, not committed, not yet flashed:**

| Role | Commit (firestarter_fw) | File | sha256 (hex) | Leonardo flash size |
|------|--------------------------|------|---------------|----------------------|
| Pre-fix (RED) | `af47bf464a24c005e556cf3d7308679064feca5e` (plan 201-02 tip, parent of plan 201-03's firmware commit `76fd3c7`) | `/workspaces/tmp/201-06-bench-images/prefix-af47bf4-leonardo.hex` | `1538be87486133717e861d40261ddc857e7832ce22689448c4fe3c6f146e5586` | 23850/32768 B |
| Post-fix (GREEN) | `e5842d8ceacac45e8640cd274947e7ee6c88fb58` (phase 201's HEAD at bench-session time, includes plans 201-02 through 201-05) | `/workspaces/tmp/201-06-bench-images/postfix-e5842d8-leonardo.hex` | `36970caac008582ac766485d44d86a37054fb2de6d4a4d6908df08af590a4c3f` | 24134/32768 B |

Both images were built with a plain `pio run -e leonardo` in `/workspaces/firestarter_fw`. No
`DEV_TOOLS` build flag was set (matching a stable-channel image, not the beta/dev-tools image).
The working tree was returned to `v1.40-program-parameter-fidelity` after the pre-fix build and
verified clean; all three repositories (`/workspaces`, `firestarter_fw`, `firestarter_app`)
confirmed on `v1.40-program-parameter-fidelity` before proceeding.

Nothing has been flashed yet. Nothing has been written to any part.

## Operator statements (Task 1 checkpoint)

**1. Shield revision, read from the silkscreen (operator statement, not a firmware field):**

Rev 2.0. Stated by the operator from the silkscreen. This is the source of record for the shield
revision in this session; the firmware-reported `Hardware revision: Rev 2.0-class` field recorded
above under Session setup is NOT a substitute for it — that field cannot distinguish Rev 2.2 from
Rev 2.0 from a modified Rev 0, and in this instance it happens to agree with the silkscreen, which
is a coincidence of this particular board, not something the field can be relied on to do in
general.

**2. W27C512 seating confirmation (orientation, and any silkscreen-called jumper for this pin
count set as printed):**

The operator seated a W27C512 in the socket. The first chip-ID attempt against it failed (see the
chip-ID history below), and the operator then re-seated the part. The operator states it is now
seated, in the correct orientation, with the jumper this pin count calls for on the board's
silkscreen set as printed.

**3. Chip-ID reading and history for the seated part:**

Three chip-ID events occurred this session, over the serial link, measured by the coordinator.
Recorded in full because the excursion is part of the evidence, not just its outcome:

- **First attempt, before the VPP adjustment below:** refused at init by the firmware's VPP guard —
  `ERROR: VPP is high: 18.8V > 12.0V`. Nothing was written or read from the part at this point; the
  guard fired before any chip-ID read was attempted.
- **After the operator set VPP to 12.1 V (see below):** `Programmer reported chip ID: 0x9201`,
  stable across three consecutive reads, and not present anywhere in the chip database — no row
  has an ID starting `0x92`. Treated as a stop; nothing further was attempted against the part in
  this state.
- **After the operator re-seated the part:** `Chip ID check passed for W27C512`, confirmed twice.
  The firmware prints a raw ID value only on mismatch, so on a pass the check is against the
  database's expected `0xDA08` — the pass itself is the transcription. No raw hex value was
  printed on this attempt, and none is invented here to stand in for one.
- **Conclusion:** the stable `0x9201` reading was a seating fault, not a wrong part. The chip is
  confirmed as a W27C512 by chip-ID (`0xDA08`, matched by pass), not by the marking on its package.

**VPP:** the operator found VPP at 18.8 V on the first attempt (the reading that tripped the
firmware guard above), then adjusted the pot themselves and set it to 12.1 V — inside the
11.4–12.5 V accepted window for a 12 V target. Claude did not run a live monitor loop for this;
the 18.8 V and 12.1 V values are the operator's own bounded readings, reported here as stated.

## W27C512 rehearsal

**Status: EVIDENCE — not a test, not a CI leg, cannot re-run automatically.**

Chip-ID confirmed `0xDA08` (W27C512) for the whole of this section, per the Task 1 checkpoint
above. Driven with `firestarter ... --skip-erase` throughout, so `FLAG_CAN_ERASE` is set but the
erase that would otherwise run above the blank check is suppressed — the identical code path a
UV part takes (D-11), which is what makes this rehearsal a faithful proxy rather than an analogy.

Host: `firestarter`, version `3.0.0b48` (editable install at `/workspaces/firestarter_app`, branch
`v1.40-program-parameter-fidelity`). Chip: `w27c512` as resolved by the host database
(`W27C512,W27E512`, memory size `0x10000`, protocol `0x07`).

**Device geometry used for both runs:** low address `0x000000`, 64 bytes, pattern
`a55a3cc3` repeated 16 times (non-`0xFF`). Target address `0x00FF00`, 64 bytes, pattern
`11223344` repeated 16 times when written; the target region is required blank (`0xFF`) before
each write attempt. `0x00FF00` sits `0xFF00` (65,280) bytes away from the low address on a
64 KiB part — the same shape as the originating `AM27C020` transcript's low address versus its
`0x03ff00` target, scaled to this part's smaller geometry.

**A rig characteristic measured during this session, recorded here because it changed the
procedure:** device contents were not found to survive every AVR firmware reflash reliably. In
the first RED-to-GREEN transition (Run 1 below) the low-address pattern written before flashing
the pre-fix image was still present, unchanged, after flashing the post-fix image over it — the
GREEN half's `write` succeeded against a device state carried across the flash. In an initial
attempt at a second run, the identical procedure — write the low-address pattern, confirm it by
read-back, then reflash — was followed by a read-back showing the low address blank (`0xFF`)
after the reflash, with no read-back taken in between the confirm and the reflash to say when it
changed. Rather than treat one instance of survival as a rule, the procedure was tightened for
every half recorded below: after every firmware flash, the device state (erase, write the
low-address pattern, read back and confirm both the low address and the target region) was
re-established and read-back-confirmed immediately before that half's three-step transcript,
never carried across a flash on the strength of an earlier confirmation. This is a stricter
version of the GREEN-half re-establishment the plan itself specifies, applied uniformly to every
half of every run below. No transcript below rests on state that was not read back and confirmed
on the firmware it was measured under.

**A finding on the firmware version string, recorded because the plan expected it to differ and
it does not:** `firestarter -p /dev/ttyACM0 fw` reports `Current firmware version: 3.0.0b33, for
controller: leonardo` identically under the pre-fix and the post-fix image. `VERSION` is a
hand-set string literal in `firestarter_fw/include/version.h`; it is bumped at a release cut, not
per commit, and no plan in this phase bumps it. The two images are therefore distinguished in
this record by their commit SHA and image SHA-256 (recorded in Session setup above), not by the
version string — recording that plainly rather than reporting two version-string readings that
are, in fact, the same string.

### Run 1

**Setup (on the pre-fix image, flashed first):**

```
$ firestarter -p /dev/ttyACM0 erase w27c512
Erase for W27C512 successful (0.58s). (main done)

$ firestarter -p /dev/ttyACM0 blank w27c512
Blank check for W27C512 successful (4.94s). (main done)

$ firestarter -p /dev/ttyACM0 write w27c512 low.bin -a 0x000000 --skip-erase
Write to W27C512 successful (5.37s).
```
Read-back confirmed: bytes `0x000000`-`0x00003F` = `a55a3cc3` x16 (non-`0xFF`); bytes
`0x00FF00`-`0x00FF3F` = `0xFF` x64 (blank).

**RED half — pre-fix image `af47bf4`, firmware reports `3.0.0b33`:**

```
$ firestarter -p /dev/ttyACM0 blank w27c512
Blank checking EPROM W27C512
ERROR: Not blank, at 0x000000, v: 0xa5
Programmer error during BLANK_CHECK: Not blank, at 0x000000, v: 0xa5

$ firestarter -p /dev/ttyACM0 write w27c512 target.bin -a 0x00FF00 --skip-erase
Writing target.bin to W27C512
ERROR: Not blank, at 0x000000, v: 0xa5
Programmer error during WRITE: Programmer error during init: Not blank, at 0x000000, v: 0xa5
Write to W27C512 failed.
(exit code 1)

$ firestarter -p /dev/ttyACM0 verify w27c512 target.bin -a 0x00FF00
Verifying target.bin against W27C512
ERROR: 0x11 != 0xff at 0x00ff00
Programmer error during VERIFY: 0x11 != 0xff at 0x00ff00
Verify for W27C512 failed.
(exit code 1)
```

Step 3 is the load-bearing line: `0x11` is `target.bin`'s first byte, `0xff` is what the device
actually held at `0x00ff00` — the target slot was blank while the write was refused on account of
the byte at `0x000000`, 65,280 bytes away.

**GREEN half — post-fix image `e5842d8`, firmware reports `3.0.0b33`, same device state, no
re-write (state carried across this particular reflash — see the rig-characteristic note above):**

```
$ firestarter -p /dev/ttyACM0 blank w27c512
Blank checking EPROM W27C512
ERROR: Not blank, at 0x000000, v: 0xa5
Programmer error during BLANK_CHECK: Not blank, at 0x000000, v: 0xa5

$ firestarter -p /dev/ttyACM0 write w27c512 target.bin -a 0x00FF00 --skip-erase
Writing target.bin to W27C512
  [progress denominator: 0x0000/0xff40 bytes -- region-bounded, not the whole-device 0x10000
  the pre-fix write showed above]
Write to W27C512 successful (0.84s).
(exit code 0)

$ firestarter -p /dev/ttyACM0 verify w27c512 target.bin -a 0x00FF00
Verifying target.bin against W27C512
Verify for W27C512 successful (0.31s).
(exit code 0)
```

Step 1 unchanged from the RED half, byte-for-byte — the standalone command is frozen (BLANK-02),
observed here on silicon. Step 2 now succeeds; its progress denominator moved from `0x10000`
(whole device, under the pre-fix image) to `0xff40` (`0x00FF00` + `0x40`, the region end) under
the post-fix image — D-06's write-loop progress denominator change, observed directly on this
board, not merely read from source. Step 3 verifies clean.

### Run 2

**Setup (on the pre-fix image, re-flashed for this run) — erase, then re-establish:**

```
$ firestarter -p /dev/ttyACM0 erase w27c512
Erase for W27C512 successful (0.58s). (main done)

$ firestarter -p /dev/ttyACM0 write w27c512 low.bin -a 0x000000 --skip-erase
Write to W27C512 successful (5.37s).
```
Read-back confirmed: bytes `0x000000`-`0x00003F` = `a55a3cc3` x16; bytes `0x00FF00`-`0x00FF3F` =
`0xFF` x64. Confirmed on the pre-fix image, immediately before the RED steps below, per the
tightened procedure above.

**RED half — pre-fix image `af47bf4`, firmware reports `3.0.0b33`:**

```
$ firestarter -p /dev/ttyACM0 blank w27c512
Blank checking EPROM W27C512
ERROR: Not blank, at 0x000000, v: 0xa5
Programmer error during BLANK_CHECK: Not blank, at 0x000000, v: 0xa5

$ firestarter -p /dev/ttyACM0 write w27c512 target.bin -a 0x00FF00 --skip-erase
Writing target.bin to W27C512
ERROR: Not blank, at 0x000000, v: 0xa5
Programmer error during WRITE: Programmer error during init: Not blank, at 0x000000, v: 0xa5
Write to W27C512 failed.
(exit code 1)

$ firestarter -p /dev/ttyACM0 verify w27c512 target.bin -a 0x00FF00
Verifying target.bin against W27C512
ERROR: 0x11 != 0xff at 0x00ff00
Programmer error during VERIFY: 0x11 != 0xff at 0x00ff00
Verify for W27C512 failed.
(exit code 1)
```

Identical shape to Run 1's RED half, on the same part, same rig, same pre-fix image.

**Re-establishment before the GREEN half — flash post-fix image, then erase and re-write (per the
plan's own instruction for this half, and the tightened procedure above):**

```
$ firestarter -p /dev/ttyACM0 erase w27c512
Erase for W27C512 successful (0.58s). (main done)

$ firestarter -p /dev/ttyACM0 write w27c512 low.bin -a 0x000000 --skip-erase
  [progress denominator: 0x0000/0x0040 bytes -- region-bounded under the post-fix image]
Write to W27C512 successful (0.84s).
```
Read-back confirmed: bytes `0x000000`-`0x00003F` = `a55a3cc3` x16; bytes `0x00FF00`-`0x00FF3F` =
`0xFF` x64. Confirmed on the post-fix image, immediately before the GREEN steps below.

**GREEN half — post-fix image `e5842d8`, firmware reports `3.0.0b33`:**

```
$ firestarter -p /dev/ttyACM0 blank w27c512
Blank checking EPROM W27C512
ERROR: Not blank, at 0x000000, v: 0xa5
Programmer error during BLANK_CHECK: Not blank, at 0x000000, v: 0xa5

$ firestarter -p /dev/ttyACM0 write w27c512 target.bin -a 0x00FF00 --skip-erase
Writing target.bin to W27C512
  [progress denominator: 0x0000/0xff40 bytes -- region-bounded]
Write to W27C512 successful (0.84s).
(exit code 0)

$ firestarter -p /dev/ttyACM0 verify w27c512 target.bin -a 0x00FF00
Verifying target.bin against W27C512
Verify for W27C512 successful (0.30s).
(exit code 0)
```

Step 1 unchanged from Run 2's RED half. Step 2 succeeds, region-bounded denominator as in Run 1.
Step 3 verifies clean.

### Summary of both runs

| Run | Half | blank-check | write --skip-erase | verify | Firmware reported |
|-----|------|--------------|---------------------|--------|--------------------|
| 1 | RED  | not blank at `0x000000`, `v: 0xa5` | refused at init, same reason | `0x11 != 0xff at 0x00ff00` | `3.0.0b33` (image `af47bf4`) |
| 1 | GREEN | not blank at `0x000000`, `v: 0xa5` (unchanged) | succeeded, denominator `0xff40` | clean | `3.0.0b33` (image `e5842d8`) |
| 2 | RED  | not blank at `0x000000`, `v: 0xa5` | refused at init, same reason | `0x11 != 0xff at 0x00ff00` | `3.0.0b33` (image `af47bf4`) |
| 2 | GREEN | not blank at `0x000000`, `v: 0xa5` (unchanged) | succeeded, denominator `0xff40` | clean | `3.0.0b33` (image `e5842d8`) |

Two complete RED-then-GREEN pairs, on the same part (chip-ID `0xDA08`, confirmed under Task 1) and
the same rig, each pair's device state independently established and read-back-confirmed rather
than assumed to carry over from the other pair. `git status --porcelain` for `firestarter_fw` is
clean throughout (no source edited during this session); `firestarter_app`'s only untracked entry
(`datasheets/LST62832I.pdf`) predates this session and is logged separately in
`deferred-items.md` — it is not a bench-session artifact. All three repositories remain on
`v1.40-program-parameter-fidelity`.

## M27C512 confirmation (operator-authorised substitute for the plan's named TMS27C512)

**Status: EVIDENCE — not a test, not a CI leg, cannot re-run automatically.**

**Naming note.** The plan named the TMS27C512 as the confirming part. The part actually seated in
the socket for this section is an **ST M27C512**, not a TMS27C512 — the operator does not have a
TMS27C512. This section heading is retitled from the plan's own wording to name the part that was
genuinely in the socket, per D-16.4's rule that the record must not claim a part that was never
present. See "Deviation 1" below for the authorisation.

### Deviation 1 — part substitution: TMS27C512 → ST M27C512

The plan's Task 3 `<action>` itself anticipated this outcome and named the criterion that governs it:
"If it reads as an M27C512 the part is a different UV device and the operator must decide whether
it still satisfies criterion 1's word *non-erasable* before anything is written." That reading
occurred (see the chip-ID history below), and the operator made that decision: **proceed.**

The decision rests on the database, not on assertion. `firestarter info m27c512` reports, verbatim:

```
Name:               M27C512,M27V512
Manufacturer:       SGS-THOMSON
Number of pins:     28
Memory size         0x10000
Type:               UV-EPROM
Can be erased:      no (UV erase only)
VCC:                5.0v
Programming VCC:    6.5v
VPP:                13.0v
Chip ID:            0x203d
Pulse delay:        100µS
...
Flags: 0x00000020
  - Provides readable manufacturer/device ID
```

`0x00000020` is `FLAG_OUTPUT_ENABLE` (`firestarter_app/firestarter/constants.py:114`).
`FLAG_CAN_ERASE` is `0x02` (`:109`) and is absent from that value — `0x00000020 & 0x02 == 0`. Per
`database.py:576-579`, `FLAG_CAN_ERASE` is set only when `electrical-type` is `EEPROM` or
`Flash/EEPROM` and `algo != 5`; M27C512's `electrical-type` is `UV-EPROM`, so the flag is clear by
the same code path that clears it for a TMS27C512. The M27C512 therefore satisfies criterion 1's
word *non-erasable* on the same measured basis the plan specified for the TMS27C512 — the
programmer cannot erase it, and the device holds the same `0x10000` geometry as the W27C512
rehearsal part.

**Authorised by:** the operator, at the Task 3 checkpoint, after being shown the chip-ID readings
below and the database entry above.

### Deviation 2 — target address: `0x00FF00` → `0x008000`

The plan's target address, `0x00FF00`, is unusable on this part. A full-device read-back
(`firestarter read m27c512 full.bin`, `0x10000` bytes, 7.39s) produced this map — 271 non-`0xFF`
bytes total across the device:

```
PROGRAMMED 0x000000-0x00000F   (16 bytes)
BLANK      0x000010-0x00FF00   (65265 bytes)
PROGRAMMED 0x00FF01-0x00FFFF   (255 bytes, a descending ramp: fe fd fc ... 00)
```

`0x00FF00` is the single last blank byte before the high programmed block. A 64-byte write starting
there would run into the programmed ramp at `0x00FF01`, one byte in. The operator authorised
**`0x008000`, 64 bytes**, instead — inside the blank span, `0x8000` clear of the low programmed
block and `0x7F01` clear of the high one.

**Authorised by:** the operator, at the Task 3 checkpoint, from the read-back map above.

**Why this device is stronger evidence than the W27C512 rehearsal.** The rehearsal part held data
below its target address only. This part holds programmed data on *both* sides of the chosen
target — 16 bytes below at `0x000000`-`0x00000F` and 255 bytes above at `0x00FF01`-`0x00FFFF` — so
a write succeeding at `0x008000` demonstrates the region-scoped check ignoring non-blank bytes in
both directions, not just one.

### Chip-ID readings and VPP history (operator statements and coordinator measurements)

Three chip-ID events are recorded across this bench session for the confirming part, plus the two
already recorded above for the W27C512. Recorded in full because the excursion is evidence, not
just its outcome — consistent with how the W27C512's own seating excursion is recorded above.

- **First read, VPP still at 12.1 V** (the setting left over from the W27C512 rehearsal):
  ```
  WARN: VPP is low: 12.1V < 13.0V
  Programmer reported chip ID: 0x203D
  ```
  Database lookup matched two rows on `0x203D`: `M27C512,M27V512 | SGS-THOMSON | 28 | 0x203D |
  UV-EPROM | 13.0v` and `M27C512,M27V512,M27... | ST | 28 | 0x203D | UV-EPROM | 13.0v`. Both name an
  M27C512, not a TMS27C512 (which the plan expected at `0x9785`) and not a W27C512
  (`0xDA08`) — the read is unambiguous.
- **After the operator raised VPP to 13.0 V:**
  ```
  Chip ID check passed for M27C512
  ```
  No VPP warning on this attempt, exit 0 — the pot setting is confirmed inside this part's 13 V
  window by the absence of the warning that fired at 12.1 V.
- **Conclusion:** `0x203D` is recorded as the value read for this part, not `0x9785` as the plan
  expected for a TMS27C512. This is the chip-ID event that triggered Deviation 1 above.

**VPP history for the whole session, all operator pot adjustments (the operator owns the pot; no
live monitor loop was run for any of these readings):**

| Setting | Part in socket | Reason | Outcome |
|---|---|---|---|
| 18.8 V | W27C512 | initial state at session start | firmware guard refused the chip-ID read at init (`ERROR: VPP is high: 18.8V > 12.0V`); nothing written |
| 12.1 V | W27C512 | operator set for the 12 V part (window 11.4–12.5 V) | Task 2's whole rehearsal ran here |
| 13.0 V | M27C512 | operator set for the 13 V part (window 12.35–13.5 V) | confirmed in window by the chip-ID check passing with no VPP warning |

### Pre-write device state (read back, not believed)

Per Deviation 1's decision and Deviation 2's address, the pre-write state was read back rather than
taken on the operator's statement of what the part holds:

- **`0x000000`-`0x00000F` window (first 16 bytes of a 64-byte read):**
  `44 20 82 3c fd e6 f1 c2 6b 30 f9 0e c7 dd 01 e4`, then `0xFF` from `0x000010` onward within that
  64-byte window. 16 non-`0xFF` bytes in the first 64.
- **`0x00FF00`-`0x00FF3F` window:** `0x00FF00` itself reads `ff`; `0x00FF01` onward is the
  descending ramp noted in the full-device map above. 63 non-`0xFF` bytes in that 64-byte window.

This device holds programmed data on both sides of the `0x008000` target, which is why it is
recorded above as stronger evidence than the W27C512 rehearsal's one-sided data placement.

### Pre-swap confirmation (automatable half, Task 3)

**Confirming the post-fix image is on the board.** The version string cannot do this by itself —
recorded above under W27C512 rehearsal, `VERSION` reads `3.0.0b33` under both the pre-fix and the
post-fix image, because it is bumped at a release cut, not per commit. The confirmation instead
rests on two things, both checked directly rather than assumed:

1. **Flash provenance.** The most recent `avrdude` flash of this session targeted
   `/workspaces/tmp/201-06-bench-images/postfix-e5842d8-leonardo.hex` (image SHA-256
   `36970caa...`, from `firestarter_fw` commit `e5842d8`), and `avrdude` reported
   `24134 bytes of flash verified` for that run. No flash has run since.
2. **Behavioural confirmation, on the board, not merely from the flash log.** The GREEN half of
   W27C512 rehearsal Run 2, run immediately beforehand on this same board, showed the write's
   progress denominator as `0xff40` (`0x00FF00` + `0x40`, the region end) rather than `0x10000`
   (the whole device) — the region-bounded write-loop denominator D-06 introduces, which the
   pre-fix image does not produce. `firestarter -p /dev/ttyACM0 fw` was re-run at this
   checkpoint and confirmed the board responds and reports `3.0.0b33, for controller: leonardo` —
   consistent with, though not sufficient on its own to prove, the post-fix image being loaded;
   the flash-provenance and behavioural evidence above (points 1 and 2) are what actually
   distinguish it.

**Making the socket safe for the chip change.** No RURP-specific "power off for chip swap"
procedure is documented anywhere in this project's notes; none was invented here. What was done:
the last operation run on the board (`verify`, the GREEN half's step 3 above) completed and
reported `Verify for W27C512 successful`, with no operation left in progress. `eprom_internal_write_init_body`'s
single-exit high-voltage wrapper (`firestarter_fw/src/proms/eprom.cpp:152-158`, per
`201-CONTEXT.md` D-09) guarantees VPP is de-asserted on every exit from a write or verify
operation, so the board is in its ordinary idle state — no VPP asserted, no bus drive — the same
state it is in between any two commands in normal use. Nothing further was issued to reach that
state; nothing needed to be. As an added margin for the physical swap itself (this project's own
records document a bench convention of protecting the chip-out step, even though the specific
"remove chip before sideload" rule that generalises from is Uno-class only and does not bind a
Leonardo — see the operator instructions below), the operator is asked to disconnect the board's
USB cable before removing the W27C512 and reconnect it only after the TMS27C512 is seated; that
disconnect/reconnect is a physical action for the operator, not something this session can
perform.

### Swap and chip-ID confirmation (operator statement)

The operator disconnected the board's USB cable, removed the W27C512, seated the M27C512, and
reconnected the cable. The operator states the M27C512 is seated in the correct orientation, with
the jumper this pin count calls for on the board's silkscreen set as printed — the same
configuration the W27C512 used, since both parts are 28-pin DIP on the same socket. The chip-ID
readings that followed the swap are recorded in "Chip-ID readings and VPP history" above.

### Last reversible moment — read-back confirmation before the write

Coordinator-measured, immediately before any write to this part. `firestarter read m27c512
confirm_preread.bin -a 0x008000 -s 64` was run and the output file inspected at file offset
`0x008000` (64 bytes) — **not** at file offset 0, because this read command pads its output file
from address 0, so a 64-byte read at `0x008000` produces an `0x8040`-byte file with the requested
bytes living at that offset, not at the start of the file. Misreading the padding as device content
would report a blank region as zero-filled; the bytes were read from the correct offset:

```
bytes at 0x8000..0x803F: ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
                          ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
all 0xFF: True
non-ff count: 0
```

`0x008000`-`0x00803F` reads entirely `0xFF`. This is the last reversible moment: the write that
follows cannot be undone on this UV-EPROM without a UV eraser.

### The confirming run (exactly once)

Host: `firestarter`, version `3.0.0b48` (editable install at `/workspaces/firestarter_app`, branch
`v1.40-program-parameter-fidelity`). Firmware on the board: `3.0.0b33`, confirmed by `firestarter
-p /dev/ttyACM0 fw` both immediately before and immediately after this run — the version string
does not distinguish the pre-fix and post-fix images (recorded under W27C512 rehearsal above), so
this run's firmware identity rests on the flash provenance and behavioural confirmation already
recorded under "Pre-swap confirmation" above, not on this string alone. Target file: 64 bytes,
pattern `deadbeef` repeated 16 times, distinct from the W27C512 rehearsal's `11223344` pattern so
the two transcripts are never confused for each other.

No `--skip-erase` on the write: `FLAG_CAN_ERASE` is clear for this part (Deviation 1 above), so
there is no erase to skip — the write proceeds directly to the blank check the same way it would on
a genuine TMS27C512.

```
$ firestarter -p /dev/ttyACM0 blank m27c512
Blank checking EPROM M27C512
ERROR: Not blank, at 0x000000, v: 0x44
Programmer error during BLANK_CHECK: Not blank, at 0x000000, v: 0x44
(exit code 1)

$ firestarter -p /dev/ttyACM0 write m27c512 m27c512_target.bin -a 0x008000
Writing m27c512_target.bin to M27C512
  0%|          | 0x0000/0x8040 bytes 100%|██████████| 0x8040/0x8040 bytes 100%|██████████| 0x8040/0x8040 bytes
  0%|          | 0x0000/0x0040 bytes 100%|██████████| 0x0040/0x0040 bytes
Write to M27C512 successful (0.84s).
(exit code 0)

$ firestarter -p /dev/ttyACM0 verify m27c512 m27c512_target.bin -a 0x008000
Verifying m27c512_target.bin against M27C512
  0%|          | 0x0000/0x0040 bytes 100%|██████████| 0x0040/0x0040 bytes
Verify for M27C512 successful (0.30s).
(exit code 0)
```

Measured 2026-09-20T09:18:01Z. The shape matches the expectation exactly: `blank-check` reports the
device not blank at the low address (`0x000000`, `v: 0x44` — the exact byte value read back and
recorded above under "Pre-write device state"), the write succeeds, and the verify is clean. The
write's first progress line (`0x0000/0x8040`) is the region-bounded blank-check scan from `0` to
`region_end` (`0x008000 + 0x40`); the second (`0x0000/0x0040`) is the write-loop's own
region-bounded denominator (D-06) — both bounded by the region, not by `mem_size` (`0x10000`).

### Criterion 1, adjudicated

A write into a blank region (`0x008000`, 64 bytes) of a non-blank part succeeded, on a part whose
`electrical-type` is `UV-EPROM` and whose `FLAG_CAN_ERASE` is therefore clear — the programmer has
no way to erase this part, so the non-blank state at `0x000000` and the programmed ramp at
`0x00FF01`-`0x00FFFF` could not have been cleared by anything this session did. The word
*non-erasable* in criterion 1 rests on this part, not on a proxy. **Criterion 1 is satisfied.** This
run cannot be repeated on this part: it is a UV-EPROM, the byte pattern just written cannot be
un-programmed without a UV eraser, and D-12 budgeted exactly one confirming run.

## How to read this record

This whole file is evidence. It was produced by a human at a bench with physical parts — chips
seated by hand, a pot adjusted by hand, a UV-EPROM that received one write it cannot take back. No
automated pipeline reached any of it: no CI leg can reach a UV part, because no CI runner has a
socket, a pot, or an operator to seat a chip in it. Nothing in this file re-runs automatically, and
nothing here should be read as if it does.

**What rests on this file alone:** criterion 1 of Phase 201 — that a write into a blank region of a
non-blank, non-erasable part succeeds on real silicon — rests entirely on the M27C512 confirming
run recorded above. No native suite and no host suite exercises real UV-EPROM electrical behaviour;
`fake_chip.py`'s model of blank semantics is software, not silicon, however faithfully it is built.
If this file were lost, criterion 1 would have no remaining evidence anywhere in the codebase.

**What is also covered elsewhere:** the region-scoped blank-check mechanism itself — the code path
this bench session exercises — is independently covered by the native and host suites landed in
earlier plans of this phase: the multi-chunk resumption and erase-end characterization in
`test/native/avr/test_val_eprom`, the source-contract coverage over the nine reference sites, and
the host-side `write -a` leg against `fake_chip.py` once it learned the region. Those suites prove
the mechanism is wired correctly in software; this file proves the mechanism does the right thing
against a real non-erasable part, which software alone cannot prove. The two are complementary —
software coverage cannot substitute for this file's role, and this file cannot substitute for
software coverage of the branches it does not exercise (the W27C512 rehearsal's RED/GREEN pair
above covers the defect-and-fix shape; this section covers only the confirming case).
