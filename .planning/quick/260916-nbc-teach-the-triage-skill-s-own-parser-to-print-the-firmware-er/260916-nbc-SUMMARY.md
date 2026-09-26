---
phase: quick-260916-nbc
plan: 01
subsystem: testing
tags: [unittest, stdlib, ast, devtest-triage, firmware-messages]

requires:
  - phase: quick-260916-ess
    provides: "The `_mutation.py` / test-discovery conventions this plan's tests build on"
provides:
  - "`scripts/firmware_messages.py`: an owned, stdlib-only copy of the app's `CATALOG` id->name table, plus `resolve_error(code, reported_name=None)` implementing the full DD-3 render contract"
  - "`devtest_issues.py show`'s step table gains an `error` column between `verdict` and `reason`, resolving each step's `error_code`/`error_name` through `firmware_messages.resolve_error`"
  - "`fixtures/dev-test-error-codes-populated.md`: a hand-authored fixture carrying real codes (write 183, verify 175, blank-check 185) with no `error_name`, matching the shape of the ten open dev-test issues"
  - "`CatalogDriftTest`: ast-based drift detector between the owned table and the app's real `CATALOG`, with a negative control and a reachability test for its skip branch"
  - "`SelfContainmentTest`: ast-based runtime-coupling guard over both scripts (forbidden import roots, dynamic imports, subprocess argv0), with a negative control proving the scanner is not vacuous"
  - "SKILL.md section 2 sample output regenerated from real command runs; two new Troubleshooting rows for `unknown` and `?`"
affects: [devtest-triage]

actuals:
  tokens: 9465
  tasks: 3
  commits: 3
  plan_head_before: 5fbbe9a53539ff4b2979e756531946627c206804

tech-stack:
  added: []
  patterns:
    - "Owned-table-plus-ast-drift-test pattern (established in devtest-rootcause's infoic_lookup.py / test_infoic_lookup.py) reused for a second table: transcribe by hand, verify by ast.parse, never import the source of truth"
    - "cmd_show pinned end-to-end via a real argparse.Namespace + contextlib.redirect_stdout + tempfile body file, never a hand-built output string"

key-files:
  created:
    - .claude/skills/devtest-triage/scripts/firmware_messages.py
    - .claude/skills/devtest-triage/scripts/tests/test_firmware_messages.py
    - .claude/skills/devtest-triage/fixtures/dev-test-error-codes-populated.md
  modified:
    - .claude/skills/devtest-triage/scripts/devtest_issues.py
    - .claude/skills/devtest-triage/scripts/tests/test_devtest_issues.py
    - .claude/skills/devtest-triage/SKILL.md

key-decisions:
  - "Followed DD-1 exactly: MESSAGE_NAMES mirrors CATALOG only (79 entries), DEBUG_CATALOG excluded. Verified live against the checked-out firestarter_app: the nine colliding ids (0x00-0x05, 0x10, 0x20, 0x30) really do differ between the two tables in this tree, confirming the exclusion is load-bearing and not theoretical."
  - "resolve_error is pure and total per DD-3 -- implemented exactly the seven-row contract table, confirmed with one test per row plus adversarial cases (bool True, negative, over-255, a 10**40 bignum, newline/backtick/shell-metacharacter reported names)."
  - "Drift and self-containment tests followed the devtest-rootcause test_infoic_lookup.py template named in the plan: ast.parse over source text, never import, skip-with-reason only when the submodule is absent, and a negative control for every comparator so the RED path is provably reachable rather than assumed."
  - "No changes were needed to firmware_messages.py during Task 2 -- the resolver written in Task 1 already satisfied every DD-3 test written against it on the first run (62/62 passed immediately). Task 2's TDD framing therefore served as a pinning/regression suite rather than surfacing an implementation gap."

requirements-completed: [260916-nbc]

coverage:
  - id: D1
    description: "show prints an error column for every step row, carrying error_code verbatim plus the resolved MSG_* name"
    requirement: "260916-nbc"
    verification:
      - kind: unit
        ref: "test_devtest_issues.py#TestErrorColumnRendering.test_populated_codes_render_all_three_resolved_names"
        status: pass
      - kind: unit
        ref: "test_firmware_messages.py#TestResolveErrorKnownAndUnknown.test_known_code_resolves_table_name"
        status: pass
    human_judgment: false
  - id: D2
    description: "null/absent error_code renders '-'; unknown code renders 'NNN unknown'; untrusted code renders '?' without echoing the value; reported error_name is shown, with a table disagreement rendered as both"
    requirement: "260916-nbc"
    verification:
      - kind: unit
        ref: "test_firmware_messages.py#TestResolveErrorRejectsUntrustedCode (5 tests)"
        status: pass
      - kind: unit
        ref: "test_firmware_messages.py#TestResolveErrorWithReportedName (3 tests)"
        status: pass
      - kind: unit
        ref: "test_firmware_messages.py#TestResolveErrorRejectsHostileReportedName (7 tests)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Neither firmware_messages.py nor devtest_issues.py acquires a runtime dependency on firestarter_app (no forbidden import root, no dynamic import, every subprocess argv literal and gh-headed)"
    requirement: "260916-nbc"
    verification:
      - kind: unit
        ref: "test_firmware_messages.py#SelfContainmentTest.test_no_runtime_coupling_to_firestarter_app"
        status: pass
      - kind: unit
        ref: "test_firmware_messages.py#SelfContainmentTest.test_import_scanner_detects_a_planted_import"
        status: pass
    human_judgment: false
  - id: D4
    description: "The owned table is proven to drift-detect against the app's real CATALOG when checked out, and to skip (never fail) when it is absent"
    requirement: "260916-nbc"
    verification:
      - kind: unit
        ref: "test_firmware_messages.py#CatalogDriftTest.test_catalog_matches_the_app (ran, not skipped, in this environment)"
        status: pass
      - kind: unit
        ref: "test_firmware_messages.py#CatalogDriftTest.test_table_drift_negative_control"
        status: pass
      - kind: unit
        ref: "test_firmware_messages.py#CatalogDriftTest.test_find_messages_reachable_on_a_nonexistent_root"
        status: pass
    human_judgment: false
  - id: D5
    description: "SKILL.md's two section-2 sample blocks are byte-identical to the real output of the commands printed above them"
    verification: []
    human_judgment: true
    rationale: "Doc-content match against live command output has no automated gate in this plan by design (DD's own human-check note) -- confirmed by a byte-for-byte comparison script during execution (see below), which is the closest to automated proof available, but the plan itself designates this a human read."

duration: ~50min
completed: 2026-09-16
status: complete
---

# Quick Task 260916-nbc: Firmware Error Codes in devtest show Summary

**`devtest_issues.py show` now prints each failing step's firmware error code next to the
symbolic `MSG_*` name it resolves from its own owned copy of the app's message catalog — no
`firestarter_app` import required, and a drift test that fails the day the two tables disagree.**

## Performance

- **Duration:** ~50 min
- **Tasks:** 3
- **Files created:** 3 (`firmware_messages.py`, `test_firmware_messages.py`, one new fixture)
- **Files modified:** 3 (`devtest_issues.py`, `test_devtest_issues.py`, `SKILL.md`)

## Accomplishments

- `firmware_messages.py` owns a stdlib-only, 79-entry transcription of `CATALOG` from
  `firestarter_app/firestarter/messages.py`, deliberately excluding the separate,
  colliding `DEBUG_CATALOG` id space (DD-1) — verified live against the checked-out app that the
  nine colliding ids genuinely differ between the two tables.
- `resolve_error(code, reported_name=None)` implements the full 7-row DD-3 contract: `-` for
  absent, `?` for anything not a plain non-bool int in `0..255` (bignums, strings, `True`,
  negatives, out-of-range all rejected and never echoed), the table's name when there is one,
  `unknown` when there isn't, and either agreement or a `NNN REPORTED (table: RESOLVED)`
  disagreement notice when a report supplies its own `error_name`. A reported name must match
  `^[A-Za-z0-9_]{1,40}$` or it is discarded silently — proven against a newline, a backtick, a
  shell metacharacter, an empty string, a 41-char string, and a non-`str` value.
- `cmd_show`'s step table gained an `error` column (28 chars wide, between `verdict` and
  `reason`, per DD-4) built from the same width spec as its header so the two can never drift
  apart.
- New fixture `dev-test-error-codes-populated.md`: hand-authored, header-disclosed as synthetic,
  modelling the shape of the ten currently-open `dev test` issues (real codes, no
  `error_name`). The two pre-existing frozen fixtures were never touched — confirmed via
  `git diff --quiet HEAD` at the end of every task.
- `CatalogDriftTest` (ast-parses `messages.py`'s `CATALOG` `AnnAssign`, never imports it) ran
  for real in this environment (the submodule is checked out) and found zero drift, plus a
  negative control proving the comparator is not vacuous and a reachability test for the
  skip-with-reason branch.
- `SelfContainmentTest` proves neither script has a runtime dependency on `firestarter_app`:
  forbidden import roots, dynamic imports (`__import__`/`import_module`), and every
  `subprocess.*` call's argv0 are all checked via `ast`, never a text-substring match (which
  would be unsatisfiable given the four legitimate, correct occurrences of the string
  `firestarter_app` already in `devtest_issues.py`). A negative control plants three forbidden
  import shapes into a temp module and confirms the scanner flags every one.
- The full skill suite grew from the measured 39-test baseline to 68 tests, `OK` on its own
  exit status (not laundered through a grep).
- SKILL.md's two section-2 sample blocks were regenerated by actually running the
  `--body-file` commands they publish and pasting the real stdout; a post-hoc byte-for-byte
  comparison script confirmed both blocks match verbatim.

## Task Commits

1. **Task 1: End-to-end — a known code renders as name in `show`, one path only** -
   `4d02e129` (feat)
2. **Task 2: Pin the null, unknown, hostile and reported-name edges** - `de8459a1` (test)
3. **Task 3: Drift check against the app catalog, self-containment guard, and SKILL.md sync** -
   `81080882` (test)

## Files Created/Modified

- `.claude/skills/devtest-triage/scripts/firmware_messages.py` - owned `MESSAGE_NAMES` table +
  `resolve_error()`
- `.claude/skills/devtest-triage/scripts/devtest_issues.py` - `import firmware_messages`, new
  `error` column in `cmd_show`'s step loop and header
- `.claude/skills/devtest-triage/fixtures/dev-test-error-codes-populated.md` - new hand-authored
  fixture, real codes, no `error_name`
- `.claude/skills/devtest-triage/scripts/tests/test_firmware_messages.py` - 29 tests: resolver
  contract, `CatalogDriftTest`, `SelfContainmentTest`
- `.claude/skills/devtest-triage/scripts/tests/test_devtest_issues.py` - extended `issue()`
  helper with optional per-step `error_code`/`error_name`; 4 new rendered-row tests
- `.claude/skills/devtest-triage/SKILL.md` - regenerated section-2 sample output, added the
  populated-codes example, sentinel prose, two Troubleshooting rows, and an updated
  Self-contained paragraph

## Verification Evidence

Baseline measured before this plan: `Ran 39 tests` / `OK`.

Final full suite:

```
$ python3 -m unittest discover -s .claude/skills/devtest-triage/scripts/tests -t .claude/skills/devtest-triage/scripts/tests
...
Ran 68 tests in 0.188s

OK
```

(The interleaved `ERROR: ...` lines during the run are expected stderr from two pre-existing,
unrelated `eprom_ledger.py` tests exercising its refusal paths — not failures; the suite's own
exit status and the printed `OK` are what was asserted, per DD-8's warning against string
matching a `Ran N tests` line as proof.)

Named-class invocations, proving neither suite is an unreachable stub:

```
$ python3 -m unittest -v test_firmware_messages.SelfContainmentTest
...OK (2 tests)
$ python3 -m unittest -v test_firmware_messages.CatalogDriftTest
...OK (4 tests) -- test_catalog_matches_the_app printed "ok", not "skipped": the drift
comparison genuinely ran in this environment.
```

Frozen fixtures confirmed untouched after every task:

```
$ git diff --quiet HEAD -- .claude/skills/devtest-triage/fixtures/dev-test-at28c256-null-identity.md \
    .claude/skills/devtest-triage/fixtures/dev-test-at28c256-populated-identity.md
$ echo $?
0
```

Every verify leg in the plan was run as a single command (or `&&`-chained single-purpose
commands) per DD-8, using `/usr/bin/grep` and `-qFe`/`wc -l`/`git diff --quiet` forms rather
than the traps the plan called out (`grep -c` on zero, `grep -v '^\+\+\+'`, OR-`grep`, `;`
chains, `git diff --stat`). All exited 0.

## Decisions Made

See `key-decisions` in frontmatter. No decisions required departing from the plan's DD-1
through DD-8 — all were followed as specified, having been settled against the real files
during planning.

## Deviations from Plan

None — plan executed exactly as written. Task 2's TDD framing (write tests, watch them fail,
then close gaps) did not surface any gap: Task 1's `resolve_error` implementation already
satisfied all 20 resolver-contract tests and the 4 rendered-row tests on first run. This is
recorded as a decision above rather than a deviation, since no code outside the plan's
described scope was touched.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `show` now surfaces the firmware error code and its resolved name for every one of the ten
  currently-open `dev test` issues, none of which carry `error_name` — triage no longer needs
  to hand-parse the JSON block to learn what a failing step's code means.
- `CatalogDriftTest` and `SelfContainmentTest` are load-bearing regression nets: any future edit
  that reassigns a `CATALOG` id, or that accidentally introduces an import of
  `firestarter_app`/`firestarter`/`messages`, a dynamic import, or a non-`gh` subprocess call in
  either `firmware_messages.py` or `devtest_issues.py`, will fail the suite.
- No blockers. Sibling item 260916-nb9 (already landed in `firestarter_app`, adding
  `error_name` + schema 2.1) is fully compatible with this plan's parser without any further
  change — `resolve_error`'s `reported_name` parameter was designed for exactly that shape.

## Self-Check: PASSED

All 3 created files exist on disk (`firmware_messages.py`, `test_firmware_messages.py`,
`dev-test-error-codes-populated.md`); all 3 task commit hashes (`4d02e129`, `de8459a1`,
`81080882`) are present in `git log --oneline --all`.

---
*Phase: quick-260916-nbc*
*Completed: 2026-09-16*
