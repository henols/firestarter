---
phase: 140-parameter-table
plan: 02
subsystem: firmware
tags: [eprom, protocol-dispatch, pytest-gate, static-analysis, fail-closed, table-05]

# Dependency graph
requires:
  - phase: 140-01
    provides: "eprom_params.cpp (the params-table half this gate's params_table leg scans) and the confirmed-byte-unchanged src/proms/eprom.cpp (D-10) this gate's blob-SHA leg pins"
provides:
  - "tests/golden/protocol_branch_inventory.json: the pinned two-tier (24-site) branch-predicate inventory for src/proms/eprom.cpp, plus eprom_params.cpp's switch-free/key-comparison/keys assertion"
  - "tests/test_protocol_branch_inventory.py: the 7-test D-13 gate -- an independent live re-parser (comment/string-stripped, bracket-matched) compared positionally against the pinned inventory"
  - "D-15 proof: the gate seen RED on 3 distinct planted violations (new protocol-keyed site, new non-inventoried handle-field site, vacuous/empty scan target) and GREEN once on the real tree, verbatim below"
affects: [140-07-close-reconciliation, 141-per-byte-program-loop, 142-vpp-routing-rewrite]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Independent live re-parse of C/C++ branch predicates (comment/string-stripped, bracket-matched, not flat-regex) compared positionally against a committed JSON inventory -- the D-13/TABLE-05 gate shape"
    - "Two-tier pinned inventory (tier-1 algorithm-keyed vs tier-2 allowlisted-with-reason) resolving 'forbidding a class of branch would be RED on arrival against ~20 pre-existing sites' (D-15 trap 2)"

key-files:
  created:
    - firestarter/tests/golden/protocol_branch_inventory.json
    - firestarter/tests/test_protocol_branch_inventory.py
  modified: []

key-decisions:
  - "Predicate text = 'keyword (condition)' for if/while/switch (matches 140-PATTERNS.md's Read-Only Reference table verbatim); bare middle-clause/ternary-condition text for for-loops and ternaries (the gate_specification's own span definition)"
  - "keyed_on is a purely mechanical regex extraction of every literal handle-><field> occurrence, including through function-pointer fields like firestarter_get_data/firestarter_get_control_register -- human judgment happens only in the class/reason classification, never in extraction"
  - "eprom_params.cpp's own docstring uses the word 'switch' twice in prose explaining the file contains none -- the params_table leg comment-strips before counting, confirmed by measuring 2 raw vs 0 comment-stripped occurrences before writing the assertion"

patterns-established:
  - "Any future gate scanning this repo's C/C++ source for a bare keyword (switch, if, etc.) MUST comment-strip first -- eprom_params.cpp's own docstring is now a standing, verified example of why a raw scan is RED on arrival for the wrong reason"

requirements-completed: []

coverage:
  - id: D1
    description: "Pinned two-tier (24-site) branch-predicate inventory for src/proms/eprom.cpp, classified and reasoned; exactly 3 tier-1 (protocol-keyed) sites at lines 71/145/218; eprom_params.cpp proved switch-free with exactly 1 key comparison and keys 0x07/0x08/0x0B"
    verification:
      - kind: other
        ref: "python3 -c \"...\" against tests/golden/protocol_branch_inventory.json -> INVENTORY_OK sites=24; blob-SHA cross-check: both source paths' recorded blob_sha equal live `git rev-parse HEAD:<path>`"
        status: pass
    human_judgment: false
  - id: D2
    description: "The 7-test D-13 gate (test_protocol_branch_inventory.py): independent live re-parser, blob-SHA pin (doubling as the D-10 byte-unchanged proof), positional site comparison naming the first divergence, non-vacuity, params-table scan, default-target-resolution, git-required self-scan"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_protocol_branch_inventory.py -v -- 7 passed"
        status: pass
      - kind: integration
        ref: "cd firestarter && python3 -m pytest tests/ -q -> 234 passed, 0 failed; python3 -m pytest tests/test_checker_convention.py -q -> 7 passed (module correctly stays outside the checker glob)"
        status: pass
    human_judgment: false
  - id: D3
    description: "D-15 non-vacuity proof: the gate seen RED on 3 distinct planted violations (Run A: new protocol-keyed site; Run B: new non-inventoried handle-field site; Run C: vacuous/empty scan target) for the right reason each time, and GREEN once (Run D) on the real, byte-unchanged tree"
    verification:
      - kind: other
        ref: "4 mktemp-scoped planted runs against tests/test_protocol_branch_inventory.py -- verbatim output in this SUMMARY's 'Planted-Violation Proof' section"
        status: pass
    human_judgment: false

# Metrics
duration: 30min
completed: 2026-08-10
status: complete
---

# Phase 140 Plan 02: Protocol-Branch Inventory Gate Summary

**24-site two-tier branch-predicate inventory pinning `eprom.cpp`'s exactly-3 protocol-keyed algorithm sites, enforced by a 7-test independent bracket-matched re-parser gate, proven RED on 3 planted violations before its GREEN was believed.**

## Performance

- **Duration:** ~30 min
- **Started:** ~2026-08-10T01:01:00Z
- **Completed:** 2026-08-10T01:30:00Z
- **Tasks:** 3 (as planned)
- **Files modified:** 2 (both new, as planned; 0 deviations)

## Accomplishments

- Derived the complete 24-site branch-predicate inventory for `src/proms/eprom.cpp`, cross-validated **three independent ways** (manual line-by-line read of the whole 332-line file, a throwaway extractor script per the plan's `<gate_specification>`, and raw `grep` counts of `if`/`for`/`switch`/`while`/`?`): exactly **3 tier-1 (protocol-keyed) sites at lines 71, 145, 218**, and exactly **21 tier-2 sites**, each classified (`algorithm_selector` / `vpp_route` / `pin_routing` / `operation_flag` / `command_dispatch` / `loop_bounds` / `status_check` / `data_compare`) with a one-sentence reason stating why it is not an algorithm selector.
- Shipped `firestarter/tests/golden/protocol_branch_inventory.json` (280 lines) -- `meta` block with per-file blob SHAs, `why_two_checks` / `how_to_update` / `frozen_for` / `allowlist_rationale` prose, the ordered 24-site array, `counts`, and `params_table` (0 switch statements, 1 key comparison, keys `0x07`/`0x08`/`0x0B`).
- Shipped `firestarter/tests/test_protocol_branch_inventory.py` (565 lines) -- 7 pytest cases with a self-contained comment/string-stripping, bracket-matched extractor (no `conftest.py`, no import of any `check_*.py` machinery, stdlib+pytest only), the two documented env seams, and a self-scan forbidding any skip bypass.
- Proved D-15 non-vacuity: 3 distinct planted violations, each seen RED for the correct, named reason (never a `git`/import/path error), plus one GREEN run on the real, byte-unchanged tree -- all four runs captured verbatim below.
- Reconfirmed `src/proms/eprom.cpp` remains byte-unchanged (D-10): blob SHA pinned in the inventory and `git diff --quiet -- src/proms/eprom.cpp` exits 0, both before and after every planted-violation run.
- `cd firestarter && python3 -m pytest tests/ -q` -> **234 passed, 0 failed** (227 baseline from 140-01 + this plan's 7); `tests/test_checker_convention.py -q` -> 7 passed, unaffected (this module correctly stays outside its `check_*.py` glob, adding no fixtures and no `scripts/` entry).

## Task Commits

1. **Task 1: Author tests/golden/protocol_branch_inventory.json** -- `5ad3c13` (feat, firestarter)
2. **Task 2: Author tests/test_protocol_branch_inventory.py** -- `af5de12` (feat, firestarter)
3. **Task 3: Plant three violations, see RED, capture verbatim, then see GREEN** -- no new commit (proof-only task against the artifacts from Tasks 1-2; produces no tracked file change -- every planted input lived in a `mktemp -d` scratch directory outside both repositories and was deleted immediately after its run). Evidence recorded in this SUMMARY.

**Plan metadata:** this SUMMARY's own commit (docs: complete plan) -- see final commit below.

## Files Created/Modified

- `firestarter/tests/golden/protocol_branch_inventory.json` (new, 280 lines) -- the pinned two-tier branch-predicate inventory and the `eprom_params.cpp` params-table assertion.
- `firestarter/tests/test_protocol_branch_inventory.py` (new, 565 lines) -- the 7-test D-13/TABLE-05 gate.

## Decisions Made

- **Predicate text format:** `"{keyword} ({condition})"` for `if`/`while`/`switch` (matches `140-PATTERNS.md`'s Read-Only Reference table verbatim, e.g. `"switch (handle->protocol)"`); the bare condition text for `for`-loop middle clauses and ternary conditions (no keyword wrapper), since the gate specification defines the "span" itself as just that clause for those two constructs.
- **`keyed_on` is purely mechanical** (a regex over every literal `handle-><field>` occurrence, plus the three literal tokens for `is_flag_set`/`using_p1_as_vpp`/`is_operation_in_progress`), never a semantic filter -- e.g. line 132's `handle->firestarter_get_data(...)` correctly contributes `firestarter_get_data` to `keyed_on` because it IS a struct field access, even though it's a function-pointer call rather than a plain data read. The human judgment this plan calls for is confined to the `class`/`reason` classification step, never the extraction step.
- **Comment-stripping is load-bearing for the params-table leg, not optional:** measured before writing the assertion that `src/proms/eprom_params.cpp`'s own docstring contains the literal word "switch" twice (explaining that the accessor uses a linear scan "never a switch"), so a raw (non-comment-stripped) token count would report 2 and fail this gate on arrival for a completely wrong reason. `_scan_params_table` strips comments first; verified 2 (raw) vs 0 (comment-stripped) before committing the golden JSON.
- **Ternary handling exercised for real, not just theoretically:** `eprom.cpp:296`'s `is_flag_set(FLAG_FORCE) ? RESPONSE_CODE_WARNING : RESPONSE_CODE_ERROR` is the file's one ternary and is correctly extracted as a tier-"other" `operation_flag` site -- confirmed via `grep -n '?' src/proms/eprom.cpp` returning exactly this one line before finalizing the inventory.
- **Followed the plan's exact Task-3 planting recipe verbatim** (the same `sed '146i\...'` insertions and `mktemp -d`/env-seam/cleanup discipline given in the plan's own `<verify>` blocks) rather than inventing alternative planted violations, so the captured evidence matches what a reviewer re-running the plan's literal commands would see.

## Deviations from Plan

None - plan executed exactly as written. No auto-fixes, no blocking issues, no architectural questions arose; the 24-site derivation matched the plan's stated 21-line tier-2 floor and 3-line tier-1 pin exactly (not merely as a superset).

## Issues Encountered

- **Transient, self-resolving full-suite failure during Task 2's own verification (not a real regression).** Running `python3 -m pytest tests/ -q` immediately after writing (but before committing) Task 2's file showed `tests/test_flash_path_record_sync.py::TestFlashPathRecordSync::test_planted_mutation_of_the_real_subset_is_detected` FAILED, because that pre-existing (Phase 129) test's own planted-mutation proof asserts the **entire** firmware repo's `git status --porcelain` is empty -- and at that moment it was not, because Task 2's own new file was still untracked. Committing Task 2 immediately resolved it: re-running `python3 -m pytest tests/ -q` on the now-clean tree showed `234 passed`. Not treated as a deviation (no code was wrong; the ordering was simply verify-before-commit colliding with an unrelated test's whole-repo cleanliness assumption). Named here per this project's own "name the divergence" convention rather than left implicit.
- **Run B and Run C's planted violations also failed `test_exactly_three_protocol_keyed_sites_at_the_pinned_lines` (test 3), not only their primary named test.** The plan's action text names test 2 as Run B's expected failure and test 4 as Run C's, but inserting a line via `sed` shifts every subsequent line number by one, so the tier-1 site originally at `:218` is also reported at a shifted line in both runs' live re-parse -- a benign, correctly-detected side effect of the insertion mechanics, not a sign of a wrong extractor. Both runs still failed for the right, named reason on their primary test; this is disclosed for completeness rather than smoothed over.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The firmware half of TABLE-05's gate is committed, lives in the repo that can see what it checks (`firestarter/tests/`), and runs in that repo's `pytest tests/ -v` CI leg (`build.yml` / `beta-build.yml`) with no cross-repo path seam.
- `src/proms/eprom.cpp` remains byte-unchanged; `native_trace_v131`'s frozen fixture stays GREEN through this phase (D-10 preserved) -- confirmed indirectly via the unchanged blob SHA and directly via `git diff --quiet`.
- Phase 141 (per-byte program loop) and Phase 142 (VPP-routing rewrite) are the two events this inventory is explicitly `frozen_for`: when either phase legitimately changes `eprom.cpp`, this gate will go RED and must be re-derived (never hand-edited) with the commit message stating which site moved and why -- that is the intended, expected interaction, not a phase-140 concern.
- This plan marks **no requirement checkbox complete**, per its own `<requirement_completion>` scope: TABLE-05 spans this plan (firmware half) and 140-03 (DB half, already shipped per `140-03-SUMMARY.md`); only plan 140-07 may flip either checkbox in `.planning/REQUIREMENTS.md`.
- No blockers for the remaining Wave 2 plans (140-04, 140-05) or for 140-06/140-07. Wave 2's shared-submodule concurrency note was observed in practice: `git status --porcelain` showed only this plan's own files at every commit point, and no sibling-plan file was staged or touched.

---
*Phase: 140-parameter-table*
*Completed: 2026-08-10*

## Planted-Violation Proof (D-15)

All four runs below reproduce, verbatim, the plan's own literal `<verify>` command lines and their exact stdout. Every planted input lived in a `mktemp -d` scratch directory outside both repositories and was deleted immediately after its run (`rm -rf "$T"`); `git -C /workspaces/firestarter status --porcelain` and `git -C /workspaces/firestarter diff --quiet -- src/proms/eprom.cpp` were both re-confirmed clean after all four runs completed.

### Run A -- a new protocol-keyed branch site (expect RED on tests 2 and 3)

Command:
```
cd /workspaces/firestarter && T=$(mktemp -d) && sed '146i\    if (handle->protocol == 0x07) { }' src/proms/eprom.cpp > "$T/eprom.cpp" && FIRESTARTER_BRANCH_SCAN_SOURCE="$T/eprom.cpp" python3 -m pytest tests/test_protocol_branch_inventory.py -q; rc=$?; rm -rf "$T"; test $rc -ne 0 && echo "RUN_A_RED_AS_REQUIRED rc=$rc"
```

Verbatim stdout:
```
.FF....                                                                  [100%]
=================================== FAILURES ===================================
________________ test_branch_sites_match_the_recorded_inventory ________________

    def test_branch_sites_match_the_recorded_inventory():
        inventory = _load_inventory()
        recorded = [
            (s["line"], s["predicate"], s["keyed_on"], s["tier"])
            for s in inventory["sites"]
        ]
        live = [
            (s["line"], s["predicate"], s["keyed_on"], s["tier"])
            for s in _extract_predicates(_SCAN_EPROM.read_text())
        ]
    
        n = min(len(recorded), len(live))
        for i in range(n):
            if recorded[i] != live[i]:
>               raise AssertionError(
                    f"first divergence at index {i} -- recorded={recorded[i]!r}, "
                    f"live={live[i]!r}. A NEW branch site, a changed predicate "
                    "spelling, or a changed keyed_on/tier is exactly the class "
                    "of change TABLE-05's gate exists to catch."
                )
E               AssertionError: first divergence at index 14 -- recorded=(218, 'if (handle->protocol == 0x0B || is_flag_set(FLAG_VPE_AS_VPP))', ['ctrl_flags', 'protocol'], 'protocol'), live=(146, 'if (handle->protocol == 0x07)', ['protocol'], 'protocol'). A NEW branch site, a changed predicate spelling, or a changed keyed_on/tier is exactly the class of change TABLE-05's gate exists to catch.

tests/test_protocol_branch_inventory.py:431: AssertionError
_________ test_exactly_three_protocol_keyed_sites_at_the_pinned_lines __________

    def test_exactly_three_protocol_keyed_sites_at_the_pinned_lines():
        live = _extract_predicates(_SCAN_EPROM.read_text())
        protocol_lines = sorted(s["line"] for s in live if s["tier"] == "protocol")
>       assert protocol_lines == [71, 145, 218], (
            "expected exactly three tier-protocol sites at lines [71, 145, "
            f"218], found {protocol_lines}. A fourth protocol-keyed branch "
            "site is a second algorithm selector and a TABLE-05 violation -- "
            "fewer than three means one of the pinned sites was removed "
            "without updating this inventory."
        )
E       AssertionError: expected exactly three tier-protocol sites at lines [71, 145, 218], found [71, 145, 146, 219]. A fourth protocol-keyed branch site is a second algorithm selector and a TABLE-05 violation -- fewer than three means one of the pinned sites was removed without updating this inventory.
E       assert [71, 145, 146, 219] == [71, 145, 218]
E         
E         At index 2 diff: 146 != 218
E         Left contains one more item: 219
E         Use -v to get more diff

tests/test_protocol_branch_inventory.py:446: AssertionError
=========================== short test summary info ============================
FAILED tests/test_protocol_branch_inventory.py::test_branch_sites_match_the_recorded_inventory
FAILED tests/test_protocol_branch_inventory.py::test_exactly_three_protocol_keyed_sites_at_the_pinned_lines
2 failed, 5 passed in 0.07s
RUN_A_RED_AS_REQUIRED rc=1
```

### Run B -- a branch keyed on a handle field not in the inventory (expect RED on test 2)

Command:
```
cd /workspaces/firestarter && T=$(mktemp -d) && sed '146i\    if (handle->mem_size > 0) { }' src/proms/eprom.cpp > "$T/eprom.cpp" && FIRESTARTER_BRANCH_SCAN_SOURCE="$T/eprom.cpp" python3 -m pytest tests/test_protocol_branch_inventory.py -q; rc=$?; rm -rf "$T"; test $rc -ne 0 && echo "RUN_B_RED_AS_REQUIRED rc=$rc"
```

Verbatim stdout:
```
.FF....                                                                  [100%]
=================================== FAILURES ===================================
________________ test_branch_sites_match_the_recorded_inventory ________________

    def test_branch_sites_match_the_recorded_inventory():
        inventory = _load_inventory()
        recorded = [
            (s["line"], s["predicate"], s["keyed_on"], s["tier"])
            for s in inventory["sites"]
        ]
        live = [
            (s["line"], s["predicate"], s["keyed_on"], s["tier"])
            for s in _extract_predicates(_SCAN_EPROM.read_text())
        ]
    
        n = min(len(recorded), len(live))
        for i in range(n):
            if recorded[i] != live[i]:
>               raise AssertionError(
                    f"first divergence at index {i} -- recorded={recorded[i]!r}, "
                    f"live={live[i]!r}. A NEW branch site, a changed predicate "
                    "spelling, or a changed keyed_on/tier is exactly the class "
                    "of change TABLE-05's gate exists to catch."
                )
E               AssertionError: first divergence at index 14 -- recorded=(218, 'if (handle->protocol == 0x0B || is_flag_set(FLAG_VPE_AS_VPP))', ['ctrl_flags', 'protocol'], 'protocol'), live=(146, 'if (handle->mem_size > 0)', ['mem_size'], 'other'). A NEW branch site, a changed predicate spelling, or a changed keyed_on/tier is exactly the class of change TABLE-05's gate exists to catch.

tests/test_protocol_branch_inventory.py:431: AssertionError
_________ test_exactly_three_protocol_keyed_sites_at_the_pinned_lines __________

    def test_exactly_three_protocol_keyed_sites_at_the_pinned_lines():
        live = _extract_predicates(_SCAN_EPROM.read_text())
        protocol_lines = sorted(s["line"] for s in live if s["tier"] == "protocol")
>       assert protocol_lines == [71, 145, 218], (
            "expected exactly three tier-protocol sites at lines [71, 145, "
            f"218], found {protocol_lines}. A fourth protocol-keyed branch "
            "site is a second algorithm selector and a TABLE-05 violation -- "
            "fewer than three means one of the pinned sites was removed "
            "without updating this inventory."
        )
E       AssertionError: expected exactly three tier-protocol sites at lines [71, 145, 218], found [71, 145, 219]. A fourth protocol-keyed branch site is a second algorithm selector and a TABLE-05 violation -- fewer than three means one of the pinned sites was removed without updating this inventory.
E       assert [71, 145, 219] == [71, 145, 218]
E         
E         At index 2 diff: 219 != 218
E         Use -v to get more diff

tests/test_protocol_branch_inventory.py:446: AssertionError
=========================== short test summary info ============================
FAILED tests/test_protocol_branch_inventory.py::test_branch_sites_match_the_recorded_inventory
FAILED tests/test_protocol_branch_inventory.py::test_exactly_three_protocol_keyed_sites_at_the_pinned_lines
2 failed, 5 passed in 0.11s
RUN_B_RED_AS_REQUIRED rc=1
```

### Run C -- a vacuous (empty) scan target (expect RED on test 4, non-vacuity)

Command:
```
cd /workspaces/firestarter && T=$(mktemp -d) && : > "$T/empty.cpp" && FIRESTARTER_BRANCH_SCAN_SOURCE="$T/empty.cpp" python3 -m pytest tests/test_protocol_branch_inventory.py -q; rc=$?; rm -rf "$T"; test $rc -ne 0 && echo "RUN_C_RED_AS_REQUIRED rc=$rc"
```

Verbatim stdout:
```
.FFF...                                                                  [100%]
=================================== FAILURES ===================================
________________ test_branch_sites_match_the_recorded_inventory ________________

    def test_branch_sites_match_the_recorded_inventory():
        inventory = _load_inventory()
        recorded = [
            (s["line"], s["predicate"], s["keyed_on"], s["tier"])
            for s in inventory["sites"]
        ]
        live = [
            (s["line"], s["predicate"], s["keyed_on"], s["tier"])
            for s in _extract_predicates(_SCAN_EPROM.read_text())
        ]
    
        n = min(len(recorded), len(live))
        for i in range(n):
            if recorded[i] != live[i]:
                raise AssertionError(
                    f"first divergence at index {i} -- recorded={recorded[i]!r}, "
                    f"live={live[i]!r}. A NEW branch site, a changed predicate "
                    "spelling, or a changed keyed_on/tier is exactly the class "
                    "of change TABLE-05's gate exists to catch."
                )
>       assert len(recorded) == len(live), (
            f"site count diverged after {n} matching entries -- "
            f"recorded_count={len(recorded)} live_count={len(live)}"
        )
E       AssertionError: site count diverged after 0 matching entries -- recorded_count=24 live_count=0
E       assert 24 == 0
E        +  where 24 = len([(46, 'switch (handle->cmd)', ['cmd'], 'other'), (53, 'if (!is_flag_set(FLAG_SKIP_BLANK_CHECK))', ['ctrl_flags'], 'oth...peration_state'], 'other'), (96, 'if (handle->response_code == RESPONSE_CODE_ERROR)', ['response_code'], 'other'), ...])
E        +  and   0 = len([])

tests/test_protocol_branch_inventory.py:437: AssertionError
_________ test_exactly_three_protocol_keyed_sites_at_the_pinned_lines __________

    def test_exactly_three_protocol_keyed_sites_at_the_pinned_lines():
        live = _extract_predicates(_SCAN_EPROM.read_text())
        protocol_lines = sorted(s["line"] for s in live if s["tier"] == "protocol")
>       assert protocol_lines == [71, 145, 218], (
            "expected exactly three tier-protocol sites at lines [71, 145, "
            f"218], found {protocol_lines}. A fourth protocol-keyed branch "
            "site is a second algorithm selector and a TABLE-05 violation -- "
            "fewer than three means one of the pinned sites was removed "
            "without updating this inventory."
        )
E       AssertionError: expected exactly three tier-protocol sites at lines [71, 145, 218], found []. A fourth protocol-keyed branch site is a second algorithm selector and a TABLE-05 violation -- fewer than three means one of the pinned sites was removed without updating this inventory.
E       assert [] == [71, 145, 218]
E         
E         Right contains 3 more items, first extra item: 71
E         Use -v to get more diff

tests/test_protocol_branch_inventory.py:446: AssertionError
________________________ test_inventory_is_non_vacuous _________________________

    def test_inventory_is_non_vacuous():
        inventory = _load_inventory()
        sites = inventory["sites"]
        assert len(sites) >= 24, (
            f"non-vacuous guard: expected >= 24 recorded sites, got "
            f"{len(sites)} -- an empty or truncated inventory must FAIL, not "
            "silently pass."
        )
        for s in sites:
            assert s.get("predicate") and s.get("reason"), (
                f"non-vacuous guard: site at line {s.get('line')!r} is missing "
                "a non-empty predicate or reason."
            )
    
        targets = (_SCAN_EPROM, _SCAN_PARAMS)
        existing_nonempty = [p for p in targets if p.is_file() and p.stat().st_size > 0]
        sizes = {str(p): (p.stat().st_size if p.is_file() else None) for p in targets}
>       assert len(existing_nonempty) == 2, (
            "non-vacuous guard: expected exactly 2 scan targets to exist and "
            f"be non-empty, found {len(existing_nonempty)} of 2 -- sizes="
            f"{sizes}. A vacuous (missing or empty) scan target must FAIL, "
            "never silently pass as if nothing needed checking."
        )
E       AssertionError: non-vacuous guard: expected exactly 2 scan targets to exist and be non-empty, found 1 of 2 -- sizes={'/tmp/tmp.jRJVlpOpOY/empty.cpp': 0, '/workspaces/firestarter/src/proms/eprom_params.cpp': 3116}. A vacuous (missing or empty) scan target must FAIL, never silently pass as if nothing needed checking.
E       assert 1 == 2
E        +  where 1 = len([PosixPath('/workspaces/firestarter/src/proms/eprom_params.cpp')])

tests/test_protocol_branch_inventory.py:472: AssertionError
=========================== short test summary info ============================
FAILED tests/test_protocol_branch_inventory.py::test_branch_sites_match_the_recorded_inventory
FAILED tests/test_protocol_branch_inventory.py::test_exactly_three_protocol_keyed_sites_at_the_pinned_lines
FAILED tests/test_protocol_branch_inventory.py::test_inventory_is_non_vacuous
3 failed, 4 passed in 0.07s
RUN_C_RED_AS_REQUIRED rc=1
```

### Run D -- the real tree, no env seam set (expect GREEN, 7 passed)

Command:
```
cd /workspaces/firestarter && python3 -m pytest tests/test_protocol_branch_inventory.py -q 2>&1 | tail -3 && git diff --quiet -- src/proms/eprom.cpp && echo "RUN_D_GREEN_AND_EPROM_UNCHANGED"
```

Verbatim stdout:
```
.......                                                                  [100%]
7 passed in 0.06s
RUN_D_GREEN_AND_EPROM_UNCHANGED
```

### Post-proof cleanliness re-check

```
$ git -C /workspaces/firestarter status --porcelain
(empty)
$ git -C /workspaces/firestarter diff --quiet -- src/proms/eprom.cpp && echo "eprom.cpp still byte-unchanged"
eprom.cpp still byte-unchanged
```

No RED run failed for the wrong reason (no `git` error, import error, or path error in any of the three) -- every failure named the planted site or the non-vacuity condition explicitly, so no locator fix was required and all four runs were captured on the first attempt.

## Self-Check: PASSED

Files verified present on disk (before writing this SUMMARY):
- FOUND: `firestarter/tests/golden/protocol_branch_inventory.json`
- FOUND: `firestarter/tests/test_protocol_branch_inventory.py`

Commits verified present in git history (before writing this SUMMARY):
- FOUND (firestarter): `5ad3c13`
- FOUND (firestarter): `af5de12`
