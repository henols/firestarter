---
phase: 121-dev-test-fix-gates-docs-redesign
plan: 13
subsystem: docs
tags: [documentation, sdp, gate-02, lockable-proms, community-validation, cross-repo]

# Dependency graph
requires:
  - phase: 121-12
    provides: D-15's messages.toml SDP unlock-done symmetry caveat (GATE-02 contributes-only)
  - phase: 121-09
    provides: the always-writes/UV-only-ask contract these docs now describe
  - phase: 121-08
    provides: FLAG_CAN_ERASE cleared for protocol 0x0D, the family-fact NA erase reason
provides:
  - "Eight docs across both sub-repos corrected to match the post-fix SDP/erase model and the always-writes reality"
  - "doc/lockable-proms.md first-committed (was untracked) with its wrong §17 Atmel row split against sdp_capability.py's derived allow-set"
  - "GATE-02 closed"
affects: [121-14]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Doc-list widening recorded in the requirement's traceability sentence, never in the requirement's own wording (D-17, following LOCK-04/LOCK-06/HOST-04/D-06)"

key-files:
  created: []
  modified:
    - firestarter/doc/PROTOCOLS.md
    - firestarter/CLAUDE.md
    - firestarter/README.md
    - firestarter_app/doc/protocol-id.md
    - firestarter_app/doc/lockable-proms.md
    - firestarter_app/doc/community-validation.md
    - firestarter_app/doc/beta-testing-install.md
    - firestarter_app/README.md
    - .planning/REQUIREMENTS.md

key-decisions:
  - "lockable-proms.md's §17 Atmel row split strictly against sdp_capability.py's SDP_CAPABLE_TOKENS membership, never the doc's own prior prose -- AT28C64B/AT28C256(+variants) stay SDP-capable, AT28C16(+E/F)/plain AT28C64 are described as byte-write parts with no SDP command decoder"
  - "No provenance header added to lockable-proms.md (D-16, an owned trade-off) -- first 10 lines of the file are byte-identical to the pre-commit working tree"
  - "The unrelated 'non-destructive' phrase describing the fw/hw smoke test in beta-testing-install.md step 6 was reworded (not just the dev-test paragraph) to satisfy the plan's literal grep acceptance criterion while staying accurate -- that sentence was never wrong, just coincidentally sharing a banned substring"

requirements-completed: [GATE-02]

coverage:
  - id: D1
    description: "Each of firestarter/doc/PROTOCOLS.md, CLAUDE.md, README.md and firestarter_app/doc/protocol-id.md contains an explicit statement that protocol 0x0D has no erase operation"
    requirement: GATE-02
    verification:
      - kind: other
        ref: "grep -ci 'no erase' doc/PROTOCOLS.md CLAUDE.md README.md (firestarter) -> 2, 2, 1; grep -ci 'no erase' doc/protocol-id.md (firestarter_app) -> 1"
        status: pass
    human_judgment: false
  - id: D2
    description: "PROTOCOLS.md states the SDP protection state is not readable and the blank-check-skip-flag consequence (required + skips only the blank check on this family); the pre-fix 'permanently disables SDP' wording is gone"
    requirement: GATE-02
    verification:
      - kind: other
        ref: "grep -n 'not readable' doc/PROTOCOLS.md; grep -ci 'permanently disable' doc/PROTOCOLS.md -> 0; grep -c '84' doc/PROTOCOLS.md -> 3 (bucket table row unchanged)"
        status: pass
    human_judgment: true
  - id: D3
    description: "doc/lockable-proms.md is tracked, §17's Atmel row corrected against the derived allow-set, and no provenance header was added"
    requirement: GATE-02
    verification:
      - kind: other
        ref: "git -C firestarter_app ls-files doc/lockable-proms.md -> doc/lockable-proms.md; first-10-lines diff empty"
        status: pass
    human_judgment: false
  - id: D4
    description: "doc/beta-testing-install.md, doc/community-validation.md and README.md (host) each state dev test writes to the chip; 'non-destructive' is gone from all three; the doubled run count and the fingerprint-based N>=2 argument are both documented"
    requirement: GATE-02
    verification:
      - kind: other
        ref: "grep -ci 'writes to the chip' -> 1/1/1; grep -ci 'non-destructive' -> 0/0/0; grep -n 'twice' doc/beta-testing-install.md"
        status: pass
    human_judgment: false
  - id: D5
    description: "Full host pytest suite is green (docs-only change, suite must not have moved) and both sub-repo working trees are clean at task end (git status --porcelain, not a path-scoped diff)"
    requirement: GATE-02
    verification:
      - kind: other
        ref: "python3 -m pytest tests/ -p no:cacheprovider -q -> 1134 passed in 62.02s, exit 0"
        status: pass
      - kind: other
        ref: "git -C firestarter status --porcelain -> only pre-existing untracked firestarter/firestarter/; git -C firestarter_app status --porcelain -> only pre-existing dirt (.gitignore, .coverage, SECURITY.md, write_test_port.sh, .planning/config.json)"
        status: pass
    human_judgment: false
  - id: D6
    description: "GATE-02 ticked in REQUIREMENTS.md with a traceability sentence naming plan 121-13 and recording D-17's two-document widening; GATE-02's own requirement wording is unedited; no other requirement row changed"
    requirement: GATE-02
    verification:
      - kind: other
        ref: "git diff .planning/REQUIREMENTS.md -- only the GATE-02 checkbox line and its traceability-table row changed"
        status: pass
    human_judgment: false

# Metrics
duration: ~50min
completed: 2026-07-29
status: complete
---

# Phase 121 Plan 13: Cross-Repo Doc Corrections + Always-Writes Reality Summary

**Corrected all eight GATE-02-named docs across both sub-repos to describe the post-fix SDP/erase model (no erase on protocol 0x0D, SDP protection state not readable) and the always-writes reality (D-04), and first-committed `doc/lockable-proms.md` with its wrong AT28C16/64 row split against `sdp_capability.py`'s derived allow-set — closing GATE-02.**

## Performance

- **Duration:** ~50 min
- **Completed:** 2026-07-29
- **Tasks:** 2/2
- **Files modified:** 9 (8 declared docs + `.planning/REQUIREMENTS.md`)

## Accomplishments

### Task 1 — Firmware docs + protocol-id.md (post-fix SDP/erase model)

- **`firestarter/doc/PROTOCOLS.md` §1.6**: replaced the pre-fix "Firmware permanently disables SDP via a 6-cycle sequence before writing" wording with the current model — firmware emits the SDP-disable sequence on the protocol-0x0D-local emitter (Phase 117), reports before/after with a `micros()`-measured duration (Phase 118), the user can decline via `--skip-sdp-unlock` (Phase 120), and the SDP protection state is **not readable** either way, so nothing may be inferred about a part's protection state from a successful emission.
- Corrected the erase model: firmware implements **no erase operation at all** for protocol `0x0D` (`configure_eeprom28c()` has no erase entry point of any kind); the host's general `FLAG_CAN_ERASE` derivation from `electrical.type` is authoritative for every other protocol but is deliberately cleared for all 84 `0x0D` chips (Phase 121 D-12); named the operational consequence — `--skip-erase` has nothing to skip and warns, while `-b`/`--no-blank-check` is *required* on a non-blank AT28C and, on this family only, skips the blank check and nothing else.
- Left the `0x0D` bucket table row's 84-chip count untouched (validation ceiling).
- **`firestarter/CLAUDE.md`**: added the same fact to the 0x0D table row's Notes cell and a new "Protocol 0x0D notes" section pointing to `doc/PROTOCOLS.md` §1.6.
- **`firestarter/README.md`**: added a two-sentence "Protocol Notes" section (README depth, not a protocol essay).
- **`firestarter_app/doc/protocol-id.md`**: extended the `0x0D` row's Notes column only — no restructuring, no other row touched.

### Task 2 — lockable-proms.md ship + always-writes reality

- **`firestarter_app/doc/lockable-proms.md`** (first commit, was untracked): split §17's wrong "Atmel AT28C16 / 64 / 256" row into two rows, cross-checked against `sdp_capability.py`'s `SDP_CAPABLE_TOKENS` — see the membership check below. No provenance header added (D-16). First 10 lines of the file are unchanged from the pre-commit working tree.
- **`firestarter_app/doc/beta-testing-install.md`**: replaced the "This runs a non-destructive-by-default capability sweep" sentence (the single most wrong line in the doc set) with the always-writes reality — writes to the chip, UV stop-and-ask (yes=full, no/no-TTY=256B region), every other family written in full twice, no read-only answer. Also reworded step 6's unrelated "non-destructive" smoke-test sentence to satisfy the plan's literal grep check while remaining accurate (that sentence was never wrong, it just shared the banned substring incidentally).
- **`firestarter_app/doc/community-validation.md`**: corrected the intro to state `dev test` writes; added to the `community-reported` row that a `write-partial` run earns the identical auto-tag as a full round-trip; added the fingerprint-based argument explaining why that can never poison N≥2 (`dedup_fingerprint` differentiates partial from full, so `count_agreeing`'s grouping can never cross-agree the two) — Phase 114's GRAD-01 lock holds through the fingerprint, not the tag. `community-confirmed` row left untouched (still human-gated-only).
- **`firestarter_app/README.md`**: added a two-sentence always-writes warning next to the existing flag-free `dev test <chip>` invocation callout.
- **`.planning/REQUIREMENTS.md`**: ticked `GATE-02`, appended a traceability sentence naming Plan 121-13 and recording D-17's widening (adding `doc/community-validation.md` and `doc/beta-testing-install.md` to the named doc list) without editing GATE-02's own requirement wording. Traceability table row updated to `Plan 121-13 | Complete`. No other requirement row touched (verified by `git diff`).

## §17 Atmel Row — Old vs New, Cross-Checked Against `sdp_capability.py`

**Old (wrong) row:**
```
| **Atmel AT28C16 / 64 / 256**      | Usually no explicit SDP flag | SDP can be enabled/disabled             |
```

**New (split) rows:**
```
| **Atmel AT28C64B / AT28C256** (page-write EEPROMs; incl. BV/LV/HC/MC variants) | Usually no explicit SDP flag | SDP can be enabled/disabled |
| **Atmel AT28C16** (incl. AT28C16E/F) and **plain AT28C64** | No — no SDP command decoder at all | Earlier-generation byte-write parts; not SDP-capable, unlike AT28C64B/AT28C256 above |
```

**Membership check against `sdp_capability.py:SDP_CAPABLE_TOKENS`** (ground truth per D-16's instruction, never the doc's own prose):
- `AT28C64B`, `AT28HC64B`, `AT28HC64BF` — **in** allow-set → stays SDP-capable.
- `AT28C256`, `AT28C256E`, `AT28C256F`, `AT28HC256`, `AT28HC256E`, `AT28HC256F`, `AT28HC256L` — **in** allow-set → stays SDP-capable.
- `AT28C16`, `AT28HC16`, `AT28HC16L` (DB entry `AT28C16,AT28HC16,AT28HC16L`) — **none** in allow-set → refused.
- `AT28C16E`, `AT28C16F` (DB entry `AT28C16E,AT28C16F`) — **none** in allow-set → refused.
- Plain `AT28C64` (DB entry `AT28C64,AT28C64B(Non-Standard),AT28HC64,AT28HC64L`) — none of these four tokens (note the parenthetical form `AT28C64B(Non-Standard)` is kept verbatim per `split_part_number_tokens` and does **not** match the plain `AT28C64B` allow-set token) are in the allow-set → this whole DB entry refuses unanimously, confirming the doc's new "plain AT28C64" row is correct even though it visually resembles the SDP-capable `AT28C64B`.

This matches `.planning/STATE.md`'s Phase 120 finding verbatim: AT28C16, its E/F variants, and plain AT28C64 are all outside the derived SDP-capable set (byte-write parts).

## Consistency Check Across the Three Tester-Facing Docs

Re-read `doc/beta-testing-install.md`, `doc/community-validation.md`, and `README.md` together after editing: all three now state, in the reader's first encounter with `dev test`, that it (a) writes to the chip, (b) asks only on a UV-erasable part (yes=full, no/no-TTY=partial), and (c) writes every other family in full with no prompt. This agrees with the command's own first-line notice (`_ALWAYS_WRITES_NOTICE` in `cli_handlers.py`, landed in Plan 121-09): *"dev test ALWAYS WRITES to the chip -- run it only on a blank or scratch part you are willing to sacrifice. Every write/verify/erase step runs TWICE per invocation..."* No reconciliation was needed beyond wording — no doc disagreed with another on substance.

## Validation-Ceiling Review (sentence by sentence, per task)

Every added/changed sentence across both tasks was re-read against `.planning/REQUIREMENTS.md`'s Validation Ceiling section before commit. None claims or implies SDP has been demonstrated on real AT28C silicon; none changes a `support_status`; none changes the 84-chip count.

| # | Added claim | Disposition |
|---|---|---|
| 1 | PROTOCOLS.md: firmware emits SDP-disable sequence, reports before/after, protection state not readable | **Permitted** — measured host-side/firmware behavior fact; explicitly disclaims silicon-state inference |
| 2 | PROTOCOLS.md: 0x0D has no erase operation at all; host clears FLAG_CAN_ERASE for 84 chips | **Permitted** — a source-code/DB-transform fact, not a silicon-behavior claim |
| 3 | CLAUDE.md / README.md (firmware): same facts at reference/README depth | **Permitted** — same facts, shorter form |
| 4 | protocol-id.md: 0x0D has no erase; host clears FLAG_CAN_ERASE | **Permitted** — same fact |
| 5 | lockable-proms.md §17 split: AT28C16/plain-AT28C64 have no SDP command decoder; AT28C64B/AT28C256 do | **Permitted** — datasheet-sourced capability claim (same evidentiary class the rest of the ~300-row table already carries), not a verification claim |
| 6 | beta-testing-install.md / community-validation.md / README.md (host): dev test always writes, UV stop-and-ask, doubled run count | **Permitted** — describes host command behavior (landed in Plan 121-09), not a silicon-validation claim |
| 7 | community-validation.md: partial-run auto-tag + fingerprint-based N≥2 argument | **Permitted** — describes report-side mechanics (`dedup_fingerprint`/`count_agreeing`), not a chip-support claim |

No sentence required rewording after this review — every draft already satisfied the ceiling on first pass.

## Task Commits

Each task was committed atomically, per sub-repo:

**Task 1:**
1. `firestarter` — `48c36e5` (docs): PROTOCOLS.md §1.6, CLAUDE.md, README.md
2. `firestarter_app` — `4149ee8` (docs): protocol-id.md

**Task 2:**
3. `firestarter_app` — `c3c9424` (docs): lockable-proms.md (first commit), community-validation.md, beta-testing-install.md, README.md

`.planning/REQUIREMENTS.md`'s GATE-02 edit is committed in the meta repo alongside this SUMMARY (see final commit).

## Files Created/Modified

- `firestarter/doc/PROTOCOLS.md` — §1.6 Write algorithm + Erase model rewritten
- `firestarter/CLAUDE.md` — 0x0D table row Notes extended + new "Protocol 0x0D notes" section
- `firestarter/README.md` — new two-sentence "Protocol Notes" section
- `firestarter_app/doc/protocol-id.md` — 0x0D row Notes extended
- `firestarter_app/doc/lockable-proms.md` — first commit; §17 Atmel row split
- `firestarter_app/doc/community-validation.md` — intro, community-reported row, N≥2 fingerprint argument
- `firestarter_app/doc/beta-testing-install.md` — sweep paragraph rewritten; step 6 wording adjusted
- `firestarter_app/README.md` — always-writes warning added next to the `dev test` callout
- `.planning/REQUIREMENTS.md` — GATE-02 ticked with traceability sentence

## Decisions Made

- §17's Atmel split is sourced strictly from `sdp_capability.py`'s allow-set membership, never the doc's own prior prose (per D-16's explicit instruction), and the per-part membership check is recorded above rather than merely asserted.
- No provenance/uncertainty header was added to `lockable-proms.md` — D-16 rejected that explicitly; this is an owned trade-off, recorded so no downstream agent re-opens it.
- The unrelated "non-destructive" sentence describing the `fw`/`hw` smoke test (beta-testing-install.md step 6) was reworded to satisfy the plan's literal file-wide grep acceptance criterion, even though that specific sentence was never inaccurate — it just happened to share the banned substring with the sweep-destructiveness claim the plan targets.

## Deviations from Plan

None — plan executed exactly as written. The one judgment call (rewording the unrelated step-6 "non-destructive" sentence) was required by the plan's own literal acceptance-criteria grep and is recorded above, not treated as a deviation from the plan's intent.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- GATE-02 is closed; all eight named docs (widened per D-17) are corrected and consistent with each other and with the command's own first-line notice.
- Plan 121-14 (GATE-03, the final non-regression sweep) can proceed — it re-verifies every requirement row at the phase's final commit, including re-confirming GATE-02 stays ticked and that no row this plan didn't touch changed.
- No blockers. Full host suite green at 1134 passed / 0 failed; both sub-repo working trees left in their pre-existing dirty state only (no new untracked/uncommitted files introduced by this plan).

---
*Phase: 121-dev-test-fix-gates-docs-redesign*
*Completed: 2026-07-29*

## Self-Check: PASSED

- FOUND: `firestarter/doc/PROTOCOLS.md`, `firestarter/CLAUDE.md`, `firestarter/README.md`
- FOUND: `firestarter_app/doc/protocol-id.md`, `firestarter_app/doc/lockable-proms.md`, `firestarter_app/doc/community-validation.md`, `firestarter_app/doc/beta-testing-install.md`, `firestarter_app/README.md`
- FOUND: `.planning/REQUIREMENTS.md`
- FOUND: commit `48c36e5` in `firestarter` git log
- FOUND: commits `4149ee8`, `c3c9424` in `firestarter_app` git log
