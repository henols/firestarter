# Phase 73: Bench-Validate the 6 Families on Leonardo (hybrid-gated) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-17
**Phase:** 73-bench-validate-the-6-families-on-leonardo-hybrid-gated
**Areas discussed:** Bench inventory & shield, SRAM no-op method (VAL-06), Bench-driving model, Closeability & family priority

---

## Bench inventory & shield

### Chips A (EPROM/EEPROM/Flash-AMD/Flash-type4)
| Option | Description | Selected |
|--------|-------------|----------|
| W27C512 (0x07) | Known-good baseline; Phase 75 erase rep | ✓ |
| AT28C256 (5V EEPROM 0x0D) | SDP-disable + 64-byte page + DQ7 polling | |
| AM29F040 (Flash AMD 0x06) | Largest flash family; sector/chip erase | ✓ |
| AT29C040 (Flash type-4 0x05) | Exposes FIX-02 CMD_CHECK_CHIP_ID gap | |

### Chips B (Flash Intel / SRAM)
| Option | Description | Selected |
|--------|-------------|----------|
| AM28F010 (Flash Intel 0x10) | 12V P1 + status-register branches | |
| An SRAM chip (0x0E/27/28/29) | Needed for VAL-06 | ✓ |

### Shield rev
| Option | Description | Selected |
|--------|-------------|----------|
| Rev 2.2 | Latest; reads clean on Leonardo | |
| Rev 2.0 | Reads clean on Leonardo; no known fault | ✓ |
| Modified Rev 0 | Carries Rev-0 read-path fault history | |

**User's choice:** On hand = W27C512, AM29F040, an SRAM chip. Shield = Rev 2.0.
**Notes:** Operator corrected the W27C512 framing — "you have a delusion that it is a UV-EPROM, it is an EEPROM, check info to confirm." Verified live: `chip_database.json` WINBOND `W27C512,W27E512`, `electrical.type: EEPROM`, `vpp_mv: 12000`, 28-pin, `support_status: supported`. Confirmed — recorded as D-04. AT28C256 / AT29C040 / AM28F010 → SKIP-deferred (no chip on hand).

---

## SRAM no-op method (VAL-06)

### SRAM part
| Option | Description | Selected |
|--------|-------------|----------|
| 62256 (32K×8 SRAM) | Volatile async SRAM, 0x0E | |
| 6264 (8K×8 SRAM) | Volatile async SRAM | |
| FM1608 (FRAM) | Non-volatile FRAM; carries byte-0 write bug | ✓ |

### Rigor (anti false-positive)
| Option | Description | Selected |
|--------|-------------|----------|
| Two distinct patterns (A then B) | Echo can't track two writes — strongest | ✓ |
| Single distinct non-trivial pattern | Simpler; weaker vs echo | |
| You decide | Planner picks | |

### Verdict bar
| Option | Description | Selected |
|--------|-------------|----------|
| Baseline-read + N≥2 confirm | Read initial contents, reproduce ≥2× | ✓ |
| Single decisive Leonardo run | One clean run classifies | |

**User's choice:** FM1608; two distinct patterns A→B; baseline-read + N≥2 confirm.
**Notes:** FM1608 is FRAM (non-volatile) not volatile SRAM — removes the volatility confound but introduces the parked byte-0 bug as a confounder. Per-byte verdict logic added (D-08): all-bytes-fail = FIX-01 no-op defect; byte-0-only discrepancy = persistence works (VAL-06 PASS) + separately-parked FRAM bug.

---

## Bench-driving model

### Driving
| Option | Description | Selected |
|--------|-------------|----------|
| Claude drives over USB passthrough | Operator does chip/shield/meter/photos only | ✓ |
| Fully operator-manual | Operator runs all commands | |
| You decide | Planner picks | |

### Pre-write gate
| Option | Description | Selected |
|--------|-------------|----------|
| Chip-OUT VPP meter dry-run for W27C512 | Physical 12V VPP dry-run before seated write | |
| Standard precondition only | verify-port + live R1/R2 + Tier-1 stub VPP assertions | ✓ |

**User's choice:** Claude drives over USB passthrough; standard precondition only.
**Notes:** Pre-write gate is a deliberate, operator-authorized relaxation for this phase (D-11) — W27C512/EVEN-01 proven clean on Leonardo; Leonardo chip-OUT-exempt; AM29F040 + FM1608 are no-VPP.

---

## Closeability & family priority

### VAL-06 gate
| Option | Description | Selected |
|--------|-------------|----------|
| Yes — VAL-06 must be resolved | Definitive verdict required to close | ✓ |
| No — SRAM may SKIP-defer too | Inconclusive carries forward | |

### On-hand bar
| Option | Description | Selected |
|--------|-------------|----------|
| Record a verdict — PASS or FAIL both close | FAIL routes to Phase 74 | ✓ |
| Must all be GREEN-PASS | Any FAIL blocks close | |

### Deferred bar
| Option | Description | Selected |
|--------|-------------|----------|
| Yes — SKIP-deferred is closeable | Tier-1/2 GREEN + Tier-3 SKIP-deferred | ✓ |
| No — acquire chips first | Block until all 6 bench-run | |

**User's choice:** VAL-06 is a hard gate; on-hand families close on any recorded verdict; chip-less families close as SKIP-deferred.
**Notes:** Partial coverage is explicit per-cell, never silent.

---

## Claude's Discretion

- Exact FM1608 A/B pattern bytes (subject to non-trivial rule).
- Run ordering across the 3 on-hand families + operator hardware-action checkpoint sequencing.
- Evidence-SHA capture/log format (within Phase-71 artifact schema).
- Whether AM29F040 sector-vs-chip erase is exercised in its Tier-3 cell or recorded advisory.

## Deferred Ideas

- FM1608 byte-0 write bug — parked debug item, out of v1.13 scope; separated as a confounder, not fixed.
- Acquiring AT28C256 / AT29C040 / AM28F010 to lift their SKIP-deferred cells — future bench session.
