# Phase 161: BOARD — Board Sweep, Three Boards on Rev 2.0 - Context

**Gathered:** 2026-08-27
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase produces **results**, not mechanism. Phase 160 built the rig; Phase 161 runs it.

It delivers exactly three cells on the Rev 2.0 shield — **A1** (Uno / ATmega328P), **A2**
(uno328pb / ATmega328PB) and **A3/B2** (Leonardo / ATmega32U4) — each running the **control arm
then the v1.33 arm**, each arm against **W27C512** (65536 B) then **W29C020** (262144 B). That is
**12 evidence positions**, each holding a full-device read-back SHA verdict or a *named* reason for
its absence, each carrying its RIG-02 provenance block captured before the cell's first test step,
and each recording a measured write duration.

`.planning/v1.34/PROCEDURE.md` is executed **unchanged** (except for the one declared amendment in
D-05/D-09 below, which lands before any real sweep cell runs). Every cell cites its step ids rather
than re-describing the run.

**A3/B2 is executed exactly once in this milestone, here.** Phase 163 cites its rows and never
re-runs them. Its teardown hands the standing rig to Phase 162.

**This phase changes no product code.** Not firmware, not the host app — both submodules stay
byte-unchanged. The milestone lists "any product-code change not traced to a v1.33-caused
regression" as Out of Scope, and Phase 161 discovers regressions; it does not fix them. RCA and
fixes are Phase 165's, and land on the v1.33 PR branch. A plan that finds itself needing a source
edit in either sub-repo must stop and report.

**Everything Phase 160 locked stays locked.** The planner does not re-open: the P-01…P-11 step
list; arm order (control first — so the control arm never inherits the other arm's chip contents);
the single pot setting per cell (both bench chips declare `vpp_mv: 12000`); the oracle (full-device
SHA against the written image, never an exit code; N=3 on v1.33 always, control escalating to N=3
only where v1.33's three reads disagreed); the 12 pre-computed images in `bench/IMAGE-PLAN.json`;
the `EVIDENCE.jsonl` `_schema` row; the two-state cell outcome taxonomy; the forbidden-invocation
table; or the write-duration definition.

**The measured fact that shapes this phase's risk:** both arms are indistinguishable in every
self-reported identity string — firmware `3.0.0b22` and app `3.0.0b32` on *both*. The arm exists in
exactly two places: the **invoked binary path** and the **on-device read-back**. Nothing else on the
wire can tell them apart.

</domain>

<decisions>
## Implementation Decisions

### Plan decomposition & operator handovers

- **D-01:** **Three plans, one per cell** — `A1`, `A2`, `A3/B2`, each running `P-01`→`P-11`
  end-to-end across both arms and both chips. *(User's choice.)* Rejected: one plan per cell-arm
  (6) and one plan per position (12–15) — both cut the blast radius of a bad verify-leg constant,
  but both multiply handovers, which is the property D-02 optimises for.

- **D-02:** **No handover until a real physical action is needed.** *(User's explicit instruction,
  verbatim: "I dont want any handover until a real physical action is needed.")* The executor stops
  **only** at the procedure's genuinely operator-performed steps — `P-01` (mount + declare
  silkscreen), `P-03` (Uno-class chip-out), `P-05` (seat chip 1), `P-06` (pot adjust), `P-08` (swap
  to chip 2) — and their repeats across the arm switch at `P-10`. Everything between those is one
  continuous run. **No artificial park prompts, no "continue?" checkpoints, no confirmation gates
  that do not correspond to the operator physically touching the rig.**

  A planner authoring `human-verify` checkpoints anywhere other than those steps is violating this
  decision. Cell boundaries are themselves physical actions (the Rev 2.0 shield moves to a different
  board), so they are already natural stops and need no additional gate.

- **D-03:** **Records are still written per position — that is not a handover.** Decided
  mechanically, not asked. Each position's `provenance.json`, `WRV-VERDICT.json` and
  `EVIDENCE.jsonl` row are written as that position completes, so a kill mid-cell leaves a
  consistent record and a resumable state. This requires nothing from the operator and therefore
  does not conflict with D-02.

- **D-04:** **`bash .planning/v1.34/tools/run_gates.sh` is the per-cell gate.** Decided
  mechanically — Phase 160 designated it the standing per-wave gate for 161–166, and D-01 makes a
  wave equal a cell. **Measure its exit code directly, never through a pipe.**

### Evidence row production

- **D-05:** **Build a phase-owned `append_evidence.py`.** *(User's choice.)* It reads
  `provenance_<position>.json`, `WRV-VERDICT.json` and `READBACK-VERDICT.json` and **derives every
  machine-readable field itself** — never transcribed. The plan supplies only the genuinely human
  fields (`verdict` prose, `anomalies`). This is D-13's own argument applied one layer out: RIG-05's
  "zero fields sourced from session memory" was discharged by `capture_provenance.py` being a
  mechanism rather than a transcriber's discipline; the evidence row deserves the same treatment.

  The trigger is measured, not hypothetical. `capture_provenance.py:43` states rows are "assembled
  by each plan's own inline evidence-append" — 12 rows × ~40 fields hand-authored. Phase 160's own
  carry-forward list records a **plan-authoring defect that recurred 4×** (hardcoded arm-agnostic
  constants in `<automated>` verify legs, plans 08/09/10/12), each caught only in flight, with the
  standing warning that 161–166 inherit similarly-authored legs "where one wrong constant is twenty
  false results."

  Rejected: hand-authoring gated by `gate_record.py` alone (the gate checks **shape and domain, not
  correctness** — a field transcribed from the wrong position's provenance passes every check it
  makes); and hand-authoring plus a re-derivation cross-check (the diff script is most of the
  writer's work, done somewhere nothing selftests).

  **Constraint:** `run_gates.sh` discovers every `*.py` under `tools/` and **fails the suite** if
  one does not advertise `--selftest`. `append_evidence.py` must ship with one.

- **D-06:** **Rows append per position, not at teardown — `PROCEDURE.md` Amendment 3.** *(Claude's
  call — the user answered "You decide".)* The append moves into `P-07`/`P-09`, and **`P-11` becomes
  a completeness assertion** ("all four of this cell's rows are present in `EVIDENCE.jsonl`") rather
  than a writer — so the cell-level guarantee survives the change.

  Rejected: appending at `P-11` as currently written (a kill after position 3 loses all four rows'
  assembly, and `EVIDENCE.jsonl` silently lags the bench, which is what D-15's append-only design
  exists to prevent); and a per-cell staging file merged at `P-11` (re-creates the exact failure
  D-15 rejected when it declined per-cell JSON sidecars — a second record whose merge into the
  canonical one becomes a step that can be got wrong).

  **Amendment 3 lands in the cleanest possible window: no real sweep cell has run yet**, so it will
  record that every cell (`A1`/`A2`/`A3-B2`/`B1`/`B3`) ran under the new text. It must follow the
  established amendment shape — (a) what changed, (b) why, (c) which cells ran under which text —
  and the `render_steps.py --arm control` vs `--arm v133` empty-diff gate must be re-confirmed after
  the edit. The new text carries no `$ARM_BIN` token, so the gate should stay empty.

### Cell A2 (uno328pb) — the expected-failure cell

- **D-07:** **A2 runs all four positions on both arms.** *(Claude's call — the user answered "you
  decide".)* If the W27C512 write fails as Backlog 999.2 predicts, the chip is still swapped and
  W29C020 is still written, on **both** arms.

  Rationale: 999.2's brownout was observed on a **27C-family program** — pulsed high-VPP. W29C020 is
  **algorithm 5**, a 5 V page-write EEPROM with auto-erase — a materially different electrical
  situation that **has never been tried on this board**. SC#3 forbids asserting the W27C512 failure
  from the backlog rather than observing it; extending that same unobserved assumption to a chip
  nobody has run would be a weaker claim, not a safer one. Cost is two operator swaps and ~20 min.

  SC#3's own clause governs the upside: if W29C020 (or W27C512) **completes** on uno328pb on either
  arm, that is recorded as an observation against 999.2, **not discarded as noise**.

  Rejected: stopping the arm at first failure (SC#1 permits a named absence, but "we chose not to
  run it" is a weak name and produces zero comparative information); and running W29C020 on the
  v1.33 arm only (breaks the A/B symmetry that is this milestone's entire deliverable, leaving a
  v1.33 result with no control).

- **D-08:** **A stalled write is killed at a ceiling derived from a measured healthy figure, and
  the kill is logged.** *(Claude's call — the user answered "you decide".)*

  - **W27C512 ceiling = 4× its measured healthy write = ~165 s** (measured: 41.010 s wall-clock,
    37.48 s app-reported — `bench/cells/BRINGUP-wrv/WRITE.md`).
  - **W29C020 ceiling = 4× A1's control-arm W29C020 wall-clock.** The cell order supplies this for
    free: A1 runs before A2. **Fallback if A1's own W29C020 never completes: a stated absolute of
    600 s**, recorded as a fallback rather than a derivation.
  - The kill runs under a **numbered log** with full stdout/stderr and the **last progress frame**
    captured, and is recorded as `timed out at N s against a measured baseline of M s`.

  The logging half is the load-bearing half. Phase 160's single **unlogged** shell-timeout kill (a
  120 s cut during plan 11's `vpp` invocation) is exactly what produced the untraceable
  `~/.firestarter` contamination that phase had to carry forward as an open item. An arbitrary
  fixed ceiling was rejected because it says nothing about how far past normal a stall went; letting
  a hang run unbounded was rejected because it blocks the bench indefinitely and is what went wrong
  before.

  Note for the planner: **write-progress emission is time-keyed per block, and the clock restarts
  each block**, so there are zero intra-block frames — the last frame names the block, not a
  byte offset.

### W29C020 — first silicon in this milestone

- **D-09:** **A one-time, non-destructive smoke check before A1's control-arm W29C020 write.**
  *(Claude's call — the user answered "you decide".)* A chip-id read plus a blank check (~30 s),
  **on A1's control arm only**, before the first full 262144 B write in this milestone's history.

  Rationale: it buys the exact distinction this milestone exists to make cleanly — "DIP32 mis-seated
  / pin-1 wrong / part not addressable on Rev 2.0" versus "the write path is broken" — for 30 s,
  instead of ~3 min of failed write plus an operator re-seat. W29C020 has run **only against
  `judge_wrv.py`'s fixture**; `BRINGUP-wrv` proved 65536 B on silicon and nothing has ever proved
  262144 B.

  **Recorded as a bring-up datum in A1's cell dir, outside the `P-01`…`P-11` step list** — so
  positional symmetry across the 12 holds and no procedure amendment is triggered. If the planner
  instead wants it *inside* `P-09`, that is a step-list change and must be declared as its own
  amendment, not folded silently.

  Rejected: going straight to the full write (a seating fault then costs a failed write and a
  re-seat to diagnose); and smoke-checking every cell's first W29C020 (adds a step to 3 of 12
  positions, breaking positional symmetry, to catch a board-specific DIP32 problem the A1 check
  already makes recognisable).

  **Flag discipline:** the blank check is the standalone command. `-b` / `--no-blank-check` is on
  the forbidden list and must not appear. A not-blank result is a perfectly good outcome here — it
  still proves addressability.

### The uno328pb v1.33 read-back — de-risked off the critical path

- **D-10:** **Prove the v1.33-arm read-back on uno328pb before the sweep starts.** *(User's
  choice.)* Plug in the **bare uno328pb** — no shield, no chip, so the Uno-class chip-out rule is
  satisfied trivially — flash the v1.33 arm, run `judge_readback.py`, and **observe the match**.
  ~3 min and one USB replug, executed before A1's cell.

  **The measured gap this closes:** a v1.33 flash on uno328pb has **never produced a judged match**.
  Both recorded 328PB verdicts judge against the **control** hex span (26074 B) —
  `BRINGUP-uno328pb/READBACK-VERDICT.json` (`flashed_arm: control`, `expect_arm: control`,
  `judged_match: true`) and `BRINGUP-uno328pb/crossflash/READBACK-VERDICT.json` (`flashed_arm:
  v133`, `expect_arm: control`, `judged_match: false`, the deliberate D-03 cross-flash). The v1.33
  arm's own **23000 B** span has never been read back and matched on that board, and the
  `vector-exclusion` policy (offsets 0 and 100) was derived live **on the control-arm flash**.

  So A2's second arm would otherwise be the first time `judge_readback.py` is asked to confirm a
  v1.33 flash on a 328PB — live, at cell 2 of 3, with A1 already spent. `P-04`'s own wording names
  "a read-back mismatch on a board that was correctly flashed" as a **P-H1 halt**. If the exclusion
  policy does not transfer, this pre-proof surfaces it as bring-up rig work fixable in-phase.

  Rejected: pre-classifying a 328PB read-back mismatch as **P-H2** (books an unresolved *rig*
  uncertainty as if it were an A/B *result*, forcing Phase 165 to disentangle "policy didn't
  transfer" from "v1.33 broke the flash"); and leaving it as **P-H1** and accepting the risk
  (correct handling, at the most expensive possible moment).

  Record this as a bring-up position in its own cell dir, not as one of the 12 sweep positions.

### A3/B2 teardown & the handoff to Phase 162

- **D-11:** **A3/B2's leave-state is: Leonardo, Rev 2.0, v1.33 arm, `W27C512` seated, VPP 12.0 V.**
  *(User's choice.)* The cell ends at `P-09` with the DIP32 W29C020 in the socket, so `P-11` adds
  one operator swap back to the 28-pin part. W27C512 is the **v1.31 reference part on this exact
  rig** and a natural place for Phase 162's 11-part sweep to start.

  Arm order already delivers the rest of what Phase 162 requires — "no reconfiguration and no
  re-flash", with the rig **already carrying the v1.33 arm** — because v1.33 runs second by D-05 of
  Phase 160 / `P-10`.

- **D-12:** **The leave-state requirement goes into `PROCEDURE.md` cell-**agnostically**; the value
  goes in the plan.** Decided mechanically. A "swap back to W27C512 at teardown" clause that applies
  only to A3/B2 would be **cell-conditional text — the same shape as the arm-conditional text the
  procedure explicitly forbids**. Instead: `P-11` gains a general *"declare and record the
  leave-state (board, port, arm, chip seated, pot, shield)"* requirement, folded into **Amendment 3**
  alongside D-06's append change; A3/B2's actual value is specified in Phase 161's plan and written
  into the cell record and the STATE.md SAFETY line.

  Phase 160 established the STATE.md SAFETY-line convention and Phase 161 continues it: the line
  names the attached board, the seated chip, and what operations are consequently unsafe.

### Claude's Discretion

The user answered **"you decide"** on five questions; D-06, D-07, D-08, D-09 and D-10's *rejected
alternatives* record what was weighed. The planner may revisit these on evidence, but not on
preference:

- **D-07 (A2 runs all 4):** if A2's W27C512 failure turns out to physically damage or endanger the
  W29C020 (e.g. the brownout leaves a rail in a state that is unsafe for a 32-pin part), stop and
  report; safety outranks coverage. Nothing currently on the record suggests this.
- **D-08 (ceilings):** the 4× multiple is a judgment call, not a measurement. If A1's healthy
  figures show high variance, widen it and **state the widening**, do not silently exceed it.
- **D-09 (smoke check):** the exact commands are left to research/planning; the locked property is
  that it is **non-destructive, once, on A1 control, outside the step list**.
- **D-10 (pre-proof):** if the bare 328PB cannot be flashed without the shield for some reason not
  currently known, the pre-proof still happens with the shield mounted and the chip out; the locked
  property is that it happens **before A1**, not what it is mounted on.

Still open and left to research/planning:

- The concrete `append_evidence.py` interface (arguments, where the human fields enter, how it
  refuses an incomplete position) — D-05 locks the property, not the CLI.
- W29C020's read-set duration budget. The only measured read figure is `BRINGUP-wrv`'s **53.437 s**
  for a 3-run 65536 B set on Uno + Rev 2.0. 262144 B is 4× the bytes; the planner should measure
  rather than extrapolate, and A1 is where that measurement first exists.
- Whether A1's opening sequence needs anything beyond the obvious. The rig is currently left on the
  **v1.33** arm with a chip **seated**, but A1 must start on **control** — so A1 opens with a
  chip-out and a re-flash to control. That is `P-03`→`P-04` run normally, not a special case.

### Reviewed Todos (not folded)

`todo.match-phase 161` returned **27 matches; none were folded.** Every match is a product-code item
(firmware or host app), and this phase changes no product code — the milestone lists that as Out of
Scope. The matches are keyword coincidences on `write`, `read`, `chip`, `shield`, `phase`, not scope
overlaps.

Two matches are genuinely in this milestone but belong to **Phase 164**, not here:
`photograph-operator-modified-rev0-board` and `write-full-modifications-md-rework-trace`. Both are
REV0-01…03 work and both require the Modified Rev 0 board, which Phase 163's cell B1 puts on the
bench.

`avrdude-mcu-detection-fallback` was already folded **as mechanism only** by Phase 160 D-14 and
stays `pending` for its product deliverable. It is not re-folded here.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### The rig — binding, produced by Phase 160

- `.planning/v1.34/PROCEDURE.md` — **the** document this phase executes. Steps `P-01`…`P-11`, halt
  policy `P-H1`/`P-H2`, 9 standing bench rules, the outcome taxonomy, the write-duration definition,
  the forbidden-invocation table, the recording discipline, and Amendments 1–2. Amendment 3 is
  authored by this phase (D-06, D-12).
- `.planning/v1.34/rig-pins.json` — arm binary paths, per-target avrdude/programmer/judged-span
  policy, `hex_span_expected_by_arm` (**use this, never the legacy scalar `hex_span_expected`**),
  chip sizes/VPP/stamp widths, `forbidden_flags`, `forbidden_argv0`, the frozen `config_dir`.
- `.planning/v1.34/bench/IMAGE-PLAN.json` — the 21 positions' `mask` / `stamp_width` / `sha256`.
  Phase 161 uses the 12 rows whose `cell_id` is `A1`, `A2` or `A3-B2`. Also carries the
  `artifact_volume_policy`, including the **commit-on-failure exception** (a non-clean position's
  `run_*.bin` **and** `written.bin` are committed with `git add -f`).
- `.planning/v1.34/bench/EVIDENCE.jsonl` — canonical, append-only. Line 1 is the `_schema` header
  pinning `locked_columns` (9) and `evid_extension_columns` (31). **`EVIDENCE.md` is rendered from
  it and never hand-edited.**
- `.planning/v1.34/tools/` — `run_gates.sh` (the per-cell gate; **exit code measured directly, never
  through a pipe**), `capture_provenance.py`, `judge_readback.py`, `judge_wrv.py`, `probe_board.py`,
  `gen_addr_image.py`, `gate_record.py`, `render_evidence.py`, `render_steps.py`, `check_arms.py`,
  `check_rebuild.py`, `touch_1200.py`.
- `.planning/v1.34/images/` — the six committed `.hex` files + `SHA256SUMS.txt` (D-04).
- `.planning/v1.34/PHASE-160-GATE.md` §6 — the six accepted carry-forward limits. **These are
  disclosed, not new gaps; do not re-raise them as findings.**

### Phase 160's own decisions (the ones this phase inherits, not re-opens)

- `.planning/phases/160-rig-dual-arm-build-flash-provenance-the-shared-cell-procedur/160-CONTEXT.md`
  — D-01…D-18. Especially **D-01/D-02** (read-back proof, judged span vs whole-flash), **D-05**
  (the proof runs at *every* cell's flash), **D-10/D-11** (the oracle and the N=3 asymmetry),
  **D-12** (distinct address-attributable image per position — the decision most load-bearing
  against a false green), **D-15** (JSONL canonical), **D-18** (the two-axis outcome taxonomy).
- `.planning/phases/160-.../160-VERIFICATION.md` §"Known, Previously-Disclosed Limits" — the same
  six items, confirmed present in the record.
- `.planning/v1.34/bench/cells/BRINGUP-wrv/` — the **worked example** of a complete position:
  `WRITE.md`, `WRV-VERDICT.json`, `provenance.json`, `logs/00`…`13`, and the `RECONSTRUCTION.md` /
  `RECONSTRUCTION-DIFF.md` pair from the D-17 fresh-context test.
- `.planning/v1.34/bench/cells/BRINGUP-uno328pb/READBACK-VERDICT.json` and
  `crossflash/READBACK-VERDICT.json` — the two verdicts that establish D-10's measured gap.

### Milestone definition (binding)

- `.planning/ROADMAP.md` §"v1.34 — Pre-Merge Hardware Regression Validation" — the five-cell matrix,
  the control-arm SHAs, the failure policy, the declared known faults, the merge posture, the branch
  model.
- `.planning/ROADMAP.md` §"Phase 161" — the goal and **Success Criteria 1–5**, which this phase is
  measured against.
- `.planning/ROADMAP.md` §"Phase 162" — what A3/B2's teardown must hand over (D-11).
- `.planning/REQUIREMENTS.md` — **BOARD-01…04** (lines 43–46) and the Out-of-Scope list.

### Prior art and precedent

- `.planning/phases/145-bench-validation/145-BENCH-LOG.md` — v1.31's bench record. Source of the
  **0.37 s** figure SC#4 names: it is the **spread (max − min) across three app-reported,
  success-only write figures** (106.06 / 105.69 / 106.06 s), **not a duration** — the non-claim is
  already written into `PROCEDURE.md`'s write-duration section and must be carried, not re-derived.
- `.planning/v1.15/bench/EVIDENCE.json`, `.planning/v1.18/bench/EVIDENCE.json` — where
  `locked_columns` comes from, byte-identical in both.
- Backlog **999.2** (`.planning/phases/999.2-uno328pb-program-path-brownout-hang/`) — A2's expected
  failure, which D-07 requires be **observed, not asserted**.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **The entire rig is the reusable asset.** Twelve tools behind one gate
  (`bash .planning/v1.34/tools/run_gates.sh`, 11/11 selftests + 5/5 live gates, proven to fail
  closed with exit 1). Phase 161 adds exactly one tool (`append_evidence.py`, D-05) and one
  procedure amendment (D-06/D-12). It builds nothing else.
- `capture_provenance.py` — takes `--cell-id --position-id --arm --target --port --chip
  --shield-rev`; **hard-refuses without the position's read-back verdict**, and **refuses to run
  without an operator-declared shield revision**. Gained `image_mask` / `image_stamp_width` /
  `image_sha` plus a `--patch-image-plan` retrofit during 160-13's reconstruction rounds.
- `gate_record.py` — `--cell <provenance.json>` or `--jsonl <EVIDENCE.jsonl>`; enforces field
  presence, the `"not measured — <reason>"` shape as a valid non-null, the two-state cell-outcome
  domain, and rejects forbidden flags by exact token match anywhere in a recorded argv.
- `judge_readback.py` — runs its own avrdude read with **`-A` explicit** (without it the read-back
  truncates), normalises the flashed arm's `.hex` with the pinned `avr-objcopy`, judges the
  `[0, hex_span)` prefix under the target's `judged_span_policy`.
- `judge_wrv.py` — SHA-256 over the full device size against the **written image**; records the
  app's own 0/1/2 separately as `app_verdict_unjudged` with a `verdict_disagreement` cross-check
  that never substitutes one for the other.

### Established Patterns

- **The judged verdict and the unjudged verdict are recorded separately, and their disagreement is
  itself a finding** — never resolved by preferring one. Applies to `judge_readback.py`'s
  judged-span-vs-whole-flash pair and `judge_wrv.py`'s SHA-vs-app pair alike.
- **A negative control is recorded as having FIRED, not as having been configured.**
- **Nothing is fabricated.** A blocked reading is recorded as `"not measured — <reason>"` on the
  same line, never as a blank. `gate_record.py` treats that exact shape as a valid non-null.
- **No SHA is ever transcribed by hand** — computed by a tool and written by that tool. D-05 extends
  this rule from provenance fields to the evidence row.
- **A wrong record is marked SUPERSEDED and kept visible, never erased** (Phase 160's false shield
  declaration set this precedent).
- **One clean re-seat per position is allowed** (Standing bench rule 8) — **both** the discarded
  attempt and the re-run are recorded.

### Integration Points

- **Measured facts 161 inherits — do not re-derive.** Per-env avrdude: `uno` → 6.3 (`arduino`),
  `uno328pb` → **8.1** (`urclock`), `leonardo` → 6.3 (`avr109`). No override of PlatformIO's
  resolution is needed on any target, and 6.3 in a uno/leonardo log is **not** a forbidden-binary
  violation — `forbidden_binaries` governs the rig's own direct invocations.
- **Node classes differ and the name is not a discriminator.** uno328pb is a **CH340**
  (`1a86:7523`) → `/dev/ttyUSB0`; Uno and Leonardo → `/dev/ttyACM0`, the *same name*,
  distinguishable only by node creation time. **Always re-probe the signature**: `atmega328p`
  `0x1e950f`, `atmega328pb` `0x1e9516`, `atmega32u4` `0x1e9587`.
- **Leonardo's 1200-baud touch returns the SAME node, never a new one.** Use bare `touch_1200.py`
  (settle-only, reuse `--port`); `--wait-new-port` was **empirically refuted** — it polls for a node
  this board never produces and burned ~5.27 s of the ~8 s Caterina window. PlatformIO's
  `leonardo.json` owns the touch on the *flash* path; `touch_1200.py` is only for the direct-avrdude
  *read-back*.
- **Hex spans are arm-dependent.** control/v133: uno 26026/22952 · uno328pb 26074/23000 · leonardo
  28170/25098. Control is larger because PR#55's VPE-settle amortisation added bytes with its
  `size_baseline.json` re-record deliberately deferred.
- **`FIRESTARTER_CONFIG_DIR` is set inline on every arm-invoking command, never exported.**
  `config.py` computes `HOME_PATH`/`DATABASE_FILE`/`PIN_MAP_FILE` as **import-time** constants, so a
  session-level export is a partial fix that *looks* complete. A shell `FOO=bar cmd` prefix is
  stripped before exec and **never reaches argv**, so an argv check can never detect a missing
  prefix — **asserting `~/.firestarter` absent at per-cell teardown is the only detector.**
- **`pio` runs only with cwd `/workspaces/firestarter`.** The generated, gitignored
  `/workspaces/platformio.ini` has a duplicate `[platformio]` section that makes `configparser`
  abort — the identical command string succeeds or fails on cwd alone.
- **Every `import firestarter` probe needs `python -P`** — `/workspaces/firestarter` (the firmware
  repo) wins as a PEP 420 namespace portion and the probe silently prints `None` without it.

</code_context>

<specifics>
## Specific Ideas

- **"I dont want any handover until a real physical action is needed."** This is the strongest
  steer in the discussion and it governs plan authoring directly. `human-verify` checkpoints belong
  at `P-01`, `P-03`, `P-05`, `P-06`, `P-08` and nowhere else.
- The measured baselines the planner should anchor on rather than guess: **W27C512 write 41.010 s
  wall / 37.48 s app-reported**, **3-run read set 53.437 s** — both on Uno + Rev 2.0, v1.33 arm,
  from `BRINGUP-wrv`.
- **Read every `<automated>` verify leg before trusting it.** Phase 160's carry-forward warning is
  explicit: the hardcoded-arm-agnostic-constant defect recurred **four times**, and 161 spans twelve
  positions where one wrong constant is twelve false results. `hex_span_expected_by_arm` exists
  because of it.
- **This procedure must not run under `--auto` / `--chain` / any auto-advance mode** (Standing bench
  rule 7). Those auto-approve the `human-verify` checkpoints every physical step depends on;
  `autonomous: false` on a plan is not self-protecting against that.

</specifics>

<deferred>
## Deferred Ideas

- **Fixing anything this phase finds.** Regressions are classified and fixed in **Phase 165**, on
  the **v1.33 PR branch**, not here and not on v1.34's branch. Phase 161 records; it does not repair.
- **The `~/.firestarter` stray directory** (created 07:59:25, holding `{"port": "/dev/ttyACM0"}`).
  Carried forward from Phase 160 as an accepted, disclosed limit — the sandbox denies deleting it.
  **Do not attempt removal again.** Its only role here is as the per-cell teardown detector
  (D-12's config-dir check): if it *changes*, that is a `P-H1` finding.
- **Sparse argv recording.** RIG-05's "recorded command line" property holds for the invocations
  `provenance.json` itself carries, not as a general property of every logged step. Disclosed at
  Phase 160's gate; not re-litigated here.
- **`BRINGUP-wrv`'s missing teardown `probe_board.py` re-run.** Amendment 2 added the command so it
  cannot recur; that cell's gap is recorded, not backfilled.
- **Program-window VPP/VCC under load** stays unmeasured — the DTR-reset-on-close tooling gap
  stands, and Phase 166's honesty ledger already owns the resulting non-claim. v1.34 makes **no
  electrical claim**.
- **The `avrdude --detect-mcu` product deliverable.** Phase 160 folded the *mechanism* only (D-14);
  the todo stays `pending` and the host-side flag is not built here.
- **Phase 164's Modified Rev 0 work** — the board photograph and the `MODIFICATIONS.md` rework
  trace. Both surfaced in this phase's todo scan; both need the board Phase 163's cell B1 puts on
  the bench.

### Reviewed Todos (not folded)

All 27 `todo.match-phase 161` results were reviewed and none folded — see the "Reviewed Todos"
subsection under `<decisions>` for the reasoning and the two Phase-164-bound exceptions.

</deferred>

---

*Phase: 161-board-board-sweep-three-boards-on-rev-2-0*
*Context gathered: 2026-08-27*
