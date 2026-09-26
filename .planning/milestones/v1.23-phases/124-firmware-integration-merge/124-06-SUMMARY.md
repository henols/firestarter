---
phase: 124-firmware-integration-merge
plan: "06"
subsystem: firmware-ci
tags: [firestarter, c-preprocessor, dev-tools, value-semantics, py32f071, pio, native-test, host-gate]

# Dependency graph
requires:
  - phase: 124-firmware-integration-merge
    plan: "04"
    provides: "The landed tree (e2c422d) and its recorded post-landing AVR flash/RAM + native case/suite figures this plan's conversion is measured against."
  - phase: 124-firmware-integration-merge
    plan: "05"
    provides: "check_cmake_manifest.py driven to 0 violations, including the amended src/dev_tools.cpp PY32_EXCLUDED reason that names D-02's shared-default mechanism as end-of-wave state."
provides:
  - "DEV_TOOLS converted from presence-semantics (#ifdef) to value-semantics (#if) at all six sites, plus one shared #ifndef DEV_TOOLS / #define DEV_TOOLS 0 default at placement B, so DEV_TOOLS=0 disables dev tools on every target instead of perversely enabling them on ARM (D-02, MERGE-08's third defect)"
  - "Measured zero AVR flash/RAM cost for the conversion across uno/uno328pb/leonardo, and unchanged 141/17 on both native envs, against Plan 124-04's recorded landing figures"
  - "Confirmation that the three host-repo gates scanning include/firestarter.h as source text (MERGE-07) still run and pass through this preprocessor restructure: check_is_memory_cmd_no_ifdef.py, test_revision_constants_parity.py, and the full host suite (1158 passed, 0 skipped)"
affects: [124-08, 124-10, 124-12, 124-close]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Placement B: a shared value-semantics default sited INSIDE the header guard beside an existing precedent (DATA_BUFFER_SIZE), not above the guard -- placement above the guard passes the host's _find_header_guard_line_indices parity test only by arithmetic cancellation between a spurious #endif decrement and an un-skipped #ifndef increment (C-18), a false green"
    - "Unanchored-substring count as the mechanical proof that only directive lines moved, not comment prose: grep -c '#ifdef DEV_TOOLS' (no line anchors) counts every literal occurrence, directive or comment; converting only the anchored '^#ifdef DEV_TOOLS$' lines to '#if DEV_TOOLS' necessarily drops the unanchored count by exactly the number of directives converted, while comment occurrences (which never match '^#ifdef DEV_TOOLS$' because they're prefixed by '//') survive untouched"

key-files:
  created: []
  modified:
    - firestarter/include/firestarter.h
    - firestarter/include/dev_tools.h
    - firestarter/src/dev_tools.cpp
    - firestarter/src/firestarter.cpp

key-decisions:
  - "Placement B (inside __FIRESTARTER_H__, beside DATA_BUFFER_SIZE) chosen per C-18's correction, not placement A (above the guard) -- verified the false-green mechanism is real by reading _find_header_guard_line_indices's behavior in the plan's read_first material rather than assuming C-18's claim."
  - "The two out-of-scope sites (include/dev_tools.h, src/dev_tools.cpp) were left without a local default, per correction C-7: they test DEV_TOOLS before including anything, so the shared default in firestarter.h is not syntactically reachable there. Documented as a caveat in the comment rather than papered over, because ISO C/C++ evaluates an undefined identifier in #if as 0 -- exactly the intended default -- so behavior is correct there without a load-bearing mechanism. Flagged for future -Wundef work."
  - "Task 2's mechanical substitution used per-line sed anchored to a specific recorded line number for each of the six directives (never a global token replace), so the five comment occurrences describing the historical presence-semantics mechanism (Phase 119 LOCK-02/LOCK-03 rationale) were structurally impossible to touch."

requirements-completed: []

# Per D-02's dispatch: REQUIREMENTS.md ticking is Plan 124-12's sole responsibility (see
# <requirement_ticking_scope> in dispatch prompt). This plan proves MERGE-08's third defect
# and re-confirms MERGE-07 but does not tick either ID.

coverage:
  - id: D1
    description: "One shared DEV_TOOLS value-semantics default (#ifndef DEV_TOOLS / #define DEV_TOOLS 0 / #endif) added inside the __FIRESTARTER_H__ guard, placement B (beside DATA_BUFFER_SIZE), with a comment recording the uniform-mechanism rationale, the placement-B rationale (C-18), and the two-sites-out-of-scope caveat (C-7)"
    requirement: "MERGE-08"
    verification:
      - kind: unit
        ref: "grep -cE '^#define DEV_TOOLS 0$' include/firestarter.h == 1; grep -cE '^#ifndef DEV_TOOLS$' include/firestarter.h == 1; git diff HEAD -- include/firestarter.h shows addition-only, no CMD_*/FLAG_* line touched"
        status: pass
    human_judgment: false
  - id: D2
    description: "Six #ifdef DEV_TOOLS directives converted to #if DEV_TOOLS via line-anchored substitution across include/firestarter.h, include/dev_tools.h, src/dev_tools.cpp, src/firestarter.cpp (3 sites); zero #ifdef DEV_TOOLS directives remain; the five historical-mechanism comment occurrences (4 in firestarter.h -> 3, 4 in firestarter.cpp -> 1) survive untouched; dev_tools.h's own __DEV_TOOLS_H__ include guard untouched; platformio.ini receives no edit"
    requirement: "MERGE-08"
    verification:
      - kind: unit
        ref: "grep -cE '^#if DEV_TOOLS$' across the four files sums to 6 (1+1+1+3); grep -cE '^#ifdef DEV_TOOLS$' sums to 0; unanchored 'grep -c #ifdef DEV_TOOLS' fell from 4->3 (firestarter.h) and 4->1 (firestarter.cpp), every surviving hit read and confirmed comment prose; grep -cE '^#ifndef __DEV_TOOLS_H__$' include/dev_tools.h == 1; git diff --name-only HEAD lists exactly the four files, platformio.ini absent"
        status: pass
    human_judgment: false
  - id: D3
    description: "AVR flash/RAM byte-identical to Plan 124-04's recorded post-landing figures on all three targets after the conversion (measured zero cost, not assumed); both native envs still report 141 cases / 17 suites, all PASSED; check_build_warnings.py PASS macro_redefinition=0 on all three AVR envs; check_cmake_manifest.py unregressed"
    requirement: "MERGE-08"
    verification:
      - kind: unit
        ref: "clean pio run -e {uno,uno328pb,leonardo}: uno 23954/1573, uno328pb 24004/1579, leonardo 26016/2014 -- all byte-identical to 124-04/124-05's recorded figures; cold pio test -e native and -e native_nodevtools: 141 cases/17 suites PASSED both; check_build_warnings.py --log (three AVR logs) PASS macro_redefinition=0 each; check_cmake_manifest.py PASS unchanged"
        status: pass
    human_judgment: false
  - id: D4
    description: "The three host-repo gates that scan include/firestarter.h as source text (MERGE-07) run and pass through this preprocessor restructure: check_is_memory_cmd_no_ifdef.py, test_revision_constants_parity.py, and the full host suite with -rs asserting zero SKIPPED"
    requirement: "MERGE-07"
    verification:
      - kind: unit
        ref: "check_is_memory_cmd_no_ifdef.py exits 0, 8 commands, no conditional, predicate body lines 133-147; pytest tests/test_revision_constants_parity.py -q -- 13 passed (matches Phase 123's recorded count); pytest tests/test_check_is_memory_cmd_no_ifdef.py -q -- 6 passed; pytest tests/ -q -rs -- 1158 passed, 0 failed, 0 skipped (matches Phase 123's recorded 1158); git -C firestarter_app status --porcelain unchanged from the plan's recorded pre-existing dirt list"
        status: pass
    human_judgment: false

duration: ~20min
completed: 2026-07-31
status: complete
---

# Phase 124 Plan 06: DEV_TOOLS Presence->Value Semantics Conversion Summary

**Converted the shared `DEV_TOOLS` build switch from presence-semantics (`#ifdef`) to value-semantics (`#if`) at all six sites plus one shared default, so `DEV_TOOLS=0` now disables dev tools uniformly on every target instead of perversely enabling them on ARM — measured zero AVR flash/RAM cost and reconfirmed all three host-repo gates that read the edited header as source text.**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-07-31T09:17:00Z (approx, hand-off from Plan 05 per STATE.md `last_updated`)
- **Completed:** 2026-07-31T09:36:43Z
- **Tasks:** 3 completed
- **Files modified:** 4 (firmware submodule only; Task 3 wrote nothing)

## Accomplishments

- **Task 1:** Added the single shared `#ifndef DEV_TOOLS / #define DEV_TOOLS 0 / #endif` default inside the `__FIRESTARTER_H__` guard, immediately beside the existing `DATA_BUFFER_SIZE` default (placement B, per correction C-18 — placement above the guard passes the host parity test's guard finder only by arithmetic cancellation, never for the right reason). The comment above the block records: (a) the uniform-mechanism rationale — same directive, same meaning, on AVR/native/native_nodevtools/ARM; (b) the placement-B rationale citing C-18's arithmetic-cancellation trap; (c) correction C-7's honest scope caveat — `include/dev_tools.h` and `src/dev_tools.cpp` test `DEV_TOOLS` before including anything, so this default is documentary (not load-bearing) there, ISO C/C++'s undefined-identifier-in-`#if`-is-0 rule already gives the correct behavior at those two sites, and a future `-Wundef` build would need the default pulled into a dependency-free header included unconditionally at their top.
- **Task 2:** Converted exactly six `#ifdef DEV_TOOLS` directive lines to `#if DEV_TOOLS` via per-line `sed` anchored to each site's recorded line number (never a global token substitution): `include/firestarter.h:66` (CMD_DEV_ADDRESS/CMD_DEV_REGISTER), `include/dev_tools.h:11` (whole-body guard), `src/dev_tools.cpp:8` (whole-file guard), `src/firestarter.cpp:21, 97, 271` (include guard, debug-log pair, dispatch arm). Verified the five comment occurrences describing the historical presence-semantics mechanism (Phase 119 LOCK-02/LOCK-03 rationale) survived untouched by reading each one and by the unanchored substring-count proof (see below). `dev_tools.h`'s own `__DEV_TOOLS_H__` include guard was left alone. No `platformio.ini` edit was made — confirmed `-D DEV_TOOLS` at line 26 already expands to `=1` by inspection, and `git diff --name-only HEAD` after the edit lists exactly the four target files, `platformio.ini` absent. Rebuilt all three AVR targets clean and both native envs cold, comparing against Plan 124-04's recorded post-landing figures.
- **Task 3:** Re-ran, from `/workspaces/firestarter_app`, the three host-repo gates that scan `include/firestarter.h` as source text (MERGE-07): `check_is_memory_cmd_no_ifdef.py`, `test_revision_constants_parity.py`, `test_check_is_memory_cmd_no_ifdef.py`, and the full host suite with `-rs`. All passed; the predicate's reported line range shifted (see Deviations) but the eight-command enumeration and the no-conditional invariant held. Confirmed the pre-existing `firestarter_app` working-tree dirt (modified `.gitignore`; untracked `.coverage`, `.planning/config.json`, `SECURITY.md`, `write_test_port.sh`) was unchanged by this plan — nothing was written into that repo.

## Observed Verification Values

### Task 1 — the shared default (placement B)

Quoted block, as landed at `include/firestarter.h:20-42` (between `DATA_BUFFER_SIZE`'s `#endif` at line 18 and `CMD_FRAME_MAX`'s comment at line 44):

```c
// D-02: the single shared value-semantics default for the DEV_TOOLS switch,
// so the same directive means the same thing on every target (AVR, native,
// native_nodevtools and ARM/py32f071) instead of one presence-semantics
// mechanism on AVR/native and a different by-omission mechanism on ARM,
// where DEV_TOOLS=0 would perversely ENABLE dev tools under the old
// #ifdef-based test. Placed INSIDE the __FIRESTARTER_H__ guard, beside
// DATA_BUFFER_SIZE above (the in-tree precedent for exactly this idiom) --
// placing it above the guard instead causes the host-repo parity test's
// _find_header_guard_line_indices to misidentify the real guard, and the
// test then passes only by an arithmetic cancellation between a spurious
// #endif decrement and an un-skipped #ifndef increment (correction C-18),
// never for the right reason. Honest scope caveat (correction C-7): two of
// the six conversion sites -- include/dev_tools.h and src/dev_tools.cpp --
// test DEV_TOOLS before including anything, so this default is not
// syntactically in scope there. Behaviour is still correct at those two
// sites without it: ISO C/C++ evaluates an undefined identifier inside a
// preprocessor #if expression as 0, which is exactly this default's value,
// so the block below is documentary (not load-bearing) at those two sites.
// If -Wundef is ever enabled, those two sites will need this default pulled
// into a dependency-free header included unconditionally at their top.
#ifndef DEV_TOOLS
#define DEV_TOOLS 0
#endif
```

- Bounding lines: block sits from line 20 (comment start) to line 42 (`#endif`), strictly between `__FIRESTARTER_H__`'s `#define` (line 9) and the CMD_DEV_ADDRESS/CMD_DEV_REGISTER conditional block (line 66 post-shift).
- `grep -cE '^#define DEV_TOOLS 0$' include/firestarter.h` → **1**. `grep -cE '^#ifndef DEV_TOOLS$' include/firestarter.h` → **1**.
- `git diff HEAD -- include/firestarter.h` (Task 1 commit) → addition-only, 24 lines inserted, 0 removed, no `CMD_*`/`FLAG_*` line touched.

### Task 2 — the six-site conversion

- **Six sites, pre-edit line numbers, all confirmed `#ifdef DEV_TOOLS`:** `include/firestarter.h:66`, `include/dev_tools.h:11`, `src/dev_tools.cpp:8`, `src/firestarter.cpp:21, 97, 271`.
- **Post-edit anchored count:** `grep -cE '^#if DEV_TOOLS$'` across the four files: `include/firestarter.h`=1, `include/dev_tools.h`=1, `src/dev_tools.cpp`=1, `src/firestarter.cpp`=3 — **sums to 6** (1+1+1+3), matching the plan's exact breakdown.
- **Post-edit anchored `#ifdef` count:** `grep -cE '^#ifdef DEV_TOOLS$'` across the four files — **sums to 0** in each file.
- **Unanchored substring proof (mechanical evidence only directives moved):**
  - `include/firestarter.h`: pre-edit `grep -c '#ifdef DEV_TOOLS'` = **4** (lines 42 directive, 51/70/73 comment prose, at pre-Task-1 line numbers) → post-edit = **3** (lines 75, 94, 97 post-shift, all read and confirmed comment prose describing the historical mechanism).
  - `src/firestarter.cpp`: pre-edit = **4** (lines 21/97/271 directives, 79 comment prose) → post-edit = **1** (line 79, read and confirmed comment prose).
  - Both pre-edit counts matched the plan's predicted baseline (4/4) exactly before substitution began, per the plan's "stop and reconcile if different" instruction — no reconciliation was needed.
- `grep -cE '^#ifndef __DEV_TOOLS_H__$' include/dev_tools.h` → **1** (include guard survived, untouched).
- `git diff --name-only HEAD` (Task 2 commit) → exactly `include/dev_tools.h`, `include/firestarter.h`, `src/dev_tools.cpp`, `src/firestarter.cpp`. `platformio.ini` absent from that list, and its `-D DEV_TOOLS` at line 26 was read and confirmed to already expand to `=1` (no value suffix — GCC/PlatformIO's `-D FOO` bare form is `FOO=1`) — no edit made.

- **AVR flash/RAM, clean builds, compared side-by-side with Plan 124-04/124-05's recorded post-landing figures:**

  | Env | 124-04/05 recorded | This plan (post-conversion) | Delta |
  |---|---|---|---|
  | uno flash | 23954 | 23954 | 0 |
  | uno RAM | 1573 | 1573 | 0 |
  | uno328pb flash | 24004 | 24004 | 0 |
  | uno328pb RAM | 1579 | 1579 | 0 |
  | leonardo flash | 26016 | 26016 | 0 |
  | leonardo RAM | 2014 | 2014 | 0 |

  **All six pairs byte-identical — the conversion's measured AVR cost is genuinely zero, confirming the plan's claim rather than absorbing it unmeasured.**

- **Native counts** (cold, single uninterrupted `pio test` invocation after `rm -rf .pio/build/<env>`, 540000ms Bash timeout):

  | Env | Cases | Suites | All PASSED |
  |---|---|---|---|
  | native | 141 | 17 | yes |
  | native_nodevtools | 141 | 17 | yes |

- **`check_build_warnings.py --log`, three AVR envs (clean rebuild + captured logs):** `PASS: uno: macro_redefinition=0 (== 0), uno328pb: macro_redefinition=0 (== 0), leonardo: macro_redefinition=0 (== 0)` — exit 0.
- **`check_cmake_manifest.py`:** `PASS: ... 23 enforced source(s) resolved ... allow-listed omission(s): src/boards/leonardo_rurp_shield.cpp, src/boards/rurp_common.cpp, src/boards/uno_rurp_shield.cpp, src/dev_tools.cpp, src/rurp_config_utils.cpp` — exit 0, unregressed from Plan 124-05's landing.
- **`firestarter/tests/` (firmware-side pytest, not the host suite):** `1 failed, 65 passed` — the sole failure is `tests/test_check_orphan_provisional.py::test_unarmed_on_the_real_tree_with_no_seam_override`, owned by Plan 124-08, unchanged and left red as required.
- **`git status --porcelain` (firestarter submodule, end of Task 2):** empty.

### Task 3 — host-repo gates (MERGE-07), run from `/workspaces/firestarter_app`

- `python3 tools/check_is_memory_cmd_no_ifdef.py` → `PASS: is_memory_cmd() has no preprocessor conditional and enumerates exactly the eight expected commands (.../firestarter/include/firestarter.h, predicate body lines 133-147)` — exit 0.
- `python3 -m pytest tests/test_revision_constants_parity.py -q` → **13 passed, 0 failed** (matches Phase 123's recorded count exactly).
- `python3 -m pytest tests/test_check_is_memory_cmd_no_ifdef.py -q` → **6 passed**.
- `python3 -m pytest tests/ -q -rs` → **1158 passed, 0 failed, 0 skipped** (matches Phase 123's recorded 1158 exactly; explicit grep for `SKIPPED`/`skipped` in the captured log returned 0 hits).
- `git -C /workspaces/firestarter_app status --porcelain` → `M .gitignore`, `?? .coverage`, `?? .planning/config.json`, `?? SECURITY.md`, `?? write_test_port.sh` — identical to the pre-existing dirt list recorded in this plan's context section (which additionally names `.planning/config.json`); nothing new, nothing removed.

## Task Commits

Each code-producing task was committed atomically, inside the `firestarter` submodule (`/workspaces/firestarter`) on branch `v1.23-py32f071-integration`. Task 3 modifies no files (gate re-run only) and produced no commit.

1. **Task 1: Add the shared value-semantics default at placement B** - `b8516ea` (feat)
2. **Task 2: Convert the six conditionals with a line-anchored substitution** - `edc73e2` (fix)

_No plan-metadata commit is made inside the submodule — the meta-repo's own SUMMARY.md commit (below) is this plan's final commit._

## Files Created/Modified

- `firestarter/include/firestarter.h` - added the shared `DEV_TOOLS` default (placement B) + converted the CMD_DEV_ADDRESS/CMD_DEV_REGISTER conditional to `#if DEV_TOOLS`
- `firestarter/include/dev_tools.h` - converted the whole-body guard to `#if DEV_TOOLS`
- `firestarter/src/dev_tools.cpp` - converted the whole-file guard to `#if DEV_TOOLS`
- `firestarter/src/firestarter.cpp` - converted the include guard, debug-log pair, and dispatch arm (3 sites) to `#if DEV_TOOLS`

## Decisions Made

- **Placement B chosen and verified, not assumed.** Read `_find_header_guard_line_indices`'s behavior in the plan's cited research material before committing to siting the default inside the guard beside `DATA_BUFFER_SIZE`; did not take C-18's claim on faith.
- **The two out-of-scope sites documented, not silently left inconsistent.** `include/dev_tools.h` and `src/dev_tools.cpp` test `DEV_TOOLS` before including `firestarter.h`, so the shared default cannot reach them syntactically. The comment records this honestly (correction C-7) rather than implying uniform load-bearing coverage across all six sites — behavior is still correct there today because ISO C/C++ treats an undefined identifier in `#if` as 0.
- **Per-line anchored `sed`, not a global substitution.** Each of the six directive conversions targeted its own recorded line number, making it structurally impossible to touch the five comment occurrences that deliberately preserve the historical presence-semantics record (Phase 119 LOCK-02/LOCK-03 rationale).

## Deviations from Plan

### Documented Findings (not auto-fixed — measurement facts, not defects)

**1. `is_memory_cmd`'s reported predicate-body line range shifted further than RESEARCH predicted.** The plan's `read_first` material cited Phase 123's recorded range as `109-123` and RESEARCH's post-D-02 prediction as `113-127` (a +4 shift). The actual observed range after this plan's edits is **133-147** — a +24 shift from Phase 123's baseline, not +4. Root cause: Task 1's comment block above the shared default is 20 comment lines plus 4 code lines (24 total), materially longer than whatever draft RESEARCH measured against when it predicted +4. This is a measurement fact, not a defect — the predicate itself is byte-identical in structure and content (still the same eight named commands, still zero preprocessor conditionals, still `static inline` in the header), only its line position moved because a large amount of explanatory prose was inserted above it in the same file, exactly as the plan's own acceptance criteria anticipated by requiring the *actual* range be recorded and compared rather than assumed. Reported here as a finding per the plan's explicit instruction, not silently reconciled.

---

**Total deviations:** 0 auto-fixed; 1 documented finding (a predicted-vs-observed line-range discrepancy caused by comment length, not a code defect).
**Impact on plan:** None on scope, correctness, or the discharged claims. `check_is_memory_cmd_no_ifdef.py` still exits 0 with the same eight-command enumeration and the same no-conditional guarantee; only the reported line numbers moved.

## Issues Encountered

None beyond the line-range finding documented above.

## User Setup Required

None - no external service configuration required.

## Requirement Ticking Scope

Per this plan's dispatch instructions, `.planning/REQUIREMENTS.md` was **not** touched by this plan. What was proved: MERGE-08's third defect (the `DEV_TOOLS` presence→value conversion, measured zero AVR cost) and a re-confirmation of MERGE-07 (the three host-repo source-text gates still run and pass through this preprocessor restructure). Plan 124-12 owns citing this evidence when it ticks MERGE-07/MERGE-08.

## Next Phase Readiness

- `DEV_TOOLS` now means the same thing (value-tested, default 0) on every target — AVR (`-D DEV_TOOLS` → `=1`), native (inherits the same flag), native_nodevtools (undefined → default 0), and ARM/py32f071 (undefined → default 0, no `target_compile_definitions` change needed there either).
- AVR flash/RAM figures for the next plan's baseline are unchanged from 124-04/124-05: uno 23954/1573, uno328pb 24004/1579, leonardo 26016/2014.
- `firestarter/tests/`'s sole remaining red, `test_check_orphan_provisional.py::test_unarmed_on_the_real_tree_with_no_seam_override`, is confirmed still red and unowned by this plan — Plan 124-08's target.
- `check_cmake_manifest.py`'s `src/dev_tools.cpp` `PY32_EXCLUDED` reason (written by Plan 124-05 in anticipation of this plan) is now fully true of the actual mechanism, not just of the manifest's own comment: `DEV_TOOLS` genuinely resolves to 0 by the shared default in a build that omits `-D DEV_TOOLS` (ARM, native_nodevtools).
- No blockers for 124-08 onward.

## Self-Check: PASSED

- FOUND: `firestarter/include/firestarter.h` (modified, `#define DEV_TOOLS 0` count=1 confirmed via grep)
- FOUND: `firestarter/include/dev_tools.h` (modified, `#if DEV_TOOLS` confirmed via grep)
- FOUND: `firestarter/src/dev_tools.cpp` (modified, `#if DEV_TOOLS` confirmed via grep)
- FOUND: `firestarter/src/firestarter.cpp` (modified, 3x `#if DEV_TOOLS` confirmed via grep)
- FOUND commit `b8516ea` (firestarter submodule) — `git log --oneline --all | grep b8516ea` matches
- FOUND commit `edc73e2` (firestarter submodule) — `git log --oneline --all | grep edc73e2` matches

---
*Phase: 124-firmware-integration-merge*
*Completed: 2026-07-31*
