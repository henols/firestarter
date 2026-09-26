---
phase: 134-the-plan-derived-sdp-oracle-in-dev-test
plan: 09
subsystem: testing
tags: [python, pytest, cli_handlers.py, chip_test.py, sdp, leg-14, non-vacuity, gate]

# Dependency graph
requires:
  - phase: 134-08
    provides: "_SDP_RECOVERY_LOUD / _SDP_RECOVERY_NEUTRAL / SDP_RECOVERY_CONSTANT_NAMES
      (cli_handlers.py) -- D-12's two named recovery-string constants plus
      the tuple naming them -- this plan's scan target"
provides:
  - "tests/test_sdp_recovery_wording.py: LEG-14's committed, scoped gate.
    _scan_recovery_constants(named_values) scans EXACTLY
    SDP_RECOVERY_CONSTANT_NAMES for three rules (rewrite present, bulk-clear
    word absent, no hyphenated _SDP_LEG_OPS/_SDP_OPS literal), fails closed
    on a zero-symbol scan, and is proven non-vacuous by two committed
    planted-violation legs plus a one-time observed-RED proof against the
    real constant (recorded verbatim below)."
affects: [137]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "_ALWAYS_WRITES_NOTICE is scanned SEPARATELY from the two named
      recovery constants, for rule 1 (the 'rewrite' word) only -- never
      rules 2/3 -- because it legitimately contains the bulk-clear word in
      its own shipped write/verify/erase step enumeration. Running the full
      three-rule scan against it would re-plant the exact Phase-133 D-14
      _sample-shaped trap this module exists to avoid. This is the plan's
      own D-13 warning applied literally to the gate's own scope, not just
      to a hypothetical whole-report grep."
    - "In-memory-copy idiom for planted-violation legs (no fixture file):
      the scan target is imported module constants, so there is nothing on
      disk to mutate -- mirrors test_op_registration_parity.py's
      test_altered_registry_copy_fails_parity_non_vacuous."
    - "Aggregate-then-raise: _scan_recovery_constants collects every
      offending (name, rule) pair before raising once, mirroring
      _assert_op_parity's shape rather than failing on the first hit."

key-files:
  created:
    - firestarter_app/tests/test_sdp_recovery_wording.py
  modified: []

key-decisions:
  - "_ALWAYS_WRITES_NOTICE gets a dedicated test
    (test_always_writes_notice_contains_required_recovery_word) checking
    ONLY rule 1, rather than being folded into _scan_recovery_constants's
    named_values dict alongside the two recovery constants. The plan's own
    must-haves truth statement ('resolves ... plus _ALWAYS_WRITES_NOTICE
    ... scans only those values') reads as if all three rules apply
    uniformly to all three constants; measuring the real text shows
    _ALWAYS_WRITES_NOTICE legitimately contains the bulk-clear word (\"the
    shipped write/verify/erase steps\"), so a uniform three-rule scan would
    make the positive control fail on real, correct text -- the identical
    shape D-13 itself names as the reason a whole-report grep is wrong.
    Resolved by scoping rules 2/3 to SDP_RECOVERY_CONSTANT_NAMES only,
    exactly as the plan's key_links section states the scan target to be
    (\"cli_handlers.SDP_RECOVERY_CONSTANT_NAMES -- a module-level tuple\")."
  - "_FORBIDDEN_RECOVERY_WORD is written as the literal string \"erase\" in
    the test module (matching the codebase's own OP_ERASE = \"erase\"
    style at chip_test.py:336), not spelled out letter-by-letter -- the
    plan's own action text spells it letter-by-letter only to avoid
    tripping a plan-prose-level word scanner (the
    <!-- planner-discipline-allow: erase --> comment in the plan file);
    that concern does not apply to the committed test module itself, which
    must contain the literal word to test for it."
  - "Word-boundary regex (\\berase\\b) rather than plain substring
    containment for the forbidden-word rule, so 'UV-erasable' (which
    legitimately appears elsewhere in this codebase's prose) would not
    false-positive if it ever entered a scanned constant -- only the
    standalone word triggers."
  - "Split into two commits matching the plan's two tasks (test-only, no
    production file touched by either): Task 1's commit ships the positive
    control, three-rule gate, and fail-closed/target-resolution legs (6
    tests); Task 2's commit adds the two planted-violation non-vacuity legs
    (8 tests total). Obligation #4's observed-RED proof against the real
    constant left no trace in either commit (git diff of
    cli_handlers.py confirmed empty before Task 2's commit)."

requirements-completed: [LEG-14]

coverage:
  - id: D1
    description: "_scan_recovery_constants(named_values) scans EXACTLY
      cli_handlers.SDP_RECOVERY_CONSTANT_NAMES (_SDP_RECOVERY_LOUD,
      _SDP_RECOVERY_NEUTRAL) for three rules: the 'rewrite' word present,
      the bulk-clear word absent as a standalone word, no hyphenated
      _SDP_LEG_OPS/_SDP_OPS substring. A positive control over the real,
      unmodified constants runs FIRST in file order and does not raise."
    requirement: LEG-14
    verification:
      - kind: unit
        ref: "tests/test_sdp_recovery_wording.py::test_positive_control_real_constants_do_not_raise"
        status: pass
      - kind: unit
        ref: "tests/test_sdp_recovery_wording.py::test_always_writes_notice_contains_required_recovery_word"
        status: pass
    human_judgment: false
  - id: D2
    description: "The gate FAILS CLOSED: a zero-symbol scan (empty mapping)
      raises rather than passing vacuously, and resolving a constant name
      that does not exist on firestarter.cli_handlers raises
      AttributeError rather than silently narrowing the scan set."
    requirement: LEG-14
    verification:
      - kind: unit
        ref: "tests/test_sdp_recovery_wording.py::test_fail_closed_on_zero_symbol_scan"
        status: pass
      - kind: unit
        ref: "tests/test_sdp_recovery_wording.py::test_fail_closed_on_missing_constant_name"
        status: pass
    human_judgment: false
  - id: D3
    description: "Target-resolution legs: SDP_RECOVERY_CONSTANT_NAMES is
      non-empty and every name resolves to a non-empty str attribute; the
      tuple has not silently shrunk below its expected minimum count (2)."
    requirement: LEG-14
    verification:
      - kind: unit
        ref: "tests/test_sdp_recovery_wording.py::test_recovery_constant_names_non_empty_and_resolve_to_non_empty_strings"
        status: pass
      - kind: unit
        ref: "tests/test_sdp_recovery_wording.py::test_recovery_constant_count_has_not_silently_shrunk"
        status: pass
    human_judgment: false
  - id: D4
    description: "Two committed planted-violation non-vacuity legs (the
      in-memory-copy idiom): planting the forbidden bulk-clear word, and
      separately a hyphenated _SDP_LEG_OPS op literal, into a copy of one
      real recovery constant each MUST make the scan fail -- each with a
      fixture-setup assertion proving the mutation applied, wrapped in the
      house try/except AssertionError: pass / else: raise shape."
    requirement: LEG-14
    verification:
      - kind: unit
        ref: "tests/test_sdp_recovery_wording.py::test_planted_forbidden_word_is_caught_non_vacuous"
        status: pass
      - kind: unit
        ref: "tests/test_sdp_recovery_wording.py::test_planted_hyphenated_op_literal_is_caught_non_vacuous"
        status: pass
    human_judgment: false
  - id: D5
    description: "Non-vacuity obligation #4 (134-VALIDATION.md row 4):
      observed RED against the REAL constant, not merely a committed
      planted-copy leg. _SDP_RECOVERY_LOUD in firestarter/cli_handlers.py
      was temporarily edited to contain the bulk-clear word; the scoped
      gate was run and failed, naming exactly '_SDP_RECOVERY_LOUD'; the
      file was then restored and `git diff firestarter/cli_handlers.py`
      confirmed empty before the commit that follows. This is a one-time,
      execution-time proof -- not a permanent test in the committed file
      (the committed non-vacuity proof is D4 above)."
    human_judgment: true
    rationale: "The RED observation is a manual, one-time procedural step
      by design (VALIDATION.md's own framing: 'execution-time obligation;
      cannot be discharged before the code exists'), not a repeatable
      automated check -- the verbatim transcript below is the evidence."
  - id: D6
    description: "No regression: the full test suite and the mypy
      watermark gate stay green after this plan's additions."
    verification:
      - kind: unit
        ref: "pytest tests/ -o addopts=\"\" -q (1425 passed, 30 snapshots unchanged)"
        status: pass
      - kind: other
        ref: "tools/ci_replica_venv.sh (5/5 legs green; mypy errors: 33 (watermark: 35), checked 125 source files)"
        status: pass
    human_judgment: false

# Metrics
duration: 40min
completed: 2026-08-04
status: complete
---

# Phase 134 Plan 09: LEG-14's Committed, Scoped Recovery-Wording Gate Summary

**Authored `tests/test_sdp_recovery_wording.py` — a new pytest module that scans exactly
`cli_handlers.SDP_RECOVERY_CONSTANT_NAMES` for the "rewrite" recovery wording, the absence of the
bulk-clear word, and no hyphenated SDP-leg op literal, proven non-vacuous by two committed
planted-violation legs plus a one-time observed-RED proof against the real `_SDP_RECOVERY_LOUD`
constant.**

## Performance

- **Duration:** 40 min
- **Started:** 2026-08-04T19:06:32Z (134-08's last commit)
- **Completed:** 2026-08-04T19:47:00Z (this plan's final commit, submodule)
- **Tasks:** 2
- **Files modified:** 1, inside the `firestarter_app` submodule (test-only; zero production files)

## Accomplishments

- Created `firestarter_app/tests/test_sdp_recovery_wording.py` (new file, 8 tests, all green):
  `_scan_recovery_constants(named_values: dict[str, str]) -> None` — the gate — resolves and scans
  exactly `cli_handlers.SDP_RECOVERY_CONSTANT_NAMES` (today: `_SDP_RECOVERY_LOUD`,
  `_SDP_RECOVERY_NEUTRAL`), asserting per constant: (1) contains `"rewrite"` (case-insensitive), (2)
  does NOT contain the bulk-clear word as a standalone word (`\berase\b`, case-insensitive), (3)
  contains no hyphenated op literal from `chip_test._SDP_LEG_OPS | chip_test._SDP_OPS` as a substring
  (folding RESEARCH OQ-5's hazard into the same gate). Raises `AssertionError` naming **every**
  offending `(name, rule)` pair, mirroring `_assert_op_parity`'s aggregate-then-raise shape.
- Scoped `_ALWAYS_WRITES_NOTICE` **separately**, via its own dedicated test
  (`test_always_writes_notice_contains_required_recovery_word`), checking rule 1 (the "rewrite" word)
  **only** — never rules 2/3. Measured that `_ALWAYS_WRITES_NOTICE` legitimately contains the
  bulk-clear word today, in its own shipped "write/verify/erase steps" step enumeration; running the
  full three-rule scan against it (as a literal reading of the plan's must-haves truth statement
  could suggest) would make the positive control itself fail on correct text — the exact D-13 trap
  applied one layer deeper, to the gate's own scope rather than a hypothetical whole-report grep. The
  plan's own key_links section states the scan target is `cli_handlers.SDP_RECOVERY_CONSTANT_NAMES`
  (a module-level tuple that does not include `_ALWAYS_WRITES_NOTICE`), which this design honours.
- Added the positive control (`test_positive_control_real_constants_do_not_raise`), the first
  `def test_` in the file by construction — verified by `grep -n 'def test_' ... | head -1`.
- Added two fail-closed legs mirroring `tests/test_check_sdp_capability.py`: a zero-symbol scan
  (empty mapping) raises rather than exiting clean; resolving a constant name that does not exist on
  `firestarter.cli_handlers` raises `AttributeError` (via a bare `getattr`, no default) rather than
  silently narrowing the scan set.
- Added two target-resolution legs: `SDP_RECOVERY_CONSTANT_NAMES` is non-empty and every name
  resolves to a non-empty `str` attribute; a minimum-count assertion (`>= 2`) catches a silent shrink
  of the tuple.
- Added two committed planted-violation non-vacuity legs, using the in-memory-copy idiom (no fixture
  file — the scan target is imported module constants, so there is no source file to plant into,
  mirroring `test_op_registration_parity.py`'s `test_altered_registry_copy_fails_parity_non_vacuous`):
  one plants the bulk-clear word into a copy of a real recovery constant, the other plants a
  hyphenated `_SDP_LEG_OPS` literal. Both assert the mutation actually applied (fixture-setup
  assertion) before wrapping the scan call in `try/except AssertionError: pass / else: raise
  AssertionError("Non-vacuity failure: ...")`.
- **Discharged non-vacuity obligation #4** (`134-VALIDATION.md` row 4) against the REAL constant, not
  merely the committed planted-copy legs above. See "Non-Vacuity Obligation #4" below for the full
  procedure and verbatim RED transcript.
- Ticked **LEG-14** — the only requirement this plan may tick, closing the two-part split: plan
  134-08 wrote the recovery wording and named the constants; this plan built and proved the gate.
- Ran the full suite (`1417 → 1425` passed, +8 new tests, 30 snapshots unchanged, coverage unchanged
  at 82.12% — no production code changed) and `tools/ci_replica_venv.sh` (5/5 legs green; `mypy
  errors: 33 (watermark: 35)`, `checked 125 source files` — up from 124, confirming D-15's "floor, not
  ceiling" reading: adding a test module raises `checked` further above `MIN_CHECKED_SOURCE_FILES =
  120`, it does not spend a budget).

## Non-Vacuity Obligation #4 (134-VALIDATION.md row 4)

Procedure, exactly as the plan's Task 2 specifies:

1. Confirmed clean baseline: `git diff firestarter/cli_handlers.py` was empty before the edit.
2. Temporarily edited `_SDP_RECOVERY_LOUD` in `firestarter/cli_handlers.py` to insert the phrase
   `"(do not erase it), and a "` into its assembled string, planting the bulk-clear word into the
   REAL, live constant (not a copy).
3. Ran `.venv/ci-replica/bin/python -m pytest tests/test_sdp_recovery_wording.py -o addopts="" -q`
   and observed **RED**, naming exactly `_SDP_RECOVERY_LOUD`. Verbatim relevant excerpt:

   ```
   F.......                                                                 [100%]
   =================================== FAILURES ===================================
   ______________ test_positive_control_real_constants_do_not_raise _______________
   ...
   >       _scan_recovery_constants(_real_scan_target())
   ...
       if problems:
   >           raise AssertionError(
                   "LEG-14 recovery-wording scan found violation(s):\n"
                   + "\n".join(f"  - {p}" for p in problems)
               )
   E           AssertionError: LEG-14 recovery-wording scan found violation(s):
   E             - '_SDP_RECOVERY_LOUD': contains forbidden bulk-clear word 'erase' -- protocol 0x0D has no bulk-clear operation; this is wrong advice

   tests/test_sdp_recovery_wording.py:125: AssertionError
   =========================== short test summary info ============================
   FAILED tests/test_sdp_recovery_wording.py::test_positive_control_real_constants_do_not_raise
   1 failed, 7 passed in 0.19s
   ```

4. Restored `firestarter/cli_handlers.py` to its exact prior text (removed the planted phrase).
   Confirmed `git diff firestarter/cli_handlers.py` returned **empty** (byte-identical restore)
   before making Task 2's commit.
5. Re-ran the gate: `8 passed in 0.18s` — green again.
6. `git show --stat HEAD` for Task 2's commit lists only `tests/test_sdp_recovery_wording.py` —
   `firestarter/cli_handlers.py` carries no trace of the temporary edit.

## Task Commits

Each task was committed atomically, inside the `firestarter_app` submodule on
`gsd/v1.30-sdp-surface-retirement`:

1. **Task 1: the scoped gate — positive control, the three per-constant assertions, and the
   fail-closed legs** — `f246a7e` (test) — 6 tests.
2. **Task 2: the planted-violation non-vacuity leg, and obligation #4 observed RED against the real
   constant** — `2895516` (test) — adds 2 planted-violation legs (8 tests total). Obligation #4's
   temporary edit-and-restore left no trace in this commit — verified via `git diff
   firestarter/cli_handlers.py` (empty) before staging, and `git show --stat` (test file only) after.

**Plan metadata:** committed with this SUMMARY (docs: complete plan), in the meta repo.

## Files Created/Modified

- `firestarter_app/tests/test_sdp_recovery_wording.py` (new) — LEG-14's scoped gate:
  `_scan_recovery_constants`, `_resolve_named_constants`, `_real_scan_target`, and 8 tests (positive
  control first; `_ALWAYS_WRITES_NOTICE`'s rule-1-only check; 2 fail-closed legs; 2 target-resolution
  legs; 2 planted-violation non-vacuity legs).

## Decisions Made

- **`_ALWAYS_WRITES_NOTICE` is scanned separately from the two named recovery constants, for rule 1
  only.** See `key-decisions` in the frontmatter for the full measured rationale — this is the plan's
  own D-13 warning, applied to the gate's own scope rather than left as a hypothetical about a
  whole-report grep.
- **`_FORBIDDEN_RECOVERY_WORD` is the literal string `"erase"`** in the committed module, matching the
  codebase's existing `OP_ERASE = "erase"` style — the plan's letter-by-letter spelling in its own
  prose is a plan-document-level discipline (avoiding tripping some other scanner over PLAN.md text),
  not a constraint on the test module's own source.
- **Word-boundary regex, not substring containment**, for the forbidden-word rule — so a legitimate
  word like "erasable" would not false-positive if it ever entered a scanned constant.
- **Split into two commits matching the plan's two tasks**, both test-only. Obligation #4's temporary
  production-file edit was verified restored (`git diff` empty) before Task 2's commit, so neither
  commit carries any trace of the transient plant.

## Deviations from Plan

None — plan executed exactly as written, including the fail-closed and non-vacuity design covered
above (which is the plan's own specified design, not a deviation from it).

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Threat Flags

None new. This plan's `<threat_model>` (T-134-35/36/37) is fully covered: T-134-35 (an
unreachable-green gate) is mitigated by the positive control, two committed planted-violation legs,
the zero-symbol fail-closed leg, and obligation #4's observed-RED proof against the real constant;
T-134-36 (a rename silently emptying the scan set) is mitigated by the resolver's bare-`getattr`
fail-closed behaviour, the non-empty-name assertion, and the minimum-count floor; T-134-37 (wrong
recovery advice reaching a user) is mitigated by the scoped gate enforcing "rewrite" and forbidding
the bulk-clear word in every scanned constant. T-134-SC (package-manager installs) — no new package
installed.

## Next Phase Readiness

- LEG-14 is now **Complete** in `REQUIREMENTS.md` — the only requirement this plan ticks. `git diff --
  .planning/REQUIREMENTS.md` confirmed exactly two lines changed (the checkbox and the traceability
  table row), plus the requirements-completed frontmatter provenance already in place from earlier
  phases; no other requirement row touched.
- Phase 137's CLOSE-03 hand-off is in place: the module's docstring names
  `SDP_RECOVERY_CONSTANT_NAMES` as the tuple that scanner should extend, and explicitly states that
  scanner is not authored here.
- No blockers. Full suite 1417 → 1425 passed (+8 new tests), coverage unchanged at 82.12% (>= 70%
  floor, no production code changed), 30 snapshots unchanged. `tools/ci_replica_venv.sh`: 5/5 legs
  green; `mypy errors: 33 (watermark: 35)`, `checked 125 source files` (up from 124 — a floor, not a
  ceiling, per D-15's correction; headroom unchanged at 2).
- Next: plan 134-10 (LEG-13/LEG-17), owning `tests/test_dev_test_cmd.py`, `tests/test_chip_test.py`
  and `tests/fixtures/` — disjoint from this plan's sole file, `tests/test_sdp_recovery_wording.py`.

## Self-Check: PASSED

- `firestarter_app/tests/test_sdp_recovery_wording.py` — FOUND, contains `def _scan_recovery_constants(`,
  `_REQUIRED_RECOVERY_WORD`, `_FORBIDDEN_RECOVERY_WORD`; 8/8 tests pass.
- Commit `f246a7e` (submodule) — FOUND in `git -C firestarter_app log --oneline --all`.
- Commit `2895516` (submodule) — FOUND in `git -C firestarter_app log --oneline --all`.
- `git -C firestarter_app diff firestarter/cli_handlers.py` — confirmed EMPTY (byte-identical restore
  after obligation #4's temporary edit).
- `.planning/REQUIREMENTS.md` — `git diff` confirms exactly the LEG-14 checkbox and traceability-table
  row changed; every other row untouched (LEG-13/17/18 remain Pending, per this plan's scope).

---
*Phase: 134-the-plan-derived-sdp-oracle-in-dev-test*
*Completed: 2026-08-04*
