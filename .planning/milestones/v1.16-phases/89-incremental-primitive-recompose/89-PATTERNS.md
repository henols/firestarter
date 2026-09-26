# Phase 89: Incremental Primitive Recompose - Pattern Map

**Mapped:** 2026-06-26
**Files analyzed:** 8 (1 new module = 2 files; 6 in-place handler edits)
**Analogs found:** 8 / 8 (every primitive has an in-repo verbatim precedent)

> This is a firmware C++ **refactor-under-test**, not a feature. The ONLY genuinely-new
> files are `firestarter/src/proms/primitives.cpp` + `firestarter/include/primitives.h`
> (D-03). Everything else is an in-place edit that MUST replicate the existing handler's
> conventions byte-for-byte (zero-diff golden trace is the goal, D-04). For every new
> primitive there is an *already-byte-identical* precedent in the tree — the work is
> extraction, never invention.

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `include/primitives.h` **(NEW)** | header / module-decl | n/a | `include/eprom.h` (guard+`extern "C"` style) + `include/flash_utils.h` (cross-handler helper precedent) | exact (convention) |
| `src/proms/primitives.cpp` **(NEW)** | utility (cross-family primitives) | transform / readback | `src/proms/flash_utils.cpp` (the proven cross-handler helper TU) | exact (structural) |
| `include/flash_utils.h` (P7 edit) | config / const-data | n/a | self — delete dead `FLASH_ENABLE_WRITE_PROTECTION` (== `FLASH_ENABLE_WRITE`) | exact |
| `src/proms/eeprom_28c.cpp` (P7+P4+P5 edit) | handler (0x0D EEPROM) | CRUD / poll-readback | self + `flash_utils.cpp` (already `#include`d) | exact |
| `src/proms/eprom.cpp` (P3+P4+P5 edit) | handler (0x07/08/0B EPROM) | CRUD / VPP-gate / verify-readback | `flash_intel.cpp` (shares VPP body + chip-id tail verbatim) | exact (body) |
| `src/proms/flash_intel.cpp` (P3+P4 edit) | handler (0x10 Intel flash) | CRUD / VPP-gate | `eprom.cpp` (shares VPP window body verbatim) | exact (body) |
| `src/proms/flash_type_4.cpp` (P5 edit; P4 already done) | handler (0x05 page-write flash) | CRUD / poll-readback | `eeprom_28c.cpp` (same single-addr poll shape) | exact (body) |
| `src/proms/flash_type_3.cpp` (P7 edit only) | handler (0x06 AMD flash) | CRUD | self (uses `FLASH_ENABLE_WRITE`; no P4 chip-id site per Phase 88 D-03) | n/a (P7-touch only) |

---

## New-Module Patterns (D-03 — `primitives.{cpp,h}`)

### Header structure — copy `include/eprom.h` guard/`extern "C"` skeleton, NOT `flash_utils.h`'s in-header definitions

**Analog (guard + extern "C" + declarations-only):** `include/eprom.h:8-21`
```cpp
#ifndef __EPROM_H__
#define __EPROM_H__

#include "firestarter.h"
#ifdef __cplusplus
extern "C" {
#endif

    void configure_eprom(firestarter_handle_t* handle);

#ifdef __cplusplus
}
#endif
#endif // __EPROM_H__
```

**CRITICAL distinction (verified `include/flash_utils.h:24-60`):** `flash_utils.h` *defines*
its `const byte_flip_t` tables **in the header** (each including TU gets an internal-linkage
copy — that ODR quirk is exactly what produces P7's flash savings when a dead copy is deleted).
`primitives.h` must do the OPPOSITE: declare **functions only** (external linkage), define the
function bodies in `primitives.cpp`. Do NOT define functions in the header.

The proven function-declaration convention to copy is `flash_utils.h:62-69`:
```cpp
    void flash_util_byte_flipping(firestarter_handle_t* handle, const byte_flip_t* byte_flips, size_t size);
    void flash_util_verify_operation(firestarter_handle_t* handle, uint8_t expected_data);
    uint16_t flash_util_get_chip_id(firestarter_handle_t* handle);
    void flash_util_check_chip_id_execute(firestarter_handle_t* handle);
```
All take `firestarter_handle_t* handle` as the first/only state arg, return `void` (status via
`handle->response_code`) or a scalar. Match this exactly for `chip_id_report` / `vpp_check_window`
/ `poll_readback`.

### Build pickup — NO platformio.ini change required (RESEARCH Pattern 1, CONFIRMED)

**Source:** `firestarter/platformio.ini`
- `[env:native]` line 129: `build_src_filter = +<proms/>` — globs the whole `proms/` dir, so
  dropping `primitives.cpp` there is auto-compiled into the native test binary.
- `[env:leonardo]` (line 57) / uno use the default `src/` recursive filter — also auto-picked-up.
- `test_build_src = yes` (line 130) — handlers + the new TU are part of the test build.

No new `-I` line is needed (`-I include` is already present, line 98). No `test_filter` change.
The existing `flash_utils.cpp` is the living proof: it sits in `proms/`, is `#include`d by
`eeprom_28c.cpp`/flash3/flash4, and links cleanly into both AVR and native with zero ini edits.

### Module-comment convention — copy `flash_utils.cpp:8-28` banner style

`flash_utils.cpp` opens with a block comment naming (a) which handlers/protocols call it, (b)
what primitives it holds, (c) the safety boundary (`No VPP regulator control lives here`), (d)
datasheet + `doc/PROTOCOLS.md` cross-refs. `primitives.cpp` should carry the analogous banner
(callers = eprom + eeprom28c + flash_intel + flash4; primitives = chip_id_report / vpp_check_window
/ poll_readback; the D-06 note that keying is on `handle->protocol`).

---

## Pattern Assignments

### P4 — `chip_id_report` primitive (PRIM-03)

**THE precedent already exists and is byte-identical across all 4 sites.** The generalization
target is literally `flash_util_check_chip_id_execute`.

**Primary analog (the report tail, lift verbatim):** `flash_utils.cpp:110-126`
```cpp
void flash_util_check_chip_id_execute(firestarter_handle_t* handle) {
    uint16_t chip_id = flash_util_get_chip_id(handle);       // <-- protocol-specific READ (stays handler-local)
    if (chip_id != handle->chip_id) {                        // <-- shared REPORT TAIL begins here
        uint8_t _b[4];
        _b[0] = (uint8_t)((chip_id >> 8) & 0xFF);
        _b[1] = (uint8_t)(chip_id & 0xFF);
        _b[2] = (uint8_t)((handle->chip_id >> 8) & 0xFF);
        _b[3] = (uint8_t)(handle->chip_id & 0xFF);
        if (is_flag_set(FLAG_FORCE)) {
            LOG_WARN_ID_BYTES(MSG_WARN_CHIP_ID_MISMATCH, _b, 4);
            handle->response_code = RESPONSE_CODE_WARNING;
        } else {
            LOG_ERROR_ID_BYTES(MSG_ERR_CHIP_ID_MISMATCH, _b, 4);
            handle->response_code = RESPONSE_CODE_ERROR;
        }
    }
}
```

**Suggested signature (planner discretion, D-03):** `void chip_id_report(firestarter_handle_t* handle, uint16_t read_id);`
— the caller performs the protocol-specific read, then passes the read id in.

**Four call sites (the report tail is byte-identical in all four — verified):**

| Site | File:lines | Protocol-specific READ that STAYS handler-local |
|------|-----------|--------------------------------------------------|
| eprom | report tail `eprom.cpp:356-369`; read `eprom_get_chip_id` `eprom.cpp:249-260` | A9-12V: `CTRL_VPP_REGULATOR_ENABLE`+`delay(50)` then `CTRL_VPP_A9_ENABLE`+`delay(100)`, read 0x0000/0x0001, clear |
| eeprom28c | report tail `eeprom_28c.cpp:100-115`; read `eeprom_28c.cpp:92-99` | A9-12V like eprom, but `mfr_addr = mem_size-64` (NOT 0x0000); **preserve the `mem_size < 64` underflow guard `eeprom_28c.cpp:82-91`** |
| flash_intel | report tail `flash_intel.cpp:218-231`; read `flash_intel.cpp:214-217` | command-register: `set_data(0,0x90)` autoselect → read → `set_data(0,0xFF)` exit |
| flash4 | already delegates: `flash_type_4.cpp:143-145` → `flash_util_check_chip_id_execute`; read `flash_utils.cpp:103-105` | AMD unlock: `FLASH_ENABLE_ID`/`FLASH_DISABLE_ID` sequence |

**The `error_code` param wrinkle (verified — Assumption A3, do NOT collapse without trace check):**
`eprom_internal_check_chip_id` (`eprom.cpp:353-370`) takes an explicit `uint8_t error_code` and
keys `if (error_code == RESPONSE_CODE_WARNING)` instead of `is_flag_set(FLAG_FORCE)`. Its caller
`eprom_generic_init` (`eprom.cpp:343-351`) passes `is_flag_set(FLAG_FORCE) ? WARNING : ERROR` —
which equals what the shared `FLAG_FORCE` tail computes, so it *looks* redundant. BUT another
caller may pass `ERROR` unconditionally. **Preserve the param (or verify the golden trace) before
collapsing eprom's keying onto `FLAG_FORCE`.** flash3 has NO chip-id site (Phase 88 D-03).

**Match quality:** exact — the tail is proven byte-identical in `flash_utils.cpp` (Phase 74).

---

### P3 — `vpp_check_window` primitive (PRIM-04) — HIGHEST DEFERRAL RISK (D-02)

**The window-compare body is shared VERBATIM between exactly two sites; three axes DIVERGE and
MUST stay handler-local.** Key on `handle->protocol`, never `electrical.type` (D-06).

**Primary analog (the shared middle — read+window+`_b[8]`+FORCE):** `eprom.cpp:280-323`
```cpp
    delay(100);
    uint16_t vpp_mv = rurp_read_voltage_mv();
    LOG_DEBUG_ID_SUB_U16(DBG_CHECKING_VPP_VOLTAGE, vpp_mv);
    if (vpp_mv > (uint32_t)handle->vpp_mv + 500) {          // HIGH: over-voltage guard (D-08)
        // pack _v0.._v3 into _b[8], then:
        if (is_flag_set(FLAG_FORCE)) {
            LOG_WARN_ID_BYTES(MSG_WARN_VPP_HIGH, _b, 8);
            handle->response_code = RESPONSE_CODE_WARNING;
        } else {
            LOG_ERROR_ID_BYTES(MSG_ERR_VPP_HIGH, _b, 8);
            handle->response_code = RESPONSE_CODE_ERROR;
        }
    } else if (vpp_mv < (uint32_t)handle->vpp_mv * 95 / 100) {  // LOW: always WARNING
        // identical _b[8] pack, then:
        LOG_WARN_ID_BYTES(MSG_WARN_VPP_LOW, _b, 8);
        handle->response_code = RESPONSE_CODE_WARNING;
    }
```
**Identical body confirmed at** `flash_intel.cpp:63-106` (same thresholds, same `_b[8]` byte
packing, same `MSG_WARN_VPP_HIGH/LOW` + `MSG_ERR_VPP_HIGH`, same FORCE-downgrade). The over-voltage
HIGH check (`> vpp_mv + 500`) is the SAFE-04/D-08 invariant — extract the compare but the threshold
and FORCE/ERROR semantics MUST stay byte-identical (golden trace + the INV-01/INV-03 bit guards).

**The three handler-local divergences (do NOT move into the shared primitive):**

| Axis | `eprom_check_vpp` (`eprom.cpp:262-325`) | `flash_intel_check_vpp` (`flash_intel.cpp:52-108`) |
|------|------------------------------------------|------------------------------------------------------|
| REV0 guard (`eprom.cpp:264-270` / `flash_intel.cpp:54-60`) | identical early-return WARNING — *can* move only if trace stays zero-diff; keep local first cut (Open Q2) | identical |
| Regulator enable | toggles itself: `0x0B\|\|FLAG_VPE_AS_VPP → REGULATOR` else `REGULATOR\|VPE_DROP`, then `delay(100)` (`eprom.cpp:271-279`) | does NOT toggle — caller `flash_intel_write_init:133` set `REGULATOR\|P1`+`delay(500)` already |
| Trailing clear | `set_control_register(REGULATOR\|VPE_DROP, 0)` (`eprom.cpp:324`) | NONE — caller holds VPP through the write (`flash_intel.cpp:107` comment) |

**The protocol-keying idiom to replicate (D-06):** `eprom.cpp:271` and `eprom.cpp:198`
```cpp
if (handle->protocol == 0x0B || is_flag_set(FLAG_VPE_AS_VPP)) {   // EPROM_LEGACY direct-VPE
    handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE, 1);
} else {                                                          // EPROM_STD/QUICK drop-resistor
    handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE, 1);
}
```
This keying stays inside each handler's retained routing — NEVER inside the shared `vpp_check_window`.

**Suggested signature:** `void vpp_check_window(firestarter_handle_t* handle);` — owns ONLY the
read+window+pack+FORCE block. Caller enables/clears regulator around the call.

**Deferral trigger (D-02):** if `test_golden_eprom_0x07/08/0B_write` or `test_golden_flash_intel_write`
trace order changes and won't zero-diff, defer P3 with a FUT/CR row and leave both handlers in
pre-extraction duplicated form. **Run the full `pio test -e native`** — the 0x100 `VPE_DROP` bit is
LOW-BYTE-invisible in golden traces (RESEARCH Pitfall 5), so the INV-01/INV-03 bit asserts are the
complementary guard.

**Match quality:** exact (body byte-identical) but high structural-divergence risk on the surround.

---

### P5 — `poll_readback` primitive (PRIM-05) — SECOND-HIGHEST RISK (D-02)

**Three sites, THREE different loop shapes.** Only sites 1+2 share a kernel; eprom's site is a
different algorithm (buffer-wide bitmask). Outer retry/page/erase algorithms stay intact.

**Site 1 (single-addr poll) — analog:** `eeprom_28c.cpp:156-176`
```cpp
static bool eeprom28c_wait_for_write(firestarter_handle_t* handle, uint32_t address, uint8_t expected) {
    uint8_t observed = 0;
    for (uint16_t j = 0; j < 2000; j++) {                  // <-- iteration cap 2000 (PARAMETER)
        delayMicroseconds(10);
        observed = handle->firestarter_get_data(handle, address);
        if (observed == expected) { return true; }
    }
    {   uint8_t _b[5];                                     // <-- error frame DIVERGES (order + msg id)
        _b[0]=addr>>16; _b[1]=addr>>8; _b[2]=addr; _b[3]=expected; _b[4]=observed;
        LOG_ERROR_ID_BYTES(MSG_ERR_EEPROM_TIMEOUT, _b, 5);
    }
    handle->response_code = RESPONSE_CODE_ERROR;
    return false;
}
```

**Site 2 (single-addr poll) — analog:** `flash_type_4.cpp:119-141` — **SAME loop, DIFFERENT params:**
- iteration cap `1024` (not 2000)
- error frame `MSG_ERR_FL4_VERIFY_TIMEOUT` with **different `_b[]` byte order**: `_b[0]=expected`,
  `_b[1..3]=address`, `_b[4]=observed` (eeprom28c puts address first, expected at `_b[3]`).

→ The shared kernel between sites 1+2 is the bounded `for { delayMicroseconds(10); observed=get_data(addr); if(==expected) return true }`. The **iteration cap and the entire error frame MUST be parameters** (or the traces diverge). Pass them in, or share only the inner read-compare leaf.

**Site 3 (whole-buffer bitmask) — DIFFERENT algorithm, do NOT unify:** `eprom.cpp:182-194`
```cpp
static int verify_and_update_mask(firestarter_handle_t* handle, uint8_t* mismatch_bitmask) {
    int mismatch_count = 0;
    for (uint32_t i = 0; i < handle->data_size; i++) {         // whole buffer, NOT single addr
        if (handle->firestarter_get_data(handle, (handle->address + i)) != (uint8_t)handle->data_buffer[i]) {
            mismatch_count++;
            mismatch_bitmask[i / 8] |= (1 << (i % 8));
        } else {
            mismatch_bitmask[i / 8] &= ~(1 << (i % 8));
        }
    }
    return mismatch_count;                                     // returns count, no timeout, no error frame
}
```
The outer retry loop `eprom_write_execute:216-232` (NUMBER_OF_RETRIES + pulse_delay ramp) stays
untouched. The only shareable atom here is the leaf "read addr, compare expected byte" — over-sharing
this site will change the trace.

**Recommended cut:** share eeprom28c+flash4 (params = iteration cap + error-frame closure), OR a tiny
`read-compare-byte` leaf used by all three. **Defer P5 (D-02)** if `test_golden_eeprom28c_write` or
`test_golden_flash4_write` element/count drifts.

**Match quality:** exact (sites 1+2 loop body); site 3 is a partial/leaf match only.

---

### P7 — SDP / const-table dedup (PRIM-02) — WARM-UP, lowest risk, NO new module

**This is delete-not-merge — the tables are byte-identical (verified).** Stays flash-local in
`flash_utils.h` (D-03); does NOT touch `primitives.cpp`.

**Edit 1 — delete dead duplicate in `include/flash_utils.h:48-52`:**
```cpp
    const byte_flip_t FLASH_ENABLE_WRITE_PROTECTION[] = {   // byte-identical to FLASH_ENABLE_WRITE (42-46)
        {0x5555, 0xAA}, {0x2AAA, 0x55}, {0x5555, 0xA0},
    };
```
Grep confirms ZERO callers (`grep -rn FLASH_ENABLE_WRITE_PROTECTION src/ include/` → only the
definition at `flash_utils.h:48`). Delete it. Savings = every TU that includes `flash_utils.h`
drops its internal-linkage copy.

**Edit 2 — redirect `eeprom_28c.cpp`'s local table to the shared one:**
- `EEPROM_SDP_DISABLE` (`eeprom_28c.cpp:47-54`) is byte-identical to `FLASH_DISABLE_WRITE_PROTECTION`
  (`flash_utils.h:53-60`) — both the 6-write `…{0x5555,0x80}…{0x5555,0x20}` sequence.
- Single caller: `eeprom_28c.cpp:124` `flash_execute_command(EEPROM_SDP_DISABLE);`
- `eeprom_28c.cpp` already `#include "flash_utils.h"` (the table is in scope). Delete the local
  `EEPROM_SDP_DISABLE`, change line 130 to `flash_execute_command(FLASH_DISABLE_WRITE_PROTECTION);`.

**Warning sign (RESEARCH Pitfall 1):** if `test_golden_eeprom28c_write` changes after P7, the tables
were NOT identical — STOP and inspect. They are identical; expect zero-diff.

**Match quality:** exact (byte-identical const data).

---

## Shared Patterns (cross-cutting — apply to every touched handler)

### Error / WARN-vs-ERROR frame idiom (the universal FORCE-downgrade)
**Source:** `flash_utils.cpp:118-124` (canonical); replicated at `eprom.cpp:362-368`,
`eeprom_28c.cpp:102-108`, `flash_intel.cpp:224-230`, the two VPP sites, the three poll sites.
```cpp
if (is_flag_set(FLAG_FORCE)) {
    LOG_WARN_ID_BYTES(MSG_WARN_<X>, _b, N);
    handle->response_code = RESPONSE_CODE_WARNING;
} else {
    LOG_ERROR_ID_BYTES(MSG_ERR_<X>, _b, N);
    handle->response_code = RESPONSE_CODE_ERROR;
}
```
**Apply to:** every extracted primitive. Status is reported ONLY via `handle->response_code`
(WARNING/ERROR) + a `LOG_*_ID_BYTES` frame — never a return value or a thrown exception. Each call
site checks `if (handle->response_code == RESPONSE_CODE_ERROR) return;` after the primitive
(see `eprom.cpp:345-346`, `flash_intel.cpp:136-143`, `eeprom_28c.cpp:123-125`).

### `_b[]` byte-packing idiom (big-endian, manual)
**Source:** `flash_utils.cpp:107-105` (the 4-byte chip-id pack). Every frame manually packs
`uint8_t _b[N]` MSB-first inside a local `{ }` block, then one `LOG_*_ID_BYTES(MSG, _b, N)`.
The exact `_b[]` length AND byte order is part of the golden-trace contract — **never reorder**
(P5's two poll sites deliberately differ; that difference must be preserved as a parameter).

### Protocol-keying (D-06 / SAFE-01) — NEVER `electrical.type`
**Source:** `eprom.cpp:198` & `eprom.cpp:271` (`handle->protocol == 0x0B || is_flag_set(FLAG_VPE_AS_VPP)`).
WARNING-5 structural guards `using_p1_as_vpp(handle)` (`eprom.cpp:373`) and the host
`novpp_in_eprom`/`eeprom28c_in_eprom` checks MUST survive. All behavioral branching in a primitive
keys on `handle->protocol` and `handle` flags only.

### Register-write convention
**Source:** `flash_utils.cpp:44-48`, `eprom.cpp` throughout — always
`handle->firestarter_set_control_register(handle, <CTRL_* bitmask>, <0|1>)` and
`handle->firestarter_get_data(handle, addr)` (function-pointer indirection through `handle`,
never a direct `rurp_*` call inside `proms/` handler logic). Primitives use the same indirection.

### Refactor-under-test commit pattern (D-01/D-02)
**Source:** Phase 87-04 `DELTA≤16` gate + Phase 88 golden oracle. One atomic commit per primitive;
between commits rerun `pio test -e native` (byte-exact golden), `pio run -e leonardo` (delta ≤+16),
`check_dispatch.py` (0 violations), `diff_db.py` (empty). Independently reversible → enables
abort-that-primitive-and-continue.

---

## No Analog Found

**None.** Every primitive has an in-repo verbatim precedent:

| Primitive | Precedent in tree |
|-----------|-------------------|
| `chip_id_report` (P4) | `flash_util_check_chip_id_execute` (`flash_utils.cpp:107`) — already the exact primitive, 4 byte-identical tails |
| `vpp_check_window` (P3) | `eprom_check_vpp` body == `flash_intel_check_vpp` body, verbatim |
| `poll_readback` (P5) | `eeprom28c_wait_for_write` == `flash4_wait_for_page_write` loop (params differ) |
| P7 tables | `FLASH_ENABLE_WRITE` / `FLASH_DISABLE_WRITE_PROTECTION` already present |

The new module `primitives.{cpp,h}` is original authorship only in *location*; its header
convention copies `eprom.h`, its TU/banner convention copies `flash_utils.cpp`, and every function
body is lifted from an existing handler. No RESEARCH.md fallback patterns are needed.

---

## Metadata

**Analog search scope:** `firestarter/src/proms/`, `firestarter/include/`, `firestarter/platformio.ini`
**Files scanned (read live this session):** `flash_utils.{h,cpp}`, `eprom.cpp` (170-386),
`eeprom_28c.cpp` (40-176), `flash_intel.cpp` (40-232), `flash_type_4.cpp` (110-159), `eprom.h`,
`platformio.ini` (69-131); grep-verified P7 table callers.
**Line-number reconciliation vs CONTEXT/RESEARCH:** all verified accurate — `flash_util_check_chip_id_execute`
at `flash_utils.cpp:107` (report tail 112-125); eprom VPP `262-325`, eprom verify-mask `182-194`,
eprom chip-id tail `356-369`; eeprom28c SDP table `47-54`, chip-id `77-116`, poll `156-176`;
flash_intel VPP `52-108`, chip-id `213-232`; flash4 poll `119-141`, P4 delegate `143-145`.
`FLASH_ENABLE_WRITE_PROTECTION` confirmed callerless (dead); `EEPROM_SDP_DISABLE` one caller (line 130).
**Pattern extraction date:** 2026-06-26
