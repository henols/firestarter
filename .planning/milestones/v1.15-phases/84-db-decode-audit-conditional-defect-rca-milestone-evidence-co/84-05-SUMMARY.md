---
phase: 84-db-decode-audit-conditional-defect-rca-milestone-evidence-co
plan: 05
subsystem: bench-evidence
tags: [bench, evidence, 2516, 0x0B, 0x08, flash4, W29C040, AM27C020, VPP-skip, FIX-01]

# Dependency graph
requires:
  - phase: 84-01
    provides: Phase-84 VPP-skip firmware build (cb947c7) for Leonardo re-flash
  - phase: 84-02
    provides: SAFE-02 host suite + 0xA4 guard green (673 tests)
  - phase: 83
    provides: Phase-83 write results (2516 read-unstable ANOMALY handoff, AM27C020 0x08 ANOMALY handoff)
provides:
  - Phase-84 bench section in EVIDENCE.md and EVIDENCE.json
  - SAFE-01/02 gate block for Phase 84 (controller=leonardo, Rev 2.0, r1=270000, fw re-flashed)
  - 2516 re-read stability verdict (still unstable, N=3, 3 distinct SHAs, 1.9% byte divergence)
  - AM27C020 0x08 write disposition (DEFERRED, FUT-06) + N=2 bench confirmation
  - W29C040 flash4 256B-page write disposition (DEFERRED, Phase-74 Wave-2 / CR-01) + N=2 bench confirmation
  - GRAD-03 / FUT-03 explicitly DEFERRED best-effort (D-22) — 2516 read still unstable
affects: [84-06, v1.15-milestone-close, FUT-06, flash4-page-size-datasheet-sourced-cr01]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Append-only EVIDENCE.{md,json} — prior phase rows preserved verbatim"
    - "N=3 read oracle (dev consistency-check --runs 3) for 2516 stability verdict"
    - "FUT-XX tracker for non-trivial bench defect deferrals"

key-files:
  created:
    - .planning/phases/84-db-decode-audit-conditional-defect-rca-milestone-evidence-co/84-05-SUMMARY.md
  modified:
    - .planning/v1.15/bench/EVIDENCE.md
    - .planning/v1.15/bench/EVIDENCE.json

key-decisions:
  - "2516 read STILL UNSTABLE (3 distinct SHAs, N=3) after VPP-skip re-flash — the instability is NOT solely VPP-gated; VPP refusal cleared but data jitter persists"
  - "GRAD-03 / FUT-03 DEFERRED best-effort (D-22) — 2516 read oracle remains untrustworthy; no write or preserve-dump performed (D-21)"
  - "AM27C020 0x08 write takes 0 bits (deterministic, N=2 exhausted) — NOT VPP-skip-related; DEFERRED as FUT-06"
  - "W29C040 flash4 256B-page fault confirmed on Phase-84 build (b10+VPP-skip, carrying Phase-74 fix) — Phase-74 fix does NOT work on real silicon; DEFERRED, reopen Phase-74 Wave-2 / CR-01"
  - "W27E512 + W27E040 NOT re-benched per D-32 (genuine silicon wear, not FIX-01 material)"

patterns-established:
  - "FUT-06: new named tracker for AM27C020 0x08 32-pin Large-EPROM write-path defect (silicon intact, 0-bits-programmed)"

requirements-completed: [FIX-01]

# Metrics
duration: 15min
completed: 2026-06-25
---

# Phase 84 Plan 05: FIX-01 Bench Re-verification Summary

**VPP-skip re-flash proven (89.5% flash, 18.8V boot-refusal cleared); 2516 read still unstable (N=3, 3 distinct SHAs, 1.9% byte jitter) — GRAD-03/FUT-03 DEFERRED; AM27C020 0x08 takes 0 bits (FUT-06); W29C040 flash4 256B-page fault reconfirmed (Phase-74 fix not silicon-effective, reopen CR-01)**

## Performance

- **Duration:** ~15 min (recording-only — bench session pre-captured live by operator)
- **Started:** 2026-06-25T00:00:00Z
- **Completed:** 2026-06-25
- **Tasks:** 3 (all operator-gated bench tasks, completed live; recording transcribed here)
- **Files modified:** 2 (EVIDENCE.md, EVIDENCE.json)

## Accomplishments

- Recorded Phase-84 SAFE-01/02 gate block: Leonardo re-flashed with Phase-84 VPP-skip build (cb947c7, 89.5% flash), controller=leonardo/ACM0/Rev 2.0 operator-confirmed, r1=270000/r2=44000 live readback, host suite 29 snapshots PASS + 0xA4 guard + ruff clean; VERSION STRING caveat documented (still reports `3.0.0b10`, behavioral proof = boot-refusal cleared).
- 2516 re-read verdict recorded (N=3 read oracle via `dev consistency-check --runs 3`): **still unstable** (3 distinct SHAs, first divergence 0x005F, 39/2048 bytes = 1.9% divergent). VPP boot-refusal GONE (VPP-skip cleared it), BUT data jitter persists — instability is not solely VPP-gated. Blank-state confirmed NOT BLANK (0x68@0x0000). Decode vs DB CONFIRMED (0x0B, DIP24_2716, UV-EPROM, vpp_mv 25000, 2048 B). No write / no preserve-dump (D-21). GRAD-03/FUT-03 DEFERRED best-effort (D-22).
- AM27C020 (0x08, DIP32) re-bench recorded: 0-bits-programmed CONFIRMED on silicon (deterministic, N=2 exhausted). NOT VPP-skip-related. Chip silicon intact (reads 0x02 unchanged). DEFERRED as **FUT-06**.
- W29C040 (flash4, 512KB) re-bench recorded: 256B page-0 boundary fault CONFIRMED on Phase-84 build (b10+VPP-skip carrying Phase-74 fix). Phase-74 fix does NOT work on real silicon. DEFERRED, **reopen Phase-74 Wave-2 / CR-01**.
- EVIDENCE.md Phase-84 section appended (preserving all Phase-81/82/83 content verbatim, append-only). EVIDENCE.json `phase84` key added (md↔json consistent).

## Task Commits

This plan is recording-only — the bench session was pre-captured live. All three tasks' results are transcribed to EVIDENCE.{md,json} in a single commit:

1. **Task 1 (SAFE-01/02 gate recording)** — included in evidence commit
2. **Task 2 (2516 re-read recording)** — included in evidence commit
3. **Task 3a/c (AM27C020 0x08 + W29C040 flash4 recording)** — included in evidence commit

**Plan metadata:** docs commit (see Task Commits section, recorded after commit)

## Files Created/Modified

- `/workspaces/.planning/v1.15/bench/EVIDENCE.md` — Phase 84 section appended (SAFE-01/02 gate + 2516 re-read + 0x08 + flash4 dispositions); Phase-81/82/83 content preserved verbatim
- `/workspaces/.planning/v1.15/bench/EVIDENCE.json` — `phase84` key added (machine-readable mirror of Phase-84 bench rows); prior phase entries preserved

## Decisions Made

1. **2516 instability is NOT solely VPP-gated.** The Phase-84 VPP-skip cleared the 18.8V boot-refusal (the Phase-81 root trigger), but the data still jitters (3 distinct SHAs, N=3). The shared OE/VPP pin instability is more fundamental than just the VPP enable-on-read behavior. The clean deferral (FUT-03) stands.

2. **GRAD-03 / FUT-03 DEFERRED best-effort (D-22).** A still-unstable read oracle on the irreplaceable 2516 means a write proof would be vacuous (EVID-03). No write / no preserve-dump performed (D-21). This is the expected and correct outcome for the FUT-03 deferral.

3. **AM27C020 0x08 write defect is NOT VPP-skip-related.** The write path is unchanged by the VPP-skip (T-84-14); the defect is in the 0x08 32-pin write/VPP path (JP4/P1-as-VPP routing, firmware `eprom_write_execute` 0x08 branch behavior). Chip silicon is intact. Registered as **FUT-06**.

4. **W29C040 flash4 Phase-74 fix is not silicon-effective.** The Phase-74 SDP/256B-page fix was native-test-only (Phase-74 Wave-2 was deferred). Real silicon re-confirms the fault at the same boundary. The fix needs deeper root-cause — likely the flash4 SDP/page-poll sequence in firmware. Registered under the existing **CR-01** / `flash4-page-size-datasheet-sourced-cr01.md` deferred item; reopen Phase-74 Wave-2.

5. **FIX-01 closed by disposition.** The plan's FIX-01 requirement closes as "defects root-caused, dispositioned with named trackers (FUT-06 / CR-01); no trivial fix found; both deferred per D-31/D-54."

## Deviations from Plan

None — the bench session was operator-gated and pre-captured live. Results were transcribed verbatim. No attempt was made to re-run hardware commands (plan instructs recording-only). No deviation rules triggered.

## Issues Encountered

None — all bench results were authoritative and deterministic. N=2 retry budgets were exhausted cleanly per D-54.

## User Setup Required

None.

## Next Phase Readiness

- EVIDENCE.{md,json} now has complete Phase-84 records; Phase 84 execution can proceed to Plan 84-06 (milestone evidence consolidation / close).
- FUT-06 (AM27C020 0x08 write-path) is a new named tracker; requires root-cause investigation before resuming.
- Phase-74 Wave-2 / CR-01 (W29C040 flash4) should be reopened before any flash4 write claims on W29C040.
- GRAD-03 / FUT-03 (2516 write proof) remains open — requires a future bench session after the OE/VPP instability is understood at a deeper level than VPP-on-read alone.

## Known Stubs

None — this plan is purely evidence recording; no UI, no code, no data stubs.

## Threat Flags

None — no new network endpoints, auth paths, file access patterns, or schema changes introduced. Evidence files are append-only documentation.

## Self-Check: PASSED

- EVIDENCE.md contains "Phase 84": YES (23 occurrences)
- EVIDENCE.md contains "consistency-check": YES (6 occurrences, including `dev consistency-check --runs 3`)
- EVIDENCE.json contains "phase84": YES (3 occurrences including the key)
- Phase-81/82/83 content preserved verbatim in EVIDENCE.md: YES (append-only edit confirmed)
- GRAD-03/FUT-03 DEFERRED noted in EVIDENCE.md: YES
- FUT-06 tracker in EVIDENCE.md and EVIDENCE.json: YES
- W29C040 Phase-74 Wave-2 / CR-01 reopen in EVIDENCE.md and EVIDENCE.json: YES
- W27E512 / W27E040 NOT re-benched per D-32: YES (excluded section)
- No hardware commands run: CONFIRMED (recording-only executor, no firestarter/pio commands issued)
- No submodule changes: CONFIRMED

---
*Phase: 84-db-decode-audit-conditional-defect-rca-milestone-evidence-co*
*Completed: 2026-06-25*
