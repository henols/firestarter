---
phase: 119-lock-sdp-enable-command-surface-fw-half
plan: "09"
subsystem: docs-planning
tags: [meta, roadmap, requirements, project-md, state-md, devtest-01, lock-04, lock-06, correction-record]

# Dependency graph
requires:
  - phase: 119-lock-sdp-enable-command-surface-fw-half
    plan: "07"
    provides: "LOCK-04 Complete (mechanism-corrected, intent-satisfied); LOCK-02 Complete; DEVTEST-01's firmware half proven end to end (cases 24/25, case group 4)"
  - phase: 119-lock-sdp-enable-command-surface-fw-half
    plan: "08"
    provides: "Full per-plan flash decomposition against the live 2992 B Leonardo headroom, landing at 2600 B free; the release-config 24388/28672 (1292 B DEV_TOOLS cost) figure restated from RESEARCH"
provides:
  - "ROADMAP.md's Phase 121 one-line entry and Phase Details criterion 2 amended to record DEVTEST-01's firmware half as landed early in Phase 119, naming the generic NULL-main mechanism, with Phase 121 retaining only the host half"
  - "ROADMAP.md's Phase 119 Phase Details block carries a correction note for superseded criteria 4/5/6 (LOCK-04 mechanism, criterion 5's relocated header comment, LOCK-06's live 2992 B headroom)"
  - "REQUIREMENTS.md's DEVTEST-01 requirement text and traceability row record the firmware/host split by phase; checkbox stays unticked; Coverage sentence updated to describe the split without changing the 36/36 total"
  - "PROJECT.md's SIXTH CORRECTION block: 7 items covering LOCK-04's mechanism correction, criterion 5's relocation, LOCK-06's superseded headroom + the binding 1292 B DEV_TOOLS cost, DEVTEST-01's early landing, the three command behaviour deltas (incl. CMD_IDLE), the _SRAM_PROTO_IDS KEEP disposition for Phase 120, and the new host gate + retired sdp_expected.h blob-SHA shorthand"
  - "Folded todo prove-pio-dev-flag-fails-closed.md's item 4 extended with the 1292 B DEV_TOOLS flash-cost figure; items 1-3 confirmed still open under 999.15/gh#8"
  - "STATE.md hand-corrected after state.record-session re-clobbered current_phase_name/stopped_at/last_activity_desc/completed_plans/percent, per the file's own documented tooling-underwrite pattern"
affects: [119-10, 119-11, 121, 122]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "PROJECT.md correction-block convention: numbered items, each opening with a bold one-line label, citing the D-NN/F-NNN decision it corrects, and explicitly stating whether REQUIREMENTS.md wording was left untouched"
    - "ROADMAP scope amendment for a capability that landed early: amend both the one-line milestone entry AND the Phase Details success criterion, name the mechanism, and add an explicit 'why it moved' note framing it as operator-approved scope addition rather than a leak"

key-files:
  created: []
  modified:
    - .planning/ROADMAP.md
    - .planning/REQUIREMENTS.md
    - .planning/PROJECT.md
    - .planning/STATE.md
    - .planning/todos/pending/prove-pio-dev-flag-fails-closed.md

key-decisions:
  - "DEVTEST-01's checkbox stays unticked in REQUIREMENTS.md — only the mapping (firmware half → Phase 119, host half → Phase 121) and the Phase 121 scope text changed. This plan does not close the requirement."
  - "LOCK-04's and LOCK-06's requirement WORDING in REQUIREMENTS.md was not touched, per D-05/D-15's explicit prohibition — only ROADMAP.md's Phase 119 Phase Details block and PROJECT.md's sixth correction block record the mechanism corrections."
  - "PROJECT.md's sixth correction block groups all seven required items (LOCK-04, criterion 5, LOCK-06/1292B, DEVTEST-01 move, three behaviour deltas, _SRAM_PROTO_IDS KEEP, the new host gate + retired blob-SHA shorthand) in the same numbered-item shape as the five prior correction blocks, rather than splitting them across separate paragraphs."
  - "The folded todo's item 4 was already answered by Plan 119-02 (112/112 with DEV_TOOLS absent) — this plan does not re-answer it, only extends it with the 1292 B DEV_TOOLS flash-cost figure measured via RESEARCH's temporary [env:leonardo_nodevtools] build and restated in 119-08's flash decomposition. Items 1-3 remain explicitly open, scoped to 999.15/gh#8."
  - "STATE.md was hand-corrected after state.record-session, per the file's own documented sequence: called record-session first, then advance-plan/update-progress/record-metric/add-decision, then diffed the file and hand-fixed current_phase_name's dropped closing paren, stopped_at, last_activity_desc, progress.completed_plans (27→28) and progress.percent (43→93) — all of which the tooling re-clobbered exactly as previously observed."

requirements-completed: []

coverage:
  - id: D1
    description: "ROADMAP.md's Phase 121 one-line entry and Phase Details criterion 2 amended: the firmware fail-close is recorded as landed in Phase 119 (generic NULL-main refusal, MSG_ERR_NOT_SUPPORTED/RESPONSE_CODE_ERROR), Phase 121 retains only the host OP_ERASE->NA half, with an explicit 'why it moved' note"
    verification:
      - kind: unit
        ref: "git diff --stat .planning/ROADMAP.md -- 9 lines changed (small, targeted); grep -n 'landed EARLY, in Phase 119' .planning/ROADMAP.md -- present"
        status: pass
    human_judgment: false
  - id: D2
    description: "ROADMAP.md's Phase 119 Phase Details block carries a correction note for criteria 4/5/6 (LOCK-04 mechanism-corrected/intent-satisfied, criterion 5's header comment relocated to eeprom_28c.cpp, criterion 6's 3348B superseded by live 2992B)"
    verification:
      - kind: unit
        ref: "grep -n 'Mechanism-corrected, intent-satisfied' .planning/ROADMAP.md -- present in Phase 119's Phase Details block"
        status: pass
    human_judgment: false
  - id: D3
    description: "REQUIREMENTS.md's DEVTEST-01 block and traceability row record the firmware/host split by phase; checkbox unticked; Coverage sentence updated; LOCK-04/LOCK-06 wording untouched"
    verification:
      - kind: unit
        ref: "git diff .planning/REQUIREMENTS.md -- only the DEVTEST-01 requirement line, its traceability row, and the Coverage 'Mapped to phases' sentence changed (6 lines); grep -n 'LOCK-04\\|LOCK-06' shows no diff to those lines"
        status: pass
    human_judgment: false
  - id: D4
    description: "PROJECT.md's SIXTH CORRECTION block added in the same shape as the existing five, with all seven required items"
    verification:
      - kind: unit
        ref: "grep -c 'SIXTH\\|_SRAM_PROTO_IDS\\|2992\\|1292' .planning/PROJECT.md -- 3 (matches); manual read confirms 7 numbered items present"
        status: pass
    human_judgment: false
  - id: D5
    description: "Folded todo item 4 extended with the 1292 B DEV_TOOLS cost figure; items 1-3 confirmed open under 999.15/gh#8; todo not closed"
    verification:
      - kind: unit
        ref: "grep -n '1292 B\\|999.15' .planning/todos/pending/prove-pio-dev-flag-fails-closed.md -- present; no 'CLOSED'/'resolved' marker added to the file"
        status: pass
    human_judgment: false
  - id: D6
    description: "STATE.md's frontmatter hand-verified correct after the record-session call re-clobbered current_phase_name/stopped_at/last_activity_desc/completed_plans/percent; body Current Position and a new Plan 119-09 outcome paragraph added"
    verification:
      - kind: unit
        ref: "grep -n 'current_phase_name: LOCK — SDP-enable + command surface (FW half)' .planning/STATE.md -- closing paren present (was dropped by state.record-session); grep -n 'completed_plans: 28' and 'percent: 93' -- present"
        status: pass
    human_judgment: false
  - id: D7
    description: "Both sub-repo working trees clean at the end of this plan; commit stages only .planning/ paths; no requirement marked Complete"
    verification:
      - kind: unit
        ref: "git -C /workspaces/firestarter status --short -- empty; git show --stat HEAD (both commits) -- only .planning/ paths listed"
        status: pass
    human_judgment: false

duration: ~30min
completed: 2026-07-28
status: complete
---

# Phase 119 Plan 09: D-08's Owned Amendment — Phase 121 Scope + DEVTEST-01 Mapping + PROJECT.md's Sixth Correction Summary

**Amended Phase 121's ROADMAP scope and REQUIREMENTS.md's DEVTEST-01 mapping to record that the firmware fail-close (a generic op-layer NULL-`main` refusal, not a `0x0D`-local `default:` arm) landed early in Phase 119, added PROJECT.md's sixth correction block gathering all of this phase's mechanism-vs-intent divergences and behaviour deltas, and hand-corrected STATE.md after its tooling re-clobbered five fields exactly as previously documented — with DEVTEST-01's checkbox still unticked and zero requirement status changes.**

## Performance

- **Duration:** ~30 min
- **Completed:** 2026-07-28
- **Tasks:** 2/2
- **Files modified:** 5 (`.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md`, `.planning/PROJECT.md`, `.planning/STATE.md`, `.planning/todos/pending/prove-pio-dev-flag-fails-closed.md`)

## Accomplishments

- **Task 1 — Phase 121 + DEVTEST-01 mapping amended.** `ROADMAP.md`'s Phase 121 one-line milestone entry now records that the firmware fail-close (`OP_ERASE`/`CMD_ERASE` phantom-success class) already landed in Phase 119 under D-06/D-07/D-08, naming the generic op-layer NULL-`main` mechanism, and states Phase 121's remaining work is the host-side `NA` marking only. Phase 121's Phase Details criterion 2 was rewritten in the same shape: **"Satisfied by Phase 119, landed early"**, naming `op_execute_stateful_operation`, `MSG_ERR_NOT_SUPPORTED`/`RESPONSE_CODE_ERROR`, and an explicit *"why it moved"* parenthetical framing this as an operator-approved scope addition (the cross-family sweep accepted), never a leak. Phase 119's own Phase Details block gained a correction note for criteria 4 (LOCK-04's `default:` arm disproven; mechanism-corrected/intent-satisfied by D-06), 5 (the header comment relocated to `eeprom_28c.cpp` because `flash_utils.h` is FIX-04 byte-frozen) and 6 (LOCK-06's `3348 B` superseded by the live `2992 B` figure). `REQUIREMENTS.md`'s DEVTEST-01 requirement line and its traceability row now record the phase split (firmware → Phase 119, host → Phase 121); the Coverage "Mapped to phases" sentence was updated to describe the split while the 36/36 total and 0-unmapped count are unchanged. **Checkbox stays `- [ ]`.** `git diff --stat` confirmed both `ROADMAP.md` (9 lines) and `REQUIREMENTS.md` (6 lines) changes are small and targeted; `git diff .planning/REQUIREMENTS.md` showed no touch to LOCK-04's or LOCK-06's wording.
- **Task 2 — PROJECT.md's sixth correction block, the todo closeout, and STATE.md.** Added a **SIXTH CORRECTION** block to `PROJECT.md`'s "Current Milestone: v1.22" section, in the same numbered-item shape as the five existing blocks, with all seven required items (see below). Extended the already-answered item 4 of `.planning/todos/pending/prove-pio-dev-flag-fails-closed.md` with the 1292 B `-D DEV_TOOLS` flash-cost figure (25680 − 24388, measured via RESEARCH's temporary `[env:leonardo_nodevtools]` build and restated in Plan 119-08); confirmed items 1-3 remain open, scoped to 999.15/gh#8, and the todo file is not closed. Ran the prescribed STATE.md sequence — `state.record-session` first, then `state.advance-plan`/`state.update-progress`/`state.record-metric` × 2 `state.add-decision` calls — diffing the file before and after each call. As documented in the file's own HTML comment, `state.record-session` re-clobbered `current_phase_name` (dropped its closing `)`), left `stopped_at`/`last_activity_desc` stale at "Completed 119-08-PLAN.md", and reverted `progress.completed_plans`/`percent` to stale values (27/43 instead of 28/93) despite an intervening `state.advance-plan` + `state.update-progress` having set them correctly moments earlier. All five hand-corrected. Confirmed `firestarter/` and `firestarter_app/` working trees clean (aside from `firestarter_app`'s pre-existing, unrelated untracked/modified files carried from earlier sessions).

## PROJECT.md's Sixth Correction Block — the Seven Items

1. **LOCK-04's mechanism is superseded (D-05).** `configure_eeprom28c`'s `default:` arm would have refused `read`/`verify` on all 84 `0x0D` chips; D-06's single generic NULL-`main` refusal satisfies the intent instead. Mechanism-corrected, intent-satisfied — LOCK-04's `REQUIREMENTS.md` wording untouched.
2. **Criterion 5's header comment moved (RESEARCH F-K).** `flash_utils.h` is FIX-04 byte-frozen; the datasheet rationale lives beside `EEPROM_SDP_ENABLE` in `eeprom_28c.cpp` plus `test_sdp_harness.cpp:291-296`, machine-checked by the three-way identity/distinctness guard and a host source-text parity leg. This is the fourth mechanism-vs-intent divergence this milestone has produced.
3. **LOCK-06's `3348 B` is superseded (D-15) and `-D DEV_TOOLS` is confirmed the binding, tighter configuration.** Live Leonardo figure: `25680/28672` → **2992 B** free. Release-config (`DEV_TOOLS` absent) measured `24388/28672` → the flag **costs 1292 B**, so the `DEV_TOOLS` build carries the smaller headroom and remains the binding constraint. LOCK-06's `REQUIREMENTS.md` wording untouched.
4. **DEVTEST-01's firmware half landed in Phase 119, early (D-07/D-08).** The same generic NULL-`main` refusal closes `CMD_ERASE`'s and `CMD_CHECK_CHIP_ID`'s phantom-success on `0x0D`; Phase 121 keeps the host `NA`-marking half. This plan's own amendment is cross-referenced, not restated.
5. **Three command behaviour deltas, all deliberate.** Cmd 7/8 no longer reach `configure_memory` in a release build (D-01); **cmd 0 / `CMD_IDLE`** (RESEARCH F-B2, which D-01 does not name) now produces silence instead of two error frames — an explicit refusal arm was considered and declined on flash grounds.
6. **`_SRAM_PROTO_IDS` does NOT become dead code (RESEARCH F-F2).** The host's SRAM/FRAM blank-check short-circuit fires before D-06's guard is reachable; correct Phase 120 disposition is **KEEP**, identified here, not acted on.
7. **A new host gate joins the CORRECTION-4 checklist, and one blob-SHA shorthand is retired.** `check_is_memory_cmd_no_ifdef.py` (Plan 119-03) is added to the Phases 120-122 checklist alongside the eight pre-existing gates; `_shared/sdp_expected.h`'s whole-file blob-SHA shorthand no longer applies (Plan 119-05 added four new arrays) — its identity proof is per-array byte-identity of the pre-existing arrays.

## Task Commits

Each task was committed atomically in `/workspaces` (meta-repo only, no submodule touched):

1. **Task 1: Amend Phase 121's ROADMAP scope and REQUIREMENTS.md's DEVTEST-01 mapping** — `ea3b5ff` (docs)
2. **Task 2: Add PROJECT.md's sixth correction block, close out todo item 4, and hand-verify STATE.md** — `61b8777` (docs)

**Plan metadata:** committed alongside this SUMMARY (docs, meta commit staging SUMMARY.md + STATE.md + ROADMAP.md + REQUIREMENTS.md).

## Files Created/Modified

- `.planning/ROADMAP.md` — Phase 121's one-line entry + Phase Details criterion 2 amended; Phase 119's Phase Details block gained a criteria 4/5/6 correction note
- `.planning/REQUIREMENTS.md` — DEVTEST-01 requirement text + traceability row + Coverage sentence, only
- `.planning/PROJECT.md` — the SIXTH CORRECTION block (7 items)
- `.planning/todos/pending/prove-pio-dev-flag-fails-closed.md` — item 4 extended with the 1292 B figure; items 1-3 confirmed open
- `.planning/STATE.md` — Current Position updated, a new Plan 119-09 outcome paragraph added, frontmatter hand-corrected (`current_phase_name`, `stopped_at`, `last_activity_desc`, `progress.completed_plans`, `progress.percent`)

## Decisions Made

See `key-decisions` in frontmatter for the five load-bearing ones (DEVTEST-01 checkbox stays unticked, LOCK-04/LOCK-06 wording untouched, the sixth correction block's seven-item shape, the todo's item-4 extension vs. re-answering, and the STATE.md hand-correction sequence). All match the plan's `must_haves.truths`/`prohibitions` verbatim; none required deviation from the plan's explicit instructions.

## Deviations from Plan

None — plan executed exactly as written. Both tasks' acceptance criteria were met without any Rule 1-4 auto-fixes. The STATE.md tooling under-write was **anticipated by the plan itself** (`must_haves.truths` item on STATE.md tooling) and handled via the prescribed sequence, not treated as a deviation.

## Issues Encountered

None beyond the anticipated and prescribed-for STATE.md tooling under-write, documented above and in Decisions Made.

## User Setup Required

None — no external service configuration required.

## Known Stubs

None. This plan is meta-documentation-only; no UI or data-rendering path is affected.

## Requirement Status

**No requirement marked Complete by this plan**, per the plan's explicit instruction. `DEVTEST-01` **stays Pending**, checkbox unticked — only its phase mapping changed (firmware half attributed to Phase 119, host half to Phase 121). `LOCK-01` through `LOCK-05` remain Complete, untouched; `LOCK-06` remains Pending (closes in Plans 119-10/119-11).

## Next Phase Readiness

- A Phase 121 planner reading `ROADMAP.md`/`REQUIREMENTS.md` will find the firmware half recorded as already shipped in Phase 119 with the mechanism named, and only the host half theirs — the discovery D-08 exists to prevent will not occur.
- `PROJECT.md`'s sixth correction block is in place for Plan 119-10's non-regression sweep and Plan 119-11's bench measurement to cite rather than re-derive.
- The folded todo shows exactly item 4 answered (now with the 1292 B figure), items 1-3 still open under 999.15/gh#8.
- `STATE.md` agrees with reality: Plan 10 of 11 next, all five hand-corrected frontmatter fields verified.
- No blockers for Plan 119-10.

---
*Phase: 119-lock-sdp-enable-command-surface-fw-half*
*Completed: 2026-07-28*

## Self-Check: PASSED

- FOUND: `.planning/ROADMAP.md` Phase 121 + Phase 119 amendments
- FOUND: `.planning/REQUIREMENTS.md` DEVTEST-01 mapping + Coverage sentence
- FOUND: `.planning/PROJECT.md` SIXTH CORRECTION block
- FOUND: `.planning/todos/pending/prove-pio-dev-flag-fails-closed.md` item 4 extension
- FOUND: `ea3b5ff` (Task 1 commit)
- FOUND: `61b8777` (Task 2 commit)
