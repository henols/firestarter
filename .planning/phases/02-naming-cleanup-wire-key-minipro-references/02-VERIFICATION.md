---
phase: 02-naming-cleanup-wire-key-minipro-references
verified: 2026-05-12T09:30:00Z
status: passed
score: 14/14 must-haves verified
overrides_applied: 0
re_verification:
  previous_status: none
  previous_score: n/a
  gaps_closed: []
  gaps_remaining: []
  regressions: []
---

# Phase 2: Naming Cleanup (Wire Key + Minipro References) Verification Report

**Phase Goal:** The host-side codebase has clean naming — the wire JSON VPP key is unambiguously `"vpp_mv"`, the chip-database file no longer carries the upstream toolchain name, and "minipro" appears in the app only where it's load-bearing (the `MINIPRO_XML_URL` constant and one attribution line). No dispatch regression on any of the 743 chips.
**Verified:** 2026-05-12T09:30:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (Roadmap Success Criteria + Plan must_haves)

| #   | Truth                                                                                                                              | Status     | Evidence                                                                                                                                                          |
| --- | ---------------------------------------------------------------------------------------------------------------------------------- | ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SC1 | Python emitter writes `"vpp_mv"`; firmware parses `"vpp_mv"` into `handle->vpp_mv`; app CLAUDE.md example shows only `"vpp_mv"`     | ✓ VERIFIED | `database.py:518` reads `"vpp_mv": vpp_mv,`; `json_parser.c:62/74/309` triple-flip; `firestarter_app/CLAUDE.md:54` shows `"vpp_mv": 12000,` only, no `"vpp"` line |
| SC2 | Chip-database file renamed to `chip_database.json`; all readers/writer/docs point at new name                                       | ✓ VERIFIED | `chip_database.json` exists; old file absent; 7 callsites flipped; meta + sub-repo CLAUDE.md all reference `chip_database.json`                                  |
| SC3 | "minipro" reduced to single load-bearing site (`MINIPRO_XML_URL` + 1 CLAUDE.md attribution)                                         | ✓ VERIFIED | `database.py`=0, `check_dispatch.py`=0, `firestarter/CLAUDE.md`=0, meta `CLAUDE.md`=0, `firestarter_app/CLAUDE.md`=1 (at :68 next to `infoic.xml`); `MINIPRO_XML_URL` preserved at `build_db.py:10` |
| SC4 | `check_dispatch.py` confirms all 743 chips parse end-to-end on Uno + Leonardo simulator buffer paths with no wire regression       | ✓ VERIFIED | `python tools/check_dispatch.py` exit 0; output: `PASS: all 743 chips have a valid dispatch path; ... 0 wire-key regressions`                                    |
| SC5 | `firestarter --help` + `firestarter info W27C512` (and `--adapter` smoke) succeed against the renamed DB                            | ✓ VERIFIED | All three commands exit 0; `info W27C512` returns 10-line metadata; `info --adapter W27C512` returns 63 lines including adapter pinout table                     |
| T1  | (Plan 01) Firmware atomic three-site flip lands in single commit; legacy `key_vpp` identifier and `"vpp"` literal gone              | ✓ VERIFIED | `json_parser.c`: `key_vpp_mv` decl at :62, dispatch row at :74, `extract_int("vpp_mv", ...)` at :309; commit `firestarter@39b29a9` is single atomic commit       |
| T2  | (Plan 01) `firestarter/CLAUDE.md` documents only `vpp_mv` field (no `vpp / vpp_mv` legacy form)                                     | ✓ VERIFIED | `firestarter/CLAUDE.md:74` shows `- vpp_mv — VPP voltage in millivolts (used by SAF-04 ADC validation)`                                                           |
| T3  | (Plan 02) `git mv` preserved blame chain across rename                                                                              | ✓ VERIFIED | `git log --follow --format='%H' -- firestarter/data/chip_database.json` returns 4 commits (rename + 3 prior under old filename)                                  |
| T4  | (Plan 02) Internal `_map_data()` writes `"vpp_volts"`; both consumers + emitter fallback read `"vpp_volts"`                         | ✓ VERIFIED | `database.py:417` `"vpp_volts": vpp,`; `:510` `get("vpp_volts", 0) * 1000`; `eprom_info.py:271` `ic.get('vpp_volts', '-')`; `ic_layout.py:513` `eprom_data.get('vpp_volts', 'N/A')` |
| T5  | (Plan 02) Upstream-schema READ at `database.py:375` PRESERVED (D-08-compat — reads on-disk DB string `"12V"`)                       | ✓ VERIFIED | `grep -n 'electrical\.get("vpp", "0")' database.py` returns `:375`                                                                                                |
| T6  | (Plan 02) `pyproject.toml [tool.setuptools.package-data]` and `MANIFEST.in` declare the actual shipping data files                  | ✓ VERIFIED | `pyproject.toml` lists `data/chip_database.json`, `data/database_overrides.json`, `data/pinouts.json`; `MANIFEST.in` includes the same plus `avrdude.conf`       |
| T7  | (Plan 03) `check_dispatch.py` augmented: package-import `EpromDatabase`, `db = EpromDatabase()`, `wire_regressions = []`, round-trip block | ✓ VERIFIED | All five grep gates pass (`from firestarter.database import EpromDatabase`, `db = EpromDatabase()`, `wire_regressions = []`, `"vpp_mv" not in wire`, `"vpp" in wire`) |
| T8  | (Plan 03) Surviving minipro attribution at `firestarter_app/CLAUDE.md` is co-located with `infoic.xml` + `chip_database.json`        | ✓ VERIFIED | `grep -nF minipro firestarter_app/CLAUDE.md` returns `:68: ... parses tools/infoic.xml (minipro chip database XML) and outputs firestarter/data/chip_database.json.` |
| T9  | (Plan 03) `MINIPRO_XML_URL` constant at `build_db.py:10` retained verbatim per D-09                                                  | ✓ VERIFIED | `sed -n '10p' build_db.py` shows `MINIPRO_XML_URL = "https://gitlab.com/DavidGriffith/minipro/-/raw/master/infoic.xml"`                                          |

**Score:** 14/14 truths verified

### Required Artifacts

| Artifact                                                  | Expected                                                       | Status     | Details                                                                                          |
| --------------------------------------------------------- | -------------------------------------------------------------- | ---------- | ------------------------------------------------------------------------------------------------ |
| `firestarter_app/firestarter/database.py`                 | `:518` wire-key flip + `:417`/`:510` internal rename + comment scrubs at `:45`/`:389` | ✓ VERIFIED | All four edits in place; line `:375` upstream-schema read preserved                              |
| `firestarter/src/json_parser.c`                           | `key_vpp_mv` PROGMEM literal at `:62`, dispatch row at `:74`, `extract_int("vpp_mv", ...)` at `:309` | ✓ VERIFIED | All three sites flipped; legacy `key_vpp` + `"vpp"` literal both removed                         |
| `firestarter_app/firestarter/data/chip_database.json`     | Renamed from `minipro_complete_db.json` via `git mv`            | ✓ VERIFIED | File exists; old name absent; `git log --follow` returns 4 commits (blame preserved)             |
| `firestarter_app/tools/build_db.py`                       | `OUTPUT_FILE` at `:12` references `chip_database.json`; `MINIPRO_XML_URL` at `:10` preserved; `:23` comment softened | ✓ VERIFIED | All three confirmed via inline read                                                              |
| `firestarter_app/tools/check_dispatch.py`                 | Docstring + `_DATA_DIR` flipped; D-15 Shape A augmentation present; 0 minipro mentions | ✓ VERIFIED | All five augmentation grep gates pass; `grep -cF minipro` = 0                                    |
| `firestarter_app/firestarter/eprom_info.py`               | `:271` consumer reads `'vpp_volts'`                              | ✓ VERIFIED | Line `:271` reads `ic.get('vpp_volts', '-')`                                                     |
| `firestarter_app/firestarter/ic_layout.py`                | `:516` consumer reads `'vpp_volts'`                              | ✓ VERIFIED | Line `:516` reads `eprom_data.get('vpp_volts', 'N/A')`                                           |
| `firestarter_app/pyproject.toml`                          | `package-data` lists real shipping files                          | ✓ VERIFIED | `chip_database.json`, `database_overrides.json`, `pinouts.json`                                  |
| `firestarter_app/MANIFEST.in`                             | sdist file list aligned to real shipping files                    | ✓ VERIFIED | 11 include lines, all reference real files (see WR-01 below — `avrdude.conf` line has known drift) |
| `firestarter_app/CLAUDE.md`                               | Wire example shows `"vpp_mv": 12000,` only; exactly 1 minipro line (at `:68`); filename references updated | ✓ VERIFIED | Wire example verified at `:54`; minipro count = 1 at `:68`; data-flow + Key Files + Pipeline filename touches confirmed |
| `firestarter/CLAUDE.md`                                   | Field-list collapsed to `vpp_mv` only; filename `:30` flipped; `:69` minipro removed (count = 0) | ✓ VERIFIED | All three confirmed                                                                              |
| `CLAUDE.md` (meta)                                        | `:44` filename flipped; 0 minipro mentions                        | ✓ VERIFIED | Line `:44` reads `chip_database.json`; meta minipro count = 0                                    |

### Key Link Verification

| From                                                | To                                              | Via                                                          | Status   | Details                                                                                                       |
| --------------------------------------------------- | ----------------------------------------------- | ------------------------------------------------------------ | -------- | ------------------------------------------------------------------------------------------------------------- |
| `database.py:518` (Python emitter)                  | `json_parser.c:62/74/309` (firmware parser)     | wire JSON over 250000 baud serial — key `"vpp_mv"`            | ✓ WIRED  | Cross-sub-repo contract: emitter writes `"vpp_mv"`, parser registers `key_vpp_mv` + `extract_int("vpp_mv", handle->vpp_mv)` |
| `json_parser.c:503` (extract_int)                   | `firestarter_handle_t.vpp_mv` (firestarter.h:85) | C-struct field write via extract_int macro                    | ✓ WIRED  | Struct field unchanged (correct from v1.0); parse layer aligned                                               |
| `database.py:189` (`_read_config_file`)             | `firestarter/data/chip_database.json`            | filesystem path lookup at editable-install root                | ✓ WIRED  | `firestarter info W27C512` exit 0 confirms runtime resolution                                                 |
| `build_db.py:12` (`OUTPUT_FILE`)                    | `firestarter/data/chip_database.json`            | os.path.join(_DATA_DIR, "chip_database.json")                  | ✓ WIRED  | Writer points at same path as reader                                                                          |
| `_map_data()` output (`database.py:417`)            | `eprom_info.py:271` + `ic_layout.py:513` + `database.py:510` | in-memory dict key `vpp_volts`                                  | ✓ WIRED  | All four sites symmetric; consumers + emitter fallback all read same key                                      |
| `check_dispatch.py` (augmented)                     | `database.py::convert_to_programmer` + `chip_database.json` | `db.convert_to_programmer(db.get_eprom(part))` per-chip round-trip | ✓ WIRED  | Dynamic regression scan exits 0 with `0 wire-key regressions` across all 743 chips                            |

### Data-Flow Trace (Level 4)

| Artifact                              | Data Variable                | Source                                              | Produces Real Data | Status     |
| ------------------------------------- | ---------------------------- | --------------------------------------------------- | ------------------ | ---------- |
| `database.py::convert_to_programmer`  | `vpp_mv` wire-dict value     | `_map_data()` → `vpp_mv` int millivolts             | Yes                | ✓ FLOWING  |
| `json_parser.c::get_vpp_mv`           | `handle->vpp_mv`             | wire JSON `"vpp_mv"` token via `extract_int` macro  | Yes                | ✓ FLOWING  |
| `eprom_info.py:271` (info CLI render) | `ic['vpp_volts']`            | `_map_data()` dict write at `:417`                  | Yes                | ✓ FLOWING  |
| `ic_layout.py:513` (DIP render)       | `eprom_data['vpp_volts']`    | `_map_data()` dict write at `:417`                  | Yes                | ✓ FLOWING  |
| `check_dispatch.py` (augmented)       | `wire` dict per chip          | `db.convert_to_programmer(db.get_eprom(part))`      | Yes                | ✓ FLOWING  |

### Behavioral Spot-Checks

| Behavior                                           | Command                                                                                | Result                                                                                            | Status |
| -------------------------------------------------- | -------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- | ------ |
| Wire emit contains `vpp_mv`, not `vpp`             | `python -c "from firestarter.database import EpromDatabase; ..."`                       | `{'memory-size': 65536, 'type': 1, 'algorithm': 7, 'pin-count': 28, 'vpp_mv': 12000, ...}`        | ✓ PASS |
| `check_dispatch.py` reports 0 wire regressions     | `cd firestarter_app && python tools/check_dispatch.py`                                  | Exit 0; `PASS: all 743 chips have a valid dispatch path; ... 0 wire-key regressions`              | ✓ PASS |
| `firestarter --help` runs                          | `firestarter --help`                                                                    | Exit 0; CLI usage printed                                                                          | ✓ PASS |
| `firestarter info W27C512` resolves renamed DB     | `firestarter info W27C512`                                                              | Exit 0; chip metadata printed (10 lines: Name, Manufacturer, Pins, Memory, Type, VCC, Chip ID...) | ✓ PASS |
| `firestarter info --adapter W27C512` adapter table | `firestarter info --adapter W27C512`                                                    | Exit 0; 63 lines with adapter pinout table for DIP28_27512                                         | ✓ PASS |

### Probe Execution

| Probe                  | Command                                  | Result                                                                                     | Status |
| ---------------------- | ---------------------------------------- | ------------------------------------------------------------------------------------------ | ------ |
| `check_dispatch.py`    | `cd firestarter_app && python tools/check_dispatch.py` | Exit 0; `PASS: all 743 chips have a valid dispatch path; 0 SRAM chips route to configure_eprom; 0 DIP28_2764 Flash/EEPROM chips route to configure_eprom; 0 wire-key regressions` | ✓ PASS |

(No `scripts/*/tests/probe-*.sh` convention probes exist in this project; `check_dispatch.py` is the host-side regression scanner declared by the plan.)

### Requirements Coverage

| Requirement | Source Plan(s)        | Description                                                                                       | Status      | Evidence                                                                                                |
| ----------- | --------------------- | ------------------------------------------------------------------------------------------------- | ----------- | ------------------------------------------------------------------------------------------------------- |
| WIRE-01     | 02-01, 02-02          | Wire JSON `"vpp"` key renamed to `"vpp_mv"` across Python emitter, firmware parser, and docs       | ✓ SATISFIED | SC1 + T1 + T4 evidence (Python emit + firmware parse + docs all use `vpp_mv` only)                       |
| WIRE-02     | 02-03                 | `check_dispatch.py` host-side test confirms every chip parses end-to-end with no wire regression   | ✓ SATISFIED | SC4 + T7 evidence (augmented scanner runs all 743 chips with `0 wire-key regressions`)                   |
| CLEAN-01    | 02-02                 | Data filename renamed from `minipro_complete_db.json` to `chip_database.json`; all refs updated     | ✓ SATISFIED | SC2 + T3 + T6 evidence (file renamed via `git mv`; blame preserved; 7 callsites + packaging metadata flipped) |
| CLEAN-02    | 02-03                 | Unnecessary minipro mentions removed; single CLAUDE.md attribution + `MINIPRO_XML_URL` constant retained | ✓ SATISFIED | SC3 + T8 + T9 evidence (1 minipro line in `firestarter_app/CLAUDE.md:68`; 0 elsewhere; URL constant preserved) |

All four phase requirement IDs (WIRE-01, WIRE-02, CLEAN-01, CLEAN-02) are satisfied. REQUIREMENTS.md traceability table currently shows WIRE-01 + CLEAN-01 as "Complete" and WIRE-02 + CLEAN-02 as "Pending" — the latter two are now closed by this phase and the traceability table should be updated to "Complete" as part of the metadata commit.

### Anti-Patterns Found

| File                                         | Line     | Pattern                                    | Severity     | Impact                                                                                                  |
| -------------------------------------------- | -------- | ------------------------------------------ | ------------ | ------------------------------------------------------------------------------------------------------- |
| `firestarter_app/MANIFEST.in`                | :4       | `include firestarter/data/avrdude.conf` references a file that does not exist | ⚠️ Warning (pre-existing) | Phase 02 REVIEW WR-01; pre-existing drift NOT introduced by this phase; setuptools emits warning at sdist time |
| `firestarter_app/firestarter/database.py`    | :191     | `override_proms = None  # //_read_config_file("database_overrides.json")` — `database_overrides.json` packaged but never loaded | ⚠️ Warning (pre-existing) | Phase 02 REVIEW WR-02; pre-existing condition NOT introduced by this phase                              |
| `firestarter_app/tools/check_dispatch.py`    | ~:62     | Stale comment references nonexistent `_PROTOCOL_OVERRIDES` constant | ℹ️ Info (cosmetic) | Phase 02 REVIEW WR-03; cosmetic stale comment, no behavioral impact                                     |

No blockers found. All three items above are advisory carry-overs from `02-REVIEW.md` (pre-existing or cosmetic drift), explicitly out-of-scope for phase 02 goal achievement.

### Open Follow-Ups (Advisory, Non-Blocking)

These items were flagged by the standalone code review (`02-REVIEW.md`) and should be addressed in a future cleanup plan. They are NOT blockers for phase 02 verification:

1. **WR-01:** Remove the unused `include firestarter/data/avrdude.conf` line from `MANIFEST.in` (file doesn't exist).
2. **WR-02:** Either un-comment `database.py:191` to actually load `database_overrides.json`, or remove the file + its packaging declarations.
3. **WR-03:** Remove the stale `_PROTOCOL_OVERRIDES` comment reference in `check_dispatch.py:62`.

(Plus the pre-existing co-located dirt in `firestarter_app/` working tree documented across all three Plan SUMMARYs: `firestarter/__init__.py` version bump, deleted `.planning/codebase/*.md` files, and the `ic_layout.py` whitespace reformat carrying a load-bearing `pin_map_details["vpp-pin"][0]` indexing fix.)

### Human Verification Required

None. All phase 02 success criteria are programmatically verifiable via grep gates + `check_dispatch.py` dynamic scan + CLI smoke. Hardware-side verification (HW-01..HW-05) is owned by Phase 4 per the roadmap dependency graph and is not in scope for this phase.

### Gaps Summary

**No gaps found.** All 5 roadmap Success Criteria and all 14 must-have truths (5 SCs + 9 plan-derived) are verified end-to-end:

1. **Wire-key flip (SC1):** Python emitter at `database.py:518` emits `"vpp_mv"`; firmware parser at `json_parser.c:62/74/309` reads `"vpp_mv"` into `handle->vpp_mv`; doc examples in both sub-repo CLAUDE.md files show only `vpp_mv`. Cross-sub-repo contract holds end-to-end.

2. **File rename (SC2):** `git mv` preserved blame (`--follow` returns 4 commits); 7 callsites (reader path, docstring, OUTPUT_FILE, check_dispatch docstring, check_dispatch glob, meta CLAUDE.md, all three CLAUDE.md doc files) all point at `chip_database.json`; old filename is absent from the working tree.

3. **Minipro scrub (SC3):** `firestarter_app/CLAUDE.md` keeps exactly 1 attribution line at `:68` (co-located with `infoic.xml` + `chip_database.json`); `firestarter/CLAUDE.md` = 0; meta `CLAUDE.md` = 0; `database.py` = 0; `check_dispatch.py` = 0; `MINIPRO_XML_URL` constant at `build_db.py:10` retained verbatim per D-09 (load-bearing — the actual upstream URL).

4. **Regression scan (SC4):** `python tools/check_dispatch.py` exits 0 with the verbatim PASS line `PASS: all 743 chips have a valid dispatch path; 0 SRAM chips route to configure_eprom; 0 DIP28_2764 Flash/EEPROM chips route to configure_eprom; 0 wire-key regressions`. The new D-15 Shape A augmentation (per-chip `db.convert_to_programmer(db.get_eprom(part))` round-trip + `wire_regressions` failure list) is wired into the existing union-failure check + `sys.exit(1)` contract.

5. **CLI smoke (SC5):** `firestarter --help` exit 0; `firestarter info W27C512` exit 0 (renamed DB resolves through `EpromDatabase` singleton + editable-install package-data); `firestarter info --adapter W27C512` exit 0 (exercises both `pinouts.json` read path AND `get_adapter_table()` — no `KeyError` from the renamed dict key `vpp_volts`).

Three internal layers of `vpp` semantics are correctly distinguished and the boundaries are regression-proofed:
- **Wire layer:** `vpp_mv` (int mV) — flipped by Plan 02-01.
- **Internal dict layer:** `vpp_volts` (float V) — flipped by Plan 02-02; both consumers + emitter fallback symmetric with the `vpp_mv` int sibling.
- **Upstream-schema READ layer:** `electrical.get("vpp", "0").replace("V", "")` at `database.py:375` — PRESERVED per D-08-compat (reads on-disk DB string `"12V"` and legacy user-override DBs at `~/.firestarter/database.json`).

Phase 02 is structurally complete and ready to move forward to Phase 3 (Retroactive Verification).

---

_Verified: 2026-05-12T09:30:00Z_
_Verifier: Claude (gsd-verifier)_
