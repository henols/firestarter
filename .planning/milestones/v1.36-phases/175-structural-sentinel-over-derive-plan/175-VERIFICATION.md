---
phase: 175-structural-sentinel-over-derive-plan
verified: 2026-09-04T15:30:00Z
status: passed
score: 4/4 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 175: Structural Sentinel over `derive_plan` Verification Report

**Phase Goal:** It becomes structurally impossible for a plan to emit a write with no verify behind
it, or to silently drop an unsupported step's diagnostic record — proven RED against a planted
counter-example before it is asked to license Phase 177's change.

**Verified:** 2026-09-04
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (Roadmap Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | A structural test over `derive_plan` output fails when fed a deliberately planted counter-example plan containing a write with no verify — proving the predicate is not vacuously true | ✓ VERIFIED | `test_planted_counter_plan_with_no_verify_is_flagged` (hand-built plan). Independently re-derived: stripping the verify step from a real shipped plan (`M8720`/`full`) via a fresh Python session produces `[(2, 'write', 'no supported, field-matching verify in the block')]`, while the unmodified plan produces `[]`. `evidence/175-01-anti-vacuity-red-green.txt` W1 shows the predicate weakened to return `[]` unconditionally turns 10 real tests RED (genuine pytest tracebacks with real chip names, not prose) |
| 2 | Sweeping the predicate across every `full`- and `partial`-scope plan the shipped database can produce reports zero write-without-verify violations | ✓ VERIFIED | `test_no_shipped_plan_emits_a_write_without_a_verify` asserts corpus size == 1354 before asserting zero violations. Independently re-ran `pytest tests/test_derive_plan_structural_sentinel.py` in a fresh py3.11 venv: 31/31 passed |
| 3 | The predicate is anchored to the module's own operation-type constants, so a future op type omitted from the closure list cannot silently escape the check | ✓ VERIFIED | `REQUIRES_VERIFY = frozenset({chip_test.OP_WRITE, chip_test.OP_WRITE_PARTIAL})` is a literal frozenset — confirmed by direct grep of the source, not derived by subtraction (D-01's explicit rejection honored). `module_op_constants()` discovers all `OP_*` via `vars(chip_test)` at runtime. `test_a_fourteenth_op_fails_the_partition_closed` monkeypatches a 14th `OP_*` constant onto the live module and asserts `assert_total_partition` raises — independently re-run, passes |
| 4 | Unsupported steps remain present in `Plan.steps` with an NA verdict rather than being dropped — verified by a whole-database sweep counting `StepResult` entries before/after, zero steps removed | ✓ VERIFIED | Two independent proofs, both required (D-10): (a) execution half — `test_derive_plan_no_drop_sweep.py` runs all 1,354 plans through the real `run_plan`, asserts `alignment_violations == ()` (16,248 results for 16,248 steps) AND separately `na_verdict_violations == ()` (9,304/9,304 unsupported steps carry `VERDICT_NA`); (b) frozen half — `tests/fixtures/plan_shapes.json` + `test_plan_shapes_drift.py` pins the `(op, supported)`-grain shape of all 677 chips, proven able to fail via 5 independently-observed non-zero exits (`evidence/175-03-plan-shapes-drift.txt`). Independently re-ran both modules (6/6 + 6/6 = 12/12 passed) |

**Score:** 4/4 roadmap success criteria verified (0 present-but-behavior-unverified)

### Plan-Level Must-Haves Cross-Check

| Must-have (source plan) | Status | Evidence |
|---|---|---|
| D-01/D-06 fail-closed 13-op partition, `REQUIRES_VERIFY` literal not derived by subtraction (175-01) | ✓ VERIFIED | `test_op_census_is_thirteen`, `test_op_vocabulary_is_totally_partitioned` — re-run, pass. `frozenset(...)` literal confirmed via grep |
| D-02 predicate anchored to production `cycle_block_bounds`, never re-derived (175-01, 175-02) | ✓ VERIFIED | `write_verify_violations` and `erase_blank_check_violations` each call `chip_test.cycle_block_bounds(plan.steps)` exactly once |
| D-03 unsupported verify is not an oracle (175-01) | ✓ VERIFIED | `test_an_unsupported_verify_is_not_an_oracle` + corpus-wide `test_an_unsupported_verify_flags_every_write_bearing_plan` (1,354/1,354 sensitive) |
| D-04 field-matching (write_region, region_policy, cycle_payload) (175-01) | ✓ VERIFIED | `test_a_field_skewed_verify_is_not_an_oracle` (3 sub-cases) + corpus-wide `test_a_region_skewed_verify_flags_every_write_bearing_plan` |
| D-05 erase→blank-check kept as a separately-named leg, presence not supportedness (175-02) | ✓ VERIFIED | `erase_blank_check_violations` distinct function; 608 live-erase plans, 0 violations; 162-plan/81-chip 28C carve-out pinned by count AND single reason string, both independently re-confirmed in evidence |
| D-12 UV write-scope ceiling at both `derive_plan` and handler level (175-02) | ✓ VERIFIED | `uv_policy_violations`, `uv_blank_check_order_violations` (540 UV plans, 0 violations both directions) + `test_resolve_write_scope_returns_partial_for_every_uv_row` sweeps the real `cli_handlers._resolve_write_scope` over all 677 names, both `interactive` values, 0 disagreements with `Plan.is_uv` |
| D-10 frozen half: committed artifact + generator + drift test, no skip marker (175-03) | ✓ VERIFIED | `plan_shapes.json` (677 chips, 8 families), `measure_plan_shapes.py` validates-before-emit, `test_plan_shapes_drift.py` has 0 skip markers (grep-confirmed) and re-runs clean (6/6) |
| D-10 execution half: alignment AND NA-verdict, not alignment alone (175-04) | ✓ VERIFIED | Both `alignment_violations` and `na_verdict_violations` implemented as separate predicates, both swept and both proven sensitive at 40/40 on `SENSITIVITY_SLICE` |
| Child-suite timeout raised 180s→420s, only that literal + docstring changed (175-04) | ✓ VERIFIED | `grep -n timeout tests/test_skip_census.py` shows `timeout=420` at line 244; independently re-ran `test_skip_census.py`, 5/5 passed in 173.45s (well inside the 420s cap) |
| Zero production diff, zero re-key, PRUNE-05/06 marked Complete (175-05) | ✓ VERIFIED | `git -C firestarter_app status --porcelain firestarter/` empty; `git -C firestarter status --porcelain` empty; `git diff c134530 -- chip_database.json` empty; `test_blast_radius_invariance.py` + `test_rekey_ledger.py` re-run 114/114 passed; REQUIREMENTS.md shows both `[x]` and both traceability rows `Complete` |

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `firestarter_app/tests/plan_corpus.py` | Shared corpus surface | ✓ VERIFIED | 146 lines, `EpromDatabase(skip_local_override=True)`, 746 rows → 677 names → 1,354 plans confirmed by direct execution |
| `firestarter_app/tests/test_derive_plan_structural_sentinel.py` | Write→verify + erase→blank-check + UV ceiling predicates | ✓ VERIFIED | 1,065 lines, 31 tests, re-run 31/31 passed independently |
| `firestarter_app/tools/measure_plan_shapes.py` | Validate-before-emit generator | ✓ VERIFIED | 366 lines, `--check`/`--planted-fault` seams confirmed functional by direct invocation in the evidence transcript |
| `firestarter_app/tests/fixtures/plan_shapes.json` | Committed frozen pin | ✓ VERIFIED | Aggregate block matches exactly: rows=746, distinct_part_numbers=677, plans=1354, distinct_shape_families=8, total_steps=16248, unsupported_steps=9304 (independently loaded and inspected) |
| `firestarter_app/tests/test_plan_shapes_drift.py` | Drift gate, no skip marker | ✓ VERIFIED | 201 lines, 0 skip markers, re-run 6/6 passed |
| `firestarter_app/tests/test_derive_plan_no_drop_sweep.py` | Execution half of no-drop proof | ✓ VERIFIED | 318 lines, 6 tests, re-run 6/6 passed |
| `.planning/phases/.../evidence/*.txt` (6 transcripts) | Observed RED/GREEN, not prose | ✓ VERIFIED | All 6 present; spot-checked 3 in full — genuine pytest tracebacks with real assertion failures, not fabricated summaries |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `write_verify_violations` | `chip_test.cycle_block_bounds` | direct call | ✓ WIRED | Confirmed by source read; called exactly once per invocation, never re-implemented |
| `erase_blank_check_violations` | `chip_test.cycle_block_bounds` | direct call | ✓ WIRED | Same production helper, same discipline |
| `test_resolve_write_scope_returns_partial_for_every_uv_row` | `cli_handlers._resolve_write_scope` | direct call via `make_app_context` | ✓ WIRED | Confirmed: sweeps the real production function, not a stub |
| `measure_plan_shapes.py` | `tests/plan_corpus.py` | `from tests.plan_corpus import ...` | ✓ WIRED | Confirmed in `derive()`; no second `EpromDatabase` built |
| `test_derive_plan_no_drop_sweep.py` | `chip_test.run_plan` | direct call, mock operator | ✓ WIRED | Confirmed: real dispatch layer, nothing monkeypatched |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|---|---|---|---|---|
| `tools/measure_plan_shapes.py` | 150-152, 219-221 | `ruff format --check` fails (long-line wrapping) | ℹ️ Info | Confirmed independently via `ruff format --check`. Not a CI blocker — `.github/workflows/ci.yml`'s ruff gate scopes to `firestarter/ tests/` only; `tools/` is out of CI scope (confirmed by reading the workflow file). Matches code review WR-01 exactly |
| `tests/test_plan_shapes_drift.py` | 86-91, 120-125, 138-149 | `subprocess.run` calls with no `timeout=` | ℹ️ Info | Matches code review WR-02. Robustness gap only; does not affect correctness of the drift gate |
| `tools/measure_plan_shapes.py` | 88, 91-93 | Bare `next()` can raise unhandled `StopIteration` outside documented exit codes | ℹ️ Info | Matches code review WR-03. Unreachable on the shipped corpus today (every `full`/`partial` plan has an `OP_ID` and a write step); a defensive-programming gap, not a correctness defect |

No debt markers (`TBD`/`FIXME`/`XXX`) found in any new file. No `TODO`/`HACK`/`PLACEHOLDER` found. No pytest skip markers.

### Requirements Coverage

| Requirement | Source Plans | Description | Status | Evidence |
|---|---|---|---|---|
| PRUNE-06 | 175-01, 175-02, 175-03, 175-05 | Structural test fails on write-with-no-verify | ✓ SATISFIED | Roadmap SC1-3 all verified above; REQUIREMENTS.md checkbox + traceability row both `Complete` |
| PRUNE-05 | 175-03, 175-04, 175-05 | Unsupported steps keep `StepResult` with NA, never dropped | ✓ SATISFIED | Roadmap SC4 verified above (both halves); REQUIREMENTS.md checkbox + traceability row both `Complete` |

No orphaned requirements — `grep -n "Phase 175" REQUIREMENTS.md` returns exactly PRUNE-05 and PRUNE-06, matching what every plan's frontmatter declares.

### Behavioral Spot-Checks / Independent Reproduction

All checks below were run by the verifier independently, in a fresh `uv venv --python 3.11` (not trusting the executor's own transcripts alone):

| Check | Command | Result | Status |
|---|---|---|---|
| Sentinel module | `pytest tests/test_derive_plan_structural_sentinel.py` | 31 passed | ✓ PASS |
| Drift + no-drop modules | `pytest tests/test_plan_shapes_drift.py tests/test_derive_plan_no_drop_sweep.py` | 12 passed in 37.80s | ✓ PASS |
| Fail-closed 14th-op test alone | `pytest ...::test_a_fourteenth_op_fails_the_partition_closed` | 1 passed | ✓ PASS |
| Counter-example re-derivation (independent of the module's own tests) | ad-hoc script stripping `OP_VERIFY` from real plan `('M8720','full')` | `[(2, 'write', 'no supported, field-matching verify in the block')]` on the mutant, `[]` on the original | ✓ PASS — genuinely non-vacuous |
| No-move frozen-hash oracle | `pytest tests/test_blast_radius_invariance.py tests/test_rekey_ledger.py` | 114 passed | ✓ PASS |
| Child-suite timeout raise | `pytest tests/test_skip_census.py` | 5 passed in 173.45s | ✓ PASS (well under 420s cap) |
| Production diff | `git status --porcelain` in both sub-repos + `git diff` on `chip_database.json` | all empty | ✓ PASS |
| Comment/skip census | `grep -cE '^\s*#'` + skip-marker grep on all 5 new files | 1 (shebang) in generator, 0 elsewhere; 0 skip markers | ✓ PASS |
| CI-scoped ruff gate | `ruff format --check firestarter/ tests/` per `ci.yml`'s actual invocation | passes (the `tools/` format gap is out of CI scope) | ✓ PASS |
| Requirement IDs | `grep "Phase 175" REQUIREMENTS.md` | PRUNE-05, PRUNE-06 both `Complete` | ✓ PASS |
| Commit existence | `git cat-file -e` on all 11 `firestarter_app` commit hashes cited across the five SUMMARYs | all present | ✓ PASS |

### Human Verification Required

None. This phase is entirely test-only, deterministic, and machine-verifiable — no UI, no hardware behavior, no state-transition/cancellation invariant that presence-and-wiring checks cannot see. Every claim in the plans and SUMMARYs was independently reproducible from a fresh interpreter, and the anti-vacuity evidence (`evidence/175-01-anti-vacuity-red-green.txt`, `175-02-erase-and-uv-pins.txt`, `175-03-plan-shapes-drift.txt`, `175-04-no-drop-sweep.txt`) contains genuine observed pytest failures with real chip identifiers and tracebacks, not narrated claims.

### Gaps Summary

None. All four roadmap success criteria hold, independently reproduced from a clean py3.11 venv rather than trusted from the executor's transcripts. The three code-review warnings (ruff-format gap in an out-of-CI-scope `tools/` file, missing `timeout=` on three test-side subprocess calls, an unreachable `StopIteration` path in the generator) are real but do not affect the phase's central structural claims and were independently re-confirmed as non-blocking. The phase's explicitly-recorded "currently unreachable" arms (a write outside the cycle block on the shipped corpus; an unsupported write step; the erase-leg's outside-the-block arm) are honestly labeled as such and exercised only via hand-built counter-plans — not silently claimed as tested on the real database, and not silently skipped.

---

_Verified: 2026-09-04_
_Verifier: Claude (gsd-verifier)_
