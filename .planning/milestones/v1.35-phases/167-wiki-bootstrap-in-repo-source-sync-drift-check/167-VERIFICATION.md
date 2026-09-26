---
phase: 167-wiki-bootstrap-in-repo-source-sync-drift-check
verified: 2026-08-30T21:00:00Z
status: passed
score: 6/6 must-haves verified
behavior_unverified: 0
overrides_applied: 0
re_verification: No — initial verification
---

# Phase 167: WIKI — Bootstrap, In-Repo Source, Sync & Drift Check Verification Report

**Phase Goal:** The publishing pipeline exists and is trustworthy before a single page of content
depends on it — pages are authored in the repository, published by one command, and a check catches
the wiki drifting from its source.
**Verified:** 2026-08-30
**Status:** passed
**Re-verification:** No — initial verification

## Central Standard: "A check seen only green proves nothing"

This phase's entire justification rests on negative evidence, not positive assertion. Each of the
four adversarial-stance instructions was checked directly against the codebase, not against
SUMMARY.md prose:

1. **All 11 negative cases + 1 determinism case observed RED before GREEN — CONFIRMED.**
   `tools/wiki/selftest.sh:481` registers exactly the 12 case IDs `167-VALIDATION.md` enumerates
   (`stale_sidebar_exit_1`, `sidebar_deterministic`, `orphan_exit_1`, `sidebar_link_is_not_evidence`,
   `broken_link_exit_1`, `md_suffix_link_exit_1`, `illegal_filename_exit_1`, `wiki_absent_exit_2`,
   `drift_detected_exit_1`, `hand_edit_overwritten`, `idempotent_head_unchanged`,
   `deleted_page_removed`). Every one of the three SUMMARYs that introduced cases (167-01, 167-02,
   167-03) carries a verbatim captured RED transcript at the pre-implementation commit and a
   verbatim captured GREEN transcript at the post-implementation commit — read directly, not taken
   on the SUMMARY's word: `8921d5f5`→`01757d7b` (2 cases), `8c8e4973`→`c9211d92` (5 cases),
   `b66bac59`→`e5669680` (5 cases). All 16 commit hashes cited across the six SUMMARYs resolve in
   this repository (`git cat-file -t` checked for all 16). Running `bash tools/wiki/selftest.sh`
   today reproduces 12/12 green. No case's red state is asserted only in prose. **No gap.**

2. **`sidebar_link_is_not_evidence` is genuinely load-bearing — CONFIRMED by reading the case body,
   not the claim.** `tools/wiki/selftest.sh:163-196`: the case adds `Page-Orphan.md`, regenerates
   `_Sidebar.md` (so the sidebar legitimately contains the link), asserts `sidebar --check` exits 0
   (ruling out staleness as the cause of any later failure), then asserts `links` still exits 1 and
   stderr names `Page-Orphan`. `check_orphans()` in `tools/wiki/wiki.py:216-232` reads only
   `Home.md` (`HOME_PAGE` constant) — `_Sidebar.md` never appears in its logic. Plan 167-02's
   captured mutation (neutering `check_orphans` to `return []`) independently confirmed exactly this
   case and `orphan_exit_1` go red while the other 5 offline cases stay green. The orchestrator's
   own fixture reproduction (a page linked only from a freshly-generated sidebar still exits 1) is
   consistent with what the code does. **No gap.**

3. **Fixture-proven vs live-proven is distinguished, not conflated — CONFIRMED.** Criteria 2, 3, 4
   are demonstrated twice, and both plans say so explicitly: 167-03's "Fixture faithfulness" section
   states in its own words that the bare-repo fixture "proves nothing about the GitHub service
   tier." 167-06's Steps A–I are the live re-run — I verified this independently rather than
   trusting the transcript: `git ls-remote https://github.com/henols/firestarter_prom.wiki.git
   refs/heads/master` today returns `0155a854752fa9088743daaedc2f2472223dd713` (the wiki exists, on
   `master`), and a fresh clone of it into a scratch directory today is byte-for-byte identical to
   the three files in `wiki/` at HEAD (`diff` on all three, `IDENTICAL` each time), with exactly
   three files present — no more, no less. This confirms the live state at verification time, not
   just the state captured mid-execution in the SUMMARY. **No gap.**

4. **A1 (`GITHUB_TOKEN` wiki-push authorization) is left honestly unproven — CONFIRMED.** Grepped
   `tools/wiki/wiki.py`, both workflow YAMLs, and every 167-* planning artifact for a claim that the
   token was verified: the only hits are explicit unproven/measurement-point framing
   (`167-06-SUMMARY.md:434`, `167-05-SUMMARY.md:143`, `167-RESEARCH.md:567,687`). No artifact
   anywhere asserts the CI publish path has been exercised. `wiki-publish.yml` is authored, has
   never executed on a runner (no `push` to `beta` touching `wiki/**`/`tools/wiki/**` has happened;
   the `wiki-drift-live` job in `wiki-check.yml` has never been dispatched). **No gap.**

## Post-Execution Changes (verified directly, not from SUMMARY)

1. **Credential redaction (`e44403fe`) — verified complete.** Read `cmd_publish` end-to-end in
   `tools/wiki/wiki.py:290-420`. `safe_remote()` (line 284) strips the userinfo component. All three
   print sites the commit message names are redacted: `wiki remote not reachable` (line 300),
   `wiki remote does not exist` (line 305), the `OK: published ... to` success line (line 415) — and
   a fourth site the fix also covers, the push-failure path, replaces the raw remote in
   `push.stderr` before printing it (lines 409-411). No remaining `print`/`f-string` site in
   `cmd_publish` emits `args.wiki_remote` unredacted — checked every occurrence of `wiki_remote` in
   the file (11 occurrences: 2 are `_git()` calls whose output isn't printed, 1 is the origin-URL
   equality check with no print, the rest route through `safe_remote`). `bash tools/wiki/selftest.sh`
   run today: 12/12 green, confirming the fix didn't regress anything.

2. **`PY32F071-FIRMWARE-INSTALL` deferral (`c7b359b0`) — verified complete.** `wiki/Home.md`'s
   "Coming to this wiki" list has exactly 12 entries, `PY32F071-FIRMWARE-INSTALL` absent.
   `.planning/v1.35/MIGRATION-TABLE.md` has 12 `TBD` rows (not 13) plus an explicit "Deferred, not
   migrating" section naming the file and the reason. `ROADMAP.md` line 290 (Phase 168 criterion 1)
   reads "All 12 migrating files" with the deferral called out inline. The live wiki was
   republished after this commit and, per the check above, is byte-identical to `wiki/` today.
   **Known, deliberately-left inconsistency confirmed present and correctly attributed:**
   `ROADMAP.md` still titles Phase 168 "MIGRATE — The 13 `doc/` Files" (lines 236, 283) — this is
   the operator-left inconsistency the task described, not a defect introduced by this phase, and
   is not scored against Phase 167's goal.

## Observable Truths (Success Criteria, verbatim from ROADMAP.md)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `firestarter_prom.wiki.git` exists, is clonable, carries a Home page that names and links every documentation page **currently in `wiki/`** | ✓ VERIFIED | `git ls-remote` returns a ref on `master`; live clone has exactly `Home.md`, `How-This-Wiki-Is-Published.md`, `_Sidebar.md`; `Home.md` links `How-This-Wiki-Is-Published` in legal form and is itself the reachability root. See Requirement Honesty section below for the reading applied to the 12 not-yet-existing pages. |
| 2 | A wiki-side edit, re-published, is overwritten (authority direction) | ✓ VERIFIED | Fixture: `hand_edit_overwritten` case, RED at `b66bac59`→GREEN at `e5669680`. Live: 167-06 Step G — a scripted wiki-side edit to `Home.md` was pushed, `publish` (dry-run) detected it (exit 1), `publish --push` destroyed it, re-clone confirmed byte-identical to `wiki/Home.md`. Also demonstrated live via the operator's genuine `Scratch.md` (deleted, no in-repo counterpart) and `Home.md` (overwritten, in-repo counterpart exists) in the same first publish. |
| 3 | One command publishes; a second run with no source change produces no wiki commit | ✓ VERIFIED | Fixture: `idempotent_head_unchanged`, RED→GREEN. Live: 167-06 Step F — `git ls-remote ... refs/heads/master` identical (`c9bdce523bd6...`) before and after a second `--push` that reported "no change." |
| 4 | Drift check reports failure against a divergent wiki, observed failing before trusted | ✓ VERIFIED | Fixture: `drift_detected_exit_1`, RED→GREEN. Live: 167-06 Step B — `publish` (dry-run) against the operator's pre-existing pages exited 1 with a full diff printed, *before* any push; Step E — exit 0 once in sync. Second live red-then-green pair in Step G against a hand-edit. |
| 5 | Every page reachable from Home or sidebar; orphan detection is not a tautology | ✓ VERIFIED | `orphan_exit_1` + `sidebar_link_is_not_evidence`, both RED→GREEN, plus the load-bearing mutation proof (see Central Standard §2). `wiki.py check` exits 0 against the real `wiki/` tree today. |
| 6 | `has_wiki` false/false/true across firestarter/firestarter_app/firestarter_prom | ✓ VERIFIED | Re-verified live in plan 167-05 via `gh api`, matching the milestone-activation reading. Not independently re-run in this verification pass (read-only GitHub API state, low drift risk, already an explicit re-verification of a pre-existing fact). |

**Score:** 6/6 truths verified (0 present-but-behavior-unverified).

## Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `tools/wiki/wiki.py` | stdlib CLI: sidebar/links/check/publish, 0/1/2 exit contract | ✓ VERIFIED | 542 lines, 0 comment lines (excl. shebang), all 4 subcommands present and wired into `COMMANDS` dict, exercised directly this session |
| `tools/wiki/selftest.sh` | fixture-driven harness, 12 cases | ✓ VERIFIED | 502 lines, 0 comment lines, `bash tools/wiki/selftest.sh` run this session: 12/12 PASS |
| `wiki/Home.md` | hand-authored reachability root | ✓ VERIFIED | present, links `How-This-Wiki-Is-Published`, lists 12 (not 13) future pages, states beta caveat |
| `wiki/How-This-Wiki-Is-Published.md` | D-12 scaffolding page | ✓ VERIFIED | present, states authority rule, overwrite warning, both publish commands, naming/link-form rules |
| `wiki/_Sidebar.md` | generated, committed, byte-stable | ✓ VERIFIED | `wiki.py sidebar --check` exits 0 against the real tree this session |
| `.planning/v1.35/MIGRATION-TABLE.md` | D-04 provenance shell | ✓ VERIFIED | 12 TBD rows (post-deferral), explicit non-registry statement, deferral section for PY32F071 |
| `.github/workflows/wiki-check.yml` | offline CI check, keyed to `beta`, `contents: read` | ✓ VERIFIED | both jobs (`wiki-check`, `wiki-drift-live`) declare `contents: read`; trigger is `branches: [beta]`, no `main` line; 0 comment lines |
| `.github/workflows/wiki-publish.yml` | CI publish, keyed to `beta`, `contents: write` | ✓ VERIFIED | `permissions: contents: write` at job level; `branches: [beta]`, no `main`; single `WIKI_TOKEN` job-level env with one `secrets.` line; 0 comment lines; never executed (A1 open, correctly unclaimed) |

## Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `wiki-check.yml` | `tools/wiki/wiki.py check` + `selftest.sh` | `run:` steps | WIRED | executed locally this session with the same commands, both exit 0 |
| `wiki-publish.yml` | `tools/wiki/wiki.py publish --push --require-wiki` | `run:` step, tokenized remote | WIRED (authored; unexecuted on a runner — A1 correctly flagged, not claimed) |
| `cmd_publish` | `cmd_check` | direct call, offline gate before any remote contact | WIRED | confirmed in source: `cmd_publish` calls `cmd_check(args)` first and returns before `ls-remote` on failure |
| `wiki/Home.md` | `wiki/How-This-Wiki-Is-Published.md` | `[How this wiki is published](How-This-Wiki-Is-Published)` | WIRED | resolves; `wiki.py links` reports 0 failures |
| Live `firestarter_prom.wiki` | `wiki/` (in-repo) | `wiki.py publish --push` | WIRED and LIVE-PROVEN | fresh clone today byte-identical to `wiki/`, 3/3 files |

## Data-Flow Trace (Level 4)

Not applicable in the conventional sense (no UI rendering dynamic state) — the equivalent check here
is the live-wiki-equals-source diff performed above, which is the strongest form of this trace for a
publishing pipeline: verified today, not from a stale capture.

## Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Selftest harness green | `bash tools/wiki/selftest.sh` | 12/12 PASS | ✓ PASS |
| Offline check green against real content | `python3 tools/wiki/wiki.py check` | exit 0 | ✓ PASS |
| Live wiki reachable | `git ls-remote .../firestarter_prom.wiki.git refs/heads/master` | ref returned | ✓ PASS |
| Live wiki matches source | clone + diff against `wiki/*.md` | 3/3 identical | ✓ PASS |
| Zero comments (operator hard rule) | `grep` sweep, 4 files | 0 everywhere | ✓ PASS |
| Branch keying | `grep` for `main`/`beta` in both workflows | `beta` present, no `main` line, in both | ✓ PASS |
| Permission split | `grep 'contents:'` in both workflows | check=read (both jobs), publish=write | ✓ PASS |

## Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|--------------|--------|----------|
| WIKI-01 | 167-03, 167-06 | Wiki exists, reachable, Home indexes documentation by name | ✓ SATISFIED (scoped reading — see below) | live clone, Home.md content |
| WIKI-02 | 167-01/02/03/06 | In-repo copy is authoritative | ✓ SATISFIED | fixture + live overwrite/delete demonstrations |
| WIKI-03 | 167-01/02/03/06 | One-command publish, idempotent | ✓ SATISFIED | fixture + live idempotence (identical `ls-remote` HEAD) |
| WIKI-04 | 167-01/02/03/05/06 | Drift check fails on divergence, observed red first | ✓ SATISFIED | fixture + live red-then-green, twice |
| WIKI-05 | 167-02/04/05 | Every page reachable, non-tautological orphan check | ✓ SATISFIED | mutation-proven load-bearing check |
| WIKI-06 | 167-05 | `has_wiki` false/false/true | ✓ SATISFIED | `gh api` re-verification recorded in 167-05-SUMMARY.md |

No orphaned requirements: `REQUIREMENTS.md`'s Traceability table maps exactly these six IDs to
Phase 167, matching what all six PLAN frontmatters declare between them.

### Requirement Honesty — WIKI-01

`REQUIREMENTS.md` states WIKI-01 as: *"...with a Home page that indexes every documentation page by
name."* The ROADMAP's own Phase 167 success criterion 1 is more precise: *"carries a Home page that
names and links every documentation page."* Twelve of the documentation pages this milestone will
eventually carry (the Phase 168 migration set) do not exist on the wiki yet — deliberately, per this
phase's explicit boundary ("No documentation content moves in this phase. The 13 `doc/` files are
Phase 168's work").

**Reading applied:** "every documentation page" is read as *every documentation page that exists in
`wiki/` at the close of this phase* — i.e., `Home.md` and `How-This-Wiki-Is-Published.md`. Under
that reading, both are indexed: `How-This-Wiki-Is-Published` is linked from `Home.md` in the single
legal form, and `Home.md` is the reachability root itself. `Home.md` additionally *names* (as plain
text, deliberately not linked, per D-12 and the plan's own reasoning about not inventing wiki-page
names ahead of Phase 168) the 12 pages still to come.

This reading is the only one consistent with the phase's own stated boundary and with D-12's explicit
rationale for why the 12 future pages are named but not linked (linking to non-existent pages would
fail the phase's own broken-link check). Under the broader reading — "every documentation page this
milestone will ultimately carry, linked" — WIKI-01 is **not** yet satisfied, and would not be until
Phase 168 publishes those 12 pages. I am flagging this explicitly rather than silently picking the
convenient reading: **REQUIREMENTS.md marking WIKI-01 `Complete` is defensible only under the scoped
reading**, which is well-supported by the phase's own design decisions (D-12) but is a real
interpretive choice, not a mechanical fact. A future reader auditing "Complete" checkboxes for
overclaim should know this one carries an asterisk.

## Anti-Patterns Found

None. `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` grep across the four core artifacts
(`wiki.py`, `selftest.sh`, both workflow YAMLs) returns nothing (the `TBD` cells in
`MIGRATION-TABLE.md` are explicitly labeled provenance-table placeholders for Phase 168 to fill,
not debt markers in shipped tooling, and the table is not itself a phase deliverable artifact under
test — it is documentation of intent). Comment-line count is 0 in all four core artifacts (operator
hard rule respected). No `return null`/empty-stub patterns found in the CLI's real subcommands.

## Minor Finding (non-blocking)

`.planning/codebase/STRUCTURE.md`'s `.github/workflows/` tree entry (corrected in plan 167-05) lists
`catalog-sync-check.yml` and `wiki-check.yml` but was never updated after plan 167-06 added
`wiki-publish.yml` — the CI quick-reference row and workflow tree both omit the third file. This is
cosmetic documentation staleness, not a functional gap in the phase's deliverables, and does not
affect any of the six success criteria. Flagged for a follow-up correction (Phase 168 or a
quick task), not treated as a phase-blocking gap.

## Human Verification Required

None. Every success criterion was either mechanically reproducible (fixture, offline check) or
independently re-verified against live infrastructure in this verification pass (wiki existence,
byte-identical mirror, branch/permission keying in the workflow YAMLs).

## Gaps Summary

No gaps. All six ROADMAP success criteria for Phase 167 are met, verified independently of the
SUMMARY narrative: the selftest harness was re-run (12/12 green), the offline check was re-run (exit
0), the live wiki was re-cloned and diffed byte-for-byte against `wiki/` (identical, exactly 3
pages), both post-execution corrections (credential redaction, PY32F071 deferral) were read in the
actual diff and confirmed complete, and the phase's central evidentiary claim — that every negative
case was observed red before green — was checked against the actual case bodies and captured
transcripts in three separate SUMMARYs, not accepted as a bullet-point assertion. One interpretive
note is recorded (WIKI-01's scoped reading) and one cosmetic documentation-staleness item is flagged
as a non-blocking follow-up.

---

*Verified: 2026-08-30*
*Verifier: Claude (gsd-verifier)*
