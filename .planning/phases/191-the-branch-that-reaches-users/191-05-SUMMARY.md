---
phase: 191-the-branch-that-reaches-users
plan: 05
subsystem: testing
tags: [firmware-flash, avrdude, leonardo, bench, update-check, phase-disposition]

# Dependency graph
requires:
  - phase: 191-04
    provides: "The published, live-verified PyPI release (firestarter 2.0.9), and the green fixture re-run proving subject_redirects: 0 against it"
provides:
  - "The fifth and final leg of 999.9's chain: a real update-check on the attached Leonardo, run from a clean install of the published 2.0.9 stable, flashing firmware 2.0.6 and leaving the board on it"
  - "The phase disposition record naming the three things Phase 191 does not achieve, plus the four stated boundary/deviation notes (Bench: none, D-10, the fixture's control slug, the unadvanced gitlink)"
affects: [phase-192, phase-193]

# Actuals (#2632)
actuals:
  tokens: 5150
  tasks: 2
  commits: 3
  plan_head_before: b13f5f6b

tech-stack:
  added: []
  patterns:
    - "The bench leg uses a SEPARATE scratch venv from the fixture's — the fixture tears its venv down on exit, and the bench leg needs a persistent one to drive an interactive CLI (stdin-fed Confirm.ask prompt)."
    - "A failed no-flag version handshake against a firmware string the host cannot parse is not retried into a different shape — it is recorded as the finding it is (two consecutive identical failures), and the plan's own named fallback (`fw --install`) is taken instead, with the reason stated in the transcript."
    - "The phase disposition record answers each ROADMAP success criterion in its own section, citing the specific evidence file and reading for every factual claim, rather than asserting completion in prose."

key-files:
  created:
    - .planning/phases/191-the-branch-that-reaches-users/evidence/191-stable-02-bench-leonardo.txt
    - .planning/phases/191-the-branch-that-reaches-users/evidence/191-stable-disposition.md
  modified: []

key-decisions:
  - "The no-flag path (`firestarter fw -b leonardo -p /dev/ttyACM0`, answered y) could not complete a version handshake against the board's firmware 3.0.0b22 at all -- it failed with 'Could not determine current firmware version', not with the predicted version-parse warning, on two consecutive attempts. Since the plan's named fallback covers exactly this contingency ('if the CLI reports it could not determine the current firmware version, re-run as `fw --install`'), the fallback was taken and the reason recorded in the transcript rather than retried further or worked around."
  - "Because no current-version string was ever read, the predicted `_compare_versions` ValueError/downgrade-offer sequence (which requires BOTH a current and a latest version to resolve) never had an opportunity to fire in this specific run. This is stated plainly in both the transcript and the disposition record as a finding about what this leg did and did not exercise, rather than silently treated as if the predicted sequence had been observed."
  - "The disposition record answers all four ROADMAP success criteria in dedicated sections, each claim citing its supporting evidence file, and separately states the four boundary/deviation notes the plan requires (Bench: none, the D-10 191/192 boundary, the fixture's deliberate control slug, the deliberately unadvanced firestarter_app gitlink) so a later reader or Phase 192's sweep does not misread any of them as an omission."
  - "No GSD state-writing verb was run against .planning/config.json during either task; `requirements.mark-complete` and the final `state`/`roadmap` verbs run only in the metadata close-out, and config.json's sub_repos (all four entries) were confirmed intact throughout."

requirements-completed: [STABLE-02]

coverage:
  - id: D1
    description: "A real update-check against the published 2.0.9 stable was run on the attached Leonardo: pre-flash reading, the named fallback flash to 2.0.6, and a closing reading showing 'Current firmware version: 2.0.6, for controller: leonardo' and an already-up-to-date message. No confirmation gate was added; the board is left on 2.0.6."
    requirement: STABLE-02
    verification:
      - kind: other
        ref: "191-stable-02-bench-leonardo.txt -- the plan's 9 automated <verify> legs (port present, controller-identity grep, 2.0.6 grep, already-up-to-date grep, installed_file grep, no .hex residue, config.json survives, phase-dir porcelain) -- all run directly, all pass"
        status: pass
    human_judgment: false
  - id: D2
    description: "The phase disposition record names all three unachieved items (stranded non-upgrading users, the missing origin/main regression guard D-02, the two-place broken release pipeline D-05 with both backlog items linked by filename), and separately states the Bench: none deviation, the D-10 191/192 boundary, the fixture's deliberate control slug, and the unadvanced firestarter_app gitlink."
    requirement: STABLE-02
    verification:
      - kind: other
        ref: "191-stable-disposition.md -- the plan's 8 automated <verify> legs ('does not achieve', D-02, D-05, backlog filename, 'bench: none', v1.38-url-02-main, subject_redirects, phase-dir porcelain, firestarter_app gitlink diff) -- all run directly, all pass"
        status: pass
    human_judgment: false

duration: 12min
completed: 2026-09-13
status: complete
---

# Phase 191 Plan 05: Bench Leg on the Leonardo and the Phase Disposition Record Summary

**Flashed firmware 2.0.6 to the Leonardo on `/dev/ttyACM0` from a clean install of the published `firestarter` 2.0.9 stable via the plan's named fallback path (the no-flag version handshake could not complete against the board's `3.0.0b22`), then wrote the phase disposition record naming all three things Phase 191 does not achieve.**

## Performance

- **Duration:** ~12 min
- **Started:** 2026-09-13T22:01:00Z (approx)
- **Completed:** 2026-09-13T22:08:29Z
- **Tasks:** 2
- **Files modified:** 2 (both new)

## Accomplishments
- Installed the published `firestarter` 2.0.9 into a fresh scratch venv (`mktemp -d`, outside `/workspaces`), separate from the fixture's own venv, and confirmed provenance first: `firestarter.__file__` resolved inside the scratch venv, `__version__` read `2.0.9` (matching `191-stable-01-pypi.txt`), and `FIRESTARTER_RELEASE_URL` read the repointed `firestarter_fw` endpoint.
- Ran the no-flag path (`firestarter fw -b leonardo -p /dev/ttyACM0`, answered `y`) twice, both times failing to complete a version handshake against the board's actual firmware (`3.0.0b22`) at all -- `Could not determine current firmware version` -- rather than reaching the predicted version-parse warning. This is the plan's own named contingency, and it is recorded as a finding, not smoothed over by retrying into a different shape.
- Took the plan's named fallback (`firestarter fw --install -b leonardo -p /dev/ttyACM0`), which proceeded through the no-current-version arm without a prompt, downloaded `firestarter_leonardo.hex` (`2.0.6`), and flashed it successfully in ~5.3s via `avrdude`.
- Confirmed the closing reading: `Current firmware version: 2.0.6, for controller: leonardo on port /dev/ttyACM0` / `Firmware is already up to date` -- the per-port controller-identity confirmation this project requires, taken with no flags and no stdin input. The board is left on `2.0.6`.
- Confirmed no `.hex` residue survived under `~/.firestarter` (removed automatically by `manage_firmware_update` after the successful install) and that `config.json` and `reports/` -- the operator's own data -- were untouched; removed the scratch venv by explicit path.
- Wrote `191-stable-disposition.md`: one section per ROADMAP success criterion, each claim citing its supporting evidence file and reading, naming all three unachieved items (stranded non-upgrading users; the missing `origin/main` regression guard, D-02; the two-place broken release pipeline, D-05, linking both filed backlog items by filename) and separately stating the `Bench: none` deviation, the D-10 191/192 boundary, the fixture's deliberate control slug, and the deliberately unadvanced `firestarter_app` gitlink.
- Recorded, in both the transcript and the disposition record, that this leg's handshake failure meant the predicted `_compare_versions` ValueError/downgrade-offer sequence never had material to fire on -- it requires both a current and a latest version to resolve, and no current version was ever read in this run.

## Task Commits

Each task was committed atomically:

1. **Task 1: Flash the Leonardo from a clean install of the published stable and capture the transcript** - `a3154c45` (test)
2. **Task 2: Write the phase disposition record, naming all three things this phase does not achieve** - `c794da9d` (docs)

**Plan metadata:** commit pending (this SUMMARY + STATE/ROADMAP/REQUIREMENTS)

## Files Created/Modified
- `.planning/phases/191-the-branch-that-reaches-users/evidence/191-stable-02-bench-leonardo.txt` - the live bench transcript: provenance, the failed no-flag handshake (twice), the named fallback flash to 2.0.6, and the closing reading
- `.planning/phases/191-the-branch-that-reaches-users/evidence/191-stable-disposition.md` - the phase disposition record answering all four ROADMAP success criteria and stating the four boundary/deviation notes

## Decisions Made
See frontmatter `key-decisions` for the full list: the named-fallback path taken (and why, recorded rather than retried around); the honest statement that the predicted parse-warning sequence did not fire because no current version was ever read; the disposition record's per-criterion, evidence-cited structure; and the confirmed absence of any `config.json` sub_repos disturbance.

## Deviations from Plan

None - plan executed exactly as written. The no-flag path's failure to complete a version handshake, and the resulting use of the plan's own named fallback, is the plan's explicitly anticipated contingency ("if the CLI reports it could not determine the current firmware version, re-run as `firestarter fw --install ...`"), not an unplanned deviation -- it is documented above and in both evidence files as the honesty requirement demands, rather than treated as a defect or worked around further.

## Issues Encountered
The no-flag invocation could not read the board's current firmware version over two consecutive attempts (`Timeout waiting for a response` / `No compatible programmer found on any port` on the version-read handshake, despite the subsequent `--install` invocation's own avrdude flash succeeding moments later on the same port). This is recorded honestly in the transcript as a real, measured limitation of the no-flag path against firmware 951 commits older than the stable host, per the plan's own prediction and the honesty requirement -- not retried into a cleaner-looking but less truthful transcript.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Phase 191 is complete: URL-02 and STABLE-01 were already Complete from prior plans; STABLE-02 is now satisfied by this plan's bench leg plus 191-01/191-04's fixture pair.
- 999.9's full chain (install -> query -> locate release -> download asset -> update-check) has been demonstrated end to end against the published `2.0.9` stable, split across the board-free fixture and this real-hardware leg.
- The phase disposition record is the single reference for what shipped and what remains open: three named unachieved items, two filed backlog items (`beta-release.yml`'s `pypi` job named as the proven fix for both), and the four boundary/deviation notes Phase 192 and any later reader need in order not to misread this phase's scope.
- No blockers for Phase 192 (`Live References Only`), which re-verifies `origin/main` as a git ref per D-10 and does not edit it.

---
*Phase: 191-the-branch-that-reaches-users*
*Completed: 2026-09-13*

## Self-Check: PASSED
- FOUND: .planning/phases/191-the-branch-that-reaches-users/evidence/191-stable-02-bench-leonardo.txt
- FOUND: .planning/phases/191-the-branch-that-reaches-users/evidence/191-stable-disposition.md
- FOUND: commit a3154c45 (Task 1: bench transcript)
- FOUND: commit c794da9d (Task 2: disposition record)
