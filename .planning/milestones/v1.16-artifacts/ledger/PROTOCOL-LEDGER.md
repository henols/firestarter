# v1.16 Protocol Ledger — Per-Protocol Bench Validation + Documentation

**Milestone:** v1.16 — Protocol-First Architecture Rebuild
**Firmware under test:** submodule commit `a296195` (Phase 89 HEAD, incl. CR-01 fix)
**Version string caveat:** firmware reports `3.0.0b10`; the actual build is the v1.16 recompose — record the submodule commit, not the version string
**Oracle:** leonardo + RURP Rev 2.0
**Generated:** 2026-06-26
**Milestone flash impact:** −518 B net (25654 → 25136 B / 87.7%); primitives P7 (0 B) + P4 (−164 B) + P3 (−402 B) + P5 (+2 B) + CR-01 fix (+46 B). See `89-FLASH-LEDGER.md` for the full step table.

**Composes with (cross-reference only — no data copied):**
- `firestarter_app/tools/validation_matrix_spec.json` — v1.13 per-family validation matrix (join key: `matrix_family`)
- `.planning/milestones/v1.15-artifacts/bench/EVIDENCE.json` — v1.15 per-chip bench evidence (join key: `evidence_chip`)

**D-04 compose-by-cross-reference:** this ledger holds join keys only; SHA-256 digests and verdict data remain authoritative in the upstream files above.

---

## Protocol Bucket Table

| Bucket | Proposed Name | Handler (File) | Matrix Family | Primitives Used | On-Hand Chip | Verification Status | Evidence Refs |
|--------|---------------|----------------|---------------|-----------------|--------------|--------------------:|---------------|
| `0x05` | FLASH-AMD-STD | `configure_flash4()` (`flash_type_4.cpp`) | `flash4` [proto 5] | P4, P5, P7 | W29C020 | **PASS** | P90 (a296195, leonardo+Rev2.0): read N=3 + write-cycle A→B (auto-erase, `write -b`) both byte-identical to v1.15 baseline; neg-control verify(A) RC=1. Artifacts: `bench/W29C020-read/`, `bench/W29C020-wcB/`, `bench/BENCH-LOG.md` |
| `0x06` | FLASH-AMD-ALT | `configure_flash3()` (`flash_type_3.cpp`) | `flash3` [proto 6] | P4, P7 | SST39SF040 | **PASS** | **FIX-91 (P91, stock a296195, leonardo+Rev2.0):** read N=3 + write-cycle byte-identical to v1.15. The P90 FAIL was a TEST-METHOD error — `write -b` set FLAG_SKIP_ERASE so flash3 (NOR) skipped the required erase (3 stuck bytes @0x0-0x2 == imgA & imgB). Re-bench via erase-enabled plain `firestarter write` (writeA→verifyA→writeB→verifyB→consistency-check N=3) PASSES; recompose fw innocent (b10 fails identically with `-b`). Artifacts: `bench/SST39SF040-fix/`, `bench/SST39SF040-read/`, `rca/91-RCA.md` |
| `0x07` | EPROM-STD | `configure_eprom()` (`eprom.cpp`) | `eprom` [proto 7] | P4, P3 | W27C512 | **PASS** | **FIX-91 (P91, operator returned + W27C512 seated, stock a296195, leonardo+Rev2.0):** chip-ID PASSED (0xDA08); read N=3 + write-cycle byte-identical to v1.15 `e16b2a5b…`. SAME cause as 0x06 — `write -b` skipped the erase (`eprom_internal_erase`, gated on FLAG_CAN_ERASE which W27C512 has); P90 bad-bytes-@0x0 = skipped erase, NOT a VPP regression. Fixed via erase-enabled plain `firestarter write` (writeA→verifyA→writeB→verifyB→consistency-check N=3); no VPP-high guard. Artifacts: `bench/W27C512-fix/`, `bench/W27C512-read/`, `rca/91-RCA.md` |
| `0x08` | EPROM-QUICK | `configure_eprom()` (`eprom.cpp`) | `eprom` [proto 8] | P4, P3 | AM27C020 | **open-defect-carried** (FUT-08) | **Phase-99 bench (leonardo+Rev2.0, fw 35706c2, Phase-98 fix):** DEFER (fix-effective-but-unreliable) — small pure-1→0 writes (no UV eraser on hand) show write#1 60/64 bytes byte-exact (Phase-97 0-bits signature REFUTED), write#2 0/64 (marginal/unreliable). No byte-exact graduation. See `bench/AM27C020-graduation/` + `.planning/milestones/v1.18-artifacts/bench/EVIDENCE.json` and Open Defects below |
| `0x0B` | EPROM-LEGACY | `configure_eprom()` (`eprom.cpp`) | `eprom` [proto 11] | P4, P3 | — | **open-defect-carried** (FUT-03) | See Open Defects below |
| `0x0D` | EEPROM-POLL | `configure_eeprom28c()` (`eeprom_28c.cpp`) | `eeprom28c` [proto 13] | P4, P5, P7 | — | **UNVERIFIED** | No on-hand silicon. Rep chip: AT28C256 (`datasheets/0x0D-EEPROM-POLL/AT28C256.pdf`) |
| `0x0E` | SRAM-32PIN | `configure_sram()` (`sram.cpp`) | `sram` [proto 14] | — | — | **UNVERIFIED** | No on-hand silicon. Rep chip: DS1245Y (`datasheets/0x0E-SRAM-32PIN/DS1245Y.pdf`) |
| `0x10` | FLASH-INTEL | `configure_flash_intel()` (`flash_intel.cpp`) | `flash_intel` [proto 16] | P4, P3 | — | **UNVERIFIED** | No on-hand silicon. Rep chip: Intel-28F010 (`datasheets/0x10-FLASH-INTEL/Intel-28F010.pdf`) |
| `0x27` | SRAM-24PIN | `configure_sram()` (`sram.cpp`) | `sram` [proto 39] | — | — | **UNVERIFIED** | No on-hand silicon. Rep chip: 6116 (`datasheets/0x27-SRAM-24PIN/6116.pdf`) |
| `0x28` | SRAM-STD | `configure_sram()` (`sram.cpp`) | `sram` [proto 40] | — | FM1608 | **PASS** | P90 (a296195, leonardo+Rev2.0): read N=3 + write-cycle A→B (`write -b` FRAM method) both byte-identical to v1.15 baseline; neg-control verify(A) RC=1. Artifacts: `bench/FM1608-read/`, `bench/FM1608-wcB/`, `bench/BENCH-LOG.md`. Note: EVIDENCE labels FM1608 family `"0x40 (SRAM_STD / FRAM)"` — `0x40` is decimal 40 = hex `0x28` (NAME-04 conflation, retired in PROTOCOLS.md §1.10) |
| `0x29` | SRAM-512K-1M | `configure_sram()` (`sram.cpp`) | `sram` [proto 41] | — | — | **UNVERIFIED** | No on-hand silicon. Rep chip: DS1245Y (`datasheets/0x29-SRAM-512K-1M/DS1245Y.pdf`; DS1250Y bot-blocked at Phase 85 D-02) |
| `0x34` | EEPROM-X88C64 | `configure_not_implemented()` (`not_implemented.cpp`) | null (no matrix family) | — | — | **UNVERIFIED** | No on-hand silicon; handler returns `0xBB` (not_implemented); PCB-blocked FUT-01. Rep chip: X88C64 (`datasheets/0x34-EEPROM-X88C64/X88C64.pdf`) |

**Verification status key:**
- `bench-pending` — on-hand silicon, Plan 04 bench session will flip to PASS (if SHA regression matches v1.15 baseline) or FAIL-INVESTIGATE
- `UNVERIFIED` — no on-hand silicon; full row with datasheet-representative chip; bench-proven when silicon acquired
- `open-defect-carried` — on-hand chip exists but under an open defect; carried verbatim from STATE.md (no status change)
- `PASS` — bench-proven: oracle=leonardo+Rev2.0, p90 SHA regression matches v1.15 baseline (both read and write-cycle)
- `FAIL-INVESTIGATE` — bench-tested, read matches v1.15 but write-cycle does NOT (reproducible recompose write-path regression; D-03 never-auto-pass). NOT graduated; see BENCH-LOG.md Session Summary RCA scope

**Primitives key (Phase 89 recompose):**
- P3 — `vpp_check_window` (extracted to `primitives.cpp`; handles the +500 mV over-voltage gate for VPP-gated families; −402 B net savings)
- P4 — `chip_id_report` (extracted to `primitives.cpp`; AMD/JEDEC chip-id read+compare; −164 B net savings)
- P5 — `poll_readback` (extracted to `primitives.cpp`; bounded single-address readback poll; +2 B net cost)
- P7 — SDP / const-table dedup (shared SDP byte-sequence tables in `flash_utils.h`; 0 B)
- SRAM buckets (0x0E/0x27/0x28/0x29) use none of the above — plain read/write, no VPP/chip-id/poll primitive use

---

## Open Defects (carried verbatim — no status change)

These three defects are carried at their current documented status. No re-litigation, no status change.
Source records: `.planning/STATE.md` Deferred Items + `.planning/milestones/v1.15-artifacts/bench/EVIDENCE.json` phase84 blocks.

### CR-01 / W29C040 / bucket 0x05

**Chip:** W29C040 (512 KB flash4)
**Defect ID:** CR-01 (reopened Phase-74 Wave-2)
**Disposition (verbatim):** Phase-74 fix not silicon-effective. Reopen Phase-74 Wave-2 (likely dual-repo lockstep firmware fix). FAIL CONFIRMED: timeout verifying byte @0x0000ff (256 B page-0 boundary).
**Source:** `.planning/STATE.md#deferred-items` · `.planning/milestones/v1.15-artifacts/bench/EVIDENCE.json#phase84.task3c_w29c040` · `firestarter_app/tools/flash4-page-size-datasheet-sourced-cr01.md`
**Status changed:** no

### FUT-08 / AM27C020 / bucket 0x08

**Chip:** AM27C020 (262144 B, DIP32 32-pin Large EPROM)
**Defect ID:** FUT-08 (supersedes FUT-06; renumbered from the operator-requested "FUT-07" to avoid collision with the pre-existing v1.17 FUT-07/W29C040 defect — see `.planning/STATE.md` Deferred Items table)
**Disposition (verbatim):** Supersedes FUT-06 (renumbered FUT-08 to avoid collision with the pre-existing v1.17 FUT-07/W29C040 defect). Phase-98 fix (rw-pin:[31] → CTRL_READ_WRITE 0x40) landed and is bench-effective — 0x08 write path programs bits (Phase-97 0-bits refuted, 60/64 byte-exact at Phase-99 bench), BUT programming is marginal/unreliable (write#2 0/64). Next: characterize program-window VPP-under-load (DMM at socket pin 1) + write timing.
**Source:** `.planning/phases/99-bench-ledger-graduation-gate-evidence-ledger-update/99-03-BENCH-LOG.md` · `.planning/milestones/v1.18-artifacts/bench/EVIDENCE.json`
**Status changed:** no

### FUT-03 / 2516 / bucket 0x0B

**Chip:** 2516 (2048 B, DIP24, NMOS Legacy EPROM)
**Defect ID:** FUT-03
**Disposition (verbatim):** 2516 0x0B read instability + write proof — deferred best-effort (D-22). 3 distinct SHAs after VPP-skip; shared OE/VPP pin. 2516 stays UNVERIFIED; not write-graduated (SAFE-04).
**Source:** `.planning/STATE.md#deferred-items` · `.planning/milestones/v1.15-artifacts/bench/EVIDENCE.json#phase84.task2_2516_reread`
**Status changed:** no

---

## SAFE-04 Safety Posture (verify-present-only)

Per Plan 90-03 evidence (`.planning/milestones/v1.16-artifacts/ledger/SAFE-04-VERIFICATION.md`):

| Guard | Location (post-recompose) | Status |
|-------|--------------------------|--------|
| Over-voltage HIGH check `vpp_mv > (uint32_t)handle->vpp_mv + 500` | `firestarter/src/proms/primitives.cpp:106` (inside `vpp_check_window`; moved from handler bodies in P3) | PRESENT + UNMODIFIED |
| Host `chip_resolver.resolve_chip` support-status guard | `firestarter_app/firestarter/chip_resolver.py:55` | PRESENT + UNCHANGED |
| 2516 `verification_status=UNVERIFIED` | `firestarter_app/firestarter/data/chip_database.json` | UNVERIFIED — no write-graduation this phase |

---

*Generated by Phase 90 Plan 02. Machine-readable form: `PROTOCOL-LEDGER.json` (same rows, same verification statuses).*
