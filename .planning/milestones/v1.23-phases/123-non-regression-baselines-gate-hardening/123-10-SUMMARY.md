---
phase: 123-non-regression-baselines-gate-hardening
plan: 10
subsystem: testing
tags: [python, pytest, subprocess, regex, honesty-gate, py32f071]

# Dependency graph
requires:
  - phase: 122-close-honesty-ledger-community-ask-release-decision
    provides: check_permitted_claims.py's env-seam contract, two-guard fail-closed/never-vacuous shape, and the checker+fixture+pytest convention this plan copies and adapts
provides:
  - "v1.23 check_permitted_claims.py: 8-phrase forbidden-claim table, PY32F071 required caveat, D-16 line-scoped proximity scoping, D-15 all-or-nothing arming over the four named Phase 130 closing artifacts"
  - "Five committed fixtures proving both directions of D-16 (a py32 overclaim fires; a legitimate AVR bench-validated sentence does not)"
  - "test_check_permitted_claims.py: 10 subprocess-only tests, including the D-16 adjacency-mutation proof and the D-15 arming-transition proof driven from an isolated tmp_path copy"
affects: [123-11, Phase 130 close]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Line-scoped (not sentence-scoped) proximity window for co-occurrence gating in markdown/prose scanners"
    - "All-or-nothing arming over a named-but-not-yet-existing artifact set (D-15), distinct from ordinary fail-closed on explicit targets"
    - "Driving a default-target-resolution code path under test by copying the checker script itself into an isolated tmp_path, rather than creating real artifacts"

key-files:
  created:
    - .planning/phases/123-non-regression-baselines-gate-hardening/check_permitted_claims.py
    - .planning/phases/123-non-regression-baselines-gate-hardening/test_check_permitted_claims.py
    - .planning/phases/123-non-regression-baselines-gate-hardening/fixtures/clean_control.md
    - .planning/phases/123-non-regression-baselines-gate-hardening/fixtures/clean_control_second.md
    - .planning/phases/123-non-regression-baselines-gate-hardening/fixtures/clean_avr_bench_control.md
    - .planning/phases/123-non-regression-baselines-gate-hardening/fixtures/planted_py32_overclaim.md
    - .planning/phases/123-non-regression-baselines-gate-hardening/fixtures/planted_missing_caveat.md
  modified: []

key-decisions:
  - "Reused the FIRESTARTER_CLAIMSCAN_TARGETS env-var name verbatim across the two phase directories per RESEARCH assumption A3 (the two checkers never coexist in one process); documented the suffix-if-ever-shared fallback in a comment"
  - "Hoisted the never-vacuous guard above the missing-target guard in main() (deliberate hardening over v1.22's fragile ordering, observable behaviour unchanged)"
  - "D-16 implemented as a 3-line window (PROXIMITY_WINDOW=1) over scan_text's line-by-line matching, not sentence segmentation, to avoid mangling version numbers, filenames and markdown tables"
  - "D-15 arming applies only to the true default-target path (no argv, no env seam); argv/env-seam-resolved targets keep the ordinary fail-closed guard"

requirements-completed: []  # This plan ticks nothing per requirement_closure; BASE-07/BASE-08 close in 123-11.

coverage:
  - id: D1
    description: "check_permitted_claims.py carries the 8-row v1.23 phrase table, the PY32F071 caveat, D-16 proximity scoping, and D-15 all-or-nothing arming over the four named Phase 130 artifacts"
    requirement: "BASE-07"
    verification:
      - kind: unit
        ref: "test_check_permitted_claims.py#test_scanner_exits_zero_on_clean_fixture"
        status: pass
      - kind: unit
        ref: "test_check_permitted_claims.py#test_d15_arming_both_directions"
        status: pass
    human_judgment: false
  - id: D2
    description: "D-16 proximity scoping is proven in both directions with committed fixtures and a mutation test proving suppression is real"
    requirement: "BASE-08"
    verification:
      - kind: unit
        ref: "test_check_permitted_claims.py#test_d16_negative_direction_avr_bench_control_passes"
        status: pass
      - kind: unit
        ref: "test_check_permitted_claims.py#test_d16_proximity_suppression_is_real_not_accidental"
        status: pass
    human_judgment: false

duration: 20min
completed: 2026-07-30
status: complete
---

# Phase 123 Plan 10: v1.23 Claim Gate — check_permitted_claims.py Summary

**Copied and adapted v1.22's honesty-claim scanner into Phase 123: an 8-row forbidden-phrase table gated to a `PY32F071`/`py32` token within a 3-line window (D-16), armed all-or-nothing over four named Phase 130 closing artifacts that don't exist yet (D-15), proven by five fixtures and ten subprocess tests.**

## Performance

- **Duration:** ~20 min
- **Tasks:** 3/3 completed
- **Files created:** 7 (1 checker, 1 test module, 5 fixtures)

## Accomplishments

- `check_permitted_claims.py` carries `FORBIDDEN_PATTERNS` with exactly 8 labelled, case-insensitive entries (`runs-on-py32`, `works-end-to-end`, `silicon-verified`, `bench-validated`, `hardware-validated`, `flashed-a-py32`, `closed-loop-vpp`, `pin-map-correct`), cross-checked against both `REQUIREMENTS.md` §Validation Ceiling and the research-supplied table — both sources agree on all eight.
- `REQUIRED_CAVEAT_PROSE = "no PY32F071 hardware exists"` with a whitespace-tolerant `REQUIRED_CAVEAT_PATTERN`.
- D-16 proximity scoping: `PY32_TOKEN_RE` (matches `py32`/`PY32`/`PY32F071` case-insensitively) and `PROXIMITY_WINDOW = 1` (a 3-line window) implemented inside `scan_text`, which now returns `(label, substring, line_number)` triples so the FAIL bucket can name the offending line.
- D-15 all-or-nothing arming: `_DEFAULT_TARGETS` names exactly four `_HERE`-relative paths — `130-LEDGER.md`, `130-DECISION.md`, `130-RELEASE-NOTES-fw.md`, `130-RELEASE-NOTES-app.md`. Running the checker today (no argv, no env seam) prints:
  ```
  UNARMED: none of the 4 named v1.23 closing artifacts for Phase 130 exist yet (130-LEDGER.md, 130-DECISION.md, 130-RELEASE-NOTES-fw.md, 130-RELEASE-NOTES-app.md) -- the close has not started, so the claim gate has nothing to scan yet. This is expected before Phase 130 runs.
  ```
  and exits 0. Arming applies only to the default-target path; a fully explicit target list (argv or env seam) always uses the ordinary fail-closed guard instead.
- The never-vacuous guard (`if not targets`) is hoisted above the missing-target guard in `main()` — a deliberate hardening over v1.22's fragile ordering (the literal string `"if not targets"` occurs before the first `"missing = ["` in the file).
- Five fixtures under `fixtures/`, all unreachable from `_DEFAULT_TARGETS` (which names only `130-*.md` one directory up):
  - `clean_control.md` / `clean_control_second.md` — clean passages carrying the caveat, exit 0; used together to prove the anti-skip PASS line names both basenames.
  - `clean_avr_bench_control.md` — **D-16's negative direction, no v1.22 analogue.** Contains true AVR sentences (`"the Leonardo target remains bench-validated from v1.15"`, `"...Uno target remains hardware-validated..."`) that must NOT fire, plus the required caveat separated by a documented 2-blank-line gap. Exits 0.
  - `planted_py32_overclaim.md` — `"the PY32F071 target is bench-validated"` on one line, co-occurring with a py32 token; exits non-zero naming `bench-validated`.
  - `planted_missing_caveat.md` — clean prose, no caveat; exits non-zero naming the missing-caveat bucket alone.
- `test_check_permitted_claims.py` — 10 subprocess-only tests (never imports the scanner), `10 passed, 0 failed, 0 skipped`:
  1. Clean pass through the seam.
  2. Planted py32 overclaim fires, `bench-validated` label asserted by name.
  3. D-16 negative direction: `clean_avr_bench_control.md` exits 0 despite containing `bench-validated`.
  4. D-16 adjacency-mutation proof: copies the fixture, inserts a py32-token line immediately adjacent to the `bench-validated` line, asserts the run now FAILS — proving test 3 passed because of suppression, not because the pattern never matched.
  5. Missing-caveat fixture fires, the specific bucket message asserted.
  6. Never-vacuous on an explicitly empty env-seam value — asserts the specific `"no scan targets resolved"` message, not merely non-zero exit.
  7. Fail-closed on a nonexistent target, naming the path.
  8. D-15 arming both directions — copies `check_permitted_claims.py` itself into an isolated `tmp_path` (its `_HERE` then resolves inside `tmp_path`, so `_DEFAULT_TARGETS` point at `tmp_path/130-*.md`, never the real Phase 130 directory). Direction 1: zero of the four present → `UNARMED:`, exit 0. Direction 2: create exactly `130-LEDGER.md` in `tmp_path` → armed but incomplete → exit non-zero, naming the three still-missing artifacts by name. Asserts (redundantly, as a belt-and-braces check) that the real Phase 130 directory carries no `130-*.md` as a side effect.
  9. Positional argv overrides the env seam (precedence pin).
  10. PASS line names both scanned files at once (anti-skip).

## Task Commits

1. **Task 1: Copy and adapt check_permitted_claims.py** — `04a55e0` (feat)
2. **Task 2: Author the five fixtures** — `503e207` (test)
3. **Task 3: Write test_check_permitted_claims.py** — `3db280d` (test)

**Plan metadata:** committed separately below.

## Files Created/Modified

- `.planning/phases/123-non-regression-baselines-gate-hardening/check_permitted_claims.py` — the v1.23 claim gate
- `.planning/phases/123-non-regression-baselines-gate-hardening/test_check_permitted_claims.py` — 10-test pytest module
- `.planning/phases/123-non-regression-baselines-gate-hardening/fixtures/clean_control.md`
- `.planning/phases/123-non-regression-baselines-gate-hardening/fixtures/clean_control_second.md`
- `.planning/phases/123-non-regression-baselines-gate-hardening/fixtures/clean_avr_bench_control.md`
- `.planning/phases/123-non-regression-baselines-gate-hardening/fixtures/planted_py32_overclaim.md`
- `.planning/phases/123-non-regression-baselines-gate-hardening/fixtures/planted_missing_caveat.md`

## Decisions Made

- Kept the `FIRESTARTER_CLAIMSCAN_TARGETS` env-var name identical to v1.22's (RESEARCH assumption A3), rather than suffixing it, since the two checkers live in different phase directories and never coexist in one process; documented the suffix-if-ever-shared fallback in a comment.
- Hoisted the never-vacuous guard above the missing-target guard as a deliberate hardening over v1.22's latent ordering wart, per the plan's explicit instruction — observable behaviour is unchanged.
- Implemented D-16 as a 3-line window over line-by-line matching rather than sentence segmentation, per the plan's explicit reasoning about markdown tables/version numbers/filenames having no reliable sentence terminator.
- Drove the D-15 arming-transition test (test 8) by copying the checker script itself into `tmp_path` rather than creating any file in the real Phase 130 directory — this is the mechanism the plan asked to be named and justified in the test docstring.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Task 1's literal automated-verify snippet raises `NameError: name '__file__' is not defined` when `exec`'d, independent of the file under test**
- **Found during:** Task 1 verification
- **Issue:** The plan's `<verify><automated>` block for Task 1 does `exec(compile(src..., 'c', 'exec'), ns)` without first seeding `ns['__file__']`. `check_permitted_claims.py`'s module-top `_HERE = os.path.dirname(os.path.abspath(__file__))` line therefore raises `NameError` under `exec` for ANY well-formed copy — reproduced identically against v1.22's original, unmodified `check_permitted_claims.py` run through the same literal snippet, confirming the defect is in the verify harness's exec invocation, not in this plan's implementation.
- **Fix:** No change to `check_permitted_claims.py` (it is correct and matches the v1.22 precedent exactly). Verified the equivalent property manually by seeding `ns = {'__file__': 'check_permitted_claims.py'}` before `exec`, which reproduces the same assertions the plan's snippet intends, all passing (`CLAIMGATE_SRC_OK`, `CLAIMGATE_OK`). The real-world invocation path (`python3 check_permitted_claims.py`, used throughout Tasks 2/3 and the pytest suite) works correctly and unmodified — this issue only affects the literal in-process `exec` harness text, never the shipped checker.
- **Files modified:** none (verification-only workaround)
- **Verification:** All of Task 1's other assertions (8 labels, caveat prose, `PROXIMITY_WINDOW`, 4 default targets, guard hoist ordering, docstring substrings) pass with the seeded namespace; `python3 check_permitted_claims.py` (real subprocess invocation, no `exec` involved) independently confirms `UNARMED:` + exit 0.
- **Committed in:** `04a55e0` (Task 1 commit; no separate fix commit needed since nothing in the shipped file changed)

---

**Total deviations:** 1 auto-fixed (1 blocking, verification-harness-only — no code change)
**Impact on plan:** None on the shipped checker or its behavior. No scope creep.

## Issues Encountered

- First draft of `clean_avr_bench_control.md` had its own explanatory HTML comment literally naming both forbidden phrases (`bench-validated`, `hardware-validated`) directly adjacent to a sentence that also used the word "py32" — which put a py32 token inside the proximity window of the comment's own phrase mentions and caused the fixture to (correctly, but unintentionally) fail. Rewrote the explanatory comment to avoid combining forbidden-phrase words with the py32 token, re-verified exit 0. This was caught and fixed before committing — not a deviation from the shipped checker, a fixture-authoring correction.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The v1.23 claim gate exists and is fully tested seven phases before Phase 130 writes any of the four artifacts it will scan — running it today correctly reports `UNARMED:` rather than a false pass or a false fail.
- 123-11 (the next plan touching this gate) can now run it against `123-NONREGRESSION.md` and any other in-phase prose; BASE-07 and BASE-08 remain open until 123-11 explicitly closes them, per this plan's `requirement_closure` instruction.
- Phase 130 must read the module docstring's "Phase 130 coupling" paragraph before naming its four closing artifacts: it must produce exactly `130-LEDGER.md`, `130-DECISION.md`, `130-RELEASE-NOTES-fw.md`, `130-RELEASE-NOTES-app.md`, or amend `_DEFAULT_TARGETS` in the same commit that renames one.

---
*Phase: 123-non-regression-baselines-gate-hardening*
*Completed: 2026-07-30*

## Self-Check: PASSED

All 7 created files found on disk; all 3 task commits (`04a55e0`, `503e207`, `3db280d`) plus the SUMMARY commit (`707de49`) found in `git log --oneline --all`.
