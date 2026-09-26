---
phase: quick-260822-gxx
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - firestarter_app/firestarter/submit.py
  - firestarter_app/firestarter/cli_handlers.py
  - firestarter_app/tests/test_submit.py
  - firestarter_app/tests/test_dev_test_cmd.py
commits_land_in: firestarter_app
autonomous: true
requirements: []
must_haves:
  truths:
    - "A step row whose verdict is NA renders `-` in the Reason column of the filed GitHub issue body table."
    - "A step row whose verdict is NA renders `-` in the Reason column of the saved `~/.firestarter/reports/dev-test-<chip>.md` table."
    - "A step row whose verdict is SKIPPED still renders its reason verbatim in BOTH markdown tables."
    - "The fenced JSON block and the saved `dev-test-<chip>.json` still carry every step's full `reason` string verbatim, including the suppressed SDP prose."
    - "The rule is keyed on the verdict token, not on a match against the SDP message text or a per-op special case."
  artifacts:
    - "firestarter_app/firestarter/submit.py::_reason_text — the single shared formatter"
    - "firestarter_app/tests/test_submit.py — unit coverage of _reason_text + build_body"
    - "firestarter_app/tests/test_dev_test_cmd.py — end-to-end coverage of the saved .md artifact"
  key_links:
    - "cli_handlers.py's md_lines loop imports _reason_text FROM submit (never re-implements the rule) — the same single-source pattern already used for _duration_text / _runs_text."
    - "submit.py reads VERDICT_NA from firestarter.chip_test rather than hardcoding a bare \"NA\" literal."
    - "The D-2 guard test asserts sdp_capability.REASON_WRONG_PROTOCOL is ABSENT from the table half of the body and PRESENT in the JSON half of the same body string."
---

<objective>
`dev test` attaches `sdp_capability.REASON_WRONG_PROTOCOL` to all six `sdp-*` NA
steps, so a filed W27C512 report repeats "SDP lock/unlock applies only to
protocol 0x0D parallel EEPROMs (observed protocol 0x07)" six times down the
Reason column. The operator's ruling: **"NA is enough."**

Suppress the Reason cell on every `NA`-verdict row in both markdown tables via
ONE shared formatter in `submit.py`. Render-layer only.

Purpose: a filed issue's results table reads as a verdict summary, not six
copies of one disclaimer.
Output: `submit._reason_text`, both call sites wired to it, and tests that pin
the new rendering, the SKIPPED exemption, and the JSON-retention guard.
</objective>

<execution_context>
@/workspaces/.claude/gsd-core/workflows/execute-plan.md
@/workspaces/.claude/gsd-core/templates/summary.md
</execution_context>

<context>
@/workspaces/CLAUDE.md
@/workspaces/firestarter_app/CLAUDE.md
@/workspaces/firestarter_app/firestarter/submit.py
@/workspaces/firestarter_app/firestarter/cli_handlers.py
</context>

<locked_decisions>
Settled with the operator before planning. Do not revisit or widen.

**D-1 — Suppression is keyed on the verdict, and covers ALL NA rows.**
Any step whose verdict is `NA` renders `-` in the Reason column. NOT a match on
the SDP message text; NOT a per-op special case. It also silences e.g.
"FLAG_CAN_ERASE not set for this chip" and the flash4 blank-check prose — that
is intended. `SKIPPED` rows are **NOT** affected: a SKIPPED reason is frequently
the real disclosure ("no target resolved") and must keep rendering.

**D-2 — The fenced JSON block is untouched.**
`DiagnosticReport.to_dict()` keeps every step's full `reason`. Both
`dev-test-<chip>.json` and the fenced JSON block inside the issue body keep
carrying it verbatim. Do **not** alter `to_dict()`, `_step_dict()`,
`derive_plan`, `sdp_capability.py`, or any reason constant. The SUB-02
invariant — the markdown table and the JSON block derive from the SAME
sanitized dict — must survive.

**D-3 — Both markdown tables change; the console is EXEMPT.**
Verified during planning at `firestarter/diagnostic_report.py:938-939`:

    for step_row in d["steps"]:
        if step_row["verdict"] not in _RAN_VERDICTS:
            continue

`_RAN_VERDICTS` is `frozenset({VERDICT_OK, VERDICT_BAD, VERDICT_MARGINAL})`
(`chip_test.py:3742`). An `NA` row is never emitted as a console step row at
all, so there is no Reason cell there to suppress. **`diagnostic_report.py`
gets ZERO edits in this plan.** Confirmed — the operator's read is correct.
</locked_decisions>

<planning_findings>
Established by reading the source before writing this plan. Trust these; do not
re-derive them.

1. **`submit.py` may import `firestarter.chip_test` without breaching SAFE-02.**
   `submit.py` already does `from firestarter.diagnostic_report import
   is_submittable` at module level, and `diagnostic_report.py:49` already does
   `from firestarter.chip_test import (_RAN_VERDICTS, ...)`. So `chip_test` is
   ALREADY in submit's transitive import graph. `chip_test`'s own module-level
   `firestarter` imports are exactly `sdp_honesty`, `chip_resolver`,
   `constants`, `exceptions`, `sdp_capability` — no serial-transport class, no
   hardware-manager class. Neither `chip_test` nor `diagnostic_report` imports
   `submit`, so there is no cycle. **Use `from firestarter.chip_test import
   VERDICT_NA`** (defined at `chip_test.py:1082`); do not hardcode `"NA"`.

2. **Both call sites confirmed.**
   - `submit.py:214-251` `build_body` — reads dicts: `step.get("reason") or "-"`
     on the line inside the `for step in sanitized_dict.get("steps", [])` loop.
   - `cli_handlers.py:2644-2663` — reads `StepResult` attributes:
     `f"| {r.op} | {r.verdict} | {runs} | {took} | {r.reason or '-'} |"`.
   Hence the helper must take plain values, not an object.

3. **The established single-source pattern is a function-local aliased import.**
   `cli_handlers.py:2642-2643` does
   `from firestarter.submit import _duration_text as submit_duration_text`
   inside the `dev_test` body, with a comment explaining the local-import
   choice. Its own comment states the intent: *"both formatters are imported
   from `submit` rather than re-implemented, so the two tables can never
   disagree on how an absent value renders."* Follow it exactly.

4. **Keep the `submit_`-prefixed alias.** `tools/check_devtest_orchestrator.py`
   GATE-10 walks `dev_test`'s body statements and intersects every referenced
   `Name`/`Attribute` with the set of **module-level `_`-prefixed functions
   defined in `cli_handlers.py`**, asserting that set is a subset of
   `_HANDLER_FUNCTION_NAMES`. `_reason_text` lives in `submit.py`, so an
   unaliased import would not actually trip it today — but aliasing matches the
   two existing imports and keeps the gate's blast radius at zero.

5. **`_skip_result` sets `run_count=0`** (`chip_test.py:1305`) and leaves
   `duration_s=None`. `_runs_text(0)` returns `"-"` and `_duration_text(None)`
   returns `"-"`. So a rendered NA row is exactly
   `| <op> | NA | - | - | - |` after this change — assert that literal row.

6. **No downstream parser reads the Reason column.**
   `grep -n "reason" tools/parse_devtest_issue.py` returns nothing; the parser
   consumes only the fenced JSON block. Suppression degrades no triage tooling.

7. **Existing tests that touch this surface (all currently green, 94 passed in
   `tests/test_submit.py`):**
   - `tests/test_submit.py:201` `test_build_body_table_from_sanitized_steps` —
     asserts `"| erase | NA | - | - | - |"`. That fixture's NA step already has
     `reason: ""`, so this assertion survives the change unchanged. It is
     therefore NOT a proof of the new behaviour; a new NA row carrying real
     prose must be added (Task 1).
   - `tests/test_dev_test_cmd.py:927` — asserts the `.md` header row only.
   - `tests/test_dev_test_cmd.py:1995`
     `test_r4_refuse_chip_na_reason_matches_sdp_capability_identity` — asserts
     `data["steps"]["write-inhibited"]["reason"] == sdp_capability(...)[1]` in
     the saved **JSON**. This is an existing D-2 guard on the `.json` artifact
     and must stay green untouched.
   - `tests/test_chip_test_sdp_leg.py` NA parametrizations are engine-level
     (`sdp_hold_state`, `_baseline_closes_sdp_gate`) — unaffected.
   - `tests/__snapshots__/test_characterization.ambr` contains zero occurrences
     of `Reason` — no snapshot to regenerate.

8. **`_CHIP_NO_ID` is the ready-made end-to-end fixture.** It is a REFUSE chip
   (`sdp_capability(...) -> (False, reason)`) whose `write-inhibited` step lands
   `NA` carrying that reason. `tests/test_dev_test_cmd.py` already imports
   `sdp_capability` and `_REAL_DB` and already has `_reports_dir()`.

9. **Gates that must stay green:** `python tools/check_devtest_orchestrator.py`
   full-scans `submit.py` and scopes-scans `dev_test` in `cli_handlers.py`
   (baseline: `PASS ... 0 VPP-set, 0 raw-wire-dict, 0 --force, 0 broad-except`).
   `tools/check_diagnostic_report_claims.py` scans ONLY
   `diagnostic_report.py` — untouched here.
   mypy strict-island includes `cli_handlers` but not `submit`; annotate the new
   helper anyway to match `_duration_text`'s existing `(seconds: Any) -> str`
   shape. ruff `select = ["E","F","I","UP"]`, line-length 88, double quotes;
   isort orders `chip_test` before `diagnostic_report`.
</planning_findings>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Add the shared `_reason_text` formatter and wire `build_body`</name>
  <files>firestarter_app/firestarter/submit.py, firestarter_app/tests/test_submit.py</files>
  <behavior>
    `_reason_text(verdict, reason)`:
    - verdict `"NA"`, reason a non-empty prose string -> `"-"`
    - verdict `"NA"`, reason `""` -> `"-"`
    - verdict `"NA"`, reason `None` -> `"-"`
    - verdict `"SKIPPED"`, reason `"no target resolved"` -> `"no target resolved"`
    - verdict `"BAD"`, reason `"port gone"` -> `"port gone"`
    - verdict `"OK"`, reason `""` -> `"-"`
    - verdict `None`/missing, reason `""` -> `"-"`
    `build_body` with an `NA` step carrying prose and a `SKIPPED` step carrying
    prose: the table half suppresses only the NA one; the fenced JSON half
    carries both verbatim.
  </behavior>
  <action>
Per D-1 and D-2, both render-layer only.

In `firestarter_app/firestarter/submit.py`:

1. Add `from firestarter.chip_test import VERDICT_NA` to the module-level
   firestarter import group, ordered BEFORE the existing
   `from firestarter.diagnostic_report import is_submittable` (isort "I").
   Do not add any other new import. See planning finding 1 for why this does
   not breach the module's ORCHESTRATOR-ONLY (SAFE-02) invariant — restate that
   justification briefly in a comment on the import line so a future reader does
   not "fix" it: chip_test is already transitively present via
   `diagnostic_report`, and it imports no serial-transport or hardware-manager
   class.

2. Define `_reason_text(verdict: Any, reason: Any) -> str` immediately after
   `_runs_text` and before `build_body`. It returns `"-"` when
   `verdict == VERDICT_NA`, otherwise returns `str(reason)` when `reason` is
   truthy, otherwise `"-"`. Keep the existing `or "-"` absent-value contract for
   every non-NA verdict — this function is a strict superset of the behaviour it
   replaces.

   Its docstring must state the rule keyed on the VERDICT and must state, in
   prose, that SKIPPED deliberately keeps its reason because a SKIPPED reason is
   frequently the real disclosure, and that the caller's fenced JSON block still
   carries the full string. Cite the operator ruling ("NA is enough", quick task
   260822-gxx). Do NOT quote the SDP message text anywhere in the docstring or
   any comment in this file.

3. In `build_body`, replace `reason = step.get("reason") or "-"` with a call to
   `_reason_text(step.get("verdict"), step.get("reason"))`. Change nothing else
   in `build_body` — the column set, the row f-string shape and the
   `include_json` behaviour all stay byte-identical in intent.

4. Extend `build_body`'s docstring with one short paragraph naming the NA
   suppression and pointing at `_reason_text`.

In `firestarter_app/tests/test_submit.py`:

5. Add a parametrized unit test over `submit._reason_text` covering all seven
   behaviour rows above. The SKIPPED and BAD rows are the non-vacuity proof that
   the rule is verdict-keyed and not blanket suppression — do not omit them.

6. Add `test_build_body_na_row_suppresses_reason_json_retains_it`. Import
   `REASON_WRONG_PROTOCOL` from `firestarter.sdp_capability` and build the NA
   step's reason FROM that constant (never a re-worded copy — this project's
   existing R4 test compares against the live source by identity for the same
   reason). Build a sanitized dict with an `sdp-lock` NA step carrying that
   prose and a `read` SKIPPED step carrying `"no target resolved"`, call
   `submit.build_body(sanitized, [], include_json=True)`, then split the result
   on `"```json"` into a table half and a json half and assert:
     - `"| sdp-lock | NA | - | - | - |"` is in the table half
     - `"| read | SKIPPED | - | - | no target resolved |"` is in the table half
     - `REASON_WRONG_PROTOCOL` is NOT in the table half
     - `REASON_WRONG_PROTOCOL` IS in the json half   <- the D-2 guard
   The last two assertions are the load-bearing pair; write them with messages
   naming D-1 and D-2 respectively.

7. Leave `test_build_body_table_from_sanitized_steps` (line ~201) as is — its NA
   step has an empty reason and renders `-` before and after. Do not weaken or
   delete it.

Do NOT touch `to_dict()`, `_step_dict()`, `derive_plan`, `sdp_capability.py`,
`diagnostic_report.py`, or any reason constant.
  </action>
  <verify>
    <automated>cd /workspaces/firestarter_app && python -m pytest tests/test_submit.py -o addopts="" -q</automated>
    <automated>cd /workspaces/firestarter_app && python -c "from firestarter.submit import _reason_text; assert _reason_text('NA','x')=='-'; assert _reason_text('SKIPPED','no target resolved')=='no target resolved'; assert _reason_text('OK','')=='-'; print('OK')"</automated>
    <automated>cd /workspaces/firestarter_app && grep -n 'def _reason_text' firestarter/submit.py && grep -c 'VERDICT_NA' firestarter/submit.py</automated>
  </verify>
  <done>`submit._reason_text` exists, is imported-from-source keyed on `VERDICT_NA`, `build_body` calls it, the parametrized unit test and the NA/SKIPPED/JSON-retention test pass, and every pre-existing test in `tests/test_submit.py` still passes (baseline was 94 passed).</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Wire the saved `dev-test-<chip>.md` table to the same helper</name>
  <files>firestarter_app/firestarter/cli_handlers.py, firestarter_app/tests/test_dev_test_cmd.py</files>
  <behavior>
    A full `dev test _CHIP_NO_ID` run writes `dev-test-<chip>.md` whose
    `write-inhibited` row is `| write-inhibited | NA | - | - | - |`, while the
    fenced JSON block in the SAME file still carries
    `sdp_capability(_CHIP_NO_ID, _REAL_DB)[1]` verbatim.
  </behavior>
  <action>
Per D-1 and D-3.

In `firestarter_app/firestarter/cli_handlers.py`, inside the `dev_test` handler
body at the existing local-import block (~line 2645):

1. Add a third aliased local import alongside the two that are already there:
   `from firestarter.submit import _reason_text as submit_reason_text`.
   Keep the `submit_` alias prefix — see planning finding 4.

2. In the `for r in results:` loop, replace `{r.reason or '-'}` in the row
   f-string with a `reason = submit_reason_text(r.verdict, r.reason)` local
   computed alongside the existing `took` / `runs` locals, and interpolate
   `{reason}`.

3. Extend the existing block comment above `took` so it covers the third
   formatter, keeping its established framing: the rule is imported from
   `submit` rather than re-implemented so the two tables can never disagree.
   Add one clause recording that the console needs no equivalent because
   `DiagnosticReport.render()` already drops non-`_RAN_VERDICTS` rows entirely
   (D-3). Do not quote the SDP message text in this comment.

Leave everything else in `dev_test` untouched — no reordering, no new
module-level import, no change to the `.json` write above it.

In `firestarter_app/tests/test_dev_test_cmd.py`:

4. Add `test_md_artifact_na_row_suppresses_reason_json_retains_it` to the same
   class that holds `test_md_artifact_contains_fenced_json_block` (~line 912),
   reusing that test's `make_app_context` / `make_clean_operator` /
   `make_hardware_manager` / `_off_tty()` setup verbatim and the existing
   `_reports_dir()` helper. `sdp_capability` and `_REAL_DB` are already imported
   in this module.

   Invoke `["dev", "test", _CHIP_NO_ID]`, assert `result.exit_code == 0`, read
   `dev-test-{_CHIP_NO_ID}.md`, resolve
   `allowed, expected_reason = sdp_capability(_CHIP_NO_ID, _REAL_DB)`, assert
   `allowed is False` as a fixture-setup guard, then split the file on
   `"```json"` and assert:
     - `"| write-inhibited | NA | - | - | - |"` is in the table half
       (planning finding 5 establishes both the `-` Runs and `-` Took cells:
       `_skip_result` sets `run_count=0` and leaves `duration_s=None`)
     - `expected_reason` is NOT in the table half            <- D-1
     - `expected_reason` IS in the json half                 <- D-2
   Give each of the last two assertions a failure message naming its decision.

5. Do not modify `test_md_artifact_contains_fenced_json_block` or
   `test_r4_refuse_chip_na_reason_matches_sdp_capability_identity` — the latter
   is the pre-existing D-2 guard on the `.json` artifact and must stay green
   untouched as written.
  </action>
  <verify>
    <automated>cd /workspaces/firestarter_app && python -m pytest tests/test_dev_test_cmd.py -o addopts="" -q</automated>
    <automated>cd /workspaces/firestarter_app && python -m pytest tests/test_dev_test_cmd.py -o addopts="" -q -k "md_artifact or r4_refuse_chip_na_reason"</automated>
    <automated>cd /workspaces/firestarter_app && grep -c "submit_reason_text" firestarter/cli_handlers.py | grep -qx 2 && echo "both import and call site present"</automated>
    <automated>cd /workspaces/firestarter_app && test -z "$(git diff --name-only -- firestarter/diagnostic_report.py firestarter/chip_test.py firestarter/sdp_capability.py)" && echo "D-2/D-3 untouched-files guard OK"</automated>
  </verify>
  <done>The saved `.md` NA row renders `-` for its reason while the same file's JSON block keeps the full prose; `tests/test_dev_test_cmd.py` passes in full; `diagnostic_report.py`, `chip_test.py` and `sdp_capability.py` show no diff.</done>
</task>

<task type="auto">
  <name>Task 3: Run the full gate set and commit inside the submodule</name>
  <files>firestarter_app/ (commit only — no new source edits beyond gate fixes)</files>
  <action>
1. Confirm the working branch: `cd /workspaces/firestarter_app` and verify
   `git branch --show-current` prints `quick-devtest-na-reason`. If it does not,
   STOP and report — do not create or switch branches.

2. Run the whole gate set from `/workspaces/firestarter_app`:
   - `ruff check .` and `ruff format --check .`
   - `mypy` over the strict-island list (at minimum `firestarter/cli_handlers.py`)
   - `python tools/check_devtest_orchestrator.py` — must still print a `PASS:`
     line naming all three scanned files with `0 VPP-set, 0 raw-wire-dict,
     0 --force, 0 broad-except`
   - the full `python -m pytest tests/ -o addopts="" -q`

3. If any gate is red, fix the code — never weaken an assertion into vacuity and
   never delete a test to make a gate pass. If a red gate cannot be fixed inside
   this plan's four files, STOP and report rather than widening scope.

4. Commit ONLY inside the submodule, from `/workspaces/firestarter_app`. Stage
   exactly the four changed files by path — the submodule working tree carries
   unrelated untracked files (`SECURITY.md`, `datasheets/*.pdf`,
   `write_test_port.sh`, `.planning/config.json`) that must NOT be swept in, so
   do not use `git add -A` or `git commit -a`:

       git add firestarter/submit.py firestarter/cli_handlers.py \
               tests/test_submit.py tests/test_dev_test_cmd.py
       git commit -m "fix(dev-test): suppress the Reason cell on NA-verdict rows"

   Verify with `git show --stat --name-only HEAD` that exactly those four paths
   landed.

5. Do NOT commit anything from `/workspaces` (the meta repo). Do NOT stage the
   submodule gitlink. Do NOT write or commit PLAN.md / SUMMARY.md / STATE.md —
   the orchestrator owns the docs commit. Do NOT touch ROADMAP.md.
  </action>
  <verify>
    <automated>cd /workspaces/firestarter_app && ruff check . && ruff format --check .</automated>
    <automated>cd /workspaces/firestarter_app && python tools/check_devtest_orchestrator.py</automated>
    <automated>cd /workspaces/firestarter_app && python -m pytest tests/ -o addopts="" -q</automated>
    <automated>cd /workspaces/firestarter_app && git show --stat --name-only HEAD | grep -E 'submit\.py|cli_handlers\.py|test_submit\.py|test_dev_test_cmd\.py' | wc -l | grep -qx 4 && echo "exactly the 4 intended files committed"</automated>
    <automated>cd /workspaces/firestarter_app && git branch --show-current | grep -qx quick-devtest-na-reason && echo "on the right branch"</automated>
  </verify>
  <done>ruff, mypy, the orchestrator gate and the full pytest suite are green; one commit exists on `quick-devtest-na-reason` inside `firestarter_app` touching exactly the four intended files; the meta repo has no source commit.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| host -> public GitHub issue | `build_body` output is published verbatim to a public tracker; anything it drops is invisible to a triager reading the rendered table. |
| host -> local report artifact | `dev-test-<chip>.md` / `.json` under `$FIRESTARTER_CONFIG_DIR/reports`. |

No new trust boundary is introduced: this plan adds one pure string formatter
and changes no wire command, no VPP value, no filesystem path and no network
call. `submit.py` remains ORCHESTRATOR-ONLY (SAFE-02) — planning finding 1
records why the one new import does not breach it.

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-gxx-01 | Information disclosure (loss of evidence) | `submit._reason_text` | medium | mitigate | Suppression is render-layer only; D-2 keeps the full `reason` in `to_dict()`, the `.json` artifact and the fenced JSON block. Task 1 step 6 and Task 2 step 4 each assert the prose is PRESENT in the JSON half of the very same string whose table half omits it. |
| T-gxx-02 | Tampering (over-broad suppression) | `_reason_text` verdict predicate | medium | mitigate | The predicate is `verdict == VERDICT_NA` read from `chip_test`, never a substring match on message text. The parametrized SKIPPED and BAD rows in Task 1 step 5, plus the SKIPPED table assertion in step 6, are the non-vacuity proof that non-NA reasons still render. |
| T-gxx-03 | Repudiation (unattributable report) | downstream triage tooling | low | accept | `tools/parse_devtest_issue.py` reads only the fenced JSON block — `grep -n "reason"` over it returns nothing (planning finding 6) — so no automated consumer loses a field. |
| T-gxx-SC | Tampering | npm/pip/cargo installs | n/a | accept | No package install task in this plan; no dependency is added or upgraded. The Package Legitimacy Gate does not apply. |
</threat_model>

<verification>
- `python -m pytest tests/ -o addopts="" -q` green from `/workspaces/firestarter_app`.
- `ruff check .`, `ruff format --check .`, mypy strict-island, and
  `python tools/check_devtest_orchestrator.py` all green.
- `git diff --name-only origin/beta...HEAD` inside `firestarter_app` lists
  exactly `firestarter/submit.py`, `firestarter/cli_handlers.py`,
  `tests/test_submit.py`, `tests/test_dev_test_cmd.py`.
- `firestarter/diagnostic_report.py` shows a zero-byte diff (D-3, console exempt).
- `firestarter/chip_test.py` and `firestarter/sdp_capability.py` show a zero-byte
  diff (D-2, model layer untouched).
</verification>

<success_criteria>
- An `NA` row in the filed issue body table renders `-` in the Reason column.
- An `NA` row in `dev-test-<chip>.md` renders `-` in the Reason column.
- A `SKIPPED` row still renders its reason in both tables, proven by test.
- `sdp_capability.REASON_WRONG_PROTOCOL` still appears in the fenced JSON block
  of both artifacts, proven by test in each of the two renderers.
- The rule lives in exactly ONE function. `cli_handlers.py` already contains 2
  pre-existing occurrences of the NA verdict constant (unrelated exit-code
  wiring); that count must stay at 2 — the handler calls the helper and adds no
  new verdict predicate of its own:
  `grep -c VERDICT_NA firestarter/cli_handlers.py` returns `2`.
- One commit on `quick-devtest-na-reason` inside the `firestarter_app`
  submodule; the meta repo carries no source commit.
</success_criteria>

<output>
Create `.planning/quick/260822-gxx-dev-test-suppress-the-reason-cell-on-na-/260822-gxx-SUMMARY.md` when done
</output>
</content>
</invoke>
