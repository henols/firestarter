---
phase: 191-the-branch-that-reaches-users
plan: 04
subsystem: testing
tags: [pypi, github-releases-api, workflow-dispatch, redirect-contract, publish-verification]

# Dependency graph
requires:
  - phase: 191-03
    provides: "The merged commit on henols/firestarter_app main (1d526ea3), the confirmed observation that release.yml failed under branch protection exactly as D-04 predicted, and the three exact operator commands for the hand-cut with the real merge sha substituted"
provides:
  - "A published, live-verified PyPI release (firestarter 2.0.9) reached via operator-performed tag + GitHub release + publish.yml workflow_dispatch, none of it executed by the agent"
  - "STABLE-01 satisfied by an artefact on the public index, cross-checked against three independent sha readings (tag peel, release target_commitish, and 191-03's merge commit) that all agree"
  - "STABLE-02's install-side chain demonstrated green against the published artefact by the same unmodified script that exited 1 against the pre-cut stable in 191-01 -- the red/green transcript pair this phase exists to produce"
  - "A disclosed PyPI-index propagation-lag finding: the JSON API reported 2.0.9 immediately, but pip's own resolution briefly served the previous stable (2.0.7) before catching up on retry -- recorded rather than hidden behind the eventual clean run"
affects: [191-05, phase-193]

# Actuals (#2632)
actuals:
  tokens: 3318
  tasks: 1
  commits: 3
  plan_head_before: c2b789d0

tech-stack:
  added: []
  patterns:
    - "A published artefact is verified against the live PyPI JSON API and a clean-room pip install, never against the operator's report and never against the publish workflow's own conclusion (extending 189-04/190-16/191-01's pattern to the publish step itself)."
    - "A tag's identity is confirmed by peeling it (git refs API -> object.sha -> commits API) rather than trusting the annotated tag's own message, so an annotated-tag indirection cannot silently point the wrong commit."
    - "A workflow_dispatch run id handed over by the operator is polled to a terminal status and recorded as context, explicitly labelled as not the verification -- the run's own green tick has been the historical blind spot (GitHub 2.0.8 existed on GitHub, never on PyPI, with nothing reporting an error)."

key-files:
  created:
    - .planning/phases/191-the-branch-that-reaches-users/evidence/191-stable-01-pypi.txt
    - .planning/phases/191-the-branch-that-reaches-users/evidence/191-stable-02-fixture-published.txt
  modified: []

key-decisions:
  - "Verified the operator's report (tag 2.0.9, release 2.0.9, publish.yml run 34785081751) against three independent live reads rather than trusting it: the tag's refs API object peeled through the commits API to 1d526ea30f0a00c23ad8198b4679ee9459f31a88, the release's target_commitish read the same sha directly, and both matched 191-03's recorded merge commit exactly. No discrepancy found."
  - "Polled the publish.yml run to a terminal status per the resume instructions; it was already completed/success on the first read (no polling loop needed) -- all steps including 'Publish package' green. Recorded explicitly as context, not as the verification, per the plan's repudiation mitigation (T-191-04-02)."
  - "Read PyPI's JSON API live: info.version 2.0.9 on the first read, ~2 minutes after the publish run completed, with both release files (wheel + sdist) present and the project Homepage unchanged (correctly -- URL-02 repointed the firmware endpoint, not the PyPI project's own metadata)."
  - "The fixture's byte-identity was proven (git diff --stat: 0 lines) BEFORE it was invoked, and the phase directory's porcelain state was reasoned about explicitly: the first PyPI evidence file had to be committed before the fixture's own Check 4 (porcelain guard) would pass, because that guard allow-lists only the fixture script and its baseline transcript. This ordering constraint is now on record for any future re-run in this phase directory."
  - "A genuine PyPI propagation-lag finding was disclosed rather than smoothed over: the JSON API already reported 2.0.9 when the FIRST fixture invocation still resolved pip to 2.0.7 -- evidence that pip's install path and the JSON metadata endpoint are not backed by the same cache state at every instant. A second invocation, run after independently confirming the plain simple-index URL already listed 2.0.9, resolved 2.0.9 correctly. All three fixture invocations (the propagation-lag fail, the resolved-but-porcelain-dirty fail, and the final clean pass) are recorded in the evidence file's addendum, not just the last one."
  - "No tag, release, or workflow dispatch was created or run by the agent at any point in this plan -- confirmed by review of every command executed in this continuation, all of which were gh api / gh run view / curl reads."

requirements-completed: [STABLE-01, STABLE-02]

coverage:
  - id: D1
    description: "Operator's tag 2.0.9, GitHub release 2.0.9, and publish.yml run 34785081751 verified live: the tag peels (via the refs and commits APIs) to 1d526ea30f0a00c23ad8198b4679ee9459f31a88, the release's target_commitish is the same sha, both match 191-03's recorded merge commit, and the publish run is completed/success with all steps green (recorded as context, not verification)."
    requirement: STABLE-01
    verification:
      - kind: other
        ref: "gh api repos/henols/firestarter_app/git/refs/tags/2.0.9, gh api repos/henols/firestarter_app/commits/2.0.9, gh api repos/henols/firestarter_app/releases/tags/2.0.9, gh run view 34785081751 -R henols/firestarter_app -- all read directly, recorded in 191-stable-01-pypi.txt"
        status: pass
    human_judgment: false
  - id: D2
    description: "Live PyPI JSON index reports info.version 2.0.9 (matching the confirmed cut version) with both the wheel and sdist present under that release and the project Homepage unchanged; a genuine pip-level propagation-lag was observed and disclosed rather than hidden, resolving on retry."
    requirement: STABLE-01
    verification:
      - kind: other
        ref: "curl https://pypi.org/pypi/firestarter/json (info.version, project_urls.Homepage, releases[version]) -- run directly, recorded in 191-stable-01-pypi.txt with the propagation-lag addendum"
        status: pass
    human_judgment: false
  - id: D3
    description: "191-stable-install-fixture.sh proven byte-identical to its committed state (git diff --stat: 0 lines), then re-run unmodified with EXPECT_VERSION=2.0.9: exits 0, prints STABLE INSTALL CONTRACT OK, installed_version/pypi_latest_stable both 2.0.9, control_redirects: 1, subject_redirects: 0, installed_file resolves inside the scratch venv under /tmp -- the green half of the red/green pair against 191-01's baseline."
    requirement: STABLE-02
    verification:
      - kind: other
        ref: "191-stable-02-fixture-published.txt -- the plan's 9 automated <verify> legs (fixture-diff, live-pypi-version, info.version-mention, verdict-token, subject_redirects:0, control_redirects:1, installed_file-under-tmp, no-hex-residue, porcelain) -- all run directly, all pass"
        status: pass
    human_judgment: false

duration: 22min
completed: 2026-09-13
status: complete
---

# Phase 191 Plan 04: Verifying the Published Stable Live and Re-Running the Fixture Green Summary

**Read the operator's tag/release/publish.yml dispatch live against three independent APIs (all agreeing on commit 1d526ea3), then re-ran 191-01's unmodified install fixture against the published `firestarter` 2.0.9 -- exit 0, `subject_redirects: 0` where the identical script exited 1 against 2.0.7 an hour earlier.**

## Performance

- **Duration:** ~22 min (this continuation; Task 1's decision and Task 2's operator action were completed before this continuation began)
- **Started:** 2026-09-13T21:53:00Z (approx, resume)
- **Completed:** 2026-09-13T22:15:00Z (approx)
- **Tasks:** 1 (Task 3 -- Tasks 1 and 2 were the operator gates, already satisfied with no agent artifact/commit before this continuation began)
- **Files modified:** 2 new evidence files

## Accomplishments
- Verified the operator's report against three independent live reads instead of trusting it: the tag `2.0.9`'s ref object (an annotated tag) peels through the commits API to `1d526ea30f0a00c23ad8198b4679ee9459f31a88`; the GitHub release `2.0.9`'s `target_commitish` reads the identical sha directly; and both match 191-03's recorded merge commit exactly. No discrepancy.
- Polled `publish.yml` run `34785081751` to a terminal status (already `completed`/`success` on the first read, no polling loop needed) -- every step including "Publish package" green -- and recorded it explicitly as context, never as the verification, per the plan's own repudiation mitigation (T-191-04-02).
- Read `pypi.org/pypi/firestarter/json` live: `info.version` `2.0.9` on the first read (~2 minutes after the publish run completed), with both `firestarter-2.0.9-py3-none-any.whl` and `firestarter-2.0.9.tar.gz` present and `project_urls.Homepage` unchanged (correctly -- URL-02 repointed the firmware release constant, not the PyPI project's own metadata).
- Proved `191-stable-install-fixture.sh` byte-identical to its committed state (`git diff --stat`: 0 lines) before invoking it, per the plan's non-negotiable requirement that the red/green pair's evidential value depends entirely on the script being unmodified.
- Discovered and disclosed a genuine PyPI propagation-lag finding rather than smoothing it over: the JSON API already reported `2.0.9` while the FIRST fixture invocation's `pip install` still resolved `2.0.7` -- `pip`'s install path and the JSON metadata endpoint were not backed by the same cache state at that instant. A second invocation, run after independently confirming the plain simple-index URL already listed `2.0.9`, resolved `2.0.9` correctly but then failed the fixture's own porcelain guard (Check 4) because the just-written PyPI evidence file was still untracked -- an ordering artifact, not a propagation one. Committing that evidence file first let the third invocation pass cleanly end-to-end. All three invocations are recorded in the evidence addendum, not just the final clean one.
- Final green transcript: exit 0, `STABLE INSTALL CONTRACT OK`, `installed_version: 2.0.9`, `pypi_latest_stable: 2.0.9`, `control_redirects: 1`, `subject_redirects: 0`, `installed_file` resolving under the scratch venv's `/tmp` path -- the opposite reading from 191-01's committed baseline (`2.0.7`, `subject_redirects: 1`, exit 1) against the identical, unmodified script.
- Confirmed no `.hex` residue survived in `~/.firestarter` and both working trees (meta and `firestarter_app`) were clean after the run; `.planning/config.json`'s `sub_repos` (all four entries) were left untouched throughout, since no state-writing GSD verb was run during this plan's execution.

## Task Commits

Each task was committed atomically:

1. **Task 1: Confirm which version is cut** -- no commit (pure decision; completed by the operator before this continuation began).
2. **Task 2: Operator cuts the release and dispatches publish.yml** -- no commit (pure handoff; completed by the operator before this continuation began).
3. **Task 3: Verify PyPI live, then re-run the unmodified fixture green** -- two commits, split because the fixture's own porcelain guard required the first evidence file committed before the final green run could pass Check 4:
   - `004c3567` (test): live tag/release/publish.yml verification against three independent APIs, recorded in `191-stable-01-pypi.txt`
   - `8d330e30` (test): the green fixture re-run transcript and the propagation-lag addendum, recorded in `191-stable-02-fixture-published.txt` (and an update to `191-stable-01-pypi.txt`)

**Plan metadata:** commit pending (this SUMMARY + STATE/ROADMAP/REQUIREMENTS)

## Files Created/Modified
- `.planning/phases/191-the-branch-that-reaches-users/evidence/191-stable-01-pypi.txt` -- live tag/release/publish-run verification, the live PyPI JSON reading, and the propagation-lag addendum documenting all three fixture invocations
- `.planning/phases/191-the-branch-that-reaches-users/evidence/191-stable-02-fixture-published.txt` -- the green half of the STABLE-02 fixture pair, run unmodified against the published 2.0.9

## Decisions Made
See frontmatter `key-decisions` for the full list: three-way sha cross-check on the tag/release/merge-commit; the publish run polled to terminal and recorded as context only; the live PyPI JSON reading with no lag on that specific API; the fixture-porcelain-guard commit-ordering constraint now on record; the disclosed pip-level propagation-lag finding and its resolution on retry; and the confirmation that no outward-facing act was performed by the agent.

## Deviations from Plan

**1. [Rule 3 - Blocking] The fixture's porcelain guard (Check 4) required the PyPI evidence file committed before a clean run was possible**
- **Found during:** Task 3, second fixture invocation
- **Issue:** The plan's action step instructs writing both evidence files and then committing them together at the end. But the fixture script itself (unmodified, and correctly so) runs a porcelain guard mid-execution that only allow-lists the fixture and its baseline transcript -- any other untracked file in the phase directory, including the PyPI evidence file this same task had just written, fails Check 4.
- **Fix:** Committed `191-stable-01-pypi.txt` on its own first (commit `004c3567`), then ran the fixture a third time, which passed Check 4 cleanly since the newly-committed file no longer showed as untracked. The final green transcript and remaining evidence updates were committed together afterward (commit `8d330e30`).
- **Files modified:** `.planning/phases/191-the-branch-that-reaches-users/evidence/191-stable-01-pypi.txt`, `.../191-stable-02-fixture-published.txt`
- **Verification:** Final fixture invocation exited 0 with `CHECK4 OK` and `STABLE INSTALL CONTRACT OK`; `git status --porcelain` over the phase directory and `.planning/config.json` returned empty afterward.
- **Committed in:** `004c3567`, `8d330e30`

---

**Total deviations:** 1 auto-fixed (1 blocking -- commit-ordering constraint discovered by the fixture's own unmodified guard, not a script change).
**Impact on plan:** No scope creep; the fixture itself was never touched. The two-commit split is a truthful record of the actual sequence of events rather than a synthesized single commit that would hide the ordering constraint this fixture's design surfaced.

## Issues Encountered
The pip-level propagation lag described above (first invocation resolved `2.0.7` although the JSON API already reported `2.0.9`) is disclosed as a finding in the evidence file's addendum, per the plan's explicit instruction to record lag rather than hide it. It resolved on the very next invocation and did not require an extended wait.

## User Setup Required
None -- no external service configuration required in this continuation. Both operator gates (Task 1's version decision, Task 2's tag/release/dispatch) were satisfied before this continuation began, per the resume state.

## Next Phase Readiness
- STABLE-01 and STABLE-02 are both satisfied: `firestarter` 2.0.9 is live on PyPI, cross-verified against three independent commit-sha readings, and the unmodified STABLE-02 fixture now exits 0 against it -- the opposite reading from 191-01's committed red baseline.
- The orphaned GitHub release `2.0.8` (cut 2026-08-07, never published to PyPI) remains exactly as it was: not cleaned up, not back-published, superseded by `2.0.9` for `pip install` purposes -- as the plan explicitly required.
- No blockers for 191-05 (the Leonardo bench leg, D-09) -- a separate plan, untouched here.
- The two `release.yml`/`publish.yml` pipeline defects (D-05) remain filed as backlog items from 191-02/191-03, not fixed by this phase, as decided.

---
*Phase: 191-the-branch-that-reaches-users*
*Completed: 2026-09-13*

## Self-Check: PASSED
- FOUND: .planning/phases/191-the-branch-that-reaches-users/evidence/191-stable-01-pypi.txt
- FOUND: .planning/phases/191-the-branch-that-reaches-users/evidence/191-stable-02-fixture-published.txt
- FOUND: commit 004c3567 (Task 3 part 1: live tag/release/publish verification)
- FOUND: commit 8d330e30 (Task 3 part 2: green fixture re-run)
