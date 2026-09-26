# Phase 161: BOARD — Board Sweep, Three Boards on Rev 2.0 - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-27
**Phase:** 161-board-board-sweep-three-boards-on-rev-2-0
**Areas discussed:** Plan cut & park states, A2 failure protocol, W29C020 first silicon, Evidence row assembly, uno328pb read-back risk, A3/B2 leave-state

---

## Area selection

| Option | Description | Selected |
|--------|-------------|----------|
| Plan cut & park states | How the 12 positions split into plans; where the operator can walk away | ✓ |
| A2 failure protocol | Continuation policy and hang timeout for the expected uno328pb failure | ✓ |
| W29C020 first silicon | 262144 B has never run on hardware this milestone | ✓ |
| Evidence row assembly | 12 rows × ~40 fields, currently hand-authored per plan | ✓ |

**User's choice:** all four.

---

## Plan cut & park states

### Q1 — How should the 12 positions be cut into plans?

| Option | Description | Selected |
|--------|-------------|----------|
| One plan per cell-arm (6) | Plan never spans an arm switch or re-flashes mid-plan; 2 positions per plan; blast radius of a bad verify leg = 2 positions | |
| One plan per cell (3) | A1, A2, A3/B2 end-to-end, P-01→P-11; fewest handoffs; 2–3 h executor runs spanning two flashes and ~6 operator checkpoints | ✓ |
| One plan per position (12) | Maximum isolation and cleanest resume, but duplicates the P-04 flash proof and needs extra bookend plans (~14–15 total) | |

**User's choice:** One plan per cell (3).

### Q2 — What happens if a per-cell plan is interrupted mid-cell?

| Option | Description | Selected |
|--------|-------------|----------|
| Park after each position | Record + SAFETY line written after every completed position; 4 durable points per cell | |
| Park at the arm boundary only | Two durable points per cell (P-09→P-10, and teardown) | |
| No mid-cell park — restart the cell | Cell is atomic; an interrupt discards it and re-runs from P-01 | |

**User's choice:** Free text — *"I dont want any handover until a real physical action is needed."*

**Notes:** This reframed the question rather than answering it. The user is objecting to
**handovers/prompts**, not to record durability. Resolved as: `human-verify` checkpoints exist
**only** at the genuinely operator-performed steps (P-01 mount/declare, P-03 chip-out, P-05 seat,
P-06 pot, P-08 swap) and their repeats at the P-10 arm switch. Everything between is one continuous
run. Records are still written per position, because that requires nothing from the operator and so
does not conflict with the instruction. Cell boundaries are physical remounts and therefore already
natural stops needing no extra gate.

This area was closed after two questions rather than the default four — the free-text answer
collapsed the remaining ones (gate cadence was already settled by Phase 160 designating
`run_gates.sh` the standing per-wave gate; session scheduling across cells is inherently a physical
action).

---

## A2 failure protocol

### Q3 — If A2's W27C512 write fails as Backlog 999.2 predicts, what happens to that arm's W29C020 position?

| Option | Description | Selected |
|--------|-------------|----------|
| Run all 4 positions regardless | Four real verdicts instead of two verdicts + two named absences; tests whether the brownout is chip-dependent | ✓ (Claude) |
| Stop the arm at first failure | Record the W29C020 positions as named absences citing the observed W27C512 symptom; saves a swap and ~20 min | |
| Run W29C020 on v1.33 arm only | Halves the cost, keeps the headline arm complete — but breaks the A/B symmetry | |

**User's choice:** "you decide."

**Notes:** Claude selected *run all 4*. 999.2's brownout was observed on a 27C-family **program**
(pulsed high-VPP); W29C020 is algorithm 5, a 5 V page-write EEPROM with auto-erase, never tried on
this board. SC#3 forbids asserting the W27C512 failure from the backlog rather than observing it, so
extending that unobserved assumption to an untested chip would be the weaker claim. Cost: two
operator swaps, ~20 min. SC#3's own clause covers the upside — an unexpected completion is recorded
as an observation against 999.2, not discarded.

### Q4 — How long does a stalled write get before it's killed and recorded?

| Option | Description | Selected |
|--------|-------------|----------|
| Scaled ceiling from the baseline | Per-chip ceiling derived from the measured healthy figure; kill recorded as "timed out at N s against a measured baseline of M s" | ✓ (Claude) |
| Fixed 300 s per command | One flat ceiling everywhere; simple, but says nothing about how far past normal the stall went | |
| No kill — let it run and watch | Richest symptom capture, but an indefinite bench block — and an unlogged kill is what created the stray `~/.firestarter` | |

**User's choice:** "you decide."

**Notes:** Claude selected the scaled ceiling. W27C512 = 4 × 41.010 s ≈ 165 s. W29C020 baselines off
A1's control-arm figure (cell order supplies it for free), with a stated 600 s absolute fallback if
A1's own W29C020 never completes. The load-bearing half is that the kill is **logged** — numbered
log, full stdout/stderr, last progress frame — because Phase 160's single unlogged 120 s
shell-timeout kill produced the untraceable `~/.firestarter` contamination it had to carry forward.

---

## W29C020 first silicon

### Q5 — Should W29C020's first appearance (A1, control arm) be de-risked before the full 262144 B write?

| Option | Description | Selected |
|--------|-------------|----------|
| Cheap smoke check first | chip-id read + blank check on A1 control only, ~30 s; separates a seating/support fault from a write-path fault | ✓ (Claude) |
| Go straight to the full write | No special-casing; a seating fault shows up as a write failure and gets one re-seat under Standing rule 8 | |
| Smoke check on every cell's first W29C020 | Consistent per-cell de-risking, but adds a step to 3 of 12 positions and breaks positional symmetry | |

**User's choice:** "you decide."

**Notes:** Claude selected the one-time check. It buys the exact distinction the milestone exists to
make — "DIP32 mis-seated / not addressable on Rev 2.0" vs "the write path is broken" — for 30 s
instead of ~3 min of failed write plus an operator re-seat. Recorded as a bring-up datum in A1's
cell dir, **outside the P-01…P-11 step list**, so positional symmetry holds and no procedure
amendment is triggered. Putting it inside P-09 instead would require its own amendment, declared as
such. The blank check is the standalone command; `-b` / `--no-blank-check` is forbidden.

---

## Evidence row assembly

### Q6 — How should Phase 161's 12 evidence rows be produced?

| Option | Description | Selected |
|--------|-------------|----------|
| Build an append tool | `append_evidence.py` derives every machine field from provenance + verdict artifacts; the plan supplies only verdict prose and anomalies | ✓ |
| Hand-author, gate with `gate_record.py` | No new tooling and the gate is proven to fail closed — but it checks shape, not correctness | |
| Hand-author plus a cross-check | Catches transcription without a writer, though the diff script is most of the writer's work, somewhere nothing selftests | |

**User's choice:** Build an append tool.

**Notes:** Same argument Phase 160's D-13 used for `capture_provenance.py` — discharge the property
by mechanism, not by a transcriber's diligence. Trigger is measured: Phase 160's carry-forward list
records a plan-authoring defect that recurred **4×**, with the standing warning that 161–166 inherit
similarly-authored legs where one wrong constant is many false results. The tool must advertise
`--selftest` or `run_gates.sh`'s discovery step fails the whole suite.

### Q7 — P-11 says rows append at teardown; per-position durability conflicts with that. Which wins?

| Option | Description | Selected |
|--------|-------------|----------|
| Per-position — amend P-11 | Tool appends as each position completes; PROCEDURE.md gets Amendment 3 | ✓ (Claude) |
| At teardown — procedure unchanged | Four rows land atomically, no amendment — but a kill after position 3 loses the assembly work | |
| Per-position to a staging file | Durability without touching the step list, at the cost of a second record needing explanation and gating | |

**User's choice:** "You decide."

**Notes:** Claude selected per-position + Amendment 3. The staging file re-creates the exact failure
D-15 rejected when it declined per-cell JSON sidecars — a second record whose merge becomes a step
that can be got wrong. Holding to teardown lets `EVIDENCE.jsonl` silently lag the bench, which is
what its append-only design prevents. The append moves into P-07/P-09 and **P-11 becomes a
completeness assertion** so the cell-level guarantee survives. Amendment 3 lands before any real
sweep cell has run, so it will record that every cell ran under the new text.

---

## Wrap-up — two further gray areas

### Q8 — Decide the two newly-surfaced areas now, or hand them to research/planning?

| Option | Description | Selected |
|--------|-------------|----------|
| I'm ready for context | Write CONTEXT.md with the five decisions; hand both open items downstream | |
| Explore both | (1) uno328pb read-back ambiguity; (2) A3/B2's leave-state for Phase 162 | ✓ |
| Just the 328PB one | Decide the halt-risk one; leave the leave-state to planning | |

**User's choice:** Explore both.

---

## uno328pb read-back risk

### Q9 — The v1.33/328PB read-back is unproven and sits on the critical path. How should that risk be handled?

| Option | Description | Selected |
|--------|-------------|----------|
| Prove it before the sweep | Bare uno328pb, no shield, no chip; flash v1.33, judge, observe the match. ~3 min + one USB replug | ✓ |
| Classify as P-H2 — record and carry | Preserves momentum, but books an unresolved rig uncertainty as an A/B result | |
| Leave it as P-H1 and accept | Procedure-faithful and correct handling — at the most expensive possible moment | |

**User's choice:** Prove it before the sweep.

**Notes:** Surfaced by checking the actual verdicts rather than assuming. Both recorded 328PB
verdicts judge against the **control** hex span (26074 B): one match with control flashed, one
deliberate D-03 cross-flash mismatch with v133 flashed but control expected. The v1.33 arm's own
23000 B span has **never** been read back and matched on that board, and the `vector-exclusion`
policy (offsets 0 and 100) was derived live on the *control-arm* flash. Without the pre-proof, A2's
second arm is the first such confirmation — live, at cell 2 of 3, with A1 already spent, and P-04
names a mismatch on a correctly-flashed board as a **P-H1 halt**.

---

## A3/B2 leave-state

### Q10 — A3/B2 ends at P-09 with W29C020 in the socket. What does P-11 leave behind?

| Option | Description | Selected |
|--------|-------------|----------|
| W29C020 seated, state declared | Zero chip handling and zero pot work for Phase 162; W29C020 is one of its 11 parts and already at 12000 mV | |
| Socket empty, state declared | Electrically safest park; costs a handling step and gives 162 nothing to start from | |
| Swap back to W27C512 | The v1.31 reference part on this exact rig and a natural start for 162 — at the cost of one teardown swap | ✓ |

**User's choice:** Swap back to W27C512.

**Notes:** Leave-state is Leonardo, Rev 2.0, v1.33 arm, W27C512 seated, VPP 12.0 V. Claude took the
mechanical consequence: a cell-conditional clause in PROCEDURE.md would be the same shape as the
arm-conditional text the procedure forbids, so P-11 instead gains a general, cell-agnostic "declare
and record the leave-state" requirement (folded into Amendment 3), and A3/B2's actual value lives in
the plan, the cell record and the STATE.md SAFETY line.

---

## Claude's Discretion

Five questions answered "you decide", each resolved in CONTEXT.md with its rejected alternatives
recorded:

- **Q3 → D-07** — A2 runs all four positions on both arms.
- **Q4 → D-08** — ceilings scaled from measured healthy figures; the kill is logged.
- **Q5 → D-09** — one-time non-destructive smoke check on A1 control, outside the step list.
- **Q7 → D-06** — per-position append with Amendment 3; P-11 becomes a completeness check.
- **Q2 (partial) → D-03** — per-position record writes, since they require nothing of the operator.

Also decided mechanically without asking: **D-04** (run_gates.sh cadence — already designated by
Phase 160), **D-12** (leave-state requirement is cell-agnostic in the procedure, cell-specific in
the plan), and the todo disposition (27 matches, none folded — all product-code items, out of scope
for a phase that changes no product code; two belong to Phase 164).

## Deferred Ideas

- Fixing anything this phase finds — Phase 165, on the v1.33 PR branch.
- The stray `~/.firestarter` directory — accepted, disclosed, sandbox denies removal; do not retry.
- Sparse argv recording — disclosed at Phase 160's gate, not re-litigated.
- `BRINGUP-wrv`'s missing teardown `probe_board.py` re-run — Amendment 2 prevents recurrence; the
  gap is not backfilled.
- Program-window VPP/VCC under load — remains unmeasured; Phase 166's honesty ledger owns the
  non-claim.
- The `avrdude --detect-mcu` product deliverable — mechanism folded by Phase 160 D-14, todo stays
  pending.
- Phase 164's Modified Rev 0 photograph and `MODIFICATIONS.md` rework trace — surfaced in the todo
  scan, need the board cell B1 puts on the bench.
