---
phase: 204-the-command-surfaces-leave-the-firmware
plan: 05
subsystem: firmware-host-compat
tags: [bench, hardware, avr, platformio, serial-protocol, verify, blank-check, firestarter_fw, firestarter_app]

# Dependency graph
requires:
  - phase: 204-the-command-surfaces-leave-the-firmware
    provides: "plan 01's single-ordinal tracer recipe and BENCH-TRACER.md (rig identity, digest baseline); plan 03's ordinal-4 retirement; plan 04's closed record"
provides:
  - "204-BENCH-MATRIX.md: the full four-role D-07 bench record — both retired ordinals, both skew directions, three matching whole-device digests"
  - "REL-02, REL-03, FWCMD-06 proven on real hardware and marked Complete"
  - "Measured pre-sweep/post-sweep flash and RAM baseline for uno, uno328pb, leonardo, for Phase 205 to compare against"
affects: [205-the-pre-flights-leave-the-firmware, 207-the-release-and-the-record]

actuals:
  tokens: 6346
  tasks: 3
  commits: 4
  plan_head_before: ebf25550b67a07f71ad043917d87826b93cef3be

tech-stack:
  added: []
  patterns: ["detached git worktree for building a historical firmware commit without disturbing the working tree", "bench matrix record with a role table naming every artifact by commit sha or pinned version"]

key-files:
  created:
    - .planning/phases/204-the-command-surfaces-leave-the-firmware/204-BENCH-MATRIX.md
  modified:
    - .planning/REQUIREMENTS.md
    - .planning/STATE.md
    - .planning/ROADMAP.md

key-decisions:
  - "Task 2's un-forced 'verify' and 'blank' both hit the rig's known VPP-sensing false-positive precheck (13.1V read as high) before any chip content was exchanged; re-ran with -f for the same documented reason task 1's read needed it, and recorded the un-forced attempt rather than silently discarding it."
  - "Task 2's blank leg produced 'Read stopped in flight ... ERROR: Timeout' before the not-blank verdict; read eprom_operations.py source (202-04 D-06) before treating it as a defect and confirmed it is the designed abort-predicate fast-stop path, not a protocol failure — recorded as such rather than re-running until a cleaner-looking transcript appeared."
  - "FWCMD-06/REL-02/REL-03 marked Complete against the D-07 label-substitution evidence (post-204/pre-204 artifact labels), not against a literal 3.1.0b1 version string, which is Phase 207's bump — stated explicitly in both REQUIREMENTS.md and 204-BENCH-MATRIX.md."
  - "The seated part's identity (WINDOWS.md entry 3, chip-ID readback mismatch) is carried forward as unconfirmed, not re-investigated or forced past — every substantive claim in the matrix is chip-identity-independent by construction and the record says so."

requirements-completed: [FWCMD-06, REL-02, REL-03]

coverage:
  - id: D1
    description: "A post-204 host performs verify and blank correctly against pre-204 firmware on real hardware (REL-02) — verify matches (exit 0), blank reports not-blank via the designed abort-predicate path (exit 1), neither output carries an unknown-command line"
    requirement: "REL-02"
    verification:
      - kind: manual_procedural
        ref: "204-BENCH-MATRIX.md Task 2(a) — verify/blank transcripts, exit codes, durations against pre-204 firmware (e5842d8)"
        status: pass
    human_judgment: false
  - id: D2
    description: "A published 3.0.0b49 host receives an explicit coded refusal on both retired ordinals from post-204 firmware (REL-03, FWCMD-06) — never silence, never a hang, captured verbatim with exit code and duration"
    requirement: "REL-03"
    verification:
      - kind: manual_procedural
        ref: "204-BENCH-MATRIX.md Task 3(c)/(d) — 'Unknown command: 6' and 'Unknown command: 4' transcripts, exit 1, ~3.5s each"
        status: pass
    human_judgment: false
  - id: D3
    description: "The seated part's content is byte-identical across the whole matrix — three whole-device reads (pre-swap, post-swap, post-refusal) share one SHA-256 digest, ruling out a silent erase"
    requirement: "FWCMD-06"
    verification:
      - kind: manual_procedural
        ref: "204-BENCH-MATRIX.md Task 3(e) — three sha256sum comparisons, all matching a094e902a30b4fa3369ee493338351e11a8b6667f7539460b63f78dce896ae43"
        status: pass
    human_judgment: false
  - id: D4
    description: "The D-07 label substitution is stated explicitly, every role is named by commit sha or pinned version, and the host's inability to read back which firmware is on the board is stated"
    verification:
      - kind: manual_procedural
        ref: "204-BENCH-MATRIX.md 'D-07 label substitution' section and role table"
        status: pass
    human_judgment: false
  - id: D5
    description: "Per-target flash and RAM figures give Phase 205 a real Phase 204 baseline (pre-sweep vs post-sweep, uno/uno328pb/leonardo)"
    verification:
      - kind: manual_procedural
        ref: "204-BENCH-MATRIX.md Task 1(b)/Task 2(d) size tables; leonardo 24134->23810 B, under the 28672 B ceiling"
        status: pass
    human_judgment: false
  - id: D6
    description: "The seated part's identity remains genuinely unconfirmed — a human with physical access to the bench must eventually resolve WINDOWS.md entry 3"
    verification: []
    human_judgment: true
    rationale: "This is an open item this plan deliberately did not resolve (per the orchestrator's explicit instruction) — it needs the operator who placed the part, not further automated reads. A human must confirm the part's real identity at some point before the chip-ID-specific claim can be closed, though every substantive claim this plan makes is independent of that answer."

duration: 1h 10m
completed: 2026-09-22
status: complete
---

# Phase 204 Plan 5: The Four-Role Bench Matrix Summary

**Both host-firmware compatibility directions proven on real Leonardo hardware — a post-204 host works cleanly against pre-204 firmware, and a published `3.0.0b49` host is explicitly refused on both retired ordinals with the seated part byte-identical across three whole-device reads.**

## Performance

- **Duration:** 1h 10m
- **Started:** 2026-09-22T10:00:00Z (approx, rig re-derivation)
- **Completed:** 2026-09-22T11:15:00Z
- **Tasks:** 3
- **Files modified:** 4 (1 created, 3 shared-artifact updates)

## Accomplishments
- Built pre-204 firmware (`e5842d8`) from a detached `firestarter_fw` worktree, flashed it to the attached Leonardo, and baselined the seated part: 65536 bytes, non-blank, digest `a094e902...` — identical to plan 01's tracer baseline, confirming the same physical part, unmoved since that session.
- Proved REL-02 on the bench: the post-204 host's `verify` matched the baseline (exit 0) and `blank` reported not-blank (exit 1, via the designed abort-predicate fast-stop path) against pre-204 firmware, with no unknown-command line in either output — the compatibility claim was observed, not argued from code structure.
- Swapped to post-204 firmware (`24e3fdf`, 23810 B) and proved the part survived the flash byte-for-byte before running any refusal leg, isolating the flash's effect from the refusal legs' effect.
- Proved REL-03/FWCMD-06 on the bench: the published `3.0.0b49` host was refused with `Unknown command: 6` and `Unknown command: 4` against post-204 firmware, both promptly (~3.5s) and non-empty, never a hang. Three whole-device reads (pre-swap, post-swap, post-refusal) share one SHA-256 digest, proving no hardware side effect from either refusal.
- Recorded per-target flash/RAM figures for uno, uno328pb and leonardo, both pre-sweep and post-sweep, giving Phase 205 a real Phase 204 baseline instead of a Phase 201-era one (leonardo 24134 → 23810 B, well under its 28672 B bootloader ceiling).
- `204-BENCH-MATRIX.md` carries the full D-07 role table, the label-substitution statement, both refusal transcripts, all three digests, and the Leonardo-only coverage gap stated plainly — plus the carried-forward, deliberately-unresolved chip-identity caveat (WINDOWS.md entry 3).

## Task Commits

Each task was committed atomically:

1. **Task 1: Build and flash the pre-204 firmware, and baseline the part** - `53c4fbc2` (docs)
2. **Task 2: The new-host-against-old-firmware direction, then swap the firmware** - `d2f4ba4a` (docs)
3. **Task 3: The published host is refused on both ordinals, and the part is unchanged** - `d9944d6d` (docs)

**Plan metadata:** (this commit)

## Files Created/Modified
- `.planning/phases/204-the-command-surfaces-leave-the-firmware/204-BENCH-MATRIX.md` - the four-role bench record: D-07 role table and substitution statement, per-task step logs, three whole-device digests, two refusal transcripts, per-target size figures, the Leonardo-only coverage gap, and the carried-forward chip-identity caveat.
- `.planning/REQUIREMENTS.md` - FWCMD-06, REL-02, REL-03 marked Complete with evidence citations; traceability table updated.
- `.planning/STATE.md` - Current Position advanced to "5 of 5 complete"; session/metric/decision entries added (hand-corrected after each `gsd-tools query state.*` call reset `progress.completed_phases`/`percent` and appended a stale `milestone_name` suffix — see Deviations).
- `.planning/ROADMAP.md` - Phase 204's plan count and 204-05 checkbox updated to complete.

## Decisions Made
- Un-forced `verify`/`blank` hit the rig's documented VPP-sensing false-positive precheck; re-ran with `-f` for the same reason task 1's read needed it, and the un-forced attempt is recorded rather than discarded.
- The blank leg's "abort predicate fired" / "ERROR: Timeout" sequence was read against `eprom_operations.py` source (202-04 D-06) before being treated as evidence — confirmed as the designed early-stop path for a non-`--full` mismatch, not a protocol failure.
- FWCMD-06/REL-02/REL-03 marked Complete on the D-07 label-substitution evidence (post-204/pre-204 artifact labels standing in for the not-yet-bumped `3.1.0b1` string), stated explicitly in both REQUIREMENTS.md and the bench record.
- The seated part's identity (WINDOWS.md entry 3) was carried forward unconfirmed and NOT re-investigated, per explicit instruction — every substantive claim in this matrix is chip-identity-independent by construction.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] `gsd-tools query state.*` verbs repeatedly corrupted STATE.md frontmatter**
- **Found during:** State updates after task commits (state.advance-plan, state.record-metric, state.add-decision, state.record-session)
- **Issue:** Each of the four state-mutation verbs reset `progress.completed_phases` (2→0) and `progress.percent` (33→0) on every call, and re-appended a stale `(ACTIVATED 2026-09-20)` suffix to `milestone_name` — the exact corruption pattern already on record in this repo's known-issues memory.
- **Fix:** Copied STATE.md aside before each verb call, ran the verb, diffed the result, and hand-restored the four corrupted fields (`milestone_name`, `progress.completed_phases`, `progress.completed_plans`, `progress.percent`) while keeping the verb's legitimate additions (metrics table row, decision bullet, Current Position update, Last-session/Stopped-at lines).
- **Files modified:** `.planning/STATE.md`
- **Verification:** Final `git diff .planning/STATE.md` reviewed end-to-end; frontmatter reads `completed_phases: 2`, `completed_plans: 14`, `percent: 33`, `milestone_name: Verification Moves to the Host` (no parenthetical) — matching the values this plan's prompt named as correct.
- **Committed in:** (this metadata commit)

---

**Total deviations:** 1 auto-fixed (1 blocking — known tool-corruption pattern, worked around per the state_writer_warning already on record).
**Impact on plan:** No impact on the bench evidence itself. The correction is purely to `.planning/STATE.md` bookkeeping and was fully expected given this repo's documented history with these verbs.

## Issues Encountered
None beyond the documented deviation above. The rig behaved exactly as `204-BENCH-TRACER.md` and this plan's `<environment_facts_measured_at_plan_time>` predicted: same USB identity, same VPP-sensing noise pattern, same chip-ID mismatch, same digest for the same physical part.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- **Phase 204 is now plan-complete (5/5).** Phase-level verification and close (`/gsd-verify-work 204`) are a separate next step, not performed by this plan.
- **Open item carried forward, not a blocker:** `WINDOWS.md` entry 3 (seated part's chip identity unconfirmed) stays `open` — genuinely needs operator sign-off, not further automated investigation. It does not block Phase 204's close because every claim this phase makes is chip-identity-independent.
- **Coverage gap for Phase 205 and beyond:** both skew directions in this matrix, and plan 01's before it, ran on a Leonardo (1024-byte buffer) only. No Uno-class board is attached to this devcontainer; the 512-byte chunked-transfer path remains unproven. Stated explicitly in `204-BENCH-MATRIX.md`.
- **Phase 205 has a real baseline now:** pre-sweep and post-sweep flash/RAM figures for all three AVR targets are recorded in `204-BENCH-MATRIX.md`, replacing the Phase 201-era numbers Phase 205's own measurement would otherwise have had to compare against.
- `~/.firestarter/` is absent, exactly as it was before this plan ran. The throwaway old-host environment at `$HOME/.local/share/gsd-204-oldhost-venv` and the pre-204 firmware worktree were the only scratch artifacts; the worktree was removed and pruned, the venv is left in place (survives for reuse, as it did across waves).
- No branch in any of the three repositories touched `beta`. All three repos remain on `v1.41-verification-to-host` with gitlinks matching each sub-repo's `HEAD`.

## Self-Check: PASSED

- `.planning/phases/204-the-command-surfaces-leave-the-firmware/204-BENCH-MATRIX.md` exists on disk and is committed (`git log` shows it introduced in `53c4fbc2` and extended in `d2f4ba4a`/`d9944d6d`).
- `git log --oneline --all --grep="204-05"` returns 3 matching commits (`53c4fbc2`, `d2f4ba4a`, `d9944d6d`).
- All three whole-device read files (`pre.bin`, `mid.bin`, `post.bin`) were confirmed 65536 bytes and byte-identical during task execution; their SHA-256 (`a094e902a30b4fa3369ee493338351e11a8b6667f7539460b63f78dce896ae43`) matches plan 01's own tracer baseline.
- `~/.firestarter/` confirmed absent via `ls -la` immediately before writing this summary.
- `git -C firestarter_fw rev-parse --abbrev-ref HEAD` / `git -C firestarter_app rev-parse --abbrev-ref HEAD` / `git rev-parse --abbrev-ref HEAD` (meta) all report `v1.41-verification-to-host`.
- `git ls-tree HEAD firestarter_fw firestarter_app` matches each sub-repo's own `rev-parse HEAD`.
- `git worktree list` shows only the primary `firestarter_fw` checkout — the pre-204 build worktree was removed and pruned.

---
*Phase: 204-the-command-surfaces-leave-the-firmware*
*Completed: 2026-09-22*
