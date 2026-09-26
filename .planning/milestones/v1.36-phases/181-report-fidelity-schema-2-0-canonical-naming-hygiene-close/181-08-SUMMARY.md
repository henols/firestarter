---
phase: 181-report-fidelity-schema-2-0-canonical-naming-hygiene-close
plan: 08
subsystem: dev-test-engine
tags: [chip-id, structured-field, echo-not-readback, write-refusal-predicate, slots-remaining, ladder-fold, dedup-fingerprint]

requires:
  - phase: 181-report-fidelity-schema-2-0-canonical-naming-hygiene-close
    plan: "07"
    provides: "fingerprint siblings exported, divergence exported and recorded on agreement, _STEPS_ELEMENT_0_KEYS at 19 keys, D-16 re-proven"
provides:
  - "StepResult.chip_id_detected -- one additive int|None field fed by the value operator.check_eprom_id already returns and previously discarded on a pass (RPT-A5, D-23). _dispatch_id's mismatch gate, verdict expression and both reason strings stay byte-identical."
  - "_chip_id_fields reads chip_id_actual STRUCTURALLY off the id step's own field instead of scraping reason.rsplit('0x'); chip_id_actual populates on a PASSING id check as well as on a mismatch, with no companion provenance key (RPT-A1)"
  - "The honesty ceiling stated in three places (StepResult docstring, _chip_id_fields docstring, evidence transcript): on a pass, check_eprom_id's OK reply carries no id back from the firmware, so the value is the host's own expected id echoed out of the command dict -- chip_id_actual on a pass equals chip_id_expected and records the id the check was verified AGAINST, never an independent read-back"
  - "render()'s chip_id row guard extended (is None OR == chip_id_expected) to preserve D-10's one-sided-on-agreement invariant now that chip_id_actual populates on a pass -- a necessary deviation from the plan's literal 'do not touch' framing, proven output-identical by a real Click invocation and a unit render test"
  - "steps[].chip_id_detected exported unconditionally; _STEPS_ELEMENT_0_KEYS moved 19 -> 20 in the same commit"
  - "chip_test._write_step_was_refused(results) -- one module-level predicate, true iff results carries a write-op (OP_WRITE/OP_WRITE_PARTIAL) result whose verdict is SKIPPED. Two call sites: _write_coverage_line (D-20) and build_db_diff's fourth arm (D-21)."
  - "_write_coverage_line's slots-remaining sentence reports the AFTER-this-run count (resolved count - 1) when the write ran, and the resolved count unreduced when it was refused -- the resolver's own slots_remaining=slots_total-slot_index expression stays byte-unchanged (D-20, T-179-07)"
  - "build_db_diff's fourth arm gains a write-refusal disqualifier: a SKIPPED write withholds the candidate/community-reported disposition a verified PASS proposes; NA and OK writes are unaffected (D-21, T-179-05). 19-shape census: 5 flips, all M27C512 shapes whose write is genuinely SKIPPED (exhausted slots) -- the defect closing, not a regression."
  - "Three planted-RED anti-vacuity legs prove the two new gates are not vacuous: an over-broad NA-as-refusal predicate, a no-condition (always-subtract) slots implementation, and a bare empty-expected-set comparison -- all observed RED, zero fixture files written"
  - "Both folded todos (2026-09-08-uv-ladder-flip-on-exhausted-slots.md, 2026-09-08-slots-remaining-off-by-one-at-target-resolution.md) edited in place: resolves_phase: none -> 181"
  - "D-16 re-proven three times (after Task 1's additive key, after Task 2's disposition/slots changes, after Task 3): all 19 FROZEN_HASHES literals byte-identical to app base 04fd982, md5 of the sorted literal set unchanged (555a6d762d528102b74061b504183df6)"
affects: [181-09, 181-10]

actuals:
  tokens: 24210
  tasks: 3
  commits: 6
  plan_head_before: 2b3e957905de28d01881096d00f308c1af5ed972

tech-stack:
  added: []
  patterns:
    - "structural-field-not-prose-scrape: the detected chip id crosses chip_test.py -> cli_handlers.py -> diagnostic_report.py as an integer StepResult field, never recovered by parsing StepResult.reason -- a reword of the human sentence can no longer silently return None"
    - "one-predicate-two-call-sites: a single module-level predicate in the engine (chip_test.py) answers 'did a write actually run' for both the report's slots-remaining disclosure and its advisory ladder fold, so the two folded defects (D-20, D-21) cannot drift into two look-alike-but-different expressions"
    - "subtract-at-the-disclosure-point-not-the-resolver: WriteTarget.slots_remaining stays a resolve-time (before-this-run) count; the after-this-run arithmetic lives at _write_coverage_line, the one place that holds both the resolved count and the run's own outcome -- a resolver-side subtraction would assert a consumption that may never occur"
    - "extend-a-guard-condition-rather-than-recompute-a-branch: render()'s pre-existing chip_id_actual-is-None guard was extended with an equality clause instead of being restructured, keeping the two display branches (one-sided/two-sided) byte-unchanged while their governing condition absorbed the new field semantics"

key-files:
  created:
    - .planning/phases/181-report-fidelity-schema-2-0-canonical-naming-hygiene-close/evidence/181-08-chip-id-structured.txt
    - .planning/phases/181-report-fidelity-schema-2-0-canonical-naming-hygiene-close/evidence/181-08-write-refused-predicate.txt
  modified:
    - firestarter_app/firestarter/chip_test.py
    - firestarter_app/firestarter/cli_handlers.py
    - firestarter_app/firestarter/diagnostic_report.py
    - firestarter_app/tests/test_blast_radius_invariance.py
    - firestarter_app/tests/test_chip_test.py
    - firestarter_app/tests/test_chip_test_cycle.py
    - firestarter_app/tests/test_diagnostic_report.py
    - firestarter_app/tests/test_dev_test_cmd.py
    - firestarter_app/tests/fixtures/reports/*.json (19 files across two additive/disposition-change rounds)
    - .planning/todos/pending/2026-09-08-uv-ladder-flip-on-exhausted-slots.md
    - .planning/todos/pending/2026-09-08-slots-remaining-off-by-one-at-target-resolution.md

key-decisions:
  - "render()'s chip_id row guard was extended (is None OR == chip_id_expected) rather than left untouched as the plan's orchestrator_dispositions literally said. Forced by the plan's own acceptance criteria (the end-to-end test explicitly named 'D-10's gate'): with chip_id_actual now populated (== chip_id_expected) on every pass, the original is-None-only guard would have rendered a two-sided 'expected/actual' pair on every clean run, violating the explicit prohibition that a matching pair is never added to the table. The two display branches' content stayed byte-unchanged; only the governing condition grew one clause. Proven output-identical for every historical shape by a real Click invocation plus a unit render test."
  - "The pre-existing 8-line comment above that guard, which explained the OLD (now-false) mechanism, was deleted outright rather than reworded -- per this phase's own established precedent (a pure deletion cannot exceed the comment-census baseline; a reword always can) and per CLAUDE.md's hard no-comments rule. The up-to-date rationale lives in StepResult's and _chip_id_fields' docstrings and in this plan's evidence transcript."
  - "Three pre-existing tests collided with the D-21 write-refusal disqualifier because they hand-constructed a 'PASS-only, no BAD verdicts' shape using a SKIPPED WRITE-op result specifically: two in test_diagnostic_report.py were retargeted to a non-write SKIPPED op (blank-check), preserving their original claim; LADDER_PINS in test_blast_radius_invariance.py moved its five m27c512-* entries from candidate/community-reported to no-change/'' in the SAME commit as the behavior change, following the file's own established re-key-with-behavior discipline (matching how Phase 177 moved two other shapes' pins) -- this is a real, deliberate re-key of a disposition pin, not an accidental drift."
  - "The write-refusal predicate is placed in chip_test.py (the engine), not diagnostic_report.py (the report), because it reads the engine's own op/verdict vocabulary (OP_WRITE/OP_WRITE_PARTIAL, VERDICT_SKIPPED) -- matching the project's existing precedent (_id_step_closes_gate, _baseline_closes_sdp_gate) of keeping verdict-interpretation predicates where the vocabulary is owned."

requirements-completed: [RPT-A1, RPT-A5]

coverage:
  - id: D1
    description: "StepResult carries chip_id_detected, fed by _dispatch_id on all three id-dispatch paths (pass/mismatch/not-ok), with both reason strings byte-identical to base"
    requirement: RPT-A5
    verification:
      - kind: unit
        ref: "tests/test_chip_test.py::test_dispatch_id_pass_records_the_echoed_expected_id, ::test_dispatch_id_mismatch_records_the_firmware_reported_id, ::test_dispatch_id_not_ok_with_no_id_leaves_chip_id_detected_none"
        status: pass
      - kind: unit
        ref: "Task 1 inline verify leg 1 (all three cases, exact reason strings asserted)"
        status: pass
    human_judgment: false
  - id: D2
    description: "_chip_id_fields reads chip_id_actual structurally off chip_id_detected (no rsplit scrape); populates on a PASS as well as on a mismatch; chip_id_mismatch_reason still comes from reason prose only on a mismatch"
    requirement: RPT-A1
    verification:
      - kind: unit
        ref: "tests/test_dev_test_cmd.py::test_a_clean_run_saves_a_populated_chip_id_actual_equal_to_expected (real Click invocation, w27c020, DB chip-id 55941 echoed on pass)"
        status: pass
      - kind: unit
        ref: "Task 1 inline verify leg 2 (AST: chip_id_detected present, rsplit absent, docstring mentions 'structural')"
        status: pass
    human_judgment: false
  - id: D3
    description: "The console chip_id row stays one-sided on agreement and two-sided only on a real mismatch, even though chip_id_actual now populates on a pass -- D-10's invariant preserved by an extended guard condition, proven output-identical to base"
    requirement: RPT-A1
    verification:
      - kind: e2e
        ref: "tests/test_dev_test_cmd.py::test_a_clean_run_saves_a_populated_chip_id_actual_equal_to_expected (asserts 'chip_id (expected/actual)' absent from real rendered console output on a clean pass)"
        status: pass
      - kind: unit
        ref: "tests/test_diagnostic_report.py::test_chip_id_one_sided_row_when_actual_equals_expected, ::test_hex_cell_chip_id_both_populated_is_4_digit_upper_hex (retargeted to a genuine mismatch pair)"
        status: pass
    human_judgment: false
  - id: D4
    description: "chip_id_detected exported unconditionally in steps[]; _STEPS_ELEMENT_0_KEYS moved 19 -> 20 in the same commit"
    requirement: RPT-A5
    verification:
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py::test_to_dict_steps_element_0_key_list_is_pinned"
        status: pass
      - kind: unit
        ref: "Task 1 inline verify leg 3 (distinct_step_key_sets=1, step_key_count=20)"
        status: pass
    human_judgment: false
  - id: D5
    description: "One write-refusal predicate (_write_step_was_refused), two call sites, returns true only for a SKIPPED write-op result"
    verification:
      - kind: unit
        ref: "Task 2 inline verify leg 1 (7 cases: SKIPPED write/write-partial true; OK/BAD/NA write false; SKIPPED non-write false; empty list false)"
        status: pass
    human_judgment: false
  - id: D6
    description: "The slots-remaining sentence reports the after-this-run count (resolved - 1) when the write ran, and the resolved count unreduced when refused; the resolver's own expression and the virgin-part assertion are both byte-unchanged"
    verification:
      - kind: unit
        ref: "tests/test_chip_test_cycle.py::test_slots_remaining_line_reports_after_this_run_when_the_write_ran, ::test_slots_remaining_line_reports_the_resolved_count_when_the_write_was_refused"
        status: pass
      - kind: unit
        ref: "Task 2 inline verify leg (grep: resolver expression and virgin-part assertion both present, unchanged)"
        status: pass
    human_judgment: false
  - id: D7
    description: "build_db_diff withholds the candidate disposition for a SKIPPED write and is unchanged for NA and for a clean OK run; all 19 shapes censused, 5 flips recorded (all M27C512, all genuinely SKIPPED writes, zero flips on OK/NA)"
    verification:
      - kind: unit
        ref: "tests/test_diagnostic_report.py::test_a_refused_write_disqualifies_the_fourth_arm_but_na_and_ok_do_not"
        status: pass
      - kind: other
        ref: "evidence/181-08-write-refused-predicate.txt Section 4 (full 19-shape before/after census)"
        status: pass
    human_judgment: false
  - id: D8
    description: "Three planted-RED legs prove the D-20/D-21 gates are not vacuous: an over-broad NA-as-refusal predicate, a no-condition slots implementation, and an empty-expected-set comparison, all in-memory, zero fixture files"
    verification:
      - kind: unit
        ref: "tests/test_diagnostic_report.py::test_a_planted_na_as_refusal_disqualifier_reddens_the_na_case_claim, ::test_a_planted_missing_write_ran_condition_reddens_the_refused_slots_claim, ::test_comparing_a_real_disposition_against_an_empty_expected_set_fails_rather_than_passes_vacuously"
        status: pass
    human_judgment: false
  - id: D9
    description: "Both folded todos (T-179-05, T-179-07) edited in place, resolves_phase: none -> 181, neither moved nor deleted"
    verification:
      - kind: other
        ref: "grep -qF 'resolves_phase: 181' on both files; git status --porcelain .planning/todos/ shows no deletion"
        status: pass
    human_judgment: false
  - id: D10
    description: "All 19 FROZEN_HASHES literals byte-identical to app base 04fd982 across every additive/disposition change in this plan; md5 of the sorted literal set matches 555a6d762d528102b74061b504183df6"
    verification:
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py -k test_dedup_fingerprint_is_frozen (19 passed, re-run after every task)"
        status: pass
      - kind: other
        ref: "git diff 04fd982 -- tests/fixtures/report_shapes.py: empty, at every checkpoint"
        status: pass
    human_judgment: false
  - id: D11
    description: "Zero # comments added to product source across the mandated full census (git diff --name-only 04fd982..HEAD, all .py files); files over baseline: 0/27"
    verification:
      - kind: unit
        ref: "Mandated tokenize COMMENT-token census script, run after every task and at plan end: files over baseline: 0/27"
        status: pass
    human_judgment: false
  - id: D12
    description: "Whole-repo porcelain across the meta repo, the firmware submodule, and the app repo after this plan's own commits"
    verification:
      - kind: other
        ref: "git -C /workspaces/firestarter status --porcelain (clean); git -C /workspaces/firestarter_app status --porcelain firestarter/ (clean); git -C /workspaces/firestarter_app status --porcelain (clean, whole repo)"
        status: pass
    human_judgment: false

duration: ~50min
completed: 2026-09-09
status: complete
---

# Phase 181 Plan 08: The detected chip ID becomes a structured field; one write-refusal predicate closes two folded defects Summary

**`StepResult.chip_id_detected` replaces a `reason.rsplit("0x")` scrape with a structural integer field, `chip_id_actual` now populates on a passing id check with the echo-not-read-back ceiling stated in three places, and one `_write_step_was_refused` predicate simultaneously fixes the exhausted-slots ladder false-green and the slots-remaining off-by-one — with a necessary render() guard extension keeping the console `chip_id` row one-sided on agreement.**

## Performance

- **Duration:** ~50 min
- **Started:** 2026-09-09 (required-reading pass)
- **Completed:** 2026-09-09T15:02Z
- **Tasks:** 3 of 3 completed
- **Files modified:** 9 app-repo product/test files + 19 regenerated report-snapshot fixtures (touched across two rounds) + 2 meta-repo evidence transcripts + 2 meta-repo todo frontmatter edits

## Accomplishments

- **Task 1 — the detected chip ID becomes a structured field, `chip_id_actual` populates on a pass, and a necessary deviation preserves D-10.** `StepResult` gained `chip_id_detected: int | None = None`, fed by `_dispatch_id`'s already-in-hand `detected_id` on all three paths (pass/mismatch/not-ok); the mismatch gate, verdict expression and both reason strings stayed byte-identical (D-23), proven by exact-string asserts. `_chip_id_fields`' single mismatch-only loop became two independent reads: `chip_id_actual` now reads `chip_id_detected` structurally whenever the id step ran, populating on a PASS (RPT-A1) as well as a mismatch, with `chip_id_mismatch_reason` still sourced from prose only on a mismatch. On a pass, `check_eprom_id`'s OK reply carries no id back from the firmware — the value is the host's own expected id, echoed out of the command dict — so `chip_id_actual` equals `chip_id_expected` exactly and records the id the check was verified AGAINST, never an independent read-back; this ceiling is stated in `StepResult`'s docstring, `_chip_id_fields`' docstring, and the evidence transcript. Measuring against the plan's own explicit e2e acceptance test surfaced a genuine tension the plan's `orchestrator_dispositions` framing ("do not touch the console row") did not resolve: with `chip_id_actual` now populated (`== chip_id_expected`) on every pass, `render()`'s original `is None`-only guard would have rendered a two-sided "expected/actual" pair on every clean run — exactly what D-10's prohibition forbids. The guard was extended to `is None or == chip_id_expected`, keeping both display branches' content byte-unchanged while their governing condition absorbed the new field semantics; proven output-identical to every historical shape by a real Click invocation (`w27c020`, DB chip-id `55941` echoed on a pass) and a unit-level render test. The now-false 8-line comment explaining the old mechanism was deleted outright (pure deletion, matching this phase's own precedent) rather than reworded. Two pre-existing tests that had hand-constructed an equal expected/actual pair purely to exercise hex formatting were retargeted to a genuine mismatch pair. `_step_dict` exports `chip_id_detected` unconditionally; `_STEPS_ELEMENT_0_KEYS` moved 19 → 20 in the same commit. 19 report-shape snapshots regenerated (18 changed, `synthetic-arm4-empty-results` unaffected — zero steps), each diff confined to the added key; zero frozen-hash literal lines moved.
- **Task 2 — one "did a write actually run" predicate closes two folded defects.** `chip_test._write_step_was_refused(results)` — a module-level predicate, `True` iff `results` carries a write-op result (`OP_WRITE`/`OP_WRITE_PARTIAL`) whose verdict is `SKIPPED`, read via `getattr`-with-safe-default in `run_errored`'s own style — is the single answer both D-20 and D-21 consume, with `NA` deliberately excluded so an unsupported-write part's disposition never moves. `_write_coverage_line` (D-20, T-179-07) now subtracts one from the resolved `slots_remaining` when the write actually ran, and reports the resolved count unreduced when it was refused; the resolver's `slots_remaining=slots_total - slot_index` expression and the virgin-part test assertion both stay byte-unchanged — the subtraction lives at the disclosure point, the one place both the count and the outcome are known. `build_db_diff`'s fourth arm (D-21, T-179-05) gained the disqualifier as an extra condition, computed before the arm chain beside `run_errored`. A full 19-shape census (composing `build_db_diff` onto every frozen shape's own results, both through the old and the new arm logic) found exactly 5 flips — all M27C512 shapes whose `write` step genuinely reads `SKIPPED` ("every UV slot exhausted"), moving from candidate/community-reported to no-change/"" — the T-179-05 defect closing, not a regression; zero flips occurred on any OK or NA write, matching the plan's own stop condition. Three pre-existing tests collided because they had hand-built a "PASS-only, no BAD" shape using a SKIPPED *write*-op result specifically: two in `test_diagnostic_report.py` retargeted their SKIPPED step to a non-write op (`blank-check`), preserving their original claim; `test_blast_radius_invariance.py`'s `LADDER_PINS` moved its five `m27c512-*` entries in this same commit, following the file's own established re-key-with-behavior discipline (matching how two other shapes moved in Phase 177) — the coverage sentinel confirms all four `build_db_diff` arms stay populated after the move. 19 snapshots regenerated again (6 changed: 5 disposition/ladder_state, 1 slots-sentence on `uv-slot-write-pass`, a UV write that genuinely ran); `dedup_fingerprint` stays byte-identical throughout (`db_diff` is outside its pre-image).
- **Task 3 — three planted counter-examples, observed RED; both folded todos now name this phase.** Following this project's anti-vacuity house style (`test_readback_inventory.py`'s assert-the-anchor-first triad), three legs prove the two new gates are not vacuous, all in-memory/in-process with zero fixture files written: (1) an over-broad predicate that also treats NA as a refusal, monkeypatched onto `diagnostic_report._write_step_was_refused` for one test's duration, confirmed to actually differ from the real predicate on the anchor input, then shown to change the NA-case disposition (RED); (2) a no-condition (always-subtract) slots implementation's output for a REFUSED write, computed and shown to differ from the real function's correct "unreduced" output (RED); (3) a standalone vacuity leg comparing a real disposition against an empty expected set, shown to raise `AssertionError` rather than pass (RED). Both folded todos (`2026-09-08-uv-ladder-flip-on-exhausted-slots.md`, `2026-09-08-slots-remaining-off-by-one-at-target-resolution.md`) edited in place, `resolves_phase: none` → `resolves_phase: 181`, neither moved nor deleted. The invariance re-proof closes with `frozen_hash_literal_count=19`, zero literal lines moved since app base `04fd982`, and `shapes_reproducing=19/19`.
- **Zero `#` comments added to product source.** The mandated full census (`git diff --name-only 04fd982..HEAD`, all `.py` files, 27 files) found `files over baseline: 0/27` at every checkpoint this plan re-ran it — including the deliberate net *reduction* from Task 1's comment deletion (cli_handlers.py 357→356, diagnostic_report.py 207→199).

## Task Commits

Each task committed atomically, split across the app submodule (code) and the meta repo (evidence/todos):

1. **Task 1: chip_id_detected structured field + chip_id_actual on a pass**
   - `ade31d9` (feat, app repo): the field, `_dispatch_id`'s kwarg, `_chip_id_fields`' rewrite, `_step_dict`'s key, the render() guard extension, the comment deletion, five new tests, 19 regenerated snapshots
   - `b86de7cf` (docs, meta repo): `181-08-chip-id-structured.txt`
2. **Task 2: one write-refusal predicate, two folded defects**
   - `d3efc7e` (fix, app repo): the predicate, both call sites' wiring, both docstrings, two slots-branch tests, three ladder tests, the 5-entry LADDER_PINS re-key, 6 regenerated snapshots
   - `7e048768` (docs, meta repo): `181-08-write-refused-predicate.txt` (Task 2 portion)
3. **Task 3: three planted counter-examples; both folded todos resolve to Phase 181**
   - `19eaec5` (test, app repo): the three planted-RED legs
   - `091d009f` (docs, meta repo): `181-08-write-refused-predicate.txt` extended (Task 3 portion, final) + both todo frontmatter edits

**Plan metadata commit:** this SUMMARY.md, committed separately in the meta repo per the sequential-executor protocol (`STATE.md`/`ROADMAP.md` NOT touched — owned by the orchestrator).

## Files Created/Modified

- `firestarter_app/firestarter/chip_test.py` — `StepResult.chip_id_detected`; `_dispatch_id`'s kwarg; `_write_step_was_refused`, the shared predicate
- `firestarter_app/firestarter/cli_handlers.py` — `_chip_id_fields`' structural two-read rewrite and docstring
- `firestarter_app/firestarter/diagnostic_report.py` — `_step_dict`'s `chip_id_detected` key; `render()`'s extended guard (comment deleted); `_write_coverage_line`'s after-this-run arithmetic; `build_db_diff`'s fourth-arm disqualifier
- `firestarter_app/tests/test_blast_radius_invariance.py` — `_STEPS_ELEMENT_0_KEYS` gains `chip_id_detected` (19→20); `LADDER_PINS`' five m27c512 entries re-keyed with an accompanying rationale paragraph
- `firestarter_app/tests/test_chip_test.py` — three id-dispatch tests plus the pass-path echo equality test; `_dispatch_id` added to imports
- `firestarter_app/tests/test_chip_test_cycle.py` — two slots-branch tests (write ran / write refused)
- `firestarter_app/tests/test_diagnostic_report.py` — one console-row one-sided-on-agreement test; the retargeted hex-cell mismatch test; three ladder-disqualifier tests; three planted-RED anti-vacuity tests; `Step` added to imports
- `firestarter_app/tests/test_dev_test_cmd.py` — one end-to-end pass-path chip-id test (asserts both the populated field and D-10's console-row invariant)
- `firestarter_app/tests/fixtures/reports/*.json` (19 files) — regenerated via `tools/snapshot_report_shapes.py` across two rounds (Task 1's additive key, Task 2's disposition/slots changes)
- `.planning/phases/181-.../evidence/181-08-chip-id-structured.txt` — Task 1's four-case/scalar/ceiling/deviation transcript
- `.planning/phases/181-.../evidence/181-08-write-refused-predicate.txt` — Tasks 2+3's predicate/scalar/19-shape-census/planted-RED transcript
- `.planning/todos/pending/2026-09-08-uv-ladder-flip-on-exhausted-slots.md` — `resolves_phase: none` → `181`
- `.planning/todos/pending/2026-09-08-slots-remaining-off-by-one-at-target-resolution.md` — `resolves_phase: none` → `181`

## Decisions Made

See `key-decisions` in frontmatter for the full text. In summary: `render()`'s chip_id guard was extended (not left alone) because the plan's own acceptance test demanded it, with the pre-existing comment explaining the old mechanism deleted rather than reworded; three pre-existing tests that collided with the new write-refusal disqualifier were retargeted rather than left red, including a deliberate `LADDER_PINS` re-key landed in the same commit as its behavior change; and the shared predicate lives in the engine module (`chip_test.py`), matching this project's existing pattern for verdict-interpretation predicates.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `render()`'s chip_id row guard needed extending, not leaving alone, to satisfy D-10 under the new pass-path population**
- **Found during:** Task 1, while implementing `_chip_id_fields`' structural read
- **Issue:** The plan's `orchestrator_dispositions` said "do not touch" the console row, but its own acceptance criteria (the `test_dev_test_cmd.py` end-to-end test explicitly named "D-10's gate") require the row to stay one-sided on agreement. With `chip_id_actual` now populated (`== chip_id_expected`) on every pass, the untouched `is None`-only guard would have rendered a two-sided pair on every clean run — a direct violation of the explicit prohibition "a matching pair is not added to the table."
- **Fix:** Extended the guard to `is None or == chip_id_expected`. Both display branches' content stayed byte-unchanged. Deleted the now-false 8-line comment above the guard (pure deletion, per this phase's own established precedent for a falsified comment) rather than rewording it.
- **Files modified:** `firestarter_app/firestarter/diagnostic_report.py`
- **Verification:** Real Click invocation (`test_a_clean_run_saves_a_populated_chip_id_actual_equal_to_expected`) confirms no two-sided row in rendered output on a clean pass; unit test confirms the same at the `_minimal_report` level; the AST verify leg confirms `render()` still contains exactly one two-sided-row site and one `is None` guard line.
- **Committed in:** `ade31d9` (Task 1 commit)

**2. [Rule 1 - Bug] Two pre-existing hex-formatting/one-sided-row tests hand-constructed an equal expected/actual pair, which now collides with D-10's agreement invariant**
- **Found during:** Task 1, running `tests/test_diagnostic_report.py`
- **Issue:** `test_hex_cell_chip_id_both_populated_is_4_digit_upper_hex` set `chip_id_expected == chip_id_actual == 0x1234` purely to exercise the two-sided row's hex formatting — under RPT-A1 this is exactly the agreement case D-10 now requires to render one-sided, so the assertion failed.
- **Fix:** Retargeted to a genuine mismatch pair (`0x1234 / 0x5678`), preserving the original intent. Added a new dedicated test (`test_chip_id_one_sided_row_when_actual_equals_expected`) for the equal-and-populated case. Updated `test_chip_id_one_sided_row_when_no_mismatch_was_recorded`'s docstring, which had asserted the now-false "populated ONLY on a mismatch" claim.
- **Files modified:** `firestarter_app/tests/test_diagnostic_report.py`
- **Verification:** Full module suite green (84/84 before Task 2's additions).
- **Committed in:** `ade31d9` (Task 1 commit)

**3. [Rule 1 - Bug] Three pre-existing tests hand-constructed a "PASS-only" shape using a SKIPPED write-op result, colliding with D-21's write-refusal disqualifier**
- **Found during:** Task 2, running `tests/test_diagnostic_report.py` and `tests/test_blast_radius_invariance.py`
- **Issue:** `test_db_diff_verdict_mapping` and `test_ladder_state_verdict_mapping` both used `StepResult(op="write", verdict=VERDICT_SKIPPED)` to represent a generic "OK + NA/SKIPPED, no BAD" shape — exactly the shape D-21 now correctly withholds candidate for. `LADDER_PINS`' five `m27c512-*` entries pinned the OLD (buggy) candidate/community-reported disposition for shapes whose write step is genuinely SKIPPED (exhausted slots) — the exact T-179-05 defect this plan closes.
- **Fix:** Retargeted the two hand-built tests' SKIPPED step to a non-write op (`blank-check`), preserving their original claim; documented the retarget in each docstring. Re-keyed `LADDER_PINS`' five entries to no-change/"" in the SAME commit as the behavior change, with an accompanying rationale paragraph added to the module docstring, following the file's own established convention for this exact dict.
- **Files modified:** `firestarter_app/tests/test_diagnostic_report.py`, `firestarter_app/tests/test_blast_radius_invariance.py`
- **Verification:** Both modules' full suites green; the coverage sentinel (`test_ladder_pins_cover_all_four_build_db_diff_arms`) confirms all four `build_db_diff` arms stay populated after the re-key.
- **Committed in:** `d3efc7e` (Task 2 commit)

---

**Total deviations:** 3 auto-fixed, all Rule 1 (bugs — code or a test asserting behavior this plan's own requirements falsify). **Impact:** All three were necessary to satisfy this plan's own acceptance criteria (RPT-A1's console-row invariant, D-21's write-refusal fix) as written. None widened scope beyond RPT-A1/RPT-A5/D-20/D-21. No scope creep — every touched test was already colliding with a requirement this plan was explicitly asked to deliver.

## Issues Encountered

None beyond the deviations above.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

RPT-A1 and RPT-A5 are both fully discharged. `steps[].chip_id_detected` is a structured field, exported unconditionally, fed by the value the id dispatch already had; `chip_id_actual` populates on a passing check with the echo ceiling stated in three places and no companion provenance key; the console `chip_id` row stays one-sided on agreement, proven by a real Click invocation. D-20 and D-21 are both discharged by one shared predicate with two call sites: the slots-remaining sentence now reports the after-this-run count, and `build_db_diff`'s fourth arm no longer proposes a verified PASS's disposition for a run that wrote nothing — closing both T-179-05 and T-179-07 with a full 19-shape census recorded rather than absorbed. D-16 holds after every additive/disposition change in this plan: 19 frozen hashes, zero moved literal lines. `steps[]` now carries 20 keys per element (was 19 at this plan's start). Both folded todos name Phase 181; plan `181-10` owns moving them to `completed/` after the phase's own verification.

**Do not run the seven-leg green-tree battery here, do not invoke `check_rekey_ledger.py`, and do not assert a suite floor of 2239.** Per the plan's own `<verification>` section, that battery runs once, in `181-10`. This plan's own automated legs (per-module pytest across every touched/dependent module — 460 passed across the six-module combined run — `ruff check`/`ruff format --check`, the snapshot-drift check, the frozen-hash reproof, the mandated tokenize census, and the three porcelain legs) all pass independently of that battery.

## Comment Census (mandated full census, `git diff --name-only 04fd982..HEAD`, all `.py` files)

```
files over baseline: 0 / 27
```

Two comment counts actually FELL below their measured Task-1-start baselines (a legitimate direction the non-increase gate permits): `cli_handlers.py` 357→356 (the `_chip_id_fields` scrape's reason-format comment removed along with the code it annotated) and `diagnostic_report.py` 207→199 (the now-false 8-line console-row comment deleted outright, per this phase's established precedent for a falsified comment).

## Self-Check: PASSED

- Both evidence transcripts confirmed present on disk with `[ -f ]`.
- All six commit hashes confirmed present via `git log --oneline --all`: app `ade31d9`, `d3efc7e`, `19eaec5`; meta `b86de7cf`, `7e048768`, `091d009f`.
- `pytest` re-run across all six touched/dependent test modules combined (`test_chip_test.py`, `test_dev_test_cmd.py`, `test_blast_radius_invariance.py`, `test_diagnostic_report.py`, `test_chip_test_cycle.py`, `test_readback_inventory.py`): `460 passed`, zero failed/error/skipped.
- All plan-level `<verification>` items re-confirmed: the three id-dispatch cases with byte-identical reason strings; the structural `_chip_id_fields` read with no `rsplit`; the console row's exactly-one two-sided site and exactly-one `is None` guard line; `chip_id_detected` exported on every step element at the measured twenty-key count; exactly one write-refusal predicate with two call sites, returning `False` for NA; the slots sentence's after-this-run/refused-unreduced split with the resolver and virgin-part assertion both byte-unchanged; `build_db_diff` withholding candidate for a SKIPPED write and unchanged for NA/OK, all 19 shapes censused with every flip recorded; three planted-RED legs passing with zero fixture files; both folded todos naming Phase 181 with neither deleted; the snapshot-check and frozen-hash reproof both green; zero comment-count rises in the final diff; all three porcelain legs printing nothing.
- `ruff check firestarter/ tests/` and `ruff format --check firestarter/ tests/` both green (174 files formatted).
- `firestarter_app/tools/snapshot_report_shapes.py --check` exits 0.
- `firestarter/data/chip_database.json` untouched by this plan (not in `files_modified`; no diff exists for it).

---
*Phase: 181-report-fidelity-schema-2-0-canonical-naming-hygiene-close*
*Completed: 2026-09-09*
