---
phase: 156-duplicated-report-extraction-boolean-convention-repair-firmw
plan: "03"
subsystem: firmware
tags: [avr, size-reduction, dedup, vpp, memory-utils, golden-inventory, udivmodhi4]

requires:
  - phase: 156-duplicated-report-extraction-boolean-convention-repair-firmw plan 01
    provides: ".planning/v1.33/156-before-figures.md -- authoritative before-half baselines (31 __udivmodhi4, 524/562 B eprom_check_vpp/flash_intel_write_init, 23-site golden, 348/0/0 pytest)"
  - phase: 156-duplicated-report-extraction-boolean-convention-repair-firmw plan 02
    provides: "Regression oracles for the under-voltage severity pairing (test_vpp04_e/f) and the chip-ID mismatch fork, proven RED-then-GREEN against a planted transposition on eprom.cpp/flash_intel.cpp BEFORE this plan's edit -- genuine regression guards for this plan, not post-hoc description"
provides:
  - "mem_util_report_voltage (src/proms/memory.cpp, declared in include/memory_utils.h) -- one shared VPP-mismatch report replacing four byte-identical packing blocks"
  - "Re-derived tests/golden/protocol_branch_inventory.json: 23 sites -> 22, protocol_keyed_sites unchanged at 1"
  - "DEDUP-01's own measured flash delta (-268 B on all three AVR targets, RAM unchanged), confirming the previously-unverified -268/-158 split"
affects: [156-04, 156-05, 156-06, 156-07]

tech-stack:
  added: []
  patterns:
    - "Call-site severity fork as ternary parameter pair: `bool force = is_flag_set(FLAG_FORCE);` feeding two parallel ternaries into a shared reporter, rather than an if/else duplicating the packing block per branch -- the extractor correctly does not count the resulting plain assignment as a branch predicate"
    - "Golden re-derivation via the module's own _extract_predicates(), machine-diffed field-by-field against the prior inventory to prove only `line` moved on survivors"

key-files:
  created: []
  modified:
    - firestarter/src/proms/memory.cpp
    - firestarter/include/memory_utils.h
    - firestarter/src/proms/eprom.cpp
    - firestarter/src/proms/flash_intel.cpp
    - firestarter/tests/golden/protocol_branch_inventory.json
    - firestarter/tests/test_protocol_branch_inventory.py

key-decisions:
  - "Task 1's plan-specified intermediate verification (avr-nm listing the unwired helper, avr-objdump showing zero __udivmodsi4) is physically unobservable: the AVR toolchain's default -ffunction-sections + --gc-sections strips a defined-but-unreferenced function entirely (flash stayed at the pre-figures 24660 B with the helper authored but not yet called). Deferred that specific check to after Task 2 wired the four call sites, where the helper becomes reachable and both checks are meaningful and green (0xbe / 190 B; 6/6 division call sites in the helper are __udivmodhi4). Documented rather than silently reordered."
  - "The plan's automated Task 1 check asserted a TOTAL-zero __udivmodsi4 count across the whole ELF, but 12 __udivmodsi4 sites are pre-existing and unrelated to this helper -- confirmed unchanged before/after by building the pristine 3d0b73d tree in a throwaway worktree (/tmp/probe156c, removed and pruned). Verified the load-bearing claim precisely instead: disassembled mem_util_report_voltage in isolation and confirmed all 6 of its division call sites are __udivmodhi4, zero __udivmodsi4."
  - "Lowered tests/test_protocol_branch_inventory.py's non-vacuous floor from 23 to 22 in the SAME commit as the golden re-derivation, even though this file is outside this plan's declared files_modified list. Site count legitimately dropped to 22 (one genuine branch removal), so leaving the floor at 23 would have made test_inventory_is_non_vacuous permanently RED after the commit -- which the plan's own acceptance criteria require to pass. Followed the file's own established precedent (a prior 24->23 lowering, same comment idiom, called out rather than slipped in) rather than leaving a broken gate or silently editing without explanation."

requirements-completed: []

coverage:
  - id: D1
    description: "mem_util_report_voltage replaces two of the four VPP-mismatch packing blocks (eprom.cpp) with the AVR 16-bit promotion mechanically proven intact"
    requirement: "DEDUP-01"
    verification:
      - kind: unit
        ref: "avr-objdump disassembly of mem_util_report_voltage: 6/6 division call sites are __udivmodhi4, 0 __udivmodsi4 (manual toolchain inspection, recorded in this SUMMARY)"
        status: pass
      - kind: unit
        ref: "pio test -e native_loop_v131 (82/82) -- test_vpp04_a, test_vpp04_c, test_vpp04_e, test_vpp04_f, test_vpp02_e1 all pass post-refactor"
        status: pass
    human_judgment: false
  - id: D2
    description: "The other two VPP-mismatch packing blocks (flash_intel.cpp's flash_intel_check_vpp) collapse onto the same shared helper, with the severity fork preserved as a call-site ternary pair"
    requirement: "DEDUP-01"
    verification:
      - kind: unit
        ref: "pio test -e native_loop_v131 (82/82) -- test_vpp04_f_flash_intel_undervoltage_warning_pairing"
        status: pass
      - kind: other
        ref: "Source-level identity: the extracted expressions and eight byte assignments in mem_util_report_voltage are character-identical to the four removed blocks (no value oracle exists; see 156-PATTERNS.md and 156-before-figures.md Ceiling 4)"
        status: pass
    human_judgment: false
  - id: D3
    description: "protocol_branch_inventory.json re-derived by its own extractor in the same commit as the eprom.cpp edit, so the gate is never red at any COMMIT (it was transiently red pre-commit, as documented by the golden's own one-commit convention)"
    requirement: "DEDUP-01"
    verification:
      - kind: unit
        ref: "python3 -m pytest tests/test_protocol_branch_inventory.py -q (7/7, post-commit)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Severity fork survives at all four call sites as an explicit (msg_id, response_code) pair; the four VPP oracles and the size/warning/pytest gates all confirm no regression"
    requirement: "DEDUP-03"
    verification:
      - kind: unit
        ref: "pio test -e native (172/172), -e native_nodevtools (172/172), -e native_loop_v131 (82/82); python3 -m pytest tests/ -q (348/0/0); python3 scripts/check_size_baseline.py --policy merge05 (PASS, all three AVR targets -268 B, RAM unchanged)"
        status: pass
    human_judgment: false

duration: ~25min
completed: 2026-08-23
status: complete
---

# Phase 156 Plan 03: One Shared VPP-Mismatch Report Replaces Four Copy-Pasted Blocks Summary

**Added `mem_util_report_voltage` (190 B, `uint16_t`-parameterised so its arithmetic stays on the 16-bit `__udivmodhi4` helper) and collapsed all four byte-identical VPP-mismatch packing blocks onto it -- measuring a genuine, per-target `-268 B` flash delta with RAM unchanged, and re-deriving the branch-inventory golden from 23 to 22 sites inside the same commit.**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-08-23T15:28:53Z
- **Completed:** 2026-08-23T15:45:22Z (plus SUMMARY authoring)
- **Tasks:** 3
- **Files modified:** 6 (5 planned + 1 test-floor adjustment, documented as a deviation)

## Accomplishments

- Authored `mem_util_report_voltage(firestarter_handle_t*, uint16_t measured_mv, uint16_t expected_mv, uint8_t msg_id, uint8_t response_code)` in `src/proms/memory.cpp`, declared in `include/memory_utils.h` inside the existing `extern "C"` guard, with the four value expressions and eight byte assignments character-identical to the four removed blocks.
- Collapsed both `eprom.cpp` blocks (in `eprom_check_vpp`) and both `flash_intel.cpp` blocks (in the static, fully-inlined `flash_intel_check_vpp` -- confirmed lexically at `flash_intel.cpp:26`, NOT `flash_intel_write_init:106` as the requirement text says; `flash_intel_check_vpp` is absent from the symbol table, matching `156-before-figures.md` C-1) onto the shared helper. The over-voltage arm's `if (is_flag_set(FLAG_FORCE))` became `bool force = is_flag_set(FLAG_FORCE);` feeding two parallel ternaries; the under-voltage arm passes `MSG_WARN_VPP_LOW`/`RESPONSE_CODE_WARNING` as literals.
- Measured DEDUP-01's own flash delta directly (not inherited from research's combined `-426 B`): **-268 B on all three AVR targets** (`uno` 24660->24392, `uno328pb` 24708->24440, `leonardo` 26804->26536), RAM unchanged on all three. This **confirms** the previously-unverified `-268 / -158` DEDUP-01/DEDUP-02 split recorded as UNVERIFIED in `156-before-figures.md` C-3.
- `__udivmodhi4` call sites fell from the measured baseline of 31 to **13** on `uno` -- matching research's stated post-DEDUP-01+02 target of 13 even though only DEDUP-01 has landed, meaning DEDUP-02's chip-ID blocks (plan 04) evidently carry none of the remaining `__udivmodhi4` traffic. `mem_util_report_voltage` disassembles to exactly 6 `__udivmodhi4` calls and 0 `__udivmodsi4` calls -- the 16-bit promotion survived the hoist into a function, mechanically proven, not asserted.
- `mem_util_report_voltage` measures **190 B (0xbe)**, matching the figure the `-426 B` estimate was based on. `eprom_check_vpp` fell from 524 B to **280 B (0x118)**; `flash_intel_write_init` fell from 562 B to **348 B (0x15c)** -- both smaller than the `156-before-figures.md` recorded values, as required.
- Re-derived `tests/golden/protocol_branch_inventory.json` via `tests/test_protocol_branch_inventory.py`'s own `_extract_predicates()`: 23 sites -> 22, `protocol_keyed_sites` unchanged at exactly 1 (line 70). The removed site is the `if (is_flag_set(FLAG_FORCE))` predicate at old line 728 -- a genuine branch removal (it became a plain `bool` assignment the extractor correctly does not count), not a relocation. All 22 surviving sites machine-compared field-by-field against the prior inventory and found byte-identical apart from `line`; 5 sites shifted (736->718, 787->753, 790->756, 791->757, 798->764, 815->781 -- 6 listed because one, 736->718, sits immediately below the edited block and the rest sit in the untouched chip-ID arm further down the file).
- All four VPP severity-fork oracles from plan 02 (and the pre-existing over-voltage cases) re-run and pass: `pio test -e native_loop_v131` 82/82, naming `test_vpp04_a`, `test_vpp04_c`, `test_vpp04_e`, `test_vpp04_f`, `test_vpp02_e1` explicitly.
- Full gate sweep post-commit: `pio test -e native` 172/172, `-e native_nodevtools` 172/172, `python3 -m pytest tests/ -q` 348 passed / 0 failed (matches `156-before-figures.md`'s canonical-checkout baseline exactly), `python3 scripts/check_build_warnings.py --rebuild` PASS (uno/uno328pb/leonardo macro-redefinition == 0; native/native_nodevtools within the 1166 watermark), `python3 scripts/check_size_baseline.py --policy merge05 --rebuild` PASS (all three AVR flash deltas negative, comfortably inside the one-sided MERGE-05 allowance; RAM unchanged; native/native_nodevtools case counts 172/172).

## Task Commits

1. **Task 1 + Task 2 + Task 3 (single plan-level commit, per the plan's own "commit once, for the whole plan" instruction):** `6bc3ed3` (refactor) -- helper + declaration + four call sites + golden re-derivation + test-floor adjustment, all in one commit, anchored `git rev-list --count 3d0b73d..HEAD == 1`.

**Plan metadata:** committed in the meta repo immediately after this SUMMARY (see the meta repo's own commit log).

## Files Created/Modified

- `firestarter/src/proms/memory.cpp` -- added `mem_util_report_voltage`, inserted between `mem_util_calculate_top_address_register` and `mem_util_split_delay`
- `firestarter/include/memory_utils.h` -- added the declaration inside the `extern "C"` guard, below `mem_util_delay_us`, with its own contract-naming comment
- `firestarter/src/proms/eprom.cpp` -- both `eprom_check_vpp` VPP-mismatch blocks collapsed to two-call-site form
- `firestarter/src/proms/flash_intel.cpp` -- both `flash_intel_check_vpp` VPP-mismatch blocks collapsed to two-call-site form
- `firestarter/tests/golden/protocol_branch_inventory.json` -- re-derived: 23 sites -> 22, `blob_shas['src/proms/eprom.cpp']` updated to the post-edit hash, `recorded_at_head` set to this commit's parent (`3d0b73d`), a fifth `recorded_by` entry appended
- `firestarter/tests/test_protocol_branch_inventory.py` -- non-vacuous floor lowered 23 -> 22 (deviation; see Decisions Made and Deviations from Plan)

## Decisions Made

- **Task 1's intermediate avr-nm/objdump check deferred to after Task 2.** The AVR toolchain's default `-ffunction-sections`/`--gc-sections` strips a defined-but-unreferenced function from the linked image entirely. Building immediately after Task 1 (helper authored, no call sites wired) showed `uno` flash still at the pre-figures baseline of 24660 B with no `mem_util_report_voltage` symbol in `avr-nm`'s output at all -- the function was garbage-collected. This is a plan-instruction-vs-toolchain-reality mismatch, not a code defect: the acceptance criteria are fully achievable, just only observable once the helper has a caller. Both checks (symbol present at 0xbe, `__udivmodsi4` absent from the helper) were performed and passed after Task 2 wired all four call sites.
- **The plan's Task 1 automated check literally asserts zero `__udivmodsi4` call sites across the WHOLE ELF**, but 12 such sites are pre-existing and unrelated to this refactor (confirmed identical before and after by building the pristine `3d0b73d` tree in a throwaway `git worktree` at `/tmp/probe156c`, removed and pruned afterward). Verified the load-bearing claim precisely instead: disassembled `mem_util_report_voltage` in isolation and confirmed all 6 of its own division call sites are `__udivmodhi4`, none `__udivmodsi4`.
- **Lowered `tests/test_protocol_branch_inventory.py`'s non-vacuous floor from 23 to 22**, in the same commit as the golden re-derivation, even though this file is outside the plan's declared `files_modified` list. The extraction legitimately produces 22 sites now (one genuine branch removal); leaving the hardcoded floor at 23 would make `test_inventory_is_non_vacuous` permanently fail after the commit, which contradicts the plan's own acceptance criteria ("`python3 -m pytest tests/test_protocol_branch_inventory.py -q` passes all legs"). Followed the file's own established precedent for this exact situation (a prior `24 -> 23` lowering with an explanatory comment, "called out rather than slipped in") rather than leaving a permanently-red gate. This is a Rule 3 (blocking-issue) auto-fix: without it, the plan's own stated success condition is unreachable.
- **The single commit carries 6 paths, not the plan's stated 5** (the test-floor file above is the sixth). Documented here rather than silently matching the letter of "exactly five paths" while leaving a broken gate.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Task 1's intermediate size/objdump verification could not observe the unwired helper**
- **Found during:** Task 1 (authoring `mem_util_report_voltage`)
- **Issue:** The plan's Task 1 acceptance criteria require `avr-nm` to list the new helper and `avr-objdump` to show its division calls at the intermediate point where the helper is defined but not yet called from any of the four sites. The AVR toolchain's default linker garbage-collection (`--gc-sections`) strips unreferenced functions, so at that intermediate point the helper is absent from the linked ELF entirely and flash size is unchanged (24660 B, matching the pre-figures baseline exactly).
- **Fix:** Performed the size/symbol/disassembly verification after Task 2 wired the four call sites instead, where the helper is reachable. Both checks passed cleanly at that point (0xbe size, 6/6 `__udivmodhi4`, 0 `__udivmodsi4` in the helper).
- **Files modified:** None (verification-ordering only, no code changed as a result)
- **Verification:** `avr-nm --print-size --size-sort -C .pio/build/uno/firestarter_uno.elf | grep report_voltage` -> `0000118c 000000be t mem_util_report_voltage`; `avr-objdump -d` disassembly of the function's body shows 6 `call ... __udivmodhi4` and 0 `__udivmodsi4`.
- **Committed in:** `6bc3ed3` (the single plan commit)

**2. [Rule 3 - Blocking] Task 1's total-ELF `__udivmodsi4 == 0` check is unsatisfiable due to pre-existing, unrelated 32-bit divisions**
- **Found during:** Task 1 verification
- **Issue:** The plan's automated verify command for Task 1 asserts `avr-objdump -d ... | grep -cE '(r?call|jmp).*__udivmodsi4'` equals 0 across the whole ELF. The pristine, unmodified tree at `3d0b73d` already contains 12 such call sites, unrelated to `eprom.cpp`/`flash_intel.cpp`/`memory.cpp`.
- **Fix:** Verified the actual load-bearing claim -- that the NEW helper's own arithmetic does not reach `__udivmodsi4` -- by disassembling `mem_util_report_voltage` specifically, and separately confirmed the pre-existing 12-site count is unchanged before/after by building the pristine tree in a throwaway `git worktree` (`/tmp/probe156c`, at `3d0b73d`), then removing and pruning it.
- **Files modified:** None
- **Verification:** Pristine-tree build: `PRE udivmodsi4: 12`. Post-refactor build: `12` (unchanged). Helper-specific disassembly: 0 `__udivmodsi4` reachable from `mem_util_report_voltage`.
- **Committed in:** `6bc3ed3`

**3. [Rule 3 - Blocking] Golden site-count floor pinned below the new, correct site count**
- **Found during:** Task 3 (re-deriving the golden)
- **Issue:** `tests/test_protocol_branch_inventory.py::test_inventory_is_non_vacuous` hardcodes `assert len(sites) >= 23`. The re-derived golden legitimately has 22 sites (one genuine branch removal). Left unedited, this assertion would fail forever after the commit, contradicting the plan's own acceptance criteria that this exact test must pass post-commit.
- **Fix:** Lowered the floor to 22, following the file's own established `24 -> 23` precedent (same comment idiom: called out explicitly, not silently changed, with the specific cause named).
- **Files modified:** `firestarter/tests/test_protocol_branch_inventory.py`
- **Verification:** `python3 -m pytest tests/test_protocol_branch_inventory.py -q` -> 7 passed (post-commit).
- **Committed in:** `6bc3ed3`

---

**Total deviations:** 3 auto-fixed (all Rule 3 -- blocking issues preventing the plan's own stated acceptance criteria from being satisfiable as literally written; none changed the substantive de-duplication, the arithmetic, or the severity forks).
**Impact on plan:** No scope creep. All three deviations are verification-ordering or gate-consistency fixes required to make the plan's own success criteria reachable given AVR toolchain behavior (linker GC) and pre-existing, unrelated code (the 12 `__udivmodsi4` sites) that the plan's literal wording did not anticipate.

## Issues Encountered

None beyond the three deviations above, all resolved inline.

## User Setup Required

None -- no external service configuration required. This plan edits firmware source and a committed test golden only.

## Next Phase Readiness

- `firestarter` is now at `6bc3ed3` on `gsd/v1.33-source-hygiene-firmware-size-reduction`, tree clean (`git -C firestarter status --porcelain` empty), no worktree remaining beyond the tracked `firestarter_py32_ci` sibling (the throwaway `/tmp/probe156c` worktree was removed and pruned).
- DEDUP-01's own contribution is fully measured and attributable: `-268 B` flash on all three AVR targets, RAM unchanged, `__udivmodhi4` count reduced, golden re-derived from 23 to 22 sites, all four VPP severity-fork oracles green.
- **No DEDUP-0X requirement was marked Complete in `.planning/REQUIREMENTS.md`** -- plan 07 is the landing plan that closes them, per this plan's explicit instructions. This plan's contribution: DEDUP-01 in full (helper, four call sites, golden re-derivation, measured flash delta); DEDUP-03's "the fork survives" half (severity stays an explicit `(msg_id, response_code)` pair at every call site, re-verified by plan 02's oracles plus the pre-existing over-voltage cases).
- Plan 04 (DEDUP-02) can proceed against the chip-ID blocks in `flash_utils.cpp`, `flash_intel.cpp`, `eprom.cpp`, `eeprom_28c.cpp`, and will re-derive this same golden a sixth time for the one remaining `FLAG_FORCE`-keyed site (the chip-ID mismatch ternary, now at line 757 in `eprom.cpp`) -- flagged in advance in this commit's `recorded_by` entry as the one that genuinely relocates into a file (`flash_utils.cpp`) this gate does not scan, per the plan's T-156-18 mitigation.
- The `-268 / -158` DEDUP-01/DEDUP-02 split cited in `156-before-figures.md` C-3 as UNVERIFIED is now **confirmed** on the DEDUP-01 side: exactly `-268 B` on all three targets. Plan 04 should expect roughly `-158 B` to close the combined `-426 B` research estimate, though that remains plan 04's own measurement to make.

---
*Phase: 156-duplicated-report-extraction-boolean-convention-repair-firmw*
*Completed: 2026-08-23*

## Self-Check: PASSED

- `.planning/phases/156-duplicated-report-extraction-boolean-convention-repair-firmw/156-03-SUMMARY.md` exists on disk -- FOUND
- `firestarter` commit `6bc3ed3` (refactor(156-03): one shared VPP-mismatch report replaces four copy-pasted blocks) exists in `git -C firestarter log --oneline --all` -- FOUND
- meta repo commit `47708821` (docs(156-03): record SUMMARY for VPP-mismatch report de-duplication) exists in `git log --oneline --all` -- FOUND

No missing items.
