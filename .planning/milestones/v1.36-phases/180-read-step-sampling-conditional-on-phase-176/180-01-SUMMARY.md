---
phase: 180-read-step-sampling-conditional-on-phase-176
plan: 01
subsystem: testing
tags: [ast, pytest, tdd, chip_test, eprom_operations, prune-08, dev-test]

requires:
  - phase: 176-transport-instrumentation-connect-cost-measurement-partially
    provides: MEAS-01's per-board-class per-connect cost (176-MEASUREMENT.md §4a/§4b/§6/§7)
  - phase: 177-evidence-gated-read-back
    provides: test_readback_inventory.py's ast-census machinery and planted-mutation idiom, and the 177-READBACK-INVENTORY.md closing-document form this plan mirrors
provides:
  - Two structural + two behavioural pins on roadmap criterion 3 (the read step's verdict is the last full read's result, never anything derived from the read-vs-read comparison)
  - A structural, static pin on the one-connect-per-read premise (Ruling 1 / D-02)
  - 180-PRUNE-08-CLOSURE.md's verdict and connect-arithmetic sections
affects: [180-02, 180-03]

actuals:
  tokens: 6100
  tasks: 3
  commits: 6
  plan_head_before: 2bd3db0a6d7075c7ce1383c76f45ef604710c348

tech-stack:
  added: []
  patterns:
    - "ast-based structural pins over grep, resolving module source from the target module's own __file__ (never the test file's directory)"
    - "planted-mutation RED proofs on in-memory source strings, anchor-uniqueness asserted before mutation, no fixture files"
    - "tokenize COMMENT-token delta gate in place of the regex phase_added_comments leg, to catch trailing comments the regex cannot see"

key-files:
  created:
    - .planning/phases/180-read-step-sampling-conditional-on-phase-176/180-PRUNE-08-CLOSURE.md
    - .planning/phases/180-read-step-sampling-conditional-on-phase-176/evidence/180-01-verdict-pin-red.txt
    - .planning/phases/180-read-step-sampling-conditional-on-phase-176/evidence/180-01-behavioural-legs.txt
    - .planning/phases/180-read-step-sampling-conditional-on-phase-176/evidence/180-01-one-connect-pin.txt
  modified:
    - firestarter_app/tests/test_readback_inventory.py
    - firestarter_app/tests/test_chip_test.py

key-decisions:
  - "Committed as test(180-01) throughout — no product-source implementation followed any RED phase, because these are pins on already-correct existing behaviour (D-06, Ruling 1), not new features. workflow.tdd_mode is false project-wide (advisory), so the planted-mutation RED transcripts on disk are the D-07 evidence rather than a separate gsd_run check tdd-red-evidence gate run."
  - "The one-connect mutant extends read_eprom's with header with a second _operation_context item bound to a throwaway name (self._operation_context(eprom_name, eprom_data_dict, cmd) as _extra_context) — syntactically valid Python the ast module parses without executing, so the undefined cmd name at that call site is harmless: the mutant is never run, only parsed."
  - "Imported eprom_operations as a module alias (from firestarter import eprom_operations as eo) alongside the existing chip_test alias, per the plan's own stated alternative, rather than reaching through EpromOperator.__module__."

requirements-completed: []

coverage:
  - id: D1
    description: "_dispatch_read's verdict= expression is pinned to the exact name set [VERDICT_BAD, VERDICT_OK, last_ok] (D-06 leg 3, roadmap criterion 3)"
    requirement: "PRUNE-08"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_readback_inventory.py#test_read_verdict_expression_reads_only_the_last_full_read_result"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_readback_inventory.py#test_a_planted_divergence_term_in_the_verdict_reddens_the_pin"
        status: pass
    human_judgment: false
  - id: D2
    description: "A failing last full read yields VERDICT_BAD; a failing first read with a passing last read yields VERDICT_OK, both proven through the real run_plan (D-06 legs 1-2, roadmap criterion 3 positive half)"
    requirement: "PRUNE-08"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test.py#test_read_step_last_run_failure_yields_bad"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test.py#test_read_step_first_run_failure_with_passing_last_run_yields_ok"
        status: pass
    human_judgment: false
  - id: D3
    description: "One operator.read_eprom call is pinned to exactly one _operation_context, which connects through _setup_operation/find_and_connect and disconnects inside a non-empty finally block (Ruling 1, D-02's structural half)"
    requirement: "PRUNE-08"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_readback_inventory.py#test_one_read_eprom_call_costs_exactly_one_connect"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_readback_inventory.py#test_a_planted_second_operation_context_in_read_eprom_reddens_the_pin"
        status: pass
    human_judgment: false
  - id: D4
    description: "180-PRUNE-08-CLOSURE.md states the verdict and the connect arithmetic (10 connects vs 1, enumerated block list, N = log2(size) - 6) with both per-board-class medians and no modelled figure"
    requirement: "PRUNE-08"
    verification:
      - kind: other
        ref: "grep checks in Task 1's <verify> block against 180-PRUNE-08-CLOSURE.md (headings, block list, load-bearing sentence, both medians, absence of KB/s and 2.56)"
        status: pass
    human_judgment: true
    rationale: "The closing document's argument is a prose/arithmetic judgment call (does it honestly represent D-01 through D-11's dispositions, does it avoid overstating evidence) that the automated grep checks only spot-check structurally; a human should confirm the argument reads as intended before the phase closes."

duration: 55min
completed: 2026-09-08
status: complete
---

# Phase 180 Plan 01: Read-Step Verdict and One-Connect Pins Summary

**Five additive pytest pins (two structural, two behavioural, one docstring/module update) close roadmap criterion 3 and Ruling 1's structural premise, and open `180-PRUNE-08-CLOSURE.md` on the 10-vs-1 connect argument — zero product-source or firmware lines changed.**

## Performance

- **Duration:** 55 min
- **Started:** 2026-09-08T14:06:00Z (approx, first task read)
- **Completed:** 2026-09-08T15:01:18Z
- **Tasks:** 3
- **Files modified:** 5 (2 test modules, 1 closing document, 2 evidence transcripts — 3 total evidence files)

## Accomplishments

- **D-06 leg 3 (structural):** `test_read_verdict_expression_reads_only_the_last_full_read_result` pins `_dispatch_read`'s `verdict=` keyword to the exact sorted name set `["VERDICT_BAD", "VERDICT_OK", "last_ok"]` via `ast`, asserted as full-set equality never membership. `test_a_planted_divergence_term_in_the_verdict_reddens_the_pin` proves it observed RED against an in-memory mutant whose verdict also consults `divergence`.
- **D-06 legs 1-2 (behavioural):** `test_read_step_last_run_failure_yields_bad` and `test_read_step_first_run_failure_with_passing_last_run_yields_ok` prove, through the real `run_plan` (never `_dispatch_read` directly), that the read step's verdict is the LAST full read's return value — a failing last read is BAD regardless of the first read's result, and a failing first read with a passing last read is OK.
- **Ruling 1 / D-02's structural half:** `test_one_read_eprom_call_costs_exactly_one_connect` pins, by `ast`, that `read_eprom`'s `with` header opens exactly one `_operation_context`, which connects through `_setup_operation`/`find_and_connect` on entry and disconnects via `_disconnect_programmer` inside a non-empty `finally` block on exit. `test_a_planted_second_operation_context_in_read_eprom_reddens_the_pin` proves it observed RED against a planted second connect.
- **`180-PRUNE-08-CLOSURE.md`** opened with `## The verdict` (measured, not worth doing — D-01, citing `176-MEASUREMENT.md` §4a/§4b/§6/§7, never blending the two board-class medians) and `## The connect arithmetic` (the enumerated 64 KiB block list, `N = log2(size) - 6`, the size table, the three 64 KiB reference parts, the structural one-connect premise, and the load-bearing "10 connects where the sweep it replaces costs 1" sentence) — with no figure from `dev-test-sequence-cost-model.md` published (D-04, Ruling 3).
- Three evidence transcripts recorded under `evidence/`, each showing `pin_at_head=GREEN` / `pin_at_planted=RED` for its structural pin, plus the four-row behavioural matrix for the two legs and their controls.

## Task Commits

Each task's test-file change was committed atomically inside `firestarter_app` (branch `gsd/v1.36-dev-test-fidelity`), then its meta-repo artifacts + gitlink advance committed inside `/workspaces` (branch `gsd/v1.36-dev-test-fidelity-planning`):

1. **Task 1: verdict pin + closing document** — app `f0eb002` (test-only), meta `2d0b048e` (closure doc + evidence + gitlink)
2. **Task 2: behavioural legs** — app `07c6dab` (test-only), meta `a5a80d15` (evidence + gitlink)
3. **Task 3: one-connect pin** — app `3ca6195` (test-only), meta `ec82f258` (evidence + gitlink)

**Plan metadata:** committed separately, see final `docs(180-01)` commit.

_Note: no `feat`/`refactor` commits exist for this plan — every task is an additive pin on already-existing, already-correct behaviour; there is no product-code implementation step to separate from the test commit._

## Files Created/Modified

- `firestarter_app/tests/test_readback_inventory.py` — +4 test functions (2 pins × 2 legs each: assertion + planted-mutant RED), 2 helpers (`_verdict_expression_names`, `_read_eprom_connect_shape`), 2 sibling constants (`_VERDICT_ANCHOR`, `_CONTEXT_ANCHOR`), 1 sibling resolver (`_operations_source`), module docstring updated (4 anti-vacuity legs, both new pins named, one-connect pin's static-pin ceiling stated). 10 tests total (was 6).
- `firestarter_app/tests/test_chip_test.py` — +2 test functions (`test_read_step_last_run_failure_yields_bad`, `test_read_step_first_run_failure_with_passing_last_run_yields_ok`), placed between :2172 and the (now-shifted) fingerprint test. `-k read_step` selects 4 tests (was 2).
- `.planning/phases/180-read-step-sampling-conditional-on-phase-176/180-PRUNE-08-CLOSURE.md` — new. `## The verdict` and `## The connect arithmetic` sections.
- `.planning/phases/180-read-step-sampling-conditional-on-phase-176/evidence/180-01-verdict-pin-red.txt`, `180-01-behavioural-legs.txt`, `180-01-one-connect-pin.txt` — new evidence transcripts.

## Decisions Made

See `key-decisions` in frontmatter. In short: pure `test(180-01)` commits throughout (no implementation step exists for these pins); the one-connect mutant is syntactically valid-but-never-executed Python so an undefined name inside it is harmless; `eprom_operations` reached via a module alias rather than through `EpromOperator.__module__`.

## Deviations from Plan

None — plan executed exactly as written. One line-number note, not a deviation: `test_write_step_attaches_fingerprint_with_region_start_addr_base` in `test_chip_test.py` moved from `:2177` (as cited by the plan and by 180-PATTERNS.md) to `:2239` after Task 2's two new tests (62 lines) were inserted immediately before it, per the plan's own placement instruction. All other line numbers the plan cited (`chip_test.py:2767` `_dispatch_read`, `:2851` `_read_region`, `:2141`/`:2166` the two existing siblings; `eprom_operations.py:454/499/515/531/545/547/548/550/552/896/905/911-912` the connect chain and the `_CONTEXT_ANCHOR` lines) were verified exact to the line before use, with no drift.

## Rationale That Would Otherwise Have Been a Source Comment

Per `/workspaces/CLAUDE.md`'s hard no-comments rule, every rationale for this plan's new code lives in a docstring already (each new test states its claim and its ceiling; the one-connect pin's docstring states plainly that it is a *static* pin, proving shape rather than a runtime trace). No rationale needed a home outside a docstring or this SUMMARY — nothing was omitted from source for lack of a place to put it.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `180-02` (the seed amendment) and `180-03` (requirement marking + phase seal) can proceed; `180-PRUNE-08-CLOSURE.md` now exists with its verdict and arithmetic sections, and `test_readback_inventory.py`/`test_chip_test.py`'s D-06/Ruling-1 gates are live and RED-proven, so plan 03's gate battery has real, non-vacuous pins to run against.
- `PRUNE-08`'s requirements-ledger flip is deliberately **not** done here — it is shared across all three plans in this phase (`180-02-PLAN.md` and `180-03-PLAN.md` both declare `requirements: [PRUNE-08]`), and `requirements.ready-ids` confirmed it is not yet ready to mark complete (0/1 ready) because sibling plans 02 and 03 have not yet produced their SUMMARY.md. This is the correct, gated behaviour, not an oversight.
- No blockers.

---
*Phase: 180-read-step-sampling-conditional-on-phase-176*
*Completed: 2026-09-08*

## Self-Check: PASSED

All created files verified present on disk (closing document, three evidence transcripts,
this SUMMARY, both modified test modules). All six task commits verified present in their
respective repos' `git log --oneline --all` (app: `f0eb002`, `07c6dab`, `3ca6195`; meta:
`2d0b048e`, `a5a80d15`, `ec82f258`). All plan-level `<verification>` commands re-run and
passing: `test_readback_inventory.py` 10 passed, `test_chip_test.py -k read_step` 4 passed,
`phase_added_comments=0`, both submodules porcelain-clean.
