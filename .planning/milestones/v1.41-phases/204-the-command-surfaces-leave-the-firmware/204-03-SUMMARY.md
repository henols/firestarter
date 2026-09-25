---
phase: 204-the-command-surfaces-leave-the-firmware
plan: 03

subsystem: firmware-protocol
tags: [protocol-retirement, dispatch, source-contract-gate, golden-rederive, blank-check, avr]

requires:
  - phase: 204-01
    provides: "ordinal 6 (CMD_VERIFY / COMMAND_VERIFY) retired end to end; the reserved-ordinal note shape and the gate re-anchor pattern this plan repeats for ordinal 4"
  - phase: 204-02
    provides: "the eighth source-contract gate (verify-survival) and the native id-asserting suite, both proven to fail on the right violations before this sweep began"
provides:
  - "ordinal 4 (CMD_BLANK_CHECK / COMMAND_BLANK_CHECK) fully removed from the firmware and the host command ladders, in a lockstep commit pair"
  - "a second reserved-ordinal note at the ordinal-4 gap on both ladders, mirroring ordinal 6's shape"
  - "the region-scoped census gate re-anchored from six whole-device function-pointer assignments to one"
  - "the branch-inventory golden re-derived by its own extractor, positionally verified field by field, landed with src/proms/eprom.cpp in one commit"
  - "four new absence legs on the verify-survival source-contract gate (FWCMD-01/FWCMD-03), each RED observed against the pre-deletion tree"
  - "the forwarding-count and native admission-count gates re-anchored from eight to seven"
affects: [204-04-remaining-scope, 204-05-bench-matrix, 205-preflights-leave, 207-release-and-docs]

actuals:
  tokens: 25800
  tasks: 3
  commits: 7

tech-stack:
  added: []
  patterns:
    - "Second reserved-ordinal note at its own gate, matching the first note's shape verbatim on both ladders -- direct repeat of plan 01's pattern."
    - "Behaviour-preserving collapse landed alone, in its own commit, isolated from every reference-deletion commit that follows it -- the one commit in the sweep that changes behaviour rather than removing a dead reference."
    - "Golden re-derivation proven safe via positional (predicate, keyed_on, tier) equality BEFORE line values are trusted, never a dict keyed on that triple (a recorded collision trap)."

key-files:
  modified:
    - firestarter_fw/src/proms/memory.cpp
    - firestarter_fw/src/operation_utils.cpp
    - firestarter_fw/src/proms/eprom.cpp
    - firestarter_fw/src/proms/flash_nor_unlock.cpp
    - firestarter_fw/src/proms/flash_intel.cpp
    - firestarter_fw/src/proms/flash_5v_page.cpp
    - firestarter_fw/src/proms/eeprom_28c.cpp
    - firestarter_fw/tests/test_blank_check_region_source_contract.py
    - firestarter_fw/tests/test_protocol_branch_inventory.py
    - firestarter_fw/tests/golden/protocol_branch_inventory.json
    - firestarter_fw/test/native/avr/test_val_eprom/test_val_eprom.cpp
    - firestarter_fw/test/native/avr/test_val_nor_unlock/test_val_nor_unlock.cpp
    - firestarter_fw/test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp
    - firestarter_fw/include/firestarter.h
    - firestarter_fw/include/eprom_operations.h
    - firestarter_fw/include/memory_utils.h
    - firestarter_fw/src/firestarter.cpp
    - firestarter_fw/src/eprom_operations.cpp
    - firestarter_fw/tests/test_verify_survival_source_contract.py
    - firestarter_fw/tests/test_boolean_convention_source_contract_v133.py
    - firestarter_fw/test/native/avr/test_cmd_admission/test_cmd_admission.cpp
    - firestarter_fw/test/native/avr/test_dispatch/test_configure_memory.cpp
    - firestarter_app/firestarter/constants.py
    - firestarter_app/firestarter/eprom_operations.py
    - firestarter_app/tests/test_eprom_operations.py

key-decisions:
  - "Left FWCMD-01/02/03 unmarked in REQUIREMENTS.md per the orchestrator's explicit wave-context instruction, rather than independently re-deriving readiness via requirements.ready-ids -- FWCMD-02/03 are also declared by 204-04 (not yet run)."
  - "A stale literal CMD_VERIFY reference in memory_utils.h (a plan-01 leftover, caught by this plan's own verify script since that file sits on the <verify> scan list though not the prose <files> list) landed as a fourth, small, clearly-documented firmware commit rather than being folded into the sweep via git commit --amend -- the meta gitlink already referenced the pre-fix SHA, and rewriting local history to preserve a literal 'three commits' count was judged riskier than an honest fourth green commit."
  - "The plan's own environment-facts predicted Task 3 would delete exactly one native test case; measured, it deleted zero -- the SRAM case-group's blank-check assertion (Fork B) was a sub-assertion inside an existing RUN_TEST function, not its own case. The fails_when threshold (more than one below baseline) was not tripped."
  - "eprom_lock_status's two shape-citation comments, which named the deleted eprom_blank_check wrapper as the thing they mirrored, were re-pointed at eprom_check_chip_id -- the closest surviving single-step wrapper that also carries a LOG_DEBUG_ID_SUB line, preserving the 'but deliberately WITHOUT one' contrast the comments make."

requirements-completed: []

coverage:
  - id: D1
    description: "Ordinal 4 is absent from every one of its 11 firmware sites (the #define, the is_memory_cmd arm, the dispatch switch arm, the eprom_blank_check wrapper and its declaration, and all five protocol configure_* arms)"
    requirement: FWCMD-01
    verification:
      - kind: unit
        ref: "command: python3 source-presence assertion over 12 firmware files, run after each of the three tasks (see Task Commits section)"
        status: pass
      - kind: unit
        ref: "firestarter_fw/tests/test_verify_survival_source_contract.py::test_neither_retired_ordinal_appears_in_the_dispatch_switch, ::test_neither_retired_ordinal_appears_in_the_admission_predicate, ::test_no_protocol_handler_configures_a_retired_ordinal"
        status: pass
    human_judgment: false
  - id: D2
    description: "The two command-keyed branches in mem_util_blank_check_region and the whole emit-and-ack block in _single_step_operation_callback are collapsed to the direct-emit arm write-init and erase-end already took, proven behaviour-preserving (no gate changed verdict)"
    requirement: FWCMD-01
    verification:
      - kind: unit
        ref: "command: pio test -e native -f *test_val_eprom* (chunking/cursor-restore case), pio test -e native full suite, pio test -e native_nodevtools, pytest tests/ -- all green, zero verdict changes, immediately after Task 1's commit"
        status: pass
    human_judgment: false
  - id: D3
    description: "mem_util_blank_check, mem_util_blank_check_region, blank_check_saved_address and BLANK_CHECK_CHUNK_SIZE all still exist and are still reached from write-init and erase-end"
    requirement: FWCMD-01
    verification:
      - kind: unit
        ref: "command: python3 source-presence assertion for all four names in src/proms/memory.cpp, and for mem_util_blank_check surviving in src/proms/eprom.cpp's erase-end assignment, after each task"
        status: pass
    human_judgment: false
  - id: D4
    description: "Ordinal 4 is absent from the host: constants.py defines no COMMAND_BLANK_CHECK and COMMAND_NAMES carries no key 4, landed as a commit pair with the firmware define"
    requirement: FWCMD-03
    verification:
      - kind: unit
        ref: "command: .venv311/bin/python constants-presence assertion (Task 3's host verify leg); firestarter_app@2a17fd7 paired with firestarter_fw@305b2f4/fa7603c, meta gitlink@40b58f34"
        status: pass
    human_judgment: false
  - id: D5
    description: "Both ladders carry a reserved-ordinal note at the ordinal-4 gap, naming the release and the never-reuse reason, matching ordinal 6's note shape; a committed test fails if either firmware note or firmware define reappears"
    requirement: FWCMD-03
    verification:
      - kind: unit
        ref: "firestarter_fw/tests/test_verify_survival_source_contract.py::test_both_reserved_ordinal_gaps_carry_a_recorded_reason; firestarter_app/tests/test_eprom_operations.py::TestOrdinalsNeverSentByVerifyOrBlank::test_neither_retired_ordinal_is_defined_or_named_on_the_host_ladder"
        status: pass
    human_judgment: false
  - id: D6
    description: "The source-contract gate gained four absence legs (dispatch switch, admission predicate, all five protocol handlers, reserved-note presence), each SEEN failing against the pre-deletion tree via a planted violation before the sweep landed"
    requirement: FWCMD-01
    verification:
      - kind: unit
        ref: "verbatim RED transcripts captured for all four legs -- see 'RED Evidence' section below; each restored and reverified clean before its commit"
        status: pass
    human_judgment: false
  - id: D7
    description: "The protocol_branch_inventory.json golden was re-derived by the gate module's own extractor, never hand-edited, and diffed field by field against the previous golden keyed on the site line"
    requirement: null
    verification:
      - kind: unit
        ref: "command: python3 positional-diff script (Task 2's golden verify leg) -- 22 sites, zero non-line divergences, 20 sites shifted by exactly -3, protocol-keyed line moved 70->67, counts unchanged 22/1/21"
        status: pass
    human_judgment: false
  - id: D8
    description: "The sweep lands as commits that each leave all four firmware CI legs green, so no bisect lands on a RED tree"
    requirement: null
    verification:
      - kind: unit
        ref: "command: pio test -e native, -e native_nodevtools, pytest tests/ -o addopts=\"\", pio run -- run and green after EACH of the four firmware commits (29daf42, 5f66595, 305b2f4, fa7603c)"
        status: pass
    human_judgment: false
  - id: D9
    description: "The retired ordinal can no longer reach configure_memory at all, so it can no longer reach the VPP check a standalone blank check reaches today -- strictly safer, not merely equally safe"
    requirement: null
    verification:
      - kind: unit
        ref: "structural: is_memory_cmd's admission set no longer includes ordinal 4 (test_admission_count_is_exactly_seven, test_admission_truth_table_over_every_cmd_value); a refused frame falls through firestarter.cpp's default: arm before configure_memory runs"
        status: pass
    human_judgment: false
  - id: D10
    description: "Three re-anchored counts land at one, seven and seven, each as a coordinated edit of constant, function name and docstring census"
    requirement: FWCMD-01
    verification:
      - kind: unit
        ref: "test_exactly_one_whole_device_function_pointer_assignment_and_zero_region_form_ones (census: 6->1); test_the_seven_forwarding_calls_are_present (8->7); test_admission_count_is_exactly_seven (8->7)"
        status: pass
    human_judgment: false

duration: "~45min (from Task 1's first commit 09:49:41Z to Task 3's final gitlink-advance commit 10:32:18Z; includes a host pytest run that ran ~175s and a coverage run that ran several minutes in the background)"
completed: 2026-09-22
status: complete
---

# Phase 204 Plan 3: Ordinal 4 (CMD_BLANK_CHECK) retired end-to-end, mirroring plan 01's ordinal-6 sweep

**Retired the standalone blank-check command's wire ordinal from all 11 firmware sites and the host ladder in a four-commit sweep (three planned, one small Rule-1 follow-up), re-anchoring the region-scoped census gate, the branch-inventory golden, the forwarding-count gate and the native admission suite along the way -- with the blank-check machinery itself (mem_util_blank_check, mem_util_blank_check_region) proven to survive intact for write-init and erase-end.**

## Performance

- **Duration:** ~45 min wall-clock (Task 1 commit 09:49:41Z -> final gitlink commit 10:32:18Z)
- **Started:** 2026-09-22T09:49:41Z
- **Completed:** 2026-09-22T10:32:18Z
- **Tasks:** 3 automated tasks, no checkpoints
- **Files modified:** 22 across two repositories (19 firmware, 3 host) plus 2 meta gitlink commits and this SUMMARY

## Accomplishments

- Collapsed `mem_util_blank_check_region`'s two command-keyed branches (the deferred not-blank stash, the suppressed progress emit) and `_single_step_operation_callback`'s whole deferred emit-and-ack block to the direct-emit arm the surviving write-init and erase-end callers already took -- proven behaviour-preserving: all four firmware CI legs green immediately after, zero gate verdict changes.
- Deleted the blank-check arm from all five protocol configure handlers (eprom, NOR-unlock, Intel flash, 5V-page flash, 28C parallel); re-anchored the region-scoped census gate from six whole-device function-pointer assignments to one; re-derived the branch-inventory golden with its own extractor, positionally verified field by field against the previous golden (22 sites, only line values and the eprom.cpp checksum moved), landed in the same commit as the source it describes.
- Deleted the `#define`, the `is_memory_cmd` arm, the dispatch switch arm, and the `eprom_blank_check` wrapper plus its declaration; extended the reserved-ordinal note to a second gate matching ordinal 6's shape; re-pointed two stale shape-citation comments at a surviving wrapper.
- Extended `test_verify_survival_source_contract.py` with four new absence legs (dispatch switch, admission predicate, all five protocol handlers, reserved-note presence) -- each RED **observed** against the pre-deletion tree via a planted violation, then restored clean before its commit.
- Re-anchored the forwarding-count gate and the native admission suite from eight to seven (constant, function name, docstring census, all three, in each); deleted the SRAM case-group's stale blank-check assertion (Fork B) whose own KEEP disposition no longer applied.
- Retired `COMMAND_BLANK_CHECK` from the host ladder in a paired commit; repaired four stale comments naming the retired ordinal, including the SRAM short-circuit's exemption rationale (now true of every protocol handler, not only `configure_sram`); added the host-side half of FWCMD-03's gate.
- Found and fixed one Rule-1 deviation via the task's own verify script: a stale literal ordinal reference in `memory_utils.h` left over from plan 01.

## Task Commits

This plan spans two repositories; commits are grouped by task, plus the meta repository's gitlink advances.

1. **Task 1: Collapse the two command-keyed branches and the deferred emit block** -- firmware `29daf42` (refactor)
2. **Task 2: The five protocol handlers, the census gate, and the golden re-derived in the same commit** -- firmware `5f66595` (feat)
3. **Task 3: Both ladders lose ordinal 4, in one lockstep commit pair, with the absence gated** -- firmware `305b2f4` (feat), host `2a17fd7` (feat), meta gitlink advance `85e49226` (chore)
4. **Deviation fix (Rule 1): stale literal in memory_utils.h** -- firmware `fa7603c` (docs), meta gitlink advance `40b58f34` (chore)

**Plan metadata:** this SUMMARY's own commit, made after this file.

_Total: 4 commits in `firestarter_fw` (measured: `git rev-list --count 65e8d20..fa7603c` = 4), 1 commit in `firestarter_app`, 2 gitlink-advance commits in the meta repo. `plan_head_before` (meta): `01e1ded7`._

## Files Created/Modified

- `firestarter_fw/src/proms/memory.cpp`, `firestarter_fw/src/operation_utils.cpp` -- the behaviour-preserving collapse (Task 1).
- `firestarter_fw/src/proms/eprom.cpp`, `flash_nor_unlock.cpp`, `flash_intel.cpp`, `flash_5v_page.cpp`, `eeprom_28c.cpp` -- the five configure-handler arm deletions (Task 2).
- `firestarter_fw/tests/test_blank_check_region_source_contract.py` -- census re-anchored 6->1 (Task 2).
- `firestarter_fw/tests/test_protocol_branch_inventory.py`, `tests/golden/protocol_branch_inventory.json` -- pinned line re-anchored 70->67; golden re-derived (Task 2).
- `firestarter_fw/test/native/avr/test_val_eprom/test_val_eprom.cpp` -- chunking test re-keyed to a direct function-pointer assignment (Fork C, Task 2); the remaining bare command-field assignment re-keyed to `CMD_READ` (Task 3).
- `firestarter_fw/test/native/avr/test_val_nor_unlock/test_val_nor_unlock.cpp`, `test_val_eeprom28c/test_val_eeprom28c.cpp` -- the two no-VPP tests deleted (Fork D, Task 2).
- `firestarter_fw/include/firestarter.h` -- the `#define` and admission arm deleted; second reserved-ordinal note added; predicate comment corrected to seven (Task 3).
- `firestarter_fw/include/eprom_operations.h`, `src/eprom_operations.cpp` -- the wrapper and declaration deleted; two shape-citation comments re-pointed (Task 3).
- `firestarter_fw/src/firestarter.cpp` -- the dispatch arm deleted; the third shape citation re-pointed; default arm byte-identical (Task 3).
- `firestarter_fw/include/memory_utils.h` -- stale literal ordinal reference repaired (deviation fix).
- `firestarter_fw/tests/test_verify_survival_source_contract.py` -- four new absence legs added (Task 3).
- `firestarter_fw/tests/test_boolean_convention_source_contract_v133.py` -- forwarding-count census re-anchored 8->7 (Task 3).
- `firestarter_fw/test/native/avr/test_cmd_admission/test_cmd_admission.cpp` -- admission census re-anchored 8->7 (Task 3).
- `firestarter_fw/test/native/avr/test_dispatch/test_configure_memory.cpp` -- SRAM case-group's blank-check assertion deleted (Fork B, Task 3).
- `firestarter_app/firestarter/constants.py` -- `COMMAND_BLANK_CHECK` and its names-map row deleted; second reserved-ordinal note added (Task 3).
- `firestarter_app/firestarter/eprom_operations.py` -- four stale comments repaired (Task 3).
- `firestarter_app/tests/test_eprom_operations.py` -- one guard test converted to an integer literal; one new host-side reserved-ordinal gate leg added (Task 3).

## RED Evidence

All four new absence legs were planted against the tree AFTER the corresponding source deletion had already landed in this session, so each plant temporarily REINTRODUCED the retired identifier (via a non-comment code insertion -- comment-stripping means a `//`-prefixed plant is invisible to these gates and silently passes, which was itself caught and corrected once during this exercise) to prove the leg fails for the intended reason, then the file was restored via `cp` from a pre-plant copy and re-verified clean (`git diff --stat` empty) before the corresponding commit.

**Leg 1 -- `test_neither_retired_ordinal_appears_in_the_dispatch_switch`.** Planted a `case CMD_BLANK_CHECK:` arm (real code, not a comment) into `src/firestarter.cpp`'s dispatch switch:
```
E           assert 'CMD_BLANK_CHECK' not in '{\n        ...reak;\n    }'
E           'CMD_BLANK_CHECK' is contained here: ...
tests/test_verify_survival_source_contract.py:368: AssertionError
```
Restored; re-ran -- PASSED; `git diff --stat` empty.

**Leg 2 -- `test_neither_retired_ordinal_appears_in_the_admission_predicate`.** Planted a `case CMD_VERIFY:` line into `is_memory_cmd`'s switch body in `include/firestarter.h`:
```
E           assert 'CMD_VERIFY' not in '{\n    swit...e;\n    }\n}'
E           'CMD_VERIFY' is contained here: ...
tests/test_verify_survival_source_contract.py:393: AssertionError
```
Restored; re-ran -- PASSED; `git diff --stat` empty.

**Leg 3 -- `test_no_protocol_handler_configures_a_retired_ordinal`.** Planted `int unused_marker_CMD_BLANK_CHECK_token;` at the end of `src/proms/flash_intel.cpp`:
```
E       AssertionError: found a retired command identifier surviving in a protocol configure handler ...
E         Got:
E         src/proms/flash_intel.cpp: the blank-check command's retired identifier
tests/test_verify_survival_source_contract.py:415: AssertionError
```
Restored; re-ran -- PASSED; no diff (this file already matched its committed Task-2 state).

**Leg 4 -- `test_both_reserved_ordinal_gaps_carry_a_recorded_reason`.** Removed one occurrence of the marker phrase ("retired in 3.1.0") from the ordinal-6 note in `include/firestarter.h`:
```
E       AssertionError: expected the reserved-ordinal marker to appear at least twice in include/firestarter.h (once per retired ordinal), found 1 ...
tests/test_verify_survival_source_contract.py:433: AssertionError
```
Restored; re-ran -- PASSED; `git diff --stat` showed only the plan's own pending edit, no residue.

All four planted violations were observed failing for the intended reason and none was left in the working tree before its corresponding commit.

## Golden Diff Summary (criterion 6)

Re-derived `tests/golden/protocol_branch_inventory.json` with `test_protocol_branch_inventory.py`'s own `_extract_predicates` against the swept `src/proms/eprom.cpp`, run BEFORE staging:

- **Site count:** 22 (unchanged). **Protocol-keyed:** 1 (unchanged). **Other:** 21 (unchanged).
- **Positional field-by-field diff against the previous golden:** zero divergences on `predicate`, `keyed_on` or `tier` across all 22 sites -- verified programmatically before any `line` value was carried forward.
- **Line shift:** 20 of 22 sites shifted by exactly -3 (the three deleted lines of `configure_eprom`'s blank-check arm); the two sites above the cut (the command-dispatch switch at line 45, the `FLAG_SKIP_BLANK_CHECK` check at line 52) are line-identical.
- **Protocol-keyed pinned line:** moved from 70 to 67, matching the extractor's measured output (not the plan's carried-forward guess, though they agreed).
- **Blob checksum:** `src/proms/eprom.cpp`'s recorded `blob_shas` entry updated to `git hash-object`'s output on the working tree before staging; `eprom_params.cpp`'s checksum untouched (that file was not edited).
- **Landed in the same commit as `src/proms/eprom.cpp`** (`5f66595`), confirmed by `git show --name-only` listing both paths.

## Decisions Made

See frontmatter `key-decisions` for the four implementation decisions (REQUIREMENTS.md non-mark per wave-context instruction; the fourth commit vs. amend tradeoff; the measured zero-case-deletion correction to the plan's own prediction; the `eprom_lock_status` shape-citation re-point target).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Repaired a stale literal ordinal reference in `memory_utils.h`**
- **Found during:** Task 3's own final `<verify>` re-run, after the primary sweep commit (`305b2f4`) had already landed
- **Issue:** Task 3's own verify script scans `include/memory_utils.h` for the literal absence of both retired ordinals (it is on that `<verify>` block's file list, though not on the plan's prose `<files>` list). `memory_verify_execute`'s doc comment, written by plan 01, named the retired verify ordinal by its C identifier (`CMD_VERIFY`) rather than in natural language -- a pre-existing defect plan 01's own verify script did not check for, now caught by this plan's broader scan.
- **Fix:** Rewrote the comment to describe the retired ordinal in natural language ("the standalone verify command's own wire ordinal"), preserving the same factual content.
- **Files modified:** `firestarter_fw/include/memory_utils.h`
- **Verification:** re-ran the task's full presence-assertion script; all four firmware CI legs green afterward; committed separately (`fa7603c`) rather than amended into `305b2f4`, because the meta gitlink commit had already advanced to reference the pre-fix SHA.
- **Committed in:** `fa7603c`

---

**Total deviations:** 1 auto-fixed (Rule 1 -- bug). **Impact on plan:** Necessary for the task's own stated acceptance criterion (neither retired ordinal appears in any of the 12 scanned firmware files); landed as a fourth commit rather than three, documented explicitly rather than forced into an artificial count. No scope creep -- the fix is exactly the literal-text repair the verify script demanded.

## Issues Encountered

None beyond the deviation above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 204-04 (the record: orphaned catalog ids annotated, remaining stale firmware citations, CMP-F1's deferral finding) can proceed. It also declares FWCMD-02 and FWCMD-03, which is why those two stay `Pending` in REQUIREMENTS.md until 204-04 finishes -- FWCMD-01 was declared only by plans 01 and 03 (both now complete) but was deliberately left unmarked too, per the wave-context instruction; the next executor or a manual pass should re-run `requirements.ready-ids` once 204-04 lands to reconcile all three in one pass.
- `mem_util_blank_check`, `mem_util_blank_check_region`, `blank_check_saved_address` and `BLANK_CHECK_CHUNK_SIZE` all survive, reachable only from write-init and erase-end now -- exactly Phase 205's starting point.
- Native baseline for the next plan to compare against: `pio test -e native` and `-e native_nodevtools` both 243/243 (20 suites, down 2 from plan 02's 245 -- the two Fork D no-VPP tests this plan deleted).
- `pio run -e leonardo`: 23810 B (down from 24082 B at plan 02's tip), well under the 28672-byte ceiling.
- Host suite: 2307 passed / 2 deselected (`no_programmer_found_*`, expected with a board attached); coverage 86.12% (floor 70%); ruff clean; ruff format clean.
- All three repositories remain on `v1.41-verification-to-host`; no branch touched `beta` at any point; nothing was pushed.

---
*Phase: 204-the-command-surfaces-leave-the-firmware*
*Completed: 2026-09-22*

## Self-Check: PASSED

All key files verified present on disk; all six commits (`29daf42`, `5f66595`, `305b2f4`, `fa7603c` in `firestarter_fw`; `2a17fd7` in `firestarter_app`; `85e49226`, `40b58f34` in the meta repo) verified present in `git log --oneline --all`.
