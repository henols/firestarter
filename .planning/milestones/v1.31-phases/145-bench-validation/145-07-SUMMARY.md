---
phase: 145-bench-validation
plan: 07
subsystem: bench-validation
tags: [gate-3, pulse-override, claim-b, cap-03, a1-overhead, w27c512, leonardo]
status: complete

requires:
  - "145-06: Gate 2 closed VALIDATED (3/3 cycles byte-exact on both oracles)"
  - "firestarter@ebe9cb3: the CTRL_VPE_ENABLE write-path fix from debug session w27c512-program-fail-byte0"
provides:
  - "D-10 Claim B: measured, HOLDS on 4/4 blocks with 24 firmware-backed intra-block positions"
  - "D-12 --pulse-us-on-silicon: exercised on a real part above the 4687 us residual-gap threshold"
  - "D-12 A1 per-pulse overhead: derived at ~1.44 ms/byte with five named error sources"
  - "D-17 no---force assertion extended over Gate 3's own 4 invocations"
affects:
  - "145-08: closes the Gate 3 verdict line and collects D-10's eyes-on half"
  - "146: carries the T-145-45 threat-register divergence and the multi-pulse A1 gap"

tech-stack:
  added: []
  patterns:
    - "Two-oracle frame validation: tqdm bar positions cross-checked byte-for-byte against decoded MSG_DATA_PROGRESS lines in the -v debug log"
    - "Controlled pulse-width comparison: same image, same blocks, same board, only the pulse differs"

key-files:
  created:
    - .planning/phases/145-bench-validation/logs/pulse4688.stdout.log
    - .planning/phases/145-bench-validation/logs/pulse4688.stderr.raw
    - .planning/phases/145-bench-validation/logs/frames_pulse4688.txt
    - .planning/phases/145-bench-validation/logs/pulse_db.stdout.log
    - .planning/phases/145-bench-validation/logs/pulse_db.stderr.raw
    - .planning/phases/145-bench-validation/logs/frames_pulse_db.txt
  modified:
    - .planning/phases/145-bench-validation/145-BENCH-LOG.md
    - .planning/phases/145-bench-validation/SHA256SUMS.txt

decisions:
  - "Companion database-pulse run taken as an ORCHESTRATOR decision under an explicit operator no-preference answer, never recorded as operator-authorized"
  - "Gate 3's operator authorization recorded as a SELECTION, not a manufactured verbatim quote"
  - "Two acceptance assertions remade after they returned false greens; substitutions recorded, evidence never reshaped"
  - "T-145-45's firmware mitigation recorded as a divergence-finding rather than applied silently"

metrics:
  duration: ~35 min
  tasks: 3
  bench-runs: 2
  bench-time: 42.81 s
---

# Phase 145 Plan 07: Gate 3 — `--pulse-us 4688` Summary

Ran the one gate the database pulse cannot reach: a 4096-byte write at 4688 µs banked **D-10 Claim B
on 4/4 blocks with an independent second oracle**, exercised `--pulse-us` on silicon above the
4687 µs residual-gap threshold where the advertised CAP-03 budget (244 s) exceeds the old 120 s
fallback, and — with a companion database-pulse run — derived **D-12's A1 at ~1.44 ms per byte**,
which is an upper bound on a *different* quantity than Phase 143 assumed.

## Operator authorization — recorded as three distinguishable shapes

**The required 4688 µs run: AUTHORIZED (2026-08-17), by SELECTION — no verbatim quote exists.** The
operator authorized by choosing a presented option labelled *"Authorize the 4688 µs run"*, not by
typing prose. **No verbatim sentence was manufactured for it.** This follows session 1's D-13
precedent (a selection, explicitly noted as such) and is deliberately kept distinct from Gate 2's
authorization, which *was* typed and stays quoted as `"you can erase or do anything its a test ic for
you"` (2026-08-16). The option stated its cost before the answer: 4096 bytes / 4 blocks, ~21 s, one
erase-and-program cycle, ~47× the database pulse energy per cell.

**The companion database-pulse run: NOT an operator authorization.** Asked separately, the operator
returned **no preference** — neither authorizing nor declining. The decision to run it was the
**orchestrator's**, taken under that explicit no-preference answer, and is recorded in those terms
throughout. The reasoning, for the record: ~2 s at the database 100 µs pulse is ordinary stress the
part has survived 15+ times this phase, not the 47× run, and A1 would otherwise be permanently
orphaned since Phase 146 cannot run a bench.

The gate was presented only after reading `## Gate 2 verdict: **VALIDATED**` directly, and
`logs/pulse4688.stderr.raw` did not exist at that moment.

## The two runs

Port re-verified fresh before each (D-19): `leonardo on port /dev/ttyACM0`, firmware `3.0.0b17` —
**not used as an identity check**; the build is identified by `firestarter@ebe9cb3` with empty
porcelain, since the version string did not move across the debug session's 96-byte change.

| Run | Command | Exit | Elapsed |
|---|---|---|---|
| 1 (required) | `firestarter -v -p /dev/ttyACM0 write W27C512 .planning/phases/145-bench-validation/images/img_4k_pulse.bin --pulse-us 4688` | **0** | **30.94 s** |
| 2 (orchestrator) | `firestarter -v -p /dev/ttyACM0 write W27C512 .planning/phases/145-bench-validation/images/img_4k_pulse.bin` | **0** | **11.87 s** |

Both reported `Write to W27C512 successful`. `grep -ciE "bad bytes|MAX_PULSES|PULSE_TOO_WIDE"`
returns **0** on both.

**The `--pulse-us` provenance line, default-visible, verbatim:**

```
W27C512: --pulse-us 4688 overrides the database program pulse for this run (100 us -> 4688 us). This run's timing is NOT the database's.
```

Run 2 emits **no** provenance line (`grep -c -- "--pulse-us"` → 0); its absence is the evidence it
used the database pulse. Wire commands corroborate both: `'pulse-delay': 4688` and `'pulse-delay': 100`.

## Extractor summary values

| | run 1 (4688 µs) | run 2 (database 100 µs) |
|---|---|---|
| `segments=` | 2 | 2 |
| `selected_segment=` | 2 | 2 |
| `frames=` | 70 | 30 |
| `intra_block_frames=` | **24** | **4** |
| `blocks_with_multiple_updates=` | **4** | **2** |
| `step_histogram=` | `40:1,164:22,204:2` | `335:1,688:1,689:1,1024:2` |

Run 1 per-block updates: block 0 → 7, block 1 → 7, block 2 → 6, block 3 → 6.
Run 2 per-block updates: block 0 → 2, block 1 → 2 (blocks 2 and 3 → 1 each).

## D-10 Claim B: **HOLDS** — and why it is not an artifact

Claim B literally: two or more distinct bar positions inside the same `n // 1024` bucket.
`blocks_with_multiple_updates=4` — **all four blocks**, six intra-block positions each, 24 total.

All three Gate 2 cycles reported `blocks_with_multiple_updates=2` and were **correctly declined** as
bar-latch transitions. This run is different, established on three grounds rather than asserted:

1. **An independent second oracle agrees exactly.** The `-v` debug log decodes each received
   `MSG_DATA_PROGRESS` as its own `DATA: n/65536` line, separately from the tqdm bar the extractor
   parses. In the MAIN phase the firmware emitted **24** frames at **byte-for-byte the same 24
   positions**. Sets identical — zero tqdm positions unbacked by a firmware frame, zero firmware
   frames without one.
2. **Blocks 2 and 3 contain no boundary row at all** — their 6 updates each are *entirely* firmware
   frames, so the bar-latch objection cannot apply to them even in principle.
3. **The step signature is a uniform cadence** (`164:22` — 22 steps of exactly 164 bytes), against
   the artifact signature in `frames_cycle1.txt` (`1023:11,1024:40,1025:11` plus two anomalies
   confined to blocks 0 and 1).

**Run 2 is the control that makes this a comparison rather than an argument** — the same image, same
four blocks, same board, only the pulse differs — and it reproduces the artifact signature exactly
(4 intra-block frames, "multiples" only in blocks 0/1 where a boundary row sits beside the single
firmware frame). Artifact and real signal were produced side by side and are visibly different.

Mechanism, not luck: `EPROM_PROGRESS_EMIT_INTERVAL_MS` is 1000 ms with `last_emit_ms` reset per
block. At ~6.10 ms/byte a block runs ~6.2 s and crosses it six times; at ~1.54 ms/byte it runs ~1.6 s
and crosses it once.

## D-12 item 1 — `--pulse-us` on silicon

Exercised on a real part: parsed, provenance line fired, **override demonstrably took effect**. The
same 4096 bytes took 30.94 s against 11.87 s. Pure pulse time alone accounts for it — 4096 × 4688 µs
= **19.20 s** vs 4096 × 100 µs = **0.41 s** (18.79 s predicted, 19.07 s observed). A run that had
silently fallen back to 100 µs could not have taken 30.94 s.

## D-12 item 2 — the above-4687 µs budget-mechanism proof

`120 s / (25 × 1024)` = **4687.5 µs**, so **4688 µs is the first integer above the threshold**.
Through the firmware's own `padded_s = ceil(raw_pulse_only_us / 1e6) × 2 + 2`:

| Pulse | Raw pulse-only | Advertised CAP-03 | vs the old 120 s fallback |
|---|---|---|---|
| 100 µs (database) | 3 s | **8 s** | far inside — discriminates nothing |
| 4687 µs | 120 s | 242 s | raw exactly *at* the fallback |
| **4688 µs (this run)** | **121 s** | **244 s** | **both exceed it** |

The run completed, so the advertised-budget mechanism carried it — the fallback could not have. That
is a claim Gate 2's cycles were structurally incapable of making at an 8 s advertised budget.

**Non-claim:** **nothing logs the advertised budget.** The host decodes CAP-03 silently and prints no
figure at any verbosity. No attempt was made to observe it and **none is quoted as measured** — 244 s
and 121 s are arithmetic from the published formula and the `0x07` row's constants. The measured fact
is exactly one: a run whose advertised budget exceeds the old fallback completed without a timeout.

## D-12 item 3 — A1: **DERIVED**, with five error sources

Model `E = F + N_pulsed × (A1 + P)`; two runs at the same pulse cancel `F`. `img_4k_pulse.bin` has
**zero `0xFF` bytes** (all 4096 pulsed); the 64 KiB images' `0xFF` counts are subtracted (img1 65408,
img2 65152, img3 65408).

| Pair | Arithmetic | µs/pulsed byte | A1 |
|---|---|---|---|
| cycle 1 − run 2 | (106.06 − 11.87) / (65408 − 4096) | 1536.24 | **1436.24 µs** |
| cycle 2 − run 2 | (105.69 − 11.87) / (65152 − 4096) | 1536.62 | **1436.62 µs** |
| cycle 3 − run 2 | (106.06 − 11.87) / (65408 − 4096) | 1536.24 | **1436.24 µs** |

**Spread 1436.24 – 1436.62 µs** (range 0.38 µs) — tightness of the inputs, *not* an accuracy claim.

**Two independent cross-checks from the frame cadence**, which use no wall-clock subtraction: the
first frame's byte offset within a block measures the per-byte loop directly, excluding INIT, erase
and setup. 4688 µs run: first frame at byte **164** → 6097.6 µs/byte → A1 ≈ **1409.6 µs**. Database
run: first frame at byte **689** → 1451.4 µs/byte → A1 ≈ **1351.4 µs**. Three methods across a 47×
pulse range land at **≈1.35–1.44 ms**, and the overhead barely moving as the pulse widens 47× is
itself the strongest support for the additive model.

**Model validation (required):** observed (30.94 − 11.87)/4096 = **4655.76 µs/byte** against the
expected 4588 µs pulse difference — **+67.76 µs, +1.48 %**, i.e. **0.278 s** of fixed-cost mismatch.
Recorded as observed; the setup line alone differs by 0.10 s between the runs and the remainder is
unattributed.

**Error sources:** (1) fixed cost does not amortise identically (~0.28 s mismatch measured);
(2) the `0xFF` skip means pulsed-byte ≠ byte count, and the skip still costs a loop iteration;
(3) per-block costs — the VPE settle and the `0x07` final full-block verify pass — ran **64×** in a
cycle and **4×** in the 4 KiB runs, the largest un-modelled term; (4) it is wall-clock host-side
arithmetic, never an instrumented per-pulse reading; (5) **it is a per-BYTE overhead at one pulse per
byte, an UPPER BOUND on A1 as Phase 143 defines it, not the same quantity** — the inner `for (;;)`
repeats only the pulse plus one verify read, while per-byte work also pays a pre-pulse check read,
the address change and its shift-register writes.

**Against Phase 143's `[ASSUMED]` ~20 to 60 µs/pulse — INDICATIVE, not conclusive.** ~1.44 ms sits
roughly **24×–72× above** it. This does **not refute** the assumption (error source 5), but the range
is **not corroborated** by anything measured here, and the only bound this bench places on A1 is a
loose upper one.

**Explicitly NOT DISCHARGED, `no v1.31 owner`:** the **per-pulse overhead inside a multi-pulse retry
loop** — the regime Phase 143's own `0x0B` worked example uses — was not measured, because no byte in
either run needed more than one pulse and `0x07` was the only protocol on the bench. Phase 146 is
docs-and-claims only and cannot run a bench.

## Deviations from Plan

### Findings recorded rather than applied silently

**1. T-145-45's firmware mitigation does not exist on this part.** The plan's threat register claims
the firmware "independently refuses over-cap pulses with `MSG_ERR_PULSE_TOO_WIDE`… 4688 is well
inside both". `eprom.cpp` guards that refusal with `energy_cap_us > 0 && …`, and `eprom_params.cpp`'s
`0x07` row ships `energy_cap_us = 0` (UNCAPPED) — the refusal is **structurally unreachable**, as the
firmware's own `CLAUDE.md` states. **Only the host's `click.IntRange(1, 65535)` bound applied.** With
`max_pulses = 25` the worst case was **~117 ms** of program energy into a single cell with no
firmware backstop. Authorized on that basis; recorded as a finding for Phase 146, not adjudicated
here.

**2. RQ-4's frames-per-block table is superseded.** It predicted **zero** intra-block frames at the
database pulse; 145-05/06 measured **64**. Its ~5-frames-per-block estimate for this run was close
(measured **6**) but the table is recorded as stale, not cited as a passing prediction.

### Acceptance assertions remade (evidence never reshaped)

**3. [Rule 3] Task 1's authorization check returned a false green.** The plan's
`grep -A3 "Gate 3" … | grep -i "authoriz" | grep -qv "NOT YET RUN"` printed *"Gate 3 authorization
recorded"* **before any authorization existed**, matching session 1's `**Operator authorization:**
NOT REACHED …`. Substituted with a check anchored to the resumed-session heading requiring both
dispositions; **the `^\*\*` line anchor is load-bearing** — the first form returned 3 because it
matched *its own definition* quoted in the record, the same self-inflicted false green 145-06 hit.

**4. [Rule 3] Task 1's Gate-2 precondition check is non-discriminating.** It matches session 1's
superseded `FAIL` block too. The precondition was confirmed by reading
`## Gate 2 verdict: **VALIDATED**` directly.

**5. [Rule 3] The plan expects `Gate 3 verdict:` to read `NOT YET RUN`.** It reads `NOT REACHED` —
session 1 rewrote it. Intent honoured: **no new verdict line was written**, asserted with
`grep -c -E '^\*\*Gate 3 verdict:'` → 1. A bare `grep -c "Gate 3 verdict:"` returns 4, three being
prose references.

All four substituted assertions were given **negative controls** and confirmed able to fail.

### State-update divergences, recorded rather than suppressed

**6. `ROADMAP.md` changed by exactly one line**, `[ ] 145-07-PLAN.md` → `[x]`, via the mandated
`roadmap.update-plan-progress`. This is in tension with the phase's zero-changed-lines criteria
elsewhere; the update was **not suppressed** and the diff was confirmed to be that single checkbox —
no whole-file reformat, no unrelated phase's `**Plans:**` line clobbered. **`REQUIREMENTS.md` is
byte-identical** and `BENCH-01` remains `[ ]` / `Pending`: `requirements.mark-complete` was
**deliberately not run** despite the plan frontmatter listing `requirements: [BENCH-01]`, because
ticking is centralised in `145-09` behind its own operator gate.

**7. Two `gsd-tools` state verbs reject the argument form the executor workflow documents.**
`state.record-metric` and `state.add-decision` were invoked positionally per
`workflows/execute-plan.md` and both returned `{"error": …required}`; they need named flags
(`--phase/--plan/--duration`, `--summary`). Re-run correctly. `add-decision` then tagged all four
entries `[Phase ?]`, repaired by hand to `[Phase 145]`.

**8. `last_activity_desc` was clobbered by the state writers** — Gate 2's full description was
replaced with the truncated, *wrong* string `145-05 complete. See`. Restored by hand with an accurate
145-07 description, and the `Plan: 8 of 9` parenthetical (still reading `145-01..145-06 complete`)
corrected in the same pass. Diffing STATE.md rather than trusting the writers is what caught both.

## Chip state and safety

This run **bulk-erased the whole chip** — the part no longer holds `img3.bin`. Cycle 3's evidence was
captured, SHA-compared and committed beforehand, so nothing was lost. **No degradation was observed**:
both runs byte-exact on the firmware's `VERIFY_PER_PULSE_PLUS_FINAL` oracle, zero `MSG_ERR_MAX_PULSES`,
zero `MSG_ERR_VERIFY`. **Gate 2's VALIDATED verdict was not touched, qualified or reopened**, and
**D-09's UNCONSUMED re-seat ledger was not reopened** — no retry was needed or performed.

**D-17 extended over Gate 3's own runs**, as 145-06 required: **4 silicon-touching invocations** (two
`fw` probes, two writes), all recorded verbatim, **zero** with `--force`, `-b`, `--no-blank-check`,
`--skip-erase`, `-a` or `-s`. Corroborated at the **wire** level: `Flags set: CanErase (0x02)` in both
writes — `FLAG_FORCE (0x01)`, `FLAG_SKIP_ERASE (0x04)`, `FLAG_SKIP_BLANK_CHECK (0x08)` all clear.
*Trap named:* the `fw` probe prints `Use --force to reinstall.` as advice text; `grep -c -- "force"`
over both write logs returns **0**.

## What this plan did NOT prove

- **No eyes-on claim.** D-10's operator-perception half is uncollected — `145-08`'s.
- **No `Gate 3 verdict:` line written** — `145-08` closes it.
- **Nothing about the database's timing** from run 1; it ran at a 46.88× override.
- **No observed CAP-03 number** — nothing logs it.
- **A1's multi-pulse regime unmeasured**; the derived figure bounds a different quantity.
- **No independent host-side SHA compare over the Gate 3 writes** — they are attested by the
  firmware's own verify pass only. This gate measured *timing and progress emission*, not data
  fidelity, and **no BENCH-01 evidence rests on it**.
- **MERGE-05's +96 B leonardo band breach** is carried, not adjudicated; no baseline re-anchored.
- **`leonardo` and `0x07` only** — the emission is compiled out on `SERIAL_ON_IO` targets; nothing
  here speaks to `0x08`, `0x0B` or Uno-class boards.
- **No requirement checkbox flipped.** `BENCH-01` remains unticked; ticking is `145-09`'s behind its
  own blocking operator gate.

## Self-Check: PASSED
