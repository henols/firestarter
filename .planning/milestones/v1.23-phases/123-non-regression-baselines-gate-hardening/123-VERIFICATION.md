---
phase: 123-non-regression-baselines-gate-hardening
verified: 2026-07-31T03:15:00Z
status: passed
score: 8/8 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 123: Non-Regression Baselines & Gate Hardening Verification Report

**Phase Goal:** Every gate and baseline this milestone will judge later phases against exists — and
is proven able to fail on a planted violation — before a single firmware file moves.
**Verified:** 2026-07-31
**Status:** passed
**Re-verification:** No — initial verification

**Verification method:** This report re-executes the phase's evidence rather than trusting
123-NONREGRESSION.md's narration. Every command below was re-run independently in this session
against the live trees at `firestarter@34bda8c` / `firestarter_app@ccbc401` / meta
`gsd/v1.23-py32f071-integration`. Where 123-NONREGRESSION.md's claim disagreed with what this
session observed, that disagreement would have been reported — none was found. One claim
(the checker-convention meta-test's "proven to fail" assertion) was independently reproduced from
scratch by this verifier (temporarily removing a real test file and restoring it), not merely read
from the SUMMARY.

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria, verified mechanically)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Committed baseline records flash+RAM for all 3 AVR targets + native case/suite counts | ✓ VERIFIED | `firestarter/scripts/baseline/size_baseline.json` read directly; re-ran `pio run -e {uno,uno328pb,leonardo}` fresh — uno 23932/1573, uno328pb 23976/1579, leonardo 26072/2014, all byte-exact vs JSON. Re-ran `pio test -e native` and `-e native_nodevtools` fresh — both **141 cases, 17 suites, all PASSED**, matching JSON exactly. |
| 2 | Split FW-absent proxy: present-repo+missing-target ⇒ hard failure; skip census fails on absent-reason-while-marker-exists; both proven against committed fixture | ✓ VERIFIED | `tests/fw_presence.py` `ARMED = _PLATFORM_DIR.is_dir()`-style split confirmed; `test_present_repo_missing_target_is_hard_failure` asserts `MissingScanTargetError` in output (subprocess-verified). Committed `tests/fixtures/fake_firestarter/` confirmed via `git ls-files` (3 files, no `.git`, no `src/proms/eeprom_28c.cpp` — exactly the planted omission). `test_no_skip_claims_firmware_absent_while_marker_present` + `test_every_skip_reason_is_allow_listed` present and passing. Ran `pytest tests/test_fw_presence.py tests/test_scan_paths_resolve.py tests/test_skip_census.py` → **16 passed** (matches NONREGRESSION H11). |
| 3 | CMake manifest-drift gate: non-zero on mismatched-path fixture, exit-0 on reasoned `PY32_EXCLUDED` omission | ✓ VERIFIED | `pytest tests/test_check_cmake_manifest.py -v` → 8/8 passed including `test_mismatched_path_fails_with_exactly_one_violation` (asserts `returncode != 0` AND `"FAIL: 1 "` substring) and `test_reasoned_omission_passes_and_is_named`. Live gate run: `python3 scripts/check_cmake_manifest.py` → `UNARMED: .../platform/py32f071 absent -- ... arms itself the moment Phase 124 lands`, exit 0 — reproduced verbatim, and `platform/` genuinely absent on disk. `ARMED = _PLATFORM_DIR.is_dir()` confirmed in source — a structural coarse key, not a manual flag. |
| 4 | Orphan-provisional-macro checker non-zero on zero-consumer fixture; warning-count gate non-zero on one-macro-redefinition fixture | ✓ VERIFIED | `pytest tests/test_check_orphan_provisional.py -v` → 8/8 passed incl. `test_orphan_fails_with_exactly_one_violation` (asserts `returncode != 0`, `"FAIL: 1 "`, named macro). `pytest tests/test_check_build_warnings.py -v` → 10/10 passed incl. `test_avr_exact_zero_fires_on_planted_redefinition` and `test_native_watermark_fires_on_planted_excess`. Live gate: `check_orphan_provisional.py` → identical `UNARMED:` line, exit 0 (no `RURP_*_PROVISIONAL` in tree today, confirmed). |
| 5 | `check_permitted_claims.py` non-zero on empty target list (fail-closed) and on forbidden-phrase fixture; every new checker has planted fixture + non-zero-exit pytest | ✓ VERIFIED | `FIRESTARTER_CLAIMSCAN_TARGETS="" python3 check_permitted_claims.py` → `FAIL: no scan targets resolved -- the gate cannot vacuously pass with nothing scanned`, exit 1 (reproduced directly). Default run (env unset) → `UNARMED: none of the 4 named v1.23 closing artifacts for Phase 130 exist yet`, exit 0 — correctly distinguishes "absent env var" from "present but empty" (D-15). `pytest test_check_permitted_claims.py` → **10 passed**, including D-16 both-direction proximity tests. BASE-08 meta-test (`test_checker_convention.py`) 7/7 passed; independently reproduced its failure mode by temporarily moving `tests/test_check_orphan_provisional.py` aside — suite went **1 failed, 6 passed** naming the exact missing pairing, then restored cleanly (48 passed, `git status --porcelain` clean). |

**Score:** 8/8 must-haves verified (5 ROADMAP success criteria + BASE-01, BASE-07, BASE-08 folded into the table above represent all 8 BASE-01..08 requirements; see Requirements Coverage below for the 1:1 mapping).

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter/scripts/baseline/size_baseline.json` | Machine-readable baseline, meta block + AVR + native + warnings | ✓ VERIFIED | Read directly; contains `firmware_tree_sha`, all 6 AVR figures, both native `{cases,suites}` pairs, `avr_rule: "== 0"`, `native_rule: "<= total_watermark"`, and the 360-pre-existing-debt note (checked in Requirement BASE-06 detail below) |
| `firestarter/scripts/check_size_baseline.py` | AVR+native comparator, env-seam driven | ✓ VERIFIED, WIRED | Ran directly against real baseline; matches JSON exactly for all 3 AVR + 2 native envs |
| `firestarter/scripts/check_build_warnings.py` | AVR exact-zero + native 360-watermark | ✓ VERIFIED, WIRED | Ran against fresh `pio test -e native` output captured this session; 360/360 confirmed independently via `grep -cE 'warning:'` |
| `firestarter/scripts/check_cmake_manifest.py` | Coarse-key armed, exempt SDK sources, reasoned allow-list | ✓ VERIFIED, WIRED (UNARMED, honestly) | Live-ran; `ARMED = _PLATFORM_DIR.is_dir()` confirmed in source |
| `firestarter/scripts/check_orphan_provisional.py` | Coarse-key armed, repo-wide macro scan | ✓ VERIFIED, WIRED (UNARMED, honestly) | Live-ran; same coarse-key pattern confirmed |
| `firestarter/tests/test_checker_convention.py` | BASE-08 meta-test, FLOOR=4/FIXTURE_FLOOR=9 | ✓ VERIFIED, WIRED | 7/7 passed; failure mode independently reproduced (see above) |
| `firestarter_app/tests/fw_presence.py` | Single presence probe, `.git`-keyed | ✓ VERIFIED, WIRED | Source read; `MissingScanTargetError` confirmed raised via subprocess test |
| `firestarter_app/tests/scan_paths.py` | D-11 central cross-repo scan-path inventory | ✓ VERIFIED, WIRED | `pytest tests/test_scan_paths_resolve.py` → 4 passed; resolves against the real firmware sibling |
| `firestarter_app/tools/check_no_exists_proxy.py` | D-9 recurrence lint | ✓ VERIFIED, WIRED | Ran directly: `PASS: scanned 78 file(s)`, exit 0; planted fixture + line-number-naming test confirmed (`tests/test_check_no_exists_proxy.py`, 8/8 passed) |
| `firestarter_app/tests/fixtures/fake_firestarter/` | Committed incomplete sibling (D-12) | ✓ VERIFIED | `git ls-files` confirms exactly 3 committed files, `.git` marker correctly absent (git itself refuses to stage any `.git`-named path component — independently reproduced in a scratch repo) |
| `.planning/phases/123-.../check_permitted_claims.py` | v1.23 8-phrase claim gate, D-15/D-16 | ✓ VERIFIED, WIRED | Ran directly; fail-closed and UNARMED behaviors both reproduced |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `check_size_baseline.py` / `check_build_warnings.py` | `size_baseline.json` | `FIRESTARTER_SIZE_BASELINE` env seam | WIRED | Confirmed by reading both scripts' source and running them against the real baseline file with no override |
| 7 rekeyed host proxy modules | `../firestarter/.git` | `fw_presence.py` import | WIRED | `pytest` the 7-module set → 49 passed, 0 skipped (matches NONREGRESSION H10) |
| `check_cmake_manifest.py` / `check_orphan_provisional.py` | `platform/py32f071/` | `ARMED = _PLATFORM_DIR.is_dir()` | WIRED (correctly dormant) | Confirmed structural, not a manual flip constant |
| `check_permitted_claims.py` | Phase-130 closing artifacts | `FIRESTARTER_CLAIMSCAN_TARGETS` env seam, default list | WIRED (correctly dormant) | Distinguishes unset-env (default list, UNARMED) from explicitly-empty (fail-closed) — both reproduced |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| BASE-01 | 123-01, 123-02 | Baseline records flash+RAM+native counts | ✓ SATISFIED | Re-measured fresh this session, byte-exact |
| BASE-02 | 123-07, 123-08 | FW-absent proxy split, hard-failure-not-skip | ✓ SATISFIED | `MissingScanTargetError` reproduced |
| BASE-03 | 123-09 | Skip census fails on absent-reason-while-present | ✓ SATISFIED | Test present and passing, allow-list confirmed |
| BASE-04 | 123-04 | CMake manifest-drift gate, coarse-armed | ✓ SATISFIED | Live-run + fixture tests both reproduced |
| BASE-05 | 123-05 | Orphan-provisional-macro checker, coarse-armed | ✓ SATISFIED | Live-run + fixture tests both reproduced |
| BASE-06 | 123-03 | Warning-count gate, AVR==0 + native watermark | ✓ SATISFIED | All 3 statement locations confirmed present (see detail below) |
| BASE-07 | 123-10 | `check_permitted_claims.py` v1.23 table, fail-closed | ✓ SATISFIED | Fail-closed and D-16 both directions reproduced |
| BASE-08 | 123-02..09, 123-06 | Every new checker has planted fixture + non-zero-exit pytest | ✓ SATISFIED | 40 firmware pytest + 8 host recurrence-lint tests, all reproduced |

**No orphaned requirements** — REQUIREMENTS.md maps only BASE-01..08 to Phase 123, all 8 accounted for above. **No other requirement category (MERGE/VPP/CFG/HOST/REL/PCB/CLOSE) was touched**, confirmed by `git log -p -- .planning/REQUIREMENTS.md` since `1ea7649` showing only BASE-01..08 checkbox flips, in a single commit (`466904b`, attributed to 123-11).

### BASE-06 three-statement check (mandate item 6)

Locked scope: `== 0` on the three AVR envs, `<= 360` watermark on native, plus an explicit "characterised pre-existing debt, not a regression" statement in three places — all three independently confirmed present:
1. **Baseline JSON** (`warnings.note` field): "...caused by each suite's own test/native/avr/<suite>/avr/pgmspace.h host shim... It is not a regression and not damage."
2. **Checker docstring** (`check_build_warnings.py` lines 14-29): "**The 360 is characterised pre-existing debt, not damage.**... it is **not a regression** and it is not damage."
3. **Evidence artifact** (`123-NONREGRESSION.md` §5.3): "Measured **pre-existing** on `beta` at the recorded fork point... **not a regression** and not damage."

### D-16 both-directions check (mandate item 7)

`fixtures/clean_avr_bench_control.md` (contains "bench-validated" with no py32 token nearby) — `test_d16_negative_direction_avr_bench_control_passes` confirms exit 0. `fixtures/planted_py32_overclaim.md` — `test_planted_py32_overclaim_flips_checker_to_failure` confirms non-zero exit. A third test, `test_d16_proximity_suppression_is_real_not_accidental`, mutates a copy of the clean control by inserting a py32 token into the proximity window and confirms the mutated copy DOES fail — proving suppression is a real mechanism, not an accidental non-match. All three read and confirmed present in `test_check_permitted_claims.py`; full suite (10 tests) run and passed.

### Behavioral Spot-Checks / Re-executed Counts (mandate item 5)

| Check | Command | Expected | Observed |
|-------|---------|----------|----------|
| Firmware pytest | `cd firestarter && python3 -m pytest tests/ -q` | 48 passed, 0 skipped | **48 passed** ✓ |
| Firmware native | `pio test -e native` | 141/141, 17 suites | **141/141, 17 suites, all PASSED** ✓ (fully re-run, not skipped) |
| Firmware native_nodevtools | `pio test -e native_nodevtools` | 141/141, 17 suites | **141/141, 17 suites, all PASSED** ✓ (fully re-run, not skipped) |
| Host full suite | `cd firestarter_app && python3 -m pytest tests/` | 1158 passed, 0 skipped | **1158 passed**, 0 skipped ✓ |
| Meta claim gate pytest | `python3 -m pytest test_check_permitted_claims.py` | 10 passed | **10 passed** ✓ |
| Host ruff/format/mypy | `ruff check`, `ruff format --check`, `check_mypy_watermark.py` | clean | All checks passed; 104 files formatted; 1 error, 34 below watermark 35 (unchanged) ✓ |
| AVR builds (uno/uno328pb/leonardo) | `pio run -e <env>` | match baseline exactly | **23932/1573, 23976/1579, 26072/2014** — byte-exact ✓ |

All counts independently re-executed by this verifier, not read from SUMMARY/NONREGRESSION prose. No disagreement found anywhere.

### Anti-Patterns Found

None. Scanned all new checker scripts, paired tests, and the `check_no_exists_proxy.py`/claim-gate files for `TBD|FIXME|XXX|TODO|HACK|PLACEHOLDER` — zero hits. The single `TBD` string found in the phase's own artifacts (`123-11-PLAN.md:310`) is a direct quote of ROADMAP.md's own literal `**Plans**: TBD` placeholder text for a *future* phase, not a debt marker in this phase's delivered code.

### Boundary Compliance (mandate item 8)

- **No firmware production code moved.** `git diff --stat <fork_point_firmware>..HEAD -- src include platformio.ini .github test` independently re-run by this verifier: **empty**. Fork point (`5c9160a3...`) confirmed an ancestor of HEAD.
- **`platformio.ini` untouched**: `git log --oneline <fork>..HEAD -- platformio.ini` → empty.
- **No ref-less `diff --stat --` shape** anywhere in the phase's own `*-PLAN.md` files: independently re-run, **0** occurrences.
- **Host-repo changes confined to `tests/` and `tools/`** — confirmed via `git diff --name-only <fork_point_host>..HEAD`, no path under `firestarter_app/firestarter/` (the app's own package) touched.
- **No push, no `gh` invocation** — no `origin/v1.23-py32f071-integration` remote branch exists in either sub-repo; no `gh` references found in phase artifacts.
- **Both py32 worktrees untouched** — `firestarter_py32_ci/` and `firestarter_app_py32/` directory mtimes are 2026-07-28, predating this phase's 2026-07-30/31 work; both are separate gitignored checkouts, unaffected by any commit in the tracked repos.
- **Requirement ticking discipline** — only BASE-01..08 flipped, only in commit `466904b` (123-11). Confirmed via full `git log -p` over REQUIREMENTS.md since milestone start.

### Human Verification Required

None. Every must-have in this phase is a checker/gate/count that is mechanically verifiable, and every one was independently re-executed in this session.

### Notes / Minor Observations (not gaps)

1. **`test_checker_convention.py` (BASE-08 meta-test) does not use a traditional committed `planted_*` fixture** the way the other four checkers do — by design (D-08 explicitly rejects a registry file; the meta-test asserts hardcoded floors against the live `firestarter/scripts/` tree). This verifier independently reproduced its failure mode (temporarily removing `tests/test_check_orphan_provisional.py`, confirming `1 failed, 6 passed` naming the exact gap, then restoring cleanly) rather than trusting 123-06-SUMMARY.md's identical claim. The mechanism is real and the design rationale (avoiding a registry file per D-08) is sound; noted here only because the phase's own verification mandate calls this checker out by name.
2. **`check_mypy_watermark.py` has no paired test** — explicitly acknowledged as pre-existing (v1.18-era) debt in `test_checker_convention.py`'s docstring and out of BASE-08's scope (which targets checkers "introduced in this milestone"). Not a gap this phase claims to close.
3. **`STATE.md` frontmatter still reads `status: executing`** rather than a closed/complete marker, though the body text and progress counters correctly show Phase 123 complete (11/11 plans, BASE-01..08 all Complete). This is orchestrator bookkeeping, not a phase-goal defect.

---

_Verified: 2026-07-31_
_Verifier: Claude (gsd-verifier)_
