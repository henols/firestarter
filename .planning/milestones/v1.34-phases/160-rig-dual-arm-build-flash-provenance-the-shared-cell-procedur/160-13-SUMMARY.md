---
phase: 160-rig-dual-arm-build-flash-provenance-the-shared-cell-procedur
plan: 13
subsystem: infra
tags: [falsification, reconstruction, todo, validation, phase-gate, sign-off]

requires:
  - phase: 160 (plans 01-12)
    provides: the assembled rig (six firmware images, both host arms, twelve tools, PROCEDURE.md,
      the canonical evidence record) plus four bring-up positions each independently exercised
      and independently falsified — the substrate this plan tests for reconstructibility and
      then closes the phase over
provides:
  - The RIG-05 discharge: a genuinely fresh, tool-less context, given only BRINGUP-wrv's
    provenance record and PROCEDURE.md, reconstructed the bring-up run three times, with
    rounds 1 and 2 each failing and each failure driving a real fix at the source (the tool,
    then the procedure) rather than in prose
  - capture_provenance.py extended with image_mask/image_stamp_width/image_sha in RECORD_KEYS,
    a resolve_image_plan_fields() lookup against bench/IMAGE-PLAN.json (zero device I/O), and a
    new --patch-image-plan retrofit mode, used to re-capture BRINGUP-wrv's own record
  - PROCEDURE.md Amendment 2 — P-11's teardown re-probe gained the literal command block every
    other step already had, closing a prescription ambiguity the reconstruction surfaced
  - The annotated, still-pending avrdude-mcu-detection-fallback todo (mechanism reused, product
    deliverable explicitly not built, status/resolves_phase untouched)
  - 160-VALIDATION.md's 38-row per-task verification map and its Wave 0 tool-list reconciliation
    (12 tools: the original 10 plus check_arms.py and render_steps.py, each explained)
  - PHASE-160-GATE.md — the single document naming every falsification artifact by path,
    presented to and approved by the operator
  - RIG-05 marked Complete; all five phase requirements (RIG-01…05) now Complete
affects: [161, 162, 163, 165, 166]

tech-stack:
  added: []
  patterns:
    - "A fresh-context reconstruction is only as separate as its mechanism: spawning a genuinely
       new, tool-less `claude -p` subprocess per round (no shared conversation history, no
       filesystem/web tools, an isolated cwd outside the project so no CLAUDE.md or auto-memory
       auto-loads) with the two allowed documents pasted verbatim into a one-shot prompt is what
       makes 'zero fields sourced from session memory' a property of the mechanism rather than a
       transcriber's discipline."
    - "A record insufficiency a reconstruction surfaces is fixed at the tool that captures the
       record, not by hand-patching the JSON — and the fix can be retrofit onto an
       already-captured record via a dedicated patch mode that touches no device or git probe,
       so a correction never requires re-running hardware-facing steps against a cell whose
       physical state must not be disturbed."
    - "A prescription ambiguity (a step's prose describes an action but gives no literal command,
       unlike every sibling step) is fixed by amending the procedure itself and re-confirming the
       arm-agnostic empty-diff render gate stays empty — not by accepting whatever a reconstructing
       context had to guess."
    - "A phase gate document earns trust by citing artifacts and quoting numbers out of them, not
       by restating a plan SUMMARY's prose — and a sign-off is recorded by stating explicitly that
       every non-claim and carried-forward item was PRESENTED and ACCEPTED, not merely disclosed
       in a document the approver may not have opened."

key-files:
  created:
    - .planning/v1.34/bench/cells/BRINGUP-wrv/RECONSTRUCTION.md
    - .planning/v1.34/bench/cells/BRINGUP-wrv/RECONSTRUCTION-DIFF.md
    - .planning/v1.34/PHASE-160-GATE.md
  modified:
    - .planning/v1.34/tools/capture_provenance.py (RECORD_KEYS +3, resolve_image_plan_fields(),
      patch_image_plan_fields(), --image-plan/--patch-image-plan args, 5 new selftest legs)
    - .planning/v1.34/bench/cells/BRINGUP-wrv/provenance.json (image_mask/image_stamp_width/
      image_sha added via --patch-image-plan; every other field and every commands[] entry
      byte-unchanged)
    - .planning/v1.34/PROCEDURE.md (Amendment 2: P-11 literal command block + amendment log entry)
    - .planning/todos/pending/avrdude-mcu-detection-fallback.md (additive annotation only)
    - .planning/phases/160-rig-dual-arm-build-flash-provenance-the-shared-cell-procedur/160-VALIDATION.md
      (38-row map, Wave 0 reconciliation, sign-off checklist, front-matter flags)
    - .planning/REQUIREMENTS.md (RIG-05 → Complete, both the checkbox and the traceability row)
    - .planning/ROADMAP.md (160-13-PLAN.md checkbox ticked; Overview row and phase-level checkbox
      deliberately left untouched — phase completion is the orchestrator's step)
    - .planning/STATE.md (Current Position, Session, Decisions, Performance Metrics, front matter)
  not_committed_per_policy: []

key-decisions:
  - "Separation for the reconstruction was achieved by process isolation (a brand-new claude -p
     subprocess per round, --disallowedTools denying all filesystem/web tools, an isolated cwd
     outside /workspaces) rather than by instructing a same-session agent to 'pretend' it has no
     other context — the latter cannot be verified; the former structurally cannot leak session
     state because no tool call could reach it even if attempted."
  - "The mask/stamp_width/sha record insufficiency was fixed by extending capture_provenance.py's
     own gathered field set and adding a --patch-image-plan mode, not by manually editing
     provenance.json's JSON — per this project's standing 'fix at the source, never hand-patch
     the record' rule, and per this plan's own key_links instruction."
  - "The P-11 prescription ambiguity was fixed by amending PROCEDURE.md with a literal command
     block (mirroring P-02's shape), not by accepting the reconstruction's inferred-by-analogy
     output path — and the fix was verified structurally (render_steps.py's empty-diff gate
     re-confirmed empty) rather than merely asserted safe."
  - "A third reconstruction round was run (against the record AND the procedure, both fixed)
     even though the plan's own acceptance criteria did not require a fresh round for a
     prescription-ambiguity fix — to produce one genuinely clean, guess-minimal transcript
     rather than leave the final documented round carrying a still-open guess."
  - "BRINGUP-wrv's own actual P-11 teardown never having re-run probe_board.py (discovered by
     this same reconstruction exercise) was disclosed, not backfilled — backfilling it would
     require an avrdude signature probe against a board this plan's own constraints forbid
     touching while a chip is seated. Recorded in RECONSTRUCTION-DIFF.md and carried into
     PHASE-160-GATE.md's non-claims rather than silently resolved."
  - "The operator's approval is recorded as acceptance of the limits AS STATED, not as a claim
     that the limits are resolved — PHASE-160-GATE.md's §1-§7 (including every non-claim and
     carried-forward item) are byte-unchanged from the version the operator reviewed; only the
     header and the sign-off section were updated to record the response."
  - "Phase-level completion (ROADMAP.md's Phase 160 checkbox and Overview row, STATE.md's phase
     status) was deliberately left untouched per the coordinator's explicit instruction — that is
     the orchestrator's own next step after this plan returns, not this plan's to record."

requirements-completed: [RIG-05]

coverage:
  - id: D1
    description: "A fresh, tool-less context, given only provenance.json and PROCEDURE.md,
      emitted the command set and physical setup for BRINGUP-wrv three times; round 1's guessed
      mask/stamp_width/sha was a genuine record insufficiency, round 2's guessed P-11 teardown
      path was a genuine prescription ambiguity, and round 3 (after both fixes) reproduced only
      cosmetic self-hedges over values already stated in the two inputs"
    requirement: RIG-05
    verification:
      - kind: other
        ref: "bench/cells/BRINGUP-wrv/RECONSTRUCTION.md (all three rounds' verbatim output) and
          RECONSTRUCTION-DIFF.md (classification: 1 record insufficiency fixed, 1 prescription
          ambiguity fixed, 6 cosmetic, 1 not-a-divergence; closing sentence: zero values sourced
          from outside the two inputs)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The record insufficiency was fixed at capture_provenance.py (not hand-patched)
      and the record was re-captured with zero device I/O; the whole canonical record and full
      gate suite stayed green after the fix"
    requirement: RIG-05
    verification:
      - kind: other
        ref: "python3 tools/capture_provenance.py --selftest (rc=0, 5 new legs); diff of
          provenance.json before/after the --patch-image-plan invocation (3 lines added, nothing
          else touched); gate_record.py --cell / --jsonl both rc=0; render_evidence.py --check
          rc=0; bash tools/run_gates.sh rc=0 (11/11 selftests + 5/5 live gates)"
        status: pass
    human_judgment: false
  - id: D3
    description: "The prescription ambiguity was fixed by amending PROCEDURE.md (Amendment 2)
      and the arm-agnostic step-list diff was reconfirmed empty after the edit"
    requirement: RIG-05
    verification:
      - kind: other
        ref: "diff <(render_steps.py --arm control) <(render_steps.py --arm v133) — empty, 11
          lines both arms, unchanged from before the edit"
        status: pass
    human_judgment: false
  - id: D4
    description: "The folded todo carries an additive annotation with status/resolves_phase
      unchanged, and 160-VALIDATION.md holds 38 ordered, placeholder-free rows with the Wave 0
      list reconciled to the 12 tools that exist"
    requirement: RIG-05
    verification:
      - kind: other
        ref: "git diff -U0 on the todo shows only added lines; the python row/placeholder/
          tool-list check (160-13-02's second automated leg) prints 'OK validation map: 38
          ordered rows, no placeholders, flags true, all 12 tools listed'"
        status: pass
    human_judgment: false
  - id: D5
    description: "PHASE-160-GATE.md names every falsification artifact by path with numbers read
      from the cited artifact, and the operator opened it, reviewed the non-claims and
      carried-forward items, and signed off"
    verification: []
    human_judgment: true
    rationale: "Whether the gate document's non-claims are stated plainly enough, and whether the
      carried-forward items are an acceptable state to release the sweep phases on, are matters
      of operator judgment this plan cannot mechanically verify — it can only assert that every
      cited path exists and every quoted number matches its source, which was checked."

duration: ~2h40m (across the initial reconstruction/gate-assembly session and this closing session)
completed: 2026-08-27
status: complete
---

# Phase 160 Plan 13: D-17 Reconstruction, Validation Close-Out & Phase Sign-Off Summary

**RIG-05 discharged by a genuinely fresh, tool-less context rebuilding the bring-up run three
times against BRINGUP-wrv's real record — rounds 1 and 2 each found a real gap and drove a fix
at the source, round 3 confirmed both closures — and the operator approved the assembled phase
gate verbatim ("Approved — close Phase 160") with every non-claim and carried-forward item
explicitly presented and explicitly accepted.**

## Performance

- **Duration:** ~2h40m total (Task 1-2 and the initial gate assembly in one session; the
  operator's sign-off and its recording in a second, short session)
- **Tasks:** 3/3 complete (Task 3 a `checkpoint:human-verify` gate, resolved by operator approval)
- **Files modified:** 5 (Task 1 commit) + 2 (Task 2 commit) + 1 (Task 3 gate-assembly commit) +
  4 (this closing session's metadata: REQUIREMENTS.md, ROADMAP.md, STATE.md, PHASE-160-GATE.md)

## Accomplishments

- **RIG-05 discharged, both halves.** The script gate (plans 04/07) proves the record is
  complete; this plan's fresh-context reconstruction proves it is *sufficient* — a party
  holding only `provenance.json` + `PROCEDURE.md` genuinely rebuilt the run, self-reporting
  every value it had to guess rather than filling gaps with plausible defaults.
- **Both reconstruction failures drove real fixes, not workarounds.** Round 1's guessed
  `$MASK` was a genuine gap in `capture_provenance.py`'s own gathered field set — fixed by
  extending the tool (`RECORD_KEYS` +3, a zero-device-I/O `IMAGE-PLAN.json` lookup, a new
  `--patch-image-plan` retrofit mode) and re-capturing the real record with a 3-line diff.
  Round 2's guessed teardown-probe path was a genuine gap in `PROCEDURE.md`'s own prose (every
  other step had a literal command; `P-11`'s re-probe did not) — fixed by amending the
  procedure (Amendment 2) and reconfirming the empty-diff render gate.
- **A third round was run to produce one clean, guess-minimal transcript**, even though the
  plan's own acceptance criteria did not require a fresh round for the prescription-ambiguity
  fix — the remaining self-flagged "guesses" in that round were all, on inspection, values
  already stated directly in `PROCEDURE.md`'s own text, or the one genuinely runtime-only
  quantity (`--app-verdict`) that the procedure itself represents as a bracketed placeholder.
- **A second, distinct finding was disclosed, not backfilled.** This same reconstruction
  exercise revealed that `BRINGUP-wrv`'s own actual `P-11` teardown (Plan 12) never re-ran
  `probe_board.py` at all — a genuine compliance gap against the (pre-amendment) prescription.
  It is not correctable now without an avrdude signature probe against a seated chip, which
  this plan's own constraints forbid; it is recorded and carried forward.
- **The validation map and Wave 0 reconciliation were filled honestly, not asserted.** All 38
  tasks across the 13 plans got one row each, in order, with the sampling-continuity claim
  walked (no gap found) rather than checked off by assumption, and the Wave 0 tool list
  reconciled to the 12 files that actually exist under `.planning/v1.34/tools/` (the original
  10 plus `check_arms.py` and `render_steps.py`, each explained against the strategy document's
  own gap-flags).
- **`PHASE-160-GATE.md` was assembled from artifacts, not from memory**, citing the three
  cross-flash falsifications' differing-byte counts, the reconstruction's round count and
  divergence counts, a 12-tool gate-birth ledger (every tool has a recorded red observation,
  none is a gap), the full gate suite result, the 4-bring-up/0-sweep record state (quoted
  verbatim from `EVIDENCE.md`'s own reconciliation line), a comprehensive non-claims section,
  and the exact rig state Phase 161 inherits.
- **The operator approved the gate verbatim** — *"Approved — close Phase 160"* — after being
  presented with every non-claim and carried-forward item explicitly, and choosing approval
  over the two offered alternatives (strengthening a named artifact, or fixing the
  argv-recording gap first) with the limits accepted as stated. `PHASE-160-GATE.md`'s §1-§7
  are byte-unchanged from the version reviewed; only its header and sign-off section record
  the response.
- **RIG-05 marked Complete; all five phase requirements (RIG-01…05) are now Complete.**
  Phase-level completion (`ROADMAP.md`'s Phase 160 checkbox/Overview row, `STATE.md`'s phase
  status) is deliberately left for the orchestrator's own `phase.complete` step, per explicit
  instruction — this plan records plan-level and requirement-level completion only.

## Task Commits

1. **Task 1: D-17 — reconstruct the bring-up run from the record alone and diff it against the
   prescription** — `a96e2c92` (feat)
2. **Task 2: Annotate the folded todo and fill the validation map** — `0ecdd512` (docs)
3. **Task 3 (gate assembly, presented and blocked):** `33643699` (docs) — `PHASE-160-GATE.md`
   committed awaiting sign-off
4. **This closing session (sign-off recorded, plan-level metadata):** commit follows this
   SUMMARY, per the standard task-commit protocol

## Files Created/Modified

- `.planning/v1.34/bench/cells/BRINGUP-wrv/RECONSTRUCTION.md` — all three reconstruction
  rounds' verbatim output, the input list, and the separation mechanism
- `.planning/v1.34/bench/cells/BRINGUP-wrv/RECONSTRUCTION-DIFF.md` — the prescription side
  built from the real artifacts, every divergence classified, both fixes named, the closing
  zero-outside-inputs statement
- `.planning/v1.34/tools/capture_provenance.py` — `image_mask`/`image_stamp_width`/`image_sha`
  in `RECORD_KEYS`, `resolve_image_plan_fields()`, `patch_image_plan_fields()`,
  `--image-plan`/`--patch-image-plan` CLI flags, 5 new `--selftest` legs
- `.planning/v1.34/bench/cells/BRINGUP-wrv/provenance.json` — the 3 new fields patched in,
  every other field and every `commands[]` entry byte-unchanged
- `.planning/v1.34/PROCEDURE.md` — Amendment 2 (`P-11`'s literal command block + amendment
  log entry)
- `.planning/todos/pending/avrdude-mcu-detection-fallback.md` — additive 2026-08-27 annotation
- `.planning/phases/160-.../160-VALIDATION.md` — 38-row map, Wave 0 reconciliation, sign-off
  checklist, `nyquist_compliant`/`wave_0_complete` set true
- `.planning/v1.34/PHASE-160-GATE.md` — assembled, presented, and (this session) updated to
  record the operator's approval
- `.planning/REQUIREMENTS.md` — RIG-05 → Complete (checkbox + traceability row)
- `.planning/ROADMAP.md` — 160-13-PLAN.md checkbox ticked only; phase-level checkbox and
  Overview row deliberately untouched
- `.planning/STATE.md` — Current Position, Session, Decisions, Performance Metrics updated;
  `milestone_name`/`current_phase_name` verified unchanged after every edit

## Decisions Made

See `key-decisions` in the frontmatter above — summarized: separation was achieved by process
isolation, not instruction; both reconstruction failures were fixed at their source (tool,
then procedure), never by hand-patching a record or accepting a guess; a third round was run
for a clean final transcript even though not strictly required; the newly-discovered teardown
compliance gap was disclosed rather than backfilled; the operator's approval was recorded as
acceptance of the limits as stated, with the gate document's substance left intact; and phase-
level completion was deliberately left to the orchestrator.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - missing critical functionality] `provenance.json` never carried the image
mask/stamp_width/sha fields the run genuinely needed**
- **Found during:** Task 1, round 1 of the fresh-context reconstruction
- **Issue:** The reconstructing context could not fill `gen_addr_image.py`'s mask argument
  from the two allowed inputs — `provenance.json`'s schema never listed `image_mask`/
  `image_stamp_width`/`image_sha`, even though a later-stage record (`EVIDENCE.jsonl`)
  already carried the identical values under the same field names.
- **Fix:** Extended `capture_provenance.py`'s `RECORD_KEYS` and added a zero-device-I/O
  lookup against `bench/IMAGE-PLAN.json` plus a `--patch-image-plan` retrofit mode; re-captured
  `BRINGUP-wrv`'s record (diff: 3 lines added, nothing else touched); re-ran the reconstruction
  fresh (round 2) and confirmed the gap closed.
- **Files modified:** `.planning/v1.34/tools/capture_provenance.py`,
  `.planning/v1.34/bench/cells/BRINGUP-wrv/provenance.json`
- **Verification:** `capture_provenance.py --selftest` rc=0 (5 new legs); `gate_record.py
  --cell`/`--jsonl` both rc=0; `render_evidence.py --check` rc=0; `run_gates.sh` rc=0.

**2. [Rule 2 - missing critical functionality] `PROCEDURE.md`'s `P-11` teardown re-probe had
no literal command, unlike every other step**
- **Found during:** Task 1, round 2 of the reconstruction
- **Issue:** The reconstructing context had to invent an `--out` filename by analogy to `P-02`
  because `P-11`'s prose said what to do but gave no literal command block.
- **Fix:** Amended `PROCEDURE.md`'s `P-11` with a literal command block naming an explicit,
  distinct output path (`board_probe_teardown.json`), recorded as Amendment 2; reconfirmed the
  arm-agnostic step-list diff stayed empty.
- **Files modified:** `.planning/v1.34/PROCEDURE.md`
- **Verification:** `diff <(render_steps.py --arm control) <(render_steps.py --arm v133)` —
  empty, both arms 11 lines, unchanged.

**3. [Rule 3 - blocking, disclosed rather than resolved] A stray `__pycache__` directory under
`.planning/v1.34/tools/` broke Task 2's own filesystem-glob-based tool-list check**
- **Found during:** Task 2, running the plan's own second automated verify leg
- **Issue:** A gitignored, untracked bytecode-cache directory (from earlier `python3` runs)
  matched `glob.glob('.planning/v1.34/tools/*')` and was reported as a "tool produced but
  absent from the Wave 0 list."
- **Fix:** Removed the cache directory (a targeted `rm -rf` of a known-safe, regeneratable,
  gitignored artifact — not a `git clean` invocation, and nothing tracked or evidentiary was
  touched).
- **Files modified:** none (a local filesystem artifact, never git-tracked).
- **Verification:** the same check re-run afterward prints "all 12 tools listed"; `run_gates.sh`
  re-run green.

---

**Total deviations:** 3 auto-handled (2 Rule 2 fixes at the record-insufficiency/prescription-
ambiguity sources the reconstruction itself was designed to surface, 1 Rule 3 filesystem
cleanup). Every fix was verified against the real record and the full gate suite before
proceeding; no measurement was ever adjusted to force a green.

## Issues Encountered

One infrastructure flake: round 3's first fresh-context invocation returned a content-safety
classifier refusal (`API Error: Sonnet 4.5 can't help with this... Details: [bio]`), unrelated
to any content in either input document. Retried once, identically; the retry succeeded and
is the transcript recorded in `RECONSTRUCTION.md`.

## User Setup Required

None. This plan was entirely host-side (a fresh-context reconstruction via a separate `claude
-p` subprocess, a todo annotation, a validation map, a gate document) plus the operator's own
review-and-respond step for the phase gate, which is complete.

## Next Phase Readiness

- **RIG-05 is Complete. All five phase requirements (RIG-01…05) are now Complete.**
- **The operator has approved the phase gate** (`PHASE-160-GATE.md`, verbatim: "Approved —
  close Phase 160"), with every non-claim and carried-forward item explicitly presented and
  explicitly accepted.
- **Phase-level completion is the orchestrator's own next step** — this plan deliberately does
  not tick `ROADMAP.md`'s Phase 160 checkbox, does not touch the Phase 160 Overview row, and
  does not change `STATE.md`'s `current_phase`/`status` fields beyond plan-level progress.
- **The rig is left exactly as it stood entering this plan**, for Phase 161's first cell to
  inherit without reconfiguration: Uno (ATmega328P) + Rev 2.0 shield, v1.33 arm flashed and
  proven, **W27C512 seated**, pot confirmed at 12.0V, port `/dev/ttyACM0`. Zero device I/O ran
  during this plan.
- **Carried-forward, not blockers:** `~/.firestarter`'s continued existence (disclosed, not
  cleared — sandbox denies deletion and it is evidence); `BRINGUP-wrv`'s un-re-run `P-11`
  board probe (disclosed, not backfilled — would require a forbidden signature probe); the
  sparse argv-recording finding and its scope consequence for RIG-05; the recurring
  plan-authoring-defect pattern (4 occurrences); the Wave 6 superseded-in-place false claim;
  and the ~20 latent rig-tooling defects found only on first real-hardware contact. All six
  are named in `PHASE-160-GATE.md`'s non-claims and were part of what the operator explicitly
  accepted.
- **Both submodules remain porcelain-clean** (`firestarter` @ `5759dc8d644a8a7fb26e9a0ccd11a8bfd53fc463`,
  detached HEAD from the last device operation; `firestarter_app` clean). Neither was touched
  by this plan.

---
*Phase: 160-rig-dual-arm-build-flash-provenance-the-shared-cell-procedur*
*Completed: 2026-08-27*
