# Phase 50 — Post-Change Uno RAM Report (FRAME-03 Evidence)

**Date:** 2026-06-01
**Plan:** 50-04 (Integration gates — RAM proof + dual-repo full-suite green gate)
**Status:** PASSED — RAM gate exits 0, both suites green

---

## Summary

The post-change Uno RAM figures are **identical to the Phase-49 baseline**: 1503 bytes used /
2048 bytes total → **545 bytes free**. The FRAME-03 requirement (no second ~512 B encode buffer;
free RAM >= ~545 B ceiling) is satisfied. No second buffer was materialized.

---

## RAM Figures — Post-Change vs Phase-49 Baseline

| Metric          | Phase-49 Baseline (2026-06-01) | Post-Change (Plan 02+03) | Delta   |
|-----------------|-------------------------------|--------------------------|---------|
| RAM used        | 1503 B                        | 1503 B                   | 0 B     |
| RAM total       | 2048 B                        | 2048 B                   | —       |
| **RAM free**    | **545 B**                     | **545 B**                | **0 B** |
| RAM used %      | 73.4%                         | 73.4%                    | 0%      |
| Flash used      | 22492 B / 32256 B (69.7%)     | 22812 B / 32256 B (70.7%) | +320 B |

The RAM figure is unchanged from the baseline. The COBS encoder/decoder is streaming — no second
~512 B static buffer was added to the firmware. The COBS state variables (write cursor, block
remaining, 254-run flag) are ~5-6 B of stack-allocated locals in `rurp_communication_read_data`
and `rurp_communication_write`, not a second heap/BSS buffer. This is consistent with the
RESEARCH.md §Pattern 2 / §Pattern 1 analysis (ADR §4.3 decode-in-place; streaming encode to
`SERIAL_PORT.write()` directly).

**No second ~512 B static buffer was materialized.** The ~6 B COBS state is stack-local, not a
BSS allocation. The free-RAM ceiling of ~545 B (the Phase-49 binding constraint from
`.planning/v1.10-FRAMING-DECISION.md §4.5` and ADR D-04) is preserved with zero margin consumed.

---

## Gate Results

| Gate                        | Command                              | Result  | Detail                              |
|-----------------------------|--------------------------------------|---------|-------------------------------------|
| Uno RAM ceiling (FRAME-03)  | `bash firestarter/scripts/check_uno_ram.sh` | **PASSED** | free=545 B >= floor=545 B      |
| Firmware native suite       | `pio test -e native`                 | **PASSED** | 28/28 test cases, 5 suites (10 s)   |
| Host pytest suite           | `python -m pytest --cov-fail-under=70` | **PASSED** | 408/408 tests, 29 snapshots (23 s)  |

---

## Firmware Test Suite Detail

```
Environment    Test                             Status    Duration
-------------  -------------------------------  --------  ------------
native         native/avr/test_dispatch         PASSED    00:00:01.979
native         native/avr/test_read_timing      PASSED    00:00:01.962
native         native/avr/test_cobs_data_frame  PASSED    00:00:02.020
native         native/avr/test_data_input       PASSED    00:00:02.042
native         native/avr/test_messages         PASSED    00:00:02.007
================== 28 test cases: 28 succeeded in 00:00:10.010 ================
```

Suites include:
- `test_cobs_data_frame` — Phase 50 COBS encode/decode round-trip, resync, full-buffer, CRC8 (new, covers FRAME-01/02/04/CRC-01)
- `test_messages` — log/telemetry frame + CRC8 polynomial smoke (existing, covers Framing-4 UNCHANGED)
- `test_dispatch`, `test_read_timing`, `test_data_input` — existing dispatch + timing suites (regression-clean)

---

## Flash Growth Note

Flash increased by 320 B (22492 → 22812 B; 69.7% → 70.7%). This is the COBS encode/decode
function code added to `rurp_serial_utils.cpp`. Flash is not a binding constraint for this phase
(RAM is the binding constraint per FRAME-03 / D-04); the 70.7% usage is well within the
`[env:uno]` ceiling and does not represent a regression.

---

## Leonardo DATA_BUFFER_SIZE — Operator Watch-Item

The `[env:leonardo]` build currently pins `DATA_BUFFER_SIZE=512` as a TEMP A/B-test override
(comment in `platformio.ini:64`: "TEMP: 512 to match Uno for buffer-size A/B test (was 1024)").

FRAME-04 nominally specifies "1024 B (Leonardo) transfers complete through the new framing
transparently." COBS is size-agnostic — it frames any N-byte payload identically, so the COBS
framing code is correct regardless of this define. The 1024 B framing path is exercised by the
`test_cobs_data_frame` suite (which tests at parameterized payload sizes including full-buffer
cases) and is independent of the shipped Leonardo define.

The disposition of this pin — **restore to 1024** OR **keep as deliberate A/B pin** — is an
operator decision surfaced as Task 2 (checkpoint:decision) in Plan 50-04. It is not resolved in
this report; see Task 2 for context and options.

---

## FRAME-03 Attestation

This report attests:

1. **RAM gate passes:** `bash firestarter/scripts/check_uno_ram.sh` exits 0 — free RAM = 545 B,
   at or above the 545 B floor established by the Phase-49 baseline.

2. **No second ~512 B static buffer was materialized.** The Plan-02 firmware rewrite of
   `rurp_communication_read_data` uses decode-in-place into the existing `data_buffer[512]`
   (write cursor never overtakes read cursor — a mathematical COBS property). The Plan-02 rewrite
   of `rurp_communication_write` streams COBS-encoded bytes directly to `SERIAL_PORT.write()`
   without an intermediate buffer. Both functions add only ~5-6 bytes of stack-local COBS state
   (block_remaining, out-cursor, CRC accumulator), not a second BSS allocation.

3. **Dual-repo full-suite green:** firmware `pio test -e native` (28/28) and host
   `python -m pytest --cov-fail-under=70` (408/408) both pass in this post-change state.

4. **Phase-51 lockstep constraint noted (D-03):** This is a breaking beta upgrade — a mixed
   host/firmware pair (one updated, one not) will fail to communicate. No interim version/interop
   guard is added in Phase 50 (accepted per D-03); the version/handshake guard lands in Phase 51.
   The breaking nature is accepted and documented here per plan objective.

---

## Leonardo DATA_BUFFER_SIZE A/B-Pin Disposition (FRAME-04 — Task 2)

**Operator decision (2026-06-01): keep-512-documented**

The `[env:leonardo]` build pin `DATA_BUFFER_SIZE=512` (line 65 of `firestarter/platformio.ini`,
comment: "TEMP: 512 to match Uno for buffer-size A/B test (was 1024)") is **deliberately retained
unchanged** as an explicit A/B-test condition, not silently shipped.

### Rationale

The 512 B pin was set to match the Uno buffer size for a side-by-side comparison tied to the v1.9
read-bug investigation (paused at Phase 44; resumes at Phase 45 after v1.10 completes). Restoring
1024 would end that A/B condition prematurely — before the v1.9 RCA has used it. The operator
decision preserves the v1.9 A/B state.

### FRAME-04 Satisfaction

FRAME-04 requires "512 B (Uno) and 1024 B (Leonardo) transfers complete through the new framing
transparently." COBS is **size-agnostic** — the framing code treats any N-byte payload identically;
there is no special case for 512 vs 1024. The `test_cobs_data_frame` suite (Phase 50 Plan 01/02/03)
includes parameterized round-trip tests at multiple payload sizes — including full-buffer cases that
cover the 1024 B path — and all 28/28 test cases pass. FRAME-04's 1024 B Leonardo path is
**test-validated** by those size-agnostic tests independent of the shipped Leonardo define.

The shipped Leonardo build running at `DATA_BUFFER_SIZE=512` does not represent a defect in the
framing layer; it represents a deliberate A/B-test condition that the operator owns.

### State

- `firestarter/platformio.ini` `[env:leonardo]`: `DATA_BUFFER_SIZE=512` — **UNCHANGED**
- No firmware commit was made for Task 2 (disposition is documentation-only)
- The A/B pin will be revisited when the v1.9 read-bug RCA resumes (Phase 45+)
- Nothing is promoted to stable without operator authorization (per D-03 / D-17v2 carry-forward)
