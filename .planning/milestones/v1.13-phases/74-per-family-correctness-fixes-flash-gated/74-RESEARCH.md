# Phase 74: Per-Family Correctness Fixes (flash-gated) — Research

**Researched:** 2026-06-18
**Domain:** Embedded C++ firmware (Arduino/AVR), flash memory page-write algorithms, AMD/JEDEC SDP protocol, Python host reconciliation
**Confidence:** HIGH (firmware source verified by direct read; W29C040 datasheet facts verified across multiple sources)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**FIX-01 — SRAM `configure_sram` no-op question → CLOSED NOT-NEEDED (evidence-gated on VAL-06)**
Phase 73 VAL-06 resolved this to `table-stakes-PASS`. No firmware change. The plan must mark FIX-01 closed-with-evidence, NOT implement an SRAM rewrite.

**FIX-02 — flash4 correctness → EXPANDED to TWO defects:**
- Defect A: Add `case CMD_CHECK_CHIP_ID:` to `configure_flash4` mirroring `flash3_check_chip_id_execute`. Proven by RED→GREEN native test.
- Defect B: Investigate AND fix the W29C040 write algorithm failure found in Phase 73 VAL-04 (exit code 2, write -b timeout). Then Tier-3 re-bench to PASS on Leonardo.
- VPP invariant: flash4 is a 5V part family. Any handler change must NOT enable the VPP regulator. If any register change touches VPP, it requires a register-bit-sequence native test + chip-OUT VPP multimeter dry-run before any seated write.

**FIX-03 — stale "0x39 = 0 chips, future-proofed" comment → CLOSE-WITH-EVIDENCE + RECONCILE**
The "2 chips" claim in REQUIREMENTS.md is false. Phase 72 GAP-5 confirmed 0 DB chips on 0x39. The plan must:
1. Document FIX-03 closed not-needed against the "2-chip coverage" target.
2. Reconcile firmware↔host 0x39 inconsistency in comments across firmware `memory.cpp` (no change needed), `firestarter/CLAUDE.md`, host `database.py`, `ic_layout.py`. No behavioral wire change needed.

**Cross-cutting constraints (LOCKED):**
- Software-first RED→GREEN: each fix starts from a failing native/wire test, then GREEN.
- No regression: `check_dispatch.py`, `diff_db.py`, and all native suites stay green.
- Flash ceiling: every firmware-touching fix builds `pio run -e leonardo` under ~88% flash; record flash-%.
- Dual-repo lockstep: any wire-touching change is meta-repo `messages.toml`-only → regen both sub-repos; py3.12-masks-CI-3.11 drift gate green.
- Bench precondition: Tier-3 re-bench (FIX-02 Defect B) requires live R1≈270000 readback, retry-on-timeout, Leonardo only (never uno328pb), verify `controller:` identity per port at task start.
- Milestone branch: code commits on `v1.13-algo-validation` in each sub-repo.

### Claude's Discretion

None explicitly listed; research options and make prescriptive recommendations where scope is undefined (e.g., recording-stub test structure for FIX-02B, page size handling strategy).

### Deferred Ideas (OUT OF SCOPE)

- Erase path (ERASE-01) → Phase 75
- GAP-01 / GAP-02 (X88C64 0x34 re-classification) → Phase 76
- flash3/VAL-03 AM29F040 Tier-3 cell (no chip on hand)
- Other SKIP-deferred Tier-3 cells (eeprom28c, flash_intel)
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| FIX-01 | IF VAL-06 confirms `configure_sram` is a silent no-op, correct it; IF it already works, close as not-needed with evidence | VAL-06 = table-stakes-PASS confirmed by Phase 73 SC#4; close not-needed, cite `firestarter_app/val-results/sram/val06-perbyte-verdict.txt` + `validation-matrix.json` |
| FIX-02 | `configure_flash4` handles `CMD_CHECK_CHIP_ID` (Defect A) AND W29C040 write-algorithm failure is fixed (Defect B), proven by native test + Tier-3 re-bench | Defect A: add `case CMD_CHECK_CHIP_ID:` in `configure_flash4` mirroring `flash3_check_chip_id_execute`; Defect B: add SDP unlock + correct PAGE_SIZE 256 for W29C040 family |
| FIX-03 | Stale "0x39 = 0 chips, future-proofed" comment corrected; "2 current 0x39 DB chips" premise false (Phase 72 GAP-5); reconcile firmware↔host 0x39 doc inconsistency | Confirmed 0 DB chips on 0x39 and 0x35; `memory.cpp:89` comment is accurate; reconcile in `firestarter/CLAUDE.md` + `database.py` + `ic_layout.py` |
</phase_requirements>

---

## Summary

Phase 74 delivers three evidence-driven correctness fixes. FIX-01 is already resolved: Phase 73 VAL-06 proved `configure_sram` is not a no-op (FM1608 two-pattern N=2, zero mismatches, authoritative PASS). No firmware change needed for SRAM.

FIX-02 splits into two defects. Defect A is trivial: `configure_flash4` is missing a `case CMD_CHECK_CHIP_ID:` that `configure_flash3` already has — a 5-line mirror of `flash3_check_chip_id_execute` with a new helper function. Defect B is the real engineering work: the W29C040 (Winbond, 512K×8, algorithm 0x05 / configure_flash4) failed Phase 73 Tier-3 bench with exit code 2 because `flash4_write_execute` is missing the AMD/JEDEC Software Data Protection (SDP) 3-byte unlock sequence before each page write AND uses the wrong page size (64 bytes vs the W29C040's 256 bytes). The SDP sequence `{0x5555,0xAA}, {0x2AAA,0x55}, {0x5555,0xA0}` is already encoded as `FLASH_ENABLE_WRITE` in `flash_utils.h` — flash3 uses it per-byte; flash4 must use it per-page. The W29C040 is a 5V-only device with internal VPP generation; the current `flash4_erase_execute` incorrectly asserts `CTRL_VPP_REGULATOR_ENABLE` (12V boost). FIX-02B's fix scope is: fix `flash4_write_execute` to call `flash_execute_command(FLASH_ENABLE_WRITE)` before each 256-byte page load, fix `PAGE_SIZE` to 256, and remove (or gate) the VPP regulator enable from `flash4_erase_execute` for the W29C040 family, all proven by a Tier-1 recording-stub register-sequence test then Tier-3 Leonardo re-bench.

FIX-03 is documentation reconciliation only. Phase 72 confirmed `memory.cpp:89` is accurate (0x39 dispatches to `configure_flash4` by analogy, 0 DB chips). The inconsistency is that host-side comments in `database.py:60` and `ic_layout.py:228` describe 0x35/0x39 as "removed" while firmware `firestarter/CLAUDE.md` calls 0x39 "future-proofed." The reconciliation adds no behavioral change.

**Primary recommendation:** Fix FIX-02B by (1) adding SDP unlock (`flash_execute_command(FLASH_ENABLE_WRITE)`) at the start of each page write in `flash4_write_execute`, (2) changing `PAGE_SIZE` from 64 to 256 in `flash_type_4.cpp`, and (3) for `flash4_erase_execute` — do NOT enable VPP for flash4 chips (all 27 flash4 DB chips are 5V-only page-EEPROMs with internal VPP generation). The existing `FLASH_ENABLE_WRITE` command in `flash_utils.h` is the SDP unlock the W29C040 expects.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| FIX-01 closure — cite evidence | Planning artifact | — | No code change; evidence already on disk in `val-results/sram/` |
| FIX-02A chip-id dispatch | Firmware (`flash_type_4.cpp`) | Tier-1 native test | Handler-level case statement; verified by dispatch register-sequence test |
| FIX-02B SDP write algorithm | Firmware (`flash_type_4.cpp`) | Tier-1 register-sequence test + Tier-3 bench | Core write-path fix; must be proven by side-effect recording AND real chip |
| FIX-02B erase VPP safety | Firmware (`flash_type_4.cpp`) | Tier-1 VPP-bit assertion test | Safety invariant: no VPP register bits set for 5V-only flash4 family |
| FIX-03 0x39 reconciliation | Firmware/host doc comments | — | Comment-only changes in `CLAUDE.md`, `database.py`, `ic_layout.py` |
| Non-regression gate | Host tools (`check_dispatch.py`, `diff_db.py`) | All native suites | Automated gates; must stay green across all three fixes |

---

## Standard Stack

### Core (firmware)
| Component | Version | Purpose | Notes |
|-----------|---------|---------|-------|
| `firestarter/src/proms/flash_type_4.cpp` | current | configure_flash4 + flash4_write_execute (the fix target) | Contains the two defects |
| `firestarter/src/proms/flash_utils.h` + `flash_utils.cpp` | current | `FLASH_ENABLE_WRITE` constant + `flash_util_byte_flipping` + `flash_util_verify_operation` | SDP unlock lives here already |
| `firestarter/src/proms/flash_type_3.cpp` | current | `flash3_check_chip_id_execute` + `flash3_get_chip_id` — the Defect A mirror source | Copy pattern from here |
| `firestarter/include/flash_utils.h` | current | `FLASH_ENABLE_WRITE` byte_flip_t constant: `{0x5555,0xAA},{0x2AAA,0x55},{0x5555,0xA0}` | This IS the SDP unlock sequence |
| `firestarter/test/native/avr/test_val_flash4/test_val_flash4.cpp` | current | Existing VPP-safety test suite; RED→GREEN tests for Defect A and B land here or in a new sibling | 6 tests currently GREEN; extend without regressing |
| `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` | current | Dispatch suite; Defect A chip-id test lands here | 15 tests currently GREEN |

### Core (host — FIX-03 reconciliation targets)
| Component | Lines | Content |
|-----------|-------|---------|
| `firestarter_app/firestarter/database.py` | 60-63 | Comment: `# 0x35 … and 0x39 … removed in Phase 57 (DEC-05) to match build_db.py's canonical allowlist; no DB chip uses either protocol.` |
| `firestarter_app/firestarter/ic_layout.py` | 228-229 | Comment: `# 0x35 (ITE EC MCU) and 0x39 (phantom) removed in Phase 57 (DEC-05); they are not memory protocols and no DB chip uses them.` |
| `firestarter/CLAUDE.md` | dispatch table row 4 | `protocol ∈ {0x05, 0x35, 0x39} → configure_flash4() — page-write flash (0x39 future-proofed, no chips in current DB)` |
| `firestarter/src/proms/memory.cpp` | 89 | `if (handle->protocol == 0x05 || handle->protocol == 0x35 || handle->protocol == 0x39)` — no comment; comment is in CLAUDE.md |

### Non-regression gates
| Tool | Command | Current State |
|------|---------|---------------|
| `check_dispatch.py` | `python3 tools/check_dispatch.py` | PASS: 744 chips, 730 supported, 0 regressions [VERIFIED: direct run] |
| `diff_db.py` | `python3 tools/diff_db.py` | PASS: 0 changed chips [VERIFIED: direct run] |
| Native firmware tests | `pio test -e native` | PASS: 77/77 [VERIFIED: direct run] |
| Leonardo flash build | `pio run -e leonardo` | SUCCESS: **88.9%** (25482/28672 bytes) [VERIFIED: direct build] |

**Flash budget note [VERIFIED: direct build]:** Current flash is 88.9% (25482/28672). The ~88% "ceiling" in CONTEXT.md is already exceeded by 0.9%. FIX-02A (CMD_CHECK_CHIP_ID case + helper call) adds ~60-80 bytes. FIX-02B (SDP call + PAGE_SIZE change) adds ~30-50 bytes via the `flash_execute_command` inline. Total expected delta: ~100-130 bytes → estimated 89.3-89.8%. This is within functional headroom (Leonardo has 32KB; build uses 28672 target). The planner must record the actual post-fix flash-% and confirm it does not cause link failures.

---

## W29C040 Datasheet Analysis — FIX-02B Root Cause

### What the W29C040 actually is

The W29C040 is a **5V-only page-mode EEPROM** (not an AMD-style sector-erase flash). It internally generates its own programming voltage. Key properties [CITED: Scribd W29C040 overview; multiple secondary sources]:

| Property | Value |
|----------|-------|
| Organization | 512K × 8 (524,288 bytes) |
| Supply voltage | 5V VCC only — **no external VPP pin required** |
| Internal VPP | Generated internally during write cycle |
| Page size | **256 bytes** (NOT 64 bytes as currently coded) |
| Write cycle | Self-timed automatic erase+program per page (≈5 ms typical) |
| Write type | Page load → internal erase+program (not byte-at-a-time) |
| SDP | Shipped with Software Data Protection **enabled** by default |
| Chip erase | 6-byte software sequence (separate from page write) |
| Chip ID VPP field in DB | vpp_mv=12000 in chip_database.json — this is the **WP/VPP pin voltage for chip-ID read**, NOT a programming VPP; all 27 flash4 chips show this value; firmware must NOT enable the boost regulator for writes |

### SDP 3-byte unlock sequence

The W29C040's SDP "write enable" sequence is the standard AMD/JEDEC page-load command sequence [CITED: SST29EE010 datasheet; AT29C040A application notes; multiple EEPROM programmer sources]:

```
Write 0xAA to address 0x5555
Write 0x55 to address 0x2AAA
Write 0xA0 to address 0x5555
```

Then immediately load the page bytes (up to 256 bytes, sequentially or in any order within the page).

**This sequence is ALREADY DEFINED in `flash_utils.h` as `FLASH_ENABLE_WRITE`:**
```cpp
const byte_flip_t FLASH_ENABLE_WRITE[] = {
    {0x5555, 0xAA},
    {0x2AAA, 0x55},
    {0x5555, 0xA0},
};
```

`flash3_write_execute` calls `flash_execute_command(FLASH_ENABLE_WRITE)` before EACH byte write. The W29C040 needs it called before each PAGE load (the 3-byte sequence marks the start of a page load cycle, then the page bytes follow, then the chip self-programs).

### Why the current flash4_write_execute fails

The current `flash4_write_execute` [VERIFIED: direct read of `firestarter/src/proms/flash_type_4.cpp`]:

```cpp
void flash4_write_execute(firestarter_handle_t* handle) {
    for (uint32_t i = 0; i < handle->data_size; i++) {
        uint32_t address = handle->address + i;
        uint8_t expected = handle->data_buffer[i];
        handle->firestarter_set_data(handle, address, expected);   // <-- bare write, no SDP unlock

        bool reached_page_end = ((address) % PAGE_SIZE) == PAGE_SIZE - 1;  // PAGE_SIZE=64 -- WRONG
        bool is_last_byte = i == handle->data_size - 1;
        if (reached_page_end || is_last_byte) {
            if (!flash4_wait_for_page_write(handle, address, expected)) {
                return;
            }
        }
    }
}
```

**Two defects in this function:**

1. **Missing SDP unlock:** No `flash_execute_command(FLASH_ENABLE_WRITE)` before loading page bytes. Since the W29C040 ships with SDP enabled, any write without the 3-byte sequence is silently rejected — data never reaches the page buffer, no erase+program fires, chip reads back what was already there (all-0x00 in the Phase 73 FAIL: chip wasn't blank to begin with, and even standalone `write -b` timed out at byte 0x3F).

2. **Wrong PAGE_SIZE:** `#define PAGE_SIZE 64` but W29C040's page is 256 bytes. The poll fires at byte 63 (within an ongoing page load that the chip won't commit until all 256 bytes or a WE# low-to-high timeout). The page doesn't latch until all 256 bytes are loaded or a 150µs inter-byte timeout fires. Polling at byte 63 with DQ7 on an uncommitted page will observe the last byte written, which hasn't been programmed yet — the chip returns the complement of DQ7 (or old data), causing the poll to either time out or incorrectly pass.

### Why the flash4_erase_execute is wrong for W29C040

The current `flash4_erase_execute` [VERIFIED: direct read] asserts `CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE | CTRL_VPE_ENABLE` — this activates the 12V boost regulator. The W29C040 has no external VPP pin; it generates VPP internally. Asserting 12V on the VPP socket line against a W29C040 is an overvoltage hazard. Furthermore, the W29C040's chip erase requires the standard 6-byte AMD software sequence (same as `FLASH_ERASE` in `flash_utils.h`) — not the VPP-asserted OE=12V pulse the current erase function implements.

**Phase 73 FAIL evidence confirms this:** The erase reported "success" (0.06s) but the chip was NOT erased to 0xFF (first byte = 0x00, not 0xFF). The external VPP erase pattern was accepted as a no-op by the 5V-only chip [CITED: `firestarter_app/val-results/flash4/validation-matrix.json` + `73-03-SUMMARY.md`].

### Page size variation across flash4 family — scoping the fix

The 27 flash4 chips in the DB have varying page sizes by chip capacity [ASSUMED from AT29 series datasheet patterns; confirmed for AT29C256=64B, AT29C040=256B, SST29EE010=128B]:

| Chip size | Typical page size | Representative chips |
|-----------|------------------|---------------------|
| 32KB (AT29C256, AT29LV256) | 64 bytes | AT29C256-family |
| 64KB (AT29C512, SST29EE512) | 64-128 bytes | AT29C512, W29C512 |
| 128KB (AT29C010A, SST29EE010) | 128 bytes | SST29EE010, W29C010 |
| 256KB (AT29C020, SST29EE020) | 128-256 bytes | W29C020 |
| 512KB (AT29C040, W29C040) | 256 bytes | W29C040, AT29C040 |

**Critical constraint:** The chip_database.json has NO `page_size` field for flash4 chips (`pulse_duration: "Algorithm Controlled"` only). The firmware cannot derive page size from the wire dict at runtime.

**Recommended fix strategy for PAGE_SIZE:** Change `#define PAGE_SIZE 64` to `#define PAGE_SIZE 256` in `flash_type_4.cpp`. This is the correct value for W29C040 (the failing chip). For chips with smaller pages (e.g., AT29C256 with 64-byte pages), using PAGE_SIZE=256 causes the SDP + page bytes to span multiple 64-byte physical pages — the chip's WE# inactivity timer fires after the 150µs inter-byte gap, committing each physical page automatically, THEN the firmware polls at byte 255. The poll is against the last byte of what the chip committed on the final physical page. This is functionally correct: the chip has already self-programmed all 4 physical pages (4×64B), and the DQ7 poll on the last byte confirms the last page write completion. No data is lost. The only risk is if the inter-byte delay between data writes exceeds 150µs (causing an early commit mid-load). At 16 MHz AVR with the `memory_set_data` path (delayMicroseconds(3) + CE pulse), inter-byte time is well under 150µs.

**Alternative (lower risk, more code):** Read `handle->mem_size` to infer page size: ≤65536 → 64, ≤262144 → 128, else 256. This adds ~15 bytes of code but removes all ambiguity. Recommend the planner choose based on flash budget headroom after FIX-02A.

### Concrete target write algorithm for W29C040

Each 256-byte page write must follow this sequence [CITED: SST29EE010 datasheet; AT29C040 application note structure; confirmed matches `FLASH_ENABLE_WRITE` in `flash_utils.h`]:

```
PHASE 1 — SDP 3-byte load command (uses flash_util_byte_flipping):
  Write 0xAA → address 0x5555
  Write 0x55 → address 0x2AAA
  Write 0xA0 → address 0x5555

PHASE 2 — Load up to 256 bytes into the page buffer:
  Write byte[0] → page_start_address + 0
  Write byte[1] → page_start_address + 1
  ...
  Write byte[255] → page_start_address + 255
  (All within the same 256-byte page boundary)

PHASE 3 — Wait for internal write cycle (auto-triggered by WE# inactivity):
  Poll DQ7 at the last byte address: wait until read_back & 0x80 == written_byte & 0x80
  Timeout: 10ms (W29C040 typical 5ms; 2000 × 10µs = 20ms poll window in current code)
```

The existing `flash4_wait_for_page_write` DQ7 poll loop is correct (polls last-written address, checks DQ7 match). It just needs to be called at 256-byte boundaries, not 64-byte.

**Firmware code change (conceptual):**
```cpp
// In flash_type_4.cpp
#define PAGE_SIZE 256  // W29C040: 256-byte page (was 64 — wrong for W29C040 family)

void flash4_write_execute(firestarter_handle_t* handle) {
    for (uint32_t i = 0; i < handle->data_size; i++) {
        uint32_t address = handle->address + i;
        uint8_t expected = handle->data_buffer[i];

        // SDP unlock: send 3-byte command sequence at the START of each page load
        bool is_page_start = (address % PAGE_SIZE) == 0;
        bool is_first_byte = (i == 0);
        if (is_page_start || is_first_byte) {
            flash_execute_command(FLASH_ENABLE_WRITE);  // {0x5555,0xAA},{0x2AAA,0x55},{0x5555,0xA0}
        }

        handle->firestarter_set_data(handle, address, expected);

        bool reached_page_end = ((address + 1) % PAGE_SIZE) == 0;
        bool is_last_byte = i == handle->data_size - 1;
        if (reached_page_end || is_last_byte) {
            if (!flash4_wait_for_page_write(handle, address, expected)) {
                return;
            }
        }
    }
}
```

**Note on `flash4_erase_execute`:** The VPP-asserting erase must be removed or gated. For the W29C040, chip erase should use `flash_execute_command(FLASH_ERASE)` (the existing 6-byte AMD chip-erase sequence in `flash_utils.h`). However, this changes erase behavior for ALL flash4 chips. The erase path is only triggered when `FLAG_CAN_ERASE` is set — since no flash4 DB chip has `FLAG_CAN_ERASE` enabled (the host only sets it for 0x07-path chips per `database.py:594-597`), the erase path in `flash4_write_init` is dead code for all 27 flash4 DB chips. The planner should confirm this and document accordingly — if erase is never called for flash4 chips via the DB, the VPP bug in `flash4_erase_execute` is latent (won't fire during normal operation). The fix for write only (SDP + PAGE_SIZE) is sufficient to make W29C040 writes work.

### VPP safety — confirmed safe fix

The SDP fix (`flash_execute_command(FLASH_ENABLE_WRITE)`) uses `flash_util_byte_flipping` which calls `handle->firestarter_set_control_register(handle, CTRL_READ_WRITE, 0)` only — it does NOT set `CTRL_VPP_REGULATOR_ENABLE`, `CTRL_VPP_P1_ENABLE`, or `CTRL_VPP_VPE_DROP_ENABLE`. This is confirmed by `flash_utils.cpp:21-28` [VERIFIED: direct read]. The fix cannot accidentally enable the VPP boost regulator.

The existing `test_val_flash4.cpp` suite already asserts that configure_flash4 + CMD_WRITE does not set VPP bits in the CONTROL_REGISTER during the configure phase. The new recording-stub test for FIX-02B must additionally assert that `flash4_write_execute` (operation phase) does not set VPP bits — an operation-phase VPP test, not just configure-phase.

---

## FIX-02A: CMD_CHECK_CHIP_ID Defect — Mirror from flash3

### What is missing

`configure_flash4` (`flash_type_4.cpp:26-40`) handles CMD_WRITE, CMD_ERASE, CMD_BLANK_CHECK but has NO `case CMD_CHECK_CHIP_ID:` [VERIFIED: direct read]. `configure_flash3` (`flash_type_3.cpp:31-51`) has:

```cpp
case CMD_CHECK_CHIP_ID:
    handle->firestarter_operation_init = NULL;
    handle->firestarter_operation_main = flash3_check_chip_id_execute;
    break;
```

`flash3_check_chip_id_execute` calls `flash3_get_chip_id` which uses `flash_execute_command(FLASH_ENABLE_ID)` / `FLASH_DISABLE_ID` (AMD chip-ID read sequence) via `flash_util_byte_flipping`.

### The analog for flash4

A new function `flash4_check_chip_id_execute` mirrors `flash3_check_chip_id_execute` exactly — they both use the same AMD 6-byte ID-read sequence (`FLASH_ENABLE_ID` → read 0x0000/0x0001 → `FLASH_DISABLE_ID`). The flash4 and flash3 chips both use AMD-compatible command sets, so the same ID-read mechanism applies.

**Option A:** Add a new `flash4_check_chip_id_execute` function + `flash4_get_chip_id` in `flash_type_4.cpp` (mirroring flash3 exactly — ~15 lines).
**Option B:** Move `flash3_get_chip_id` to `flash_utils.cpp` as `flash_get_chip_id` and call from both flash3 and flash4. This saves ~10 bytes on flash but introduces an internal API change.

Recommendation: Option A (inline mirror) for this phase — simpler, no API churn. Flash budget is tight but Option A's delta (~60 bytes) is acceptable.

### Native test for Defect A

The `test_configure_memory.cpp` dispatch suite tests `CMD_READ` for all protocols. A new test must use `CMD_CHECK_CHIP_ID` for protocols 0x05, 0x35, and 0x39 and assert `h.firestarter_operation_main != NULL` (i.e., the case was handled and a non-NULL function pointer was set). Pattern:

```cpp
void test_flash4_check_chip_id_0x05_sets_operation(void) {
    firestarter_handle_t h = make_handle(0x05, 0, CMD_CHECK_CHIP_ID);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,
        "CMD_CHECK_CHIP_ID on 0x05 must not error");
    TEST_ASSERT_NOT_NULL_MESSAGE(h.firestarter_operation_main,
        "CMD_CHECK_CHIP_ID must set a non-NULL operation_main");
}
```

This test is currently RED (configure_flash4 has no case for CMD_CHECK_CHIP_ID so `firestarter_operation_main` stays NULL, which is technically not an error today but is the defect). To make it unambiguously RED, the test should assert `!= NULL`.

---

## FIX-03: 0x39 / 0x35 Comment Reconciliation

### Current state of 0x39 / 0x35 across the two repos

**Firmware side [VERIFIED: direct read]:**
- `firestarter/src/proms/memory.cpp:89`: `if (handle->protocol == 0x05 || handle->protocol == 0x35 || handle->protocol == 0x39)` — no inline comment; dispatches correctly to `configure_flash4`. This is accurate behavior.
- `firestarter/CLAUDE.md` dispatch table row 4: `protocol ∈ {0x05, 0x35, 0x39} → configure_flash4() — page-write flash (0x39 future-proofed, no chips in current DB)`. This is accurate about 0x39 (0 chips). But it's silent about 0x35 also having 0 DB chips.

**Host side [VERIFIED: direct read]:**
- `firestarter_app/firestarter/database.py:60-63`: Comment says `# 0x35 (IC2_ALG_ITE — an ITE EC MCU, not a memory algorithm) and 0x39 (phantom — no IC2_ALG constant) removed in Phase 57 (DEC-05) to match build_db.py's canonical allowlist; no DB chip uses either protocol.`
- `firestarter_app/firestarter/ic_layout.py:228-229`: Comment says `# 0x35 (ITE EC MCU) and 0x39 (phantom) removed in Phase 57 (DEC-05); they are not memory protocols and no DB chip uses them.`
- `firestarter_app/tools/build_db.py:128-148`: `KNOWN_PROTOCOLS` set — 0x35 and 0x39 are NOT in the set; comment confirms `# NOT 0x35 or 0x39 — removed by v1.11 DEC-05` [VERIFIED: direct read].

**The inconsistency:** Host calls 0x35 "ITE EC MCU, not a memory algorithm" and 0x39 "phantom (no IC2_ALG constant)." Firmware CLAUDE.md calls 0x39 "future-proofed." These are two different characterizations of the same placeholder-dispatch.

**Phase 72 GAP-5 canonical finding [CITED: `.planning/v1.13-PROTOCOL-ENUMERATION.md` line ~257]:** "0 current DB chips (correct per DEC-05). The 'stale comment' is in REQUIREMENTS.md phrasing — source file audit shows `memory.cpp:89` comment is accurate." The debt is reconciling the docs, not the firmware.

### Target reconciliation

1. **`firestarter/CLAUDE.md` dispatch table row 4** (the only place needing update in the firmware repo): Update to also note that 0x35 is a phantom (0 DB chips), making the note symmetric: `protocol ∈ {0x05, 0x35, 0x39} → configure_flash4() — 0x05 = 27 DB chips; 0x35 and 0x39 = 0 DB chips (phantom entries, future-proofed dispatch preserved for forward compatibility)`.

2. **`firestarter_app/firestarter/database.py:60` and `ic_layout.py:228`** (host side): Add a cross-reference note that firmware still dispatches 0x39 for forward-compat, and that host routes it to `not_implemented` (per `KNOWN_PROTOCOLS` exclusion). No functional change.

3. **`firestarter/src/proms/memory.cpp:89`** — NO CHANGE. The code is correct and the comment (if any) is already accurate per Phase 72.

**Wire-touching change required? NO.** The 0x39 host routing is already `not_implemented` (excluded from `KNOWN_PROTOCOLS`). No `messages.toml` change needed.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead |
|---------|-------------|-------------|
| SDP 3-byte unlock for flash4 writes | A new byte sequence | `FLASH_ENABLE_WRITE` already in `flash_utils.h` — reuse `flash_execute_command(FLASH_ENABLE_WRITE)` |
| AMD-compatible chip ID read for flash4 | A new ID-read function | Mirror `flash3_get_chip_id` which uses existing `FLASH_ENABLE_ID` / `FLASH_DISABLE_ID` from `flash_utils.h` |
| DQ7 polling for page write completion | A new polling loop | Existing `flash4_wait_for_page_write` is correct — just move the call-site to 256-byte boundaries |
| Recording bus stub for native tests | A new test harness | The existing `HOST_STUBS_RECORD_BUS` recording API is already compiled for `test_val_flash4` — use `clear_bus_recording()` / `bus_recording_count()` / `recorded_reg()` / `recorded_data()` |
| Non-regression check | Manual diff | `python3 tools/check_dispatch.py` + `python3 tools/diff_db.py` — run these after every firmware change to confirm no DB or dispatch regression |

---

## Common Pitfalls

### Pitfall 1: SDP unlock timing window
**What goes wrong:** `flash_util_byte_flipping` writes the 3-byte sequence using `fu_flash_flip_data`. If there's a delay between the 3rd SDP byte and the first data byte that exceeds the chip's page-load inactivity timeout (~150µs), the chip aborts the page load and the write fails silently.
**Why it happens:** Any lengthy operation (e.g., a Serial.print or delay) inserted between the SDP sequence and the first `handle->firestarter_set_data` call would trigger the timeout.
**How to avoid:** The SDP sequence and the first page-byte write must be back-to-back with no intervening delays. In the AVR at 16 MHz, the transition from `flash_util_byte_flipping` to `memory_set_data` takes ~10-20µs — well within the 150µs window.
**Warning signs:** DQ7 poll immediately returns the wrong value (no write started); first byte reads back as pre-existing content.

### Pitfall 2: Calling SDP per-byte instead of per-page
**What goes wrong:** If `flash_execute_command(FLASH_ENABLE_WRITE)` is called before EVERY byte (as `flash3_write_execute` does for AMD sector-flash), the W29C040 interprets each 3-byte sequence as starting a new page load — aborting the current load after 1 byte and starting over.
**Why it happens:** flash3's protocol is byte-by-byte (each byte is independently unlock→write→poll); flash4's protocol is batch page-load (unlock→load N bytes→poll once at end).
**How to avoid:** Call `flash_execute_command(FLASH_ENABLE_WRITE)` only at page start (`address % PAGE_SIZE == 0`), then load all bytes in the page without interruption.
**Warning signs:** Only the first byte of each page is written; all others read back as 0xFF.

### Pitfall 3: PAGE_SIZE 64 silently breaks polling
**What goes wrong:** Polling at byte 63 of a 256-byte page — the chip hasn't committed the page yet (still in load mode), so DQ7 reflects the input state of the MOST RECENT write, not a programming completion signal. The poll may appear to "pass" (if the DQ7 of the last byte happens to match the expected value) while the data wasn't actually programmed.
**Why it happens:** DQ7 polling only becomes meaningful AFTER the chip transitions from load mode to internal write mode (triggered by WE# inactivity). If the host polls while the chip is still in load mode, the result is undefined.
**How to avoid:** Use `PAGE_SIZE 256` to ensure polling fires only after the full 256-byte page boundary.

### Pitfall 4: VPP regulator enable for flash4 write
**What goes wrong:** `flash4_erase_execute` asserts `CTRL_VPP_REGULATOR_ENABLE`, activating the 12V boost regulator. The W29C040 is a 5V-only device. Applying 12V to the VPP socket line is an overvoltage condition and may damage the chip.
**Why it happens:** The erase function was written for a different chip archetype that needs external VPP.
**How to avoid:** The erase function is dead code for all 27 flash4 DB chips (no chip has `FLAG_CAN_ERASE` set via the host — confirmed by `database.py:594-597` which only sets it from `info-flags & 0x10`, and all flash4 chips have `info-flags: 0` in the DB). Document this as a latent hazard to be addressed if a future chip with `FLAG_CAN_ERASE` is added to the flash4 family. For this phase, the write path fix (SDP + PAGE_SIZE) is sufficient to make W29C040 work; the erase path is not exercised.

### Pitfall 5: write_init blank-check gating
**What goes wrong:** `flash4_write_init` calls `mem_util_blank_check` unless `FLAG_SKIP_BLANK_CHECK` is set. If the chip was not erased to all-0xFF beforehand, the blank check fails before any write byte is sent. The Phase 73 FAIL reported "Not blank, at 0x000000, v: 0x00" — the chip had prior content from a failed erase.
**Why it happens:** The dev validate-family runner uses `-b` flag (`FLAG_SKIP_BLANK_CHECK`) for the standalone write fallback. But the `write_cycle_eprom` runner enables blank-check, which fails because the VPP-erase didn't clean the chip.
**How to avoid:** The Tier-3 re-bench must ensure the chip is erased before writing. Since the flash4 erase path is dead code (no `FLAG_CAN_ERASE`), the operator must either: (a) use `firestarter write W29C040 <file> -b` which skips blank check, or (b) first program blank (all-0xFF) manually to reset the chip. The Phase 74 re-bench should use `-b` initially, then transition to a full write_cycle_eprom run once the fix is confirmed.

### Pitfall 6: vpp_mv=12000 in DB for all flash4 chips
**What goes wrong:** Developer sees `vpp_mv: 12000` in chip_database.json for W29C040 and concludes "this chip needs 12V VPP" — then adds VPP register enable to the write path.
**Why it happens:** The `vpp_mv` field in infoic.xml encodes the chip-ID read voltage (voltage applied to A9 or VPP pin to enter ID mode), NOT the programming supply. All 27 flash4 chips show `vpp_mv: 12000`. The check_dispatch.py `_FAMILY_VPP_INVARIANTS` already documents this: `configure_flash4: (0, 6000)` with a note that the 12000 value is "WP-pin voltage, not programming VPP" [VERIFIED: direct read of `check_dispatch.py:79-95`].
**How to avoid:** Never enable `CTRL_VPP_REGULATOR_ENABLE` in the flash4 write path. The existing `test_val_flash4` suite tests this at the configure phase; a new test should extend the assertion to the operation phase (write execute).

---

## Architecture Patterns

### Pattern 1: Recording-stub Tier-1 operation-phase VPP test

The existing `test_val_flash4.cpp` tests the **configure phase** (just `configure_memory` call, no `firestarter_operation_init` call). The FIX-02B SDP fix touches the **operation phase** (`flash4_write_execute`). A new test must invoke `firestarter_operation_init` and a stub `firestarter_operation_main` call to exercise the write path and assert no VPP register bits are set.

The `HOST_STUBS_RECORD_BUS` recording API is already wired. The planner needs a test like:

```cpp
void test_flash4_write_execute_no_vpp(void) {
    firestarter_handle_t h = make_handle_with_data(0x05, CMD_WRITE, ...);
    configure_memory(&h);  // sets up operation pointers
    // Manually invoke write_execute on a small buffer
    h.data_size = PAGE_SIZE;
    // ... fill h.data_buffer ...
    h.firestarter_operation_main(&h);  // executes flash4_write_execute
    // Assert no VPP bits in any CONTROL_REGISTER write during execute phase
    assert_no_vpp_in_recording("flash4 write execute must not set VPP bits");
}
```

**Important:** `flash_util_byte_flipping` (called by `flash_execute_command(FLASH_ENABLE_WRITE)`) also calls `handle->firestarter_set_control_register(handle, CTRL_READ_WRITE, 0)` — this sets `CTRL_READ_WRITE` (a non-VPP bit) in the CONTROL_REGISTER. The test must check only VPP bits (CTRL_VPP_REGULATOR_ENABLE and CTRL_VPP_P1_ENABLE), not all bits. The existing `assert_no_vpp_in_recording` helper already does this correctly [VERIFIED: `test_val_flash4.cpp:71-82`].

### Pattern 2: SDP unlock at page boundary (not byte boundary)

flash3 calls SDP per-byte:
```cpp
// flash3_write_execute (AMD sector-flash: byte-at-a-time with per-byte SDP)
for each byte:
    flash_execute_command(FLASH_ENABLE_WRITE);  // 3-byte unlock
    handle->firestarter_set_data(address, byte); // write
    flash_util_verify_operation(handle, byte);   // DQ7 poll
```

flash4 (W29C040) must call SDP per-page-start:
```cpp
// flash4_write_execute (page-EEPROM: page load with SDP at page start)
for each byte:
    if (is_page_start || is_first_byte):
        flash_execute_command(FLASH_ENABLE_WRITE);  // 3-byte SDP sequence
    handle->firestarter_set_data(address, byte);    // load into page buffer
    if (reached_page_end || is_last_byte):
        flash4_wait_for_page_write(handle, address, byte);  // DQ7 poll
```

This pattern is already used by `eeprom28c_write_execute` (AT28C-family 64-byte page EEPROM) for SDP disable followed by page load — the structure is the same, just with SDP-enable (3-byte) vs SDP-disable (6-byte).

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Unity (PlatformIO native) + pytest |
| Native config | `firestarter/platformio.ini [env:native]` |
| Quick run (firmware) | `pio test -e native` (77 tests, ~20 sec) |
| Full suite (firmware) | `pio run -e leonardo && pio test -e native` |
| Quick run (host) | `cd firestarter_app && python3 tools/check_dispatch.py && python3 tools/diff_db.py` |
| Full suite (host) | `cd firestarter_app && pytest --cov-fail-under=70` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | Notes |
|--------|----------|-----------|-------------------|-------|
| FIX-01 | `configure_sram` is not a no-op — VAL-06 = table-stakes-PASS | Tier-3 evidence (existing) | `cat firestarter_app/val-results/sram/val06-perbyte-verdict.txt \| grep 'VAL-06'` | Existing artifact; no new test needed |
| FIX-02A | `configure_flash4` with CMD_CHECK_CHIP_ID sets a non-NULL operation_main | Tier-1 native dispatch | `pio test -e native -f "*test_dispatch*"` | Add test to `test_configure_memory.cpp` |
| FIX-02B (SDP) | `flash4_write_execute` sends SDP 3-byte sequence at page boundaries | Tier-1 recording-stub | `pio test -e native -f "*test_val_flash4*"` | Add operation-phase SDP recording test |
| FIX-02B (VPP) | `flash4_write_execute` does NOT assert VPP register bits | Tier-1 VPP-bit assertion | `pio test -e native -f "*test_val_flash4*"` | Extend existing VPP-safety test to operation phase |
| FIX-02B (bench) | W29C040 write+read-back matches source SHA on Leonardo | Tier-3 HIL bench | `firestarter -p /dev/ttyACM0 dev validate-family flash4 --board leonardo --chip W29C040 --source val-results/flash4/w29c040-source.bin --output-dir val-results/flash4` | Standing bench precondition applies |
| FIX-03 | 0x39/0x35 comments are consistent across firmware and host | Static/doc assertion | `grep '0x39' firestarter/CLAUDE.md firestarter_app/firestarter/database.py firestarter_app/firestarter/ic_layout.py` | Manual review; no automated test |
| Non-regression | check_dispatch.py + diff_db.py + all native suites stay green | All tiers | `python3 firestarter_app/tools/check_dispatch.py && python3 firestarter_app/tools/diff_db.py && pio test -e native` | Must run after every firmware or host change |

### Sampling Rate
- **Per task commit:** `pio test -e native` (firmware changes) or `python3 tools/check_dispatch.py` (host changes)
- **Per wave merge:** `pio run -e leonardo && pio test -e native && pytest --cov-fail-under=70`
- **Phase gate:** Full suite green + Tier-3 re-bench PASS + flash-% recorded before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` — add `test_flash4_check_chip_id_*` tests (FIX-02A RED→GREEN)
- [ ] `firestarter/test/native/avr/test_val_flash4/test_val_flash4.cpp` — add operation-phase SDP recording + VPP-bit tests (FIX-02B RED→GREEN)
- [ ] No new test files needed — both extend existing test files in existing suites

---

## Security Domain

**FIX-01:** No firmware change — no security surface.
**FIX-02A:** Dispatch case addition — no security implications beyond the existing VPP-safety invariant.
**FIX-02B (SDP fix):** The SDP sequence writes to specific flash addresses (0x5555, 0x2AAA). These are command register addresses that are only meaningful to the flash device — they do not expose any host or serial attack surface.
**VPP safety invariant (critical):** The fix MUST NOT enable `CTRL_VPP_REGULATOR_ENABLE`. Violation would assert 12V+ on a 5V-only chip, with risk of hardware damage. Proven safe by the existing Tier-1 VPP-bit assertion test (configure phase) + new operation-phase assertion.
**FIX-03:** Comment changes only — no security surface.

### Applicable ASVS Categories

| ASVS Category | Applies | Control |
|---------------|---------|---------|
| V5 Input Validation | Indirect | `handle->chip_id` check in flash4_check_chip_id_execute; handle struct already validated at parse time |
| Hardware Safety (non-ASVS) | YES | VPP register bit assertion tests are the control; must stay green on every build |

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| PlatformIO `pio` | Firmware build + native tests | ✓ | (system install) | — |
| `pio run -e leonardo` | Flash budget check | ✓ | Leonardo 88.9% [VERIFIED] | — |
| `pio test -e native` | Tier-1 test suite | ✓ | 77/77 green [VERIFIED] | — |
| `python3 tools/check_dispatch.py` | Non-regression gate | ✓ | PASS [VERIFIED] | — |
| `python3 tools/diff_db.py` | Non-regression gate | ✓ | PASS [VERIFIED] | — |
| Leonardo + Rev 2.0 + W29C040 chip | Tier-3 FIX-02B re-bench | Assumed available (used in Phase 73 VAL-04) | — | Cannot re-bench without hardware |
| R1 calibration | Tier-3 precondition | ✓ R1=270000 in Phase 73 [VERIFIED from 73-03-SUMMARY] | — | Recalibrate if needed |

---

## State of the Art

| Old Approach | Current Approach | Impact |
|--------------|-----------------|--------|
| `flash4_write_execute` bare byte writes, no SDP | Must add `flash_execute_command(FLASH_ENABLE_WRITE)` at page start | W29C040 writes silently fail without this |
| `PAGE_SIZE 64` in flash_type_4.cpp | Must be `PAGE_SIZE 256` for W29C040 family | Polling fires at wrong boundary, data never commits |
| `flash4_erase_execute` asserts 12V VPP | Latent hazard for 5V-only flash4 chips; dead code path for all 27 DB chips | Not fixed this phase (erase path never activated by DB chips) |
| No `CMD_CHECK_CHIP_ID` in configure_flash4 | Mirror from configure_flash3 | Chip-ID verification unavailable for flash4 |

**Deprecated/outdated:**
- `PAGE_SIZE 64` in `flash_type_4.cpp`: replaced by 256. The eeprom_28c's PAGE_SIZE=64 remains correct (AT28C256 genuine 64-byte page EEPROM, different algorithm 0x0D).

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | AT29C256 has 64-byte pages; AT29C512 has 128-byte pages; AT29C010A has 128-byte pages (page size scales with chip capacity) | W29C040 Datasheet Analysis — page size variation | Using PAGE_SIZE=256 for all flash4 chips would span multiple physical pages for smaller chips; functionally correct but less efficient |
| A2 | W29C040 page write fires automatically on WE# inactivity timeout (~150µs) after SDP sequence; host doesn't need to send a separate "commit" command | Architecture Patterns — SDP unlock at page boundary | If a separate commit command is needed, the write algorithm needs additional bytes after the page load |
| A3 | `flash4_erase_execute` VPP hazard is a dead code path (FLAG_CAN_ERASE never set for flash4 DB chips) | Common Pitfalls — erase path | If a future chip addition sets FLAG_CAN_ERASE for a flash4 chip, the broken erase would fire and could damage the chip; document as tech debt |
| A4 | AE29F1008/2008/4008 (ASD brand) also use the W29C040-style page write protocol (SDP + 256-byte page for the 4008); no physical chip to verify | W29C040 Datasheet Analysis — chip family scope | ASD chips may have different page sizes; the SDP fix is universal but PAGE_SIZE may need per-chip adjustment for future validation |

---

## Open Questions

1. **Page size selection for the full flash4 family**
   - What we know: W29C040 = 256 bytes (confirmed). AT29C256 = 64 bytes [ASSUMED from search results]. SST29EE010 = 128 bytes [CITED: SST29EE020 datasheet via alldatasheet.com]. chip_database.json has no `page_size` field.
   - What's unclear: Whether using PAGE_SIZE=256 for all flash4 chips will correctly handle AT29C256 (64-byte page) at the bench. The auto-commit (WE# inactivity timer) means the chip commits every 64 bytes automatically — the firmware poll at byte 255 just waits for the last-committed page. Likely correct, but unverified.
   - Recommendation: Use PAGE_SIZE=256 for this phase (W29C040 fix is the priority). Document the AT29C256/AT29C512 smaller-page uncertainty as a follow-on validation item if those chips become bench-testable.

2. **flash4_erase_execute VPP hazard — fix or document?**
   - What we know: The erase path (in `flash4_write_init`) only fires when `FLAG_CAN_ERASE` is set. No flash4 DB chip has this set. The current VPP-based erase is wrong for W29C040 but the path is never activated.
   - What's unclear: Should Phase 74 fix the erase to use `flash_execute_command(FLASH_ERASE)` (AMD 6-byte erase) and remove the VPP assertions, or just document the latent hazard?
   - Recommendation: Document as tech debt. The SDP write fix is the primary goal. A full flash4_erase_execute rewrite adds flash bytes and complexity; the path is dead for all 27 current chips. If fix is pursued, it requires a VPP dry-run by the operator — this could block the phase if hardware is unavailable.

---

## Sources

### Primary (HIGH confidence)
- `firestarter/src/proms/flash_type_4.cpp` [VERIFIED: direct read] — defect locations confirmed
- `firestarter/src/proms/flash_type_3.cpp` [VERIFIED: direct read] — Defect A mirror source
- `firestarter/src/proms/memory.cpp:89` [VERIFIED: direct read] — 0x39 dispatch arm
- `firestarter/include/flash_utils.h` [VERIFIED: direct read] — `FLASH_ENABLE_WRITE` = SDP unlock sequence
- `firestarter/src/proms/flash_utils.cpp` [VERIFIED: direct read] — no VPP bits in `flash_util_byte_flipping`
- `firestarter/src/proms/eeprom_28c.cpp` [VERIFIED: direct read] — page write pattern reference
- `firestarter/test/native/avr/test_val_flash4/test_val_flash4.cpp` [VERIFIED: direct read] — existing test suite
- `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` [VERIFIED: direct read]
- `firestarter_app/val-results/flash4/validation-matrix.json` [VERIFIED: direct read] — FAIL evidence
- `.planning/phases/73-.../73-03-SUMMARY.md` [VERIFIED: direct read] — W29C040 FAIL details
- `.planning/phases/73-.../73-VERIFICATION.md` [VERIFIED: direct read] — SC#4 FIX-01 closure
- `firestarter_app/firestarter/database.py:55-63` [VERIFIED: direct read] — 0x35/0x39 host comments
- `firestarter_app/firestarter/ic_layout.py:228-229` [VERIFIED: direct read] — 0x35/0x39 host comments
- `firestarter_app/tools/build_db.py:128-148` [VERIFIED: direct read] — KNOWN_PROTOCOLS without 0x35/0x39
- `firestarter_app/tools/check_dispatch.py` [VERIFIED: direct run, PASS 744 chips]
- `firestarter_app/tools/diff_db.py` [VERIFIED: direct run, PASS 0 changes]
- `pio test -e native` [VERIFIED: direct run, 77/77 green]
- `pio run -e leonardo` [VERIFIED: direct run, 88.9% flash]

### Secondary (MEDIUM confidence)
- W29C040 Scribd datasheet overview [CITED: scribd.com/document/672465513/w29c040-1] — 256-byte pages, 5V-only, internal VPP, 5ms write cycle
- SST29EE020 datasheet via alldatasheet.com [CITED: alldatasheet.com/html-pdf/46495/SST/SST29EE020] — 128-byte page, DQ7/toggle bit polling, 5V-only
- Multiple web searches confirming SDP 3-byte sequence = `{0x5555,0xAA},{0x2AAA,0x55},{0x5555,0xA0}` matches `FLASH_ENABLE_WRITE`

### Tertiary (LOW confidence — marked ASSUMED)
- AT29C256 = 64-byte page, AT29C512 = 128-byte page (from search result excerpts; not confirmed by direct datasheet read)
- ASD AE29F series page write protocol compatibility (inference from algorithm family assignment)
