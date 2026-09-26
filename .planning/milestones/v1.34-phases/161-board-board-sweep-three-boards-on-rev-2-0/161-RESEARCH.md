# Phase 161: BOARD — Board Sweep, Three Boards on Rev 2.0 — Research

**Researched:** 2026-08-27
**Domain:** Hardware bench execution against a pre-built rig. No product code, no external dependencies, no packages.
**Confidence:** HIGH on everything measurable from the repository (all primary claims are `[VERIFIED]` from files or from `--help` output taken in this session); LOW only where the answer is "this has never been run and must be measured at the bench".

---

<user_constraints>
## User Constraints (from CONTEXT.md)

Full text, with rationale and rejected alternatives, at
`.planning/phases/161-board-board-sweep-three-boards-on-rev-2-0/161-CONTEXT.md:46-279`.
**The planner must read that file; this section reproduces the locked properties only.**

### Locked Decisions

- **D-01:** **Three plans, one per cell** — `A1`, `A2`, `A3/B2`, each running `P-01`→`P-11` end-to-end across both arms and both chips. *(User's choice.)*
- **D-02:** **No handover until a real physical action is needed.** *(User's explicit instruction, verbatim: "I dont want any handover until a real physical action is needed.")* The executor stops **only** at `P-01`, `P-03`, `P-05`, `P-06`, `P-08` and their repeats across the arm switch at `P-10`. **No artificial park prompts, no "continue?" checkpoints, no confirmation gates that do not correspond to the operator physically touching the rig.**
- **D-03:** **Records are still written per position — that is not a handover.** Each position's `provenance.json`, `WRV-VERDICT.json` and `EVIDENCE.jsonl` row are written as that position completes.
- **D-04:** **`bash .planning/v1.34/tools/run_gates.sh` is the per-cell gate.** **Measure its exit code directly, never through a pipe.**
- **D-05:** **Build a phase-owned `append_evidence.py`.** *(User's choice.)* It reads `provenance_<position>.json`, `WRV-VERDICT.json` and `READBACK-VERDICT.json` and **derives every machine-readable field itself** — never transcribed. The plan supplies only the genuinely human fields (`verdict` prose, `anomalies`). **Constraint:** `run_gates.sh` discovers every `*.py` under `tools/` and **fails the suite** if one does not advertise `--selftest`.
- **D-06:** **Rows append per position, not at teardown — `PROCEDURE.md` Amendment 3.** The append moves into `P-07`/`P-09`, and **`P-11` becomes a completeness assertion**.
- **D-07:** **A2 runs all four positions on both arms.** If W27C512 fails as 999.2 predicts, the chip is still swapped and W29C020 is still written, on **both** arms. If A2 unexpectedly *completes*, that is an observation against 999.2, not noise.
- **D-08:** **A stalled write is killed at a ceiling derived from a measured healthy figure, and the kill is logged.** W27C512 ceiling = 4× 41.010 s ≈ **165 s**; W29C020 ceiling = 4× A1's control-arm W29C020 wall-clock, fallback absolute **600 s** recorded as a fallback. Numbered log, full stdout/stderr, last progress frame captured, recorded as `timed out at N s against a measured baseline of M s`.
- **D-09:** **A one-time, non-destructive smoke check before A1's control-arm W29C020 write.** Chip-id read plus a blank check, **on A1's control arm only**, **outside the `P-01`…`P-11` step list**, recorded as a bring-up datum in A1's cell dir. **The blank check is the standalone command. `-b` / `--no-blank-check` is forbidden and must not appear.** A not-blank result is a valid outcome.
- **D-10:** **Prove the v1.33-arm read-back on uno328pb before the sweep starts.** Bare uno328pb, no shield, no chip; flash v1.33; run `judge_readback.py`; **observe the match**. Recorded as a bring-up position in its own cell dir, not as one of the 12.
- **D-11:** **A3/B2's leave-state is: Leonardo, Rev 2.0, v1.33 arm, `W27C512` seated, VPP 12.0 V.** *(User's choice.)* `P-11` adds one operator swap back to the 28-pin part.
- **D-12:** **The leave-state requirement goes into `PROCEDURE.md` cell-agnostically; the value goes in the plan.** `P-11` gains a general *"declare and record the leave-state (board, port, arm, chip seated, pot, shield)"* requirement, folded into **Amendment 3**.

**Also locked and not re-openable** (161-CONTEXT.md:31-37): the `P-01`…`P-11` step list; arm order (control first); one pot setting per cell; the oracle (full-device SHA against the written image, never an exit code; N=3 on v1.33 always, control escalating only where v1.33's three reads disagreed); the 12 pre-computed images in `bench/IMAGE-PLAN.json`; the `EVIDENCE.jsonl` `_schema` row; the two-state cell outcome taxonomy; the forbidden-invocation table; the write-duration definition.

### Claude's Discretion

Verbatim from `161-CONTEXT.md:236-262`:

> The user answered **"you decide"** on five questions; D-06, D-07, D-08, D-09 and D-10's *rejected alternatives* record what was weighed. The planner may revisit these on evidence, but not on preference:
>
> - **D-07 (A2 runs all 4)** — if A2's W27C512 failure turns out to physically damage or endanger the W29C020 … stop and report; safety outranks coverage. Nothing currently on the record suggests this.
> - **D-08 (ceilings)** — the 4× multiple is a judgment call, not a measurement. If A1's healthy figures show high variance, widen it and **state the widening**, do not silently exceed it.
> - **D-09 (smoke check)** — the exact commands are left to research/planning; the locked property is that it is **non-destructive, once, on A1 control, outside the step list**.
> - **D-10 (pre-proof)** — if the bare 328PB cannot be flashed without the shield … the locked property is that it happens **before A1**, not what it is mounted on.
>
> Still open and left to research/planning:
>
> - The concrete `append_evidence.py` interface (arguments, where the human fields enter, how it refuses an incomplete position) — D-05 locks the property, not the CLI.
> - W29C020's read-set duration budget. … the planner should measure rather than extrapolate, and A1 is where that measurement first exists.
> - Whether A1's opening sequence needs anything beyond the obvious. …

**All three "still open" items are answered below** — §W29C020 Read Budget, §`append_evidence.py` Interface, §A1's Opening Sequence. The third answer **corrects** CONTEXT's own provisional guess; see Pitfall 1.

### Deferred Ideas (OUT OF SCOPE)

Verbatim from `161-CONTEXT.md:436-457`:

> - **Fixing anything this phase finds.** Regressions are classified and fixed in **Phase 165**, on the **v1.33 PR branch**, not here and not on v1.34's branch. Phase 161 records; it does not repair.
> - **The `~/.firestarter` stray directory** … **Do not attempt removal again.** Its only role here is as the per-cell teardown detector (D-12's config-dir check): if it *changes*, that is a `P-H1` finding.
> - **Sparse argv recording.** … Disclosed at Phase 160's gate; not re-litigated here.
> - **`BRINGUP-wrv`'s missing teardown `probe_board.py` re-run.** … that cell's gap is recorded, not backfilled.
> - **Program-window VPP/VCC under load** stays unmeasured … v1.34 makes **no electrical claim**.
> - **The `avrdude --detect-mcu` product deliverable.** … the host-side flag is not built here.
> - **Phase 164's Modified Rev 0 work** … both need the board Phase 163's cell B1 puts on the bench.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

Source: `.planning/REQUIREMENTS.md:43-46`.

| ID | Description | Research Support |
|----|-------------|------------------|
| **BOARD-01** | Cell A1 (Uno / Rev 2.0) completes both arms × both chips — W27C512 (DIP28, `0x07`, 64 KiB) and W29C020 (DIP32, `0x05`, 256 KiB page-write) — with every result recorded | §Per-Cell Constants (A1 column); §Position Ledger (4 A1 rows); §A1's Opening Sequence; §W29C020 First Silicon |
| **BOARD-02** | Cell A2 (uno328pb / Rev 2.0) completes both arms × both chips, with its expected program failure captured on **both** arms rather than assumed | §Cell A2 — the Expected-Failure Cell (measured 999.2 symptom); §D-08 Stall Ceilings and the Logged Kill; Pitfall 4 (`judged_match` ≠ SHA equality on uno328pb) |
| **BOARD-03** | Cell A3/B2 (Leonardo / Rev 2.0) completes both arms × both chips on the rig v1.31 used | §Per-Cell Constants (A3/B2 column); Pitfall 2 (`capture_provenance.py` has never run on a Leonardo and will hard-refuse without a touch); §D-11 Leave-State |
| **BOARD-04** | Each cell records measured write duration per arm, so a timing regression is visible against v1.31's W27C512 consistency of 0.37 s | §The Write-Duration Definition and the v1.31 0.37 s Non-Claim (incl. the *measured* 106 s → ~37 s shift that is NOT a v1.33 effect) |
</phase_requirements>

---

## Summary

Phase 161 runs a finished rig. Phase 160 shipped twelve tools behind one gate, a prescriptive
eleven-step procedure, a pre-computed 21-position image plan, and one fully-worked example
position (`BRINGUP-wrv`). This phase adds exactly **one** tool (`append_evidence.py`, D-05) and
**one** procedure amendment (Amendment 3, D-06/D-12) and then executes 12 positions across three
cells. `bash .planning/v1.34/tools/run_gates.sh` was measured green in this session — **11/11 tool
selftests, 5/5 live gates, exit 0** [VERIFIED: run in this session] — so the substrate the planner
is building on is sound today.

The research therefore concentrated on **the seams where a plan can go wrong**, because Phase 160's
own gate document records that "roughly twenty latent rig-tooling defects were found across waves
5-9, and **every one of them had a passing fixture-based `--selftest` and failed on first contact
with real hardware**" [CITED: `.planning/v1.34/PHASE-160-GATE.md`, §6 final bullet], and that an
arm-agnostic-constant plan-authoring defect recurred **4×**. Six such seams were found, all of them
new (none is on §6's disclosed carry-forward list) and all of them fatal to results rather than
merely inconvenient:

1. **`$CELL_DIR/reads/` is reused by all four positions of a cell** and `judge_wrv.py` *globs*
   `run_*.bin`. Position 2 will judge position 1's files. This produces a false `disagreement` or
   `mismatch` on up to 9 of 12 positions.
2. **`capture_provenance.py` has only ever run on the Uno** and internally shells to
   `probe_board.py` with no 1200-baud touch — measured to fail on a Leonardo running application
   firmware. A3/B2's `P-02` will hard-refuse as written.
3. **`P-11`'s teardown assertion (1) — "assert `~/.firestarter` still does not exist" — is already
   unconditionally RED** on this container and would produce twelve `P-H1` false halts.
4. **On `uno328pb`, `sha_actual_judged != sha_expected_judged` on a *correct* flash** (8 vector bytes
   excluded). Only `judged_match` is the verdict.
5. **`gate_record.py`'s `check_cross_oracle()` reads three keys that do not exist in the v1.34
   `EVIDENCE.jsonl` schema** — the leg is structurally inert against every row this phase writes.
   `append_evidence.py` is the only place left to close it.
6. **A1's opening sequence is *not* `P-03`→`P-04` run normally.** The chip must come out *before*
   `P-02`, because `P-02`'s `probe_board.py` is an avrdude signature probe and `STATE.md`'s SAFETY
   line forbids exactly that with a chip seated on a Uno-class board.

**Primary recommendation:** author **Amendment 3 with four clauses, not two** — D-06's evidence
append, D-12's leave-state declaration, per-position `reads`/`written`/`WRV` paths (seam 1), and a
restatement of `P-11` assertion (1) as *unchanged-since-baseline* rather than *absent* (seam 3) —
then land three plans, one per cell, whose `<automated>` verify legs read every arm- and
target-dependent constant out of `rig-pins.json` at runtime instead of embedding it.

---

## Architectural Responsibility Map

There is no application under construction here; the "tiers" are the rig's own layers.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Physical rig state (mount, chip in/out, pot) | **Operator** | — | Standing bench rules 3 and 4 (`PROCEDURE.md:47-51`); Claude never touches the rig |
| Board/MCU identity | **avrdude signature probe** (`probe_board.py`) | operator silkscreen for the *shield* | Standing bench rule 6; `hw_revision` cannot discriminate the three shields |
| Firmware flashing | **PlatformIO** (`pio run -t upload -e $TARGET`) | — | Supplies the per-target flags the procedure does not reproduce (`-x nometadata`, the 1200-baud touch) |
| Flash-arm proof | **`judge_readback.py`** (independent avrdude read) | — | Never the uploader's own verify pass (D-01) |
| Chip write | **arm binary under test** (`$ARM_BIN … write`) | — | The thing being A/B'd |
| Chip read set | **arm binary under test** (`dev consistency-check` / `read`) | — | Produces artifacts only; it is not the judge |
| Write→read→verify verdict | **`judge_wrv.py`** (independent SHA over the full device) | app's own 0/1/2, recorded unjudged | Pitfall 6: `Consistency check: PASS` compares reads to *each other*, never to the written image |
| Provenance capture | **`capture_provenance.py`** | operator (`--shield-rev` only) | RIG-05 discharged by mechanism, not transcriber discipline |
| Evidence row assembly | **`append_evidence.py`** (Phase 161 builds this) | human (`verdict`, `anomalies` prose only) | D-05 — the same argument, one layer out |
| Evidence row persistence | **`render_evidence.py --append`** then a plain re-render | — | Append-only integrity + `--check` gate stay coupled |
| Record-shape gate | **`gate_record.py`** via `run_gates.sh` | — | Shape and domain; **not** correctness (see Pitfall 5) |

---

## Standard Stack

**No packages are installed by this phase.** Both sub-repos stay byte-unchanged; the rig imports
stdlib only, with `pyserial` the single permitted exception in `touch_1200.py`
[VERIFIED: `rig-pins.json:175` `tool_conventions.import_policy`].

| Component | Version | Purpose | Source of truth |
|---|---|---|---|
| Python (rig tools) | 3.12.14 | every `tools/*.py`, run as system `python3` | `rig-pins.json:69` |
| avrdude (rig's own direct invocations) | **8.1**, `/home/vscode/.platformio/packages/tool-avrdude/avrdude` | `probe_board.py`, `judge_readback.py` | `rig-pins.json:38-44` |
| avrdude (PlatformIO upload path, per env) | uno **6.3**, uno328pb **8.1**, leonardo **6.3** | `pio run -t upload` resolves these itself | 161-CONTEXT.md:386-391 — and 6.3 in a uno/leonardo log is **not** a `forbidden_binaries` violation |
| avr-objcopy | GNU binutils 2.26.20160125, pinned (not on PATH) | hex→bin normalisation inside `judge_readback.py` | `rig-pins.json:58-60` |
| PlatformIO Core | 6.1.19 | the only sanctioned flash path | `rig-pins.json:71` |
| git | `/usr/local/bin/git`, pinned | `P-04`'s firmware checkout; allowed as an argv0 by `gate_record.py` | `rig-pins.json:61-62` |
| control arm binary | `/workspaces/.v1.34-arms/control/.venv/bin/firestarter` | fw `8695ee5…`, app `6bfa645…` | `rig-pins.json:10-16` |
| v133 arm binary | `/workspaces/.v1.34-arms/v133/.venv/bin/firestarter` | fw `5759dc8…`, app `cb189a9…` | `rig-pins.json:17-23` |

### Package Legitimacy Audit

**Not applicable.** This phase installs zero external packages in either ecosystem. No
`npm install`, no `pip install`, no `cargo add`. The one tool it authors (`append_evidence.py`)
is stdlib-only by rig convention. There is therefore no slopsquatting surface, and the
`package-legitimacy check` seam was not invoked.

**Packages removed due to [SLOP] verdict:** none.
**Packages flagged as suspicious [SUS]:** none.

---

## Per-Cell Constants — the single highest-value table in this document

Phase 160 recorded a plan-authoring defect that **recurred 4×**: arm-agnostic constants hardcoded
into `<automated>` verify legs (plans 08/09/10/12), each caught only in flight
[CITED: `PHASE-160-GATE.md` §6]. Across 12 positions one wrong constant is twelve false results.
**Every value below is arm- or target-dependent. A verify leg should read it out of
`rig-pins.json` at runtime, not embed it.**

All values [VERIFIED: `.planning/v1.34/rig-pins.json`].

| Constant | **A1** | **A2** | **A3/B2** |
|---|---|---|---|
| `cell_id` (as passed to tools) | `A1` | `A2` | `A3/B2` |
| `cell_slug` (dir name, `cell_id.replace("/","-")`) | `A1` | `A2` | **`A3-B2`** |
| `$TARGET` (PlatformIO env) | `uno` | `uno328pb` | `leonardo` |
| MCU | `atmega328p` | `atmega328pb` | `atmega32u4` |
| **signature to re-probe** | `0x1e950f` | `0x1e9516` | `0x1e9587` |
| avrdude programmer | `arduino` | `urclock` | `avr109` |
| avrdude baud | 115200 | 115200 | **57600** |
| node class | `/dev/ttyACM*` | **`/dev/ttyUSB*`** (CH340 `1a86:7523`) | `/dev/ttyACM*` |
| `judged_span_policy` | `hex-extent` | **`vector-exclusion`** | `hex-extent` |
| `vector_exclusions` | `[]` | `[{off 0,len 4},{off 100,len 4}]` | `[]` |
| `hex_span_expected_by_arm.control` | **26026** | **26074** | **28170** |
| `hex_span_expected_by_arm.v133` | **22952** | **23000** | **25098** |
| legacy scalar `hex_span_expected` | 22952 | 23000 | 25098 | ← **never use; equals the v133 value and silently rejects a correct control flash** |
| `chip_out_before_sideload` | `true` | `true` | **`false`** (exempt) |
| `needs_1200_touch` | `false` | `false` | **`true`** |
| bootloader | optiboot 512 B | urboot 384 B | Caterina 4096 B |
| control `.hex` | `images/firestarter_uno.control.hex` | `images/firestarter_uno328pb.control.hex` | `images/firestarter_leonardo.control.hex` |
| v133 `.hex` | `images/firestarter_uno.v133.hex` | `images/firestarter_uno328pb.v133.hex` | `images/firestarter_leonardo.v133.hex` |
| PIO-resolved avrdude in the upload log | 6.3 | 8.1 | 6.3 |
| **`sha_actual_judged == sha_expected_judged` on a correct flash?** | yes | **NO** — see Pitfall 4 | yes |

Chip constants, identical for all three cells [VERIFIED: `rig-pins.json:142-158`]:

| | `w27c512` | `w29c020` |
|---|---|---|
| `size_bytes` / `--expect-size` | 65536 | 262144 |
| package / pins | DIP28 / 28 | DIP32 / 32 |
| `vpp_mv` | 12000 | 12000 — **same, hence one pot set per cell (`P-06`)** |
| `algorithm` | 7 (`0x07`) | 5 (`0x05`) |
| `stamp_width` (`gen_addr_image.py --stamp-width`) | **16** | **32** |
| chip ID in the DB | `0xDA08` (W27C512) | **`0xDA45`** [VERIFIED: `firestarter search w29c020`, run this session] |

`forbidden_flags` — rejected by exact token match anywhere in a recorded argv
[VERIFIED: `rig-pins.json:160`]: `--force`, `-f`, `-b`, `--no-blank-check`, `--skip-erase`.
`forbidden_argv0`: any first token that is not one of the two absolute `venv_bin` paths; the bare
token `firestarter` on `PATH` is a **third, un-named arm** and is never invoked.

---

## The 12 Positions — IMAGE-PLAN.json Ledger

All 12 rows [VERIFIED: `.planning/v1.34/bench/IMAGE-PLAN.json`, read this session]. `mask` is stored
as a decimal int; `gen_addr_image.py` accepts hex or dec.

| # | `position_id` | cell_slug | arm | chip | size | mask (dec / hex) | stamp | `sha256` (written image) | `ff_count` |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `A1__control__w27c512` | A1 | control | w27c512 | 65536 | 16 / `0x10` | 16 | `8ee568689ae9ab14ac5e34179542fecbe44373c7ef8b4400a1b6f3e3f0d563a4` | 128 |
| 2 | `A1__control__w29c020` | A1 | control | w29c020 | 262144 | 17 / `0x11` | 32 | `46e0fe13b11c46d3a86039c6812ddf6a809746ab33c945104e6753d0eb877dfb` | 256 |
| 3 | `A1__v133__w27c512` | A1 | v133 | w27c512 | 65536 | 18 / `0x12` | 16 | `49476bbd2250ddb0b8d7ad5a44672151b5c7cf1571d4df9906722792ed9e123f` | 128 |
| 4 | `A1__v133__w29c020` | A1 | v133 | w29c020 | 262144 | 19 / `0x13` | 32 | `cc638893cf2760f79d5175e7ef4d93a00f5e75f803d7b0cc7e88b957ea88c452` | 1280 |
| 5 | `A2__control__w27c512` | A2 | control | w27c512 | 65536 | 20 / `0x14` | 16 | `09522e05dadfb8ff99f1f26e94b07da5cfa3e89da2d7044f3fee9c43904c0673` | 128 |
| 6 | `A2__control__w29c020` | A2 | control | w29c020 | 262144 | 21 / `0x15` | 32 | `39ffcb4cf82599429f7a09643571283977ccc423b35c86e5877c8705bdf85edd` | 256 |
| 7 | `A2__v133__w27c512` | A2 | v133 | w27c512 | 65536 | 22 / `0x16` | 16 | `36b87c396aad25f27599290344360e8b501457ac8d5432de29411705257f558a` | 128 |
| 8 | `A2__v133__w29c020` | A2 | v133 | w29c020 | 262144 | 23 / `0x17` | 32 | `ef6a3c384a6e4722b3bdd4184dda3046f7025667872da2571b00116b1694e14c` | 1280 |
| 9 | `A3-B2__control__w27c512` | A3-B2 | control | w27c512 | 65536 | 24 / `0x18` | 16 | `a094e902a30b4fa3369ee493338351e11a8b6667f7539460b63f78dce896ae43` | 128 |
| 10 | `A3-B2__control__w29c020` | A3-B2 | control | w29c020 | 262144 | 25 / `0x19` | 32 | `01bab1275e83430c4a33e77c04c369e086dc57857ed003d35a207023a1b60dd0` | 256 |
| 11 | `A3-B2__v133__w27c512` | A3-B2 | v133 | w27c512 | 65536 | 26 / `0x1a` | 16 | `558decd0795b5d534aece2d94be4c52d62d42aa67a03f72a37f984d0eeadb807` | 128 |
| 12 | `A3-B2__v133__w29c020` | A3-B2 | v133 | w29c020 | 262144 | 27 / `0x1b` | 32 | `5da571d8407b97c754858bb63524b4adc80c8078d90d8a39f478cb248edfbfb8` | 1280 |

**Note the `position_id` uses `cell_slug`, not `cell_id`** — `A3-B2__control__w27c512`, never
`A3/B2__…`. `capture_provenance.py` takes `--cell-id A3/B2` and derives the slug itself
[VERIFIED: `capture_provenance.py:534`].

`capture_provenance.py` looks this row up by `--position-id` and populates `image_mask` /
`image_stamp_width` / `image_sha` **itself** — those three are never supplied by hand
[VERIFIED: `capture_provenance.py:43-57`].

### `artifact_volume_policy` (`IMAGE-PLAN.json` top level)

- **Committed:** the six `.hex` files + `SHA256SUMS.txt`, `IMAGE-PLAN.json`, every
  `flash_readback.bin` (32768 B each, *not reproducible from any record*), every `provenance*.json`,
  `EVIDENCE.jsonl`, `EVIDENCE.md`, the text logs.
- **Not committed by default:** the 21 generated `written.bin` images (reproducible from
  `gen_addr_image.py` + this file) and the chip read-back `run_*.bin` files.
- **COMMIT-ON-FAILURE EXCEPTION:** for any position whose judged verdict is **not** a clean match —
  a SHA mismatch, an N=3 disagreement, or a verdict disagreement — that position's `run_*.bin`
  **and** its `written.bin` **are** committed, via **`git add -f`**, because Phase 165's RCA needs
  the actual bytes.

`bench/.gitignore` implements this as exactly two patterns
[VERIFIED: `.planning/v1.34/bench/.gitignore:8-9`]:

```
cells/*/reads/
cells/*/written.bin
```

**Consequence the planner must handle** (measured with `git check-ignore -v` in this session): if
per-position paths are introduced (Pitfall 3 requires them), `cells/<slug>/reads/<position_id>/…`
stays ignored by the directory rule, but a renamed image such as `cells/<slug>/written_<pos>.bin`
would **not** be ignored and would silently commit up to 12 large binaries. Keep the leaf filename
`written.bin` inside a per-position directory, or extend `.gitignore` in the same change.

---

## PROCEDURE.md — the step list, distilled

`.planning/v1.34/PROCEDURE.md`, 529 lines, executed **unchanged** except Amendment 3.
`render_steps.py` renders exactly **11 steps** per arm and the control-vs-v133 diff is **empty**
[VERIFIED: run this session — `live gate PASS: render_steps.py -- diff empty, control=11 v133=11 lines`].
**Cite step ids; do not re-describe runs.**

| Step | Title | Performer | Operator-physical? (D-02 checkpoint allowed) |
|---|---|---|---|
| `P-01` | Mount and declare (shield revision from silkscreen) | operator | **YES** |
| `P-02` | Re-verify port identity (`probe_board.py` + `$ARM_BIN hw`) | Claude | no |
| `P-03` | Uno-class chip-out (covers flash **and** its read-back) | operator | **YES** |
| `P-04` | Flash this arm, prove it by independent read-back | Claude | no |
| `P-05` | Uno-class: seat the 28-pin chip | operator | **YES** |
| `P-06` | Set the pot **once per cell**, one confirming `vpp` read | operator + Claude | **YES** |
| `P-07` | Chip 1 write → read → judge (65536 B) | Claude | no |
| `P-08` | Swap to the 32-pin chip, **no pot re-adjustment** | operator | **YES** |
| `P-09` | Chip 2 write → read → judge (262144 B) | Claude | no |
| `P-10` | Arm switch — return to `P-03` for v1.33 | Claude + operator | inherits `P-03`/`P-05`/`P-08` |
| `P-11` | Teardown: re-probe, config-dir check, evidence | Claude (+ operator, see below) | see Pitfall 1 / D-11 |

`human-verify` checkpoints belong at `P-01`, `P-03`, `P-05`, `P-06`, `P-08` **and nowhere else**
(D-02). Two `P-11` operator actions are nonetheless *required by the decisions themselves* and are
not "artificial park prompts": D-11's swap back to W27C512 on A3/B2, and the Uno-class chip-out
before `P-11`'s teardown probe on A1/A2 (Pitfall 1).

### The 9 standing bench rules (`PROCEDURE.md:31-77`)

1. Port identity re-verified **every cell**, never inherited — `ttyACM*` **and** `ttyUSB*`.
2. Chip-out-before-sideload is **Uno-class only**; a read is the same electrical situation as a
   write. **Leonardo exempt.**
3. Photography, multimeter, chip handling, pot adjustment are **operator-only**.
4. The operator adjusts the pot; Claude takes **exactly one** confirming read, never a loop.
5. VPP/VPE monitors do not route to the socket — a blank reading is a **contact fault**.
6. Board identity by silkscreen + avrdude signature, **never** a firmware-reported revision.
7. **Never under `--auto` / `--chain` / any auto-advance mode.** `autonomous: false` is not
   self-protecting.
8. **One clean re-seat per position**; both the discarded attempt and the re-run are recorded.
9. `FIRESTARTER_CONFIG_DIR` set **inline** on every arm-invoking command, never exported.

### Halt policy

- **`P-H1` — rig failure → halt and fix in-phase.** Named examples: *a read-back mismatch on a
  board that was correctly flashed*, a judge crashing, a provenance field missing, a gate that
  cannot read its own input.
- **`P-H2` — cell failure → record `skipped-with-reason` and carry to Phase 165; the sweep
  continues.** Named examples: a write that fails, three reads that disagree, a chip that reds.
- Phase 145 D-13's halt-on-any-failure policy is **deliberately not inherited**.

### Outcome taxonomy

**Cell outcome: exactly two states — `validated` / `skipped-with-reason`. No third state, ever.**
`gate_record.py` enforces the domain from the file's own `_schema`. The three-state
`v1.33-caused` / `pre-existing` / `inconclusive` axis is **Phase 165's triage classification of a
failure**, never a cell result.

### Amendments 1 and 2 — the established shape

Both amendments are a dated paragraph at the bottom of `PROCEDURE.md` with exactly three labelled
clauses [VERIFIED: `PROCEDURE.md:499-529`]:

> **Amendment N — <date>, Phase <phase> Plan <NN>:** **(a)** what changed …  **(b)** Why: …
> **(c)** Which cells ran under which text: … No real sweep cell (`A1`/`A2`/`A3-B2`/`B1`/`B3`) has
> run yet under either text. … the arm-agnostic empty-diff render gate (`render_steps.py --arm
> control` vs `--arm v133`) was re-confirmed empty after this edit — the new command block carries
> no arm-dependent token.

Amendment 2 additionally states *why* the empty-diff gate stays empty (the added command block
takes no `$ARM_BIN`). **Amendment 3 must say the same thing and must be re-confirmed the same
way**, by re-running the gate — which `run_gates.sh` does as its third live leg, so a full
`run_gates.sh` after the edit is the confirmation.

---

## Amendment 3 — what it must contain

D-06 and D-12 name two clauses. Research found **two more that belong in the same edit**, for the
same reason D-06 gives: the window is free (no real sweep cell has run), and a silent mid-sweep
drift is exactly what the amendment mechanism exists to prevent.

**Clause (a) — what changed, four items:**

1. **(D-06)** The `EVIDENCE.jsonl` append moves from `P-11` into `P-07` and `P-09` — one row per
   position, written as that position completes. **`P-11` becomes a completeness assertion**: "all
   four of this cell's rows are present in `bench/EVIDENCE.jsonl`."
2. **(D-12)** `P-11` gains a general, **cell-agnostic** requirement: *declare and record the
   leave-state — board, port, arm, chip seated, pot, shield.* The value is supplied by the phase's
   plan, never by conditional text in the procedure.
3. **(NEW — Pitfall 3)** `P-07`/`P-09`'s `--output-dir`, `--reads`, `written.bin` and
   `wrv_verdict.json` paths become **per-position**, keyed on `$POSITION_ID` (already a declared,
   arm-independent substitution token, `PROCEDURE.md:112`). Reason: `judge_wrv.py` globs `run_*.bin`
   in `--reads` and counts what it finds; four positions sharing one directory cross-contaminate.
4. **(NEW — Pitfall 5)** `P-11` teardown assertion (1) is restated from *"assert `~/.firestarter`
   still does not exist"* to *"assert `~/.firestarter` is **unchanged from the recorded
   baseline**"*, with the baseline pinned. Reason: the directory already exists (a Phase 160
   disclosed carry-forward), so the assertion as literally written is unconditionally RED and would
   book twelve false `P-H1` halts.

**Clause (b) — why:** for each of the four, the measured trigger. D-06: a kill after position 3
loses all four rows' assembly and `EVIDENCE.jsonl` silently lags the bench. D-12: cell-conditional
text is the same shape as the arm-conditional text the procedure forbids. (3): measured — see
Pitfall 3. (4): measured — `~/.firestarter` exists, birth/mtime `2026-08-27T07:59:25Z`.

**Clause (c) — which cells ran under which text:** *"Every bring-up cell (`BRINGUP-uno`,
`BRINGUP-uno328pb`, `BRINGUP-leonardo`, `BRINGUP-wrv`) ran under the pre-Amendment-3 text. **No real
sweep cell (`A1`/`A2`/`A3-B2`/`B1`/`B3`) has run under either text** — Amendment 3 lands before the
first sweep cell, so every sweep cell in this milestone runs under the new text."*

**Empty-diff re-confirmation:** none of the four clauses adds an `[arm: …]` marker or an `$ARM_BIN`
token — `$POSITION_ID` is explicitly listed among the non-arm-dependent tokens
(`PROCEDURE.md:106-118`), and the `~/.firestarter` restatement is prose in `P-11`'s body. The gate
should stay empty. Re-confirm with `bash .planning/v1.34/tools/run_gates.sh` (third live leg) —
**exit code measured directly, never through a pipe** (D-04).

**Baseline values to pin into clause (4)** [all VERIFIED by `stat`/`sha256sum` in this session]:

| Property | Value |
|---|---|
| path | `/home/vscode/.firestarter` |
| contents | exactly one file, `config.json`, 30 bytes |
| `config.json` body | `{\n    "port": "/dev/ttyACM0"\n}` |
| `config.json` sha256 | `b323867c1f01b22a705dd9caf003ab7302a249fe46772f5b02e44aaa2760dd79` |
| tree sha (sorted relpath + content) | `423546cd37b5b45d9654e5acd07bd7e2a3c9e1df77e4d5feb79951bf37329951` |
| mtime | `1787817565` = `2026-08-27 07:59:25 UTC` |

A **change** to any of those at a cell teardown is the `P-H1` finding (161-CONTEXT.md:441-444). Do
not attempt deletion — the sandbox denies it and Phase 160 already disclosed that.

Assertion (2) — the frozen `FIRESTARTER_CONFIG_DIR` SHA — is unaffected and stays as written. Its
expected value is `77adfdd26ed8710c4a70882e6dc9ee7bb494286fe225000d581f9e730dd77ad0`
[VERIFIED: `arms-provenance.json` `config_dir_sha`], checked via
`check_arms.py --expect-config-sha <sha>`.

---

## `append_evidence.py` — proposed interface (D-05)

### House conventions this tool must match

All [VERIFIED] by reading the eleven existing tools.

| Convention | Rule | Evidence |
|---|---|---|
| Entry point | `sys.exit(main())` at module bottom; `main() -> int` | `rig-pins.json:172`; e.g. `judge_wrv.py:344`, `render_evidence.py:579` |
| Argparse | `argparse.ArgumentParser(description=__doc__)`, long `--flags` only, no positionals (except `gen_addr_image.py`, the documented exception) | `judge_wrv.py:157-169` |
| `--selftest` | `ap.add_argument("--selftest", action="store_true")`, dispatched first in `main()`, delegating to `_run_selftest() -> int` | every tool |
| Selftest content | on-disk fixtures in a `tempfile` dir, **positive legs plus named negative legs**, accumulate-then-report (never bail on the first failure) | `render_evidence.py:397+`, `gate_record.py` |
| Failure style | print `FAIL: <named reason>` to **stderr**, return non-zero. Never write an empty artifact and exit 0 | `render_evidence.py` "FAIL CLOSED" docstring |
| Exit codes | `0` ok · `1` a real failure · `2` bad usage / missing required argument | `judge_wrv.py:189` (`return 2` on missing args) |
| Imports | stdlib only | `rig-pins.json:175` |
| Sibling reuse | `importlib.util.spec_from_file_location(name, _HERE / "sibling.py")` — never re-derive a sibling's algorithm | `capture_provenance.py:361-365`, `gate_record.py:83-87` |
| Path defaults | `_HERE = Path(__file__).resolve().parent`; `_DEFAULT_PINS = _HERE.parent / "rig-pins.json"` | `judge_wrv.py:64-65` |
| Docstring | opens with the D-16 boundary paragraph ("meta-repo BENCH TOOLING, not host source … must NEVER be copied into `firestarter/` or `firestarter_app/`") | every tool |

**The `--selftest` discovery contract, quoted exactly** [VERIFIED: `tools/run_gates.sh:99-129`]:

```bash
PY_TOOLS=()
while IFS= read -r -d '' f; do
    PY_TOOLS+=("$f")
done < <(find "$TOOLS_DIR" -maxdepth 1 -name '*.py' -print0 | sort -z)
...
for tool in "${PY_TOOLS[@]}"; do
    name="$(basename "$tool")"
    if ! grep -q -- '"--selftest"' "$tool"; then
        echo "FAIL: $name does not advertise a --selftest mode" >&2
        FAILURES+=("$name: does not advertise a --selftest mode")
        continue
    fi
    ...
    if python3 "$tool" --selftest; then ...
```

Two literal consequences: the source must contain the token **`"--selftest"` with double quotes**
(a single-quoted `'--selftest'` would fail the grep even with a working flag), and
`python3 <tool> --selftest` must exit 0 **with no arguments and no device**. Discovery is
`-maxdepth 1`, so `tools/__pycache__/` is not scanned.

### Proposed argument surface

```
append_evidence.py
  --position-id     A1__control__w27c512        (required)
  --cell-dir        <path>                      (default: bench/cells/<slug from position-id>)
  --provenance      <path>                      (default: <cell-dir>/provenance_<position-id>.json)
  --wrv             <path>                      (default: <cell-dir>/positions/<position-id>/WRV-VERDICT.json)
  --readback        <path>                      (default: <cell-dir>/READBACK-VERDICT.json)
  --image-plan      <path>                      (default: bench/IMAGE-PLAN.json)
  --pins            <path>                      (default: rig-pins.json)
  --jsonl           <path>                      (default: bench/EVIDENCE.jsonl)

  # the ONLY human inputs (D-05)
  --verdict-file    <path|->                    (required) prose for the `verdict` column
  --anomalies-file  <path|->                    (required) prose for the `anomalies` column
  --blank-state     <string>                    (required) must be a real reading or the
                                                "not measured — <reason>" shape
  --shield-note     <string>                    (optional) appended to the derived `shield` column

  # measured at the bench, not present in any of the three source artifacts
  --write-wallclock-s  FLOAT | "not measured — <reason>"   (required)
  --write-app-reported-s FLOAT | "not measured — <reason>" (required)

  --commands-extra  <path>                      (optional) JSON list merged after provenance.commands
  --dry-run                                     print the assembled row, write nothing
  --selftest
```

`--verdict-file` / `--anomalies-file` take a **file or `-`** rather than an inline string because
both are multi-paragraph prose in practice (`BRINGUP-wrv`'s `verdict` is ~1.4 kB and its
`anomalies` ~2.9 kB) and shell-quoting that inline is its own defect class.

### Field derivation map — all 40 columns

`_schema.record_keys` = `locked_columns` (9) + `evid_extension_columns` (31) = **40**
[VERIFIED: `bench/EVIDENCE.jsonl` line 1]. Sources: **P** = `provenance_<pos>.json`,
**W** = `WRV-VERDICT.json`, **R** = `READBACK-VERDICT.json`, **I** = `IMAGE-PLAN.json`,
**K** = `rig-pins.json`, **T** = a constant table inside the tool, **H** = human via CLI,
**M** = measured at the bench via CLI.

| # | Column | Src | Derivation |
|---|---|---|---|
| 1 | `chip` | P | `provenance.chip` |
| 2 | `family` | K+T | `"0x%02x (%s)" % (pins.chips[chip].algorithm, LABEL[chip])`; `LABEL` is a 2-entry tool constant (`EPROM_STD` / `FLASH_5V_PAGE`) |
| 3 | `board` | P+K+T | `BOARD_LABEL[target_env]` + `" (%s)" % pins.targets[env].mcu.upper()` |
| 4 | `shield` | P+H | `"mounted, %s, %s seated" % (shield_rev_declared, chip.upper())` + optional `--shield-note` |
| 5 | `blank_state` | **H** | `--blank-state`; validated against `gate_record.py`'s `_NOT_MEASURED_RE` if it is not a real reading |
| 6 | `op` | T+W | template keyed on `expect_size` and `read_count` |
| 7 | `sha256` | W | `wrv.written_sha`; **refuse if `!= provenance.image_sha` or `!= image_plan[pos].sha256`** |
| 8 | `verdict` | **H** | `--verdict-file` |
| 9 | `anomalies` | **H** | `--anomalies-file` |
| 10 | `position_id` | P | `provenance.position_id`; refuse if `!= wrv.position_id` or `!= --position-id` |
| 11 | `cell_id` | P | `provenance.cell_id` |
| 12 | `cell_slug` | P | `provenance.cell_slug` |
| 13 | `arm` | P | `provenance.arm`; refuse if `!= readback.flashed_arm` |
| 14 | `target_env` | P | `provenance.target_env`; refuse if `!= readback.target` |
| 15 | `board_signature` | P | `provenance.board_signature`; cross-check against `pins.targets[env].mcu`'s known signature |
| 16 | `controller_string` | P | `provenance.controller_string` |
| 17 | `shield_rev_declared` | P | `provenance.shield_rev_declared` |
| 18 | `fw_sha` | P | `provenance.fw_sha`; refuse if `!= pins.arms[arm].fw_sha` |
| 19 | `fw_readback_sha_judged` | P/R | `provenance.fw_readback_sha_judged`; refuse if `!= readback.sha_actual_judged` |
| 20 | `fw_readback_sha_whole_flash` | P/R | `provenance…`; refuse if `!= readback.sha_whole_flash_unjudged` |
| 21 | `fw_readback_judged_span_bytes` | **R** | `readback.judged_span_bytes` — **not in `capture_provenance.py`'s `RECORD_KEYS`; this is why D-05 names three sources** |
| 22 | `host_arm_sha` | P | `provenance.host_arm_sha`; refuse if `!= pins.arms[arm].app_sha` |
| 23 | `host_arm_porcelain_clean` | P | `provenance…` |
| 24 | `host_arm_file` | P | `provenance…` |
| 25 | `config_dir_sha` | P | `provenance…` |
| 26 | `interpreter` | P | `provenance…` |
| 27 | `dep_freeze_sha` | P | `provenance…` |
| 28 | `eeprom_calibration` | P | `provenance…` (nested object, copied whole) |
| 29 | `image_mask` | P+I | `provenance.image_mask`; refuse if `!= image_plan[pos].mask` |
| 30 | `image_stamp_width` | P+I | same cross-check |
| 31 | `image_sha` | P+I | same cross-check, and against `wrv.written_sha` |
| 32 | `read_count` | W | `wrv.read_count` |
| 33 | `read_shas` | W | `wrv.read_shas` |
| 34 | `app_verdict_unjudged` | W | `wrv.app_verdict_unjudged` |
| 35 | `sha_verdict_judged` | W | `wrv.sha_verdict_judged` |
| 36 | `verdict_disagreement` | W | `wrv.verdict_disagreement` |
| 37 | `write_duration_wallclock_s` | **M** | `--write-wallclock-s` |
| 38 | `write_duration_app_reported_s` | **M** | `--write-app-reported-s` |
| 39 | `commands` | P(+H) | `provenance.commands` + `--commands-extra`; every entry re-validated against `gate_record.check_commands()` **before** the row is written |
| 40 | `outcome` | **W (derived)** | `"validated"` iff `wrv.sha_verdict_judged == "match" and not wrv.verdict_disagreement and not wrv.size_violations`; else `"skipped-with-reason"` |

**Human-supplied: exactly 5 of 40** (`blank_state`, `verdict`, `anomalies`, and the two write
durations), plus an optional `--shield-note`. Everything else is derived and cross-checked.

### Refusal behaviour for an incomplete position

Accumulate-then-report (the house idiom), then `return 1` with every gap named:

- any of the three source artifacts missing or unparseable;
- `--position-id` disagreeing with any of the three artifacts;
- any cross-check in the table above failing (a field transcribed from the wrong position's
  provenance — **the exact failure `gate_record.py` cannot see**, D-05's own argument);
- `blank_state` blank, or `"not measured"` with no reason (reuse `gate_record.py`'s
  `_NOT_MEASURED_RE`, `^not measured\s*(?:—|--)\s*\S.*$`, via the sibling-import idiom, **never**
  re-derived);
- `verdict` or `anomalies` empty;
- `outcome` derived as `skipped-with-reason` while `--verdict-file` does not name an observed
  symptom — the `P-H2` record contract;
- `position_id` already present in `EVIDENCE.jsonl` (`render_evidence.append_row_to_file` already
  refuses this; surface its message rather than duplicating the check).

### Writing the row — delegate, do not re-implement

`render_evidence.py` already owns the append-only write path and does all of: `record_keys`
presence/extra-key validation, outcome-domain validation, duplicate-`position_id` refusal, a
byte-unchanged-prefix re-read immediately before an **atomic** temp-file + `os.replace`
[VERIFIED: `render_evidence.py:234-306`]. `append_evidence.py` should assemble the dict and call
`append_row_to_file()` through the sibling-import idiom, or shell to
`render_evidence.py --append -`.

**`--append` does NOT re-render `EVIDENCE.md`** [VERIFIED: `render_evidence.py:355` — the `--append`
branch `return`s before the render path]. `run_gates.sh`'s fourth live leg is
`render_evidence.py --check`, which compares `EVIDENCE.md` byte-for-byte against a fresh render.
**Append and re-render are one atomic pair; skipping the re-render turns the per-cell gate red.**

```bash
# after every append, in the same step:
python3 /workspaces/.planning/v1.34/tools/render_evidence.py \
  --jsonl /workspaces/.planning/v1.34/bench/EVIDENCE.jsonl \
  --target /workspaces/.planning/v1.34/bench/EVIDENCE.md
```

---

## Rig Tool argv Contract

Read out of `--help` in this session [VERIFIED]. **Required** = the tool refuses without it.

| Tool | Required | Optional | Writes |
|---|---|---|---|
| `run_gates.sh` | — | `--quick` (skips `check_rebuild`+`check_arms` only) | nothing. Exit `0` pass · `1` a gate failed · `2` bad usage / zero tools discovered |
| `capture_provenance.py` | `--cell-id --position-id --arm{control,v133} --target{uno,uno328pb,leonardo} --port --chip{w27c512,w29c020} --shield-rev{Rev 2.0,Rev 2.2,Modified Rev 0}` | `--pins --image-plan --out --pending-readback --patch-readback --patch-image-plan --selftest` | `--out` (default `bench/cells/<slug>/provenance.json`). **Hard-refuses without the cell's `READBACK-VERDICT.json`** unless `--pending-readback`. **Internally shells out to `probe_board.py` and to `$ARM_BIN -v -p $PORT hw`** — see Pitfall 2 |
| `judge_readback.py` | `--target --port --flashed-arm --expect-arm --out-dir` (all flagged optional by argparse but the run needs them) | `--pins --manifest --readback --no-read --selftest` | into `--out-dir`: `READBACK-VERDICT.json`, `flash_readback.bin` (32768 B), `expected_span.bin`, `judged_span.bin`, `SHA256SUMS.txt`, `avrdude_read.stderr.log`. Refuses on a `PENDING-xshowvector` policy and on a `forbidden_binaries` avrdude |
| `judge_wrv.py` | `--written --reads --expect-size --app-verdict --position-id` (missing → exit **2**) | `--pins --out --selftest` | `--out` verdict JSON. **Exit 1 on any non-match, after writing the artifact.** `--reads` must be an existing directory |
| `probe_board.py` | `--port --target` | `--pins --show-urclock --out --selftest` | `--out` JSON. Route 1 (wrong `-p`, no `-U`), Route 2 (`-v`, correct `-p`) fallback. **Never issues `-U`; `-n` only.** No 1200-baud touch |
| `gen_addr_image.py` | positional `<size_bytes> <mask> <output_path>` | `--stamp-width{16,32}`, `--decode`, `--selftest` | the image. Retains `raise SystemExit(main(sys.argv))` (documented exception) |
| `gate_record.py` | one of `--cell <provenance.json>` / `--jsonl <EVIDENCE.jsonl>` | `--pins --selftest` | nothing. Accumulates every violation in one pass |
| `render_evidence.py` | — (defaults resolve to the milestone's own files) | `--jsonl --target --check --append --selftest` | `--target` (render mode) or `--jsonl` (append mode). **Never both** |
| `render_steps.py` | — | `--arm{control,v133} --procedure --selftest` | stdout, one `P-NN\t<text>` line per step |
| `check_arms.py` | — | `--pins --out --help-diff-out --expect-config-sha --selftest` | `--out`, `--help-diff-out`. Hard-fails on any probe failure |
| `check_rebuild.py` | — | `--images --expect --arms --envs --out --selftest` | `--out`. Fails closed on a missing/empty/short `--images` dir |
| `touch_1200.py` | `--port` | `--settle-s --wait-new-port --timeout-s --out --selftest` | `--out`. **Use the bare (settle-only) mode; `--wait-new-port` was empirically refuted on this Leonardo** |

**argv-recording trap** [VERIFIED: `gate_record.py:_is_rig_tool_invocation`]: a recorded rig-tool
command passes `check_commands` only when argv[0] is an **absolute** interpreter path **and** argv[1]
is an **absolute** script path containing `/.planning/v1.34/tools/`. `PROCEDURE.md`'s literal blocks
show *relative* paths (`python3 .planning/v1.34/tools/…`) for readability; the **recorded** argv must
be absolute, as `BRINGUP-wrv`'s row is. A relative script path in a `commands[]` entry fails the gate.

**avrdude `-b` exemption is narrow** [VERIFIED: `gate_record.py:check_commands`]: `-b` is on
`forbidden_flags` (the app's `--no-blank-check`) but is also avrdude's baud option, so the exemption
is scoped **only** to `pins.avrdude.binary` as argv0. A `-b` in any other recorded command is
rejected.

---

## The Position Directory Shape — `BRINGUP-wrv` as the worked example

`.planning/v1.34/bench/cells/BRINGUP-wrv/` is one complete position
[VERIFIED: directory listing this session]:

```
bench/cells/BRINGUP-wrv/
├── provenance.json            # capture_provenance.py --out   (29 fields + _schema + commands)
├── WRV-VERDICT.json           # judge_wrv.py --out
├── READBACK-VERDICT.json      # judge_readback.py --out-dir   ← CELL-level, one per flash event
├── flash_readback.bin  (32768 B)   ┐
├── expected_span.bin   (22952 B)   │ judge_readback.py --out-dir, same five artifacts
├── judged_span.bin     (22952 B)   │
├── SHA256SUMS.txt                  │
├── avrdude_read.stderr.log         ┘
├── probe.json / probe.json.stderr.log      # probe_board.py --out
├── check_arms_teardown.json                # check_arms.py --out at P-11
├── written.bin  (65536 B, gitignored)
├── reads/run_01.bin run_02.bin run_03.bin  (gitignored)
├── WRITE.md                   # the human narrative for this position
├── POT.md                     # P-06's record
└── logs/NN_<verb>.stdout.log + .stderr.log
```

**Log-numbering convention** [VERIFIED]: zero-padded two-digit, sequential from `00`, one
`.stdout.log`/`.stderr.log` pair per invocation, the suffix naming the verb. `BRINGUP-wrv`'s actual
sequence maps cleanly onto the step list and is the template for a sweep position:

| Log | Command | Step |
|---|---|---|
| `00_check_arms_pre_cell` | `check_arms.py` | pre-cell |
| `01_probe_board` | `probe_board.py --out` | `P-02` |
| `02_hw_probe_pre_flash` | `$ARM_BIN -p $PORT hw` | `P-02` |
| `03_capture_provenance_pending` | `capture_provenance.py --pending-readback` | `P-02` |
| `04_fw_checkout_v133` | `git -C /workspaces/firestarter checkout <sha>` | `P-04` |
| `05_pio_upload_v133` | `pio run -t upload -e uno` (cwd `/workspaces/firestarter`) | `P-04` |
| `06_judge_readback_v133` | `judge_readback.py` | `P-04` |
| `07_capture_provenance_patch` | `capture_provenance.py --patch-readback` | `P-04` |
| `08_vpp_confirming_read` | `$ARM_BIN -p $PORT vpp` | `P-06` |
| `09_gen_addr_image` | `gen_addr_image.py` | `P-07` |
| `10_write_w27c512` | `time $ARM_BIN … write` | `P-07` |
| `11_consistency_check` | `$ARM_BIN … dev consistency-check --runs 3 --keep-files` | `P-07` |
| `12_judge_wrv` | `judge_wrv.py` | `P-07` |
| `13_check_arms_teardown` | `check_arms.py --expect-config-sha` | `P-11` |

**The two-phase `capture_provenance.py` idiom is the load-bearing discovery here**
(logs 03 and 07). `captured_at_step` is fixed at **2** [VERIFIED: `capture_provenance.py:110`], so
the record must be created at `P-02`, *before* the flash — but the two `fw_readback_sha_*` fields do
not exist until `P-04`. Hence:

1. At `P-02`, run `capture_provenance.py --pending-readback` **once per position** (4× for a sweep
   cell), each with its own `--out $CELL_DIR/provenance_<position_id>.json`. This satisfies SC#2's
   "captured **before** that cell's first test step" for all four positions.
2. After each arm's `P-04`, run `capture_provenance.py --patch-readback` for **that arm's two**
   positions. It reads the cell's `READBACK-VERDICT.json`, rewrites only the two SHA fields
   atomically, and runs **no device or git probe** — so the pre-flash identity timestamps survive.

The default `--out` is `bench/cells/<slug>/provenance.json`, which would collide across four
positions. **Always pass `--out` explicitly**, matching `PROCEDURE.md`'s
`provenance_$POSITION_ID.json`.

---

## Answers to CONTEXT's Four Deferred Questions

### 1. `append_evidence.py`'s interface — answered above (§`append_evidence.py`).

### 2. W29C020's read-set duration budget

**Where the 53.437 s figure lives, and what it actually covers.** It is recorded twice — in
`EVIDENCE.jsonl`'s `BRINGUP-wrv` row, in the `verdict` prose and in `commands[2].note` ("elapsed
53.437s wall-clock -- the 262144B read-set cost baseline") [VERIFIED]. It is the **wall-clock of the
whole `dev consistency-check w27c512 --runs 3 --output-dir … --keep-files` invocation** on
Uno + Rev 2.0, **v1.33 arm**, W27C512 (65536 B).

**Decomposition, measured from the raw log**
[VERIFIED: `bench/cells/BRINGUP-wrv/logs/11_consistency_check.stdout.log`] — the app prints its own
per-run figure:

```
Run 1/3: SHA-256 fff15da9…  bytes=65536  elapsed=17.62s
Run 2/3: SHA-256 fff15da9…  bytes=65536  elapsed=17.62s
Run 3/3: SHA-256 fff15da9…  bytes=65536  elapsed=17.62s
```

- 3 × 17.62 s = **52.86 s** of app-timed reading.
- Residual ≈ **0.58 s** = process start-up + serial handshake + SHA/file overhead outside the timers.
- Implied rate on that chain: 65536 B / 17.62 s ≈ **3719 B/s**.

**What is knowable.** Arithmetic only: *if* the per-byte rate transfers, a single 262144 B read is
4× ≈ 70.5 s, a 3-run set ≈ 211 s + overhead ≈ **3.5 min**. **This is an arithmetic projection on an
untested assumption and must not be written into a plan as a budget.**

**What is not knowable and must be measured.** Whether the rate transfers at all. W29C020 is
algorithm `0x05` (5 V page-write EEPROM) against W27C512's `0x07`; a different protocol, 18 address
bits instead of 16, four times the 512-byte chunks on a Uno-class buffer. Phase 160's own gate says
it plainly: *"The 262144-byte read size is proven by fixture, not yet on silicon … The 262144 B path
(W29C020) is Phase 161's first on-silicon exercise of that size."* [CITED: `PHASE-160-GATE.md` §6].

**Where the first measurement lands.** Position **`A1__control__w29c020`** (`P-09`, A1's control
arm) — a **single** `read w29c020 …/run_01.bin`, so the first datum is a one-read cost, not a set.
The first **3-run set** at 262144 B lands one position later, at `A1__v133__w29c020`. The plan should
record both wall-clocks explicitly as the milestone's first 262144 B read figures and let A2/A3-B2
inherit them as baselines, exactly as A1's write wall-clock feeds D-08's ceiling.

### 3. D-09's smoke-check commands

Verified against the control arm's live `--help` this session:

```bash
# 1. chip-id read (non-destructive)
FIRESTARTER_CONFIG_DIR=/workspaces/.planning/v1.34/config \
  /workspaces/.v1.34-arms/control/.venv/bin/firestarter -p $PORT id w29c020

# 2. blank check — the STANDALONE command (non-destructive)
FIRESTARTER_CONFIG_DIR=/workspaces/.planning/v1.34/config \
  /workspaces/.v1.34-arms/control/.venv/bin/firestarter -p $PORT blank w29c020
```

- `firestarter id [OPTIONS] EPROM` — "Checks an EPROM, if supported." Only option: `-f/--force`.
- `firestarter blank [OPTIONS] EPROM` — "Checks if an EPROM is blank." Only option: `-f/--force`.

**Flag discipline verified:** neither command's argv carries any token from `forbidden_flags`
(`--force`, `-f`, `-b`, `--no-blank-check`, `--skip-erase`). `-f` *exists* as an option on both and
**must not be passed**. `-b`/`--no-blank-check` belongs to `write` and does not appear here at all —
the blank check is genuinely a standalone command, exactly as D-09 requires. argv0 is the control
arm's absolute `venv_bin`, so `forbidden_argv0` is satisfied.

**Outcome reading.** Both emit a success line the plan can grep by *string*, never line number:
`Chip ID check passed for W29C020: <id> (<t>s)` and
`Blank check for W29C020 successful (<t>s). <msg>`. `w29c020` resolves in the DB as
`W29C020,W29C020C,…`, WINBOND, 32 pins, chip ID **`0xDA45`**, Flash/EEPROM, VPP 12.0 V
[VERIFIED: `firestarter search w29c020`, this session].

**A not-blank result is a valid outcome** (D-09) — it still proves addressability. So is a
**chip-id mismatch refusal**: `blank` without `-f` refuses when the id does not match, and that
refusal *is* the seating/pin-1 signal D-09 is buying. Record it and proceed; do not force past it.

**Recorded as a bring-up datum in A1's cell dir, outside `P-01`…`P-11`** (D-09) — suggested
`bench/cells/A1/SMOKE-W29C020.md` plus `logs/` entries numbered in A1's own sequence, with a note
that these two invocations sit outside the step list and trigger no amendment.

**One free fact worth recording while there.** `write --help` states: *"Phase 153 (ERASE-01/
ERASE-02): since this phase, `-b`/`--no-blank-check` is **unread** on protocols `0x0D` and `0x05` —
neither protocol's write path performs a pre-write blank check any more."* W29C020 **is** `0x05`.
So on this part the write performs **no** pre-write blank check at all, and D-09's standalone `blank`
is the only blank observation the whole milestone will have for W29C020. That raises the value of
the smoke check and should be stated in the record.

### 4. A1's opening sequence — CONTEXT's provisional answer needs one correction

CONTEXT guessed (161-CONTEXT.md:260-262): *"A1 opens with a chip-out and a re-flash to control. That
is `P-03`→`P-04` run normally, not a special case."* **The chip-out is right; the placement is not.**

The inherited state [VERIFIED: `PHASE-160-GATE.md` §7 and `STATE.md:193`]: Arduino Uno, signature
`0x1e950f`, Rev 2.0 shield mounted, **W27C512 seated**, VPP 12.0 V, **v1.33 arm flashed**, port
`/dev/ttyACM0`. `/workspaces/firestarter` HEAD is `5759dc8…` (v133) [VERIFIED: `git rev-parse`].

`STATE.md`'s SAFETY line is explicit: *"No avrdude firmware operation (upload/read-back/
**signature-probe**) may run on this board while the chip is seated."* But `P-02` — **before**
`P-03`'s chip-out — runs `probe_board.py`, which is an avrdude signature probe (`-c arduino`, DTR
reset, `-n`). On a normal cell that is harmless because at `P-01`/`P-02` no chip has been seated yet
(`P-05` is where seating happens). **A1 is the exception because it inherits a seated chip.**

**Recommended handling — no amendment needed.** Fold "remove the chip from the socket" into
**`P-01`'s** operator handover for A1 (it is already an operator-physical D-02 checkpoint, so this
costs no extra handover), then run `P-02` normally against an empty socket. `P-03` then re-confirms
what is already true — a no-op confirmation, which is correct rather than wasteful. Rejected:
reordering `P-02`/`P-03`, which is a step-list change requiring its own amendment.

**The same wrinkle generalises to A2, and to the tail of both cells:**

- **A2:** the Rev 2.0 shield carries its socket with it, so whatever chip is in it travels to the
  uno328pb. `uno328pb` is Uno-class → the socket must be empty at A2's `P-02` too. Fold it into
  A2's `P-01`.
- **A1 and A2's `P-11`:** Amendment 2 added a literal `probe_board.py` re-run at teardown — another
  avrdude signature probe — and at `P-11` the **W29C020 is seated** (`P-08` put it there). So A1 and
  A2 each need an operator chip-out **before** the teardown probe. Amendment 2's own text
  acknowledges this exact bind ("backfilling it now would require an avrdude signature probe against
  a board this phase's own constraints forbid touching with a chip seated"). D-11 already sanctions
  a `P-11` operator action for A3/B2, so this is consistent, not a new class of handover.
- **Convenient consequence:** A1 and A2 end with an **empty socket**, which is precisely what the
  next cell's `P-02` needs. A3/B2 ends with **W27C512 seated** per D-11 (the Leonardo is exempt, so
  its `P-11` probe runs with the chip in).

---

## Cell A2 — the Expected-Failure Cell

The predicted symptom, from the source rather than from the ROADMAP summary
[CITED: project memory `project_uno328pb_vpp_recal_and_program_brownout`, Phase 54 UAT 2026-06-04,
observed on a **Rev 2.0** shield — the same shield A2 uses]:

> **Chip-PROGRAM path browns out — UNRESOLVED (backlog Phase 999.2).** Even with VPP correct + `-f`,
> a write hangs **deterministically on the FIRST program block** (6 attempts incl. reflash + reseat +
> random/zero payloads); **the firmware stops responding the instant it drives program current**
> (VPP 12.7 V / VCC 5.3 V — suspected VPP-regulator brownout under load). The READ/blank-check path
> works (streamed 72×512 B chunks).

Three planning consequences:

1. **It is a hang, not a fast error.** D-08's ceiling is the mechanism that ends it. Expect to hit
   the 165 s W27C512 ceiling on A2's W27C512 positions rather than a clean non-zero exit.
2. **The last progress frame will name block 0.** Write-progress emission is **time-keyed per block
   and the clock restarts each block**, so there are **zero intra-block frames** — the captured last
   frame names the block, never a byte offset (161-CONTEXT.md:157-159; standing memory
   `reference_progress_emit_is_time_keyed_per_block`).
3. **The read path works on this board.** So a `blank`/`read` after a failed write is still
   informative, and `judge_wrv.py` can still be run to produce a real verdict artifact (below).
4. **Un-asserted, not un-expected.** SC#3 requires the symptom be **observed and recorded** — where
   it stops and exactly what the host reported — never asserted from 999.2. And per D-07, a
   **completed** program on either arm is an observation *against* 999.2, recorded, not discarded.
   W29C020 is algorithm `0x05`, a 5 V page-write part, and has **never been tried on this board**.

### Producing a non-blank record for a failed position

`judge_wrv.py --reads` requires the directory to **exist** but happily counts zero files
[VERIFIED: `judge_wrv.py:203-207` `is_dir()` check, then `load_reads()` globs]. With
`--app-verdict 2` or `read_count == 0` the judged verdict is **`incomplete-read-set`**
[VERIFIED: `judge_wrv.py:109-110`]. So:

```bash
mkdir -p "$POSDIR/reads"
python3 /workspaces/.planning/v1.34/tools/judge_wrv.py \
  --written "$POSDIR/written.bin" --reads "$POSDIR/reads" \
  --expect-size 65536 --app-verdict 2 --position-id A2__control__w27c512 \
  --pins /workspaces/.planning/v1.34/rig-pins.json \
  --out "$POSDIR/WRV-VERDICT.json"   # exits 1 — capture the code, do not fail the step
```

Every one of the 12 positions then holds a real `WRV-VERDICT.json`, which is what SC#1's "no
position is blank" and `append_evidence.py`'s refusal contract both need.

---

## The Write-Duration Definition and the v1.31 0.37 s Non-Claim (BOARD-04)

**The judged measure is wall-clock around the write command.** It is the only measure that exists
for every arm, target and outcome — including a position where the write is *expected* to fail and
the app emits no success line at all. The app's own success-only figure is recorded **alongside** as
a second, **unjudged** datum whenever the write succeeds
[CITED: `PROCEDURE.md:414-426`].

**What v1.31's 0.37 s actually is** [VERIFIED at source:
`.planning/phases/145-bench-validation/145-BENCH-LOG.md:1446-1451`]: the **spread (max − min)**
across three full 64 KiB write cycles' **app-reported, success-only** figures — 106.06 / 105.69 /
106.06 s — on **Leonardo + Rev 2.0**, firmware `ebe9cb3`. **It is a spread, not a duration.** Phase
145 made no comparative claim with it.

**The non-claim to carry, not re-derive** (`PROCEDURE.md:437-447`): v1.34's per-position wall-clock
is a *different quantity* by a *different method*. v1.34's own **app-reported** figures are the
directly comparable quantity, and even that comparison is valid **only on A3/B2**, the one cell this
milestone shares with v1.31's rig.

**A measured trap the planner must pre-empt.** `BRINGUP-wrv`'s W27C512 write took **41.010 s
wall-clock / 37.48 s app-reported** on a Uno [VERIFIED: `bench/cells/BRINGUP-wrv/WRITE.md:94-97`],
against v1.31's ~106 s on a Leonardo. That is roughly a **3× shift**, and it is **not** a v1.33
effect: PR #55's per-byte VPE-settle amortisation (105.9 s → 33.35 s, merged as fw `3.0.0b22`) is in
the **control** arm's merge-base — `rig-pins.json:96` records the same PR as the reason the control
hex is *larger* than v133's. **Both arms carry the fix.** A3/B2's app-reported figures will therefore
land far below 106 s on **both** arms, and stating that next to 0.37 s without this sentence would
read as a spectacular v1.33 improvement that is nothing of the kind. Say it explicitly in the record.

**A structural point about the comparison itself:** v1.34 takes **one** write per position, so there
is **no v1.34 spread** to set against v1.31's spread. The honest A3/B2 statement is: two
app-reported figures (control, v133) whose *difference* is the A/B signal, presented beside v1.31's
three-cycle spread with the method difference named — never a single figure "compared to 0.37 s".

**One more arm-dependence.** `PROCEDURE.md:433` cites the success line at
`eprom_operations.py:1934`. That is the **v133** arm's line number; on the **control** arm the
identical string is at **line 2045** [VERIFIED: grepped both arms this session]. Any verify leg or
extraction that keys on a line number is arm-dependent. **Grep the string
`Write to {CHIP} successful (`, never a line number.**

---

## D-08 — Stall Ceilings and the Logged Kill

| Chip | Ceiling | Basis |
|---|---|---|
| W27C512 | **~165 s** | 4 × the measured healthy **41.010 s wall-clock** ([VERIFIED] `bench/cells/BRINGUP-wrv/WRITE.md:94`; app-reported 37.48 s at `:97`) |
| W29C020 | 4 × A1's control-arm W29C020 wall-clock | Supplied for free by the cell order — A1 runs before A2 |
| W29C020 fallback | **600 s absolute**, recorded *as a fallback, not a derivation* | Used only if A1's own W29C020 never completes |

**The logging half is the load-bearing half.** Phase 160's single **unlogged** shell-timeout kill (a
120 s cut during plan 11's `vpp` invocation) is what produced the untraceable `~/.firestarter`
contamination that phase carried forward. A kill must therefore run under a **numbered log** in the
cell's `logs/` sequence, with **full stdout and stderr** captured and the **last progress frame**
recorded, and be written into the record as
`timed out at N s against a measured baseline of M s`.

Because progress emission is **time-keyed per block with the clock restarting each block**, there
are **zero intra-block frames**: the last frame names the **block**, not a byte offset. On A2 the
expected last frame is the first program block.

Mechanically, the kill wants a wrapper that survives the timeout with its output intact — e.g.
`timeout --signal=INT <N> … > logs/NN_write.stdout.log 2> logs/NN_write.stderr.log`, with the
wrapper's own exit code (124 on timeout) recorded next to the elapsed wall-clock. Do **not** pipe
the killed command's output through anything that would swallow it.

---

## D-10 — The uno328pb v1.33 Pre-Proof

**What is proven today, exactly** [VERIFIED: both files read this session]:

| File | `flashed_arm` | `expect_arm` | `judged_match` | `judged_span_bytes` | Meaning |
|---|---|---|---|---|---|
| `BRINGUP-uno328pb/READBACK-VERDICT.json` | `control` | `control` | **`true`** | 26074 (control span) | The `vector-exclusion` policy works — **on the control arm's hex** |
| `BRINGUP-uno328pb/crossflash/READBACK-VERDICT.json` | `v133` | `control` | **`false`** | 26074 (control span) | The deliberate D-03 cross-flash MISMATCH — a negative control that fired |

**What is *not* proven:** the v1.33 arm's own **23000 B** span has never been read back and matched
on a 328PB. Both recorded verdicts judge against the **control** span, and the `vector-exclusion`
offsets (0 and 100) were derived live **on the control-arm flash** (`BRINGUP-uno328pb/BOOTLOADER.md`,
from `-xshowvector`). `P-04` names *"a read-back mismatch on a board that was correctly flashed"* as
a **`P-H1` halt** — so without the pre-proof, A2's second arm would be the first time
`judge_readback.py` is asked to confirm a v1.33 flash on a 328PB, live, at cell 2 of 3, with A1
already spent.

**What the pre-proof runs** (bare uno328pb, no shield, no chip → the Uno-class chip-out rule is
satisfied trivially; ~3 min and one USB replug, **before A1**):

```bash
# 0. re-verify the port — CH340 bridge, so /dev/ttyUSB*, and the number shuffles
python3 /workspaces/.planning/v1.34/tools/probe_board.py \
  --target uno328pb --port $PORT \
  --pins /workspaces/.planning/v1.34/rig-pins.json \
  --out $CELLDIR/board_probe.json          # expect board_signature 0x1e9516

# 1. flash the v1.33 arm through the sanctioned path only
/usr/local/bin/git -C /workspaces/firestarter checkout 5759dc8d644a8a7fb26e9a0ccd11a8bfd53fc463
/usr/local/bin/git -C /workspaces/firestarter status --porcelain      # must be empty
cd /workspaces/firestarter && /usr/local/bin/pio run -t upload -e uno328pb

# 2. the proof
python3 /workspaces/.planning/v1.34/tools/judge_readback.py \
  --target uno328pb --port $PORT --flashed-arm v133 --expect-arm v133 \
  --out-dir $CELLDIR --pins /workspaces/.planning/v1.34/rig-pins.json
```

**Success criterion:** `judged_match: true` with `judged_span_bytes: 23000` (the **v133**
`hex_span_expected_by_arm` value for `uno328pb`, **not** 26074 and **not** the legacy scalar) and
`vector_exclusions_applied` carrying both entries.

**Do NOT assert SHA equality** — see Pitfall 4.

Record it as a bring-up position in its own cell dir (suggested `bench/cells/BRINGUP-uno328pb-v133/`,
a `BRINGUP-` prefix so `_schema.bringup_row_exclusion` keeps it out of the 20-position close-out
reconciliation), never as one of the 12.

---

## Common Pitfalls

### Pitfall 1 — A1/A2's avrdude signature probes collide with the chip-out rule

**What goes wrong:** `P-02` and (post-Amendment-2) `P-11` both run `probe_board.py`, an avrdude
signature probe. `STATE.md`'s SAFETY line and standing bench rule 2 forbid exactly that on a
Uno-class board with a chip seated. A1 inherits a seated W27C512; at `P-11` both A1 and A2 have a
seated W29C020.
**Why it happens:** `P-02` precedes `P-03` in the step list, which is correct for a cell that starts
with an empty socket — the normal case. A1 is the milestone's only inherited-state cell, and `P-11`
is the tail of every Uno-class cell.
**How to avoid:** fold the chip-out into `P-01`'s operator handover for A1 and A2, and add an
operator chip-out before `P-11`'s teardown probe on both. No amendment needed; both are already
operator-physical moments.
**Warning signs:** a plan whose first `human-verify` says only "declare the silkscreen".
`[VERIFIED: PROCEDURE.md:146-171, 316-334; STATE.md:193; PHASE-160-GATE.md §7]`

### Pitfall 2 — `capture_provenance.py` has never run on a Leonardo and will hard-refuse

**What goes wrong:** A3/B2's `P-02` fails before the cell starts.
**Why it happens:** `capture_provenance.py` internally shells out to `probe_board.py` **first**, then
to `$ARM_BIN -v -p $PORT hw`, and treats a non-zero from either as a **hard failure, never a null
field** [VERIFIED: `capture_provenance.py:210-296`]. `probe_board.py` performs **no 1200-baud touch**
[VERIFIED: grep — zero touch references in the file], and a Leonardo running its *application*
firmware was **measured** to reject the `avr109` handshake: *"the application firmware does not speak
avr109; the bootloader must be entered first, even for identity"*, rc=1 after ~6.0 s
[CITED: `bench/cells/BRINGUP-leonardo/BOOTLOADER-WINDOW.md`, "Attempt 0"]. And
`capture_provenance.py` has been run live on exactly **one** board — only `BRINGUP-wrv` (target
`uno`) holds a `provenance.json`; `BRINGUP-uno328pb` and `BRINGUP-leonardo` hold none
[VERIFIED: directory listing]. There is a second half to the bind: even *with* a preceding touch, the
following `hw` probe runs against Caterina, not the application.
**How to avoid:** treat this as D-10's twin and **pre-prove `capture_provenance.py` on the Leonardo
before A3/B2's cell opens** — same argument, same cost, and A3/B2 is the milestone's most expensive
cell to lose. Failing that, budget an explicit `P-H1` risk at A3/B2 `P-02` and know the shape of the
fix: sequence `hw` (application) → `touch_1200.py --port $PORT` (bare mode) → `probe_board.py`
inside the ~8 s Caterina window, and give `capture_provenance.py` a way to consume those two results
rather than re-running them. Measured window numbers: touch→responsive programmer **3.487 s**,
touch→completed judged read-back **3.878 s**, settle **2.0 s**
[VERIFIED: `rig-pins.json:134-139`]. The touch returns the **same** node, never a new one;
`--wait-new-port` was empirically refuted on this board.
**Warning signs:** an A3/B2 plan whose `P-02` is a copy of A1's.

### Pitfall 3 — one `reads/` directory for four positions poisons `judge_wrv.py`

**What goes wrong:** up to 9 of the 12 positions get a false `disagreement` or `mismatch`.
**Why it happens:** `PROCEDURE.md`'s literal blocks give `P-07` **and** `P-09` the same
`--output-dir $CELL_DIR/reads` and the same `--reads $CELL_DIR/reads`, and
`judge_wrv.load_reads()` **globs** `sorted(reads_dir.glob("run_*.bin"))` and counts what it finds
[VERIFIED: `judge_wrv.py:146-150`]. Concretely: `P-09` (262144 B) sees `P-07`'s three 65536 B files →
`size_violations` non-empty → the judged verdict **can never be `match`**
[VERIFIED: `judge_wrv.py:112-113`]. Across the arm switch it is worse: control's `run_01.bin` from a
*different mask* survives into v133's set → `distinct_read_shas == 2` → verdict `disagreement`, an
N=3 finding that never happened. The same collision hits `$CELL_DIR/written.bin` (four different
images, one filename — and the commit-on-failure exception needs each failing position's own bytes)
and `$CELL_DIR/wrv_verdict.json`.
**How to avoid:** per-position paths, `$POSITION_ID`-keyed, folded into **Amendment 3 clause (3)**.
Suggested layout, chosen so `bench/.gitignore` still covers the large files:
`$CELL_DIR/reads/$POSITION_ID/run_NN.bin` (covered by `cells/*/reads/`),
`$CELL_DIR/positions/$POSITION_ID/written.bin` **plus** a new `.gitignore` line, and
`$CELL_DIR/positions/$POSITION_ID/WRV-VERDICT.json`.
**Warning signs:** any `--reads` or `--output-dir` argument that does not contain the position id.
**Bonus naming inconsistency to settle in the same edit:** `PROCEDURE.md` says
`--out $CELL_DIR/wrv_verdict.json` (lowercase) while `BRINGUP-wrv` and D-05 both use
`WRV-VERDICT.json`. Pick `WRV-VERDICT.json` and say so.

### Pitfall 4 — on uno328pb, the judged SHAs differ on a *correct* flash

**What goes wrong:** an `<automated>` leg asserting
`sha_actual_judged == sha_expected_judged` produces a false RED on every A2 flash, twice.
**Why it happens:** `judge_readback.py` computes `judged_match` with an **exclusion-aware byte
compare** (`judge_span_bytes()` skips every offset in `compute_excluded_positions()`), but records
`sha_actual_judged` / `sha_expected_judged` as plain SHAs of the **raw** spans
[VERIFIED: `judge_readback.py:120-147`]. On `uno328pb` 8 bytes are excluded (reset vector `[0,4)`,
SPM_Ready vector `[100,104)`), so a correct flash yields `judged_match: true` with
`43dcb663…` ≠ `b18a7151…` — visible in the committed `BRINGUP-uno328pb/READBACK-VERDICT.json`.
**How to avoid:** the verdict is **`judged_match == true`**, always, on every target. Assert that,
plus `judged_span_bytes == pins.targets[env].hex_span_expected_by_arm[arm]`.
**Warning signs:** any leg comparing two `sha_*_judged` fields to each other.

### Pitfall 5 — `gate_record.py`'s cross-oracle leg is inert against this schema

**What goes wrong:** the planner trusts `run_gates.sh` to catch a row that says `validated` while its
SHAs disagree. It cannot.
**Why it happens:** `check_cross_oracle()` reads `written_image_sha256`, `read_sha256` and
`app_dev_consistency_verdict` [VERIFIED: `gate_record.py`], and **none of the three is in the v1.34
`EVIDENCE.jsonl` `record_keys`** — which carry `sha256`, `read_shas`, `app_verdict_unjudged`. Every
guard is `if written and read and …`, so with all three `None` the function returns an empty
violation list for every row. This is the `gate authored before the content it checks` class, not a
disclosed §6 item.
**How to avoid:** `append_evidence.py` **derives** `outcome` from `WRV-VERDICT.json` (column 40 of
the map above) and refuses to emit `validated` unless `sha_verdict_judged == "match"`,
`verdict_disagreement` is false and `size_violations` is empty. The judged truth then reaches the row
by mechanism instead of by a gate that cannot see it.
**Warning signs:** a plan citing `gate_record.py` as the oracle for a position's correctness. It is a
**shape and domain** gate: field presence/non-nullity, the `not measured — <reason>` idiom, the
two-state outcome domain, forbidden flags by exact token, argv0 allow-list, `pio` cwd. Those all
work. Correctness is `judge_wrv.py`'s job.

### Pitfall 6 — `P-11` teardown assertion (1) is already RED

**What goes wrong:** twelve `P-H1` false halts, one per position, in a phase whose halt policy says a
rig failure stops the sweep.
**Why it happens:** the literal text is *"Assert `~/.firestarter` still does not exist … Treat its
existence as a `P-H1` rig failure"* (`PROCEDURE.md:350-356`), but the directory exists on this
container right now [VERIFIED: `ls`/`stat` this session, mtime `2026-08-27 07:59:25 UTC`, one file
`config.json`, 30 bytes, `{"port": "/dev/ttyACM0"}`], as a Phase 160 disclosed carry-forward whose
removal the sandbox denies.
**How to avoid:** Amendment 3 clause (4) restates it as *unchanged from the recorded baseline*, with
the SHAs and mtime from §Amendment 3 pinned. CONTEXT already reaches the same conclusion
(161-CONTEXT.md:441-444: *"if it changes, that is a `P-H1` finding"*) — the amendment makes the
procedure text say so.
**Warning signs:** a verify leg containing `test ! -d ~/.firestarter`.

### Pitfall 7 — `render_evidence.py --append` does not re-render `EVIDENCE.md`

**What goes wrong:** the per-cell `run_gates.sh` gate (D-04) goes red on its fourth live leg, and it
looks like a hand-edit rather than a missed step.
**Why:** the `--append` branch returns before the render path [VERIFIED: `render_evidence.py:355`].
**How to avoid:** always pair the append with a plain render, in the same step. Twelve appends, twelve
renders.

### Pitfall 8 — `judge_wrv.py` exits 1 on a non-match, after writing the artifact

A `skipped-with-reason` position is a **normal, expected outcome** here (A2 is expected to produce
four of them). If the plan's step treats `judge_wrv.py`'s exit code as its own success criterion, an
expected cell failure becomes a plan failure. Capture the code as a datum; the verdict JSON is written
before the non-zero return [VERIFIED: `judge_wrv.py:213-238`].

### Pitfall 9 — the standing environment traps (all four re-confirmed)

- **`pio` runs only with cwd `/workspaces/firestarter`.** The generated, gitignored
  `/workspaces/platformio.ini` has a duplicate `[platformio]` section that makes `configparser`
  abort; the identical command string succeeds or fails on cwd alone. `gate_record.py` rejects any
  recorded `pio` command whose `cwd` is not `pins.pio_project_dir`.
- **`FIRESTARTER_CONFIG_DIR` is set inline, never exported.** `config.py` computes `HOME_PATH` /
  `DATABASE_FILE` / `PIN_MAP_FILE` at **import time**. A shell `FOO=bar cmd` prefix is stripped
  before exec and **never reaches argv**, so no argv check can detect a missing prefix —
  **asserting the `~/.firestarter` baseline at per-cell teardown is the only detector that exists.**
- **Every `import firestarter` probe needs `python -P`.** `/workspaces/firestarter` (the firmware
  repo) wins as a PEP 420 namespace portion and the probe silently prints `None` without it.
  Measured on both arms [CITED: `arms-provenance.json` `pitfall1_trap_confirmed`].
- **`run_gates.sh`'s exit code is measured directly, never through a pipe** (D-04).

---

## Don't Hand-Roll

| Problem | Don't build | Use instead | Why |
|---|---|---|---|
| Append a row to `EVIDENCE.jsonl` | `open(..., "a")` | `render_evidence.append_row_to_file()` / `--append` | Append-only integrity: it re-reads and asserts the prefix is byte-unchanged, then does an atomic temp+`os.replace`; a plain append is not atomic and tears |
| Compute the config-dir SHA | a fresh `sha256` walk | `check_arms.compute_config_dir_sha()` via the `importlib` sibling idiom | `gate_record.py` already does exactly this and says "No SHA algorithm is re-derived here" |
| Validate a `"not measured — reason"` string | a new regex | `gate_record._NOT_MEASURED_RE` | Two accepted separators (em dash **and** `--`), case-insensitive, rejects a bare `not measured` |
| Judge a read set | compare the app's `Consistency check: PASS` | `judge_wrv.py` | Pitfall 6: the app compares the N reads to **each other**, never to the written image; a chip that reliably returns the wrong bytes still passes |
| Prove a flash | avrdude's `-U flash:w:…:v` verify pass | `judge_readback.py` | D-01: the uploader must never judge its own upload |
| Regenerate a position's image | a bespoke script | `gen_addr_image.py` + `IMAGE-PLAN.json`'s recorded `mask`/`stamp_width` | The recorded `sha256` is the check; a different mask invalidates it |
| Identify a board | `firestarter fw`/`hw` handshake | `probe_board.py` signature probe | Both arms answer identically (`3.0.0b22` / `3.0.0b32`); a handshake names nothing |
| Enter the Caterina bootloader | a hand-rolled serial open | `touch_1200.py` (bare mode) | It refuses to swallow a serial failure, unlike the product-code analog it was copied from |
| Re-derive `hex_span` | a literal in a verify leg | `pins.targets[env].hex_span_expected_by_arm[arm]` | The flat `hex_span_expected` equals the v133 value and rejects a correct control flash |

**Key insight:** every one of these already exists, already has a `--selftest`, and already fails
closed. The single highest-leverage thing this phase can do is *not write code* — one new tool, one
amendment, and twelve careful executions.

---

## Code Examples

### A sweep position's write→read→judge (P-07, with per-position paths)

```bash
FCD=/workspaces/.planning/v1.34/config
T=/workspaces/.planning/v1.34/tools
CELL=/workspaces/.planning/v1.34/bench/cells/A1
POS=A1__control__w27c512
ARM_BIN=/workspaces/.v1.34-arms/control/.venv/bin/firestarter
mkdir -p "$CELL/positions/$POS" "$CELL/reads/$POS"

# image: mask 16 (0x10), stamp 16, 65536 B  -> IMAGE-PLAN.json sha 8ee56868...
python3 "$T/gen_addr_image.py" --stamp-width 16 65536 16 "$CELL/positions/$POS/written.bin"

# write, timed by wall clock (the judged measure)
time FIRESTARTER_CONFIG_DIR=$FCD "$ARM_BIN" -p "$PORT" write w27c512 "$CELL/positions/$POS/written.bin"

# control arm: ONE read, named to match judge_wrv's run_NN.bin glob
FIRESTARTER_CONFIG_DIR=$FCD "$ARM_BIN" -p "$PORT" read w27c512 "$CELL/reads/$POS/run_01.bin"

# judge -- exit 1 on non-match is a DATUM, not a step failure
python3 "$T/judge_wrv.py" --written "$CELL/positions/$POS/written.bin" \
  --reads "$CELL/reads/$POS" --expect-size 65536 --app-verdict 0 \
  --position-id "$POS" --pins /workspaces/.planning/v1.34/rig-pins.json \
  --out "$CELL/positions/$POS/WRV-VERDICT.json"
```

The v1.33 arm substitutes the read step with the three-run form
(`dev consistency-check w27c512 --runs 3 --output-dir "$CELL/reads/$POS" --keep-files`), and the
control arm escalates to the same three-run form **only** where the v1.33 arm's three reads for that
position disagreed. A disagreement is **recorded, never retried away.**

### The two-phase provenance capture (P-02 then P-04)

```bash
# P-02 -- once per position, BEFORE any test step. captured_at_step is fixed at 2.
for POS in A1__control__w27c512 A1__control__w29c020 A1__v133__w27c512 A1__v133__w29c020; do
  ARM=${POS#A1__}; ARM=${ARM%%__*}; CHIP=${POS##*__}
  FIRESTARTER_CONFIG_DIR=$FCD python3 "$T/capture_provenance.py" \
    --cell-id A1 --position-id "$POS" --arm "$ARM" --target uno --port "$PORT" \
    --chip "$CHIP" --shield-rev "Rev 2.0" --pending-readback \
    --pins /workspaces/.planning/v1.34/rig-pins.json \
    --out "$CELL/provenance_$POS.json"
done

# P-04 -- after THIS arm's flash + judge_readback, patch that arm's two positions only
for POS in A1__control__w27c512 A1__control__w29c020; do
  python3 "$T/capture_provenance.py" --cell-id A1 --position-id "$POS" \
    --arm control --target uno --port "$PORT" --chip "${POS##*__}" \
    --shield-rev "Rev 2.0" --patch-readback --out "$CELL/provenance_$POS.json"
done
```

`--patch-readback` runs **no** device or git probe, so the pre-flash identity timestamps survive
untouched — that is why it exists.

### The per-cell gate (D-04) — exit code measured directly

```bash
bash /workspaces/.planning/v1.34/tools/run_gates.sh > "$CELL/logs/NN_run_gates.stdout.log" \
                                                    2> "$CELL/logs/NN_run_gates.stderr.log"
RC=$?            # <-- directly. NEVER `run_gates.sh | tee`, which yields tee's status.
echo "run_gates exit=$RC"
```

---

## Environment Availability

Probed in this session; no hardware command was run.

| Dependency | Required by | Available | Version | Fallback |
|---|---|---|---|---|
| `run_gates.sh` suite (11 tools + 5 live gates) | D-04 per-cell gate | ✓ **exit 0** | 11/11 selftests, 5/5 live | — |
| control arm binary | every control position | ✓ | app `6bfa645…`, self-reports `3.0.0b32` | — |
| v133 arm binary | every v133 position | ✓ | app `cb189a9…`, self-reports `3.0.0b32` | — |
| both arms' CLI surface identical | one arm-agnostic step vocabulary | ✓ | 25/25 entries, zero set difference; `--help` text also identical | — |
| pinned avrdude 8.1 | `probe_board.py`, `judge_readback.py` | ✓ | 8.1, `-A` probe PASSED | system 7.1, named, unused |
| pinned `avr-objcopy` | hex normalisation | ✓ | binutils 2.26 (not on PATH — hence pinned) | — |
| PlatformIO | `P-04` flash | ✓ | core 6.1.19 | — |
| six committed `.hex` images | both arms, three targets | ✓ | all 6 match `SHA256SUMS.txt` | — |
| frozen `FIRESTARTER_CONFIG_DIR` | rule 9 | ✓ | sha `77adfdd2…`, unchanged | — |
| `/workspaces/firestarter` HEAD | `P-04` checkout | ✓ | currently `5759dc8…` (**v133**) — A1 must check out control `8695ee5…` first | — |
| Uno + Rev 2.0 + W27C512 seated + v1.33 | A1's inherited state | ✓ | `/dev/ttyACM0`, sig `0x1e950f`, VPP 12.0 V | — |
| uno328pb board | A2, D-10 | **operator-held** | CH340 → `/dev/ttyUSB*` | — |
| Leonardo board | A3/B2 | **operator-held** | native USB → `/dev/ttyACM*` | — |
| W29C020 DIP32 part | 6 of 12 positions | **operator-held, never yet run on this rig** | DB id `0xDA45` | D-09 smoke check is the early detector |

**Missing with no fallback:** none — but three of the four physical items are operator-held and
their availability is confirmed only at each cell's `P-01`.
**Known-degraded:** `capture_provenance.py` is unproven on `uno328pb` and `leonardo` (Pitfall 2).

---

## Validation Architecture

`workflow.nyquist_validation` is absent from `.planning/config.json`, so it is treated as **enabled**.
This phase has no unit-test framework: it is a hardware evidence phase and its "tests" are the rig's
own gates plus the 12 positions.

### Test framework

| Property | Value |
|---|---|
| Framework | `bash .planning/v1.34/tools/run_gates.sh` — 11 Python `--selftest` suites + 5 live gates |
| Config file | `.planning/v1.34/rig-pins.json` (constants) + `bench/EVIDENCE.jsonl` line 1 (`_schema`) |
| Quick run | `bash .planning/v1.34/tools/run_gates.sh --quick` (skips `check_rebuild`/`check_arms` only) |
| Full suite | `bash .planning/v1.34/tools/run_gates.sh` — **exit code measured directly, never through a pipe** |
| Baseline | measured green in this session: 11/11 selftests, 5/5 live gates, `EXIT=0` |

### Requirements → validation map

| Req | Behaviour | Type | Automated command | Exists? |
|---|---|---|---|---|
| BOARD-01 | A1's 4 positions each hold a verdict or a named absence | evidence | `gate_record.py --jsonl bench/EVIDENCE.jsonl` + a row-count assertion over `cell_id == "A1"` | ✅ (row filter is new, trivial) |
| BOARD-02 | A2's 4 positions, failure **observed** on both arms | evidence + human | same, plus each A2 row's `verdict` naming the observed stop point and host output | ✅ / prose is human by D-05 |
| BOARD-03 | A3/B2's 4 positions | evidence | same, filtered on `cell_id == "A3/B2"` | ✅ |
| BOARD-04 | measured write duration per position | evidence | assert `write_duration_wallclock_s` non-null on all 12 rows (a real float or the `not measured — reason` shape) | ✅ via `gate_record.py` field-presence |
| SC#2 | provenance captured before the cell's first test step; arm confirmed by read-back | mechanism | `captured_at_step == 2` on all 12 `provenance_*.json`; `READBACK-VERDICT.judged_match == true` per flash | ✅ |
| SC#5 | A3/B2 executed exactly once | arithmetic | exactly 4 rows with `cell_id == "A3/B2"`, one per `(arm × chip)` | ✅ — and `render_evidence.append_row_to_file` refuses a duplicate `position_id` structurally |
| D-05 | zero machine-readable fields transcribed | mechanism | `append_evidence.py --selftest` negative legs: a field from the wrong position's provenance must be **refused** | ❌ **Wave 0** |
| Amendment 3 | procedure stays arm-agnostic | gate | `render_steps.py --arm control` vs `--arm v133` diff empty (3rd live leg of `run_gates.sh`) | ✅ |

### Sampling rate

- **Per position:** `judge_wrv.py` (the oracle) + `append_evidence.py` + `render_evidence.py` render.
- **Per cell (= per wave, D-01/D-04):** full `bash run_gates.sh`, exit code measured directly.
- **Phase gate:** full suite green, 12 rows present, then `/gsd-verify-work`.

### Wave 0 gaps

- [ ] `.planning/v1.34/tools/append_evidence.py` — the tool itself (D-05).
- [ ] Its `--selftest`: positive (a complete position assembles a 40-key row in `record_keys` order)
      **plus** named negatives — missing `WRV-VERDICT.json`; `position_id` disagreeing across the
      three artifacts; `image_sha` ≠ `written_sha`; a bare `not measured` in `blank_state`; an empty
      `verdict`; `outcome` derived `validated` while `sha_verdict_judged != "match"`.
- [ ] `PROCEDURE.md` Amendment 3 (four clauses) + a `run_gates.sh` re-confirmation.
- [ ] `bench/.gitignore` extension if per-position `written.bin` moves out from under
      `cells/*/written.bin`.

### Claims this phase CANNOT validate — record as non-claims

1. **Any electrical claim.** Program-window VPP/VCC **under load** stays unmeasured (the
   DTR-reset-on-close tooling gap). v1.34 makes **no electrical claim**.
2. **8 bytes on uno328pb.** Under `vector-exclusion`, `[0,4)` and `[100,104)` — 8 of 26074 judged
   bytes — are excluded from every comparison. A fault confined entirely to those 8 bytes is
   invisible on A2. (Disclosed §6 item; carry it, do not re-raise it.)
3. **A duration-to-spread comparison against v1.31.** See §Write-Duration. Also: v1.34's ~3× faster
   W27C512 figures are PR #55's VPE-settle amortisation, present in **both** arms — not a v1.33 effect.
4. **Python 3.11.** Both arms run devcontainer 3.12.14, not the app-CI floor. (Disclosed §6.)
5. **Stable-channel reachability.** `dev consistency-check` is in `BETA_ONLY_DEV_COMMANDS`; the
   judged SHA is unaffected, but the read-set command is a dev-channel-only surface. (Disclosed §6.)
6. **Byte-level re-check of a clean position.** A clean-match read set is re-checkable by SHA only —
   the bytes stay local unless the position failed, in which case they are committed with
   `git add -f`.
7. **Cause.** This phase records; **Phase 165** classifies and fixes, on the v1.33 PR branch.

---

## Security Domain

`security_enforcement` is not set to `false`, so the domain is addressed. This phase writes no
application code, exposes no network surface, accepts no untrusted input, and installs no packages.

| ASVS category | Applies | Control |
|---|---|---|
| V2 Authentication | no | no auth surface; local bench only |
| V3 Session Management | no | no sessions |
| V4 Access Control | no | single-operator local rig |
| V5 Input Validation | **yes (narrowly)** | `append_evidence.py` parses three JSON artifacts it produced itself; validate with `json.load` + explicit key/type checks and fail closed, per the house `FAIL:` idiom |
| V6 Cryptography | **yes (narrowly)** | SHA-256 is used as an **integrity oracle, not a security primitive**; always `hashlib.sha256`, never a hand-rolled digest, and never a transcribed hash |
| V12 Files & Resources | **yes** | atomic temp+`os.replace` writes only; `render_evidence` re-asserts the byte-unchanged prefix before replacing |
| V14 Configuration | **yes** | every binary is pinned in `rig-pins.json`, never resolved from `PATH`; `forbidden_binaries` refused outright |

| Threat pattern | STRIDE | Mitigation already in the rig |
|---|---|---|
| Wrong binary silently executed (`PATH` shadowing) | Spoofing | `forbidden_argv0` + `gate_record.check_commands` absolute-path allow-list |
| A record claiming a result it did not measure | Repudiation | `capture_provenance.py` / `append_evidence.py` derive every field; "no SHA is ever transcribed by hand" |
| A gate that discovers nothing and passes | Tampering | `run_gates.sh` exits **2** on zero tools discovered; every tool fails closed on an empty input |
| A row rewritten after the fact | Tampering | append-only with a byte-unchanged-prefix re-read; a duplicate `position_id` is refused |
| Destructive flag slipping into a bench command | Tampering | `forbidden_flags` by exact token, enforced mechanically |

**One live security-adjacent hygiene item, disclosed not new:** `~/.firestarter` exists outside the
frozen config dir. Do **not** delete it (the sandbox denies it and deleting destroys the evidence);
its baseline is pinned in §Amendment 3 and a *change* is the finding.

---

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|---|---|---|
| A1 | The Caterina sequencing fix for Pitfall 2 (`hw` → touch → probe) is a **proposal**, not a measured chain — `capture_provenance.py` has never completed on a Leonardo | Pitfall 2 | A3/B2's `P-02` still hard-refuses; recover as a `P-H1` fixed in-phase, at the most expensive cell |
| A2 | The ≈3.5 min projection for a 3-run 262144 B read set assumes W29C020 streams at W27C512's measured 3719 B/s | §W29C020 read budget | Only a schedule estimate; explicitly **not** a budget, and the real figure lands at A1 |
| A3 | A2's W27C512 write will hang at the first program block on both arms | §Cell A2 | D-07/SC#3 already require this be observed; a completion is a *finding*, and D-08's ceiling bounds the cost either way |
| A4 | `probe_board.py`'s `-n` signature probe counts as an "avrdude operation" barred with a chip seated | Pitfall 1 | Derived from `STATE.md:193`'s explicit "signature-probe" wording; if it does not, the A1 `P-01` chip-out is merely harmless |
| A5 | A `[ASSUMED]` reading of A2's expected VPP behaviour — the board was recalibrated to R1=270000 in 2026-06 and that EEPROM value is assumed to persist | §Cell A2 | `P-06`'s single confirming `vpp` read is the check; a bad reading is a bench fault fixed at `P-06`, never forced past |
| A6 | The suggested layout `cells/<slug>/positions/<pos>/written.bin` requires a `.gitignore` addition | Pitfall 3 | Measured with `git check-ignore`; if the planner keeps `written.bin` under `reads/<pos>/` instead, no `.gitignore` change is needed |

Everything else in this document is `[VERIFIED]` from a file read, a `--help` invocation, or a
gate run in this session, or `[CITED]` to a specific artifact.

---

## Open Questions

1. **Should `capture_provenance.py` get a Leonardo pre-proof, mirroring D-10?**
   - Known: it has run live on exactly one board (Uno); it shells to `probe_board.py` with no touch;
     that combination is measured to fail on a Leonardo running application firmware.
   - Unclear: whether a touch-then-probe sequence leaves the board able to answer `hw` in the same
     invocation, and whether the fix is a new `--probe-json`/`--skip-hw` seam on the tool (a rig
     change, `P-H1`-class, legitimately fixed in-phase) or purely a step ordering.
   - Recommendation: run it as a second pre-proof alongside D-10's, on the Leonardo, before A1. It is
     ~5 minutes and it de-risks the milestone's most expensive cell.

2. **Does Amendment 3's per-position path change belong in Amendment 3 or a separate Amendment 4?**
   - Recommendation: **Amendment 3**. D-06's own argument — "the cleanest possible window: no real
     sweep cell has run yet" — applies identically, and two amendments landing the same hour with the
     same clause (c) is noise.

3. **`fw_readback_judged_span_bytes` and per-arm `READBACK-VERDICT.json` retention.**
   - Known: `judge_readback.py --out-dir $CELL_DIR` writes six artifacts at the cell root, and
     `capture_provenance.read_readback_verdict()` hardcodes `cells/<slug>/READBACK-VERDICT.json`
     [VERIFIED: `capture_provenance.py:311`]. The v133 flash at `P-10`/`P-04` **overwrites** all six,
     including the control arm's `flash_readback.bin` — which `artifact_volume_policy` calls
     "not reproducible from any record" and commits.
   - The SHAs survive (they are already in the control positions' provenance), so no *field* is lost;
     the *binaries* are.
   - Recommendation: after each arm's second position completes, copy the six artifacts to
     `$CELL_DIR/readback_<arm>/` before the arm switch. Keep the cell-root copy where
     `capture_provenance.py` expects it. Cheap, and it preserves a committed artifact class.

4. **Whether A2's W29C020 positions can be attempted safely after a W27C512 brownout.**
   - D-07 says yes and nothing on the record contradicts it; Claude's Discretion already carves out
     "stop and report" if the brownout leaves a rail unsafe for a 32-pin part. No further research
     can settle this — it is an operator judgement at A2's `P-08`.

---

## Sources

### Primary (HIGH confidence — read or executed in this session)

- `.planning/v1.34/PROCEDURE.md` (529 lines, full read) — step list, 9 standing rules, halt policy,
  outcome taxonomy, write-duration definition, forbidden invocations, Amendments 1-2
- `.planning/v1.34/rig-pins.json` (177 lines, full read) — every per-target and per-arm constant
- `.planning/v1.34/bench/IMAGE-PLAN.json` — 21 positions, the 12 in scope, `artifact_volume_policy`
- `.planning/v1.34/bench/EVIDENCE.jsonl` — the `_schema` header (40 `record_keys`) and the four
  bring-up rows, incl. `BRINGUP-wrv` in full
- `.planning/v1.34/bench/.gitignore` + `git check-ignore -v` probes
- `.planning/v1.34/tools/run_gates.sh` (231 lines, full read) — the `--selftest` discovery contract
- `.planning/v1.34/tools/{judge_wrv,judge_readback,render_evidence,gate_record,capture_provenance,probe_board}.py`
  — targeted reads of `load_reads`, `judge_position`, `judge_span_bytes`, `cross_check_hex_span`,
  `append_row_to_file`, `check_commands`, `_allowed_argv0_set`, `_is_rig_tool_invocation`,
  `check_cross_oracle`, `probe_board_signature`, `probe_controller_string`, `read_readback_verdict`
- `--help` on all eleven rig tools (executed this session)
- `--help` on the control arm's `firestarter`, `id`, `blank`, `read`, `write`,
  `dev consistency-check`; `firestarter search w29c020` (executed this session)
- `bash .planning/v1.34/tools/run_gates.sh` → **EXIT=0**, 11/11 selftests, 5/5 live gates
- `.planning/v1.34/bench/cells/BRINGUP-wrv/` — `WRITE.md`, `WRV-VERDICT.json`,
  `READBACK-VERDICT.json`, `provenance.json`, `logs/00`…`13`
- `.planning/v1.34/bench/cells/BRINGUP-uno328pb/{,crossflash/}READBACK-VERDICT.json`
- `.planning/v1.34/bench/cells/BRINGUP-leonardo/{BOOTLOADER-WINDOW.md,probe_pretouch_attempt.json.stderr.log,probe.json}`
- `.planning/v1.34/PHASE-160-GATE.md` §6 (the 13 disclosed non-claims) and §7 (the inherited rig state)
- `.planning/v1.34/{README.md,arms-provenance.json,bench/ARM-CLI-SURFACE.md}`
- `.planning/phases/145-bench-validation/145-BENCH-LOG.md:1446-1451` — the 0.37 s spread at source
- `.planning/{REQUIREMENTS.md:43-46,ROADMAP.md,STATE.md:188-195,config.json}`
- `stat`/`sha256sum` on `~/.firestarter`; `git rev-parse HEAD` + `status --porcelain` in both sub-repos
- `grep -n` for the write/blank/id success lines in **both** arms' `eprom_operations.py`

### Secondary (MEDIUM)

- `.planning/phases/161-.../161-CONTEXT.md` — the decisions this research is bounded by
- Project memory `project_uno328pb_vpp_recal_and_program_brownout` — the 999.2 symptom, Phase 54 UAT
  2026-06-04, Rev 2.0 shield
- Project memory `reference_progress_emit_is_time_keyed_per_block`,
  `project_w27c512_write_slow_rca_per_byte_vpe_settle`, `feedback_fixture_selftests_pass_while_hardware_fails`

### Tertiary (LOW)

- None. **No web search, no Context7, no external documentation lookup was performed**: this phase
  installs nothing, imports nothing outside the stdlib, and every question it raises is answered by
  an artifact in this repository. The `research-plan` seam was not invoked because zero external
  questions were generated (`init.phase-op` confirms `brave_search`, `exa_search` and `firecrawl` are
  all `false` for this project in any case).

---

## Project Constraints (from CLAUDE.md)

`/workspaces/CLAUDE.md` is a meta-repo file. Its directives and their bearing here:

| Directive | Bearing on Phase 161 |
|---|---|
| "This repo tracks only `.planning/` and `.claude/`. Neither sub-repo is committed here." | Every artifact this phase writes lives under `.planning/v1.34/`. Confirms D-16's boundary and the "no product code" boundary. |
| "**Serial protocol changes** must be kept in sync between `serial_comm.py` and `firestarter.cpp`" | N/A — no protocol change. |
| "**Constants/flag bits** are duplicated between `constants.py` and `firestarter.h`. Change both together." | N/A — nothing is changed. |
| "**Board differences:** Uno has a 512-byte data buffer; Leonardo has 1024. Buffer size affects chunked transfer." | **Directly relevant to A2 read timing.** The W29C020 read on a Uno-class board moves 512 chunks where the Leonardo moves 256 — another reason the A1 262144 B read figure is not portable to A3/B2. |
| "EPROM database is generated; user overrides go in `~/.firestarter/database.json`" | Reinforces why `FIRESTARTER_CONFIG_DIR` must be inline: `DATABASE_FILE` is an import-time constant derived from it. |
| "`pio run -e uno` … run from `firestarter/`" | Matches Pitfall 9 and `rig-pins.json`'s `pio_project_dir`. |
| Sub-repo `CLAUDE.md`s | Not consulted — this phase edits neither sub-repo, and both must stay byte-unchanged. |

**Project skills** (`/workspaces/.claude/skills/`): `devtest-triage`, `devtest-rootcause`,
`find-skills`, `skill-creator`. The two firestarter skills are about `dev test` chip-validation
issues and product-code root-causing — **out of scope here** (Phase 161 changes no product code and
runs no `dev test`; that is Phase 162). Standing memory
`feedback_skills_must_own_their_scripts` is noted but no skill script is touched.

---

## Metadata

**Confidence breakdown:**

| Area | Level | Reason |
|---|---|---|
| Standard stack / per-cell constants | **HIGH** | Every value read from `rig-pins.json`, `IMAGE-PLAN.json` or `--help` in this session |
| Rig tool argv contract | **HIGH** | `--help` executed on all eleven tools; source read for every seam claimed |
| The six pitfalls | **HIGH** | Each traced to a specific line of source or a measured filesystem/gate observation; none is inferred |
| Amendment 3 content | **HIGH** on the four clauses' necessity; **MEDIUM** on whether clauses 3-4 belong in one amendment | The necessity is measured; the packaging is a judgement (Open Question 2) |
| `append_evidence.py` interface | **MEDIUM** | The 40-column derivation map is verified against real artifacts; the CLI shape is a proposal the planner may reshape |
| W29C020 timing | **LOW on any number, HIGH on the framing** | Deliberately: nothing has ever read 262144 B on this rig |
| A3/B2 `capture_provenance.py` viability | **LOW** | Never run on a Leonardo; the failure mode is measured, the fix is not |

**Research date:** 2026-08-27
**Valid until:** the first sweep cell runs. Every "never been measured" claim here is falsified the
moment A1 executes, and the `~/.firestarter` baseline is a live filesystem fact — re-read both before
planning if more than a few days pass.
