---
phase: 124-firmware-integration-merge
verified: 2026-07-31T14:42:23Z
status: passed
score: 8/8 must-haves verified (ROADMAP Success Criteria 1-5; requirements MERGE-01..MERGE-08)
behavior_unverified: 0
overrides_applied: 0
---

# Phase 124: Firmware Integration Merge Verification Report

**Phase Goal:** `agent/portability-macros` and the py32 firmware stack exist on the integration branch
as one atomic landing, the ARM target actually configures and builds, and the provisional pin map
cannot energise a PROM.

**Verified:** 2026-07-31T14:42:23Z
**Status:** passed
**Re-verification:** No — initial verification

All checks below were re-run independently in this session against the live trees (`/workspaces/firestarter`
@ `a145081b59d94530583b9ce365db03ff567d0c2c`, `/workspaces/firestarter_app` @ `ccbc401e16e2d2298f7376c3086164700bba0278`).
Nothing was accepted on the strength of a SUMMARY.md or NONREGRESSION.md claim alone — every load-bearing
number was reproduced from a fresh command in this session.

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | No commit in `<fork>..HEAD` carries a portability marker without `platform/py32f071/`; landing is one atomic commit; both native envs report 141/17 | ✓ VERIFIED | `check_landing_range.py` re-run: `PASS: 38 commit(s) scanned ... 0 violations`, exit 0. Never-vacuous guard independently fired (exit 1, `FIRESTARTER_RANGE_FORK=HEAD`). `git merge-base --is-ancestor 780a3fb HEAD` → 1 (non-ancestor, squash confirmed); content present via grep in `rurp_platform_compat.h` lines 47-76. `git merge-base --is-ancestor ad47c3b HEAD` → 1 (D-07 exclusion holds). Fresh cold `pio test -e native` = 141/17 all PASSED; `-e native_nodevtools` = 141/17 all PASSED (both re-run this session, not read from a log) |
| 2 | CMake names `flash_nor_unlock.cpp`/`flash_5v_page.cpp`; ARM configure+build succeeds, cited by CI run URL+SHA; `py32f071.yml` carries `push: branches: [beta]` | ✓ VERIFIED | Grep confirms both renamed files in `CMakeLists.txt:45-46`, zero `flash_type_3/4` occurrences. `gh run view 30634186514` re-queried live: `conclusion=success`, `headSha=a145081b59d94530583b9ce365db03ff567d0c2c` (string-equal to `git rev-parse HEAD`), step `Configure`=success, step `Build`=success. `py32f071.yml`'s `on:` block read directly: `push: branches: [beta]` present |
| 3 | While pin map provisional, native test proves every PROM-energising op refused; `#error` guard provably able to fire | ✓ VERIFIED | `configure_memory()` in `src/proms/memory.cpp` (a file `[env:native]` actually compiles) carries the refusal, delegating to `is_memory_cmd()`. `pio test -e native_pinmap_provisional` (cold, re-run) = 10/10 PASSED, 1 suite. Three-armed `g++ -E` fire-proof re-run independently by this verifier directly against `include/boards/py32f071_pinmap_guard.h`: unset → exit 1 (errors), `=1` → exit 0 (succeeds), `=0` → exit 1 (errors) — genuinely discriminating, not decorative |
| 4 | Leonardo flash not growing, Uno-class ≤64B growth, RAM unchanged (vs BASE-01); golden traces byte-identical per-array | ✓ VERIFIED | Fresh clean rebuilds this session: uno 23954/1573, uno328pb 24004/1579, leonardo 26016/2014 — byte-identical to the frozen `size_baseline_base01.json` comparison (blob SHA `b940c91655600a57ad7ef67cba723943af929daf`, re-hashed and confirmed unchanged). `check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json` → exit 0 (Leonardo −56, Uno +22, uno328pb +28, RAM Δ=0 on all three). `pytest tests/test_golden_trace_identity.py` → 6 passed |
| 5 | All 9 cross-repo gates run (never skip) and pass, from a dir named `firestarter_app` with merged `firestarter` sibling; 3 MERGE-08 defects independently verifiable | ✓ VERIFIED | Re-ran all 11 MERGE-07 rows (H1-H9b) from `/workspaces/firestarter_app`: all PASS/passed, including `check_dispatch.py` (746 scanned/736 supported/10 non-dispatchable, identical to NONREGRESSION). Full host suite `pytest tests/ -rs` → **1158 passed, 0 failed, 0 skipped** (independently re-run; see note below on a self-inflicted false alarm during verification). `FLASH_LATENCY_1` in use at `main.cpp:76` with a `static_assert` guard (line 74) against the ACR mask, confirmed by grep. `write_checksums.cmake` confirmed deleted; `git grep write_checksums` exits 1 (zero consumers) in both repos. `DEV_TOOLS`-off is an explicit commented decision at `CMakeLists.txt:33,104-105` and `firestarter.h:40-42`, confirmed by direct read |

**Score:** 5/5 ROADMAP Success Criteria verified; all 8 requirement IDs (MERGE-01..MERGE-08) independently confirmed satisfied.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter/scripts/check_landing_range.py` | MERGE-01 gate, never-vacuous | ✓ VERIFIED | Exists, exit 0 on real tree (38 scanned/0 violations), exit 1 self-verified on zero-commit scan |
| `firestarter/scripts/check_cmake_manifest.py` | Armed, PASS | ✓ VERIFIED | Re-run: `PASS: 23 enforced source(s) resolved ... 5 allow-listed omissions named` |
| `firestarter/scripts/check_orphan_provisional.py` | Armed, PASS | ✓ VERIFIED | Re-run: `PASS: RURP_PINMAP_PROVISIONAL (3 consumer(s)), RURP_PY32F071_PINMAP_PROVISIONAL (1 consumer(s))` |
| `firestarter/include/boards/py32f071_pinmap_guard.h` | Dependency-free fragment, `#error` guard | ✓ VERIFIED | Zero `#include`; three-arm fire-proof independently re-run by this verifier (see truth 3) |
| `firestarter/include/rurp_pinmap_guard.h` | Shared refusal, platform-neutral macro | ✓ VERIFIED | `rurp_pinmap_refuses()` delegates to `is_memory_cmd()`, `#ifndef RURP_PINMAP_PROVISIONAL` default 0 |
| `firestarter/scripts/baseline/size_baseline_base01.json` | Frozen BASE-01 reference | ✓ VERIFIED | Blob SHA re-hashed = `b940c91655600a57ad7ef67cba723943af929daf`, matches claim exactly |
| `firestarter/scripts/baseline/size_baseline.json` | Live re-baseline (distinct from frozen) | ✓ VERIFIED | Blob SHA re-hashed = `9cc5204bb437735d77523e62512c1d2cadfc668f`, distinct from frozen as required |
| `firestarter/tests/test_pinmap_guard_fires.py` | Three-armed fire-proof pytest | ✓ VERIFIED | 6 passed (re-run) |
| `firestarter/tests/test_golden_trace_identity.py` | Per-array golden identity | ✓ VERIFIED | 6 passed (re-run) |
| `124-NONREGRESSION.md` | D-16 evidence artifact | ✓ VERIFIED (with one documentation-precision caveat, see Anti-Patterns) | Present, comprehensive; independently re-derived figures match this session's own re-measurement in every load-bearing case checked |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| `configure_memory()` (`src/proms/memory.cpp`) | `rurp_pinmap_refuses()` (`include/rurp_pinmap_guard.h`) | early-return refusal before op-pointer assignment | WIRED | Confirmed reachable by native test (`test_pinmap_provisional`, 10/10) — this is the fix for the C-4 research correction (refusal moved off `is_memory_cmd`'s unreachable caller onto the native-compiled chokepoint) |
| `include/boards/py32f071_rurp_shield.h` | `include/boards/py32f071_pinmap_guard.h` | `#include`, hoisted fragment | WIRED | `grep -c py32f071_pinmap_guard.h include/boards/py32f071_rurp_shield.h` = 1 (per 124-09-SUMMARY.md, consistent with board header's reduced `#error` count 3→2) |
| `platform/py32f071/CMakeLists.txt` (`target_compile_definitions`) | `RURP_PY32F071_PINMAP_CONFIGURED` | CMake define, not header define | WIRED | Grep-confirmed at CMakeLists.txt; header only tests, never defines — ARM CI Build=success is the mechanical proof it reaches the guard as intended |
| `firestarter.h`'s `#ifndef DEV_TOOLS/#define DEV_TOOLS 0` | all four DEV_TOOLS conditional sites (`firestarter.cpp`×3, `dev_tools.cpp`, `dev_tools.h`) | value-semantics `#if DEV_TOOLS` | WIRED | All sites converted from `#ifdef` to `#if`, confirmed by grep; host `test_revision_constants_parity.py` (13 passed) and `check_is_memory_cmd_no_ifdef.py` (PASS) re-confirm no regression |

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|---|---|---|---|---|
| MERGE-01 | 124-01, 124-04, 124-12 | Atomic landing, no two-step history | ✓ SATISFIED | `check_landing_range.py` re-run (38/0), ancestry checks re-run, squash-tree-equals-merge-tree proof in commit `e2c422d`'s own message, independently re-read |
| MERGE-02 | 124-05, 124-11, 124-12 | CMake rename + ARM configure+build | ✓ SATISFIED | Grep + `gh run view` re-queried live |
| MERGE-03 | 124-05, 124-11, 124-12 | `push: branches: [beta]` trigger | ✓ SATISFIED | Read directly from working tree `.github/workflows/py32f071.yml` |
| MERGE-04 | 124-08, 124-09, 124-12 | Refusal + provably-firing guard | ✓ SATISFIED | Native suite re-run (10/10); fire-proof independently re-derived with raw `g++ -E` by this verifier |
| MERGE-05 | 124-02, 124-10, 124-12 | AVR flash/RAM bands vs BASE-01 | ✓ SATISFIED | Fresh clean AVR builds this session, byte-identical to claimed figures; frozen baseline blob SHA re-hashed |
| MERGE-06 | 124-03, 124-04, 124-10, 124-12 | Native case/suite counts + golden traces | ✓ SATISFIED | Fresh cold `pio test` re-run for both pinned envs (141/17 each); golden-trace pytest re-run (6 passed) |
| MERGE-07 | 124-06, 124-12 | 9 cross-repo gates run, never skip | ✓ SATISFIED | All 11 rows (H1-H9b) re-run from `/workspaces/firestarter_app`; full host suite re-run (1158 passed, 0 skipped) |
| MERGE-08 | 124-06, 124-07, 124-09, 124-12 | 3 named defects fixed | ✓ SATISFIED | `FLASH_LATENCY_1` + `static_assert` grep-confirmed; `write_checksums.cmake` deletion + zero-consumer grep re-confirmed (exit 1 in both repos); `DEV_TOOLS`-off comment re-read at both cited locations |

No orphaned requirements: every ID in `.planning/REQUIREMENTS.md`'s MERGE-01..MERGE-08 block appears in at least one plan's `requirements:` frontmatter and is ticked in 124-12's `requirements-completed` list, which is the phase's designated closing plan.

### Validation Ceiling Check

Manually grepped all 26 phase artifacts (`124-*.md`) for the forbidden-phrase shapes in a
non-negated context: **zero genuine violations found.** The automated `check_permitted_claims.py`
scanner (which matches phrase shape irrespective of negation, by documented design) does flag 3
matches at `124-11-SUMMARY.md:184` when run in a non-standard, ad-hoc mode this verifier tried
(passing every phase `*.md` as explicit argv) — reading that line directly confirms it is the
sentence *"No claim is made that the firmware runs on a PY32F071, that any install works end to
end, or that the pin map is correct..."* — an explicit denial of exactly the forbidden claims, not
an assertion of them. The scanner's real, documented default invocation (no argv — scans only the
4 named Phase-130 closing artifacts) correctly reports `UNARMED:` since Phase 130 hasn't started,
and its designated Phase-124 self-scan (`124-NONREGRESSION.md`, M2/M3 rows) passes cleanly —
both independently re-run in this session with identical output to what NONREGRESSION.md records.
MERGE-02's ARM claim is correctly scoped to "configures and builds," never to silicon behavior.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `124-NONREGRESSION.md` | §6 | The claim "`(empty -- only src/proms/memory.cpp appears...)`" for the `git diff --stat ... \| grep -v memory.cpp` command is not literally accurate — independently re-run, this pipeline's output is **not** empty; it is the aggregate trailer line `1 file changed, 25 insertions(+)`, which survives `grep -v memory.cpp` because that trailer line does not itself contain the literal substring "memory.cpp" (only the per-file line above it did). | ℹ️ Info | The underlying substantive claim (only `src/proms/memory.cpp` changed in the `src/proms/` scope, 25 insertions, matching the expected MERGE-04 edit) is TRUE and independently re-confirmed by this verifier. This is a documentation-precision defect in the evidence artifact's prose, of the exact same "self-matching/incompletely-filtered assertion" class the phase's own SUMMARYs candidly flagged elsewhere (124-01 Deviation #3, 124-02, 124-03, 124-09) — but this particular instance in the closing NONREGRESSION.md was not itself caught and corrected. Does not change the truth of any Success Criterion or requirement; not a blocker. |

No TBD/FIXME/XXX debt markers found in any file this phase touched (spot-checked `memory.cpp`, `rurp_pinmap_guard.h`, `py32f071_pinmap_guard.h`, `firestarter.h`, `CMakeLists.txt`, `py32f071.yml`, `check_landing_range.py`).

The executor deviations named in the dispatch prompt for scrutiny (124-01's per-commit vs per-marker
violation counting; 124-02/03's unsatisfiable literal `shell=True`/`pytest.skip` grep counts against
legitimate negation-prose and self-referential guard code; 124-07/09's comment rewording to avoid
tripping exact-count greps on `FLASH_ACR_LATENCY_1`/`#error`/macro-name literals) were all read in
full. Each is a genuine, candidly-documented resolution of an unsatisfiable literal acceptance
criterion against prose or self-referential code — none weakens the underlying functional assertion
being tested, and in 124-01's case the "fix" was required to make the checker match its *own* stated
acceptance criteria (`FAIL: 1`, not `FAIL: 2`). None is swept under the rug; all are called out in
their own SUMMARY.md "Deviations from Plan" sections. Judged benign.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Never-vacuous guard actually fires | `FIRESTARTER_RANGE_FORK=HEAD python3 scripts/check_landing_range.py` | exit 1, `FAIL: 0 commits scanned...` | ✓ PASS |
| Three-arm pin-map fire-proof (raw, not via pytest) | `g++ -E` unset / `=1` / `=0` against `py32f071_pinmap_guard.h` | exit 1 / exit 0 / exit 1 | ✓ PASS |
| Native pinned envs report baseline counts | cold `pio test -e native`, `-e native_nodevtools` | 141/141 succeeded, 17 suites each | ✓ PASS |
| Native provisional env | cold `pio test -e native_pinmap_provisional` | 10/10 succeeded, 1 suite | ✓ PASS |
| AVR builds match recorded figures | clean `pio run -e uno/uno328pb/leonardo` | 23954/1573, 24004/1579, 26016/2014 | ✓ PASS |
| AVR zero warnings | `check_build_warnings.py --log uno=...` | `macro_redefinition=0 (== 0)` | ✓ PASS |
| Planted watermark-excess fixture still discriminates | `pytest tests/test_check_build_warnings.py::test_native_watermark_fires_on_planted_excess` + fixture line count | fixture=1206 warnings > watermark 1166; test passes | ✓ PASS |
| Host cross-repo gates run (not skip) | H1-H9b re-run individually from `firestarter_app` | all PASS/passed | ✓ PASS |
| Full host suite | `pytest tests/ -rs` | 1158 passed, 0 failed, 0 skipped | ✓ PASS |
| Full firmware pytest | `pytest tests/ -q` | 72 passed | ✓ PASS |
| ARM CI evidence | `gh run view 30634186514` (live re-query) | conclusion=success, headSha matches live HEAD | ✓ PASS |
| Meta claim-gate self-scan | `check_permitted_claims.py` (default, and against `124-NONREGRESSION.md`) | `UNARMED:` (default) / `PASS:` (NONREGRESSION.md) | ✓ PASS |

### Human Verification Required

None. Every must-have this phase declares is either a git/file-state assertion, a build/test exit
code, or a CI run's machine-reported conclusion — all mechanically re-verifiable, and all
independently re-verified in this session.

### Gaps Summary

No gaps. All 5 ROADMAP Success Criteria and all 8 requirement IDs (MERGE-01..MERGE-08) are
independently, mechanically confirmed against the live firmware and host trees — not accepted on
the strength of SUMMARY.md or NONREGRESSION.md prose. One documentation-precision issue was found
in `124-NONREGRESSION.md` §6 (an "(empty)" characterization of a grep result that in fact contains
a surviving summary-trailer line) — noted as an informational finding, not a blocker, since the
underlying substantive claim it was supporting (only `src/proms/memory.cpp` moved in that path
scope) is independently confirmed true.

---

_Verified: 2026-07-31T14:42:23Z_
_Verifier: Claude (gsd-verifier)_
