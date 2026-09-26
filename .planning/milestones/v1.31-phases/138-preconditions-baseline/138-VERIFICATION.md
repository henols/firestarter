---
phase: 138-preconditions-baseline
verified: 2026-08-09T08:30:00Z
status: passed
score: 4/4 must-haves verified
overrides_applied: 0
---

# Phase 138: Preconditions & Baseline Verification Report

**Phase Goal:** Before any v1.31 code moves, all three repos sit on verified branch bases and the pre-change
state — golden traces, per-target size, suite counts, and the live pulse-width distribution — is captured as
a citable baseline.
**Verified:** 2026-08-09T08:30:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (mapped 1:1 to ROADMAP Success Criteria, per the critical-criterion correction)

| # | Truth (ROADMAP Success Criterion) | Status | Evidence |
|---|---|---|---|
| 1 | Criterion 1 (as corrected by OD-1): `firestarter_app`'s v1.30 app work is present on `origin/beta` by content-equivalence, not ancestry, discharged by F-138-01's four oracles | ✓ VERIFIED | Independently re-ran all four oracles: `gh pr view 44 --repo henols/firestarter_app --json state,mergedAt,mergeCommit` → `{"state":"MERGED","mergeCommit":{"oid":"568e58b..."}}`; `git show --no-patch --format='%P' 568e58b` → single parent `16a313a` (confirms squash mechanism); `git merge-base --is-ancestor gsd/v1.30-sdp-surface-retirement origin/beta` → exit 1 (confirms the structural false-negative the correction describes); `comm -23` of both branches' `git ls-tree -r --name-only` → **0 lines** (empty — zero files missing). All four oracles reproduce exactly as `138-BRANCH-BASES.md` §2 and `138-BASELINE.md` §3 claim. |
| 2 | Criterion 2: each of the three repos' v1.31 branches names a verified base commit — firmware off `beta`@`3085084`, app off post-merge `beta` tip, meta off v1.30 tip | ✓ VERIFIED | `firestarter`: `git merge-base gsd/v1.31-... 3085084` → `30850845f9c0994706f28d2a74fccc3adbb4b387` (exact). `firestarter_app`: branch HEAD `4d18b645ab18a2d2465f0f623062e9249eb24132`, matches `origin/beta` at measurement time. `meta`: `d0f0c6a056efaa3537909d8ff90492f3792403f1` found in meta history and is an ancestor of current HEAD (`git merge-base HEAD d0f0c6a0...` returns itself). All three named by full SHA in `138-BRANCH-BASES.md` §4. |
| 3 | Criterion 3: committed baseline artifact holds frozen pre-change golden trace + per-target (uno/uno328pb/leonardo) flash/RAM + full native and host suite pass counts, captured before any `eprom.cpp` edit | ✓ VERIFIED | Fixture blob SHA `git rev-parse HEAD:test/native/avr/_shared/eprom_v131_expected.h` → `ca3e09f164e6e1c541ecb63d15bbebf5bce41d70` (exact match). 6/6 identity-gate assertions pass live (`pytest tests/test_golden_trace_identity_eprom_v131.py -v`). All 4 native envs measured live: `native` 141/17, `native_nodevtools` 141/17, `native_pinmap_provisional` 10/1, `native_trace_v131` 5/1 — all PASSED, exact match. AVR builds measured live: uno 23954B/1573B, uno328pb 24004B/1579B, leonardo 26016B/2014B — exact match. Firmware `pytest tests/ -q` → 227 passed (exact). Host suite `.venv/ci-replica/bin/python -m pytest tests/ -o addopts="" -q` → **1539 passed, 0 skipped** (exact match, ~201s). `git diff 3085084..HEAD --stat` on firmware shows **zero** changes to `src/proms/eprom.cpp` or `src/proms/memory.cpp` — the write-path fence held; all 8 changed files are additive test/baseline artifacts. |
| 4 | Criterion 4: committed artifact states live per-protocol `pulse_delay` distribution re-derived from shipped `chip_database.json` for `0x07`/`0x08`/`0x0B`, measured this milestone | ✓ VERIFIED | Ran `.planning/phases/138-preconditions-baseline/138-pulse-distribution.py` live: `0x07` n=170 (modal 100µs, 66.5%), `0x08` n=127 (modal 100µs, 81.9%), `0x0B` n=32 (modal 500µs, 65.6%) — exact match to `138-BASELINE.md` §6 and `138-02-PULSE-DISTRIBUTION.md`. Database blob SHA `ebd1eaac01698f64dc0861f8478b8931493d3bab` reproduced exactly. Reproduced the planted-failure non-vacuity proof independently with the documented synthetic DB — script correctly reports `VIOLATIONS: 1` / `RESULT: FAIL` before any passing run is trusted. |

**Score:** 4/4 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `.planning/phases/138-preconditions-baseline/138-BRANCH-BASES.md` | Four-oracle PREP-01 adjudication + 3 base SHAs + F-138-01/02/03 | ✓ VERIFIED | 258 lines (min 90), contains `F-138-01` (2 occurrences) |
| `.planning/REQUIREMENTS.md` (PREP-01/02 rows) | Ticked with evidence citation + wording-correction annotation | ✓ VERIFIED | `[x] PREP-01`/`[x] PREP-02`, correction block present, cites `138-BRANCH-BASES.md` |
| `.planning/phases/138-preconditions-baseline/138-pulse-distribution.py` | Reproducible self-checking script, imports `_parse_pulse_duration` | ✓ VERIFIED | 492 lines (min 150); ran live, output matches committed record exactly; imports (does not reimplement) production parser |
| `.planning/phases/138-preconditions-baseline/138-02-PULSE-DISTRIBUTION.md` | Verbatim committed output, two+ runs | ✓ VERIFIED | 348 lines (min 70), contains `RESULT: PASS` ×3, planted-failure run documented and independently reproduced |
| `firestarter/test/native/avr/_shared/host_stubs_common.inc` | `HOST_STUBS_RECORD_TIMING` storage + accessors + opt-out guard | ✓ VERIFIED | Guard present, properly fenced with `#ifdef`/`#error` cross-check against `HOST_STUBS_REAL_REGISTER_UTILS` |
| `firestarter/test/native/avr/_shared/eprom_v131_expected.h` | Comparator + 3 frozen arrays (198/221/201 entries) | ✓ VERIFIED | 649 lines; blob SHA exact match; entry counts exact match to inventory JSON |
| `firestarter/test/native/avr/test_trace_eprom_v131/*.cpp` | Per-protocol capture suite | ✓ VERIFIED | Exists; `pio test -e native_trace_v131` → 5/5 PASSED live |
| `firestarter/platformio.ini` | Dedicated 4th native env, not in `default_envs` | ✓ VERIFIED | `[env:native_trace_v131]` present; `default_envs = uno, uno328pb, leonardo` (env correctly excluded) |
| `.planning/phases/138-preconditions-baseline/138-03-TRACE-CAPTURE.md` | Entry counts, bus_config derivation, F-138-06/07 | ✓ VERIFIED | 263 lines (min 60) |
| `firestarter/tests/golden/eprom_v131_trace_inventory.json` | Blob SHA + per-array inventory | ✓ VERIFIED | Contains `blob_sha` matching live fixture blob exactly |
| `firestarter/tests/test_golden_trace_identity_eprom_v131.py` | 6-assertion parallel identity gate, fail-closed on missing git | ✓ VERIFIED | 244 lines (min 150); ran live — 6/6 PASSED; `test_git_is_required_not_optional` self-scans source for absence of skip-bypass |
| `.planning/phases/138-preconditions-baseline/138-04-HOST-BASELINE.md` | Host suite counts, tree/interpreter/version named | ✓ VERIFIED | 213 lines (min 70), contains `ci-replica`; both directory-name-dependent tests independently re-run and pass |
| `firestarter/scripts/baseline/size_baseline_v131.json` | Immutable v1.31 freeze, BASE-01 schema | ✓ VERIFIED | Contains `deltas_vs_size_baseline`; read back live through `check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_v131.json` → exit 0, `PASS` on all 3 AVR targets |
| `.planning/phases/138-preconditions-baseline/138-06-FIRMWARE-MEASUREMENT.md` | Verbatim gate output + F-138-04/05 | ✓ VERIFIED | 391 lines (min 90), contains `F-138-04`; F-138-05's `KeyError` independently reproduced live |
| `.planning/phases/138-preconditions-baseline/138-BASELINE.md` | 9-section narrative + findings register | ✓ VERIFIED | 428 lines (min 150), contains `F-138-01`; all cited CI run ids independently re-verified via `gh run view` |
| `.planning/phases/138-preconditions-baseline/138-VALIDATION.md` | Per-task verification map, signed off | ✓ VERIFIED | Contains `nyquist_compliant: true`; all 10 map rows green |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `.planning/REQUIREMENTS.md` | `138-BRANCH-BASES.md` | Evidence citation on PREP-01/02 | ✓ WIRED | Lines 60, 70, 78 cite `138-BRANCH-BASES.md` with section anchors |
| `.planning/REQUIREMENTS.md` | `138-BASELINE.md` / `138-02-PULSE-DISTRIBUTION.md` | Evidence citation on PREP-03/04 | ✓ WIRED | Lines 82, 100 cite both artifacts with section anchors |
| `138-BRANCH-BASES.md` | git refs in both submodules | Full base SHA, re-resolvable | ✓ WIRED | `git merge-base` calls in both submodules reproduce the cited SHAs exactly |
| `138-pulse-distribution.py` | `firestarter_app/firestarter/database.py` | Imports production parser | ✓ WIRED | Script output confirms `Resolved parser module: /workspaces/firestarter_app/firestarter/database.py` |
| `test_trace_eprom_v131.cpp` | `eprom_v131_expected.h` | Relative include | ✓ WIRED | `test_consuming_suites_still_include_the_fixture` passes live |
| `platformio.ini` | `test/native/avr/test_trace_eprom_v131/` | `test_filter` + `-I` build flag | ✓ WIRED | `pio test -e native_trace_v131` builds and runs the suite successfully |
| `test_golden_trace_identity_eprom_v131.py` | `eprom_v131_trace_inventory.json` | Reads inventory, cross-checks header | ✓ WIRED | All 6 assertions pass live including cross-check assertions |
| `size_baseline_v131.json` | `check_size_baseline.py` | `--baseline` seam | ✓ WIRED | Live read-back: exit 0, PASS on all 3 targets |
| `138-BASELINE.md` | five per-plan artifacts | Filename+section citation | ✓ WIRED | `grep` confirms citations to all five: `138-02-PULSE-DISTRIBUTION.md`, `138-03-TRACE-CAPTURE.md`, `138-04-HOST-BASELINE.md`, `138-05-SUMMARY.md`, `138-06-FIRMWARE-MEASUREMENT.md` |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|---|---|---|---|---|
| `138-pulse-distribution.py` output | Histogram counts per protocol | Live parse of `firestarter_app/firestarter/data/chip_database.json` via production `_parse_pulse_duration` | Yes — re-ran independently, byte-identical output including blob SHA | ✓ FLOWING |
| `eprom_v131_expected.h` arrays | Merged strobe+timing entries | Empirical capture from real (unmodified) `eprom_write_execute` under Unity/native | Yes — 6/6 identity-gate assertions pass against the committed blob | ✓ FLOWING |
| `size_baseline_v131.json` figures | Flash/RAM/suite counts | Cold `pio run`/`pio test` invocations on the measured tree | Yes — independently rebuilt all 3 AVR targets and all 4 native envs, byte-identical figures | ✓ FLOWING |
| `138-BASELINE.md` §1 CI evidence | Run ids, conclusions | `gh run view` against live GitHub Actions API | Yes — independently re-queried all 3 run ids, identical fields returned | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| PREP-01 four-oracle adjudication reproduces | `gh pr view 44`, `git show --no-patch --format=%P 568e58b`, `git merge-base --is-ancestor`, `comm -23` of ls-tree lists | MERGED/568e58b; single parent 16a313a; exit 1; 0 lines | ✓ PASS |
| Golden-trace identity gate | `pytest tests/test_golden_trace_identity_eprom_v131.py -v` | 6 passed | ✓ PASS |
| Native suite counts (4 envs) | `pio test -e native / -e native_nodevtools / -e native_pinmap_provisional / -e native_trace_v131` | 141/17, 141/17, 10/1, 5/1 — all PASSED | ✓ PASS |
| Firmware pytest gate suite | `python3 -m pytest tests/ -q` (in `/workspaces/firestarter`) | 227 passed | ✓ PASS |
| AVR flash/RAM (3 targets) | `pio run -e uno / -e uno328pb / -e leonardo` | 23954/1573, 24004/1579, 26016/2014 | ✓ PASS |
| Host suite count | `.venv/ci-replica/bin/python -m pytest tests/ -o addopts="" -q` (in `/workspaces/firestarter_app`) | 1539 passed, 0 skipped, 201s | ✓ PASS |
| Directory-name-dependent host tests | `pytest tests/test_gen_validation_header.py::test_validate_spec_called_before_emission tests/test_sdp_bus_config_drift.py::test_bad_pinout_fails_closed_and_writes_nothing` | 2 passed | ✓ PASS |
| Pulse-distribution script (real DB) | `python3 138-pulse-distribution.py` | Exact histogram/blob-SHA match to committed artifact | ✓ PASS |
| Pulse-distribution script (planted failure) | `DB_PATH=<synthetic> python3 138-pulse-distribution.py` | `VIOLATIONS: 1`, `RESULT: FAIL` | ✓ PASS |
| Size-baseline read-back via `--baseline` seam | `check_size_baseline.py --policy merge05 --baseline size_baseline_v131.json --avr-log ...` | exit 0, PASS all 3 targets | ✓ PASS |
| F-138-05 KeyError defect (recorded, not fixed) | `check_size_baseline.py --native-log native_trace_v131=...` | `KeyError: 'native_trace_v131'`, exit 1 | ✓ PASS (confirms honest finding, not a fabricated claim) |
| Write-path fence held | `git diff 3085084..HEAD --stat` (firmware) | 8 files changed, all additive test/baseline artifacts; zero changes to `eprom.cpp`/`memory.cpp` | ✓ PASS |
| Three CI runs, read-only | `gh run view <id> --repo <repo> --json event,headBranch,headSha,conclusion,workflowName,createdAt` ×3 | All 3 match `138-BASELINE.md` §1/§2 exactly (`success`, correct branch/SHA) | ✓ PASS |

### Probe Execution

No `scripts/*/tests/probe-*.sh` convention applies to this phase — this is a documentation/measurement phase with pytest/Unity as its test runners (already covered under Behavioral Spot-Checks above). Step 7c: SKIPPED (no probe-based verification convention declared by this phase).

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| PREP-01 | 138-01 | App v1.30 branch merged/equivalent to `origin/beta`, verified | ✓ SATISFIED | Content-equivalence via F-138-01, independently re-verified (4/4 oracles reproduce) |
| PREP-02 | 138-01 | Milestone branches on verified base commits, all 3 repos | ✓ SATISFIED | All 3 bases independently re-verified by full-SHA `git merge-base` |
| PREP-03 | 138-03, 138-04, 138-05, 138-06, 138-07 | Pre-change baseline: frozen trace, per-target size, suite counts | ✓ SATISFIED | All figures independently reproduced live (trace, AVR sizes, native counts, host counts) |
| PREP-04 | 138-02, 138-07 | Live pulse-width distribution re-derived this milestone | ✓ SATISFIED | Script re-run live, output byte-identical to committed record including blob SHA |

No orphaned requirements: REQUIREMENTS.md maps only PREP-01 through PREP-04 to Phase 138 (confirmed via `grep -n "Phase 138" REQUIREMENTS.md`), and all four appear in plan `requirements:` frontmatter fields (138-01 → PREP-01/02; 138-07 → PREP-03/04), matching the phase's own documented per-plan tick-scoping.

### Anti-Patterns Found

None. Scanned all firmware files created/modified this phase (`host_stubs_common.inc`, `eprom_v131_expected.h`, `host_stubs.cpp`, `test_trace_eprom_v131.cpp`, `test_golden_trace_identity_eprom_v131.py`, `size_baseline_v131.json`, `platformio.ini`) for `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` — zero matches. Scanned all `.planning/phases/138-preconditions-baseline/*.md` artifacts — the only `TBD` string matches are self-referential ("no remaining TBD in Task ID/Plan/Wave columns"), not actual debt markers. The write-path fence (`eprom.cpp`/`memory.cpp` untouched) was independently confirmed via `git diff --stat`, ruling out the most likely way a "measurement-only" phase could quietly become a behavior-change phase.

### Human Verification Required

None. Every must-have in this phase resolves to a command whose output is independently re-checkable (git/gh/pytest/pio), and every command was actually re-run during this verification pass rather than accepted from SUMMARY.md's narration. The phase's own non-autonomous gate (138-07's operator-authorized push+dispatch) already occurred and is corroborated by three independently re-queried `gh run view` calls returning `conclusion: success`.

### Gaps Summary

No gaps. All four ROADMAP Success Criteria (as amended by the operator's dated OD-1 correction, which this verification honored per the task's explicit instruction) are independently VERIFIED against live command output, not accepted from SUMMARY.md or 138-BASELINE.md narration alone. Every committed artifact this phase's plans declared as a must-have exists, is substantive (passes min_lines/contains checks), is wired (its consumers actually read it and its identity/comparison gates pass live), and — where it renders a measured figure — that figure was independently re-derived and matches exactly. The write-path fence (`eprom.cpp`/`memory.cpp` off-limits) held: `git diff` over the full base..HEAD range on the firmware repo shows zero touches to either file, confirming the phase measured rather than changed programming behavior, as its goal requires. The 11 findings in the consolidated register (F-138-01 through F-138-11) are honest, owned, recorded-not-fixed dispositions by design (per the phase's own D-07 convention) — several were independently reproduced during this verification (F-138-01's four oracles, F-138-05's KeyError) and confirmed genuine rather than fabricated.

---

*Verified: 2026-08-09T08:30:00Z*
*Verifier: Claude (gsd-verifier)*
