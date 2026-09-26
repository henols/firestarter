---
phase: 119-lock-sdp-enable-command-surface-fw-half
plan: 04
subsystem: firmware-sdp-lock
tags: [firmware, firestarter_app, sdp, at28c, eeprom28c, source-scan-gate, dispatch]

# Dependency graph
requires:
  - phase: 119-lock-sdp-enable-command-surface-fw-half
    plan: "02"
    provides: CMD_SDP_UNLOCK (9) / CMD_SDP_LOCK (10) command values and is_memory_cmd() admission
  - phase: 119-lock-sdp-enable-command-surface-fw-half
    plan: "03"
    provides: check_is_memory_cmd_no_ifdef.py, closing LOCK-03
provides:
  - "EEPROM_SDP_ENABLE[3] (AA-55-A0, external linkage) -- the new AT28C SDP-enable command table"
  - "eeprom28c_emit_sdp_sequence_timed() -- shared micros()-bracket + report-pair + length-derived t_BLC budget-check helper, driven by both SDP sequences"
  - "eeprom28c_sdp_unlock_execute() / eeprom28c_sdp_lock_execute() -- file-static standalone ops wired into configure_eeprom28c's CMD_SDP_UNLOCK / CMD_SDP_LOCK arms (no default: arm added)"
  - "eprom_sdp_unlock() / eprom_sdp_lock() entry points (eprom_operations.{cpp,h}) and their loop() case arms in firestarter.cpp"
  - "check_no_log_in_sdp_window.py repaired: appended emit anchor, by-design-helper comment, two tripwire notes; new PASS: baseline (emitter 298-314, poll 348-361)"
affects: [119-05, 119-06, 119-07, 119-10]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Shared timed-emit helper parameterised by message-id pair (uint8_t emitted_msg_id, uint8_t done_us_msg_id) -- lets one function drive two independently-catalogued report pairs without a second copy of the micros()-bracket/budget-check shape"
    - "Two standalone ops rather than one cmd-discriminated function for a shared table-driven sequence -- keeps separate-literal-ids shape literal and keeps 'which sequence ran' answerable from a stack trace"
    - "Cross-repo source-scanning gate repair landed in the SAME plan/commit sequence as the firmware refactor that breaks it (append-only anchor tuple), per the Phase 117 four-times-bitten lesson"

key-files:
  created: []
  modified:
    - firestarter/src/proms/eeprom_28c.cpp
    - firestarter/src/eprom_operations.cpp
    - firestarter/include/eprom_operations.h
    - firestarter/src/firestarter.cpp
    - firestarter_app/tools/check_no_log_in_sdp_window.py

key-decisions:
  - "EEPROM_SDP_ENABLE[3] = {0x5555,0xAA},{0x2AAA,0x55},{0x5555,0xA0} with external linkage (same load-bearing-extern shape as EEPROM_SDP_DISABLE) and a five-item rationale comment discharging ROADMAP criterion 5's intent without touching FIX-04-frozen flash_utils.h (deliberate deviation, same class as D-05/D-15)"
  - "eeprom28c_emit_sdp_sequence_timed() factored out of write_init's former unlock branch; both micros() reads still bracket ONLY eeprom28c_emit_command_sequence's call, the completion wait stays OUTSIDE the helper and at each call site (two different waits: 118's DQ6 poll for unlock, D-11's plain t_WC delay for lock)"
  - "configure_eeprom28c gets two new case arms and explicitly NO default: arm (D-05) -- a comment records why: configure_memory pre-sets CMD_READ/CMD_WRITE/CMD_VERIFY's main before this switch runs, so a default: arm would refuse read/verify on all 84 0x0D chips; CMD_ERASE/CMD_CHECK_CHIP_ID refusal is deferred to Plan 119-07's op-layer NULL-main guard"
  - "Two separate functions (eeprom28c_sdp_unlock_execute / eeprom28c_sdp_lock_execute) rather than one cmd-discriminated function -- CONTEXT.md's discretion item, chosen to keep D-13's separate-literal-ids shape literal and to make 'which sequence ran' answerable from a stack trace; flash cost of the split is small (recorded below) so LOCK-06 can judge it on measurement rather than assumption"
  - "eprom_sdp_unlock/eprom_sdp_lock entry points carry no LOG_DEBUG_ID_SUB line (matches eprom_read's precedent, avoids a new DBG_* catalog id) and no precondition check (D-06's NULL-main op-layer guard, Plan 119-07, is the refusal mechanism for these on the wrong protocol)"
  - "LOCK-02's ROADMAP claim corrected in-source: with init/end left NULL those phases are NOT skipped -- INIT/END frame pairs and their host ACKs still run; what is absent is only the DONE round-trip and any '#' data frame (traced shape: 4 ACKs, 7 framed lines, zero '#' frames, zero DONE string)"
  - "check_no_log_in_sdp_window.py's _EMIT_ANCHOR_PATTERNS gained a third, appended entry for eeprom28c_emit_sdp_sequence_timed(handle, EEPROM_SDP_DISABLE -- both prior entries kept unreordered (append-only per the anti-hollow/revert-tripwire contract)"

requirements-completed: []

coverage:
  - id: D1
    description: "EEPROM_SDP_ENABLE[3] added with external linkage and the five-item rationale comment; flash_utils.h byte-untouched; FLASH_ENABLE_WRITE_PROTECTION still uncalled"
    requirement: LOCK-01
    verification:
      - kind: unit
        ref: "git diff --quiet -- include/flash_utils.h -- exits 0"
        status: pass
      - kind: unit
        ref: "grep -rn FLASH_ENABLE_WRITE_PROTECTION src/ include/ -- only the flash_utils.h definition and this plan's comment reference it, zero call sites"
        status: pass
    human_judgment: false
  - id: D2
    description: "eeprom28c_emit_sdp_sequence_timed() shared helper drives both SDP sequences' report pair, micros() bracket and length-derived t_BLC budget check; writes no response_code"
    requirement: LOCK-01
    verification:
      - kind: unit
        ref: "pio test -e native -f \"*test_sdp_harness*\" and *test_eeprom28c_sdp* -- both suites within the 116/116 all-suite run, unchanged pass count"
        status: pass
    human_judgment: false
  - id: D3
    description: "eeprom28c_sdp_lock_execute is exactly three writes plus delay(AT28C_TWC_MAX_MS) -- no read, no completion poll, no data write; eeprom28c_sdp_unlock_execute reuses 118's ids and the completion wait"
    requirement: LOCK-01
    verification:
      - kind: unit
        ref: "manual source inspection of eeprom28c_sdp_lock_execute/eeprom28c_sdp_unlock_execute bodies (eeprom_28c.cpp:395-418) -- no eeprom28c_wait_for_sdp_completion call in the lock body, no firestarter_get_data call anywhere in either op"
        status: pass
    human_judgment: false
  - id: D4
    description: "configure_eeprom28c gains CMD_SDP_UNLOCK/CMD_SDP_LOCK arms, no default: arm, with the declined-arm rationale comment naming CMD_ERASE and CMD_CHECK_CHIP_ID"
    requirement: LOCK-02
    verification:
      - kind: unit
        ref: "pio run -- 3/3 SUCCESS; pio test -e native/-e native_nodevtools -- both 116/116 across 17 suites (no dispatch regression)"
        status: pass
    human_judgment: false
  - id: D5
    description: "cmd 9/cmd 10 dispatchable end to end: eprom_sdp_unlock/eprom_sdp_lock entry points wired into loop()'s switch, outside any preprocessor conditional, with LOCK-02's corrected claim recorded in-source"
    requirement: LOCK-02
    verification:
      - kind: unit
        ref: "git diff src/firestarter.cpp -- shows only the two new case arms added; default:/CMD_IDLE/DEV_TOOLS arms unchanged"
        status: pass
    human_judgment: false
  - id: D6
    description: "check_no_log_in_sdp_window.py repaired in the same plan as the D-14 refactor that broke it: appended (not replaced) emit anchor, by-design-helper comment, two tripwire notes recorded"
    verification:
      - kind: unit
        ref: "python3 tools/check_no_log_in_sdp_window.py -- PASS (emitter lines 298-314, completion-poll lines 348-361), exit 0"
        status: pass
      - kind: unit
        ref: "python3 -m pytest tests/test_check_no_log_in_sdp_window.py -q -- 7 passed (only test_checker_exits_zero_on_clean_source had been broken by Task 1; repaired by the anchor append, not by editing the test)"
        status: pass
    human_judgment: false
  - id: D7
    description: "Full host + firmware non-regression set green before the meta commit: 27/27 across the five firmware-scanning pytest modules, three check_*.py tools all exit 0, ruff clean, native suites 116/116 in both envs, pio run 3/3"
    verification:
      - kind: unit
        ref: "pytest tests/test_check_no_log_in_sdp_window.py tests/test_check_is_memory_cmd_no_ifdef.py tests/test_sdp_table_parity.py tests/test_sdp_bus_config_drift.py tests/test_revision_constants_parity.py -q -- 27 passed"
        status: pass
      - kind: unit
        ref: "check_no_log_in_sdp_window.py + check_is_memory_cmd_no_ifdef.py + check_dispatch.py -- all exit 0"
        status: pass
      - kind: unit
        ref: "ruff check + ruff format --check tools/check_no_log_in_sdp_window.py -- All checks passed / already formatted (ruff 0.15.20, py39 target)"
        status: pass
    human_judgment: false

duration: ~55min
completed: 2026-07-28
status: complete
---

# Phase 119 Plan 04: EEPROM_SDP_ENABLE, Shared Timed-Emit Helper, and Standalone cmd 9/10 Summary

**Landed the milestone's only new state-mutating operation -- `EEPROM_SDP_ENABLE[3]` (AA-55-A0, three writes + t_WC, no payload) driving a new standalone `CMD_SDP_LOCK`, alongside `CMD_SDP_UNLOCK`'s byte-identical-to-auto-unlock standalone twin, both dispatchable end to end through a shared `eeprom28c_emit_sdp_sequence_timed()` helper -- and repaired the cross-repo `check_no_log_in_sdp_window.py` gate the helper refactor broke, in the same plan as predicted.**

## Performance

- **Duration:** ~55 min
- **Completed:** 2026-07-28
- **Tasks:** 3/3
- **Files modified:** 5 (4 firmware files, 1 host gate file)

## Accomplishments

- Added `EEPROM_SDP_ENABLE[3]` (`{0x5555,0xAA}`, `{0x2AAA,0x55}`, `{0x5555,0xA0}`) immediately after `EEPROM_SDP_DISABLE`, with `extern` linkage and a five-item comment: the doc0270/DS20006432B citation (Write Protect activates at end-of-write even with no other data loaded); the load-bearing-extern rationale; the `0x0D`-local decision (D-09, mirrors 117 D-10); the D-10 dual-purpose hazard (byte-identical to `FLASH_ENABLE_WRITE`/`FLASH_ENABLE_WRITE_PROTECTION`, discriminated only by "no data write follows"); and the criterion-5 deviation naming `test_sdp_harness.cpp:291-296` as the second record.
- Factored `eeprom28c_emit_sdp_sequence_timed(handle, sequence, length, emitted_msg_id, done_us_msg_id)`: `LOG_ID` -> `micros()` bracket around `eeprom28c_emit_command_sequence` -> `LOG_ID_U32` -> length-derived `AT28C_TBLC_MAX_US` budget check with `LOG_WARN_ID_U32` on overrun. Writes no `response_code` anywhere. Rewired `eeprom28c_write_init`'s unlock branch to call it (keeping the single `sdp_seq_len` hoist and the completion wait at the call site, unmoved).
- Added `eeprom28c_sdp_unlock_execute` (helper + `eeprom28c_wait_for_sdp_completion`, reusing 118's `MSG_INFO_SDP_UNLOCK`/`_DONE_US` ids -- byte-identical shape to the auto-unlock, an equality Plan 119-06 will assert) and `eeprom28c_sdp_lock_execute` (helper + `delay(AT28C_TWC_MAX_MS)` only -- no completion poll, no read, no data write, per D-11/D-12).
- Added `CMD_SDP_UNLOCK`/`CMD_SDP_LOCK` arms to `configure_eeprom28c`'s switch, setting only `firestarter_operation_main`. Added **no `default:` arm** (D-05); a comment records why (configure_memory pre-sets read/write/verify's main before this switch runs; CMD_ERASE/CMD_CHECK_CHIP_ID refusal is Plan 119-07's op-layer job).
- Added `eprom_sdp_unlock`/`eprom_sdp_lock` to `eprom_operations.{cpp,h}` (each body `return !op_execute_simple_operation(handle);`, no debug line, no precondition check) and two `case` arms to `firestarter.cpp`'s `loop()`, outside any preprocessor conditional, with a comment recording LOCK-02's corrected claim.
- Repaired `check_no_log_in_sdp_window.py`: appended a third `_EMIT_ANCHOR_PATTERNS` entry for the new `eeprom28c_emit_sdp_sequence_timed(handle, EEPROM_SDP_DISABLE` call site (both prior entries kept, unreordered); added a comment stating the helper's body must never become a third scanned window; recorded the two remaining resolver tripwires (literal `void` return type; `eeprom28c_wait_for_sdp_completion` continuing to exist).

## Task ordering / the predicted gate break

Task 1's helper factor moved `eeprom28c_write_init`'s emit call from a direct `eeprom28c_emit_command_sequence(...)` call to `eeprom28c_emit_sdp_sequence_timed(...)`, which broke the gate's secondary rename-tripwire exactly as RESEARCH F-M predicted:

```
python3 tools/check_no_log_in_sdp_window.py
ERROR: no command-emit anchor found inside eeprom28c_write_init() -- if the
emitter was renamed or replaced, add the new anchor to _EMIT_ANCHOR_PATTERNS
in check_no_log_in_sdp_window.py rather than deleting this gate
```
(exit code 1, an `ERROR:` on stderr -- the fail-closed leg, not a `FAIL:` on stdout)

Only `test_checker_exits_zero_on_clean_source` broke (the one case that runs against the real `eeprom_28c.cpp` with no env override); all six synthetic-fixture cases (2-7) were unaffected because they construct their own minimal source using the pre-existing `eeprom28c_emit_command_sequence(handle, EEPROM_SDP_DISABLE, 6);` call shape, which still matches the second, pre-existing `_EMIT_ANCHOR_PATTERNS` entry. Task 3 appended the third anchor entry (append-only, per the anti-hollow contract) and the gate went green again with a **new phase baseline**:

```
PASS: no logging call in SDP timing window
(.../firestarter/src/proms/eeprom_28c.cpp, emitter lines 298-314, completion-poll lines 348-361)
```
(shifted from the pre-plan baseline of emitter 222-238 / completion-poll 272-285, entirely due to Task 1 inserting the new table and helper above them -- expected, not a regression).

No pytest case was deleted, loosened, or renamed; the fixture `tests/fixtures/planted_log_in_window.cpp` was not touched (its own synthetic `eeprom28c_emit_command_sequence(handle, EEPROM_SDP_DISABLE, 6);` call inside its own `eeprom28c_write_init` still resolves under the append-only anchor set).

## Flash/RAM Figures

Baseline entering this plan (post-119-02, per that plan's SUMMARY): Leonardo 25692/28672 (2980 B free); Uno 23554/32256; uno328pb 23604/32384.

| Board | Flash after Task 1+2 | Delta vs 119-02 baseline | Free flash |
|---|---|---|---|
| Leonardo | 25954/28672 | **+262 B** | **2718 B** |
| Uno | 23814/32256 | +260 B | 28442 B |
| uno328pb | 23858/32384 | +254 B | 28526 B |

`pio run`: 3/3 SUCCESS on all three AVR envs, both after Task 1 and after Task 2. RAM unchanged on all three boards (Leonardo 2014/2560, Uno 1573/2048, uno328pb 1579/2048).

**Per-task attribution:** Task 1 alone (table + helper + two ops + `configure_eeprom28c` arms) already measured Leonardo 25954 and uno328pb 23858 -- identical to the post-Task-2 figures. Task 2 (the two `eprom_operations.cpp` entry points + two `loop()` case arms) therefore measured **+0 B** on Leonardo and uno328pb in this plan's build (confirmed by a clean rebuild after both tasks landed). Uno's Task-1-only figure was not captured separately (the first post-Task-1 build's `tail` output did not include the Uno env's size line before the terminal summary), so Uno's +260 B is reported as the Task-1+2 combined total only; the Leonardo/uno328pb evidence strongly suggests Task 2's own cost is ~0 B there too. **LOCK-06's later flash-headroom arithmetic should start from 2718 B free on Leonardo**, not the 2980 B this plan started with.

## check_no_log_in_sdp_window.py Baseline (New)

- **Old (pre-119-04):** emitter lines 222-238, completion-poll lines 272-285.
- **New (post-119-04):** emitter lines 298-314, completion-poll lines 348-361.

## test_sdp_table_parity.py Interaction with EEPROM_SDP_ENABLE

Confirmed empirically (not just by analysis): `test_sdp_table_parity.py`'s 4 cases all passed unchanged as part of the 27-test host-gate run. Its `_extract_byte_flip_pairs` extractor anchors on `\b{decl_name}\s*\[...\]\s*=\s*` -- a name-exact, word-boundary-anchored pattern -- so `EEPROM_SDP_ENABLE` (a distinct identifier) does not collide with the `EEPROM_SDP_DISABLE` search the module performs. No new parity leg was added for the enable table; that is Plan 119-06's explicit scope.

## Task Commits

Each task was committed atomically inside its own submodule:

1. **Task 1: Add EEPROM_SDP_ENABLE[3], factor the timed-emit helper, and write the two standalone SDP ops** (`firestarter/`) -- `bedb544` (feat)
2. **Task 2: Wire the command entry points and the loop() case arms** (`firestarter/`) -- `308d198` (feat)
3. **Task 3: Repair check_no_log_in_sdp_window.py's emit anchor, its pytest and its fixture** (`firestarter_app/`) -- `ab5dbe6` (feat)

**Plan metadata:** committed alongside this SUMMARY (docs, meta commit staging both gitlinks + SUMMARY.md).

## Files Created/Modified

- `firestarter/src/proms/eeprom_28c.cpp` -- `EEPROM_SDP_ENABLE[3]`; `eeprom28c_emit_sdp_sequence_timed`; `eeprom28c_sdp_unlock_execute`/`eeprom28c_sdp_lock_execute`; `configure_eeprom28c`'s two new arms and declined-`default:` comment; `eeprom28c_write_init`'s unlock branch rewired to the helper
- `firestarter/src/eprom_operations.cpp` -- `eprom_sdp_unlock`/`eprom_sdp_lock`
- `firestarter/include/eprom_operations.h` -- their declarations
- `firestarter/src/firestarter.cpp` -- two new `loop()` case arms with the LOCK-02-corrected-claim comment
- `firestarter_app/tools/check_no_log_in_sdp_window.py` -- appended emit anchor, by-design-helper comment, two tripwire notes

## Decisions Made

See `key-decisions` in frontmatter for the seven load-bearing ones (table shape/rationale, helper factoring, no-`default:` arm, two-functions-not-one discretion, entry-point omissions, LOCK-02's corrected claim, append-only gate repair). All match the plan's `must_haves.truths`/`prohibitions` verbatim -- none required deviation from the plan's explicit instructions.

## Deviations from Plan

None -- plan executed exactly as written, including the deliberate criterion-5 comment-not-header-edit deviation the plan itself names as expected (recorded in `EEPROM_SDP_ENABLE`'s comment, item 5).

## Issues Encountered

One process note, not a plan deviation: during Task 2's flash-delta investigation, `git stash -u`/`git stash pop` was used transiently to compare Task-1-only build output against Task-1+2 output. This is prohibited by the destructive-git-operations rule (the stash list is shared across worktrees/sessions) -- the stash was popped immediately (the only entry created this session, verified as `stash@{0}` before popping) and all Task 2 changes were confirmed intact afterward via `git diff --stat` and `grep`. No work was lost and no other session's stash entries (stash@{1} through stash@{10}, all pre-existing) were touched. Recorded here so this practice is not repeated.

The same pre-existing untracked/modified `firestarter_app` files noted in prior plans' SUMMARYs (`.gitignore` local edit, `.coverage`, `.planning/config.json`, `SECURITY.md`, `doc/lockable-proms.md`, `write_test_port.sh`) remain present and unrelated to this plan's scope -- confirmed unchanged by `git status --short` before and after, out of scope per the scope boundary rule.

## User Setup Required

None -- no external service configuration required.

## Known Stubs

None. This plan lands firmware operations and their host-gate repair -- no UI or data-rendering path is affected. `CMD_SDP_LOCK` is unreachable from the shipped CLI this phase (`dev sdp` is Phase 120, D-17), which is a deliberate scope boundary (T-119-04-HWREACH, disposition "transfer"), not a stub.

## Requirement Status

**Per plan instruction, NO requirement rows were changed.** This plan's frontmatter lists `LOCK-01, LOCK-02, LOCK-05` and closes **none** of them:
- **LOCK-01 stays OPEN** until Plan 119-05 proves the emitted stream against the four dump-authored `SDP_FIXED_LOCK_*` goldens.
- **LOCK-02 stays OPEN** until Plan 119-07's dispatch proofs (the op-layer NULL-`main` guard and full cmd x protocol matrix).
- **LOCK-05 stays OPEN** until Plan 119-06's three-way identity + distinctness guard.

`REQUIREMENTS.md` was not touched (verified via `git status --short` in the meta repo before this plan's meta commit -- no diff against that file).

## Next Phase Readiness

- `EEPROM_SDP_ENABLE[3]` and the shared helper are ready for Plan 119-05's golden-stream assertions and Plan 119-06's three-way identity/distinctness guard.
- `cmd 9`/`cmd 10` are fully dispatchable in firmware; Plan 119-07 still owns the generic op-layer refusal for `CMD_ERASE`/`CMD_CHECK_CHIP_ID` on this protocol and the full cmd x protocol matrix.
- Leonardo flash headroom for LOCK-06's later arithmetic: **2718 B free** (was 2980 B at this plan's start; this plan spent 262 B).
- `check_no_log_in_sdp_window.py`'s new baseline (emitter 298-314, poll 348-361) is the reference for any future gate-range assertion.
- No blockers for Plan 119-05.

---
*Phase: 119-lock-sdp-enable-command-surface-fw-half*
*Completed: 2026-07-28*

## Self-Check: PASSED

- FOUND: `firestarter/src/proms/eeprom_28c.cpp`
- FOUND: `firestarter_app/tools/check_no_log_in_sdp_window.py`
- FOUND: `bedb544` (Task 1 commit, firestarter submodule)
- FOUND: `308d198` (Task 2 commit, firestarter submodule)
- FOUND: `ab5dbe6` (Task 3 commit, firestarter_app submodule)
