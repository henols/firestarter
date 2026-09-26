---
phase: 121-dev-test-fix-gates-docs-redesign
plan: 05
subsystem: dev-test
tags: [chip_test, derive_plan, uv-eprom, write-region, python, host-cli]

# Dependency graph
requires:
  - phase: 121-02
    provides: fail-closed _dispatch_step/_dispatch_multi_run guard in chip_test.py
provides:
  - "is_uv_eprom(full) -- exact, name-keyed 301/301 UV-EPROM predicate"
  - "Plan.is_uv and Step.write_region carried fields"
  - "derive_plan's three-valued write_scope (none|partial|full) replacing the destructive bool kwarg"
  - "_top_anchored_or_default region helper used by derive_plan"
affects: [121-06, 121-09]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Decide-once-carry-downstream: a fact (UV-ness) computed exactly once from the richest available data (full DB dict) and carried on the return object rather than re-derived from a lossy proxy at execution time"
    - "Fail-closed enum kwarg: an unrecognised write_scope value raises ValueError naming the offending value and all accepted literals, never silently defaulting to a writing mode"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/chip_test.py
    - firestarter_app/firestarter/cli_handlers.py
    - firestarter_app/tests/test_chip_test.py

key-decisions:
  - "is_uv_eprom is keyed on full['electrical-type'] == 'UV-EPROM' -- exact 301/301 against the live DB, versus the execution-time algorithm==0x0B proxy's 32/301"
  - "write_scope='full' reproduces destructive=True's write_region exactly: engine default for non-UV, top-anchored UV window for UV (matching _write_region_for's existing behaviour) -- proven byte-for-byte equivalent to the pre-plan destructive=True/False op sequences"
  - "write_scope='partial' is NOT is_uv-gated for its region: it always applies the top-anchored-window-or-fallback formula, independent of chip type -- its whole purpose is the small-region write; this is a deliberate deviation from the literal wording that could be read as is_uv-conditioned, resolved by the plan's own acceptance criteria (mem_size 65536 -> (65280,256); mem_size 0/missing -> (0,256))"
  - "_write_region_for (the execution-time proxy) is left untouched in this plan -- its production caller wiring is 121-06/121-09's work; this plan only wires derive_plan's own compile-time region computation"

requirements-completed: []

coverage:
  - id: D1
    description: "is_uv_eprom(full) predicate, exact 301/301 over the live DB, with a four-chip pinning table (M27C512/AM27C020 true; W27C512/AT28C256 false)"
    verification:
      - kind: unit
        ref: "tests/test_chip_test.py#test_is_uv_eprom_exact_301_over_real_db"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py#test_is_uv_eprom_four_chip_table"
        status: pass
    human_judgment: false
  - id: D2
    description: "Plan.is_uv and Step.write_region carried fields, defaulted so every existing construction site stays valid"
    verification:
      - kind: unit
        ref: "tests/test_chip_test.py#test_plan_and_step_carried_fields_default"
        status: pass
    human_judgment: false
  - id: D3
    description: "derive_plan's destructive bool kwarg replaced by a three-valued write_scope (none/partial/full), fail-closed on any other value, behaviour-preserving for none/full"
    verification:
      - kind: unit
        ref: "tests/test_chip_test.py#test_derive_plan_destructive_flag_strips_not_annotates"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py#test_derive_plan_write_scope_rejects_unknown_value"
        status: pass
      - kind: integration
        ref: "tests/test_dev_test_cmd.py (zero edits, git status --porcelain empty)"
        status: pass
    human_judgment: false
  - id: D4
    description: "write_scope='partial' new third mode: same op sequence as 'full', top-anchored-window-or-fallback write_region regardless of is_uv"
    verification:
      - kind: unit
        ref: "tests/test_chip_test.py#test_derive_plan_partial_same_ops_as_full_different_region"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py#test_derive_plan_partial_write_region_uv_memory_size"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py#test_derive_plan_partial_write_region_missing_memory_size_falls_back"
        status: pass
    human_judgment: false
  - id: D5
    description: "Plan.is_uv wired through derive_plan (not is_uv_eprom directly), proven for the four-chip table"
    verification:
      - kind: unit
        ref: "tests/test_chip_test.py#test_derive_plan_is_uv_wired_from_is_uv_eprom"
        status: pass
    human_judgment: false

# Metrics
duration: 25min
completed: 2026-07-29
status: complete
---

# Phase 121 Plan 05: Decide UV-ness once, in derive_plan (D-02) Summary

**Added an exact, name-keyed `is_uv_eprom` predicate (301/301 vs the execution-time proxy's 32/301) and replaced `derive_plan`'s boolean `destructive` kwarg with a three-valued `write_scope` (`none`/`partial`/`full`) that carries the UV decision and the write-region consequence on the `Plan`/`Step` objects, with zero observable CLI behaviour change.**

## Performance

- **Duration:** ~25 min
- **Completed:** 2026-07-29T18:07:52Z
- **Tasks:** 3 of 3
- **Files modified:** 3 (`firestarter/chip_test.py`, `firestarter/cli_handlers.py`, `tests/test_chip_test.py`)

## Accomplishments

- `is_uv_eprom(full)` -- a pure, public predicate keyed on `full["electrical-type"] == "UV-EPROM"`, measured exact at 301/301 against the live `chip_database.json`, versus the pre-existing execution-time `algorithm == 0x0B` proxy's 32/301 coverage. Pinned against a four-chip table: `M27C512` (algorithm `0x07`) and `AM27C020` (algorithm `0x08`) both `True` despite neither matching the algorithm proxy; `W27C512` (the Winbond part routinely confused with the ST `M27C512`) and `AT28C256` both `False`.
- `Plan.is_uv: bool` and `Step.write_region: tuple[int, int] | None` -- two new defaulted dataclass fields carrying the UV decision and its write-window consequence. Docstrings name who decides (`derive_plan`, exactly once) and who may only read (`run_plan`, the execution layer, everything downstream).
- `derive_plan(name, db, *, write_scope="none")` replaces `derive_plan(name, db, *, destructive=False)`. Three accepted literals:
  - `"none"` -- reproduces `destructive=False` byte-for-byte: write/verify/erase structurally omitted from `Plan.steps`, recorded on `Plan.locked_destructive` instead.
  - `"full"` -- reproduces `destructive=True` byte-for-byte: write/verify/erase are real steps; `write_region` is the engine default for non-UV chips and the top-anchored UV window for UV chips (matching `_write_region_for`'s existing execution-time behaviour).
  - `"partial"` (new) -- same op sequence as `"full"`, but `write_region` on the write/verify steps always applies the top-anchored-window-or-fallback formula, independent of `is_uv` (this scope's whole purpose is the small-region write). Still emits `OP_WRITE`; plan `121-06` swaps that to `OP_WRITE_PARTIAL`.
  - Any other value raises `ValueError` naming the offending value and the three accepted literals -- never a silent fallback to a writing mode.
- Single production caller (`cli_handlers.py:1932`) rewired to `derive_plan(chip, app.db, write_scope="full" if destructive else "none")`. `tests/test_dev_test_cmd.py` needed **zero edits** (`git status --porcelain` confirmed empty), proving the CLI's observable behaviour is unchanged.
- Engine test suite mechanically reworked: all 19 `derive_plan(..., destructive=True/False)` call sites translated to `write_scope="full"/"none"`; three new legs added (partial-scope same-ops-different-region incl. both acceptance-criterion cases, unknown-value `ValueError`, `Plan.is_uv` wiring through `derive_plan` for the four-chip table). `tests/test_provenance.py` needed no change -- its one `destructive=` grep hit is `locked_destructive=[]` on a direct `Plan(...)` construction, not a `derive_plan` call.

## Task Commits

1. **Task 1: Add the pure is_uv_eprom predicate and the two carried plan-object fields** - `1df3cd4` (feat)
2. **Task 2: Replace derive_plan's destructive kwarg with a three-valued write_scope, behaviour-preserving** - `da6cda2` (refactor)
3. **Task 3: Mechanically rework the engine test suite onto write_scope** - `cd006ea` (test)

**Plan metadata:** commit pending (this SUMMARY + docs commit)

## Files Created/Modified

- `firestarter_app/firestarter/chip_test.py` - `is_uv_eprom`, `Plan.is_uv`/`Step.write_region` fields, `derive_plan`'s `write_scope` rewrite, `_top_anchored_or_default`/`_DEFAULT_REGION` helpers, `count_applicable`'s docstring updated
- `firestarter_app/firestarter/cli_handlers.py` - single production `derive_plan` call rewired to `write_scope=`
- `firestarter_app/tests/test_chip_test.py` - 19 call sites translated, 16 new tests added (8 in Task 1, 8 in Task 3)

## Decisions Made

- **`is_uv_eprom` takes the `full` DB dict, never the programmer dict.** `resolve_chip`/`convert_to_programmer`'s output carries `algorithm` but not `electrical-type` -- `derive_plan` is the only layer holding the richer `full` dict, so it is the only layer that can decide UV-ness exactly.
- **`write_scope="partial"`'s region computation is not `is_uv`-gated.** Read literally, the plan's Task 2 action text could be parsed as "top-anchored UV window" implying an `is_uv` check; the acceptance criteria settle it unambiguously (a `memory-size=65536` case yielding `(65280, 256)` and a missing/zero `memory-size` case yielding the engine default `(0, 256)`, with neither case gated on chip type). Implemented as: `"full"` conditions on `is_uv` (matching legacy `_write_region_for` behaviour exactly); `"partial"` always applies the top-anchored-window-or-fallback formula. This is recorded here because a plausible alternative reading (`"partial"` also `is_uv`-gated, defaulting to `None`/engine-default for non-UV) would have failed the plan's own acceptance criteria if a non-UV chip were ever passed with `write_scope="partial"` and a real `memory-size` -- the chosen reading is the only one consistent with the stated `(0, 256)` fallback figure being a concrete tuple rather than `None`.
- **`_write_region_for` (the execution-time UV proxy) is deliberately left untouched.** It still exists, still used by `_dispatch_multi_run` at execution time; converting its production callers from guessing to reading `Plan.is_uv`/`Step.write_region` is explicitly plan `121-06`'s work (per the plan's own "Do not touch `_write_region_for` in this task" instruction on Task 1, and Task 3's instruction not to add new `_write_region_for(full_dict)` unit tests).
- **`locked_destructive` and the N-of-M banner are kept, not deleted** (per the plan's `must_haves`) -- the docstring now records the forward-looking note that after plan `121-09` no CLI path reaches `write_scope="none"`, so the list becomes permanently empty in production, and that removal is a deferred cleanup, not this phase's work.

## Deviations from Plan

None - plan executed exactly as written. The one interpretive decision (partial-scope region not `is_uv`-gated) was resolved directly from the plan's own explicit acceptance criteria, not a change to scope, behaviour, or requirements -- documented above under Decisions Made for future-phase clarity, not tracked as a Rule 1-4 deviation.

## Issues Encountered

- **`/tmp/venv311/bin/ruff` does not exist in this devcontainer** (no `python3.11` interpreter installed, no venv at that path). Substituted the PATH-installed `ruff` binary (`/home/vscode/.local/bin/ruff`, v0.16.0) and `mypy` (v2.3.0) directly -- `ruff` is a standalone Rust binary that applies `pyproject.toml`'s `target-version = "py39"` rule set regardless of which Python interpreter it runs under, so this substitution does not weaken the CI-parity check. `ruff check` and `ruff format --check` both exit 0 against `firestarter/` and `tests/`.
- **pytest's terminal summary line (`N passed in Xs`) does not print in this environment** (observed on both `test_chip_test.py`-only and full-suite runs, with `-q`, `-rN`, and `-p no:cacheprovider`; no `conftest.py` hook found that would suppress it). Worked around by cross-checking exit codes (all 0) plus `pytest --collect-only -q`'s per-file counts, summed with `awk`, against the known 1064-test baseline (confirmed present) and the final 1080-test count (1064 + 16 new). This is an environment quirk, not a project regression -- flagging for future executors in this devcontainer.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `Plan.is_uv` and `Step.write_region` are now available for plan `121-06` to wire `_write_region_for`'s production callers away from the `algorithm == 0x0B` guess and onto the carried fields, and for `OP_WRITE_PARTIAL` to consume `write_scope="partial"`'s region.
- `write_scope="full"`/`"none"` are proven behaviour-identical to the pre-plan `destructive=True`/`False` contract (op sequences and `locked_destructive` contents pinned exactly in `test_derive_plan_destructive_flag_strips_not_annotates`), so plan `121-06`'s and `121-09`'s callers can adopt the new kwarg with no surprise.
- `test_dev_test_cmd.py` stayed byte-clean throughout -- the CLI-facing contract this plan must not disturb is intact.
- Full host suite green: 1080 passed, 0 failed (1064 baseline + 16 new tests from this plan). `ruff check`/`format --check` exit 0. mypy watermark unchanged (1 error, 35 watermark -- pre-existing, not from this plan). `python3 tools/check_devtest_orchestrator.py` still PASSes (0 VPP-set, 0 raw-wire-dict, 0 `--force`, firmware untouched).
- No requirement marked Complete (DEVTEST-03/DEVTEST-04 both remain Pending, closed later by 121-06/121-09 per the plan's requirement-scope lock). `REQUIREMENTS.md`, `STATE.md`, `ROADMAP.md` untouched by this plan.

## Self-Check: PASSED

- `firestarter_app/firestarter/chip_test.py` -- FOUND (modified, exists)
- `firestarter_app/firestarter/cli_handlers.py` -- FOUND (modified, exists)
- `firestarter_app/tests/test_chip_test.py` -- FOUND (modified, exists)
- Commit `1df3cd4` -- FOUND in `firestarter_app` git log
- Commit `da6cda2` -- FOUND in `firestarter_app` git log
- Commit `cd006ea` -- FOUND in `firestarter_app` git log

---
*Phase: 121-dev-test-fix-gates-docs-redesign*
*Completed: 2026-07-29*
