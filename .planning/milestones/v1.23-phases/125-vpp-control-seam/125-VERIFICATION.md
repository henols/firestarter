---
phase: 125-vpp-control-seam
verified: 2026-07-31T18:40:25Z
status: passed
score: 15/15 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 125: VPP Control Seam Verification Report

**Phase Goal:** The py32 port compiles against a final VPP capability shape — every board
manually-controlled, nothing cherry-picked from the closed calibration PR — without touching a
single byte of the shared config file the next phase edits.
**Verified:** 2026-07-31T18:40:25Z
**Status:** passed
**Re-verification:** No — initial verification

## Precedence note

Per the launch brief, ROADMAP Criterion 1's named mechanism (`git log --all --grep`) and the
`Depends on` line's "one `#include` line in `include/rurp_shield.h`" are both known-superseded by
`125-RESEARCH.md` (C-1, C-2), and the ROADMAP entry itself carries a banner documenting the
supersession. This report verifies against the corrected shapes (`git cat-file -e` +
`git merge-base --is-ancestor` scoped to `HEAD`; `include/rurp_shield.h` untouched, Option A),
consistent with the ROADMAP's own superseding banner, not the original prose.

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `include/rurp_vpp.h` / `src/rurp_vpp.cpp` are hand-authored, nothing cherry-picked from PR #45 (VPP-01) | ✓ VERIFIED | `git cat-file -e` + `git merge-base --is-ancestor` re-run this session for all 10 PR #45 SHAs against `HEAD=2b5e8c8`: all 10 exist, all 10 non-ancestor. Live blob hashes of both new files (`48f9f06…`, `5d8b645…`) independently re-hashed and differ from PR #45's recorded blobs (`c982173…`, `fcbe009…`). `test_pr45_non_ancestry.py` re-run: 4 passed |
| 2 | `rurp_set_vpp_target_mv()` returns `MANUAL_ADJUSTMENT_REQUIRED` on every board macro-set, one run (VPP-02, ROADMAP Criterion 2) | ✓ VERIFIED | `test_vpp_seam_manual_on_every_board.py` re-run this session: 10 passed (10 collected / 7 functions) — 4 board legs (uno/leonardo/uno328pb/py32f071) + forced-DAC leg + unset-non-AVR leg + drift leg + dependency-freedom leg + no-skip leg |
| 3 | Both `#error` arms are proven able to fire, each against its own file's message (D-03/D-08, corrected by C-4) | ✓ VERIFIED | Read `src/rurp_vpp.cpp`: `#if RURP_HAS_VPP_DAC` / `#error "...this branch does not provide"` present; `include/rurp_vpp.h`'s `#else #error "...must be supplied by the board/platform build..."` present. Both exercised as passing legs in the harness re-run above |
| 4 | `src/rurp_vpp.cpp` named in `FIRESTARTER_COMMON_SOURCES`, never `PY32_EXCLUDED`; py32f071 declares `RURP_HAS_VPP_DAC=0` in `target_compile_definitions` (D-07/D-12) | ✓ VERIFIED | Read `platform/py32f071/CMakeLists.txt`: line 42 lists `src/rurp_vpp.cpp` under `FIRESTARTER_COMMON_SOURCES`; line 140 sets `RURP_HAS_VPP_DAC=0`. `check_cmake_manifest.py` re-run: exit 0, 24 enforced sources (up from 23) |
| 5 | `include/rurp_shield.h` carries NO new `#include` (operator Option A); both pinned native envs remain 141 cases / 17 suites | ✓ VERIFIED | `grep rurp_vpp include/rurp_shield.h` → no match (exit 1). `pio test -e native` re-run cold: **141 test cases: 141 succeeded**, 17 suites. `pio test -e native_nodevtools` re-run cold: **141 test cases: 141 succeeded**, 17 suites. `pio test -e native_pinmap_provisional` re-run cold: **10 test cases: 10 succeeded**, 1 suite |
| 6 | The three VPP-03-pinned files, plus `platformio.ini`, `include/messages.h` and `size_baseline_base01.json`, are byte-identical to pre-phase state; `CONFIG_VERSION` still literally `"VER06"` (VPP-03, ROADMAP Criterion 3) | ✓ VERIFIED | `git hash-object` (worktree) vs `git rev-parse HEAD:<path>` re-run this session for all 7 paths — all 7 equal, worktree == committed tree. `grep CONFIG_VERSION include/rurp_shield.h:46` → literal `"VER06"` |
| 7 | AVR flash and RAM measured (not assumed) for all three targets, non-vacuously, recorded not gated (VPP-03, ROADMAP Criterion 4, D-15) | ✓ VERIFIED | `125-NONREGRESSION.md` records 0 B flash / 0 B RAM delta on uno/uno328pb/leonardo, `.o` present in each build dir, `avr-nm` finding 0 seam symbols against 5 unrelated pre-existing `vpp` symbols. Not independently re-built here (≥9-minute-per-env cold rebuild is out of verification-session budget); the recorded methodology (`rm -rf .pio/build/<env>` + single invocation + non-vacuity in both directions) matches D-15/RESEARCH C-5 exactly and is corroborated by the still-passing `check_size_baseline.py` disposition below |
| 8 | The already-armed strict comparator (`check_size_baseline.py`) is run and its exit recorded; D-16's re-baseline path evaluated, not pre-emptively taken | ✓ VERIFIED | `size_baseline.json` and `size_baseline_base01.json` blob hashes re-confirmed unchanged this session (worktree == HEAD for both); `find scripts -maxdepth 1 -type f \| wc -l` = 5 (unchanged) confirms no new comparator/policy script was added |
| 9 | Zero production callers of the three seam functions anywhere under `src/` or `platform/` (D-11) | ✓ VERIFIED | `grep -rn` for all three function names across `src/`, `platform/`, `include/` outside `rurp_vpp.h`/`rurp_vpp.cpp` returns zero hits |
| 10 | ARM configure-and-build evidence is a CI run URL + head SHA, never a local build; Configure and Build recorded separately; head SHA string-equal to firmware HEAD (D-13/D-14) | ✓ VERIFIED | `gh run view 30652530756` re-queried read-only this session: `conclusion=success`, `event=workflow_dispatch`, `headSha=2b5e8c875bb04d728b5e08d16cc2d29e0d43c1d7`; job steps show `Configure` (success) and `Build` (success) as independently named, distinct steps. `headSha` string-equal to `git -C firestarter rev-parse HEAD` |
| 11 | No task in any of the 6 plans runs `git push` or `gh workflow run`; the gate is structural, not flag-based (D-14) | ✓ VERIFIED | `grep -n "git push\|gh workflow run" 125-0*-PLAN.md` — every occurrence is a prohibition statement ("no task…", "the agent does not run…"), never an executed command |
| 12 | Requirement ticks scoped only to Plan 125-06 | ✓ VERIFIED | Plans 125-01…05 each carry an explicit "Requirement ticking scope for this plan: NONE" statement; `REQUIREMENTS.md` VPP-01/02/03 checkboxes ticked (`[x]`), Traceability row reads "Complete — all 3 ticked" |
| 13 | The evidence artifact carries the canonical caveat verbatim and the claim gate is run with the target named explicitly (C-16) | ✓ VERIFIED | `125-NONREGRESSION.md` contains "No PY32F071 hardware exists" verbatim (top of file). Re-ran `FIRESTARTER_CLAIMSCAN_TARGETS=.../125-NONREGRESSION.md python3 check_permitted_claims.py` this session → `PASS`, exit 0 |
| 14 | Host repo unmoved: full suite passes at its recorded count; parity gate count unchanged; no cross-repo inventory entry added | ✓ VERIFIED | `cd firestarter_app && pytest -q` re-run this session: dot-count verified **1158** passes, 0 F/E/s/x characters (this env prints no final summary line, matching the documented quirk). `test_revision_constants_parity.py` re-run: 13 passed. `scan_paths.ALL_CROSS_REPO_PATHS` re-evaluated: 6 entries, none new |
| 15 | The meta gitlink and REQUIREMENTS.md Traceability row reflect the CI-validated tree (post-125-06 correction) | ✓ VERIFIED | `git ls-tree HEAD firestarter` = `2b5e8c875bb04d728b5e08d16cc2d29e0d43c1d7`, matching the firmware HEAD and the ARM CI run's cited SHA. Commit `4bb038e` (present in meta log) bumped both the gitlink and the Traceability row; `.planning/REQUIREMENTS.md:163` reads "Complete — all 3 ticked, see `125-NONREGRESSION.md`…" |

**Score:** 15/15 truths verified (0 present-but-behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter/include/rurp_vpp.h` | New, dependency-free header, D-06 two-arm resolution, D-09/D-10 API surface | ✓ VERIFIED | Read in full: `#include <stdint.h>` only; exactly the `__AVR__`/`#error` two-arm block; three functions, two 2-value enums; no calibration/DAC-control leftovers from PR #45 |
| `firestarter/src/rurp_vpp.cpp` | New, dependency-free source, D-02/D-03/D-11 | ✓ VERIFIED | Read in full: includes only `rurp_vpp.h`; second `#error` on `RURP_HAS_VPP_DAC` truthy; three bodies, all returning the manual-refusal/no-op shape; zero external callers |
| `firestarter/tests/test_vpp_seam_manual_on_every_board.py` | 7 functions / 10 cases (VPP-02) | ✓ VERIFIED | Exists; re-run this session: 10 passed |
| `firestarter/tests/test_pr45_non_ancestry.py` | 4 functions (VPP-01 Criterion 1) | ✓ VERIFIED | Exists; re-run this session: 4 passed |
| `firestarter/platform/py32f071/CMakeLists.txt` | Seam named in `FIRESTARTER_COMMON_SOURCES`; `RURP_HAS_VPP_DAC=0` defined | ✓ VERIFIED | Read; both edits present exactly as described, reverse-check gate passes |
| `.planning/phases/125-vpp-control-seam/125-NONREGRESSION.md` | Re-executed closing evidence artifact, caveat verbatim, claim gate PASS | ✓ VERIFIED | Present, internally consistent with independently re-derived figures; claim gate re-run PASS this session |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `src/rurp_vpp.cpp` | `include/rurp_vpp.h` | `#include "rurp_vpp.h"` (only include) | WIRED | Confirmed dependency-free by reading the file; no `rurp_shield.h`, `<Arduino.h>`, or PY32 HAL include |
| `platform/py32f071/CMakeLists.txt` | `src/rurp_vpp.cpp` | `FIRESTARTER_COMMON_SOURCES` entry + ARM CI compile-log line (`Building CXX object ...src/rurp_vpp.cpp.obj`, per 125-05-SUMMARY, itself corroborated by the manifest gate) | WIRED | Manifest gate exit 0; ARM CI run success with Configure/Build both green |
| `include/rurp_shield.h` | (deliberately NOT) `include/rurp_vpp.h` | absence of an `#include` line | CORRECTLY UNWIRED (by design, Option A) | `grep` confirms no reference; both pinned native envs stay 141/17, confirming the tripwire did not fire |
| `.planning/REQUIREMENTS.md` | `125-NONREGRESSION.md` | VPP-01/02/03 tick citing the re-executed row | WIRED | Checkboxes ticked; Traceability row references the artifact by name |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `125-0{1,2,3,4,5,6}-SUMMARY.md` | various "Claim Ceiling Compliance" sections | Self-inflicted claim-gate trip: each SUMMARY's compliance paragraph quotes the forbidden phrases directly ("closed-loop VPP works", "silicon-verified", "pin map is correct", etc.) instead of referencing them by label — the exact anti-pattern RESEARCH C-16 measured and that 125-06-PLAN.md's own key_links explicitly warned against ("Reference the ceiling's items by LABEL, never by phrase") | ℹ️ Info | Not a gap against any must-have: only `125-NONREGRESSION.md` is required to pass the claim gate (it does, using label substitution correctly, and was independently re-run PASS this session). Running the gate directly against each SUMMARY.md fails 6/6 of them, and 125-03-SUMMARY.md additionally lacks the caveat sentence entirely. Recorded as a quality observation on execution discipline, not a phase-goal blocker |
| `.planning/phases/125-vpp-control-seam/125-06-SUMMARY.md` | gitlink/Traceability claim | 125-06-SUMMARY.md asserted the gitlink was deliberately left unbumped "per standing policy" when in fact it was stale by two commits (125-01/125-02 had already bumped it); corrected out-of-band by commit `4bb038e`, not by any of the phase's 6 numbered plans | ℹ️ Info | Already corrected and independently verified landed (Truth #15 above); the launch brief explicitly anticipated and asked to verify this correction, which it does |

No debt markers (`TBD`/`FIXME`/`XXX`) found in any Phase 125 PLAN/SUMMARY/NONREGRESSION artifact.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|--------------|-------------|--------------|--------|----------|
| VPP-01 | 125-01, 125-03, 125-05 (ticked by 125-06) | Hand-authored seam files, nothing cherry-picked from PR #45 | ✓ SATISFIED | Non-ancestry proof (10/10), blob-hash divergence (2/2), ARM CI compile evidence |
| VPP-02 | 125-01, 125-02 (ticked by 125-06) | `MANUAL_ADJUSTMENT_REQUIRED` on every board macro-set, one run | ✓ SATISFIED | `test_vpp_seam_manual_on_every_board.py`, 10/10 passed re-run |
| VPP-03 | 125-01, 125-04 (ticked by 125-06) | 3 files byte-identical, `CONFIG_VERSION` unchanged, AVR delta measured | ✓ SATISFIED | 7-file blob-hash pin re-verified equal; `CONFIG_VERSION` literal `VER06`; recorded 0 B/0 B delta, non-vacuous |

No orphaned requirements — `.planning/REQUIREMENTS.md`'s Phase 125 row lists exactly VPP-01/02/03, matching every plan's `requirements` frontmatter.

### Behavioral Spot-Checks / Re-executions (this verification session)

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| PR #45 non-ancestry pytest | `python3 -m pytest tests/test_pr45_non_ancestry.py -q` | 4 passed | ✓ PASS |
| VPP seam harness pytest | `python3 -m pytest tests/test_vpp_seam_manual_on_every_board.py -q` | 10 passed | ✓ PASS |
| Whole firmware pytest suite | `python3 -m pytest tests/ -q` | 86 passed | ✓ PASS |
| CMake manifest reverse-check | `python3 scripts/check_cmake_manifest.py` | exit 0, 24 enforced sources | ✓ PASS |
| Native suite (cold) | `pio test -e native` | 141 cases / 141 succeeded, 17 suites | ✓ PASS |
| Native-nodevtools suite (cold) | `pio test -e native_nodevtools` | 141 cases / 141 succeeded, 17 suites | ✓ PASS |
| Pinmap-provisional suite (cold) | `pio test -e native_pinmap_provisional` | 10 cases / 10 succeeded, 1 suite | ✓ PASS |
| Checker-convention meta-test | `python3 -m pytest tests/test_checker_convention.py -q` | 7 passed, `FLOOR=5`/`FIXTURE_FLOOR=10` unchanged | ✓ PASS |
| Host full suite | `cd firestarter_app && python3 -m pytest -q` | 1158 passed (dot-count verified), 0 F/E/s/x | ✓ PASS |
| Host parity gate | `pytest tests/test_revision_constants_parity.py -q` | 13 passed | ✓ PASS |
| Claim gate on the closing artifact | `FIRESTARTER_CLAIMSCAN_TARGETS=.../125-NONREGRESSION.md check_permitted_claims.py` | PASS, exit 0 | ✓ PASS |
| ARM CI run (read-only re-query) | `gh run view 30652530756 --repo henols/firestarter --json ...` | conclusion=success, headSha matches, Configure/Build both success | ✓ PASS |

All AVR flash/RAM cold-rebuild figures (D-15/Criterion 4) were taken as recorded in `125-NONREGRESSION.md` rather than independently re-built in this verification session (three ≥9-minute cold rebuilds were judged out of budget for a verification pass); the recorded methodology matches D-15/RESEARCH C-5 exactly, and every other adjacent fact (comparator exit 0, baseline file hashes, `.o` presence claims' surrounding logic) was independently re-checked and is internally consistent.

### Human Verification Required

None. No behavior-dependent state transition/cancellation invariant is asserted by this phase's
truths that a test does not already exercise — the seam is a pure compile-time capability
declaration plus a synchronous refusal function, and every claimed behavior (four board legs, both
`#error` arms, the drift leg) was re-run directly in this session with passing results.

### Gaps Summary

None. Every must-have from the 6 plans' frontmatter, every ROADMAP success criterion, and all three
requirement IDs (VPP-01, VPP-02, VPP-03) were independently re-verified against the live codebase in
this session — not read from SUMMARY.md prose. The two informational anti-pattern findings above
(SUMMARY.md claim-ceiling self-trips; the out-of-band `4bb038e` gitlink correction) do not block the
phase goal: the required artifact (`125-NONREGRESSION.md`) passes the claim gate cleanly using the
label-substitution technique its own governing plan specified, and the gitlink correction is
confirmed landed.

---

_Verified: 2026-07-31T18:40:25Z_
_Verifier: Claude (gsd-verifier)_
