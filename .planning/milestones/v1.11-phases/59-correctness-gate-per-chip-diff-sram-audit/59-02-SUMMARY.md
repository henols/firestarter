---
phase: 59-correctness-gate-per-chip-diff-sram-audit
plan: "02"
subsystem: documentation
tags: [gate-04, sram-audit, nvram-behavioral-truths, two-layer-doc, host-only]
dependency_graph:
  requires: [59-01]
  provides: [GATE-04]
  affects: [firestarter_app/doc/sram-nvram-behavior.md]
tech_stack:
  added: []
  patterns: [two-layer-doc-lockstep (meta-repo planning layer + sub-repo shipped layer)]
key_files:
  created:
    - .planning/phases/59-correctness-gate-per-chip-diff-sram-audit/59-SRAM-AUDIT.md
    - firestarter_app/doc/sram-nvram-behavior.md
  modified: []
decisions:
  - "GATE-04 audit: configure_sram is a near-no-op (LOG_DEBUG_ID_SUB only); no VPP assertion, no regulator enable — firmware safety surface is zero"
  - "BLOCKER-2 guard proof cited as primary host-side safety evidence (0 SRAM chips route to configure_eprom across 743-chip DB)"
  - "DS1225/M48T08 WP# claims carry [ASSUMED] marker (risk LOW — worst case is non-destructive write failure)"
  - "Safety Verdict: no genuine safety issue found; no firmware escalation needed; escalation criterion stated explicitly (audited verdict, not silent dismissal)"
  - "Two-layer lockstep: 59-SRAM-AUDIT.md (meta-repo, investigation-canonical) + sram-nvram-behavior.md (sub-repo, GitHub-visible operator subset)"
metrics:
  duration: "~4 min"
  completed: "2026-06-09"
  tasks_completed: 2
  tasks_total: 2
  files_created: 2
  files_modified: 0
---

# Phase 59 Plan 02: GATE-04 SRAM/NVRAM Audit Summary

GATE-04 delivered in two lockstep documentation layers: a planning-layer audit trail and a
shipped GitHub-visible operator doc, both committed in the same plan wave.

## What Was Built

### Task 1: Planning-Layer Audit Trail (59-SRAM-AUDIT.md)

Created `.planning/phases/59-correctness-gate-per-chip-diff-sram-audit/59-SRAM-AUDIT.md` as
the investigation-canonical (D-04 layer 1) GATE-04 audit trail.

**Firmware Layer Audit finding:** `configure_sram` in `firestarter/src/proms/sram.cpp` is
confirmed a near-no-op — the entire function body is `LOG_DEBUG_ID_SUB(DBG_CONFIGURING_SRAM)`.
No pin configuration, no VPP assertion, no regulator enable. `sram.h` declares only the
function prototype with no additional state.

**Host-Side Dispatch Audit finding:** The BLOCKER-2 guard in `check_dispatch.py` defines
`_SRAM_PROTOCOLS = {0x0E, 0x27, 0x28, 0x29}` and confirms **0 of 743 chips** with these
protocols route to `configure_eprom` (the VPP-asserting handler). This is the primary
host-side safety proof — the firmware near-no-op alone is insufficient; the BLOCKER-2 guard
is the second necessary layer of evidence.

**Three NVRAM Behavioral Truths documented:**

(a) Blank-check limitation: DS1225/DS1230/DS1245/M48T02/M48T08/M48T35/FM1608/FM16W08/FM1808/
    BQ4010/BQ4011 retain data indefinitely (battery/ferroelectric). Never factory-blank.
    Operators must use `-b` (`FLAG_SKIP_BLANK_CHECK`) or accept blank-check failure.

(b) WP# pin behavior: DS1225 class uses hardware WP# pin (pin 26, internally pulled low by
    default — writes enabled). M48T08 class uses software control-register bit 7 (e.g., address
    0x1FF8) that firmware does NOT clear automatically. Both carry [ASSUMED] markers.

(c) RTC-oscillator side effect: Timekeeper NVRAMs (M48T08/M48T35 class) run the 32.768 kHz
    oscillator whenever VCC is present, including during RURP operations. RTC clock advances
    during programming — not a hardware-damage path, but operators must re-set the time after
    programming.

**Safety Verdict recorded:** No genuine safety issue found. No firmware escalation needed.
Escalation criterion stated explicitly: a firmware backlog item would be raised ONLY if a real
safety issue had surfaced (VPP-on-5V-part path found). None was found. Audited verdict, not
silent dismissal.

### Task 2: Shipped Operator Doc (firestarter_app/doc/sram-nvram-behavior.md)

Created `firestarter_app/doc/sram-nvram-behavior.md` as the operator-facing subset (D-04 layer
2). Committed inside the `firestarter_app` submodule on `v1.11-infoic-decode-correctness`.

Mirrors the `pinout-safety-review.md` pattern: title, one-sentence scope, explicit
`Full audit trail:` pointer to `59-SRAM-AUDIT.md`, three behavioral-truth sections, Safety
closing note.

The shipped doc omits the firmware-source quoting and host-side dispatch-proof internals (those
live in the planning layer) and focuses on what an operator must know before programming
NVRAM/SRAM parts.

## Commits

| Layer | Commit | Repository | Content |
|-------|--------|------------|---------|
| Meta-repo task 1 | `6d787cd` | /workspaces (meta) | 59-SRAM-AUDIT.md (249 lines) |
| Submodule task 2 | `d3b7de0` | firestarter_app | sram-nvram-behavior.md (114 lines) |
| Meta-repo submodule bump | `1cccefa` | /workspaces (meta) | gitlink pointer update |

Both layers committed in lockstep. Firmware sub-repo (`firestarter/`) untouched throughout.

## Deviations from Plan

None — plan executed exactly as written.

The two-layer structure, section content, and lockstep commit discipline all followed the
plan specification and the 59-PATTERNS.md analog pattern (`pinout-safety-review.md` /
`58-SR-1-CHECKLIST.md`) exactly.

## Known Stubs

None. Both documents are complete artifacts with no placeholder or TODO content.

## Threat Flags

No new security-relevant surface introduced. This plan creates documentation-only files
(markdown, no code). No network endpoints, auth paths, file access patterns, or schema changes
at trust boundaries.

## Self-Check: PASSED

- `59-SRAM-AUDIT.md`: EXISTS, 249 lines (min 40), all required sections present
- `sram-nvram-behavior.md`: EXISTS, 114 lines (min 30), `59-SRAM-AUDIT` pointer present
- All three truths: blank, WP#, RTC — present in both layers
- DS1225 and M48T08 named in both layers
- `configure_sram` near-no-op finding documented in both layers
- Safety Verdict with no-escalation + escalation criterion: present in 59-SRAM-AUDIT.md
- Safety closing note (no firmware change in v1.11): present in sram-nvram-behavior.md
- [ASSUMED] markers on DS1225/M48T08 behavioral claims: present in both layers
- Commits `6d787cd`, `d3b7de0`, `1cccefa`: all exist in git log
- `firestarter/` sub-repo: untouched (confirmed by git status)
