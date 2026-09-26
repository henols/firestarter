# BRINGUP-uno328pb — Read Chain Proof + D-03 Cross-Flash Record

**Target:** `uno328pb` (ATmega328PB, `urboot 384 B` bootloader, `urclock` programmer)
**Port:** `/dev/ttyUSB0`
**Judged-span policy in force:** `vector-exclusion` (derived in `BOOTLOADER.md` from a live
`-xshowvector` interrogation plus a measured flash+read-back diff). Exclusions: reset vector
`[0,4)` and interrupt vector 25 (SPM_Ready) `[100,104)` — **8 bytes** excluded from every
comparison below, out of the control arm's full **26074 B** judged extent (**26066 B** are
actually compared for control; **22992 B** for the v1.33 arm, whose own hex spans 23000 B).

**Purpose:** Prove the `uno328pb` read chain on-device (the read flag `-A` is not the default
for this programmer — Pitfall 2), then prove the wrong-arm detector can actually FAIL by a
real deliberate cross-flash (D-03) — not a comparator-only exercise.

Three flash-and-judge events, in order. `FIRESTARTER_CONFIG_DIR` is not involved in any
command on this page — no arm-binary CLI invocation is part of this sequence; only `git`,
`pio`, and this phase's own `judge_readback.py`, which resolves `avrdude`/`avr-objcopy` from
`rig-pins.json`, never from `PATH`.

---

## Event 1 — control flashed, judged as control (read chain proof)

The control arm was flashed once and read twice: first by an ad hoc diagnostic read used to
**derive** the vector-exclusion windows (`BOOTLOADER.md`, before the comparator was armed —
that diagnostic read is not a position record and is not the read this event reports), then
by this task's own **official**, tool-recorded read-back below, run after
`judged_span_policy` was resolved.

```
git -C /workspaces/firestarter checkout 8695ee52c27a4bee4387c5c489afd5f3d7275e8a   # cwd: /workspaces
/usr/local/bin/pio run -t upload -e uno328pb --upload-port /dev/ttyUSB0            # cwd: /workspaces/firestarter
python3 .planning/milestones/v1.34-artifacts/tools/judge_readback.py --target uno328pb --port /dev/ttyUSB0 \
  --flashed-arm control --expect-arm control \
  --out-dir .planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-uno328pb --pins .planning/milestones/v1.34-artifacts/rig-pins.json  # cwd: /workspaces
```

PlatformIO build report: `Flash: [========  ]  79.6% (used 26074 bytes from 32768 bytes)` —
confirms the control arm's own known span (26074 B) was actually written, matching
`rig-pins.json`'s `hex_span_expected_by_arm.control`.

- **Read flag:** `-A` passed explicitly (`judge_readback.py`'s `run_avrdude_read()`, Pitfall 2)
  — without it the read is a variable-length file, not a stable provenance datum.
- **Read-back size: exactly 32768 bytes** (`readback_size_bytes`), verified by a size check,
  not by exit code.
- **Verdict:** `judged_match = true`, under the `vector-exclusion` policy, with
  `vector_exclusions_applied` carrying the two windows (offset 0/length 4, offset 100/length
  4) — the exclusion is recorded in the verdict itself, not only inside the tool.
- **Judged span:** `judged_span_bytes = 26074` (the control arm's own `uno328pb` hex extent —
  the field name is the `.hex`'s own address extent per D-02, unreduced by the exclusion;
  **26066 of those 26074 bytes are actually byte-compared**, the other 8 being the two excluded
  vector windows).
- `sha_actual_judged` = `43dcb663c5bfcf29...`, `sha_expected_judged` = `b18a71515b3446...` —
  these two SHAs are **expected to differ** under a vector-exclusion policy (the actual
  read-back genuinely differs from the raw hex at the two patched vector windows; `judged_match`
  is computed by the exclusion-aware byte comparison, not by SHA equality, whenever any
  exclusion windows are in force).
- `sha_whole_flash_unjudged` = `2c0a81d25d6422ab...` (32768 B, UNJUDGED, recorded but never
  consumed in the `judged_match` decision).
- **Elapsed wall-clock** (avrdude read + objcopy normalize, around the `judge_readback.py`
  invocation): **~4.07 s** — comparable to, and somewhat faster than, the `uno` read-chain
  baseline from plan 08 (~5.5 s, three timed runs at 5.49–5.51 s). The two chains use
  different avrdude programmers (`urclock` vs `arduino`) at the same 115200 baud, so a modest
  difference either way is unsurprising; both are well under 10 s, and neither result changes
  this plan's determination.
- Full record: `READBACK-VERDICT.json` (this cell directory — the correction event below
  re-establishes the identical verdict as the file's final committed state).

---

## Event 2 — v1.33 flashed, judged against **control**'s hex (the deliberate cross-flash, D-03)

```
git -C /workspaces/firestarter checkout 5759dc8d644a8a7fb26e9a0ccd11a8bfd53fc463   # cwd: /workspaces
/usr/local/bin/pio run -t upload -e uno328pb --upload-port /dev/ttyUSB0            # cwd: /workspaces/firestarter
python3 .planning/milestones/v1.34-artifacts/tools/judge_readback.py --target uno328pb --port /dev/ttyUSB0 \
  --flashed-arm v133 --expect-arm control \
  --out-dir .planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-uno328pb/crossflash --pins .planning/milestones/v1.34-artifacts/rig-pins.json  # cwd: /workspaces
```

PlatformIO build report for this flash: `Flash: [=======   ]  70.2% (used 23000 bytes from
32768 bytes)` — confirms the v1.33 arm's own known span (23000 B) was actually written, not a
stale cache.

- **Verdict:** `judged_match = false` — **`judge_readback.py` exited non-zero (rc=1)**, as
  required.
- **Differing-byte count: 22300 of 26066 bytes actually judged** (the 26074 B extent minus the
  8 excluded vector-window bytes) — **85.6%** of the judged span. This is not a marginal
  signal.
- **Exclusion still in force during this event too:** the first differing offset reported is
  `0x00006` (6), not `0x00000` — offsets 0–3 (the reset-vector window) were correctly *skipped*
  by the comparator even while judging a genuine mismatch, confirming the exclusion mechanism
  applies uniformly rather than only on a clean match.
- **First differing offsets** (offset / expected byte from control's hex / actual byte from
  the v1.33 read-back):
  - `0x00006` expected `0xF7` actual `0xC7`
  - `0x0000A` expected `0xF7` actual `0xC7`
  - `0x0000E` expected `0xF7` actual `0xC7`
  - `0x00012` expected `0xF7` actual `0xC7`
  - `0x00042` expected `0x88` actual `0xE2`
  - `0x00043` expected `0x24` actual `0x20`
  - (14 more shown in `crossflash/READBACK-VERDICT.json`'s `first_diffs`, 20 total capped by
    the tool; 22300 total differing bytes recorded in `diff_count`)
- `sha_actual_judged` = `9d047995bebb03a4...` (the v1.33 read-back's judged prefix)
- `sha_expected_judged` = `b18a71515b344662...` (control's own hex extent — **unchanged from
  Event 1**, confirming the judge compared against the correct fixed reference)
- `sha_whole_flash_unjudged` = `e8aab2dc38722f6b...` — **differs from Event 1's
  `2c0a81d25d642...`**, a second, independent (never consumed in the judged decision)
  confirmation that the flash content actually moved.
- Full record: `crossflash/READBACK-VERDICT.json`, `crossflash/flash_readback.bin` (32768 B),
  `crossflash/judged_span.bin`, `crossflash/SHA256SUMS.txt`.

**The negative control FIRED.** The wrong-arm detector was exercised for real — a genuine
device flash of the v1.33 arm, judged by an independent avrdude read-back against the control
arm's hex extent under the vector-exclusion policy resolved in `BOOTLOADER.md` — and it
correctly reported MISMATCH with measured, non-trivial evidence (22300 of 26066 judged bytes
differing, 85.6%), not merely configured-but-never-observed.

**Post-exclusion detector strength, stated as a number (SC#2's own requirement):** 8 bytes are
excluded from every comparison on this target; the negative control still fired with 22300
differing bytes against a judged region of 26066 bytes that remain compared — an 8-byte
exclusion cannot plausibly mask a wrong-arm flash that diverges across **2,788 times** that
many bytes (22300 / 8 ≈ 2788×). The check stays falsifiable at full strength.

---

## Event 3 — control re-flashed, judged as control (the correction)

```
git -C /workspaces/firestarter checkout 8695ee52c27a4bee4387c5c489afd5f3d7275e8a   # cwd: /workspaces
/usr/local/bin/pio run -t upload -e uno328pb --upload-port /dev/ttyUSB0            # cwd: /workspaces/firestarter
python3 .planning/milestones/v1.34-artifacts/tools/judge_readback.py --target uno328pb --port /dev/ttyUSB0 \
  --flashed-arm control --expect-arm control \
  --out-dir .planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-uno328pb --pins .planning/milestones/v1.34-artifacts/rig-pins.json  # cwd: /workspaces
```

- **Verdict:** `judged_match = true` — the correction is observed matching.
- `sha_whole_flash_unjudged` = `2c0a81d25d6422ab...` — **byte-identical to Event 1's value**,
  confirming the board was restored to exactly the same flash content, not merely "a" passing
  state.
- Full record: `READBACK-VERDICT.json` (this cell directory — final, committed state).

---

## Board state at teardown

**The board carries the `control` arm** as of the end of this task — the arm task 2's
diagnostic flash and this task's Event 1 first wrote, and this task's correction (Event 3)
restores. Deliberate, matching the same convention `BRINGUP-uno` established.

The `firestarter/` submodule's working tree was restored to its starting branch
(`gsd/v1.33-source-hygiene-firmware-size-reduction`, `5759dc8d644a8a7fb26e9a0ccd11a8bfd53fc463`)
after this task's three checkouts; `git -C /workspaces/firestarter status --porcelain` is
empty.

---

## Metadata suppression, re-confirmed

`-xshowall`'s own printed output (`BOOTLOADER.md`, Query 1) shows this board's *pre-existing*
content (from a session before this bring-up) already carried a filename+date metadata block
(`2026-08-21 20.05 firestarter_uno328pb.hex`) — direct evidence that urclock's metadata write
is real and observable when not suppressed. Every flash in this record ran through the pinned
PlatformIO path, which appends `-xnometadata` unconditionally for this protocol
(`~/.platformio/platforms/atmelavr/builder/main.py:220`), so none of the three events above
wrote a fresh metadata block — consistent with the whole-flash unjudged SHA being reproducible
across Events 1 and 3 (byte-identical), which a fresh, date-stamped metadata write would have
broken.

## Mid-run replug (record correction, added 2026-08-27)

**A physical event occurred between Event 3's flash and its judged read-back, and it was
absent from this record until now — that omission is itself the defect this note corrects.**

Task 1's original operator gate recorded the socket declaration `"Yes — shield on, chip
removed"`. That declaration was **false**, and the operator has since corrected it: no shield
was fitted for any event in this file (Event 1 through the first part of Event 3) — the
operator's own words: *"I sad the sheil was on but it wasnt, so i added it now"*. The shield
was fitted **after** Event 3's flash, via a deliberate unplug/fit/replug, which the operator
also confirmed explicitly: *"Yes — unplugged, fitted, replugged."*

**Timing, from the recorded logs and the device-node timestamp:**

| Time (UTC) | Event |
|---|---|
| 06:23–06:34:30 | Task 2 interrogation + Events 1–2 + Event 3's flash — **no shield fitted** |
| 06:34:30.52 | `09_pio_upload_control_correction_event3.stdout.log` — Event 3's correction flash completes; avrdude self-verifies **26240 bytes of flash verified**, `[SUCCESS] Took 9.36 seconds` |
| ~06:34:40 | Operator unplugs the board, fits the shield, replugs — `/dev/ttyUSB0`'s device-node creation time moves from 06:18 to **06:34:40**, corroborating the replug independently of the operator's own statement |
| 06:34:43.55 | `10_judge_readback_correction_event3.stdout.log` — Event 3's judged read-back runs, ~3 s **after** the replug |

**Harmlessness derivation (shown, not assumed):**

1. **No safety invariant was violated.** With no shield fitted, there is no socket and
   therefore no chip present, for the entire span 06:23–06:34:40. The Uno-class chip-out rule
   exists to keep a chip out of the socket while avrdude drives the bus; with no shield there
   is no socket at all, so the rule is satisfied *a fortiori* for every avrdude invocation in
   this file — the shield (and, per the operator, a chip) arrived only *after* the last flash
   in this record.
2. **The plan's own requirements are unaffected.** 160-09-PLAN.md task 1: *"A shield is not
   required — the flash and read-back need the board only."* The absence of a shield during
   Events 1–3 is exactly the state the plan anticipated as sufficient; it does not invalidate
   any measurement above.
3. **The replug itself was harmless to Event 3's verdict, and this is measured, not assumed.**
   Event 3's flash self-verified as complete and byte-correct (avrdude's own "26240 bytes of
   flash verified") at 06:34:30.52, roughly **10 seconds before** the unplug at ~06:34:40. Flash
   memory is non-volatile — an unplug/replug that follows a completed, self-verified write does
   not alter its content, and a serial replug forces a fresh device reset, which is the normal
   precondition for any avrdude read regardless. Event 3's judged read-back then ran at
   06:34:43.55, ~3 seconds **after** the replug, and reported `judged_match = true` with
   `sha_whole_flash_unjudged` byte-identical to Event 1's value — an independent, non-judged
   confirmation that the flash content the replug bracketed was unchanged. No evidence in this
   record contradicts the harmlessness conclusion; if any had (a truncated read, a whole-flash
   SHA divergence, a judged mismatch), it would be reported here instead.

**Corrected record pointers:** `bench/EVIDENCE.jsonl` row 3's `shield` field, `probe.json`'s
`operator_declared_socket_state` / `device_node_reenumeration_midrun_replug` fields, and
`160-09-SUMMARY.md`'s Deviation/Finding all carry this same correction and are consistent with
this section.

---

## Arm-span cross-check (per-arm hex span, not a flat value)

`rig-pins.json`'s `hex_span_expected_by_arm.uno328pb` (fixed in 160-08 alongside `uno`'s
identical defect) correctly gave `judge_readback.py`'s `cross_check_hex_span()` the
**per-arm** expected span for every event above: 26074 B when `--expect-arm control`, 23000 B
when the v1.33 arm was the one actually written (confirmed by PlatformIO's own build report in
Event 2). No override was needed here — the fix already landed in this plan's own dependency
(160-08) before this plan ran.

**Deviation note (documented in SUMMARY.md):** this plan's own written text and one embedded
verify script (`160-09-PLAN.md` task 3) refer to a flat `23000` B judged span throughout —
inherited from before 160-08 distinguished `hex_span_expected_by_arm` per arm, the same class
of stale constant `BRINGUP-uno`'s `CROSSFLASH.md` already documented for `uno` (there,
`22952` was `v133`'s span, not `control`'s). `23000` is genuinely the **v1.33** arm's
`uno328pb` hex span; the **control** arm's is `26074`. Every event above judges the control
arm against its own arm-correct span (26074 B), not the plan's flat `23000` figure.
