---
phase: 83
slug: uv-eprom-write-proof-gated-on-phase-81-blank-state
status: verified
threats_open: 0
asvs_level: 1
created: 2026-06-24
---

# Phase 83 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

This phase is verification-only + bench-validation: no new product code was added.
Task 1 (per plan) ran the host suite + 0xA4 guard + ruff without touching source;
Task 2 generated UV write-image files (in `/tmp`) and updated `.planning` EVIDENCE.
No new endpoints, auth paths, file access, or schema changes were introduced. The
threat register is therefore dominated by **physical/irreversible-silicon** and
**evidence-integrity** threats, mitigated procedurally (blank-state re-confirm,
explicit operator spend gate, byte-exact image + SHA oracles, board-locked
non-vacuous read bar) rather than by code controls.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| operator ↔ irreversible UV silicon | Any VPP-applying write to a UV part is permanent; spend must be explicitly authorized before VPP | write authorization / VPP enable |
| image file ↔ bench write driver | The generated image becomes the exact irreversible payload written to a chip | binary ROM image (64KB / 256KB) |
| host write driver ↔ chip socket | A wrong chip name, wrong image, or wrong VPP could damage or mis-write the part | chip selection + payload + VPP rail |
| read board ↔ verify oracle | Only a Leonardo + Rev 2.0 read is trustworthy; an off-board read yields a vacuous PASS | read-back bytes / SHA verdict |
| Phase 83 scope ↔ irreplaceable 2516 | The 2516 must never be selected/written in Phase 83 (its read path is unstable; deferred to Phase 84) | chip-selection scope |

---

## Threat Register

| Threat ID | Category | Component | Disposition | Mitigation | Status |
|-----------|----------|-----------|-------------|------------|--------|
| T-83-01 | Tampering | write image file (wrong size/content) | mitigate | Byte size (65536 / 262144) and content asserted (all-0x00 for AM27C020; reproducible deterministic SHA for ST M27C512) before any chip write; both oracles recorded in EVIDENCE pre-bench | closed |
| T-83-02 | Denial of Service | bench session on a red host suite | mitigate | SAFE-02 gate: pytest (663) + 0xA4 guard + ruff recorded green before Plans 02/03; STOP-on-red honored (suite green) | closed |
| T-83-03 | Elevation/Destruction | accidental 2516 selection (Plan 01) | mitigate | Plan 01 touched no chip and no 2516 artifact; EVIDENCE scope note records 2516 as OUT (Phase 84) | closed |
| T-83-04 | Elevation/Destruction | wrong chip / wrong image written irreversibly (ST M27C512) | mitigate | UV-01 blank re-confirm + UV-02 explicit operator spend gate before VPP; exact 64KB image + SHA fixed in Plan 01; `dev write-cycle` asserts read-back SHA == image SHA | closed |
| T-83-05 | Information Disclosure (vacuous PASS) | untrusted verify read (ST M27C512) | mitigate | Board locked to Leonardo + Rev 2.0 (controller + r1≈270000 readback); EVID-03 bar = N≥3 byte-identical read + negative control RC=1 | closed |
| T-83-06 | Tampering | over-voltage applied to UV part (ST M27C512) | mitigate | Standard 0x07 13V VPP path (no VPE rail); over-voltage stayed blocked (SC#5); live r1 readback confirms VPP read trustworthily | closed |
| T-83-07 | Elevation/Destruction | accidental 2516 selection (Plan 02) | mitigate | Plan 02 named ONLY ST M27C512; no 2516 seated or selected | closed |
| T-83-08 | Elevation/Destruction | wrong chip / wrong image written irreversibly (AM27C020) | mitigate | UV-01 NOT-BLANK re-confirm + UV-02 operator spend gate before VPP; exact 262144-byte all-0x00 image + SHA fixed in Plan 01; write failed safely (0 bits programmed, chip intact) → ANOMALY handed to Phase 84, part not destroyed | closed |
| T-83-09 | Information Disclosure (vacuous PASS) | untrusted verify read (AM27C020) | mitigate | Board locked to Leonardo + Rev 2.0 (r1≈270000); EVID-03 bar applied (N=3 + neg-control RC=1) — read instability surfaced honestly, not masked | closed |
| T-83-10 | Tampering | over-voltage applied to UV part (AM27C020) | mitigate | Standard 0x08 13V VPP path (no VPE rail); over-voltage stayed blocked (SC#5) | closed |
| T-83-11 | Elevation/Destruction | accidental 2516 selection / consuming the irreplaceable part | mitigate | Plan 03 named ONLY AM27C020; 2516 deferred to Phase 84 and never seated, selected, or written | closed |
| T-83-SC | Tampering | npm/pip/cargo installs (supply chain) | accept | No package installs in this phase (reuse-first, EVID-02); no new third-party dependency introduced | closed |

*Status: open · closed*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-83-SC | T-83-SC | No package installs occurred in this phase; reuse-first (EVID-02) with only existing `dev write-cycle` / `consistency-check` / `verify` tooling. No new supply-chain surface to mitigate. | Henrik Olsson | 2026-06-24 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-06-24 | 12 | 12 | 0 | gsd-secure-phase (short-circuit: register_authored_at_plan_time=true, threats_open=0) |
| 2026-06-24 | 12 | 12 | 0 | gsd-secure-phase re-verify (State A audit: register == union of 3 plan threat models; all 12 closures cross-confirmed against SUMMARY Threat Surface Notes; no new threats) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-06-24
