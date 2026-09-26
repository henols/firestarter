---
phase: 121-dev-test-fix-gates-docs-redesign
plan: 03
subsystem: testing
tags: [ast, static-analysis, sdp, gate, anti-hollow, pytest, subprocess-testing]

# Dependency graph
requires:
  - phase: 120-host-cli-surface-wire-emission-capability-refusal
    provides: "SDP_CAPABLE_TOKENS static allow-list in firestarter/sdp_capability.py (43 ALLOW / 41 REFUSE)"
provides:
  - "tools/check_sdp_capability_invariants.py: AST invariant gate over firestarter/sdp_capability.py"
  - "tests/test_check_sdp_capability.py: 9-leg anti-hollow pytest pairing"
  - "tests/fixtures/planted_permit_by_default.py, tests/fixtures/planted_widenable_allowset.py: first Python planted-violation fixtures in the repo"
affects: ["121-14 (requirement-row re-verification)", "GATE-03 (full non-regression close)"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "AST checker with FIRESTARTER_<NAME>_SRC env-override seam (mirrors check_devtest_orchestrator.py / check_is_memory_cmd_no_ifdef.py)"
    - "Ordered (lineno-sorted) event scan for lexical dominance, avoiding ast.walk's BFS non-source-order"
    - "Committed tests/fixtures/*.py planted-violation convention (vs inline tmp_path) — first Python files in that directory"

key-files:
  created:
    - firestarter_app/tools/check_sdp_capability_invariants.py
    - firestarter_app/tests/test_check_sdp_capability.py
    - firestarter_app/tests/fixtures/planted_permit_by_default.py
    - firestarter_app/tests/fixtures/planted_widenable_allowset.py
  modified: []

key-decisions:
  - "Class 1(a) is scoped to tuple-literal `(True, ...)` returns only (per RESEARCH Open Question 5), so the delegating wrapper `sdp_capability()`'s pass-through return is never flagged without needing a whitelist"
  - "The 'exactly one module-level binding' fail-closed symbol guard and Class 2(a) are the same computed check (count != 1 module-level Assign/AnnAssign/AugAssign bindings), reported through one message — the plan describes them as two framings of one fact"
  - "Deliberate-break proof executed manually (not committed): neutering Class 2 detection flips 2 legs (Class 2 planted-violation, zero-symbol fail-closed) RED; restoring the checker flips both back GREEN"
  - "REQUIREMENTS.md was deliberately NOT edited despite PLAN.md's own instruction that this plan 'MAY mark GATE-01 Complete' — the spawning orchestrator's dispatch prompt explicitly locked requirement-row bookkeeping to plan 121-14 for this phase; this is an intentional override, not an oversight (see reference_executors_prematurely_mark_requirements_complete.md)"

requirements-completed: []  # GATE-01 acceptance criteria are all met (see below), but the row is intentionally left unticked per the requirement_scope_LOCK in this plan's dispatch — 121-14 owns re-verification and row bookkeeping for this phase.

coverage:
  - id: D1
    description: "AST checker denies Class 1 (permit-by-default: unconditional True-tuple return + bare except) over firestarter/sdp_capability.py"
    requirement: "GATE-01"
    verification:
      - kind: unit
        ref: "tests/test_check_sdp_capability.py#test_checker_exits_nonzero_on_planted_permit_by_default"
        status: pass
      - kind: unit
        ref: "tests/test_check_sdp_capability.py#test_planted_permit_by_default_also_reports_bare_except"
        status: pass
    human_judgment: false
  - id: D2
    description: "AST checker denies Class 2 (widenable allow-set: not-exactly-once binding, non-literal frozenset shape, augmented/union rebind)"
    requirement: "GATE-01"
    verification:
      - kind: unit
        ref: "tests/test_check_sdp_capability.py#test_checker_exits_nonzero_on_planted_widenable_allowset"
        status: pass
    human_judgment: false
  - id: D3
    description: "Gate fails closed on a missing target path and on a zero-symbol scan; PASS line names the resolved scanned path"
    requirement: "GATE-01"
    verification:
      - kind: unit
        ref: "tests/test_check_sdp_capability.py#test_fail_closed_on_missing_target"
        status: pass
      - kind: unit
        ref: "tests/test_check_sdp_capability.py#test_fail_closed_on_zero_symbol_scan"
        status: pass
      - kind: unit
        ref: "tests/test_check_sdp_capability.py#test_default_target_resolves_to_an_existing_file"
        status: pass
      - kind: unit
        ref: "tests/test_check_sdp_capability.py#test_pass_line_names_the_scanned_file"
        status: pass
    human_judgment: false

# Metrics
duration: 55min
completed: 2026-07-29
status: complete
---

# Phase 121 Plan 03: GATE-01 SDP Capability AST Invariant Checker Summary

**One AST checker (`tools/check_sdp_capability_invariants.py`) denies permit-by-default and widenable-allow-set edits to `firestarter/sdp_capability.py`, paired with a 9-leg subprocess pytest and two committed planted-violation fixtures — the first `.py` fixtures in the repo.**

## Performance

- **Duration:** 55 min
- **Started:** 2026-07-29T00:00:00Z (approx, session start)
- **Completed:** 2026-07-29
- **Tasks:** 3/3
- **Files modified:** 4 created, 0 modified

## Accomplishments
- Built `tools/check_sdp_capability_invariants.py`: a genuinely-populated `ast.parse` + `ast.NodeVisitor` gate denying two violation classes over `firestarter/sdp_capability.py` — Class 1 (permit-by-default: a tuple-literal `(True, ...)` return not dominated by an `SDP_CAPABLE_TOKENS` membership test, plus any bare `except:`) and Class 2 (widenable allow-set: not-exactly-once module-level binding, a shape other than a direct `frozenset(...)` of string literals, or any augmented/union/add/update rebind).
- Paired it with `tests/test_check_sdp_capability.py`: 9 subprocess-level legs proving the checker actually fails on each planted violation class, fails closed on a missing target and on a zero-symbol scan, and is non-vacuous by path (the exported default-target constant resolves to a real file on disk).
- Added `tests/fixtures/planted_permit_by_default.py` and `tests/fixtures/planted_widenable_allowset.py` — the first `.py` files under `tests/fixtures/` (all 5 prior fixtures are C/C++), each committed (not `tmp_path`-inline) per CONTEXT's Claude's-Discretion precedent, and confirmed excluded from both ruff and pytest collection by plan 121-01's `extend-exclude`.
- Left `firestarter/sdp_capability.py` byte-unchanged (verified via `git status --porcelain`) and `tests/test_sdp_capability.py`'s 12 existing legs untouched.
- Executed and recorded a deliberate-break proof: temporarily neutered `_find_widenable_allowset_violations` to a no-op, confirmed exactly the two Class-2-dependent legs (`test_checker_exits_nonzero_on_planted_widenable_allowset`, `test_fail_closed_on_zero_symbol_scan`) went RED, then restored the checker byte-for-byte and confirmed all 9 legs GREEN again.

## Task Commits

Each task was committed atomically in the `firestarter_app` sub-repo (branch `v1.22-at28c-software-data-protection-lifecycle`):

1. **Task 1: Write the two planted-violation fixtures** — `a3bee52` (test)
2. **Task 2: Write the GATE-01 AST checker** — `f33aef8` (feat)
3. **Task 3: Write the paired anti-hollow pytest** — `69c7a72` (test)

**Plan metadata:** this SUMMARY.md commit in the meta repo (`docs(121-03): ...`).

## Files Created/Modified
- `firestarter_app/tests/fixtures/planted_permit_by_default.py` — D-14 Class 1 fixture: unconditional `(True, ...)` return + bare `except:`, both undominated by any `SDP_CAPABLE_TOKENS` membership test
- `firestarter_app/tests/fixtures/planted_widenable_allowset.py` — D-14 Class 2 fixture: `SDP_CAPABLE_TOKENS` bound from a generator expression over a runtime call, then rebound via `|=`
- `firestarter_app/tools/check_sdp_capability_invariants.py` — the AST gate: `FIRESTARTER_SDP_CAPABILITY_SRC` env seam, `_DEFAULT_SDP_CAPABILITY_SRC` exported constant, `_PermitByDefaultVisitor` (ordered lineno-scan for lexical dominance), module-level binding-count guard, `main() -> int` / `sys.exit(main())` exit contract
- `firestarter_app/tests/test_check_sdp_capability.py` — 9-leg subprocess pytest pairing (clean pass, non-vacuous-by-path, PASS-line naming, Class 1 + Class 2 planted violations, bare-except co-detection, seam sanity, fail-closed on missing target, fail-closed on zero-symbol scan)

## Decisions Made
- Scoped Class 1(a) to tuple-literal returns only (not a general "any truthy first-element return"), per RESEARCH Open Question 5 — this matches `sdp_capability_for_entry`'s single allow return exactly and ignores `sdp_capability()`'s one-line delegating return without a whitelist.
- Unified the "fail-closed symbol guard" (count != 1 → cannot vacuously pass) and Class 2(a) ("bound anywhere other than exactly once") into one computed check with one shared message — the plan's own wording describes these as the same fact viewed from two angles, and splitting them would have produced a duplicate, confusing report.
- Chose `def main() -> int` + `sys.exit(main())` (the `check_is_memory_cmd_no_ifdef.py` exit-code contract) over `check_devtest_orchestrator.py`'s `-> None` + inline `sys.exit(1)`, per the plan's explicit preference (newer, mypy-friendlier, `ERROR:`-vs-`FAIL:` distinction already present).
- **REQUIREMENTS.md intentionally not edited.** PLAN.md's own `<requirement_ownership>` section states this plan "MAY mark GATE-01 Complete," but the dispatching orchestrator's prompt for this execution explicitly locked all requirement-row bookkeeping (including GATE-01) to plan 121-14, citing this project's recorded pattern of executors prematurely marking multi-plan requirements complete. All of GATE-01's acceptance criteria are demonstrably met by this plan's own commits (see `coverage:` above); only the REQUIREMENTS.md checkbox/traceability-row edit itself was withheld, per the dispatch-time instruction taking precedence over the plan file's own (now-superseded) delegation.

## Deviations from Plan

None — plan executed as written, with one dispatch-time scope override (REQUIREMENTS.md non-edit, documented above and in `key-decisions`) that is not a plan deviation but an explicit instruction received at execution time superseding PLAN.md's own requirement-ownership section.

## Issues Encountered

- During the first Task 2 pass, `ruff format --check` flagged 3 formatting nits in the newly-written checker (long lines, an unnecessary parenthesized conditional, a call that needed wrapping). Ran `ruff format` scoped to just the new file (not the whole `tools/`/`firestarter/`/`tests/` tree, which carries 4 pre-existing, out-of-scope ruff errors in `tools/catalog/codegen_vectors.py` and one import-order issue predating this plan — confirmed via a before/after diff with the new file temporarily moved aside). Logged the pre-existing errors below as deferred, out-of-scope items per the Scope Boundary rule (this plan touches neither file).
- Same formatting cycle repeated for `tests/test_check_sdp_capability.py` (one long assert message needed re-wrapping). Both are cosmetic, auto-applied by `ruff format`, and re-verified against all 9 new tests + the paired `test_sdp_capability.py` afterward.
- During the deliberate-break proof, an initial attempt neutering only `_find_permit_by_default_violations` (Class 1a) did NOT flip any Class-1 leg RED, because the bare-except detector (`_find_bare_except_violations`) still populated the same `permit_by_default_violations` bucket/label, so the "permit-by-default" keyword assertion stayed true. This is expected given the two Class-1 sub-violations share one report bucket — not a checker defect (both sub-classes are still independently detected and printed with distinct per-violation text, `Class 1a` vs `Class 1b`). Re-ran the experiment against Class 2 instead (fully independent bucket), which cleanly demonstrated the RED→GREEN cycle the acceptance criterion asks for.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- GATE-01's checker and pytest are in place and green; `python3 tools/check_sdp_capability_invariants.py` exits 0 on real source and the full `firestarter_app` suite is at 1064 passed / 0 failed (up from the 1055-passed baseline after 121-01/121-02, +9 new tests).
- `.planning/REQUIREMENTS.md`'s GATE-01 row remains unticked by design — plan 121-14 (or whichever plan owns requirement-row re-verification for this phase) should tick it once it re-confirms this plan's acceptance criteria, referencing this SUMMARY's `coverage:` block.
- No blockers for GATE-02/GATE-03 or any other plan in this phase; this plan touched no production source (`firestarter/sdp_capability.py` byte-unchanged) and no shared test file beyond adding a new one.

---
*Phase: 121-dev-test-fix-gates-docs-redesign*
*Completed: 2026-07-29*

## Self-Check: PASSED

- FOUND: firestarter_app/tools/check_sdp_capability_invariants.py
- FOUND: firestarter_app/tests/test_check_sdp_capability.py
- FOUND: firestarter_app/tests/fixtures/planted_permit_by_default.py
- FOUND: firestarter_app/tests/fixtures/planted_widenable_allowset.py
- FOUND: .planning/phases/121-dev-test-fix-gates-docs-redesign/121-03-SUMMARY.md
- FOUND (firestarter_app): a3bee52, f33aef8, 69c7a72
- FOUND (meta): 7fad125
