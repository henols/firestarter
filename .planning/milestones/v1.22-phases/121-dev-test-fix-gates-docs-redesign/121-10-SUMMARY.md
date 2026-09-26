---
phase: 121-dev-test-fix-gates-docs-redesign
plan: 10
subsystem: cli
tags: [click, cli, eeprom, sdp, warn-and-proceed]

# Dependency graph
requires:
  - phase: 121-08
    provides: "protocol-0x0D FLAG_CAN_ERASE cleared at convert_to_programmer (D-12)"
  - phase: 121-09
    provides: "cli_handlers.py write handler shape, D-04/D-18 skip-sdp-unlock arm"
provides:
  - "write --skip-erase warn-and-proceed arm for protocol-0x0D chips (D-13)"
  - "dedicated test module pinning the arm's exact scope + its deliberate non-extension to -b/--no-blank-check"
affects: [121-13-gate-02-docs, 121-14-nonregression]

# Tech tracking
tech-stack:
  added: []
  patterns: ["warn-and-proceed sibling if-arm (not elif-chained) alongside an existing if/elif block"]

key-files:
  created:
    - firestarter_app/tests/test_write_skip_erase_0x0d.py
  modified:
    - firestarter_app/firestarter/cli_handlers.py

key-decisions:
  - "New arm added as a plain sibling `if`, not chained as another `elif` onto the existing D-04/D-18 block — the two blocks gate on different flags (skip_sdp_unlock vs skip_erase) and must be able to fire independently on the same 0x0D chip."
  - "Did not add a docstring paragraph for D-13 (only an in-body comment) after discovering it changed `firestarter write --help` output and broke two syrupy golden-snapshot characterization tests (test_help_write, test_no_blank_check_polarity); the comment carries the same rationale without touching the public help surface."
  - "Interpreted the plan's 'both vacuous flag warnings can appear together' leg as pairing D-13's new line with the pre-existing D-04 auto-set line (not literally HOST-02 D-18's line) — D-18's warning is scoped to non-0x0D chips while D-13's is scoped to 0x0D chips, so those two specific warnings can structurally never co-occur on one chip; D-04's auto-set line is the only other 0x0D-scoped line available to pair with."

requirements-completed: []  # GATE-02 is contributes-only here (closed by plan 121-13); nothing marked Complete.

coverage:
  - id: D1
    description: "write --skip-erase on a protocol-0x0D chip prints a warn-and-proceed line and still calls write_eprom (never aborts)"
    requirement: "GATE-02"
    verification:
      - kind: unit
        ref: "tests/test_write_skip_erase_0x0d.py#test_skip_erase_on_0x0d_warns_and_proceeds"
        status: pass
    human_judgment: false
  - id: D2
    description: "The warning does not fire on non-0x0D chips, or when --skip-erase is absent"
    requirement: "GATE-02"
    verification:
      - kind: unit
        ref: "tests/test_write_skip_erase_0x0d.py#test_skip_erase_on_non_0x0d_does_not_warn"
        status: pass
      - kind: unit
        ref: "tests/test_write_skip_erase_0x0d.py#test_no_skip_erase_on_0x0d_does_not_warn"
        status: pass
    human_judgment: false
  - id: D3
    description: "The blank-check flag (-b/--no-blank-check) never produces the erase warning, even on a 0x0D chip (RESEARCH C-8 scope split), with a deliberate-break proof performed"
    requirement: "GATE-02"
    verification:
      - kind: unit
        ref: "tests/test_write_skip_erase_0x0d.py#test_blank_check_flag_on_0x0d_does_not_produce_an_erase_warning"
        status: pass
    human_judgment: false
  - id: D4
    description: "The emitted operation_flags (FLAG_SKIP_ERASE bit) are unchanged whether or not the warning line prints"
    requirement: "GATE-02"
    verification:
      - kind: unit
        ref: "tests/test_write_skip_erase_0x0d.py#test_skip_erase_warning_does_not_change_the_emitted_flags"
        status: pass
    human_judgment: false
  - id: D5
    description: "The new arm and the pre-existing D-04 auto-set block fire independently (sibling if, not a mutually-exclusive elif chain)"
    requirement: "GATE-02"
    verification:
      - kind: unit
        ref: "tests/test_write_skip_erase_0x0d.py#test_both_vacuous_flag_warnings_can_appear_together"
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-07-29
status: complete
---

# Phase 121 Plan 10: Warn-and-Proceed on Vacuous --skip-erase (D-13) Summary

**`write --skip-erase` on a protocol-0x0D (28C/SDP) chip now prints one warn-and-proceed line stating the family has no erase to skip, then completes a normal write — closing the runtime half of Phase 120's deferred flag-surface honesty item.**

## Performance

- **Duration:** ~25 min
- **Tasks:** 2/2 completed
- **Files modified:** 1 (`firestarter/cli_handlers.py`)
- **Files created:** 1 (`tests/test_write_skip_erase_0x0d.py`)

## Accomplishments
- Added a sibling `if skip_erase and is_protocol_0x0d:` arm in `write`, placed independently of the existing D-04/D-18 `if`/`elif` block so both can fire on the same invocation.
- The warning never refuses, never aborts, and never touches `_build_op_flags` — `FLAG_SKIP_ERASE` (0x04) is still emitted unconditionally whenever `--skip-erase` is passed, confirmed identical (`0x4`) with and without the 0x0D protocol match.
- Pinned the arm's exact scope with 6 tests, including a negative leg proving `-b`/`--no-blank-check` is deliberately NOT extended (RESEARCH C-8), and performed the mandated deliberate-break proof live (widened the condition to `(skip_erase or not blank_check) and is_protocol_0x0d`, confirmed the negative leg went RED, restored, confirmed GREEN).

## Task Commits

Each task was committed atomically in `firestarter_app`:

1. **Task 1: Add the warn-and-proceed arm for --skip-erase on protocol 0x0D** - `40811a4` (feat)
2. **Task 2: Pin the arm's scope with a dedicated test module** - `48ec222` (test)

**Plan metadata:** committed separately in the meta repo (this SUMMARY + no STATE/ROADMAP/REQUIREMENTS changes — those are orchestrator-owned per this plan's dispatch).

## Files Created/Modified
- `firestarter_app/firestarter/cli_handlers.py` — new sibling `if` arm in `write` (D-13); in-body comment records the D-13/C-8 rationale (see Deviations below for why no docstring paragraph was added).
- `firestarter_app/tests/test_write_skip_erase_0x0d.py` — new 6-leg test module.

## Decisions Made
- Sibling `if`, not `elif`-chained, so the D-04 auto-set block and the new D-13 arm can both fire on one capability-refused 0x0D chip in one invocation (proven by `test_both_vacuous_flag_warnings_can_appear_together`).
- No docstring paragraph added for D-13 (see Deviations) — the in-body comment above the new `if` carries the full four-part rationale (no-refuse/no-abort/no-suppress; why safe; why the bit still emits; the C-8 non-extension note) without touching `--help` output.
- The plan's "both vacuous flag warnings can appear together" leg is interpreted as D-13's line paired with the D-04 auto-set line rather than literally HOST-02 D-18's line, because D-18's warning is scoped to non-0x0D chips and D-13's is scoped to 0x0D chips — those two specific lines are structurally incapable of co-occurring on a single chip's protocol.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Removed the D-13 docstring paragraph after it broke two golden-snapshot tests**
- **Found during:** Task 1, first full-suite run.
- **Issue:** The plan's read_first list pointed at the `write` command's docstring as a template location, so a D-13 paragraph was added there. Click renders the full docstring in `--help`, and `tests/test_characterization.py::test_help_write` / `test_no_blank_check_polarity` pin `write --help`'s exact stdout via syrupy snapshots — the new paragraph flipped both to a diff, i.e. 2 failed / 1100 passed on the first full run.
- **Fix:** Removed the docstring paragraph; kept the equivalent rationale as a plain Python comment directly above the new `if` block (comments do not render in `--help`, so this preserves in-source documentation without touching the public CLI surface or requiring a snapshot regen).
- **Files modified:** `firestarter/cli_handlers.py` (net: comment retained, docstring unchanged from pre-plan state).
- **Verification:** Full suite re-run: `1102 passed` (0 failed), both previously-failing snapshot tests green again.
- **Committed in:** `40811a4` (Task 1 commit — the docstring add/remove happened before the commit, so the committed diff contains only the comment + `if` arm, not the discarded docstring paragraph).

---

**Total deviations:** 1 auto-fixed (1 bug fix, self-contained within Task 1 before its commit).
**Impact on plan:** No scope creep — the fix kept the required rationale content, just relocated it from a Click-rendered docstring to a plain comment. `write --help`'s golden snapshots remain byte-identical to pre-plan state.

## Issues Encountered
None beyond the docstring/snapshot interaction documented above.

## User Setup Required
None - no external service configuration required.

## Verification Evidence

- `cd /workspaces/firestarter_app && python -m pytest tests/ --tb=short` → **1102 passed, 0 failed** (baseline 1096 + 6 new legs).
- `python3 -m pytest tests/test_write_skip_erase_0x0d.py tests/test_write_skip_sdp_unlock.py -v` → 13 passed (6 new + 7 pre-existing, unchanged count).
- `python3 -m pytest tests/ --cov=firestarter --cov-fail-under=70 -q` → **81.91% total**, gate passes.
- `python3 tools/check_mypy_watermark.py` → 1 error (watermark 35) — well below watermark, no regression.
- `ruff check firestarter/cli_handlers.py tests/test_write_skip_erase_0x0d.py` → all checks passed.
- `ruff format --check firestarter/cli_handlers.py tests/test_write_skip_erase_0x0d.py` → both formatted (test file was auto-reformatted once by `ruff format`, then verified clean).
- `python3 tools/check_devtest_orchestrator.py` → PASS (no new unlisted helper introduced; the D-13 arm is inline, not a new named function).
- Deliberate-break proof (task 2 acceptance criterion): widened `if skip_erase and is_protocol_0x0d:` to `if (skip_erase or not blank_check) and is_protocol_0x0d:`, ran `test_blank_check_flag_on_0x0d_does_not_produce_an_erase_warning` → **FAILED** as expected (the erase-warning line leaked onto the blank-check-flag path), then restored the original condition and re-ran → **PASSED**.
- Flags-invariance check (task 1 acceptance criterion): `build_flags(True, False, False, False, skip_erase=True, skip_sdp_unlock=False)` → `0x4` (`FLAG_SKIP_ERASE` set) — identical whether the chip is protocol-0x0D (warning prints) or not (warning suppressed), confirmed via `write_eprom.call_args` comparison in `test_skip_erase_warning_does_not_change_the_emitted_flags`.
- `git -C /workspaces/firestarter_app status --porcelain` — only pre-existing, out-of-scope untracked/modified files remain (`.gitignore`, `.coverage`, `.planning/config.json`, `SECURITY.md`, `doc/lockable-proms.md`, `write_test_port.sh`); both plan files (`cli_handlers.py`, `tests/test_write_skip_erase_0x0d.py`) are committed.
- `.planning/REQUIREMENTS.md` — untouched (verified via `git -C /workspaces status --porcelain .planning/REQUIREMENTS.md`, empty output).
- `firestarter/submit.py` and `tests/test_submit.py` — not read or modified (owned by plan 121-11 this wave).

## Next Phase Readiness
- D-13's runtime half is closed; plan 121-13 can now write the GATE-02 documentation statement citing this arm plus the RESEARCH C-8 scope split (why `-b` is exempt) as settled fact rather than a wart.
- No blockers for 121-11 (submit.py, untouched) or 121-12/121-13 (GATE-02 documentation, still open).

## Self-Check: PASSED

- FOUND: `firestarter_app/firestarter/cli_handlers.py`
- FOUND: `firestarter_app/tests/test_write_skip_erase_0x0d.py`
- FOUND: `.planning/phases/121-dev-test-fix-gates-docs-redesign/121-10-SUMMARY.md`
- FOUND commit `40811a4` (firestarter_app, feat)
- FOUND commit `48ec222` (firestarter_app, test)
- FOUND commit `085878d` (meta, docs)

---
*Phase: 121-dev-test-fix-gates-docs-redesign*
*Completed: 2026-07-29*
