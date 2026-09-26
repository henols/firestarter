---
phase: 146-close-honesty-ledger-claim-gate-gh-15-reconciliation
plan: 05
subsystem: docs
tags: [planning-record, honesty-ledger, claim-gate, gh15]

# Dependency graph
requires:
  - phase: 146-03
    provides: measured ARM-toolchain-installable finding that closed the Phase 130 record-gate RED
provides:
  - Five inherited D-04/D-05 corrections discharged into PROJECT.md/REQUIREMENTS.md, each as a
    labelled ⚠ CORRECTION block appended after the text it corrects
  - 146-CORRECTIONS.md — the ten-row consolidated register, including three named divergences from
    the inherited correction-queue framing and the record-gate flip's measured causation
affects: [146-06, 146-07, 146-12, 146-13]

# Tech tracking
tech-stack:
  added: []
  patterns: ["labelled ⚠ CORRECTION block appended after its subject, never above it (D-14 pattern)"]

key-files:
  created:
    - .planning/phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/146-CORRECTIONS.md
  modified:
    - .planning/PROJECT.md
    - .planning/REQUIREMENTS.md

key-decisions:
  - "Task 1 re-measured the record-gate flip's causation rather than inheriting the replan brief's
    attribution: the removing commit is 91a06604, an interrupted 146-05 executor, not 146-04.
    146-04-SUMMARY.md's RED report is accurate at every 146-04 commit and was not edited."
  - "The independence clause (\"Independent of Phases 140-142 (different repo)\") has zero PROJECT.md
    hits — no block was manufactured for a premise research disproved; PROJECT.md:131 was updated
    from forward-looking to discharged instead, since it was never false."
  - "F-140-05's throughput-table correction covers TWO rows (0x07 and 0x08), not the one CONTEXT
    names, because the shipped source's own comment (eprom_params.cpp:41-43) names the 0x08
    contradiction explicitly."
  - "F-140-07's energy-cap justification is already corrected in place in firestarter/doc/PROTOCOLS.md
    §1.5 (Phase 140 record, plan 140-06); this plan discharges only the remaining .planning-side sites,
    not the firmware document."

requirements-completed: [CLOSE-04]

coverage:
  - id: D1
    description: "Verified the ROADMAP half (two blocks + charter discharge) already landed at 8df5e564, and the Phase 130 record gate is rc=0 at HEAD with the flip's causation measured (91a06604, not 146-04)"
    verification:
      - kind: other
        ref: "python3 .planning/phases/130-close-honesty-ledger-claim-gate-release-decision/check_record_corrections.py"
        status: pass
    human_judgment: false
  - id: D2
    description: "Landed four labelled correction blocks in PROJECT.md (C-3 wire-field, C-5 throughput table, C-6 energy-cap justification, C-8/OD-B comparative claim) and one in REQUIREMENTS.md (C-6 D-02 rationale), plus updated PROJECT.md:131 from deferred to discharged"
    verification:
      - kind: other
        ref: "grep -c 'CORRECTION (Phase 146' .planning/PROJECT.md == 4; .planning/REQUIREMENTS.md == 1"
        status: pass
      - kind: other
        ref: "python3 .planning/phases/130-close-honesty-ledger-claim-gate-release-decision/check_record_corrections.py (rc=0 before and after)"
        status: pass
    human_judgment: false
  - id: D3
    description: "146-CORRECTIONS.md written: ten-row register, three divergence findings, record-gate section, block-versus-history rule with site inventory, two adjacency findings, three non-claims; green under its own claim gate with a negative-control proof that the locator can fail"
    verification:
      - kind: other
        ref: "python3 146-check-claims.py 146-CORRECTIONS.md (rc=0); negative control on scratch copy (rc=1, 3 planted labels named)"
        status: pass
    human_judgment: false

duration: ~35min
completed: 2026-08-17
status: complete
---

# Phase 146 Plan 05: Correction-Queue Discharge & Consolidated Register Summary

**Landed the five still-owed D-04/D-05 correction blocks (four in PROJECT.md, one in REQUIREMENTS.md) and wrote `146-CORRECTIONS.md`, a ten-row register that also names three places the inherited correction framing itself was wrong.**

## Performance

- **Duration:** ~35 min
- **Completed:** 2026-08-17
- **Tasks:** 3
- **Files modified:** 3 (2 modified, 1 created)

## Accomplishments

- Verified (not re-landed) the ROADMAP half of the correction queue already committed at `8df5e564`
  by an interrupted executor, and confirmed the Phase 130 record gate is `rc=0` at HEAD with tally
  `{'block': 23, 'line-label': 4, 'inline-history': 6, 'inline-allow': 10, 'superseded': 12}`,
  matching `146-CITATIONS.md` §0.6's last-green reading exactly.
- Measured the record-gate flip's real causation: the needle (`arm-none-eabi-gcc` + `absent`
  co-occurring) is gone from `.planning/STATE.md:11` starting at commit `91a06604` — an interrupted
  `146-05` executor's own commit — not `146-04` as the replan brief's first-version §4 claimed.
  Confirmed `146-04-SUMMARY.md`'s report of the gate as still RED was **accurate at every `146-04`
  commit** through `0accb44e`; the file was not edited.
- Landed four `⚠ CORRECTION (Phase 146 / CLOSE-04)` blocks in `PROJECT.md` and one in
  `REQUIREMENTS.md`, each appended after the text it corrects, each citing false text by `file:line`
  rather than restating it:
  - **C-3** — the `pulse-delay` wire field is parsed unclamped (`json_parser.c:466-469,304-306`,
    `firestarter.h:197`); an over-ceiling value is delivered, not truncated, via Phase 141's
    split-delay helper; the only firmware-side refusal is `0x0B`'s, inert on `0x07`/`0x08`. Recorded,
    not clamped — Backlog 999.31 owns the bound decision.
  - **C-5** — the throughput table's overpulse column is false for **both** `0x07` and `0x08` (not
    just `0x07`), per the shipped source's own contradiction comment; the `0x0B` max-pulses cell now
    reads the shipped value (255, not the energy cap).
  - **C-6** — the "classic 2716 total programming time" justification for the 50 ms energy cap is
    wrong (the datasheet's actual total is 100 seconds); the value itself is unaffected. Landed in
    both `PROJECT.md` and `REQUIREMENTS.md`'s D-02 rationale cell. `firestarter/doc/PROTOCOLS.md`
    §1.5 already carries this correction, landed by the Phase 140 record — not redone here.
  - **C-8 (OD-B)** — the "Faster than today in the typical case" sentence is an unsupported
    comparative claim (145 D-08 forbids one without a control run); corrected in place.
  - `PROJECT.md:131` updated from "deferred to Phase 146" to "DISCHARGED AT Phase 146, plan 146-05" —
    a true statement update, not a correction (the independence clause has zero `PROJECT.md` hits).
- Wrote `146-CORRECTIONS.md`: a ten-row register (C-1 through C-10) covering all seven origin findings
  plus the record-gate flip, three named divergences from the inherited correction-queue framing, a
  record-gate section stating both causation readings side by side, a block-versus-history rule with
  its full site inventory, two host-README adjacency findings owed to plan 146-07, and three closing
  non-claims. Green under `146-check-claims.py` run positionally against the file alone; a negative
  control on a scratch copy outside the phase directory (with three planted forbidden phrases)
  exited non-zero naming all three labels, then was discarded.

## Task Commits

Each task was committed atomically:

1. **Task 1: Verify the landed ROADMAP half and record the record-gate flip with its causation** —
   measurement-only task, no files modified; findings folded into this SUMMARY and into
   `146-CORRECTIONS.md`'s "Record gate" section (Task 3).
2. **Task 2: Land the four PROJECT blocks and the one REQUIREMENTS block** - `c023f42d` (docs)
3. **Task 3: Write 146-CORRECTIONS.md — the consolidated register** - `471511da` (docs)

**Plan metadata:** (this commit, plus the follow-up STATE.md/ROADMAP.md hand-edit commit)

## Files Created/Modified

- `.planning/phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/146-CORRECTIONS.md` -
  the consolidated correction register (created)
- `.planning/PROJECT.md` - four `⚠ CORRECTION` blocks landed (C-3, C-5, C-6, C-8) plus the `:131`
  discharge-status update (62 insertions, 1 deletion)
- `.planning/REQUIREMENTS.md` - one `⚠ CORRECTION` block landed (C-6, scoped to D-02's rationale
  cell) (13 insertions)

## Decisions Made

- **Re-measured rather than inherited the record-gate flip's attribution.** The replan brief's
  first-version §4 credited `146-04` with closing the RED; testing the needle against every
  historical `STATE.md` blob shows it sits on line 11 through `146-04`'s last commit (`0accb44e`)
  and is gone starting at `91a06604` (`146-05`, interrupted). `146-04-SUMMARY.md` was left unedited
  because its RED report was accurate when written.
- **No block was written for the independence clause's `PROJECT.md` half**, because
  `grep -c "Independent of Phases 140"` against `PROJECT.md` returns 0 — the premise that a false
  `PROJECT.md` site existed was itself wrong, and manufacturing a correction for a non-existent
  false statement would have violated D-14/this plan's own prohibitions.
- **F-140-05's correction was widened to two rows** (`0x07` and `0x08`) rather than the one row
  CONTEXT named, because the shipped source's own comment names both.
- **F-140-07's firmware-doc half was left untouched** — `firestarter/doc/PROTOCOLS.md` §1.5 already
  carries the identical correction (landed by plan 140-06); re-editing it would have been redundant
  and outside this plan's meta-only scope (D-06).
- **C-7 (debug-message wording) and C-8/F-144-01 (stale native-env numerals) were recorded in the
  register but not landed as blocks** — both are owed by plans 146-07 and 146-06 respectively, per
  D-05's "three corrections land in other plans" instruction; landing them here would have exceeded
  this plan's `files_modified` scope and duplicated another plan's ownership.

## Deviations from Plan

None — plan executed as written, with one internal correction during Task 3's authoring: the
register's row-id column was initially written as bold Markdown (`| **C-1** | ...`), which the
task's own verify regex `^\| *C-[0-9]` cannot match through the `**` markup. Caught immediately by
running the verify command before considering the task done; fixed by stripping the bold markup
from the row-id cells only (content unchanged), re-verified `register_rows=10`, and re-ran the claim
gate to confirm it still passes. Not logged as a Rule 1-4 deviation since it is a same-task
self-correction against the task's own stated acceptance criterion, not new-work discovery.

## Issues Encountered

None beyond the verify-regex fix above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `146-06` and `146-07` can proceed to land their own owed corrections (C-7 debug-message wording +
  orphaned catalog id; C-8/F-144-01 stale native-env numerals; the two README adjacency findings
  A-1/A-2), all pre-located and cited in `146-CORRECTIONS.md`.
- `146-12` has the public gh#15 justification correction (C-6's public half) queued and cited,
  ready for its blocking operator wording review.
- STATE.md and ROADMAP.md are updated by hand in a following separate commit per this plan's
  state-and-roadmap protocol; that commit also re-runs and records the Phase 130 record gate one
  final time after the STATE.md write.

---
*Phase: 146-close-honesty-ledger-claim-gate-gh-15-reconciliation*
*Completed: 2026-08-17*
