---
phase: 142
slug: high-voltage-routing
status: planned
nyquist_compliant: true
wave_0_complete: false
created: 2026-08-11
---

# Phase 142 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `142-RESEARCH.md` §Validation Architecture. Do not restate that
> section here — it carries the per-requirement oracle tables and the non-claims.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | PlatformIO Unity (`test_framework = unity`, `platform = native`) for firmware behaviour; plain `pytest` (no config, no `addopts`) for `firestarter/tests/` source-contract gates |
| **Config file** | `firestarter/platformio.ini` — env `[env:native_loop_v131]` (`:373-414`), extended by exactly two lines (`test_filter` **and** `-I`, both required — Phase 119 D-04) |
| **Quick run command** | `pio test -e native_loop_v131` (0.8 s, 39 cases at arrival) |
| **Full suite command** | `pio test -e native` && `pio test -e native_nodevtools` (must stay **141 cases / 17 suites / all_passed**) && `python3 -m pytest tests/ -o addopts="" -q` (256 at arrival) |
| **Estimated runtime** | ~15 s native + ~11 s pytest; cold triple-target `pio run -t clean` adds ~2 min |
| **Never run** | `check_size_baseline.py` / `check_build_warnings.py` against `native_loop_v131` — F-138-05 uncaught `KeyError`, exit 1 / exit 2 |

---

## Sampling Rate

- **After every task commit:** `pio test -e native_loop_v131 -f "*test_vpp_eprom_v131*"` plus the full `native_loop_v131` env
- **After every task commit (pytest gates):** `python3 -m pytest tests/ -o addopts="" -q` — **commit first.** `tests/test_flash_path_record_sync.py:1247` asserts whole-repo `git status --porcelain == ""`, so any in-flight firmware diff turns it RED (F-141-11, orphaned, do not fix here)
- **After every plan wave:** full suite command above, plus `pio run -e uno` / `-e uno328pb` / `-e leonardo` — **leonardo must LINK** (26400/28672 B at arrival, 2272 B headroom; the ceiling is a build failure, not a gate)
- **Before `/gsd-verify-work`:** full suite green, `native_trace_v131` **expected RED and named as such in the record** (D-17 — do not re-freeze), cold `pio run -t clean` figures captured on all three AVR targets for D-16
- **Max feedback latency:** ~1 s (native_loop_v131) / ~11 s (pytest)

---

## Per-Task Verification Map

Populated by the planner from each PLAN.md's `<verify><automated>` blocks. Every
requirement below has at least one off-hardware oracle named in
`142-RESEARCH.md` §Validation Architecture "Per-requirement oracles".

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 142-01 T1 | 142-01 | 1 | VPP-03 | T-142-MACRO | Both EPROM_HV_* composites defined exactly once, positioned after the wide arm, P1-free, correct in both build variants | source-scan + full native regression | `python3` header check then `pio test -e native` | ✅ header exists | ⬜ pending |
| 142-01 T2 | 142-01 | 1 | VPP-04 | T-142-ELIDE / T-142-PINNED | Suite reachable from the existing env by BOTH required lines; recorder sits below the register cache-compare elision; VPP millivolts injectable; neither pinned env nor the baseline moved | config + source-scan | `python3` env-and-stub check | ❌ W0 | ⬜ pending |
| 142-01 T3 | 142-01 | 1 | VPP-04 | T-142-VACUOUS / T-142-WINDOW | Recorders start clean, composites are what the header says, and the read-back mismatch window returns 0xFF then target then ~target | unit (native) | `pio test -e native_loop_v131 -f "*test_vpp_eprom_v131*"` | ❌ W0 | ⬜ pending |
| 142-02 T1 | 142-02 | 2 | VPP-01 | T-142-A16 / T-142-BLAST | Nine-row (pins, revision) preserve truth table plus the 32-pin non-EPROM baseline, seen RED on exactly the three new-behaviour rows before the change | unit (native), RED-before-GREEN | `pio test -e native_loop_v131 -f "*test_vpp_eprom_v131*"` | ❌ W0 | ⬜ pending |
| 142-02 T2 | 142-02 | 2 | VPP-01 | T-142-A16 / T-142-LEGACY / T-142-FUTUREREV | Drop bit preserved for pins>=32 on an explicit four-case Rev 2-class set only, fail-safe default, no protocol key, no EPROM_HV_ token in memory.cpp | source-scan + unit + pinned envs | `python3` source check then `pio test -e native_loop_v131` then `pio test -e native` and `-e native_nodevtools` | ❌ W0 | ⬜ pending |
| 142-03 T1 | 142-03 | 3 | VPP-04 | T-142-OVERV / T-142-HOTRAIL / T-142-FORCE / T-142-REVVAC | Injected over-voltage yields MSG_ERR_VPP_HIGH plus RESPONSE_CODE_ERROR with an 8-byte payload; no route left asserted; FLAG_FORCE downgrades; an in-range control fires nothing | unit (native, HOST_STUBS_CUSTOM_VOLTAGE_MV) | `pio test -e native_loop_v131 -f "*test_vpp_eprom_v131*"` | ❌ W0 | ⬜ pending |
| 142-03 T2 | 142-03 | 3 | VPP-03 | T-142-SCOPECREEP | Pre-rewrite CMD_ERASE and CMD_CHECK_CHIP_ID control-value streams pinned as measured literals, so the composite widening is a measured no-op (assumption A3) | unit (native), pre-change baseline | `pio test -e native_loop_v131 -f "*test_vpp_eprom_v131*"` | ❌ W0 | ⬜ pending |
| 142-03 T3 | 142-03 | 3 | VPP-04 | T-142-PLANTLEAK | All five legs seen RED on a distinct named planted violation; eprom.cpp proven byte-restored by blob SHA | unit (native) + pytest | `pio test -e native_loop_v131` then `python3 -m pytest tests/ -o addopts="" -q` | ❌ W0 | ⬜ pending |
| 142-04 T1 | 142-04 | 4 | VPP-01 / VPP-02 / VPP-03 | T-142-PROGMEM / T-142-LEAKEXIT / T-142-VPEREMAP / T-142-SUCCESSDIS / T-142-GOLDEN / T-142-TABLE05 | **One atomic task (parts A-T), ONE commit, five files** — commit granularity is per task (`gsd-executor.md:410`), so one commit requires one task: **A-H** one exposed resolver reading vpp_path via pgm_read_byte, two call sites, zero protocol-equality predicates, two conditional wrappers, four composite disables, two deletions; **I-K** the inverted LOOP-08 case rewritten as VPP-01's positive proof, the disable case asserting the drop bit clear on a decidable revision, the success-exit assertion untouched; **L-T** golden re-derived by its own extractor with hand-authored reasons, correct blob SHA, consistent counts, re-pinned locator — all landing in ONE commit with the source change | source-scan + unit (native) + pinned envs + three AVR links + pytest gate + planted RED | `python3` source check then `pio test -e native` and `-e native_nodevtools` then `pio run` on all three targets; `pio test -e native_loop_v131`; `python3` re-derivation check then `python3 -m pytest tests/ -o addopts="" -q` (post-commit only, L-1) | ❌ W0 (parts A-K legs) · ✅ exists (D-18 gate) | ⬜ pending |
| 142-05 T1 | 142-05 | 5 | VPP-01 | T-142-FLAGDROP / T-142-REV1REG | Seven-row resolver truth table including the fail-closed arm no drive can reach; direct path, flag override and the Rev 1 stripping negative all proven in the strobe stream | unit (native) | `pio test -e native_loop_v131 -f "*test_vpp_eprom_v131*"` | ❌ W0 | ⬜ pending |
| 142-05 T2 | 142-05 | 5 | VPP-03 | T-142-DIVERGE / T-142-VACUOUSEQ | The physical byte eprom_check_vpp measures under equals the physical byte in effect at the write path's first genuine pulse, both non-zero and carrying both route bits | unit (native) + planted RED | `pio test -e native_loop_v131 -f "*test_vpp_eprom_v131*"` | ❌ W0 | ⬜ pending |
| 142-05 T3 | 142-05 | 5 | VPP-02 | T-142-VERIFYEXIT / T-142-UNCOND / T-142-WRONGEXIT | The final-pass verify exit and the energy-cap exit leave no route asserted; the write_init exit has honest defensive cover; the unreachable exit is named, not faked | unit (native) + planted RED | `pio test -e native_loop_v131` then `python3 -m pytest tests/ -o addopts="" -q` | ❌ W0 | ⬜ pending |
| 142-06 T1 | 142-06 | 5 | VPP-02 | T-142-CMDDONE / T-142-VACUOUSSCAN / T-142-SKIP | command_done zeroes all three latch registers inside its own brace-matched body and is reached from both dispatch arms, each asserted individually | source-contract (pytest) | `python3 -m pytest tests/test_hv_routing_source_contract_v142.py -o addopts="" -q` | ❌ W0 | ⬜ pending |
| 142-06 T2 | 142-06 | 5 | VPP-03 | T-142-DUPMASK / T-142-DEADRETURN / T-142-SELFMATCH | One resolver definition, at least two calls, one #define of each composite across include/, no hand-rolled equivalent and no return of the deleted dead helper | source-contract (pytest) | `python3 -m pytest tests/test_hv_routing_source_contract_v142.py -o addopts="" -q` | ❌ W0 | ⬜ pending |
| 142-06 T3 | 142-06 | 5 | VPP-02 / VPP-03 | T-142-SEAMLEAK / T-142-OVERCLAIM | At least nine planted scratch fixtures seen RED through an import-time env seam in a child process, no production file edited, seams proven unset | pytest gate + planted RED | `python3 -m pytest tests/ -o addopts="" -q` | ❌ W0 | ⬜ pending |
| 142-07 T1 | 142-07 | 6 | VPP-01 | T-142-STALEDOC | The algorithm-handler rows describe the shipped routing, the pre-existing-defect paragraph is retired with its authority named, and no jumper designator is asserted | source-scan + pytest | `python3` docs check then `python3 -m pytest tests/ -o addopts="" -q` | ✅ exists | ⬜ pending |
| 142-07 T2 | 142-07 | 6 | VPP-01 / VPP-02 / VPP-03 / VPP-04 | T-142-BASELINE / T-142-SILENCERED | Cold flash and RAM on all three AVR targets with deltas and headroom; MERGE-05 and native_trace_v131 REDs recorded verbatim and NOT fixed; warning total recorded against 1166 | build + gate scripts | `pio run -t clean` then `pio run` per target, then `check_build_warnings.py --rebuild` and `check_size_baseline.py --policy merge05 --rebuild` | ✅ exists | ⬜ pending |
| 142-07 T3 | 142-07 | 6 | VPP-01 / VPP-02 / VPP-03 / VPP-04 | T-142-OVERCLAIM / T-142-SC1FLAT / T-142-EARLYFLIP / T-142-REFLOW | The record carries the qualified SC1, every non-claim, the D-15 inventory, the findings and the hand-offs; all four requirements flipped in BOTH coverage tables by one hand edit | source-scan | `python3` record-and-flip check | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `firestarter/test/native/avr/test_vpp_eprom_v131/host_stubs.cpp` — opt into `HOST_STUBS_REAL_REGISTER_UTILS` (**mandatory**: the only layer below `rurp_write_to_register`'s elision, F-141-09) + `HOST_STUBS_RECORD_TIMING` + `HOST_STUBS_CUSTOM_READ_DATA_BUFFER` + `HOST_STUBS_CUSTOM_VOLTAGE_MV`; `reset_register_cache`, the readback model, `rurp_log_id` capture. Largely a copy of `test_loop_eprom_v131/host_stubs.cpp` plus the voltage mock.
- [ ] `firestarter/test/native/avr/test_vpp_eprom_v131/test_vpp_eprom_v131.cpp` — `setUp` mocking **all four** ArduinoFake timing functions (`delay`, `delayMicroseconds`, `millis`, `micros` — an unmocked call SIGABRTs; this is the C-2 mechanism); `tearDown` resetting `hardware_revision` unconditionally; a `drive_vpp_init(...)` helper calling `firestarter_operation_init` (NOT `drive_loop_write`, which deliberately skips `_init`)
- [ ] `firestarter/platformio.ini` — the two `[env:native_loop_v131]` lines (`test_filter` **and** `-I`). **Owner: plan 142-01 task 2**
- [ ] Re-derived `firestarter/tests/golden/protocol_branch_inventory.json` + the pinned `protocol_lines` literal at `firestarter/tests/test_protocol_branch_inventory.py:446` (D-18: re-derive by independent parse, never hand-edit a line number, a `keyed_on` set, a class or a count). **Owner: plan 142-04, parts L-T of its single task, in the SAME commit as the `eprom.cpp` change** (L-2 — and that plan is one task precisely because GSD commits per task, so one commit requires one task). Expected tier-1 movement 3 to 1, which also **renames** the locator test; a second tier-1 site is a TABLE-05 violation to fix in source, and a total below 24 sites is a real truncation signal, not a threshold to lower
- [ ] A `command_done()` source-contract leg in `firestarter/tests/` (D-09's owed test) — nothing asserts it today. **Owner: plan 142-06** (new module `tests/test_hv_routing_source_contract_v142.py`). **Open Question 7 DECIDED: source contract, labelled as such** — a behavioural oracle needs `firestarter.cpp` in a native `build_src_filter`, which collides with `main()` and would need a seventh env, forbidden by D-14
- [ ] Fate of `test_loop_eprom_v131.cpp:1573-1632` (`test_loop08_dip32_drop_bit_is_cleared_deliberately_before_the_first_pulse`) — **DECIDED during planning: REWRITE in place, renamed `test_vpp01_dip32_drop_bit_survives_the_block_on_rev2_class`, owned by plan 142-04, parts I-K of its single task.** Its `v0` drop-bit-SET assertion survives and becomes the non-vacuity partner for the new positive claim; its handle, bus config, revision override and A16-crossing seeding are already correct; and `test_loop08_the_28_pin_row_keeps_its_drop_bit` stays its paired control
- [ ] Nothing else. No new env, no `size_baseline.json` edit, no `messages.toml`, no codegen, no host change

**Every case must call `reset_register_cache(0,0,0)`** — `rurp_register_utils.h:12-14` initialises the globals to `0xff`, which ORs `CTRL_VPP_REGULATOR_ENABLE` into the first write of any case that does not (L-7).

**Every drop-bit assertion must set `hardware_revision = REVISION_2_2`** — on the default `REVISION_0` the drop bit and A16 both map to physical `0x01` and the claim is undecidable (L-6). `HOST_STUBS_RECORD_BUS` is unusable for drop-bit work: it truncates the `0x100` bit to zero.

---

## Planted-RED obligations (D-15 discipline)

Three legs are **green on arrival** and prove nothing until seen RED. Transcript verbatim in the owning plan's SUMMARY (precedent: 12 planted runs in Phase 140, 13 in Phase 141).

| Leg | Why green on arrival | Planted violation |
|-----|----------------------|-------------------|
| VPP-04(b) — no route asserted on the over-voltage refusal | `eprom.cpp:393` already clears `REGULATOR\|DROP` on every path but the pre-assert Rev-0 return (C-3) | Temporarily make `eprom.cpp:370-371` an early `return` |
| VPP-02 X2's widened drop-bit assertion | `test_loop05_the_loops_own_strobes_disable_the_high_voltage_route` already asserts `REGULATOR` clear | Revert the composite at `:174` to `REGULATOR` alone |
| `command_done()` source contract | The three zeroing lines already exist | Point the scanner at a fixture with one zeroing line removed — **three plants, one per register**, plus **two more**, one per dispatch call arm (plan 142-06 task 3) |
| VPP-04 (a) refusal fires, and (c) the `FLAG_FORCE` downgrade | Both already hold (`eprom.cpp:352` and the `:366-372` fork) | Widen the over-voltage compare so the refusal never fires (arms (a)); remove the `FLAG_FORCE` fork so both paths error (arms (c)) — plan 142-03 task 3 |
| The pre-rewrite `CMD_ERASE` / `CMD_CHECK_CHIP_ID` byte-identity baselines | Pure equality assertions on a measured stream — they pass on any change that happens not to move a bit | Narrow the erase-path assert mask at `:399`, and narrow the chip-id clear at `:327` to drop A9 — plan 142-03 task 3 |
| The `(pins, revision)` preserve truth table's negatives and the 32-pin non-EPROM baseline | Green before the change | Make the new preserve arm unconditional (arms the Rev 1 / Rev 0 / UNKNOWN rows); OR a stray bit into `top_address` instead of into `mask` (arms the byte-identity baseline) — plan 142-02 task 2 |
| VPP-03's measure-versus-apply equality | Green once plan 142-04 lands | Re-introduce the deleted `pins >= 32` clear, reproducing the exact pre-phase divergence — plan 142-05 task 2 |
| VPP-02's final-pass verify and energy-cap exits | Green once the wrapper lands | Remove the wrapper's conditional disable (arms the verify exit); make the wrapper unconditional (turns `test_loop05_a_successful_block_does_not_disable_the_route` RED, which is C-1's tiebreaker made executable) — plan 142-05 task 3 |
| The `include/`-glob composite-count legs | Green on arrival, and they have **no env seam** | **Either** add a glob-scoped seam and plant a duplicate `#define` in a scratch copy, **or** record the leg as unplanted with its reason. Do not plant by editing the real header — plan 142-06 task 3 decides and states which |

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| — | — | — | — |

**All phase behaviors that this phase *claims* have automated verification.** The following are **explicit non-claims** — neither automated nor deferred-to-manual, but out of scope by decision, and the phase record must state them rather than leave them inferable:

| Non-claim | Authority |
|-----------|-----------|
| `0x08` silicon behaviour after the route change | D-03 — bench-only, deliberately not attempted; AM27C020 is a known stress case (`PROJECT.md:560`, v1.18 P99: write#1 60/64, write#2 0/64) so it is not a pass/fail oracle either way |
| That the drop resistor produces ~13 V | No native suite reads an ADC; `rurp_read_voltage_mv` is a mock |
| **Any** timing change | `delay()`/`delayMicroseconds()` are unstubbed ArduinoFake free functions; the recorder stores arguments only. A trace diff proves *which* delay was requested, never how long anything took |
| Physical de-assertion where the mapper aliases two logical bits | C-4 (Rev 2-class `CTRL_ADDRESS_LINE_18` ≡ `CTRL_VPP_P1_ENABLE` ≡ physical `0x08`) and the Rev 0/1 drop↔A16 case. The composite's guarantee is **logical**, not physical |
| The address-bus `vpp_line` bit is cleared on write-path exit | D-11 — `memory.cpp:418-420` ignores `read_write`; clearing it would change the read path. Cleared only by `command_done()` |
| That `command_done()` runs on the real AVR abort path | The timeout arm (`firestarter.cpp:169-171`) depends on `millis()`, outside every native suite's reach |
| D-03's non-claim discipline is gate-enforced | **It is not.** CLOSE-01's `check_permitted_claims.py` is Phase 146's (L-12); prose-enforced only this phase |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies — 20 of 20 blocks present, each `bash -n` clean and each naming an absolute working directory
- [x] Sampling continuity: no 3 consecutive tasks without automated verify — every task carries one
- [x] Wave 0 covers all MISSING references — plan 142-01 lands the suite, the stubs and the env wiring; every later plan depends on it
- [x] No watch-mode flags
- [x] Feedback latency < 15s — 0.8 s for `native_loop_v131`, about 11 s for the pytest suite
- [ ] Every new gate leg seen RED on a planted violation, transcript in SUMMARY
- [ ] `native_trace_v131` RED is **named as expected** in the record (D-17), not silenced
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** planner-approved 2026-08-11; the two execution-dependent boxes above (planted-RED transcripts and the named `native_trace_v131` RED) are discharged by plans 142-02 through 142-07.
