# Phase 142: High-Voltage Routing — Research

**Researched:** 2026-08-11
**Domain:** AVR firmware control-register routing, single-exit disable invariants, native (host) Unity oracles
**Confidence:** HIGH on everything source-verifiable in this tree (all claims below carry a `file:line` or a quoted command output); MEDIUM on flash-cost estimates (reasoned, not measured — measurement requires editing source, which this research pass may not do); LOW on nothing (every LOW item is instead named as an Open Question).

**Repo state at research time:** `firestarter/` @ `4921388` on `gsd/v1.31-27c-programming-algorithm-fidelity`, working tree clean (`git status --porcelain` empty).

---

## Summary

CONTEXT.md's 18 decisions are, with three exceptions, resting on premises that hold. I re-located all ~25 cited source lines; **21 are exact, 6 need correction, and 1 (`rurp_pinout.h:95-96`) is simply the wrong pair of lines for the claim it supports.** More importantly, three substantive corrections change what the planner must write:

1. **D-10's word "unconditionally" contradicts D-09 and would turn an existing GREEN native case RED.** `test_loop_eprom_v131.cpp:1286-1309` (`test_loop05_a_successful_block_does_not_disable_the_route`) asserts that a *successful* block leaves `CTRL_VPP_REGULATOR_ENABLE` **set**. A wrapper that disables unconditionally after the inner body returns breaks it. The wrapper must gate on `handle->response_code == RESPONSE_CODE_ERROR`.
2. **D-15(b)'s template (`test_flash_intel_vpp`) runs in NO PlatformIO environment, and when forced to run it SIGABRTs after case 1 — the SAF-04 case never executes.** It is an *unrun* in-tree pattern, not "a working, in-tree template."
3. **`eprom_check_vpp()` is ALREADY exit-safe on its over-voltage refusal path** (`eprom.cpp:393` clears `REGULATOR|DROP` on every path except the pre-assert Rev-0 return). D-15(b) will therefore be **green on arrival** and must be planted-RED to mean anything.

A fourth finding is a genuine hardware trap the CONTEXT does not name: **on Rev 2-class boards logical `CTRL_ADDRESS_LINE_18` and logical `CTRL_VPP_P1_ENABLE` collapse onto the same physical bit `0x08`** (`rurp_pinout.h:127`, corroborated by `doc/SHIELD-REVISIONS.md:76` + `:83`). A composite "all HV off" mask that clears logical P1 cannot guarantee physical de-assertion when logical A18 is set. It is not reachable on the 27C write path today, but it is exactly the class of aliasing D-02 exists to guard against in the other direction, and it must be scoped explicitly.

**Primary recommendation:** put two *distinct* composites in `rurp_pinout.h` after `:97` — an all-off DISABLE composite (`REGULATOR|DROP|A9|VPE`, no explicit `P1`, so `eprom_internal_set_control_register`'s remap still converts VPE→P1 on P1 parts) and *nothing else*, because the preserve/HOLD mask is revision- and pins-conditional and therefore cannot be a `#define` at all. Draw the disable guarantee around **`eprom_write_execute` (mandatory — all four leaking exits are there) plus `eprom_write_init` (defensive, ~free)** and do **not** widen to `erase_execute` / `get_chip_id`, because those two are already internally exit-safe and `PROJECT.md:189-190` licenses a change there only "where a change is required for safe shared cleanup." Build every route-change proof on the `native_loop_v131` strobe recorder (`control_write_value()`), never on `HOST_STUBS_RECORD_BUS`, which truncates the `0x100` drop bit to zero.

---

## Corrections

### C-1 (HIGH severity) — D-10's "unconditionally disables" contradicts D-09 and breaks a live GREEN test

D-10: *"the public `eprom_write_execute` calls it and then **unconditionally** disables."*
D-09: *"the per-block success exit deliberately leaves the rail up."*

These cannot both be implemented. The tiebreaker is a test that exists and passes today:

```
test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:1286
  void test_loop05_a_successful_block_does_not_disable_the_route(void) {
:1307     TEST_ASSERT_TRUE_MESSAGE((last & CTRL_VPP_REGULATOR_ENABLE) != 0,
:1308         "a SUCCESSFUL block must leave CTRL_VPP_REGULATOR_ENABLE SET -- nothing in this phase's scope disables it on the success path");
```

Observed GREEN (`pio test -e native_loop_v131`, this session):
```
test_loop_eprom_v131.cpp:1710: test_loop05_a_successful_block_does_not_disable_the_route	[PASSED]
================= 39 test cases: 39 succeeded in 00:00:00.778 =================
```

That case's own comment (`:1290-1292`) explicitly says *"generalising disable-on-every-exit to every exit in the file is Phase 142 / VPP-02's job"* — it was authored anticipating this phase, and it encodes D-09's success-exit exemption as an assertion.

**Determination:** the wrapper's disable must be conditional — `if (handle->response_code == RESPONSE_CODE_ERROR) { <disable composite>; }`. The *structural* property D-10 wants (a new `return` inside the inner body cannot escape the guarantee) is fully preserved by a conditional wrapper; what is not preserved is the literal word "unconditionally." If the planner intends to change `test_loop05_a_successful_block_does_not_disable_the_route` instead, that is a **deliberate deletion of a Phase 141 assertion** and needs to be named as such in the plan, not done incidentally.

### C-2 (HIGH severity) — the D-15(b) template suite runs in no environment and aborts before its SAF-04 case

CONTEXT `<code_context>` calls `test_flash_intel_vpp`'s SAF-04 assertions *"a working, in-tree template."* Evidence that it is neither working nor run:

```
$ grep -n "test_flash_intel_vpp" platformio.ini
72:; KNOWN-FLAKY: test_flash_intel_vpp suite has all individual Unity assertions
```
That is the *only* occurrence — a comment. Diffing every suite directory against every `test_filter`/`-I` entry in `platformio.ini`:
```
--- dirs NOT in any test_filter ---
test_flash_intel_vpp
```
It is the **only** suite directory absent from every environment. Forced to run (`-f` overrides the positive allowlist rather than intersecting it):
```
$ pio test -e native -f "*test_flash_intel_vpp*"
test/native/avr/test_flash_intel_vpp/test_flash_intel_vpp.cpp:194: test_flash_intel_vpp_nominal_proceeds	[PASSED]
Program received signal SIGABRT (Aborted)
------ native:native/avr/test_flash_intel_vpp [ERRORED] Took 0.61 seconds ------
================== 2 test cases: 1 succeeded in 00:00:00.613 ==================
```
The SAF-04 case is `RUN_TEST` #6 (`test_flash_intel_vpp.cpp:199`); execution stops during case #2. **Its assertions (`:184-189`) have never been observed to pass in this configuration.** `platformio.ini:72-74`'s claim that "all individual Unity assertions PASS but the suite as a whole ERRORS (Unity teardown abort)" does not hold today — the abort is mid-run, not at teardown.

Probable mechanism (**UNVERIFIED**): that suite's `setUp` (`test_flash_intel_vpp.cpp:55-65`) mocks only `delay`. `flash_intel.cpp:162-163` and `flash_utils.cpp:34-35` call `millis()`, which is unmocked. Every other suite in the tree mocks all four — `test_loop_eprom_v131.cpp:125-134`, with the explicit comment *"ArduinoFake SIGABRTs on any unmocked call — cheap insurance matching house convention."*

**Determination:** the SAF-04 *shape* (record `(bit, state)` pairs; assert `last write had the route bits in its mask and state==false`) is still a fine pattern to copy, but a plan that says "copy the working template" is copying dead code. Two concrete consequences:
- Copy the **shape**, and mock `delay`, `delayMicroseconds`, `millis`, `micros` (the `test_loop_eprom_v131.cpp:125-134` set).
- Do **not** copy its interception mechanism verbatim for the EPROM family. See C-5.

### C-3 (MEDIUM severity) — `eprom_check_vpp()`'s over-voltage refusal already de-energises; D-15(b) is green on arrival

`eprom_check_vpp` (`eprom.cpp:331-394`) has exactly **one** `return` (`:337`, the Rev-0 warning) and it fires **before** any route is asserted. Every other path — nominal, over-voltage ERROR (`:370-371`), over-voltage-with-`FLAG_FORCE` WARNING (`:367-368`), under-voltage WARNING (`:389-390`) — falls through to:
```
eprom.cpp:393    handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE, 0);
```

So the property D-15(b) demands ("no HV route is left asserted on that refusal path") is **already true**. The gate leg is therefore a *regression* gate, and per the standing D-15 discipline it must be seen RED on a planted violation (e.g. temporarily convert `:370-371` into an early `return`) before its GREEN is believed. A plan that presents D-15(b) as newly-established behaviour would be overclaiming.

Corollary for `eprom_write_init`: its single `return` (`:131`) fires on `RESPONSE_CODE_ERROR` from `eprom_generic_init`, whose two error sources are `eprom_check_vpp` (exit-safe, above) and `eprom_internal_check_chip_id` → `eprom_get_chip_id` (also exit-safe: `:327` clears `REGULATOR|A9` and there is no `return` between `:320` and `:327`). **No exit in `eprom_write_init` leaks a route today.** Wrapping it is defensive, not corrective — say so.

### C-4 (MEDIUM severity, new) — on Rev 2-class, logical `CTRL_ADDRESS_LINE_18` and logical `CTRL_VPP_P1_ENABLE` are the SAME physical bit

```
rurp_pinout.h:121   #define CTRL_VPP_P1_ENABLE_REV2       0x08
rurp_pinout.h:127   #define CTRL_ADDRESS_LINE_18_REV2     CTRL_VPP_P1_ENABLE_REV2
rurp_hw_rev_utils.h:26     ctrl_reg |= data & CTRL_ADDRESS_LINE_18 ? CTRL_ADDRESS_LINE_18_REV2 : 0;
```
Logically they are distinct in the wide layout (`CTRL_VPP_P1_ENABLE` = `0x08` at `:91`, `CTRL_ADDRESS_LINE_18` = `0x20` at `:93`). Physically, on `REVISION_2_0/2_1/2_2/2_3`, both land on `0x08`. Independently documented:
```
doc/SHIELD-REVISIONS.md:76  | P1_VPP_ENABLE         | N | CTRL_VPP_P1_ENABLE       | 0x08 / 0x08 | ✓ ... |
doc/SHIELD-REVISIONS.md:83  | REV_2_ADDRESS_LINE_18 | N | CTRL_ADDRESS_LINE_18_REV2 | 0x08 | not-present | not-present | ✓ ✓ ✓ ✓ |
```
Consequence for VPP-02: `memory_set_control_register` (`memory.cpp:145-149`) operates on the **logical** register; clearing logical `P1` (`0x08`) leaves logical `A18` (`0x20`) untouched, and the mapper will re-emit physical `0x08` from it. **A clear of `CTRL_VPP_P1_ENABLE` is not a guarantee of physical VPP-pin-1 de-assertion on Rev 2-class whenever `CTRL_ADDRESS_LINE_18` is set.**

Reachability on the 27C write path (assessed, not assumed): logical `A18` is only ever set from `mem_util_calculate_top_address_register`'s `(address >> 16) & CTRL_ADDRESS_LINE_18` (`memory.cpp:164`), i.e. bit 21 of the *remapped* bus address. Bus line 21 is socket pin 1 on a 32-pin DIP (`rurp_shield.h:40  #define VPP_P1_32_DIP 0x15`). On every 27C 32-pin part pin 1 *is* VPP, so `using_p1_as_vpp()` is true, and `mem_util_remap_address_bus` deliberately skips setting bit 21 (`memory.cpp:418-420`); no address line occupies bus 21 either. **So the aliasing is not reachable from a 27C write today.** It becomes reachable the moment an all-off composite that names `CTRL_VPP_P1_ENABLE` is used outside the EPROM family.

**Determination:** scope the composite explicitly to the EPROM family (name it `EPROM_*`), and state the A18/P1 physical aliasing as a named non-claim in the phase record rather than discovering it in Phase 144.

### C-5 (MEDIUM severity) — the SAF-04 interception mechanism silently bypasses the EPROM family's own remap

`test_flash_intel_vpp.cpp:182` replaces `h.firestarter_set_control_register = mock_set_ctrl_reg` **after** `configure_memory(&h)`. For protocol `0x10` that is harmless. For the EPROM family it is not: `configure_eprom` (`eprom.cpp:65-66`) *saves* the memory-layer function into the file-scope global `ep_set_control_register` and installs `eprom_internal_set_control_register` in its place. Overwriting `h.firestarter_set_control_register` therefore **removes** the `using_p1_as_vpp` VPE→P1 remap (`eprom.cpp:442-445`) from the path under test — the test would observe `CTRL_VPE_ENABLE` where production emits `CTRL_VPP_P1_ENABLE`.

Two sound interception points for the EPROM family:
- **Preferred:** leave the handle alone and observe at the `rurp_*` layer via `HOST_STUBS_REAL_REGISTER_UTILS` (`control_write_value()` in `test_loop_eprom_v131.cpp:1169-1173` returns the **post-remap physical byte**). This is the only layer that also proves the write was not elided.
- **Alternative:** override the global `ep_set_control_register` (declared non-`static` at `eprom.cpp:36`, so it is externally linkable) *after* `configure_memory`, which keeps the remap in the path.

### C-6 (LOW severity) — stale citations that will mislead an implementer

| Cited in | Claim | Actual |
|---|---|---|
| `142-CONTEXT.md` D-02 / canonical_refs | `rurp_pinout.h:95-96` gives "`0x01` vs `0x100`" | `:95` is `CTRL_VPP_REGULATOR_ENABLE 0x80`. The correct pair is **`:88`** (`CTRL_ADDRESS_LINE_16 0x01`) and **`:96`** (`CTRL_VPP_VPE_DROP_ENABLE 0x100`). |
| `142-CONTEXT.md` canonical_refs | `rurp_pinout.h:106-125` = the REV1/REV2 families | Block is **`:105-129`**. The cited range **omits `:128`**, which is the A18/P1 alias of C-4 — the single most consequential line in that block for this phase. |
| `142-CONTEXT.md` canonical_refs | `rurp_hw_rev_utils.h:17-41` = the mapper | Function signature is at **`:15`**; body `:15-41`. |
| `142-CONTEXT.md` D-14 / `<code_context>` | `test_flash_intel_vpp/host_stubs.cpp:39` = the mock | **`:38`** (`extern "C" void set_mock_vpp_mv(uint16_t mv)`). |
| `142-CONTEXT.md` canonical_refs | `memory.cpp:163-194` = `mem_util_calculate_top_address_register` | Function is **`:163-196`**; the `pins < 32` guard `:172-189`; the preserve OR-in `:190`; `pins == 28` A17 force `:192-194`. |
| `PROJECT.md:119` (Phase 146's to fix) | `eprom.cpp:114` pays a `delay(10)` VPE settle | **No `delay(10)` exists in `eprom.cpp`.** `grep -n "delay(" src/proms/eprom.cpp` → `197:delay(500)`, `321:delay(50)`, `324/348/400/403:delay(100)`, `452:delay(500)`. Phase 141 replaced it. `eprom.cpp:114` is now `eprom_check_vpp(handle);` inside `eprom_check_chip_id_init`. |
| `test_loop_eprom_v131.cpp:1597` (in-test prose) | drop bit excluded from preserve mask at `memory.cpp:161-162` | Actual guard `:172`, mask OR `:188`. |
| `tests/golden/protocol_branch_inventory.json` `meta.allowlist_rationale` | "the VPP-path duplication at `:145/:218`" and "line 71's switch" and "pin_routing predicate at `:320`" | Stale prose inside the golden itself. The authoritative numbers are in its own `sites` array: `:70`, `:190`, `:340`, `:442`. `meta.frozen_for` uses the correct `:190`/`:340`. **Re-derivation should fix `allowlist_rationale` too, or it will keep misleading readers.** |

### C-7 (LOW severity, informational) — JP4's function is documented two ways in this repo

D-01 leans on JP4 as the physical pin-1 VPP jumper. Supporting evidence exists:
- `firestarter/doc/SHIELD-REVISIONS.md:65` — *"`JMP_*` for shield-level jumper designators (today only the VPP-bypass jumper, `JMP_VPP_P1_BYPASS` = JP4)"*
- `.planning/v1.7-SHIELD-REVS.md:69` — *"JP4 (1x2 vertical header) added — physical connector for VPP jumper (P1_VPP_JMP); designator renamed from JP3-mod"*
- `.planning/PROJECT.md:560` — *"AM27C020 0x08 32-pin write/VPP path; RCA'd, 0-bits-programmed, **JP4-closed didn't fix**"* — someone has physically closed JP4 as a VPP-to-pin-1 experiment.

Contradicting evidence, same repo:
- `.planning/v1.7-SHIELD-REVS.md:37, :41-44` place JP4 in the **hardware-revision detect divider** chain: *"JP4 (P1_VPP_JMP) → R41 → A3 → GND."*

`JMP_VPP_P1_BYPASS` / `P1_VPP_JMP` appear in **no firmware source file** (`grep -rn` over `src/ include/` → no match); the alias is documentation-only. **Do not assert "JP4 routes VPP to socket pin 1" as a verified electrical fact in the phase record.** Two things that *are* verified and sufficient for D-01/D-02: (a) the drop bit is a VPP *level* selector (Phase 141 H1), and (b) **JP4 is `not-present` on Rev 0 and Rev 1** (`doc/SHIELD-REVISIONS.md:87`), which independently reinforces D-02's Rev-2-only gate — on Rev 0/1 there is no jumper to close, in addition to the bit alias.

### Checked and found sound (no correction needed)

| CONTEXT claim | Verdict | Evidence |
|---|---|---|
| D-02: on Rev 0/Rev 1 the drop bit maps onto the same physical bit as A16 | **HOLDS** | `rurp_hw_rev_utils.h:30-31` `ctrl_reg = data; ctrl_reg \|= data & CTRL_VPP_VPE_DROP_ENABLE ? CTRL_VPP_VPE_DROP_ENABLE_REV1 : 0;` — `rurp_register_t` is `uint16_t` under `HARDWARE_REVISION` (`rurp_types.h:16`), so `uint8_t ctrl_reg = data` truncates logical `0x100` away, then `:31` re-inserts it as `CTRL_VPP_VPE_DROP_ENABLE_REV1` = `0x01` (`rurp_pinout.h:106`); logical A16 = `0x01` (`:88`) passes straight through the same assignment; and `CTRL_ADDRESS_LINE_16_REV1` is *defined as* `CTRL_VPP_VPE_DROP_ENABLE_REV1` (`:116`). |
| D-02: on Rev 2-class they are distinct | **HOLDS** | `rurp_hw_rev_utils.h:24-25` maps drop→`CTRL_VPP_VPE_DROP_ENABLE_REV2` (`0x01`, `:119`) and A16→`CTRL_ADDRESS_LINE_16_REV2` (`0x20`, `:124`). |
| D-02: legacy non-`HARDWARE_REVISION` build has a genuine macro alias | **HOLDS** | `rurp_pinout.h:75-76`: `#define CTRL_VPP_VPE_DROP_ENABLE 0x01` / `#define CTRL_ADDRESS_LINE_16 CTRL_VPP_VPE_DROP_ENABLE`. |
| D-02: revision lookup is boot-cached, no ADC per call | **HOLDS** | `rurp_hw_rev_utils.h:100-106` → EEPROM override or `rurp_get_physical_hardware_revision()` (`:43-45`) which returns the file-scope `revision` (`:13`), set once in `rurp_detect_hardware_revision()`. **But see the cost quantification in §Gate and Budget Posture — "no new class of cost" is true; "free" is not.** |
| D-02: unknown revision must fail toward today's stripping | **HOLDS and is the documented house pattern** | `rurp_hw_rev_utils.h:33-37` `default: /* ctrl_reg = 0 */ break;` — `REVISION_UNKNOWN` (`0xFE`, `rurp_shield.h:31`) yields no VPP/VPE enables at all. |
| D-09: `command_done()` zeroes all three registers on both success and abort | **HOLDS** | `firestarter.cpp:162-171`; `:166` `CONTROL_REGISTER=0x00`, `:167` `LEAST_SIGNIFICANT_BYTE=0x00`, `:168` `MOST_SIGNIFICANT_BYTE=0x00`. Exactly **two** call sites: `:176` (the `timeout < millis()` abort arm of `loop()`) and `:290` (`if (finished) command_done(&handle);` after the `:217-288` dispatch switch). |
| D-09: nothing tests `command_done()` today | **HOLDS** | `grep -rn command_done` over `src/ test/` returns only `firestarter.cpp:30/162/176/290`, a prose mention at `operation_utils.cpp:166`, and four *comments* in `test_loop_eprom_v131.cpp` (`:262`, `:1260`, `:1264`, `:1267`) explaining why that suite deliberately does **not** drive it. Zero assertions. |
| D-13: `MSG_ERR_VPP_HIGH` / `MSG_WARN_VPP_HIGH` in no test | **HOLDS** | `grep -rn "MSG_ERR_VPP_HIGH\|MSG_WARN_VPP_HIGH\|MSG_WARN_VPP_LOW\|MSG_WARN_REV0_VPP" test/ tests/` → **no output**. Source refs only: `eprom.cpp:367/370`, `flash_intel.cpp:55/58`, `messages.h:71/101`. |
| D-13: `test_val_eprom` pins `vpp_mv = 0` against a 0-returning stub | **HOLDS** | `test_val_eprom.cpp:74` `h.vpp_mv = 0;  /* vpp setpoint=0 matches stub voltage=0: no warn/error */`; that suite does **not** define `HOST_STUBS_CUSTOM_VOLTAGE_MV`, so `rurp_read_voltage_mv()` returns `0` from `host_stubs_common.inc:275-277`. `0 > 0+500` false; `0 < 0*95/100` false. Vacuous by construction. |
| D-08 / F-141-05: `0xBF` is the last free ERROR slot | **HOLDS** | `messages.h` `0xA0`…`0xBE` are all occupied (`:77-107`, contiguous); `0xBF` unused. |
| D-06: `FLAG_VPE_AS_VPP` is a pure CLI escape hatch, set by no DB entry | **HOLDS** | `firestarter_app/firestarter/cli_handlers.py:574` `@click.option("--vpe-as-vpp", "vpe_as_vpp", is_flag=True, help="Use VPE as VPP voltage")`; the only assignment is `eprom_operations.py:196-197` `if vpe_as_vpp: flags \|= FLAG_VPE_AS_VPP`. No database path touches it. |
| D-07: both `eprom.cpp` and `memory.cpp` already include `rurp_pinout.h` | **HOLDS** | `eprom.cpp:17`, `memory.cpp:25` (direct), plus transitively via `rurp_shield.h:20`. |
| D-14: `native`/`native_nodevtools` pinned at 141 cases / 17 suites | **HOLDS, and re-measured live** | `size_baseline.json` `native_envs.native = {cases:141, suites:17, all_passed:true}`, same for `native_nodevtools`; `check_size_baseline.py:100 NATIVE_ENVS = ("native","native_nodevtools")`, `:278 rec = baseline["native_envs"][env]`, `:280-289` asserts cases, suites AND all_passed. Live: `pio test -e native` → `141 test cases: 141 succeeded`, 17 suites listed. Both envs' `test_filter` and `-I` lists parsed to exactly 17 entries each. |
| D-16: the three cold flash/RAM figures | **HOLDS, independently re-measured this session** | see §Gate and Budget Posture. |
| D-16: native warning watermark 1166 with zero headroom | **HOLDS** | `size_baseline.json` `warnings.native.native.total_watermark = 1166` (and `native_nodevtools` = 1166), `warnings.policy.native_rule = "<= total_watermark"`. Recorded == watermark ⇒ zero headroom. |
| D-17: `native_trace_v131` is RED right now | **HOLDS, observed** | `pio test -e native_trace_v131` → `test_protocol_0x07_…: Expected 198 Was 91 [FAILED]`, `0x08: Expected 221 Was 119 [FAILED]`, `0x0B: Expected 201 Was 59 [FAILED]`, then `SIGQUIT`, `[ERRORED]`, `6 test cases: 3 failed, 2 succeeded`. |
| D-18: both blob SHAs pinned and currently matching | **HOLDS** | `git hash-object src/proms/eprom.cpp src/proms/eprom_params.cpp` → `b36d3c4c…`, `5dffe841…`; identical to `meta.blob_shas`. All 27 recorded site line numbers match the current file. Whole pytest gate suite: **256 passed**. |
| D-12's "fact worth carrying": a 27C write asserts only `REGULATOR` (+drop) | **HOLDS** | The only control-register writes reachable from `eprom_write_execute` are `:192`, `:195`, `:218`, `:174`. No `A9`/`VPE`/`P1`. |
| `<code_context>`: `PROGMEM` rows must go through `pgm_read_*` | **HOLDS** | `eprom_params.h:71-77` (the accessor returns "a POINTER INTO PROGMEM"); `eprom_params.cpp:45` `PROGMEM`; existing consumers `eprom.cpp:105`, `:228-233`. |
| `<code_context>`: register-write elision is real | **HOLDS** | `rurp_register_utils.h:39-41` `case CONTROL_REGISTER: if (control_register == data) { return; }` — compared in **logical** space, *before* `rurp_map_ctrl_reg_for_hardware_revision` (`:47-49`). |

---

## Re-located Source Map

`✓` = cited range is exact. Corrections in **bold**.

| Cited (CONTEXT.md) | Actual | Note |
|---|---|---|
| `eprom.cpp:189-198` write-path route selection | ✓ `:189-198` | `:189` regulator-off guard, `:190` predicate, `:192`/`:195` the two asserts, `:197` `delay(500)` |
| `eprom.cpp:190` / `:340` the two duplicated predicates | ✓ | byte-identical text: `if (handle->protocol == 0x0B \|\| is_flag_set(FLAG_VPE_AS_VPP))` |
| `eprom.cpp:217-219` Phase 141 `pins >= 32` clear | ✓ `:217-219` | |
| `eprom.cpp:173-182` `eprom_internal_report_budget_failure` | ✓ `:173-182` | `static`; disable at `:174` |
| `eprom.cpp:233-234` `(void)`-cast `vpp_path` hoist | ✓ `:233-234` | |
| `eprom.cpp:296-314` final verify pass + early return | ✓ `:296-314` | `return` at `:311` |
| `eprom.cpp:331-394` `eprom_check_vpp` | ✓ `:331-394` | Rev-0 return `:337`; asserts `:342`/`:345`; **unconditional clear `:393`** (C-3) |
| `eprom.cpp:345` drop-bit-on measurement | ✓ `:345` | |
| `eprom.cpp:396-410` `eprom_internal_erase` | ✓ `:396-410` | asserts `:399`, `:402`; clear `:409` |
| `eprom.cpp:441-447` `using_p1_as_vpp` remap | ✓ `:441-447` | predicate `:442`, rewrite `:443-444` |
| `eprom.cpp:70-77` / `:71-76` pulse fallback switch | **`:70-75`** | switch `:70`, cases `:71-73` |
| `memory.cpp:163-194` `mem_util_calculate_top_address_register` | **`:163-196`** | guard `:172`, `mask \|= DROP` `:188`, preserve OR-in `:190`, `pins==28` A17 `:192-194` |
| `memory.cpp:172` the `pins < 32` guard | ✓ `:172` | |
| `memory.cpp:366-376` `memory_set_data` | ✓ `:294-304` | `mem_util_delay_us(handle->pulse_delay)` at `:302` |
| `memory.cpp:401-424` `mem_util_remap_address_bus` | ✓ `:329-352` | |
| `memory.cpp:418-420` the `vpp_line` bit | ✓ `:346-348` | `if (config.vpp_line != 0xFF && !using_p1_as_vpp(handle))` — `read_write` genuinely ignored (D-11 holds) |
| `rurp_pinout.h:75-96` per-variant `CTRL_*` | **`:74-97`** incl. guards | legacy arm `:74-84`, wide arm `:85-97` |
| `rurp_pinout.h:95-96` "distinct `0x01` vs `0x100`" | **`:88` + `:96`** | C-6 |
| `rurp_pinout.h:75-76` legacy aliases | ✓ `:75-76` | |
| `rurp_pinout.h:106-125` REV1/REV2 families | **`:105-129`** | omitted `:128` = A18/P1 alias (C-4) |
| `rurp_hw_rev_utils.h:17-41` mapper | **`:15-41`** | Rev2 arm `:19-27`, Rev0/1 arm `:28-32`, fail-safe default `:33-37` |
| `rurp_hw_rev_utils.h:43-45` boot-cached static | ✓ `:43-45` | backing storage is `:13` `uint8_t revision = 0xFF;` |
| `rurp_hw_rev_utils.h:100-106` `rurp_get_hardware_revision` | ✓ `:100-106` | also declared `rurp_shield.h:151` → callable from `memory.cpp` |
| `memory_utils.h:43-47` `using_p1_as_vpp` | ✓ `:43-47` | `static inline`; constants `rurp_shield.h:40-42` (`0x15`/`0x0F`/`0x0B`) |
| `eprom_params.h:46` `VPP_PATH_*` enum | ✓ `:46` | `VPP_PATH_DROP_RESISTOR = 0`, `VPP_PATH_DIRECT_VPE = 1`; `:43-45` explicitly says Phase 142 owns the masks |
| `eprom_params.h:57` the `vpp_path` column | ✓ `:57` | `uint8_t` |
| `eprom_params.cpp:46-48` the three rows | ✓ `:50-52` | `0x07`/`0x08` → `VPP_PATH_DROP_RESISTOR`; `0x0B` → `VPP_PATH_DIRECT_VPE` |
| `firestarter.cpp:162-171` `command_done()` | ✓ `:162-171` | |
| `firestarter.cpp:210-286` dispatch switch | ✓ `:215-291` | `:289-291` `if (finished) command_done(...)` |
| `host_stubs_common.inc:274-278` voltage seam | ✓ `:274-278` | |
| `test_flash_intel_vpp/host_stubs.cpp:39` mock | **`:38`** | |
| `test_flash_intel_vpp.cpp:160-189` / `:186-189` SAF-04 | **fn `:173-190`, assertions `:184-189`** | and see C-2 |
| `platformio.ini` `[env:native_loop_v131]` `:373` | ✓ `:373` | |
| `test_protocol_branch_inventory.py:446` `protocol_lines` | ✓ `:446` | `assert protocol_lines == [70, 190, 340]` |
| `doc/SHIELD-REVISIONS.md` §7 `JMP_VPP_P1_BYPASS` row | ✓ `:87` | `not-present` on rev_0 and rev_1 (C-7) |
| `doc/SHIELD-REVISIONS.md` §6 32-pin capability on every rev | ✓ `:50-56` | Rev 0 `:50`, Rev 1 `:51` both list "UV-EPROM 32-pin DIP" |
| `PROJECT.md:125-127` superseded DIP32 caveat | ✓ `:125-127` | plus C-6: its `eprom.cpp:114` `delay(10)` sibling at `:119` is also stale |
| `PROJECT.md:189-190` out-of-scope line D-12 cites | ✓ `:189-190` | *"Erase, blank-check, chip-ID, bus remapping and VPP validation behavior — unchanged except where a change is required for safe shared cleanup."* |

---

## Control-Register Assertion Map

This is D-12's demanded artifact. **Every** control-register write reachable from `src/proms/eprom.cpp`, plus the indirect writes that carry HV bits across an address change.

### A. Direct writes in `eprom.cpp` (all go through `handle->firestarter_set_control_register`, i.e. `eprom_internal_set_control_register` → `ep_set_control_register` → `memory_set_control_register`)

| # | file:line | enclosing function | bits (logical) | set/clear | reachable from |
|---|---|---|---|---|---|
| 1 | `eprom.cpp:174` | `eprom_internal_report_budget_failure` (`static`) | `REGULATOR` | **clear** | `CMD_WRITE` only (called from `eprom_write_execute:267`, `:274`) |
| 2 | `eprom.cpp:192` | `eprom_write_execute` | `REGULATOR` | set | `CMD_WRITE` (`0x0B` or `FLAG_VPE_AS_VPP` arm) |
| 3 | `eprom.cpp:195` | `eprom_write_execute` | `REGULATOR \| DROP` | set | `CMD_WRITE` (`0x07`/`0x08` arm) |
| 4 | `eprom.cpp:218` | `eprom_write_execute` | `DROP` | **clear** | `CMD_WRITE`, `handle->pins >= 32` only — **removed by D-04** |
| 5 | `eprom.cpp:320` | `eprom_get_chip_id` | `REGULATOR` | set | `CMD_CHECK_CHIP_ID`; **and** any command whose `init` is `eprom_generic_init` with `handle->chip_id > 0` — i.e. `CMD_READ`, `CMD_WRITE`, `CMD_VERIFY`, `CMD_ERASE`, `CMD_BLANK_CHECK` |
| 6 | `eprom.cpp:323` | `eprom_get_chip_id` | `A9` | set | same as #5 |
| 7 | `eprom.cpp:327` | `eprom_get_chip_id` | `REGULATOR \| A9` | **clear** | same as #5 — no `return` between #5 and #7 ⇒ **exit-safe** |
| 8 | `eprom.cpp:342` | `eprom_check_vpp` | `REGULATOR` | set | **every** EPROM command (`eprom_generic_init:413`, `eprom_check_chip_id_init:114`, `eprom_write_init:129`) — `0x0B`/`FLAG_VPE_AS_VPP` arm |
| 9 | `eprom.cpp:345` | `eprom_check_vpp` | `REGULATOR \| DROP` | set | same as #8 — `0x07`/`0x08` arm. **This is the measured-route/applied-route divergence D-03 names.** |
| 10 | `eprom.cpp:393` | `eprom_check_vpp` | `REGULATOR \| DROP` | **clear** | same as #8, on **all** paths except the pre-assert Rev-0 return at `:337` ⇒ **exit-safe** (C-3) |
| 11 | `eprom.cpp:399` | `eprom_internal_erase` | `REGULATOR` | set | `CMD_ERASE` (`eprom_erase_execute:124`) **and** `CMD_WRITE` (`eprom_write_init:136`, gated on `FLAG_CAN_ERASE && !FLAG_SKIP_ERASE`) |
| 12 | `eprom.cpp:402` | `eprom_internal_erase` | `A9 \| VPE` → remapped to `A9 \| P1` when `using_p1_as_vpp` | set | same as #11. **The only `A9\|VPE` assertion on the write path** (D-12's note, confirmed) |
| 13 | `eprom.cpp:409` | `eprom_internal_erase` | `REGULATOR \| A9 \| VPE` (→`…\|P1`) | **clear** | same as #11 — no `return` between #11 and #13 ⇒ **exit-safe** |
| 14 | `eprom.cpp:451` | `eprom_internal_ensure_regulator_enabled` | `REGULATOR` | set | **UNREACHABLE — zero callers.** `grep -rn eprom_internal_ensure_regulator_enabled` over `src/ include/` returns only the definition at `eprom.cpp:449`. Dead code duplicating the `:189-198` guard. |

### B. Reads of the control register in `eprom.cpp`

| file:line | function | bit | note |
|---|---|---|---|
| `eprom.cpp:189` | `eprom_write_execute` | `REGULATOR` | the LOOP-08 once-per-block guard; a tier-2 inventory site |
| `eprom.cpp:450` | `eprom_internal_ensure_regulator_enabled` | `REGULATOR` | dead (see #14) |

### C. The bit-rewrite layer

`eprom.cpp:441-447` — `eprom_internal_set_control_register`:
```
:442    if (bit & CTRL_VPE_ENABLE && using_p1_as_vpp(handle)) {
:443        bit &= ~CTRL_VPE_ENABLE;
:444        bit |= CTRL_VPP_P1_ENABLE;
:445    }
```
Installed for **every** EPROM command (`eprom.cpp:65-66`), so it intercepts writes #1-#13. `using_p1_as_vpp` (`memory_utils.h:43-47`) is true for `pins==32 && vpp_line==0x15`, `pins==28 && vpp_line==0x0F`, `pins==24 && vpp_line==0x0B`.

> **Trap for the all-off composite:** if the composite names **both** `CTRL_VPE_ENABLE` and `CTRL_VPP_P1_ENABLE`, then on a `using_p1_as_vpp` handle `:443` strips `VPE` from the mask, so the physical VPE line (`0x04` on every revision branch) is never cleared. Recommended composite therefore names `CTRL_VPE_ENABLE` and **not** `CTRL_VPP_P1_ENABLE`, letting `:442-445` do the conversion — byte-identical semantics to today's `:409`.

### D. Indirect writes carrying HV bits (not in `eprom.cpp`, but in every `eprom.cpp` code path)

Every `handle->firestarter_set_address(...)` and every `firestarter_get_data`/`firestarter_set_data` reaches `mem_util_set_address` (`memory.cpp:224-308`), which writes `CONTROL_REGISTER` **unconditionally** at `:231` with the value from `mem_util_calculate_top_address_register` (`:163-196`). That function's preserve mask is:
```
memory.cpp:171   rurp_register_t mask = CTRL_VPP_A9_ENABLE | CTRL_VPE_ENABLE | CTRL_VPP_P1_ENABLE | CTRL_VPP_REGULATOR_ENABLE;
memory.cpp:172   if (handle->pins < 32) {
memory.cpp:188       mask |= CTRL_VPP_VPE_DROP_ENABLE;
memory.cpp:193   }
memory.cpp:194   top_address |= rurp_read_from_register(CONTROL_REGISTER) & mask;
```
Call sites inside `eprom.cpp`'s reach: `eprom.cpp:401` (`eprom_internal_erase`), and — via `memory_get_data:252` / `memory_set_data:298` — every read and every pulse in the per-byte loop (`eprom.cpp:247`, `:257`, `:260`, `:287`, `:298`), the final verify pass, `mem_util_blank_check` (`memory.cpp` blank-check loop → `firestarter_get_data`), and `eprom_get_chip_id:325-326`.

Also `memory_set_control_register` (`memory.cpp:145-149`) is a read-modify-write on the **cached logical** value (`rurp_read_from_register` returns the `rurp_register_utils.h:14` global).

### E. Every exit from the candidate functions

**`eprom_write_init` (`eprom.cpp:127-145`) — 2 exits:**

| exit | file:line | trigger | route state on exit **today** |
|---|---|---|---|
| E1 | `:131` `return;` | `eprom_generic_init` set `RESPONSE_CODE_ERROR` | **clear** — both error sources (`eprom_check_vpp` #10, `eprom_get_chip_id` #7) clear before returning |
| E2 | `:145` fall-through | normal, or `mem_util_blank_check` set ERROR | **clear** — erase (#13) cleared; blank check touches no HV bit |

**`eprom_write_execute` (`eprom.cpp:184-315`) — 5 exits:**

| exit | file:line | trigger | route state on exit **today** |
|---|---|---|---|
| X1 | `:226` `return;` | `row == NULL` (dead in practice — refused at `eprom.cpp:86-90`) | **LEAKS `REGULATOR` + `DROP`** — `:189-198` already ran |
| X2 | `:268` `return;` | `pulses >= max_pulses` → `MSG_ERR_MAX_PULSES` | **partially leaks:** `#1` cleared `REGULATOR`, but on `pins < 32` the `DROP` bit set at `:195` is still asserted (preserved by `memory.cpp:188`) |
| X3 | `:275` `return;` | `accumulated >= energy_cap_us` → `MSG_ERR_ENERGY_CAP` | same as X2 |
| X4 | `:311` `return;` | final-pass verify mismatch → `MSG_ERR_VERIFY` | **LEAKS `REGULATOR` + `DROP`** — no disable at all. **This is VPP-02's headline gap.** |
| X5 | `:315` fall-through | success | leaves `REGULATOR` (+`DROP` on `pins<32`) set **by design** — D-09, asserted by `test_loop_eprom_v131.cpp:1307` |

### Recommended function boundary (D-12 determination)

**Wrap `eprom_write_execute` (required) and `eprom_write_init` (recommended, defensive). Do NOT widen to `eprom_erase_execute`, `eprom_check_chip_id_execute`, or `eprom_get_chip_id`.**

Reasoning, tied to evidence:
- **All four leaking exits are in `eprom_write_execute`** (X1, X2, X3, X4). Wrapping it is the whole of VPP-02's corrective content.
- `eprom_write_init`'s two exits leak nothing today (E1, E2), but its erase leg is the *only* write-path code that asserts `A9|VPE(→P1)` (#12) and its safety rests on there being no `return` between `:399` and `:409` — a property a future edit can break silently. A wrapper makes that structural for `~0` cost (see §Gate and Budget Posture). This is exactly D-12's recorded default.
- **Widening to `eprom_erase_execute` / `eprom_check_chip_id_execute` is NOT "required for safe shared cleanup"** and is therefore forbidden by `PROJECT.md:189-190`: `eprom_internal_erase` (#11→#13) and `eprom_get_chip_id` (#5→#7) each already clear everything they assert, with no intervening `return`. A wrapper there would be pure scope creep and would change the emitted strobe stream for `CMD_ERASE` and `CMD_CHECK_CHIP_ID`, moving two more tier-2 inventory sites for no safety gain.
- **Separate the two obligations.** VPP-02 (the *guarantee*) → the wrapper, scoped as above. VPP-03 (*one shared mask set*) → convert the hand-rolled bit lists at `#1` (`:174`), `#7` (`:327`), `#10` (`:393`) and `#13` (`:409`) into references to the shared composite. That is mask consolidation, not guarantee widening, and it is byte-identical on the wire (see below), so it does not touch behaviour anywhere `PROJECT.md:189-190` protects.
- **Byte-identity argument for the `:409` / `:327` / `:393` conversions:** `memory_set_control_register` computes `control_register & ~bit` on a clear. Widening the mask can only clear bits that are already 0 in the cached value, which yields an identical `data`, which `rurp_register_utils.h:39-41` then **elides identically**. Order of operations makes this concrete: `eprom_generic_init` → `eprom_check_vpp` clears `DROP` at `:393` **before** `eprom_internal_erase` runs, so `DROP` is 0 at `:409`; and `A9`/`VPE`/`P1` are 0 at `:393`. Verify this claim in the strobe stream rather than asserting it (see §Validation Architecture, VPP-03).
- **Kill or keep `eprom_internal_ensure_regulator_enabled` deliberately.** It is dead (#14) and duplicates the `:189-198` guard — a perfect candidate for the resolver consolidation. But removing it deletes tier-2 inventory site `:450` and moves the golden. Either fold it into the resolver **or** leave it byte-untouched and name it in the record; do not let it be an accident of the rewrite.

---

## Shared Mask Placement

**Determination: two `#define`s in `firestarter/include/rurp_pinout.h`, placed after `:97`, named with an `EPROM_` prefix — and the preserve/HOLD mask deliberately NOT among them.**

### Include-graph evidence

| Consumer | Includes `rurp_pinout.h` |
|---|---|
| `src/proms/eprom.cpp` | directly, `:17` |
| `src/proms/memory.cpp` | directly, `:25` |
| both | transitively via `rurp_shield.h:20` (`eprom.cpp:16`, `memory.cpp:24`) |

Full includer set: `rurp_hw_rev_utils.h:7`, `rurp_register_utils.h:5`, `rurp_shield.h:20`, `memory.cpp:25`, `eprom.cpp:17`, `hardware_operations.cpp:12`, `flash_intel.cpp:17`, `flash_5v_page.cpp:17`, `rurp_common.cpp:10`, `flash_utils.cpp:12`, `eeprom_28c.cpp:17`, plus six native suites. Placing composites here reaches every consumer with **zero new edges**.

**The alternative is worse, confirmed:** `eprom_params.h` deliberately has no shield dependency — `eprom_params.h:43-45` says so in the source: *"`vpp_path` names an ABSTRACT route, not a control-register bitmask — Phase 142 owns the mask sets, and naming a mask here would force this dependency-free header to pull in the shield's register header."* And `eprom_params.h:13-18` records that pairing an Arduino framework header with the `pgmspace` shim emits **14 macro-redefinition warnings against a watermark with zero headroom**. `eprom.h` is likewise unsuitable: `memory.cpp` would then need an EPROM-family header to compute its preserve mask (`memory.cpp:171-193` serves every protocol).

### Per-variant correctness

A composite `#define` body is expanded at **use** site, so it automatically picks up whichever arm of `rurp_pinout.h:74-97` is live. Concrete values:

| Composite | legacy (`#ifndef HARDWARE_REVISION`) | wide (`HARDWARE_REVISION`, every shipped build) |
|---|---|---|
| `REGULATOR \| DROP \| A9 \| VPE` | `0x80\|0x01\|0x02\|0x04` = **`0x87`** | `0x80\|0x100\|0x02\|0x04` = **`0x186`** |
| `REGULATOR \| DROP` | `0x81` | `0x180` |

Both are correct **as logical disable masks in every variant**, including the legacy aliased build: there, `DROP` *is* `A16` (`:75-76`), so clearing the composite also clears A16 — harmless on a *disable*, because `command_done()` (`firestarter.cpp:166`) zeroes the whole register at operation end anyway and a stale A16 cannot energise anything.

**The variant where a naive composite IS wrong — and this is the one D-07 asked research to flag:**

> A **preserve/HOLD** composite must NOT be a plain `#define` that includes `CTRL_VPP_VPE_DROP_ENABLE`.
>
> - Legacy build: `DROP == A16` at the macro level (`:75-76`), so a preserve mask naming `DROP` pins `A16` high forever.
> - Rev 0 / Rev 1, `HARDWARE_REVISION` build: `DROP` (logical `0x100`) and `A16` (logical `0x01`) both map onto physical `0x01` (`rurp_hw_rev_utils.h:30-31` + `rurp_pinout.h:106`, `:116`). Preserving `DROP` across `set_address` on a 32-pin part drives physical A16 high on **every** address. This is exactly D-02's rationale, now confirmed at the macro level.
> - Rev 2-class: they are distinct (`0x01` vs `0x20`, `rurp_hw_rev_utils.h:24-25`), so preserving `DROP` is safe.
>
> Membership therefore depends on a **runtime** revision read and on `handle->pins`. It cannot be a preprocessor constant. Express it as the existing conditional in `memory.cpp:171-193`, extended with a revision test — not as a header composite.

### Recommended shape

```c
/* rurp_pinout.h, after :97 — logical composites, correct in every build variant. */
#define EPROM_HV_ROUTE_MASK        (CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE)
#define EPROM_HV_ALL_OFF_MASK      (CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE \
                                    | CTRL_VPP_A9_ENABLE | CTRL_VPE_ENABLE)
```
Notes the planner must carry:
- **`CTRL_VPP_P1_ENABLE` is deliberately absent** from `EPROM_HV_ALL_OFF_MASK`. Including it defeats `eprom.cpp:442-445`'s VPE→P1 remap (see §Control-Register Assertion Map C) and, on Rev 2-class, `P1` is physically indistinguishable from `A18` (C-4) so naming it buys no guarantee.
- **`EPROM_` prefix, not a generic `VPP_MASK`.** The `native`/`native_nodevtools` warning watermark is 1166 with zero headroom and **all 1166 are macro redefinitions**; a generic name risks colliding with an ArduinoFake or `pgmspace` macro and tripping a live gate. `EPROM_HV_*` collides with nothing in this tree (`grep -rn "EPROM_HV" .` → no match).
- **Flash cost: 0 B until referenced** (`rurp_pinout.h:63-64` records the house rule: *"`#define` (NOT `constexpr`) per Phase 33 D-07 — preprocessor constants resolve at compile time and contribute 0 B to the `.hex` until referenced"*). A `static inline` function would also be inlined by avr-gcc at these call sites; the `#define` is preferred purely because it matches the file's existing convention and cannot acquire a linkage.
- **D-05's resolver is a separate artifact from these composites.** The resolver needs `handle` (for `pins`, `ctrl_flags`, `protocol`) and `eprom_params_for()`, so it belongs in `eprom.cpp` (or `eprom.h` if a native suite must call it directly — the `eprom_overprogram_us` precedent at `eprom.h:34` shows the house pattern for exposing a pure helper to a native oracle). Reading `vpp_path` **must** go through `pgm_read_byte(&row->vpp_path)`, never `row->vpp_path` (`eprom_params.h:71-77`).

---

## Test Env Mechanics

### The exact `platformio.ini` edits (D-14)

`[env:native_loop_v131]` today, verbatim (`platformio.ini:404-414`):
```ini
platform = native
test_framework = unity
test_filter =
	native/avr/test_loop_eprom_v131
build_flags =
	${env:native.build_flags}
	-I test/native/avr/test_loop_eprom_v131
lib_deps =
	fabiobatsilva/ArduinoFake@^0.4.0
build_src_filter = +<proms/> +<boards/rurp_serial_utils.cpp> +<json_parser.c> +<operation_utils.cpp>
test_build_src = yes
```
**Exactly two added lines** (Phase 119 D-04 — both are required; a suite dir is invisible to `pio test` until it is in `test_filter`, and its headers are unreachable until a matching `-I` exists):
```ini
test_filter =
	native/avr/test_loop_eprom_v131
	native/avr/test_vpp_eprom_v131          # <-- edit 1
build_flags =
	${env:native.build_flags}
	-I test/native/avr/test_loop_eprom_v131
	-I test/native/avr/test_vpp_eprom_v131  # <-- edit 2
```
`${env:native.build_flags}` (`platformio.ini:120-141`) supplies `-D HARDWARE_REVISION`, `-D DEV_TOOLS`, `-std=gnu++17`, `-I include`, all **17** existing suite `-I` paths, and `-D RURP_BOARD_NAME=\"native\"`. So the new suite compiles with `HARDWARE_REVISION` defined — `rurp_register_t` is `uint16_t` (`rurp_types.h:16`) and the drop bit is `0x100`.

**Run by name:**
```bash
pio test -e native_loop_v131 -f "*test_vpp_eprom_v131*"
```
`-f` **overrides** the positive `test_filter` rather than intersecting it — verified this session (it collected and ran `test_flash_intel_vpp`, which appears in no `test_filter`). So this command works even before edit 1 lands, provided edit 2 (`-I`) has landed. Useful during authoring; the committed state still needs both edits so a bare `pio test -e native_loop_v131` runs it.

**Side effect to record honestly:** a bare `pio test -e native_loop_v131` will then report **2 suites** and `39 + N` cases instead of today's `1 suite / 39 cases`. That figure is recorded only in the Phase 141 record, never asserted by a gate — but the Phase 142 record should restate the new figure so a later reader is not surprised.

**Prohibitions (all verified):**
- Do **not** add the suite to `[env:native]` or `[env:native_nodevtools]`. Both are pinned at 17 `test_filter` entries and 17 `-I` entries (parsed), and `check_size_baseline.py:278-289` asserts `cases == 141`, `suites == 17` **and** `all_passed` on both.
- Do **not** pass `native_loop_v131` to `check_size_baseline.py` — `NATIVE_ENVS` is hardcoded at `:100` and `:278` does a bare dict lookup ⇒ uncaught `KeyError`, exit 1, a false regression signal (F-138-05, unfixed).
- Do **not** pass it to `check_build_warnings.py` either — `NATIVE_ENVS` at `:87` is the same pair; an unknown env is exit 2.
- Do **not** create a seventh env.

### The voltage seam

`test/native/avr/_shared/host_stubs_common.inc:274-278`, verbatim:
```c
#ifndef HOST_STUBS_CUSTOM_VOLTAGE_MV
extern "C" uint16_t rurp_read_voltage_mv() {
    return 0;
}
#endif
```
The suite's `host_stubs.cpp` must, **before** the `#include` of the `.inc` (the guard is read at include time — `host_stubs_common.inc:23-25`, and every suite restates this pitfall):
```c
#define HOST_STUBS_CUSTOM_VOLTAGE_MV
#include "../_shared/host_stubs_common.inc"
...
static uint16_t s_mock_vpp_mv = 0;
extern "C" void set_mock_vpp_mv(uint16_t mv) { s_mock_vpp_mv = mv; }
extern "C" uint16_t rurp_read_voltage_mv() { return s_mock_vpp_mv; }
```
Exact signature: `extern "C" uint16_t rurp_read_voltage_mv()` — no parameters (declared `rurp_shield.h:140`).

### ⚠ The hardware-revision landmine this suite will hit first

`HOST_STUBS_REAL_REGISTER_UTILS` (which the route-change proof needs — see §Validation Architecture) **also defines `HOST_STUBS_CUSTOM_HW_REVISION_BLOCK`** (`host_stubs_common.inc:105`), which suppresses all four hardware-revision stubs so the **real** `rurp_hw_rev_utils.h` supplies them. The real `rurp_get_hardware_revision()` (`:100-106`) returns `rurp_get_config()->hardware_revision` whenever it is `< 0xFF`, and `host_stubs_common.inc:306` gives `static rurp_configuration_t s_host_config = {};` ⇒ **`hardware_revision == 0 == REVISION_0`** (`rurp_shield.h:25`).

Consequence: a suite that opts into the strobe recorder and calls `eprom_check_vpp` will take the **Rev-0 early return at `eprom.cpp:337`** and never reach the over-voltage compare. D-15(a) would be silently vacuous.

Two fixes, both already in-tree:
- **Override the EEPROM revision per case** — `test_loop_eprom_v131.cpp:1524` `rurp_get_config()->hardware_revision = REVISION_2_2;` with an unconditional reset in `tearDown` (`:143-151`: *"Unity calls `tearDown()` even when a case fails via `TEST_ASSERT`'s longjmp, so this reset is unconditional and always runs"*). **This is the right choice for Phase 142** — it also disambiguates the drop bit from A16 in the recorded physical byte, which the D-01/D-02 proof needs.
- The narrower `HOST_STUBS_CUSTOM_HW_REVISION` (`test_val_eprom/host_stubs.cpp:36` + `:44-47`) is **incompatible** with `HOST_STUBS_REAL_REGISTER_UTILS`; `test_loop_eprom_v131/host_stubs.cpp` says so explicitly in its header comment.

### The recorder layers, and why `HOST_STUBS_RECORD_BUS` cannot be used here

| Layer | Hooks | Sees the `0x100` drop bit? | Sees elision? |
|---|---|---|---|
| default (no flag) | none (`rurp_write_to_register` is a no-op, `:232-234`) | — | — |
| `HOST_STUBS_RECORD_BUS` (`:211-231`) | `rurp_write_to_register` **replaced** | **NO** — `:228` stores `(uint8_t)data`; `rurp_read_from_register` returns `0` (`:237-242`) so the logical register is always read as 0 | **NO** — records the call, not the strobe |
| `HOST_STUBS_REAL_REGISTER_UTILS` (`:96-209`) | `rurp_write_data_buffer` + `rurp_set_control_pin` (below the elision) | **YES**, as the *physical* mapped byte (`0x01` on Rev 2-class) | **YES** — an elided write produces no strobe, exactly like hardware |
| `+ HOST_STUBS_RECORD_TIMING` (`:135-206`) | suite-supplied `.AlwaysDo` on `delay`/`delayMicroseconds` | — | records **arguments only, never elapsed time** |

`test_val_eprom.cpp:92-96` documents the truncation in the production tree already: *"`CTRL_VPP_VPE_DROP_ENABLE` is 0x100 when `HARDWARE_REVISION` is defined — it does not fit in `uint8_t`. The recording buffer stores `uint8_t` data values, so `CTRL_VPP_VPE_DROP_ENABLE` cannot be detected via the 8-bit recording."*

**⇒ Any VPP-01 route-change proof must use `HOST_STUBS_REAL_REGISTER_UTILS`.** `HOST_STUBS_RECORD_BUS` is structurally incapable of it.

### Reusable harness already in `native_loop_v131`

`test_loop_eprom_v131/host_stubs.cpp` and `test_loop_eprom_v131.cpp` already provide, and the new suite can copy verbatim:
- `reset_register_cache(lsb, msb, ctrl)` — mandatory; the real globals are `0xff`-initialised (`rurp_register_utils.h:12-14`) and `0xff` ORs `CTRL_VPP_REGULATOR_ENABLE` into the first write of any case that forgets.
- `control_write_count()` / `control_write_strobe_index(i)` / `control_write_value(i)` (`test_loop_eprom_v131.cpp:1136-1173`) — the *post-remap physical byte* of the Nth **non-elided** `CONTROL_REGISTER` write.
- `first_genuine_pulse_strobe_index(values, n)` (`:1183-1193`) — for ordering claims.
- `loop_readback_seed/reads/reset` — a 16-bit-address-keyed read-back model.
- `clear_logged_ids()` / `logged_id_at(i)` / `logged_id_param(i,j)` — needed for asserting `MSG_ERR_VPP_HIGH` **by id**, which no test in the tree does today.
- `drive_loop_write(h, base, block, n)` (`:275-288`) — and its documented contract: *never* `_init`, *never* the whole command (because `command_done()` zeroes the register and would make any HV assertion vacuous). **For D-15 the new suite needs the opposite driver** (it must call `firestarter_operation_init` to reach `eprom_check_vpp`), so author a sibling `drive_vpp_init(...)` rather than bending `drive_loop_write`.
- `setUp` must mock `delay`, `delayMicroseconds`, `millis`, `micros` (`:125-134`) — ArduinoFake SIGABRTs on any unmocked call. **This is the C-2 lesson.**

### D-15(b) template shape (adapted from SAF-04, strengthened)

Because C-2 shows the SAF-04 case has never run, and C-5 shows its interception mechanism is wrong for the EPROM family, the recommended shape is:

```c
/* (a) refusal fires */
TEST_ASSERT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
TEST_ASSERT_TRUE(count_logged_id(MSG_ERR_VPP_HIGH) == 1);   /* by ID -- no test does this today */

/* (b) no route left asserted -- physical, post-remap, non-elided */
int n = control_write_count();
TEST_ASSERT_TRUE_MESSAGE(n >= 2, "non-vacuity: assert + clear must both have strobed");
int last = control_write_value(n - 1);
TEST_ASSERT_TRUE(last >= 0
    && (last & CTRL_VPP_REGULATOR_ENABLE) == 0
    && (last & CTRL_VPP_VPE_DROP_ENABLE_REV2) == 0);
/* paired non-vacuity: an EARLIER value must have had the route SET */
```
The `saw_earlier_set` non-vacuity pairing is already written out at `test_loop_eprom_v131.cpp:1277-1283` — copy that, it is the assertion that stops (b) from being *"vacuously true of a register that was never energised at all."*

---

## Gate and Budget Posture

### Cold flash / RAM — independently re-measured this session, not inherited

`pio run -t clean -e <env>` then `pio run -e <env>`, one uninterrupted invocation per env:

```
--- leonardo ---
RAM:   [========  ]  78.7% (used 2014 bytes from 2560 bytes)
Flash: [========= ]  92.1% (used 26400 bytes from 28672 bytes)
--- uno ---
RAM:   [========  ]  76.8% (used 1573 bytes from 2048 bytes)
Flash: [========  ]  75.7% (used 24424 bytes from 32256 bytes)
--- uno328pb ---
RAM:   [========  ]  77.1% (used 1579 bytes from 2048 bytes)
Flash: [========  ]  75.6% (used 24474 bytes from 32384 bytes)
```

Every figure in D-16 reproduces exactly. Against `size_baseline_base01.json` (`avr_targets`: uno 23932, uno328pb 23976, leonardo 26072): **+492 / +498 / +328** vs bands **64 / 64 / 0** (`check_size_baseline.py:107 MERGE05_UNO_CLASS_FLASH_BAND = 64`, `:240 band = 0 if env == "leonardo" else …`). MERGE-05 stays RED, as D-16 states.

**Leonardo headroom: 28672 − 26400 = 2272 B.** This is a **link failure** boundary, not a gate, and Phase 143 must also fit.

### Flash cost per design option (ESTIMATES — reasoned from the AVR ISA and this tree's own measured precedents; not measured, because measurement requires editing source)

| Option | Estimate | Reasoning |
|---|---|---|
| **Composites as `#define`** | **0 B** | `rurp_pinout.h:63-64` states the house rule outright: preprocessor constants "contribute 0 B to the `.hex` until referenced." A wider immediate mask costs 0-2 B at the use site (`0x186` vs `0x180` are both 2-byte immediates on a 16-bit `rurp_register_t`). |
| **Composites as `static inline` in a header** | **0 to +10 B** | avr-gcc inlines a mask-returning inline at `-Os`; risk is it does not, adding a call. `#define` is the safer choice under a 2272 B ceiling. |
| **Single-exit wrapper (rename body to `static`, public fn calls it + conditional disable)** | **−10 to +30 B, likely near-neutral** | `static` inner + one caller usually gets a tail-call or is inlined outright; the added cost is one `response_code` compare + one `set_control_register` call ≈ 12-20 B. D-10's "roughly flash-neutral" is plausible. Two wrappers (init + execute) ≈ 2× that. |
| **Disable call before every `return` (rejected alternative)** | **+40 to +80 B** | 4 call sites in `eprom_write_execute` × ~14 B each. The wrapper is *cheaper* as well as structurally stronger. |
| **Route resolver replacing two duplicated branches** | **−30 to −80 B (plausible shrink)** | Collapses two `if/else` pairs with two immediate masks each (`eprom.cpp:190-196`, `:340-346`) into one function + two calls, and deletes the `:217-219` branch (D-04). D-16's "plausibly shrinks … but that is a prediction, not a promise" is the right posture. |
| **Runtime revision gate inside `mem_util_calculate_top_address_register`** | **+20 to +45 B flash; runtime ~1% of a write** | `rurp_get_hardware_revision()` is a real out-of-line call (`rurp_hw_rev_utils.h:100`, declared `rurp_shield.h:151`) that itself calls `rurp_get_config()`. Two CALL/RET pairs + compares ≈ 30-50 cycles ≈ 2-3 µs per `set_address`; `set_address` runs twice per byte ⇒ ~5 µs/byte ⇒ ~0.33 s over a 64 KB write against a ~32 s total. **D-02's "adds no new class of cost" is correct (no ADC read); "free" would not be.** |
| Cheaper alternative for the gate, if the ceiling bites | — | Resolve the revision **once per block** in `eprom_write_execute` and carry it as a `handle` field (1 B RAM; leonardo has 546 B free). Costs a `firestarter_handle_t` change visible to every protocol — name it as a fallback, not a default. |

### Native warning watermark

`size_baseline.json` → `warnings.native.native.total_watermark = 1166`, `warnings.native.native_nodevtools.total_watermark = 1166`, `warnings.policy.native_rule = "<= total_watermark"`. Recorded == watermark ⇒ **zero headroom**. `check_build_warnings.py:164-167` fails when `total_count > watermark`; `:171-176` returns INFO (not a failure) when below.

**What would trip it** — only warnings emitted while compiling what `native` / `native_nodevtools` build: `src/proms/*.cpp`, `src/boards/rurp_serial_utils.cpp`, `src/json_parser.c`, `src/operation_utils.cpp`, every `include/` header they pull, and the **17** filtered suites. Concretely for this phase:
1. A **macro-redefinition** collision from a new `#define` in `rurp_pinout.h` (all 1166 existing warnings are macro redefinitions). Mitigated by the `EPROM_HV_*` prefix.
2. An **unused-variable** warning in `eprom.cpp` — e.g. removing `(void)vpp_path;` (`:234`) while leaving `vpp_path` unread on some path, or hoisting a row field the resolver then doesn't use.
3. Any `-Wunused-function` from the `static` inner function if a build configuration leaves it uncalled.

The new suite's own TU is **not** compiled by either gated env, so a warning there is invisible to this gate. Do not treat that as licence to emit one.

### D-18 — the protocol-branch inventory golden

`meta.how_to_update`, **verbatim**:

> If eprom.cpp or eprom_params.cpp legitimately change in a way that moves this inventory, re-derive it by running an independent parse against the new file (never hand-edit a line number, a keyed_on set, a class, or a count merely to make a surprise disappear), and state in the commit message which site changed, or was added or removed, and why. Diffing the extractor's live output against this JSON is the only sanctioned way to update it.

`meta.frozen_for`, **verbatim**:

> Phase 141 (plan 141-04) removed the retry-escalation loop (program_mismatched_bytes / verify_and_update_mask / NUMBER_OF_RETRIES) and replaced it with a per-byte pulse-to-verify loop -- this re-derivation (141-05) is that movement's record: tier-2 grew 21->24 (6 sites added, 3 removed), tier-1 held at exactly 3. Phase 142 is next to touch this file: it will rewrite the VPP branches, now at :190 (eprom_write_execute) and :340 (eprom_check_vpp), into the eprom_params table's vpp_path column, and will choose the final DIP32 route for the :217 pins >= 32 branch this phase added. Phase 142 MUST show up here as deliberate inventory movement (sites removed, or a tier-1 site's predicate spelling changing from raw 0x0B to PROTO_EPROM_24PIN), never as an unexplained prose claim. An unchanged site count across that phase would itself be suspicious and should be checked by hand.

Pinned state (all currently matching):
```
meta.blob_shas["src/proms/eprom.cpp"]        = b36d3c4c7c854c1d8b24ab262b1319f7111f11cf
meta.blob_shas["src/proms/eprom_params.cpp"] = 5dffe841aeb7013f9f53e9991a6248b203ae22da
meta.recorded_at_head                        = 3504e5042e36b307e332e03999f89f9034272fa1
counts = { total_sites: 27, protocol_keyed_sites: 3, other_sites: 24 }
```
`$ git hash-object src/proms/eprom.cpp src/proms/eprom_params.cpp`
→ `b36d3c4c7c854c1d8b24ab262b1319f7111f11cf`, `5dffe841aeb7013f9f53e9991a6248b203ae22da` — **match**. All 27 recorded line numbers match the current file. HEAD is `4921388` (later than `recorded_at_head`) because 141-06…141-08 were test-only.

The three tier-1 sites and their predicted fate:

| line | predicate | after Phase 142 |
|---|---|---|
| `:70` | `switch (handle->protocol)` (pulse fallback) | **survives** — D-01 forbids touching it |
| `:190` | `if (handle->protocol == 0x0B \|\| is_flag_set(FLAG_VPE_AS_VPP))` | **removed as tier-1** (D-05 resolver); the `FLAG_VPE_AS_VPP` half survives inside the resolver as a **tier-2** `ctrl_flags` site (D-06) |
| `:340` | identical text | same |

So the expected movement is **tier-1: 3 → 1**, plus tier-2 churn from `:217`'s deletion (D-04) and the resolver's new call sites. `test_protocol_branch_inventory.py:443-452` asserts `protocol_lines == [70, 190, 340]` **as a literal** — it goes RED the moment `:190` or `:340` moves.

**Re-derivation procedure (exact):**

1. There is **no standalone regenerator script.** `grep -rln protocol_branch_inventory scripts/ tests/` → only `tests/test_protocol_branch_inventory.py`. The extractor is `_extract_predicates(text)` (`:277-370`) inside the test module.
2. Site dicts have **six** keys: `line, predicate, keyed_on, tier, class, reason`. The gate compares only `(line, predicate, keyed_on, tier)` (`:419-426`). **`class` and `reason` are hand-authored prose the extractor cannot produce** — expect to re-write a `reason` paragraph for every moved site. Budget for it.
3. Re-derive by importing the module's own extractor and dumping live output — e.g. `python3 -c "import sys; sys.path.insert(0,'tests'); import test_protocol_branch_inventory as m, json; print(json.dumps(m._extract_predicates(m._SCAN_EPROM.read_text()), indent=1))"` — then diff against the committed `sites` array. Never hand-edit a line number.
4. Update `meta.blob_shas` from `git rev-parse HEAD:<path>` **after** the source commit, and bump `meta.recorded_at_head`, `meta.recorded_by`, `meta.frozen_for`.
5. Update the `[70, 190, 340]` literal at `test_protocol_branch_inventory.py:446` and its message text.
6. Also fix `meta.allowlist_rationale`'s stale `:145/:218/:320/:71` numbers (C-6) — the re-derivation is the natural moment.

**Timing asymmetry the planner must know:** `test_blob_shas_match_the_recorded_inventory` (`:398-414`) reads `git rev-parse HEAD:<path>` — the **committed** blob, so it goes RED only *after* commit. `test_branch_sites_match_the_recorded_inventory` (`:417-440`) reads the **working tree** (`_SCAN_EPROM.read_text()`, `:97-99`), so it goes RED the instant `eprom.cpp` is edited. Both are fixed by re-deriving the golden **in the same commit** as the source change.

**Tests RED until re-derivation:** `test_blob_shas_match_the_recorded_inventory`, `test_branch_sites_match_the_recorded_inventory`, `test_exactly_three_protocol_keyed_sites_at_the_pinned_lines`. The other four (`test_inventory_is_non_vacuous` ≥24 sites, `test_params_table_has_no_second_selector`, `test_default_targets_resolve_inside_this_repository`, `test_git_is_required_not_optional`) stay GREEN.

### Other gates and their arrival state

Whole pytest suite at the Phase 141 tip: **`256 passed in 10.68s`** (`python3 -m pytest tests/ -o addopts="" -q`). Note `addopts` is unset in this repo — no `-q` doubling problem here, unlike `firestarter_app`.

`tests/test_write_path_source_contract_v131.py` (12 legs) pins things this phase can break:
- `:397` `assert def_count == 1` for `eprom_internal_report_budget_failure` — **do not rename or delete it**; making it a caller of the shared composite is fine.
- `:402` `assert call_count >= 2` for calls to it.
- `:441/:446/:452` `len(eprom_hits) == 1`, `len(memory_hits) == 1`, `total == 2` — exactly one `mem_util_delay_us` call in each of `eprom.cpp` and `memory.cpp`.
- `:458-486` `_ALLOWED_DELAY_US_ARGS = {"settling","strobe","rem"}` scanned across **`src/ include/ lib/ platform/`** — any new `delayMicroseconds(x)` with a non-literal, non-allowed argument name anywhere in the firmware tree fails this.
- `:375-392` presence counts for `firestarter_set_data`, `firestarter_get_data`, `MSG_ERR_MAX_PULSES`, `MSG_ERR_ENERGY_CAP` — all `> 0`.

`tests/test_golden_trace_identity_eprom_v131.py` pins the blob SHA of the **fixture** `eprom_v131_expected.h`, not `eprom.cpp` — it stays GREEN as long as the fixture is untouched (D-17 concerns the *suite*, not this gate).

`tests/test_eprom_params_citations.py` stays GREEN — D-01 forbids `eprom_params.cpp` data changes.

---

## Validation Architecture

> `.planning/config.json` has no `workflow.nyquist_validation` key ⇒ treated as **enabled**. This section is the input to `142-VALIDATION.md`.

### Test Framework

| Property | Value |
|---|---|
| Native framework | PlatformIO Unity (`test_framework = unity`), `platform = native` |
| Env for new work | `[env:native_loop_v131]` (`platformio.ini:373-414`) — **existing**, extended by two lines |
| pytest gates | plain `pytest`, no config file, no `addopts` (`firestarter/tests/`) |
| Quick run (new suite) | `pio test -e native_loop_v131 -f "*test_vpp_eprom_v131*"` |
| Quick run (regression, loop) | `pio test -e native_loop_v131` |
| Full native gate | `pio test -e native` **and** `pio test -e native_nodevtools` (must stay 141/17/all-passed) |
| Full pytest gate | `python3 -m pytest tests/ -o addopts="" -q` (256 at arrival) |
| Flash measurement | `pio run -t clean -e <env>` then `pio run -e <env>`, per env, one invocation |
| **Never** | `check_size_baseline.py` / `check_build_warnings.py` with `native_loop_v131` (F-138-05, exit 1 / exit 2) |

### Per-requirement oracles

#### VPP-01 — `0x07`/`0x08` route through regulator + drop; `0x0B` direct; selection from `vpp_path`

| Claim | Provable off-hardware? | Oracle |
|---|---|---|
| `0x07` (pins 28) asserts `REGULATOR\|DROP` and the drop bit survives every `set_address` of the block | **YES** | `native_loop_v131` strobe stream. Existing precedent is already green: `test_loop08_the_28_pin_row_keeps_its_drop_bit` (`:1634-1663`) walks every `control_write_value(i)` and asserts `CTRL_VPP_VPE_DROP_ENABLE_REV1` set. |
| `0x08` (pins 32) **now** keeps `REGULATOR\|DROP` across the block on Rev 2-class (D-01/D-02/D-04) | **YES — this is the phase's headline provable claim** | Same recorder, with `rurp_get_config()->hardware_revision = REVISION_2_2` (mandatory: on the default `REVISION_0` the drop bit and A16 both map to physical `0x01` and the claim is undecidable — `test_loop_eprom_v131.cpp:1511-1523` documents exactly this). The **inversion** of `test_loop08_dip32_drop_bit_is_cleared_deliberately_before_the_first_pulse` (`:1573-1632`) is the natural new case; that existing case must be **rewritten or deleted by this phase**, and that is a deliberate, nameable act. |
| `0x08` on Rev 0 / Rev 1 keeps **today's** stripping (D-02) | **YES** | Same suite, `hardware_revision = REVISION_1`, asserting the drop bit is absent from every control value after the first `set_address`. Rev 1 (not Rev 0) is the load-bearing case — Rev 0 is separately refused at `eprom.cpp:334-338`. |
| Unknown revision keeps today's stripping (fail-safe) | **YES** | Same suite, `hardware_revision = REVISION_UNKNOWN` (`0xFE`). Cheap; closes the `rurp_hw_rev_utils.h:33-37` direction. |
| `0x0B` asserts `REGULATOR` **without** drop | **YES** | Strobe stream: no `CTRL_VPP_VPE_DROP_ENABLE_REV2` bit in any control value. |
| Selection is driven by `vpp_path`, not a `protocol ==` switch | **YES, two independent oracles** | (a) behavioural — the resolver returns the drop mask for `0x07`/`0x08` and the direct mask for `0x0B`, which is what the strobe cases above show; (b) **structural** — `test_protocol_branch_inventory.py`'s re-derived golden showing tier-1 dropping 3 → 1. (b) is the one that proves the *mechanism* rather than the outcome. |
| `--vpe-as-vpp` still forces the direct path on `0x07`/`0x08` (D-06) | **YES** | `h.ctrl_flags \|= FLAG_VPE_AS_VPP`, assert no drop bit. |
| **The `0x08` route change is correct on silicon** | **NO — EXPLICIT NON-CLAIM (D-03)** | Bench-only, and deliberately not attempted. Independent evidence that a bench attempt would be a poor oracle: `PROJECT.md:560` records AM27C020 as *"RCA'd, 0-bits-programmed, JP4-closed didn't fix; not trivially fixable"*, and v1.18 Phase 99 measured write#1 60/64 then write#2 0/64. |
| **F-141-09 hazard** | — | The proof **must** be built on `HOST_STUBS_REAL_REGISTER_UTILS`, whose hooks (`rurp_write_data_buffer`, `rurp_set_control_pin`, `host_stubs_common.inc:204-209`) sit **below** `rurp_write_to_register`'s cache-compare elision (`rurp_register_utils.h:39-41`). An elided write produces no strobe — same as hardware. `HOST_STUBS_RECORD_BUS` is doubly unusable: it records calls the hardware never sees, **and** it truncates the `0x100` drop bit to zero (`host_stubs_common.inc:228`, documented at `test_val_eprom.cpp:92-96`). |

#### VPP-02 — every write-path exit disables every active route

| Exit (§Control-Register Assertion Map E) | Provable off-hardware? | Oracle |
|---|---|---|
| X2 `:268` `MSG_ERR_MAX_PULSES` | **YES** — already partly covered | `test_loop05_the_loops_own_strobes_disable_the_high_voltage_route` (`:1246-1284`) asserts last control value has `REGULATOR` clear. **Extend it** to also assert `CTRL_VPP_VPE_DROP_ENABLE_REV2` clear — that is the genuinely new content, because on `pins<32` the drop bit is left asserted today. |
| X3 `:275` `MSG_ERR_ENERGY_CAP` | **YES** | Same shape, protocol `0x0B` at 500 µs (the only row with `energy_cap_us > 0`). |
| X4 `:311` `MSG_ERR_VERIFY` | **YES — the highest-value new case** | Seed a byte that converges in the per-byte loop but mismatches in the final pass. The `loop_readback` model supports it: `converge_after = N` makes read N+1 match, so a `read_count`-sensitive target flips on the final pass. Assert last control value has `REGULATOR` **and** drop clear. Today this exit disables **nothing**. |
| X1 `:226` `row == NULL` | **structurally unreachable** — refused at `eprom.cpp:86-90` | Not testable behaviourally. Covered *structurally* by the wrapper: name it as covered-by-construction, do not fake a case. |
| X5 `:315` success | **YES, as a negative control** | `test_loop05_a_successful_block_does_not_disable_the_route` (`:1286-1309`) **must stay green** — it is the assertion that stops the wrapper from being an unconditional disable (C-1). |
| E1/E2 (`eprom_write_init`) | **YES** | Already clear today (C-3); the wrapper is defensive. A single case asserting the last control value is route-clear after a `write_init` that errors is cheap non-regression. |
| `command_done()` actually zeroes the registers (D-09's owed test) | **YES, but not in a native suite** | `firestarter.cpp` is excluded from every native env's `build_src_filter` (`+<proms/> +<boards/rurp_serial_utils.cpp> +<json_parser.c> +<operation_utils.cpp>`), and `host_stubs_common.inc:317-325` stubs `op_reset_timeout` precisely because that TU is absent. **Two honest options:** (a) a **source-contract pytest** leg in `tests/` asserting `command_done`'s body contains the three `rurp_write_to_register(<reg>, 0x00)` lines and that both call sites (`:176`, `:290`) exist — cheap, greppable, in the `test_write_path_source_contract_v131.py` idiom already used in this repo; (b) widen a native env's `build_src_filter` to include `firestarter.cpp` — costs a `main()` collision and a new env, which D-14 forbids. **Recommend (a), and label it a source-contract claim, not a behavioural one.** |
| The address-bus `vpp_line` bit is cleared on write-path exit | **NO — EXPLICIT NON-CLAIM (D-11)** | `memory.cpp:418-420` sets `1UL << config.vpp_line` ignoring `read_write`; clearing it would change read-path behaviour. Cleared only by `command_done()` (`firestarter.cpp:167-168` zero the LSB/MSB latches, and `:166` the control register). |
| Physical de-assertion of the P1/VPP line when logical `A18` is set (Rev 2-class) | **NO — NEW EXPLICIT NON-CLAIM (C-4)** | `rurp_pinout.h:127` aliases them. Not reachable from a 27C write (analysis in C-4), but the composite's guarantee is *logical*, not physical, and the record should say so. |

#### VPP-03 — one shared mask set

| Claim | Provable off-hardware? | Oracle |
|---|---|---|
| `eprom_check_vpp` and the write path resolve the route through the same code | **YES, two oracles** | (a) **structural** — a pytest source-contract leg asserting `eprom.cpp` contains exactly **one** definition of the resolver and **≥2** calls, and **zero** remaining `handle->protocol == 0x0B` occurrences (the `test_write_path_source_contract_v131.py:387-402` def-count/call-count idiom, and its `_NEEDLE_*` string-splitting trick at `:163-166` so the gate module's own text does not match itself). (b) **behavioural** — for a given `(protocol, pins, ctrl_flags, revision)`, the mask `eprom_check_vpp` asserts equals the mask the write path asserts. **This is the honest headline of the phase (D-03): today they differ for `0x08` (`:345` measures with drop on; `:218` strips it).** A case that shows the *same* physical control byte from both is the direct proof. |
| The `:174`/`:327`/`:393`/`:409` conversions are byte-identical on the wire | **YES** | Strobe-count and strobe-value equality for a `CMD_ERASE` and a `CMD_CHECK_CHIP_ID` drive, before vs after. This is the cheapest possible defence of the `PROJECT.md:189-190` boundary — **do not assert byte-identity in prose; measure it.** |
| No composite is duplicated | **YES** | pytest: exactly one `#define EPROM_HV_ALL_OFF_MASK` in `include/`, and zero literal `CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE` sequences left in `eprom.cpp`. |

#### VPP-04 — the over-voltage refusal still blocks

| Claim | Provable off-hardware? | Oracle |
|---|---|---|
| (a) injected out-of-range reading → `MSG_ERR_VPP_HIGH` + `RESPONSE_CODE_ERROR` | **YES** | New suite, `HOST_STUBS_CUSTOM_VOLTAGE_MV` + `set_mock_vpp_mv(vpp_mv + 501)`, `hardware_revision = REVISION_2_2`, assert `logged_id` contains `MSG_ERR_VPP_HIGH` (0xB8) **by id** — no test in the tree does this today. |
| (b) no HV route left asserted on that refusal path | **YES, but green on arrival (C-3)** | Strobe stream; **must be planted-RED** (e.g. temporarily make `eprom.cpp:370-371` an early `return`) before its GREEN means anything. |
| (c) `FLAG_FORCE` downgrades to `MSG_WARN_VPP_HIGH` + `RESPONSE_CODE_WARNING` | **YES** | Same drive with `FLAG_FORCE`; assert id `0x82`. |
| VPP-04's premise ("re-verified against the **existing** gate") | **FALSE — the requirement's own premise does not hold** | Confirmed by grep (D-13). The requirement is discharged by **authoring** the gate and recording the correction. `test_flash_intel_vpp` is not a substitute — it is protocol `0x10`, and per C-2 it runs in no environment and aborts before its own SAF-04 case. |
| The refusal blocks on real silicon at a real over-voltage | **NO — bench-only, not attempted** | The 6.25 V evidence ceiling (`ROADMAP.md:157`) and D-03 both apply. |

### What no off-hardware oracle can establish (non-claims, to be stated in the record)

1. `0x08` silicon behaviour after the route change (D-03).
2. That the drop resistor actually produces ~13 V — no ADC is read in any native suite; `rurp_read_voltage_mv` is a mock.
3. **Any timing change.** `delay()` / `delayMicroseconds()` are ArduinoFake free functions; the timing recorder stores **arguments only**. `host_stubs_common.inc:135-145` states it: *"delay()/delayMicroseconds() are not stubbed anywhere in this file at all … the hook that calls `timing_push()` lives in the DEFINING SUITE's own `setUp()`."* A trace diff can prove *which* delay was requested, never how long anything took.
4. Physical de-assertion where the mapper aliases two logical bits (C-4, and the Rev 0/1 drop↔A16 case).
5. That `command_done()` runs on the real AVR abort path — the timeout arm (`firestarter.cpp:169-171`) depends on `millis()` and is outside every native suite's reach.

### Sampling rate

- **Per task commit:** `pio test -e native_loop_v131` (0.8 s at arrival). Plus `python3 -m pytest tests/ -o addopts="" -q` — **but see the F-141-11 landmine: commit first.**
- **Per wave merge:** `pio test -e native` + `pio test -e native_nodevtools` (must stay 141/17/all-passed) + full pytest + `pio run -e uno/-e uno328pb/-e leonardo` (leonardo must **link** — 2272 B headroom).
- **Phase gate:** all of the above, plus cold `pio run -t clean` on all three AVR targets for the D-16 record, plus `native_trace_v131` **expected RED** named in the record so `/gsd-verify-work` reads it as expected.

### Wave 0 gaps

- [ ] `test/native/avr/test_vpp_eprom_v131/host_stubs.cpp` — `HOST_STUBS_REAL_REGISTER_UTILS` + `HOST_STUBS_RECORD_TIMING` + `HOST_STUBS_CUSTOM_READ_DATA_BUFFER` + **`HOST_STUBS_CUSTOM_VOLTAGE_MV`**, `reset_register_cache`, the readback model, the `rurp_log_id` capture. Largely a copy of `test_loop_eprom_v131/host_stubs.cpp` plus the voltage mock.
- [ ] `test/native/avr/test_vpp_eprom_v131/test_vpp_eprom_v131.cpp` — `setUp` mocking all four ArduinoFake timing functions; `tearDown` resetting `hardware_revision` unconditionally; a `drive_vpp_init(...)` helper that calls `firestarter_operation_init` (NOT `drive_loop_write`, which deliberately skips `_init`).
- [ ] `platformio.ini` — the two lines above.
- [ ] Re-derived `tests/golden/protocol_branch_inventory.json` + the `[70, 190, 340]` literal at `test_protocol_branch_inventory.py:446`.
- [ ] A `command_done()` source-contract leg (D-09's owed test) — new legs in `tests/`, or a new module.
- [ ] Decide the fate of `test_loop08_dip32_drop_bit_is_cleared_deliberately_before_the_first_pulse` (`test_loop_eprom_v131.cpp:1573-1632`) — its claim is **inverted** by D-01/D-04 on Rev 2-class. Rewriting it is required; doing so silently is not acceptable.
- [ ] Nothing else. No new env, no baseline JSON edit, no `messages.toml`, no codegen, no host change.

### D-15 discipline

Every new leg seen RED on a planted violation, transcript verbatim in the plan SUMMARY (12 planted runs in Phase 140, 13 in Phase 141). Three legs need explicit planted-RED design because they are **green on arrival**:
- VPP-04(b) — plant an early `return` at `eprom.cpp:370-371`.
- VPP-02 X2's widened drop-bit assertion — plant by reverting the composite at `:174` to `REGULATOR` alone.
- The `command_done()` source-contract leg — plant by pointing the scanner at a fixture with one of the three zeroing lines removed.

---

## Landmines

**L-1 — `tests/test_flash_path_record_sync.py:1247` asserts the WHOLE firmware repo is clean.**
```python
assert _git_porcelain(_FW_REPO_ROOT) == "", (
    "the firmware repo's working tree is no longer clean after "
    "the planted-copy test"
)
```
`_git_porcelain` (`:252-262`) runs `git -C <repo> status --porcelain`. Any uncommitted change anywhere in `firestarter/` — including the very file being edited — turns this RED. **Working rule: `git add -A && git commit` before running the full pytest suite.** F-141-11, orphaned and unassigned; do not fix it here.

**L-2 — one plan must own all `eprom.cpp` edits, and it is achievable here.**
The D-18 golden pins `eprom.cpp`'s blob SHA, and the working-tree site test goes RED on the first keystroke (§Gate and Budget Posture). Phase 141 confined all `eprom.cpp` edits to one plan so the gate went RED once, for one reason. **That is achievable in Phase 142**, because `memory.cpp` and `rurp_pinout.h` are **not** pinned by that golden — `meta.sources` is exactly `["src/proms/eprom.cpp", "src/proms/eprom_params.cpp"]`, and `eprom_params.cpp` is read-only this phase (D-01). Recommended decomposition:

| Plan | Touches | Golden impact |
|---|---|---|
| **P1** (Wave 0) | `rurp_pinout.h` (composites), `platformio.ini` (2 lines), the new suite skeleton + planted-RED transcripts | none |
| **P2** | `memory.cpp` only — the `pins`/revision-gated preserve mask (D-01/D-02) + its native cases + a non-EPROM no-leak proof | none |
| **P3** | **`eprom.cpp` only, once** — resolver (D-05), delete `:217-219` (D-04), wrapper (D-10, conditional per C-1), convert `:174`/`:327`/`:393`/`:409` to the composite (VPP-03) — **and, in the same commit, the re-derived golden + the `:446` literal** | RED→GREEN inside one commit |
| **P4** | VPP-04 gate legs, the `command_done()` source contract, `firestarter/CLAUDE.md` `0x08` row, the phase record + cold measurements | none |

P2 before P3 matters: P2's preserve-mask change makes the drop bit *survivable* on Rev 2-class; P3's deletion of the explicit `:217-219` clear then becomes the fix rather than a no-op. Landing P3 first would briefly leave `0x08` with no drop route at all.

**L-3 — `mem_util_calculate_top_address_register` is shared by EVERY protocol.**
`memory.cpp:163-200`, sole caller `mem_util_set_address:230`, which is `handle->firestarter_set_address` for **every** protocol (`memory.cpp:92`). The D-01/D-02 change sits inside the `handle->pins < 32` guard, so a non-EPROM protocol can only be affected if it runs with `pins >= 32` — which includes `PROTO_SRAM_32PIN` (`0x0E`), `PROTO_SRAM_32PIN_NVRAM` (`0x29`), `PROTO_FLASH_INTEL` (`0x10`) and 32-pin flash. **Cheapest no-leak proof:** a native case in the new suite that drives a 32-pin **non-EPROM** protocol (`0x10` is ideal — it uses `CTRL_VPP_P1_ENABLE`, a different route) with `hardware_revision = REVISION_2_2` and asserts the recorded control-value sequence is **identical before and after** the change. Cheaper still, and complementary: assert the new drop-bit membership is reached only when the *protocol-supplied* condition holds, i.e. gate the new mask bit on something no non-EPROM protocol can satisfy. **`test_val_sram` and `test_val_flash_intel` are both in the pinned 17** and will catch a gross regression for free — but they use `HOST_STUBS_RECORD_BUS`, which cannot see the `0x100` bit, so they are **not** sufficient.

**L-4 — `eprom_check_vpp()` runs for EVERY EPROM command; the blast radius of changing its route resolution is 6 commands, not 1.**
`eprom_generic_init` (`eprom.cpp:412-420`) calls it at `:413`, and `configure_eprom:43` makes `eprom_generic_init` the **default** `firestarter_operation_init`. `eprom_check_chip_id_init:114` and `eprom_write_init:129` also reach it. Reachable commands: `CMD_READ`, `CMD_WRITE`, `CMD_VERIFY`, `CMD_ERASE`, `CMD_BLANK_CHECK`, `CMD_CHECK_CHIP_ID`. Quantified consequence: making `eprom_check_vpp` resolve the route through `eprom_hv_route_mask(handle)` changes the emitted control-register value for **`0x08` on every one of those six commands**, including reads. Two guards:
- `test_val_eprom`'s six cases (in the pinned 17) cover exactly this surface for all three protocols, write-init **and** read-configure (`test_val_eprom.cpp:210-217`). They must stay green. They will, because they only assert `CTRL_VPP_REGULATOR_ENABLE` presence/absence, which does not move. **Note `test_val_eprom`'s handles have `pins == 0`** (`make_handle`, `:69-79`, zero-init) ⇒ any `pins`-keyed arm sees `pins == 0` and takes the `< 32` path.
- The `PROJECT.md:189-190` boundary ("VPP validation behavior — unchanged except where required for safe shared cleanup") is satisfied because closing the measure/apply divergence **is** the shared cleanup — but say that explicitly rather than letting it be inferred.

**L-5 — `PROGMEM` row reads.** `eprom_params_for()` returns a pointer into PROGMEM (`eprom_params.h:71-77`: *"every field must be read back with `pgm_read_byte` / `pgm_read_dword`, never dereferenced directly (a direct read compiles and silently returns RAM garbage on AVR)"*). The resolver must use `pgm_read_byte(&row->vpp_path)`. It also must handle `row == NULL` (`eprom_params.cpp:61`) — and if `eprom_check_vpp` starts calling the resolver, it acquires a NULL path it does not have today. `configure_eprom:86-90` already refuses an unknown protocol, so it is unreachable in practice; fail closed anyway (the drop-resistor path is the *safer* default per `eprom.cpp:82-84`).

**L-6 — `HOST_STUBS_RECORD_BUS` cannot see the drop bit; `HOST_STUBS_REAL_REGISTER_UTILS` cannot see it on Rev 0/1.** Both halves matter. `host_stubs_common.inc:228` truncates to `uint8_t`; and on the default `REVISION_0` mapping the drop bit and A16 both become physical `0x01`. Every drop-bit assertion needs **both** the real-register-utils layer **and** an explicit `REVISION_2_x` override.

**L-7 — `rurp_register_utils.h`'s globals persist across Unity cases.** `lsb_address`, `msb_address`, `control_register` are non-`static`, initialised to `0xff` (`:12-14`). `0xff` ORs `CTRL_VPP_REGULATOR_ENABLE` into the first write of any case that does not call `reset_register_cache(0,0,0)`. Every case must reset deliberately (`test_loop_eprom_v131/host_stubs.cpp` header comment states this as a named seam).

**L-8 — `native_trace_v131` is RED and must be *named* as expected-RED, not silenced.** Observed: `3 failed, 2 succeeded`, `[ERRORED]`, `SIGQUIT`. D-17 forbids re-freezing. This phase changes the strobe stream again (D-01, D-04, D-10), so the failure *values* will change; that is expected and is not evidence of anything.

**L-9 — the `0xBF` slot.** `messages.h` `0xA0`–`0xBE` are fully occupied; `0xBF` is the only free ERROR id and Phase 143 wants it. Any design that needs a new refusal id is a **checkpoint to the operator** (D-08), not a quiet claim.

**L-10 — dead code that the rewrite will brush against.** `eprom_internal_ensure_regulator_enabled` (`eprom.cpp:449-454`) has zero callers and duplicates the `:189-198` guard. Decide about it explicitly; removing it deletes tier-2 inventory site `:450` and moves the golden.

**L-11 — `firestarter/CLAUDE.md` goes stale the moment D-01 lands.** Its `0x08` row carries a "Pre-existing defect" paragraph describing exactly the behaviour D-01 changes, and its `0x07`/`0x08` VPP column says "13V via `CTRL_VPP_VPE_DROP_ENABLE`". Both must move in the same change (CONTEXT's Integration Points; and `firestarter/CLAUDE.md` is firmware documentation for code this phase changes, unlike `PROJECT.md:125-127` which is Phase 146's).

**L-12 — no v1.31 claim gate exists yet.** CLOSE-01's `check_permitted_claims.py` is Phase 146's (`ROADMAP.md:183`, `:390`); Phase 139 shipped only a Phase-139-scoped `139-check-claims.py`. So D-03's non-claim discipline in the Phase 142 record is **prose-enforced only** this phase — say so rather than implying a gate protects it.

---

## Open Questions for the Planner (RESOLVED)

> **All seven are resolved.** Four were decided during planning and three were settled by the
> operator as amendments in `142-CONTEXT.md`. Each resolution is annotated inline below and is
> restated in the owning plan's objective and in `ROADMAP.md`'s Phase 142 block. Nothing in this
> section is still open; the question text is retained so the reasoning that produced each answer
> stays legible.

1. **`test_loop08_dip32_drop_bit_is_cleared_deliberately_before_the_first_pulse` — rewrite or delete?**
   `test_loop_eprom_v131.cpp:1573-1632`. Its central assertions (`:1610-1615`, `:1626-1631`) are **inverted** by D-01/D-04 on Rev 2-class. Rewriting it into its own inverse is the honest move (it becomes VPP-01's positive proof), but the plan must say which it is doing. Not decidable from source — it is an authoring choice.
   **RESOLVED — REWRITE in place, renamed** `test_vpp01_dip32_drop_bit_survives_the_block_on_rev2_class`, owned by plan **142-04** (parts I-K of its single task). Its `v0` drop-bit-SET assertion survives as the non-vacuity partner; `test_loop08_the_28_pin_row_keeps_its_drop_bit` stays its paired control.

2. **Does the phase change `test_loop05_a_successful_block_does_not_disable_the_route`, or does the wrapper stay conditional?** See C-1. Recommendation: keep the test, make the wrapper conditional. If the operator wants a literal unconditional disable, the ~64 s cost D-09 rejected returns and the decision must be re-opened with them. **This is the single most consequential open item.**
   **RESOLVED — the wrapper is CONDITIONAL on `handle->response_code == RESPONSE_CODE_ERROR`**, operator-confirmed as the **D-10 amendment** (`142-CONTEXT.md`, correction C-1). The literal word "unconditionally" in D-10's original text is given up; `test_loop05_a_successful_block_does_not_disable_the_route`'s assertion stays green and unchanged. Implemented by plan **142-04**, exercised by plan **142-05**.

3. **What exactly gates the new drop-bit preserve — revision alone, or revision AND something protocol-supplied?**
   `mem_util_calculate_top_address_register` sees only `handle` and `address`. Revision alone (`REVISION_2_x` ⇒ preserve `DROP` for all `pins`) is the minimal reading of D-01/D-02, but it changes behaviour for **every** 32-pin protocol on Rev 2-class, not just `0x08` (L-3). A narrower gate needs a protocol- or route-derived signal, and the only zero-RAM way to get one into that function is `handle->protocol` — which would create a **fourth tier-1 protocol-keyed site** and violate TABLE-05. The alternatives are a new 1-byte `handle` field set once per block, or accepting the wider blast radius with an explicit no-leak proof. **Not resolvable from source; needs a planner decision, and it is the choice most likely to need operator sign-off.**
   **RESOLVED — REVISION ALONE**, with the wider blast radius accepted and paid for by an explicit 32-pin **non-EPROM** byte-identity proof (L-3's cheapest no-leak oracle). Operator-confirmed as the **D-02 amendment**; no new `handle` field, no protocol key, so no fourth tier-1 site and no TABLE-05 violation. Owned by plan **142-02**.

4. **Where does the resolver live, and is it exposed to the native suite?**
   `eprom.cpp` (file-static) is cheapest, but then the resolver can only be tested through its effects on the strobe stream. Exposing it via `eprom.h` (the `eprom_overprogram_us` precedent at `eprom.h:34`) buys a direct unit oracle for `(protocol, pins, flags, revision) → mask` at a few bytes of flash. Recommendation: **expose it** — the truth table is the clearest possible VPP-01 evidence and it makes the Rev 0/1/UNKNOWN arms testable without a full drive.
   **RESOLVED — EXPOSE via `include/eprom.h`**, following the `eprom_overprogram_us` precedent (`eprom.h:18-35`) and adding no new include edge (`rurp_register_t` is already reachable through `firestarter.h`). Declared and defined by plan **142-04**; its `(protocol, ctrl_flags)` truth table, including the fail-closed NULL-row arm no drive can reach, is plan **142-05**'s first oracle.

5. **JP4's electrical function.** C-7. Not resolvable from the two documents in this repo, and it does not block implementation. Needs an operator answer before the phase record can assert anything about JP4; the safe path is to cite the operator's own framing (a physical jumper controls pin-1 VPP on DIP32) without naming a designator or asserting a net.
   **RESOLVED — do NOT name the designator and do NOT assert a net.** Operator-confirmed as the **D-01 amendment**: the phase cites only that a physical jumper controls pin-1 VPP on DIP32, and the documentation contradiction is **logged as a finding** (C-7, documentation owner, logged not resolved) in plan **142-07**'s findings register rather than resolved here.

6. **`eprom_internal_ensure_regulator_enabled` — fold, delete, or leave?** L-10. Folding it into the resolver is the tidiest and is arguably what VPP-03 asks for; leaving it is the smallest diff. Either is defensible; silence is not.
   **RESOLVED — DELETE it.** Zero callers, no header declaration, and it duplicates the `:189-198` regulator guard the resolver now owns; `--gc-sections` already collects it, so deletion reclaims 0 B and there is no flash argument for keeping it. Its tier-2 site `:450` disappearing is the deliberate inventory movement `meta.frozen_for` demands. Owned by plan **142-04**; its absence is additionally pinned by plan **142-06**'s source contract.

7. **Should the `command_done()` test be a source-contract pytest or is a behavioural oracle wanted?** §Validation Architecture VPP-02. A source contract is cheap and honest but proves only that the source says the right thing. A behavioural oracle needs `firestarter.cpp` in a native `build_src_filter`, which collides with `main()` and would need a seventh env — forbidden by D-14. Recommendation: source contract, labelled as such.
   **RESOLVED — SOURCE CONTRACT, labelled as such.** A behavioural oracle would need `firestarter.cpp` in a native `build_src_filter`, which collides with `main()` and would need a seventh env (forbidden by D-14). Owned by plan **142-06** in the new module `tests/test_hv_routing_source_contract_v142.py`, which asserts `command_done()`'s three zeroing writes inside its own brace-matched body and both dispatch call arms individually.

---

## Sources

### Primary — this repository, read directly (HIGH confidence)

`firestarter/src/proms/eprom.cpp` (whole file, 454 lines) · `firestarter/src/proms/memory.cpp:55-424` · `firestarter/src/proms/eprom_params.cpp` · `firestarter/src/firestarter.cpp:126-291` · `firestarter/include/rurp_pinout.h` · `firestarter/include/rurp_hw_rev_utils.h` · `firestarter/include/rurp_register_utils.h` · `firestarter/include/rurp_types.h` · `firestarter/include/memory_utils.h` · `firestarter/include/eprom_params.h` · `firestarter/include/eprom.h` · `firestarter/include/rurp_shield.h:25-42, :138-165` · `firestarter/include/messages.h:71-107` · `firestarter/platformio.ini` (whole) · `firestarter/test/native/avr/_shared/host_stubs_common.inc` (whole) · `firestarter/test/native/avr/test_loop_eprom_v131/{host_stubs.cpp,test_loop_eprom_v131.cpp}` · `firestarter/test/native/avr/test_val_eprom/{host_stubs.cpp,test_val_eprom.cpp}` · `firestarter/test/native/avr/test_flash_intel_vpp/{host_stubs.cpp,test_flash_intel_vpp.cpp}` · `firestarter/tests/test_protocol_branch_inventory.py` · `firestarter/tests/test_write_path_source_contract_v131.py` · `firestarter/tests/test_flash_path_record_sync.py` · `firestarter/tests/golden/protocol_branch_inventory.json` · `firestarter/scripts/check_size_baseline.py` · `firestarter/scripts/check_build_warnings.py` · `firestarter/scripts/baseline/size_baseline.json` · `firestarter/scripts/baseline/size_baseline_base01.json` · `firestarter/doc/SHIELD-REVISIONS.md` §§6-7 · `firestarter/CLAUDE.md` · `firestarter_app/firestarter/{cli_handlers.py,eprom_operations.py}` · `.planning/{PROJECT.md,ROADMAP.md,REQUIREMENTS.md,STATE.md,v1.7-SHIELD-REVS.md}` · `.planning/phases/141-per-byte-program-loop/141-LOOP-RECORD.md`

### Primary — commands executed this session (HIGH confidence)

```
git rev-parse HEAD                                        -> 4921388522d9c6a36651cb9e42a09dea641bcb89
git status --porcelain                                    -> (empty)
git hash-object src/proms/eprom.cpp src/proms/eprom_params.cpp
                                                          -> b36d3c4c… / 5dffe841…  (== pinned)
python3 -m pytest tests/ -o addopts="" -q                 -> 256 passed in 10.68s
pio run -t clean -e leonardo && pio run -e leonardo        -> RAM 2014/2560, Flash 26400/28672 (92.1%)
pio run -t clean -e uno && pio run -e uno                  -> RAM 1573/2048, Flash 24424/32256 (75.7%)
pio run -t clean -e uno328pb && pio run -e uno328pb        -> RAM 1579/2048, Flash 24474/32384 (75.6%)
pio test -e native                                         -> 141 test cases: 141 succeeded, 17 suites PASSED
pio test -e native_loop_v131                               -> 39 test cases: 39 succeeded (1 suite)
pio test -e native_trace_v131                              -> ERRORED; 6 cases: 3 failed, 2 succeeded (expected, D-17)
pio test -e native -f "*test_flash_intel_vpp*"             -> ERRORED after case 1 (SIGABRT); 2 cases: 1 succeeded
grep -rn "MSG_ERR_VPP_HIGH|MSG_WARN_VPP_HIGH" test/ tests/ -> no output
grep -rn "eprom_internal_ensure_regulator_enabled" src/ include/ -> definition only, zero callers
grep -rn "JMP_VPP_P1_BYPASS|P1_VPP_JMP" src/ include/      -> no match (doc-only alias)
grep -rn "command_done" src/ test/                         -> 4 decls/defs/calls + 1 prose + 4 comments; zero assertions
suite-dir vs test_filter set difference                    -> only test_flash_intel_vpp is unfiltered
platformio.ini test_filter/-I entry counts                 -> native 17/17, native_nodevtools 17/17
```

### Secondary — MEDIUM confidence

Flash-cost estimates in §Gate and Budget Posture are reasoned from the AVR ISA plus this tree's own recorded precedents (`rurp_hw_rev_utils.h:52` records "~30 B added Flash" for an 8-sample ADC average; `rurp_pinout.h:63-64` records the 0-B `#define` rule). Labelled as estimates; a plan must measure, not inherit them.

### Not used

No Context7, WebFetch, or WebSearch lookup was performed. Every claim in this document is about code and artifacts in this repository, so external documentation would have added nothing verifiable. This is a deliberate scoping decision, not an omission.

---

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|---|---|---|
| A1 | The `test_flash_intel_vpp` SIGABRT is caused by `millis()` being unmocked (`flash_intel.cpp:162-163`, `flash_utils.cpp:34-35`) while `setUp` mocks only `delay` | C-2 | Labelled **UNVERIFIED** in place. The *fact* that the suite runs in no env and aborts before its SAF-04 case is measured, not assumed; only the mechanism is a hypothesis. If wrong, the new suite might inherit an abort — mitigated by mocking all four timing functions regardless. |
| A2 | Flash-cost figures per design option | Gate and Budget Posture | Labelled ESTIMATES. If the wrapper + resolver + revision gate net *positive* rather than neutral, leonardo's 2272 B headroom absorbs it comfortably; the risk is to Phase 143, not to this phase. Measure cold per plan. |
| A3 | The `:174`/`:327`/`:393`/`:409` composite conversions are byte-identical on the wire | Control-Register Assertion Map; VPP-03 | Reasoned from the clear-only semantics of `memory_set_control_register` plus the ordering of `eprom_check_vpp:393` before `eprom_internal_erase`. **Do not assert it in prose — measure the strobe stream.** If wrong, `CMD_ERASE`/`CMD_CHECK_CHIP_ID` behaviour moves, which `PROJECT.md:189-190` forbids. |
| A4 | The A18/P1 physical aliasing (C-4) is unreachable on the 27C write path | C-4 | Derived from `VPP_P1_32_DIP == 0x15 == 21`, `using_p1_as_vpp` suppressing the bit-21 set at `memory.cpp:418`, and 27C 32-pin parts having VPP on pin 1. Not exhaustively checked against every `0x08` row's `bus_config` in `chip_database.json` (host-side, out of this phase's repo scope). If wrong, an all-off composite naming `P1` could be ineffective on Rev 2-class — which is exactly why the recommended composite does **not** name `P1`. |
| A5 | The composite `#define` naming `EPROM_HV_*` collides with nothing | Shared Mask Placement | Verified by `grep -rn "EPROM_HV"` → no match, but that only covers today's tree, not ArduinoFake's or avr-libc's macro namespaces. A collision would surface as a macro-redefinition warning against the zero-headroom 1166 watermark — visible immediately on the first `pio test -e native`, so it fails loudly rather than silently. |

---

## Metadata

**Confidence breakdown**
- Corrections C-1…C-7: **HIGH** — each rests on a quoted source line or a quoted command output from this session.
- Re-located source map: **HIGH** — every row re-read against the working tree at `4921388`.
- Control-register assertion map: **HIGH** — exhaustive `grep -n "set_control_register\|get_control_register" src/proms/eprom.cpp` plus a whole-file read; every `return` in both candidate functions enumerated by line.
- Shared mask placement: **HIGH** on the include graph and per-variant values; **MEDIUM** on the flash figures.
- Test env mechanics: **HIGH** — the two `platformio.ini` edits, the voltage seam, the recorder-layer capabilities and the `-f`-overrides-`test_filter` behaviour were each observed, not inferred.
- Gate and budget posture: **HIGH** — all three cold builds and all three test envs re-run this session; both golden `meta` blocks quoted verbatim.
- Validation architecture: **HIGH** on which claims are provable off-hardware and by which oracle; **MEDIUM** on the exact `loop_readback` seeding needed to force an X4 final-pass mismatch (the model supports it; the specific seed values are the plan's to derive).

**Research date:** 2026-08-11
**Valid until:** the next commit that touches `firestarter/src/proms/eprom.cpp`, `src/proms/memory.cpp`, `include/rurp_pinout.h`, `platformio.ini`, or `tests/golden/protocol_branch_inventory.json`. Every line citation in this document is anchored to `firestarter` @ `4921388`; re-locate before relying on any of them after that point. The measured figures (256 pytest, 141/17 native, 39 loop, 3-failed trace, 24424/24474/26400 flash) are anchored to the same commit.
