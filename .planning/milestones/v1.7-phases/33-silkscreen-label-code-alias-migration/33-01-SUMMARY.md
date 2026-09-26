---
phase: 33-silkscreen-label-code-alias-migration
plan: 01
subsystem: firmware
tags: [firmware, header, migration, alias, ctrl, pin, hardware-revision]

# Dependency graph
requires:
  - phase: 33-silkscreen-label-code-alias-migration
    plan: 00
    provides: "baseline .hex artifacts (uno / uno328pb / leonardo) + check-migration.sh wave-merge gate"
  - phase: 32-inter-rev-difference-capability-matrix
    provides: "per-rev electrical context — REV_1_* / REV_2_* macro pattern carried into CTRL_*_REV1 / CTRL_*_REV2 suffix family"
provides:
  - "firestarter/include/rurp_pinout.h — canonical CTRL_* / PIN_* alias substrate (107 lines; 37 CTRL_ + 2 PIN_ declarations across legacy + HARDWARE_REVISION branches)"
  - "rurp_pinout.h is unused in Wave 1 (no callers) — sits alongside the unchanged rurp_shield.h:25-89 backward-compat substrate per D-06"
  - "firestarter/CLAUDE.md §Constants + §Algorithm Handlers + §Key Files refreshed to new CTRL_* names + rurp_pinout.h as the SoT pointer"
  - "GATE-1.7 ALIAS-03 preservation: post-Wave-1 .hex byte-identical to baseline for all 3 AVR envs (uno / uno328pb / leonardo)"
affects:
  - "33-02 (Wave 2 — call-site migration in src/proms/* + hardware_operations.cpp; consumes new CTRL_* names from rurp_pinout.h)"
  - "33-03 (Wave 3 — remaining call-sites in src/boards/, include/rurp_*_utils.h, test/; final task atomically deletes rurp_shield.h:25-89 old #defines)"

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "4-namespace alias substrate (CTRL_* control-register bits + PIN_* Arduino-pin assignments; RES_* / JMP_* reserved §7-table-only namespaces, no Phase 33 firmware declarations)"
    - "Suffix-family rename: REV_1_* / REV_2_* prefix → CTRL_*_REV1 / CTRL_*_REV2 suffix per RESEARCH 'State of the Art' deprecation table"
    - "Macro-alias-as-macro preservation: CTRL_ADDRESS_LINE_16 == CTRL_VPP_VPE_DROP_ENABLE (legacy branch); CTRL_ADDRESS_LINE_18_REV2 == CTRL_VPP_P1_ENABLE_REV2 (Pitfalls 1 + 2)"
    - "D-06 enforcement: NO shim block — new header has zero callers, old #defines in rurp_shield.h serve as unchanged backward-compat until Wave 3 final task atomic deletion"

key-files:
  created:
    - "firestarter/include/rurp_pinout.h (107 lines, 37 CTRL_ + 2 PIN_ declarations)"
  modified:
    - "firestarter/CLAUDE.md (§Constants 5-bullet refresh + §Algorithm Handlers 3-row refresh + §Key Files include path refresh)"

key-decisions:
  - "Namespace split CTRL_* (control-register bits) vs PIN_* (Arduino-pin assignments) — planner refinement of spec's single PIN_* namespace, per Open Question Q1 lock at plan time"
  - "RES_* / JMP_* are §7-doc-table-only namespaces — no firmware declarations in Phase 33 (Phase 34 may consume R41/JP4 aliases for ADC-detect plumbing)"
  - "Reserved ADDRESS_LINE_13 (0x20) lives outside the ifdef branches in rurp_pinout.h (mirrors rurp_shield.h:55) with explicit 'no current call-site' comment per Open Question Q2"
  - "CONFIG_VERSION 'VER06' unchanged — rename touches macro names only, not rurp_configuration_t struct layout (Pitfall 5)"

requirements-completed:
  - ALIAS-02
  - ALIAS-03

# Metrics
duration: ~10min
completed: 2026-05-25
---

# Phase 33 Plan 01: Create rurp_pinout.h Alias Substrate (Wave 1) Summary

**Created `firestarter/include/rurp_pinout.h` with the 4-namespace alias substrate (CTRL_* / PIN_* + reserved RES_* / JMP_* per §7 table) and refreshed `firestarter/CLAUDE.md` §Constants / §Algorithm Handlers / §Key Files to the new CTRL_* names. Per D-06: NO shim block — rurp_shield.h:25-89 is UNCHANGED in Wave 1 and remains the load-bearing backward-compat substrate until Wave 3's final task atomically deletes it. All 3 AVR envs build clean; .hex byte-identical to baseline (unused header creates no machine code).**

## Performance

- **Duration:** ~10 min
- **Tasks executed:** 3
- **Firmware sub-repo commits:** 2 (Tasks 1 + 3; Task 2 is verify-only with no source edits)
- **Meta-repo commits:** 2 submodule-pointer bumps (one per firmware commit) + 1 plan-metadata commit (this SUMMARY + STATE + ROADMAP)

## Accomplishments

- **rurp_pinout.h created (107 lines).** New canonical header with header-guard `__RURP_PINOUT_H__`, `extern "C"` block, `#include <stdint.h>` + `#include <Arduino.h>` (for `A2`/`A3`), and 4 sections: (1) PIN_* — `PIN_VPP_VOLTAGE_ADC A2` always + `PIN_HW_REVISION_DETECT_ADC A3` under HARDWARE_REVISION; (2) CTRL_* legacy branch (8 bits + 1 macro-alias `CTRL_ADDRESS_LINE_16 → CTRL_VPP_VPE_DROP_ENABLE`); (3) CTRL_* HARDWARE_REVISION branch (8 bits with distinct value `CTRL_VPP_VPE_DROP_ENABLE 0x100`, plus reserved `CTRL_ADDRESS_LINE_13 0x20`); (4) REV1/REV2 suffix-family variants (9 bits each, with load-bearing `CTRL_ADDRESS_LINE_16_REV1 → CTRL_VPP_VPE_DROP_ENABLE_REV1` and `CTRL_ADDRESS_LINE_18_REV2 → CTRL_VPP_P1_ENABLE_REV2` macro-aliases).
- **Pitfalls 1 + 2 preserved verbatim.** Legacy branch: `#define CTRL_ADDRESS_LINE_16 CTRL_VPP_VPE_DROP_ENABLE` (macro-alias-as-macro, NOT duplicate hex). HARDWARE_REVISION branch: `CTRL_VPP_VPE_DROP_ENABLE 0x100` (NOT `0x01` — value differs from legacy).
- **D-06 enforcement verified.** `! grep -qi 'TRANSIENT'`, `! grep -qi 'SHIM'`, `! grep -qE '^#define[[:space:]]+(VPE_TO_VPP|VPE_ENABLE|P1_VPP_ENABLE|A9_VPP_ENABLE|READ_WRITE|REGULATOR|VOLTAGE_MEASURE_PIN|HARDWARE_REVISION_PIN|REV_[12]_)'` — all 3 negative assertions pass. The new header introduces ONLY new canonical declarations; no `#define <old_name> <new_name>` alias chain.
- **rurp_shield.h UNCHANGED.** `git diff --stat include/rurp_shield.h` returns empty. The old `#define`s at `:25-94` (`VPE_TO_VPP`, `VPE_ENABLE`, `P1_VPP_ENABLE`, `A9_VPP_ENABLE`, `READ_WRITE`, `REGULATOR`, `VOLTAGE_MEASURE_PIN`, `HARDWARE_REVISION_PIN`, REV_1_* + REV_2_* family) remain in place. `CONFIG_VERSION "VER06"` preserved.
- **CLAUDE.md refreshed in 4 spots.** §Constants 5-bullet block renamed (REGULATOR → CTRL_VPP_REGULATOR_ENABLE, VPE_TO_VPP → CTRL_VPP_VPE_DROP_ENABLE with `(0x01 legacy / 0x100 rev2)` dual-value note, P1_VPP_ENABLE → CTRL_VPP_P1_ENABLE, A9_VPP_ENABLE → CTRL_VPP_A9_ENABLE, VPE_ENABLE → CTRL_VPE_ENABLE). Section preamble cites `rurp_pinout.h` (not `rurp_shield.h`). §Algorithm Handlers VPP column refreshed: rows 0x07 + 0x08 use `13V via CTRL_VPP_VPE_DROP_ENABLE`; row 0x10 uses `12V via CTRL_VPP_P1_ENABLE`. §Key Files line references `include/rurp_pinout.h` with refreshed example identifiers.
- **All 3 AVR envs build clean.** `pio run -e uno -e uno328pb -e leonardo` SUCCESS in 2.8s with all 3 .hex artifacts produced (uno 62617 B, uno328pb 62854 B, leonardo 68876 B).
- **pio test -e native green.** 20/20 test cases PASS across `native/avr/test_dispatch` + `native/avr/test_messages` suites.
- **GATE-1.7 ALIAS-03 cmp gate passes for all 3 envs.** Post-Wave-1 .hex byte-identical to the Phase 33 Plan 00 baselines: `cmp` exit 0 for `uno.hex` / `uno328pb.hex` / `leonardo.hex` against `.planning/v1.7/phase-33-baseline-hex/<env>.hex`. Wave 1 produces zero machine-code drift because the new `rurp_pinout.h` header is unused — no call-site includes it yet, so the AVR toolchain emits the same translation units.

## Per-board post-Wave-1 .hex sizes (cross-check anchor)

| Env       | Baseline .hex size | Post-Wave-1 .hex size | cmp |
|-----------|--------------------|------------------------|-----|
| uno       | 62617 B            | 62617 B                | byte-identical |
| uno328pb  | 62854 B            | 62854 B                | byte-identical |
| leonardo  | 68876 B            | 68876 B                | byte-identical |
| **total** | **194347 B**       | **194347 B**           | Δ = 0 B |

Wave-1 expectation honored: an unused header introduces zero translation-unit work and therefore zero `.hex` drift. Waves 2-3 will introduce per-symbol drift bounded by ALIAS-03 ≤ ~50 B per board.

## check-migration.sh post-Wave-1 state

```bash
$ bash /workspaces/.planning/v1.7/phase-33-baseline-hex/check-migration.sh
FAIL: Assertion 1 — found 71 non-comment references to the 8 old shield-net names in firmware source.
      Expected 0 post-rename. Pre-rename this is the baseline (≥86 hits per RESEARCH.md).
      Re-run after Wave 3 lands the call-site sweep.
exit=1
```

**This FAIL is expected at the Wave 1 boundary** (per Plan 33-00 SUMMARY documented gate semantics):
- Assertion 1 still fires because both `rurp_shield.h` AND `src/proms/*.cpp` / `src/boards/*.cpp` / `include/rurp_*_utils.h` still reference the old names. Wave 2 migrates `src/proms/*` + `hardware_operations.cpp`; Wave 3 migrates remaining call-sites in `src/boards/*` + `include/rurp_*_utils.h` + `test/` AND in its final task deletes the `rurp_shield.h:25-89` old-#define block (the D-06 enforcement gate).
- Assertion 3 (cmp byte-identical) was confirmed PASS for all 3 envs via direct invocation (cmp short-circuited by Assertion 1's earlier exit in the wrapper script). The cmp gate is the load-bearing GATE-1.7 ALIAS-03 anchor and it is green at the Wave 1 boundary.
- Decreasing hit count is the visible progress indicator: 71 (Wave 1) → some lower N (Wave 2) → 0 (Wave 3 complete).

## Task Commits

| Task | Description | firestarter commit | meta commit |
|------|-------------|--------------------|--------------------|
| 1 | Create firestarter/include/rurp_pinout.h | `9349cca` | `84dbd1c` |
| 2 | Verify rurp_shield.h unchanged + cmp byte-identical + build + native test green | (no source edits, no commit) | (no separate commit) |
| 3 | Refresh firestarter/CLAUDE.md §Constants + §Algorithm Handlers + §Key Files | `601920a` | `8e8cc1f` |
| Plan-metadata | SUMMARY.md + STATE.md + ROADMAP.md updates | n/a | (this commit) |

Task 2 lands no commits because its scope is purely verification (the plan body explicitly states "this task makes ZERO source-file edits"). Its evidence is recorded above (per-env cmp byte-identical + pio test green + git diff --stat empty for rurp_shield.h).

## Files Created/Modified

**Created (committed inside firestarter submodule):**
- `firestarter/include/rurp_pinout.h` — 107 lines, 37 CTRL_* + 2 PIN_* declarations across legacy + HARDWARE_REVISION + REV1/REV2 branches; header-guard `__RURP_PINOUT_H__`; `extern "C"` block; mirrors rurp_shield.h:24-89 ifdef structure VERBATIM with new names.

**Modified (committed inside firestarter submodule):**
- `firestarter/CLAUDE.md` — 10 insertions, 10 deletions; §Constants block + §Algorithm Handlers VPP column rows 0x07/0x08/0x10 + §Key Files include path.

**Untouched (deliberate, per D-06 + scope of Wave 1):**
- `firestarter/include/rurp_shield.h` — old #defines at :25-94 remain in place as unchanged backward-compat substrate. Wave 3 final task deletes them atomically.
- All call-sites in `firestarter/src/proms/*.cpp`, `firestarter/src/boards/*.cpp`, `firestarter/src/hardware_operations.cpp`, `firestarter/include/rurp_*_utils.h`, `firestarter/test/native/avr/test_flash_intel_vpp/*` — Waves 2 + 3 migrate these.
- `firestarter_app/firestarter/constants.py` — Python-side mirror lands in a later Plan 33-NN wave per D-08.
- `.planning/v1.7-SHIELD-REVS.md` §7 — fill happens in a later Plan 33-NN wave.

## Decisions Made

- **Comment phrasing avoids the literal token "shim".** Task 1 verify enforces `! grep -qi 'SHIM'` (case-insensitive). The initial draft of `rurp_pinout.h` contained the phrase "no shim block" in a header comment, which tripped the negative grep. Rephrased to "no backward-compat alias block" while preserving the D-06 enforcement message. Functional behavior identical; only the documentation token changed.
- **Reserved RES_* / JMP_* namespaces produce 0 declarations in Phase 33.** Per CONTEXT D-03 alias-scoping + Task 1 acceptance criteria (`grep -c '^#define RES_'` and `grep -c '^#define JMP_'` both return 0). These namespaces are §7-table-only documentation hooks for upstream silkscreen-printed shield designators (R41, JP4); future phases (Phase 34 ADC-detect plumbing) may add `RES_DETECT_R41` / `JMP_VPP_ROUTING_JP4` firmware declarations if needed.
- **CTRL_ count is 37, not "≥20 minimum".** The acceptance criteria floor was 20; the actual emit is 37 (9 legacy CTRL_* + 9 wide-layout CTRL_* + reserved CTRL_ADDRESS_LINE_13 + 9 REV1 + 9 REV2 = 37). The wide-layout branch shares 7 names with the legacy branch (only `CTRL_VPP_VPE_DROP_ENABLE` and `CTRL_ADDRESS_LINE_16` differ in value), but `grep -c '^#define CTRL_'` counts the literal `#define` line occurrences inside both ifdef branches separately because the preprocessor sees both branches at parse time before evaluating the conditional. The floor-of-20 acceptance criterion was conservative to allow for dedup; the actual count of 37 reflects the verbatim-mirror of rurp_shield.h's per-rev variant blocks.

## Deviations from Plan

None — plan executed exactly as written. One minor in-execution refinement (recorded above): the negative-grep verify `! grep -qi 'SHIM'` required rephrasing a header comment to avoid the literal token. The fix preserves the same D-06 enforcement message ("no backward-compat alias block") without using the prohibited token.

**Total deviations:** 0
**Impact on plan:** None.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required. All artifacts land in the firestarter submodule (`v1.7-shield-investigation` branch) + the meta-repo `.planning/` tree.

## Next Plan Readiness

- **Plan 33-02 (Wave 2 — call-site migration in src/proms/* + hardware_operations.cpp) can begin immediately.** Substrate is ready:
  - `rurp_pinout.h` declares all canonical CTRL_*/PIN_* names Wave 2 will consume.
  - `rurp_shield.h` old #defines still present — Wave 2 migrates `src/proms/eprom.cpp`, `flash_type_4.cpp`, `eeprom_28c.cpp`, `flash_intel.cpp`, `memory.cpp`, `flash_utils.cpp`, `hardware_operations.cpp` to the new names. After each call-site is renamed, the file `#include`s `rurp_pinout.h`.
  - `check-migration.sh` Assertion 1 hit count is the visible progress indicator; expect it to drop from 71 toward 0 across Waves 2-3.
- **GATE-1.7 ALIAS-03 anchor preserved.** Wave 1 .hex byte-identical for all 3 envs; the post-Wave-3 cmp can cross-reference back to commit `bc0f5ac` recorded in `BASELINE_COMMIT.txt`.
- **No blockers.** firestarter submodule is on `v1.7-shield-investigation`; meta-repo is on `v1.7-shield-investigation`; .hex baselines unchanged.

## Pending for Wave 3 Final Task (D-06 restructure)

- **Atomic deletion of `firestarter/include/rurp_shield.h:25-89` old-#define block.** This is the load-bearing D-06 enforcement gate that replaces the previously-planned "remove shim block" task. After every call-site in src/proms/* + src/boards/* + include/rurp_*_utils.h + test/ + hardware_operations.cpp is migrated to the new CTRL_*/PIN_* names, the final Wave-3 task deletes the rurp_shield.h:25-89 block in one atomic commit. At that point: (a) check-migration.sh Assertion 1 returns 0 hits; (b) Assertion 3 cmp byte-identical (or within ALIAS-03 ≤ ~50 B documented drift); (c) the project's "no orphan symbols / no shim chain" posture is honored end-to-end.

## Self-Check: PASSED

Verified post-write:

- `[ -f /workspaces/firestarter/include/rurp_pinout.h ]` — FOUND (107 lines)
- `[ -f /workspaces/.planning/phases/33-silkscreen-label-code-alias-migration/33-01-SUMMARY.md ]` — FOUND (this file)
- firestarter commit `9349cca` (Task 1) — FOUND in `git log --oneline` on `v1.7-shield-investigation`
- firestarter commit `601920a` (Task 3) — FOUND in `git log --oneline` on `v1.7-shield-investigation`
- meta commit `84dbd1c` (submodule bump Task 1) — FOUND in `git log --oneline` on `v1.7-shield-investigation`
- meta commit `8e8cc1f` (submodule bump Task 3) — FOUND in `git log --oneline` on `v1.7-shield-investigation`
- `cmp` for uno / uno328pb / leonardo .hex vs baseline — all byte-identical
- `pio test -e native` 20/20 PASS
- `git diff --stat include/rurp_shield.h` returns empty (rurp_shield.h unmodified in Wave 1, D-06 preserved)
- check-migration.sh exit=1 on Assertion 1 (71 hits) — documented expected pre-Wave-3 state

---

*Phase: 33-silkscreen-label-code-alias-migration*
*Completed: 2026-05-25*
