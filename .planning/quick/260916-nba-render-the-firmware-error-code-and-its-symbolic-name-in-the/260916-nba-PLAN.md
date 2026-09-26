---
phase: quick-260916-nba
plan: 01
type: execute
wave: 2
depends_on: [260916-nb9]
files_modified:
  - firestarter_app/firestarter/submit.py
  - firestarter_app/firestarter/cli_handlers.py
  - firestarter_app/tests/test_submit.py
  - firestarter_app/tests/test_dev_test_cmd.py
autonomous: true
requirements: [260916-nba]

estimate:
  tokens: 35000
  raw_tokens: 70000
  tasks: 2
  confidence: high

must_haves:
  truths:
    - "A triager reading the markdown step table of a filed `dev test` issue sees the firmware message id AND its symbolic name for every failing step, without unfolding the fenced JSON block and without opening the firmware source."
    - "The saved `dev-test-<chip>.md` artifact and the filed issue body render the identical Error cell for the identical step — neither table can drift from the other, because both call the SAME formatter in `submit.py`."
    - "A report in which no step carries an error code renders a table byte-identical to today's: no Error column, no column of empty placeholders."
    - "An `NA` verdict renders `-` in the Error column, exactly as it already renders `-` in the Reason column."
    - "A `SKIPPED` verdict still shows its code — the UV pre-write blank-check is adjudicated SKIPPED precisely so its `MSG_ERR_NOT_BLANK` finding survives, and suppressing it here would destroy the disclosure that step exists to make."
    - "A message id absent from the catalog renders the bare integer and never raises; a null or non-integer code renders `-` and never raises."
    - "Nothing about the fenced JSON block, the `.json` artifact, or the rich console table changes."
    - "No name-to-id table is hand-written anywhere in this change: the name comes from the resolution 260916-nb9 added, or failing that from the one canonical `firestarter.messages` catalog that `codec.py` and `serial_comm.py` already read."
  artifacts:
    - firestarter_app/firestarter/submit.py
    - firestarter_app/firestarter/cli_handlers.py
    - firestarter_app/tests/test_submit.py
    - firestarter_app/tests/test_dev_test_cmd.py
  key_links:
    - "`submit._error_text` -> BOTH markdown tables (`submit.build_body` for the filed issue body, `cli_handlers` for the saved `.md` artifact) — the single seam that keeps the two renderings in lockstep, exactly as `_duration_text`/`_runs_text`/`_reason_text` already do"
    - "`StepResult.error_code` -> `diagnostic_report._step_dict` -> `submit.sanitize_dict` -> the rendered cell (the value crosses the scrubber before it reaches a public issue body)"
    - "`firestarter.messages.CATALOG` -> the resolved symbolic name (the generated, meta-repo-owned catalog is the ONLY id-to-name authority)"
---

<objective>
Add the firmware error code and its symbolic name to the human-readable markdown step
table of a `dev test` report, so a triager opening issue #86 reads `MSG_ERR_OP_TIMEOUT
(183)` on the failing `write` row instead of having to unfold the fenced JSON block and
then grep the firmware source for `183`.

**Scope correction (state it in the SUMMARY).** The batch item names
`firestarter_app/firestarter/chip_test.py` as the scope. That file holds only the
`StepResult.error_code` dataclass field (line 1085) — it renders no table. The markdown
step table is rendered in exactly two places, and this plan changes both:

- `firestarter_app/firestarter/submit.py::build_body` — the issue body that gets filed
  or pasted, rendered from `sanitized_dict["steps"]` (plain dicts).
- `firestarter_app/firestarter/cli_handlers.py` (the `dev test` handler, around the
  `md_lines` list) — the saved `dev-test-<chip>.md` artifact, rendered from the live
  `StepResult` objects.

Both already import `_duration_text`, `_runs_text` and `_reason_text` from `submit.py`
rather than re-implementing them, for the stated reason that the two tables must never
disagree on how an absent value renders. The new formatter joins that set. No new
rendering logic is written in `cli_handlers.py`.

**Column shape.** `| Step | Verdict | Runs | Took | Error | Reason |` — the new fixed-width
column sits between `Took` and `Reason` so the variable-length prose cell stays last.

**Column presence.** The Error column is emitted only when at least one row in that table
would render a non-`-` cell. A passing report therefore keeps today's exact table, which is
both what "keep the table readable when no step has an error code" asks for and what keeps
every existing table assertion green.

**Cell format.** `MSG_ERR_OP_TIMEOUT (183)` when the name resolves; the bare `183` when the
id is not in the catalog; `-` when there is no code or the verdict is `NA`.

**Name resolution.** Sibling item 260916-nb9 lands first (this plan's `depends_on`) and
exposes a resolved `error_name` on the report JSON. Prefer that value when the caller has
it. Where it is absent — the `StepResult` objects `cli_handlers` iterates, and any report
predating nb9 — resolve through the ONE canonical authority, `firestarter.messages.CATALOG`
(`CATALOG[0xB7].name == "MSG_ERR_OP_TIMEOUT"`), which `codec.py` and `serial_comm.py`
already read. Do not hand-write a second id-to-name table anywhere.

Purpose: the single most useful datum in a `dev test` failure currently reaches the public
issue only inside a JSON block nobody unfolds.
Output: two changed product modules, two changed test modules, no schema change.
</objective>

<execution_context>
@/workspaces/.claude/gsd-core/workflows/execute-plan.md
@/workspaces/.claude/gsd-core/templates/summary.md
</execution_context>

<context>
@CLAUDE.md
@firestarter_app/CLAUDE.md
@firestarter_app/firestarter/submit.py
@firestarter_app/tests/test_submit.py
@firestarter_app/tests/test_devtest_firmware_error_propagation.py
</context>

<tasks>

<task type="tracer" tdd="true">
  <name>Task 1: One failing step's code and name reach BOTH markdown tables, end to end</name>
  <files>firestarter_app/firestarter/submit.py, firestarter_app/firestarter/cli_handlers.py, firestarter_app/tests/test_submit.py, firestarter_app/tests/test_dev_test_cmd.py</files>
  <precondition>The `firestarter_app` submodule working tree is populated (`firestarter_app/firestarter/submit.py` is readable) and checked out on branch `v1.39-protocol-0x05-write-correctness`, and `firestarter_app/.venv311/bin/python -V` reports Python 3.11 with the package installed via `pip install -e '.[test]'` — CI runs 3.11 only and the devcontainer's default 3.12 masks 3.11 failures. Halt and report if either is unmet.</precondition>
  <read_first>
    `firestarter_app/firestarter/submit.py` — `_duration_text`, `_runs_text`, `_reason_text`
    and `build_body`. These three formatters are the shape the new one copies: a single
    argument-tolerant function that returns a non-empty placeholder for an absent value,
    with `_reason_text` keyed on the VERDICT rather than on the payload. `VERDICT_NA` is
    already imported at module level from `firestarter.chip_test`; so is the rest of that
    module's chip_test surface, and `chip_test` does not import `submit`, so a module-level
    import from `chip_test` here introduces no cycle.

    `firestarter_app/firestarter/cli_handlers.py` — the `dev test` handler's `md_lines`
    construction and the three local `from firestarter.submit import ...` lines feeding it.

    `firestarter_app/tests/test_devtest_firmware_error_propagation.py` — `_failing_operator`
    (sets `last_firmware_error_code` on a `Mock(spec=EpromOperator)`) is the reference shape
    for a double that produces a real coded failure.

    `firestarter_app/firestarter/messages.py` — `CATALOG: dict[int, MessageDef]`, whose
    entries carry `.name`. Generated in the meta repo and synced; never edit it here.
  </read_first>
  <behavior>
    Write these as failing tests first, then implement.

    In `tests/test_submit.py`:
    - `_error_text("BAD", 183, None)` returns `MSG_ERR_OP_TIMEOUT (183)`.
    - `_error_text("OK", None, None)` returns `-`.
    - `_error_cells` over rows whose cells are all `-` returns `None` (the signal to omit
      the column); over rows where at least one cell is real it returns the full cell list.
    - `build_body` on a sanitized dict whose `write` step carries `error_code` 183 emits the
      header `| Step | Verdict | Runs | Took | Error | Reason |`, the matching separator row,
      and a `write` row whose fifth cell is `MSG_ERR_OP_TIMEOUT (183)`; every other cell on
      every row is unchanged from what it renders today.

    In `tests/test_dev_test_cmd.py`:
    - A `dev test` run whose blank-check fails with `last_firmware_error_code` set to 0xB0
      writes a `dev-test-<chip>.md` whose table carries `MSG_ERR_NOT_BLANK (176)` on that
      step's row. This is the end-to-end leg: operator failure, through `StepResult`,
      through the handler's table, onto disk.
  </behavior>
  <action>
    In `submit.py`, beside the existing three formatters, add two module-level functions.

    `_error_text(verdict, error_code, error_name=None)` returns the Error cell.
    Return `-` when `verdict` equals `VERDICT_NA`, mirroring `_reason_text`'s
    verdict-keyed suppression. Return `-` when `error_code` is `None` or cannot be coerced
    with `int()` — use the same tolerant try/except shape `_runs_text` and `_duration_text`
    already use, so a replayed or malformed report can never raise here. Otherwise resolve a
    display name: use `error_name` when the caller supplied a truthy one (this is the field
    260916-nb9 added to the report JSON); else look the coerced integer up in the single
    canonical catalog and take its `.name`. Before checking for nb9's helper, grep
    `firestarter/chip_test.py` for `error_name` and import the resolver nb9 landed if one is
    importable; if none is, call `firestarter.messages.CATALOG.get(code)` directly, which is
    the same authority nb9's own resolver reads. Under no circumstances author a second
    id-to-name mapping. With a name, return name then the DECIMAL code in parentheses — the
    decimal matches the `error_code` integer in the fenced JSON verbatim, so the two surfaces
    cross-reference without a base conversion. With no name, return the bare decimal code.

    `_error_cells(rows)` takes an iterable of `(verdict, error_code, error_name)` triples,
    maps each through `_error_text`, and returns the resulting list — or `None` when every
    cell in it is the absent placeholder. `None` is the single authority on whether either
    table emits the column, so the two tables cannot disagree about when the column appears.

    In `build_body`, build the triples from `sanitized_dict["steps"]` with `.get()` for all
    three keys (a pre-nb9 report has no `error_name` key and must not `KeyError`), call
    `_error_cells` once, and branch the header, the separator row and each data row on
    whether it returned `None`. When it returns `None`, the emitted header and rows must be
    character-identical to what the function emits today. Insert the cell between `Took` and
    `Reason`.

    In the `dev test` handler in `cli_handlers.py`, add `_error_text` and `_error_cells` to
    the existing local `from firestarter.submit import ...` group, build the triples from the
    `StepResult` objects using `r.verdict`, `r.error_code` and `getattr(r, "error_name", None)`
    — the `getattr` keeps this correct whether or not nb9 also put the field on the dataclass
    — and apply the identical header/separator/row branch. Do not re-derive any cell here.

    Leave `diagnostic_report.py` untouched: no schema field, no `SCHEMA_VERSION` change, no
    console-table change. That file's `to_dict` already exports `error_code`, and nb9 owns
    `error_name`.

    Write no comments into `firestarter_app` product source; this plan cannot override that
    project rule. Put the rationale for the column position, the omission rule and the
    NA-suppression choice in the SUMMARY and the commit message instead. Docstrings are not
    comments — give each new function one, in the register the neighbouring formatters use.
  </action>
  <reversibility rating="reversible">A render-only addition behind an omission rule; reverting restores the previous table exactly and touches no persisted schema.</reversibility>
  <verify>
    <automated>cd firestarter_app && ./.venv311/bin/python -m pytest tests/test_submit.py -q -o addopts="" && ./.venv311/bin/python -m pytest tests/test_dev_test_cmd.py -q -o addopts="" -k "error or md_artifact"</automated>
  </verify>
  <done>A sanitized report dict carrying `error_code` 183 on its `write` step renders a table whose header is `| Step | Verdict | Runs | Took | Error | Reason |` and whose `write` row carries `MSG_ERR_OP_TIMEOUT (183)`; a real `dev test` run against a blank-check failure writes a `dev-test-<chip>.md` carrying `MSG_ERR_NOT_BLANK (176)`; and the pre-existing table assertions in `tests/test_submit.py` and `tests/test_dev_test_cmd.py` still pass untouched, because their fixtures carry no codes and therefore get no column.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Pin the verdict policy, the degradation paths, and the untrusted-value hardening</name>
  <files>firestarter_app/firestarter/submit.py, firestarter_app/tests/test_submit.py</files>
  <read_first>
    `firestarter_app/firestarter/chip_test.py` around line 2650 — the docstring that explains
    why a non-blank UV part's pre-write blank-check is adjudicated `SKIPPED` rather than `NA`:
    `NA` is rejected precisely because `submit._reason_text` suppresses the Reason cell for
    `NA` only, "which would destroy the very finding this step exists to surface", and
    `SKIPPED` "preserves `reason` and `error_code` verbatim". That paragraph is the authority
    for this task's asymmetric suppression rule, and it must be cited in the SUMMARY.
  </read_first>
  <behavior>
    Write these as failing tests first, then implement. All in `tests/test_submit.py`,
    parametrized where the existing `_reason_text` tests are parametrized.

    Verdict policy:
    - `_error_text("NA", 183, None)` returns `-`. An NA row's Error cell is suppressed by the
      same rule that suppresses its Reason cell.
    - `_error_text("SKIPPED", 176, None)` returns `MSG_ERR_NOT_BLANK (176)`. A SKIPPED row is
      NOT suppressed — this pins the UV pre-write blank-check disclosure.
    - `_error_text("BAD", 175, None)` returns `MSG_ERR_VERIFY (175)` and
      `_error_text("BAD", 185, None)` returns `MSG_ERR_CHIP_ID_MISMATCH (185)` — the other two
      codes issue #86 actually carries.

    Degradation:
    - An id absent from the catalog returns the bare decimal string and does not raise.
      Assert inside the test that the chosen id is genuinely not a `CATALOG` key, so the test
      cannot silently decay into a resolvable-id test when the catalog grows.
    - A non-integer `error_code` (a string, a float that is not finite, an object) returns `-`
      and does not raise.
    - An explicitly supplied `error_name` wins over catalog resolution.

    Untrusted-value hardening:
    - An `error_name` containing a pipe character, a newline, or a carriage return renders a
      cell that contains none of those characters, so a replayed report cannot break out of
      its table cell or inject a row. Assert the rendered table still has exactly one row per
      step.
    - An `error_name` longer than the cap renders truncated to the cap.

    Column omission, at both tables:
    - `build_body` on a report where every step's cell is `-` emits a body containing
      `| Step | Verdict | Runs | Took | Reason |` and containing no `Error` header.
    - The same report's `include_json=True` body still carries the fenced JSON block with the
      `error_code` values intact — the table suppression is render-layer only.
  </behavior>
  <action>
    Extend `_error_text` in `submit.py` to satisfy the behaviors above. The NA suppression and
    the SKIPPED pass-through are one branch each. The degradation paths are the tolerant
    `int()` coercion already specified in Task 1 plus a `.get()` on the catalog — confirm both
    are actually reached rather than adding new guards on top of them.

    For the hardening, normalize the resolved name before it reaches the cell: replace or drop
    any pipe, newline and carriage return, and truncate to 64 characters. Apply this to the
    name only — the code is already an `int` by then and cannot carry markup. Keep it a single
    small helper or a single expression inside `_error_text`; do not spread it across the two
    call sites, or the two tables can diverge.

    Change nothing in `cli_handlers.py` in this task: it consumes the formatter, so every
    behavior above reaches the saved artifact through Task 1's wiring. If a test shows
    otherwise, that is a Task 1 wiring defect to fix, not a reason to duplicate logic.

    Write no comments into `firestarter_app` product source. Docstring updates on the two new
    functions are the place to state the NA-versus-SKIPPED asymmetry and the omission rule.
  </action>
  <verify>
    <automated>cd firestarter_app && ./.venv311/bin/python -m pytest tests/test_submit.py tests/test_devtest_firmware_error_propagation.py tests/test_diagnostic_report.py -q -o addopts="" && ./.venv311/bin/ruff check firestarter tests && ./.venv311/bin/ruff format --check firestarter tests</automated>
  </verify>
  <done>Every behavior listed above has a passing test that was observed RED first; an NA row renders `-` while a SKIPPED row renders its code; an unknown id renders bare; a malformed code renders `-` without raising; a hostile `error_name` cannot alter the table's row count or column count; a codeless report's table is byte-identical to today's; and `ruff check` plus `ruff format --check` are clean.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| report dict -> public GitHub issue body | `build_body` output is pasted or filed verbatim into a public issue; everything it renders leaves the operator's machine. |
| replayed report JSON -> `build_body` | `build_body` accepts any dict shaped like a report, including one authored elsewhere or generated by an older host; the test suite itself replays hand-built dicts. |
| firmware wire frame -> `error_code` | The integer originates in a firmware `response.id` decoded off the serial link and is attacker-influenceable only by whoever owns the attached board. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-nba-01 | Information disclosure | `submit.build_body` new Error cell | medium | mitigate | The cell is derived from an `int` plus a name resolved out of the generated `messages.CATALOG` — a compile-time constant set. No free text, no path, no device name and no operator-supplied string is introduced into the issue body by this change; `sanitize_dict` still runs upstream and its int leaves pass through untouched. Pinned by the Task 2 test asserting the cell contents for a known id. |
| T-nba-02 | Tampering | `_error_text` rendering an externally supplied `error_name` | medium | mitigate | A replayed report could carry an `error_name` containing a pipe or a newline and forge extra cells or extra rows in the rendered markdown a triager then trusts. Task 2 strips pipe, newline and carriage return from the name and caps it at 64 characters, with a test asserting the rendered table's row and column counts are unchanged by a hostile value. |
| T-nba-03 | Denial of service | `_error_text` coercion path | low | mitigate | A malformed or unbounded `error_code` must not raise inside the report writer and abort a completed `dev test` run before its artifact is written. The tolerant `int()` coercion returns `-` for any non-coercible value; Task 2 pins it. |
| T-nba-04 | Spoofing | Symbolic name attribution | low | accept | A name resolved from a host-local `messages.py` that has drifted from the firmware could mis-name a code. Accepted: the code itself is always rendered alongside the name, so a triager retains the unambiguous integer, and catalog drift is already governed by the meta-repo codegen sync. |
| T-nba-SC | Tampering | package-manager installs | low | accept | No npm/pip/cargo install is performed by this plan; no new dependency is introduced. The package-legitimacy gate does not apply. |
</threat_model>

<verification>
Run from the `firestarter_app` sub-repo on Python 3.11 (CI runs 3.11 only; the devcontainer's
default 3.12 masks 3.11 failures):

- `./.venv311/bin/python -m pytest tests/ -q -o addopts=""` — the whole app suite green,
  including `tests/test_dev_test_cmd.py` (roughly 70 s on its own) and
  `tests/test_parse_devtest_issue.py`, which parses filed bodies through
  `tools/parse_devtest_issue.py`. That parser reads the fenced JSON block and never the step
  table, so the column addition must leave it entirely unaffected.
- `./.venv311/bin/ruff check firestarter tests` and
  `./.venv311/bin/ruff format --check firestarter tests` — the CI tooling gate.
- Confirm by eye on one rendered body that the Error column sits between `Took` and `Reason`
  and that the separator row has the same cell count as the header.
</verification>

<success_criteria>
- The markdown step table of a `dev test` report shows the firmware message id and its
  symbolic name for every step that has one, in both the saved `.md` artifact and the filed
  issue body, with a single formatter shared by both.
- A report with no coded step renders exactly today's table.
- `NA` rows render `-`; `SKIPPED` rows keep their code.
- Unknown and malformed codes degrade without raising.
- No id-to-name table is hand-written; the name comes from 260916-nb9's resolution or from
  `firestarter.messages.CATALOG`.
- No `SCHEMA_VERSION` change, no JSON field added, no console-table change in this plan.
- No comments added to `firestarter_app` product source.
- Full app suite plus both ruff gates green on Python 3.11.
</success_criteria>

<output>
Create `.planning/quick/260916-nba-render-the-firmware-error-code-and-its-symbolic-name-in-the/260916-nba-SUMMARY.md` when done.

Record in it: the scope correction (the render sites are `submit.py` and `cli_handlers.py`,
not `chip_test.py`), the column-position and column-omission rationale, the NA-versus-SKIPPED
asymmetry with its citation to the `chip_test.py` docstring that motivates it, and whether
260916-nb9's resolver was importable or the catalog was read directly.
</output>
