---
phase: 33-silkscreen-label-code-alias-migration
plan: 02
subsystem: firmware
tags: [firmware, call-sites, proms, migration, ctrl, alias, hardware-revision]

# Dependency graph
requires:
  - phase: 33-silkscreen-label-code-alias-migration
    plan: 00
    provides: "baseline .hex artifacts (uno / uno328pb / leonardo) + check-migration.sh wave-merge gate"
  - phase: 33-silkscreen-label-code-alias-migration
    plan: 01
    provides: "firestarter/include/rurp_pinout.h — canonical CTRL_*/PIN_* alias substrate consumed by Wave 2 call-sites"
provides:
  - "firestarter/src/proms/eprom.cpp — 22 call-sites migrated to CTRL_* (UV-EPROM handler, alg 0x07/0x08/0x0B)"
  - "firestarter/src/proms/memory.cpp — 6 call-sites + load-bearing aliasing comment refreshed (top-level dispatch + bus_config mask math)"
  - "firestarter/src/proms/flash_intel.cpp — 7 call-sites migrated (REGULATOR | P1_VPP_ENABLE pattern, alg 0x10)"
  - "firestarter/src/proms/flash_type_4.cpp — 3 call-sites migrated (REGULATOR | VPE_TO_VPP | VPE_ENABLE triplet)"
  - "firestarter/src/proms/eeprom_28c.cpp — 3 call-sites migrated (SAF-05 A9-12V chip-id read)"
  - "firestarter/src/proms/flash_utils.cpp — 3 call-sites migrated (bare READ_WRITE toggle)"
  - "firestarter/src/hardware_operations.cpp — 2 call-sites migrated (hw_read_voltage VPP/VPE branch at :27/:30)"
  - "src/proms/* + src/hardware_operations.cpp is grep-zero for old shield-net names outside comment-only lines"
  - "GATE-1.7 ALIAS-03 preservation: post-Wave-2 .hex byte-identical to Wave 0 baseline for all 3 AVR envs"
affects:
  - "33-03 (Wave 3 — remaining call-sites in src/boards/, include/rurp_*_utils.h, test/native/avr/; final task atomically deletes rurp_shield.h:25-89 old #define block per D-06)"

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Hard-rename via Edit-per-occurrence (no sed-bulk) — comment refreshes handled deliberately alongside code renames"
    - "Per-file #include rurp_pinout.h added directly after #include rurp_shield.h (or where rurp_shield.h is not direct-included, before first CTRL_* reference) — rurp_shield.h does NOT yet transitively include rurp_pinout.h (Wave 3 final task)"
    - "Load-bearing aliasing comment refresh: memory.cpp:142-144 documents CTRL_VPP_VPE_DROP_ENABLE and CTRL_ADDRESS_LINE_16 share the same CONTROL bit (Pitfall 1 documentation under new names)"
    - "CONTROL_REGISTER preserved as latch selector (D-03 anti-pattern bullet — different semantic layer than CTRL_* alias)"

key-files:
  created: []
  modified:
    - "firestarter/src/proms/eprom.cpp (22 lines + comments refreshed at :145, :148, :276, :279, :317)"
    - "firestarter/src/proms/memory.cpp (6 lines + load-bearing aliasing comment at :142-144 refreshed)"
    - "firestarter/src/proms/flash_intel.cpp (7 lines + comments at :34 + :80 refreshed)"
    - "firestarter/src/proms/flash_type_4.cpp (3 lines — REGULATOR | VPE_TO_VPP | VPE_ENABLE triplet)"
    - "firestarter/src/proms/eeprom_28c.cpp (3 lines — eeprom28c_check_chip_id SAF-05)"
    - "firestarter/src/proms/flash_utils.cpp (3 lines — bare READ_WRITE toggle)"
    - "firestarter/src/hardware_operations.cpp (2 lines — hw_read_voltage VPP/VPE branch)"

key-decisions:
  - "Per-file include strategy — files that already include rurp_shield.h add rurp_pinout.h directly after it (eprom, memory, flash_intel, flash_utils, hardware_operations); files that do NOT include rurp_shield.h directly (flash_type_4, eeprom_28c — they get bus access via flash_utils.h transitive chain) add rurp_pinout.h adjacent to operation_utils.h. Avoids relying on a transitive resolution path that does not yet exist (rurp_shield.h → rurp_pinout.h transitive include lands in Wave 3 final task per D-06)."
  - "Comment refresh handled deliberately per file, NOT sed-bulk. memory.cpp:142-144 aliasing comment (Pitfall 1 documentation), flash_intel.cpp:34/:80 caller-asserted-precondition comments, eprom.cpp:145/:148/:276/:279/:317 (eprom_internal_set_control_register function-header), and the load-bearing comment in eprom.cpp:279 (assumes CTRL_VPP_VPE_DROP_ENABLE isn't set) all refreshed to canonical names while their surrounding code renamed."
  - "CONTROL_REGISTER untouched in hardware_operations.cpp:27/:30 — 74HC573 latch selector lives at rurp_shield.h:103 in a different semantic layer than the CTRL_* control-register bits, per RESEARCH §Anti-Patterns and D-03 alias-scoping."

requirements-completed:
  - ALIAS-02
  - ALIAS-03

# Metrics
duration: ~8min
completed: 2026-05-25
---

# Phase 33 Plan 02: Wave 2 — src/proms/* + hardware_operations.cpp Call-Site Migration Summary

**Hard-renamed 46 call-sites across 7 .cpp files in src/proms/ + src/hardware_operations.cpp from the 8 old shield-net names (VPE_ENABLE, VPE_TO_VPP, P1_VPP_ENABLE, A9_VPP_ENABLE, READ_WRITE, REGULATOR, ADDRESS_LINE_16/17/18) to the canonical CTRL_* namespace from rurp_pinout.h (Wave 1 substrate). Per-file `#include "rurp_pinout.h"` added because rurp_shield.h does not yet transitively include it (D-06; Wave 3 final task). GATE-1.7 ALIAS-03 .hex byte-identical to baseline for all 3 AVR envs.**

## Performance

- **Duration:** ~8 min
- **Tasks executed:** 3
- **Firmware sub-repo commits:** 3 (one per task)
- **Meta-repo commits:** 3 submodule-pointer bumps + 1 plan-metadata commit (this SUMMARY + STATE + ROADMAP)
- **Files modified (firmware):** 7

## Accomplishments

- **eprom.cpp — 22 call-sites migrated.** Every reference in the UV-EPROM handler (alg 0x07 / 0x08 / 0x0B) renamed: `programming_bits = VPE_ENABLE` → `CTRL_VPE_ENABLE` at :114; `REGULATOR | VPE_TO_VPP` canonical pattern in `eprom_write_init` :143-149; `REGULATOR` set state changes in `eprom_write_execute` :180; `REGULATOR | VPE_TO_VPP` in `eprom_check_vpp` :197/:204/:219/:222/:270; `REGULATOR` solo in `eprom_internal_erase` :276; `A9_VPP_ENABLE | VPE_ENABLE` erase pulse at :279; `REGULATOR | A9_VPP_ENABLE | VPE_ENABLE` cleanup at :286; `using_p1_as_vpp` helper (VPE_ENABLE → P1_VPP_ENABLE redirect) at :319-321; `REGULATOR` in `eprom_internal_ensure_regulator_enabled` :327-328. Function-header comment for `eprom_internal_set_control_register` also refreshed.
- **memory.cpp — 6 call-sites + load-bearing comment refreshed.** `top_address` mask at :139 (`ADDRESS_LINE_16 | ADDRESS_LINE_17 | ADDRESS_LINE_18 | READ_WRITE` → 4× CTRL_*). `mask = A9_VPP_ENABLE | VPE_ENABLE | P1_VPP_ENABLE | REGULATOR` at :140 (4× CTRL_*). `ADDRESS_LINE_17` at :149. `VPE_TO_VPP` at :144 → `CTRL_VPP_VPE_DROP_ENABLE`. The aliasing comment at :142-144 was the most load-bearing edit: "CTRL_VPP_VPE_DROP_ENABLE and CTRL_ADDRESS_LINE_16 share the same CONTROL bit — preserving CTRL_VPP_VPE_DROP_ENABLE would corrupt A16 for 32-pin (512KB) chips. DIP32 chips use CTRL_VPP_P1_ENABLE instead." (Pitfall 1 documentation honored verbatim).
- **flash_intel.cpp — 7 call-sites + 2 comments migrated.** Every `REGULATOR | P1_VPP_ENABLE` in `flash_intel_write_init` :106/:114/:120, `flash_intel_erase_execute` :145, and `flash_intel_cleanup` :157 renamed to `CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_P1_ENABLE`. Caller-asserted-precondition comments at :34 ("Caller already asserted REGULATOR | P1_VPP_ENABLE") and :80 ("caller continues to use REGULATOR | P1_VPP_ENABLE through the write pulse") refreshed to CTRL_* names — these are part of the SAF-04 ADC-compare contract documentation.
- **flash_type_4.cpp — 3 call-sites migrated.** `REGULATOR | VPE_TO_VPP | VPE_ENABLE` triplet in `flash4_erase_execute` :108/:116/:132 → `CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE | CTRL_VPE_ENABLE`.
- **eeprom_28c.cpp — 3 call-sites migrated.** `eeprom28c_check_chip_id` (SAF-05 A9-12V chip-id read) :70 `REGULATOR, 1` → `CTRL_VPP_REGULATOR_ENABLE, 1`; :72 `A9_VPP_ENABLE, 1` → `CTRL_VPP_A9_ENABLE, 1`; :77 `REGULATOR | A9_VPP_ENABLE, 0` → combined rename.
- **flash_utils.cpp — 3 call-sites migrated.** Bare `READ_WRITE` toggle at :21 (state=0), :25 (state=0), :30 (state=1) renamed to `CTRL_READ_WRITE` — covers both `flash_util_byte_flipping` (asserts CTRL_READ_WRITE low for setup + clear) and `flash_util_verify_operation` (asserts high to poll DQ7).
- **hardware_operations.cpp — 2 call-sites migrated.** `hw_read_voltage` VPP/VPE branch: :27 `REGULATOR | VPE_TO_VPP` → `CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE` (CMD_READ_VPP path); :30 `REGULATOR` → `CTRL_VPP_REGULATOR_ENABLE` (CMD_READ_VPE path). `CONTROL_REGISTER` (74HC573 latch selector) preserved — different semantic layer than CTRL_* per D-03.
- **All 3 AVR envs build clean post-wave.** `pio run -e uno -e uno328pb -e leonardo` SUCCESS for every commit in the wave (Tasks 1, 2, 3).
- **pio test -e native 20/20 PASS** at every wave checkpoint (per-task + post-wave). Native build path does NOT set `-D HARDWARE_REVISION`, so this exercises the legacy `#ifndef HARDWARE_REVISION` path including the load-bearing `CTRL_ADDRESS_LINE_16 == CTRL_VPP_VPE_DROP_ENABLE` macro-alias-as-macro aliasing (Pitfall 1). All dispatch + message tests green.
- **GATE-1.7 ALIAS-03 cmp byte-identical preserved for all 3 envs end-of-wave.** Post-Wave-2 .hex byte-identical to the Phase 33 Plan 00 baselines: `cmp` exit 0 for `uno.hex` / `uno328pb.hex` / `leonardo.hex` against `.planning/v1.7/phase-33-baseline-hex/<env>.hex`. The `#define` expansion produces identical token streams under both the new `CTRL_*` names (defined in `rurp_pinout.h`) and the old shield-net names (still defined unchanged in `rurp_shield.h:25-89`); since both headers compile-time-expand to the same hex values, no machine code drift is introduced.

## check-migration.sh post-Wave-2 state

```bash
$ bash /workspaces/.planning/v1.7/phase-33-baseline-hex/check-migration.sh
FAIL: Assertion 1 — found 33 non-comment references to the 8 old shield-net names in firmware source.
      Expected 0 post-rename. Pre-rename this is the baseline (≥86 hits per RESEARCH.md).
      Re-run after Wave 3 lands the call-site sweep.
exit=1
```

**This FAIL is expected at the Wave 2 boundary** (per Plan 33-00 SUMMARY documented gate semantics). Hit count progression: Wave 0 baseline ≥86 hits → Wave 1 71 hits → **Wave 2 33 hits (−38 from Wave 1)** → Wave 3 0 hits (after final-task deletion of rurp_shield.h:25-89 block).

Where the 33 remaining hits live (all Wave 3 targets — exactly as documented in 33-01 SUMMARY "Next Plan Readiness"):

| File | Hits | Wave 3 disposition |
|---|---|---|
| `firestarter/include/rurp_shield.h` | 16 | DELETE entire :25-94 block atomically (final task) |
| `firestarter/include/rurp_hw_rev_utils.h` | 8 | RENAME — `rurp_map_ctrl_reg_for_hardware_revision()` dispatcher LHS+RHS (Pattern 3, Pitfall 3) |
| `firestarter/test/native/avr/test_flash_intel_vpp/test_flash_intel_vpp.cpp` | 7 | RENAME — Pitfall 6 (mocks + assertions reference P1_VPP_ENABLE / REGULATOR) |
| `firestarter/src/boards/rurp_common.cpp` | 1 | RENAME — `analogRead(VOLTAGE_MEASURE_PIN)` → `analogRead(PIN_VPP_VOLTAGE_ADC)` |
| `firestarter/include/rurp_register_utils.h` | 1 | RENAME — settle-check `(control_register & P1_VPP_ENABLE)` → `CTRL_VPP_P1_ENABLE` |

**Assertion 3 (cmp byte-identical) PASS for all 3 envs end-of-wave** — verified by direct `cmp` invocation (the wrapper script short-circuits on Assertion 1's earlier exit). The cmp gate is the load-bearing GATE-1.7 ALIAS-03 anchor and it is green.

## Per-board post-Wave-2 .hex sizes

| Env       | Baseline .hex size | Post-Wave-2 .hex size | cmp |
|-----------|--------------------|------------------------|-----|
| uno       | 62617 B            | 62617 B                | byte-identical |
| uno328pb  | 62854 B            | 62854 B                | byte-identical |
| leonardo  | 68876 B            | 68876 B                | byte-identical |
| **total** | **194347 B**       | **194347 B**           | Δ = 0 B |

Wave 2 expectation honored: `#define` expansion of the new `CTRL_*` names emits the same hex values as the unchanged `rurp_shield.h:25-89` old `#define`s, so AVR-toolchain output is byte-identical across the rename.

## Task Commits

| Task | Description | firestarter commit | meta commit |
|------|-------------|--------------------|--------------------|
| 1 | Rename eprom.cpp (22 lines + comments) + memory.cpp (6 lines + load-bearing aliasing comment) | `7610a9a` | `fa8203f` |
| 2 | Rename flash_intel.cpp (7) + flash_type_4.cpp (3) + eeprom_28c.cpp (3) + flash_utils.cpp (3) | `99c79ab` | `947f528` |
| 3 | Rename hardware_operations.cpp hw_read_voltage VPP/VPE branch (2 lines at :27/:30) | `00e02c8` | `55009f5` |
| Plan-metadata | SUMMARY.md + STATE.md + ROADMAP.md updates | n/a | (this commit) |

## Files Created/Modified

**Modified (committed inside firestarter submodule):**

- `firestarter/src/proms/eprom.cpp` — 22 lines renamed + 5 comments refreshed; `#include "rurp_pinout.h"` added after `#include "rurp_shield.h"`.
- `firestarter/src/proms/memory.cpp` — 6 lines renamed + load-bearing aliasing comment at :142-144 refreshed; `#include "rurp_pinout.h"` added after `#include "rurp_shield.h"`.
- `firestarter/src/proms/flash_intel.cpp` — 7 lines renamed + 2 caller-precondition comments at :34/:80 refreshed; `#include "rurp_pinout.h"` added.
- `firestarter/src/proms/flash_type_4.cpp` — 3 lines renamed; `#include "rurp_pinout.h"` added adjacent to `#include "operation_utils.h"` (file does not directly include rurp_shield.h).
- `firestarter/src/proms/eeprom_28c.cpp` — 3 lines renamed; `#include "rurp_pinout.h"` added.
- `firestarter/src/proms/flash_utils.cpp` — 3 lines renamed; `#include "rurp_pinout.h"` added after `#include "rurp_shield.h"`.
- `firestarter/src/hardware_operations.cpp` — 2 lines renamed; `#include "rurp_pinout.h"` added.

**Untouched (deliberate, per scope of Wave 2):**

- `firestarter/include/rurp_shield.h` — old `#define`s at :25-94 remain in place as unchanged backward-compat substrate per D-06. Wave 3 final task deletes them atomically.
- `firestarter/include/rurp_hw_rev_utils.h`, `firestarter/include/rurp_register_utils.h` — dispatcher + settle-check still reference old names; Wave 3 migrates.
- `firestarter/src/boards/uno_rurp_shield.cpp`, `leonardo_rurp_shield.cpp`, `rurp_common.cpp` — board adapters; Wave 3 migrates (rurp_common.cpp has 1 reference: `analogRead(VOLTAGE_MEASURE_PIN)`).
- `firestarter/test/native/avr/test_flash_intel_vpp/test_flash_intel_vpp.cpp` — Wave 3 migrates per Pitfall 6.
- `firestarter_app/firestarter/config.py` — preserved drift, unrelated (per execution contract note).
- `firestarter_app/firestarter/constants.py` and `main.py` — Python-side mirror lands in a later Plan 33-NN wave per D-08.
- `.planning/v1.7-SHIELD-REVS.md` §7 — fill happens in a later Plan 33-NN wave.

## Decisions Made

- **Per-file `#include "rurp_pinout.h"` strategy adopted directly.** rurp_shield.h does NOT yet transitively include rurp_pinout.h (that lands in Wave 3 Task 4's atomic edit alongside the :25-94 deletion). To avoid relying on a transitive resolution path that does not yet exist, every .cpp that consumes a new `CTRL_*` name adds `#include "rurp_pinout.h"` directly. Files that already include rurp_shield.h add the new include adjacent to it (eprom, memory, flash_intel, flash_utils, hardware_operations); files that get bus access via flash_utils.h transitive chain (flash_type_4, eeprom_28c) add the include adjacent to operation_utils.h. No build error surfaced — the strategy was confirmed correct on first build of every task.
- **Comment-refresh discipline matched rename per-file.** Six comment blocks across 4 files refreshed: memory.cpp:142-144 (Pitfall 1 aliasing documentation); flash_intel.cpp:34 + :80 (caller-asserted precondition); eprom.cpp:145, :148, :276, :279, :317 (function-header for eprom_internal_set_control_register + load-bearing "assumes VPE_TO_VPP isn't set" inline). Comment refresh kept literal CTRL_* names that match the renamed code immediately above them, so future grep for old names returns clean.
- **CONTROL_REGISTER preserved verbatim in hardware_operations.cpp:27/:30.** Per D-03 + RESEARCH §Anti-Patterns, `CONTROL_REGISTER` is the 74HC573 latch selector (defined at rurp_shield.h:103 alongside `LEAST_SIGNIFICANT_BYTE` / `MOST_SIGNIFICANT_BYTE` / `OUTPUT_ENABLE` / `CHIP_ENABLE`), NOT a control-register bit alias — it lives in a different semantic layer than the `CTRL_*` namespace and is out of scope for Phase 33.

## Deviations from Plan

None — plan executed exactly as written.

The plan's task action text described eeprom_28c.cpp `:70, :72, :77` AND flash_intel.cpp had clusters at `:105-114, :120, :145, :157`. The actual files showed the patterns at the documented line numbers (eeprom_28c was exact; flash_intel had `:106, :114, :120, :145, :157` matching the cluster). One incidental refinement: flash_type_4.cpp and eeprom_28c.cpp did not directly `#include "rurp_shield.h"` (they go through flash_utils.h transitively), so for those two files the new `#include "rurp_pinout.h"` was placed adjacent to `#include "operation_utils.h"` rather than next to a non-existent rurp_shield.h include — same outcome, more accurate placement.

**Total deviations:** 0
**Impact on plan:** None.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required. All artifacts land in the firestarter submodule (`v1.7-shield-investigation` branch) + the meta-repo `.planning/` tree.

## Next Plan Readiness

- **Plan 33-03 (Wave 3 — remaining call-sites in src/boards/, include/rurp_*_utils.h, test/native/avr/) can begin immediately.** Substrate is ready:
  - 33 remaining old-name references concentrated in 5 known files (all Wave 3 targets per RESEARCH inventory).
  - `rurp_pinout.h` from Wave 1 declares every canonical CTRL_*/PIN_* name Wave 3 will consume.
  - `rurp_shield.h:25-89` old #defines still present for AVR build resolution until Wave 3's final atomic task deletes them.
- **GATE-1.7 ALIAS-03 anchor preserved through end of Wave 2.** Wave 2 .hex byte-identical for all 3 envs; the cmp gate continues to be the load-bearing constraint for the remaining waves.
- **No blockers.** firestarter submodule is on `v1.7-shield-investigation`; meta-repo is on `v1.7-shield-investigation`; .hex baselines unchanged.

## Pending for Wave 3 Final Task (D-06 restructure)

- **Wave 3 Task plan (per RESEARCH §Exact Call-Site Inventory + Pattern Assignments §3, §4, §12, §13, §14):**
  1. Rename `include/rurp_hw_rev_utils.h` dispatcher (10 references — LHS canonical input mask + RHS REV_[12]_* per-rev output bits). LHS uses canonical `CTRL_*`; RHS uses suffix-family `CTRL_*_REV1` / `CTRL_*_REV2` names. Pitfall 3 — BOTH sides rename.
  2. Rename `include/rurp_register_utils.h` settle-check at `case CONTROL_REGISTER` (`P1_VPP_ENABLE` → `CTRL_VPP_P1_ENABLE`).
  3. Rename `src/boards/rurp_common.cpp` `analogRead(VOLTAGE_MEASURE_PIN)` at :58 → `PIN_VPP_VOLTAGE_ADC`.
  4. Rename `test/native/avr/test_flash_intel_vpp/test_flash_intel_vpp.cpp` 7 references (mocks + SAF-04 assertions). Pitfall 6 — must include because native build does NOT set `-D HARDWARE_REVISION`.
  5. **Atomic D-06 enforcement**: delete `rurp_shield.h:25-89` old-#define block + add `#include "rurp_pinout.h"` at the top of `rurp_shield.h` (after the existing `#include "rurp_types.h"` at :19). At this point: (a) check-migration.sh Assertion 1 returns 0 hits; (b) Assertion 3 cmp byte-identical preserved; (c) project posture honored end-to-end.

## Self-Check: PASSED

Verified post-write:

- `[ -f /workspaces/.planning/phases/33-silkscreen-label-code-alias-migration/33-02-SUMMARY.md ]` — FOUND (this file)
- firestarter commit `7610a9a` (Task 1) — FOUND in `git log --oneline` on `v1.7-shield-investigation`
- firestarter commit `99c79ab` (Task 2) — FOUND
- firestarter commit `00e02c8` (Task 3) — FOUND
- meta commit `fa8203f` (submodule bump Task 1) — FOUND
- meta commit `947f528` (submodule bump Task 2) — FOUND
- meta commit `55009f5` (submodule bump Task 3) — FOUND
- `cmp` for uno / uno328pb / leonardo .hex vs baseline — all 3 byte-identical (GATE-1.7 ALIAS-03 PASS)
- `pio test -e native` 20/20 PASS at every task + post-wave
- `pio run -e uno -e uno328pb -e leonardo` SUCCESS at every task + post-wave
- `grep -nE '\b(VPE_ENABLE|VPE_TO_VPP|P1_VPP_ENABLE|A9_VPP_ENABLE|READ_WRITE|REGULATOR|ADDRESS_LINE_1[678])\b' firestarter/src/proms/*.cpp firestarter/src/hardware_operations.cpp | grep -v '//' | wc -l` returns 0 — all 7 Wave-2 .cpp files grep-zero outside comment-only lines
- check-migration.sh exit=1 on Assertion 1 (33 hits — all in Wave 3 targets) — documented expected pre-Wave-3 state; Assertion 3 (cmp) green by direct invocation

---

*Phase: 33-silkscreen-label-code-alias-migration*
*Completed: 2026-05-25*
