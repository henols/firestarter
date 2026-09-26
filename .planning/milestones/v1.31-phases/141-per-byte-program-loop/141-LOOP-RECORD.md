# 141-LOOP-RECORD: Phase 141 Per-Byte Program Loop — Close Record

**Owner requirements:** LOOP-01, LOOP-02, LOOP-03, LOOP-04, LOOP-05, LOOP-06, LOOP-07, LOOP-08 — all
eight discharged **here**, by this plan (141-09), citing the evidence the eight prior plans
(141-01 through 141-08) produced. **Status:** the cold measurement this document reconciles was taken
strictly after `141-PREDICTIONS.md` was committed, exactly as that document requires. **The MERGE-05
flash-band policy is RED and stays RED** — an explicit operator decision, recorded in §1 and not
softened anywhere in this document. Every other gate this phase touches is green. LOOP-01 through
LOOP-08 are marked complete in `.planning/REQUIREMENTS.md` by this same plan's Task 3, after every
piece of evidence below exists.

This document follows `140-PARAM-TABLE-RECORD.md`'s house shape (numbered sections, a findings
register with owners, an explicit "what this is and is not" framing, a hand-off table), adapted to
the sections this plan's own Task 2/Task 3 action text specifies.

---

## 1. MERGE-05 verdict — RED, and it stays RED (operator decision)

**Operator decision, recorded before this plan (141-09) began — 2026-08-10, during `/gsd-execute-phase
141`, before Wave 3 was dispatched.** The operator was presented three options for the flash-band
overage below (continue-and-record / halt-and-shrink / re-baseline) and chose: **"Continue; 141-09
records it."** This document's job is to record the RED faithfully, not to fix it and not to soften
it. Per that instruction, this plan did **not** run the plan's own action-text reduction ladder
(payload-size shrink / `verify_mode` call collapse / dead-function deletion) — attempting it would
re-litigate a decision the operator already closed before this plan was dispatched. No baseline JSON
was edited; `git status --porcelain scripts/baseline/` is empty in `/workspaces/firestarter`.

### 1.1 Cold measurement (this plan's own, re-derived — matches the pre-dispatch figures exactly)

Each target was measured via `pio run -t clean -e <env>` followed by a single uninterrupted
`pio run -e <env>`, one target at a time, logs captured:

```
uno:      RAM 1573 B / Flash 24424 B  (75.7% of 32256)
uno328pb: RAM 1579 B / Flash 24474 B  (75.6% of 32384)
leonardo: RAM 2014 B / Flash 26400 B  (92.1% of 28672 — 2272 B headroom)
```

### 1.2 `check_size_baseline.py --policy merge05` — verdict, verbatim

```
$ cd /workspaces/firestarter && python3 scripts/check_size_baseline.py --policy merge05 \
    --baseline scripts/baseline/size_baseline_base01.json \
    --avr-log uno=<log> --avr-log uno328pb=<log> --avr-log leonardo=<log>
FAIL:
  uno: flash_used baseline=23932 observed=24424 delta=+492 exceeds MERGE-05 uno-class band of 64 B
  uno328pb: flash_used baseline=23976 observed=24474 delta=+498 exceeds MERGE-05 uno-class band of 64 B
  leonardo: flash_used baseline=26072 observed=26400 delta=+328 exceeds MERGE-05 leonardo band of 0 B
$ echo $?
1
```

**RAM passes exactly** on all three targets (0 delta vs BASE-01: 1573/1579/2014, identical) — the
script prints no RAM `FAIL:` line, and the equality enforcement (`check_size_baseline.py:224-227`)
is satisfied. The removed `uint8_t mismatch_bitmask[DATA_BUFFER_SIZE / 8]` stack array (64 B on
Uno-class, 128 B on Leonardo, `eprom.cpp:155` pre-141-04) is a genuine peak-stack improvement that
deliberately does **not** appear in this figure — a stack array is neither `.data` nor `.bss`, so
`avr-size`'s static `ram_used` cannot see it move, exactly as `141-PREDICTIONS.md` P2 stated before
any code moved.

### 1.3 `check_build_warnings.py --rebuild` — passes, watermark holds with zero headroom

```
PASS: uno: macro_redefinition=0 (== 0), uno328pb: macro_redefinition=0 (== 0),
      leonardo: macro_redefinition=0 (== 0), native: total warnings=1166 (== watermark 1166),
      native_nodevtools: total warnings=1166 (== watermark 1166)
```
Exit 0. The three AVR targets stay at exact-zero macro-redefinition warnings; both pinned native
envs sit exactly **at** the 1166 watermark — **zero headroom**, unchanged since before this phase
started. Neither `native_loop_v131`, `native_trace_v131`, nor `native_params_v131` was ever passed
to this script or to `check_size_baseline.py` (an unrecognized env name raises an uncaught `KeyError`
in the latter, exit 1 — F-138-05, inherited, accepted, not fixed by this phase).

### 1.4 Measured-versus-predicted table

`141-PREDICTIONS.md` was committed at `4c5d9172` (meta repo, branch
`gsd/v1.31-27c-programming-algorithm-fidelity`), **before** plan 141-04 (or any later plan) moved a
byte of `src/proms/eprom.cpp` or `src/proms/memory.cpp` — the ordering this document's own reconciliation
section requires.

| Target | BASE-01 | 141-PREDICTIONS.md P1 (Phase-141-only delta) | Predicted absolute | **Measured absolute (this plan, cold)** | **Measured total delta vs BASE-01** | Band | Remaining headroom |
|---|---|---|---|---|---|---|---|
| `uno` | 23932 | +30 B | 23984 (+52 vs BASE-01) | **24424** | **+492** | 64 B (uno-class) | **−428 B (over budget)** |
| `uno328pb` | 23976 | +30 B | 24034 (+58 vs BASE-01) | **24474** | **+498** | 64 B (uno-class) | **−434 B (over budget)** |
| `leonardo` | 26072 | +18 B | 26034 (−38 vs BASE-01, i.e. under ceiling) | **26400** | **+328** | 0 B (must not grow) | **−328 B (over budget)** |

RAM (P2, all three): predicted exact-0 delta — **measured exact-0 delta, confirmed** (1573/1579/2014,
byte-identical to BASE-01).

**The overrun is roughly 14x P1's point estimate**, and beyond even `141-PREDICTIONS.md`'s own
acknowledged worst case (that document's own ingredient ledger, recomputed from its high-adds/
low-removes extremes, reaches approximately +274 B — still well short of the measured +422/+422/
+336 B this phase's own rewrite contributed on top of the pre-141-04 tip).

### 1.5 Attribution of the overrun

Of `uno`'s measured **+492 B** total delta vs BASE-01:

- **+22 B** — pre-existing Phase 140 tip (already spent before Phase 141 began; unrelated to this
  phase's own work).
- **+48 B** — plan 141-02's `mem_util_delay_us` / `mem_util_split_delay` safe-delay helper.
- **+422 B** — plan 141-04's rewrite itself, decomposed via `avr-nm --print-size` (LTO is active,
  confirmed by `__gnu_lto_slim`/`__gnu_lto_v1` markers in every `.o`, which is why `eprom_overprogram_us`,
  `eprom_params_for`, and `configure_eprom` do not appear as separate linked symbols in either build):
  - **+108 B** — `eprom_write_execute` itself (898 → 1006 B): the actual per-byte pulse→verify loop,
    the two skip checks, the dual budget tracking, the DIP32 branch, the `overprogram` gate, and the
    `VERIFY_PER_PULSE_PLUS_FINAL` final-pass loop.
  - **+110 B** — `eprom_internal_report_budget_failure` (new, kept out-of-line by LTO because it has
    two call sites).
  - **+156 B** — `configure_memory` (864 → 1020 B): `configure_eprom`'s two new D-03/D-05 refusals
    land here once inlined, **and** this is the first place `eprom_params_for()`'s own linear-scan
    accessor body becomes genuinely linked at all — the two costs are inseparable in this one number.
  - **+48 B** — `EPROM_PARAMS[]` (36 B) + `EPROM_PARAM_KEYS[]` (3 B) PROGMEM data becoming linked for
    the first time, plus alignment/padding.

**Key framing for the record: roughly +204 B of the +422 B is Phase 140's parameter table finally
being paid for**, not new Phase 141 logic. Before this phase, nothing in `src/` called
`eprom_params_for()`, so `-Wl,--gc-sections` collected the whole table and its accessor wholesale
(Phase 140 F-140-02, `140-PARAM-TABLE-RECORD.md` §6). `configure_memory`'s own +156 B delta is where
that first-live-reference cost lands, combined with `configure_eprom`'s two refusals — the two are
not separable by this measurement, but the accessor-body-plus-hoisted-reads component of that number
is itself larger than the entirety of what `141-PREDICTIONS.md` budgeted for it. **Only roughly
+218 B is attributable to this phase's own loop and reporter logic** (`eprom_write_execute` +108 B,
`eprom_internal_report_budget_failure` +110 B). The **64 B `MERGE05_UNO_CLASS_FLASH_BAND`** was set
in Phase 123/124, before Phase 140's parameter table existed to be paid for — the band's own
provenance predates the cost this phase is now the first to pay.

### 1.6 The prediction miss — which ingredient was under-budgeted

`141-PREDICTIONS.md`'s own ingredient ledger budgeted roughly **70-80 B combined** for "the accessor
body" (`eprom_params_for()`'s ≤3-iteration linear scan) plus "six hoisted `pgm_read_*` reads" (one
per `eprom_params_t` column, at the loop's setup). The measured first-live-reference cost — captured
in the `configure_memory` delta above, **+156 B**, which is *at minimum* that same accessor-body cost
(it also carries `configure_eprom`'s two refusals) — is **at least double** the entire budgeted
figure, on its own, before the per-byte loop's own growth or the new reporter are even counted. This
is the single largest source of the miss: **the first-live-reference cost of the Phase 140 table was
under-budgeted by roughly 2x**, not merely imprecisely estimated. The retry-loop-removal's reclaim
(the *removes* half of the ledger) also plausibly landed toward the low end of its own acknowledged
range — 141-04-SUMMARY names the named uncertainty explicitly: AVR has no hardware 32-bit multiply/
divide, and if `libgcc`'s `__mulsi3`/division-helper routines were already linked elsewhere in the
binary for an unrelated reason, removing the one retry-loop call site reclaims only the call-site
overhead, not the shared routine body.

This is not reconciled by editing the implementation to force agreement with the prediction — no
task in this plan alters `src/proms/eprom.cpp` or `src/proms/memory.cpp`, and no baseline JSON was
edited. The number is recorded as measured; Phase 144 / TEST-08 owns the full 138-143 cross-phase
flash/RAM delta reconciliation, and inherits this attribution rather than re-deriving it.

---

## 2. D-13 protocol-branch-inventory movement — tier-1 unchanged, tier-2 GREW (correcting D-11's own framing)

**Before** (recorded golden, pre-141-04): **24 total** = **3 tier-1** (protocol-keyed, lines 71/145/218)
+ **21 tier-2** (handle-field-keyed).

**After** (measured, 141-04's live cross-check and 141-05's independent re-derivation from the
scanner agree exactly): **27 total** = **3 tier-1** (lines 70/190/340 — text byte-identical at each
site, only the line number moved) + **24 tier-2**.

**Net: tier-2 grew 21 → 24 (+3), tier-1 stayed exactly 3.** Sites removed (3, all inside the two now-
deleted helper functions): the two `program_mismatched_bytes`/`verify_and_update_mask` loop bounds and
the verify-comparison inside them. Sites added (6): D-03's pre-flight refusal (`energy_cap_us > 0 &&
pulse_delay > energy_cap_us`); D-09's `pins >= 32` DIP32 branch; the byte-loop bound; LOOP-06's
already-matching skip check; the pulse-verify loop's own convergence check (same predicate text as
the skip check, a distinct site); and the final full-block verify pass's loop bound
(`VERIFY_PER_PULSE_PLUS_FINAL` rows only).

**Correcting `141-CONTEXT.md` D-11's own framing, as a named finding, not a silent overwrite:** D-11
said "record the shrinkage" — that phrasing assumed removals would dominate. They did not. A
per-byte loop structurally adds more handle-field-keyed predicates (skip checks, dual budget checks,
a DIP32 branch, an overprogram gate) than the old flat block-retry loop needed, so **tier-2 growth
is the correct, legitimate outcome of this rewrite, not a violation of anything D-13 exists to
catch.** D-13's actual invariant — the one that matters for TABLE-05 — is that **tier-1 stays exactly
3**: no fourth protocol-keyed dispatch axis was introduced. That invariant held throughout. A reader
who takes "the shrinkage" literally from D-11's prose alone, without checking the measured tier-1/
tier-2 split, would wrongly read tier-2's growth as a regression; this section exists so that reading
is corrected here, once, rather than repeated by a downstream plan.

(For completeness: `141-PREDICTIONS.md`'s own P3 predicted a total of 33, decomposing 12 added
tier-2 sites against `_extract_predicates`'s literal `"handle->"`-substring heuristic. Only 6 of
those 12 are textually visible to the scanner — the other 6 operate on **local variables** hoisted
from `handle->`/table fields one statement earlier, so their condition text contains no `handle->`
substring and the scanner, a text scanner rather than a data-flow analyzer, does not count them, even
though they are real handle-derived branches. This is a structural property of the extractor's
heuristic, confirmed and explained in `141-04-SUMMARY.md`, not a defect in either the extractor or
the rewrite — the extractor's actual job, catching a *second protocol-keyed dispatch axis*, does not
care about tier-2 undercounting.)

---

## 3. LOOP-03's non-claim — the overprogram path is proven in arithmetic and gating only

**Stated plainly:** the end-to-end `overprogram` pulse path is proven **only** in its arithmetic and
its gating, **never through the loop itself**, because `overprogram_factor` is `0` on all three
shipped rows (`0x07`, `0x08`, `0x0B` — Phase 140, `140-PARAM-TABLE-RECORD.md` §§3-4) and no live row
can ever reach the code that would emit an overprogram pulse.

- **The pure function:** `eprom_overprogram_us(pulse_count, pulse_us, factor, cap_us)` (D-08),
  declared in `eprom.h`, proven at all six named boundary inputs by plan 141-08 Task 1: the `3×N`
  product (`(1, 100, 3, 75000) → 300`), the `factor = 0` gate every shipped row takes (`(5, 100, 0,
  75000) → 0`), the cap clamp at and above the boundary (`(25, 1000, 3, 75000) → 75000`; `(25, 1001,
  3, 75000) → 75000`), 32-bit-overflow safety at `3 × 25 × 65535 = 4915125` (`(25, 65535, 3, 75000) →
  75000`, correctly clamped rather than wrapping), and the `cap_us = 0` fail-safe reading (`(5, 100,
  3, 0) → 0`).
- **The separate assertion that all three live rows emit zero extra pulses** — proven natively (plan
  141-07/141-08's `native_loop_v131` cases): no live row (`0x07`/`0x08`/`0x0B`) ever produces a third,
  overprogram pulse.
- **What is NOT proven:** no test in this phase drives `eprom_write_execute` itself with a nonzero
  `overprogram_factor` — there is no shipped data that reaches that branch, so the loop-integration
  half of LOOP-03 has no oracle. This is a structural fact about the shipped table, not a gap this
  phase could have closed with more test-writing effort.

**Handed to Phase 146 / CLOSE-04**, alongside F-140-05 (the `0x07` Intel-family-split candidate that
would be the first row to actually exercise this path).

---

## 4. What "hard-fails the block" actually does — traced, not assumed

LOOP-05 says the write **aborts** on a budget failure. `eprom_write_execute` operates on exactly one
512-byte (Uno-class) or 1024-byte (Leonardo) block; the host streams the rest across multiple commands.
This section names precisely what the firmware does with the remaining blocks, traced through the
live source (line numbers current as of this plan's own read):

1. `eprom_internal_report_budget_failure` sets `handle->response_code = RESPONSE_CODE_ERROR` and
   disables `CTRL_VPP_REGULATOR_ENABLE` before returning.
2. `_process_incoming_data` (`src/eprom_operations.cpp:115-117`) — `if (!op_execute_function(handle
   ->firestarter_operation_main, handle)) { return false; }` — returns `false` **immediately**. Line
   124 (`handle->address += handle->data_size;`) is never reached: **`handle->address` does not
   advance.**
3. `op_execute_stateful_operation` (`src/operation_utils.cpp`) propagates that `false` back up through
   `eprom_write`'s own `!op_execute_stateful_operation(...)` negation, which resolves to `finished =
   true` in `firestarter.cpp`'s main dispatch switch (`src/firestarter.cpp:210-286`).
4. `if (finished) { command_done(&handle); }` (`firestarter.cpp:284-286`) fires immediately.
   `command_done()` (`firestarter.cpp:162-171`) zeroes `CONTROL_REGISTER`, `LEAST_SIGNIFICANT_BYTE`
   and `MOST_SIGNIFICANT_BYTE`, disables the chip, and sets `handle->cmd = CMD_IDLE`.

**Conclusion for the record: the firmware processes no further blocks.** The streaming pump exits on
the very command in which the failure occurred; it does not skip ahead to the next block and it does
not silently continue. "The write aborts" and "the firmware stops accepting more blocks for this
write" are **the same event**, not two different claims that happen to coincide. The host observes
the `RESPONSE_CODE_ERROR` frame (carrying the budget-failure message id and its payload) followed by
normal command termination — no further `DATA:`/`OK:` exchange for this write occurs.

**Phase 143 / HOST-03 has to render exactly this.** A host-side implementation that assumes the
firmware might continue past a failed block, or that retries the same block automatically expecting
firmware-side resumption, would be building against a behaviour the firmware does not have.

---

## 5. The three new message IDs and the band cost

`MSG_ERR_PULSE_TOO_WIDE` (`0xAE`), `MSG_ERR_MAX_PULSES` (`0xBD`), `MSG_ERR_ENERGY_CAP` (`0xBE`) — all
three authored in meta's `tools/catalog/messages.toml` (D-04) and regenerated into both sub-repos.

**The ERROR band `0xA0..0xBF` now has exactly one free slot: `0xBF`.** Confirmed by direct
enumeration of `firestarter/include/messages.h`: every value `0xA0` through `0xBE` is assigned (26
consecutive IDs, including this phase's own three), and `0xBF` is the sole gap before the band's own
ceiling. **Phase 142 and Phase 143 both need to know this before either claims a new ERROR id** — at
most one of them can take `0xBF`; the other must either share an existing id (with a discriminator)
or use a different band.

**`MSG_ERR_WRITE_FAILED` (`0xB1`)'s three-param shape (`u24 address, u8 retries, u16 bad bytes`) is now
emitted by nothing on the 27C path.** Confirmed by a whole-tree grep: zero references to
`MSG_ERR_WRITE_FAILED` anywhere under `src/`. It was the old block-retry loop's own failure id;
`eprom_internal_report_budget_failure` reports `MSG_ERR_MAX_PULSES`/`MSG_ERR_ENERGY_CAP` instead, with
a different, smaller payload shape (`u24 address, u8 pulse_count`). **Phase 143 must not expect
`MSG_ERR_WRITE_FAILED` on a write through the rewritten 27C loop** — whatever other protocol family
still emits it (if any), it is not this one.

---

## 6. The two orphaned catalog IDs — left assigned, deliberately

`MSG_INFO_RETRIES` (`0x51`) and the debug id `DBG_PULSE_DELAY_MISMATCH` (`0x15`) are now unreferenced
by firmware — confirmed by a whole-tree grep of `src/` and `include/`: both ids exist only in their
own `#define` in `messages.h`, with zero call sites anywhere else. Both were the old block-retry
loop's own instrumentation (the retry-count info message and the pulse-delay-mismatch debug trace),
now dead since the per-byte loop's cadence has no analogous retry-escalation event.

**Decision: leave both assigned and unedited.** No orphan-id gate exists in either repo, and deleting
an id risks a later reuse collision for zero behavioural gain — a future catalog author picking a
"free" id that used to mean something else is a worse failure mode than one dead id sitting quietly
in the table. `DBG_PULSE_DELAY_MISMATCH`'s own wording ("retrying with increased pulse delay") now
actively **contradicts** shipped behaviour — the new loop never increases pulse delay; every pulse is
fixed-width. **A wording-only catalog change produces a zero-byte firmware diff** because
`messages.h` is codegen-generated and ID-only (`#define MSG_ERR_WRITE_FAILED 0xB1`-shaped; the wording
lives host-side) — so fixing the stale wording costs nothing in flash and could be done cheaply.
**Handed to Phase 146 / CLOSE-04** as the wording question; this phase does not touch the catalog for
either id.

---

## 7. LOOP-06 is protocol-scoped on READS, universal on PULSES (orchestrator finding, plan 141-07)

Plan 141-07 drove protocol `0x0B` for its LOOP-06 cases instead of the `0x07` its own action prose
named — the correct call, verified directly from source
(`src/proms/eprom.cpp:296-314`, `src/proms/eprom_params.cpp:46-48`):

| Protocol | `verify_mode` | Final full-block pass |
|---|---|---|
| `0x07` `PROTO_EPROM_28PIN` | `VERIFY_PER_PULSE_PLUS_FINAL` | yes — re-reads every byte unconditionally |
| `0x08` `PROTO_EPROM_32PIN` | `VERIFY_PER_PULSE_PLUS_FINAL` | yes — re-reads every byte unconditionally |
| `0x0B` `PROTO_EPROM_24PIN` | `VERIFY_PER_PULSE` | no final pass |

The `VERIFY_PER_PULSE_PLUS_FINAL` block re-reads **every** byte of the block unconditionally, with no
skip for an `0xFF` byte or an already-matching byte. Therefore:

| Protocol | `0xFF` byte reads | already-matching byte reads | program pulses (both cases) |
|---|---|---|---|
| `0x0B` | 0 | 1 | 0 |
| `0x07` / `0x08` | 1 | 2 | 0 |

**Why this is not a requirement failure:** `.planning/REQUIREMENTS.md`'s own wording for LOOP-06 is
about the **pulse**: "Already-matching bytes and `0xFF` bytes are skipped without emitting a program
pulse." The pulse skip is universal across all three shipped protocols — confirmed natively on all
three. **LOOP-06 is genuinely, fully satisfied.**

**What is over-specified, and corrected here as a scoped non-claim:** plan 141-07's own action prose
claimed a `0xFF` target byte is "never read and never pulsed" — that holds only on `VERIFY_PER_PULSE`
protocols (`0x0B` today). On `0x07`/`0x08` it is **false by design**: the unconditional final pass
reads every byte, including ones the per-byte loop itself never touched. The read-skip is proven on
`0x0B` only; it is not, and was never claimed by the requirement itself to be, a universal read-skip.

---

## 8. `STROBE_KIND_DATA` is not a sound raw pulse-count oracle (finding, plan 141-07)

`rurp_internal_write_to_register` (`include/rurp_register_utils.h:63-89`) pushes every non-elided
register write (LSB/MSB/CONTROL latch) through the **same** `rurp_write_data_buffer()` call a genuine
chip-data pulse uses. Both therefore record an indistinguishable-by-kind `STROBE_KIND_DATA` entry. A
raw count of `STROBE_KIND_DATA` entries overcounts actual program pulses by every register-shift write
in the same capture window — plan 141-07 measured this directly: a drafted 4-byte `0x07` case expected
10 raw `STROBE_KIND_DATA` entries and observed 19.

**A fixed-floor baseline-delta subtraction does not repair this either.** On `0x08` specifically,
`LOOP_BUS_CONFIG_0x08`'s `rw_line` makes every read↔write direction change force a non-elided
`CONTROL` rewrite, so that register noise **scales with pulse count** rather than adding a constant
per-drive floor — a 2-pulse run showed a delta of 6 against its own 0-pulse baseline, not 2.

**The sound replacement:** filter by the strobe's recorded **value**, not its kind — `count_data_
pulses_with_value(byte)` counts only `STROBE_KIND_DATA` entries whose value equals the actual byte
being programmed. A genuine pulse's `rurp_write_data_buffer(data)` call always carries `data ==
expected`; a register-shift's call carries a register value (an address byte or a CONTROL bitmask)
that cannot coincidentally collide with a chosen test byte value. **Any future native case counting
data pulses must filter by value** — this is now a load-bearing convention for
`test_loop_eprom_v131.cpp` and any suite that extends it.

---

## 9. Arithmetic correction: the honest 0x0B energy-cap worst case is 99998 µs, not 99999 µs

Plan 141-05 caught and corrected an off-by-one carried by `141-CONTEXT.md`'s own D-01/D-0B worked
example and repeated in several plan documents. The worst-case accumulated-at-failure under D-03's
pre-flight refusal is **`2 × 49999 = 99998` µs**, reached at pulse width `w = 49999` — **not** the
`2 × 50000 − 1 = 99999` µs several plan files state.

**Why `99999` is wrong:** the loose bound `accumulated < energy_cap_us + w` evaluates to `99999` only
if substituted at `w = energy_cap_us` (i.e. `w = 50000`). But at `w = 50000` exactly, D-03's own
pre-flight refusal permits **at most one pulse** before the energy-cap check can fire on a second
pulse — the second pulse requires `(i-1) × w < energy_cap_us`, which is false the moment `w ==
energy_cap_us`. So `99999` is never actually reachable by any input; the algebraic slip used
`2 × cap − 1` where `2 × w` was needed. An exhaustive brute-force search over every integer `w` in
`[1, 50000]` (the full range D-03 permits) confirms `w = 49999` is the **global maximum**, giving
`99998` µs, at exactly 2 pulses.

**The corrected value lives in `firestarter/CLAUDE.md`'s `0x0B` Algorithm Handlers row**, which states
both the naive `99999` evaluation and its correction transparently, rather than silently swapping one
unexplained number for another. **The plan files (`141-CONTEXT.md`, and this same worked example
repeated in `141-05-PLAN.md`'s action text) still say `99999`** — this record names that they are
stale on this one figure and that `CLAUDE.md` is the corrected source, per this project's standing
convention of not silently rewriting locked context documents after the fact.

**Separately, and not to be confused with this correction:** `141-CONTEXT.md` D-01's *different*
figure — the "without D-03" bound of `50000 + 65535` for an unbounded `--pulse-us` value — describes a
scenario D-03's refusal makes arithmetically unreachable once D-03 ships. That figure is not repeated
in this record.

---

## 10. Native env run-by-name obligations — no CI leg, ever, for three of them

None of `native_loop_v131`, `native_trace_v131`, or `native_params_v131` runs in **any CI leg** of
either repository — confirmed by inspection: neither `firestarter/.github/workflows/build.yml` nor
`beta-build.yml` invokes any `pio test` env beyond the two pinned ones, `native` and
`native_nodevtools`. Their pass counts are **local run-by-name obligations**, recorded here as this
phase's evidence, never implied as CI-covered:

- **`native_loop_v131`** (this phase's own oracle, D-10 — authored because the frozen `native_trace_v131`
  fixture cannot verify the rewrite): `cd /workspaces/firestarter && pio test -e native_loop_v131` →
  **39 test cases: 39 succeeded** (6 harness self-checks from 141-03, 14 from 141-07, 19 from 141-08).
- **`native_params_v131`** (Phase 140's table-accessor suite, unaffected by this phase): `pio test -e
  native_params_v131` → **9 test cases: 9 succeeded**.
- **`native_trace_v131`** (D-10's frozen pre-change fixture, deliberately not re-frozen this phase): `pio
  test -e native_trace_v131` → **6 test cases: 3 failed, 2 succeeded** — see §10.1.

### 10.1 `native_trace_v131` — the one expected non-green, named as expected

`native_trace_v131` is **RED by design (D-10)**, and this record names it explicitly here so
`/gsd-verify-work` reads it as expected, not as a regression. Full detail — the confirmed RED shape,
the banners, the full entry list, and the cadence walk — lives in `141-NEW-TRACE.md`, this plan's own
Task 1 artifact; cross-reference it rather than duplicating its content here.

**Correcting this plan's own must_have wording, honestly:** this plan's frontmatter states the RED
must be named "with its determinism leg confirmed still passing." Measured reality, verified in
`141-NEW-TRACE.md` §3: the determinism assertion (a second drive on the same handle, compared
positionally against the first) sits **after** the length-equality check that fails first, and Unity
aborts the test case on that first failure. **The determinism leg never executes — it does not "still
pass"; it is structurally unreached.** This record does not repeat the "still passing" claim.
Independent (weaker-form) evidence the new cadence is nonetheless deterministic exists — two separate
process invocations of the dump binary produced byte-identical output — and is recorded in
`141-NEW-TRACE.md` §3 as exactly that: cross-process evidence, not the intra-process form the helper
itself performs.

---

## 11. Orphaned defect hand-off: the unscoped porcelain check in `test_flash_path_record_sync.py`

`firestarter/tests/test_flash_path_record_sync.py::test_planted_mutation_of_the_real_subset_is_detected`
asserts, at its own line ~1247, `assert _git_porcelain(_FW_REPO_ROOT) == ""` — the **whole repository's**
`git status --porcelain`, not scoped to the one file (`FLASH-PATH-AND-PCB.md`) the test actually plants
a mutation against and restores. Any legitimate uncommitted mid-plan change anywhere else in the tree —
which every single-task-commit workflow in this project produces between a task's file edit and its
commit — makes this specific test fail with a message about a file it never touched. **Every plan in
this phase had to work around it** (commit the in-flight change first, then re-run the full suite) —
141-04, 141-05, 141-06, and 141-08's own SUMMARYs each independently record hitting this exact trap.
This is a genuine, orphaned test defect — not a false claim about the codebase, but a false claim
about what the test itself is checking (it names one file's sync in its docstring and checks the
entire tree's cleanliness in its assertion) — and is handed off here rather than fixed in-phase,
since fixing it would be a change to a gate file outside this phase's declared scope. **Owner:
unassigned; flagged for whichever phase next touches this test module or `check_permitted_claims.py`-
adjacent gate hygiene.**

---

## 12. Hand-offs

| # | Finding | Owner |
|---|---|---|
| H1 | D-09's corrected mechanism: the drop bit dies via the `pins < 32` **preserve-mask** guard at `memory.cpp:172` (current line; comment block spans ~159-190), **not** via a bit collision — on every shipped build (`-D HARDWARE_REVISION` in every `[env]`'s shared `build_flags`) `CTRL_ADDRESS_LINE_16` is `0x01` and `CTRL_VPP_VPE_DROP_ENABLE` is `0x100`, two distinct bits. `0x08` (`pins == 32`, `vpp_path = VPP_PATH_DROP_RESISTOR`) is the row where the exclusion actually bites. The in-file comment that previously stated the collision theory was corrected during this phase (141-04/141-05). | **Phase 142 / VPP-01, VPP-03** (route choice: P1 vs. drop resistor; mask-set consolidation) |
| H2 | D-12's finding: the roadmap calls Phase 143 "independent of 140-142 (different repo)", but HOST-02's own named precedent — `mem_util_blank_check`'s operation-in-progress + `progress_data` pattern, `memory.cpp:379-413`-ish (CONTEXT.md's `:307-341` citation predates this phase's line shifts; re-locate before relying on the exact range) — is a **firmware** pattern. If HOST-02 needs intra-block emission, part of Phase 143 lands in `firestarter/`, despite the roadmap's framing. Named here **before** Phase 143 plans, as D-12 requires. | **Phase 143** |
| H3 | Milestone C3 correction: `pulse-delay` is parsed by `extract_long` into an **unclamped** `uint32_t` (`json_parser.c:503`) — an over-ceiling `delayMicroseconds` value is reachable **today**, before `--pulse-us` ships. C3's "no bare pulse comes near [the 16383 µs ceiling]" is true of `chip_database.json` data (whose full pulse-width set is 10/20/50/100/200/500/1000 µs) and **false** of the wire. | **Phase 146 / CLOSE-04**, alongside F-140-05 and F-140-07 |
| H4 | The honest energy-cap ceiling: exactly **50 ms** on every shipped `0x0B` width (200/500/1000 µs give exactly 250/100/50 pulses, `accumulated` landing on exactly 50000), and a worst case of **99998 µs** (not 99999 — §9) for an arbitrary width under D-03's refusal. `141-CONTEXT.md` D-01's larger, roughly-double figure (`50000 + 65535` µs) describes the bound **without** D-03 and is arithmetically unreachable now that D-03 ships — this record deliberately does not restate that figure's numeral. | **Phase 146 / CLOSE-04**, alongside F-140-05 and F-140-07 |
| H5 | Two dispositions this phase **decided rather than deferred**, so Phase 144 does not re-litigate them: (a) `verify_mode` is **consumed** — `0x07`/`0x08` run one additional, unconditional final full-block verify pass after the byte loop; `0x0B` does not. (b) `eprom_overprogram_us(..., cap_us=0)` yields **0 us** with no special-case branch, since a positive product always compares greater than a zero cap. | **Phase 144** (informational — not to be re-decided) |
| H6 | The Phase 144 seam: **TEST-01 owns the requirement flip and the consolidated cross-phase accounting; this phase's own suite is its own verification.** Same split as 140-04 vs. TEST-01. | **Phase 144 / TEST-01** |

---

## 13. D-15 evidence inventory — planted-RED transcripts across 141-05, 141-06, 141-08

D-15 requires every new gate to be seen RED on a planted violation before its GREEN is believed.
Tally across the three plans that authored or re-derived a gate this phase (141-07 authored native
behaviour cases against production code but did not plant gate violations, so it contributes 0 to
this specific tally — its own deviations were test-authoring bugs caught by running against real
code, a different D-15-adjacent discipline, recorded in its own SUMMARY):

| Plan | Gate | Planted violations | Runs |
|---|---|---|---|
| 141-05 | `test_exactly_three_protocol_keyed_sites_at_the_pinned_lines` (D-13 re-derivation) | A: fourth protocol-keyed branch inserted; B: `:340` site's protocol read removed | 2 |
| 141-06 | `test_write_path_source_contract_v131.py` (12-leg LOOP-02/LOOP-07 source-contract gate) | Legs 1-9: retry macro, block-mismatch reporter, mask updater, adaptive-growth formula, loop-constructs-present, unclamped pulse_delay, missing safe-helper reroute, tree-wide sweep violation, 16383 boundary shift | 9 |
| 141-08 | `test_loop05_the_loops_own_strobes_disable_the_high_voltage_route`; `test_loop07_no_recorded_us_delay_exceeds_the_avr_ceiling_under_a_real_drive` | Case 2: disable call removed from `eprom_internal_report_budget_failure`; Case 4: raw `delayMicroseconds` reintroduced in `memory_set_data` | 2 |

**Total: 2 + 9 + 2 = 13 planted-RED runs**, matching or exceeding the standard Phase 140 set (12 runs
across three gates, `140-PARAM-TABLE-RECORD.md` §8). Every planted run failed for the reason it was
planted to fail — never an import/decode/path error — and every gate's real-tree run was independently
confirmed GREEN immediately after its own planted-and-restored cycle, per each plan's own SUMMARY.

---

## 14. Suite and env counts — final state at phase close

| Env / suite | Start-of-phase (post Phase 140) | This plan's measurement | CI coverage |
|---|---|---|---|
| `native` | 141 cases / 17 suites | **141 / 17**, PASSED | `build.yml` / `beta-build.yml` |
| `native_nodevtools` | 141 cases / 17 suites | **141 / 17**, PASSED | `build.yml` / `beta-build.yml` |
| `native_trace_v131` | 5 cases / 1 suite, GREEN (D-10, Phase 140 kept it green deliberately) | **6 / 1 (dump build) or 5/1 (normal) — 3 failed, 2 succeeded** | **none** — local run-by-name only; RED expected (D-10) |
| `native_params_v131` | 9 cases / 1 suite | **9 / 1**, PASSED | **none** — local run-by-name only |
| `native_loop_v131` | created plan 141-03 (6 harness cases) | **39 / 1**, PASSED | **none** — local run-by-name only |
| firmware `pytest tests/ -q` | 244 passed (end of Phase 140) | **256 passed** (244 + 12 from 141-06's new gate module) | `build.yml` |
| AVR `uno` / `uno328pb` / `leonardo` | 23954/24004/26016 B flash (Phase 140 tip) | **24424 / 24474 / 26400 B flash**; RAM unchanged at 1573/1579/2014 | `build.yml` / `beta-build.yml` |

---

## 15. Findings register

| ID | Mechanism | Owner | Disposition |
|---|---|---|---|
| F-141-01 | MERGE-05 flash-band policy RED on all three AVR targets (+492/+498/+328 B vs. a 64/64/0 B band) | henols (operator) | **Recorded, accepted, not fixed.** Operator decision predates this plan's dispatch: "Continue; 141-09 records it." §1. |
| F-141-02 | `141-PREDICTIONS.md` P1's point estimate (+30/+30/+18 B) missed by ~14x; the under-budgeted ingredient is the first-live-reference cost of Phase 140's parameter table (~+204 B measured vs. ~70-80 B budgeted) | henols / Phase 144 TEST-08 | Recorded, not fixed. §1.6. |
| F-141-03 | D-11's "record the shrinkage" framing for the D-13 inventory was wrong in direction — tier-2 grew (+3), not shrank; tier-1 held at exactly 3 | n/a (a framing correction, not a defect) | Corrected in this record, §2. |
| F-141-04 | LOOP-03's overprogram path has no loop-integration oracle — proven only as a pure function plus a zero-shipped-row assertion | Phase 146 / CLOSE-04 (candidate: a future `0x07` family split, F-140-05, is the first row that would exercise it) | Recorded, not fixed — no shipped data can exercise this path. §3. |
| F-141-05 | The ERROR band `0xA0..0xBF` has exactly one free slot (`0xBF`) after this phase's three new ids | Phase 142, Phase 143 (whichever claims a new ERROR id next) | Recorded. §5. |
| F-141-06 | `MSG_ERR_WRITE_FAILED` (0xB1) is now emitted by nothing on the 27C path | Phase 143 / HOST-03 | Recorded — host must not expect this id on a rewritten-loop write. §5. |
| F-141-07 | `MSG_INFO_RETRIES` and `DBG_PULSE_DELAY_MISMATCH` are orphaned catalog ids; the latter's wording now contradicts shipped behaviour | Phase 146 / CLOSE-04 (wording only; ids stay assigned) | Recorded, not fixed this phase. §6. |
| F-141-08 | LOOP-06's read-skip is proven on `0x0B` only; `0x07`/`0x08`'s unconditional final pass makes a universal read-skip claim false by design | n/a — LOOP-06 itself is satisfied (it is a pulse-skip requirement); this is a scoped non-claim about an over-broad plan-level claim | Recorded. §7. |
| F-141-09 | `STROBE_KIND_DATA` raw counts are not a sound pulse-count oracle; register-shift writes share the identical strobe shape as a genuine chip-data pulse | Any future native suite extending `test_loop_eprom_v131.cpp` | Recorded as a load-bearing convention (filter by value). §8. |
| F-141-10 | An arithmetic slip (`2 × 50000 − 1 = 99999`) in `141-CONTEXT.md`'s own D-0B worked example; the true worst case is `2 × 49999 = 99998` | henols (documentation accuracy); corrected in `firestarter/CLAUDE.md` | **Corrected in `CLAUDE.md`** during plan 141-05; the plan files (`141-CONTEXT.md`, `141-05-PLAN.md`) still say 99999 and are named here as stale on this one figure. §9. |
| F-141-11 | `test_flash_path_record_sync.py::test_planted_mutation_of_the_real_subset_is_detected` asserts whole-repo `git status --porcelain` emptiness instead of scoping to the one file it tests | Unassigned — orphaned defect, hand-off only | Recorded, not fixed this phase (out of declared scope). §11. |
| F-138-05 (inherited) | `check_size_baseline.py`'s `compare_native` raises an uncaught `KeyError` (not exit 2) for an unrecognized native env; `check_build_warnings.py` exits 2 cleanly for the same condition | henols | Recorded, not fixed (standing D-07 precedent). Neither script was invoked with `native_loop_v131`, `native_trace_v131`, or `native_params_v131` anywhere in this phase. |

---

## 16. What this document is not

This record does not edit `.planning/PROJECT.md`, the posted gh#15 comment, or any of this phase's
own locked context documents (`141-CONTEXT.md`, `141-RESEARCH.md`, `141-PREDICTIONS.md`) to correct
the figures named above — those documents stay as originally committed, per this project's standing
convention, and this record is where the corrections live instead. This record does not attempt to
bring MERGE-05 green — that was foreclosed by the operator's own decision before this plan was
dispatched (§1). This record does not modify `scripts/baseline/size_baseline.json` or
`size_baseline_v131.json` — Phase 144 / TEST-08 owns baseline reconciliation.

---

*Phase: 141-per-byte-program-loop — Plan 09*
*Recorded: 2026-08-10, from this plan's own cold measurement, the eight prior plans' committed
SUMMARY.md artifacts (`141-01-SUMMARY.md` through `141-08-SUMMARY.md`), `141-PREDICTIONS.md`
(commit `4c5d9172`), `141-CONTEXT.md`, and the orchestrator's own pre-dispatch MERGE-05 verdict and
finding set.*

