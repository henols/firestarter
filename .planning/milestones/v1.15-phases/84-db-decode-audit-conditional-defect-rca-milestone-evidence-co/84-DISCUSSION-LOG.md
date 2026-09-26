# Phase 84: DB Decode Audit + Conditional Defect RCA + Milestone Evidence Consolidation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-24
**Phase:** 84-db-decode-audit-conditional-defect-rca-milestone-evidence-consolidation
**Areas discussed:** Firmware-touch posture, 2516 / GRAD-03 attempt, FIX-01 defect scope, Audit + close posture

---

## Area selection

All four offered gray areas were selected for discussion: Firmware-touch posture, 2516 / GRAD-03
attempt, FIX-01 defect scope, Audit + close posture.

---

## Firmware-touch posture

### Allowed to ship firmware?

| Option | Description | Selected |
|--------|-------------|----------|
| FW change allowed | Permit dual-repo lockstep fw fix (e.g. VPP-skip-on-read); accepts fw gate (pio test native + Leonardo flash ≤~90%); fw diverges from pinned b10 | ✓ |
| Host-only or defer | Keep milestone host-only; RCA + formally defer any firmware-rooted defect; 2516/GRAD-03 stays deferred | |
| FW only if it unblocks 2516 | Permit fw change only if RCA shows it will stabilize the 0x0B read for the 2516 | |

**User's choice:** FW change allowed
**Notes:** Honors the standing 2026-06-24 directive ("don't check/report errors/warnings when VPP isn't used"), which requires touching `firestarter.cpp`.

### How broad?

| Option | Description | Selected |
|--------|-------------|----------|
| VPP-skip directive only | Bound to skipping VPP error/warning checks on read+blank-check (firmware + host parity); RCA but don't fix 0x08/flash4 in fw | ✓ |
| VPP-skip + active shared-pin read | Also actively drive the 0x0B shared OE/VPP pin to a clean read level | |
| All firmware-rooted defects | Attempt fw fixes for VPP-skip + 0x0B shared-pin + 0x08 + flash4 | |

**User's choice:** VPP-skip directive only
**Notes:** Minimal, lowest-risk firmware change.

---

## 2516 / GRAD-03 attempt

| Option | Description | Selected |
|--------|-------------|----------|
| Read-stabilize gates write | If read stabilizes after the fix, write; else defer cleanly | |
| Read-revalidate only, never write | Never write the irreplaceable 2516 this phase even if read stabilizes; GRAD-03 stays deferred | ✓ |
| Attempt write if at all readable | Push to close GRAD-03 now even on a marginal read | |

**User's choice:** Read-revalidate only, never write
**Notes:** Maximally protect the single irreplaceable part. GRAD-03 write proof / FUT-03 stay a documented best-effort deferral regardless; SC#4 cannot be satisfied by design.

---

## FIX-01 defect scope

### FM1608 (d) blank-check tooling gap

| Option | Description | Selected |
|--------|-------------|----------|
| Fix host-side this phase | Close the FRAM (0x40) blank-check 'Empty input' gap host-side, pin with a test | ✓ |
| RCA + defer | Document but defer the fix | |

**User's choice:** Fix host-side this phase

### RCA depth for (a) 0x08 AM27C020 + (c) W29C040 flash4

| Option | Description | Selected |
|--------|-------------|----------|
| Documentary RCA, defer fix | Root-cause from existing evidence + code/datasheet; no new bench run | |
| RCA + confirmatory re-bench | Re-bench (a)/(c) on Leonardo+Rev2.0 to confirm root cause before deferring; may upgrade to a fix if trivial | ✓ |

**User's choice:** RCA + confirmatory re-bench

### Fold matching todos?

| Option | Description | Selected |
|--------|-------------|----------|
| VPP-skip-on-read todo | The FIX-01 firmware fix (score 0.9, resolves_phase 84) | ✓ (Claude's discretion) |
| flash4 page-size CR-01 todo | The W29C040 (c) defect's named root-cause tracker | ✓ (Claude's discretion) |

**User's choice:** "you decide" → Claude folded both (VPP-skip = the D-11 fw fix; flash4 CR-01 = the D-31 (c) tracker).

---

## Audit + close posture

### Cosmetic DB electrical.type labels (SST39SF040, FM1608)

| Option | Description | Selected |
|--------|-------------|----------|
| Accept as-is, document | Record as cosmetic observations; no DB edit | |
| Edit DB to correct labels | Fix the strings, re-run check_dispatch/diff_db + host suite | ✓ |

**User's choice:** Edit DB to correct labels
**Notes:** Claude flagged the load-bearing HOW-constraint — `electrical.type` is codegen'd by `build_db.py` and feeds FLAG_CAN_ERASE (`ic_layout.py`); the edit must be at the build_db layer, verified label-only via `diff_db.py`, with no CAN_ERASE/dispatch perturbation (D-40).

### REWR-01/02/04 traceability cleanup

| Option | Description | Selected |
|--------|-------------|----------|
| Annotate FAIL dispositions | Update REQUIREMENTS.md rows with silicon disposition; fix UV-01..04 checkbox drift | ✓ |
| Leave as-is | Evidence already records the FAILs; don't touch traceability | |

**User's choice:** Annotate FAIL dispositions

### Decode-audit artifact form

| Option | Description | Selected |
|--------|-------------|----------|
| New audit doc | Dedicated `.planning/v1.15/DECODE-AUDIT.md` | ✓ |
| Append to EVIDENCE | Add a consolidated section to EVIDENCE.md | |

**User's choice:** New audit doc

---

## Claude's Discretion

- DECODE-AUDIT.md structure/layout and cross-reference style.
- The exact mechanism keying the firmware VPP-skip gate (op type vs flag bits vs VPP-driving step),
  keeping host↔firmware parity.
- Test names/placement for the FM1608 fix and any firmware native test.
- Driver choice for the (c) W29C040 256B-page retry (`write -b` vs `dev write-cycle`).
- Bench session order of operations.
- Folding of both matching todos (operator delegated).

## Deferred Ideas

- 2516 write proof / GRAD-03 / SC#4 / FUT-03 close — best-effort deferral (read revalidation only).
- Deeper 0x0B shared-pin firmware fix; 0x08 AM27C020 write fix; W29C040 flash4 256B-page fix
  (RCA + re-bench, fix-if-trivial else defer / reopen Phase-74 Wave-2).
- REWR-02 positive 0x08 PASS → FUT-05. Firmware versioning/beta-cut → milestone-close mechanic.
- v1.9 read-bug RCA (FUT-C); 2516 upstream into build_db.py (FUT-B).
