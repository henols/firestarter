---
phase: 89-incremental-primitive-recompose
plan: "03"
subsystem: firmware
tags: [refactor, primitive-extract, vpp-gate, P3, primitives-module, PRIM-04, SAFE-04]
dependency_graph:
  requires: [89-02]
  provides: [P3-vpp-check-window-committed, vpp-gate-primitive-extracted]
  affects:
    - firestarter/include/primitives.h
    - firestarter/src/proms/primitives.cpp
    - firestarter/src/proms/eprom.cpp
    - firestarter/src/proms/flash_intel.cpp
tech_stack:
  added: []
  patterns: [refactor-under-test, delete-not-merge, per-step-gate, primitives-module]
key_files:
  created: []
  modified:
    - firestarter/include/primitives.h
    - firestarter/src/proms/primitives.cpp
    - firestarter/src/proms/eprom.cpp
    - firestarter/src/proms/flash_intel.cpp
decisions:
  - "P3 executed as planned: vpp_check_window lifts byte-identical window-compare body from both VPP handlers; delay(100) kept handler-local in eprom_check_vpp (flash_intel caller already delayed 500ms)"
  - "D-08 threshold preserved byte-identical: vpp_mv > (uint32_t)handle->vpp_mv + 500 now lives in primitives.cpp"
  - "D-06 respected: protocol == 0x0B / FLAG_VPE_AS_VPP regulator routing stays in eprom_check_vpp; no regulator control in vpp_check_window (REGULATOR count in primitives.cpp == 0)"
  - "REV0 guard kept handler-local in both handlers per Open Q2 (first cut)"
  - "Pre-existing firestarter_app .gitignore diff noted — same as P7/P4, not caused by P3, not a source change"
requirements-completed: [PRIM-04, PRIM-06, SAFE-01, SAFE-02, SAFE-03]

metrics:
  duration: "18min"
  completed: "2026-06-26"
  tasks_completed: 2
  files_modified: 4
---

# Phase 89 Plan 03: P3 vpp_check_window Primitive Extraction Summary

P3 (PRIM-04) extraction: shared `vpp_check_window()` primitive added to the
primitives module. Both VPP handlers (`eprom_check_vpp`, `flash_intel_check_vpp`)
call the shared body; each keeps its own regulator routing, settle delay, REV0
guard, and trailing clear. Leonardo flash shrank by 402 B (25490 → 25088 B),
the biggest per-step saving in the phase. All gates green; SAFE-04 intact.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Extract vpp_check_window; keep regulator routing + REV0 guard + clear handler-local | firestarter@a52fd0a | primitives.h, primitives.cpp, eprom.cpp, flash_intel.cpp |
| 2 | Per-step P3 gate — full native suite + flash delta + frozen-world host gates + INV grep + D-08 posture | (gate-run, no code change) | — |

## P3 Step Ledger (PRIM-06 input)

| Metric | Value |
|--------|-------|
| Prior step (P4 post) | 25490 B |
| Post-P3 Leonardo flash | 25088 B |
| Step delta | -402 B (well within +16 B gate — D-01 PASS) |
| Flash % | 87.5% (down from 88.9% after P4) |
| Phase cumulative delta vs baseline (25654 B) | -566 B |

## Gate Results

| Gate | Result | Detail |
|------|--------|--------|
| Targeted golden traces (0x07/0x08/0x0B write + flash_intel write) | PASS | 21/21 test cases zero-diff |
| INV-01/INV-03 bit-level asserts | PASS | Both green — 0x100 VPE_DROP LOW-BYTE-invisible guard confirmed |
| Full native suite (`pio test -e native`) | PASS | 102/102 tests green |
| Flash delta D-01 | PASS | -402 B (25490 → 25088 B, expected net-decrease, biggest step saving) |
| `check_dispatch.py` | PASS | Exit 0, 0 dispatch regressions, 0 consistency violations (746 chips) |
| `diff_db.py` | PASS | Exit 0, 0 changed / 0 new / 0 missing (identity diff) |
| SAFE-06 host source change | PASS (pre-existing .gitignore note) | Only change in firestarter_app is pre-existing `.gitignore` annotation — same as P7/P4, not a source file, not caused by P3 |
| INV-01..09 greppability (SAFE-02) | PASS | All 9 INV ids hit >= 3 files: INV-01=9, INV-02=3, INV-03=6, INV-04=4, INV-05=3, INV-06=3, INV-07=3, INV-08=3, INV-09=5 |
| D-08 over-voltage check (SAFE-04) | PASS | `vpp_mv > (uint32_t)handle->vpp_mv + 500` HIGH check present in primitives.cpp:66 (threshold + FORCE/ERROR semantics byte-identical; now owned by the shared primitive) |

## Acceptance Criteria Verification

- `grep -c 'vpp_check_window' firestarter/include/primitives.h` = 2 (declared + doc comment) >= 1 — PASS
- `grep -c 'void vpp_check_window' firestarter/src/proms/primitives.cpp` = 1 (defined) — PASS
- `grep -c 'vpp_check_window' firestarter/src/proms/eprom.cpp` = 1 (eprom handler calls shared check) — PASS
- `grep -c 'vpp_check_window' firestarter/src/proms/flash_intel.cpp` = 1 (flash_intel handler calls shared check) — PASS
- `grep -c 'protocol == 0x0B' firestarter/src/proms/eprom.cpp` = 2 (D-06 keying NOT moved into primitives.cpp) — PASS
- `grep -c 'REGULATOR' firestarter/src/proms/primitives.cpp` = 0 (no regulator control inside shared primitive) — PASS
- All 21 write golden traces byte-identical AND INV-01/INV-03 bit asserts green — PASS (zero-diff, no D-02 deferral needed)

## Implementation Notes

### delay() divergence resolution

`eprom_check_vpp` had `delay(100)` immediately before the shared window body;
`flash_intel_check_vpp` had no delay (caller `flash_intel_write_init` already
delayed 500ms before entering the check). Per the plan's explicit rule: "if delay
placement diverges, keep delay handler-local." The `delay(100)` was left in
`eprom_check_vpp` before the `vpp_check_window(handle)` call. This means
`flash_intel_check_vpp` does NOT gain an extra delay call — correct behavior
preserved.

Since `delay()` is stubbed as a no-op in the native test harness, this divergence
has no effect on golden trace byte-equality. The golden traces record only bus
writes (register, data pairs), never delay calls.

### D-08 threshold location

The `vpp_mv > (uint32_t)handle->vpp_mv + 500` threshold now lives in
`primitives.cpp:66` (inside `vpp_check_window`). The FORCE/ERROR semantics are
byte-identical. This is the correct outcome: the threshold is now in one place
rather than duplicated in two handlers, and it remains protected by the golden
traces and INV asserts.

### REV0 guard stays handler-local

Both `eprom_check_vpp` and `flash_intel_check_vpp` retain their own REV0 guard
(early return on REVISION_0 hardware). Per Open Q2 from the RESEARCH doc, the
first cut keeps the guard handler-local. This was the correct call — the golden
traces do not test the REV0 path, and folding the guard in would add a parameter
or conditional to `vpp_check_window` without a corresponding flash saving.

## Deviations from Plan

None — plan executed exactly as written. The pre-existing `.gitignore` change
in `firestarter_app` was noted (not caused by P3; predates this plan; not a
source-code change; same as P7/P4 SUMMARY notation).

## Known Stubs

None.

## Threat Flags

None. P3 extracted ONLY the read+window+pack+FORCE body; all regulator routing,
REV0 guard, and trailing clear stayed handler-local. T-89-01 mitigated:
`vpp_check_window` contains no regulator control (`REGULATOR` count = 0, machine-
verified). T-89-02 mitigated: D-08 `+500` threshold byte-identical and confirmed
present in primitives.cpp. `check_dispatch.py` confirmed 0 violations; `diff_db.py`
confirmed identity diff (T-89-03 untouched).

## Self-Check: PASSED

- `firestarter/include/primitives.h` — modified (vpp_check_window declaration added)
- `firestarter/src/proms/primitives.cpp` — modified (vpp_check_window definition added; rurp_shield.h include added)
- `firestarter/src/proms/eprom.cpp` — modified (eprom_check_vpp calls vpp_check_window)
- `firestarter/src/proms/flash_intel.cpp` — modified (flash_intel_check_vpp calls vpp_check_window)
- Commit `a52fd0a` exists in firestarter submodule on v1.16 branch
- All 102 native tests green
- Flash delta = -402 B (25490 → 25088 B, 87.5%)
- Both host gates exit 0
- INV-01..09 all >= 3 files
- D-08 over-voltage check confirmed present + byte-identical threshold
