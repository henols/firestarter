---
phase: 137-close-honesty-ledger-claim-gate-gh12-followup
plan: 02
subsystem: testing
tags: [claim-gate, ast-scan, diagnostic-report, pytest, subprocess-testing, v1.30, mypy-config]

# Dependency graph
requires:
  - phase: 137-close-honesty-ledger-claim-gate-gh12-followup
    provides: "plan 137-01's FORBIDDEN_PATTERNS 14-label vocabulary (check_permitted_claims.py), forked verbatim here rather than re-derived"
  - phase: 134-the-plan-derived-sdp-oracle-in-dev-test
    provides: "SDP_RECOVERY_CONSTANT_NAMES + tests/test_sdp_recovery_wording.py (LEG-14, plan 134-09) -- the already-gated cli_handlers.py surface this plan deliberately does NOT re-scan"
provides:
  - "firestarter_app/tools/check_diagnostic_report_claims.py -- AST-derived string-literal claim scan over diagnostic_report.py, the one dev-test-report surface no gate scanned before this plan"
  - "tests/test_check_diagnostic_report_claims.py -- 4 subprocess-level anti-hollow legs (clean-pass, planted-violation, missing-target, unparsable-target)"
  - "two committed fixtures (one clean-shaped-planted-violation, one deliberately unparsable) plus a necessary mypy exclude for tests/fixtures/"
affects: [137-06 (final whole-milestone CI-parity recipe re-measures this plan's mypy/suite numbers), 137-03/04/05 (unaffected -- different artifacts, different gate)]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "AST-derived ast.Constant string-literal extraction for a claim scanner, mirroring check_no_community_support_status_write.py's NodeVisitor shape but collecting string values instead of assignment targets"
    - "Buffer-with-line-index-mapping technique: each collected literal's embedded newlines sanitized to a single space, then placed on its own buffer line, preserving a 1:1 index-to-original-lineno correspondence so a whole-buffer regex scan still reports accurate source line numbers"
    - "mypy exclude mirrors ruff's own extend-exclude for tests/fixtures/ -- same directory, same rationale (fixture input for source-scan gates, never project source), now applied to both tools"

key-files:
  created:
    - firestarter_app/tools/check_diagnostic_report_claims.py
    - firestarter_app/tests/test_check_diagnostic_report_claims.py
    - firestarter_app/tests/fixtures/planted_diagnostic_report_claim.py
    - firestarter_app/tests/fixtures/planted_unparsable.py
  modified:
    - firestarter_app/pyproject.toml
    - .planning/REQUIREMENTS.md
    - .planning/ROADMAP.md

key-decisions:
  - "Forked the 14-label FORBIDDEN_PATTERNS vocabulary verbatim from plan 137-01's meta-repo check_permitted_claims.py (byte-for-byte label parity confirmed by an AST-derived diff of both files, not a manual eyeball) -- the plan's own explicit instruction, avoiding a second, possibly-divergent vocabulary"
  - "Deliberately did NOT extend the scan to firestarter/cli_handlers.py's SDP_RECOVERY_CONSTANT_NAMES (_SDP_RECOVERY_LOUD/_SDP_RECOVERY_NEUTRAL), even though Phase 134 plan 134-08's own source comment names Phase 137's CLOSE-03 as an available extension point for that tuple. Both REQUIREMENTS.md's own CLOSE-03 wording and this plan's PLAN.md scope the scan to diagnostic_report.py only; the SDP recovery constants already have their own committed, narrower-scoped gate (tests/test_sdp_recovery_wording.py, LEG-14, plan 134-09) which that plan's own D-13 record explicitly warns against duplicating. Re-scanning that surface here would be out-of-scope re-derivation, not a coverage gap -- recorded explicitly in the new checker's own docstring so a future reader does not 'fix' this into a false gap"
  - "No proximity window and no self-verifying relational rule (both present in the meta-repo donor) -- the plan's own Task 1 spec says neither is needed here: every string literal in diagnostic_report.py is already report context by construction, so windowing adds complexity with no signal, and the self-verifying rule was never named as in-scope for this checker"
  - "[Rule 3 deviation] Added tests/fixtures/ to mypy's [tool.mypy] exclude (pyproject.toml), mirroring ruff's own pre-existing extend-exclude for the identical directory and reason. Without it, mypy's directory walk over tests/ aborts (exit 2, 'errors prevented further checking') on the newly-added tests/fixtures/planted_unparsable.py -- a deliberate, genuine Python SyntaxError the plan's own Task 2 spec requires -- which would invalidate the entire watermark run rather than reporting one ordinary per-file error. Measured that none of the 6 pre-existing tests/fixtures/*.py files ever contributed an error to the 33-error baseline, so this exclude only changes the checked-file count (129, still comfortably above tools/check_mypy_watermark.py's own MIN_CHECKED_SOURCE_FILES=120 floor), never the error count."

requirements-completed: [CLOSE-03]

coverage:
  - id: D1
    description: "Host-side AST claim scanner (firestarter_app/tools/check_diagnostic_report_claims.py) scans every ast.Constant string literal in diagnostic_report.py against the same 14-label forbidden-claim vocabulary as the meta-repo gate, fail-closed on a missing or unparsable target, currently PASS (zero forbidden matches) against the real, clean source"
    requirement: "CLOSE-03"
    verification:
      - kind: unit
        ref: "python3 tools/check_diagnostic_report_claims.py (no args) against the real diagnostic_report.py -- exit 0, PASS: line, 164 string literals checked"
        status: pass
      - kind: unit
        ref: "tests/test_check_diagnostic_report_claims.py::test_scanner_exits_zero_on_real_diagnostic_report"
        status: pass
    human_judgment: false
  - id: D2
    description: "Anti-hollow proof: a committed planted-violation fixture drives the gate to a non-zero exit naming an attributable forbidden-phrase label"
    requirement: "CLOSE-03"
    verification:
      - kind: unit
        ref: "tests/test_check_diagnostic_report_claims.py::test_planted_violation_flips_checker_to_failure"
        status: pass
    human_judgment: false
  - id: D3
    description: "Two fail-closed legs: a missing scan target and an unparsable (genuine SyntaxError) scan target both exit non-zero with an attributable message, never a silent skip"
    requirement: "CLOSE-03"
    verification:
      - kind: unit
        ref: "tests/test_check_diagnostic_report_claims.py::test_fail_closed_on_nonexistent_target"
        status: pass
      - kind: unit
        ref: "tests/test_check_diagnostic_report_claims.py::test_fail_closed_on_unparsable_source"
        status: pass
    human_judgment: false
  - id: D4
    description: "Full firestarter_app suite and mypy watermark are unaffected in substance by this plan's additions -- 1508 passed (1504 baseline + 4 new tests), mypy 33/35 (headroom flat at 2, checked-file count adjusted for a necessary mypy exclude, not a code-quality regression)"
    verification:
      - kind: unit
        ref: ".venv/ci-replica/bin/python -m pytest tests/ -o addopts=\"\" -q"
        status: pass
      - kind: unit
        ref: ".venv/ci-replica/bin/python tools/check_mypy_watermark.py"
        status: pass
    human_judgment: false

# Metrics
duration: ~15min
completed: 2026-08-05
status: complete
---

# Phase 137 Plan 02: Host-Side `diagnostic_report.py` Claim Scan (CLOSE-03) Summary

**AST-derived string-literal scanner over `diagnostic_report.py` -- the one `dev test` report surface no gate scanned before this plan -- sharing the meta-repo gate's 14-label vocabulary verbatim, proven non-hollow by a committed planted-violation fixture, wired into `pytest tests/` where CI already runs it.**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-08-05T17:46:00Z (plan/context read, following 137-01's completion)
- **Completed:** 2026-08-05T18:00:00Z
- **Tasks:** 2 (both `type="auto"`)
- **Files modified:** 7 (2 new source files, 2 new fixtures, 3 doc/config edits)

## Accomplishments

- `firestarter_app/tools/check_diagnostic_report_claims.py` authored: an AST-based scanner that
  parses `firestarter/diagnostic_report.py`, walks every `ast.Constant` string literal via a fresh
  `ast.NodeVisitor`, and scans the collected literals against the identical 14-label
  `FORBIDDEN_PATTERNS` vocabulary as plan 137-01's meta-repo `check_permitted_claims.py` (byte-for-byte
  label parity confirmed by an AST-derived comparison of both files' vocabulary lists, not a manual
  read). No proximity window and no relational self-verifying rule (both present in the donor) --
  neither is needed here per the plan's own Task 1 spec: every literal in this file is already report
  context by construction. Fail-closed on a missing scan target (`FAIL: scan target not found on
  disk`) and on an unparsable one (`FAIL: could not parse ... as Python`) -- never a silent skip.
  Env-override seam `FIRESTARTER_DIAGREPORT_SRC` lets the paired pytest re-point the scanner at a
  fixture without touching the real source. Run with no arguments against the real, clean
  `diagnostic_report.py`: `PASS: scanned .../diagnostic_report.py, 164 string literals checked, zero
  forbidden matches`, exit 0.

- Two committed fixtures under `tests/fixtures/`: `planted_diagnostic_report_claim.py` (a small,
  standalone, syntactically-valid module -- NOT a copy of the real source -- containing exactly one
  string literal, `"dev test proves the lock held"`, that deliberately trips two forbidden labels at
  once: `dev-test-proves-unqualified` and `lock-held-unqualified`) and `planted_unparsable.py` (a
  genuine Python `SyntaxError`, literally `def broken(:\n    pass`, for the fail-closed-on-unparsable
  leg).

- `tests/test_check_diagnostic_report_claims.py`: 4 subprocess-level pytest legs (never an in-process
  import of the scanner, mirroring `tests/test_check_no_community_support_status_write.py`'s
  convention): clean-pass on the real source, the planted-violation anti-hollow proof (asserts both
  non-zero exit and the `dev-test-proves-unqualified` label appears in the `FAIL:` output), and the two
  fail-closed legs (missing target, unparsable target). All 4 pass:
  `.venv/ci-replica/bin/python -m pytest tests/test_check_diagnostic_report_claims.py -o addopts=""
  -q` -> `4 passed`.

- **Deliberate scope boundary, documented in the checker's own docstring:** this scanner does NOT
  extend to `firestarter/cli_handlers.py`'s two named SDP recovery-string constants
  (`_SDP_RECOVERY_LOUD` / `_SDP_RECOVERY_NEUTRAL`, resolvable via `cli_handlers.SDP_RECOVERY_CONSTANT_NAMES`)
  even though Phase 134 plan 134-08's own source comment names Phase 137's CLOSE-03 as an available
  extension point for that tuple ("Phase 137's CLOSE-03 tool-side scanner is handed
  `SDP_RECOVERY_CONSTANT_NAMES` below so it EXTENDS this tuple rather than re-deriving or duplicating
  plan 134-09's pytest"). Both `REQUIREMENTS.md`'s own CLOSE-03 wording ("covers `diagnostic_report.py`'s
  string literals") and this plan's `PLAN.md` scope the scan to `diagnostic_report.py` only. The SDP
  recovery constants already have their own committed, narrower-scoped gate
  (`tests/test_sdp_recovery_wording.py`, LEG-14, plan 134-09, 3 targeted rules: "rewrite" present,
  bulk-clear-word absent, no hyphenated op literal) -- that plan's own D-13 record explicitly names
  Phase 137's CLOSE-03 as an extension point, **not duplicated here**. Re-scanning that already-gated
  surface with a second, differently-scoped 14-label checker would be exactly the out-of-scope
  re-derivation 134-09's own docstring warns against, not a coverage gap CLOSE-03 exists to close. This
  reasoning is recorded verbatim in the new checker's own module docstring's "Scope note" so a future
  reader does not mistake the narrower scope for an oversight.

## Task Commits

Each task was committed atomically:

1. **Task 1: Author the AST claim scanner** - `89f2fb2` (feat, submodule `firestarter_app`)
2. **Task 2: Commit fixtures + pair with 4 subprocess pytest legs** - `cc036e8` (test, submodule
   `firestarter_app`)

**Plan metadata:** (this commit, following SUMMARY write, meta repo)

## Files Created/Modified

- `firestarter_app/tools/check_diagnostic_report_claims.py` - the CLOSE-03 AST claim scanner, 14-label
  vocabulary forked verbatim from plan 137-01, fail-closed on missing/unparsable target
- `firestarter_app/tests/test_check_diagnostic_report_claims.py` - 4 subprocess-level anti-hollow legs
- `firestarter_app/tests/fixtures/planted_diagnostic_report_claim.py` - trips
  `dev-test-proves-unqualified` + `lock-held-unqualified`
- `firestarter_app/tests/fixtures/planted_unparsable.py` - a genuine Python `SyntaxError` fixture
- `firestarter_app/pyproject.toml` - `[tool.mypy]` gained `exclude = ["^tests/fixtures/"]` (Rule 3 fix,
  see Deviations below)
- `.planning/REQUIREMENTS.md` - CLOSE-03 ticked `[x]` with evidence citation; traceability table row
  updated to Complete. No other requirement checkbox touched.
- `.planning/ROADMAP.md` - Phase 137's `137-02-PLAN.md` checkbox ticked with completion date.

## Decisions Made

See `key-decisions` in frontmatter above for the full rationale on each. Summary:
- Forked 137-01's 14-label vocabulary verbatim (plan's own instruction).
- Deliberately scoped to `diagnostic_report.py` only, NOT `cli_handlers.py`'s SDP recovery constants
  (already gated by 134-09; re-scanning would duplicate, not close, a gap).
- No proximity window, no self-verifying rule (not in this checker's spec; every literal here is
  already report-context by construction).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] mypy aborts on the required unparsable fixture without an exclude**
- **Found during:** Task 2 (writing `tests/fixtures/planted_unparsable.py` per the plan's own literal
  instruction: a file containing `def broken(:\n    pass`)
- **Issue:** `tools/check_mypy_watermark.py` invokes `mypy firestarter/ tests/`, a directory walk that
  reaches `tests/fixtures/planted_unparsable.py`. mypy 2.3.0 aborts entirely on that file's genuine
  `SyntaxError` (`Found 1 error in 1 file (errors prevented further checking)`), which
  `check_mypy_watermark.py`'s own classifier correctly treats as untrustworthy (exit 2, "cannot be
  trusted as a complete, well-formed mypy run") rather than a normal watermark count -- this would have
  broken CI's mypy gate for the ENTIRE project, not just reported one new error, the moment this plan's
  Task 2 fixture landed.
- **Fix:** Added `exclude = ["^tests/fixtures/"]` to `[tool.mypy]` in `pyproject.toml`, mirroring
  `[tool.ruff]`'s own pre-existing `extend-exclude = ["tests/golden", "tests/fixtures"]` for the
  identical directory and the identical stated reason ("fixture input for the source-scan gates, never
  project source").
- **Verification:** Measured that none of the 6 pre-existing `tests/fixtures/*.py` files (all
  syntactically valid) ever contributed an error to the pre-plan 33-error baseline (`mypy firestarter/
  tests/` output grepped for `fixtures/` before the exclude: zero lines). Post-fix:
  `tools/check_mypy_watermark.py` reports `checked 129 source files`, `mypy errors: 33 (watermark:
  35)` -- error count and watermark both unchanged, headroom flat at 2, checked-file count still far
  above the script's own `MIN_CHECKED_SOURCE_FILES = 120` floor. Full suite re-confirmed green after
  the fix: `1508 passed` (1504 baseline + 4 new tests).
- **Files modified:** `firestarter_app/pyproject.toml`
- **Committed in:** `cc036e8` (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking, Rule 3)
**Impact on plan:** Necessary for CI correctness -- without it, this plan's own required Task 2
fixture would have broken the mypy watermark gate for the whole project on the next PR. No scope
creep: the fix is a one-line config addition mirroring an already-established, identically-reasoned
exclusion for the same directory.

## Issues Encountered

None beyond the one deviation above.

## User Setup Required

None - no external service configuration required.

## Vocabulary Parity Confirmation

An AST-derived comparison (not a manual read) of `FORBIDDEN_PATTERNS`'s label list in both files
confirms byte-for-byte parity:

```
new (check_diagnostic_report_claims.py): ['verified-fixed', 'confirmed-working', 'silicon-verified',
  'verified-on-silicon', 'works-on-silicon', 'now-works', 'should-now-work', 'proven-on-silicon',
  'lock-inhibited-the-write', 'lock-held-unqualified', 'proven-behaviour', 'behaviourally-verified',
  'now-proven', 'dev-test-proves-unqualified']  (14 entries)
old (check_permitted_claims.py, plan 137-01): identical list, identical order  (14 entries)
match: True
```

## Test Results (Task 2 acceptance criteria)

1. `.venv/ci-replica/bin/python -m pytest tests/test_check_diagnostic_report_claims.py -o addopts=""
   -q` -> **4 passed**.
2. `grep -c 'subprocess' tests/test_check_diagnostic_report_claims.py` -> 2 (import + helper usage).
3. Full suite: `.venv/ci-replica/bin/python -m pytest tests/ -o addopts="" -q` -> **1508 passed, 0
   failed** -- exactly the Phase 136.1 baseline (1504) plus these 4 new tests, no discrepancy to
   explain.
4. mypy headroom: `tools/check_mypy_watermark.py` -> **33 errors, watermark 35, headroom 2** --
   unmoved from the Phase 136.1 baseline, per the Rule 3 fix above. Checked-file count is 129 (down
   from the 132 baseline because `tests/fixtures/` -- 8 files now, 6 pre-existing + 2 new -- is
   excluded from mypy's walk; still 9 above `MIN_CHECKED_SOURCE_FILES = 120`).

## Next Phase Readiness

- `firestarter_app/tools/check_diagnostic_report_claims.py` is proven correct and wired into
  `pytest tests/`, where CI's existing `pytest tests/ --cov-fail-under=70` step will run it on every
  future PR without any new YAML.
- Plan 137-03 (honesty ledger, CLOSE-04) can cite this gate's existence and green state directly.
- Plan 137-06 (final whole-milestone CI-parity recipe, CLOSE-01) will re-measure mypy/suite numbers
  one more time at close; this plan's 33/35 and 1508-passed figures are this wave's contribution to
  that eventual whole-milestone reading, not a final one.
- **One requirement ticked: CLOSE-03** -- the only one this plan may discharge. Project-wide
  requirement state after this plan: **51 ticked `[x]` / 5 open** (`CLOSE-01`, `CLOSE-04`, `CLOSE-05`,
  `CLOSE-06`, `RELOCK-07` remain — all later Phase 137 plans' own scope), confirmed by direct grep
  count (`grep -c '^\- \[x\]' REQUIREMENTS.md` -> 51; `grep -c '^\- \[ \]' REQUIREMENTS.md` -> 5),
  matching the mandated ticking scope exactly.

---
*Phase: 137-close-honesty-ledger-claim-gate-gh12-followup*
*Completed: 2026-08-05*

## Self-Check: PASSED

- FOUND: `firestarter_app/tools/check_diagnostic_report_claims.py`
- FOUND: `firestarter_app/tests/test_check_diagnostic_report_claims.py`
- FOUND: `firestarter_app/tests/fixtures/planted_diagnostic_report_claim.py`
- FOUND: `firestarter_app/tests/fixtures/planted_unparsable.py`
- FOUND commit `89f2fb2` (Task 1, submodule `firestarter_app`)
- FOUND commit `cc036e8` (Task 2, submodule `firestarter_app`)
- Re-confirmed `python3 tools/check_diagnostic_report_claims.py` (no args) still exits 0 against the
  real, unmodified `diagnostic_report.py`
- Re-confirmed `.venv/ci-replica/bin/python -m pytest tests/test_check_diagnostic_report_claims.py
  -o addopts="" -q`: 4 passed
- Re-confirmed full suite: 1508 passed, 0 failed; mypy 33/35, headroom 2
