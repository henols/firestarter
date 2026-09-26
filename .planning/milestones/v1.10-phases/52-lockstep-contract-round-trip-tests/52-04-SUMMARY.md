---
phase: 52-lockstep-contract-round-trip-tests
plan: "04"
subsystem: merge-gate
tags: [golden-vectors, byte-identity, drift-gate, lockstep, D-09, LOCK-01, LOCK-02]
dependency_graph:
  requires: [52-01, 52-02, 52-03]
  provides: [cross-repo-byte-identity-proof, dual-repo-full-suite-green, lockstep-contract-closed]
  affects: []
tech_stack:
  added: []
  patterns: [D-09 byte-identity assertion at merge gate, dual-repo codegen drift gate, dual-repo full-suite green gate]
key_files:
  created: []
  modified: []
decisions:
  - "Verification-only plan — no production files modified; all assertions pass cleanly"
  - "D-09 cross-repo catalog byte-identity confirmed: both diffs empty (frame-vectors.toml + codegen_vectors.py)"
  - "Both per-repo codegen drift gates clean: regenerating frame_vectors.h and frame_vectors.py leaves git diff --exit-code clean"
  - "Firmware full native suite: 39/39 tests passed across 7 suites (0 failures)"
  - "Host full suite: 422/422 tests passed at 71.28% coverage (above 70% floor)"
metrics:
  duration: 4m
  completed: "2026-06-02"
  tasks: 2
  files: 0
---

# Phase 52 Plan 04: Merge Gate — Lockstep Contract Proof Summary

Verification-only merge gate that proves the cross-repo COBS framing contract holds end-to-end. Both vendored catalog/codegen copies are byte-identical (D-09 pinned by explicit diff), both per-repo codegen drift gates are clean, and both full test suites are green. LOCK-01 and LOCK-02 are satisfied locally; per-repo CI on `v1.10-serial-transport-hardening` is the final D-08 confirmation.

## Tasks Completed

| Task | Name | Artifact |
|------|------|----------|
| 1 | Assert cross-repo byte-identity + both codegen drift gates clean | Gate evidence recorded in SUMMARY |
| 2 | Dual-repo full-suite green gate | Gate evidence recorded in SUMMARY |

## Task 1: Cross-Repo Byte-Identity + Codegen Drift Gate Results

### D-09 Byte-Identity (both diffs empty)

```
diff firestarter/tools/catalog/frame-vectors.toml firestarter_app/tools/catalog/frame-vectors.toml
# exit code: 0 (empty — byte-identical)

diff firestarter/tools/catalog/codegen_vectors.py firestarter_app/tools/catalog/codegen_vectors.py
# exit code: 0 (empty — byte-identical)
```

Both vendored copies are byte-identical. The D-09 accepted risk is explicitly pinned: the "shared" golden vectors are provably shared.

### Codegen Drift Gates (both clean)

**Firmware (`firestarter/`):**
```
python3 tools/catalog/codegen_vectors.py --catalog tools/catalog/frame-vectors.toml --target include/frame_vectors.h --language cpp-vectors
# OK: wrote include/frame_vectors.h (cpp-vectors, 12 vectors).
git diff --exit-code include/frame_vectors.h
# exit code: 0 (clean — no drift)
```

**Host (`firestarter_app/`):**
```
python3 tools/catalog/codegen_vectors.py --catalog tools/catalog/frame-vectors.toml --target firestarter/frame_vectors.py --language python-vectors
# OK: wrote firestarter/frame_vectors.py (python-vectors, 12 vectors).
git diff --exit-code firestarter/frame_vectors.py
# exit code: 0 (clean — no drift)
```

Both vector artifacts are drift-free. The catalog can be re-run without producing any change.

## Task 2: Dual-Repo Full-Suite Green Gate Results

### Firmware Full Native Suite (`pio test -e native`)

**Result: 39/39 tests PASSED, 0 failures**

```
=================================== SUMMARY ===================================
Environment    Test                             Status    Duration
-------------  -------------------------------  --------  ------------
native         native/avr/test_dispatch         PASSED    00:00:02.045
native         native/avr/test_read_timing      PASSED    00:00:02.149
native         native/avr/test_cobs_cmd_frame   PASSED    00:00:02.061
native         native/avr/test_cobs_data_frame  PASSED    00:00:00.674
native         native/avr/test_frame_vectors    PASSED    00:00:00.670
native         native/avr/test_data_input       PASSED    00:00:02.240
native         native/avr/test_messages         PASSED    00:00:02.064
================= 39 test cases: 39 succeeded in 00:00:11.903 =================
```

The `test_frame_vectors` suite (new from Plan 02) plus the unperturbed existing `test_cobs_cmd_frame`, `test_cobs_data_frame`, `test_dispatch`, `test_read_timing`, `test_data_input`, and `test_messages` suites all pass.

### Host Full Suite (`pytest tests/ --cov=firestarter --cov-fail-under=70`)

**Result: 422/422 tests PASSED, coverage 71.28% (above 70% floor)**

```
422 passed in 11.61s
Required test coverage of 70% reached. Total coverage: 71.28%
```

The `test_frame_vectors.py` suite (new from Plan 03) plus all prior suites pass. Coverage 71.28% is above the 70% floor enforced by CI.

### Note on D-08 ("CI green across both repos")

This local gate is the **pre-CI confirmation**. The final D-08 condition — "CI green across both repos" — is satisfied by the two sub-repo CI pipelines running on `v1.10-serial-transport-hardening` after the paired commits land. The per-repo CI runs the same test commands (drift gate + full suite) as this local gate; local green is a necessary and sufficient precondition for CI green absent any environment-specific flakiness.

## Acceptance Criteria Verification

- `diff firestarter/tools/catalog/frame-vectors.toml firestarter_app/tools/catalog/frame-vectors.toml` is empty (D-09) — **PASS**
- `diff firestarter/tools/catalog/codegen_vectors.py firestarter_app/tools/catalog/codegen_vectors.py` is empty (D-09) — **PASS**
- Regenerating `include/frame_vectors.h` leaves `git diff --exit-code` clean — **PASS**
- Regenerating `firestarter/frame_vectors.py` leaves `git diff --exit-code` clean — **PASS**
- `pio test -e native` (firmware) reports 0 failures across all 7 registered suites — **PASS** (39/39)
- `pytest tests/ --cov=firestarter --cov-fail-under=70` (host) passes at >=70% floor — **PASS** (71.28%)
- SUMMARY records byte-identity diffs and drift-gate results explicitly — **PASS** (this section)
- SUMMARY records both full-suite results (counts + coverage) and notes per-repo CI as final D-08 confirmation — **PASS** (this section)

## Deviations from Plan

None — plan executed exactly as written. All verification assertions passed on the first run. No reconciliation was required (both diffs were empty, both drift gates were clean, both suites were green).

## Known Stubs

None — this is a verification-only plan; no production files were modified or stubbed.

## Threat Flags

No new production network endpoints, auth paths, or trust-boundary schema changes introduced. This plan modifies no files and only asserts invariants already established by Plans 01/02/03.

T-52-02 (catalog drift, D-09): **mitigated** — explicit byte-identity diff confirmed empty at this gate.
T-52-10 (stale generated artifact): **mitigated** — both codegen drift gates clean.
T-52-11 (new vector regressing existing suites): **mitigated** — full-suite runs in both repos confirmed green.

## Self-Check: PASSED

No files were created or modified by this plan. All assertions are confirmed by real command output above.

Commits: This is a verification-only plan; no task commits were created (nothing to commit — no files changed). The final metadata commit captures this SUMMARY plus STATE.md and ROADMAP.md updates.
