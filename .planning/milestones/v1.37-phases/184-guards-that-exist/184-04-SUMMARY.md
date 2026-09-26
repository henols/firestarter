---
phase: 184-guards-that-exist
plan: 04
subsystem: testing
tags: [dispatch-mirror, provenance, fixture-severance, no-exists-proxy, claim-hygiene]

# Dependency graph
requires:
  - phase: 184-01
    provides: "scan_paths.py entry removal and the app-repo test-module resolver check that governs tests/scan_paths.py"
  - phase: 184-03
    provides: "CLAIM-03 verdict note (.planning/notes/dispatch-invariant-retirement-verdict.md) carrying the fail-open finding, the precondition for this plan's deletion"
provides:
  - "Two orphaned planted_dispatch_* fixtures deleted from firestarter_app"
  - "Three provenance citations to tests/test_dispatch_mirror.py re-dated with its disposal (39ea3e8, 2026-08-31)"
  - "Evidence that the app repo's remaining dispatch_mirror residue is exactly the three D-02 keeps"
affects: [184-05]

# Actuals (#2632)
actuals:
  tokens: 2652
  tasks: 3
  commits: 2

tech-stack:
  added: []
  patterns: []

key-files:
  created: []
  modified:
    - firestarter_app/tools/check_no_exists_proxy.py
    - firestarter_app/tests/fixtures/planted_no_exists_proxy.py

key-decisions:
  - "Deleted (not re-pointed) both planted_dispatch_* fixtures per D-07 — under D-05's retire-outright verdict no consumer will ever exist to re-point them at."
  - "Kept the tests/test_dispatch_mirror.py name at all three citation sites and added its disposal (deleted 2026-08-31, 39ea3e8) rather than stripping the name, per D-02."
  - "Repaired the existing # comment in planted_no_exists_proxy.py in place, compressing wording to add the disposal fact without increasing the file's total comment-line count (stayed at 5)."

requirements-completed: [CLAIM-02, CLAIM-01]

coverage:
  - id: D1
    description: "Both planted_dispatch_* fixtures deleted after being read in full and after checking the verdict note already held the fail-open finding"
    requirement: "CLAIM-02"
    verification:
      - kind: other
        ref: "cd firestarter_app && test ! -e tests/fixtures/planted_dispatch_comment_only_hex.cpp && test ! -e tests/fixtures/planted_dispatch_missing_hex.cpp"
        status: pass
      - kind: other
        ref: "git ls-files -- 'tests/fixtures/planted_dispatch*' (empty)"
        status: pass
    human_judgment: false
  - id: D2
    description: "All three surviving provenance citations keep the tests/test_dispatch_mirror.py name and now state its disposal, worded consistently"
    requirement: "CLAIM-01"
    verification:
      - kind: other
        ref: "grep -c test_dispatch_mirror / 39ea3e8 / 2026-08-31 across both files"
        status: pass
      - kind: unit
        ref: "tests/test_check_no_exists_proxy.py"
        status: pass
    human_judgment: false
  - id: D3
    description: "App suite still collects cleanly (2360 tests) after the deletions; no module imports or globs a deleted fixture path"
    verification:
      - kind: other
        ref: "pytest tests/ --collect-only -q -o addopts=\"\" -> 2360 tests collected"
        status: pass
    human_judgment: false
  - id: D4
    description: "App repo's remaining dispatch_mirror occurrences are exactly the three D-02 deliberately keeps, no tools/wiki/dispatch_mirror residue"
    requirement: "CLAIM-01"
    verification:
      - kind: other
        ref: "git grep -n dispatch_mirror -- . ':(exclude).planning' -> exactly 3 hits, 2 files"
        status: pass
    human_judgment: false

duration: 24min
completed: 2026-09-11
status: complete
---

# Phase 184 Plan 04: Guards That Exist — Fixture Disposal & Citation Re-dating Summary

**Deleted the two orphaned `planted_dispatch_*` C++ fixtures whose consumer (`tests/test_dispatch_mirror.py`) was removed 2026-08-31, and re-dated the three surviving `test_dispatch_mirror.py` citations in `check_no_exists_proxy.py`/`planted_no_exists_proxy.py` to name that disposal (39ea3e8) instead of leaving it unverifiable.**

## Performance

- **Duration:** 24 min
- **Started:** 2026-09-11T00:00:00Z (approx, sequential inline execution)
- **Completed:** 2026-09-11
- **Tasks:** 3
- **Files modified:** 4 (2 deleted, 2 edited)

## Accomplishments

- Both `planted_dispatch_comment_only_hex.cpp` and `planted_dispatch_missing_hex.cpp` deleted from `firestarter_app/tests/fixtures/`, after reading each in full and checking — not assuming — that `.planning/notes/dispatch-invariant-retirement-verdict.md` (written by 184-03) already carried the comment-blind `0x[0-9A-Fa-f]+` fail-open finding those headers encoded.
- All three surviving citations of `tests/test_dispatch_mirror.py` (in `tools/check_no_exists_proxy.py` and twice in `tests/fixtures/planted_no_exists_proxy.py`) now name that module's disposal — deleted 2026-08-31 in `39ea3e8` — worded consistently across both files, with the name itself untouched.
- Proved the app suite still collects cleanly (2360 tests) after the deletions, that the three targeted test files still pass, and that the app repo's only remaining `dispatch_mirror` occurrences are exactly the three citations D-02 deliberately keeps.

## Task Commits

Each task was committed atomically, inside `/workspaces/firestarter_app`:

1. **Task 1: Delete the two orphaned `planted_dispatch_*` fixtures (D-07, CLAIM-02)** — `4a90ce4` (test)
2. **Task 2: Re-date the three surviving provenance citations (D-02, CLAIM-01)** — `a745cb6` (docs)
3. **Task 3: Prove the app suite still collects, and that the residue is exactly what D-02 keeps** — no commit (evidence-only task, no files modified)

**Gitlink advance:** the meta repo's `firestarter_app` submodule pointer is advanced to `a745cb6` in this plan's metadata commit.

## Task 1 Evidence — Precondition Check and Pre-Deletion Search

**Precondition check** (run before touching either fixture): grepped `.planning/notes/dispatch-invariant-retirement-verdict.md` for the `0x[0-9A-Fa-f]+` regex and both fixture filenames.

```
$ /usr/bin/grep -n '0x\[0-9A-Fa-f\]+' .planning/notes/dispatch-invariant-retirement-verdict.md
93:check extracted every `0x[0-9A-Fa-f]+` token from the whole file text of
212: * extracts every `0x[0-9A-Fa-f]+` token from the WHOLE file text via a bare
222:same `0x[0-9A-Fa-f]+` regex from the RED side, and explains why that sibling fixture never
230: * every `0x[0-9A-Fa-f]+` token from the WHOLE file text via a bare regex

$ /usr/bin/grep -n 'planted_dispatch_comment_only_hex.cpp\|planted_dispatch_missing_hex.cpp' .planning/notes/dispatch-invariant-retirement-verdict.md
204:`firestarter_app/tests/fixtures/planted_dispatch_comment_only_hex.cpp`'s own header states
221:GREEN was the finding, not a bug to fix. `firestarter_app/tests/fixtures/planted_dispatch_missing_hex.cpp`'s header names the
244:  $ cd /workspaces/firestarter_app && /usr/bin/grep -c '^    {0x' tests/fixtures/planted_dispatch_comment_only_hex.cpp tests/fixtures/planted_dispatch_missing_hex.cpp
245:  tests/fixtures/planted_dispatch_comment_only_hex.cpp:13
246:  tests/fixtures/planted_dispatch_missing_hex.cpp:13
```

Precondition confirmed: the note already carries the finding, quoted verbatim from both headers, before either file was deleted.

**Both fixtures were read in full.** Concrete facts taken from each header:
- `planted_dispatch_comment_only_hex.cpp` (85 lines): its paired test leg `test_planted_comment_only_hex_is_NOT_detected` asserts **GREEN, not RED** — the GREEN is the finding, because `test_dispatch_mirror_firmware_leg_enumerates_all_protocols` extracted every `0x[0-9A-Fa-f]+` token from whole file text via a comment-blind regex, so a comment-only mention of `0x10` satisfied the gate exactly as well as a real dispatch case.
- `planted_dispatch_missing_hex.cpp` (95 lines): deliberately never spells the real `flash_intel` identifier (`0x10`) as a contiguous `0x`-prefixed token anywhere in the file, not even in its own header — because a stray mention would silently satisfy the same regex and invalidate the fixture's purpose.

**Repository-wide search for `planted_dispatch`, run before deletion:**

```
$ cd /workspaces/firestarter_app && git grep -n 'planted_dispatch' -- .
tests/fixtures/planted_dispatch_comment_only_hex.cpp:15: * It is a faithful copy of `planted_dispatch_missing_hex.cpp` (itself a
exit=0
```

The only hit is one fixture naming its sibling in its own header comment — no consumer outside the two files themselves. Deletion proceeded only after this was confirmed.

**Post-deletion checks (all passed):**
```
$ test ! -e tests/fixtures/planted_dispatch_comment_only_hex.cpp && test ! -e tests/fixtures/planted_dispatch_missing_hex.cpp && echo BOTH_FIXTURES_GONE
BOTH_FIXTURES_GONE
$ git ls-files -- 'tests/fixtures/planted_dispatch*'
(empty)
$ git ls-files -- 'tests/fixtures/planted_no_exists_proxy.py'
tests/fixtures/planted_no_exists_proxy.py
$ git grep -c 'planted_dispatch' -- . ':(exclude).planning'; echo exit=$?
exit=1
$ /usr/bin/grep -c 'planted_dispatch' .planning/notes/dispatch-invariant-retirement-verdict.md
7
```

Both headers' do-not-delete instruction is **superseded by D-05 and D-07**: their consumer `tests/test_dispatch_mirror.py` was deleted 2026-08-31 by `39ea3e8`, and under D-05's retire-outright verdict no consumer will ever exist to re-point them at. The knowledge the instruction protected now lives in `.planning/notes/dispatch-invariant-retirement-verdict.md`, named in the commit message.

## Task 2 Evidence — The Three Edited Passages, Verbatim

**Site 1 — `tools/check_no_exists_proxy.py` (module docstring, compound-shape bullet):**
```
  - the compound shape: `FW_ABSENT = not (a.exists() and b.exists())` --
    exactly what `tests/test_dispatch_mirror.py` used before its rekey onto
    `tests/fw_presence.py`; that module was later deleted entirely on
    2026-08-31 (`39ea3e8`).
```

**Site 2 — `tests/fixtures/planted_no_exists_proxy.py` (module docstring, item 2):**
```
  2. `COMPOUND_ABSENCE_PROXY` -- the compound shape, a `not` over a boolean
     combination of two `.exists()` calls -- the exact shape
     `tests/test_dispatch_mirror.py` used before its own rekey; that module
     was later deleted entirely on 2026-08-31 (`39ea3e8`).
```

**Site 3 — `tests/fixtures/planted_no_exists_proxy.py` (existing `# PLANTED VIOLATION (compound shape)` comment, repaired in place, not extended):**
```
# PLANTED VIOLATION (compound shape): a module-level absence proxy over a
# boolean combination of two `.exists()` calls -- mirrors the exact shape
# test_dispatch_mirror.py used before its Phase 123 Plan 08 rekey (ANDing
# two paths before negating); deleted 2026-08-31 (`39ea3e8`).
```
This is the one existing `#` comment among the three sites; its wording was repaired in place (the redundant "(it ANDed the existence of two firmware-repo paths together before negating)" parenthetical was compressed to "(ANDing two paths before negating)" to make room for the disposal fact within the same 4 lines) — no line was added to the block, and no new block was created.

**Verify output (all matched the plan's exact-count gates):**
```
test_dispatch_mirror: check_no_exists_proxy.py=1, planted_no_exists_proxy.py=2
39ea3e8:              check_no_exists_proxy.py=1, planted_no_exists_proxy.py=2
2026-08-31:            check_no_exists_proxy.py=1, planted_no_exists_proxy.py=2
comment-line count of planted_no_exists_proxy.py: 5 (unchanged from before this task)
tests/test_check_no_exists_proxy.py: 8 passed in 0.77s
SIMPLE_ABSENCE_PROXY|COMPOUND_ABSENCE_PROXY|legitimate_in_function_check count: 6 (unchanged)
```

`git diff` for both files touches only the module docstrings and the one existing comment block — no executable line changed in either file (confirmed by inspecting the diff before committing).

## Task 3 Evidence — Collection, Targeted Tests, and the `dispatch_mirror` Residue

**Collection (deliberately not a full run):**
```
$ .venv311/bin/python -m pytest tests/ --collect-only -q -o addopts=""
2360 tests collected in 1.77s
```
A full run was deliberately not used: `/dev/ttyACM0` is attached in this devcontainer, which reddens `test_no_programmer_found_*` for reasons unrelated to this phase (per `184-CONTEXT.md`'s flagged assumption and the project's own characterization-test memory). Collection is what actually catches the realistic failure mode of Task 1 — a module that imported, globbed, or parametrized over a deleted fixture path — and it passed clean at 2360, above the 2300-test floor and consistent with the pre-phase count of 2359 (+1 net from an unrelated prior wave commit).

**Targeted tests:**
```
$ .venv311/bin/python -m pytest tests/test_check_no_exists_proxy.py tests/test_sdp_honesty.py tests/test_scan_paths_resolve.py -o addopts="" -q
22 passed in 1.22s
```

**`dispatch_mirror` residue enumeration (full output):**
```
$ git grep -n 'dispatch_mirror' -- . ':(exclude).planning'
tests/fixtures/planted_no_exists_proxy.py:20:     `tests/test_dispatch_mirror.py` used before its own rekey; that module
tests/fixtures/planted_no_exists_proxy.py:42:# test_dispatch_mirror.py used before its Phase 123 Plan 08 rekey (ANDing
tools/check_no_exists_proxy.py:19:    exactly what `tests/test_dispatch_mirror.py` used before its rekey onto
```
Exactly three hits across exactly two files (`tests/fixtures/planted_no_exists_proxy.py`, `tools/check_no_exists_proxy.py`), and every one names `tests/test_dispatch_mirror.py`. A separate check for `tools/wiki/dispatch_mirror` returned nothing (exit 1). These three are the citations D-02 deliberately keeps — a different module (`tests/test_dispatch_mirror.py`, app repo, deleted 2026-08-31 by `39ea3e8`), unrelated to the deleted meta-repo checker `tools/wiki/dispatch_mirror.py` (deleted 2026-09-02 by `5426d7ef`) that CLAIM-01's literal criterion 1 grep collides with. This is exactly the collision D-03 amends success criterion 1 for; the amendment itself lands in `184-05`, and this task supplies the evidence it rests on.

**Final porcelain check:**
```
$ git status --porcelain
(empty — no output for tracked paths; two pre-existing untracked datasheets/*.pdf files, unrelated to this plan, are left alone per the orchestrator's instructions)
```

## Files Created/Modified

- `firestarter_app/tests/fixtures/planted_dispatch_comment_only_hex.cpp` — deleted (whole file, 85 lines)
- `firestarter_app/tests/fixtures/planted_dispatch_missing_hex.cpp` — deleted (whole file, 95 lines)
- `firestarter_app/tools/check_no_exists_proxy.py` — module docstring, compound-shape citation re-dated
- `firestarter_app/tests/fixtures/planted_no_exists_proxy.py` — module docstring item 2 and one existing `#` comment re-dated; lint behaviour and all three planted subjects unchanged

## Decisions Made

- Followed D-07 exactly: deleted rather than re-pointed, because D-05's retire-outright verdict means no consumer will ever exist to re-point either fixture at.
- Followed D-02 exactly: kept the `tests/test_dispatch_mirror.py` name at all three citation sites and added its disposal, rather than stripping the name (which the plan explicitly prohibits) or leaving the citation unverifiable.
- At the one existing-comment site, chose to compress the redundant "(it ANDed the existence of two firmware-repo paths together before negating)" parenthetical into "(ANDing two paths before negating)" so the disposal fact fit inside the same 4-line block without exceeding the file's pre-task comment-line count of 5. This is a prose compression of an existing line, not new commentary, and preserves the same information (the docstring above it already states "a boolean combination of two `.exists()` calls").

## Deviations from Plan

None — plan executed exactly as written.

### Observation (not a deviation, no fix required)

Task 3's `<precondition>` and `<read_first>` name `firestarter_app/tests/test_flash_path_record_sync.py` as asserting the whole repository is porcelain. That file does not exist in the current `firestarter_app` tree (`find . -iname '*flash_path_record_sync*'` returns nothing; `git grep -ln porcelain -- tests/` shows five other files, none matching that name, and the one that checks `git status --porcelain` — `tests/test_py32_asset_name_host.py` — checks the **firmware** repo's porcelain status, not the app repo's). This is a stale citation in the plan, most likely inherited from an earlier planning pass. It did not block this plan: Tasks 1 and 2 were committed before Task 3 ran regardless, per the plan's own ordering, and the two pre-existing untracked `datasheets/*.pdf` files (present before this plan started, explicitly out of scope per the orchestrator's instructions) do not affect `git status --porcelain`'s tracked-file assertions used elsewhere in the suite. Left unfixed per the scope boundary — out of scope for this plan's `files_modified` list.


**Orchestrator correction to the observation above.** The citation is wrong in its *repository*,
not in its existence. `test_flash_path_record_sync.py` is real, is 54 KB, and lives in the
**firmware** repo:

```
$ ls -la /workspaces/firestarter/tests/test_flash_path_record_sync.py
-rw-r--r-- 1 vscode vscode 54608 Aug  2 21:07 firestarter/tests/test_flash_path_record_sync.py
$ git -C /workspaces/firestarter_app log --all --name-only --pretty=format: -- '*flash_path_record_sync*'
(nothing — it has never existed in the app repo under any name)
```

`test_flash_path_record_sync.py::test_planted_mutation_of_the_real_subset_is_detected` does assert
that an entire repository's `git status --porcelain` is empty, unscoped to the one file it tests —
but the repository it asserts is `firestarter`, and it is one of five such `test_planted_*` gates
there. So Task 3's `<precondition>` is a **misattribution across repositories**: that gate has never
governed `firestarter_app`, and committing Tasks 1 and 2 first was never what kept it green.

The correction does not change the executor's disposition — the precondition was satisfied for an
unrelated and sufficient reason (GSD's atomic-commit-per-task rule), the plan's own ordering held,
and no `files_modified` entry is affected. It is recorded because "the file does not exist" and "the
file exists in the other repository" are different facts, and this phase does not get to leave the
weaker one standing in its own record.
## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- CLAIM-02 is fully disposed: both orphaned fixtures are gone, and the knowledge they encoded is on record in `.planning/notes/dispatch-invariant-retirement-verdict.md` (184-03).
- CLAIM-01's app-repo work is complete: the three surviving `test_dispatch_mirror.py` citations now name their subject's disposal.
- `184-05` can now amend success criterion 1 (D-03) using this plan's Task 3 evidence — the exact three-hit, two-file `dispatch_mirror` enumeration is recorded above.
- The app suite collects cleanly at 2360 tests and all targeted tests pass; no blockers for the next plan.

---
*Phase: 184-guards-that-exist*
*Completed: 2026-09-11*

## Self-Check: PASSED

- `.planning/phases/184-guards-that-exist/184-04-SUMMARY.md` exists on disk.
- Both `planted_dispatch_*` fixtures confirmed absent from `firestarter_app/tests/fixtures/`.
- `firestarter_app` commits `4a90ce4` and `a745cb6` found in `git log --oneline --all`.
- Meta-repo commit `262ae84` (SUMMARY + gitlink advance) found in `git log --oneline --all`.
