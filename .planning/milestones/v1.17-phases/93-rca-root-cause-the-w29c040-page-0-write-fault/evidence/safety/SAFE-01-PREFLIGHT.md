---
artifact: SAFE-01-PREFLIGHT
phase: 93-rca-root-cause-the-w29c040-page-0-write-fault
plan: 01
recorded: 2026-06-26
recorder: executor (automated — no bench hardware needed for native+DB inspection)
---

# SAFE-01 Pre-flight Verification — Phase 93 RCA

This document records the four SAFE-01 checklist verdicts that must be
established BEFORE any bench task (Plans 02–04) proceeds. Per the RESEARCH
§ "Security Domain" definition, each verdict carries raw evidence.

---

## Checklist Item 1 — `test_flash4_write_execute_no_vpp` (VPP-free write path)

**Verdict: GREEN — CONFIRMED**

The native flash4 validation suite was run from `/workspaces/firestarter`:

```
pio test -e native -f "*test_val_flash4*"
```

**Raw output (relevant lines):**

```
test/native/avr/test_val_flash4/test_val_flash4.cpp:487: test_flash4_write_execute_no_vpp	[PASSED]
test/native/avr/test_val_flash4/test_val_flash4.cpp:486: test_flash4_write_execute_emits_sdp	[PASSED]
test/native/avr/test_val_flash4/test_val_flash4.cpp:490: test_inv04_flash4_256b_page_boundary	[PASSED]
test/native/avr/test_val_flash4/test_val_flash4.cpp:493: test_golden_flash4_write	[PASSED]
test/native/avr/test_val_flash4/test_val_flash4.cpp:494: test_golden_flash4_chip_id	[PASSED]
================= 11 test cases: 11 succeeded in 00:00:00.898 =================
```

**Full suite exit:** PASSED (11 test cases: 11 succeeded)

**Interpretation:** `test_flash4_write_execute_no_vpp` PASSED — `flash4_write_execute`
(the operation phase) sets NO `CTRL_VPP_REGULATOR_ENABLE (0x80)` or
`CTRL_VPP_P1_ENABLE (0x08)` bits in any CONTROL_REGISTER write during the write
execute call. The flash4 write-execute path is VPP-free at the register level.

**Note on scope:** This test verifies the WRITE-EXECUTE path (flash4_write_execute).
It does NOT cover flash4_erase_execute. See Checklist Item 2 for the FLAG_CAN_ERASE
finding that makes flash4_erase_execute's VPP assertions relevant.

---

## Checklist Item 2 — `FLAG_CAN_ERASE` absent from W29C040 wire `flags`

**Verdict: RED — HIGH-SEVERITY SAFE-01 VIOLATION (T-93-CANERASE)**

**Raw evidence — W29C040 wire command flags inspection:**

```python
from firestarter.database import EpromDatabase
from firestarter.chip_resolver import resolve_chip

db = EpromDatabase(skip_local_override=True)
data = resolve_chip('W29C040', db)
# Result:
#   algorithm: 5
#   flags: 0x2   ← FLAG_CAN_ERASE (0x02) IS SET
#   memory-size: 524288
#   vpp_mv: 12000
#   pin-count: 32
```

**Inspected `flags` value: `0x02` — FLAG_CAN_ERASE (0x02) IS PRESENT.**

**Causal chain (T-93-CANERASE):**

1. `flags = 0x02` is sent in the wire JSON to the firmware.
2. Firmware `flash4_write_init` (flash_type_4.cpp:78) calls `is_flag_set(FLAG_CAN_ERASE)`.
3. With `FLAG_CAN_ERASE` set and `FLAG_SKIP_ERASE` NOT set, it calls
   `flash4_erase_execute(handle)`.
4. `flash4_erase_execute` (flash_type_4.cpp:155) asserts:
   `CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE | CTRL_VPE_ENABLE`
   — this is a 12V boost regulator assertion on a 5V-only chip.

**Source of the flag:** `database.py:convert_to_programmer()` (line ~605) sets
`FLAG_CAN_ERASE` for any chip whose `electrical.type` is `"EEPROM"` or
`"Flash/EEPROM"`. The W29C040 DB entry has `"type": "Flash/EEPROM"` (line 14458
in chip_database.json). This is correctly derived from the raw DB field but
produces a 12V-on-5V hazard for all `flash4` (protocol 0x05) chips.

**Why this was previously latent:** The RESEARCH (Pitfall 3) flagged this as
"latent dead code — no flash4 DB chip sets FLAG_CAN_ERASE." That assessment was
INCORRECT. The flag IS set. The Pitfall 3 assessment was based on the Phase-74
research's belief that only `0x07` EE-EPROM chips would have this flag, but
`convert_to_programmer` applies it to ALL `Flash/EEPROM` type chips including
those on protocol 0x05.

**Severity: HIGH**

**Action required before bench tasks (Plans 02–04) proceed:**
The bench plans MUST NOT issue `firestarter write W29C040` against a chip that
has not had `FLAG_SKIP_ERASE` forced — OR the host/firmware must be patched so
`FLAG_CAN_ERASE` does not route through `flash4_erase_execute` for protocol 0x05.
This is a fix-phase (Phase 94) concern, but it MUST be acknowledged here and
the bench operator must use `--skip-erase` or equivalent to avoid 12V on the
5V W29C040 during the RCA bench runs.

**Recommended safe repro command:**
```bash
firestarter write -b --skip-erase W29C040 /tmp/w29c040_img.bin
```
The `--skip-erase` flag sets `FLAG_SKIP_ERASE (0x04)` which bypasses
`flash4_erase_execute` in `flash4_write_init`.

---

## Checklist Item 3 — SDP emitted + 256B page size confirmed

**Verdict: GREEN — BOTH CONFIRMED**

From the same native test run:

```
test/native/avr/test_val_flash4/test_val_flash4.cpp:486: test_flash4_write_execute_emits_sdp	[PASSED]
test/native/avr/test_val_flash4/test_val_flash4.cpp:490: test_inv04_flash4_256b_page_boundary	[PASSED]
```

**`test_flash4_write_execute_emits_sdp` PASSED:**
`flash4_write_execute` emits the `FLASH_ENABLE_WRITE` SDP 3-byte sequence
(`0x5555←AA, 0x2AAA←55, 0x5555←A0` MSB pattern: `0x55, 0x2A, 0x55`) at the
start of each page load. The Phase-74 "missing SDP" trap is ruled out — SDP
is present in the current `a296195` firmware build.

**`test_inv04_flash4_256b_page_boundary` PASSED:**
For a 512KB chip (W29C040, `mem_size=524288`), a 65-byte write from address 0
fires exactly ONE SDP (at address 0, which is first_byte + page_start).
Address 64 is a 64B boundary but NOT a 256B boundary — so it does NOT fire a
second SDP. This proves `flash4_page_size(524288) = 256` (not the old fixed 64).
The Phase-74 "wrong page size" trap is ruled out — 256B pages are correct for W29C040.

**Implication:** The RCA must search deeper than the Phase-74 hypotheses. Both
SDP emission and 256B page sizing are already correct in the firmware. The
page-0 write fault's root cause is NOT "missing SDP" and NOT "wrong page size."

---

## Checklist Item 4 — `resolve_chip("W29C040")` normal-path resolution

**Verdict: GREEN — CONFIRMED (normal path, no `--force` bypass)**

```python
from firestarter.database import EpromDatabase
from firestarter.chip_resolver import resolve_chip

db = EpromDatabase(skip_local_override=True)
data = resolve_chip('W29C040', db)
# Resolved successfully (no ChipNotFoundError, no ChipNotImplementedError)
# support_status = "supported" — passes the in-host refusal guard
# Resolved fields:
#   algorithm: 5         (protocol 0x05 — flash4)
#   pin-count: 32
#   memory-size: 524288  (512 KB)
#   vpp_mv: 12000
#   chip-id: 55878       (0xDA46 — W29C040 manufacturer+device ID)
#   bus-config: {'bus': [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,20,21], 'rw-pin': 22}
#   pinout: DIP32_SST39SF040 (inferred from bus-config/pin-count)
```

`resolve_chip("W29C040")` resolves through the normal `support_status="supported"` gate
without requiring `--force`. SAFE-01 escape-hatch precondition is met: no test-only
bypass is needed or introduced anywhere in Phase 93.

---

## Summary Table

| # | Checklist Item | Verdict | Severity |
|---|---------------|---------|----------|
| 1 | `test_flash4_write_execute_no_vpp` — write-execute VPP-free | GREEN | — |
| 2 | `FLAG_CAN_ERASE` absent from W29C040 wire `flags` | **RED — VIOLATED** | **HIGH (T-93-CANERASE)** |
| 3 | SDP emitted (`test_flash4_write_execute_emits_sdp` PASSED) | GREEN | — |
| 3 | 256B page (`test_inv04_flash4_256b_page_boundary` PASSED) | GREEN | — |
| 4 | `resolve_chip("W29C040")` normal-path (no `--force`) | GREEN | — |

---

## SAFE-01 Overall Verdict: CONDITIONAL

**The write-execute path itself is VPP-free (Item 1, GREEN).** SDP and page
size are correct (Item 3, GREEN). Normal resolve path is confirmed (Item 4, GREEN).

**HOWEVER: Item 2 is a HIGH-severity violation (T-93-CANERASE).** The W29C040
wire command carries `flags=0x02` (FLAG_CAN_ERASE), which routes `flash4_write_init`
through `flash4_erase_execute` — a function that asserts 12V (CTRL_VPP_REGULATOR_ENABLE)
on a 5V-only chip. This is a latent hardware-damage path.

**Bench Plans 02–04 MUST use `--skip-erase` (or the equivalent `FLAG_SKIP_ERASE`
operation flag) to bypass `flash4_erase_execute` for the duration of the RCA.
The full fix (preventing `FLAG_CAN_ERASE` from being set for protocol 0x05 chips,
OR preventing `flash4_erase_execute` from asserting VPP for 5V chips) is deferred
to Phase 94 (FIX-01).**

This finding is referenced in evidence/93-RCA-FINDINGS.md § "SAFE-01 —
Non-Bypass Confirmation" per the SAFE-01 cross-link requirement.
