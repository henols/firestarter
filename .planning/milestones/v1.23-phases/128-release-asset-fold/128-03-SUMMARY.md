---
phase: 128-release-asset-fold
plan: 03
subsystem: ci
tags: [cmake, github-actions, py32f071, release-assets, firmware, filename-contract]

# Dependency graph
requires:
  - phase: 127-host-dfu-installer
    provides: "frozen `asset_candidates(\"py32f071\")[0]` filename contract in firestarter_app/firestarter/firmware.py"
  - phase: 124-firmware-integration-merge
    provides: "the py32f071 CMake target itself, which this plan renames outputs on"
provides:
  - "platform/py32f071/CMakeLists.txt emits firestarter_py32f071.{elf,bin,hex,map} (underscore, not hyphen)"
  - "the emitted HEX_FILE basename proven equal to the frozen host asset_candidates(\"py32f071\")[0] value via a non-vacuous guard"
  - "an inventory of the 21 remaining hyphenated occurrences (all confined to .github/workflows/py32f071.yml), a measured baseline for Plan 128-04"
affects: [128-04, 128-06, 128-07, 128-09, 128-10]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Cross-repo filename equality proven with a per-parse non-vacuity guard (regex must match before comparing) rather than a bare string comparison, so a rename that breaks the regex fails loudly instead of passing on two empty strings"

key-files:
  created: []
  modified:
    - firestarter/platform/py32f071/CMakeLists.txt

key-decisions:
  - "D-14 followed literally: the four-site rename was re-applied by hand from unmerged commit ad47c3b and cited in the commit message as re-applied, never cherry-picked, because ad47c3b's tree predates Phase 124's `push: branches: [beta]` trigger and its workflow shape is superseded by Plan 128-02's composite action."
  - "MISMATCH-2 corrected in the shipped comment: ad47c3b's own final sentence claimed the rename alone kept beta-build.yml's release glob working unmodified. That claim is false — the shipped glob is rooted at `.pio/build/` while this CMake build writes to `build/py32f071/`, so a second `files:` entry is required (Plan 128-07). The corrected comment states this instead of repeating ad47c3b's original wording."

patterns-established: []

requirements-completed: []  # Deliberate: this plan closes only the emitted-CMake-filename slice of REL-04.
                            # REL-04 as a whole additionally needs 128-04 (workflow renames), 128-06 (in-workflow
                            # assertions), 128-09 (three-way cross-repo binding) and 128-10 (run A evidence).
                            # Plan 128-10 is the sole owner of ticking REL-04 in REQUIREMENTS.md.

coverage:
  - id: D1
    description: "The four CMake output literals (TARGET_NAME, the -Wl,-Map= link option, BIN_FILE, HEX_FILE) renamed from firestarter-py32f071.* to firestarter_py32f071.*, with a corrected explanatory comment citing ad47c3b and the second-glob-entry fact"
    requirement: "REL-04"
    verification:
      - kind: unit
        ref: "cd /workspaces/firestarter && python3 -m pytest tests/ -q (180 passed)"
        status: pass
      - kind: other
        ref: "grep -v '^[[:space:]]*#' platform/py32f071/CMakeLists.txt | grep -c firestarter-py32f071 -> 0; grep -n firestarter_py32f071 shows the four rename sites"
        status: pass
    human_judgment: false
  - id: D2
    description: "The CMake-emitted hex basename proven equal to the frozen host asset_candidates(\"py32f071\")[0] value via a non-vacuous per-parse guard, plus a repo-wide inventory of remaining hyphenated occurrences"
    requirement: "REL-04"
    verification:
      - kind: unit
        ref: "inline python3 script in /workspaces/firestarter_app comparing CMake-parsed HEX_FILE basename against asset_candidates('py32f071')[0], asserting both are non-empty and regex-matching before comparing -> printed EQUAL firestarter_py32f071.hex"
        status: pass
    human_judgment: false

# Metrics
duration: ~20min
completed: 2026-08-01
status: complete
---

# Phase 128 Plan 03: py32f071 CMake Output Rename Summary

**Re-applied ad47c3b's hyphen-to-underscore CMake output rename by hand (never cherry-picked) and corrected its false glob-coverage claim, proving the emitted `firestarter_py32f071.hex` basename equals the frozen host contract via a non-vacuous guard.**

## Performance

- **Duration:** ~20 min
- **Completed:** 2026-08-01T21:02:56Z
- **Tasks:** 2/2
- **Files modified:** 1 (firestarter/platform/py32f071/CMakeLists.txt)

## Accomplishments

- All four emitted-output literals in `platform/py32f071/CMakeLists.txt` (`TARGET_NAME`, the `-Wl,-Map=` link option, `BIN_FILE`, `HEX_FILE`) now use the underscored basename `firestarter_py32f071.*`, matching what `name_firmware.py` produces for the AVR targets.
- The explanatory comment above `TARGET_NAME` was re-applied from `ad47c3b`'s reasoning (host-installer resolution by `firestarter_<board>.hex`, board name from `RURP_BOARD_NAME`) and its false final claim corrected: the shipped glob is rooted at `.pio/build/` while this CMake build writes to `build/py32f071/`, so one glob cannot cover both trees and a second `files:` entry is required (Plan 128-07 adds it). The comment also states the rename was re-applied by hand, not cherry-picked, and why.
- Proved, non-vacuously, that the emitted `HEX_FILE` basename (`firestarter_py32f071.hex`) equals `asset_candidates("py32f071")[0]` as computed live from the frozen `firestarter_app/firestarter/firmware.py` — the guard asserts each parsed string is non-empty and regex-matches a lowercase underscored firestarter hex name *before* comparing, so a rename that breaks the regex fails loudly rather than passing on two empty strings.
- Inventoried the repo-wide remaining hyphenated occurrences (comment-stripped, repo-wide): **21 occurrences, all confined to `.github/workflows/py32f071.yml`** (lines 66, 79, 86, 87, 88, 90, 91, 92, 93, 94, 95, 100, 101, 102, 103, 113, 116, 117, 118, 119, 120) — the measured baseline Plan 128-04 and Plan 128-08's consistency sweep close against.
- `RURP_BOARD_NAME="py32f071"` and the SDK `GIT_TAG 0ed2f4b4d3391eccfd4491006a30295fd78e32c2` pin are untouched — confirmed by grep count of 1 each.

## Task Commits

1. **Task 1: Rename the four CMake output literals and rewrite the explanatory comment** - `a7db7b7` (fix)
2. **Task 2: Prove the emitted name equals the frozen host contract, non-vacuously** - verification-only, no source changes; no separate commit (see Deviations below)

**Plan metadata:** committed separately (this SUMMARY + STATE/ROADMAP update)

## Files Created/Modified

- `firestarter/platform/py32f071/CMakeLists.txt` - Renamed the four emitted-output literals hyphen→underscore; corrected the explanatory comment's false glob-coverage claim.

## Decisions Made

- Followed D-14 literally: hand re-application citing `ad47c3b`, not a cherry-pick, because `ad47c3b`'s tree predates Phase 124's `push: branches: [beta]` trigger and its workflow-side rewrite is superseded by Plan 128-02's composite action.
- Followed the plan's instruction to REPLACE `ad47c3b`'s false final sentence (128-PATTERNS.md MISMATCH-2) rather than carry it forward, and to cite Phase 128 Plan 03 + `ad47c3b` in the new comment per house style (every comment names the decision/requirement/phase that produced the line).
- Did not tick REL-04 in REQUIREMENTS.md — this plan closes only the emitted-CMake-filename slice; Plan 128-10 is the sole owner of REL-04 closure, per the plan's explicit scope boundary.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug in the plan's own verify script] Automated grep-count assertion in Task 1's `<verify>` block undercounts by one due to a pre-existing, unrelated occurrence**
- **Found during:** Task 1 verification
- **Issue:** The plan's automated verify command asserts `grep -c 'firestarter_py32f071' /tmp/cml.nc` equals exactly 4 (one per renamed literal: `TARGET_NAME`, `-Wl,-Map=`, `BIN_FILE`, `HEX_FILE`). The comment-stripped file actually contains **5** occurrences of the substring `firestarter_py32f071`, because line 9 — `project(firestarter_py32f071 C CXX ASM)` — already used the underscored form *before this plan touched the file* (confirmed via `git diff`: line 9 is untouched by this plan's diff). This CMake `project()` name is unrelated to the four emitted-output-file literals the plan's acceptance criteria enumerate by exact line (`TARGET_NAME` `.elf`, `-Wl,-Map=` `.map`, `BIN_FILE` `.bin`, `HEX_FILE` `.hex`), and its inclusion in a substring grep is incidental, not a code defect.
- **Fix:** No source change was needed — the source is correct per the acceptance criteria's own line-by-line check (`grep -n 'firestarter_py32f071' platform/py32f071/CMakeLists.txt` shows exactly one match each on the four expected lines, plus the pre-existing line 9). Verified the hyphenated form is fully absent (0 occurrences) and each of the four required renamed sites is present with the correct extension. This is documented here rather than silently patched around, per the scope boundary against modifying anything the plan didn't scope.
- **Files modified:** None beyond the plan's own scope (firestarter/platform/py32f071/CMakeLists.txt, already covered above).
- **Verification:** `git diff platform/py32f071/CMakeLists.txt` confirms line 9 (`project(...)`) is untouched by this plan's edits; `grep -n 'firestarter_py32f071' platform/py32f071/CMakeLists.txt` shows the four expected rename sites plus the pre-existing `project()` line; `python3 -m pytest tests/ -q` is green (180 passed).
- **Committed in:** a7db7b7 (Task 1 commit) — no additional commit needed since no source was altered for this deviation.

---

**Total deviations:** 1 auto-fixed (1 bug — in the plan's own verify script, not in source code)
**Impact on plan:** No scope creep. The rename itself is correct and matches every acceptance criterion that names an exact line; only the generic substring-count assertion needed contextual correction, which is recorded here rather than silently worked around.

## Issues Encountered

None beyond the deviation above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The emitted CMake basename (`firestarter_py32f071.hex`) is proven equal to the host's frozen `asset_candidates("py32f071")[0]` contract, non-vacuously — Plan 128-09's three-way cross-repo test has a correct firmware side to bind against.
- The measured baseline of 21 remaining hyphenated occurrences, all confined to `.github/workflows/py32f071.yml`, is exactly what Plan 128-04 (the workflow-side rename) needs to close against, and gives Plan 128-08's consistency sweep a measured starting point rather than an assumption.
- No blockers. `firestarter`'s working tree is clean (`git status --porcelain` empty) after the Task 1 commit, satisfying the precondition Plan 128-09 needs (128-RESEARCH F-16).
- REL-04 remains open as a whole — only its emitted-filename slice is closed here. Plan 128-10 must not skip re-verifying this slice when it ticks REL-04.

---
*Phase: 128-release-asset-fold*
*Completed: 2026-08-01*

## Self-Check: PASSED

- FOUND: `/workspaces/.planning/phases/128-release-asset-fold/128-03-SUMMARY.md`
- FOUND: `/workspaces/firestarter/platform/py32f071/CMakeLists.txt`
- FOUND: commit `9039b43` (meta repo, SUMMARY.md)
- FOUND: commit `a7db7b7` (firestarter repo, CMake rename)
