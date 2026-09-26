---
phase: 33-silkscreen-label-code-alias-migration
plan: 03
subsystem: firmware
tags: [firmware, dispatcher, hardware-revision, test, native, migration, ctrl, alias, d-06, atomic-delete, gate-1.7]

# Dependency graph
requires:
  - phase: 33-silkscreen-label-code-alias-migration
    plan: 00
    provides: "baseline .hex artifacts (uno / uno328pb / leonardo) + check-migration.sh wave-merge gate + BASELINE_COMMIT.txt cross-ref"
  - phase: 33-silkscreen-label-code-alias-migration
    plan: 01
    provides: "firestarter/include/rurp_pinout.h — canonical CTRL_*/PIN_* alias substrate consumed by all Wave 2 + 3 call-sites"
  - phase: 33-silkscreen-label-code-alias-migration
    plan: 02
    provides: "src/proms/*.cpp + src/hardware_operations.cpp migrated to CTRL_*; rurp_shield.h:25-89 unchanged (D-06 backward-compat substrate awaiting atomic delete)"
provides:
  - "firestarter/include/rurp_hw_rev_utils.h — rurp_map_ctrl_reg_for_hardware_revision() dispatcher fully renamed (LHS canonical + RHS CTRL_*_REV1/REV2 suffix family); rurp_detect_hardware_revision() pin refs migrated"
  - "firestarter/include/rurp_register_utils.h — settle-check at case CONTROL_REGISTER renamed to CTRL_VPP_P1_ENABLE"
  - "firestarter/src/boards/uno_rurp_shield.cpp — comment refresh READ_WRITE → CTRL_READ_WRITE"
  - "firestarter/src/boards/rurp_common.cpp — analogRead(VOLTAGE_MEASURE_PIN) → analogRead(PIN_VPP_VOLTAGE_ADC); include order fix for Arduino.h"
  - "firestarter/test/native/avr/test_flash_intel_vpp/test_flash_intel_vpp.cpp — mock recorder + SAF-04 assertions migrated to CTRL_VPP_P1_ENABLE (Pitfall 6 native legacy-branch gate)"
  - "firestarter/include/rurp_shield.h — :25-94 old-#define block DELETED ATOMICALLY (D-06 hard-rename enforcement gate); #include \"rurp_pinout.h\" added"
  - "firestarter/include/rurp_pinout.h — stray #include <Arduino.h> removed (latent Wave 1 bug fix uncovered by D-06 atomic delete)"
  - "Post-Wave-3 codebase is steady state — 0 hits for 8 old shield-net names + REV_[12]_ family + ADDRESS_LINE_1[3678] (word-bounded grep)"
  - "GATE-1.7 ALIAS-03 byte-identical preserved end-of-phase-firmware-side: cmp exit 0 for all 3 AVR envs, Δ = 0 B vs Wave 0 baseline"
affects:
  - "33-04 (Python-side mirror + §7 fill — Wave 4)"
  - "Phase 34 (Shield-Version-Detect Design + Firmware Plumbing) — canonical CTRL_*/PIN_* substrate ready for new ADC detect resistor"
  - "Phase 35 (Documentation + Milestone Close) — v1.7-SHIELD-REVS.md §7 alias-table substrate"

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Hard-rename via Edit-per-occurrence — comment refreshes handled deliberately alongside code renames (no sed-bulk)"
    - "Per-file #include rurp_pinout.h added (rurp_hw_rev_utils.h + rurp_register_utils.h + rurp_common.cpp + test_flash_intel_vpp.cpp + rurp_shield.h itself), Task 4 added the include to rurp_shield.h itself so all transitive consumers gain visibility"
    - "Atomic D-06 enforcement: rurp_shield.h :25-94 deleted in a single commit (no shim block was ever introduced — the original declarations themselves served as the backward-compat substrate through Waves 1+2)"
    - "Latch selectors (CONTROL_REGISTER + LEAST_SIGNIFICANT_BYTE / MOST_SIGNIFICANT_BYTE / OUTPUT_ENABLE / CHIP_ENABLE) + REVISION_* enum + VPP_P*_DIP magic constants preserved in rurp_shield.h (out of D-03 alias scope)"

key-files:
  created: []
  modified:
    - "firestarter/include/rurp_hw_rev_utils.h (10 dispatcher renames + 6 detect-fn pin refs + 1 include added)"
    - "firestarter/include/rurp_register_utils.h (1 settle-check rename + 1 comment refresh + 1 include added)"
    - "firestarter/include/rurp_shield.h (70 lines deleted, 1 include added — net shrink ~52 lines)"
    - "firestarter/include/rurp_pinout.h (Rule 1 bug fix — Arduino.h removed from inside extern-C bracketing)"
    - "firestarter/src/boards/uno_rurp_shield.cpp (1 comment-line refresh)"
    - "firestarter/src/boards/rurp_common.cpp (1 ADC-read rename + 1 include added + 1 include-order fix)"
    - "firestarter/test/native/avr/test_flash_intel_vpp/test_flash_intel_vpp.cpp (7 renames + 1 include added)"

key-decisions:
  - "D-06 atomic delete executed in one commit (not split across multiple) — the entire :25-94 block came out in a single Edit and the post-commit grep-zero + cmp-byte-identical + native-test-green gates all passed together"
  - "Rule 1 fix applied to rurp_pinout.h — removed #include <Arduino.h> from inside extern-C wrapper. The header's A2/A3 pin macros are simple integer literals from Arduino's pins_arduino.h; every consumer pulls <Arduino.h> in their own TU. The latent bug from Wave 1 surfaced only when rurp_shield.h started including rurp_pinout.h in the D-06 atomic delete — at which point every TU pulling rurp_shield.h hit conflicting C++ String operator+ declarations inside extern-C"
  - "Rule 3 fix applied to rurp_common.cpp — moved <Arduino.h> before rurp_shield.h to give Arduino.h a clean non-extern-C scope (defensive — kept after the rurp_pinout.h bug fix was also applied)"
  - "check-migration.sh Rule 1 fix — wrapped grep pipelines in `{ … || true; }` so pipefail does not abort when no matches found (the success case). The original script was designed for the Wave-0 baseline where grep would find ≥86 hits"
  - "CONTROL_REGISTER (74HC573 latch selector at rurp_shield.h post-edit :54) preserved verbatim — out of D-03 alias scope per RESEARCH §Anti-Patterns"
  - "REVISION_0/1/2_0/2_1/2_2 hardware-revision enum values preserved verbatim — out of D-03 alias scope (revision identifiers, not RURP-signal aliases)"
  - "VPP_P1_32_DIP / VPP_P1_28_DIP / VPP_P21_24_DIP DIP-bus magic constants preserved verbatim in rurp_shield.h — consumed by using_p1_as_vpp() in memory_utils.h, NOT in the migration name set (no rename needed)"

requirements-completed:
  - ALIAS-02
  - ALIAS-03

# Metrics
duration: ~13min
completed: 2026-05-25
---

# Phase 33 Plan 03: Wave 3 — Remaining Headers + Native Test + Atomic D-06 Delete Summary

**Closed the firmware-side rename sweep: 6 firmware files migrated (dispatcher + settle-check + board adapter comment + ADC-read + native test + atomic rurp_shield.h:25-89 deletion), plus a latent Wave-1 bug fix in rurp_pinout.h's extern-C/Arduino.h bracketing uncovered by the D-06 atomic delete. Post-Wave-3 grep-zero + REV_*-zero + cmp byte-identical for all 3 AVR envs — GATE-1.7 ALIAS-03 met.**

## Performance

- **Duration:** ~13 min
- **Started:** 2026-05-25T11:38:58Z
- **Completed:** 2026-05-25T11:51:35Z
- **Tasks:** 4
- **Firmware sub-repo commits:** 4 (one per task)
- **Meta-repo commits:** 4 submodule-pointer bumps + 1 plan-metadata commit (this SUMMARY + STATE + ROADMAP)
- **Files modified (firmware):** 7

## Accomplishments

- **rurp_hw_rev_utils.h dispatcher fully migrated (LHS canonical input mask + RHS CTRL_*_REV1/REV2 suffix family — Pitfall 3 BOTH sides renamed).** `rurp_map_ctrl_reg_for_hardware_revision()` body at :13-35: LHS `A9_VPP_ENABLE | VPE_ENABLE | P1_VPP_ENABLE | ADDRESS_LINE_17 | READ_WRITE | REGULATOR` → 6× CTRL_*; RHS `REV_2_VPE_TO_VPP / REV_2_ADDRESS_LINE_16 / REV_2_ADDRESS_LINE_18` → `CTRL_VPP_VPE_DROP_ENABLE_REV2 / CTRL_ADDRESS_LINE_16_REV2 / CTRL_ADDRESS_LINE_18_REV2`; RHS `REV_1_VPE_TO_VPP` → `CTRL_VPP_VPE_DROP_ENABLE_REV1`. Bare LHS conditional checks (`data & VPE_TO_VPP` etc.) renamed. Switch-case + REVISION_0/1/2_0/2_1/2_2 case labels + function signature preserved verbatim. `rurp_detect_hardware_revision()` body at :41-58: 3× `HARDWARE_REVISION_PIN` → `PIN_HW_REVISION_DETECT_ADC`; 3× `VOLTAGE_MEASURE_PIN` → `PIN_VPP_VOLTAGE_ADC`. Per-file `#include "rurp_pinout.h"` added alongside `#include "rurp_shield.h"`.

- **rurp_register_utils.h settle-check migrated.** `case CONTROL_REGISTER:` settle-check at :42-44: `if ((control_register & P1_VPP_ENABLE) > (data & P1_VPP_ENABLE))` → `(control_register & CTRL_VPP_P1_ENABLE) > (data & CTRL_VPP_P1_ENABLE)` (both occurrences renamed). Comment line at :17 refreshed: "P1_VPP_ENABLE bit" → "CTRL_VPP_P1_ENABLE bit". `CONTROL_REGISTER` case label and `rurp_map_ctrl_reg_for_hardware_revision(data)` dispatcher call preserved verbatim (latch selector + dispatcher fn out of D-03 scope). `#include "rurp_pinout.h"` added.

- **uno_rurp_shield.cpp comment-only refresh.** Line :29: `// NOTE: The original code included `READ_WRITE` (0x40) …` → `// NOTE: The original code included `CTRL_READ_WRITE` (0x40) …` (per Open Question Q4 — reduces future grep-confusion).

- **rurp_common.cpp ADC-read migrated + Arduino.h include-order Rule-3 fix.** Line :58: `analogRead(VOLTAGE_MEASURE_PIN)` → `analogRead(PIN_VPP_VOLTAGE_ADC)`. `#include "rurp_pinout.h"` added. ADDITIONAL Rule-3 blocking-issue fix (defensive): reordered `#include <Arduino.h>` to BEFORE `#include "rurp_shield.h"` so `<Arduino.h>` is processed in non-extern-C scope before any header that wraps `extern "C"` includes it transitively.

- **test_flash_intel_vpp.cpp mock + assertions migrated (Pitfall 6 — native legacy-branch gate).** :47 mock recorder `(reg & P1_VPP_ENABLE)` → `(reg & CTRL_VPP_P1_ENABLE)`; :187 `TEST_ASSERT_BITS_HIGH(P1_VPP_ENABLE, …)` → `TEST_ASSERT_BITS_HIGH(CTRL_VPP_P1_ENABLE, …)`. 5 comment refreshes at :39 / :163 / :169 / :171 / :186 to keep grep-zero on word-bounded match (note: the verifier filters comment lines, but comments still refreshed for accuracy). `#include "rurp_pinout.h"` added.

- **Atomic D-06 enforcement gate: rurp_shield.h :25-94 DELETED in one commit.** Original block (74 lines) removed entirely:
  - Legacy `#ifndef HARDWARE_REVISION` branch (8 #defines: VPE_TO_VPP, ADDRESS_LINE_16, A9_VPP_ENABLE, VPE_ENABLE, P1_VPP_ENABLE, ADDRESS_LINE_17, ADDRESS_LINE_18, READ_WRITE, REGULATOR)
  - HARDWARE_REVISION `#else` branch (9 #defines, ADDRESS_LINE_16/A9_VPP_ENABLE/…/VPE_TO_VPP wide layout with distinct values)
  - `VOLTAGE_MEASURE_PIN A2` (:21) + `HARDWARE_REVISION_PIN A3` (:36)
  - `ADDRESS_LINE_13 0x20` (:55)
  - `REV_1_*` block (8 #defines + 3 ADDRESS_LINE_* aliases, :72-81)
  - `REV_2_*` block (8 #defines + 1 ADDRESS_LINE_18 alias, :84-93)

  PRESERVED (per Pattern Assignment §2):
  - File header + header guard + `#ifdef __cplusplus extern "C" {` block
  - `#include <stdint.h>`, `<stddef.h>`, `<string.h>`, `<avr/pgmspace.h>`, `"rurp_types.h"`
  - **NEW** `#include "rurp_pinout.h"` added directly after `"rurp_types.h"`
  - `REVISION_0/1/2_0/2_1/2_2` enum values (out of D-03 alias scope) — wrapped in `#ifdef HARDWARE_REVISION` to match prior compile-time gating
  - `VPP_P1_32_DIP / VPP_P1_28_DIP / VPP_P21_24_DIP` DIP-bus magic constants (consumed by `using_p1_as_vpp()` in memory_utils.h — verified by grep, NOT in migration set)
  - `CONFIG_VERSION "VER06"` (Pitfall 5 — NOT bumped; struct layout byte-identical)
  - `VALUE_R1` / `VALUE_R2`
  - `LEAST_SIGNIFICANT_BYTE / MOST_SIGNIFICANT_BYTE / OUTPUT_ENABLE / CONTROL_REGISTER / CHIP_ENABLE` (74HC573 latch selectors — different semantic layer than CTRL_* bits, out of D-03 scope)
  - All function prototypes + `rurp_chip_enable`/`rurp_chip_disable`/`rurp_chip_output`/`rurp_chip_input` macro pair
  - Closing `extern "C"` + header-guard `#endif`

- **All 3 AVR envs build clean post-Wave-3.** `pio run -e uno -e uno328pb -e leonardo` SUCCESS for every commit in the wave (Tasks 1, 2, 3, 4).

- **pio test -e native 20/20 PASS at every wave checkpoint.** Native build path does NOT set `-D HARDWARE_REVISION`, so this exercises the legacy `#ifndef HARDWARE_REVISION` path including the load-bearing `CTRL_ADDRESS_LINE_16 == CTRL_VPP_VPE_DROP_ENABLE` macro-alias-as-macro aliasing (Pitfall 1). All dispatch + message tests green.

- **test_flash_intel_vpp native test compiles + first Unity test PASSES.** Beyond the default `test_filter` allowlist, running `pio test -e native -f test_flash_intel_vpp` shows the file COMPILES (verifying the rename is syntactically + semantically correct against the legacy-branch CTRL_VPP_P1_ENABLE = 0x08 value) and `test_flash_intel_vpp_nominal_proceeds` PASSES. Subsequent SIGABRT in Unity teardown is pre-existing Phase 17 carryover documented in platformio.ini comment, NOT caused by this rename.

- **GATE-1.7 ALIAS-03 cmp byte-identical preserved end-of-phase-firmware-side.** Post-Wave-3 `.hex` files byte-identical to Phase 33 Plan 00 Wave 0 baselines: `cmp` exit 0 for `uno.hex` / `uno328pb.hex` / `leonardo.hex` against `.planning/v1.7/phase-33-baseline-hex/<env>.hex`. SHA256 match: see "Per-board hex measurement" table below.

- **check-migration.sh PASSES — final phase gate green.** Output: `PASS: alias migration verified clean`. All 3 assertions:
  1. **Assertion 1 (grep-zero):** 0 hits for the 8 old shield-net names (VPE_ENABLE, VPE_TO_VPP, P1_VPP_ENABLE, A9_VPP_ENABLE, READ_WRITE, REGULATOR, HARDWARE_REVISION_PIN, VOLTAGE_MEASURE_PIN) across `firestarter/{include,src,test}/` — word-bounded, comments filtered out
  2. **Assertion 2 (REV_*-zero):** 0 hits for `REV_[12]_*` prefix family (REVISION_* enum excluded per D-03)
  3. **Assertion 3 (cmp byte-identical):** all 3 envs byte-identical to baseline

## Per-board hex measurement

| Env       | Baseline size | Post-W3 size | Baseline SHA256 (truncated)        | Post-W3 SHA256 (truncated)        | cmp                          |
|-----------|--------------:|-------------:|------------------------------------|-----------------------------------|------------------------------|
| uno       |        62617 B |       62617 B | `5e7f393a48543b4d…d73be28927` (full match) | `5e7f393a48543b4d…d73be28927` | byte-identical (Δ = 0 B) |
| uno328pb  |        62854 B |       62854 B | `d9e51b7e54fe26af…d22e91ee7` (full match) | `d9e51b7e54fe26af…d22e91ee7` | byte-identical (Δ = 0 B) |
| leonardo  |        68876 B |       68876 B | `9bc0ed128fb0729c…ed6095e` (full match)   | `9bc0ed128fb0729c…ed6095e`   | byte-identical (Δ = 0 B) |
| **total** | **194347 B**   | **194347 B**  | —                                  | —                                 | **Δ = 0 B across all 3**     |

**Full SHA256 values:**
- uno:      `5e7f393a48543b4d2c95f48c37a3751814a3221afebda6866eb4a7d73be28927`
- uno328pb: `d9e51b7e54fe26af6a3286ae8a6e483b56892936c4efd15c13dad9ed22e91ee7`
- leonardo: `9bc0ed128fb0729c6952c2a8e922516fc42a47f49426f3d6e641a6536ed6095e`

Wave 3 expectation honored: `#define` expansion of CTRL_*/PIN_* names in `rurp_pinout.h` produces identical token streams as the (now-deleted) old `rurp_shield.h:25-89` names, so AVR-toolchain output is byte-identical across the atomic rename. The 0-B drift is well under the GATE-1.7 ALIAS-03 ≤ ~50 B per-board budget.

**Baseline commit SHA cross-reference** (`.planning/v1.7/phase-33-baseline-hex/BASELINE_COMMIT.txt`):
`bc0f5ac05b37c94eb7ddc706f65dbdc94c47899e` — cross-referenced in Task 4 fix-commit message per RESEARCH B2 traceability protocol.

## Task Commits

| Task | Description | firestarter commit | meta commit |
|------|-------------|--------------------|-----|
| 1 | Rename rurp_hw_rev_utils.h dispatcher LHS+RHS (10 macro refs) + detect-fn pin refs (6 macro refs) + `#include rurp_pinout.h` | `9560c13` | `6ea9cd4` |
| 2 | Rename rurp_register_utils.h settle-check (2 refs) + uno_rurp_shield.cpp comment refresh + rurp_common.cpp ADC read + Arduino.h include-order fix + `#include rurp_pinout.h` | `255c775` | `bc59b98` |
| 3 | Rename test_flash_intel_vpp.cpp mock recorder + SAF-04 assertions (7 refs, incl. comments) + `#include rurp_pinout.h` | `02c8933` | `7698e18` |
| 4 | Atomic D-06 delete of rurp_shield.h:25-89 old-#define block (70 lines removed) + `#include rurp_pinout.h` added; Rule-1 fix to rurp_pinout.h Arduino.h bracketing | `2707f8c` | `b747ac3` |
| Plan-metadata | SUMMARY.md + STATE.md + ROADMAP.md updates | n/a | (this commit) |

## Files Created/Modified

**Modified (committed inside firestarter submodule):**

- `firestarter/include/rurp_hw_rev_utils.h` — 10 dispatcher renames (LHS canonical mask + RHS CTRL_*_REV1/REV2 suffix family) + 6 detect-fn pin renames + `#include "rurp_pinout.h"` added
- `firestarter/include/rurp_register_utils.h` — settle-check `P1_VPP_ENABLE` → `CTRL_VPP_P1_ENABLE` (2 occurrences in same conditional) + 1 comment refresh + `#include "rurp_pinout.h"` added
- `firestarter/include/rurp_shield.h` — 70 old-#define lines DELETED (full `:25-94` block per D-06 atomic enforcement); `#include "rurp_pinout.h"` added; net shrink from ~194 → ~140 lines
- `firestarter/include/rurp_pinout.h` — `#include <Arduino.h>` REMOVED (Rule 1 latent Wave-1 bug fix uncovered by D-06 atomic delete)
- `firestarter/src/boards/uno_rurp_shield.cpp` — 1 historical-comment refresh (`READ_WRITE` → `CTRL_READ_WRITE`)
- `firestarter/src/boards/rurp_common.cpp` — `VOLTAGE_MEASURE_PIN` → `PIN_VPP_VOLTAGE_ADC` at :58 + `#include "rurp_pinout.h"` added + `#include <Arduino.h>` moved to top (Rule 3 defensive blocking-issue fix)
- `firestarter/test/native/avr/test_flash_intel_vpp/test_flash_intel_vpp.cpp` — 7 renames (2 code, 5 comments) `P1_VPP_ENABLE` → `CTRL_VPP_P1_ENABLE`, `REGULATOR` → `CTRL_VPP_REGULATOR_ENABLE` (comment-only) + `#include "rurp_pinout.h"` added

**Modified (in meta-repo working tree, NOT committed — gitignored per Phase 31 D-11):**

- `.planning/v1.7/phase-33-baseline-hex/check-migration.sh` — wrapped grep pipelines in `{ … || true; }` so `pipefail` does not abort when no matches found (Wave-0 baseline state assumed ≥86 hits; success-case 0-hit state would otherwise cause silent script abort). Script is gitignored; documented here for handoff.

**Untouched (deliberate, per execution-contract scope):**

- `firestarter_app/firestarter/config.py` — preserved drift, unrelated to this phase
- `firestarter_app/firestarter/constants.py` and `main.py` — Python-side mirror lands in a later Plan 33-NN wave per D-08
- `.planning/v1.7-SHIELD-REVS.md` §7 — fill happens in a later Plan 33-NN wave
- `firestarter/src/boards/leonardo_rurp_shield.cpp` — confirmed 0 hits (PATTERNS.md noted this; verified by post-wave grep)
- `firestarter/include/rurp_internal_register_utils.h`, `rurp_serial_utils.h`, `firestarter.h`, etc. — also 0 hits

## Decisions Made

- **D-06 atomic enforcement: rurp_shield.h:25-89 deleted in ONE commit, not split.** The entire 70-line block came out via a single Edit-tool replacement; post-commit grep-zero + cmp-byte-identical + native-test-green gates all passed together. The "rollback path" documented in the plan (Pitfall 1 preservation check via Unity native test) was implicitly verified by the test_dispatch + test_messages 20/20 PASS after the delete — confirming that `rurp_pinout.h`'s legacy `#ifndef HARDWARE_REVISION` branch correctly preserves the `CTRL_ADDRESS_LINE_16 == CTRL_VPP_VPE_DROP_ENABLE` macro-alias-as-macro semantics.

- **Rule 1 fix applied to rurp_pinout.h — Arduino.h removed from inside extern-C wrapper.** The header's A2/A3 pin macros are simple integer literals that resolve via consumers' own `<Arduino.h>` includes. The latent bug from Wave 1 was masked through Waves 1+2 because every .cpp file that consumed CTRL_* names also pre-included `<Arduino.h>` BEFORE rurp_pinout.h (the per-file include pattern from Wave 2). The bug surfaced ONLY when rurp_shield.h itself started including rurp_pinout.h in Task 4 — at which point every TU that pulls rurp_shield.h (which is most of the codebase) hit the conflicting C++ String operator+ declarations inside extern-C. Fixing the header was cleaner than ordering Arduino.h inclusions across ~20 .cpp files.

- **Rule 3 fix applied to rurp_common.cpp — Arduino.h moved before rurp_shield.h.** Kept as a defensive adjustment after the rurp_pinout.h bug fix. This file had Arduino.h at line 12 (after rurp_shield.h at line 8), which was the original include order. The reorder makes the file's include sequence robust against future header changes.

- **check-migration.sh fixed (Rule 1 bug).** The original script had `OLD_NAMES_HITS=$(grep ... | grep -v ... | wc -l)` under `set -euo pipefail`. When grep returns 0 hits (success case), exit=1; pipefail aborts the script before the `if -ne 0` check could run. Wrapped grep pipelines in `{ … || true; }` so the success case yields `OLD_NAMES_HITS=0` and the assertion proceeds normally. Script lives under gitignored `.planning/v1.7/`; bug-fix documented here for handoff.

- **CONTROL_REGISTER preserved verbatim in rurp_shield.h post-edit at :54 + rurp_register_utils.h :38.** Per D-03 + RESEARCH §Anti-Patterns, `CONTROL_REGISTER` is the 74HC573 latch selector (one of 5 latch selectors: LEAST_SIGNIFICANT_BYTE, MOST_SIGNIFICANT_BYTE, OUTPUT_ENABLE, CONTROL_REGISTER, CHIP_ENABLE), NOT a control-register bit alias — different semantic layer than CTRL_* namespace.

- **REVISION_* enum + VPP_P*_DIP magic constants preserved verbatim.** Both are out of D-03 alias scope: REVISION_* are hardware-revision identifiers (matched by the verifier's `grep -v REVISION_` exclusion), and VPP_P*_DIP are DIP-bus magic constants emitted by the Python host's `pin_conversions` table that the firmware compares against in `using_p1_as_vpp()`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Removed stray `#include <Arduino.h>` from `rurp_pinout.h` extern-C wrapper**
- **Found during:** Task 4 (D-06 atomic delete)
- **Issue:** The original rurp_pinout.h (created in Plan 33-01) opened `extern "C"` and then included `<Arduino.h>` inside it. `<Arduino.h>` declares C++ classes (`String`, `StringSumHelper`, `operator+` overloads) that MUST NOT be nested inside `extern "C"`. The bug was latent through Waves 1 + 2 because every consumer pre-included `<Arduino.h>` before `rurp_pinout.h` (the per-file include pattern from Wave 2). The bug surfaced ONLY when rurp_shield.h itself started including rurp_pinout.h in Task 4 (per plan) — at which point every TU pulling rurp_shield.h transitively encountered the conflicting declarations.
- **Fix:** Removed `#include <Arduino.h>` from rurp_pinout.h. Consumers that need A2/A3 macro resolution include `<Arduino.h>` themselves (rurp_hw_rev_utils.h and rurp_common.cpp both already do).
- **Files modified:** firestarter/include/rurp_pinout.h
- **Verification:** All 3 AVR envs build clean; cmp byte-identical for all 3 envs vs Wave 0 baseline; pio test -e native 20/20 PASS
- **Committed in:** `2707f8c` (Task 4 commit, alongside the rurp_shield.h atomic delete)

**2. [Rule 3 - Blocking] Reordered `#include <Arduino.h>` to before `#include "rurp_shield.h"` in rurp_common.cpp**
- **Found during:** Task 2 (rurp_common.cpp ADC-read rename — initial build failure)
- **Issue:** Initially encountered the same Arduino.h + extern-C conflict in rurp_common.cpp specifically (before the broader Task-4 rurp_pinout.h fix). The .cpp file had `<Arduino.h>` at line 12, AFTER `rurp_shield.h` at line 8 — but the new `#include "rurp_pinout.h"` (which then pulled `<Arduino.h>`) was placed inside rurp_shield.h's `extern "C"` block.
- **Fix:** Reordered to put `<Arduino.h>` at line 1 of executable includes, before `rurp_shield.h` + `rurp_pinout.h`. This is a defensive include-order pattern that survives the later Task-4 rurp_pinout.h bug fix.
- **Files modified:** firestarter/src/boards/rurp_common.cpp
- **Verification:** uno + uno328pb + leonardo build clean after the fix
- **Committed in:** `255c775` (Task 2 commit, alongside the ADC-read rename)

**3. [Rule 1 - Bug] Fixed check-migration.sh `pipefail` abort on success-case grep**
- **Found during:** Task 4 (post-delete verifier run)
- **Issue:** check-migration.sh has `set -euo pipefail`. The grep-zero assertion uses `OLD_NAMES_HITS=$(grep ... | grep -v ... | wc -l)`. When the underlying grep finds 0 hits, it returns exit=1. With `pipefail`, the whole pipeline returns non-zero, and `set -e` aborts the script BEFORE the `if -ne 0` check runs — even when the assertion is actually green. The script was designed assuming the Wave-0 baseline state where grep would find ≥86 hits.
- **Fix:** Wrapped grep pipeline stages in `{ … || true; }` so the success-case 0-hit state produces `OLD_NAMES_HITS=0` and the assertion can complete normally.
- **Files modified:** .planning/v1.7/phase-33-baseline-hex/check-migration.sh (gitignored — Phase 31 D-11; not in any commit)
- **Verification:** check-migration.sh now outputs `PASS: alias migration verified clean` with exit 0 against the post-Wave-3 state
- **Committed in:** N/A (script is gitignored; fix lives in working tree; documented here for handoff)

---

**Total deviations:** 3 auto-fixed (1 Rule 1 latent header bug, 1 Rule 3 include-order blocking fix, 1 Rule 1 verifier script bug)
**Impact on plan:** All three deviations were necessary for the planned migration to succeed. Deviation 1 (rurp_pinout.h Arduino.h bracketing) is a Wave-1 latent bug that the plan's D-06 atomic delete naturally surfaced — the plan's rollback-path documentation correctly identified Pitfall 1 as the highest-risk failure mode, and the bug fix path was within scope (header bracketing, not architectural). Deviation 2 (rurp_common.cpp include order) is a defensive adjacent fix. Deviation 3 (check-migration.sh) is a gitignored tooling fix uncovered by exercising the script against its target end-state (post-Wave-3) for the first time.

## Issues Encountered

- **Build failure after Task 2 initial rurp_common.cpp rename — diagnosed and fixed within Task 2.** First attempt at Task 2 introduced the include-order problem documented in Deviation 2. The build failed with "conflicting declaration of C function 'StringSumHelper& operator+'". Diagnosed by inspecting the include chain (rurp_pinout.h opens extern "C" then pulls Arduino.h with C++ classes), fixed by reordering the .cpp's own includes, and the same task commit shipped the rename + fix together. No rollback needed.
- **Build failure after Task 4 initial rurp_shield.h #include "rurp_pinout.h" — diagnosed and fixed within Task 4.** Same root cause as above, but now affecting the WHOLE codebase because rurp_shield.h is transitively included everywhere. Diagnosed by following the rurp_pinout.h:34 (Arduino.h) include chain in the compiler error output, fixed by removing `#include <Arduino.h>` from rurp_pinout.h (the cleaner fix — header A2/A3 macros resolve through consumers' own Arduino.h). All 3 AVR envs + native test green after the fix.
- **check-migration.sh silent abort on success case — diagnosed and fixed within Task 4 verification.** Same script worked at Wave 0 / 1 / 2 boundaries (assertions FAILED with non-zero hit counts, expected). At Wave 3 boundary, with 0-hit success state, the script silently aborted before printing "PASS". Diagnosed by running `bash -x` to trace pipeline behavior under `set -euo pipefail`, fixed with `{ … || true; }` wrappers around grep stages.

## User Setup Required

None — no external service configuration required. All artifacts land in the firestarter submodule (`v1.7-shield-investigation` branch) + the meta-repo `.planning/` tree.

## Phase 33 firmware-side file totals (all 4 waves)

Per the 33-03-PLAN.md output spec:

| Wave | File | Type | Wave-3 disposition |
|------|------|------|--------------------|
| 1 | firestarter/include/rurp_pinout.h | NEW | n/a — Wave-1 created; Rule-1 bug fix landed here in Wave 3 Task 4 (Arduino.h removal) |
| 1 | firestarter/CLAUDE.md | DOC | n/a — Wave-1 refreshed; untouched in W3 |
| 2 | firestarter/src/proms/eprom.cpp | RENAME | done W2 |
| 2 | firestarter/src/proms/memory.cpp | RENAME | done W2 |
| 2 | firestarter/src/proms/flash_intel.cpp | RENAME | done W2 |
| 2 | firestarter/src/proms/flash_type_4.cpp | RENAME | done W2 |
| 2 | firestarter/src/proms/eeprom_28c.cpp | RENAME | done W2 |
| 2 | firestarter/src/proms/flash_utils.cpp | RENAME | done W2 |
| 2 | firestarter/src/hardware_operations.cpp | RENAME | done W2 |
| 3 | firestarter/include/rurp_hw_rev_utils.h | RENAME | done W3 Task 1 |
| 3 | firestarter/include/rurp_register_utils.h | RENAME | done W3 Task 2 |
| 3 | firestarter/src/boards/uno_rurp_shield.cpp | RENAME | done W3 Task 2 |
| 3 | firestarter/src/boards/rurp_common.cpp | RENAME | done W3 Task 2 |
| 3 | firestarter/test/native/avr/test_flash_intel_vpp/test_flash_intel_vpp.cpp | RENAME | done W3 Task 3 |
| 3 | firestarter/include/rurp_shield.h | DELETE+INCLUDE | done W3 Task 4 (atomic D-06 enforcement) |

**Total firmware files modified in Phase 33:** 14 files (1 NEW header + 12 firmware modifications + 1 test) + 1 doc (CLAUDE.md). All Wave-3 acceptance criteria GREEN.

## D-06 Restructure Note

No transient shim block was ever introduced. Per the D-06 restructure plan, the rurp_shield.h:25-89 #defines remained unchanged through Waves 1+2 as the backward-compat substrate — the original declarations themselves served as the resolution path for old-name references in Wave 1's untouched call-sites and Wave 2's still-being-migrated call-sites. Wave 3's final task atomically removed them in one commit, completing the D-06 hard-rename enforcement.

## Next Plan Readiness

- **Plan 33-04 (Wave 4 — Python-side mirror + §7 fill) can begin immediately.** Firmware-side ALIAS-02 + ALIAS-03 are met. The host-side mirror per D-08 (constants.py + main.py docstring) needs the new canonical CTRL_*/PIN_* names as input; those are now stable in `firestarter/include/rurp_pinout.h`. The §7 alias table in `.planning/v1.7-SHIELD-REVS.md` can now be authored against the post-rename state.
- **GATE-1.7 ALIAS-03 anchor preserved through end of Wave 3.** Wave 3 .hex byte-identical for all 3 envs; the cmp gate continues to be the load-bearing constraint for any remaining waves.
- **Phase 34 (Shield-Version-Detect Design + Firmware Plumbing) substrate ready.** New ADC detect resistor design + firmware ADC read path can reuse the CTRL_*/PIN_* substrate; the dispatcher in rurp_hw_rev_utils.h is now spelled in the canonical alias namespace.
- **No blockers.** firestarter submodule + meta-repo both on `v1.7-shield-investigation`. .hex baselines unchanged.

## Threat Flags

None — Phase 33 is a documentation-first / rename-only milestone. No new network endpoints, no new auth paths, no new file access patterns, no schema changes at trust boundaries. The rename produces byte-identical firmware (`cmp` exit 0 across all 3 envs), so attack surface is unchanged.

## Self-Check

Verified post-write:

- `[ -f /workspaces/.planning/phases/33-silkscreen-label-code-alias-migration/33-03-SUMMARY.md ]` — FOUND (this file)
- firestarter commit `9560c13` (Task 1) — FOUND in `git log --oneline` on v1.7-shield-investigation
- firestarter commit `255c775` (Task 2) — FOUND
- firestarter commit `02c8933` (Task 3) — FOUND
- firestarter commit `2707f8c` (Task 4) — FOUND
- meta commit `6ea9cd4` (submodule bump Task 1) — FOUND
- meta commit `bc59b98` (submodule bump Task 2) — FOUND
- meta commit `7698e18` (submodule bump Task 3) — FOUND
- meta commit `b747ac3` (submodule bump Task 4) — FOUND
- `cmp` for uno / uno328pb / leonardo .hex vs baseline — all 3 byte-identical (GATE-1.7 ALIAS-03 PASS)
- `pio test -e native` 20/20 PASS post-wave
- `pio run -e uno -e uno328pb -e leonardo` SUCCESS post-wave
- `bash /workspaces/.planning/v1.7/phase-33-baseline-hex/check-migration.sh` exits 0 with `PASS: alias migration verified clean`
- Word-bounded full-tree grep for 8 old shield-net names + REV_[12]_ family + ADDRESS_LINE_1[3678] (excl. comments + REVISION_*) returns 0 hits

## Self-Check: PASSED

---

*Phase: 33-silkscreen-label-code-alias-migration*
*Completed: 2026-05-25*
