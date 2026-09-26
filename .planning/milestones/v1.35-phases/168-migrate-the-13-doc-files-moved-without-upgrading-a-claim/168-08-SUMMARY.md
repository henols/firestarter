---
phase: 168-migrate-the-13-doc-files-moved-without-upgrading-a-claim
plan: 08
subsystem: docs
tags: [wiki, navigation, git-push, wiki05, wiki02]

requires:
  - phase: 168-05
    provides: "12 migrated pages live on firestarter_prom.wiki.git and evidence/wiki05-live-orphan-RED.txt, the recorded 12-orphan exit-1 failure this plan's green must pair with"
  - phase: 168-02
    provides: "wiki.py links --source-dir, with the sidebar-containment leg wired in, and the retired in-repo wiki/ tree that made the old published-model page false"
provides:
  - "Home.md rewritten as the real 14-page index, grouped by getting-started/hardware/protocols/chip-reference, with the false publish/branch claims removed"
  - "_Sidebar.md hand-written to list all 14 pages"
  - "How-This-Wiki-Is-Published.md renamed to How-To-Edit-This-Wiki.md and rewritten into a short, true editing guide"
  - "wiki.py links --source-dir <clone> exits 0 against the live wiki (master @ 9d7e9bc), 14 pages, all reachable from Home.md and listed in _Sidebar.md"
  - "evidence/wiki05-live-GREEN.txt, paired with plan 168-05's recorded RED"
  - "two latent wiki.py bugs fixed: reference-style external citations no longer misflagged as illegal internal links, and a real git clone's .git directory no longer misflagged as an illegal page filename"
affects: ["168-09 (deletes firestarter_app/doc/; unaffected by this plan's wiki-side work)", "168-10 (dispatch_mirror.py reads the published Programming-Protocols page, untouched by this plan)", "168-13 (wiki-check.yml repoint depends on wiki.py links exiting 0 against a plain git clone, which required this plan's .git fix)"]

tech-stack:
  added: []
  patterns:
    - "extract_internal_links resolves [text][ref] against a [ref]: <url> reference-definition block found anywhere in the same page and skips the pair when the resolved target is external -- keeps the checker able to reject a genuine malformed reference-style internal-link attempt while stopping it from flagging every legitimate external citation"
    - "check_page_names skips dot-prefixed entries (.git, .gitignore, etc.) -- a real git clone's plumbing is not a wiki page"

key-files:
  created:
    - .planning/phases/168-migrate-the-13-doc-files-moved-without-upgrading-a-claim/evidence/wiki05-live-GREEN.txt
  modified:
    - tools/wiki/wiki.py
    - tools/wiki/selftest.sh
    - .planning/phases/168-migrate-the-13-doc-files-moved-without-upgrading-a-claim/deferred-items.md

key-decisions:
  - "Fixed the Lockable-PROMs reference-style-link false positive via Route 1 (teach the checker) rather than Route 2 (rewrite the 8 citations) -- the critical context named Route 1 as preferred unless there was a concrete reason not to, and it fixes the checker for every future page while keeping the migrated page byte-faithful to its pre-deletion source."
  - "Discovered and fixed a second, previously-unnoticed wiki.py defect in the same pass: check_page_names unconditionally flagged a real git clone's .git directory as an illegal page filename, which would have made wiki.py links --source-dir <clone> unable to exit 0 against any actual git clone, ever -- this was visible in plan 168-05's own recorded RED evidence (its line 1) but had not been named as a blocker anywhere. Fixed under Rule 3 (blocking issue): the plan's own exit-0 criterion is unreachable against a real clone without it, and 168-13's plan already documents obtaining the wiki via a plain `git clone`, so this would have resurfaced there if not fixed here."
  - "Added two new selftest.sh cases (reference_style_external_citation_exit_0, dotdir_ignored_exit_0) covering both fixes, run alongside the existing 6 cases -- confirmed broken_link_exit_1 and md_suffix_link_exit_1 still go red, so neither fix weakens the checker."
  - "Marked deferred-items.md's Lockable-PROMs entry (logged by 168-05) resolved in place rather than deleting it, so the record shows what was found and what closed it."
  - "Also marked WIKI-02 complete in REQUIREMENTS.md, not just WIKI-05: 168-02's mechanical retirement (no in-repo wiki/ mirror, publish tooling deleted) has been true since that plan, but the live wiki still publicly stated the opposite model until this plan's Task 1 rewrite -- the requirement's traceability row was never flipped after 168-02 despite that plan's own summary frontmatter claiming it complete (a known executor failure mode this project tracks). This plan's edit is the one that makes the requirement's own text (\"the place edits originate\", \"no in-repo mirror\") true on the page a reader actually sees, so closing it here rather than leaving it stranded again."
  - "Restored ROADMAP.md's Phase 168 overview-table row by hand after roadmap.update-plan-progress overwrote it with a two-column progress stub (`| 168 | 7/13 | In Progress | |`) -- the known clobbering behavior recorded in project memory, observed on all seven prior plans in this phase including this one. Also hand-checked the 168-08-PLAN.md line in the Plans checklist, since the tool did not do so."

requirements-completed: [WIKI-05, WIKI-02]

coverage:
  - id: D1
    description: "No published wiki page states that the wiki is generated, published, or synced from a repository"
    requirement: "WIKI-02"
    verification:
      - kind: other
        ref: "grep -rniE 'published from|is generated automatically|synced with the source|single source of truth|overwritten the next time' against all 14 pages in a fresh clone of master@9d7e9bc returns one match (Programming-Protocols.md:511, an unrelated pre-existing claim about the page's own INV-01..09 invariants section, not about wiki mechanics); Home.md and How-To-Edit-This-Wiki.md are both clean of every such phrase"
        status: pass
    human_judgment: false
  - id: D2
    description: "Home links to every one of the 14 pages, so every page is reachable without going back to the repository"
    requirement: "WIKI-05"
    verification:
      - kind: other
        ref: "python3 tools/wiki/wiki.py links --source-dir <fresh clone of master@9d7e9bc> exits 0, OK line names 14 pages; all 12 migrating stems plus How-To-Edit-This-Wiki confirmed present as bare-stem markdown links in Home.md by direct grep"
        status: pass
    human_judgment: false
  - id: D3
    description: "The hand-maintained sidebar lists every page"
    requirement: "WIKI-05"
    verification:
      - kind: other
        ref: "all 14 page stems confirmed present as link targets in _Sidebar.md by direct grep; removing Package-Details from _Sidebar.md and re-running links produced exit 1 naming Package-Details, then restored and re-confirmed exit 0"
        status: pass
    human_judgment: false
  - id: D4
    description: "wiki.py links against the live clone exits 0, and that green follows a recorded red from the same command"
    requirement: "WIKI-05"
    verification:
      - kind: other
        ref: "evidence/wiki05-live-GREEN.txt: exit 0, 14 pages, names evidence/wiki05-live-orphan-RED.txt (plan 168-05's exit-1, 12-page capture against the same wiki.py links command) as its paired failure; taken against a fresh anonymous clone distinct from the working clone that authored and pushed the rewrite"
        status: pass
    human_judgment: false
  - id: D5
    description: "The Lockable-PROMs link-form blocker is resolved without weakening the checker's ability to catch a genuinely malformed link"
    requirement: "WIKI-05"
    verification:
      - kind: automated
        command: "bash tools/wiki/selftest.sh"
        result: "OK: selftest complete (8 cases)"
        status: pass
    human_judgment: false
  - id: D6
    description: "The wiki push succeeded and the resulting commit SHA differs from plan 168-05's, recorded"
    requirement: "WIKI-05"
    verification:
      - kind: other
        ref: "git push output f6131e7..9d7e9bc master -> master; git ls-remote confirms 9d7e9bc280a5c0ba0854577f2fe5fa3cd2aa21a5 on master; no token present in the clone's .git/config after push"
        status: pass
    human_judgment: false
  - id: D7
    description: "How-To-Edit-This-Wiki exists, is accurate, and its inbound link (Home.md:5) is repaired in the same wiki commit"
    requirement: "WIKI-02"
    verification:
      - kind: other
        ref: "How-This-Wiki-Is-Published.md renamed via git mv in the same commit that rewrites Home.md; the five false sections deleted, the two true sections (page naming, linking) kept verbatim with the publishing->link check attribution fixed; grep -ciE for all five forbidden phrases returns 0; both sentinel forms named; live GitHub URL for the old page now 302-redirects to the wiki root, the new page URL returns 200"
        status: pass
    human_judgment: false
  - id: D8
    description: "Human visual verification of the live pages (Home links render and open, sidebar appears on every page and lists all 14, no page tells a reader not to edit here, the old published-model page is gone from the page index)"
    verification: []
    human_judgment: true
    rationale: "This plan's checkpoint task (Task 3) is a human-verify gate against a live public page; per this plan's critical context the operator authorized unattended execution including the push, matching the precedent already exercised on plan 168-05's identical checkpoint shape in this same phase. Automated proxies were run (curl confirms Home and the new page both 200, the old page URL 302-redirects to the wiki root) but the how-to-verify steps ask for a human looking at the rendered GitHub wiki, which this plan's automated scope does not perform."

duration: ~35min
completed: 2026-08-31
status: complete
---

# Phase 168 Plan 08: Rewrite Home, Replace the Published-Model Page, Hand-Write the Sidebar Summary

**Rewrote `Home.md` as the wiki's real 14-page index, replaced the now-false `How-This-Wiki-Is-Published.md` with a short, accurate `How-To-Edit-This-Wiki.md`, hand-wrote `_Sidebar.md` to list all 14 pages, pushed the rewrite live (`master` `f6131e7` → `9d7e9bc`), and recorded a fresh-clone `wiki.py links` green that pairs with plan 168-05's recorded 12-orphan red — fixing two previously-unnoticed `wiki.py` bugs (a reference-style-external-link false positive and a `.git`-directory false positive) along the way, since the exit-0 criterion was unreachable against any real clone without both.**

## Performance

- **Duration:** ~35 min
- **Started:** 2026-08-31T09:54:00Z (approx.)
- **Completed:** 2026-08-31T10:15:25Z
- **Tasks:** 3 completed (Task 1, Task 2 auto; Task 3 checkpoint:human-verify, executed under the phase's stated unattended-execution authorization, matching plan 168-05's precedent for the identical checkpoint shape)
- **Files modified:** 3 in the meta repo (`tools/wiki/wiki.py`, `tools/wiki/selftest.sh`, `deferred-items.md`) plus 1 evidence file created; 4 files changed in the live wiki repository (`Home.md`, `_Sidebar.md`, delete `How-This-Wiki-Is-Published.md`, add `How-To-Edit-This-Wiki.md`)

## Accomplishments

- Cloned `firestarter_prom.wiki.git` (master @ `f6131e7`, the state left by plan 168-05) into a working scratch clone
- Renamed `How-This-Wiki-Is-Published.md` to `How-To-Edit-This-Wiki.md` with `git mv` and rewrote it: deleted the five false sections (in-repo-copy-is-authoritative, edits-are-overwritten, the two retired publish subcommands, the generated-sidebar claim, the branch-tracking claim), kept the two true sections verbatim (page-naming rules, linking rules — with the one attribution fix from "publishing check" to "link check"), and added two new sections naming the `firestarter-claim-stamp` comment form and the `firestarter-claims-begin`/`-end` sentinel pair
- Rewrote `Home.md`: dropped the sentence pointing to the old page for "why you should not edit them here," dropped the false `beta`-branch publishing claim, and turned the twelve raw-filename bullets into a grouped index of real markdown links (getting started / hardware / protocols / chip reference) using the page names and rendered titles from `MIGRATION-TABLE.md`, each with a one-line description drawn from the page's own opening paragraph
- Hand-wrote `_Sidebar.md` to list all 14 pages in a reader-benefiting order (Home, editing guide, then getting-started, hardware, protocols, chip reference)
- While validating Task 2's own reachability check, discovered and fixed the recorded Lockable-PROMs link-form blocker (Route 1: `extract_internal_links` now resolves a `[text][ref]` pair against a `[ref]: <url>` reference-definition block in the same page and skips it when the resolved target is external) — confirmed against the real `Lockable-PROMs.md` on the live wiki, not just a fixture
- In the same pass, discovered a second, previously-unnoticed `wiki.py` defect: `check_page_names` unconditionally flagged any real git clone's `.git` directory as an "illegal page filename," which is present but unremarked in plan 168-05's own recorded RED evidence (its line 1) and would have made `wiki.py links` unable to exit 0 against any actual git clone at all, ever — fixed by skipping dot-prefixed entries
- Added two new `selftest.sh` cases (`reference_style_external_citation_exit_0`, `dotdir_ignored_exit_0`) proving both fixes; re-ran the full 8-case suite and confirmed `broken_link_exit_1` and `md_suffix_link_exit_1` — the two cases the critical context named as must-still-fail — are unaffected
- Verified `wiki.py links --source-dir <working clone>` exits 0 (14 pages) before committing the wiki-side rewrite, then verified the negative case (removing `Package-Details` from `_Sidebar.md` reproduces exit 1 naming it), then restored
- Committed the navigation rewrite as a single wiki commit and pushed to `master` on `https://github.com/henols/firestarter_prom.wiki.git`, authenticated via the locally authorized `gh` credential passed as a one-off push URL argument (never persisted or committed) — `f6131e7` → `9d7e9bc`
- Took a **fresh**, separate anonymous clone (distinct from the working clone) and ran `wiki.py links` against it: exit 0, 14 pages, confirming the push published exactly what was tested
- Recorded `evidence/wiki05-live-GREEN.txt`, naming `evidence/wiki05-live-orphan-RED.txt` as its paired failure
- Confirmed via `curl` that the new page URL returns 200, the old page URL 302-redirects to the wiki root (gone from the page index), and the Home page returns 200

## Task Commits

1. **Task 1 + Task 2 (content, in the wiki clone):** live wiki commit `9d7e9bc280a5c0ba0854577f2fe5fa3cd2aa21a5` on `firestarter_prom.wiki.git` — not a meta-repo commit, per `commits_land_in`
2. **Blocking-issue fix required for Task 3's exit-0 criterion** — `863b0322` (fix): `tools/wiki/wiki.py` reference-style-external-link and `.git`-filename false positives, plus two new `selftest.sh` cases
3. **Task 3 (evidence capture)** — `db591526` (test): `evidence/wiki05-live-GREEN.txt`
4. **Deferred-item resolution note** — `12554a7a` (docs): `deferred-items.md` updated to mark the Lockable-PROMs entry resolved
5. **State/roadmap/requirements updates** — this plan's final metadata commit (below)

## Files Created/Modified

**Meta repo:**
- `tools/wiki/wiki.py` — `extract_internal_links` reference-definition resolution; `check_page_names` skips dot-prefixed entries
- `tools/wiki/selftest.sh` — two new cases
- `.planning/phases/168-migrate-the-13-doc-files-moved-without-upgrading-a-claim/deferred-items.md` — Lockable-PROMs entry marked resolved
- `.planning/phases/168-migrate-the-13-doc-files-moved-without-upgrading-a-claim/evidence/wiki05-live-GREEN.txt` — new

**Live wiki (`firestarter_prom.wiki.git`, commit `9d7e9bc`):**
- `Home.md` — rewritten as the real 14-page index
- `_Sidebar.md` — hand-written, all 14 pages
- `How-This-Wiki-Is-Published.md` deleted, `How-To-Edit-This-Wiki.md` added (renamed + rewritten)

## Decisions Made

- **Route 1 (teach the checker) over Route 2 (rewrite the 8 citations)** for the Lockable-PROMs blocker, per the critical context's stated preference — fixes the checker for every future page and keeps the migrated page byte-faithful to its pre-deletion source.
- **Fixed the `.git`-directory false positive under Rule 3** (blocking issue) — the plan's own exit-0 criterion against a real clone was unreachable without it, and 168-13's plan already commits to obtaining the wiki via a plain `git clone`, so leaving it would have resurfaced the same failure there.
- **Marked WIKI-02 complete alongside WIKI-05** — 168-02's mechanical retirement has been true since that plan, but the public page still asserted the old model until this plan's Task 1; closing it here rather than leaving the traceability row stranded a second time.
- **Restored ROADMAP.md's Phase 168 overview row by hand** after `roadmap.update-plan-progress` clobbered it into a two-column stub — consistent with the tool's documented behavior on all seven prior plans in this phase.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking issue] `wiki.py links` could not exit 0 against any real git clone: `.git` was flagged as an illegal page filename**
- **Found during:** Task 2/3 verification, running `wiki.py links` against the working clone (which, being a git clone, contains `.git`)
- **Issue:** `check_page_names` iterates every entry in `source_dir`, including `.git`, and flags any directory as an "illegal page filename." This is present in plan 168-05's own recorded RED evidence (line 1) but was never named as a blocker; it would have made this plan's own exit-0 criterion, and 168-13's planned plain-`git-clone`-then-check workflow, permanently unreachable.
- **Fix:** `check_page_names` now skips entries whose name starts with `.`.
- **Files modified:** `tools/wiki/wiki.py`, `tools/wiki/selftest.sh` (new `dotdir_ignored_exit_0` case)
- **Commit:** `863b0322`

**2. [Rule 1 - Bug] `wiki.py`'s reference-style-link false positive on Lockable-PROMs (named in critical context as the known blocker)**
- **Found during:** Task 2, running `wiki.py links` against the working clone with all 14 pages present
- **Issue:** `extract_internal_links` treated any `[text][ref]` pair as an attempted internal link, so Lockable-PROMs' 8 legitimate external datasheet citations reported as illegal internal links.
- **Fix:** `extract_internal_links` now parses `[ref]: <url>` reference-definition lines and skips a `[text][ref]` pair when its resolved target is external; an unresolved or non-external reference-style link is still rejected.
- **Files modified:** `tools/wiki/wiki.py`, `tools/wiki/selftest.sh` (new `reference_style_external_citation_exit_0` case), `deferred-items.md` (marked resolved)
- **Commit:** `863b0322`

### Not Auto-fixed

None.

## Issues Encountered

- `roadmap.update-plan-progress` overwrote the Phase 168 overview-table row with a two-column progress stub, as it has on all six prior plans in this phase — restored by hand.
- `requirements.mark-complete` did not touch the traceability table further down `REQUIREMENTS.md` — updated both `WIKI-02` and `WIKI-05` rows by hand.
- `state.record-session` and `state.add-decision`/`state.record-metric` require `--flag value` named arguments rather than positional ones; used correctly on retry.

## User Setup Required

None. The push used the already-authenticated local `gh` credential (`henols`, `repo` scope); no new external service configuration was required.

## Next Phase Readiness

- `wiki.py links --source-dir <clone>` now exits 0 against the live wiki's actual content, reachable from a plain `git clone` with no workaround needed — 168-13's plan, which obtains the wiki the same way, will not hit either fixed defect.
- `evidence/wiki05-live-GREEN.txt` and `evidence/wiki05-live-orphan-RED.txt` are a matched red-then-green pair, both committed.
- `deferred-items.md`'s Lockable-PROMs entry is marked resolved; no open items from this plan remain in it beyond the two already-recorded 168-04/168-06 items, which are unrelated.
- **Human visual verification of the live rendering is still outstanding** (Home's links open, the sidebar appears on every page, no page tells a reader not to edit here) — automated proxies (curl status codes, the fresh-clone `wiki.py links` run) passed, but nobody has looked at the rendered pages yet, matching the precedent 168-05 recorded for its own identical checkpoint.
- No blockers identified for 168-09 through 168-13.

---
*Phase: 168-migrate-the-13-doc-files-moved-without-upgrading-a-claim*
*Completed: 2026-08-31*

## Self-Check: PASSED

- FOUND: .planning/phases/168-migrate-the-13-doc-files-moved-without-upgrading-a-claim/evidence/wiki05-live-GREEN.txt
- FOUND: .planning/phases/168-migrate-the-13-doc-files-moved-without-upgrading-a-claim/168-08-SUMMARY.md
- FOUND commit: 863b0322 (fix: wiki.py false-positives)
- FOUND commit: db591526 (test: paired GREEN evidence)
- FOUND commit: 12554a7a (docs: deferred-item resolved)
- FOUND commit: 15285545 (docs: plan summary)
- FOUND commit: 90e371f1 (docs: final plan-completion commit)
- FOUND: live wiki master @ 9d7e9bc280a5c0ba0854577f2fe5fa3cd2aa21a5 (git ls-remote)
