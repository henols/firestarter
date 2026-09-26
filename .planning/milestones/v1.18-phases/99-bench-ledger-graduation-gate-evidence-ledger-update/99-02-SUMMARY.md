---
phase: 99-bench-ledger-graduation-gate-evidence-ledger-update
plan: 02
subsystem: testing
tags: [bench-prep, evidence-gate, anti-fabrication, sha256]

# Dependency graph
requires:
  - phase: 99-bench-ledger-graduation-gate-evidence-ledger-update
    plan: 01
    provides: check_ledger.py D-09 extension recognizing a v1.18-native 0x08 graduation
provides:
  - "deterministic 262144-byte AM27C020 write payload (imgA.bin, gen_test_image seed 1) with recorded self-verifying SHA"
  - "annotated SHA256SUMS.txt header carrying firmware-commit + bench-discipline provenance ahead of the live spend"
  - "check_graduation.py: Phase-99 EVIDENCE-cell completeness + SHA-self-consistency anti-fabrication gate"
affects: [99-03, 99-04]

# Tech tracking
tech-stack:
  added: []
  patterns: ["EVIDENCE-cell completeness gate keyed on an `op` prefix filter (phase99*) to disambiguate from the Phase-97 pre-fix cell, mirroring check_signature.py's shape"]

key-files:
  created:
    - .planning/v1.18/bench/AM27C020-graduation/imgA.bin
    - .planning/v1.18/bench/AM27C020-graduation/SHA256SUMS.txt
    - .planning/v1.18/bench/check_graduation.py
  modified: []

key-decisions:
  - "check_graduation.py filters on `op` starting with \"phase99\" (not the Phase-97 `tier0_microprobe+rca01` cell) so it can never be satisfied by the pre-fix failure-signature cell that check_signature.py already owns."
  - "Branch logic keyed off the cell's own `verdict` string (PASS*/DEFER*) rather than a separate flag: PASS requires write_image_sha256 == readback_sha256 (self-consistency oracle); DEFER requires bits_flipped + post_read_sha256 (the failing-vs-fixed differential) and explicitly does NOT require write==readback, since a deferred/OTP chip has no readback to match."
  - "SHA256SUMS.txt records the firmware submodule COMMIT (35706c2), not the version string, per the project's standing version-string caveat (both the pre-fix and Phase-98 fix builds report the same 3.0.0b10 version)."
  - "Readback SHA line intentionally omitted from SHA256SUMS.txt — appending it is plan 99-03's job (the bench session); fabricating it here would violate the anti-fabrication constraint this whole plan exists to enforce."

requirements-completed: [BENCH-02]

# Metrics
duration: 15min
completed: 2026-07-01
---

# Phase 99 Plan 02: Bench-Independent Graduation Prep Summary

**Staged the deterministic AM27C020 write image, its annotated SHA256SUMS provenance header, and a Phase-99 anti-fabrication EVIDENCE gate (check_graduation.py) so the operator bench session (99-03) is a pure execute-and-record step.**

## Performance

- **Duration:** 15 min
- **Started:** 2026-07-01T10:57:xx Z (immediately following 99-01)
- **Completed:** 2026-07-01T11:02:58Z
- **Tasks:** 2
- **Files created:** 3

## Accomplishments
- Generated `imgA.bin`: exactly 262144 bytes via `firestarter_app/tools/gen_test_image.py 262144 1` (seed 1 = image A convention); SHA `b2fc5cbfcc25be3daa0e8e88e6977c7da6164a6fcf9c577ca943da940a133457`.
- Wrote `AM27C020-graduation/SHA256SUMS.txt` with an annotated comment header (firmware commit `35706c2`, controller `leonardo`, shield `Rev 2.0`, method, and a `PENDING BENCH` verdict placeholder) followed by the plain `sha256sum imgA.bin` line; self-verifies via `sha256sum -c`.
- Built `check_graduation.py` mirroring `check_signature.py`'s shape: loads `EVIDENCE.json`, filters the AM27C020 cell whose `op` starts with `phase99` (never the Phase-97 `tier0_microprobe+rca01` cell), and branches PASS (write==readback self-consistency) vs DEFER (bits_flipped + post_read_sha256 differential).
- Confirmed the gate correctly reports the expected pre-bench state: `MISSING: no phase99 AM27C020 cell yet`, exit 1, against the real (unmodified) `EVIDENCE.json`.
- Validated all branch logic (PASS-consistent, PASS-mismatch, PASS-missing-field, DEFER-ok, DEFER-missing-field, common-field-TBD, unknown-verdict, phase97-cell-must-be-ignored) against 9 synthetic fixture cells swapped into a throwaway copy of `EVIDENCE.json` and restored afterward — the real file was never left mutated (`git status` clean throughout).
- `ruff check` + `ruff format --check` both pass on `check_graduation.py`.

## Task Commits

Each task was committed atomically:

1. **Task 1: Generate the deterministic write image + annotated SHA256SUMS header** - `b210619` (feat)
2. **Task 2: Add the Phase-99 EVIDENCE graduation gate (check_graduation.py)** - `a73c87c` (feat)

**Plan metadata:** committed separately after this summary via the final-commit step.

## Files Created/Modified
- `.planning/v1.18/bench/AM27C020-graduation/imgA.bin` - new; 262144-byte deterministic payload, seed 1.
- `.planning/v1.18/bench/AM27C020-graduation/SHA256SUMS.txt` - new; annotated header + self-verifying `imgA.bin` SHA line; no readback line yet (bench appends it).
- `.planning/v1.18/bench/check_graduation.py` - new; anti-fabrication EVIDENCE-cell gate, ruff-clean, exit-code contract (0 pass / 1 gap) matching `check_signature.py`.

## Decisions Made
- Chose the `op`-prefix filter (`phase99*`) over overwriting or extending the Phase-97 cell in place, so `check_signature.py` (which still reads the `tier0_microprobe+rca01` cell) is never affected by this plan.
- Kept the script a plain stdlib script with no argv, matching the sibling gate's contract exactly.
- Referenced SHAs only via cell fields inside `check_graduation.py` — no raw 64-hex literal appears in the script body (verified by grep).

## Deviations from Plan

None — plan executed exactly as written. Both tasks' verification and acceptance criteria were met on the first attempt with no debugging iteration.

## Known Stubs

None. `SHA256SUMS.txt`'s `PENDING BENCH` verdict placeholder and the omitted readback SHA line are explicitly specified as the correct pre-bench state by the plan (not stubs to resolve in this plan) — plan 99-03 fills them in from real bench data.

## Threat Flags

None. This plan's threat model (`T-99-02a`, `T-99-04a`, `T-99-SC`) is fully addressed by the artifacts produced: `check_graduation.py` is exactly the anti-fabrication mitigation for `T-99-02a`; the SHA256SUMS commit-not-version-string header is the mitigation for `T-99-04a`; no package installs occurred (`T-99-SC` not applicable). No new security-relevant surface was introduced beyond what the threat model already anticipated.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required. This plan is bench-independent by design; no hardware, serial connection, or operator action was needed or attempted.

## Next Phase Readiness
- Plan 99-03 (operator-gated bench session) can now run the manual `write -b` → `read`/`verify` → SHA-compare sequence against `imgA.bin`, append the readback SHA line to `SHA256SUMS.txt`, and record the real bench-discipline readings.
- Plan 99-04 (EVIDENCE + PROTOCOL-LEDGER update) will author the `phase99*` AM27C020 cell that `check_graduation.py` is now waiting for; once written, `check_graduation.py` will branch correctly to PASS or DEFER based on the real `verdict` string and real SHA fields.
- No blockers. Nothing in this plan touched hardware, voltage, or fabricated any bench result (SAFE-01 and the anti-fabrication constraint both held throughout).

---
*Phase: 99-bench-ledger-graduation-gate-evidence-ledger-update*
*Completed: 2026-07-01*

## Self-Check: PASSED

- FOUND: .planning/v1.18/bench/AM27C020-graduation/imgA.bin
- FOUND: .planning/v1.18/bench/AM27C020-graduation/SHA256SUMS.txt
- FOUND: .planning/v1.18/bench/check_graduation.py
- FOUND: .planning/phases/99-bench-ledger-graduation-gate-evidence-ledger-update/99-02-SUMMARY.md
- FOUND commit: b210619 (feat, Task 1)
- FOUND commit: a73c87c (feat, Task 2)
- FOUND commit: aa9ff36 (docs, summary)
