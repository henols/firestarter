---
phase: 149-firmware-page-size-seam-dual-repo-lockstep
verified: 2026-08-20T00:00:00Z
status: passed
score: 9/9 must-have truth groups verified (all 5 roadmap success criteria + all requirement-level must_haves across 8 plans)
behavior_unverified: 0
overrides_applied: 0
---

# Phase 149: Firmware Page-Size Seam (dual-repo lockstep) Verification Report

**Phase Goal:** Deliver the per-chip page size from `chip_database.json` over the existing JSON
command path to the `0x0D` handler with a conservative 64-byte fallback, constants held in
lockstep across both repos, flash/RAM measured against a pre-change baseline on all three AVR
targets, and the change stated software-proven and unvalidated on silicon.

**Verified:** 2026-08-20
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (Roadmap Success Criteria, cross-checked against code, not SUMMARY prose)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Per-chip page size travels DB → wire → firmware handler; a 128-byte-page entry is observed to deliver 128 | ✓ VERIFIED | `firestarter_app/tools/build_db.py` emit arm confirmed to add page_size to exactly 15@128 + 3@64 of the 84 algorithm-13 rows (independently recomputed from the live `chip_database.json`, matches commit c254cbc's own claim exactly). `database.py:558-567` emits `page-size` wire key only when present. Firmware `json_parser.c` parses it into `handle->page_size`. Native oracle `test_pgsz_delivered_128_halves_the_flush_count` (ran directly: 11/11 PASSED) proves 128 → 130 `get_data` calls (1 flush) vs the 64-byte default's 132 (2 flushes) |
| 2 | Absent page-size field falls back to conservative 64-byte floor, exercised by a test | ✓ VERIFIED | `eeprom28c_page_mask()` (`eeprom_28c.cpp:572-580`) validates `requested==0` BEFORE the power-of-two/subtraction check (rejects the wrap-to-all-ones hazard), and non-power-of-two / out-of-range also fall back. Ran `test_pgsz_absent_field_reproduces_the_64_byte_cadence`, `test_pgsz_explicit_64_matches_the_absent_cadence`, `test_pgsz_non_power_of_two_falls_back_silently`, `test_pgsz_out_of_range_falls_back_silently` directly: all 4 PASSED (132 calls in every case) |
| 3 | `firestarter.h` and `constants.py` constants/flag bits stay in lockstep, verified by a cross-repo parity check | ✓ VERIFIED | `tests/test_json_key_parity.py` ran live (firmware checkout present, not skipped): 10/10 PASSED, including `test_page_size_key_string_matches_constants_py`, `test_every_dispatched_identifier_has_a_declared_key_string`, and both planted-drift detection legs (`test_planted_key_string_drift_is_detected`, `test_planted_undispatched_key_is_detected`). `constants.py:150-153`'s "Firmware sync" note is now true (deviation #1 confirmed resolved in app commit 0744348) |
| 4 | Flash+RAM deltas measured for all 3 AVR targets against a pre-change baseline; leonardo headroom stated as a number; v1.31 MERGE-05 breach named | ✓ VERIFIED | Cold `--rebuild` run of `check_size_baseline.py` (default byte-identity mode) against live `size_baseline.json`: PASS, figures byte-identical (uno 25130/1575, uno328pb 25180/1581, leonardo 27212/2016). `--policy merge05 --baseline size_baseline_base01.json` with the committed cold `149-postchange-cold-*.log` files: PASS, printing `+306<=306=band0+exempt96+seam210` (leonardo, 0 B headroom stated) and `+306<=370=band64+exempt96+seam210` (uno-class). Re-ran the 3 tripwire fixtures one byte past the new allowance directly: all 3 FAIL as designed (flash leonardo, flash uno, RAM uno) |
| 5 | Every artifact states "software-proven and unvalidated on silicon"; no silicon claim; `0x0D` stays UNVERIFIED; no support_status change | ✓ VERIFIED | Phrase appears 10+ times through `149-PAGE-SIZE.md` (opening statement plus every plan-evidence section) and in `firestarter_app/README.md`'s new "Breaking Changes (v1.32)" subsection (confirmed present via grep). Ran the phase's own claim gate (`149-check-claims.py`) against all 9 targets including README via argv: EXIT=0. Re-ran the committed RED transcripts (8 planted-violation legs) directly: all reproduce EXIT=1 exactly as recorded. `grep -rn "support_status"` across DB tooling shows no write path touched by this phase; `0x0D`'s `support_status` value is unchanged in `chip_database.json` |

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter/include/firestarter.h` | `page_size` field on handle | ✓ VERIFIED | `uint16_t page_size` present, reset to 0 per command in `json_parser.c:290` |
| `firestarter/src/json_parser.c` | `key_page_size`, dispatch row, `get_page_size` | ✓ VERIFIED | All three present; `key_parsers[]` row confirmed wired |
| `firestarter/src/proms/eeprom_28c.cpp` | `AT28C_PAGE_SIZE_FALLBACK`, `eeprom28c_page_mask`, hoisted mask | ✓ VERIFIED | All present; mask resolved once above the per-byte loop (`eeprom28c_write_execute:606`), never per-byte modulo |
| `firestarter_app/tools/build_db.py` | provenance-keyed page_size emit arm | ✓ VERIFIED | `_upstream_proto_id` captured before `classify()` reassigns `proto_id`; independently recomputed 15@128+3@64 = 18 rows |
| `firestarter_app/firestarter/database.py` | wire `page-size` key emission | ✓ VERIFIED | Emit-when-present at both ingest (`_map_data`) and wire-conversion sites |
| `firestarter_app/firestarter/constants.py` | `JSON_KEY_PAGE_SIZE`, true "Firmware sync" note | ✓ VERIFIED | Present; note confirmed no longer false (deviation #1 resolved) |
| `firestarter_app/tests/test_page_size_invariants.py`, `test_wire_dict_equivalence.py`, `test_json_key_parity.py` | exhaustive host proofs | ✓ VERIFIED | Ran directly: 26 + 10 = 36 tests, all passed, live legs (not skipped) |
| `firestarter/tests/test_check_size_baseline.py` + fixtures | tripwire re-armed | ✓ VERIFIED | Ran the 3 planted fixtures directly against BASE-01: all FAIL exactly as documented |
| `firestarter/scripts/baseline/size_baseline.json` | live baseline re-anchored | ✓ VERIFIED | Cold rebuild figures match byte-for-byte; `firmware_tree_sha` corrected to `c6349d22...` |
| `.planning/phases/.../149-PAGE-SIZE.md` | complete D-16 review artifact | ✓ VERIFIED | 1699 lines, all sections present, no placeholders, phrase present throughout |
| `firestarter_app/README.md` | changelog subsection | ✓ VERIFIED | "Breaking Changes (v1.32)" section present, phrase included, gate-scanned via argv |
| `.planning/phases/.../149-check-claims.py` | extended 9-target claim gate | ✓ VERIFIED | Ran directly against all 9 targets (8 phase artifacts + README via argv): EXIT=0 |
| 4 new pending todos + folded todo removed | `.planning/todos/pending/*` | ✓ VERIFIED | All 4 files present on disk; `remove-dead-json-init-sizeof-pointer-bug.md` confirmed deleted (commit a4004885); `json_init()` confirmed absent from `src/`/`include/` via grep |

### Key Link Verification

| From | To | Via | Status |
|------|-----|-----|--------|
| `build_db.py` | `chip_database.json` | provenance-keyed emit, `proto_id == 0x0D` before reassignment | ✓ WIRED — recomputed independently, exact 18-row match |
| `chip_database.json` | wire `page-size` key | `database.py` emit-when-present | ✓ WIRED |
| `json_parser.c` | `firestarter_handle_t.page_size` | `get_page_size`/`extract_int` | ✓ WIRED |
| `firestarter_handle_t.page_size` | `eeprom28c_write_execute`'s flush boundary | `eeprom28c_page_mask()` hoisted once | ✓ WIRED — behaviorally proven by native oracle |
| `test_json_key_parity.py` | `firestarter/src/json_parser.c` | `fw_path()` module-scope resolution | ✓ WIRED — live legs ran (firmware present), hard-fails on rename by design |
| `scan_paths.py` | `src/json_parser.c` | new `ScanPathEntry` | ✓ WIRED — confirmed entry present |
| `check_size_baseline.py::_merge05_flash_allowance` | PASS-line builder + `compare_avr_policy_merge05` | sole resolver | ✓ WIRED — output strings match exactly on live run |

### Behavioral Spot-Checks (executed live, not trusted from SUMMARY)

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Flush-count oracle (128→130, 64/absent/invalid→132) | `pio test -e native -f "*test_val_eeprom28c*"` | 11/11 PASSED | ✓ PASS |
| D-11 unknown-key-before-known-key non-desync | `pio test -e native -f "*test_read_timing*"` | 9/9 PASSED | ✓ PASS |
| DB census (15@128+3@64 among algorithm-13 rows) | ad hoc `python3` recount over live `chip_database.json` | 15/3/18/84 exact match | ✓ PASS |
| Host invariant + wire equivalence + parity suites | `pytest tests/test_page_size_invariants.py tests/test_wire_dict_equivalence.py tests/test_json_key_parity.py` | 36/36 passed (parity live, not skipped) | ✓ PASS |
| Cold AVR rebuild vs live baseline (default mode) | `check_size_baseline.py --rebuild` | PASS, byte-identical to `size_baseline.json` | ✓ PASS |
| MERGE-05 policy vs BASE-01 with committed cold logs | `check_size_baseline.py --policy merge05 --baseline size_baseline_base01.json --avr-log ...` | PASS, exact reported figures reproduced | ✓ PASS |
| Tripwire re-armed one byte past new allowance | 3 planted fixtures run directly against BASE-01 | All 3 FAIL as designed | ✓ PASS |
| Full firmware suite | `pytest tests/ -o addopts="" -q` (firestarter repo) | 315 passed | ✓ PASS |
| Full native + native_nodevtools | `pio test -e native -e native_nodevtools` | 302 test cases succeeded (151+151) | ✓ PASS |
| Build warnings gate | `check_build_warnings.py --rebuild` | PASS, 998 (168 below 1166 watermark), 0 macro redefinitions | ✓ PASS |
| Full host app suite | `pytest -q` (firestarter_app repo) | 1697 passed | ✓ PASS |
| Claim gate over all 9 targets incl. README via argv | `149-check-claims.py 149-PAGE-SIZE.md ... README.md` | EXIT=0 | ✓ PASS |
| Claim gate paired suite (RED+GREEN reproduction) | `pytest test_check_claims_v132.py` | 20/20 passed | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| PGSZ-01 | 149-01, 149-03, 149-04 | Page size travels DB → wire → firmware | ✓ SATISFIED | Emit arm + wire key + parse + handle field, all confirmed live |
| PGSZ-02 | 149-04 | 0x0D handler uses delivered value, conservative fallback | ✓ SATISFIED | Native flush-count oracle proves the behavior (not just presence) |
| PGSZ-03 | 149-05 | Constants stay in lockstep across repos | ✓ SATISFIED | Parity gate ran live, planted-drift legs detected as designed |
| PGSZ-04 | 149-01, 149-06, 149-07 | Flash/RAM measured against pre-change baseline, all 3 AVR targets | ✓ SATISFIED | Cold pre-edit and post-change logs both present and consistent; gates reproduce exactly |
| PGSZ-05 | all plans, finished 149-08 | "software-proven and unvalidated on silicon" stated, no silicon/support_status claim | ✓ SATISFIED | Claim gate enforces it mechanically over 9 targets, phrase confirmed present everywhere required |

No orphaned requirements found — REQUIREMENTS.md's Phase 149 mapping (PGSZ-01..05) exactly matches the union of `requirements:` fields declared across all 8 plans' frontmatter.

### Anti-Patterns Found

None. Scanned every file touched by this phase in both repos (`firestarter.h`, `json_parser.h/.c`, `eeprom_28c.cpp`, `build_db.py`, `database.py`, `constants.py`, `check_size_baseline.py`) for `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` — zero matches. No stub returns, no empty handlers, no hardcoded-empty data flowing to a rendered/consumed path.

### Deviations Assessed

1. **Plan 05's truth #7 (constants.py "Firmware sync" note) was initially false, sent back, fixed in app commit `0744348`.** Independently confirmed the note now reads correctly and cites the real commit/mechanism. Resolved, not a gap.

2. **Plan 07's "tests/ byte-unchanged" criterion was unsatisfiable and overridden via fixture severance.** Independently confirmed: `captured_build_{uno,uno328pb,leonardo}.log` and `merge05_base01_anchor_*.log` are byte-identical before/after commit `6e3f90a` (git diff empty); the new `captured_build_v132_*.log` family exactly matches the committed cold post-change logs (diff empty on Flash/RAM lines). Full firmware suite reruns green (315 passed). Severance is sound — nothing that needed to stay frozen moved.

3. **Plan 08 amended 5 of 7 earlier SUMMARYs and flipped PGSZ-01..05 before its own operator gate.** Diffed every amended line (`149-01` through `149-07` in commit `97da8f3d`): all changes are either (a) additive PGSZ-05 caveat-phrase sentences, or (b) paraphrasing the literal word "proven" as "bare-claim-word"/"unqualified correctness claim" to avoid the SUMMARY self-tripping its own claim gate — no factual claim, number, or measured finding was altered or softened in any of the diffed hunks. REQUIREMENTS.md/ROADMAP.md diff is a clean, scoped Pending→Complete flip with no other line touched. Separately, the ROADMAP Phase-149 top-level checkbox was flipped in a later, distinct commit (`7ae74579`) with its own disclosed rationale (coordinator-directed, operator-approved exception) — consistent and not concerning.

### Evidence Ceiling Compliance (scrutinized hardest)

Confirmed independently, not merely quoted from the artifact: `chip_database.json`'s `0x0D` (algorithm 13) rows show no `support_status` field change from this phase's commits (only `programming.page_size` was added to 18 rows); AT28C256 rows are untouched (confirmed via `git diff c254cbc~1 c254cbc` limited to exactly 18 changed page_size additions). No AT28C part is referenced anywhere as bench-tested. The claim gate mechanically enforces the caveat phrase across all 9 targets and was proven both RED (on 8+ planted overclaim fixtures, reproduced live) and GREEN (on the real artifacts, reproduced live).

### PGSZ-02's Non-Vacuity Note

Confirmed the orchestrator's caution: of the 5 flush-cadence native legs, only `test_pgsz_delivered_128_halves_the_flush_count` discriminates old vs. new behavior (130 vs. the pre-existing unconditional 64-byte modulo's 132). The other four (absent/explicit-64/non-power-of-two/out-of-range) all assert 132 — the same result the old unconditional 64-byte modulo already produced pre-change. This is not a gap: those four legs correctly pin PGSZ-02's *fallback* behavior (they must reproduce the old cadence, by definition), and the one discriminating leg is exactly the criterion the roadmap's success criterion #1 demands ("observed to deliver 128"). All 5 ran and passed live.

## Human Verification Required

None. Every must-have that admits an automated check was checked and re-derived independently in this
verification pass (DB census recomputed from scratch, all size/warning/claim gates re-run cold, all
native and host test suites re-run). PGSZ-05's silicon-validation exclusion is a documented, deliberate
scope boundary (Evidence Ceiling) rather than an unverified claim — nothing in this phase asserts
anything that would require a physical AT28C part to check.

## Gaps Summary

None found. All 5 roadmap success criteria verified against live code and live test runs; all 5
requirement IDs (PGSZ-01..05) accounted for across the 8 plans' frontmatter and REQUIREMENTS.md;
all three flagged deviations independently assessed and found sound; no anti-patterns; no orphaned
requirements; no stubs; no broken key links.

---

_Verified: 2026-08-20_
_Verifier: Claude (gsd-verifier)_
