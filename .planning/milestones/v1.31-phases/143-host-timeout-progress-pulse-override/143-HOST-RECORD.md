# 143-HOST-RECORD: Phase 143 Host Timeout, Progress & Pulse Override — Close Record

**Owner requirements:** HOST-01, HOST-02, HOST-03, HOST-04, HOST-05 — all five discharged **here**, by
this plan (143-10), citing the evidence the nine prior plans (143-01 through 143-09) produced. This
document follows `142-VPP-RECORD.md`'s house shape (numbered sections, a findings register with owners,
an explicit "what this is and is not" framing, a hand-off table).

*Sections 1-6 and 8-11 are written by this plan's Task 3, after every piece of evidence below exists.
Section 7 (this plan's Task 2) is measured and recorded first, so the requirement evidence table and the
non-claims section that follow can cite real numbers rather than predictions.*

---

## 1. Honest headline

**"A long write now reports what it is doing, and a failed byte now reports as a failed byte."**

This is **not** "writes are faster" and **not** "writes are more reliable" — this phase changed neither.
Every proof in this record is **off-hardware**: the host suite (`firestarter_app/tests/`, §7.6) and the
native envs (`pio test`, §7.3), plus the source-contract gates that pin what a native test structurally
cannot see (§8). **No bench evidence exists in this record** — real bar motion on hardware, a real long
write that actually survives without timing out on a physical board, and the per-pulse-overhead
measurement (A1, §4) are all **Phase 145**'s, and Phase 145 must **re-flash** before any bench check
(H4, §10) — BF-1 (§3) means a stale, pre-CAP-02 v1.31 image cannot even connect, so "whatever happens to
be on the board" is not a safe assumption to carry into that phase.

---

## 2. Requirement evidence table

One row per `HOST-01`..`HOST-05`, naming which plans produced the evidence and a command that proves it.
**Two requirements are split across two plans; neither plan alone satisfies its requirement:**

| Requirement | Evidence (plan) | Command / artifact proving it |
|---|---|---|
| **HOST-01** | 143-01 (BF-3-corrected budget arithmetic, native cases), 143-02 (CAP-03 host decode at the computed `ver_end`, byte-layout cases), 143-03 (CAP-02 ported + CAP-03 wired onto the wire, BF-1 closed), 143-04 (the write-path timeout: `_write_block_timeout()`, the 120 s fallback, D-12's negative proof) | `pio test -e native_loop_v131 -f "*test_loop_eprom_v131*"` (budget arithmetic); `pytest tests/test_hw_revision_gate.py -k cap03` (host decode); `pytest tests/test_ack_layout_source_contract_v143.py` (firmware ack layout); `pytest tests/test_write_response_budget.py` (write-path timeout) |
| **HOST-02** | 143-05 (guarded firmware emission + cadence native cases), 143-06 (host DATA branch, offset arithmetic, no-rebuild, no-rewind), 143-08 (the guard's source-contract pin, `leonardo`-only in both directions) | `pio test -e native_loop_v131 -f "*test_loop_eprom_v131*"` (cadence); `pytest tests/test_write_progress.py` (host render); `pytest tests/test_progress_emission_is_leonardo_only.py` (the guard) |
| **HOST-03** | **split — 143-04 AND 143-09; neither alone satisfies it.** 143-04 stops the 10 s transport timeout from firing before a program failure can surface; 143-09 renders that failure as `EpromOperationError` naming the address, plus the disposition hint | `pytest tests/test_write_response_budget.py` (timeout no longer fires first); `pytest tests/test_budget_failure_render.py` (the `0xBD`/`0xBE`/`0xAE` render and hint) |
| **HOST-04** | **split — 143-04 AND 143-07; neither alone satisfies it.** 143-04 lands `write_eprom`'s `pulse_us` transport (rides the existing `pulse-delay` wire key, no new wire field); 143-07 lands the `--pulse-us` CLI flag, its bounds, and the D-17 report line | `pytest tests/test_pulse_us_override.py::test_override_rides_the_db_dict` (transport); `pytest tests/test_pulse_us_override.py::test_override_reaches_the_wire_through_the_cli` (CLI end to end) |
| **HOST-05** | 143-07 (parse-time refusal at exit 2, no port opened, the no-flag regression guard, the write-only scope) | `pytest tests/test_pulse_us_override.py::test_out_of_range_is_refused_at_parse_time` and `::test_refusal_opens_no_port` |

---

## 3. Blocking-finding reconciliations

`143-RESEARCH.md`'s "Blocking Findings" falsified three of `143-CONTEXT.md`'s own decisions before any
code moved. Each is reconciled here: which decision was affected, what the corrected behaviour is, why,
and where it shipped.

### BF-1 — CAP-02's firmware half was absent; D-08 had nothing to append to

**Affected decision:** D-08 (the CAP-03 carrier: "firmware appends bytes, host reads further into
`params_bytes`"). **Falsified premise:** D-08 assumed CAP-02's `[hw_revision u8][ver_len u8][ver bytes]`
tail already existed on this firmware branch — it did not. The v1.31 firmware branch forked at `3085084`,
one commit before `origin/beta`'s CAP-02 port (`13eb350`/`b1737b2`, PR #49) landed, so the shipped ack was
still the bare 2-byte `LOG_OK_ID_U16(MSG_OK_READY, ...)`. **Consequence, measured, not theoretical:** every
command from the v1.31 app against a v1.31 firmware build failed at connect — `_probe_port` raises
`FirmwareOutdatedError` when no firmware identity is reported, and `test_absent_identity_refuses` asserts
that refusal on purpose. **Corrected behaviour:** CAP-02 is **ported**, not invented — verbatim from
`13eb350`, cited by commit hash in the shipping commit's own message — into the **same** pack block as
CAP-03, so the ack's shape stays one length-discriminated blob rather than two independent emits.
**Where it shipped:** 143-03 (`67127e2`), source-contract-pinned by
`tests/test_ack_layout_source_contract_v143.py` (`d9154b0`).

### BF-2 — D-02's emission is undeliverable on `SERIAL_ON_IO` targets; a naive form would have regressed HOST-03

**Affected decision:** D-02 (firmware emits the existing `MSG_DATA_PROGRESS` from inside the per-byte
loop). **Falsified premise:** D-02's own reasoning implies the emission "feeds the host's response
window for free" everywhere — false on `uno`/`uno328pb`, where `rurp_set_programmer_mode()` tears the
UART down for the whole programmer-mode window and the Uno's `rurp_log_id` override defers frames into a
4-slot buffer whose 5th-frame overflow is a **silent drop**. **Consequence, if shipped naively:** a byte
that fails at `max_pulses` would have its `MSG_ERR_MAX_PULSES` frame dropped behind four already-buffered
progress frames, converting a program **failure** (which surfaces correctly on `uno` **today**, without
this phase's changes) into a host **transport timeout** — directly regressing HOST-03 on exactly the
boards D-02 was meant to help. **Corrected behaviour:** the emission (and its `last_emit_ms` state) is
**compiled out**, structurally, via `#ifndef SERIAL_ON_IO` — not a runtime choice, and not one of three
rejected, still-costly alternatives (a runtime `com_mode` accessor, a raised `DEFERRED_LOG_MAX`, or
reserved headroom). **Where it shipped:** 143-05 (`b4f0779`, the guard), pinned mechanically by 143-08's
`tests/test_progress_emission_is_leonardo_only.py` (`9349fce`) — a **source contract**, never behavioural,
because `src/boards/uno_rurp_shield.cpp` compiles in no native environment and the native capture stub
carries no `com_mode` gate.

### BF-3 — D-11's formula under-estimated by up to 2x on a reachable `--pulse-us` value

**Affected decision:** D-11 (the per-byte bound formula, `min(max_pulses x pulse, energy_cap_us)`, plus
an overprogram term of `min(3 x overprogram_factor x pulse, overprogram_cap_us)`). **Falsified premise:**
the shipped per-byte loop increments `accumulated += org_delay` **before** testing
`accumulated >= energy_cap_us`, so the true pulse count is `min(max_pulses, ceil(energy_cap_us /
pulse_us))`, which can exceed D-11's naive division whenever `pulse_us` does not divide `energy_cap_us`
evenly. At `0x0B` / `--pulse-us 49999` (host-legal, firmware-accepted), D-11's literal formula yields
50000 us/byte (one pulse); the real loop needs a **second** pulse, for 99998 us/byte — a budget computed
with D-11's literal form would time out a **working** write at ~51 s, which D-09 names as strictly worse
than a generous ceiling. **Second, independent falsification:** D-11's overprogram term does not match
the shipped `eprom_overprogram_us(pulse_count, pulse_us, factor, cap_us)`, which computes
`factor x pulse_count x pulse_us` clamped at `cap_us` — D-11's literal reading (restating `3 x factor` as
a second multiplier alongside the shipped function's own `factor`) under-estimates 8.3x for the first
future row that sets a non-zero `overprogram_factor`. **Corrected behaviour:** the pulse count **ceils**
(`eprom_worst_pulses`), and the overprogram term is produced by **calling** `eprom_overprogram_us` with
that ceiled count, never by restating its formula. **Where it shipped:** 143-01 (`f1b17cd`,
`include/eprom_budget.h` / `src/proms/eprom_budget.cpp`), proven by six native cases each seen RED under
a named production-code plant (`143-01-SUMMARY.md`'s D-25 Evidence section).

**Presented for confirmation (per Task 3's operator checkpoint, how-to-verify step 2):** both BF-2 and
BF-3 are cases where a CONTEXT decision was **scoped down** or **replaced** rather than shipped as
literally written — D-02 was narrowed to `leonardo`-only delivery, and D-11's formula was replaced with
the corrected arithmetic. Neither narrowing was discretionary; both were forced by evidence gathered
**before** any code moved (`143-RESEARCH.md`'s "Blocking Findings"), and both are cited above with the
exact mechanism and the exact commit.

---

## 4. The padding rule, in prose (D-09)

A host-side reader of the wire cannot see how conservative CAP-03's advertised budget is — the two bytes
on the wire are just a `uint16_t` count of seconds. The rule, stated once here exactly as
`include/eprom_budget.h` states it in the firmware's own source:

```
padded_s = ceil(raw_pulse_only_us / 1e6) * 2 + 2
```

**"Twice the ceil-rounded pulse-only worst case, plus two seconds."** A **multiplier**, not an additive
constant, because the per-pulse fixed overhead scales with pulse **count**, not with block size alone —
at `0x0B` / `--pulse-us 200` the per-byte loop runs 250 pulses x 1024 bytes = 256 000 iterations, and the
`[ASSUMED]` (`143-RESEARCH.md` "Budget Arithmetic and Encoding" A1; **not measured** — Phase 145 may
record the real figure) ~20-60 us-per-pulse overhead adds roughly 15 s on top of a 51.2 s pulse-only
budget — about 30%. A flat `+N` seconds could never absorb that at every pulse width, which is why the
firmware's own multiplier form is load-bearing, not cosmetic.

What `raw_pulse_only_us` counts: pulse widths only, times the block's byte count. What the `x2+2` padding
absorbs, that the raw figure never counts: the once-per-block VPE settle (500 ms), the per-pulse pre-pulse
settle, the verify read strobe, the shift-register writes behind every address change, the `0x07`/`0x08`
final full-block verify pass, and the serial transport cost of one chunk (~41 ms per 1024 B at 250000
baud). The "+2" makes a one-second floor automatic, so no separate floor clamp is needed anywhere in this
budget. The host applies **no multiplier of its own** (D-09) — it uses the advertised value verbatim,
because only the firmware knows all of the above; a host-side multiplier would leave two sides
contributing to the final number, and a spurious timeout would need both examined.

---

## 5. Non-claims

At minimum, carrying forward every non-claim named across this phase's decisions and findings:

1. **D-06, both dimensions.** Intra-block write progress is emitted on the **EPROM path only** — flash,
   EEPROM (`0x0D`), SRAM and every other write family keep today's block-granularity progress and
   today's silent-stall behaviour — **and** delivered on **`leonardo` only**: on `SERIAL_ON_IO` targets
   (`uno`, `uno328pb`) the emission is **compiled out**, structurally (BF-2, §3), not by choice.
2. **No bench claim about any protocol is made here.** Every proof in this record is off-hardware (§1,
   §7.3, §7.6). Real bar motion, a real long write surviving on a physical board, and the per-pulse
   overhead (A1) are Phase 145's.
3. **The `#ifndef SERIAL_ON_IO` guard is proven only by a source contract, never behaviourally.**
   `src/boards/uno_rurp_shield.cpp` (the file implementing `com_mode`, the strong `rurp_log_id()`
   override, and the 4-slot `deferred_log` buffer) is compiled in **no** native environment, and the
   native `rurp_log_id` capture stub carries **no** `com_mode` gate — a native test cannot distinguish
   "delivered" from "would have been delivered if the UART were not torn down." Only a source scan
   (`tests/test_progress_emission_is_leonardo_only.py`) can pin this guard.
4. **`native_trace_v131` is RED by design (D-24) and this phase added zero frames to it.** Confirmed
   fresh this session (§7.3): the `Was` values (91/115/59) are byte-identical to the pre-phase tip,
   because that fixture pins `millis()` to `AlwaysReturn(0)`, so 143-05's time-gated emission structurally
   cannot fire there. Phase 144 / TEST-06 will find **zero** D-02-attributable strobes when it re-derives
   this fixture.
5. **The D-10 fallback's residual gap.** With **no** budget advertised, `0x07`/`0x08` above
   `120 / (25 x 1024) = 4687 us` on a **Leonardo** and `120 / (25 x 512) = 9375 us` on an **Uno** can
   still time out (the board-specific figures come from each board's own `DATA_BUFFER_SIZE`: 1024 B on
   Leonardo, 512 B on Uno). **BF-1 corrects D-10's own wording here:** the realistic absent-advertisement
   case is a **released beta** firmware (has CAP-02, lacks CAP-03) — or a v1.31 build after the CAP-02
   port but before CAP-03 lands — **not** a mid-milestone v1.31 build carrying neither, which cannot
   connect at all and so never reaches this residual gap in the first place. Cited verbatim from the
   shipped code comment, `firestarter_app/firestarter/eprom_operations.py:109-125`.
6. **`--pulse-us`'s `1..65535` bound is minipro parity, not a wire-type constraint.** `pulse-delay` is
   parsed by the firmware's `extract_long` into an **unclamped** `uint32_t`
   (`firestarter/src/json_parser.c`) — a value above 65535 is reachable on the wire independently of this
   flag. Reconciling that gap is **H3, Phase 146 / CLOSE-04's**, not this phase's; this record and
   `firestarter/CLAUDE.md`'s new ack section both state the provenance rather than implying a type limit.
7. **No host-side warning exists for a `--pulse-us` in `50001..65535` on `0x0B`.** D-16 leaves the
   `0x0B`-only over-cap case to the firmware's existing pre-flight refusal (`MSG_ERR_PULSE_TOO_WIDE`,
   `0xAE`, firing **before any high voltage is enabled**) rather than mirroring `energy_cap_us` host-side,
   which would contradict D-07's whole point (no datasheet-derived value duplicated host-side).
8. **`MSG_ERR_WRITE_FAILED` (`0xB1`) is a dead id on this family (D-20).** Nothing on the 27C write path
   emits it any more (whole-tree grep, zero references under `src/`, re-confirmed fresh this session:
   zero matches), and no host code keys on it — confirmed by 143-09's non-vacuous source-contract leg
   (`tests/test_budget_failure_render.py::test_no_host_path_expects_write_failed_on_27c`).
9. **`0xBF` remains the sole free `0xA0..0xBF` ERROR slot.** This phase spent no new message id — CAP-03
   rides `MSG_OK_READY`'s existing variable-length param blob (zero `messages.toml` diff, zero codegen
   run), and the budget-failure hint (D-19) reuses `MSG_ERR_MAX_PULSES`/`MSG_ERR_ENERGY_CAP`/
   `MSG_ERR_PULSE_TOO_WIDE`, all pre-existing.

---

## 6. The D-01 correction, recorded (not applied here)

`ROADMAP.md`'s Phase 143 framing reads, verbatim: **"Depends on: Phase 138 ... Independent of Phases
140-142 (different repo)"**, and the milestone's matching sequencing-spine sentence states that Phase 143
"can run in parallel with them."

**This is factually wrong for the shipped decision.** This phase depends on **Phase 141's** per-byte
loop (the thing D-02's emission is placed inside) and **Phase 140's** parameter table (the thing
`eprom_block_budget_s` reads `max_pulses`/`energy_cap_us`/`overprogram_factor`/`overprogram_cap_us`
from) — and it is **dual-repo**, not confined to `firestarter_app`. Hand-off H2 (`141-LOOP-RECORD.md`
§12, and `141-CONTEXT.md` D-12) predicted exactly this and required it be named **before** Phase 143
planned, not discovered during it: HOST-02's own precedent is a firmware pattern, so choosing real
intra-block progress (D-02) necessarily put part of this phase in `firestarter/`.

**Recording the correction is this phase's obligation. Amending `ROADMAP.md` / `PROJECT.md`'s prose is
Phase 146 / CLOSE-04's**, alongside the C3, F-140-05 and F-140-07 corrections already queued there
(`143-CONTEXT.md` D-01). `git -C /workspaces diff --stat -- .planning/ROADMAP.md .planning/PROJECT.md`
is confirmed empty as part of this same task (see Part B below) — neither file's prose was touched here.

---

## 7. Measured size and gate verdicts

All AVR figures below were measured **cold**: `pio run -t clean -e <env>` followed by a single
uninterrupted `pio run -e <env>`, one target at a time, in this plan's own Task 2 session. The native
warning figures were measured cold too — `.pio/build/native` and `.pio/build/native_nodevtools` were
removed before invoking `check_build_warnings.py --rebuild`, so the recorded native totals are the COLD
figure `size_baseline.json`'s own `meta.warm_vs_cold_correction` distinguishes from a WARM re-run (COLD
1166 vs WARM 998 for both pinned native envs) — this measurement reproduced **1166**, confirming it is
the cold figure, not an accidentally-warm one.

### 7.1 Cold flash/RAM, all three AVR targets

```
--- uno ---
RAM:   [========  ]  76.8% (used 1573 bytes from 2048 bytes)
Flash: [========  ]  77.0% (used 24824 bytes from 32256 bytes)
--- uno328pb ---
RAM:   [========  ]  77.1% (used 1579 bytes from 2048 bytes)
Flash: [========  ]  76.8% (used 24874 bytes from 32384 bytes)
--- leonardo ---
RAM:   [========  ]  78.7% (used 2014 bytes from 2560 bytes)
Flash: [========= ]  93.8% (used 26906 bytes from 28672 bytes)
```

These figures are **byte-identical** to the post-143-08 tip (143-08 touched no firmware source; this
plan's own Task 1 is a docs-only `CLAUDE.md` commit) — cold and the prior incremental measurements agree
exactly, so no incremental-build artifact was hiding anything.

| Target | `size_baseline.json` baseline (Phase 124) | Measured (this plan, cold) | Delta vs. Phase-124 baseline |
|---|---|---|---|
| `uno` flash | 23954 B | 24824 B | **+870 B** |
| `uno328pb` flash | 24004 B | 24874 B | **+870 B** |
| `leonardo` flash | 26016 B | 26906 B | **+890 B** |
| `uno` / `uno328pb` / `leonardo` RAM | 1573 / 1579 / 2014 B | 1573 / 1579 / 2014 B | **+0 / +0 / +0 (exact)** |

RAM is unmoved on all three targets. `leonardo` headroom: **28672 − 26906 = 1766 B** remaining against the
hard build-failure ceiling, and **2130 − 1766 = 364 B** of F-142-08's hand-off headroom consumed this
phase. **`leonardo` still fits — D-22's whole bar is satisfied.**

**This phase's own contribution, isolated from the pre-existing (Phase 140-142) drift:**

| Target | Phase-142 tip (cold, `142-VPP-RECORD.md` §1.1) | This phase's own delta | Attributed to |
|---|---|---|---|
| `uno` flash | 24568 B | **+256 B** | 143-03 (CAP-02 port + CAP-03 wire-up, one pack block) |
| `uno328pb` flash | 24618 B | **+256 B** | 143-03, identical to `uno` |
| `leonardo` flash | 26542 B | **+256 B** (143-03) **+108 B** (143-05) = **+364 B** | 143-03 (CAP-02+CAP-03) and 143-05 (the guarded progress emission) |
| every target, 143-01/143-08/143-10 Task 1 | — | **+0 B** | 143-01 (arithmetic added but uncalled, `--gc-sections`-eliminated), 143-08 (Python-only gate, no firmware source), 143-10 Task 1 (docs-only) |

143-03's own SUMMARY records this identically: "this plan spent 256 B of F-142-08's 2130 B hand-off on
all three AVR targets (uno/uno328pb/leonardo all +256 B identically)." 143-05's own SUMMARY records the
`leonardo`-only +108 B, with `uno`/`uno328pb` confirmed byte-identical (proving the `#ifndef SERIAL_ON_IO`
guard genuinely excludes the code there, not merely an assertion about source text).

**RESEARCH's `[ASSUMED]` estimates, verdict:**

- **A2 (CAP-02 ~+34 B):** does **not** hold as a standalone prediction of the measured total, and
  cannot be cleanly isolated from it. BF-1's recommended disposition — and 143-03's own design decision
  — packed CAP-02 and CAP-03 into **one** `_ready[]` buffer and **one** `LOG_OK_ID_BYTES` emit, landed in
  one commit, specifically so the ack's shape is a single length-discriminated blob rather than two
  independent emits. The measured **+256 B** on every target is therefore CAP-02 **plus** CAP-03 **plus**
  the previously dead-code-eliminated `eprom_budget.cpp` functions becoming referenced (143-01 added them
  uncalled, at +0 B, precisely because nothing referenced them yet) — not CAP-02 alone. A2's ~34 B figure,
  cited from the upstream `13eb350` commit message, describes a narrower change than what this branch
  actually shipped, and the record states this rather than implying A2 was falsified by a like-for-like
  comparison that was never possible once BF-1's port-in-one-block disposition was chosen.
- **A3 (the emission 40-120 B on `leonardo`):** **held.** The measured `leonardo`-only contribution from
  143-05's guarded `MSG_DATA_PROGRESS` emission is **+108 B** — inside the stated 40-120 B range, and the
  `uno`/`uno328pb` zero-delta measurement is the direct, measured proof (not merely an assertion) that the
  `#ifndef SERIAL_ON_IO` guard costs nothing on those targets.

### 7.2 Warnings, cold

```
$ rm -rf .pio/build/native .pio/build/native_nodevtools
$ python3 scripts/check_build_warnings.py --rebuild
PASS: uno: macro_redefinition=0 (== 0), uno328pb: macro_redefinition=0 (== 0), leonardo: macro_redefinition=0 (== 0), native: total warnings=1166 (== watermark 1166), native_nodevtools: total warnings=1166 (== watermark 1166)
$ echo $?
0
```

All three AVR targets: `macro_redefinition=0`, satisfying the stricter `avr_rule: "== 0"`. Both pinned
native envs: **1166**, exactly at the watermark with **zero headroom**, unmoved from the post-143-08 tip
(143-01 through 143-08 never moved this figure either — the phase's native-side additions are all pure,
Arduino-free C, contributing no new `pgmspace.h`-vs-`ArduinoFake` redefinition). No new warning of any
kind was introduced by this phase, on any target.

### 7.3 Native envs

| Env | Measured this plan | Baseline / prior tip | Gate coverage |
|---|---|---|---|
| `native` | **141 test cases: 141 succeeded**, 17 suites | unmoved since `size_baseline.json` (Phase 124) and every intervening phase | `check_size_baseline.py` (default byte-identity mode), CI (`build.yml`/`beta-build.yml`) |
| `native_nodevtools` | **141 test cases: 141 succeeded**, 17 suites | unmoved, identical to `native` | same |
| `native_loop_v131` | **79 test cases: 79 succeeded**, 2 suites (`test_loop_eprom_v131` 47 + `test_vpp_eprom_v131` 32) | unmoved since the post-143-08 tip | **No gate asserts these counts and no CI leg of either repository runs this env** (D-14 of `142-CONTEXT.md`, carried). This record is the only place a later reader finds them. |
| `native_params_v131` | **9 test cases: 9 succeeded**, 1 suite | unmoved since Phase 140 | **No gate, no CI leg** — same caveat as `native_loop_v131`. |
| `native_trace_v131` | **6 test cases: 3 failed, 2 succeeded** (`ERRORED` overall) | unmoved since the post-142-04 tip | **RED by design (D-24).** No gate asserts it; no CI leg runs it. **Not re-frozen here.** |

**`native_trace_v131`, verbatim, both sides recorded:**

```
$ pio test -e native_trace_v131
test_smoke_setup_leaves_both_recorders_clean	[PASSED]
test_smoke_timing_hook_fires_for_delay_and_delaymicroseconds	[PASSED]
test_protocol_0x07_am27c512_capture_is_sound_and_deterministic: Expected 198 Was 91. 0x07 AM27C512 DIP28_27512	[FAILED]
test_protocol_0x08_am27c020_capture_is_sound_and_deterministic: Expected 221 Was 115. 0x08 AM27C020 DIP32_27C020	[FAILED]
test_protocol_0x0B_am2716_capture_is_sound_and_deterministic: Expected 201 Was 59. 0x0B AM2716 DIP24_2716	[FAILED]
Program received signal SIGQUIT (Quit)
6 test cases: 3 failed, 2 succeeded
```

Every `Was` value (91/115/59) is **byte-identical** to the value recorded at the post-143-03 and
post-143-05 tips — **this phase added zero frames to the frozen trace**, exactly as D-24 requires:
`native_trace_v131`'s harness pins `millis()` to `AlwaysReturn(0)`, so 143-05's time-gated emission (whose
predicate is `(millis() - last_emit_ms) >= EPROM_PROGRESS_EMIT_INTERVAL_MS`) can never fire there — a
frozen clock never advances past the interval. Phase 144 / TEST-06, which owns the eventual freeze and the
attributable diff, will therefore find **zero** D-02-attributable strobes when it re-derives this fixture.

**Never passed to either baseline script this session:** `native_loop_v131`, `native_params_v131`, or
`native_trace_v131` — confirmed by inspection of every command run in this task. An unrecognized native
env raises an uncaught `KeyError` in `check_size_baseline.py` (F-138-05, inherited, not fixed) and exits 2
from `check_build_warnings.py`. Neither was risked.

### 7.4 Baseline gate (`check_size_baseline.py`)

**The bare, no-argument invocation** (the literal form this plan's own `<verify>` block names) does not
compare anything and is not the substantive verdict:

```
$ python3 scripts/check_size_baseline.py
FAIL: no envs compared -- supply --avr-log/--native-log or --rebuild (never-vacuous guard: a comparator that compares nothing must not pass)
$ echo $?
1
```

This is the script's own documented "never-vacuous guard" (its own module docstring: "zero envs were
compared... not bypassed by `--policy`") — a tool-usage condition, not a flash-regression finding. It is
recorded here for completeness because the plan's own shorthand verify block names exactly this
invocation, but it is **not** one of the three permitted RED reasons (MERGE-05, the OD-2 CAP-02 drift, or
this phase's own measured growth) and is not treated as a fourth, unattributed reason — it simply supplies
no data to attribute. The substantive verdict is the `--rebuild` invocation below, matching the
established convention every firmware plan in this phase (143-01, 143-03, 143-05, 143-08) already used:

```
$ python3 scripts/check_size_baseline.py --rebuild
FAIL:
  uno: flash_used baseline=23954 observed=24824
  uno328pb: flash_used baseline=24004 observed=24874
  leonardo: flash_used baseline=26016 observed=26906
$ echo $?
1
```

**Every RED reason enumerated and attributed:**

| Target | `flash_used` delta | Attribution |
|---|---|---|
| `uno` | +870 B | +614 B — MERGE-05/OD-2 drift already RED and operator-accepted through the Phase-142 tip (`142-VPP-RECORD.md` §1.5, the script's own default-baseline invocation), unmoved by this phase's own measurement, **plus** +256 B — this phase's own measured growth (143-03's CAP-02 port + CAP-03 wire-up), against a baseline deliberately left un-updated (D-22) |
| `uno328pb` | +870 B | identical composition to `uno`: +614 B pre-existing + 256 B this phase |
| `leonardo` | +890 B | +526 B — MERGE-05/OD-2 drift through the Phase-142 tip, **plus** +256 B (143-03) **plus** +108 B (143-05's guarded progress emission) = +364 B this phase's own growth |

**No RAM mismatch and no native mismatch appear anywhere in this output** — only `flash_used` lines, on
all three AVR targets, confirming RAM and both pinned native envs' case/suite/status facts still match
`size_baseline.json` exactly. **No reason outside the three permitted categories appeared.**
`git diff --exit-code -- scripts/baseline/size_baseline.json` is clean — the baseline was not edited, per
D-22.

### 7.5 Firmware pytest

```
$ python3 -m pytest tests/ -o addopts="" -q
292 passed in 12.70s
```

**292 passed** — the post-143-08 count, unchanged by this plan's own docs-only Task 1 commit (confirmed:
this run was made immediately after committing `CLAUDE.md` alone, satisfying L-1). Reconciled against the
phase's own running total: 272 (post-142-07) → 282 (143-03, `+10`: `test_ack_layout_source_contract_v143.py`)
→ 292 (143-08, `+10`: `test_progress_emission_is_leonardo_only.py`) → **292** (143-01/143-05/143-09/this
plan's Task 1 add zero Python-pytest-collected tests — their additions are native Unity C++ cases, or, for
143-09, a `firestarter_app`-only change).

Both new gate modules are confirmed included and green, alongside every other "must stay green" module
named by this plan:

```
$ python3 -m pytest tests/test_ack_layout_source_contract_v143.py tests/test_progress_emission_is_leonardo_only.py tests/test_protocol_branch_inventory.py tests/test_hv_routing_source_contract_v142.py tests/test_write_path_source_contract_v131.py tests/test_golden_trace_identity.py tests/test_golden_trace_identity_eprom_v131.py tests/test_flash_path_record_sync.py -o addopts="" -q
108 passed in 1.70s
```

### 7.6 Host (`firestarter_app`, read-only this phase)

From `/workspaces/firestarter_app`, `.venv/ci-replica/bin/python` (verified `Python 3.11.15`, L-3):

```
$ .venv/ci-replica/bin/python -m pytest tests/ --cov=firestarter --cov-fail-under=70 -o addopts=""
1578 passed, 1 warning in 229.49s (0:03:49)
Required test coverage of 70% reached. Total coverage: 82.92%
30 snapshots passed.
```

**1578 passed**, coverage **82.92%** (≥ 70% floor). Reconciled against the **1547** phase-start baseline
(`138-04-HOST-BASELINE.md`), every added test attributed to its plan:

| Plan | Host tests added | Running total |
|---|---|---|
| phase start (`138-04-HOST-BASELINE.md`) | — | 1547 |
| 143-01 | 0 (firmware-only plan) | 1547 |
| 143-02 | +5 (`test_hw_revision_gate.py`'s CAP-03 decode cases) | 1552 |
| 143-03 | 0 (firmware-only plan) | 1552 |
| 143-04 | +10 (`test_write_response_budget.py` 6 + `test_pulse_us_override.py` 4) | 1562 |
| 143-05 | 0 (firmware-only plan) | 1562 |
| 143-06 | +6 (`test_write_progress.py`; Test 5's negative split into two functions, plan-permitted) | 1568 |
| 143-07 | +6 (`test_pulse_us_override.py` extended in place, 4→10) | 1574 |
| 143-08 | 0 (firmware-only plan) | 1574 |
| 143-09 | +4 (`test_budget_failure_render.py`) | 1578 |
| **Total** | **+31** | **1578** |

`1547 + 5 + 10 + 6 + 6 + 4 = 1578` — the measured figure, exactly. No discrepancy.

```
$ ruff check firestarter/ tests/
All checks passed!
$ ruff format --check firestarter/ tests/
134 files already formatted
$ .venv/ci-replica/bin/python tools/check_mypy_watermark.py
checked 136 source files
mypy errors: 33 (watermark: 35)
$ echo $?
0
```

`ruff check` and `ruff format --check` both clean. The mypy watermark gate **exits 0** — 33 errors, 2
below the 35 watermark, unmoved from the 143-04/143-06/143-07/143-09 baseline (this phase's own new code
is fully typed; the 33 pre-existing errors are untouched). **Exit 0 is a genuine pass, not the exit-2
"cannot be trusted" condition.**

`git -C /workspaces/firestarter status --porcelain` was confirmed clean both immediately before this sweep
and immediately after — no L-6/L-1b deselection was needed, and `firestarter_app`'s own
`git status --porcelain` shows only the same eight pre-existing untracked files present at session start
(`.coverage`, `.planning/config.json`, `SECURITY.md`, four datasheets, `write_test_port.sh`) — **nothing
was written or committed in `firestarter_app` by this plan**, matching its read-only role in
`commits_land_in`.

---

## 8. D-25 inventory

Every new gate leg and native case authored in this phase, the plan that owns it, and a pointer to the
SUMMARY holding its planted-RED/RED-before-GREEN and GREEN transcripts. **No leg in this phase's nine
prior plans required a locator-only repair** — every plant or pre-implementation RED landed on the
intended leg (or, in four documented cases, on the intended leg **plus** an honest, stronger-than-required
spillover onto a sibling leg sharing the same extraction helper) on the **first** attempt.

| Plan | New legs / cases | Evidence form | Transcript pointer |
|---|---|---|---|
| 143-01 | 6 native Unity cases (`test_budget_uncapped_energy_cap_is_not_a_cap_at_zero`, `test_budget_pulse_count_ceils_because_the_loop_tests_after_it_increments`, `test_budget_0x0b_at_49999us_is_99998us_per_byte_not_50000`, `test_budget_overprogram_term_is_zero_for_factor_zero_and_clamped_for_factor_three`, `test_budget_zero_pulse_width_never_divides_by_zero`, `test_budget_block_seconds_matches_the_shipped_rows_and_is_padded`) | Planted-violation: 5 plants against `eprom_budget.cpp` | `143-01-SUMMARY.md` §"D-25 Evidence" |
| 143-02 | 5 pytest cases (`test_decode_cap03_budget_at_short_identity_length`, `test_decode_cap03_budget_at_long_identity_length_proves_ver_end_is_computed`, `test_decode_cap02_ack_without_a_budget_tail_leaves_the_budget_none`, `test_decode_legacy_two_byte_ack_leaves_both_identity_and_budget_none`, `test_decode_implausible_cap03_budget_is_clamped_away`) | Planted-violation: 4 plants against `serial_comm.py` | `143-02-SUMMARY.md` §"D-25 Evidence" — **Plant A's finding**: both fixture cases went RED together (not the predicted one-RED/one-GREEN asymmetry), caused by a coincidental shared 4-byte prefix between the two mandated identity strings; recorded honestly, not massaged to match the prediction |
| 143-03 | 10 pytest legs in `tests/test_ack_layout_source_contract_v143.py` (7 layout + 3 self-protection) | Planted-violation: 8 plants (7 named + 1 empty-scratch-file plant) against a scratch copy of `src/firestarter.cpp` | `143-03-SUMMARY.md` §"D-25 Evidence" — Plants 2, 4, 6 and 8 produced honest spillover onto a sibling leg sharing the same extractor, each documented as a **stronger**, not weaker, result |
| 143-04 | `tests/test_write_response_budget.py` (6 tests), `tests/test_pulse_us_override.py` (4 tests, transport half) | RED-before-GREEN (Tests 4/5 strengthened with a same-drive contrast assertion, to avoid a vacuous pre-implementation pass) | `143-04-SUMMARY.md` §"D-25 Evidence" |
| 143-05 | 2 native Unity cases (`test_progress_emits_when_the_clock_advances_past_the_interval`, `test_progress_emits_nothing_when_the_clock_does_not_advance`) | Planted-violation: 4 plants against `src/proms/eprom.cpp` | `143-05-SUMMARY.md` §"D-25 Evidence" — Plant 4 produced a different specific assertion than predicted (the floor check, not a monotonicity check), proving the same placement-sensitivity property via a different route |
| 143-06 | `tests/test_write_progress.py` (6 tests; Test 5's negative split into its own function, per the plan's own explicit allowance) | RED-before-GREEN | `143-06-SUMMARY.md` §"D-25 Evidence" |
| 143-07 | `tests/test_pulse_us_override.py` extended 4→10 (6 new `CliRunner` cases) | RED-before-GREEN (2 of the 6 are honest, permanently-passing controls — structurally incapable of failing pre-implementation — documented as such rather than forced RED) | `143-07-SUMMARY.md` §"D-25 Evidence" |
| 143-08 | 10 pytest legs in `tests/test_progress_emission_is_leonardo_only.py` (7 positive + 3 self-protection) | Planted-violation: 10 distinct plants (8 named + both directions of the `platformio.ini` env-scope leg + both sub-variants of the empty-scan-target leg) | `143-08-SUMMARY.md` §"D-25 Evidence" — **zero locator-only repairs across all 10 plants**, explicitly stated in that SUMMARY |
| 143-09 | `tests/test_budget_failure_render.py` (4 tests, including D-20's dead-id leg) | RED-before-GREEN (Test 4 pairs a positive non-vacuity assertion with the negative absence check, specifically to avoid a standing-true vacuous leg) | `143-09-SUMMARY.md` §"D-25 Evidence" |

**Totals, cross-checked against §7.5 and §7.6's own counts:**
- **8 new native Unity cases** (firmware, `pio test`): 6 (143-01) + 2 (143-05) — folded into `native_loop_v131`'s 71→79 growth.
- **20 new firmware-repo Python pytest legs** (two new gate modules): 10 (143-03) + 10 (143-08) —
  accounts for the firmware pytest suite's 272→292 growth (§7.5) exactly.
- **31 new `firestarter_app` Python pytest cases**: 5 (143-02) + 10 (143-04) + 6 (143-06) + 6 (143-07,
  net new) + 4 (143-09) — accounts for the host suite's 1547→1578 growth (§7.6) exactly.
- **Grand total: 59** new test legs/cases authored this phase.

---

## 9. Findings register

| ID | Finding | Owner | Disposition |
|---|---|---|---|
| F-143-01 | `pio` invocations abort when run with cwd `/workspaces` (the meta repo), because the meta repo holds an untracked `platformio.ini` with a duplicate `[platformio]` section (L-2, named in this plan). Every `pio` invocation in this phase ran with cwd `/workspaces/firestarter`. | henols | Named, not fixed. |
| F-143-02 | F-141-11, carried forward: `tests/test_flash_path_record_sync.py` asserts the **whole firmware repo**'s `git status --porcelain`, not just the one file it exists to test. Still orphaned. Bit this phase too (L-1): `firestarter/CLAUDE.md` had to be committed before running the full firmware pytest suite. | Unassigned | Recorded, not fixed. |
| F-143-03 | **New this phase (L-1b).** The **host** suite has the same coupling, on the *other* repo: `firestarter_app/tests/test_py32_flash_map_host.py::TestLinkerScriptParityFailsClosedOnBadInput::test_planted_mutated_config_origin_is_detected` asserts `_git_porcelain(FW_ROOT) == ""` for the sibling firmware repo. An untracked file in `firestarter` is enough to turn it RED. Extends F-141-11/F-143-02's blast radius across the repo boundary. This plan's `CLAUDE.md` commit landed before the host sweep specifically to avoid tripping it (confirmed clean, §7.6). | Unassigned | Recorded, not fixed. |
| F-143-04 | F-138-05, carried forward: `check_size_baseline.py`'s `compare_native` raises an uncaught `KeyError` for an unrecognized native env name (exit 1, a false regression signal); `check_build_warnings.py` exits 2 for the same condition. Neither script was invoked with `native_loop_v131`, `native_params_v131`, or `native_trace_v131` anywhere in this phase (confirmed, §7.3). | henols | Recorded, not fixed. |
| F-143-05 | **The corrected D-15 rationale.** `143-CONTEXT.md`'s D-15 justifies the `--pulse-us` parse-time refusal as firing "before `AppContext` builds" — **false**: Click's `cli()` group callback runs first, before `write()`'s own parameters are even type-converted, so `AppContext` already exists by the time a parse-time refusal fires. The guarantee that actually holds (and that HOST-05 needs) is narrower and still true: nothing in `cli()` or `AppContext` construction opens a serial port — port-opening is confined to `SerialCommunicator.find_and_connect`, reachable only from inside `write_eprom`'s own body, which a parse-time refusal never reaches. Corrected in `write()`'s own docstring and `test_refusal_opens_no_port`'s docstring (143-07). | This record (143-10) | Corrected; no further action needed. |
| F-143-06 | **The `start_time` reset citation has drifted twice.** `143-CONTEXT.md`/`143-RESEARCH.md` cite the reset that fires for a decoded binary id frame at `serial_comm.py:448`/`:513` — wrong on both counts (`:448` sits inside the ring-fence *comment* block, not a code line at all; `:513` is the "flush preceding text before a binary frame" reset, a different branch). `143-PATTERNS.md` corrected this to `:502` — accurate against the **pre-execution** file. Re-verified fresh this session against the file as it stands after 143-02's edit (which inserted the CAP-03 decode arm earlier in the same file, shifting every later line): the same logical reset (immediately after `yield response` inside the decoded-frame branch) now sits at **`serial_comm.py:567`**, not `:502`. | This record (143-10) | Recorded as `:567`, freshly re-verified — a third link in the same citation-drift chain `143-CONTEXT.md`'s own "current line numbers — re-locate before relying on them" caveat anticipates. |
| F-143-07 | **No standing cross-repo wire-layout parity gate exists** between the firmware's `MSG_OK_READY` pack block and the host's `_decode_id_frame` arm. Each side is independently pinned (143-03's source contract; 143-02's byte-layout cases) but nothing compares the two sides directly — `RESEARCH` Open Question 4 named this gap, and it is exactly BF-1's own shape (a two-repo protocol with nothing comparing the sides, which is how BF-1 went unnoticed for three milestones). | Phase 144 / TEST-07 | Handed off, not built here. |

---

## 10. Hand-offs

| # | Item | Owner |
|---|---|---|
| H1 | `native_trace_v131`'s re-freeze and the frozen-vs-new attributable diff. This phase added **zero** frames to the fixture (confirmed, §7.3/§5.4) — the re-freeze will find zero D-02-attributable strobes. | **Phase 144 / TEST-06** |
| H2 | A byte-layout parity assertion for CAP-03 — the standing cross-repo gap BF-1 exposed and F-143-07 names (nothing today compares the firmware's pack block against the host's decode arm directly). | **Phase 144 / TEST-07** |
| H3 | MERGE-05 and the `size_baseline.json` update. Inherits this phase's own measured growth (+870 B `uno`/`uno328pb`, +890 B `leonardo`, §7.1/§7.4) alongside the pre-existing Phase 140-142 drift (+614/+614/+526 B, `142-VPP-RECORD.md` §1.5) — both attributed, neither reconciled here (D-22). | **Phase 144 / TEST-08** |
| H4 | All bench evidence: real bar motion (HOST-02's user-visible claim, never proven on hardware by this phase), a real long write surviving on a physical board, and the per-pulse-overhead measurement (A1, `[ASSUMED]` ~20-60 us/pulse, never measured, §4). **Must re-flash before any bench check and record which image was on the board** — BF-1 means a stale, pre-CAP-02 v1.31 image cannot even connect, so "whatever is on the board" cannot be assumed close enough. | **Phase 145** |
| H5 | The `--pulse-us` documentation entry. This phase ships the flag; the doc chapter is Phase 146's, per `143-CONTEXT.md`'s own phase-boundary note. | **Phase 146 / CLOSE-03** |
| H6 | The `ROADMAP.md`/`PROJECT.md` prose correction (D-01, §6); H3's unclamped `extract_long` on `pulse-delay` (non-claim 6, §5); `DBG_PULSE_DELAY_MISMATCH`'s stale "retrying with increased pulse delay" wording (F-141-07, contradicts a fixed-width-pulse loop); `MSG_INFO_RETRIES`'s orphan status. | **Phase 146 / CLOSE-04** |

---

## 11. Deferred ideas carried forward

The full `143-CONTEXT.md` `<deferred>` list, with each item's owner or its explicit no-owner status:

- **Fixing `set_progress`'s rebuild-on-differing-total** (`eprom_operations.py:268-270`) — a latent defect
  for every caller (closes and re-creates the tqdm bar, zeroing `current_step`, whenever a frame's total
  differs from the bar's). D-04 routes around it because the fix is shared code on the read and
  blank-check paths. **No owner outside v1.31.**
- **Intra-block progress for the non-EPROM write families** (flash `0x05`, EEPROM `0x0D`, SRAM, …) — D-06's
  explicit non-claim (§5, item 1). Each has its own write path; none gets a heartbeat from this phase.
  **No owner.**
- **A combined byte-count-OR-time cadence** (D-03's rejected third option) — better bar smoothness on fast
  writes, for more flash and a second code path. **Revisit only if a bench run shows the time-bounded
  cadence looks jerky at 100 us — no owner today.**
- **Host-side warning for a `--pulse-us` above `0x0B`'s energy cap** — D-16 left this to the firmware's
  existing pre-flight refusal (§5, item 7). **Becomes free if CAP-03 ever advertises the cap itself — no
  owner today.**
- **Reconciling H3** (`extract_long` parses `pulse-delay` into an unclamped `uint32_t`) — **Phase 146 /
  CLOSE-04**, alongside F-140-05 and F-140-07 (H6 above).
- **Correcting the roadmap's "Phase 143 is independent of 140-142" prose** and the matching
  sequencing-spine sentence — **Phase 146 / CLOSE-04** (D-01, §6, H6 above).
- **`DBG_PULSE_DELAY_MISMATCH`'s stale wording and `MSG_INFO_RETRIES`'s orphan status** — F-141-07,
  **Phase 146 / CLOSE-04** (H6 above), wording only.
- **`native_trace_v131` re-freeze and the frozen-vs-new attributable diff** — **Phase 144 / TEST-06** (H1
  above).
- **Cross-phase flash/RAM reconciliation and the `size_baseline.json` update** — **Phase 144 / TEST-08**
  (H3 above).
- **Fixing F-141-11 / F-143-02/F-143-03** (`test_flash_path_record_sync.py` and its host-side analog
  asserting whole-repo porcelain) — still orphaned and unassigned.
- **Fixing F-138-05 / F-143-04** (`check_size_baseline.py`'s uncaught `KeyError` on an unknown native env)
  — inherited, accepted, not fixed. **Owner `henols`.**
- **`--pulse-us` on any command other than `write`** — D-18, a decided out-of-scope, not a true deferral:
  nothing else emits a program pulse.

**Reviewed todos, none folded** (seven todos matched by keyword; the top four scored 0.9 on bare-word
overlap alone and belong to other families): "Skip VPP error/warning checks when VPP is unused" (deferred
again, `142-CONTEXT.md`'s reasoning still applies, out-of-scope for v1.31); "FM1608 byte 0 write never
lands" (a different family's write-path defect, noted as a testing caution only); "`CONFIG_VERSION` is not
bumped when a calibration default changes" (EEPROM config migration, backlog 999.1's territory); "Prove
the PlatformIO dev-tools build flag fails CLOSED" (a build-flag question this phase adds no dev-gated
surface to); "AT28C256 write-path failure (gh#20)" (protocol `0x0D`, explicitly out of D-06's scope);
"avrdude MCU-detection fallback for blank-chip / wrong-firmware recovery" (firmware-install territory,
untouched here).

---

*Phase: 143-host-timeout-progress-pulse-override — Plan 10*
*Recorded: 2026-08-13, from this plan's own measurement and gate runs, the nine prior plans' committed
SUMMARY.md artifacts (`143-01-SUMMARY.md` through `143-09-SUMMARY.md`), `143-CONTEXT.md`,
`143-RESEARCH.md`, `143-PATTERNS.md`, `143-VALIDATION.md`, and `142-VPP-RECORD.md` for the cross-phase
pairing.*
