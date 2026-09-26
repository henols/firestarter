---
phase: 73-bench-validate-the-6-families-on-leonardo-hybrid-gated
audited: 2026-06-18
asvs_level: 2
threats_total: 20
threats_closed: 20
threats_open: 0
status: SECURED
---

# Phase 73 — Security Audit / Threat Verification

Phase 73 is a hybrid software+hardware bench-validation phase. It adds **zero production
code** (D-15 reuse-not-rebuild). Threat mitigations are therefore *process controls* whose
evidence lives in the committed bench artifacts (recorded controller identity, live R1
readback, passing negative controls, explicit per-cell verdicts, N>=2 confirm runs) rather
than in new source. A mitigation is CLOSED when the recorded evidence shows the control was
actually applied — verified here against the on-disk `validation-matrix.json` cells, the
per-byte verdict file, and the SHA-distinct negative-control images, not merely against the
SUMMARY prose.

The threat register is the union of the four per-plan `<threat_model>` blocks
(73-01..73-04-PLAN.md). Each plan also carries the shared `T-73-SC` supply-chain threat
(accept). Total distinct register entries: 17 mitigate + 1 accept (T-73-08) + 4 instances
of T-73-SC (accept), counted as 20 verified dispositions below.

## Threat Verification

| Threat ID | Plan | Category | Disposition | Status | Evidence |
|-----------|------|----------|-------------|--------|----------|
| T-73-01 | 01 | Spoofing | mitigate | CLOSED | `firestarter -p /dev/ttyACM0 fw` → `controller: leonardo, firmware 3.0.0b8` recorded (73-01-SUMMARY §Task 2); ran before the config write |
| T-73-02 | 01 | Tampering | mitigate | CLOSED | `r1: 270000` confirmed present in `~/.firestarter/config.json` (73-01-SUMMARY §Task 2; Rule-1 auto-fix because `config -r1` writes Arduino EEPROM only). Gate armed for Wave-2; live R1=270000 in-band [202500,337500] |
| T-73-03 | 01 | Repudiation | mitigate | CLOSED | All six Tier-1 (28) + Tier-2 (26) suites GREEN; no RED cell to surface (73-01-SUMMARY §Task 1). STOP-on-RED control had nothing to fire on — disposition satisfied by the GREEN evidence |
| T-73-04 | 01 | Info disclosure | mitigate | CLOSED | Explicit `"verdict": "SKIP-deferred"` cells on disk for eeprom28c / flash4(initial) / flash_intel — not silent omissions. Verified in `val-results/{eeprom28c,flash_intel}/validation-matrix.json` |
| T-73-05 | 02 | Spoofing | mitigate | CLOSED | Pre-write gate (73-02-SUMMARY): `fw`→leonardo, `hw`→Rev 2.0 confirmed before W27C512 write |
| T-73-06 | 02 | Repudiation | mitigate | CLOSED | Negative control recorded: `verify W27C512 w27c512-wrongfile.bin` exited 1 (`0x33 != 0x00 at 0x000000`). Source/wrongfile images are SHA-distinct (verified on disk) — oracle non-vacuous |
| T-73-07 | 02 | Tampering | mitigate | CLOSED | Live R1=270000 in-band recorded at gate; STOP-if-out-of-band control armed (73-02-SUMMARY §Pre-Write Gate) |
| T-73-08 | 02 | Elevation (12V VPP) | accept | CLOSED | Accepted-risk log below — W27C512 12V is EVEN-01-proven-clean path on Leonardo (D-11); run completed PASS with no hazard event |
| T-73-09 | 03 | Spoofing | mitigate | CLOSED | Pre-write gate (73-03-SUMMARY): `fw`→leonardo, `hw`→Rev 2.0, `config`→R1=270000 confirmed before the W29C040/flash4 write |
| T-73-10 | 03 | Repudiation | mitigate | CLOSED | Negative control recorded: `verify W29C040 w29c040-wrongfile.bin` exited 1 (`0xaa != 0x00 at 0x000000`). Source/wrongfile SHA-distinct on disk |
| T-73-11 | 03 | Tampering | mitigate | CLOSED | flash4 erase/write hw-error (exit 2 + standalone fallback timeout) recorded as a Phase-74 candidate **with full detail** in `flash4/validation-matrix.json` `reason` field — not a silent retry |
| T-73-12 | 03 | Info disclosure | mitigate | CLOSED | flash3 cell explicitly recorded SKIP-deferred (operator reason), later upgraded to explicit PASS via SST39SF040 bonus; flash4 explicitly FAIL. No silent partial coverage (D-13) |
| T-73-13 | 04 | Spoofing | mitigate | CLOSED | Pre-write gate (73-04-SUMMARY): controller=leonardo, Rev 2.0, R1=270000 in-band before any FM1608 write |
| T-73-14 | 04 | Spoofing (bus echo) | mitigate | CLOSED | Two distinct non-trivial patterns written — A=0x5A, B=0xA5 (bitwise complement). `pattern_a.bin` and `pattern_b.bin` are SHA-distinct on disk; both round-trip with zero mismatches → not a floating-bus echo (D-06) |
| T-73-15 | 04 | Repudiation (byte-0 bug) | mitigate | CLOSED | Per-byte D-08 logic applied and recorded in `val06-perbyte-verdict.txt` (byte-0 status explicitly evaluated; byte-0-only would be table-stakes-PASS). Byte 0 matched in all 4 round-trips here |
| T-73-16 | 04 | Repudiation (vacuous/one-off) | mitigate | CLOSED | Passing negative control (`verify FM1608 baseline` → exit 1, `0xff != 0x5a`) + baseline read + N=2 confirm runs (run1/run2 for A and B) recorded; `retry_count: 2` in sram matrix cell |
| T-73-17 | 04 | Tampering (forced verdict) | mitigate | CLOSED | Verdict is definitive and backed by zero-mismatch agreement across both runs ("Runs agreeing: YES … no ambiguity", verdict file). No forced verdict on ambiguous data; the no-force control was honored |
| T-73-SC | 01 | Tampering (supply chain) | accept | CLOSED | Accepted-risk log below — no packages installed; zero production flash (D-15) |
| T-73-SC | 02 | Tampering (supply chain) | accept | CLOSED | Accepted-risk log below |
| T-73-SC | 03/04 | Tampering (supply chain) | accept | CLOSED | Accepted-risk log below (shared entry across plans 03 and 04) |

**Closed: 20/20. Open: 0.**

## Accepted-Risk Log

### T-73-08 — 12V VPP hazard to seated chip (Elevation)
- **Disposition:** accept (operator-authorized D-11 relaxation).
- **Rationale verified holds:** The only 12V-VPP write this phase was W27C512 on the
  Leonardo/Rev 2.0 path, which is the EVEN-01-proven-clean program path. Tier-1
  recording-stub VPP assertions were GREEN (73-01). The run completed an authoritative PASS
  (write + full readback + SHA match) with no hazard event. No multimeter dry-run was
  required per the operator-authorized D-11 relaxation. Accepted risk stands; no escalation.

### T-73-SC — npm/pip/cargo supply-chain installs (Tampering)
- **Disposition:** accept (all four plans).
- **Rationale verified holds:** `tech-stack.added: []` in every plan SUMMARY frontmatter;
  RESEARCH §Package Legitimacy Audit recorded "none". The phase drives existing CLI over
  USB and writes only evidence artifacts under `val-results/`. Zero production firmware flash
  added (no `pio run` source changes; D-15). No new dependency was introduced — nothing to
  audit further. Accepted risk stands.

## Unregistered Flags

None. All four per-plan SUMMARY `## Threat Flags` / `## Threat Surface Scan` sections
reported no new network endpoints, auth paths, file-access patterns, or schema changes at
trust boundaries. No new attack surface appeared during implementation that lacks a threat
mapping.

## Auditor Notes (informational, not gaps)

- **Chip-substitution deviation (73-03):** The flash3 plan's threat IDs (T-73-09..12) were
  authored for an AM29F040 run but the executed run used W29C040 (flash4) plus a later
  SST39SF040 bonus (flash3). The mitigations (port re-verify, negative control, explicit
  verdict, hw-error-as-Phase-74-candidate) are chip-agnostic process controls and were
  applied to whichever chip was on the bench. Each was independently verified above against
  the actual recorded evidence. The substitution does not leave any mitigation unverified.
- The `firestarter config -r1` vs local-JSON discrepancy (T-73-02) was a real executor
  finding, auto-fixed by writing `r1` to `~/.firestarter/config.json` directly. The gate is
  confirmed armed; this strengthens rather than weakens the mitigation.
