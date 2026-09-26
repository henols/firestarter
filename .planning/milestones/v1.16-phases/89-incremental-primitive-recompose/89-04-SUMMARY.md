---
phase: 89-incremental-primitive-recompose
plan: "04"
subsystem: firmware
tags: [refactor, primitive-extract, poll-readback, P5, primitives-module, PRIM-05, SAFE-01, SAFE-02, SAFE-03]
dependency_graph:
  requires: [89-03]
  provides: [P5-poll-readback-committed, poll-readback-primitive-extracted]
  affects:
    - firestarter/include/primitives.h
    - firestarter/src/proms/primitives.cpp
    - firestarter/src/proms/eeprom_28c.cpp
    - firestarter/src/proms/flash_type_4.cpp
tech_stack:
  added: []
  patterns: [refactor-under-test, per-step-gate, primitives-module, caller-owns-error-frame]
key_files:
  created: []
  modified:
    - firestarter/include/primitives.h
    - firestarter/src/proms/primitives.cpp
    - firestarter/src/proms/eeprom_28c.cpp
    - firestarter/src/proms/flash_type_4.cpp
decisions:
  - "P5 extracted as planned: poll_readback() shares only the bounded single-address poll kernel; each caller emits its own error frame to preserve per-site byte-order divergence (MSG_ERR_EEPROM_TIMEOUT addr-first vs MSG_ERR_FL4_VERIFY_TIMEOUT expected-first)"
  - "Signature chosen: bool poll_readback(handle, address, expected, max_iters, observed_out*) — returns bool, caller uses observed_out in its error frame on false; avoids frame-parameter complexity entirely"
  - "eprom.cpp verify_and_update_mask (whole-buffer bitmask, returns count, no timeout frame) left completely untouched — different algorithm, out of P5 scope per plan"
  - "Both golden traces (eeprom28c + flash4 write) pass byte-identical; zero-diff achieved. ROADMAP SC#4 third poll site (eprom verify_and_update_mask) recorded post-verification as an operator-accepted D-02 deferral (different algorithm)"
requirements-completed: [PRIM-05, PRIM-06, SAFE-01, SAFE-02, SAFE-03]

metrics:
  duration: "15min"
  completed: "2026-06-26"
  tasks_completed: 2
  files_modified: 4
---

# Phase 89 Plan 04: P5 poll_readback Primitive Extraction Summary

P5 (PRIM-05) extraction: shared `poll_readback()` primitive added to the
primitives module. Both single-address poll callers (`eeprom28c_wait_for_write`,
`flash4_wait_for_page_write`) call the shared kernel with their respective caps
(2000 / 1024); each caller retains its own error-frame emission with its
site-specific MSG id and `_b[]` byte order. `eprom.cpp verify_and_update_mask`
left untouched (different algorithm). Flash rose +2 B (25088 → 25090 B), within
the +16 B per-step gate. All gates green.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Extract poll_readback; leave eprom bitmask + outer loops intact | firestarter@abbbb5c | primitives.h, primitives.cpp, eeprom_28c.cpp, flash_type_4.cpp |
| 2 | Per-step P5 gate — full native suite + flash delta + frozen-world host gates + INV grep | (gate-run, no code change) | — |

## P5 Step Ledger (PRIM-06 input)

| Metric | Value |
|--------|-------|
| Prior step (P3 post) | 25088 B |
| Post-P5 Leonardo flash | 25090 B |
| Step delta | +2 B (within +16 B gate — D-01 PASS) |
| Flash % | 87.5% (unchanged from P3 — +2 B is subpercent) |
| Phase cumulative delta vs baseline (25654 B) | -564 B |

## Gate Results

| Gate | Result | Detail |
|------|--------|--------|
| Targeted golden traces (eeprom28c + flash4 + eprom write) | PASS | 32/32 test cases zero-diff |
| Full native suite (`pio test -e native`) | PASS | 102/102 tests green |
| Flash delta D-01 | PASS | +2 B (25088 → 25090 B, within +16 B gate) |
| Phase cumulative | PASS | 25090 < 25654 B baseline (-564 B) |
| `check_dispatch.py` | PASS | Exit 0, 0 dispatch regressions, 0 consistency violations (746 chips) |
| `diff_db.py` | PASS | Exit 0, 0 changed / 0 new / 0 missing (identity diff) |
| SAFE-06 host source change | PASS | host source unchanged; git -C firestarter_app diff --quiet exit 0 |
| INV-01..09 greppability (SAFE-02) | PASS | All 9 INV ids >= 3 files: INV-01=9, INV-02=3, INV-03=6, INV-04=4, INV-05=3, INV-06=3, INV-07=3, INV-08=3, INV-09=5 |

## Acceptance Criteria Verification

- `grep -c 'poll_readback' firestarter/include/primitives.h` = 2 (decl + doc comment) >= 1 — PASS
- `grep -c 'poll_readback' firestarter/src/proms/primitives.cpp` = 3 (def + comment) >= 1 — PASS
- `grep -c 'poll_readback' firestarter/src/proms/eeprom_28c.cpp` = 1 — PASS
- `grep -c 'poll_readback' firestarter/src/proms/flash_type_4.cpp` = 1 — PASS
- `grep -c 'poll_readback' firestarter/src/proms/eprom.cpp` = 0 (eprom bitmask path untouched) — PASS
- `grep -c 'verify_and_update_mask' firestarter/src/proms/eprom.cpp` = 2 (unchanged) — PASS
- eeprom28c error frame: addr-first `_b[5]` = `{addr>>16, addr>>8, addr, expected, observed}` — PASS
- flash4 error frame: expected-first `_b[5]` = `{expected, addr>>16, addr>>8, addr, observed}` — PASS
- 32/32 golden traces zero-diff (eeprom28c write+chip_id, flash4 write+chip_id, all 4 eprom write variants) — PASS

## Implementation Notes

### Signature choice

The plan offered two options: (a) pass the error frame as a parameter, or (b) share only
the inner read-compare leaf (returning observed back to the caller). Option (b) was chosen —
`bool poll_readback(handle, address, expected, max_iters, observed_out*)` — because it
completely avoids the frame-parameter complexity. The two error frames differ not only in
MSG id but also in `_b[]` byte order (eeprom28c = addr-first; flash4 = expected-first),
so any "shared frame" approach would require passing the byte order as data or a function
pointer. Returning `false + *observed_out` is the minimal surface: the kernel loop is
shared, the frame emission stays in the caller where the MUST-NOT-normalise byte order
is explicit.

### delayMicroseconds relocation

The `delayMicroseconds(10)` call moved from eeprom_28c.cpp and flash_type_4.cpp into
the shared kernel in primitives.cpp. `primitives.cpp` gained `#include <Arduino.h>` to
declare it. `eeprom_28c.cpp` retains `<Arduino.h>` for `delay()` (used in chip-id path);
`flash_type_4.cpp` retains it for `delay()` in `flash4_erase_execute`.

### eprom.cpp verify_and_update_mask

`verify_and_update_mask` is a whole-buffer bitmask updater returning a mismatch count,
with no timeout and no error frame. It is structurally different from the two single-address
bounded polls — it is NOT routed through `poll_readback`. The outer retry loop
`eprom_write_execute` (NUMBER_OF_RETRIES + pulse_delay ramp) is also entirely untouched.
`poll_readback` count in eprom.cpp = 0, machine-verified.

> **D-02 DEFERRAL (operator-accepted 2026-06-26, recorded post-verification).**
> ROADMAP §Phase 89 SC#4 names a *third* `poll_readback` site — the verify-readback half of
> `eprom_write_execute` (this `verify_and_update_mask`). It is intentionally NOT shared: routing
> a whole-buffer bitmask (returns count, no timeout, no error MSG) through the single-address
> bounded-poll kernel would change behavior, violating the behavior-preserving contract. The
> gsd-verifier flagged the missing deferral record (status `human_needed`); the operator confirmed
> the scope narrowing is correct and accepted it as a D-02 deferral rather than a defect. Treated
> as aspirational ROADMAP wording. PRIM-05 / Truth #4 accepted SATISFIED on this basis. No code
> change. See 89-VERIFICATION.md `operator_resolutions`.

### Phase-cumulative savings

| Step | Pre-B | Post-B | Delta |
|------|-------|--------|-------|
| Baseline (Phase 88) | — | 25654 | — |
| P7 (89-01) | 25654 | 25654 | 0 |
| P4 (89-02) | 25654 | 25490 | −164 |
| P3 (89-03) | 25490 | 25088 | −402 |
| P5 (89-04) | 25088 | 25090 | +2 |
| **Cumulative** | | **25090** | **−564 B** |

The +2 B rise from P5 is the call-overhead cost of an extra function call; the shared
kernel does not eliminate bytes from the AVR binary because the loop body is small and
AVR linker does not inline across TUs. The phase-cumulative −564 B vs baseline satisfies
D-01 and PRIM-06.

## Deviations from Plan

Plan executed exactly as written; P5 was extracted cleanly with zero-diff golden traces.
Post-verification, the ROADMAP SC#4 third poll site (eprom `verify_and_update_mask`) was
recorded as an operator-accepted D-02 deferral (see the `eprom.cpp verify_and_update_mask`
section above) — a documentation addition, not a code deviation.

## Known Stubs

None.

## Threat Flags

None. P5 extracted ONLY the bounded poll loop kernel; all VPP/regulator control, dispatch
routing, and host guards are untouched. T-89-01 mitigated: `poll_readback` contains no
regulator control. T-89-02 mitigated: D-08 `+500` threshold byte-identical and confirmed
present in primitives.cpp (vpp_check_window, from P3). `check_dispatch.py` confirmed 0
violations; `diff_db.py` confirmed identity diff (T-89-03 untouched).

## Self-Check: PASSED

- `firestarter/include/primitives.h` — modified (poll_readback declaration + doc block added)
- `firestarter/src/proms/primitives.cpp` — modified (poll_readback definition; #include <Arduino.h> added)
- `firestarter/src/proms/eeprom_28c.cpp` — modified (eeprom28c_wait_for_write calls poll_readback)
- `firestarter/src/proms/flash_type_4.cpp` — modified (flash4_wait_for_page_write calls poll_readback; #include "primitives.h" added)
- Commit `abbbb5c` exists in firestarter submodule on v1.16 branch
- All 102 native tests green
- Flash delta = +2 B (25088 → 25090 B, 87.5%)
- Both host gates exit 0
- INV-01..09 all >= 3 files
- eprom.cpp poll_readback count = 0; verify_and_update_mask count = 2 (unchanged)
