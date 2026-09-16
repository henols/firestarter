# BRINGUP-uno — D-03 Cross-Flash Record

**Target:** `uno` (ATmega328P, optiboot bootloader, `arduino` programmer)
**Port:** `/dev/ttyACM0`
**Purpose:** Prove the wrong-arm detector (independent avrdude read-back judged against a
named arm's hex extent) can actually FAIL, by a real deliberate cross-flash — not a
comparator-only exercise. SHA-comparing a good read-back against the other arm's hex would
only prove that two different files hash differently; it would never exercise the read-back
path at all.

Three flash-and-judge events, in order. Every command below ran with cwd exactly as shown;
`FIRESTARTER_CONFIG_DIR` is not involved in any command on this page (no arm-binary CLI
invocation is part of the cross-flash sequence itself — only `git`, `pio`, and this phase's
own `judge_readback.py`, which resolves `avrdude`/`avr-objcopy` from `rig-pins.json`, never
from `PATH`).

---

## Event 1 — control flashed, judged as control (baseline match, from Task 2)

```
git -C /workspaces/firestarter checkout 8695ee52c27a4bee4387c5c489afd5f3d7275e8a   # cwd: /workspaces
/usr/local/bin/pio run -t upload -e uno --upload-port /dev/ttyACM0                # cwd: /workspaces/firestarter
python3 .planning/milestones/v1.34-artifacts/tools/judge_readback.py --target uno --port /dev/ttyACM0 \
  --flashed-arm control --expect-arm control \
  --out-dir .planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-uno --pins .planning/milestones/v1.34-artifacts/rig-pins.json  # cwd: /workspaces
```

- **Verdict:** `judged_match = true`
- **Judged span:** 26026 B (the **control** arm's own `uno` hex extent — see the "Arm-span
  defect resolved before this task ran" note below; this is NOT the plan's originally-stated
  22952 B, which is `v133`'s span)
- `sha_actual_judged == sha_expected_judged` = `f60fa76ff808b5ca...`
- `sha_whole_flash_unjudged` = `d9eb943a55bc0668...` (32768 B, UNJUDGED, distinct from the
  judged-span SHA)
- Elapsed wall-clock (avrdude read + objcopy normalize): ~5.5 s (three timed runs: 5.495 s,
  5.505 s, 5.493 s) — the uno read-chain cost baseline for plans 09/10.
- Full record: `READBACK-VERDICT.json` (this cell directory, current file — the correction
  event below re-establishes the identical verdict as the file's final committed state).

---

## Event 2 — v1.33 flashed, judged against **control**'s hex (the deliberate cross-flash)

```
git -C /workspaces/firestarter checkout 5759dc8d644a8a7fb26e9a0ccd11a8bfd53fc463   # cwd: /workspaces
/usr/local/bin/pio run -t upload -e uno --upload-port /dev/ttyACM0                # cwd: /workspaces/firestarter
python3 .planning/milestones/v1.34-artifacts/tools/judge_readback.py --target uno --port /dev/ttyACM0 \
  --flashed-arm v133 --expect-arm control \
  --out-dir .planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-uno/crossflash --pins .planning/milestones/v1.34-artifacts/rig-pins.json  # cwd: /workspaces
```

PlatformIO build report for this flash: `RAM: 1434/2048 B (70.0%), Flash: 22952/32768 B
(70.0%)` — confirms the v1.33 arm's own known span (22952 B) was actually written, not a
stale cache.

- **Verdict:** `judged_match = false` — **`judge_readback.py` exited non-zero (rc=1)**, as
  required.
- **Differing-byte count: 22367 of 26026** judged bytes (86% of the judged span) — this is
  not a marginal signal; the two `uno` images diverge substantially across the whole span.
- **First differing offsets** (offset / expected byte from control's hex / actual byte from
  the v1.33 read-back):
  - `0x00002` expected `0xA0` actual `0x70`
  - `0x00006` expected `0xC8` actual `0x98`
  - `0x0000A` expected `0xC8` actual `0x98`
  - `0x0000E` expected `0xC8` actual `0x98`
  - `0x00042` expected `0x5F` actual `0xB9`
  - `0x00043` expected `0x24` actual `0x20`
  - (17 more shown in `crossflash/READBACK-VERDICT.json`'s `first_diffs`, 20 total capped by
    the tool)
- `sha_actual_judged` = `5ca22f3a7090c7c364dca9867ffb1ba9b5d36a66aba2cf5ff8ed3af8c78c18e1`
  (the v1.33 read-back's judged prefix)
- `sha_expected_judged` = `f60fa76ff808b5ca0454e0bff0698f605a57a61069f6c7b8061e61b27ac3fa23`
  (control's own hex extent — **unchanged from Event 1**, confirming the judge compared
  against the correct fixed reference)
- `sha_whole_flash_unjudged` = `944b73f6158e633d09fe5c743c9375159c499c4cdc03537d24cdd59770920eb`
  — **differs from Event 1's `d9eb943a55bc0668...`**, a second, independent (SHA-comparison
  never depended on) confirmation that the flash content actually moved.
- Full record: `crossflash/READBACK-VERDICT.json`, `crossflash/flash_readback.bin` (32768 B),
  `crossflash/judged_span.bin`, `crossflash/SHA256SUMS.txt`.

**The negative control FIRED.** The wrong-arm detector was exercised for real — a genuine
device flash of the v1.33 arm, judged by an independent avrdude read-back against the control
arm's hex extent — and it correctly reported MISMATCH with measured, non-trivial evidence
(22367 differing bytes out of 26026, first offsets and byte values quoted above), not merely
configured-but-never-observed.

---

## Event 3 — control re-flashed, judged as control (the correction)

```
git -C /workspaces/firestarter checkout 8695ee52c27a4bee4387c5c489afd5f3d7275e8a   # cwd: /workspaces
/usr/local/bin/pio run -t upload -e uno --upload-port /dev/ttyACM0                # cwd: /workspaces/firestarter
python3 .planning/milestones/v1.34-artifacts/tools/judge_readback.py --target uno --port /dev/ttyACM0 \
  --flashed-arm control --expect-arm control \
  --out-dir .planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-uno --pins .planning/milestones/v1.34-artifacts/rig-pins.json  # cwd: /workspaces
```

- **Verdict:** `judged_match = true` — the correction is observed matching.
- `sha_whole_flash_unjudged` = `d9eb943a55bc0668...` — **byte-identical to Event 1's value**,
  confirming the board was restored to exactly the same flash content, not merely "a"
  passing state.
- Full record: `READBACK-VERDICT.json` (this cell directory — final, committed state).

---

## Board state at teardown

**The board carries the `control` arm** as of the end of this task. This is the arm task 2
flashed first and this task's correction restores — deliberate, per the plan's own
instruction ("the arm on the board at the end of task 3's correction sequence is the one this
plan leaves behind deliberately rather than incidentally"). Plan 09/10 (uno328pb, leonardo)
use a different board/target and are unaffected by this board's arm state.

The `firestarter/` submodule's working tree was restored to its starting branch
(`gsd/v1.33-source-hygiene-firmware-size-reduction`) after this task's three checkouts;
`git -C /workspaces/firestarter status --porcelain` is empty.

---

## Arm-span defect resolved before this task ran

The plan's own task 2 acceptance criterion stated `judged_span_bytes` must be `22952` — but
`22952` is the **v1.33** arm's `uno` hex span, not the **control** arm's (measured,
`images/BUILD-MANIFEST.json`: control=26026 B, v133=22952 B — a ~3 KB divergence, root-caused
there to PR #55's VPE-settle amortisation plus Phase 158's size reduction landing only on the
v1.33 side). `rig-pins.json`'s `targets.uno.hex_span_expected` carried a single flat value
(22952) for a quantity that is genuinely arm-dependent, which would have made
`judge_readback.py`'s own cross-check reject a correctly-flashed control-arm read-back as "not
the artifact the manifest describes."

Resolved in this plan (see SUMMARY.md "Deviations" for the full account) by: (1) adding
`hex_span_expected_by_arm` to `rig-pins.json` for all three targets, keyed by arm, with the
flat `hex_span_expected` kept unedited for backward compatibility; (2) fixing
`judge_readback.py`'s `cross_check_hex_span()` to consult the per-arm map first, and to
correctly normalize `BUILD-MANIFEST.json`'s `images` field (a **list**, not the dict shape the
tool's own pre-existing selftest fixture assumed — a second, related bug fixed alongside the
first). Every event above judges against the arm-correct span (26026 B for control), not the
plan's originally-stated 22952 B.

---

## Finding: PlatformIO's avrdude resolution is per-env, not a single choice

Corrected 2026-08-27 per orchestrator spot-check (the first version of this finding, recorded
in this plan's task-2 commit message and `EVIDENCE.jsonl`, stated it as a general property of
"PlatformIO's own upload path" for `uno`, which reads as broader than it is — the distinction
matters most on exactly the target plan 09 flashes next).

Measured from cwd `/workspaces/firestarter`:

| env | `pio pkg list` avrdude | required | protocol |
|---|---|---|---|
| `uno` | `tool-avrdude @ 1.60300.200527` (6.3) | `~1.60300.0` | `arduino` |
| `uno328pb` | `tool-avrdude @ 1.80100.0` (8.1) | `~1.80100.0` | `urclock` |
| `leonardo` | `tool-avrdude @ 1.60300.200527` (6.3) | `~1.60300.0` | `avr109` |

Capability check (each binary's own `-C` conf supplied explicitly — 6.3's shipped conf path is
a dead hardcoded path, so `-c '?type'` without `-C` fails for that unrelated reason, not for a
capability reason):

```
avrdude 6.3  -c '?type' | grep -c urclock   -> 0   (6.3 has no urclock programmer id at all)
avrdude 8.1  -c '?type' | grep -c urclock   -> 1
avrdude 6.3  -c avr109 -p atmega32u4 -P /dev/null -n
             -> gets past option-parse to a real port-open attempt (fails only because
                /dev/null isn't a serial device); avrdude.conf:903 defines `id = "avr109"`
                (6.3's `-c '?type'` SUMMARY listing omits it, but the id is real and accepted)
```

**Conclusion: there is no target on which PlatformIO hands a protocol to an avrdude build that
cannot drive it.** PlatformIO resolves 8.1 precisely where `urclock` is required — MiniCore's
`ATmega328PB.json` declares `"protocol": "urclock"` and its env pins `~1.80100.0` — and
resolves 6.3 for `uno`/`leonardo`, both of whose protocols (`arduino`, `avr109`) 6.3 is capable
of driving. `rig-pins.json`'s `forbidden_binaries` entry governs this rig's own **direct**
avrdude invocations (which `probe_board.py` and `judge_readback.py` correctly honored
throughout, using the pinned 8.1 binary exclusively) and does not conflict with PlatformIO's
internal per-env resolution — D-01's separation of the upload and judge code paths still
holds. **No override of PlatformIO's avrdude resolution is needed on any of the three
targets** — plan 09 should not spend a cycle forcing 8.1 that `uno328pb` already gets, and
plan 10 should not read a `leonardo` log's 6.3 as a forbidden-binary violation; it is neither
forbidden in that context nor incapable of the `avr109` protocol it is asked to drive.

## Bonus fact for plan 10 (leonardo): the 1200-baud touch is PlatformIO's job on the flash path

`~/.platformio/platforms/atmelavr/boards/leonardo.json`'s `upload` block carries
`"use_1200bps_touch": true` and `"wait_for_upload_port": true` alongside
`"protocol": "avr109"` — PlatformIO performs the 1200-baud touch and the port
re-enumeration wait **itself** as part of `pio run -t upload -e leonardo`. `tools/touch_1200.py`
(authored in wave 2) is therefore needed for the **direct-avrdude read-back** plan 10 runs
**outside** PlatformIO (the `judge_readback.py` step, which is a separate avrdude invocation
per D-01 and does not go through PlatformIO's upload machinery), not for the flash step itself.
This does not contradict `touch_1200.py`'s own standing note that real re-enumeration
behavior on this specific board is unproven until plan 10 actually runs it — it only narrows
which step needs the tool.
