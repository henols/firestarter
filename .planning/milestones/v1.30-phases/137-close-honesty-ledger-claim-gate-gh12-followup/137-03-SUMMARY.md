---
phase: 137-close-honesty-ledger-claim-gate-gh12-followup
plan: 03
subsystem: testing
tags: [honesty-ledger, claim-gate, sdp, v1.30, close]

# Dependency graph
requires:
  - phase: 137-01
    provides: "check_permitted_claims.py — the v1.30 claim gate 137-LEDGER.md must scan clean against, via the FIRESTARTER_CLAIMSCAN_TARGETS_V130 env seam"
  - phase: 134-the-plan-derived-sdp-oracle-in-dev-test
    provides: "134-RECORD.md §1/§3/§4/§5/§6/§7 — the source for six of this ledger's nine milestone-level corrections"
  - phase: 136.1-sdp-partition-provenance
    provides: "136.1-RECORD.md Finding 1 (PROV-05 already-satisfied premise) and Finding 5 (the 'committed NOTHING' process failure)"
provides:
  - "137-LEDGER.md: the v1.30 honesty ledger, one of check_permitted_claims.py's four default scan targets, now ARMED for the first time"
  - "11 claim classes each paired with a permitted wording, a measured/re-run evidence citation, and an explicit non-claim"
  - "9 milestone-level corrections carried forward from Phase 133/134/136.1 phase records into one outward-visible document"
  - "3 process failures recorded plainly, not only technical/code defects"
affects: [137-06 (re-runs the claim gate with no arguments once all four artifacts exist; ticks CLOSE-01)]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Honesty-ledger seven-section shape forked from 122-LEDGER.md: header/composes-with, ceiling-quoted-verbatim, status key, claim classes table, mechanism corrections, process failures + negative space, closing three-way split"
    - "Claim-gate-safe citation of a forbidden phrase: cite by reference ('quoted in full above') rather than repeat verbatim a second time near an SDP-context token, when the scanner's proximity window would otherwise flag the citation as an assertion"

key-files:
  created:
    - .planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/137-LEDGER.md
  modified:
    - .planning/REQUIREMENTS.md

key-decisions:
  - "Expanded the claim-classes table to 11 rows (beyond the plan's own minimum-10 spec) to also carry PROV-01...06's provenance-not-verdicts framing (136.1-RECORD.md §5's 'no ICs refused' operator-request narrative) as its own citable class, per the orchestrator's fuller nine-correction/three-process-failure objective"
  - "When the claim gate flagged a genuine forbidden-phrase co-occurrence (the ceiling's own causal claim, restated near the phrase 'AT28C part' in the closing three-way split), reworded the flagged sentence to cite the earlier verbatim quote by reference rather than repeat it a second time near an SDP-context token -- the same discipline 122-LEDGER.md's own header note already names for its own equivalent citation. The factual content (the causal claim is not provable, quoted once in full higher up the document) is unchanged; only the second, redundant restatement was removed."

requirements-completed: [CLOSE-04]

coverage:
  - id: D1
    description: "137-LEDGER.md exists, follows the seven-section shape, and contains all mandated content: both Evidence Ceiling narrowings verbatim, 11 claim classes, 7 condensed mechanism corrections, 3 process failures, negative space (incl. operator-batch C-1/C-3), and the closing three-way split"
    requirement: "CLOSE-04"
    verification:
      - kind: unit
        ref: "grep checks: 'no AT28C silicon was tested' / six-step / P-21 test name / '703' / 'c3c9424' all present"
        status: pass
    human_judgment: false
  - id: D2
    description: "Every re-measurable figure was re-measured live this plan against firestarter_app HEAD cc036e8, not copied from a citation"
    requirement: "CLOSE-04"
    verification:
      - kind: unit
        ref: "live pytest + live DB re-derivation + live grep, see Re-Measurements section below"
        status: pass
    human_judgment: false
  - id: D3
    description: "137-LEDGER.md scans clean, alone, against plan 137-01's claim gate via the env-override seam"
    requirement: "CLOSE-04"
    verification:
      - kind: unit
        ref: "FIRESTARTER_CLAIMSCAN_TARGETS_V130=137-LEDGER.md python3 check_permitted_claims.py -> PASS: scanned 137-LEDGER.md"
        status: pass
    human_judgment: false

# Metrics
duration: 45min
completed: 2026-08-05
status: complete
---

# Phase 137 Plan 03: The v1.30 Honesty Ledger (CLOSE-04) Summary

**Authored `137-LEDGER.md` — the milestone's central closing artifact — pairing 11 permitted claims with their explicit non-claims, carrying forward all nine of the milestone's own measured-wrong corrections and three process failures into one outward-visible document, every figure re-measured live rather than copied from a citation.**

## Performance

- **Duration:** ~45 min
- **Started:** 2026-08-05T18:07:00Z (context read)
- **Completed:** 2026-08-05T18:55:00Z
- **Tasks:** 2 (both `type="auto"`, converged on one artifact — see Task Commits)
- **Files modified:** 2 (`137-LEDGER.md` created, `REQUIREMENTS.md` edited)

## Accomplishments

- `137-LEDGER.md` authored, forking `122-LEDGER.md`'s seven-section shape: header + composes-with,
  the ceiling quoted verbatim (both named narrowings), the status/claim key, an 11-row claim classes
  table, a 7-item condensed mechanism-corrections section, a 3-item process-failures section, negative
  space (including operator-batch C-1/C-3), and the closing mechanical/operator-review/
  inherently-unverifiable three-way split.
- All six PLAN.md-mandated corrections present and cited by name: the six-step (not four-step) SDP
  leg, the exit-code precedence bug (marginal outranking BAD, fixed by D-14/134-05), the seven (not
  six) laundering routes, the chip-ID gate's structural vacuity for all 43 ALLOW chips, LEG-02's
  703-chip (not 41-chip) tested population, and PROV-05's premise already satisfied by Phase 121
  commit `c3c9424`.
- Three additional corrections carried into the ledger per this plan's fuller orchestrator-level
  objective: the `n_ran=6` (not `5`) banner discrepancy, Phase 133's own registry-count correction
  (6 policed + 6 declared non-registries, not "eight"), and the genuine coverage reduction 137-02
  itself shipped (checked files 132 -> 129, still above the 120 floor).
- Three process failures recorded plainly, per this plan's own instruction that a ledger admitting
  only code defects is not an honesty ledger: the "committed NOTHING" measured-from-`git-status`-alone
  incident (136.1-RECORD.md Finding 5), the AT28C64 "curation gap" misreading reproduced from
  part-number familiarity (operator-batch D-1), and `134-VALIDATION.md`'s approval asserting an
  artifact did not exist while a concurrent session had already committed it minutes later.
- CLOSE-04 ticked in `REQUIREMENTS.md`, traceability row updated to Complete. Project-wide requirement
  state: **52 ticked / 4 open** (CLOSE-01, CLOSE-05, CLOSE-06, RELOCK-07 remain — all later Phase 137
  plans' own scope).

## Re-Measurements (live, this plan, 2026-08-05, against `firestarter_app` HEAD `cc036e8`)

Per this plan's own Task 2 mandate ("re-measure every re-measurable figure fresh... do not claim
re-measurement you did not perform"), every bullet below was actually run this plan, from
`/workspaces/firestarter_app`, using `tools/ci_replica_venv.sh`'s numpy-free venv (never the
devcontainer's ambient Python 3.12), with `-o addopts=""` on every pytest invocation.

**1. `git -C /workspaces/firestarter_app rev-parse HEAD`:**
```
cc036e8dc3cd77bbdfc7ec5190d79cdb172153c7
```
Confirmed the current tip — unchanged from the value 137-02's own final commit already recorded in
the meta repo's tracked gitlink (`git ls-tree HEAD firestarter_app`), and unchanged again after this
plan's own commits (this plan touches no file inside `firestarter_app`).

**2. `derive_plan` ALLOW/REFUSE population — live DB re-derivation (fresh Python pass, not test-only):**
```
ALLOW: 43
REFUSE: 703
TOTAL DB: 746
0x0D total: 84
0x0D ALLOW: 43
0x0D REFUSE: 41
```
Confirms both citations simultaneously: the full-DB REFUSE population LEG-02's test actually covers
(703, a superset of 41) and the protocol-0x0D-scoped 43/41/84 split the ROADMAP names. Paired pytest
run: `pytest tests/test_chip_test_sdp_leg.py -k "test_derive_plan_allow_population_emits_six_supported_ops or test_derive_plan_refuse_population_emits_six_na_steps_with_reason or test_all_sdp_allow_chips_have_zero_chip_id_measured_live" -o addopts="" -q` -> `2 passed, 77 deselected in 1.17s` (the third selector lives in `test_dev_test_cmd.py`, run separately below).

**3. Chip-ID-zero test for all 43 ALLOW chips:**
```
$ pytest tests/test_dev_test_cmd.py -k "test_all_sdp_allow_chips_have_zero_chip_id_measured_live" -o addopts="" -q
1 passed, 50 deselected in 0.25s
```
Independently re-derived outside the test too: a fresh pass over every ALLOW-classified DB entry
found **zero** chips with a nonzero `chip-id` (`ALLOW chips with nonzero chip-id: []`).
`grep -rniE "gated by chip[- ]id" firestarter/ tests/` returns **0** hits tree-wide.

**4. `tools/ci_replica_venv.sh` full run (all 5 legs):**
```
Leg 1 (venv create-or-reuse + install): exit 0
Leg 2 (numpy absent):                   exit 0
Leg 3 (ruff check + format --check):    exit 0
Leg 4 (mypy watermark gate):             exit 0
Leg 5 (pytest --cov, CI's exact args):   exit 0
CI-REPLICA: PASS
```
Leg 4's own completion clause, captured separately (the `tail -80` in the background run truncated
it): `Found 33 errors in 13 files (checked 129 source files)` -- **mypy 33/35, headroom 2**, **checked
129** (above the `MIN_CHECKED_SOURCE_FILES = 120` floor; down from 132 at Phase 136.1's own close, per
plan 137-02's `tests/fixtures/` mypy exclude -- a genuine, already-disclosed reduction, not a new
finding this plan made). Leg 5's full suite: **1508 passed** (30 snapshots), coverage **82.14%**
(>=70% floor) -- reconciled against the 1504 baseline cited in `136.1-CI-PARITY.md`: **+4**, exactly
plan 137-02's own four new tests; this plan (137-03) adds zero new tests (it is a documentation-only
plan) so the count is unchanged by this plan's own work.

**5. `grep -c '^- \[x\] \*\*LEG-' .planning/REQUIREMENTS.md`:**
```
18
```
Unchanged from Phase 134's close, as expected -- this plan touches zero `LEG-*` rows.

**6. Additional live re-confirmations beyond the plan's own five named bullets, run because the
ledger's claim classes cite them directly:**
- `pytest tests/test_dev_test_cmd.py -k "test_leaked_lock_exits_1 or test_mixed_bad_and_marginal_exits_1_not_2" -o addopts="" -q` -> `2 passed, 49 deselected in 2.79s` (claim class 3/4).
- `pytest tests/test_chip_test.py -k "count_applicable_sdp" -o addopts="" -q` -> `3 passed, 106 deselected in 0.13s`, confirming `m_applicable=10`, `n_ran=6` live (mechanism correction 6).
- `_EXIT_CODE_PRECEDENCE: tuple[int, ...] = (1, 2, 0)` read directly at `cli_handlers.py:2026` (claim class 4).
- `skip_sdp_unlock: bool = False` read directly at `cli_handlers.py:319`, inside `_build_op_flags` (claim class 8 / P-21).
- `test_dev_sdp_removal_is_safe_only_because_auto_unlock_is_default_on` re-read at
  `tests/test_write_skip_sdp_unlock.py:328-395` (claim class 8 / P-21 exact test name).
- `pyproject.toml:173` `[tool.mypy] exclude = ["^tests/fixtures/"]` confirmed present (mechanism
  correction 7, the coverage reduction).
- `git status --porcelain -- .planning/v1.16/ledger/` -> empty (PROTOCOL-LEDGER.md untouched, matching
  v1.22's D-09 discipline).
- `grep -rniE "lock inhibited the write|proven on silicon|silicon-proven" firestarter/ tests/ .planning/`
  -> 3 hits, all three read in full context and confirmed to be **disclaiming** usages ("...is NOT
  provable this milestone"), zero affirmative overclaims tree-wide.

## Corrections Made In Place (per Task 2's reconciliation mandate)

Two corrections were made during this plan's own drafting/scanning/review cycle. Every cited figure
agreed with its live re-measurement on the first pass (see Re-Measurements above) — neither
correction below stems from a citation disagreeing with a fresh number; the first is a claim-gate
compliance fix, the second a self-caught timeline error found on final review, before this plan
reported itself done.

- **The closing three-way split's third bullet** originally repeated the Evidence Ceiling's own
  forbidden-phrase shape ("the causal claim 'the lock inhibited the write'") a second time, in a
  sentence whose immediate surrounding window also named "an AT28C part" — tripping
  `check_permitted_claims.py`'s proximity-scoped `lock-inhibited-the-write` pattern. This is the exact
  hazard `122-LEDGER.md`'s own header note names for its own equivalent citation ("this ledger does
  not repeat that sentence's exact wording: doing so would trip this same document's own claim
  scanner... That is the gate working as intended, not a defect to route around"). Reworded to cite
  the earlier verbatim quote by reference instead of restating it a second time — the factual content
  (the causal claim is not provable this milestone) is unchanged and remains quoted in full, once,
  earlier in the document; only the redundant second restatement, sitting next to a triggering
  context token, was removed. Re-scanned clean immediately after (commit `228dc4b1`).
- **The negative-space mypy-headroom bullet** originally claimed headroom was "unmoved across Phases
  132 through 137." Re-checked against the very phase records this ledger cites elsewhere:
  `132-RECORD.md` residual 2 states **32/35** (3 of headroom) at Phase 132's own close;
  `133-RECORD.md` residual 4 states the count moved to **33/35** (2 of headroom) **during Phase 133**.
  So headroom has been unmoved **since Phase 133**, not since Phase 132 — a self-caught inconsistency
  against this ledger's own cited sources, corrected in place before reporting this plan complete
  (commit `228dc4b1`).

## Task Commits

Both of this plan's tasks converge on one artifact (`137-LEDGER.md`); Task 1's draft and Task 2's
re-measurement + in-place correction were committed together as the validated final state, plus a
separate commit ticking the requirement:

1. **Tasks 1+2: Author + re-measure + validate `137-LEDGER.md`** - `3fedc9b8` (docs)
2. **Tick CLOSE-04 in `REQUIREMENTS.md`** - `4a0d2a17` (docs)
3. **SUMMARY + STATE.md/ROADMAP.md updates** - `b23dec27`, `3bddb191` (docs)
4. **Self-caught mypy-headroom timeline fix in the ledger (final review)** - `228dc4b1` (fix)

**Plan metadata:** (this commit, following SUMMARY write)

## Files Created/Modified

- `.planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/137-LEDGER.md` - the v1.30
  honesty ledger, one of `check_permitted_claims.py`'s four default scan targets, now armed for the
  first time (1 of 4 artifacts present; still `FAIL:` not `PASS:` under a no-argument run until
  137-04/137-05 author the remaining three — expected and correct at this wave).
- `.planning/REQUIREMENTS.md` - CLOSE-04 ticked `[x]` with evidence citation; traceability table row
  updated to Complete. No other requirement checkbox touched (52 ticked / 4 open, confirmed by direct
  grep count both before and after this plan's edit: 51/5 -> 52/4).

## Decisions Made

- Expanded the claim-classes table to 11 rows rather than the plan's own literal minimum of 10, to
  also carry the PROV-01...06 "provenance, not verdicts" framing (136.1-RECORD.md §5's "no ICs
  refused" operator-request narrative) as its own citable class — the orchestrator's own fuller
  objective named this as one of nine milestone-level corrections that must reach the ledger.
- When the claim gate flagged a genuine forbidden-phrase co-occurrence, reworded the flagged sentence
  to cite the earlier verbatim quote by reference rather than delete or soften the underlying finding
  — per this plan's own instruction ("if the gate flags something true, fix the claim, not the gate").

## Deviations from Plan

None requiring a rule beyond ordinary drafting-then-scanning iteration. The one correction (see
"Corrections Made In Place" above) is exactly the reconciliation loop Task 2's own action text
describes ("read the FAIL bucket, reword the flagged sentence... and re-run until green") — not a
deviation from the plan, its literal execution.

## Known Stubs

None. `137-LEDGER.md` is a complete, fully-cited document; no placeholder text, no unwired data,
no hardcoded-empty claim rows.

## Threat Flags

None. This plan introduces no new network endpoint, auth path, file-access pattern, or schema change
at a trust boundary — it authors one Markdown document inside its own phase directory and edits one
requirement checkbox. Matches this plan's own threat-model register (T-137-09/10/11 all `mitigate`,
T-137-SC `accept`, none newly discovered).

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `137-LEDGER.md` exists, is armed as one of the claim gate's four default targets, and scans clean
  alone. It will remain `FAIL:` (not yet the real `PASS:`) under a no-argument run of
  `check_permitted_claims.py` until 137-04 authors `137-RELEASE-NOTES-app.md` (and its own
  `137-DECISION.md`) and 137-05 authors `137-GH12-COMMENT.md` — expected and by design at this wave
  (the all-or-nothing arming branch only legitimately reports `UNARMED:` at zero-of-four; a
  one-of-four state correctly falls through to the ordinary fail-closed branch, which this plan's own
  scoped single-file scan via the env seam deliberately bypasses to test this artifact in isolation).
- `137-04` depends on this plan (`depends_on: ["137-03"]`) and owns `137-DECISION.md` (the C-1
  `build_db_diff`/`ladder_state` disposition this ledger's own negative-space section explicitly
  defers, by name, rather than inventing one here).
- CLOSE-04 is the only requirement this plan ticks. Project-wide requirement state after this plan:
  **52 ticked `[x]` / 4 open** (`CLOSE-01`, `CLOSE-05`, `CLOSE-06`, `RELOCK-07`) — confirmed by direct
  grep count, matching the mandated ticking scope exactly.

---
*Phase: 137-close-honesty-ledger-claim-gate-gh12-followup*
*Completed: 2026-08-05*

## Self-Check: PASSED

- FOUND: `.planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/137-LEDGER.md`
- FOUND commit `3fedc9b8` (Tasks 1+2)
- FOUND commit `4a0d2a17` (CLOSE-04 tick)
- Re-confirmed `FIRESTARTER_CLAIMSCAN_TARGETS_V130=137-LEDGER.md python3 check_permitted_claims.py` exits 0 with `PASS: scanned 137-LEDGER.md`
- Re-confirmed `grep -c '^- \[x\]' .planning/REQUIREMENTS.md` -> 52, `grep -c '^- \[ \]' .planning/REQUIREMENTS.md` -> 4
