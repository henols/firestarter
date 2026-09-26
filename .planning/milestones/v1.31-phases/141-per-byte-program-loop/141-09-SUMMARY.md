---
phase: 141-per-byte-program-loop
plan: 09
subsystem: testing
tags: [firmware, avr, platformio, eprom, requirements, phase-close, gh-15, firestarter]

# Dependency graph
requires:
  - phase: 141-per-byte-program-loop (141-04)
    provides: the rewritten per-byte pulse-to-verify eprom_write_execute, whose flash/RAM delta and trace cadence this plan measures
  - phase: 141-per-byte-program-loop (141-05)
    provides: the re-derived D-13 protocol-branch-inventory golden and the CLAUDE.md 0x0B energy-cap correction (99998us) this plan cites
  - phase: 141-per-byte-program-loop (141-07)
    provides: LOOP-01/04/06 native proof and the STROBE_KIND_DATA oracle finding this plan hands forward
  - phase: 141-per-byte-program-loop (141-08)
    provides: LOOP-03/05/07/08 native proof (39/39 in native_loop_v131), completing this phase's behavioural evidence base
provides:
  - "141-NEW-TRACE.md: the post-change v131 merged strobe+timing trace for all three protocols, the confirmed RED shape (D-10), and the honest non-claim that the determinism leg is structurally unreachable rather than 'still passing'"
  - "141-LOOP-RECORD.md: measured-vs-predicted flash/RAM, the MERGE-05 RED verdict recorded verbatim with the operator's pre-dispatch decision to accept it, the D-13 inventory movement (tier-2 grew, correcting D-11's own framing), LOOP-03's arithmetic-only non-claim, the traced hard-fails-the-block abort chain, the new message-ID band cost, the two orphaned catalog IDs, LOOP-06's protocol-scoped read-skip finding, the STROBE_KIND_DATA oracle finding, the 99998us energy-cap correction, the native envs' no-CI-leg obligation, and the unscoped-porcelain test-defect hand-off"
  - "All eight LOOP-01..08 requirements flipped to complete in REQUIREMENTS.md, in one 16-line hand edit"
affects: [142-high-voltage-routing, 143-host-integration, 144-test-and-baseline-reconciliation, 146-close]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Phase-close record mirrors 140-PARAM-TABLE-RECORD.md's house shape: numbered sections, a findings register with owners, an explicit what-this-is-not section, a hand-off table"
    - "Operator decisions made mid-orchestration (before a plan's own dispatch) are recorded as authoritative and are not re-litigated by the plan that inherits them, even when the plan's own action text describes a remediation ladder"
    - "REQUIREMENTS.md requirement flips done as a hand edit with a pre-edit snapshot and a diff assertion (exact line-count budget), never via a whole-file-reformatting automated verb"

key-files:
  created:
    - .planning/phases/141-per-byte-program-loop/141-NEW-TRACE.md
    - .planning/phases/141-per-byte-program-loop/141-LOOP-RECORD.md
  modified:
    - .planning/REQUIREMENTS.md

key-decisions:
  - "MERGE-05 stays RED, per an explicit operator decision recorded before this plan's dispatch ('Continue; 141-09 records it.') -- the plan's own action-text reduction ladder (payload shrink / verify_mode collapse / dead-function deletion) was deliberately NOT attempted, since running it would re-litigate a decision already closed by the operator. This is a documented deviation from the plan's literal Task 2 action text and automated verify expectation (exit 0), authorized by the orchestrating agent's own pre-measured verdict and explicit instruction to record faithfully rather than fix or soften."
  - "141-NEW-TRACE.md does not claim the trace determinism leg 'still passes' -- verified from source that Unity aborts each of the three failing protocol cases on the length-equality check, strictly before the determinism comparison ever executes. This corrects this plan's own frontmatter must_have wording rather than silently satisfying it with an inaccurate claim."
  - "141-LOOP-RECORD.md corrects 141-CONTEXT.md D-11's 'record the shrinkage' framing as a finding: tier-2 grew (21->24, +3), not shrank; only tier-1 held at exactly 3 is the actual invariant D-13 protects."
  - "Requirements flip executed as a hand edit (Edit tool), snapshot-and-diffed against a pre-edit copy, confirming exactly 16 changed lines and no other requirement family touched -- per this project's standing finding that gsd-tools' requirements/roadmap verbs reformat the whole file."

requirements-completed: [LOOP-01, LOOP-02, LOOP-03, LOOP-04, LOOP-05, LOOP-06, LOOP-07, LOOP-08]

coverage:
  - id: D1
    description: "141-NEW-TRACE.md captures the post-change v131 trace (all three protocols' banners and full entry lists), confirms native_trace_v131's RED shape matches the orchestrator's pre-measured verdict exactly, and states the determinism-leg unreachability honestly rather than claiming it passes"
    requirement: ""
    verification:
      - kind: other
        ref: "cd /workspaces/firestarter && pio test -e native_trace_v131 -- 6 test cases: 3 failed, 2 succeeded, matching the pre-dispatch verdict exactly"
        status: pass
      - kind: other
        ref: "two independent process invocations of .pio/build/native_trace_v131/firestarter_native diffed byte-identical"
        status: pass
    human_judgment: false
  - id: D2
    description: "141-LOOP-RECORD.md records the MERGE-05 RED verdict verbatim, the operator's pre-dispatch decision to accept it, and the avr-nm attribution of the flash overrun -- no reduction ladder attempted, no baseline JSON edited"
    requirement: ""
    verification:
      - kind: other
        ref: "cd /workspaces/firestarter && python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json --avr-log uno=... --avr-log uno328pb=... --avr-log leonardo=... -- exit 1, FAIL lines matching this record's §1.2 verbatim"
        status: fail
      - kind: other
        ref: "git -C /workspaces/firestarter status --porcelain scripts/baseline/ -- empty"
        status: pass
    human_judgment: true
    rationale: "The MERGE-05 gate itself reports FAIL by design (operator decision to accept the RED, not a defect this plan could or should resolve). A human should confirm the record's framing of that RED (attribution, prediction-miss analysis, and the explicit non-remediation) is honest and complete, since the deterministic classifier cannot distinguish 'RED correctly recorded per an out-of-band operator decision' from 'RED because the plan failed its own gate.'"
  - id: D3
    description: "All eight LOOP-01..08 requirements flipped to Complete in REQUIREMENTS.md, verified by diff to touch exactly 16 lines and no other requirement family"
    requirement: "LOOP-01,LOOP-02,LOOP-03,LOOP-04,LOOP-05,LOOP-06,LOOP-07,LOOP-08"
    verification:
      - kind: other
        ref: "diff -u /tmp/.../REQ.before.md .planning/REQUIREMENTS.md -- exactly 16 lines changed (8 checkboxes + 8 coverage rows)"
        status: pass
      - kind: other
        ref: "python3 -c \"... assert done == ['LOOP-01'..'LOOP-08']; assert pend == []\" -- OK phase record complete; 8 LOOP requirements marked complete"
        status: pass
    human_judgment: false

duration: ~2h (approx -- see Issues Encountered)
completed: 2026-08-10
status: complete
---

# Phase 141 Plan 09: Phase Close — Trace Capture, Flash/RAM Reconciliation, Requirement Flip Summary

**Captured the post-change v131 trace as a committed artifact, measured flash/RAM cold against the pre-committed prediction and recorded MERGE-05's RED verdict verbatim (operator decision: accepted, not remediated), wrote the phase's non-claims and hand-offs into 141-LOOP-RECORD.md, and flipped all eight LOOP-01..08 requirements in one 16-line hand edit.**

## Performance

- **Duration:** ~2h (approx — see Issues Encountered)
- **Completed:** 2026-08-10T23:18:14Z
- **Tasks:** 3
- **Files modified:** 3 (2 created, 1 modified) — all in the meta repo

## Accomplishments

- `141-NEW-TRACE.md` (292 lines): exact build/run commands, all three protocol banners (`total=91/119/59`,
  `strobe_overflow=0`, `timing_overflow=0` on every protocol), the complete merged entry list per
  protocol, the confirmed RED shape (compiled cleanly, `RESPONSE_CODE_OK` passes, the sole failure is
  the length-equality check with no divergent index ever computed since Unity aborts before reaching
  it), the honest non-claim that the determinism leg is structurally unreachable rather than "still
  passing," and the byte-level cadence walk against the synthetic fixture (byte 0: already-matching
  skip, 0 pulses; byte 1: `0xFF` skip, 0 pulses/0 reads; byte 2: 2 pulses; byte 3: 1 pulse — versus the
  old loop's 7 pulses across 3 passes).
- `141-LOOP-RECORD.md` (521 lines): the full measured-versus-predicted table (flash overrun ~14x the
  point estimate, attributed via `avr-nm` to Phase 140's parameter table finally being paid for at
  first live reference), the MERGE-05 RED recorded verbatim with the operator's pre-dispatch decision
  to accept it, the D-13 inventory movement (tier-2 grew 21→24, correcting D-11's "shrinkage" framing
  as a finding), LOOP-03's arithmetic-only non-claim, the traced "hard-fails the block" abort chain
  (`eprom_operations.cpp:115-117` → `firestarter.cpp:284-286`'s `command_done()`), the new message-ID
  band cost (`0xBF` is the ERROR band's only remaining free slot; `MSG_ERR_WRITE_FAILED` is now
  emitted by nothing on the 27C path), the two orphaned catalog IDs (left assigned, not deleted),
  LOOP-06's protocol-scoped read-skip finding, the `STROBE_KIND_DATA` oracle finding, the corrected
  99998µs (not 99999µs) energy-cap worst case, the three non-CI native envs' run-by-name obligation,
  an orphaned-defect hand-off for the unscoped porcelain check in `test_flash_path_record_sync.py`,
  a full hand-offs table (6 items, to Phases 142/143/144/146), the D-15 planted-RED tally (13 runs
  across 141-05/06/08, exceeding Phase 140's 12), and a findings register (13 entries).
- Cold-remeasured flash/RAM for all three AVR targets independently — matched the orchestrator's
  pre-dispatch figures exactly (uno 24424/1573, uno328pb 24474/1579, leonardo 26400/2014) — and
  independently re-ran `check_size_baseline.py --policy merge05` (exit 1, identical FAIL lines) and
  `check_build_warnings.py --rebuild` (exit 0, watermark holds at 1166 with zero headroom on both
  pinned native envs, exact-zero macro-redefinition on all three AVR targets).
- Flipped all eight `LOOP-01`..`LOOP-08` requirements to `[x]`/`Complete` in `.planning/REQUIREMENTS.md`
  via a hand edit, snapshot-and-diffed against a pre-edit copy: exactly 16 lines changed (8 checkboxes
  + 8 coverage rows), no `VPP-*`/`HOST-*`/`TEST-*`/`BENCH-*`/`CLOSE-*` row touched.
- Confirmed the phase's full evidence base remains green at close: `native`/`native_nodevtools`
  141/17 each; `native_loop_v131` 39/39; `native_params_v131` 9/9; `pytest tests/` 256/256; all three
  AVR targets build SUCCESS. `native_trace_v131` remains the **one** expected non-green (3 failed, 2
  succeeded), named as expected throughout this plan's own artifacts.
- No file under `/workspaces/firestarter` was modified by this plan — confirmed `git -C
  /workspaces/firestarter status --porcelain` empty before, during, and after every task.

## Task Commits

Each task was committed atomically, in the meta repo, on branch `gsd/v1.31-27c-programming-algorithm-fidelity`:

1. **Task 1: Capture the post-change trace and confirm the RED's shape** - `cdc81c22` (docs)
2. **Task 2: Measure flash/RAM against the committed prediction and record the MERGE-05 verdict** - `be45605a` (docs)
3. **Task 3: Write the phase record's non-claims/hand-offs, then flip all eight requirements** - `cc71d38b` (docs)

**Plan metadata:** this SUMMARY + STATE.md/ROADMAP.md (committed separately, per the execution protocol).

## Files Created/Modified

- `.planning/phases/141-per-byte-program-loop/141-NEW-TRACE.md` (new) - the post-change trace, both
  sides of Phase 144 / TEST-06's diff
- `.planning/phases/141-per-byte-program-loop/141-LOOP-RECORD.md` (new) - the phase-close record:
  measurements, non-claims, hand-offs, findings register
- `.planning/REQUIREMENTS.md` (modified) - LOOP-01..08 flipped, 16 lines changed exactly

## Decisions Made

See `key-decisions` in the frontmatter for the full list. Summarized:
1. **MERGE-05 stays RED** — the operator's own pre-dispatch decision, inherited and recorded rather
   than re-litigated. This plan did not attempt the plan's own action-text reduction ladder.
2. **The determinism-leg wording in this plan's own frontmatter must_have was not satisfied literally**
   — it was corrected against measured reality (the leg is structurally unreachable, not "still
   passing") rather than satisfied by an inaccurate claim.
3. **D-11's "record the shrinkage" framing was corrected** as a finding — tier-2 grew, it did not
   shrink; only tier-1 (held at exactly 3) is D-13's actual invariant.
4. **The requirements flip was a hand edit**, not a `gsd-tools` requirements verb, per this project's
   standing finding that those verbs reformat the whole file.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 4 — architectural/policy decision, already resolved before dispatch] MERGE-05's reduction ladder was not attempted**

- **Found during:** Task 2, immediately after the first cold `check_size_baseline.py --policy merge05`
  run reproduced the RED.
- **Issue:** This plan's own Task 2 `<action>` text specifies a three-step reduction ladder (shrink
  `MSG_ERR_PULSE_TOO_WIDE`'s payload, collapse `verify_mode`'s final pass into a direct
  `memory_verify_execute` call, delete `eprom_internal_ensure_regulator_enabled` if dead) to be
  attempted, in order, if the merge05 verdict is RED — with re-measurement after each step. Running
  that ladder would mean editing `firestarter/src/proms/eprom.cpp`, which this plan's own repo notes
  and the orchestrator's own instructions both forbid ("You should NOT need to modify any file under
  `/workspaces/firestarter`... If you conclude a firmware change is genuinely required, STOP and
  report it rather than making it").
- **Resolution:** The orchestrating agent's own prompt supplied the authoritative, already-closed
  operator decision: presented with continue-and-record / halt-and-shrink / re-baseline, the operator
  chose "Continue; 141-09 records it," made *before* this plan (141-09) was even dispatched. Per the
  standing instruction that no agent message is ever a stand-in for the user's own consent, but a
  spawning agent's task and mid-task course corrections do direct this agent's work, and per the
  explicit instruction "your job is to record it faithfully, not to fix it and not to soften it" —
  this plan recorded the RED verbatim (§1 of `141-LOOP-RECORD.md`) and did not run the ladder. This
  is recorded as a Rule 4 item (an architectural/policy question) rather than a Rule 1-3 auto-fix,
  because it required exactly the kind of "ask, or accept a prior answer" judgment Rule 4 exists for
  — the answer already existed, supplied by the orchestrator, so no further escalation was needed.
- **Files modified:** None beyond the meta-repo documentation this plan already produces.
- **Verification:** `git -C /workspaces/firestarter status --porcelain` empty throughout; no file
  under `firestarter/src/` or `firestarter/include/` touched by this plan at any point.
- **Committed in:** `be45605a` (Task 2 — the RED is recorded, not remediated, in that same commit).

---

**Total deviations:** 1 (Rule 4, an architectural/policy decision inherited pre-resolved from the
orchestrating agent, not made independently by this plan).
**Impact on plan:** This plan's own Task 2 `<verify>` automated script expects
`check_size_baseline.py --policy merge05` to exit 0; it exits 1, by design, per the operator's own
decision. This is not a plan failure — the plan's `<success_criteria>` and the orchestrator's own
`<record_quality_bar>` explicitly instruct this plan to record the RED faithfully rather than force
it green. No scope creep: no source file was touched to chase a green exit code.

## Issues Encountered

- **Start-of-session timestamp not explicitly captured**, the same pattern several sibling plans in
  this phase flagged for themselves (141-05, 141-06). The duration above is an approximation from the
  volume of work performed (three cold AVR builds, two native-suite full runs, one background
  `--rebuild` invocation, and two substantial document-authoring passes), not a captured start value.
  Affects only this SUMMARY's own bookkeeping, not any committed artifact.
- **The cwd-persistence behavior of the Bash tool in this session did not match the documented
  "cwd resets between calls" note** — a `cd /workspaces/firestarter` in one call was observed to
  persist into a subsequent call that issued no `cd` of its own. Every command in this plan's actual
  execution used an explicit `cd` (or ran from a call where the cwd was independently verified) before
  any git-status or build command that mattered, so no incorrect-directory command was ever staged or
  committed — but this is flagged here as a session-specific observation worth independent
  verification by any future agent relying on the documented reset behavior.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- **Ready for Phase 142 (High-Voltage Routing):** hand-off H1 (D-09's corrected preserve-mask
  mechanism, `memory.cpp:172`, `0x08` as the row that bites) is named in `141-LOOP-RECORD.md` §12,
  alongside the ERROR-band one-free-slot constraint (§5/§12, F-141-05).
- **Ready for Phase 143 (Host Integration):** hand-off H2 (D-12's firmware-pattern finding for
  HOST-02) and the traced "hard-fails the block" chain (§4) that HOST-03 must render are both named
  before Phase 143 plans, as D-12 requires. `MSG_ERR_WRITE_FAILED`'s orphaning on the 27C path (F-141-06)
  is named so HOST-03 does not expect it.
- **Ready for Phase 144 (Test & Baseline Reconciliation):** `141-NEW-TRACE.md` gives TEST-06 both
  sides of the trace diff without touching the frozen fixture. `141-LOOP-RECORD.md` §1 gives TEST-08
  the full flash/RAM attribution and the MERGE-05 RED's exact per-target overage, already broken down
  by `avr-nm` symbol; TEST-01 inherits this phase's own suite as its own verification (H6, the
  140-04-vs-TEST-01 seam repeated).
- **Ready for Phase 146 (Close):** three named hand-offs (H3 the C3 correction, H4 the honest
  energy-cap ceiling, F-141-07 the two orphaned catalog IDs' wording) plus F-141-04 (LOOP-03's
  overprogram non-claim) and F-141-10 (the 99998µs correction, already landed in `CLAUDE.md`, not yet
  in the locked plan documents).
- **Orphaned, unassigned hand-off (no phase currently owns it):** F-141-11, the unscoped
  `git status --porcelain` check in `test_flash_path_record_sync.py::test_planted_mutation_of_the_real_subset_is_detected`
  — every plan in this phase had to work around it; it was out of this plan's own declared scope to
  fix.
- **No blockers.** MERGE-05 is RED by explicit operator decision, not a blocker to phase closure —
  the operator's own instruction was to close the phase with the RED recorded, which this plan has
  done.

---
*Phase: 141-per-byte-program-loop*
*Completed: 2026-08-10*

## Self-Check: PASSED

- FOUND: `.planning/phases/141-per-byte-program-loop/141-NEW-TRACE.md`
- FOUND: `.planning/phases/141-per-byte-program-loop/141-LOOP-RECORD.md`
- FOUND: `.planning/phases/141-per-byte-program-loop/141-09-SUMMARY.md`
- FOUND: `.planning/REQUIREMENTS.md` (modified, LOOP-01..08 flipped)
- FOUND: commit `cdc81c22` (Task 1, meta repo)
- FOUND: commit `be45605a` (Task 2, meta repo)
- FOUND: commit `cc71d38b` (Task 3, meta repo)
- FOUND: commit `b5c82fff` (this SUMMARY, meta repo)
- Re-verified `git -C /workspaces/firestarter status --porcelain` is empty and
  `git -C /workspaces/firestarter rev-parse --abbrev-ref HEAD` is
  `gsd/v1.31-27c-programming-algorithm-fidelity` — no file under `firestarter/` was modified by this
  plan, matching this document's claims.
