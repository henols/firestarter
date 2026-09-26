---
phase: 180-read-step-sampling-conditional-on-phase-176
plan: 04
subsystem: testing
tags: [gap-closure, ast, pytest, seed-amendment, dev-test-fidelity]

# Dependency graph
requires:
  - phase: 180-read-step-sampling-conditional-on-phase-176 (plans 01-03)
    provides: "PRUNE-08's close, the seed's first-pass amendment, the two structural pins as first shipped"
provides:
  - "The seed's R3 with the rejected sampler's operative text removed by absence, connect-count objection preserved"
  - "A dated follow-through paragraph in the seed's Phase 180 amendment section"
  - "The one-connect pin hardened to every connect-shaped call in read_eprom's body (WR-01)"
  - "The verdict pin hardened to last_ok's assignment shape inside _dispatch_read (WR-02)"
  - "IN-01 closed: the stale parenthesised line-number citation removed from the verdict pin's docstring"
affects: [180-05, future-dev-test-milestones]

actuals:
  tokens: 41000
  tasks: 2
  commits: 3

tech-stack:
  added: []
  patterns:
    - "Seed amendment by removal, not annotation, per D-09/Phase 177 precedent"
    - "Three-way GREEN/RED/GREEN discrimination transcript for hardened pins (pre-hardening claim holds on mutant, hardened claim reddens, hardened claim green at HEAD)"

key-files:
  created:
    - .planning/phases/180-read-step-sampling-conditional-on-phase-176/evidence/180-04-seed-regeneration-closed.txt
    - .planning/phases/180-read-step-sampling-conditional-on-phase-176/evidence/180-04-one-connect-pin-hardened.txt
    - .planning/phases/180-read-step-sampling-conditional-on-phase-176/evidence/180-04-verdict-pin-hardened.txt
  modified:
    - .planning/seeds/dev-test-adaptive-sequencing.md
    - firestarter_app/tests/test_readback_inventory.py

key-decisions:
  - "The scattered-transport-fault detection-probability sentence was removed with the rest of the stated-cost paragraph, not preserved separately — no phase measured a detection probability, it is the 'and this would still be safe' half of the rejected design's case, and it refers to a sample size that no longer exists anywhere in the seed."
  - "The block-selection rule (which blocks the sample would touch) was removed as buildable spec; the block count itself (10, folded into '10 connects') was kept because it is part of the measured connect-count objection D-09 requires preserved."
  - "The follow-through's own not-touched list was restated in full rather than cross-referenced upward — the plan's own diagnosis of how the amendment record went stale was that a reader had to resolve a reference upward."

requirements-completed: [PRUNE-08]

coverage:
  - id: D1
    description: "Seed R3 no longer carries a buildable spec for the rejected sampler; connect-count objection preserved; four byte-unchanged regions proven identical to the pinned pre-edit blob"
    requirement: "PRUNE-08"
    verification:
      - kind: other
        ref: "evidence/180-04-seed-regeneration-closed.txt (11 negative greps, 5 positive greps, 4 region cmp legs, all rc=0)"
        status: pass
    human_judgment: false
  - id: D2
    description: "One-connect pin (WR-01) hardened to every connect-shaped call in read_eprom's body; verdict pin (WR-02) hardened to last_ok's assignment shape; both docstrings corrected; IN-01's stale line citation removed; module runs 12 green"
    requirement: "PRUNE-08"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_readback_inventory.py::test_one_read_eprom_call_costs_exactly_one_connect"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_readback_inventory.py::test_read_verdict_expression_reads_only_the_last_full_read_result"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_readback_inventory.py::test_a_planted_stray_setup_operation_call_in_read_eprom_reddens_the_hardened_pin"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_readback_inventory.py::test_a_planted_last_ok_reassignment_before_the_return_reddens_the_hardened_pin"
        status: pass
    human_judgment: false

duration: 15min
completed: 2026-09-08
status: complete
---

# Phase 180 Plan 04: Seed R3 Removal and Structural-Pin Hardening (WR-01/WR-02/IN-01) Summary

**Removed the rejected sampler's remaining operative text from the dev-test seed by absence rather than annotation, and hardened both PRUNE-08 structural pins with a three-way GREEN/RED/GREEN discrimination each.**

## Performance

- **Duration:** 15 min
- **Started:** 2026-09-08T17:56:03Z
- **Completed:** 2026-09-08T18:10:40Z
- **Tasks:** 2
- **Files modified:** 2 (plus 3 new evidence files)

## Accomplishments

- Closed the one gap `180-VERIFICATION.md` recorded (`gaps_found`, 23/24): R3's escalation-trigger paragraph and stated-cost paragraph, previously left untouched below the "Measured and rejected" verdict by plan 180-02's own `<action>` text, are now removed outright. The verdict paragraph itself no longer enumerates the sample's block-selection rule, though the block count survives folded into the connect-count objection.
- Verified, by `cmp` against the pinned pre-edit blob `7a47a1fd9236bb4068bc72be6c8f8ed35f86e300`, that nothing outside R3's body and the appended follow-through moved: the frontmatter (6 lines), R1 through the R3 heading (45 lines), R4 through the Phase 177 heading (72 lines), and the whole Phase 177 amendment section (18 lines) are all byte-identical.
- Appended a dated `**Follow-through, gap closure.**` paragraph to the seed's existing `## Status: Phase 180 amendment` section, restating its own not-touched list (R1, R2, R4, the projected-effect table, the per-class characteristics section, the sequencing note, the out-of-scope section) rather than cross-referencing the paragraph above it.
- Hardened WR-01: `_read_eprom_connect_shape` gained `connect_route_calls`, scoped to `read_eprom`'s own `FunctionDef`, counting every `_operation_context`/`_setup_operation`/`find_and_connect` call anywhere in its body rather than only the `with`-header count. A new anti-vacuity leg plants a stray `self._setup_operation(...)` call and proves the mutant is invisible to `context_count` (stays 1) while `connect_route_calls` reddens (reads 2).
- Hardened WR-02: new `_last_ok_assignment_shape` walks `_dispatch_read` for every assignment targeting `last_ok`, tagging each `const_true` / `read_eprom_call` / `other`. A new anti-vacuity leg plants a `last_ok` rebinding after the `reason` assignment and proves the mutant is invisible to `_verdict_expression_names` (stays at the three-name list) while `tags` gains a third `other` entry.
- Corrected both docstrings to state only what each check now proves, and closed IN-01 by dropping the stale parenthesised line-number citation from the verdict pin's docstring while keeping the sibling function's name.
- `firestarter_app/tests/test_readback_inventory.py` runs 12 passed (up from the measured 10 at app HEAD `93a1672`).

## Task Commits

Task 1 (meta repo, `/workspaces` on `gsd/v1.36-dev-test-fidelity-planning`):
1. **Task 1: seed R3 removal + follow-through** — `3678b66b` (docs) — seed amendment plus evidence transcript.

Task 2 (submodule `firestarter_app` on `gsd/v1.36-dev-test-fidelity`, plus meta-repo gitlink bump):
2. **Task 2: pin hardening** — `d164d74` (test, inside `firestarter_app`) — `test_readback_inventory.py` extended to 12 tests.
3. **Task 2 evidence + gitlink** — `dcec60f9` (test, in `/workspaces`) — two hardening transcripts and the `firestarter_app` gitlink advance.

**Plan metadata:** to be committed after this SUMMARY (docs commit including STATE.md/ROADMAP.md exclusions per plan instruction — ROADMAP.md is intentionally NOT touched by this plan).

## Files Created/Modified

- `.planning/seeds/dev-test-adaptive-sequencing.md` — R3's verdict paragraph reduced to a single paragraph (block-selection rule removed, connect-count objection preserved); escalation and stated-cost paragraphs deleted outright; a dated follow-through appended to the Phase 180 amendment section.
- `firestarter_app/tests/test_readback_inventory.py` — `connect_route_calls` key added to `_read_eprom_connect_shape`; new `_last_ok_assignment_shape` helper; two new anti-vacuity tests; both hardened assertions added to the existing pins; both docstrings corrected; module docstring's anti-vacuity count updated from four to six.
- `.planning/phases/180-read-step-sampling-conditional-on-phase-176/evidence/180-04-seed-regeneration-closed.txt` — new.
- `.planning/phases/180-read-step-sampling-conditional-on-phase-176/evidence/180-04-one-connect-pin-hardened.txt` — new.
- `.planning/phases/180-read-step-sampling-conditional-on-phase-176/evidence/180-04-verdict-pin-hardened.txt` — new.

## Removed Text, Preserved Outside Git History

**The removed escalation paragraph (formerly seed lines :89-91, pre-edit blob `7a47a1fd9236bb4068bc72be6c8f8ed35f86e300`):**

> Escalate to the full second read only when the sample diverges, so exact
> divergence counts (`cmp_len`, `bad`, `pct`, `first_offset`) survive intact on
> every run where they mean anything.

**The removed stated-cost paragraph (formerly seed lines :93-99):**

> **Cost, stated:** on a passing run the divergence metric becomes an *estimate*
> over a sampled subset rather than an exact whole-device count. A scattered
> transport fault — the uno328pb signature, and the only fault class this metric
> was built to catch — is caught with high probability by any sample of this size,
> because scatter is what makes it detectable. A fault confined entirely to
> unsampled bytes would be missed on the first pass; the bit-structured stride is
> chosen to make that region small and address-line-aligned rather than arbitrary.

**Disposition of the scattered-transport-fault (`uno328pb`) detection-probability sentence:** removed with the rest of the stated-cost paragraph, per the plan's explicit instruction. Reason recorded here, not deferred: (1) no phase measured a detection probability — the "caught with high probability" claim is an unmeasured probabilistic argument, not a measurement; (2) it is the "and this would still be safe" half of the rejected design's case, which is exactly the kind of reassurance a planner would need to re-propose the sampler; (3) it refers to a sample size (the bit-structured stride's block set) that no longer exists anywhere in the seed after this edit, so left in place it would dangle. The genuinely measured facts — MEAS-01's per-board-class medians and the connect arithmetic — remain, in R4's already-corrected sentence and in the surviving R3 paragraph respectively.

**Also removed from the verdict paragraph itself:** the block-selection clause, formerly "— one 256 B block at each device-size-scaled boundary, plus block 0 and the top block —". The block *count* (10, expressed as "10 separate `read_eprom` calls — 10 connects") is part of the measured objection and was kept; the rule for *which* blocks were chosen is a buildable spec and was removed, per D-09's distinction between a count and a specification.

## Exact Seed Line Ranges (post-edit; shifted from the plan's pre-edit :75-99)

- R3 heading: line 70 (unchanged).
- R3 body (new, single verdict paragraph): lines 75-90.
- R4 heading: now line 91 (was line 101 pre-edit; shifted by 10 lines net removal in R3's body before the follow-through addition).
- `## Status: Phase 180 amendment` heading: line 179.
- Appended follow-through paragraph: lines 202-212.
- Seed total: 213 lines (was 210 before this plan's edit).

## Measured Values (structural pins)

**WR-01, `_read_eprom_connect_shape` on `eprom_operations.py`:**
- At HEAD: `context_count=1`, `connect_route_calls=1`.
- On the planted stray-`_setup_operation`-call mutant: `context_count=1` (pre-hardening claim unmoved), `connect_route_calls=2` (hardened claim reddens).

**WR-02, `_last_ok_assignment_shape` on `chip_test.py`'s `_dispatch_read`:**
- At HEAD: `tags=['const_true', 'read_eprom_call']`, `for_loop_count=1`, `read_assign_in_for_loop=True`.
- On the planted `last_ok`-reassignment mutant: `_verdict_expression_names` stays `['VERDICT_BAD', 'VERDICT_OK', 'last_ok']` (pre-hardening claim unmoved), `tags=['const_true', 'read_eprom_call', 'other']` (hardened claim reddens).

**Module test count:** 10 passed (before) → 12 passed (after), verified by `./.venv311/bin/python -m pytest tests/test_readback_inventory.py -o addopts="" -q`.

## Decisions Made

- Reduced the R3 verdict paragraph rather than deleting the whole rule — the connect-count objection is a measured fact that must survive so the design cannot be regenerated without meeting it (D-09's explicit requirement), distinct from the block-selection rule and escalation/cost paragraphs, which are buildable spec.
- Did not front any retained sentence with a "for the historical record" banner — D-09 names that route as the exact insufficient pattern (outvoted but not absent), so removal, not annotation, was the only compliant option.
- Restated the follow-through's not-touched list in full inside the new paragraph rather than pointing back at the paragraph above it, per the plan's explicit instruction and its own diagnosis of why the prior amendment record read as internally contradictory to `180-VERIFICATION.md`.

## Deviations from Plan

None — plan executed exactly as written. Every measurement the plan asserted this planning session (grep counts, blob region line counts, anchor line content and indentation, anchor uniqueness, mutant discrimination values, docstring contents) was independently re-measured here and matched exactly; no claim in the plan was found false.

## Issues Encountered

None. `ruff format` reformatted one line in `test_readback_inventory.py` (`connect_route_calls` boolean-expression wrapping) to match project style after the edit — a cosmetic, deterministic formatter pass, not a deviation from the plan's specified logic.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- The blocking gap from `180-VERIFICATION.md` (`gaps[0]`, `prohibitions_flagged[0]`, `human_verification[1]`) is closed by removal, settled by eleven measured scalars rather than a comprehension judgment.
- WR-01, WR-02 and IN-01 from `180-REVIEW.md` are closed, each hardening proven RED against a mutant the pre-hardening pin passes.
- Zero product-source lines, zero firmware lines, zero `chip_database.json` bytes, and zero `#` comments were added (`tokenize` COMMENT counts held at 621 / 0).
- Plan `180-05` is unblocked: it owns IN-02, the seven-leg battery re-run with the floor moved to the measured 2247, `REQUIREMENTS.md`'s re-flip to Complete, and `ROADMAP.md`'s checkbox update — none of which this plan touched.
- No blockers.

---
*Phase: 180-read-step-sampling-conditional-on-phase-176*
*Completed: 2026-09-08*

## Self-Check: PASSED

- All key files exist on disk: seed, test module, and all three evidence transcripts.
- Meta-repo commits found: `3678b66b` (Task 1), `dcec60f9` (Task 2 evidence + gitlink).
- Submodule commit found: `d164d74` (Task 2, inside `firestarter_app`).
- All acceptance criteria for both tasks re-verified independently (fragment removal, region `cmp`, discrimination scalars, docstring scalars, pytest count, ruff, tokenize gate) and all passed.
