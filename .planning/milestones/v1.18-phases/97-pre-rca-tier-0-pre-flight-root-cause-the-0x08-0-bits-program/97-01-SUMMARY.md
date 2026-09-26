---
phase: 97-pre-rca-tier-0-pre-flight-root-cause-the-0x08-0-bits-program
plan: 01
subsystem: testing
tags: [rca, diagnostic, safe-01, evidence-scaffold, held-rail-proxy, am27c020, 0x08, eprom-quick]

# Dependency graph
requires:
  - phase: 93-rca-root-cause-the-w29c040-page-0-write-fault
    provides: RCA-FINDINGS doc structure (frontmatter, Bench Discipline Log, RC table, SAFE-01 close-out, hand-off) reused as the v1.18 template
  - phase: 81-2516-db-entry-non-destructive-read-sweep
    provides: v1.15 EVIDENCE.{md,json} cell schema (locked_columns + per-cell keys) reused for the v1.18 bench record
provides:
  - SAFE-01 non-invasive confirmation note (evidence/SAFE-01-PREFLIGHT.md) with current-tree file:line evidence
  - v1.18 bench EVIDENCE record (md + json) with two never-fabricated cells (AM27C020 0x08 + W27C512 0x07 control)
  - 97-RCA-FINDINGS.md verdict-doc skeleton (RC-1..RC-5 disconfirmation table, held-rail proxy values pinned)
  - confirmed provenance of the four committed Wave-0 gate scripts (check_pre01/signature/diff07/verdict.py)
affects: [97-02 (fills Cell A + RC verdicts), 97-03 (fills Cell B + RCA-03), 98-fix, 99-bench-ledger]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Wave-1 no-hardware scaffold: SAFE-01 invariant + capture templates locked BEFORE the single irreversible bench session"
    - "Bypass-command gate matches real `firestarter write|dev … --force/-b` command invocations, not free-text term mentions"
    - "Held-rail static-proxy values pinned against the LIVE host `dev reg -f` bit map with host-vs-firmware alias caveat documented"

key-files:
  created:
    - .planning/phases/97-pre-rca-tier-0-pre-flight-root-cause-the-0x08-0-bits-program/evidence/SAFE-01-PREFLIGHT.md
    - .planning/phases/97-pre-rca-tier-0-pre-flight-root-cause-the-0x08-0-bits-program/evidence/97-RCA-FINDINGS.md
    - .planning/v1.18/bench/EVIDENCE.json
    - .planning/v1.18/bench/EVIDENCE.md
  modified: []

key-decisions:
  - "SAFE-01 invariant holds NOT by firmware lacking FLAG_FORCE relaxation (it has one at primitives.cpp:121) but by the Phase-97 procedure never passing --force"
  - "Held program-window value pinned at host-space 0x188 (0x080|0x100|0x008), alias-probe pair 0x180-vs-0x188; marked [ASSUMED] per A1"
  - "All bench-measurement fields seeded as TBD-bench placeholders; never fabricated (D-02)"
  - "Task 4 ASSERTS the four Wave-0 gate scripts (present/tracked/parse-clean); does NOT recreate or modify them"

patterns-established:
  - "Diagnostic-phase Wave-1 scaffold: three artifacts + gate-script provenance, zero source edits"
  - "Host -f bit map is authoritative for held-rail proxy; firmware physical bit aliases (CTRL_VPP_P1_ENABLE_REV2 == CTRL_ADDRESS_LINE_18_REV2 == 0x08) must be remapped"

requirements-completed: [SAFE-01]

# Metrics
duration: 4min
completed: 2026-06-29
---

# Phase 97 Plan 01: Tier-0 Pre-Flight Diagnostic Scaffolding Summary

**No-hardware Wave-1 foundation for the AM27C020 `0x08` RCA: SAFE-01 confirmed non-invasively by file:line code-read (over-voltage ERROR path intact, host guard unbypassed), the v1.18 bench EVIDENCE record + 97-RCA-FINDINGS verdict skeleton stood up with never-fabricated TBD cells, held-rail proxy values 0x188/0x180 pinned against the live host `dev reg -f` bit map, and the four committed Wave-0 gate scripts asserted present/tracked/parse-clean.**

## Performance

- **Duration:** 4 min
- **Started:** 2026-06-29T15:43:35Z
- **Completed:** 2026-06-29T15:47:39Z
- **Tasks:** 4
- **Files modified:** 4 created (0 source files touched)

## Accomplishments
- **SAFE-01 confirmed read-only** with current-tree (`bccd995`/`e0bdea4`) file:line evidence: HIGH→ERROR at `primitives.cpp:106,121,126` (relaxes to WARNING only under FLAG_FORCE), LOW→WARNING/proceed at `primitives.cpp:129,145`, `resolve_chip` live-path guard at `chip_resolver.py:16`, normal `0x08` dispatch at `memory.cpp:121-122`. No guard triggered; no source edited.
- **v1.18 bench EVIDENCE record** (md+json) with two schema-correct, never-fabricated cells — AM27C020 (`0x08`, full Failure Signature Capture Schema) + W27C512 (`0x07` differential control) — plus top-level `pre_01_result` + `blank_state_sha256` PRE-01 placeholders.
- **97-RCA-FINDINGS.md skeleton** mirroring v1.17 Phase-93: Bench Discipline Log, PRE-01, RCA-01, RCA-02 differential matrix, RCA-03 RC-1..RC-5 disconfirmation table (Verdict column TBD + D-03 callout), SAFE-01 close-out, Phase-98 hand-off.
- **Held-rail proxy values pinned** (`0x188` P1-on / `0x180` P1-off) against the live `cli_handlers.py:1010-1018` host `-f` bit map, with the firmware-vs-host alias caveat (`rurp_pinout.h:121,127`: `CTRL_VPP_P1_ENABLE_REV2 == CTRL_ADDRESS_LINE_18_REV2 == 0x08`) documented; `0x188` marked `[ASSUMED]` per A1.
- **Wave-0 gate-script provenance confirmed:** the four `.planning/v1.18/bench/check_{pre01,signature,diff07,verdict}.py` scripts are present, git-tracked, and parse-clean (`py_compile`) — they are committed Wave-0 infrastructure on which Plans 02/03 automated verify blocks depend.

## Task Commits

Each task was committed atomically (into the meta repo, `.planning/` files):

1. **Task 1: SAFE-01 non-invasive confirmation note** - `fb283c6` (docs)
2. **Task 2: Scaffold v1.18 bench EVIDENCE record (md + json)** - `65278ea` (docs)
3. **Task 3: Scaffold 97-RCA-FINDINGS.md + pin held-rail proxy values** - `4207a3d` (docs)
4. **Task 4: Confirm provenance of the four Wave-0 gate scripts** - no commit (assertion-only; scripts intentionally NOT modified — see Decisions)

**Plan metadata:** (final docs commit — SUMMARY + STATE + ROADMAP)

## Files Created/Modified
- `evidence/SAFE-01-PREFLIGHT.md` - SAFE-01 four-confirmation note with current-tree file:line citations
- `evidence/97-RCA-FINDINGS.md` - RCA verdict-doc skeleton + pinned held-rail proxy subsection
- `.planning/v1.18/bench/EVIDENCE.json` - machine-readable bench record (v1.15 schema, 2 TBD cells)
- `.planning/v1.18/bench/EVIDENCE.md` - human-readable mirror with D-08 bench-discipline columns

## Wave-0 Gate-Script Dependency (Task 4 record)

The four scripts below are **committed, git-tracked Wave-0 gate infrastructure** that the Plan-02/03 automated `<verify>` blocks invoke. Task 4 confirmed all four exist on disk, are git-tracked, and parse cleanly under `python3 -m py_compile`. They were **NOT** recreated or modified by this plan.

| Script | Consumed by | Asserts |
|--------|-------------|---------|
| `.planning/v1.18/bench/check_pre01.py` | Plan 02 Task 2 | AM27C020 cell `pre_read_sha256` + `controller` captured (no TBD) |
| `.planning/v1.18/bench/check_signature.py` | Plan 02 Task 3 | AM27C020 failure-signature fields filled + pre/post SHA consistency |
| `.planning/v1.18/bench/check_diff07.py` | Plan 03 Task 2 | W27C512 differential verdict recorded (no TBD) |
| `.planning/v1.18/bench/check_verdict.py` | Plan 03 Task 3 | RC-1 + RC-2 each verdicted + classification + 0x07 differential filled |

## Decisions Made
- **SAFE-01 invariant shape:** documented explicitly that the firmware DOES contain a FLAG_FORCE relaxation of the over-voltage HIGH branch (`primitives.cpp:121-127`); SAFE-01 is satisfied because the Phase-97 procedure never passes `--force`, not because the relaxation is absent. This avoids a later reader mistaking "FLAG_FORCE exists" for a SAFE-01 hole.
- **Held value `0x188`** derived from verified program-time bits (regulator `0x080` + VPE-drop `0x100` + P1-route `0x008`), pinned in the **host `-f` namespace** (distinct bits) rather than the firmware physical layout (where P1_ENABLE and A18 alias to the same `0x08`); marked `[ASSUMED — confirm at first bench reading]` per RESEARCH A1.
- **Task 4 is assertion-only** (no commit): the gate scripts already exist, are committed, and are sound — recreating them would risk drift from the versions Plans 02/03 invoke. Provenance is recorded here in the SUMMARY instead.
- All bench-measurement fields seeded as `TBD-bench` / `TBD — Plan 02/03 fills`, never fabricated (D-02); a 0-bit-flip is INDETERMINATE pre-fix and never triggers deferral (D-01/D-06).

## Deviations from Plan

None - plan executed exactly as written. All four task `<verify>` gates passed as authored (including the repaired SAFE-01 bypass-command gate, which matches real bypass command invocations rather than prose).

## Issues Encountered
None. Pre-existing untracked items (`W29C040.bin`, `scratchpad/`) and pre-existing dirty submodule state (`firestarter/platformio.ini`, `firestarter_app/.gitignore`, etc.) were present at session start and are out of scope — left untouched, no source under `firestarter/` or `firestarter_app/` was modified.

## Known Stubs
The three diagnostic artifacts are intentional **Wave-1 scaffolds** — every bench-measurement field is an explicit `TBD-bench` / `TBD — Plan 02/03 fills` placeholder. This is by design (D-02: never fabricate bench results). The placeholders are resolved by **Plan 97-02** (Cell A + RC-1/RC-2 verdicts) and **Plan 97-03** (Cell B + RCA-03 named cause). The downstream `check_*.py` gates enforce that no `TBD` survives into the Plan-02/03 verifies.

## Next Phase Readiness
- Plan 97-02 has ready-to-fill artifacts: EVIDENCE Cell A (AM27C020 0x08), the PRE-01 + RCA-01 sections, and the pinned `0x188`/`0x180` held-rail proxy commands for the operator DMM.
- Plan 97-03 has the W27C512 differential cell + RCA-02/RCA-03 sections.
- SAFE-01 confirmed for Phase 97; recurs as a standing precondition through Phases 98–99.
- No blockers. Operator bench (Leonardo + Rev 2.0, seated AM27C020, DMM at pin 1 + pin 31) is the gating resource for Plans 02/03.

## Self-Check: PASSED

- All 4 created files verified present on disk.
- All 3 task commits verified in git log (`fb283c6`, `65278ea`, `4207a3d`); Task 4 is assertion-only (no commit, by design).
- No source modified under `firestarter/` or `firestarter_app/` (diagnostic phase).

---
*Phase: 97-pre-rca-tier-0-pre-flight-root-cause-the-0x08-0-bits-program*
*Completed: 2026-06-29*
