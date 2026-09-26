---
phase: 133-sdp-leg-mechanism
plan: 05
subsystem: testing
tags: [ast, ruff, mypy, gate, dev-test, chip_test.py, check_devtest_orchestrator]

# Dependency graph
requires:
  - phase: 133-sdp-leg-mechanism (plans 01-04)
    provides: "the final engine source (_dispatch_sdp arm 5, the cleanup registry drain) the clean-source GREEN leg is measured against"
provides:
  - "A fourth deny bucket in tools/check_devtest_orchestrator.py's AST visitor: bare except:, except Exception:, except BaseException:, and tuple forms containing either"
  - "A (basename, function)-scoped exemption table (_BROAD_EXCEPT_EXEMPTIONS) with exactly one row for chip_test.py's _sample, carrying a D-14 reason"
  - "Guard (a): _validate_exemption_table -- pure, argument-taking, rejects empty/whitespace reasons"
  - "Guard (b): _stale_exemption_row_violations -- fails when a scanned same-basename file no longer defines the exempted function"
  - "8 new tests (26 total in the paired module) proving each broad form RED, the exemption scoped (not global), both guards RED, and non-vacuity by deliberate mutation"
affects: ["134-plan-derived-sdp-oracle"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Enclosing-function-name stack pushed/popped in visit_FunctionDef/visit_AsyncFunctionDef, consulted only by visit_ExceptHandler -- minimal state added to an otherwise-stateless AST visitor"
    - "Exemption table as a committed (file, function) -> reason dict, validated by a pure function taking the table as a parameter (provable in-process, no env seam, no subprocess)"
    - "Stale-row guard wired into main() over the actually-scanned paths (post scanned-empty fail-closed check), not into the pure validator -- it needs parsed source"

key-files:
  created: []
  modified:
    - firestarter_app/tools/check_devtest_orchestrator.py
    - firestarter_app/tests/test_check_devtest_orchestrator.py

key-decisions:
  - "Rule and exemption landed in one commit (feb90f6) -- the rule alone turns the pre-existing clean-source leg RED against chip_test.py's real _sample handler, so they could not be split across commits without a transiently-RED gate"
  - "Exemption matching scoped on (os.path.basename(scanned_path), enclosing_function_name), never a global whitelist of the broad form -- proven by a dedicated leg (test_checker_exemption_keeps_clean_source_green) that plants the same shape under a different function name and confirms it is still flagged"
  - "Stale-row guard (b) is intentionally independent of visit_ExceptHandler -- it fires on structural absence of the named function, not on whether that function contains a broad handler, so it correctly stayed GREEN when visit_ExceptHandler was deliberately deleted during the non-vacuity proof"

patterns-established:
  - "A fourth-bucket extension to an existing multi-bucket AST gate: declare the list in __init__, extend it identically across every existing per-leg scan block, add one _print_bucket arm, extend the PASS-line counter -- verified by grep parity across bucket names"

requirements-completed: []  # This plan supplies LEG-11's second, independent (build-time gate) proof. LEG-11 is shared with 133-01/02/07 and is NOT ticked here -- see requirement_id_fence. Plan 133-07 is the only plan permitted to mark requirements complete.

coverage:
  - id: D1
    description: "Fourth AST deny bucket flags bare except:, except Exception:, except BaseException:, and tuple forms containing either, across all three scan legs"
    requirement: "LEG-11"
    verification:
      - kind: unit
        ref: "tests/test_check_devtest_orchestrator.py#test_checker_exits_nonzero_on_planted_broad_except"
        status: pass
      - kind: unit
        ref: "tests/test_check_devtest_orchestrator.py#test_checker_exits_nonzero_on_planted_broad_except_variants[base_exception]"
        status: pass
      - kind: unit
        ref: "tests/test_check_devtest_orchestrator.py#test_checker_exits_nonzero_on_planted_broad_except_variants[tuple_form]"
        status: pass
      - kind: unit
        ref: "tests/test_check_devtest_orchestrator.py#test_checker_exits_nonzero_on_planted_broad_except_variants[bare_except]"
        status: pass
    human_judgment: false
  - id: D2
    description: "One (basename, function)-scoped exemption for chip_test.py's _sample keeps the real, clean sources GREEN; the same shape under a different function name is still flagged"
    requirement: "LEG-11"
    verification:
      - kind: unit
        ref: "tests/test_check_devtest_orchestrator.py#test_checker_exemption_keeps_clean_source_green"
        status: pass
    human_judgment: false
  - id: D3
    description: "Guard (a): exemption rows with an empty or whitespace-only reason fail; the real table passes (positive control)"
    requirement: "LEG-11"
    verification:
      - kind: unit
        ref: "tests/test_check_devtest_orchestrator.py#test_exemption_table_empty_reason_fails"
        status: pass
    human_judgment: false
  - id: D4
    description: "Guard (b): a stale exemption row (exempted function renamed away in a same-basename scanned file) fails the gate"
    requirement: "LEG-11"
    verification:
      - kind: unit
        ref: "tests/test_check_devtest_orchestrator.py#test_checker_exemption_stale_row_fails"
        status: pass
      - kind: unit
        ref: "tests/test_check_devtest_orchestrator.py#test_exemption_table_rows_all_resolve"
        status: pass
    human_judgment: false
  - id: D5
    description: "Fail-closed-on-empty-scan property re-proven reachable after the fourth bucket's wiring"
    verification:
      - kind: manual_procedural
        ref: "cd firestarter_app && FIRESTARTER_DEVTEST_SRC=/nonexistent/a.py FIRESTARTER_DEVTEST_HANDLER=/nonexistent/b.py FIRESTARTER_DEVTEST_SUBMIT=/nonexistent/c.py python3 tools/check_devtest_orchestrator.py -> exit 1, 'FAIL: no orchestrator source files found to scan'"
        status: pass
    human_judgment: false
  - id: D6
    description: "firestarter/chip_test.py is byte-unchanged by this plan (engine untouched, no narrowing of _sample)"
    verification:
      - kind: other
        ref: "git -C firestarter_app diff --stat HEAD~2 -- firestarter/  (empty output)"
        status: pass
    human_judgment: false

# Metrics
duration: 11min
completed: 2026-08-04
status: complete
---

# Phase 133 Plan 05: Broad-Except Deny Bucket + Guarded Exemption Table Summary

**Fourth AST deny bucket in `tools/check_devtest_orchestrator.py` catches `except Exception:`/`except BaseException:`/bare `except:`/tuple forms -- gated GREEN on real, clean source via one `(file, function)`-scoped exemption (D-14) with two independently mutation-proven guards (empty-reason, stale-row).**

## Performance

- **Duration:** 11 min (10:01:25Z -> 10:12:10Z, per commit timestamps)
- **Tasks:** 2
- **Files modified:** 2 (`tools/check_devtest_orchestrator.py`, `tests/test_check_devtest_orchestrator.py`)

## Accomplishments

- Added `_BROAD_EXCEPT_NAMES`, `_BROAD_EXCEPT_EXEMPTIONS`, `_validate_exemption_table`, `_stale_exemption_row_violations`, an enclosing-function-name stack (`visit_FunctionDef`/`visit_AsyncFunctionDef`), and `visit_ExceptHandler` to `_OrchestratorDenyVisitor`, wired into all three existing scan legs (`chip_test.py` full scan, `cli_handlers.py` name-scoped handler scan, `submit.py` full scan) in `main()`.
- The rule and its exemption landed in a single commit (`feb90f6`) -- confirmed by direct observation that reverting only the exemption row flips the pre-existing `test_checker_exits_zero_on_clean_source` leg RED (see Mutation Proofs below), which is exactly the transient-RED failure mode the plan required avoiding.
- Added 8 new test functions (3 of them parametrized to 3 cases each) to `tests/test_check_devtest_orchestrator.py`, bringing the module from 18 to 26 tests, all shelling out through the existing `_run_checker(...)` subprocess helper except the one pure-function guard-(a) leg.
- Proved non-vacuity by two deliberate, restored mutations against the real working tree (not merely asserted): removing the exemption row, and deleting `visit_ExceptHandler` entirely. Both observed failures are recorded verbatim below.

## Task Commits

1. **Task 1: Add the broad-handler deny-rule, enclosing-function context, and guarded exemption table** - `feb90f6` (feat)
2. **Task 2: Prove the bucket with real subprocess REDs plus both exemption guards** - `1d18691` (test)

**Plan metadata:** This SUMMARY commit (meta repo)

## Files Created/Modified

- `firestarter_app/tools/check_devtest_orchestrator.py` - fourth deny bucket (`broad_except_violations`), exemption table + both guards, docstring updates (three buckets -> four)
- `firestarter_app/tests/test_check_devtest_orchestrator.py` - 8 new tests (11-16 in the Coverage: numbering, with #12 parametrized to 3 cases), Coverage: docstring list extended

## Decisions Made

- **Rule + exemption, one commit.** The deny-rule alone fires RED against `chip_test.py`'s pre-existing `_sample` broad handler (its `# noqa: BLE001` is inert -- `BLE` is not in this repo's ruff `select`). Landing them separately would have carried a RED gate across a commit boundary, which this project's discipline forbids. Verified directly (see Mutation Proofs).
- **Exemption scoped on `(os.path.basename(scanned_path), enclosing_function_name)`**, never a bare function-name match or a global whitelist of the broad form. `test_checker_exemption_keeps_clean_source_green` proves this by planting the identical shape under a *different* function name and confirming it is still flagged.
- **Guard (a) is pure and argument-taking** (`_validate_exemption_table(table)`), reading no module global -- provable entirely in-process, the one leg in the module that does not shell out, because no env seam or import-time binding is involved.
- **Guard (b) is wired into `main()` over the actually-scanned paths**, after the scanned-empty fail-closed check, because it needs parsed source (not just the table) to detect a renamed-away function.
- **Guard (b) is intentionally independent of `visit_ExceptHandler`.** During the non-vacuity mutation proof, deleting `visit_ExceptHandler` correctly left `test_checker_exemption_stale_row_fails` passing -- the stale-row guard checks structural presence of the named function, not whether that function's body contains a broad handler. This is correct, not a gap: the two guards protect different failure modes (an unreasoned/rotted exemption vs. an unmonitored broad-except site).

## Mutation Proofs (non-vacuity, seen not assumed)

All four mutations below were applied to the real working tree, observed to fail, then reverted and reverified GREEN (`diff` confirmed byte-identical restoration; full 26-test module reverified passing after each restore).

**1. Fail-closed-on-empty-scan re-proof** (all three seams pointed at nonexistent paths):
```
$ FIRESTARTER_DEVTEST_SRC=/nonexistent/a.py FIRESTARTER_DEVTEST_HANDLER=/nonexistent/b.py FIRESTARTER_DEVTEST_SUBMIT=/nonexistent/c.py python3 tools/check_devtest_orchestrator.py
FAIL: no orchestrator source files found to scan (checked: ['/nonexistent/a.py', '/nonexistent/b.py', '/nonexistent/c.py']) -- the gate cannot vacuously pass with nothing scanned
exit=1
```

**2. Exemption removed** (`_BROAD_EXCEPT_EXEMPTIONS` replaced with `{}`), then ran the pre-existing clean-source leg:
```
$ pytest tests/test_check_devtest_orchestrator.py -k test_checker_exits_zero_on_clean_source -q
FAILED tests/test_check_devtest_orchestrator.py::test_checker_exits_zero_on_clean_source
AssertionError: checker exited 1 on clean source.
stdout:
FAIL: 1 broad exception handler(s):
  .../firestarter/chip_test.py:1273: broad exception handler (except Exception:)
1 failed, 25 deselected in 0.12s
```
Restored; `test_checker_exits_zero_on_clean_source` reverified passing (1 passed, 25 deselected).

**3. `visit_ExceptHandler` deleted entirely**, then ran the four broad-except-dependent legs:
```
$ pytest tests/test_check_devtest_orchestrator.py -k "planted_broad_except or planted_broad_except_variants or exemption_stale or exemption_keeps_clean_source_green" -q
FAILED tests/test_check_devtest_orchestrator.py::test_checker_exits_nonzero_on_planted_broad_except
FAILED tests/test_check_devtest_orchestrator.py::test_checker_exits_nonzero_on_planted_broad_except_variants[base_exception]
FAILED tests/test_check_devtest_orchestrator.py::test_checker_exits_nonzero_on_planted_broad_except_variants[tuple_form]
FAILED tests/test_check_devtest_orchestrator.py::test_checker_exits_nonzero_on_planted_broad_except_variants[bare_except]
FAILED tests/test_check_devtest_orchestrator.py::test_checker_exemption_keeps_clean_source_green
5 failed, 1 passed, 20 deselected in 0.44s
```
The 1 passed was `test_checker_exemption_stale_row_fails` -- correctly independent of `visit_ExceptHandler` (see Decisions Made). Restored (`diff` confirmed byte-identical); full module reverified 26 passed.

**4. Stale-row leg's own observed output** (fixture: real `chip_test.py` source with `def _sample(` -> `def _sample_renamed(`, `altered != original` asserted first):
```
$ FIRESTARTER_DEVTEST_SRC=<fixture with chip_test.py basename, _sample renamed> python3 tools/check_devtest_orchestrator.py
FAIL: 1 broad exception handler(s):
  /tmp/chip_test.py:1273: broad exception handler (except Exception:)
FAIL: 1 stale broad-except exemption row(s):
  STALE exemption row ('chip_test.py', '_sample'): a scanned file named 'chip_test.py' no longer defines a function named '_sample' -- the exemption has rotted and is silently permitting an omission
exit=1
```
Both the plain broad-except violation AND the stale-row violation fire together here -- expected, since renaming the function away also un-exempts its (now differently-named) handler.

## Exemption Row Reason String (exact wording, D-14)

```
D-14: _sample (firestarter/chip_test.py) is a best-effort diagnostic hook
invoked with an opaque caller-supplied callable (the sampler) that may
raise literally anything; its swallow-all behaviour is its documented
contract, and narrowing it would change shipped production behaviour
reachable through _make_sampler in cli_handlers.py, which criterion 4
forbids.
```
(Line-wrapped here for readability; the committed string is a single Python string literal in `_BROAD_EXCEPT_EXEMPTIONS`, keyed on `("chip_test.py", "_sample")`.)

## Verification Evidence

- `python3 tools/check_devtest_orchestrator.py` -> exit 0, `PASS: scanned ../firestarter/chip_test.py, ../firestarter/cli_handlers.py, ../firestarter/submit.py; 0 VPP-set, 0 raw-wire-dict, 0 --force, 0 broad-except; firmware untouched (host-only, asserted)`
- `pytest tests/test_check_devtest_orchestrator.py -q` -> 26 passed (up from 18)
- `pytest tests/ -q` (full suite) -> 1331 passed, 30 snapshots passed (up from 1323 at wave-4 close; +8 new tests, 0 regressions)
- `ruff check tools/check_devtest_orchestrator.py tests/test_check_devtest_orchestrator.py` -> All checks passed; `ruff format --check` on both -> clean (both files were auto-reformatted once during authoring and reverified clean)
- `tools/ci_replica_venv.sh` (numpy-free py3.11 CI replica): `mypy errors: 32 (watermark: 35)` -- **unchanged from wave-4 close, watermark not moved**; `checked 123 source files` (was 122 at Phase 132 close; no new file was added by this plan, the +1 reflects the replica venv's own environment, not a new source file); coverage `81.84%` -- unchanged; `CI-REPLICA: PASS`
- `git -C firestarter_app diff --stat HEAD~2 -- firestarter/` -> empty output, confirmed twice (after each task) -- the engine is byte-unchanged by this plan
- `grep -c 'subprocess.run' tests/test_check_devtest_orchestrator.py` -> `1` (unchanged) -- the existing `_run_checker` helper was reused for every new leg except the one pure-function guard-(a) leg, as required

## Deviations from Plan

None - plan executed exactly as written. No auto-fixes were needed; the module's existing three-bucket shape and the house exemption-table idiom (`_HANDLER_FUNCTION_NAMES`, `_EXEMPT_FW_TO_HOST`) were followed directly.

## Issues Encountered

- Two comments containing the literal text `# noqa: BLE001` (describing the *inert* pre-existing suppression comment on `chip_test.py`'s `_sample`) tripped ruff's own noqa-directive parser as an invalid noqa code, because ruff scans raw comment lines for the pattern regardless of prose intent. Reworded the comment to say "inert BLE001-suppression comment" instead of reproducing the literal `# noqa: BLE001` string inside a `#`-comment. No behavior change; purely a wording fix to keep `ruff check` clean. (Not logged as a Rule 1/2/3 deviation -- it is an authoring correction to satisfy the plan's own `ruff check` acceptance criterion, not a bug in shipped logic.)

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- LEG-11's build-time gate proof is complete for this plan's scope; the requirement itself remains open (shared with 133-01/02/07) per the requirement fence -- **not ticked here**.
- `.planning/REQUIREMENTS.md` was not modified, consistent with the fence.
- Waves 1-4 artifacts (frozen precedence matrix, `_dispatch_sdp` arm-5 position, the `results`-name-prohibited drain) were not touched; confirmed no edits to `firestarter/chip_test.py` or `tests/test_chip_test_sdp_leg.py`.
- Ready for Plan 06 (LEG-15 op-registration parity) and Plan 07 (requirement ticking + phase close).

## Self-Check: PASSED

- FOUND: `firestarter_app/tools/check_devtest_orchestrator.py`
- FOUND: `firestarter_app/tests/test_check_devtest_orchestrator.py`
- FOUND: `.planning/phases/133-sdp-leg-mechanism/133-05-SUMMARY.md`
- FOUND commit `feb90f6` (submodule): feat(133-05) broad-except deny bucket + exemption table
- FOUND commit `1d18691` (submodule): test(133-05) non-vacuity proofs
- FOUND commit `dd8b299` (meta repo): docs(133-05) this summary

---
*Phase: 133-sdp-leg-mechanism*
*Completed: 2026-08-04*
