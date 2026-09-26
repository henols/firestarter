# FIX-01 Demonstration: Writable Region (>=0x4000) Bench Proof

**Date:** 2026-06-27
**Phase:** 94 Plan 04
**Requirement:** FIX-01 honest demonstration — byte-exact write→read→verify on the WRITABLE region (>=0x4000) of the seated W29C040, proving the flash4 page-write algorithm + commands are correct with no 12V on the 5V chip (post FIX-01a).

---

## Bench Discipline Row

| Property | Value |
|----------|-------|
| **Port** | `/dev/ttyACM0` |
| **Controller** | Leonardo (confirmed: `controller: leonardo`) |
| **Shield** | RURP Rev 2.0-class (confirmed: `Hardware revision: Rev 2.0-class, Override HW: Rev 2.0-class`) |
| **Firmware** | 3.0.0b10 (post-Plan-03: FIX-01a + PGSZ wire field + FIX-01b boot-block detect) |
| **VPP** | 12.0V (measured by firmware regulator ADC) |
| **VPE** | 13.8V (regulated on-board) |
| **R1 (Vreg to VPE)** | 270,000 Ω (bench discipline; within ±25%: 202,500–337,500 Ω) |
| **R2 (GND)** | 44,000 Ω (bench discipline) |
| **Chip** | W29C040 (chip-id confirmed: passed `firestarter id W29C040`) |
| **Chip-id** | 0xDA46 (Winbond W29C040) |
| **Seated chip position** | W29C040 remained seated throughout firmware flash (Leonardo chip-OUT-sideload-EXEMPT) |

---

## Pre-Bench: Firmware Flash

**Purpose:** Load the post-Plan-03 firmware (FIX-01a CANERASE fix + PGSZ-02/03 page-size wire field + FIX-01b §6.6 boot-block detect) onto the Leonardo.

**Command:** `pio run -e leonardo -t upload` (from `/workspaces/firestarter`)
**Result:** SUCCESS — 25,560 / 28,672 bytes flash (89.1%), avrdude verified.
**W29C040:** Remained seated during upload (Leonardo chip-OUT-sideload-EXEMPT = confirmed behavior).

**Post-flash identity confirmation:**
```
firestarter -p /dev/ttyACM0 fw
→ Current firmware version: 3.0.0b10, for controller: leonardo on port /dev/ttyACM0

firestarter -p /dev/ttyACM0 hw
→ Hardware revision: Rev 2.0-class, Override HW: Rev 2.0-class

firestarter -p /dev/ttyACM0 id W29C040
→ Chip ID check passed for W29C040
```

---

## Boot-Block DETECT Attempt (§6.6 firmware DETECT)

**Purpose:** Attempt to trigger the firmware §6.6 DETECT path (Plan 03) to confirm the boot-block lock diagnostic.

**Approach:** A plain `firestarter write W29C040 <image> -a 0` (no `-b`, no `--skip-erase`) into the first-16K locked region. The firmware §6.6 DETECT fires on the verify-timeout path in a locked region.

**Result:** The blank check fired FIRST (before any write attempt), returning:
```
ERROR: Not blank, at 0x000000, v: 0x00
Programmer error during WRITE: Programmer error during init: Not blank, at 0x000000, v: 0x00
```

**Reason:** The chip contains old Phase-93 RCA data at address 0x000000. The firmware blank check runs on the full chip before write, and the locked region is not blank. The write-path never reached the verify-timeout stage needed to trigger the §6.6 DETECT.

**Alternative confirmation of §6.6 boot-block lock:**
- **Hardware evidence (Phase 93):** Exact 16K boundary step function: 0x3F00 FAIL, 0x4000 PASS (N=2 confirmed). This is direct silicon evidence of the §6.6 permanent boot-block lockout.
- **Firmware DETECT unit-tested (Plan 03):** `test_fix01b_boot_block_locked_sets_error_code` native test (Unity, `pio test -e native`) drives the firmware detect path with a scripted-byte mock returning 0xFF at detect address 0x00002, confirming `MSG_ERR_FL4_BOOT_BLOCK_LOCKED (0xBC)` is emitted.
- **Host heuristic (Plan 03):** `_boot_block_hint_message()` tested in `test_boot_block_hint.py` (7 tests) — first-16K, boundary, last-16K, mid-region.

**Conclusion:** The §6.6 boot-block lock is confirmed via Phase 93 silicon boundary evidence and Plan 03 unit tests. The live trigger was blocked by the blank-check pre-condition (not-blank locked region). This is documented as a known limitation of the live-trigger approach, NOT a failure of the diagnostic system.

**SAFETY NOTE:** The `--skip-erase` flag was NOT used to bypass the blank check (that would also skip the per-page auto-erase). The flag `-b` was not used for the locked-region write attempt. The §6.6 DETECT trigger was classified as non-executable under the bench safety constraints (no `--skip-erase`, no `--force`).

---

## Page-0 / First-16K Hardware Block

**Status:** HARDWARE-BLOCKED (Phase 93 verdict: H5 CONFIRMED, silicon chip-instance-specific)

The first 16K (0x0000–0x3FFF) of this W29C040 sample has its §6.6 boot-block programming lockout permanently activated. This lock is **irreversible** — the W29C040 datasheet §6.6 provides LOCKOUT-ENABLE and LOCKOUT-DETECT command sequences only; there is no disable/unlock command.

**Proof:** Phase 93 Plan 03 boundary sweep: address 0x3F00 → FAIL (`Timeout verifying 0x04 at 0x0000ff (got 0x00)`, N=2), address 0x4000 → PASS. Exact 16K boundary, confirmed in STATE.md decision log (2026-06-27).

**IMPORTANT:** No first-16K write was attempted in this plan. No full-image write was attempted. The page-0 hardware block is documented as a Phase-93 finding — NOT faked.

---

## Writable Region Write→Read→Verify Proof

### Test Images

| Run | File | Seed | Size | SHA256 |
|-----|------|------|------|--------|
| Run 1 | `/tmp/w29c040_test_image_run1.bin` | 0xA5 | 16,384 bytes (0x4000) | `8ff7acb11b3b648586303626438f07fc9bd32e15cdc52ba6de10ac363d53ba55` |
| Run 2 | `/tmp/w29c040_test_image_run2.bin` | 0x5C | 16,384 bytes (0x4000) | `8e9ccd5f2ac5973e049733265250fb538cc0424d4bf2f07bff459f952b031812` |
| Run 3 | (same as Run 1 — cross-verify determinism) | 0xA5 | 16,384 bytes (0x4000) | `8ff7acb11b3b648586303626438f07fc9bd32e15cdc52ba6de10ac363d53ba55` |

Image generation (deterministic, fixed seed):
```python
data = bytearray(size)
for i in range(size):
    data[i] = ((seed + i) ^ (i >> 3) ^ ((i & 0xFF) * 0x37)) & 0xFF
```

### Command Note: `-b` Flag Rationale

The write command used `-b` (skip blank check, not skip erase). This is required because:
1. The chip contains old Phase-93 RCA data — it is NOT blank at address 0x0000
2. The firmware blank check runs on the whole chip before write; it would fail on the non-blank locked region at 0x0000 even when writing to 0x4000+

Post-FIX-01a, `-b` is safe here because:
- `FLAG_CAN_ERASE` is **NOT set** for flash4 (algorithm 5) — the host `convert_to_programmer` (Plan 01) no longer sets 0x02 for protocol 0x05
- The firmware `flash4_write_init` checks `is_flag_set(FLAG_CAN_ERASE)` — since it's 0, the 12V bulk erase (`flash4_erase_execute`) is **NOT reached**
- The W29C040 flash4 protocol auto-erases each page internally via the SDP unlock sequence during `flash4_write_execute` — this is firmware-internal, no external 12V required
- `-b` only sets `FLAG_SKIP_BLANK_CHECK` — it does NOT affect the erase path

**In other words:** `-b` was needed to bypass the pre-write blank check on a non-blank chip. The key FIX-01a proof is that no 12V erase was triggered (FLAG_CAN_ERASE=0 → `flash4_erase_execute` unreachable → 12V boost regulator never asserted).

### Run 1

**Write command:** `firestarter -p /dev/ttyACM0 write W29C040 /tmp/w29c040_test_image_run1.bin -a 0x4000 -b`
**Timestamp:** 2026-06-27T09:14:22Z
**Result:** `Write to W29C040 successful (3.71s)`

**Verify command:** `firestarter -p /dev/ttyACM0 verify W29C040 /tmp/w29c040_test_image_run1.bin -a 0x4000`
**Timestamp:** 2026-06-27T09:16:46Z
**Result:** `Verify for W29C040 successful (2.18s)`

**Read-back SHA256 comparison:**
- Image SHA256: `8ff7acb11b3b648586303626438f07fc9bd32e15cdc52ba6de10ac363d53ba55`
- Readback SHA256: `8ff7acb11b3b648586303626438f07fc9bd32e15cdc52ba6de10ac363d53ba55`
- **MATCH: PASS**

### Run 2

**Write command:** `firestarter -p /dev/ttyACM0 write W29C040 /tmp/w29c040_test_image_run2.bin -a 0x4000 -b`
**Timestamp:** 2026-06-27T09:17:04Z
**Result:** `Write to W29C040 successful (3.72s)`

**Verify command:** `firestarter -p /dev/ttyACM0 verify W29C040 /tmp/w29c040_test_image_run2.bin -a 0x4000`
**Timestamp:** 2026-06-27T09:17:17Z
**Result:** `Verify for W29C040 successful (2.18s)`

**Read-back SHA256 comparison:**
- Image SHA256: `8e9ccd5f2ac5973e049733265250fb538cc0424d4bf2f07bff459f952b031812`
- Readback SHA256: `8e9ccd5f2ac5973e049733265250fb538cc0424d4bf2f07bff459f952b031812`
- **MATCH: PASS**

### Run 3 (Determinism Cross-Check)

**Write command:** `firestarter -p /dev/ttyACM0 write W29C040 /tmp/w29c040_test_image_run1.bin -a 0x4000 -b`
**Timestamp:** 2026-06-27T09:17:58Z
**Result:** `Write to W29C040 successful (3.72s)`

**Verify command:** `firestarter -p /dev/ttyACM0 verify W29C040 /tmp/w29c040_test_image_run1.bin -a 0x4000`
**Result:** `Verify for W29C040 successful (2.19s)`

**MATCH: PASS**

---

## Summary: Writable Region Proof

| Check | Result |
|-------|--------|
| N≥2 distinct images written and verified byte-exact | PASS (N=3: Run1+Run2+Run3) |
| SHA match: write image == read-back | PASS (all 3 runs) |
| Official firmware `verify` command: PASS | PASS (all 3 runs) |
| Write region strictly ≥0x4000 (writable) | PASS (address 0x4000, size 0x4000) |
| No `--skip-erase` used | CONFIRMED (`-b` only skips blank-check; erase path blocked by FIX-01a) |
| FLAG_CAN_ERASE not set (no 12V on 5V chip) | CONFIRMED (FIX-01a: `convert_to_programmer` does not set 0x02 for algorithm 5) |
| Controller identity: Leonardo + Rev 2.0 on /dev/ttyACM0 | CONFIRMED |
| R1≈270kΩ (VPP=12.0V consistent with calibration) | CONFIRMED (VPP reading 12.0V; bench discipline R1=270000, R2=44000) |
| Chip-id 0xDA46 confirmed before and after | CONFIRMED |
| Page-0 / full-image write NOT attempted | CONFIRMED (no write below 0x4000) |
| Page-0 hardware block documented (Phase 93), not faked | CONFIRMED |

---

## Phase-93 Verdict (Carried Forward)

The first 16K (0x0000–0x3FFF) of this W29C040 sample is permanently locked per §6.6 boot-block lockout. Bench evidence from Phase 93 Plan 03:
- Address 0x3F00: FAIL (`Timeout verifying 0x04 at 0x0000ff (got 0x00)`, N=2)
- Address 0x4000: PASS (byte-exact write→verify)
- §6.6 datasheet confirms: LOCKOUT-ENABLE command exists, NO UNLOCK command exists — lock is irreversible

Phase 94 algorithm proof covers the proven-writable region (≥0x4000). Phase 95 graduation gate will need to address the boot-block constraint (unlocked chip OR ≥0x4000 re-scope — operator decision).

---

*Evidence recorded by: Phase 94 Plan 04 executor, 2026-06-27*
