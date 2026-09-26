---
phase: 93-rca-root-cause-the-w29c040-page-0-write-fault
plan: "03"
subsystem: firmware-rca
tags: [w29c040, flash4, boot-block, rca, differential, silicon]

requires:
  - phase: 93-02
    provides: "RCA-01 baseline signature captured N=2 (Timeout at 0x0000ff, observed=0x00, H4 disconfirmed)"

provides:
  - "RCA-02 differential isolation complete — H1/H2/H3/H5 tested, H5 (boot block lock) named root cause"
  - "H1-H5 disconfirming matrix fully populated — no untested axis remains"
  - "evidence/differential/ — 21 capture files: single-byte test, DEBUG_ADDRESS trace, non-page-0/A18=1 writes, diagnostic boundary sweep"
  - "93-RCA-FINDINGS.md RCA-02 section + RCA-03 named root cause filled"
  - "SAFE-01 reaffirmed — all writes used --skip-erase, normal 0x05 dispatch only, DEBUG_ADDRESS trace build re-flashed to normal after"

affects:
  - "93-04 (if any)"
  - "94-rca-fix-w29c040"
  - "95-bench-graduation"
  - "96-ledger"

tech-stack:
  added: []
  patterns:
    - "2×N differential isolation (Phase 44 method): hold constant except one axis, flip it, observe if failure moves"
    - "Boot-block boundary sweep: test pages at boundary-1, boundary, boundary+1 to confirm exact lock region"
    - "SERIAL_DEBUG overhead trap: enabling SERIAL_DEBUG+DEBUG_ADDRESS simultaneously floods the serial link during poll loops (5008+ messages), causing host protocol timeout; use DEBUG_ADDRESS ONLY for trace build without SERIAL_DEBUG, or accept init-phase-only traces"

key-files:
  created:
    - ".planning/phases/93-rca-root-cause-the-w29c040-page-0-write-fault/evidence/differential/test2_single_byte_write.txt"
    - ".planning/phases/93-rca-root-cause-the-w29c040-page-0-write-fault/evidence/differential/test3_debug_trace_1byte.txt"
    - ".planning/phases/93-rca-root-cause-the-w29c040-page-0-write-fault/evidence/differential/test4_page_at_0x1000.txt"
    - ".planning/phases/93-rca-root-cause-the-w29c040-page-0-write-fault/evidence/differential/test5_page_at_0x40000.txt"
    - ".planning/phases/93-rca-root-cause-the-w29c040-page-0-write-fault/evidence/differential/test_summary.txt"
    - "17 additional evidence capture files under evidence/differential/"
  modified:
    - ".planning/phases/93-rca-root-cause-the-w29c040-page-0-write-fault/evidence/93-RCA-FINDINGS.md"

key-decisions:
  - "H5 CONFIRMED as root cause: W29C040 §6.6 first-16K boot block programming lockout activated on this chip instance — irreversible silicon-level protection, not a firmware bug"
  - "H1 (timing), H2 (addressing), H3 (SDP), H4 (poll site) all DISCONFIRMED with direct bench evidence"
  - "W29C020 differential done from datasheets per operator fallback decision (chip not seated); live control DEFERRED (best-effort, future bench)"
  - "SERIAL_DEBUG+DEBUG_ADDRESS simultaneously causes protocol timeout from 5008 poll messages; future trace builds should use DEBUG_ADDRESS without SERIAL_DEBUG, or trace only the INIT phase"
  - "Firmware write algorithm IS correct for unlocked pages (0x4000+); Phase 94 must use a different/unlocked W29C040 instance for BENCH graduation testing"
  - "T-93-CANERASE (FLAG_CAN_ERASE 12V hazard) remains open for Phase 94 FIX-01; separate concern from page-0 root cause"

patterns-established:
  - "Boundary sweep pattern: when a write fails on specific addresses, test (boundary-256), boundary, (boundary+256) to find exact locked region"
  - "Boot block lockout diagnosis: if writes fail for a contiguous region starting at 0x0000 with exact 2^N KB boundary, suspect §6.6 boot block lockout rather than firmware bugs"

requirements-completed: [RCA-02, SAFE-01]

duration: 35min
completed: 2026-06-27
---

# Phase 93 Plan 03: RCA-02 Differential Isolation + H1–H5 Disconfirming Matrix Summary

**W29C040 §6.6 first-16K boot block programming lockout confirmed as the sole root cause: silicon-level hardware protection on this chip instance, not a firmware timing/addressing/SDP bug.**

## Performance

- **Duration:** ~35 min
- **Started:** 2026-06-27T06:53:10Z
- **Completed:** 2026-06-27T07:28:00Z
- **Tasks:** 2 (Tasks 1 + 2 executed autonomously per OPERATOR_DECISION_SCOPE)
- **Files modified:** 22 (evidence captures + FINDINGS.md)

## Accomplishments

- **Root cause named:** H5 CONFIRMED — W29C040 §6.6 first-16K (0x0000–0x3FFF) boot block programming lockout is permanently activated on this chip instance. Writes to locked addresses silently fail — chip ignores the command, DQ7 poll returns `0x00` (never-committed state) on every read.
- **H1/H2/H3/H4 all disconfirmed** with direct bench evidence — no firmware algorithm defect found. The write path works correctly for unlocked pages (0x4000+).
- **Exact boundary identified:** 0x3F00 (last page inside 16K) FAILS; 0x4000 (first page outside 16K) PASSES — exact step-function at the 16K boundary matching §6.6 first boot block size.

## Task Commits

1. **RCA-02 differential + H1-H5 matrix** - `7d6d1d5` (feat)

## Test Results Summary

| Test | Address | Result | Hypothesis verdict |
|------|---------|--------|-------------------|
| #2 Single-byte to page-0 | 0x000000 | FAIL (0x00) | H1 DISCONFIRMED, H3 DISCONFIRMED |
| #3 DEBUG_ADDRESS trace | 0x000000 | top=0x00 correct; protocol timeout on full trace | H2 DISCONFIRMED for page-0 |
| #4 Non-page-0 page | 0x001000 | FAIL (0x00) | Not page-0-specific; H5 indicated |
| #5 A18=1 page | 0x040000 | **PASS** | H2 exonerated; A18 routing correct |
| Diag | 0x002000 | FAIL | Inside 16K — locked |
| Diag | 0x003F00 | FAIL | Last page in 16K — locked |
| Diag | 0x004000 | **PASS** | First page outside 16K — unlocked |
| Diag | 0x07BC00 | **PASS** | Mid-chip — unlocked |
| Diag | 0x07C000 | **PASS** | Last 16K boot block NOT locked |

## Files Created/Modified

- `evidence/differential/test2_single_byte_write.txt` — H1/H3 fork: single-byte FAIL at 0x000000
- `evidence/differential/test3_debug_trace_1byte.txt` — DEBUG_ADDRESS+SERIAL_DEBUG trace (5065 lines); confirmed top=0x00 at init
- `evidence/differential/test4_page_at_0x1000.txt` — Non-page-0 FAIL at 0x0010ff
- `evidence/differential/test5_page_at_0x40000.txt` — A18=1 PASS; read-back confirms correct data
- `evidence/differential/test_summary.txt` — Full boot-block lock pattern summary
- `evidence/differential/test_diag_0x*.txt` — Diagnostic boundary sweep captures (7 files)
- `evidence/differential/w29c040_{1byte,256b_seed43,256b_seed44}.bin` — Test images
- `evidence/93-RCA-FINDINGS.md` — RCA-02 section filled; RCA-03 named root cause recorded; H1-H5 matrix populated

## Decisions Made

- **W29C020 datasheet-only differential** (operator fallback): SDP/pinout/VPP exonerated SAME in both datasheets; surviving differing axes are page size (256B vs 128B), A18 (W29C040 only), boot block boundary (16K vs 8K). Live control write DEFERRED as best-effort.
- **SERIAL_DEBUG + DEBUG_ADDRESS combination is too verbose for live-bench use:** SERIAL_DEBUG enables poll-loop debug messages (5008+ during a 1-byte write timeout), flooding the host-firmware protocol and causing `Command 2 timed out` error. Future trace builds: use DEBUG_ADDRESS without SERIAL_DEBUG, or capture only the INIT phase.
- **Normal firmware re-flashed after trace build** (25136 bytes, confirmed via avrdude verify).

## Deviations from Plan

**Deviation D-01 [Rule 1 - Finding]:** The SERIAL_DEBUG + DEBUG_ADDRESS trace build caused a protocol timeout (5008 poll-loop debug messages flood the serial link). Only the init-time address trace (`Address 0x000000, top msb lsb 00 00 00`) was captured; the full page-load cadence trace was unavailable. This is sufficient for H2 disconfirmation (top-address is stable at init) but not for per-byte cadence timing (H1 quantitative). However, H1 was already disconfirmed by the single-byte test failure (Test #2), so the missing timing cadence does not leave any hypothesis untested.

**Deviation D-02 [Rule 1 - Unexpected finding]:** The plan expected Test #4 (non-page-0 at 0x1000) to potentially distinguish page-0-specific vs general failure. The result revealed the fault covers the entire first 16K, not just page 0. This led to the boot-block boundary sweep (diagnostic tests not in the original plan), which identified the exact root cause. The diagnostic sweep was within plan scope (H5 investigation) and produced the final root cause identification.

---

**Total deviations:** 2 minor findings (no rule violations; both productive)
**Impact on plan:** SERIAL_DEBUG trace limitation was auto-worked-around (H2 disconfirmed via Test #5 instead); diagnostic boundary sweep added per H5 investigation path.

## Issues Encountered

- **SERIAL_DEBUG overhead:** Combining SERIAL_DEBUG + DEBUG_ADDRESS for the trace build generates 5008 "Write EPROM" poll messages in a single 1-byte write, swamping the COBS/serial protocol and causing host timeout. Resolved by noting the init-time trace (`top msb lsb 00 00 00`) was sufficient for H2 and by using Test #5 (A18=1 PASS) as additional H2 exoneration.
- **Boot block lockout discovery:** The failure region being exactly the first 16K (not just page 0) was unexpected. Required adding diagnostic boundary tests outside the original test matrix. The discovery was cleanly bounded by §6.6 and confirmed as the root cause.

## Known Stubs

None — this is an RCA evidence plan with no data-rendering stubs.

## Threat Flags

None — no new network endpoints, auth paths, file access patterns, or schema changes. DEBUG_ADDRESS trace build was passive (no dispatch change) and re-flashed to normal after use. SAFE-01 reaffirmed.

## Next Phase Readiness

**For Phase 94 (Fix):**
- Root cause is chip-instance-specific silicon state (boot block lock), NOT a firmware bug
- The write algorithm is correct for unlocked pages; firmware changes for page-0 graduation are NOT needed (the algorithm already works)
- Phase 94 MUST address: (1) T-93-CANERASE (FLAG_CAN_ERASE=0x02 causes 12V erase on 5V chip — FIX-01), (2) obtaining an unlocked W29C040 or using addresses ≥ 0x4000 for BENCH graduation testing
- The seated W29C040 cannot be used to test page-0 (boot block lock is irreversible); operator must decide: new chip or test on 0x4000+ region

**Blocker for Phase 95 (BENCH graduation):**
- Phase 95 BENCH-01 requires writing page-0 for a byte-exact write→verify SHA gate
- Current chip has first 16K permanently locked; a different (unlocked) W29C040 instance is required
- OR Phase 95 acceptance criteria can be redefined to use address ≥ 0x4000 (firmware is proven working there)

---
*Phase: 93-rca-root-cause-the-w29c040-page-0-write-fault*
*Completed: 2026-06-27*
