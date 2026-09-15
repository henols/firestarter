# Phase 193 disposition record

**Date:** 2026-09-14

This record answers the ROADMAP's four Phase 193 success criteria, one section each, every
claim naming the artefact, transcript, or file that supports it.

## Criterion 1

**Criterion text:** An instrument reports per-version download share for the `firestarter` PyPI
package, and the seed's trigger names a threshold and an observation window rather than "once
adoption has moved".

**Disposition: met.** The instrument is `tools/adoption/pypi_version_share.sh` — a committed,
argument-free, credential-free shell script querying the ClickHouse public PyPI download
dataset. Its live executed reading is recorded in
`evidence/193-gate-01-instrument-run.txt`, READING 1: `window: 2026-06-16 .. 2026-09-13`,
`fixed_downloads_ge_2_0_9: 17`, `at_risk_downloads_2_0_7: 116`, `fixed_share_pct: 12.8`,
`TRIGGER: NOT MET`.

`.planning/seeds/SEED-claim-firestarter-slug.md`'s `trigger_condition` frontmatter names the
threshold and window verbatim: fixed share of `(>= 2.0.9) / ((>= 2.0.9) + 2.0.7)` at or above
90%, AND `2.0.7` drawing 10 or fewer `pip` plus `uv` downloads, both measured over a rolling
90-day window on the stable channel, with a single reading from
`tools/adoption/pypi_version_share.sh` as the evidence. That is a threshold and an observation
window, not a vague "once adoption has moved" condition.

## Criterion 2

**Criterion text:** That instrument's record states what it cannot see: installed base is not
observable, download share is a proxy, and the residual — users who never upgrade — cannot be
driven to zero by any threshold.

**Disposition: met.** Every run of `tools/adoption/pypi_version_share.sh` prints the banner line
`WHAT THIS DOES NOT MEASURE` unconditionally, beneath the verdict, so the caveat travels with the
number on every invocation (`evidence/193-gate-01-instrument-run.txt`, READING 1). It states all
three limits this criterion requires:

- **Installed base is not observable.** "Installed base is not observable. Download share is a
  proxy for it, not a census of it."
- **Download share is a proxy.** Same line, second half.
- **The never-upgrade residual cannot be driven to zero.** "A user who installed 2.0.7 and never
  reinstalls generates zero downloads and is invisible to every instrument considered, including
  this one," and "This threshold therefore certifies that new acquisition of stranded versions
  has effectively stopped — a necessary condition, never a sufficient one."

The seed's "Why the trigger is what it is" section restates the same limit in its own words: the
pre-2.0.7 tail "sits outside the instrument's reach entirely," and "No threshold can separate a
stranded human down there from a scanner."

## Criterion 3

**Criterion text:** The no-Releases-on-the-meta-repo rule is recorded with its mechanism, not
just its instruction: a `v1.36` tag parses as PEP 440 `1.36`, so `3.0.0b29 >= 1.36` reads true and
`fw` reports firmware current forever. A reader must be able to see *why* the rule exists without
re-deriving it.

**Disposition: met.** `CLAUDE.md`'s `## Milestone close and branch protection` section carries the
rule as its fourth bullet: "The meta repository must never publish a GitHub Release — bare
milestone tags only." The same bullet reproduces the mechanism inline, so the disposition below is
readable standalone: a tag like `v1.36` parses as PEP 440 `1.36`, `Version("3.0.0b29") >=
Version("1.36")` then reads true, so `fw` reports firmware already up to date for every stranded
CLI, silently and permanently. This risk is latent today and armed by a single future action.

The mechanism is cited, not restated in full: the bullet points at
`.planning/notes/999.9-repo-rename-impact-analysis.md`, section heading **"Standing rule this
must produce"**, for the complete version-comparison walkthrough. There is one source of truth
for the walkthrough itself, and no second copy that can drift.

## Criterion 4

**Criterion text:** The `.gitmodules` history trap carries a workaround demonstrated for both an
existing clone and a fresh clone at a pre-rename ref.

**Disposition: met.** Both workarounds were executed, not merely reasoned about, against the
published `v1.35` tag — the concrete pre-rename ref a reader will actually hit, chosen because
its `.gitmodules` still declares the old firmware slug permanently (tags do not move), and
because it is reachable in a fresh `origin` clone, unlike the milestone-branch commit that
actually landed the URL repoint.

- **Existing clone (Workaround A):** `evidence/193-gate-03-existing-clone.txt`. READING 1
  captures the invisible-agreement state (both `.git/config`'s override and `.gitmodules` name
  `firestarter_fw`). READING 2 forces the divergence by checking out `v1.35` and shows the
  override surviving the checkout and being honoured by the subsequent `submodule update`, ending
  `EXISTING CLONE WORKAROUND OK`.
- **Fresh clone (Workaround B):** `evidence/193-gate-03-fresh-clone.txt`. READING 1 proves the
  override survives `git submodule init` and the child clones from `firestarter_fw` despite
  `v1.35`'s own `.gitmodules` naming the old slug, ending `FRESH CLONE WORKAROUND OK`. READING 2
  proves the trap does not bite today: a plain, no-override `submodule update --init` at the same
  ref still succeeds through the live slug redirect.
- **The hazard transcript:** `evidence/193-gate-03-submodule-sync-hazard.txt` records the third,
  supporting reading — `git submodule sync` run at a pre-rename ref silently clobbers both the
  `.git/config` override and the child's own `origin` remote back to the old slug, and the
  two-command repair for it. This is not a required third workaround. It documents why the
  operator-facing "Ordered procedure" step in `999.9-repo-rename-impact-analysis.md` (`git
  submodule sync --recursive`) would silently undo either workaround above if run at a pre-rename
  ref.

Both demonstrations and the hazard are written up as ordered, literal-command procedures in
`.planning/notes/gitmodules-archaeology-trap.md`, which `CLAUDE.md`'s repository-structure area
now points at directly, alongside the updated `tools/` inventory this phase's own
`tools/adoption/` addition made necessary.

## Honest limits

The instrument's integers move daily as new downloads land — the `17` / `116` / `12.8%` figures
above are a capture taken 2026-09-14, not a standing fact, and a reader meeting this file later
must re-run `tools/adoption/pypi_version_share.sh` rather than trust these numbers. Separately,
the post-claim failure shape this phase's mechanism describes — `git submodule update --init`
resolving the freed slug to the meta repository itself — remains unverified by construction: the
old slug still redirects today (D-1, D-7), so testing the failure would require performing the
destructive claim this milestone declines to perform. Nothing in this record, or in
`.planning/notes/gitmodules-archaeology-trap.md`, claims that failure has been observed.
