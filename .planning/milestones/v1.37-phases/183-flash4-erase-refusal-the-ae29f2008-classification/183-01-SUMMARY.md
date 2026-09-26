---
phase: 183-flash4-erase-refusal-the-ae29f2008-classification
plan: 01
subsystem: firmware
tags: [platformio, avr-gcc, size-baseline, flash-cost-pricing, messages-catalog]

# Dependency graph
requires: []
provides:
  - "firestarter submodule forked onto gsd/v1.37-operator-safety-answered-reports-claim-hygiene, from origin/beta"
  - "cold-build flash/RAM baseline for uno, uno328pb, leonardo (Task 2 figures) that later 183 plans measure deltas against"
  - "measured SAFE-07 three-way pricing table (M1/M2/M3) that 183-03 Task 1's tracer slice depends on"
affects: [183-02, 183-03, 183-04, 183-05, 183-06]

actuals:
  tokens: 6000
  tasks: 3
  commits: 2
  plan_head_before: eac5ce6e43f2f687afb924a49d181301cd7ea8f0

tech-stack:
  added: []
  patterns:
    - "D-16 cold-build procedure: rm -rf .pio/build/<env> then exactly one pio run -e <env>, never pio run -t clean, never --rebuild"
    - "Throwaway firmware probe measured and reverted inside a single task, proven by both a porcelain-clean assertion and a negative git grep for the probe's own symbols"

key-files:
  created: []
  modified:
    - "firestarter/src/eprom_operations.cpp (Task 3 probe — applied, measured, reverted; net zero diff at plan end)"

key-decisions:
  - "M1's firmware cost was measured with a throwaway probe reusing an existing message id (MSG_ERR_UNKNOWN_CMD) rather than minting a new catalog id, because MSG_ERR_NOT_SUPPORTED's wire_format is id_frame (host renders the text) — a new id would cost zero firmware bytes on its own and would only add codegen ceremony, while an existing second id reproduces M1's real shape (a discriminating branch plus a second immediate at the same call site)"
  - "M3 (host pre-flight policy gate) is the chosen mechanism, decided by D-02 (M1 and M2 both fire after 'Connecting... OK', the exact sequence gh#62's reporter read as a malfunction) — not by the flash figures, which show no cliff on any target"
  - "The observed toolchain (PlatformIO Core 6.1.19, avr-gcc 7.3.0) matches size_baseline.json's meta pins exactly; no toolchain drift affects this plan's figures"

requirements-completed: [SAFE-07]

coverage:
  - id: D1
    description: "Firmware submodule forked onto the v1.37 milestone branch from origin/beta, with the meta-repo gitlink advanced to match"
    requirement: "SAFE-07"
    verification:
      - kind: other
        ref: "cd /workspaces/firestarter && git rev-parse --abbrev-ref HEAD == gsd/v1.37-operator-safety-answered-reports-claim-hygiene && git merge-base --is-ancestor origin/beta HEAD"
        status: pass
    human_judgment: false
  - id: D2
    description: "Cold-build baseline flash/RAM figures recorded for uno, uno328pb, leonardo (D-16 procedure)"
    requirement: "SAFE-07"
    verification:
      - kind: other
        ref: "three rm -rf .pio/build/<env> + pio run -e <env> cold builds, Flash:/RAM: lines captured to scratch logs"
        status: pass
    human_judgment: false
  - id: D3
    description: "M1's per-target firmware-flash delta measured via a reverted probe; M2/M3 recorded as structural zeros; three-row pricing table with grounds (figures + D-02) written to this SUMMARY"
    requirement: "SAFE-07"
    verification:
      - kind: other
        ref: "probe build logs (183-m1-{uno,uno328pb,leonardo}.log) diffed against Task 2 baseline logs; git grep negative checks for probe symbols after revert"
        status: pass
    human_judgment: false

duration: 10min
completed: 2026-09-11
status: complete
---

# Phase 183 Plan 01: SAFE-07 Firmware-Flash Pricing and the v1.37 Branch Fork Summary

**Measured M1's firmware cost at a consistent +12 B flash / +0 B RAM across all three AVR targets, recorded M2 and M3 as structural zeros, and forked the firmware submodule onto the v1.37 milestone branch — with D-02, not the flash figures, deciding M3 as the winner.**

## Performance

- **Duration:** ~10 min
- **Started:** 2026-09-11T08:14:00Z (approx)
- **Completed:** 2026-09-11T08:20:00Z (approx)
- **Tasks:** 3
- **Files modified:** 2 (firestarter gitlink in meta repo; firestarter/src/eprom_operations.cpp transiently, reverted to zero net diff)

## Accomplishments
- Firmware submodule forked `gsd/v1.37-operator-safety-answered-reports-claim-hygiene` from `origin/beta` (`3e26c1bb`); meta-repo gitlink advanced and committed in the same task.
- Cold-build baseline recorded for all three AVR envs, unmodified `origin/beta` tree.
- M1 measured with a reverted throwaway probe; M2 and M3 recorded as structural zeros with their reasons; the three-way pricing table below names M3 as the winner, citing the figures and D-02.

## Task Commits

Each task was committed atomically. Tasks 2 and 3 produced **no tracked-file change** by design — they are measurement-only, and Task 3's probe is reverted inside its own task, so neither has a corresponding source commit.

1. **Task 1: Create the v1.37 firmware milestone branch off origin/beta** - `339a6b4a` (chore) — meta-repo gitlink advance to the newly forked firmware branch. (No commit inside the firmware submodule itself: this task creates git branch state only, no file is edited in that repo.)
2. **Task 2: Cold-build baseline for uno, uno328pb and leonardo (D-16)** - no commit (measurement-only; no tracked file modified in either repo).
3. **Task 3: Measure M1's firmware cost with a reverted probe, and record the three-way pricing** - no commit (the probe was applied, measured, and reverted within this task; `git status --porcelain` in the submodule is clean at task end).

**Plan metadata:** commit for this SUMMARY.md follows immediately after this file is written (see `git_commit_metadata` step).

_Note: This plan is measurement-and-branch-setup only — see `<artifacts_this_phase_produces>` in the PLAN.md; it creates no firmware source symbol._

## Files Created/Modified
- `firestarter` (gitlink, meta repo) — advanced from `gsd/v1.36-dev-test-fidelity` tip to `3e26c1bb` on the new v1.37 branch
- `firestarter/src/eprom_operations.cpp` — Task 3's M1 probe applied, measured across all three AVR targets, then reverted via `git checkout --`; working tree is byte-identical to before the plan started

## SAFE-07 Pricing Table

### Task 2 — cold-build baseline (unmodified `origin/beta` tree, pre-M1)

| Env | flash_used | flash_total | ram_used | ram_total |
|---|---|---|---|---|
| uno | 22968 | 32768 | 1434 | 2048 |
| uno328pb | 23016 | 32768 | 1440 | 2048 |
| leonardo | 25114 | 32768 | 1875 | 2560 |

Each figure is that env's own `Flash:`/`RAM:` report line, from `rm -rf .pio/build/<env>` followed by exactly one `pio run -e <env>` (D-16). No figure above is read from `size_baseline.json` — that file's own live `avr_targets` (22952/23000/25098 flash) come from an earlier session's cold measurement and are cited only for cross-reference, never subtracted against.

**Observed toolchain (this session):** `pio --version` → `PlatformIO Core, version 6.1.19` (matches `size_baseline.json` meta's `platformio_core: "6.1.19"` pin exactly); `avr-gcc --version` (first line) → `avr-gcc (GCC) 7.3.0` (matches `meta.avr_gcc: "7.3.0"` pin exactly). No toolchain drift from the pinned meta.

### Task 3 — M1 probe measurement (same three envs, probe applied)

| Env | probe flash_used | Task-2 baseline flash_used | **M1 delta (flash)** | probe ram_used | Task-2 baseline ram_used | M1 delta (RAM) |
|---|---|---|---|---|---|---|
| uno | 22980 | 22968 | **+12 B** | 1434 | 1434 | +0 B |
| uno328pb | 23028 | 23016 | **+12 B** | 1440 | 1440 | +0 B |
| leonardo | 25126 | 25114 | **+12 B** | 1875 | 1875 | +0 B |

Every delta above is computed against that same env's own Task-2 baseline figure — never across envs, and never against `size_baseline.json`'s recorded values, per the plan's explicit instruction.

**The probe:** in `eprom_erase`'s existing `!is_flag_set(FLAG_CAN_ERASE)` guard, a `handle->protocol == PROTO_FLASH_5V_PAGE` compare-and-branch was added, emitting `MSG_ERR_UNKNOWN_CMD` (id `0xAB`, an existing catalog id, reused rather than minted) on the matching path while the non-matching path kept `LOG_ERROR_ID(MSG_ERR_NOT_SUPPORTED)`. `proto_constants.h` was added to the file's includes (it was not previously resolved there). No comment was written anywhere in the probe. The probe was reverted via `git checkout -- src/eprom_operations.cpp`, restoring the file to a byte-identical state to before Task 3 — proven by both a porcelain-clean assertion and a negative `git grep` for `PROTO_FLASH_5V_PAGE` and `MSG_ERR_UNKNOWN_CMD` in `src/eprom_operations.cpp`.

**Why an existing id and not a new one:** a new `messages.toml` id would require editing `/workspaces/tools/catalog/messages.toml`, running `tools/catalog/sync_to_subrepos.sh`, and regenerating `include/messages.h` — all to obtain a `#define` that itself costs zero firmware bytes, since the generated header is id-only and an unused `#define` materialises nothing. Reusing a second existing id (`MSG_ERR_UNKNOWN_CMD`) instead reproduces M1's real firmware shape exactly: a discriminating branch plus a second immediate value at the same call site, with no codegen round trip. The measured +12 B is that branch-plus-second-immediate — consistent across all three targets, as expected, since the branch logic is identical AVR code on each.

### The three-row pricing record (M1 / M2 / M3)

| Mechanism | Where it fires | Firmware-flash figure | Basis |
|---|---|---|---|
| **M1** — new firmware message id + `handle->protocol` compare-and-branch | Firmware, post-connect | **+12 B flash / +0 B RAM, measured, all three targets** | Reverted probe (above); reused an existing message id rather than minting a new one, per the reasoning above |
| **M2** — host renders better text against the existing `MSG_ERR_NOT_SUPPORTED` (`0xA5`) | Host, post-connect | **0 bytes, structural** | Edits only `firestarter_app`; `MSG_ERR_NOT_SUPPORTED`'s `wire_format = "id_frame"` means the format string already lives on the host, so no file under `firestarter/` is touched and no rebuild can move a firmware figure |
| **M3** — host pre-flight policy gate (`flash4_erase_gate.py`, D-01) | Host, **pre-connect** | **0 bytes, structural** | New host-only module (`flash4_erase_gate.py` + tests + `cli_handlers.erase` wiring); firmware is untouched, so no rebuild can move a firmware figure |

M2 and M3's zeros are recorded as rows, not omitted, per the plan's SAFE-07 edge-case instruction (a figure of zero is a measured-or-structural zero with its reason, never an absent row).

**Decision and grounds:** M3 is the chosen mechanism. The deciding constraint is **D-02**: M1 and M2 both fire *after* `Connecting... OK` — the exact sequence gh#62's reporter read as a malfunction — while M3 fires pre-connect, before that sequence starts. D-07 further weakens M1 because the chip name is host-side context, not firmware-side (D-11). **The flash figures did not decide this choice** — none of the three targets shows a flash cliff. Per RESEARCH.md § A.3, leonardo (the tightest target) sits 1808 B **below** its BASE-01 reference figure even before this plan's own measurement, with 724 B of named MERGE-05 exemptions already stacked on top and unused; "leonardo has 0 B headroom" is the MERGE-05 *band literal* (`band = 0` for leonardo in `check_size_baseline.py`), not the measured position. Stated plainly: M1's +12 B would not have been a problem on flash-budget grounds on any target measured here — it was eliminated by D-02, not by size.

## Decisions Made
- Reused an existing message id (`MSG_ERR_UNKNOWN_CMD`) for the M1 probe instead of minting a new catalog id — see "Why an existing id and not a new one" above. This is the measurement methodology, not a change to what M1 would cost in a real implementation (a new id, being `id_frame`-only, costs the same ≈0 B on top of the branch).
- Ran all three AVR envs' probe builds (uno, uno328pb, leonardo) rather than leonardo alone, even though the plan's `<verify>` block only re-runs leonardo — Task 3's `<action>` and its acceptance criteria require a per-env measured delta for all three targets, so uno and uno328pb probe builds were also run and are reported in the table above.

## Deviations from Plan

None - plan executed exactly as written. (Two minor mechanical substitutions, both explicitly permitted by the plan/context rather than deviations from its instructions: (1) `pio --version` was run from `/tmp` rather than the meta repo root, because `/workspaces/platformio.ini` has a pre-existing duplicate-`[platformio]`-section defect unrelated to this plan — out of scope per the executor's scope-boundary rule, logged here rather than fixed; (2) build/probe log files were written to this session's own scratchpad directory rather than the literal path embedded in the plan's `<verify>` blocks, because that literal path belonged to the planning session's scratchpad and does not exist in this execution session — the verify commands' pass/fail semantics (grep for `Flash:`/`RAM:` lines, `PROBE_PRESENT`, `PROBE_REVERTED`, the negative `git grep` checks) were all run and all passed independent of the log destination.)

## Issues Encountered

None. Both `.pio/build/*` and the meta repo's own `/workspaces/platformio.ini` duplicate-section defect are pre-existing and out of this plan's scope; neither blocked any task.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- The firmware submodule sits on `gsd/v1.37-operator-safety-answered-reports-claim-hygiene`, forked from `origin/beta`, with a clean tracked tree — every later firmware task in this phase (183-04, 183-05) has somewhere legal to commit.
- SAFE-07's measured pricing table and D-3's activation decision are both satisfied: M3 is named as the mechanism, with grounds recorded.
- 183-03 Task 1 (the phase's tracer slice) depends on this plan precisely so the mechanism is priced before it is chosen — that dependency is now satisfied.
- No blockers.

---
*Phase: 183-flash4-erase-refusal-the-ae29f2008-classification*
*Completed: 2026-09-11*

## Self-Check: PASSED

- FOUND: `.planning/phases/183-flash4-erase-refusal-the-ae29f2008-classification/183-01-SUMMARY.md`
- FOUND: commit `339a6b4a` (Task 1 — meta gitlink advance)
- FOUND: commit `c36165c2` (plan metadata — this SUMMARY)
- `cd /workspaces/firestarter && git rev-parse --abbrev-ref HEAD` → `gsd/v1.37-operator-safety-answered-reports-claim-hygiene`
- `cd /workspaces/firestarter && git status --porcelain --untracked-files=no` → empty (clean)
- Meta gitlink (`git ls-tree HEAD -- firestarter`) matches `git -C firestarter rev-parse HEAD` exactly (`3e26c1bb...`)
