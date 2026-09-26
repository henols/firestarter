---
phase: 126
slug: flash-persistent-config-via-a-storage-backend-seam-highest-r
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-31
---

# Phase 126 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `126-RESEARCH.md` § Validation Architecture. Task IDs are bound at plan time.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** (new tests) | `pytest` 9.1.1 driving host `g++` 14.2.0 by subprocess |
| **Framework** (existing native) | PlatformIO + Unity — **pinned at 141 cases / 17 suites, must not move** (RESEARCH C-13) |
| **Config file** | none — `firestarter/tests/` has no `conftest.py` / `pytest.ini` / `pyproject.toml`. Self-contained per-file path resolution is the house pattern (Phase 125) |
| **Quick run command** | `cd /workspaces/firestarter && python3 -m pytest tests/ -q` |
| **Full suite command** | `python3 -m pytest tests/ -v` + `pio test -e native` + `pio test -e native_nodevtools` + `pio run -e uno` / `-e uno328pb` / `-e leonardo` + `python3 scripts/check_size_baseline.py` + `python3 scripts/check_cmake_manifest.py` + `python3 scripts/check_build_warnings.py` |
| **Estimated runtime** | ~10 s quick (compile-and-run pytest) / ~5–8 min full (cold AVR builds dominate) |
| **CI coverage of new tests** | **ZERO legs on this branch.** `pytest tests/` runs only in `build.yml` (main) and `beta-build.yml` (beta); `py32f071.yml` has no pytest step. Discharged by an in-phase **local** run whose verbatim output lands in `126-NONREGRESSION.md` (D-01). Do not claim CI coverage this branch lacks. |

---

## Sampling Rate

- **After every task commit:** `python3 -m pytest tests/ -q`
- **After every plan wave:** full `pytest tests/ -v` + both pinned `pio test` envs **with counts asserted** (141 cases / 17 suites) + the nine-row cross-repo gate sweep (A-7 discipline: assert gates RAN, not SKIPped) + `check_cmake_manifest.py`
- **After the AVR move specifically, before any ARM work:** three cold AVR builds (`pio run -t clean -e <env> && pio run -e <env>` for uno, uno328pb, leonardo) + `check_size_baseline.py` — the only point at which a flash delta is attributable to the move
- **Before `/gsd-verify-work`:** full suite green, all counts asserted, `126-NONREGRESSION.md` re-executed in the closing plan
- **Max feedback latency:** ~10 s per task; ~8 min per wave

---

## Per-Task Verification Map

Rows are requirement-scoped; the `Task ID` column is bound when plans land.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | TBD | TBD | CFG-01 | — | N/A | unit (text) | `pytest tests/test_config_storage_design_vendored.py -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | CFG-02 | — | N/A | unit + git | `pytest tests/test_flash_geometry_recorded_before_linker.py -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | CFG-03 | — | Seam header declares exactly 2 fns, included by exactly 3 TUs, `rurp_shield.h` untouched (D-09) | unit (source scan) | `pytest tests/test_config_storage_seam_shape.py -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | CFG-04 | — | `EEPROM.get`/`put` at offset 48 with `sizeof(rurp_configuration_t)`, byte-identical pre/post | integration (g++) | `pytest tests/test_config_storage_eeprom_regression.py -v` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | CFG-04 | — | AVR flash/RAM delta inside the A-5 band on all three targets | integration (build) | 3× cold `pio run` then `python3 scripts/check_size_baseline.py` | ✅ armed | ⬜ pending |
| TBD | TBD | TBD | CFG-05 | V5 | blank slots ⇒ no valid record; `magic` must not be `0xFFFFFFFF`/`0x00000000` | integration (g++) | `pytest tests/test_config_storage_dualslot.py::test_blank_slots_report_no_valid_record -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | CFG-05 | V5 | newest sequence wins when both slots valid | integration (g++) | `…::test_newest_sequence_wins_when_both_slots_valid -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | CFG-05 | V5 / T-`length` | bad-CRC slot rejected; **and** `rec.length > len` rejected *before* any copy | integration (g++) | `…::test_slot_with_bad_crc_is_rejected_in_favour_of_the_other -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | CFG-05 | V5 | both slots corrupt ⇒ no valid record (D-15: same outcome as blank, different input) | integration (g++) | `…::test_both_slots_corrupt_reports_no_valid_record -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | CFG-05 | DoS (torn write) | interrupted write leaves previous record loadable — abort after N ∈ {0,1,32,63,64} words (C-2) | integration (g++) | `…::test_interrupted_write_leaves_the_previous_record_loadable -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | CFG-05 | — | successive saves alternate slots | integration (g++) | `…::test_successive_saves_alternate_slots -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | CFG-05 | — | CRC32 known-answer anchor `CRC32("123456789") == 0xCBF43926` (D-05) — 7th fn, non-vacuity proof for the six | integration (g++) | `…::test_crc32_matches_the_independent_known_answer_vector -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | CFG-06 | V4 (WRP) | `.ld` reserves 2 pages in **different erase units**, page size 256, region inside `0x08000000 + 128 KiB`, sector-aligned, symbols `PROVIDE`d | unit (parse) | `pytest tests/test_py32_flash_map.py -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | CFG-06 | — | `CMakeLists.txt` names `py32f071_hal_flash.c` whenever a TU calls `HAL_FLASH_` (C-3 — turns a CI-only link failure into a local one) | unit (source scan) | `pytest tests/test_py32_flash_map.py::test_manifest_names_the_flash_driver -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | CFG-07 | — | `rurp_configuration_t` + `CONFIG_VERSION "VER06"` unchanged; `platform/py32f071/src/config.cpp` **absent from the tree** | unit | `pytest tests/test_config_schema_pinned.py -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | all | — | Native counts unmoved: **141 cases / 17 suites** on both pinned envs (assert the counts, never "tests pass") | integration | `pio test -e native` ; `pio test -e native_nodevtools` | ✅ exists | ⬜ pending |
| TBD | TBD | TBD | all | — | Golden register traces byte-identical, **per-array** for `_shared/sdp_expected.h` | integration | via `pio test -e native` | ✅ exists | ⬜ pending |
| TBD | TBD | TBD | all | — | The nine cross-repo gates **RAN**, not SKIPped (A-7) | integration | host-suite sweep in the sibling layout, re-run **every wave** | ✅ exists | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_config_storage_eeprom_regression.py` — CFG-04. **Must be authored against the pre-refactor file and its blob SHA recorded** (D-04). Needs a hand-written fake `EEPROM.h` (C-12), not `.pio/libdeps`
- [ ] `tests/test_config_storage_dualslot.py` — CFG-05. Six named functions + the CRC KAT; needs the RAM fake with an abort-after-N-words hook (C-2) and a "program on a non-erased page is a test failure" assertion (C-8)
- [ ] `tests/test_py32_flash_map.py` — CFG-06 + D-12(b). Parses the `.ld`, asserts the erase-unit property against the CFG-02 figure, asserts the manifest names the flash driver (C-3)
- [ ] `tests/test_config_storage_seam_shape.py` — CFG-03. Two declarations, three including TUs, `rurp_shield.h` unchanged (D-09)
- [ ] `tests/test_config_schema_pinned.py` — CFG-07. Schema + `CONFIG_VERSION` + `config.cpp` absence
- [ ] `tests/test_config_storage_design_vendored.py` + `tests/test_flash_geometry_recorded_before_linker.py` — CFG-01 / CFG-02
- [ ] Framework install: **none needed** — `pytest 9.1.1` and `g++ 14.2.0` are present
- [ ] **No new `scripts/check_*.py`.** Phase 125's C-11 measured the cost: a new checker costs four artifacts plus bumps to `test_checker_convention.py`'s `FLOOR = 5` **and** `FIXTURE_FLOOR = 10`. Those floors are scoped to `scripts/check_*.py`, so `tests/test_*.py` files cost **zero** bumps

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Config survives a real DFU install on silicon | CFG-06 | No py32 PCB exists; MERGE-04 refuses every PROM-energising operation on py32 | Deferred — carried as an explicit non-claim, not scheduled work |
| First-boot write-back cost on a Cortex-M0+ (D-14) | CFG-05 | Unmeasurable without hardware | Recorded as *not measured*, never as *acceptable* |
| Config write during a PROM programming pulse (C-7) | — | Not exercisable today (MERGE-04) | Explicit non-claim; do not schedule work against it |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all ❌ MISSING references above
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s per task
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
