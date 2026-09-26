---
phase: 49-framing-mechanism-decision-cobs-0x00-vs-slip-0xc0
verified: 2026-06-01T00:00:00Z
status: passed
score: 6/6 must-haves verified
human_verification_signoff: "Operator approved all 3 reasoning-soundness items 2026-06-01 (henrik@predictly.se) — SAFE-01 chain, decision evidence-backing, frozen-contract completeness accepted."
overrides_applied: 0
human_verification:
  - test: "Read the SAFE-01 resolution section (§1.2–1.4 of .planning/v1.10-FRAMING-DECISION.md). Confirm that it proves host 0x00-silence in the mode-transition window via all three sub-claims (A: pyserial flush() guarantees physical TX, B: atomic-write mandate, C: Phase 51 frame-decoder consumption contract), and that the scope is explicitly the Phase 51 command-channel case."
    expected: "Each sub-claim is confirmed with a sound reasoning chain citing specific file + line references (not bare assertions). The section lands a definitive outcome: proof conclusive, COBS eligible."
    why_human: "The SAFE-01 static proof is a reasoning chain over code architecture — grep can verify the keywords are present (Q2, Q3, bus-aliasing, com_mode, flush, init_programmer) but cannot assess whether the argument is logically sound or whether the cited sub-claim conclusions are correctly derived from the code evidence."
  - test: "Read the Decision statement (§3 of .planning/v1.10-FRAMING-DECISION.md). Confirm it cites the scored matrix ranking as the basis for the COBS selection — not a bare 'we picked COBS'."
    expected: "The decision statement references the aggregate score (11/12 vs 10/12), names which criteria COBS won on (byte-exactness, overhead) and which SLIP won on (simplicity), and explicitly states D-04 (inconclusive->SLIP) does not apply because the proof is conclusive."
    why_human: "Whether the decision cites the matrix ranking sufficiently versus making a bare assertion is a judgment call over the prose quality, not a string match."
  - test: "Read the Frozen Frame Contract (§4 of .planning/v1.10-FRAMING-DECISION.md). Confirm all D-06 fields are present and unambiguous: delimiter byte, escape/run-length scheme, exact frame-layout field table with CRC8 placement, explicit len_u16-retention decision, per-file change map naming all four files, log/telemetry-unchanged statement, and the CRC8-before-parse mandate."
    expected: "All fields are present and specific enough that a Phase 50 executor can implement without re-opening any design question. No 'TBD' or open choices remain in the contract."
    why_human: "Completeness and unambiguity of a design contract requires reading comprehension — grep can confirm keywords are present but cannot evaluate whether the contract is sufficient for implementation."
---

# Phase 49: Framing Mechanism Decision Verification Report

**Phase Goal:** Resolve the deferred framing-mechanism choice (COBS 0x00 vs SLIP 0xC0) and the 0x00 bus-aliasing safety question (v1.9-COBS-DECISION §2.0 / Open Q2/Q3) before any implementation commits to a delimiter.
**Verified:** 2026-06-01
**Status:** human_needed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | The ADR names exactly one chosen mechanism (COBS 0x00 or SLIP 0xC0) justified by a scored matrix, not a bare assertion | VERIFIED | `v1.10-FRAMING-DECISION.md` §3 names "COBS 0x00 (streaming hand-rolled, per v1.9-COBS-DECISION §4.3)" and §2 contains a 5-row scored matrix (safety, byte-exactness, simplicity, overhead, aggregate) with COBS 11/12 vs SLIP 10/12. Decision statement cites matrix ranking explicitly. |
| 2 | The SAFE-01 0x00 bus-aliasing risk is resolved: either a static proof of host 0x00-silence in the mode-transition window (COBS) or explicit SLIP selection per D-04 | VERIFIED (automated) / UNCERTAIN (reasoning quality) | All four required grep tokens present: Q2, Q3, bus-aliasing, com_mode, flush, init_programmer. Three sub-claims documented (A: pyserial flush(), B: atomic-write mandate, C: Phase 51 frame-decoder consumption contract). Proof declared conclusive. Human check required for soundness of the reasoning chain. |
| 3 | The ADR confirms the chosen mechanism is streaming-encodable with no second ~512 B buffer, fits the ~545 B Uno ceiling, and layers on unchanged CRC8-CCITT poly 0x07 | VERIFIED | §4.5 explicitly states: "Both the COBS encoder and decoder operate streaming with no second ~512 B encode buffer." RAM overhead confirmed as ~6 bytes stack. "~545 B free-RAM Uno ceiling (measured 2026-06-01 at 1503/2048 B used)" cited. CRC8-CCITT poly 0x07 PROGMEM table cited at rurp_serial_utils.cpp lines 109-131. |
| 4 | The ADR contains a per-file change map naming all four files (rurp_serial_utils, serial_comm, frame_parser, test_messages) | VERIFIED | §4.6 contains a 4-row table. All four files named: rurp_serial_utils.cpp (Phase 50), serial_comm.py (Phase 50+51), frame_parser.py (Phase 50), test_rurp_log_id.cpp (Phase 52). Each row specifies the change required per file. |
| 5 | The ADR cross-references v1.9-COBS-DECISION.md and supersedes its DEFER line for the mechanism question | VERIFIED | Header "Supersedes: .planning/v1.9-COBS-DECISION.md DEFER line for the mechanism question". §5 quotes the exact DEFER line text and lists three Q-closures: §2.0, §5 Q2, §5 Q3. Cross-references appear 9 times throughout the document. |
| 6 | The frame contract mandates firmware verify CRC8 BEFORE handing the decoded payload to the JSON parser (Phase 51 design constraint, T-49-01) | VERIFIED | §4.4 "CRC8-Before-Parse Security Mandate (V5 — Phase 51 Design Constraint)" states: "The firmware MUST verify CRC8 BEFORE handing the decoded frame payload to the JSON parser." grep -qiE "CRC8.*(before|prior).*(json|pars)" PASSES. |

**Score:** 6/6 truths verified (5 fully automated, 1 with structural-evidence confirmation pending human reasoning-chain review)

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `.planning/v1.10-FRAMING-DECISION.md` | Binding framing-mechanism ADR + frozen D-06 frame contract containing "v1.9-COBS-DECISION" | VERIFIED | File exists, 268 lines. All four plan-frontmatter artifact checks pass: `contains: v1.9-COBS-DECISION` confirmed. No fenced code blocks (none found by grep). |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `.planning/v1.10-FRAMING-DECISION.md` | `.planning/v1.9-COBS-DECISION.md` | supersession cross-reference of the DEFER line (D-05); pattern: `v1.9-COBS-DECISION` | VERIFIED | grep -q "v1.9-COBS-DECISION" PASSES. 9 occurrences including header supersession declaration, §5 full supersession note quoting the DEFER line verbatim, and three §5 Q-closure bullets. |
| `.planning/v1.10-FRAMING-DECISION.md` | Phase 50/51/52 implementation | per-file change map naming all four target files; pattern: `rurp_serial_utils|serial_comm|frame_parser|test_messages` | VERIFIED | grep -qE pattern PASSES. All four files appear in §4.6 table with phase assignments and change descriptions. |

---

### Data-Flow Trace (Level 4)

Not applicable. This is a documentation-only phase. The single deliverable is a planning document (`.planning/v1.10-FRAMING-DECISION.md`). No dynamic data rendering.

---

### Behavioral Spot-Checks

Not applicable. This phase produces no runnable code. The validation contract is document-assertion based (bash + grep), all of which were run above.

---

### Probe Execution

Not applicable. No probe scripts exist or are referenced for this phase. The PLAN and VALIDATION documents explicitly state "no test runner; document-assertion based."

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| SAFE-01 | 49-01-PLAN.md | SERIAL_ON_IO 0x00 bus-aliasing risk resolved and documented — either static proof of host 0x00-silence OR explicit SLIP 0xC0 adoption | SATISFIED | REQUIREMENTS.md marks SAFE-01 as `[x]` with annotation "SATISFIED: static proof conclusive (Phase 49 Plan 01 — .planning/v1.10-FRAMING-DECISION.md)". Traceability table shows "SAFE-01 | Phase 49 | Complete (2026-06-01)". ADR §1 contains the static proof with three sub-claims; §1.4 declares "proof is conclusive." |

---

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| (none) | — | No TBD, FIXME, XXX, TODO, placeholder, or stub patterns found in `.planning/v1.10-FRAMING-DECISION.md` | — | — |

No anti-patterns detected. The ADR contains no fenced code blocks (which would be a mild protocol violation per task spec), no debt markers, and no deferred open questions.

---

### Human Verification Required

Three manual reviews are required. These were deferred by the planner in `49-VALIDATION.md` under "Manual-Only Verifications" and are confirmed as structurally sound by automated checks but require judgment to pass.

#### 1. SAFE-01 Reasoning Chain Soundness

**Test:** Read §1.2 (Firmware Half — com_mode Gate), §1.3 (Host Half — Three Sub-Claims), and §1.4 (Proof Outcome) of `.planning/v1.10-FRAMING-DECISION.md`.
**Expected:** Each of the three sub-claims (A: pyserial flush() maps to POSIX tcdrain() — physical TX guaranteed; B: atomic-write mandate closes the split-write window by design contract; C: Phase 51 frame decoder must consume the 0x00 before calling the JSON parser — design contract) is confirmed with a sound reasoning chain citing file + line references. The proof is scoped explicitly to the Phase 51 command-channel case (not the moot Phase 50 data-path case). The outcome is declared conclusive.
**Why human:** The SAFE-01 proof is a multi-step architectural argument. Automated checks confirmed Q2/Q3/bus-aliasing keywords and sub-claim A/B/C structural presence. Whether the cited code evidence (uno_rurp_shield.cpp lines 70-97, serial_comm.py line 141, firestarter.cpp lines 162-172) actually supports each sub-claim conclusion requires code-reading judgment. Sub-claim C in particular relies on Phase 51 design contracts not yet implemented — the verifier must assess whether these are sufficient commitments.

#### 2. Decision Statement Evidence-Backing

**Test:** Read §3 (Decision Statement) of `.planning/v1.10-FRAMING-DECISION.md`.
**Expected:** The statement cites the aggregate matrix score (11/12 vs 10/12), identifies the per-criterion outcomes (byte-exactness and overhead favor COBS; simplicity favors SLIP; safety is a tie), explicitly notes that D-04 (inconclusive -> SLIP) does not apply because the proof is conclusive, and references D-04/D-05 and the bus-aliasing analysis as required by ROADMAP Success Criterion 1.
**Why human:** Whether the decision statement rises above a "bare assertion" is a prose-quality judgment. Automated check confirmed matrix-ranking language is present. The ROADMAP SC-1 requires the rationale to reference D-04, D-05, and the bus-aliasing analysis specifically — a human must read whether those references appear as substantive rationale or just incidental mentions.

#### 3. Frozen Frame Contract Completeness

**Test:** Read §4.1 through §4.6 of `.planning/v1.10-FRAMING-DECISION.md`.
**Expected:** All D-06 fields are present and unambiguous so Phases 50–52 inherit a concrete contract with no open design questions: (a) delimiter byte (0x00), (b) escape/run-length scheme (COBS streaming, run-length header = run_len+1), (c) exact frame-layout field table with CRC8-CCITT placement (§4.3 table), (d) explicit len_u16 retention decision (removed — §4.3), (e) atomic-write mandate, (f) per-file change map with all four files (§4.6 table), (g) log/telemetry unchanged statement (§4.2), (h) CRC8-before-parse mandate (§4.4). No fields left as TBD.
**Why human:** Structural completeness of a design contract requires end-to-end reading. Automated checks confirmed all D-06 keywords are present. A human must verify that the field table in §4.3 is unambiguous (field widths, encoding, value columns are all specified), that the per-file change map provides sufficient detail for implementation (not just filenames), and that no open design questions were inadvertently deferred.

---

### Gaps Summary

No automated gaps found. All six must-have truths are structurally verified. All four required grep assertions pass. SAFE-01 is marked complete in REQUIREMENTS.md. The ADR file exists at the required path with 268 lines, no fenced code blocks, and all required sections present.

Three human verification items are required per the planner's deliberate deferral in `49-VALIDATION.md`. These items were classified as "Manual-Only Verifications" because they assess reasoning-chain quality and contract completeness — properties that automated grep cannot evaluate. The phase `status: human_needed` reflects this.

---

_Verified: 2026-06-01_
_Verifier: Claude (gsd-verifier)_
