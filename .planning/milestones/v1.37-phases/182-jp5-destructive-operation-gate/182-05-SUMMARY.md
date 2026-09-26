---
phase: 182-jp5-destructive-operation-gate
plan: 05
subsystem: hardware-record
tags: [schematic-trace, hardware-record, vpp-routing, record-correction, gh60]

requires:
  - phase: 182-jp5-destructive-operation-gate (plan 01/04)
    provides: locked D-01...D-15 decisions this trace answers to, and the CONTEXT/RESEARCH
      artefacts (JP4 symbol coordinates, evidence photographs) this plan reads
provides:
  - "SAFE-03's answer: a VPP-destination table (revision family x JP4 state -> reachable
    socket pin) in .planning/notes/jumper-display-ground-truth.md, with per-claim citations
    and three cells marked PROBE-PENDING"
  - "gh#60's operations question answered and cited: writing and erasing energize socket
    pin 1; reading, verifying, blank-checking and id do not"
  - "JP4's record corrected in jumper-display-ground-truth.md: socket pin 1 is JP4's common
    pole, not a destination; the footprint-change attribution moved from Rev2.2->Rev2.3 to
    Rev2.1->Rev2.2"
  - "The R41-couples-to-JP4 claim in v1.7-SHIELD-REVS.md retracted as measured false; the
    hw_revision detect band is independent of JP4 position"
  - "Assumption A1 (VPE rail level with the regulator off, unmeasured) recorded by name with
    its J6 pin 4 probe, pointing at Plan 06"
affects: [182-06, 182-07, D-09-jumper-display-phase, 187-answered-reports]

actuals:
  tokens: 9500
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "Desk-trace evidence citation discipline: every VPP-destination table cell is either
      cited to a named artefact (pos-CSV, gerber drill file, kicad_sch/kicad_pcb coordinate,
      firmware file:line) or explicitly marked PROBE-PENDING with its probe named — no cell
      asserted from inference alone"
    - "Rev 2.2 provenance rule: read Rev 2.2's own pos-CSV and gerber bundle first; the
      shared Rev 2.1 schematic blob is stale evidence about Rev 2.2 on at least two axes now
      (R41 value, JP4 footprint)"

key-files:
  created: []
  modified:
    - .planning/notes/jumper-display-ground-truth.md
    - .planning/v1.7-SHIELD-REVS.md

key-decisions:
  - "JP4 is not a VPP source: socket pin 1 is its common pole, and its two selectable poles
    export whatever socket pin 1 carries to socket pin 3 (28-pin part's pin 1) or socket
    pin 25 (24-pin part's pin 21, Rev 2.2+ only)"
  - "The JP4 footprint change (1x2 -> 2x2, 3-pole) is at Rev 2.1 -> Rev 2.2, settled by Rev
    2.2's own pick-and-place CSV and gerber drill file, not the Rev 2.2->Rev 2.3 transition
    the project record previously claimed"
  - "The R41-couples-to-JP4 claim is retracted outright as measured false: R41's GND pin
    routes directly to GND in both schematic and PCB, ~29 mm from JP4, in a different board
    region; the hw_revision detect band never depended on JP4 position"
  - "D-14 (the R41/JP4 characterization) stays characterize-only in this phase: no firmware
    change lands; the bench falsification (reading hw_revision at each JP4 position,
    predicted no change) is Plan 06's to run"
  - "255 DIP32_SST39SF040 rows with A18 on socket pin 1 are recorded as a structural
    remainder and deliberately not gated in this phase, per D-06's ban on gating from
    inference; Plan 07 files the backlog item"

requirements-completed: [SAFE-03]

coverage:
  - id: D1
    description: "VPP-destination table (revision family x JP4 state -> reachable socket
      pin) written into jumper-display-ground-truth.md, every cell cited or PROBE-PENDING"
    requirement: "SAFE-03"
    verification:
      - kind: other
        ref: "/usr/bin/grep -c 'PROBE-PENDING' .planning/notes/jumper-display-ground-truth.md (>=3)"
        status: pass
      - kind: other
        ref: "/usr/bin/grep -n 'socket pin 25' .planning/notes/jumper-display-ground-truth.md"
        status: pass
    human_judgment: false
  - id: D2
    description: "gh#60 operations question answered plainly and cited to eprom.cpp /
      rurp_pinout.h / rurp_hw_rev_utils.h file:line"
    requirement: "SAFE-03"
    verification:
      - kind: other
        ref: "/usr/bin/grep -nE '0x08|CTRL_VPP_P1_ENABLE|CTRL_ADDRESS_LINE_18' .planning/notes/jumper-display-ground-truth.md"
        status: pass
    human_judgment: false
  - id: D3
    description: "JP4's row corrected in place (common-pole framing, footprint-revision
      attribution moved to Rev2.1->Rev2.2); confirmed defect 4 resolved"
    verification:
      - kind: other
        ref: "/usr/bin/grep -n 'VPP to socket pin 1 only' .planning/notes/jumper-display-ground-truth.md (absent)"
        status: pass
    human_judgment: false
  - id: D4
    description: "The R41-couples-to-JP4 claim retracted in v1.7-SHIELD-REVS.md, with the
      independent-of-JP4-position consequence stated, and every 'via JP4' phrasing corrected"
    requirement: "SAFE-03"
    verification:
      - kind: other
        ref: "/usr/bin/grep -n \"R41's lower terminal connects to one pin of JP4\" .planning/v1.7-SHIELD-REVS.md (absent)"
        status: pass
      - kind: other
        ref: "/usr/bin/grep -n 'independent of JP4 position' .planning/v1.7-SHIELD-REVS.md"
        status: pass
    human_judgment: false
  - id: D5
    description: "Systemic-cause note naming all three Rev-2.2-inferred-from-Rev-2.1 wrong
      answers, and section 6's 24-pin UV-EPROM capability row revision-qualified"
    verification:
      - kind: other
        ref: "/usr/bin/grep -niE 'systemic|three wrong answers' .planning/v1.7-SHIELD-REVS.md"
        status: pass
    human_judgment: true
    rationale: "Section 6's capability-column correction and the 'no other family's row
      touched' constraint were verified by reading the diff (git diff --stat, per-row scan)
      rather than by an automated grep leg the plan specified; a human should confirm the
      prose reads correctly in context."

duration: 55min
completed: 2026-09-10
status: complete
---

# Phase 182 Plan 05: JP5 Destructive-Operation Gate — SAFE-03 Trace Summary

**Settled the VPP-destination table and answered gh#60 from the shield schematic, PCB, gerbers
and firmware — not inference — and corrected two wrong project-record claims the trace found
along the way.**

## Performance

- **Duration:** 55 min
- **Started:** 2026-09-10T14:02:36Z (approx, from session start)
- **Completed:** 2026-09-10T14:57:36Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Wrote the VPP-destination table into `.planning/notes/jumper-display-ground-truth.md`:
  revision family x JP4 state -> reachable socket pin, with the Rev 0/1 row, both Rev 2.0/2.1
  JP4 states, and all three Rev 2.2/2.3 JP4 states, three cells marked `PROBE-PENDING` with
  their exact probes named.
- Answered gh#60 plainly, cited to firmware file:line: **writing and erasing energize socket
  pin 1; reading, verifying, blank-checking and `id` do not** (`id` puts 12 V on socket pin 26
  via Q7 instead). Recorded the crux that makes the pin-map fix insufficient on its own: on
  Rev 2.x, `CTRL_ADDRESS_LINE_18` and `CTRL_VPP_P1_ENABLE` collapse onto the same physical bit
  `0x08`, and that bit is rewritten from the address on every byte during a write.
- Corrected JP4's row: socket pin 1 is its common pole, not a destination; its two poles
  export whatever pin 1 carries to socket pin 3 or socket pin 25. Corrected the footprint
  change's revision attribution from Rev 2.2->Rev 2.3 to Rev 2.1->Rev 2.2, citing Rev 2.2's
  own pick-and-place CSV and gerber drill file.
- Retracted the R41-couples-to-JP4 claim in `v1.7-SHIELD-REVS.md` outright as measured false,
  stating the consequence: the `hw_revision` detect band is independent of JP4 position.
  Corrected every "via JP4" phrasing this false claim had propagated into (§8 ASCII topology,
  §9 ADC band table).
- Revision-qualified §6's 24-pin legacy UV-EPROM capability row (readable on Rev 0/2.0/2.1,
  programmable on Rev 2.2+) and corrected the Rev 2.3 "capability set unchanged" note.
- Added "Rev 2.2 provenance discipline (Phase 182)" naming the systemic cause: Rev 2.2 has
  now been inferred from Rev 2.1's shared schematic blob three times, producing three wrong
  answers (R41 4k7-vs-10k, JP4's footprint, and the revision at which the footprint changed),
  while Rev 2.2's own artefacts sat in the same directory throughout.
- Recorded assumption A1 (VPE rail level with the regulator off, unmeasured) by name with its
  `J6` pin 4 probe and the widened-scope consequence, pointing at Plan 06.
- Resolved `jumper-display-ground-truth.md`'s confirmed defect 4 (24-pin VPP maps get no
  JP3/JP4 guidance) as a by-product of the table.
- Recorded the 255-row `DIP32_SST39SF040` A18-on-pin-1 structural remainder as deliberately
  not gated in this phase (D-06 forbids gating on inference); Plan 07 files the backlog item.
- Found and fixed a stale `file:LINE` citation during the citation-hygiene pass:
  `rurp_pinout.h:144` -> `:149` for the `CTRL_ADDRESS_LINE_18_REV2` alias, in both touched
  files.

## Task Commits

Each task was committed atomically:

1. **Task 1: The VPP-destination table and the gh#60 answer, in the jumper ground-truth
   note** — `cfc0dc71` (docs)
2. **Task 2: Correct every JP4 claim the trace settles in v1.7-SHIELD-REVS.md, and retract the
   R41 claim** — `2d102f19` (docs)

**Plan metadata:** committed with the SUMMARY (this file) plus STATE.md/ROADMAP.md/
REQUIREMENTS.md updates.

## Files Created/Modified

- `.planning/notes/jumper-display-ground-truth.md` — JP4/JP5 rows corrected; new "VPP
  destination per revision and JP4 state" and "Which operations energize socket pin 1" and
  "Evidence photographs" sections added; confirmed defect 4 resolved.
- `.planning/v1.7-SHIELD-REVS.md` — JP4 footprint-revision attribution corrected across §1,
  §3, §4, §5, §6, §7; "JP4 Caveat" retracted; §8/§9 "via JP4" phrasing corrected; §6's 24-pin
  legacy UV-EPROM row revision-qualified; new "Rev 2.2 provenance discipline" section added.

## Decisions Made

See `key-decisions` in frontmatter. No decisions beyond what the plan and CONTEXT.md's D-10
through D-15 already locked — this plan executes the trace those decisions specified and
records exactly what it found, including the two additional wrong claims (footprint-revision
attribution, and the stale `file:LINE` citation) that surfaced only while doing the citation
work D-13 and the plan's own verify legs required.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed a stale `file:LINE` citation found during the mandated citation
round-trip**
- **Found during:** Task 2, citation-hygiene pass (the plan's own instruction: "re-check every
  `file:LINE` citation inside the regions you touched... round-trip one of them")
- **Issue:** `182-RESEARCH.md` and this plan's own draft of the gh#60 section cited
  `firestarter/include/rurp_pinout.h:144` for `#define CTRL_ADDRESS_LINE_18_REV2
  CTRL_VPP_P1_ENABLE_REV2`. Reading the file directly (HEAD `c14f191`, byte-identical to
  `origin/beta` on this file) showed the alias is at line 149, not 144. The substance was
  correct; the line number was off by five.
- **Fix:** Corrected the citation to `:149` in both `jumper-display-ground-truth.md` and the
  round-trip note added to `v1.7-SHIELD-REVS.md`.
- **Files modified:** `.planning/notes/jumper-display-ground-truth.md`,
  `.planning/v1.7-SHIELD-REVS.md`
- **Verification:** `sed -n '149p' firestarter/include/rurp_pinout.h` confirmed the line reads
  `#define CTRL_ADDRESS_LINE_18_REV2          CTRL_VPP_P1_ENABLE_REV2`.
- **Committed in:** `2d102f19` (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 bug — stale citation).
**Impact on plan:** Necessary for the citation-hygiene requirement the plan itself imposed. No
scope creep; no code changed.

## Issues Encountered

None beyond the deviation above. Writing corrections into `v1.7-SHIELD-REVS.md` without line
wraps splitting a quoted phrase from its safety-word annotation required two rounds of
self-correction against the plan's own grep verify legs (the file's markdown table rows and
prose are grep-matched per physical line, so a wrapped sentence can silently fail a same-line
check) — resolved before committing by re-running every verify leg from the plan and fixing
the two lines that failed.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- SAFE-03 is met for this phase's scope: the VPP-destination table and the gh#60 answer are
  recorded with per-claim citations, and the R41/JP4 record correction is in place.
- Plan 06 (bench-measurement checkpoint) has its work cut out precisely: the J6 pin 4 VPE
  probe (assumption A1), the three PROBE-PENDING cells (Rev 2.0/2.1 pole destination, Rev 2.2
  pad orientation, Rev 0/1 JP3 routing), and the D-14 falsification read (hw_revision at each
  JP4 position, predicted no change).
- Plan 07 has two backlog items to file: the 255-row `DIP32_SST39SF040` structural remainder,
  and D-15's two findings (DIP24 unreachable VPP, the mirrored JP4 24-pin-position hazard).
- The D-09 phase (not yet numbered) inherits a corrected, citable foundation:
  `jumper-display-ground-truth.md`'s JP4 row and the VPP-destination table are consistent with
  `v1.7-SHIELD-REVS.md`'s corrected JP4 claims — verified by review, no contradiction found.

---
*Phase: 182-jp5-destructive-operation-gate*
*Completed: 2026-09-10*

## Self-Check: PASSED

- FOUND: `.planning/notes/jumper-display-ground-truth.md`
- FOUND: `.planning/v1.7-SHIELD-REVS.md`
- FOUND commit: `cfc0dc71`
- FOUND commit: `2d102f19`
- Plan-level `<verification>` re-run: `PROBE-PENDING` count 3 (>=3, pass); R41-coupling claim
  absent (pass); `git diff --stat HEAD~2` shows exactly the two `.planning/` files this plan
  names and no others (pass).
