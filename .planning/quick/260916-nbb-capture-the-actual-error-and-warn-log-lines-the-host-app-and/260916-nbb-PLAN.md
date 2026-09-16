---
phase: quick-260916-nbb
plan: 01
type: execute
wave: 2
depends_on: ["260916-nb9", "260916-nba"]
files_modified:
  - firestarter_app/firestarter/log_capture.py
  - firestarter_app/firestarter/chip_test.py
  - firestarter_app/firestarter/diagnostic_report.py
  - firestarter_app/firestarter/cli_handlers.py
  - firestarter_app/firestarter/submit.py
  - firestarter_app/pyproject.toml
  - firestarter_app/tests/test_log_capture.py
  - firestarter_app/tests/test_blast_radius_invariance.py
  - firestarter_app/tests/test_dev_test_cmd.py
autonomous: true
requirements: [260916-nbb]

estimate:
  tokens: 55000
  raw_tokens: 110000
  tasks: 3
  confidence: high

must_haves:
  truths:
    - "A firmware `ERROR:`/`WARN:` line emitted during a `dev test` run appears in the saved report JSON under `log_capture.entries`, tagged `source: firmware` (D-01)."
    - "A host-side `logger.warning`/`logger.error` line emitted during the same run appears in the same block tagged `source: host` (D-01)."
    - "Each entry names the step that was running when the line was emitted, or `null` for a line emitted outside any step (D-02)."
    - "The block can never carry more than `max_entries` entries or a message longer than `max_line_chars` characters, and every line lost to either bound is counted in `dropped`/`truncated` rather than vanishing silently (D-03)."
    - "Capture is always on for the whole run window and the block is always exported, whatever the run's verdict (D-04)."
    - "A captured line carrying a home directory path, a serial device name, a temp path or the operator's username is scrubbed before any GitHub issue body is built (D-05)."
    - "Two runs identical except for their captured log lines still produce the same `dedup_fingerprint`."
    - "A captured message can neither close the markdown fence it is rendered inside nor carry a terminal control sequence into a triager's console."
    - "The capture handler is attached to the root logger only for the run window and is gone afterwards; installing twice leaves exactly one."
    - "No source comment is added anywhere under `firestarter_app/firestarter/`."
  artifacts:
    - firestarter_app/firestarter/log_capture.py
    - firestarter_app/tests/test_log_capture.py
  key_links:
    - "`chip_test._run_step` -> `log_capture.step_scope(step.op)` — the ONLY step-attribution seam; it covers the plain loop, `_run_cycle_block` and the SDP cleanup drain in one place"
    - "`cli_handlers.dev_test` -> `log_capture.install()` / `snapshot()` / `uninstall()` — defines the measurement window, mirroring `transport_counters.reset()`/`snapshot()`"
    - "`DiagnosticReport.to_dict()['log_capture']` -> `submit.sanitize_dict` — the single publish-time PII boundary for every captured line"
    - "`tests/test_blast_radius_invariance.py::_TO_DICT_KEYS` -> the new top-level key; the pin is exhaustive and MUST gain `log_capture` in the same commit or the suite goes red"
    - "`log_capture.FIRMWARE_LOGGER_NAME` -> `serial_comm.rurp_logger.name` — a rename on either side silently reclassifies every firmware line as a host line"
---

<objective>
Make a failed `dev test` say which code path failed, by keeping the `ERROR:`/`WARN:` lines the
run actually produced instead of throwing all of them away and filing one exception string.

Purpose: issue #86's `write` step reports `Operation timed out` and nothing else. The firmware
emitted diagnostic lines on the way to that timeout and the host logged them to the console,
where they died. A triager opening the issue sees a terminal symptom with no path to a cause.
This plan buffers those lines during the run, tags each with the step that was running and the
side that emitted it, bounds the result so an issue body stays pasteable, and exports the block
through the same `to_dict()` the JSON artifact, the markdown artifact and the filed issue all
already derive from.

Output: one new leaf module `firestarter/log_capture.py`, one new top-level report key
`log_capture`, a compact diagnostics section in the two markdown surfaces, and a test module
that proves the bounds, the attribution and the scrub.

Scope note: every file this plan touches sits under `firestarter_app/firestarter/` or its
`tests/`, with ONE deliberate exception — `firestarter_app/pyproject.toml` gains a single entry
adding the new module to the mypy strict island, the same from-birth strengthening
`firestarter.sdp_honesty` recorded. Declared here so it is not read as scope creep at merge.

Design decisions this plan settles (the four questions the task description left open, plus the
schema question):

- D-01: Capture is a `logging.Handler` on the ROOT logger at level WARNING, so it collects host and firmware lines by one mechanism; `source` is `firmware` when the emitting logger is named `RURP` (the firmware feedback logger `serial_comm._log_rurp_feedback` uses) and `host` otherwise.
- D-02: Lines attach as ONE run-level block whose every entry names its step, never as a per-step list inside `steps[]` — one block is capped as a unit, keeps `steps[]`'s pinned element shape untouched, sits beside `transport_health` (the existing run-level diagnostics precedent), and still answers "which step" per line.
- D-03: Overflow drops the OLDEST entry (a `deque(maxlen=MAX_ENTRIES)` ring) and adds the lost lines to an exported `dropped` count; an over-long message is cut to `MAX_LINE_CHARS` and counted in `truncated`. Drop-oldest is chosen over drop-middle because the lines nearest the failure are the ones triage needs and a ring is correct by construction rather than by a hand-written rule; the exported counts are what keep the loss non-silent.
- D-04: Capture is ALWAYS on for the run window and the block is ALWAYS exported, never gated on a BAD or marginal verdict — the WARNING level filter is what keeps a clean run's block small (usually empty), and a warning on an otherwise-OK run is exactly the marginal evidence a verdict gate would discard.
- D-05: Every captured message is normalized at capture time (whitespace collapsed, non-printable characters dropped, backtick fences neutralized, then truncated) and rides inside `to_dict()`, which `submit.submit_report` already deep-scrubs through `sanitize_dict` before any issue body exists; the locally saved artifacts stay unsanitized exactly as `reason` already is.
</objective>

<execution_context>
@/workspaces/.claude/gsd-core/workflows/execute-plan.md
@/workspaces/.claude/gsd-core/templates/summary.md
</execution_context>

<context>
@/workspaces/CLAUDE.md
@/workspaces/firestarter_app/CLAUDE.md
@/workspaces/firestarter_app/firestarter/transport_counters.py
</context>

<facts_established_during_planning>
Measured in the devcontainer during planning against
`v1.39-protocol-0x05-write-correctness` (meta `5fbbe9a5`, app `2acf5d3`). Do not re-derive
these; do re-check any one a task's behaviour depends on.

- **Test interpreter.** `/workspaces/firestarter_app/.venv311/bin/python` is CPython 3.11.16 with
  the package editable-installed, `pytest` 9.1.1, `ruff` 0.16.5, `mypy` 2.3.1. The devcontainer's
  `python3` is 3.12.14 and MUST NOT be used to judge this suite — CI runs 3.11 only.
- **Green baseline.** `./.venv311/bin/python -m pytest tests/test_blast_radius_invariance.py
  tests/test_diagnostic_report.py tests/test_dev_test_cmd.py tests/test_submit.py -o addopts="" -q`
  is `325 passed in 69.47s`. `-o addopts=""` is required: the project `addopts` is `-ra -q` and a
  second `-q` suppresses the count line.
- **Lint baseline.** `ruff check firestarter tests` is `All checks passed!`; `ruff format --check
  firestarter tests` is `137 files already formatted`.
- **mypy baseline is NOT zero.** The strict island run reports exactly ONE pre-existing error,
  `firestarter/submit.py:782: error: Incompatible types in assignment`, reached transitively.
  A gate demanding exit 0 is red on arrival; pin the count instead.
- **Where firmware lines become log records.** `serial_comm._log_rurp_feedback` maps the wire
  prefix to a level on the module logger `rurp_logger = logging.getLogger("RURP")`: `ERROR` ->
  `logging.ERROR`, `WARN` -> `logging.WARNING`, `INFO` -> `logging.INFO`, everything else DEBUG.
  So a root handler at level WARNING collects exactly the two bands this task names, plus
  CRITICAL, and nothing from the protocol-phase frames.
- **Host lines.** `serial_comm.logger` is `logging.getLogger("SerialComm")`, `cli_handlers.logger`
  is `logging.getLogger("Firestarter")`. Both propagate to root. `_read_and_parse_lines` emits two
  re-sync warnings from inside a byte loop — they are the realistic flood source that makes the
  consecutive-repeat collapse in Task 2 load-bearing rather than decorative.
- **Root handlers are REPLACED at group entry.** `cli_handlers._setup_logging` ends with
  `root_logger.handlers = [handler]`. It runs at Click group entry, before any command body, so a
  handler installed inside `dev_test` is never clobbered — but a handler installed at import time
  would be. Install inside the handler body, nowhere else.
- **The step dispatch funnel.** `chip_test._run_step` is called from three places
  (`run_plan`'s plain loop, `_run_cycle_block`, and the SDP cleanup drain's nested def) and
  `_run_step_untimed` from exactly one — `_run_step` itself. Wrapping `_run_step`'s body is the
  single seam that attributes every executed step. NA/SKIPPED steps `continue` before reaching it
  and emit nothing.
- **`chip_test.py` has no logger and must not get one** — its own source says so at the failed-unlock
  site. It gains ONE import from this plan and nothing else.
- **`to_dict()` runs three times per run** (console render, saved `.json`, `to_json_block()` inside
  the `.md`). Any value that must agree across all three is stamped ONCE onto the dataclass before
  the first render — this is exactly why `elapsed` is a stored attribute. The log snapshot follows
  that rule.
- **The exhaustive pin.** `tests/test_blast_radius_invariance.py::_TO_DICT_KEYS` is a sorted
  15-entry list compared element-wise, with an anti-vacuity leg proving it reddens on an ADDED key.
  Adding a top-level key without updating that list fails the suite. `tests/test_dev_test_cmd.py`'s
  own key check is a deliberate spot-check and needs no edit.
- **`_STEPS_ELEMENT_0_KEYS`, `_TRANSPORT_HEALTH_KEYS`, `_VOLTAGE_KEYS`, `_DB_DIFF_KEYS` are
  untouched by this plan** — the block is top-level, not nested inside `steps[]`.
- **The scrub already reaches nested lists.** `submit.sanitize_dict` -> `_scrub_value` recurses
  through dict, list and tuple and rewrites every string leaf; `_SCRUBS` covers `/home/<user>`,
  `/Users/<user>`, `C:\Users\<user>`, `/dev/ttyACM*`, `/dev/ttyUSB*`, `/dev/tty.*`, `COM<n>` and
  `/tmp/...`, plus the current username as a whole word when it is at least 3 characters.
  `submit_report` builds EVERY body from `sanitize_dict(report.to_dict())` — the gh tier, the
  browser tier and the duplicate-comment tier all read that one sanitized dict.
- **The browser tier drops the JSON block past `_URL_ESCALATE_BYTES` (7500).** That is why the
  markdown diagnostics section in Task 3 is not redundant with the fenced JSON: on an escalated
  browser submission the markdown is the only surface the captured lines survive on.
- **`dedup_fingerprint` hashes an explicit allow-list with no dataclass reflection**, so a new
  field is excluded automatically. Task 3 pins that with a test rather than trusting it.
- **`diagnostic_report.py`'s import-purity guard** (`test_report_module_is_orchestrator_only`)
  forbids importing `SerialCommunicator` or `HardwareManager` by AST. Carrying the block as a plain
  mapping keeps that module importing nothing new at all.
- **The mypy strict island** in `pyproject.toml` lists nine modules and records `sdp_honesty`
  joining from birth as a deliberate strengthening. `firestarter.log_capture` joins the same way.
  `firestarter.transport_counters` is NOT in it; that is not a precedent against, it predates nothing.
- **`/usr/bin/grep` for every evidence grep.** The `grep` on PATH is ugrep and honours
  `.gitignore`, which silently under-scans.
- **The comment gate below was proven sensitive before it was written into this plan.** Fed a
  planted `+# ...` diff line it prints `1`; run against the clean tree it prints `0`. Its second
  stage MUST stay `/usr/bin/grep -v '^+++'` with no backslashes: in GNU basic regex `\+` is the
  one-or-more operator, so the tempting `-v '^\+\+\+'` matches every added line and wipes the
  whole pipeline — the gate then prints `0` for any diff whatsoever and fails OPEN. Measured.
- **`grep -c` exits 1 when the count is zero**, which reads as a failed command. Every count gate
  here ends in `wc -l` instead, so the printed number is the verdict and the exit status is not.
- **Both mypy gate legs were run verbatim during planning** against today's tree: the count leg is
  meaningful only after `log_capture.py` exists, and the pin leg already prints
  `Found 1 error in 1 file (checked 9 source files)` at rc 0.
</facts_established_during_planning>

<tasks>

<task type="tracer">
  <name>Task 1: One firmware ERROR line, emitted mid-write, lands in the saved report JSON tagged with its step</name>
  <files>firestarter_app/firestarter/log_capture.py, firestarter_app/firestarter/chip_test.py, firestarter_app/firestarter/diagnostic_report.py, firestarter_app/firestarter/cli_handlers.py, firestarter_app/pyproject.toml, firestarter_app/tests/test_blast_radius_invariance.py, firestarter_app/tests/test_dev_test_cmd.py</files>
  <read_first>firestarter_app/firestarter/transport_counters.py in full (the module this one is modelled on); `_log_rurp_feedback` in firestarter_app/firestarter/serial_comm.py; `_run_step` in firestarter_app/firestarter/chip_test.py; `to_dict`, the `DiagnosticReport` field block and `_transport_dict` in firestarter_app/firestarter/diagnostic_report.py; the `dev_test` handler body in firestarter_app/firestarter/cli_handlers.py from `transport_counters.reset()` through `report.render(console)`; `_TO_DICT_KEYS` and `test_to_dict_key_list_pins_are_sensitive_to_added_and_removed_keys` in firestarter_app/tests/test_blast_radius_invariance.py; `make_clean_operator`, `make_hardware_manager`, `_load_report` and the `_isolate_config_dir` fixture in firestarter_app/tests/test_dev_test_cmd.py.</read_first>
  <action>
Wire ONE path end to end: a `logging` record emitted while a step is running reaches the saved
`dev-test-<chip>.json`. Bounds and normalization are in this task because they are the module's
contract, not a later polish; message rewriting and repeat collapse are Task 2.

Create `firestarter_app/firestarter/log_capture.py` as a stdlib-only leaf module. It imports
nothing from `firestarter` — that is what keeps the import graph acyclic, the same property
`transport_counters` states about itself. Module docstring explains, in the voice
`transport_counters.py` uses: why process-lifetime module state rather than per-instance state
(`EpromOperator.comm` is torn down after every operator call, so a buffer on a
`SerialCommunicator` is destroyed before the report is built); why the sink attaches to the ROOT
logger (it is the one place both the firmware feedback logger and every host module logger
converge, per D-01); and why the window is opened and closed by the caller rather than at import.

Public surface:

- `MAX_ENTRIES = 20` and `MAX_LINE_CHARS = 160` — module constants, the whole size contract. Their
  product plus framing is the block's worst case, so no third knob exists. State in the docstring
  that the bound is sized for a GitHub issue body that also carries the fenced JSON block and,
  on the browser tier, must survive percent-encoding.
- `FIRMWARE_LOGGER_NAME = "RURP"` — the logger name `serial_comm.rurp_logger` is built from. A
  record whose `name` equals it is `firmware`; every other record is `host`.
- `install()` — idempotent. Remove any previously attached instance of this module's handler class
  from the root logger FIRST, then clear the buffer and counters, then attach a fresh handler at
  `logging.WARNING`. Self-healing by construction: a run that raised on the way out cannot leave a
  second handler behind.
- `uninstall()` — remove this module's handler from the root logger if present; a no-op otherwise.
- `step_scope(op)` — a `contextlib.contextmanager` that sets the current step name for the duration
  and restores the PREVIOUS value in a `finally`, never a hard `None`. Copy `probe_scope`'s reasoning
  verbatim in the docstring: restoring the previous value is what keeps a nested or exception-exiting
  scope from leaving the sink stuck.
- `snapshot()` — build and return a FRESH mapping every call so a caller mutating it cannot reach
  back into the sink. Shape, with every key present unconditionally:
  `{"entries": [...], "captured": int, "dropped": int, "truncated": int, "max_entries": MAX_ENTRIES, "max_line_chars": MAX_LINE_CHARS}`.
  Each element of `entries` carries exactly `{"step": str|None, "source": str, "level": str, "message": str, "repeat": int}`,
  again unconditionally — `step` is `None` for a line emitted outside any step scope, `repeat` is
  `1` until Task 2 collapses duplicates.

Handler behaviour, per record: read the message with `record.getMessage()`, never a formatter, so
the captured text is identical under `-v` and without it. Level is `record.levelname`. Cut the
message to `MAX_LINE_CHARS` by keeping the first `MAX_LINE_CHARS - 3` characters and appending
three dots, so every exported message satisfies `len(message) <= MAX_LINE_CHARS` exactly, and
increment `truncated` when a cut happened. Increment `captured` for every accepted record. Before
appending to a full ring, add the front entry's `repeat` to `dropped` — a `deque(maxlen=...)`
evicts silently otherwise and the whole point of the counter is that loss is visible. The handler
never raises: wrap its body so a formatting failure in a third-party record cannot break a run
that is otherwise fine.

Add `firestarter.log_capture` to the mypy strict-island `module` list in
`firestarter_app/pyproject.toml`, joining from birth the way `firestarter.sdp_honesty` did. Every
def in the new module carries annotations.

In `firestarter_app/firestarter/chip_test.py`: add `from firestarter.log_capture import step_scope`
to the existing `from firestarter.*` import group and wrap `_run_step`'s BODY in
`with step_scope(step.op):`. `_run_step` is chosen for the same reason its docstring already gives
for the duration stamp — it is the one wrapper every dispatch path passes through, so one seam
attributes every executed step. Do not add a logger to this module and do not touch
`_run_step_untimed`.

In `firestarter_app/firestarter/diagnostic_report.py`: add a `log_capture: dict[str, Any] | None = None`
field to `DiagnosticReport` and export it verbatim from `to_dict()` as the top-level key
`log_capture`. Follow `db_diff`'s honesty convention — `None` means no capture window ran (a
synthetic report built directly in a unit test), a mapping means one did, and an empty `entries`
list inside that mapping means the window ran and produced nothing. This module imports nothing
new: it carries and serializes the mapping, it never builds one. Document on the field, in the
voice `elapsed` uses, that the value is STAMPED by `cli_handlers.py` before the first render
because `to_dict()` runs three times per run and a live read would answer a different question
each time. Bump `SCHEMA_VERSION` one patch step above whatever it reads at HEAD when this task
runs: `2.1` becomes `2.2`, and if sibling 260916-nb9 has not landed and it still reads `2.0`,
make it `2.1`.

In `firestarter_app/firestarter/cli_handlers.py`: add `log_capture` to the existing
`from firestarter import (...)` tuple in alphabetical position. Call `log_capture.install()`
immediately after `transport_counters.reset()`, so the window opens before the identity read and
a warning from that read is captured with `step: null`. Then, immediately AFTER the existing
`report.elapsed = (...)` assignment and BEFORE `report.render(console)`, assign
`report.log_capture = log_capture.snapshot()` and call `log_capture.uninstall()` on the next line.
That placement is deliberate and must not drift: it is the widest honest window, and it is before
the first of the three `to_dict()` calls, so the console, the `.json` and the `.md` cannot disagree.

Update `_TO_DICT_KEYS` in `firestarter_app/tests/test_blast_radius_invariance.py` to include
`log_capture` in sorted position and update the count wording in its own docstring; update
`test_schema_version_is_pinned` to the new literal, keeping the triple-equality idiom
(constant, literal, baked value) intact.

Add ONE end-to-end test to `firestarter_app/tests/test_dev_test_cmd.py` (it must live there: the
`_isolate_config_dir` autouse fixture and the operator/hardware doubles are module-local). Build
a clean operator whose `write_eprom` side effect first emits a record on
`logging.getLogger("RURP")` at ERROR with a recognizable sentinel message, then returns success.
Invoke `dev test` through `CliRunner`, load the saved report with `_load_report`, and assert the
sentinel appears in exactly one `log_capture.entries` element, with `source` of `firmware`,
`level` of `ERROR` and `step` naming the write step. Assert by identity and content, never by an
absolute root-handler count — pytest attaches its own handlers.

Write no comments into any file under `firestarter_app/firestarter/`. Rationale for every decision
above goes in the SUMMARY or the commit message. Module and function docstrings are not comments
and are expected here.
  </action>
  <verify>
    <automated>cd /workspaces/firestarter_app && ./.venv311/bin/python -m pytest tests/test_dev_test_cmd.py tests/test_blast_radius_invariance.py tests/test_diagnostic_report.py -o addopts="" -q</automated>
    <automated>cd /workspaces/firestarter_app && ./.venv311/bin/python -c "import firestarter.log_capture as m; print(sorted(m.snapshot()))"</automated>
    <automated>cd /workspaces/firestarter_app && D=$(git diff 2acf5d3 -- firestarter/) || exit 1; printf '%s\n' "$D" | /usr/bin/grep -E '^\+' | /usr/bin/grep -v '^+++' | /usr/bin/grep -E '^\+[[:space:]]*#' | /usr/bin/grep -vE '(noqa|type:|pragma)' | wc -l</automated>
  </verify>
  <done>A firmware-side ERROR record emitted during the write step appears once in the saved `dev-test-CHIP.json` under `log_capture.entries` with `source`, `level` and the write step's name; `snapshot()` returns all six keys; the third command prints `0`; the three test files pass.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Bound and neutralize what a captured line can contain, and prove every bound</name>
  <files>firestarter_app/firestarter/log_capture.py, firestarter_app/tests/test_log_capture.py</files>
  <behavior>
    - A message containing CR, LF or tabs collapses to single spaces and is stripped, so one entry is always one line.
    - A message containing characters outside printable ASCII loses them, so an escape sequence from a garbled frame cannot reach a triager's terminal.
    - A run of three or more backticks becomes an equal-length run of single quotes, so a captured line cannot close the markdown fence it is rendered inside.
    - Normalization runs in a fixed order — collapse whitespace, drop non-printable, neutralize fences, then truncate — so the length bound is the last word and is always satisfied.
    - Every exported message satisfies `len(message) <= MAX_LINE_CHARS`; a message one character over the bound is cut and counts once in `truncated`; a message exactly at the bound is untouched and counts zero.
    - Two consecutive records agreeing on step, source, level and normalized message collapse into one entry whose `repeat` is 2; a third identical one makes it 3.
    - A different message between two identical ones prevents the collapse: three entries, each `repeat` 1.
    - `MAX_ENTRIES + 5` distinct messages leave exactly `MAX_ENTRIES` entries, the OLDEST five gone, `dropped` equal to 5, and the newest message still present.
    - Evicting a collapsed entry adds its whole `repeat` to `dropped`, never 1.
    - `captured` counts every accepted record, so it stays greater than or equal to the number of entries whatever collapsing and eviction did.
    - A record below WARNING is not captured at all; WARNING, ERROR and CRITICAL are.
    - A record on the `RURP` logger is `firmware`; a record on any other logger name is `host`.
    - `install()` called twice leaves exactly one instance of the handler class on the root logger; `uninstall()` leaves zero; `uninstall()` on an uninstalled sink is a no-op.
    - `step_scope` nested two deep restores the OUTER step on inner exit, and restores it even when the inner body raises.
    - `snapshot()` returns a fresh object each call: mutating the returned entries list cannot change the next snapshot.
    - `FIRMWARE_LOGGER_NAME` equals `serial_comm.rurp_logger.name` — the drift guard.
  </behavior>
  <action>
Write `firestarter_app/tests/test_log_capture.py` first, one test per behavior above, and watch the
new ones fail before implementing. Drive the sink through the real `logging` API
(`logging.getLogger(...).warning(...)`), never by calling the handler's own method directly — the
handler's level filter and the root propagation are part of what is under test. Use a fixture that
calls `log_capture.uninstall()` in teardown so a failing test cannot leak a handler into the rest
of the suite.

Then implement in `firestarter_app/firestarter/log_capture.py`: a private normalization function
applying the four steps in the stated order, and consecutive-duplicate collapse in the append path
keyed on the tuple of step, source, level and normalized message. Collapse is not cosmetic: the
two re-sync warnings in `serial_comm._read_and_parse_lines` fire from inside a byte loop, and
without collapsing, one bad cable evicts every other line in the ring and the block reports a
cable when the chip was the finding. Record that reasoning in the function's docstring.

Use a compiled module-level regex for the backtick run and for the non-printable class rather than
rebuilding them per record; the handler runs on every warning of a long run.

The drift guard imports `firestarter.serial_comm` inside the test function, not at module scope,
and compares `rurp_logger.name` against `FIRMWARE_LOGGER_NAME`. It exists because a rename on
either side would silently reclassify every firmware line as a host line — a failure with no
symptom in any other test.

No comments in the module. The test module may carry docstrings explaining what each property
proves; put the reasoning there and in the SUMMARY.
  </action>
  <verify>
    <automated>cd /workspaces/firestarter_app && ./.venv311/bin/python -m pytest tests/test_log_capture.py -o addopts="" -q</automated>
    <automated>cd /workspaces/firestarter_app && ./.venv311/bin/python -m pytest tests/test_dev_test_cmd.py tests/test_blast_radius_invariance.py -o addopts="" -q</automated>
    <automated>cd /workspaces/firestarter_app && D=$(git diff 2acf5d3 -- firestarter/) || exit 1; printf '%s\n' "$D" | /usr/bin/grep -E '^\+' | /usr/bin/grep -v '^+++' | /usr/bin/grep -E '^\+[[:space:]]*#' | /usr/bin/grep -vE '(noqa|type:|pragma)' | wc -l</automated>
  </verify>
  <done>Every behavior above is a passing test in `tests/test_log_capture.py`, each observed red before its implementation; the existing suites still pass; the comment count prints `0`.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: Put the captured lines on the two markdown surfaces and prove the publish path is safe</name>
  <files>firestarter_app/firestarter/submit.py, firestarter_app/firestarter/cli_handlers.py, firestarter_app/tests/test_log_capture.py</files>
  <read_first>`build_body`, `_duration_text`, `_reason_text`, `_runs_text`, `sanitize_dict`, `_scrub_value`, `_SCRUBS`, `build_issue_url` and `submit_report` in firestarter_app/firestarter/submit.py; the `md_lines` block in `dev_test` in firestarter_app/firestarter/cli_handlers.py, including the local imports of the three `submit` formatters it already reuses.</read_first>
  <behavior>
    - A report whose `log_capture` carries entries renders a diagnostics section after the step table, inside a fenced text block, one line per entry, each naming its step, source and level.
    - An entry with `repeat` above 1 renders its repeat count; an entry with `repeat` of 1 renders no count.
    - The section's heading states the `captured`, `dropped` and `truncated` numbers, so a reader can tell the block is partial without opening the JSON.
    - A report with zero entries renders NO section at all, and a report whose `log_capture` is `None` renders no section and does not raise.
    - The saved `.md` artifact and the filed issue body carry the SAME section text, because both call the same formatter in `submit.py` — the discipline the three existing shared formatters already follow.
    - A captured message containing a home directory path, a `/dev/ttyACM` device, a `/tmp` path or the operator's username is scrubbed in the body `submit_report` builds, both in the fenced JSON and in the diagnostics section.
    - A captured message containing a triple backtick cannot close the fence the section is rendered inside.
    - Two reports identical except for their captured log lines produce the SAME `dedup_fingerprint`.
    - A full block at both bounds renders a diagnostics section under 4000 characters.
  </behavior>
  <action>
Add ONE formatter to `firestarter_app/firestarter/submit.py` that takes the report mapping and
returns the diagnostics section as a list of markdown lines, empty when there is nothing to show.
Call it from `build_body` after the step table, and call the same function from `dev_test`'s
`md_lines` block in `cli_handlers.py` via the same local-import style that module already uses for
`_duration_text`, `_reason_text` and `_runs_text` — one formatter, two surfaces, no second field
list. State in its docstring why this section is not redundant with the fenced JSON that already
carries the same data: `build_issue_url` drops the JSON block past `_URL_ESCALATE_BYTES`, so on an
escalated browser submission this section is the only place the captured lines survive.

`build_body` must read the section from the SANITIZED mapping it is already handed, never from the
unsanitized report — the same reason its docstring already gives for sourcing the reason cells
from `sanitized_dict["steps"]`.

Render inside a fenced text block so a long line cannot break the step table above it. Keep the
section absent entirely on an empty or `None` block, matching the `elapsed` line's existing
conditional in the same function.

Add the remaining tests to `firestarter_app/tests/test_log_capture.py`, including the three that
carry the threat model: the scrub proof (plant a home path, a device node, a temp path and the
username inside a captured message, run `sanitize_dict` over a real `to_dict()` mapping, assert
every vector is rewritten in the nested entries), the fence proof, and the dedup-stability proof.
Build the report objects for these through the same construction the existing report tests use, and
drive the scrub through `sanitize_dict` rather than re-implementing it.

No comments in either source file.
  </action>
  <verify>
    <automated>cd /workspaces/firestarter_app && ./.venv311/bin/python -m pytest tests/test_log_capture.py tests/test_submit.py tests/test_dev_test_cmd.py -o addopts="" -q</automated>
    <automated>cd /workspaces/firestarter_app && ./.venv311/bin/python -m pytest -o addopts="" -q</automated>
    <automated>cd /workspaces/firestarter_app && ./.venv311/bin/python -m ruff check firestarter tests && ./.venv311/bin/python -m ruff format --check firestarter tests</automated>
    <automated>cd /workspaces/firestarter_app && ./.venv311/bin/python -m mypy firestarter/main.py firestarter/cli_handlers.py firestarter/chip_resolver.py firestarter/frame_parser.py firestarter/codec.py firestarter/address_parser.py firestarter/exceptions.py firestarter/serial_comm.py firestarter/sdp_honesty.py firestarter/log_capture.py 2>&1 | /usr/bin/grep -E '^firestarter/(log_capture|cli_handlers)\.py.*error:' | wc -l</automated>
    <automated>cd /workspaces/firestarter_app && ./.venv311/bin/python -m mypy firestarter/main.py firestarter/cli_handlers.py firestarter/chip_resolver.py firestarter/frame_parser.py firestarter/codec.py firestarter/address_parser.py firestarter/exceptions.py firestarter/serial_comm.py firestarter/sdp_honesty.py firestarter/log_capture.py 2>&1 | /usr/bin/grep -E '^Found 1 error'</automated>
    <automated>cd /workspaces/firestarter_app && D=$(git diff 2acf5d3 -- firestarter/) || exit 1; printf '%s\n' "$D" | /usr/bin/grep -E '^\+' | /usr/bin/grep -v '^+++' | /usr/bin/grep -E '^\+[[:space:]]*#' | /usr/bin/grep -vE '(noqa|type:|pragma)' | wc -l</automated>
  </verify>
  <done>The diagnostics section appears in both markdown surfaces from one formatter and is absent on an empty block; the scrub, fence and dedup proofs pass; the whole suite passes; ruff is clean; the fourth command prints `0` and the fifth prints the pre-existing single-error line (a `Found 2 errors` line, or no output, is a regression); the last command prints `0`.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| firmware -> host (serial) | Message text originating on the board crosses into host process memory and, from there, into a public issue body. Anyone with physical access to the programmer controls it. |
| host process -> local artifact | `~/.firestarter/reports/dev-test-<chip>.{json,md}` is written unsanitized, as `reason` already is. |
| host process -> public GitHub issue | `submit_report` publishes the report to `henols/firestarter`, a public tracker, over the gh tier, the browser tier or a duplicate comment. This is the boundary this item newly widens. |
| host logging -> operator terminal | A triager reading the saved `.md` or `cat`-ing the artifact renders captured text in a terminal. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-nbb-01 | Information Disclosure | captured message text -> public issue body | high | mitigate | Lines ride inside `to_dict()`, and `submit_report` builds EVERY body from `sanitize_dict(report.to_dict())`, whose `_scrub_value` recurses into the nested entries list. Task 3 proves the four vectors (home path, tty device, temp path, username) are rewritten inside a captured message, not merely inside `reason`. |
| T-nbb-02 | Information Disclosure | data bytes reaching a captured line | medium | mitigate | The handler filters at WARNING, and no WARNING-or-above site in the package embeds a memory buffer; `MAX_LINE_CHARS` bounds any future one to 160 characters regardless. Task 2 pins the length bound on every exported message. |
| T-nbb-03 | Tampering | firmware-supplied text closing the markdown fence in an issue body | medium | mitigate | Task 2 rewrites any run of three or more backticks to single quotes before the message is stored, so no captured line can terminate the fence it is rendered inside. Proven by the fence test in Task 3. |
| T-nbb-04 | Tampering | control/escape sequences reaching a triager's terminal | medium | mitigate | Task 2 drops every character outside printable ASCII at capture time, ahead of truncation. |
| T-nbb-05 | Denial of Service | unbounded buffer growth from a warning inside a byte loop | low | mitigate | `deque(maxlen=MAX_ENTRIES)` plus per-message truncation bounds memory by construction; consecutive-duplicate collapse keeps a re-sync storm from evicting the diagnostically useful lines. |
| T-nbb-06 | Denial of Service | an oversized issue body failing to submit | low | mitigate | The worst-case block is `MAX_ENTRIES` times `MAX_LINE_CHARS` plus framing; Task 3 asserts the rendered section stays under 4000 characters, well inside `_URL_ESCALATE_BYTES`. |
| T-nbb-07 | Repudiation | silent truncation hiding the failing line | medium | mitigate | `dropped` and `truncated` are exported counts and are stated in the markdown section heading, so a reader always knows the block is partial (D-03). |
| T-nbb-08 | Information Disclosure | the unsanitized local `.json`/`.md` artifacts | low | accept | Pre-existing and unchanged: `reason` already lands there unsanitized. The files stay on the operator's own machine and `submit_report` is the only publisher; sanitizing the local copy would make the saved artifact disagree with the one a maintainer receives. |
| T-nbb-09 | Spoofing | a firmware line misattributed as a host line after a logger rename | low | mitigate | `FIRMWARE_LOGGER_NAME` is compared against `serial_comm.rurp_logger.name` by a test (Task 2), so a rename on either side fails loudly. |
| T-nbb-SC | Tampering | npm/pip/cargo installs | low | accept | No package manager runs. The module is stdlib-only and no dependency is added, so the package-legitimacy gate has nothing to audit. |
</threat_model>

<verification>
Run the whole suite on the 3.11 interpreter — never the devcontainer's 3.12, which masks CI:

```bash
cd /workspaces/firestarter_app && ./.venv311/bin/python -m pytest -o addopts="" -q
```

Then the lint and type gates, and the comment gate:

```bash
cd /workspaces/firestarter_app && ./.venv311/bin/python -m ruff check firestarter tests
cd /workspaces/firestarter_app && ./.venv311/bin/python -m ruff format --check firestarter tests
cd /workspaces/firestarter_app && D=$(git diff 2acf5d3 -- firestarter/) || exit 1; printf '%s\n' "$D" \
  | /usr/bin/grep -E '^\+' | /usr/bin/grep -v '^+++' \
  | /usr/bin/grep -E '^\+[[:space:]]*#' | /usr/bin/grep -vE '(noqa|type:|pragma)' | wc -l
```

`2acf5d3` is the `firestarter_app` submodule HEAD at planning time. Anchoring there rather than
on a bare `git diff` is load-bearing: once a task commits, an unanchored working-tree diff is
empty and the gate prints `0` for work it never looked at.

Do not pipe a pytest run into `head` — a pipe masks the exit code and a failed run reads green.

Falsifiability audit, to be recorded in the SUMMARY. For every new test, name how it was observed
red:

| Kind | RED evidence |
|---|---|
| The fourteen bound/attribution properties in Task 2 | Written before the implementation; paste the observed failure lines |
| The end-to-end tracer in Task 1 | Red before the `dev_test` wiring exists, because the key is absent from the artifact |
| The scrub, fence and dedup proofs in Task 3 | Observed red by planting the vector against the unhardened normalizer; paste the observed failure line |
| The `_TO_DICT_KEYS` pin | Already red on arrival the moment the key is added and the pin is not — record that it was seen red before the pin was updated |

A test whose red evidence cannot be produced does not ship. Delete it rather than carry it.
</verification>

<success_criteria>
- `cd /workspaces/firestarter_app && ./.venv311/bin/python -m pytest -o addopts="" -q` exits 0.
- `ruff check` and `ruff format --check` over `firestarter tests` are both clean.
- The strict-island mypy run reports `Found 1 error` and zero errors in `log_capture.py` or `cli_handlers.py`.
- The comment gate prints `0`.
- A `dev test` run's saved `.json` carries a `log_capture` block whose entries name their step, their source and their level.
- `dropped` and `truncated` are non-zero only when lines were genuinely lost, and both reach the markdown section heading.
- The markdown diagnostics section is byte-identical between the saved `.md` and the filed issue body.
- `dedup_fingerprint` is unchanged by the contents of the block.
- The SUMMARY records the five design decisions D-01 to D-05, the rejected drop-middle alternative, the red evidence table, and the fact that the local artifacts stay unsanitized by design.
</success_criteria>

<output>
Create `.planning/quick/260916-nbb-capture-the-actual-error-and-warn-log-lines-the-host-app-and/260916-nbb-SUMMARY.md` when done.
</output>
