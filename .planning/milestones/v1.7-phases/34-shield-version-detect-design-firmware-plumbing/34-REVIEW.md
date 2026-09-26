---
phase: 34-shield-version-detect-design-firmware-plumbing
reviewed: 2026-05-25T16:27:16Z
depth: standard
files_reviewed: 8
files_reviewed_list:
  - firestarter/include/rurp_shield.h
  - firestarter/include/rurp_pinout.h
  - firestarter/include/rurp_hw_rev_utils.h
  - firestarter_app/CLAUDE.md
  - firestarter_app/firestarter/constants.py
  - firestarter_app/firestarter/serial_comm.py
  - firestarter_app/tests/test_decoder.py
  - firestarter_app/tests/test_revision_constants_parity.py
findings:
  critical: 2
  warning: 5
  info: 4
  total: 11
status: issues_found
---

# Phase 34: Code Review Report

**Reviewed:** 2026-05-25T16:27:16Z
**Depth:** standard
**Files Reviewed:** 8
**Status:** issues_found

## Summary

Phase 34 lands the shield-version-detect substrate: firmware enum extension
(`REVISION_2_3` + `REVISION_UNKNOWN`), three ADC threshold `#define`s on A3, a
reworked 4-arm band-lookup in `rurp_detect_hardware_revision()`, a new
`case REVISION_2_3:` arm in the ctrl-reg dispatcher, plus the Python parity
block, sync-rule doc, hard pytest parity gate, and a module-scope
`_REVISION_SILKSCREEN` mapping consumed by the `MSG_OK_REV` formatter.

Overall the substrate is internally self-consistent and the parity gate is
strong. However the review surfaced two **BLOCKER**-class defects in the
firmware-side ADC path (internal pull-up active during `analogRead` and a
guard-gap band that I cannot reconcile with the R41/R(top) divider math from
the design docs), plus a Phase-34-incomplete silkscreen-mapping plumbing
gap: two other catalog messages (`MSG_INFO_HW`, `MSG_INFO_PHYSICAL_HW`) that
carry the same revision byte still render via the generic
`"HW: Rev%u"` format and will surface `REVISION_UNKNOWN` (0xFE) as the
nonsense string `"HW: Rev254"`. The narrative findings below are organized
by severity.

## Narrative Findings (AI reviewer)

## Critical Issues

### CR-01: `INPUT_PULLUP` active during `analogRead` on A3 detect divider corrupts band math (BLOCKER)

**File:** `firestarter/include/rurp_hw_rev_utils.h:61`
**Issue:**
```cpp
void rurp_detect_hardware_revision() {
    pinMode(PIN_HW_REVISION_DETECT_ADC, INPUT_PULLUP);   // <-- BUG
    pinMode(PIN_VPP_VOLTAGE_ADC,        INPUT_PULLUP);   // <-- pre-existing, but see CR-01b
    ...
    uint16_t adc_a3 = analog_read_avg8(PIN_HW_REVISION_DETECT_ADC);
```
On AVR ATmega328P/ATmega32U4 the `INPUT_PULLUP` mode enables the internal
~20–50 kΩ pull-up resistor between the pin and AVcc. While the chip
hardware still allows the ADC to sample that pin, the internal pull-up is
in parallel with whatever external network is driving the pin. For the
R41-on-A3 detect divider the math the phase docs assume (`adc_a3` ≈
ratio of R41/(R41+R_top) × 1024) is silently corrupted:

- **No R41 (Rev 0 / Rev 1 boards)** — pin is otherwise floating; internal
  pull-up drags the reading toward 1023 (≥ `ADC_BAND_R41_10K_HIGH=600`).
  Accidentally still correct ("high band → Rev 0/1 disambig"), but only
  because the pull-up is the load-bearing element. Not what the design
  doc claims.
- **R41 = 4k7 (Rev 2.0/2.1/2.2)** — internal ~30 kΩ in parallel with R41
  to AVcc (i.e. parallel with itself, since R41 is also tied to AVcc as
  the divider's top leg per RESEARCH §ADC band math) raises the effective
  top-leg conductance ~15 %. The 4k7 bucket's true ADC band shifts up.
- **R41 = 10k (Rev 2.3)** — same direction, larger effect (~30 % of the
  top-leg conductance is now the internal pull-up). The intended 10k
  bucket band (`[220, 600)`) is no longer centered on the design value.

The `analog_read_avg8` 8-sample averaging is good practice against AVcc
switching noise but it cannot recover the systematic offset introduced by
the internal pull-up.

Compounding factor: the SAME bug existed pre-Phase-34 when this function
used `digitalRead` — for digital input the pull-up was *required* to
establish a definite high level on floating Rev-0/1 boards, so the
`INPUT_PULLUP` line was correct under the old digital-read regime. The
rework in Phase 34 switched the read mode to `analogRead` but did NOT
update the pin mode — the leftover `INPUT_PULLUP` line is now actively
hostile to the new band-lookup math.

**Fix:**
```cpp
void rurp_detect_hardware_revision() {
    pinMode(PIN_HW_REVISION_DETECT_ADC, INPUT);  // high-Z; let R41 + R_top divider drive the pin
    pinMode(PIN_VPP_VOLTAGE_ADC,        INPUT);  // CR-01b — symmetric fix for the A2 disambig read
    ...
}
```
And **re-derive** `ADC_BAND_R41_4K7_HIGH`, `ADC_BAND_R41_10K_LOW`,
`ADC_BAND_R41_10K_HIGH` from the pure R41/R_top divider before bench-
validating on real boards. The current threshold values (200/220/600)
were picked assuming the divider drives a high-Z input; with `INPUT_PULLUP`
they describe a different circuit and the per-rev classification on
real silicon is non-deterministic against the docs.

For the high-band Rev 0/1 disambig leg (line 80 `analogRead(PIN_VPP_VOLTAGE_ADC)
< 1000`) the operator can choose either: (a) leave the A2 pin as `INPUT`
and accept the empirical < 1000 threshold the prior bench characterization
yielded with `INPUT_PULLUP`, OR (b) set both pins to `INPUT_PULLUP` ONLY
for the A2 read by toggling `pinMode` between the two reads. Either way
the **A3 read must be `INPUT` (high-Z)** for the new band-lookup math to
hold.

### CR-02: Guard-gap band `[200, 220)` is impossibly narrow for an 8-sample-averaged AVR ADC (BLOCKER)

**File:** `firestarter/include/rurp_pinout.h:58-62`
**File:** `firestarter/include/rurp_hw_rev_utils.h:68-87`
**Issue:** The thresholds enforce:
```
adc_a3 < 200                          → REVISION_2_0 (R41=4k7 bucket)
adc_a3 ∈ [200, 220)                   → REVISION_UNKNOWN (guard gap, 20 counts wide)
adc_a3 ∈ [220, 600)                   → REVISION_2_3 (R41=10k bucket)
adc_a3 ≥ 600                          → REVISION_0 / REVISION_1 (no R41 + A2 disambig)
```
With 8-sample averaging the noise floor on an AVR 10-bit ADC against a
switching-AVcc reference is empirically ~±5–10 counts, but the 4k7-bucket
ceiling (200) and the 10k-bucket floor (220) sit only 20 counts apart.
That is barely 2× the expected noise band — under cold-boot conditions,
edge-of-tolerance R41 stock parts (5 % tolerance), and the AVcc-noise
profile the RESEARCH §ADC Voltage Band Math doc explicitly calls out, the
real-board read for a 4k7 board can pop above 200 (or a 10k board can pop
below 220) and silently classify as `REVISION_UNKNOWN`.

The fallout: `REVISION_UNKNOWN` is consumed by
`rurp_map_ctrl_reg_for_hardware_revision()` as the `default:` arm with
`ctrl_reg = 0` (line 32-37). That zeros out **every** control-register
bit — `CTRL_VPP_REGULATOR_ENABLE`, `CTRL_VPE_ENABLE`, `CTRL_VPP_P1_ENABLE`,
and all address-line routes — and **every** EPROM/Flash write through
`dev_tools.cpp:100` + `:145` becomes a no-op-with-VPP-off. The chip
appears unresponsive; the operator has no idea why because no error is
emitted — `rurp_get_hardware_revision()` happily returns 0xFE and the
LOG_INFO_ID_U8(MSG_INFO_HW, ...) emit on every boot (firestarter.cpp:134)
just shows `"HW: Rev254"` (see WR-02 below).

This interacts catastrophically with CR-01 (the `INPUT_PULLUP` bug shifts
the per-rev bands by 15-30 %; a 4k7 board could easily land at adc_a3 ≈
210 with both bugs compounding).

**Fix:** Two-part:
1. **Widen the guard gap** — pick band thresholds with at least 40–50 counts
   between adjacent buckets after empirical 8-sample-averaged characterization
   of real Rev 2.0 + Rev 2.3 boards under the production AVcc-switching
   load. The 20-count gap is the upper-bound theoretical noise margin; the
   real-board safety margin needs to be 2-3× the noise band.
2. **Hard-fail loudly when REVISION_UNKNOWN is the effective revision** —
   the dispatcher's `default: break; → ctrl_reg = 0` silent-failure mode is
   wrong. At minimum `dev_tools.cpp` callers of
   `rurp_map_ctrl_reg_for_hardware_revision()` should check
   `rurp_get_hardware_revision() == REVISION_UNKNOWN` and emit
   `LOG_ERROR_ID(MSG_ERR_*)` instead of writing 0 to the control register.
   Better: have the firmware refuse to dispatch any EPROM operation while
   the effective revision is `REVISION_UNKNOWN`, prompting the operator to
   set the EEPROM override.

Both fixes are needed; widening the band alone leaves the silent-zero-ctrl-
reg failure mode in place for legitimate edge cases (truly broken R41).
Fixing the silent-failure alone leaves Phase 34 calibration brittle for
in-spec boards.

## Warnings

### WR-01: `MSG_INFO_HW` + `MSG_INFO_PHYSICAL_HW` bypass `_REVISION_SILKSCREEN` and will render `REVISION_UNKNOWN` as `"HW: Rev254"`

**File:** `firestarter_app/firestarter/serial_comm.py:171-179` (silkscreen dict)
**File:** `firestarter_app/firestarter/messages.py:145-146` (catalog entries — out of phase scope but load-bearing)
**File:** `firestarter/src/firestarter.cpp:133-134` (the two emit sites)
**Issue:** Phase 34 added `_REVISION_SILKSCREEN` to map revision bytes to
silkscreen strings, and threaded it into `_format_message()` only for the
`MSG_OK_REV` (P-02) path (serial_comm.py:351-357). But the firmware ALSO
emits the same revision byte through two other catalog entries every boot:
```python
0x5B: MessageDef(id=0x5B, name="MSG_INFO_HW",          format="HW: Rev%u",          params=(("u8", "dec"),) ...)
0x5C: MessageDef(id=0x5C, name="MSG_INFO_PHYSICAL_HW", format="Physical HW: Rev%u", params=(("u8", "dec"),) ...)
```
emitted from `firestarter.cpp:133-134`:
```cpp
LOG_INFO_ID_U8(MSG_INFO_PHYSICAL_HW, (uint8_t)rurp_get_physical_hardware_revision());
LOG_INFO_ID_U8(MSG_INFO_HW,          (uint8_t)rurp_get_hardware_revision());
```
These ID frames bypass `_format_message()`'s `MSG_OK_REV`-specific branch
and fall through to the generic catalog format-string path
(`serial_comm.py:482-497`). Result: on any Phase-34 firmware running on a
guard-gap board, the host log will show `"INFO: HW: Rev254"` /
`"INFO: Physical HW: Rev254"` instead of `"HW: rev_unknown"` — directly
contradicting the Phase 34 D-09 decision that "host displays silkscreen
strings; the wire still carries the raw revision byte".

Even for normal-operation reads the inconsistency is visible: an operator
on a Rev 2.3 board will see:
- `OK: Rev 2.3` (P-02 path, silkscreen-aware)
- `INFO: HW: Rev5` (catalog format-string path, raw byte)
- `INFO: Physical HW: Rev5` (same)

side-by-side in the boot log. The two surfaces disagree on what the same
byte means.

**Fix:** Extend `_format_message()` to handle MSG_INFO_HW + MSG_INFO_PHYSICAL_HW:
```python
from firestarter.messages import MSG_INFO_HW, MSG_INFO_PHYSICAL_HW
...
if msg_id == MSG_INFO_HW and len(params) == 1:
    return f"HW: {_REVISION_SILKSCREEN.get(params[0], f'Rev{params[0]}')}"
if msg_id == MSG_INFO_PHYSICAL_HW and len(params) == 1:
    return f"Physical HW: {_REVISION_SILKSCREEN.get(params[0], f'Rev{params[0]}')}"
```
And add corresponding test coverage analogous to
`test_ok_rev_p02_with_override_decodes` / `test_ok_rev_p02_no_override_decodes`.

### WR-02: `MSG_OK_CFG` Override clause still renders `Rev{int}` instead of silkscreen string

**File:** `firestarter_app/firestarter/serial_comm.py:359-363`
**Issue:** The P-02 (`MSG_OK_REV`) renderer was updated to use
`_REVISION_SILKSCREEN.get(...)` for both physical AND effective bytes
(lines 351-357). The P-03 (`MSG_OK_CFG`) renderer was NOT updated:
```python
if msg_id == MSG_OK_CFG and len(params) == 3:
    r1, r2, override = params[0], params[1], params[2]
    if override == 0xFF:
        return f"R1: {r1}, R2: {r2}"
    return f"R1: {r1}, R2: {r2}, Override HW: Rev{override}"   # <-- raw byte, no silkscreen
```
For a Rev 2.3 EEPROM override the host will display
`"R1: 270000, R2: 44000, Override HW: Rev5"`, but the matching MSG_OK_REV
ack on the same board renders `"Rev 2.3"`. The same revision byte should
not have two different display formats on adjacent ack lines.

The existing test `test_ok_cfg_p03_with_override_decodes` (test_decoder.py:400-412)
asserts the OLD format `"R1: 10000, R2: 4700, Override HW: Rev2"` — this
test should be updated to enforce the silkscreen-string format alongside
the renderer change.

**Fix:**
```python
if msg_id == MSG_OK_CFG and len(params) == 3:
    r1, r2, override = params[0], params[1], params[2]
    if override == 0xFF:
        return f"R1: {r1}, R2: {r2}"
    override_str = _REVISION_SILKSCREEN.get(override, f"Rev{override}")
    return f"R1: {r1}, R2: {r2}, Override HW: {override_str}"
```
Plus update `test_ok_cfg_p03_with_override_decodes` to assert
`"Override HW: Rev 2.0-class"` (or whichever rev byte the test uses).

### WR-03: `_REVISION_SILKSCREEN` is not validated against `CATALOG`/firmware enum at import time

**File:** `firestarter_app/firestarter/serial_comm.py:171-179`
**File:** `firestarter_app/tests/test_revision_constants_parity.py`
**Issue:** The parity test
(`test_revision_byte_values_match_firmware_enum`) enforces that the
`REVISION_*` byte constants in `constants.py` match the firmware enum.
But it does NOT enforce that `_REVISION_SILKSCREEN`'s **key set** is the
complete set of `REVISION_*` constants. If a future revision lands —
say a `REVISION_2_4` is added to `constants.py` and the firmware enum —
the parity test continues to pass (it only asserts the values present)
but `_REVISION_SILKSCREEN.get(REVISION_2_4, f"Rev{REVISION_2_4}")` falls
through to the `f"Rev{byte}"` fallback, silently shipping a raw-byte
string for the new rev.

**Fix:** Add an assertion to the parity test:
```python
def test_silkscreen_dict_covers_all_revisions():
    from firestarter.serial_comm import _REVISION_SILKSCREEN
    from firestarter.constants import (
        REVISION_0, REVISION_1, REVISION_2_0, REVISION_2_1,
        REVISION_2_2, REVISION_2_3, REVISION_UNKNOWN,
    )
    expected = {
        REVISION_0, REVISION_1, REVISION_2_0, REVISION_2_1,
        REVISION_2_2, REVISION_2_3, REVISION_UNKNOWN,
    }
    assert set(_REVISION_SILKSCREEN.keys()) == expected, (
        "_REVISION_SILKSCREEN must map every REVISION_* constant exactly"
    )
```

### WR-04: `rurp_get_physical_hardware_revision()` returns 0xFF when called before `rurp_detect_hardware_revision()`

**File:** `firestarter/include/rurp_hw_rev_utils.h:12, 42-44`
**Issue:** The file-scope `uint8_t revision = 0xFF;` initializer is
intentionally retained (per commit 032a2e2 — "leave alone for
byte-stability"). However:
- 0xFF is now the **reserved EEPROM-override-absent sentinel** per the
  Phase 34 D-07 carve-out documented in serial_comm.py:171-179 and
  constants.py:90.
- Any call to `rurp_get_physical_hardware_revision()` between MCU boot
  and `rurp_detect_hardware_revision()` will return 0xFF.

In normal boot flow `setup()` (firestarter.cpp:39) calls
`rurp_detect_hardware_revision()` immediately, so the file-scope
initializer's lifetime is microseconds. But:
1. Any future code path that queries the physical revision before
   `setup()` runs (a constructor of a global C++ object instantiated
   before `main()`, or a hook in `rurp_load_config()` itself) gets 0xFF.
2. The semantics now silently collide: `rurp_get_hardware_revision()`
   (line 91-97) checks `rurp_config->hardware_revision < 0xFF` to decide
   whether to use the EEPROM override or the physical detect — if the
   detect hasn't run yet, BOTH legs return 0xFF and the dispatcher's
   `default:` arm zeros the control register without any indication
   that detect simply hasn't completed yet.

The commit message acknowledges this ("dead-code in normal boot flow")
but does not enforce it.

**Fix:** Initialize `revision = REVISION_UNKNOWN` (0xFE) so the value-set
of `revision` is disjoint from the EEPROM-override-absent sentinel:
```cpp
uint8_t revision = REVISION_UNKNOWN;   // 0xFE, not 0xFF — preserve sentinel disjointness
```
This is a 0-byte .hex-stable change (both values are 8-bit immediates).
The phase-34 D-07 carve-out is explicitly documented to expect 0xFE for
"detect inconclusive"; the 0xFF initializer was a pre-Phase-34
incidental that now violates the new invariant. The "byte-stability"
rationale in the commit message conflates the file-scope initializer
(which the compiler folds into `.bss` init data) with the function-body
assignment (which is now `REVISION_UNKNOWN`); changing the initializer
shifts a single immediate operand byte in the `.hex`, not the layout.

### WR-05: `rurp_hw_rev_utils.h` defines non-inline functions and a global variable in a header — fragile single-TU contract

**File:** `firestarter/include/rurp_hw_rev_utils.h:12, 14, 42, 60, 91`
**Issue:** This header — which is **included transitively via
`rurp_register_utils.h`** by the per-board TUs `uno_rurp_shield.cpp` and
`leonardo_rurp_shield.cpp` — provides full **non-inline function bodies**
for:
- `rurp_map_ctrl_reg_for_hardware_revision()` (line 14)
- `rurp_get_physical_hardware_revision()` (line 42)
- `rurp_detect_hardware_revision()` (line 60)
- `rurp_get_hardware_revision()` (line 91)

…and a **file-scope global variable** `uint8_t revision = 0xFF;` (line 12).

If `rurp_register_utils.h` is ever included into a second active TU per
build (either by a future firmware change or by the existing native-test
infrastructure that compiles a subset of the same TUs), the linker will
emit multiple-definition errors for each of the four functions and the
`revision` global. The pattern only compiles today because PlatformIO
selects a single board file per `-e <env>` invocation.

This is **pre-existing** (Phase 33 + Phase 34 both touched this file
without addressing the issue), but Phase 34 actively grew the surface
(`analog_read_avg8` was added as `static inline` correctly, but the
4 existing function bodies remain non-inline). The risk grows every time
a function is touched.

**Fix:** Either:
1. **Move the function bodies to a new `.cpp`** (e.g.
   `src/rurp_hw_rev_utils.cpp`) and keep the header declarations-only.
   Lowest-risk, most idiomatic.
2. **Mark each function `static inline`** as a stopgap. Works for the
   functions but does NOT fix the `revision` global.
3. **Document the single-TU invariant** with a `#error` guard if the
   header is included more than once at link time (harder to express
   cleanly in C++ without a token-paste trick on `__COUNTER__` or build
   metadata).

Option 1 is the right answer. Option 2 leaves the global problem open.

## Info

### IN-01: `analog_read_avg8` AVR overflow safety is unbearable on the edge

**File:** `firestarter/include/rurp_hw_rev_utils.h:52-58`
**Issue:**
```cpp
static uint16_t analog_read_avg8(uint8_t pin) {
    uint16_t sum = 0;
    for (uint8_t i = 0; i < 8; i++) {
        sum += (uint16_t)analogRead(pin);
    }
    return (uint16_t)(sum >> 3);  // average over 8 samples
}
```
8 × 1023 = 8184 which fits comfortably in `uint16_t` (max 65535). Math is
correct. However, the implicit cast `(uint16_t)analogRead(pin)` discards
nothing meaningful (`analogRead` returns `int`, always 0..1023) and the
divide-by-8 via shift is fine. **No bug**, but the explicit `uint16_t`
cast on a value that is already guaranteed `≤ 1023` is dead noise; readers
will momentarily wonder if there's a portability concern. Consider
dropping the cast or adding a brief comment explaining "AVR analogRead is
0..1023".

**Fix:** (style only)
```cpp
sum += (uint16_t)analogRead(pin);  // analogRead returns 0..1023 on AVR ADC
```

### IN-02: `pinMode(PIN_VPP_VOLTAGE_ADC, INPUT)` restore on line 88 leaks `INPUT_PULLUP` for A3

**File:** `firestarter/include/rurp_hw_rev_utils.h:88`
**Issue:** The detect function ends with:
```cpp
pinMode(PIN_VPP_VOLTAGE_ADC, INPUT);     // restore A2 to high-Z
```
but does NOT restore `PIN_HW_REVISION_DETECT_ADC` (A3) to `INPUT`. After
detect runs once at boot, A3 stays in `INPUT_PULLUP` mode for the rest of
the firmware lifetime. This is asymmetric and surprising. If any other
code path ever re-reads A3 (currently none in the firmware tree per
grep) it gets the pulled-up reading.

This is closely related to CR-01 (the `INPUT_PULLUP` mode itself is
wrong); fixing CR-01 by setting A3 to `INPUT` from the start makes this
finding moot. Calling it out separately because the asymmetry is a
documentation/intent ambiguity even if CR-01 is rejected.

**Fix:** Restore A3 to `INPUT` symmetrically:
```cpp
pinMode(PIN_HW_REVISION_DETECT_ADC, INPUT);
pinMode(PIN_VPP_VOLTAGE_ADC,        INPUT);
```

### IN-03: Test naming mismatch — `_REVISION_SILKSCREEN` test descriptions reference "Path A" but the test asserts the Path B output

**File:** `firestarter_app/tests/test_decoder.py:366-394`
**Issue:** Two new tests' docstrings reference "Phase 34 D-05 Path A
silkscreen-string mapping":
- `test_ok_rev_p02_with_override_decodes` (line 366)
- `test_ok_rev_p02_no_override_decodes` (line 381)

Without the Phase 34 D-05 doc handy a maintainer cannot tell whether
"Path A" was the chosen path or the rejected alternative. The assertions
themselves are clear (`"Rev 2.0-class, Override HW: Rev 1"` and `"Rev 1"`)
but the docstring's "Path A" tag is meaningless out of doc context.

**Fix:** Either:
1. Inline the chosen-path summary in the docstring:
   `"...renders '...' per Phase 34 D-05 (host-side silkscreen mapping)..."`,
   dropping the "Path A" reference.
2. Or add a short comment near the test class explaining what "Path A"
   meant in the D-05 decision.

Minor; documentation hygiene only.

### IN-04: CLAUDE.md sync rule is informational; lacks an executable enforcement pointer for CTRL_* parity

**File:** `firestarter_app/CLAUDE.md:99-100`
**Issue:** The new line documents the `RURP_HARDWARE_REVISIONS` sync rule
and points at the hard pytest parity gate
(`test_revision_constants_parity.py`). It does NOT do the same for the
`RURP_CONTROL_REGISTER_BITS` (CTRL_*) parity block already mentioned in
the same sentence ("Additionally, the `RURP_CONTROL_REGISTER_BITS` block
in `constants.py` (CTRL_* names) mirrors the control-register-bit
declarations in `firestarter/include/rurp_pinout.h`"). The CTRL_*
parity is documented but there is no executable test enforcing it. A
parallel `test_ctrl_bits_parity.py` would close the gap symmetrically.

**Fix:** Add a parallel pytest that hard-asserts CTRL_* byte values from
`constants.py` match `rurp_pinout.h`. Out of scope for Phase 34 strictly
(the new sync-rule line is the deliverable; the CTRL_* parity gate is a
v1.7 follow-up), but should be tracked as a known gap.

---

_Reviewed: 2026-05-25T16:27:16Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
