---
phase: 06-logging-infrastructure
plan: 06
subsystem: firmware
tags: [firmware, flash-budget, measurement, leonardo, uno, lmig-coexistence]

# Dependency graph
requires:
  - 06-02 (firmware rurp_log_id helper + CRC8 table + messages.c committed; defines what the measurement quantifies)
provides:
  - .planning/phases/06-logging-infrastructure/06-FLASH-MEASUREMENT.md (Phase 6 close flash baseline + decision tree result)
  - Phase 9 LMIG-04 baseline anchor (3-row comparison table: v1.1 close, Phase 6 close, Phase 9 close TARGET)
affects: [09-delete-old-log-macros-measure-flash-savings, 10-milestone-close-v1.2]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Flash budget measurement protocol: pio run -e <board>, extract Flash: line, compute byte delta vs prior milestone baseline, classify against pre-declared decision tree (Case A/B/C)"
    - "v1.1 → Phase 6 → Phase 9 three-snapshot anchor table; isolates pure-migration recovery delta from intervening framework/toolchain drift"

key-files:
  created:
    - .planning/phases/06-logging-infrastructure/06-FLASH-MEASUREMENT.md
  modified: []

key-decisions:
  - "Decision Case A — Leonardo build succeeded with 380 bytes free (28,292 / 28,672), well above the 50-byte Case-A/B threshold. No -D NO_TEXT_LOGS fall-back required."
  - "v1.1 → Phase 6 byte delta is −7 bytes (28,299 → 28,292) — within toolchain rounding noise. Both states display 98.7% Flash at the one-decimal-percent PlatformIO reporting precision. Phase 6 LMIG-01 coexistence proven: legacy text path AND new ID-frame path both link, no cliff hit."
  - "No formal Uno v1.1 baseline existed; this measurement establishes the Uno Phase 6 close anchor at 80.9% (26,100 / 32,256, 6,156 B free) for the Phase 9 milestone comparison."

patterns-established:
  - "Three-snapshot flash anchor: v1.1 close baseline + Phase 6 mid-point + Phase 9 target — enables Phase 9 to report two deltas (v1.1 → v1.2 headline + Phase 6 → Phase 9 pure-migration recovery), isolating call-site-conversion + legacy-deletion benefit from any intervening framework drift."
  - "Decision-tree-driven measurement: plan pre-declares Cases A/B/C with explicit thresholds (≥50 B free, <50 B free, >100% overflow) so executor never improvises a measurement classification."

requirements-completed: [LFW-01, LFW-02]

# Metrics
duration: 8 min
completed: 2026-05-18
---

# Phase 6 Plan 06: Flash Budget Measurement Summary

**Phase 6 close flash budget measured on both Leonardo (98.7%, 380 B free) and Uno (80.9%, 6,156 B free); Decision = Case A; no -D NO_TEXT_LOGS fall-back required; Phase 9 LMIG-04 baseline anchored with a 3-row v1.1 → Phase 6 → Phase 9 comparison table.**

## Performance

- **Duration:** 8 min (start `2026-05-18T12:16:03Z`, end `2026-05-18T12:24:00Z`)
- **Tasks:** 1/1 complete
- **Files created:** 1 measurement artifact (+ this SUMMARY)
- **Files modified:** 0 firmware sources (measurement-only plan)

## Accomplishments

- **Leonardo Flash:** 98.7% (28,292 / 28,672 bytes), **380 bytes free**. `pio run -e leonardo` exit 0.
- **Uno Flash:** 80.9% (26,100 / 32,256 bytes), **6,156 bytes free**. `pio run -e uno` exit 0.
- **Delta vs v1.1 close baseline (Leonardo 98.7% ≈ 28,299 B):** −7 bytes / −0.024 pct points — within toolchain rounding; LMIG-01 coexistence holds and the Plan 02 additive code did not tip Leonardo over the 28,672-byte ATmega32U4 cliff.
- **Decision:** **Case A** (build successful with ≥50 bytes free). No `-D NO_TEXT_LOGS` fall-back required. `firestarter/platformio.ini` untouched.
- **Phase 9 anchor:** measurement artifact at `.planning/phases/06-logging-infrastructure/06-FLASH-MEASUREMENT.md` contains the explicit `## Anchor for Plan 09` section with the 3-row v1.1 → Phase 6 → Phase 9 TARGET (< 90% Leonardo, < ~25,805 / 28,672 B) comparison table for Phase 9's LMIG-04 final-delta computation.

## Task Commits

Each task = single atomic commit in the meta-repo (this is a docs-only plan; no firmware submodule pointer movement).

### Task 1 — Measure pio run -e leonardo + pio run -e uno; record raw output

1. **meta-repo:** `<final-commit>` (docs) — adds `06-FLASH-MEASUREMENT.md` + this SUMMARY + STATE.md + ROADMAP.md updates atomically. (Single combined commit since the artifact, SUMMARY, and state/roadmap bumps are all docs in the meta-repo and have no functional separation.)

**Plan metadata commit:** combined with Task 1 commit (single docs-only commit covers measurement artifact + SUMMARY + STATE.md + ROADMAP.md per orchestrator's sequential-execution instruction).

## Files Created/Modified

### Meta-repo — created

- `.planning/phases/06-logging-infrastructure/06-FLASH-MEASUREMENT.md` — Phase 6 close flash measurement artifact. Contains: metadata header (date, boards, baseline), raw `pio run -e leonardo` build tail (fenced code block), Leonardo Flash bullet + delta-vs-v1.1, raw `pio run -e uno` build tail (fenced code block), Uno Flash bullet, `## Decision` section with `Case A` literal token + rationale, `## Fall-Back Measurement` section marked "Section omitted — no fall-back needed", `## Anchor for Plan 09` section with v1.1 → Phase 6 → Phase 9 TARGET comparison table.
- `.planning/phases/06-logging-infrastructure/06-06-SUMMARY.md` — this file.

### Meta-repo — modified

- `.planning/STATE.md` — plan counter advanced (5 → 6 of 6 in Phase 6), session timestamp updated, decisions appended, performance metric row added.
- `.planning/ROADMAP.md` — Phase 6 progress table row updated (6/6 plans complete).
- `.planning/REQUIREMENTS.md` — LFW-01 and LFW-02 marked complete in traceability table.

### Submodules — untouched

- `firestarter/` — no commit (no firmware code change). `git -C firestarter status` shows only the pre-existing `include/rurp_register_utils.h` dirty file carried forward from before Phase 6 began. `git -C firestarter diff platformio.ini` is empty (the `-D NO_TEXT_LOGS` fall-back path was NOT exercised because Decision was Case A).
- `firestarter_app/` — no commit (no host code change).

## Decisions Made

1. **Decision Case A.** Leonardo build successful with 380 bytes free (>> 50-byte Case A/B threshold). No fall-back required. Rationale: the Phase 6 Plan 02 additive code is largely linker-dead in Phase 6 because no call-site invokes `rurp_log_id` yet — LMIG-01 (coexistence) prevented call-site conversion in Phase 6. The CRC8 table + messages.c PROGMEM table + frame emitter + Uno strong override sit dormant until Phase 7-8 call-site conversion activates them.

2. **v1.1 baseline byte-derivation:** baseline byte count for Leonardo is derived from `98.7% × 28,672 = 28,299 bytes` (ROADMAP and PROJECT.md pinned the percentage, not the byte count). Stated explicitly in the measurement artifact's `**Baseline (v1.1 close):**` header line as `~28,299 bytes` so the −7 byte delta is reproducible.

3. **Three-snapshot anchor for Phase 9:** the artifact's `## Anchor for Plan 09` section explicitly enumerates three reference points (v1.1 close, Phase 6 close THIS plan, Phase 9 close TARGET < 90%) in a single table so Phase 9's LMIG-04 SUMMARY can cite both the headline v1.1 → v1.2 delta AND the Phase 6 → Phase 9 pure-migration-recovery delta. This isolates the call-site-conversion + legacy-deletion savings from any intervening framework/toolchain drift.

## Deviations from Plan

None — plan executed exactly as written. Decision tree resolved to Case A (the lowest-friction path the plan named); no fall-back, no platformio.ini edit, no submodule commit needed.

## Issues Encountered

- **(Non-issue) Delta sign:** the v1.1 close → Phase 6 close byte delta is −7 (i.e., slightly negative), which is counter-intuitive given Phase 6 Plan 02 ADDED ~600-900 bytes of code per RESEARCH estimate. Explanation: the Plan 02 additive code (CRC8 table, messages.c PROGMEM table, `_firestarter_emit_frame`, weak `rurp_log_id`, Uno strong override) has zero production callers in Phase 6 (LMIG-01 coexistence: no call-sites converted yet). The linker GC'd or did not yet pull in the relevant sections. Both v1.1 close and Phase 6 close round to 98.7% at PlatformIO's one-decimal-percent reporting precision. The artifact documents this clearly so the Phase 9 reader is not misled — Phase 7-8 call-site conversion WILL activate the emitter (drawing the table in as live code) AND retire `rurp_log_P` call-sites (releasing per-call PROGMEM strings); the net direction across both is downward toward the < 90% Phase 9 target.

## User Setup Required

None — no external services configured.

## Next Phase Readiness

**Phase 7 (Convert ERROR + WARN + INFO Call-Sites — LMIG-02)** is unblocked:
- Flash budget on Leonardo has 380 bytes free at Phase 6 close. Phase 7's per-call-site conversion replaces `log_error_format(...)` calls (each carrying its own PROGMEM string + format buffer dance) with `LOG_ID(MSG_*)` invocations. Net delta per converted call-site is expected negative (string → 1-byte ID + 0-N raw param bytes). The 380 B free headroom is comfortable for Phase 7's incremental conversion approach.
- The `## Anchor for Plan 09` section locks the Phase 6 close number for the milestone-close delta computation.

**Phase 8 (Convert State-Machine Prefix Call-Sites OK/INIT/MAIN/END — LMIG-03)** is unblocked:
- Same flash headroom argument as Phase 7. The four state-machine prefix strings (`OK:`, `INIT:`, `MAIN:`, `END:`) are the dominant per-call-site PROGMEM consumers; their conversion is the largest single batch of byte reclamation before Phase 9's `LOG_*_MSG` deletion.

**Phase 9 (Delete Old Log Macros + Measure Flash Savings — LFW-03, LFW-04, LMIG-04)** has its baseline anchor:
- This plan's measurement artifact provides the exact byte counts Phase 9's final flash-savings measurement compares against. Phase 9 SUMMARY will cite both `Leonardo 98.7% (28,299 B) → <X>%` (v1.1 → v1.2 headline) and `Leonardo 98.7% (28,292 B) → <X>%` (Phase 6 → Phase 9 pure-migration recovery).

**Phase 10 (Milestone Close — DOC-02)** unblocked downstream by Phase 9.

## Verification Commands

```bash
# Production builds — both succeed at Phase 6 close, LMIG-01 coexistence verified.
cd firestarter && pio run -e leonardo   # => SUCCESS  RAM 60.6%  Flash 98.7% (28292/28672)  380 B free
cd firestarter && pio run -e uno        # => SUCCESS  RAM 77.5%  Flash 80.9% (26100/32256)  6156 B free

# Plan 02 modifications intact (rurp_log_id surface count >= 4 = decl + weak default + Uno strong override + use-sites).
grep -c "rurp_log_id" firestarter/include/rurp_shield.h \
                       firestarter/src/boards/rurp_serial_utils.cpp \
                       firestarter/src/boards/uno_rurp_shield.cpp \
  | awk -F: '{sum+=$2} END {print sum}'
# => 6 (>= 4 acceptance threshold ✓)

# platformio.ini clean — no -D NO_TEXT_LOGS residue.
grep -n "NO_TEXT_LOGS" firestarter/platformio.ini || echo "(no match — clean ✓)"
git -C firestarter diff platformio.ini   # => empty ✓

# Artifact file passes the plan's automated verify grep set.
test -f .planning/phases/06-logging-infrastructure/06-FLASH-MEASUREMENT.md && echo "ARTIFACT EXISTS ✓"
grep -nE "Leonardo Flash:|Flash:.*%|pio run -e leonardo" .planning/phases/06-logging-infrastructure/06-FLASH-MEASUREMENT.md
grep -n  "Delta vs v1.1\|Baseline.*98.7"                    .planning/phases/06-logging-infrastructure/06-FLASH-MEASUREMENT.md
grep -nE "Anchor for Plan 09|## Decision"                   .planning/phases/06-logging-infrastructure/06-FLASH-MEASUREMENT.md
grep -nE "Case A|Case B|Case C"                             .planning/phases/06-logging-infrastructure/06-FLASH-MEASUREMENT.md
# => all match ✓
```

## Self-Check: PASSED

Files exist:
- `.planning/phases/06-logging-infrastructure/06-FLASH-MEASUREMENT.md` — FOUND
- `.planning/phases/06-logging-infrastructure/06-06-SUMMARY.md` (this file) — FOUND

Acceptance grep checks (Plan 06-06 `<verify><automated>`):
- `Leonardo Flash:` / `Flash:.*%` / `pio run -e leonardo` present — MATCHED (5 hits)
- `Delta vs v1.1` / `Baseline.*98.7` present — MATCHED (2 hits)
- `Anchor for Plan 09` / `## Decision` present — MATCHED (2 hits)
- `Case A` literal token present — MATCHED (1 hit)

Behavioural verification:
- `pio run -e leonardo` => exit 0 (Flash 98.7%, 28292/28672, 380 B free) — RECORDED
- `pio run -e uno`      => exit 0 (Flash 80.9%, 26100/32256, 6156 B free) — RECORDED
- `grep -c rurp_log_id ...` => 6 (>= 4) — Plan 02 regression check PASSED
- `git -C firestarter diff platformio.ini` => empty — NO_TEXT_LOGS residue check PASSED

---
*Phase: 06-logging-infrastructure*
*Completed: 2026-05-18*
