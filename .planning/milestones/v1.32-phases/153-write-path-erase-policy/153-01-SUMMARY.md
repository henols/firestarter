---
phase: 153-write-path-erase-policy
plan: 01
subsystem: firmware-planning
tags: [decision-record, avr-size-budget, eeprom-28c, sdp, merge-05, size-baseline]

requires: []
provides:
  - "153-DECISIONS.md — the settled-before-code record every later plan in Phase 153 cites"
  - "D-153-01: erase supply form (six inline set_data calls, 0 B RAM) + MERGE-05 funding posture (fourth named exemption, sized in plan 14)"
  - "D-153-02: SDP-disable prefix emitted before the chip-erase sequence, via eeprom28c_sdp_unlock_execute reuse"
  - "D-153-03: GATE-03 mechanism correction — check_dispatch.py cannot see handler-body register writes; brace-matched negative source scan is the real control"
  - "D-153-04: no post-erase blank check wired on 0x0D; erase --sector-address ignored"
  - "D-153-05: erase stays standalone — out of write_init and out of write's FLAG_SKIP_SDP_UNLOCK auto-set"
  - "Verified cold pre-change size/test baseline on uno, uno328pb, leonardo, native, native_nodevtools, and the host pytest suite"
affects: [153-02, 153-03, 153-04, 153-05, 153-14]

tech-stack:
  added: []
  patterns:
    - "MERGE-05 named-exemption mechanism (fourth instance reserved: MERGE05_ERASE_STANDALONE_EXEMPTION_BYTES)"
    - "Decision-record-before-code (D-153-NN ids cited by later plans instead of re-deciding)"

key-files:
  created:
    - .planning/phases/153-write-path-erase-policy/153-DECISIONS.md
  modified: []

key-decisions:
  - "Erase supply form: six inline handle->firestarter_set_data calls, 0 B RAM — not a new .data table (would cost +30 B RAM against a fully-consumed RAM exemption)"
  - "Chip erase emits an SDP-disable prefix first (asymmetry argument: a phantom erase on 0x0D is undetectable, so silence in AN 0544B is not permission)"
  - "check_dispatch.py structurally cannot see a handler-body control-register write; the real GATE-03 control is a brace-matched negative source scan built in plan 05"
  - "No post-erase blank check wired on 0x0D (erase -b is a documented no-op); erase --sector-address ignored on this chip-erase-only protocol"
  - "erase stays standalone: no FLAG_CAN_ERASE-gated block added to eeprom28c_write_init, no --skip-sdp-unlock option on erase"

requirements-completed: []  # This plan owns NO requirement flips (stated verbatim in its own
  # objective: "Requirement flips owned by this plan: none"). It discharges only the
  # stated-in-writing halves of ERASE-04/ERASE-08/ERASE-09 and unblocks ERASE-01/02/03 for later
  # plans to implement in code; marking any of these Complete here would be premature (see
  # project lesson on executors prematurely marking multi-plan requirements complete).

coverage:
  - id: D1
    description: "153-DECISIONS.md settles D-153-01 (erase supply form + MERGE-05 funding posture) with measured RAM figures and named rejected alternatives"
    requirement: "ERASE-04"
    verification:
      - kind: unit
        ref: "grep assertions in 153-01-PLAN.md Task 1 <verify> block, all run and passing"
        status: pass
    human_judgment: false
  - id: D2
    description: "153-DECISIONS.md settles D-153-02..05 (SDP-disable prefix, GATE-03 mechanism correction, no post-erase blank check, erase stays standalone)"
    requirement: "ERASE-04"
    verification:
      - kind: unit
        ref: "grep assertions in 153-01-PLAN.md Task 2 <verify> block, all run and passing"
        status: pass
    human_judgment: false
  - id: D3
    description: "Cold pre-change size/test position reproduced and transcribed for uno, uno328pb, leonardo (byte-identical to size_baseline.json), native/native_nodevtools (163 cases/17 suites), and host pytest (1806 passed, 83.61% coverage)"
    requirement: "ERASE-08"
    verification:
      - kind: unit
        ref: "grep assertions in 153-01-PLAN.md Task 3 <verify> block, all run and passing; git diff --quiet in firestarter/ confirmed"
        status: pass
    human_judgment: false

duration: 35min
completed: 2026-08-21
status: complete
---

# Phase 153 Plan 01: Wave-0 Decision Record & Cold Baseline Summary

**Settled the erase supply form, SDP-disable prefix, and GATE-03 mechanism correction in writing before any code was touched, and reproduced a byte-identical cold pre-change size/test baseline on all three AVR targets plus native and host suites.**

## Performance

- **Duration:** ~35 min
- **Tasks:** 3/3 completed
- **Files modified:** 1 (new file)

## Accomplishments

- Created `153-DECISIONS.md` carrying five settled decision sections (`D-153-01` through
  `D-153-05`) that every later plan in this phase cites instead of re-deciding.
- Settled the erase supply form as six inline `set_data` calls (0 B RAM) and reserved the fourth
  named MERGE-05 exemption (`MERGE05_ERASE_STANDALONE_EXEMPTION_BYTES`) for plan 14 to size from
  measurement.
- Settled the SDP-disable-prefix question with an asymmetry argument (a phantom erase on `0x0D`
  is undetectable — Phase 151 established the protection state is unreadable) and pinned the
  reuse mechanism (`eeprom28c_sdp_unlock_execute`), the `rurp_set_data_output()` consequence for
  plan 03, and the observable stream shape for plan 04.
- Corrected the GATE-03 mechanism claim in writing: `check_dispatch.py` is DB-and-dispatch-table
  scoped and structurally cannot see a handler-body control-register write; the real control is a
  brace-matched negative source scan, planned as a real gate in plan 05.
- Recorded that no post-erase blank check is wired on `0x0D` and that `erase` stays out of both
  `write_init`'s implicit erase-on-write pattern and `write`'s `FLAG_SKIP_SDP_UNLOCK` auto-set.
- Reproduced the pre-change cold position on `uno`, `uno328pb`, `leonardo` — all three
  byte-identical to the committed `size_baseline.json` — plus `native`/`native_nodevtools`
  (163 cases / 17 suites each) and the host pytest suite (1806 passed, 83.61% coverage).
- Recorded the phrase "software-proven and unvalidated on silicon" verbatim, per ERASE-09.

## Task Commits

1. **Task 1: Record the erase supply form and MERGE-05 funding posture (D-153-01)** - `de2dd336` (docs)
2. **Task 2: Settle the SDP-disable-prefix question and GATE-03 mechanism correction (D-153-02..05)** - `79e1142f` (docs)
3. **Task 3: Reproduce the pre-change cold size position on all three AVR targets** - `c03a4ad4` (docs)

**Plan metadata:** (final commit hash recorded after this summary is committed)

## Files Created/Modified

- `.planning/phases/153-write-path-erase-policy/153-DECISIONS.md` - the settled decision record for the whole phase (D-153-01..05 plus the pre-change measured position)

## Decisions Made

- **D-153-01:** six inline `set_data` calls for the erase sequence, 0 B RAM; three alternative
  forms rejected by name; fourth named FLASH-only MERGE-05 exemption reserved for plan 14.
- **D-153-02:** the `0x0D` chip erase emits an SDP-disable prefix (reusing
  `eeprom28c_sdp_unlock_execute`), based on an undetectable-phantom-erase asymmetry argument, not
  the application note's silence.
- **D-153-03:** `check_dispatch.py`'s GATE-03 guard cannot observe a handler-body register write;
  the primary control is a brace-matched negative source scan (plan 05), and
  `check_dispatch.py` itself remains byte-unchanged.
- **D-153-04:** no post-erase blank check on `0x0D`; `erase --sector-address` is ignored (chip
  erase is device-global by construction).
- **D-153-05:** `erase` stays standalone — no implicit erase-on-write block, no
  `--skip-sdp-unlock` option.

## Deviations from Plan

None — plan executed exactly as written. All three tasks' automated verification checks passed
on first attempt; no auto-fixes, no blocking issues, no architectural questions arose.

## Issues Encountered

None. The `pytest` host-suite command in Task 3 ran longer than the default foreground timeout
and was completed as a background command; this is an environment/tooling accommodation, not a
plan deviation — the command executed exactly as specified in the plan (`-o addopts=""`, full
coverage flags) and its result (1806 passed, 83.61% coverage) was captured and transcribed
unchanged.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plans 02-06 (and later) can now cite `D-153-01` through `D-153-05` directly instead of
  re-deciding the erase supply form, the SDP-disable prefix, the GATE-03 mechanism, the
  post-erase blank check disposition, or the write/erase separation.
- Plan 14 has a verified, cold, three-target pre-change baseline (byte-identical to
  `size_baseline.json`) to measure its delta against, plus agreeing native case/suite counts and
  a host coverage figure.
- No blockers: all three AVR targets reproduced byte-identically; no discrepancy to flag.

---
*Phase: 153-write-path-erase-policy*
*Completed: 2026-08-21*

## Self-Check: PASSED

- FOUND: `.planning/phases/153-write-path-erase-policy/153-DECISIONS.md`
- FOUND: `.planning/phases/153-write-path-erase-policy/153-01-SUMMARY.md`
- FOUND: commit `de2dd336`
- FOUND: commit `79e1142f`
- FOUND: commit `c03a4ad4`
- FOUND: commit `307243d6`
