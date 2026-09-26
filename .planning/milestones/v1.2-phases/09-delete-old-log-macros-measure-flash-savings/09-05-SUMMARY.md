---
phase: 09-delete-old-log-macros-measure-flash-savings
plan: 05
subsystem: phase-close-measurement
tags:
  - logging
  - measurement
  - bench-verification
  - phase-close
  - partial-pending-bench

# Dependency graph
requires:
  - phase: 09-02-atomic-legacy-deletion-and-version-bump
    provides: "Cold-cache build baseline locked at firestarter@ace9274: Uno 22,226 B / Leonardo 24,456 B Flash post-deletion"
  - phase: 09-03-host-comment-refresh
    provides: "Host-side FIRESTARTER_DEV_ALLOW_PRE_V12 rationale comment refreshed post-Phase-9 (firestarter_app@7f9b944)"
  - phase: 09-04-host-stubs-trim
    provides: "Host_stubs_common.inc dead LOG_*_MSG + rurp_log stubs trimmed (firestarter@ace9274)"
provides:
  - "09-MEASUREMENT.md — Phase 9 close milestone artifact (Task 1 of 3 complete; Tasks 2 + 3 pending operator-on-bench)"
  - "LMIG-04 acceptance number: Leonardo Flash 85.3% (24,456 / 28,672 bytes), 4,216 B free — a -3,843-byte (-13.4 pp) reduction vs v1.1 close"
  - "SC#1 PROGMEM exemption audit closed: 12 named-symbol declarations all categorized (MAGIC_PREAMBLE / CRC8_TABLE / json_parser keys + key_parsers[]); 1 inline F() literal (LFW-05 bootstrap)"
  - "SC#2 legacy macro grep gate: 0 hits — LFW-03 closed"
  - "SC#3 host-side fwguard regression: 4/4 PASS (bench native-pass exercise pending Task 2)"
  - "SC#4 Leonardo Flash < 90%: PASS (85.3% with 4,216 B headroom)"
  - "SC#5 Uno Flash recorded: PASS (68.9%, 10,030 B free)"
affects:
  - "Phase 10 DOC-02 milestone-close documentation — will quote the v1.1 → Phase 9 row verbatim into MILESTONES.md"
  - "Phase 9 plan-checker / verifier — must recognise the Pending operator-on-bench placeholders as a known carry-over (similar to Phase 8's pending UAT)"

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "5-column anchor-table extension pattern — 09-MEASUREMENT.md extends 08-MEASUREMENT.md:310-316 with one new close row (Phase 9 close), replacing the prior TARGET/TBD placeholder"
    - "Two-table PROGMEM exemption audit form — (a) named-symbol declarations gate SC#1; (d) inline F() literals informational-only; mutually exclusive by syntactic pattern, no double-counting"
    - "Pending operator-on-bench placeholder convention — bench commands + expected outputs + acceptance criteria pre-filled in the artifact so the operator transcribes observed values inline"

key-files:
  created:
    - .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-MEASUREMENT.md
    - .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-05-SUMMARY.md
  modified: []
  deleted: []

key-decisions:
  - "D-08 honored: BOTH delta rows present in the artifact (Phase 8 → Phase 9 incremental + v1.1 → Phase 9 milestone close)"
  - "D-09 honored: anchor table extends 08-MEASUREMENT.md:310-316 with the Phase 9 close row replacing TARGET/TBD"
  - "RESEARCH.md Risks #5 + #7 honored: both AVR measurements from cold-cache (pio run -t clean before pio run)"
  - "RESEARCH.md Risk #6 honored: byte count is authoritative; percentage reported alongside, rounded to 1 decimal"
  - "RESEARCH.md Risk #8 honored: PROGMEM audit produces TWO mutually-exclusive labeled tables — named-symbol declarations (SC#1 gate) vs inline F() literal sites (exempt)"
  - "Tasks 2 + 3 deferred to operator-on-bench: artifact placeholders carry exact bench commands + acceptance criteria; plan-checker/verifier expected to recognise as known-pending bench step per CONTEXT.md Claude's-Discretion Phase 8 UAT carry-over bundle"

patterns-established:
  - "Phase-close measurement artifact = single source of truth (Phase 10 DOC-02 quotes verbatim; no re-running required)"
  - "Partial-pending-bench SUMMARY pattern — Task 1 GREEN documented + bench carry-over surfaced cleanly so the next agent / verifier knows the exact resume point"

requirements-completed:
  - LFW-03  # SC#2 grep gate 0 hits; LFW-03 closed
  - LFW-04  # SC#1 PROGMEM audit complete with two-table form; zero uncategorized log-purposed PROGMEM
  # LMIG-04 SC#4 (Leonardo < 90%) + SC#5 (Uno recorded) PASS; SC#3 host pytest 4/4 PASS.
  # SC#3 bench native-pass + Phase 8 SC#2/SC#3 chip-seated carry-over remain pending Tasks 2 + 3.
  # NOT marking LMIG-04 closed yet — bench tasks pending.

# Metrics
duration: 8 min
completed: 2026-05-19
status: PARTIAL (Task 1 GREEN; Tasks 2 + 3 awaiting operator-on-bench)
---

# Phase 9 Plan 05: Measurement + Bench UAT Summary (PARTIAL)

**Task 1 (automated SC#1/SC#2/SC#4/SC#5 measurement artifact) GREEN: 09-MEASUREMENT.md published with LMIG-04 acceptance number Leonardo 85.3% (24,456 / 28,672, 4,216 B free) — a -3,843-byte / -13.4 pp reduction vs v1.1 close baseline of 98.7%. Tasks 2 (chipless bench wire-protocol matrix re-run post-3.0.0-dev bump) + 3 (Phase 8 SC#2 + SC#3 chip-seated W27C512 write + readback carry-over) require operator-on-bench and are surfaced as a CHECKPOINT below.**

## Performance

- **Duration:** ~8 min
- **Started:** 2026-05-19 (Task 1 execution)
- **Completed (Task 1 only):** 2026-05-19
- **Tasks:** 1 / 3 (1 autonomous GREEN; 2 + 3 pending operator-on-bench)
- **Files modified:** 0 production / 0 host / 1 planning artifact created (09-MEASUREMENT.md) + 1 SUMMARY (this file)
- **Commits:** 1 (`0df4b63` — Task 1 artifact)

## Accomplishments (Task 1 — autonomous portion)

- **LMIG-04 milestone-close numbers captured from cold-cache builds:**
  - Leonardo: 85.3% (24,456 / 28,672 bytes), 4,216 B free, SRAM 1,465 / 2,560 B (57.2%)
  - Uno: 68.9% (22,226 / 32,256 bytes), 10,030 B free, SRAM 1,497 / 2,048 B (73.1%)
- **5-column anchor table extended** from 08-MEASUREMENT.md:310-316 with the Phase 9 close row replacing prior TARGET/TBD placeholder. Phase 10 DOC-02 will quote the v1.1 → Phase 9 row verbatim.
- **4-delta attribution table** computed per CONTEXT.md D-08:
  - v1.1 (98.7%) → Phase 9 close: **−3,843 B (−13.4 pp)** Leonardo — the LMIG-04 acceptance number.
  - Phase 6 close → Phase 9 close: −3,836 B Leonardo / −3,874 B Uno.
  - Phase 7 close → Phase 9 close: −2,570 B Leonardo / −2,612 B Uno.
  - Phase 8 close → Phase 9 close: −82 B Leonardo / −104 B Uno (the isolated Phase 9 surface win — small because Phase 9 deleted infrastructure that was already mostly inlined-away in production builds).
- **PROGMEM exemption audit (SC#1):** TWO distinct labeled sub-tables published —
  - **Table (a) — named-symbol PROGMEM declarations (SC#1 acceptance gate):** 12 hits, all categorized into MAGIC_PREAMBLE (1), CRC8_TABLE (1), or json_parser keys + key_parsers[] table (10). **Zero uncategorized log-purposed PROGMEM hits.** LFW-04 satisfied.
  - **Table (d) — inline `F("...")` literal sites (informational, exempt):** 1 actual hit at `hardware_operations.cpp:88` (the LFW-05 inline bootstrap `F("OK: FW: ")` per CONTEXT.md D-01).
  - Per RESEARCH.md Risk #8: the two tables are mutually exclusive — `F(...)` literals do NOT yield named symbols and so cannot match `grep PROGMEM`. No site is double-counted.
- **LFW-03 grep gate (SC#2):** 0 hits — confirmed zero legacy macro surface in firestarter/src/include/lib (excluding rurp_log_id survivors + comment-only lines).
- **SC#3 host pytest gate:** 4 / 4 fwguard cases PASS (the bench native-pass exercise — firmware actually reporting `3.0.0-dev` over the wire without env-var prefix — is the Task 2 acceptance criterion still pending operator-on-bench).
- **SC#4 acceptance:** Leonardo Flash 85.3% < 90.0% with 4,216 B of headroom — PASS.
- **SC#5 acceptance:** Uno Flash recorded alongside (68.9%, 10,030 B free) — PASS.
- **09-MEASUREMENT.md published** at 403 lines (≥ 100-line minimum); contains all required sections including Bench Verification (placeholder for Task 2) + Phase 8 SC#2 carried (placeholder for Task 3) + Phase 8 SC#3 carried (placeholder for Task 3).

## Task Commits

| Task | Description | Commit | Sub-repo |
|------|-------------|--------|----------|
| 1 | 09-MEASUREMENT.md artifact (SC#1/SC#2/SC#4/SC#5 + Tasks 2 + 3 placeholders) | `0df4b63` | meta-repo |
| 2 | Chipless bench wire-protocol matrix re-run on Uno + Leonardo (SC#3 native-pass + Phase 8 chipless matrix) | **⏸ Pending operator-on-bench** | — |
| 3 | Phase 8 SC#2 + SC#3 chip-seated UAT carry-over on Uno + Leonardo (W27C512 write + readback) | **⏸ Pending operator-on-bench** | — |

## Files Created/Modified

- `.planning/phases/09-delete-old-log-macros-measure-flash-savings/09-MEASUREMENT.md` (CREATED, 403 lines)
- `.planning/phases/09-delete-old-log-macros-measure-flash-savings/09-05-SUMMARY.md` (this file)

No firmware, host, or test changes — Task 1 is a pure measurement + audit artifact.

## Verification Results

### Plan-level acceptance gate (Task 1 portion — autonomous gates)

| # | Gate | Expected | Actual | Result |
|---|------|----------|--------|--------|
| 1 | Artifact exists | file present | 403 lines on disk | PASS |
| 2 | Anchor Table section present | substring | present | PASS |
| 3 | 4-Delta Attribution section present | substring | present | PASS |
| 4 | PROGMEM Exemption Audit section present | substring | present | PASS |
| 5 | Named-symbol PROGMEM declarations table present | substring | present | PASS |
| 6 | Inline F() literal sites table present | substring | present | PASS |
| 7 | Legacy Macro Grep Gate section present | substring | present | PASS |
| 8 | Bench Verification — Chipless Wire-Protocol Validation section present | substring | present (placeholder) | PASS |
| 9 | Phase 8 SC#2 (carried) section present | substring | present (placeholder) | PASS |
| 10 | Phase 8 SC#3 (carried) section present | substring | present (placeholder) | PASS |
| 11 | LMIG-04 — Leonardo Flash < 90% | `< 90.0` | `85.3` | PASS |
| 12 | LFW-03 grep gate hits | `0` | `0` | PASS |
| 13 | LFW-04 PROGMEM uncategorized hits | `0` | `0` (12/12 categorized) | PASS |
| 14 | SC#3 host pytest fwguard | `4 passed` | `4 passed in 0.03s` | PASS |
| 15 | Cold-cache reproducibility — firmware Flash bytes match Plan 09-02 SUMMARY | Uno 22,226 / Leo 24,456 | Uno 22,226 / Leo 24,456 | PASS |

### Plan-level acceptance gate (Tasks 2 + 3 portion — bench gates)

| # | Gate | Status |
|---|------|--------|
| 16 | Uno `fw` output contains `OK: FW: 3.0.0-dev:uno` | ⏸ Pending Task 2 bench |
| 17 | Leonardo `fw` output contains `OK: FW: 3.0.0-dev:leonardo` | ⏸ Pending Task 2 bench |
| 18 | Phase 8 SC#2 (carried) populated or annotated "no chip available" | ⏸ Pending Task 3 bench |
| 19 | Phase 8 SC#3 (carried) populated or annotated "no chip available" | ⏸ Pending Task 3 bench |

Gates 1-15 PASS. Gates 16-19 await operator-on-bench session — surfaced as CHECKPOINT below.

## Decisions Made

- **Both delta rows present in 09-MEASUREMENT.md per CONTEXT.md D-08:** the Phase 8 → Phase 9 incremental delta (the "logging.h macro tower deletion, isolated" attribution) AND the v1.1 → Phase 9 milestone-close delta (the LMIG-04 acceptance number). Phase 10 DOC-02 will quote the latter into MILESTONES.md.
- **PROGMEM audit honors RESEARCH.md Risk #8 strictly:** TWO greps producing TWO mutually-exclusive labeled tables, with an explicit no-double-counting note. The (a)-named-symbol table is the SC#1 acceptance gate (12 hits, all categorized); the (d)-inline-F() table is informational only (1 actual literal site at the LFW-05 bootstrap).
- **Cold-cache reproducibility confirmed:** the Plan 09-05 measurement byte counts (Uno 22,226 / Leonardo 24,456) match Plan 09-02 SUMMARY's recorded values byte-for-byte. This independently confirms (a) PlatformIO's deterministic link order, (b) that the cold-cache `pio run -t clean` discipline reliably reproduces the same build output, and (c) that Plans 09-03 (host-only) + 09-04 (test-stubs-only) introduced zero firmware Flash change.
- **Tasks 2 + 3 surfaced as a CHECKPOINT** per planner's explicit instruction — the plan is non-autonomous because the chipless bench matrix + chip-seated UAT both require physical hardware; programmatic execution is not possible from this agent's environment.

## Deviations from Plan

None — Task 1 executed exactly as written. The plan explicitly marked Tasks 2 + 3 as `<task type="checkpoint:human-verify" gate="blocking">` and Task 1 followed the autonomous portion verbatim. The artifact's section structure, the two-table PROGMEM audit form, the cold-cache build discipline, the byte-count-as-authoritative rule, and the 4-delta attribution all match the plan's `<action>` and `<acceptance_criteria>` byte-for-byte.

**Total deviations:** 0.
**Impact on plan:** None — Task 1 GREEN; Tasks 2 + 3 pending operator-on-bench as the plan explicitly designed.

## Authentication Gates

None.

## Issues Encountered

None during Task 1 execution.

## Known Stubs

None in the artifact itself. The Bench Verification + Phase 8 SC#2 + Phase 8 SC#3 sections contain placeholder text (`_pending operator transcription_`) for the operator to fill, but these are INTENTIONAL pending markers documented per the plan's explicit Task 2 + Task 3 design, NOT unwired stubs. The placeholders carry the exact bench commands + acceptance criteria so the operator can run the bench session without re-reading the plan.

## Threat Flags

None new. The plan's `<threat_model>` covers all 6 STRIDE entries (T-09-05-01 through T-09-05-06). The Task 1 measurement work mitigates:
- T-09-05-03 (PROGMEM audit double-counting): the two-table form with explicit no-double-counting note is the mitigation; zero uncategorized log-purposed PROGMEM hits confirms LFW-04 satisfied.
- T-09-05-04 (build-cache staleness): cold-cache `pio run -t clean` before each AVR measurement; byte counts reproduce Plan 09-02 SUMMARY exactly.

T-09-05-01 (wire-shape regression), T-09-05-02 (Leonardo socket masquerade), and T-09-05-06 (transcription error) are mitigated by the bench Tasks 2 + 3 acceptance gates — operator-on-bench step.

## User Setup Required

None for Task 1.

For Tasks 2 + 3 (operator-on-bench): both Uno + Leonardo connected with ports identified; for Task 3 a W27C512 chip (or substitute supported chip) and ideally a pre-existing baseline `.bin` file from prior Phase 8 bench testing (or capture a fresh baseline as the new v1.2+ reference).

## CHECKPOINT — Tasks 2 + 3 Pending Operator-On-Bench

**Type:** `checkpoint:human-verify` (× 2 — bench Tasks 2 + 3)
**Plan:** 09-05
**Progress:** 1 / 3 tasks complete (Task 1 GREEN)

### Completed Tasks

| Task | Name | Commit | Files |
| ---- | ---- | ------ | ----- |
| 1 | Run autonomous SC#1/SC#2/SC#4/SC#5 — measure dual AVR Flash + capture PROGMEM exemption audit | `0df4b63` (meta-repo) | `.planning/phases/09-delete-old-log-macros-measure-flash-savings/09-MEASUREMENT.md` (created, 403 lines) |

### Current Tasks

**Task 2:** Bench wire-protocol re-run post-3.0.0-bump on Uno + Leonardo (SC#3 native-pass + Phase 8 chipless matrix)
**Status:** Awaiting operator-on-bench
**Blocked by:** Requires physical Uno + Leonardo boards on operator's bench; cannot execute programmatically from this environment.

**Task 3:** Phase 8 SC#2 + SC#3 chip-seated UAT carry-over on Uno + Leonardo (W27C512 write + readback)
**Status:** Awaiting operator-on-bench
**Blocked by:** Requires physical Uno + Leonardo + W27C512 chip (or substitute) on operator's bench.

### Bench Session Recipe (verbatim from 09-MEASUREMENT.md placeholders)

The artifact contains the exact bench commands + expected outputs + acceptance criteria pre-filled in the Bench Verification + Phase 8 SC#2 + Phase 8 SC#3 sections. Operator runs:

**Task 2 — Chipless bench matrix:**
```bash
cd /workspaces/firestarter_prom/firestarter
pio run -t upload -e uno --upload-port /dev/ttyACM0
pio run -t upload -e leonardo --upload-port /dev/ttyACM1
firestarter -p /dev/ttyACM0 fw       # expect: OK: FW: 3.0.0-dev:uno, ...
firestarter -p /dev/ttyACM1 fw       # expect: OK: FW: 3.0.0-dev:leonardo, ...
firestarter -p /dev/ttyACM0 hw       # P-02 sentinel; firestarter -p /dev/ttyACM1 hw
firestarter -p /dev/ttyACM0 config   # P-03 sentinel; firestarter -p /dev/ttyACM1 config
firestarter -p /dev/ttyACM0 vpp ; firestarter -p /dev/ttyACM1 vpp
firestarter -p /dev/ttyACM0 vpe ; firestarter -p /dev/ttyACM1 vpe
firestarter -p /dev/ttyACM0 id W27C512 ; firestarter -p /dev/ttyACM1 id W27C512
```
Operator transcribes observed outputs into the Bench Verification section's per-row table cells.

**Task 3 — Chip-seated W27C512 write + readback (BOTH boards):**
```bash
# Seat chip in Uno, then:
firestarter -p /dev/ttyACM0 write -e W27C512 <test.hex>
firestarter -p /dev/ttyACM0 read  -e W27C512 -o /tmp/ph9-uno-readback.bin
diff <baseline.bin> /tmp/ph9-uno-readback.bin

# Move chip to Leonardo, then:
firestarter -p /dev/ttyACM1 write -e W27C512 <test.hex>
firestarter -p /dev/ttyACM1 read  -e W27C512 -o /tmp/ph9-leonardo-readback.bin
diff <baseline.bin> /tmp/ph9-leonardo-readback.bin

# If Leonardo readback diverges, re-seat per [[project_leonardo-shield-socket-wonky]] before declaring regression.
# If no chip available, annotate "no chip available — carrying Phase 8 SC#2/SC#3 to Phase 10".
```

### Awaiting

Operator runs the bench session and transcribes observed outputs into the placeholder sections of `09-MEASUREMENT.md`. Resume signals (per the plan's Task 2 + 3 `<resume-signal>` blocks):
- Task 2: type `bench-chipless-approved` with observed outputs filled into the artifact, OR describe issues.
- Task 3: type `chip-uat-approved` with observed write + read transcripts, OR `no chip available — carrying Phase 8 SC#2/SC#3 to Phase 10`, OR `readback-regression` if a non-zero diff persists after re-seat (potential Phase 9 wire-format regression — stop for investigation).

After both bench tasks complete (or are explicitly carried), the operator (or a continuation agent spawned with the transcripts in-context) re-runs the plan-level acceptance gate from 09-05-PLAN.md's `<verification>` block — the artifact-side gates (1-15 above) already PASS, so the new pass would confirm gates 16-19 + emit a final `PLAN 05 GREEN — Phase 9 ready for /gsd-verify-work` line.

## Next Phase Readiness

- **Plan 09-05 is PARTIAL** — Task 1 GREEN, Tasks 2 + 3 pending operator-on-bench. The phase-level `/gsd-verify-phase` verifier should recognise the `⏸ Pending operator-on-bench` placeholders in 09-MEASUREMENT.md as a known carry-over (analog: Phase 8 SC#2/SC#3 were pending in `08-MEASUREMENT.md` and explicitly bundled forward into Phase 9 per CONTEXT.md Claude's-Discretion).
- **LMIG-04 measurement artifact is complete** for the parts that can be measured without hardware: SC#1/SC#2/SC#4/SC#5 + the host-side portion of SC#3 (pytest fwguard 4/4). Phase 10 DOC-02 can already quote the v1.1 → Phase 9 acceptance number (−3,843 B / −13.4 pp on Leonardo, 85.3% milestone close); the bench-side native-pass SC#3 + Phase 8 SC#2/SC#3 chip-seated UAT add operational confirmation but do not change the milestone number.
- **No new infrastructure / library deps / catalog changes.**
- **Phase 10** (`feature/phase-10-static-pins`): unchanged by this plan; the uncommitted Phase 10 work-in-progress in `firestarter/` was deliberately not touched.

## TDD Gate Compliance

This plan was not a TDD plan (`tdd: false` on all 3 tasks); no RED/GREEN/REFACTOR sequence applies. Task 1 executes the autonomous portion of the plan-level acceptance gate as 15 independent checks, all of which returned PASS for the artifact-side gates (gates 1-15). The bench-side gates (16-19) are surfaced as a CHECKPOINT pending operator-on-bench.

## Self-Check: PASSED

- `.planning/phases/09-delete-old-log-macros-measure-flash-savings/09-MEASUREMENT.md` exists on disk (403 lines): PASS.
- Commit `0df4b63` exists in meta-repo `git log`: PASS.
- All 15 Task 1 plan-level acceptance gates PASS (artifact sections + LMIG-04 < 90% + LFW-03 zero hits + LFW-04 all categorized + pytest 4/4 + cold-cache byte-count reproducibility).
- LMIG-04 milestone-close acceptance number quotable into Phase 10 DOC-02: Leonardo 85.3% (24,456 / 28,672 bytes), −3,843 B (−13.4 pp) vs v1.1 close baseline of 98.7%.
- This SUMMARY.md exists at `.planning/phases/09-delete-old-log-macros-measure-flash-savings/09-05-SUMMARY.md`.
- Bench Tasks 2 + 3 surfaced as CHECKPOINT with exact bench commands + acceptance criteria in both the SUMMARY and the artifact placeholders.

---

*Phase: 09-delete-old-log-macros-measure-flash-savings*
*Plan: 05-measurement-and-bench-uat*
*Status: PARTIAL — Task 1 GREEN; Tasks 2 + 3 awaiting operator-on-bench*
*Completed (Task 1): 2026-05-19*
