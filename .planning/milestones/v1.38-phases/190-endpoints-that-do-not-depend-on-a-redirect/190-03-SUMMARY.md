---
phase: 190-endpoints-that-do-not-depend-on-a-redirect
plan: 03
subsystem: firmware-release-management
tags: [click, requests, github-releases-api, pytest]

requires:
  - phase: 190-01
    provides: "The three FIRESTARTER_*_URL constants addressing henols/firestarter_fw, and the file this plan edits in the same module"
provides:
  - "manage_firmware_update returns False and emits one named message when a release cannot be resolved and a board has been identified, instead of the prior silent True"
  - "_endpoint_for_channel(channel, version), a module-level helper mapping stable/pre/pinned to the endpoint constant actually addressed"
  - "The double-emit hazard is proven closed on BOTH --install and --force, not only --force as D-08's wording named"
affects: [190-04]

actuals:
  tokens: 1770
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "A guard placed immediately before a method's final fall-through return, relying on the structural fact that every branch inside the enclosing `if should_install_now:` block returns, rather than adding a flag condition that could drift out of step with that fact"
    - "Asserting an ERROR-level record COUNT (== 1) rather than presence, to make a double-emission regression visible to a test"

key-files:
  created:
    - firestarter_app/tests/test_fw_update_dead_endpoint.py
  modified:
    - firestarter_app/firestarter/firmware.py

key-decisions:
  - "Followed RESEARCH Finding 2/3 over CONTEXT's literal wording: the guard's placement (immediately before the final `return True`, no flag condition) is structurally unreachable from both --install and --force, not only --force, because every branch inside `if should_install_now:` returns and both flags set that flag True. Both flag combinations are tested, not only the one CONTEXT named."
  - "The new message's endpoint is resolved through a dedicated helper (`_endpoint_for_channel`) rather than inlined, because the channel actually addressed differs across stable/pre/pinned and a hardcoded string would be wrong on two of the three."
  - "Kept `fetch_release_info` / `fetch_latest_release_info`'s (None, None) contract untouched (D-07) — no typed exception, no third return value. The guard reads only the two values already returned."
  - "Test module docstring carries the rationale (why two stubs are required, why record-count not presence, the reachability check and its observed counts) without citing plan/phase/decision identifiers, per the project's non-overridable no-comments-in-source rule — this diverges from 190-01's test module, which did cite them in its docstring; this plan's docstrings avoid that citation style instead of extending it."

patterns-established:
  - "_endpoint_for_channel(channel, version) -> str: the single place that maps a release channel to the constant it actually resolves through; any future message naming 'the endpoint' should call this rather than re-deriving it."

requirements-completed: [URL-04]

coverage:
  - id: D1
    description: "A plain fw version check against an unresolvable release returns False and logs exactly one ERROR record naming the board and an endpoint URL containing henols/firestarter_fw, and the message does not contain the already-up-to-date wording"
    requirement: "URL-04"
    verification:
      - kind: unit
        ref: "tests/test_fw_update_dead_endpoint.py#test_bare_check_with_unresolvable_release_returns_false_and_names_endpoint"
        status: pass
    human_judgment: false
  - id: D2
    description: "--install and --force each still emit exactly one ERROR record on an unresolvable release (the pre-existing install-time guard fires; the new guard is structurally unreachable from either), proving the double-emit hazard closed on both paths, not only --force"
    requirement: "URL-04"
    verification:
      - kind: unit
        ref: "tests/test_fw_update_dead_endpoint.py#test_install_flag_with_unresolvable_release_emits_exactly_one_error"
        status: pass
      - kind: unit
        ref: "tests/test_fw_update_dead_endpoint.py#test_force_flag_with_unresolvable_release_emits_exactly_one_error"
        status: pass
    human_judgment: false
  - id: D3
    description: "The already-up-to-date path (resolvable release, equal version, no flags) is unchanged: still returns True and emits no ERROR record"
    requirement: "URL-04"
    verification:
      - kind: unit
        ref: "tests/test_fw_update_dead_endpoint.py#test_already_up_to_date_path_still_returns_true_with_no_error"
        status: pass
      - kind: unit
        ref: "tests/test_fw_update_path_gate.py, tests/test_fw_port_targeting_and_blind_install.py, tests/test_py32_dfu.py (all pass unedited, run post-change)"
        status: pass
    human_judgment: false
  - id: D4
    description: "The pinned channel's failure message names the by-tag endpoint with the requested tag rendered into it, not the stable endpoint — proving the message is not a hardcoded string"
    requirement: "URL-04"
    verification:
      - kind: unit
        ref: "tests/test_fw_update_dead_endpoint.py#test_pinned_channel_names_the_by_tag_endpoint_with_the_requested_tag"
        status: pass
      - kind: unit
        ref: "tests/test_fw_update_dead_endpoint.py#test_pinned_channel_message_differs_from_the_stable_endpoint"
        status: pass
    human_judgment: false
  - id: D5
    description: "No comment was added to firmware.py by this plan's edit, and the guard does not name force_install or install_flag (source-swept, not merely reviewed)"
    verification:
      - kind: other
        ref: "git diff HEAD~1 HEAD -- firestarter/firmware.py | grep -c '^+[[:space:]]*#' (prints 0)"
        status: pass
      - kind: other
        ref: "git diff HEAD~1 HEAD -- firestarter/firmware.py | grep -cE '^\\+.*(force_install|install_flag)' (prints 0)"
        status: pass
    human_judgment: false
  - id: D6
    description: "Full firestarter_app test suite green on Python 3.11, and mypy's error count unchanged against the measured 33-error baseline (not a CI gate, recorded as a quality signal only)"
    verification:
      - kind: unit
        ref: "pytest tests/ -o addopts= -q -> 2145 passed"
        status: pass
      - kind: other
        ref: "mypy firestarter/ tests/ -> Found 33 errors in 13 files (matches measured baseline, no new errors)"
        status: pass
    human_judgment: false

duration: ~35min
completed: 2026-09-13
status: complete
---

# Phase 190 Plan 03: Update-Path Fall-Through Guard Summary

**`fw`'s plain version check no longer reports success after checking nothing: an unresolvable release now returns exit 1 with one message naming both the board and the actual endpoint addressed, and the guard is proven structurally incapable of double-emitting on either `--install` or `--force`.**

## Performance

- **Duration:** ~35 min
- **Completed:** 2026-09-13T17:33:27Z
- **Tasks:** 2 (Task 1 auto, Task 2 TDD test module)
- **Files modified:** 1 modified (`firmware.py`), 1 created (`test_fw_update_dead_endpoint.py`)

## Accomplishments

- Added `_endpoint_for_channel(channel, version)`, a module-level helper in `firmware.py` mapping the three release channels to the endpoint constant each actually resolves through: `FIRESTARTER_RELEASES_URL` for `"pre"`, `FIRESTARTER_RELEASE_BY_TAG_URL.format(tag=version)` for `"pinned"` with a version, and `FIRESTARTER_RELEASE_URL` otherwise (both `"stable"` and the safe default).
- Added a guard immediately before `manage_firmware_update`'s final `return True`: when `not latest_version or not download_url`, logs one `ERROR` naming the board and the resolved endpoint, then returns `False`. The condition mirrors the pre-existing install-time guard's condition exactly.
- Proved, per RESEARCH Finding 2, that D-08's premise (only `--force` reaches the hazard) is incomplete: `--install` reaches the SAME pre-existing install-time guard by the same route, because `elif install_flag:` tests `not is_up_to_date`, which is `True` when `latest_version` is `None`. Both flag combinations are tested here, not only the one CONTEXT named.
- The new guard names neither `force_install` nor `install_flag`, per RESEARCH Finding 3: it sits below the `if should_install_now:` block, and every branch inside that block returns, so the guard is unreachable whenever either flag set that variable `True`. This was checked, not merely reasoned about: removing the guard's four lines and re-running the new test module failed exactly the 3 tests whose assertions depend on the removed guard (bare-check, pinned-channel, pinned-channel-differs), leaving the `--install`/`--force`/up-to-date tests green — restoring the guard returned the module to 6/6.
- Added `tests/test_fw_update_dead_endpoint.py`: 6 tests covering the previously-uncovered fall-through branch — bare-check unresolvable (returns `False`, exactly one `ERROR`, message names board + `henols/firestarter_fw` endpoint, does not contain "already up to date"), `--install` unresolvable (exactly one `ERROR`), `--force` unresolvable (exactly one `ERROR`), the up-to-date path (still `True`, zero `ERROR` records), and two pinned-channel tests (the by-tag endpoint with the requested tag rendered in, and that the message does not name the stable endpoint).
- Ran the full `firestarter_app` test suite on Python 3.11: **2145 passed**, 1 pre-existing deprecation warning (Click `MultiCommand`), 32 snapshot tests passed — unrelated to this change.
- Ran `mypy firestarter/ tests/` as a quality signal (not a CI gate here): **33 errors in 13 files**, exactly matching the measured pre-existing baseline — no new errors introduced by this plan's edit.

## Task Commits

Both commits are in the `firestarter_app` submodule, on `v1.38-repository-rename`:

1. **Task 1: Guard the fall-through so an unresolvable release is a named failure, not a silent success** - `6f8ed57` (feat)
2. **Task 2: Cover the branch that was never covered, including the paths that must NOT change** - `560ec24` (test)

No meta-repo (`/workspaces`) commit is made by the plan's tasks — this `SUMMARY.md` is written to `.planning/` and committed separately per the phase's artifact-ownership split. The gitlink advance to these two commits is `190-04`'s job, not this plan's.

## Files Created/Modified

- `firestarter_app/firestarter/firmware.py` - added `_endpoint_for_channel` (module-level helper, sits beside `_asset_label`/`_pick_asset`) and the guard immediately before `manage_firmware_update`'s final `return True`
- `firestarter_app/tests/test_fw_update_dead_endpoint.py` (new) - 6 tests covering the fall-through guard, the no-double-emit proof on both flag combinations, the up-to-date non-regression, and the pinned-channel endpoint content

## Decisions Made

- The guard's placement (immediately before the final fall-through, no flag condition) is the entire proof of no-double-emission: every branch inside the enclosing `if should_install_now:` block returns, so the guard is unreachable whenever `should_install_now` was `True` — which both `--install` and `--force` set. A flag condition was deliberately NOT added; it would be redundant logic that could drift out of step with that structural property, per the plan's explicit prohibition.
- `_endpoint_for_channel` was added as a small standalone helper rather than inlining the three-way branch into the guard, because the same mapping is conceptually reusable and keeps the guard itself to a single `if`/`logger.error`/`return`.
- The message text follows the plan's suggested prose exactly (`"Could not resolve a firmware release for {board} from {endpoint}. The installed firmware version was not compared against any release."`), checked against the up-to-date branch's actual wording ("already up to date") to confirm the two are not merely different in source but distinguishable in the emitted string, per ROADMAP criterion 3.
- Followed the project's no-comments-in-source hard rule strictly: the new test module's docstring carries the rationale (why two stubs, why record-count not presence, the reachability check's observed numbers) but does not cite phase/plan/decision identifiers (no "Phase 190 Plan 03", no "D-06"), diverging from 190-01's test module which did include such a citation in its own docstring. This plan's docstrings do not extend that citation style; CLAUDE.md's hard rule takes precedence over following that precedent.

## Deviations from Plan

None - plan executed exactly as written, including satisfying D-08's intent beyond its literal wording per RESEARCH Finding 2/3 (both `--install` and `--force` proven no-double-emit, not only `--force`), which the plan itself instructed as the correct reading.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `_endpoint_for_channel` and the guard are available for `190-04`'s live end-to-end demonstration of both URL-04 failure modes (the `fw --list` half from `190-01` and this update-path half).
- The gitlink advance to commits `6f8ed57` and `560ec24` (plus `190-01`'s and `190-02`'s commits) is `190-04`'s job.
- No blockers. All verification legs in the plan ran clean; the full suite and mypy baseline were both confirmed on Python 3.11 via `.venv311`.

---
*Phase: 190-endpoints-that-do-not-depend-on-a-redirect*
*Completed: 2026-09-13*

## Self-Check: PASSED

- FOUND: `firestarter_app/firestarter/firmware.py`
- FOUND: `firestarter_app/tests/test_fw_update_dead_endpoint.py`
- FOUND: submodule commit `6f8ed57` (Task 1)
- FOUND: submodule commit `560ec24` (Task 2)
- FOUND: meta-repo commit `f6326f89` (SUMMARY)
