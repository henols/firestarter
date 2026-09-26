# Phase 162: CHIP — 11-Part `dev test` Sweep on the Reference Rig - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-27
**Phase:** 162-chip-11-part-dev-test-sweep-on-the-reference-rig
**Areas discussed:** Divergence rule (SC#3/#4), Procedure + evidence shape, VPP pot policy per part, UV parts + run depth

---

## Area selection

| Option | Description | Selected |
|--------|-------------|----------|
| Divergence rule (SC#3/#4) | What counts as `same` vs `diverges: <how>`; v1.15 holds four dispositions per part and `dev test` is a fifth kind of operation | ✓ |
| Procedure + evidence shape | PROCEDURE.md is WRV-shaped; EVIDENCE.jsonl is pinned at 20 WRV positions | ✓ |
| VPP pot policy per part | 12 V / 13 V / 25 V split against the +7.5% ratiometric ADC error | ✓ |
| UV parts + run depth | Three irrecoverable UV slot writes; 2-cycle vs `--fast` on the 512 KiB parts | ✓ |

**User's choice:** all four.

---

## Divergence rule (SC#3/#4)

### Q1 — What does "the recorded v1.15 disposition" resolve to?

| Option | Description | Selected |
|--------|-------------|----------|
| Write-path headline, read as fallback | Strongest v1.15 write-path statement, P81 read only for parts never written | |
| All four cited, headline drives divergence | Row cites every sweep that touched the part; divergence keyed on the write-path headline | *(Claude's pick)* |
| Per-operation disposition set | A disposition per op, each sourced to the sweep that measured it | |
| You decide | | ✓ |

**User's choice:** "You decide."
**Notes:** Claude chose the all-sweeps-cited option (D-01). Rationale recorded: citing every sweep costs a table column and discharges SC#3's "no unsourced disposition" and SC#5's "cited inline in their own row" together. Per-operation was rejected because v1.15 measured `erase` and `blank-check` for essentially nothing, so it would manufacture divergences out of absent data — and under SC#4 each divergence costs a real chip swap.

### Q2 — What counts as `diverges`?

| Option | Description | Selected |
|--------|-------------|----------|
| Any comparable per-step flip | Per-step verdicts compared wherever the prior sweep measured that op; column names step and direction | ✓ |
| Overall exit code only | Map exit 0/1/2 against the headline | |
| Write-path outcome only | Diverge only when write/verify changed state | |
| You decide | | |

**Notes:** Exit-code-only was rejected in the option text on a concrete failure: exit code is a `max()` over steps, so a newly-broken `write` on a part that already fails `erase` still exits 1 and reads as "same FAIL as v1.15".

### Q3 — What does a row read when there is no comparable prior disposition?

| Option | Description | Selected |
|--------|-------------|----------|
| `diverges: no comparable baseline` — control arm becomes the baseline | Keeps SC#3's two values; the control re-run supplies the missing baseline | ✓ |
| `same` unless the run is bad | Clean run with no contradiction records `same` | |
| Add a documented third value | `no-baseline: <why>` plus a declared SC#3 deviation | |
| You decide | | |

**Notes:** Four rows were identified as affected during the discussion — W29C040 (boot-block carve-out changes the region), FM1608 (v1.15 used the now-forbidden `write -b`), ST M27C512 (16 B @0x0000 vs a masked 256 B top slot), and 2516 (write DEFERRED). The 2516 later dropped out of the sweep entirely (see D-14), and AM27C020 was added as an unresolved candidate once the v1.18 supersession surfaced.

### Q4 — Which baseline, given AM27C020's disposition is v1.18's?

| Option | Description | Selected |
|--------|-------------|----------|
| Most recent recorded disposition, v1.15 as the floor | Row names the milestone its baseline came from | ✓ |
| Literal v1.15 only | Supersession recorded in anomalies | |
| Both columns | v1.15 column plus a superseding column | |
| You decide | | |

**Notes:** Raised by Claude mid-area after tracing the `write#1 60/64, write#2 0/64` figures the roadmap attributes to v1.15 — they are v1.18's, from Phases 97–99, which shipped a `DIP32_27C020` + `rw-pin:[31]` fix that refuted v1.15's 0-bits signature. `.planning/v1.18/bench/EVIDENCE.json` covers only AM27C020 and W27C512, so the supersession is narrow but lands on an SC#5 known-carried part. Recorded as a deliberate stated interpretation of SC#3 rather than a silent one.

### Q5 — Same verdict, different symptom?

| Option | Description | Selected |
|--------|-------------|----------|
| Symptom-identity counts, but only where the record calls it deterministic | W27E512/W27E040/W29C040 diverge on a moved symptom; AM27C020 and 2516 do not | ✓ |
| Verdict only, symptom recorded but never triggers | | |
| Symptom-identity counts everywhere | | |
| You decide | | |

**Notes:** The user chose "More questions" at the area checkpoint specifically to reach this one.

---

## Procedure + evidence shape

### Q1 — How does Phase 162 relate to PROCEDURE.md?

| Option | Description | Selected |
|--------|-------------|----------|
| Amendment 4 — a parallel `C-01…C-NN` list in the same file | Shares `P-01`/`P-02`/`P-04`/`P-06`/`P-11` by reference | ✓ |
| A separate `.planning/v1.34/CHIP-PROCEDURE.md` | New document citing the standing rules | |
| Cite the applicable subset only, no new step list | Steps live in plan files | |
| You decide | | |

**Notes:** The tension was surfaced by reading PROCEDURE.md §Scope, which defines a cell as two arms × two bench chips while claiming to be "executed unchanged by Phases 161, 162 and 163". Amendment 4 must correct §Scope as well as add the list, and re-confirm the `render_steps.py` empty-diff gate afterwards.

### Q2 — Where do the chip-sweep results live?

| Option | Description | Selected |
|--------|-------------|----------|
| Sibling `bench/CHIP-EVIDENCE.jsonl` with its own `_schema` | Same 9 `locked_columns` core, chip-specific extension list | ✓ |
| Same EVIDENCE.jsonl behind a `CHIP-` prefix exclusion | Mirrors the `BRINGUP-` mechanism | |
| Markdown table only | Prose plus the saved `dev test` JSON artifacts | |
| You decide | | |

**Notes:** Three concrete obstacles were established before asking: `position_count_expected: 20`, a `close01_counting_rule` over every non-`BRINGUP-` row, and `gate_record.py` rejecting keys outside the two lists — where all 31 extension columns are WRV artifacts. The 9 locked columns do map cleanly, which is what made the sibling viable.

### Q3 — What tooling gets built?

| Option | Description | Selected |
|--------|-------------|----------|
| `append_chip_evidence.py` + `render_chip_evidence.py`, artifact copy-out in the appender | Derives every machine field; copies the fixed-path report before it can be overwritten | ✓ |
| Extend `append_evidence.py` with a chip mode | One tool, one selftest | |
| Appender only, render on demand | | |
| You decide | | |

**Notes:** Extends Phase 161 D-05's derive-never-transcribe argument. The overwrite hazard is real and specific: the report path is a fixed `dev-test-<chip>.json`, so the control re-run destroys the v1.33 report. `run_gates.sh` fails the suite if any `tools/*.py` lacks `--selftest`, taking it from 12/12 to 14/14.

### Q4 — The `gh` dedup query

| Option | Description | Selected |
|--------|-------------|----------|
| Allow, declare it, prove nothing was filed | Issue-count before/after as CLOSE-04's pasted command output | ✓ |
| Neutralize by shadowing `gh` on PATH | Zero network, degraded branch | |
| Allow, but no extra proof | Cite the code | |
| You decide | | |

**Notes:** Verified live rather than assumed — `sys.stdin.isatty()` is False under the executor's shell; `find_prior_report_fn` runs at `submit.py:683`, before the TTY branch at `:685`; off-TTY the function prints the URL and returns without reaching `submit_via_gh` or `comment_via_gh`. `submit.py` differs 105 lines between the arms, which is the argument against suppressing the path.

**Area checkpoint:** user chose "Next area", declining a further question about whether SC#2's `fw_board_identity` check needs a pre-flight. Claude took that as discretion and made it a pre-flight anyway (see Claude's Discretion).

---

## VPP pot policy per part

### Q1 — How is the pot set across the sweep?

| Option | Description | Selected |
|--------|-------------|----------|
| Two settings: 12 V as-is, one raised session for the 13 V pair | | |
| One setting for the whole sweep | | |
| Per-part setting from the multimeter | Each part gets its own metered real-rail figure | ✓ |
| You decide | | |

**Notes:** Claude's option text flagged that per-part collapses for two groups (a real 13 V rail reads ~13.98 V and hard-ERRORs; the shield cannot reach 25 V); the user selected it with that caveat visible. Accepted as their decision and proceeded. The choice is well-motivated on its own terms: it produces a per-part measured VPP figure, which is materially better evidence for Phase 166's honesty ledger where every VPP figure must be labelled. The guard arithmetic was pinned from `src/proms/eprom.cpp:530-537` rather than from memory — high is a blocking ERROR, low is a non-blocking WARNING.

### Q2 — What does "the part's target" resolve to when unreachable?

| Option | Description | Selected |
|--------|-------------|----------|
| Highest real rail that keeps the firmware reading in band | ~12.3–12.4 V real for the 13 V pair; pot maximum for the 2516 | ✓ |
| Part's target where reachable, today's setting where not | | |
| Highest the pot reaches, guard be damned | | |
| You decide | | |

**Notes:** Gains ~0.9 V of real rail on the two parts whose writes are irrecoverable, while staying inside the blocking ceiling. Each part records target / achieved / firmware / shortfall.

### Q3 — Fresh meter read per part, or per pot change?

| Option | Description | Selected |
|--------|-------------|----------|
| One meter read per pot change + a firmware read per part | Pot step folds into the chip-swap handover | ✓ |
| Fresh meter read for every part, all eleven | | |
| Meter at pot changes only, no per-part firmware read | | |
| You decide | | |

**Notes:** Keeps one operator stop per part rather than two, which is what Phase 161 D-02 requires. The rejected third option was ruled out because a blank or `0x303` reading is exactly how a contact fault surfaces on this rig, and inheriting a group figure would hide it.

**Area checkpoint:** user chose "Next area", declining a question about FM1608's `vcc_mv: 3300`. Recorded in CONTEXT.md as an open research item instead.

---

## UV parts + run depth

### Q1 — How should the three UV parts be handled?

| Option | Description | Selected |
|--------|-------------|----------|
| Run all three — this is the UV bench test, opened deliberately | | |
| Run M27C512 and AM27C020, hold the 2516 | 10 reports + 1 named absence | ✓ |
| Hold all three for a separate operator-initiated session | | |
| You decide | | |

**Notes:** Slot capacity was computed and presented (`size / 256`): M27C512 ~256 slots, AM27C020 ~1024, 2516 only **8** — so one `dev test` slot is 12.5% of the 2516. Memory records the operator owns the timing of the first UV bench test; this discussion opened it for the two large parts only.

### Q2 — Does the held 2516 get a non-`dev test` observation?

| Option | Description | Selected |
|--------|-------------|----------|
| A read-only observation recorded outside the step list | N=3 read, no slot consumed, mirrors 161 D-09 | |
| Named absence only, no seating | | |
| Read-only observation AND a full row | | |
| You decide | | |

**User's free-text response:** *"För the 2516 is it only 2.2 and above that is supporting and there must be more work done before we can test it."*

**Notes:** This supersedes all three offered options. The 2516 is **unsupported hardware on the Rev 2.0 shield** and needs further work besides — a hardware fact of the same class as SC#1's own "adapter absent" example, and specifically not the weak "we chose not to run it" name that 161 D-07 warned about. No seating, no read, no write. Claude checked the firmware for a revision gate (`rurp_hw_rev_utils.h`) and found no explicit 25 V ceiling, so the operator's declaration is the authority and is recorded verbatim. Knock-on noted as a deferred idea: Phase 163 cell B3 does mount the Rev 2.2 shield, but "more work first" makes this a backlog item, not a fold into 163.

### Q3 — Run depth

| Option | Description | Selected |
|--------|-------------|----------|
| Default 2-cycle on all ten | ~65 min machine time | ✓ |
| `--fast` on the three 512 KiB parts only | saves ~21 min | |
| `--fast` everywhere | ~37 min total | |
| You decide | | |

**Notes:** A per-part duration table was extrapolated from `BRINGUP-wrv`'s measured figures and presented with the question. The deciding argument was that `--fast` disables read-nondeterminism measurement, and read nondeterminism is a live UNDETERMINED question from Phase 161 cell A2.

### Q4 — Sequencing the control-arm re-runs

| Option | Description | Selected |
|--------|-------------|----------|
| Interleave — arbitrate each divergence with the chip still seated | 2 free flashes per divergence, zero extra chip handlings | ✓ |
| Batch — finish all ten, then one control flash and re-seat | | |
| Interleave, but no re-flash back | | |
| You decide | | |

**Notes:** Framed on the scarce resource: flashing is pre-authorised and the Leonardo is chip-out-exempt, while chip handling is operator-only and Phase 161 had to record a condition caveat on the shared W27C512 after eight handlings. Noted at decision time that this inverts Phase 160's "control first" ordering — forced by SC#4 — and that on the two UV parts the control re-run lands on the *next* slot, because slot selection is stateless.

---

## Claude's Discretion

Areas where the user deferred, or where precedent settled the question and it was decided without asking:

- **D-01 (disposition source)** — the only explicit "You decide" of the discussion.
- **D-06** — SC#4's arithmetic stated as `10 + N` with the deviation from the roadmap's `11 + N` named on the same line; follows mechanically from the 2516 absence.
- **D-18** — part ordering, derived from the pot and package groups: one pot move, two JP4 changes, nine seatings, with the already-seated W27C512 first at zero handling cost.
- **`fw_board_identity` pre-flight** — the user declined the question at the area checkpoint; Claude made it a pre-flight bring-up datum anyway, on 161 D-10's argument that discovering a null at part 10 wastes the sweep.
- **Halt mapping** — a `dev test` BAD on a part is `P-H2` (a result); `P-H1` is reserved for rig faults.
- **Stall ceilings** — 4× a measured healthy figure per size class, with the kill logged under a numbered log; 161 D-08's pattern.
- **Wave/gate granularity, per-position artifact paths, artifact volume policy** — all follow the 160/161 precedent.

## Deferred Ideas

- The 2516 entirely — needs a Rev 2.2+ shield **and** further work; a backlog item, explicitly not a fold into Phase 163.
- Fixing anything found — Phase 165, on the v1.33 PR branch.
- The FM1608 byte-0 register cache-elision defect — folded as a citation only; the fix is out of scope in both directions.
- `~/.firestarter/config.json`'s recurring mtime change — expect a fourth recurrence; do not attempt removal.
- Program-window VPP/VCC under load — remains unmeasured; v1.34 makes no electrical claim.
- The A2 N=3 read-instability question — record data points, do not attempt to close.
- Extending `rig-pins.json`'s `chips` map to the full inventory — a planning call, not a casual mid-sweep edit.
- Phase 164's Modified Rev 0 photography and rework trace — surfaced again in the todo scan.
