---
phase: 119-lock-sdp-enable-command-surface-fw-half
plan: "07"
subsystem: firmware-sdp-lock
tags: [firmware, firestarter_app, sdp, at28c, eeprom28c, native-tests, unity, platformio, dispatch]

# Dependency graph
requires:
  - phase: 119-lock-sdp-enable-command-surface-fw-half
    plan: "04"
    provides: "CMD_SDP_UNLOCK/CMD_SDP_LOCK wired into configure_eeprom28c with no default: arm added"
  - phase: 119-lock-sdp-enable-command-surface-fw-half
    plan: "06"
    provides: "LOCK-05 closed (three-way AA-55-A0 identity/distinctness); LOCK-02 advanced but left open"
provides:
  - "[env:native] and [env:native_nodevtools] both widened with +<operation_utils.cpp>, in lockstep -- resolves RESEARCH Open Question 1 as option (a): the NULL-main guard and the full cmd x protocol matrix are now machine-checked, not prose"
  - "op_execute_stateful_operation's NULL-main fall-through now emits MSG_ERR_NOT_SUPPORTED + RESPONSE_CODE_ERROR instead of a silent phantom-success return false (D-06/D-07's single generic op-layer guard)"
  - "Six table-driven case groups in test_dispatch/test_configure_memory.cpp enumerating the complete command-by-protocol matrix (LOCK-04's positive invariant, fail-closed claim, LOCK-02's dispatch half, DEVTEST-01's 0x0D gaps, the SRAM cells, the unchanged not-implemented path)"
  - "Cases 24/25 in test_eeprom28c_sdp/test_eeprom28c_sdp.cpp proving the refusal frame itself and CMD_ERASE-on-0x0D's DEVTEST-01 firmware-half fix at the wiring level"
  - "LOCK-04 Complete (mechanism-corrected, intent-satisfied) and LOCK-02 Complete in REQUIREMENTS.md"
affects: [119-09, 119-10, 121]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "A generic op-layer NULL-callback guard closes a whole phantom-success class in one site, rather than per-handler default: arms that would each have to be hand-written not to swallow pre-set generic mains"
    - "Table-driven native Unity cases (a struct array + one function that loops and asserts, one RUN_TEST) for a matrix that would otherwise require one test function per (cmd, protocol) cell"
    - "A satisfiable native link gap (an AVR-only symbol newly reachable after widening build_src_filter) is resolved with a no-op host stub, not treated as 'genuinely unsatisfiable' -- distinguishing that class from a true ArduinoFake SIGABRT risk"

key-files:
  created: []
  modified:
    - firestarter/platformio.ini
    - firestarter/test/native/avr/_shared/host_stubs_common.inc
    - firestarter/test/native/avr/test_data_input/host_stubs.cpp
    - firestarter/src/operation_utils.cpp
    - firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp
    - firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp
    - .planning/REQUIREMENTS.md

key-decisions:
  - "Option (a) taken for RESEARCH Open Question 1: +<operation_utils.cpp> added to build_src_filter in BOTH [env:native] and [env:native_nodevtools], in lockstep, with a provenance comment naming D-06/D-07. The only fallout was a link error (op_reset_timeout, defined only in firestarter.cpp's AVR-only loop()), not the anticipated ArduinoFake SIGABRT -- resolved with a no-op extern \"C\" stub in the shared host_stubs_common.inc plus test_data_input/host_stubs.cpp's own inline stub set (that suite deliberately does not include the shared .inc). Zero suites aborted on an unmocked millis/delay virtual; the anticipated risk from RESEARCH F-F did not materialize in practice."
  - "The generic refusal lives at operation_utils.cpp's single NULL-main fall-through (D-06), reusing MSG_ERR_NOT_SUPPORTED (0xA5, already eprom_erase's FLAG_CAN_ERASE refusal id) -- no new catalog id. The refusal's comment records all five required items verbatim (the phantom-success mechanism, D-06's single-site rationale with both rejected alternatives priced, why read/write/verify can never be NULL-main plus LOCK-04's mechanism correction, the blast radius including the six structurally-excluded commands and the unchanged configure_not_implemented protocols, and the _SRAM_PROTO_IDS keep-disposition for Phase 120)."
  - "No default: arm was added to configure_eeprom28c or any other configure_* handler; configure_memory gained no protocol check -- both explicit MUST-NOTs honored."
  - "test_configure_memory.cpp's six case groups are table-driven (one protocol_family_row_t array, one function per group that loops and asserts) except case group 5 (SRAM), which tests each of the four SRAM protocol ids individually since configure_sram is the one handler with zero per-command logic to diverge on -- exactly the kind of regression this sweep exists to catch."
  - "Case 25 proves DEVTEST-01's firmware half by calling op_execute_simple_operation directly rather than eprom_erase() itself, because eprom_erase lives in src/eprom_operations.cpp, an AVR-only TU still excluded from build_src_filter (Task 1 widened the filter with operation_utils.cpp only, per the plan's explicit scope) -- this is the exact op-layer function eprom_erase's body delegates to, so the proof is at the wiring level, deliberately bypassing eprom_erase's own separate, unrelated FLAG_CAN_ERASE precondition check to isolate this task's guard alone."
  - "LOCK-04's REQUIREMENTS.md row is marked Complete with a mechanism-corrected, intent-satisfied parenthetical naming D-05's disproof and D-06's guard; LOCK-04's own requirement wording is byte-unchanged, per the plan's explicit prohibition. LOCK-02's row is marked Complete with the dispatch-proof plans (119-04, 119-07) named in its parenthetical. DEVTEST-01 and LOCK-06 are left Pending; LOCK-01/03/05 are left Complete, untouched."

requirements-completed: [LOCK-04, LOCK-02]

coverage:
  - id: D1
    description: "RESEARCH Open Question 1 resolved: option (a) taken -- both native envs widened with +<operation_utils.cpp> in lockstep, with a satisfiable link gap (op_reset_timeout) stubbed rather than falling back to option (b)"
    requirement: LOCK-04
    verification:
      - kind: unit
        ref: "pio test -e native and -e native_nodevtools -- both 129/129 across 17/17 suites after Task 1 (zero suites added, zero SIGABRT)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The single generic NULL-main refusal at operation_utils.cpp: LOG_ERROR_ID(MSG_ERR_NOT_SUPPORTED) + response_code = RESPONSE_CODE_ERROR + return false, replacing the bare return false phantom-success fall-through; no new catalog id, no default: arm added anywhere"
    requirement: LOCK-04
    verification:
      - kind: unit
        ref: "grep -c MSG_ERR_NOT_SUPPORTED src/operation_utils.cpp -- 3 (LOG_ERROR_ID call site plus two comment references); pio test -e native -- 129/129 (0 pre-existing cases moved, since no suite drove the op layer with a NULL main before Task 1)"
        status: pass
      - kind: unit
        ref: "pio run -- 3/3 SUCCESS, flash delta +18 B on all three boards (Leonardo 25954->25972, Uno 23814->23832, uno328pb 23858->23876)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Case groups 1-6 in test_configure_memory.cpp enumerate the complete command-by-protocol matrix: read/write/verify never-NULL across every protocol family; SDP cmds NULL-main for every non-0x0D protocol; SDP cmds non-NULL-main with NULL init/end on 0x0D; CMD_ERASE/CMD_CHECK_CHIP_ID NULL-main on 0x0D (DEVTEST-01); the SRAM group's three newly-refused cells; the unchanged not-implemented path"
    requirement: LOCK-02
    verification:
      - kind: unit
        ref: "pio test -e native -f \"*test_dispatch*\" -- 22/22 (was 16/16, +6 new case-group functions); pio test -e native_nodevtools -- same suite green"
        status: pass
    human_judgment: false
  - id: D4
    description: "Cases 24/25 in test_eeprom28c_sdp.cpp: the refusal frame itself (NULL main -> MSG_ERR_NOT_SUPPORTED + RESPONSE_CODE_ERROR + false, driven through the real op_execute_stateful_operation) and CMD_ERASE on 0x0D refused end to end through op_execute_simple_operation (DEVTEST-01's firmware half, wiring-level proof)"
    requirement: LOCK-02
    verification:
      - kind: unit
        ref: "pio test -e native -f \"*test_eeprom28c_sdp*\" -- 25/25 (was 23/23, +2 new cases)"
        status: pass
    human_judgment: false
  - id: D5
    description: "Full non-regression sweep: both native envs 137/137 across 17 suites (was 129/129); pio run 3/3 SUCCESS, flash unchanged from Task 2's 25972/23832/23876 (Task 3 is test-only); the five test_val_* stream suites green with no golden regenerated; CLAUDE.md's dispatch-order table still matches memory.cpp; all four firestarter_app host gates exit 0; 30/30 across the six named host-gate pytest modules; firestarter_app working tree unchanged"
    verification:
      - kind: unit
        ref: "pio test -e native / -e native_nodevtools -- 137/137 across 17 suites, both envs"
        status: pass
      - kind: unit
        ref: "pio run -- 3/3 SUCCESS (Leonardo 25972/28672, unchanged from Task 2)"
        status: pass
      - kind: unit
        ref: "check_no_log_in_sdp_window.py / check_dispatch.py / check_is_memory_cmd_no_ifdef.py / gen_sdp_bus_config.py --check -- all exit 0"
        status: pass
      - kind: unit
        ref: "python3 -m pytest tests/test_sdp_table_parity.py tests/test_check_no_log_in_sdp_window.py tests/test_check_is_memory_cmd_no_ifdef.py tests/test_sdp_bus_config_drift.py tests/test_revision_constants_parity.py tests/test_dispatch_mirror.py -q -- 30 passed"
        status: pass
    human_judgment: false
  - id: D6
    description: "LOCK-04 and LOCK-02 marked Complete in REQUIREMENTS.md (LOCK-04's parenthetical reads mechanism-corrected, intent-satisfied; LOCK-04's own wording byte-unchanged); DEVTEST-01 left Pending (host half is Phase 121); LOCK-06 left Pending; LOCK-01/03/05 left Complete, untouched"
    verification:
      - kind: unit
        ref: "git diff .planning/REQUIREMENTS.md -- only LOCK-02 and LOCK-04's checkbox+parenthetical and their traceability-table rows changed"
        status: pass
    human_judgment: false

duration: ~25min
completed: 2026-07-28
status: complete
---

# Phase 119 Plan 07: Generic NULL-Main Refusal + Complete cmd x Protocol Matrix Summary

**Closed the whole phantom-success class with one guard at `operation_utils.cpp`'s NULL-main fall-through (`MSG_ERR_NOT_SUPPORTED` + `RESPONSE_CODE_ERROR` instead of a silent `return false`), made it machine-checked rather than prose by widening both native envs' `build_src_filter` to link `operation_utils.cpp`, and enumerated the complete command-by-protocol matrix as native Unity cases — closing LOCK-04 (mechanism-corrected, intent-satisfied) and LOCK-02, with DEVTEST-01's firmware half proven end to end.**

## Performance

- **Duration:** ~25 min
- **Completed:** 2026-07-28
- **Tasks:** 3/3
- **Files modified:** 7 (6 firmware files, 1 meta file)

## Accomplishments

- **Task 1 (Open Question 1, resolved as option (a)):** Widened `[env:native]` and `[env:native_nodevtools]`'s `build_src_filter` with `+<operation_utils.cpp>`, in lockstep, with a provenance comment naming D-06/D-07. The anticipated risk (RESEARCH F-F: ArduinoFake `SIGABRT` on unmocked `millis`/`delay` in the 12 suites that don't mock them) **did not materialize** — zero suites aborted. The actual fallout was a link error RESEARCH did not anticipate: `op_reset_timeout()` is defined only in `firestarter.cpp` (loop()'s AVR-only command-timeout watchdog), which neither native env compiles. This is a **satisfiable** link gap, not a "genuinely unsatisfiable" one (the plan's stated bar for falling back to option (b)) — resolved with a no-op `extern "C"` stub, once in the shared `_shared/host_stubs_common.inc` (covers 16 of 17 suites) and once inline in `test_data_input/host_stubs.cpp` (which deliberately does not include the shared `.inc`, per its own file-header contract, so it needed its own copy). Same no-op contract as every other stub in both files; no suite was weakened. Verified: `pio test -e native` and `-e native_nodevtools` both 129/129 across 17/17 suites (this task adds no test case); `pio run` 3/3 SUCCESS, Leonardo flash unchanged at 25954/28672 (a native-only filter change spends zero production flash, as predicted).
- **Task 2 (the generic refusal):** Replaced the bare `return false` fall-through in `op_execute_stateful_operation` with `LOG_ERROR_ID(MSG_ERR_NOT_SUPPORTED); handle->response_code = RESPONSE_CODE_ERROR; return false;`, reusing the existing `0xA5` id (already `eprom_erase`'s `FLAG_CAN_ERASE` refusal) — no new catalog entry. The `return false` semantics are unchanged: every `eprom_*` caller still inverts it, so the command still reports finished and `command_done()` still runs; what changes is that an error frame is now emitted instead of silence. The comment on this refusal records all five items the plan requires (the phantom-success mechanism, D-06's single-site rationale with both rejected alternatives priced, why read/write/verify can never be NULL-main plus LOCK-04's mechanism correction, the blast radius including the six structurally-excluded non-memory commands and the unchanged `configure_not_implemented` protocols, and the `_SRAM_PROTO_IDS` keep-disposition for Phase 120). No `default:` arm was added to `configure_eeprom28c` or any other `configure_*` handler; `configure_memory` gained no protocol check. **Zero pre-existing test cases moved** — no suite drove the op layer with a NULL main before Task 1 widened `build_src_filter`, so there was no old silent-OK expectation to break. Flash delta **+18 B on all three boards** (Leonardo 25954→25972, Uno 23814→23832, uno328pb 23858→23876) — a `LOG_ERROR_ID` call plus a store, exactly the small attributable increment the plan predicted.
- **Task 3 (the matrix, enumerated):** Added six table-driven case groups to `test_dispatch/test_configure_memory.cpp` and two wiring-level cases to `test_eeprom28c_sdp/test_eeprom28c_sdp.cpp`, both possible only because Task 1 widened `build_src_filter`. See the full matrix below. `pio test -e native`/`-e native_nodevtools` both 137/137 across 17/17 suites (+8 new cases: 6 case-group functions + cases 24/25, 0 pre-existing case moved). `pio run` 3/3 SUCCESS, flash unchanged at 25972/23832/23876 (test-only task, zero production flash spent). Marked **LOCK-04 and LOCK-02 Complete** in `REQUIREMENTS.md`.

## The Complete Command-by-Protocol Matrix

`G` = generic pre-set main (`memory.cpp:48-58`), `H` = handler-specific main, `NULL→refused` = this task's new `MSG_ERR_NOT_SUPPORTED` refusal (was a silent `∅`/OK before this plan), `unchanged` = `configure_not_implemented`'s own earlier `RESPONSE_CODE_ERROR`, never touching the op layer at all.

| Protocol(s) | Handler | READ (1) | WRITE (2) | ERASE (3) | BLANK_CHECK (4) | CHIP_ID (5) | VERIFY (6) | SDP_UNLOCK (9) | SDP_LOCK (10) |
|---|---|---|---|---|---|---|---|---|---|
| `0x07 0x08 0x0B` | `configure_eprom` | G | H | H | H | H | G | **NULL→refused** | **NULL→refused** |
| **`0x0D`** | `configure_eeprom28c` | G | H | **NULL→refused ⚠ DEVTEST-01** | H | **NULL→refused (upstream-gated, see below)** | G | **H (new, LOCK-02)** | **H (new, LOCK-02)** |
| `0x10` | `configure_flash_intel` | G | H | H | H | H | G | **NULL→refused** | **NULL→refused** |
| `0x06` | `configure_flash_nor_unlock` | G | H | H | H | H | G | **NULL→refused** | **NULL→refused** |
| `0x05 0x35 0x39` | `configure_flash_5v_page` | G | H | H | H | H | G | **NULL→refused** | **NULL→refused** |
| `0x0E 0x27 0x28 0x29` | `configure_sram` (empty body) | G | G | **NULL→refused** | **NULL→refused (see below)** | **NULL→refused (upstream-gated)** | G | **NULL→refused** | **NULL→refused** |
| `0x11 0x2A-0x2C 0x34 0` | `configure_not_implemented` | unchanged | unchanged | unchanged | unchanged | unchanged | unchanged | unchanged | unchanged |

**Cells with a qualification, not over-claimed:**
- **`0x0D` + `CMD_CHECK_CHIP_ID`** and **SRAM + `CMD_CHECK_CHIP_ID`**: also newly refused by this guard, but `eprom_check_chip_id` already refuses earlier with `MSG_ERR_NO_CHIP_ID` when `handle->chip_id == 0`, and TRACE-05 pinned `chip_id_check: false` across all 84 `algorithm == 13` entries — so in practice the host never sends a non-zero chip id for `0x0D`, and this cell is already refused upstream. Case group 4 records this explicitly; it is not the primary mitigation.
- **SRAM + `CMD_BLANK_CHECK`**: also newly refused at this guard, but the host's `_SRAM_PROTO_IDS` workaround in `firestarter_app/firestarter/eprom_operations.py` short-circuits `check_eprom_blank` **before any firmware command is issued**, so this guard is not reachable from that call path. It does **not** become dead code — it fires earlier and gives a materially better user-facing message. Correct Phase 120 disposition: **keep**, not delete. `firestarter_app` was not modified in this plan.
- **`0x0D` / SRAM + `SDP_UNLOCK` / `SDP_LOCK`**: this is where D-06's "provably total" claim earns its keep — every non-`0x0D` protocol family is refused by the SAME one guard, with no per-handler maintenance, which is exactly LOCK-04's fail-closed intent (not its literal `default:`-arm mechanism, which D-05 disproved).

**Cross-family byte-identity confirmed, not assumed:** `test_val_eprom`, `test_val_nor_unlock`, `test_val_5v_page`, `test_val_flash_intel` and `test_val_sram` are all green with no golden regenerated — the matrix shows why: no cell any of those five stream suites exercises changes from `H`/`G` to anything else; the change is purely in the `NULL→refused` cells, none of which emitted bus traffic before this plan.

## RESEARCH Open Question 1 — What LOCK-04's and DEVTEST-01's Proofs Rest On

**Option (a) taken.** Both native envs now compile `operation_utils.cpp`, so:
- The single NULL-main refusal (Task 2) is exercised by the **real production function**, not a helper extracted for testability.
- The complete cmd × protocol matrix (Task 3, case groups 1-6) is a **machine-checked enumeration**, driving `configure_memory` and then observing `firestarter_operation_main` — a dispatch-level proof.
- Cases 24/25 additionally drive the **real op layer** (`op_execute_stateful_operation` / `op_execute_simple_operation`) and observe the actual refusal frame (`MSG_ERR_NOT_SUPPORTED` in the captured ids, `RESPONSE_CODE_ERROR`, `false` return) — a **wiring-level** proof, the strongest option RESEARCH offered.
- LOCK-04's and DEVTEST-01's proofs are therefore **tests, not prose.**

**Suite-by-suite evidence:** all 17 suites, both envs, passed on the first attempt after Task 1's `build_src_filter` widening except one link error (`op_reset_timeout`, resolved with a stub — see Task 1 above). Zero suites aborted with `SIGABRT` on an unmocked ArduinoFake virtual; the anticipated 12-suites-don't-mock-`millis`/`delay` risk from RESEARCH F-F did not manifest.

## Task Commits

Each task was committed atomically inside the `firestarter/` submodule:

1. **Task 1: Resolve Open Question 1 as a bounded spike (option (a) taken)** — `9bacb78` (test)
2. **Task 2: Land the single generic NULL-main refusal at the operation layer** — `e9d0577` (fix)
3. **Task 3: Enumerate the command-by-protocol matrix, pin the never-NULL invariant, and prove the cmd 9/10 dispatch** — `52326d5` (test)

**Plan metadata:** committed alongside this SUMMARY (docs, meta commit staging the gitlink + SUMMARY.md + STATE.md + ROADMAP.md + REQUIREMENTS.md).

## Files Created/Modified

- `firestarter/platformio.ini` — `+<operation_utils.cpp>` appended to `build_src_filter` in both `[env:native]` and `[env:native_nodevtools]`, in lockstep, with provenance comments
- `firestarter/test/native/avr/_shared/host_stubs_common.inc` — no-op `op_reset_timeout()` stub (covers 16 of 17 suites)
- `firestarter/test/native/avr/test_data_input/host_stubs.cpp` — its own inline `op_reset_timeout()` stub (doesn't include the shared `.inc`)
- `firestarter/src/operation_utils.cpp` — the generic NULL-main refusal at `op_execute_stateful_operation`'s fall-through, with its five-item load-bearing comment
- `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` — case groups 1-6, table-driven, enumerating the complete cmd × protocol matrix
- `firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp` — cases 24/25, the refusal frame and `CMD_ERASE`-on-`0x0D` proven end to end
- `.planning/REQUIREMENTS.md` — LOCK-04 and LOCK-02 checkboxes + parentheticals + traceability-table rows only

## Decisions Made

See `key-decisions` in frontmatter for the six load-bearing ones (option (a) taken with the satisfiable-link-gap distinction, the refusal's single-site placement and comment contract, the two explicit MUST-NOTs honored, case group 5's per-id testing rationale, case 25's wiring-level mechanism, and the REQUIREMENTS.md marking scope). All are consistent with the plan's `must_haves.truths`/`prohibitions` verbatim.

## Deviations from Plan

**None beyond the plan's own anticipated Task-1 branch point.** RESEARCH anticipated Task 1 might hit an ArduinoFake `SIGABRT` (Pitfall 5) requiring per-suite mock additions, or a "genuinely unsatisfiable" link error requiring fallback to option (b). Neither of those two anticipated outcomes occurred; instead a **third, satisfiable** link error (`op_reset_timeout`) appeared, which the plan's own language ("if it is genuinely unsatisfiable ... go to (b)") implicitly permits resolving when it is not genuinely unsatisfiable. This is documented here as the actual suite-by-suite evidence the plan required, not as a deviation from the plan's explicit instructions — no suite was weakened, `TEST_IGNORE_MESSAGE` appears nowhere, and option (a) was fully achieved with both native envs in lockstep.

## Issues Encountered

None beyond the Task 1 link error described above and resolved the same task.

## User Setup Required

None — no external service configuration required.

## Known Stubs

None. This plan is firmware + native-test-only; `CMD_SDP_LOCK`/`CMD_SDP_UNLOCK` remain unreachable from the shipped CLI this phase (Phase 120 scope), which is a pre-existing, deliberate scope boundary, not a new stub introduced here.

## Requirement Status

**LOCK-04 is Complete (mechanism-corrected, intent-satisfied).** `REQUIREMENTS.md`'s parenthetical names D-05's disproof (a literal `default:` arm in `configure_eeprom28c` would refuse read/verify on all 84 `0x0D` chips, and could never refuse another protocol anyway) and D-06's guard (the single generic op-layer refusal, which this plan lands). LOCK-04's own requirement wording is byte-unchanged, per the plan's explicit prohibition.

**LOCK-02 is Complete.** Its dispatch half (case group 3: non-NULL main, NULL init/end for both new commands on `0x0D`, with RESEARCH F-T's correction recorded) and its wiring proof (cases 24/25) close the requirement Plan 119-04 opened.

**DEVTEST-01 stays Pending** — only its firmware half (`CMD_ERASE` refused on `0x0D`, proven by case group 4 and case 25) lands here; the host half (`OP_ERASE` marked `NA` in the `dev test` sweep) stays Phase 121, and the `REQUIREMENTS.md`/`ROADMAP.md` mapping amendment is Plan 119-09's owned task, not this plan's.

**LOCK-06 stays Pending** (flash headroom judgement is Plan 119-10's task, against the live 2718 B figure from Plan 119-04, not this plan's own +18 B increment in isolation). **LOCK-01, LOCK-03, LOCK-05 remain Complete, untouched.**

## Next Phase Readiness

- LOCK-04 and LOCK-02 are both closed; the phantom-success class is closed generically for every protocol and every command, not just SDP's corner of it.
- DEVTEST-01's firmware half is done and recorded — Plan 119-09 can now amend Phase 121's ROADMAP scope and `REQUIREMENTS.md` mapping with the firmware-side proof already in hand.
- Leonardo flash headroom for LOCK-06's arithmetic: this plan spent **+18 B** on top of Plan 119-04's **2718 B free** baseline, landing at **2700 B free** (Leonardo 25972/28672) — Plan 119-10 judges the full-phase delta against the live figure, not this plan's increment alone.
- Both native envs stay in lockstep (`build_src_filter` identical), so the DEV_TOOLS-invariance proof continues to cover the op layer in future plans.
- No blockers for Plan 119-08.

---
*Phase: 119-lock-sdp-enable-command-surface-fw-half*
*Completed: 2026-07-28*

## Self-Check: PASSED

- FOUND: `firestarter/platformio.ini`
- FOUND: `firestarter/test/native/avr/_shared/host_stubs_common.inc`
- FOUND: `firestarter/test/native/avr/test_data_input/host_stubs.cpp`
- FOUND: `firestarter/src/operation_utils.cpp`
- FOUND: `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp`
- FOUND: `firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp`
- FOUND: `9bacb78` (Task 1 commit, firestarter submodule)
- FOUND: `e9d0577` (Task 2 commit, firestarter submodule)
- FOUND: `52326d5` (Task 3 commit, firestarter submodule)
- FOUND: `.planning/REQUIREMENTS.md` LOCK-04/LOCK-02 updated
