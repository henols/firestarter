# Phase 181 Closure: Report Fidelity — Schema 2.0, Canonical Naming & Hygiene

Eighteen requirements landed and all nineteen `FROZEN_HASHES` literals are byte-identical to app
base `04fd982` — zero re-keys, declared positively across every registered shape, not merely
absence-of-evidence. That is this phase's headline claim, and everything below is the enumeration
behind it, not the verdict itself.

## 1. The verdict

Zero re-keys, asserted positively. All 19 `FROZEN_HASHES` literals in
`firestarter_app/tests/fixtures/report_shapes.py` are measured byte-identical to app base `04fd982`
after every plan in the phase landed: `git diff 04fd982 -- tests/fixtures/report_shapes.py`, filtered
to twelve-hex literal lines, returns zero matches, and `test_dedup_fingerprint_is_frozen`'s 19-way
parametrization passes 19/19. This measurement was repeated at the close of every wave (see each
plan's own `frozen-hash-reproof` / `frozen-hash-invariance` evidence transcript) and is repeated here
one final time, after plan `181-09`'s deletion and this plan's own record and pin, with the same
result: zero moved.

## 2. What is excluded, and why

`dedup_fingerprint`'s pre-image is exactly five components — `chip` | `protocol` |
`op=verdict:classification` | `repeat_policy_tag` | `coverage_tag` — built from an explicit
allow-list with no reflection over `DiagnosticReport`'s dataclass fields. Every change this phase
made falls outside that list:

- **The canonical name is additive, and the hashed chip token keeps the operator's raw spelling**
  (D-2). `auto_capture.canonical_part_number` is a new field; `ac.chip`, the hash's first component,
  is untouched.
- **Every RPT-B deletion removed an unhashed key.** `voltage.vpp_mv`/`vpe_mv` and
  `banner.locked_steps` were never inputs to the hash — they are schema/render surface only.
- **`duration_s`'s fold to a mean, the stored `elapsed` field, the `divergence` export, the
  fingerprint siblings (`total`/`bad`/`bad_pct`/`evidence`), the `is_uv` boolean, and the structured
  `chip_id_detected`/`chip_id_actual` fields are all unhashed.** None of them is `chip`, `protocol`,
  an `op=verdict:classification` triple, `repeat_policy_tag`, or `coverage_tag`.
- **`schema_version` is never read by the hash.** The 1.8 → 2.0 bump is free.

Name each and the pattern is the same: this phase's entire surface sits outside the five-entry
allow-list by construction, not by luck.

## 3. The reason it matters

`count_agreeing` reads the `dedup_fingerprint` embedded in an already-filed issue body and never
re-hashes. A re-key is therefore **permanent for the historical corpus** — no migration of a filed
issue is possible, and every `N>=2` promotion group built on the old hash silently forks. This is
why D-16's "zero, asserted positively" standard exists rather than "no *known* re-key": absence of
evidence for a hash that was never checked is not the same claim.

## 4. Which gate would redden

Four independent gates, any one of which reddens if a future change moves a hash this phase declared
frozen:

1. **The 19-way frozen parametrization**, `test_dedup_fingerprint_is_frozen` in
   `tests/test_blast_radius_invariance.py` — pins each shape to an absolute literal, not a relational
   comparison, so a re-key is visible per-shape rather than silently passing because both sides moved
   together.
2. **The literal-line diff against the app base** — `git diff 04fd982 -- tests/fixtures/report_shapes.py`,
   filtered to twelve-hex literal lines. This is the check this closure document's own verdict (§1)
   is built on.
3. **The write-op selector pin** from plan `181-04`,
   `test_the_write_op_selector_reads_write_scope_and_never_is_uv` in
   `tests/test_derive_plan_structural_sentinel.py` — guards the one place D-09's amendment could have
   silently re-keyed seven shapes by reading `is_uv` instead of `write_scope`.
4. **HYG-03's new allow-list AST pin**, `test_dedup_fingerprint_hashes_an_explicit_allow_list_and_never_the_serialized_mapping`
   and its planted-mutant leg `test_a_planted_reflective_body_reddens_the_allow_list_pin` (this plan,
   Task 1) — guards the mechanism itself: a future refactor that hashes `to_dict()` or reflects over
   dataclass fields reddens before it ever reaches a shape's literal.

## 5. Requirement clusters, by evidence

Each cluster cites its plan's own evidence transcript by path rather than restating its numbers —
re-run the cited transcript's commands to verify independently.

- **RPT-A (chip-id, fingerprint, divergence, is_uv) — 5 requirements, plans `181-01`, `181-07`,
  `181-08`.** `plan.is_uv` reaches `to_dict()` as a top-level boolean
  (`evidence/181-01-frozen-hash-invariance.txt`); the four `fingerprint_*` siblings and `divergence`
  export unconditionally (`evidence/181-07-fingerprint-siblings.txt`,
  `evidence/181-07-divergence-on-agreement.txt`); the detected chip ID is a structured `StepResult`
  field and `chip_id_actual` populates on a passing check with the echo-not-readback ceiling stated
  in three places (`evidence/181-08-chip-id-structured.txt`).
- **RPT-B (voltage/banner deletions) — 2 requirements, plans `181-04`, `181-09`.**
  `banner.locked_steps` / `Plan.locked_destructive` / `write_scope="none"` deleted at the fullest
  depth D-08 adjudicated (`evidence/181-04-scope-narrowing.txt`); `voltage.vpp_mv`/`vpe_mv` deleted,
  proven by an attribute-scoped AST census rather than asserted
  (`evidence/181-09-voltage-census.txt`).
- **RPT-D (duration semantics) — 2 requirements, plan `181-06`.** `duration_s` folds to the mean over
  the cycles that ran; `elapsed` is a stored wall-clock field, stamped once at CLI entry
  (`evidence/181-06-duration-mean.txt`, `evidence/181-06-elapsed-surfaces.txt`) — see §6 for the
  duration comparison.
- **RPT-E (schema 2.0, forward-only, dedup invariance) — 3 requirements, plan `181-01`.**
  `schema_version` → `"2.0"`; the frozen schema-1.2 fixtures still parse forward-only
  (`evidence/181-01-forward-only-parse.txt`); RPT-E3 re-anchors to the 19 `FROZEN_HASHES` literals
  now that the `RK-174-` ledger is retired (`evidence/181-01-key-pin-planted-red.txt`).
- **RPT-F (canonical naming, skill update) — 2 requirements, plans `181-05`, `181-09`.**
  `auto_capture.canonical_part_number` carries the matched `part_number` under D-01's token-match
  rule and D-02's verbatim-parenthetical rule (`evidence/181-05-canonical-surfaces.txt`,
  `evidence/181-05-frozen-hash-reproof.txt`); the `devtest-triage` skill updated in the same task as
  the paired deletion, per D-5's two-repo residue adjudication
  (`evidence/181-09-skill-same-commit.txt`).
- **HYG (dependency bounds, the never-re-key decision, orchestrator allow-list) — 4 requirements,
  plans `181-03`, `181-04`, `181-10`.** `syrupy>=5.0,<7`; the runtime dependency set pinned to exactly
  six packages (`evidence/181-03-dependency-pins.txt`); `_HANDLER_FUNCTION_NAMES` a two-way edit
  removing `_resolve_write_scope` (`evidence/181-04-scope-narrowing.txt`); HYG-03's decision recorded
  in `.planning/MILESTONES.md`'s v1.36 section and enforced by an AST pin observed RED against two
  planted mutants (`evidence/181-10-hyg03-record.txt`, this plan).

## 6. The duration comparison, stated as what the removed row excluded

Per this milestone's house rule (operation counts, never seconds — D-25), the comparison is not a
pass/fail threshold on either absolute number; it is what the deleted "steps total" row's own removed
comment already conceded it was missing. A single real `dev test` invocation recorded in
`evidence/181-06-elapsed-surfaces.txt` measured `elapsed=0.066` against `old_would_be_sum=0.004` (the
sum of that run's own `steps[].duration_s`) — `elapsed` is larger because it counts real setup cost
the summed row never saw: **the connects (the `EpromDatabase` load and the hardware-identity read)
and plan derivation.** The relation (`elapsed >= old_would_be_sum`) is the evidence of the exclusion,
not a number to reproduce exactly — both are mock-timing artifacts of one `CliRunner` invocation, and
the point is categorical (the old row excluded real setup cost), not numerical.

## 7. Deliberately NOT done

- **No canonical-spelling sweep of the app test suite (D-04).** Measured actively harmful: rewriting
  `chip="m27c512"` to `chip="M27C512"` produces the exact hash Phase 174 froze as
  `m27c512-full-canonical-name` specifically to catch a `parts[0]` normalization — a sweep would
  collide two frozen shapes and re-key the milestone's own oracle.
- **No second derived duration number.** RPT-D2 asks for the sum-of-sums row's removal, not its
  replacement by a second derived number (D-06); `elapsed` is stored once, never recomputed.
- **No console two-sided chip-id row on a clean pass.** D-10's invariant — one-sided on agreement,
  two-sided only on a real mismatch — is preserved by extending `render()`'s guard condition rather
  than adding a second display branch, proven output-identical to every historical shape.
- **No firmware change.** This is a host-only phase; `firestarter/` (the firmware submodule) stays
  porcelain-clean throughout, confirmed in §8.
- **No rewrite of the `devtest-triage` skill's database-versus-datasheet example row.** The `:375`
  row (`vpp_mv: 13500`) is the DATABASE's programming voltage, a different field sharing a name with
  the report's deleted key — rewriting it would turn a correct row into a false one
  (`evidence/181-09-skill-same-commit.txt`).
- **No re-key, anywhere, of anything.** D-16's declared standard for this entire phase; see §1.

## 8. D-22's fence

The phase stops at this record. The beta cut, the `v1.36` tag, and the three `.github`-only pull
requests to protected `main` branches are left to `/gsd-complete-milestone` and `/gsd-ship` — the
same shape v1.35 closed with, keeping a verifier pass between the last code change and any
outward-facing push. `main` is protected in all three repositories with `current_user_can_bypass:
never`; this phase does not go near it. **Before `/gsd-ship` runs, local `beta` must be recreated
from `origin/beta`** — `ship.md` anchors its audit range on `git merge-base beta HEAD`, and local
`beta` goes stale between milestone sessions. This is information for whoever runs the close, not an
action taken by this plan: `evidence/181-10-green-tree-battery.txt` records `pushed=false`,
`tagged=false`, `pr_opened=false`, `branch_cut=false`, and no commit subject in this plan's history
claims otherwise.

Whole-repo porcelain, measured after every commit in this plan:

```
git -C /workspaces/firestarter_app status --porcelain      -> empty
git -C /workspaces/firestarter_app status --porcelain firestarter/ -> empty
git -C /workspaces/firestarter status --porcelain          -> empty
git -C /workspaces status --porcelain .planning/ .claude/  -> empty
```

## 9. The green-tree battery, and the one measured departure from this plan's own text

The seven-leg battery (`ruff check`, `ruff format --check`, the mypy watermark at 35, the
snapshot-shapes check, the `dev test` orchestrator gate, the diagnostic-report claim scanner, and the
full suite) is recorded leg-by-leg with an explicit `rc=` in `evidence/181-10-green-tree-battery.txt`.
The full suite measured **2285 passed, 0 failed**.

The floor actually asserted was **2239**, the plan's own figure, and it is stale: it predates waves
5-8 and clears by 46. An earlier draft of this section claimed the floor had been re-derived from
the wave-8 measurement of 2282; that claim was false and is corrected here. The floor leg is
therefore weak evidence, and it is not what this battery rests on.

What the battery rests on is the reconciliation, which is exact and was the point of this plan's
one revision: `passed(2285) + failed(0) + skipped(0) + xfailed(0) + xpassed(0) + error(0) = 2285 =
collected(2285)`. A count that reconciles against pytest's own `collected` total cannot be satisfied
by a hand-written scalar, a backdated file, or a falsified count — the three plants this leg was
observed RED against. The honest contemporary floor is the wave-8 measurement of **2282**; 2285 is
+3 against it, which reconciles exactly with the HYG-03 AST pin this plan added (two test functions
plus a helper).

Two departures from this plan's own literal text, both measured and both recorded rather than
silently absorbed:

1. **The mypy watermark leg initially FAILED** (37 against a watermark of 35) — plan `181-09`
   introduced `tests/test_voltage_field_census.py` without re-running this leg. Fixed inline
   (Rule 3 — a blocking issue for this plan's own required battery), app commit `6de7273`; see
   `evidence/181-10-green-tree-battery.txt` §Leg 3 for the before/after transcript.
2. **The three historically pre-existing `tests/test_skip_census.py` failures did not occur in this
   run.** They are a 180-second per-child-process timeout racing the suite's own ~741-second
   historical wall time; this run completed in 476.19 seconds, well inside every child's budget, so
   the flake did not fire. Recorded as measured — 0 failures, not 3 — per the standing rule that a
   gate must report what it measured, never what a prior document expected it to measure.
