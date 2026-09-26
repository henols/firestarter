---
phase: 179-uv-slot-writes-flag-skip-blank-check-hardware-gated
plan: 04
subsystem: dev-test-engine
tags: [uv-eprom, bench-measurement, hardware-gated, chip_test, firestarter_app, phase-seal]

requires:
  - phase: 179-uv-slot-writes-flag-skip-blank-check-hardware-gated (plan 01)
    provides: FLAG_SKIP_BLANK_CHECK on a proven monotonic UV masked write, the SKIPPED blank-check verdict adjudication
  - phase: 179-uv-slot-writes-flag-skip-blank-check-hardware-gated (plan 02)
    provides: uv-slot-write-pass registered in the frozen corpus, the host-side machine-checked form of criteria 1 and 2
  - phase: 179-uv-slot-writes-flag-skip-blank-check-hardware-gated (plan 03)
    provides: tests/test_chip_test_uv_slot_write.py, criterion 4's committed host half and criterion 3's witness-wins legs
provides:
  - "ROADMAP criterion 1 and 2's hardware half: a real ST M27C512 on a Leonardo (/dev/ttyACM0), holding data outside its top slot, accepted a slot write at 0xFF00 with overall_verdict == PASS and write/verify run_count == 2, recorded in 179-MEASUREMENT.md from the actual run"
  - "UV-01, UV-02 and UV-03 marked Complete in REQUIREMENTS.md, on the strength of the measured BENCH RESULT: PASS sentinel -- never on the host-only proof alone"
  - "Two prior planning claims FALSIFIED and repaired in place: PITFALLS.md's claimed hardware_refused abort mechanism (it never existed) and SUMMARY.md's prescribed probe-read string-equality witness form (it never matches a real run)"
  - "Three residuals filed as todos: the UV-02-forced ladder flip on exhausted slots (T-179-05), the Q5 write-shortcut disclosure key (deferred to Phase 181), and the Q8 stale-comment mid-line-boundary blocker"
  - "Phase 179 sealed: ROADMAP.md's four plan checkboxes ticked, every gate green in both repositories, phase_added_comments=0 across the whole phase"
affects: []

actuals:
  tokens: 9534
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "blocking-human bench checkpoint defended three ways at once: task type (human-action, not human-verify), gate attribute (blocking-human, never auto-approved), and a machine-checked artifact (measured hash/port/slot/exit-code that an auto-approval cannot fabricate)"
    - "sentinel-branched requirement marking: a single BENCH RESULT: line in a committed artifact is the sole input to which requirements a later task is entitled to mark Complete, never a judgement call at seal time"
    - "falsified prior claims repaired in place beside the superseded text, never deleted, following Phase 178's 835baba precedent"

key-files:
  created:
    - .planning/phases/179-uv-slot-writes-flag-skip-blank-check-hardware-gated/179-MEASUREMENT.md
    - .planning/phases/179-uv-slot-writes-flag-skip-blank-check-hardware-gated/evidence/179-04-phase-seal.txt
    - .planning/todos/pending/2026-09-08-uv-ladder-flip-on-exhausted-slots.md
    - .planning/todos/pending/2026-09-08-uv-write-shortcut-disclosure-key.md
  modified:
    - .planning/REQUIREMENTS.md
    - .planning/ROADMAP.md
    - .planning/research/PITFALLS.md
    - .planning/research/SUMMARY.md
    - .planning/todos/pending/2026-09-04-stale-uv-prompt-comment-in-cli-handlers.md

key-decisions:
  - "The operator's answered pre-flight questions (part confirmed on hand, Rev 2.0 shield stated verbatim as operator-stated not measured, two-slot budget accepted) and the Leonardo/ttyACM0 port swap were honored exactly as relayed by the continuation dispatch -- no re-asking, no re-deriving."
  - "The run produced PASS on the first and only attempt; the accepted spare slot was never spent, and no retry occurred."
  - "Two pre-existing false-positive collisions in the plan's own <verify> regex (an un-anchored 'Plans:' match against an archived v1.3 phase, and an assumed colon-inside-bold format for Phase 178's Plans line that Phase 178 never used) were identified, confirmed pre-existing via git blame/git show against the pre-phase commit, and documented as deviations rather than silently worked around by touching unrelated ROADMAP sections."

requirements-completed: [UV-01, UV-02, UV-03]

coverage:
  - id: D1
    description: "A real ST M27C512 UV EPROM, holding data outside its top 256-byte slot, accepted a write to that slot on real hardware without being refused (ROADMAP criterion 1, hardware half)"
    requirement: "UV-01"
    verification:
      - kind: manual_procedural
        ref: ".planning/phases/179-uv-slot-writes-flag-skip-blank-check-hardware-gated/179-MEASUREMENT.md (write-partial verdict=OK, run_count=2, write_region_start=65280/0xFF00, exit=0)"
        status: pass
    human_judgment: false
  - id: D2
    description: "That same run's overall_verdict read PASS and its write/verify steps read run_count == 2, title [dev test] m27c512 -- PASS (dea6e2474d30) (ROADMAP criterion 2, hardware half)"
    requirement: "UV-02"
    verification:
      - kind: manual_procedural
        ref: ".planning/phases/179-uv-slot-writes-flag-skip-blank-check-hardware-gated/179-MEASUREMENT.md (title=[dev test] m27c512 -- PASS (dea6e2474d30), write run_count=2, verify run_count=2, blank-check=SKIPPED reason='Not blank, at 0x000000, v: 0x44' error_code=176, exit=0)"
        status: pass
    human_judgment: false
  - id: D3
    description: "UV-03's witness-form claim closes on real hardware too: the run's write_current_source read 'probe read (tranche 2/2)', matching the structural witness (not region_policy) that plans 179-01/03 proved in host tests"
    requirement: "UV-03"
    verification:
      - kind: manual_procedural
        ref: ".planning/phases/179-uv-slot-writes-flag-skip-blank-check-hardware-gated/179-MEASUREMENT.md (write_current_source='probe read (tranche 2/2)')"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test_uv_slot_write.py (179-03, 12/12 legs, host-side proof of criterion 3 in both disagreement directions)"
        status: pass
    human_judgment: false
  - id: D4
    description: "The sentinel-branched requirement marking is honored exactly: UV-01/UV-02/UV-03 all read Complete because the sentinel is PASS, never marked on host-only proof alone"
    verification:
      - kind: other
        ref: ".planning/phases/179-uv-slot-writes-flag-skip-blank-check-hardware-gated/evidence/179-04-phase-seal.txt (sentinel=PASS, uv01_ticked=1, uv02_ticked=1, uv03_ticked=1, uv_status_rows=3, uv_pending_rows=0)"
        status: pass
    human_judgment: false
  - id: D5
    description: "Every gate green in both repositories at phase close, with zero added source comments across the whole phase and both submodules porcelain-clean"
    verification:
      - kind: integration
        ref: ".planning/phases/179-uv-slot-writes-flag-skip-blank-check-hardware-gated/evidence/179-04-phase-seal.txt (8x rc=0, 2265 passed / 0 failed / 32 snapshots, phase_added_comments=0, cli_handlers_diff=0, plan_shapes_diff=0, firmware_diff=clean, app_tree=clean, chip_database_diff=clean)"
        status: pass
    human_judgment: false

duration: 50min
completed: 2026-09-08
status: complete
---

# Phase 179 Plan 04: Bench Wave and Phase Seal Summary

**A real ST M27C512 UV EPROM on a Leonardo, holding 16 bytes of data outside its top slot, accepted a slot write at `0xFF00` and reached `overall_verdict == PASS` with `run_count == 2` (title `[dev test] m27c512 — PASS (dea6e2474d30)`), closing the phase's hardware half — UV-01, UV-02 and UV-03 are now Complete, two falsified prior planning claims are repaired in place, three residuals are filed, and every gate is green in both repositories.**

## Performance

- **Duration:** 50 min (approx; continuation executor resuming a `blocking-human` bench checkpoint the operator had already answered and physically actioned, exact wall-clock not independently tracked)
- **Started:** 2026-09-08 (continuation dispatch, resuming Task 1's bench wave)
- **Completed:** 2026-09-08T07:52:57Z
- **Tasks:** 2
- **Files modified:** 5 modified, 4 created (all in the meta repo; this plan touches zero source or test files in either sub-repo)

## Accomplishments

- **Task 1 — the bench wave.** Port identity confirmed by command (`Current firmware version: 3.0.0b22, for controller: leonardo on port /dev/ttyACM0`) before driving anything; the offered `3.0.0b25` firmware update was declined and `fw --install` was never run. A pre-run read confirmed the part genuinely holds 16 bytes of non-`0xFF` data at `0x0000-0x000F`, outside the top slot, with the top slot (`0xFF00-0xFFFF`) itself blank and available. `firestarter -p /dev/ttyACM0 dev test m27c512` was run exactly once, two cycles, no `--fast`, exit code 0. Result: `write-partial` and `verify` both `OK` at `run_count == 2`; `blank-check` adjudicated `SKIPPED` with its finding intact (`reason="Not blank, at 0x000000, v: 0x44"`, `error_code=176`); title `[dev test] m27c512 — PASS (dea6e2474d30)`; write coverage `slot 0xFF00 (256 bytes)`. One slot of the accepted two-slot budget was spent; the spare was never needed. A post-run `fw` check confirmed the same board/port — no mid-session shuffle. `firestarter` submodule stayed porcelain-clean throughout. `179-MEASUREMENT.md` records every measured line the acceptance criteria name, plus the operator-stated Rev 2.0 shield identity labeled explicitly as operator-stated (not machine-confirmed — the run's own `hw_revision` telemetry happened to agree, from a pre-existing EEPROM override, and that is disclosed as a coincidence, not corroboration).
- **Task 2 — the seal.** `BENCH RESULT: PASS` → UV-01, UV-02 and UV-03 all ticked `- [x]` and set to `Complete` in `REQUIREMENTS.md`. `ROADMAP.md`'s Phase 179 block (`**Plans:** 4 plans`, already present from planning) had its four plan checkboxes ticked. Two falsified prior claims repaired in place, beside the superseded text, following Phase 178's `835baba` precedent: `PITFALLS.md`'s claimed `hardware_refused`-abort mechanism (measured: no such mechanism exists in `run_plan`'s dispatch path; the real pre-179-01 abort came from the write step's own firmware refusal) and `research/SUMMARY.md`'s prescribed `current_source == "probe read"` string-equality witness (measured: staged tranches carry `"probe read (tranche N/2)"`, which never matches that equality — Phase 179 used a structural boolean instead, now pinned by a dedicated regression test). Three residuals filed: two new todos (`uv-ladder-flip-on-exhausted-slots`, T-179-05; `uv-write-shortcut-disclosure-key`, Q5/A5 deferred to Phase 181) and one extension to the existing Q8 todo, recording the measured mid-line comment boundary that blocks a zero-comment-added fix. All eight gates green in both repositories; full suite `2265 passed, 0 failed, 32 snapshots passed`; `phase_added_comments=0` measured from the pre-phase sha `835baba` (not `HEAD~1`); `cli_handlers.py` and `plan_shapes.json` byte-unchanged across the whole phase; both submodules and `chip_database.json` porcelain-clean.

## Task Commits

Each task was committed atomically, in the meta repo (no sub-repo commits — this plan touches zero source or test files):

1. **Task 1: The bench wave** - `04c96de7` (feat, meta: `179-MEASUREMENT.md`)
2. **Task 2: Seal the phase** - `98289bdb` (feat, meta: `REQUIREMENTS.md`, `ROADMAP.md`, `PITFALLS.md`, `research/SUMMARY.md`, three todos, evidence file)

**Plan metadata:** committed separately (this SUMMARY.md + STATE.md).

## Files Created/Modified

- `.planning/phases/179-uv-slot-writes-flag-skip-blank-check-hardware-gated/179-MEASUREMENT.md` - the committed bench record (new)
- `.planning/phases/179-uv-slot-writes-flag-skip-blank-check-hardware-gated/evidence/179-04-phase-seal.txt` - measured phase-seal evidence (new)
- `.planning/todos/pending/2026-09-08-uv-ladder-flip-on-exhausted-slots.md` - T-179-05 residual (new)
- `.planning/todos/pending/2026-09-08-uv-write-shortcut-disclosure-key.md` - Q5/A5 residual, deferred to Phase 181 (new)
- `.planning/REQUIREMENTS.md` - UV-01/UV-02/UV-03 ticked and marked Complete (scoped edit)
- `.planning/ROADMAP.md` - Phase 179's four plan checkboxes ticked (scoped edit)
- `.planning/research/PITFALLS.md` - Pitfall 5 step 2's falsified abort mechanism repaired in place
- `.planning/research/SUMMARY.md` - the falsified probe-read string-equality witness form repaired in place
- `.planning/todos/pending/2026-09-04-stale-uv-prompt-comment-in-cli-handlers.md` - Q8's mid-line-boundary blocker appended

## Decisions Made

See `key-decisions` in frontmatter. In brief: the operator's relayed pre-flight answers and physical actions were honored exactly as given, the bench run passed on the first and only attempt (no retry, one spare slot unspent), and two pre-existing bugs in the plan's own `<verify>` regex were identified, confirmed pre-existing via `git blame`, and documented rather than worked around by touching unrelated ROADMAP.md sections.

## Flagged assumptions carried forward from `179-01-PLAN.md`

Per this plan's own Task 2 instruction, the three probe-surfaced flagged assumptions from `179-01-PLAN.md`'s spec-less probe arithmetic are carried into this phase record verbatim, so they leave the phase visible rather than expiring with the plan set:

- **UV-01, probe category `unclassified`.** The probe could not assign an edge category to "a UV part holding data outside the target slot accepts a slot write". Assumption taken: "accepts" means the FIRMWARE performs the write — `write_eprom` returns `True` and the step reports `VERDICT_OK` — and nothing weaker (a host-side skip of the pre-flight, a warning, a retry). If the operator reads "accepts" as also requiring `firestarter write -a 0x…` to stop being refused on the same part, that is a firmware+host change in a different phase (RESEARCH assumption A7) and this plan under-delivers. Surfaced, not resolved.
- **UV-02, probe category `unclassified`.** The probe could not assign an edge category to "`overall_verdict == "PASS"` with `run_count == 2`". Assumption taken: `run_count == 2` is the WRITE step's and the VERIFY step's, not the blank-check step's — `run_count` is per-step, and the blank-check's hard-coded `run_count=1` is correct because `OP_BLANK_CHECK` is not in `_REPEAT_POLICY_OPS`. If the operator reads UV-02 as requiring the blank-check step to run twice, that is a `_REPEAT_POLICY_OPS` change nobody has asked for. Surfaced, not resolved.
- **UV-03, probe category `encoding`** ("Whose definition of length/equality applies — bytes, code points, grapheme clusters, or normalized form?"). This is very likely a classification miss for this domain, and it is recorded as a flagged assumption rather than dropped for exactly that reason. There is no text in the witness: `WriteTarget.current` and `WriteTarget.pattern` are `bytes`, `mask_write_pattern` is a per-byte `&`, and `WriteTarget.__post_init__` compares `len(self.pattern)` against the region length in BYTES. Assumption taken: the byte domain is the only domain in play and no normalization question exists. Surfaced, not resolved.

(A fourth item from the same section — Q5, the report-disclosure key — is not repeated here verbatim; it is the residual already filed as `2026-09-08-uv-write-shortcut-disclosure-key.md` above.)

## Deviations from Plan

### Auto-fixed Issues

None — no code, test, or behavioral fix was needed. This plan touches only `.planning/` artifacts.

### Documented (not auto-fixed) — pre-existing bugs in the plan's own `<verify>` regex

**1. [Rule 1 - Bug, in the plan's authored verify script] `roadmap_plans` check counts an unrelated archived phase's line**
- **Found during:** Task 2's own verify leg, computing `roadmap_plans` from `.planning/ROADMAP.md`
- **Issue:** The `<verify>` script's `grep -cE '^\*\*Plans:\*\* 4 plans'` is not end-anchored, so it also matches `.planning/ROADMAP.md:4517` — `**Plans:** 4 plans (Wave 0 shipped; Waves 1-3 paused on bench hardware)`, a line from the ARCHIVED v1.3 milestone's Phase 12 section, dated 2026-05-20 (confirmed via `git blame`, commit `94338cff8`, and via `git show` at the pre-phase-179 commit `2137122b` — this line predates Phase 179 by over three months and is untouched by this plan). The regex expects exactly 1 match; it measures 2.
- **Fix:** Not applied — fixing would require either editing the un-anchored regex (out of this plan's scope, since it lives inside `179-04-PLAN.md`'s own text, not a `.planning/` artifact this plan owns) or touching the archived v1.3 section (explicitly forbidden: "every OTHER phase section in the file is byte-unchanged"). Verified manually instead: `grep -n '^\*\*Plans:\*\* 4 plans$'` (end-anchored) confirms exactly one match, at line 414, Phase 179's own block — the artifact itself is correct; only the un-anchored gate script produces a false count.
- **Verification:** `git blame -L 4517,4517 -- .planning/ROADMAP.md` → commit `94338cff8`, 2026-05-20, pre-dates this phase. `git show 2137122b:.planning/ROADMAP.md | sed -n '4517p'` → identical text, confirming the collision existed before this plan's first commit.
- **Committed in:** N/A (no fix — documented as a pre-existing gate defect, not fixed).

**2. [Rule 1 - Bug, in the plan's authored verify script] Phase 178 byte-unchanged check assumes the wrong `Plans:` format**
- **Found during:** Task 2's second `<verify>` leg, checking `sed -n '/^### Phase 178:/,/^### Phase 179:/p' .planning/ROADMAP.md | grep -qxF '**Plans:** 4 plans'`
- **Issue:** Phase 178's actual line reads `**Plans**: 4 plans` (colon OUTSIDE the bold markers) — the format ROADMAP.md used before Phase 179's own block introduced `**Plans:** 4 plans` (colon inside). The verify script's exact-string match assumes Phase 178 uses the same format Phase 179 does; it does not, and never has.
- **Fix:** Not applied — same reasoning as deviation 1: touching Phase 178's section is explicitly forbidden by this plan's own scope, and the mismatch is in the gate script's assumed string, not in ROADMAP.md's content.
- **Verification:** `git show 2137122b:.planning/ROADMAP.md | sed -n '/^### Phase 178:/,/^### Phase 179:/p'` shows the identical `**Plans**: 4 plans` line at the pre-phase-179 commit, confirming Phase 178's format predates this plan and was never touched by it.
- **Committed in:** N/A (no fix — documented as a pre-existing gate defect, not fixed).

---

**Total deviations:** 0 auto-fixed, 2 documented pre-existing gate-script defects (both confirmed via `git blame`/`git show` to predate this plan and to be outside this plan's edit scope). **Impact on plan:** none on the actual artifacts — `.planning/REQUIREMENTS.md` and `.planning/ROADMAP.md` are both correctly and exclusively scoped to Phase 179's own content, verified by direct `git diff` inspection (see Self-Check below) independent of the plan's own regex.

## Issues Encountered

None beyond the two documented gate-script defects above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 179 is fully closed: UV-01, UV-02 and UV-03 are all `Complete`. Criterion 4 (`D-179-1` Option A) is satisfied by both halves — `179-03`'s committed, unskipped regression module and this plan's committed bench artifact — neither standing in for the other.
- No blockers for Phase 180 (Read-Step Sampling, conditional on Phase 176's measurement) or Phase 181 (Report Fidelity), which do not depend on this phase's hardware bench work.
- Three residuals are now visible in `.planning/todos/pending/` for future phases to pick up: the ladder-flip guard (any phase touching `build_db_diff`), the write-shortcut disclosure key (explicitly named for Phase 181, alongside `RPT-A4`), and the Q8 stale-comment operator decision (rewrite vs. delete).
- `179-MEASUREMENT.md` and this SUMMARY together are the phase's complete hardware evidence trail; no further bench work is owed by Phase 179.

## Self-Check: PASSED

- `.planning/phases/179-uv-slot-writes-flag-skip-blank-check-hardware-gated/179-MEASUREMENT.md` exists and contains exactly one `BENCH RESULT: PASS` line: confirmed.
- Commits `04c96de7`, `98289bdb` found in `git log --oneline --all`: confirmed.
- `git diff` on `.planning/REQUIREMENTS.md` and `.planning/ROADMAP.md` (against the pre-plan commit `2137122b`) shows edits confined exactly to the UV-01/02/03 lines and rows, and Phase 179's four plan checkboxes — re-verified directly, independent of the plan's own two flagged verify-regex defects.
- All Task 1 `<acceptance_criteria>` re-verified against the committed `179-MEASUREMENT.md`: all pass (verified via the plan's own automated `<verify>` command, TASK1_VERIFY=PASS).
- Task 2's `<acceptance_criteria>` re-verified: 23/25 automated checks in the plan's own script pass; the 2 that do not are the pre-existing gate-script defects documented above, confirmed via `git blame`/`git show` to predate this plan.
- Full suite: `2265 passed, 0 failed, 32 snapshots passed`. `phase_added_comments=0`, `cli_handlers_diff=0`, `plan_shapes_diff=0`, `firmware_diff=clean`, `app_tree=clean`, `chip_database_diff=clean` — all measured this session in `evidence/179-04-phase-seal.txt`.

---
*Phase: 179-uv-slot-writes-flag-skip-blank-check-hardware-gated*
*Completed: 2026-09-08*
