---
phase: 181-report-fidelity-schema-2-0-canonical-naming-hygiene-close
plan: 01
subsystem: report-fidelity
tags: [diagnostic-report, schema-versioning, dedup-fingerprint, blast-radius-invariance, pytest]

requires:
  - phase: 178-fault-attribution-the-two-axis-vocabulary
    provides: "SCHEMA_VERSION 1.8, the run_status/status export precedent (ec1db5c) this plan's is_uv change mirrors"
  - phase: 174-blast-radius-invariance-harness
    provides: "the 19 FROZEN_HASHES literals, the seven D-07 key-list pins, and the anti-vacuity idiom this plan extends"
provides:
  - "to_dict()'s new top-level is_uv key (RPT-A4), read off Plan.is_uv, never re-derived"
  - "SCHEMA_VERSION at 2.0 (RPT-E1), with every literal assertion that named 1.8 moved in the same commit"
  - "proof, not projection, that an additive top-level key cannot re-key any of the 19 frozen dedup hashes (D-16) -- the mechanism every remaining plan in this phase depends on"
  - "a forward-only parse proof for the two frozen pre-2.0 devtest-triage fixtures (RPT-E2)"
  - "RPT-E3's re-anchoring from the retired GATE-06 ledger onto the surviving 19-literal + two-commit-rule mechanism (D-15)"
affects: [181-02, 181-05, 181-06, 181-07]

actuals:
  tokens: 6432
  tasks: 3
  commits: 6

tech-stack:
  added: []
  patterns:
    - "read-off-the-single-decision carry-through (RPT-A4): to_dict()['is_uv'] = self.plan.is_uv, never recomputed from a proxy"
    - "additive-key-cannot-re-key: dedup_fingerprint's explicit five-entry allow-list with no reflection over dataclass fields"
    - "in-memory mapping mutation for anti-vacuity (never a fixture file, never production code)"

key-files:
  created:
    - .planning/phases/181-report-fidelity-schema-2-0-canonical-naming-hygiene-close/evidence/181-01-frozen-hash-invariance.txt
    - .planning/phases/181-report-fidelity-schema-2-0-canonical-naming-hygiene-close/evidence/181-01-forward-only-parse.txt
    - .planning/phases/181-report-fidelity-schema-2-0-canonical-naming-hygiene-close/evidence/181-01-key-pin-planted-red.txt
  modified:
    - firestarter_app/firestarter/diagnostic_report.py
    - firestarter_app/tests/test_blast_radius_invariance.py
    - firestarter_app/tests/test_diagnostic_report.py
    - firestarter_app/tests/fixtures/reports/*.json (19 committed snapshots, regenerated)

key-decisions:
  - "SCHEMA_VERSION moved 1.8 -> 2.0 in the same commit as is_uv and the _TO_DICT_KEYS pin (D-13/D-14), matching the ec1db5c precedent exactly."
  - "Renamed both of test_diagnostic_report.py's schema-version tests (test_schema_version_1_8_single_sourced -> test_schema_version_2_0_single_sourced, test_schema_version_is_one_eight -> test_schema_version_is_two_oh) and their literal-count/triple-equality assertions, following the identical rename precedent set at every prior schema bump (1.3->1.4, 1.5->1.6, 1.6->1.7, 1.7->1.8, confirmed via git history of ec1db5c). The plan's <action> named only the :1489 assertion by content; the paired source-census assertion at the (then) :1213 line (`source.count('\"1.8\"') == 1`) would otherwise fail the moment SCHEMA_VERSION's only quoted-\"1.8\" occurrence in diagnostic_report.py disappeared -- documented here as the rationale that would otherwise have been a source comment."
  - "Task 1's tracer feedback gate was run explicitly: all six of Task 1's <verify> legs were re-executed post-commit before starting Task 2, per the auto-mode branch of the tracer feedback gate protocol. All six passed; expansion proceeded without a checkpoint."
  - "Removed four stale __pycache__ .pyc files (and, more broadly, cleared tests/, tools/, and firestarter/ __pycache__ dirs) left over from the retired tests/test_rekey_ledger.py module -- gitignored, untracked bytecode cache, not git history -- because a stale compiled cache of the OLD test_blast_radius_invariance.py source still contained the string 'check_rekey_ledger' and was tripping Task 3's grep-based verify leg. Deleting cache files by explicit path is not a git clean operation and touches nothing tracked."

requirements-completed: [RPT-A4, RPT-E1, RPT-E2, RPT-E3]

coverage:
  - id: D1
    description: "to_dict() carries a top-level boolean is_uv read off the single derive_plan decision (self.plan.is_uv), never recomputed from a proxy"
    requirement: RPT-A4
    verification:
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py#test_to_dict_top_level_key_list_is_pinned"
        status: pass
      - kind: unit
        ref: "AST leg (Task 1 verify): to_dict_keys=14, is_uv_source=self.plan.is_uv"
        status: pass
    human_judgment: false
  - id: D2
    description: "SCHEMA_VERSION reads 2.0, and every literal assertion that named 1.8 moved with it in the same commit"
    requirement: RPT-E1
    verification:
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py#test_schema_version_is_pinned"
        status: pass
      - kind: unit
        ref: "tests/test_diagnostic_report.py#test_schema_version_is_two_oh, tests/test_diagnostic_report.py#test_schema_version_2_0_single_sourced"
        status: pass
    human_judgment: false
  - id: D3
    description: "All 19 FROZEN_HASHES literals in tests/fixtures/report_shapes.py stay byte-identical to app base 04fd982 -- the D-16 headline claim"
    requirement: RPT-E1
    verification:
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py#test_dedup_fingerprint_is_frozen (19-way parametrized)"
        status: pass
      - kind: other
        ref: "git diff 04fd982 -- tests/fixtures/report_shapes.py, literal-line count leg"
        status: pass
    human_judgment: false
  - id: D4
    description: "Both frozen pre-2.0 devtest-triage fixtures (schema 1.2 and 1.4) still parse under 2.0, carrying locked_steps/vpp_mv/vpe_mv, with neither fixture file modified"
    requirement: RPT-E2
    verification:
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py#test_frozen_pre_2_0_fixtures_still_parse_forward_only"
        status: pass
    human_judgment: false
  - id: D5
    description: "RPT-E3 re-anchors from the retired GATE-06 ledger onto the 19 absolute FROZEN_HASHES literals plus the two-commit review rule; the exception clause discharges as empty"
    requirement: RPT-E3
    verification:
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py module docstring + grep leg for 'retired'"
        status: pass
    human_judgment: false
  - id: D6
    description: "The key-list pin was observed RED in both drift directions and against an empty expected list, in-memory only, no fixture written"
    verification:
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py#test_the_to_dict_key_pin_reddens_on_a_planted_added_and_removed_key, #test_the_to_dict_key_pin_is_not_vacuous_against_an_empty_expected_list"
        status: pass
    human_judgment: false
  - id: D7
    description: "Whole-repo porcelain across the meta repo, the firmware submodule, and the app repo after this plan's own commits"
    verification:
      - kind: other
        ref: "git -C /workspaces/firestarter status --porcelain (clean); git -C /workspaces/firestarter_app status --porcelain scoped to this plan's own files (clean)"
        status: unknown
    human_judgment: true
    rationale: "A concurrent, unrelated /gsd-debug session (see .planning/debug/beta-probe-empty-input.md, status: investigating, present as an untracked file before this plan started) is actively editing firestarter_app/firestarter/serial_comm.py and has added an untracked firestarter_app/tests/test_probe_spurious_setup_ack.py in the shared working tree. Neither file is in this plan's files_modified list, neither is touched by this plan, and per the deviation-rule scope boundary this plan must not revert, stash, or otherwise act on unrelated work outside its own scope. Full detail under 'Known Environmental Condition' below -- a human should confirm this is understood as external, not a defect in this plan's own work, before treating the whole-repo porcelain acceptance criterion as met."

duration: 42min
completed: 2026-09-09
status: complete
---

# Phase 181 Plan 01: End-to-end additive-key/frozen-hash proof (RPT-A4, RPT-E1, RPT-E2, RPT-E3) Summary

**`plan.is_uv` reaches `to_dict()` as a top-level `is_uv` boolean, `SCHEMA_VERSION` moves 1.8 -> 2.0, and all 19 frozen dedup hashes are measured byte-identical to app base `04fd982` -- the mechanism every later plan in this phase depends on, proven rather than projected.**

## Performance

- **Duration:** 42 min
- **Started:** 2026-09-09T09:28:00Z (approx., pre-instrumentation)
- **Completed:** 2026-09-09T10:10:00Z (approx.)
- **Tasks:** 3 of 3 completed
- **Files modified:** 3 product/test files + 19 regenerated JSON snapshots + 3 evidence transcripts (app repo) + 3 evidence transcripts + this SUMMARY (meta repo)

## Accomplishments

- `to_dict()` gained a fourteenth top-level key, `is_uv`, whose value expression is the attribute chain `self.plan.is_uv` -- proven by AST inspection, never a call, never a recomputation from `electrical-type` or `algorithm`.
- `SCHEMA_VERSION` moved from `"1.8"` to `"2.0"`; every literal assertion across both test files that named `1.8` moved in the same commit as the key change (D-13/D-14), matching the `ec1db5c` precedent's discipline exactly.
- The `_TO_DICT_KEYS` pin gained `"is_uv"` (alphabetically sorted) and its counted-keys docstring moved from "thirteen" to "fourteen"; `test_schema_version_is_pinned`'s triple-equality and failure message moved to `2.0`, past tense.
- All 19 committed report snapshots under `tests/fixtures/reports/` were regenerated via `tools/snapshot_report_shapes.py`; every one of the 19 diffs is confined to exactly the `is_uv` and `schema_version` lines (verified per-file, not just in aggregate).
- **D-16's headline claim is now a measured fact, not a projection:** `git diff 04fd982 -- tests/fixtures/report_shapes.py` shows zero added or removed twelve-hex frozen-hash literal lines. All 19 `FROZEN_HASHES` entries are byte-identical to the phase base.
- RPT-E2: both frozen pre-2.0 devtest-triage fixtures (schema `1.2` and `1.4`) still parse under `_extract_fenced_report` and still carry `banner.locked_steps`, `voltage.vpp_mv`, `voltage.vpe_mv` -- the three keys this phase deletes downstream -- with neither fixture file touched. A negative control confirms a body missing `schema_version` returns `None`, so the presence-only rule is a real gate.
- RPT-E3: the module docstring of `test_blast_radius_invariance.py` now states, in writing, that GATE-06's `RK-174-` ledger is retired and that RPT-E3's anchor is now the 19 absolute `FROZEN_HASHES` literals plus the two-commit review rule quoted verbatim from `test_dedup_fingerprint_is_frozen`'s own failure message. Phase 181 declares zero re-keys, so the exception clause discharges as empty.
- The `to_dict()` key-list pin was observed RED, in-memory only, against a planted added key, a planted removed key, and an empty expected list -- proving the pin the rest of this phase relies on is sensitive, not vacuously green.
- Zero deletions, zero firmware lines touched, zero `#` comments added (measured via `tokenize` COMMENT-token census: `diagnostic_report.py` at 214/214, `test_diagnostic_report.py` at 183/183, `test_blast_radius_invariance.py` at 0/0 -- all at their ceilings, none exceeded).

## Task Commits

Each task was committed atomically, split across the app submodule (code) and the meta repo (evidence):

1. **Task 1: End-to-end is_uv/schema-2.0/frozen-hash proof**
   - `4336561` (feat, app repo): `is_uv` key, `SCHEMA_VERSION` 2.0, `_TO_DICT_KEYS` pin move, 19 regenerated snapshots
   - `dd3b53bb` (docs, meta repo): `181-01-frozen-hash-invariance.txt`
2. **Task 2: RPT-E2 forward-only parse**
   - `2fe0cc6` (test, app repo): `test_frozen_pre_2_0_fixtures_still_parse_forward_only`
   - `30602deb` (docs, meta repo): `181-01-forward-only-parse.txt`
3. **Task 3: Anti-vacuity key-pin RED proof + RPT-E3 re-anchoring**
   - `90a5472` (test, app repo): two new anti-vacuity tests + RPT-E3 module docstring paragraph
   - `4349e613` (docs, meta repo): `181-01-key-pin-planted-red.txt`

**Plan metadata commit:** this SUMMARY.md, committed separately per the sequential-executor protocol (STATE.md/ROADMAP.md are NOT touched -- owned by the orchestrator).

_TDD note: all three tasks carry `tdd="true"`. Task 1 (`type="tracer"`) was executed and verified end-to-end in one commit per the plan's own instruction (not split into RED/GREEN/REFACTOR commits, matching the plan's explicit "ONE commit" directive); the tracer feedback gate (all six `<verify>` legs) was then re-run post-commit before Task 2 began, per the auto-mode branch of the tracer protocol. Tasks 2 and 3 each landed their new test(s) and the production-side proof together, since no production code changed in either task -- only test additions and docstring extensions, matching each task's own `<action>` (RPT-E2 and Task 3 add tests against already-existing behavior, never introduce a RED against not-yet-written production code)._

## Files Created/Modified

- `firestarter_app/firestarter/diagnostic_report.py` -- `SCHEMA_VERSION` to `"2.0"`; `to_dict()` gains `is_uv: self.plan.is_uv`; docstring extended with the RPT-A4/D-16 exclusion sentence
- `firestarter_app/tests/test_blast_radius_invariance.py` -- `_TO_DICT_KEYS` +`is_uv`; `test_schema_version_is_pinned` moved to 2.0; new `test_frozen_pre_2_0_fixtures_still_parse_forward_only`; two new anti-vacuity tests for the key-list pin; module docstring gains the RPT-E3 re-anchoring paragraph
- `firestarter_app/tests/test_diagnostic_report.py` -- both schema-version tests renamed and moved to 2.0 (see Decisions)
- `firestarter_app/tests/fixtures/reports/*.json` (19 files) -- regenerated; each diff confined to `is_uv` and `schema_version`
- `.planning/phases/181-.../evidence/181-01-frozen-hash-invariance.txt` -- D-16 headline transcript
- `.planning/phases/181-.../evidence/181-01-forward-only-parse.txt` -- RPT-E2 transcript
- `.planning/phases/181-.../evidence/181-01-key-pin-planted-red.txt` -- anti-vacuity RED-proof transcript

## Decisions Made

See `key-decisions` in frontmatter. In summary: the schema-version test renames in `test_diagnostic_report.py` were necessary and not explicitly named by the plan's `<action>` text, so they are recorded here per `/workspaces/CLAUDE.md`'s rule that rationale which would otherwise be a source comment belongs in the SUMMARY. The tracer feedback gate was explicitly re-run per protocol. Stale `__pycache__` bytecode from the already-deleted `test_rekey_ledger.py` module was cleared (gitignored, untracked, not a `git clean` operation) because it was tripping a grep-based verify leg with a string from an old compiled cache, not from any tracked source.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Renamed and updated the two paired schema-version tests in `test_diagnostic_report.py`**
- **Found during:** Task 1
- **Issue:** The plan's `<action>` named only the `:1489` `SCHEMA_VERSION == "1.8"` assertion. A second, tightly-coupled test (`test_schema_version_1_8_single_sourced`, asserting `source.count('"1.8"') == 1` over `diagnostic_report.py`'s own source) would break the instant `SCHEMA_VERSION` became `"2.0"`, since `"1.8"` no longer appears anywhere in that module's source.
- **Fix:** Renamed `test_schema_version_1_8_single_sourced` -> `test_schema_version_2_0_single_sourced` (count assertion now `'"2.0"'`) and `test_schema_version_is_one_eight` -> `test_schema_version_is_two_oh` (assertion now `"2.0"`), updating both docstrings, following the exact rename precedent set at every prior schema bump (confirmed via `git show ec1db5c` for the 1.7->1.8 rename).
- **Files modified:** `firestarter_app/tests/test_diagnostic_report.py`
- **Verification:** `pytest tests/test_diagnostic_report.py -o addopts="" -q` -- `77 passed` (matches pre-edit baseline exactly)
- **Committed in:** `4336561`

**2. [Rule 3 - Blocking] Cleared stale `__pycache__` bytecode referencing the retired `check_rekey_ledger` module**
- **Found during:** Task 3
- **Issue:** Task 3's verify leg `! grep -rqF 'check_rekey_ledger' tests/ firestarter/ tools/` failed against a stale, gitignored, untracked `.pyc` compiled cache of an OLD version of `test_blast_radius_invariance.py` (from before the 2026-09-08 ledger retirement) still containing that string.
- **Fix:** Removed the stale `.pyc` files and cleared `__pycache__` directories under `tests/`, `tools/`, `firestarter/` (bytecode cache only, not `git clean`, nothing tracked touched).
- **Files modified:** none tracked (cache only)
- **Verification:** `pytest tests/test_blast_radius_invariance.py -o addopts="" -q` -- `103 passed` after clearing; grep leg passes
- **Committed in:** n/a (no tracked files changed)

---

**Total deviations:** 2 auto-fixed (1 bug, 1 blocking). **Impact:** Both were necessary to keep the touched test files internally consistent and green; neither widened this plan's scope beyond what RPT-E1/D-13/D-14 already required.

## Issues Encountered

### Known Environmental Condition -- concurrent, unrelated session dirt (not caused by this plan)

`firestarter_app/firestarter/serial_comm.py` carries uncommitted changes, and `firestarter_app/tests/test_probe_spurious_setup_ack.py` exists untracked, in the shared working tree. Neither file is in this plan's `files_modified` list and neither was touched by any task in this plan. Evidence this is a separate, concurrently active session: `.planning/debug/beta-probe-empty-input.md` (an untracked meta-repo file, `status: investigating`, `created: 2026-09-09T09:11:18Z`) was already present before this plan started and describes an active `/gsd-debug` investigation into a serial-open race on Uno-class boards -- directly matching the `serial_comm.py` diff's content (`MSG_ERR_EMPTY_INPUT`, `SETUP_ACK_RECOVERY_TIMEOUT`). `serial_comm.py`'s mtime (09:31:33) is after `diagnostic_report.py`'s (09:29:40), confirming the edit landed during this plan's execution window, not before it.

Per the deviation-rule scope boundary, this plan does not touch, revert, stash, or commit that unrelated work. As a direct consequence, two of this plan's porcelain checks read dirty for reasons outside this plan's control:

- `git -C /workspaces/firestarter status --porcelain` -- **clean** (firmware submodule untouched, as required).
- `git -C /workspaces/firestarter_app status --porcelain firestarter/` -- **dirty** (`serial_comm.py` only; not this plan's file).
- `git -C /workspaces/firestarter_app status --porcelain` -- **dirty** (`serial_comm.py` + untracked `test_probe_spurious_setup_ack.py`; neither this plan's file).

Scoped to this plan's own files (`git status --porcelain -- firestarter/diagnostic_report.py tests/test_blast_radius_invariance.py tests/test_diagnostic_report.py tests/fixtures/reports/ tests/fixtures/report_shapes.py`), the result is empty -- everything this plan touched is committed. This is flagged as `human_judgment: true` in the coverage block above (D7) rather than silently marked passing, so a human confirms the read before the whole-repo porcelain acceptance criterion is treated as met.

## User Setup Required

None -- no external service configuration required.

## Next Phase Readiness

The mechanism every remaining plan in this phase depends on -- an additive report key cannot re-key a filed report -- is now proven end to end and measured, not projected: 19/19 frozen dedup hashes byte-identical, `to_dict()` at fourteen keys, `SCHEMA_VERSION` at `2.0`. Plan `181-02`'s deletions (the largest surface change in the milestone, per D-08) can now land against a gate that has itself been observed to catch a re-key, not merely assumed to.

**Blocker for the phase, not for this plan:** the whole-repo porcelain state depends on an unrelated concurrent session's work-in-progress on `serial_comm.py` completing (committing or reverting) before any later plan in this phase runs a whole-repo porcelain leg of its own. This plan's own work is fully committed and does not depend on that session resolving.

## Self-Check: PASSED

- All three evidence transcripts, `diagnostic_report.py`, `test_blast_radius_invariance.py`, and `test_diagnostic_report.py` confirmed present on disk with `[ -f ]`.
- All six commit hashes (`4336561`, `2fe0cc6`, `90a5472` in `firestarter_app`; `dd3b53bb`, `30602deb`, `4349e613` in the meta repo) confirmed present via `git log --oneline --all`.
- `tests/test_blast_radius_invariance.py -o addopts="" -q` re-run: `103 passed`.
- `tests/test_diagnostic_report.py -o addopts="" -q` re-run: `77 passed` (matches pre-plan baseline exactly).
- All plan-level `<verification>` items re-confirmed: 19/19 frozen hashes byte-identical; `to_dict()` fourteen keys with `is_uv` reading `self.plan.is_uv`; `SCHEMA_VERSION` `2.0` with no `"1.8"` literal in the pin module; `tools/snapshot_report_shapes.py --check` exits 0; both frozen devtest-triage fixtures parse under 2.0 unmodified; the key-list pin observed RED in both drift directions plus the empty-list control; `tokenize` comment counts at ceiling (214/183/0, none exceeded).
- Porcelain: firmware submodule clean; this plan's own files clean when scoped; whole-app-repo leg reads dirty due to the documented unrelated concurrent session (see "Known Environmental Condition" above) -- not a failure of this plan's own work.

---
*Phase: 181-report-fidelity-schema-2-0-canonical-naming-hygiene-close*
*Completed: 2026-09-09*
