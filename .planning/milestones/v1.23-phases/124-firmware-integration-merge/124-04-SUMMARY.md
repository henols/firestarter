---
phase: 124-firmware-integration-merge
plan: 04
subsystem: firmware-ci
tags: [firestarter, git, merge, squash, cmake, py32f071, pio, native-test, size-baseline]

# Dependency graph
requires:
  - phase: 124-firmware-integration-merge
    plan: "01"
    provides: "scripts/check_landing_range.py -- the Criterion-1 landing-shape gate this plan runs against the real landing, in a scratch clone first and then on the real HEAD."
  - phase: 124-firmware-integration-merge
    plan: "02"
    provides: "scripts/check_size_baseline.py --policy merge05 + the frozen scripts/baseline/size_baseline_base01.json this plan judges the landed tree's AVR flash/RAM deltas against."
  - phase: 124-firmware-integration-merge
    plan: "03"
    provides: "tests/test_golden_trace_identity.py + tests/golden/sdp_expected_inventory.json -- the per-array golden-trace pin this plan re-runs post-landing."
provides:
  - "The PY32F071 port landed on v1.23-py32f071-integration as one squashed commit (e2c422d), tree-proven equal to a true merge's tree, with zero Criterion-1 violations over the full fork..HEAD range"
  - "The recorded post-landing measurement set every later Phase 124 plan (05-12) is judged against: AVR flash/RAM for uno/uno328pb/leonardo, native case/suite counts + cold/warm warning counts for native and native_nodevtools, and the five gates that go red for named, pre-declared, owned reasons"
affects: [124-05, 124-06, 124-07, 124-08, 124-09, 124-10, 124-11, 124-12, 124-close]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Scratch clone (git clone --shared --no-checkout, then a local fetch of the source repo's own refs/remotes/origin/* refspecs) as the throwaway venue for proving a squash-vs-true-merge tree equality without ever running --no-ff on the real branch"
    - "Two throwaway branches (squash + true-merge) built from the identical starting point in the scratch clone, compared by git rev-parse BRANCH^{tree}, then discarded -- the real landing repeats only the squash half"
    - "Native pio test cold/warm pairing requires a single uninterrupted invocation after rm -rf .pio/build/<env>; a 2-minute default Bash timeout truncates the cold ARM/host toolchain build mid-compile and silently contaminates the next 'cold' measurement with partial cache -- must raise the timeout explicitly for this one command class"

key-files:
  created: []
  modified:
    - firestarter/.github/workflows/py32f071.yml
    - firestarter/include/avr/pgmspace.h
    - firestarter/include/boards/py32f071_rurp_shield.h
    - firestarter/include/rurp_platform.h
    - firestarter/include/rurp_platform_compat.h
    - firestarter/include/rurp_serial_utils.h
    - firestarter/include/rurp_shield.h
    - firestarter/platform/py32f071/ (15 files, all newly added by the squash)

key-decisions:
  - "The squash commit message records tip SHAs + 780a3fb by content, not the full 52-commit shortlog (the plan's own recorded discretion choice)."
  - "Task 1's and Task 3's acceptance-criteria literal integers ('14 ahead / 0 behind', 'origin/beta..HEAD is 15') were stale by execute time: three wave-1 plans (124-01/02/03) added 7 commits to the branch after RESEARCH's session-time measurement, so the real pre-landing count was 21 ahead (not 14) and the real post-landing count is 22 (not 15). The load-bearing invariant those criteria exist to protect -- 'HEAD..origin/beta stays 0' and 'exactly one new commit lands' -- held exactly; only the absolute integers drifted, which is precisely what the plan's own critical_execution_constraint #1 (re-compute, do not transcribe) predicts and licenses. Reported as a finding, not silently reconciled."
  - "A genuinely cold pio test -e native / native_nodevtools run exceeds the default 2-minute Bash tool timeout and gets SIGTERM-killed mid-compile; because .pio/build/<env> is a persistent build cache across separate Bash invocations, a second (default-timeout) invocation after a truncated first one reuses the partially-compiled objects and reports an artificially low warning count that is NOT a true cold measurement. Fixed by re-running rm -rf .pio/build/<env> immediately before a single Bash call carrying an explicit extended timeout (540000ms), so the entire cold build+link+test cycle completes in one uninterrupted invocation."

requirements-completed: [MERGE-01, MERGE-05, MERGE-06]

coverage:
  - id: D1
    description: "agent/portability-macros + agent/py32f071-toolchain land on v1.23-py32f071-integration as one squashed commit (e2c422d), its tree proven byte-identical to a true git merge --no-ff's tree via two throwaway branches built in a scratch clone, and check_landing_range.py exits 0 with 0 violations over the full fork..HEAD range on the real post-landing HEAD"
    requirement: "MERGE-01"
    verification:
      - kind: unit
        ref: "scripts/check_landing_range.py invoked as a real subprocess against the real post-landing HEAD -- PASS: 22 commit(s) scanned in 5c9160a3..HEAD, 1 carrying a portability marker, 0 violations"
        status: pass
      - kind: manual_procedural
        ref: "scratch clone tree-equality proof: squash branch tree == true-merge branch tree == 9bacc2cf111353461f2614b425646995e3898207; true-merge throwaway branch independently fires exactly the 5 RESEARCH-predicted violating SHAs (52d6c1f, adb133a, b253092, c0c6695, 532997c) under the same checker"
        status: pass
    human_judgment: false
  - id: D2
    description: "780a3fb's four program-memory helper macros (pgm_read_ptr, strncpy_P, strncmp_P, sprintf_P) are present by content in include/rurp_platform_compat.h at HEAD, while 780a3fb itself and ad47c3b are both proven non-ancestors of HEAD (squash, not merge; D-07 exclusion held)"
    requirement: "MERGE-01"
    verification:
      - kind: unit
        ref: "git merge-base --is-ancestor 780a3fb HEAD -- exit 1 (non-ancestor, as a squash requires); grep -nE for the four identifiers in include/rurp_platform_compat.h -- all four present"
        status: pass
      - kind: unit
        ref: "git merge-base --is-ancestor ad47c3b HEAD -- exit 1 (D-07 exclusion confirmed post-landing)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Both native envs (native, native_nodevtools) report exactly 141 cases / 17 suites, all PASSED, on the landed tree; check_size_baseline.py --native-log exits 0 for both"
    requirement: "MERGE-06"
    verification:
      - kind: automated_ui
        ref: "pio test -e native -- 141 test cases: 141 succeeded, 17 suite rows in the SUMMARY table"
        status: pass
      - kind: automated_ui
        ref: "pio test -e native_nodevtools -- 141 test cases: 141 succeeded, 17 suite rows"
        status: pass
      - kind: unit
        ref: "scripts/check_size_baseline.py --native-log native=... --native-log native_nodevtools=... -- PASS: native(cases=141,suites=17), native_nodevtools(cases=141,suites=17)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Golden-trace per-array pin (Plan 124-03) still passes unchanged on the landed tree -- the 22-path merge surface did not touch test/native/avr/_shared/sdp_expected.h"
    requirement: "MERGE-06"
    verification:
      - kind: unit
        ref: "pytest tests/test_golden_trace_identity.py -q -- 6 passed, 0 failed"
        status: pass
    human_judgment: false
  - id: D5
    description: "AVR flash/RAM on all three targets sit inside MERGE-05's band (Leonardo no-growth, Uno-class <=64B, RAM unchanged) against the frozen BASE-01, asserted by exit code; the six raw figures match RESEARCH's measured deltas exactly (Leonardo -56, Uno +22, uno328pb +28, RAM unchanged on all three)"
    requirement: "MERGE-05"
    verification:
      - kind: unit
        ref: "scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json --avr-log uno=... --avr-log uno328pb=... --avr-log leonardo=... -- PASS: uno(flash=23954/32256[+22<=64],ram=1573/2048[=]), uno328pb(flash=24004/32384[+28<=64],ram=1579/2048[=]), leonardo(flash=26016/28672[-56<=0],ram=2014/2560[=])"
        status: pass
    human_judgment: false
  - id: D6
    description: "Every gate expected to go red on this landing (W-1..W-5) does so for the pre-declared reason, with the exact predicted shape, and none was repaired in this plan"
    verification:
      - kind: unit
        ref: "check_size_baseline.py default mode (no --policy) on all three AVR logs -- FAIL: uno +22, uno328pb +28, leonardo -56, all diverging from BASE-01 strict equality (W-1, owner 124-10)"
        status: pass
      - kind: unit
        ref: "check_build_warnings.py --log on native + native_nodevtools warm logs -- FAIL: macro_redefinition observed=998 exceeds recorded=360 (both envs) (W-2, owner 124-10)"
        status: pass
      - kind: unit
        ref: "check_cmake_manifest.py -- FAIL: 9 violation(s), including the flash_type_3/4.cpp rename pair (W-4, owner 124-05)"
        status: pass
      - kind: unit
        ref: "check_orphan_provisional.py -- FAIL: 1 violation(s): RURP_PY32F071_PINMAP_PROVISIONAL zero consumers (W-5, owner 124-08)"
        status: pass
      - kind: unit
        ref: "pytest tests/ -q -- 2 failed, 64 passed: test_check_cmake_manifest.py::test_unarmed_on_the_real_tree_with_no_seam_override and test_check_orphan_provisional.py::test_unarmed_on_the_real_tree_with_no_seam_override (W-3, owners 124-05 and 124-08)"
        status: pass
    human_judgment: false

duration: ~20min
completed: 2026-07-31
status: complete
---

# Phase 124 Plan 04: THE LANDING Summary

**Squashed `agent/portability-macros` + `agent/py32f071-toolchain` onto `v1.23-py32f071-integration` as one commit (`e2c422d`), tree-proven byte-identical to a true merge, then measured the landed tree: all three AVR targets and both native envs match RESEARCH's predicted figures exactly, MERGE-05/MERGE-06 both pass by exit code, and all five expected-red gates fired for their pre-declared, pre-owned reasons.**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-07-31T08:36:13Z (STATE.md `last_updated` at hand-off from Plan 03)
- **Completed:** 2026-07-31T08:57:54Z
- **Tasks:** 3 completed
- **Files modified:** 22 (20 added, 2 modified) by the landing commit; 0 by Tasks 1 and 3 (scratch-clone and measurement only)

## Accomplishments

- **Task 1 (re-verification):** Rebuilt both a squash and a true-merge landing on throwaway branches inside a scratch clone (`git clone --shared --no-checkout`, then a local fetch of the real repo's own `refs/remotes/origin/*` refs since the shared clone does not carry them by default). Proved `git rev-parse BRANCH^{tree}` is identical for both (`9bacc2cf111353461f2614b425646995e3898207`), and that `check_landing_range.py` discriminates them exactly as RESEARCH predicted: 0 violations on the squash branch, exactly 5 on the true-merge branch, naming the identical five SHAs RESEARCH recorded (`52d6c1f`, `adb133a`, `b253092`, `c0c6695`, `532997c`). Confirmed the 22-path merge surface (20 added, 2 modified: `include/rurp_serial_utils.h`, `include/rurp_shield.h`) and re-derived `780a3fb`'s four contributed identifiers (`pgm_read_ptr`, `strncpy_P`, `strncmp_P`, `sprintf_P`) directly from `git show 780a3fb -- include/rurp_platform_compat.h`.
- **Task 2 (the real landing):** `git merge --squash origin/agent/py32f071-toolchain` + one `git commit` on the real `v1.23-py32f071-integration` branch, producing `e2c422d`, whose tree (`9bacc2cf111353461f2614b425646995e3898207`) matches the scratch clone's proof exactly. The commit message records both tip SHAs, the merge-base, the 22-path surface, the tree-equality claim, `780a3fb`'s content-inclusion (naming its four identifiers), the squash-not-merge rationale (citing the 5-violation count), and the explicit D-07 statement that `ad47c3b`/`feature/py32f071-release-assets` is deliberately not landed. `check_landing_range.py` on the real post-landing HEAD: `PASS: 22 commit(s) scanned ... 0 violations`.
- **Task 3 (measurement):** Clean AVR builds for uno/uno328pb/leonardo; cold+warm `pio test` for both native envs (requiring an explicit extended Bash timeout to avoid a build-cache-contamination trap discovered mid-task, see Deviations); all size-baseline, build-warning, cmake-manifest, orphan-provisional, and pytest gates run and recorded, including the four planned-red gates plus the two planned-red pytest node IDs.

## Observed Verification Values

### Task 1 — scratch-clone re-verification
- `git rev-parse --abbrev-ref HEAD` (real repo, before landing): `v1.23-py32f071-integration`; `git status --porcelain`: empty.
- `git rev-list --count HEAD..origin/beta`: **0**. `git rev-list --count origin/beta..HEAD`: **21** (not RESEARCH's session-time 14 — see Decisions: three wave-1 plans added 7 commits since RESEARCH ran; the load-bearing `0` held).
- `git merge-base --is-ancestor origin/agent/portability-macros origin/agent/py32f071-toolchain`: exit 0.
- `git merge-base --is-ancestor 780a3fb origin/agent/py32f071-toolchain`: exit 0. `git rev-parse origin/agent/py32f071-toolchain`: `e5abb5146b6c452c4847ec1a8eb240c16e100613` (unchanged from the orchestrator-supplied value).
- Squash-branch tree SHA == true-merge-branch tree SHA: **`9bacc2cf111353461f2614b425646995e3898207`** (both, string-equal).
- Criterion-1 gate on squash branch: `PASS: 22 commit(s) scanned in 5c9160a34b665878b05403ab014b959926feb6bf..HEAD, 1 carrying a portability marker, 0 violations` (exit 0).
- Criterion-1 gate on true-merge branch: `FAIL: 5 violation(s) ... 52d6c1f20fa59bca619388c25b0ab79ffbc6b1e4, adb133a211be7d0b5f2a901e2156d7acd9cc3622, b25309260fc28a60b131d8064f0a6e7bc1655ebe, c0c66959bf526e345b060ea76e24e016aaacb0ed, 532997cd215c9e769af0afa41b3c0f282b58d324` (exit 1) — matches RESEARCH's five SHAs exactly.
- Merge surface: `git diff --name-status <merge-base a1953c2>..origin/agent/py32f071-toolchain` — exactly 22 paths, 20 `A`, 2 `M` (`include/rurp_serial_utils.h`, `include/rurp_shield.h`).
- `git rev-parse origin/feature/py32f071-release-assets`: `ad47c3baca1bf229f15c1dfc5dd259931357a110`; confirmed not merged (see Task 2).
- `780a3fb`'s contributed identifiers, derived from `git show 780a3fb -- include/rurp_platform_compat.h`: `pgm_read_ptr`, `strncpy_P`, `strncmp_P`, `sprintf_P` (each a new `#ifndef .../#define ...` guard).

### Task 2 — the landing commit
- Landing commit: **`e2c422d35c3363d695cc4cc8425e575b670a948e`** (short `e2c422d`).
- `git rev-parse HEAD^{tree}`: `9bacc2cf111353461f2614b425646995e3898207` — equal to both Task 1 tree SHAs.
- `git status --porcelain` staged-file count before commit: exactly 22 (20 `A`, 2 `M`), matching Task 1's scratch dry-run exactly.
- `python3 scripts/check_landing_range.py` (post-landing, real HEAD): `PASS: 22 commit(s) scanned in 5c9160a34b665878b05403ab014b959926feb6bf..HEAD, 1 carrying a portability marker, 0 violations` (exit 0).
- `git merge-base --is-ancestor 780a3fb HEAD`: exit **1** (non-ancestor — squash, not merge). All four identifiers confirmed present in `include/rurp_platform_compat.h` at HEAD (lines 47-48, 59-60, 71-72, 75-76).
- `git merge-base --is-ancestor ad47c3b HEAD`: exit **1** (D-07 held).
- `git rev-list --count origin/beta..HEAD`: **22** (not the plan's stated "15" — same stale-arithmetic cause as Task 1's "14"; see Decisions).
- All four required artifact files present (`platform/py32f071/CMakeLists.txt`, `include/rurp_platform_compat.h`, `include/avr/pgmspace.h`, `.github/workflows/py32f071.yml`).
- `git status --porcelain`: empty after commit.

### Task 3 — post-landing measurements
- **AVR flash/RAM** (clean builds, one env at a time):

  | Env | Flash used | RAM used | RESEARCH-predicted | Match |
  |---|---|---|---|---|
  | uno | 23954 / 32256 | 1573 / 2048 | 23954 / 1573 | exact |
  | uno328pb | 24004 / 32384 | 1579 / 2048 | 24004 / 1579 | exact |
  | leonardo | 26016 / 28672 | 2014 / 2560 | 26016 / 2014 | exact |

- **Native counts** (cold, single uninterrupted `pio test` invocation after `rm -rf .pio/build/<env>`, extended Bash timeout):

  | Env | Cases | Suites | All PASSED | Cold total warnings | Cold macro-redef warnings |
  |---|---|---|---|---|---|
  | native | 141 | 17 | yes | 1166 | 1166 |
  | native_nodevtools | 141 | 17 | yes | 1166 | 1166 |

  **Warm re-run** (same build dirs, immediate second invocation, no clean):

  | Env | Cases | Suites | Warm total warnings | Warm macro-redef warnings |
  |---|---|---|---|---|
  | native | 141 | 17 | 998 | 998 |
  | native_nodevtools | 141 | 17 | 998 | 998 |

  Build-state recipe: cold = `rm -rf .pio/build/<env>` immediately before a single `pio test -e <env>` invocation with an explicit 540000ms Bash timeout (the default 2-minute timeout truncates the toolchain build mid-compile); warm = a second `pio test -e <env>` invocation immediately after, with no intervening clean, reusing the just-built `.pio/build/<env>` cache. All four integers (1166/1166 cold, 998/998 warm) match RESEARCH's recorded post-merge figures exactly.

- **Gate results** (verbatim, all run from `/workspaces/firestarter`):
  - `check_size_baseline.py --native-log native=... --native-log native_nodevtools=...`: `PASS: native(cases=141,suites=17), native_nodevtools(cases=141,suites=17)` — exit 0 (MERGE-06 half one).
  - `check_size_baseline.py` DEFAULT mode, all three AVR logs: `FAIL:\n  uno: flash_used baseline=23932 observed=23954\n  uno328pb: flash_used baseline=23976 observed=24004\n  leonardo: flash_used baseline=26072 observed=26016` — exit 1. **Planned red (W-1), owning plan: 124-10.**
  - `check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json`, all three AVR logs: `PASS: uno(flash=23954/32256[+22<=64],ram=1573/2048[=]), uno328pb(flash=24004/32384[+28<=64],ram=1579/2048[=]), leonardo(flash=26016/28672[-56<=0],ram=2014/2560[=])` — exit 0 (MERGE-05).
  - `check_build_warnings.py --log`, three AVR envs: `PASS: uno: macro_redefinition=0 (== 0), uno328pb: macro_redefinition=0 (== 0), leonardo: macro_redefinition=0 (== 0)` — exit 0.
  - `check_build_warnings.py --log`, both native envs (warm logs): `FAIL:\n  native: macro_redefinition observed=998 exceeds recorded=360; native: total warnings observed=998 exceeds watermark=360\n  native_nodevtools: macro_redefinition observed=998 exceeds recorded=360; native_nodevtools: total warnings observed=998 exceeds watermark=360` — exit 1. **Planned red (W-2), owning plan: 124-10.**
  - `check_cmake_manifest.py`: `FAIL: 9 violation(s)` naming the `flash_type_3.cpp`/`flash_type_4.cpp` rename pair plus 6 uncovered-but-present source files and `src/rurp_config_utils.cpp` — exit 1. **Planned red (W-4), owning plan: 124-05.**
  - `check_orphan_provisional.py`: `FAIL: 1 violation(s): RURP_PY32F071_PINMAP_PROVISIONAL: zero consumers outside its own definition (include/boards/py32f071_rurp_shield.h:38)` — exit 1. **Planned red (W-5), owning plan: 124-08.**
  - `python3 -m pytest tests/ -q`: **2 failed, 64 passed** — `tests/test_check_cmake_manifest.py::test_unarmed_on_the_real_tree_with_no_seam_override` and `tests/test_check_orphan_provisional.py::test_unarmed_on_the_real_tree_with_no_seam_override`. **Planned red (W-3), owning plans: 124-05 and 124-08.**
  - `python3 -m pytest tests/test_golden_trace_identity.py -q`: **6 passed, 0 failed** (MERGE-06 half two — the golden-trace pin holds unchanged across the merge).
- `git status --porcelain` (end of Task 3): empty — no measurement command wrote into the tree.

## Task Commits

Each code-producing task was committed atomically, inside the `firestarter` submodule (`/workspaces/firestarter`) on branch `v1.23-py32f071-integration`. Task 1 and Task 3 modify no repo files (scratch clone and measurement only) and produced no commits.

1. **Task 2: Produce the squashed landing commit** - `e2c422d` (feat)

_No plan-metadata commit is made inside the submodule — the meta-repo's own SUMMARY.md commit (below) is this plan's final commit._

## Files Created/Modified

- `firestarter/.github/workflows/py32f071.yml` - landed workflow (124-05 adds its `push` trigger later)
- `firestarter/include/avr/pgmspace.h` - landed AVR-shim header
- `firestarter/include/boards/py32f071_rurp_shield.h` - landed board header (carries the hollow guard 124-09 repairs later)
- `firestarter/include/rurp_platform.h` - landed portability header
- `firestarter/include/rurp_platform_compat.h` - landed portability header, includes 780a3fb's four helper macros by content
- `firestarter/include/rurp_serial_utils.h` - modified by the squash (part of the 2-modified half of the 22-path surface)
- `firestarter/include/rurp_shield.h` - modified by the squash (part of the 2-modified half of the 22-path surface)
- `firestarter/platform/py32f071/` - 15 newly landed files (CMakeLists.txt, cmake/write_checksums.cmake, src/main.cpp, linker/PY32F071xB_FLASH.ld, etc.)

## Decisions Made

- **Squash tree equality re-computed, not transcribed.** Built both a squash and a true-merge landing on throwaway branches in a scratch clone and compared `^{tree}` SHAs directly, rather than trusting RESEARCH's recorded `693ffdf`. Both landings' tips had not moved since RESEARCH ran, so the recomputed values matched exactly — but the comparison was genuinely re-run, per the plan's explicit instruction.
- **Commit message records tip SHAs + `780a3fb` by name, not the full 52-commit shortlog** — the plan's own recorded Claude's-discretion default.
- **Stale literal-integer acceptance criteria treated as findings, not blockers.** The plan's Task 1/Task 2 acceptance criteria state "14 ahead / 0 behind" and "`origin/beta..HEAD` is 15" — both session-time snapshots from before RESEARCH's measurement, made stale by 124-01/02/03's own 7 commits landing in between. The actual load-bearing invariants (`HEAD..origin/beta` stays 0; exactly one new commit lands) held exactly; only the absolute counts (21 pre-landing, 22 post-landing) differ from the literal numbers written into the plan. Reported here rather than silently reconciled, per this same class of acceptance-criterion imprecision documented in 124-01/02/03's own summaries.
- **Cold-native-build Bash timeout raised explicitly.** A genuinely cold `pio test -e native`/`native_nodevtools` run compiles the full 17-suite Unity test tree from scratch and exceeds the tool's default 2-minute Bash timeout; the resulting `SIGTERM` leaves a partially-populated `.pio/build/<env>` cache that a subsequent default-timeout invocation silently reuses, undercounting the cold measurement. Fixed by re-issuing `rm -rf .pio/build/<env>` and re-running the entire `pio test` invocation in one Bash call carrying an explicit `timeout: 540000`. Both cold measurements (1166/1166) then matched RESEARCH's recorded figures exactly, confirming the fix rather than papering over a discrepancy.

## Deviations from Plan

### Auto-fixed Issues

None — all corrections were to my own measurement procedure (the cold-build timeout trap above), not to plan-specified repo content, and were caught and corrected before any commit or recorded figure was finalized.

### Documented Discrepancies (not auto-fixed — stale plan literals, not code defects)

**1. `origin/beta..HEAD` counts (14/15) in the plan's acceptance criteria are stale by execute time.** See "Decisions Made" above. The plan's own critical_execution_constraint #1 ("re-compute, do not transcribe") anticipates exactly this class of drift for the tree-equality SHA; the same caution turned out to apply to these two literal integers as well, because three wave-1 plans (124-01/02/03, 7 commits total) landed between RESEARCH's session and this plan's execution. Not a violation of any load-bearing invariant: `HEAD..origin/beta` is still 0, and exactly one new commit (`e2c422d`) landed.

---

**Total deviations:** 0 auto-fixed on repo content; 1 documented discrepancy (stale acceptance-criterion literals, not a code defect) plus 1 self-corrected measurement-procedure trap (cold-build timeout) caught before any figure was recorded.
**Impact on plan:** None on scope, correctness, or the discharged requirements. The landing is exactly what D-05 specifies (one squashed commit, tree-proven equal to a true merge), every measurement matches RESEARCH's predicted figures exactly, and every expected-red gate fired for its pre-declared, pre-owned reason.

## Issues Encountered

- **Scratch clone did not carry remote-tracking refs by default.** `git clone --shared --no-checkout` of a local repository copies `refs/heads/*` but not the source repo's own `refs/remotes/origin/*` remote-tracking refs (those are not real branches in the source, so ordinary clone semantics don't fetch them). Resolved by an explicit `git fetch /workspaces/firestarter <refspec>` for each of the four needed refs (`agent/portability-macros`, `agent/py32f071-toolchain`, `feature/py32f071-release-assets`, `beta`) directly from the local path — no network access was needed or attempted.
- **Cold-native-build timeout trap** — see Decisions Made above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The PY32F071 port now exists on `v1.23-py32f071-integration` as one atomic, tree-proven-clean landing (`e2c422d`). MERGE-01, MERGE-05, and MERGE-06 are discharged by real exit codes against the real landed tree (not merely by the checkers' own unit tests, which is what 124-01/02/03 had proven before this plan ran).
- **Note on requirements bookkeeping:** `REQUIREMENTS.md` already showed MERGE-01/MERGE-05/MERGE-06 checked `[x]` before this plan executed, because 124-01/02/03 each ran `requirements.mark-complete` for their own assigned ID upon completing the *enforcement gate* for that requirement (per each plan's `requirements-completed` frontmatter) — before the actual landing this plan performs existed. This is the same premature-marking pattern flagged in memory (`reference_executors_prematurely_mark_requirements_complete.md`), originating in 124-01/02/03, not this plan. By the time this plan's `requirements.mark-complete [MERGE-01, MERGE-05, MERGE-06]` runs, the claims are now genuinely true — the landing exists and all three gates pass against it — so no correction was needed, only this note for the record.
- Every plan from 124-05 onward has its exact starting figures: AVR flash/RAM (uno 23954/1573, uno328pb 24004/1579, leonardo 26016/2014), native counts (141/17 both envs), native warning watermarks (cold 1166/1166, warm 998/998), and the five red gates each with a named owner (124-05: `check_cmake_manifest.py` 9 violations + its `UNARMED:` pytest; 124-08: `check_orphan_provisional.py` 1 violation + its `UNARMED:` pytest; 124-10: default-mode `check_size_baseline.py` + native `check_build_warnings.py`).
- Per D-03, the shared-code `DEV_TOOLS` conversion (124-06), `write_checksums.cmake` deletion + flash-latency fix (124-07) are separate later commits, not folded into this landing — so any flash/RAM delta those plans produce will be cleanly attributable against the figures recorded here.
- `ad47c3b`/`feature/py32f071-release-assets` confirmed NOT an ancestor of HEAD post-landing (D-07 holds).
- No blockers for 124-05 onward.

## Self-Check: PASSED

- FOUND: `.planning/phases/124-firmware-integration-merge/124-04-SUMMARY.md`
- FOUND commit `e2c422d` (firestarter submodule) — `git log --oneline --all | grep e2c422d` matches
- FOUND: `firestarter/platform/py32f071/CMakeLists.txt`
- FOUND: `firestarter/include/rurp_platform_compat.h`
- FOUND: `firestarter/include/avr/pgmspace.h`
- FOUND: `firestarter/.github/workflows/py32f071.yml`

---
*Phase: 124-firmware-integration-merge*
*Completed: 2026-07-31*
