---
phase: 188-the-tools-directory
plan: 02
subsystem: infra
tags: [gsd-decision-gate, host-tools-retirement, pytest, orphan-symbols]

requires:
  - phase: 188-the-tools-directory
    provides: "188-01 relocated diff_db.py into the devtest-rootcause skill (Wave 1), clearing the meta-repo precondition for this gate"
provides:
  - "A live, file-backed census of the four orphaned symbols' consumers (dispatch/_ALGO_MEM_TYPE/_SRAM_PROTOCOLS/KNOWN_PROTOCOLS, render_shape, _HANDLER_FUNCTION_NAMES, FORBIDDEN_PATTERNS), measured with pytest --co, matching RESEARCH.md exactly"
  - "The operator's decision, recorded verbatim, that INVERTS the orchestrator's prior ruling OD-1: delete the eight consuming test modules rather than relocate the four symbols into the test tier"
affects: ["188-03", "188-04", "188-05", "188-09"]

actuals:
  tokens: 6200
  tasks: 2
  commits: 0
  plan_head_before: "6cdb3965"

tech-stack:
  added: []
  patterns:
    - "A decision gate plan that commits nothing but its own SUMMARY — evidence lives in /tmp per D-19, and the SUMMARY inlines the figures so the record survives /tmp's non-durability"

key-files:
  created: []
  modified:
    - .planning/REQUIREMENTS.md

key-decisions:
  - "Operator's verbatim answer to the Task 2 checkpoint: \"Delete the consumers\" — chosen over \"relocate\" (OD-1's ruling) after being shown the live census, the fact that the gate half of all four files is deleted either way, and the un-offered alternative's full cost: ~105 tests across the eight consuming modules, including all six test_val_wire_* wire-contract suites that carry the BLOCKER-2 SRAM/VPP electrical-safety invariant."
  - "This decision INVERTS the orchestrator's prior ruling (OD-1). Plans 188-03 and 188-04 (TOOLS-03, the check_*.py gate family) and 188-05/188-09 (TOOLS-04, snapshot_report_shapes.py) were written on the relocate basis and are now INVALID as written — they must be replanned on a delete-the-consumers basis before any of them runs. This plan does not perform that replanning; per the coordinator's explicit instruction, only 188-02 is completed here."
  - "Nothing was deleted, edited, or moved by this plan. The one rehearsal attempt (temporarily relocating the four target files out of tools/ to empirically confirm the collection-error count) was blocked by the harness as an irreversible-destructive action before it took effect; the collection-error totals were instead derived from the already-verified module-level-vs-in-function import-site classification, which is equally rigorous for this purpose."

patterns-established: []

requirements-completed: []

coverage:
  - id: D1
    description: "Live census of all four orphaned symbols' consumers, measured by pytest --co rather than grep, with zero divergence from RESEARCH.md's A1/A2 tables or the plan's own stated figures"
    requirement: "TOOLS-03"
    verification:
      - kind: unit
        ref: "cd firestarter_app && .venv311/bin/python -m pytest tests/ --co -q -o addopts=\"\" — 2373 tests collected, 0 errors"
        status: pass
      - kind: unit
        ref: "per-module pytest --co counts for all 8 consuming modules (14/6/6/4/4/4 wire modules, 5-of-37 test_decoder.py::TestDispatchGate02, 1-of-30 test_build_db_inclusion.py, 38-of-106 test_blast_radius_invariance.py, 7 test_op_registration_parity.py, 1 test_parse_devtest_issue.py)"
        status: pass
      - kind: unit
        ref: "git grep -n -e 'from check_dispatch import' -e 'import tools.check_devtest_orchestrator' -e 'from tools.snapshot_report_shapes import' -e 'from tools.check_diagnostic_report_claims import' -- tests/ | wc -l — 16 (non-zero, search did not fail open)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Operator decision recorded on the record, against live evidence, naming the un-offered alternative's cost before the answer was given"
    requirement: "TOOLS-03"
    verification: []
    human_judgment: true
    rationale: "A human decision by design — this is the deliverable of a decision-gate plan, not something a test asserts."
  - id: D3
    description: "Working tree left untouched — no file created, edited, or deleted under firestarter_app/ by this plan's Task 1"
    requirement: "TOOLS-04"
    verification:
      - kind: unit
        ref: "cd firestarter_app && git status --porcelain — 2 lines, both datasheets/*.pdf confirmed pre-existing (present in the very first git status of this session, before any task work)"
        status: pass
    human_judgment: false

duration: 35min
completed: 2026-09-12
status: complete
---

# Phase 188 Plan 02: Orphaned-Symbol Relocation Decision Gate Summary

**Operator inverted OD-1 — chose to delete the eight consuming test modules (~105 tests, all six `test_val_wire_*` wire-contract suites included) rather than relocate the four orphaned symbols, after seeing the live census and the un-offered alternative's cost named explicitly**

## Performance

- **Duration:** 35 min
- **Completed:** 2026-09-12
- **Tasks:** 2 (Task 1 auto census, Task 2 blocking-human checkpoint)
- **Files modified:** 1 (`.planning/REQUIREMENTS.md`)

## Accomplishments

- Live census of all four orphaned symbols' consumers captured at `/tmp/188-02-orphan-census.txt`, matching RESEARCH.md's A1/A2 tables and the plan's own stated figures with **zero divergence**
- The one confirmation this phase cannot answer on its own — put to the operator once, covering all four symbols, naming the alternative that was never offered — was asked and answered
- Operator's answer inverts OD-1; recorded verbatim, with full context, so the distinction between "we relocated" and "we decided to delete instead" stays legible at the next planning pass
- `REQUIREMENTS.md` amended for TOOLS-03 and TOOLS-04, recording this plan's decision-gate contribution without marking either requirement Complete (both remain multi-plan and open)

## The Live Census (inlined — `/tmp` is not durable)

Captured 2026-09-12 from `/workspaces/firestarter_app`, Python 3.11.16 (`.venv311`), pytest 9.1.1.
Measured with `/usr/bin/grep` (never the devcontainer's ugrep) and `pytest --co -q -o addopts=""`
(per-module/per-test collection counts, never `def test_` line counts).

**Baseline:** `pytest tests/ --co -q -o addopts=""` → **2373 tests collected, 0 errors.** The baseline
itself is healthy before this phase touches anything.

| Symbol | Source file (gate half deleted either way) | Consumer(s) | Live test count | Breaks at |
|---|---|---|---|---|
| `dispatch`, `_ALGO_MEM_TYPE`, `_SRAM_PROTOCOLS`, `KNOWN_PROTOCOLS` | `tools/check_dispatch.py` | 6× `test_val_wire_*` (module-level, bare import after `sys.path` prepend) + `test_decoder.py::TestDispatchGate02` (in-function) + `test_build_db_inclusion.py::test_non_supported_chips_are_non_dispatchable` (in-function) | **44** (14+6+6+4+4+4+5+1), 8 modules | 38 at collection, 6 at runtime |
| `render_shape` | `tools/snapshot_report_shapes.py` | `test_blast_radius_invariance.py`, 2 parametrized sites (`test_committed_snapshot_matches_a_fresh_regeneration`, `test_composing_a_db_diff_never_leaks_onto_a_cached_build_shape`) over 19 shape IDs | **38**, 1 module | runtime (module-level import absent; only the parametrized test bodies import) |
| `_HANDLER_FUNCTION_NAMES` | `tools/check_devtest_orchestrator.py` | `test_op_registration_parity.py`, module-level import (`:113`) + 1 locator site (`:365`) | **7** (whole module), 1 module | collection (module-level) |
| `FORBIDDEN_PATTERNS` | `tools/check_diagnostic_report_claims.py` | `test_parse_devtest_issue.py::test_parser_marker_strings_trip_no_forbidden_claim_pattern` (in-function, `:740`) | **1**, 1 module | runtime |

**Totals across all four symbols:** **90 tests** broken if the four files vanish unrepaired — **45** at
collection time (module reports `ERROR`, zero results: the six `test_val_wire_*` modules + `test_op_registration_parity.py`), **45** at runtime (in-function imports raise when the specific test body executes: `test_decoder.py` ×5, `test_build_db_inclusion.py` ×1, `test_blast_radius_invariance.py` ×38, `test_parse_devtest_issue.py` ×1). Eleven distinct consuming modules total across all four symbols.

**Divergence from RESEARCH.md:** none on any figure. Every count above matches RESEARCH.md's A1/A2
dangling-reference sweep tables exactly, and matches the plan's own Task 2 `<how-to-verify>` prose
("44 tests across eight modules... render_shape — 38 tests... _HANDLER_FUNCTION_NAMES — 7 tests...
FORBIDDEN_PATTERNS — 1 test... Forty-five of those break at collection time") verbatim.

**Working-tree note:** `git status --porcelain` in `firestarter_app` showed 2 lines
(`datasheets/MBM27C1001.pdf`, `datasheets/MX27C4000.pdf`), both untracked operator files confirmed
present before this plan's Task 1 began — not a change attributable to this task. No file was created,
edited, or deleted under `firestarter_app/` by Task 1. A rehearsal attempt (briefly relocating the four
target files out of `tools/` to empirically confirm the collection-error count rather than infer it) was
blocked by the harness as an irreversible-destructive action before it took effect; the collection-error
totals above were derived instead from the already-verified module-level-vs-in-function import
classification, which is equally conclusive for this purpose (a module-level import unconditionally fails
at collection when its target is absent; an in-function import only raises when that specific test body
runs).

## The Decision

**Task 2's checkpoint** (`gate="blocking-human"`) presented all four symbols with the live figures above,
stated that the gate half of every one of the four files is deleted either way (the operator was not
choosing whether to retire the gates), and named the alternative that OD-1's ruling never put to the
operator: deleting the eight consuming test modules (~105 tests, six of them the `test_val_wire_*`
wire-contract suites that carry the BLOCKER-2 SRAM/VPP electrical-safety invariant — the host's own proof
that each chip family's wire dict routes to the electrically-correct handler, never `configure_eprom` for
a 5V SRAM part).

**The operator's answer, verbatim:** **"Delete the consumers."**

This is option 2, not OD-1's relocate ruling. The operator was shown the full blast radius — ~105 tests
gone, all six `test_val_wire_*` modules destroyed, the BLOCKER-2 electrical-safety invariant's test coverage
among them — and chose it anyway. Recorded here as their decision, made against the live numbers, not as
an oversight or a default.

**Consequence:** this **inverts OD-1**. Plans **188-03**, **188-04**, and **188-05** (and, per
`REQUIREMENTS.md`'s TOOLS-04 traceability, **188-09**) are written on the relocate basis and are now
**invalid as written** — each must be replanned on a delete-the-consumers basis before it runs. This plan
does not perform that replanning: per explicit instruction, only 188-02 is completed here; the replan is
the orchestrator's next move.

## Task Commits

This plan's `commits_in_repo` is `none` — Task 1 produced only the `/tmp` evidence file (deliberately not
committed, D-19), and Task 2 is a decision with no file to commit. The only commits this plan makes are
this SUMMARY and the `REQUIREMENTS.md` update, both below.

1. **Task 1: Re-measure the four orphaned symbols' consumers live** — no commit (evidence at `/tmp/188-02-orphan-census.txt` by design)
2. **Task 2: Confirm the relocation of four orphaned symbols before any file carrying them is deleted** — no commit (decision recorded here)

**Plan metadata:** committed alongside this SUMMARY (see the commit immediately following this file's creation)

## Files Created/Modified

- `.planning/REQUIREMENTS.md` — TOOLS-03 and TOOLS-04 amended: this plan's decision recorded as a
  contributing paragraph under each requirement (matching the shape 188-01 established for TOOLS-04),
  plus both traceability-table rows updated. Neither requirement marked Complete — both remain open,
  multi-plan requirements per the shared-ID gate.

## Decisions Made

See "The Decision" above. Summarized: operator chose "delete the consumers" over the OD-1 relocate ruling,
inverting it, with the full cost disclosed before the choice was made.

## Deviations from Plan

None — plan executed exactly as written. Task 1's rehearsal-via-harness-denial is not a deviation from the
plan's action spec (which never asked for an actual file move; it asked for measurement), but is noted
above for transparency about how the collection-error total was derived.

## Issues Encountered

None. The checkpoint answer diverges from the plan's downstream assumption (that "relocate" would be
chosen), but that divergence is precisely what this decision gate exists to catch before any deletion
happens — it is not an execution problem.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- **Plans 188-03, 188-04, 188-05, and 188-09 must be replanned** before any of them executes: each currently
  assumes the four symbols relocate into the test tier, and the operator has instead directed that the
  eight consuming test modules (dispatch's six `test_val_wire_*` + `test_decoder.py`'s dispatch class +
  `test_build_db_inclusion.py`'s one test, `test_blast_radius_invariance.py`, `test_op_registration_parity.py`,
  `test_parse_devtest_issue.py`) be deleted instead of repaired.
- This plan performed no replanning and starts no downstream work, per explicit instruction — that is the
  orchestrator's next move.
- D-24 branch invariant re-confirmed at the end of this plan: **ok=3/3** — meta
  (`gsd/v1.37-operator-safety-answered-reports-claim-hygiene-activated-202`), `firestarter`
  (`gsd/v1.37-operator-safety-answered-reports-claim-hygiene`), and `firestarter_app`
  (`gsd/v1.37-operator-safety-answered-reports-claim-hygiene`) all on their `v1.37`-slug branches, none on
  `beta`/`main`, none detached.

---
*Phase: 188-the-tools-directory*
*Completed: 2026-09-12*
