---
phase: 151-protection-readability-lock-status
plan: 14
subsystem: bench-session
tags: [protection-readability, lock-status, bench, firmware-sideload, w29c020, w29c040, probe]

# Dependency graph
requires:
  - phase: 151-protection-readability-lock-status (plan 10)
    provides: "the funded +288 B MERGE05_LOCK_STATUS_READ_EXEMPTION_BYTES firmware image, cold-measured on all three AVR targets"
  - phase: 151-protection-readability-lock-status (plan 13)
    provides: "dev lock-status <chip> [--force], the CLI surface exercised on the bench"
provides:
  - ".planning/phases/151-protection-readability-lock-status/151-BENCH.md — the bench record: leg A confirmed, leg B recorded both forms, leg C recorded not-run with reason, leg D recorded as not existing, and an explicit non-claims list"
affects: [152]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "The strong discriminator for 'did the sideload actually take' is not the version string (host truncates the pre-release suffix) but dev lock-status's own comms-error text: 'Unknown command: 16' present before, absent after, with a real raw byte appearing only after."
    - "--force labels every outcome of the forced read path — success or comms failure alike — as unadjudicated_probe / exit 4; the class token is therefore not itself the sideload discriminator, the presence/absence of the comms-error text and the raw byte are."

key-files:
  created:
    - .planning/phases/151-protection-readability-lock-status/151-BENCH.md
  modified: []

key-decisions:
  - "Leg C was not run at all — neither the unforced refusal nor the forced probe — because the operator stated no W29C040 sample is on the bench. Running dev lock-status W29C040 against the physically-seated W29C020 would have misattributed a different part's reading to W29C040, so nothing was executed under that name; the artifact instead describes the DB entry's known refusal shape from 151-DESIGN.md §5 without claiming it was observed live."
  - "The raw byte from leg B's forced run (0xFE) happens to match Sequence B's decode table's 'boot block locked' value, and the record states that match explicitly while also stating in the same breath that stating the match is not a validation — sub-claims (ii) the address and (iii) the decode have no oracle, so a plausible-looking byte is a plausibility observation, not a verification."
  - "No requirement checkbox was touched. LOCK-02/LOCK-03/LOCK-04 were already Complete (flipped by 151-13 on software evidence); this plan owns no requirement flip and upgrades no claim."

requirements-completed: []

coverage:
  - id: D1
    description: "Product-ID mode entry and exit confirmed on real silicon via a chip-ID read returning 0xDA45"
    requirement: "LOCK-02 (advances only — already Complete)"
    verification:
      - kind: manual
        ref: "151-BENCH.md §Leg A — firestarter id W29C020 verbose output, chip-id 55877 (0xDA45), 'Chip ID check passed', exit 0"
        status: pass
    human_judgment: true
  - id: D2
    description: "Both 0x05 probe runs (unforced refusal, forced probe) recorded with raw results either way, no validation claim attached"
    requirement: "LOCK-03 (advances only — already Complete)"
    verification:
      - kind: manual
        ref: "151-BENCH.md §Leg B — unforced undocumented_alias naming W29C022 (exit 2); forced unadjudicated_probe, raw byte 0xFE (exit 4)"
        status: pass
    human_judgment: true
  - id: D3
    description: "Leg D (0x06 Autoselect) recorded in the milestone's own words: 'software-proven and unrun on silicon'; leg C recorded not-run with the operator's reason; v1.17 W29C040 RCA recorded as not closed"
    requirement: "LOCK-02, LOCK-03 (advances only — already Complete)"
    verification:
      - kind: manual
        ref: "151-BENCH.md §Leg C, §Leg D, §What this session did not establish"
        status: pass
    human_judgment: true

# Metrics
duration: ~40min
completed: 2026-08-20
status: complete
---

# Phase 151 Plan 14: The Bench Session — Leg A Confirmed, Leg B Probed, Leg C Skipped Summary

**Sideloaded the Phase 151 firmware to the operator's Leonardo, confirmed the flash took via a comms-error discriminator (not the truncated version string), ran the one bench leg with an oracle (leg A, `0xDA45`) and the one probe leg with a seated part (leg B, raw byte `0xFE`), and recorded leg C as not-run because no `W29C040` sample exists on the bench — with an explicit non-claims list closing out every claim this session is prohibited from making.**

## Performance

- **Duration:** ~40 min
- **Started:** 2026-08-20 (immediately following 151-13's completion)
- **Completed:** 2026-08-20
- **Tasks:** 4 (Task 1 and Task 3 checkpoints pre-resolved by the operator before this session began driving any port; Task 2 and Task 4 executed)
- **Files modified:** 1 (created)

## Session Identity (as recorded in `151-BENCH.md`)

- **Board:** Leonardo (ATmega32U4) on **`/dev/ttyACM0`**, confirmed this session.
- **`controller:` identity:** `leonardo on port /dev/ttyACM0` (from `firestarter fw`'s own output), read identically before and after the sideload.
- **Shield revision:** **Rev 2.0**, operator-stated, not independently probeable — `hw` reports "Rev 2.0-class" which is consistent with, but not proof of, that statement.
- **Part seated:** **`W29C020`**, operator-stated marking, suffix not distinguished (the three `W29C020*` aliases share one `chip_id 0x0000da45` and are indistinguishable on the wire regardless).
- **Part not on the bench:** `W29C040` — no sample available; leg C did not run.
- **Firmware flashed:** the Phase 151 build, `firestarter` submodule HEAD `373d6da7d674883f09b0a2e582851461f0e6c561`, sideloaded via `pio run -t upload -e leonardo --upload-port /dev/ttyACM0` (27500 B against the 28672 B Caterina cliff, 1172 B margin) — **not** `fw --install`.

## Leg A — Chip-ID Result

`firestarter -v -p /dev/ttyACM0 id W29C020` — EPROM data carries `'chip-id': 55877` (`0xDA45`); firmware reported *"Chip ID check passed for W29C020"*, exit code `0`. One attempt was sufficient; no timeout, no retry needed. This confirms sub-claim (i) — Product-ID mode entry and exit work on this part and socket — and nothing more.

## Leg B — Raw Byte and Class Token from Each Forced Run

- **Unforced:** `dev lock-status W29C020` → class token `undocumented_alias`, exit `2`, naming `W29C022 (undocumented)`.
- **Forced:** `dev lock-status W29C020 --force` → class token `unadjudicated_probe`, exit `4`, **raw status byte `0xFE`**.

`0xFE` matches Sequence B's decode table's "boot block locked" value; the record states that match while also stating that stating it is not a validation — sub-claims (ii) the address and (iii) the decode have no oracle.

## No Claim Upgraded, No Requirement Flipped

This plan's `requirements:` frontmatter is `[]`; LOCK-02 and LOCK-03 were already `Complete` (flipped by `151-13` on host and firmware-native software evidence). `REQUIREMENTS.md` was not touched by this plan, and no acceptance criterion or artifact statement asserts either sequence is correct, validated, or silicon-validated — confirmed by a `grep -c` of the three prohibited phrasings returning `0`.

## The Sideload Discriminator (Not the Version String)

`firestarter fw` reported the identical, truncated `3.0.0b19` string both before and after the sideload — expected, weak evidence per orchestrator constraint 1. The **strong** discriminator: before the sideload, `dev lock-status W29C020 --force` returned `ERROR: Unknown command: 16` embedded in its `unadjudicated_probe` rendering; after the sideload, the identical command returned a real raw byte (`0xFE`) with no comms error. That is the confirmation `CMD_LOCK_STATUS = 16` now exists on this board.

## Leg C and Leg D

- **Leg C (`W29C040`): not run.** Operator reason, recorded verbatim: *"no W29C040 sample available on the bench (operator, 2026-08-20)."* Neither the unforced refusal nor the forced probe was executed against the physically-seated `W29C020` under the `W29C040` name, because doing so would have misattributed a different part's reading. The v1.17 `W29C040` locked-boot-block RCA remains **not closed** — that RCA asked for a second `W29C040` sample, and this session had none to offer, not even partial corroboration.
- **Leg D (`0x06` Autoselect): no bench leg exists anywhere in this phase.** `lock-status` on a `0x06` part ships **software-proven and unrun on silicon**, stated in those exact words in `151-BENCH.md`.

## Non-Claims List (full text in `151-BENCH.md` §What this session did not establish)

- Neither sequence is claimed correct or validated — both are datasheet-derived; the strongest test over either is a pinned byte table plus citation, a **change detector, not a correctness proof**.
- Nothing about `W29C020C` or `W29C022` specifically is claimed — all three aliases share `chip_id 0x0000da45` and are indistinguishable on the wire.
- The v1.17 `W29C040` RCA is **not closed**.
- The milestone Evidence Ceiling is unchanged: `0x0D` stays `UNVERIFIED`, gh#21/#32/#11/#12 all stay open, no AT28C or `0x0D` silicon claim is made.

## Verification

- `151-BENCH.md` passes both of the plan's automated structural checks: all six required `##` sections present; all six required literal phrases present (`software-proven and unrun on silicon`, `change detector, not a correctness proof`, `0x0000da45`, `W29C042`, `W29C022`, `UNVERIFIED`); `silicon-validated` present in the D-03 cap restatement.
- `grep -c 'validated on silicon\|silicon-validated sequence\|the sequence is correct' 151-BENCH.md` → `0`.
- `firestarter --version` (py3.11 venv) → `Firestarter, version 3.0.0b21`, confirming the CLI environment used throughout.
- `git status --short` in `/workspaces/firestarter` shows a clean tracked tree — the sideload changed only the physical board, no tracked source file.

Python environment used: the pre-provisioned py3.11 venv at
`/tmp/claude-1000/-workspaces/f3ebf666-a01b-4de4-9860-8a006054ba0c/scratchpad/p151/venv311`
(per orchestrator constraint 8).

## Deviations from Plan

### Auto-fixed Issues

None — plan executed exactly as written, with Task 1 and Task 3's checkpoints pre-resolved by the operator before this session began (per this plan's own explicit prompt context), and Task 4's leg-C handling followed the plan's own "record as not-run with the stated reason" branch rather than the default "run it" branch.

**Total deviations:** 0.

## Issues Encountered

None. The one interesting bench observation — that a forced comms failure and a forced successful probe render under the same `unadjudicated_probe` class token and the same exit code `4` — is not a defect; it is the correct consequence of `--force` labeling every outcome of the bypassed path as an unadjudicated probe, and it is documented in `151-BENCH.md` as the reason the discriminator is the raw-byte/comms-error text, not the class token.

## User Setup Required

None — the operator's replies (board/shield/part identification, and the leg-C skip) were already captured verbatim in this plan's own prompt context before execution began.

## Next Phase Readiness

- Phase 151 is now fully executed — `151-14` was its last remaining plan (wave 6 of 6).
- `151-BENCH.md` is the phase's bench-evidence artifact; it makes no requirement claim and flips nothing in `REQUIREMENTS.md`.
- Phase 152 (Outward-Facing Close) can cite this record for its own claim gate: `dev lock-status` is shipped and beta-only (per `151-13`), leg A is a genuine positive control, legs B/C/D are all correctly bounded probes or non-existent legs, and the v1.17 RCA and the `0x0D` Evidence Ceiling both remain explicitly open — Phase 152's outward text must not describe either as closed.

## Self-Check: PASSED

- FOUND: .planning/phases/151-protection-readability-lock-status/151-BENCH.md
- FOUND commit: d5b99517
- Re-verified live at self-check time: `[ -f 151-BENCH.md ]` → FOUND; `git log --oneline --all | grep d5b99517` → FOUND.

---
*Phase: 151-protection-readability-lock-status*
*Completed: 2026-08-20*
