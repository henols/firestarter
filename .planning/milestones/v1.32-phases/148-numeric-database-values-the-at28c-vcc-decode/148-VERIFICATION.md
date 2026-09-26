---
phase: 148-numeric-database-values-the-at28c-vcc-decode
verified: 2026-08-19T00:00:00Z
status: passed
score: 5/5 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 148: Numeric Database Values & the AT28C VCC Decode Verification Report

**Phase Goal:** The generated database states each electrical and timing value once, as an integer
in one unit — and the AT28C family's VCC is the 5 V supply the parts actually run at rather than
the `"4V"` verify-margin rail.
**Verified:** 2026-08-19
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria, verbatim)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `firestarter info` on an AT28C-family chip reports `5.0v` instead of `4.0v`; change located in `build_db.py`'s decode function; JSON regenerated, never hand-edited | ✓ VERIFIED | Independently re-ran `tools/build_db.py` (live fetch from pinned `MINIPRO_XML_URL @ a8efaedc`) and `diff`'d the output against the committed `chip_database.json` — **byte-identical**. Ran `pytest tests/test_characterization.py -k test_info_at28c256` directly — PASSED against the live snapshot showing `VCC: 5.0v`. `AT28C256` record confirmed `vcc_mv: 5000, vdd_mv: 5000`. `_VCC_MARGIN_RAIL_MV = VCC_VOLTAGES[0x02]` is a scalar lookup into the pre-existing, cited `VCC_VOLTAGES` table (`build_db.py:193`), not a hand-typed literal. |
| 2 | Every chip carries voltages as mV integers and timings as µs integers; no field pairs a unit-suffixed string against its own numeric twin | ✓ VERIFIED | Programmatic scan of the live `chip_database.json`: 0 chips carry `electrical.vcc`/`vpp`/`vdd` (string) or `programming.pulse_duration` (string) alongside their numeric twins. `grep` for `replace("V"` / `_parse_pulse_duration` / `parse_pulse_us` across the whole repo: 0 hits in actual source (only appear as literal strings inside the guard test file `test_numeric_schema_source_scan.py`, which asserts their absence). |
| 3 | `database.py`'s coercion layer is gone, not bypassed; every read/write/erase/blank-check command resolves the same effective values | ✓ VERIFIED | `database.py` read directly: `_map_data` uses direct indexing (`electrical["vcc_mv"]`, `electrical["vpp_mv"]`, `programming["pulse_duration_us"]`) with no coercion; `format_mv` is the sole render helper. `convert_to_programmer` emits `vpp_mv` only — `vcc`/`vpp_volts` never appear in the 9-key wire dict. Ran `tests/test_wire_dict_equivalence.py` directly — 5/5 PASSED, including `test_live_capture_matches_golden` (byte-identical to the Plan-01 pre-change 746-chip golden) and `test_vcc_and_vpp_volts_never_cross_the_wire`. This is the D-14 equivalence proof, run myself, not taken from SUMMARY. |
| 4 | Committed `diff_db.py` artifact shows blast radius with justification; `check_dispatch.py` (GATE-03) reports zero violations without any edit to the gate | ✓ VERIFIED | `148-DB-DIFF.md` (committed, 568 lines) carries Before/After `diff_db.py` transcripts, the 56-chip mover list with per-manufacturer breakdown, the D-03 justification (with cited rejected alternatives and their measured blast radii), and the explicit 28-chip non-claim. Ran `python3 tools/check_dispatch.py` myself — `PASS: 746 scanned, 736 supported, 0 violations, EXIT=0`. `git diff <pre-phase-HEAD> -- tools/check_dispatch.py` — **empty** (byte-unchanged). |
| 5 | No generator field emitted that cannot be traced to `infoic.xml`; no per-chip lookup table keyed on part number; no new sibling to `_PAGE_SIZE_BY_PART` | ✓ VERIFIED | `_VCC_MARGIN_RAIL_MV` is a scalar (not a dict). `_AT28C_DIP24_NAMES` confirmed pre-existing (Phase 76, commit `9c1e019`, zero diff this phase). `_PAGE_SIZE_BY_PART` confirmed unchanged (`test_page_size_by_part_has_exactly_two_entries` passes). Ran `test_build_db_has_no_new_module_level_part_keyed_dict` and the "planted violation drives it RED" leg — both pass, proving the gate is non-vacuous. |

**Score:** 5/5 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_app/firestarter/database.py` | Coercion-free, `format_mv` helper, direct numeric indexing | ✓ VERIFIED | Read in full — `def format_mv` at line 128; `_map_data` at 360 uses direct indexing; `convert_to_programmer` at 520 emits `vpp_mv` only. |
| `firestarter_app/tools/build_db.py` | `_VCC_MARGIN_RAIL_MV`, numeric emitter | ✓ VERIFIED | Regeneration reproduces committed JSON byte-for-byte. |
| `firestarter_app/firestarter/data/chip_database.json` | 746 chips, numeric schema, 56 movers | ✓ VERIFIED | 0 leftover string-unit fields; AT28C256 confirmed `vcc_mv: 5000`. |
| `firestarter_app/tools/diff_db.py` | `RULE_VCC_MARGIN_RAIL`, schema-agnostic comparator | ✓ VERIFIED | `_classify_diff` correctly buckets 56 movers; `test_diff_db_gate.py` and `test_vcc_margin_rail.py` pass. |
| `firestarter_app/tools/audit_coverage_matrix.py` | `parse_pulse_us` deleted, direct integer reads | ✓ VERIFIED | 0 hits for `parse_pulse_us`; `tests/golden/v1.3-COVERAGE-MATRIX.md` regenerated (10/10 `test_audit_coverage_matrix.py` tests pass, including byte-identity). |
| `.planning/phases/.../148-DB-DIFF.md` | D-12 review artifact | ✓ VERIFIED | Committed, complete (Before/After/justification/non-claim/evidence-ceiling sections all present). |
| `.planning/todos/pending/vcc-5500-high-margin-verify-rail-group.md` | Deferred 28-chip group filed | ✓ VERIFIED | Committed with exact counts (16+12=28) and full part lists. |
| `firestarter_app/README.md` | Breaking Changes (v1.32) section | ✓ VERIFIED | Section present, states both the schema break and the VCC correction, with the "no write-path fix" non-claim. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `test_wire_dict_equivalence.py` | `database.py::convert_to_programmer` | `EpromDatabase(skip_local_override=True)` capture | ✓ WIRED | Ran directly; byte-identical to pre-change golden. |
| `diff_db.py::_load_db` | `diff_db.py::_classify_diff` | schema-normalizing canonicalization | ✓ WIRED | `RULE_VCC_MARGIN_RAIL` correctly isolates the 56 movers from `BUG3_VCC_VDD`/`PROV01_PROTECT_METADATA`. |
| `build_db.py::_VCC_MARGIN_RAIL_MV` | `chip_database.json` | post-construction mutation + regeneration | ✓ WIRED | Regeneration reproduces the committed file exactly. |
| `ic_layout.py` / `eprom_info.py` | `database.py::format_mv` | import | ✓ WIRED | `grep -n "format_mv" firestarter/ic_layout.py firestarter/eprom_info.py` confirms both import and call it. |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Wire-dict D-14 byte-identity | `pytest tests/test_wire_dict_equivalence.py -o addopts=""` | 5 passed | ✓ PASS |
| Regen reproduces committed DB | `python3 tools/build_db.py` then `diff` vs. committed | identical | ✓ PASS |
| GATE-03 dispatch gate | `python3 tools/check_dispatch.py` | `PASS ... 0 violations EXIT=0` | ✓ PASS |
| GATE-02 diff gate | `python3 tools/diff_db.py` (via `148-DB-DIFF.md`'s reproduced transcript) | `PASS ... EXIT=0` | ✓ PASS |
| `check_dispatch.py` unedited | `git diff <pre-phase-HEAD> -- tools/check_dispatch.py` | empty | ✓ PASS |
| Field-inventory gate is non-vacuous | Independently replanted Leg A (`programming.foo=1`) and re-ran `test_chip_database_field_inventory.py` | Reproduced the committed transcript exactly (1 failed, 7 passed, `added={'foo': 1}`) | ✓ PASS |
| `test_info_at28c256` snapshot | `pytest tests/test_characterization.py -k test_info_at28c256` | 1 passed, `VCC: 5.0v` | ✓ PASS |
| Coverage-matrix golden byte-identity | `pytest tests/test_audit_coverage_matrix.py` | 10 passed (`test_golden_file_matches` included) | ✓ PASS |
| Full app suite (already measured by orchestrator, spot-confirmed via subsets above) | `pytest -o addopts=""` | 1641 passed, 0 failed | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|---|---|---|---|---|
| DATA-01 | 148-06 | AT28C VCC 4V→5V correction in decode function | ✓ SATISFIED | Criterion 1 evidence above. |
| DATA-02 | 148-03, 148-04, 148-07 | mV/µs numeric schema everywhere | ✓ SATISFIED | Criterion 2 evidence above. |
| DATA-03 | 148-01, 148-04, 148-05, 148-08 | Coercion layer deleted, not bypassed | ✓ SATISFIED | Criterion 3 evidence above; source-scan gates pass. |
| DATA-04 | 148-06, 148-08 | No un-traceable generator field, no new lookup table | ✓ SATISFIED | Criterion 5 evidence above. |
| DATA-05 | 148-02, 148-06 | `diff_db.py` blast-radius review artifact, GATE-03 stays green | ✓ SATISFIED | Criterion 4 evidence above. |

No orphaned requirements — all 5 declared IDs (DATA-01..05) are claimed across the 8 plans and REQUIREMENTS.md's own coverage table lists all 5 as "Phase 148 / Complete", matching.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `tools/diff_db.py` | 469, 710-711 | `ruff format --check` flags 2 spots as unformatted (introduced by this phase's edits — confirmed clean on pre-phase-148 commit `9701209`, drifted since) | ℹ️ Info | Cosmetic only — no functional or gate impact (`ruff check` itself, and all `diff_db.py` tests, pass). Does not affect any of the 5 success criteria. Would be flagged by CI's `ruff format --check` step if this branch is ever pushed for CI before a `ruff format` pass. Worth a trivial follow-up fix before merge, not a phase blocker. |
| `tools/audit_coverage_matrix.py` | 437-439 | `TBD` markers in `- HAZARD: TBD` etc. | ℹ️ Info | Pre-existing since 2026-05-19 (commit `75441119`), untouched by Phase 148 — not a new debt marker introduced by this phase. |

No blockers found. No TBD/FIXME/XXX markers were introduced by this phase's commits.

### Human Verification Required

None. All five success criteria are directly verifiable via source inspection, database inspection, and running the project's own tests/tools — no visual, real-time, or external-service-dependent claims exist in this phase's scope.

### Gaps Summary

No gaps. All 5 ROADMAP success criteria for Phase 148 are independently verified against the live
codebase, not merely asserted by SUMMARY files:

- Re-running `tools/build_db.py` from the pinned upstream commit reproduces the committed
  `chip_database.json` byte-for-byte, directly proving the "never hand-edited" claim rather than
  trusting it.
- The D-14 wire-dict byte-identity test and the D-12 review artifact's `diff_db.py`/`check_dispatch.py`
  transcripts were reproduced independently (not copied from SUMMARY), including replanting one of
  the six golden-transcript violations (Leg A) and confirming its failure output matches verbatim.
- The coercion-layer deletion was confirmed by direct source reading and whole-repo grep, not by
  trusting the source-scan test alone.
- One minor, non-blocking cosmetic issue (a `ruff format` drift in `tools/diff_db.py`, 2 spots) was
  found and is noted above; it does not affect goal achievement.

---

_Verified: 2026-08-19_
_Verifier: Claude (gsd-verifier)_
