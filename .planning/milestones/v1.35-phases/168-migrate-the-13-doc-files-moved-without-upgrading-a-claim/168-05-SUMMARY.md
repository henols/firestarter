---
phase: 168-migrate-the-13-doc-files-moved-without-upgrading-a-claim
plan: 05
subsystem: docs
tags: [wiki, migration, git-push, honest-stamp, wiki05]

requires:
  - phase: 168-01
    provides: ".planning/v1.35/MIGRATION-TABLE.md with page names, rendered titles and pre-deletion SHAs"
  - phase: 168-02
    provides: "wiki.py links --source-dir, with the sidebar-containment leg wired in"
  - phase: 168-03
    provides: "regenerated firestarter_app/firestarter/data/chip_database.json (the stamp's hash input)"
provides:
  - "12 documentation pages live on firestarter_prom.wiki.git (master 0155a85 -> f6131e7), copied byte-for-byte from the pre-deletion doc/ sources with a bounded edit set"
  - "evidence/wiki05-live-orphan-RED.txt: the real 12-orphan, exit-1 WIKI-05 failure, captured before Home.md was touched"
  - "a firestarter-claim-stamp (db-sha256-16=ccbc8d2c4866a5af verified=2026-08-31) on the 11 claim-bearing pages, computed fresh against 168-03's regenerated database"
  - "firestarter-claims-begin/end regions on the three pages whose tables a resolve-check can scope to: Programming-Protocols, AT28C04-Adapter, Protocol-ID"
affects: ["168-08 (rewrites Home.md and the sidebar; must not re-open this evidence)", "168-11 (HONEST-01 multiset comparison reads these pages)", "168-12 (HONEST-02 stamp/resolve checker reads the claims regions)", "168-13 (wiki-check.yml repoint; inherits the Lockable-PROMs deferred item)"]

tech-stack:
  added: []
  patterns:
    - "cp source -> wiki page name, then an enumerated bounded edit list (title / .planning path removal / cross-file link repair / claim stamp / claim region) -- never retype or summarise"
    - "firestarter-claim-stamp: db-sha256-16=<16hex> verified=<date> as an invisible HTML-comment trailer, computed fresh at push time rather than copied from any earlier discussion value"
    - "firestarter-claims-begin/end sentinels bound a resolve-check to an explicitly delimited table region rather than free-text scraping the whole page (168-RESEARCH's D-09 leg-2 falsification)"

key-files:
  created:
    - .planning/phases/168-migrate-the-13-doc-files-moved-without-upgrading-a-claim/evidence/wiki05-live-orphan-RED.txt
  modified:
    - .planning/phases/168-migrate-the-13-doc-files-moved-without-upgrading-a-claim/deferred-items.md

key-decisions:
  - "Computed the claim-stamp hash fresh (ccbc8d2c4866a5af) rather than reusing the 0cfd3a83e881bfcc value recorded at discussion time -- plan 168-03 regenerated chip_database.json in wave 2, and the hash differs, confirming the fresh-compute instruction was load-bearing, not defensive."
  - "Shield-Revisions.md's unopenable-path removal was done as a minimal in-place rewrite (drop the path, keep the surrounding sentence and the 'Full Investigation History' section header + bullet list) rather than deleting the whole section outright -- an initial full-section deletion undershot the plan's own 10%-line-count band (109 vs 128 source lines, -15%); the revised edit lands at 127 vs 128 (-0.8%) while still removing every .planning/ reference."
  - "For the six app-sourced files whose only heading was an H2 subtitle (Beta-Testing-Install, Community-Validation, Infoic-Field-Dictionary, Package-Details, Protocol-Flags, Protocol-ID), inserted the rendered-title H1 immediately before the existing H2 rather than replacing it -- there was no H1 to 'replace' in these files, and the H2 subtitle is more specific page content, not framing to remove."
  - "Lockable-PROMs.md had no heading at all; inserted '# Lockable PROMs' as a new first line rather than searching for a non-existent H1 to replace."
  - "protocol-id.md:7 and package-details.md:7 / protocol-flags.md:7's inline citations of doc/infoic-field-dictionary.md (plain code-span text, not markdown link syntax) were rewritten to page-title references (some as actual internal links, e.g. [Infoic Field Dictionary](Infoic-Field-Dictionary)) under the same D-13 rule that governs the three researched cross-file .md links -- the intra-corpus reference read_first list named these exact line numbers as needing repair during the move."
  - "Did not fix Lockable-PROMs.md's 8 external reference-style citations ([Infineon][1] etc.) that wiki.py's link-form checker flags as illegal internal-link attempts -- pre-existing in the source, first surfaced by migration, outside this plan's bounded edit set; logged to deferred-items.md for whichever plan owns the post-Home-rewrite clean check."
  - "Pushed via the gh-authenticated credential passed as a one-off URL argument (https://x-access-token:$(gh auth token)@...), never persisted into the clone's git config or committed anywhere -- confirmed the stored remote URL and .git/config carry no token after the push."

requirements-completed: [MIGRATE-01, LEGACY-06, HONEST-02, WIKI-05]

coverage:
  - id: D1
    description: "All 12 migrating documents are published on the live wiki under the names recorded in MIGRATION-TABLE.md; PY32F071-FIRMWARE-INSTALL.md is not published"
    requirement: "MIGRATE-01"
    verification:
      - kind: other
        ref: "git ls-remote https://github.com/henols/firestarter_prom.wiki.git master (f6131e7); fresh --depth 1 clone contains 15 .md files; grep -rl PY32F071 <clone>/*.md returns nothing"
        status: pass
    human_judgment: false
  - id: D2
    description: "No published page contains a .planning/ path a public reader cannot open"
    requirement: "MIGRATE-01"
    verification:
      - kind: other
        ref: "grep -rl 'planning/' <clone>/*.md returns nothing (0 files)"
        status: pass
    human_judgment: false
  - id: D3
    description: "The two GSD-framed pages (Pinout-Safety-Review, SRAM-and-NVRAM-Behavior) read as reference documentation: no phase-artifact title, no audit-trail pointer, safety content intact"
    requirement: "LEGACY-06"
    verification:
      - kind: other
        ref: "H1 has no phase number in either file; grep -c 'audit trail' = 0 for both; grep -c CITED SRAM-and-NVRAM-Behavior.md = 0; DIP24_2816 5V/no-VPP-path guarantee and the NVRAM blank-check limitation both read intact in the migrated text"
        status: pass
    human_judgment: false
  - id: D4
    description: "Every page whose source made per-chip or per-protocol claims carries a freshly computed database stamp; the resolve-check is scoped to an explicit claims region on the three pages where a table can be checked cleanly"
    requirement: "HONEST-02"
    verification:
      - kind: other
        ref: "11 of 12 pages carry firestarter-claim-stamp: db-sha256-16=ccbc8d2c4866a5af verified=2026-08-31 (matches sha256sum of the current chip_database.json, truncated to 16 hex); Beta-Testing-Install.md carries none (confirmed clean of chip/protocol claims); exactly 3 pages (Programming-Protocols, AT28C04-Adapter, Protocol-ID) carry a firestarter-claims-begin/end region; Shield-Revisions.md carries none, by design"
        status: pass
    human_judgment: false
  - id: D5
    description: "The §0 Programming-Protocols tables survive the move byte-for-byte (Pitfall 6 / test_dispatch_mirror's table-shape dependency)"
    requirement: "HONEST-02"
    verification:
      - kind: other
        ref: "diff of the 25 pipe-rows inside the claims region against the first 25 pipe-rows of firestarter/doc/PROTOCOLS.md: no differences"
        status: pass
    human_judgment: false
  - id: D6
    description: "The live 12-orphan failure of wiki.py links is captured as evidence before Home.md is rewritten, with the correct exit status"
    requirement: "WIKI-05"
    verification:
      - kind: other
        ref: ".planning/phases/168-.../evidence/wiki05-live-orphan-RED.txt: 12 lines matching 'orphan page not linked', each naming one of the 12 page stems, trailing 'exit 1'; git diff 0155a85..f6131e7 -- Home.md _Sidebar.md How-This-Wiki-Is-Published.md is empty (untouched by this push)"
        status: pass
    human_judgment: false
  - id: D7
    description: "The wiki push itself succeeded cleanly and the resulting commit SHA is recorded"
    requirement: "WIKI-05"
    verification:
      - kind: other
        ref: "git push output '0155a85..f6131e7 master -> master'; git ls-remote confirms f6131e7bada724d4b54a1733c4be5923a501f529 on master; no token present in .git/config or any committed file"
        status: pass
    human_judgment: false
  - id: D8
    description: "Human visual verification of the live pages (tables render, hyphen-hazard titles render correctly, no visible stamp/sentinel comments, Pinout-Safety-Review reads without GSD context)"
    verification: []
    human_judgment: true
    rationale: "This plan's checkpoint task (Task 3) is a human-verify gate against a live public page; the operator authorized unattended execution of this phase, but the visual-rendering claims (tables render as tables, hyphen-hazard page titles display correctly, no visible HTML comments) require a human looking at the rendered GitHub wiki pages, which no automated check in this plan's scope performs."

duration: ~22min
completed: 2026-08-31
status: complete
---

# Phase 168 Plan 05: Publish 12 Documentation Pages to the Live Wiki Summary

**Cloned `firestarter_prom.wiki.git`, copied all 12 migrating `doc/` files to their recorded page names with a bounded edit set (title, unopenable-path removal, cross-file link repair, freshly-computed database stamp, claims regions on 3 pages), pushed the result live (`master` `0155a85` → `f6131e7`), then captured the real 12-orphan `wiki.py links` failure before anything touched `Home.md`.**

## Performance

- **Duration:** ~22 min
- **Started:** 2026-08-31T08:52:00Z (approx.)
- **Completed:** 2026-08-31T09:08:56Z
- **Tasks:** 3 completed (Task 1, Task 2 auto; Task 3 checkpoint:human-verify, executed under the phase's stated unattended-execution authorization)
- **Files modified:** 2 in the meta repo (`deferred-items.md`, the new evidence file); 12 new files pushed to the external wiki repository

## Accomplishments

- Cloned `firestarter_prom.wiki.git` into a scratch directory outside all three tracked repositories; verified the anonymous clone needs no credentials
- Copied `PROTOCOLS.md`, `SHIELD-REVISIONS.md`, and `AT28C04-ADAPTER.md` into the clone under their recorded page names, applying only the plan's enumerated edits: rendered-title H1, removal of all 6/4/1 unopenable `.planning/` references, a freshly-computed `firestarter-claim-stamp`, and a `firestarter-claims-begin/end` region around Programming-Protocols' §0 tables and AT28C04-Adapter's part-number table — proved byte-for-byte identical to source inside the region
- Copied the nine app-sourced files under their recorded page names, applying the same bounded edit set plus the three researched cross-file link rewrites and the two intra-corpus doc-path citations (`package-details.md:7`, `protocol-flags.md:7`, `protocol-id.md:7,22`, `infoic-field-dictionary.md:146`) not previously captured as formal links
- De-framed `Pinout-Safety-Review.md` and `SRAM-and-NVRAM-Behavior.md`: dropped both phase-number title suffixes, both audit-trail pointer lines, and the three `[CITED: .planning/...]` markers in the SRAM file — all safety content (the DIP24 5V/no-VPP guarantee, the NVRAM blank-check limitation) verified intact in the result
- Confirmed `PY32F071-FIRMWARE-INSTALL.md` was not copied anywhere in the clone
- Pushed all 12 pages as a single commit to `master` on the live public wiki (`0155a85` → `f6131e7`), authenticated via the locally-authorized `gh` credential passed as a one-off push argument (never persisted or committed)
- Immediately after the push, and before touching `Home.md`, ran `wiki.py links` against a fresh clone of the pushed state and captured its full output (12 `orphan page not linked` lines + the pre-existing sidebar-containment leg's 12 matching lines + 8 pre-existing reference-link-form errors in `Lockable-PROMs.md`, discussed below) with exit status 1 to `evidence/wiki05-live-orphan-RED.txt`
- Verified `Home.md`, `_Sidebar.md`, and `How-This-Wiki-Is-Published.md` are byte-identical between `0155a85` and `f6131e7` — this plan did not touch them

## Task Commits

1. **Task 1: Clone the wiki and lay down the three firmware-sourced pages** — no meta-repo commit (all work lives in the untracked scratch clone, per `commits_land_in`)
2. **Task 2: Lay down the nine app-sourced pages, including the two de-framed ones** — `bbbbadd4` (docs) — logs the one discovered-but-deferred issue (Lockable-PROMs' reference-link false positives); the page content itself lives in the scratch clone, not the meta repo
3. **Task 3: Push the 12 pages, then capture the live orphan failure before touching Home** — `b01e4edc` (test) — the evidence file; the page push itself is an external wiki commit (`f6131e7`), not a meta-repo commit

## Files Created/Modified

**Meta repo:**
- `.planning/phases/168-migrate-the-13-doc-files-moved-without-upgrading-a-claim/evidence/wiki05-live-orphan-RED.txt` — the captured 12-orphan, exit-1 RED
- `.planning/phases/168-migrate-the-13-doc-files-moved-without-upgrading-a-claim/deferred-items.md` — logged the Lockable-PROMs reference-link discovery

**Live wiki (`firestarter_prom.wiki.git`, commit `f6131e7`):**
- `Programming-Protocols.md`, `Shield-Revisions.md`, `AT28C04-Adapter.md` (from `firestarter/doc/`)
- `Beta-Testing-Install.md`, `Community-Validation.md`, `Infoic-Field-Dictionary.md`, `Lockable-PROMs.md`, `Package-Details.md`, `Pinout-Safety-Review.md`, `Protocol-Flags.md`, `Protocol-ID.md`, `SRAM-and-NVRAM-Behavior.md` (from `firestarter_app/doc/`)

## Decisions Made

- **Claim-stamp hash computed fresh** (`ccbc8d2c4866a5af`, `verified=2026-08-31`) rather than reusing the discussion-time value — confirmed different from `0cfd3a83e881bfcc`, proving 168-03's database regeneration actually changed the file and that the "compute fresh" instruction mattered.
- **`Shield-Revisions.md`'s unopenable-path removal redone as a minimal in-place edit** after an initial pass (deleting the whole "Full Investigation History" section outright) undershot the 10%-line-count band; the final version keeps the section header and its bullet list, rewriting only the two sentences that named the `.planning/` path, landing at 127 vs 128 source lines.
- **H1 insertion for six app-sourced files with no true H1** (only an H2 subtitle): inserted the rendered title as a new H1 immediately above the existing H2, rather than replacing anything, since there was no H1 to replace and the H2 is legitimate page content.
- **`Lockable-PROMs.md` had no heading at all**; inserted `# Lockable PROMs` as the new first line.
- **Intra-corpus doc-path citations repointed to page titles**, some as internal wiki links (`[Infoic Field Dictionary](Infoic-Field-Dictionary)`), matching D-13's page-title-not-URL rule and covering the four locations the plan's `read_first` named as needing repair during the move rather than after.
- **Push authenticated via a one-off `gh auth token` URL argument**, never written into the clone's persisted git config or any committed file — confirmed clean afterward.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `Shield-Revisions.md`'s first unopenable-path edit undershot the plan's own 10% line-count band**
- **Found during:** Task 1, self-verification pass after the initial edit
- **Issue:** Deleting the entire "Full Investigation History" section (its whole content depended on the unopenable `.planning/v1.7-SHIELD-REVS.md` path) dropped the file to 109 lines against a 128-line source — a 15% reduction, outside the acceptance criterion's 10% band even though the deletion was individually defensible under D-11.
- **Fix:** Re-copied the source fresh and redid the edit minimally — kept the section header and its bullet list of topic names, rewriting only the two sentences that literally named the `.planning/` path, dropping the "Meta-repo is private" trailer sentence that depended on "the path above." Result: 127 vs 128 lines (−0.8%), zero `.planning/` references remaining.
- **Files modified:** `Shield-Revisions.md` (in the wiki scratch clone, not tracked)
- **Commit:** n/a (pre-push content edit; not a tracked-repo change)

### Not Auto-fixed (logged as deferred)

**Lockable-PROMs.md's 8 external reference-style link citations trip `wiki.py`'s internal-link-form checker.** `wiki.py`'s `extract_internal_links` cannot distinguish a `[text][ref]`-style external citation (resolved by a `[N]: https://...` definition elsewhere in the same file) from a malformed internal-link attempt, so all 8 of the file's legitimate external datasheet citations report as `illegal internal link form`. This is pre-existing content, first exercised by the migration (the checker never ran against it while the file lived in the app repo); fixing it would mean rewriting the citations into inline-link form, which is outside this plan's bounded edit set (title / unopenable paths / cross-file links / stamp). Logged to `deferred-items.md` for whichever plan owns the post-Home-rewrite clean `wiki.py links` run.

---

**Total deviations:** 1 auto-fixed (Rule 1, line-count band), 1 logged-deferred (pre-existing checker false-positive, out of scope)
**Impact on plan:** The auto-fix corrected a genuine acceptance-criterion miss with no content loss. The deferred item does not affect this plan's own acceptance criteria (neither Task 2's automated verify nor the plan's top-level `<verification>` requires a clean `wiki.py links` run — only the 12-orphan count and exit status matter here) and is explicitly out of this plan's edit scope.

## Issues Encountered

None beyond the deviation above.

## User Setup Required

None. The push used the already-authenticated local `gh` credential (`henols`, `repo` scope); no new external service configuration was required.

## Next Phase Readiness

- 12 pages are live and readable on `firestarter_prom.wiki.git` at `f6131e7`; `PY32F071-FIRMWARE-INSTALL.md` remains unpublished as designed.
- `evidence/wiki05-live-orphan-RED.txt` is committed and `Home.md` is confirmed untouched — plan 168-08 can rewrite `Home.md`/`_Sidebar.md` next without destroying this evidence.
- The claim-stamp (`db-sha256-16=ccbc8d2c4866a5af`) and the three claims regions are in place for 168-12's HONEST-02 checker to read.
- `deferred-items.md` carries one open item (Lockable-PROMs reference-link false positives) for whichever plan owns the post-Home-rewrite clean check (likely 168-13's `wiki-check.yml` repoint).
- **Human verification of the live rendering is still outstanding** (Task 3's `how-to-verify` steps: tables render as tables, `AT28C04-Adapter`/`SRAM-and-NVRAM-Behavior` titles render correctly, no visible stamp/sentinel comments, `Pinout-Safety-Review` reads without GSD context) — the operator's unattended-execution authorization covered the push itself, not a substitute for eventually looking at the rendered pages at `https://github.com/henols/firestarter_prom/wiki`.
- No blockers identified for 168-06 through 168-13.

---
*Phase: 168-migrate-the-13-doc-files-moved-without-upgrading-a-claim*
*Completed: 2026-08-31*

## Self-Check: PASSED

- FOUND: .planning/phases/168-migrate-the-13-doc-files-moved-without-upgrading-a-claim/evidence/wiki05-live-orphan-RED.txt
- FOUND: .planning/phases/168-migrate-the-13-doc-files-moved-without-upgrading-a-claim/168-05-SUMMARY.md
- FOUND: .planning/phases/168-migrate-the-13-doc-files-moved-without-upgrading-a-claim/deferred-items.md
- FOUND commit: bbbbadd4
- FOUND commit: b01e4edc
- FOUND commit: 14e00adf
- FOUND: live wiki master @ f6131e7bada724d4b54a1733c4be5923a501f529 (git ls-remote)
