# Phase 174: Blast-Radius Invariance Harness - Context

**Gathered:** 2026-09-03
**Status:** Ready for planning

<domain>
## Phase Boundary

A **test-only** harness in `firestarter_app`. No production module changes, no firmware change.

This phase builds the oracle the rest of v1.36 is measured against, and nothing else. It delivers
four artifacts:

1. A frozen `(report shape → absolute 12-hex `dedup_fingerprint`)` table plus its committed report
   corpus, both under `firestarter_app/tests/fixtures/` (GATE-01, GATE-02, GATE-05).
2. A pinned `build_db_diff` disposition + `ladder_state` output over the same shapes (GATE-03).
3. A measured, committed raw-CLI-token → `part_number` delta artifact (GATE-04).
4. A pre-seeded re-key ledger — machine-readable in the app, narrated in meta's `MILESTONES.md`
   (GATE-06).

Nothing else in v1.36 may land before this phase is green. This is the milestone's one hard
ordering constraint.

**Explicitly NOT in this phase:** any change to `dedup_fingerprint`, `classify_fingerprint`,
`build_db_diff`, `derive_plan`, the report schema, or the transport counters. Those are Phases
175–181. This phase only *measures* them at the branch base.

</domain>

<decisions>
## Implementation Decisions

### Corpus Form

- **D-01:** A frozen shape is stored as a **Python builder plus a committed `to_dict()` JSON
  snapshot** — the builder constructs the `DiagnosticReport` and the hash is taken off the object
  exactly as production does, and the same shape's `to_dict()` output is committed as JSON beside
  it. **No deserializer is written.** There is no `from_dict` anywhere in the tree today;
  `DiagnosticReport` is constructed at exactly one production site
  (`firestarter_app/firestarter/cli_handlers.py:2388`) and `dedup_fingerprint` takes the object,
  not a dict. A loader would be new machinery sitting between fixture and hash that production
  never exercises — if it drifted, the oracle would lie while staying green. The committed JSON is
  an *output* snapshot, so it carries no such risk, and it is already in place as Phase 181's
  RPT-E2/E3 parse oracle.

- **D-02:** Frozen shapes come from **two separate tables**. A hand-specified table pins the hash
  *function* and is immune to database regeneration. A second, smaller table built from real
  `derive_plan` output for named chips (m27c512/full, the SST27SF512 six-step shape) pins the
  shapes research actually measured. `chip_database.json` is GENERATED, so a generator fix in a
  later milestone will redden only the second table — and that is a signal worth having, not noise.
  A hand-specified-only table could not catch re-key path #2 (SDP-step pruning, 637 of 677 chips),
  which arrives via plan shape rather than via the hash function.

- **D-03:** Builders live in a **new module under `firestarter_app/tests/fixtures/`**, beside the
  committed JSON — not grown inside `tests/test_diagnostic_report.py`, which already carries 68
  `dedup_fingerprint` call sites. Phase 181's schema tests must be able to import the shapes
  without pulling that module in. — **Reversibility:** costly — every later phase's test imports
  and every ledger `shape_id` reference points at this module path; moving it later means touching
  seven phases' test files plus the ledger.

- **D-04:** Every frozen shape carries a **stable string `shape_id`** (e.g. `uv-slot-write-pass`,
  `sst27sf512-six-step`). The re-key ledger, the pinned ladder table, and the committed JSON
  filenames all key off it, so a declared re-key names exactly which rows it is licensed to move.
  Positional indices were rejected: this milestone *will* insert shapes as later phases land, and
  reordering would silently invalidate every ledger reference. — **Reversibility:** one-way once
  ledger rows exist — a `shape_id` is a published contract between the app table and
  `MILESTONES.md`; renaming one after a re-key is declared orphans that ledger row.

### Table Coverage

- **D-05:** The synthetic row set is derived from **this milestone's own change list**, not from a
  generic cross-product: the four measured re-key paths (read-back gating, SDP-step pruning,
  canonical naming, UV `run_count` collapse), plus ATTR-01's status-axis shape and PRUNE-03's
  synthesized-fingerprint shape. Every row exists because a *named later phase* will be measured
  against it. The roadmap floor of four was rejected because ATTR-04's criterion — "confirmed by
  Phase 174's oracle reporting zero unexpected hash changes when the status axis is exercised" —
  would have had no row to confirm against.

- **D-06:** All **27 filed `[dev test]` issues** are committed as `(issue number, chip, embedded
  12-hex)` rows — the actual history a re-key forks. Additionally, builder shapes must
  **reproduce the filed hash** for the four chips research already measured: **m27c512,
  sst27sf512, at28c256, w27e257**. Reproducing all 27 was rejected as first-phase scope and
  because several would need issue bodies parsed — the loader D-01 declines to build. Recording
  them without any reproduction assertion was rejected: this project has a standing rule against
  gates that assert nothing.

  Real dedup groups already exist in the wild and must survive: `00e121446ceb` spans gh#20 / gh#21
  / gh#32 (at28c256, N=3), and `334c3fa198bf` spans gh#39 / gh#40 (at28c256, N=2). A re-key does
  not merely change a string — it resets `count_agreeing`'s promotion count for these groups.

  **Superseded in part — operator ratification, 2026-09-03.** The four-chip reproduction reduction
  no longer stands: plan 174-04 reproduces every filed hash, **26 of 26** (**26 filed issues, not
  27** — the count was measured by title rather than inherited). The reduction's stated cause is
  gone, because the corpus commits each row's `steps`, `run_counts` and `coverage_tag` as data
  rather than parsing issue bodies at test time; the enabling discovery was that a step's
  `fingerprint` serialises as a bare classification string rather than an object (read as an object,
  0 of 26 reproduce; read as a string, 26 of 26 do). The widening applies to the corpus reproduction
  assertion only — the four named chips keep their dedicated builder shapes and the `SHAPE_IDS` set
  is unchanged. Everything else in this decision stands, and no decision id is added, renumbered or
  split by this amendment.

- **D-07:** The **sorted `to_dict()` key-list pin lands in this phase**, not Phase 181. The
  committed JSON snapshots are being written here anyway, so an element-wise sorted key-list
  assertion on top of them is a few lines. It also means Phase 181's three key deletions
  (`voltage.vpp_mv`, `voltage.vpe_mv`, `banner.locked_steps`) are measured against a gate that
  predates them, rather than landing in the same phase as their own gate. This is an addition to
  the roadmap's five stated criteria, taken deliberately — research named it "the one genuinely
  missing schema gate" and assigned it to Phase 174.

- **D-08:** The ladder pin covers **all four `build_db_diff` disposition branches** — `BAD`,
  marginal-or-indeterminate, all-OK, and the fallback — each with its `(proposed_disposition,
  ladder_state)` pair. Cheap once shapes exist, and it catches a ladder change in any arm.
  **It must include a non-SDP all-OK shape.** Research measured that AT28C256's SDP leg attaches
  fingerprints in every arm, so a harness exercising only AT28C256 cannot see the D-4/D-6 ladder
  flip at all.

### Re-Key Protocol

- **D-09:** **Append, never edit.** Each row carries `(shape_id, before_hash, after_hash,
  ledger_id)`. `after_hash` is `None` until a phase declares the re-key; the assertion is
  `current == after_hash if declared else before_hash`. The original value never leaves the tree,
  so RPT-E3's "exactly the change it declared and nothing more" becomes a machine check rather
  than a sentence, and the before-hash stays readable without git archaeology. — **Reversibility:**
  costly — the four-tuple row shape is consumed by seven later phases and by the meta-side ledger
  checker; changing it mid-milestone means rewriting every declared row.

- **D-10:** The harness also asserts the **complete `shape_id` set**, element-wise, against a
  committed sorted list — the same idiom as the `to_dict()` key list. Deleting an inconvenient row,
  or adding one that quietly widens the oracle, is a RED. Without this, the cheapest route past a
  failing gate is to remove the row, and this milestone has eight phases of which seven re-key
  something.

- **D-11:** A declared re-key lands in **its own commit**, separate from the behaviour change that
  caused it. The behaviour change lands and turns the gate RED; a second commit touching only
  `after_hash`, the ledger row, and nothing else makes it green. The re-key is then a reviewable
  unit on its own, and an executor cannot reflexively "fix the test" inside a large change commit.
  **This is a constraint on Phases 175–181, not just on 174** — the planner for each of those
  phases must carry it.

- **D-12:** The ledger is **pre-seeded in this phase** with all four measured re-keys: before-hashes
  filled, `after_hash` empty, each row naming its owning phase. The milestone's total known blast
  radius is then stated up front as a commitment, and a *fifth*, undeclared re-key stands out as an
  unplanned row rather than blending in.

  The four measured pairs from research (against `firestarter_app @ 0a93999`), to be re-measured at
  the actual branch base before freezing:

  | # | Change | Owner | before → after |
  |---|---|---|---|
  | 1 | Gate the fingerprint read-back on failure | Phase 177 | `4dc282a5d596` → `60a031573aab` (SST27SF512 six-step) |
  | 2 | Prune unsupported SDP steps from `Plan.steps` | out of scope (rejected) | `a00791f1c2b4` → `7d1cd4157cfa` (m27c512/full) |
  | 3 | Canonical `part_number` naming | Phase 181, avoided by D-2 | `a00791f1c2b4` → `a6f6c6354047` |
  | 4 | UV blank-check abort → `run_count` collapse | Phase 179 | shape-level, via `repeat_policy_tag` |

  Rows 2 and 3 are re-keys the milestone has decided **not** to take (D-2 makes naming additive;
  dropping unsupported steps is Out of Scope). They are still seeded, because the ledger's job is
  to record the blast radius that *exists*, and a later phase that accidentally takes one must
  redden against a row that already names it.

### Ledger Home and the GATE-04 Delta

- **D-13:** The **app-side table is the authoritative machine-readable ledger**, checked by the app
  suite. A checker in the **meta repo** — which can see both trees, since `firestarter_app` is a
  submodule of it — asserts that every filled `after_hash` has a matching `MILESTONES.md` row. The
  direction that can actually see both files is the one that holds the check, so it cannot fail
  open. An app-side gate reading meta would be the same shape as this project's documented
  fail-open host gates that scan firmware source.

- **D-14:** GATE-04's delta is measured as a **whole-database aggregate over all 746 rows PLUS
  explicit per-chip rows for each of the 27 filed issues**. The roadmap criterion says "across the
  shipped database"; research says "for every chip with a filed `[dev test]` issue". Both readings
  are satisfied rather than one being chosen — the aggregate answers the criterion, and the 27
  named rows are the ones whose titles RPT-F1 can actually change.

- **D-15:** The raw CLI token is resolved through **`chip_resolver.resolve_chip`**
  (`firestarter_app/firestarter/chip_resolver.py:16`) — the path the CLI actually takes — and the
  returned `part_number` is recorded. Measures the real mapping including aliases and comma-joined
  lists, which is exactly where RPT-F1's "which alias does a title show when `part_number` is a
  comma-joined list" rule has to be written. The lowercase-form proxy (732/746 differ) may be
  reported alongside as the published number, but it is not the measurement.

- **D-16:** The delta artifact is **script-generated, committed, and drift-tested**: a script in
  `firestarter_app` produces it, the output is committed, and a test asserts the committed file
  still matches a fresh run. `chip_database.json` is GENERATED, so the delta moves whenever the
  generator does — and a drift RED there *is* the canonical-naming blast radius this gate exists to
  surface, not noise. Per standing policy the script must be owned by this repo, not imported from
  elsewhere.

### Claude's Discretion

Decided without asking, on standing precedent — the planner should treat these as locked:

- **Anti-vacuity is mandatory.** The frozen table gets a planted-mutation leg that must make it go
  RED. A gate authored before the content it guards can be unreachable and prove nothing; RED is
  not proven until it has been *seen*. Copy the anti-vacuity discipline from
  `firestarter_app/tests/test_erase_flag_invariants.py` and the closure idiom from
  `firestarter_app/tests/test_chip_test_sdp_leg.py:827`
  (`test_shipped_ops_never_reach_sdp_arm`).
- **All measurement in the py3.11 CI-replica venv**, never the devcontainer's default 3.12, which
  is proven in this project to hide breakage that reddens beta CI. `uv venv --python 3.11`.
- **No new library.** HYG-02 is milestone-wide; stdlib + pytest only. `syrupy>=5.0,<7` bounding is
  Phase 181's, not this phase's.
- **Branch:** fork `gsd/v1.36-dev-test-fidelity` off `beta` **in the app submodule too**. The
  submodule is currently still on `gsd/v1.35-documentation-consolidation-wiki-migration`.
- **Grep in this devcontainer is ugrep and honors `.gitignore`** — it silently under-scans. Use
  `/usr/bin/grep` or a `bash` script for any gate evidence.

### Folded Todos

None. 36 todos matched Phase 174 by keyword, all at an undiscriminating 0.60 score; none is
about this phase's work. Three todos already carry `resolves_phase` for this milestone (177, 181,
181) and are correctly homed there.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirements
- `.planning/ROADMAP.md` §"Phase 174: Blast-Radius Invariance Harness" — the five success criteria
  that bound this phase. Note D-07 adds a sixth deliverable (the `to_dict()` key-list pin)
  deliberately.
- `.planning/REQUIREMENTS.md` §"Blast-Radius Oracle" — GATE-01…GATE-06 verbatim.
- `.planning/REQUIREMENTS.md` §"Decisions taken at definition" — D-1…D-8, settled by the operator
  2026-09-02; no phase re-litigates them. D-2 (additive canonical naming), D-3 (`schema_version`
  2.0), D-4/D-6 (the `match` bucket and its deliberate one-time re-key) all bear on what this
  phase must pin.
- `.planning/REQUIREMENTS.md` §"Out of Scope" — dropping unsupported steps from `Plan.steps` and
  `RIG_FAULT` as a sixth verdict are both rejected; the ledger seeds a row for the former anyway
  (D-12).

### Research (measured against `firestarter_app @ 0a93999`)
- `.planning/research/SUMMARY.md` §"Executive Summary" — the four measured re-key paths with their
  before/after hashes, and the proof that every existing dedup test is relational.
- `.planning/research/SUMMARY.md` §"Phase 174: Blast-radius invariance harness" — the recommended
  deliverable list, including the AT28C256 ladder-flip blind spot (see D-08).
- `.planning/research/SUMMARY.md` §"Critical Pitfalls" 1 — "any plan that says 'dedup is unaffected
  because no *field* changed'" is the warning sign.
- `.planning/research/STACK.md` — why no library is added; the py3.11 CI-replica requirement.
- `.planning/research/PITFALLS.md` — full pitfall detail.

### Ledger destination
- `.planning/MILESTONES.md` — the re-key ledger section this phase creates (GATE-06). Existing
  milestone sections show the house format; §v1.33 "Post-Close Correction: The Sweep's Oracle Was
  Blind" is the closest precedent for recording a measurement that falsified a prior claim.

### Product code this phase measures (reads only — does not modify)
- `firestarter_app/firestarter/diagnostic_report.py:186` — `dedup_fingerprint`. The docstring
  states what it excludes; `parts` is `[chip, protocol]` + one `f"{op}={verdict}:{cls}"` per step
  + `repeat_policy_tag` + `coverage_tag` when non-empty.
- `firestarter_app/firestarter/diagnostic_report.py:287` — `build_db_diff`, the four disposition
  branches D-08 pins.
- `firestarter_app/firestarter/diagnostic_report.py:260` — `_LADDER_COMMUNITY_REPORTED` and
  siblings.
- `firestarter_app/firestarter/diagnostic_report.py:771` — `DiagnosticReport.to_dict`, the source of
  the committed JSON snapshots and of D-07's key list.
- `firestarter_app/firestarter/diagnostic_report.py:150` — `is_submittable`, the existing choke
  point Phase 178 will gate at.
- `firestarter_app/firestarter/cli_handlers.py:2388` — the **sole** production `DiagnosticReport`
  construction site. D-01 rests on this being singular.
- `firestarter_app/firestarter/chip_test.py:162` — `classify_fingerprint`, whose four buckets have
  no perfect-match arm today (why a passing write reports `indeterminate`).
- `firestarter_app/firestarter/chip_resolver.py:16` — `resolve_chip`, D-15's measurement path.
- `firestarter_app/tools/parse_devtest_issue.py:164` — `count_agreeing`, which reads the
  **embedded** hash and never re-hashes. This is why a re-key is permanent.

### Test idioms to copy, not reinvent
- `firestarter_app/tests/test_diagnostic_report.py:1377` — the single existing frozen-hash literal
  (`"a0a50436ae3d"`) and its "a GATE, not a claim" docstring. This phase generalizes it.
- `firestarter_app/tests/test_diagnostic_report.py:151` — `_minimal_report`, the existing builder
  shape to model the new fixture module on.
- `firestarter_app/tests/test_diagnostic_report.py:1311` — `_coverage_report`, the builder behind
  the existing frozen literal.
- `firestarter_app/tests/test_erase_flag_invariants.py` — the whole-DB sweep + anti-vacuity
  discipline.
- `firestarter_app/tests/test_chip_test_sdp_leg.py:827` — `test_shipped_ops_never_reach_sdp_arm`,
  the closure-sentinel idiom.
- `firestarter_app/tests/test_sdp_db_invariant.py`, `firestarter_app/tests/test_page_size_invariants.py`
  — two more shipped whole-DB sweeps.

### Related open finding
- `.planning/todos/pending/build-db-diff-ladder-state-community-reported-regression.md` — the
  ladder flip D-4/D-6 fixes in Phase 177. Not folded here, but it names exactly which shape
  GATE-03 must pin, or the flip lands silently.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`_minimal_report` / `_coverage_report`** (`tests/test_diagnostic_report.py:151`, `:1311`):
  working builders that construct `DiagnosticReport` from a `step_specs` list of
  `(op, verdict, fingerprint_classification, reason)` tuples. The new fixture module should be a
  generalization of these, not a fresh design.
- **The one frozen literal at `tests/test_diagnostic_report.py:1377`**: an existing, already-blessed
  precedent for absolute-hash assertion, with a docstring that argues the case. Its reasoning is
  reusable verbatim.
- **`firestarter_app/tests/fixtures/`**: the directory already exists and holds ~20 `planted_*`
  counter-example files. The planted-mutation idiom D-Discretion requires is already the house
  style here.
- **27 filed `[dev test]` issues** in `henols/firestarter_prom`, each with its `dedup_fingerprint`
  in the title, reachable via `gh issue list`. This is a free, real historical corpus.

### Established Patterns
- **Whole-database sweeps** ship three times already (`test_erase_flag_invariants.py`,
  `test_sdp_db_invariant.py`, `test_page_size_invariants.py`). Copy, do not invent.
- **Element-wise committed comparison** is the house idiom for "pin a list" (used by the
  constants-parity tests). D-07 and D-10 both use it.
- **Anti-vacuity legs with a planted counter-example** are how this repo proves a gate is not
  tautological. There is a live counter-example of the failure mode: the `MAX_27C020_SIZE` parity
  test guards a firmware `#define` that does not exist.
- **Hash discipline already in the code**: both `repeat_policy_tag` and `coverage_tag` return `""`
  for their default case and are appended only when non-empty, *precisely* so no historical group
  is re-keyed. Any new discriminator must follow the same empty-default rule.

### Integration Points
- The new fixture module is imported by this phase's tests and, from Phase 175 onward, by every
  later phase's regression tests. Its import path is effectively a published contract (D-03).
- The meta-side ledger checker (D-13) is new tooling in the meta repo — it has no existing home;
  `/workspaces/tools/` currently holds only `catalog/` and `wiki/`. `tools/wiki/` checkers were
  retired 2026-09-02, so there is no live meta-side checker to model on and no CI workflow
  currently registering one. The planner must decide where it runs.

### Branch-base facts verified at discussion time
- `firestarter_app` submodule is on `gsd/v1.35-documentation-consolidation-wiki-migration` at
  `0a93999`. `origin/beta` is 6 commits ahead, but the **entire content delta is one line in
  `firestarter/__init__.py`** (a version bump) — and `dedup_fingerprint` deliberately excludes
  `host_version`. **Research's measured hashes reproduce on `beta`.** They must still be
  re-measured at the branch base before freezing, but no surprise is expected.
- `firestarter_app/tools/build_db.py` has an **uncommitted** stray change — a local-variable
  rename `_AT28C_DIP24_NAMES` → `AT28C_DIP24_NAMES`, cosmetic, no DB-output effect. It is not this
  phase's work; do not sweep it into a commit.

</code_context>

<specifics>
## Specific Ideas

- **"A gate authored before the content it guards can be unreachable"** is the framing that drove
  the anti-vacuity requirement. The harness must be *seen* RED, not assumed RED.
- **The ledger's job is to record the blast radius that exists, not only the one being taken** —
  which is why rows 2 and 3 (re-keys the milestone declines) are still seeded (D-12).
- **The 27 filed issues are the point.** The abstract statement "a re-key forks history" becomes
  concrete when it is `00e121446ceb` spanning gh#20 / gh#21 / gh#32 — a three-member at28c256
  dedup group that `count_agreeing` would reset to one.
- **The cross-repo check must run from the side that can see both trees.** Meta holds the app as a
  submodule; the app cannot see meta. Every app-side gate that scanned the other repo in this
  project has failed open.

</specifics>

<deferred>
## Deferred Ideas

- **Reproducing all 27 filed hashes from builders** — **CLOSED — delivered in this phase by
  operator ratification 2026-09-03.** Reason: the corpus commits each row's step vector as data, so
  no issue-body parsing and no deserializer is needed and every filed hash reproduces through the
  real `dedup_fingerprint`. Corrected count: **26 filed issues, not 27**. The `(issue, chip, hash)`
  artifact remains the input for any broader historical work, and the supersession is noted in prose
  at the D-06 bullet rather than as a new decision.
- **A general report deserializer (`from_dict`)** — deliberately not built (D-01). If Phase 181's
  RPT-E2 forward-compatibility work turns out to need one, it should be introduced there with its
  own drift gate against `cli_handlers.py:2388`, not smuggled in here.
- **Whether the 4.22 s whole-DB sweep runs on every push** against a 737 s suite, or is marked
  slow — raised, set aside as a planner call.
- **`--fast` / `repeat_policy_tag` shape interaction** with the pre-seeded UV `run_count` re-key
  row — raised, set aside; Phase 179 owns the UV shape.
- **The stray uncommitted `tools/build_db.py` rename** — noted, not this phase's business.

### Reviewed Todos (not folded)

- **`build-db-diff-ladder-state-community-reported-regression.md`** — the `ladder_state` no longer
  reaching `community-reported` for a genuinely-passing ALLOW chip. This is exactly what D-4/D-6's
  `match` bucket fixes, and it belongs to **Phase 177**. Reviewed here because it names the shape
  GATE-03 must pin (D-08).
- **`2026-08-30-gate-fingerprint-readback-on-step-failure.md`** — already tagged `resolves_phase: 177`.
- **`2026-08-31-dev-test-chip-name-must-match-database.md`** — already tagged `resolves_phase: 181`.
- **`delete-banner-locked-steps-dead-field.md`** — already tagged `resolves_phase: 181`.
- The remaining 32 keyword matches (firmware safe-state, VPP checks, JP4 labels, FM1608 byte 0,
  pinout corroboration, etc.) are unrelated to a test-only harness phase and were not considered
  further.

</deferred>

---

*Phase: 174-blast-radius-invariance-harness*
*Context gathered: 2026-09-03*
