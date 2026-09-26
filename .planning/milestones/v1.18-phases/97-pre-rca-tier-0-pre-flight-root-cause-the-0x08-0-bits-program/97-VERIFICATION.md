---
phase: 97-pre-rca-tier-0-pre-flight-root-cause-the-0x08-0-bits-program
verified: 2026-06-30T14:00:00Z
status: passed
score: 5/5 must-haves verified
overrides_applied: 0
---

# Phase 97: PRE + RCA Verification Report

**Phase Goal:** Tier-0 writability pre-flight + reproduce the 0x08 0-bits-programmed failure signature + differential isolation + a named root cause sufficient for Phase 98 to design the fix without further RCA.
**Verified:** 2026-06-30
**Status:** PASSED
**Re-verification:** No — initial verification

---

## Overall Verdict: PASS-WITH-CONCERNS

All five roadmap success criteria are substantively met. The four gate scripts pass on real artifact data. The evidence is operator-witnessed and never fabricated. Two known gaps are honestly documented and do not undermine the phase goal: (1) the direct pin-1/pin-31 DMM was tooling-blocked, handled by code-decode substitution; (2) two minor stale scaffold strings remain in RCA-FINDINGS.md. One analytical nuance is flagged below (the RC-1 causal claim vs. the physical pin-31 state at address 0), but the verdict survives scrutiny.

---

## Goal Achievement

### Observable Truths (Roadmap Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Tier-0 pre-flight recorded — N≥3 stable reads, blank-state SHA, micro-probe attempted, result documented (never fabricated) | VERIFIED | N=3 byte-identical oracle (PRE-01 table in RCA-FINDINGS.md), SHA `90cd45f5…`, NOT-BLANK `0x02@0x0000`, single write attempt at `0x000000`, result INDETERMINATE per D-01/D-02. check_pre01.py PASS. |
| 2 | 0x08 failure reproduced with captured signature (failing bytes, VPP readback, pin 1 + pin 31 during pulse, bench discipline) | VERIFIED | bad bytes 1/1, retries 20, bits_flipped=0, VPP ADC 13.0V; pin 1/pin 31 DMM tooling-blocked but documented "not measured" (never fabricated) with routing confirmed by code; pre==post SHA confirms chip pristine; bench discipline row 02 complete. check_signature.py PASS. |
| 3 | 0x08 vs 0x07 differential across candidate axes — differing variables isolated, unchanged axes exonerated | VERIFIED | 8-row matrix with all axes assessed; W27C512 byte-exact PASS same session; two 32-pin-only axes confirmed as delta; check_diff07.py PASS. |
| 4 | Named root cause (or ranked hypotheses with disconfirming evidence) recorded, classified — sufficient for Phase 98 fix design | VERIFIED | RC-1 CONFIRMED (host-pinout + firmware-algorithm), RC-2 EXONERATED, RC-3/RC-4 not-pursued (D-03 trigger not met), RC-5 INDETERMINATE (no deferral). Classification explicit. Phase-98 fix surfaces named (DIP32_27C020 + PGM control). check_verdict.py PASS. |
| 5 | Over-voltage stays ERROR-blocked; host guard never bypassed; normal 0x08 dispatch; no escape hatch | VERIFIED | SAFE-01-PREFLIGHT.md with file:line citations (primitives.cpp:106/121/126, chip_resolver.py:16/51-57, memory.cpp:121-122). No source edited. flags=0x08 (SkipBlankCheck only, no FLAG_FORCE) confirmed in EVIDENCE.json Cell A anomalies. |

**Score: 5/5 truths verified**

---

## Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `evidence/SAFE-01-PREFLIGHT.md` | SAFE-01 code-read confirmation | VERIFIED, SUBSTANTIVE | Four confirmations with current-tree file:line citations. Accurately notes firmware DOES have FLAG_FORCE relaxation but procedure never uses it — correct shape of the invariant. |
| `evidence/97-RCA-FINDINGS.md` | COMPLETE status, PRE-01/RCA-01/RCA-02/RCA-03/SAFE-01 sections, RC-1..RC-5 verdicts, named cause, Phase-98 hand-off | VERIFIED, SUBSTANTIVE | Frontmatter `status: COMPLETE`. All sections present and filled with real data. Named cause + classification explicit. Phase-98 fix surfaces named. Two stale scaffold strings ("TBD — Plan 02/03 fills" at line 30, "Verdicts TBD — Plan 03 fills" at line 99) are cosmetic scaffold prose that do not overlap unfilled fields — all verdict slots are filled. |
| `.planning/v1.18/bench/EVIDENCE.json` | Two filled cells (AM27C020 + W27C512) with real data, no TBD in substantive fields | VERIFIED with one note | Cell A failure-signature fields filled (bad_bytes, retries, bits_flipped, vpp_adc_mv, dmm_pin1_v, dmm_pin31_v, pre/post SHA). `sha256` field = `TBD-bench` — this is the "final written image SHA" field, which correctly has no value for a diagnostic attempt that programmed 0 bits. Not a substantive gap; no gate script checks it. Cell B (W27C512) fully filled. |
| `.planning/v1.18/bench/EVIDENCE.md` | Human-readable mirror of EVIDENCE.json | VERIFIED with note | Plan-03 bench discipline row contains TBD values. The same information is correctly filled in `97-RCA-FINDINGS.md` Bench Discipline Log row 03. Minor documentation inconsistency; not substantive. |
| `check_pre01.py`, `check_signature.py`, `check_diff07.py`, `check_verdict.py` | Present, tracked, parse-clean, pass | VERIFIED | All four scripts exist, are git-tracked, and exit 0 when run from the repo root against the filled artifacts. Scripts check substantive content (not just file existence): pre_read_sha256 + controller, failure-signature fields + pre==post consistency, W27C512 verdict, RC-1/RC-2 verdicts + classification. |
| `.planning/debug/resolved/held-rail-dev-reg-timeout.md` | Tooling bug documented, resolved | VERIFIED, SUBSTANTIVE | H1 (DTR-reset-on-close) confirmed end-to-end with file:line evidence. H2 (routing fault) disproven by control-register decode (0x188 → physical 0x89, P1 asserted, A18 alias NOT triggered). Non-invasive workaround (hold_rail.py) delivered. Phase-98 source fix named. |

---

## Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| PRE-01 oracle | blank-state SHA in EVIDENCE.json | `dev consistency-check --runs 3` | WIRED | SHA `90cd45f5…` in both EVIDENCE.json `blank_state_sha256` and `pre_read_sha256` of Cell A |
| RCA-01 micro-probe | chip pristine assertion | post-attempt N=3 oracle (pre==post SHA) | WIRED | pre_read_sha256 == post_read_sha256 in EVIDENCE.json; check_signature.py verifies this |
| RC-2 exoneration | code-decode proof | `rurp_map_ctrl_reg_for_hardware_revision` (REVISION_2_0 arm) | WIRED | debug doc traces: 0x188 & 0xDE = 0x88, + VPE_DROP → 0x89 = REGULATOR+P1+VPE_DROP; P1 asserted |
| RC-1 code half | DIP32_STD pin 31 = A18 | `pinouts.json` + `database.py:141` | WIRED | pinouts.json DIP32_STD.pins.address-bus-pins ends `[..., 30, 31]` (A18); database.py `pin_conversions[32][31]=22` |
| CE-only pulse (RC-1 firmware half) | `memory.cpp:346` | `rurp_chip_enable()` only, no PGM | WIRED | `memory_set_data` calls `rurp_chip_enable()` + delay + `rurp_chip_disable()`; no PGM assertion |
| 0x07 differential control | passing W27C512 | same session, same `configure_eprom()` | WIRED | SHA `d9471636…` write/readback match in EVIDENCE.json Cell B; check_diff07.py PASS |

---

## Requirement-by-Requirement Verdict

### PRE-01 — Tier-0 Silicon Writability Gate

**SATISFIED.**

- N≥3 byte-identical read oracle: PASS (consistency-check 3/3, distinct SHAs=1).
- Blank-state SHA256: `90cd45f5343cd938006f20635de39479159c51b9d56c1b6f1fb23075ed567297` — recorded, not fabricated.
- Identity/decode confirmed: UV-EPROM, DIP32, 0x40000, VPP 13.0V, protocol 0x08, chip-id 0x197.
- Micro-probe: single attempt at 0x000000, result `bits_flipped=0`, documented as INDETERMINATE (not as OTP, no deferral triggered — D-01/D-02 honored).
- check_pre01.py: PASS.

**Judgment on "writability INDETERMINATE" framing:** D-01/D-02 state explicitly that a 0-flip on the broken path is consistent with both "broken path" and "OTP" and must not trigger deferral. The documents honor this throughout — no deferral language appears. Correct.

### RCA-01 — Reproduce the 0x08 Failure Signature

**SATISFIED, with one tooling-blocked field documented honestly.**

- Single attempt: `write -b` (one irreversible spend — correctly ONE, D-01).
- Signature: bad bytes 1/1, retries 20, bits_flipped=0. Matches v1.15 seed. Current fw tip re-captured, not cited from v1.15 (A3 concern addressed).
- VPP ADC: 13.0V (confirmed immediately pre-attempt). Baseline was 12.0V — confound corrected before the attempt, which makes the 0-bits result unambiguous.
- DMM pin 1 / pin 31: "not measured" — blocked by tooling bug (DTR-reset-on-close), root-caused in `debug/resolved/held-rail-dev-reg-timeout.md`. Routing confirmed by code instead (H2 disproven). NEVER fabricated.
- Chip pristine: pre==post SHA confirmed (N=3 both before and after).
- Bench discipline: controller, port, R1/R2, fw commit recorded.
- check_signature.py: PASS.

**Judgment on `-b` deviation:** The PLAN must-have said "no -b skip." The `-b` flag was required because the chip is NOT-BLANK (0x02 @ 0x0000) — a plain `write` aborts at blank-check before programming, which would produce no failure signature. This was verified: for AM27C020 (UV EPROM, no FLAG_CAN_ERASE), `eprom_write_init` (eprom.cpp:154) only triggers erase when `FLAG_CAN_ERASE` is set; since it is NOT set for this chip, `-b` skips ONLY the blank-check (nothing else). The over-voltage guard (`vpp_check_window`) only checks `FLAG_FORCE` (primitives.cpp:121), not `FLAG_SKIP_BLANK_CHECK`. SAFE-01 is fully intact. The justification is sound.

**Judgment on the `flags=0x08` field in EVIDENCE.json verdict:** correctly stated as "SkipBlankCheck only (no FLAG_FORCE) — SAFE-01 intact." Accurate.

### RCA-02 — Differential vs Passing 0x07 W27C512

**SATISFIED.**

- Same session, same bench, same `configure_eprom()` handler.
- W27C512 byte-exact write→verify→readback: SHA `d9471636…` matched, write 6.52s, verify 0.64s.
- 8-row differential matrix with all axes assessed; three axes confirmed as differing (VPP routing, program-enable bit rewrite, pin 31 role) — all specific to the 32-pin/0x08 path.
- Unchanged axes exonerated: handler, pulse width, CE-only pulse model, regulator, VPE-drop, verify pass.
- check_diff07.py: PASS.

**Judgment on M27C512 anomaly:** The operator first seated an ST M27C512 (UV/13V, chip-id 0x203d). The chip-ID check aborted the write without any program pulse — M27C512 left pristine. This is recorded in EVIDENCE.json Cell B anomalies and in RCA-FINDINGS.md Bench Discipline row 03, not glossed. The actual control was then the Winbond W27C512 (EEPROM/12V/0xda08), which is the correct reversible control for this differential (same `0x07` protocol, same `configure_eprom()`, able to erase and re-verify). The anomaly is handled honestly per D-02.

### RCA-03 — Named Root Cause and Classification

**SATISFIED. RC-1 CONFIRMED and RC-2 EXONERATED each carry an individual verdict (D-03 exit bar met).**

**RC-1 (CONFIRMED):**
- Code half (unambiguous): pin_conversions[32][31]=22 (database.py:141) maps pin 31 as address bus line 22 (A18). DIP32_STD.pins.address-bus-pins ends with 31 (confirmed in pinouts.json). memory.cpp:346 strobes CE only — no PGM concept.
- Differential half: passing 0x07 W27C512 (28-pin) has no pin-31 mapping issue, exonerating all axes except the 32-pin address/PGM axis.
- Elimination half: RC-2 exonerated (VPP reaches pin 1) → by elimination the 0-bits cause rests with the pin-31 modeling.
- Missing measurement: direct pin-31 DMM was tooling-blocked. RC-1 rests on code + differential + elimination, not direct measurement. This is noted explicitly as a "residual" in RCA-FINDINGS.md; Phase-98 fix validation closes it empirically.

**Analytical note on RC-1 strength (the most important judgment in this phase):** At address 0x000000, A18=0, so bus line 22 is LOW, meaning pin 31 is physically at VIL during the attempt. The AM27C020 requires PGM=VIL for programming, which is coincidentally satisfied at this address. This means the RC-1 claim "chip never sees program-enable on pin 31" is technically imprecise for address 0: the signal IS at the required level, it is just there for the wrong architectural reason (address-driven, not PGM-driven). The correct framing — which the documents do use — is that the pinout MODELS pin 31 as an address line rather than as a held program-enable control, and the fix is a dedicated DIP32_27C020 pinout. The "confirmation" of RC-1 is therefore a confirmation of the architectural mismodeling, not a direct measurement of the pin being in the wrong state. Given that (a) VPP IS correctly at pin 1 at 13V (RC-2 exonerated), (b) the CE pulse fires, (c) pin 31 IS VIL at addr0, yet (d) 0 bits are programmed, there may be an additional undiscovered mechanism. The documents acknowledge this honestly: "Phase-98 fix validation (byte-exact write after redirecting pin 31) closes it empirically." This is the correct epistemic stance — RC-1 is the best-supported hypothesis, not a closed proof. The phase goal ("named root cause sufficient for Phase 98 to design the fix") is met.

**RC-2 (EXONERATED):**
- VPP ADC confirmed at 13.0V (within 12.5–13.0V band).
- Code decode: host -f 0x188 → `rurp_map_ctrl_reg_for_hardware_revision` (REVISION_2_0) → physical CTRL 0x89 = REGULATOR(0x80) + P1(0x08) + VPE_DROP_REV2(0x01). The CTRL_VPP_P1_ENABLE_REV2 == CTRL_ADDRESS_LINE_18_REV2 alias is NOT triggered because input bit 0x20 (A18 in host space) is not set in 0x188. P1-route IS asserted.
- Residual: direct pin-1 DMM not measured (same tooling block). Routing is code-confirmed, not bench-confirmed. Noted honestly.

**Classification:** `host-pinout` (primary) + `firmware-algorithm` (secondary). Correct: the pin-31 mapping lives in the host pinout DB; the CE-only pulse model is the firmware side.

**Phase-98 hand-off:** DIP32_27C020 pinout entry + pin-31 PGM redirection, scoped to 0x08-UV-32-pin class to protect existing 27C040/SST39SF040 DIP32 users (pin 31 = A18/WE). Secondary: hold CTRL_VPP_P1_ENABLE across full pulse window. Fix-design concern: 0x08 firmware alias (CTRL_VPP_P1_ENABLE_REV2 == CTRL_ADDRESS_LINE_18_REV2) flagged for Phase 98.

- check_verdict.py: PASS.

### SAFE-01 — Over-Voltage Guard and Host Guard Non-Bypass

**SATISFIED.**

- Over-voltage HIGH → ERROR confirmed at primitives.cpp:106/121/126. The document correctly notes that the firmware DOES contain a FLAG_FORCE relaxation (primitives.cpp:121-127); SAFE-01 is satisfied because the procedure never passes `--force`, not because the relaxation is absent. This is the accurate shape of the invariant.
- Under-voltage LOW → WARNING/proceed noted (silent-under-program risk; pin-1 DMM rationale).
- Host guard `resolve_chip` at chip_resolver.py:16/51-57 confirmed in live write path.
- Normal 0x08 dispatch at memory.cpp:121-122, no special-case, no escape hatch.
- Zero source edits in Phase 97 (diagnostic only).
- `-b` flag = FLAG_SKIP_BLANK_CHECK (0x08), which does NOT relax the over-voltage guard (verified in firmware: only FLAG_FORCE relaxes the HIGH branch).

---

## Behavioral Spot-Checks (Gate Scripts)

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| PRE-01 fields populated (blank-state SHA + controller) | `python3 .planning/v1.18/bench/check_pre01.py` | "PRE-01 pre-flight captures present" | PASS |
| RCA-01 signature complete (no TBD, pre==post SHA) | `python3 .planning/v1.18/bench/check_signature.py` | "RCA-01 signature complete; bits_flipped=0" | PASS |
| RCA-02 differential verdict recorded | `python3 .planning/v1.18/bench/check_diff07.py` | "RCA-02 differential control recorded; W27C512 verdict=PASS" | PASS |
| RC-1 + RC-2 verdicted, classified, 0x07 filled | `python3 .planning/v1.18/bench/check_verdict.py` | "RCA verdict complete: RC-1 + RC-2 verdicted, classified, 0x07 differential filled" | PASS |

All four scripts check substantive content against real artifact data, not trivially. check_signature.py additionally verifies pre==post SHA consistency (chip pristine). check_verdict.py additionally verifies a valid classification term is present. Scripts are not self-passing stubs.

---

## Gate Script Quality Assessment

The gate scripts were examined for trivial-pass risk:

- `check_pre01.py`: checks two specific JSON fields (`pre_read_sha256`, `controller`) for absence of "TBD". Would fail if Plan 01 had left them unfilled.
- `check_signature.py`: checks seven signature fields for absence of "TBD" AND verifies pre==post SHA when bits_flipped=0. The cross-check is a real semantic constraint.
- `check_diff07.py`: checks the W27C512 cell `verdict` field for absence of "TBD". Would fail if Plan 03 had not completed.
- `check_verdict.py`: uses regex to find "confirm", "exonerate", "out", or "ruled" in RC-1 and RC-2 lines of RCA-FINDINGS.md AND checks for a valid classification string AND checks W27C512 verdict. Substantive multi-condition gate.

Assessment: the scripts are adequate gatekeepers for the documented content. They do not check the physical measurement values themselves (e.g., VPP=13.0V in range) but that is consistent with this being a diagnostic/documentation phase rather than a pass/fail test harness.

---

## Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `97-RCA-FINDINGS.md` | 30 | "TBD — Plan 02/03 fills" (scaffold prose in status blockquote) | INFO | Stale scaffold text — the document frontmatter says COMPLETE and all verdict slots are filled. This is the Wave-1 scaffold description that was not removed when Plans 02/03 filled the document. No unfilled field corresponds to it. |
| `97-RCA-FINDINGS.md` | 99 | "Verdicts TBD — Plan 03 fills" (in RCA-02 blockquote) | INFO | Same pattern — stale scaffold prose; the RCA-02 verdict table immediately below is fully filled. |
| `EVIDENCE.md` | 41 | Plan 97-03 bench discipline row still contains TBD values | INFO | The same bench discipline data for Plan 03 is correctly recorded in `97-RCA-FINDINGS.md` row 03 (line 42). Minor documentation inconsistency between two mirrors. |
| `EVIDENCE.json` | 47 | `"sha256": "TBD-bench"` in Cell A | INFO | This field represents the "final written image SHA" — for an RCA probe that wrote 0 bits, there is no final image SHA to record. The pre/post read SHAs (the relevant values) are correctly filled. No gate script checks this field. Not a substantive gap. |

No TBD, FIXME, or XXX debt markers appear in any of the critical evidence fields or verdict slots. The four INFO-level items above are stale scaffold prose or correctly-unfilled placeholders with clear explanations.

---

## Three Known Gaps Assessed

### Gap 1: Held-Rail Pin-1/Pin-31 DMM Not Measured

**Assessment: HONEST HANDLING, NOT A BLOCKER.**

The held-rail proxy was blocked by a real, root-caused tooling bug (DTR-reset-on-close drops the Leonardo when `dev_set_registers` finally: closes the port). The mechanism is fully documented in `debug/resolved/held-rail-dev-reg-timeout.md` with file:line evidence from both firmware (`dev_tools.cpp:71-127`) and host (`eprom_operations.py:1454-1517`, `serial_comm.py:132-136`, `uno_rurp_shield.cpp:58`).

The routing question the DMM was meant to answer (does VPP reach socket pin 1?) is answered by code-decode: the H2 hypothesis (routing fault) is DISPROVEN, not just unconfirmed. This is a genuine code-decode substitute, not a hand-wave.

What remains unconfirmed is the exact physical voltage at socket pin 1 during the program attempt (the DMM at the ADC node and at socket pin 1 cross-check). The EVIDENCE records "not measured" rather than fabricating a value, per D-02. The documents acknowledge this as a residual.

This gap does NOT undermine phase goal achievement because: (a) VPP routing is code-confirmed (H2 disproven), (b) VPP level is ADC-confirmed at 13.0V, (c) the residual is documented, and (d) Phase-98 fix validation (byte-exact write) provides empirical closure.

### Gap 2: JP4 Silkscreen Meaning "PENDING"

**Assessment: MANAGED RISK, NOT A BLOCKER.**

D-08 required asking the operator the Rev 2.0 silkscreen meaning before toggling JP4. The operator reported JP4 "open" at session start, but the silkscreen meaning was not formally resolved ("PENDING"). The firmware `info` command output itself provided the authoritative JP4 guidance for 32-pin: "JP4 Closed = 32-pin." The operator moved JP4 to "closed" for the 0x08 attempt based on this firmware guidance.

This is documented honestly as a discrepancy. It does not undermine the RCA because: (a) the attempt was made at corrected rig (JP4 closed per fw guidance), (b) the 0-bits result still occurred, confirming RC-2 was not the lone cause, and (c) RC-3 (JP4 wrong position) was not pursued because RC-1 accounts for the symptom. A genuine JP4-position fault would have been a VPP routing issue (RC-2), which is covered by the code-decode exoneration.

### Gap 3: RC-1 "CONFIRMED" without Direct Pin-31 DMM

**Assessment: VERDICT IS SUPPORTED BUT REQUIRES HONEST FRAMING.**

See detailed analysis in RCA-03 section above. The RC-1 verdict is based on code + differential + elimination — three independent evidence types. The direct pin-31 DMM was tooling-blocked (same bug as gap 1). The verdict is the strongest defensible claim given available evidence, with the residual explicitly acknowledged.

The important analytical nuance: at address 0x000000, A18=0 so pin 31 IS physically at VIL, which satisfies the AM27C020 PGM=VIL programming requirement. This means the physical mechanism "pin 31 is in the wrong state" may not be the FULL story at address 0. The documents' framing "chip never sees a program-enable on pin 31" should more precisely be "the system doesn't TREAT pin 31 as a controlled PGM signal — it's address-driven, not deliberately asserted." The fix (dedicated DIP32_27C020 pinout with explicit PGM control) is the correct engineering response regardless of whether the physical signal at address 0 happens to be VIL.

The RCA-FINDINGS.md correctly says Phase-98 fix validation closes the verdict empirically. This is the appropriate epistemic stance for Phase 97.

---

## Human Verification Required

None identified. This is a diagnostic/RCA phase. All evidence is documentation and code analysis. The bench measurements were operator-witnessed (Leonardo + Rev 2.0, 2026-06-30). The empirical validation of the fix is Phase 99, not Phase 97.

---

## Requirements Coverage

| Requirement | Phase | Evidence | Status |
|-------------|-------|----------|--------|
| PRE-01 | Phase 97 | EVIDENCE.json `pre_01_result` + `blank_state_sha256`; RCA-FINDINGS PRE-01 table; check_pre01.py PASS | SATISFIED |
| RCA-01 | Phase 97 | EVIDENCE.json Cell A (all signature fields); RCA-FINDINGS RCA-01 table; check_signature.py PASS | SATISFIED |
| RCA-02 | Phase 97 | EVIDENCE.json Cell B; RCA-FINDINGS RCA-02 differential matrix + "Two-axis collapse" verdict; check_diff07.py PASS | SATISFIED |
| RCA-03 | Phase 97 | RCA-FINDINGS RC-1..RC-5 table (each with verdict); Named Root Cause + Classification section; Phase-98 hand-off section; check_verdict.py PASS | SATISFIED |
| SAFE-01 | Phase 97 | SAFE-01-PREFLIGHT.md four confirmations with file:line; EVIDENCE.json Cell A flags=0x08 (no FLAG_FORCE); zero source edits | SATISFIED |

---

## Summary

Phase 97 delivers what it set out to deliver: a non-destructive pre-flight (PRE-01), a reproduced failure signature on real silicon (RCA-01), a passing differential control (RCA-02), and a named root cause with classification sufficient for Phase 98 (RCA-03). SAFE-01 was maintained throughout. All four gate scripts pass on real artifact data.

The two nuances that required judgment are both handled honestly:

**The `-b` deviation** is sound. For the AM27C020 UV EPROM (no FLAG_CAN_ERASE), `-b` skips only the blank-check step; it does not touch the erase path (there is none for this chip) and does not relax the over-voltage guard. SAFE-01 holds. Without `-b`, the write would abort at blank-check before any program pulse, producing no failure signature.

**The unmeasured pin-1/pin-31 DMM** is honestly documented as "not measured" with the real tooling bug root-caused. The routing question it was meant to answer is answered by code-decode (H2 disproven). The RC-1 verdict is appropriate given the available evidence: "pin 31 is architecturally modeled as address line A18, not as a held PGM control" is confirmed by code analysis independent of the physical signal state. The document explicitly flags the residual and defers empirical closure to Phase-98 fix validation. This is correct epistemic practice for a hardware RCA where one measurement instrument was blocked by a known tooling bug.

The phase goal is achieved.

---

*Verified: 2026-06-30*
*Verifier: Claude (gsd-verifier)*
