---
phase: quick-260916-nb9
plan: 01
subsystem: testing
tags: [python, pytest, diagnostic-report, error-codes, dev-test]

requires: []
provides:
  - "resolve_error_name(error_code) pure resolver in firestarter/chip_test.py, reading firestarter.messages.CATALOG only"
  - "error_name key in diagnostic_report._step_dict, emitted unconditionally beside error_code"
  - "SCHEMA_VERSION 2.1"
affects: [dev-test-reporting, github-issue-triage, messages-catalog-consumers]

actuals:
  tokens: 2981
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "Derived-at-serialization-time value, never stored on the dataclass, to prevent a second source of truth from drifting"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/chip_test.py
    - firestarter_app/firestarter/diagnostic_report.py
    - firestarter_app/tests/test_chip_test.py
    - firestarter_app/tests/test_diagnostic_report.py
    - firestarter_app/tests/test_blast_radius_invariance.py

key-decisions:
  - "error_name is NOT stored on StepResult — it is derived by resolve_error_name(result.error_code) at _step_dict serialization time, so the integer and its name can never disagree in a filed report (T-nb9-04)."
  - "resolve_error_name reads firestarter.messages.CATALOG only, never DEBUG_CATALOG — the two registries collide on nine ids (0,1,2,3,4,5,16,32,48) under different names, and error_code is always a top-level response.id, a namespace CATALOG alone describes (T-nb9-02)."

patterns-established:
  - "A pure resolver placed beside repeat_policy_tag/coverage_tag in chip_test.py, imported into diagnostic_report.py rather than reimplemented there"

requirements-completed: [260916-nb9]

coverage:
  - id: D1
    description: "resolve_error_name(error_code) resolves the three issue #86 ids (183/175/185) and is exhaustive over all 79 CATALOG ids"
    requirement: "260916-nb9"
    verification:
      - kind: unit
        ref: "tests/test_chip_test.py::test_resolve_error_name_names_the_issue_86_ids"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py::test_resolve_error_name_is_exhaustive_over_the_catalog"
        status: pass
    human_judgment: false
  - id: D2
    description: "resolve_error_name degrades to null (never raises) for a null code, an id in neither registry, and every one of the 0-255 unnamed ids, and never falls back to DEBUG_CATALOG"
    requirement: "260916-nb9"
    verification:
      - kind: unit
        ref: "tests/test_chip_test.py::test_resolve_error_name_null_for_a_null_code"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py::test_resolve_error_name_null_for_an_id_in_neither_registry"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py::test_resolve_error_name_never_falls_back_to_debug_catalog"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py::test_resolve_error_name_never_raises_over_the_unnamed_range"
        status: pass
    human_judgment: false
  - id: D3
    description: "to_dict()['steps'][i] carries error_name unconditionally beside error_code, including on null/unrecognized codes"
    requirement: "260916-nb9"
    verification:
      - kind: unit
        ref: "tests/test_diagnostic_report.py::test_step_dict_emits_the_resolved_error_name_beside_the_code"
        status: pass
      - kind: unit
        ref: "tests/test_diagnostic_report.py::test_step_dict_keys_error_name_unconditionally"
        status: pass
      - kind: unit
        ref: "tests/test_diagnostic_report.py::test_step_dict_error_name_null_for_a_null_error_code"
        status: pass
      - kind: unit
        ref: "tests/test_diagnostic_report.py::test_step_dict_error_name_null_for_an_unrecognized_error_code"
        status: pass
    human_judgment: false
  - id: D4
    description: "SCHEMA_VERSION bumped to 2.1, single-sourced, and all four pinned test sites moved in the same commits"
    requirement: "260916-nb9"
    verification:
      - kind: unit
        ref: "tests/test_diagnostic_report.py::test_schema_version_2_1_single_sourced"
        status: pass
      - kind: unit
        ref: "tests/test_diagnostic_report.py::test_schema_version_is_two_one"
        status: pass
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py::test_schema_version_is_pinned"
        status: pass
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py::test_to_dict_steps_element_0_key_list_is_pinned"
        status: pass
    human_judgment: false
  - id: D5
    description: "The schema bump re-keys no historical dedup_fingerprint, and the updated key pin is proven sensitive to the new key"
    requirement: "260916-nb9"
    verification:
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py::test_schema_bump_rekeys_no_frozen_hash"
        status: pass
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py::test_steps_element_0_key_pin_is_sensitive_to_the_error_name_key"
        status: pass
    human_judgment: false

duration: ~45min
completed: 2026-09-16
status: complete
---

# Quick 260916-nb9: Resolved error_name Beside error_code Summary

**A pure `resolve_error_name(error_code)` resolver reads `firestarter.messages.CATALOG` to name every `dev test` failing step's integer error code (e.g. `183` -> `MSG_ERR_OP_TIMEOUT`), emitted unconditionally as `error_name` beside the existing `error_code` in the serialized report — schema bumped 2.0 -> 2.1, all 19 historical dedup hashes unchanged.**

## Performance

- **Duration:** ~45 min
- **Tasks:** 2/2 completed
- **Files modified:** 5

## Accomplishments

- Named the failure: a triager reading a filed `dev test` issue now sees `MSG_ERR_OP_TIMEOUT` instead of a bare `183`, without importing `firestarter.messages` or checking out this repository.
- `resolve_error_name` is exhaustive and non-raising over the entire integer space: it agrees with `CATALOG[id].name` for all 79 catalog ids, returns `None` for any of the other 177 ids in `0..255`, and never falls back to `DEBUG_CATALOG` even on the one id (`6`) that collides there under a different name.
- Zero re-keying: all 19 `FROZEN_HASHES` literals in `tests/fixtures/report_shapes.py` are unchanged, and a new sensitivity leg proves the updated `_STEPS_ELEMENT_0_KEYS` pin actually reddens when `error_name` is removed rather than having been merely widened to accept it.

## Task Commits

Each task was committed atomically in the `firestarter_app` submodule (branch `v1.39-protocol-0x05-write-correctness`, anchored at `2acf5d33c9ed1d08b191a6ca245e91b3cc71d16a`):

1. **Task 1: Resolve the name end to end — catalog to report JSON, with the schema bump** - `a969fa8` (feat)
2. **Task 2: Pin the degradation contract and prove the bump re-keys nothing** - `e4cbfdf` (test)

Docs (this SUMMARY.md, PLAN.md) are committed by the orchestrator, not by this executor, per the batch's constraints.

## Files Created/Modified

- `firestarter_app/firestarter/chip_test.py` - adds `resolve_error_name(error_code)` beside `repeat_policy_tag`/`coverage_tag`; imports `firestarter.messages`; extends `StepResult`'s docstring sentence about `error_code` to say where the name is resolved (a docstring, not a comment)
- `firestarter_app/firestarter/diagnostic_report.py` - imports `resolve_error_name` from `chip_test`; emits `"error_name"` unconditionally in `_step_dict`, immediately after `"error_code"`; bumps `SCHEMA_VERSION` `"2.0"` -> `"2.1"`
- `firestarter_app/tests/test_chip_test.py` - 6 new tests: the three issue #86 ids named as literals, exhaustiveness over `CATALOG`, null-for-null, null-for-unrecognized, the deliberate non-fallback to `DEBUG_CATALOG` on id 6, and the full 0-255 non-raising sweep
- `firestarter_app/tests/test_diagnostic_report.py` - 4 new tests plus 2 renames: serialized `error_name` beside `error_code`, unconditional keying, null-with-key-present degradation for a null and an unrecognized code; `test_schema_version_2_0_single_sourced` -> `test_schema_version_2_1_single_sourced`, `test_schema_version_is_two_oh` -> `test_schema_version_is_two_one`
- `firestarter_app/tests/test_blast_radius_invariance.py` - `_STEPS_ELEMENT_0_KEYS` gains `error_name` in sorted position (20 -> 21 entries); `test_schema_version_is_pinned` moved to `"2.1"`; 2 new tests: the sensitivity leg for the updated key pin, and an explicit re-key-review statement over all 19 `FROZEN_HASHES`

## Decisions Made

1. **`error_name` is derived, never stored on `StepResult`.** Storing it would create a second source of truth that could disagree with `error_code` in a filed report (T-nb9-04, Repudiation). It is computed once, at `_step_dict` serialization time, from `result.error_code` alone.
2. **Read `CATALOG` only, never `DEBUG_CATALOG`, with no fallback.** The two registries collide on nine ids (`0, 1, 2, 3, 4, 5, 16, 32, 48`) with different meanings — `MSG_*` in one, `DBG_*` in the other. `error_code` is always a top-level `response.id`, a namespace only `CATALOG` describes; `codec.py:206`'s bare `CATALOG.get(msg_id)` is the existing precedent this resolver follows. A `DEBUG_CATALOG` fallback would silently mis-name a real failure (T-nb9-02, Spoofing) — pinned by id `6` resolving to `None`, explicitly not `"DBG_CMD_FINISHED"`.
3. **The non-raising get accessor (`dict.get`), not a try/except around indexing.** A garbled or malicious `response.id` from a malfunctioning serial peer must never crash report generation after a run has already completed (T-nb9-01, DoS) — the resolver degrades to `None` for any id outside `CATALOG`, swept over the entire `0-255` range in Task 2.
4. **`error_name` inserted immediately after `error_code`** in `_step_dict`'s return literal (sorted position, between `error_code` and `fingerprint` in `_STEPS_ELEMENT_0_KEYS`), matching the plan's stated insertion point and keeping the key set's alphabetical pin trivial to eyeball.

## Deviations from Plan

None — plan executed exactly as written, including the exact resolver signature, the read-only `CATALOG`-only lookup, the derived-not-stored placement, the schema bump, and all four pinned test-site updates (`_STEPS_ELEMENT_0_KEYS`, `test_schema_version_is_pinned`, and the two renamed single-sourcing/version tests).

One placement adjustment made during execution, not a deviation from any stated constraint: `from firestarter import messages` was initially added directly above `from firestarter.sdp_capability import sdp_capability` (adjacent to the resolver's new code); `ruff check`'s `I001` (import-block sort) reported it out of order, so it was moved to alphabetical position ahead of `from firestarter.chip_resolver import resolve_chip`. Verified with `ruff check`/`ruff format --check` after the move — both clean.

## RED Transcripts

**Task 1** (`resolve_error_name` did not exist; `error_name` was absent from `_step_dict`; `SCHEMA_VERSION` was still `"2.0"`) — `python3 -m pytest tests/test_chip_test.py tests/test_diagnostic_report.py tests/test_blast_radius_invariance.py -o addopts="" -q`:

```
8 failed, 304 passed in 5.82s
FAILED tests/test_chip_test.py::test_resolve_error_name_names_the_issue_86_ids
FAILED tests/test_chip_test.py::test_resolve_error_name_is_exhaustive_over_the_catalog
FAILED tests/test_diagnostic_report.py::test_schema_version_2_1_single_sourced
FAILED tests/test_diagnostic_report.py::test_step_dict_emits_the_resolved_error_name_beside_the_code
FAILED tests/test_diagnostic_report.py::test_step_dict_keys_error_name_unconditionally
FAILED tests/test_diagnostic_report.py::test_schema_version_is_two_one
FAILED tests/test_blast_radius_invariance.py::test_to_dict_steps_element_0_key_list_is_pinned
FAILED tests/test_blast_radius_invariance.py::test_schema_version_is_pinned
```

Post-implementation: `312 passed` (304 baseline + 8).

**Task 2** (degradation-contract and invariance tests): all 8 new tests were GREEN immediately on first run — Task 1's implementation already satisfied the full degradation contract (non-raising `dict.get`, no `DEBUG_CATALOG` fallback, unconditional keying) and `dedup_fingerprint`'s explicit allow-list already excluded `error_code`/`error_name` from hashing, so there was no RED to observe for this task's own assertions. This matches the plan's own hedge ("write these RED first where a RED is possible") — verified by running the 6 `test_chip_test.py` legs and the full suite:

```
tests/test_chip_test.py -k "resolve_error_name": 6 passed, 156 deselected in 0.49s
tests/test_chip_test.py + tests/test_diagnostic_report.py + tests/test_blast_radius_invariance.py: 320 passed in 3.57s
```

## Issues Encountered

None beyond the import-order fixup noted above.

## Verification Discipline

Every verify leg named in the plan was run and its actual output inspected, not merely its exit code:

- `python3 -m pytest tests/test_chip_test.py tests/test_diagnostic_report.py tests/test_blast_radius_invariance.py -o addopts="" -q` — RED (8 failed, 304 passed) before implementation, GREEN (312 passed) after. Confirmed the failures were the expected 8, not an unrelated collection error.
- The `build_shape` smoke test (`python3 -c "..."`) printed `OK 2.1 6` — confirms `schema_version` and unconditional keying on a real fixture-built report, not just on `_minimal_report`'s synthetic shape.
- `test "$(/usr/bin/grep -o '"2\.1"' firestarter/diagnostic_report.py | wc -l)" = 1` used `wc -l` per this batch's known `grep -c`-exits-1-on-zero trap, and used `/usr/bin/grep` (not the devcontainer's ugrep) per the known `.gitignore`-honoring under-scan trap. Printed `GATE_PASS`.
- The no-comment gate used `^\+[[:space:]]*#` (not the batch's known-broken `^\+\+\+` GNU-BRE trap) and captured the diff into a variable before piping, per the plan's own stated smoke-test protocol. Ran twice — after Task 1's commit and again after Task 2's — both printed `NO COMMENT ADDED`.
- Full suite: `python3 -m pytest tests/ -o addopts="" -q` under `.venv311` (Python 3.11.16, confirmed via `python -V` and `firestarter.__file__` resolving inside the venv, not the devcontainer's 3.12) — `1949 passed in 193.36s`, with the pass-count line visible because `-o addopts=""` overrode the doubled-`-q`-suppression trap.
- `ruff check .` — `All checks passed!` (repo-wide, including this batch's files). `ruff format --check .` (repo-wide) reported 2 pre-existing unformatted files (`.github/scripts/update_version.py`, `tools/planning_citation_gate.py`) that are outside this plan's `files_modified` and confirmed via `git diff --stat` against the anchor sha to be byte-identical to the pre-task tree — out of scope per the deviation rules' scope boundary, not fixed, not regressed by this change. Scoped `ruff format --check` over exactly this plan's 5 files: `5 files already formatted`.
- The Python 3.11 CI-fidelity leg ran successfully against the pre-existing `.venv311` (not freshly provisioned via `uv venv`, since it already existed and was CI-parity per the execution environment's own instructions) — full suite green there too.

## Known Stubs

None.

## Threat Flags

None — this plan's threat model (T-nb9-01 through T-nb9-08, T-nb9-SC) covers the full surface introduced; no new surface fell outside it.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

`resolve_error_name` and the `error_name` key are available to any future consumer of `diagnostic_report.to_dict()` — the saved `dev-test-<chip>.json`, the fenced JSON block in the saved `.md`, and the filed GitHub issue body all pick it up with no further wiring, since `submit.build_body`'s value-scrubbing is generic over dict values. No blockers.

## Self-Check: PASSED

All 5 modified files found on disk; both commits (`a969fa8`, `e4cbfdf`) found in `firestarter_app`'s history on branch `v1.39-protocol-0x05-write-correctness`.
