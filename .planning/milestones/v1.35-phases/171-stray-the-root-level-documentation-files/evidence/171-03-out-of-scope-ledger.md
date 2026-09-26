# Phase 171 Out-of-Scope Ledger

Items found during Phase 171 that were deliberately **not** acted on, so a future failure or
drift report is attributed correctly and is not mistaken for regression introduced by this
phase. Each item records the measured fact, why it was left alone, and who owns it.

1. **`MIGRATION-TABLE.md`'s `Protocol-Flags` and `Protocol-ID` rows list pages a fresh clone of
   the live wiki does not have.** This is confirmed-real drift from the operator's post-168
   wiki reorganisation, not something introduced by this plan. `171-CONTEXT.md`'s deferred list
   assigns it to whoever owns the table; this phase only appends rows, it does not correct
   existing ones. Worth fixing before the Backlog 999.9 repository-rename sweep greps the table
   for source paths, since those two rows would currently send it after pages that no longer
   exist.

2. **`.github/workflows/wiki-check.yml:104-107` passes `--wiki-dir` to `dispatch_mirror.py`,
   which accepts only `--app-dir` and `--fw-dir`** (`tools/wiki/dispatch_mirror.py:157-158`).
   That step would exit 2 the very first time the workflow ever runs. Introduced by `4b14a5a2`,
   and present on `origin/beta` as well as this branch. Not fixed here — recorded so a future
   red run of that workflow is not blamed on Phase 171.

3. **`wiki-check.yml` is absent from `origin/main`, the default branch of
   `henols/firestarter_prom`, so GitHub never registered its `schedule` or `workflow_dispatch`
   triggers.** `gh workflow list --all` returns only `Catalog sync check` — `wiki-check.yml`
   is not among the registered workflows at all. **There was no CI safety net for this phase.**
   Every check this plan and its predecessors ran, ran locally, and its output is committed to
   this evidence directory as the only proof any of it happened. A reader must not assume a
   green cron run covered this work — none exists yet. Putting the workflow on the default
   branch is Phase 172/173 territory.

4. **`firestarter/test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md:637` names `SECURITY.md`
   in a Phase 117 list of files that were untracked at that point in project history.** It is
   plain text, not a markdown link, and it does not resolve to the deleted file in any tooling
   sense. Historical-by-intent per the operator's standing citation-repair rule (repair stale
   `.planning/` → live-file citations, but never rewrite `.planning/` → `.planning/` citations
   or historical archive records that are correct as of the moment they were written). No
   action taken; do not edit it. This also corrects `171-CONTEXT.md`'s claim that the
   repo-wide `SECURITY.md` grep produced only the file's own title line as a hit — 171-02's
   sweep found this second, permitted hit as well.

5. **`firestarter_app/tools/build_db.py` carries an uncommitted modification that predates
   Phase 171 and is unrelated to it.** It has been present in the working tree since before
   this phase started. Excluded from every Phase 171 commit by explicit path-scoped staging
   (`git add <path>`, never `git add -A` or `git commit -a`); left unresolved rather than
   stashed or reverted, per the standing prohibition on `git stash` inside a shared checkout
   and the general rule against touching work that is not this phase's own.

6. **`firestarter_app/firestarter.egg-info/SOURCES.txt` is gitignored, still lists two of the
   three deleted files, and is re-absorbed by `setuptools` into any sdist built directly in the
   live working tree.** This is the measured cause of the 220-entry false positive that a
   working-tree sdist build would otherwise report (171-02's `171-02-sdist-clean-tree-diff.txt`
   used a clean `git archive` extraction instead, precisely to avoid it). No repository change
   is owed — the file is a build artifact, not tracked source — and the standing rule going
   forward is simply never to build the packaging oracle directly in the live working tree.

7. **`github.com/henols/firestarter_app/blob/main/autocomplete.md` still resolves (HTTP 200)
   and still serves the older, argcomplete-era text**, until the `gsd/v1.35-…` milestone branch
   merges to `main`. The three LEGACY requirements' success criteria are properties of the
   milestone branch, so this is a sequencing note about `main` lagging behind rather than a
   criterion failure of this plan. It resolves itself at milestone merge, which is out of this
   plan's scope.

8. **Observing that `henols/firestarter_app`'s Security tab is empty is deferred to the
   milestone merge.** The GitHub Security tab derives from the repository's default branch
   (`main`), where `SECURITY.md` has never existed on any commit reachable from `main`. Calling
   `gh api repos/henols/firestarter_app/community/profile -q .files.security_policy` today
   returns `null` regardless of anything this phase does, so recording that as a pass here
   would be vacuous — it proves nothing this plan changed. The meaningful check is only
   possible after the milestone branch merges to `main`, which is out of scope for Phase 171.
