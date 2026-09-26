# 152-MERGE-RECORD.md — the beta-merge handoff record for `/gsd-complete-milestone`

**No prior phase produced a document of this shape.** There is no donor to adapt; the content is
fully specified by `152-RESEARCH.md` §E-5's six numbered items plus its one-line instruction. Every
value below carries the command and the timestamp it was read with, and a statement that it was
measured here — live, in this plan — rather than reused from any prior document's citation,
following `146-LEDGER.md`'s live-capture attribution style.

This ships software-proven and unvalidated on silicon.

No AT28C part was tested at any point in v1.32.

Protocol `0x0D` stays UNVERIFIED in PROTOCOL-LEDGER.

## 1. The three pull requests

| Repo | PR | URL | Merge method (read back from the API) | State |
|---|---|---|---|---|
| `firestarter` | #53 | https://github.com/henols/firestarter/pull/53 | merge commit (`mergeCommit.oid` present, 2 parents) | MERGED |
| `firestarter_app` | #53 | https://github.com/henols/firestarter_app/pull/53 | merge commit (`mergeCommit.oid` present, 2 parents) | MERGED |
| meta (this repo, `firestarter_prom`) | #38 | https://github.com/henols/firestarter_prom/pull/38 | merge commit (`9e154847d6`, 2 parents `acae91615d` + `be2216a048`, read back via `gh api`) | MERGED |

Measured live, this plan, `2026-08-21T17:20:15Z`:

```
$ gh pr view 53 --repo henols/firestarter --json baseRefName,headRefName,mergeCommit,mergedAt,state
{"baseRefName":"beta","headRefName":"gsd/v1.32-at28c-write-path-root-cause-report-provenance",
 "mergeCommit":{"oid":"a1f474b5b3acd2f6fb246ec14ad6774dc52ced3f"},
 "mergedAt":"2026-08-21T17:02:46Z","state":"MERGED"}

$ gh pr view 53 --repo henols/firestarter_app --json baseRefName,headRefName,mergeCommit,mergedAt,state
{"baseRefName":"beta","headRefName":"gsd/v1.32-at28c-write-path-root-cause-report-provenance",
 "mergeCommit":{"oid":"8f2e8d7de709bf58c5e20daea34b17c073ee59b9"},
 "mergedAt":"2026-08-21T17:04:01Z","state":"MERGED"}
```

Both merge commits carry exactly 2 parents each, read back via `gh api repos/<owner>/<repo>/commits/<oid>`
in `152-11-SUMMARY.md` (`a1f474b5...` → parents `7f6afc65be`, `d990a4ce80`; `8f2e8d7d...` → parents
`f505ae77d2`, `a0bfd5e8b3`) — confirming the merge-commit method independently of intent.

**The meta repository's PR was deliberately held until Plan 152-20, and was opened and merged there.**
Measured `2026-08-21T19:07:25Z`:

```
$ gh pr view 38 --repo henols/firestarter_prom --json state,baseRefName,mergedAt,mergeCommit
{"baseRefName":"beta","mergedAt":"2026-08-21T19:07:25Z","state":"MERGED",
 "mergeCommit":{"oid":"9e154847d6fbe4b22f54dade0c95b633e44e0728"}}

$ gh api repos/henols/firestarter_prom/commits/9e154847d6fbe4b22f54dade0c95b633e44e0728 --jq '.parents|length'
2

$ git fetch origin && git cherry origin/beta HEAD
(no output)
```

**The meta repository has no release workflow, so this merge cut nothing.** Confirmed:
`gh release list --repo henols/firestarter_prom` returns no releases at all. Unlike the two sub-repo
merges, which each fired a pre-release by design, this one publishes no artifact.

**Plan 152-20 owns creating it, and here is why it must stay unopened until then:** this phase keeps
writing planning artifacts inside `.planning/` after this plan's own cut — the record corrections
already landed in Waves 1-2 (`ROADMAP.md`, `REQUIREMENTS.md`, `PROJECT.md`), and Waves 4-6+ still owe
the extended claim-gate target list (Plan 152-13), the three issue-thread comments and the two
release bodies actually being posted (Plans 152-14 through 152-18), and the meta-repo close-out
itself (Plan 152-20). Opening the meta PR now would leave every one of those tail commits off
whatever gets merged to `beta` — the exact "partial publish" failure class this phase exists to
prevent, applied to its own record rather than to the sub-repos' code.

## 2. `git cherry`, per sub-repo, captured AFTER the merge

Re-measured live in this plan, not transcribed from `152-11-SUMMARY.md`, against the `origin/beta`
position each repo settled at after **both** the merge and that repo's own pre-release workflow's
version-bump auto-commit (the same position each repo's new cut tag's `targetCommitish` names in
§3 below):

```
$ git -C /workspaces/firestarter fetch origin --quiet
$ git -C /workspaces/firestarter rev-parse origin/beta
88d204a5a023bcad6f708b33150502ba90fdec2b
$ git -C /workspaces/firestarter cherry origin/beta HEAD
(no output)
$ echo $?
0

$ git -C /workspaces/firestarter_app fetch origin --quiet
$ git -C /workspaces/firestarter_app rev-parse origin/beta
86f85d77d8102b633da82aef4b5601947f6cc80b
$ git -C /workspaces/firestarter_app cherry origin/beta HEAD
(no output)
$ echo $?
0
```

Measured here at `2026-08-21T17:20:05Z`. **Literal result: empty output, `rc=0`, in both repos** — not
`-` lines, nothing at all. This is the expected and correct shape under a merge-commit landing: `git
cherry upstream HEAD` lists only commits reachable from `HEAD` that are absent from `upstream` by
patch-id, and under a merge-commit landing every commit that was on the milestone branch becomes an
ancestor of the new `origin/beta` (via the merge commit's second parent), so there is nothing left to
list. This satisfies the same intent an "all `-`" result would have demonstrated under a rebase-style
landing: **nothing on the milestone branch remains re-mergeable into `beta`.**

**This is the oracle that survives a squash; `git merge-base --is-ancestor` is not.** v1.30's close
merged via a **squashed** PR to `beta` (PR #44 → `568e58b`), which made `git merge-base --is-ancestor`
report a **false negative** — the close then looked un-merged even though the work was genuinely
published. `git cherry` does not have this failure mode: it reasons from patch-id equivalence, not
from commit-graph ancestry, so it produces the correct answer under a squash, a rebase, or (as
measured here) a merge commit.

## 3. The two observed cut tags

Read live, this plan, never predicted — see the plan's Task 1 for the full poll sequence and the two
pre-release workflow runs' terminal `conclusion: success` (databaseId `32506085800` for `firestarter`,
databaseId `32506199814` for `firestarter_app`, both already recorded in `152-11-SUMMARY.md` and
re-confirmed still `completed`/`success` at the top of this plan's own Task 1):

```
$ gh release list --repo henols/firestarter --limit 8    # 2026-08-21T17:14:49Z
3.0.0b20  Pre-release  3.0.0b20  2026-08-21T17:07:09Z
...

$ gh release view 3.0.0b20 --repo henols/firestarter \
    --json tagName,createdAt,publishedAt,targetCommitish,isPrerelease,url
{"createdAt":"2026-08-21T17:06:10Z","isPrerelease":true,"publishedAt":"2026-08-21T17:07:09Z",
 "tagName":"3.0.0b20","targetCommitish":"88d204a5a023bcad6f708b33150502ba90fdec2b",
 "url":"https://github.com/henols/firestarter/releases/tag/3.0.0b20"}

$ gh release list --repo henols/firestarter_app --limit 8    # 2026-08-21T17:14:49Z
3.0.0b23  Pre-release  3.0.0b23  2026-08-21T17:06:43Z
...

$ gh release view 3.0.0b23 --repo henols/firestarter_app \
    --json tagName,createdAt,publishedAt,targetCommitish,isPrerelease,url
{"createdAt":"2026-08-21T17:06:41Z","isPrerelease":true,"publishedAt":"2026-08-21T17:06:43Z",
 "tagName":"3.0.0b23","targetCommitish":"86f85d77d8102b633da82aef4b5601947f6cc80b",
 "url":"https://github.com/henols/firestarter_app/releases/tag/3.0.0b23"}
```

Both `targetCommitish` values match the `git cherry` measurement's `origin/beta` positions in §2
exactly, and match this milestone's two merge commits' respective repositories. **Both cuts'
current release body length was measured `0`** before substitution — `gh release view <tag> --repo
<r> --json body -q '.body | length'` → `0` for both — the 0-to-N non-vacuity baseline Plan 152-17 and
Plan 152-18 assert against.

**Never a predicted value:** the app tag is `3.0.0b23`, one higher than the `3.0.0b22` that existed
before this merge; the firmware tag is `3.0.0b20`, one higher than the pre-merge `3.0.0b19`. Both
increments are exactly what each repo's own release workflow computed — read here, not derived by
this record.

## 4. The registry confirmation, read directly from the registry

```
$ curl -s https://pypi.org/pypi/firestarter/json | python3 -c "..."     # 2026-08-21T17:15:10Z
stable info.version: 2.0.7
n_releases: 147
new pre-release tag (3.0.0b23) present in registry: True
  upload_time: 2026-08-21T17:07:09.083895Z  firestarter-3.0.0b23-py3-none-any.whl
  upload_time: 2026-08-21T17:07:10.558274Z  firestarter-3.0.0b23.tar.gz
newest stable tag (2.0.8) present in registry: False
2.0.7 present: True
```

Measured directly against the registry, not inferred from `gh release list`. **The pre-release
channel is in sync**: `3.0.0b23`'s GitHub release published `2026-08-21T17:06:43Z`, and its wheel
uploaded to PyPI `2026-08-21T17:07:09Z` — a **26-second** delta. **The stable channel remains
divergent, exactly as this milestone's research measured before the merge**: PyPI's own
`info.version` still reports `2.0.7`; GitHub's `2.0.8` stable release is entirely absent from the
registry's release map. Nothing in this record, or in either release-note draft, states that `2.0.8`
is installable via `pip` — only `2.0.7` is, per this direct read.

## 5. The post-merge published-branch SHA per sub-repo, and the intended future gitlink

| Sub-repo | `origin/beta` SHA, measured after both the merge and its workflow's own auto-commit | Gitlink this repo should eventually be pinned to |
|---|---|---|
| `firestarter` | `88d204a5a023bcad6f708b33150502ba90fdec2b` | `88d204a5a023bcad6f708b33150502ba90fdec2b` |
| `firestarter_app` | `86f85d77d8102b633da82aef4b5601947f6cc80b` | `86f85d77d8102b633da82aef4b5601947f6cc80b` |

**This is a stated instruction for the milestone close, not an action performed here.** Confirmed
live, this plan, that neither gitlink has been touched:

```
$ git -C /workspaces ls-tree HEAD firestarter firestarter_app
160000 commit d990a4ce80fcb56c9becf2312d1fe8757e1fc54d	firestarter
160000 commit a0bfd5e8b32989a60fc93b94e7b102506e6cf56f	firestarter_app
```

Both gitlinks still point at each sub-repo's pre-merge milestone-branch tip (the merge commit's
*second* parent in each case) — not at `origin/beta`, and not at the post-merge SHAs in the table
above. **`/gsd-complete-milestone` re-pins both gitlinks to the table's right-hand column; this plan
does not perform that re-pin.**

## 6. The instruction

**The beta merges for this milestone are complete; do not re-merge; verify with `git cherry`, never
with ancestry.**

## Notes for the milestone close

Three measured warnings, carried forward from this project's own history of milestone-close defects,
for whoever runs `/gsd-complete-milestone` against this record:

1. **`/gsd-new-milestone` step 6's `phases.clear` operation is destructive and must be skipped.** It
   hard-deletes 50+ phase directories; it is not a reversible archival step.
2. **Milestone close has previously broken its own record gates.** Archiving a section can orphan a
   `lines=N` reference another gate's target list still names, and a prior close's `git rm
   REQUIREMENTS.md` tripped a target list that still expected the file to exist. Verify every record
   gate's target list survives the archival edits, not just that the archival edits themselves
   succeed.
3. **`.planning/research/` is not archived at milestone close.** `git mv` it into the archived
   milestone's directory before the next milestone's researchers run, or their queries will silently
   return nothing from this milestone's research.

---

*Phase: 152-outward-facing-close-operator-gated*
*Written: 2026-08-21*

---

## ⚠ TAIL — commits made to the meta repository AFTER PR #38 merged, which are NOT on `beta`

PR #38 merged at `2026-08-21T19:07:25Z`. Everything committed to `/workspaces` after that moment is on
the milestone branch **only**. As of this record the tail is, by path:

- `.planning/phases/152-outward-facing-close-operator-gated/152-MERGE-RECORD.md` — this file, completed
  by Plan 152-20 after the merge (it could not record the merge before it happened).
- `.planning/phases/152-outward-facing-close-operator-gated/152-20-SUMMARY.md` — Plan 152-20's own
  SUMMARY, which cannot exist until the plan finishes.
- `.planning/phases/152-outward-facing-close-operator-gated/152-CLAIM-GATE-TRANSCRIPTS.md` — the pasted
  result of the final positional-argv gate run over `152-20-SUMMARY.md`.
- `.planning/ROADMAP.md`, `.planning/STATE.md` — whatever phase verification and the close produce.
- Anything a `/gsd-verify-work` or milestone-close step writes after this point.

**How the close must handle this — read literally:**

1. **Push the tail onto `beta` at the close.** Do NOT open a second pull request for it, and do NOT
   re-merge either sub-repository to pick it up.
2. **Do NOT re-merge `firestarter` or `firestarter_app`.** Both are already fully on `beta`
   (`git cherry origin/beta HEAD` is empty in both). Re-merging would cut a second pair of
   pre-releases announcing nothing, under version numbers the published release bodies do not name.
3. **Verify with `git cherry`, never `git merge-base --is-ancestor`.** All three merges in this
   milestone are two-parent merge commits, so ancestry happens to work — but a squash anywhere in the
   history makes `--is-ancestor` a false negative, and this project has already been bitten by that
   once (v1.30's PR #44).
4. **Do not re-pin the gitlinks here.** The intended future gitlink values are in §5 above; pinning
   them is the milestone close's job, not this phase's.
