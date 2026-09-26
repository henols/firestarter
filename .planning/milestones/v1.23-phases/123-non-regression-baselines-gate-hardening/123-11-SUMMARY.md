---
phase: 123-non-regression-baselines-gate-hardening
plan: 11
subsystem: build-measurement-baselines
tags: [non-regression-gate, evidence-artifact, requirement-closure, cross-repo-gates, milestone-close]

# Dependency graph
requires:
  - phase: 123-non-regression-baselines-gate-hardening (123-01 .. 123-10)
    provides: "size_baseline.json, all four firmware checkers + fixtures, tests/fw_presence.py + scan_paths.py, the skip census + recurrence lint, the v1.23 claim gate — every artifact this plan re-verifies and cites"
provides:
  - ".planning/phases/123-non-regression-baselines-gate-hardening/123-NONREGRESSION.md — D-05's recorded evidence artifact, every row re-executed this session"
  - "BASE-01..BASE-08 ticked Complete in .planning/REQUIREMENTS.md, each citing a named 123-NONREGRESSION.md row"
  - "ROADMAP.md Phase 123 Details block: all 11 plan boxes ticked"
affects: ["Phase 124 (MERGE-05/06/07 read this artifact instead of recomputing)", "Phase 130 (CLOSE-02 honesty ledger cites this artifact)"]

tech-stack:
  added: []
  patterns:
    - "Cumulative fork_point..HEAD diff (not a working-tree diff) as the phase-wide no-firmware-code-moves proof"
    - "Cite-by-location instead of verbatim-quote when a forbidden-claim gate would trip on its own citation (122-NONREGRESSION.md precedent)"

key-files:
  created:
    - .planning/phases/123-non-regression-baselines-gate-hardening/123-NONREGRESSION.md
  modified:
    - .planning/REQUIREMENTS.md
    - .planning/ROADMAP.md

key-decisions:
  - "Section 7 (validation ceiling) cites REQUIREMENTS.md's forbidden-claim list by location (REQUIREMENTS.md:14) rather than quoting it verbatim — quoting it tripped check_permitted_claims.py's own courtesy claim-scan (5 matches), reproducing exactly the self-referential trap 122-NONREGRESSION.md's §7 already documented and worked around the same way"
  - "Row H5's idempotence baseline is recorded as the empty string (firestarter's own git status --porcelain was empty both before and after gen_sdp_bus_config.py ran), not the non-empty '?? firestarter/' baseline 122-NONREGRESSION.md recorded for a different phase-end tree state — the plan's own instruction is to assert against THIS session's pre-run baseline, not a copied one"
  - "ROADMAP.md's '**Plans**: 10/11 plans executed' header line left byte-unchanged per the plan's explicit instruction — that line is roadmap.update-plan-progress's job in the standard state-update step, not this task's; only the 123-11-PLAN.md checkbox itself was ticked"

requirements-completed: [BASE-01, BASE-02, BASE-03, BASE-04, BASE-05, BASE-06, BASE-07, BASE-08]

coverage:
  - id: D1
    description: "123-NONREGRESSION.md exists, mirrors 122-NONREGRESSION.md's command/expected/observed shape, and every row was re-executed live in this session (not copied from a prior plan's SUMMARY)"
    verification:
      - kind: other
        ref: "wc -l 123-NONREGRESSION.md -> 343 (>= 120 minimum); all 20 required literal strings/figures present; FIRESTARTER_CLAIMSCAN_TARGETS=... python3 check_permitted_claims.py -> PASS, exit 0"
        status: pass
    human_judgment: false
  - id: D2
    description: "All eight BASE requirements ticked Complete in REQUIREMENTS.md, each traceable to a named 123-NONREGRESSION.md row; Traceability table row updated to Complete; coverage counts (47/47/0) unaffected"
    verification:
      - kind: other
        ref: "grep -cE '^- \\[x\\] \\*\\*BASE-0[1-8]\\*\\*' REQUIREMENTS.md -> 8; grep -cE '^- \\[ \\] \\*\\*BASE-0' REQUIREMENTS.md -> 0; git diff HEAD -- REQUIREMENTS.md touches exactly 9 lines"
        status: pass
    human_judgment: false
  - id: D3
    description: "ROADMAP.md Phase 123 Details block: 123-11-PLAN.md box ticked, exactly 11 plan rows present, no Phase 124-130 or earlier-milestone line touched, STATE.md untouched"
    verification:
      - kind: other
        ref: "11 ticked plan rows counted; git diff --numstat HEAD -- ROADMAP.md -> 2 (1+1, within the 30-line ceiling); grep -cE Phase 12[4-9]:|Phase 130: over the diff -> 0; git status --porcelain -- STATE.md -> empty"
        status: pass
    human_judgment: false

duration: 55min
completed: 2026-07-31
status: complete
---

# Phase 123 Plan 11: Full Cross-Repo Gate Sweep + D-05 Evidence Artifact + BASE Requirement Closure Summary

**Re-ran every gate this phase created plus the 11-row pre-existing cross-repo gate set against the finished trees, wrote `123-NONREGRESSION.md` (343 lines, mirroring `122-NONREGRESSION.md`'s command/expected/observed shape), and ticked BASE-01 through BASE-08 in REQUIREMENTS.md — the only place any BASE requirement is marked Complete.**

## Performance

- **Duration:** ~55 min
- **Tasks:** 3/3 completed
- **Files modified:** 3 (1 created evidence artifact, 2 modified: REQUIREMENTS.md, ROADMAP.md)

## Accomplishments

### Task 1 — full gate sweep, re-executed live (no file writes)

Every row in the plan's action text was re-run in this session against the trees as they stand,
never copied from a prior plan's SUMMARY:

- **Firmware:** `python3 -m pytest tests/ -q` → **48 passed**, 0 skipped. Both native envs
  (`pio test -e native` / `-e native_nodevtools`) → **141/141 succeeded, 17 suites**, agreeing exactly.
  Fresh clean rebuilds of all three AVR envs matched the recorded baseline byte-exact
  (uno 23932/1573, uno328pb 23976/1579, leonardo 26072/2014), each passing both
  `check_size_baseline.py` and `check_build_warnings.py` (exit 0). Both native envs' fresh logs
  measured **360** total warnings (all macro-redefinition-shaped), matching the recorded watermark
  exactly. Both coarse-key gates (`check_cmake_manifest.py`, `check_orphan_provisional.py`) printed
  the identical `UNARMED:` line, exit 0.
- **The phase-wide no-firmware-code-moves proof:** `FORK=5c9160a34b665878b05403ab014b959926feb6bf`
  (read from `123-01-SUMMARY.md`'s `fork_point_firmware` field), asserted non-empty, asserted an
  ancestor of HEAD (`git merge-base --is-ancestor` → exit 0). The cumulative
  `git diff --stat "$FORK"..HEAD -- src include platformio.ini .github test` produced **empty
  output**; `git status --porcelain -- src include platformio.ini .github test` was also empty.
- **The anti-regression guard on the claim mechanism itself:**
  `grep -rlE -e 'diff --stat +--[^a-zA-Z-]' -e 'diff --stat +--$' .../123-*/ --include='*-PLAN.md' | wc -l`
  → **0** — the vacuous ref-less `--stat` shape does not occur anywhere in this phase's own plan set.
- **Host:** the seven rekeyed proxy modules (`-rs`) → **49 passed**, 0 skipped. All eleven
  pre-existing cross-repo gate rows passed (4 tool invocations + 6 pytest module runs contributing
  7+5+6+4+13+2 = 37 individual test passes, plus the idempotence check on row 5).
  `check_no_exists_proxy.py` → PASS, 78 files scanned, exit 0. Full host suite
  `python3 -m pytest tests/` → **1158 passed**, 0 skipped (confirmed via `-rs`: zero `SKIPPED` lines
  anywhere). `ruff check` / `ruff format --check` / `check_mypy_watermark.py` all green (1 error,
  34 below the 35 watermark, unchanged).
- **Meta:** `test_check_permitted_claims.py` → **10 passed**. `check_permitted_claims.py` (no args)
  → `UNARMED:`, exit 0 (Phase 130's four closing artifacts don't exist yet).
- **Branch state, all three repos:** firmware and host both on `v1.23-py32f071-integration`
  (`34bda8c9...` / `ccbc401e...`); meta on `gsd/v1.23-py32f071-integration`. No file was created,
  modified or deleted by this task in any repo — `git status --porcelain` was empty in `firestarter`
  both before and after the sweep (including around `gen_sdp_bus_config.py`'s idempotence check),
  and `firestarter_app`'s status matched its recorded pre-existing dirt exactly
  (`M .gitignore`; untracked `.coverage`, `.planning/config.json`, `SECURITY.md`,
  `write_test_port.sh`).

No row failed. No baseline, watermark, floor, or allow-list was adjusted.

### Task 2 — `123-NONREGRESSION.md` (commit `620d0d7`)

Written mirroring `122-NONREGRESSION.md`'s shape: a header block pinning both sub-repos' branch/HEAD
and the recorded fork points, a re-execution pledge, and eight numbered sections (the claim as precise
statements; the BASE-01 baseline recorded-vs-observed; the full gate table; what is UNARMED and what
arms it; known-and-explained conditions; the cumulative no-firmware-code-moves proof; the validation
ceiling; deliberately-not-taken). 343 lines. Contains every required literal figure
(141/17/1158/48/49/23932/1573/23976/1579/26072/2014/360) and every required string (`not a regression`,
`pre-existing`, `local evidence`, `MERGE-06`, `PY32_EXCLUDED`, `flash_type_3`, `545`, `475`).

**One self-correction during authoring:** the first draft quoted REQUIREMENTS.md's forbidden-claim
list verbatim in §7 (the validation ceiling) — this tripped `check_permitted_claims.py`'s own
courtesy claim-scan (5 forbidden-phrase matches: `runs-on-py32`, `works-end-to-end`,
`silicon-verified`, `bench-validated`, `hardware-validated`), reproducing the exact self-referential
trap `122-NONREGRESSION.md`'s own §7 already hit and documented. Fixed by citing the forbidden list
by location (`REQUIREMENTS.md:14`) instead of reproducing its wording, per the same precedent — this
is the gate working as intended, not a defect to route around by weakening the pattern set. Re-ran
the claim gate after the fix: `PASS: scanned 123-NONREGRESSION.md; 1 file(s) carry the required
silicon caveat`, exit 0.

### Task 3 — requirement + roadmap closure (commit `466904b`)

Ticked all eight BASE checkboxes in `.planning/REQUIREMENTS.md` and the Traceability row
`BASE-01 … BASE-08 | Phase 123 | Complete`. Coverage counts (47 total / 47 mapped / 0 unmapped)
unaffected — no other row touched. `git diff HEAD -- REQUIREMENTS.md` shows exactly the 9 expected
changed lines (8 checkboxes + 1 traceability row).

Ticked the `123-11-PLAN.md` checkbox in `ROADMAP.md`'s Phase 123 Details block — the only remaining
unticked box, all 11 plan rows now `- [x]`. No objective text beside any box changed; no row added or
removed. `git diff --numstat HEAD -- ROADMAP.md` = 2 (1 line added, 1 removed — within the ≤30
ceiling); zero changed lines matching Phase 124-130 or any earlier milestone section. The Phase 123
Goal, Depends on, Requirements, Success Criteria, and `**Plans**:` header line are byte-unchanged, per
the plan's explicit instruction (that summary line is `roadmap.update-plan-progress`'s job in the
standard state-update step, not this task's). `.planning/STATE.md` was not touched by this plan.

## Per-requirement tick justification (citing `123-NONREGRESSION.md` rows)

| Requirement | `123-NONREGRESSION.md` row cited |
|---|---|
| **BASE-01** | §2 — the recorded-vs-observed AVR/native table, all figures reproduced byte-exact on a fresh clean rebuild this session |
| **BASE-02** | §1 item 2 + §3 host gate table row H10 (49 passed, 0 skipped — the seven rekeyed proxy modules) |
| **BASE-03** | §1 item 3 + §3 row H11 (`test_skip_census.py`, part of the 16-passed run) |
| **BASE-04** | §4 verbatim `UNARMED:` line for `check_cmake_manifest.py` + §6's `PY32_EXCLUDED` format quote and the `flash_type_3.cpp`/`flash_type_4.cpp` first-firing hand-off |
| **BASE-05** | §4 verbatim `UNARMED:` line for `check_orphan_provisional.py` + §6's `RURP_PY32F071_PINMAP_PROVISIONAL` hand-off to MERGE-04 |
| **BASE-06** | §3 firmware gate rows F5a-F5c (AVR `macro_redefinition=0`) and F7a-F7b (native `total=360==watermark 360`) |
| **BASE-07** | §3 meta gate row M2 (`UNARMED:`, exit 0, D-15 all-or-nothing arming) + §1 item 1 |
| **BASE-08** | §1 item 4-5 (armed-on-arrival vs coarse-key-armed enumeration) + this plan's own Task 2 self-correction, which is itself proof the gate fires on a real drafting mistake, not only on planted fixtures |

## Task Commits

1. **Task 1: Full gate sweep** — no commit (measurement-only, no files written; verification-only
   per the plan's own `<files>` spec)
2. **Task 2: Write `123-NONREGRESSION.md`** — `620d0d7` (docs)
3. **Task 3: Tick BASE-01..BASE-08 + ROADMAP plan checkbox** — `466904b` (docs)

## Files Created/Modified

- `.planning/phases/123-non-regression-baselines-gate-hardening/123-NONREGRESSION.md` — the D-05
  evidence artifact (343 lines)
- `.planning/REQUIREMENTS.md` — BASE-01..BASE-08 checkboxes ticked; Traceability row → Complete
- `.planning/ROADMAP.md` — `123-11-PLAN.md` checkbox ticked (11/11 plan rows now `- [x]`)

## Fork-point proof, verbatim (for the operator's own re-verification)

```
FORK=5c9160a34b665878b05403ab014b959926feb6bf   # from 123-01-SUMMARY.md's fork_point_firmware
test -n "$FORK"                                  # exit 0
git -C /workspaces/firestarter merge-base --is-ancestor "$FORK" HEAD   # exit 0
git -C /workspaces/firestarter diff --stat "$FORK"..HEAD -- src include platformio.ini .github test
# (empty)
git -C /workspaces/firestarter status --porcelain -- src include platformio.ini .github test
# (empty)
grep -rlE -e 'diff --stat +--[^a-zA-Z-]' -e 'diff --stat +--$' \
  /workspaces/.planning/phases/123-non-regression-baselines-gate-hardening/ --include='*-PLAN.md' | wc -l
# 0
```

## Branch state at phase end

| Repo | Branch | HEAD SHA |
|---|---|---|
| `firestarter` | `v1.23-py32f071-integration` | `34bda8c9b473c3f19f7dd722d7ccadc2ae74fd77` |
| `firestarter_app` | `v1.23-py32f071-integration` | `ccbc401e16e2d2298f7376c3086164700bba0278` |
| meta (`/workspaces`) | `gsd/v1.23-py32f071-integration` | `466904b53279bee490d9c258cfb0572cddb24931` (after this plan's two commits) |

## What `.planning/STATE.md` will need to say (for the operator to verify, not assume)

- `current_phase`: still `123` until the orchestrator's own phase-completion step advances it to `124`
  (this plan does not touch STATE.md by design — see Decisions)
- Phase 123 status: complete, **11/11 plans executed** (was 10/11 before this plan)
- `progress.completed_plans`: should become 11 (was 10)
- Last activity: executed 123-11 (full cross-repo gate sweep + `123-NONREGRESSION.md` + BASE-01..08 tick)
- Decisions to add: the two key-decisions in this SUMMARY's frontmatter (cite-by-location fix; H5
  idempotence baseline reasoning)

## Decisions Made

See `key-decisions` in frontmatter. In brief: (1) cited REQUIREMENTS.md's forbidden-claim list by
location rather than quoting it verbatim, matching `122-NONREGRESSION.md`'s own precedent for this
exact self-referential trap; (2) recorded row H5's idempotence baseline as the empty string measured
in this session, not a copied non-empty baseline from a different phase's tree state; (3) left
ROADMAP's `**Plans**:` summary line byte-unchanged, per the plan's explicit instruction that this is
`roadmap.update-plan-progress`'s job.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] First draft of `123-NONREGRESSION.md` §7 tripped its own courtesy claim-scan**
- **Found during:** Task 2, running the plan's own mandated courtesy claim-scan step
- **Issue:** Quoting `REQUIREMENTS.md`'s eight-phrase forbidden-claim list verbatim in the validation-
  ceiling section matched five of the scanner's own `FORBIDDEN_PATTERNS` entries — the same
  self-referential trap `122-NONREGRESSION.md`'s own §7 documented and worked around.
- **Fix:** Reworded §7 to cite the forbidden list by location (`REQUIREMENTS.md:14`) rather than
  reproduce its wording, following `122-NONREGRESSION.md`'s exact precedent and explaining why in the
  same paragraph.
- **Files modified:** `.planning/phases/123-non-regression-baselines-gate-hardening/123-NONREGRESSION.md`
  (not yet committed at the time of the fix — folded into Task 2's single commit).
- **Verification:** Re-ran `FIRESTARTER_CLAIMSCAN_TARGETS=... python3 check_permitted_claims.py` →
  `PASS`, exit 0. Re-verified all 20 required literal strings/figures still present after the edit;
  line count still ≥ 120 (343 lines).
- **Committed in:** `620d0d7` (Task 2's only commit — caught before commit, not a follow-up)

---

**Total deviations:** 1 auto-fixed (Rule 1, self-referential wording collision with the plan's own
claim-scan gate — no scope creep, no behavioral change to any checker).
**Impact on plan:** None on the sweep's findings or the requirement ticks. The self-correction is
itself evidence the claim gate fires correctly on a real drafting mistake, which strengthens rather
than weakens this plan's own honesty claim.

## Issues Encountered

None beyond the one auto-fixed deviation above.

## User Setup Required

None — no external service configuration required.

## Explicit statement: nothing pushed, nothing published, nowhere commented

This plan pushed nothing (`git push` never invoked in any repo), invoked no `gh` command, created no
tag, and bumped no gitlink. `git status --porcelain` in the meta repo shows only the pre-existing
`firestarter_app` gitlink `-dirty` marker (reflecting that sub-repo's own pre-existing untracked/
modified files, unrelated to this plan's commits) — no new push-worthy state exists anywhere. Phase
130 owns every outward-facing action for this milestone.

## Next Phase Readiness

- Phase 123 is now fully verified and requirement-complete: BASE-01 through BASE-08 all Complete,
  11/11 plans shipped, `123-NONREGRESSION.md` committed as the phase's canonical evidence artifact.
- Phase 124 can read `123-NONREGRESSION.md` directly for MERGE-05 (baseline figures), MERGE-06 (native
  case/suite counts — both envs agree, no amendment needed), and MERGE-07 (the nine-gate/eleven-row
  evidence, local not CI) without recomputing anything.
- Phase 124's first moves are pre-armed: `check_cmake_manifest.py` will fire on the
  `flash_type_3.cpp`/`flash_type_4.cpp` rename the instant `platform/py32f071/CMakeLists.txt` lands
  unchanged (MERGE-02), and `check_orphan_provisional.py` will fire on
  `RURP_PY32F071_PINMAP_PROVISIONAL`'s zero-consumer state (MERGE-04).
- No blockers. All three repos on their expected branches; meta HEAD at `466904b5...`.

---
*Phase: 123-non-regression-baselines-gate-hardening*
*Completed: 2026-07-31*

## Self-Check: PASSED

- FOUND: `/workspaces/.planning/phases/123-non-regression-baselines-gate-hardening/123-NONREGRESSION.md`
- FOUND commit `620d0d7` (meta, Task 2)
- FOUND commit `466904b` (meta, Task 3)
- Verified: meta on `gsd/v1.23-py32f071-integration`; firmware + host both on `v1.23-py32f071-integration`
- Verified: all 8 BASE checkboxes ticked in REQUIREMENTS.md, 0 remaining unticked
- Verified: ROADMAP Phase 123 Details block lists 11 plan rows, all `- [x]`
- Verified: `.planning/STATE.md` untouched by this plan (`git status --porcelain -- .planning/STATE.md` empty)
