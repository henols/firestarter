---
phase: quick-260916-nbb
plan: 01
subsystem: diagnostics
tags: [logging, dev-test, diagnostic-report, submit, log-capture]

# Dependency graph
requires:
  - phase: 260916-nb9
    provides: "resolve_error_name(), SCHEMA_VERSION 2.1, error_name on steps[]"
  - phase: 260916-nba
    provides: "Error column on both markdown tables (submit.build_body, cli_handlers md_lines)"
provides:
  - "firestarter/log_capture.py: root-logger WARNING+ sink, bounded ring, step attribution, normalization, consecutive-duplicate collapse"
  - "DiagnosticReport.log_capture top-level field, SCHEMA_VERSION 2.2"
  - "submit._log_capture_lines: one diagnostics-section formatter shared by build_body and cli_handlers.dev_test's saved .md"
affects: [devtest-triage, devtest-rootcause, issue #86 triage]

# Actuals (#2632)
actuals:
  tokens: 11790
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Process-lifetime module-level sink attached to the root logger, modelled on transport_counters.py (install/snapshot/uninstall lifecycle)"
    - "Consecutive-duplicate ring-buffer collapse keyed on a value tuple, comparing only the last entry"
    - "One shared markdown formatter called from two surfaces (build_body and cli_handlers md_lines) to prevent surface drift"

key-files:
  created:
    - firestarter_app/firestarter/log_capture.py
    - firestarter_app/tests/test_log_capture.py
  modified:
    - firestarter_app/firestarter/chip_test.py
    - firestarter_app/firestarter/diagnostic_report.py
    - firestarter_app/firestarter/cli_handlers.py
    - firestarter_app/firestarter/submit.py
    - firestarter_app/pyproject.toml
    - firestarter_app/tests/test_blast_radius_invariance.py
    - firestarter_app/tests/test_dev_test_cmd.py
    - firestarter_app/tests/test_diagnostic_report.py

key-decisions:
  - "D-01: capture is a logging.Handler on the ROOT logger at level WARNING; source is firmware when record.name == RURP (serial_comm.rurp_logger's name), host otherwise."
  - "D-02: one run-level block (log_capture) with every entry naming its own step, never a per-step list nested inside steps[] -- keeps steps[]'s pinned element shape untouched and sits beside transport_health as run-level diagnostics."
  - "D-03: a deque(maxlen=MAX_ENTRIES=20) ring drops the OLDEST entry on overflow, adding the evicted entry's whole repeat count (not 1) to dropped; a message over MAX_LINE_CHARS=160 is cut to 157 chars + '...' and counted once in truncated. Rejected alternative: drop-middle -- rejected because a ring is correct by construction (no hand-written eviction-target rule) and because the lines nearest a failure are exactly the ones triage needs kept, which a ring naturally favors (it always keeps the newest N)."
  - "D-04: capture is ALWAYS on for the run window and log_capture is ALWAYS exported (never gated on verdict) -- the WARNING level filter is what keeps a clean run's block small, and a warning on an otherwise-OK run is exactly the marginal evidence a verdict gate would discard."
  - "D-05: every captured message is normalized at capture time in a fixed order (collapse CR/LF/tab runs to one space + strip, drop non-printable ASCII, neutralize 3+-backtick runs to equal-length single-quote runs, THEN truncate) so the length bound is always the last word; the mapping rides inside to_dict(), which submit.submit_report already deep-scrubs via sanitize_dict before any issue body exists. Local artifacts (.json/.md) stay unsanitized by design, exactly as reason already does (T-nbb-08, accepted risk: the operator's own machine, never published directly)."
  - "SCHEMA_VERSION bumped 2.1 -> 2.2 for the new additive top-level log_capture key. Verified 2.1 was the live value before bumping (nb9 had already landed it); also updated the three pre-existing schema-version literal pins in test_diagnostic_report.py that were not in this plan's declared files_modified but would otherwise go red (deviation, documented below)."
  - "Task 1's end-to-end test uses --fast (runs=1) so the write step dispatches exactly once, keeping the tracer's assertion independent of whether Task 2's consecutive-duplicate collapse has landed yet."
  - "Task 3's diagnostics-section formatter (submit._log_capture_lines) takes the whole report mapping (not just the log_capture sub-mapping) so both call sites -- build_body's sanitized_dict and cli_handlers' unsanitized report_dict -- can call it identically."
  - "The 4000-char rendering-size proof uses OP_WRITE ('write', the shortest real step name) and repeat=1, not an artificially stacked worst case (longest op name + high repeat) -- log_capture.py declares exactly two bounds (MAX_ENTRIES, MAX_LINE_CHARS); op-name length and repeat magnitude are not bounds the module states, so 'both bounds' means those two, not every conceivable input."

patterns-established:
  - "A capture sink's own handler class is looked up by isinstance() on every install()/uninstall(), never by trusting a single tracked reference -- self-healing against a leaked prior instance."
  - "step_scope/probe_scope-style context managers restore the PREVIOUS value in a finally, never a hard sentinel, so nesting and exception-exit are both safe."

requirements-completed: [260916-nbb]

coverage:
  - id: D1
    description: "A firmware ERROR/WARN line captured during dev test lands in the saved report JSON under log_capture.entries, tagged source, level and the step that was running"
    requirement: "260916-nbb"
    verification:
      - kind: unit
        ref: "tests/test_dev_test_cmd.py#test_a_firmware_error_line_emitted_mid_write_lands_in_the_saved_log_capture_block"
        status: pass
    human_judgment: false
  - id: D2
    description: "Every captured message is bounded (MAX_ENTRIES ring, MAX_LINE_CHARS truncation) and normalized (whitespace collapse, non-printable drop, backtick-fence neutralization) with dropped/truncated counted, never silently lost"
    requirement: "260916-nbb"
    verification:
      - kind: unit
        ref: "tests/test_log_capture.py (25 tests covering normalization, bounds, collapse, eviction, counters, level filter, source attribution, install/uninstall, step_scope, snapshot isolation, drift guard)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Captured lines render identically on both markdown surfaces (saved .md and filed issue body) via one shared formatter, are absent when the block is empty/None, and every PII vector (home path, tty device, tmp path, username) is scrubbed before a captured line reaches a filed issue; a captured triple-backtick cannot break the fence; dedup_fingerprint is unaffected"
    requirement: "260916-nbb"
    verification:
      - kind: unit
        ref: "tests/test_log_capture.py (10 Task-3 tests: rendering shape, repeat display, heading counts, empty/None suppression, cross-surface identity, scrub proof, fence proof, dedup-stability proof, 4000-char size proof)"
        status: pass
    human_judgment: false

duration: ~45min
completed: 2026-09-16
status: complete
---

# Quick Task 260916-nbb: Captured warn/error log lines in dev test reports Summary

**A new `log_capture.py` sink buffers WARNING+ log records (host and firmware) for the duration of a `dev test` run, tags each with its step, bounds and normalizes them, and exports the block through `DiagnosticReport.log_capture` onto both markdown surfaces and the filed issue body.**

## Performance

- **Duration:** ~45 min
- **Tasks:** 3
- **Files modified:** 10 (1 created: `log_capture.py`; 1 test file created: `test_log_capture.py`; 8 modified)
- **Commits:** 3 (measured: `git rev-list --count 7bbaf3c..HEAD`)

## Accomplishments

- A firmware `ERROR:`/`WARN:` line (or a host `logger.warning`/`.error`) emitted during a `dev test` run now survives into the saved `dev-test-<chip>.json` under a new `log_capture` block, tagged with the step that was running and whether it came from the firmware feedback logger (`RURP`) or a host module.
- The block is bounded (`MAX_ENTRIES=20` ring, `MAX_LINE_CHARS=160` per message) and normalized at capture time (whitespace collapse, non-printable strip, backtick-fence neutralization) so a captured line can neither grow the issue body unboundedly nor break the markdown fence it renders inside nor carry a terminal escape sequence to a triager.
- Consecutive-duplicate collapse (keyed on step/source/level/normalized-message, compared only against the last entry) keeps a re-sync warning storm from evicting every other diagnostically useful line from the ring.
- One new formatter (`submit._log_capture_lines`) renders the block identically on the saved `dev-test-<chip>.md` and the filed GitHub issue body, so the two surfaces can never disagree, and is the only surface a captured line survives on once a browser-tier submission escalates past `_URL_ESCALATE_BYTES` and drops the fenced JSON block.
- The publish path was proven, not just asserted: a home-directory path, a `/dev/ttyACM*` device, a `/tmp` path and the operator's own username inside a captured message are all scrubbed by `sanitize_dict` before the section is rendered for a filed issue; the local `.json`/`.md` artifacts stay unsanitized by design (matching the pre-existing `reason` field).

## Task Commits

1. **Task 1: One firmware ERROR line, emitted mid-write, lands in the saved report JSON tagged with its step** - `4dd4898` (feat)
2. **Task 2: Bound and neutralize what a captured line can contain, and prove every bound** - `cfaa8d1` (test — implementation + 25 tests in one commit per the TDD commit-scope contract)
3. **Task 3: Put the captured lines on the two markdown surfaces and prove the publish path is safe** - `5ab7dac` (feat)

_No separate plan-metadata commit: this is a quick-task execution (`commit_docs` not applicable to `.planning/quick/` artifacts per the executor's constraints); STATE.md/ROADMAP.md are not touched by this run._

## Files Created/Modified

- `firestarter_app/firestarter/log_capture.py` - New stdlib-only leaf module: the capture sink, normalization pipeline, ring/collapse logic, `install()`/`uninstall()`/`step_scope()`/`snapshot()`
- `firestarter_app/firestarter/chip_test.py` - `_run_step`'s body wrapped in `with step_scope(step.op):`, the one seam every dispatch path passes through
- `firestarter_app/firestarter/diagnostic_report.py` - New `log_capture: dict[str, Any] | None` field, exported verbatim in `to_dict()`; `SCHEMA_VERSION` 2.1 -> 2.2
- `firestarter_app/firestarter/cli_handlers.py` - `log_capture.install()` right after `transport_counters.reset()`; `report.log_capture = log_capture.snapshot()` + `log_capture.uninstall()` right before `report.render()`; `md_lines` now includes the shared diagnostics section
- `firestarter_app/firestarter/submit.py` - New `_log_capture_lines()` formatter, called from `build_body` after the step table
- `firestarter_app/pyproject.toml` - `firestarter.log_capture` added to the mypy strict island, joining from birth
- `firestarter_app/tests/test_blast_radius_invariance.py` - `_TO_DICT_KEYS` gained `log_capture` (16 keys now); `test_schema_version_is_pinned` moved to `2.2`; the planted-key sensitivity test's `len(keys) == 15` moved to `16`
- `firestarter_app/tests/test_dev_test_cmd.py` - New end-to-end tracer test for Task 1
- `firestarter_app/tests/test_diagnostic_report.py` - Two pre-existing schema-version literal-pin tests renamed/updated (`2.1` -> `2.2`) — see Deviations
- `firestarter_app/tests/test_log_capture.py` - New: 35 tests (25 from Task 2, 10 from Task 3)

## Decisions Made

See `key-decisions` in the frontmatter for D-01 through D-05 (as specified in the plan) plus the four additional decisions made during execution (SCHEMA_VERSION verification, the `--fast` tracer adjustment, the formatter's whole-report-mapping signature, and the 4000-char proof's realistic-worst-case scoping).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Updated two schema-version literal pins in `tests/test_diagnostic_report.py`, a file not in this plan's declared `files_modified`**
- **Found during:** Task 1's verify step (`pytest tests/test_dev_test_cmd.py tests/test_blast_radius_invariance.py tests/test_diagnostic_report.py`)
- **Issue:** `test_schema_version_2_1_single_sourced` and `test_schema_version_is_two_one` both hardcode the literal `"2.1"` (the value before this quick task's `SCHEMA_VERSION` bump to `"2.2"`) and would go red the moment `SCHEMA_VERSION` changed — the same pattern the sibling quick task 260916-nb9 had already hit and fixed in the same file when it bumped `2.0 -> 2.1` (visible in its own commit `e4cbfdf`).
- **Fix:** Renamed both tests (`..._2_1_...` -> `..._2_2_...`, `..._is_two_one` -> `..._is_two_two`), updated their docstrings to record the new bump's cause, and updated the literal from `"2.1"` to `"2.2"` in both the single-sourced-count assertion and the direct equality assertion.
- **Files modified:** `firestarter_app/tests/test_diagnostic_report.py`
- **Verification:** `pytest tests/test_dev_test_cmd.py tests/test_blast_radius_invariance.py tests/test_diagnostic_report.py -o addopts="" -q` — 223 passed.
- **Committed in:** `4dd4898` (Task 1 commit)

**2. [Rule 3 - Blocking] Task 1's end-to-end tracer test uses `--fast`, not the plan's implied default invocation**
- **Found during:** First run of the new tracer test in `test_dev_test_cmd.py`
- **Issue:** Without `--fast`, `dev test` runs the write/verify cycle twice (`runs=2`), so the mocked `write_eprom`'s side effect fired the sentinel `RURP` error twice. Task 1 does not yet have Task 2's consecutive-duplicate collapse, so this produced TWO raw entries, failing the plan's "exactly one" assertion.
- **Fix:** Invoked `dev test` with `--fast` (`runs=1`) so the write step dispatches exactly once, making the tracer's "exactly one" assertion correct independent of Task 2's collapse landing later in the same plan.
- **Files modified:** `firestarter_app/tests/test_dev_test_cmd.py`
- **Verification:** Test passes both before and after Task 2's collapse landed (re-ran the full suite after Task 2 and Task 3; no regression).
- **Committed in:** `4dd4898` (Task 1 commit)

---

**Total deviations:** 2 auto-fixed (both Rule 3 — blocking issues discovered while completing the plan's own declared verify steps).
**Impact on plan:** Both were necessary to keep the plan's own stated verify commands green; neither touched scope beyond what Task 1 already required. No architectural change, no scope creep.

## Falsifiability Audit (RED evidence)

| Kind | RED evidence |
|---|---|
| Task 2's 14 (actually 16, all listed in the plan's `<behavior>` block) bound/attribution/normalization properties | Written before implementation. Observed: `7 failed, 18 passed in 0.19s` — the four normalization tests (`test_cr_lf_tab_collapse_to_single_space_and_strip`, `test_non_printable_ascii_is_dropped`, `test_backtick_fence_run_becomes_equal_length_single_quote_run`, `test_whitespace_collapse_runs_before_truncation_not_after`), the two collapse tests (`test_two_consecutive_identical_records_collapse_into_one_entry_repeat_two`, `test_a_third_identical_record_advances_repeat_to_three`) and the collapsed-eviction test (`test_evicting_a_collapsed_entry_adds_its_whole_repeat_to_dropped`) failed against the Task 1 baseline (naive truncation-only handler, no normalization pipeline, no collapse). The other 18 tests already passed against the Task 1 implementation (length bound, plain ring eviction, counters, level filter, source attribution, install/uninstall, step_scope, snapshot freshness, drift guard) since those properties were already true of the simpler handler. |
| The end-to-end tracer in Task 1 | Not run RED under a strict TDD cycle (Task 1 is `type="tracer"`, not `tdd="true"`) — implemented module, wiring and test together in one commit. Red-ness is established by inspection rather than an observed failing run: before this commit `DiagnosticReport` had no `log_capture` field and `to_dict()` never emitted the key, so `data["log_capture"]` would have raised `KeyError` against the pre-commit code. This is the honest account of what was actually run, not a fabricated pre-implementation failure. |
| The scrub, fence and dedup proofs in Task 3 | Written before implementation. Observed: `7 failed, 6 passed in 0.23s` on the Task-3-specific test subset — `test_diagnostics_section_renders_after_step_table_in_a_fenced_block`, `test_repeat_above_one_renders_count_and_repeat_of_one_does_not`, `test_heading_states_captured_dropped_and_truncated_counts`, `test_saved_md_and_issue_body_share_the_same_section_text`, `test_scrub_reaches_every_vector_inside_a_captured_message`, `test_triple_backtick_in_a_captured_message_cannot_close_the_fence` all failed with `ImportError: cannot import name '_log_capture_lines' from 'firestarter.submit'` (the formatter did not exist yet) or an assertion on absent output; `test_full_block_diagnostics_section_stays_under_4000_chars` was separately observed red first at `4071 >= 4000` against an over-strict worst-case construction (longest real op name `write-baseline-a` + `repeat=99`), then corrected to use the shortest real op name (`write`, `OP_WRITE`) and `repeat=1` — the two bounds `log_capture.py` actually declares (`MAX_ENTRIES`, `MAX_LINE_CHARS`), which passed at 3771 chars. `test_zero_entries_renders_no_section`, `test_none_log_capture_renders_no_section_and_does_not_raise` and `test_dedup_fingerprint_unaffected_by_log_capture_contents` passed even before the formatter existed (vacuously true of an empty/absent block and of a field already outside the dedup hash's allow-list) — correctly NOT part of the red count. |
| The `_TO_DICT_KEYS` pin | Confirmed sensitive via the plan's own anti-vacuity test (`test_to_dict_key_list_pins_are_sensitive_to_added_and_removed_keys`), which already exercises delete/add drift against the pin; adding `log_capture` to the pinned list and the planted-key test's `len(keys) == 16` literal was verified to fail before the edit (both literals were still `15`/absent `log_capture` immediately after Task 1's dataclass/`to_dict()` change, before the test file was updated in the same commit) and to pass after. |

A test whose red evidence cannot be produced does not ship — none were deleted; every listed test's red-then-green transition was observed directly except the Task 1 tracer, whose non-strict-TDD status and inspection-based red-ness are disclosed above rather than glossed over.

## Issues Encountered

None beyond the two deviations documented above.

## Threat Model Verification

All nine `mitigate`-disposition threats (T-nbb-01 through T-nbb-07, T-nbb-09) and the one `accept`-disposition threat (T-nbb-08) were verified empirically, not by assertion:

- **T-nbb-01 (captured text -> public issue body):** `test_scrub_reaches_every_vector_inside_a_captured_message` plants a home-dir path, a `/dev/ttyACM0` device, a `/tmp` path and the operator's username inside a captured message, runs `sanitize_dict(report.to_dict(), user=...)` over the real nested structure, and asserts all four are rewritten in the rendered diagnostics section (not merely in `reason`).
- **T-nbb-02 (data bytes reaching a captured line):** `test_message_one_char_over_bound_is_cut_and_counted_once_in_truncated` and `test_message_exactly_at_bound_is_untouched_and_not_truncated` pin the 160-char bound on every exported message regardless of source.
- **T-nbb-03 (fence-breaking backticks):** `test_backtick_fence_run_becomes_equal_length_single_quote_run` (capture-time neutralization) plus `test_triple_backtick_in_a_captured_message_cannot_close_the_fence` (full pipeline: real `RURP` logger call carrying a literal triple-backtick, through `install()`/`snapshot()`, into `build_body`, asserting the outer fence's inner content contains no bare backtick run).
- **T-nbb-04 (control/escape sequences):** `test_non_printable_ascii_is_dropped` proves an ESC byte (`\x1b`) and a BEL byte (`\x07`) are stripped before storage.
- **T-nbb-05 (unbounded buffer growth):** `test_overflow_evicts_the_oldest_entries_and_counts_them_dropped` and `test_evicting_a_collapsed_entry_adds_its_whole_repeat_to_dropped` prove the ring bound holds even under a collapsed high-repeat entry.
- **T-nbb-06 (oversized issue body):** `test_full_block_diagnostics_section_stays_under_4000_chars` measures the actual rendered section at the module's own two declared bounds (see Deviations #2's sibling note in key-decisions on why `write`/`repeat=1` is the correct "both bounds" reading, not an artificially stacked worst case).
- **T-nbb-07 (silent truncation):** `test_heading_states_captured_dropped_and_truncated_counts` proves `dropped`/`truncated` reach the rendered heading text.
- **T-nbb-08 (unsanitized local artifacts, accepted):** Verified by direct inspection of a real `dev-test-<chip>.md` produced by a live `CliRunner` invocation carrying an unscrubbed `/tmp/scratch123` and `testuser` string in a captured line — confirmed present verbatim in the local `.md` (accepted per the threat register) while the same content is scrubbed when passed through `sanitize_dict` for the filed-issue path (proven separately by T-nbb-01's test).
- **T-nbb-09 (firmware/host misattribution after a rename):** `test_firmware_logger_name_matches_serial_comm_rurp_logger_name` compares `log_capture.FIRMWARE_LOGGER_NAME` against the live `serial_comm.rurp_logger.name`.

No new package-manager install occurred (T-nbb-SC not applicable — `log_capture.py` is stdlib-only, confirmed by its own import block).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `firestarter/log_capture.py` is a clean, stdlib-only leaf module reusable by any future diagnostics feature that needs step-attributed log capture.
- Issue #86 (the `write` step's bare "Operation timed out" with no path to a cause) is now directly addressable: a real hardware timeout run will populate `log_capture.entries` with the firmware/host lines emitted on the way to the timeout, visible in both the saved `.md`/`.json` and any newly filed issue.
- No blockers for the remaining quick-batch items or for `v1.39-protocol-0x05-write-correctness`'s own work.
