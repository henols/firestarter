# Phase 174: Blast-Radius Invariance Harness - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-03
**Phase:** 174-blast-radius-invariance-harness
**Areas discussed:** Corpus form, Table coverage, Re-key protocol, Ledger + delta artifact

---

## Corpus Form

### Q1 — How should a frozen report shape be physically stored, given there is no deserializer in the tree?

| Option | Description | Selected |
|--------|-------------|----------|
| Builders + `to_dict()` snapshot | Builders construct the `DiagnosticReport` (hash off the object, as production does); each shape's `to_dict()` committed as JSON. No loader, so nothing untrusted sits between fixture and hash; the JSON is already Phase 181's RPT-E2/E3 parse oracle. | ✓ |
| Python builders only | A parametrize table of `(shape spec → expected 12-hex)`, reusing `_minimal_report`. Smallest surface, but GATE-05 satisfied thinly and Phase 181 builds the JSON oracle from scratch. | |
| Report JSON + test-only loader | Commit real report JSON and write a loader to rebuild `DiagnosticReport`. Closest to filed issues, but the loader is machinery production never exercises — drift makes the oracle lie while staying green. | |

**User's choice:** Builders + `to_dict()` snapshot
**Notes:** Verified during scouting that no `from_dict` exists anywhere in the tree and `DiagnosticReport` is constructed at exactly one production site (`cli_handlers.py:2388`). That singularity is what the decision rests on.

### Q2 — Where do the frozen shapes come from — the real shipped database, or hand-specified step lists?

| Option | Description | Selected |
|--------|-------------|----------|
| Both, in separate tables | Hand-specified shapes pin the hash function (immune to DB regeneration); a second, smaller table from real `derive_plan` output pins the shapes research measured. A DB regen reddens only the second — a signal, not noise. | ✓ |
| Real `derive_plan` output only | Matches research's measured hashes exactly, but `chip_database.json` is GENERATED, so a generator fix in any later milestone reddens the oracle for an unrelated reason. | |
| Hand-specified only | Fully decoupled, stable — but cannot catch a re-key arriving via plan shape, which is re-key path #2 (SDP-step pruning, 637 of 677 chips). | |

**User's choice:** Both, in separate tables

### Q3 — Where should the shape builders live?

| Option | Description | Selected |
|--------|-------------|----------|
| New `tests/fixtures/` module | Self-contained beside the committed JSON; importable by Phase 181's schema tests without dragging in `test_diagnostic_report.py`'s 68 dedup call sites. | ✓ |
| Extend existing helpers in place | Grow `_minimal_report` / `_coverage_report` and put the table beside the existing frozen literal at line 1377. Zero new files, but the oracle lives inside a 2000+ line test module. | |

**User's choice:** New `tests/fixtures/` module

### Q4 — How does a ledger row point at a table row?

| Option | Description | Selected |
|--------|-------------|----------|
| Stable string id per shape | Each shape carries an id like `uv-slot-write-pass`; the ledger, ladder table, and JSON filenames all key off it, so a declared re-key names exactly which rows it may move. | ✓ |
| Positional index | No id field; rows identified by position. Less to write, but reordering or inserting silently invalidates every ledger reference — and this milestone will insert shapes. | |

**User's choice:** Stable string id per shape

---

## Table Coverage

### Q1 — How broad should the synthetic frozen-hash table be?

| Option | Description | Selected |
|--------|-------------|----------|
| Every shape a v1.36 phase can move | Row set derived from the milestone's own change list: the four measured re-key paths plus ATTR-01's status-axis shape and PRUNE-03's synthesized-fingerprint shape. Every row exists because a named later phase is measured against it. | ✓ |
| Roadmap floor — the four re-key shapes | Exactly criterion 1. Smallest honest gate, but Phase 178's status axis and Phase 177's match bucket land against no pinned row, and ATTR-04 has nothing to confirm against. | |
| Research's full cross-product | 3 populations × 3 scopes × pass/fail/marginal × `--fast` × uv-slot × both tag states. Maximum coverage, but most rows guard nothing this milestone touches. | |

**User's choice:** Every shape a v1.36 phase can move

### Q2 — What should be done with the 27 filed `[dev test]` issues?

| Option | Description | Selected |
|--------|-------------|----------|
| Reproduce the measured subset from builders | Commit all 27 `(issue, chip, hash)` rows; additionally reproduce the filed hash from builders for m27c512, sst27sf512, at28c256, w27e257. Bounded work, proves the table matches real history for the groups that matter, no loader. | ✓ |
| Record all 27 as an artifact only | Commit the table, no reproduction assertion. Cheap and honest about scope, but asserts nothing — against this project's standing rule. | |
| Reproduce all 27 | Truest possible oracle, but 27 hand-reconstructed shapes is substantial first-phase work and several need issue bodies parsed — the loader Q1 declined to build. | |

**User's choice:** Reproduce the measured subset from builders
**Notes:** `gh issue list` confirmed 27 filed `[dev test]` issues, each carrying its `dedup_fingerprint` in the title. Real dedup groups already exist: `00e121446ceb` spans gh#20 / gh#21 / gh#32; `334c3fa198bf` spans gh#39 / gh#40.

### Q3 — Does the sorted `to_dict()` key-list pin belong in this phase?

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, land it here | The committed JSON snapshots are being written anyway; the assertion is a few lines on top. Gives Phase 181's three key deletions a gate that predates them. | ✓ |
| No, it is Phase 181's (RPT-E2) | The roadmap's five criteria do not mention it; keeps the boundary exactly as written. But then the deletions land in the same phase as their own gate. | |

**User's choice:** Yes, land it here
**Notes:** Research named this "the one genuinely missing schema gate" and assigned it to Phase 174; the roadmap criteria did not. Taken as a deliberate addition to the phase's stated deliverables.

### Q4 — How much of `build_db_diff` should the ladder pin cover?

| Option | Description | Selected |
|--------|-------------|----------|
| All four disposition branches | Pin `BAD`, marginal-or-indeterminate, all-OK, and the fallback, each with its `(disposition, ladder_state)` pair. Must include a NON-SDP all-OK shape — AT28C256's SDP leg attaches fingerprints in every arm, so an AT28C256-only harness cannot see the flip. | ✓ |
| The all-OK non-SDP shape only | Minimal, directly targets D-4/D-6's declared re-key, but a change in the `BAD` or marginal arm lands silently. | |

**User's choice:** All four disposition branches

---

## Re-Key Protocol

### Q1 — How does a later phase legally move a pinned hash?

| Option | Description | Selected |
|--------|-------------|----------|
| Append, never edit | Rows carry `(shape_id, before_hash, after_hash, ledger_id)`; assert `after` if declared else `before`. The original value never leaves the tree, making RPT-E3's "nothing more" a check rather than a claim. | ✓ |
| Edit the literal in place | Simplest table; the MILESTONES.md row is the justification. But the before-hash survives only in prose and git history, and a wrong new value is indistinguishable from a right one at review. | |
| Single committed manifest, diffed whole | A re-key shows as a reviewable manifest diff. Clean signal, but declared and undeclared changes are both just diff lines. | |

**User's choice:** Append, never edit

### Q2 — Should the harness also pin the SET of shapes, not just each shape's hash?

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — assert the complete shape-id set | A committed sorted list asserted element-wise. Deleting an inconvenient row, or quietly widening the oracle, becomes a RED. | ✓ |
| No — per-row hash assertions are enough | Rows are self-describing and a removed row shows in the diff. Less machinery, but "green because the row was deleted" is a real failure mode across eight phases. | |

**User's choice:** Yes — assert the complete shape-id set

### Q3 — Should a declared re-key land in the same commit as the change that caused it?

| Option | Description | Selected |
|--------|-------------|----------|
| Separate, explicit re-key commit | The change lands and turns the gate RED; a second commit touching only `after_hash` and the ledger row makes it green. The re-key is its own reviewable unit and cannot be reflexively "fixed" inside a large diff. | ✓ |
| Same commit as the behaviour change | One atomic unit, causal link impossible to lose. But the hash edit is buried in the change's diff — exactly how a silent re-key gets through review. | |

**User's choice:** Separate, explicit re-key commit
**Notes:** This is a constraint on Phases 175–181, not only on 174. Each of those planners must carry it.

### Q4 — Should the ledger be pre-seeded with the four measured re-keys?

| Option | Description | Selected |
|--------|-------------|----------|
| Pre-seed with before-hashes, after blank | All four rows written now, each naming its owning phase. Total known blast radius stated up front; a fifth undeclared re-key stands out as an unplanned row. | ✓ |
| Leave empty until each phase lands | Nothing asserted before it is true, but the milestone then has no single place stating its blast radius — which is what was wrong at activation. | |

**User's choice:** Pre-seed with before-hashes, after blank

---

## Ledger Home + Delta Artifact

### Q1 — How should the meta/app repo boundary be handled for the ledger?

| Option | Description | Selected |
|--------|-------------|----------|
| App table authoritative + meta-side binding check | The app table is the machine-readable ledger, checked by the app suite. A checker in the META repo — which sees both trees via the submodule — asserts every filled `after_hash` has a MILESTONES.md row. The direction that can see both files holds the check, so it cannot fail open. | ✓ |
| App table authoritative, MILESTONES.md by hand | Nothing new to build, but this project has documented app-side gates that scan the other repo and fail OPEN. | |
| Mirror the ledger into the app as JSON | One checkable file, but GATE-06 names MILESTONES.md specifically and a quoted copy drifts. | |

**User's choice:** App table authoritative + meta-side binding check

### Q2 — What is GATE-04's delta measured over?

| Option | Description | Selected |
|--------|-------------|----------|
| Whole DB summary + per-issue rows | Aggregate over all 746 rows (the roadmap's wording) plus explicit per-chip rows for the 27 filed issues (research's wording). Both readings satisfied. | ✓ |
| Whole shipped database only | Complete and uniform, but buries the 27 names that matter behind 719 that no issue references. | |
| Filed-issue chips only | Tightest signal, but the criterion says "across the shipped database" and a future chip's first issue would be unmeasured. | |

**User's choice:** Whole DB summary + per-issue rows

### Q3 — How is the raw CLI token determined?

| Option | Description | Selected |
|--------|-------------|----------|
| Real resolution through `resolve_chip` | Feed each token through `chip_resolver.resolve_chip` — the path the CLI takes — and record the returned `part_number`. Measures aliases and comma-joined lists, where RPT-F1's title rule must be written. | ✓ |
| Lowercase-form comparison | Reproduces research's published 732/746 number trivially, but is a proxy for resolution and says nothing about aliases. | |
| The 27 tokens as actually typed | Ground truth about operator behaviour including the mixed casing already visible, but only covers chips already filed against. | |

**User's choice:** Real resolution through `resolve_chip`

### Q4 — Is the delta artifact a one-shot snapshot or regenerated?

| Option | Description | Selected |
|--------|-------------|----------|
| Script + committed output + drift test | Script generates, output committed, test asserts it still matches a fresh run. `chip_database.json` is GENERATED — a drift RED is the canonical-naming blast radius this gate exists to surface. | ✓ |
| One-shot measured snapshot | Cannot go stale-RED, matches "a committed, measured artifact" literally. But it silently stops describing reality the first time the database is regenerated. | |

**User's choice:** Script + committed output + drift test

---

## Claude's Discretion

Decided without asking, on standing project precedent:

- **Anti-vacuity leg is mandatory** — a planted mutation that must make the frozen table go RED. A gate authored before the content it guards can be unreachable; RED is not proven until seen.
- **All measurement in the py3.11 CI-replica venv**, never the devcontainer's default 3.12.
- **No new library** — HYG-02 is milestone-wide; the `syrupy` bounding belongs to Phase 181.
- **Fork `gsd/v1.36-dev-test-fidelity` off `beta` in the app submodule** (still on the v1.35 branch).
- **Use `/usr/bin/grep` or a bash script for gate evidence** — the devcontainer's `grep` is ugrep and honors `.gitignore`, silently under-scanning.

## Deferred Ideas

- Reproducing all 27 filed hashes from builders — scoped down to four; the committed artifact is the input if Phase 181 wants broader proof.
- A general report deserializer (`from_dict`) — deliberately not built; if RPT-E2 needs one, introduce it there with its own drift gate.
- Whether the 4.22 s whole-DB sweep runs on every push against a 737 s suite, or is marked slow — planner's call.
- `--fast` / `repeat_policy_tag` interaction with the pre-seeded UV `run_count` row — Phase 179 owns the UV shape.
- The stray uncommitted `tools/build_db.py` local-variable rename in the submodule — noted, not this phase's business.
