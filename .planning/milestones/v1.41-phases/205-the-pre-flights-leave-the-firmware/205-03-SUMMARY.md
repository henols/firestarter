---
phase: 205-the-pre-flights-leave-the-firmware
plan: "03"
subsystem: firmware, testing
tags: [avr, platformio, pytest, source-contract-gate, blank-check-removal, golden-rederive]

requires:
  - phase: 205-01
    provides: "firestarter_app owns erase -b's blank-check verdict; the host guard this plan's removal depends on."
  - phase: 205-02
    provides: "An honestly green firestarter_fw pytest tree (320/320) and the FWBLANK-05 phase-entry flash/RAM baseline."
provides:
  - "The four blank-check pre-flight call sites are gone from eprom.cpp, flash_intel.cpp and flash_nor_unlock.cpp (FWBLANK-01/02)."
  - "The blank-check machinery itself -- mem_util_blank_check, mem_util_blank_check_region, blank_check_saved_address, BLANK_CHECK_CHUNK_SIZE and the orphaned uint32_to_bytes -- is deleted from memory.cpp and memory_utils.h with no caller, declaration or comment left anywhere in the repository (FWBLANK-03)."
  - "mem_util_operation_end survives with its two callers, its region-end read, and a migrated mechanical fence in the surviving source-contract module."
  - "The branch-inventory golden is re-derived by the gate's own extractor, positionally verified, and lands in the same commit as eprom.cpp."
  - "Every citation stranded by the sweep is repaired honestly, including two sites RESEARCH found but neither task's own file list named."
affects: [205-04, 205-05, 205-06, 205-07]

actuals:
  tokens: 62000
  tasks: 2
  commits: 4
  commits_by_repo:
    firestarter_fw: 2
    meta: 2

tech-stack:
  added: []
  patterns:
    - "A pre-authored absence leg is run against the pre-sweep tree BEFORE the sweep lands, and its failure text is read to confirm it failed because it FOUND the target, not because a path mis-resolved. Applied to all three new legs in this plan (two in task 1, one in task 2)."
    - "A golden re-derive with a known predicate-collision matches old sites to live sites POSITIONALLY (drop the known-removed entries by line number, zip old[i] against live[i], verify 0 mismatches on (predicate, keyed_on, tier)) rather than through a dict keyed on that signature, which silently collapses colliding entries."
    - "An append-only audit-log field (a golden's meta.recorded_by) is never scrubbed to satisfy a later absence check -- it is excluded from the check by construction, not edited to hide the history it exists to preserve."

key-files:
  created: []
  modified:
    - firestarter_fw/src/proms/eprom.cpp
    - firestarter_fw/src/proms/flash_intel.cpp
    - firestarter_fw/src/proms/flash_nor_unlock.cpp
    - firestarter_fw/src/proms/memory.cpp
    - firestarter_fw/include/memory_utils.h
    - firestarter_fw/include/firestarter.h
    - firestarter_fw/CLAUDE.md
    - firestarter_fw/PROTOCOLS.md
    - firestarter_fw/tests/test_verify_survival_source_contract.py
    - firestarter_fw/tests/test_blank_check_region_source_contract.py (deleted)
    - firestarter_fw/tests/test_protocol_branch_inventory.py
    - firestarter_fw/tests/golden/protocol_branch_inventory.json
    - firestarter_fw/tests/test_progress_emission_is_leonardo_only.py
    - firestarter_fw/test/native/avr/test_val_eprom/test_val_eprom.cpp
    - firestarter_fw/test/native/avr/test_val_eprom/host_stubs.cpp
    - firestarter_fw/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp
    - firestarter_fw/test/native/avr/test_val_5v_page/test_val_5v_page.cpp
    - .planning/phases/205-the-pre-flights-leave-the-firmware/205-03-SUMMARY.md

key-decisions:
  - "Pulled two citation repairs (eprom.cpp:394's 0xE0 rationale and flash_nor_unlock.cpp's guard-justification comment) from task 2 into task 1's commit. Task 1's own acceptance criteria (a whole-file absence scan on the three call-site files) would fail against their surviving prose otherwise, and the underlying facts they now state -- 0xE0 has one emitter; OPERATION_IN_PROGRESS is never set once nothing calls the region form -- are already true as of task 1's deletions, not merely as of task 2's."
  - "Repaired two citation sites RESEARCH found but neither task's authored <files> list named: test_eeprom28c_sdp.cpp:1325/1329 and test_val_5v_page.cpp:205/799/803 each named the deleted whole-device function directly in an assertion message or a companion comment. Task 2's own repo-wide git-grep acceptance criterion would otherwise still fail. Only prose changed; no assertion's pass/fail behavior changed."
  - "The three new absence legs (two in task 1, one in task 2) scan RAW, non-comment-stripped text, per task 2's explicit design intent that these legs must catch a stray reference left in a comment as loudly as one left in code. This diverges from the pre-existing Coverage 9 leg in the same module, which scans comment-stripped text -- a pre-existing inconsistency, left as-is rather than fixed, since fixing it was outside this plan's scope."
  - "tests/golden/protocol_branch_inventory.json's meta.recorded_by field -- an append-only audit log of every prior re-derivation's own commit message -- still quotes the deleted function names verbatim as historical record (Phase 142/143/145/201 entries). Left untouched: scrubbing it would violate the golden's own established never-hand-edit and audit-trail conventions. Task 2's own <verify> git-grep excludes it explicitly for this reason, alongside the survival gate module."
  - "The golden re-derive matched old sites to live sites positionally, not through a (predicate, keyed_on, tier) dict key: the two deleted sites (formerly lines 52 and 141) share an identical signature, which is exactly the collision this golden's own history has hit before. Verified 0 mismatches across all 20 surviving pairs before carrying class/reason forward."
  - "Corrected a pre-existing, unrelated docstring drift while touching this section: test_protocol_branch_inventory.py's Coverage list still named a retired function (test_exactly_three_protocol_keyed_sites_at_the_pinned_lines) that Phase 142 already replaced with the current one-site form. Fixed opportunistically; not caused by this plan."

requirements-completed: [FWBLANK-01, FWBLANK-02, FWBLANK-03]

coverage:
  - id: D1
    description: "The write-init blank check is removed from eprom.cpp, flash_intel.cpp and flash_nor_unlock.cpp, and the erase-end blank check is removed from eprom.cpp's CMD_ERASE arm (FWBLANK-01/FWBLANK-02). The branch-inventory golden is re-derived by the gate's own extractor with positional alignment proven (0 mismatches across 20 pairs), and lands in the same commit as eprom.cpp."
    requirement: FWBLANK-01
    verification:
      - kind: unit
        ref: "tests/test_verify_survival_source_contract.py::test_no_write_init_body_performs_a_blank_check"
        status: pass
      - kind: unit
        ref: "tests/test_verify_survival_source_contract.py::test_the_erase_arm_assigns_no_operation_end_in_eprom_cpp"
        status: pass
      - kind: unit
        ref: "tests/test_protocol_branch_inventory.py (all 7 legs)"
        status: pass
      - kind: integration
        ref: "python3 -c one-liner: no blank-check reference in eprom.cpp/flash_intel.cpp/flash_nor_unlock.cpp; machinery+survivor intact in memory.cpp (task 1 verify)"
        status: pass
    human_judgment: false
  - id: D2
    description: "mem_util_blank_check, mem_util_blank_check_region, blank_check_saved_address, BLANK_CHECK_CHUNK_SIZE and uint32_to_bytes are deleted together, with no caller, declaration, doc comment or commented-out reference surviving anywhere in the repository (FWBLANK-03). mem_util_operation_end survives with two callers, the region-end read, and a migrated mechanical fence."
    requirement: FWBLANK-03
    verification:
      - kind: unit
        ref: "tests/test_verify_survival_source_contract.py::test_the_blank_check_machinery_is_absent"
        status: pass
      - kind: unit
        ref: "tests/test_verify_survival_source_contract.py::test_operation_end_is_defined_exactly_once_and_reads_both_members"
        status: pass
      - kind: other
        ref: "git grep -e mem_util_blank_check -e blank_check_saved_address -e BLANK_CHECK_CHUNK_SIZE -e uint32_to_bytes (repo-wide, excluding the survival gate module and the golden's audit log) -> exit 1, no matches"
        status: pass
    human_judgment: false
  - id: D3
    description: "Both commit boundaries leave all four firmware CI legs green in order (pio test -e native, pio test -e native_nodevtools, pytest tests/, pio run); two native tests deleted and two re-keyed/inverted, each with its RUN_TEST line handled."
    verification:
      - kind: integration
        ref: "pio test -e native (241/241), pio test -e native_nodevtools (241/241), pytest tests/ (315/315), pio run (uno/uno328pb/leonardo all SUCCESS)"
        status: pass
    human_judgment: false

duration: 95min
completed: 2026-09-22
status: complete
---

# Phase 205 Plan 03: The four blank-check call sites and the machinery behind them leave the firmware Summary

**Two commits in `firestarter_fw` delete FWBLANK-01/02/03's whole surface -- four call sites, the five-symbol machinery behind them, and every stranded citation -- with the branch-inventory golden re-derived and positionally verified, and both commit boundaries green on all four CI legs.**

## Performance

- **Duration:** ~95 min
- **Started:** 2026-09-22 (session start)
- **Completed:** 2026-09-22
- **Tasks:** 2
- **Files modified:** 17 in `firestarter_fw` (11 in task 1's commit, 11 in task 2's commit, with overlap on the two test-support modules), 1 gitlink advance in the meta repo

## Accomplishments

- `configure_eprom`'s `CMD_ERASE` arm assigns no `firestarter_operation_end` at all; none of the three write-init bodies (`eprom.cpp`, `flash_intel.cpp`, `flash_nor_unlock.cpp`) calls a blank-check function anymore. The host owns both refusals now.
- `test_blank_check_region_source_contract.py` retires; its only permanent fence (`mem_util_operation_end`'s definition-and-survivor proof) migrates into `test_verify_survival_source_contract.py`, which gains three new absence legs across both tasks.
- `tests/golden/protocol_branch_inventory.json` re-derived by the gate's own extractor: two sites sharing an identical `(predicate, keyed_on, tier)` signature were matched to their live counterparts *positionally*, not through a colliding dict key -- 0 mismatches across 20 pairs before `class`/`reason` were carried forward. Counts move 22→20 / 21→19 / 1 (unchanged); the sole protocol-keyed site shifts 67→64.
- `mem_util_blank_check`, `mem_util_blank_check_region`, `blank_check_saved_address`, `BLANK_CHECK_CHUNK_SIZE` and the orphaned `uint32_to_bytes` are gone from `memory.cpp` and `memory_utils.h`, cut in two descending spans around the surviving `mem_util_operation_end`.
- Every stranded citation is repaired honestly, including two sites RESEARCH found but neither task's authored file list named (`test_eeprom28c_sdp.cpp`, `test_val_5v_page.cpp`) -- required to satisfy task 2's own repository-wide absence check.
- OQ-4's latency is recorded, not swept: `set_operation_in_progress`/`clear_operation_in_progress` are now uncalled; the five `is_operation_in_progress` reads become constant (one always-false, four always-true).
- All four firmware CI legs green in order at both commit boundaries.

## Task Commits

Each task was committed atomically:

1. **Task 1: the four call sites, the golden, and the census gate retired with its survivor fence migrated** — `1cf1b22` (feat, in `firestarter_fw`)
2. **Task 2: delete the machinery in two spans, and repair every citation the deletion strands** — `512e6ab` (feat, in `firestarter_fw`)

**Gitlink advance:** `6fe22049` (chore, in the meta repo) — advances the `firestarter_fw` gitlink to `512e6ab`.

_Note: no TDD tasks in this plan; both tasks required a captured RED transcript before their new absence legs' commit, per the plan's own discipline (see "RED Transcripts" below)._

## Files Created/Modified

- `firestarter_fw/src/proms/eprom.cpp` — deleted the `CMD_ERASE` arm's blank-check assignment (`:52-54`) and the write-init region call (`:141-143`); rewrote the `MSG_DATA_PROGRESS` rationale comment that cross-referenced the deleted function (formerly `:394`).
- `firestarter_fw/src/proms/flash_intel.cpp` — deleted the write-init blank-check call (`:91-93`).
- `firestarter_fw/src/proms/flash_nor_unlock.cpp` — deleted the write-init blank-check call (`:101-103`) and the commented-out dead assignment (`:41`); rewrote the `is_operation_in_progress` guard's justification comment.
- `firestarter_fw/src/proms/memory.cpp` — deleted the saved-address cursor, the chunk-size constant, `uint32_to_bytes`, the region-scoped scan body and the whole-device wrapper, in two descending spans around the surviving `mem_util_operation_end`.
- `firestarter_fw/include/memory_utils.h` — deleted the whole-device wrapper's and the region form's declarations; left `mem_util_operation_end`'s declaration untouched.
- `firestarter_fw/include/firestarter.h` — deleted the ordinal-4 record's stale "leaves in Phase 205" sentence.
- `firestarter_fw/CLAUDE.md` — rewrote the 0xE0 payload-contract paragraph (one emitter now, not two).
- `firestarter_fw/PROTOCOLS.md` — rewrote the `0x0D` erase-model paragraph's three blank-check clauses: no longer names the deleted machinery, states `erase --blank-check` now *works* on this protocol (a behaviour gain, not a no-op), and describes the write path's own no-blank-check fact without naming the deleted symbol.
- `firestarter_fw/tests/test_verify_survival_source_contract.py` — gained `test_no_write_init_body_performs_a_blank_check`, `test_the_erase_arm_assigns_no_operation_end_in_eprom_cpp`, `test_operation_end_is_defined_exactly_once_and_reads_both_members` (migrated), and `test_the_blank_check_machinery_is_absent`; extended `test_scan_targets_are_non_vacuous`'s default-target list to cover `memory_utils.h`.
- `firestarter_fw/tests/test_blank_check_region_source_contract.py` — **deleted** (retired; its docstring named this the commit to do it in).
- `firestarter_fw/tests/test_protocol_branch_inventory.py` — re-pinned the protocol-keyed line literal `67` → `64`; lowered the non-vacuous floor `21` → `20` (the count itself moved, not merely line numbers); fixed a pre-existing stale Coverage-list entry.
- `firestarter_fw/tests/golden/protocol_branch_inventory.json` — re-derived (see Accomplishments).
- `firestarter_fw/tests/test_progress_emission_is_leonardo_only.py` — Coverage 6 prose corrected from "two emitters" to "one emitter"; assertions unchanged.
- `firestarter_fw/test/native/avr/test_val_eprom/test_val_eprom.cpp` — deleted `test_erase_end_blank_check_scans_from_zero` and `test_blank_check_resumes_across_chunks_and_restores_the_cursor`; re-keyed `test_write_init_accepts_blank_region_on_non_blank_part` → `test_write_init_performs_no_blank_check_at_all`; inverted `test_write_init_still_refuses_when_target_region_is_non_blank` → `test_write_init_no_longer_refuses_when_target_region_is_non_blank`; updated the `RUN_TEST` block and rewrote now-stale surrounding comments.
- `firestarter_fw/test/native/avr/test_val_eprom/host_stubs.cpp` — restated the `VAL_EPROM_SHADOW_SIZE` sizing rationale in the past tense.
- `firestarter_fw/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp` — rewrote an assertion message and its companion comment that named the deleted function directly (prose only; the assertion's pass/fail logic is unchanged).
- `firestarter_fw/test/native/avr/test_val_5v_page/test_val_5v_page.cpp` — same treatment, three sites (prose only).

## Decisions Made

See the frontmatter `key-decisions` block above for the full reasoning on each. In one sentence each:

1. Pulled two citation repairs from task 2 into task 1, because task 1's own acceptance criteria demanded it and the underlying facts were already true.
2. Repaired two citation sites RESEARCH found but the plan's file lists omitted, because task 2's own repo-wide grep would otherwise fail.
3. Used RAW-text scans for all three new absence legs, per task 2's explicit stated intent.
4. Left the golden's `meta.recorded_by` historical audit log untouched, because scrubbing it would violate the golden's own established convention.
5. Matched golden sites positionally, not by a colliding dict key, exactly as the plan required.
6. Fixed one unrelated, pre-existing stale docstring line while touching that section.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug in the plan's own verify script] Two citation repairs moved from task 2 into task 1**
- **Found during:** Task 1, running the plan's own literal `<verify>` python one-liner and acceptance criteria (a whole-file raw-text absence scan on `eprom.cpp`, `flash_intel.cpp`, `flash_nor_unlock.cpp`) against the tree after only deleting the four call sites.
- **Issue:** `eprom.cpp:394`'s `MSG_DATA_PROGRESS` rationale comment and `flash_nor_unlock.cpp`'s guard-justification comment both name `mem_util_blank_check` literally in prose. The plan's `artifact_precedence` and task 2's own action text assign both repairs to task 2 — but task 1's own acceptance criteria (`git grep mem_util_blank_check` over the three call-site files "returns nothing") and its own verify one-liner (a raw substring check over the same three files) would fail against them if left for task 2, since task 1 must complete before task 2 starts.
- **Fix:** Rewrote both comments in task 1's commit, using the exact behavioral facts task 2's action text specifies (0xE0 has one emitter now; the guard's cited justification is gone) — both facts are already true as of task 1's own deletions (nothing calls the region form after task 1; the only-caller-of-the-guard's-justification is gone), not merely as of task 2's later machinery deletion.
- **Files modified:** `firestarter_fw/src/proms/eprom.cpp`, `firestarter_fw/src/proms/flash_nor_unlock.cpp`
- **Verification:** The plan's own task-1 verify one-liner passes cleanly; re-confirmed no regression when task 2 landed.
- **Committed in:** `1cf1b22` (Task 1 commit)

**2. [Rule 3 - Blocking issue] Two citation sites outside either task's authored file list**
- **Found during:** Task 2, running the task's own repository-wide `git grep` acceptance check after all four production-source edits and the primary citation repairs.
- **Issue:** `test_eeprom28c_sdp.cpp:1325,1329` and `test_val_5v_page.cpp:205,799,803` each name `mem_util_blank_check` or `BLANK_CHECK_CHUNK_SIZE` directly, in an assertion message or a companion comment. RESEARCH's own "Gate Impact" section named the two tests these sites belong to (`test_case30_write_init_no_blank_check_with_flag_clear_erase01`, `test_5v_page_write_init_no_blank_check_erase02`) and said their prose "must be rewritten" — but neither task's authored `<files>` list included either file, so the repair was never scheduled. Left unrepaired, task 2's own acceptance criterion (repo-wide absence, excluding only the survival gate module) fails.
- **Fix:** Rewrote each site's prose to describe the removed mechanism without naming the deleted symbol, preserving every assertion's pass/fail behavior exactly. No test logic changed.
- **Files modified:** `firestarter_fw/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp`, `firestarter_fw/test/native/avr/test_val_5v_page/test_val_5v_page.cpp`
- **Verification:** `pio test -e native -f "*test_eeprom28c_sdp*" -f "*test_val_5v_page*"` — 82/82 cases pass; repo-wide grep (excluding the survival module and the golden's audit log) returns exit 1 (no matches).
- **Committed in:** `512e6ab` (Task 2 commit)

**3. [Rule 1 - unrelated pre-existing drift, fixed opportunistically] Stale Coverage-list entry in `test_protocol_branch_inventory.py`**
- **Found during:** Task 1, editing the module's docstring to re-pin the protocol-keyed line.
- **Issue:** The Coverage list's item 3 still read `test_exactly_three_protocol_keyed_sites_at_the_pinned_lines`, a name Phase 142 already replaced with the current single-site form (`test_exactly_one_protocol_keyed_site_at_the_pinned_line`). Not caused by this plan; found while touching adjacent text.
- **Fix:** Corrected the Coverage-list entry to match the actual function name and behavior.
- **Files modified:** `firestarter_fw/tests/test_protocol_branch_inventory.py`
- **Verification:** No test behavior change; docstring-only.
- **Committed in:** `1cf1b22` (Task 1 commit)

---

**Total deviations:** 3 auto-fixed (1 verify-script-scope bug across two commits, 1 blocking gap in the plan's own file lists, 1 unrelated pre-existing drift).
**Impact on plan:** All three were necessary to make the plan's own stated acceptance criteria actually pass, or were zero-risk documentation fixes. No scope creep into FWBLANK-04 (the flag retirement) or FWBLANK-05 (the flash/RAM measurement) — both remain untouched, correctly deferred to later plans.

## RED Transcripts

**Task 1** — `test_no_write_init_body_performs_a_blank_check` and `test_the_erase_arm_assigns_no_operation_end_in_eprom_cpp`, run against the untouched (pre-sweep) tree:

```
tests/test_verify_survival_source_contract.py::test_no_write_init_body_performs_a_blank_check FAILED
tests/test_verify_survival_source_contract.py::test_the_erase_arm_assigns_no_operation_end_in_eprom_cpp FAILED
...
E       AssertionError: found a write-init body still referencing a blank-check function ...
E         Got:
E         src/proms/eprom.cpp: the whole-device blank-check function
E         src/proms/eprom.cpp: the region-scoped blank-check function
E         src/proms/flash_intel.cpp: the whole-device blank-check function
E         src/proms/flash_nor_unlock.cpp: the whole-device blank-check function
...
E       AssertionError: configure_eprom's CMD_ERASE arm in src/proms/eprom.cpp still assigns handle->firestarter_operation_end ...
E         Got arm body:
E                     handle->firestarter_operation_main = eprom_erase_execute;
E                     if (!is_flag_set(FLAG_SKIP_BLANK_CHECK)) {
E                         handle->firestarter_operation_end = mem_util_blank_check;
E                     }
2 failed, 1 passed in 0.11s
```
Both failed for the intended reason — they FOUND the call sites, not a mis-resolved path. The third leg present at this point (`test_operation_end_is_defined_exactly_once_and_reads_both_members`, migrated) already PASSED, confirming the survivor fence works before any deletion.

**Task 2** — `test_the_blank_check_machinery_is_absent`, run against the tree with task 1 committed but before task 2's `memory.cpp`/`memory_utils.h` deletions (captured by temporarily restoring those two files from `HEAD`, running the leg, then restoring the edited versions — no `git stash` used):

```
tests/test_verify_survival_source_contract.py::test_the_blank_check_machinery_is_absent FAILED
...
E       AssertionError: found blank-check machinery surviving in memory.cpp or memory_utils.h ...
E         Got:
E         src/proms/memory.cpp: the whole-device blank-check function
E         src/proms/memory.cpp: the region-scoped blank-check function
E         src/proms/memory.cpp: the blank-check saved-address cursor
E         src/proms/memory.cpp: the blank-check chunk-size constant
E         src/proms/memory.cpp: the orphaned byte-packing helper
E         include/memory_utils.h: the whole-device blank-check function
E         include/memory_utils.h: the region-scoped blank-check function
1 failed, 13 deselected in 0.14s
```
Failed for the intended reason — it found all five symbols across both files.

## Issues Encountered

None beyond the deviations documented above.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `firestarter_fw`'s pytest tree is honestly green: 315/315 collected and passing (314 legs at task 1's boundary, +1 at task 2's), no `--ignore`, no wholesale skip.
- Both native environments (`native`, `native_nodevtools`) are green at 241/241 cases each at task 2's boundary (243 baseline − 2 deleted native tests, one per task).
- `pio run` succeeds for `uno`, `uno328pb` and `leonardo`; leonardo measures 23292 B flash / 1835 B RAM, matching `205-RESEARCH.md`'s predicted −518 B / −4 B delta exactly. `205-FLASH-RAM.md`'s phase-exit figures are plan 06's job to record, not this plan's — the number is confirmed reproducible here for that plan's benefit.
- `FLAG_SKIP_BLANK_CHECK` (`0x08`) itself is untouched in both the firmware header and `constants.py` — its retirement is FWBLANK-04, plan 04's job, correctly out of this plan's scope.
- `PROTOCOLS.md:321`'s deferral of the control-flag clause to plan 04 stands as designed: the clause is now written in terms of behaviour, so it stays accurate whether or not plan 04 has landed yet.
- No branch in any of the three repositories is `beta` at any point in this plan's execution.
- Two folded todos closed by this plan's deletions: `2026-08-30-write-init-blank-check-is-whole-device.md` (firmware half, FWBLANK-01 itself) and `2026-09-20-blank-check-region-fails-open-on-start-greater-than-end.md` (closed by deletion, not by the local clamp it suggested — the structural objection it raised is exactly why the whole check moved to the host).

---
*Phase: 205-the-pre-flights-leave-the-firmware*
*Completed: 2026-09-22*

## Self-Check: PASSED
