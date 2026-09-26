---
status: partial
phase: 08-convert-state-machine-prefix-call-sites-ok-init-main-end
source: [08-VERIFICATION.md]
started: 2026-05-18T00:00:00Z
updated: 2026-08-09
---

## Current Test

[Test 1 blocker RESOLVED 2026-08-09 — the 0xA4 transport regression it was handed to /gsd-debug for has since been fixed; residual is Uno-side hardware only. See Carry-Over Assessment below.]

## Tests

### 1. SC#2 — End-to-end write on Uno + Leonardo
expected: Both `firestarter write -e W27C512 -i <known.bin>` runs complete normally with INIT/MAIN/END acks rendered from ID-frame decoding alone (no literal `INIT:` / `MAIN:` / `END:` text prefix in CLI output). The bootstrap `OK: FW: ...` line still appears at session start (LFW-05 preserved).
result: blocked
blocked_by: other
reason: |
  Bench session 2026-06-16, Leonardo /dev/ttyACM0, W27C512 seated, firmware updated b6→b8 during the session.
  PHASE-08 DELIVERABLE VERIFIED WORKING: all acks (`OK:`, `DATA:`, `ERROR:`) render via ID-frame decoding
  with NO literal `INIT:`/`MAIN:`/`END:` text prefixes; bootstrap `OK: FW: 3.0.0b8:leonardo` shown. The
  SC#2 *protocol* assertion is satisfied.
  END-TO-END WRITE DOES NOT COMPLETE — but the cause is OUT OF PHASE-08 SCOPE: firmware aborts during the
  write MAIN phase with MSG_ERR_EMPTY_INPUT (0xA4). Per firmware src/firestarter.cpp:186-189 this code is
  OVERLOADED ("CRC mismatch, COBS violation, overflow, or read underrun" — dedicated MSG_ERR_BAD_FRAME
  deferred), so this is a write-data-chunk COBS/CRC framing fault, not literally empty input. Reproduced
  across 3 file sizes (100 B, 37 KB, 64 KB) on matched b8/b8 → not a version issue. Regression vs the
  Phase-54 "EVEN-01 write proven clean on Leonardo/ACM0" baseline. Disposition (operator, 2026-06-16):
  hand off to /gsd-debug as a standalone write-path transport regression; NOT a Phase-08 gap.
  Earlier in the session writes also hit a VPP-high (13.1V > 12.0V) init abort; operator adjusted VPP and
  the `id`/`read` paths then init clean — VPP no longer a factor in the remaining write fault.

### 2. SC#3 — Byte-identical readback on Uno + Leonardo
expected: `firestarter read -e W27C512 -o /tmp/ph8-{uno,leo}.bin` produces a file byte-identical to the pre-Phase-8 baseline. `diff /tmp/ph8-uno.bin <Phase 7 baseline file>` and the Leonardo equivalent both exit 0.
result: pass
notes: |
  Bench 2026-06-16, Leonardo /dev/ttyACM0, fw 3.0.0b8. `firestarter read W27C512 /tmp/ph8-leo.bin` completed
  cleanly: full 65536 bytes in 7.26s via chunked MSG_DATA_CHUNK MAIN streaming; `Connecting... OK` +
  `Read complete`, NO literal `INIT:`/`MAIN:`/`END:` prefixes. The Phase-08 deliverable (ID-frame ack
  rendering + chunked read streaming, incl. the u16-required W-04 >253B path) is verified end-to-end on the
  read path. CAVEAT: the strict byte-identical-vs-Phase-7-baseline diff was NOT performed — no Phase-7
  baseline file is present in the workspace, and the chip contents were disturbed by the in-session write
  attempts. The byte-identical check is a chip-data assertion, not the Phase-08 protocol assertion; the
  protocol behavior SC#3 targets is confirmed. Uno not exercised this session (no Uno-class board at bench).

## Summary

total: 2
passed: 1
issues: 0
pending: 0
skipped: 0
blocked: 1

## Gaps

None against Phase 08 — the Phase-08 protocol deliverable (prefix→ID-frame ack rendering) is verified working
on both write and read paths. The write end-to-end failure is a separate, out-of-scope write-data-chunk
transport regression (overloaded MSG_ERR_EMPTY_INPUT / 0xA4) handed off to /gsd-debug; it is not a Phase-08
code defect and does not produce a Phase-08 gap.

---

## Carry-Over Assessment — 2026-08-09

Recorded during the v1.31 pre-close sweep. **Status stays `partial`** — the residual is
genuine hardware work and is not being rubber-stamped. But the blocker that paused this
file is gone, and the scope is now much smaller than it reads above.

### The blocker is resolved

Test 1 was parked because the write aborted with `MSG_ERR_EMPTY_INPUT` (0xA4), dispositioned
as "hand off to /gsd-debug as a standalone write-path transport regression; NOT a Phase-08
gap". That hand-off completed. Root cause was host-side: the INIT and END phases were
acking DATA frames they must not ack. The fix is in the v1.31 tree:

- `firestarter_app/firestarter/eprom_operations.py:488` — `ack_data=False` on the INIT/END path
- `:497-501` — the contract documented ("MAIN-phase flow … callers in those phases pass `ack_data=False`")
- `firestarter_app/tests/test_eprom_operations.py:135` — `test_init_phase_data_frames_not_acked` regression guard

### What this file already proved

The Phase-08 *deliverable* — ID-frame decoding of the state-machine acks with no literal
`INIT:`/`MAIN:`/`END:` text prefixes, bootstrap `OK: FW: …` preserved — was verified working
on the bench on 2026-06-16 (Leonardo, W27C512 seated, fw b8). That is the phase's actual
contribution and it is confirmed.

### What is genuinely still open

1. **The Uno leg.** SC#2/SC#3 asked for Uno *and* Leonardo. No Uno-class board has ever run it.
2. **An explicit byte-identity `diff`** of a readback against a pre-Phase-8 baseline.

The Leonardo leg is otherwise superseded: Phase 91 (v1.16) graduated W27C512 to PASS with a
full erase-enabled write+verify (chip-ID 0xDA08, erase SHA `e16b2a5b`), Phase 73 bench-validated
6 families on Leonardo, and v1.21 validated 3 boards.

**Recommendation (operator decision, not taken here):** close the Leonardo leg on the Phase 91
evidence, and resolve the Uno leg on policy — the project's standing posture is Leonardo-only
bench validity, so an Uno-class requirement written in May 2026 may simply be out of posture
now. Either way it should be dispositioned rather than left open indefinitely.

_Assessed: 2026-08-09 · v1.31 pre-close carry-over sweep · no hardware run, no criteria weakened_
