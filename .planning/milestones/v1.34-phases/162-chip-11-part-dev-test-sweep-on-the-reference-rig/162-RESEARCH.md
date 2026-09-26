# Phase 162: CHIP — 11-Part `dev test` Sweep on the Reference Rig — Research

**Researched:** 2026-08-27
**Domain:** Bench execution + evidence tooling for `firestarter dev test` across 11 physical parts on Leonardo + RURP Rev 2.0
**Confidence:** HIGH on R1–R4, R6–R8 (all resolved from source, live probes, or the record); MEDIUM on R5 (measured anchors exist for two of three size classes; the third is extrapolated and labelled as such)

## Summary

CONTEXT.md's D-01…D-18 are locked and this research does not re-open them. It answers the
explicitly-open list and, in the course of doing so, found **four rig defects that block or
falsify the phase as currently conceived** — none of which CONTEXT.md names. In order of
severity:

1. **`dev test` writes its report *inside the frozen config dir*, which breaks the rig's own
   config-dir-SHA assertion on every single run.** Proven empirically below (R3). The frozen
   dir's pinned SHA `77adfdd2…` is computed by `rglob` over every file under
   `/workspaces/.planning/v1.34/config`; one `reports/dev-test-*.json` changes it to
   `2fcae67d…`. That reds `check_arms.py` inside `run_gates.sh` (the per-wave gate),
   `gate_record.check_config_dir_sha` on every already-appended row, and P-11 assertion (2).
   The fix is cheap and it *strengthens* D-09: the appender must **copy out then remove** the
   report, which restores the SHA exactly (proven).
2. **`capture_provenance.py` cannot run on nine of the ten parts.** `--chip` is
   `choices=["w27c512","w29c020"]` (argparse hard gate, `capture_provenance.py:141`/`:77`) and
   `pins["chips"][args.chip]` is a hard index (`:613`). CONTEXT.md's code_context says the tool
   is "Reusable as-is for the chip sweep's positions" — it is not. Both `rig-pins.json`'s
   `chips` map **and** `_CHIP_CHOICES` must be extended (R7).
3. **A `C-01…C-NN` list cannot live in `PROCEDURE.md`'s `## Step list`.** `render_steps.py`'s
   `_STEP_ID_RE` is `^P-(\d\d)$` and `validate_steps()` raises on anything else — which would
   red the `render_steps.py` live gate, not merely fail to render (R6).
4. **`~/.firestarter/config.json`'s mtime has *already* drifted** from Amendment 3's pinned
   `1787817565` to `1787854674` (measured live). P-11 assertion (1) as literally written is
   unconditionally red before this phase starts and would book a false `P-H1` at every
   position (R6/R8).

On the four assigned open questions: **AM27C020 is `diverges: no comparable baseline`** on four
independent grounds (R1). **FM1608's `vcc_mv: 3300` is decorative** — never transmitted, no VCC
control path exists in firmware, and it cannot confound the byte-0 defect; the 3300 is genuine
upstream data whose SRAM→5 V correction is structurally skipped by a Phase-84 relabel (R2). The
appender interface, the sibling `_schema`, the duration budget and the shell gotchas are all
resolved concretely below.

Two further corrections to CONTEXT.md's factual base, both material to the divergence table:
**v1.16's `PROTOCOL-LEDGER.md` is a newer baseline than v1.15 for four parts** (W27C512,
W29C020, SST39SF040, FM1608), so D-04's supersession is broader than "narrow"; and
**`derive_plan`'s step shape is *not* uniform across the ten parts** — `id` is NA on FM1608,
`erase` is NA on five of ten, `blank-check` is NA on three of ten, and the write op is
`write-partial` (not `write`) on the two UV parts. Measured live, per part, in R5.

**Primary recommendation:** plan a Wave 0 that fixes the four rig defects above (config-dir
copy-out-then-remove, `chips`-map + `_CHIP_CHOICES` extension, Amendment 4 under a *new* H2
heading, mtime re-pin) and proves each fix with a runnable gate **before** the first part runs.
Then run the sweep in D-18's order with parts 5 and 6 swapped, so the only healthy 512 KiB part
supplies that size class's stall ceiling.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Deciding what `dev test` does per part (region, ops, cycles) | Host app (`chip_test.derive_plan`) | — | Read-only for this phase; the plan is derived from frozen DB fields and cannot be steered from the bench |
| Applying VPP / driving the bus | Firmware (`eprom.cpp`) | Shield hardware | The asymmetric `eprom_check_vpp` guard lives here; the host never sets VPP |
| Socket VCC | Shield hardware | — | Fixed 5 V rail. No host field and no firmware path controls it (R2) |
| Report content & persistence | Host app (`cli_handlers.dev_test` + `diagnostic_report`) | Filesystem (`<config dir>/reports/`) | Unconditional, fixed path per chip token — the collision and config-dir-SHA problems both originate here |
| Evidence row derivation | Meta-repo bench tooling (`.planning/v1.34/tools/`) | — | Never product code; D-16 boundary |
| Record shape enforcement | `gate_record.py` + `render_evidence.append_row_to_file` | `run_gates.sh` | Both are fully schema-driven and reusable on the sibling file (R3) |
| Procedure prescription | `PROCEDURE.md` | `render_steps.py` | The arm-agnosticism gate lives in the renderer, not the prose |
| Physical actions (seat, JP4, pot, meter) | Operator | — | Standing bench rule 3; Claude never touches the rig |

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01: A row cites every prior sweep that touched the part; `same`/`diverges` is keyed on the
  write-path headline.** *(Claude's call — the user answered "You decide".)*
- **D-02: `diverges` means any comparable per-step flip, in either direction.** *(User's choice.)*
  Compare `dev test`'s per-step verdicts — `id`, `read`, `write`, `verify`, `erase`, `blank-check`
  — against the prior disposition wherever the prior sweep measured that op. The column **names
  the step and the direction**, e.g. `diverges: write OK→BAD` or `diverges: verify BAD→OK`.
- **D-03: Where no comparable prior disposition exists, the row reads `diverges: no comparable
  baseline — <why>`, and the control arm supplies the baseline.** *(User's choice.)* Known to
  apply, at minimum three rows: W29C040, FM1608, ST M27C512; **AM27C020 — unresolved, and the
  planner must settle it.**
- **D-04: A row compares against the *most recent* recorded disposition, with v1.15 as the floor,
  and names which milestone it came from.** *(User's choice.)*
- **D-05: Symptom-identity counts as a flip — but only where the record calls the fault
  deterministic.** Deterministic: W27E512 (`bit 7 @0x3d`), W27E040 (`bit 4 @0x7db`), W29C040
  (`timeout @0x0000ff`). Non-deterministic, so variance never triggers: AM27C020, 2516.
- **D-06: SC#4's arithmetic is stated as `10 + N`, with the deviation from the roadmap's `11 + N`
  named on the same line.** `10 reports + 1 named absence = 11 parts`; `10 primary runs + N
  control re-runs = total runs`. N expected ≥ 3.
- **D-07: `PROCEDURE.md` gains Amendment 4 — a parallel `C-01…C-NN` chip-sweep step list in the
  same file.** Shares `P-01`, `P-02`, `P-04`, `P-06`, `P-11` **by reference, never by copy**.
  Must also **correct §Scope**. Re-confirm the `render_steps.py` empty-diff gate after the edit.
- **D-08: The chip sweep's record is a sibling `.planning/v1.34/bench/CHIP-EVIDENCE.jsonl` with
  its own `_schema`.** Identical 9 `locked_columns` core plus a chip-specific extension list. Its
  own `position_count_expected`. **`EVIDENCE.jsonl`'s 20 stays 20 and is not touched.**
- **D-09: Build `append_chip_evidence.py` and `render_chip_evidence.py`; the appender copies the
  report artifact out.** Derives every machine field; copies
  `<config dir>/reports/dev-test-<chip>.{json,md}` out before the next run overwrites it;
  refuses an incomplete position; takes only the genuinely human fields. Both ship `--selftest`
  (12 tools today → 14).
- **D-10: The `gh` dedup query is allowed to run, is declared, and nothing-was-filed is *proven*.**
  Each run records its dedup outcome. CLOSE-04 needs an issue-count-before/after as **pasted
  command output**, not an assertion.
- **D-11: The pot is set per part, from the multimeter.** Every part records its own VPP figures.
- **D-12: Where the DB target is unreachable, "the setting" is the highest real rail that keeps
  the firmware reading in band.** 12 V group (8 of 10) already in band; 13 V pair (M27C512,
  AM27C020) → aim ~13.2–13.3 V firmware ≈ 12.3–12.4 V real rail. Record `vpp_target_mv`,
  `vpp_real_mv`, `vpp_firmware_mv`, `vpp_shortfall_mv`.
- **D-13: One meter reading per pot change, one firmware VPP reading per part.** Pot step folds
  into the chip-swap handover. Operator adjusts and reads solo; state target, wait, ONE read; no
  live monitor loops. Blank or `0x303` = contact fault.
- **D-14: The 2516 is a named absence — unsupported hardware on Rev 2.0.** Not seated, not read,
  not written. Do not re-open; the read-only-observation option is superseded.
- **D-15: M27C512 and AM27C020 are run — this is the UV masked-write path's first hardware
  exercise.** Record the slot actually written and the count remaining.
- **D-16: Default 2-cycle `dev test` on all ten. No `--fast`.**
- **D-17: Control-arm re-runs are interleaved, arbitrated with the chip still seated.** Two
  flashes per divergence, zero extra chip handlings. Every re-flash carries its own `P-04`
  read-back proof. v1.33 runs first (forced by SC#4). On the UV parts the control re-run lands on
  the **next slot** — record it, do not fight it.
- **D-18: Part order minimises pot and JP4 movement; the already-seated part runs first.** One
  pot move, two JP4 changes, nine seatings. The planner may reorder **on evidence**, not on
  preference, and any reorder must state its cost in pot/JP4 movements.

### Claude's Discretion

- **`fw_board_identity` pre-flight (SC#2).** One `read_programmer_identity` probe as a bring-up
  datum, outside the `C-01…C-NN` step list, before any part runs. ~10 s. Null ⇒ `P-H1` halt.
- **Halt mapping.** A `dev test` BAD on a part is a result — `P-H2`. `P-H1` stays reserved for
  rig faults: null `fw_board_identity`, read-back mismatch after a correct flash, blank/`0x303`
  VPP reading, or a change to `~/.firestarter/config.json`.
- **Stall ceilings, per 161 D-08's pattern.** 4× a measured healthy figure per size class; the
  first part of each class supplies it. State a fallback absolute where none exists yet. The
  logging half is load-bearing.
- **Wave/gate granularity.** `bash .planning/v1.34/tools/run_gates.sh` is the per-wave gate, exit
  code measured directly, never through a pipe. A wave is naturally a pot/JP4 group.
- **Per-position paths and artifact volume.** Follow `IMAGE-PLAN.json`'s
  `artifact_volume_policy`, including its commit-on-failure exception.

### Deferred Ideas (OUT OF SCOPE)

- **The 2516, entirely.** Backlog item, not a fold into Phase 163. File it; do not schedule it.
- **Fixing anything this phase finds.** Divergences are classified and fixed in **Phase 165**, on
  the **v1.33 PR branch**.
- **The FM1608 byte-0 register cache-elision defect.** Folded here only as a *citation*.
- **`~/.firestarter/config.json`'s recurring mtime change.** Handed to Phase 165. **Do not
  attempt removal.**
- **Program-window VPP/VCC under load stays unmeasured.** Every VPP figure is an idle firmware-ADC
  sample or an operator meter reading — never a program-window measurement. v1.34 makes **no
  electrical claim**.
- **The A2 N=3 read-instability question** remains UNDETERMINED. Record data points; do not close.
- **Extending `rig-pins.json`'s `chips` map to the full inventory.** A planning call; if pinned,
  that pinning is a rig asset future phases inherit.
- **Phase 164's Modified Rev 0 work.**
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| CHIP-01 | `firestarter dev test` runs under v1.33 firmware on Leonardo + Rev 2.0 against all 11 v1.15 inventory parts, each producing a report artifact | R5 gives the measured per-part plan shape, region and duration budget; R3 gives the artifact copy-out mechanics and the fixed report path per chip token; R7 unblocks `capture_provenance.py` for the nine new parts. D-14 converts part 11 into a named absence — R4 gives the row shape that makes `11 = 10 + 1` arithmetic over rows |
| CHIP-02 | Every report is firmware-attributable with a non-null `fw_board_identity`; a null is a defect to investigate | R8 gives the exact pre-flight probe (no CLI surfaces the field; only `read_programmer_identity()` does) and the `persist=False` trick that keeps the probe from dirtying the frozen config dir. R4 pins `fw_board_identity` as a top-level extension column derived from `auto_capture` |
| CHIP-03 | Each chip's result is compared against its recorded v1.15 disposition and every divergence is listed explicitly | R1 settles AM27C020. R5's per-part `derive_plan` table shows which steps are structurally NA per part, so an NA is never mis-booked as a divergence. The prior-disposition table in R1 gives every part's newest recorded disposition with its source milestone (correcting D-04's "narrow" scope) |
| CHIP-04 | A control-arm re-run for every diverging chip and for no other, keeping the sweep at 11 runs plus divergences | R4 proposes making SC#4 an arithmetic identity over rows (`count(arm=="control") == count(v133 rows whose divergence_verdict starts "diverges")`), which is stronger than a prose count |
| CHIP-05 | Known-dead and known-limited parts reported with their prior disposition cited inline, so their reds are never counted as v1.34 findings | R1's disposition table carries the verbatim symptom + `file:line` for W27E512 @0x3d, W27E040 @0x7db, W29C040 §6.6/@0x0000ff, AM27C020 non-determinism. R2 adds FM1608's byte-0 todo as a fifth known-carried citation |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

| Directive | How this phase must comply |
|-----------|----------------------------|
| Meta-repo tracks only `.planning/` and `.claude/`; neither sub-repo is committed here | Every artifact this phase produces lives under `.planning/v1.34/`. No sub-repo commit. |
| `chip_database.json` is **GENERATED** by `tools/build_db.py`; never hand-edit | R2's FM1608 `vcc_mv` finding is reported as a generator-side observation for the backlog. **No DB edit in this phase.** |
| Serial-protocol and constant changes must be kept in sync across `serial_comm.py` ↔ `firestarter.cpp` and `constants.py` ↔ `firestarter.h` | Not applicable — this phase changes no product code in either repo. |
| Board differences: Uno 512 B buffer, Leonardo 1024 B | Explains the measured Leonardo-vs-Uno throughput gap in R5. All figures in this research are Leonardo figures unless stated. |
| `pio` runs from `firestarter/` | R8. Applies to D-17's re-flashes. |

---

## R1 — AM27C020's comparability under D-03

### The actual v1.18 record, quoted

`.planning/v1.18/bench/EVIDENCE.json` holds **three** cells, two of them AM27C020. The
disposition D-03 asks about is the third cell (`op: "phase99_deferral"`). Quoted verbatim:

```
"chip": "AM27C020",
"family": "0x08 (EPROM_QUICK)",
"board": "leonardo",  "shield": "Rev 2.0",
"op": "phase99_deferral",
"fw_commit": "35706c2 (Phase 98-05 fix; REFLASHED + avrdude-verified this session; version string 3.0.0b10)",
"vpp_adc_mv": "12900-13000 (idle confirmation reads before write#1 and after write#2; stable, in the 12.75±0.25 band)",
"write_image_sha256": "fdeab9acf3710362bd2658cdc9a29e8f9c757fcf9811603a8c447cd1d9151108",
"bits_flipped": "write#1 @0x1da00: 60/64 bytes programmed byte-exact (ramp +0x04..+0x3F, first 4
   bytes 0x1da00-0x1da03 stayed 0xFF, bad_bytes 4, retries 20); write#2 @0x16600 (confirmatory,
   different region): 0/64 bytes programmed, bad_bytes 64, retries 20 — marginal/unreliable, not a
   deterministic leading-byte offset",
"pre_read_sha256":  "90cd45f5343cd938006f20635de39479159c51b9d56c1b6f1fb23075ed567297",
"post_read_sha256": "5586826791e919f0e3bb150d67ce4ab80d132290dc9d76d97cb32d836c679487",
"verdict": "DEFER (fix-effective-but-unreliable) — Phase-98 fix programs bits (Phase-97 0-bits
   refuted: 60/64 byte-exact) but marginal/unreliable (write#2 0/64); no byte-exact graduation →
   FUT-08 …",
"anomalies": "No UV eraser on hand; full 262144-byte imgA.bin was NOT written … Used a minimal,
   physically-valid pure-1→0 program proof instead: a distinctive 64-byte ramp (writeA.bin,
   0x00..0x3F) written into a currently-all-0xFF scratch region. `firestarter dev write-cycle`
   correctly NOT used … Both writes used -b only, no --skip-erase, no --force (SAFE-01 intact)."
```

The earlier `tier0_microprobe+rca01` cell (pre-fix) is the Phase-97 0-bits reproduction that the
Phase-98 fix **refuted**; it is not the comparison target under D-04. `pre_01_result` also
records, for the same part: *"read oracle N=3 byte-identical PASS; decode 0x08/chip-id 0x197
confirmed; NOT-BLANK 0x02@0x0000."* [VERIFIED: `.planning/v1.18/bench/EVIDENCE.json`]

### What v1.18 measured, versus what `dev test` measures

| Axis | v1.18 Phase 99 | `dev test AM27C020` on the v1.33 arm (measured live) |
|---|---|---|
| Region | `0x1da00` (write#1) and `0x16600` (write#2) — mid-device scratch regions chosen for being all-`0xFF` | `(261888, 256)` = **`0x3FF00`, the top slot** — `uv_slot_starts()` is top-down and `derive_plan` takes `slot_starts[0]` |
| Length | **64 B** | **256 B** |
| Pattern | a distinctive **ramp `0x00..0x3F`** into an all-`0xFF` region — every byte drives many `1→0` transitions; a maximal electrical stress | `cycle_payload = uv-tranche`, `P = C & D`, guaranteed only **≥ 64 cleared bits and ≥ 64 retained bits** out of the slot's 2048 bits — a deliberately partial, far gentler mask |
| Invocation | `firestarter write … -b` (recorded verbatim in `anomalies`) | the engine's own `write-partial` dispatch; **`-b` is on this phase's forbidden-invocation table** |
| Step verdict recorded | none. The disposition is **`DEFER (fix-effective-but-unreliable)`** — a milestone-level judgement about the *fix*, outside `dev test`'s five-verdict vocabulary `{OK, BAD, NA, SKIPPED, marginal}` (`chip_test.py:899-903`) | a real per-step verdict on op `write-partial` |
| Cycle semantics | two *independent* writes at two *different* addresses, hours apart in one session | two cycles of the **same** step, compared by `_fold_cycles`: differing verdicts → `marginal`; identical → that verdict (`chip_test.py:1307-1325`) |

### Verdict

**`diverges: no comparable baseline — v1.18's figures are a 64 B ramp write at 0x1da00/0x16600
via the now-forbidden `write -b`, against `dev test`'s 256 B `P = C & D` masked slot at 0x3FF00;
and v1.18's disposition is `DEFER`, which is not a per-step verdict D-02 can flip against.`**

Four independent grounds, any one sufficient:

1. **Different invocation — the exact ground D-03 already accepts for FM1608.** CONTEXT.md's D-03
   admits FM1608 because "v1.15's PASS came from `write -b`, a flag now on the forbidden list.
   Different invocation." AM27C020's v1.18 baseline used `-b` too, by its own `anomalies` field.
   Applying the rule consistently is not a re-litigation of D-03; it is D-03 doing its job.
2. **Different region.** Mid-device scratch versus the top slot.
3. **Different length and, materially, different pattern semantics.** A ramp into virgin `0xFF`
   demands roughly half of all bits go to `0`; the masked tranche demands only 64 of 2048. A
   marginal part can pass the second and fail the first. Comparing them would be comparing a
   stress test to a smoke test.
4. **No per-step verdict exists to flip against.** `DEFER` is not in `{OK, BAD, marginal}`.

**The tempting `same`-eligible reading, and why it is rejected.** `dev test` does have a
`marginal` verdict, and "write#1 partial, write#2 total failure" *looks* structurally like a
2-cycle marginal. It is not, for a mechanical reason: replayed through `_fold_cycles`, write#1
(60/64, not byte-exact) folds to `BAD` and write#2 (0/64) folds to `BAD`; two `BAD`s produce
`BAD`, not `marginal` (`chip_test.py:1317-1322`). So even the most generous mapping of v1.18's
numbers onto `dev test`'s verdict machinery yields `BAD`, not `marginal` — which would make
`same` a claim that `dev test` should come back `BAD`. That is a prediction, not a baseline.

**Where a comparable baseline *does* exist for this part, and must still be used (D-01/D-02).**
The write path has none; two other steps do:

| `dev test` step | v1.18 baseline | Source |
|---|---|---|
| `id` | chip-id `0x197` confirmed | `pre_01_result` |
| `read` | N=3 byte-identical **PASS**; and a post-write `consistency-check --runs 3` **PASS, 1 distinct SHA** | `pre_01_result`, `readback` |
| `blank-check` | **NOT-BLANK** (`0x02 @ 0x0000`) | `pre_01_result` |
| `write-partial` | **none comparable** | — |
| `verify` | none comparable (inherits the write's region) | — |
| `erase` | structurally NA on both sides — UV-EPROM, `derive_plan` marks it `supported=False` | measured live |

So the row's headline is `diverges: no comparable baseline`, per D-01 keyed on the write path —
but the `id`, `read` and `blank-check` cells carry real v1.18 comparisons and a flip in any of
them is a genuine finding.

### D-04's `DIP32_27C020` premise — CONFIRMED

The claim that v1.18 Phases 97–99 shipped a scoped `DIP32_27C020` pinout with
`rw-pin:[31]` → `CTRL_READ_WRITE` (0x40) is confirmed from four independent places in the record:

- `.planning/PROJECT.md:1173` — *"The fix — a scoped `DIP32_27C020` pinout with `rw-pin:[31]`
  resolving pin 31 to `CTRL_READ_WRITE` (0x40) via the existing revision-invariant `rw_line`
  mechanism … size-gated to ≤256K (27C040/27C080 stay `DIP32_STD`)"*
- `.planning/RETROSPECTIVE.md:822` — same, plus `MAX_27C020_SIZE=262144` dual-repo lockstep
- `.planning/STATE.md:1816` — *"rw-pin:[31] on DIP32_27C020 mirrors the working
  DIP32_SST39SF040 precedent — pin 31 resolves via pin_conversions[32][31]=22 to
  config.rw_line=22 -> CTRL_READ_WRITE (0x40)"*
- `.planning/v1.18/bench/AM27C020-graduation/SHA256SUMS.txt:2` — *"firmware submodule commit
  35706c2 (Phase 98-05 HEAD, corrected DIP32_27C020 rw-pin:[31]"*

**And it is live on the v1.33 arm**, verified this session: `db.get_eprom("AM27C020")["pin-map"]
== "DIP32_27C020"`. So v1.18 genuinely is the superseding baseline under D-04 and comparing
against v1.15's 0-bits signature would book a known-false divergence, exactly as D-04 argues.

**Two refinements to D-04's stated scope, both material.** D-04 calls the supersession "narrow …
covers only AM27C020 and W27C512". It is broader: `.planning/v1.16/ledger/PROTOCOL-LEDGER.md`
(fw `a296195`, **leonardo + Rev 2.0** — the same rig) records **newer PASS dispositions than
v1.15** for four parts. And the size gate means **W27E040 stays `DIP32_STD`** despite also being
algorithm 8 — it is 524288 B, above the ≤256K guard — so v1.18's fix does not touch it and it is
not a `DIP32_27C020` part. Verified live: `W27E040 → DIP32_STD`.

### The full prior-disposition table (D-01/D-04 inputs, all ten parts)

Newest first. Every citation is a real line in the record; the planner should carry these into
the divergence table verbatim rather than re-deriving them.

| Part | Newest recorded disposition | Source | Method used then | Comparability note |
|---|---|---|---|---|
| W27C512 | **PASS** — chip-ID `0xDA08` passed; read N=3 + write-cycle byte-identical to v1.15 `e16b2a5b…` | v1.16 Phase 91 FIX-91, `PROTOCOL-LEDGER.md` bucket `0x07` | erase-enabled **plain `firestarter write`** (A→B) + `consistency-check` N=3 | Closest to comparable of any part: full-device, no forbidden flag. Also validated on this exact rig in v1.34 A3/B2 |
| W27E512 | **FAIL (genuine)** — *"erase cannot clear bit 7 @0x3d (reads 0x7f, want 0xFF) — DETERMINISTIC across initial run + 2 reseats … stuck cell, not contact/VPP"*; explicitly **excluded from the Phase-84 re-bench by D-32** as silicon wear | v1.15 Phase 82, `v1.15/bench/EVIDENCE.md:~86` and `:254` | write-cycle A→B | Shares one DB row with W27C512 (`W27C512,W27E512`, id `0xDA08`). Deterministic ⇒ D-05 symptom-identity applies. **SC#5 known-carried** |
| SST27SF512 | **PASS** — auto-erase proven, N=3 1-distinct-SHA == image B | v1.15 Phase 82 | write-cycle A→B | Full-device both sides |
| W27E040 | **FAIL (genuine)** — *"erase cannot clear bit 4 @0x7db (reads 0xef, want 0xFF) — DETERMINISTIC across initial run + 1 reseat … genuine stuck cell"*; **excluded from Phase 84 by D-32** | v1.15 Phase 82 | write-cycle A→B | Deterministic ⇒ D-05 applies. **SC#5 known-carried**. Note `DIP32_STD`, not `DIP32_27C020` |
| ST M27C512 | **PASS** — 16 B `@0x0000` partial spend; post-write full-chip SHA `008948af…`; N=3 1 distinct SHA | v1.15 Phase 83 | `write` 16 B + `verify -a 0x0000` | D-03 already books this: 16 B `@0x0000` vs a 256 B masked slot `@0xFF00`, different region **and** pattern semantics |
| SST39SF040 | **PASS** — read N=3 + write-cycle byte-identical to v1.15; the P90 FAIL was a **test-method error** (`-b` set FLAG_SKIP_ERASE so flash3 skipped the required erase) | v1.16 Phase 91 FIX-91, bucket `0x06` | erase-enabled **plain `write`** | Newer than v1.15 and obtained without `-b`. Also the **only healthy 512 KiB part** — see R5 |
| W29C040 | **FAIL CONFIRMED** — *"Timeout verifying 0xd7 at 0x0000ff (got 0x00)"*, deterministic N=2, on the build that **carries** the Phase-74 SDP/256 B-page fix; *"the Phase-74 W29C040 flash4 fix does NOT work on real silicon"* | v1.15 Phase 84 Task 3c | `write -b`, 1024 B image crossing the 256/512/768 page boundaries | D-03 already books this: `0x0000ff` is **inside** `dev test`'s carve-out (`derive_plan` gives `(16384, 491520)`), so the failing address is not written at all. **SC#5 known-carried (CR-01)** |
| W29C020 | **PASS** — read N=3 + write-cycle A→B (auto-erase) byte-identical to v1.15 baseline | v1.16 Phase 90, bucket `0x05` | `write -b` | `-b`-obtained. Also validated on this exact rig in v1.34 A3/B2 |
| FM1608 | **PASS** — read N=3 + write-cycle A→B byte-identical to v1.15 baseline; neg-control verify(A) RC=1 | **v1.16 Phase 90**, bucket `0x28` — *newer than the v1.15 Phase 82 row D-03 cites* | `write -b` **FRAM method** (`dev write-cycle` unusable: erase "Not supported") | D-03's reason stands; its **source milestone is v1.16, not v1.15**. **Plus** the byte-0 todo as a second known-carried citation (R2) |
| AM27C020 | **DEFER (fix-effective-but-unreliable)** / `open-defect-carried` **FUT-08** | v1.18 Phase 99 + `PROTOCOL-LEDGER.md` bucket `0x08` | `write -b`, two 64 B ramps | **`diverges: no comparable baseline`** — this section |
| *(2516)* | **DEFERRED**; Phase 84 re-read still **FAIL (3 distinct SHAs, 39/2048 bytes divergent, first at `0x005F`)** | v1.15 Phase 84 Task 2 | `dev consistency-check 2516 --runs 3` | **Named absence, D-14. Not seated.** |

### A systematic comparability hazard the planner must state once, up front

**Five of the ten parts' newest dispositions were obtained with `write -b`** (FM1608, W29C020,
W29C040, AM27C020, and v1.15's W29C040) — and the `-b` of that era **also skipped the erase**.
That is not an inference: v1.16 Phase 91's own RCA is exactly this
(*"`write -b` set FLAG_SKIP_ERASE so flash3 (NOR) skipped the required erase"*, `PROTOCOL-LEDGER.md`
bucket `0x06`), and `PROCEDURE.md`'s forbidden-invocation table records the correction:
*"this flag does **not** also skip the erase (an older standing memory said otherwise); the erase
is now a separate flag (Phase 153)"*. So a `-b`-obtained baseline was taken under **different
flag semantics than exist on either arm today**. The planner should state this once as a shared
clause of the `no comparable baseline` reasons rather than re-arguing it per row.

### D-05 consistency check on AM27C020

D-05 classifies AM27C020 as non-deterministic, so symptom variance must not trigger a re-run.
That is **consistent with, not contradicted by, D-03 booking a re-run here** — the two rules have
different triggers. D-03's trigger (no comparable baseline) fires; D-05's (a moved deterministic
symptom) does not. The record supports D-05's classification directly: v1.18's own verdict says
*"marginal/unreliable … **not** a deterministic leading-byte offset"*, and v1.15 Phase 83 recorded
*"mild read instability: 2 of 3 N=3 reads byte-identical, the 3rd had a localized 12-byte glitch
reading `0x00` at `0x008004`–`0x00800f`"*.

**But the planner must state the consequence up front rather than discover it:** AM27C020's
control re-run is **guaranteed non-arbitrating**. Under D-17 the control re-run lands on the
**next slot down** (`0x3FE00`, not `0x3FF00`) because slot selection is stateless and
content-keyed; and the part is on record as non-deterministic. So a v1.33-vs-control difference
on this part cannot distinguish arm from silicon. CONTEXT.md's own D-05 rejected-alternatives
paragraph already knows this ("the two parts recorded as unable to arbitrate anything, which are
guaranteed uninterpretable"). Write it into the row, and put the symptom variance in `anomalies`.

### Bonus falsifiable oracle: AM27C020's expected pre-read SHA

Nothing between v1.19 and v1.33 touched this part at the bench — grep across `.planning/v1.19`
through `.planning/v1.33` returns only documentation mentions (coverage matrices, carryover
notes), no bench artifact. So the chip should still be in its v1.18 post-write state:

**Expected full-device pre-write read SHA-256 =
`5586826791e919f0e3bb150d67ce4ab80d132290dc9d76d97cb32d836c679487`**
(`.planning/v1.18/bench/EVIDENCE.json`, `post_read_sha256` of the `phase99_deferral` cell).

`dev test` does not expose a read SHA (see R3 §"what `dev test` throws away"), so this cannot be
checked from the report. It *can* be checked with one extra non-destructive
`dev consistency-check AM27C020 --runs 1` before the `dev test` run. **Recommendation: do it.**
It is ~45 s, it is the only continuity check available on a part whose write path is the phase's
riskiest, and a mismatch would mean either an undocumented touch since 2026-06-30 or a read
fault — either of which changes how the row is read.

**What the planner must do differently because of this.** Book AM27C020 as
`diverges: no comparable baseline` **before** the bench session, not after, so the control re-run
is budgeted (it is a 256 KiB-read-bound run, ~2.3 min plus two flashes) rather than discovered;
state on the same row that the re-run cannot arbitrate and why; carry the `id`/`read`/`blank-check`
sub-comparisons against v1.18 as real cells; add the one-off `consistency-check --runs 1`
continuity read; and hoist the shared `-b`-semantics clause out of the per-row reasons.

---

## R2 — FM1608's `vcc_mv: 3300` on a Rev 2.0 shield

**Answer: the field is decorative — display-only. It is never transmitted to the firmware, no
VCC control path exists on any shield revision, and the socket runs at the board's fixed 5 V
rail regardless of what the DB says.**

### The trace, end to end, with citations

**1. The DB row (both arms, byte-identical).**

```
FM1608 | RAMTRON | pinout=DIP28_JEDEC_SRAM_8K | algorithm=40 (0x28) | size=8192 | pins=28
       | type=FRAM | vcc_mv=3300  vdd_mv=5000  vpp_mv=12000 | chip_id_check=false
```
Verified live against **both** `/workspaces/.v1.34-arms/control/firestarter/data/chip_database.json`
and `…/v133/…` — the rows are byte-identical, so `vcc_mv: 3300` is **pre-existing and can never be
a v1.33-caused finding**. Every other part in the sweep declares `vcc_mv: 5000`.

**2. `vcc_mv` is not in the wire dict.** `database.py:513-560`, `convert_to_programmer()` — the
one function that builds what goes to the programmer — emits exactly:
`memory-size`, `algorithm`, `pin-count`, **`vpp_mv`**, `pulse-delay`, and optionally `chip-id`,
`bus-config`, `page-size`, `flags`. **`vcc_mv` is absent.** It reaches only two display sites:
`ic_layout.py:568` (`"vcc_str": format_mv(eprom_data["vcc_mv"])`) and `eprom_info.py:91`
(`'vcc' is kept as per original logic`). `vdd_mv` reaches nothing in the app at all.
[VERIFIED: grep over `/workspaces/.v1.34-arms/v133/firestarter/*.py`]

**3. The firmware has no VCC *control* path — only a measurement.** `grep -i vcc` over
`/workspaces/firestarter/src/` and `/workspaces/firestarter/include/` returns exactly:
- `src/boards/rurp_common.cpp:42` `uint16_t rurp_read_vcc_mv()` — computes VCC from the internal
  1.1 V bandgap (`VCC_mV = 1126400 / ADC_reading`). A **read**.
- `src/hardware_operations.cpp:69-76` — formats that reading for the `hw`/`info` reply.
- `include/rurp_hw_rev_utils.h:48-65` — AVcc *noise* robustification on the A3 detect divider.
- `include/eprom_params.h:31-33` — decisive: *"`verify_mode`: WHEN to verify, never at what VCC.
  The datasheets' raised-VCC verify margin is unreachable on this shield's ~6.25 V ceiling, so no
  value in this column may ever encode a verify VCC."*

There is no setter, no wire field, no register. **No shield revision can honour a 3300 mV VCC
because nothing in the firmware can ask for one.**

**4. The generator says so itself.** `/workspaces/.v1.34-arms/v133/tools/build_db.py:740-748`
carries a correction rule whose comment is the authoritative statement of shield behaviour:

> *"upstream's lower test-rail vcc misreports the real supply. **The shield feeds SRAM-class parts
> a fixed 5V, which is vdd.** … SRAM only. On UV-EPROM and Flash/EEPROM, vdd is the ELEVATED
> program rail (~6.5V) and must never be surfaced as operating Vcc."*
> ```python
> if _etype == "SRAM":
>     chip_entry["electrical"]["vcc_mv"] = chip_entry["electrical"]["vdd_mv"]
> ```

### Why FM1608 alone keeps the 3300 — the root cause, cited

The 3300 is **genuine upstream data, correctly decoded**, not invented:

- upstream `infoic.xml` for `FM1608@DIP28` carries `voltages="0x0100"`, `type="4"` (MP_SRAM),
  `protocol_id="0x07"` [VERIFIED: `infoic.xml @ a8efaedc`, read via
  `.claude/skills/devtest-rootcause/scripts/infoic_lookup.py FM1608`]
- `build_db.py:691` — `"vcc_mv": VCC_VOLTAGES.get((voltages >> 8) & 0x0F, 5000)`;
  `(0x0100 >> 8) & 0x0F == 0x01`
- `build_db.py:163` — `VCC_VOLTAGES = { 0x01: 3300, … }` → **3300**

The SRAM correction *should* fire (upstream types it `4 = SRAM`) — but it does not, because of an
ordering interaction:

- `build_db.py:613` — `_PHASE84_RELABEL = {"FM1608": "FRAM"}` sets `_etype = "FRAM"`
- `build_db.py:744` — `if _etype == "SRAM":` … evaluates **False**

Line 613 runs before line 744, so the one chip the relabel touches is the one chip the correction
can no longer reach. The relabel's own comment says it *"must NOT touch proto_id / pinout / vpp /
algorithm"* — it does not; it silently disables an unrelated correction instead.

**Classification: a pre-existing `build_db.py` decode gap** (the SRAM-class vcc→vdd substitution
should key on the SRAM *family* including FRAM, not the post-relabel string).
- It is **not** Phase 162 work (this phase changes no product code, and `chip_database.json` is
  generated — never hand-edit it, per CLAUDE.md).
- It is **not** Phase 165 work either — Phase 165 owns v1.33-*caused* regressions, and this is
  byte-identical on both arms.
- **File it as a backlog item.** Its only live consequence is that `firestarter info FM1608`
  prints a wrong, user-facing `Vcc: 3.3V`.

### Does the 3300 interact with the byte-0 defect?

**No — it cannot confound or mask it, in either direction.**
`.planning/todos/pending/fm1608-byte0-write-never-lands-register-cache-elision.md` hypothesises
`rurp_write_to_register`'s cache-skip eliding all three shift-register strobes on the first
`memory_set_data(0, byte0)` call, so byte 0 never gets a strobe before the data CE pulse. That is
a **digital strobe-sequencing** mechanism inside the shield's shift-register path. A supply-voltage
value that is never transmitted and never actuated cannot participate in it. Concretely:

- the socket is at the board 5 V rail on every run, so there is no under-voltage condition to
  blame a missing byte-0 write on, and equally no 3.3 V condition to *excuse* one;
- the todo's already-falsified list rules out the competing explanations independently: three
  uniform writes (`0x00`, `0xAA`, `0x5A`) all left byte 0 at `0xFF` while bytes 1..8191 took each
  pattern; a triple-read after one write was byte-identical; and a single-byte `write -a 0`
  reproduced it.

**What this predicts for part 4, and it is a strong prediction.** `derive_plan` gives FM1608
(measured live):

```
id           supported=False  "no chip-id in DB entry"
read         supported=True
blank-check  supported=False  "blank-check not applicable to FRAM (volatile/byte-rewritable…)"
write        supported=True   policy=full-device  region=(0, 8192)  payload=alternate
verify       supported=True   policy=full-device  region=(0, 8192)  payload=alternate
erase        supported=False  "FLAG_CAN_ERASE not set for this chip"
+ 6 SDP legs NA
```

So FM1608 gets **two full-device 8192 B writes with *different* patterns** (`cycle_payload =
alternate`, because FRAM permits `0→1`), each followed by a verify over `(0, 8192)`. If the
byte-0 defect manifests, the expected shape is:
`write` reports success, `verify` goes **BAD** with a **single-byte mismatch at offset `0x0000`**
and every other byte correct — and `classify_fingerprint` will attach a classification to it.
That row must cite the todo inline as **known-carried, pre-existing**, per the Folded Todos
instruction, so it cannot enter Phase 165's failure set or Phase 166's findings as a v1.34
discovery.

Also worth pre-recording: **FM1608's `id` step is structurally NA forever** (`chip_id_check:
false`, `chip_id_value: 0x00000000`) and its `blank-check` and `erase` are structurally NA. Three
of the six comparison cells in D-02's table are NA on this part by construction, not by omission.

### How the plan proves this at execution time, before part 4 is written

Three commands, all non-destructive, all runnable **now** (no device needed for the first two):

```bash
# 1. vcc_mv is not on the wire — assert the exact wire-dict key set.
FIRESTARTER_CONFIG_DIR=/workspaces/.planning/v1.34/config \
/workspaces/.v1.34-arms/v133/.venv/bin/python -P -c '
from firestarter.database import EpromDatabase
db = EpromDatabase(); full = db.get_eprom("FM1608")
wire = db.convert_to_programmer(full)
assert "vcc_mv" not in wire, wire
assert "vdd_mv" not in wire, wire
print("PASS: vcc_mv/vdd_mv absent from wire dict; keys =", sorted(wire))
'
# expected: PASS: vcc_mv/vdd_mv absent from wire dict; keys = ['algorithm', 'chip-id',
#           'flags', 'memory-size', 'pin-count', 'pulse-delay', 'vpp_mv']

# 2. the firmware has no VCC setter — a negative grep, asserted as empty.
! grep -rn "rurp_set_vcc\|set_vcc\|write_vcc\|VCC_SET" /workspaces/firestarter/src /workspaces/firestarter/include
# expected: exit 0 from the negation, i.e. zero matches

# 3. the field is pre-existing, not arm-dependent — a byte-comparison of the two DB rows.
diff <(python3 -c 'import json;d=json.load(open("/workspaces/.v1.34-arms/control/firestarter/data/chip_database.json"));print(json.dumps([r for r in d["RAMTRON"] if r["part_number"]=="FM1608"],sort_keys=True))') \
     <(python3 -c 'import json;d=json.load(open("/workspaces/.v1.34-arms/v133/firestarter/data/chip_database.json"));print(json.dumps([r for r in d["RAMTRON"] if r["part_number"]=="FM1608"],sort_keys=True))')
# expected: empty diff, exit 0
```

The **operator-verified** complement — and it is the only part of R2 that needs the bench — is
the actual socket voltage at FM1608's VCC pin, which would require a multimeter on pin 28 with
the part seated. **Recommendation: do not ask for it.** It measures the shield, not v1.33; it is
outside every requirement in this phase; and CONTEXT.md's deferred list already forbids
program-window electrical claims. Record instead: *"socket VCC not measured — no VCC control path
exists in firmware (`eprom_params.h:31-33`, `rurp_read_vcc_mv()` is read-only) and the shield's
rail is fixed; v1.34 makes no electrical claim."*

**What the planner must do differently because of this.** Resolve R2 in **Wave 0**, from the three
commands above, and record the answer as a row in the phase's own findings before part 4 is
seated — the CONTEXT constraint is "resolve it *before* the part is written", and these commands
need no bench at all. Pre-record FM1608's expected failure shape (verify BAD, single byte at
`0x0000`) with the todo cited **in the plan**, so the executor cannot mistake it for a discovery.
Mark FM1608's `id`, `blank-check` and `erase` cells structurally NA in the divergence table
template. File the `build_db.py` relabel/correction ordering gap as a backlog item, not as work.

---

## R3 — The concrete `append_chip_evidence.py` / `render_chip_evidence.py` interface

### FIRST: the blocking finding this section exists to surface

**`dev test` writes its report inside the frozen config dir, and that breaks the rig's own
config-dir-SHA assertion on every run.**

The mechanism, in three cited steps:

1. `cli_handlers.py:2497-2508` — `out_path = Path(get_config_dir()) / "reports"`;
   `out_path.mkdir(parents=True, exist_ok=True)`; then `dev-test-<chip>.json` and
   `dev-test-<chip>.md` are written there. `get_config_dir()` is **call-time**, so it honours
   `FIRESTARTER_CONFIG_DIR` — which is exactly why the report lands in
   `/workspaces/.planning/v1.34/config/reports/`.
2. `check_arms.py:201-210` — `compute_config_dir_sha()` hashes **`root.rglob("*")` filtered to
   `is_file()`**, i.e. *every file at any depth* under the config dir.
3. Therefore the pinned `77adfdd26ed8710c4a70882e6dc9ee7bb494286fe225000d581f9e730dd77ad0`
   changes the moment the first report lands.

**Proven empirically, non-destructively** (on a `/tmp` copy — the real dir was not touched):

```
clean copy       : 77adfdd26ed8710c4a70882e6dc9ee7bb494286fe225000d581f9e730dd77ad0   ← matches the pin
empty reports/   : 77adfdd26ed8710c4a70882e6dc9ee7bb494286fe225000d581f9e730dd77ad0   ← an empty dir is invisible
one report file  : 2fcae67dd0c67acef8162e77a6afe9a4774a6fa90887849066dda372b7354ccd   ← BROKEN
after copy-out+rm: 77adfdd26ed8710c4a70882e6dc9ee7bb494286fe225000d581f9e730dd77ad0   ← RESTORED
```

Live confirmation that the dir is currently pristine and holds exactly two files:
`config_dir_sha = 77adfdd2…`, `files: ['.gitkeep', 'config.json']`. And
`/workspaces/.planning/v1.34/config/reports` **does not exist yet**, so the first report is
unambiguously this phase's — there is no leftover to disambiguate.

**What breaks, concretely:**

| Consumer | Effect |
|---|---|
| `run_gates.sh` live gate `check_arms.py --expect-config-sha 77adfdd2…` | RED on every wave after the first part. This is the per-wave gate. |
| `gate_record.py --jsonl …` `check_config_dir_sha` (`gate_record.py:297-316`) | Recomputes **live** and compares to each row's recorded value. Because `dev test` overwrites per chip, the live SHA changes every run — so **every previously-appended row's `config_dir_sha` mismatches at the next gate run**. Cascading, not one-off. |
| `PROCEDURE.md` P-11 config-dir assertion (2) | RED. |

**The fix, and it is the one D-09 already half-specifies: the appender must copy the report out
and then REMOVE the source.** The empty `reports/` directory is invisible to `rglob(...).is_file()`,
so removing just the two files restores the SHA exactly (line 4 of the proof above). This turns
D-09's copy-out from an anti-overwrite convenience into a **load-bearing rig invariant**, and it
makes the config-dir gate a real detector of a missed copy-out rather than a nuisance.

Alternatives, with costs named, in case the executor finds copy-out-then-remove too fragile:

| Option | Cost |
|---|---|
| **(A) Copy out then remove** *(recommended)* | Every row's `config_dir_sha` is the pristine `77adfdd2…`; the gate stays meaningful for the 20 WRV rows too. Fragile in exactly one way: a killed appender leaves the dir dirty — which is *visible* as a red gate, which is the correct behaviour. |
| (B) A second, chip-sweep-only `FIRESTARTER_CONFIG_DIR` seeded as a byte-copy | A copy with identical relative paths and contents has the **same** SHA (proven, line 1 above), and `check_arms.py`/`gate_record.py` both read `pins["config_dir"]`, which would keep pointing at the untouched frozen dir. But it introduces a second config dir into a milestone whose whole premise is one frozen dir shared by both arms, and Standing bench rule 9's *value* would differ from the pinned `config_dir`. Needs a `rig-pins.json` field and an amendment clause. |
| (C) Exclude `reports/` from `compute_config_dir_sha` | Weakens the frozen-dir assertion for the 20 WRV positions as well, and edits a tool that is load-bearing for another phase's evidence. Rejected. |

Verify leg for (A) — runnable, and it is the assertion that makes the invariant real:

```bash
CFG=/workspaces/.planning/v1.34/config
python3 -c "
import hashlib,pathlib,sys
root=pathlib.Path(sys.argv[1]); h=hashlib.sha256()
for p in sorted(f for f in root.rglob('*') if f.is_file()):
    h.update(p.relative_to(root).as_posix().encode()); h.update(p.read_bytes())
got=h.hexdigest(); want='77adfdd26ed8710c4a70882e6dc9ee7bb494286fe225000d581f9e730dd77ad0'
print(('PASS' if got==want else 'FAIL'), got); sys.exit(0 if got==want else 1)
" "$CFG"
```

### The `run_gates.sh` discovery contract, quoted from the script

Two mechanisms, both exact:

```bash
PY_TOOLS=()
while IFS= read -r -d '' f; do
    PY_TOOLS+=("$f")
done < <(find "$TOOLS_DIR" -maxdepth 1 -name '*.py' -print0 | sort -z)

if [ "${#PY_TOOLS[@]}" -eq 0 ]; then
    echo "FAIL: discovery found zero *.py files under $TOOLS_DIR -- a suite that finds nothing must fail, not pass" >&2
    exit 2
fi
...
for tool in "${PY_TOOLS[@]}"; do
    name="$(basename "$tool")"
    if ! grep -q -- '"--selftest"' "$tool"; then
        echo "FAIL: $name does not advertise a --selftest mode" >&2
        FAILURES+=("$name: does not advertise a --selftest mode")
        continue
    fi
    echo "--- selftest: $name ---"
    if python3 "$tool" --selftest; then
        SELFTEST_COUNT=$((SELFTEST_COUNT + 1))
    ...
```

Precisely:
- discovery is `find -maxdepth 1 -name '*.py'` — so `__pycache__/` is excluded and a subdirectory
  of helpers would be **invisible**, not discovered;
- the advertisement test is **`grep -q -- '"--selftest"'`** — a search for the *literal
  double-quoted string* in the file's bytes. `ap.add_argument("--selftest", action="store_true")`
  satisfies it; a `'--selftest'` single-quoted variant would **not**;
- the tool is then executed as `python3 "$tool" --selftest` and must exit 0 — it is run with the
  **system `python3`**, not an arm venv, so **the new tools must be stdlib-only** (as all twelve
  existing ones are);
- failure style is accumulate-then-report, exit 1 at the end; exits 2 for bad usage or zero tools.

**Baseline measured live, so the planner can assert the delta:**
`bash .planning/v1.34/tools/run_gates.sh --quick` → `tool self-tests run: 12 / 12`,
`render_steps.py -- diff empty, control=11 v133=11 lines`, `ALL GATES PASSED`.
After this phase: **`14 / 14`**.

### Second finding: `run_gates.sh`'s live gates are hardcoded to `EVIDENCE.jsonl`

D-09 gets the two new tools' `--selftest` legs for free via discovery. It does **not** get their
*live* gates for free. Both live-gate invocations name the WRV file literally:

```bash
python3 "$TOOLS_DIR/render_evidence.py" --jsonl "$BENCH_DIR/EVIDENCE.jsonl" --target "$BENCH_DIR/EVIDENCE.md" --check
python3 "$TOOLS_DIR/gate_record.py"     --jsonl "$BENCH_DIR/EVIDENCE.jsonl" --pins "$PINS_FILE"
```

So unless `run_gates.sh` is edited, `CHIP-EVIDENCE.jsonl` is **never gated** and
`CHIP-EVIDENCE.md`'s `--check` **never runs** — the sibling file would be the one record in the
milestone with no byte-identical-regeneration proof, which is precisely what D-08's rejected
"markdown table only" alternative was rejected for. **The plan must add two live gates**, taking
the suite from 5 live gates to 7. That is a `run_gates.sh` edit, and it is small:

```bash
echo "--- live gate: render_chip_evidence.py --check ---"
if python3 "$TOOLS_DIR/render_chip_evidence.py" --jsonl "$BENCH_DIR/CHIP-EVIDENCE.jsonl" --target "$BENCH_DIR/CHIP-EVIDENCE.md" --check; then ... fi
echo "--- live gate: gate_record.py (CHIP-EVIDENCE.jsonl) ---"
if python3 "$TOOLS_DIR/gate_record.py" --jsonl "$BENCH_DIR/CHIP-EVIDENCE.jsonl" --pins "$PINS_FILE"; then ... fi
```

### Can `gate_record.py` gate the sibling JSONL as-is? — YES, no schema-selection argument needed

`validate_jsonl_file()` (`gate_record.py:367-425`) is **fully schema-driven**. It reads
`record_keys` and `outcome_values` from the file's *own* line-1 `_schema` and validates every
subsequent row against them; nothing about the WRV column set is hardcoded:

```python
if lineno == 1:
    if "_schema" not in obj: violations.append("line 1: missing the '_schema' header record")
    else:
        schema = obj["_schema"]; seen_schema = True
        if not isinstance(schema.get("record_keys"), list): ...
        if not isinstance(schema.get("outcome_values"), list): ...
    continue
...
required_keys = schema.get("record_keys", []) if isinstance(schema, dict) else []
row_violations = (check_required_fields(obj, required_keys) + check_commands(obj, pins)
                  + check_outcome(obj, schema) + check_cross_oracle(obj) + check_config_dir_sha(obj, pins))
```

Consequences the sibling `_schema` must respect, each derived from the code:

| Requirement | Why (cited) |
|---|---|
| Line 1 must carry `_schema` with **both** `record_keys` (list) and `outcome_values` (list) | `:392-400` |
| The field holding argv **must be named `commands`** | `check_commands(record, pins)` reads `record.get("commands")` and is the only thing that rejects a forbidden flag by exact token match and enforces the argv0 allow-list from `pins["arms"][*]["venv_bin"]`. A differently-named field gets **zero** protection. |
| The field holding the two-state result **must be named `outcome`** | `check_outcome` keys on `"outcome" not in record` → returns `[]` (silently no-op). A differently-named field is unchecked. |
| Every declared `record_keys` entry must be non-null, non-blank, non-`PENDING`/`TODO`/`N/A`-style, **or** exactly `"not measured — <reason>"` | `check_required_fields` + `_is_blank_or_placeholder` + `_is_acceptable_not_measured` (`:95-127`). A bare `"not measured"` with no reason is **rejected**. |
| Nested dicts/lists are safe as values | `_is_blank_or_placeholder` returns True only for `None`, `""` and placeholder *strings*; a dict is non-blank. So per-step maps may be nested rather than flattened into 30 columns. |
| `check_cross_oracle` is inert; `check_config_dir_sha` is live | `check_cross_oracle` keys on `written_image_sha256`/`read_sha256`/`app_dev_consistency_verdict` — absent from a chip row, so no-op (`append_evidence.py`'s own docstring says the same about the WRV schema). `check_config_dir_sha` **will** run if the row carries `config_dir_sha` — which it should, and which is why finding #1 above matters. |

**Correction to CONTEXT.md domain fact 2.** It states `gate_record.py` rejects *"a key outside
either list"*. It does not — `validate_object`/`validate_jsonl_file` run only the five checks
above and none rejects an extra key. That guarantee comes from **`render_evidence.append_row_to_file`**
(`render_evidence.py:261-271`):

```python
missing = [k for k in record_keys if k not in new_row]
if missing: raise RenderError(f"row omits declared key(s): {missing}")
extra = [k for k in new_row if k not in record_keys]
if extra:   raise RenderError(f"row carries key(s) not declared in record_keys: {extra}")
if new_row.get("outcome") not in outcome_domain: raise RenderError(...)
```

…plus, in the same function: **duplicate-`position_id` refusal** (`:273-288`), a
**byte-unchanged-prefix re-read immediately before the atomic `os.replace`** (`:293-298`), and
key-ordering to `record_keys`. It is entirely generic — no WRV assumptions — so
**`append_chip_evidence.py` should reuse it unchanged**, exactly as `append_evidence.py` does.
Two names are therefore mandatory in the sibling schema: **`position_id`** (duplicate refusal) and
**`outcome`** (domain check).

### What `dev test` throws away — the limits on what any appender can derive

- **The read bytes do not survive.** `_dispatch_read` (`chip_test.py:2646-2653`) reads each run
  into a `tempfile.TemporaryDirectory` which is destroyed when the step ends. Only the
  **divergence metric** survives (`repeat_divergent`, `cmp_len`, `bad`, `pct`, `first_offset`) and
  only when the runs disagreed. **There is no read SHA in a `dev test` report at all.** So if a
  part shows read nondeterminism (the live A2 N=3 question), the diverging bytes are
  unrecoverable from that run. Record the limitation; a follow-up
  `dev consistency-check <chip> --runs 3 --keep-files` is the only way to capture them, and that
  is an extra run the plan must decide about explicitly rather than assume.
- **`chip_id_actual` is `None` on a pass, by design.** `render()`'s comment (`:835-842`): the
  firmware's OK reply carries no id back, so the host refuses to present its own expected value as
  a measurement. **Do not "fix" that `None`** and do not record it as a missing field — record it
  as `"not measured — chip_id_actual is None on a passing id check by design (the firmware's OK
  reply carries no id; cli_handlers._chip_id_fields discards the host's own echo)"`.
- **`duration_s` is a cycle SUM.** `_fold_cycles`: *"`duration_s` — the SUM across cycles, so
  'steps total' stays honest."* Divide by `run_count` before quoting a per-op figure.
- **`dedup_fingerprint` deliberately excludes the UV slot** (`_step_dict`'s comment, `:682-689`),
  so two UV runs on different slots dedup together. Do not treat a matching fingerprint as
  evidence of a matching slot.

### The proposed CLI

Modelled on `append_evidence.py`'s shape (`:491-507`): defaults for every path, **required** for
every genuinely-human field, `--dry-run`, `--selftest`.

```
python3 .planning/v1.34/tools/append_chip_evidence.py
  # identity ---------------------------------------------------------------
  --position-id CHIP__{v133|control}__<chip_slug>     REQUIRED  (append_row_to_file dedup key)
  --arm {control|v133}                                REQUIRED
  --chip <chip_slug>                                  REQUIRED  (lower-case rig slug, e.g. sst27sf512)
  --chip-token <TOKEN-AS-TYPED>                       REQUIRED  (e.g. SST27SF512 — see the casing trap below)
  --cell-dir PATH                          default: bench/cells/CHIP
  # machine sources (every field derived from these; none transcribed) -----
  --report-json PATH   default: <config_dir>/reports/dev-test-<chip-token>.json
  --report-md   PATH   default: <config_dir>/reports/dev-test-<chip-token>.md
  --provenance  PATH   default: <cell-dir>/provenance_<position-id>.json
  --readback    PATH   default: <cell-dir>/READBACK-VERDICT_<arm>.json     (per-arm, see D-17 below)
  --exit-code   INT                                   REQUIRED  (the dev test process exit code, 0|1|2)
  --console-log PATH                                  REQUIRED  (numbered stdout/stderr log; the D-10 dedup line is scraped from it)
  --commands-extra PATH                    default: none  (JSON list merged after provenance.commands)
  --pins PATH          default: rig-pins.json
  --jsonl PATH         default: bench/CHIP-EVIDENCE.jsonl
  # the FOUR genuinely-human fields ---------------------------------------
  --verdict-file PATH|-                               REQUIRED  (verdict prose)
  --anomalies-file PATH|-                             REQUIRED  (anomalies prose)
  --vpp-real-mv FLOAT|"not measured — <reason>"       REQUIRED  (the operator's meter reading)
  --prior-disposition-file PATH|-                     REQUIRED  (verbatim prior disposition + its file:line citation + source milestone)
  # the divergence call (human, but domain-checked) ------------------------
  --divergence-verdict "same"|"diverges: <how>"       REQUIRED  (refused unless it is exactly "same" or starts "diverges: " with a non-empty tail)
  --known-carried TEXT|"no"                           REQUIRED  (SC#5; free text or the literal "no")
  --control-rerun-for POSITION_ID          default: none (set only on an arm=control row)
  # named-absence mode (the 2516) -----------------------------------------
  --named-absence "<reason>"               mutually exclusive with --report-json/--exit-code
  # misc ------------------------------------------------------------------
  --jp4 {28-pin|32-pin}                               REQUIRED
  --reseat-count INT                       default: 0        (standing bench rule 8)
  --dry-run          print the assembled row, write nothing
  --selftest
```

**Where the four human fields enter** — and nothing else does:
1. `--verdict-file` — the bench synthesis prose (locked column `verdict`).
2. `--anomalies-file` — the locked column `anomalies`, which is also where D-05's non-determinism
   variance and D-17's next-slot note go.
3. `--vpp-real-mv` — the operator's multimeter reading. The **only** number a human supplies.
   `vpp_target_mv` comes from the DB, `vpp_firmware_mv` from the recorded `vpp` invocation's
   output, and `vpp_shortfall_mv` is **computed**, never accepted.
4. `--prior-disposition-file` — the D-01/D-04 citation. Prose plus a `file:line`, because no tool
   can derive "which prior sweep is the most recent one that touched this part".

`--divergence-verdict` and `--known-carried` are also human but are *judgements about the
comparison*, not evidence; they are domain-checked (see refusals) rather than derived.

**Everything else is derived.** From the report JSON: `fw_board_identity`, `hw_revision`,
`host_version`, `protocol`, `chip_id_*`, every step's `verdict`/`run_count`/`duration_s`/
`error_code`/`fingerprint`, the read `divergence`, all five `write_*` target fields,
`write_coverage`, `banner`, `sdp_hold_state`, `db_diff`, `transport_health`,
`dedup_fingerprint`, `schema_version`. From provenance: every position/arm/board/host/config
field. From `rig-pins.json`: `family`'s algorithm, the target's MCU, the forbidden-flag and argv0
policy. From the copied files: their own SHA-256, computed by the tool
(**no SHA is ever transcribed by hand**).

**How it refuses an incomplete position** — accumulate-then-report by name, one pass, never
first-failure-only (`append_evidence.py`'s stated discipline):

| Refusal | Reason |
|---|---|
| `--report-json` missing, unreadable, or not valid JSON | there is no position to record |
| `report["schema_version"] != "1.7"` | the appender derives from a pinned shape; a schema bump must be a deliberate edit, not a silent mis-parse |
| `report["auto_capture"]["chip"] != --chip-token` | the report belongs to a different part — the "field copied from the neighbouring position" failure D-05 exists to prevent |
| `fw_board_identity` is null | **SC#2 is a hard requirement.** Refuse, and route to `P-H1`. Never write a row with a null here. |
| provenance `arm`/`position_id`/`chip` disagree with the CLI args | cross-check refusal |
| provenance `fw_sha` != `pins["arms"][arm]["fw_sha"]` | the wrong arm's provenance |
| `readback["judged"]` absent | the flash was never proved for this arm (P-04 / D-05 / D-17) |
| the recomputed live `config_dir_sha` != the pristine pin | **the previous run's report was not copied out** — the invariant from finding #1 |
| `--divergence-verdict` is neither `same` nor `diverges: <non-empty>` | keeps SC#3's column at exactly two values (D-03) |
| `--control-rerun-for` set on an `arm=v133` row, or unset on an `arm=control` row | SC#4's identity |
| any human field blank, or `"not measured"` with no reason | `_is_acceptable_not_measured` |
| `--named-absence` given together with `--report-json`/`--exit-code` | an absence has no report |
| `check_commands(row, pins)` reports a forbidden flag or a disallowed argv0 | delegated to `gate_record`, applied **before** the write |
| `append_row_to_file` reports a missing/extra key, a bad `outcome`, a duplicate `position_id`, or a changed prefix | delegated to `render_evidence`, unchanged |

**How the copy-out works** — and the ordering is the whole point:

```
1. assert  sha256_tree(<config_dir>) == 77adfdd2…                    (the previous run was cleaned up)
   … dev test runs, writing <config_dir>/reports/dev-test-<TOKEN>.{json,md} …
2. read    the report JSON and derive every machine field
3. copy    reports/dev-test-<TOKEN>.json → $CELL_DIR/reports/<position_id>.json
           reports/dev-test-<TOKEN>.md   → $CELL_DIR/reports/<position_id>.md
4. sha256  both copies; record path + sha for each in the row
5. verify  the copies' SHAs equal the sources' SHAs
6. remove  both source files (NOT the reports/ directory — an empty dir is SHA-invisible)
7. assert  sha256_tree(<config_dir>) == 77adfdd2…  again             (the invariant is restored)
8. append  the row via render_evidence.append_row_to_file
```

The destination is **`$POSITION_ID`-keyed**, which is what makes D-17's interleaved control re-run
safe: `dev test W27E040` on the control arm overwrites `reports/dev-test-W27E040.json`, but the
v1.33 copy already lives at `CHIP__v133__w27e040.json` and the control's lands at
`CHIP__control__w27e040.json`. Step 3 must run **before** the next `dev test` invocation of the
same part on either arm — with step 6 in place, that is enforced by step 1's assertion failing.

**Artifact volume:** these are a few KB each; ~13 runs × 2 files ≈ well under 100 KB.
`IMAGE-PLAN.json`'s `artifact_volume_policy` excludes only *reproducible* or *voluminous*
artifacts (written images, `run_*.bin`). A `dev test` report is neither — it is not reproducible
from any record and it is tiny. **Commit all of them unconditionally**; the commit-on-failure
exception never needs to fire, and `bench/.gitignore` (`cells/*/reads/`, `cells/*/written.bin`)
does not cover `cells/*/reports/`. State that reading explicitly so a future reader does not
apply the exception by analogy.

### `--selftest` must assert, at minimum

Mirroring `append_evidence.py`'s positive/negative structure, stdlib-only, in a temp dir, with no
device and no arm:

*Positive*
1. a complete fixture triple (report JSON + provenance + readback) derives **all** declared
   `record_keys` and round-trips through `append_row_to_file` into a fixture JSONL;
2. `--named-absence` produces a complete row with every machine field as
   `"not measured — <reason>"` and passes `check_required_fields`;
3. `vpp_shortfall_mv` is **computed** from target and firmware readings — asserted by feeding two
   different firmware readings and observing two different shortfalls (a constant-returning
   implementation cannot pass both legs);
4. the copy-out leaves the fixture config dir's tree SHA **byte-identical** to its pre-run value,
   and the two copies' SHAs equal the sources';
5. a UV fixture's `write_coverage` slot line and `slots_remaining` reach the row verbatim (D-15);
6. `write-partial` is accepted as the write op — a fixture whose write step is `op="write-partial"`
   populates the same write columns as one whose op is `write` (guards the UV parts);
7. `--dry-run` writes nothing (asserted by an unchanged file mtime *and* an unchanged byte count).

*Negative — each must exit non-zero and name the field*
8. `fw_board_identity: null` is refused (SC#2);
9. a report whose `auto_capture.chip` mismatches `--chip-token` is refused;
10. `schema_version: "1.6"` is refused;
11. `--divergence-verdict "inconclusive"` is refused; `"diverges: "` with an empty tail is refused;
12. a `commands` entry containing `-b` (and, separately, `--force`) is refused via the delegated
    `check_commands`;
13. a duplicate `position_id` is refused (delegated);
14. a row with an extra key is refused (delegated) — this is the leg that proves the extra-key
    guarantee lives in `render_evidence`, not `gate_record`;
15. a dirty config dir at step 1 is refused, naming the un-copied report;
16. `--control-rerun-for` set on an `arm=v133` row is refused.

For `render_chip_evidence.py --selftest`: a fixture JSONL renders to a deterministic markdown
table; `--check` is green against the freshly rendered target and **red** against a byte-mutated
one (both directions observed); a JSONL with a row key outside `record_keys` is refused; and
regeneration over an unchanged row set is byte-identical (no timestamp anywhere — the WRV file's
`jsonl_convention` requires this and the `--check` gate depends on it).

**What the planner must do differently because of this.** Treat the config-dir/report collision as
a **Wave 0 blocker with its own verify leg**, not a detail inside D-09 — it reds the per-wave gate
and cascades across already-appended rows. Add the two missing live gates to `run_gates.sh` in the
same wave, and assert `tool self-tests run: 14 / 14` and 7 live gates as the delta. Pin the exact
`--chip-token` casing per part in the plan (see R8), because the report filename and therefore the
copy-out depend on it. Require both new tools to be stdlib-only (`run_gates.sh` invokes them with
the system `python3`). Do not ask the appender to derive a read SHA — there is none.

---

## R4 — The `CHIP-EVIDENCE.jsonl` `_schema` shape

### The 9 `locked_columns`, verbatim

From `.planning/v1.34/bench/EVIDENCE.jsonl` line 1. These must be **byte-identical** in the
sibling, in this order, because Phase 166's CLOSE-01 asserts the locked core uniformly across
every milestone's evidence file:

```json
"locked_columns": [
  "chip",
  "family",
  "board",
  "shield",
  "blank_state",
  "op",
  "sha256",
  "verdict",
  "anomalies"
]
```

The file's own note explains why they are reusable: *"the nine-column core pinned verbatim from
`.planning/v1.15/bench/EVIDENCE.json` and `.planning/v1.18/bench/EVIDENCE.json`, where it is
**byte-identical** — the stable core every milestone's evidence record has carried."* Confirmed
against both upstream files this session: v1.18's `locked_columns` is the same nine in the same
order.

**How each locked column is filled for a chip row** (the two that need care are `op` and `sha256`):

| Locked column | Value for a chip row | Derivation |
|---|---|---|
| `chip` | `w27c512`, `w27e512`, `sst27sf512`, `fm1608`, `w27e040`, `sst39sf040`, `w29c040`, `w29c020`, `am27c020`, `m27c512`, `2516` | the rig slug (`--chip`) |
| `family` | e.g. `0x07 (EPROM-STD)` | `"0x%02x (%s)" % (chip_cfg["algorithm"], LABEL[chip])`, mirroring `append_evidence.py:261` |
| `board` | `Arduino Leonardo (ATMEGA32U4)` | `_BOARD_LABEL` + `pins.targets.leonardo.mcu` |
| `shield` | `mounted, Rev 2.0, <CHIP> seated` | provenance `shield_rev_declared` |
| `blank_state` | derived from the report's `blank-check` step: its verdict, or `"not measured — blank-check is NA for this part (<the plan's own reason string>)"` | `steps[]` — **not** a human field here, unlike the WRV appender, because `dev test` measures it |
| `op` | `dev test <TOKEN>: <write-op> over <region>, <run_count> cycles, exit <code>` | assembled from `steps[]` + `write_region_*` + `--exit-code` |
| `sha256` | **`"not measured — dev test retains no read image; _dispatch_read reads into a TemporaryDirectory that is destroyed with the step (chip_test.py:2646). The report artifact SHAs are recorded in report_json_sha256/report_md_sha256."`** | see R3 §"what `dev test` throws away" |
| `verdict` | human prose (`--verdict-file`) | — |
| `anomalies` | human prose (`--anomalies-file`) | — |

`sha256` is the one locked column a chip row genuinely cannot fill, and the
`not_measured_convention` is exactly the mechanism for it — reason on the same line, never a
blank. Worth flagging to Phase 166: **this is the only milestone-evidence row in the project whose
`sha256` is a named absence**, so CLOSE-01's uniform locked-core assertion must accept a
`"not measured — …"` value there (it does: `check_required_fields` treats that shape as a valid
non-null).

### The proposed chip extension column list

40 columns. Every one is derived from a named real field. Grouped for readability; the schema's
`evid_extension_columns` and `record_keys` lists are flat, and `record_keys` =
`locked_columns + evid_extension_columns` in that order (mirroring the WRV file's 9 + 31 = 40).

**Position and provenance (19) — mirrors `capture_provenance.py`'s `RECORD_KEYS` exactly, so the
sibling inherits the same cross-checks and the same P-11 config-dir assertion:**

| # | Column | Source |
|---|---|---|
| 1 | `position_id` | **mandatory name** — `append_row_to_file`'s duplicate refusal |
| 2 | `cell_id` | `CHIP` (primaries and control re-runs alike; the arm distinguishes them) |
| 3 | `cell_slug` | `CHIP` |
| 4 | `arm` | `control` \| `v133` — **the SC#4 discriminator, see the counting rule** |
| 5 | `target_env` | `leonardo` |
| 6 | `board_signature` | provenance (avrdude signature, authoritative board identity) |
| 7 | `controller_string` | provenance (`hw`'s printed controller line, non-authoritative) |
| 8 | `shield_rev_declared` | provenance (operator silkscreen) |
| 9 | `fw_sha` | `pins.arms[arm].fw_sha` — `8695ee52…` (control) / `5759dc8d…` (v133) |
| 10 | `fw_readback_sha_judged` | `READBACK-VERDICT` `sha_actual_judged` |
| 11 | `fw_readback_sha_whole_flash` | `READBACK-VERDICT` `sha_whole_flash_unjudged` (D-02: unjudged, never consumed in the decision) |
| 12 | `fw_readback_judged_span_bytes` | `pins.targets.leonardo.hex_span_expected_by_arm[arm]` → **28170** (control) / **25098** (v133) |
| 13 | `host_arm_sha` | provenance (`git rev-parse HEAD` in the arm worktree) |
| 14 | `host_arm_porcelain_clean` | provenance |
| 15 | `host_arm_file` | provenance |
| 16 | `config_dir_sha` | recomputed live; **must be the pristine `77adfdd2…`** (R3 finding #1) |
| 17 | `interpreter` | provenance (`Python 3.12.14`) |
| 18 | `dep_freeze_sha` | provenance |
| 19 | `eeprom_calibration` | provenance (R1/R2 read-back) |

**`dev test` report-derived (13) — every field traced to `diagnostic_report.py`:**

| # | Column | Derived from |
|---|---|---|
| 20 | `report_schema_version` | `to_dict()["schema_version"]` → `SCHEMA_VERSION = "1.7"` (`diagnostic_report.py:48`) |
| 21 | `host_version` | `_auto_capture_dict()["host_version"]` (`:596`) |
| 22 | **`fw_board_identity`** | `_auto_capture_dict()["fw_board_identity"]` (`:597`) — **SC#2/CHIP-02** |
| 23 | `hw_revision` | `_auto_capture_dict()["hw_revision"]` (`:598`) |
| 24 | `protocol` | `_auto_capture_dict()["protocol"]` (`:600`); set from `convert_to_programmer()["algorithm"]` at `cli_handlers.py:2483` |
| 25 | `chip_id` | object: `{expected, actual, mismatch_reason}` from `:601-603`. `actual` is `null` on a pass **by design** — record the design note, do not "fix" it |
| 26 | `step_verdicts` | object `{op: verdict}` over `_steps_list()` (`:751-770`), each row's `op`/`verdict` (`:692-693`). **Keys are the real op strings**, so a UV part's write key is `write-partial` (`OP_WRITE_PARTIAL`, `chip_test.py:318`) |
| 27 | `step_run_counts` | `{op: run_count}` (`:704`). Expect 2 for `read`/`write`/`verify`/`erase`, **1** for `id`/`blank-check` (`chip_test.py:1075-1079`), 0 for NA/SKIPPED |
| 28 | `step_durations_s` | `{op: duration_s}` (`:723`). **CYCLE SUM — divide by `run_count`** |
| 29 | `step_error_codes` | `{op: error_code}` (`:717`) — the exact firmware `response.id` |
| 30 | `step_fingerprints` | `{op: fingerprint.classification}` (`:718-720`) |
| 31 | `read_divergence` | `steps[read].divergence` — `{repeat_divergent, cmp_len, bad, pct, first_offset}` (`chip_test.py:2663-2669`), or `null` when the 2 runs agreed. **Not in D-08's list, and it should be: this is a free 2-run read-stability probe on every part, and the A2 N=3 question is live** |
| 32 | `write_target` | object: `{region_start, region_length, bits_cleared, bits_retained, current_source}` from `:724-728` |
| 33 | **`write_coverage`** | `_write_coverage_line(result, step)` (`:459-520`). The D-15 disclosure: for a UV part, `slot 0x3FF00 (256 bytes), N bits cleared this cycle` **+ slots-remaining**; for flash4, the boot-block exclusion sentence even on success; `null` on a plain unexcluded full-device write |

**Run-level (5):**

| # | Column | Source |
|---|---|---|
| 34 | `banner` | `{n_ran, m_applicable, locked_steps}` (`:732-739`) |
| 35 | `sdp_hold_state` | `to_dict()["sdp_hold_state"]`. Expect a `NOT-RUN: <reason>` state on all ten — none is protocol `0x0D`, so the SDP exit floor is unreachable (`cli_handlers.py:2551-2556`, gated on `sdp_oracle_applicable(plan)`) |
| 36 | `db_diff` | `{current_support_status, proposed_disposition, ladder_state}` (`:741-749`). Advisory only; `community-confirmed` is never auto-assigned |
| 37 | `transport_health` | `{cobs_errors, crc_failures, retries, timeouts, transport_suspect}` (`:606-618`) — carries `NOT_MEASURED` for absent counters, which the gate accepts |
| 38 | `dedup_fingerprint` | `to_dict()["dedup_fingerprint"]` (`dedup_fingerprint()`, `:186-241`) |
| 39 | `repeat_policy` | derived from `repeat_policy_tag(results)` (`chip_test.py:1088-1116`): `""` for the default N≥2, `runs=1` if degraded. **Expect `""` on all ten — D-16 forbids `--fast`. A `runs=1` here is a protocol violation the gate should catch** |
| 40 | `exit_code` | the process exit code. Record it **alongside** `step_verdicts`, because `_dev_test_exit_code` is a `max()` over per-step codes: a run with both a BAD step and a marginal step exits **2**, which the handler's own docstring ("2 if any step is marginal **and none BAD**") describes incorrectly. The step verdicts are the interpretable record; the code alone is not |

**Artifact (4):** `report_json_path`, `report_json_sha256`, `report_md_path`, `report_md_sha256`.

**VPP (4) — D-11/D-12:** `vpp_target_mv` (DB `vpp_mv`: 12000 for eight parts, **13000** for
M27C512 and AM27C020), `vpp_real_mv` (**the one human number**), `vpp_firmware_mv` (the recorded
`$ARM_BIN -p $PORT vpp` reading), `vpp_shortfall_mv` (**computed**; the plan must pin the sign
convention — recommend `vpp_target_mv − vpp_firmware_mv`, positive = under target, and say so in
the schema note so Phase 166's honesty ledger cannot misread a sign).

**Divergence (6) — D-01…D-05:** `prior_disposition` (verbatim + `file:line`),
`prior_disposition_source` (milestone + phase), `prior_dispositions_all` (D-01's every-sweep
citation list), `divergence_verdict` (exactly `same` or `diverges: <how>`), `known_carried`
(SC#5), `control_rerun_for` (the `position_id` this control row arbitrates, or
`"not applicable — this is a primary v1.33 row"`).

**Physical / process (5):** `jp4_position`, `uv_slot` (`{slot_written, slots_remaining,
slots_total}` or a named-absence string), `reseat_count`, **`commands`** (mandatory name),
`dedup_query_outcome` (D-10 — see below).

**Result (1):** **`outcome`** (mandatory name), domain `["validated", "skipped-with-reason"]`.

That is 9 locked + 40 extension = **49 `record_keys`**. If the planner prefers to hold the WRV
file's exact 40-column total for symmetry, the four VPP columns can be nested into one `vpp`
object and the six divergence columns into one `divergence` object, giving 9 + 31 = 40. Nesting is
safe (`_is_blank_or_placeholder` only rejects `None`/`""`/placeholder *strings*), and it costs
`render_chip_evidence.py` a decision about how to render a nested cell. **Recommendation: keep them
flat.** The divergence and VPP columns are the two things Phase 166 reads most, and a flat column
is greppable from `CHIP-EVIDENCE.md` without a JSON parse.

### `outcome` — what `validated` means for a chip row

`append_evidence.py` computes `outcome` and **never accepts it as input**. The sibling must do the
same, and it needs its own definition because there is no judged SHA. Proposed, derived from the
report alone:

```
validated  iff  fw_board_identity is not null                      (SC#2)
           and  the report was copied out and both copy SHAs match  (the artifact exists)
           and  the config-dir invariant held before and after      (the record is trustworthy)
otherwise  skipped-with-reason
```

Note deliberately what is **not** in that definition: the chip's own verdicts. A `dev test`
**BAD is a result, not a skip** — CONTEXT.md's halt mapping says so (`P-H2`, carried forward), and
SC#1 counts "a report artifact produced", not "a passing report". If `outcome` were keyed on the
chip's verdict, the four known-red parts would book as `skipped-with-reason` and CLOSE-01's
`validated + skipped-with-reason == expected` arithmetic would still balance — but the semantic
would be wrong and Phase 165 would inherit four rows that look un-run. **State this reading in the
schema note**, because it is the one place the sibling's `outcome` semantics diverge from the WRV
file's (where `validated` does mean the judged SHA matched).

### `position_count_expected`, its counting rule, and the exclusion mechanism

```json
"position_count_expected": 11,
"primary_arm": "v133",
"control_rerun_exclusion": "A row whose arm is 'control' is a DIVERGENCE ARBITRATION re-run (D-17), not a sweep position — it is excluded from the 11-position reconciliation and reconciled separately by chip_sc04_rule below. This is the structural analogue of EVIDENCE.jsonl's 'BRINGUP-' cell_id prefix exclusion, keyed on 'arm' rather than on a cell_id prefix because the chip sweep runs one cell and the arm is already the discriminator (position_id is <cell_slug>__<arm>__<chip>, so no prefix is needed to keep the ids distinct).",
"close01_counting_rule": "Computed over rows with arm == 'v133' only: (rows with outcome=='validated') + (rows with outcome=='skipped-with-reason') == position_count_expected (11). The 11 is the v1.15 physical inventory: 10 parts run plus the 2516's named absence (D-14). Evaluated as a script over rows, not a human count.",
"chip_sc04_rule": "SC#4/CHIP-04 as an arithmetic identity, not a prose claim: count(rows where arm=='control') == count(rows where arm=='v133' and divergence_verdict startswith 'diverges') AND every control row's control_rerun_for names an existing v133 row whose divergence_verdict startswith 'diverges' AND no two control rows name the same one. Total runs = 10 + N where N = count(arm=='control'); the roadmap's '11 + N' is read as '10 + N' per D-06/D-14, and that deviation is stated here, on this line.",
"named_absence_convention": "Exactly one row (chip=='2516') carries named_absence set and every machine-derived field as 'not measured — <reason>'. Its arm is recorded as 'v133' because that is the arm the phase was configured under, NOT because a run occurred; op reads 'not run — named absence' and that is the field a reader consults. It is counted by close01_counting_rule (it is a position holding a named reason for absence) and is never counted by chip_sc04_rule.",
"not_measured_convention": "<copied verbatim from EVIDENCE.jsonl>",
"negative_control_convention": "<copied verbatim from EVIDENCE.jsonl>",
"artifact_volume_policy_ref": "<copied verbatim from EVIDENCE.jsonl, plus: dev test report artifacts are small, non-reproducible and committed unconditionally; the commit-on-failure exception does not apply to them>"
```

`chip_sc04_rule` is the section's strongest recommendation: **it turns "for every diverging chip
and for no other" into an equation over rows**, which is exactly what D-08's rejected
"markdown-table-only" alternative could not provide, and it is checkable by
`render_chip_evidence.py --check`'s sibling reconciliation or by a three-line script in the
phase gate.

**The one honest tension, named rather than hidden:** the 2516's row carries `arm: "v133"` while
no run occurred on any arm. The alternative — `arm: "not measured — never seated"` — would drop
the v133 count to 10 and make `position_count_expected: 11` unreachable, or force a third
counting term. The `named_absence` column plus the `op` string carry the truth; the `arm` field
carries the phase configuration. The convention above states this explicitly so it reads as a
decision, not an error.

### `EVIDENCE.jsonl`'s `position_count_expected: 20` is untouched — confirmed

Measured live: the WRV file holds **16 rows** after line 1 — 4 `BRINGUP-*` (excluded) and 12
sweep positions (`A1`×4, `A2`×4, `A3-B2`×4). `20 − 12 = 8` remain, and they are Phase 163's `B1`
and `B3` cells (4 positions each). Nothing in this phase appends to that file, changes that
number, or touches its `_schema`. Verify leg:

```bash
python3 -c "
import json
lines=open('.planning/v1.34/bench/EVIDENCE.jsonl').read().splitlines()
sch=json.loads(lines[0])['_schema']
rows=[json.loads(l) for l in lines[1:]]
nb=[r for r in rows if not str(r.get('cell_id','')).startswith(sch['bringup_cell_id_prefix'])]
print('position_count_expected =', sch['position_count_expected'])
print('non-bringup rows        =', len(nb))
assert sch['position_count_expected']==20
"
# expected: position_count_expected = 20 ; non-bringup rows = 12
```

Run it **before and after** the phase and diff the output — that is the cheapest possible proof
that the sibling file did not leak into the WRV one.

**What the planner must do differently because of this.** Copy the 9 locked columns byte-for-byte
(do not retype them). Add `read_divergence` and `exit_code` to D-08's named list — both are real
report fields with live evidential value that D-08 omits. Name `sha256` as a permanent
`"not measured — …"` for this file and warn Phase 166's CLOSE-01 about it. Define `outcome`
without reference to the chip's own verdicts and say why on the same line.
Adopt `chip_sc04_rule` as an equation. Pin the `vpp_shortfall_mv` sign convention in the schema,
not in prose.

---

## R5 — Measured duration budget + stall ceilings

### The measured figures that exist — and CONTEXT.md's anchors are the wrong board

CONTEXT.md's `<specifics>` anchors are `BRINGUP-wrv` figures, taken on **Uno + Rev 2.0**. This
phase runs on **Leonardo + Rev 2.0**, and `A3/B2` measured that exact rig. Use A3/B2.

**Full-device write, wall-clock and app-reported, from `bench/EVIDENCE.jsonl` rows:**

| Position | Board | Chip | Bytes | Wall | App | Derived B/s (app) |
|---|---|---|---|---|---|---|
| `BRINGUP-wrv__v133__w27c512` | **uno** | W27C512 | 65536 | 41.010 | 37.48 | 1749 |
| `A1__v133__w27c512` | uno | W27C512 | 65536 | 41.037 | 37.48 | 1749 |
| `A1__v133__w29c020` | uno | W29C020 | 262144 | 97.916 | 94.48 | 2774 |
| **`A3-B2__control__w27c512`** | **leonardo** | W27C512 | 65536 | **37.172** | **33.37** | **1964** |
| **`A3-B2__v133__w27c512`** | **leonardo** | W27C512 | 65536 | **37.118** | **33.37** | **1964** |
| **`A3-B2__control__w29c020`** | **leonardo** | W29C020 | 262144 | **66.671** | **62.99** | **4161** |
| **`A3-B2__v133__w29c020`** | **leonardo** | W29C020 | 262144 | **66.674** | **62.99** | **4161** |

**Full-device read, from `bench/cells/A3-B2/WRITE.md`:**

| Chip | Bytes | Measurement | Figure | Derived B/s |
|---|---|---|---|---|
| W27C512 | 65536 | single `read` (control position), app-reported | 7.40 s | 8856 |
| W27C512 | 65536 | `dev consistency-check --runs 3`, per-run app-reported | 10.69 / 10.57 / 10.66 s | **6148** |
| W27C512 | 65536 | whole 3-run invocation, wall | 32.607 s | — |
| W29C020 | 262144 | single read, wall / app | 45.756 / 41.87 s | 6261 |
| W29C020 | 262144 | `--runs 3`, per-run app-reported | 45.16 / 45.11 / 45.04 s | **5813** |
| W29C020 | 262144 | whole 3-run invocation, wall | 135.763 s | — |

**The one 512 KiB figure in the whole record:** `.planning/v1.15/bench/EVIDENCE.md` Phase 82 row 5,
SST39SF040 — *"flash3 slow path ~240 s/write"*, 524288 B, **leonardo + Rev 2.0**, v1.15-era
firmware → **2185 B/s**. It is a same-rig figure but a *different-firmware* figure, and it is
quoted as "~240 s", not measured to a decimal. Treat it as an order-of-magnitude anchor.

### Which size class has a real healthy baseline today, and which does not

| Class | Parts in this sweep | Healthy same-rig write baseline? | Healthy same-rig read baseline? |
|---|---|---|---|
| **8 KiB** (FM1608 only) | FM1608 | **No** — nothing measured on any rig | No |
| **64 KiB** | W27C512, W27E512, SST27SF512, ST M27C512 | **YES** — 33.37 s app / 37.12 s wall, v1.33 arm, this rig, twice | **YES** — 10.66 s/pass |
| **256 KiB** | W29C020, AM27C020 | **YES** — 62.99 s app / 66.67 s wall, v1.33 arm, this rig, twice | **YES** — 45.10 s/pass |
| **512 KiB** | W27E040, SST39SF040, W29C040 | **No** — only v1.15's "~240 s" on older firmware | **No** — nothing at all |

So: **two of three size classes have a real, current, same-rig, same-arm baseline; the 512 KiB
class has none**, and it is the class that dominates the sweep's runtime.

### The per-part plan shape, measured live (not assumed)

`derive_plan` was executed against the **v1.33 arm's own** database and engine for all eleven
tokens. This corrects CONTEXT.md's domain claim that "`derive_plan` yields the same 12-step shape
for every part" — the *count* is 12 for every part, but which steps are executable, the write op
name, the region and the payload recipe all differ:

| # | Part | Scope | Proto | Write op | Write region | Payload | `id` | `blank-check` | `erase` |
|---|---|---|---|---|---|---|---|---|---|
| 1 | W27C512 | full | 7 | `write` | `(0, 65536)` full-device | same | ✔ | ✔ *(after erase)* | ✔ |
| 2 | W27E512 | full | 7 | `write` | `(0, 65536)` | same | ✔ | ✔ *(after erase)* | ✔ |
| 3 | SST27SF512 | full | 7 | `write` | `(0, 65536)` | same | ✔ | ✔ *(after erase)* | ✔ |
| 4 | FM1608 | full | 40 (`0x28`) | `write` | `(0, 8192)` | **alternate** | **NA** *(no chip-id)* | **NA** *(FRAM)* | **NA** *(no FLAG_CAN_ERASE)* |
| 5 | W27E040 | full | 8 | `write` | `(0, 524288)` | same | ✔ | ✔ *(after erase)* | ✔ |
| 6 | SST39SF040 | full | 6 | `write` | `(0, 524288)` | same | ✔ | ✔ *(after erase)* | ✔ |
| 7 | W29C040 | full | 5 | `write` | **`(16384, 491520)`** | same | ✔ | **NA** *(flash4 auto-erase)* | **NA** |
| 8 | W29C020 | full | 5 | `write` | **`(16384, 229376)`** | same | ✔ | **NA** | **NA** |
| 9 | AM27C020 | partial | 8 | **`write-partial`** | **`(261888, 256)`** uv-slot | **uv-tranche** | ✔ | ✔ *(before write)* | **NA** *(UV)* |
| 10 | ST M27C512 | partial | 7 | **`write-partial`** | **`(65280, 256)`** uv-slot | **uv-tranche** | ✔ | ✔ *(before write)* | **NA** *(UV)* |
| — | 2516 | partial | 11 | `write-partial` | `(1792, 256)` | uv-tranche | **NA** | ✔ | **NA** | *(not run — D-14)* |

All six SDP legs are `supported=False` on all eleven — every reason string reads *"SDP lock/unlock
applies only to protocol 0x0D parallel EEPROMs"* — confirming CONTEXT.md's claim that the SDP exit
floor can never fire in this phase.

**Three consequences the planner must carry into the divergence table:**
- **`id` is NA on FM1608** (and 2516). D-02's `id` cell is structurally NA there, not a comparison.
- **`erase` is NA on five of ten** (FM1608, W29C040, W29C020, AM27C020, M27C512). Half the sweep's
  `erase` column is structurally empty on the v1.34 side — an NA, never a divergence.
- **`blank-check` is NA on three of ten** (FM1608, W29C040, W29C020).
- **The write op key is `write-partial`, not `write`, on the two UV parts.** Any per-step lookup
  keyed on the literal `"write"` will silently miss them.

### Derived per-part `dev test` duration budget

Basis: read at **6000 B/s** (conservative, from the 256 KiB per-pass figure), 0x07 write at
**1964 B/s**, flash4 (0x05) write at **4161 B/s**, flash3 (0x06) write at **2185 B/s** (v1.15),
algorithm 8 write assumed 0x07-like (**unmeasured — flagged**), FM1608 write unmeasured.
`read`/`write`/`verify`/`erase` each run **2×** (D-16 default); `id`/`blank-check` run **1×**.
`verify` costs a read of the write region. Figures are app-time; add ~10 % for wall.

| # | Part | read ×2 | write ×2 | verify ×2 | erase ×2 | blank-chk | **≈ total** | Confidence |
|---|---|---|---|---|---|---|---|---|
| 1 | W27C512 | 21 | 67 | 21 | ~2 | 11 | **~123 s (2.1 min)** | HIGH — every component measured on this rig |
| 2 | W27E512 | 21 | ≤67 | ≤21 | fails fast? | 11 | **~120 s, possibly much less** | MEDIUM — the erase failure may short-circuit |
| 3 | SST27SF512 | 21 | 67 | 21 | ~2 | 11 | **~123 s** | HIGH |
| 4 | FM1608 | 3 | ~8 | 3 | NA | NA | **~15–25 s** | LOW — write rate unmeasured; FRAM is fast |
| 5 | W27E040 | 175 | **534** | 175 | ? | 87 | **~980 s (16.3 min)** | **LOW — 512 KiB write rate on proto 8 is unmeasured** |
| 6 | SST39SF040 | 175 | **480** | 175 | ? | 87 | **~925 s (15.4 min)** | LOW — anchored only on v1.15's "~240 s" |
| 7 | W29C040 | 175 | 236 | 167 | NA | NA | **~580 s (9.7 min)** | MEDIUM — flash4 rate measured at 256 KiB, extrapolated to 512 |
| 8 | W29C020 | 90 | 110 | 78 | NA | NA | **~280 s (4.7 min)** | HIGH — both rates measured on this rig |
| 9 | AM27C020 | 90 | ~0.5 | ~0.2 | NA | 45 | **~137 s (2.3 min)** | HIGH — **read-bound**, the 256 B write is negligible |
| 10 | ST M27C512 | 21 | ~0.3 | ~0.1 | NA | 11 | **~34 s** | HIGH — read-bound |

**Primary sweep ≈ 3320 s app ≈ 62 min wall.** D-16's "~65 min of machine time" is a good
estimate — but it is *coincidentally* good: it was extrapolated from Uno figures for a `write`
command, and it happens to land near a Leonardo-figure estimate for a 12-step 2-cycle command.

**Add the control re-runs.** N ≥ 3 by D-03 (W29C040, FM1608, ST M27C512) and this research adds
AM27C020, so **N ≥ 4** before any genuine flip; W27E040 and W27E512 are both likely `diverges` on
D-05 symptom-identity grounds. Each re-run costs its part's own runtime plus **two flashes with
their own P-04 read-back proofs**. Measured flash-chain cost on this board:
`measured_touch_to_read_complete_s = 3.878` for the read-back, plus a `pio run -t upload` (tens of
seconds). Budget ~90 s per flash pair including the judge.

| Scenario | Extra machine time | Running total |
|---|---|---|
| N=4, none of them 512 KiB (W29C040 excluded — impossible, it *is* 512 KiB) | — | — |
| **N=4 realistic** (W29C040 580 s + FM1608 20 s + M27C512 34 s + AM27C020 137 s) + 4 flash pairs | ~771 s + ~360 s ≈ **19 min** | **~81 min** |
| **N=6 pessimistic** (add W27E040 980 s + W27E512 120 s) + 2 more flash pairs | +1100 s + 180 s ≈ **+21 min** | **~102 min** |

**Budget ~2 hours of machine time**, on top of nine operator chip-swap handovers, one pot move,
two JP4 changes and the per-wave gate runs. That is materially more than "~65 min" and the plan
should say so.

### Stall ceilings: 4× a measured healthy figure per size class

Per 161 D-08's pattern (*"a stalled write is killed at a ceiling derived from a measured healthy
figure, and the kill is logged"*), and noting D-08's own caveat: *"the 4× multiple is a judgment
call, not a measurement. If A1's healthy figures show high variance, widen it and **state the
widening**, do not silently exceed it."*

One important structural difference from Phase 161: **`dev test` is a single invocation covering
all twelve steps**, so the ceiling is a whole-invocation timeout, not a per-write one. There is no
way to time-box the write alone.

| Size class | First part of the class | Ceiling once that part has produced a healthy figure | **Fallback absolute for the first part itself** |
|---|---|---|---|
| 8 KiB | FM1608 (part 4) | 4 × its own measured total | **120 s** — derived: 4 × 25 s estimate, floored generously because 8 KiB cannot legitimately take minutes |
| 64 KiB | **W27C512 (part 1)** | 4 × its measured total | **500 s** — derived: 4 × 123 s, and 123 s is itself the sum of same-rig measured components |
| 256 KiB | **W29C020 (part 8)** | 4 × its measured total | **1120 s (18.7 min)** — derived: 4 × 280 s, same-rig measured components |
| 512 KiB | **W27E040 (part 5) under D-18's order** | 4 × its measured total | **3920 s (65 min)** — derived: 4 × 980 s, but the 980 s rests on an *unmeasured* proto-8 write rate |

**Every fallback above must be recorded as "derived from measured components at <rate>, ×4",
never as a bare number** — that is the difference between 161 D-08's approach and the arbitrary
fixed ceiling it rejected.

### The reorder this research recommends, and its cost

**Swap D-18's parts 5 and 6: run SST39SF040 before W27E040.**

The reason is precisely the one D-18 admits as evidence ("e.g. a part must move to keep a stall
ceiling derivable"). Under D-18's order the **first** 512 KiB part is **W27E040 — a known-red
part** (`FAIL (genuine)`, stuck bit @0x7db, deterministic). A known-red part cannot supply a
*healthy* baseline for its size class: its write either aborts early (too short → a ceiling that
would kill the healthy parts that follow) or retries (v1.18 recorded `retries: 20` per bad byte →
too long, and a ceiling derived from it would be useless). **SST39SF040 is the only 512 KiB part
in the inventory with a PASS on record** (v1.16 Phase 91 FIX-91, erase-enabled plain `write`, this
exact rig), so it is the only candidate that can supply the 512 KiB healthy figure.

**Cost of the swap, stated as D-18 requires: zero.** Both parts are DIP32 and both declare
`vpp_mv: 12000`, so they sit in the same JP4 group and the same pot group. The swap moves one
chip-swap boundary and changes nothing else:

| # | Part | Pkg | VPP | Handover | Change |
|---|---|---|---|---|---|
| 1 | W27C512 | DIP28 | 12 V | *(already seated)* | — |
| 2 | W27E512 | DIP28 | 12 V | swap | — |
| 3 | SST27SF512 | DIP28 | 12 V | swap | — |
| 4 | FM1608 | DIP28 | 12 V | swap | — |
| **5** | **SST39SF040** | DIP32 | 12 V | swap + **JP4 → 32-pin** | **moved up from 6** |
| **6** | **W27E040** | DIP32 | 12 V | swap | **moved down from 5** |
| 7 | W29C040 | DIP32 | 12 V | swap | — |
| 8 | W29C020 | DIP32 | 12 V | swap | — |
| 9 | AM27C020 | DIP32 | 13 V | swap + **pot → 13 V** (meter read) | — |
| 10 | ST M27C512 | DIP28 | 13 V | swap + **JP4 → 28-pin** | — |

Still **one pot move, two JP4 changes, nine seatings**. The 64 KiB and 256 KiB classes are already
correctly ordered: part 1 (W27C512) and part 8 (W29C020) are the two healthiest parts in the
inventory — both v1.16 PASS *and* both `validated` on this exact rig in v1.34 A3/B2 — and each is
the first of its class. AM27C020 (part 9) is physically 256 KiB but its `dev test` is read-bound,
so W29C020's figure at part 8 covers it.

### The kill log — the load-bearing half

Per 161 D-08, and unchanged here:
- the kill runs under a **numbered log** with full stdout **and** stderr captured;
- the **last progress frame** is captured, and recorded as
  `timed out at N s against a measured baseline of M s`;
- **write-progress emission is time-keyed per block with the clock restarting each block**, so the
  last frame names a **block, not a byte offset**. On a `dev test` run this is worse than on a
  bare `write`: twelve steps go past, so the log must also name **which step** was in flight.
  Recommend the executor prefix each `dev test` invocation with `ts`-style line stamping or, at
  minimum, record the wall-clock at which the last console line appeared, so the step can be
  identified after the fact.

Phase 160's single **unlogged** shell-timeout kill (a 120 s cut during plan 11's `vpp`
invocation) is what produced the untraceable `~/.firestarter` contamination this milestone still
carries. That is the failure mode the logging half exists to prevent.

### `run_count` — confirmed

`dev test` with **no** `--fast`: `run_plan(plan, …, runs=1 if fast else 2, allow_single_run=fast, …)`
(`cli_handlers.py:2460-2469`). The comment is explicit that the weaker policy needs **two**
deliberate arguments: *"a caller that passes `runs=1` alone still fails the whole plan, so the
weaker policy can only ever be reached on purpose. The default path passes neither and is
byte-for-byte the pre-existing call."* So `run_count == 2` on `read`/`write`/`verify`/`erase` and
`== 1` on `id`/`blank-check` is the expected shape, and a `repeat_policy` of `runs=1` in any row
would mean `--fast` was used in violation of D-16 — which is why R4 makes it a column.

### How the plan proves R5 at execution time

```bash
# 1. the per-part plan shape — no device needed, run it in Wave 0 and commit the output
FIRESTARTER_CONFIG_DIR=/workspaces/.planning/v1.34/config \
/workspaces/.v1.34-arms/v133/.venv/bin/python -P -c '
from firestarter.database import EpromDatabase
from firestarter import chip_test as ct
from firestarter.cli_handlers import _is_uv_eprom
db=EpromDatabase()
for p in ["W27C512","W27E512","SST27SF512","FM1608","SST39SF040","W27E040","W29C040","W29C020","AM27C020","M27C512"]:
    uv=_is_uv_eprom(type("A",(),{"db":db})(), p)
    plan=ct.derive_plan(p, db, write_scope=("partial" if uv else "full"))
    ex=[(s.op, s.region_policy, s.write_region) for s in plan.steps if s.supported]
    print(p, ex)
'
# 2. the measured anchors — assert they are still what this research read
python3 -c "
import json
rows=[json.loads(l) for l in open('.planning/v1.34/bench/EVIDENCE.jsonl')][1:]
d={r['position_id']:(r['write_duration_wallclock_s'], r['write_duration_app_reported_s']) for r in rows}
assert d['A3-B2__v133__w27c512']==(37.118, 33.37), d['A3-B2__v133__w27c512']
assert d['A3-B2__v133__w29c020']==(66.674, 62.99), d['A3-B2__v133__w29c020']
print('PASS: A3/B2 Leonardo anchors unchanged')
"
```

**Operator-verified / not provable without the bench:** every 512 KiB and 8 KiB figure in the
budget table. Those are the ones the plan must record as *measured for the first time in this
phase*, with the fallback absolute stated as the ceiling that governed the first run of each class.

**What the planner must do differently because of this.** Replace CONTEXT.md's Uno anchors with
the A3/B2 Leonardo figures throughout. Budget **~2 hours** of machine time, not 65 minutes, and
say which part of that is the ~19–21 min of control re-runs. **Swap parts 5 and 6** and record the
zero cost. Derive every fallback ceiling from measured components and show the arithmetic. Add
"which step was in flight" to the kill-log requirement, because `dev test` is twelve steps behind
one timeout. Carry the per-part NA map (`id`/`erase`/`blank-check`) into the divergence-table
template so an NA is never mis-booked, and key every per-step lookup on both `write` and
`write-partial`.

---

## R6 — `PROCEDURE.md` Amendment 4 mechanics

### What §Scope says today, verbatim (lines 13–27)

```markdown
## Scope

One cell run covers **both arms** (`control` then `v133`) and **both bench chips**
(W27C512 DIP28, then W29C020 DIP32) on one mounted shield/board pair. A cell therefore holds
**four positions**: `{control,v133} × {w27c512,w29c020}`. The five cells this milestone runs
are `A1`, `A2`, `A3/B2`, `B1`, `B3` (`.planning/STATE.md`, `.planning/REQUIREMENTS.md`); one of
those (`A3/B2`) additionally carries a bring-up position (`BRINGUP-wrv`) recorded outside the
five-cell table.

This document is executed **unchanged** by Phases 161–163. Any change to it after the first
real cell has run must be recorded as a **procedure amendment**: a dated note at the bottom of
this file naming (a) what changed, (b) why, and (c) exactly which cells ran under the old text
and which run under the new text. An amendment is never silent — a step whose text quietly
drifts mid-sweep is exactly the failure mode `render_steps.py`'s gate and this scope note exist
to prevent.
```

The header (line 8) carries the same false claim independently: *"This procedure is executed
**unchanged** by Phases 161, 162 and 163."*

**The minimal correct replacement** — two edits, both surgical, neither touching `## Step list`:

1. Line 8, replace the sentence with:
   > *"This procedure is executed **unchanged** by Phases 161 and 163, whose cells are
   > write-read-verify cells. **Phase 162 runs a different command (`firestarter dev test`) and
   > executes the `## Chip-sweep step list` section instead of `## Step list`** — see Amendment 4.
   > Every cell either phase runs cites this document's step ids rather than re-describing the
   > run."*

2. In §Scope, insert after the first paragraph (leaving the WRV cell definition intact):
   > *"**Two cell shapes, not one.** The paragraph above defines the **WRV cell** — the shape
   > Phases 161 and 163 run, and the only shape `## Step list`'s `P-01…P-11` describe. Phase 162
   > runs a **chip-sweep position** instead: one part, one arm, one `firestarter dev test`
   > invocation, on the standing Leonardo + Rev 2.0 rig Phase 161 leaves assembled. It has no
   > pre-computed image, no `IMAGE-PLAN.json` row, no full-device SHA judgement, and no
   > per-cell arm rotation — `P-07` and `P-09` do not apply to it at all. Its steps are
   > `C-01…C-NN` under `## Chip-sweep step list`, and its evidence goes to
   > `bench/CHIP-EVIDENCE.jsonl`, never to `bench/EVIDENCE.jsonl`, whose
   > `position_count_expected: 20` counts WRV positions only. The **standing bench rules, the
   > `## Arm substitution` token table, the halt policy, the outcome taxonomy, the forbidden
   > invocations and the recording discipline bind both shapes identically.**"*

Then, and only then, does the roadmap's "executed unchanged by Phase 162" claim stop standing and
being false.

### **Blocking finding: `C-NN` step ids cannot live inside `## Step list`**

`render_steps.py` parses **only** the text strictly between `## Step list` and the next `## `
heading (`extract_step_list_section`, `:69-80`), and then:

```python
_STEP_ID_RE = re.compile(r"^P-(?P<num>\d\d)$")
...
def validate_steps(steps):
    for step in steps:
        m = _STEP_ID_RE.match(step["id"])
        if not m:
            raise ProcedureParseError(f"step id {step_id!r} does not match the P-NN pattern")
        num = int(m.group("num"))
        if step_id in seen: raise ProcedureParseError(f"duplicate step id: {step_id!r}")
        if prev_num is not None and num <= prev_num:
            raise ProcedureParseError("step ids are not in strictly ascending order: …")
        if step["arm"] is not None and step["arm"] not in _ARM_CHOICES: raise ...
```

A `### C-01 — …` heading inside that section raises `ProcedureParseError` → `main()` exits
non-zero → `run_gates.sh`'s `render_steps.py` live gate **FAILS** (it checks
`CONTROL_RC`/`V133_RC` before it diffs). That is not a cosmetic problem: it reds the per-wave
gate for the rest of the milestone.

**Resolution — put the `C-NN` list under its own H2 heading.** `_NEXT_H2_RE` terminates the
parsed section at the next `^## `, so a sibling `## Chip-sweep step list` is **invisible** to
`render_steps.py`. The existing gate stays green and unchanged (still 11 lines per arm, diff
empty). Cost: the `C-NN` list gets **no arm-agnosticism gate of its own**.

Two options for closing that gap, with costs:

| Option | Cost |
|---|---|
| **(A) New H2 + widen `render_steps.py` to a second section** *(recommended)* — add `--section {P,C}` (or a `--heading` argument) and a matching id-prefix regex, then run the empty-diff gate **twice** in `run_gates.sh`, once per section | One tool edit plus two new `--selftest` legs (a `C-NN` positive fixture and a `C-NN`-in-`P` negative). Gives the chip list the same measured arm-agnosticism the WRV list has — which D-07 explicitly asks for ("re-confirm the … empty-diff gate after the edit"). The tool count stays 12+2, not 13+2, because `render_steps.py` already exists. |
| (B) New H2, no renderer change | Zero tool risk, but Amendment 4's own re-confirmation clause would be reporting a gate that does not cover the new text — a vacuous pass, precisely the shape Standing bench rule 9's discussion and `run_gates.sh`'s own "a suite that discovered nothing and exited 0" lesson warn about. |
| (C) Continue the `P-NN` numbering (`P-12…P-2N`) inside `## Step list` | Passes the regex and the ascending-order check for free, and inherits the gate with no tool edit. **But** it makes the WRV step list contain eleven steps that do not apply to a WRV cell and N steps that do not apply to a chip position, with no marker distinguishing them — reintroducing exactly the "roughly half the step list applies verbatim; the other half does not apply at all" defect Amendment 4 exists to fix. Rejected. |

**Recommend (A).** If the planner picks (B), Amendment 4's clause (a) must say plainly that the
new section is ungated and why.

### **Correction: `$ARM_BIN` is not what makes the diff non-empty**

CONTEXT.md's R6 brief says to report "precisely how the … empty-diff gate is invoked and what
makes it non-empty (the `$ARM_BIN` token)". **The `$ARM_BIN` token is *not* the mechanism, and
believing it is would lead the planner to author a wrong Amendment 4 clause.** The tool's own
docstring is explicit (`render_steps.py:16-22`):

> *"The step's substitution tokens (`$ARM_BIN`, `$PORT`, `$CELL_ID`, …) are emitted **as the
> literal token text**, never expanded — expanding `$ARM_BIN` to one arm's absolute binary path
> would make the two renders differ *by construction*, which would defeat the very property this
> gate exists to measure. What `--arm` actually selects is *inclusion*: a step whose heading
> carries the marker `[arm: control]` is emitted only when `--arm control` is given…"*

And `PROCEDURE.md`'s own `## Arm substitution` section says the same:
*"because the token is never expanded in the rendered step list … the two arms' rendered step
lists are byte-identical"* and *"**The annotation syntax `[arm: control]` / `[arm: v133]`** … A
step carrying that marker would be included in only one arm's render, breaking the empty-diff
property SC#3 requires."*

**The only thing that makes the diff non-empty is an `[arm: control]` / `[arm: v133]` annotation
marker** (`_ANNOTATION_RE = r"\[\s*arm\s*:\s*([A-Za-z0-9_]+)\s*\]"`, consumed by
`render_for_arm`'s inclusion filter). Adding `$ARM_BIN` to a step body is harmless.

Note that Amendments 2 and 3 both wrote the reassurance the *other* way round — Amendment 2:
*"the new command block carries no arm-dependent token (`probe_board.py` takes no `$ARM_BIN`)"*;
Amendment 3: *"none of the four clauses adds an `[arm: …]` marker **or** an `$ARM_BIN` token"*.
Amendment 3 at least names the marker first. **Amendment 4 should state the marker as the
mechanism and, if it wants to mention `$ARM_BIN`, say explicitly that the token is emitted
literally and is therefore diff-neutral** — otherwise the phase propagates a small factual error
into the third document in a row.

### How the gate is invoked, verbatim from `run_gates.sh`

```bash
CONTROL_RENDER="$(mktemp)"; V133_RENDER="$(mktemp)"; CONTROL_RC=0; V133_RC=0
python3 "$TOOLS_DIR/render_steps.py" --arm control --procedure "$PROCEDURE_FILE" > "$CONTROL_RENDER" || CONTROL_RC=$?
python3 "$TOOLS_DIR/render_steps.py" --arm v133    --procedure "$PROCEDURE_FILE" > "$V133_RENDER"    || V133_RC=$?
CONTROL_LINES="$(wc -l < "$CONTROL_RENDER")"; V133_LINES="$(wc -l < "$V133_RENDER")"
if   [ "$CONTROL_RC" -ne 0 ] || [ "$V133_RC" -ne 0 ]; then FAIL "exited non-zero"
elif [ "$CONTROL_LINES" -eq 0 ] || [ "$V133_LINES" -eq 0 ]; then FAIL "empty render"
elif diff -u "$CONTROL_RENDER" "$V133_RENDER" > /dev/null; then PASS
else FAIL "non-empty diff"; fi
```

Three conditions, in order: **non-zero exit**, **empty render**, **non-empty diff**. Measured
live right now: `live gate PASS: render_steps.py -- diff empty, control=11 v133=11 lines`.

A runnable verify leg the planner can put directly in an `<automated>` block — note the `; RC=$?`
pattern, never a pipe:

```bash
cd /workspaces
P=.planning/v1.34/PROCEDURE.md
T=.planning/v1.34/tools/render_steps.py
python3 "$T" --arm control --procedure "$P" > /tmp/c.txt; RC_C=$?
python3 "$T" --arm v133    --procedure "$P" > /tmp/v.txt; RC_V=$?
test "$RC_C" -eq 0 -a "$RC_V" -eq 0
test -s /tmp/c.txt -a -s /tmp/v.txt
diff -u /tmp/c.txt /tmp/v.txt
test "$(wc -l < /tmp/c.txt)" -eq 11
```
The final line is the one that catches option (C) or an accidental `P-NN` insertion: **11 steps
before the amendment, 11 after.** If it becomes 12, the amendment leaked into `## Step list`.

### The five shared steps — what each says, verified to exist under those exact ids

All five exist. `grep -n '^### ' PROCEDURE.md` yields `P-01` … `P-11` with no gaps.

| Id | Heading | What it does | Shared by reference for the chip sweep |
|---|---|---|---|
| **P-01** | *Mount and declare* (line 139) | Operator mounts the shield and **declares the revision from the silkscreen**; silkscreen is authoritative because `hw_revision` cannot distinguish Rev 2.0 / Rev 2.2 / Modified Rev 0 (the A3 ADC band collides on 10 kΩ). No command; performer: operator. Record: `shield_rev_declared` (`$SHIELD_REV`) | **Yes, and already discharged** — Phase 161's A3/B2 left the rig mounted with `Rev 2.0` declared. Cite it; do not re-perform a mount |
| **P-02** | *Re-verify port identity* (line 146) | `probe_board.py --target --port --pins --out $CELL_DIR/board_probe.json` (authoritative signature) **plus** `FIRESTARTER_CONFIG_DIR=… $ARM_BIN -p $PORT hw` (non-authoritative controller line). RIG-02's "before any test step executes" capture point; `capture_provenance.py`'s `captured_at_step` is fixed at `2` for exactly this reason. Record: `board_signature`, `controller_string` | **Yes, per session** — standing bench rule 1 forbids inheriting a port across sessions, and this phase is a new session even though the rig is standing |
| **P-04** | *Flash this arm, then prove it by independent read-back* (line 172) | `git -C /workspaces/firestarter checkout <fw_sha>`; `git status --porcelain` must be empty; `cd /workspaces/firestarter && pio run -t upload -e $TARGET`; `judge_readback.py --target --port --flashed-arm --expect-arm --out-dir --pins`. Independent avrdude read with `-A` explicit, judged over `[0, hex_span)`. **D-05: runs at every flash, not only at bring-up.** Record: `fw_sha`, `host_arm_porcelain_clean`, `fw_readback_sha_judged`, `fw_readback_sha_whole_flash`, literal `commands` | **Yes — and it fires 2N times**, once per re-flash in D-17's interleave. Note the chip stays **seated** throughout (Leonardo is chip-out-exempt, `P-03`/`P-05` are Uno-class-only and do not apply) |
| **P-06** | *Set the pot once per cell* (line 211) | Claude states the target from `rig-pins.json` `chips.*.vpp_mv`, the operator sets it, Claude takes **exactly one** confirming read via `FIRESTARTER_CONFIG_DIR=… $ARM_BIN -p $PORT vpp`. If the `VPP is high` init guard fires, the pot is adjusted and the run restarts clean from this step — **the guard is never bypassed and `--force` is never used.** Record: the confirming reading plus `--force used? No` as a load-bearing line | **Yes, but with a stated deviation.** P-06 says *once per cell*; **D-11/D-13 say once per part** (own firmware reading each), with the meter out only at the two pot boundaries. Amendment 4 must name this as an intentional supersession for the chip-sweep shape, with D-11's reason (per-part VPP figures are materially better evidence for Phase 166's honesty ledger) |
| **P-11** | *Teardown* (line 347) | Re-run `probe_board.py` to a **distinct** path (`board_probe_teardown.json`); the **two-assertion** config-dir check in order; a completeness assertion that every position of this cell has a row and `render_evidence.py --check` is green; and the cell-agnostic **leave-state declaration** (board, port, arm, chip seated, pot, shield) | **Yes, with two adjustments** — the completeness assertion must target `CHIP-EVIDENCE.jsonl` + `render_chip_evidence.py --check`, and assertion (2)'s recomputed config-dir SHA is now load-bearing for the R3 copy-out invariant |

`P-03`, `P-05`, `P-07`, `P-08`, `P-09`, `P-10` do **not** apply: `P-03`/`P-05` are Uno-class-only;
`P-07`/`P-09` write a pre-computed `IMAGE-PLAN.json` image and judge a full-device SHA; `P-08` is
the two-chip rotation within a cell; `P-10` is the per-cell arm switch, which D-17 replaces with
a per-divergence interleave. Amendment 4 should list these six as explicitly not-applicable rather
than leave it to inference — Amendment 2's own lesson was that *"a step whose literal command must
be inferred by analogy rather than read is exactly the failure mode this document's 'prescriptive,
not prose' contract exists to prevent."*

### The Amendment 3 re-confirmation, quoted as the precedent

> *"(c) Which cells ran under which text: every bring-up cell (`BRINGUP-uno`, `BRINGUP-uno328pb`,
> `BRINGUP-leonardo`, `BRINGUP-wrv`) ran under the pre-Amendment-3 text; **no real sweep cell
> (`A1`/`A2`/`A3-B2`/`B1`/`B3`) has run under either text** — Amendment 3 lands before the first
> sweep cell, so every sweep cell in this milestone runs under the new text. The arm-agnostic
> empty-diff render gate (`render_steps.py --arm control` vs `--arm v133`) was re-confirmed empty
> after this edit — none of the four clauses adds an `[arm: …]` marker or an `$ARM_BIN` token, and
> `$POSITION_ID` is already declared among the non-arm-dependent substitution tokens in
> `## Arm substitution`."*

Amendment 4's clause (c) is materially harder than Amendments 1–3's, because **three real sweep
cells have now run**. It must say, and it can say truthfully: *"`A1`, `A2` and `A3/B2` ran under
the Amendment-3 text and are unaffected — Amendment 4 adds a new section and corrects §Scope, and
changes no character of `## Step list`, so the text those three cells cite is byte-unchanged.
`B1` and `B3` (Phase 163) will run under `## Step list` at the Amendment-4 text, which for them is
identical to the Amendment-3 text. No chip-sweep position has run under any text; Amendment 4
lands before the first one."*

That claim — *"changes no character of `## Step list`"* — is mechanically checkable, and the plan
should check it rather than assert it:

```bash
python3 - <<'PY'
import re, subprocess, pathlib
def section(text):
    m = re.search(r'^##\s+Step list\s*$', text, re.M); s = m.end()
    n = re.search(r'^##\s+\S.*$', text[s:], re.M)
    return text[s:s+n.start()] if n else text[s:]
old = subprocess.run(["git","show","HEAD:.planning/v1.34/PROCEDURE.md"],capture_output=True,text=True).stdout
new = pathlib.Path(".planning/v1.34/PROCEDURE.md").read_text()
a,b = section(old), section(new)
print("PASS: ## Step list byte-unchanged" if a==b else "FAIL: ## Step list changed")
raise SystemExit(0 if a==b else 1)
PY
```

### **Second blocking finding: P-11 assertion (1) is already red**

Amendment 3 clause (4) pinned `~/.firestarter`'s baseline inline: *"exactly one file,
`config.json`, 30 bytes; `config.json` sha256 `b323867c…`; tree sha `423546cd…`; mtime
**`1787817565`** (`2026-08-27 07:59:25 UTC`). A **change** to any of those four values … is the
`P-H1` finding."*

Measured live, this session:

```
/home/vscode/.firestarter/config.json   30 bytes
  mtime    1787854674          ← pinned value was 1787817565   ** CHANGED **
  sha256   b323867c1f01b22a705dd9caf003ab7302a249fe46772f5b02e44aaa2760dd79   ← unchanged
tree_sha   423546cd37b5b45d9654e5acd07bd7e2a3c9e1df77e4d5feb79951bf37329951   ← unchanged
```

This is the **fourth recurrence** CONTEXT.md predicted (`~/.firestarter/config.json` has changed —
mtime only, content identical — in all three Phase 161 cells). Consequence: **P-11 assertion (1)
as literally written is unconditionally red before this phase starts, and would book a false
`P-H1` halt at every position.**

The fix, with the alternative rejected explicitly:
- **Re-pin the mtime at phase start** as an Amendment 4 clause, recording the transition
  `1787817565 → <measured at phase start>` as the fourth recurrence, and keep asserting **all
  four** values. A further change *during* the sweep is then this phase's own `P-H1` finding.
- **Do not** drop the mtime from the assertion. It is the **only one of the four values that has
  ever changed** — content and tree SHA are stable across all four recurrences — so dropping it
  makes the assertion vacuous. That is the same vacuous-pass shape the two-assertion design
  exists to close.
- **Do not attempt removal** (sandbox denies it; Phase 160's unlogged kill during a removal
  attempt is what contaminated the directory).

### Formatting Amendment 4 to match

The house format, from Amendments 1–3, is one bold-led paragraph per amendment at the bottom of
the file, after the `*Procedure defined: …*` line, with the three clauses inline:

```markdown
**Amendment 4 — <date>, Phase 162 Plan NN:** (a) What changed: (1) … (2) … (b) Why: (1) … (2) …
(c) Which cells ran under which text: …
```

Amendment 4's clauses should be, at minimum: **(1)** §Scope + the header sentence corrected to
name two cell shapes; **(2)** a new `## Chip-sweep step list` H2 carrying `C-01…C-NN`, sharing
`P-01`/`P-02`/`P-04`/`P-06`/`P-11` **by reference** and listing `P-03`/`P-05`/`P-07`/`P-08`/`P-09`/
`P-10` as not-applicable; **(3)** the `$CHIP` token row in `## Arm substitution` widened from
`w27c512 | w29c020` to the eleven-part inventory, plus `$CHIP_TOKEN` declared (the case-sensitive
CLI token the report filename is keyed on — see R8); **(4)** P-06's once-per-cell pot rule
superseded per-part for the chip-sweep shape, per D-11/D-13, with the reason; **(5)** P-11's
completeness assertion pointed at `CHIP-EVIDENCE.jsonl` and `render_chip_evidence.py --check`;
**(6)** the `~/.firestarter` mtime baseline re-pinned; **(7)** the config-dir copy-out invariant
from R3 stated as a `C-NN` step obligation. And the closing re-confirmation sentence, with the
marker named as the mechanism.

**What the planner must do differently because of this.** Put `C-01…C-NN` under a **new H2**, never
inside `## Step list` — the `P-NN` regex would red the gate. Decide option (A) vs (B) for the
renderer explicitly and record the choice. Write the re-confirmation clause naming the
`[arm: …]` **marker** as the mechanism, not `$ARM_BIN`. Add the "`## Step list` byte-unchanged"
check and the `wc -l == 11` check as runnable legs. And **re-pin the `~/.firestarter` mtime in the
same amendment**, because otherwise the first `C-NN` position books a false `P-H1`.

---

## R7 — `rig-pins.json`'s `chips` map: extend or read live?

### What the `chips` entries actually contain

```json
"chips": {
  "w27c512": { "size_bytes":  65536, "pin_count": 28, "package": "DIP28",
               "vpp_mv": 12000, "algorithm": 7, "stamp_width": 16 },
  "w29c020": { "size_bytes": 262144, "pin_count": 32, "package": "DIP32",
               "vpp_mv": 12000, "algorithm": 5, "stamp_width": 32 }
}
```

Six fields. Five are chip facts; **`stamp_width` is a WRV artifact only** — it is
`gen_addr_image.py`'s address-stamp width for the generated write image, and a chip-sweep
position generates no image, so it is meaningless for the nine new parts.

### Who reads them, and what breaks

Exactly three call sites across the twelve tools:

| Site | Code | Behaviour on a missing part |
|---|---|---|
| `capture_provenance.py:613` | `chip_cfg = pins["chips"][args.chip]` inside a `try/except KeyError` → `print("FAIL: rig-pins.json missing expected key: …"); return 1` | **Hard refusal, exit 1.** Named, not silent — good — but total |
| `capture_provenance.py:764-765` | `"chip_package": chip_cfg["package"]`, `"chip_size_bytes": chip_cfg["size_bytes"]` | unreachable if the above refused |
| `append_evidence.py:212` | `if chip not in pins.get("chips", {}): violations.append(f"rig-pins.json has no chips entry for chip {chip!r}")` | accumulated violation → refusal |
| `append_evidence.py:258-261` | `chip_cfg = pins.get("chips", {}).get(chip, {})`; `family = "0x%02x (%s)" % (chip_cfg.get("algorithm", 0), _CHIP_LABEL.get(chip, "UNKNOWN"))` | **`.get`-guarded — this is the silent-degradation path**: absent the validate step, a missing part would render `family` as `0x00 (UNKNOWN)` rather than fail |

So one hard refusal, one accumulated refusal, and one `.get` fallback that would silently write
`0x00 (UNKNOWN)` into a locked column if the validate step were ever bypassed. The sibling
appender must **not** copy the `.get(…, 0)` idiom for `algorithm`; it should hard-refuse.

### **The blocker CONTEXT.md does not name: `_CHIP_CHOICES` is an argparse hard gate**

```python
# capture_provenance.py:77
_CHIP_CHOICES = ["w27c512", "w29c020"]
# capture_provenance.py:141
ap.add_argument("--chip", required=True, choices=_CHIP_CHOICES)
```

`argparse` rejects `--chip sst27sf512` with a usage error and **exit 2**, *before* `rig-pins.json`
is ever read. So extending the `chips` map alone is **not sufficient**.

This directly contradicts CONTEXT.md's `<code_context>` claim that `capture_provenance.py` is
*"Reusable as-is for the chip sweep's positions"*. It is reusable, but not as-is: it needs a
one-line change **and** the pins extension.

A second, smaller blocker in the same tool: the nine new parts have **no row in
`IMAGE-PLAN.json`**, and `resolve_image_plan_fields()` hard-refuses on a missing row. The
`--no-image-plan` flag exists and does exactly the right mechanical thing (writes
`image_mask`/`image_stamp_width`/`image_sha` as an explicit not-measured placeholder naming the
reason) — but its own help text scopes it to *"a bring-up pre-proof cell that never generates a
chip image (**no chip write ever runs here**), not a temporarily-pending sweep position"*. A chip
position **does** write the chip; it just does not write a *pre-computed image*. The mechanism
fits; the documented rationale does not. Amendment 4 (or the flag's help text) must widen it, or
the plan must record the deviation explicitly.

### Recommendation, with the cost of each option named

**Do both, in Wave 0: extend `rig-pins.json`'s `chips` map to the full inventory, and derive
`_CHIP_CHOICES` from it rather than duplicating the list.**

```python
# capture_provenance.py — replace the hardcoded list with a derivation
_CHIP_CHOICES = sorted(json.loads(_DEFAULT_PINS.read_text())["chips"])
```

This is the same class of fix as Phase 160's `hex_span_expected_by_arm` correction: *a pinned
constant that duplicates a fact already held elsewhere*. Deriving it means the map is the single
source of truth and the two can never drift.

| Option | Cost |
|---|---|
| **(A) Extend the map + derive `_CHIP_CHOICES`** *(recommended)* | Touches a tool load-bearing for the 20 WRV positions — so the change must be covered by a new `--selftest` leg (a fixture pins file with an extra chip is accepted; one with the chip absent is refused) and the full `run_gates.sh` must be green before any part runs. The map becomes a **rig asset Phase 163 and Phase 166 inherit**, which is why CONTEXT.md's deferred list warns it "should not be done casually mid-sweep" — so do it in Wave 0, from the DB, by a script, committed as one atomic change, never incrementally as parts come up |
| (B) Read the app DB live inside the tools | No pins edit, always current — but it makes a meta-repo bench tool **import from a sub-repo arm**, which the D-16 boundary forbids in the strongest terms (`append_evidence.py`'s own header: *"Nothing here is imported by, or imports from, either sub-repo"*). It would also make the rig's record depend on the arm under test, destroying the independence that makes the record an oracle. **Rejected on principle, not on cost** |
| (C) Skip `capture_provenance.py` for the chip sweep | Zero tool edits, but loses `host_arm_sha`, `host_arm_porcelain_clean`, `config_dir_sha`, `interpreter`, `dep_freeze_sha`, `eeprom_calibration`, `board_signature`, `controller_string` and the readback cross-check — i.e. 19 of the 49 proposed `record_keys`, and every field `gate_record.py` can actually check. The chip rows would be materially weaker evidence than the WRV rows in the same milestone. Rejected |

**What to put in the nine new entries.** Derive them from the app DB by script, not by hand; the
values verified live this session are:

| slug | size_bytes | pin_count | package | vpp_mv | algorithm | note |
|---|---|---|---|---|---|---|
| `w27e512` | 65536 | 28 | DIP28 | 12000 | 7 | shares `W27C512,W27E512` DB row, id `0xda08` |
| `sst27sf512` | 65536 | 28 | DIP28 | 12000 | 7 | id `0xbfa4` |
| `fm1608` | 8192 | 28 | DIP28 | 12000 | 40 (`0x28`) | `chip_id_check: false`; **`vcc_mv: 3300`, see R2** |
| `w27e040` | 524288 | 32 | DIP32 | 12000 | 8 | pinout `DIP32_STD`, **not** `DIP32_27C020` (size gate) |
| `sst39sf040` | 524288 | 32 | DIP32 | 12000 | 6 | id `0xbfb7` |
| `w29c040` | 524288 | 32 | DIP32 | 12000 | 5 | id `0xda46` |
| `am27c020` | 262144 | 32 | DIP32 | **13000** | 8 | pinout `DIP32_27C020`, id `0x197` |
| `m27c512` | 65536 | 28 | DIP28 | **13000** | 7 | id `0x203d`; resolves to **SGS-THOMSON** |
| `2516` | 2048 | 24 | **DIP24** | **25000** | 11 (`0x0B`) | named absence — present in the map for completeness, never used |

**Omit `stamp_width`** on the nine (it is WRV-only) and say so in a `chips_note`. Nothing indexes
it for these parts: `capture_provenance` hard-indexes only `package` and `size_bytes`, and
`append_evidence`'s `stamp_width` comes from `IMAGE-PLAN.json`, not from `chips`.

Add a `chip_token` field to each entry too — see R8's casing trap. The report filename is keyed on
the token **as typed**, and pinning it next to the slug is the cheapest way to stop a lower-case
invocation from writing to a different file than the appender reads.

Also extend `append_evidence.py`'s `_CHIP_LABEL` **or**, better, give the sibling appender its own
label map from the v1.16 `PROTOCOL-LEDGER.md` bucket names (`EPROM-STD`, `EPROM-QUICK`,
`FLASH-AMD-STD`, `FLASH-AMD-ALT`, `SRAM-STD`, `EPROM-LEGACY`) so the two files' `family` columns
read consistently.

### **A `family`-column trap worth pre-empting**

v1.15's `EVIDENCE.md` labels FM1608's family **`0x40 (SRAM_STD / FRAM)`**. The DB algorithm is
**40 decimal = `0x28`**. `.planning/v1.16/ledger/PROTOCOL-LEDGER.md` already caught and retired
this: *"EVIDENCE labels FM1608 family `"0x40 (SRAM_STD / FRAM)"` — `0x40` is decimal 40 = hex
`0x28` (NAME-04 conflation, retired in PROTOCOLS.md §1.10)"*. Since the sibling appender formats
`family` as `"0x%02x" % algorithm`, it will correctly emit `0x28` — which will **look like a
divergence against v1.15's `0x40`**. It is not. State it in the FM1608 row's `anomalies` once.

Compounding it: **`0x40` also means `CTRL_READ_WRITE`** in the v1.18 AM27C020 fix. The same token
carries two unrelated meanings in this project's record; do not let a search conflate them.

### `hex_span_expected_by_arm` — and why the legacy scalar must not be used

```json
"leonardo": {
  "hex_span_expected": 25098,
  "hex_span_expected_by_arm": { "control": 28170, "v133": 25098 },
  "hex_span_expected_note": "Same arm-dependence defect as targets.uno.hex_span_expected_note
     (measured from BUILD-MANIFEST.json: control=28170 B, v133=25098 B). Fixed here in 160-08 …"
}
```

The `uno` note spells out the failure mode in full, and it applies verbatim to the Leonardo:

> *"`hex_span_expected` (the single flat value above) is arm-AGNOSTIC for a quantity that is
> genuinely arm-DEPENDENT … **The flat value happens to equal v133's own span and would silently
> reject a correctly-flashed control-arm read-back as 'not the artifact the manifest describes'.**
> `hex_span_expected_by_arm` is the authoritative, arm-aware replacement
> `judge_readback.py`'s `cross_check_hex_span()` now consults first (keyed by `--expect-arm`);
> `hex_span_expected` is kept, unedited, only for backward compatibility."*

**Leonardo: control = 28170, v133 = 25098.** The legacy scalar `25098` equals v133's, so it fails
**asymmetrically** — a v1.33 read-back would pass and a control read-back would be rejected. In
this phase that matters more than it did in Phase 161: **D-17 re-flashes to the control arm and
back for every divergence**, so the control-arm judgement runs N times, and a tool or a verify leg
that reached for the flat key would red every one of them and look like a rig fault.

`judge_readback.py` already consults `hex_span_expected_by_arm` first, so the tool is safe. The
exposure is a **hand-authored `<automated>` leg that hardcodes 25098** — which is precisely
Phase 160's four-times-recurring hardcoded-arm-agnostic-constant defect. See R8.

### How the plan proves R7 at execution time

```bash
# 1. the map covers every part the sweep names, and _CHIP_CHOICES agrees with it
python3 -c "
import json
pins=json.load(open('.planning/v1.34/rig-pins.json'))
need={'w27c512','w27e512','sst27sf512','fm1608','w27e040','sst39sf040','w29c040','w29c020','am27c020','m27c512','2516'}
have=set(pins['chips']); missing=need-have
assert not missing, f'rig-pins.json chips missing: {sorted(missing)}'
for c in sorted(need):
    e=pins['chips'][c]
    for k in ('size_bytes','pin_count','package','vpp_mv','algorithm','chip_token'):
        assert k in e, (c,k)
print('PASS: chips map covers', len(need), 'parts with all required fields')
"
# 2. capture_provenance accepts every one of them (argparse gate, no device touched)
for c in w27e512 sst27sf512 fm1608 w27e040 sst39sf040 w29c040 am27c020 m27c512; do
  python3 .planning/v1.34/tools/capture_provenance.py --chip "$c" 2>&1 | grep -q "invalid choice" \
    && { echo "FAIL: --chip $c still rejected by argparse"; exit 1; }
done; echo "PASS: --chip accepts all nine"
# 3. the arm-aware hex span is what a leg must use — assert both values, never the scalar
python3 -c "
import json; t=json.load(open('.planning/v1.34/rig-pins.json'))['targets']['leonardo']
assert t['hex_span_expected_by_arm']=={'control':28170,'v133':25098}, t
print('PASS: leonardo hex_span_expected_by_arm control=28170 v133=25098')
"
# 4. the WRV path is undisturbed — the whole suite, exit code taken directly
bash .planning/v1.34/tools/run_gates.sh --quick; echo "run_gates rc=$?"
```

**What the planner must do differently because of this.** Treat the `chips`-map extension as a
**Wave 0 deliverable with its own gate**, not a mid-sweep convenience — CONTEXT.md's deferred list
is right that it becomes an inherited rig asset, and the correct response to that is to do it
once, atomically, from the DB, before the first part. Change `_CHIP_CHOICES` to a derivation, not
a longer literal. Decide and record how `--no-image-plan` is used on a position that *does* write
the chip. Pre-empt the `0x28`-vs-`0x40` family trap in the FM1608 row. And never let a verify leg
mention `25098` without the arm it belongs to.

---

## R8 — Runnable-verify-leg mechanics (the anti-defect assignment)

The standing warnings this section discharges: Phase 160's **hardcoded-arm-agnostic-constant
defect recurred four times**; the GSD planner has previously written literal `&amp;&amp;` into
`<automated>` blocks, making 30 of 37 legs unrunnable; and `check_permitted_claims.py`'s `_HERE`
resolves to the checker's own directory, so it scanned nothing and exited 0. This phase spans ten
parts plus re-runs, "where one wrong constant is ten false results."

### The gotchas, each with its one-line reason

| # | Rule | Reason |
|---|---|---|
| 1 | **`run_gates.sh`'s exit code is taken directly — never through a pipe.** `bash …/run_gates.sh; RC=$?`, or `if bash …/run_gates.sh; then`. Never `\| tee`, never `\| tail`. | The script's own exit code (0/1/2) is the gate; a pipe hands you the last command's status instead. Standing rule from CONTEXT.md's discretion list. |
| 2 | **`FIRESTARTER_CONFIG_DIR=/workspaces/.planning/v1.34/config` inline on every command that invokes an arm binary or a tool that shells out to one.** Never `export`. | `config.py` computes `HOME_PATH`/`DATABASE_FILE`/`PIN_MAP_FILE` as **import-time** constants; a session export fixes only call-time consumers and silently leaves the DB and pin-map on `~/.firestarter`. Standing bench rule 9. |
| 3 | **A missing inline prefix is undetectable from argv** — the only detector is asserting `~/.firestarter` unchanged at teardown. | A shell `FOO=bar cmd` assignment is stripped before exec and never reaches the child's `argv`, so `gate_record.check_commands` has nothing to inspect. P-11 says so explicitly. |
| 4 | **`python -P` on every `import firestarter` probe; prefer the arm's own `.venv/bin/python`.** | `/workspaces/firestarter` (the firmware repo) wins as a PEP 420 namespace portion and the probe silently prints `None` without `-P`. Forbidden-invocations table. |
| 5 | **`pio` only with cwd `/workspaces/firestarter`.** Record the cwd with the argv. | The generated, gitignored `/workspaces/platformio.ini` has a duplicate `[platformio]` section that aborts `configparser`; the identical command string succeeds or fails on cwd alone. |
| 6 | **Bare `touch_1200.py`, never `--wait-new-port`.** | Measured on this exact board (160-10): the Caterina 1200-baud touch returns on the **same** node; `--wait-new-port` timed out after 3 s with the node list unchanged. `measured_post_touch_port_behavior: "same_node"`. |
| 7 | **avrdude read-back with `-A` explicit** — and use `judge_readback.py`, which already does it. | Without `-A` avrdude truncates trailing `0xFF` and the read-back is short; `judge_readback.py:29,215` names this Pitfall 2 and has a `--selftest` negative leg for the truncation symptom. |
| 8 | **Never `--force`/`-f`/`-b`/`--no-blank-check`/`--skip-erase`; never bare `firestarter`.** | `gate_record.check_commands` rejects them by **exact token match anywhere in the argv**, and `forbidden_argv0` names the bare binary as a third un-named arm on `PATH`. A leg that uses one will be refused at append time, after the bench session. |
| 9 | **Never hardcode `25098` (or `28170`, `22952`, `26026`, `23000`, `26074`).** Read `hex_span_expected_by_arm[<arm>]` from `rig-pins.json`. | Phase 160's four-times-recurring defect. The Leonardo flat scalar equals v133's span, so a hardcode fails **only on the control arm** — and D-17 runs the control arm N times. |
| 10 | **Write `&&` as `&&` inside `<automated>`, never `&amp;&amp;`.** Prefer one command per line over chained ones. | On record: a planner previously HTML-escaped the operator and 30 of 37 legs became unrunnable. One-command-per-line removes the failure mode rather than relying on care. |
| 11 | **A tool's `_HERE`-derived default path must be checked, not assumed.** If a leg passes a path, pass an **absolute** one. | `check_permitted_claims.py`'s `_HERE` resolved to the checker's own directory, so it scanned nothing and exited 0 — a green that meant nothing. |
| 12 | **`--chip-token` casing is load-bearing.** `dev test W27C512` writes `dev-test-W27C512.json`; `dev test w27c512` writes `dev-test-w27c512.json`. | `_sanitize_chip_token` (`cli_handlers.py:2195-2210`) preserves alphanumerics and replaces everything else with `_` — it does **not** normalise case, and the filename is built from the token **as typed**, not from the canonical DB name. The appender's copy-out reads that exact path. Pin the token per part in the plan and in `rig-pins.json`. |
| 13 | **`W27C512` and `W27E512` share one DB row but produce different report files** — so no collision, but also **no way to tell the two reports apart by content**: both report `auto_capture.chip` as the token, and both carry chip-id `0xDA08`. | Verified live. The `--chip-token` cross-check in the appender is the only guard against copying part 1's report into part 2's row. |
| 14 | **`M27C512` resolves to vendor `SGS-THOMSON`, not `ST`** (two DB rows exist with identical electrical/programming data; `get_eprom` returns the SGS-THOMSON one). | The roadmap calls the physical part "ST M27C512". Record the human label and the resolving DB name separately, as v1.15 Phase 83 already did: *"'ST M27C512' is a human label; resolving DB name is `M27C512`."* |
| 15 | **`dev test` takes exactly one argument and one flag.** Every v1.21-era flag (`--destructive`, `--output-dir`, `-y`, `--submit`) errors as unknown. | Verified in `cli_handlers.py:2386-2400`; the `--output-dir` removal is why the report path is fixed and why the copy-out exists. |
| 16 | **Do not run under `--auto` / `--chain` / any auto-advance mode.** `autonomous: false` on a plan is not self-protecting. | Standing bench rule 7 — those modes auto-approve the `human-verify` checkpoints every physical step depends on. |
| 17 | **`human-verify` checkpoints only at the chip swap, the JP4 change and the pot adjustment.** No park prompts, no "continue?" gates. | Phase 161 D-02, carried: *"I dont want any handover until a real physical action is needed."* D-13 folds the pot step into the swap handover for exactly this reason — **one operator stop per part, not two**. |
| 18 | **The new tools must be stdlib-only.** | `run_gates.sh` runs each `--selftest` with the **system `python3`**, not an arm venv. |
| 19 | **`grep -q -- '"--selftest"'` is the advertisement test** — the literal double-quoted string must appear in the file. | Single-quoting the flag in `add_argument` would pass `argparse` and fail discovery. |
| 20 | **A blank or `0x303` VPP reading is a contact fault, not a voltage** — `P-H1`, not a pot adjustment. | Standing bench rule 5; the VPP/VPE monitors do not route to the socket. |
| 21 | **State the pot target, wait, take exactly ONE read. No monitor loops.** | Standing bench rule 4; the operator adjusts and meters solo. |
| 22 | **The VPP guard is asymmetric: high blocks, low warns.** Never chase the DB target upward past `vpp_mv + 500` as the firmware reads it. | `src/proms/eprom.cpp:530-537` — `> vpp_mv + 500` raises `MSG_ERR_VPP_HIGH` with `RESPONSE_CODE_ERROR` (downgraded only by the forbidden `FLAG_FORCE`); `< vpp_mv * 95/100` raises `MSG_WARN_VPP_LOW` with `RESPONSE_CODE_WARNING`. With Phase 161's ~×1.075 ratiometric ADC finding, a real 13.0 V rail reads ~13.98 V and **hard-ERRORs**. |
| 23 | **Assert the config dir is pristine *before* each `dev test`, not only after.** | R3's copy-out invariant; a dirty dir at step 1 means the previous report was never copied out, and the row about to be written would carry a wrong `config_dir_sha`. |

### The SC#2 pre-flight probe — the exact shape, and the trap in it

**No CLI surfaces `fw_board_identity`.** Grep across the v1.33 arm shows it reaching only
`hardware.ProgrammerIdentity.fw_board_identity` (`hardware.py:47`) and
`cli_handlers.py:2442`'s `AutoCapture` — i.e. only `dev test`'s own report. `dev hw` prints the
revision bucket, not the identity. So the pre-flight must call `read_programmer_identity()`
directly:

```bash
FIRESTARTER_CONFIG_DIR=/workspaces/.planning/v1.34/config \
/workspaces/.v1.34-arms/v133/.venv/bin/python -P -c '
from firestarter.config import ConfigManager
from firestarter.hardware import HardwareManager
cm = ConfigManager()
cm.set_value("port", "/dev/ttyACM0", persist=False)   # persist=False is LOAD-BEARING
i = HardwareManager(cm).read_programmer_identity()
print("fw_board_identity =", repr(i.fw_board_identity))
print("hw_revision       =", repr(i.hw_revision))
'
```

**`persist=False` is not optional.** `ConfigManager.set_value(key, value, persist=True)` is the
default (`config.py:171`) and a persisting write would call `_save_config()`, writing
`config.json` **inside the frozen config dir** — breaking the same SHA invariant R3 is about, from
the pre-flight, before any part has run. The `_transient_keys` mechanism exists for exactly this
(`config.py:107-113`: *"a one-shot `--port` … would otherwise stick forever and silently retarget
every later command"*).

`read_programmer_identity` opens **one** serial connection, energize/query only — *"no VPP-set, no
wire-dict, no `--force` (SAFE-02 clean)"* (`hardware.py:164-166`). ~10 s, chip stays seated
(Leonardo is chip-out-exempt). A `None` here is a `P-H1` halt and an opened defect, per the
discretion item: Phase 147 shipped the fix, so a null is a regression, not a carried gap.

Assert the config dir immediately after the probe (gotcha 23) — that is what turns "persist=False
was passed" into "no write occurred".

### The D-10 dedup outcome — how to detect all three states

`submit.py`'s off-TTY branch (`:684-698`), reached because `sys.stdin.isatty()` is False under the
executor's shell:

```python
prior_url, dedup_ran = find_prior_report_fn(fingerprint, run_fn=run_fn)
if not isatty_fn():
    url = build_issue_url(title, body)
    _print(url, console=console)
    if prior_url:
        _print(f"Note: you appear to have already reported this -- see {prior_url}.", …)
    elif not dedup_ran:
        _print("Note: the duplicate check could not run (gh absent, unauthenticated, or offline).", …)
    return
```

So the three outcomes are distinguished from the console log as:

| Outcome | Detection |
|---|---|
| found a prior report | the log contains `Note: you appear to have already reported this -- see ` |
| **could not run** | the log contains `Note: the duplicate check could not run` |
| **ran, found nothing** | the log contains the `https://github.com/…/issues/new?…` URL line and **neither** Note string |

The third state is proven by an **absence**, which is why the appender should scrape it from a
captured console log rather than have a human assert it. `submit.py` differs **~103 lines** between
the two arms (measured), which is D-10's whole reason for letting the path run.

For CLOSE-04, the criterion explicitly refuses assertions, so capture **pasted command output**
before and after the sweep:

```bash
gh issue list --repo henols/firestarter_prom --state all --limit 1000 --json number | \
  python3 -c "import sys,json;print('issue count:',len(json.load(sys.stdin)))"
```
Run it once at phase start and once at phase end, paste both outputs verbatim, and note that
`build_issue_url` produces a *prefilled new-issue URL*, not a filed issue — nothing is created.

### Proving each of R1–R8 at execution time

| # | Provable how | Needs the bench? |
|---|---|---|
| **R1** | `python3 -c` over `.planning/v1.18/bench/EVIDENCE.json` asserting the `phase99_deferral` cell's `bits_flipped` and `anomalies` contain `0x1da00`/`0x16600`/`64-byte`/`-b`; the live `derive_plan` probe asserting AM27C020's write region is `(261888, 256)`; `db.get_eprom("AM27C020")["pin-map"] == "DIP32_27C020"`. The **continuity read** (`dev consistency-check AM27C020 --runs 1` == `5586826791…`) — **operator/bench** | Partly. The record comparison is desk-provable; the continuity read is bench |
| **R2** | The three commands in R2 §"How the plan proves this" — wire-dict key set, negative grep for a VCC setter, byte-diff of the two arms' DB rows. All desk-provable | **No** |
| **R3** | The config-dir SHA round-trip (`77adfdd2…` → dirty → `77adfdd2…`) as a `--selftest` leg; `run_gates.sh` reporting `14 / 14` and 7 live gates; the appender's 16 selftest legs | **No** |
| **R4** | The `locked_columns` byte-comparison against `EVIDENCE.jsonl`'s; `gate_record.py --jsonl CHIP-EVIDENCE.jsonl` green; `render_chip_evidence.py --check` green; the `close01_counting_rule` and `chip_sc04_rule` evaluated as scripts; `position_count_expected == 20` unchanged in the WRV file | **No** |
| **R5** | The live `derive_plan` probe (per-part shape); the `EVIDENCE.jsonl` anchor assertions. The **actual durations** are the phase's own new measurements — **bench** | Partly |
| **R6** | `render_steps.py --arm control` vs `--arm v133` exit-0/non-empty/diff-empty plus `wc -l == 11`; the `## Step list` byte-unchanged git check; the `~/.firestarter` four-value assertion against the **re-pinned** baseline | **No** |
| **R7** | The four commands in R7 §"How the plan proves R7" | **No** |
| **R8** | Each gotcha is either enforced by a tool (`check_commands`, `judge_readback`'s `-A`, `hex_span_expected_by_arm`) or asserted by a leg. The pre-flight probe's `persist=False` is proven by the config-dir SHA being unchanged **after** the probe | Probe is bench; the rest is desk |

**Operator-verified steps, named plainly** (no automated substitute exists):
1. the silkscreen declaration `Rev 2.0` (P-01) — `hw_revision` cannot distinguish the three shields;
2. every chip seating and the two JP4 changes;
3. the two multimeter readings at the pot boundaries (D-13) — Claude never meters;
4. socket VCC on FM1608 — **and R2 recommends not asking for it**;
5. program-window VPP/VCC under load — **structurally unavailable**, deferred since Phase 97;
6. the actual `dev test` durations, verdicts and symptoms for all ten parts.

**What the planner must do differently because of this.** Author every `<automated>` leg one
command per line with literal `&&` only where unavoidable; pass absolute paths; read every
arm-dependent constant from `rig-pins.json` keyed by arm; put `FIRESTARTER_CONFIG_DIR=` inline on
every arm-touching line; take `run_gates.sh`'s exit code directly. Pin `--chip-token` casing per
part. Use `persist=False` in the pre-flight and assert the config-dir SHA immediately after it.
Scrape the D-10 dedup outcome from a captured console log rather than asserting it.

---

## Standard Stack

No external library is added or considered. The "stack" for this phase is the existing rig, and
it is prescriptive: **use these, do not build alternatives.**

### Core — reuse unchanged

| Component | Where | Purpose | Why standard here |
|---|---|---|---|
| `run_gates.sh` | `.planning/v1.34/tools/` | per-wave gate; fail-closed discovery | Already proven to fail closed with exit 1; measured green today at 12/12 |
| `gate_record.py` | same | record-shape gate | **Fully schema-driven** — gates the sibling JSONL with no argument change (R3) |
| `render_evidence.append_row_to_file()` | same | the JSONL append itself | Generic; carries six guarantees the sibling must not re-implement |
| `capture_provenance.py` | same | per-position provenance | Reusable **after** the two-line R7 fix; supplies 19 of the 49 `record_keys` |
| `judge_readback.py` | same | D-17's per-re-flash proof | `-A` explicit, arm-aware `hex_span_expected_by_arm` |
| `probe_board.py`, `touch_1200.py`, `check_arms.py` | same | P-02 / P-04 / P-11 | Measured contracts, unchanged since Phase 160 |
| `render_steps.py` | same | the arm-agnosticism gate | Possibly widened to a second section (R6 option A) |
| v1.33 and control arm venvs | `/workspaces/.v1.34-arms/*/` | the two arms under test | Pinned in `rig-pins.json`; the bare `firestarter` on `PATH` is a forbidden third arm |

### Supporting — new in this phase

| Component | Purpose | When |
|---|---|---|
| `append_chip_evidence.py` | derive + append one chip row; copy the report out **and remove the source** | every position, immediately after its `dev test` |
| `render_chip_evidence.py` | regenerate `CHIP-EVIDENCE.md`; `--check` byte-compare | paired with every append, and as a new live gate |

### Alternatives considered

| Instead of | Could use | Tradeoff |
|---|---|---|
| a sibling `CHIP-EVIDENCE.jsonl` | `EVIDENCE.jsonl` with a `CHIP-` prefix exclusion | Already rejected by D-08: 31 WRV columns as `"not measured"` per row |
| two new tools | a `--chip` mode on `append_evidence.py` | Already rejected by D-08/D-09: welds two schemas into a tool load-bearing for 20 positions this phase must not disturb |
| extending `rig-pins.json` `chips` | reading the app DB live inside the tools | Rejected on the D-16 boundary, not on cost (R7) |
| copy-out-then-remove | a second config dir, or excluding `reports/` from the SHA | Both viable, both costlier; costs named in R3 |

**Installation:** none. No `pip`, no `npm`, no new dependency. Both new tools are **stdlib-only**
because `run_gates.sh` executes their `--selftest` with the system `python3`.

## Code Examples

Verified patterns, each read from a working tool in this repository.

### Reusing a sibling tool without importing across a package boundary
```python
# Source: .planning/v1.34/tools/append_evidence.py (the spec_from_file_location sibling idiom)
import importlib.util
from pathlib import Path

_HERE = Path(__file__).resolve().parent

def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, _HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

gate_record    = _load("gate_record")      # check_commands, _is_acceptable_not_measured
render_evidence = _load("render_evidence")  # append_row_to_file
```

### The append, delegated (never hand-rolled)
```python
# Source: .planning/v1.34/tools/render_evidence.py:234-310, as called by append_evidence.py
violations = gate_record.check_commands(row, pins)
if violations:
    for v in violations: print(f"FAIL: {v}", file=sys.stderr)
    return 1
render_evidence.append_row_to_file(Path(args.jsonl), row)   # extra-key, dup-id, prefix, atomic
```

### The config-dir invariant, before and after
```python
# Source: .planning/v1.34/tools/check_arms.py:201-210 (reuse it; do not re-walk)
check_arms = _load("check_arms")
PRISTINE = "77adfdd26ed8710c4a70882e6dc9ee7bb494286fe225000d581f9e730dd77ad0"
actual = check_arms.compute_config_dir_sha(pins["config_dir"])
if actual != PRISTINE:
    print(f"FAIL: config dir is dirty ({actual}) -- the previous run's report was not copied out",
          file=sys.stderr)
    return 1
```

### Deriving, never transcribing, a per-step verdict map
```python
# Source: diagnostic_report._steps_list()/_step_dict() -- the exported shape
report = json.loads(Path(args.report_json).read_text())
assert report["schema_version"] == "1.7", report["schema_version"]
steps = report["steps"]
step_verdicts   = {s["op"]: s["verdict"]   for s in steps}   # keys include "write-partial"
step_run_counts = {s["op"]: s["run_count"] for s in steps}   # 2 for read/write/verify/erase
step_durations  = {s["op"]: s["duration_s"] for s in steps}  # CYCLE SUM -- divide by run_count
write_row = next((s for s in steps if s["op"] in ("write", "write-partial")), None)
write_coverage = write_row["write_coverage"] if write_row else None
```

### An `<automated>` leg that takes an exit code directly
```bash
# Source: the standing rule in CONTEXT.md's discretion list; never pipe run_gates.sh
bash /workspaces/.planning/v1.34/tools/run_gates.sh --quick
RC=$?
test "$RC" -eq 0
```

### Reading an arm-dependent constant instead of hardcoding it
```bash
# Source: rig-pins.json targets.leonardo.hex_span_expected_note (the 160-08 fix)
ARM=control
SPAN=$(python3 -c "import json,sys;print(json.load(open('/workspaces/.planning/v1.34/rig-pins.json'))['targets']['leonardo']['hex_span_expected_by_arm'][sys.argv[1]])" "$ARM")
test "$SPAN" -eq 28170     # control; v133 is 25098. Never the flat hex_span_expected.
```

## Don't Hand-Roll

| Problem | Don't build | Use instead | Why |
|---|---|---|---|
| Appending a row to the sibling JSONL | a `json.dumps` + `open(…, "a")` | `render_evidence.append_row_to_file()` | It already does missing-key, **extra-key**, outcome-domain, duplicate-`position_id`, byte-unchanged-prefix and atomic-`os.replace` — six guarantees, and `append_evidence.py` already imports it via the sibling-`importlib` idiom |
| Rejecting a forbidden flag in a recorded argv | a `for flag in FORBIDDEN` loop | `gate_record.check_commands(row, pins)` | Exact-token match anywhere in argv, plus the `argv0` allow-list derived from `pins.arms[*].venv_bin`. Re-implementing it means two places to keep in sync with `forbidden_flags` |
| Deciding whether a value counts as "not measured" | a `startswith("not measured")` test | `gate_record._is_acceptable_not_measured` | It rejects a bare `"not measured"` with no reason — the whole point of the convention |
| Computing the config-dir SHA | a fresh `hashlib` walk | `check_arms.compute_config_dir_sha()` | The scheme (sorted relpath + content, `is_file()` only) is what `arms-provenance.json`'s recorded value was produced with; a different walk order silently produces a different digest |
| Judging a flash read-back | a hand-rolled `avrdude … flash:r:` | `judge_readback.py` | `-A` explicit (Pitfall 2), the pinned `avr-objcopy` normalisation, and `hex_span_expected_by_arm` keyed by `--expect-arm` |
| Parsing `dev test`'s per-step results | a regex over the console table | the persisted `dev-test-<TOKEN>.json` | The console `render()` drops every non-`_RAN_VERDICTS` row and suppresses NA reasons; the JSON is the complete record and is the same `to_dict()` both surfaces derive from |
| Deriving a per-op duration | quoting `duration_s` | `duration_s / run_count` | `_fold_cycles` sums across cycles |
| A second config directory, a second procedure document, or a second gate script | any of them | extend what exists | D-08's and D-07's rejected alternatives both name the same failure: a second document is a second place every standing-rule change must be applied |

## Common Pitfalls

### Pitfall 1: the report lands in the frozen config dir
**What goes wrong:** the per-wave gate goes red from part 1 onward and every already-appended row's
`config_dir_sha` starts failing. **Why:** `get_config_dir()` is call-time and honours
`FIRESTARTER_CONFIG_DIR`; `compute_config_dir_sha` walks the whole tree. **Avoid:** copy out then
remove; assert `77adfdd2…` before and after every run. **Warning sign:** `check_arms.py` failing
inside an otherwise-green suite.

### Pitfall 2: an NA step booked as a divergence
**What goes wrong:** `erase` is NA on five of ten parts and `id` is NA on FM1608, so a naive
"prior said PASS, `dev test` says nothing" reads as a flip. **Avoid:** carry R5's per-part NA map
into the table template. **Warning sign:** more than ~4 divergences before any real red.

### Pitfall 3: a per-step lookup keyed on `"write"`
**What goes wrong:** the two UV parts emit `write-partial`, so their write cell silently reads
empty. **Avoid:** key on `{"write", "write-partial"}` everywhere. **Warning sign:** M27C512 and
AM27C020 both showing an empty write verdict.

### Pitfall 4: the control re-run overwrites the v1.33 report
**What goes wrong:** `dev-test-<TOKEN>.json` is a fixed path per token; D-17 re-runs the same
token on the control arm. **Avoid:** the copy-out is `$POSITION_ID`-keyed and runs before the
re-flash. **Warning sign:** two rows with identical `report_json_sha256`.

### Pitfall 5: chasing the DB VPP target upward on the 13 V pair
**What goes wrong:** a real 13.0 V rail reads ~13.98 V through the ~×1.075 ADC and trips
`MSG_ERR_VPP_HIGH`, which blocks and can only be bypassed with the permanently-withdrawn
`--force`. **Avoid:** D-12 — highest real rail that keeps the *firmware* reading under
`vpp_mv + 500`. **Warning sign:** `VPP is high: … > 13.0V` on M27C512 or AM27C020.

### Pitfall 6: a hardcoded `25098`
**What goes wrong:** passes on v1.33, fails on control — and D-17 runs control N times.
**Avoid:** `hex_span_expected_by_arm[<arm>]`. **Warning sign:** a read-back "mismatch" that only
ever appears on control-arm re-flashes.

### Pitfall 7: treating `chip_id_actual: null` as a missing measurement
**What goes wrong:** a "fix" that echoes the host's own expected value, presenting a
never-measured number as a measurement. **Avoid:** record the design note verbatim. **Warning
sign:** a plan task proposing to populate it.

## Environment Availability

| Dependency | Required by | Available | Version | Fallback |
|---|---|---|---|---|
| Standing rig: Leonardo `2341:8036` @ `/dev/ttyACM0`, Rev 2.0, v1.33 arm flashed (`5759dc8d`), W27C512 seated | CHIP-01 | inherited from Phase 161 A3/B2 — **re-verify per standing bench rule 1** | — | none; a changed port is `P-02`'s job, not a fallback |
| v1.33 arm venv `/workspaces/.v1.34-arms/v133/.venv/bin/{firestarter,python}` | every run | ✓ | app `cb189a9b…` | none |
| control arm venv `/workspaces/.v1.34-arms/control/.venv/bin/…` | D-17 re-runs | ✓ | app `6bfa6453…`, fw `8695ee52…` | none |
| Frozen config dir `/workspaces/.planning/v1.34/config` | every run | ✓ sha `77adfdd2…`, files `['.gitkeep','config.json']` | — | none — and see Pitfall 1 |
| 12 rig tools + `run_gates.sh` | every wave | ✓ `12 / 12` selftests, `ALL GATES PASSED` (`--quick`, measured) | — | none |
| system `python3` (stdlib only) | tool selftests | ✓ | 3.12 | none |
| `pio`, cwd `/workspaces/firestarter` | D-17 re-flashes | ✓ (used in Phase 161) | — | none |
| pinned avrdude 8.1 (`rig-pins.json` `avrdude.binary`) | `judge_readback.py` | ✓ | 8.1 | `avrdude_fallback` (system 7.1), named but not used unless the pinned one cannot open the port |
| `gh`, authenticated, network | D-10 dedup + CLOSE-04 counts | assume ✓ — **verify in Wave 0** | — | **yes, and it is recorded, not worked around**: `dedup_query_outcome = "could not run: …"` is a first-class value |
| Nine physical parts + the operator | CHIP-01 | operator-gated | — | a named absence per SC#1 |
| 2516 adapter / Rev 2.2 shield | *(not required)* | ✗ by declaration | — | **named absence, D-14** |
| Multimeter | D-11/D-13 | operator-only | — | `"not measured — <reason>"` |

**Missing with no fallback:** none identified — the rig is standing and complete for the ten parts.
**Missing with fallback:** the 2516 (named absence); `gh` (recorded outcome).

## Package Legitimacy Audit

**Not applicable — this phase installs no external packages.** Both new tools are stdlib-only by
requirement (`run_gates.sh` executes each `--selftest` with the system `python3`, R3), no
`pip`/`npm` step exists anywhere in the phase, and both sub-repos stay byte-unchanged. No package
name appears in any recommendation in this document. If the planner finds itself adding a
dependency, that is a signal the tool is doing too much, not a signal to run this gate.

## Validation Architecture

### Test Framework

This is a meta-repo bench phase; there is no `pytest` suite here. The equivalent is the rig's own
gate suite, and it is a real one (fail-closed discovery, proven to exit 1).

| Property | Value |
|---|---|
| Framework | `run_gates.sh` + per-tool `--selftest` (stdlib `python3`, no third-party runner) |
| Config file | `.planning/v1.34/tools/run_gates.sh` (discovery is `find -maxdepth 1 -name '*.py'`; no separate config) |
| Quick run command | `bash .planning/v1.34/tools/run_gates.sh --quick` — all selftests + `render_steps`/`render_evidence --check`/`gate_record`, skips the two live-arm/image gates |
| Full suite command | `bash .planning/v1.34/tools/run_gates.sh` — adds `check_rebuild.py` and `check_arms.py` |
| Exit-code rule | taken **directly**, never through a pipe (`; RC=$?`) |
| Measured baseline (today) | `tool self-tests run: 12 / 12`; `render_steps.py -- diff empty, control=11 v133=11 lines`; `ALL GATES PASSED` |
| Target after this phase | `tool self-tests run: 14 / 14`; **7** live gates (5 today + 2 new); `render_steps` still 11 lines per arm |

### Phase Requirements → Test Map

| Req | Behavior | Test type | Automated command | Exists? |
|---|---|---|---|---|
| CHIP-01 | Every part has a report artifact or a named absence; count reconciles to 11 | integration | `python3 .planning/v1.34/tools/render_chip_evidence.py --jsonl …/CHIP-EVIDENCE.jsonl --target …/CHIP-EVIDENCE.md --check` + the `close01_counting_rule` script | ❌ Wave 0 |
| CHIP-01 | The per-part plan shape is what this research measured | unit | the `derive_plan` probe in R5 §"How the plan proves R5" | ❌ Wave 0 (as a committed one-shot record) |
| CHIP-02 | No row carries a null `fw_board_identity` | unit (selftest leg 8) + integration | `python3 -c "import json;rows=[json.loads(l) for l in open('.planning/v1.34/bench/CHIP-EVIDENCE.jsonl')][1:];assert all(r['fw_board_identity'] for r in rows if not r.get('named_absence'))"` | ❌ Wave 0 |
| CHIP-02 | Pre-flight identity is non-null before any part runs | manual-only (needs the board) | the `read_programmer_identity` probe (R8), recorded as a bring-up datum | ❌ Wave 0 |
| CHIP-03 | Every row's `divergence_verdict` is exactly `same` or `diverges: <non-empty>`; no blank cells; every prior disposition sourced | unit (selftest leg 11) + integration | `gate_record.py --jsonl …/CHIP-EVIDENCE.jsonl --pins …` (field-presence) + a domain script over `divergence_verdict`/`prior_disposition_source` | ❌ Wave 0 |
| CHIP-04 | A control re-run for every diverging part and for no other | integration | the `chip_sc04_rule` script (R4) | ❌ Wave 0 |
| CHIP-05 | The four (five, with FM1608) known-carried parts cite their prior disposition inline | integration | a script asserting `known_carried != "no"` and `prior_disposition` non-empty for `w27e512`, `w27e040`, `w29c040`, `am27c020`, `fm1608` | ❌ Wave 0 |
| *(rig)* | The frozen config dir is pristine before and after every run | unit (selftest leg 4) + per-wave | the SHA round-trip leg (R3) | ❌ Wave 0 |
| *(rig)* | `EVIDENCE.jsonl` is untouched: 20 expected, 12 non-bring-up rows | integration | the WRV assertion script (R4) | ❌ Wave 0 |
| *(rig)* | `## Step list` is byte-unchanged and still renders 11 arm-identical lines | integration | the two legs in R6 | ✅ partly — `run_gates.sh` already runs the diff; the `wc -l == 11` and git-section checks are new |
| *(rig)* | Every recorded argv is free of forbidden flags and uses a pinned `argv0` | unit | `gate_record.check_commands`, delegated by the appender **before** the write | ✅ exists |

### Sampling Rate

- **Per task commit:** `bash .planning/v1.34/tools/run_gates.sh --quick` (exit code direct).
- **Per wave merge** — a wave is a pot/JP4 group: the **full** `bash .planning/v1.34/tools/run_gates.sh`,
  plus the config-dir pristine assertion, plus `gate_record.py --jsonl …/CHIP-EVIDENCE.jsonl`.
- **Per position** (tighter than a wave, because a chip position is a physical event that cannot be
  replayed): the appender's own refusals run before the row is written, and
  `render_chip_evidence.py --check` runs immediately after the append — the Amendment-3
  append-then-re-render pair, applied to the sibling file.
- **Phase gate:** full suite green, `14 / 14`, 7 live gates, both counting rules evaluating true,
  and the WRV file's `position_count_expected: 20` / 12-row state unchanged from the pre-phase
  snapshot.

### Wave 0 Gaps

- [ ] `.planning/v1.34/tools/append_chip_evidence.py` — with the 16 `--selftest` legs in R3; covers CHIP-01/02/03/05
- [ ] `.planning/v1.34/tools/render_chip_evidence.py` — with `--check`, deterministic, no timestamp; covers CHIP-01
- [ ] `.planning/v1.34/bench/CHIP-EVIDENCE.jsonl` line 1 `_schema` — the 9 locked columns byte-copied, the 40 extension columns, both counting rules; covers CHIP-01/04
- [ ] `.planning/v1.34/tools/run_gates.sh` — two new live gates (`render_chip_evidence --check`, `gate_record --jsonl CHIP-EVIDENCE.jsonl`)
- [ ] `.planning/v1.34/rig-pins.json` — `chips` map extended to eleven parts with `chip_token`; `_CHIP_CHOICES` derived from it in `capture_provenance.py` (+ a selftest leg); covers CHIP-01
- [ ] `.planning/v1.34/PROCEDURE.md` — Amendment 4: §Scope + header, `## Chip-sweep step list`, `$CHIP`/`$CHIP_TOKEN` tokens, P-06 supersession, P-11 retarget, `~/.firestarter` mtime re-pin, config-dir copy-out obligation
- [ ] `render_steps.py` — optional second-section support if option (A) in R6 is taken (+ 2 selftest legs)
- [ ] The desk-provable answers to R2 (three commands) and R5 (the `derive_plan` probe), run and **committed as records** before the first part is seated
- [ ] A pre-phase snapshot of `EVIDENCE.jsonl`'s row count + `position_count_expected`, to diff against at the phase gate

## Security Domain

`security_enforcement` is not disabled in `.planning/config.json`, so this section is included.
The phase writes no product code and ships no network-facing surface; the relevant scope is the
two new meta-repo tools and the one outbound network call.

### Applicable ASVS categories

| ASVS category | Applies | Standard control |
|---|---|---|
| V2 Authentication | no | no auth surface; `gh` uses the operator's existing credential |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| **V5 Input Validation** | **yes** | The appender parses a JSON report and a provenance JSON. Use `json.load` with an explicit `schema_version` check and a `--chip-token` cross-check; **never `eval`, never `pickle`**. Refuse on any unexpected shape rather than `.get`-defaulting — the `.get(…, 0)` idiom in `append_evidence.py:261` is exactly the silent-degradation path R7 flags |
| **V6 Cryptography** | **yes (hashing only)** | `hashlib.sha256` for artifact digests and the config-dir tree walk. Reuse `check_arms.compute_config_dir_sha` rather than re-implementing the walk. Never hand-roll a digest scheme |
| V7 Error handling & logging | yes | Accumulate-then-report by name; a kill runs under a numbered log with full stdout **and** stderr (161 D-08). Do not log the operator's `gh` token — `submit.py` already sanitizes report content via `sanitize_dict` before building a body |
| V12 File handling | **yes** | The appender copies files by an operator-supplied `--position-id`. Reuse `capture_provenance.resolve_out_path`'s discipline: **refuse a path that traverses out of the milestone dir**. `_sanitize_chip_token` shows the same concern on the app side |
| V13 API / network | limited | One outbound read-only `gh issue list`. It is **allowed and declared** (D-10) precisely so a v1.33 regression in that path is exercised rather than hidden |

### Known threat patterns for this stack

| Pattern | STRIDE | Standard mitigation |
|---|---|---|
| Path traversal via `--position-id` into the copy destination | Tampering | `resolve_out_path`-style containment check against the milestone dir |
| A report from the wrong part copied into a row | Tampering / Repudiation | the `auto_capture.chip == --chip-token` cross-check; D-05's derive-never-transcribe |
| A forbidden flag reaching the hardware | Tampering (irreversible on a UV part) | `gate_record.check_commands` exact-token match; `forbidden_flags` in `rig-pins.json` |
| Silent record drift (a row rewritten after the fact) | Repudiation | `append_row_to_file`'s byte-unchanged-prefix re-read + atomic replace; append-only by construction |
| A vacuous green gate (a suite that discovers nothing) | Repudiation | `run_gates.sh` exits 2 on zero discovered tools; `render_steps.py` refuses an empty section — both are prior lessons already encoded |
| Credential leakage through a filed issue | Information disclosure | nothing is filed off-TTY; `submit.py` sanitizes before building a body; the URL is prefilled, not posted |

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|---|---|---|
| A1 | Algorithm-8 (W27E040) full-device write throughput resembles algorithm-7's ~1964 B/s | R5 | The 512 KiB budget (~980 s) and its 3920 s fallback ceiling are wrong in either direction; a too-tight ceiling kills a healthy run, a too-loose one blocks the bench. **Mitigated** by the recommended part 5/6 swap, which makes SST39SF040 supply the class figure first |
| A2 | Algorithm-6 (SST39SF040) throughput is still ~2185 B/s, from v1.15's "~240 s" on older firmware | R5 | Same as A1. It is a same-rig figure but a different-firmware one, and quoted to no decimal |
| A3 | FM1608's 8 KiB write completes in single-digit seconds | R5 | Only affects the 8 KiB fallback ceiling (120 s), which is generous |
| A4 | The `erase` step on a stuck-bit part (W27E512, W27E040) fails fast rather than retrying long | R5 | Could make part 2 or 6 run far longer than budgeted. **Verify** by watching part 2, which is early and cheap |
| A5 | AM27C020 has not been touched at the bench since 2026-06-30, so its pre-read SHA is still `5586826791…` | R1 | Only affects the optional continuity read's interpretation. Grep across v1.19–v1.33 found no bench artifact, only doc mentions |
| A6 | `gh` is authenticated and online in the executor's environment | R8 / Environment | D-10's dedup outcome becomes `"could not run"` — which is a **recorded first-class value**, not a failure |
| A7 | The blank-check step's cost is read-speed-like | R5 | Minor; it is a single-run step on seven parts |
| A8 | `dev test`'s exit code and its docstring disagree in the both-BAD-and-marginal case (`max()` yields 2) | R4 | Only affects how `exit_code` is read. **Mitigated** by recording `step_verdicts` alongside it, which is interpretable regardless |

## Open Questions

1. **Does `render_steps.py` get a second section, or does `C-01…C-NN` go ungated?**
   - Known: a `C-NN` id inside `## Step list` reds the existing gate; a new H2 is invisible to the tool.
   - Unclear: whether the planner wants a tool edit inside a phase that is otherwise tool-light.
   - Recommendation: **option (A)** — D-07 asks for the gate to be re-confirmed, and re-confirming a
     gate that does not cover the new text is the vacuous-pass shape this project keeps naming.

2. **Does `--no-image-plan` cover a chip-sweep position?**
   - Known: the mechanism fits exactly; the help text's stated rationale ("no chip write ever runs
     here") does not.
   - Recommendation: widen the help text in the same Wave 0 edit that touches `_CHIP_CHOICES`, or
     record the deviation in Amendment 4. Do not use it silently.

3. **Should the 2516's absence row carry `arm: "v133"`?**
   - Known: it is the only way `position_count_expected: 11` counts over `arm == "v133"` cleanly.
   - Unclear: whether Phase 166 will read it as an implied run.
   - Recommendation: keep it, add the `named_absence` column and the convention text in R4, and
     make `op` read `not run — named absence`.

4. **Does a part showing read divergence get a follow-up `dev consistency-check --keep-files`?**
   - Known: `dev test` destroys the read bytes; only the divergence metric survives. The A2 N=3
     question is live and CONTEXT.md wants data points, not a closure.
   - Recommendation: decide **in the plan**, not at the bench. A 64 KiB follow-up is ~33 s; a
     512 KiB one is ~4.5 min. Suggest: yes for the 64 KiB and 256 KiB classes, ask the operator for
     the 512 KiB class.

5. **What is the pre-phase `~/.firestarter/config.json` mtime to re-pin?**
   - Known: `1787854674` as of this research. It may drift again before the phase starts.
   - Recommendation: measure it in Wave 0, at the moment Amendment 4 is written, and record the
     `1787817565 → <measured>` transition as the fourth recurrence.

## Sources

### Primary (HIGH confidence)
- Live execution against the v1.33 arm's own engine: `derive_plan` for all eleven tokens; `get_eprom`/`convert_to_programmer`/`get_eprom_config`/`_sanitize_chip_token` for all ten.
- Live execution of the rig: `bash .planning/v1.34/tools/run_gates.sh --quick` (12/12, all gates passed); `compute_config_dir_sha` scheme reproduced on a `/tmp` copy (four-state proof); `~/.firestarter` tree walk.
- `/workspaces/.v1.34-arms/v133/firestarter/` — `cli_handlers.py` (`_resolve_write_scope`, `dev_test`, `_sanitize_chip_token`, `_chip_id_fields`, the report path), `chip_test.py` (`derive_plan`, `_fold_cycles`, `_dispatch_read`, `_dispatch_multi_run`, `uv_slot_starts`, `full_device_region`, the verdict vocabulary, `repeat_policy_tag`), `diagnostic_report.py` (`to_dict`, `_step_dict`, `_write_coverage_line`, `dedup_fingerprint`, `build_db_diff`), `submit.py` (the off-TTY branch), `database.py` (`convert_to_programmer`), `config.py` (`ConfigManager.set_value(persist=…)`), `hardware.py` (`read_programmer_identity`).
- `/workspaces/.v1.34-arms/{control,v133}/tools/build_db.py` — `VCC_VOLTAGES`, the bits-11-8 decode, `_PHASE84_RELABEL`, the SRAM vcc→vdd correction.
- `/workspaces/firestarter/src/`, `/workspaces/firestarter/include/` — `rurp_common.cpp`, `hardware_operations.cpp`, `eprom_params.h`, `rurp_hw_rev_utils.h`; negative grep for a VCC setter.
- `.planning/v1.34/tools/` — `run_gates.sh`, `append_evidence.py`, `capture_provenance.py`, `gate_record.py`, `render_evidence.py`, `render_steps.py`, `judge_readback.py`, `check_arms.py`, `touch_1200.py`.
- `.planning/v1.34/` — `PROCEDURE.md` (Scope, standing rules, arm substitution, P-01…P-11, halt policy, write-duration definition, forbidden invocations, recording discipline, Amendments 1–3), `rig-pins.json`, `bench/EVIDENCE.jsonl` line 1 + all 16 rows, `bench/IMAGE-PLAN.json`, `bench/.gitignore`, `bench/cells/A3-B2/WRITE.md`.
- `.planning/v1.18/bench/EVIDENCE.json`; `.planning/v1.16/ledger/PROTOCOL-LEDGER.md`; `.planning/v1.15/bench/EVIDENCE.md` (Phases 81/82/83/84).
- `.planning/PROJECT.md`, `.planning/RETROSPECTIVE.md`, `.planning/STATE.md`, `.planning/MILESTONES.md` — the `DIP32_27C020` corroboration chain.
- `.planning/todos/pending/fm1608-byte0-write-never-lands-register-cache-elision.md`.
- `.claude/skills/devtest-rootcause/scripts/infoic_lookup.py` and upstream `infoic.xml @ a8efaedc` — FM1608's `voltages="0x0100"`, `type="4"`.

### Secondary (MEDIUM confidence)
- `.planning/phases/161-…/161-CONTEXT.md` D-08 (stall-ceiling pattern, quoted).
- `.planning/v1.15/bench/EVIDENCE.md`'s "flash3 slow path ~240 s/write" — same rig, older firmware, quoted to no decimal.

### Tertiary (LOW confidence)
- None. No claim in this document rests on a web search or on training knowledge; every factual
  claim is either read from this repository, read from the two arm worktrees, or produced by a
  command executed during this session.

## Metadata

**Confidence breakdown:**
- Standard stack (the rig's twelve tools and their contracts): **HIGH** — every contract read from source and the suite executed.
- Architecture (schema shape, appender interface, procedure mechanics): **HIGH** — `append_row_to_file` and `gate_record` proven generic by reading them; the config-dir failure proven empirically.
- Prior dispositions and comparability (R1): **HIGH** — quoted from the records, cross-checked across v1.15/v1.16/v1.18.
- FM1608 `vcc_mv` (R2): **HIGH** — traced end to end with `file:line` on both sides and confirmed byte-identical across arms.
- Duration budget (R5): **MEDIUM** — 64 KiB and 256 KiB classes rest on same-rig same-arm measurements; the 512 KiB and 8 KiB classes are derived and flagged as A1–A3.
- Pitfalls (R8): **HIGH** — each is either a tool contract read from source, a measured rig fact, or a recorded prior defect.

**Research date:** 2026-08-27
**Valid until:** 2026-09-10 (14 days). Shorter than the usual 30: `~/.firestarter/config.json`'s
mtime drifts on its own, the standing rig's port identity must be re-verified per session anyway,
and any `dev test` run by another phase would change the config dir's state.

