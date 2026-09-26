---
phase: 124-firmware-integration-merge
plan: "08"
subsystem: firmware-safety
tags: [firestarter, provisional-pinmap, refusal-guard, pio, native-test, py32f071]

# Dependency graph
requires:
  - phase: 124-firmware-integration-merge
    plan: "04"
    provides: "The landed tree (e2c422d) and its recorded post-landing AVR flash/RAM figures (uno 23954/1573, uno328pb 24004/1579, leonardo 26016/2014) this plan's guard is measured zero-cost against; also the armed-but-red check_orphan_provisional.py (1 violation) and its expiring UNARMED pytest this plan closes."
  - phase: 124-firmware-integration-merge
    plan: "06"
    provides: "The DEV_TOOLS value-semantics conversion, confirming the #ifndef/#define/#endif shared-default idiom this plan's RURP_PINMAP_PROVISIONAL default reuses at rurp_pinmap_guard.h."
provides:
  - "A platform-neutral RURP_PINMAP_PROVISIONAL flag (default 0) with a static inline rurp_pinmap_refuses() predicate that delegates to is_memory_cmd(), so the refused set can never drift from the admitted set (D-12)"
  - "The refusal wired into configure_memory() (src/proms/memory.cpp), refusing all eight is_memory_cmd() commands with MSG_ERR_NOT_SUPPORTED + the command ordinal when the flag is armed, and compiling to nothing (zero AVR cost, measured) when it is not"
  - "A third native environment ([env:native_pinmap_provisional]) that compiles the real production path with the flag set, proving the refusal at a site pio test -e native can actually reach (C-4's chokepoint), without perturbing either pinned env's 141/17 count"
  - "check_orphan_provisional.py driven to PASS (both provisional macros now have real consumers) and its paired Phase-123 expiring pytest inverted to pin the armed, passing state -- W-3 fully closed, firestarter/tests/ now 0 failed"
affects: [124-10, 124-12, 124-close]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "A second, orthogonal preprocessor-conditional gate sited in a SEPARATE header (rurp_pinmap_guard.h) rather than widening is_memory_cmd() itself -- check_is_memory_cmd_no_ifdef.py forbids any conditional inside that predicate's body, so the provisional-pinmap test has to live beside it, delegating to it instead of re-testing membership by hand"
    - "A third PlatformIO native env as the only shape that lets a test exercise a build-flag-gated production path without perturbing two envs pinned at an exact case/suite count (Pitfall 5) -- build_flags are environment-scoped and build_src_filter compiles a shared .cpp once per env, so a #define at the top of one test file cannot retroactively change how the shared object was already compiled for a different env"
    - "pio test's own harness mis-reports a test binary's ordinary nonzero exit code (== failure count, Unity's convention) as SIGFPE/[ERRORED] -- confirmed identical to the test_eeprom28c_sdp RED-BASELINE.md precedent; the authoritative RED capture is the built Unity binary run directly (no pio wrapper), which exited cleanly with code 8 and no crash"

key-files:
  created:
    - firestarter/include/rurp_pinmap_guard.h
    - firestarter/test/native/avr/test_pinmap_provisional/test_pinmap_provisional.cpp
    - firestarter/test/native/avr/test_pinmap_provisional/host_stubs.cpp
    - firestarter/test/native/avr/test_pinmap_provisional/avr/pgmspace.h
  modified:
    - firestarter/include/boards/py32f071_rurp_shield.h
    - firestarter/src/proms/memory.cpp
    - firestarter/platformio.ini
    - firestarter/tests/test_check_orphan_provisional.py

key-decisions:
  - "Refusal placed at configure_memory() (src/proms/memory.cpp), not at is_memory_cmd()'s call site in src/firestarter.cpp, per correction C-4: [env:native]'s build_src_filter (+<proms/> +<boards/rurp_serial_utils.cpp> +<json_parser.c> +<operation_utils.cpp>) never compiles src/firestarter.cpp into the native test binary, so a refusal at the admission call site would be structurally unprovable by the very native test MERGE-04 demands."
  - "The refusal predicate (rurp_pinmap_refuses) delegates to is_memory_cmd() rather than re-listing the eight commands (D-12) -- verified by grep that no CMD_* macro appears in rurp_pinmap_guard.h outside comment prose, so the refused set structurally cannot drift from the admitted set."
  - "A THIRD native env ([env:native_pinmap_provisional]), not a header-seam #define trick alone, was used to prove the production path -- PlatformIO build_flags are environment-scoped and src/proms/memory.cpp is compiled once per env, so only a dedicated env with RURP_PINMAP_PROVISIONAL=1 in its build_flags can compile the real configure_memory() with the flag armed. Not added to default_envs (no main()); not fed to check_build_warnings.py (unknown env name would exit 2 there until Plan 124-10 adds it)."
  - "MSG_ERR_NOT_SUPPORTED (0xA5) reused for the refusal report, carrying handle->cmd (not handle->protocol) as its u8 payload (D-13) -- a dedicated message id would cost a meta-repo messages.toml edit, a codegen regen, and host constants-parity churn. include/messages.h is untouched (git status --porcelain confirms empty). The dedicated-id option remains recorded in 124-CONTEXT.md's deferred-ideas list."
  - "The board-header bridging block does double duty (D-11/C-12): the '#if RURP_PY32F071_PINMAP_PROVISIONAL' test makes that py32-specific macro a real consumer (discharging check_orphan_provisional.py for it), while the block it guards defines the neutral RURP_PINMAP_PROVISIONAL flag for that board -- both provisional macros now have real, non-comment consumers inside include/ (tests/ is not scanned, per C-12), so the gate PASSes."
  - "The three stale platformio.ini comments claiming [env:native_nodevtools]'s allowlist has 16 entries (it has 17) were folded in as the deferred idea CONTEXT licensed 'only if a plan arises' -- this plan touches platformio.ini anyway to add the third env, so the fold-in is explicitly marked in the commit message as deferred work, not new scope."
  - "The inverted pytest drops both of its predecessor's substring assertions ('platform/py32f071' and the literal phase number '124') rather than keeping either as a weakened check -- re-verified against the real armed PASS: line, which names neither a directory path nor a phase number, only macros and consumer counts. Weakening an assertion just to preserve an unrelated substring match would be backwards."

requirements-completed: []
# Per this plan's dispatch <requirement_ticking_scope>: REQUIREMENTS.md is
# untouched. Plan 124-12 is the sole owner of every MERGE-01..MERGE-08 tick.
# What is proved here: MERGE-04's refusal half, reusing D-12's set and
# D-13's message id, at the C-4-corrected chokepoint, plus W-3's second
# expiring-pytest closure.

coverage:
  - id: D1
    description: "Both RURP_PY32F071_PINMAP_PROVISIONAL and the new platform-neutral RURP_PINMAP_PROVISIONAL flag have real, non-comment consumers inside include/ (the only scanned directories touched); check_orphan_provisional.py flips from FAIL: 1 violation(s) to PASS, naming both macros with non-zero consumer counts"
    requirement: "MERGE-04"
    verification:
      - kind: unit
        ref: "python3 scripts/check_orphan_provisional.py -- BEFORE: FAIL: 1 violation(s): RURP_PY32F071_PINMAP_PROVISIONAL: zero consumers (recorded in 124-04-SUMMARY.md). AFTER: PASS: RURP_PINMAP_PROVISIONAL (3 consumer(s)), RURP_PY32F071_PINMAP_PROVISIONAL (1 consumer(s)) -- exit 0"
        status: pass
      - kind: unit
        ref: "grep -c 'is_memory_cmd' include/rurp_pinmap_guard.h == 12 (>=1 required); grep for the eight CMD_* macro names in that file returns 3 hits, all read and confirmed comment prose (no re-listing in the predicate body)"
        status: pass
    human_judgment: false
  - id: D2
    description: "All eight is_memory_cmd() commands (D-12's exact set) are refused by configure_memory() when RURP_PINMAP_PROVISIONAL=1, proven RED-before-GREEN by a native test that actually compiles the production configure_memory() with the flag set (not merely the header-seam predicate) -- the reachable chokepoint C-4 identifies, since src/firestarter.cpp is never compiled by [env:native]"
    requirement: "MERGE-04"
    verification:
      - kind: unit
        ref: "RED baseline (direct Unity binary run, authoritative per the test_eeprom28c_sdp SIGFPE-harness-mis-report precedent -- pio test's own wrapper reported [ERRORED]/SIGFPE for this ordinary nonzero exit, matching that precedent exactly): 10 Tests 8 Failures 0 Ignored, exit code 8. The 8 per-command refusal cases FAILED (Expected 0 Was 1 -- response_code was OK, not ERROR); the 2 negative-control cases (predicate truth table, identity command not refused) already PASSED before the guard was wired, because they do not depend on configure_memory consulting anything yet."
        status: pass
      - kind: unit
        ref: "GREEN run (pio test -e native_pinmap_provisional, after wiring): 10 test cases: 10 succeeded -- all 8 per-command cases flipped, both negative controls stayed green"
        status: pass
    human_judgment: false
  - id: D3
    description: "The new suite lives in a dedicated THIRD native environment, never folded into either pinned env's test_filter; both [env:native] and [env:native_nodevtools] still report exactly 141 cases / 17 suites, all PASSED, after every platformio.ini and memory.cpp edit in this plan"
    requirement: "MERGE-06 (unregressed)"
    verification:
      - kind: unit
        ref: "grep -c 'native/avr/test_pinmap_provisional' platformio.ini == 2 (the new env's test_filter entry + its -I flag) -- proving the suite was never added to either pinned env's allowlist"
        status: pass
      - kind: unit
        ref: "pio test -e native -- 141 test cases: 141 succeeded (re-run after the platformio.ini edit AND after the memory.cpp edit, not deferred)"
        status: pass
      - kind: unit
        ref: "pio test -e native_nodevtools -- 141 test cases: 141 succeeded (re-run after both edits)"
        status: pass
    human_judgment: false
  - id: D4
    description: "AVR flash/RAM are unchanged by the refusal on all three targets, because the guard compiles to nothing where RURP_PINMAP_PROVISIONAL resolves to its default of 0 (every AVR env)"
    requirement: "MERGE-04 / MERGE-05 (unregressed)"
    verification:
      - kind: unit
        ref: "Clean rebuilds, compared side-by-side with Plan 124-06's recorded post-conversion figures: uno flash 23954/RAM 1573 (unchanged), uno328pb flash 24004/RAM 1579 (unchanged), leonardo flash 26016/RAM 2014 (unchanged). All six pairs byte-identical."
        status: pass
    human_judgment: false
  - id: D5
    description: "The refusal reuses MSG_ERR_NOT_SUPPORTED (0xA5) carrying the command ordinal -- no new message id, include/messages.h untouched, check_is_memory_cmd_no_ifdef.py still exits 0 (is_memory_cmd itself unmodified, still conditional-free, still exactly eight commands)"
    requirement: "MERGE-04 (D-13)"
    verification:
      - kind: unit
        ref: "grep -c 'MSG_ERR' src/proms/memory.cpp == 5 (>=1 required); read and confirmed the hit is the existing MSG_ERR_NOT_SUPPORTED id carrying handle->cmd; git status --porcelain include/messages.h -- empty (untouched)"
        status: pass
      - kind: unit
        ref: "cd /workspaces/firestarter_app && python3 tools/check_is_memory_cmd_no_ifdef.py -- PASS: is_memory_cmd() has no preprocessor conditional and enumerates exactly the eight expected commands (predicate body lines 133-147, unchanged) -- exit 0"
        status: pass
    human_judgment: false
  - id: D6
    description: "W-3's second half closes: the Phase-123 expiring pytest asserting UNARMED: on the real tree is renamed and inverted to pin the now-armed-and-passing state, naming both provisional macros (the substantive new thing proved) rather than a directory path or phase number (neither of which the armed PASS: line prints); firestarter/tests/ is fully green for the first time since the landing"
    requirement: "W-3 (owned by this plan, per 124-04-SUMMARY.md and 124-06-SUMMARY.md hand-off)"
    verification:
      - kind: unit
        ref: "python3 -m pytest tests/ -q -- BEFORE this plan's Task 3(c): 1 failed, 65 passed (test_check_orphan_provisional.py::test_unarmed_on_the_real_tree_with_no_seam_override). AFTER: 66 passed, 0 failed -- new total supersedes 123-NONREGRESSION.md row F1's recorded 48, and 124-04-SUMMARY.md's recorded 64/2-failed post-landing figure."
        status: pass
      - kind: unit
        ref: "grep -c '\"124\"' tests/test_check_orphan_provisional.py == 0 -- the inverted test does not assert the phase number, matching the real armed PASS: line's actual content"
        status: pass
    human_judgment: false

duration: ~55min
completed: 2026-07-31
status: complete
---

# Phase 124 Plan 08: Provisional Pin-Map Refusal (MERGE-04) Summary

**Made the provisional PY32F071 pin map unable to energise a PROM by refusing all eight `is_memory_cmd()` commands inside `configure_memory()` -- the reachable chokepoint correction C-4 identifies, since `src/firestarter.cpp` (home of `is_memory_cmd()`'s only caller) is never compiled by `pio test -e native`. Proved it RED-before-GREEN in a dedicated third native environment that compiles the real production path with the flag armed, without perturbing either pinned env's 141/17 count, and closed W-3's second expiring pytest in the same commit that turned `check_orphan_provisional.py` green.**

## Performance

- **Duration:** ~55 min
- **Started:** 2026-07-31T09:36:43Z (approx, hand-off from Plan 06 per STATE.md `last_updated`)
- **Completed:** 2026-07-31T10:07:35Z
- **Tasks:** 3 completed
- **Files modified:** 8 (2 created, 2 modified in Task 1; 1 modified + 3 created in Task 2; 2 modified in Task 3)

## Accomplishments

- **Task 1:** Created `include/rurp_pinmap_guard.h` -- a platform-neutral `RURP_PINMAP_PROVISIONAL` default (0, `#ifndef`-wrapped) plus `rurp_pinmap_refuses(uint8_t cmd)`, a `static inline` predicate that delegates to `is_memory_cmd()` under `#if RURP_PINMAP_PROVISIONAL` so the refused set can never drift from the admitted set (D-12), and can never be re-implemented with a conditional inside `is_memory_cmd()` itself (`check_is_memory_cmd_no_ifdef.py` forbids that). Added a bridging block to `include/boards/py32f071_rurp_shield.h` immediately after `RURP_PY32F071_PINMAP_PROVISIONAL`'s definition: the `#if` test makes that macro a real consumer, and the block it guards defines the neutral flag for this board. `check_orphan_provisional.py` flipped from `FAIL: 1 violation(s)` to `PASS:` naming both macros.
- **Task 2:** Added `[env:native_pinmap_provisional]` to `platformio.ini` -- mirrors `[env:native]`, appends `-D RURP_PINMAP_PROVISIONAL=1` and the new suite's `-I` flag, names only the new suite in `test_filter`, and is not in `default_envs`. Created `test/native/avr/test_pinmap_provisional/` (suite + `host_stubs.cpp` copied whole from `test_cmd_admission` + the per-suite `avr/pgmspace.h` shim). Ran the suite BEFORE wiring the guard: 8 per-command cases FAILED (RED, as required), 2 negative controls already PASSED. Folded in the deferred "16-entry" -> "17-entry" comment correction (three occurrences) since this plan touches `platformio.ini` anyway. Re-verified both pinned envs unaffected at 141/17.
- **Task 3:** Wired `rurp_pinmap_refuses(handle->cmd)` into `configure_memory()` (`src/proms/memory.cpp`), immediately after the three existing NULL operation-pointer assignments and before the `switch`, reusing `MSG_ERR_NOT_SUPPORTED` with `handle->cmd` as payload (D-13, no new message id). The suite flipped to 10/10 GREEN. Re-ran both native envs (141/17, unchanged) and all three AVR clean builds (byte-identical to Plan 124-06's figures). Inverted `test_unarmed_on_the_real_tree_with_no_seam_override` to `test_armed_and_passing_on_the_real_tree`, dropping the phase-number and directory-path assertions (neither appears on the real armed `PASS:` line) and adding assertions naming both provisional macros. `firestarter/tests/` is now 0 failed, 66 passed.

## Observed Verification Values

### Task 1 -- the guard header and the bridging block

- `python3 scripts/check_orphan_provisional.py`:
  - **Before this plan** (recorded in 124-04-SUMMARY.md): `FAIL: 1 violation(s): RURP_PY32F071_PINMAP_PROVISIONAL: zero consumers outside its own definition (include/boards/py32f071_rurp_shield.h:38)` -- exit 1.
  - **After Task 1**: `PASS: RURP_PINMAP_PROVISIONAL (3 consumer(s)), RURP_PY32F071_PINMAP_PROVISIONAL (1 consumer(s))` -- exit 0.
- `test -f include/rurp_pinmap_guard.h` -- succeeds.
- `grep -c 'is_memory_cmd' include/rurp_pinmap_guard.h` -> **12** (comment prose + the one real delegation call).
- `grep -n` for the eight `CMD_*` macro names in `rurp_pinmap_guard.h` -> 3 hits, all read and confirmed inside the file's opening comment block (lines 38-39, 51), none in the predicate body.
- Both the guard header's neutral-flag default and the board header's neutral-flag definition are wrapped in `#ifndef` -- quoted:
  ```c
  #ifndef RURP_PINMAP_PROVISIONAL
  #define RURP_PINMAP_PROVISIONAL 0
  #endif
  ```
  ```c
  #if RURP_PY32F071_PINMAP_PROVISIONAL
  #ifndef RURP_PINMAP_PROVISIONAL
  #define RURP_PINMAP_PROVISIONAL 1
  #endif
  #endif
  ```
- `git diff --name-only HEAD` (Task 1 commit) -> exactly `include/boards/py32f071_rurp_shield.h`, `include/rurp_pinmap_guard.h`.

### Task 2 -- the third env and the RED baseline

- Chosen neutral macro name: **`RURP_PINMAP_PROVISIONAL`**. Guard-header filename: **`include/rurp_pinmap_guard.h`**.
- **RED baseline** (direct Unity binary run -- `.pio/build/native_pinmap_provisional/firestarter_native`, no `pio test` wrapper; see Deviations for why this is the authoritative capture):
  ```
  test_pinmap_provisional_refuses_cmd_read:      FAIL: Expected 0 Was 1.
  test_pinmap_provisional_refuses_cmd_write:     FAIL: Expected 0 Was 1.
  test_pinmap_provisional_refuses_cmd_erase:     FAIL: Expected 0 Was 1.
  test_pinmap_provisional_refuses_cmd_blank_check:    FAIL: Expected 0 Was 1.
  test_pinmap_provisional_refuses_cmd_check_chip_id:  FAIL: Expected 0 Was 1.
  test_pinmap_provisional_refuses_cmd_verify:    FAIL: Expected 0 Was 1.
  test_pinmap_provisional_refuses_cmd_sdp_unlock:     FAIL: Expected 0 Was 1.
  test_pinmap_provisional_refuses_cmd_sdp_lock:  FAIL: Expected 0 Was 1.
  test_pinmap_refuses_predicate_truth_table:                    PASS
  test_pinmap_provisional_does_not_refuse_identity_command:     PASS
  10 Tests 8 Failures 0 Ignored -- exit code 8
  ```
  The 8 per-command cases FAILED exactly as required (T-124-34: a suite green before the production change proves nothing). The 2 negative controls (predicate truth table; identity command not refused) were already PASSING at this point -- expected, since neither depends on `configure_memory()` consulting the guard: the predicate test calls `rurp_pinmap_refuses()` directly, and the identity-command test asserts non-refusal, which is trivially true before any refusal exists.
- `pio test -e native` -> **141 test cases: 141 succeeded** (17 suites). `pio test -e native_nodevtools` -> **141 test cases: 141 succeeded** (17 suites). Both re-run in this task.
- `grep -c 'native/avr/test_pinmap_provisional' platformio.ini` -> **2**.
- `grep -c '16-entry' platformio.ini` -> **0**; `grep -c '17-entry' platformio.ini` -> **3**.
- `ls test/native/avr/test_pinmap_provisional/` -> `test_pinmap_provisional.cpp`, `host_stubs.cpp`, `avr/`.
- Eight per-command test function names (verified via `grep -c '^void test_'` == 10 total, 8 of them command-named): `test_pinmap_provisional_refuses_cmd_read`, `_write`, `_erase`, `_blank_check`, `_check_chip_id`, `_verify`, `_sdp_unlock`, `_sdp_lock`.

### Task 3 -- wiring, rebuild, and the inverted pytest

- **GREEN run** (`pio test -e native_pinmap_provisional`, after wiring): `10 test cases: 10 succeeded` -- all 8 per-command cases and both negative controls PASSED.
- `pio test -e native` -> **141 test cases: 141 succeeded**. `pio test -e native_nodevtools` -> **141 test cases: 141 succeeded**. Both re-run after the `memory.cpp` edit.
- **AVR flash/RAM, six pairs side by side against Plan 124-06's recorded figures:**

  | Env | 124-06 recorded | This plan (post-guard) | Delta |
  |---|---|---|---|
  | uno flash | 23954 | 23954 | 0 |
  | uno RAM | 1573 | 1573 | 0 |
  | uno328pb flash | 24004 | 24004 | 0 |
  | uno328pb RAM | 1579 | 1579 | 0 |
  | leonardo flash | 26016 | 26016 | 0 |
  | leonardo RAM | 2014 | 2014 | 0 |

  **All six pairs byte-identical -- the guard's measured AVR cost is genuinely zero.**
- `grep -c 'MSG_ERR' src/proms/memory.cpp` -> **5** (the new refusal's `MSG_ERR_NOT_SUPPORTED` plus four pre-existing hits in the file's protocol-dispatch arms); read and confirmed the new hit carries `handle->cmd`. `git status --porcelain include/messages.h` -> empty (untouched).
- `python3 scripts/check_orphan_provisional.py` -> `PASS: RURP_PINMAP_PROVISIONAL (3 consumer(s)), RURP_PY32F071_PINMAP_PROVISIONAL (1 consumer(s))` -- exit 0.
- `cd /workspaces/firestarter_app && python3 tools/check_is_memory_cmd_no_ifdef.py` -> `PASS: ... predicate body lines 133-147` -- exit 0 (unchanged from Plan 124-06's recorded range; `is_memory_cmd` itself is untouched by this plan).
- `python3 -m pytest tests/ -q` (from `/workspaces/firestarter`) -> **66 passed, 0 failed** -- supersedes 124-04-SUMMARY.md's recorded post-landing `2 failed, 64 passed` and Plan 124-06's recorded `1 failed, 65 passed`; also supersedes `123-NONREGRESSION.md` row F1's recorded 48.
- `grep -c '"124"' tests/test_check_orphan_provisional.py` -> **0**.
- `git -C /workspaces/firestarter status --porcelain` -> empty after the Task 3 commit.

## Task Commits

Each code-producing task was committed atomically, inside the `firestarter` submodule (`/workspaces/firestarter`) on branch `v1.23-py32f071-integration`.

1. **Task 1: Platform-neutral flag, predicate, both macro consumers** - `bf3e5b9` (feat)
2. **Task 2: Third native env + RED refusal suite** - `9a8fac3` (test)
3. **Task 3: Wire the refusal + invert the expiring pytest** - `e49bab7` (fix)

_No plan-metadata commit is made inside the submodule -- the meta-repo's own SUMMARY.md commit (below) is this plan's final commit._

## Files Created/Modified

- `firestarter/include/rurp_pinmap_guard.h` (created) -- the platform-neutral `RURP_PINMAP_PROVISIONAL` default + `rurp_pinmap_refuses()` predicate delegating to `is_memory_cmd()`
- `firestarter/include/boards/py32f071_rurp_shield.h` (modified) -- bridging block: consumes the py32-specific flag, defines the neutral flag
- `firestarter/platformio.ini` (modified) -- new `[env:native_pinmap_provisional]`; three stale "16-entry" comments corrected to "17-entry" (deferred fold-in)
- `firestarter/test/native/avr/test_pinmap_provisional/test_pinmap_provisional.cpp` (created) -- 8 per-command refusal cases + 2 negative controls
- `firestarter/test/native/avr/test_pinmap_provisional/host_stubs.cpp` (created) -- pass-through host stub TU, copied from `test_cmd_admission`
- `firestarter/test/native/avr/test_pinmap_provisional/avr/pgmspace.h` (created) -- per-suite AVR `pgmspace.h` shim
- `firestarter/src/proms/memory.cpp` (modified) -- the refusal wired into `configure_memory()`
- `firestarter/tests/test_check_orphan_provisional.py` (modified) -- inverted expiring test, module docstring Coverage item 1 updated

## Decisions Made

See `key-decisions` in frontmatter for the full list. Highlights: placement at `configure_memory()` per C-4 (not the `is_memory_cmd()` call site, which `[env:native]`'s `build_src_filter` never compiles); delegation to `is_memory_cmd()` rather than re-listing the set (D-12); a dedicated third native env rather than a header-seam-only test, because `build_flags` are environment-scoped (Pitfall 5); `MSG_ERR_NOT_SUPPORTED` reuse with the command ordinal, not a new message id (D-13); the board-header bridging block doing double duty for both provisional macros' consumer requirements (C-12); the deferred "16-entry" comment fold-in explicitly marked as such, not new scope; and the inverted pytest dropping (not weakening) both of its predecessor's now-inapplicable substring assertions.

## Deviations from Plan

### Auto-fixed Issues

None -- the plan's own critical execution constraints (placement, D-12 delegation, D-13 message-id reuse, the third-env requirement, and the RED-before-GREEN discipline) were followed as specified; no bug, missing functionality, or blocking issue required an unplanned fix.

### Documented Findings (not auto-fixed -- measurement/tooling facts, not defects)

**1. `pio test -e native_pinmap_provisional`'s RED run was mis-reported by `pio test`'s own harness as `[ERRORED]`/`SIGFPE`, not as a clean 8-failure summary.** Running `pio test -e native_pinmap_provisional` directly printed all 10 test results correctly (8 FAILED, 2 PASSED) but then reported `Program received signal SIGFPE` and `[ERRORED]` instead of a normal failing summary. This is the *exact same* known quirk already documented in `test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md`'s "Post-suite-edit RED baseline" section: `pio test`'s wrapper mis-reports a Unity test binary that exits with a nonzero code (Unity's convention: exit code == failure count) as a crash, even though the binary itself terminates cleanly. Verified by running the built binary directly (`.pio/build/native_pinmap_provisional/firestarter_native`), with no `pio` wrapper: it printed the identical 10 results and exited with code **8** (no crash, no signal) -- the authoritative RED capture recorded above. Re-ran `pio test -e native_pinmap_provisional` after this investigation (still pre-guard) and reproduced the identical mis-report deterministically, confirming it is `pio test`'s harness behavior, not a flaky/nondeterministic crash in the test binary itself. Not a defect in this plan's code; not a new discovery either -- it is the same class of harness quirk `platformio.ini`'s own comments already document for `test_flash_intel_vpp`.

---

**Total deviations:** 0 auto-fixed; 1 documented tooling finding (pre-existing `pio test` harness mis-report of a nonzero-exit Unity binary, matching an already-documented precedent, resolved by citing the authoritative direct-binary-run capture instead).
**Impact on plan:** None on scope, correctness, or the discharged requirement coverage. The RED baseline was captured and recorded exactly as the plan requires (Task 2c); the GREEN run in Task 3 reported cleanly with no such mis-report, since a fully-passing Unity binary always exits 0.

## Issues Encountered

- The `pio test` harness mis-report documented above under Deviations. No other issues.

## User Setup Required

None -- no external service configuration required.

## Requirement Ticking Scope

Per this plan's dispatch `<requirement_ticking_scope>`, `.planning/REQUIREMENTS.md` was **not** touched. What was proved: MERGE-04's refusal half (all eight `is_memory_cmd()` commands refused at `configure_memory()`, RED-before-GREEN, zero AVR cost, both pinned native envs unregressed) and W-3's second closure (the `check_orphan_provisional.py` expiring pytest inverted; `firestarter/tests/` now fully green at 66 passed). Plan 124-12 owns citing this evidence when it ticks MERGE-04.

## Next Phase Readiness

- `firestarter/tests/` is now **0 failed, 66 passed** -- both Phase-123 expiring pytests (the CMake-manifest one in Plan 124-05, this orphan-provisional one here) are closed. This new total (66) supersedes `123-NONREGRESSION.md` row F1's recorded 48 and every intermediate figure recorded in 124-04/124-06's summaries.
- `check_orphan_provisional.py` and `check_cmake_manifest.py` (unregressed, re-checked) both PASS.
- AVR flash/RAM figures for the next plan's baseline are unchanged from 124-04/124-06: uno 23954/1573, uno328pb 24004/1579, leonardo 26016/2014.
- Both native envs remain pinned at exactly 141 cases / 17 suites; the new `[env:native_pinmap_provisional]` env is explicitly NOT in `default_envs` and NOT yet named to `check_build_warnings.py` -- Plan 124-10 (owner of the native warning-watermark work, W-2) must add it to that script's baseline `warnings` block before feeding it that env name.
- `include/messages.h` is untouched; `constants.py`/`firestarter.h` parity is unaffected (no new `CMD_*`/`FLAG_*`/`MSG_*` define was added).
- No blockers for 124-10 onward.

## Self-Check: PASSED

- FOUND: `firestarter/include/rurp_pinmap_guard.h`
- FOUND: `firestarter/test/native/avr/test_pinmap_provisional/test_pinmap_provisional.cpp`
- FOUND: `firestarter/test/native/avr/test_pinmap_provisional/host_stubs.cpp`
- FOUND: `firestarter/test/native/avr/test_pinmap_provisional/avr/pgmspace.h`
- FOUND commit `bf3e5b9` (firestarter submodule) -- `git log --oneline --all | grep bf3e5b9` matches
- FOUND commit `9a8fac3` (firestarter submodule) -- `git log --oneline --all | grep 9a8fac3` matches
- FOUND commit `e49bab7` (firestarter submodule) -- `git log --oneline --all | grep e49bab7` matches

---
*Phase: 124-firmware-integration-merge*
*Completed: 2026-07-31*
