# Phase 175: Structural Sentinel over `derive_plan` - Context

**Gathered:** 2026-09-04
**Status:** Ready for planning

<domain>
## Phase Boundary

A **test-only** sentinel in `firestarter_app`. No production module change, no firmware change,
**no re-key** — this phase must leave every Phase 174 frozen hash untouched.

It delivers the *licence* Phase 177's read-back gate rests on: a relational predicate over
`derive_plan` output, proven RED against a planted counter-example and green across the shipped
database, plus a no-drop proof for unsupported steps. Requirements: **PRUNE-05**, **PRUNE-06**.

Four things land:

1. A **write→verify** predicate over `Plan.steps`, anchored to a total, fail-closed partition of
   the module's own `OP_*` vocabulary (roadmap SC1, SC2, SC3 / PRUNE-06).
2. A separately-named **erase→blank-check** leg (operator decision, this discussion).
3. A **no-drop proof** for unsupported steps, in two halves — a frozen plan-shape pin and a
   `run_plan` alignment sweep (roadmap SC4 / PRUNE-05).
4. A **UV structural pin** locking the 2026-08-22 `aq6` write-scope ceiling in place (operator
   decision, this discussion).

**Explicitly NOT in this phase:** any change to `derive_plan`, `run_plan`, `dedup_fingerprint`,
`classify_fingerprint`, `build_db_diff`, the report schema, the transport counters, or the seed
file. No behaviour change of any kind. The **fault-mode table belongs to Phase 177**, which names it
as a deliverable — PITFALLS suggests 175 for it and the roadmap overrides that.

</domain>

<decisions>
## Implementation Decisions

### The Write→Verify Predicate

- **D-01:** The predicate decides which ops need a verify by a **total partition that fails closed**.
  Every `OP_*` string discovered at runtime via `vars(chip_test)` must land in exactly one of two
  buckets — *requires-verify* (`OP_WRITE`, `OP_WRITE_PARTIAL`) or *exempt, with a named reason*
  (`OP_ID`, `OP_READ`, `OP_BLANK_CHECK`, `OP_ERASE`, `OP_SDP_LOCK`, `OP_SDP_UNLOCK`, and the four
  SDP-leg write-shaped ops). An op in neither bucket is a RED. This is roadmap SC3 read literally:
  "a future operation type omitted from the closure list cannot silently escape the check."

  Rejected: an allow-list plus an equality pin (a future write-shaped op is genuinely outside the
  predicate until someone edits the literal — the equality leg reddens while the behavioural sweep
  stays green over an open gap); and derivation by subtraction from `_DESTRUCTIVE_OPS` (records the
  exemption reasons nowhere, and silently re-scopes itself whenever `_DESTRUCTIVE_OPS` is widened
  for an unrelated purpose).

  **The exemption bucket is load-bearing, not bookkeeping.** The SDP leg emits four write-shaped ops
  — `write-baseline-b`, `write-baseline-a`, `write-inhibited`, `write-restored` — and **none has an
  `OP_VERIFY` behind it, by design**. On `write-inhibited` the read-back *is* the oracle
  (PITFALLS Pitfall 3). A naive "every write needs a verify" predicate fires on all 43 SDP-ALLOW
  chips immediately.

- **D-02:** "Behind it" means **a supported `OP_VERIFY` at a higher index within the same cycle
  block**, with the block found via the shipped `cycle_block_bounds` helper
  (`firestarter_app/firestarter/chip_test.py:1236`) — never a re-implementation of the block rule.
  Matches PITFALLS' own wording ("followed, in the same cycle, by an `OP_VERIFY`") and survives a
  future legitimate step being inserted between write and verify.

  Rejected: strict adjacency (true of all four shipped shapes today, but it re-implements ordering
  knowledge `cycle_block_bounds` already owns — two sources that can drift); and anywhere-later in
  `Plan.steps` (a verify sitting after the six SDP-leg steps would satisfy it).

- **D-03:** The verify must be `supported=True`. A `supported=False` verify behind a live write **is**
  a write with no oracle — the exact defect the rule exists to forbid — and must not pass merely
  because a step with the right op string is present. Decided without asking; it is the rule's own
  substance.

- **D-04:** The verify must additionally match the write on **`write_region`, `region_policy` and
  `cycle_payload`**. All three are set equal on the two steps by `derive_plan` today and nothing
  downstream re-derives them, so there is no false-RED risk; each catches a distinct real failure —
  verifying the wrong window, the wrong *kind* of window, or against bytes the write never staged.
  (Operator delegated: "you decide.")

- **D-05:** `OP_ERASE` is classified *requires-oracle: blank-check*, but asserted by its **own,
  separately-named leg** — "an executable erase step has a blank-check at a higher index" — kept
  distinct from the write→verify predicate. `derive_plan` already relocates the blank-check to sit
  *after* an executable erase precisely so it doubles as that step's oracle
  (`chip_test.py:747-750`), single-sourced through `erase_is_executable`; that pairing has no guard
  today. Keeping the legs separate preserves the exact 1:1 mapping onto PRUNE-06's wording, which
  matters when **Phase 177 cites this sentinel as its licence**.

  Rejected: exempting erase outright (leaves the pairing unguarded — a future edit moving the
  blank-check back ahead of the erase would go unnoticed); and folding both into one "every mutating
  op has an oracle" predicate (widest coverage, but Phase 177 could no longer point at a leg that
  maps cleanly to its requirement).

- **D-06:** The op classification lives **test-side, cross-checked against `vars(chip_test)`** — the
  shipped `test_shipped_ops_never_reach_sdp_arm` idiom
  (`firestarter_app/tests/test_chip_test_sdp_leg.py:827`). Decided on precedent, not asked: it is
  the house pattern for exactly this, and it keeps the phase strictly test-only. A production
  frozenset in `chip_test.py` would be single-sourced but would make a test-only phase edit product
  code that nothing in production reads.

  Note for the planner: Python's normal exhaustiveness route (`assert_never` over an `Enum`/`Literal`,
  checked by mypy) is **closed here** — `Step.op` is a bare `str` and the vocabulary is 13
  module-level `str` constants. The closure must be a runtime set-difference sentinel; no type
  checker can see an omission.

### Sweep Domain

- **D-07:** The sweep covers the **shipped database only**, via
  `EpromDatabase(skip_local_override=True)` — the idiom every shipped whole-DB sweep already uses.
  **This resolves D-8**, which `.planning/REQUIREMENTS.md` explicitly deferred to this phase: the
  sentinel makes **no claim** about user-override entries in `~/.firestarter/database.json`. No later
  phase should re-open it.

  Rejected: adding synthetic adversarial override rows through a stub `db`; and reading a real
  override file when present (results differ per machine, and this project has a known leak where
  the app writes `~/.firestarter/config.json` despite `FIRESTARTER_CONFIG_DIR`, so such a test cannot
  be reliably isolated in CI).

- **D-08:** Scopes swept are **`"full"` and `"partial"`**. Decided on research, not asked: `"none"`
  emits no write step at all, so the write→verify rule is vacuously true across ~677 extra plans, and
  research classifies `"none"` as library/test surface only. `dev test` itself only ever produces
  `"full"` (non-UV) or `"partial"` (UV), so full+partial is a strict superset of the reachable domain.

- **D-09:** Anti-vacuity is **the planted counter-plan *plus* a mutated-corpus sweep**. Criterion 1's
  hand-built plan (a write, no verify) proves the predicate is not tautological. On top of it: for
  **every real plan in the sweep that contains a write**, a *copy* with its verify step removed must
  be reported as a violation. This proves sensitivity on all 746 rows rather than on one example, and
  makes a sweep that silently visits zero rows impossible to pass. It mutates plan copies, so nothing
  needs monkeypatching and nothing needs reverting.

  The empty-sweep trap is documented in this repo, not hypothetical:
  `test_erase_flag_invariants.py`'s own docstring warns that `for row in db.proms` iterates
  *manufacturer keys*, not chip records, so a wrong selector makes every downstream assertion pass
  against an empty set. And `MAX_27C020_SIZE`'s parity test guards a firmware `#define` that does not
  exist — a live example of a gate that has always passed vacuously.

### PRUNE-05 — the No-Drop Proof

- **D-10:** "Counting `StepResult` entries **before and after**" resolves as *before* = `Plan.steps`,
  *after* = the `StepResult` list. Both halves are built, because **neither alone is sufficient**:

  1. **Frozen half (measured 1.18 s):** a committed pin of the **4 distinct op-sequences** the whole
     database produces, plus the chip counts mapping onto them. Pruning a step from `derive_plan`
     reddens this immediately.
  2. **Execution half (measured ~21 s extrapolated):** a `run_plan` sweep with a mock operator
     asserting `len(results) == len(plan.steps)` for every chip **and** that every `supported=False`
     step's result carries the `NA` verdict.

  **The hole that forces both:** an alignment-only sweep cannot catch the change PRUNE-05 forbids. If
  a future phase prunes unsupported steps inside `derive_plan`, both sides shrink together and
  alignment still holds — it would pass while the six SDP ballast steps on 637 chips silently vanish
  from the dedup hash. Conversely a frozen-count-only pin says nothing about whether an unsupported
  step actually produces a `StepResult` with `NA`, which is the other half of PRUNE-05's sentence.

- **D-11:** The frozen op-sequence pin **reddening when `chip_database.json` is regenerated is
  signal, not noise** — the same call Phase 174 took deliberately at its D-02. The database is
  GENERATED; a generator change that moves plan shapes is exactly what this pin exists to surface.
  Decided on precedent.

### The UV Write-Scope Ceiling (raised by the operator; resolved)

- **D-12:** The **2026-08-22 `aq6` reversal stands** and is **pinned by this phase's sentinel**.

  Background, because the operator's stated rule described the *reverted* design: quick task
  `260822-aq6` (`firestarter_app` commit `2b42dac`) retired the full-device-on-blank UV write and its
  consent prompt, reversing `260821-wna` from one day earlier "with the operator's explicit
  agreement". Today `_resolve_write_scope` is *"UV → partial, else full"* with **no prompt on any
  path** (`interactive` is accepted and immediately `del`'d), so `full_device_permitted` is never True
  for a UV part on a reachable run, and `_resolve_write_target`'s blank→full-device branch is gone.
  A UV part always gets **one masked 256-byte slot**, blank or not, chosen top-down (0xFF00 first).
  `chip_is_blank` is still computed and still reported — it no longer decides how much of the part is
  spent. The stated reason: a 64 KiB part yields ~256 slot runs, and the full-device branch spent all
  of them at once, while `uv_slot_starts` being top-down means every address line is already
  exercised from run 1.

  The rest of the operator's rule **is already exactly what the code does**: `region_policy ==
  "uv-slot"` is set only when `is_uv_eprom` (never SRAM/FRAM/Flash/EEPROM); the blank-check is
  emitted *ahead* of the write for UV specifically because the write is irrecoverable; a non-blank
  part probes candidate slots top-down and takes the first clearing the bit floors; none qualifying →
  SKIPPED as saturated with "a UV erase is required".

  **What this phase pins** (structural, over `derive_plan` output — honest at every scope):
  - `is_uv` ⟹ `region_policy ∈ {uv-slot, fixed}` and **never** `full-device`.
  - The converse: `region_policy == "uv-slot"` ⟹ `is_uv`. Nothing else may claim the policy.
  - `is_uv` and a write step exists ⟹ a blank-check step sits at a **lower** index than the write.
  - **A handler-level leg**: `_resolve_write_scope` returns `"partial"` for **every** UV row in the
    database. This is the leg that matters most — the `derive_plan` pins stay true even if that one
    line is changed, so without it the ceiling is not actually guarded.

  **Do not assert `full_device_permitted == False` on a UV write step as a `derive_plan` invariant.**
  It is `write_scope == "full"` verbatim, independent of UV-ness, so it *is* True for a UV chip at
  `write_scope="full"` — a library-surface call. That combination is unreachable from `dev test` and
  inert anyway: `full_device_permitted` no longer gates anything on the `uv-slot` path
  (`chip_test.py:2805-2821`). Asserting it would be a false invariant.

  — **Reversibility:** costly — the pin encodes an operator-agreed product decision. Undoing it means
  reversing `aq6` in `cli_handlers.py`, deleting `TestUVWriteHasNoPrompt`'s five legs (which pin the
  prompt's absence on every path), and consulting Phase 174's ledger, which already carries a seeded
  UV `run_count` re-key row.

### Claude's Discretion

Decided without asking, on standing precedent — the planner should treat these as locked:

- The field-matching set in D-04 above is the one thing the operator explicitly delegated
  ("you decide"): region, policy and payload, all three.
- **No re-key.** This phase is test-only and must leave every Phase 174 frozen hash untouched. If any
  frozen hash moves, that is a defect in this phase, not a re-key to declare. Phase 174's **D-11**
  (a declared re-key lands in its own commit, separate from the behaviour change) binds Phases
  175–181 and therefore binds this one, vacuously if all goes well.
- **Anti-vacuity must be *seen* RED**, not assumed. A gate authored before the content it guards can
  be unreachable and prove nothing. Every leg's RED is transcribed into the plan summary.
- **All measurement in the py3.11 CI-replica venv** (`uv venv --python 3.11`), never the
  devcontainer's default 3.12, which is proven in this project to hide breakage that reddens beta CI.
  The 1.18 s / ~21 s figures above were taken on the devcontainer interpreter and are order-of-
  magnitude, not CI-replica measurements — re-take them.
- **No new library.** HYG-02 is milestone-wide; stdlib + pytest only.
- **Grep in this devcontainer is ugrep and honors `.gitignore`** — it silently under-scans. Use
  `/usr/bin/grep` or a `bash` script for any gate evidence.
- **No comments in source.** Standing operator hard rule, broadened 2026-08-29 to zero comments; a
  plan cannot override it. Docstrings are exempt (and Click docstrings are user-facing `--help`
  text — do not sweep those either).
- **Module placement**, on Phase 174's D-03 precedent: the new test module lives in
  `firestarter_app/tests/`, and any committed artifact (the frozen op-sequence pin) beside the
  existing fixtures in `firestarter_app/tests/fixtures/`.
- **No sentinel over `Plan.locked_destructive`.** A pending todo proposes deleting that field and is
  already tagged `resolves_phase: 181`; building a guard over it now would be work Phase 181 deletes.

### Folded Todos

None. 36 todos matched Phase 175 by keyword, 21 of them at an undiscriminating 0.60 score; none is
about this phase's work. The three closest are already homed elsewhere — see Reviewed Todos below.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirements
- `.planning/ROADMAP.md` §"Phase 175: Structural Sentinel over `derive_plan`" — the four success
  criteria that bound this phase. D-05 and D-12 add two legs beyond them, both deliberately and both
  recorded above.
- `.planning/REQUIREMENTS.md` §"No-Information Operations" — **PRUNE-05** and **PRUNE-06** verbatim.
- `.planning/REQUIREMENTS.md` §"Decisions taken at definition" — **D-8** is the one this phase was
  handed and D-07 above closes it. D-1 (the seed's self-contradiction) is Phase 177's, not this
  phase's.
- `.planning/REQUIREMENTS.md` §"Out of Scope" — dropping unsupported steps from `Plan.steps` is
  rejected milestone-wide; PRUNE-05 is the guard that keeps it rejected.

### Prior phase context that binds this one
- `.planning/phases/174-blast-radius-invariance-harness/174-CONTEXT.md` — **D-11** (a declared re-key
  lands in its own commit) explicitly binds Phases 175–181. Its "Claude's Discretion" block
  (py3.11 venv, no new library, anti-vacuity seen RED, `/usr/bin/grep`) carries forward verbatim.
  **D-03** sets the fixture-module placement precedent; **D-02** sets the "a generated-database
  redden is signal, not noise" precedent this phase's D-11 reuses.
- `.planning/MILESTONES.md` — the re-key ledger. This phase declares nothing into it; a row appearing
  from Phase 175 would itself be the defect.

### Research (measured against `firestarter_app @ 0a93999`)
- `.planning/research/SUMMARY.md` §"Phase 175: Structural sentinel over `derive_plan` (RED first)" —
  the deliverable list, the scope choice, and the instruction to copy
  `test_shipped_ops_never_reach_sdp_arm` and `test_erase_flag_invariants.py` verbatim.
- `.planning/research/PITFALLS.md` §"Pitfall 3" — the three places the "verify covers it" argument is
  under-scoped, including `write-inhibited` where the read-back **is** the oracle. This is the source
  of the SDP exemption in D-01, and of D-02's "same cycle" wording.
- `.planning/research/PITFALLS.md` §"Pitfall 4" — why a skipped diagnostic must emit a reason rather
  than an absence. Phase 177's problem, but it explains what this sentinel is licensing.

### Product code this phase reads (never modifies)
- `firestarter_app/firestarter/chip_test.py:486` — `derive_plan`, the whole subject.
- `firestarter_app/firestarter/chip_test.py:314-344` — the 13 `OP_*` constants D-01 partitions.
- `firestarter_app/firestarter/chip_test.py:1236` — `cycle_block_bounds`, D-02's block source. Its
  docstring records the four measured emission orders.
- `firestarter_app/firestarter/chip_test.py:1226-1233` — `_CYCLE_BLOCK_OPS` / `_CYCLE_BLOCK_START_OPS`.
- `firestarter_app/firestarter/chip_test.py:914-1004` — `_DESTRUCTIVE_OPS`, `_MULTI_RUN_OPS`,
  `_SDP_OPS`, `_SDP_LEG_OPS`, `_SDP_BASELINE_OPS`, `_SDP_LEG_GATED_OPS`.
- `firestarter_app/firestarter/chip_test.py:406-445` — `Step` and `Plan` dataclasses.
- `firestarter_app/firestarter/chip_test.py:1025` — `StepResult`; `_skip_result` immediately below it
  is what produces the `NA` rows D-10's execution half asserts.
- `firestarter_app/firestarter/chip_test.py:747-750` — the erase→blank-check relocation D-05 guards.
- `firestarter_app/firestarter/chip_test.py:786-845` — the SDP-leg emission: six steps, `supported`
  on ALLOW, `supported=False` on REFUSE, and nothing at all at `write_scope="none"`.
- `firestarter_app/firestarter/chip_test.py:2747` — `_resolve_write_target`, and `:2805-2821` where
  the retired full-device-if-blank branch is recorded as gone.
- `firestarter_app/firestarter/chip_test.py:2171` — `uv_slot_starts`, top-down by design.
- `firestarter_app/firestarter/cli_handlers.py:2236` — `_resolve_write_scope`, the UV ceiling D-12's
  handler leg pins.
- `firestarter_app/firestarter/cli_handlers.py:2366-2367` — the sole `derive_plan` call site on the
  `dev test` path; the source of "reachable scope" claims.

### Test idioms to copy, not reinvent
- `firestarter_app/tests/test_chip_test_sdp_leg.py:827` — `test_shipped_ops_never_reach_sdp_arm`.
  The closure sentinel D-01 and D-06 are modelled on: build the op set from `vars(chip_test)`,
  subtract the known sets, assert the remainder against a committed literal.
- `firestarter_app/tests/test_erase_flag_invariants.py` — the whole-DB sweep, the two-level
  `_all_rows` selector, and the anti-vacuity discipline. Its docstring's empty-selector warning is
  the trap D-09 exists to defeat.
- `firestarter_app/tests/test_sdp_db_invariant.py`, `firestarter_app/tests/test_page_size_invariants.py`
  — two more shipped whole-DB sweeps.
- `firestarter_app/tests/fixtures/` — ~20 `planted_*` counter-example files; the planted-mutation
  idiom is already house style here.

### The reversal this phase pins
- `firestarter_app` commit `2b42dac` — quick task `260822-aq6`, "retire the full-device UV write and
  its prompt; report rig life". The operator-agreed reversal D-12 locks in. Its predecessor
  `57c1b8f` (`260821-wna`) is the design the stale comment still describes.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`cycle_block_bounds`** (`chip_test.py:1236`) — a shipped *production* helper returning the
  half-open cycle-block range. D-02 depends on it; the test must not re-derive the block rule.
- **`vars(chip_test)` op discovery** — the exact three-line idiom at
  `tests/test_chip_test_sdp_leg.py:840-846` builds `{v for n,v in vars(chip_test).items() if
  n.startswith("OP_") and isinstance(v, str)}`. D-01's partition consumes this directly.
- **`EpromDatabase(skip_local_override=True)`** as a module-level singleton — the shipped sweep idiom
  (`test_erase_flag_invariants.py:98`). D-07 requires it.
- **`_mock_operator()`** (`tests/test_chip_test_sdp_leg.py`) — an existing operator double that
  `run_plan` accepts with no hardware. D-10's execution half needs exactly this.
- **`_plan_with_steps(...)`** (same module) — builds a `Plan` from bare `Step`s. D-09's hand-built
  counter-plan should use it rather than a fresh helper.

### Established Patterns
- **Whole-database sweeps** ship three times already. Copy, do not invent.
- **Element-wise committed comparison** is the house idiom for "pin a list" — used by the
  constants-parity tests and by Phase 174's D-07/D-10. D-10's frozen half uses it.
- **Anti-vacuity legs with a planted counter-example** are how this repo proves a gate is not
  tautological, and the repo carries a live counter-example of the failure mode
  (`MAX_27C020_SIZE`).
- **The op vocabulary is plain `str`, not an `Enum`** — so exhaustiveness cannot be checked
  statically. Every closure guard in this module is a runtime set-difference sentinel.

### Integration Points
- The sentinel reads `chip_test` only; it adds no production symbol and no import into product code.
- **Phase 177 consumes this phase as a licence.** Its plan should be able to cite the write→verify
  leg by name — which is why D-05 keeps the erase leg separate rather than folding both into one
  predicate.
- The `run_plan` half (D-10) touches the dispatch layer through a mock, so a Phase 177 or 178 change
  to `_dispatch_step` can redden it. That is intended coupling, not accidental.

### Measured at discussion time (devcontainer py3.12 — re-take in the py3.11 CI replica)
- 746 database rows → **1,492 plans** at `full` + `partial`, swept through `derive_plan` in
  **1.18 s**.
- **17,904** total steps across those plans, of which **10,190** are `supported=False`.
- Only **4 distinct op-sequences** exist across the entire database — the frozen pin in D-10 needs
  4 sequences plus a chip-count mapping, not 746 rows.
- A `run_plan` sweep with `_mock_operator()` extrapolates to **~21 s** for all 1,492 plans; 50 of 50
  sampled plans had `len(results) == len(plan.steps)`.
- Both repos are on `gsd/v1.36-dev-test-fidelity` with clean working trees at discussion time.

</code_context>

<specifics>
## Specific Ideas

- **"The exemption bucket is where the thinking is."** The predicate itself is three lines; the
  reason each of the ten non-write ops does not need a verify is the actual deliverable, and D-01
  forces every one of them to be written down.
- **The operator's UV rule was the *reverted* design, and the code proved it.** What surfaced the
  reversal was a direct contradiction inside one file: `_resolve_write_scope` says "there is no
  prompt on any path" thirty lines above a design-history comment saying "a UV-erasable EPROM is
  asked first". Reading the commit that removed the prompt settled it in one step.
- **The handler leg is the one that matters.** Pinning `derive_plan`'s UV region policy is easy and
  stays true even if `_resolve_write_scope` is changed to return `"full"` for UV tomorrow. Only the
  handler-level assertion actually guards the ceiling.
- **An alignment-only no-drop proof is the trap.** `len(results) == len(plan.steps)` reads like the
  requirement and cannot catch the change the requirement forbids, because a prune shrinks both sides
  together. This is worth stating in the test's own docstring so nobody later "simplifies" the frozen
  half away.

</specifics>

<deferred>
## Deferred Ideas

- **Stale design-history comment at `firestarter_app/firestarter/cli_handlers.py:2295-2305`** — it
  still describes `260821-wna`'s reverted UV prompt in the present tense ("A UV-erasable EPROM is
  asked first… yes permits the whole device to be written IF the chip reads blank"), contradicting
  `_resolve_write_scope` thirty lines above it. **File as a defect todo.** It also falls under the
  standing no-comments-in-source rule and under the pending
  `2026-08-27-strip-gsd-provenance-comments-from-source.md` sweep. Not fixed here — this phase
  touches no product file.
- **Re-reversing `aq6`** (full-device UV write on a blank part, behind a prompt) — explicitly
  declined by the operator this discussion. If ever revisited it is a behaviour change for
  **Phase 179**, and Phase 174's ledger already carries a seeded UV `run_count` re-key row it would
  have to be measured against.
- **A sentinel over `Plan.locked_destructive`** — declined; the field is proposed for deletion in
  Phase 181.
- **Whether the ~21 s `run_plan` sweep runs on every push** against a 737 s suite, or is marked
  slow — raised, set aside as a planner call. Phase 174 set the same question aside for its own
  sweep; the two should be answered together.
- **The fault-mode table** (rows = the four `classify_fingerprint` buckets plus "false PASS via
  undriven bus"; columns = caught by verify / read-back / blank-check) — PITFALLS suggests Phase 175,
  the roadmap assigns it to **Phase 177** as a named deliverable. Roadmap wins.
- **`--fast` (`runs=1`) coverage** — PITFALLS Pitfall 3 wants the structural test to cover `--fast`
  plans. It structurally cannot: `derive_plan`'s signature takes only `write_scope`, and `--fast`
  changes `runs` at execution time, not plan shape. Belongs with Phase 177's run-time evidence
  ledger. Recorded so nobody plans it here and finds it impossible.

### Reviewed Todos (not folded)

- **`2026-08-30-gate-fingerprint-readback-on-step-failure.md`** — already tagged `resolves_phase: 177`.
  It is the change this phase licenses; reviewed for that reason, not folded.
- **`build-db-diff-ladder-state-community-reported-regression.md`** — Phase 177's, via D-4/D-6.
- **`delete-banner-locked-steps-dead-field.md`** — tagged `resolves_phase: 181`. Directly relevant:
  it is why D-06's discretion block declines to build a sentinel over `Plan.locked_destructive`.
- **`2026-08-31-dev-test-chip-name-must-match-database.md`** — tagged `resolves_phase: 181`.
- **`2026-08-27-strip-gsd-provenance-comments-from-source.md`** — milestone-wide hygiene; the new
  stale-comment defect above should be filed alongside it, not merged into it.
- The remaining 31 keyword matches (firmware safe-state, VPP checks, JP4 labels, avrdude fallback,
  pinout corroboration, COBS deadlines, etc.) are unrelated to a test-only sentinel phase and were
  not considered further.

</deferred>

---

*Phase: 175-structural-sentinel-over-derive-plan*
*Context gathered: 2026-09-04*
