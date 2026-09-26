---
phase: 78
slug: x88c64-0x34-firmware-handler
status: verified
threats_open: 0
asvs_level: 1
created: 2026-06-22
---

# Phase 78 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

**Phase outcome context:** Phase 78 was a *contingent* handler-write phase that took the
**DEFER (Branch A)** path driven by the Plan 01 `A6 VERDICT: PCB-BLOCKED` (HIGH). **Zero
firmware or host code was written.** X88C64 stays `protocol-not-implemented` and host-refused;
graduation is deferred under FUT-01. Every threat below is a *proceed-path* hazard that can
only manifest if handler/dispatch code exists — so the defer-with-no-code outcome closes each
one structurally (the dangerous code was never created), and the live SAFE invariants confirm it.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| host CLI → chip dispatch | `resolve_chip` host-guard refuses `protocol-not-implemented` chips before any wire command is built — the wrong-VPP-to-wrong-pin damage barrier | chip-select / program command (would drive socket voltages) |
| firmware dispatch → hardware bus | `configure_memory` routes a non-zero unknown protocol (0x34) to the generic `configure_not_implemented` (0xBB) guard with zero hardware side effects | protocol id → control-register / VPP-rail bits |
| native test stub → recording buffer | (proceed-path only — not exercised) recording-stub would assert the register-write sequence with zero real hardware | simulated register writes |

---

## Threat Register

| Threat ID | Category | Component | Disposition | Mitigation | Status |
|-----------|----------|-----------|-------------|------------|--------|
| T-78-01 | Tampering / Damage | 0x34 routing reaching a 12V VPP handler | mitigate | No 0x34 dispatch arm added (defer branch); 0x34 stays routed to the generic 0xBB guard; X88C64 stays `protocol-not-implemented` + host-refused; `check_dispatch.py` SAFE-02 gate green (no DB change) | closed |
| T-78-02 | Tampering | Blind handler writing to unverified hardware | mitigate | No handler code written; graduation recorded hardware-deferred (D-04 / FUT-01); chip stays host-refused; `chip_resolver` host-guard NOT removed (present, 4 refs); `support_status` unchanged | closed |
| T-78-03 | Tampering | Control-register bit pollution (ALE via a busy bit) | mitigate | D-02 deferral bar enforced at the Task-1 BLOCKING gate: no `FREE-BIT-FOUND` verdict exists, so no ALE drive authorized; speculative reuse of a busy line (e.g. `CTRL_VPP_REGULATOR_ENABLE`) prohibited; verdict recorded PCB-BLOCKED | closed |
| T-78-SC | Tampering | npm/pip/cargo supply-chain (installs) | accept | No package installs introduced; documentation-only changes to a `.planning` artifact; existing toolchain only (`pip install -e '.[test]'` merely restores it) | closed |

*Status: open · closed*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-78-SC | T-78-SC | Documentation-only phase; no third-party packages added or installed. Supply-chain surface is unchanged from the prior phase baseline; the existing PlatformIO/Unity/ArduinoFake/pytest/ruff toolchain is pre-installed and merely restored. | Henrik Olsson | 2026-06-22 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-06-22 | 4 | 4 | 0 | gsd-secure-phase (orchestrator; short-circuit — plan-time register, threats_open: 0) |
| 2026-06-22 | 4 | 4 | 0 | gsd-secure-phase re-run (live re-verification — all closure evidence re-confirmed below; no drift) |

**Closure evidence (verified live 2026-06-22):**
- `git -C firestarter status --porcelain` → clean; no firmware src/include/test changes (T-78-01/02/03).
- `git -C firestarter_app status --porcelain` → `chip_resolver.py` / `chip_database.json` / `pinouts.json` / `constants.py` all clean (T-78-01/02).
- Host-guard present: `grep -c "ChipNotImplementedError\|protocol-not-implemented" chip_resolver.py` → 4 (T-78-02).
- X88C64 `unsupported_reason` = `"protocol not implemented: 0x34 …"` — still host-refused, not graduated (T-78-01/02).
- `A6 VERDICT: PCB-BLOCKED` + `Branch A — ALE PCB-blocked, no handler code` recorded in `X88C64-FEASIBILITY.md` (T-78-03).

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-06-22
