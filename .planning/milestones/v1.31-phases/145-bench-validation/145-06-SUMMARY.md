---
phase: 145-bench-validation
plan: 06
subsystem: bench-validation
tags: [w27c512, 0x07, gate-2, bench, d-03, d-05, d-06, d-07, d-09, d-14, d-17]
requires:
  - "145-05 (Gate 2 cycle 1 PASS on firmware ebe9cb3)"
provides:
  - "Gate 2 cycles 2 and 3: byte-exact 64 KiB writes on all three oracles"
  - "Gate 2 CLOSED: VALIDATED, 3/3 byte-exact on both oracles"
  - "D-09 re-seat ledger closed as UNCONSUMED with a four-row auditable history"
  - "D-17 no-force source assertion over a counted denominator of 17 invocations"
  - "D-03 erase-fired corroboration re-derived on the actual image bytes"
  - "Three v1.31 write-timing figures for a 64 KiB W27C512 on Leonardo"
affects:
  - "145-07 (Gate 3, Claim B, D-12) -- must extend the no-force assertion over its own runs"
  - "145-09 (requirement ticking; BENCH-01 still not flipped)"
  - "146 (docs/claims)"
tech-stack:
  added: []
  patterns:
    - "Three separately-recorded oracles; the firmware-side pair never merged with the host-side compare"
    - "Consecutive read-backs asserted to differ, with cmp exit 1 distinguished from exit 2"
    - "Source assertions made over a counted denominator, with the counting grep protected from matching its own evidence"
key-files:
  created:
    - .planning/phases/145-bench-validation/readbacks/readback2.bin
    - .planning/phases/145-bench-validation/readbacks/readback3.bin
    - .planning/phases/145-bench-validation/runs/cycle2/run_01.bin
    - .planning/phases/145-bench-validation/runs/cycle2/run_02.bin
    - .planning/phases/145-bench-validation/runs/cycle2/run_03.bin
    - .planning/phases/145-bench-validation/runs/cycle3/run_01.bin
    - .planning/phases/145-bench-validation/runs/cycle3/run_02.bin
    - .planning/phases/145-bench-validation/runs/cycle3/run_03.bin
    - .planning/phases/145-bench-validation/logs/write_cycle2.stdout.log
    - .planning/phases/145-bench-validation/logs/write_cycle2.stderr.raw
    - .planning/phases/145-bench-validation/logs/write_cycle3.stdout.log
    - .planning/phases/145-bench-validation/logs/write_cycle3.stderr.raw
    - .planning/phases/145-bench-validation/logs/verify_cycle2.log
    - .planning/phases/145-bench-validation/logs/verify_cycle3.log
    - .planning/phases/145-bench-validation/logs/read_cycle2.log
    - .planning/phases/145-bench-validation/logs/read_cycle3.log
    - .planning/phases/145-bench-validation/logs/consistency_cycle2.log
    - .planning/phases/145-bench-validation/logs/consistency_cycle3.log
    - .planning/phases/145-bench-validation/logs/frames_cycle2.txt
    - .planning/phases/145-bench-validation/logs/frames_cycle3.txt
  modified:
    - .planning/phases/145-bench-validation/145-BENCH-LOG.md
    - .planning/phases/145-bench-validation/SHA256SUMS.txt
decisions:
  - "Gate 2 verdict is VALIDATED -- 3/3 byte-exact on both oracles, nine clean cells"
  - "D-09's single re-seat allowance closes UNCONSUMED; each of the three cycles was written exactly once"
  - "The plan's own ^### acceptance grep is broken (returns 0 regardless of compliance); corrected to ^#{2,6} and the substitution recorded rather than hidden"
  - "The no-force claim is scoped to Gates 0-2 only; Gate 3 has not run and is not covered"
  - "MERGE-05's +96 B breach is carried, still NOT adjudicated -- Gate 2 passed on a build with an open breach"
  - "Claim B still not banked despite blocks_with_multiple_updates=2 in all three cycles"
metrics:
  duration: "~30 min"
  completed: 2026-08-17
status: complete
---

# Phase 145 Plan 06: Gate 2 Cycles 2-3 and Gate 2 Closure Summary

Gate 2 closes **VALIDATED** — three full 64 KiB cycles on three distinct images, nine clean oracle
cells, per-cycle read stability PASS, and D-09's re-seat allowance unconsumed at the end.

## Firmware image and port identity

**No reflash was performed or needed in this plan.** `/workspaces/firestarter` was asserted still at
`ebe9cb353f134d6c56a8295490142de1a43fdf8f` with **empty** `git status --porcelain` before Task 1 and
again before Task 2, so `145-05`'s avrdude-verified **27002**-byte image is unchanged.

**Port re-verified per task (D-19), never carried forward.** In both Task 1 and Task 2:

```
$ ls /dev/ttyACM*     → exactly one device, /dev/ttyACM0
$ firestarter -p /dev/ttyACM0 fw     → exit 0
Current firmware version: 3.0.0b17, for controller: leonardo on port /dev/ttyACM0
$ firestarter -p /dev/ttyACM0 id W27C512     → exit 0
Chip ID check passed for W27C512: (main done) (0.28s)
```

**The version string is useless as an identity check** — `3.0.0b17` did not move across a 96-byte
firmware change (D-18's caveat, proven by `145-05`). The image is identified by commit and byte
count only.

## The eight command lines and their exit statuses

| # | Task | Command | Exit |
|---|---|---|---|
| 1 | 1 | `firestarter -v -p /dev/ttyACM0 write W27C512 .planning/phases/145-bench-validation/images/img2.bin` | **0** |
| 2 | 1 | `firestarter -p /dev/ttyACM0 verify W27C512 .planning/phases/145-bench-validation/images/img2.bin` | **0** |
| 3 | 1 | `firestarter -p /dev/ttyACM0 read W27C512 .planning/phases/145-bench-validation/readbacks/readback2.bin` | **0** |
| 4 | 1 | `firestarter -p /dev/ttyACM0 dev consistency-check W27C512 --runs 3 --output-dir .planning/phases/145-bench-validation/runs/cycle2` | **0** (three-way: 0 PASS / 1 divergent SHAs / 2 hardware-or-serial error) |
| 5 | 2 | `firestarter -v -p /dev/ttyACM0 write W27C512 .planning/phases/145-bench-validation/images/img3.bin` | **0** |
| 6 | 2 | `firestarter -p /dev/ttyACM0 verify W27C512 .planning/phases/145-bench-validation/images/img3.bin` | **0** |
| 7 | 2 | `firestarter -p /dev/ttyACM0 read W27C512 .planning/phases/145-bench-validation/readbacks/readback3.bin` | **0** |
| 8 | 2 | `firestarter -p /dev/ttyACM0 dev consistency-check W27C512 --runs 3 --output-dir .planning/phases/145-bench-validation/runs/cycle3` | **0** |

`-v` and `-p` precede the subcommand in every case (group options). Full 64 KiB each cycle.

## The six oracle verdicts — separate lines, never merged (D-06)

### Cycle 2 (`img2.bin`)

**Oracle 1a — write's own verdict (firmware-side, first pass):**
`INFO   :EpromOperator:1982: Write to W27C512 successful (105.69s).` — exit 0,
`grep -ciE "bad bytes|MAX_PULSES"` → **0**. Wall clock 109 s.

**Oracle 1b — verify's own verdict (firmware-side, SECOND pass):**
`Verify for W27C512 successful (5.69s).` — exit 0. **Not an independent oracle** — `verify` shares
`write`'s `_main_phase_send_data` handler and the firmware performs the compare.

**Oracle 2 — independent host-side SHA compare:** `Read complete (7.40s)`, `readback2.bin` exactly
65536 bytes, `cmp` reports no difference, both digests
`b566c7a0319cc37051ec9c92bc1faef81f75e3740c7c6c8864778a549624fd96`. **65536/65536 byte-exact.**

### Cycle 3 (`img3.bin`)

**Oracle 1a:** `INFO   :EpromOperator:1982: Write to W27C512 successful (106.06s).` — exit 0,
`grep -ciE "bad bytes|MAX_PULSES"` → **0**. Wall clock 110 s.

**Oracle 1b:** `Verify for W27C512 successful (5.69s).` — exit 0. Again a second firmware-side pass.

**Oracle 2:** `Read complete (7.40s)`, `readback3.bin` exactly 65536 bytes, `cmp` no difference, both
digests `74c359c8d8668fdc5778270d61cc3fbef55a1027999f20c5798a54bf0f6aea01`. **65536/65536 byte-exact.**

`sha256sum -c SHA256SUMS.txt` exits **0** over all eight rows. `img2.bin`/`img3.bin` rows already
existed from `145-01` and are unchanged; only the two read-back rows were appended (same handling as
cycle 1 — no duplicate rows).

## Consecutive read-backs asserted to DIFFER — the no-op-erase guard

```
cmp -s readbacks/readback1.bin readbacks/readback2.bin → rc=1 (differ);  cmp -l | wc -l → 65536
cmp -s readbacks/readback2.bin readbacks/readback3.bin → rc=1 (differ);  cmp -l | wc -l → 65536
```

**All 65536 bytes changed both times.** Both files were `stat`-confirmed present at 65536 bytes
before each compare, so `cmp`'s exit **1** (*differ*) cannot be a disguised exit **2** (*error*).
That precaution is not theoretical — see the deviation below.

## D-03 erase-fired corroboration — re-derived, not quoted

Rather than cite RQ-2's figures, the transition densities were **recomputed on the actual image bytes
on disk** with a per-byte `(~prev & next)` population count:

| Transition | Bytes needing ≥1 `0`→`1` | Share |
|---|---|---|
| `img1.bin` → `img2.bin` | **65408 / 65536** | **99.8 %** |
| `img2.bin` → `img3.bin` | **59392 / 65536** | **90.6 %** |

Both match the planned figures exactly. A silently no-op erase would leave those bytes unable to
reach their targets and the write would fail with `MSG_ERR_MAX_PULSES`; both writes exited 0 with 0
bad bytes and byte-exact independent read-backs. **Stated plainly in the record as a derived
corroboration of the D-03 pre-flight, not a second independent measurement** — it reasons from the
image sequence and the observed pass; it does not observe the erase itself.

## Read stability, measured per cycle (D-07) — both verdict blocks verbatim

**Cycle 2** (`logs/consistency_cycle2.log`, exit 0):
```
Consistency check: PASS
Chip: W27C512  Board: unknown-board  Port: /dev/ttyACM0
Runs: N=3
Distinct SHAs: 1
Output dir: .planning/phases/145-bench-validation/runs/cycle2/
```

**Cycle 3** (`logs/consistency_cycle3.log`, exit 0):
```
Consistency check: PASS
Chip: W27C512  Board: unknown-board  Port: /dev/ttyACM0
Runs: N=3
Distinct SHAs: 1
Output dir: .planning/phases/145-bench-validation/runs/cycle3/
```

Six `run_NN.bin` files, all exactly 65536 bytes, both directories **not gitignored**. Each cycle
measured in its **own** output directory — nothing inferred from cycle 1 (D-07). In both cycles all
three runs reported the **same digest as the source image**, a free extra confirmation of oracle 2.

## Frame summary values (D-10 Claim A)

Extractor self-test re-run before each measurement: `SELFTEST: POSITIVE PASS`,
`SELFTEST: NEGATIVE PASS`.

**Cycle 2** (`logs/frames_cycle2.txt`):
```
segments=2
selected_segment=2
frames=267
intra_block_frames=64
blocks_with_multiple_updates=2
step_histogram=204:1,692:1,820:1,1023:18,1024:27,1025:17
```

**Cycle 3** (`logs/frames_cycle3.txt`):
```
segments=2
selected_segment=2
frames=267
intra_block_frames=64
blocks_with_multiple_updates=2
step_histogram=336:1,688:1,689:1,896:1,1023:11,1024:38,1025:11,1151:1
```

**Claim A HOLDS in both cycles as measured** — 64 intra-block frames each, corroborated independently
by 96 `DATA:` lines in each `-v` stdout capture. `145-05`'s standing correction is carried: **RQ-4's
frames-per-block table row `100 µs (DB) → 0 frames` is stale** for the shipped firmware, falsified by
the settle increase pushing block time past the 1000 ms emission cadence, not by an arithmetic error.
No predicted count was asserted anywhere.

**`blocks_with_multiple_updates=2` is NOT banked as Claim B** in either cycle, for `145-05`'s reason
(bar-latch-transition artifacts — a host draw plus the firmware frame — not two firmware emissions in
one block). Claim B remains `145-07`'s.

## v1.31 timing — three figures, no comparative claim (D-08)

| Cycle | Image | Measured write elapsed |
|---|---|---|
| 1 | `img1.bin` | 106.06 s |
| 2 | `img2.bin` | 105.69 s |
| 3 | `img3.bin` | 106.06 s |

Spread **0.37 s** across three full 64 KiB writes. **No comparative claim against any earlier
firmware** — D-08 rejected a control run and this milestone claims fidelity, not improvement. The
22.84 s pre-v1.31 figure in the record is a historical number, **not a control measurement**: not
taken on this part, in this session, under these conditions. No datasheet-conformance claim either
way.

## Re-seat ledger state

**UNCONSUMED.** No re-seat was required at any point in Gate 2, none occurred, and D-09's single
allowance was never spent. Each of the three counted cycles was written **exactly once** — no retry,
silent or documented. Session 1's pre-halt failure is **not** discarded and is **not** one of Gate
2's three cycles; it stands as a genuine failure whose cause was proven to be a firmware defect, which
is precisely why the allowance was never owed.

## No-`--force` source assertion — the counted denominator

**17 recorded silicon-touching `firestarter` invocations across Gates 0, 1 and 2** — **4** as their
own `####`-depth command-line subsection heading, **13** as `$ firestarter …` lines in fenced blocks.

```
grep -E "^#{2,6} .*firestarter " 145-BENCH-LOG.md | wc -l                                       → 4
grep -E "^#{2,6} .*firestarter " ... | grep -cE -- "--force|--skip-erase|--no-blank-check"      → 0
grep -E "^#{2,6} .*firestarter .*write " ... | grep -cE -- " -b| -a | -s "                      → 0
grep -cE "^\$ firestarter " 145-BENCH-LOG.md                                                    → 13
grep -E "^\$ firestarter " ... | grep -cE -- "--force|--skip-erase|--no-blank-check"            → 0
```

**None of the 17 contains `--force`, `--skip-erase` or `--no-blank-check`; no `write` carries `-b`,
`-a` or `-s`.** Every `--force` string in the log was inspected individually — all are negations or
declarations, never an executed command. The two `-b` uses are `erase -b` (blank-check-after, the
**opposite polarity** to `write -b`, which sets `FLAG_SKIP_ERASE`) and `blank`; both legitimate, both
named in the record so the zero-count is not sleight of hand.

Mechanisms named: **`eprom_check_vpp` hard-aborts above `vpp_mv + 500` = 12500 mV** for this part and
`--force` converts that abort into a warning; **the chip-id check likewise aborts without `--force`**,
which is what caught the v1.18 Phase-97 wrong-part mix-up.

**Scope limit:** covers Gates 0–2 only. **Gate 3 has not been run**; `145-07` must extend the
assertion over its own runs.

## Gate 2 verdict — verbatim from the record

> **Gate 2 verdict:** Three full 64 KiB cycles were written on three distinct images (`img1.bin`,
> `img2.bin`, `img3.bin`), all **3/3 byte-exact on both oracles** — the firmware-side write/verify
> pair and the independent host-side SHA compare, nine clean cells in total; per-cycle read stability
> **PASS at N=3 with 1 distinct SHA** in all three cycles; **no `--force`** in any of the 17 recorded
> invocations; **D-09's single re-seat allowance UNCONSUMED**, no re-seat performed and each cycle
> written exactly once; and **the erase demonstrably fired**, corroborated by the transition densities
> (**65408/65536, 99.8 %** of cycle-1→2 bytes and **59392/65536, 90.6 %** of cycle-2→3 bytes require
> at least one `0`→`1` transition, which no silent no-op erase can deliver) together with consecutive
> read-backs asserted to differ in **all 65536 bytes** both times. **Gate 3 (`--pulse-us 4688`) is
> next and is separately authorized** — it is `145-07`'s, it is not covered by Gate 2's spend
> authorization, and it has not been run.

## Deviations from Plan

**1. [Rule 1 — Bug, self-inflicted, caught and fixed] A `cmp` run in the wrong working directory
produced a false green.** The first cycle-2 consecutive-read-back check ran `cmp -s
readbacks/readback1.bin readbacks/readback2.bin` from `/workspaces` instead of the phase directory.
Both files were missing, `cmp` exited **2** (error), and the `test $? -ne 0` guard fired the
"cycle2 content differs" message anyway. **The plan's own verify block contains this same
`test $? -ne 0` construction**, so this is a defect in the checking idiom, not merely a typo. Caught
immediately (the adjacent `sha256sum` printed "No such file or directory"), discarded, and re-run
from the correct directory with `stat` confirming both files present and `cmp`'s exit **1**
distinguished from exit **2**. Recorded in the bench log at the point of the assertion. Commit
`59bcfeea`.

**2. [Rule 1 — Bug] The plan's Task 3 acceptance grep is broken and was not made to pass.** The plan
specifies `grep -cE "^### .*firestarter .* (write|verify|read|erase|id|dev consistency-check) "`.
Every command-line heading in this log is at `####` depth (a convention set in Gate 1, long before
this plan was written), and `^### ` does not match `#### `. The expression returns **0** against a
fully compliant record — **it cannot distinguish compliance from an empty file**. The heading depths
were **not** changed to satisfy it; the assertion is made with a corrected `^#{2,6} ` expression and
the original is quoted in the record so the substitution is visible. Commit `03be8b82`.

**3. [Rule 1 — Bug] The evidence block inflated its own counting grep.** Quoting the four command-line
headings at column 0 with their `####` intact made `grep -E "^#{2,6} .*firestarter "` match its own
evidence block, reporting **8** where the truth is **4**. Fixed by transcribing them indented and
de-hashed; the reason is recorded in the log. This is the same class of error as deviation 1 — a
measurement that measures itself. Commit `4fcb93b9`.

**4. [Record honesty] The "every command line is its own heading" claim is weakened to what the record
supports.** D-17 and the plan describe the assertion as covering command lines that each appear "as
its own subsection heading". Only **4** of the 17 do; the other 13 are fenced-block lines, and the
`verify`/`read` commands are additionally quoted inline in prose. The record claims what is true —
**all 17 are recorded verbatim somewhere and all 17 were checked** — rather than the stronger
formulation.

**5. [Record honesty] `SHA256SUMS.txt` — two rows appended, not four.** `img2.bin` and `img3.bin`
rows already existed from `145-01` and are unchanged. Same precedent as `145-05`.

**6. [Record honesty] MERGE-05's +96 B breach carried, still NOT adjudicated.** Gate 2's result was
obtained on a build with a known, open, un-adjudicated band breach. **No baseline was re-anchored, no
band widened, and `test_policy_merge05_fires_on_the_current_tree` was not touched.** Recorded at the
point of the verdict so no reader discovers it elsewhere.

**7. `REQUIREMENTS.md` untouched; `BENCH-01` NOT ticked**, despite this plan's frontmatter naming it.
Phase 145 centralises requirement ticking in `145-09` behind a blocking operator gate. `git status
--porcelain .planning/REQUIREMENTS.md` returns 0 lines.

**8. [Criterion divergence, recorded not hidden] `ROADMAP.md` DID change — by one plan checkbox.**
Task 3's acceptance criterion reads `git diff --name-only HEAD~1 -- .planning/REQUIREMENTS.md
.planning/ROADMAP.md | wc -l` returns 0. `ROADMAP.md` is **not** 0: the mandated
`roadmap.update-plan-progress 145` step flipped `- [ ] 145-06-PLAN.md` to `- [x]`. That is GSD plan
bookkeeping, **not a requirement flip**, and the diff was checked against a pre-call snapshot to
confirm the blast radius is exactly that one line — no whole-file reformat and no other phase's
`**Plans:**` line clobbered. The criterion's intent (no requirement moved before `145-09`'s operator
gate) is satisfied; its literal wording is not, and conflating the two would have meant either
skipping a mandated state update or misreporting the diff.

**9. [Tooling] The `state.*` writers needed named arguments and clobbered a field.**
`state.record-metric` and `state.add-decision` reject the positional form given in the executor
instructions (`"phase, plan, and duration required"`, `"summary required"`) and were re-run with
`--phase/--plan/--duration` and `--summary`. `state.advance-plan` **overwrote**
`last_activity_desc` with the truncated string `145-05 complete. See`, and `add-decision` emitted
`[Phase ?]` instead of resolving the phase. Both were repaired by hand against a pre-call snapshot,
along with the stale `Plan: 7 of 9 (145-01..145-05 complete…)` line and a `Resume file: None`.

### Not a deviation, but worth naming

**No operator gate was self-approved.** Gate 2's three-cycle spend authorization ("you can erase or do
anything its a test ic for you") was given in `145-05` and was already discharged; this executor had
no `AskUserQuestion` capability and reached no new gate. Gate 3's authorization is **separate and was
not sought** here.

## What this plan did NOT prove

- **The intermittent single-byte margin failure is mitigated, not explained.** Gate 2's three cycles
  bring the run to 15 consecutive clean cycles on this part. **Fifteen clean cycles is not a root
  cause** — nobody knows whether the original cause was an under-settled route, a marginal cell, or
  program-window VPP droop.
- **Program-window VPP under load was never measured** — the standing Phase-97 DTR-reset tooling gap.
  Every VPP figure in this record is an *idle* sample.
- **Gate 3 was not run**, so `--pulse-us`, Claim B, D-12 and the sharp CAP-03 discriminating case
  (a budget exceeding the 120 s legacy fallback) all remain open and are `145-07`'s.
- **Claim B is not claimed**, despite `blocks_with_multiple_updates=2` in all three cycles.
- **No comparative claim against earlier firmware** (D-08) and **no datasheet-conformance claim**.
- **Nothing about `0x08` or `0x0B`** — both remain skipped-with-reason.
- **Nothing about Uno-class boards** — the progress emission is compiled out on `SERIAL_ON_IO`
  targets, so Claim A is structurally unavailable there.
- **The advertised CAP-03 budget was still never observed**, only the completion.
- **`BENCH-01` is not complete** — Gate 3 and `145-08`'s verification-map rows remain.

## Self-Check: PASSED

All created files verified present at expected sizes: `readback2.bin`/`readback3.bin` 65536 B each;
six `run_NN.bin` files 65536 B each; all ten cycle-2/cycle-3 logs present. `sha256sum -c
SHA256SUMS.txt` exit 0 over all eight rows. `cmp` byte-exact for both image/read-back pairs; `cmp`
exit 1 (differ) for both consecutive read-back pairs. Commits verified in `git log`: `59bcfeea`,
`64a4343e`, `03be8b82`, `4fcb93b9`. `git -C /workspaces/firestarter status --porcelain` empty
(0 lines) after every task. Session 1's preserved failure evidence
(`write_cycle1_attempt1.stdout.log`, `.stderr.raw`) untouched — last modified by commit `87904804`
in `145-05`, not by this plan.
