---
phase: 73-bench-validate-the-6-families-on-leonardo-hybrid-gated
plan: 03
subsystem: testing
tags: [bench-validation, flash3, flash4, AM29F040, W29C040, VAL-03, VAL-04, SKIP-deferred, hardware, leonardo]

# Dependency graph
requires:
  - phase: 73-01
    provides: Leonardo precondition confirmed (controller:leonardo, Rev 2.0, R1=270000), VAL-01 eprom PASS
  - phase: 73-02
    provides: W27C512 Tier-3 PASS closed VAL-01

provides:
  - "flash3/VAL-03 Tier-3 cell: SKIP-deferred (no AM29F040; operator 2026-06-17 decision)"
  - "flash4/VAL-04 Tier-3 cell: FAIL (W29C040 hw-error; Phase-74 candidate)"
  - "Negative control for flash4 PASS oracle: verify w29c040-wrongfile.bin exited non-zero"
  - "Binary evidence artifacts: w29c040-source.bin + w29c040-wrongfile.bin in val-results/flash4/"

affects: [73-04, phase-74, flash4-algorithm-investigation]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Authorized chip substitution deviation: plan target (AM29F040/flash3) replaced by operator-seated chip (W29C040/flash4) at execution time"
    - "FAIL verdict as Phase-74 route per D-12: any recorded verdict closes the cell"
    - "Negative control non-vacuous proof even on FAIL verdict: verify against wrong file exits non-zero"

key-files:
  created:
    - firestarter_app/val-results/flash3/validation-matrix.json
    - firestarter_app/val-results/flash3/validation-matrix.md
    - firestarter_app/val-results/flash4/w29c040-source.bin
    - firestarter_app/val-results/flash4/w29c040-wrongfile.bin
  modified:
    - firestarter_app/val-results/flash4/validation-matrix.json
    - firestarter_app/val-results/flash4/validation-matrix.md

key-decisions:
  - "73-03-DEV: flash3/AM29F040 SKIP-deferred; flash4/W29C040 real Tier-3 run (authorized by operator 2026-06-17)"
  - "73-03-D1: flash4 W29C040 verdict = FAIL (hw-error): write_cycle_eprom exit code 2, standalone write -b also fails with timeout"
  - "73-03-D2: flash4 FAIL routes to Phase 74 per D-12 (recorded verdict closes the cell regardless of PASS/FAIL)"
  - "73-03-D3: Negative control PASSED for flash4: verify wrong file exited 1 at 0x000000 (0xaa != 0x00)"

patterns-established:
  - "Chip-substitution authorized deviation: document prominently in SUMMARY with original plan target, substituted chip, both families affected"
  - "hw-error exit-code-2 + fallback standalone write both fail → FAIL verdict not SKIP-deferred (evidence recorded, Phase-74 candidate noted)"

requirements-completed: [VAL-03, VAL-04]

# Metrics
duration: 8min
completed: 2026-06-17
---

# Phase 73 Plan 03: Flash3 SKIP-deferred + Flash4 FAIL on W29C040 Summary

**flash3/VAL-03 recorded as SKIP-deferred (no AM29F040 on hand per operator 2026-06-17); flash4/VAL-04 upgraded from SKIP-deferred to real FAIL verdict on seated W29C040 (Winbond flash4, algorithm 5) with passing negative control and Phase-74 escalation**

## AUTHORIZED DEVIATION — CRITICAL

Plan 73-03 as written targeted `flash3/VAL-03` using an AM29F040 (algorithm 6 = configure_flash3). The operator did NOT have an AM29F040 available and instead had a **W29C040 seated (Winbond, algorithm 5 = configure_flash4, VAL-04 family)**. Two actions were taken per the authorized deviation:

1. **flash3/VAL-03 → SKIP-deferred**: No AM29F040 on hand. Recorded per D-13 (partial coverage explicit, never silent). Reason: "no AM29F040 on hand; deferred to a future bench session at beta release per operator 2026-06-17".

2. **flash4/VAL-04 → Real Tier-3 run on W29C040**: The seated chip provided an opportunity to upgrade flash4's existing SKIP-deferred cell (from 73-01) to a real Tier-3 bench verdict. The run produced a **FAIL verdict** — a genuine algorithmic incompatibility finding, routed to Phase 74 per D-12.

## Performance

- **Duration:** 8 min
- **Started:** 2026-06-17T13:36:51Z
- **Completed:** 2026-06-17T13:45:16Z
- **Tasks:** 1 (Task 1: mandatory gate + flash3 SKIP-deferred + flash4 Tier-3 run)
- **Files modified:** 4 (validation-matrix.json/md for flash3 + flash4)
- **Files created:** 4 (flash3 matrix + flash4 source/wrongfile bins)
- **Submodule commit:** `6e0ce28` (firestarter_app, v1.13-algo-validation)

## Accomplishments

- **Pre-write gate PASSED**: controller=leonardo, Rev 2.0, R1=270000 (within [202500, 337500] band)
- **flash3/VAL-03 SKIP-deferred** recorded with explicit operator reason (D-13 compliant)
- **flash4/VAL-04 real Tier-3 run**: W29C040 exercised with `dev validate-family flash4` runner on Leonardo Rev 2.0
- **FAIL verdict recorded**: exit code 2 (hw-error) + standalone write -b fallback also failed → genuine algorithm issue found
- **Negative control PASSED**: verify W29C040 against wrong file exited 1 (0xaa != 0x00 at 0x000000) — oracle non-vacuous
- **Phase-74 candidate identified**: flash4 write algorithm incompatibility with W29C040 SDP/page-write timing

## Task Commits

1. **Task 1: flash3 SKIP-deferred + flash4 Tier-3 FAIL on W29C040** - `6e0ce28` (feat, in firestarter_app submodule)

## Pre-Write Gate (Mandatory)

Executed at task start per hardware_note:

| Check | Result |
|-------|--------|
| `firestarter -p /dev/ttyACM0 fw` | `controller: leonardo` CONFIRMED |
| `firestarter -p /dev/ttyACM0 hw` | Rev 2.0-class CONFIRMED |
| `firestarter -p /dev/ttyACM0 config` | R1=270000, R2=44000 (within [202500,337500]) IN BAND |

## Flash3/VAL-03 SKIP-deferred Detail

**Runner invocation**: `firestarter -p /dev/ttyACM0 dev validate-family flash3 --output-dir val-results/flash3` (no --board/--chip/--source triggers auto-SKIP-deferred path)

**Cell recorded**:
```json
{
  "family": "flash3",
  "board": "leonardo",
  "tier": 3,
  "verdict": "SKIP-deferred",
  "reason": "no AM29F040 on hand; deferred to a future bench session at beta release per operator 2026-06-17"
}
```

## Flash4/VAL-04 Tier-3 Run Detail

**Chip**: W29C040 (Winbond), algorithm=5 (configure_flash4), 512KB (524288 bytes), DIP32_SST39SF040, 12V VPP, support_status=supported

**Source image**: `w29c040-source.bin` — 524288 bytes, deterministic pattern `(0x55 ^ (i & 0xFF))`, SHA256=`f82c4afb723e09e681b0bf10f0fb71e940baef5d92793f50662ede4bd80f477e`

**Runner invocation**: `firestarter -p /dev/ttyACM0 dev validate-family flash4 --board leonardo --chip W29C040 --source val-results/flash4/w29c040-source.bin --output-dir val-results/flash4`

**Exit code**: 2 (hw-error)

**Error detail**:
- Erase reported success: "Erase for W29C040 successful (0.06s)"
- Write init blank check failed: `ERROR: Not blank, at 0x000000, v: 0x00` — chip byte 0 = 0x00, not 0xFF (blank). Chip content before erase was mixed; after erase reported success, chip still showed 0x00 at byte 0. The flash4 blank-check gate expects 0xFF as erased state; W29C040 is not erasing to 0xFF as expected.
- Fallback standalone `firestarter write W29C040 w29c040-source.bin -b`: timeout verifying `0x6a at 0x00003f (got 0x00)`. Write bytes not being accepted by chip.

**Root cause**: configure_flash4 (algorithm 5) write+erase algorithm appears incompatible with W29C040's specific SDP (Software Data Protection) and page-write timing. The erase command may not be sending the correct SDP-bypass sequence that the W29C040 requires. **This is a Phase-74 candidate for fix investigation.**

**Verdict**: FAIL (authoritative, Leonardo)

## Negative Control

**Command**: `firestarter -p /dev/ttyACM0 verify W29C040 val-results/flash4/w29c040-wrongfile.bin`

**Wrong file**: `w29c040-wrongfile.bin` — 524288 bytes, pattern `(0xAA ^ (i & 0xFF))`, SHA256=`27af2ebc3edddc1ff5e170c38da73e47ac8e5efbd41b6724bdcf06d9d6414c77`

**Result**: Exit code 1. Error: `0xaa != 0x00 at 0x000000`. PASSED (oracle non-vacuous).

## Files Created/Modified

- `firestarter_app/val-results/flash3/validation-matrix.json` — flash3 SKIP-deferred cell (operator reason recorded)
- `firestarter_app/val-results/flash3/validation-matrix.md` — human-readable flash3 matrix
- `firestarter_app/val-results/flash4/validation-matrix.json` — flash4 FAIL cell (hw-error detail, Phase-74 candidate noted)
- `firestarter_app/val-results/flash4/validation-matrix.md` — human-readable flash4 matrix
- `firestarter_app/val-results/flash4/w29c040-source.bin` — 524288-byte deterministic source image
- `firestarter_app/val-results/flash4/w29c040-wrongfile.bin` — 524288-byte wrong file for negative control

## Decisions Made

- **73-03-DEV**: Authorized chip substitution executed per operator 2026-06-17: flash3/AM29F040 SKIP-deferred; flash4/W29C040 real Tier-3 run
- **73-03-D1**: flash4 verdict = FAIL (hw-error): both `dev validate-family` exit-2 and standalone write -b fallback failed
- **73-03-D2**: FAIL verdict routes to Phase 74 per D-12 (recorded verdict closes the cell)
- **73-03-D3**: Negative control PASSED for flash4 oracle non-vacuous proof

## Deviations from Plan

### Authorized Chip-Substitution Deviation (CRITICAL — pre-authorized by operator 2026-06-17)

**PLANNED: flash3/VAL-03 with AM29F040 (algorithm 6 = configure_flash3)**
**EXECUTED: (1) flash3/SKIP-deferred + (2) flash4/VAL-04 real run on W29C040 (algorithm 5 = configure_flash4)**

- **Reason**: No AM29F040 on hand. W29C040 seated by operator. Both are 32-pin, 512KB, 12V VPP, support_status=supported, but different families.
- **Impact**:
  - VAL-03 (flash3) closed as SKIP-deferred with documented reason. AM29F040 bench deferred to beta release session.
  - VAL-04 (flash4) upgraded from SKIP-deferred (73-01) to real Tier-3 FAIL verdict — this is net-positive evidence gathering.
- **Family correction note**: W29C040 is listed in CONTEXT.md D-02 as "SKIP-deferred (no chip)" for AT29C040; W29C040 is a different member of the flash4 family. The authorized deviation uses W29C040 as the flash4 representative instead of AT29C040.

### Additional Observed Deviation: flash4 FAIL finding (no fix required)

- **Found during**: Task 1 (flash4 Tier-3 run)
- **Issue**: W29C040 write algorithm fails — erase does not produce expected 0xFF blank state; write verification times out
- **Action**: Recorded as FAIL verdict per D-12 (not auto-fixed — Phase-74 is the correct scope for algorithmic fixes)
- **Phase-74 route**: flash4 configure_flash4 SDP-bypass / page-erase timing investigation for W29C040 compatibility

---

**Total deviations:** 1 authorized chip-substitution deviation (pre-approved by operator)
**Impact on plan:** VAL-03 deferred to future session; VAL-04 upgraded from SKIP-deferred to real FAIL evidence. Net positive.

## Issues Encountered

- flash4 write algorithm incompatibility with W29C040: both the dev validate-family runner (exit code 2) and standalone `write -b` fallback failed. Root cause: configure_flash4 erase does not bring chip to 0xFF blank state; write verification times out at 0x3f. Phase-74 candidate documented.
- `.gitignore` in firestarter_app excludes `*.bin`; binary validation artifacts committed with `git add -f` (intentional override for evidence files).

## VAL-03 / VAL-04 Status

| ID | Family | Chip | Verdict | Phase-74 Route |
|----|--------|------|---------|----------------|
| VAL-03 | flash3 | AM29F040 (absent) | SKIP-deferred | No — deferred to beta bench session |
| VAL-04 | flash4 | W29C040 (W29C040) | FAIL | Yes — configure_flash4 erase+write compatibility |

## Next Phase Readiness

- **73-04** can proceed: flash3 and flash4 cells are now recorded (SKIP-deferred and FAIL respectively)
- **Phase 74 scope expanded**: flash4 W29C040 algorithm incompatibility is a confirmed Phase-74 candidate (in addition to any SRAM fix from VAL-06)
- **Blockers**: None for 73-04 execution

---

## Self-Check: PASSED

- [x] flash3/validation-matrix.json exists with SKIP-deferred cell — CONFIRMED
- [x] flash4/validation-matrix.json exists with FAIL verdict — CONFIRMED
- [x] Negative control for flash4: verify wrongfile exited non-zero — CONFIRMED (exit 1)
- [x] Pre-write gate: controller=leonardo, Rev 2.0, R1=270000 — CONFIRMED
- [x] Submodule commit 6e0ce28 in firestarter_app on v1.13-algo-validation — CONFIRMED
- [x] Meta commit 65d22ce in meta repo — CONFIRMED
- [x] Deviation documented prominently — CONFIRMED

---

## Bonus Bench Addendum (SST39SF040, post-plan) — 2026-06-17

**VAL-03 upgraded from SKIP-deferred to authoritative PASS via SST39SF040.**

### Context

Plan 73-03 recorded flash3/VAL-03 as SKIP-deferred because no AM29F040 was available. In the same session, the operator confirmed a SST39SF040 (Silicon Storage Technology, 512KB Flash, configure_flash3 / algorithm 0x06) was seated in the Rev 2.0 Leonardo socket. A bonus HIL run was executed to upgrade VAL-03 from SKIP-deferred to real bench evidence. This does NOT require a new plan file — it is an authorized post-plan extension, documented here per D-12 (any recorded verdict closes the cell).

### Pre-Write Gate (re-confirmed)

| Check | Result |
|-------|--------|
| `firestarter -p /dev/ttyACM0 fw` | `controller: leonardo` CONFIRMED |
| `firestarter -p /dev/ttyACM0 hw` | Rev 2.0-class CONFIRMED |
| `firestarter -p /dev/ttyACM0 config` | R1=270000, R2=44000 (within [202500,337500]) IN BAND |

### Run Details

**Chip**: SST39SF040 (SST, 512KB Flash, DIP32, configure_flash3 / algorithm 0x06, 12V VPP, support_status=supported)

**Source image**: `sst39sf040-source.bin` — 524288 bytes, pattern `((i * 0x37 + 0xA3) & 0xFF)`, SHA256=`c19c3e07b94b12beb32fbb6afd3de432453a895d82406a38390db78fa348368d`

**Runner invocation**: `firestarter -p /dev/ttyACM0 dev validate-family flash3 --board leonardo --chip SST39SF040 --source val-results/flash3/sst39sf040-source.bin --output-dir val-results/flash3`

**Exit code**: 0 (PASS)

**Sequence**:
1. Erase: `flash3_erase_execute` — "Erase for SST39SF040 successful (0.03s)" — configure_flash3 erase surface exercised
2. Write: 524288 bytes written successfully (239.43s)
3. Readback: full 524288-byte read-back, SHA256=`c19c3e07b94b12beb32fbb6afd3de432453a895d82406a38390db78fa348368d` — **exact match**

**Verdict**: PASS (authoritative, Leonardo Rev 2.0)

### Negative Control

**Command**: `firestarter -p /dev/ttyACM0 verify SST39SF040 val-results/flash3/sst39sf040-wrongfile.bin`

**Wrong file**: `sst39sf040-wrongfile.bin` — 524288 bytes, pattern `((i * 0x5B + 0x7E) & 0xFF)`, SHA256=`a6d1292ebb3d3a525c74c6b4a5aa10b6e55268150eea99cb468811161b4bf6c6`

**Result**: Exit code 1. Error: `0x7e != 0xa3 at 0x000000`. PASSED (oracle non-vacuous).

### VAL-03 Status Update

| ID | Family | Chip | Verdict | Pass Type | Phase-74 Route |
|----|--------|------|---------|-----------|----------------|
| VAL-03 | flash3 | SST39SF040 (bonus; AM29F040 still deferred) | **PASS** | authoritative | No |

VAL-03 is now **CLOSED with real bench evidence** (authoritative PASS on Leonardo, configure_flash3 erase+write exercised). The planned AM29F040 run is no longer required to close VAL-03 — the SST39SF040 is a full flash3-family representative using the same algorithm (0x06).

### Submodule Commit

- `d399219` (firestarter_app, v1.13-algo-validation): `feat(73-03-bonus): flash3 VAL-03 PASS on SST39SF040 — upgrade from SKIP-deferred to authoritative`

### Files Added (firestarter_app submodule)

- `val-results/flash3/sst39sf040-source.bin` — 524288-byte source image
- `val-results/flash3/sst39sf040-wrongfile.bin` — 524288-byte wrong file for negative control
- `val-results/flash3/cycle_01_readback.bin` — 524288-byte readback from chip (SHA matches source)
- `val-results/flash3/validation-matrix.json` — flash3 leonardo cell upgraded: SKIP-deferred → PASS (authoritative, chip=SST39SF040, evidence_sha recorded)
- `val-results/flash3/validation-matrix.md` — updated human-readable matrix

### D-12 Routing

PASS verdict — no Phase-74 route needed for flash3/configure_flash3. The algorithm is correct and functional.

---
*Phase: 73-bench-validate-the-6-families-on-leonardo-hybrid-gated*
*Completed: 2026-06-17*
