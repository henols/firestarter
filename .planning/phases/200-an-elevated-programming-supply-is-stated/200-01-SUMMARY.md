---
phase: 200-an-elevated-programming-supply-is-stated
plan: 01
subsystem: cli
tags: [firestarter_app, eprom_info, click, logging, vcc, tracer]

# Dependency graph
requires:
  - phase: 199-what-the-rails-can-actually-deliver
    provides: DECODE-NOTES.md § 9's verdict that the voltage word's nibbles select a programmer rail index, not a chip requirement -- the basis for D-04's amended verb
  - phase: 198-the-two-voltage-nibbles
    provides: the vdd_mv/vcc_mv decode and the 28-row VOLT-03 set this predicate must not disturb
provides:
  - "_SHIELD_FIXED_VCC_MV, programming_vcc_over_rail_mv and _format_v_prose in firestarter/eprom_info.py -- the predicate and formatter plan 200-02/200-03 build their own coverage on"
  - "the Programming VCC: field row and the two-line shortfall warning on `firestarter info`, live for all 284 elevated rows via the tracer part MBM27C1000"
  - "the project's first-defined shortfall-statement shape (VCC-02), generalising the existing no_pinout_warning advisory"
affects: [200-02, 200-03]

# Actuals (#2632)
actuals:
  tokens: 2800
  tasks: 2
  commits: 3
plan_head_before: 0d6be3f

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Raw-record injection gated so the common case adds no key (mirrors the existing support_status block six lines away in the same function)"
    - "caplog.at_level(...) around a CliRunner invocation, rather than asserting on result.output, when ctx.obj is a pre-built AppContext -- pytest's own log-capturing handler on the root logger suppresses logging.lastResort, so result.output is empty regardless of behavior in that mode"

key-files:
  modified:
    - firestarter_app/firestarter/eprom_info.py
    - firestarter_app/tests/test_cli_handlers.py

key-decisions:
  - "D-04's verb is the operator's 2026-09-19 amendment ('decodes to', not 'programs at') -- verified zero occurrences of the pre-amendment verb and exactly one occurrence of the amended sentence in firestarter/eprom_info.py."
  - "Deviation (Rule 1): the plan's Task 2 design asserted the warning text against CliRunner's result.output. Measured this session that under pytest (not a bare interpreter) result.output is always empty when ctx.obj is a pre-built AppContext, because pytest's own log-capturing handler on the root logger satisfies Logger.callHandlers's 'a handler processed this record' check and suppresses the logging.lastResort stderr fallback CliRunner would otherwise pick up. Fixed by asserting against caplog.text instead, wrapped in caplog.at_level(WARNING, logger=\"EpromConsolePresenter\") for order-independence (a sibling test that invokes cli without a pre-built ctx.obj runs the real _setup_logging, which permanently raises the root logger's level to INFO for the rest of the process -- no teardown restores it)."

requirements-completed: [VCC-01, VCC-02]

coverage:
  - id: D1
    description: "A part whose electrical.vdd_mv decodes above 5000 mV shows a Programming VCC: row between VCC: and VPP:, and a two-line WARNING naming both numbers, on `firestarter info`; a part at or below 5000 mV (or with absent/null/zero/non-numeric vdd_mv) shows neither; info exits 0 in both cases."
    requirement: "VCC-01"
    verification:
      - kind: unit
        ref: "inline predicate matrix (Task 1 verify) -- 9-case programming_vcc_over_rail_mv coverage"
        status: pass
      - kind: e2e
        ref: "firestarter info MBM27C1000 / firestarter info W27C512 (Task 1 verify, real entry point)"
        status: pass
      - kind: unit
        ref: "tests/test_characterization.py -- full module, proves the change is purely additive to existing snapshots"
        status: pass
    human_judgment: false
  - id: D2
    description: "The shortfall-statement shape (blank line, WARNING: condition+consequence, follow-on line) generalises the existing no_pinout_warning advisory and is pinned by regression tests proven capable of failing."
    requirement: "VCC-02"
    verification:
      - kind: unit
        ref: "tests/test_cli_handlers.py::test_info_elevated_programming_vcc_warns"
        status: pass
      - kind: unit
        ref: "tests/test_cli_handlers.py::test_info_five_volt_part_emits_no_programming_vcc_warning"
        status: pass
    human_judgment: false

# Metrics
duration: ~30min
completed: 2026-09-19
status: complete
---

# Phase 200 Plan 01: An elevated programming supply is stated Summary

**`firestarter info MBM27C1000` now shows `Programming VCC: 6.0v` and warns "this part's programming supply decodes to 6.0 V; the shield supplies a fixed 5.0 V. Programming will be attempted at 5.0 V." — still exits 0, and `firestarter info W27C512` (a 5 V part) shows neither.**

## Performance

- **Duration:** ~30 min (includes a ~5.5 min full-suite run)
- **Completed:** 2026-09-19T17:44:00Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- `firestarter/eprom_info.py` gains `_SHIELD_FIXED_VCC_MV = 5000`, `_format_v_prose`, and `programming_vcc_over_rail_mv` — a fail-open predicate over `raw_config_data.electrical.vdd_mv` (D-03, D-06), reachable only from `EpromConsolePresenter`.
- `present_eprom_details` renders a `Programming VCC:` row (between `VCC:` and `VPP:`) and a three-line `WARNING:` block, both gated on the same `"programming_vcc_str" in chip_data` key so they can never disagree.
- Two exact-string regression tests pin the warning's presence on `MBM27C1000` and its absence on `W27C512`, proven non-vacuous by a planted `_SHIELD_FIXED_VCC_MV` mutation.
- `info` still exits 0 in both cases (D-05); `database.py`, `cli_handlers.py`, `constants.py`, and every file under `firestarter_fw/` are byte-unchanged against `0d6be3f`.
- The tracer feedback gate passed: the plan's full `<verify>` chain was re-run end-to-end after Task 1's commit, before Task 2 began.

## Task Commits

Each task was committed atomically, inside `firestarter_app` on `v1.40-program-parameter-fidelity`:

1. **Task 1: 6.0 V reaches the operator — raw database record to rendered warning, one part, one path** - `3895753` (feat)
2. **Task 2: The silence side, pinned in process — the warning fires on 6.0 V and is absent on 5.0 V** - `077fce2` (test)

**Gitlink advance:** `4de9ca93` (docs, meta repo) — advances the `firestarter_app` submodule pointer to `077fce2`.

**Plan metadata:** committed separately in the meta repo per this plan's `<commit_protocol>`.

_Note: `plan_head_before: 0d6be3f` is the `firestarter_app` HEAD immediately before this plan's first commit; `git rev-list --count 0d6be3f..HEAD` inside `firestarter_app` reports 2, matching the two task commits above (the gitlink advance is a meta-repo commit, counted separately)._

## Files Created/Modified
- `firestarter_app/firestarter/eprom_info.py` — `_SHIELD_FIXED_VCC_MV`, `_format_v_prose`, `programming_vcc_over_rail_mv`; the gated injection in `prepare_detailed_eprom_data`; the field row and warning block in `present_eprom_details`.
- `firestarter_app/tests/test_cli_handlers.py` — `test_info_elevated_programming_vcc_warns`, `test_info_five_volt_part_emits_no_programming_vcc_warning`.

## Decisions Made
- D-04's verb is the operator's 2026-09-19 amendment: **"decodes to"**, not "programs at". Confirmed by source gate: `/usr/bin/grep -cF 'programs at' firestarter/eprom_info.py` counts 0; `/usr/bin/grep -cF 'programming supply decodes to' firestarter/eprom_info.py` counts 1. No comment, docstring, or string anywhere in the file quotes or paraphrases the pre-amendment verb.
- Deviation (Rule 1 — see below): switched the two new tests' assertion surface from `result.output` to `caplog.text`, because `result.output` is empirically always empty in this invocation shape under pytest.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug in test design] `result.output`-based assertions are vacuous under pytest for a pre-built `ctx.obj`**
- **Found during:** Task 2, first run of the new tests under the full test file.
- **Issue:** The plan's Task 2 action text specified asserting the warning text as `in result.output`. RESEARCH.md § C-3 measured this working via a bare-interpreter script, and reasoned it would hold under pytest too because `_setup_logging` is short-circuited when `ctx.obj` is a pre-built `AppContext`. That measurement was correct as far as it went, but incomplete: outside pytest, an unconfigured root logger with no handlers falls through to Python's `logging.lastResort` handler (a `StreamHandler` on `sys.stderr`), which `CliRunner`'s `mix_stderr=True` merges into `result.output`. **Under pytest**, the `_pytest.logging` plugin always installs its own capturing handler on the root logger for the duration of every test (independent of `caplog` fixture usage), which satisfies `Logger.callHandlers`'s "a handler processed this record" condition and therefore suppresses `lastResort` entirely — so nothing reaches `sys.stderr`/`sys.stdout`, and `result.output` is `''` regardless of what was logged. The originally-written test passed for the wrong reason (an always-true vacuous assertion) when run standalone and failed unpredictably when run after certain siblings in the full file (see next item), which is what surfaced the defect.
- **Fix:** Rewrote both new tests to assert against pytest's `caplog.text` fixture instead of `result.output`, preserving the same string-membership and absence checks. This is the correct, standard mechanism for asserting on log content inside pytest and is non-vacuous — verified by re-running the planted-mutation non-vacuity leg from the plan's own `<verify>` block, which still fails the negative test after the fix.
- **Files modified:** `firestarter_app/tests/test_cli_handlers.py` (test bodies and docstrings only; no production code changed).
- **Verification:** `tests/test_cli_handlers.py::test_info_elevated_programming_vcc_warns` and `::test_info_five_volt_part_emits_no_programming_vcc_warning` both pass in isolation, in combination with the polluting sibling test (see item 2), and as part of the full 68-test file and the full 2087-test suite.
- **Committed in:** `077fce2` (Task 2 commit).

**2. [Rule 1 - Bug in test design] Order-dependence: `_setup_logging` permanently mutates the shared root logger**
- **Found during:** Task 2, running the new tests together with `test_info_unknown_chip_error_path` (an existing sibling test that invokes `cli` without a pre-built `ctx.obj`).
- **Issue:** `test_info_unknown_chip_error_path` goes through the normal Click group entry, so `_setup_logging(verbose=False)` runs and executes `root_logger.setLevel(logging.INFO)` plus `root_logger.handlers = [handler]`. Neither is undone afterward — this is pre-existing production behavior (correct for the real CLI, which runs once per process) with no test-suite teardown. Once any such test runs first in the same pytest process, the root logger's level stays at `INFO` for every subsequent test, which would let `Programming VCC:` (an `INFO`-level line) leak into `caplog.text` and could flip the negative "row is absent from the visible surface" assertion depending on test execution order — a real, observed failure when the two tests were run together with `-p no:randomly` in file-definition order.
- **Fix:** Wrapped each new test's `runner.invoke(...)` call in `caplog.at_level(logging.WARNING, logger="EpromConsolePresenter")`, which pins the named logger's effective level for the duration of the `with` block regardless of ambient global state left by any prior test, making the outcome order-independent.
- **Files modified:** `firestarter_app/tests/test_cli_handlers.py` (same two test bodies as item 1).
- **Verification:** Ran `test_info_unknown_chip_error_path` immediately followed by both new tests (`-p no:randomly`, explicit order) — all three pass. Ran the full 68-test file and the full 2087-test suite — all pass.
- **Committed in:** `077fce2` (Task 2 commit).

---

**Total deviations:** 2 auto-fixed (both Rule 1, both confined to the two new test bodies in `tests/test_cli_handlers.py`; no production code was touched by either fix).
**Impact on plan:** Both fixes were necessary to make the plan's own acceptance criteria ("pytest collects both by name and they pass", "the negative test has been seen to fail against a planted mutation") true under the actual test runner. No scope creep — no other test or production file was touched.

## Backlog Observations (not acted on, per plan instruction)

- **`eprom_info.py`'s two `Support status:` / `Reason:` rows hardcode their pad** (`logger.warning("Support status:      " + support_status)`) and land one column right of every `pos`-formatted row (`pos = 20`). Verified live: the value starts at column 21 there versus column 21 (0-indexed 20) for every other field. Deliberately **not fixed** in this plan — fixing it would move the existing `test_info_*` snapshots for reasons unrelated to VCC-01 and would collide with plan 200-02's zero-deletions gate on `test_characterization.ambr`.
- **An operator's own `~/.firestarter/database.json` can supply an arbitrary `vdd_mv`,** and this warning will render whatever value that override supplies, verbatim, without validation (T-200-02 in the plan's threat model, disposition: accept). The local override file is already the sole source of truth for `vcc_mv`/`vpp_mv` under the same trust model, so this crosses no new trust boundary; it is recorded here rather than mitigated, per the plan's threat register.

## Issues Encountered
None beyond the two deviations documented above, both resolved within Task 2's own scope.

## User Setup Required
None — no external service configuration required.

## Next Phase Readiness
- The predicate (`programming_vcc_over_rail_mv`), the constant (`_SHIELD_FIXED_VCC_MV`), and the two rendered blocks are live and committed on `v1.40-program-parameter-fidelity`, ready for plan 200-02's subprocess-snapshot coverage and plan 200-03's full-database census tests to build on directly (both are named as consumers in the plan's `<verification>` cross-references).
- `tests/__snapshots__/test_characterization.ambr` was confirmed unaffected by this plan's change (`tests/test_characterization.py` — full module, 36 passed / 32 snapshots passed, before and after) — plan 200-02 starts from a clean, additive-only baseline.
- No blockers. STATE.md, ROADMAP.md, and REQUIREMENTS.md updates are deferred to the orchestrator per this plan's execution instructions.

---
*Phase: 200-an-elevated-programming-supply-is-stated*
*Completed: 2026-09-19*
</content>
