---
phase: 134-the-plan-derived-sdp-oracle-in-dev-test
plan: 06
subsystem: testing
tags: [python, pytest, diagnostic_report.py, sdp, schema-version, dedup, mypy]

# Dependency graph
requires:
  - phase: 134-04
    provides: "sdp_hold_state(plan, results) -> str and sdp_oracle_applicable(plan) -> bool --
      the pure, engine-side HELD/NOT-HELD/NOT-RUN(reason) derivation; SDP_HOLD_HELD/
      SDP_HOLD_NOT_HELD/SDP_HOLD_NOT_RUN report-value constants"
provides:
  - "DiagnosticReport.sdp_hold_state: str = \"\" -- a plain string field, never a bool, never a
    key named locked/protection_enabled (P-06 prevention 3)"
  - "the eleventh to_dict() key: \"sdp_hold_state\", emitted verbatim (measured discrepancy: the
    dict already had TEN keys before this plan, not the plan's stated nine)"
  - "render()'s own sdp_hold_state console row, beside the banner row -- never folded into a
    step's reason, which never reaches the console (D-07)"
  - "SCHEMA_VERSION bumped 1.2 -> 1.3, single-sourced, comment ladder extended with the 1.3
    entry and its additive argument"
  - "a committed recursive no-boolean assertion over the WHOLE to_dict() output (P-06
    prevention 3, D-10) -- no bool under any key containing lock/protect, anywhere"
  - "a committed D-11 re-key proof: two reports differing only in an SDP step's verdict
    produce different dedup_fingerprint values, with the D-11 cost recorded (not fixed) beside
    dedup_fingerprint's own body, which stays byte-unchanged"
affects: [134-07]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "The report's own hold-state field is the CARRIAGE half only -- the VALUE is assigned by
      cli_handlers.py in a later plan (134-07) from chip_test.sdp_hold_state(plan, results);
      DiagnosticReport itself never derives it, matching this class's own declared-non-registry
      discipline (zero op vocabulary, re-measured every run by an AST inversion guard)."
    - "A cost recorded BESIDE a function, not inside its body -- the D-11 comment sits
      immediately above dedup_fingerprint's def line so the acceptance criterion's own
      'no change to dedup_fingerprint's body' grep holds, while the cost is still documented at
      the one place a future reader would look for it."
    - "Description of the six new SDP op strings is deliberately NOT spelled out as hyphenated
      literals anywhere in diagnostic_report.py, including in prose comments -- this module is a
      declared non-registry re-measured every run for zero op vocabulary (hyphenated op-value
      string literals included), so even an explanatory comment naming them would trip the same
      structural guard a real `if result.op == ...` branch would."

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/diagnostic_report.py
    - firestarter_app/tests/test_diagnostic_report.py
    - firestarter_app/tests/test_parse_devtest_issue.py

key-decisions:
  - "MEASURED DISCREPANCY (same project convention as 134-02's 'exactly two' and 134-04's
    'n_ran=6, not 5' findings, recorded rather than silently reconciled): this plan's own
    PLAN.md read to_dict()'s prior key count as nine ('to_dict at :436, whose nine keys are at
    :443-454'). The live count on disk at plan time was already TEN (schema_version, generated,
    auto_capture, transport_health, steps, banner, voltage, is_submittable, dedup_fingerprint,
    db_diff) -- schema_version 1.1's ladder_state addition and 1.2's write-partial op both
    landed as NEW to_dict() keys in their own right over the module's history, not merely new
    vocabulary inside existing keys. sdp_hold_state is therefore the ELEVENTH key, not the
    tenth. Recorded in the SCHEMA_VERSION 1.3 comment ladder and here; does not change the
    bump's own argument (still purely additive, tools/parse_devtest_issue.py still tolerant by
    presence-only)."
  - "The D-11 cost comment beside dedup_fingerprint deliberately does not spell out the six new
    SDP op strings by name (not even as illustrative prose) -- an early draft did, and it tripped
    the plan's own acceptance-criteria grep for hyphenated op-value literals
    (write-inhibited/sdp-lock/sdp-unlock/write-baseline), which exists specifically so a
    prose-only mention cannot silently smuggle op vocabulary into this declared non-registry.
    Reworded to point at chip_test._SDP_LEG_STEP_ORDER by name instead of restating the tuple's
    contents."
  - "tests/test_parse_devtest_issue.py::test_detect_realistic_dev_test_body_parses hardcoded the
    literal \"1.2\" (Rule 1 auto-fix, not part of this plan's declared file scope but a direct,
    necessary consequence of the schema bump this plan makes) -- repaired to import and assert
    against SCHEMA_VERSION, matching the single-sourcing discipline every other schema_version
    assertion in that test module and in test_diagnostic_report.py already follows."

requirements-completed: []
# This plan ticks NOTHING, per its own dispatch scope and this project's standing convention
# (executors have prematurely ticked multi-plan requirements 4x in Phase 116). LEG-12 is named
# in this plan's frontmatter `requirements:` field as CONTRIBUTES-TO-BUT-MUST-NOT-TICK: this
# plan supplies the field, the to_dict() key, the console row and the schema bump -- the
# CARRIAGE half only. LEG-12's own text requires the field to be rendered on every run against
# an ALLOW chip, which needs the VALUE assigned from sdp_hold_state(plan, results) inside
# cli_handlers.py -- that assignment, and the requirement's close, belong to plan 134-07.
# `git diff -- .planning/REQUIREMENTS.md` shows zero changes from this plan (confirmed below).

coverage:
  - id: D1
    description: "DiagnosticReport carries sdp_hold_state: str (default \"\"), serialised
      verbatim as an eleventh to_dict() key and rendered as its own console row beside the
      banner row -- never derived here, never a bool, SCHEMA_VERSION bumped 1.2 -> 1.3."
    requirement: LEG-12
    verification:
      - kind: unit
        ref: "tests/test_diagnostic_report.py::test_hold_state_held_reaches_both_surfaces"
        status: pass
      - kind: unit
        ref: "tests/test_diagnostic_report.py::test_hold_state_not_held_reaches_both_surfaces"
        status: pass
      - kind: unit
        ref: "tests/test_diagnostic_report.py::test_hold_state_not_run_reason_reaches_both_surfaces"
        status: pass
      - kind: unit
        ref: "tests/test_diagnostic_report.py::test_hold_state_is_str_never_bool"
        status: pass
    human_judgment: false
  - id: D2
    description: "A committed recursive gate proves no boolean anywhere in to_dict()'s output
      sits under a key whose lowercased name contains lock or protect (P-06 prevention 3)."
    verification:
      - kind: unit
        ref: "tests/test_diagnostic_report.py::test_hold_state_no_boolean_under_lock_or_protect_key_anywhere_in_to_dict"
        status: pass
    human_judgment: false
  - id: D3
    description: "SCHEMA_VERSION is 1.3, single-sourced (the literal appears exactly once in the
      production module), and tools/parse_devtest_issue.py's presence-only acceptance of
      schema_version is unbroken by the bump."
    verification:
      - kind: unit
        ref: "tests/test_diagnostic_report.py::test_schema_version_1_3_single_sourced"
        status: pass
      - kind: unit
        ref: "tests/test_parse_devtest_issue.py (22 tests, all pass, incl. the repaired literal-1.2 assertion)"
        status: pass
    human_judgment: false
  - id: D4
    description: "dedup_fingerprint is left byte-unchanged (D-11); its re-key cost is recorded
      in a comment beside it; a committed test proves two reports differing only in an SDP
      step's verdict hash differently."
    verification:
      - kind: unit
        ref: "tests/test_diagnostic_report.py::test_dedup_fingerprint_sensitive_to_sdp_step_verdict_change"
        status: pass
      - kind: other
        ref: "git diff -- firestarter/diagnostic_report.py shows zero changes inside dedup_fingerprint's def body"
        status: pass
    human_judgment: false
  - id: D5
    description: "test_op_registration_parity.py's zero-op-vocabulary inversion guard over the
      whole DiagnosticReport class stays green after the field/key/row additions."
    verification:
      - kind: unit
        ref: "tests/test_op_registration_parity.py::test_non_registry_still_has_no_ops"
        status: pass
    human_judgment: false

# Metrics
duration: 20min
completed: 2026-08-04
status: complete
---

# Phase 134 Plan 06: DiagnosticReport's SDP Hold-State Field, Both Surfaces, Schema 1.3 Summary

**Gave `DiagnosticReport` a plain-string `sdp_hold_state` field, an eleventh `to_dict()` key,
and its own `render()` console row, bumped `SCHEMA_VERSION` 1.2 -> 1.3, added a committed
recursive no-boolean gate over the whole output, and proved `dedup_fingerprint`'s D-11 re-key
cost without touching its body.**

## Performance

- **Duration:** 20 min
- **Started:** 2026-08-04T17:39:33Z (134-05's last commit; this plan's context-reading began here)
- **Completed:** 2026-08-04T17:59:45Z (last task commit, submodule)
- **Tasks:** 2
- **Files modified:** 3, all inside `firestarter_app` submodule (1 production, 2 test)

## Accomplishments

- Added `sdp_hold_state: str = ""` to `DiagnosticReport`, positioned last (beside `db_diff`, the
  other handler-assigned field), with a comment naming it a plain `str`, never a `bool`, never a
  `locked`/`protection_enabled`-shaped key (P-06 prevention 3) -- and naming plan `134-07` as the
  plan that assigns its real value from `chip_test.sdp_hold_state(plan, results)`.
- Added `"sdp_hold_state": self.sdp_hold_state` to `to_dict()`'s return dict, emitted verbatim
  with no transform, following `_db_diff_dict`'s generic-serialisation precedent.
- Added the console row in `render()`, immediately after the banner row, with a comment
  recording D-07's reason (the per-step row shows only op/verdict/error_code/fingerprint, so
  `reason` never reaches the console -- this field needed its own row to be visible at all).
- Bumped `SCHEMA_VERSION` from `"1.2"` to `"1.3"`, extending the comment ladder with the 1.3
  entry in the same shape as the 1.1 and 1.2 entries: additive, no consumer breakage, and
  `tools/parse_devtest_issue.py` verified still tolerant (presence-only `schema_version` check).
- Recorded D-11 (the `dedup_fingerprint` re-key cost for all 43 ALLOW chips) as a comment
  immediately above `dedup_fingerprint`'s `def` line -- the function's own body is left
  byte-unchanged (confirmed by `git diff`), and the comment deliberately does NOT spell out the
  six new SDP op strings by name (an early draft did and tripped the plan's own op-vocabulary
  grep; reworded to point at `chip_test._SDP_LEG_STEP_ORDER` instead).
- Added 5 `pytest -k "hold"`-selected tests: `HELD`/`NOT-HELD`/`NOT-RUN: <reason>` each proven to
  reach both `to_dict()` and `render()`'s output text; a recursive walk of the whole `to_dict()`
  tree asserting no `bool` sits under any key containing `lock`/`protect`, run against all three
  hold-state values; a direct `isinstance(..., str)` / `not isinstance(..., bool)` pin.
- Added `test_schema_version_1_3_single_sourced` (asserts `to_dict()["schema_version"]` against
  the imported constant, and that the production module's own quoted `"1.3"` literal appears
  exactly once) and `test_dedup_fingerprint_sensitive_to_sdp_step_verdict_change` (D-11's re-key
  proof: two reports differing only in an SDP step's verdict hash differently).
- Repaired `tests/test_parse_devtest_issue.py::test_detect_realistic_dev_test_body_parses`,
  which hardcoded the literal `"1.2"` and broke on the bump; now imports and asserts against
  `SCHEMA_VERSION`, matching the rest of that test module's own single-sourcing discipline.
- **Ticked NOTHING** in `.planning/REQUIREMENTS.md` -- confirmed by `git status`/`git diff`
  showing no change to that file. LEG-12 stays `[ ]`; this plan supplies only the carriage half
  (the field, the key, the row, the schema bump), and plan `134-07` closes it by assigning the
  real value from `chip_test.sdp_hold_state`.

## Task Commits

Each task was committed atomically, inside the `firestarter_app` submodule on
`gsd/v1.30-sdp-surface-retirement`:

1. **Task 1: the string field, the eleventh `to_dict()` key, the console row, and the 1.3 bump**
   - `c461cc0` (feat)
2. **Task 2: the no-boolean gate, both-surface assertions, and D-11's re-key proof** - `8f3c712`
   (test)

**Plan metadata:** committed with this SUMMARY (docs: complete plan), in the meta repo.

## Files Created/Modified

- `firestarter_app/firestarter/diagnostic_report.py` -- `sdp_hold_state: str = ""` dataclass
  field; the `"sdp_hold_state"` `to_dict()` key; `render()`'s own console row; `SCHEMA_VERSION`
  bumped `1.2` -> `1.3` with its comment-ladder entry; a D-11 cost comment beside
  `dedup_fingerprint` (its body left byte-unchanged).
- `firestarter_app/tests/test_diagnostic_report.py` -- 5 hold-state tests (both-surface proofs
  for `HELD`/`NOT-HELD`/`NOT-RUN: <reason>`, the recursive no-boolean gate, the str-never-bool
  pin), 1 schema single-source test, 1 D-11 dedup re-key proof, plus an Evidence Ceiling module
  comment and 3 new imports (`SDP_HOLD_HELD`/`SDP_HOLD_NOT_HELD`/`SDP_HOLD_NOT_RUN`).
- `firestarter_app/tests/test_parse_devtest_issue.py` -- imported `SCHEMA_VERSION`; repaired the
  one test that hardcoded the now-stale `"1.2"` literal.

## Decisions Made

- **MEASURED DISCREPANCY** (this plan's PLAN.md read `to_dict()`'s prior key count as nine; the
  live count was already ten) -- `sdp_hold_state` is the eleventh key, not the tenth. Recorded in
  the `SCHEMA_VERSION` 1.3 comment ladder and above under key-decisions; does not change the
  bump's own additive argument.
- **The D-11 cost comment names `_SDP_LEG_STEP_ORDER` by reference, never the six op strings by
  name** -- an early draft spelled them out in prose and tripped the plan's own
  `grep -c 'OP_WRITE_INHIBITED\|...\|write-baseline'` acceptance criterion, which exists
  specifically to catch a comment (not just code) smuggling op vocabulary into this declared
  non-registry.
- **`tests/test_parse_devtest_issue.py`'s hardcoded `"1.2"` literal was repaired** (Rule 1
  auto-fix) rather than left broken -- a direct, necessary consequence of this plan's own schema
  bump, not scope creep; the fix makes that assertion match the single-sourcing discipline every
  other `schema_version` assertion in the test suite already follows.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `tests/test_parse_devtest_issue.py::test_detect_realistic_dev_test_body_parses`
hardcoded the stale `"1.2"` literal**
- **Found during:** Task 1's own verify command (`pytest tests/test_diagnostic_report.py
  tests/test_op_registration_parity.py tests/test_parse_devtest_issue.py -o addopts="" -q`)
- **Issue:** This test builds a report via the CURRENT builders (its own docstring says so) but
  asserted `obj["schema_version"] == "1.2"` literally, instead of importing `SCHEMA_VERSION` --
  the one shipped test in the whole suite that restated the value as a literal rather than
  importing it. It broke the instant `SCHEMA_VERSION` bumped to `"1.3"`.
- **Fix:** Imported `SCHEMA_VERSION` from `firestarter.diagnostic_report` and asserted against
  it, matching this test module's own comment ("this test builds a report via the CURRENT
  builders, so it reflects the CURRENT SCHEMA_VERSION") and every other schema_version assertion
  elsewhere in the test suite.
- **Files modified:** `tests/test_parse_devtest_issue.py`
- **Verification:** `pytest tests/test_parse_devtest_issue.py -o addopts="" -q` -- 22 passed.
- **Commit:** `c461cc0`

**2. [Rule 1 - Bug] the first draft of the D-11 cost comment spelled out the six SDP op strings
literally, tripping the plan's own op-vocabulary acceptance-criteria grep**
- **Found during:** Task 1, self-check against the plan's own acceptance criteria
  (`grep -c 'OP_WRITE_INHIBITED\|OP_SDP_LOCK\|OP_SDP_UNLOCK\|OP_WRITE_BASELINE\|write-inhibited\|sdp-lock\|sdp-unlock\|write-baseline'
  firestarter/diagnostic_report.py` must return 0)
- **Issue:** The comment recording D-11 beside `dedup_fingerprint` named the six new SDP steps
  by their hyphenated op-string values ("write-baseline-b/a, sdp-lock, write-inhibited,
  sdp-unlock, write-restored") as illustrative prose -- a plain-text grep (and the real AST
  inversion guard, `test_non_registry_still_has_no_ops`) cannot distinguish a comment from code,
  so this would have re-introduced op vocabulary into a class this module explicitly declares
  carries none.
- **Fix:** Reworded the comment to point at `chip_test._SDP_LEG_STEP_ORDER` by name instead of
  restating its six op strings.
- **Files modified:** `firestarter/diagnostic_report.py`
- **Verification:** the grep above returns `0`; `test_non_registry_still_has_no_ops` passes.
- **Commit:** `c461cc0`

---

**Total deviations:** 2 auto-fixed (1 Rule 1 test repair made necessary by this plan's own
schema bump, 1 Rule 1 documentation-only fix caught by the plan's own acceptance-criteria grep
before it ever reached a commit).
**Impact on plan:** Neither affects behavior. No scope creep.

## Out-of-Scope Finding Confirmed Still Recorded and Still Deferred

Plan `134-03`'s measured `build_db_diff`/`ladder_state` finding (a genuinely-passing ALLOW
chip's SDP-leg run now attaches an `"indeterminate"`-classified `Fingerprint`, which routes
`build_db_diff`'s `ladder_state` to `_LADDER_NONE` rather than `_LADDER_COMMUNITY_REPORTED`) is
inside THIS plan's file scope (`diagnostic_report.py`) but was **not touched** here. Confirmed
still recorded, unchanged, in `134-03-SUMMARY.md`'s Deviation #4 and its "Next Phase Readiness"
section, flagged for Phase 137's close ledger or a backlog item with a named owner. Fixing
`build_db_diff`/`classify_fingerprint`'s four-bucket design (no dedicated "perfect match"
bucket) was out of this plan's own declared scope (its `<action>` covers only `sdp_hold_state`'s
field/key/row/schema-bump and the `dedup_fingerprint` comment) and would be a real behavior
change, not a carriage addition -- not something to silently absorb into a plan whose own scope
statement names it explicitly as someone else's finding to fix. `git diff` confirms
`build_db_diff`/`classify_fingerprint`/`_LADDER_*` constants are byte-unchanged by this plan.

## Issues Encountered

None beyond the deviations documented above.

## User Setup Required

None -- no external service configuration required.

## Threat Flags

None new. This plan's `<threat_model>` (T-134-23/24/25/26) is fully covered by the
implementation as written: T-134-23 (a JSON boolean read as ground truth for an unreadable
protection state) is mitigated by the three-valued `str`-only field plus the committed
recursive no-boolean assertion over the whole `to_dict()`; T-134-24 (the artifact shape
changing while its own version claims it did not) is mitigated by the `SCHEMA_VERSION` 1.2 ->
1.3 bump with the additive argument recorded in the ladder comment; T-134-25 (op vocabulary
entering the declared non-registry `DiagnosticReport`) is mitigated by keeping derivation in
`chip_test.py` and re-confirming `test_non_registry_still_has_no_ops` green, including the
Deviation #2 self-catch above; T-134-26 (a leaked lock deduping identically with a held one) is
mitigated by leaving `dedup_fingerprint` generic and unedited, proven by the committed
SDP-verdict-sensitivity test.

## Next Phase Readiness

- `DiagnosticReport.sdp_hold_state`, its `to_dict()` key, and its `render()` row are the
  carriage plan `134-07` assigns a real value into (from `chip_test.sdp_hold_state(plan,
  results)`), closing LEG-12.
- `SCHEMA_VERSION` is `"1.3"`; `tools/parse_devtest_issue.py`'s presence-only acceptance is
  unbroken (its own test suite, 22 tests, passes unchanged in shape, one literal repaired).
- **Contributes to but does NOT tick:** LEG-12 (134-07's to close).
- The measured discrepancy (eleventh key, not tenth) and the two Rule-1 deviations above should
  be carried into Phase 137's ledger alongside 134-02's "exactly two" and 134-04's "n_ran=6, not
  5" findings, so a later reader does not encounter "nine keys"/"tenth key" in
  134-CONTEXT.md/this plan's own PLAN.md text and assume this plan's implementation is wrong
  instead.
- No blockers. mypy headroom unchanged at 2 (33/35, `checked` unchanged at 124 -- no new source
  modules added this plan, only additions to two existing test files and one existing production
  module). Full suite: 1401 passed (up from 1394 at 134-05's close; 7 new tests), coverage
  82.10% (>= 70% floor), 30 snapshots unchanged. `tools/ci_replica_venv.sh`: all 5 legs green.

## Self-Check: PASSED

- `firestarter_app/firestarter/diagnostic_report.py` -- FOUND, contains `sdp_hold_state: str =
  ""`, `"sdp_hold_state": self.sdp_hold_state,`, `table.add_row("sdp_hold_state", ...)`,
  `SCHEMA_VERSION = "1.3"`.
- `firestarter_app/tests/test_diagnostic_report.py` -- FOUND, 37/37 tests in this file pass
  (17/17 selected by `-k "hold or dedup or schema"`, 5/5 by `-k "hold"`).
- `firestarter_app/tests/test_parse_devtest_issue.py` -- FOUND, 22/22 tests pass.
- Commit `c461cc0` (submodule) -- FOUND in `git -C firestarter_app log --oneline --all`.
- Commit `8f3c712` (submodule) -- FOUND in `git -C firestarter_app log --oneline --all`.

---
*Phase: 134-the-plan-derived-sdp-oracle-in-dev-test*
*Completed: 2026-08-04*
