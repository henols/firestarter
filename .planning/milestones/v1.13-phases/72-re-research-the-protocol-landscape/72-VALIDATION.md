---
phase: 72
slug: re-research-the-protocol-landscape
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-06-17
---

# Phase 72 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Phase 72 delivers a **committed document**, not code. Validation means confirming
> the document's claims are accurate and traceable to cited source files + datasheets.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | None — document validation (grep-assertable claims against live source) |
| **Config file** | none |
| **Quick run command** | `grep -cE "feasible" .planning/v1.13-PROTOCOL-ENUMERATION.md` |
| **Full suite command** | Manual SC#1–SC#3 verification checklist (below) + code-grep anchors |
| **Estimated runtime** | ~5 seconds (grep) + reviewer cross-check |

---

## Sampling Rate

- **After every task commit:** Reviewer re-runs the grep anchor for the row(s) touched and confirms each verdict cites a real code location (`file:line`) that resolves.
- **After every plan wave:** Run all three SC#1–SC#3 verification commands; all must pass.
- **Before `/gsd-verify-work`:** Reviewer reads the full enumeration document and cross-checks ≥ 3 table rows against firmware/host source.
- **Max feedback latency:** ~10 seconds.

---

## Per-Task Verification Map

| SC | Requirement | Secure/Correct Behavior | Test Type | Automated Command | File Exists | Status |
|----|-------------|-------------------------|-----------|-------------------|-------------|--------|
| SC#1 | RSCH-01 | Each in-scope `protocol_id` has exactly one verdict (feasible-and-implemented / feasible-gap / infeasible), citing v1.11 field dictionary + datasheet, and records where v1.12's "feasible set complete" holds vs. is overstated | Document inspection | `grep -nE "feasible-and-implemented\|feasible-gap\|infeasible" .planning/v1.13-PROTOCOL-ENUMERATION.md` (≥ 12 protocol rows) | ❌ W0 (artifact created this phase) | ⬜ pending |
| SC#2 | RSCH-01 | The 5 named gap items (erase 0x07 / `configure_sram` no-op / X88C64 0x34 / flash4 chip-id / stale 0x39 comment) each marked in-scope or deferred with rationale | Document inspection | `grep -nE "erase\|configure_sram\|X88C64\|flash4\|0x39" .planning/v1.13-PROTOCOL-ENUMERATION.md` (all 5 present w/ verdict) | ❌ W0 | ⬜ pending |
| SC#3 | RSCH-01 | Anti-features re-confirmed fail-closed with cited code locations; `RURP_VPP_CEILING_MV=22000` not relaxed | Code grep + document inspection | `grep -n "RURP_VPP_CEILING_MV = 22000" firestarter_app/tools/build_db.py` (exit 0); `grep -nc "configure_not_implemented" firestarter/src/proms/memory.cpp` (≥ 1) | ✅ code files exist | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `.planning/v1.13-PROTOCOL-ENUMERATION.md` — the primary deliverable; covers RSCH-01 SC#1/SC#2/SC#3 (created during this phase, hence ❌ at plan time)
- [ ] `.planning/phases/72-re-research-the-protocol-landscape/72-VERIFICATION.md` — verification report

*Existing code files used as evidence sources (memory.cpp, sram.cpp, eprom.cpp, flash_type_4.cpp, build_db.py, check_dispatch.py, chip_database.json, protocol-id.md) all exist — no new code files required.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Verdict accuracy (does each cited `file:line` actually back the stated verdict?) | RSCH-01 SC#1 | Semantic claim — grep proves a citation exists, not that it is correct | Reviewer opens ≥ 3 cited source locations and confirms the code matches the claimed behavior |
| "Overstated vs. holds" judgment on v1.12's feasible-set-complete claim | RSCH-01 SC#1 | Requires reading v1.12 audit + comparing to current code state | Reviewer confirms each "overstated" call is backed by a concrete code gap (e.g. `sram.cpp` no-op, `flash_type_4.cpp` missing CMD_CHECK_CHIP_ID) |
| Datasheet-grounded feasibility for X88C64 0x34 | RSCH-01 SC#2 | Datasheet not machine-checkable | Reviewer confirms the row cites a named datasheet/protocol source for the STORE/RECALL classification |

---

## Validation Sign-Off

- [ ] All SC have a grep anchor or a documented manual-only verification
- [ ] Sampling continuity: every committed enumeration row has a resolvable code citation
- [ ] Wave 0 covers the enumeration artifact + verification report
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
