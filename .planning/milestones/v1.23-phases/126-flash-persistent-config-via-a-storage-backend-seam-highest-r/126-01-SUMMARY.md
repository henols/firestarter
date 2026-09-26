---
phase: 126-flash-persistent-config-via-a-storage-backend-seam-highest-r
plan: 01
subsystem: firmware/py32f071 config-storage design + gate
tags: [flash-config, py32f071, design-doc, cfg-01, cfg-02, pytest-gate]
provides:
  - "platform/py32f071/CONFIG-STORAGE.md: the vendored in-scope flash-config design (CFG-01) + the CFG-02 flash-geometry record, landed as its own commit (the CFG-02 ordering anchor)"
  - "tests/test_config_storage_design_vendored.py: a 9-function pytest gate enforcing CONFIG-STORAGE.md's required content mechanically, with a planted-violation RED demonstration"
  - "the pre-phase pin: eleven blob SHAs, gate counts, native counts, AVR figures, all recorded before any file moved"
affects: [126-02, 126-03, 126-06, 126-12]
tech-stack:
  added: []
  patterns:
    - "section-scoped content gating (SUPERSEDED span, not file-wide substring)"
    - "shared module-level violation helper exercised by both positive tests and a planted-violation RED test"
key-files:
  created:
    - firestarter/platform/py32f071/CONFIG-STORAGE.md
    - firestarter/tests/test_config_storage_design_vendored.py
  modified: []
key-decisions:
  - "CONFIG-STORAGE.md landed alone, in its own commit (fd84820), preceding any commit this phase makes to the linker script -- the CFG-02 ordering anchor Plan 126-06 will wrap git rev-list --is-ancestor around"
  - "D-16's literal 'program the header/CRC word LAST' recorded as an explicit amendment, not silently reinterpreted: the completion of one 256-byte page program IS the commit"
  - "D-18's shrink-quantum amendment (one whole 8 KiB sector, not two 256 B pages) recorded with D-10's untouched elements named"
  - "CONFIG_MAGIC 0x52555250 recorded as a this-milestone choice, explicitly NOT vendored (guards against the Phase-122 C-5 overclaim shape)"
duration: 7min
completed: 2026-07-31
status: complete
---

# Phase 126 Plan 01: Pre-Phase Pin + Vendored Flash-Config Design (CFG-01) + Flash Geometry (CFG-02) Summary

**Recorded the pre-phase pin (eleven blob SHAs, gate/suite/native counts, AVR figures), then landed `platform/py32f071/CONFIG-STORAGE.md` — the vendored in-scope flash-config design plus the CFG-02 flash-geometry record — as its own commit, gated by nine mechanical pytest checks including a planted-violation RED demonstration.**

## Performance
- **Duration:** ~7 min
- **Tasks:** 3/3 completed
- **Files modified:** 2 created, 0 modified

## Task 1 — Pre-Phase Pin (read-only, no commit)

All values recorded from the live tree before any file moved.

**Repo identity:** firmware repo `/workspaces/firestarter` — branch `v1.23-py32f071-integration`, `HEAD = 2b5e8c875bb04d728b5e08d16cc2d29e0d43c1d7`, `git status --porcelain` = **0 lines**. Meta repo branch: `gsd/v1.23-py32f071-integration`. The host repo (`/workspaces/firestarter_app`) has its own five known pre-existing porcelain lines (` M .gitignore`, plus untracked `.coverage`, `.planning/config.json`, `SECURITY.md`, `write_test_port.sh`) — recorded as pre-existing, not a finding; not touched by this plan.

**Eleven blob SHAs — all eleven MATCH their expected values (no mismatch, no STOP finding):**

| Path | Expected | Observed | Verdict |
|---|---|---|---|
| `include/rurp_types.h` | `d3fe5203a91527bdb7b20a33843c81065e21c613` | same | MATCH |
| `include/rurp_shield.h` | `602fe6f326a042ab71efd111e4dfcf3a6e41dd46` | same | MATCH |
| `platformio.ini` | `f4e720ba75a8c618cc23bac045ab65084d41a0a4` | same | MATCH |
| `include/messages.h` | `dc7dbfc6b7ad3d767f7dad1ecbe13a53ca1eb346` | same | MATCH |
| `scripts/baseline/size_baseline_base01.json` | `b940c91655600a57ad7ef67cba723943af929daf` | same | MATCH |
| `src/rurp_config_utils.cpp` (D-04 anchor) | `6705fd46e07a2d359d161dc2e7728cb4e45f89c7` | same | MATCH |
| `platform/py32f071/CMakeLists.txt` | `4ba33365050fa73faeceb9ebcd61578dede04b83` | same | MATCH |
| `platform/py32f071/linker/PY32F071xB_FLASH.ld` | `b32b5824c8e27492551db5c2b1d413f74f05b6f3` | same | MATCH |
| `platform/py32f071/src/config.cpp` | `78ebf0eabcba5adca40f517e05606cd941902801` | same | MATCH |
| `scripts/baseline/size_baseline.json` | `9cc5204bb437735d77523e62512c1d2cadfc668f` | same | MATCH |
| `scripts/check_cmake_manifest.py` | `ec56b5e163950a9e7a3c1fb43df89d574647c215` | same | MATCH |

**`CONFIG_VERSION` line, verbatim, `include/rurp_shield.h:46`:**
```
#define CONFIG_VERSION "VER06"
```

**`sizeof(rurp_configuration_t)` measured on this host** (throwaway TU, `g++` outside the repo): **`sizeof(long) = 8`**, **`sizeof(rurp_configuration_t) = 32`** — matches the expected host figure. AVR measures **15**; ARM is **computed** at **20** (RESEARCH C-6 table; ARM cannot be measured locally, `g++ -m32` fails here with no multilib). **No test in this phase may assert a literal size or offset** — the only permitted assertion is the relational one, `sizeof(StoredConfiguration) <= 256`.

**Gate/suite counts, all as expected:**
- `python3 scripts/check_cmake_manifest.py` → exit **0**, **24 enforced sources**, **14** `PY32_SDK_SOURCES` exempt, 5 allow-listed omissions (`src/boards/leonardo_rurp_shield.cpp`, `src/boards/rurp_common.cpp`, `src/boards/uno_rurp_shield.cpp`, `src/dev_tools.cpp`, `src/rurp_config_utils.cpp`).
- `python3 -m pytest tests/ -q` → **86 passed** (before this plan's new test file).
- `ls scripts/check_*.py | wc -l` → **5**.
- Native envs (recorded baseline values, not measured here): `native` and `native_nodevtools` at **141 cases / 17 suites**; `native_pinmap_provisional` at **10 cases / 1 suite**.
- AVR flash/RAM (recorded baseline values): uno 23954/32256 flash, 1573/2048 RAM; uno328pb 24004/32384, 1579/2048; leonardo 26016/28672, 2014/2560 — **leonardo's free flash is 2656 B**, not the 2600 B `126-CONTEXT.md` states (CONTEXT is stale here; RESEARCH is right).
- **Two distinct size comparators, named for later plans:** `compare_avr` (strict equality) reads the **live** `scripts/baseline/size_baseline.json`; `compare_avr_policy_merge05` (the A-5 band) reads the **frozen** `scripts/baseline/size_baseline_base01.json`. Different gates, different pass sets, different files.

No file was modified in Task 1; `git status --porcelain` was still 0 lines in `/workspaces/firestarter` at the end of the task.

## Task 2 — `platform/py32f071/CONFIG-STORAGE.md` (its own commit)

Created `firestarter/platform/py32f071/CONFIG-STORAGE.md` and committed it alone.

**Commit:** `fd84820e41788eab4da2c7c8d17d6475270980e3` — `git show --stat HEAD` lists exactly one path: `platform/py32f071/CONFIG-STORAGE.md` (284 insertions, 0 other files). This is the **CFG-02 ordering anchor**: Plan 126-06 will wrap `git rev-list --is-ancestor` around this commit against every later commit touching `platform/py32f071/linker/PY32F071xB_FLASH.ld`.

Content landed, section by section, per the plan's required order: opening statement (cites blob `4b1a441`, names `feature/py32f071-toolchain`/PR #46 and `feature/py32f071-full-support`/PR #47 as closed, states `platform/py32f071/PORTING.md` does not exist on any live branch); `## Configuration storage (vendored, in scope)` (the `StoredConfiguration` six fields verbatim, D-17's version-vs-CONFIG_VERSION warning); `## SUPERSEDED by PR #48's actual module layout` (all seven module names — `storage.cpp`, `gpio.cpp`, `board.cpp`, `adc.cpp`, `dac.cpp`, `py32f071_board.h`, `py32f071_pins.h` — plus `usb.cpp`, each mapped to PR #48's real files, `config.cpp` marked deleted-by-this-phase); `## Out of scope` (DAC-VPP + calibration routed to FUT-VPP/FUT-CAL); `## Flash geometry` (256 B page / 8192 B sector, RM V0.2 §4.1/§4.2.1/Table 4-1, pinned SDK commit `0ed2f4b4d3391eccfd4491006a30295fd78e32c2` corroboration, both do-not-use traps named); `## Reserved flash map` (D-18 amendment, D-13's migration cost); `## Amendment to D-16` (RM §4.2.3.2, `IS_FLASH_TYPEPROGRAM`, corrected commit shape); `## CONFIG_MAGIC` (`0x52555250`, explicitly not-vendored per D-19); `## Validation order for a record read from flash` (V5); `## CRC32 is not a security primitive` (V6); `## Erase before program is mandatory` (C-8); `## Write protection` (V4); `## Reset and interrupt behaviour` (C-7, D-14's cost as not-measured); `## Host contract` (D-12, C-9, C-10); `## Claim ceiling` (by reference, with the literal caveat phrase the milestone's claim gate requires).

**Claim gate, verbatim invocation and result:**
```
$ cd /workspaces/firestarter && python3 /workspaces/.planning/phases/123-non-regression-baselines-gate-hardening/check_permitted_claims.py platform/py32f071/CONFIG-STORAGE.md
PASS: scanned ../../../firestarter/platform/py32f071/CONFIG-STORAGE.md; 1 file(s) carry the required silicon caveat (this PASS is the mechanizable half of the honesty criterion only -- see the module docstring's explicit non-claim)
```
Exit code 0.

**Prohibited-file re-check, after the commit:** `git hash-object platform/py32f071/linker/PY32F071xB_FLASH.ld` → `b32b5824c8e27492551db5c2b1d413f74f05b6f3` (unchanged). `git hash-object include/rurp_shield.h` → `602fe6f326a042ab71efd111e4dfcf3a6e41dd46` (unchanged). `git rev-parse --abbrev-ref HEAD` → `v1.23-py32f071-integration` (unchanged). `python3 -m pytest tests/ -q` → still `86 passed` (this task added no test module).

## Task 3 — `tests/test_config_storage_design_vendored.py` (its own commit)

Created `firestarter/tests/test_config_storage_design_vendored.py`: one module-level helper, `_find_design_doc_violations(text)`, exercised by all nine test functions (the positive tests via a filtered view of its result, the RED demonstration via a mutated tmp_path copy).

**Nine gate functions, all passed:**
```
$ python3 -m pytest tests/test_config_storage_design_vendored.py -v
tests/test_config_storage_design_vendored.py::test_design_doc_cites_the_vendored_blob_by_sha PASSED
tests/test_config_storage_design_vendored.py::test_design_doc_marks_every_superseded_module PASSED
tests/test_config_storage_design_vendored.py::test_design_doc_records_the_flash_geometry_with_its_citation PASSED
tests/test_config_storage_design_vendored.py::test_design_doc_records_config_magic_as_not_vendored PASSED
tests/test_config_storage_design_vendored.py::test_design_doc_records_the_d16_amendment PASSED
tests/test_config_storage_design_vendored.py::test_design_doc_refuses_to_call_crc32_a_security_primitive PASSED
tests/test_config_storage_design_vendored.py::test_design_doc_records_the_reserved_map_addresses PASSED
tests/test_config_storage_design_vendored.py::test_helper_reports_a_violation_on_a_planted_copy PASSED
tests/test_config_storage_design_vendored.py::test_compiler_is_required_not_optional PASSED
9 passed in 0.03s
```

**Planted-violation RED demonstration (`test_helper_reports_a_violation_on_a_planted_copy`):** a copy of `CONFIG-STORAGE.md` was written into `tmp_path` with every occurrence of `4b1a441` replaced by `REDACTED`, then fed to the same `_find_design_doc_violations` helper the positive tests use. The helper returned a non-empty violation list containing `"missing blob SHA citation '4b1a441'"`, proving the gate can actually fail on bad input. The committed document was confirmed unmutated (`4b1a441` still present) both before and after the test.

**Suite totals:** `python3 -m pytest tests/ -q` moved from **86 to 95** (9 new functions). `ls scripts/check_*.py | wc -l` still **5** — this is a `tests/test_*.py` module, not a new checker, so `tests/test_checker_convention.py`'s `FLOOR`/`FIXTURE_FLOOR` needed no bump (unmodified).

**Commit:** `be503cba599995ee530d4787b03a3a1f196c9138` — `git show --stat HEAD` lists exactly one path: `tests/test_config_storage_design_vendored.py` (357 insertions). `git rev-parse --abbrev-ref HEAD` confirmed `v1.23-py32f071-integration` after the commit.

## Task Commits
1. **Task 1: Record the pre-phase pin** — no commit (read-only evidence capture)
2. **Task 2: Author `platform/py32f071/CONFIG-STORAGE.md`** — `fd84820` (firmware repo)
3. **Task 3: Gate the vendored design** — `be503cb` (firmware repo)

## Files Created/Modified
- `firestarter/platform/py32f071/CONFIG-STORAGE.md` — the vendored flash-config design + CFG-02 geometry record, the CFG-02 ordering anchor for the phase
- `firestarter/tests/test_config_storage_design_vendored.py` — the CFG-01 gate, 9 pytest functions, section-scoped SUPERSEDED check + planted-violation RED demonstration

## Deviations from Plan

None — plan executed exactly as written. All eleven pre-phase blob SHAs matched their expected values (no STOP finding required). Both prohibited-file checks (`include/rurp_shield.h`, `platform/py32f071/linker/PY32F071xB_FLASH.ld`) remained unchanged throughout. No requirement checkbox in `.planning/REQUIREMENTS.md` was touched (`git diff --stat -- .planning/REQUIREMENTS.md` is empty). Both gitignored py32 worktrees (`firestarter_py32_ci`, `firestarter_app_py32`) show no porcelain changes.

## Known Stubs

None. Both new files are fully wired: `CONFIG-STORAGE.md` is a complete, self-contained design record (no placeholder sections), and `test_config_storage_design_vendored.py`'s nine functions all execute real assertions against real content — none is a stub or a TODO.

## Threat Flags

None. This plan adds no new network endpoint, auth path, file-access pattern, or schema change at a trust boundary — it is documentation plus a read-only pytest gate. The threat register rows in the plan's own `<threat_model>` (T-126-01-01 through T-126-01-08) are all addressed by content already recorded in `CONFIG-STORAGE.md` and enforced by the new test module; no additional surface was introduced beyond what the plan's threat model already named.

## Next Phase Readiness

The CFG-02 ordering anchor (`fd84820`) exists and precedes every later commit in this phase — Plan 126-06 can safely wrap `git rev-list --is-ancestor` around it once it lands the linker edit. Plan 126-02 (parallel, same wave) can proceed independently — it authors `tests/test_config_storage_eeprom_regression.py` against the pre-refactor `src/rurp_config_utils.cpp` blob recorded here (`6705fd46e07a2d359d161dc2e7728cb4e45f89c7`). Plan 126-03's D-08 manifest edits and Plan 126-07's HAL-free core (`CONFIG_MAGIC`, `StoredConfiguration`, the D-16-corrected commit shape) now have a committed design record to build against rather than only the closed-PR blob and CONTEXT/RESEARCH prose.

## Self-Check: PASSED

- FOUND: `firestarter/platform/py32f071/CONFIG-STORAGE.md`
- FOUND: `firestarter/tests/test_config_storage_design_vendored.py`
- FOUND: `.planning/phases/126-flash-persistent-config-via-a-storage-backend-seam-highest-r/126-01-SUMMARY.md`
- FOUND (firmware repo): commit `fd84820` (CONFIG-STORAGE.md)
- FOUND (firmware repo): commit `be503cb` (test module)
- FOUND (meta repo): commit `f5515c8` (this SUMMARY)

No missing items.
