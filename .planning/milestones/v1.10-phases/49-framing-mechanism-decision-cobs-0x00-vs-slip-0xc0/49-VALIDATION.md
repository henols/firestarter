---
phase: 49
slug: framing-mechanism-decision-cobs-0x00-vs-slip-0xc0
status: approved
nyquist_compliant: true
wave_0_complete: false
created: 2026-06-01
---

# Phase 49 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> **Phase 49 produces NO code** — its deliverable is the ADR `.planning/v1.10-FRAMING-DECISION.md`.
> Validation is **document-assertion based**: verify the ADR is structurally complete, internally
> consistent, and traceable to its binding inputs. No unit tests, no `pytest`, no `pio test`.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Document assertion (bash + grep) — no test runner |
| **Config file** | none |
| **Quick run command** | `grep` assertions in the Per-Task Verification Map below |
| **Full suite command** | run all assertions below + human review of the SAFE-01 resolution section |
| **Estimated runtime** | ~2 seconds (grep) + manual review |

---

## Sampling Rate

- **After every task commit:** Human review of the ADR section authored in that task
- **After every plan wave:** Run the automated `grep` assertions; human review of the SAFE-01 resolution section
- **Before `/gsd-verify-work`:** All assertions green AND SAFE-01 section contains either (a) static proof of host `0x00`-silence citing its sub-claims, or (b) explicit "inconclusive → SLIP selected per D-04"
- **Max feedback latency:** ~5 seconds (assertions are local grep)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| SAFE-01 resolution | TBD | — | SAFE-01 | — | ADR resolves `0x00` bus-aliasing risk, traceable to COBS-DECISION §5 Q2/Q3 | doc-assertion | `grep -qE "Q2\|Q3\|bus-aliasing" .planning/v1.10-FRAMING-DECISION.md && echo PASS` | ❌ W0 (ADR written this phase) | ⬜ pending |
| SAFE-01 outcome | TBD | — | SAFE-01 | — | ADR either proves host `0x00`-silence OR explicitly selects SLIP under D-04 | manual | Human review of SAFE-01 resolution section | ❌ W0 | ⬜ pending |
| Scored matrix | TBD | — | SAFE-01 (D-02) | — | Matrix scores all 4 criteria (safety, byte-exactness, simplicity, overhead) | doc-assertion | `grep -qiE "safety\|byte-exact\|simplicity\|overhead" .planning/v1.10-FRAMING-DECISION.md && echo PASS` | ❌ W0 | ⬜ pending |
| Frame contract | TBD | — | SAFE-01 (D-06) | — | Per-file change map names all 4 files | doc-assertion | `grep -qE "rurp_serial_utils\|serial_comm\|frame_parser\|test_messages" .planning/v1.10-FRAMING-DECISION.md && echo PASS` | ❌ W0 | ⬜ pending |
| Supersession link | TBD | — | SAFE-01 (D-05) | — | ADR cross-references v1.9-COBS-DECISION.md and supersedes its DEFER line | doc-assertion | `grep -q "v1.9-COBS-DECISION" .planning/v1.10-FRAMING-DECISION.md && echo PASS` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*
*Task IDs finalized by the planner; rows map to the success criteria, not to code.*

---

## Wave 0 Requirements

- [ ] `.planning/v1.10-FRAMING-DECISION.md` — the ADR itself (created during Phase 49 execution; the assertions above target this file)
- [ ] No test files, no framework install, no CI changes required in Phase 49

*Phase 50 will require updating `test_rurp_log_id.cpp`; host-side parser tests land in Phase 52 — those are not Phase 49 gaps.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| SAFE-01 resolution is sound | SAFE-01 | The static-proof argument (firmware `com_mode` gate + host `0x00`-silence) is a reasoning chain, not a grep-able string | Read the SAFE-01 resolution section; confirm it either (a) proves host `0x00`-silence in the mode-transition window with its sub-claims (pyserial `flush()`, `init_programmer()` RX drain), or (b) declares the proof inconclusive and selects SLIP `0xC0` per D-04 |
| Mechanism choice is evidence-backed | SAFE-01 (D-01/D-02) | "Highest aggregate score" is a judgment over the matrix, not a string match | Read the decision statement; confirm it cites the scored matrix ranking, not a bare assertion (Success Criterion 1) |
| Frame contract is fully frozen | SAFE-01 (D-06) | Completeness of delimiter + escape scheme + frame layout + CRC8 placement is a structural review | Confirm all D-06 fields are present and unambiguous so Phases 50–52 inherit a contract, not an open question |

---

## Validation Sign-Off

- [ ] All success-criteria rows have a doc-assertion or a manual-review instruction
- [ ] Sampling continuity: every authored ADR section is reviewed at its task commit
- [ ] Wave 0 covers the one MISSING reference (the ADR file)
- [ ] No watch-mode flags (N/A — no test runner)
- [ ] Feedback latency < 5s
- [x] `nyquist_compliant: true` set in frontmatter (task→row mapping confirmed by plan-checker)

**Approval:** approved 2026-06-01
