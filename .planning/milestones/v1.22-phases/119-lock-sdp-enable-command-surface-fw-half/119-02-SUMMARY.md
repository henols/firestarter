---
phase: 119-lock-sdp-enable-command-surface-fw-half
plan: 02
subsystem: firmware-protocol-dispatch
tags: [firmware, platformio, native-test, dispatch, sdp, at28c, cmd-admission]

# Dependency graph
requires:
  - phase: 119-lock-sdp-enable-command-surface-fw-half
    plan: "01"
    provides: the three catalog ids (MSG_INFO_SDP_LOCK 0x60, MSG_INFO_SDP_LOCK_DONE_US 0x61, MSG_INFO_PAGE_LOAD_WORST_US 0x62) this plan does not yet emit but that Plan 119-04 will
provides:
  - CMD_SDP_UNLOCK (9) and CMD_SDP_LOCK (10), unconditionally defined command values
  - is_memory_cmd(uint8_t) — a static inline, header-resident, DEV_TOOLS-invariant admission predicate replacing the old #ifdef-conditional ordinal guard
  - "[env:native_nodevtools] — a second native PlatformIO env compiling and running the full 16(->17)-suite test_filter without -D DEV_TOOLS"
  - test_cmd_admission — an exhaustive 256-value truth-table suite proving is_memory_cmd() is set-equal in both build configurations
affects: [119-03, 119-04, 119-07]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Second native PlatformIO env pattern: duplicate the FULL positive test_filter + -I allowlist rather than a subset, to get DEV_TOOLS-invariance coverage across every suite for near-zero measured cost"
    - "Admission predicates that must be DEV_TOOLS-invariant belong in the header as static inline, named-macro-only, zero-preprocessor-conditional functions — never as a .cpp definition (native's build_src_filter would not link it) and never referencing a conditionally-defined macro"

key-files:
  created:
    - firestarter/test/native/avr/test_cmd_admission/test_cmd_admission.cpp
    - firestarter/test/native/avr/test_cmd_admission/host_stubs.cpp
    - firestarter/test/native/avr/test_cmd_admission/avr/pgmspace.h
  modified:
    - firestarter/platformio.ini (new [env:native_nodevtools]; four new test_filter/-I lines in both native envs)
    - firestarter/.github/workflows/build.yml (new "Run native unit tests (no DEV_TOOLS)" CI step)
    - firestarter/CLAUDE.md (corrected stale "no platformio.ini change needed for new suites" claim)
    - firestarter/include/firestarter.h (CMD_SDP_UNLOCK/CMD_SDP_LOCK defines; is_memory_cmd() predicate)
    - firestarter/src/firestarter.cpp (guard replacement; :134 second-guard scope-decision comment)
    - .planning/todos/pending/prove-pio-dev-flag-fails-closed.md (item 4 recorded as answered)

key-decisions:
  - "is_memory_cmd() is a switch over exactly eight named CMD_* macros (CMD_READ/WRITE/ERASE/BLANK_CHECK/CHECK_CHIP_ID/VERIFY/SDP_UNLOCK/SDP_LOCK), static inline in firestarter.h, with zero preprocessor conditionals in its body -- it never names CMD_DEV_ADDRESS/CMD_DEV_REGISTER, which is what lets it compile identically under -D DEV_TOOLS and without it"
  - "Three named behaviour deltas, all deliberate: cmd 7 and cmd 8 (CMD_DEV_ADDRESS/CMD_DEV_REGISTER) no longer reach configure_memory in a release build -- D-01's safety tightening, since a release build previously configured a memory handler for a command it was about to refuse anyway; cmd 0 (CMD_IDLE) now falls to loop()'s existing case CMD_IDLE: break; (silence) instead of producing two error frames (0xBB then MSG_ERR_SETUP) -- accepted because CMD_IDLE is a firmware-internal state no shipped host path emits"
  - "firestarter.cpp's SECOND, independent ordinal-range guard at (post-edit) line 134 -- handle->cmd > CMD_IDLE && handle->cmd < CMD_READ_VPP, gating three debug-only DBG_MEM_SIZE/DBG_ADDR_MASK/DBG_MATCH_LINES lines -- was deliberately left unconverted. It gates diagnostics, never hardware configuration, so D-03's safety argument doesn't apply; converting it would silently drop those three lines for cmd 7/8 in a DEV_TOOLS build for zero safety gain. CMD_SDP_UNLOCK/CMD_SDP_LOCK (9/10) already satisfy this range test unchanged, so there is no coverage gap for the two new commands."
  - "[env:native_nodevtools] duplicates [env:native]'s FULL 16-entry test_filter/-I lists rather than a subset carrying only the new truth-table suite -- RESEARCH measured zero test-porting cost (no test file anywhere references DEV_TOOLS or CMD_DEV_*) for ~52s of extra cold-build CI time, buying DEV_TOOLS-invariance proof across all 16 pre-existing suites, not just the new one"
  - "test_cmd_admission asserts on is_memory_cmd() ONLY, never on dispatch/configure_memory/any handler -- keeps it orthogonal to test_dispatch (which tests what a command DOES) and focused purely on what the admission gate ADMITS"

requirements-completed: []

coverage:
  - id: D1
    description: "CMD_SDP_UNLOCK (9) / CMD_SDP_LOCK (10) defined unconditionally in include/firestarter.h, placed between the DEV_TOOLS-conditional CMD_DEV_* pair and CMD_READ_VPP (11), with a comment recording D-03's ordering reason and the Phase 120 HOST-01/HOST-03 host-surface pointer"
    verification:
      - kind: unit
        ref: "grep -c 'CMD_SDP_UNLOCK 9\\|CMD_SDP_LOCK 10' include/firestarter.h -> 2"
        status: pass
    human_judgment: false
  - id: D2
    description: "is_memory_cmd(uint8_t) added as a static inline header predicate naming exactly eight CMD_* macros, no preprocessor conditional in its body, does not name CMD_DEV_ADDRESS/CMD_DEV_REGISTER -- replaces the old #ifdef DEV_TOOLS ordinal guard in firestarter.cpp's parse_json"
    verification:
      - kind: unit
        ref: "test/native/avr/test_cmd_admission/test_cmd_admission.cpp#test_admission_truth_table_over_every_cmd_value -- exhaustive 256-value truth table"
        status: pass
      - kind: unit
        ref: "pio test -e native -f \"*test_cmd_admission*\" -- 4/4"
        status: pass
      - kind: unit
        ref: "pio test -e native_nodevtools -f \"*test_cmd_admission*\" -- 4/4"
        status: pass
    human_judgment: false
  - id: D3
    description: "[env:native_nodevtools] stood up (full 16/17-suite test_filter + -I list, no -D DEV_TOOLS, explicit -D MONITOR_SPEED/-D HARDWARE_REVISION, not in default_envs); CI step added after the existing native step; folded todo item 4 recorded as answered"
    verification:
      - kind: unit
        ref: "pio test -e native -- 116 test cases across 17 suites succeeded"
        status: pass
      - kind: unit
        ref: "pio test -e native_nodevtools -- 116 test cases across 17 suites succeeded"
        status: pass
      - kind: unit
        ref: "pio run -- uno/uno328pb/leonardo all SUCCESS"
        status: pass
    human_judgment: false
  - id: D4
    description: "Host gates (firestarter_app) re-run at baseline after the firmware header/cpp edits: no source-scanning gate broken by the rename/edit class that bit Phase 117 four times"
    verification:
      - kind: unit
        ref: "pytest tests/test_revision_constants_parity.py tests/test_sdp_table_parity.py tests/test_check_no_log_in_sdp_window.py tests/test_sdp_bus_config_drift.py -- 21 passed"
        status: pass
      - kind: unit
        ref: "python3 tools/check_no_log_in_sdp_window.py -- exit 0"
        status: pass
      - kind: unit
        ref: "python3 tools/check_dispatch.py -- exit 0 (746 scanned, 0 regressions)"
        status: pass
    human_judgment: false

duration: ~35min
completed: 2026-07-28
status: complete
---

# Phase 119 Plan 02: is_memory_cmd() Admission Predicate + Two-Env Truth Table Summary

**Replaced the `#ifdef DEV_TOOLS`-conditional ordinal command guard with a header-inline `is_memory_cmd()` predicate, defined the two new SDP command values it admits, and proved DEV_TOOLS-invariance with an exhaustive 256-value truth table run in a newly-stood-up no-DEV_TOOLS native env.**

## Performance

- **Duration:** ~35 min
- **Completed:** 2026-07-28
- **Tasks:** 3/3
- **Files modified:** 9 (6 firmware files modified, 3 new test files, 1 planning todo)

## Accomplishments

- Stood up `[env:native_nodevtools]` in `platformio.ini`: full 16-entry (later 17) `test_filter`/`-I` allowlist duplicated from `[env:native]`, `build_flags` spelled out explicitly (`-D MONITOR_SPEED=250000 -D HARDWARE_REVISION`) with `-D DEV_TOOLS` omitted, not added to `default_envs`. Proved before adding any new suite: `pio test -e native` 112/112, `pio test -e native_nodevtools` 112/112 with **zero test-code changes**, `pio run` 3/3 SUCCESS.
- Added a `pio test -e native_nodevtools` CI step to `.github/workflows/build.yml` immediately after the existing native step, named to D-04; will not fire on this milestone branch (workflow triggers on `main` only) — the local run above is the in-phase proof.
- Corrected `firestarter/CLAUDE.md`'s stale "platformio.ini needs no changes for new native suites" claim: it is a positive `test_filter` allowlist, and a new suite now needs four lines (one `test_filter` + one `-I`, in each of two envs).
- Recorded the folded todo `prove-pio-dev-flag-fails-closed.md`'s item 4 as answered against the todo file itself (112/112 with DEV_TOOLS absent, zero test-porting cost); items 1-3 (the sysenv fail-open/fail-closed matrix, `avr-nm` symbol capture) left untouched, scoped to 999.15/gh#8.
- Defined `CMD_SDP_UNLOCK` (9) / `CMD_SDP_LOCK` (10) unconditionally in `include/firestarter.h`, placed between the DEV_TOOLS-conditional `CMD_DEV_*` pair and `CMD_READ_VPP` (11).
- Added `static inline bool is_memory_cmd(uint8_t cmd)` in the header: a `switch` over exactly the eight named macros `CMD_READ`, `CMD_WRITE`, `CMD_ERASE`, `CMD_BLANK_CHECK`, `CMD_CHECK_CHIP_ID`, `CMD_VERIFY`, `CMD_SDP_UNLOCK`, `CMD_SDP_LOCK`, with no preprocessor conditional in its body and no reference to `CMD_DEV_ADDRESS`/`CMD_DEV_REGISTER`.
- Replaced the old `#ifdef DEV_TOOLS` / `handle->cmd < CMD_DEV_ADDRESS` guard in `firestarter.cpp`'s `parse_json` with `if (is_memory_cmd(handle->cmd))`; the `else` branch is now unconditional, with the `DEV_TOOLS` conditional moved inside it to wrap only the two `DBG_FLAG_OUTPUT_EN`/`DBG_FLAG_CHIP_EN` debug lines (which compile empty in a release build).
- Left `firestarter.cpp`'s second, independent ordinal-range guard (three `DBG_MEM_SIZE`/`DBG_ADDR_MASK`/`DBG_MATCH_LINES` debug lines) unconverted, with an explicit in-source comment recording why.
- Created `test/native/avr/test_cmd_admission/` (three files: suite, `host_stubs.cpp` pass-through, byte-identical `avr/pgmspace.h`) with four cases: the exhaustive 256-value truth table, the cmd-7/8-rejection case (bare numeric literals, no `CMD_DEV_*` reference), the `CMD_IDLE`-rejection case, and a non-memory-command sample. Added the suite to both native envs' `test_filter`/`-I` lists (four new lines total).

## Three Named Behaviour Deltas (D-01 names only 7/8; this plan owns the third)

1. **cmd 7 (`CMD_DEV_ADDRESS`)** — no longer reaches `configure_memory()` in a release build. Previously, a release build ran `json_parse` and `configure_memory` for this command before `loop()`'s `default:` refused it with `MSG_ERR_UNKNOWN_CMD` — i.e. it configured a memory handler for a command it was about to refuse. That configuration step is now skipped; the `MSG_ERR_UNKNOWN_CMD` refusal itself is unchanged. **Deliberate safety tightening (D-01).**
2. **cmd 8 (`CMD_DEV_REGISTER`)** — identical delta and disposition to cmd 7.
3. **cmd 0 (`CMD_IDLE`)** — previously satisfied the old guard's range test (`< CMD_READ_VPP`, and `< CMD_DEV_ADDRESS` in a `DEV_TOOLS` build) in both build configurations, running `json_parse` and `configure_memory`, which produced two error frames (`0xBB MSG_ERR_PROTOCOL_NOT_IMPLEMENTED`, then `MSG_ERR_SETUP`, since `handle->protocol` is 0 for an idle handle). After `is_memory_cmd()`, cmd 0 is not admitted and falls to `loop()`'s pre-existing `case CMD_IDLE: break;`, producing silence and returning to waiting. **Accepted deliberately (RESEARCH F-B2's third delta):** `CMD_IDLE` is a firmware-internal state, not a command any shipped host path emits; an explicit refusal arm for cmd 0 was considered and declined on flash-cost grounds against the live 2980 B Leonardo headroom (see below) for a frame no host sends.

## The Second Ordinal Guard (`firestarter.cpp`, post-edit line 134)

`if (handle->cmd > CMD_IDLE && handle->cmd < CMD_READ_VPP)` — gates three `LOG_DEBUG_ID_SUB_*` lines (`DBG_MEM_SIZE`, `DBG_ADDR_MASK`, `DBG_MATCH_LINES`) inside `init_programmer_framed`. **Deliberately left unconverted.** It gates diagnostic output only, never hardware configuration, so it is not an admission gate and D-03's safety argument doesn't apply to it. Converting it to `is_memory_cmd()` would silently drop those three debug lines for cmd 7/8 in a `DEV_TOOLS` build — a diagnostic regression — for zero safety gain and non-zero flash cost (these are `LOG_DEBUG_ID_SUB_*` calls, gated to zero cost only when `-D SERIAL_DEBUG` is also set, which it is not by default). The two new commands (`CMD_SDP_UNLOCK` 9, `CMD_SDP_LOCK` 10) already satisfy this range test unchanged, so there is no coverage gap introduced for them. A comment recording this decision was added in-source so a verifier does not have to rediscover it.

## Both Envs' Case/Suite Counts

- Before Task 3 (predicate + guard replacement only): `pio test -e native` 112/112 across 16 suites; `pio test -e native_nodevtools` 112/112 across 16 suites — unchanged baseline in both, zero test-code changes at that point.
- After Task 3 (new suite added): `pio test -e native` **116/116 test cases across 17/17 suites**; `pio test -e native_nodevtools` **116/116 test cases across 17/17 suites** — identical counts in both envs, the D-04 semantic proof.
- `pio test -e native -f "*test_cmd_admission*"`: 4/4. `pio test -e native_nodevtools -f "*test_cmd_admission*"`: 4/4.

## Flash/RAM Figures

Measured against the phase-119 base recorded in `119-01-SUMMARY.md` (Leonardo 25680/28672, 2992 B free; Uno 23542/32256; uno328pb 23592/32384 — all RAM unchanged there since Plan 119-01 added only unreferenced catalog ids):

| Board | Flash (before -> after) | Delta | RAM | Free flash after |
|---|---|---|---|---|
| Leonardo | 25680 -> 25692 / 28672 | **+12 B** | 1998/2560 (unchanged) | **2980 B** |
| Uno | 23542 -> 23554 / 32256 | +12 B | 1559/2048 (unchanged) | 28702 B |
| uno328pb | 23592 -> 23604 / 32384 | +12 B | 1563/2048 (unchanged) | 28780 B |

`pio run`: 3/3 SUCCESS for all three AVR envs, both before and after Task 3 (the native-only test suite addition costs nothing on the AVR builds). The +12 B delta is the net cost of `is_memory_cmd()`'s eight-case switch plus the restructured `if`/`else` in `parse_json`, offset by nothing removed (the old guard's debug lines are retained, just relocated). This is a smaller delta than either of Phase 117's (+204 B) or Phase 118's (+152 B) measurements — LOCK-06's later arithmetic should start from **2980 B** free on Leonardo, not the 2992 B this plan started with.

## Folded-Todo Item-4 Result

Recorded directly in `.planning/todos/pending/prove-pio-dev-flag-fails-closed.md`: `pio test -e native_nodevtools` passes 112/112 across 16/16 suites (measured before Task 3 added the new suite) with zero test-code changes, confirming the grep-based prediction that no test file references `DEV_TOOLS` or `CMD_DEV_*`. This answers item 4 ONLY — items 1 through 3 (the `sysenv.FIRESTARTER_DEV_TOOLS` fail-open/fail-closed matrix and the `avr-nm` symbol capture) remain untouched, scoped to backlog 999.15 / gh#8.

## `CLAUDE.md` Correction

`firestarter/CLAUDE.md`'s "Reuse pattern for future native tests" section previously claimed `[env:native]`'s configuration "does not need changes for new suites." That was already false before this plan (the positive `test_filter` allowlist requires a matching line, per the section's own earlier text) and is now doubly false with a second native env: a new suite needs **four** lines (one `test_filter` + one `-I`, in each of the two native envs). The section was rewritten to state this explicitly, citing `platformio.ini`'s `test_filter` block, so the next phase does not repeat the error.

## Task Commits

Each task was committed atomically inside the `firestarter/` submodule:

1. **Task 1: Stand up [env:native_nodevtools], its CI step, and correct CLAUDE.md's stale suite claim** — `76f70c7` (feat)
2. **Task 2: Define CMD_SDP_UNLOCK / CMD_SDP_LOCK, add is_memory_cmd(), and replace the ordinal guard** — `dcb3576` (feat)
3. **Task 3: Add the test_cmd_admission truth-table suite and run it in BOTH native envs** — `8341b3f` (test)

**Plan metadata:** committed alongside this SUMMARY (docs, meta commit).

## Files Created/Modified

- `firestarter/platformio.ini` — new `[env:native_nodevtools]` block; four new `test_filter`/`-I` lines split across both native envs
- `firestarter/.github/workflows/build.yml` — new "Run native unit tests (no DEV_TOOLS)" CI step
- `firestarter/CLAUDE.md` — corrected the stale new-native-suite claim
- `firestarter/include/firestarter.h` — `CMD_SDP_UNLOCK`/`CMD_SDP_LOCK` defines; `is_memory_cmd()` predicate
- `firestarter/src/firestarter.cpp` — guard replacement in `parse_json`; scope-decision comment on the second ordinal guard
- `firestarter/test/native/avr/test_cmd_admission/test_cmd_admission.cpp` — new truth-table suite (4 cases)
- `firestarter/test/native/avr/test_cmd_admission/host_stubs.cpp` — new pass-through stub TU
- `firestarter/test/native/avr/test_cmd_admission/avr/pgmspace.h` — new, byte-identical copy of `test_dispatch`'s
- `.planning/todos/pending/prove-pio-dev-flag-fails-closed.md` — item 4 recorded as answered

## Decisions Made

See `key-decisions` in frontmatter for the four load-bearing ones (predicate shape, three behaviour deltas, second-guard scope decision, full-vs-subset test_filter duplication). All match the plan's `must_haves.truths` verbatim; none required deviation.

## Deviations from Plan

None — plan executed exactly as written. All three tasks' acceptance criteria were met without any Rule 1-4 auto-fixes.

## Issues Encountered

None. `firestarter_app`'s pre-existing untracked/modified files (`.gitignore` local edit, `.coverage`, `.planning/config.json`, `SECURITY.md`, `doc/lockable-proms.md`, `write_test_port.sh`) predate this plan (carried from Plan 119-01's session) and are unrelated to this plan's firmware-only scope — confirmed unchanged by `git status --short` before and after, out of scope per the scope boundary rule.

## User Setup Required

None — no external service configuration required.

## Known Stubs

None. This plan lands firmware-only defines, a predicate, and test infrastructure — no UI or data-rendering path is affected, and no call site emits or consumes the two new command values yet (that is Plan 119-04's explicit, intentional scope).

## Requirement Status

**Per plan instruction, NO requirement rows were changed.** This plan's frontmatter lists `LOCK-03, LOCK-02` but closes neither:
- **LOCK-03 stays OPEN** until Plan 119-03 lands D-04's textual source-scan gate (`check_is_memory_cmd_no_ifdef.py`) with its planted-violation fixture — the other half of D-04's proof shape (this plan supplied the semantic/two-env half).
- **LOCK-02 stays OPEN** until Plan 119-07 — this plan lands only the two command DEFINES (D-03's prerequisite ordering); no host CLI surface, no `loop()` dispatch arm, no `configure_eeprom28c` wiring.

`REQUIREMENTS.md` was not touched.

## Next Phase Readiness

- `CMD_SDP_UNLOCK` (9) and `CMD_SDP_LOCK` (10) exist, are admitted by `is_memory_cmd()`, and reach `loop()`'s `default:` (inert, correct) — ready for Plan 119-04 to add `case` arms and wire `configure_eeprom28c`'s lock/unlock ops.
- `[env:native_nodevtools]` and its CI step are in place for every subsequent Phase 119 plan to keep exercising.
- Leonardo flash headroom for LOCK-06's later arithmetic: **2980 B free** (was 2992 B at this plan's start; this plan spent 12 B).
- No blockers for Plan 119-03.

---
*Phase: 119-lock-sdp-enable-command-surface-fw-half*
*Completed: 2026-07-28*

## Self-Check: PASSED

- FOUND: `firestarter/test/native/avr/test_cmd_admission/test_cmd_admission.cpp`
- FOUND: `firestarter/platformio.ini`
- FOUND: `76f70c7` (Task 1 commit)
- FOUND: `dcb3576` (Task 2 commit)
- FOUND: `8341b3f` (Task 3 commit)
