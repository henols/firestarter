---
quick_id: 260821-spg
phase: quick-260821-spg
plan: 01
type: execute
wave: 1
depends_on: []
commits_land_in: firestarter_app
files_modified:
  - firestarter_app/firestarter/cli_handlers.py
  - firestarter_app/firestarter/diagnostic_report.py
  - firestarter_app/firestarter/submit.py
  - firestarter_app/tools/check_devtest_orchestrator.py
  - firestarter_app/tools/check_diagnostic_report_claims.py
  - firestarter_app/tests/test_check_devtest_orchestrator.py
  - firestarter_app/tests/test_dev_test_cmd.py
  - firestarter_app/tests/test_diagnostic_report.py
  - firestarter_app/tests/test_op_registration_parity.py
  - firestarter_app/tests/test_submit.py
  - firestarter_app/tests/test_sdp_recovery_wording.py
  - firestarter_app/doc/community-validation.md
autonomous: true
requirements: [QUICK-260821-spg]

must_haves:
  truths:
    - "`firestarter dev test --help` fits on one screen (<=14 lines) and says what the command does: runs the chip-validation sweep, writes to the chip, and produces a diagnostic report you can file."
    - "A completed `dev test` run prints NO up-front always-writes preamble and NO SDP recovery / restore-advice line -- neither the loud nor the neutral form."
    - "The result table renders `protocol` as a 2-digit hex cell and both chip-ID sides as 4-digit hex cells, and does not crash when either value is `None` or non-numeric."
    - "The result table has no `transport_health` row, no `is_submittable` row, and no `db_diff:*` rows (nor the `not computed` fallback), and each per-step row shows a bare verdict with no error-code/fingerprint suffix."
    - "`dev test` no longer echoes the issue body to the console on either the off-TTY or the interactive path, while the saved-report path line, the issue URL, the dedup notes, the confirm prompts and the filed/comment URLs all still print."
    - "`DiagnosticReport.to_dict()` still carries every key it carries today (`transport_health`, `is_submittable`, `db_diff`, per-step `error_code`/`fingerprint`, `dedup_fingerprint`, `sdp_hold_state`, `voltage`), and the saved JSON/markdown artifacts plus the filed issue body are unchanged in content."
    - "The design-history prose that was `dev_test`'s docstring still lives in `cli_handlers.py` as comment text, reachable by `grep`, and is absent from `--help`."
    - "`_dev_test_exit_code`, its marginal-beats-bad `max` precedence, the `sdp_oracle_not_run` floor, the `write-restored` sweep step, `sdp_left_writable` and `sdp_hold_state` all behave exactly as before -- `report.sdp_hold_state` is still computed, still rendered in its own console row, and still in the JSON."
    - "Every test and tool that asserted the removed console output has an explicit, recorded disposition (retargeted at the JSON payload, deleted as testing removed behaviour, or kept unchanged) -- no blanket deletion, no weakened data invariant."
    - "The full `firestarter_app` suite plus `ruff check`, `ruff format --check` and the mypy watermark gate are green locally on the devcontainer's Python 3.12; CI's Python 3.11 leg is NOT claimed."
  artifacts:
    - firestarter_app/firestarter/cli_handlers.py
    - firestarter_app/firestarter/diagnostic_report.py
    - firestarter_app/firestarter/submit.py
    - firestarter_app/tools/check_devtest_orchestrator.py
  key_links:
    - "`dev_test`'s body -> the two removed `click.echo(...)` calls -> the tester's console."
    - "`DiagnosticReport.to_dict()` -> `render()` (fewer rows) and `to_json_block()` (unchanged) -- the single-source contract RPT-01/D-01 requires render to keep deriving from that same dict."
    - "`submit_report` -> `build_body` -> `build_issue_url` / `gh` stdin / browser tier: the body is still BUILT and still SENT, only the two console echoes go."
    - "`tools/check_devtest_orchestrator.py::_HANDLER_FUNCTION_NAMES` <-> `tests/test_check_devtest_orchestrator.py::_EXPECTED_DEV_TEST_REFERENCED_HELPERS` <-> the set of `_`-helpers `dev_test`'s body references: an EXACT-equality gate, so deleting `_sdp_recovery_line` requires all three to move in the same commit."
    - "`sdp_honesty.unreadable_state_caveat()` -> `lock_status.py:221` and `chip_test`'s NOT-RUN fallback: it keeps live production callers after the two deleted recovery constants go, so `tests/test_sdp_honesty.py` and `tests/test_chip_test_sdp_leg.py` stay untouched."
---

<objective>
Trim `firestarter dev test`'s console output to what a tester actually needs: a short
`--help`, no lectures before or after the run, a result box whose numbers read as hex and
whose rows are all signal, and no dump of the issue body into the terminal.

Purpose: the operator's verbatim complaint is that `dev test` prints "a lot of rubbish".
Every item below is display-layer only. The diagnostic PAYLOAD -- the JSON, the markdown
artifact, the filed issue body, the exit codes and the SDP oracle -- is deliberately
untouched, so nothing a maintainer triages from is lost.

Output: shorter help text, two removed echoes, a slimmer result table, no body dump, plus
an explicitly-dispositioned test surface (nine test modules and two tools assert this
output today).
</objective>

<execution_context>
@/workspaces/.claude/gsd-core/workflows/execute-plan.md
@/workspaces/.claude/gsd-core/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@/workspaces/CLAUDE.md
@/workspaces/firestarter_app/CLAUDE.md

Source files to read before editing:
@/workspaces/firestarter_app/firestarter/cli_handlers.py
@/workspaces/firestarter_app/firestarter/diagnostic_report.py
@/workspaces/firestarter_app/firestarter/submit.py
@/workspaces/firestarter_app/firestarter/sdp_honesty.py
</context>

<stated_assumption>
**Recorded so the operator can correct it:** "Trying to restore the eprom to its initial
state is never interesting" is read as a complaint about the SDP recovery/restore PROSE,
not as a request to remove the `write-restored` sweep step.

Basis: every other item in the same message is about printed output, and the sentence
continues "if you run the dev test you are aware that the data on the EPROM will be
destroyed" -- i.e. do not lecture me about recovery. So `OP_WRITE_RESTORED`
(`chip_test.py:406`), `sdp_left_writable`, `sdp_hold_state` and the `sdp_oracle_not_run`
exit floor all stay, `report.sdp_hold_state` is still computed and still appears in the
JSON and in its own console row, and only the two prose forms and their selector go.

If that reading is wrong, the sweep-step removal is a separate, larger change (it moves
exit codes and the SDP oracle) and must be planned as such.
</stated_assumption>

<planner_measurements>
Measured on branch `quick-devtest-output-trim` (2026-08-21). Use these anchors instead of
re-searching; verify each still matches before editing (line numbers shift as you edit).

## Source anchors

`firestarter/cli_handlers.py`
- imports: `SDP_HOLD_HELD` (45), `SDP_HOLD_NOT_HELD` (46), `SDP_HOLD_NOT_RUN` (47),
  `sdp_left_writable` (59), `sdp_hold_state` (58), `sdp_oracle_applicable` (60),
  `from firestarter import sdp_honesty` (35).
- `_ALWAYS_WRITES_PASS_COUNT = 6` (2486) + its comment block (2487-2506).
- `_ALWAYS_WRITES_NOTICE` (2507-2523).
- recovery-constant comment block (2526-2542), `_SDP_RECOVERY_LOUD` (2543-2549),
  `_SDP_RECOVERY_NEUTRAL` (2550-2556), `SDP_RECOVERY_CONSTANT_NAMES` (2558-2563),
  `_sdp_recovery_line` (2566-2587).
- decorators (2589-2592), `def dev_test` (2593), docstring (2594-2630) -- 37 lines,
  which is what `--help` renders today.
- `click.echo(_ALWAYS_WRITES_NOTICE)` (2631).
- recovery echo: comment 2733-2737, `hold_state`/`left_writable` locals 2738-2739,
  `click.echo(_sdp_recovery_line(...))` (2740).
- exit-code block (2744-2752) -- untouched.

Import-usage after the deletions (measured, whole file):
- `sdp_left_writable` -> ONLY line 2739 -> import must go.
- `SDP_HOLD_HELD` / `SDP_HOLD_NOT_HELD` -> ONLY inside `_sdp_recovery_line` -> imports must go.
- `SDP_HOLD_NOT_RUN` -> still used at 2750 (exit floor) -> KEEP.
- `sdp_honesty` -> still used at 1848 (`map_unknown_cmd_to_outdated_for_operation`) -> KEEP.
- `_ALWAYS_WRITES_PASS_COUNT` -> after deleting the notice, referenced only by tests -> KEEP
  (a module-level constant, so no ruff F-rule fires; it backs a real sweep invariant).

`firestarter/diagnostic_report.py`
- `NOT_MEASURED` (102), `NOT_REPORTED` (103), `_identity_cell` (375-395).
- `to_dict()` ends ~553 -- DO NOT TOUCH.
- `render()` (555): rows at 567 host_version, 568 fw_board_identity, 569 hw_revision,
  570 protocol, 571-575 chip_id, 577-582 per-step, 584-592 transport_health,
  594 banner, 599 sdp_hold_state, 602-609 voltage, 611 is_submittable,
  613-628 db_diff (3 rows + `not computed` fallback).
- `to_json_block()` (634) -- DO NOT TOUCH.

`firestarter/submit.py`
- `_print(body, console=console)` at 611 (off-TTY path) and 626 (interactive path). Both go.
- `body` stays live afterwards: `build_issue_url(title, body)`, `comment_via_gh_fn(...)`,
  `submit_via_gh(...)`, `submit_via_browser(...)` all still consume it -- no unused local.
- the `is_submittable` refuse gate (585-600) stays exactly as is.

Value shapes (so the hex cells are written against reality, not a guess):
- `auto_capture.protocol` is `str(prog.get("algorithm"))` (cli_handlers:2687) -- a decimal
  int-as-string like `"13"` in production. Test fixtures already pass hex-shaped strings
  (`"0x0D"` in `tests/test_chip_test.py:2509`, `"0x08"` in `_minimal_report`), so the
  formatter must be idempotent on `0x`-prefixed input.
- `chip_id_expected` / `chip_id_actual` are `Optional[int]` (`_chip_id_fields`,
  cli_handlers:2334-2362) -- ints in production, `None` on a clean/NA/SKIPPED id step.

## Hard constraint measured during planning (do NOT render `NOT_REPORTED` for absent IDs)

`tests/test_diagnostic_report.py::test_absent_identity_renders_the_explicit_marker_in_both_rows`
(1124-1148) asserts `rendered.count(NOT_REPORTED) == 2` over the WHOLE table, and its
docstring records that the `chip_id (expected/actual)` row "legitimately renders
`None / None` on this same minimal report (D-12)". So the hex helper must render an
absent/non-numeric value as `str(value)` (i.e. `None` -> `"None"`, exactly today's text),
NOT as `NOT_REPORTED`. That keeps a live gate green and keeps D-12's recorded rationale
true. The operator asked only that `None` not crash; the display text for absent is
unspecified, so this is the low-churn, non-contradicting choice.

## Doc claim that becomes false

`doc/community-validation.md:46-50` states `ladder_state` "flows through
`DiagnosticReport.to_dict()['db_diff']['ladder_state']` into **both** `render()` (the
`rich` table) and `to_json_block()`". Removing the db_diff rows makes that false; correct
it to JSON-only in Task 2.

## Gate / test disposition table (every match accounted for)

Matches counted with
`_SDP_RECOVERY|SDP_RECOVERY_CONSTANT_NAMES|_ALWAYS_WRITES_NOTICE|ALWAYS WRITES|is_submittable|transport_health|unreadable_state_caveat`.

| Target | Matches | Disposition | Why |
| --- | --- | --- | --- |
| `tests/test_sdp_recovery_wording.py` | 21 | **(b) delete the whole file** | Every one of its three scan targets (`SDP_RECOVERY_CONSTANT_NAMES` and the two constants it resolves, plus a rule-1 scan of `_ALWAYS_WRITES_NOTICE`) is being removed. It contains no data invariant -- it is a pure wording gate over console prose that no longer exists. The honesty rules it enforced still apply to the strings that REMAIN, and those are gated by `tests/test_sdp_honesty.py` (the caveat sentence) and `tools/check_diagnostic_report_claims.py` (the report module's literals). |
| `tests/test_dev_test_cmd.py::TestAlwaysWritesNotice` (517-542) | 2 | **(b) delete the class** | Asserts the removed preamble is the first stdout line, on both the normal and unknown-chip run. Pure assertion about deleted output. |
| `tests/test_dev_test_cmd.py::TestAlwaysWritesNoticeDerivedCountD09::test_pass_count_is_derived_from_a_live_plan_never_a_literal` | 2 | **(a) retarget** | Real data invariant: derives the write-pass count from a live `derive_plan` result and pins `_ALWAYS_WRITES_PASS_COUNT`. Keep the derivation and the equality; drop only the trailing `str(...) in _ALWAYS_WRITES_NOTICE` line. Rename the class off "Notice". |
| ...`::test_notice_names_sdp_lock_completed_run_and_rewrite_recovery` | 4 | **(b) delete** | Wording gate on deleted prose. |
| ...`::test_notice_contains_no_sdp_leg_op_literal` | 2 | **(b) delete** | Same claim is independently held for the surviving units by `tests/test_op_registration_parity.py::test_non_registry_still_has_no_ops`. |
| `tests/test_dev_test_cmd.py::TestSdpRecoveryFormsD12` (3 CLI tests) | 8 | **(a) retarget** | Each test also carries genuine data assertions (`sdp_hold_state` value, `write-restored` verdict, `sdp_lock.assert_not_called()`), and `make_restore_failed_operator` is used by NOTHING ELSE in the suite (measured) -- deleting the class would silently drop the only coverage of the restore-failed path. Keep the fixtures and the data assertions; drop the two prose assertions per test. |
| `tests/test_dev_test_cmd.py::TestCtrlCResidualNotClosedD12` | 2 | **(a) retarget** | Keep the "no report file was written" assertion (the real claim); drop the two now-unreferenceable constant assertions. |
| `tests/test_dev_test_cmd.py` line 322-339 (`_ALWAYS_WRITES_PASS_COUNT` end-to-end write count) | 1 | **(c) keep unchanged** | Counts real write passes through the CLI; independent of any printed prose. |
| `tests/test_dev_test_cmd.py::test_json_artifact_is_report_to_dict` (lines 746, 750) | 2 | **(c) keep unchanged** | Asserts `transport_health` and `is_submittable` are keys of the SAVED JSON. This is exactly the payload that must survive -- it is now the non-vacuity proof that only the console changed. |
| `tests/test_op_registration_parity.py` | 3 | **(a) surgical edit** | Remove the `_ALWAYS_WRITES_NOTICE` entry from `_DECLARED_NON_REGISTRIES` (358-363), drop `_DECLARED_NON_REGISTRY_COUNT` 6 -> 5, and fix the docstring mention (line 83). Its locator resolves a now-deleted constant, so leaving it breaks the module. Every other entry and both tests stay. |
| `tools/check_devtest_orchestrator.py` (`_HANDLER_FUNCTION_NAMES`, 167 + comment 164-166) | 1 | **(a) surgical edit** | `tests/test_check_devtest_orchestrator.py::test_handler_function_names_all_resolve_to_real_callables` requires every listed name to be a real callable, so `_sdp_recovery_line` must leave the frozenset with the function. |
| `tests/test_check_devtest_orchestrator.py::_EXPECTED_DEV_TEST_REFERENCED_HELPERS` (553-561) | 1 | **(a) surgical edit** | `test_every_helper_referenced_by_dev_test_is_listed` asserts EXACT equality with the set derived from `dev_test`'s body, so removing the call requires removing the name (7 -> 6). Its own `len(derived) >= 6` floor still holds at exactly 6. Add a dated line to the comment block (540-551) recording the removal, matching that block's existing convention. |
| `tests/test_diagnostic_report.py` | 10 | **(c) keep unchanged, + new tests** | All ten matches are `to_dict()`-level or `build_db_diff` unit calls; none asserts a console row for `transport_health`/`is_submittable`/`db_diff` (measured). Task 2 ADDS hex-render tests here. |
| `tests/test_provenance.py` | 8 | **(c) keep unchanged** | `is_submittable(...)` unit calls plus one render test asserting the `hw_revision` CELL -- that row stays. |
| `tests/test_chip_test_sdp_leg.py` | 7 | **(c) keep unchanged** | All about `sdp_honesty.unreadable_state_caveat()`, which keeps production callers (`lock_status.py:221`, `sdp_honesty.summary_line`, `chip_test`'s NOT-RUN fallback) after the two constants go. |
| `tests/test_sdp_honesty.py` | 6 | **(c) keep unchanged** | Same -- the caveat function and its wording are untouched. |
| `tests/test_parse_devtest_issue.py` | 4 | **(c) keep unchanged** | Parses ISSUE BODIES; `build_body`/`sanitize_dict` and the body itself are unchanged. |
| `tools/check_diagnostic_report_claims.py` | 2 | **(c) keep logic, prose-only fix** | Its 14 forbidden-phrase scan is unaffected. Its "Scope note" claims the two recovery constants "already have their own committed, scoped gate (`tests/test_sdp_recovery_wording.py`)" -- both are gone, so that paragraph becomes false and must be corrected. No test asserts this module's docstring (measured), so the edit is safe. |
| `tests/test_submit.py::test_offtty_prints_body_and_url_never_sends` (823-859) | -- | **(a) retarget** | Asserts `"| id | OK |"` reaches `console.print`. Retarget: URL still printed, body table line NOT printed, every negative-call assertion kept. Rename to match. |
| `tools/check_no_log_in_sdp_window.py`, `tools/check_sdp_capability_invariants.py`, `tools/check_protection_readability_invariants.py` | 0 | **(c) keep unchanged** | Measured: none of the three references `cli_handlers.py`, `diagnostic_report.py` or `submit.py`'s render/echo surfaces. |
| `tests/__snapshots__/test_characterization.ambr` | 0 | **(c)** | Measured: contains no `dev test` output, so no snapshot regenerates. |
| `doc/community-validation.md`, `README.md` | -- | **doc fix in Task 2** | Only `community-validation.md:46-50` makes a render-surface claim; nothing quotes the removed prose. |

## Known red window

Tasks 1-3 each leave `tests/test_dev_test_cmd.py` unable to IMPORT (it imports the deleted
constants at module scope), so the FULL suite is red until Task 4. That is expected and
planned: each task's own verify legs are scoped to what must be green at that point, and
Task 4 is the task that proves the whole suite.
</planner_measurements>

<execution_constraints>
- Branches are ALREADY created. Do NOT create or switch branches. Meta (`/workspaces`) and
  `/workspaces/firestarter_app` are both on `quick-devtest-output-trim`.
- ALL code commits land INSIDE `/workspaces/firestarter_app` on that branch. Do NOT bump
  the meta-repo gitlink -- the operator handles that.
- No worktree isolation (worktrees leave this repo's submodules empty). Work in place.
- Python env: `cd /workspaces/firestarter_app && python -m pytest`. `addopts` is `-ra -q`;
  add `-o addopts=""` when you want the count line.
- The devcontainer is Python 3.12; CI is Python 3.11. A clean local run is necessary but
  NOT sufficient -- report it as "green locally on 3.12", never as "CI green".
- `ruff format --check firestarter/ tests/` is a gate: every edit must be format-clean.
- Do not introduce `except Exception:` anywhere in `cli_handlers.py`, `submit.py` or
  `chip_test.py` -- `tools/check_devtest_orchestrator.py` has a broad-except deny bucket.
- New string literals in `diagnostic_report.py` are scanned by
  `tools/check_diagnostic_report_claims.py` (14 forbidden honesty-claim phrases, e.g.
  "verified fixed", "confirmed working"). Keep new labels and docstrings plain and factual.
- One commit per task, conventional-commit style, scope `dev-test-output`.
</execution_constraints>

<tasks>

<task type="auto">
  <name>Task 1: Shorten `dev test --help` and remove both console lectures</name>
  <files>firestarter/cli_handlers.py, tools/check_devtest_orchestrator.py, tests/test_check_devtest_orchestrator.py</files>
  <action>
Read `firestarter/cli_handlers.py` around lines 2480-2760 first, then make four coupled edits.

**1a. Replace `dev_test`'s docstring (2594-2630) with a short help blurb.** At most 6 lines,
at most ~14 rendered `--help` lines including Click's usage/options block. It must say: it
runs the community chip-validation sweep for CHIP; it writes to the chip; it saves a
diagnostic report under the config dir's `reports` directory and offers to file it; and the
exit code meaning (0 all steps clear, 2 any marginal step, 1 any bad step including a
chip-ID mismatch). One short clause about writing to the chip belongs in `--help` -- that is
where such a fact is useful; what the operator removed is the run-time lecture, not the
documentation.

**1b. Preserve the design-history prose, out of `--help`.** Move the whole existing
docstring's substance -- the zero-options/D-05 note, the ALWAYS-WRITES/D-04 ordering note,
the UV-ask D-01/D-03 behaviour, the Phase 121 D-01/D-03/D-04/D-05 reversal paragraph, the
Phase 112 Plan 04 partial-reversal note, and the exit-code derivation -- into a `#` comment
block placed immediately ABOVE the `@dev.command(name="test")` decorator. Keep the wording;
only reflow it as comment lines. Add one leading line recording why it moved: it is
load-bearing project history that was being rendered as help text, and this quick task moved
it out of `--help` without deleting it. Comments are not AST string literals, so this does
not interact with any op-vocabulary or claim scanner.

**1c. Delete the two echoes and everything that existed only to feed them.** Remove
`click.echo(_ALWAYS_WRITES_NOTICE)` (2631) and the whole recovery-echo block (2733-2740,
including the `hold_state` and `left_writable` locals and their comment). Then delete
`_ALWAYS_WRITES_NOTICE` (2507-2523) with its comment block (2487-2506), the recovery-constant
comment block (2526-2542), `_SDP_RECOVERY_LOUD`, `_SDP_RECOVERY_NEUTRAL`,
`SDP_RECOVERY_CONSTANT_NAMES` and `_sdp_recovery_line` (2543-2587). Rationale for deleting
rather than keeping them unreferenced: a prose constant that nothing prints, still policed by
three separate wording gates, is exactly the dead weight this task exists to remove.

KEEP `_ALWAYS_WRITES_PASS_COUNT = 6`. It backs a real sweep invariant (a full ALLOW-chip run
makes six write passes) that two surviving tests measure from a live plan. Rewrite its
comment block down to a few lines stating what the number is and that it is measured by
`tests/test_dev_test_cmd.py`, dropping the parts that only described the deleted notice.

Then prune the now-unused imports: `sdp_left_writable` (59), `SDP_HOLD_HELD` (45),
`SDP_HOLD_NOT_HELD` (46). Keep `SDP_HOLD_NOT_RUN`, `sdp_hold_state`, `sdp_oracle_applicable`
and `from firestarter import sdp_honesty` -- all still used (see the measurements table).

**1d. Do NOT touch anything else in the handler.** `report.sdp_hold_state = sdp_hold_state(...)`,
`report.db_diff = build_db_diff(...)`, the JSON/markdown writes, the `Report written to ...`
line, the `submit_report` call and the entire exit-code block stay byte-identical.

**1e. Move the two coupled gate declarations in the same commit.** In
`tools/check_devtest_orchestrator.py`, remove `"_sdp_recovery_line"` from
`_HANDLER_FUNCTION_NAMES` along with its two-line comment (164-167). In
`tests/test_check_devtest_orchestrator.py`, remove `"_sdp_recovery_line"` from
`_EXPECTED_DEV_TEST_REFERENCED_HELPERS` (back to six names) and append one dated line to the
comment block above it (540-551) recording that the recovery echo was removed from
`dev_test`'s body by this quick task, so the count moves from seven back to six -- matching
that block's existing per-change convention.
  </action>
  <verify>
    <automated>cd /workspaces/firestarter_app && python -c 'from firestarter.cli_handlers import dev_test; h = dev_test.help or ""; print(h); assert "REVERSAL" not in h and "D-05" not in h and "Phase 121" not in h, h; assert len(h.strip().splitlines()) <= 8, len(h.strip().splitlines())'</automated>
    <automated>cd /workspaces/firestarter_app && python -c 'from click.testing import CliRunner; from firestarter.cli_handlers import cli; r = CliRunner().invoke(cli, ["dev", "test", "--help"]); n = len(r.output.strip().splitlines()); print(n); print(r.output); assert r.exit_code == 0 and n <= 14, (r.exit_code, n)'</automated>
    <automated>cd /workspaces/firestarter_app && python -c 'src = open("firestarter/cli_handlers.py").read(); assert "REVERSAL" in src and "supersedes" in src, "the design-history prose must still be present in the file"'</automated>
    <automated>cd /workspaces/firestarter_app && python -c 'import firestarter.cli_handlers as m; gone = [n for n in ("_ALWAYS_WRITES_NOTICE", "_SDP_RECOVERY_LOUD", "_SDP_RECOVERY_NEUTRAL", "SDP_RECOVERY_CONSTANT_NAMES", "_sdp_recovery_line") if hasattr(m, n)]; assert not gone, gone; assert hasattr(m, "_ALWAYS_WRITES_PASS_COUNT")'</automated>
    <automated>cd /workspaces/firestarter_app && python -c 'import inspect, firestarter.cli_handlers as m; src = inspect.getsource(m.dev_test.callback); assert "click.echo" not in src, src; assert "sdp_hold_state" in src and "_dev_test_exit_code" in src and "sdp_oracle_applicable" in src'</automated>
    <automated>cd /workspaces/firestarter_app && python tools/check_devtest_orchestrator.py && python -m pytest tests/test_check_devtest_orchestrator.py -q</automated>
    <automated>cd /workspaces/firestarter_app && ruff check firestarter/ tools/ && ruff format --check firestarter/</automated>
  </verify>
  <done>`dev test --help` renders 14 lines or fewer and carries no design-history prose; that prose is still greppable in `cli_handlers.py` as comment text; neither echo remains; the five names are gone and `_ALWAYS_WRITES_PASS_COUNT` remains; the exit-code block, `sdp_hold_state` assignment and `submit_report` call are untouched; the orchestrator tool and its test module are green with a six-name expected set.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Hex-render protocol and chip IDs, drop the noise rows</name>
  <files>firestarter/diagnostic_report.py, tests/test_diagnostic_report.py, doc/community-validation.md</files>
  <behavior>
Add these tests to `tests/test_diagnostic_report.py` FIRST, against a helper that does not
exist yet, and see them fail before implementing. Read the `Value` cell for a named row via
the existing `dict(zip(field_col.cells, value_col.cells))` idiom already used at line ~1138;
use the existing `_rendered_text(table)` helper for whole-table checks.

- `protocol="13"` (production shape, decimal int-as-string) renders the cell `0x0D`.
- `protocol="0x0D"` (fixture shape) renders `0x0D` -- the formatter is idempotent.
- `protocol=None` renders `None` and does not raise.
- `protocol="banana"` renders `banana` verbatim and does not raise.
- `chip_id_expected=0x00A4, chip_id_actual=None` renders the cell `0x00A4 / None`.
- `chip_id_expected=0x1234, chip_id_actual=0x1234` renders `0x1234 / 0x1234` (4 digits, upper-case hex digits, `0x` prefix).
- The rendered table has NO row whose Field cell is `transport_health`, `is_submittable`,
  `db_diff`, `db_diff: current_support_status`, `db_diff: proposed_disposition` or
  `db_diff: ladder_state`, on BOTH a report with a populated `db_diff` and one with
  `db_diff=None` (the old `not computed` fallback path).
- No per-step Value cell contains an error-code or fingerprint suffix: for a report whose
  step carries a non-`None` `error_code` and a `Fingerprint`, the step row's Value cell
  equals the verdict string exactly.
- The rows that stay are still present: `host_version`, `fw_board_identity`, `hw_revision`,
  `protocol`, `chip_id (expected/actual)`, one row per step, `banner`, `sdp_hold_state`,
  `voltage`.
- `to_dict()` is unchanged: for the same report, `transport_health`, `is_submittable`,
  `db_diff`, `dedup_fingerprint`, `sdp_hold_state` and `voltage` are all still present, and
  each entry of `to_dict()["steps"]` still carries `error_code` and `fingerprint`.
  </behavior>
  <action>
Read `firestarter/diagnostic_report.py` lines 95-115 and 370-400 and 540-640 first.

Add a module-level render-only helper beside `_identity_cell` -- `_hex_cell(value, digits)`.
Contract: return `str(value)` unchanged when the value is `None` or cannot be parsed as an
integer; otherwise parse with base-0 (`int(str(value), 0)`, so both `"13"` and `"0x0D"`
work) and return an upper-case `0x`-prefixed string zero-padded to `digits` hex digits.
Catch only `ValueError`/`TypeError`, never a bare `Exception`. Its docstring must state that
it is render-only and that `to_dict()` keeps the raw typed value, mirroring `_identity_cell`'s
own recorded reasoning, and must NOT render `NOT_REPORTED` for an absent value -- see the
measured constraint in this plan: a live gate asserts `NOT_REPORTED` appears exactly twice
in the table, and D-12 deliberately leaves the chip-ID row rendering `None`.

Then, inside `render()` only:
- protocol row -> `_hex_cell(ac["protocol"], 2)`.
- chip-ID row -> `f"{_hex_cell(ac['chip_id_expected'], 4)} / {_hex_cell(ac['chip_id_actual'], 4)}"`.
- per-step rows -> Value cell is `str(step_row["verdict"])`, nothing else. Drop the
  `error_code`/`fingerprint` suffix f-string.
- delete the `transport_health` row block, the `is_submittable` row, and the entire `db_diff`
  if/else block including the fallback row.
- keep `host_version`, the two identity rows, `banner`, `sdp_hold_state` and `voltage`
  exactly as they are.
- update `render()`'s own docstring and the `sdp_hold_state` row comment so they describe
  the table as it now is (the comment at ~596-598 currently explains the per-step row shows
  op/verdict/error_code/fingerprint -- it now shows op/verdict only, which makes the
  "`reason` never reaches this table" point MORE true, not less; keep that point).

`to_dict()`, `_transport_dict`, `_step_dict`, `_db_diff_dict`, `_voltage_dict`,
`is_submittable`, `dedup_fingerprint`, `build_db_diff` and `to_json_block()` are all
untouched. Add no explanatory prose rows to the table.

Finally correct `doc/community-validation.md` (the paragraph at 46-50): `ladder_state` now
flows from `to_dict()['db_diff']['ladder_state']` into `to_json_block()` (the fenced JSON in
the issue body) only -- the console table no longer carries a `db_diff` row. Keep the
single-source point; just stop claiming the render surface.
  </action>
  <verify>
    <automated>cd /workspaces/firestarter_app && python -m pytest tests/test_diagnostic_report.py -q</automated>
    <automated>cd /workspaces/firestarter_app && python -m pytest tests/test_provenance.py tests/test_chip_test.py tests/test_parse_devtest_issue.py tests/test_check_diagnostic_report_claims.py -q</automated>
    <automated>cd /workspaces/firestarter_app && python -c 'import inspect, firestarter.diagnostic_report as m; src = inspect.getsource(m.DiagnosticReport.render); bad = [t for t in ("transport_health", "is_submittable", "db_diff", "error_code", "fingerprint") if t in src]; assert not bad, bad; assert "_hex_cell" in src'</automated>
    <automated>cd /workspaces/firestarter_app && python -c 'import inspect, firestarter.diagnostic_report as m; src = inspect.getsource(m.DiagnosticReport.to_dict); need = [t for t in ("transport_health", "is_submittable", "db_diff", "dedup_fingerprint", "sdp_hold_state", "voltage") if t not in src]; assert not need, need'</automated>
    <automated>cd /workspaces/firestarter_app && python tools/check_diagnostic_report_claims.py</automated>
    <automated>cd /workspaces/firestarter_app && ruff check firestarter/ tests/ && ruff format --check firestarter/ tests/ && python tools/check_mypy_watermark.py</automated>
  </verify>
  <done>The table shows `0x0D`-shaped protocol and `0x00A4`-shaped chip IDs, verdict-only step rows, and no transport/submittable/db_diff rows; `None` and non-numeric values render without raising; `to_dict()` and `to_json_block()` are unchanged; the new hex tests were seen RED before the helper existed and are GREEN after; the doc no longer claims a db_diff console row.</done>
</task>

<task type="auto">
  <name>Task 3: Stop echoing the issue body to the console</name>
  <files>firestarter/submit.py, tests/test_submit.py</files>
  <action>
Read `firestarter/submit.py` 555-700 first.

Delete the two `_print(body, console=console)` calls -- line 611 on the off-TTY path and
line 626 on the interactive path. Nothing else in `submit_report` changes: the
`is_submittable` refuse gate, `sanitize_dict`/`build_title`/`build_body`, the dedup query,
`build_issue_url` and its printed URL, the two dedup note lines, the duplicate-comment
prompt, the normal filing prompt, the `gh`/browser tier dispatch and every filed/comment URL
line all stay exactly as they are. `body` remains in use by `build_issue_url`,
`comment_via_gh_fn`, `submit_via_gh` and `submit_via_browser`, so no local goes unused.

Update `submit_report`'s docstring where it describes Step 4 as "prints the sanitized body
and the issue URL" -- it now prints the issue URL (and the dedup outcome). Say plainly that
the body is no longer echoed because the full report is already persisted under the config
dir's `reports` directory and that path is printed by the caller, so nothing is lost, and
that the body still reaches every downstream seam sanitized.

Then retarget the one test that asserts the echo:
`tests/test_submit.py::test_offtty_prints_body_and_url_never_sends` (823-859). Rename it to
name the new behaviour (e.g. `test_offtty_prints_url_not_body_and_never_sends`), keep every
existing negative-call assertion (`browser_open`, `run_fn`, `confirm_fn`, `which_fn` all
un-called; `find_prior_report_fn` called once) and the issue-URL assertion, and replace the
body assertion with its inverse: the markdown table line the body carries must NOT appear in
anything printed. Note in its docstring why the inverse assertion is meaningful rather than
vacuous -- `build_body` is still called and the body still reaches `build_issue_url`, so the
test proves the ECHO went and not the body.

Add one interactive-path test alongside it (same fixture shape, `isatty_fn` returning `True`,
`confirm_fn` returning `False` so nothing is filed): the confirm prompt is reached and the
body table line is never printed. That is the second removed echo, and no existing test
covers its absence.
  </action>
  <verify>
    <automated>cd /workspaces/firestarter_app && python -c 'import inspect, firestarter.submit as m; src = inspect.getsource(m.submit_report); assert src.count("_print(body") == 0, src; assert "build_issue_url" in src and "build_body" in src and "is_submittable" in src'</automated>
    <automated>cd /workspaces/firestarter_app && python -m pytest tests/test_submit.py -q</automated>
    <automated>cd /workspaces/firestarter_app && python -m pytest tests/test_parse_devtest_issue.py -q</automated>
    <automated>cd /workspaces/firestarter_app && python tools/check_devtest_orchestrator.py && ruff check firestarter/ tests/ && ruff format --check firestarter/ tests/</automated>
  </verify>
  <done>Neither `submit_report` path echoes the body; the URL, dedup notes, prompts and filed/comment URLs still print; the off-TTY test asserts the inverse and the new interactive test covers the second echo; `build_body`/`build_title`/`sanitize_dict` and the issue body itself are unchanged.</done>
</task>

<task type="auto">
  <name>Task 4: Reconcile the asserting test surface and prove the whole suite</name>
  <files>tests/test_dev_test_cmd.py, tests/test_sdp_recovery_wording.py, tests/test_op_registration_parity.py, tools/check_diagnostic_report_claims.py</files>
  <action>
Apply the disposition table in this plan's measurements section exactly -- one edit per row,
no blanket deletion, and do not weaken any assertion that is really about the DATA.

**4a. `tests/test_dev_test_cmd.py`.** Drop `_ALWAYS_WRITES_NOTICE`, `_SDP_RECOVERY_LOUD`,
`_SDP_RECOVERY_NEUTRAL` and `SDP_RECOVERY_CONSTANT_NAMES` from the `firestarter.cli_handlers`
import block (63-67), keeping `_ALWAYS_WRITES_PASS_COUNT`, `_dev_test_exit_code` and `cli`.
Delete the `TestAlwaysWritesNotice` class (517-542). In
`TestAlwaysWritesNoticeDerivedCountD09`: keep
`test_pass_count_is_derived_from_a_live_plan_never_a_literal` minus its final
`str(...) in _ALWAYS_WRITES_NOTICE` assertion, delete the two wording tests, rename the class
to describe what survives (the live-plan-derived write-pass count) and rewrite its docstring
to stop describing a notice that no longer exists. In `TestSdpRecoveryFormsD12`: keep all
three tests' fixtures and data assertions, delete the six prose assertions, rename the class
and rewrite its docstring to say it now proves the leg's OUTCOMES (hold state, restore
verdict, `sdp_lock` not called) with the recovery prose removed. In
`TestCtrlCResidualNotClosedD12`: keep the no-report-written assertions, delete the two
constant assertions, and update the docstring so it no longer promises a recovery-line claim.
Leave the write-pass end-to-end test (322-339) and `test_json_artifact_is_report_to_dict`
(730-755) untouched -- the latter is now the proof that the payload survived.

Add ONE new non-vacuous regression test (module-level, near the other CLI tests) that pins
the trim structurally rather than by absent-string scanning: assert
`firestarter.cli_handlers` has none of the four removed attributes
(`_ALWAYS_WRITES_NOTICE`, `_SDP_RECOVERY_LOUD`, `_SDP_RECOVERY_NEUTRAL`,
`SDP_RECOVERY_CONSTANT_NAMES`) and no `_sdp_recovery_line`; assert `dev test --help` renders
at most 14 lines; and assert a real off-TTY CLI run's output contains neither the markdown
table header the issue body carries nor a `transport_health` row label, while the same run's
saved JSON still has `transport_health`, `is_submittable` and `db_diff` keys. That last pair
of assertions is the whole point of the task -- console trimmed, payload intact -- and it
would fail if any of the three source edits regressed.

**4b. Delete `tests/test_sdp_recovery_wording.py`.** All three of its scan targets are gone.
Record the deletion and its reasoning in the task's commit message.

**4c. `tests/test_op_registration_parity.py`.** Remove the `_ALWAYS_WRITES_NOTICE` entry from
`_DECLARED_NON_REGISTRIES` (358-363), change `_DECLARED_NON_REGISTRY_COUNT` from 6 to 5, and
fix the module docstring mention at line 83. Add a short note at the removed entry's former
position (or in the docstring) recording that the constant was deleted with the console
preamble by this quick task, so a future reader does not read the count change as a silent
shrink. Change nothing else -- `test_non_registry_still_has_no_ops` and the count test both
stay as they are.

**4d. `tools/check_diagnostic_report_claims.py`.** Prose only: the "Scope note" paragraph
claims the two `cli_handlers.py` recovery constants "already have their own committed, scoped
gate (`tests/test_sdp_recovery_wording.py`)". Both are now gone. Rewrite that paragraph to
say the scan target is still exactly `diagnostic_report.py`, and that the console prose it
used to point at was removed by this task along with its gate, so there is no longer a second
surface to defer to. Touch no regex, no constant and no control flow.

**4e. Prove the suite.** Run the full app suite plus every gate. Fix any remaining fallout
by applying the disposition table's reasoning -- retarget at the payload, or delete a test
whose only claim was the removed console text. If anything red is neither of those, STOP and
report it rather than editing the assertion.
  </action>
  <verify>
    <automated>cd /workspaces/firestarter_app && python -m pytest tests/ -o addopts="" -q 2>&1 | tail -15</automated>
    <automated>cd /workspaces/firestarter_app && python -m pytest tests/test_dev_test_cmd.py tests/test_op_registration_parity.py tests/test_check_devtest_orchestrator.py tests/test_check_diagnostic_report_claims.py -q</automated>
    <automated>cd /workspaces/firestarter_app && python -c 'import os; assert not os.path.exists("tests/test_sdp_recovery_wording.py"), "the wording gate file must be deleted, not emptied"'</automated>
    <automated>cd /workspaces/firestarter_app && python tools/check_devtest_orchestrator.py && python tools/check_diagnostic_report_claims.py</automated>
    <automated>cd /workspaces/firestarter_app && ruff check firestarter/ tests/ tools/ && ruff format --check firestarter/ tests/ && python tools/check_mypy_watermark.py</automated>
    <automated>cd /workspaces/firestarter_app && git status --porcelain && git log --oneline -4</automated>
  </verify>
  <done>The full suite passes locally on Python 3.12 with no skips introduced by this change; every row of the disposition table is applied; the wording-gate file is deleted from disk; the new regression test proves both halves (console trimmed, JSON payload intact); ruff, ruff-format and the mypy watermark gate are green; all four commits are on `quick-devtest-output-trim` inside `firestarter_app` and the working tree is clean.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
| --- | --- |
| tester console -> filed GitHub issue | `dev test` output a stranger reads, and the report body this change stops echoing but still files |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
| --- | --- | --- | --- | --- | --- |
| T-spg-01 | Information disclosure | `submit_report`'s removed body echoes | low | mitigate | Removing an echo can only reduce disclosure. The sanitizer stays on the path that matters: `sanitize_dict` -> `build_body` is untouched and still runs before `gh`, the browser tier and `build_issue_url`; `tests/test_submit.py`'s `test_tty_body_sent_to_gh_is_sanitized` / `test_tty_body_sent_to_browser_is_sanitized` / `test_comment_body_sent_is_sanitized` stay green in Task 3. |
| T-spg-02 | Repudiation | trimmed console rows | medium | mitigate | A tester could otherwise lose evidence they used to read on screen. Mitigated by keeping the payload whole: `to_dict()` unchanged, both artifacts unchanged, the printed `Report written to <path>` line unchanged, and Task 4's regression test asserting the removed rows' data is still in the saved JSON. |
| T-spg-03 | Tampering | none | low | accept | No dependency, install step or package-manager invocation is added by this task, so no package-legitimacy surface exists here. |
</threat_model>

<verification>
1. `cd /workspaces/firestarter_app && python -m pytest tests/ -o addopts="" -q` -- full suite green (Python 3.12 local; CI's 3.11 leg unproven, state it that way).
2. `ruff check firestarter/ tests/ tools/`, `ruff format --check firestarter/ tests/`, `python tools/check_mypy_watermark.py` -- all green.
3. `python tools/check_devtest_orchestrator.py` and `python tools/check_diagnostic_report_claims.py` -- both `PASS`.
4. `python -c 'from click.testing import CliRunner; from firestarter.cli_handlers import cli; r = CliRunner().invoke(cli, ["dev", "test", "--help"]); print(r.output)'` -- eyeball the help: short, no design history.
5. `git -C /workspaces/firestarter_app log --oneline -4` -- four task commits on `quick-devtest-output-trim`; `git status --porcelain` clean; the meta-repo gitlink deliberately NOT bumped.
</verification>

<success_criteria>
- `dev test --help` is at most 14 rendered lines and reads as usage documentation, not history.
- The moved design-history prose is still in `cli_handlers.py` and still greppable.
- A run prints no preamble and no recovery/restore line; it still prints the result table, the saved-report path, the submit prompts and any filed URL.
- The result table: hex protocol (2 digits), hex chip IDs (4 digits, both sides, `None`-safe), verdict-only step rows, no transport/submittable/db_diff rows, no prose.
- The issue body is never echoed; it is still built, sanitized, URL-encoded and filed unchanged.
- `to_dict()`, `to_json_block()`, both saved artifacts, `is_submittable`'s submit gate, the exit codes and the `write-restored` sweep step are all unchanged.
- Every affected test/tool has a recorded disposition; the only deleted test file is the pure wording gate; no data invariant was weakened.
- Full suite plus ruff/format/mypy-watermark green locally, reported as local-3.12 only.
</success_criteria>

<output>
Create `.planning/quick/260821-spg-trim-dev-test-console-output-shorter-hel/260821-spg-SUMMARY.md` when done.

Record in it: the stated assumption above and whether anything challenged it; the final
`--help` text; the exact disposition applied to each test/tool row (and any row where
execution found the measurement wrong); the local-only nature of the green gate run; and the
fact that the meta-repo gitlink was intentionally left for the operator.
</output>
