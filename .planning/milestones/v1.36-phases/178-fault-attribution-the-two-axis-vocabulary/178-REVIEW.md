---
phase: 178-fault-attribution-the-two-axis-vocabulary
reviewed: 2026-09-06T00:00:00Z
depth: standard
files_reviewed: 13
files_reviewed_list:
  - firestarter_app/firestarter/chip_test.py
  - firestarter_app/firestarter/cli_handlers.py
  - firestarter_app/firestarter/diagnostic_report.py
  - firestarter_app/firestarter/submit.py
  - firestarter_app/tests/fixtures/report_shapes.py
  - firestarter_app/tests/fixtures/reports/attr01-status-axis-transport-fault.json
  - firestarter_app/tests/fixtures/shape_ids.json
  - firestarter_app/tests/test_blast_radius_invariance.py
  - firestarter_app/tests/test_chip_test.py
  - firestarter_app/tests/test_chip_test_sdp_leg.py
  - firestarter_app/tests/test_dev_test_cmd.py
  - firestarter_app/tests/test_diagnostic_report.py
  - firestarter_app/tests/test_submit.py
findings:
  critical: 0
  warning: 1
  info: 1
  total: 2
status: issues_found
resolution: both findings fixed in firestarter_app@835baba (orchestrator, code_review_gate)
---

# Phase 178: Code Review Report

**Reviewed:** 2026-09-06T00:00:00Z
**Depth:** standard
**Files Reviewed:** 13
**Status:** issues_found

## Summary

Reviewed the actual phase diff (`0a29d8b9..HEAD` in the `firestarter_app` submodule,
commits `ec1db5c`, `7a2f2a6`, `8867e60`, `c753b47`, `43e7a8a`), not just the full
files. The diff is small, tightly scoped, and unusually well cross-checked against
its own stated design decisions (`178-CONTEXT.md` D-01..D-16):

- `StepResult.status` / `STATUS_COMPLETE|ERROR|SKIP` added beside the existing
  `VERDICT_*` axis; the `(SerialError, HardwareOperationError)` arm is re-pointed
  from `verdict=BAD` to `verdict=SKIPPED, status=STATUS_ERROR` (D-01).
- Exactly three consumers are widened to read the new axis ahead of the verdict
  fold, matching D-04 verbatim: `submit.overall_verdict` (title), `build_db_diff`'s
  ladder guard, and `cli_handlers._dev_test_exit_code` (exit-code floor).
- `dedup_fingerprint` excludes `status` by construction (no `parts.append` for
  it) and this is proven by four separate positive/negative/ordering/empty-list
  tests in `test_diagnostic_report.py` — the "status must stay out of the dedup
  hash" invariant holds and is unusually well guarded against regression.
- No sixth `VERDICT_*` value is introduced anywhere in the diff.
- The frozen fixture `attr01-status-axis-transport-fault` (hash `93cef8030c40`)
  is correctly registered across `report_shapes.py`, `shape_ids.json`,
  `FROZEN_HASHES`, `LADDER_PINS`, `_PINNED_SHAPE_ID_SET`, and the committed
  snapshot JSON, all of which I cross-checked and found consistent.
- Ran the full touched-test-file set locally (`test_chip_test.py`,
  `test_chip_test_sdp_leg.py`, `test_diagnostic_report.py`, `test_submit.py`,
  `test_dev_test_cmd.py`, `test_blast_radius_invariance.py`) — all green.

I initially flagged the console `render()` table's silent omission of any
transport/tool-fault indication as a functional regression, but `178-CONTEXT.md`
D-04 explicitly scopes the status-axis wiring to exactly three consumers and
deliberately excludes `render()` — that is a recorded design decision, not an
oversight, so it is not filed as a finding. What I *did* find, immediately
adjacent to that same decision, is a comment inside `render()` whose factual
claim this phase's own change falsifies (see WR-01 below) — that is a genuine,
narrowly-scoped defect independent of the D-04 scoping decision.

## Warnings

### WR-01: `render()`'s "no nonzero-exit cause can hide here" comment is now false

**File:** `firestarter_app/firestarter/diagnostic_report.py:974-978`

**Issue:** The step-row filter in `DiagnosticReport.render()` carries this
comment (unchanged by this phase's diff):

```python
# Safe to hide: `NA` and `SKIPPED` both map to exit code 0
# (`cli_handlers._VERDICT_EXIT_CODES`), so no nonzero-exit cause can
# hide here. The one non-verdict exit term, the not-run SDP
# oracle floor, stays legible in the `sdp_hold_state` row above.
```

This asserted invariant was true before this phase: `_dev_test_exit_code`'s
*only* non-verdict exit-code term was `sdp_oracle_not_run`, which the comment
correctly notes stays visible via the `sdp_hold_state` row. This phase adds a
**second** non-verdict term, `run_status_error` (`cli_handlers.py:2162-2163`,
`codes.add(2)`), which is set whenever `run_status(results) == STATUS_ERROR`
— i.e. whenever any step carries `status=STATUS_ERROR`. A step that errors via
the `(SerialError, HardwareOperationError)` arm gets `verdict=VERDICT_SKIPPED`
(chip_test.py's re-pointed exception handler), and `render()`'s own filter two
lines below the comment (`if step_row["verdict"] not in _RAN_VERDICTS: continue`)
drops every `SKIPPED` row from the table. There is no other row anywhere in
`render()` that surfaces `run_status`/`STATUS_ERROR` (grepped: `run_status` only
appears in `to_dict()`, never read inside `render()`).

So the comment's factual claim is now false: a nonzero-exit cause (exit 2 via
`run_status_error`) *does* hide in this table — silently, in a row that simply
disappears, with no `sdp_hold_state`-style substitute row to keep it legible.
This is not a request to re-litigate the D-04 scoping decision (which
deliberately limits status-axis consumers to three and does not include
`render()`); it is a request to fix a comment that misstates the current
invariant it documents, which risks misleading a future maintainer reasoning
about exit-code/console consistency the same way this comment's author
originally reasoned about `sdp_oracle_not_run`.

**Fix:** Narrow the comment's claim to what is still true, e.g.:

```python
# Safe to hide: `NA` always maps to exit code 0. `SKIPPED` does NOT always --
# since Phase 178, a transport/tool-fault step (verdict=SKIPPED,
# status=STATUS_ERROR) can drive the exit code to 2 via
# `_dev_test_exit_code`'s `run_status_error` term, and that status is not
# otherwise surfaced anywhere in this table. The `sdp_oracle_not_run` term
# stays legible via the `sdp_hold_state` row above; `run_status_error` has
# no equivalent row here today (visible only in `to_dict()["run_status"]`,
# the saved JSON/markdown, and the exit code itself).
```
(or, if a rendered row is wanted, add one gated on `d["run_status"] ==
STATUS_ERROR`, mirroring how `sdp_hold_state` is surfaced — but that is a
scope question for the operator/roadmap, not something this review prescribes.)

## Info

### IN-01: Stale line-number citation in the new `STATUS_*` docstring

**File:** `firestarter_app/firestarter/chip_test.py:947` and `:1097`

**Issue:** Both new docstrings (the `STATUS_*` vocabulary block and
`StepResult.status`'s field docstring) cite `diagnostic_report.py:364` as "the
one colliding read site" for the database's own `support_status` field. Line
364 in the current file is `def build_db_diff(...):`'s signature line, not the
actual `support_status` read site, which is at `diagnostic_report.py:378`
(`current = (raw_config or {}).get("support_status", "supported")`). The
citation points at the right function but the wrong line inside it — a minor
inaccuracy, but this project's own history (`.planning/` note on repairing
`file:LINE` citations) treats stale line pointers as a recurring, worth-fixing
class of defect.

**Fix:** Update both citations to `diagnostic_report.py:378`, or drop the line
number and cite the function name only (`build_db_diff`) so future edits to
that function's docstring don't re-drift the pointer.

---

_Reviewed: 2026-09-06T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
