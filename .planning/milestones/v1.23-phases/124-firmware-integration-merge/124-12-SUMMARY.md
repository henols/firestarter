---
phase: 124-firmware-integration-merge
plan: "12"
subsystem: firmware-ci
tags: [firestarter, py32f071, non-regression, evidence-artifact, requirements-ledger, closing-plan]

# Dependency graph
requires:
  - phase: 124-firmware-integration-merge
    plan: "10"
    provides: "The final code-bearing tree, MERGE-05/MERGE-06 discharged as exit codes on it, and every fixture/literal the post-landing re-baseline invalidated already repaired."
  - phase: 124-firmware-integration-merge
    plan: "11"
    provides: "MERGE-02's ARM CI evidence (run 30634186514, head SHA a145081b) and MERGE-03's confirmation on the pushed ref -- this plan re-queries both read-only rather than transcribing them."
provides:
  - "124-NONREGRESSION.md -- the phase's closing recorded-evidence artifact in 123-NONREGRESSION.md's shape, every row re-executed in this closing session against the trees as they now stand"
  - "All nine cross-repo MERGE-07 gates re-run from /workspaces/firestarter_app with the merged /workspaces/firestarter sibling, zero skips, full host suite 1158 passed/0 skipped"
  - "MERGE-01..MERGE-08 all ticked in REQUIREMENTS.md, each citing a specific re-executed row; the three premature 124-01/02/03 ticks (MERGE-01/05/06) re-justified against this session's own re-execution rather than left standing unexamined"
  - "The Traceability table's Phase 124 row moved from Pending to Complete"
affects: [125-vpp-control-seam, 130-close]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "A phase-closing evidence artifact re-executes every row in its own session rather than transcribing prior plans' SUMMARY claims -- the one permitted exception is a CI-run row, which is re-queried read-only instead of re-run locally"
    - "A closing artifact inverts its predecessor's structure section-by-section: 'what is UNARMED' becomes 'what armed and what it fired on'; 'nothing was adjusted to go green' becomes explicit reasoned exceptions naming what was adjusted and why the requirement licensed it"

key-files:
  created:
    - .planning/phases/124-firmware-integration-merge/124-NONREGRESSION.md
  modified:
    - .planning/REQUIREMENTS.md

key-decisions:
  - "check_landing_range.py's scanned-commit count (38, vs 124-04's recorded 22) is reported as an expected consequence of the checker scanning forward from a fixed historical fork point across 8 further code-bearing plans (124-05..124-10), not reconciled or treated as a discrepancy -- the violations figure (0) is the load-bearing invariant and is unchanged."
  - "MERGE-01/MERGE-05/MERGE-06 were already [x] in REQUIREMENTS.md, ticked by 124-01/02/03 before the real landing existed (proving only that each plan's own enforcement gate worked). Rather than leaving those ticks standing unexamined or blindly re-ticking, each was re-justified this session against a row this plan itself re-executed (F10 for MERGE-01, F4d for MERGE-05, F2/F3/F6a/F11 for MERGE-06) -- all three are genuinely true now, and the SUMMARY says so explicitly rather than silently inheriting the premature tick."
  - "Section 8's two Phase-123 claims (no baseline/watermark adjusted; no push/gh occurred) are rewritten as explicit reasoned exceptions with exact numbers (360 warm-mislabeled -> 456 cold pre-landing -> 1166 cold landed; the milestone-branch-only push behind D-09's operator gate), per the plan's own instruction, rather than silently dropped or left as an inherited false claim."
  - "The ARM row is the one row in this document NOT locally re-executed -- it is re-queried read-only via gh run view against CI run 30634186514, exactly as D-16 permits, with the head SHA cross-checked string-equal against the live firmware HEAD re-derived in this same session."

requirements-completed: [MERGE-01, MERGE-02, MERGE-03, MERGE-04, MERGE-05, MERGE-06, MERGE-07, MERGE-08]

coverage:
  - id: D1
    description: "124-NONREGRESSION.md exists in 123-NONREGRESSION.md's established shape (9 sections + sweep summary + a 10th requirement-tick-citation section), every row re-executed in this closing session"
    requirement: "MERGE-07"
    verification:
      - kind: other
        ref: "python3 .planning/phases/123-non-regression-baselines-gate-hardening/check_permitted_claims.py .planning/phases/124-firmware-integration-merge/124-NONREGRESSION.md -- exit 0"
        status: pass
      - kind: other
        ref: "grep -c 'diff --stat' 124-NONREGRESSION.md -- 3 hits, all carrying an explicit ref range or being the anti-regression grep pattern itself; 0 ref-less occurrences"
        status: pass
    human_judgment: false
  - id: D2
    description: "All nine cross-repo MERGE-07 gates (11 rows H1-H9b) shown to run and pass from /workspaces/firestarter_app with the merged /workspaces/firestarter sibling; full host suite 1158 passed, 0 failed, 0 skipped under -rs"
    requirement: "MERGE-07"
    verification:
      - kind: integration
        ref: "cd /workspaces/firestarter_app && python3 -m pytest tests/ -q -rs -- 1158 passed, 0 failed, 0 skipped (dot-count independently verified at 1158 across 17 progress lines; zero SKIPPED/skip lines by grep)"
        status: pass
      - kind: integration
        ref: "H1-H9b (check_no_log_in_sdp_window.py, check_is_memory_cmd_no_ifdef.py, gen_sdp_bus_config.py idempotence, check_dispatch.py, check_devtest_orchestrator.py + their paired pytests) -- all 11 rows PASS/passed, exit 0 each"
        status: pass
    human_judgment: false
  - id: D3
    description: "MERGE-01 (landing-range gate re-run: 0 violations), MERGE-05 (band comparator vs frozen BASE-01, all 3 AVR targets), MERGE-06 (both native envs 141/17, golden-trace per-array identity) all re-discharged as exit codes on the final tree in this session"
    requirement: "MERGE-01, MERGE-05, MERGE-06"
    verification:
      - kind: unit
        ref: "check_landing_range.py -- PASS: 38 commit(s) scanned, 0 violations"
        status: pass
      - kind: unit
        ref: "check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json -- PASS: uno(+22<=64), uno328pb(+28<=64), leonardo(-56<=0), all RAM unchanged"
        status: pass
      - kind: unit
        ref: "check_size_baseline.py --native-log (both pinned envs) -- PASS: cases=141,suites=17 both; pytest tests/test_golden_trace_identity.py -- 6 passed"
        status: pass
    human_judgment: false
  - id: D4
    description: "MERGE-02's ARM configure-and-build evidence and MERGE-03's push-trigger confirmation both re-verified this session -- CI run re-queried read-only, workflow file re-read from both the local tree and the fetched remote ref"
    requirement: "MERGE-02, MERGE-03"
    verification:
      - kind: other
        ref: "gh run view 30634186514 -- re-queried this session: conclusion=success, headSha=a145081b59d94530583b9ce365db03ff567d0c2c (string-equal to live firmware HEAD), Configure=success, Build=success"
        status: pass
      - kind: other
        ref: "git fetch origin v1.23-py32f071-integration && git show origin/...:py32f071.yml -- push: branches: [beta] present on the pushed ref, byte-identical to the local file"
        status: pass
    human_judgment: false
  - id: D5
    description: "MERGE-04's refusal (native suite 10/10) and fire-proof (6 passed) both re-run this session; MERGE-08's three named defects re-verified against the live tree"
    requirement: "MERGE-04, MERGE-08"
    verification:
      - kind: unit
        ref: "pio test -e native_pinmap_provisional -- 10 test cases: 10 succeeded; pytest tests/test_pinmap_guard_fires.py -- 6 passed"
        status: pass
      - kind: unit
        ref: "grep -n FLASH_LATENCY_1/FLASH_ACR_LATENCY_1 main.cpp; test -f write_checksums.cmake (absent); grep DEV_TOOLS CMakeLists.txt/firestarter.h -- all three defects confirmed fixed this session"
        status: pass
    human_judgment: false
  - id: D6
    description: "MERGE-01..MERGE-08 all ticked in REQUIREMENTS.md, each citing a specific re-executed row, multi-clause requirements justified clause by clause; Traceability row updated from Pending to Complete"
    requirement: "MERGE-01, MERGE-02, MERGE-03, MERGE-04, MERGE-05, MERGE-06, MERGE-07, MERGE-08"
    verification:
      - kind: other
        ref: "grep -n 'MERGE-0' .planning/REQUIREMENTS.md -- all 8 lines now [x]; Traceability row reads 'Complete -- all 8 ticked, see 124-NONREGRESSION.md §3/§4 for the row cited per requirement'"
        status: pass
      - kind: other
        ref: "git rev-parse --abbrev-ref HEAD after each commit -- gsd/v1.23-py32f071-integration, unchanged"
        status: pass
    human_judgment: false

duration: ~75min
completed: 2026-07-31
status: complete
---

# Phase 124 Plan 12: MERGE-07 Sweep + 124-NONREGRESSION.md + Requirement Ticks Summary

**Re-executed all nine cross-repo gates and every AVR/native/firmware assertion in this closing session (never transcribed from the eleven prior plans' SUMMARY files), wrote `124-NONREGRESSION.md` in `123-NONREGRESSION.md`'s shape with its two deliberately-violated claims carried as reasoned exceptions, and ticked all eight MERGE-01..MERGE-08 requirements against specific re-executed rows.**

## Performance

- **Duration:** ~75 min
- **Started:** 2026-07-31 (session start, reading all 12 plan/summary artifacts + REQUIREMENTS.md + 123-NONREGRESSION.md)
- **Completed:** 2026-07-31T14:03:11Z
- **Tasks:** 3 completed
- **Files modified:** 2 (1 created, 1 modified) — meta-repo only, neither sub-repo modified

## Accomplishments

- **Task 1 — the full cross-repo sweep, firmware then host, all in this session:**
  - Firmware (`/workspaces/firestarter`): `pytest tests/ -q` → **72 passed**, 0 skipped. Both pinned native envs (`native`, `native_nodevtools`) cold → **141/141, 17 suites, all PASSED** each. The third env (`native_pinmap_provisional`) → **10/10, 1 suite, all PASSED**. All three AVR clean builds byte-identical to the recorded landing figures (uno 23954/1573, uno328pb 24004/1579, leonardo 26016/2014). `check_size_baseline.py` default mode and `--policy merge05` (vs the **frozen** `size_baseline_base01.json`) both exit 0 with the exact RESEARCH-predicted deltas (-56/+22/+28, RAM unchanged). `check_build_warnings.py --log` exits 0 on all three AVR envs (0 warnings) and all three native envs (cold: 1166/1166/138, all `== watermark`). `check_cmake_manifest.py` and `check_orphan_provisional.py` both **PASS** (armed, inverted from Phase 123's `UNARMED:`). `check_landing_range.py` → **PASS: 38 commit(s) scanned ... 0 violations**. `test_golden_trace_identity.py` and `test_pinmap_guard_fires.py` → 6 passed each.
  - Host (`/workspaces/firestarter_app`, the literally-named directory with the merged `firestarter` sibling): all eleven MERGE-07 rows (H1-H9b) PASS/passed, including H5's idempotence proof (`git -C firestarter status --porcelain` empty **before and after** `gen_sdp_bus_config.py`). The full host suite with `-rs`: **1158 passed, 0 failed, 0 skipped** (zero `SKIPPED` lines found by direct grep; dot-count independently verified at 1158 — byte-identical to Phase 123's recorded 1158). `check_no_exists_proxy.py`, `ruff check`, `ruff format --check`, `check_mypy_watermark.py` all match Phase 123's recorded green state.
  - ARM row: re-queried `gh run view 30634186514` read-only — `conclusion=success`, `headSha=a145081b59d94530583b9ce365db03ff567d0c2c` **string-equal** to the live firmware HEAD re-derived this session, Configure and Build steps each independently `success`. MERGE-03 re-confirmed on the **pushed remote ref** (`git fetch` + `git show origin/...`), not just the local file.
  - Meta claim scanner: self-test 10 passed; default run `UNARMED:` (Phase 130 hasn't started, expected); a courtesy run against the finished `124-NONREGRESSION.md` itself, exit 0.
  - Confirmed at the end: `git -C /workspaces/firestarter status --porcelain` empty; `git -C /workspaces/firestarter_app status --porcelain` matches the named pre-existing dirt exactly (`M .gitignore`; untracked `.coverage`, `.planning/config.json`, `SECURITY.md`, `write_test_port.sh`) — neither sub-repo was modified by this plan's sweep.
- **Task 2 — wrote `124-NONREGRESSION.md`** in `123-NONREGRESSION.md`'s section shape (header, re-execution pledge, sections 1-9 plus a new §10 requirement-tick-citation section, and the closing sweep summary table). Section 4 inverts Phase 123's "what is UNARMED" into "what armed and what it fired on" (the 9-violation CMake-manifest first fire, the 1-violation orphan-provisional first fire, the two expired Phase-123 pytests, the unpredicted native-warning watermark fire with its warm-vs-cold correction). Section 6 enumerates what moved across the full 38-commit range (never a path-scoped `git diff` standing in for "untouched") and proves the AVR-specific board files and `src/proms/*` (except `memory.cpp`) untouched. Section 8 carries both Phase-123 claims this phase deliberately violates as **explicit reasoned exceptions** with exact numbers (the frozen-vs-live baseline distinction, the 360→456→1166 warm/cold correction chain, and the milestone-branch-only push behind D-09's operator gate) — and separately re-asserts the bullets that still hold (no cross-repo CI leg added, no release cut, `beta` not pushed, Phase 130 still owns every remaining outward-facing action). The claim scanner was run against the finished file and its exit code (0) and verbatim output recorded inside the document itself.
- **Task 3 — ticked MERGE-01..MERGE-08 in `REQUIREMENTS.md`**, each citing a specific row from `124-NONREGRESSION.md`, with per-clause justification for every multi-clause requirement (MERGE-01's 3 clauses, MERGE-02's 2+1, MERGE-04's 2, MERGE-05's 3, MERGE-06's 2). The three requirements already `[x]` from 124-01/02/03 (MERGE-01, MERGE-05, MERGE-06 — ticked before the real landing existed) were re-justified against this session's own re-execution rather than left standing unexamined. The Traceability table's Phase 124 row moved from `Pending` to `Complete`. Committed in the meta-repo; `git rev-parse --abbrev-ref HEAD` confirmed `gsd/v1.23-py32f071-integration` after both commits.

## Observed Verification Values

See `124-NONREGRESSION.md` §§1-10 and the Sweep Summary table for the complete, row-by-row record. Headline figures:

- Firmware pytest: **72 passed**, 0 failed, 0 skipped.
- Native envs (cold): native 141/17, native_nodevtools 141/17, native_pinmap_provisional 10/1 — all PASSED.
- AVR: uno 23954/1573, uno328pb 24004/1579, leonardo 26016/2014 — byte-identical across every code-bearing plan since the landing.
- `check_landing_range.py`: **38 scanned, 0 violations** (vs 124-04's recorded 22 — the scanned count grows with every subsequent commit by design; violations, the load-bearing figure, stayed 0).
- Host full suite: **1158 passed, 0 failed, 0 skipped** — byte-identical to Phase 123's recorded 1158.
- Host MERGE-07 eleven-row table: all PASS.
- ARM CI run `30634186514`: conclusion=success; Configure=success; Build=success; head SHA string-equal to live firmware HEAD.
- Claim scanner against the finished `124-NONREGRESSION.md`: exit 0.
- `git -C /workspaces/firestarter status --porcelain`: empty. `git -C /workspaces/firestarter_app status --porcelain`: matches the named pre-existing dirt exactly.
- `git rev-parse --abbrev-ref HEAD` (meta repo, after both commits): `gsd/v1.23-py32f071-integration`.

## Task Commits

Both code-producing tasks were committed atomically, in the meta-repo (`/workspaces`) on branch `gsd/v1.23-py32f071-integration`. Task 1 (the sweep) modified no files and produced no commit.

1. **Task 2: Write 124-NONREGRESSION.md** - `559a233` (docs)
2. **Task 3: Tick MERGE-01..MERGE-08 against re-executed rows** - `1a4027c` (docs)

**Plan metadata:** committed separately below (this SUMMARY.md + STATE.md + ROADMAP.md commit).

## Files Created/Modified

- `.planning/phases/124-firmware-integration-merge/124-NONREGRESSION.md` - the closing D-16 recorded-evidence artifact
- `.planning/REQUIREMENTS.md` - MERGE-01..MERGE-08 all ticked `[x]`; Traceability row updated to Complete

## Decisions Made

- **`check_landing_range.py`'s scanned-commit growth (22 → 38) reported as expected, not reconciled.** The checker scans forward from a fixed historical fork point; every one of Plans 124-05 through 124-10's commits widens the range. The **violations** figure (0, both before and now) is the invariant MERGE-01 requires — the scanned count is a byproduct of "how far the range has grown," not a target to hold constant.
- **The three premature ticks (MERGE-01/05/06) were re-justified, not silently re-ticked.** Each was ticked by an earlier plan (124-01/02/03) before the real landing existed — proving only that each plan's own enforcement gate worked in isolation, the exact premature-marking pattern this project has flagged before. Rather than leaving those ticks standing unexamined, this plan re-executed the discharging row for each (F10, F4d, F2/F3/F6a/F11 respectively) and states explicitly in both this SUMMARY and `124-NONREGRESSION.md` §10 that they are re-justified against this session's own evidence, genuinely true now.
- **Section 8's two violated Phase-123 claims are rewritten as reasoned exceptions with exact numbers**, not silently dropped: the baseline/watermark exception names the frozen-vs-live baseline distinction and the 360-warm→456-cold→1166-cold correction chain (crediting Plan 124-10's own `meta.warm_vs_cold_correction`); the push/gh exception names the milestone-branch-only target, the re-proven zero-CI-trigger safety argument, and D-09's structural operator gate (crediting Plan 124-11's own decision record). Both exceptions are followed by an explicit re-assertion of the bullets that still hold unchanged.
- **The ARM row is the one row in this document not re-executed locally** — no ARM toolchain exists in this devcontainer. It is re-queried read-only via `gh run view`, per D-16's own permitted exception, with the head SHA cross-checked string-equal against the live firmware HEAD independently re-derived in this session (not assumed from Plan 124-11's own cross-check).

## Deviations from Plan

### Auto-fixed Issues

None — no bugs, missing functionality, or blocking issues were found during execution. All eleven prior plans' claimed figures reproduced byte-exact against this session's independent re-execution, with one expected non-discrepancy noted above (`check_landing_range.py`'s growing scanned count).

### Documented Findings (not defects — measurement facts)

**1. `check_landing_range.py`'s scanned-commit count grew from 124-04's recorded 22 to 38.** Not a discrepancy — the checker scans the full `<fork>..HEAD` range from a fixed historical fork point, and eight further code-bearing plans (124-05 through 124-10) added commits to that range after 124-04's own measurement. The violations figure (0) — the load-bearing invariant MERGE-01 requires — is unchanged. Documented explicitly in `124-NONREGRESSION.md`'s re-execution pledge rather than silently reconciled.

---

**Total deviations:** 0 auto-fixed; 1 documented finding (an expected, non-defect measurement growth in a moving count, not the invariant figure).
**Impact on plan:** None on scope or correctness. Every gate this phase is judged by executed in this session, in the real layout, with its observed value recorded, and none reported a skip.

## Issues Encountered

None beyond the documented finding above. One pytest full-suite invocation (`firestarter_app`'s 1158-test suite) exceeded the default Bash timeout and was completed via `run_in_background`; its output was captured to a log file and the pass/skip/fail counts independently verified by dot-counting and grep, not merely trusted from a truncated tail.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- MERGE-07 is fully discharged: all nine cross-repo gates shown to run (never skip) and pass, from the literally-named `firestarter_app` directory with the merged `firestarter` sibling.
- `124-NONREGRESSION.md` exists as the phase's closing recorded-evidence artifact, in the established shape, with every row re-executed in this closing session.
- All eight MERGE-01..MERGE-08 requirements are ticked, each citing a specific re-executed row; the Traceability table reflects the actual tick state (`Complete`).
- Phase 125 (VPP Control Seam) inherits a `scripts/baseline/size_baseline.json` that matches the tree as it stands (Plan 124-10's re-baseline) — VPP-03's flash-delta measurement has a live baseline to measure against.
- No push, no workflow dispatch, and no write-method `gh` call was made by this plan — only read-only `gh run view` and `git fetch` queries, per this plan's own constraint.
- No blockers for Phase 125 onward.

## Self-Check: PASSED

- FOUND: `.planning/phases/124-firmware-integration-merge/124-NONREGRESSION.md`
- FOUND: `.planning/REQUIREMENTS.md` (modified, all 8 MERGE ticks confirmed via grep)
- FOUND commit `559a233` (meta repo) — `git log --oneline --all | grep 559a233` matches
- FOUND commit `1a4027c` (meta repo) — `git log --oneline --all | grep 1a4027c` matches
- Confirmed branch `gsd/v1.23-py32f071-integration` after both commits (not switched)
- Re-verified independently: `.planning/phases/124-firmware-integration-merge/124-12-SUMMARY.md` present on disk (this file)

---
*Phase: 124-firmware-integration-merge*
*Completed: 2026-07-31*
