---
phase: quick-260822-gxx
plan: 01
subsystem: testing
tags: [dev-test, submit, cli, markdown-rendering, sdp]

# Dependency graph
requires:
  - phase: quick-260822-aq6
    provides: "dev test run_count disclosure + --fast; the Runs/Took column pattern this plan extends with a Reason column change"
provides:
  - "submit._reason_text — single shared formatter suppressing the Reason cell on any NA-verdict step row"
  - "build_body (filed GitHub issue body) wired to _reason_text"
  - "cli_handlers.py's dev_test .md-artifact writer wired to the same _reason_text via a submit_-prefixed aliased import"
  - "chip_test.sdp_hold_state() (follow-on) — returns bare HELD / NOT-HELD / NOT-RUN; the NOT-RUN reason suffix is gone, so no dev test surface reports a reason for a non-running SDP oracle"
  - "DiagnosticReport._step_dict() (delta, operator reversal of this plan's own D-2) — an NA-verdict step's exported \"reason\" is now \"\" in every export surface (the saved .json, and the fenced JSON block inside both the saved .md and a filed issue body), not just the render layer"
affects: [dev-test, submit, sdp-capability-reporting, diagnostic-report]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Single-source render formatter imported by both call sites (submit.py owns it, cli_handlers.py aliases it as submit_reason_text) so the filed issue body and the saved .md artifact can never disagree on how an NA reason renders."

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/submit.py
    - firestarter_app/firestarter/cli_handlers.py
    - firestarter_app/tests/test_submit.py
    - firestarter_app/tests/test_dev_test_cmd.py
    - firestarter_app/firestarter/diagnostic_report.py  # delta only (D-2 reversal)

key-decisions:
  - "Suppression keyed strictly on verdict == VERDICT_NA (imported from chip_test), never on message text or a per-op special case (D-1, operator ruling: 'NA is enough')."
  - "SKIPPED rows are exempt — a SKIPPED reason is frequently the real disclosure (e.g. 'no target resolved') and must keep rendering."
  - "SUPERSEDED by the delta below: the plan originally shipped D-2 as render-layer-only (to_dict()/_step_dict() untouched, JSON retains every reason verbatim). The operator reversed this mid-run; see 'Delta: D-2 Reversal' section."
  - "FOLLOW-ON (branch quick-devtest-holdstate-bare, operator: 'strip'): chip_test.sdp_hold_state() now returns the BARE SDP_HOLD_NOT_RUN token. Stripped at the SOURCE rather than at to_dict(), because export-layer suppression would leave a value computed, carried on the dataclass and read by nothing (the console already truncated it via _state_cell) — dead weight a later reader restores as a bug. Both prose branches go, including the sdp_honesty.unreadable_state_caveat() fallback."
  - "DELTA (260822-gxx, same day, operator ruling 'Actually if a step is NA no reason shall never be reported in any place'): DiagnosticReport._step_dict() now exports \"\" for any NA-verdict step's reason. This is the ONE additional edit beyond the original plan's four files — diagnostic_report.py. derive_plan and sdp_capability.py remain untouched (the in-memory model still carries the full prose; only the exported/reporting dict is suppressed)."
  - "DELTA exemption — NOW RESOLVED by the follow-on below. It read: sdp_hold_state (a top-level field, not a step) is deliberately left carrying its full 'NOT-RUN: <reason>' prose, the operator's ruling being scoped to steps; it was the SOLE remaining place the suppressed reason text could still appear in a saved/filed artifact, and was surfaced to the operator separately. The operator's reply was one word: 'strip'. See 'Follow-on: sdp_hold_state stripped to bare NOT-RUN'."

patterns-established:
  - "New markdown-cell formatters go in submit.py and are imported (aliased submit_<name>) into cli_handlers.py's dev_test handler body, matching the existing _duration_text / _runs_text convention."

requirements-completed: []

coverage:
  - id: D1
    description: "An NA-verdict row's Reason cell renders '-' in the filed GitHub issue body table (submit.build_body), while the fenced JSON block in the same body still carries the full reason string."
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_submit.py#test_build_body_na_row_suppresses_reason_json_retains_it"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_submit.py#test_reason_text_verdict_keyed_suppression"
        status: pass
    human_judgment: false
  - id: D2
    description: "SUPERSEDED by the delta: originally, an NA-verdict row's Reason cell rendered '-' in the saved dev-test-<chip>.md table while the same file's fenced JSON block still carried the full reason string. Post-delta, the JSON half is ALSO suppressed to \"\" — proven end-to-end on the REFUSE fixture (_CHIP_NO_ID), with sdp_hold_state confirmed as the one deliberate exception."
    verification:
      - kind: integration
        ref: "firestarter_app/tests/test_dev_test_cmd.py#TestReportDestination::test_md_artifact_na_row_suppresses_reason_everywhere"
        status: pass
      - kind: integration
        ref: "firestarter_app/tests/test_dev_test_cmd.py#TestReportDestination::test_reason_wrong_protocol_absent_from_report_except_sdp_hold_state"
        status: pass
    human_judgment: false
  - id: D3
    description: "SKIPPED-verdict rows keep rendering their reason verbatim in both markdown tables (non-suppression proof)."
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_submit.py#test_reason_text_verdict_keyed_suppression[SKIPPED-no target resolved-no target resolved]"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_submit.py#test_build_body_na_row_suppresses_reason_json_retains_it"
        status: pass
    human_judgment: false
  - id: D4
    description: "SUPERSEDED identity-proof re-homing: the original D-2 JSON-retention guard (test_r4_refuse_chip_na_reason_matches_sdp_capability_identity, asserting the step's own exported reason matched sdp_capability() by identity) no longer holds, since that reason is now suppressed. The identity proof survives, re-homed onto sdp_hold_state (renamed test). derive_plan and sdp_capability.py stay untouched and green; diagnostic_report.py itself is NOT untouched anymore (delta edit to _step_dict() only) — chip_test.py and sdp_capability.py remain zero-diff."
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_dev_test_cmd.py#test_r4_refuse_chip_na_reason_suppressed_sdp_hold_state_keeps_identity"
        status: pass
      - kind: other
        ref: "git diff --name-only origin/beta...HEAD (firestarter_app) — chip_test.py, sdp_capability.py show zero diff; diagnostic_report.py shows a delta-only diff (_step_dict reason suppression)"
        status: pass
    human_judgment: false

duration: 45min
completed: 2026-08-22
status: complete
---

# Quick Task 260822-gxx: Suppress the Reason cell on NA-verdict rows Summary

**Added `submit._reason_text`, a single verdict-keyed formatter suppressing the Reason cell on any NA-verdict step row in both markdown tables; then, per an operator reversal the same day, extended suppression into `DiagnosticReport._step_dict()` itself so the reason is absent from every exported/reporting surface (not just rendered tables) — with `sdp_hold_state` left as the one deliberate, documented exception.**

## Performance

- **Duration:** ~30 min (original plan) + ~15 min (same-day delta)
- **Tasks:** 3 (all auto, tdd on Tasks 1-2) + 1 delta task
- **Files modified:** 5 total (`firestarter/submit.py`, `firestarter/cli_handlers.py`, `tests/test_submit.py`, `tests/test_dev_test_cmd.py`, `firestarter/diagnostic_report.py` [delta only])

## Accomplishments
- `submit._reason_text(verdict, reason)` — verdict-keyed Reason-cell formatter; `NA` always renders `-`, every other verdict (including `SKIPPED`) keeps the old `reason or "-"` contract.
- `submit.build_body` (the filed GitHub issue body) now calls `_reason_text` instead of the bare `step.get("reason") or "-"`.
- `cli_handlers.py`'s `dev_test` handler imports `_reason_text` as `submit_reason_text` (matching the existing `submit_duration_text` / `submit_runs_text` aliased-import pattern) and uses it to render the saved `dev-test-<chip>.md` table.
- 8 new/updated unit tests in `test_submit.py` (a 7-row parametrized `_reason_text` suite plus a `build_body` NA/SKIPPED/JSON-retention test) and 1 new end-to-end test in `test_dev_test_cmd.py` on the `_CHIP_NO_ID` REFUSE fixture.
- A filed W27C512-style report no longer repeats `sdp_capability.REASON_WRONG_PROTOCOL` six times down the Reason column — each `sdp-*` NA row now reads `-`, while the machine-readable JSON half is unaffected.

## Task Commits

1. **Task 1: Add the shared `_reason_text` formatter and wire `build_body`** - `2ce37ba` (feat)
2. **Task 2: Wire the saved `dev-test-<chip>.md` table to the same helper** - `91f6368` (feat)
3. **Task 3: Run the full gate set and commit inside the submodule** - no additional commit (verification-only task; the two commits above already carry all four intended files)
4. **Delta task (same day, operator reversal of D-2): suppress `_step_dict()`'s exported reason for NA steps** - `5fe007e` (fix)

All commits land in `firestarter_app` on branch `quick-devtest-na-reason`. Commits 1-3 were forked off `origin/beta` at `15b12f8`. The delta commit (`5fe007e`) lands on the same branch but was executed from a **relocated worktree**, `/workspaces/firestarter_app_gxx` (see "Delta: D-2 Reversal" below) — the branch, all prior commits (`2ce37ba`, `91f6368`), and the working tree state are identical to the original `/workspaces/firestarter_app` checkout at hand-off. The meta repo (`/workspaces`) received no source commit from either the original plan or the delta.

## Files Created/Modified
- `firestarter_app/firestarter/submit.py` - added `VERDICT_NA` import (with a comment restating why it doesn't breach the ORCHESTRATOR-ONLY/SAFE-02 invariant), `_reason_text()`, and wired `build_body` to it.
- `firestarter_app/firestarter/cli_handlers.py` - added a third aliased local import (`submit_reason_text`) inside `dev_test`, and replaced the bare `r.reason or '-'` with `submit_reason_text(r.verdict, r.reason)`.
- `firestarter_app/tests/test_submit.py` - added `test_reason_text_verdict_keyed_suppression` (7-row parametrized); the `build_body` NA/SKIPPED test was later renamed and inverted by the delta (see below).
- `firestarter_app/tests/test_dev_test_cmd.py` - added a `.md`-artifact NA-suppression test to `TestReportDestination`; renamed/inverted by the delta, plus one new end-to-end guard added by the delta (see below).
- **Delta only:** `firestarter_app/firestarter/diagnostic_report.py` - `_step_dict()` now exports `""` for any NA-verdict step's `reason` (was `result.reason` unconditionally); imports `VERDICT_NA` from `chip_test`.

## Decisions Made
- Followed all three locked decisions (D-1/D-2/D-3) exactly as specified in the original plan — no widening at plan-execution time. Suppression was keyed purely on `verdict == VERDICT_NA`; `SKIPPED` was exempt; `diagnostic_report.py` received zero edits at that point (the console never emits a Reason cell for an NA row in the first place, since `_RAN_VERDICTS` excludes `NA`).
- No new imports beyond the one `VERDICT_NA` import specified in the plan; kept the `submit_`-prefixed alias convention in `cli_handlers.py` per planning finding 4 (keeps `check_devtest_orchestrator.py`'s GATE-10 blast radius at zero).
- **Same-day delta:** the operator reversed the plan's own D-2 after execution ("Actually if a step is NA no reason shall never be reported in any place"). See "Delta: D-2 Reversal" section below for the full account.

## Deviations from Plan

None for the original plan's three tasks — executed exactly as written. No further verify-leg mechanics needed fixing beyond what the plan had already pre-fixed (the HTML-entity `&&` and false `grep -c` baseline issues it names were not re-encountered; all `<automated>` verify legs in this plan ran as written).

The delta itself is not a "deviation" in the Rule 1-4 sense — it is an explicit, deliberate operator instruction issued after the plan's own commits landed, reversing one of the plan's own locked decisions (D-2). It is documented in full below rather than folded into this section.

## Delta: D-2 Reversal (same day, post-plan)

**What changed and why.** After this plan's three tasks completed and committed (`2ce37ba`, `91f6368`), the operator reversed D-2 mid-run: *"Actually if a step is NA no reason shall never be reported in any place"* (double negative; intent: a step with verdict `NA` reports NO reason, anywhere — not just suppressed in the rendered markdown tables, which is all the original plan did).

**The fix.** `DiagnosticReport._step_dict()` (`firestarter/diagnostic_report.py`, ~line 782) previously emitted `"reason": result.reason` unconditionally for every step. It now emits `"reason": "" if result.verdict == VERDICT_NA else result.reason`. Because every export surface derives from this one dict's `to_dict()`, this single edit covers:
- the saved `~/.firestarter/reports/dev-test-<chip>.json`
- the fenced JSON block inside the saved `dev-test-<chip>.md`
- the fenced JSON block inside a filed GitHub issue body (via `submit.sanitize_dict`)

**Explicitly out of scope / untouched by the delta:**
- `Step.reason` / `StepResult.reason` (the in-memory model) keep the full prose — `chip_test.derive_plan` (LEG-02), `sdp_capability.py`, and every reason constant received zero edits. Only the exported/reporting layer changed.
- `submit.py`'s `_reason_text` and `build_body` received zero edits — `build_body` already receives an already-sanitized dict, and after the delta that dict's NA-step `reason` values arrive pre-suppressed to `""`, so `_reason_text`'s existing table-rendering behavior needs no change.
- `cli_handlers.py`'s saved-`.md` table loop reads `StepResult` attributes directly (not the dict), so `_reason_text` there is unaffected — it was already suppressing the table cell; the delta's contribution is entirely on the JSON side.

**Deliberate exception — `sdp_hold_state` (NOT suppressed).** `sdp_hold_state` is a top-level report field (not a step) that carries `f"{SDP_HOLD_NOT_RUN}: {reason}"`, derived in `chip_test.sdp_hold_state()` from the in-memory `write-inhibited` `StepResult.reason` — untouched by this delta. The operator's ruling was scoped to steps, so this field was deliberately left as-is. Consequence, discovered and proven by test during this delta: for a REFUSE chip (e.g. `M8720`/`_CHIP_NO_ID`), all six SDP-leg steps carry the IDENTICAL `sdp_capability()` reason (LEG-02); five of those six are now suppressed to `""` in the exported dict, but `sdp_hold_state` — derived from the sixth (`write-inhibited`) via the untouched in-memory path — still carries the full text. **This means the reason string is NOT literally absent from a REFUSE chip's saved artifact end-to-end; it survives in exactly one field.** This is surfaced here for the operator to review separately; it was not resolved as part of this delta (constraints explicitly forbade touching `sdp_hold_state`).

**Test inversions (all in `firestarter_app`, same commit `5fe007e`):**
1. `tests/test_dev_test_cmd.py::test_r4_refuse_chip_na_reason_matches_sdp_capability_identity` → renamed `test_r4_refuse_chip_na_reason_suppressed_sdp_hold_state_keeps_identity`. Flipped the step-level `reason == expected_reason` assertion to `reason == ""`; kept the identity proof alive by re-homing it onto the pre-existing `sdp_hold_state == f"{SDP_HOLD_NOT_RUN}: {expected_reason}"` assertion in the same test.
2. `tests/test_dev_test_cmd.py::test_md_artifact_na_row_suppresses_reason_json_retains_it` → renamed `test_md_artifact_na_row_suppresses_reason_everywhere`. The "JSON retains it" half is now the opposite: asserts the JSON half's `steps[]` entry has `reason == ""`, and separately asserts `sdp_hold_state` is the one place `expected_reason` still appears.
3. `tests/test_dev_test_cmd.py::TestAbsentChipHardFail::test_dev_test_present_but_unsupported_still_sweeps` — inverted only the `blank-check` NA-step reason assertion (`"0x0d" in reason.lower()` → `reason == ""`); left the sweep-behavior assertions (`read`/`write` SKIPPED with reasons intact) untouched, since those steps are not NA.
4. `tests/test_submit.py::test_build_body_na_row_suppresses_reason_json_retains_it` → renamed `test_build_body_na_row_reason_absent_everywhere_skipped_retains_it`. **Chose to update the fixture rather than route it through `_step_dict()`:** the hand-built `sanitized` dict now carries `reason: ""` on the NA step (matching what `_step_dict()` actually produces post-delta) rather than constructing a full `DiagnosticReport`/`StepResult` object graph just to call `_step_dict()` directly — `submit.build_body` itself received no code change in this delta, so the simpler fixture update is sufficient to prove its existing "empty reason renders `-`" contract still holds; routing through the real dataclass would have added test-only coupling to `diagnostic_report.py`'s internals for no additional proof value. The SKIPPED-row non-suppression assertion is unchanged.

**New non-vacuous guard added:** `tests/test_dev_test_cmd.py::TestReportDestination::test_reason_wrong_protocol_absent_from_report_except_sdp_hold_state` — for the REFUSE fixture `_CHIP_NO_ID`, asserts `sdp_capability.REASON_WRONG_PROTOCOL` is absent from the saved `.md`'s table half AND from every `steps[]` entry's `reason` in the JSON half, while confirming it as the sole exception, `sdp_hold_state` DOES still carry it (the documented, deliberate carve-out) and `sdp_capability()` itself is unchanged and still returns the string live.

**Worktree relocation.** The delta was originally attempted from `/workspaces/firestarter_app` but a prior executor run correctly STOPPED because a concurrent session had taken over that checkout (branch `debug-w27c512-devtest-all-bad`, with its own uncommitted WIP in `chip_test.py`/`eprom_operations.py`). The delta was completed from a dedicated sibling git worktree, `/workspaces/firestarter_app_gxx`, checked out on the same `quick-devtest-na-reason` branch with both prior task commits (`2ce37ba`, `91f6368`) present and a clean tree — a sibling of `/workspaces/firestarter/` exactly like `/workspaces/firestarter_app_py32`, so the sibling-firmware-repo-scanning tests (`../firestarter`) resolve normally. The `debug-w27c512-devtest-all-bad` session in `/workspaces/firestarter_app` was never touched, read, or modified.

## Issues Encountered

- **Transient full-suite failures unrelated to this task's files.** The first full `pytest tests/ -o addopts="" -q` run (from Task 3's gate set) showed 6 failures, all in firmware/host parity-guard tests (`test_cap03_ack_layout_parity.py`, `test_json_key_parity.py`, `test_py32_asset_name_host.py`, `test_py32_flash_map_host.py`) that assert the **sibling firmware repo's working tree** (`/workspaces/firestarter`) is porcelain-clean. This environment runs concurrent sessions against the same non-worktree-isolated `firestarter_app` and `firestarter` checkouts (confirmed live: mid-execution, `firestarter_app`'s HEAD was briefly switched to a `debug-w27c512-erase-pulse` branch by another process, and `firestarter/chip_test.py` + `firestarter/eprom_operations.py` picked up uncommitted WIP not authored by this plan). Verified pre-existing and not caused by this plan's changes: the same 6 tests pass in isolation both before and after this plan's edits (confirmed against a `git worktree` checkout of the pre-plan commit `15b12f8`), and a full-suite rerun immediately after showed **1952 passed, 0 failed**. This plan's own 4 files show a clean, unchanged diff throughout (`git diff --stat -- firestarter/submit.py firestarter/cli_handlers.py tests/test_submit.py tests/test_dev_test_cmd.py` returns nothing after commit), and I switched `firestarter_app`'s branch back to `quick-devtest-na-reason` (a plain non-destructive `git checkout`, no reset/clean) without touching or committing the concurrent session's uncommitted files.
- No `deferred-items.md` entries needed: `ruff check .` (whole-repo) flags 4 pre-existing errors in `tools/catalog/codegen_vectors.py` and `ruff format --check .` flags 3 pre-existing reformat-needed files, both confirmed present at the pre-plan commit (`15b12f8`) via a `git show` diff, and entirely outside this plan's 4 files (`ruff check`/`ruff format --check` scoped to the 4 files pass clean). `mypy` over the strict-island list surfaces one pre-existing type error at `submit.py`'s `submit_via_gh` call site (unrelated code, unchanged by this plan, confirmed present at `15b12f8` via a scratch copy). All three are out of scope per the deviation-rules Scope Boundary and were left untouched, not fixed.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- This is a standalone quick task; no follow-on phase depends on it.
- A future `dev test --submit` run against any REFUSE-verdict chip (SDP-inapplicable protocols, `FLAG_CAN_ERASE`-absent chips, flash4 blank-check NA rows, etc.) will file a report whose Reason column reads `-` on every NA row, AND whose fenced JSON block's `steps[]` entries carry `reason: ""` for those same rows (post-delta) — except `sdp_hold_state`, which is the one field still carrying the full prose (see Delta section above; flagged for separate operator review).
- The pre-existing sibling-repo porcelain-guard test flakiness noted during the original plan's Task 3 (see Issues Encountered) did NOT reoccur during the delta: a full `pytest tests/ -o addopts="" -q` run from the relocated worktree passed **1953 passed, 1 warning** (0 failures) in one run, with the concurrent `/workspaces/firestarter_app` session (branch `debug-w27c512-devtest-all-bad`) never touched. No action taken, no ticket filed.
- **The `sdp_hold_state` exemption is a deliberate, documented residual, not a bug** — the operator's ruling was explicitly scoped to steps, and this quick task does not resolve whether `sdp_hold_state` should also be suppressed. That question is left open for the operator.

---
*Phase: quick-260822-gxx*
*Completed: 2026-08-22*

## Self-Check: PASSED

Original plan: all 4 modified files confirmed present on disk; both task commits (`2ce37ba`, `91f6368`) confirmed present in `firestarter_app`'s git history.

Delta (2026-08-22, executed from `/workspaces/firestarter_app_gxx`): `firestarter/diagnostic_report.py`, `tests/test_dev_test_cmd.py`, `tests/test_submit.py` confirmed present on disk; delta commit `5fe007e` and both prior commits (`2ce37ba`, `91f6368`) confirmed present in git history; `SUMMARY.md` confirmed present on disk.


## Follow-on: `sdp_hold_state` stripped to bare `NOT-RUN`

**Branch:** `quick-devtest-holdstate-bare` (forked off `firestarter_app` beta `134c29c`)
**Commit:** `e04c331` — merged to beta as `39b74ab`
**Operator instruction:** one word — *"strip"* — in reply to this SUMMARY's flagged exemption.

The delta above left `sdp_hold_state` carrying `NOT-RUN: <reason>`, so a REFUSE chip's
saved `.json`, the fenced JSON in the saved `.md`, and the filed issue body each still
carried the prose ONCE. That exemption is now closed.

**Seam chosen: the source (`chip_test.sdp_hold_state()`), not `to_dict()`.** Suppressing at
the export layer would have left a value that is computed, carried on the dataclass, and read
by nothing — the console already truncated it via `_state_cell`, and the JSON would have
dropped it. Dead data of that shape gets "restored" later as a bug, so the function no longer
produces it. Both prose branches were removed: the step's own `reason`, and the fixed
`sdp_honesty.unreadable_state_caveat()` fallback.

**Knock-ons handled:**
- `chip_test.py`'s `from firestarter import sdp_honesty` import became unused (ruff F401) and was removed with its trailing comment. `unreadable_state_caveat()` itself keeps three other callers and is NOT orphaned.
- `_state_cell()` retained as defensive for legacy/foreign colon-bearing input, but its docstring no longer claims `to_dict()` keeps the full string — that claim became false.
- `cli_handlers.py` untouched; the D-15 exit floor's `startswith(SDP_HOLD_NOT_RUN)` still fires on the bare token, now pinned by `TestExitFloorD15`'s four CLI-driven tests using exact equality.
- The `sdp_capability()` identity proof, which the delta had re-homed onto the `sdp_hold_state` assertion, was re-homed AGAIN onto a focused unit test in `tests/test_sdp_capability.py` — where a claim about `sdp_capability`'s output actually belongs.
- The end-to-end absence guard's `sdp_hold_state` carve-out was removed; it now asserts `REASON_WRONG_PROTOCOL` is absent from the ENTIRE saved `.md` and `.json`.

**Verified end-to-end (orchestrator, independent of the executor):** all four branches return
`HELD` / `NOT-HELD` / `NOT-RUN` / `NOT-RUN` correctly; a composed REFUSE-chip issue body
contains neither the full prose, nor `REASON_WRONG_PROTOCOL`, nor the substring `0x0D`;
`sdp_capability()` still returns the string live.

**Gates, on a Python 3.11 CI-parity venv (not the devcontainer's 3.12):** ruff 0.16.4 lint +
format clean; mypy watermark **35/35, zero new errors** (it had zero headroom);
`check_devtest_orchestrator.py` and `check_diagnostic_report_claims.py` both PASS;
**1964 passed**, 32 snapshots, 84.42% coverage.

**Flagged, not fixed (pre-existing, out of scope):** `sdp_honesty.py`'s module docstring
claims three production callers of `unreadable_state_caveat()` and names
`cli_handlers._sdp_recovery_line`, which quick task 260821-spg deleted. That paragraph was
already stale before this change; this change makes it one caller staler.
