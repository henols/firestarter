---
phase: quick-260916-nbc
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - .claude/skills/devtest-triage/scripts/firmware_messages.py
  - .claude/skills/devtest-triage/scripts/devtest_issues.py
  - .claude/skills/devtest-triage/scripts/tests/test_firmware_messages.py
  - .claude/skills/devtest-triage/scripts/tests/test_devtest_issues.py
  - .claude/skills/devtest-triage/fixtures/dev-test-error-codes-populated.md
  - .claude/skills/devtest-triage/SKILL.md
autonomous: true
requirements: [260916-nbc]

estimate:
  tokens: 55000
  raw_tokens: 110000
  tasks: 3
  confidence: high

must_haves:
  truths:
    - "`show` prints an `error` column for every step row, carrying the report's `error_code` verbatim in decimal plus the symbolic `MSG_*` name the skill resolves itself."
    - "A step whose `error_code` is null or absent renders `-` in that column; every other cell of that row is unchanged from today's output."
    - "A code the owned table does not know renders `NNN unknown` — the row still prints, nothing raises, nothing is dropped."
    - "An `error_code` that is not a plain int in 0..255 renders `?`, and the untrusted value itself is never echoed into the output."
    - "A body carrying `error_name` has that name rendered; when the reported name disagrees with the owned table, BOTH are shown as `NNN REPORTED (table: RESOLVED)`."
    - "`show` resolves names with `firestarter_app` absent: no module under `.claude/skills/devtest-triage/scripts/` has a runtime dependency on it — no `import firestarter_app`/`firestarter`/`messages`, no dynamic import, and every `subprocess` call still takes a literal argv whose first element is `gh` (DD-7). `DEFAULT_DB`'s path string is explicitly NOT such a dependency and stays as it is."
    - "The drift test FAILS when the owned table and the app's `CATALOG` disagree, and SKIPS with a printed reason (never fails) when `firestarter_app/firestarter/messages.py` is absent."
    - "The drift comparator is proven non-vacuous by a negative control, and the skip predicate is proven reachable by a direct call on a nonexistent root."
    - "The runtime-coupling scanner is proven non-vacuous by a negative control that plants each forbidden import shape into a synthetic module and asserts every one is caught."
    - "The full skill test suite still passes — 39 pre-existing tests plus the new ones, zero failures."
    - "Both frozen pre-2.0 fixtures are byte-identical to their pre-task content."
  artifacts:
    - .claude/skills/devtest-triage/scripts/firmware_messages.py
    - .claude/skills/devtest-triage/scripts/tests/test_firmware_messages.py
    - .claude/skills/devtest-triage/fixtures/dev-test-error-codes-populated.md
  key_links:
    - "`cmd_show`'s step loop in `devtest_issues.py` -> `firmware_messages.resolve_error()` — the single call site, the only place a code becomes a printable cell."
    - "owned `MESSAGE_NAMES` -> `CATALOG` in `firestarter_app/firestarter/messages.py`, joined ONLY by the ast drift test, never by a runtime import."
    - "SKILL.md sec2 sample output -> the real `show` output, regenerated from the command it publishes rather than hand-written."
---

<objective>
Teach `devtest_issues.py show` to print each step's firmware error code and its symbolic
message name, resolving the name from a table the skill owns outright.

Purpose: the ten `dev test` issues open today all carry `error_code` in their JSON block and
none of them carry a name. Triage currently has to hand-parse the JSON to learn that `write`
failed with 183. Those ten bodies will never be regenerated, so resolving the integer locally
is the only thing that makes them readable — a report-supplied `error_name` is a bonus, not a
dependency.

Output: a new stdlib-only `firmware_messages.py` owning the id-to-name table and the render
contract, that table wired into `show`'s step table, an ast-based drift test against the app's
generated `messages.py`, a new hand-authored fixture carrying real codes, and SKILL.md's
published sample output brought back in step with what the command actually prints.
</objective>

<execution_context>
@/workspaces/.claude/gsd-core/workflows/execute-plan.md
@/workspaces/.claude/gsd-core/templates/summary.md
</execution_context>

<context>
@/workspaces/CLAUDE.md
@/workspaces/.claude/skills/devtest-triage/SKILL.md
@/workspaces/.claude/skills/devtest-triage/scripts/devtest_issues.py
@/workspaces/.claude/skills/devtest-rootcause/scripts/tests/test_infoic_lookup.py
</context>

<design_decisions>

These were settled during planning against the real files. Do not re-litigate them; implement them.

## DD-1. The owned table mirrors `CATALOG` ONLY — `DEBUG_CATALOG` is deliberately excluded

`firestarter_app/firestarter/messages.py` defines TWO module-level id-to-name dicts, not one:

| dict | entries | name prefix |
|---|---|---|
| `CATALOG` | 79 | `MSG_*` |
| `DEBUG_CATALOG` | 54 | `DBG_*` |

They are **separate id spaces and they collide**: 9 ids appear in both with different meanings
(`0x00`-`0x05`, `0x10`, `0x20`, `0x30`; e.g. `0x01` is `MSG_OK_READY` in one and
`DBG_FIRMWARE_VERSION` in the other). A step's `error_code` is the firmware `response.id`
captured off `EpromOperationError.error_code` (see `chip_test.py`, the `error_code` docstring
near the `StepResult` dataclass), which is a `CATALOG` id. Merging the two dicts would make
resolution ambiguous on exactly those 9 ids and would silently mislabel one of them.

So: the owned table is `CATALOG` and nothing else. Pin the exclusion with a test asserting the
colliding ids resolve to their `MSG_*` names and that no value in the owned table starts with
`DBG_`.

## DD-2. The drift check parses with `ast`, never imports

`tests/test_firmware_messages.py` locates `firestarter_app/firestarter/messages.py` from its own
`__file__` (never the cwd), `ast.parse`s it, and walks the `CATALOG` `AnnAssign` node pulling the
`name=` keyword out of each `MessageDef(...)` call. `ast.literal_eval` on the dict does NOT work
here (the values are `Call` nodes) — this differs from the `VPP_MV` precedent in
`devtest-rootcause/scripts/tests/test_infoic_lookup.py`, which is otherwise the template for this
whole test: locator from `__file__`, skip-with-reason when the submodule is absent, and a
negative control proving the comparator is not unconditionally empty.

When `firestarter_app` is not checked out the test SKIPS. It never fails, and `show` never
notices, because the table is a literal in the skill's own module.

## DD-3. The render contract for `resolve_error(code, reported_name=None) -> str`

| Input | Cell |
|---|---|
| `error_code` absent or `None` | `-` |
| not an `int`, or a `bool`, or outside `0..255` | `?` |
| int in the owned table, no usable `error_name` | `183 MSG_ERR_OP_TIMEOUT` |
| int NOT in the owned table, no usable `error_name` | `183 unknown` |
| usable `error_name`, code not in the table | `183 MSG_SOMETHING_NEW` |
| usable `error_name` equal to the table's answer | `183 MSG_ERR_OP_TIMEOUT` |
| usable `error_name` disagreeing with the table | `183 MSG_SOMETHING (table: MSG_ERR_OP_TIMEOUT)` |

"Usable `error_name`" means a `str` matching `^[A-Za-z0-9_]{1,40}$`. Anything else — wrong type,
control characters, 4 KB of text, markup — is discarded silently and the table's answer is used.
This is how the item's "prefer the report's name when it has one" and the standing untrusted-body
posture are both honoured: the reported name is preferred for display, but it can never introduce
an unbounded or non-identifier string into the output, and it can never quietly overwrite a name
the skill can prove.

`bool` is excluded explicitly — `True` is an `int` in Python and would otherwise resolve to id 1.
The `0..255` gate is what stops a JSON bignum in a hostile body from being printed at all.

The decimal form is printed exactly as the body carries it, so a triager can grep the same token
straight out of the JSON block.

## DD-4. Column placement and widths

The new column goes between `verdict` and `reason` in the existing step table. Build both the
header and the rows from the SAME widths so they cannot drift:

    header: f"  {'step':<12} {'verdict':<10} {'error':<28} reason"
    row:    f"  {op:<12} {v:<10} {err:<28} {reason}"

28 is sized to `185 MSG_ERR_CHIP_ID_MISMATCH`, which is 28 characters exactly. Four
error-severity names are longer and overflow their cell, pushing `reason` right on that one row
(`MSG_ERR_PROTOCOL_NOT_IMPLEMENTED`, `MSG_ERR_FL4_BOOT_BLOCK_LOCKED`, `MSG_ERR_FL4_VERIFY_TIMEOUT`,
`MSG_ERR_MEM_SIZE_TOO_SMALL`) — accepted deliberately: a truncated message name is worse than a
ragged line, and no cell is ever cut. `reason` keeps its existing `[:90]` truncation — do not
change it.

The `ROUTE:` line keeps bare op names. Nothing there changes.

## DD-5. Fixtures

Both existing fixtures under `fixtures/` are FROZEN, carry `error_code: null` on every step, and
their own headers forbid regenerating them. Do not edit them, do not regenerate them — they are
what proves the `-` cell renders correctly.

Add ONE new hand-authored fixture, `fixtures/dev-test-error-codes-populated.md`, carrying real
codes (write 183, verify 175, blank-check 185) and NO `error_name` key — the exact shape of the
ten reports open today. Its header must say plainly that it is hand-authored test data modelled
on that shape, not a real community report and not evidence about any chip.

The post-`error_name` case (the shape sibling item 260916-nb9 will produce) is covered by a body
built inline in the test module. It does not get a third fixture file.

## DD-6. `depends_on` is empty

Sibling 260916-nb9 adds `error_name` to the report. This plan must work on bodies that predate
it, so it must not wait on it; and it touches no file any sibling touches.

## DD-7. "Self-contained" means NO RUNTIME COUPLING — it does not mean the string is absent

The property this skill actually advertises is that `show` keeps working when `firestarter_app`
is not checked out. That is a statement about what the module *does at runtime*, not about which
words appear in its text. Measured on the current unmodified `devtest_issues.py`, the bare
substring `firestarter_app` occurs FOUR times, and all four are correct and out of this plan's
scope:

| line | occurrence | why it stays |
|---|---|---|
| 6 | module docstring | it is the sentence that *states* the property |
| 40 | `_repo_root()` checkout probe | `os.path.isdir` test, no import, no exec |
| 45 | `DEFAULT_DB` path join | locates an OPTIONAL json file for `fold`/`list`; absent file just means no db_diff |
| 53 | comment on `NOT_REPORTED` | explains why the constant is duplicated rather than imported |

A text-substring check would therefore be RED forever and could only be made GREEN by deleting
correct code. Do not write one. The checkable property is instead, for BOTH
`firmware_messages.py` and `devtest_issues.py`, parsed with `ast`:

1. No `Import`/`ImportFrom` node whose root module is `firestarter_app`, `firestarter` or
   `messages`. (Relative imports, `level > 0`, are fine — they stay inside the scripts dir.)
2. No call to `__import__` and no call to an `import_module` attribute.
3. Every `subprocess.<fn>(...)` call takes a LITERAL list as its first argument whose first
   element is the constant `"gh"` — so nothing can shell out to a firestarter script, and
   T-nbc-03's "fixed argv lists" claim stops being an assertion and becomes a gate.

All three already hold on today's `devtest_issues.py`: import roots are exactly
`{__future__, argparse, json, os, re, subprocess, sys}`, there are zero dynamic imports, and the
module's single `subprocess` call has `argv[0] == "gh"`. So the check is satisfiable the moment
it is written, and the only thing that can redden it is new code — which is the point.

`DEFAULT_DB` is explicitly tolerated. Do not "fix" it, do not route around it, do not mention it
in the assertion's failure message as though it were a violation.

## DD-8. Verify legs are one command each, and every one must be able to go RED

No `<automated>` leg chains commands with `;` — a `;` chain reports only the LAST command's
status, so a leg like `run-suite; grep; show; git diff --stat` passes even when the suite is
broken (measured: `sh -c 'false; false; true'` exits 0). Where a leg needs more than one step it
chains with `&&`, and where it needs more than one assertion it becomes more than one leg.

Traps this project has already paid for, all of which apply here:

  - `grep -c` exits 1 on a zero count, so it cannot be used to assert "zero". Count with `wc -l`
    and compare, or assert with `grep -q`.
  - `grep -qF 'A' -e 'B' -e 'C'` is an OR — it exits 0 on ANY one match. Requiring all three means
    three `&&`-chained `grep -qFe` calls, or a `wc -l` count compared to 3.
  - `grep -qF` with a dash-leading pattern exits 2. Always spell it `-qFe <pattern>`.
  - The devcontainer's `grep` is ugrep and honors `.gitignore`, silently under-scanning. Every leg
    here calls `/usr/bin/grep` explicitly.
  - `git diff --stat` exits 0 whether or not anything differs. To gate on "unchanged" use
    `git diff --quiet HEAD -- <paths>`, which exits 1 on a difference and covers staged changes
    too.

Each leg below was smoke-tested against the pre-change tree and observed to exit non-zero. A leg
that cannot be shown to go RED first is not a gate.
</design_decisions>

<tasks>

<task type="tracer">
  <name>Task 1: End-to-end — a known code renders as name in `show`, one path only</name>
  <files>.claude/skills/devtest-triage/scripts/firmware_messages.py, .claude/skills/devtest-triage/scripts/devtest_issues.py, .claude/skills/devtest-triage/fixtures/dev-test-error-codes-populated.md</files>
  <read_first>.claude/skills/devtest-triage/scripts/devtest_issues.py (module header, the constants block around `MAX_BODY`/`NOT_REPORTED`, and `cmd_show`), .claude/skills/devtest-triage/fixtures/dev-test-at28c256-null-identity.md (the body shape to model the new fixture on)</read_first>
  <action>
Wire one code through every layer: owned table -> resolver -> step row -> CLI stdout.

Create `scripts/firmware_messages.py`, stdlib-only, no imports outside the standard library.
Module docstring states: the table is transcribed from `CATALOG` in the app's generated
`messages.py`; `DEBUG_CATALOG` is excluded on purpose because it is a separate id space that
collides with `CATALOG` on nine ids (per DD-1); the copy exists so this skill keeps working with
`firestarter_app` absent, and `tests/test_firmware_messages.py` is what detects the two drifting
apart. Mirror the wording style of `infoic_lookup.py`'s owned-table docstring in the sibling
skill.

Define `MESSAGE_NAMES: dict[int, str]` as a literal holding all 79 `CATALOG` entries, keys as hex
literals, values the full `MSG_*` names. Generate the literal once rather than typing it — run an
`ast` extraction over `firestarter_app/firestarter/messages.py` at implementation time, pretty-print
the pairs, and paste the result in. The committed module must contain the literal dict; it must
NOT extract anything at import time.

Define `resolve_error(code, reported_name=None) -> str` implementing DD-3 in full. Keep it pure:
no I/O, no subprocess, no exceptions escaping — every rejected input falls through to `?` or the
table answer.

In `devtest_issues.py`, add a plain `import firmware_messages` alongside the existing stdlib
imports (the script's own directory is `sys.path[0]` when run as `python3 <path>/devtest_issues.py`,
and the test suite already inserts `_SCRIPTS_DIR` — no `sys.path` juggling, and no fallback import
of anything in `firestarter_app`). In `cmd_show`'s step loop, read `s.get("error_code")` and
`s.get("error_name")`, pass both to `resolve_error`, and print the row and header with DD-4's
widths.

Add `fixtures/dev-test-error-codes-populated.md` per DD-5: title-parseable body (`[dev test]
w27c512 - FAIL` works; `parse_title` accepts a plain hyphen), a fenced JSON block carrying
`schema_version`, `generated`, `dedup_fingerprint`, `auto_capture`, and a `steps` array where
`write` carries 183, `verify` 175, `blank-check` 185, and the passing steps carry `error_code:
null`. No `error_name` key anywhere in this fixture.
  </action>
  <verify>
    <automated>sh -c 'cd /tmp && OUT=$(python3 /workspaces/.claude/skills/devtest-triage/scripts/devtest_issues.py show --body-file /workspaces/.claude/skills/devtest-triage/fixtures/dev-test-error-codes-populated.md --title "[dev test] w27c512 - FAIL") && printf "%s\n" "$OUT" | /usr/bin/grep -qFe "183 MSG_ERR_OP_TIMEOUT" && printf "%s\n" "$OUT" | /usr/bin/grep -qFe "175 MSG_ERR_VERIFY" && printf "%s\n" "$OUT" | /usr/bin/grep -qFe "185 MSG_ERR_CHIP_ID_MISMATCH"'</automated>
    <automated>sh -c 'cd /tmp && python3 /workspaces/.claude/skills/devtest-triage/scripts/devtest_issues.py show --body-file /workspaces/.claude/skills/devtest-triage/fixtures/dev-test-at28c256-null-identity.md --title "[dev test] at28c256 - FAIL"' | /usr/bin/grep -qEe '^  step +verdict +error +reason$'</automated>
  </verify>
  <done>Running `show` from a directory outside the checkout prints all three codes with their resolved names in the step table. Running it against `fixtures/dev-test-at28c256-null-identity.md` still succeeds and shows `-` in the new column on every row.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Pin the null, unknown, hostile and reported-name edges</name>
  <files>.claude/skills/devtest-triage/scripts/tests/test_firmware_messages.py, .claude/skills/devtest-triage/scripts/tests/test_devtest_issues.py, .claude/skills/devtest-triage/scripts/firmware_messages.py</files>
  <read_first>.claude/skills/devtest-triage/scripts/tests/test_devtest_issues.py (the `issue()` body builder and the sys.path preamble both new tests must reuse)</read_first>
  <behavior>
Resolver cases, one test each, asserting the exact cell string from DD-3:
    - `resolve_error(None)` and a step dict with no `error_code` key -> `-`
    - `resolve_error(183)` -> `183 MSG_ERR_OP_TIMEOUT`
    - `resolve_error(0x99)` (a real in-range gap in the catalog) -> `153 unknown`
    - `resolve_error("183")`, `resolve_error(True)`, `resolve_error(-1)`, `resolve_error(256)`,
      `resolve_error(10**40)` -> `?` in every case, and the input never appears in the output
    - `resolve_error(183, "MSG_ERR_OP_TIMEOUT")` -> `183 MSG_ERR_OP_TIMEOUT`
    - `resolve_error(183, "MSG_SOMETHING")` -> `183 MSG_SOMETHING (table: MSG_ERR_OP_TIMEOUT)`
    - `resolve_error(0x99, "MSG_BRAND_NEW")` -> `153 MSG_BRAND_NEW`
    - a `reported_name` that is not a str, is empty, is 41+ chars, or carries a space, a
      newline, a backtick or a shell metacharacter -> discarded, table answer used, and the
      rejected text never appears in the output
Rendered-row cases through `cmd_show` itself, stdout captured with `contextlib.redirect_stdout`
and a body written under `tempfile`, `args.number = None` so no `gh` call is possible:
    - the header line carries `error` between `verdict` and `reason`
    - a body whose failing steps carry 183/175/185 prints all three resolved names
    - a body whose steps all carry `error_code: null` prints `-` on every row and leaves
      the `ROUTE:` line byte-identical to today's
    - a body carrying `error_name` on a step renders the reported name
  </behavior>
  <action>
Create `tests/test_firmware_messages.py` for the resolver cases and extend
`tests/test_devtest_issues.py` with the rendered-row cases. Both reuse the existing preamble that
puts `_SCRIPTS_DIR` on `sys.path`; `test_devtest_issues.py`'s new cases build bodies through its
existing `issue()` helper where the shape allows, extending that helper to accept optional
per-step `error_code`/`error_name` rather than hand-building a parallel body dict.

Write the tests first and watch them fail against Task 1's code, then close whatever gaps the
failures expose in `resolve_error`. No network, no `gh`, no writes outside `tempfile` — the suite
header's standing promise.
  </action>
  <verify>
    <automated>python3 -m unittest discover -s /workspaces/.claude/skills/devtest-triage/scripts/tests -t /workspaces/.claude/skills/devtest-triage/scripts/tests</automated>
    <automated>sh -c 'N=$(python3 -m unittest discover -s /workspaces/.claude/skills/devtest-triage/scripts/tests -t /workspaces/.claude/skills/devtest-triage/scripts/tests 2>&1 | /usr/bin/sed -n "s/^Ran \([0-9]*\) tests.*/\1/p"); [ -n "$N" ] && [ "$N" -gt 39 ]'</automated>
  </verify>
  <done>The suite exits 0 on its own status (no grep laundering the exit code), the `Ran N tests` count is strictly greater than the 39 measured before this plan, and every DD-3 row has a named test asserting its exact cell string.</done>
</task>

<task type="auto">
  <name>Task 3: Drift check against the app catalog, self-containment guard, and SKILL.md sync</name>
  <files>.claude/skills/devtest-triage/scripts/tests/test_firmware_messages.py, .claude/skills/devtest-triage/SKILL.md</files>
  <read_first>.claude/skills/devtest-rootcause/scripts/tests/test_infoic_lookup.py (the locator, skip-with-reason and negative-control pattern to follow), .claude/skills/devtest-triage/SKILL.md (section 2 "Parse the report" and the Troubleshooting table)</read_first>
  <action>
Add the drift suite to `tests/test_firmware_messages.py` per DD-2. Put the drift, negative-control,
reachability and exclusion cases in a class named exactly `CatalogDriftTest`, and the
runtime-coupling cases in a class named exactly `SelfContainmentTest` — Task 3's verify legs
invoke both by name (`python3 -m unittest test_firmware_messages.<Class>`), which is what proves
each suite is reachable rather than silently collected-and-empty. Rename neither.

  - `_find_messages(root=None)` resolves `firestarter_app/firestarter/messages.py` from this
    file's own path, returns `None` when the file is absent. Take the root as an argument so the
    absent branch is directly callable.
  - `extract_catalog_via_ast(path)` returns `{id: name}` from the `CATALOG` `AnnAssign` only,
    reading the `name=` keyword of each `MessageDef(...)` call. It raises `LookupError` naming the
    file when no `CATALOG` assignment is found, and it must not touch `DEBUG_CATALOG`.
  - `table_drift(a, b)` returns one line per disagreeing key, naming the key in hex.
  - The drift test skips with a printed reason when `_find_messages()` is `None`; otherwise it
    asserts `table_drift(MESSAGE_NAMES, extract_catalog_via_ast(path)) == []`.
  - A negative control perturbs a copy of the owned table by one key and asserts the comparator
    reports it, naming that key — the comparator must be proven non-vacuous, not assumed.
  - A reachability test asserts `_find_messages("/nonexistent-root")` is `None`, so the skip leg
    is proven to be reachable rather than authored blind.
  - An exclusion test asserts every colliding id (`0x00`-`0x05`, `0x10`, `0x20`, `0x30`) resolves
    to its `MSG_*` name and that no value in `MESSAGE_NAMES` starts with `DBG_`.
  - A runtime-coupling suite, `SelfContainmentTest`, enforcing DD-7 over BOTH
    `firmware_messages.py` and `devtest_issues.py`. It must NOT grep for the substring
    `firestarter_app` — that string legitimately occurs four times in `devtest_issues.py` today
    (docstring, `_repo_root` probe, `DEFAULT_DB`, a comment) and a substring test would be
    unsatisfiable. Build it on `ast` instead, on the source text, never importing the app:

      * `_import_roots(path) -> set[str]` — `ast.parse` the file, walk it, collect the root
        module of every `ast.Import` alias and of every absolute `ast.ImportFrom`
        (`node.level == 0`). Relative imports are in-package and are ignored.
      * `_dynamic_imports(path) -> list[str]` — any `ast.Call` to the name `__import__` or to an
        attribute named `import_module`.
      * `_subprocess_argv0(path) -> list` — for every `ast.Call` whose func is a `subprocess.*`
        attribute, the first element of a literal-list first argument, or a `NON-LITERAL` marker
        when the argv is not a literal list.
      * `test_no_runtime_coupling_to_firestarter_app`: for each of the two modules, assert
        `_import_roots(p) & {"firestarter_app", "firestarter", "messages"} == set()`, assert
        `_dynamic_imports(p) == []`, and assert every entry of `_subprocess_argv0(p)` equals
        `"gh"`. Failure messages name the module and the offending node — and must never point at
        `DEFAULT_DB`, which is a path string, not a dependency, and is expected to stay.
      * `test_import_scanner_detects_a_planted_import`: the negative control. Write each of
        `import firestarter_app`, `from firestarter_app.firestarter import messages` and
        `import firestarter.messages` to a `tempfile` module and assert `_import_roots` flags
        every one. Without this the scanner could be silently vacuous.

    Measured on the pre-change tree, `devtest_issues.py` already satisfies all three clauses —
    import roots are exactly `{__future__, argparse, json, os, re, subprocess, sys}`, no dynamic
    imports, single `subprocess` call with `argv[0] == "gh"` — so this suite is satisfiable on
    day one and only new code can redden it.

Then bring SKILL.md back in step with reality. Section 2 publishes a verbatim reproduction of
`show`'s output and that block is now wrong:

  - Regenerate the section 2 sample block by RUNNING the `--body-file` command it already
    publishes against `fixtures/dev-test-at28c256-null-identity.md` and pasting the real output.
    Do not hand-edit it into shape.
  - Add a short second block, generated the same way from the new populated fixture, showing what
    a report carrying real codes looks like, and name the new fixture as its source.
  - Add two or three lines of prose giving the sentinels: `-` means the report carried no code for
    that step, `unknown` means the code is newer than this skill's table, `?` means the body's
    `error_code` was not a plain integer in 0..255 and was not trusted, and
    `NNN NAME (table: OTHER)` means the report's own `error_name` disagrees with the table.
  - Add two Troubleshooting rows: one for `unknown` (the code post-dates the table — run the skill
    suite, the drift test names it) and one for `?` (malformed or hostile body — read the JSON
    block by hand).
  - Keep the "Self-contained" paragraph true: it now also covers the owned message table.
  </action>
  <verify>
    <automated>python3 -m unittest discover -s /workspaces/.claude/skills/devtest-triage/scripts/tests -t /workspaces/.claude/skills/devtest-triage/scripts/tests</automated>
    <automated>sh -c 'cd /workspaces/.claude/skills/devtest-triage/scripts/tests && python3 -m unittest -v test_firmware_messages.SelfContainmentTest'</automated>
    <automated>sh -c 'cd /workspaces/.claude/skills/devtest-triage/scripts/tests && python3 -m unittest -v test_firmware_messages.CatalogDriftTest'</automated>
    <automated>sh -c 'cd /tmp && python3 /workspaces/.claude/skills/devtest-triage/scripts/devtest_issues.py show --body-file /workspaces/.claude/skills/devtest-triage/fixtures/dev-test-at28c256-null-identity.md --title "[dev test] at28c256 - FAIL"' | /usr/bin/grep -qEe '^  step +verdict +error +reason$'</automated>
    <automated>git -C /workspaces diff --quiet HEAD -- .claude/skills/devtest-triage/fixtures/dev-test-at28c256-null-identity.md .claude/skills/devtest-triage/fixtures/dev-test-at28c256-populated-identity.md</automated>
  </verify>
  <human-check>SKILL.md's two section-2 sample blocks are byte-identical to what the `--body-file` commands printed above them actually output. This is not machine-checkable without the doc itself becoming a generated artifact with its own generator and gate, which is out of scope for this item — so it is a human read, not a fake automated leg.</human-check>
  <done>The full suite exits 0 on its own status; `SelfContainmentTest` and `CatalogDriftTest` each pass when named directly, so neither is an unreachable stub; `show` against the frozen null fixture prints the four-column header with `error` between `verdict` and `reason`; `git diff --quiet HEAD` over the two frozen fixtures exits 0, proving them untouched including any staged change; and a human has confirmed SKILL.md's two sample blocks match real command output.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| GitHub issue body -> `extract_report` -> `cmd_show` | Community-authored, wholly untrusted. This plan adds two NEW body-controlled fields to the parse surface: `steps[].error_code` and `steps[].error_name`. |
| `cmd_show` stdout -> operator terminal / downstream agent | Rendered cells are read by a human and by a triage agent; a forged name is a wrong-conclusion vector, not just cosmetic. |
| repo file `firestarter_app/firestarter/messages.py` -> drift test | Repo-local and trusted for content, but executing it would couple the skill to the submodule and break the self-contained property the skill advertises. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-nbc-01 | Spoofing | `resolve_error` `reported_name` path | medium | mitigate | Allowlist `^[A-Za-z0-9_]{1,40}$`; anything else discarded and the owned table's answer used. A reported name that disagrees with the table is rendered `NNN REPORTED (table: RESOLVED)` so the disagreement is visible, never silently trusted (DD-3, Task 2). |
| T-nbc-02 | Denial of Service | `resolve_error` `code` path | medium | mitigate | `error_code` accepted only as a non-bool `int` in `0..255`; a JSON bignum or a 4 KB string renders `?` and is never echoed. The 40-char name bound caps the other field. `MAX_BODY` stays in force upstream (Task 1, Task 2). |
| T-nbc-03 | Elevation of Privilege | new parse surface in `cmd_show` | high | mitigate | No new subprocess, no `eval`/`exec`, no format-string evaluation, no body text interpolated into any command. `resolve_error` is pure and total. `gh` keeps receiving fixed argv lists — this plan adds no `gh` call at all. Pinned mechanically by `SelfContainmentTest`'s `_subprocess_argv0` clause in Task 3, which asserts every `subprocess.*` call has a literal argv headed by `"gh"` (DD-7), so this row is a gate rather than a claim. |
| T-nbc-04 | Tampering | drift test reading `messages.py` | medium | mitigate | `ast.parse` only, never `import` — importing would execute submodule code inside the skill's test run. Path derived from `__file__`, never the cwd; absent submodule SKIPS (DD-2, Task 3). |
| T-nbc-05 | Repudiation | owned `MESSAGE_NAMES` going stale | medium | mitigate | A reassigned id would resolve to a confidently wrong name and misdirect triage. The ast drift test plus its negative control detect divergence; an id the table does not know renders `unknown` rather than guessing (Task 3). |
| T-nbc-06 | Information Disclosure | rendered output | low | accept | Cells carry only message ids and identifier-shaped names already present in a public issue. No secret, path or token is introduced. |
| T-nbc-SC | Tampering | npm/pip/cargo installs | high | accept | No package-manager install task exists in this plan. `firmware_messages.py` and both test modules are stdlib-only, and no dependency is added to any manifest — so the package-legitimacy gate has no surface here. |
</threat_model>

<verification>
- `python3 -m unittest discover -s .claude/skills/devtest-triage/scripts/tests -t .claude/skills/devtest-triage/scripts/tests` exits 0 ON ITS OWN STATUS — not piped into a grep that launders the exit code — with more than 39 tests (39 measured before this plan).
- The drift test passes with `firestarter_app` checked out, and skips with a printed reason when it is not. It is present in this tree, so the drift comparison genuinely runs rather than skipping.
- `show` renders the new column correctly for all four body shapes: real codes, all-null codes, an out-of-table code, and a body carrying `error_name`.
- Neither script acquires a RUNTIME dependency on `firestarter_app` per DD-7 — no forbidden import root, no dynamic import, every `subprocess` argv still literal and `gh`-headed. The pre-existing `DEFAULT_DB` path string and the docstring/comment prose are expected to remain and are not violations. `show` runs from a cwd outside the checkout.
- The two frozen fixtures are unmodified, gated with `git diff --quiet HEAD` (which exits 1 on a difference) rather than `--stat` (which never does).
- SKILL.md's two sample blocks are the real output of the commands printed above them — a human-verify item, not an automated leg.
</verification>

<success_criteria>
Triage can read `show <n>` on any of the ten currently-open issues and see, per failing step, the
firmware error code exactly as the body carries it and the message name the skill resolved itself
— with no `firestarter_app` import, no regenerated fixture, and a test that will fail the day the
app's catalog and the skill's copy disagree.
</success_criteria>

<output>
Create `.planning/quick/260916-nbc-teach-the-triage-skill-s-own-parser-to-print-the-firmware-er/260916-nbc-SUMMARY.md` when done.
</output>
