---
phase: 205-the-pre-flights-leave-the-firmware
plan: "06"
subsystem: firmware-build, messages-catalog, docs
tags: [platformio, avr, flash-ram-measurement, messages.toml, codegen, meta-repo-path-citation]

requires:
  - phase: 205-05
    provides: "The negative-address fix's own flash/RAM cost, recorded as a separate
      section in 205-FLASH-RAM.md, and the post-fix tree this plan's phase-exit
      measurement reproduces."
  - phase: 205-04
    provides: "The completed sweep (FWBLANK-01 through FWBLANK-04) whose reclaim this
      plan's delta table separates from plan 05's fix cost; the two orphaned catalog ids
      (0x08, 0x0B) whose 204 annotation shape this plan's 0xB0/0x2E annotations follow."
provides:
  - "205-FLASH-RAM.md's completed phase-exit section, delta table (sweep reclaim / fix
    cost / phase net, each named to its two commit shas) and twelve total artifact digests
    (FWBLANK-05)."
  - "MSG_ERR_NOT_BLANK (0xB0) and DBG_FLAG_SKIP_BLANK (0x2E) kept and annotated in
    tools/catalog/messages.toml, proven to reach no generated artifact (D-08)."
  - "Three stale FLAG_SKIP_BLANK_CHECK/flash_nor_unlock.cpp:41 prose citations repaired in
    firestarter_app, closing out deferred-items.md's three open findings (orchestrator
    added scope)."
affects: [205-07]

actuals:
  tokens: 24000
  tasks: 3
  commits: 5
  commits_by_repo:
    meta: 4
    firestarter_app: 1
    firestarter_fw: 0

tech-stack:
  added: []
  patterns:
    - "Codegen-inertness proof by regeneration-to-temp-path-and-diff: run
      codegen.py --language {cpp,python} --target /tmp/... from the amended catalog and
      diff -u the result against the sub-repo's checked-in copy. Empty diff is the proof a
      comment-only catalog edit reaches no generated artifact, following the shape 694acce3
      (phase 204) established."
    - "Annotation self-reference trap: writing a retired identifier's own name inside its
      annotation comment (e.g. 'LOG_DEBUG_ID_SUB(DBG_FLAG_SKIP_BLANK)') creates an earlier
      t.index() match than the actual name= line, breaking any downstream string-offset
      scan that assumes the found index is the field itself. Paraphrase self-references in
      annotation prose ('a LOG_DEBUG_ID_SUB call on this sub-id') instead of naming the
      identifier literally."

key-files:
  created: []
  modified:
    - .planning/phases/205-the-pre-flights-leave-the-firmware/205-FLASH-RAM.md
    - tools/catalog/messages.toml
    - .planning/phases/205-the-pre-flights-leave-the-firmware/deferred-items.md
    - firestarter_app/firestarter/cli_handlers.py
    - firestarter_app/tests/test_uv_mask.py
    - firestarter_app/tests/fixtures/report_shapes.py

key-decisions:
  - "Phase-exit is the same tree as plan 05's post-fix measurement, not a fresh commit --
    no firmware commit landed between plan 05's task 2 and this plan. Re-measured anyway
    rather than copying plan 05's numbers, per this plan's own prohibition (T-205-22): the
    six digests and Flash:/RAM: lines came out byte-identical to plan 05's, which is the
    proof of no drift rather than a shortcut around measuring."
  - "MSG_ERR_NOT_BLANK's annotation states the divergence from the plain-orphan shape
    explicitly (D-08): unlike the three debug ids, 0xB0 is not orphaned on the host -- a
    post-3.1.0 host still receives it from pre-3.1.0 firmware, which is the skew plan 07's
    bench leg puts on silicon -- so it is deliberately still rendered, not merely kept."
  - "deferred-items.md's three findings were marked status: resolved in place rather than
    deleting the file, even though all three are now closed. 205-04-SUMMARY.md already
    cites the file by path as evidence of the deviation it recorded; deleting it would turn
    that citation stale, which the project's own standing rule says to repair, not create."
  - "The three-citation repair landed as its own firestarter_app commit, separate from the
    catalog and flash/RAM commits, per the orchestrator's added-scope instruction that it
    be reported and committed distinctly from plan-authored scope."

requirements-completed: [FWBLANK-05]

coverage:
  - id: D1
    description: "FWBLANK-05's flash/RAM record is complete: phase-exit figures measured
      from a clean pio run (reproduced twice, byte-identical), a delta table stating the
      sweep's reclaim, the fix's cost and the phase's net as three separate claims each
      naming its two commit shas, both leonardo denominators with byte margins, and twelve
      total artifact digests."
    requirement: FWBLANK-05
    verification:
      - kind: integration
        ref: "pio run -t clean -e uno -e uno328pb -e leonardo && pio run -e uno -e uno328pb -e leonardo (reproduced twice, identical Flash:/RAM: lines and six digests both times)"
        status: pass
      - kind: other
        ref: "python3 -c heading/token check on 205-FLASH-RAM.md (task 1's own verify one-liner): prints 'FWBLANK-05 record complete'"
        status: pass
    human_judgment: false
  - id: D2
    description: "MSG_ERR_NOT_BLANK (0xB0) and DBG_FLAG_SKIP_BLANK (0x2E) are annotated in
      place in tools/catalog/messages.toml, keeping every existing field value, proven to
      reach no generated artifact by regenerating messages.h and messages.py to a temporary
      path and diffing byte-for-byte against both sub-repos' checked-in copies."
    requirement: FWBLANK-05
    verification:
      - kind: integration
        ref: "python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check (OK: catalog valid, 79 messages)"
        status: pass
      - kind: integration
        ref: "diff -u against firestarter_fw/include/messages.h and firestarter_app/firestarter/messages.py, both regenerated to a temp path -- both diffs empty"
        status: pass
      - kind: other
        ref: "python3 -c annotation-content assertion (task 2's own verify one-liner): prints 'both catalog ids annotated'"
        status: pass
    human_judgment: false
  - id: D3
    description: "Orchestrator-added scope: three stale prose citations of retired
      identifiers (flash_nor_unlock.cpp:41's dead assignment, FLAG_SKIP_BLANK_CHECK) are
      repaired in firestarter_app, prose-only, no assertion logic changed, and
      deferred-items.md's three open findings are marked resolved."
    verification:
      - kind: integration
        ref: "firestarter_app/.venv-ci-188/bin/python -m pytest tests/ -o addopts=\"\" -q (2319 passed, 36 snapshots passed)"
        status: pass
      - kind: other
        ref: "ruff check on all three modified firestarter_app files: All checks passed"
        status: pass
    human_judgment: false
---

# Phase 205 Plan 06: FWBLANK-05's measurement finishes, two catalog ids get annotated, and three stale citations get repaired Summary

**205-FLASH-RAM.md now carries the completed phase-exit figures and a three-way delta table
(sweep reclaim −518 B / fix cost +22 B / phase net −496 B flash per AVR target, identical on
uno, uno328pb, leonardo), MSG_ERR_NOT_BLANK and DBG_FLAG_SKIP_BLANK are kept and annotated in
the meta-repo catalog with a proven-empty regeneration diff, and three sibling-plan stale
prose citations of retired identifiers are repaired in firestarter_app.**

## Performance

- **Duration:** ~9 min (bounded by commit timestamps: 18:03:19Z first commit to
  18:12:04Z last commit — no start-time sentinel captured at kickoff)
- **Started:** 2026-09-22T18:03:19Z (approximate)
- **Completed:** 2026-09-22T18:12:04Z
- **Tasks:** 2 plan tasks + 1 orchestrator-added scope task
- **Files modified:** 6 (2 meta-repo docs, 1 meta-repo catalog, 3 firestarter_app)

## Accomplishments

- `205-FLASH-RAM.md`'s phase-exit section is filled from a clean `pio run` reproduced twice
  with byte-identical output — `uno` 20956 B flash / 1394 B RAM, `uno328pb` 21000 B / 1400 B,
  `leonardo` 23314 B / 1835 B — matching plan 05's post-fix tree exactly (same commit,
  `6e11d057b59977dd870c1ddcc588dd2f6f3ea1db`, since no firmware commit landed since).
- The delta table states three separate arithmetic claims, each naming its two commit shas:
  the sweep's own reclaim (entry `a4e002f2` minus post-sweep `9061dd1`: −518 B flash / −4 B
  RAM per target, identical on all three), the fix's cost (post-sweep minus post-fix
  `6e11d05`: +22 B / +0 B, already recorded by plan 05, reproduced here for readability),
  and the phase's net (entry minus exit: −496 B / −4 B per target) — with the arithmetic
  check (reclaim + cost = net) holding on every target.
- Leonardo is quoted against both denominators: 23314/32768 = 71.1% (9454 B margin) and
  23314/28672 = 81.3% (5358 B true margin), strictly below the real
  ATmega32U4-on-Caterina ceiling.
- `MSG_ERR_NOT_BLANK` (0xB0) and `DBG_FLAG_SKIP_BLANK` (0x2E) are annotated in
  `tools/catalog/messages.toml`, keeping every existing field value. 0xB0's annotation
  states the divergence from the plain-orphan shape: a post-3.1.0 host still receives it
  from pre-3.1.0 firmware, so it is deliberately still rendered. Regenerating both
  `messages.h` and `messages.py` from the amended catalog to a temporary path produced
  output byte-identical to both sub-repos' checked-in copies; neither sub-repo has a
  modified file.
- (Orchestrator-added scope, reported separately below) Three stale prose citations of
  retired identifiers — logged as open findings in `deferred-items.md` by sibling plans
  205-03/04 — are repaired in `firestarter_app`, and `deferred-items.md` is updated to mark
  all three resolved.

## Task Commits

Each task was committed atomically:

1. **Task 1: complete the FWBLANK-05 record with the phase-exit figures and the separated
   arithmetic** — `84dd34b5` (docs, meta repo) — filled `205-FLASH-RAM.md`'s phase-exit
   section, delta table and provenance/status.
2. **Task 2: annotate the two catalog ids, meta repo only** — `4b075577` (docs, meta
   repo) — annotated `MSG_ERR_NOT_BLANK` (0xB0) and `DBG_FLAG_SKIP_BLANK` (0x2E) in
   `tools/catalog/messages.toml`.

**Plan metadata:** none separate — both task commits above are the plan's full scope; no
firmware commit was needed (no sub-repo source touched by either task).

_Note: no TDD tasks in this plan._

### Added scope (orchestrator-added, not plan-authored — reported separately)

3. **Repair three stale prose citations** — `c7c1d9a` (docs, `firestarter_app`) — reworded
   `cli_handlers.py:1102`'s `flash_nor_unlock.cpp:41` tense and `test_uv_mask.py:201` /
   `report_shapes.py:653`'s `FLAG_SKIP_BLANK_CHECK` mentions. Followed by:
   - `fffa6762` (docs, meta repo) — `deferred-items.md`'s three findings marked resolved.
   - `c74433f5` (chore, meta repo) — advanced the `firestarter_app` gitlink to `c7c1d9a`.

## Files Created/Modified

- `.planning/phases/205-the-pre-flights-leave-the-firmware/205-FLASH-RAM.md` — phase-exit
  section, delta table, restated build configuration, frontmatter status flipped to
  complete.
- `tools/catalog/messages.toml` — two new comment blocks, no field values changed.
- `.planning/phases/205-the-pre-flights-leave-the-firmware/deferred-items.md` — all three
  findings marked `status: resolved` (added scope).
- `firestarter_app/firestarter/cli_handlers.py` — one docstring sentence reworded to past
  tense (added scope).
- `firestarter_app/tests/test_uv_mask.py` — one docstring phrase reworded (added scope).
- `firestarter_app/tests/fixtures/report_shapes.py` — one docstring phrase reworded (added
  scope).

## Decisions Made

- **Phase-exit is the post-fix tree re-measured, not a fresh commit.** No firmware commit
  landed between plan 05's task 2 and this plan, so `firestarter_fw` HEAD stayed at
  `6e11d057b59977dd870c1ddcc588dd2f6f3ea1db` throughout this plan's task 1. Re-measuring
  rather than copying plan 05's figures is what the plan's own prohibition (T-205-22)
  requires; the six digests and three `Flash:`/`RAM:` lines came out byte-identical to
  plan 05's post-fix section both times, which is itself the evidence that no drift
  occurred, not a shortcut taken instead of measuring.
- **0xB0's annotation names the divergence explicitly rather than following the plain
  204 shape verbatim.** `MSG_ERR_NOT_BLANK` is not orphaned on the host the way the three
  debug ids are — a post-3.1.0 host still receives it from pre-3.1.0 firmware, which is the
  exact skew plan 07's bench leg observes on silicon (D-08). The annotation states this as
  the reason it is deliberately still *rendered*, not merely retained.
- **Fixed an annotation self-reference trap found while writing the 0x2E comment.** Writing
  the retired identifier's own name inside its annotation prose (`LOG_DEBUG_ID_SUB(DBG_FLAG_SKIP_BLANK)`)
  created an earlier string match than the actual `name =` line, which broke the plan's own
  `t.index()`-based verify one-liner (it found the annotation's self-reference instead of
  the field, so the 1400-char lookback window missed the closing "Not free for reuse."
  sentence — itself initially split across a line wrap, a second instance of the same class
  of bug). Fixed both: paraphrased the self-reference, and kept "Not free for reuse." on one
  unwrapped comment line. Recorded as a Rule 1 auto-fix (bug in the annotation's own
  verifiability), not a deviation from the plan's intent.
- **deferred-items.md's three entries were marked resolved, not deleted.**
  `205-04-SUMMARY.md` already cites the file by path as evidence of the deviation it
  recorded ("`deferred-items.md` — new; three out-of-scope stale-citation findings"; see
  its `key-files.created` and Deviations section). Deleting the file once it held nothing
  open would make that existing citation stale — exactly the failure mode this project's
  standing citation-repair rule exists to prevent — so all three were flipped to
  `status: resolved` in place instead.
- **The citation repair landed as its own `firestarter_app` commit**, separate from both
  plan-authored commits, per the orchestrator's instruction that added scope be committed
  and reported distinctly from the plan's own tasks.

## Deviations from Plan

None from the plan's own two tasks — both executed exactly as written. The self-reference
fix during task 2 (documented above under Decisions Made) is a Rule 1 auto-fix to the
annotation text's own verifiability, not a deviation from the plan's intent or scope; the
annotation content itself matches everything the plan's `<action>` and `<acceptance_criteria>`
required.

The three-citation repair and `deferred-items.md` update are the orchestrator's added scope,
not a plan deviation — reported in their own section above, per the orchestrator's
instruction.

**Total deviations:** 0 auto-fixed against the plan's own tasks. **Impact:** none — the
plan's stated scope and this SUMMARY's coverage match exactly.

## Issues Encountered

None beyond the self-reference/line-wrap verify-script trap described above, which was
found and fixed while still inside task 2's own verification loop before the task was
considered complete.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `205-FLASH-RAM.md` is complete: phase-entry, plan-05 fix-cost and phase-exit sections all
  filled, cross-checked, with twelve artifact digests and three commit shas. FWBLANK-05 is
  fully satisfied.
- `tools/catalog/messages.toml`'s four orphaned ids (0x08, 0x0B from phase 204; 0xB0, 0x2E
  from this plan) are all annotated and kept, ready for plan 07's B3 bench leg to observe
  0xB0 rendered on silicon from pre-205 firmware.
- `deferred-items.md` now holds zero open findings for this phase.
- No blocker for plan 07. This plan touched no file plan 07 is expected to modify, and left
  both sub-repository working trees clean.

## Self-Check: PASSED

- `[ -f /workspaces/.planning/phases/205-the-pre-flights-leave-the-firmware/205-FLASH-RAM.md ]` → FOUND
- `[ -f /workspaces/tools/catalog/messages.toml ]` → FOUND
- `[ -f /workspaces/firestarter_app/firestarter/cli_handlers.py ]` → FOUND
- `[ -f /workspaces/firestarter_app/tests/test_uv_mask.py ]` → FOUND
- `[ -f /workspaces/firestarter_app/tests/fixtures/report_shapes.py ]` → FOUND
- `git -C /workspaces log --oneline --all | grep -q 84dd34b5` → FOUND
- `git -C /workspaces log --oneline --all | grep -q 4b075577` → FOUND
- `git -C /workspaces log --oneline --all | grep -q fffa6762` → FOUND
- `git -C /workspaces log --oneline --all | grep -q c74433f5` → FOUND
- `git -C /workspaces/firestarter_app log --oneline --all | grep -q c7c1d9a` → FOUND
- Re-ran task 1's `<verify>`: clean `pio run` printed 3 `Flash:`/3 `RAM:` lines, 6 digests
  produced, `git status --porcelain` in `firestarter_fw` empty, `205-FLASH-RAM.md`
  heading/token check printed "FWBLANK-05 record complete" — all PASS.
- Re-ran task 2's `<verify>`: catalog validator "OK: catalog valid (79 messages, version
  1)"; committed-file-list check showed exactly `tools/catalog/messages.toml`; both
  sub-repo `git status --porcelain` empty (only the pre-existing untracked
  `datasheets/LST62832I.pdf` in `firestarter_app`, unrelated and left alone); annotation
  content check printed "both catalog ids annotated" — all PASS.
- Re-ran the added-scope task's proof: `firestarter_app/.venv-ci-188/bin/python -m pytest
  tests/ -o addopts="" -q` → 2319 passed, 36 snapshots passed; `ruff check` on all three
  modified files → All checks passed.
- `git -C /workspaces/firestarter_fw rev-parse --abbrev-ref HEAD` → `v1.41-verification-to-host`
- `git -C /workspaces/firestarter_app rev-parse --abbrev-ref HEAD` → `v1.41-verification-to-host`
- `git -C /workspaces rev-parse --abbrev-ref HEAD` → `v1.41-verification-to-host`
- Meta gitlink for `firestarter_app` (`git ls-tree HEAD -- firestarter_app`) →
  `c7c1d9a1c8207e77cf539ca0c68b6a01d317e888`, matching `firestarter_app` HEAD exactly.
- Meta gitlink for `firestarter_fw` (`git ls-tree HEAD -- firestarter_fw`) →
  `6e11d057b59977dd870c1ddcc588dd2f6f3ea1db`, matching `firestarter_fw` HEAD exactly
  (unchanged by this plan — no firmware source was touched).
- No push was made to any branch in any repository during this plan.

---
*Phase: 205-the-pre-flights-leave-the-firmware*
*Completed: 2026-09-22*
