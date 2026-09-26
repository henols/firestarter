---
phase: 145-bench-validation
plan: 05
subsystem: bench-validation
tags: [w27c512, 0x07, gate-2, bench, d-06, d-10, d-11, cap-03, resumed]
requires:
  - "145-04 (Gate 1 closed: part erased, blank, identified)"
  - "debug session w27c512-program-fail-byte0 (firmware fix eb563d2 + ebe9cb3)"
provides:
  - "Gate 2 cycle 1 of 3: byte-exact 64 KiB write on all three oracles"
  - "D-10 Claim A measured verdict: HOLDS (64 intra-block frames)"
  - "D-11 CAP-03 advertised-budget free evidence, with its non-claim stated"
  - "143 H4's long-write half discharged"
affects:
  - "145-06 (cycles 2 and 3, then the Gate 2 verdict)"
  - "145-07 (Gate 3, Claim B, D-12) -- RQ-4's frames-per-block table is now stale"
  - "146 (docs/claims) -- three carry-forwards no longer ownerless"
tech-stack:
  added: []
  patterns:
    - "Three separately-recorded oracles; the firmware-side pair never merged with the host-side compare"
    - "Firmware image identified by commit + avrdude byte count, never by version string (D-18)"
    - "Visible supersession of a stale record rather than in-place rewriting"
key-files:
  created:
    - .planning/phases/145-bench-validation/readbacks/readback1.bin
    - .planning/phases/145-bench-validation/runs/cycle1/run_01.bin
    - .planning/phases/145-bench-validation/runs/cycle1/run_02.bin
    - .planning/phases/145-bench-validation/runs/cycle1/run_03.bin
    - .planning/phases/145-bench-validation/logs/write_cycle1.stdout.log
    - .planning/phases/145-bench-validation/logs/write_cycle1.stderr.raw
    - .planning/phases/145-bench-validation/logs/verify_cycle1.log
    - .planning/phases/145-bench-validation/logs/read_cycle1.log
    - .planning/phases/145-bench-validation/logs/consistency_cycle1.log
    - .planning/phases/145-bench-validation/logs/frames_cycle1.txt
  modified:
    - .planning/phases/145-bench-validation/145-BENCH-LOG.md
    - .planning/phases/145-bench-validation/SHA256SUMS.txt
decisions:
  - "Session 1's failure record and HALTED verdict are preserved verbatim; supersession is by visible pointer, never by rewrite"
  - "D-09's single re-seat allowance is adjudicated UNCONSUMED -- the prior failure had a firmware cause and no chip was touched"
  - "The MERGE-05 +96 B band breach is recorded as carried, NOT adjudicated -- no baseline re-anchored, no band widened"
  - "Claim A HOLDS; RQ-4's zero-frame prediction was falsified by the settle increase, not by an error in its mechanism"
  - "blocks_with_multiple_updates=2 is recorded but explicitly NOT banked as Claim B -- the pairs are latch-transition artifacts"
metrics:
  duration: "~35 min"
  completed: 2026-08-17
status: complete
---

# Phase 145 Plan 05: Gate 2 Cycle 1 Summary

Gate 2's first of three authorized 64 KiB cycles passed byte-exact on all three oracles after the
phase resumed on a corrected firmware build, and D-10 Claim A measured **HOLDS** — the opposite of
RQ-4's prediction, for a reason that is itself a measurement.

## Context: this plan was RESUMED after a HALT

Session 1 (2026-08-16) halted here: `write W27C512 img1.bin` exited 1 with `Byte at 0x000000 failed
to program within 25 pulses`. Debug session `.planning/debug/w27c512-program-fail-byte0.md` found
the cause in **firmware** — v1.31 Phase 141 deleted `program_mismatched_bytes()`, the only place the
EPROM write path asserted `CTRL_VPE_ENABLE`, so every program pulse since went out with the 12 V
rail generated but never routed onto the socket. Fixed in `firestarter` `eb563d2` + `ebe9cb3`.

This vindicated session 1's refusal to spend D-09's re-seat allowance: the operator inspected the
bench and found no physical cause because there was none.

## Operator authorization — verbatim, already given, not re-sought

> **"you can erase or do anything its a test ic for you"** — operator, 2026-08-16

Recorded verbatim in `145-BENCH-LOG.md` under Gate 2. It authorizes this exact three-cycle spend and
also discharged `145-04`'s standalone-expendability carry-forward. Task 1's gate was therefore
already closed when this plan resumed, and **no operator gate was self-approved in this session** —
this executor had no `AskUserQuestion` capability and would have handed back rather than answered.
The plan's pre-gate acceptance criterion still held on resume: `logs/write_cycle1.stderr.raw` did
not exist at the moment work began (session 1's evidence lives under the `write_cycle1_attempt1.*`
names) and was asserted absent immediately before the write.

**Wear disclosure added to the record:** the debug session ran 13 further full 64 KiB cycles on this
same part under its own operator authorization. Those are outside Gate 2's three-cycle budget and
are named in the bench log so nobody reads this part as having seen only three program cycles.

## Firmware image under test — SUPERSEDES Gate 1

`145-04-SUMMARY.md` said no reflash was needed "unless the tree changes". The tree changed, so the
board was reflashed from `/workspaces/firestarter` at the clean tip with `pio run -t upload -e
leonardo` (never `fw --install`, which resolves a GitHub release asset the v1.31 branch does not
have and would flash `beta`).

| Row | Gate 1 (session 1) | **This session** |
|---|---|---|
| Firmware commit | `a594173d…` | **`ebe9cb353f134d6c56a8295490142de1a43fdf8f`** |
| Flash / data bytes | 26906 / 2014 | **27002 / 2014** |
| Flash headroom | 93.8 %, 1766 B free | **94.2 %, 1670 B free** |
| avrdude verified | 26906 | **27002** (`avrdude: 27002 bytes of flash written` / `… verified`) |
| Version string | `3.0.0b17` | **`3.0.0b17` — unchanged, and therefore useless as a discriminator** |

`git -C /workspaces/firestarter status --porcelain` was empty before the build, after the upload,
and after every task. The upload log was captured whole and read in full, not grepped with a
hard-coded pattern; avrdude was `tool-avrdude @ 1.60300.200527 (6.3.0)`.

**Gate 1's "0 B delta" line is corrected, not carried.** This build is **+96 B** against the 0 B
leonardo must-not-grow band, and session 1's reason clause — "a phase that compiles nothing new
cannot move flash" — no longer applies: a debug session compiled it.

## Port identity, re-verified this plan (D-19)

`firestarter -p /dev/ttyACM0 fw` run twice, once before and once after the reflash, both reporting
`Current firmware version: 3.0.0b17, for controller: leonardo on port /dev/ttyACM0`. Exactly one
`/dev/ttyACM*` device present throughout. `firestarter -p /dev/ttyACM0 id W27C512` → exit 0,
`Chip ID check passed for W27C512`.

## The four cycle-1 command lines and their exit statuses

| # | Command | Exit |
|---|---|---|
| 1 | `firestarter -v -p /dev/ttyACM0 write W27C512 .planning/phases/145-bench-validation/images/img1.bin` | **0** |
| 2 | `firestarter -p /dev/ttyACM0 verify W27C512 .planning/phases/145-bench-validation/images/img1.bin` | **0** |
| 3 | `firestarter -p /dev/ttyACM0 read W27C512 .planning/phases/145-bench-validation/readbacks/readback1.bin` | **0** |
| 4 | `firestarter -p /dev/ttyACM0 dev consistency-check W27C512 --runs 3 --output-dir .planning/phases/145-bench-validation/runs/cycle1` | **0** (three-way: 0 PASS / 1 FAIL divergent SHAs / 2 hardware or serial error) |

`-v` and `-p` precede the subcommand in every case (group options).

## The three oracle verdicts — separate lines, never merged

**Oracle 1a — write's own verdict (firmware-side, first pass):**
`INFO   :EpromOperator:1982: Write to W27C512 successful (106.06s).` — exit 0,
`grep -ci "bad bytes"` → **0**.

**Oracle 1b — verify's own verdict (firmware-side, SECOND pass):**
`Verify for W27C512 successful (5.68s).` — exit 0.

**D-06 independence boundary:** `verify` uses the **same `_main_phase_send_data` handler as
`write`** and the **firmware** performs the compare, so 1b is a second firmware-side pass, not an
independent oracle. The genuinely independent oracle is oracle 2.

**Oracle 2 — independent host-side SHA compare:** `readback1.bin` is exactly 65536 bytes; `cmp`
against `img1.bin` reports no difference; both digests are
`f72489604bfe917db7ee505e4d674576b2905a418e8dc55372b78dcab3e34e3a`. **65536/65536 byte-exact.**
`sha256sum -c SHA256SUMS.txt` exits 0 over all six rows.

**Measured elapsed, as a first-class figure:** **106.06 s** for the 64 KiB write. No v1.31 figure
existed before this run; the only prior recorded figure is a 22.84 s pre-v1.31 run. **58.9 s of the
difference is the shipped `EPROM_VPP_SETUP_US` 100 → 1000 µs settle increase** (65408 pulsed bytes ×
900 µs), which the debug session independently cross-checked as settle rather than extra pulses.

## Read stability for this cycle (D-07)

```
Consistency check: PASS
Chip: W27C512  Board: unknown-board  Port: /dev/ttyACM0
Runs: N=3
Distinct SHAs: 1
Output dir: .planning/phases/145-bench-validation/runs/cycle1/
```
`run_01.bin`, `run_02.bin`, `run_03.bin` each exactly 65536 bytes; `git check-ignore` reports
`runs/cycle1` **not ignored**, so the evidence commits. All three runs reported the **same digest as
the source image**, which is three further confirmations of oracle 2 beyond the one required.

## D-10 Claim A — measured, and the prediction was falsified

Extractor self-test re-run this session: `SELFTEST: POSITIVE PASS`, `SELFTEST: NEGATIVE PASS`,
exit 0 — which matters more than usual here, because this session's result is a positive one.

The six summary values, verbatim from `logs/frames_cycle1.txt`:
```
segments=2
selected_segment=2
frames=267
intra_block_frames=64
blocks_with_multiple_updates=2
step_histogram=336:1,688:2,1023:11,1024:40,1025:11
```

**Claim A** (*at least one bar frame reported a position that is not a multiple of 1024*):
**HOLDS.** 64 intra-block positions, one per block, at a constant ≈688-byte offset — `688, 1712,
2736, 3760, 4785, … 65200`. Only a firmware `MSG_DATA_PROGRESS` (`0xE0`) frame can produce a
non-multiple-of-1024 position, since every host chunk hand-off lands exactly on a 1024 boundary for
a 65536-byte file on a 1024-byte-buffer board.

**Corroborated independently of the extractor:** the `-v` stdout capture carries 96 `DATA: n/65536`
lines — the first 32 stepping by 2048 (the INIT blank check at `BLANK_CHECK_CHUNK_SIZE = 2048`) and
the remaining 64 being the MAIN-phase write at the same `688, 1712, 2736, …` positions. Two
different artifacts, two different mechanisms, same 64 positions. `segments=2`,
`selected_segment=2` confirms the 32 INIT frames were discarded, so no 2048-step blank-check frame
was miscounted as write motion (Pitfall 6 / T-145-28).

**Why RQ-4 predicted zero and measured 64.** RQ-4's mechanism was right and its input was stale.
Emission is time-keyed at `EPROM_PROGRESS_EMIT_INTERVAL_MS` = 1000 ms with `last_emit_ms` a
function-local re-initialised at the top of every block, and RQ-4 estimated a 400–700 ms block —
under the cadence, so no frame could fire. The debug session's settle increase pushed measured block
time to **106.06 / 64 = 1.657 s**, crossing the cadence: `floor(1657/1000) = 1` frame per block,
which is exactly the 64 measured. The predicted within-block offset `1024 × 1000/1657 ≈ 618` bytes
lands close to the observed ≈688. **The prediction was falsified by a firmware change made outside
this phase for an unrelated reason, and by the very mechanism RQ-4 named** — the 1000 ms cadence and
per-block reset are what make it *one* frame per block rather than several.

**Standing correction for downstream work:** RQ-4's frames-per-block table row `100 µs (DB) → 0
frames` is **stale for the shipped firmware**; the true figure on `ebe9cb3` is **1 frame per block**.

**`blocks_with_multiple_updates=2` is recorded but NOT banked as Claim B.** The two pairs are block 0
(`0`, `688`) and block 1 (`1024`, `1712`) — in each, the lower position is a host-side draw (tqdm's
initial render; a chunk hand-off boundary) and the upper is the firmware frame. They are
**latch-transition artifacts**, not two firmware emissions inside one block. Read with maximum
literalism Claim B's wording is satisfied for two blocks; this record declines to claim it on that
basis. Claim B and verification-map row 24 remain `145-07` Task 2's on the Gate 3 `--pulse-us 4688`
run.

**Emission constraint:** guarded by `#ifndef SERIAL_ON_IO` (`eprom.cpp:398,403`) — `leonardo`-only
(plus `native`), **compiled out on `SERIAL_ON_IO` targets** (`uno`, `uno328pb`). This measurement is
structurally unavailable on Uno-class hardware and nothing here generalises to it.

## D-11 — CAP-03 advertised-budget free evidence

The write completed, so the advertised-budget path held on real hardware. Measured **106.06 s**,
**1.657 s per block**, against an **8 s** computed per-block advertised budget for W27C512 at 100 µs
on a 1024-byte block, and the **120 s** legacy fallback it replaces.

**The non-claim, stated:** nothing logs the advertised budget — the host decodes it silently from
the `MSG_OK_READY` capability blob. The `-v` capture was read for one and there is none. The
evidence is the **completion itself**; no attempt was made to observe the number in the logs
(Pitfall 9). The 8 s figure is computed and cited, not measured.

**Honest qualifier on sharpness:** 1.657 s per block fits inside *both* the 8 s advertised budget and
the 120 s fallback, so this run does not discriminate between them — it would have completed even if
the advertised budget had never been implemented. The discriminating case is a budget exceeding
120 s, which is Gate 3's `--pulse-us 4688` (244 s advertised), owned by `145-07`.

**143 H4's long-write half: DISCHARGED** by this run with that qualifier attached. Phase 146 no
longer carries it as unproven. H4's `--pulse-us`-above-4687 µs half remains open.

## Prohibitions — explicit statement

**No `--force` was used anywhere. No `write -b`, no `--no-blank-check`, no `--skip-erase`. No
`-a`/`--address` and no `-s`/`--size`** — the write covered the full 65536 bytes, all 64 blocks
(D-04). Every command line is quoted verbatim in the bench log as its own heading or fenced block so
the flags are auditable without trusting prose (D-17). `--force used? No` is recorded for this cycle.

## Deviations from Plan

### Auto-fixed / adjudicated

**1. [Rule 3 — Blocking] Reflash inserted before Task 2.** The plan predates the firmware fix and
assumes `145-04`'s image is still on the board. Running cycle 1 against `a594173d` would have
reproduced the halt. Reflashed at `ebe9cb3`; recorded as a visible supersession of four Gate 1 rows
rather than an in-place edit. Bench log: "Firmware-image supersession". Commit `817de578`.

**2. [Rule 2 — Record correctness] Gate 1's "0 B delta" line corrected.** It is false for this
build (+96 B) and its reason clause no longer applies. Stated as a correction, not carried forward.
Commit `817de578`.

**3. [Record honesty] D-16 restated.** No plan edited a source file, so D-16 holds on its own terms —
but the firmware checkout changed mid-phase via a debug session. Recorded plainly so D-16 cannot read
as "the firmware was untouched throughout".

**4. [Record honesty] MERGE-05 breach carried, not adjudicated.** The build is +96 B against a 0 B
leonardo band, `test_policy_merge05_fires_on_the_current_tree` records it live, BASE-01 was
deliberately not re-anchored. **Nothing in this plan re-anchored a baseline, widened a band or
touched a gate.** Recorded so no reader discovers elsewhere that these measurements came from a build
with an open breach.

**5. [Record honesty] D-09 adjudicated explicitly, not assumed.** Prior failure had a firmware cause;
no chip was touched; **the allowance is UNCONSUMED and still available**. This run is cycle 1 on a
different build, not "Attempt 2" under D-09's ledger. Session 1's failure is **not** discarded.

**6. `SHA256SUMS.txt` — one row appended, not two.** The plan says append both digests; `img1.bin`'s
row already existed from `145-01` and is unchanged. Appending a duplicate would have made the
manifest ambiguous for no gain. The acceptance criterion (lines for both, identical digests,
`sha256sum -c` exit 0) is satisfied.

**7. `REQUIREMENTS.md` untouched; BENCH-01 NOT ticked**, despite this plan's frontmatter naming it.
Phase 145 centralises requirement ticking in `145-09` behind a blocking operator gate — the ROADMAP
states "`145-01` … `145-08` tick **none**". BENCH-01 is multi-plan and Gate 2 needs 3/3 cycles; one
passing cycle cannot complete it.

**8. Claim A HOLDS where the brief predicted a null.** Not a deviation in method — the extractor was
run **once**, over the **first and only** write of this session, and nothing was re-run to obtain a
better number. Reported as measured, with the reason the prediction failed.

### Not deviations, but worth naming

Cycle 1's `write` was run **once**. There was no retry, no second attempt, and no source edit to make
any result appear.

## What this plan did NOT prove

- **Gate 2 is not closed.** One of three cycles. The 3/3 rule and the erase-actually-fired
  corroboration (which needs cycle 2's 99.8 % `0→1` transitions) are `145-06`'s.
- **Claim B is not claimed**, despite two blocks literally satisfying its wording.
- **The advertised budget was not observed** — only the completion was, and the run does not
  discriminate the 8 s budget from the 120 s fallback.
- **Nothing about `0x08` or `0x0B`** — those remain skipped-with-reason, and the debug session's fix
  to those protocols is proven only in the golden trace, never on a part.
- **Nothing about Uno-class boards** — the progress emission is compiled out there.
- **The intermittent single-byte margin failure is mitigated, not explained.** It did not recur in
  this cycle, which is one more clean cycle on top of the debug session's 12 — not an explanation.
- **Program-window VPP under load is still not measured** (the standing Phase-97 DTR-reset tooling
  gap). It remains in the bench log's "Not measured" table.

## Self-Check: PASSED

All created files verified present at expected sizes (`readback1.bin` 65536 B; `run_01..03.bin`
65536 B each; all six logs present). Commits verified in `git log`: `817de578`, `e087dcf7`.
`git -C /workspaces/firestarter status --porcelain` empty. `sha256sum -c SHA256SUMS.txt` exit 0.
Session 1's preserved failure evidence (`write_cycle1_attempt1.stdout.log` 4165 B,
`.stderr.raw` 5315 B) intact and unmodified.
