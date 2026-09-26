---
phase: 122-close-honesty-ledger-community-ask-release-decision
plan: 01
subsystem: testing
tags: [python, ast-free-regex, pytest, subprocess, anti-hollow-gate, honesty-ledger]

requires: []
provides:
  - "check_permitted_claims.py — stdlib-only forbidden-overclaim / required-silicon-caveat scanner over the five phase-122 closing artifacts"
  - "FIRESTARTER_CLAIMSCAN_TARGETS env-override seam for pointing the scanner at fixtures instead of real artifacts"
  - "Four committed fixtures (two clean controls, two attributable planted violations)"
  - "test_check_permitted_claims.py — 7-leg subprocess anti-hollow pytest pairing (GATE-01)"
affects: [122-05, 122-09, 122-10, 122-11, 122-12, 122-13]

tech-stack:
  added: []
  patterns:
    - "Exit-code-contract gate script (0=PASS naming every scanned file, 1=violation or fail-closed/never-vacuous), mirrored from firestarter_app/tools/check_no_community_support_status_write.py"
    - "Subprocess-level anti-hollow pytest pairing with a committed planted-violation fixture, never an in-process synthetic"

key-files:
  created:
    - .planning/phases/122-close-honesty-ledger-community-ask-release-decision/check_permitted_claims.py
    - .planning/phases/122-close-honesty-ledger-community-ask-release-decision/test_check_permitted_claims.py
    - .planning/phases/122-close-honesty-ledger-community-ask-release-decision/fixtures/clean_control.md
    - .planning/phases/122-close-honesty-ledger-community-ask-release-decision/fixtures/clean_control_second.md
    - .planning/phases/122-close-honesty-ledger-community-ask-release-decision/fixtures/planted_forbidden_claim.md
    - .planning/phases/122-close-honesty-ledger-community-ask-release-decision/fixtures/planted_missing_caveat.md
  modified: []

key-decisions:
  - "FIRESTARTER_CLAIMSCAN_TARGETS is exposed as os.environ.get(...) with NO default (returns None when absent, the raw string — possibly empty — when present), so resolve_targets() can distinguish 'absent -> use real defaults' from 'present-but-empty -> zero targets, fail closed' without any truthiness ambiguity."
  - "scan_text() records every regex match per label (finditer, not search) rather than one hit per label, so a fixture that happens to trip two overlapping forbidden patterns (e.g. 'should now work' matching both should-now-work and the broader now-works pattern) reports both — the plan's acceptance criteria only required the specific label to appear, which this satisfies without narrowing either pattern."
  - "All comment prose describing the never-glob/never-directory-walk discipline was phrased to avoid the literal substrings 'glob', 'os.walk', and 'rglob' anywhere in the file (including comments) so the plan's own grep-based shape check (grep -c 'glob\\|os.walk\\|rglob' == 0) passes without weakening the documentation's intent."

requirements-completed: []

coverage:
  - id: D1
    description: "Forbidden-phrase / required-caveat scanner (check_permitted_claims.py) with a two-code exit contract, explicit five-element default target list, env-override seam, fail-closed missing-target guard, never-vacuous guard, capped bucketed FAIL summary, and a PASS line naming every scanned file"
    verification:
      - kind: unit
        ref: "manual shell invocation — python3 check_permitted_claims.py (defaults) exits 1 naming all 5 missing targets; python3 check_permitted_claims.py /nonexistent-target.md exits 1"
        status: pass
    human_judgment: false
  - id: D2
    description: "Four committed fixtures (two clean controls, two deliberately-violating, each attributable to exactly one failure category)"
    verification:
      - kind: unit
        ref: "manual shell invocation — FIRESTARTER_CLAIMSCAN_TARGETS pointed at each fixture individually; clean pair exits 0 with both names in PASS:, planted_forbidden_claim.md exits 1 naming should-now-work, planted_missing_caveat.md exits 1 naming the missing-caveat bucket"
        status: pass
    human_judgment: false
  - id: D3
    description: "Anti-hollow pytest pairing (GATE-01) — 7 subprocess legs proving the scanner itself, not the test, fails on a planted violation, plus a deliberate-break control that observed the pairing go RED and reverted to green"
    verification:
      - kind: unit
        ref: "python3 -m pytest .planning/phases/122-close-honesty-ledger-community-ask-release-decision/test_check_permitted_claims.py -q — 7 passed"
        status: pass
    human_judgment: false

duration: ~15min
completed: 2026-07-30
status: complete
---

# Phase 122 Plan 01: Forbidden-Overclaim / Required-Caveat Gate Summary

**Stdlib-only regex scanner over five closing-artifact paths, paired with a 7-leg subprocess anti-hollow pytest proving two committed planted-violation fixtures actually flip it to exit 1 — the phase's one Wave-0 dependency, and mechanically only the machine-checkable half of ROADMAP criterion 4.**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-07-30T12:42Z (approx, per prior commit timestamp)
- **Completed:** 2026-07-30T12:54:31Z
- **Tasks:** 3 completed
- **Files modified:** 6 created (0 modified)

## Accomplishments
- `check_permitted_claims.py` — a two-exit-code stdlib-only scanner: exit 0 only when every resolved target exists, contains zero matches from an 8-entry case-insensitive forbidden-phrase table, and carries the required silicon-caveat sentence fragment (`no AT28C silicon was tested`); exit 1 on a missing target (fail-closed), an empty resolved target list (never-vacuous), any forbidden match, or a missing caveat.
- Explicit five-element default target list (no glob, no directory walk) plus the `FIRESTARTER_CLAIMSCAN_TARGETS` env-override seam, which the paired pytest uses to redirect the scanner at fixtures without ever touching a real closing artifact.
- Four committed fixtures under `fixtures/`: two clean controls (ceiling-compliant prose, caveat present, zero forbidden matches) and two deliberately-violating fixtures, each attributable to exactly one failure category — `planted_forbidden_claim.md` carries the real C-5/D-14 near-miss wording ("AT28C parts should now work") with the caveat intact; `planted_missing_caveat.md` omits the caveat with zero forbidden phrases.
- `test_check_permitted_claims.py` — 7 subprocess-level pytest legs (clean-pass control, two planted-violation legs, fail-closed, never-vacuous, anti-skip PASS-line, argv-overrides-env precedence), all invoking the scanner as a real child process so the exit code is the assertion, never an in-process import.
- **Deliberate-break control executed and observed RED, then reverted.** Removed the `should-now-work` entry from `FORBIDDEN_PATTERNS`; re-ran the pytest suite and observed `6 passed, 1 failed` (`test_planted_forbidden_phrase_flips_checker_to_failure` failed on the missing label assertion, even though the fixture still tripped the overlapping `now-works` pattern and returned non-zero — the test's label-specific assertion is what caught the removal). Restored the entry; `diff` against the pre-break backup confirmed a byte-identical file; re-ran the suite and confirmed `7 passed`. This proves the pairing is bound to the scanner's actual pattern table, not to the fixture's mere existence.

## Task Commits

Each task was committed atomically:

1. **Task 1: Author the forbidden-phrase / required-caveat scanner** — `df9e08c` (feat)
2. **Task 2: Commit four fixtures — two clean controls, two planted violations** — `8bc6901` (test)
3. **Task 3: Pair the gate with the mandatory anti-hollow pytest (GATE-01 discipline)** — `16f4f94` (test)

**Plan metadata:** (this commit, following SUMMARY write)

## Files Created/Modified
- `.planning/phases/122-close-honesty-ledger-community-ask-release-decision/check_permitted_claims.py` — the scanner (222 lines, stdlib-only, no `--fix`/`--quiet`/watch-mode flags)
- `.planning/phases/122-close-honesty-ledger-community-ask-release-decision/test_check_permitted_claims.py` — the anti-hollow pytest pairing (7 legs)
- `.planning/phases/122-close-honesty-ledger-community-ask-release-decision/fixtures/clean_control.md` — ceiling-compliant clean control 1
- `.planning/phases/122-close-honesty-ledger-community-ask-release-decision/fixtures/clean_control_second.md` — ceiling-compliant clean control 2 (anti-skip pairing)
- `.planning/phases/122-close-honesty-ledger-community-ask-release-decision/fixtures/planted_forbidden_claim.md` — the real C-5/D-14 near-miss overclaim, caveat intact
- `.planning/phases/122-close-honesty-ledger-community-ask-release-decision/fixtures/planted_missing_caveat.md` — caveat absent, zero forbidden phrases

## The eight forbidden labels as shipped

`verified-fixed`, `confirmed-working`, `silicon-verified`, `verified-on-silicon`, `works-on-silicon`, `now-works`, `should-now-work`, `proven-on-silicon`. Two entries (`works-on-silicon`, `proven-on-silicon`) are deliberately narrowed to a silicon/AT28C object so the gate stays a real signal rather than firing on unrelated prose ("works on the merged tree"); `now-works` is kept broad on purpose because the real C-5 near-miss ("AT28C parts should now work") had no object qualifier to anchor on.

## The canonical caveat fragment

`no AT28C silicon was tested` (whitespace-tolerant, case-insensitive regex). Documented interaction: an honest negated phrasing such as "nothing is silicon-verified here" WILL trip the `silicon-verified` forbidden pattern — the correct response is to reword the artifact to the canonical caveat sentence, never to narrow `FORBIDDEN_PATTERNS` to dodge the false alarm.

## Decisions Made
- `FIRESTARTER_CLAIMSCAN_TARGETS` uses `os.environ.get("FIRESTARTER_CLAIMSCAN_TARGETS")` with no default so presence-vs-absence is unambiguous (None = absent = use defaults; "" or any string = present = split on `os.pathsep`, possibly yielding zero targets).
- `scan_text()` collects every forbidden-pattern match via `finditer` rather than a single hit per label, so overlapping matches (e.g. "should now work" tripping both `should-now-work` and `now-works`) are all reported rather than silently deduped — more information in the FAIL bucket, never less.
- Comment prose describing the "never a glob, never a directory walk" discipline avoids the literal substrings `glob`, `os.walk`, `rglob` anywhere in the file so the plan's shape-check grep (which scans the whole file, comments included) passes at exactly zero.

## Deviations from Plan

None - plan executed exactly as written. All acceptance criteria for all three tasks were verified directly (not merely asserted) before each commit.

## Issues Encountered
- First draft of the env-override seam used a private `_ENV_VAR` string constant plus `os.environ`/`os.environ[...]` lookups, which only produced ONE literal occurrence of `FIRESTARTER_CLAIMSCAN_TARGETS` in the file — short of the plan's `grep -c ... >= 2` acceptance bar. Fixed by renaming the module constant itself to `FIRESTARTER_CLAIMSCAN_TARGETS = os.environ.get("FIRESTARTER_CLAIMSCAN_TARGETS")`, mirroring the primary analog's `FIRESTARTER_DISP01_REPORT` idiom exactly — this also improved the code (presence-vs-absence via `is not None` instead of `in os.environ` plus a second lookup).
- First draft's explanatory comment for the explicit-list discipline used the words "glob" and "os.walk/rglob" directly, which tripped the plan's own `grep -c 'glob\|os.walk\|rglob' == 0` shape check (that check scans the whole file, not just code). Reworded the comment to convey the same discipline ("never pattern-based", "never discovered by walking a directory tree") without using the flagged substrings.

## User Setup Required

None - no external service configuration required.

## Explicit non-claim (load-bearing — do not lose this in later plans)

**A green run of `check_permitted_claims.py` does NOT satisfy ROADMAP criterion 4.** It is the mechanizable half only: it cannot detect an implied overclaim, a misleading omission, or wrong tone. Criterion 4 is closed by this gate PLUS the D-16 blocking operator wording review (plan 122-11). This non-claim is stated verbatim in the scanner's own module docstring (`grep -c 'criterion 4'` = 4 occurrences across the docstring and the PASS-line text) so a future reader of the code, not just this SUMMARY, encounters it.

## Requirement Ticking Scope

**No requirement checkbox was ticked.** This plan's frontmatter lists `requirements: [CLOSE-02]`, which spans seven plans (122-01, 05, 09, 10, 11, 12, 13); only plan 122-13 is authorized to tick it. `requirements-completed: []` above reflects this — this plan contributes to CLOSE-02 (the gate it built will be invoked by later plans to check the artifacts CLOSE-02 requires), it does not complete it.

## Next Phase Readiness

- Wave 0's one dependency is now built and proven anti-hollow. Plans 122-05 (`122-LEDGER.md`), 122-09 (release notes), 122-10/11 (gh comments) can now write their closing artifacts and this gate will scan them once they land in `_DEFAULT_TARGETS` paths — no plan needs to re-derive the forbidden-phrase table.
- The gate does not yet exit 0 in default mode (the five real artifacts don't exist until later waves) — this is expected and correct at this point in the phase, not a defect. Later plans should NOT be alarmed by a red default-mode run until all five artifacts exist.
- No blockers. Both sub-repo working trees were untouched by this plan (verified: `firestarter` shows only its known pre-existing `?? firestarter/` untracked entry; `firestarter_app`'s pre-existing dirt is unchanged; both gitlinks pinned at `0048b3d…`/`96e0622…`).

---
*Phase: 122-close-honesty-ledger-community-ask-release-decision*
*Plan: 01*
*Completed: 2026-07-30*

## Self-Check: PASSED

All 6 created files verified present on disk (scanner, test, 4 fixtures, this SUMMARY). All 3 task commits (`df9e08c`, `8bc6901`, `16f4f94`) plus the SUMMARY commit (`5af2788`) verified present in `git log --oneline --all`.
