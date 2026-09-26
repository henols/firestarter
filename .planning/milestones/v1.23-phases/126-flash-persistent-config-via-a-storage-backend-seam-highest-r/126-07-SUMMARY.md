---
phase: 126-flash-persistent-config-via-a-storage-backend-seam-highest-r
plan: 07
subsystem: firmware-storage
tags: [py32f071, flash, dual-slot, crc32, hal-free-core, cortex-m0plus]

# Dependency graph
requires:
  - phase: 126-03
    provides: "include/rurp_config_storage.h seam (D-06/D-07/D-08/D-09) this core sits one level below"
  - phase: 126-06
    provides: "linker symbols __config_slot_a_start/__config_slot_b_start/__config_page_size/__config_region_end and the reserved 8K CONFIG region (D-13/D-18)"
provides:
  - "platform/py32f071/src/config_storage_dualslot.h — HAL-free local header: StoredConfiguration (vendored D-17), CONFIG_MAGIC = 0x52555250 (D-19, not vendored), rurp_flash_primitives_t (three injected primitives), rurp_config_crc32 declaration, rurp_dualslot_load/save declarations, static_assert(sizeof(StoredConfiguration) <= 256)"
  - "platform/py32f071/src/config_storage_dualslot.cpp — the algorithm: table-free reflected CRC-32, V5 validation ordering (magic -> bounds-checked length -> crc32), scan/select-newest, and the D-16-as-amended-by-C-2 save path (erase inactive -> stage 0xFF-filled 64-word page -> program once)"
  - "src/config_storage_dualslot.cpp named in platform/py32f071/CMakeLists.txt's PY32_PLATFORM_SOURCES (manifest gate now at 25 enforced sources)"
affects: ["126-08 (HAL glue config_storage_flash.cpp will supply the real primitives and delete config.cpp)", "126-09 (test_config_storage_dualslot.py will compile this exact core by path against a RAM fake)", "126-12 (closing plan, only one permitted to tick CFG-05)"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Dependency-injected function-pointer primitive table (rurp_flash_primitives_t) so one source file is compiled twice — once against the real HAL, once against a RAM fake — making the tested code the shipped code (D-02). No prior analog existed in this tree."
    - "Validation-as-ordering: magic, then length bounds-checked against the caller's buffer, then crc32 — each gating the next, with the bound check ordered strictly before any copy (V5, load-bearing per the threat model)."
    - "Whole-page staging buffer (uint32_t page[64], 0xFF pre-filled) as the mandatory boundary control between a small RAM record and a HAL that always reads 64 words (C-2)."

key-files:
  created:
    - firestarter/platform/py32f071/src/config_storage_dualslot.h
    - firestarter/platform/py32f071/src/config_storage_dualslot.cpp
  modified:
    - firestarter/platform/py32f071/CMakeLists.txt

key-decisions:
  - "D-16 implemented as amended by C-2, not literally: there is no primitive that writes a trailing header/CRC word (IS_FLASH_TYPEPROGRAM accepts exactly FLASH_TYPEPROGRAM_PAGE; FLASH_Program_Page writes 64 words unconditionally; RM V0.2 §4.2.3.2 hard-faults on a non-32-bit write). The core instead erases the inactive slot, stages the whole 256-byte record in a 0xFF-filled 64-word buffer, and programs it once — completion of that single call is the commit."
  - "CONFIG_MAGIC = 0x52555250 documented explicitly as a this-milestone choice, NOT vendored (D-19) — the blob specifies the field, not the value. Recording this distinction is deliberate, per the Phase 122 C-5 overclaim precedent."
  - "The length bound (rec.length > len) is checked strictly before crc32 and before any copy — the CRC is documented in both the header and the implementation as not a security primitive, so it cannot substitute for the bound check."
  - "sequence has no rollover branch by design (Discretion) — flash endurance bounds the write count many orders of magnitude below 2^32."

patterns-established:
  - "ARM platform-directory conventions followed: Allman braces, unnamed namespace for file-local state (ScanResult, validate_record, scan_slots), extern \"C\" linkage on the four public entry points, matching platform/py32f071/src/timing.cpp."

requirements-completed: []  # CFG-05 spans this plan + 126-08 + 126-09; only 126-12 ticks CFG-01..CFG-07

coverage:
  - id: D1
    description: "HAL-free local header declaring the vendored StoredConfiguration record, CONFIG_MAGIC, the three-primitive injection contract, and the two core entry points, with a compile-time size assertion"
    verification:
      - kind: unit
        ref: "standalone g++ -std=gnu++17 -Wall -Wextra compile of a bare TU including only config_storage_dualslot.h — exit 0, zero bytes stderr"
        status: pass
    human_judgment: false
  - id: D2
    description: "Dual-slot algorithm implementation: table-free reflected CRC-32 anchored to the standard KAT, V5 validation ordering, newest-wins load, and the erase-inactive-then-program-once save path"
    verification:
      - kind: unit
        ref: "temporary RAM-fake harness (outside the repo) exercising all ten behaviours named in the plan's <behavior> block — 0 failures, 0 compile stderr"
        status: pass
    human_judgment: false
  - id: D3
    description: "CMake manifest names the new core in PY32_PLATFORM_SOURCES without promoting rurp_config_utils.cpp or touching PY32_EXCLUDED (scope boundary respected)"
    verification:
      - kind: unit
        ref: "python3 scripts/check_cmake_manifest.py — PASS at 25 enforced sources"
        status: pass
    human_judgment: false
  - id: D4
    description: "No AVR-visible regression: pytest and both pinned native envs unchanged"
    verification:
      - kind: unit
        ref: "python3 -m pytest tests/ -q (138 passed); pio test -e native and -e native_nodevtools (141 test cases: 141 succeeded, 17 suites, each)"
        status: pass
    human_judgment: false

duration: 55min
completed: 2026-07-31
status: complete
---

# Phase 126 Plan 07: The HAL-free dual-slot config storage core Summary

**HAL-free `config_storage_dualslot.{h,cpp}` — table-free reflected CRC-32, magic->bounds-checked-length->crc32 validation ordering, and an erase-inactive-then-program-one-page save path implementing D-16 as amended by C-2 — named in the ARM manifest at 25 enforced sources, with zero new bytes reaching any AVR build.**

## Performance

- **Duration:** ~55 min
- **Completed:** 2026-07-31T23:58:32Z
- **Tasks:** 2
- **Files modified:** 3 (2 created, 1 modified)

## Accomplishments

- Authored `platform/py32f071/src/config_storage_dualslot.h`: the vendored six-field `StoredConfiguration` record (D-17, `rurp_configuration_t` embedded byte-for-byte), `CONFIG_MAGIC = 0x52555250` defined once and explicitly marked not-vendored (D-19), the `rurp_flash_primitives_t` three-primitive injection contract (D-02), and the two core entry point declarations — all HAL-free, guard-free, and standalone-compilable under host `g++`.
- Authored `platform/py32f071/src/config_storage_dualslot.cpp`: a table-free bitwise reflected CRC-32 (KAT-verified), a validation helper enforcing the V5 order (`magic` → bounds-checked `length` → `crc32`, computed with `offsetof`), `rurp_dualslot_load` (scan, newest-wins, D-15 blank/corrupt indistinguishability), and `rurp_dualslot_save` (determine active slot by the same scan, erase the inactive slot, stage a `0xFF`-filled 64-word page, program it once — the D-16-as-amended-by-C-2 commit shape).
- Added `src/config_storage_dualslot.cpp` to `PY32_PLATFORM_SOURCES` — the manifest gate now reports 25 enforced sources, and no other list or exclusion was touched.
- Proved the header compiles standalone and the implementation behaves correctly using a temporary RAM-fake harness built and run outside the repository, then deleted before committing.

## Task Commits

Each task was committed atomically:

1. **Task 1: The local header** — `64e449d` (feat) — `platform/py32f071/src/config_storage_dualslot.h`
2. **Task 2: The core implementation + manifest entry** — `4d3557a` (feat) — `platform/py32f071/src/config_storage_dualslot.cpp`, `platform/py32f071/CMakeLists.txt`

**Plan metadata:** this SUMMARY commit (docs, meta repo)

## Files Created/Modified

- `firestarter/platform/py32f071/src/config_storage_dualslot.h` — local ARM-only header (245 lines); include set is exactly `<stdbool.h>`, `<stddef.h>`, `<stdint.h>`, `"rurp_types.h"`; no HAL include, no `#error` guard, no `rurp_config_storage.h` include.
- `firestarter/platform/py32f071/src/config_storage_dualslot.cpp` — the HAL-free core (233 lines); include set is exactly `"config_storage_dualslot.h"` plus `<string.h>`.
- `firestarter/platform/py32f071/CMakeLists.txt` — one line added to `PY32_PLATFORM_SOURCES`: `src/config_storage_dualslot.cpp`. `FIRESTARTER_COMMON_SOURCES` (17), `PY32_SDK_SOURCES` (14) and the six `PY32_EXCLUDED` lines are untouched.

## Verification Detail (for the record)

**Header standalone compile:**
```
g++ -std=gnu++17 -Wall -Wextra -I include -I platform/py32f071/src <bare-TU-with-empty-main>
exit 0, 0 bytes stderr
```
Observed `sizeof(StoredConfiguration)` on this host: **48** (host `long` is 8 bytes: 4+2+2+32(configuration, 8-byte aligned)+4+4 = 48). Observed AVR `sizeof(StoredConfiguration)` via `avr-g++ -mmcu=atmega328p` (toolchain present at `~/.platformio/packages/toolchain-atmelavr/bin/`): **31** — matched via `avr-objdump -t` on two `.bss` symbols of those exact sizes, confirming both `sizeof(StoredConfiguration) == 31` and `sizeof(rurp_configuration_t) == 15` on AVR, exactly as this plan's acceptance criteria expected. The ARM figure (36) is **not measured** in this container (`arm-none-eabi-gcc` is absent) and is carried forward as the value already computed and recorded in `CONFIG-STORAGE.md`/`126-RESEARCH.md` (C-6) — not re-derived here. Only the relational assertion `sizeof(StoredConfiguration) <= 256` is load-bearing; it held on both measured compilers (48 and 31, both ≤ 256).

**Implementation's validation order, quoted from the source (`validate_record`):**
1. `if (rec.magic != CONFIG_MAGIC) return false;`
2. `if (rec.length > len) return false;` — before any copy, and before the CRC check.
3. `const uint32_t computed = rurp_config_crc32(&rec, offsetof(StoredConfiguration, crc32)); if (rec.crc32 != computed) return false;`

**CRC known-answer result:** `rurp_config_crc32("123456789", 9) == 0xCBF43926` — observed via the temporary harness, matching the standard reflected CRC-32 vector exactly.

**All ten behaviours, observed on the temporary RAM fake (results crossed on stdout, never inferred from exit code):**

| # | Behaviour | Observed |
|---|---|---|
| 1 | `rurp_config_crc32("123456789", 9) == 0xCBF43926` | PASS |
| 2 | Both slots blank → `load()` returns `false`, caller blob untouched | PASS (2 checks) |
| 3 | Both slots valid → higher `sequence` wins | PASS (2 checks) |
| 4 | One valid, one CRC-corrupted → the valid one returned | PASS |
| 5 | Both slots corrupt (bad CRC) → `false`, same outcome as blank (D-15) | PASS |
| 6 | `length` > caller's `len` → rejected before any copy, buffer not written past `len` | PASS (2 checks) |
| 7 | `save` erases only the inactive slot, never both, never the active one | PASS |
| 8 | Abort-after-N word stores, N ∈ {0, 1, 32, 63, 64}, leaves the system always loadable | PASS (all 5 N values, see note below) |
| 9 | Successive saves alternate slots | PASS (verified via the N=2-save sequence in behaviour 3) |
| 10 | `program_page` on a page not just erased is a fake-detected failure, armed and untriggered across ordinary saves, then deliberately triggered once | PASS (2 checks) |

**Observed nuance on abort-after-N (worth recording precisely, not glossed over):** the record's own footprint is `ceil(sizeof(StoredConfiguration)/4)` words — 12 words (48 bytes) on this host, since the words are written in strictly increasing index order starting at word 0. For **N < 12** (covers N=0, N=1 in the tested set), the record — including its trailing `crc32` — is genuinely torn: `load()` correctly falls back to the untouched active slot's previous record. For **N ≥ 12** (covers N=32, N=63, N=64 in the tested set), the record's own bytes are already fully and correctly committed even though the primitive call itself reports non-completion for N<64 (the remaining words, 12–63, were always going to stay `0xFF` padding regardless) — so `load()` correctly returns the **new** record, not the previous one. In every one of the five N values, `load()` never fails and never returns garbage — the T-126-07-04 property (a torn write never bricks the unit) holds in its strongest form: the outcome is always *a* coherent, CRC-valid record, and only the identity of which record (previous vs. new) depends on where the abort falls relative to the record's own footprint versus the full 64-word burst. This is a stronger guarantee than "previous record loadable" read as a blanket claim across all five N values, and it is recorded here rather than forced to match an imprecise paraphrase.

**Manifest gate:** `python3 scripts/check_cmake_manifest.py` → `PASS: ... 25 enforced source(s) resolved`. `FIRESTARTER_COMMON_SOURCES` unchanged at 17 entries, `PY32_SDK_SOURCES` unchanged at 14 (structurally exempt), six `PY32_EXCLUDED` allow-list lines unchanged.

**Regression counts:** `python3 -m pytest tests/ -q` → **138 passed** (unchanged from the 126-06 baseline). `pio test -e native` → **141 test cases: 141 succeeded** across 17 suites. `pio test -e native_nodevtools` → **141 test cases: 141 succeeded** across 17 suites. Both pinned native envs unchanged; zero new bytes reach any AVR build (no `src/` file was touched or added to `FIRESTARTER_COMMON_SOURCES` by this plan).

**Hash checks (hard constraints):** `include/rurp_types.h` = `d3fe5203a91527bdb7b20a33843c81065e21c613` (unchanged). `include/rurp_shield.h` = `602fe6f326a042ab71efd111e4dfcf3a6e41dd46` (unchanged). `include/rurp_config_storage.h` = `1d74d0ede91853c2ce2bcc0bda1eb8fe8a07e5b2` (unchanged). `platform/py32f071/linker/PY32F071xB_FLASH.ld` = `571a588b0521e9602d98f735e3166a9869dab3aa` (unchanged).

**Commit SHAs and changed paths:**
- `64e449d` — `platform/py32f071/src/config_storage_dualslot.h` (1 file, 245 insertions)
- `4d3557a` — `platform/py32f071/src/config_storage_dualslot.cpp`, `platform/py32f071/CMakeLists.txt` (2 files, 234 insertions)

**Harness hygiene:** the temporary RAM-fake harness lived entirely under the scratchpad directory, outside `/workspaces/firestarter`. `git status --porcelain` inside the firmware repo showed only the two intended files before each commit and 0 lines after.

**Branch re-check (both repos, RESEARCH Pitfall 7):** `git -C /workspaces/firestarter rev-parse --abbrev-ref HEAD` → `v1.23-py32f071-integration` (after both commits). Meta repo unaffected by this plan's firmware commits (SUMMARY commit lands separately, in the meta repo, per this plan's protocol).

**Gitignored py32 worktrees:** `git -C /workspaces/firestarter_py32_ci status --porcelain` and `git -C /workspaces/firestarter_app_py32 status --porcelain` — both produced no output (untouched).

## Decisions Made

- Implemented D-16 **as amended by C-2**, not its locked literal text (see `<d16_is_amended_do_not_implement_it_literally>` in the dispatch prompt and `CONFIG-STORAGE.md`'s own amendment section): the completion of one whole-page program **is** the commit; there is no separate header/CRC/final-word step anywhere in this core.
- `CONFIG_MAGIC` documented as a this-milestone choice, explicitly not vendored (D-19) — distinct from the vendored `StoredConfiguration` layout (D-17).
- CRC32 documented, in both the header and the implementation, as detecting accidental corruption only — never described as a security, authentication, or tamper-resistance primitive, per the plan's explicit prohibition.
- The `length` bounds check is ordered strictly before the `crc32` check and before any copy — the load-bearing V5 ordering, not merely a set of independent checks.
- Chose `sizeof(rurp_configuration_t)` as the bound for `rurp_dualslot_save`'s internal active-slot scan (rather than reusing the caller's `len`, which `save()` does not need for validation purposes beyond sizing the embedded configuration copy) — this matches the seam's documented real-world contract (`include/rurp_config_storage.h`: every real caller passes exactly `sizeof(rurp_configuration_t)`), so `load()` and `save()`'s internal scan agree on which slot is active by construction.

## Deviations from Plan

None — plan executed exactly as written. The one item worth flagging is not a deviation from the *plan* but a corrected assumption in my own *scratch test harness*: my first draft of the abort-after-N=32/63 test cases wrongly expected the previous record to be returned in all cases below N=64. Re-deriving from the actual record footprint (12 words on this host) showed the correct, and more informative, behaviour documented above under "Observed nuance on abort-after-N" — the test was corrected in the scratch harness before it was deleted; nothing in the committed `.h`/`.cpp` needed any change as a result. No files listed in `files_modified` were touched beyond what the plan specified.

## Non-Claims (Claim Ceiling, explicit)

- **No ARM build was performed or is claimed.** `arm-none-eabi-gcc`, `cmake`, and `ninja` are absent from this environment; the computed ARM `sizeof(StoredConfiguration) = 36` is carried forward from `CONFIG-STORAGE.md`/`126-RESEARCH.md`, not re-derived here.
- **No PY32F071 silicon exists**, and nothing here claims behaviour observed on real hardware.
- **No power-loss-on-hardware claim.** The abort-after-N demonstration is a RAM-fake simulation of an interrupted flash-program primitive, not an observation of a real reset during a real flash write.
- **No DFU-preservation claim.** This plan does not touch the host DFU tooling or exercise an install.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `rurp_flash_primitives_t`, `rurp_dualslot_load`, `rurp_dualslot_save`, and `rurp_config_crc32` are ready for Plan 126-08 to supply real HAL-backed primitives in `config_storage_flash.cpp`, delete `platform/py32f071/src/config.cpp`, and promote `src/rurp_config_utils.cpp` into `FIRESTARTER_COMMON_SOURCES` (all deliberately deferred to that plan, per this plan's manifest scope boundary).
- Plan 126-09 can compile `config_storage_dualslot.cpp` by path against its own committed RAM fake and the six named test functions; this plan's temporary harness (now deleted) demonstrated the same ten behaviours 126-09 is expected to assert formally, plus the one nuance on abort-after-N documented above for that plan's author to consider when writing its own N-value assertions.
- No blockers. Both native envs remain at 141/141 across 17 suites; `pytest tests/` remains at 138; the manifest gate is green at 25 enforced sources.

---
*Phase: 126-flash-persistent-config-via-a-storage-backend-seam-highest-r*
*Completed: 2026-07-31*

## Self-Check: PASSED

- FOUND: firestarter/platform/py32f071/src/config_storage_dualslot.h
- FOUND: firestarter/platform/py32f071/src/config_storage_dualslot.cpp
- FOUND: .planning/phases/126-.../126-07-SUMMARY.md (this file)
- FOUND: commit 64e449d (Task 1, firestarter repo)
- FOUND: commit 4d3557a (Task 2, firestarter repo)
- FOUND: commit bc4c960 (SUMMARY, meta repo)
