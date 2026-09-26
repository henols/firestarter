---
phase: 132-retire-dev-sdp-discharge-the-mypy-debt
plan: 06
subsystem: typing
tags: [mypy, var-annotated, config, database, ci-replica-venv]

# Dependency graph
requires:
  - phase: 132-05
    provides: "typed make_app_context factory discharging the 25-error mock-typing class; measured pre-change baseline of 38 (checked 122 source files)"
provides:
  - "Six [var-annotated] collection-annotation errors annotated in firestarter/config.py (_instances, _initialized_configs, _config) and firestarter/database.py (proms, pin_maps, pin_signals), each proven gone by name from the captured mypy output"
  - "Measured post-fix mypy count of 32 (checked 122 source files), recorded in 132-MYPY-LEDGER.md section 6 with a full 69->63->38->32 subtraction table (expected vs observed per plan)"
  - "The three deliberately-carried assignment errors in database.py (:296, :384, :389) named with line numbers rather than silently left"
  - "132-MYPY-LEDGER.md sections 6, 7, 8: the measured count named as a later phase's ratchet input, the 3-error headroom stated as an accepted cost per D-09, and an explicit statement that a local reading is not a green ci job"
affects: [132-09]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Derive var-annotated fixes from actual usage (how a collection is keyed and populated), not from mypy's placeholder hint or from a prior artifact's generic description of the pattern -- config.py's two singleton registries are keyed by a config-file-path string, not by class, despite 132-06-PLAN.md's action text describing a class-to-instance mapping"
    - "Annotation-only edits to a bare-dict declaration: add the type, change nothing else, then let ruff format reflow the resulting line -- ruff check and ruff format --check are two independent gates and a long annotated line can pass the former while failing the latter"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/config.py
    - firestarter_app/firestarter/database.py
    - .planning/phases/132-retire-dev-sdp-discharge-the-mypy-debt/132-MYPY-LEDGER.md

key-decisions:
  - "config.py's _instances and _initialized_configs are annotated as dict[str, \"ConfigManager\"] and dict[str, bool] respectively -- keyed by the config-file-path string (instance_key = os.path.join(HOME_PATH, actual_filename)), NOT by class, contradicting 132-06-PLAN.md's action-text description (\"a mapping from a type to the instance type\"). Derived from __new__'s actual body per the plan's own instruction to derive from code, not from names; the plan's generic description was not re-litigated as an error, just not followed where it diverged from the measured code."
  - "database.py's proms and pin_maps are both dict[str, Any] -- JSON-round-tripped structures with no code-demonstrated narrower value type; pin_signals is dict[int, str], derived from the _assign() nested helper's actual pin-number keys and signal-name values."
  - "ruff format --check failed after the first pass on config.py (the two new annotated class-attribute lines exceeded ruff's line-length preference) and was resolved by running ruff format on the file rather than hand-wrapping -- the tool's own reflow is the house convention every other module in the tree already carries."
  - "The subtraction table's -6 step (69 -> 63) is attributed by 132-MYPY-LEDGER.md section 4's prose to plan 132-03, but the number only materialized once plan 132-04 physically deleted dev_sdp and its local factory (132-05-SUMMARY.md's own dependency line records 63 as 132-04's output). Recorded in the ledger as a plan-attribution mismatch, not a count mismatch -- the magnitude matches exactly."

requirements-completed: []

coverage:
  - id: D1
    description: "The six named unannotated-collection mypy errors (config.py:84,85,102; database.py:174,175,325) are annotated with types derived from actual usage, and each is proven gone by name from the captured replica-venv mypy output."
    verification:
      - kind: unit
        ref: "grep -cE 'config\\.py:(84|85|102).*Need type annotation' and 'database\\.py:(174|175|325).*Need type annotation' against the captured mypy run -- both 0"
        status: pass
      - kind: unit
        ref: "grep -c 'Need type annotation' against the captured mypy run -- 0 (all six of this class gone tree-wide)"
        status: pass
      - kind: integration
        ref: "bash tools/ci_replica_venv.sh -- Leg 4 (mypy watermark gate) exit 0, all 5 legs PASS"
        status: pass
    human_judgment: false
  - id: D2
    description: "No new error was introduced in either edited module; config.py's per-file error count is 0, database.py's is exactly 3 (the three deliberately-carried assignment errors), and the total count is measured against the watermark and matches the ledger's own projection of 32."
    verification:
      - kind: unit
        ref: "grep '^firestarter/config.py' against the captured mypy error lines -- 0 matches; grep '^firestarter/database.py' -- exactly 3, at :296/:384/:389"
        status: pass
      - kind: unit
        ref: "captured mypy summary line: 'Found 32 errors in 12 files (checked 122 source files)'; gate line: 'mypy errors: 32 (watermark: 35)'"
        status: pass
    human_judgment: false
  - id: D3
    description: "The config-manager singleton behaviour is unchanged by the annotation-only edit, and the full test suite plus ruff remain green."
    verification:
      - kind: unit
        ref: "python -c \"from firestarter.config import ConfigManager as C; a=C(); b=C(); assert a is b\" -- SINGLETON OK"
        status: pass
      - kind: unit
        ref: "tools/ci_replica_venv.sh Leg 5 (pytest --cov=firestarter --cov-fail-under=70) -- 1295 passed, 0 failures, coverage 81.72%; Leg 3 (ruff check + format --check) -- exit 0"
        status: pass
    human_judgment: false
  - id: D4
    description: "The measured post-fix reading (32, checked 122 source files) plus the full 69-to-32 subtraction table and the D-09 headroom cost are recorded in 132-MYPY-LEDGER.md sections 6-8, with section 4 left byte-unchanged and an explicit statement that a local reading is not a green ci job."
    verification:
      - kind: unit
        ref: "git diff on 132-MYPY-LEDGER.md shows the only deleted line is the '132-06 appends here' placeholder itself; sections 6/7/8 headings present; '132-09 appends here' placeholder still present"
        status: pass
    human_judgment: false

duration: 40min
completed: 2026-08-03
status: complete
---

# Phase 132 Plan 06: Six var-annotated Fixes + Measured Post-Fix Reading Summary

**Six bare-collection mypy annotations landed across `config.py` and `database.py` (three each, all derived from actual usage rather than mypy's placeholder hint), bringing the measured mypy count from 38 to 32 -- 3 below the existing watermark of 35 -- without touching the watermark or the ring-fenced `eprom_operations.py` module.**

## Performance

- **Duration:** ~40 min
- **Started:** 2026-08-03T20:05:42Z (STATE.md's prior session marker, 132-05 complete)
- **Completed:** 2026-08-03T20:45:00Z (approximate)
- **Tasks:** 3
- **Files modified:** 3 (`config.py`, `database.py`, `132-MYPY-LEDGER.md`)

## Accomplishments

- **Task 1 (config.py):** Annotated `_instances: dict[str, "ConfigManager"] = {}` and `_initialized_configs: dict[str, bool] = {}` at the class level, and `self._config: dict[str, Any] = {}` inside `__init__`. Derived from the actual `__new__`/`__init__` bodies: both class-level registries are keyed by `instance_key` (a config-file-path string built from `os.path.join(HOME_PATH, actual_filename)`), not by class -- the plan's own action text described a generic "class to instance" mapping shape that does not match this module's real code; followed the plan's explicit instruction to derive from code over names instead. `_config` holds heterogeneous JSON-round-tripped values, so `dict[str, Any]` is the honest annotation (no narrower value type is demonstrated anywhere in the module). Added `Any` to the existing `from typing import Optional` import. Verified the three named mypy lines (`config.py:84`, `:85`, `:102`) are gone by name (grep count 0), `config.py`'s own per-file error count is 0, and the singleton identity assertion (`ConfigManager() is ConfigManager()`) still holds. `ruff format --check` initially failed on the two new class-attribute lines (too long); resolved by running `ruff format` on the file, which reflowed them into the tree's existing multi-line `dict[...]` bracket style -- no hand-wrapping. Committed as `b76b9db`.
- **Task 2 (database.py):** Annotated `self.proms: dict[str, Any] = {}` and `self.pin_maps: dict[str, Any] = {}` in `EpromDatabase.__init__` (both hold parsed JSON chip/pin-map data with no code-demonstrated narrower value type), and `pin_signals: dict[int, str] = {}` inside `get_adapter_table`, derived from the nested `_assign()` helper's actual key type (pin number, `int`) and value type (signal name, `str`). Added `from typing import Any` (the module had no prior `typing` import). Left the three assignment-class errors untouched, as instructed -- measured at `:296` (`int` assigned to a `list[int]`-typed target), `:384` and `:389` (`float` assigned to `int`-typed variables); the plan's own read-first anchors named `:295`/`:383`/`:388`, one line lower than measured, consistent with this phase's other line-number corrections (mypy's own output is the authority). Verified the three named mypy lines (`database.py:174`, `:175`, `:325`) are gone by name, `database.py`'s per-file error count is exactly 3 (the three carried errors, no new error), and `bash tools/ci_replica_venv.sh` returns **all 5 legs PASS** (`mypy errors: 32 (watermark: 35)`, `Found 32 errors in 12 files (checked 122 source files)`). Full suite: 1295 passed, 0 failures, coverage 81.72%. `pyproject.toml` and `firestarter/eprom_operations.py` diffs both empty. Committed as `db990e8`.
- **Task 3 (ledger append, meta-repo):** Replaced the `132-06 appends here` placeholder in `132-MYPY-LEDGER.md` with `## 6. Measured post-fix reading`, `## 7. The number a later phase ratchets to, and the cost of not doing it here`, and `## 8. Still not established`. Section 6 carries the gate's verbatim stamp lines, the full 69→63→38→32 subtraction table with an expected-vs-observed column per contributing plan (132-03, 132-05, 132-06), and the remaining 32-error inventory by file and by code, including the 10-error `eprom_operations.py` ring-fence carry labelled `FUT-MYPY-02`. One real divergence surfaced and was recorded rather than reconciled: section 4's projection prose attributes the `-6` step (69→63) to plan 132-03, but that number only measured as landed once plan 132-04 physically deleted `dev_sdp` (per `132-05-SUMMARY.md`'s own dependency line, which records 63 as 132-04's output) -- a plan-attribution mismatch, not a count mismatch; the magnitude matches section 4's projection exactly. Section 7 states the measured 32 as the named ratchet input for a later phase, the accepted `35-32=3` headroom cost per D-09, both of D-09's rejected alternatives re-confirmed against the now-real number, and that the typed factory (132-05, D-10) -- not the watermark -- is the actual defence against regression. Section 8 states plainly that a local reading is not a green `ci` job. Section 4 confirmed byte-unchanged by `git diff`; the `132-09 appends here` placeholder confirmed still present. Committed as `d06048c` in the meta-repo.
- **Requirements marked Complete: none (RETIRE-06 is owned by plan 132-09).**

## Task Commits

Each task was committed atomically, in the repo that owns the file:

1. **Task 1: annotate the three collections in config.py** — `b76b9db` (fix, `firestarter_app` submodule)
2. **Task 2: annotate the three collections in database.py** — `db990e8` (fix, `firestarter_app` submodule)
3. **Task 3: append measured post-fix reading to the ledger** — `d06048c` (docs, meta-repo)

**Plan metadata:** this summary + STATE.md/ROADMAP.md updates (meta-repo, separate commit per `<final_commit>`).

## Files Created/Modified

- `firestarter_app/firestarter/config.py` — three collection annotations added (`_instances`, `_initialized_configs`, `_config`); `Any` added to the `typing` import; `ruff format`-reflowed.
- `firestarter_app/firestarter/database.py` — three collection annotations added (`proms`, `pin_maps`, `pin_signals`); `from typing import Any` added.
- `.planning/phases/132-retire-dev-sdp-discharge-the-mypy-debt/132-MYPY-LEDGER.md` — sections 6, 7, 8 appended; section 4 untouched.

## Decisions Made

- **config.py's two singleton registries are keyed by config-file-path string, not by class** — derived from `__new__`'s actual body over the plan's own generic action-text description, per the plan's explicit instruction to derive from code rather than from names.
- **database.py's `proms`/`pin_maps` use `dict[str, Any]`**, not a narrower value type, because the values are parsed JSON structures with no code-demonstrated narrower shape — a too-narrow annotation would have created new assignment errors elsewhere, turning a six-error win into a net loss (the exact risk the plan's action text called out).
- **The ledger's -6 step (69→63) is recorded as a plan-attribution mismatch, not reconciled**: section 4's prose named plan 132-03, but the number measured as landed only after 132-04's deletion.

## Deviations from Plan

None — plan executed exactly as written. The `ruff format` reflow of `config.py`'s two new lines is a mechanical formatting-tool step, not a deviation: the plan's own verification step (running the replica script, which includes `ruff format --check`) is what surfaced the need, and the fix is the tool's own canonical output, not a hand-authored workaround.

## Issues Encountered

None beyond the `ruff format --check` reflow noted above, resolved in-task.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- **Measured count: 32 (checked 122 source files), watermark unchanged at 35.** This is at or below the watermark for the first time in this phase's history, but per this plan's own `<objective>` and the phase's ordering, **this is a local measurement, not a green CI job**, and RETIRE-06's Complete transition belongs to plan 132-09's certifying dispatch, not this plan.
- The three carried `database.py` assignment errors (`:296`, `:384`, `:389`) and the 10-error ring-fenced `eprom_operations.py` cluster remain, both named and dispositioned in the ledger's section 6 inventory — plan 132-09 inherits an accurate, non-vacuous remaining-error picture.
- Full test suite green: 1295 passed, 0 failures, coverage 81.72% (floor 70%). `ruff check` + `ruff format --check` both exit 0 across `firestarter/` and `tests/`.
- `pyproject.toml` and `firestarter/eprom_operations.py` are both byte-unchanged by this plan (verified via empty `git diff --stat`) — the watermark and the ring-fence both held.
- No blockers. RETIRE-01/02/03/05 (already Complete) remain untouched; RETIRE-04 (132-08), RETIRE-06 (132-09), RETIRE-07 (132-07), RETIRE-08 (132-08) remain untouched, as required. 132-09 can proceed against the newly-measured 32-error baseline, watermark 35.

---
*Phase: 132-retire-dev-sdp-discharge-the-mypy-debt*
*Completed: 2026-08-03*

## Self-Check: PASSED

Created/modified files verified present on disk:
- `.planning/phases/132-retire-dev-sdp-discharge-the-mypy-debt/132-06-SUMMARY.md` — FOUND
- `firestarter_app/firestarter/config.py` — FOUND
- `firestarter_app/firestarter/database.py` — FOUND
- `.planning/phases/132-retire-dev-sdp-discharge-the-mypy-debt/132-MYPY-LEDGER.md` — FOUND

Commits verified present in the owning repo's history:
- `b76b9db` — FOUND (`firestarter_app` submodule)
- `db990e8` — FOUND (`firestarter_app` submodule)
- `d06048c` — FOUND (meta-repo)
