---
phase: 113-submission-flow
verified: 2026-07-03T18:00:00Z
status: passed
score: 3/3 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 113: Submission Flow Verification Report

**Phase Goal:** A tester who wants to help can file their diagnostic report to the project's GitHub issue tracker with one flag, safely — without leaking their filesystem paths, without a report so large it silently truncates, and never by accident.

**Verified:** 2026-07-03T18:00:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `--submit` files the report via a tiered flow (`gh issue create --body-file -` stdin, label `gsd-inbox`, when `gh` present+authed; else a prefilled `issues/new` browser URL) guarded to stay under the ~8 KB server cap, escalating/omitting the JSON block past ~7.5 KB encoded | ✓ VERIFIED | `submit.py:194-238` (`gh_available` PATH+auth gated, `submit_via_gh` uses list argv `["gh","issue","create","--repo",SUBMIT_REPO,"--label","gsd-inbox",...,"--body-file","-"]` with `input=body`); `submit.py:253-304` (`submit_via_browser` measures `len(url.encode("utf-8"))`, drops JSON past `_URL_ESCALATE_BYTES=7500`, hard-stops (no `browser_open` call) past `_URL_HARD_CAP_BYTES=8000`); tests `test_gh_tier_*`, `test_oversize_*`, `test_browser_tier_*` all pass (`pytest tests/test_submit.py` 76/76 collected pass) |
| 2 | Before anything is sent, the report is sanitized (whitelisted field set only, paths/PII scrubbed, byte dumps hex/base64-encoded), the sanitized body is shown to the tester for explicit confirmation, and submission never happens as a side effect of a bare `dev test` run | ✓ VERIFIED | `submit.py:101-118` (`sanitize_dict` deep-copies + scrubs `/home`, `/Users`, `C:\Users`, `/dev/ttyACM\|USB*`, `/dev/tty.*`, `COM*`, `/tmp/*`, current username, base64-encodes bytes); `submit.py:312-399` (`submit_report`: prints sanitized `body` via `_print` then calls `confirm_fn` before any dispatch; off-TTY prints+returns without opening browser/gh); `cli_handlers.py:1781-1791,1919-1922` (`--submit` is a Click `is_flag`, default `False`; the `submit_report` call site is inside `if submit:` — a bare run never reaches it); tests `test_sanitize_*` (13 tests, one per vector + mutation/nested), `test_refuse_*`, `test_tty_*`, `test_offtty_*`, `TestSubmitFlag::test_bare_run_never_calls_submit_report` all pass |
| 3 | Every submitted report carries a deterministic dedup fingerprint (chip identity + key result fields) recognizable by a maintainer triaging repeats | ✓ VERIFIED | `diagnostic_report.py:171-196` (`dedup_fingerprint` = sha256 of `chip\|protocol\|op=verdict:classification...` truncated to 12 hex chars, excludes `generated`/`host_version`/measured mV/`error_code`/`reason`); `diagnostic_report.py:396` (`to_dict()["dedup_fingerprint"]` — single source, inherited by `render()`/`to_json_block()`); `submit.py:141-151` (`build_title` reads `report.to_dict()["dedup_fingerprint"]` into `[dev test] <chip> — <verdict> (<shorthash>)`); 10 `test_dedup_*` tests (determinism, volatile-exclusion, reason/error_code exclusion, sensitivity, graceful degradation, to_dict/json_block propagation) all pass |

**Score:** 3/3 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_app/firestarter/diagnostic_report.py :: dedup_fingerprint()` | module-level deterministic hash helper | ✓ VERIFIED | Present at line 174, sibling of `is_submittable` (154), reads only `AutoCapture.chip/.protocol` + per-step `op/verdict/fingerprint.classification`; wired into `to_dict()` at line 402 |
| `firestarter_app/firestarter/submit.py` | new orchestrator-only submission module | ✓ VERIFIED | 400 lines; constants `SUBMIT_REPO`, `GSD_INBOX_LABEL`, `_URL_ESCALATE_BYTES`, `_URL_HARD_CAP_BYTES`, `_SCRUBS`; functions `sanitize_dict`, `overall_verdict`, `build_title`, `build_body`, `build_issue_url`, `gh_available`, `submit_via_gh`, `submit_via_browser`, `submit_report` — all present, substantive, wired |
| `firestarter_app/firestarter/cli_handlers.py :: --submit flag` | Click flag + lazy call site on `dev_test` | ✓ VERIFIED | Lines 1784-1794 (flag decl), 1797-1803 (`submit: bool` param), 1919-1922 (lazy import + call site placed after persist, before `sys.exit`) |
| `firestarter_app/tools/check_devtest_orchestrator.py :: submit.py leg` | third full-scan SAFE-03 leg | ✓ VERIFIED | Lines 107-114 (`FIRESTARTER_DEVTEST_SUBMIT` env-override), 390-395 (full-scan aggregation); `python tools/check_devtest_orchestrator.py` exits 0 and PASS line names `submit.py` (confirmed by direct execution) |
| `firestarter_app/tests/test_submit.py` | sanitize/title/gh/browser/refuse/tty tests | ✓ VERIFIED | 76 tests collected, all pass |
| `firestarter_app/tests/test_diagnostic_report.py` | dedup determinism/exclusion tests | ✓ VERIFIED | `-k dedup` tests pass (10 tests); full file passes |
| `firestarter_app/tests/test_dev_test_cmd.py` | `--submit` end-to-end tests | ✓ VERIFIED | `TestSubmitFlag` class, 3 tests, all pass |
| `firestarter_app/tests/test_check_devtest_orchestrator.py` | planted+clean submit-leg fixtures | ✓ VERIFIED | 4 submit-related tests pass (real-PASS-line-naming, planted VPP-set, planted force, clean-fixture-override) |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `cli_handlers.py dev_test` | `submit.py submit_report` | lazy `from firestarter import submit as submit_mod` inside `if submit:` | ✓ WIRED | Call site passes in-memory `report`, `chip`, resolved `json_file` — no re-run; verified by reading the call site and by `test_submit_flag_calls_submit_report_once_with_report_chip_json_file` |
| `submit.py build_title` | `diagnostic_report.py to_dict()["dedup_fingerprint"]` | direct dict-key read | ✓ WIRED | `build_title` line 148-151 reads `report.to_dict()["dedup_fingerprint"]` |
| `submit.py submit_report` | `submit.py sanitize_dict → build_body → build_title` | in-process composition | ✓ WIRED | Lines 371-373: `sanitized = sanitize_dict(report.to_dict())`; `body`/`title` built from it; `test_tty_body_sent_to_gh_is_sanitized` / `test_tty_body_sent_to_browser_is_sanitized` prove the PII scrub survives to the seam |
| `submit.py submit_report` | `submit.py gh_available → submit_via_gh → submit_via_browser` (fallback) | tier dispatch | ✓ WIRED | Lines 385-399: gh preferred, falls back to browser on `None` return from `submit_via_gh`; `test_tty_confirm_gh_create_fails_falls_back_to_browser` proves this |
| `check_devtest_orchestrator.py main()` | `submit.py` (AST scan) | `_scan_file(FIRESTARTER_DEVTEST_SUBMIT)` full scan | ✓ WIRED | Lines 390-395 aggregate into the same violation buckets as the chip_test.py leg; `_assert_host_only` covers it (submit.py added to `targets`) |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Full firestarter_app suite has exactly the 3 known pre-existing failures, no new regressions | `python -m pytest tests/ --tb=no` | `3 failed, 913 passed in 46.85s` — failures are exactly `test_audit_coverage_matrix::test_golden_file_matches`, `test_characterization::test_no_programmer_found_read`, `test_characterization::test_no_programmer_found_erase` | ✓ PASS |
| Phase-113 test files pass in isolation | `pytest tests/test_submit.py tests/test_diagnostic_report.py tests/test_dev_test_cmd.py tests/test_check_devtest_orchestrator.py` | `109 passed in 1.20s` | ✓ PASS |
| SAFE-03 orchestrator gate passes and names submit.py | `python tools/check_devtest_orchestrator.py` | `PASS: scanned ../firestarter/chip_test.py, ../firestarter/cli_handlers.py, ../firestarter/submit.py; 0 VPP-set, 0 raw-wire-dict, 0 --force; firmware untouched (host-only, asserted)` exit=0 | ✓ PASS |
| Anti-hollow submit-leg fixtures | `pytest tests/test_check_devtest_orchestrator.py -k submit -v` | 4 passed (real PASS-line-naming, planted VPP-set → nonzero, planted force → nonzero, clean env-override fixture → zero) | ✓ PASS |
| `--submit` end-to-end wiring | `pytest tests/test_dev_test_cmd.py -k submit -v` | 3 passed | ✓ PASS |
| ruff style gate on phase-113 files | `ruff check` + `ruff format --check` on submit.py, diagnostic_report.py, cli_handlers.py, check_devtest_orchestrator.py, and the 4 phase-113 test files | `All checks passed!` / `8 files already formatted` | ✓ PASS |
| mypy watermark | `python tools/check_mypy_watermark.py` | `mypy errors: 1 (watermark: 35)` — 34 below watermark, no regression | ✓ PASS |
| submit.py test coverage | `pytest tests/ --cov=firestarter --cov-fail-under=70` | `firestarter/submit.py 118 0 100%` | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| SUB-01 | 113-02, 113-03, 113-04 | Tiered gh/browser submission flow with byte-cap guard | ✓ SATISFIED | `submit_via_gh`, `submit_via_browser`, `--submit` flag; all tests pass |
| SUB-02 | 113-02, 113-03, 113-04 | Sanitization + explicit/interactive-only confirm | ✓ SATISFIED | `sanitize_dict`, D-03/D-04 gates in `submit_report`; bare-run-never-submits test passes |
| SUB-03 | 113-01, 113-02 | Deterministic dedup fingerprint | ✓ SATISFIED | `dedup_fingerprint`, wired into `to_dict()` and `build_title` |

No orphaned requirements found — REQUIREMENTS.md maps only SUB-01/02/03 to Phase 113, and all three are declared across the four plans' frontmatter and closed.

### Anti-Patterns Found

None. Scanned `submit.py`, `diagnostic_report.py` (dedup section), and `check_devtest_orchestrator.py` (submit leg) for `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER`/empty-return stubs — zero matches. No debt markers.

### Human Verification Required

None. All three roadmap success criteria are backed by passing automated tests exercising the actual behavior (determinism, volatile-exclusion, sanitization per-vector, TTY/off-TTY dispatch, oversize escalation/hard-stop, gh-tier detection, SAFE-03 anti-hollow proof) — not just presence/wiring checks. No visual, real-time, or external-service-dependent behavior in this phase requires human judgment (the `gh` CLI and GitHub network interaction are both seam-injected and never exercised for real in the test suite, which is the correct approach for a CI-safe submission flow).

### Gaps Summary

No gaps. All three roadmap Success Criteria (SUB-01, SUB-02, SUB-03) are implemented, wired, and behaviorally verified by a comprehensive, passing test suite (109/109 phase-113-relevant tests; 913/916 in the full suite, with the 3 failures being pre-existing environment/golden-fixture artifacts unrelated to this phase, confirmed unchanged in count and identity). The SAFE-03 orchestrator gate was extended to a third full-scan leg for `submit.py` and proven non-hollow via planted-violation fixtures. Code quality gates (ruff, mypy watermark, coverage) are all green for the phase's files.

---

_Verified: 2026-07-03T18:00:00Z_
_Verifier: Claude (gsd-verifier)_
