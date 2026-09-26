---
phase: 113-submission-flow
plan: 03
subsystem: submission
tags: [github-issues, webbrowser, gh-cli, pii-sanitization, click, tty-gate]

# Dependency graph
requires:
  - phase: 113-submission-flow (Plan 02)
    provides: submit.py module with SUBMIT_REPO/GSD_INBOX_LABEL constants, byte
      thresholds, sanitize_dict, overall_verdict, build_title, build_body,
      build_issue_url, gh_available, submit_via_gh
provides:
  - submit_via_browser(title, body, saved_json_path, *, browser_open, console) with
    the D-05 oversize escalation (drop fenced JSON past 7.5 KB encoded, hard-stop
    past ~8 KB encoded, browser_open called at most once)
  - submit_report(report, chip, saved_json_path, *, which_fn, run_fn, browser_open,
    isatty_fn, confirm_fn, console) — the single orchestration entry composing every
    Plan-02 builder plus the new browser tier, implementing the D-03 refuse gate and
    D-04 TTY/off-TTY dispatch
affects: [113-04-submission-flow-cli-wiring, 114-disposition-close]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Byte-measurement-not-char-count guard: escalation always keys on
      len(url.encode('utf-8')) of the fully-encoded URL, never the raw body
      length (Pitfall 3)"
    - "Seam-injected orchestration function (which_fn/run_fn/browser_open/isatty_fn/
      confirm_fn, all keyword-injectable with real stdlib/rich defaults) mirroring
      the existing _is_interactive/Confirm.ask precedent in cli_handlers.py"
    - "Public-body filename-only redaction: the oversize note and every sent body
      reference the saved report by saved_json_path.name only; local console
      messages (never sent anywhere) may print the full path"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/submit.py
    - firestarter_app/tests/test_submit.py

key-decisions:
  - "submit_via_browser strips the fenced JSON block by splitting the already-built
    body string on the literal '\\n\\n```json\\n' marker (build_body's own fence
    format) rather than re-invoking build_body(..., include_json=False) — the
    function's signature (title, body, saved_json_path) never receives the
    sanitized_dict/results build_body needs, so operating on the string boundary is
    the only option consistent with the plan-mandated signature"
  - "Hard-stop message (path + gh-tier directive) is a LOCAL console print, not part
    of any submitted body — printing the full saved_json_path there is safe per
    RESEARCH ('a local hint printed to their own console, not embedded in the issue
    body'); only the escalation NOTE embedded in the public body is restricted to
    saved_json_path.name"
  - "Deferred marking SUB-01/SUB-02 Complete in REQUIREMENTS.md: both requirements
    also appear in 113-04's frontmatter, which wires the --submit Click flag and
    the real end-to-end CLI call site — until that lands, a bare `dev test` run has
    no way to reach submit_report at all, so the requirement is not yet fully
    satisfied from a user's perspective"

patterns-established:
  - "submit_via_browser/submit_report share a tiny internal _print(msg, console=)
    helper (console.print if given, else builtin print) rather than requiring every
    caller to branch on console is/isn't None"

requirements-completed: []  # SUB-01/SUB-02 intentionally left Pending — see key-decisions; 113-04 wires the CLI call site that fully satisfies them

coverage:
  - id: D1
    description: "submit_via_browser opens a prefilled issues/new URL under the cap and returns it"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_submit.py::test_browser_tier_small_body_opens_once"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_submit.py::test_browser_tier_under_cap_returns_the_url"
        status: pass
    human_judgment: false
  - id: D2
    description: "D-05 escalation drops the fenced JSON block past 7500 encoded bytes, naming only the saved report's filename in the public body"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_submit.py::test_oversize_drops_json_past_escalate_threshold"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_submit.py::test_oversize_note_names_filename_not_full_path"
        status: pass
    human_judgment: false
  - id: D3
    description: "D-05 hard-stop past ~8000 encoded bytes never opens the browser, in both the JSON-fence and no-fence cases"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_submit.py::test_oversize_hard_stop_no_open_past_cap"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_submit.py::test_oversize_hard_stop_no_json_fence_still_hard_stops"
        status: pass
    human_judgment: false
  - id: D4
    description: "D-03 refuse gate: a report missing chip/protocol/host_version is refused, naming the specific missing field(s), before any seam (isatty_fn/confirm_fn/browser_open/run_fn) is touched"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_submit.py::test_refuse_missing_protocol_prints_field_and_does_not_send"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_submit.py::test_refuse_never_calls_isatty"
        status: pass
    human_judgment: false
  - id: D5
    description: "D-04 off-TTY never sends (no browser/gh/confirm); on-TTY previews then confirms before dispatching to gh-or-browser, with a gh-create failure falling back to the browser tier"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_submit.py::test_offtty_prints_body_and_url_never_sends"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_submit.py::test_tty_decline_aborts_without_sending"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_submit.py::test_tty_confirm_gh_available_dispatches_to_gh_not_browser"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_submit.py::test_tty_confirm_gh_unavailable_dispatches_to_browser"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_submit.py::test_tty_confirm_gh_create_fails_falls_back_to_browser"
        status: pass
    human_judgment: false
  - id: D6
    description: "The body sent to either tier is always the sanitized one — a PII vector in a step reason never reaches gh's stdin or the browser URL unscrubbed"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_submit.py::test_tty_body_sent_to_gh_is_sanitized"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_submit.py::test_tty_body_sent_to_browser_is_sanitized"
        status: pass
    human_judgment: false

duration: 35min
completed: 2026-07-03
status: complete
---

# Phase 113 Plan 03: submit_via_browser + submit_report Summary

**Browser-tier D-05 byte-cap escalation (drop JSON at 7.5 KB encoded, hard-stop at 8 KB) plus the single `submit_report` orchestration entry implementing the D-03 refuse gate and D-04 TTY/off-TTY dispatch, all seam-injected against `test_submit.py`.**

## Performance

- **Duration:** 35 min
- **Started:** 2026-07-03
- **Completed:** 2026-07-03
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- `submit_via_browser` measures `len(url.encode("utf-8"))` on the fully-encoded URL, drops the fenced JSON block past 7500 bytes (appending a note naming only `saved_json_path.name`), and hard-stops (never opening the browser) past 8000 bytes — proven across the fits / JSON-dropped / hard-stop branches, including a case where the JSON fence never existed at all.
- `submit_report` refuses a non-submittable report (naming the missing `chip`/`protocol`/`host_version` field), never sends off-TTY, previews the sanitized body then confirms on a TTY, and dispatches to the `gh` tier (falling back to the browser tier on a `gh issue create` failure) or straight to the browser tier when `gh` is unavailable.
- Added 22 new unit tests (7 oversize/browser-tier + 15 refuse/tty), all seam-injected via `Mock` — zero PATH, network, browser, or terminal touched.

## Task Commits

Each task was committed atomically:

1. **Task 1: submit_via_browser with D-05 oversize escalation** - `1e497a5` (feat)
2. **Task 2: submit_report orchestration — D-03 refuse gate + D-04 TTY/off-TTY dispatch** - `f2f925d` (feat)

_Commits are inside the `firestarter_app` submodule on branch `v1.21-community-chip-validation-command` (planning.sub_repos protocol) — the meta repo has no matching per-task commits, only this SUMMARY.md + STATE.md + ROADMAP.md metadata commit._

## Files Created/Modified
- `firestarter_app/firestarter/submit.py` — added `_print`, `submit_via_browser`, `submit_report`
- `firestarter_app/tests/test_submit.py` — added 22 tests covering both new functions

## Decisions Made
- `submit_via_browser` drops the JSON block by splitting the pre-built `body` string on its own fence marker rather than re-calling `build_body(..., include_json=False)`, since the plan-mandated signature (`title, body, saved_json_path`) never receives the `sanitized_dict`/`results` that `build_body` needs — the string-boundary split is the only implementation consistent with that signature while still satisfying every `<behavior>` clause.
- The hard-stop message prints the full `saved_json_path` to the tester's own console (never sent anywhere) — RESEARCH explicitly permits this ("a local hint printed to their own console, not embedded in the issue body"); only the escalation note embedded in the *public* body is restricted to `saved_json_path.name`.
- Left `SUB-01`/`SUB-02` unchecked in REQUIREMENTS.md — both are also `113-04`'s frontmatter requirements, and `113-04` is what wires the `--submit` Click flag / real CLI call site. Until that lands, a bare `dev test` run has no way to reach `submit_report`, so the requirement isn't fully satisfied from a user's perspective yet.

## Deviations from Plan

None — plan executed exactly as written. Both `<must_haves>` truths and every `<behavior>` clause in both tasks are covered by a named test.

## Issues Encountered
- Constructing an oversize test body that is small by raw char count but large by encoded byte count required empirical measurement (letters/digits don't expand under `urllib.parse.quote`; spaces/quotes/braces/newlines each expand 3x via `%XX`). Resolved by building a payload of space-separated tokens repeated a computed number of times (183) rather than a naive `"x" * N` string, which would not have demonstrated the byte-vs-char distinction Pitfall 3 warns about.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- `submit.py` is now feature-complete for Phase 113's non-wiring scope: every builder (Plan 02) plus both tiers (`submit_via_gh` Plan 02, `submit_via_browser` this plan) plus the single orchestration entry (`submit_report`, this plan) exist and are fully unit-tested.
- Ready for Plan 04: add the `--submit` Click flag + lazy `submit_report` call site to `dev_test` in `cli_handlers.py`, and extend `check_devtest_orchestrator.py` with a third full-scan leg covering `submit.py` (per RESEARCH §SAFE-03 Orchestrator Checker recommendation — `submit.py` is not yet in the scan set, though it is clean against all three deny buckets by construction).
- No blockers.

---
*Phase: 113-submission-flow*
*Completed: 2026-07-03*

## Self-Check: PASSED

- FOUND: firestarter_app/firestarter/submit.py
- FOUND: firestarter_app/tests/test_submit.py
- FOUND: .planning/phases/113-submission-flow/113-03-SUMMARY.md
- FOUND commit: 1e497a5 (Task 1)
- FOUND commit: f2f925d (Task 2)
