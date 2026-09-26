# Phase 175: Structural Sentinel over `derive_plan` - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-04
**Phase:** 175-structural-sentinel-over-derive-plan
**Areas discussed:** Predicate scope & closure; What "behind it" asserts; Sweep domain (D-8);
PRUNE-05's no-drop proof; plus the UV write-scope ceiling, raised by the operator mid-discussion

---

## Area selection

| Option | Description | Selected |
|--------|-------------|----------|
| Predicate scope & closure | Which ops require a verify; where the classification lives | ✓ |
| What "behind it" asserts | Adjacency vs cycle block; which fields must match | ✓ |
| Sweep domain (D-8) | Scopes; user-override DB; anti-vacuity strength | ✓ |
| PRUNE-05's no-drop proof | Alignment invariant vs frozen count table | ✓ |

**User's choice:** all four.

---

## UV write-scope ceiling (unplanned — raised by the operator)

The operator answered the first closure question by describing a behaviour rule instead: *"If the
EPROM isn't erasable a blank check must be made, if it is blank the full space can be used for
writes, but a question shall be raised if the full space can be used, if it is not blank find
suitable small partitions and use them for small writes. And this is only for eproms that can't be
erased so it doesn't apply to SRAM, FLASH or erasable EPROMs."*

Investigation showed this describes the **reverted** `260821-wna` design. Quick task `260822-aq6`
(commit `2b42dac`, 2026-08-22) retired the full-device-on-blank UV write and its prompt, reversing
`wna` one day later "with the operator's explicit agreement". A contradiction inside a single file
surfaced it: `_resolve_write_scope` states "there is no prompt on any path" thirty lines above a
design-history comment still saying "A UV-erasable EPROM is asked first".

| Option | Description | Selected |
|--------|-------------|----------|
| Keep aq6; pin it here | Reversal stands; the sentinel pins the structure so it cannot creep back; file the stale comment as a defect | ✓ |
| Keep aq6, pin nothing extra | Reversal stands; existing tests suffice; only the stale comment is filed | |
| Re-reverse it — bring back full+prompt | Behaviour change; would go to Phase 179, not here | |
| Just fix the stale comment | No new invariant; correct the comment only | |

**User's choice:** Keep aq6; pin it here.
**Notes:** Every other clause of the operator's rule is already exactly what the code does — UV-only
policy, blank-check ahead of the write, top-down slot probing on a non-blank part, saturated →
SKIPPED. Follow-up investigation established that `full_device_permitted` must **not** be asserted
False on a UV write step: it is `write_scope == "full"` verbatim and is inert on the `uv-slot` path,
so such an assertion would be a false invariant. The pin therefore targets `region_policy`, its
converse, blank-check ordering, and a handler-level leg over `_resolve_write_scope`.

---

## Predicate scope & closure

### Q1 — which ops require a verify?

| Option | Description | Selected |
|--------|-------------|----------|
| Total partition, fails closed | Every `OP_*` from `vars(chip_test)` must land in exactly one bucket — requires-verify or exempt-with-a-named-reason; an unclassified op is a RED | ✓ |
| Allow-list + equality pin | Predicate covers `{write, write-partial}`; a separate leg pins that set against a committed literal | |
| Derive by subtraction | `_DESTRUCTIVE_OPS - _SDP_LEG_OPS - {erase, sdp-lock}`; zero new sets | |

**User's choice:** Total partition, fails closed.
**Notes:** Chosen against the backdrop that the SDP leg's four write-shaped ops legitimately have no
verify — on `write-inhibited` the read-back *is* the oracle. Research input recorded at the time:
Python's `assert_never`/`Literal` exhaustiveness route is unavailable here because `Step.op` is a
bare `str`, so the closure must be a runtime set-difference sentinel.

### Q2 — where does `OP_ERASE` go?

First posed in dense terms; the operator asked for a simpler explanation and it was re-posed as a
plain-language table.

| Option | Description | Selected |
|--------|-------------|----------|
| A — two separate tests | Guard write→verify and erase→blank-check as two clearly-named legs | ✓ |
| B — only write→verify | Exactly what the phase asked for; erase pairing left unguarded | |
| C — one combined test | "Every step that changes the chip has a checker after it" | |

**User's choice:** A — two separate tests.
**Notes:** Keeps the write→verify leg mapping 1:1 onto PRUNE-06's wording, which matters because
Phase 177 cites it as its licence.

### Decided on precedent, not asked

- Classification lives test-side, cross-checked against `vars(chip_test)` — the shipped
  `test_shipped_ops_never_reach_sdp_arm` idiom; keeps the phase test-only.
- No sentinel over `Plan.locked_destructive` — a pending todo proposes deleting the field and is
  tagged `resolves_phase: 181`.

---

## What "behind it" asserts

### Q1 — positional strictness

| Option | Description | Selected |
|--------|-------------|----------|
| Same cycle block | A supported `OP_VERIFY` at a higher index within the block found by the shipped `cycle_block_bounds` | ✓ |
| Strict adjacency | The very next step must be the verify | |
| Anywhere later in the plan | Any higher index in `Plan.steps` | |

**User's choice:** Same cycle block.
**Notes:** Measured input: all four shipped emission orders currently place verify immediately after
write, so adjacency would pass today — it was rejected for re-implementing ordering knowledge
`cycle_block_bounds` already owns.

### Q2 — which fields must match

| Option | Description | Selected |
|--------|-------------|----------|
| Region, policy and payload | Assert all three equal the write's | ✓ (by delegation) |
| Region only | Assert `write_region` only | |
| Existence only | Assert nothing about fields | |

**User's choice:** "you decide" → Claude selected *region, policy and payload*.
**Notes:** All three are set equal by construction today, so there is no false-RED risk, and each
catches a distinct failure — wrong window, wrong kind of window, wrong expected bytes.

### Decided without asking

The verify must be `supported=True`. A `supported=False` verify behind a live write *is* a write with
no oracle.

---

## Sweep domain (D-8)

### Q1 — user-override database entries

| Option | Description | Selected |
|--------|-------------|----------|
| Shipped DB + synthetic adversarial rows | Sweep 746 rows, plus hand-built adversarial rows through a stub `db` | |
| Shipped DB only | `skip_local_override=True`, 746 rows, no claim about overrides | ✓ |
| Read the real override if present | Sweep `~/.firestarter/database.json` when it exists | |

**User's choice:** Shipped DB only.
**Notes:** This resolves REQUIREMENTS D-8, which was explicitly deferred to this phase. Recorded as a
closed question so no later phase re-opens it. The rejected third option carried a concrete hazard:
this project has a known leak where the app writes `~/.firestarter/config.json` despite
`FIRESTARTER_CONFIG_DIR`, so such a test cannot be reliably isolated in CI.

### Q2 — anti-vacuity strength

| Option | Description | Selected |
|--------|-------------|----------|
| Counter-plan + mutated-corpus sweep | Plus: every real plan containing a write must be flagged once its verify is removed from a copy | ✓ |
| Counter-plan + visited-count | Plus an assertion that the sweep visited the expected number of rows | |
| Counter-plan only | Exactly criterion 1 | |

**User's choice:** Counter-plan + mutated-corpus sweep.
**Notes:** Research input: the empty-selector trap is documented in
`test_erase_flag_invariants.py`'s own docstring, and `MAX_27C020_SIZE`'s parity test is a live
example of a gate in this repo that has always passed vacuously.

### Decided on research, not asked

Scopes swept are `"full"` and `"partial"`. `"none"` emits no write step, so the rule is vacuous
across ~677 extra plans; research classifies it as library/test surface only.

---

## PRUNE-05's no-drop proof

Measured before the question was posed: 746 rows → 1,492 plans swept in **1.18 s**; 17,904 total
steps of which **10,190** unsupported; only **4 distinct op-sequences** database-wide; a `run_plan`
sweep with a mock operator extrapolates to **~21 s**, with 50 of 50 sampled plans aligned.

| Option | Description | Selected |
|--------|-------------|----------|
| Both halves | Frozen 4-op-sequence pin (1.18 s) plus the `run_plan` alignment + NA-verdict sweep (~21 s) | ✓ |
| Frozen counts only | The op-sequence pin alone | |
| Alignment sweep only | `len(results) == len(plan.steps)` alone | |

**User's choice:** Both halves.
**Notes:** The hole was named before the question was asked: an alignment-only sweep **cannot** catch
the change PRUNE-05 forbids, because pruning unsupported steps inside `derive_plan` shrinks both
sides together and alignment still holds. Conversely a frozen pin alone says nothing about whether an
unsupported step actually yields a `StepResult` with `NA`.

---

## Wrap-up

| Option | Description | Selected |
|--------|-------------|----------|
| I'm ready for context | Write CONTEXT.md and hand off | ✓ |
| Explore more gray areas | Surface further candidates | |

**User's choice:** I'm ready for context.

---

## Claude's Discretion

- **Delegated explicitly by the operator:** the verify's field-matching set — region, policy and
  payload, all three.
- Decided on standing precedent and recorded as locked in CONTEXT.md: no re-key in this phase;
  anti-vacuity must be *seen* RED; all measurement in the py3.11 CI-replica venv; no new library;
  `/usr/bin/grep` for gate evidence; no comments in source; module placement per Phase 174's D-03;
  the frozen op-sequence pin reddening on database regeneration is signal, not noise (Phase 174 D-02
  precedent); no sentinel over `Plan.locked_destructive`.

## Deferred Ideas

- Stale design-history comment at `cli_handlers.py:2295-2305` describing the reverted UV prompt in
  the present tense — **file as a defect todo**; not fixed here, since this phase touches no product
  file.
- Re-reversing `aq6` — declined by the operator; would be Phase 179 behaviour work.
- A sentinel over `Plan.locked_destructive` — declined; field proposed for deletion in Phase 181.
- Whether the ~21 s `run_plan` sweep runs on every push or is marked slow — planner call; Phase 174
  set the same question aside for its own sweep.
- The fault-mode table — PITFALLS suggests Phase 175, the roadmap assigns it to Phase 177 as a named
  deliverable. Roadmap wins.
- `--fast` (`runs=1`) coverage — structurally impossible in a `derive_plan` sweep, since `--fast`
  changes `runs` at execution time and not plan shape. Belongs with Phase 177's run-time evidence
  ledger. Recorded so nobody plans it here and finds it impossible.

## Todos reviewed, none folded

36 matched by keyword, 21 at an undiscriminating 0.60 score. The four closest are already homed:
`gate-fingerprint-readback-on-step-failure` (177), `build-db-diff-ladder-state-…-regression` (177),
`delete-banner-locked-steps-dead-field` (181), `dev-test-chip-name-must-match-database` (181).
