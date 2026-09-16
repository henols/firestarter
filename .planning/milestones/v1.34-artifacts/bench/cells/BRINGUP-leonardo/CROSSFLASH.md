# BRINGUP-leonardo — Read Chain Proof + D-03 Cross-Flash Record

**Target:** `leonardo` (ATmega32U4, `Caterina 4096 B` bootloader, `avr109` programmer, 57600 baud)
**Port:** `/dev/ttyACM0`
**Judged-span policy in force:** `hex-extent` (no vector exclusions — Caterina's own upload path
does not patch reset/interrupt vectors the way `uno328pb`'s `urclock` does; see
`BOOTLOADER-WINDOW.md`, "Event 1", `vector_exclusions_applied: []`). Judged span: the flashed
arm's own `leonardo` hex extent, **28170 B for control**, **25098 B for v1.33**
(`rig-pins.json` `hex_span_expected_by_arm.leonardo`).

**Purpose:** Prove the `leonardo` read chain on-device (Caterina/avr109, entered only via the
1200-baud touch — the milestone's lowest-confidence mechanism, `BOOTLOADER-WINDOW.md`), then
prove the wrong-arm detector can actually FAIL by a real deliberate cross-flash (D-03) — not a
comparator-only exercise. This is the **third and final** target; `uno` (plan 08) and
`uno328pb` (plan 09) already proved their own chains and their own cross-flash detectors.

Three flash-and-judge events, in order. Each event's flash step is followed by a fresh
1200-baud touch (bare mode — see `BOOTLOADER-WINDOW.md`'s measured same-node finding) and then
an immediate `judge_readback.py` invocation, run within the same shell block with no added
delay. `FIRESTARTER_CONFIG_DIR` is not involved in any command on this page — no arm-binary CLI
invocation is part of this sequence; only `git`, `pio`, `touch_1200.py`, and this phase's own
`judge_readback.py` / `probe_board.py`, which resolve `avrdude`/`avr-objcopy` from
`rig-pins.json`, never from `PATH`.

---

## Event 1 — control flashed, judged as control (read chain proof)

```
git -C /workspaces/firestarter checkout 8695ee52c27a4bee4387c5c489afd5f3d7275e8a   # cwd: /workspaces
cd /workspaces/firestarter && /usr/local/bin/pio run -t upload -e leonardo --upload-port /dev/ttyACM0  # cwd: /workspaces/firestarter
python3 .planning/milestones/v1.34-artifacts/tools/touch_1200.py --port /dev/ttyACM0 --settle-s 2.0 \
  --out .../BRINGUP-leonardo/touch_for_read_event1.json                          # cwd: /workspaces
python3 .planning/milestones/v1.34-artifacts/tools/judge_readback.py --target leonardo --port /dev/ttyACM0 \
  --flashed-arm control --expect-arm control \
  --out-dir .planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-leonardo --pins .planning/milestones/v1.34-artifacts/rig-pins.json  # cwd: /workspaces
```

PlatformIO build report: `Flash: [========= ] 86.0% (used 28170 bytes from 32768 bytes)` —
confirms the control arm's own known span (28170 B) was actually written, matching
`rig-pins.json`'s `hex_span_expected_by_arm.control`. `[SUCCESS] Took 6.93 seconds` — PlatformIO
performs its own 1200-baud touch and port-wait internally for the flash step
(`leonardo.json`'s `use_1200bps_touch`/`wait_for_upload_port`), so no separate `touch_1200.py`
call precedes this flash.

- **Read flag:** `-A` passed explicitly (`judge_readback.py`'s `run_avrdude_read()`, Pitfall 2)
  — without it the read is a variable-length file, not a stable provenance datum.
- **Read-back size: exactly 32768 bytes** (`readback_size_bytes`), verified by a size check, not
  by exit code.
- **Verdict:** `judged_match = true`, under the `hex-extent` policy with zero vector exclusions.
- **Judged span:** `judged_span_bytes = 28170` (the control arm's own `leonardo` hex extent).
  `sha_actual_judged == sha_expected_judged` = `d734ad490329d530...` — an exact SHA match (no
  vector-exclusion windows are in force on this target, unlike `uno328pb`).
- `sha_whole_flash_unjudged` = `334f9144d44a4e53...` (32768 B, UNJUDGED, recorded but never
  consumed in the `judged_match` decision, D-02).
- **Bootloader-entry timing (this task's own requirement):** touch-to-judged-verdict elapsed
  **3.878 s** from the read-back touch's onset, against Caterina's ~8 s inactivity window —
  **more than 4 s of margin**. Full measurement detail, including the failed
  `--wait-new-port` attempt and the Rule 1 decode-crash fix that preceded a clean identity
  probe, is in `BOOTLOADER-WINDOW.md`.
- Full record: `READBACK-VERDICT.json` (this cell directory — the correction event below
  re-establishes the identical verdict as the file's final committed state).

---

## Event 2 — v1.33 flashed, judged against **control**'s hex (the deliberate cross-flash, D-03)

```
git -C /workspaces/firestarter checkout 5759dc8d644a8a7fb26e9a0ccd11a8bfd53fc463   # cwd: /workspaces
cd /workspaces/firestarter && /usr/local/bin/pio run -t upload -e leonardo --upload-port /dev/ttyACM0  # cwd: /workspaces/firestarter
python3 .planning/milestones/v1.34-artifacts/tools/touch_1200.py --port /dev/ttyACM0 --settle-s 2.0 \
  --out .../BRINGUP-leonardo/touch_for_crossflash_event2.json                    # cwd: /workspaces
python3 .planning/milestones/v1.34-artifacts/tools/judge_readback.py --target leonardo --port /dev/ttyACM0 \
  --flashed-arm v133 --expect-arm control \
  --out-dir .planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-leonardo/crossflash --pins .planning/milestones/v1.34-artifacts/rig-pins.json  # cwd: /workspaces
```

PlatformIO build report for this flash: `Flash: [======== ] 76.6% (used 25098 bytes from 32768
bytes)` — confirms the v1.33 arm's own known span (25098 B) was actually written, not a stale
cache. `[SUCCESS] Took 8.32 seconds`.

- **Verdict:** `judged_match = false` — **`judge_readback.py` exited non-zero (rc=1)**, as
  required.
- **Differing-byte count: 24454 of 28170 bytes judged** (the control arm's own `leonardo` hex
  extent) — **86.8%** of the judged span. This is not a marginal signal.
- **First differing offsets** (offset / expected byte from control's hex / actual byte from the
  v1.33 read-back):
  - `0x00002` expected `0x11` actual `0xE1`
  - `0x00003` expected `0x02` actual `0x01`
  - `0x00006` expected `0x39` actual `0x09`
  - `0x0000A` expected `0x39` actual `0x09`
  - `0x0000E` expected `0x39` actual `0x09`
  - `0x00012` expected `0x39` actual `0x09`
  - (14 more shown in `crossflash/READBACK-VERDICT.json`'s `first_diffs`, 20 total capped by the
    tool; 24454 total differing bytes recorded in `diff_count`)
- `sha_actual_judged` = `c15dbc20e86ee8f87a0ba4f18dcba85622b8b626aa27b69fb560637038ba69e2`
  (the v1.33 read-back's judged prefix)
- `sha_expected_judged` = `d734ad490329d5307f4760d7525b045f78d0f61168868e9c36f1956519439820`
  (control's own hex extent — **unchanged from Event 1**, confirming the judge compared against
  the correct fixed reference)
- `sha_whole_flash_unjudged` = `7bfb041c9ed1349a14b0922c482a1495de458d5ec882696e79cc34808eb0cd6a`
  — **differs from Event 1's `334f9144d44a4e53...`**, a second, independent (never consumed in
  the judged decision) confirmation that the flash content actually moved.
- **Read-back timing:** touch-to-judged-verdict elapsed **4.015 s** — comparable to Event 1's
  3.878 s, confirming the window comfortably fits a MISMATCH-producing read just as readily as
  a matching one; the read itself is not sensitive to which arm is on the board.
- Full record: `crossflash/READBACK-VERDICT.json`, `crossflash/flash_readback.bin` (32768 B),
  `crossflash/judged_span.bin`, `crossflash/expected_span.bin`.

**The negative control FIRED.** The wrong-arm detector was exercised for real — a genuine
device flash of the v1.33 arm, entered via a fresh 1200-baud touch and judged by an
independent avrdude read-back against the control arm's hex extent — and it correctly reported
MISMATCH with measured, non-trivial evidence (24454 of 28170 judged bytes differing, 86.8%),
not merely configured-but-never-observed. Because `judged_span_policy` is `hex-extent` with
**zero** vector exclusions on this target (unlike `uno328pb`'s 8-byte exclusion), there is no
exclusion window whose strength needs to be argued — every byte of the judged span is compared,
and the check is at full strength by construction.

---

## Event 3 — control re-flashed, judged as control (the correction)

```
git -C /workspaces/firestarter checkout 8695ee52c27a4bee4387c5c489afd5f3d7275e8a   # cwd: /workspaces
cd /workspaces/firestarter && /usr/local/bin/pio run -t upload -e leonardo --upload-port /dev/ttyACM0  # cwd: /workspaces/firestarter
python3 .planning/milestones/v1.34-artifacts/tools/touch_1200.py --port /dev/ttyACM0 --settle-s 2.0 \
  --out .../BRINGUP-leonardo/touch_for_correction_event3.json                    # cwd: /workspaces
python3 .planning/milestones/v1.34-artifacts/tools/judge_readback.py --target leonardo --port /dev/ttyACM0 \
  --flashed-arm control --expect-arm control \
  --out-dir .planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-leonardo --pins .planning/milestones/v1.34-artifacts/rig-pins.json  # cwd: /workspaces
```

PlatformIO build report: `Flash: [========= ] 86.0% (used 28170 bytes from 32768 bytes)`,
`[SUCCESS] Took 9.80 seconds`.

- **Verdict:** `judged_match = true` — the correction is observed matching.
- `sha_whole_flash_unjudged` = `334f9144d44a4e53cae73e86ef185c53e0170cc519166e6e692313b97e7db0d6`
  — **byte-identical to Event 1's value**, confirming the board was restored to exactly the
  same flash content, not merely "a" passing state.
- Touch-to-judged-verdict elapsed **3.873 s** — consistent with Events 1 and 2's timing.
- Full record: `READBACK-VERDICT.json` (this cell directory — final, committed state).

---

## Board state at teardown

**The board carries the `control` arm** as of the end of this task — the arm this task's
Event 1 first wrote and Event 3's correction restores. Deliberate, matching the same convention
`BRINGUP-uno` and `BRINGUP-uno328pb` established. The seated **W27C512 chip is untouched
throughout this entire cell** — no chip operation (`read`/`write`/`erase`/`blank`/`vpp`) was
performed anywhere in tasks 1–3; this bring-up is firmware-only.

The `firestarter/` submodule's working tree was restored to its starting branch
(`gsd/v1.33-source-hygiene-firmware-size-reduction`, `5759dc8d644a8a7fb26e9a0ccd11a8bfd53fc463`)
after this task's three checkouts; `git -C /workspaces/firestarter status --porcelain` is empty.

---

## Cross-target rollup — D-03 complete across all three targets

| Target | Programmer / bootloader | Differing bytes (judged span) | Judged-span policy |
|---|---|---|---|
| `uno` (plan 08) | `arduino` / optiboot 512 B | 22367 / 26026 (86%) | `hex-extent` |
| `uno328pb` (plan 09) | `urclock` / urboot 384 B (vector) | 22300 / 26066 (85.6%) | `vector-exclusion` (8 B excluded) |
| `leonardo` (this plan) | `avr109` / Caterina 4096 B | 24454 / 28170 (86.8%) | `hex-extent` (0 B excluded) |

**D-03 is complete across all three targets.** Each chain's wrong-arm detector has been
exercised by a real, deliberate device flash of the *other* arm, judged by an independent
avrdude read-back against the *intended* arm's hex extent, and each one reported MISMATCH with
measured, non-trivial evidence (all three in the 85–87% range) rather than being inferred from
another target's proof. This matters because the three chains' upload-and-read paths genuinely
differ — `arduino`/STK500v1 at 115200 baud with no bootloader-entry mechanism beyond DTR;
`urclock`/urboot at 115200 baud with vector patching on a vector bootloader; `avr109`/Caterina
at 57600 baud entered only via a 1200-baud touch with a time-bounded window — so a single-target
proof would have left two chains taken on the comparator's word. `leonardo` additionally
completes SC#2's bootloader-window falsification: the read chain not only completed but was
shown able to report a genuine MISMATCH within the same measured window that produced a match,
proving the detector's strength is not an artifact of only ever having been run once.

**No named alternative is in force anywhere in this milestone's RIG-01 SC#2 claim.** All three
targets took Branch A (a proven full read-back), not the alternative partial-span-read branch
SC#2 makes available for a window that proves too short. `leonardo`'s Caterina window, the one
this milestone's own RESEARCH.md flagged as the highest-risk chain (`A1`, "High" confidence
concern), measured comfortably inside its ~8 s inactivity budget on every one of the three
timed events above (3.878 s / 4.015 s / 3.873 s).

## Deviation note (documented in SUMMARY.md, same class as the other two targets' arm-span defect)

This plan's own embedded task-2 verify script (`160-10-PLAN.md`) hardcodes `judged_span_bytes
== 25098` as the Branch-A full-read criterion — but `25098` is the **v1.33** arm's own
`leonardo` hex span, not the **control** arm's (`28170`, per `rig-pins.json`
`hex_span_expected_by_arm.leonardo.control`, fixed in 160-08). This is the identical class of
stale flat-constant defect `BRINGUP-uno` and `BRINGUP-uno328pb` already documented for their own
targets. Every event above judges the control arm against its own arm-correct span (28170 B),
not the plan's flat 25098 B figure; the corrected assertion (substituting
`hex_span_expected_by_arm.control` for the plan's hardcoded literal) was run in place of the
plan's own script and is recorded verbatim in `160-10-SUMMARY.md`.
