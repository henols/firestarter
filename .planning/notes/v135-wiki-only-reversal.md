# v1.35 — Operator reverses the in-repo wiki source model

**Date:** 2026-08-30
**Raised during:** `/gsd-discuss-phase 168` (session halted before `168-CONTEXT.md` was written)
**Status:** Decided by operator; ROADMAP.md and REQUIREMENTS.md repair APPLIED (WIKI-03/04 withdrawn, WIKI-02 rewritten and WIKI-05 reopened, both reassigned to Phase 168, which closed 2026-09-01)

## The decision

Documentation lives **only in the GitHub wiki**. There is no in-repo `wiki/` source tree
mirrored to a publishing target. Operator's words: *"I just want it in the wiki that's the
simplest and cleanest way."*

This reverses **milestone activation decision 5** (2026-08-30): *"wiki pages are sourced in
`firestarter_prom` and synced so they are versioned, reviewable and drift-checkable."*

The operator was shown the full cost below before deciding, and reaffirmed.

## What this voids

| Artifact | Disposition |
|---|---|
| **WIKI-02** — in-repo copy is the single source of truth | Void; must be reopened |
| **WIKI-03** — one-command idempotent publish | Void; no source to publish from |
| **WIKI-04** — drift check, demonstrated failing | Void; nothing to drift against |
| `wiki/Home.md`, `wiki/How-This-Wiki-Is-Published.md`, `wiki/_Sidebar.md` | Retire |
| `.github/workflows/wiki-publish.yml` | Retire |
| `tools/wiki/wiki.py` — `publish`, `sidebar`, `check` | Retire |
| `.github/workflows/wiki-check.yml` | Retire, or repoint at a wiki clone |

All of the above shipped in Phase 167 across 6 plans with 6/6 verification passing.

## What survives

- **WIKI-01** (wiki exists, Home indexes every page) and **WIKI-06** (both sub-repo wikis
  disabled, `has_wiki=false`) are unaffected.
- **WIKI-05** (every page reachable from Home or sidebar) survives as a property but becomes
  hand-maintained — the generated `_Sidebar.md` goes away.
- **`.planning/milestones/v1.35-MIGRATION-TABLE.md`** survives intact. It lives under `tools/`, not `wiki/`,
  and is still what makes Phase 168's move auditable (168 criterion 1) and still what the
  Backlog 999.9 repo-rename sweep greps for source paths.
- **`wiki.py links`** (orphan detection, link-form allowlist, filename legality) is the one
  part of the tooling that could be repointed at a cloned wiki rather than retired.

## Phase 168 remains coherent

MIGRATE-01…04 and LEGACY-06 are unaffected by the reversal. Two requirements need a new
mechanism, and both have a workable path:

- **HONEST-01** — criterion 4's "diff of claim-bearing statements between source and
  destination" still works: snapshot `doc/` **before** deletion, compare against the wiki
  afterward. The snapshot must be taken before the delete or the oracle is gone.
- **HONEST-02** — `firestarter_prom.wiki.git` **is a git repository**, so CI can clone it and
  run the claim check against real published pages. This is a first-party git clone, not the
  flaky external HTTP liveness probe that 167's D-11 rejected — materially different, and it
  keeps the relocated claim gates viable.

## Decisions locked earlier in the same session (still valid)

These were taken before the reversal and survive it, because they concern where the claim
gates live, not where the pages live:

- **Claim gates move to the meta repo.** The four app test modules that read `doc/*.md` as
  their oracle stop doing so; the assertion moves to where the wiki content and both
  submodules are reachable together.
- **Only the doc legs move.** 19 doc-reading sites relocate; the other ~19 code-side tests
  across those 1,962 lines stay in `firestarter_app/tests/` and keep running in app CI.
- **`test_dispatch_mirror.py` relocates and finally runs for real.** It has never executed in
  app CI (no firmware sibling in a bare `actions/checkout@v4`). In the meta repo all three
  legs exist. Meta CI gains `submodules: recursive`, and a previously-dormant gate may come
  back RED on first run — to be fixed in-phase.
- **Gates take the `tools/wiki/` standalone-checker shape** — a `python3` script with the
  same 0/1/2 exit contract as `wiki.py`, driven by `selftest.sh`, not a new pytest harness.
  The meta repo still has no test harness and this decision keeps it that way.

## Measured facts worth not re-deriving

- The 12 migrating files contain `support_status` 13× as a field name, but only
  `adapter-required` ×4 and `protocol-not-implemented` ×1 as values. **`vpp-exceeds-max` is
  0. `UNVERIFIED` / `PROTOCOL-LEDGER` is 0.** Two of the things HONEST-01 names are simply
  not in the corpus, so that half of the requirement is vacuous and must be stated as such
  rather than silently passed.
- `PROTOCOL-LEDGER.json` is a stale v1.16 planning artifact, last touched at Phase 99.
- **52 `doc/`-path reference lines across 27 files** (app 40 / fw 12) — including product
  source (`protection_readability.py`, `py32_dfu.py`, `include/proto_constants.h`) and two
  `CLAUDE.md` files that encode a lockstep-maintenance rule against `doc/SHIELD-REVISIONS.md` §4.
- Exactly three doc files are in the app sdist, confirmed at
  `firestarter.egg-info/SOURCES.txt:28-30`: `package-details.md`, `protocol-flags.md`,
  `protocol-id.md`.
- `firestarter_app` CI is a bare `actions/checkout@v4` on py3.11 with no sibling or parent
  repo, so the four `_FA_DIR / "doc"` gates run for real there today while
  `test_dispatch_mirror.py` already skips.

## Next steps

1. ~~Hand-edit `ROADMAP.md` and `REQUIREMENTS.md`.~~ **DONE 2026-08-30.** Applied by hand, not
   regenerated. `REQUIREMENTS.md`: WIKI-02 rewritten for wiki-only, WIKI-03 and WIKI-04
   **withdrawn** with their original text preserved struck-through, WIKI-05 reopened, HONEST-02
   given its clone-and-check mechanism, the operator-gated blocker marked resolved, and the
   traceability table updated (WIKI-02/05 reassigned to Phase 168). `ROADMAP.md`: activation
   decision 5 struck and re-costed, the milestone headline corrected, the "two distinct checks"
   paragraph rewritten to say only one survives, the overview table and coverage line updated to
   **30/30 active**, Phase 167's detail section banner-marked *superseded — do not plan from it*,
   and Phase 168's criteria 4 and 5 restated with criteria 7 and 8 added for WIKI-02/WIKI-05.
   `STATE.md`: frontmatter moved to phase 168 / status `planning`, and the conflation paragraph
   corrected.
2. ~~Decide the disposition of Phase 167's shipped tooling.~~ **DECIDED 2026-08-30.** Retire
   `wiki/`, `wiki-publish.yml`, and `wiki.py`'s `publish` / `sidebar` / `check`; keep
   `MIGRATION-TABLE.md` and `wiki.py links` (repointed at a wiki clone, to serve WIKI-05). The
   *execution* of that retirement is Phase 168's work — it is Phase 168 criterion 7, which
   deliberately requires retirement rather than dormancy: a retired-but-present publish path is a
   loaded gun aimed at the live wiki, since running it would overwrite pages from a stale source.
3. **Re-run `/gsd-discuss-phase 168`** against the re-scoped criteria. Three of the four original
   gray areas are still open and unanswered — the claim-diff unit, the two GSD-phase files, and
   the link-repair blast radius. The fourth (oracle relocation) is decided; carry its four
   decisions forward from this note rather than re-asking them.
