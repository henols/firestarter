---
phase: 156-duplicated-report-extraction-boolean-convention-repair-firmw
verified: 2026-08-23T17:37:53Z
status: passed
score: 4/4 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 156: Duplicated-Report Extraction + Boolean-Convention Repair Verification Report

**Phase Goal:** Collapse two report blocks that were copy-pasted four times each — and, at zero
byte cost, remove the inverted-return convention that needed a ten-line comment to defend itself.
**Verified:** 2026-08-23T17:37:53Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria, verbatim)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | One `mem_util_report_voltage()` replaces four byte-identical VPP packing blocks (`eprom.cpp` x2, `flash_intel.cpp` x2); 8-byte payload and `uint16 + 50` arithmetic preserved exactly; `__udivmodhi4` call sites fall (30/31) → 13 | ✓ VERIFIED | `mem_util_report_voltage` exists at `src/proms/memory.cpp:318`, called from `eprom.cpp:718,718` and `flash_intel.cpp:44,44` (4 sites, confirmed by grep). `git show 6bc3ed3` diff confirms the packing arithmetic (`(x+50)/1000`, `((x+50)/100)%10`, 8-byte layout) is copied byte-for-byte from the four removed blocks, no logic change. Independently rebuilt `uno` at pre-phase commit `adf1a31` in a throwaway worktree: `__udivmodhi4` call-site count measured **31** (not the stale ROADMAP figure of 30 — this is `156-before-figures.md`'s own C-2 correction, itself independently re-confirmed here). Rebuilt final tree `1151dc4`: measured **13**. `31 → 13` confirmed directly, not merely quoted from the phase's own record. |
| 2 | One `mem_util_report_chip_id()` replaces four chip-ID blocks (`flash_utils.cpp`, `flash_intel.cpp`, `eprom.cpp`, `eeprom_28c.cpp`); copies had already drifted (3 inline `is_flag_set(FLAG_FORCE)` vs. `eprom.cpp`'s `error_code` param, `eeprom_28c.cpp`'s redundant casts); resolved single semantic stated, not silently chosen | ✓ VERIFIED | `mem_util_report_chip_id` exists at `src/proms/memory.cpp:360`, called from `flash_utils.cpp:107`, `eeprom_28c.cpp:292`, `eprom.cpp:737`, `flash_intel.cpp:124` (4 sites, confirmed by grep). The helper's own leading comment (`memory.cpp:337-359`) states the resolved semantic explicitly: comparison and payload are unified, policy (the `warn_only` boolean) is deliberately left to the caller so `eprom_check_chip_id_execute`'s unconditional refusal is preserved. Read directly: `eprom_check_chip_id_execute` (`eprom.cpp:117`) calls `eprom_internal_check_chip_id(handle, RESPONSE_CODE_ERROR)` unconditionally, which passes `error_code == RESPONSE_CODE_WARNING` (always false) into `mem_util_report_chip_id` as `warn_only` — the standalone `CMD_CHECK_CHIP_ID` path genuinely still refuses regardless of `--force`. `after-figures.md` §7's six-divergence table matches source inspection. **Caveat, confirmed real:** no test drives `eprom_check_chip_id_execute` through a chip-ID *mismatch* — the one test that exercises this function (`test_vpp03_case_i_cmd_check_chip_id_control_stream_is_pinned_pre_rewrite`) deliberately sets `chip_id == 0xFFFF` matching the mocked readback, a MATCH not a mismatch, and asserts only register-write sequencing, never `response_code` on a mismatch. `REQUIREMENTS.md` DEDUP-02's entry correctly states this is "source-level only" evidence rather than implying test coverage — an honest disclosure, not a hidden gap. |
| 3 | The WARNING/ERROR fork is proven preserved by a test that can see it (a green golden trace alone is insufficient, since every `LOG_{WARN,ERROR}_ID_BYTES` is the same alias of `LOG_ID_BYTES`) | ✓ VERIFIED | Read `include/logging_id.h:105-119`: confirmed both macros alias `LOG_ID_BYTES` identically. Read the actual test bodies (not just SUMMARY prose): `test_vpp04_e`/`test_vpp04_f` (`test/native/avr/test_vpp_eprom_v131/test_vpp_eprom_v131.cpp:847-911`) assert `TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_WARNING, h.response_code, ...)` directly, plus positive/negative message-id assertions in both directions — this genuinely discriminates a `response_code`/id transposition, not merely a golden id match. Ran this suite directly: `pio test -e native_loop_v131 -f "*test_vpp_eprom_v131*"` → 35/35 passed. `test_case7_mismatching_chip_id_with_force_warns` (`test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp:813-919`) asserts `response_code` AND message id in both the WARN and ERROR direction, with an anti-hollow re-drive proving conditionality on `FLAG_FORCE`. Ran directly: `pio test -e native -f "*test_eeprom28c_sdp*"` → 33/33 passed, this env is a CI leg (`build.yml:142`). |
| 4 | The nine `return !op_execute_*_operation(...)` inversions in `eprom_operations.cpp` are removed or explicitly declined with the measurement cited (flip measured byte-for-byte zero on both targets) | ✓ VERIFIED | `grep -c "return !op_execute" src/eprom_operations.cpp` → 0. `grep -cE '^\s*return op_execute_(stateful|simple)_operation' src/eprom_operations.cpp` → 9 (the nine forwarding returns, un-negated). Exactly one negated call survives in the engine (`src/operation_utils.cpp:92`, `return !callback(handle);` — the MAIN-phase delegation, correctly identified as out of scope since the callbacks keep their own opposite convention). Rebuilt all three AVR targets on the final tree: `uno` 24234/1567, `uno328pb` 24282/1573, `leonardo` 26378/2008 — matching the pre-flip figures exactly (size-identical, confirmed independently). The corrected framing ("size-identical, NOT image-identical" — `.hex` SHA changes) is stated honestly in both ROADMAP's corrections paragraph and `156-after-figures.md` §3, not glossed over. The non-vacuous source-contract gate (`tests/test_boolean_convention_source_contract_v133.py`) ran directly: 7/7 passed. |

**Score:** 4/4 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter/src/proms/memory.cpp` — `mem_util_report_voltage` | New shared VPP-report helper | ✓ VERIFIED | Exists at `:250`, 190 B on `uno` (`0xbe`), matches after-figures |
| `firestarter/src/proms/memory.cpp` — `mem_util_report_chip_id` | New shared chip-ID-report helper | ✓ VERIFIED | Exists at `:292`, 90 B on `uno` (`0x5a`), matches after-figures |
| `firestarter/include/memory_utils.h` | Declarations for both helpers | ✓ VERIFIED | Both prototypes present at `:62`, `:73` |
| `firestarter/src/eprom_operations.cpp` | Nine `!` inversions removed | ✓ VERIFIED | Zero `return !op_execute` occurrences; nine plain forwarding returns confirmed |
| `firestarter/src/operation_utils.cpp` | Six engine returns flipped, one negation (callback) retained | ✓ VERIFIED | Exactly one `return !callback(...)` remains, confirmed by grep and by the source-contract test |
| `firestarter/tests/test_boolean_convention_source_contract_v133.py` | Non-vacuous gate for the 9 wrapper sites (never native-compiled) | ✓ VERIFIED | 7/7 tests pass; non-vacuity independently proven by the orchestrator via planted mutations |
| `firestarter/test/native/avr/test_vpp_eprom_v131/test_vpp_eprom_v131.cpp` (new cases E/F) | Under-voltage severity-pairing oracle | ✓ VERIFIED | Both new cases present, both assert `response_code` and message id, both pass (35/35 in-suite) |
| `firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp` (strengthened Case 7) | Chip-ID severity-pairing oracle, both directions | ✓ VERIFIED | Both directions present and asserted, 33/33 in-suite passes |
| `firestarter/tests/golden/protocol_branch_inventory.json` | Re-derived site inventory tracking the two removed branches | ✓ VERIFIED | Recorded `total_sites: 21` (23→22 at 156-03, 22→21 at 156-04); live re-extraction via `pytest tests/test_protocol_branch_inventory.py` passes 7/7 |
| `.planning/v1.33/156-before-figures.md`, `156-after-figures.md` | Authoritative measurement records | ✓ VERIFIED | Both present, both internally cross-checked against the codebase directly by this verification (not merely trusted) |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `eprom.cpp:718,718` / `flash_intel.cpp:44,44` | `memory.cpp:mem_util_report_voltage` | direct call | WIRED | 4 call sites confirmed, arithmetic and severity-parameter passing confirmed byte-identical to the removed blocks |
| `flash_utils.cpp:107` / `flash_intel.cpp:124` / `eprom.cpp:737` / `eeprom_28c.cpp:292` | `memory.cpp:mem_util_report_chip_id` | direct call | WIRED | 4 call sites confirmed, each passing its own caller-derived `warn_only` |
| `eprom_operations.cpp` wrappers | `operation_utils.cpp:op_execute_stateful_operation` / `op_execute_simple_operation` | plain (un-negated) `return` | WIRED | Confirmed via grep; matches `test_boolean_convention_source_contract_v133.py` Coverage 1/2/3 |

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|-------------|-----------------|--------------|--------|----------|
| DEDUP-01 | 156-01, 156-03, 156-07 | VPP report dedup, −268 B | ✓ SATISFIED | Confirmed above (truth 1); REQUIREMENTS.md entry carries the C-1/C-2/C-3 corrections honestly |
| DEDUP-02 | 156-01, 156-04, 156-07 | Chip-ID report dedup, −158 B, resolved divergences | ✓ SATISFIED | Confirmed above (truth 2); the one named coverage gap (standalone-path mismatch) is correctly labeled source-level-only in REQUIREMENTS.md, not overclaimed |
| DEDUP-03 | 156-01, 156-02, 156-03, 156-04, 156-07 | WARNING/ERROR fork proven preserved | ✓ SATISFIED | Confirmed above (truth 3) by directly reading and re-running the discriminating tests |
| DEDUP-04 | 156-01, 156-05, 156-06, 156-07 | Boolean-convention flip, measured zero-cost | ✓ SATISFIED | Confirmed above (truth 4) |

No orphaned requirements: REQUIREMENTS.md's Phase 156 table (`DEDUP-01..04`) matches exactly the union of `requirements:` fields declared across all seven PLAN.md frontmatter blocks.

### Anti-Patterns Found

None. Scanned all seven files this phase touched (`src/proms/eprom.cpp`, `flash_intel.cpp`, `flash_utils.cpp`, `eeprom_28c.cpp`, `memory.cpp`, `src/eprom_operations.cpp`, `src/operation_utils.cpp`) for `TBD|FIXME|XXX|TODO|HACK|PLACEHOLDER` — zero matches.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| `__udivmodhi4` call sites, before | rebuild `uno` at `adf1a31` in a throwaway worktree, `avr-objdump | grep -c` | 31 | ✓ PASS (matches corrected C-2 figure, not stale ROADMAP "30") |
| `__udivmodhi4` call sites, after | rebuild `uno` at `1151dc4`, same command | 13 | ✓ PASS |
| DEDUP-03 under-voltage pairing test | `pio test -e native_loop_v131 -f "*test_vpp_eprom_v131*"` | 35/35 succeeded | ✓ PASS |
| DEDUP-03 chip-ID pairing test | `pio test -e native -f "*test_eeprom28c_sdp*"` | 33/33 succeeded | ✓ PASS |
| DEDUP-04 source-contract gate | `python3 -m pytest tests/test_boolean_convention_source_contract_v133.py -v` | 7/7 passed | ✓ PASS |
| Golden branch-inventory re-derivation | `python3 -m pytest tests/test_protocol_branch_inventory.py -q` | 7 passed, `total_sites: 21` confirmed live | ✓ PASS |
| Flash/RAM final figures | `pio run -e uno -e uno328pb -e leonardo` | 24234/1567, 24282/1573, 26378/2008 | ✓ PASS (matches after-figures exactly, −426 B total, RAM unchanged) |
| Zero remaining `!` wrapper inversions | `grep -c "return !op_execute" src/eprom_operations.cpp` | 0 | ✓ PASS |

### Where This Verification Went Beyond Trusting the Records

- Independently rebuilt the pre-phase commit (`adf1a31`) in a throwaway worktree (removed and pruned afterward) to re-measure the `__udivmodhi4` site count from 0, rather than trusting `156-before-figures.md`'s own "31" figure — got 31, confirming the record's own C-2 correction rather than the stale ROADMAP text.
- Read the actual diff of commit `6bc3ed3` to confirm the VPP packing arithmetic is byte-for-byte identical between the four removed blocks and the new helper, rather than trusting the commit message's "arithmetic preserved exactly" claim.
- Read the actual test bodies (not just SUMMARY prose) for the two DEDUP-03 oracles and confirmed both directly assert `response_code`, which is the specific bar ROADMAP criterion 3 sets ("a test that can see it," explicitly ruling out golden-trace-only evidence).
- Confirmed the DEDUP-02 "no oracle for the standalone unconditional-refusal path" caveat is real by reading the one test that touches `eprom_check_chip_id_execute` and confirming it only drives a chip-ID match, never a mismatch.
- Ran (not just read about) six independent commands: two objdump counts, three PlatformIO test-suite invocations (scoped to the relevant suites, not the whole run), one pytest module, and a full three-target rebuild.

### Human Verification Required

None. This is a firmware-internal refactor with no user-facing behavior, no hardware-only claim made (the phase itself correctly declines to make one — "No bench claim," ceiling 6), and all four success criteria resolve on source inspection, disassembly, and test execution.

### Gaps Summary

No gaps. All four ROADMAP success criteria are independently confirmed against the actual codebase at `firestarter` `1151dc4`, not merely inferred from SUMMARY.md or the phase's own before/after-figures records (though those records were also independently spot-checked and found accurate, including their own self-reported corrections C-1 through C-7). The phase's own honesty about residual coverage ceilings (the standalone chip-ID mismatch path, the LTO ledger's non-closing per-symbol sum, the `.hex`-not-byte-identical DEDUP-04 result) is itself evidence of a well-verified phase, not evidence of incompleteness — none of these ceilings falls inside what the four ROADMAP criteria actually require.

---

_Verified: 2026-08-23T17:37:53Z_
_Verifier: Claude (gsd-verifier)_
