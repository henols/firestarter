# v1.35 — Phases 169 and 170 were executed ad hoc, outside the phase machinery

**Date:** 2026-09-01
**Raised during:** Phase 168 close, when the ROADMAP and REQUIREMENTS were found to disagree
**Status:** Reconciled — ROADMAP checkboxes and STATE.md corrected; this note is the evidence

## What happened

Both phases' content work was done as direct commits on
`gsd/v1.35-documentation-consolidation-wiki-migration` on 2026-08-31, without
`/gsd-plan-phase`, without plans or summaries, and without a verification pass. The
requirement marks in `REQUIREMENTS.md` were updated to match; the ROADMAP checkboxes were
not. That split is what surfaced the discrepancy.

Neither phase has a `phases/169-*/` or `phases/170-*/` directory, and neither ever will —
the work is done and re-running the machinery over finished content would produce
paperwork, not verification.

## The commits

| Phase | Repo | Commit | What it did |
|---|---|---|---|
| 169 | meta | `3d381098` | Added `README.md` (49 lines) and `.devcontainer/README.md` |
| 169 | meta | `3cb8a617` | Simplified the README to 37 lines; devcontainer guide reframed around using it |
| 169 | meta | `b206bc68` | Recorded FRONT outcomes in REQUIREMENTS.md |
| 170 | `firestarter_app` | `767079a` | Cut the README to app scope, fixed the table of contents |
| 170 | `firestarter` | `c26562a` | Cut the README to firmware scope |
| 170 | meta | `746db2c7` | Recorded REPO and LEGACY outcomes in REQUIREMENTS.md |

`99c7a8a9` (CLAUDE.md no longer claims an in-repo wiki source tree) is adjacent cleanup from
the same day, belonging to the model reversal rather than to either phase.

## What was checked at reconciliation, 2026-09-01

Verified against the live artifacts, not against the commit messages:

| Criterion | Result |
|---|---|
| 169-1 (FRONT-01) what Firestarter is, first screenful | PASS — states it in the first 10 lines, above any table or link list |
| 169-2 (FRONT-02) full path to a first chip read | **NOT MET, by operator decision** — see below |
| 169-3 (FRONT-03) links into the wiki, no duplication | PASS — Documentation section is a wiki link; no wiki content restated |
| 169-4 (FRONT-04) three repo descriptions set | PASS — `gh repo view` returns a distinct non-empty description for all three |
| 170-1 (REPO-01) firmware README is firmware-scoped | PASS — 151 → 91 lines; headings are boards/building/installing/protocol/reporting/docs/license; 4 links up to `firestarter_prom` |
| 170-2 (REPO-02) app README is app-scoped | PASS — 779 → 118 lines |
| 170-3 (REPO-03) readable in one sitting | PASS by judgement; no line-count criterion, per the operator's decision recorded in the ROADMAP |
| 170-4 (LEGACY-02) TOC matches sections | PASS — mechanically checked: 9 TOC entries, 0 unresolved anchors, 0 headings missing from the TOC. The advertised-but-absent `Id`/`Vpe`/`Hw` and the omitted `List`/`Search`/`VCC` are both gone as defects |
| 170-5 (LEGACY-03) no breaking-change wall above install | PASS — no breaking/upgrade/version-history text above `## Installation` in either README; both point at the wiki's Breaking-Changes page, which returns 200 and carries v1.10, v1.20 and v1.32 |
| 170-6 (REPO-04) PyPI long description surface | PASS — sdist built locally (`firestarter-3.0.0b33.tar.gz`, 220 files). Its `PKG-INFO` carries the trimmed 118-line README as the long description, `Description-Content-Type: text/markdown`, `Name: firestarter`, the MIT license classifier, a `pip install` command and the wiki link. Zero `doc/` path references and zero `doc/` files in the archive, which also re-confirms MIGRATE-03 |

Every external link in all three READMEs was fetched: 10 distinct URLs, all 200.

## FRONT-02 is deliberately not met

FRONT-02 (a complete path from nothing to a first chip read, carried by the README itself)
and FRONT-03 (everything past getting started is a link into the wiki, with no duplication)
cannot both hold. The operator chose the wiki `Home` page as the place that path lives, on
2026-08-31. FRONT-02 is struck through in `REQUIREMENTS.md` and recorded as
**Not met — superseded** in the coverage table, not silently dropped.

## What this costs, for Phase 173's honesty ledger

Both phases' requirement marks now rest on this note's checks rather than on a
`gsd-verifier` pass. Two consequences worth carrying into the close:

1. **No independent verification pass ran.** The checks above were made by the same agent
   that is recording them, in one sitting, after the fact. They are mechanical where
   mechanical was possible (anchors, HTTP status, line counts, `gh` output) and judgement
   elsewhere.
2. **Every criterion was met on its own terms**, including REPO-04, which was checked the
   way the criterion asks — against a locally built sdist's `PKG-INFO`, not against
   `pyproject.toml`'s intent. The only criterion not satisfied is FRONT-02, and that is a
   recorded decision rather than a gap.
