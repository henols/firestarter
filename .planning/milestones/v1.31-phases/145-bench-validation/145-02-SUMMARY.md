---
phase: 145-bench-validation
plan: "02"
subsystem: testing
tags: [bench-validation, support-status, chip-database, disposition-record, am27c020, m2716, m2732, gate-0]

# Dependency graph
requires:
  - phase: 145-01
    provides: "145-BENCH-LOG.md skeleton with Gate 0 subsections stubbed NOT YET RUN, D-14 taxonomy fixed in the preamble, D-20 dispatch line, and the verification-map bindings table"
provides:
  - "145-BENCH-LOG.md: BENCH-03 support_status invariance re-measured at the tip across the whole v1.31 range on four independent legs, verdict validated"
  - "145-BENCH-LOG.md: BENCH-02 0x08 (AM27C020) disposition — skipped-with-reason, citing Phase 99's write#1 60/64 -> write#2 0/64 and FUT-08, judged a fail under D-14"
  - "145-BENCH-LOG.md: BENCH-02 0x0B (M2716/M2732) disposition — skipped-with-reason, citing Phase 79's 22.4V DMM / 23.9V firmware VPE reading at max pot, graduation parked at plan 79-03"
  - "Gate 0 closed with a verdict naming all four cleared items and stating zero hardware was touched"
affects: [145-03, 145-04, 145-05, 145-06, 145-07, 145-08, 145-09]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Whole-milestone-range git diff as the machine-checked invariance proof (D-15): merge-base confirmed live rather than assumed, diffed against HEAD across the WHOLE range, never against this phase's own commits"
    - "Skipped-with-reason disposition record shape: missing part + prior bench state with numbers and exact source + explicit 'NOT inferred from the 0x07 result' sentence + a clean one-word verdict line — never a bare line"

key-files:
  created: []
  modified:
    - .planning/phases/145-bench-validation/145-BENCH-LOG.md

key-decisions:
  - "requirements-completed left empty and REQUIREMENTS.md untouched: BENCH-02 and BENCH-03 are multi-plan requirements flipped to Complete only by 145-09 behind its blocking operator gate, per explicit dispatch instructions and 145-01's own established precedent for BENCH-01"
  - "Ran the full firmware suite (312 passed) and the host sibling-porcelain subset (38 passed) as an end-of-wave regression tripwire, matching 145-01's baseline exactly, even though no task's own verify block required it — zero source was touched by this plan, so this is due-diligence confirmation, not new record content, and was not written into 145-BENCH-LOG.md (that subsection is 145-01's territory)"

patterns-established:
  - "Every disposition-record number is cited with its exact source file and re-verified live rather than re-derived: Phase 99's 0x08 numbers and Phase 79's 0x0B numbers are quoted from their SUMMARY/BENCH-LOG files, not re-measured, while BENCH-03's four legs are re-run live this session rather than copied from RESEARCH.md"

requirements-completed: []

coverage:
  - id: D1
    description: "BENCH-03 support_status invariance re-measured at the tip across the whole v1.31 range on four independent legs (whole-range diff, generator-inputs diff, mechanism-lock re-run, value histogram), with the three benign textual mentions verified by grepping the actual diff and the firmware repo's zero-hit scope confirmed; verdict validated"
    requirement: "BENCH-03"
    verification:
      - kind: other
        ref: "cd firestarter_app && git diff 4d18b645..HEAD -- firestarter/data/chip_database.json | wc -c -> 0"
        status: pass
      - kind: other
        ref: "cd firestarter_app && python3 tools/check_no_community_support_status_write.py -> exit 0"
        status: pass
      - kind: other
        ref: "cd firestarter_app && sha256sum firestarter/data/chip_database.json -> 3befbaad7bbb88307abd94db0447ad78e847c40f3c96be7751f5b87a1e913479"
        status: pass
    human_judgment: false
  - id: D2
    description: "0x08 (AM27C020) BENCH-02 disposition recorded skipped-with-reason: names the missing part, cites Phase 99's write#1/write#2 numbers and FUT-08, judged a fail under D-14's taxonomy, and states plainly it is not inferred from the 0x07 result"
    requirement: "BENCH-02"
    verification:
      - kind: other
        ref: "grep assertions over 145-BENCH-LOG.md: AM27C020, FUT-08, '60 of 64', '0 of 64', 35706c2, 0x1da00, 'not inferred from the', 'skipped-with-reason'"
        status: pass
    human_judgment: false
  - id: D3
    description: "0x0B (M2716/M2732) BENCH-02 disposition recorded skipped-with-reason: names both missing parts, cites Phase 79's rail-corrected VPE numbers and the NOT-CLEARED-then-retired 25V bar, names plan 79-03 as the parked definitive proof; Gate 0 closed with a verdict naming all four cleared items and zero hardware touched"
    requirement: "BENCH-02"
    verification:
      - kind: other
        ref: "grep assertions over 145-BENCH-LOG.md: M2716, M2732, 22.4, 23.9, 79-03, 'parked', 'not inferred from the', Gate 0 verdict no longer NOT YET RUN"
        status: pass
    human_judgment: false

# Metrics
duration: 9min
completed: 2026-08-15
status: complete
---

# Phase 145 Plan 02: Bench Validation — Gate 0 Hardware-Free Requirements Summary

**BENCH-03 re-measured validated on four independent legs at the tip; both BENCH-02 disposition records written citing Phase 99's and Phase 79's exact numbers — Gate 0 closed with zero hardware touched.**

## Performance

- **Duration:** 9 min
- **Started:** 2026-08-15T16:24:00Z
- **Completed:** 2026-08-15T16:31:27Z
- **Tasks:** 3 completed
- **Files modified:** 1 (`145-BENCH-LOG.md`, three sequential edits)

## Accomplishments

- Re-measured BENCH-03 at the tip across the **whole** v1.31 range on four independent legs, all
  matching discussion-time expectations exactly: merge-base `4d18b645ab18a2d2465f0f623062e9249eb24132`
  confirmed live (not assumed), the whole-range `chip_database.json` diff empty (0 bytes), the
  generator-inputs diff empty, `check_no_community_support_status_write.py` exiting 0, and the value
  histogram `total 746 / supported 736 / adapter-required 9 / protocol-not-implemented 1` with digest
  `3befbaad7bbb88307abd94db0447ad78e847c40f3c96be7751f5b87a1e913479`
- Verified — not restated from RESEARCH — the three benign textual `support_status` mentions in the
  diff range by grepping the actual diff per file: two in
  `tests/golden/chip_database_field_inventory.json` (an occurrence count and a key-list entry) and
  one in `tests/test_write_response_budget.py` (a docstring); a full unscoped diff grep confirmed
  exactly 3 mentions exist in the whole range
- Confirmed zero `support_status` hits across `firestarter/src/`, `include/`, `scripts/`, establishing
  BENCH-03's single-repo scope
- Wrote the `0x08` AM27C020 disposition citing Phase 99's write#1 (60 of 64 byte-exact, `bad bytes: 4`,
  failing offset `0x1da00`) and write#2 (0 of 64, `bad bytes: 64`), the `dev consistency-check` PASS at
  N=3 with one distinct SHA, idle VPP `12.9`–`13.0 V`, the explicit not-measured program-window entry
  naming the DTR-reset-on-close blocker, and carry-forward `FUT-08` — judged plainly a **fail** under
  D-14's taxonomy and explicitly **not inferred** from the `0x07` result
- Wrote the `0x0B` M2716/M2732 disposition citing Phase 79's rail-corrected `22.4 V` operator DMM /
  `23.9 V` firmware VPE reading at max pot, R1/R2 `270000`/`44000`, the strict 25 V bar NOT CLEARED
  then retired by operator override, the four NMOS chips' best-effort `supported` graduation, and the
  `79-03`-parked definitive proof — likewise explicitly **not inferred** from the `0x07` result
- Closed Gate 0 with a verdict naming all four cleared items (instrument inventory/tripwire baseline,
  the four write images, BENCH-03 validated, both BENCH-02 dispositions) and stating plainly that zero
  hardware was touched
- Confirmed both sub-repos' regression suites unaffected as an end-of-wave tripwire: firmware suite
  **312 passed**, host sibling-porcelain subset **38 passed** — matching 145-01's recorded baseline
  exactly (no source was touched by this plan, so no drift was expected or found)

## Task Commits

Each task was committed atomically:

1. **Task 1: Re-measure and record BENCH-03 — no support_status changed across the whole v1.31 range** - `4dca6847` (docs)
2. **Task 2: Write the 0x08 AM27C020 skipped-with-reason disposition record** - `1d676ec1` (docs)
3. **Task 3: Write the 0x0B M2716/M2732 skipped-with-reason disposition record and close Gate 0** - `1c8c01e1` (docs)

**Plan metadata:** commit pending (this summary + STATE.md/ROADMAP.md updates)

## Files Created/Modified

- `.planning/phases/145-bench-validation/145-BENCH-LOG.md` - filled Gate 0's three remaining
  subsections (BENCH-03 `support_status` invariance, `0x08` disposition, `0x0B` disposition) and the
  `Gate 0 verdict:` line, closing Gate 0 entirely

## Decisions Made

- **`requirements-completed` left empty; `REQUIREMENTS.md` untouched.** BENCH-02 and BENCH-03 are
  multi-plan requirements whose flip to Complete is owned by `145-09` behind its blocking operator
  gate, per this plan's explicit dispatch instructions and 145-01's own established precedent for
  BENCH-01. Evidence lives in `145-BENCH-LOG.md` instead.
- **Ran the full firmware suite + host sibling-porcelain subset as an end-of-wave tripwire**, even
  though no task's own `<verify>` block required it, matching the phase's validation-contract
  "after every plan wave" sampling rule. Zero source was touched, so this is due-diligence
  confirmation, recorded here rather than added to `145-BENCH-LOG.md`'s tripwire-baseline
  subsection, which is `145-01`'s territory and already complete.

## Deviations from Plan

None - plan executed exactly as written. All three tasks' verify blocks passed on the first attempt;
every BENCH-03 leg matched `145-RESEARCH.md`'s discussion-time expectation exactly (the confirmed
merge-base, both empty diffs, the mechanism-lock exit code, the histogram, and the digest). No bugs,
missing functionality, blocking issues, or architectural questions arose — this is a zero-hardware
record-writing plan operating entirely inside the meta repo, reading both sub-repos read-only.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- **Gate 0 is fully closed.** Both hardware-free requirements — BENCH-02 and BENCH-03 — are complete
  and recorded with their full evidence in `145-BENCH-LOG.md`, so a D-13 halt at any later gate
  (Gate 1 through Gate 3) cannot cost either requirement.
- `145-03` onward can proceed to the first hardware-touching plan (Gate 1: identity, reflash, VPP)
  whenever the operator is physically present at the bench with the Leonardo + Rev 2.0 shield and the
  W27C512. Per D-20 and the standing STATE.md restriction for Phase 145, that plan — and every plan
  through `145-08` — must not run under `--auto`/`--chain`.
- No blockers.

## Self-Check: PASSED

File claimed above (`145-BENCH-LOG.md`) confirmed present on disk. All 3 commit hashes (`4dca6847`,
`1d676ec1`, `1c8c01e1`) confirmed present in `git log --oneline --all`.

---
*Phase: 145-bench-validation*
*Completed: 2026-08-15*
