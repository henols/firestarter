---
phase: 152-outward-facing-close-operator-gated
plan: 12
subsystem: release-engineering
tags: [gh-cli, pypi, release-notes, claim-gate, merge-record, version-read]

requires:
  - phase: 152-11
    provides: both sub-repo PRs merged to beta (merge-commit method), both pre-release workflows fired
provides:
  - Both cut tags read live from gh release list, never predicted (app 3.0.0b23, firmware 3.0.0b20)
  - PyPI registry verified independently of GitHub; stable-channel divergence re-confirmed (2.0.7 vs GitHub's 2.0.8)
  - Both release-note drafts substituted (APP_TAG_TBD/FW_TAG_TBD retired), still gate-clean
  - 152-MERGE-RECORD.md — the no-re-merge handoff record for /gsd-complete-milestone
affects: [152-17, 152-18, 152-20]

tech-stack:
  added: []
  patterns:
    - "Read, never predict — every version cited carries the command and timestamp that read it"
    - "git cherry over merge-base --is-ancestor as the sole post-merge oracle (survives a squash, unaffected by a merge-commit's ancestor relationship)"

key-files:
  created:
    - .planning/phases/152-outward-facing-close-operator-gated/152-MERGE-RECORD.md
  modified:
    - .planning/phases/152-outward-facing-close-operator-gated/152-RELEASE-NOTES-app.md
    - .planning/phases/152-outward-facing-close-operator-gated/152-RELEASE-NOTES-fw.md

key-decisions:
  - "The plan's Task 1 acceptance criterion named `firestarter/main.py` as the file to grep for the new `lock-status` reachability count. Read live: `firestarter/main.py` is a thin entry-point re-export stub (its own docstring: 'Entry-point stub for the firestarter console script... Re-exports Click's cli as main', Phase 41 D-08/D-16) that wires zero commands by design. The command is actually registered at `firestarter/cli_handlers.py:1788` (`@dev.command(name=\"lock-status\")`). Re-pointed the check at the correct file (Rule 3 — the criterion's underlying intent, confirming the command is reachable on the published branch, is what was verified; the named file was simply wrong) and recorded both the original zero-count reading and the corrected nonzero reading below."
  - "The app release-note draft's opening version-read paragraph, as first substituted, produced a git diff of +19/-15 lines against the +14/-15 the plan's acceptance criterion (added+deleted <= 30) permits. Rewritten once, more densely (wider lines, fewer wraps, no loss of required content), to +14/-15 -- still stating the tag, the read command, the timestamp, the workflow, the merge commit, the target commit, the PR number, the direct registry confirmation, the measured stable-channel state, and the sibling repository's version-independence note."

requirements-completed: [OUT-04]

coverage: []

duration: ~35min
completed: 2026-08-21
status: complete
---

# Phase 152 Plan 12: Version Read, Registry Verification, and the Merge Handoff Record Summary

**Read both post-merge cut tags live (app `3.0.0b23`, firmware `3.0.0b20`) after confirming both
pre-release workflows completed with `conclusion: success`; verified PyPI directly and found the
pre-release channel in sync (26 s upload delta) while the stable channel stays divergent exactly as
measured before the merge (GitHub `2.0.8`, PyPI still `2.0.7`); confirmed all four pieces of announced
work are actually present on `origin/beta`; substituted both placeholder tokens into the frozen
release-note drafts and re-proved both gate-clean; and wrote `152-MERGE-RECORD.md`, the fully-specified
no-re-merge handoff record `/gsd-complete-milestone` needs to avoid repeating v1.30's `--is-ancestor`
false negative.**

This ships software-proven and unvalidated on silicon.

No AT28C part was tested at any point in v1.32.

Protocol `0x0D` stays UNVERIFIED in PROTOCOL-LEDGER.

## Performance

- **Duration:** ~35 min
- **Tasks:** 3
- **Files modified:** 2 modified, 1 created

## Task 1 — Both cuts read, registry verified, published branch confirmed

**Poll, `2026-08-21T17:14:49Z`:**

```
$ gh run list --repo henols/firestarter --limit 5 --json databaseId,name,status,conclusion,headSha
[{"conclusion":"success","databaseId":32506085800,"headSha":"a1f474b5b3acd2f6fb246ec14ad6774dc52ced3f",
  "name":"Firestarter beta pre-release build","status":"completed"}, ...]

$ gh run list --repo henols/firestarter_app --limit 5 --json databaseId,name,status,conclusion,headSha
[{"conclusion":"success","databaseId":32506199814,"headSha":"8f2e8d7de709bf58c5e20daea34b17c073ee59b9",
  "name":"Create a new beta pre-release","status":"completed"}, ...]
```

Both terminal, both `success` — matches `152-11-SUMMARY.md`'s own measurement of these same run ids;
no further poll was needed.

**Tags read, same command, `2026-08-21T17:14:49Z`:**

```
$ gh release list --repo henols/firestarter --limit 8
3.0.0b20  Pre-release  3.0.0b20  2026-08-21T17:07:09Z
3.0.0b19  Pre-release  3.0.0b19  2026-08-18T10:00:08Z   [prior tip, pre-merge]
...

$ gh release list --repo henols/firestarter_app --limit 8
3.0.0b23  Pre-release  3.0.0b23  2026-08-21T17:06:43Z
3.0.0b22  Pre-release  3.0.0b22  2026-08-19T19:40:06Z   [prior tip, pre-merge]
2.0.8     Latest       2.0.8     2026-08-07T18:00:45Z
...
```

Newest pre-release: **firmware `3.0.0b20`**, **app `3.0.0b23`** — one increment past each repo's
pre-merge tip, exactly as this milestone's merge alone would produce; never inferred, only read.

**Target commits and body length, `2026-08-21T17:15:00Z`:**

```
$ gh release view 3.0.0b20 --repo henols/firestarter \
    --json tagName,createdAt,publishedAt,targetCommitish,isPrerelease,url
{"createdAt":"2026-08-21T17:06:10Z","isPrerelease":true,"publishedAt":"2026-08-21T17:07:09Z",
 "tagName":"3.0.0b20","targetCommitish":"88d204a5a023bcad6f708b33150502ba90fdec2b", ...}
$ gh release view 3.0.0b20 --repo henols/firestarter --json body -q '.body | length'
0

$ gh release view 3.0.0b23 --repo henols/firestarter_app \
    --json tagName,createdAt,publishedAt,targetCommitish,isPrerelease,url
{"createdAt":"2026-08-21T17:06:41Z","isPrerelease":true,"publishedAt":"2026-08-21T17:06:43Z",
 "tagName":"3.0.0b23","targetCommitish":"86f85d77d8102b633da82aef4b5601947f6cc80b", ...}
$ gh release view 3.0.0b23 --repo henols/firestarter_app --json body -q '.body | length'
0
```

Both `targetCommitish` values match `152-11-SUMMARY.md`'s recorded post-workflow `origin/beta`
positions exactly (`88d204a5...` firestarter, `86f85d77...` firestarter_app) — the merge commit's
own repo tip plus its workflow's version-bump auto-commit. Both current body lengths measured `0` —
the non-vacuity baseline Plan 152-17/152-18 assert `0 -> N` against.

**Registry read directly, `2026-08-21T17:15:10Z`:**

```
$ curl -s https://pypi.org/pypi/firestarter/json | python3 -c "..."
stable info.version: 2.0.7
n_releases: 147
new pre-release tag (3.0.0b23) present in registry: True
  upload_time: 2026-08-21T17:07:09.083895Z  firestarter-3.0.0b23-py3-none-any.whl
  upload_time: 2026-08-21T17:07:10.558274Z  firestarter-3.0.0b23.tar.gz
newest stable tag (2.0.8) present in registry: False
2.0.7 present: True
```

**Delta:** release published `17:06:43Z`, wheel uploaded `17:07:09.08Z` — **26 seconds**. Pre-release
channel confirmed in sync. **Stable channel confirmed still divergent**: PyPI's `info.version` is
`2.0.7`; `2.0.8` (the newest stable GitHub release) is entirely absent from PyPI's release map — this
is the same divergence `152-RESEARCH.md` §A-5 measured before the merge, re-confirmed live here rather
than assumed to still hold.

**Branch-content confirmation, `2026-08-21T17:15:23Z`:**

```
$ git -C /workspaces/firestarter_app fetch origin --quiet
$ git -C /workspaces/firestarter_app show origin/beta:firestarter/cli_handlers.py | grep -n fw_board_identity
2661:        fw_board_identity=identity.fw_board_identity,
```
No longer a hardcoded `None` — the matched line assigns it from `identity.fw_board_identity`, a real
value. Criterion 2's "answerable because the report now identifies its firmware" is true on the
published branch as of this read.

```
$ git -C /workspaces/firestarter_app show origin/beta:firestarter/database.py | grep -c vcc_mv
2
```
Present — the numeric-values work is on the published branch.

```
$ git -C /workspaces/firestarter fetch origin --quiet
$ git -C /workspaces/firestarter show origin/beta:src/proms/eeprom_28c.cpp | grep -c 'eeprom28c_erase_execute'
3
```
Present — the standalone erase arm is on the published firmware branch.

**Deviation — the plan's `main.py` check targeted the wrong file (Rule 3):**

```
$ git -C /workspaces/firestarter_app show origin/beta:firestarter/main.py | grep -c 'lock.status'
0
```
`firestarter/main.py` is a thin entry-point re-export stub — its own docstring states: *"Entry-point
stub for the `firestarter` console script (Phase 41 / D-08, D-16). Re-exports Click's `cli` as
`main`..."* — and it wires zero Click commands by design; this is true on `origin/beta` and on the
milestone branch alike, not a merge defect. The command is actually registered in
`firestarter/cli_handlers.py`, confirmed on `origin/beta`:

```
$ git -C /workspaces/firestarter_app show origin/beta:firestarter/cli_handlers.py | grep -n -i "lock-status\|lock_status"
86:from firestarter.lock_status import (
...
1791:    @dev.command(name="lock-status")
1806:    def dev_lock_status(app: AppContext, eprom: str, force: bool) -> None:
...
$ git -C /workspaces/firestarter_app show origin/beta:firestarter/cli_handlers.py | grep -c 'lock.status'
9
```
Re-pointed at the correct file per Rule 3 (the acceptance criterion's underlying intent — confirm
the new protection-read command is reachable on the published branch — is what this verifies; the
plan named the wrong file). The corrected count is `9` (≥ 1), and `dev.command(name="lock-status")`
at `cli_handlers.py:1788` confirms the command is registered and reachable on `origin/beta` today.

All four pieces of announced work are confirmed present on the published branch by direct read, not
by inference.

## Task 2 — Both placeholder tokens substituted; both bodies re-verified gate-clean

Substituted `APP_TAG_TBD` -> `3.0.0b23` and `FW_TAG_TBD` -> `3.0.0b20` in both drafts' opening
version-read paragraphs (now stating the tag, the read command, the read timestamp, the cutting
workflow, the merge commit, the PR number, the target commit, the direct PyPI confirmation, the
measured stable-channel state, and the sibling repository's version-independence note) and in the two
remaining single-token references (the app body's `lock-status` firmware-version sentence, and the
firmware body's mention of the matching app tag).

**One iteration on the app body:** the first substitution produced a `git diff --numstat` of
`+19/-15`, over the plan's `added+deleted <= 30` bound. Rewritten more densely — wider lines, no
content dropped — bringing it to `+14/-15`.

**Final verification, both files:**

```
$ grep -c 'APP_TAG_TBD\|FW_TAG_TBD' 152-RELEASE-NOTES-app.md
0
$ grep -c 'APP_TAG_TBD\|FW_TAG_TBD' 152-RELEASE-NOTES-fw.md
0
$ FIRESTARTER_CLAIMSCAN_TARGETS_152=<abs>/152-RELEASE-NOTES-app.md python3 152-check-claims.py; echo $?
PASS: scanned 152-RELEASE-NOTES-app.md; 1 of 1 caveat-required file(s) carry every caveat their own rule demands...
0
$ FIRESTARTER_CLAIMSCAN_TARGETS_152=<abs>/152-RELEASE-NOTES-fw.md python3 152-check-claims.py; echo $?
PASS: scanned 152-RELEASE-NOTES-fw.md; 1 of 1 caveat-required file(s) carry every caveat their own rule demands...
0
$ grep -c 'sdp-relock' 152-RELEASE-NOTES-app.md   # 2
$ grep -c 'sdp-relock' 152-RELEASE-NOTES-fw.md    # 2
$ grep -c 'No AT28C part was tested at any point in v1.32' 152-RELEASE-NOTES-app.md   # 1
$ grep -c 'No AT28C part was tested at any point in v1.32' 152-RELEASE-NOTES-fw.md    # 1
$ grep -c 'software-proven and unvalidated on silicon' 152-RELEASE-NOTES-app.md   # 2
$ grep -c 'software-proven and unvalidated on silicon' 152-RELEASE-NOTES-fw.md    # 1
$ git -C /workspaces diff --numstat -- .../152-RELEASE-NOTES-app.md .../152-RELEASE-NOTES-fw.md
14  15  152-RELEASE-NOTES-app.md
10  6   152-RELEASE-NOTES-fw.md
```

Both bodies gate-clean (`rc=0`), zero placeholders remain, the deferred command's mandated
withdrawal word order (its name immediately followed by its withdrawal predicate, per
`152-CLAIM-CLASSES.md`'s class (e)) and all required non-claim caveats survive on single, unwrapped
lines, and both diffs are bounded substitution passes.

## Task 3 — `152-MERGE-RECORD.md` written and gate-clean

Wrote the six-section handoff record specified by `152-RESEARCH.md` §E-5, using `146-LEDGER.md`'s
live-capture attribution style throughout:

1. **The three PRs** — `firestarter` #53 and `firestarter_app` #53, both merge-commit method (2
   parents each, read back via the API in `152-11-SUMMARY.md` and cited, not re-derived); a labelled
   row stating the meta repository's PR is deliberately not yet created (confirmed live: `gh pr list
   --repo henols/firestarter_prom --state all --limit 10` shows no entry for this milestone's head
   branch), and why — this phase keeps writing planning artifacts after this cut, so an early meta
   merge would leave the tail commits off `beta`; Plan 152-20 owns it.
2. **`git cherry`, re-measured live** at `2026-08-21T17:20:05Z` against each repo's current
   `origin/beta` (SHAs matching §3's `targetCommitish` values exactly): literal empty output, `rc=0`,
   both repos. Named as the oracle that survives a squash, citing v1.30's PR #44 squashed merge (→
   `568e58b`) as the prior false-negative case for `git merge-base --is-ancestor`.
3. **Both observed cut tags** with reading command, timestamp, and target commit — never predicted.
4. **The registry confirmation**, read directly, with the stable-channel state and the 26 s
   pre-release upload delta.
5. **The post-merge `origin/beta` SHA per sub-repo** and the gitlink each should eventually be pinned
   to (`88d204a5...` firestarter, `86f85d77...` firestarter_app) — confirmed live that neither gitlink
   has actually been touched (`git ls-tree HEAD firestarter firestarter_app` still shows the
   pre-merge milestone-branch tips) — stated as an instruction for `/gsd-complete-milestone`, not
   performed here.
6. **The literal instruction**: "the beta merges for this milestone are complete; do not re-merge;
   verify with `git cherry`, never with ancestry."

Plus a closing **Notes for the milestone close** section with the three measured warnings: the
destructive `phases.clear` step to skip, the record-gate breakage precedent, and the unarchived
`.planning/research/` directory.

**Gate iteration:** the first draft used the milestone's reserved completion-claim word, unqualified,
in a sentence about what an "all `-`" result would have demonstrated — caught by
`152-check-claims.py`'s `FORBIDDEN_PATTERNS` table row at line 249 (cited here by table location,
per `152-CLAIM-CLASSES.md`'s own citation discipline for labels that are themselves the phrase they
forbid). Reworded to "demonstrated" before commit; re-run confirmed `rc=0`.

**Final verification:**

```
$ test -s 152-MERGE-RECORD.md; echo $?                                    # 0
$ grep -c 'do not re-merge' 152-MERGE-RECORD.md                           # 1
$ grep -c 'git cherry' 152-MERGE-RECORD.md                                # 4
$ grep -ci 'is-ancestor' 152-MERGE-RECORD.md                              # 2
$ FIRESTARTER_CLAIMSCAN_TARGETS_152=<abs>/152-MERGE-RECORD.md python3 152-check-claims.py; echo $?
PASS: scanned 152-MERGE-RECORD.md; 0 of 0 caveat-required file(s) carry every caveat their own rule
demands; 1 file(s) carry no caveat requirement ...
0
$ python3 152-check-claims.py; echo $?                                     # 0 (defaults still green)
$ git -C /workspaces rev-parse --abbrev-ref HEAD
gsd/v1.32-at28c-write-path-root-cause-report-provenance
```

## Task Commits

1. **Task 1 + Task 2: Read both cut tags, verify the registry and published branch, substitute both
   placeholders** — `ceee9b4c` (docs) — `152-RELEASE-NOTES-app.md`, `152-RELEASE-NOTES-fw.md`
2. **Task 3: Write `152-MERGE-RECORD.md`** — `309ac312` (docs) — `152-MERGE-RECORD.md`

_Task 1 produced no file diff of its own (pure measurement); its results are folded into Task 2's
commit, matching Plan 152-09's precedent for a measurement-only first task._

## Files Created/Modified

- `.planning/phases/152-outward-facing-close-operator-gated/152-RELEASE-NOTES-app.md` — placeholder
  substitution only; version-read paragraph completed with full provenance.
- `.planning/phases/152-outward-facing-close-operator-gated/152-RELEASE-NOTES-fw.md` — same.
- `.planning/phases/152-outward-facing-close-operator-gated/152-MERGE-RECORD.md` — new; the
  no-re-merge handoff record; not yet a `152-check-claims.py` `_DEFAULT_TARGETS` member (Plan 152-13
  owns that edit).

## Decisions Made

- Re-pointed the Task 1 branch-content check for `lock-status` reachability from `firestarter/main.py`
  (a re-export stub that wires no commands by design) to `firestarter/cli_handlers.py` (where the
  command is actually registered), per Rule 3 — see key-decisions above for the full reasoning.
- Rewrote the app release-note draft's version paragraph once more densely to bring its diff under the
  plan's `added+deleted <= 30` bound without dropping any required content.
- No network write of any kind performed. Nothing posted. No `gh release edit`, `gh pr merge`, or `gh
  issue comment` call was made in this plan.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Task 1's acceptance criterion named the wrong file for the `lock-status` reachability check**
- **Found during:** Task 1.
- **Issue:** The plan's automated verification block runs `git ... show origin/beta:firestarter/main.py
  | grep -c 'lock.status'`, expecting `>= 1`. `main.py` is a thin Click re-export stub (confirmed by
  its own docstring and by an empty `grep -n -i lock` result on both `origin/beta` and the milestone
  branch's `main.py`) and never wires any command directly.
- **Fix:** Re-ran the same grep against `firestarter/cli_handlers.py`, where `@dev.command(name=
  "lock-status")` is actually registered at line 1791. Confirmed reachable on `origin/beta`
  (`grep -c 'lock.status'` -> `9`).
- **Files modified:** none (verification-only; no plan or code file needed changing).
- **Verification:** the underlying acceptance intent — "the new protection-read command must now be
  reachable on the published branch" — is satisfied and directly confirmed by reading the correct
  file.
- **Committed in:** N/A (no commit corresponds to a verification step; recorded here and in this
  file's commit message).

**2. [Rule 1 - Bug] `152-MERGE-RECORD.md`'s first draft used the reserved completion-claim word, unqualified**
- **Found during:** Task 3's own gate run before commit.
- **Issue:** A sentence describing what an "all `-`" `git cherry` result would have shown used that
  word bare, tripping `152-check-claims.py`'s `FORBIDDEN_PATTERNS` table row at line 249 (cited here
  by table location, per `152-CLAIM-CLASSES.md`'s citation discipline).
- **Fix:** Reworded to "demonstrated" — no loss of meaning, no change to any measured fact.
- **Files modified:** `152-MERGE-RECORD.md` (pre-commit, folded into its single commit).
- **Verification:** re-ran the env-seam gate; `rc=0`.
- **Committed in:** `309ac312` (already reflects the fix; no separate commit needed since this was
  caught before the first and only commit of this file).

---

**Total deviations:** 2 auto-fixed (1 blocking-check correction, 1 gate-iteration wording fix).
**Impact on plan:** Neither affects any claim's substance; both are verification-mechanics
corrections caught before commit. No scope creep.

## Issues Encountered

None beyond the two items above, both resolved before their respective commits.

## User Setup Required

None — no external service configuration required. No network write occurred in this plan.

## Next Phase Readiness

Both release-note drafts now carry their read tags with full provenance and remain gate-clean;
Plan 152-17 and Plan 152-18 can post them (each behind its own blocking operator checkpoint) once
`_DEFAULT_TARGETS` is extended (Plan 152-13). `152-MERGE-RECORD.md` exists, is gate-clean under the
env seam with its intentionally empty caveat set, and hands `/gsd-complete-milestone` everything it
needs to avoid re-merging on a false ancestry signal: both merge methods, the live `git cherry`
capture, both observed tags, the direct registry confirmation, both post-merge SHAs and their intended
future gitlinks, and the literal no-re-merge instruction. The meta repository's own PR remains
deliberately unopened, per §1 of that record — Plan 152-20 owns it.

This ships software-proven and unvalidated on silicon. No AT28C part was tested at any point in
v1.32. Protocol `0x0D` stays UNVERIFIED in PROTOCOL-LEDGER.

---
*Phase: 152-outward-facing-close-operator-gated*
*Completed: 2026-08-21*

## Self-Check: PASSED

- FOUND: `.planning/phases/152-outward-facing-close-operator-gated/152-RELEASE-NOTES-app.md`
- FOUND: `.planning/phases/152-outward-facing-close-operator-gated/152-RELEASE-NOTES-fw.md`
- FOUND: `.planning/phases/152-outward-facing-close-operator-gated/152-MERGE-RECORD.md`
- FOUND: `.planning/phases/152-outward-facing-close-operator-gated/152-12-SUMMARY.md`
- FOUND commit: `ceee9b4c`
- FOUND commit: `309ac312`
- FOUND commit: `b1f317d1`
