---
phase: 173-close-beta-cut-under-protection-close-procedure-honesty-ledg
verified: 2026-09-02T18:10:43Z
status: passed
score: 5/5 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 173: CLOSE — Beta Cut Under Protection, Close Procedure & Honesty Ledger Verification Report

**Phase Goal:** The protection this milestone added does not break the way this project actually
ships, and the milestone closes with its non-claims stated as plainly as its claims.
**Verified:** 2026-09-02T18:10:43Z
**Status:** passed
**Re-verification:** No — initial verification

This phase's deliverables are almost entirely outward-facing (GitHub rulesets, GitHub issues, a
GitHub wiki, GitHub releases, PyPI). Every truth below was checked against the live system —
`gh api`, a fresh independent wiki clone, a live PyPI JSON read, and live release/branch reads —
not against SUMMARY.md prose or evidence-file claims taken on faith. Where the phase's own
evidence file made a specific, falsifiable claim (an exit code, a SHA, a byte count, a comment
URL, a pinned-issue count), that exact claim was independently reproduced.

## Goal Achievement

### Observable Truths (the five ROADMAP success criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | All three `main` branches reject a direct push by ruleset, with server-side rejection text, and zero probe branches survive | ✓ VERIFIED | All three `evidence/173-03-probe-*.txt` transcripts carry GitHub's own receive-stage text `remote: error: GH013: Repository rule violations found for refs/heads/main.` / `Changes must be made through a pull request.` — not a client-side rejection and not `--dry-run`. Each probe branch was cut from a true fast-forward of a freshly fetched `origin/main` (`checkout -B ruleset-probe origin/main`). Live re-check: `gh api repos/<r>/branches` shows **zero** `ruleset-probe*` branches on any of the three remotes. Live re-check: all three rulesets (`22043478`/`4998759`/`22046179`) still read `enforcement: active`, `current_user_can_bypass: never`, identical bypass actor and conditions — matches `173-03-rulesets-before/after.json`. |
| 2 | Six provenance footers are live on the `firestarter_prom` wiki | ✓ VERIFIED | Cloned `firestarter_prom.wiki.git` independently (not the producing clone) and ran `python3 tools/wiki/provenance_footers.py --table .planning/v1.35/MIGRATION-TABLE.md --wiki-dir <fresh clone>` myself: `OK: 6 footers verified, 11 pages accounted for, 0 unrecorded.` exit 0. Manually confirmed exactly 6 of 11 `.md` pages carry a `*Relocated from ...*` trailer (`Install-Beta`, `Lockable-PROMs`, `Programming-Protocols`, `Shell-Completion`, `Shield-Revisions`, `Testing-Chips`). Also independently ran `wiki.py links` (11 pages, all reachable, all in `_Sidebar.md`) and `honest02_truth.py` (leg 1: 5/10 matched, 0 missing — matches the sweep's cited baseline exactly) — all green. |
| 3 | Four upstream comments posted; gh#6/gh#7 closed; gh#9 pinned; gh#5 open | ✓ VERIFIED | Live `gh api`: gh#5 `state: open, comments: 1`; gh#6 `state: closed, comments: 1`; gh#7 `state: closed, comments: 1`; gh#9 `state: open, comments: 1`. Live GraphQL `pinnedIssues`: `totalCount: 1`, issue 9. Fetched the four live comment bodies by their recorded comment ids and byte-diffed against `evidence/bodies/173-gh{5,6,7,9}.md` (after stripping jq's trailing-newline artifact) — **byte-identical** in all four cases; matches the sha256 hashes recorded in `evidence/173-07-operator-approval.txt`. Spot-checked content: gh#6 names both D-11 declines by name ("Required status checks" / "Required review-thread resolution"); gh#5 names FUT-W-01…04 as deferred; gh#7 states the generated-site premise was rejected 2026-07-27 and the Wiki was chosen; gh#9 states it stays open as the pinned orientation issue. |
| 4 | `henols/firestarter_prom#55` is OPEN and UNMERGED (correct, by operator decision) | ✓ VERIFIED | Live `gh pr view 55 --repo henols/firestarter_prom`: `state: OPEN, mergedAt: null, baseRefName: main`. `CLOSE-RECORD.md` §2, L6, L14, L15 and NON-CLAIM 1 in `evidence/173-09-closing-sweep.txt` all state the guard is code-plus-open-PR, not a live check, and that `gh run list --workflow 'Wiki check'` returns zero rows — reproduced live: zero rows. The footer-push-before-PR-open ordering constraint also holds: wiki footer commit `d7073f64c8` timestamps at `2026-09-02T14:40:17Z`, PR #55 opened `2026-09-02T15:10:13Z`. |
| 5 | The `beta` lockstep cut: firmware 3.0.0b25, app 3.0.0b36, PyPI carrying 3.0.0b36, meta `v1.35` peeling to `origin/beta` tip `6e84030b`, `main` untouched in all three repos | ✓ VERIFIED | Live `gh api .../releases`: firmware prerelease `3.0.0b25` (published `2026-09-02T17:21:41Z`); app prerelease `3.0.0b36` (published `2026-09-02T16:14:37Z`). Live PyPI JSON (`https://pypi.org/pypi/firestarter/json`): releases include `3.0.0b36`; `info.version` (stable channel) unchanged at `2.0.7`. `git ls-remote --tags origin v1.35` → `da49a737...` peeling to `6e84030bb526da7bde603b94c4d899c0b80adc30`, which equals `git ls-remote origin refs/heads/beta`'s current tip — confirmed live. Live `gh api .../git/ref/heads/main` for all three repos returns SHAs (`71148eda`, `135bf9a3`, `1625aef6`) that exactly match the pre-cut baseline recorded in `evidence/173-09-beta-cut.txt` §7 and the last-commit dates on all three (`2026-09-02T08:5[6-7]`) predate the cut's 14:22+ activity. PR merges `firestarter_prom#56`, `firestarter#59`, `firestarter_app#58` all confirmed `MERGED` against `beta` live. `beta-release.yml` confirmed live to call `publish.yml` via `workflow_call` (D-04's manual dispatch correctly recorded as dropped, per CLOSE-RECORD.md §4 correction 4). |

**Score:** 5/5 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `tools/wiki/provenance_footers.py` | Bidirectional footer guard, no comments, exit-code contract 0/1/2 | ✓ VERIFIED | 269 lines, exactly one line matching `^\s*#` (the shebang). Ran myself against a fresh clone: green (exit 0). Independently constructed a malicious table row (`../../../etc/passwd`) and confirmed `UNSAFE ROW` is reported and exit 1, never opened — the row-driven direction's path-containment guard is real, not asserted. |
| `.planning/v1.35/MIGRATION-TABLE.md` | Corrected table, 6 footer-eligible rows, `Protocol-Flags`/`Protocol-ID` retired, 3 new rows for `Breaking-Changes`/`Chip-Database-Fields`/`Pin-Maps` | ✓ VERIFIED | Main table has 11 rows (`Home`, 6 footer-eligible, `Contributing`, `Breaking-Changes`, `Chip-Database-Fields`, `Pin-Maps`); `Protocol-Flags`/`Protocol-ID` absent from the main table. Matches the checker's own `11 pages accounted for`. |
| `.github/workflows/wiki-check.yml` | Fourth `run:` leg, no comment, no widened permissions, no `--emit` | ✓ VERIFIED | Leg at line 129 matches the three-line shape of the other legs, no comment line inside the added block, `permissions: contents: read` unchanged, no new `uses:` line added, `--emit` never passed. |
| `.planning/config.json` | `git.base_branch: "beta"`, `git.protected_branches: ["main"]`, hand-edited, nested under `git` | ✓ VERIFIED | Confirmed nested correctly. `gsd_run query git.base-branch` → `beta`. `--is-protected beta` → `true`, `--is-protected main` → `true`, `--is-protected <milestone branch>` → `false` — reproduced live, matches the claimed distinguishing read-back exactly. |
| `.planning/notes/v135-close-procedure-under-protection.md` | Names the blocked route, `current_user_can_bypass: never`, all 7 consumer sites | ✓ VERIFIED | Present, states the route is blocked end to end, no comments, cites `prom#54`/`firestarter#58`/`firestarter_app#57` — all three independently confirmed MERGED to `main` on 2026-09-02 (`08:56:5[6-8]Z`–`08:57:0[2-6]Z`). |
| `CLAUDE.md` §"Milestone close and branch protection" | Auto-loaded pointer to the note | ✓ VERIFIED | Section present, states the blocked route and the `beta`-repoint fact directly, and points at the notes file. |
| `.planning/v1.35/CLOSE-RECORD.md` | Comprehensive ledger, ≥15 rows, 3 named minimums, 4 non-claims + 3 findings inherited, POLICY-04 non-claim, Phases 167–171 carryover including FRONT-02 | ✓ VERIFIED | 261 lines, 21 ledger rows (L1–L21), all three criterion-3 minimums present verbatim (L1 relocation-is-not-verification, L2 FUT-W deferred-not-delivered, L3 HONEST-02 point-in-time), FRONT-02 named as declined-not-met at L16, POLICY-04's probe-only non-claim recorded at L8 with §2's later correction noted rather than silently overwritten. |
| Backlog rows 999.46/999.47/999.48 | Exactly-once, unclobbered, correctly filed | ✓ VERIFIED | `/usr/bin/grep -n "### Phase 999.4[4-9]"` returns each of 999.44–999.48 exactly once, in order, with 999.44/999.45's bodies intact and unmangled. 999.46 (rulesets block stable release) and 999.47 (pre-existing `Catalog sync check` red) filed by plan 173-08; 999.48 (`tools/wiki/` absent from `main`) filed after 173-08 finished, per instructions and confirmed by 173-08's own SUMMARY (`modified: .planning/ROADMAP.md (orchestrator's write, commit 6d0eae0a — not this plan's own commits)`), matching the task's framing exactly. |
| `evidence/173-09-closing-sweep.txt` | Written before either requirement checkbox flipped, per-criterion verdicts | ✓ VERIFIED | Walks all 5 criteria in order with cited evidence, explicit VERDICT lines, a "REQUIREMENT MARKS THIS SWEEP AUTHORIZES" section naming only POLICY-04/POLICY-05. `REQUIREMENTS.md` marks both `[x]` with the exact evidence citation this sweep specifies. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `MIGRATION-TABLE.md` | wiki page trailing block | `provenance_footers.py`'s shared parser/footer-builder | ✓ WIRED | Reproduced myself: generator and checker agree; a hand-planted drifted footer is independently confirmed detected (`evidence/173-01-planted-failures.txt` shows 5 distinct failure words, all restoring to green — reproduced the `UNSAFE ROW` case myself with a synthetic malicious table). |
| `.planning/config.json` `git.base_branch` | 7 GSD consumer sites | `git-base-branch.cjs` tier-1 resolver | ✓ WIRED | `gsd_run query git.base-branch` reads `beta` live; `--is-protected` read-backs match the documented distinguishing pattern exactly (verified, not fell-closed). |
| `evidence/bodies/173-gh<n>.md` | posted GitHub comment | `gh issue comment --body-file` | ✓ WIRED | Live-fetched all 4 comment bodies and diffed byte-for-byte against the approved draft files — identical. |
| `wiki-check.yml`'s new leg | `main` | pull request #55 | ✓ WIRED (PR open, unmerged by design) | PR #55 confirmed live OPEN, base `main`, matching D-10/the operator's narrowed authorization. |
| merged PR to `beta` | prerelease pair | `beta-release.yml`/`beta-build.yml` → `publish.yml` (`workflow_call`) | ✓ WIRED | Live-confirmed `beta-release.yml` on `origin/beta` calls `publish.yml` via `workflow_call`; PyPI carries `3.0.0b36` with no corresponding manual `workflow_dispatch` run since 2026-08-02 (reproduced the `gh run list` claim's shape independently via the release/PyPI reads above). |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Provenance checker green on live wiki | `python3 tools/wiki/provenance_footers.py --table ... --wiki-dir <fresh clone>` | `OK: 6 footers verified, 11 pages accounted for, 0 unrecorded.` rc=0 | ✓ PASS |
| Provenance checker correctly rejects a path-escaping row | synthetic table row `../../../etc/passwd` against real 6-row baseline | `ERROR: UNSAFE ROW: ... resolves outside the wiki directory` rc=1 | ✓ PASS |
| `wiki.py links` green on live wiki | `python3 tools/wiki/wiki.py links --source-dir <fresh clone>` | `OK: 11 pages, all reachable...` rc=0 | ✓ PASS |
| `honest02_truth.py` matches cited baseline | `python3 tools/wiki/honest02_truth.py ...` | `leg1 stamp-present 5 matched/0 missing` — matches sweep's cited figure exactly | ✓ PASS |
| Ruleset rejection is server-side, not client-side | inspected all 3 probe transcripts for `remote:`-prefixed text | `GH013: Repository rule violations found` present in all 3 | ✓ PASS |
| No `ruleset-probe*` branches survive | `gh api repos/<r>/branches` on all 3 repos | 0 matches in all 3 | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plans | Description | Status | Evidence |
|-------------|-------------|--------------|--------|----------|
| POLICY-04 | 173-03, 173-04, 173-07, 173-08, 173-09 | `beta` lockstep cut demonstrated working under the new rulesets | ✓ SATISFIED | Marked complete on the probe alone per D-03 (criterion 1's own wording permits this), and the full cut was additionally performed and independently re-verified above — POLICY-04 holds on both the probe and the performed cut. |
| POLICY-05 | 173-01, 173-02, 173-05, 173-06, 173-08, 173-09 | GSD close procedure updated for PR-only `main` | ✓ SATISFIED | Config-first fix verified by distinguishing read-back; no admin bypass exists to document, and the note says so rather than inventing one — matches criterion 2's "PR flow or documented admin bypass" disjunction on its first branch. |

Both requirements are correctly claimed by all plans whose frontmatter lists them, and are flipped
to `[x]` only by plan 173-09's closing sweep, written before the flip — exactly the multi-plan
requirement pattern this project's own memory calls out as a known failure mode elsewhere, handled
correctly here.

No orphaned requirements: `REQUIREMENTS.md`'s Phase 173 mapping names only POLICY-04 and POLICY-05,
and no other requirement ID appears in any of the 9 plans' frontmatter.

### Anti-Patterns Found

None. Scanned every file this phase modified (`tools/wiki/provenance_footers.py`,
`.planning/v1.35/MIGRATION-TABLE.md`, `.github/workflows/wiki-check.yml`, `.planning/config.json`,
`.planning/notes/v135-close-procedure-under-protection.md`, `CLAUDE.md`,
`.planning/v1.35/CLOSE-RECORD.md`, `.planning/REQUIREMENTS.md`) with `/usr/bin/grep -nE
"TBD|FIXME|XXX|TODO|HACK|PLACEHOLDER"` — zero matches in all eight files. No debt markers, no
stub returns, no placeholder prose.

**Advisory only, not a phase gap — code review CR-01/CR-02 on `provenance_footers.py`.** The
`173-REVIEW.md` code review (advisory, does not block the phase) found that `load_pages()` — the
live-wiki-page enumeration used by the wiki→row accounting direction — has no path-containment
check and no error handling, so a symlink placed *inside* the wiki clone pointing outside it would
be silently followed and read, and an unreadable/broken file among the live pages would crash the
process. This is a real, demonstrated gap in the reviewer's transcript. It does **not** fail the
plan 173-01 must-have under verification ("a table row whose wiki-page cell resolves outside the
wiki directory is reported and exits 1 rather than being opened") — that must-have is about the
row→page direction, and I independently reproduced that guard working correctly with a synthetic
malicious table row (`UNSAFE ROW`, exit 1, never opened). The reviewer's finding is about the
un-guarded reverse direction (a live page that is itself an escaping symlink), which is a narrower,
lower-likelihood attack surface against a wiki this project's own account fully controls via
clone-commit-push with no external contributors. Recorded here for visibility; does not block this
phase's pass.

### Human Verification Required

None. All five ROADMAP success criteria and every plan-level must-have inspected in this
verification were checked against live, independently-reproduced evidence (GitHub API, PyPI JSON,
a fresh wiki clone, live release reads) rather than taken from SUMMARY.md or evidence-file prose.

### Gaps Summary

No gaps. Every one of the five ROADMAP success criteria is independently confirmed true against
the live system as of this verification's timestamp, not merely claimed by the phase's own
evidence files:

1. The ruleset rejection probe's server-side evidence, zero surviving probe branches, and
   unchanged rulesets were all re-derived from GitHub directly.
2. The six wiki footers and the checker that guards them were re-run against an independently
   taken fresh clone, with the checker's exit-0/exit-1 boundary behavior (including the
   path-containment guard) exercised directly rather than assumed from its source.
3. The honesty ledger is comprehensive (21 rows, exceeding the 15-row floor), names all three
   required minimums verbatim, and records its own discrepancies (§1's four, §4's seven
   corrections) rather than silently absorbing them.
4. All three new backlog rows (999.46/47/48) exist exactly once, correctly filed, with 999.48's
   post-hoc filing by the orchestrator matching the task's own framing of that fact.
5. All four upstream replies were independently re-fetched from GitHub and are byte-identical to
   the operator-approved drafts; gh#6/gh#7 are closed, gh#5/gh#9 are open, and gh#9 is pinned
   (`pinnedIssues.totalCount: 1`) — a fact I confirmed via a live GraphQL call, not by reading the
   phase's own claim about it.

The beta lockstep cut (an additional, non-required-by-D-03 deliverable) was also independently
re-verified: both prerelease tags exist on their release APIs, PyPI carries the app prerelease
with the stable channel unchanged, the meta tag peels to `origin/beta`'s live tip, and all three
`main` branches are unchanged from their pre-cut SHAs.

The one advisory item (code-review CR-01/CR-02 on the un-guarded reverse direction of
`provenance_footers.py`'s live-page enumeration) is real but out of scope for this must-have and
does not block the phase, per the task's own instruction that code review is advisory input to
judgement rather than a gate.

---

_Verified: 2026-09-02T18:10:43Z_
_Verifier: Claude (gsd-verifier)_
