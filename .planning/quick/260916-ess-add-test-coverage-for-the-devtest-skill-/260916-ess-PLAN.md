---
phase: quick-260916-ess
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - .claude/skills/devtest-triage/scripts/tests/_mutation.py
  - .claude/skills/devtest-triage/scripts/tests/test_devtest_issues.py
  - .claude/skills/devtest-triage/scripts/tests/test_eprom_ledger.py
  - .claude/skills/devtest-rootcause/scripts/tests/test_infoic_lookup.py
  - .claude/skills/devtest-triage/SKILL.md
  - .claude/skills/devtest-rootcause/SKILL.md
autonomous: true
requirements: [260916-ess]

estimate:
  tokens: 78000
  raw_tokens: 39000
  tasks: 3
  confidence: low

must_haves:
  truths:
    - "`python3 -m unittest discover` over both skills' tests directories exits 0, and one command runs both."
    - "Every test in the suite has been observed RED. For the pure-logic properties the RED observation is permanent and executable: a mutation guard re-derives it on every run."
    - "Each mutation guard asserts its anchor string occurs exactly once in the module under test, so a refactor that dissolves the anchor fails the suite loudly instead of silently disarming the guard."
    - "All nine documented `supersedes()` outcomes are pinned: the qualifying close, leg 1 (earlier report), leg 2 (same build, older host, older firmware), leg 3 (failing step NA, failing step absent), the firmware-not-comparable caveat, and the host-not-comparable refusal."
    - "The three-leg close is exercised through the real path a `gh` payload takes: issue dict -> `_summarize()` -> `supersedes()`. No test constructs a `supersedes()` argument by hand."
    - "`render()` -> `read_records()` is proven to round-trip every authored field of every row, and `render()` is proven idempotent on its own output."
    - "The Notes section survives a rewrite byte for byte."
    - "A record the database does not know is dropped from the render AND reported on stderr — the silent-drop path is asserted to be non-silent."
    - "No test requires `firestarter_app`. Ledger tests build a synthetic chip database in a temp directory; the one test that genuinely needs the generator calls `skipTest` with the reason printed."
    - "The `VPP_MV` table in `infoic_lookup.py` is compared against the generator's table extracted with `ast.literal_eval` — the generator is never imported."
    - "No test performs network I/O, invokes `gh`, or writes outside a temp directory."
    - "Both SKILL.md files state the one command that runs the tests and state plainly that nothing runs them automatically."
  artifacts:
    - .claude/skills/devtest-triage/scripts/tests/_mutation.py
    - .claude/skills/devtest-triage/scripts/tests/test_devtest_issues.py
    - .claude/skills/devtest-triage/scripts/tests/test_eprom_ledger.py
    - .claude/skills/devtest-rootcause/scripts/tests/test_infoic_lookup.py
  key_links:
    - "`supersedes()` -> `gh issue close` on a stranger's issue (the only irreversible outward action either skill takes)"
    - "`ROW_RE` + `render()` -> the tracked file VALIDATED-EPROMS.md (a parser regression silently deletes validated-chip history)"
    - "`extract_report()` -> untrusted community-authored issue bodies"
    - "`infoic_lookup.VPP_MV` -> `firestarter_app/tools/build_db.py:VPP_MV` (a private copy with no drift detector)"
    - "tests directory layout -> the `unittest discover` one-liner published in both SKILL.md files"
---

<objective>
Give the two risk-carrying devtest skill scripts a stdlib-only `unittest` suite that can
actually fail, and say honestly where it runs.

`supersedes()` gates an irreversible outward action — closing a community member's GitHub
issue — on three legs that no test has ever exercised. `eprom_ledger.py` rewrites the tracked
file `VALIDATED-EPROMS.md` from a regex, so a parser regression deletes validated-chip
history with no diff to warn anyone. Those two get the coverage. `diff_db.py` (1000 lines,
reports only) gets none, deliberately.

Purpose: two self-tests were deleted from these skills this morning because neither could
observe what it claimed to verify — both exited 0 against a SKILL.md gutted to one line of
garbage. This plan's whole design constraint is that the same thing cannot happen again:
every pure-logic property carries a **mutation guard** that loads a deliberately broken copy
of the module under test and asserts the property fails on it. The RED demonstration is not a
note in a commit message; it is a test that runs every time.

Output: three test modules and one helper, living inside the skills they test, runnable by
one command, plus a line in each SKILL.md saying what that command is and that no CI runs it.
</objective>

<execution_context>
@/workspaces/.claude/gsd-core/workflows/execute-plan.md
@/workspaces/.claude/gsd-core/templates/summary.md
</execution_context>

<context>
@/workspaces/CLAUDE.md
@/workspaces/.claude/skills/devtest-triage/SKILL.md
@/workspaces/.claude/skills/devtest-triage/scripts/devtest_issues.py
@/workspaces/.claude/skills/devtest-triage/scripts/eprom_ledger.py
@/workspaces/.claude/skills/devtest-rootcause/scripts/infoic_lookup.py
</context>

<facts_established_during_planning>
These were measured in the devcontainer during planning. Do not re-derive them; do check any
that a task's behaviour depends on.

- `python3` is 3.12.14. `import pytest` raises `ModuleNotFoundError`. stdlib `unittest` only.
- `/workspaces/.github/` contains `CONTRIBUTING.md` and `ISSUE_TEMPLATE` and **no `workflows/`
  directory**. Nothing in this repository runs any test automatically. Say so; do not imply a gate.
- `__pycache__/` is already git-ignored twice over — `.gitignore:6` names
  `.claude/skills/*/scripts/__pycache__/` and `.gitignore:23` names `__pycache__/`. No
  gitignore work is needed.
- `python3 -m unittest discover -s "$d" -t "$d"` collects `test_*.py` from a directory that has
  **no** `__init__.py`, provided `-t` equals `-s`. Verified on a scratch tree. With `-t` set to
  a parent, 3.12 discovery skips the non-package directories and collects nothing.
- Loading a mutated copy of a module with
  `importlib.util.spec_from_file_location` + `module_from_spec` + `exec_module` works for both
  scripts: neither has import-time side effects beyond a `_repo_root()` path computation.
- Every mutation anchor listed in the tasks below was confirmed to occur **exactly once** in its
  file with `/usr/bin/grep -cF`.
- `el.render(records, synthetic_db_path, notes)` runs with no `firestarter_app` present. The
  synthetic database shape it needs is:
  `{vendor: [{"part_number": "A, B", "pinout": "KEY", "programming": {"algorithm": int, "chip_id_check": bool, "chip_id_value": "0x1f8c", "page_size": int|None}, "electrical": {"size_bytes": int, "vcc_mv": int, "vpp_mv": int}}]}`.
  A two-vendor, three-entry database was round-tripped successfully during planning.
- `infoic_lookup.VPP_MV` and `firestarter_app/tools/build_db.py:VPP_MV` are **equal today**
  (16 entries, `{0: 12000, 16: 9000, … 240: 18000}`). The drift test is green on arrival.
- `/usr/bin/grep` must be used for any evidence grep: the `grep` on PATH is ugrep and honours
  `.gitignore`, which silently under-scans.
</facts_established_during_planning>

<tasks>

<task type="tracer" tdd="true">
  <name>Task 1: Pin the three-leg supersede rule and the untrusted-body parser, with mutation guards</name>
  <files>.claude/skills/devtest-triage/scripts/tests/_mutation.py, .claude/skills/devtest-triage/scripts/tests/test_devtest_issues.py</files>
  <behavior>
    `_mutation.py` exposes `load_mutant(module_path, old, new)`:
    - asserts `source.count(old) == 1` and raises `AssertionError` naming the anchor and the
      count when it is not 1 (this is what makes a later refactor fail loudly rather than
      quietly disarm a guard);
    - writes the patched source to a `tempfile.mkdtemp()` file and returns the executed module.

    Fixture builder in the test module: `issue(number, chip, verdict, generated, host, fw, steps)`
    returns the `{"number","title","body"}` dict shape `gh issue list --json number,title,body`
    produces, with the report embedded as a fenced ```json block carrying `schema_version`.
    Every supersede assertion goes through `di._summarize(issue(...))`, never a hand-built dict.

    Parser tests (`extract_report`, `parse_title`, `is_devtest`, `fingerprint`):
    - a body whose first fenced block is not JSON and whose second is a valid report -> the
      report is still found (the "first qualifying block wins" claim);
    - a fenced block that parses but has no `schema_version` -> `None`;
    - `is_devtest` is False when the title marker is absent, and False when the JSON report is
      absent — both markers required;
    - a title with a plain hyphen instead of an em dash still parses;
    - `fingerprint` falls back to the raw-body regex when the report dict is absent, and returns
      `"-"` when neither carries one;
    - a body of `"x" * (di.MAX_BODY + 50_000)` neither raises nor hangs.

    `version_key`:
    - `version_key("3.0.0b22") < version_key("3.0.0")` — a final release outranks its prereleases;
    - `version_key("3.0.0b22:leonardo")[:4] == (3, 0, 0, 22.0)` — the board suffix is outside the version;
    - `version_key("unknown")` is None, and `version_key("")` is None.

    `supersedes`, all nine outcomes, measured during planning and reproduced verbatim here.
    The failure under test is host `3.0.0b27`, fw `3.0.0b20:leonardo`, generated
    `2026-08-22T10:00:00Z`, failing `write` and `verify`:

    | PASS report | Expected |
    |---|---|
    | later, host `3.0.0b33`, fw `3.0.0b22:leonardo`, all OK | `(True, [])` |
    | generated earlier than the failure | False, `"not later than the failure by report timestamp"` |
    | same host and firmware as the failure | False, `"same host and firmware as the failure"` |
    | host `3.0.0b20` (older) | False, `"ran an OLDER host"` |
    | fw `3.0.0b10:leonardo` (older) | False, `"ran OLDER firmware"` |
    | `write` comes back `NA` | False, ``"step `write` is NA in the PASS, not OK"`` |
    | `write` absent from `steps[]` | False, ``"step `write` is absent in the PASS, not OK"`` |
    | `fw_board_identity` null on the PASS | True, with the note `"firmware not comparable on both sides"` |
    | `host_version` null on the PASS | False, `"host version not comparable"` |

    Assert on a substring of the returned reason, not on the whole sentence — the wording is
    prose and will be edited; the leg that blocked is the property.

    Four mutation guards. Each loads the mutant, re-runs the scenario that the intact code
    answers correctly, and asserts the mutant answers it WRONGLY:

    | Anchor (exactly once in `devtest_issues.py`) | Mutated to | Scenario that must flip |
    |---|---|---|
    | `ok["generated_full"] > fail["generated_full"]` | `… != …` | the earlier PASS now supersedes |
    | `advanced = oh > fh or (ff is not None and of is not None and of > ff)` | `advanced = True` | the same-build PASS now supersedes |
    | `if got != "OK":` | `if got not in ("OK", "NA"):` | the `write NA` PASS now supersedes |
    | `float(pre) if pre is not None else float("inf")` | `… else 0.0` | `3.0.0b22 < 3.0.0` is no longer true |

    The third is the one that matters most: it is exactly the hazard SKILL.md §3a leg 3 exists
    to prevent — closing a live `blank-check BAD` against a later `blank-check NA`.
  </behavior>
  <action>Create `.claude/skills/devtest-triage/scripts/tests/` and write `_mutation.py` and
`test_devtest_issues.py` implementing the behavior block above. Import the module under test by
inserting `os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` at `sys.path[0]` — that
resolves under both `python3 <file>` and `unittest discover -t <tests dir>`, both verified during
planning. Use `import devtest_issues as di`; call the private `_summarize` directly, which is
deliberate: it is the seam between the `gh` payload and the close decision.
Every test file ends with `if __name__ == "__main__": unittest.main()`.
No network, no `gh`, no subprocess, no writes outside `tempfile`. `_mutation.py` does not start
with `test_` so discovery will not collect it as a test module.
Do not add tests for `cmd_fold`, `cmd_show` or `gh()` — they need the network or assert on print
formatting, which is churn, not risk.</action>
  <verify>
    <automated>python3 /workspaces/.claude/skills/devtest-triage/scripts/tests/test_devtest_issues.py -v</automated>
    <automated>python3 - <<'EOF'
import re,sys
p="/workspaces/.claude/skills/devtest-triage/scripts/tests/test_devtest_issues.py"
s=open(p,encoding="utf-8").read()
for tok in ("subprocess","gh(","requests","urllib"):
    assert tok not in s, f"test module reaches outward: {tok}"
assert s.count("load_mutant(") >= 4, "fewer than four mutation guards"
print("ok")
EOF</automated>
  </verify>
  <done>`test_devtest_issues.py` runs green standalone. Its verbose output names at least nine
supersede scenarios and four mutation guards. Deleting any one of the four mutation anchors from
`devtest_issues.py` makes the suite fail with the anchor-count assertion rather than passing.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Prove the ledger round-trips, preserves Notes, and cannot drop a row silently</name>
  <files>.claude/skills/devtest-triage/scripts/tests/test_eprom_ledger.py</files>
  <behavior>
    A module-level synthetic chip database (the shape is pinned in
    `facts_established_during_planning`) written to a `tempfile.mkdtemp()` path in `setUp`. Three
    entries across two vendors, covering: a chip with aliases and `chip_id_check: True`, a chip
    with `chip_id_check: False` (renders `none`), and a `page_size: None` family (renders
    `not used`). `firestarter_app` is never read.

    - **Round trip.** `read_records(write(render(records)))` returns every authored field of
      every row — chip, host, firmware, issues, date — with no row lost and none invented.
      Include a row whose `issues` cell holds two references (`#21, #48`) and one whose firmware
      is the `not reported` sentinel, because both traverse the `|`-delimited `ROW_RE`.
    - **Idempotence.** `render(read_records(rendered), db, read_notes(rendered)) == rendered`.
    - **Notes survive.** A multi-line Notes body, including a line containing a `|` and a line
      containing `## `, comes back from `read_notes` byte-identical after a rewrite.
    - **Empty Notes.** With no Notes content the render emits `- None.` and `read_notes` on that
      output round-trips to the same render.
    - **A dropped row is loud.** A record naming a chip absent from the database is dropped from
      the render AND `WARN: not in the database, dropped:` appears on **stderr** — capture with
      `contextlib.redirect_stderr(io.StringIO())` and assert on both halves. Silent data loss is
      the failure mode this whole file exists to catch.
    - **`read_records` locates the table by its header row, not by the heading.** Rename
      `## Validated chips` to `## Chips` in the rendered text and assert the records still parse;
      then corrupt the `| Chip … Host …` header row and assert it returns `[]` rather than
      mis-parsing.
    - **`cmd_add` refusals**, driven through the real handler with an
      `argparse.Namespace(ledger=…, db=…, chip=…, host=…, firmware=…, issues=…, date=…, force=False)`:
      an unknown chip returns 1 and does not create or modify the ledger file; a chip already
      recorded returns 1 without `--force` and returns 0 with `force=True`, replacing the row
      rather than duplicating it; omitting `--firmware` records the `not reported` sentinel and
      never infers a firmware from the host version.

    Two mutation guards, same `_mutation.load_mutant` helper as Task 1 (import it; it lives in
    this same directory):

    | Anchor (exactly once in `eprom_ledger.py`) | Mutated to | Scenario that must flip |
    |---|---|---|
    | `(?P<date>\d{4}-\d{2}-\d{2})` | `(?P<date>\d{4}-\d{2}-\d{2}\d)` | the round trip now returns zero records |
    | `notes.strip("\n") if notes.strip() else "- None."` | `"- None."` | the Notes body is now lost on rewrite |

    Plus one guarded live test: if `/workspaces/VALIDATED-EPROMS.md` and the real
    `firestarter_app/firestarter/data/chip_database.json` both exist, assert `cmd_check` returns 0
    against them; otherwise `self.skipTest("firestarter_app submodule not checked out — the real
    ledger cannot be rendered")`. The skip reason must be printed, not silent.
  </behavior>
  <action>Write `test_eprom_ledger.py` implementing the behavior block above. Call
`el.cmd_add`, `el.cmd_check`, `el.render`, `el.read_records` and `el.read_notes` directly with
explicit `--ledger`/`--db` values so the module's `DEFAULT_LEDGER` and `DEFAULT_DB` constants are
never touched. Every path used for writing comes from `tempfile`; `tearDown` removes the tree with
`shutil.rmtree(..., ignore_errors=True)`. Never write to the real `VALIDATED-EPROMS.md` — the live
test reads only, through `cmd_check`, which does not write.
Do not test `family_names`. Its docstring claims adding a chip never renames an existing family,
and that claim does not obviously hold when a second family with the same protocol arrives; pinning
a behaviour whose intent is unsettled would pin a possible defect. Note the open question in the
SUMMARY instead.</action>
  <verify>
    <automated>python3 /workspaces/.claude/skills/devtest-triage/scripts/tests/test_eprom_ledger.py -v</automated>
    <automated>python3 - <<'EOF'
import hashlib,subprocess
p="/workspaces/VALIDATED-EPROMS.md"
before=hashlib.sha256(open(p,"rb").read()).hexdigest()
r=subprocess.run(["python3","/workspaces/.claude/skills/devtest-triage/scripts/tests/test_eprom_ledger.py"],
                 capture_output=True,text=True)
after=hashlib.sha256(open(p,"rb").read()).hexdigest()
assert r.returncode==0, r.stderr[-2000:]
assert before==after, "the suite mutated the real ledger"
print("ok — ledger untouched")
EOF</automated>
  </verify>
  <done>`test_eprom_ledger.py` runs green standalone, the real `VALIDATED-EPROMS.md` is
byte-identical before and after the run, and both mutation guards report their mutant returning the
wrong answer. With `firestarter_app` absent the live-ledger test reports `skipped` with its stated
reason and the rest of the file still passes.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: Detect infoic_lookup table drift, then publish the one command in both SKILL.md files</name>
  <files>.claude/skills/devtest-rootcause/scripts/tests/test_infoic_lookup.py, .claude/skills/devtest-rootcause/SKILL.md, .claude/skills/devtest-triage/SKILL.md</files>
  <behavior>
    `test_infoic_lookup.py`:
    - **Drift.** Extract `VPP_MV` from `firestarter_app/tools/build_db.py` with `ast.parse` +
      `ast.literal_eval` over the module-level `Assign` node — never `import build_db`, which
      would defeat the skill's stdlib-only, submodule-optional property. Assert it equals
      `infoic_lookup.VPP_MV`. When `build_db.py` is absent, `self.skipTest("firestarter_app
      submodule not checked out — cannot compare against the generator's VPP_MV")`. This is the
      drift the skill's own documentation says nothing detects for you; measured equal today, so
      it arrives green.
    - **Negative control for the drift comparison.** The comparison is expressed as a helper
      `table_drift(a, b) -> list[str]`; assert it is empty for the two live tables and non-empty,
      naming the key, for a copy of `infoic_lookup.VPP_MV` with one value perturbed. This is the
      RED demonstration for a test that would otherwise be unfalsifiable when the submodule is
      absent — it fails on a broken input even in a bare clone.
    - **`format_vpp`.** `12000 -> "12V"`, and an unknown index (`VPP_MV.get(0x99)` is `None`)
      renders without raising. Read the real rendering off the function; do not invent a format.
    - Assert `VPP_MV` is keyed on the masked index (every key `& 0x0F == 0`, i.e. `voltages & 0xF0`
      values only), which is the decode invariant the SKILL.md troubleshooting table names.

    SKILL.md edits, one block in each file, placed in the existing command block near the top
    (`devtest-triage` §"Self-contained" block; `devtest-rootcause` the equivalent block):

    ```bash
    # Tests for this skill's scripts. stdlib unittest, no pytest, no network, no submodule.
    for d in $ROOT/.claude/skills/*/scripts/tests; do
      python3 -m unittest discover -s "$d" -t "$d" || break
    done
    ```

    followed by one prose line, present in both files, stating plainly: **nothing runs these
    automatically — this repository has no CI workflow; run them by hand after editing a script.**
    Do not write "CI", "gate", or "enforced" about them anywhere.
  </behavior>
  <action>Create `.claude/skills/devtest-rootcause/scripts/tests/` and write
`test_infoic_lookup.py` per the behavior block, importing `infoic_lookup` via the same
`sys.path` insertion pattern as Task 1. This skill gets no `_mutation.py`: importing Task 1's copy
across skills would break the self-containment both SKILL.md files advertise, and the negative
control above covers the falsifiability requirement without one. Locate `build_db.py` from the
test file's own path (four `os.pardir` hops to the checkout root, then
`firestarter_app/tools/build_db.py`), never from the current working directory.
Then edit both SKILL.md files. Keep every existing code fence byte-identical apart from the block
you add — the `.planning/` tree carries `file:LINE` citations into both files, so after the edit run
the citation check in `<verify>` and repair any citation the insertion displaced.</action>
  <verify>
    <automated>python3 /workspaces/.claude/skills/devtest-rootcause/scripts/tests/test_infoic_lookup.py -v</automated>
    <automated>for d in /workspaces/.claude/skills/*/scripts/tests; do python3 -m unittest discover -s "$d" -t "$d" || exit 1; done</automated>
    <automated>python3 - <<'EOF'
import subprocess
hits=[]
for f in ("/workspaces/.claude/skills/devtest-triage/SKILL.md",
          "/workspaces/.claude/skills/devtest-rootcause/SKILL.md"):
    s=open(f,encoding="utf-8").read()
    assert "unittest discover" in s, f"{f}: the test command is not published"
    assert "no CI" in s or "nothing runs" in s or "not run automatically" in s, \
        f"{f}: does not say the tests are unenforced"
    for bad in ("CI gate","enforced by CI","the CI runs"):
        assert bad not in s, f"{f}: overclaims automation with {bad!r}"
print("ok")
EOF</automated>
    <automated>cd /workspaces && /usr/bin/grep -rn "skills/devtest-\(triage\|rootcause\)/SKILL.md:[0-9]" .planning/ --include=*.md | head -40</automated>
  </verify>
  <done>Both test suites run green from the single discovery loop, which exits 0. Both SKILL.md
files publish that one command and state that nothing runs it automatically. Every `.planning/`
`file:LINE` citation into either SKILL.md still names the content it named before the edit.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| GitHub issue body -> `devtest_issues.py` | Community-authored, untrusted text crosses into a parser whose verdict can close a stranger's issue |
| `supersedes()` -> `gh issue close` | A pure function's return value authorises an irreversible outward action |
| `eprom_ledger.render()` -> tracked `VALIDATED-EPROMS.md` | A regex decides which validated-chip rows survive a rewrite |
| test process -> working tree | Tests execute code that writes files; a stray default path writes the real ledger |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-ess-01 | Tampering | `supersedes()` leg 3 | high | mitigate | Task 1 pins `NA` and absent-step as non-superseding and guards the `if got != "OK":` branch with a mutant; a regression that closes a live defect behind a green title now fails the suite |
| T-ess-02 | Denial of Service | `extract_report()` on a hostile body | medium | mitigate | Task 1 asserts an over-`MAX_BODY` body neither raises nor hangs, and that a non-JSON fence does not abort the scan |
| T-ess-03 | Tampering | `ROW_RE` / `render()` | high | mitigate | Task 2 proves the round trip and guards the date group with a mutant; a dropped row is asserted to reach stderr |
| T-ess-04 | Tampering | test process writing `VALIDATED-EPROMS.md` | medium | mitigate | Task 2 passes explicit temp `--ledger`/`--db` everywhere and its second verify leg hashes the real ledger before and after the run |
| T-ess-05 | Information Disclosure | test suite reaching the network | low | mitigate | Task 1 verify greps the module for `subprocess`/`gh(`/`urllib`; no test invokes `gh` |
| T-ess-06 | Spoofing | `infoic_lookup.VPP_MV` drift | medium | mitigate | Task 3 compares against the generator's table via `ast.literal_eval`, so a silently drifted VPP index stops misreading as a chip defect |
| T-ess-07 | Tampering | new dependency installs | low | accept | No package manager runs. stdlib only, by hard constraint; the package-legitimacy gate has nothing to audit |
</threat_model>

<verification>
One command runs everything:

```bash
for d in /workspaces/.claude/skills/*/scripts/tests; do
  python3 -m unittest discover -s "$d" -t "$d" || exit 1
done
```

Do not pipe that loop into `tail` or `head` — a pipe masks the exit code and the run reads green
when it failed. Measured during planning.

Falsifiability audit, to be recorded in the SUMMARY. For every test in the suite, name how it was
observed RED:

| Kind | RED evidence |
|---|---|
| The seven mutation-guarded properties | Permanent and executable — the guard loads a broken module on every run and asserts the wrong answer |
| The drift comparison | Permanent — `table_drift` is asserted non-empty against a perturbed copy |
| Everything else (parser cases, `cmd_add` refusals, Notes preservation, stderr warning) | Observed once, by hand, against a deliberately broken input; paste the observed failure line into the SUMMARY |

A test whose RED evidence cannot be produced does not ship. Delete it rather than carry it.
</verification>

<success_criteria>
- `for d in /workspaces/.claude/skills/*/scripts/tests; do python3 -m unittest discover -s "$d" -t "$d" || exit 1; done` exits 0.
- The run reports at least nine `supersedes` scenarios, seven mutation guards and the drift comparison.
- `python3 -c "import pytest"` is still not needed by anything in the suite.
- `git status --porcelain VALIDATED-EPROMS.md firestarter_app firestarter_fw` is empty after a full run.
- Both SKILL.md files carry the one command and the no-automation statement.
- The SUMMARY records the RED evidence for every test and the `family_names` open question.
</success_criteria>

<output>
Create `.planning/quick/260916-ess-add-test-coverage-for-the-devtest-skill-/260916-ess-SUMMARY.md` when done.
</output>
