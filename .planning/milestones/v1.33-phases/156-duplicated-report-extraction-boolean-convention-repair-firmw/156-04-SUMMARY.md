---
phase: 156-duplicated-report-extraction-boolean-convention-repair-firmw
plan: "04"
subsystem: firmware
tags: [avr, size-reduction, dedup, chip-id, memory-utils, golden-inventory, udivmodhi4]

requires:
  - phase: 156-duplicated-report-extraction-boolean-convention-repair-firmw plan 01
    provides: ".planning/v1.33/156-before-figures.md -- authoritative before-half baselines (31 __udivmodhi4, 22-site golden after plan 03, 348/0/0 pytest)"
  - phase: 156-duplicated-report-extraction-boolean-convention-repair-firmw plan 02
    provides: "Regression oracle for the chip-ID mismatch fork (test_case7_mismatching_chip_id_with_force_warns, both fork directions pinned by message id) -- a genuine regression guard for this plan's collapse, not post-hoc description"
  - phase: 156-duplicated-report-extraction-boolean-convention-repair-firmw plan 03
    provides: "mem_util_report_voltage precedent (src/proms/memory.cpp / include/memory_utils.h), the golden re-derived 23->22, and the confirmed -268 B DEDUP-01 half of the -426 B combined estimate"
provides:
  - "mem_util_report_chip_id (src/proms/memory.cpp, declared in include/memory_utils.h) -- one shared chip-ID-mismatch report replacing four drifted copies (flash_utils.cpp, flash_intel.cpp, eprom.cpp, eeprom_28c.cpp)"
  - "Re-derived tests/golden/protocol_branch_inventory.json: 22 sites -> 21, protocol_keyed_sites unchanged at 1"
  - "DEDUP-02's own measured flash delta (-158 B on all three AVR targets, RAM unchanged), closing the previously-unverified -268/-158 split at a combined, phase-total -426 B matching 156-before-figures.md exactly"
affects: [156-05, 156-06, 156-07]

tech-stack:
  added: []
  patterns:
    - "Severity-as-parameter, never severity-as-internal-flag-test: mem_util_report_chip_id takes bool warn_only rather than testing is_flag_set(FLAG_FORCE) itself, because one of its four former call sites (the standalone CMD_CHECK_CHIP_ID command) must keep refusing unconditionally regardless of --force. The two-callers-disagree-on-policy shape is preserved by parameterisation, not collapsed."
    - "Single-boolean-derives-both-outputs shape: the id AND the response_code both come from the same warn_only boolean, making a transposition between them impossible by construction -- deliberately narrower than mem_util_report_voltage's two independent parameters, because that helper's under-voltage arm needs a pairing its over-voltage arm does not."
    - "Positional (line-order) golden re-derivation instead of a predicate-text dict lookup, required because three surviving sites share an identical predicate/keyed_on/tier signature (`if (handle->response_code == RESPONSE_CODE_ERROR)` / [response_code] / other, at lines 146/177/676) -- a naive dict keyed on that signature collapses distinct sites and loses their distinct class/reason metadata."

key-files:
  created: []
  modified:
    - firestarter/src/proms/memory.cpp
    - firestarter/include/memory_utils.h
    - firestarter/src/proms/flash_utils.cpp
    - firestarter/src/proms/flash_intel.cpp
    - firestarter/src/proms/eprom.cpp
    - firestarter/src/proms/eeprom_28c.cpp
    - firestarter/tests/golden/protocol_branch_inventory.json
    - firestarter/tests/test_protocol_branch_inventory.py

key-decisions:
  - "The plan's own acceptance-check grep for the 4-byte payload array (`uint8_t _b[4]` count == 0 across the four edited files) collides with a genuinely unrelated, pre-existing declaration: `eprom_internal_report_budget_failure` in eprom.cpp packs an unrelated {addr_hi, addr_mid, addr_lo, pulse_count} 4-byte payload for MSG_ERR_MAX_PULSES/MSG_ERR_ENERGY_CAP, using the identical `uint8_t _b[4];` spelling by coincidence. The literal grep therefore returns 1, not 0. Verified the substantive claim precisely instead: `grep -c 'chip_id != handle->chip_id'` across all four files is 0 (all four mismatch-comparison blocks are gone), and `mem_util_report_chip_id(handle` appears exactly once per site (4 total) -- the extra textual hit the naive `mem_util_report_chip_id` grep found in eprom.cpp is the explanatory comment at the call site, not a second call. Left `eprom_internal_report_budget_failure` completely untouched -- it is out of scope for this refactor."
  - "Lowered tests/test_protocol_branch_inventory.py's non-vacuous floor from 22 to 21 in the SAME commit as the golden re-derivation, even though this file is outside this plan's declared files_modified list -- following the identical precedent plan 03 established for the 23->22 step. Site count legitimately dropped to 21 (the chip-ID mismatch guard relocated into memory.cpp); leaving the floor at 22 would have made test_inventory_is_non_vacuous permanently RED after the commit."
  - "The golden re-derivation was self-corrected before committing: an initial draft matched old sites to new sites by a (predicate, keyed_on, tier) dict key, which silently collapsed three sites that share the identical text `if (handle->response_code == RESPONSE_CODE_ERROR)` / [response_code] / other (lines 146, 177, 676 in the prior inventory) into a single dict entry, losing two of their distinct class/reason values and corrupting the sites array (caught via `git diff --stat` showing ~7700 changed lines instead of the expected small diff). Re-derived using positional (ascending-line-order) two-pointer alignment instead -- matching the gate's own test_branch_sites_match_the_recorded_inventory comparison method, which is itself positional, not a text-keyed lookup. No incorrect JSON was ever committed; the mistake was caught and fixed before staging."

requirements-completed: []

coverage:
  - id: D1
    description: "mem_util_report_chip_id replaces all four chip-ID mismatch blocks (flash_utils.cpp, flash_intel.cpp, eprom.cpp, eeprom_28c.cpp) with the transposition-proof single-boolean shape"
    requirement: "DEDUP-02"
    verification:
      - kind: unit
        ref: "avr-nm --print-size --size-sort -C .pio/build/uno/firestarter_uno.elf: mem_util_report_chip_id measures 0x5a (90 B), matching the plan's predicted figure exactly"
        status: pass
      - kind: unit
        ref: "pio test -e native (172/172), -e native_nodevtools (172/172), -e native_loop_v131 (82/82) -- including test_case7_mismatching_chip_id_with_force_warns (both fork directions) and test_migrated_mismatching_chip_id_errors"
        status: pass
    human_judgment: false
  - id: D2
    description: "Divergence 1 (severity keyed on is_flag_set(FLAG_FORCE) inline vs. an error_code parameter) is preserved by parameterisation, not collapsed -- the standalone CMD_CHECK_CHIP_ID path still refuses unconditionally"
    requirement: "DEDUP-02"
    verification:
      - kind: other
        ref: "Source-level identity: eprom_check_chip_id_execute is byte-unchanged (still passes RESPONSE_CODE_ERROR unconditionally), eprom_generic_init is byte-unchanged (still passes the FLAG_FORCE-derived value), and mem_util_report_chip_id contains zero is_flag_set(FLAG_FORCE) references (grep -c == 0). No behavioural oracle exists for this specific claim; stated as a ceiling, not implied covered."
        status: pass
    human_judgment: false
  - id: D3
    description: "protocol_branch_inventory.json re-derived by its own extractor in the same commit as the eprom.cpp edit, so the gate is never red at any COMMIT"
    requirement: "DEDUP-02"
    verification:
      - kind: unit
        ref: "python3 -m pytest tests/test_protocol_branch_inventory.py -q (7/7, post-commit)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Severity fork survives at all four call sites via warn_only; the chip-ID oracle, the size/warning/pytest gates all confirm no regression, and the phase's combined -426 B total is measured"
    requirement: "DEDUP-03"
    verification:
      - kind: unit
        ref: "pio run -e uno/-e uno328pb/-e leonardo: 24234/24282/26378, RAM 1567/1573/2008 (unchanged); python3 -m pytest tests/ -q (348/0/0); python3 scripts/check_size_baseline.py --policy merge05 --rebuild (PASS, one-sided, all three AVR targets negative delta, RAM unchanged, native/native_nodevtools case counts 172/172)"
        status: pass
    human_judgment: false

duration: ~55min
completed: 2026-08-23
status: complete
---

# Phase 156 Plan 04: One Shared Chip-ID-Mismatch Report Replaces Four Drifted Copies Summary

**Added `mem_util_report_chip_id` (90 B, single-boolean-derives-both-outputs shape) and collapsed all four chip-ID-mismatch blocks onto it, preserving the one divergence that must not be collapsed (the standalone `CMD_CHECK_CHIP_ID` path's unconditional refusal) -- measuring a genuine, per-target `-158 B` flash delta with RAM unchanged, closing the phase's combined `-426 B` total exactly against `156-before-figures.md`, and re-deriving the branch-inventory golden from 22 to 21 sites inside the same commit.**

## Performance

- **Duration:** ~55 min
- **Completed:** 2026-08-23T16:06:50Z
- **Tasks:** 3
- **Files modified:** 8 (7 planned + 1 test-floor adjustment, documented as a deviation -- following plan 03's identical precedent)

## Accomplishments

- Authored `mem_util_report_chip_id(firestarter_handle_t*, uint16_t actual, bool warn_only)` in `src/proms/memory.cpp`, declared in `include/memory_utils.h` inside the existing `extern "C"` guard immediately below `mem_util_report_voltage`'s prototype. The helper takes an early `return` when `actual == handle->chip_id` (the mismatch guard hoisted out of all four call sites), then derives BOTH the message id and `response_code` from the single `warn_only` boolean -- making a transposition between them impossible by construction, deliberately unlike `mem_util_report_voltage`'s two independent parameters (that helper's under-voltage arm needs a pairing its over-voltage arm does not).
- The helper's leading comment states the resolved single semantic as the plan requires: what the function does; that severity is the CALLER's decision because the four former copies did not agree on how to derive it and one of them (the standalone `CMD_CHECK_CHIP_ID` path) must not agree; that the helper unifies the COMPARISON and PAYLOAD but deliberately not the POLICY; the single-boolean-derives-both-outputs shape and why it differs from `mem_util_report_voltage`'s; and that severity rides entirely in the message id because every `LOG_{WARN,ERROR}_ID_BYTES` macro is the same alias of `LOG_ID_BYTES`.
- Collapsed all four call sites to one line apiece: `flash_util_check_chip_id_execute` (flash_utils.cpp, Site A, `#include "memory_utils.h"` added -- it was absent), `flash_intel_check_chip_id` (flash_intel.cpp, Site B), `eprom_internal_check_chip_id` (eprom.cpp, Site D -- kept its own `uint8_t error_code` parameter and both of its two callers byte-unchanged, translating `error_code == RESPONSE_CODE_WARNING` into `warn_only`, with a one-line comment recording why the parameter survives), and `eeprom28c_check_chip_id` (eeprom_28c.cpp, Site C -- dropped the redundant `(uint16_t)` casts and the superfluous inner brace level along with the block, kept the function `static`).
- Repaired the stale in-source citation at `eeprom_28c.cpp`'s comment block (it pointed at `flash_intel.cpp:112-121` for `flash_intel_check_chip_id`, which now lives at `:153`) by naming the symbol instead of a line number, since Phases 157/158 will move that file again -- an incidental fix inside a comment this plan touches anyway, not a `.planning/` remap and not scope creep.
- Measured DEDUP-02's own flash delta directly: **-158 B on all three AVR targets** (`uno` 24392->24234, `uno328pb` 24440->24282, `leonardo` 26536->26378), RAM unchanged on all three. Combined with DEDUP-01's confirmed `-268 B`, the phase totals exactly **-426 B** on all three targets against `156-before-figures.md`'s `24660/24708/26804` baseline -- landing precisely at `24234/24282/26378`, the phase's stated target. This **confirms** the previously-unverified `-268 / -158` split.
- `__udivmodhi4` call sites: **13** (unchanged from plan 03's landing) -- confirming plan 03's own observation that DEDUP-02's chip-ID blocks carry none of the remaining `__udivmodhi4` traffic (chip-ID comparison is integer equality, not division). `__udivmodsi4` stays at the pre-existing, unrelated **12** sites.
- Per-symbol ledger, `uno`: `mem_util_report_chip_id` measures **0x5a (90 B)**, matching the plan's predicted figure exactly. `flash_util_check_chip_id_execute` 192 B -> **118 B (0x76)**; `flash_intel_check_chip_id` 220 B -> **146 B (0x92)**; `eeprom28c_write_init` 430 B -> **374 B (0x176)**; `eprom_check_chip_id_execute` 6 B -> **24 B (0x18)** (grew -- absorbed part of the inlined helper); `eprom_internal_check_chip_id` (was 260 B) is **ABSENT** from the symbol table, fully inlined into its two callers. Ledger sum: `90 - 74 - 74 - 56 + 18 - 260 = -356 B`, against the measured `-158 B` image delta -- the ledger does **not** close, exactly as expected under `-flto`, because the inlined helper's bytes are redistributed into `main` and the two call sites rather than summing cleanly. Recorded as LTO redistribution with the cause named, never fudged.
- Re-derived `tests/golden/protocol_branch_inventory.json` via `tests/test_protocol_branch_inventory.py`'s own `_extract_predicates()`: 22 sites -> 21, `protocol_keyed_sites` unchanged at exactly 1 (line 70). The removed site is `if (chip_id != handle->chip_id)` (formerly line 764) -- relocated into `mem_util_report_chip_id`'s early return in `src/proms/memory.cpp`, a file this gate does not scan; the `recorded_by` entry states this explicitly as a relocation, never a deletion, and cites `tests/test_hv_routing_source_contract_v142.py` as the sibling gate this exact pattern exists to catch. One surviving site shifted (781 -> 775, the `using_p1_as_vpp` pin-routing fork). The surviving `is_flag_set(FLAG_FORCE)` ternary at line 757 (`eprom_generic_init`'s own caller-policy decision) is a DIFFERENT, untouched site -- not the removed one.
- Full gate sweep post-commit: `pio test -e native` 172/172, `-e native_nodevtools` 172/172, `-e native_loop_v131` 82/82; `python3 -m pytest tests/ -q` **348 passed / 0 failed** (matches `156-before-figures.md`'s canonical-checkout baseline exactly); `python3 -m pytest tests/test_protocol_branch_inventory.py -q` 7/7; `python3 scripts/check_build_warnings.py --rebuild` PASS (uno/uno328pb/leonardo macro-redefinition == 0; native/native_nodevtools 998 observed, 168 below the 1166 watermark -- INFO only, no fail); `python3 scripts/check_size_baseline.py --policy merge05 --rebuild` PASS (all three AVR flash deltas negative and comfortably inside the one-sided MERGE-05 allowance, RAM unchanged, native/native_nodevtools case counts 172/172 -- one-sidedness (D-03) stated: a shrink needs no named exemption to pass).
- `messages.h` byte-unchanged; `tests/test_check_erase_no_vpp.py` (11/11 within the run) and `tests/test_hv_routing_source_contract_v142.py` both re-run and pass (23 total between the two modules) despite touching `eeprom_28c.cpp`.

## The Six-Divergence Resolution Table

| # | Sites affected | Resolution | Reasoning |
|---|---|---|---|
| 1 | severity keyed on `is_flag_set(FLAG_FORCE)` inline (A, B, C) vs. an `error_code` parameter (D) | `bool warn_only` parameter -- A/B/C pass `is_flag_set(FLAG_FORCE)` directly, D passes `error_code == RESPONSE_CODE_WARNING` | **Must NOT be collapsed.** `eprom.cpp`'s two callers of Site D disagree on policy by design: `eprom_check_chip_id_execute` (standalone `CMD_CHECK_CHIP_ID`) passes `RESPONSE_CODE_ERROR` unconditionally; `eprom_generic_init` passes the `FLAG_FORCE`-derived value. Folding `is_flag_set(FLAG_FORCE)` into the helper would silently make the standalone command start honouring `--force`, which it must not. |
| 2 | redundant `(uint16_t)` casts (C only) | Dropped | Provable no-ops: `chip_id` is already `uint16_t` at `eeprom_28c.cpp` (confirmed at its declaration) and `handle->chip_id` is `uint16_t` in `firestarter.h`. Zero behaviour and zero size delta. |
| 3 | superfluous extra brace level (C only) | Dropped | Lexical only, no behaviour change. |
| 4 | the mismatch guard living at the call site (all four) | Moved into the helper's early return | Byte-identical logic at all four sites; consequence tracked in the golden as a RELOCATION into `memory.cpp`, not a deletion. |
| 5 | linkage (C is `static`, A/B/D external) | UNCHANGED | Out of scope; `eeprom28c_check_chip_id` stays `static`, the other three stay externally linked. |
| 6 | `#include "memory_utils.h"` absent from A (`flash_utils.cpp`) | One include added | The declaration is required. This single line shifts all 97 of `flash_utils.cpp`'s `.planning/` citations -- one of the four include additions ROADMAP D-01 measures as causing 41% of the milestone's citation rework. The staleness is expected and close-blocked by REMAP-04; not remapped here. |

**No divergence requires a behaviour change to resolve:** 1 is preserved by parameterisation, 2 and 3 are provable no-ops, 4 is a pure relocation, 5 is untouched, 6 is additive.

## Task Commits

1. **Task 1 + Task 2 + Task 3 (single plan-level commit, per the plan's own "commit once, for the whole plan" instruction):** `2065559` (refactor) -- helper + declaration + four call sites + stale-citation repair + golden re-derivation + test-floor adjustment, all in one commit, anchored `git rev-list --count 6bc3ed3..HEAD == 1`.

**Plan metadata:** committed in the meta repo immediately after this SUMMARY (see the meta repo's own commit log).

## Files Created/Modified

- `firestarter/src/proms/memory.cpp` -- added `mem_util_report_chip_id`, inserted immediately beside `mem_util_report_voltage`
- `firestarter/include/memory_utils.h` -- added the declaration inside the `extern "C"` guard, immediately below `mem_util_report_voltage`'s prototype
- `firestarter/src/proms/flash_utils.cpp` -- Site A collapsed to one call; `#include "memory_utils.h"` added
- `firestarter/src/proms/flash_intel.cpp` -- Site B collapsed to one call
- `firestarter/src/proms/eprom.cpp` -- Site D collapsed to one call, `error_code` parameter and both callers kept byte-unchanged, comment added recording why the parameter survives
- `firestarter/src/proms/eeprom_28c.cpp` -- Site C collapsed to one call (casts and brace dropped), stale citation repaired incidentally
- `firestarter/tests/golden/protocol_branch_inventory.json` -- re-derived: 22 sites -> 21, `blob_shas['src/proms/eprom.cpp']` updated to the post-edit hash, `recorded_at_head` set to this commit's parent (`6bc3ed3`), a sixth `recorded_by` entry appended
- `firestarter/tests/test_protocol_branch_inventory.py` -- non-vacuous floor lowered 22 -> 21 (deviation; see Decisions Made and Deviations from Plan)

## Decisions Made

- **The plan's literal `uint8_t _b[4]` grep check has an unrelated pre-existing collision.** `eprom_internal_report_budget_failure` in `eprom.cpp` (an entirely unrelated function reporting `MSG_ERR_MAX_PULSES`/`MSG_ERR_ENERGY_CAP`) happens to declare a same-shaped `uint8_t _b[4];` for its own {addr_hi, addr_mid, addr_lo, pulse_count} payload. The plan's acceptance grep for "the 4-byte payload array declaration appears zero times" would therefore read 1, not 0. Verified the substantive claim precisely instead: zero `chip_id != handle->chip_id` comparisons remain anywhere in the four files, and `mem_util_report_chip_id(handle` (the actual call, not the comment mentioning its name) appears exactly once per site. `eprom_internal_report_budget_failure` was left completely untouched -- out of scope.
- **Lowered `tests/test_protocol_branch_inventory.py`'s non-vacuous floor from 22 to 21**, in the same commit as the golden re-derivation, following plan 03's identical precedent for the prior `23 -> 22` step. The extraction legitimately produces 21 sites now (the mismatch guard relocated into `memory.cpp`); leaving the hardcoded floor at 22 would make `test_inventory_is_non_vacuous` permanently fail after the commit, contradicting the plan's own acceptance criteria.
- **Self-corrected the golden re-derivation method before committing.** An initial draft matched the prior 22-site inventory to the new 21-site extraction by a `(predicate, keyed_on, tier)` dict key. Three sites in this file share the byte-identical predicate text `if (handle->response_code == RESPONSE_CODE_ERROR)` with identical `keyed_on`/`tier` (lines 146, 177, 676) but distinct `class`/`reason` metadata (a generic status check vs. two Phase-142 single-exit HV-disable gates) -- the dict key silently collapsed all three into one entry, corrupting the sites array (visible immediately as a ~7700-line diff instead of the expected small one). Re-derived using positional, ascending-line-order two-pointer alignment instead -- the same method the gate's own `test_branch_sites_match_the_recorded_inventory` uses to compare recorded vs. live. No incorrect JSON was ever staged or committed.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] The plan's own `uint8_t _b[4]` count-zero acceptance check collides with an unrelated pre-existing declaration**
- **Found during:** Task 2 verification
- **Issue:** `eprom_internal_report_budget_failure` (unrelated to chip-ID reporting; reports `MSG_ERR_MAX_PULSES`/`MSG_ERR_ENERGY_CAP`) declares its own `uint8_t _b[4];` for a differently-shaped payload, pre-dating this plan. The literal grep the plan's acceptance criteria specify (`uint8_t _b\[4\]` count == 0 across the four files) therefore returns 1, not 0.
- **Fix:** Verified the load-bearing claim precisely: `grep -c 'chip_id != handle->chip_id'` across all four files is 0 (all four blocks genuinely gone), and each file calls `mem_util_report_chip_id(handle` exactly once. Left the unrelated function untouched.
- **Files modified:** None (verification-precision only; no code changed as a result)
- **Verification:** `grep -n 'chip_id != handle->chip_id' src/proms/flash_utils.cpp src/proms/flash_intel.cpp src/proms/eprom.cpp src/proms/eeprom_28c.cpp` -> empty. Per-file `mem_util_report_chip_id(handle` count: 1/1/1/1.
- **Committed in:** `2065559` (the single plan commit)

**2. [Rule 3 - Blocking] Golden site-count floor pinned above the new, correct site count**
- **Found during:** Task 3 (re-deriving the golden)
- **Issue:** `tests/test_protocol_branch_inventory.py::test_inventory_is_non_vacuous` hardcoded `assert len(sites) >= 22`. The re-derived golden legitimately has 21 sites (the mismatch guard relocated). Left unedited, this assertion would fail forever after the commit.
- **Fix:** Lowered the floor to 21, following plan 03's own established `23 -> 22` precedent (same comment idiom: called out explicitly, cause named).
- **Files modified:** `firestarter/tests/test_protocol_branch_inventory.py`
- **Verification:** `python3 -m pytest tests/test_protocol_branch_inventory.py -q` -> 7 passed (post-commit).
- **Committed in:** `2065559`

---

**Total deviations:** 2 auto-fixed (both Rule 3 -- blocking issues preventing the plan's own literal acceptance criteria from being satisfiable as written; neither changed the substantive de-duplication, the parameterisation, or the golden's correctness). One additional self-caught authoring mistake (the dict-key collision in the golden re-derivation method) was corrected before anything was staged and is recorded above as a Decision rather than a deviation, since no incorrect artifact was ever committed.
**Impact on plan:** No scope creep. Both deviations are verification-precision or gate-consistency fixes required to make the plan's own success criteria reachable given a pre-existing, unrelated same-shaped declaration and a genuine site-count reduction the plan's literal wording did not special-case.

## Issues Encountered

None beyond the two deviations and the one self-caught authoring mistake, all resolved inline before commit.

## Ceiling Carried Forward

**Divergence 1's gap has no oracle.** There is no test anywhere that exercises `eprom_check_chip_id_execute` (the standalone `CMD_CHECK_CHIP_ID` command) specifically to confirm it ignores `FLAG_FORCE`. `test_case7_mismatching_chip_id_with_force_warns` exercises the mismatch fork through `eprom_generic_init`'s write-path caller, not through the standalone command. The evidence for this claim is source-level only: `eprom_check_chip_id_execute` is byte-unchanged (still passes `RESPONSE_CODE_ERROR` unconditionally) and `mem_util_report_chip_id` contains zero `is_flag_set(FLAG_FORCE)` references. Stated per the plan's own Ceiling 2, not implied covered by a test that does not exist.

## User Setup Required

None -- no external service configuration required. This plan edits firmware source and a committed test golden only.

## Next Phase Readiness

- `firestarter` is now at `2065559` on `gsd/v1.33-source-hygiene-firmware-size-reduction`, tree clean (`git -C firestarter status --porcelain` empty), no worktree remaining beyond the tracked `firestarter_py32_ci` sibling.
- DEDUP-02's own contribution is fully measured and attributable: `-158 B` flash on all three AVR targets, RAM unchanged, golden re-derived from 22 to 21 sites, the chip-ID severity-fork oracle from plan 02 green in both fork directions.
- **The phase's combined DEDUP-01 + DEDUP-02 total is now closed and matches `156-before-figures.md` exactly:** `-426 B` on all three AVR targets (`uno` 24660->24234, `uno328pb` 24708->24282, `leonardo` 26804->26378), RAM unchanged on all three, `__udivmodhi4` down from the measured 31-site baseline to 13.
- **No DEDUP-0X requirement was marked Complete in `.planning/REQUIREMENTS.md`** -- plan 07 is the landing plan that closes them, per this plan's explicit instructions. This plan's contribution: DEDUP-02 in full (helper, four call sites, golden re-derivation, measured flash delta, incidental citation repair); DEDUP-03's "the chip-ID fork survives" half (severity stays a caller-supplied parameter at every call site, re-verified by plan 02's oracle in both fork directions).
- Plan 05 can proceed against `src/eprom_operations.cpp`, `src/operation_utils.cpp` and `include/operation_utils.h`, which this plan explicitly did not touch.

---
*Phase: 156-duplicated-report-extraction-boolean-convention-repair-firmw*
*Completed: 2026-08-23*

## Self-Check: PASSED

- `.planning/phases/156-duplicated-report-extraction-boolean-convention-repair-firmw/156-04-SUMMARY.md` exists on disk -- FOUND
- `firestarter` commit `2065559` (refactor(156-04): one shared chip-ID mismatch report replaces four drifted copies) exists in `git -C firestarter log --oneline --all` -- FOUND

No missing items.
