---
phase: 50-data-path-framing-layer-automatic-resync-dual-repo-lockstep
plan: 04
subsystem: firmware, testing
tags: [cobs, framing, serial, platformio, dual-repo, ram, arduino, leonardo]

# Dependency graph
requires:
  - phase: 50-data-path-framing-layer-automatic-resync-dual-repo-lockstep
    provides: "Plan 02 COBS firmware rewrite (rurp_serial_utils.cpp) + Plan 03 host pytest suite"
provides:
  - "FRAME-03 post-change RAM attestation: 545 B free, no second ~512 B buffer, RAM gate exits 0"
  - "Dual-repo full-suite green gate: firmware 28/28 native + host 408/408 pytest held"
  - "Leonardo DATA_BUFFER_SIZE=512 A/B-pin disposition: deliberate keep-512-documented (operator-decided 2026-06-01)"
  - "50-RAM-REPORT.md as binding FRAME-03 evidence artifact"
affects:
  - phase-51 (version/handshake guard builds on this lockstep gate)
  - v1.9-rca-phase-45 (Leonardo 512 B A/B pin preserved for that investigation)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "COBS streaming encode (no second buffer): FRAME-03 RAM proof pattern — compare post-change vs baseline; zero delta = streaming confirmed"
    - "Leonardo buffer A/B-pin: deliberate 512 B override retained for cross-phase RCA investigation; COBS size-agnostic so framing correctness is test-validated independent of shipped define"

key-files:
  created:
    - ".planning/phases/50-data-path-framing-layer-automatic-resync-dual-repo-lockstep/50-RAM-REPORT.md"
    - ".planning/phases/50-data-path-framing-layer-automatic-resync-dual-repo-lockstep/50-04-SUMMARY.md"
  modified:
    - ".planning/phases/50-data-path-framing-layer-automatic-resync-dual-repo-lockstep/50-RAM-REPORT.md (Task 2 disposition section appended)"

key-decisions:
  - "keep-512-documented: Leonardo DATA_BUFFER_SIZE=512 A/B pin retained unchanged (operator decision 2026-06-01) — preserves v1.9 RCA cross-phase A/B condition; FRAME-04 1024 B path is test-validated by size-agnostic COBS round-trip tests"
  - "FRAME-03 satisfied: post-change Uno RAM identical to Phase-49 baseline (545 B free, 0 B delta) — streaming COBS adds only ~6 B stack-local state, no second BSS buffer"
  - "D-03 breaking-upgrade accepted: no mixed-version interop guard in Phase 50; version/handshake guard deferred to Phase 51"

patterns-established:
  - "RAM gate pattern: run check_uno_ram.sh post-change and tabulate vs baseline; zero delta proves streaming encode"
  - "A/B-pin disposition: operator-owned cross-phase conditions are documented in the RAM-report artifact, not silently shipped"

requirements-completed: [FRAME-03, FRAME-04]

# Metrics
duration: 15min
completed: 2026-06-01
---

# Phase 50 Plan 04: Integration Gates — RAM Proof + Leonardo Buffer Disposition Summary

**COBS integration gates closed: Uno RAM held at 545 B free (no second buffer, FRAME-03), both full suites green (28/28 native + 408/408 host), and Leonardo DATA_BUFFER_SIZE=512 A/B-pin recorded as deliberate operator decision (FRAME-04 1024 B path test-validated independently)**

## Performance

- **Duration:** ~15 min (Task 2 continuation agent — Task 1 was pre-committed)
- **Started:** 2026-06-01T00:00:00Z
- **Completed:** 2026-06-01
- **Tasks:** 2 (Task 1 pre-committed at b4b3a35; Task 2 documentation-only)
- **Files modified:** 2

## Accomplishments

- Post-change Uno RAM gate confirmed: free RAM = 545 B (identical to Phase-49 baseline, 0 B delta); `check_uno_ram.sh` exits 0; no second ~512 B static buffer materialized by Plan-02 COBS firmware rewrite
- Dual-repo full-suite green confirmed: firmware `pio test -e native` 28/28 (5 suites including new `test_cobs_data_frame`) + host `python -m pytest --cov-fail-under=70` 408/408 (29 snapshots, coverage floor held)
- Leonardo DATA_BUFFER_SIZE A/B-pin surfaced for operator decision and recorded: keep-512-documented; `platformio.ini` unchanged; disposition + v1.9 linkage + FRAME-04 test-validation note captured in 50-RAM-REPORT.md

## Task Commits

1. **Task 1: Post-change Uno RAM proof + dual-repo full-suite green gate** — `b4b3a35` (docs — pre-committed before this continuation agent)
2. **Task 2: Leonardo DATA_BUFFER_SIZE A/B-pin disposition** — documentation-only; no firmware commit (platformio.ini unchanged); disposition recorded in 50-RAM-REPORT.md and this SUMMARY
3. **Plan metadata** — this commit (50-RAM-REPORT.md Task 2 section + 50-04-SUMMARY.md)

## Files Created/Modified

- `.planning/phases/50-data-path-framing-layer-automatic-resync-dual-repo-lockstep/50-RAM-REPORT.md` — Task 1: RAM figures table, gate results, no-second-buffer attestation; Task 2: Leonardo A/B-pin keep-512-documented disposition section (appended)
- `.planning/phases/50-data-path-framing-layer-automatic-resync-dual-repo-lockstep/50-04-SUMMARY.md` — this file

## Decisions Made

**Task 1:** No decisions needed — gate passed with zero delta (RAM unchanged from baseline). Flash +320 B (22492→22812, 69.7→70.7%) is acceptable; Flash is not the binding constraint.

**Task 2:** Operator decision (2026-06-01) — **keep-512-documented** for Leonardo `DATA_BUFFER_SIZE`. Rationale: the 512 B pin was set as a cross-phase A/B condition for the v1.9 read-bug RCA (paused at Phase 44, resumes Phase 45+). Restoring 1024 would end the A/B condition before it can be used. COBS is size-agnostic; FRAME-04's 1024 B path is exercised by the parameterized `test_cobs_data_frame` suite (28/28 pass) independent of the shipped define. The deliberate-pin disposition is recorded in `50-RAM-REPORT.md` (new section: "Leonardo DATA_BUFFER_SIZE A/B-Pin Disposition (FRAME-04 — Task 2)").

## Deviations from Plan

None — plan executed exactly as written. Task 2 option `keep-512-documented` was selected by the operator; all specified documentation actions were applied. No unplanned work was needed.

## Issues Encountered

None. Task 1 was pre-committed in the prior agent run (commit b4b3a35). Task 2 required only the disposition documentation with no code changes.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- **Phase 51** (FRAME-05: JSON command channel framing) can begin — the dual-repo green gate and breaking-upgrade documentation per D-03 are now in place; Phase 51 will add the version/handshake guard that prevents mixed-version interop
- **v1.9 Phase 45** (read-bug RCA continuation) has the Leonardo 512 B A/B pin preserved for its investigation
- Nothing is promoted to stable without operator authorization (D-17v2 carry-forward)

## Known Stubs

None — this plan is evidence/documentation only; no code stubs were introduced.

## Threat Flags

None — no new security-relevant surface introduced. T-50-06 (shipping 512 B Leonardo without explicit decision) is accepted/operator-gated: the disposition is now explicitly documented in 50-RAM-REPORT.md.

## Self-Check

**Files exist:**
- `.planning/phases/50-data-path-framing-layer-automatic-resync-dual-repo-lockstep/50-RAM-REPORT.md` — FOUND (contains "545", "keep-512-documented", "A/B-Pin Disposition", "test-validated")
- `.planning/phases/50-data-path-framing-layer-automatic-resync-dual-repo-lockstep/50-04-SUMMARY.md` — FOUND (this file)
- `firestarter/platformio.ini` `[env:leonardo]` `DATA_BUFFER_SIZE=512` — VERIFIED UNCHANGED (line 65)

**Commits exist:**
- `b4b3a35` — Task 1 pre-committed (50-RAM-REPORT.md initial content + dual-repo green gate)
- Plan metadata commit — pending (this commit)

## Self-Check: PASSED

All success criteria met:
- [x] platformio.ini [env:leonardo] still shows DATA_BUFFER_SIZE=512 (verified: line 65, unchanged)
- [x] 50-RAM-REPORT.md documents deliberate keep-512 A/B-pin disposition with v1.9 linkage + FRAME-04 1024 B test-validation note (appended section)
- [x] 50-04-SUMMARY.md created (covers both tasks, Self-Check section)
- [x] STATE.md / ROADMAP.md untouched (orchestrator owns these)

---
*Phase: 50-data-path-framing-layer-automatic-resync-dual-repo-lockstep*
*Completed: 2026-06-01*
