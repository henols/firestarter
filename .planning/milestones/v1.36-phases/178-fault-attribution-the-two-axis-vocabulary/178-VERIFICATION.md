---
phase: 178-fault-attribution-the-two-axis-vocabulary
verified: 2026-09-06T13:24:51Z
status: passed
score: 5/5 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 178: Fault Attribution — The Two-Axis Vocabulary Verification Report

**Phase Goal:** A run that failed to execute validly — a half-seated cable, a transport fault —
stops being reported as a verdict on the chip, and the tool never spends a chip's `BAD` on a fault
that was never the chip's.

**Verified:** 2026-09-06T13:24:51Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

All verification below was performed by reading the actual submodule source at HEAD
(`firestarter_app` commits `ec1db5c..835baba`, base `0a29d8b9`) and by independently re-running code
against a live Python 3.11 interpreter — not by reading SUMMARY.md prose or trusting the phase's own
evidence transcripts. Where the phase's evidence transcripts exist, I additionally cross-checked
their claims against a fresh, independently-run reproduction.

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | A run whose transport failed to execute validly reports a status-axis value distinct from the chip-verdict axis, and that step does not carry a `BAD` chip verdict | ✓ VERIFIED | Independently reproduced the tracer: `chip_test.py:2567` re-points `(SerialError, HardwareOperationError)` to `StepResult(verdict=VERDICT_SKIPPED, status=STATUS_ERROR, ...)`, constructed directly (not via `_skip_result`, confirmed by AST test `test_the_transport_arm_does_not_route_through_skip_result`). Live run against `sst27sf512` with `check_eprom_id.side_effect=SerialError(...)` produced `verdict=SKIPPED, status=ERROR`, never `BAD`. `_id_step_closes_gate` (byte-identical predicate, still reads `VERDICT_BAD, VERDICT_SKIPPED` with no `status`/`STATUS_` term) returned `True`; `op.sdp_lock.call_count == 0` — the destructive gate stays closed. |
| 2 | The overall verdict and the auto-generated issue title for such a run do not read `[dev test] <chip> — FAIL`; they reflect the status-axis outcome instead | ✓ VERIFIED | Live run: `submit.build_title(...)` returned `"[dev test] sst27sf512 — INCONCLUSIVE (harness) (c7d5d02611cb)"`. `submit.overall_verdict` guards on `getattr(r, "status", STATUS_COMPLETE) == STATUS_ERROR` *ahead* of the `BAD` check (`submit.py:150-165`), returning `_TITLE_VERDICT_HARNESS = "INCONCLUSIVE (harness)"`. `devtest_issues.py`'s `TITLE_RE` still captures the bare token `INCONCLUSIVE`; test `test_build_title_for_a_transport_fault_is_not_fail` applies that exact regex and asserts the captured group. |
| 3 | The status-axis value is additive and excluded from `dedup_fingerprint`, confirmed by Phase 174's oracle reporting zero unexpected hash changes, and no sixth `verdict` value is introduced | ✓ VERIFIED | `dedup_fingerprint`'s `parts.append` (3 call sites, confirmed via `inspect.getsource`) only reads `f"{result.op}={result.verdict}:{cls}"` plus two optional tags — never `result.status`. **Non-vacuity independently confirmed**: `test_status_axis_does_not_perturb_dedup_fingerprint` (Leg B — equal hash across identical verdicts, differing only in status) is paired with its anti-vacuity sibling `test_a_verdict_change_still_perturbs_dedup_fingerprint` (different hash when verdict changes, status held equal) — both present, both green, and structurally distinct (I read both bodies directly; neither varies the other's held-constant dimension). Phase 174's oracle (`tools/snapshot_report_shapes.py --check`) reports 18/18 matching after registering `attr01-status-axis-transport-fault` (a real transport-fault shape, hash `93cef8030c40`), and all 17 inherited hashes are unmoved. `VERDICT_*` still has exactly 5 members (`OK`, `BAD`, `NA`, `SKIPPED`, `marginal`) — grepped directly, no sixth value exists. |
| 4 | A run with a genuine chip fault and a run with a transport-only fault both still offer the submit prompt; auto-classification changes the title and disposition only, never suppresses the offer | ✓ VERIFIED | `is_submittable`'s source (`diagnostic_report.py:227-239`) contains none of `status`/`run_status`/`STATUS_ERROR`/`run_valid` — read directly. `test_a_transport_faulted_report_still_reaches_the_confirm_prompt` calls `submit_report` twice on the same status-ERROR report with fresh `confirm_fn` mocks each time and asserts `assert_called_once()` both times (idempotency edge) — read directly, not merely collected. `build_db_diff`'s ERROR guard (`diagnostic_report.py:383-390`) only changes `proposed_disposition`/`ladder_state`, never touches submittability. |
| 5 | The report states in words that a rail-voltage reading does not prove socket continuity, and nothing this phase ships claims to detect a disconnected VPP jumper from that reading alone | ✓ VERIFIED | `_RAIL_READING_DISCLOSURE = "vpp/vpe readings measure the regulator rail only -- they do not show whether the eprom socket is connected (advisory)"` (`diagnostic_report.py:64-67`), exported as `to_dict()["rail_reading_disclosure"]` and rendered as its own console row (`table.add_row("rail reading", d["rail_reading_disclosure"])`, `diagnostic_report.py:1043`). Both surfaces independently asserted by test: `test_rail_reading_disclosure_is_exported_and_rendered` renders the actual `Table` object and asserts the disclosure string appears in the rendered cell text (not just the dict), and `test_rail_reading_disclosure_renders_when_no_rail_was_measured` proves it renders unconditionally when all four rail fields are `None`. `tools/check_diagnostic_report_claims.py` (14 forbidden-phrase patterns) passes: `PASS: ... 216 string literals checked, zero forbidden matches`. |

**Score:** 5/5 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_app/firestarter/chip_test.py` | `STATUS_*` vocabulary, `StepResult.status`, re-pointed exception arm, `run_status()` fold | ✓ VERIFIED | All present at HEAD; read directly (lines 952-954, 1124, 2049-2065, 2567-2574). Exactly 5 `VERDICT_*` constants remain. |
| `firestarter_app/firestarter/diagnostic_report.py` | `SCHEMA_VERSION="1.8"`, `run_status` field/export, `status` step key, `build_db_diff` ERROR guard, `_RAIL_READING_DISCLOSURE` | ✓ VERIFIED | All present and wired into `to_dict()` (line 905-906) and `render()` (line 1043). |
| `firestarter_app/firestarter/submit.py` | `_TITLE_VERDICT_HARNESS`, status-first guard in `overall_verdict` | ✓ VERIFIED | Present at lines 138-165, guard ahead of `BAD` check as required. |
| `firestarter_app/firestarter/cli_handlers.py` | `report.run_status` assignment seam, `_dev_test_exit_code`'s `run_status_error` term | ✓ VERIFIED | `report.run_status = run_status(results)` (line 2462); `run_status_error=(report.run_status == STATUS_ERROR)` (line 2542); `codes.add(2)` composed into the precedence set, not a `max()`. |
| `firestarter_app/tests/fixtures/reports/attr01-status-axis-transport-fault.json` | Frozen snapshot pinning `status: ERROR`, `verdict: SKIPPED` | ✓ VERIFIED | Read directly: first step carries `"status": "ERROR"`, `"verdict": "SKIPPED"`. Registered in `_BUILDERS`, `SHAPE_IDS`, `FROZEN_HASHES` (`93cef8030c40`), `shape_ids.json`, and `LADDER_PINS`. Note: the shape's top-level `run_status` key reads `""` (empty), not `"ERROR"` — the builder constructs the `DiagnosticReport` directly via `_build_real_path_report` rather than through `cli_handlers.dev_test`'s assignment seam, so the run-level fold field is never populated on this fixture. This does not affect `dedup_fingerprint` (which reads neither field) or the real CLI path (verified live above), and the plan's own must-have language ("pins the exported key name `status` and the value `ERROR`") refers to the per-step key, which is correctly pinned. Flagged for completeness, not a gap. |
| `.planning/phases/.../evidence/*.txt` | Measured tracer, confirmation, non-change, and seal records | ✓ VERIFIED (cross-checked) | All 10 evidence files present; spot-checked claims (`legB_equal=True`, `stale_frozen=` empty, `mentions_run_status=False`, gate/hash/title/exit-code values) independently reproduced live rather than only read from the file. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `chip_test.py`'s `(SerialError, HardwareOperationError)` handler | `StepResult` | Direct construction, no `_skip_result` | ✓ WIRED | AST-walked directly: one matching `ExceptHandler`, one `StepResult` call, zero `_skip_result` calls inside it. |
| `chip_test.run_status` | `cli_handlers.dev_test` | `report.run_status = run_status(results)` | ✓ WIRED | Assignment present at call site beside `sdp_hold_state`'s sibling assignment. |
| `DiagnosticReport.run_status` | `cli_handlers._dev_test_exit_code` | `run_status_error=` keyword computed at call site | ✓ WIRED | `codes.add(2)` composed into the same precedence-candidate set as `sdp_oracle_not_run`; confirmed both `exit_error_only=2` and `exit_bad_and_error=1` (BAD dominates exit code while title still reads harness-inconclusive — the documented deliberate asymmetry). |
| `StepResult.status` | `diagnostic_report.dedup_fingerprint` | Deliberate absence of a `parts.append` line | ✓ WIRED (by exclusion) | Confirmed structurally (`parts_append_count=3`, `hash_reads_status=False`) and behaviorally (Leg B + anti-vacuity sibling, both read directly). |
| `_RAIL_READING_DISCLOSURE` | `render()` | `d["rail_reading_disclosure"]`, never recomputed | ✓ WIRED | Single-sourced through `to_dict()`, read off the dict at the render site as required by D-14. |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| ATTR-01 | 178-01 | Status axis separate from result axis | ✓ SATISFIED | `StepResult.status`, `run_status()` fold, both independently exercised. |
| ATTR-02 | 178-01 | Tool/transport failure not reported as chip verdict | ✓ SATISFIED | Transport arm re-pointed to `VERDICT_SKIPPED`; `EpromOperationError` arm (a genuine chip finding) untouched, confirmed by `test_the_transport_precedence_rows_carry_the_error_status`'s `EpromOperationError → status=COMPLETE` assertion. |
| ATTR-03 | 178-01/02 | Overall verdict/title reflect status axis | ✓ SATISFIED | Live-reproduced title and `overall_verdict` output. |
| ATTR-04 | 178-01/02/03 | Additive, excluded from dedup hash, no sixth verdict | ✓ SATISFIED | Structural + behavioral (Leg A + Leg B + anti-vacuity) proof, all independently read. |
| ATTR-05 | 178-02 | Submit prompt never suppressed | ✓ SATISFIED | `is_submittable` unchanged; `confirm_fn` fires twice on repeated calls. |
| ATTR-06 | 178-04 | Rail-reading disclosure, in words, both surfaces | ✓ SATISFIED | Rendered-table and exported-dict assertions both read directly; forbidden-claims gate green. |

All six requirements are marked `Complete` in `.planning/REQUIREMENTS.md` (lines 166-171) with Phase 178 named, and each is backed by a specific artifact verified above — none was flipped without evidence. RIG-01 remains correctly `Deferred` (line 127) and is not re-opened by this phase, matching the phase's own prohibition.

### Anti-Patterns Found

None. Scanned the full `0a29d8b9..HEAD` diff across `firestarter/` and `tests/` for `TBD|FIXME|XXX|TODO|HACK|PLACEHOLDER` — zero matches. `git -C /workspaces/firestarter status --porcelain` is empty (no firmware submodule touched). Zero `#` comments added to source (the phase's own standing "no comments" rule); rationale is carried in docstrings and bare-string-literal expression statements as designed.

### Behavioral Spot-Checks / Independent Reproduction

| Behavior | Command | Result | Status |
|---|---|---|---|
| Transport fault tracer, live | Constructed a `SerialError`-raising operator, ran `derive_plan`/`run_plan` against the real `sst27sf512` DB entry | `verdict=SKIPPED status=ERROR reason=True gate_closes=True sdp_lock_calls=0 title=[...INCONCLUSIVE (harness)...] exit=2 ladder=('', True)` | ✓ PASS |
| Targeted test suite (8 touched modules) | `pytest tests/test_dev_test_cmd.py tests/test_chip_test_sdp_leg.py tests/test_blast_radius_invariance.py tests/test_rekey_ledger.py tests/test_submit.py tests/test_diagnostic_report.py tests/test_chip_test.py tests/test_op_registration_parity.py -o addopts=""` | `620 passed` | ✓ PASS |
| Snapshot oracle | `tools/snapshot_report_shapes.py --check` | `OK: 18 snapshot(s) ... match a fresh regeneration` | ✓ PASS |
| Rekey ledger | `tools/rekey/check_rekey_ledger.py` | `OK: 8 ledger row(s), 8 MILESTONES.md row(s) bound` | ✓ PASS |
| Diagnostic-claims gate | `tools/check_diagnostic_report_claims.py` | `PASS: ... zero forbidden matches` | ✓ PASS |
| Orchestrator gate | `tools/check_devtest_orchestrator.py` | `PASS: ... firmware untouched (host-only, asserted)` | ✓ PASS |
| Lint/format/mypy | `ruff check`, `ruff format --check`, `check_mypy_watermark.py` | all clean, `mypy errors: 35 (watermark: 35)` | ✓ PASS |
| Rail-disclosure rendering | `test_rail_reading_disclosure_is_exported_and_rendered`, `..._renders_when_no_rail_was_measured` (read source directly) | Both assert the sentence in the *rendered* `Table` cell text, not only the dict | ✓ PASS |

### Code Review Follow-Through

The phase's own code review (178-REVIEW.md) flagged one warning (WR-01: a now-false comment in `render()` claiming no nonzero-exit cause can hide in the step table — falsified by this phase's own `run_status_error` term driving exit 2 while the `SKIPPED` row is filtered out) and one info item (stale line-number citation). Both were fixed in commit `835baba`, which I read directly: the false comment was deleted (not rewritten into a new false claim) and the citation corrected from `:364` to `:378`. This is a comment-accuracy fix, not a functional change — it does not affect any of the five success criteria, none of which requires console-table surfacing of the status axis (D-04 deliberately scopes status-axis consumers to exactly three: title, ladder, exit code).

### Human Verification Required

None. All five success criteria are independently reproducible from static analysis, direct source reading, and live code execution — no visual, real-time, or external-service behavior is in scope for this phase.

### Gaps Summary

No gaps. All five ROADMAP success criteria are verified against the actual codebase at
`firestarter_app@835baba`, independently reproduced (not merely re-reading the phase's own evidence
transcripts), all six ATTR requirements are satisfied with named artifacts, the anti-vacuity proof
required for criterion 3 is present and structurally distinct from its positive twin, and the
adjacent code-review defect was fixed before this phase closed. The phase goal — a transport fault no
longer spends a chip's `BAD` — holds.

---

_Verified: 2026-09-06T13:24:51Z_
_Verifier: Claude (gsd-verifier)_
