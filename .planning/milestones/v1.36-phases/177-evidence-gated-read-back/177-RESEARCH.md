# Phase 177: Evidence-Gated Read-Back - Research

**Researched:** 2026-09-05
**Domain:** Python host engine change in `firestarter_app/firestarter/chip_test.py` (the `dev test` plan-execution engine) + one `.planning/seeds/` documentation amendment
**Confidence:** HIGH on the code inventory and the measured hash blast radius (every figure recomputed this session in the py3.11 CI-replica venv); MEDIUM on the PRUNE-04 scope adjudication, which needs an operator decision.

---

## Summary

Phase 177 is a **six-line-of-logic change with a very large evidence surface**. The mechanical change is small: gate the fingerprint read-back at `chip_test.py:3100` on a predicate that consults *all* cycles, synthesize a `match`-classified `Fingerprint` on the cheap path instead of leaving the field `None`, and amend one paragraph of a seed file. The work is in the blast radius: the fingerprint classification string is an input to `dedup_fingerprint`, so this phase re-keys report identities that community issues have already been filed under, and Phase 174 built the machinery that turns that from an accident into a declared decision.

The three most consequential findings, all measured this session:

1. **The Phase 174 ledger's projected `after_hash` for this phase's own row is stale.** `RK-174-01-p177-readback-gating` projects `sst27sf512-six-step` moving `4dc282a5d596 → 60a031573aab`, and Phase 174 froze a companion shape `sst27sf512-six-step-readback-gated` at that value. That projection models the **naive** R2 reading — the fingerprint is *dropped*, so `cls` becomes empty. PRUNE-03 forbids that: the fingerprint is *synthesized* and classified `match`. The measured post-PRUNE-03 value for that shape is **`7fb88e0b07d6`**, not `60a031573aab`. A plan that reuses the projected number will land on the wrong value and the phase will look like it did something it did not.

2. **PRUNE-03 moves two frozen shapes that Phase 177 does not own a ledger row for, and one of them is the shape Phase 178 must prove it did *not* re-key.** Measured: `sst27sf512-full-all-ok` `4b3e52cab987 → 14d306256076` (owned by `RK-174-06-p178-status-axis-must-not-rekey`, whose entire purpose is to assert *no* re-key) and `w27e257-full-all-ok` `22908e2954c3 → 3a9f95aba65e` (no ledger row at all). Both carry a passing write/verify with **no fingerprint today**, and PRUNE-03 gives them one. This phase must append ledger rows for these, or Phase 178's oracle is already broken before Phase 178 starts.

3. **PRUNE-04's population inside the `dev test` engine is empty once D-1's exclusion is honoured.** `chip_test.py` has exactly two `operator.read_eprom` call sites; neither is a whole-device read compared against a held buffer that is not already excluded by D-1 (the fingerprint) or by the seed's own SDP carve-out (the read-back *is* the verdict). The one genuine site in the whole app is `eprom_operations.write_cycle_eprom` — which is not the `dev test` engine, and whose read-back is itself a read-repeatability diagnostic, so converting it to a verify would repeat exactly the mistake D-1 exists to prevent. **Criterion 4 needs an operator decision before it can be planned.**

**Primary recommendation:** Plan this phase as four sequenced units — (a) the cross-cycle gate + synthesized `match` fingerprint as one behaviour commit that is *expected* to redden the Phase 174 gate; (b) a separate declaration commit per the D-11 protocol filling `after_hash` in `tests/fixtures/rekey_ledger.py` and the matching `.planning/MILESTONES.md` row; (c) the seed amendment (PRUNE-07), which touches no code; (d) a `checkpoint:decision` on PRUNE-04's scope, opened **first**, because a vacuous or an over-broad reading both produce a wrong plan.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Deciding *whether* the fingerprint read-back runs | Host engine (`chip_test.py`, `_dispatch_multi_run` / `_run_cycle_block`) | — | The outcome evidence that licenses skipping it exists only in the engine's cycle loop. No firmware or transport tier sees "did any cycle fail". |
| Producing the mismatch distribution | Host engine (`classify_fingerprint`) | Device (`read_eprom`) | The classifier needs the whole byte-diff distribution; only a real read-back supplies it. `[CITED: .planning/notes/dev-test-sequence-cost-model.md:75-76]` |
| Deciding pass/fail on a write | Firmware (`memory_verify_execute`) via `operator.verify_eprom` | — | The firmware compares in place and early-returns on the first mismatch. `[VERIFIED: firestarter/src/proms/memory.cpp:377-396]` |
| Classifying a bit-perfect compare | Host engine (`classify_fingerprint` / synthesized path) | — | Free — no device I/O. This is the D-4/D-6 split: "the read-back is what costs; the classification is free." |
| Report identity (`dedup_fingerprint`) | Host report layer (`diagnostic_report.py:248-302`) | — | Reads `result.fingerprint.classification`; the engine never re-hashes. |
| Recording a deliberate re-key | Meta repo (`.planning/MILESTONES.md`) + app repo (`tests/fixtures/rekey_ledger.py`) | Meta checker `tools/rekey/check_rekey_ledger.py` | The ledger is machine-authoritative; MILESTONES.md narrates it. Bound in both directions. |

---

## User Constraints (from REQUIREMENTS.md — no CONTEXT.md exists yet)

`/workspaces/.planning/phases/177-evidence-gated-read-back/` is empty; there is **no `177-CONTEXT.md`**. The binding decisions are the milestone-level ones taken at definition, quoted verbatim:

### Locked Decisions

> **D-1** — The seed's R1 sentence — *"this applies to the fingerprint read-backs"* — is **amended**. Read literally it converts the diagnostic into an oracle and destroys the mismatch distribution `classify_fingerprint` exists to compute. A rule that contradicts itself in the artifact a planner reads is a defect in the artifact. Owned by RPT/PRUNE phase that touches the seed.

> **D-4 + D-6** — `classify_fingerprint` gains a **`match` bucket** for `bad == 0`, emitted on the cheap path; `build_db_diff` stops forcing `_LADDER_NONE` on it, so an **all-OK run becomes promotable to `community-reported`**. Removes the `indeterminate`-on-a-bit-perfect-compare absurdity. **Re-keys dedup history once, deliberately** — declared and dated in `MILESTONES.md`, and stated publicly because it changes what a report implies to the triage skill and to every human reader.

> **PRUNE-01**: A passing run performs **zero** fingerprint read-backs.
>
> **PRUNE-02**: The read-back gate consults the step's outcomes **across all cycles**, not the final cycle alone. A cycle-1-fail / cycle-2-pass run keeps its fingerprint. (`not all(outcomes)` at `chip_test.py:3100` is insufficient at HEAD — under the cycle block `outcomes` is a one-element list for the final cycle only.)
>
> **PRUNE-03**: A passing write/verify still reports a fingerprint, **synthesized** from what the operation already established (`bad=0`, `total=region_length`, `ff_ratio: None`) and classified `match` per D-4/D-6. The read-back is what costs; the classification is free.
>
> **PRUNE-04**: Where the engine reads a whole device back only to compare it against a buffer it already holds, it uses the on-device verify instead. **The fingerprint read-back is explicitly excluded from this rule** (D-1).
>
> **PRUNE-07**: The seed `.planning/seeds/dev-test-adaptive-sequencing.md` is amended so R1 no longer instructs a planner to destroy the diagnostic R2 preserves (D-1).

Also binding from Phase 174's own decisions, quoted from `.planning/MILESTONES.md:41`:

> Every row above is a commitment, not a suggestion, and the rule for taking one is fixed: first, a behaviour change lands on its own and turns the frozen gate for that row's `shape_id` RED; second, a separate commit touching only that row's `after_hash` in `firestarter_app/tests/fixtures/rekey_ledger.py` and this table's matching row makes the gate green again, so the re-key is a reviewable unit and an executor cannot reflexively repair the test inside the same commit that changed the behaviour; third, the `before` cell is never overwritten.

### Claude's Discretion

- The exact mechanism by which "did any cycle fail" reaches `_dispatch_multi_run` (a new keyword parameter vs. an evidence ledger field on `WriteContext`). The milestone research recommended the latter; the requirement does not mandate either. `[CITED: .planning/research/SUMMARY.md:127]`
- Whether the `match` bucket is an early-return inside `classify_fingerprint`, a separate synthesizing constructor, or both. PRUNE-03's stated `ff_ratio: None` **forces** a separate constructor for the cheap path (see Pitfall 2).
- The precise seed-amendment wording, subject to criterion 5.

### Deferred Ideas (OUT OF SCOPE)

- **PRUNE-08 / seed R3** (bit-structured sampling) — Phase 180.
- **Seed R4** (session reuse) — deferred to the Future Requirements section; `R4-02` (folding the VPP/VPE sampler reads) is explicitly out of scope in a host-only milestone.
- **The `fingerprint_source` disclosure key** proposed by the milestone research `[CITED: .planning/research/SUMMARY.md:91,127]` — it is **not** in PRUNE-01..04/07 and PRUNE-03 solves the same "three meanings of `null`" problem differently (by never emitting `null` on a pass). Adding it here is scope creep; RPT-A2 in Phase 181 owns the `steps[].fingerprint` field expansion.
- **The "declared-oracle field on `Step` + closed vocabulary + fail-closed dispatch arm"** also proposed by the research for this phase `[CITED: .planning/research/SUMMARY.md:127]` — no requirement ID covers it. Flag to the planner: the roadmap's success criteria and the five requirement IDs are the contract, not the research's delivery list.

---

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PRUNE-01 | A passing run performs **zero** fingerprint read-backs | §"The gate site" gives the exact line and predicate; §"Counting read-backs in a test" gives two proven counting seams and names the existing analog test that must be inverted |
| PRUNE-02 | Gate consults outcomes **across all cycles** | §"Where cross-cycle outcomes live" names `per_step` (`chip_test.py:1514`) and `_run_cycle_block`'s loop, and shows why `outcomes` is length-1 under the cycle block |
| PRUNE-03 | Passing write/verify still reports a **synthesized** `match` fingerprint | §"The Fingerprint data structure" quotes the dataclass and the classifier's four buckets verbatim; §"Measured blast radius" gives the exact re-keys this produces |
| PRUNE-04 | Whole-device read-back-to-compare replaced by on-device verify, **fingerprint excluded** | §"PRUNE-04 call-site inventory" — exhaustive, with the search method stated; concludes the engine population is empty and raises Open Question 1 |
| PRUNE-07 | Seed R1 amended | §"The seed's self-contradiction" quotes R1 and R2 verbatim and proposes minimal amendment wording |

---

## Standard Stack

**Add nothing.** This phase is stdlib + the existing test surface. The milestone already adjudicated the stack question and declined all three candidate additions on merit `[CITED: .planning/research/SUMMARY.md:44-52]`; HYG-02 forbids a new runtime dependency.

### Core (all already installed; versions verified in the CI-replica venv this session)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| CPython | 3.11.16 | The only honest measurement environment | `[VERIFIED: ./.venv311/bin/python --version → "3.11.16 (main, Aug 25 2026, 14:00:53) [Clang 22.1.3]"]`. The devcontainer default is 3.12 and is **proven** in this project to hide breakage that reddens beta CI. |
| pytest | (installed in `.venv311`) | Whole-DB sweep + parametrized frozen tables | The idiom already ships three times in `tests/` |
| stdlib `hashlib` / `dataclasses` / `tempfile` | — | `dedup_fingerprint`, `Fingerprint`, `_read_region` | Already the only dependencies of the touched code |

**Installation:** none. `pip install -e '.[test]'` inside `firestarter_app/.venv311` is the existing dev setup.

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Hand-computing the projected hashes | Let the test suite report the diff and transcribe it | Both work; the numbers in this document were computed by *building the real shapes and calling the real `dedup_fingerprint`*, so they are reproducible — but they are still **projections of an unimplemented change** and must be re-measured after the code lands, never transcribed as targets. |

## Package Legitimacy Audit

**Not applicable — this phase installs no external packages.** `HYG-02` forbids adding a runtime dependency, and no new test dependency is needed. Zero packages to audit.

---

## Architecture Patterns

### System Architecture Diagram

```
`dev test <chip>`  (cli_handlers.dev_test)
        │
        ├─ derive_plan(chip, db, write_scope)  ──►  Plan(steps=[Step,…], is_uv)
        │
        ▼
   run_plan(plan, operator, db, runs=N)                       chip_test.py:1582
        │
        ├─ id step ─────────────► _dispatch_id ──► operator.check_eprom_id
        │        └─ mismatch closes `destructive_gate`
        │
        ├─ read step ───────────► _dispatch_read (2626) ──► operator.read_eprom ×N
        │                                └─ run1-vs-run2 divergence only
        │
        ├─ WRITE-SHAPED BLOCK ──► _run_cycle_block(cycles=N)           :1475
        │      │
        │      │  per_step: list[list[StepResult]]   ◄── THE CROSS-CYCLE LEDGER
        │      │
        │      └─ for cycle in range(cycles):        final = (cycle == cycles-1)
        │             for each live step:
        │                 _run_step(..., runs=1, collect_fingerprint=final)
        │                        │
        │                        ▼
        │                  _dispatch_multi_run                          :2922
        │                        │
        │                        ├─ resolve target (_resolve_write_target)
        │                        │     └─ uv-slot policy only: _read_region probe :2843
        │                        ├─ for _ in range(runs):
        │                        │      operator.write_eprom / verify_eprom / erase_eprom
        │                        │      └── outcomes.append(bool)   ← LENGTH == runs == 1
        │                        │                                     under the cycle block
        │                        └─ ★ GATE :3100
        │                              `if collect_fingerprint and op in (W,WP,V):`
        │                                   actual = _read_region(...)          :3108
        │                                   fingerprint = classify_fingerprint(...)
        │             └─ per_step[i].append(result)
        │      └─ _aggregate_cycle_results(per_step[i], op)             :1280
        │             └─ fingerprint = LAST cycle that produced one
        │
        └─ SDP leg ─────────────► _dispatch_sdp_leg
                                       └─ _read_region :3338  ← read-back IS the verdict

   results ──► DiagnosticReport ──► dedup_fingerprint()      diagnostic_report.py:248
                        │                 └─ parts.append(f"{op}={verdict}:{cls}")   :276
                        └─ build_db_diff()                   diagnostic_report.py:349
                                  └─ has_indeterminate_fingerprint → _LADDER_NONE     :366-376
```

### The gate site (PRUNE-01)

`chip_test.py:3100` at HEAD is **exactly** the line the requirement and the seed cite — the anchor has not drifted:

```python
        if collect_fingerprint and op in (OP_WRITE, OP_WRITE_PARTIAL, OP_VERIFY):
```
`[VERIFIED: firestarter_app/firestarter/chip_test.py:3100]`

The body it guards, verbatim:

```python
            actual = _read_region(
                operator, name, eprom_data, region_start, region_length
            )

            if actual:
                diverged = len(set(outcomes)) != 1 if outcomes else False
                fingerprint = classify_fingerprint(
                    expected,
                    actual,
                    repeat_divergent=diverged,
                    addr_base=region_start,
                )
```
`[VERIFIED: firestarter_app/firestarter/chip_test.py:3108-3117]`

`collect_fingerprint` is a keyword-only `bool = True` parameter threaded through four functions, in this order: `_run_step` (`:2349`, `:2358`) → `_run_step_untimed` (`:2394`, `:2403`) → `_dispatch_step` (`:2493`, `:2502`) → `_dispatch_multi_run` (`:2922`, `:2932`). `[VERIFIED: firestarter_app/firestarter/chip_test.py — grep of `collect_fingerprint` returns exactly lines 1499, 1549, 2358, 2387, 2403, 2439, 2502, 2562, 2932, 3100]`

### Where cross-cycle outcomes live (PRUNE-02)

Two distinct structures, and confusing them is the whole failure mode PRUNE-02 names:

**`outcomes`** — a local `list[bool]` inside one `_dispatch_multi_run` call, appended once per `runs` iteration:

```python
    outcomes: list[bool] = []
```
`[VERIFIED: firestarter_app/firestarter/chip_test.py:2993]` — appended at `:3069` (write), `:3079` (verify), `:3088` (erase).

`_run_cycle_block` calls `_run_step(..., runs=1, ...)`:

```python
                result = _run_step(
                    name,
                    step,
                    operator,
                    db,
                    runs=1,
                    sampler=sampler,
                    write_context=write_context,
                    collect_fingerprint=final,
                )
```
`[VERIFIED: firestarter_app/firestarter/chip_test.py:1541-1550]`

**`runs=1` is why `outcomes` is a one-element list.** On the final cycle, `not all(outcomes)` therefore asks *only* "did the final cycle fail" — exactly the insufficiency PRUNE-02 records.

**`per_step`** — the cross-cycle ledger, one list of `StepResult` per plan step:

```python
    per_step: list[list[StepResult]] = [[] if r is None else [r] for r in pre]
```
`[VERIFIED: firestarter_app/firestarter/chip_test.py:1514]`, appended at `:1551` (`per_step[i].append(result)`) inside the cycle loop, and folded at `:1577-1579`:

```python
    return [
        _aggregate_cycle_results(per_step[i], steps[i].op) for i in range(len(steps))
    ]
```
`[VERIFIED: firestarter_app/firestarter/chip_test.py:1577-1579]`

**At the moment the final cycle's `_run_step` is invoked, `per_step[i]` already holds cycles 1..N-1's results.** A correct "did ANY cycle fail" predicate is therefore computable at `chip_test.py:1541`, immediately before the call, and must be passed *down*. The final cycle's own outcome is only knowable inside `_dispatch_multi_run`, so the complete predicate is necessarily a disjunction:

```
collect_fingerprint AND ( prior_cycles_failed  OR  not all(outcomes) )
```

Two implementation routes, both acceptable:

- **(A) A new keyword-only parameter** (`prior_failed: bool = False`) threaded down the same four-function chain `collect_fingerprint` already uses. Smallest diff; mirrors an idiom that already exists; the type is trivially checkable.
- **(B) A run-level evidence ledger field on `WriteContext`** (`chip_test.py:1132-1168`) — the milestone research's recommendation `[CITED: .planning/research/SUMMARY.md:127]`. `WriteContext` is already threaded to `_dispatch_multi_run` and already carries cycle state (`cycle_targets`, `cycle_index`). Costs no new parameter but adds mutable run-level state that `_dispatch_multi_run` currently only *reads*.

`_RAN_VERDICTS = frozenset({VERDICT_OK, VERDICT_BAD, VERDICT_MARGINAL})` `[VERIFIED: firestarter_app/firestarter/chip_test.py:3495]`.

**`_RAN_VERDICTS` is the right membership set** for "this cycle actually reached the operator" — `_aggregate_cycle_results` uses it for exactly this discrimination (`ran = [r for r in results if r.verdict in _RAN_VERDICTS]`, `[VERIFIED: firestarter_app/firestarter/chip_test.py:1306]`). A SKIPPED/NA prior cycle is not a failure.

### The `Fingerprint` data structure (PRUNE-03)

```python
@dataclass
class Fingerprint:
    """Verdict + raw evidence for a single expected-vs-actual byte compare."""

    total: int
    bad: int
    bad_pct: float
    classification: str
    evidence: dict = field(default_factory=dict)
```
`[VERIFIED: firestarter_app/firestarter/chip_test.py:151-159]`

The four existing classification literals, verbatim:

```python
FP_BLANK_CONTACT = "blank/contact"
FP_ADDRESS_LINE = "address-line"
FP_TRANSPORT = "transport"
FP_INDETERMINATE = "indeterminate"
```
`[VERIFIED: firestarter_app/firestarter/chip_test.py:138-141]`

**There is no `match` value today.** D-4/D-6 introduce it; the requirement spells it lowercase `match`, and `build_db_diff` compares against the *literal string* `"indeterminate"` rather than the constant (`r.fingerprint.classification == "indeterminate"`, `[VERIFIED: firestarter_app/firestarter/diagnostic_report.py:367]`) — so a new bucket needs no `build_db_diff` edit to unblock the ladder. **D-6's "`build_db_diff` stops forcing `_LADDER_NONE`" happens for free.** Verified by execution: mutating an all-OK AT28C256 report's `indeterminate` fingerprints to `match` yields

```
DbDiff(current_support_status='supported',
       proposed_disposition='suggests: candidate for community-reported (advisory)',
       ladder_state='community-reported')
```
`[VERIFIED: executed this session — `build_db_diff('at28c256', EpromDatabase(skip_local_override=True), mutated_results)` in `.venv311`]`

**Does the existing classifier already yield `match` for a bit-perfect compare? No — it yields `indeterminate`, and it must be routed around, not merely extended.** Classification order is locked and the *first* test is `ff_ratio >= 0.98`:

```python
    if ff_ratio >= _FF_RATIO_THRESHOLD:
        return Fingerprint(
            total=cmp_len,
            bad=bad,
            bad_pct=bad_pct,
            classification=FP_BLANK_CONTACT,
            evidence=evidence,
        )
```
`[VERIFIED: firestarter_app/firestarter/chip_test.py:200-207]`, with `_FF_RATIO_THRESHOLD = 0.98` `[VERIFIED: firestarter_app/firestarter/chip_test.py:146]`. Its own comment states the deliberate ordering: *"Checked first regardless of whether there are zero mismatches (a perfect verify) or the pattern never matched at all."* `[VERIFIED: firestarter_app/firestarter/chip_test.py:197-199]`

With `bad == 0` and a non-0xFF-dominated region, the address-line branch is skipped (`if bad and cmp_len > (1 << 8)`, `:218`), `repeat_divergent` is not `True`, and control falls to the terminal `return Fingerprint(..., classification=FP_INDETERMINATE, ...)` at `:254-260`. **That is the D-4 absurdity, confirmed by reading the code path.**

`ff_ratio` is computed as a float and can never be `None`:

```python
    ff_ratio = (ff_count / cmp_len) if cmp_len else 0.0
```
`[VERIFIED: firestarter_app/firestarter/chip_test.py:188]`

**Therefore PRUNE-03's literal `ff_ratio: None` is unreachable through `classify_fingerprint` and requires a separate synthesizing constructor** on the cheap path — a `Fingerprint(total=region_length, bad=0, bad_pct=0.0, classification=FP_MATCH, evidence={"ff_ratio": None, ...})` built without touching the device. This is the honest form: `ff_ratio` was not *measured*, and `0.0` would be a fabricated measurement.

Whether `classify_fingerprint` *also* gains a `bad == 0 → match` early-return (for the read-back path, which still runs on failing steps and on the SDP leg) is a **decision with hash consequences** — see Open Question 2.

### What actually reaches the report

```python
            "fingerprint": (
                result.fingerprint.classification if result.fingerprint else None
            ),
```
`[VERIFIED: firestarter_app/firestarter/diagnostic_report.py:795-797]`

Only the classification **string** is exported; `total`/`bad`/`bad_pct`/`evidence` do not reach `to_dict()` until RPT-A2 (Phase 181). So roadmap criterion 3 ("still yields a fingerprint in the report … classified as a match") is satisfied by the string `"match"` appearing where `"indeterminate"` or `null` stood.

### Where the hash reads it

```python
    for result in report.results:
        cls = result.fingerprint.classification if result.fingerprint else ""
        parts.append(f"{result.op}={result.verdict}:{cls}")
```
`[VERIFIED: firestarter_app/firestarter/diagnostic_report.py:274-276]`

This single line is the entire re-key mechanism: `write=OK:indeterminate` → `write=OK:match`, and `write=OK:` → `write=OK:match` where no fingerprint existed.

### Anti-Patterns to Avoid

- **Reusing the ledger's projected `60a031573aab`.** It models the destructive R2 reading. See Finding 1.
- **Writing `#` comments into the source.** Project hard rule, see Project Constraints. The project's own established practice for recording rationale in this module is a **docstring** (Phase 176-02 recorded MEAS-02's basis and MEAS-03's three reasons in docstrings pinned by tests). `_dispatch_multi_run`'s existing docstring is the correct home for the gate's rationale.
- **Gating on the *plan's* overall outcome rather than the *step's*.** PRUNE-02 says "the step's outcomes"; a BAD `blank-check` must not force a read-back on an unrelated passing `write`.
- **Emitting the synthesized fingerprint on non-final cycles.** `_aggregate_cycle_results` takes `next((r.fingerprint for r in reversed(ran) if r.fingerprint), None)` `[VERIFIED: firestarter_app/firestarter/chip_test.py:1328]` so it would be harmless, but it makes the "one fingerprint describes the device's final state" invariant untrue by construction. Emit only when `collect_fingerprint` is True.
- **Repairing the reddened frozen-hash test in the same commit as the behaviour change.** Explicitly forbidden by the declared-re-key protocol `[VERIFIED: .planning/MILESTONES.md:41]`.

---

## PRUNE-04 call-site inventory

**How I searched** (so coverage is judgeable, not asserted):

1. `/usr/bin/grep -rn "read_eprom(" --include=*.py firestarter/` — every read entry point in the package (4 hits + 2 defs).
2. `/usr/bin/grep -n "operator\.[a-z_]*(" firestarter/chip_test.py` piped through `sort|uniq` — the complete set of operator calls the engine makes (14 sites, 8 distinct methods).
3. `/usr/bin/grep -n "sha256\|!= source\|== source"` across `eprom_operations.py`, `cli_handlers.py`, `chip_test.py` — every host-side content comparison.
4. `/usr/bin/grep -rn "read.back\|read-back\|readback" --include=*.py firestarter/` — prose/name evidence of a read-back concept.

(`/usr/bin/grep` deliberately, not the devcontainer's PATH `grep`, which is ugrep and honors `.gitignore`.)

**Result — `chip_test.py` has exactly two `operator.read_eprom` call sites: `:2642` and `:2728`.** `[VERIFIED: firestarter_app/firestarter/chip_test.py — the sorted operator-call census returns `2642 operator.read_eprom` and `2728 operator.read_eprom` and no others]`

| # | Site | What it reads | What it compares against | Disposition |
|---|------|---------------|--------------------------|-------------|
| 1 | `chip_test.py:3108` (`_read_region` inside `_dispatch_multi_run`) | the **write region**, not the whole device (region-scoped since quick task 260821-wna) | `expected` — the pattern buffer already in memory | **EXCLUDED by D-1.** This is the fingerprint diagnostic. Stays a read-back by design; Phase 177 gates *when* it runs, not *what* it is. |
| 2 | `chip_test.py:3338` (`_read_region` inside `_dispatch_sdp_leg`) | the SDP leg's fixed region | `expected_readback` (pattern A) | **EXCLUDED by the seed's own R1 carve-out** — *"it does **not** apply to the SDP leg, whose `_read_region` read-back *is* the verdict and must stay a real read."* The source says the same: *"this read-back is NOT best-effort decoration -- it IS the verdict."* `[VERIFIED: firestarter_app/firestarter/chip_test.py:3325-3338]` |
| 3 | `chip_test.py:2843` (`_read_region` inside `_resolve_write_target`) | a `_UV_PROBE_BLOCK_LENGTH` block, **uv-slot policy only** | nothing — it *is* the state lookup that computes the mask | **NOT APPLICABLE.** No buffer is held to compare against; the read produces the `current` content. Also unreachable on non-UV plans: `if region_policy != REGION_POLICY_UV_SLOT:` returns an unmasked target before any read `[VERIFIED: firestarter_app/firestarter/chip_test.py:2781-2799]`. |
| 4 | `chip_test.py:2642` (`_dispatch_read`) | the whole device, `runs` times | run *N* against run *N-1* — read-vs-read, no held buffer | **NOT APPLICABLE.** A verify cannot substitute: the metric is read repeatability, which verify cannot measure. (This is PRUNE-08 / seed R3's territory, Phase 180.) |
| 5 | `eprom_operations.py:1079` (`consistency_check_eprom`) | whole device × N | read-vs-read SHA | **NOT APPLICABLE**, same reason as #4. |
| 6 | `eprom_operations.py:1195-1250` (`write_cycle_eprom` read block) | **the whole device** | `source_sha` — the SHA of the source image the method already holds (`:1171`, `:1246-1247`) | **THE ONLY GENUINE MATCH IN THE APP.** See Open Question 1. |
| 7 | `cli_handlers.py:508` (`read` command), `eprom_operations.py:1829` (`dev_read_eprom`, hexdump) | whole device / a window | nothing | **NOT APPLICABLE** — no comparison at all. |
| 8 | `firmware.py:653-667`, `py32_dfu.py:_verify_readback` | DFU flash upload | the firmware payload | **OUT OF SCOPE** — the DFU bus, not the EPROM bus; not "the engine". |

**The on-device verify API, named precisely:** `EpromOperator.verify_eprom(eprom_name, eprom_data_dict, input_file_path, operation_flags=0, address_str=None) -> bool` `[VERIFIED: firestarter_app/firestarter/eprom_operations.py:2094-2101]`. It issues `COMMAND_VERIFY` and streams host→device via `_main_phase_send_data`; the firmware compares in place and early-returns on the first mismatch `[VERIFIED: firestarter/src/proms/memory.cpp:377-396 — `memory_verify_execute` loops `handle->data_size`, and on `byte != expected` emits `LOG_ERROR_ID_BYTES(MSG_ERR_VERIFY, _b, 5)` with expected/actual/3-byte address then `return`s]`.

**Conclusion, stated plainly so the planner does not have to infer it:** after D-1's exclusion and the seed's SDP carve-out, **the `dev test` engine has zero remaining PRUNE-04 sites.** Roadmap criterion 4 as written ("is replaced by the existing on-device verify, reducing that call site's full-device read count to zero") presupposes at least one. This must be adjudicated before planning — Open Question 1.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Comparing a buffer against the device | A host-side read + `==` | `operator.verify_eprom` (`eprom_operations.py:2094`) | Firmware-side compare, same byte coverage, early-return on first mismatch |
| Region-scoped read-back | A second `read_eprom` + slice | `chip_test._read_region` (`:2710`) — *"the ONE place this slice lives; every region read-back in this module goes through this function"* `[VERIFIED: firestarter_app/firestarter/chip_test.py:2713-2714]` | A region read produces a **hole-padded** file whose real bytes sit at absolute offset `start`; slicing from 0 silently reads zero padding |
| Byte-diff math | A new diff loop | `chip_test._diff_offsets` (`:125-129`) | Already shared by `classify_fingerprint` and `consistency_check_eprom` |
| Freezing a report hash | A hand-typed literal | `tests/fixtures/report_shapes.py` builder + `FROZEN_HASHES` + `tools/snapshot_report_shapes.py` | Phase 174 built exactly this; MILESTONES.md records that *no* inherited hash is frozen anywhere — every value is builder-produced |
| Declaring a re-key | Editing the frozen hash | `tests/fixtures/rekey_ledger.py` `after_hash` + the `.planning/MILESTONES.md` row, in a **separate commit** | `tools/rekey/check_rekey_ledger.py` binds the two trees in both directions and rejects an orphan on either side |

**Key insight:** every "obvious" implementation shortcut in this phase has already been built as a shared primitive by an earlier phase, and the checkers that enforce their use fail *loudly*. The risk here is not reinvention — it is under-declaring the blast radius.

---

## Measured blast radius (the number the planner most needs)

All values below were produced this session by building the **real** frozen shapes via `tests/fixtures/report_shapes.build_shape` and calling the **real** `firestarter.diagnostic_report.dedup_fingerprint` in `firestarter_app/.venv311` (Python 3.11.16). The "after" column applies the PRUNE-03 rule *by mutation of the built report* — it is a **projection of an unimplemented change**, and every value must be re-measured once the code lands.

Baseline reproduction check first: `sst27sf512-six-step → 4dc282a5d596` and `sst27sf512-six-step-readback-gated → 60a031573aab`, both matching `FROZEN_HASHES`. `[VERIFIED: executed this session]`

| shape_id | frozen (before) | projected (after PRUNE-03) | moves? | ledger row |
|---|---|---|---|---|
| `at28c256-full-all-ok-sdp` | `52fb759dc48c` | **`050ad3830704`** | MOVED | `RK-174-05-p177-match-bucket-d4d6` ✔ owned |
| `sst27sf512-six-step` | `4dc282a5d596` | **`7fb88e0b07d6`** | MOVED (hand-specified — moves only when its `step_specs` are edited) | `RK-174-01-p177-readback-gating` ✔ owned, **but its projected `60a031573aab` is wrong** |
| `sst27sf512-six-step-readback-gated` | `60a031573aab` | `7fb88e0b07d6` | MOVED | **no row** — this shape *is* the stale projection |
| `sst27sf512-full-all-ok` | `4b3e52cab987` | **`14d306256076`** | MOVED | `RK-174-06-p178-status-axis-must-not-rekey` — **collision, see Finding 2** |
| `w27e257-full-all-ok` | `22908e2954c3` | **`3a9f95aba65e`** | MOVED | **no row** |
| `gh47-sst27sf512-pass` | `f9dbc31dcd27` | **`1f812aae49ca`** | MOVED | **no row** — and this is a *filed community hash* |
| `m27c512-full-all-ok` / `-blank-check-bad` / `-canonical-name` / `-comma-joined-name` / `-runs-1` | unchanged | unchanged | — | their write/verify are SKIPPED (m27c512 is UV; the plain mock operator cannot satisfy the slot probe), so no fingerprint is synthesized |
| `gh20-at28c256-fail`, `gh23-w27e257-fail`, `gh28-m27c512-fail`, `synthetic-arm4-*` | unchanged | unchanged | — | failing/NA steps keep their real read-back classification |

`[VERIFIED: executed this session against firestarter_app @ df2978e, all 16 `SHAPE_IDS`]`

### Filed-corpus impact

`tests/fixtures/devtest_issue_corpus.json` holds 26 filed `[dev test]` issues, each with its `filed_hash` and step vector. Reproducing all 26 through the canonical pre-image grammar and then applying the rule *"a write-shaped step with verdict `OK` classifies `match`"*:

- **26 of 26 reproduce** at HEAD (assertion held for every row).
- **18 of 26 would re-key.** Issues: **22, 24, 25, 26, 27, 29, 31, 39, 40, 42, 45, 46, 47, 48, 49, 50, 51, 52**.
- gh#39 and gh#40 currently share `334c3fa198bf` — they move together to `40a8c24f0f9c`, so that dedup group survives intact, merely re-keyed.

`[VERIFIED: executed this session — `tests/fixtures/devtest_issue_corpus.json`, 26 rows, canonical pre-image `raw_token|protocol|op=verdict:cls…|repeat_policy_tag?|coverage_tag?` asserted equal to each row's `filed_hash` before mutation]`

This is the concrete content of D-4/D-6's *"Re-keys dedup history once, deliberately … stated publicly."* **GATE-06 requires it recorded in `MILESTONES.md` with before/after hashes.** 18 rows is a large, publishable number and it should be stated as such rather than summarized as "some history".

*(Caveat, stated honestly: FAIL-verdict rows in that 18 move under this rule only if their passing write-shaped steps get the synthesized `match`. The corpus records only the classification string, not `bad`, so I cannot verify from the corpus alone whether a FAIL row's `OK` write step had `bad == 0`. The mutation applied is exactly the rule PRUNE-01+PRUNE-03 produce — a passing step performs no read-back, so verdict is the only signal available — which is why the count is the right one to plan against.)*

---

## Counting read-backs in a test (roadmap criterion 1)

Criterion 1 demands the zero be **counted**, not inferred. Three seams exist; two are already proven in this tree.

| Seam | How | Verdict |
|---|---|---|
| `Mock(spec=OPERATOR_METHODS).read_eprom.call_count` | The engine's only device-read path is `operator.read_eprom`; `_read_region` calls it at `chip_test.py:2728` | **RECOMMENDED.** Already the mechanism of the existing analog test. |
| `FakeChip.calls` — *"a plain list of `(method_name, kwargs)` tuples so a test can assert which addresses/sizes were actually requested"* `[VERIFIED: firestarter_app/tests/fake_chip.py:44-46]` | Use when the test needs the *region* as well as the count | **RECOMMENDED for the cycle-1-fail/cycle-2-pass leg**, where a stateful double is needed anyway |
| `firestarter.transport_counters` (Phase 176) | `record_decode_failure` etc., snapshot/reset | **WRONG SEAM.** It counts decode failures, timeouts, probe timeouts and re-syncs — transport *faults*, not reads. `[VERIFIED: firestarter_app/firestarter/serial_comm.py:352, cli_handlers.py:2404/2440, eprom_operations.py:1772/1792 — the only call sites]` |

**Discrimination caveat:** `read_eprom.call_count` counts the read *step* too (`_dispatch_read`, `runs` calls). Two ways to isolate the fingerprint read-backs, both sound:
- Build the plan with **only** write/verify steps — the existing analog test already does this, and a non-UV chip's `_resolve_write_target` performs no device read (verified above), so on such a plan `read_eprom.call_count` is *exactly* the fingerprint read-back count.
- Or assert on `call_args_list` filtered by `size_str`/`address_str` matching the write region.

### The existing analog test — and the fact that Phase 177 must invert it

```python
def test_fingerprint_readback_happens_once_not_once_per_cycle():
    """`collect_fingerprint` is True only on the final cycle. Without that
    gate the write and verify steps would each add a region read-back per
    cycle -- real cost on a full-device region, for a fingerprint that only
    ever describes the device's FINAL state."""
    operator = _mock_operator()
    plan = _plan_with_steps(
        Step(op=OP_WRITE, supported=True, reason="", destructive=True),
        Step(op=OP_VERIFY, supported=True, reason=""),
    )
    run_plan(plan, operator, _REAL_DB, runs=3)

    # One read-back for the write step, one for the verify step. NOT 3 + 3.
    assert operator.read_eprom.call_count == 2
```
`[VERIFIED: firestarter_app/tests/test_chip_test.py:1507-1521]` — and it **passes today** (`1 passed in 0.05s`, run this session in `.venv311`).

Under PRUNE-01 this run is all-passing, so the expected count becomes **0**, not 2. **This test is the single most direct pre-existing statement of the behaviour Phase 177 changes and must be updated in the same commit as the gate.** Its docstring's justification (a fingerprint "only ever describes the device's FINAL state") remains true and should be preserved alongside the new one.

---

## The existing test surface

| File | Covers | Notes for the planner |
|---|---|---|
| `tests/test_chip_test.py` | plan derivation + `run_plan` execution; the analog test above at `:1507`; 8 references to `indeterminate` | Uses a module-local `_mock_operator()` (`Mock`-based, `read_eprom` returns `True` with no file side-effect, so `_read_region` returns `b""` and today's fingerprint is `None` while the *call* still counts) |
| `tests/test_chip_test_cycle.py` | the per-family cycle recipes; `_cycle_operator(name, blank=)` at `:56` builds a `Mock(spec=_OPERATOR_METHODS)` whose `_read` **seeks to the absolute address** before writing — the property `_read_region` depends on | **The nearest correct double for a cycle-1-fail/cycle-2-pass test.** Set `operator.write_eprom.side_effect = [False, True]`. |
| `tests/fake_chip.py` | `FakeChip` — real UV AND-write physics + absolute-offset reads, plus a `calls` ledger | The double to use when the test must observe *which* region was read |
| `tests/plan_corpus.py` | `mock_operator(**returns)` (`:119`), `plan_with_steps` (`:138`), `step` (`:143`); `plan_corpus` fixture builds 1,354 real plans | Shared helpers from Phase 175 |
| `tests/test_blast_radius_invariance.py` | 28 tests: `test_dedup_fingerprint_is_frozen`, `test_build_db_diff_ladder_pin_for_all_shapes`, `test_committed_snapshot_matches_a_fresh_regeneration`, `test_shape_ids_committed_anchor_matches_the_registry`, `test_shape_ids_frozen_hashes_ladder_pins_and_snapshots_agree`, `test_build_shape_raises_for_every_reserved_shape_id`, … | **This is the gate that will go RED.** Registering `prune03-synthesized-fingerprint-match` requires updating `_BUILDERS`, `FROZEN_HASHES`, the ladder pins, `tests/fixtures/shape_ids.json` and a snapshot — the four-way closure test enforces all of it at once |
| `tests/fixtures/report_shapes.py` | the 16 builders + `FROZEN_HASHES` + `RESERVED_SHAPE_IDS` | `prune03-synthesized-fingerprint-match` is **already reserved for Phase 177** `[VERIFIED: firestarter_app/tests/fixtures/report_shapes.py:639-645]` |
| `tests/fixtures/rekey_ledger.py` | the 6-row `LEDGER` tuple | `ast.literal_eval`-parsed by the meta checker; must stay logic-free |
| `tests/fixtures/reports/*.json` | 16 committed `to_dict()` snapshots | Regenerate with `tools/snapshot_report_shapes.py`; a moved classification moves the snapshot too |
| `tests/test_devtest_issue_corpus.py` | the 26 filed-issue rows reproduce through the real hash | **Will redden for the 18 rows above** unless the corpus records the re-key |
| `tests/test_diagnostic_report.py` | `build_db_diff` arms incl. the `indeterminate → _LADDER_NONE` route (`:709-785`) | These construct `indeterminate` fingerprints *directly*, so they stay valid — `indeterminate` remains reachable for failing read-backs |
| `tests/test_devtest_firmware_error_propagation.py:211` | the only test that passes `collect_fingerprint=False` explicitly | Sanity-check it still means what it says after the signature changes |

**Suite cost, for planning:** the full app suite measures **740.92 s** `[CITED: .planning/MILESTONES.md — "against a measured full-suite baseline of 740.92 s"]`; the Phase 174 blast-radius modules run in 7.92 s together. `tests/test_skip_census.py`'s three failures are **pre-existing** and unrelated.

Run tests as `cd firestarter_app && ./.venv311/bin/python -m pytest <target> -o addopts="" -q` — `addopts` is `-ra -q` and doubling `-q` suppresses the count line.

---

## The seed's self-contradiction (PRUNE-07)

`.planning/seeds/dev-test-adaptive-sequencing.md`, R1 and R2, verbatim:

> ### R1 — Never read what you can verify
>
> `verify_eprom` streams host→device and the firmware compares
> ([`memory.cpp:377-396`](../../firestarter/src/proms/memory.cpp#L377-L396)).
> Same byte coverage as a read-back, **24% cheaper**, no host file I/O, and it
> early-returns on the first mismatch — so failing runs get *faster*, not slower.
>
> Any place the engine reads the whole device back to compare it against a buffer
> it already holds is a verify. **This applies to the fingerprint read-backs; it does
> not apply to the SDP leg**, whose `_read_region` read-back *is* the verdict and
> must stay a real read.

> ### R2 — Diagnose on failure only
>
> Gate the fingerprint read-back at
> [`chip_test.py:3100`](../../firestarter_app/firestarter/chip_test.py#L3100) on
> `not all(outcomes)`.
>
> - Passing run: **zero** read-backs.
> - Failing run: **byte-identical** fidelity to today.

**The contradiction, precisely.** R1's sentence *"This applies to the fingerprint read-backs"* instructs the reader to **replace** the fingerprint read-back with `verify_eprom`. R2 promises a failing run keeps *"byte-identical fidelity to today"*, which requires the read-back to still exist and still return the whole region. Both cannot hold: `verify_eprom` returns a `bool` and, on failure, one firmware error frame carrying **one** mismatch address (`memory_verify_execute` `return`s at the first `byte != expected`, `[VERIFIED: firestarter/src/proms/memory.cpp:381-395]`). `classify_fingerprint` needs the whole mismatch *distribution* — `ff_ratio` across the buffer for bucket 1, and per-bit clustering across all `diff_offsets` for bucket 2. A planner following R1 literally therefore deletes the four-bucket diagnostic that R2's own gate exists to preserve for failing runs, and R2's promise silently becomes false.

The project already has the correct formulation, in the note the seed itself points at:

> That asymmetry is the design seam. **Verify decides; a read-back diagnoses; the read-back only needs to run when verify says something is wrong.**
> `[VERIFIED: .planning/notes/dev-test-sequence-cost-model.md:75-76]`

### Proposed minimal amendment

Replace R1's final paragraph with:

> Any place the engine reads the whole device back to compare it against a buffer
> it already holds is a verify. Two read-backs are **excluded by design and must
> stay real reads**: the **fingerprint** read-back, which R2 governs — a verify
> returns a bool and one mismatch address, while `classify_fingerprint` needs the
> whole mismatch distribution (`ff_ratio` across the buffer, bit-clustering across
> every offset), so converting it deletes the diagnostic R2 exists to preserve —
> and the **SDP leg**, whose `_read_region` read-back *is* the verdict. The seam
> is: **verify decides; a read-back diagnoses; the read-back only needs to run
> when verify says something is wrong.**

And append to R2, so the anchor stops mis-stating its own predicate:

> The predicate must consult the step's outcomes **across all cycles**, not
> `not all(outcomes)` alone: under `_run_cycle_block` each cycle calls
> `_dispatch_multi_run` with `runs=1`, so `outcomes` is a one-element list
> describing the final cycle only. A cycle-1-fail / cycle-2-pass run must keep its
> fingerprint. And a passing step still **reports** a fingerprint — synthesized
> from `bad=0`, `total=region_length`, `ff_ratio: None` and classified `match`.
> The read-back is what costs; the classification is free.

Criterion 5 asks that *"a planner reading only the seed cannot regenerate the destructive interpretation."* The affirmative "must stay real reads" phrasing plus the stated *why* satisfies that; deleting the sentence without a replacement would not, because the general rule in the preceding sentence would still sweep the fingerprint in by default.

**Housekeeping:** the seed's frontmatter reads `status: dormant` and `trigger_condition: Next milestone that touches dev test / chip_test.py`. v1.36 *is* that milestone. Whether to flip `status` is a judgement call the planner should make explicitly rather than leave. `.planning/` is tracked in the **meta repo** (`/workspaces`), not a sub-repo — this edit and the `MILESTONES.md` edit are meta-repo commits, while every code and test edit is a `firestarter_app` sub-repo commit.

---

## Common Pitfalls

### Pitfall 1: Reusing the ledger's projected `after_hash`
**What goes wrong:** the plan targets `60a031573aab` for `sst27sf512-six-step`; the real post-PRUNE-03 value is `7fb88e0b07d6`.
**Why it happens:** `MILESTONES.md:39` and `rekey_ledger.py`'s prose both name `60a031573aab` prominently, and Phase 174 froze a whole companion shape at it. The projection predates PRUNE-03 and models the fingerprint being *dropped*.
**How to avoid:** treat every projected number as falsified until re-measured after the code lands. Record the falsification in `MILESTONES.md` — this project has a standing rule against silently absorbing a measured disagreement, and MILESTONES.md already carries a "Corrections measured by plan 174-03" table that is the right home.
**Warning signs:** a plan whose acceptance criterion is a hash literal copied from a document rather than produced by a run.

### Pitfall 2: Adding `match` as an early-return inside `classify_fingerprint`
**What goes wrong:** two things. (a) `ff_ratio` can never be `None` there (`:188`), so PRUNE-03's stated evidence value is unreachable. (b) The classifier's *first* bucket is `ff_ratio >= 0.98`, checked *"regardless of whether there are zero mismatches (a perfect verify)"* — a `bad == 0` early-return placed **above** it silently converts every bit-perfect all-0xFF compare from `blank/contact` to `match`, which is a *second*, undeclared re-key of exactly the shape the `ff_ratio` false-PASS check exists to catch.
**How to avoid:** synthesize on the cheap path with a dedicated constructor. If `classify_fingerprint` also gains the bucket for the read-back path, place it **below** the `ff_ratio` test and measure the effect on `gh23-w27e257-fail` (the only frozen shape carrying `blank/contact`) before deciding.
**Warning signs:** `gh23-w27e257-fail`'s hash moving. It should **not** move.

### Pitfall 3: Re-keying a shape another phase owns, silently
**What goes wrong:** `sst27sf512-full-all-ok` is `RK-174-06-p178`'s subject, and that row's *entire purpose* is to assert Phase 178 introduced no re-key. PRUNE-03 moves it (`4b3e52cab987 → 14d306256076`) because its passing write/verify currently carry no fingerprint at all. `w27e257-full-all-ok` moves too and has no row.
**How to avoid:** append new rows (`RK-174-07-p177-…`, `RK-174-08-p177-…`) rather than editing existing ones — the ledger is append-only (D-09) and `before_hash` is never overwritten. Then Phase 178 measures from the new baseline.
**Warning signs:** a plan that mentions only two ledger rows.

### Pitfall 4: Repairing the reddened gate inside the behaviour commit
**What goes wrong:** the D-11 protocol is a review mechanism, and collapsing the two commits destroys it. `tools/rekey/check_rekey_ledger.py` will not catch this — it checks consistency, not commit topology.
**How to avoid:** plan the behaviour change and the declaration as separate tasks with separate commits, and state in the plan that the gate is *expected* RED between them.

### Pitfall 5: Skipping a diagnostic without saying so
**What goes wrong:** `fingerprint: null` would come to mean three different things: skipped-because-everything-passed, ran-and-returned-`b""`, never-had-one. `[CITED: .planning/research/SUMMARY.md:91]`
**How to avoid:** PRUNE-03 already solves this by never emitting `null` on a pass. **Do not additionally add `fingerprint_source`** — that is the research's alternative solution to the same problem and it is unscoped here (see Deferred Ideas).

### Pitfall 6: Losing the `ff_ratio` false-PASS check without the licence being green
**What goes wrong:** the read-back was written unconditional *because* `classify_fingerprint`'s bucket 1 catches a write that reports OK without driving the bus. Gating it removes that check from passing runs.
**Why it is safe here:** the licence is the verify step immediately behind every write, made structural by PRUNE-06 in Phase 175. The roadmap makes this explicit: Phase 175 *"must be green before this phase's change lands."*
**How to avoid:** confirm `tests/test_derive_plan_structural_sentinel.py` is green **before** the gate lands, and say so in the plan.

### Pitfall 7: Editing the ledger and MILESTONES.md "in the same commit"
**What goes wrong:** they are in **different git repositories** (`firestarter_app` sub-repo vs. the `/workspaces` meta repo). D-11's "one commit" is per-tree; the cross-tree binding is enforced by running `python3 tools/rekey/check_rekey_ledger.py` from `/workspaces` against the populated submodule.
**How to avoid:** plan it as two commits (one per repo) landing together, with the local checker run as the acceptance evidence.

---

## Code Examples

### The gate, as it must become (shape only — the planner owns the final form)

```python
# firestarter_app/firestarter/chip_test.py, at the :3100 site
        step_failed = prior_cycles_failed or (not all(outcomes) if outcomes else False)
        if collect_fingerprint and op in (OP_WRITE, OP_WRITE_PARTIAL, OP_VERIFY):
            if step_failed:
                actual = _read_region(
                    operator, name, eprom_data, region_start, region_length
                )
                if actual:
                    diverged = len(set(outcomes)) != 1 if outcomes else False
                    fingerprint = classify_fingerprint(
                        expected,
                        actual,
                        repeat_divergent=diverged,
                        addr_base=region_start,
                    )
            else:
                fingerprint = _synthesized_match_fingerprint(region_length)
```
*(No `#` comments — rationale belongs in `_dispatch_multi_run`'s docstring, the idiom Phase 176-02 used for MEAS-02/MEAS-03.)*

### The synthesized fingerprint (PRUNE-03's stated values, exactly)

```python
def _synthesized_match_fingerprint(region_length: int) -> Fingerprint:
    """..."""
    return Fingerprint(
        total=region_length,
        bad=0,
        bad_pct=0.0,
        classification=FP_MATCH,
        evidence={
            "ff_ratio": None,
            "repeat_divergent": None,
            "first_offset": None,
            "bit_clustering": {},
        },
    )
```

The `evidence` key set mirrors `classify_fingerprint`'s exactly `[VERIFIED: firestarter_app/firestarter/chip_test.py:190-195 — `{"ff_ratio": ..., "repeat_divergent": ..., "first_offset": ..., "bit_clustering": {}}`]`, so RPT-A2 in Phase 181 finds a uniform shape. `ff_ratio: None` is PRUNE-03's literal requirement and is the honest value: it was not measured.

### The cross-cycle predicate, computed at the call site

```python
# firestarter_app/firestarter/chip_test.py, inside _run_cycle_block's loop
                result = _run_step(
                    name,
                    step,
                    operator,
                    db,
                    runs=1,
                    sampler=sampler,
                    write_context=write_context,
                    collect_fingerprint=final,
                    prior_cycles_failed=any(
                        r.verdict != VERDICT_OK
                        for r in per_step[i]
                        if r.verdict in _RAN_VERDICTS
                    ),
                )
```

### The cycle-1-fail / cycle-2-pass test (criterion 2)

```python
def test_a_failing_first_cycle_keeps_the_fingerprint_read_back():
    operator, _writes = _cycle_operator("M8720")
    operator.write_eprom.side_effect = [False, True]   # cycle 1 fails, cycle 2 passes
    plan = ct.derive_plan("M8720", _REAL_DB, write_scope="full")
    ct.run_plan(plan, operator, _REAL_DB, runs=2)
    assert operator.read_eprom.call_count > 0
```
Built on `tests/test_chip_test_cycle.py`'s `_cycle_operator` (`:56`), whose `_read` seeks to the absolute address — a double that writes at offset 0 makes every region slice come back short and the test would pass for the wrong reason.

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|---|---|---|---|
| Whole-device fingerprint read-back | Region-scoped via `_read_region` | quick task 260821-wna | The read-back is **already not whole-device**; PRUNE-04's premise about it is historical |
| `fingerprint` read-back once per cycle | `collect_fingerprint=final` — final cycle only | the cycle-block refactor | Phase 177 is the *second* narrowing of the same cost, not the first |
| `indeterminate` on a bit-perfect compare | `match` bucket (D-4/D-6) | **this phase** | Un-blocks the promotion ladder; re-keys 18 of 26 filed reports |
| Relational dedup tests (`fp(a) == fp(b)`) | Frozen absolute hashes + append-only ledger + cross-tree checker | Phase 174 | The reason this phase's blast radius is measurable at all |

**Deprecated/outdated:**
- The projected `after_hash` `60a031573aab` and the frozen shape `sst27sf512-six-step-readback-gated` — both model the pre-PRUNE-03 reading. Not wrong when written; superseded by the requirement.
- The milestone research's Phase 177 delivery list (declared-oracle field on `Step`, `fingerprint_source`) — superseded by the requirement IDs actually assigned.

---

## Project Constraints (from CLAUDE.md and standing operator rules)

| Constraint | Source | Consequence for this phase |
|---|---|---|
| **No comments in source, at all.** A plan cannot override this. | operator standing rule (broadened 2026-08-29 from provenance-only to zero comments) | Every rationale goes in a **docstring**. The example code above is comment-free deliberately. Phase 175-05 audited "zero comments" as a phase-seal criterion — expect the same here. |
| `firestarter/constants.py` ↔ firmware `firestarter.h` must stay in sync | `firestarter_app/CLAUDE.md` | Not triggered — this phase touches no constants that mirror firmware. |
| Tooling gate: `ruff check` + `ruff format --check` + `mypy` (strict on 8 modules) + `pytest --cov-fail-under=70` | `firestarter_app/CLAUDE.md` | `chip_test.py` and `diagnostic_report.py` are **not** in the strict-island list, so new typed helpers there are mypy-*watermark* only. Watermark is 35/35; do not move it. `ruff select` is `[E,F,I,UP]` — every `# noqa: BLE001` in the tree is inert. |
| CI is **py3.11 only**; the devcontainer default 3.12 masks app CI | operator standing rule; `.planning/research/SUMMARY.md:47` | Every measurement in a plan must be taken in `firestarter_app/.venv311`. |
| Do not hand-edit `chip_database.json` | `CLAUDE.md` | Not triggered. |
| `HYG-02`: no new runtime dependency | REQUIREMENTS.md | Nothing to install. |
| `HYG-04`: any new `dev_test` helper registered in `tools/check_devtest_orchestrator.py:152-164` | REQUIREMENTS.md | Only fires for **handler-side** (`cli_handlers.py`) helpers — the allow-list is `_HANDLER_FUNCTION_NAMES` `[VERIFIED: firestarter_app/tools/check_devtest_orchestrator.py:152-165 — `_HANDLER_FUNCTION_NAMES = frozenset({...})`, last entry `"_make_sampler"` at :163]`. A new helper inside `chip_test.py` does not need registering. Verify before assuming either way. |
| Meta-repo vs sub-repo commit boundary | `CLAUDE.md`; operator memory | `.planning/seeds/…` and `.planning/MILESTONES.md` are meta commits; everything under `firestarter_app/` is a sub-repo commit on `gsd/v1.36-dev-test-fidelity`. |

**Project skills present:** `/workspaces/.claude/skills/` holds `devtest-triage`, `devtest-rootcause`, `find-skills`, `skill-creator`. `devtest-triage/SKILL.md` is a **live prose consumer of the report** — D-5/RPT-F2 bind it to Phase 181's `vpp_mv` deletion, not to this phase. But note: this phase changes what a report *implies* (an all-OK run becomes ladder-promotable). Check whether `devtest-triage/SKILL.md` reads `fingerprint` or `ladder_state` and, if so, flag it rather than silently changing the meaning underneath it.

---

## Runtime State Inventory

Not a rename/refactor/migration phase in the string-replacement sense, but the re-key **is** a data-shaped change to already-published state, so the same discipline applies:

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | **18 of 26 filed GitHub issues in `henols/firestarter_prom`** carry a `dedup_fingerprint` that this change re-keys. The hash is embedded in the issue body; `count_agreeing` reads the **embedded** value and never re-hashes, so the re-key is permanent for the historical corpus. | Declare in `MILESTONES.md` per GATE-06 with before/after. **No data migration is possible** (the issues are external); recovery is only by publishing the old→new mapping. Scope decision needed: publish the 18-row mapping, or state the reset. |
| Live service config | None — the report is generated per run; no service holds a copy. | None. |
| OS-registered state | None. | None. |
| Secrets/env vars | None. | None. |
| Build artifacts | `firestarter_app/build/lib/firestarter/chip_test.py` is a **stale copy** of the module (it still shows the pre-change line numbers). It is not on the import path but it *is* grepped by careless searches. | None required; be aware `grep -rn` across the repo returns doubles from `build/`. |
| Committed test artifacts | `tests/fixtures/reports/*.json` (16 snapshots), `tests/fixtures/shape_ids.json`, `tests/fixtures/rekey_ledger.py`, `tests/fixtures/devtest_issue_corpus.json` | Regenerate snapshots via `tools/snapshot_report_shapes.py`; hand-edit the ledger and the anchor per their own rules. |

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| CPython 3.11 venv (`firestarter_app/.venv311`) | every measurement | ✓ | 3.11.16 | none needed |
| pytest | the whole test surface | ✓ | (installed in `.venv311`) | — |
| `firestarter_app` sub-repo populated on the milestone branch | all code work | ✓ | `gsd/v1.36-dev-test-fidelity` @ `df2978e`, clean tree | — |
| `tools/rekey/check_rekey_ledger.py` (meta repo) | the GATE-06 binding | ✓ | present at `/workspaces/tools/rekey/` | the registered workflow `.github/workflows/rekey-ledger-check.yml` is the second leg |
| `tools/snapshot_report_shapes.py` | regenerating the 16 report snapshots | ✓ | present | — |
| EPROM programmer hardware | — | n/a | — | **This phase is not hardware-gated.** Every criterion is provable against the existing bench-free doubles. |

**Missing dependencies with no fallback:** none.

---

## Security Domain

`security_enforcement` is **absent** from `.planning/config.json` `[VERIFIED: /workspaces/.planning/config.json — grep for "security" returns no match]`, so it defaults to enabled.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | Local CLI; no auth surface |
| V3 Session Management | no | No sessions |
| V4 Access Control | no | No multi-user surface |
| V5 Input Validation | no (unchanged) | This phase adds no new external input. The report already scrubs free text and `dedup_fingerprint` deliberately excludes it (*"no scrubbable free text can influence it"*, `[VERIFIED: firestarter_app/firestarter/diagnostic_report.py:254-257]`) |
| V6 Cryptography | **partially** | `dedup_fingerprint` uses `hashlib.sha256` truncated to 12 hex chars and its docstring already states the correct framing: *"A non-secret dedup id, not a security control: sha256 is used for its distribution."* `[VERIFIED: firestarter_app/firestarter/diagnostic_report.py:259-260]`. Do not "harden" it; do not lengthen it. HYG-03 additionally forbids refactoring it to hash `to_dict()`. |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| A report re-key silently orphans a dedup group, blinding the triage mechanism that decides which community reports get attention | Repudiation / Denial of information | The Phase 174 ledger + `MILESTONES.md` declaration + the cross-tree checker — already built; this phase must *use* it |
| Free text (a chip name, an error message) influencing the dedup id | Tampering | Already mitigated by the allow-list hash; this phase adds no new hashed field |
| A hallucinated "hardening" of the truncated hash | — | Explicitly out of scope; the docstring pre-empts it |

No new attack surface: this phase adds no I/O, no parsing, no network call, and no new dependency.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|---|---|---|
| A1 | The `match` classification literal is spelled exactly `"match"` (lowercase, no qualifier) | Fingerprint structure; all projected hashes | **Every projected hash changes.** REQUIREMENTS.md D-4 and PRUNE-03 both write it lowercase but no code defines it yet. Confirm at plan time. |
| A2 | The synthesized fingerprint is emitted for `OP_WRITE`, `OP_WRITE_PARTIAL` **and** `OP_VERIFY` (the same three ops the current gate covers) | Code examples; projected hashes | If verify is excluded, `verify=OK:` stays empty and every projected hash moves |
| A3 | The gate is **per step**, not per run — a BAD `blank-check` does not force a read-back on a passing `write` | Anti-patterns; blast radius (`m27c512-full-blank-check-bad` does not move) | If the gate is per-run, `m27c512-full-blank-check-bad` and every FAIL-verdict filed report behave differently |
| A4 | `classify_fingerprint` is **not** given a `bad == 0` early-return above the `ff_ratio` test | Pitfall 2; `gh23-w27e257-fail` staying put | A second, undeclared re-key of the `blank/contact` population |
| A5 | The 18-of-26 filed-corpus count assumes every write-shaped step with verdict `OK` gets `match`, including on FAIL-verdict runs | Filed-corpus impact | The number could be lower if some `OK` write steps on FAIL runs had `bad > 0`; the corpus does not record `bad`, so this cannot be settled from the corpus. Settle it by re-measuring after the code lands. |
| A6 | Roadmap criterion 4 intends a *real* call-site replacement rather than a measured-empty closure | PRUNE-04 inventory; Open Question 1 | The phase either does nothing for PRUNE-04, or breaks a diagnostic. Operator decision. |
| A7 | Appending `RK-174-07`/`RK-174-08` rows is the sanctioned response to a re-key on a shape another phase owns | Pitfall 3 | If the ledger id grammar or the checker rejects two rows sharing a `shape_id`, a different mechanism is needed. The checker's stated rule is uniqueness of `ledger_id`, not of `shape_id` `[VERIFIED: /workspaces/tools/rekey/check_rekey_ledger.py:1-40 docstring]` — but this has not been exercised. |

---

## Open Questions (RESOLVED)

All five are resolved by the Phase 177 plan set. Questions 1-4 are routed to explicit
`checkpoint:decision` tasks that the operator answers at execution time; Question 5 was
answered during pattern mapping and needs no decision. Each question below carries its
resolution inline.

1. **PRUNE-04 / roadmap criterion 4: what is "the engine", and is `write_cycle_eprom` in scope?**
   - *What we know:* after D-1's exclusion and the seed's SDP carve-out, `chip_test.py` has **zero** whole-device-read-to-compare-a-held-buffer sites. The only such site in the whole package is `eprom_operations.write_cycle_eprom` (`:1195-1250` read, `:1246-1247` SHA compare against `source_sha` from `:1171`), reached from `dev write-cycle` (`cli_handlers.py:1546`) and `dev validate-family` (`cli_handlers.py:2017`).
   - *What's unclear:* whether the requirement's "the engine" means the `dev test` engine (`chip_test.py`) or the app's operator layer.
   - *Recommendation:* **open the phase with a `checkpoint:decision`.** Present both readings and the argument against converting `write_cycle_eprom`: its read-back is itself a *read-repeatability* diagnostic (it is the uno328pb read-bug oracle, and its docstring says *"Reuses `_operation_context` + `_run_state_machine` + `_main_phase_read_data` verbatim from `consistency_check_eprom`. Do NOT refactor the read-back block into a parallel read implementation."* `[VERIFIED: firestarter_app/firestarter/eprom_operations.py:1166-1168]`). Replacing it with a verify would repeat exactly the D-1 error one layer down. My recommendation is to close PRUNE-04 as **measured-empty within the engine**, with the inventory above as the evidence and `write_cycle_eprom` explicitly named-and-excluded with its reason — mirroring how PRUNE-08 is permitted to close as *measured, not worth doing*.
   - *RESOLVED:* owned by **D-177-1** (`177-01-PLAN.md`, blocking `checkpoint:decision`). Option A (close measured-empty, the recommendation above) is the default; Option B's alternate action is written out concretely inside `177-03-PLAN.md` Task 1, so the plan executes under either answer.

2. **Does `classify_fingerprint` itself gain the `match` bucket, or only the synthesized cheap path?**
   - *What we know:* the SDP leg (`_dispatch_sdp_leg`) calls `classify_fingerprint` on every arm and is **not** gated by this phase; an all-OK AT28C256 run's four SDP-leg steps carry `indeterminate` today. `RK-174-05`'s stated mechanism is *"add a `match` bucket to the fingerprint classifier"* and names `at28c256-full-all-ok-sdp` — which only moves if the classifier itself changes. So the ledger's own framing says **yes, inside the classifier.**
   - *What's unclear:* the placement relative to the `ff_ratio` test (Pitfall 2) and whether `repeat_divergent is True` should still win over `bad == 0`.
   - *Recommendation:* place it **after** the `ff_ratio` test and **after** the address-line test, before the `repeat_transport` test; then measure `gh23-w27e257-fail` (the only frozen `blank/contact` shape) and assert it does **not** move.
   - *RESOLVED:* owned by **D-177-2** (`177-01-PLAN.md`). The plan adds the `match` bucket inside the classifier, placed per the recommendation above, and pins the non-regression by asserting `gh23-w27e257-fail` does not move.

3. **What happens to `sst27sf512-six-step-readback-gated`?**
   - *What we know:* it is frozen at `60a031573aab`, models the naive R2 reading, and under PRUNE-03 collapses onto the same value as `sst27sf512-six-step` (`7fb88e0b07d6`).
   - *Recommendation:* keep the shape (deleting it fails `test_shape_ids_closure_is_sensitive_to_removed_and_added_entries` and destroys evidence), re-point its `step_specs` to a *genuinely distinct* post-177 shape — the natural one is a **failing** write/verify that keeps a real read-back classification — and record the collapse as a falsified projection in `MILESTONES.md`. Then register the reserved `prune03-synthesized-fingerprint-match` for the new passing shape.
   - *RESOLVED:* owned by **D-177-3** (`177-01-PLAN.md`). The plan keeps the shape and re-points it to the gate's failing branch with verdict `marginal` — which both replaces the falsified projection and re-populates `LADDER_PINS`' inconclusive arm, gated on `distinct_arms=4`.

4. **Is the 18-row filed-corpus re-key published, or only declared?**
   - *What we know:* GATE-06 requires declaration with before/after hashes. D-4/D-6 says the re-key is *"stated publicly because it changes what a report implies to the triage skill and to every human reader."* The "Out of Scope" table says this milestone *"does not work the tracker."*
   - *Recommendation:* declare in `MILESTONES.md` with the full 18-row mapping as a committed artifact; do **not** edit the issues (out of scope). Flag to the operator as a `checkpoint:decision` if the plan wants to go further.
   - *RESOLVED:* owned by **D-177-4** (`177-01-PLAN.md`). The 18-row figure is a projection to be measured and published as a new committed artifact, not a fixture edit; `tests/test_devtest_issue_corpus.py` rebuilds from each row's recorded classification strings and does not redden on its own.

5. **Does `.claude/skills/devtest-triage/SKILL.md` read `fingerprint` or `ladder_state`?**
   - *What's unclear:* I did not audit the skill's prose for those keys. D-5/RPT-F2 bind it to Phase 181's `vpp_mv` deletion; nothing binds it here.
   - *Recommendation:* a one-line grep at plan time. If it reads either key, the meaning-change (all-OK becomes ladder-promotable) is a consumer impact worth a sentence in the plan, even if no edit is needed.
   - *RESOLVED:* no decision needed. The pattern-mapping pass audited the skill: it reads `dedup_fingerprint` only as a dedup key (`:55-56`, `:80`, `:162`, `:193`, `:436`) and never reads the `fingerprint` classification string or `ladder_state`. No skill edit is forced. Recorded as flagged assumption PA-19 in `177-03-PLAN.md`.

---

## Sources

### Primary (HIGH confidence — read this session, in this working tree)
- `firestarter_app/firestarter/chip_test.py` — lines 65-73, 125-260, 1132-1168, 1279-1335, 1466-1576, 2603-2672, 2710-2745, 2746-2870, 2922-3160, 3300-3400
- `firestarter_app/firestarter/diagnostic_report.py` — lines 240-384, 760-800
- `firestarter_app/firestarter/eprom_operations.py` — lines 945-1000, 1140-1260, 1829-1866, 2094-2135
- `firestarter/src/proms/memory.cpp` — lines 375-398 (`memory_verify_execute`)
- `firestarter_app/tests/fixtures/report_shapes.py`, `rekey_ledger.py`, `shape_ids.json`, `devtest_issue_corpus.json`
- `firestarter_app/tests/test_chip_test.py:1495-1560`, `tests/test_chip_test_cycle.py:1-110`, `tests/fake_chip.py:1-140`, `tests/plan_corpus.py:110-146`, `tests/test_blast_radius_invariance.py` (test census)
- `firestarter_app/tools/check_devtest_orchestrator.py:140-175`
- `/workspaces/tools/rekey/check_rekey_ledger.py:1-40`
- `/workspaces/.planning/MILESTONES.md:14-45`
- `/workspaces/.planning/REQUIREMENTS.md` (full)
- `/workspaces/.planning/seeds/dev-test-adaptive-sequencing.md` (full)
- `/workspaces/.planning/notes/dev-test-sequence-cost-model.md:68-90`
- `/workspaces/.planning/ROADMAP.md:244-362`
- Executed measurements in `firestarter_app/.venv311` (Python 3.11.16): all 16 frozen-shape hashes reproduced; PRUNE-03 projections computed; `build_db_diff` ladder flip observed; 26/26 corpus rows reproduced and 18 re-keys counted; `test_fingerprint_readback_happens_once_not_once_per_cycle` run green

### Secondary (MEDIUM confidence)
- `/workspaces/.planning/research/SUMMARY.md` — the milestone research synthesis (lines 1-60, 80-135, 179-184). Authoritative for *why* decisions were taken; **not** authoritative for this phase's delivery list, which the requirement IDs supersede.

### Tertiary (LOW confidence)
- None. No web search was performed: this phase touches no external library, no protocol standard, and no third-party API. Every question was answerable from the working tree.

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — nothing is added; the one runtime constraint (py3.11) verified by execution
- Architecture / code inventory: HIGH — every file:line opened and quoted verbatim; the operator-call census is exhaustive by construction
- Blast radius / projected hashes: HIGH as *measurements of a simulated change*, MEDIUM as *predictions of the landed change* — they depend on A1/A2/A3 above
- PRUNE-04 scope: MEDIUM — the inventory is HIGH confidence, the adjudication is an operator decision
- Pitfalls: HIGH — each is grounded in a quoted line of the tree or a quoted project rule

**Research date:** 2026-09-05
**Valid until:** 2026-10-05 for the code inventory (stable, single-branch); **invalid the moment any code in `chip_test.py` or `diagnostic_report.py` changes** — re-measure every hash then.
