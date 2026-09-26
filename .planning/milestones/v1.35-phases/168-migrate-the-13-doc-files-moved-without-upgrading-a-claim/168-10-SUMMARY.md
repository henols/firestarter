---
phase: 168-migrate-the-13-doc-files-moved-without-upgrading-a-claim
plan: 10
subsystem: testing
tags: [dispatch-mirror, wiki, standalone-checker, stdlib, fail-closed]

requires:
  - phase: 168-04
    provides: "the two parsing regexes (_BUCKET_ROW_RE, _FAMILY_ROW_RE) and the DOC_FILE_TO_FUNC handler map preserved verbatim from the deleted tests/test_dispatch_mirror.py"
  - phase: 168-05
    provides: "the migrated Programming-Protocols.md page carrying the firestarter-claims-begin/-end sentinels around a byte-faithful copy of the old §0 table"
  - phase: 168-02
    provides: "wiki.py's 0/1/2 exit-code contract and selftest.sh's control-then-mutate/record/print_evidence_table driver shape, copied for this checker"

provides:
  - "tools/wiki/dispatch_mirror.py -- stdlib-only three-way dispatch-mirror checker reading the doc leg from the published wiki page's claims region, the tool leg from a path-injected import of firestarter_app/tools/check_dispatch, and the firmware leg from firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp"
  - "a non-vacuity floor (MIN_BUCKET_ROWS=6, half the current 12-row production table) that returns exit 2 -- never 0 -- when the claims region is absent or parses to a near-empty table, distinguishing a reformat from a real dispatch drift"
  - "a completeness check (every protocol in the tool's KNOWN_PROTOCOLS must have a bucket row) that catches a single deleted doc row as an attributable exit-1 naming the exact protocol, without tripping the non-vacuity floor"
  - "tools/wiki/selftest.sh's new case_dispatch_mirror_planted_drift_exit_1 (green control, planted missing-row exit-1, planted comment-only-firmware-entry exit-0) -- driver now reports 9 cases"
  - "evidence/dispatch-mirror-planted-RED.txt -- the captured missing-row run's exit status and stderr"
affects: ["168-11 (HONEST-01 lands its own selftest case into the same CASES array and driver count)", "168-12 (HONEST-02 lands a third checker + selftest case; final expected count is 11 per the phase's artifact list)", "168-13 (wiki-check.yml wires dispatch_mirror.py in as one of the three scheduled checker steps)"]

tech-stack:
  added: []
  patterns:
    - "path-injected first-party import (sys.path.insert(0, app_dir) then importlib.import_module) to reuse a sub-repo's dispatch() and KNOWN_PROTOCOLS rather than reimplementing them, mirroring the deleted app-side module's own `from tools import check_dispatch`"
    - "reverse completeness check (iterate the tool's own known-protocol set, not just what the doc happened to parse) catches an entry silently dropped from the doc without needing the non-vacuity floor to do that job"

key-files:
  created:
    - tools/wiki/dispatch_mirror.py
    - .planning/phases/168-migrate-the-13-doc-files-moved-without-upgrading-a-claim/evidence/dispatch-mirror-planted-RED.txt
  modified:
    - tools/wiki/selftest.sh

key-decisions:
  - "MIN_BUCKET_ROWS is set to 6 (half the current production table), not the literal 12 the plan's prose repeatedly names. A literal-12 floor would make the plan's own acceptance criterion -- deleting one row from the real 12-row page must exit 1, not 2 -- structurally unreachable: 12 minus 1 is 11, which is 'fewer than 12' by definition, so any single real deletion would trip the vacuity guard before Leg 1 ever ran. Halving the floor lets a single-row loss reach the named, attributable exit-1 check while a genuine reformat (which breaks the regex wholesale, measured at 0 rows in this plan's own verification) still trips exit 2. 'Twelve' in the plan's prose is preserved as the documented origin of the number, not as the literal constant."
  - "The doc-vs-tool leg does a REVERSE completeness check (every protocol in the tool's KNOWN_PROTOCOLS must have a doc bucket row) in addition to the forward per-row correctness check the deleted module carried. The deleted module only ever iterated doc_table.items() -- a row silently missing from the doc would have produced zero failures under that design, not an exit-1. The reverse check is what makes 'one bucket row deleted' attributable at all, and is why check_dispatch.KNOWN_PROTOCOLS is imported alongside dispatch() and _ALGO_MEM_TYPE."
  - "The selftest fixture reuses the checker's own hardcoded DOC_FILE_TO_FUNC file names (eprom.cpp, sram.cpp, not_implemented.cpp) rather than inventing new ones, distributing 13 bucket rows across those 3 families (5+5+3) -- comfortably above the 6-row floor so a single planted deletion (13->12) still clears it. This is why the fixture is 'three families', not literally three or four individual protocol rows as an earlier draft reading of the plan's prose might suggest."
  - "requirements-completed left empty. MIGRATE-03 and MIGRATE-04 are declared in this plan's frontmatter but plans 168-11/168-12/168-13 still own the HONEST-02 standing gate, the CI-floor verification and the final wiki-check.yml wiring -- per project precedent (168-04-SUMMARY), a multi-plan requirement is not marked complete by an intermediate plan."

requirements-completed: []

coverage:
  - id: D1
    description: "tools/wiki/dispatch_mirror.py exists as a stdlib-only, zero-comment checker with the 0/1/2 exit contract, verified against the live wiki clone plus real firestarter_app/firestarter checkouts (exit 0, 12 protocols compared)"
    requirement: "MIGRATE-03"
    verification:
      - kind: other
        ref: "python3 tools/wiki/dispatch_mirror.py --wiki-dir <live wiki clone> --app-dir firestarter_app --fw-dir firestarter -> 'OK: 12 protocols compared across wiki, host tool and firmware.', exit 0"
        status: pass
      - kind: other
        ref: "grep -cE '^(import|from) ' tools/wiki/dispatch_mirror.py -> 6, all stdlib (argparse, importlib, re, sys, pathlib); no pyproject.toml/pytest.ini/tests/ created anywhere in the meta repo"
        status: pass
    human_judgment: false
  - id: D2
    description: "A missing --wiki-dir, a page with its claims sentinels removed, and a drastically reflowed table (measured: parses to 0 rows) all exit 2, each naming which of the three it was"
    requirement: "MIGRATE-04"
    verification:
      - kind: other
        ref: "manual runs against /nonexistent, a sentinel-stripped copy, and a column-reflowed copy of the live wiki clone: 'ERROR: --wiki-dir not found', 'ERROR: claims region (...) not found', 'ERROR: claims region parsed to 0 bucket row(s)' -- all exit 2"
        status: pass
    human_judgment: false
  - id: D3
    description: "A single bucket row deleted from the live wiki clone's claims region exits 1 (not 2) and names the missing protocol"
    requirement: "MIGRATE-04"
    verification:
      - kind: other
        ref: "sed-deleted the 0x08 row from a copy of the live wiki clone; dispatch_mirror.py -> 'ERROR: 0x08 is dispatched by the host tool but has no bucket row in the claims region', exit 1"
        status: pass
    human_judgment: false
  - id: D4
    description: "bash tools/wiki/selftest.sh exits 0 with the new case_dispatch_mirror_planted_drift_exit_1 registered; the driver reports 9 cases; the missing-row sub-case's log is captured to evidence/dispatch-mirror-planted-RED.txt; the comment-only sub-case proves the compared-protocol count is unchanged"
    requirement: "MIGRATE-04"
    verification:
      - kind: automated
        command: "bash tools/wiki/selftest.sh"
        result: "OK: selftest complete (9 cases); all 10 evidence-table rows PASS, including dispatch_mirror_planted_drift_exit_1 (exit 1, names 0xA5) and dispatch_mirror_planted_drift_exit_1_comment_only (exit 0, count unchanged at 13)"
        status: pass
    human_judgment: false
  - id: D5
    description: "All 4 legs the deleted tests/test_dispatch_mirror.py originally exercised are functionally reproduced by the rebuilt checker: doc-vs-tool per-row mismatch, firmware-does-not-enumerate-a-protocol, a planted missing entry detected, and a planted comment-only entry NOT detected (the deliberate fail-open finding)"
    verification:
      - kind: other
        ref: "manual fixture runs: KNOWN_PROTOCOLS/dispatch() mismatch on the eprom family -> 5 named ERROR lines, exit 1; firmware stub with 0xA5 lines removed -> 'firmware dispatch test does not enumerate protocol(s): 0xA5', exit 1; selftest's two sub-cases cover the remaining two legs"
        status: pass
    human_judgment: false

duration: ~50min
completed: 2026-08-31
status: complete
---

# Phase 168 Plan 10: Rebuild the Dispatch-Mirror Gate in the Meta Repo Summary

**Rebuilt the three-way protocol dispatch-mirror invariant (deleted from `firestarter_app` in plan 168-04) as `tools/wiki/dispatch_mirror.py`, a standalone stdlib-only checker that reads its canonical leg from the published wiki page's `firestarter-claims` sentinel region instead of a frozen git blob, fails closed (exit 2, never 0) when that region is missing or the table has been drastically reformatted, and pairs a captured exit-1 red (a planted missing bucket row) with a captured fail-open finding (a commented-out firmware entry is not counted as real) via a new `selftest.sh` case.**

## Performance

- **Duration:** ~50 min
- **Completed:** 2026-08-31
- **Tasks:** 2 completed (both `type="auto"`)
- **Files modified:** 3 (1 new checker, 1 selftest addition, 1 new evidence file)

## Accomplishments

- Wrote `tools/wiki/dispatch_mirror.py`: a single stdlib-only script matching `wiki.py`'s shape (module constants for every path/name/regex, a `check_dispatch_mirror()` function returning `list[str]` failures, `main()` doing precondition validation before dispatch and returning 2/1/0). Copied the exit-code contract verbatim into the module docstring. Reused the exact `_BUCKET_ROW_RE`, `_FAMILY_ROW_RE` and `DOC_FILE_TO_FUNC` recorded in plan 168-04's summary rather than re-deriving them, since 168-05 migrated `PROTOCOLS.md` §0 byte-for-byte.
- Verified against the **live** `firestarter_prom.wiki.git` clone (`master@9d7e9bc`) plus real `firestarter_app` and `firestarter` checkouts: `OK: 12 protocols compared across wiki, host tool and firmware.`, exit 0.
- Proved the fail-closed floor against real mutations of the live wiki clone: a missing `--wiki-dir` exits 2; a copy with the claim sentinels stripped exits 2 naming the missing region; a copy with the bucket table's leading `| 0xNN |` columns rewritten (simulating a genuine column reflow) parses to 0 rows and exits 2, naming the count.
- Proved the single-row-deletion path is attributable, not swallowed by the vacuity floor: deleting the real `0x08` row from a copy of the live page exits 1, naming `0x08` by hex value — via a **reverse completeness check** against the imported `check_dispatch.KNOWN_PROTOCOLS`, which the deleted app-side module never had (it only ever iterated whatever the doc happened to still contain).
- Added `case_dispatch_mirror_planted_drift_exit_1` to `selftest.sh`, structured element-for-element like `case_orphan_exit_1`: a green control against a small 3-family, 13-bucket-row fixture (reusing the checker's own real handler-file names — `eprom.cpp`, `sram.cpp`, `not_implemented.cpp` — rather than inventing new ones), a planted missing-row mutation asserting exit 1 naming the deleted protocol, and a planted comment-only-firmware-entry mutation asserting exit 0 with the compared-protocol count unchanged (proving a commented-out mention is not counted as a dispatch entry — the original module's SWEEP-07 fail-open finding, now reproduced against the relocated checker).
- Captured the missing-row mutation's full log and exit status to `evidence/dispatch-mirror-planted-RED.txt`.
- Manually reproduced the two remaining original legs (doc-vs-tool per-row mismatch; firmware-does-not-enumerate-a-protocol) against ad hoc fixture mutations to confirm all 4 of the deleted module's original legs are functionally present in the rebuilt checker (see Decisions Made and coverage D5) — only 2 of the 4 are codified into `selftest.sh` by this plan; the other 2 were verified but not added as permanent selftest cases, since the plan's Task 2 scope named only the missing-row and comment-only mutations.

## Task Commits

1. **Task 1: Write the checker with the 0/1/2 contract and a fail-closed region gate** - `356f09e0` (feat)
2. **Task 2: Add the selftest case with a green control and two planted mutations** - `f956c934` (test)

## Files Created/Modified

- `tools/wiki/dispatch_mirror.py` - new; the relocated three-way dispatch-mirror checker
- `tools/wiki/selftest.sh` - added `DISPATCH_MIRROR_PY` constant, `new_dispatch_mirror_fixture()` helper, `case_dispatch_mirror_planted_drift_exit_1()`, registered in `CASES=`
- `.planning/phases/168-migrate-the-13-doc-files-moved-without-upgrading-a-claim/evidence/dispatch-mirror-planted-RED.txt` - new; the captured planted-missing-row run

## Decisions Made

- **`MIN_BUCKET_ROWS = 6`, not a literal 12.** See key-decisions above for the full reasoning: a literal-12 floor is incompatible with the plan's own acceptance criterion that a single deleted row from the real 12-row page must exit 1, not 2. Halving it preserves the floor's purpose (catch a wholesale reformat, measured at 0 rows) while leaving room for Leg 1's reverse-completeness check to do its job on a single missing row.
- **Added a reverse completeness check** (iterate the tool's `KNOWN_PROTOCOLS`, not just the doc's parsed rows) that the deleted app-side module never had. Without it, a doc row disappearing entirely would produce zero failures under the original per-row-iteration design.
- **Selftest fixture reuses the real handler-file names** (`eprom.cpp`, `sram.cpp`, `not_implemented.cpp`) from the checker's own hardcoded `DOC_FILE_TO_FUNC`, distributed across 13 bucket rows (5+5+3) rather than a literal 3-4 rows, so the fixture clears the non-vacuity floor both before and after a single planted deletion.
- **Left `requirements-completed` empty** for both `MIGRATE-03` and `MIGRATE-04`, consistent with 168-04's precedent — plans 168-11 through 168-13 still own HONEST-02's standing gate, the CI-floor verification run, and the final `wiki-check.yml` wiring that these requirements' full text describes.

## Deviations from Plan

### Auto-fixed Issues

None — no bugs, missing functionality, or blocking issues were found requiring Rule 1/2/3 fixes.

### Interpretive decisions (not deviations from stated behavior, but resolving contradictions in the plan's prose)

**1. [Gray-area decision] The plan's literal "12" and its own "exit 1 not 2 on one deleted row" criterion are mutually exclusive; resolved by using a lower floor (6) and adding a reverse-completeness check.**
- **Found during:** Task 1 design, before writing any code
- **Issue:** The plan states the non-vacuity floor as "fewer than 12 bucket rows" in prose, but Task 1's own acceptance criteria require that deleting exactly one row from the real (12-row) production table exits 1, not 2. Twelve minus one is eleven, which is unconditionally "fewer than twelve" — so a literal floor of 12 makes that acceptance criterion unreachable by construction, for any possible checker design.
- **Resolution:** Set `MIN_BUCKET_ROWS = 6` (half of 12) as the floor, and added a reverse completeness check against the tool's own `KNOWN_PROTOCOLS` set so a single missing row is caught by Leg 1 (named, exit 1) rather than needing the floor to catch it. Verified against the real 12-row production page: a genuine reflow drops the parse to 0 (well under 6, exit 2); a single deletion drops it to 11 (well over 6, reaches Leg 1, exit 1 naming the exact protocol).
- **Files modified:** `tools/wiki/dispatch_mirror.py` (design decision, not a post-hoc fix)
- **Verification:** All of Task 1's acceptance criteria and Task 2's fixture-based selftest case pass under this design; see coverage D1–D5 above.

---

**Total deviations:** 0 auto-fixed; 1 documented interpretive decision resolving an internal contradiction in the plan text.
**Impact on plan:** The decision was necessary for the plan's own stated acceptance criteria to be simultaneously satisfiable. No scope creep — the checker's behavior matches every acceptance criterion listed in the plan, including the ones that were in tension with its own prose.

## Issues Encountered

None beyond the interpretive decision above.

## User Setup Required

None. All verification ran against a read-only anonymous clone of `firestarter_prom.wiki.git` (no token needed) and the existing `firestarter_app`/`firestarter` checkouts already present in the workspace.

## Next Phase Readiness

- `tools/wiki/dispatch_mirror.py` is ready for `168-13` to wire into `.github/workflows/wiki-check.yml` as one of the three scheduled checker steps, taking `--wiki-dir`, `--app-dir` and `--fw-dir` pointed at the workflow's clone/checkout steps.
- `selftest.sh` now reports 9 cases; `168-11` and `168-12` will each add one more, reaching the phase's documented final count of 11.
- The coverage 168-04 deleted is genuinely restored: doc-vs-tool correctness, doc-vs-firmware completeness, a planted-missing-entry red, and the planted-comment-only-entry fail-open finding are all functionally present in the rebuilt checker — 2 of the 4 (missing-row via the doc side, comment-only via the firmware side) are now permanent `selftest.sh` cases; the other 2 (doc-vs-tool mismatch, firmware-side missing entry) were verified manually against ad hoc fixtures during this plan but are not separately codified as selftest cases, since the plan's Task 2 scope named only the two mutations above.
- No blockers for 168-11, 168-12 or 168-13.

---
*Phase: 168-migrate-the-13-doc-files-moved-without-upgrading-a-claim*
*Completed: 2026-08-31*

## Self-Check: PASSED

- FOUND: tools/wiki/dispatch_mirror.py
- FOUND: .planning/phases/168-migrate-the-13-doc-files-moved-without-upgrading-a-claim/evidence/dispatch-mirror-planted-RED.txt
- FOUND: case_dispatch_mirror_planted_drift_exit_1 wired into tools/wiki/selftest.sh's CASES array
- FOUND commit: 356f09e0 (feat: dispatch_mirror.py)
- FOUND commit: f956c934 (test: selftest case + evidence)
