# 142-VPP-RECORD: Phase 142 High-Voltage Routing — Close Record

**Owner requirements:** VPP-01, VPP-02, VPP-03, VPP-04 — all four discharged **here**, by this plan
(142-07), citing the evidence the six prior plans (142-01 through 142-06) produced. **Status:** the
cold measurement this document reconciles was taken by this plan's own Task 2, on all three AVR
targets, in one uninterrupted `pio run -t clean` + `pio run` pair per target. **The MERGE-05 flash-band
policy is RED and stays RED** — the same disposition the operator made for Phase 141, extended here
without re-litigation — and `native_trace_v131` is **RED by design** (D-17), not fixed, not silenced.
Every other gate this phase touches is green. VPP-01 through VPP-04 are marked complete in
`.planning/REQUIREMENTS.md` and `.planning/ROADMAP.md` by this same plan's Task 3, by hand edit, after
every piece of evidence below exists.

This document follows `141-LOOP-RECORD.md`'s house shape (numbered sections, a findings register with
owners, an explicit "what this is and is not" framing, a hand-off table).

---

## 1. Cold flash/RAM measurement, all three AVR targets — measured fresh this plan

### 1.1 Cold measurement (verbatim, this plan's own Task 2)

Each target was measured via `pio run -t clean -e <env>` followed by a single uninterrupted
`pio run -e <env>`, one target at a time:

```
--- uno ---
RAM:   [========  ]  76.8% (used 1573 bytes from 2048 bytes)
Flash: [========  ]  76.2% (used 24568 bytes from 32256 bytes)
--- uno328pb ---
RAM:   [========  ]  77.1% (used 1579 bytes from 2048 bytes)
Flash: [========  ]  76.0% (used 24618 bytes from 32384 bytes)
--- leonardo ---
RAM:   [========  ]  78.7% (used 2014 bytes from 2560 bytes)
Flash: [========= ]  92.6% (used 26542 bytes from 28672 bytes)
```

These figures are **byte-identical** to plan 142-04's own (incremental) measurement and to the
orchestrator's pre-dispatch warm measurement — cold and warm agree exactly at this tip, so no
incremental-build artifact was hiding anything.

### 1.2 Paired against the Phase 141 tip — this phase's own increment

| Target | Phase 141 tip (cold, `141-LOOP-RECORD.md` §1.1) | Phase 142 tip (cold, this plan) | Delta (this phase only) |
|---|---|---|---|
| `uno` flash | 24424 B | 24568 B | **+144 B** |
| `uno328pb` flash | 24474 B | 24618 B | **+144 B** |
| `leonardo` flash | 26400 B | 26542 B | **+142 B** |
| `uno` / `uno328pb` / `leonardo` RAM | 1573 / 1579 / 2014 | 1573 / 1579 / 2014 | **+0 / +0 / +0 (exact)** |

RAM is unmoved on all three targets — every artifact this phase adds (the resolver, the wrapper split,
the composite masks, the revision-gated preserve arm) is either `PROGMEM`/`.text` or stack-only, never
static `.data`/`.bss`.

### 1.3 Leonardo headroom and the Phase 143 consequence

**Leonardo headroom: 28672 − 26542 = 2130 B.** This is **unchanged since the 142-04 tip** — plans
142-05 and 142-06 touched no file under `src/` or `include/` (both confirmed by `git diff --exit-code`
in their own SUMMARYs), so nothing after 142-04 could have moved it. Against the Phase 141 tip's
2272 B, Phase 142 alone narrowed the margin by 142 B. **The 28672 B ceiling is a build failure, not a
gate — Phase 143 still has to fit inside whatever headroom remains,** and 2130 B is a tighter number
than any earlier phase in this milestone handed forward.

### 1.4 Measured deltas vs. research's per-option estimates

`142-RESEARCH.md` §"Gate and Budget Posture" labelled four design-option costs as **estimates**,
explicitly "not measured, because measurement requires editing source" — this section is where they
are corrected against the real number rather than inherited.

| Option | Estimate | Measured contribution |
|---|---|---|
| Composites as `#define` (`rurp_pinout.h`) | 0 B | Not separately measurable (header-only, zero until referenced) — consistent with 0 B |
| Single-exit wrapper, both `eprom_write_init` + `eprom_write_execute` | −20 to +60 B combined ("likely near-neutral") | Not separable from the resolver by this measurement (LTO — see below) |
| Route resolver replacing two duplicated branches | −30 to −80 B (a **plausible shrink**) | Did **not** shrink — see disagreement below |
| Runtime revision gate in `mem_util_calculate_top_address_register` | +20 to +45 B | Not separable from the wrapper/resolver by this measurement (LTO) |

**The disagreement, stated plainly:** summing every option's own most-pessimistic-for-growth bound
(wrapper at its stated maximum +60 B, the resolver contributing **zero** shrink — its own worst case
inside the stated range is still a decrease, −30 B, never phrased as a possible increase — and the
revision gate at its stated maximum +45 B) ceilings the combined estimate at **+75 B**. The measured
net increment is **+142 to +144 B — roughly 1.9× that pessimistic ceiling.** The disagreement is real,
not a rounding matter, and it is the same shape of miss `141-LOOP-RECORD.md` §1.6 already named once
this milestone (there, the actual overrun was ~14× the point estimate) — a second instance of this
project's per-feature flash estimates running optimistic against LTO'd reality.

**Partial, LTO-limited attribution (offered, not authoritative):** `avr-nm --print-size` against the
cold `uno` ELF shows `eprom_write_execute` at 992 B, `eprom_check_vpp` at 524 B, `eprom_hv_route_mask`
split into a 132 B `.part.1` cold fragment (GCC's own cold-path outlining, so this is not the resolver's
full cost), and `eprom_internal_report_budget_failure` at 110 B. The two `static` inner bodies
(`eprom_internal_write_execute_body`, `eprom_internal_write_init_body`) do **not** appear as distinct
linked symbols at all — LTO has folded each into its single public caller — which is exactly the same
`__gnu_lto_slim` opacity `141-LOOP-RECORD.md` §1.5 already documented for `eprom_overprogram_us` and
`eprom_params_for`. A clean before/after per-symbol diff would require checking out the 142-04-tip
commit and rebuilding under identical flags, which this task does not require and was not performed.
**Recorded as measured, not reconciled** — Phase 144 / TEST-08 owns the full cross-phase attribution
and inherits this partial data rather than re-deriving it from nothing.

### 1.5 MERGE-05 verdict — verbatim, both anchors, RED, not fixed

**D-16 disposition (carried from Phase 141, unchanged): measure cold, record, MERGE-05 stays RED.** No
shrink ladder was run. No baseline JSON was edited — confirmed:
`git diff --exit-code -- scripts/baseline/size_baseline.json scripts/baseline/size_baseline_base01.json`
exits 0, both files byte-unchanged.

**(a) The literal instructed invocation — no `--baseline` flag, the script's own default:**

```
$ python3 scripts/check_size_baseline.py --policy merge05 --rebuild
FAIL:
  uno: flash_used baseline=23954 observed=24568 delta=+614 exceeds MERGE-05 uno-class band of 64 B
  uno328pb: flash_used baseline=24004 observed=24618 delta=+614 exceeds MERGE-05 uno-class band of 64 B
  leonardo: flash_used baseline=26016 observed=26542 delta=+526 exceeds MERGE-05 leonardo band of 0 B
$ echo $?
1
```

**(b) A named, worth-recording discrepancy:** the script's own default baseline file,
`scripts/baseline/size_baseline.json`, was last touched by commit `72a6844`
("feat(124-10): re-baseline the live default to the post-landing tree") — **Phase 124, an entirely
different, older milestone (v1.24), predating v1.31's own fork by more than a dozen phases.** It has
not moved since, and its `avr_targets` figures (23954/24004/26016) happen to match PREP-03's own
Phase-138 baseline evidence figures exactly, byte for byte — the tree's flash usage did not move
between Phase 124's close and v1.31's fork. `141-LOOP-RECORD.md` §1.2, by contrast, invoked the same
script with an **explicit** `--baseline scripts/baseline/size_baseline_base01.json` override — a
*different*, slightly earlier Phase-124 freeze (commit `609d6a7`, `23932/23976/26072`) — to produce its
own reported `+492/+498/+328` verdict. Reproducing that same explicit-baseline invocation here, for
direct comparability with the Phase 141 record:

```
$ python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json --rebuild
FAIL:
  uno: flash_used baseline=23932 observed=24568 delta=+636 exceeds MERGE-05 uno-class band of 64 B
  uno328pb: flash_used baseline=23976 observed=24618 delta=+642 exceeds MERGE-05 uno-class band of 64 B
  leonardo: flash_used baseline=26072 observed=26542 delta=+470 exceeds MERGE-05 leonardo band of 0 B
$ echo $?
1
```

Both invocations are RED; neither is fixed; neither baseline file was edited. **The two verdicts differ
only in which frozen Phase-124 anchor they compare against — both anchors predate this milestone and
neither has ever been updated for it, by design (D-16: read-only all phase, and in practice untouched
since Phase 138).** This dual-anchor discrepancy is itself logged as a finding (§15) for Phase 144 /
TEST-08, who owns whichever reconciliation follows.

**Disposition, in the operator's own terms:** continue; this record notes it. Neither figure is
softened, and no reduction was attempted — D-16 forbids both the shrink ladder and the baseline edit.

### 1.6 Warning watermark — verbatim, actual number against the ceiling

```
$ python3 scripts/check_build_warnings.py --rebuild
INFO: native: total warnings observed=998 is 168 below watermark 1166 -- re-measure and lower total_watermark in size_baseline.json; do not guess a new figure
INFO: native_nodevtools: total warnings observed=998 is 168 below watermark 1166 -- re-measure and lower total_watermark in size_baseline.json; do not guess a new figure
PASS: uno: macro_redefinition=0 (== 0), uno328pb: macro_redefinition=0 (== 0), leonardo: macro_redefinition=0 (== 0), native: ..., native_nodevtools: ...
$ echo $?
0
```

**Stated precisely, not just "pass":** the recorded native warning total is **998**, comfortably 168
below the **1166** watermark *as measured today*. The "zero headroom" language `142-CONTEXT.md` D-16
and this plan's own dispatch notes carry refers to the **policy's own design**: the watermark ceiling
(1166) was set with no built-in growth allowance baked in above whatever gets measured, not to a claim
that today's actual count sits at the ceiling. Both statements are true simultaneously and are not in
tension: the *policy* has zero designed headroom above the number it is eventually set to; *today's
measured count* has 168 units of numeric slack under the currently-recorded 1166. This phase did not
move either number. `uno`/`uno328pb`/`leonardo` all report `macro_redefinition=0`, matching the
`EPROM_HV_*` prefix's own collision-avoidance design (D-07's block comment names this explicitly).

---

## 2. Env and suite counts — final state at phase close

| Env / suite | Start of phase (post 141-09) | This plan's measurement | CI coverage |
|---|---|---|---|
| `native` | 141 cases / 17 suites | **141 / 17**, PASSED | `build.yml` / `beta-build.yml` |
| `native_nodevtools` | 141 cases / 17 suites | **141 / 17**, PASSED | `build.yml` / `beta-build.yml` |
| `native_loop_v131` | 39 cases / 1 suite (`test_loop_eprom_v131` only) | **71 / 2 suites** — `test_loop_eprom_v131` (39) + new `test_vpp_eprom_v131` (32) | **none** — local run-by-name only (D-14) |
| `native_params_v131` | 9 cases / 1 suite | **9 / 1**, PASSED, unmoved | **none** — local run-by-name only |
| `native_trace_v131` | 6 cases / 1 suite, RED by design (D-17, unmoved since 142-04) | **6 / 1 — 3 failed, 2 succeeded**, RED by design | **none** — local run-by-name only; RED expected |
| New: `tests/test_hv_routing_source_contract_v142.py` | did not exist | **16 legs**, all PASSED, folded into the firmware pytest total below | `build.yml` (it is a plain pytest module under `tests/`) |
| firmware `pytest tests/ -o addopts="" -q` | 272 passed (post plan 142-06) | **272 passed**, unmoved (plan 142-06's +16 already landed; this plan's own docs-only Task 1 commit adds none) | `build.yml` |
| AVR `uno` / `uno328pb` / `leonardo` flash | 24568 / 24618 / 26542 B (142-04 tip, incremental) | **24568 / 24618 / 26542 B**, cold, byte-identical | `build.yml` / `beta-build.yml` |

**Never passed to either gate script this session:** `native_loop_v131`, `native_params_v131`, or
`native_trace_v131` — confirmed by inspection of every command run this plan (§1.5, §1.6 above); an
unrecognized native env raises an uncaught `KeyError` in `check_size_baseline.py` (F-138-05, inherited,
not fixed) and exits 2 from `check_build_warnings.py`. Neither was risked.

---

## 3. `native_trace_v131` — the expected RED (D-17), both sides recorded

```
$ pio test -e native_trace_v131
test_protocol_0x07_am27c512_capture_is_sound_and_deterministic: Expected 198 Was 91. 0x07 AM27C512 DIP28_27512   [FAILED]
test_protocol_0x08_am27c020_capture_is_sound_and_deterministic: Expected 221 Was 115. 0x08 AM27C020 DIP32_27C020 [FAILED]
test_protocol_0x0B_am2716_capture_is_sound_and_deterministic: Expected 201 Was 59. 0x0B AM2716 DIP24_2716        [FAILED]
Program received signal SIGQUIT (Quit)
6 test cases: 3 failed, 2 succeeded
```

**Labelled explicitly: expected RED, by design, not re-frozen.** Phase 141's D-10 left this fixture RED
by design; Phase 142's D-17 (carried, restated) forbids re-freezing it here; Phase 144 / TEST-06 owns
the eventual freeze and the frozen-vs-new diff. This phase changed the strobe stream again (D-01, D-04,
D-09, D-10), so the failure **values** moved once, on the `0x08` row only, during plan 142-04, and have
been unmoved since (142-05 and 142-06 touched neither `eprom.cpp` nor `memory.cpp`):

| Row | Phase 141 tip (`Was`) | 142-03 tip (`Was`) | 142-04 tip through this plan (`Was`) | `Expected` (frozen fixture) |
|---|---|---|---|---|
| `0x07` | 91 | 91 | **91** (unmoved) | 198 |
| `0x08` | 119 | 119 | **115** (−4, first move this milestone, D-04's clear-removal) | 221 |
| `0x0B` | 59 | 59 | **59** (unmoved) | 201 |

Both sides — the frozen `Expected` values and every `Was` value this phase produced, at every plan tip
— are now recorded so Phase 144 / TEST-06 has the complete before/after picture without re-deriving it.

---

## 4. Every green gate, listed by name

So this record does not read as though only the RED gates were checked: `pio test -e native`
(141/17, PASSED), `pio test -e native_nodevtools` (141/17, PASSED), `pio test -e native_loop_v131`
(71/2 suites, PASSED), `pio test -e native_params_v131` (9/1, PASSED), the whole firmware
`pytest tests/ -o addopts="" -q` (272 passed), and all three `pio run -t clean` + `pio run` links
(`uno`, `uno328pb`, `leonardo`, all SUCCESS). `check_build_warnings.py --rebuild` exits 0 (PASS). The
only two non-green results in this entire phase-close session are the two named, expected, and
D-16/D-17-governed REDs above (§1.5, §3).

---

## 5. The qualified SC1

`ROADMAP.md`'s Phase 142 SC1 reads: *"`0x07` and `0x08` route through the regulator + VPE-to-VPP
dropping path and `0x0B` through the direct legacy path, with the selection driven by the table's
`vpp_path` column rather than a separate switch."*

**This record does not restate that flat.** It is satisfied by D-01/D-02 **on Rev 2-class hardware**
(`REVISION_2_0`/`_2_1`/`_2_2`/`_2_3`) — proven by plan 142-05's route-strobe cases, including the
resolver's own truth table — and **explicitly not on Rev 0 or Rev 1**, where the drop bit and
`CTRL_ADDRESS_LINE_16` share a physical line (`rurp_hw_rev_utils.h:30-31`, verified sound in research's
"Checked and found sound" table) and today's stripping is **deliberately kept** — plan 142-05's own
`test_vpp01_route_0x08_on_rev1_still_strips_the_drop_bit` proves the negative directly, and it is the
load-bearing case since Rev 1 carries no `eprom_check_vpp` refusal of its own (unlike Rev 0's
`MSG_WARN_REV0_VPP_UNSUPPORTED`). `0x0B`'s direct path is unqualified — it takes the direct route on
every revision, proven by plan 142-05's Group R case.

---

## 6. The permitted headline and the forbidden claims (D-03)

**Permitted:** `eprom_check_vpp()` and the write path now apply the **same routing** — a
firmware-correctness claim proven off hardware, directly, in the emitted control-register stream (plan
142-05's measure-versus-apply equality case, with a planted violation reproducing the exact
pre-142-04 divergence: `Expected 129 Was 128`, the drop-bit-sized gap D-03 names).

**Forbidden, and not made anywhere in this record or in the reconciled `CLAUDE.md`:** a claim that
`0x08`'s high voltage is now silicon-correct or "fixed"; any AM27C020 claim; any `support_status`
graduation. `0x08` is bench-opportunistic this milestone (`PROJECT.md`'s own inventory) and AM27C020 is
a known-marginal stress case regardless of this phase's change — v1.18 Phase 99 measured write #1 at
60 of 64 bytes and write #2 at 0 of 64, so it would be a poor pass/fail oracle even if a bench attempt
were made, which it was not.

---

## 7. The VPP-04 premise correction (D-13)

VPP-04's own requirement wording ("re-verified against the **existing** gate rather than assumed
intact") presumes a refusal-by-message-id gate already existed for the EPROM path. **That premise does
not hold — verified by grep, before any test was written:** `MSG_ERR_VPP_HIGH` / `MSG_WARN_VPP_HIGH`
appeared in **no** test anywhere in this tree prior to plan 142-03. Two reasons compound the gap:
`test_val_eprom.cpp:74` pins `handle->vpp_mv = 0` against a `0`-returning stub specifically so the
over-voltage compare can never fire (a **named vacuity**, not an oversight); and `test_flash_intel_vpp`
is a different protocol family (`0x10`, not EPROM) and, per research correction C-2, runs in **no**
PlatformIO environment and aborts mid-run (`SIGABRT`) before its own SAF-04 case is ever reached.

**This phase authored the gate** (plan 142-03: four legs — refusal by id, no-route-left-asserted with a
paired non-vacuity control, the `FLAG_FORCE` downgrade, and an in-range negative control) rather than
pointing at a gate belonging to another protocol family. VPP-04 is discharged by **authoring plus
recording this correction**, not by re-verifying something that was never there.

---

## 8. Every non-claim (carried forward from `142-VALIDATION.md` and `142-RESEARCH.md`)

1. **`0x08` silicon behaviour after the route change** — bench-only, deliberately not attempted this
   phase (D-03).
2. **That the drop resistor produces ~13 V** — no native suite reads an ADC anywhere in this tree;
   `rurp_read_voltage_mv()` is a mock in every host-side suite.
3. **Any timing claim.** `delay()` and `delayMicroseconds()` are unstubbed ArduinoFake free functions;
   the timing recorder stores the **arguments** a call was made with, never how long anything actually
   took. A trace diff proves *which* delay was requested, never the elapsed time.
4. **C-4's logical-versus-physical non-claim.** On Rev 2-class hardware, logical `CTRL_ADDRESS_LINE_18`
   and logical `CTRL_VPP_P1_ENABLE` are the **same physical bit**, `0x08` (`rurp_pinout.h:121,127`).
   Clearing the logical P1 bit does not guarantee physical de-assertion whenever logical A18 happens to
   be set. This is **not reachable from a 27C write today** — `using_p1_as_vpp()` makes
   `mem_util_remap_address_bus` skip setting bit 21 (the address bit that would otherwise set logical
   A18) whenever VPP is routed through P1 — but the composite's guarantee is stated as **logical**, not
   physical, precisely because that reachability analysis could change under a future protocol.
5. **D-11's `vpp_line` non-claim.** The disable guarantee covers **control-register routes only**. The
   address-latch `vpp_line` bit (`mem_util_remap_address_bus`, `memory.cpp:418-420`) ignores
   `read_write` and is asserted on reads too; clearing it on write-path exit would be a read-path
   behaviour change, out of this milestone's scope. It is cleared by `command_done()` at operation end
   and by nothing else.
6. **That `command_done()` runs on the real AVR abort path is not provable off hardware.** The timeout
   arm (`firestarter.cpp:169-171`) depends on `millis()`, which sits outside every native suite's reach.
   `command_done()`'s zeroing behaviour is proven only as a **source contract** (plan 142-06): its body,
   extracted by brace-matching, is asserted to contain the three zeroing writes, and both dispatch call
   arms are asserted to reach it — never exercised behaviourally on a real timeout.

---

## 9. L-12 — the enforcement caveat, stated rather than implied

D-03's non-claim discipline above is **prose-enforced only** this phase. No v1.31 claim gate exists yet:
CLOSE-01's `check_permitted_claims.py` is Phase 146's, and Phase 139 shipped only a
Phase-139-scoped script with no reach into this phase's artifacts. A future automated check is not
assumed to exist merely because this record is careful; that would itself be an overclaim.

---

## 10. The four discretionary decisions, each with its reason

1. **D-07's placement.** The two `EPROM_HV_*` composites live in `include/rurp_pinout.h`, beside the
   `CTRL_*` bits they are built from, rather than in `eprom.h` / `eprom_params.h`. Both `eprom.cpp` and
   `memory.cpp` already include it, and a composite beside its own bits cannot drift from them. This
   **establishes** a bitwise-OR composite `#define` form in that header — zero precedent existed there
   before plan 142-01.
2. **D-12's function boundary.** The disable guarantee is carried by `eprom_write_execute` (mandatory —
   every leaking exit lived there, including the previously-uncovered `MSG_ERR_VERIFY` final-pass exit)
   and `eprom_write_init` (defensive — neither of its own exits leaked a route before this phase).
   **Not** widened to `eprom_erase_execute`, `eprom_check_chip_id_execute`, or `eprom_get_chip_id` as
   standalone commands: each already clears everything it asserts with no intervening `return`, and
   `PROJECT.md:189-190`'s out-of-scope line licenses a VPP-validation-adjacent change only where
   required for safe shared cleanup — none of the three needed it.
3. **The resolver's name, signature and exposure.** `eprom_hv_route_mask(firestarter_handle_t* handle)`
   is **exposed** via `include/eprom.h` (matching the `eprom_overprogram_us` precedent) rather than kept
   file-static — the only way to drive its `(protocol, ctrl_flags) → mask` truth table directly,
   including the fail-closed `row == NULL` arm that no drive through `configure_eprom` can ever reach
   (that function already refuses an unrecognized protocol before an operation pointer is installed).
4. **The plan decomposition.** `memory.cpp` (142-02) landed **before** `eprom.cpp` (142-04) — the
   reverse order would briefly leave `0x08` with no drop route surviving at all, since 142-04's removal
   of the explicit `pins >= 32` clear only becomes a fix once 142-02's revision-gated preserve exists to
   catch the bit (L-3). All `eprom.cpp` edits landed in **one plan, one task, one commit** (142-04) so
   the D-18 blob-SHA-pinned gate went RED exactly once, for one reason (L-2) — see §13's correction to
   the precedent this choice is credited to.

---

## 11. Seven open questions — four resolved during planning, three settled by the operator

**Resolved during planning (no operator input required):**

- **Q1 — rewrite or delete the inverted LOOP-08 case?** REWRITE in place, renamed
  `test_vpp01_dip32_drop_bit_survives_the_block_on_rev2_class` (plan 142-04). Its `v0` drop-bit-SET
  assertion survives as the non-vacuity partner for the new positive claim.
- **Q4 — where does the resolver live?** EXPOSE via `include/eprom.h` (see §10 item 3).
- **Q6 — fold, delete, or leave `eprom_internal_ensure_regulator_enabled`?** DELETE. Zero callers
  anywhere in the tree, `--gc-sections` already reclaimed its 0 B, and it duplicated the resolver's own
  once-per-block guard — exactly the divergence risk VPP-03 exists to remove.
- **Q7 — source-contract pytest or a behavioural oracle for `command_done()`?** SOURCE CONTRACT,
  labelled as such (plan 142-06). A behavioural oracle would need `firestarter.cpp` inside a native
  `build_src_filter`, which collides with `main()` and would require a seventh env — forbidden by D-14.

**Settled by the operator, as amendments recorded in `142-CONTEXT.md`:**

- **The conditional wrapper (C-1 / D-10 amended).** The wrapper's disable is **conditional** on
  `handle->response_code == RESPONSE_CODE_ERROR`, not unconditional as D-10 originally stated. The
  tiebreaker was a test that already existed and already passed:
  `test_loop05_a_successful_block_does_not_disable_the_route`, whose own comment anticipated this exact
  phase. An unconditional disable would re-arm the once-per-block guard and re-pay `delay(500)` per
  block — roughly 64 s added to a 64 K Uno write.
- **The revision-alone preserve gate (D-02 amended).** `mem_util_calculate_top_address_register`'s new
  preserve arm keys on hardware revision alone, not on `handle->protocol` (which would have created a
  fourth tier-1 protocol-keyed site, violating TABLE-05) and not on a new `handle` field (RAM cost for a
  blast radius a proof already closes). The widened nominal reach (every 32-pin protocol on Rev
  2-class, not just `0x08`) is **paid for with a proof, not an argument**: plan 142-02's 32-pin
  **non-EPROM** (`0x10`) byte-identity case, asserting the recorded control-value sequence is unchanged
  before and after.
- **The no-designator jumper framing (D-01 amended / C-7).** The phase cites only that a physical jumper
  controls pin-1 VPP routing on a 32-pin part, in the operator's own verbatim framing, without naming a
  designator or asserting a net. The documentation contradiction this project carries about that jumper
  (`firestarter/doc/SHIELD-REVISIONS.md:65` calls it the VPP-bypass jumper; `.planning/v1.7-SHIELD-REVS.md`
  places the same designator inside the hardware-revision detect divider chain) is **logged as a
  finding here** (§15), for a documentation owner, not resolved.

---

## 12. The D-15 evidence inventory — planted-RED transcripts across plans 142-01 through 142-06

| Plan | Gate / leg | Planted violations (named) | Runs |
|---|---|---|---|
| 142-01 | Read-back mismatch-window self-check | 1: removed the `mismatch_from` branch in `host_stubs.cpp` | 1 |
| 142-02 | `(pins, revision)` preserve truth table + 32-pin non-EPROM baseline | P1 (unconditional preserve, no revision gate); P2 (a stray OR into `top_address` instead of `mask`) | 2 |
| 142-03 | VPP-04 refusal gate (legs a–d) + VPP-03 pre-rewrite baselines (Case E / Case I) | V1 (widened the over-voltage compare tolerance); V2 (early `return` after the ERROR assignment); V3 (disabled the `FLAG_FORCE` fork); V4 (widened the erase-path assert mask); V5 (narrowed the chip-id clear) | 5 |
| 142-04 | D-18 golden re-derivation + re-pinned tier-1 locator | A (a fourth `handle->protocol==0x08` branch inserted in a scratch copy); B (removed the surviving tier-1 site's protocol read) | 2 |
| 142-05 | VPP-03 measure/apply equality + VPP-02 write-path exits | 1 (re-introduced the deleted `pins >= 32` clear); W1 (removed the wrapper's `ERROR`-gated clear); W2 (made the wrapper unconditional) | 3 |
| 142-06 | `command_done()` source contract + VPP-03 structural legs | 3 (one per zeroing register); 2 (one per dispatch call arm); 4 (eprom.cpp structural: duplicate resolver definition, deleted call site, reintroduced protocol-equality predicate, reintroduced hand-rolled OR sequence) | 9 |

**Total: 1 + 2 + 5 + 2 + 3 + 9 = 22 planted-RED runs.** Compared against Phase 140's 12 and Phase
141's 13, this phase's evidence base is the largest of the three, consistent with VPP-02/VPP-03's
"prove every exit, prove no divergence" shape demanding more individually-named plants than a
single-mechanism rewrite. Every planted run failed for the reason it was planted to fail — never an
import/decode/path error — and every gate's real-tree run was independently confirmed green immediately
after its own planted-and-restored cycle, per each plan's own SUMMARY.

**Several of plan 142-03's legs were green on arrival and proved nothing until planted, per research
correction C-3:** `eprom_check_vpp()`'s over-voltage refusal already de-energised every path but the
pre-assert Rev-0 return before this phase touched anything (V1/V3 above exist precisely to turn those
green-on-arrival legs into genuine regression oracles), and the pre-rewrite `CMD_ERASE` /
`CMD_CHECK_CHIP_ID` byte-identity baselines are pure equality assertions that would pass on any change
that happens not to move a bit (V4/V5 above). D-15 does not accept a green-on-arrival leg's GREEN as
evidence by itself — every one of them was planted-RED first.

**One leg is named unplanted, by decision, not oversight:** plan 142-06's include/-wide
composite-count leg (its own Coverage item 10). Reaching it with a planted duplicate `#define` would
require either a third, glob-scoped environment seam — contradicting that module's own fixed two-seam
contract (`FIRESTARTER_HV_SCAN_DISPATCH_SOURCE` and `FIRESTARTER_HV_SCAN_EPROM_SOURCE`, explicitly
"both scan targets" per that plan's own acceptance criteria) — or a transient edit to the real
`include/rurp_pinout.h`, which the plan explicitly forbade given the header's zero-headroom warning
watermark (§1.6). The other nine planted fixtures in that plan already exceed its own "at least nine"
floor, so the reasoned non-demonstration costs nothing in coverage confidence.

---

## 13. The D-18 inventory movement — and a correction to its own precedent

**Before** (Phase 141 tip, `141-LOOP-RECORD.md` §2): **27 total** = **3 tier-1** (protocol-keyed, lines
70/190/340) + 24 tier-2.

**After** (plan 142-04's re-derivation, by its own live extractor, never hand-typed): **26 total** =
**1 tier-1** (line 70 only — the `configure_eprom` pulse-fallback switch, untouched by D-01) + 25
tier-2. **Net: tier-1 3 → 1 (4 removed, 3 added), total 27 → 26 (net −1).**

- **Removed (4):** the two identical `:190`/`:340` tier-1 predicates
  (`protocol == 0x0B || is_flag_set(FLAG_VPE_AS_VPP)`), both retired as tier-1 sites by the resolver
  (D-05); the explicit `:217-219` `pins >= 32` drop-bit clear (D-04); and the dead
  `eprom_internal_ensure_regulator_enabled` guard's own tier-2 site (Q6).
- **Added (3):** the `FLAG_VPE_AS_VPP` check inside the resolver, demoted from tier-1 to a tier-2
  `ctrl_flags` site (D-06); and the two wrappers' `response_code == RESPONSE_CODE_ERROR` gates.
- **Not materialized, corrected from the plan's own prediction:** the resolver's `row == NULL`
  fail-closed arm and its `vpp_path` comparison were predicted as up to two more new tier-2 sites; the
  live extractor excludes both, because each references only the local `row` variable, never
  `handle->...` — exactly as the same extractor already excluded the pre-existing, structurally
  identical `row == NULL` check inside `eprom_write_execute` before this phase touched anything. The
  golden and locator were derived from this measured truth, not the plan's own prediction.

**The re-pinned locator is strictly stronger, not merely relocated:** `test_exactly_one_protocol_keyed_site_at_the_pinned_line`
(renamed from `test_exactly_three_protocol_keyed_sites_at_the_pinned_lines`) now pins a single literal,
`[70]`, replacing `[70, 190, 340]` — a tighter assertion surface, proven armed in both directions by two
child-process planted-violation transcripts (§12, plan 142-04's A and B).

**Correcting the precedent this phase's one-commit design is credited to, rather than repeating the
flattering version.** Both `142-CONTEXT.md` D-18 and its own L-2 landmine state that Phase 141
"confined all `eprom.cpp` edits to one plan so the gate went RED once, for one reason." That is true of
one **plan**, not one **commit** — and the "RED once" half did not happen either: `141-04` alone landed
**three** commits (`aeac4e7`, `ef0e075`, `3504e50`), and the golden re-derivation landed in a
**different** plan, `141-05`, in two more (`876ce35`, `86128af`) — leaving the D-18 gate RED across
**five commits and two plans**, exactly as `ROADMAP.md`'s own Phase 141 block records ("from `141-04`
until `141-05` re-derives it"). Phase 142 deliberately **tightened** that precedent to **one commit**:
plan 142-04 is a single task specifically because GSD commits per task unconditionally
(`gsd-executor.md:410`), so a one-commit constraint mechanically requires a one-task plan. Verified
against the pre-task anchor: `git rev-list --count 4a890b9..01836fc` == `1`. This record states the
correction rather than the flattering misattribution — repeating an unverified "one commit" claim about
Phase 141 is the exact failure mode D-13 (§7 above) already cost this milestone once.

---

## 14. D-08 — no new message id claimed

`0xBF` remains the **sole free slot** in the `0xA0..0xBF` ERROR band after this phase — every value
`0xA0` through `0xBE` was already occupied before Phase 142 began (F-141-05), and nothing in this
phase's route-resolution or disable-guarantee work needed a new refusal id (D-02's Rev 0/1 gate and
D-06's flag-versus-table question were both resolved without one, precisely to avoid contesting this
slot with Phase 143). `0xBF` is still available to Phase 143.

---

## 15. Findings register

| ID | Mechanism | Owner | Disposition |
|---|---|---|---|
| F-142-01 | C-7: the pin-1 VPP bypass jumper this project documents is described two contradictory ways (`doc/SHIELD-REVISIONS.md:65` calls it the VPP-bypass jumper; `.planning/v1.7-SHIELD-REVS.md:37,41-44` places the same physical connector inside the hardware-revision detect divider chain) | Documentation owner, unassigned | **Logged, not resolved.** D-01/D-02 needed only two independently-verified facts (the drop bit is a level selector; that jumper is not-present on Rev 0/1), neither of which requires resolving the contradiction or naming the connector's designator. |
| F-142-02 | C-2: `test_flash_intel_vpp` runs in **no** PlatformIO environment and `SIGABRT`s mid-run (case #2) before its own SAF-04 case is ever reached — `platformio.ini:72-74`'s own comment claiming a teardown-only abort does not hold today | henols / whoever next reuses this suite's shape | Recorded, not fixed. This phase copied the SAF-04 **shape** (record `(bit,state)` pairs; assert the last write is route-clear) for VPP-04's gate, never its interception mechanism (C-5). |
| F-142-03 | MERGE-05 RED on all three AVR targets, measured two ways: +614/+614/+526 B against the script's own default (Phase-124) anchor, and +636/+642/+470 B against the explicit BASE-01 anchor `141-LOOP-RECORD.md` used | Phase 144 / TEST-08 | **Recorded, accepted, not fixed** (D-16). Neither baseline JSON was edited. |
| F-142-04 | `native_trace_v131` expected RED, values moved once this phase (0x08 row: `Was 119` → `Was 115`, a decrease of 4, first movement this milestone) and unmoved since 142-04 | Phase 144 / TEST-06 | **Expected RED by design** (D-17). Both the frozen `Expected` values and every `Was` value this phase produced are recorded (§3). |
| F-142-05 | Native warning watermark: 998 measured against a 1166 ceiling with no designed growth allowance above whatever the watermark is eventually set to | henols | Recorded, not moved. The script's own INFO output recommends re-measuring and lowering the watermark; this phase does not do so (out of scope). |
| F-142-06 | F-141-11 (inherited): `test_flash_path_record_sync.py`'s whole-repo porcelain assertion bit this plan too — Task 1's in-flight `CLAUDE.md` diff failed the pytest suite until committed, exactly as L-1 predicts | Unassigned — orphaned defect, hand-off only | Recorded, not fixed (out of this phase's declared scope). Worked around per L-1: committed before running the full suite. |
| F-142-07 (inherits F-138-05) | `check_size_baseline.py`'s `compare_native` raises an uncaught `KeyError` for an unrecognized native env; `check_build_warnings.py` exits 2 for the same condition | henols | Recorded, not fixed (standing precedent). Neither script was invoked with `native_loop_v131`, `native_params_v131`, or `native_trace_v131` anywhere in this phase (confirmed, §2). |
| F-142-08 | `leonardo` headroom is 2130 B against the 28672 B build-failure ceiling — unchanged since the 142-04 tip, but 142 B narrower than the Phase 141 tip's 2272 B | Phase 143 | Named as a risk to watch, not mitigated here — the ceiling is a build failure, not a gate, and Phase 143 must still fit. |
| F-142-09 | The MERGE-05 script's default baseline file is an unmoved v1.24 relic (commit `72a6844`), distinct from the `size_baseline_base01.json` anchor Phase 141's own record used explicitly — the two anchors give materially different verdicts for the identical measured tree | Phase 144 / TEST-08 | Recorded; both verdicts shown verbatim in §1.5 rather than picking one silently. |

---

## 16. Hand-offs

| # | Item | Owner |
|---|---|---|
| H1 | The trace freeze and the old-versus-new diff — both the frozen `Expected` values (198/221/201) and every measured `Was` value this milestone has produced (91/115or119/59, with the one `0x08` movement dated to plan 142-04) are now recorded on one page. | **Phase 144 / TEST-06** |
| H2 | Baseline reconciliation, with this phase's cold figures (24568/24618/26542 B) and **both** MERGE-05 anchors (the script's own default and the explicit BASE-01 override) recorded rather than only one. | **Phase 144 / TEST-08** |
| H3 | `PROJECT.md:125-127`'s superseded DIP32 caveat (the pre-H1 bit-collision theory D-01/D-02 supersede) and `PROJECT.md:119`'s stale `delay(10)` claim (C-6: no `delay(10)` exists in `eprom.cpp` today; Phase 141 replaced it) — both **read-only this phase**, both named as hand-offs, neither edited here. The jumper documentation contradiction (F-142-01) travels with this hand-off too. | **Phase 146 / CLOSE-04** |
| H4 | `0xBF` remains the sole free `0xA0..0xBF` ERROR slot (D-08, F-141-05). `leonardo`'s 2130 B headroom (F-142-08) is tighter than any prior phase in this milestone handed forward — budget accordingly. | **Phase 143** |

---

## 17. What this document is not

This record does not edit `.planning/PROJECT.md`, this phase's own locked context documents
(`142-CONTEXT.md`, `142-RESEARCH.md`, `142-PATTERNS.md`, `142-VALIDATION.md`), or either
`scripts/baseline/size_baseline.json` or `scripts/baseline/size_baseline_base01.json` — all confirmed
byte-unchanged. It does not attempt to bring MERGE-05 green — that is foreclosed by the same operator
disposition already applied to Phase 141 (§1.5). It does not re-freeze `native_trace_v131` — D-17
forbids it, and Phase 144 / TEST-06 owns that freeze. It does not assert an electrical fact about the
pin-1 VPP jumper beyond what D-01/D-02 already verified, and no jumper designator appears anywhere in
this document or in the reconciled `firestarter/CLAUDE.md`.

---

*Phase: 142-high-voltage-routing — Plan 07*
*Recorded: 2026-08-12, from this plan's own cold measurement and gate runs, the six prior plans'
committed SUMMARY.md artifacts (`142-01-SUMMARY.md` through `142-06-SUMMARY.md`), `142-CONTEXT.md`,
`142-RESEARCH.md`, `142-PATTERNS.md`, `142-VALIDATION.md`, and `141-LOOP-RECORD.md` for the
cross-phase pairing.*
