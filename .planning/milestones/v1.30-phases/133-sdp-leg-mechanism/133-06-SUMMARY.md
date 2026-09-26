---
phase: 133-sdp-leg-mechanism
plan: 06
subsystem: testing
tags: [ast, parity-gate, chip_test.py, op-registration, pytest, ruff, mypy]

# Dependency graph
requires:
  - phase: 133-sdp-leg-mechanism (plans 01-05)
    provides: "the final engine source (OP_SDP_LOCK/OP_SDP_UNLOCK, _SDP_OPS,
      _dispatch_sdp arm 5, the _DESTRUCTIVE_OPS/_MULTI_RUN_OPS asymmetries,
      the cleanup-registry drain) this parity gate measures and polices"
provides:
  - "tests/test_op_registration_parity.py -- the phase's second and final
      new source file: a fail-closed op-registration parity gate (LEG-15)"
  - "_POLICED_REGISTRIES (6) + _DECLARED_NON_REGISTRIES (6) -- the measured
      registry census, replacing ROADMAP criterion 5's inherited 'eight'"
  - "_assert_op_parity(registries, exemptions, ops, context) -- pure,
      argument-taking membership-or-reasoned-exemption assertion"
  - "_op_names_referenced_in(func_name, source) -- AST derivation of a
      function-scoped registry's op coverage, resolved transitively through
      referenced frozenset constants"
  - "Four D-12 guards (empty/whitespace/None reason; stale op/registry row;
      declared-count mismatch) plus the inversion guard (zero-op-vocabulary
      re-measurement of every declared non-registry) plus a non-vacuity leg"
affects: [133-07, "134-plan-derived-sdp-oracle"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Registry map passed as an ARGUMENT to the parity assertion (not read
        from a module global) -- lets the non-vacuity leg exercise the
        real assertion code against an altered in-memory copy"
    - "AST-derived registry membership resolved TRANSITIVELY through
        referenced frozenset constants (an `if op in _MULTI_RUN_OPS:` arm
        counts as covering every _MULTI_RUN_OPS member), rather than a
        second hand-maintained list"
    - "Inversion guard: a declared non-registry's 'zero op vocabulary' claim
        is itself re-measured via AST every run, not assumed permanently
        true -- the genuinely valuable leg P-23's original census had no
        equivalent for"

key-files:
  created:
    - firestarter_app/tests/test_op_registration_parity.py
  modified: []

key-decisions:
  - "Comprehensive (op, registry) exemption table (24 rows), not just the
      four SDP-specific groups the plan text named by example -- the
      must_haves and _assert_op_parity's literal contract ('for every
      (op, registry) pair... membership OR a matching exemption') is a
      full 9-op x 6-registry cross product, so every non-mutating op's
      structural absence from _DESTRUCTIVE_OPS/_MULTI_RUN_OPS/_SDP_OPS/
      _dispatch_multi_run also needed a reasoned row, not just the SDP
      ops' deliberate omissions. Documented as a measured finding, not a
      deviation from spirit -- the four plan-named groups are THIS
      phase's real, newly-introduced omissions; the other 20 rows are
      pre-existing structural non-memberships this new gate is the first
      thing to ever write down explicitly."
  - "_dispatch_step needs ZERO exemptions -- measured: all 9 ops resolve
      into it via its four arms plus the _MULTI_RUN_OPS/_SDP_OPS
      transitive resolution, so it is the one registry with full
      coverage. Asserted at module import time so a future measurement
      drift here is caught immediately."
  - "Single commit for both plan tasks (task 1's parity model/main leg and
      task 2's four guards/non-vacuity/SDP-targeted leg) -- the two are
      inseparable acceptance criteria of one fail-closed gate (the plan's
      own words: 'the four guards are therefore acceptance criteria in
      their own right, not implementation detail'); a commit boundary
      between them would have carried a genuinely-incomplete (still
      partially fail-open) gate."

requirements-completed: []
# LEG-15 is named in this plan's frontmatter because this plan delivers
# ALL of LEG-15's mechanism (the parity gate itself, all four guards, the
# inversion guard, and the non-vacuity leg) -- but per the requirement
# fence, plan 133-07 is the ONLY plan permitted to tick any requirement
# box. .planning/REQUIREMENTS.md was NOT touched by this plan (verified
# below). LEG-15 remains open until 133-07 ticks it against this plan's
# green tests.

coverage:
  - id: D1
    description: "Measured registry census (6 policed + 6 declared
      non-registries) built and documented, replacing ROADMAP criterion
      5's inherited 'eight previously fail-open registries'"
    requirement: "LEG-15"
    verification:
      - kind: unit
        ref: "tests/test_op_registration_parity.py::test_declared_registry_count_matches"
        status: pass
      - kind: other
        ref: "module docstring MEASURED registry census section, cross-checked against chip_test.py/diagnostic_report.py/cli_handlers.py/tools/parse_devtest_issue.py/tools/check_devtest_orchestrator.py source"
        status: pass
    human_judgment: false
  - id: D2
    description: "_assert_op_parity: every (op, registry) pair across the
      9-op vocabulary and 6 policed registries asserts membership or a
      reasoned exemption; fails naming every offending pair"
    requirement: "LEG-15"
    verification:
      - kind: unit
        ref: "tests/test_op_registration_parity.py::test_every_op_is_registered_or_exempt"
        status: pass
    human_judgment: false
  - id: D3
    description: "Four D-12 guards: (a) empty/whitespace/None reason
      fails with a positive control; (b) a stale op/registry exemption
      row fails, proven by planting both kinds; (c) declared registry
      counts must equal measured counts"
    requirement: "LEG-15"
    verification:
      - kind: unit
        ref: "tests/test_op_registration_parity.py::test_exemption_empty_reason_fails"
        status: pass
      - kind: unit
        ref: "tests/test_op_registration_parity.py::test_stale_row_fails"
        status: pass
      - kind: unit
        ref: "tests/test_op_registration_parity.py::test_declared_registry_count_matches"
        status: pass
    human_judgment: false
  - id: D4
    description: "Inversion guard: every declared non-registry is
      re-measured via AST to still carry zero op vocabulary; non-vacuity
      leg proves the main assertion can actually fail"
    requirement: "LEG-15"
    verification:
      - kind: unit
        ref: "tests/test_op_registration_parity.py::test_non_registry_still_has_no_ops"
        status: pass
      - kind: unit
        ref: "tests/test_op_registration_parity.py::test_altered_registry_copy_fails_parity_non_vacuous"
        status: pass
      - kind: unit
        ref: "tests/test_op_registration_parity.py::test_sdp_ops_are_accounted_in_every_policed_registry"
        status: pass
    human_judgment: false

# Metrics
duration: ~55min
completed: 2026-08-04
status: complete
---

# Phase 133 Plan 06: Op-Registration Parity Gate (LEG-15) Summary

**A fail-closed op-registration parity gate (`tests/test_op_registration_parity.py`, the phase's second and final new source file): 6 measured policed registries checked op-by-op via an argument-taking `_assert_op_parity`, 6 measured declared non-registries whose zero-op-vocabulary claim is re-derived via AST every run (the inversion guard), four D-12 guards, and a non-vacuity leg -- replacing ROADMAP criterion 5's inherited "eight previously fail-open registries" with a measured breakdown.**

## Performance

- **Duration:** ~55 min
- **Completed:** 2026-08-04
- **Tasks:** 2 (delivered in one commit -- see Decisions Made)
- **Files created:** 1 (`firestarter_app/tests/test_op_registration_parity.py`)

## Accomplishments

- Built `_POLICED_REGISTRIES`: the 3 real op-keyed frozensets in `chip_test.py` (`_DESTRUCTIVE_OPS`, `_MULTI_RUN_OPS`, `_SDP_OPS`) read directly from the imported module, plus 3 function-scoped sites (`_dispatch_step`'s five arms, `derive_plan`'s `Step(op=...)` construction, `_dispatch_multi_run`'s inner run-loop branches) derived via a new `_op_names_referenced_in(func_name, source)` AST helper that resolves registry-constant references TRANSITIVELY to their real members.
- Built `_DECLARED_NON_REGISTRIES`: 6 units carrying zero op vocabulary or keyed on a different axis -- `_RAN_VERDICTS`/`count_applicable` (verdict-keyed), `dedup_fingerprint` and the `DiagnosticReport` renderer (both generic over `StepResult.op`), `tools/parse_devtest_issue.py` (measured to have zero op-string constants, correcting P-23's row 8), `_ALWAYS_WRITES_NOTICE` (a prose string), and `check_devtest_orchestrator.py`'s `_HANDLER_FUNCTION_NAMES` (function names, a materially different axis).
- Wrote a comprehensive `_OP_REGISTRY_EXEMPTIONS` table (24 rows: the 4 SDP-specific groups the plan named by example, plus 20 pre-existing structural non-memberships this new gate is the first thing to ever write down) -- see Measured Values below for the exact breakdown and Decisions Made for why the table is larger than the plan's illustrative examples.
- Implemented `_assert_op_parity` (pure, registry-map-as-argument) and the main leg `test_every_op_is_registered_or_exempt`.
- Implemented all four D-12 guards plus the inversion guard plus the non-vacuity leg plus a targeted SDP-ops disposition-pinning leg (7 test functions total).
- No `@requires_fw`, no firmware-presence import, no firmware path read -- verified the module runs with zero skips under `FIRESTARTER_FW_ROOT` pointed at an empty directory.
- Full suite green: 1338 passed (up from 1331; 7 new tests), 30 snapshots unchanged. `ruff check`/`ruff format --check` clean on the new file and on `tests/` as a whole. CI's own scope (`tools/ci_replica_venv.sh`) fully green: mypy 33 errors (watermark 35, checked 124 source files), coverage 81.84%.

## Task Commits

Both plan tasks landed in a single commit in the submodule (`firestarter_app`) on `gsd/v1.30-sdp-surface-retirement` -- see Decisions Made for why:

1. **Tasks 1+2: build the parity model, main leg, all four guards, inversion guard, non-vacuity leg, and SDP-targeted leg** -- `57e8eb5` (test)

**Plan metadata:** this SUMMARY's own commit follows this document (meta repo).

## Files Created/Modified

- `firestarter_app/tests/test_op_registration_parity.py` (new, 822 lines) -- `_POLICED_REGISTRIES`, `_POLICED_REGISTRY_COUNT`, `_DECLARED_NON_REGISTRIES`, `_DECLARED_NON_REGISTRY_COUNT`, `_OP_REGISTRY_EXEMPTIONS`, `_assert_op_parity`, `_op_names_referenced_in`, `_stale_exemption_rows`, `_measure_op_vocabulary` + its AST helpers (`_docstring_constant_ids`, `_count_op_vocabulary_references`, `_find_named_node`), `_PARITY_CONTEXT`, and 7 test functions. No production file touched (`git diff --stat -- firestarter/ tools/` is empty, verified).

## Decisions Made

- **Comprehensive 24-row exemption table, not just the plan's 4 illustrative groups.** The plan's `_OP_REGISTRY_EXEMPTIONS` action text names 4 groups (both SDP ops vs `derive_plan`, vs `_MULTI_RUN_OPS`, vs `_dispatch_multi_run`; `OP_SDP_UNLOCK` vs `_DESTRUCTIVE_OPS`) -- but `_assert_op_parity`'s own literal contract, and the must_haves' "for every op string ... and every policed registry" wording, is a full 9-op x 6-registry cross product. Measured: of the 54 pairs, 30 are real memberships and 24 are non-members needing a reasoned row. The 4 plan-named groups are this phase's real, newly-introduced omissions (SDP-specific, deliberate); the other 20 rows are pre-existing structural non-memberships (e.g. `id`/`read`/`blank-check` were never candidates for `_DESTRUCTIVE_OPS`) that this new gate is the first thing in the codebase to ever write down explicitly, rather than leave as an unstated, un-auditable assumption. This is a measured finding, documented per the plan's own "if yours differs, yours wins" instruction -- not a deviation from the gate's intent.
- **`_dispatch_step` needs zero exemptions.** Measured via the AST-derived registry: all 9 ops resolve into it (arms 1-4 cover id/blank-check/read directly plus every `_MULTI_RUN_OPS` member transitively; arm 5 covers every `_SDP_OPS` member transitively). A module-level assertion pins this so a future measurement drift is caught immediately rather than silently accepted.
- **Both plan tasks in one commit.** The plan's task 1 (parity model + main leg) and task 2 (four guards + non-vacuity + SDP-targeted leg) build the SAME single new file, and the plan's own text says "the four guards are therefore acceptance criteria in their own right, not implementation detail" -- a commit boundary between task 1 and task 2 would have shipped a genuinely-incomplete, still partially fail-open gate (no stale-row protection, no mandatory-reason enforcement, no proof the assertion can fail) as if it were a complete unit. One commit keeps the gate atomic: it either lands complete or not at all.
- **`_op_names_referenced_in` takes `source: str`, not a path** (per the plan's explicit instruction) -- reads `chip_test.py`'s real on-disk source once via `inspect.getsourcefile` + `Path.read_text`, then parses/walks it. This is the same helper used to build the three function-scoped `_POLICED_REGISTRIES` entries; no second re-implementation of the walk exists anywhere in the module.
- **AST over regex, concretely justified in the module docstring:** `_dispatch_step`'s own docstring contains the literal substring `"blank-check"` in prose describing its arms -- a text-level regex for the op VALUE would count that as a reference; identifier-level `ast.Name` matching (`OP_BLANK_CHECK`) does not, because a hyphen is not a valid Python identifier character. The inversion guard additionally excludes docstring `Constant` nodes by AST position for the same reason, one level down (a docstring describing an op in prose is not a vocabulary reference).

## Measured Registry Census (per `<CRITICAL_measure_the_census_do_not_inherit_it>`)

**ROADMAP criterion 5's "eight previously fail-open registries" is measurably wrong.** Re-measured against this session's working tree (2026-08-04, `firestarter_app` @ commit `57e8eb5`'s parent):

**6 policed registries** (a new op must join one of these, or carry a reasoned exemption):
| Registry | Source | Members (measured) |
|---|---|---|
| `_DESTRUCTIVE_OPS` | `chip_test.py`, real frozenset | `{write, write-partial, erase, sdp-lock}` (4) |
| `_MULTI_RUN_OPS` | `chip_test.py`, real frozenset | `{write, write-partial, erase, verify}` (4) |
| `_SDP_OPS` | `chip_test.py`, real frozenset | `{sdp-lock, sdp-unlock}` (2) |
| `_dispatch_step` | AST-derived (transitive) | all 9 ops -- zero exemptions needed |
| `derive_plan` | AST-derived (transitive) | `{id, read, blank-check, write, write-partial, verify, erase}` (7) |
| `_dispatch_multi_run` | AST-derived (transitive) | `{write, write-partial, erase, verify}` (4) |

**6 declared non-registries** (zero op vocabulary, or a different axis):
| Unit | Locator | Why |
|---|---|---|
| `_RAN_VERDICTS`/`count_applicable` | `chip_test.py`, function | verdict-keyed, not op-keyed |
| `dedup_fingerprint` | `diagnostic_report.py`, function | generic over `StepResult.op` |
| `diagnostic_report.py` renderer | `diagnostic_report.py`, class `DiagnosticReport` | generic over `StepResult.op` |
| `tools/parse_devtest_issue.py` | whole module | ZERO op-string constants (corrects P-23 row 8) |
| `_ALWAYS_WRITES_NOTICE` | `cli_handlers.py`, constant | fixed prose, zero op vocabulary |
| `_HANDLER_FUNCTION_NAMES` | `check_devtest_orchestrator.py`, constant | different axis -- function names, not ops |

**Net:** of P-23's original ten-row table, 6 rows are real policed registries (one MORE than P-23 counted -- `_dispatch_multi_run`'s inner branches were missing from it entirely), 3 rows carry no op vocabulary whatsoever, and 1 row (`_HANDLER_FUNCTION_NAMES`) is keyed on a materially different axis. ROADMAP criterion 5's "eight" undercounts the real policed set by one AND overcounts the declared-non-registry set by miscategorizing genuinely-empty/different-axis rows as "fail-open registries" when there was never anything a new op could be omitted from in the first place.

**Every exemption's exact reason string** is committed verbatim in `_OP_REGISTRY_EXEMPTIONS` in the source file; the 4 SDP-specific groups cite D-01/D-03/D-04/D-11/LEG-09 by name, the 20 structural rows cite the frozenset's own in-source safety-argument comment (`_DESTRUCTIVE_OPS`'s SWEEP-03 comment) or the relevant dispatch-arm mechanism (D-04's zero-added-branching-cost sentinel).

## Mutation Proofs (verbatim observed failure messages, per plan_specific_warnings)

All three were applied to the real working tree, observed to fail, then reverted and reverified byte-identical + green.

**1. Real frozenset mutation** -- `_DESTRUCTIVE_OPS` temporarily narrowed to `frozenset({OP_WRITE_PARTIAL, OP_ERASE, OP_SDP_LOCK})` (removing `OP_WRITE`) in `firestarter/chip_test.py`:
```
$ pytest tests/test_op_registration_parity.py -k test_every_op_is_registered_or_exempt -o addopts="" -q
...
E           AssertionError: Before Phase 121, an unmapped op fell through to operator.erase_eprom() and reported OK (RESEARCH Pitfall 1a). An op added to the vocabulary but missing from a registry it must join -- with no membership AND no reasoned exemption -- is that defect class returning. LEG-15 converts every such fail-open registry into one fail-closed gate.
E             - op 'write' is neither a member of registry '_DESTRUCTIVE_OPS' nor covered by a reasoned exemption
FAILED tests/test_op_registration_parity.py::test_every_op_is_registered_or_exempt
```
Reverted (`diff` against the pre-mutation copy showed zero difference); re-ran green (1 passed).

**2. Declared non-registry acquiring op vocabulary** -- a real `if plan.steps and plan.steps[0].op == OP_SDP_LOCK:` line planted into `count_applicable`'s body (after its docstring, as real code, not inside the docstring) in `firestarter/chip_test.py`:
```
$ pytest tests/test_op_registration_parity.py -k test_non_registry_still_has_no_ops -o addopts="" -q
...
E       AssertionError: A declared non-registry has acquired op vocabulary -- PROMOTE it to _POLICED_REGISTRIES, do not loosen this guard. A permanent exemption on a unit that starts switching on op strings is exactly the fail-open shape LEG-15 exists to remove.
E         _RAN_VERDICTS/count_applicable: measured 1 op-vocabulary reference(s)
FAILED tests/test_op_registration_parity.py::test_non_registry_still_has_no_ops
```
Reverted (`diff` byte-identical); re-ran green (1 passed).

**3. Blanked exemption reason** -- `("id", "_DESTRUCTIVE_OPS")`'s reason temporarily replaced with `""` in `tests/test_op_registration_parity.py` itself, exercising the leg's own positive control:
```
$ pytest tests/test_op_registration_parity.py -k test_exemption_empty_reason_fails -o addopts="" -q
...
E           AssertionError: Before Phase 121, an unmapped op fell through to operator.erase_eprom() and reported OK (RESEARCH Pitfall 1a). An op added to the vocabulary but missing from a registry it must join -- with no membership AND no reasoned exemption -- is that defect class returning. LEG-15 converts every such fail-open registry into one fail-closed gate.
E             - op 'id' is neither a member of registry '_DESTRUCTIVE_OPS' nor covered by a reasoned exemption
FAILED tests/test_op_registration_parity.py::test_exemption_empty_reason_fails
```
Reverted (`diff` byte-identical); re-ran green (7 passed, full module).

## Verification Evidence

- `pytest tests/test_op_registration_parity.py -o addopts="" -q` -> `7 passed` (zero skips)
- `FIRESTARTER_FW_ROOT=$(mktemp -d) pytest tests/test_op_registration_parity.py -o addopts="" -q` -> `7 passed` (zero skips, proving the gate runs in the standalone-CI condition)
- `pytest tests/ -o addopts="" -q` (full suite) -> `1338 passed` (up from 1331 at wave-5 close; +7 new tests, 0 regressions), 30 snapshots unchanged
- `ruff check tests/test_op_registration_parity.py` / `ruff format --check tests/test_op_registration_parity.py` -> both exit 0
- `ruff check tests/` / `ruff format --check tests/` (task-scoped commands) -> both exit 0
- `pytest tests/test_skip_census.py -x` -> `5 passed` (no new skip reason introduced)
- `git -C firestarter_app diff --stat -- firestarter/ tools/` -> empty output (this plan is test-only)
- `git -C firestarter_app diff --name-only HEAD~1` -> `tests/test_op_registration_parity.py` only
- `tools/ci_replica_venv.sh` full 5-leg run: Leg 1 exit 0, Leg 2 (numpy absent) exit 0, Leg 3 (`ruff check firestarter/ tests/` + `format --check`) exit 0, Leg 4 (mypy watermark) `Found 33 errors in 13 files (checked 124 source files)` -- `mypy errors: 33 (watermark: 35)`, Leg 5 (coverage) exit 0, `Total coverage: 81.84%`. `CI-REPLICA: PASS`.
- `grep -c 'requires_fw' tests/test_op_registration_parity.py` -> `0`; `grep -c 'fw_presence' tests/test_op_registration_parity.py` -> `0`
- `inspect.signature(_op_names_referenced_in)` -> `(func_name: str, source: str) -> frozenset[str]`; `_assert_op_parity` takes `registries` as its first parameter (not a module global read).

## Deviations from Plan

### Auto-fixed / Documented Issues

**1. [Rule-adjacent — scope, documented not auto-fixed] `ruff check firestarter/ tools/ tests/` (the plan's own `<verification>` command) fails on 3 pre-existing, unrelated files in `tools/`**
- **Found during:** running the plan's phase-wide verification command.
- **Issue:** `tools/audit_coverage_matrix.py`, `tools/catalog/codegen.py`, `tools/catalog/codegen_vectors.py` each carry pre-existing `ruff` findings (unsorted import blocks, one `UP031` percent-format).
- **Root cause confirmed pre-existing:** `git log` shows these files were last touched in Phase 63/70 (commits `9cbcf1e`, `e9dc01f`, `e8132b3`), long before this phase. Reproduced with `git stash -u` (this plan's new file removed) -- the same 4 errors appear.
- **Also confirmed out of CI's actual scope:** `tools/ci_replica_venv.sh`'s Leg 3 runs `ruff check firestarter/ tests/` -- it never includes `tools/` at all.
- **Action:** NOT fixed (out of this task's scope per the executor's scope-boundary rule). Logged to `.planning/phases/133-sdp-leg-mechanism/deferred-items.md`. `tests/test_op_registration_parity.py` itself, and `tests/` as a whole, are both ruff-clean.

**2. [Rule-adjacent — scope, documented not auto-fixed] mypy error count rose from 32 to 33 (still under the 35 watermark) due to an incidental import side effect**
- **Found during:** running `tools/ci_replica_venv.sh` after committing.
- **Issue:** `tests/test_op_registration_parity.py` imports `tools.check_devtest_orchestrator` (to read its `_HANDLER_FUNCTION_NAMES` constant), which makes mypy transitively type-check that module for the first time (its only other consumer, `tests/test_check_devtest_orchestrator.py`, shells out via `subprocess` and never imports it). This surfaced one PRE-EXISTING type error from plan 133-05's `visit_ExceptHandler`: `tools/check_devtest_orchestrator.py:442: error: Incompatible types in assignment (expression has type "str | None", variable has type "str") [assignment]`.
- **Root cause confirmed:** `git stash -u` shows 32 errors/123 checked without this plan's file, 33 errors/124 checked with it; `mypy ... | grep test_op_registration_parity` is empty in both runs -- the new file itself contributes zero errors.
- **Action:** NOT fixed (`tools/check_devtest_orchestrator.py` is not a file this plan's task list touches; `git diff --name-only HEAD~1` confirms only the new test file changed). The count remains safely under the watermark (33 <= 35, headroom 3 -> 2); the watermark itself is unmoved. Logged to `deferred-items.md` with the exact fix a future plan touching that file should make.

---

**Total deviations:** 2 documented, neither fixed (both out of this task's scope; both logged to `deferred-items.md`; neither affects this plan's own acceptance criteria or CI's actual gate).
**Impact on plan:** None -- the gate itself is complete, green, and proven capable of failing three independent ways.

## Issues Encountered

None beyond the two documented deviations above.

## User Setup Required

None -- no external service configuration required.

## Next Phase Readiness

- LEG-15's mechanism is fully delivered and green: the parity gate, all four D-12 guards, the inversion guard, and the non-vacuity leg. The requirement itself remains open (per the requirement fence) -- **not ticked here**.
- `.planning/REQUIREMENTS.md` was NOT modified by this plan (verified: `git diff --name-only HEAD -- .planning/REQUIREMENTS.md` in the meta repo shows no change).
- Waves 1-5 artifacts (frozen precedence matrix, `_dispatch_sdp` arm-5 position, the `results`-name-prohibited drain, the broad-except deny bucket + exemption table) were not touched; confirmed via `git diff --stat -- firestarter/ tools/` (empty) in the submodule.
- Ready for Plan 07 (requirement ticking + phase close) -- this plan's 7 green tests are the evidence 133-07 should cite for LEG-15.
- Two pre-existing, out-of-scope findings logged to `.planning/phases/133-sdp-leg-mechanism/deferred-items.md` for a future phase to sweep (unrelated `tools/` ruff debt from Phase 63/70; one pre-existing `check_devtest_orchestrator.py` mypy type-narrowing fix, newly visible but not newly introduced).
- No blockers.

---
*Phase: 133-sdp-leg-mechanism*
*Completed: 2026-08-04*

## Self-Check: PASSED

- FOUND: `firestarter_app/tests/test_op_registration_parity.py`
- FOUND: `.planning/phases/133-sdp-leg-mechanism/133-06-SUMMARY.md`
- FOUND: `.planning/phases/133-sdp-leg-mechanism/deferred-items.md`
- FOUND commit: `57e8eb5` (submodule `firestarter_app`)
- FOUND commit: `8c70793` (meta repo)
