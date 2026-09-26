---
phase: 126-flash-persistent-config-via-a-storage-backend-seam-highest-r
plan: 06
subsystem: firmware/py32f071 linker + flash-map gates
tags: [linker-script, py32f071, flash-config, cfg-02, cfg-06, pytest-gate]

requires:
  - phase: 126-01
    provides: "platform/py32f071/CONFIG-STORAGE.md (the CFG-02 flash-geometry record, its adding commit fd84820 is the ordering anchor)"
  - phase: 126-04
    provides: "the CFG-04 AVR-side move, unrelated to this plan's edits but a wave dependency"
provides:
  - "platform/py32f071/linker/PY32F071xB_FLASH.ld reserving Sector 15 (0x0801E000, 8K) at the top of flash, FLASH shrunk 128K->120K, a zero-length BOOTLOADER seam (D-13), four PROVIDEd symbols (D-11), and two structural ASSERTs (no modulo)"
  - "tests/test_flash_geometry_recorded_before_linker.py: CFG-02's ordering half as an exit code, with a non-vacuity guard, explicit git-tool-error handling, and a two-synthetic-repo RED demonstration"
  - "tests/test_py32_flash_map.py: CFG-06's map properties as an exit code (sector alignment, physical bounds, slot spacing, symbol presence, bootloader-seam shape, wrong-figure rejection), with a six-planted-copy RED demonstration"
affects: [126-08, 126-11, 129]

tech-stack:
  added: []
  patterns:
    - "one module-level ordering helper (_find_ordering_violations) parameterised by (repo_root, record_path, linker_path), shared by real-repo and synthetic-repo tests"
    - "textual drift-gate parser (_parse_regions / _parse_symbols) over the .ld MEMORY/PROVIDE blocks, shared by positive tests and planted-copy mutation tests"
    - "sector-alignment and bounds arithmetic kept in Python, never as a linker ASSERT with modulo (RESEARCH A6)"

key-files:
  created:
    - firestarter/tests/test_flash_geometry_recorded_before_linker.py
    - firestarter/tests/test_py32_flash_map.py
  modified:
    - firestarter/platform/py32f071/linker/PY32F071xB_FLASH.ld

key-decisions:
  - "D-18's whole-Sector-15 reservation implemented exactly as recorded in CONFIG-STORAGE.md: CONFIG at 0x0801E000, LENGTH 8K, not the minimal 512 B two-erase-unit reading"
  - "No ASSERT uses modulo on a region origin (RESEARCH A6) -- sector-alignment and physical-bounds arithmetic moved entirely into tests/test_py32_flash_map.py"
  - "BOOTLOADER region shape (not the A7 fallback PROVIDE-pair) was used: the host ld syntax probe raised no diagnostic naming a script line, so the A7 contingency was not needed"
  - "D-13's migration-cost comment written verbatim as specified: 'MOVES the application's ORIGIN', 'MIGRATION, not a resize', 'every previously flashed unit's vector table address changes'"

requirements-completed: []

coverage:
  - id: D1
    description: "Linker script reserves Sector 15 (CONFIG at 0x0801E000/8K) at top of flash, FLASH shrunk 128K->120K, zero-length BOOTLOADER seam, four PROVIDEd symbols, two structural ASSERTs"
    requirement: "CFG-06"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_py32_flash_map.py (14 functions)"
        status: pass
    human_judgment: false
  - id: D2
    description: "CFG-02's ordering constraint (geometry record precedes every in-phase linker commit) proven as an exit code, non-vacuous, with a synthetic-repo RED demonstration"
    requirement: "CFG-02"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_flash_geometry_recorded_before_linker.py (8 functions)"
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-07-31
status: complete
---

# Phase 126 Plan 06: PY32F071 Linker Flash-Map Reservation + CFG-02/CFG-06 Gates Summary

**Reserved Sector 15 (0x0801E000, 8K) at the top of PY32F071xB_FLASH.ld's flash map with a shrunk 120K app region, a zero-length D-13 bootloader seam, four PROVIDEd linker symbols, and two structural (non-modulo) ASSERTs -- then proved both CFG-02's commit-ordering constraint and CFG-06's map properties as exit codes, each with its own RED demonstration.**

## Performance

- **Duration:** ~25 min
- **Tasks:** 3/3 completed
- **Files modified:** 1 modified (linker script), 2 created (test modules)

## Pre-edit confirmation

`platform/py32f071/CONFIG-STORAGE.md`'s adding commit was confirmed present in `HEAD` before any edit: **`fd84820e41788eab4da2c7c8d17d6475270980e3`** (matches 126-01-SUMMARY.md exactly). The linker script was confirmed still at its pinned pre-phase hash **`b32b5824c8e27492551db5c2b1d413f74f05b6f3`** immediately beforehand -- this plan's Task 1 commit is the first to touch it.

## Task 1 -- Reserve Sector 15 in the linker script

Edited `platform/py32f071/linker/PY32F071xB_FLASH.ld`. The new `MEMORY` block, verbatim:

```ld
/* Flash map. Geometry is NOT guessed here -- see platform/py32f071/CONFIG-STORAGE.md
 * §"Flash geometry": Puya PY32F07X Reference Manual V0.2 §4.1/§4.2.1/Table 4-1,
 * page = 256 B, sector = 8192 B, main flash 0x08000000..0x0801FFFF (128 KiB).
 * That record landed in a commit PRECEDING this file's first edit (CFG-02).
 */
MEMORY
{
    /* D-13 -- NAMED SEAM ONLY, ZERO LENGTH, for Phase 129 (PCB-03/FUT-N05) to cite.
     *
     * READ THIS BEFORE GIVING IT A SIZE. Unlike the CONFIG region below -- which
     * sits at the TOP of flash and can grow downward without moving anything --
     * giving BOOTLOADER a non-zero length MOVES the application's ORIGIN. That is
     * a flash-map MIGRATION, not a resize: every previously flashed unit's vector
     * table address changes, on a part with no VTOR. Phase 129 must record the
     * bootloader budget as an INTENT WITH THAT COST ATTACHED, never as a number
     * that looks already paid for.
     */
    BOOTLOADER (rx) : ORIGIN = 0x08000000, LENGTH = 0

    /* Shrunk from 128K so .text/.rodata physically CANNOT reach CONFIG (D-10).
     * 0x1E000 = 120K -> app occupies 0x08000000..0x0801DFFF (sectors 0..14). */
    FLASH (rx)  : ORIGIN = 0x08000000, LENGTH = 120K

    /* Sector 15 (RM Table 4-1: pages 480-511) -- D-18 amends D-10's shrink
     * quantum to one whole 8 KiB sector. The two slots below are different
     * PAGE erase units, which is what CFG-06 requires; aligning the region to
     * a whole sector additionally means no sector-granular erase of the app
     * region can ever clip it. 7680 B of this 8192 B reservation is deliberate
     * slack, reclaimable later by FUT-N05 or by additional config slots
     * without moving any address. */
    CONFIG (r)  : ORIGIN = 0x0801E000, LENGTH = 8K

    RAM   (xrw) : ORIGIN = 0x20000000, LENGTH = 16K
}
```

Four `PROVIDE`d symbols and two `ASSERT`s (no modulo -- see below):

```ld
PROVIDE(__config_page_size    = 256);
PROVIDE(__config_slot_a_start = ORIGIN(CONFIG));                   /* 0x0801E000, page 480 */
PROVIDE(__config_slot_b_start = ORIGIN(CONFIG) + 256);             /* 0x0801E100, page 481 -- a different page erase unit */
PROVIDE(__config_region_end   = ORIGIN(CONFIG) + LENGTH(CONFIG));  /* 0x08020000 */

ASSERT(ORIGIN(FLASH) + LENGTH(FLASH) <= ORIGIN(CONFIG),
       "app region overlaps the reserved config region")
ASSERT(__config_slot_b_start - __config_slot_a_start == __config_page_size,
       "config slots must be exactly one page apart (different erase units)")
```

**No `ASSERT` uses the modulo operator.** RESEARCH A6 rates `ASSERT` with `%` on a region origin as the syntax most likely to need adjustment on real `arm-none-eabi-ld`, and no ARM toolchain exists in this environment to try it against. The sector-alignment and inside-the-physical-part arithmetic instead lives in `tests/test_py32_flash_map.py` (Task 3), a venue that can actually run it.

**A7 contingency, named but not needed.** RESEARCH A7 flags that two `MEMORY` regions sharing `ORIGIN = 0x08000000` (`BOOTLOADER` and `FLASH`) is untested here; its named fallback is `PROVIDE(__bootloader_region_start = 0x08000000); PROVIDE(__bootloader_region_size = 0);` with the identical honest comment, keeping D-13's seam intact either way. **The region shape was used** (not the fallback) because the local host `ld` probe (below) raised no diagnostic naming a script line. Plan 126-11's gated ARM CI run is the only place this can be authoritatively confirmed; if that run rejects the two-region shape, switch to the named fallback pair without dropping D-13.

**Host `ld` syntax probe -- explicitly non-authoritative.** Run in a scratch directory outside the repository:

```
$ ld -T /workspaces/firestarter/platform/py32f071/linker/PY32F071xB_FLASH.ld -o /dev/null
ld: no input files
$ echo $?
1
```

Interpretation: "no input files" is the expected message for a link with zero input objects and means nothing about the script's correctness -- no diagnostic named a line of the script. This row is **non-authoritative corroboration only** (host `ld` 2.44, wrong target: `arm-none-eabi-ld` is absent). The authoritative proof that this script assembles is Plan 126-11's gated CI run.

**Commit:** `f724613958d7bf2fcc7990e33a7eeec6a447e796` -- `git show --stat HEAD` lists exactly one path: `platform/py32f071/linker/PY32F071xB_FLASH.ld` (50 insertions, 1 deletion). `git merge-base --is-ancestor fd84820e41788eab4da2c7c8d17d6475270980e3 f724613958d7bf2fcc7990e33a7eeec6a447e796` exits **0** -- the ordering holds. `python3 -m pytest tests/ -q` still reported **116 passed** (this task added no test module). `git rev-parse --abbrev-ref HEAD` confirmed `v1.23-py32f071-integration`.

## Task 2 -- `tests/test_flash_geometry_recorded_before_linker.py` (CFG-02's ordering as an exit code)

One module-level helper, `_find_ordering_violations(repo_root, record_path, linker_path)`, returning `(violations, examined_count)`, called by every test in the module (real-repo and both synthetic-repo tests).

**Helper logic:** resolve the record's adding commit (`git log --diff-filter=A --format=%H`, oldest line) -> resolve the linker's tip commit (`git log -1`) -> compute the after-the-record commit set (`git rev-list <add>..HEAD -- <linker>`, an empty set is itself a violation -- the non-vacuity guard) -> for the tip commit and every commit in that set, run `git merge-base --is-ancestor <add> <commit>` and classify its exit code into exactly three buckets (0 = clean, 1 = ordering violation, anything else = tool-error-as-violation, never a pass) -> an examined count of zero is a violation independent of the non-vacuity check.

**Eight functions, all passed:**
```
$ python3 -m pytest tests/test_flash_geometry_recorded_before_linker.py -v
test_the_geometry_record_exists_and_was_added_by_a_commit PASSED
test_the_linker_script_has_a_commit_after_the_geometry_record PASSED
test_the_geometry_record_precedes_every_in_phase_linker_commit PASSED
test_the_linker_script_at_head_actually_carries_the_config_region PASSED
test_the_geometry_record_carries_the_page_and_sector_figures PASSED
test_a_git_tool_error_is_a_violation_not_a_pass PASSED
test_helper_reports_a_violation_on_a_synthetic_repo_with_the_wrong_order PASSED
test_compiler_is_required_not_optional PASSED
8 passed in 0.21s
```

**Observed real-repo values:** adding commit `fd84820e41788eab4da2c7c8d17d6475270980e3`; linker tip commit `f724613958d7bf2fcc7990e33a7eeec6a447e796`; after-the-record commit count **1**; examined count **1**; violations **0**.

**Two synthetic-repository outcomes (the RED demonstration):**
- **Wrong order** (`tmp_path`, `git init`, commit 1 adds a stand-in `linker.ld`, commit 2 adds a stand-in `geometry.md` -- i.e. the linker predates the record): the helper returned a **non-empty violation list**, including an ordering-violation message naming that the record's commit is NOT an ancestor of the linker commit.
- **Correct order** (a second, separate `tmp_path` repo, commit 1 adds `geometry.md`, commit 2 adds `linker.ld` after it): the helper returned **zero violations**, with examined count 1 -- proving the helper discriminates rather than merely complains.
- Neither synthetic repository touched `/workspaces/firestarter`'s real history: the real repo's `git status --porcelain` output was checked for any trace of the synthetic filenames (`geometry.md`, `linker.ld`, `wrong-order`, `correct-order`) and found none.

**Commit:** `cebc0d6d0d334e9ea7f3699f560ace62d1f033a2` -- `git show --stat HEAD` lists exactly one path: `tests/test_flash_geometry_recorded_before_linker.py` (423 insertions). `python3 -m pytest tests/ -q` moved from 116 to **124** (8 new functions). `git rev-parse --abbrev-ref HEAD` confirmed `v1.23-py32f071-integration`.

## Task 3 -- `tests/test_py32_flash_map.py` (CFG-06's map properties as an exit code)

A module-level parser (`_parse_regions` / `_parse_symbols`) extracts `(origin, length)` per `MEMORY` region and resolves each `PROVIDE`d symbol expression (handling `K` suffixes and the `ORIGIN(CONFIG) + 256` form) to an integer. Every property check is a separate `_violations_*` helper taking the parsed structures; the RED test composes them via `_all_violations` -- no parallel second implementation.

**Fourteen functions, all passed**, with the parsed map recorded as integers:

| Region | Origin | Length |
|---|---|---|
| `BOOTLOADER` | `0x08000000` | 0 |
| `FLASH` | `0x08000000` | 122880 (120K) |
| `CONFIG` | `0x0801E000` | 8192 (8K) |
| `RAM` | `0x20000000` | 16384 (16K) |

| Symbol | Resolved value |
|---|---|
| `__config_page_size` | 256 |
| `__config_slot_a_start` | `0x0801E000` |
| `__config_slot_b_start` | `0x0801E100` |
| `__config_region_end` | `0x08020000` |

```
$ python3 -m pytest tests/test_py32_flash_map.py -v
test_config_region_origin_and_length_are_the_recorded_values PASSED
test_config_page_size_symbol_is_the_reference_manual_figure PASSED
test_the_two_slots_are_in_different_page_erase_units PASSED
test_config_region_is_sector_aligned PASSED
test_config_region_lies_inside_the_physical_part PASSED
test_app_region_cannot_reach_the_config_region PASSED
test_all_four_config_symbols_are_provided PASSED
test_bootloader_seam_is_present_and_zero_length PASSED
test_bootloader_seam_carries_its_migration_cost_comment PASSED
test_the_linker_script_cites_the_geometry_record PASSED
test_no_pre_pv32f071_page_or_sector_figure_appears_near_a_config_address PASSED
test_host_contract_asymmetry_is_recorded PASSED
test_helper_reports_violations_on_planted_copies PASSED
test_compiler_is_required_not_optional PASSED
14 passed in 0.05s
```

**Six planted-copy demonstrations** (`test_helper_reports_violations_on_planted_copies`), each a full mutated copy of the real script written into `tmp_path`, each fed to `_all_violations`, each producing a non-empty violation list:

1. `CONFIG` origin moved to `0x0801FE00` (non-sector-aligned) -> sector-alignment violation.
2. `__config_slot_b_start` moved to `ORIGIN(CONFIG) + 512` (two pages apart) -> slot-spacing violation.
3. `BOOTLOADER` given `LENGTH = 8K` (non-zero) -> bootloader-seam violation.
4. `FLASH` left at the physical `LENGTH = 128K` -> app-cannot-reach-config violation (app now overlaps `CONFIG`).
5. The `__config_region_end` `PROVIDE` line deleted entirely -> missing-symbol violation.
6. `__config_page_size` set to `128` (the PY32F030/F003 figure) -> page-size violation.

The real linker script's blob SHA was confirmed **unchanged** before and after this test: `git hash-object platform/py32f071/linker/PY32F071xB_FLASH.ld` = `571a588b0521e9602d98f735e3166a9869dab3aa` both before and after (this is also the file's final committed blob SHA).

**Commit:** `c03a49a49c09d203aef482d5cad2200babd190e7` -- `git show --stat HEAD` lists exactly one path: `tests/test_py32_flash_map.py` (582 insertions). `python3 -m pytest tests/ -q` moved from 124 to **138** (14 new functions). `git rev-parse --abbrev-ref HEAD` confirmed `v1.23-py32f071-integration`.

## Task Commits

1. **Task 1: Reserve Sector 15 in the linker script** -- `f724613` (feat, firmware repo)
2. **Task 2: CFG-02's ordering as an exit code** -- `cebc0d6` (test, firmware repo)
3. **Task 3: CFG-06's map properties as an exit code** -- `c03a49a` (test, firmware repo)

## Files Created/Modified

- `firestarter/platform/py32f071/linker/PY32F071xB_FLASH.ld` -- reserved Sector 15, shrunk FLASH, added D-13 bootloader seam, four PROVIDEd symbols, two ASSERTs. New blob SHA: **`571a588b0521e9602d98f735e3166a9869dab3aa`** (was `b32b5824c8e27492551db5c2b1d413f74f05b6f3`).
- `firestarter/tests/test_flash_geometry_recorded_before_linker.py` -- CFG-02's ordering gate, 8 functions, non-vacuity guard + synthetic-repo RED demonstration.
- `firestarter/tests/test_py32_flash_map.py` -- CFG-06's map gate, 14 functions, six-planted-copy RED demonstration.

## Decisions Made

- D-18's whole-Sector-15 reservation was implemented exactly as recorded in `CONFIG-STORAGE.md` (the operator's confirmed choice), not the minimal 512 B two-erase-unit reading.
- No linker `ASSERT` uses the modulo operator (RESEARCH A6); the sector-alignment and physical-bounds arithmetic lives entirely in `tests/test_py32_flash_map.py`.
- The `BOOTLOADER` region shape was used rather than the A7 fallback `PROVIDE` pair, since the host `ld` probe raised no syntax diagnostic. This is recorded as a **named contingency, not yet authoritatively confirmed** -- if Plan 126-11's ARM CI run rejects two `MEMORY` regions sharing `ORIGIN = 0x08000000`, switch to the fallback pair (`__bootloader_region_start` / `__bootloader_region_size`) with the identical comment, never dropping D-13.

## Deviations from Plan

None -- plan executed exactly as written. Both blob-hash pre-checks (`include/rurp_shield.h` = `602fe6f326a042ab71efd111e4dfcf3a6e41dd46`, `include/rurp_types.h` = `d3fe5203a91527bdb7b20a33843c81065e21c613`, `include/rurp_config_storage.h` = `1d74d0ede91853c2ce2bcc0bda1eb8fe8a07e5b2`) all matched their pinned values, unchanged throughout. `ls scripts/check_*.py | wc -l` stayed **5** across all three tasks. No requirement checkbox in `.planning/REQUIREMENTS.md` was touched (`git diff --stat -- .planning/REQUIREMENTS.md` is empty). Both gitignored py32 worktrees (`firestarter_py32_ci`, `firestarter_app_py32`) showed no porcelain changes.

## Non-claims (explicit)

- **This plan does not prove the linker script assembles.** `arm-none-eabi-gcc`, `cmake` and `ninja` are absent from this environment. The host `ld` probe above is recorded as non-authoritative corroboration only; the authoritative proof is Plan 126-11's gated ARM CI run, cited by run URL plus head SHA when it executes.
- **No claim is made that the reserved region is preserved across a real DFU install.** That is the *intended* behaviour per `CONFIG-STORAGE.md`'s Host contract section, and remains an explicit non-claim until a PY32F071 PCB exists.

## Verification

- `python3 -m pytest tests/ -q` -> **138 passed** (was 116 before this plan; +8 ordering-gate functions, +14 flash-map-gate functions).
- Both pinned native envs re-run and confirmed: `pio test -e native` -> **141 test cases: 141 succeeded** (17 suites); `pio test -e native_nodevtools` -> **141 test cases: 141 succeeded** (17 suites). Neither moved.
- `ls scripts/check_*.py | wc -l` -> **5**, unchanged.
- `git rev-parse --abbrev-ref HEAD` in the firmware repo -> `v1.23-py32f071-integration` after every commit.
- Meta repo (`/workspaces`) remains on `gsd/v1.23-py32f071-integration`; this plan makes no code commit there, only the SUMMARY/state commit that follows.

## Issues Encountered

None.

## Next Phase Readiness

`__config_slot_a_start`, `__config_slot_b_start` and `__config_page_size` are now real, gated linker symbols that Plan 126-08's `config_storage_flash.cpp` (HAL glue) can extern-reference by exact name. Plan 126-11's gated ARM CI run is the first point this branch's actual `arm-none-eabi-ld` behavior against this script -- in particular the A7 contingency (whether `BOOTLOADER` and `FLASH` may legally share `ORIGIN = 0x08000000`) is untested until then; if it fails, the named fallback recorded above is the prescribed fix, and it must not drop D-13's seam. Phase 129's PCB-03 will cite every address this plan wrote as an actual reservation, not a proposal -- changing any of them after that point is a flash-map migration, per the plan's own success criteria.

## Self-Check: PASSED

- FOUND: `firestarter/platform/py32f071/linker/PY32F071xB_FLASH.ld` (blob `571a588b0521e9602d98f735e3166a9869dab3aa`)
- FOUND: `firestarter/tests/test_flash_geometry_recorded_before_linker.py`
- FOUND: `firestarter/tests/test_py32_flash_map.py`
- FOUND (firmware repo): commit `f724613` (linker edit)
- FOUND (firmware repo): commit `cebc0d6` (ordering gate)
- FOUND (firmware repo): commit `c03a49a` (flash-map gate)

No missing items.

## Self-Check: PASSED (re-verified post-write)

All three firmware-repo file paths and all three commit hashes re-confirmed present via `[ -f ... ]` and `git log --oneline --all | grep`; SUMMARY.md confirmed present at its meta path. No missing items.

---
*Phase: 126-flash-persistent-config-via-a-storage-backend-seam-highest-r*
*Completed: 2026-07-31*
