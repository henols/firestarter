# Phase 181: Report Fidelity — Schema 2.0, Canonical Naming & Hygiene Close - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-09
**Phase:** 181-report-fidelity-schema-2-0-canonical-naming-hygiene-close
**Areas discussed:** Canonical naming rule, Duration semantics, How deep the deletions cut, Closing scope

---

## Canonical naming rule

### Q1 — which alias does a comma-joined `part_number` show in the title?

| Option | Description | Selected |
|--------|-------------|----------|
| Match raw token, else first | Pick the alias that case-insensitively equals the operator's raw token; fall back to the first alias. All 26 filed issues resolve to the chip actually tested. | ✓ |
| Always the first alias | Simplest, stateless. But `w27c020` files as `W27C02`, a genuinely different part number, and a late-alias token is lost. | |
| Whole comma-joined string | Most literal reading of "the matched database part_number". The AT28C256 row is 68 characters of aliases. | |

**User's choice:** Match raw token, else first.
**Notes:** Measured before asking — 514 of 953 aliases resolve to a comma-joined `part_number`; the "first alias" rule is wrong on `w27c020`, `at28hc256l` and others. → CONTEXT D-01.

### Q2 — does the canonical name keep infoic's parenthetical mode annotation?

| Option | Description | Selected |
|--------|-------------|----------|
| Keep verbatim | `DS1245AB(RW)` stays as the database spells it; the selector mirrors `get_eprom_config`'s own exact-then-paren-stripped ladder. | ✓ |
| Strip for display | Cleaner titles, but the `(RW)` and `(TEST)` rows then file under an identical name. | |

**User's choice:** Keep verbatim.
**Notes:** Measured — 43 rows carry parens and 24 paren-stripped names appear on more than one row (every DALLAS NVRAM ships as both an `(RW)` and a `(TEST)` row). → CONTEXT D-02.

### Q3 — which surfaces switch to the canonical name?

| Option | Description | Selected |
|--------|-------------|----------|
| Title + body + human headings | Issue title, issue body, console table title, saved report heading. Artifact **filenames** keep the raw token. | ✓ |
| Title + body only | Literal RPT-F1. The rendered report and the filed issue then disagree about the chip's name. | |
| Every surface incl. filenames | Most consistent, but filenames become `dev-test-DS1245AB_RW_.json`, unpredictable from the command line, with two naming eras coexisting on disk. | |

**User's choice:** Title + body + human headings.
**Notes:** → CONTEXT D-03.

### Q4 — sweep the app test suite to canonical spellings, as the RPT-F1 todo asks?

| Option | Description | Selected |
|--------|-------------|----------|
| No sweep — lowercase is correct there | A test's chip token models what an operator types; 19 frozen hashes key on `ac.chip`. Only title/heading assertions gain the canonical spelling. | ✓ |
| Sweep the suite to canonical | Follows the todo literally. | |

**User's choice:** No sweep.
**Notes:** The todo claims 18 occurrences; measured **103 across 23 files**, including the frozen-shape builders. Rewriting `chip="m27c512"` yields `776846bf2dc8`, already frozen as `m27c512-full-canonical-name` — the sweep would collide two frozen shapes. → CONTEXT D-04.

---

## Duration semantics

### Q1 — which per-operation number replaces `_aggregate_cycle_results`' sum?

| Option | Description | Selected |
|--------|-------------|----------|
| Mean over cycles that ran | `sum / cycles that reached the operator`. Identical to the median at N=2; the only option where a `--fast` value and a default value measure the same quantity. | ✓ |
| Last cycle that ran | Matches the convention already used for `fingerprint` and `write_target`, but a `--fast` run's only cycle is cycle 1, which is not equivalent to cycle 2. | |
| Max over cycles that ran | Tail-oriented, but at N=2 it mostly reports "whichever cycle had the unknown start". | |

**User's choice:** Mean over cycles that ran.
**Notes:** Research (benchmark practice: report median, never a bare mean) is largely moot at N=2, where the two coincide. The engine's own `_CYCLE_BLOCK_OPS` note — "only cycle 1's write can start from an unknown state" — is recorded as a stated caveat rather than resolved. → CONTEXT D-05.

### Q2 — where does the new wall-clock `elapsed` start and stop?

| Option | Description | Selected |
|--------|-------------|----------|
| CLI entry → just before serialization | Captures the database load, identity read, plan derivation and every step; excludes render, file write and the submit prompt, named in the docstring. | ✓ |
| Handler entry → just before serialization | Same stop point, but Click dispatch and the 746-row database parse fall outside. | |
| CLI entry → process exit | Most literal "whole command", but the operator's think-time at the prompt lands inside the number and the artifact must be written twice. | |

**User's choice:** CLI entry → just before serialization.
**Notes:** Two mechanical facts established first — `to_dict()` runs three times per run, so `elapsed` must be a stored field stamped once; and the submit prompt runs after all three serializations. → CONTEXT D-06.

### Q3 — where does `elapsed` appear on the human surfaces?

| Option | Description | Selected |
|--------|-------------|----------|
| Console row + issue body line | An `elapsed` row replaces "steps total" in place; the filed body carries it too. | ✓ |
| JSON and issue body only | Quietest change, but the operator who just waited for the run has no total in front of them. | |

**User's choice:** Console row + issue body line.
**Notes:** → CONTEXT D-07.

---

## How deep the deletions cut

### Q1 — how deep does RPT-B2 cut, given D-7 defers `Plan.locked_destructive` here?

| Option | Description | Selected |
|--------|-------------|----------|
| Exported key only *(Claude's recommendation)* | Delete `banner.locked_steps` only; `Plan.locked_destructive` stays as library state. Matches D-7's own "the deletion is narrower than RPT-B2 states". | |
| Field and its plumbing | Also delete `Plan.locked_destructive`, `count_applicable`'s `+ len(...)`, and `sdp_oracle_applicable`'s second arm. | |
| Also remove `write_scope="none"` | The fullest cut: drop the unreachable mode from `derive_plan` entirely. | ✓ |

**User's choice:** Also remove `write_scope="none"`.
**Notes:** Chosen against the recommendation. The concern was stated in the option text before selection — largest surface in the milestone's closing phase, and it touches the `sdp_oracle_not_run` exit-code path Phase 178 just changed. Two measurements taken afterwards materially de-risked it: every frozen shape builds with `write_scope="full"`, and `tests/plan_corpus.py` explicitly excludes `"none"` from its 1,354-plan sweep. → CONTEXT D-08.

### Q2 — with `"none"` gone, what happens to the `write_scope` parameter?

| Option | Description | Selected |
|--------|-------------|----------|
| Required kwarg, two values *(Claude's recommendation)* | No default, so a forgotten kwarg is a `TypeError` rather than a destructive plan. | |
| Default to `"full"` | Keeps call sites compiling, but turns a fail-closed default into a fail-open one. | |
| Drop the parameter entirely | Fold the decision into `derive_plan` from `is_uv`, which it already computes. | ✓ |

**User's choice:** Drop the parameter entirely.
**Notes:** Verified equivalent after selection: `write_scope == "partial"` iff `is_uv`, and `derive_plan` already calls `is_uv_eprom(full)` on the same record `_resolve_write_scope` consults. Behaviour-identical on every reachable path; the `op=` hash component is unmoved. It is RPT-A4's own "never re-derived" principle applied one level up — a stronger choice than the framing given it. → CONTEXT D-09.

### Q3 — with `chip_id_actual` populated on a pass, what does the console `chip_id` row do?

| Option | Description | Selected |
|--------|-------------|----------|
| Two-sided whenever an id was read *(Claude's recommendation)* | The 2026-08-21 reason was a bare `None`; there is now a real measured value, and showing both proves the id was read. | |
| One-sided on agreement, two-sided on mismatch | Preserves the 2026-08-21 render decision exactly; RPT-A1 met in the export. | ✓ |

**User's choice:** One-sided on agreement.
**Notes:** The 2026-08-21 operator decision stands. → CONTEXT D-10.

### Q4 — does an agreeing read record a divergence result, or stay `None`?

| Option | Description | Selected |
|--------|-------------|----------|
| Record it — mirror PRUNE-03 | An agreeing compare reports `bad=0`, so `None` means only "no comparison possible". | ✓ |
| Serialize as-is | Every existing test stays green, but `None` conflates "compared and matched" with "never compared". | |

**User's choice:** Record it.
**Notes:** Declared cost accepted — it reddens `test_read_step_agreement_no_divergence_recorded`, which Phase 180's D-06 cited. Not in the dedup hash. → CONTEXT D-11.

---

## Closing scope

### Q1 — which residual todos does this closing phase absorb? *(multi-select)*

| Option | Description | Selected |
|--------|-------------|----------|
| UV exhausted-slots ladder false-green | T-179-05: an all-slots-spent run proposes the same disposition as a genuine PASS. | ✓ |
| `slots_remaining` off-by-one | T-179-07: measured on hardware — "256 of 256 slots left" after spending one. | ✓ |
| Delete the stale `ALWAYS WRITES` comment block | Describes the reverted `260821-wna` prompt design in the present tense. | ✓ |
| Close the already-fixed `ladder_state` todo | Resolved by Phase 177's `match` bucket; verified in code. Zero implementation. | ✓ |

**User's choice:** All four.
**Notes:** 41 todos matched the phase; these four are the ones inside "the report describes only what the run knows". The stale-comment todo's two prior blockers ("rewrite two `#` lines vs delete accurate prose") dissolve under the hard no-comments rule, and D-09 deletes the other half of the contradiction anyway. → CONTEXT `### Folded Todos`.

### Q2 — does `slots_remaining` mean before or after this run?

| Option | Description | Selected |
|--------|-------------|----------|
| After this run | `slots_total - slot_index - 1`, matching the wording already printed; conditional on the write actually running. | ✓ |
| Before this run, reword the line | One line lighter, but answers a different question than the operator asks. | |

**User's choice:** After this run.
**Notes:** The "did a write actually run" predicate is shared with the UV ladder fix — one guard, two folded defects. → CONTEXT D-20, D-21.

### Q3 — does Phase 181 perform the milestone close?

| Option | Description | Selected |
|--------|-------------|----------|
| Phase stops at the record | 18 requirements + the `MILESTONES.md` entries; the beta cut, tag and PRs stay with `/gsd-complete-milestone` and `/gsd-ship`. | ✓ |
| Phase carries the close through beta | One motion, but puts an outward-facing push inside a phase whose verification has not run. | |

**User's choice:** Phase stops at the record.
**Notes:** Matches how v1.35 closed and keeps the verifier gate — which caught gaps in phases 174, 179 and 180 — between the last code change and any push. → CONTEXT D-22.

---

## Claude's Discretion

The operator delegated nothing outright this session; every question was answered directly. Four
items were **not** opened and Claude disposed of them, recording the disposition so the planner does
not re-derive it:

- **D-23** — RPT-A5's shape: one additive `StepResult.chip_id_detected: int | None` field, fed by the
  value `_dispatch_id` already receives; `_chip_id_fields` stops scraping `reason`, and the mismatch
  prose is left unchanged.
- **D-24** — `canonical_part_number` is `None`-safe, with the title builder falling back to the raw
  token rather than rendering `None`.
- **D-25** — no rounding rule invented for the mean; `submit._duration_text` keeps owning display
  precision so the three surfaces cannot disagree.
- **D-26** — no comments, per the absolute project rule; every rationale goes in a docstring, the plan
  `SUMMARY.md`, or the commit message.

Two further mechanical calls were made inside answered areas rather than asked, because house
precedent settles them: **D-14** (the six Phase 174 key-list pins move in the same commit as the key
change, since a key-list pin is not a frozen hash literal and the two-commit rule governs
`FROZEN_HASHES` only) and **D-16** (Phase 181 declares zero re-keys, asserted positively across all
19 frozen shapes).

## Deferred Ideas

- **Exposing the gap between `elapsed` and the sum of step durations** — the connect and
  database-load overhead MEAS-01 measured. Offered at the duration gate and not opened; it would be a
  second derived number where RPT-D2 asks for the first one's removal.
- **Size-gated read sampling for parts ≥512 KiB** — carried forward from Phase 180, where the
  operator declined it as both a ship option and a re-file option. Deliberately not a requirement,
  backlog item or todo.
- **R4-01 — `EpromOperator` link leasing** — already filed in `.planning/REQUIREMENTS.md` §Future
  Requirements; named only as the change that would invalidate Phase 180's close.
- **The 999.44 firmware half** — region-scoped `mem_util_blank_check`. Out of scope for a host-only
  milestone; the product-level bug stays open knowingly.
