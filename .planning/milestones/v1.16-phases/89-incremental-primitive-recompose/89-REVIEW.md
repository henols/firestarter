---
phase: 89-incremental-primitive-recompose
reviewed: 2026-06-26T00:00:00Z
depth: standard
files_reviewed: 8
files_reviewed_list:
  - firestarter/include/flash_utils.h
  - firestarter/include/primitives.h
  - firestarter/src/proms/eeprom_28c.cpp
  - firestarter/src/proms/eprom.cpp
  - firestarter/src/proms/flash_intel.cpp
  - firestarter/src/proms/flash_type_4.cpp
  - firestarter/src/proms/flash_utils.cpp
  - firestarter/src/proms/primitives.cpp
findings:
  critical: 1
  warning: 2
  info: 1
  total: 4
status: clean
---

# Phase 89: Code Review Report

**Reviewed:** 2026-06-26
**Depth:** standard
**Files Reviewed:** 8
**Status:** issues_found

## Summary

Reviewed the Phase 89 "incremental primitive recompose" refactor (commits
`0052c42..abbbb5c`) against the pre-phase inline call sites via `git diff`.
The stated contract is behavior-preserving: four primitives (`chip_id_report`,
`vpp_check_window`, `poll_readback`, plus a P7 dead-code dedup) extracted into
`primitives.cpp` must keep error-frame ordering, timeout caps, and the SAFE-04
VPP threshold byte-identical to their originals.

Three of the four extractions are faithful:

- **`vpp_check_window`** is byte-identical to both removed inline bodies
  (eprom.cpp + flash_intel.cpp). HIGH threshold `vpp_mv > (uint32_t)handle->vpp_mv + 500`
  and LOW floor `vpp_mv < (uint32_t)handle->vpp_mv * 95 / 100` are preserved, the
  `uint32_t` casts that prevent the `uint16_t vpp_mv` field from overflowing the
  arithmetic are intact, and the `_b[8]` MSB-first packing matches. SAFE-04 over-voltage
  block is preserved. No regulator writes leaked into the primitive (D-06 intact).
- **`poll_readback`** preserves the per-iteration `delayMicroseconds(10)` → read →
  compare, the caps (2000 eeprom28c / 1024 flash4), the `observed` write-back on
  timeout, and the per-site error frames (different MSG id + `_b[]` byte order) stayed
  in the callers. `uint16_t` loop counter cannot overflow at either cap.
- **`chip_id_report`** is byte-identical for three of its four call sites
  (eeprom_28c, flash_intel, flash_utils) and for the `eprom_generic_init` path.

The **fourth `chip_id_report` call site — the EPROM `CMD_CHECK_CHIP_ID` path — is a
behavior regression** (CR-01 below). The original `eprom_internal_check_chip_id`
keyed its WARNING-vs-ERROR decision on its `error_code` parameter, not on `FLAG_FORCE`.
The `CMD_CHECK_CHIP_ID` caller passes `RESPONSE_CODE_ERROR` **unconditionally**, so
under the old code a mismatch on `firestarter id --force` was always an ERROR. The
new code routes through `chip_id_report`, which keys on `FLAG_FORCE`, so the same
operation now downgrades a mismatch to WARNING. This is host-observable and is not
caught by the golden chip-id trace (which uses a *matching* ID).

## Resolution

**CR-01 and WR-02 resolved** in firmware commit `a296195` on
`v1.16-protocol-first-architecture-rebuild` (2026-06-26).

Approach applied: (a) add explicit `bool force_warning` parameter to
`chip_id_report()` — FLAG_FORCE is no longer read inside the primitive.
`eprom_internal_check_chip_id` now passes `error_code == RESPONSE_CODE_WARNING`
(not `is_flag_set(FLAG_FORCE)`) so the CHECK_CHIP_ID path gets `false` (ERROR
unconditional) while the generic-init path still passes the FORCE-derived value.
Three flash/eeprom28c call sites pass `is_flag_set(FLAG_FORCE)` explicitly.

WR-02 gap closed by three new mismatch-fork tests in `test_val_eprom`:
`test_wr02a` (CHECK_CHIP_ID + FORCE → ERROR), `test_wr02b` (generic-init + FORCE → WARNING),
`test_wr02c` (generic-init without FORCE → ERROR).

All 105 native tests pass; Leonardo build 25136 B (net -518 B vs baseline).

WR-01 is resolved as a side-effect: the `error_code` parameter is no longer dead
(the body now uses it); the `(void)error_code` suppression and stale comment are removed.

IN-01 is informational (no code change required) — remains open/noted.

## Critical Issues

### CR-01: EPROM `CMD_CHECK_CHIP_ID` no longer reports a mismatch as ERROR under `--force` (behavior regression) — RESOLVED

**File:** `firestarter/src/proms/eprom.cpp:310-314` (and call site `:137-140`)

**Issue:**
The pre-phase `eprom_internal_check_chip_id(handle, error_code)` selected its
response on the **parameter**, not on `FLAG_FORCE`:

```c
// ORIGINAL (0052c42^):
if (error_code == RESPONSE_CODE_WARNING) { LOG_WARN...; RESPONSE_CODE_WARNING; }
else                                     { LOG_ERROR...; RESPONSE_CODE_ERROR; }
```

There are two callers with *different* `error_code` values:

1. `eprom_generic_init` (eprom.cpp:306) passes
   `is_flag_set(FLAG_FORCE) ? RESPONSE_CODE_WARNING : RESPONSE_CODE_ERROR`
   — equivalent to keying on `FLAG_FORCE`. **No change.**
2. `eprom_check_chip_id_execute` (eprom.cpp:139, the `CMD_CHECK_CHIP_ID` /
   `firestarter id` path) passes `RESPONSE_CODE_ERROR` **unconditionally** — a
   mismatch was *always* ERROR, even with `FLAG_FORCE` set.

The refactor replaced the body with `(void)error_code; chip_id_report(handle, ...)`,
and `chip_id_report` keys solely on `is_flag_set(FLAG_FORCE)`. For caller (2) with
`FLAG_FORCE` set + an ID mismatch, the firmware now emits
`LOG_WARN_ID_BYTES(MSG_WARN_CHIP_ID_MISMATCH)` + `RESPONSE_CODE_WARNING` instead of
the original `LOG_ERROR_ID_BYTES(MSG_ERR_CHIP_ID_MISMATCH)` + `RESPONSE_CODE_ERROR`.

This is reachable from the host: `cli_handlers.py:580-595` wires
`firestarter id <chip> --force` → `CMD_CHECK_CHIP_ID` with `FLAG_FORCE`, and
`eprom_operations.check_eprom_id` branches on `response.type == "ERROR"`. The
WARNING-vs-ERROR flip changes the host-visible outcome (different MSG id, different
response tag, different exit path) for a `behavior-preserving` refactor.

The golden chip-id trace (`test_val_eprom.cpp:579`, `golden_eprom_chip_id.inc`)
uses a **matching** chip_id (0x1F00 == 0x1F00), so it exercises only the no-mismatch
branch and cannot detect this divergence — matching the "behavior drift the golden
traces might NOT catch" concern.

**Fix:** Restore the per-call-site semantics. Either honor the `error_code` parameter
in the primitive, or have the primitive's caller preserve the unconditional-ERROR
behavior for the check-chip-id path. Minimal restoration without re-inlining:

```c
void eprom_internal_check_chip_id(firestarter_handle_t* handle, uint8_t error_code) {
    LOG_DEBUG_ID_SUB(DBG_CHECK_CHIP_ID);
    uint16_t read_id = eprom_get_chip_id(handle);
    if (read_id == handle->chip_id) return;
    uint8_t _b[4];
    _b[0] = (uint8_t)((read_id >> 8) & 0xFF);
    _b[1] = (uint8_t)(read_id & 0xFF);
    _b[2] = (uint8_t)((handle->chip_id >> 8) & 0xFF);
    _b[3] = (uint8_t)(handle->chip_id & 0xFF);
    if (error_code == RESPONSE_CODE_WARNING) {
        LOG_WARN_ID_BYTES(MSG_WARN_CHIP_ID_MISMATCH, _b, 4);
        handle->response_code = RESPONSE_CODE_WARNING;
    } else {
        LOG_ERROR_ID_BYTES(MSG_ERR_CHIP_ID_MISMATCH, _b, 4);
        handle->response_code = RESPONSE_CODE_ERROR;
    }
}
```

(If the intended new behavior really is "downgrade `id --force` mismatches to
WARNING," that is a deliberate semantic change that must be documented and
explicitly excluded from the behavior-preserving claim — and a golden/unit test
with a *mismatched* ID under `FLAG_FORCE` should pin it.)

## Warnings

### WR-01: `error_code` parameter is now dead/misleading — the regression vehicle — RESOLVED (side-effect of CR-01 fix)

**File:** `firestarter/src/proms/eprom.cpp:310-313`

**Issue:** `eprom_internal_check_chip_id(handle, uint8_t error_code)` now discards
its second argument via `(void)error_code`, while two callers still pass distinct
values (`RESPONSE_CODE_ERROR` vs a `FLAG_FORCE`-derived value). The signature
advertises a contract the body no longer honors — this is exactly what masks CR-01.

**Fix:** If CR-01 is fixed by honoring the parameter, this resolves itself. If the
parameter is genuinely obsolete, drop it from the signature and both call sites
(eprom.cpp:139 and :306) so the dead-arg cannot silently diverge again. Do not leave
a `(void)`-suppressed parameter that two callers still populate differently.

### WR-02: No mismatch-under-FLAG_FORCE test guards any of the four `chip_id_report` sites — RESOLVED

**File:** `firestarter/src/proms/primitives.cpp:45-60`

**Issue:** `chip_id_report` is the one primitive whose two branches (FORCE→WARNING,
no-FORCE→ERROR) are behaviorally load-bearing, yet the golden traces for all four
families (`golden_eprom_chip_id`, `golden_flash4_chip_id`, `golden_flash_intel_chip_id`)
use a **matching** ID and never enter the mismatch branch. The extraction therefore
ships with zero coverage of the WARNING/ERROR fork — the precise place CR-01 hides.

**Fix:** Add a native unit test (per family, or at least the eprom CHECK_CHIP_ID path)
that drives `chip_id != handle->chip_id` once with `FLAG_FORCE` clear (expect
`RESPONSE_CODE_ERROR` + `MSG_ERR_CHIP_ID_MISMATCH`) and once with `FLAG_FORCE` set
(expect the intended outcome). This converts the silent invariant into an enforced one.

## Info

### IN-01: `FLASH_DISABLE_WRITE_PROTECTION` is now the shared SDP-disable bus sequence for both flash and EEPROM (naming)

**File:** `firestarter/include/flash_utils.h:48-55`, used at `firestarter/src/proms/eeprom_28c.cpp:101`

**Issue:** The P7 dedup correctly deletes the duplicate `EEPROM_SDP_DISABLE` table and
redirects eeprom28c to `FLASH_DISABLE_WRITE_PROTECTION`. The two tables were byte-identical
(`AA/55/80/AA/55/20`), so this is behavior-preserving. The remaining `flash_utils.h` name
`FLASH_DISABLE_WRITE_PROTECTION` now serves the 5V EEPROM SDP-disable path too, which is
slightly misleading at the 0x0D call site.

**Fix:** Optional — a one-line comment at the `flash_utils.h` declaration noting it is the
shared AMD/JEDEC SDP-disable sequence used by both flash3/4 and eeprom28c (0x0D) would
prevent future confusion. No code change required.

---

_Reviewed: 2026-06-26_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
