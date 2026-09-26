---
phase: 98-fix-correct-the-0x08-32-pin-write-vpp-path
reviewed: 2026-06-30T00:00:00Z
depth: standard
files_reviewed: 5
files_reviewed_list:
  - firestarter_app/tools/build_db.py
  - firestarter_app/tools/diff_db.py
  - firestarter_app/firestarter/data/pinouts.json
  - firestarter/src/proms/memory.cpp
  - firestarter/test/native/avr/test_val_eprom/test_val_eprom.cpp
findings:
  critical: 1
  warning: 5
  info: 3
  total: 9
status: issues_found
---

# Phase 98: Code Review Report

**Reviewed:** 2026-06-30T00:00:00Z
**Depth:** standard
**Files Reviewed:** 5
**Status:** issues_found

## Summary

Phase 98 implements the AM27C020 0x08 32-pin write/VPP-path fix (RC-1: pin 31
modeled as A18 instead of held PGM). The change spans a new size-keyed pinout
arm in `build_db.py` (`DIP32_27C020`), a cited diff-classification rule in
`diff_db.py` (`RC1_DIP32_27C020`), the `DIP32_27C020` pinout entry, a gated
deliberate PGM hold-LOW in `memory_set_data`, and three native tests.

The size-gate predicate (`proto_id==0x08 && mem_size<=262144`) is correct at
the boundary — the A18-bearing 512K/1M chips stay on `DIP32_STD`, and the
firmware gate independently re-checks `mem_size<=262144`, so the
hardware-damage A18 risk is well guarded. The tests are honest about being
code-structure assertions (HIGH-3) rather than silicon proofs.

The dominant concern is a **control-bit-aliasing correctness defect on Rev 2.x
hardware** (the operator's actual bench shields per memory): the firmware
PGM-hold clears logical `CTRL_ADDRESS_LINE_18 (0x20)`, but on Rev 2 that
logical bit and the active-during-programming `CTRL_VPP_P1_ENABLE (0x08)` are
OR-merged onto the **same physical output bit 0x08**, so the intended PGM=VIL
hold-LOW does not reach pin 31 on the very hardware the fix targets. This is
detailed as CR-01. The native tests cannot catch it because they record the
8-bit *logical* register and assert only on write *count*, not on the
post-hardware-remap physical level — so a green suite does not validate the fix
on Rev 2.

## Critical Issues

### CR-01: Rev-2 PGM hold-LOW is masked by the CTRL_ADDRESS_LINE_18 / CTRL_VPP_P1_ENABLE physical-bit alias

**File:** `firestarter/src/proms/memory.cpp:383-391`
**Issue:**
The gated fix reads the CONTROL register and clears `CTRL_ADDRESS_LINE_18`:

```c
rurp_register_t ctrl = rurp_read_from_register(CONTROL_REGISTER);
rurp_write_to_register(CONTROL_REGISTER, ctrl & ~CTRL_ADDRESS_LINE_18);
```

`memory_set_data` is called from `program_mismatched_bytes`
(`eprom.cpp:176`) *after* line 171 sets `CTRL_VPE_ENABLE`, which
`eprom_internal_set_control_register` flips to `CTRL_VPP_P1_ENABLE (0x08)`
because `using_p1_as_vpp(handle)` is true for the 32-pin / `VPP_P1_32_DIP`
config. So at the moment the fix runs, the logical CONTROL register has
`CTRL_VPP_P1_ENABLE (0x08)` HIGH and is being held HIGH across the entire
program window.

On the non-`HARDWARE_REVISION` (legacy) layout, `CTRL_ADDRESS_LINE_18` is
`0x20` and `CTRL_VPP_P1_ENABLE` is `0x08` — distinct bits — so clearing `0x20`
leaves the P1 routing intact and the cleared line really is pin 31. Fine.

On **Rev 2.x** (`HARDWARE_REVISION` defined — the operator's Rev 2.0/2.2 bench
shields), `rurp_map_ctrl_reg_for_hardware_revision`
(`include/rurp_hw_rev_utils.h:23-26`) OR-merges the logical `CTRL_ADDRESS_LINE_18`
onto the **same physical output bit** as P1:

```c
ctrl_reg = data & (... | CTRL_VPP_P1_ENABLE | ...);     // keeps logical 0x08
ctrl_reg |= data & CTRL_ADDRESS_LINE_18 ? CTRL_ADDRESS_LINE_18_REV2 : 0; // 0x08
```

with `CTRL_ADDRESS_LINE_18_REV2 == CTRL_VPP_P1_ENABLE_REV2 == 0x08`
(`include/rurp_pinout.h:127`). The physical pin-31 line therefore resolves to
`physical[0x08] = logical_P1 OR logical_A18`. Because logical P1 is held HIGH
throughout programming, clearing logical A18 changes nothing on the physical
pin — pin 31 stays at VIH, not the intended VIL. The fix that is supposed to
hold PGM LOW across the CE pulse is a **physical no-op on the exact hardware it
targets**.

This is exactly the bit-aliasing hazard the code's own comments are aware of
(`memory.cpp:367`, `RC1_DIP32_27C020` rationale, RC-98B test) — but those
treat the alias only as a reason to *gate out* 512K parts (D-04), and miss that
the same alias also *defeats the assert* for the in-scope ≤256K parts whenever
P1-as-VPP is active (which is always, during a 0x08 32-pin program pulse).

The comment block (`memory.cpp:370-375`, HIGH-1 caveat) pre-excuses a Phase-99
"0 bits at addr 0" result as "consistent with the analysis," which could cause
a genuine still-broken result to be dismissed.

**Fix:**
The PGM line must be driven via a control path that is *not* OR-aliased to P1
on Rev 2, or the hold-LOW must be applied at a point where P1 is not concurrently
asserting the same physical bit. Concretely, confirm against the Rev-2
schematic which physical control line actually reaches pin 31 / PGM, and assert
that distinct bit. If pin 31's PGM truly shares the P1 output node on Rev 2,
then a register clear cannot deliver VIL while VPP-on-P1 is active and the
approach needs rethinking (e.g. a dedicated PGM strobe line, or sequencing PGM
outside the P1-high window). At minimum, add a host/firmware assertion or a
native test that checks the **post-remap physical** value of the pin-31 bit
(call `rurp_map_ctrl_reg_for_hardware_revision` in the test for a Rev-2 stub)
rather than the logical 8-bit recording, so the masking is caught in CI instead
of on the bench. Until the physical path is verified, the fix should be treated
as unproven on Rev 2 and the Phase-99 "consistent with analysis" escape clause
removed.

## Warnings

### WR-01: Native tests record logical bits, so they cannot validate the Rev-2 fix

**File:** `firestarter/test/native/avr/test_val_eprom/test_val_eprom.cpp:772-824`
**Issue:**
RC-98A/B/C assert only on the *count* of CONTROL_REGISTER writes and on the
8-bit logical recording (`recorded_data`). They never exercise
`rurp_map_ctrl_reg_for_hardware_revision`, so the tests pass identically whether
or not the cleared bit survives the Rev-2 physical remap (CR-01). The suite is
green by construction for a fix that is physically inert on Rev 2 — the tests
prove "an extra CONTROL write happened," not "pin 31 went LOW." This is a
verify-can-fail gap: there is no RED state for the CR-01 defect.
**Fix:** Add a Rev-2 variant test that feeds the recorded CONTROL value through
`rurp_map_ctrl_reg_for_hardware_revision` (with a Rev-2 hardware stub) and
asserts the physical pin-31 bit is LOW at the program pulse while P1-VPP is
active — or document explicitly that no host test can cover this and that Phase
99 bench is the *only* gate, removing the implication that green tests de-risk
the fix.

### WR-02: RC-98A/RC-98B pre-fix baseline counts disagree between comment and assertion

**File:** `firestarter/test/native/avr/test_val_eprom/test_val_eprom.cpp:758, 837-866`
**Issue:**
RC-98A's prose computes a pre-fix baseline of "5 CONTROL writes" and asserts
`>= 6` (consistent). RC-98B's docstring header says "the execute-phase CONTROL
write count equals the pre-fix baseline (4 writes)" (line 835-836) but the
inline comment at line 860 says "must equal the pre-fix baseline (5)" and the
assertion is `TEST_ASSERT_LESS_OR_EQUAL(5, ...)` (line 866). The "4 writes"
figure in the docstring contradicts the body's "5" and the actual `<= 5`
assertion. A `<=` assertion is also weaker than the intended "equals baseline"
— it would pass at 0..5 writes, masking a regression that *reduces* writes.
**Fix:** Correct the RC-98B docstring to "5 writes," and tighten the assertion
to `TEST_ASSERT_EQUAL(5, ctrl_writes)` so the gate-exclusion test actually pins
the baseline rather than accepting anything `<= 5`.

### WR-03: RC1_DIP32_27C020 classifier shadows legitimate compound diffs on the same chip

**File:** `firestarter_app/tools/diff_db.py:443-452`
**Issue:**
The `RC1_DIP32_27C020` arm fires on `pinout_diff and not algo_diff and not
timing_diff and cu_chip.get("pinout") == "DIP32_27C020"`. It does **not**
exclude `voltage_diff`, `type_diff`, or `vpp_diff`. So a chip that simultaneously
flips to `DIP32_27C020` *and* has, say, a vcc/vdd or vpp change would be labeled
`RC1_DIP32_27C020`, whose allowed field-path set is only `{("pinout",)}`. The
secondary deltas land in `extra_paths`; if those paths are in `_all_rule_paths`
(vpp/vcc/vdd all are) they are silently surfaced as a "compound" note rather
than scrutinized as the primary cause. By contrast, the analogous `SRAM_PINOUT`
arm immediately below also lacks the voltage/type exclusions, but the older
single-bug arms (BUG2_TIMING, etc.) carefully exclude co-varying fields. The
phase claims "pinout-only change — no algorithm/VPP/electrical.type delta"
(line 206, 335) — that invariant is asserted in prose but not enforced by the
classifier guard.
**Fix:** Add `and not voltage_diff and not type_diff and not vpp_diff` to the
`RC1_DIP32_27C020` predicate (matching the documented "pinout-only" scope) so a
co-occurring voltage/type/vpp change on a `DIP32_27C020` chip is not absorbed
under a rule that does not explain it.

### WR-04: Firmware gate omits the `using_p1_as_vpp` precondition, risking a stray PGM write on non-P1 0x08 32-pin configs

**File:** `firestarter/src/proms/memory.cpp:383`
**Issue:**
The gate is `handle->protocol == 0x08 && handle->pins == 32 && handle->mem_size
<= 262144`. It does not check `using_p1_as_vpp(handle)` or that the chip is
actually on the `DIP32_27C020` pinout. The host only assigns `DIP32_27C020` to
0x08 ≤256K chips, but `memory_set_data` is reachable for any 0x08 32-pin ≤256K
write regardless of pinout/bus-config (e.g. a hand-crafted JSON command, or a
future host change). For a 0x08 32-pin ≤256K chip that legitimately keeps pin
31 on the address bus (any config where line 22 *is* an address bit), this
branch would clear `CTRL_ADDRESS_LINE_18` mid-write and corrupt the address.
The firmware gate is the documented "D-04 belt," but it is keyed on
size+protocol+pins only, not on the pinout decision that actually determines
whether pin 31 is off the bus.
**Fix:** Tighten the gate to also require the bus configuration that
`DIP32_27C020` implies — e.g. `&& using_p1_as_vpp(handle)` (already a proxy for
the 32-pin VPP_P1 layout) and/or verify pin 31's line is not present in
`bus_config.address_lines`. This keeps the belt aligned with the host's pinout
decision rather than a looser size/proto/pin triple.

### WR-05: `interpret_timing` swallows all exceptions and silently emits "0 us"

**File:** `firestarter_app/tools/build_db.py:401-412`
**Issue:**
Not new to this phase but in a reviewed file and adjacent to the 0x08 path the
phase touches: `interpret_timing` does `try: val = int(raw_hex, 16) except
Exception: val = 0`. A malformed or missing `pulse_delay` for a 0x07/0x08/0x0B
chip silently becomes "0 us", which downstream means "use firmware default" —
masking a genuine upstream-XML decode problem rather than failing the build.
For the 0x08 EPROM_QUICK chips this phase re-pinouts, a silently-zeroed pulse
would be indistinguishable from a real default and could hide a regression.
**Fix:** Narrow the except to `(TypeError, ValueError)` and emit a
`WARN: ... unparseable pulse_delay` to stderr (consistent with the rest of the
file's diagnostic style) so a decode failure is visible.

## Info

### IN-01: `uint32_to_bytes` has a stale-pos bug (pre-existing, in a reviewed file)

**File:** `firestarter/src/proms/memory.cpp:451-456`
**Issue:**
`uint32_to_bytes` writes `buffer[pos]` then `buffer[pos++]` three times: the
first two stores both target the same index (`buffer[pos]` then `buffer[pos++]`
evaluates the post-increment but the prior line already wrote `pos` without
advancing). The byte at the original `pos` is written twice (24-bit then 16-bit)
and the 8-bit shift `>>0` is dropped, so the serialization is wrong. This code
is only reachable under `#ifdef RAW_DATA_PROGRESS` (disabled), so it is latent,
not active — flagging for cleanup since the file is under review.
**Fix:** Use explicit indices: `buffer[pos]=...>>24; buffer[pos+1]=...>>16;
buffer[pos+2]=...>>8; buffer[pos+3]=...;` or `for` over the four shifts.

### IN-02: Magic boundary constant 262144 duplicated across three files without a shared symbol

**File:** `firestarter_app/tools/build_db.py:292`, `firestarter/src/proms/memory.cpp:383`, `firestarter_app/tools/diff_db.py` (implicit via DIP32_27C020)
**Issue:**
The ≤256K size gate (`262144`) is hand-written in both the host pinout arm and
the firmware branch. These must stay in lockstep (a divergence is a
hardware-damage A18 risk per the phase's own framing), but there is no shared
named constant or cross-reference test asserting they match.
**Fix:** Define a named constant in each repo (e.g. `MAX_27C020_SIZE = 262144`)
with a comment cross-referencing the firmware constant, and ideally a test that
asserts the host and firmware boundaries agree.

### IN-03: `min` macro re-defined with classic double-evaluation hazard

**File:** `firestarter/src/proms/memory.cpp:58-60`
**Issue:**
`#define min(a,b) ((a) < (b) ? (a) : (b))` evaluates its arguments twice. The
sole current use (`memory_read_execute:219`) passes side-effect-free operands,
so it is safe today, but the macro is a latent footgun if reused with an
expression like `min(f(), g())`. Pre-existing, in a reviewed file.
**Fix:** Prefer an inline function or a guarded macro that evaluates each
argument once; or rely on the C++ `std::min` where available.

---

_Reviewed: 2026-06-30T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
