---
phase: 124-firmware-integration-merge
plan: "05"
subsystem: firmware-ci
tags: [firestarter, cmake, py32f071, ci, pytest, drift-gate]

# Dependency graph
requires:
  - phase: 124-firmware-integration-merge
    plan: "04"
    provides: "The landed tree (e2c422d) and its recorded post-landing measurement set: 9 check_cmake_manifest.py violations, 2 expiring pytests, AVR flash/RAM figures every later plan is judged against."
provides:
  - "platform/py32f071/CMakeLists.txt names flash_nor_unlock.cpp and flash_5v_page.cpp (the v1.19 Phase 104 rename), not the stale flash_type_3/4.cpp -- MERGE-02's textual half"
  - "check_cmake_manifest.py driven from 9 violations to 0 (PASS), via the rename fix plus D-15's five reasoned PY32_EXCLUDED allow-list entries"
  - "py32f071.yml carries push: branches: [beta] with no paths filter, verified by reading the file -- MERGE-03 in full"
  - "tests/test_check_cmake_manifest.py's expiring test inverted to test_armed_and_passing_on_the_real_tree, pinning the ARMED/PASS state"
affects: [124-06, 124-08, 124-10, 124-11, 124-12, 124-close]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "PY32_EXCLUDED allow-list comment block placed immediately above set(FIRESTARTER_COMMON_SOURCES so a reader meets the five deliberate omissions before the enforced list itself"
    - "A commented, non-code decision record (the ARM DEV_TOOLS-off rationale) placed directly above the target_compile_definitions block it explains, mirroring the PY32_EXCLUDED placement convention"

key-files:
  created: []
  modified:
    - firestarter/platform/py32f071/CMakeLists.txt
    - firestarter/.github/workflows/py32f071.yml
    - firestarter/tests/test_check_cmake_manifest.py

key-decisions:
  - "D-15's src/dev_tools.cpp PY32_EXCLUDED reason was written already amended (per D-02's uniform value-semantics mechanism: 'no ARM dev-tools TU; DEV_TOOLS resolves to 0 by the shared default (MERGE-08, D-02)'), not the checker docstring's original 'deliberately off by omission' wording. Plan 124-06 lands the shared #ifndef DEV_TOOLS / #define DEV_TOOLS 0 default in the same wave, so this reason describes end-of-wave state, not this plan's own commit in isolation."
  - "The rurp_config_utils.cpp PY32_EXCLUDED reason kept the required 'THIS EXCLUSION WILL NEED REVISITING in Phase 126' caveat verbatim, on one comment line so the checker's single-line EXCLUDED_LINE_RE/EXCLUDED_RE parse it as one reason segment (the checker's own fixture format, not a multi-line block)."
  - "PyYAML is absent from this devcontainer (ModuleNotFoundError on `import yaml`). Per the plan's own explicit fallback instruction, substituted a structural read of the on: block (python3 split on 'jobs:') to confirm all three arms -- push/pull_request/workflow_dispatch -- are present and unchanged apart from the new push arm. A gh workflow view confirmation is deferred to Plan 124-11's push, as instructed."
  - "'platform/py32f071' assertion in the inverted pytest was verified (not assumed) to appear on the real armed PASS line before being kept -- the PASS output does name the manifest's own path, so the assertion needed no weakening."

requirements-completed: [MERGE-02, MERGE-03]

coverage:
  - id: D1
    description: "platform/py32f071/CMakeLists.txt renamed to name flash_nor_unlock.cpp and flash_5v_page.cpp instead of the stale flash_type_3/4.cpp, verified against the real tree with ls before the edit"
    requirement: "MERGE-02"
    verification:
      - kind: unit
        ref: "ls src/proms/flash_nor_unlock.cpp src/proms/flash_5v_page.cpp -- both present before the edit; grep -c 'flash_type_3\\|flash_type_4' platform/py32f071/CMakeLists.txt -- 0 after"
        status: pass
    human_judgment: false
  - id: D2
    description: "check_cmake_manifest.py driven from a recorded starting state of 9 violations to 0 (PASS), via D-15's five reasoned PY32_EXCLUDED entries plus the rename"
    requirement: "MERGE-02"
    verification:
      - kind: unit
        ref: "python3 scripts/check_cmake_manifest.py -- pre-edit: FAIL: 9 violation(s); post-edit: PASS: 23 enforced source(s) resolved, 14 PY32_SDK_SOURCES exempt, 5 allow-listed omissions named -- exit 0"
        status: pass
    human_judgment: false
  - id: D3
    description: "py32f071.yml carries push: branches: [beta] with no paths filter, added alongside the unchanged pull_request/workflow_dispatch arms"
    requirement: "MERGE-03"
    verification:
      - kind: unit
        ref: "structural read of the on: block (python3 split on 'jobs:') -- three arms present: push:branches:[beta], pull_request (paths unchanged), workflow_dispatch; git diff --name-only HEAD lists only .github/workflows/py32f071.yml"
        status: pass
    human_judgment: false
  - id: D4
    description: "tests/test_check_cmake_manifest.py's expiring UNARMED-on-the-real-tree test inverted to test_armed_and_passing_on_the_real_tree, asserting PASS: + platform/py32f071 named; test_unarmed_on_clean_unarmed_tree_fixture left byte-identical"
    verification:
      - kind: unit
        ref: "python3 -m pytest tests/test_check_cmake_manifest.py -q -- 8 passed; python3 -m pytest tests/ -q -- 1 failed (test_check_orphan_provisional.py, owned by 124-08), 65 passed"
        status: pass
    human_judgment: false
  - id: D5
    description: "AVR flash/RAM unchanged vs 124-04's recorded landing figures after this plan's three commits"
    verification:
      - kind: unit
        ref: "check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json --rebuild -- PASS: uno(flash=23954/32256[+22<=64],ram=1573/2048[=]), uno328pb(flash=24004/32384[+28<=64],ram=1579/2048[=]), leonardo(flash=26016/28672[-56<=0],ram=2014/2560[=]), native(cases=141,suites=17), native_nodevtools(cases=141,suites=17) -- exact match to 124-04"
        status: pass
    human_judgment: false

duration: ~25min
completed: 2026-07-31
status: complete
---

# Phase 124 Plan 05: CMake Manifest Repair + MERGE-03 Push Trigger Summary

**Repaired the flash_type_3/4.cpp -> flash_nor_unlock/flash_5v_page.cpp rename defect in `platform/py32f071/CMakeLists.txt`, wrote D-15's five reasoned `PY32_EXCLUDED` allow-list entries to drive `check_cmake_manifest.py` from 9 violations to 0, added `py32f071.yml`'s `push: branches: [beta]` trigger, and inverted the expiring Phase-123 pytest to pin the armed/passing state.**

## Performance

- **Duration:** ~25 min
- **Tasks:** 3 completed
- **Files modified:** 3

## Accomplishments

- **Task 1:** Recorded the pre-edit armed gate at exactly **9 violations** (matching RESEARCH's W-4 finding, not 123-NONREGRESSION's predicted 2). Confirmed via `ls` that `src/proms/flash_nor_unlock.cpp` and `src/proms/flash_5v_page.cpp` exist in the tree before touching the manifest. Edited `FIRESTARTER_COMMON_SOURCES` lines 40-41 to name the real files, and added a five-line `PY32_EXCLUDED` comment block (with D-15's amended `src/dev_tools.cpp` reason describing D-02's uniform value-semantics mechanism) immediately above the `set(FIRESTARTER_COMMON_SOURCES` block. Added a commented ARM `DEV_TOOLS`-off decision record inside `target_compile_definitions`. Re-ran the gate: `PASS: ... 23 enforced source(s) resolved ... 14 PY32_SDK_SOURCES entries structurally exempt ... allow-listed omission(s): src/boards/leonardo_rurp_shield.cpp, src/boards/rurp_common.cpp, src/boards/uno_rurp_shield.cpp, src/dev_tools.cpp, src/rurp_config_utils.cpp` — exit 0.
- **Task 2:** Added a `push: branches: [beta]` trigger to `py32f071.yml`'s `on:` block, with a one-line comment recording D-10 (Phase 128's later double-ARM-build consequence is deliberately not pre-solved here). No `paths:` filter on the push arm, per the plan's explicit instruction — the whole point is catching a rename anywhere on a `beta` push, since the existing `pull_request` arm's `paths:` filter is what let the original rename defect through invisibly. `beta-build.yml` and `build.yml` confirmed untouched; re-read all three workflows' `on:` blocks and confirmed `v1.23-py32f071-integration` matches no `push:` branch filter in any of them (only `beta` and `main` are named).
- **Task 3:** Renamed `test_unarmed_on_the_real_tree_with_no_seam_override` to `test_armed_and_passing_on_the_real_tree` in `tests/test_check_cmake_manifest.py`, inverting its assertions to `PASS:` + `platform/py32f071` named (verified against real output before keeping the naming assertion, per the plan's caution) and rewriting the docstring plus the module's Coverage item 1. `test_unarmed_on_clean_unarmed_tree_fixture` left untouched. Full suite: **1 failed, 65 passed** — the sole remaining red is `tests/test_check_orphan_provisional.py::test_unarmed_on_the_real_tree_with_no_seam_override`, owned by Plan 124-08 and confirmed still red.

## Observed Verification Values

- **Pre-edit gate (Task 1):** `FAIL: 9 violation(s) in .../CMakeLists.txt` naming both `flash_type_3.cpp`/`flash_type_4.cpp` (unresolved paths) plus `src/boards/leonardo_rurp_shield.cpp`, `src/boards/rurp_common.cpp`, `src/boards/uno_rurp_shield.cpp`, `src/dev_tools.cpp`, `src/proms/flash_5v_page.cpp`, `src/proms/flash_nor_unlock.cpp`, `src/rurp_config_utils.cpp` (present-but-uncovered). Exit 1. **Count matches RESEARCH's 9, not 123-NONREGRESSION's predicted 2 (W-4).**
- **`ls` pre-edit:** `src/proms/flash_5v_page.cpp` and `src/proms/flash_nor_unlock.cpp` both resolved successfully (both listed, no error).
- **Post-edit gate:** `PASS: /workspaces/firestarter/platform/py32f071/CMakeLists.txt -- 23 enforced source(s) resolved across ['FIRESTARTER_COMMON_SOURCES', 'PY32_PLATFORM_SOURCES']; 14 PY32_SDK_SOURCES entries structurally exempt (FetchContent -- PY32_SDK_ROOT resolves only after a networked cmake configure); allow-listed omission(s): src/boards/leonardo_rurp_shield.cpp, src/boards/rurp_common.cpp, src/boards/uno_rurp_shield.cpp, src/dev_tools.cpp, src/rurp_config_utils.cpp`. Exit 0.
- **Rename verification:** `grep -c 'flash_type_3\|flash_type_4'` → 0; `grep -c 'flash_nor_unlock.cpp'` → 1; `grep -c 'flash_5v_page.cpp'` → 1.
- **Allow-list verification:** `grep -c 'PY32_EXCLUDED:'` → 5.
- **DEV_TOOLS verification:** `grep -n 'DEV_TOOLS'` → 3 hits (the `src/dev_tools.cpp` exclusion reason, plus the two-line `target_compile_definitions` decision comment); none is a `-D DEV_TOOLS` or `DEV_TOOLS=` define — confirmed by reading each hit.
- **`DATA_BUFFER_SIZE=512`:** still resolves at line 116 (shifted from the landing's line 107 by the 9 inserted comment/blank lines above it) — untouched by this plan, a Phase 127/128 concern per the deferred list.
- **`py32f071.yml` `on:` block (emitted verbatim):**
  ```yaml
  on:
    # MERGE-03/D-10: implemented literally as specified -- push: branches: [beta]
    # with no paths filter, so any change anywhere that breaks the ARM configure
    # is caught on beta. Phase 128 will later fold the ARM build into
    # beta-build.yml, creating a double-ARM-build question on a beta push; that
    # is recorded for Phase 128 to resolve, not pre-solved here.
    push:
      branches: [beta]
    pull_request:
      paths:
        - "platform/py32f071/**"
        - "include/**"
        - "src/**"
        - "lib/jsmn/**"
        - ".github/workflows/py32f071.yml"
    workflow_dispatch:
  ```
- **YAML parse:** `python3 -c "import yaml..."` → `ModuleNotFoundError: No module named 'yaml'` (PyYAML absent from this devcontainer). Per the plan's own fallback instruction, substituted the structural read above (three arms present, `pull_request`'s `paths:` list unchanged, `workflow_dispatch:` intact) plus `git diff --name-only HEAD` confirming only `py32f071.yml` changed. A `gh workflow view` confirmation is deferred to Plan 124-11's push.
- **Branch-vs-trigger re-confirmation:** `beta-build.yml` → `push: branches: [beta]`; `build.yml` → `push: branches: [main]`; `py32f071.yml` → `push: branches: [beta]` (new). Current branch `v1.23-py32f071-integration` matches none of the three.
- **Task 3 module test:** `python3 -m pytest tests/test_check_cmake_manifest.py -q` → **8 passed**.
- **`test_armed_and_passing_on_the_real_tree` grep count:** 2 (the `def` plus the Coverage list item 1 reference).
- **`git diff HEAD -- tests/test_check_cmake_manifest.py`:** touches exactly the Coverage item 1 docstring text and the single renamed/inverted test function — confirmed by reading the hunks (quoted in the diff below).
- **Full suite (Task 3 + final):** `python3 -m pytest tests/ -q` → **1 failed, 65 passed** — `tests/test_check_orphan_provisional.py::test_unarmed_on_the_real_tree_with_no_seam_override` is the sole failure, owned by Plan 124-08.
- **AVR/native re-measurement (post all three commits):** `check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json --rebuild` → `PASS: uno(flash=23954/32256[+22<=64],ram=1573/2048[=]), uno328pb(flash=24004/32384[+28<=64],ram=1579/2048[=]), leonardo(flash=26016/28672[-56<=0],ram=2014/2560[=]), native(cases=141,suites=17), native_nodevtools(cases=141,suites=17)` — exit 0. **Every figure matches 124-04's recorded landing figures exactly; this plan moved zero bytes of flash/RAM.**
- **`git status --porcelain` (firestarter submodule, end of plan):** empty.

**Diff (Task 3, `tests/test_check_cmake_manifest.py`):**
```diff
 Coverage:
-  1. UNARMED on the real tree (no seam override) -- the state of `beta`
-     today, must stay true until Phase 124 lands platform/py32f071/.
+  1. test_armed_and_passing_on_the_real_tree -- no seam override: Phase 124
+     landed platform/py32f071/ and repaired the flash_type_3/4.cpp rename
+     damage (124-05), so this pins the ARMED, PASSING state going forward.
+     A regression to the UNARMED line here would mean platform/py32f071/
+     had disappeared and must fail this test.
   2. UNARMED on clean_unarmed_tree/ through the seam -- proves the arming
      decision follows the supplied root, not the process cwd.
   3. Mismatched path fails with exactly one violation -- the SDK-exempt
      entries must never be counted (123-RESEARCH.md Pitfall 6).

-def test_unarmed_on_the_real_tree_with_no_seam_override():
-    """Coverage 1 -- ... the gate must exit 0 and print UNARMED:, naming
-    platform/py32f071. This must stay true until Phase 124 lands the port."""
+def test_armed_and_passing_on_the_real_tree():
+    """Coverage 1 -- ... the gate is now ARMED and must exit 0 with a PASS:
+    line naming platform/py32f071. ... a regression back to UNARMED here
+    would mean platform/py32f071/ had disappeared from the tree entirely."""
     result = _run_checker(manifest_root=None)
     assert result.returncode == 0, (...)
-    assert result.stdout.startswith("UNARMED:"), (...)
+    assert "PASS:" in result.stdout, (...)
     assert "platform/py32f071" in result.stdout, (...)
```

## Task Commits

Each task committed atomically, inside the `firestarter` submodule on branch `v1.23-py32f071-integration`.

1. **Task 1: Record the 9 armed violations, fix the rename, and write D-15's PY32_EXCLUDED allow-list** - `dae7d23` (fix)
2. **Task 2: Add MERGE-03's push trigger to py32f071.yml** - `e1aaef0` (feat)
3. **Task 3: Invert the expiring Phase-123 CMake-manifest pytest** - `dbbd1da` (test)

## Files Created/Modified

- `firestarter/platform/py32f071/CMakeLists.txt` - renamed the two rename-damaged FIRESTARTER_COMMON_SOURCES entries; added D-15's five-line PY32_EXCLUDED allow-list block; added a commented ARM DEV_TOOLS-off decision record
- `firestarter/.github/workflows/py32f071.yml` - added `push: branches: [beta]` (MERGE-03), pull_request/workflow_dispatch unchanged
- `firestarter/tests/test_check_cmake_manifest.py` - inverted the expiring UNARMED test to `test_armed_and_passing_on_the_real_tree`, updated Coverage item 1

## Decisions Made

- **D-15's `src/dev_tools.cpp` reason written already amended.** The checker docstring's prescribed text ("DEV_TOOLS deliberately off on ARM (MERGE-08)") was replaced with D-15's required amendment describing D-02's uniform value-semantics mechanism verbatim ("no ARM dev-tools TU; DEV_TOOLS resolves to 0 by the shared default (MERGE-08, D-02)"). Plan 124-06 lands the actual shared `#ifndef DEV_TOOLS` default in the same wave — this reason describes end-of-wave state, which is intentional per the plan's own instruction, not a claim that this plan's commit alone makes it true.
- **PyYAML absence handled per the plan's explicit fallback, not silently skipped.** `import yaml` fails in this devcontainer; substituted the prescribed structural read (`python3` split on `jobs:`) plus a `git diff --name-only` scope check, and deferred the `gh workflow view` confirmation to Plan 124-11's push, exactly as the plan's acceptance criteria specify.
- **The `platform/py32f071` naming assertion in the inverted pytest was kept, not dropped**, because running the real armed gate first showed the PASS line genuinely names the manifest path (`PASS: /workspaces/firestarter/platform/py32f071/CMakeLists.txt -- ...`) — verified before committing to keeping the assertion, per the plan's caution against weakening the PASS assertion to accommodate a naming claim that turned out to hold anyway.

## Deviations from Plan

None — plan executed exactly as written. All three tasks' acceptance criteria were met on the first attempt; no auto-fixes, no architectural questions, no checkpoints.

## Issues Encountered

- **PyYAML unavailable in this devcontainer** — not a defect, an environment absence the plan itself anticipated with an explicit fallback instruction (see Decisions above). No workaround package was installed (no package-manager install was needed or attempted).

## User Setup Required

None - no external service configuration required.

## Requirement Ticking Scope

Per this plan's dispatch instructions, `.planning/REQUIREMENTS.md` was **not** touched by this plan. What was proved: MERGE-02's textual half (the rename + the drift-gate green from a recorded 9-violation starting state) and MERGE-03 in full (the `push: branches: [beta]` trigger, verified by reading the file). Plan 124-12 owns citing this evidence when it ticks MERGE-02/MERGE-03.

## Next Phase Readiness

- `check_cmake_manifest.py` is green (0 violations) on the real tree, from a recorded starting state of 9 — W-4 closed.
- `py32f071.yml` carries `push: branches: [beta]` — MERGE-03 closed, verified by reading the file, and the milestone branch confirmed to match no push filter in any of the three workflows (safety argument for Plan 124-11's push, C-14).
- W-3's CMake half is closed: `test_armed_and_passing_on_the_real_tree` passes; `test_check_orphan_provisional.py`'s twin remains red, owned by Plan 124-08 (confirmed still red, not accidentally repaired).
- AVR flash/RAM figures unchanged vs 124-04's landing measurements (uno 23954/1573, uno328pb 24004/1579, leonardo 26016/2014) — this plan moved zero bytes.
- No blockers for 124-06 onward. Plan 124-06 lands D-02's shared `DEV_TOOLS` value-semantics conversion next, which is what makes this plan's amended `src/dev_tools.cpp` PY32_EXCLUDED reason fully true (it is currently true of the manifest's own comment, and becomes true of the actual mechanism once 124-06 lands).

## Self-Check: PASSED

- FOUND: `firestarter/platform/py32f071/CMakeLists.txt` (modified, 5 PY32_EXCLUDED entries confirmed via grep)
- FOUND: `firestarter/.github/workflows/py32f071.yml` (modified, push trigger confirmed via structural read)
- FOUND: `firestarter/tests/test_check_cmake_manifest.py` (modified, inverted test confirmed via pytest run)
- FOUND commit `dae7d23` (firestarter submodule) — `git log --oneline --all | grep dae7d23` matches
- FOUND commit `e1aaef0` (firestarter submodule) — `git log --oneline --all | grep e1aaef0` matches
- FOUND commit `dbbd1da` (firestarter submodule) — `git log --oneline --all | grep dbbd1da` matches

## Self-Check: PASSED (re-verified after commit)

- FOUND: `.planning/phases/124-firmware-integration-merge/124-05-SUMMARY.md`
- FOUND: `firestarter/platform/py32f071/CMakeLists.txt`
- FOUND: `firestarter/.github/workflows/py32f071.yml`
- FOUND: `firestarter/tests/test_check_cmake_manifest.py`
- FOUND commit `dae7d23`, `e1aaef0`, `dbbd1da` (all present in `git log --oneline --all`)

---
*Phase: 124-firmware-integration-merge*
*Completed: 2026-07-31*
