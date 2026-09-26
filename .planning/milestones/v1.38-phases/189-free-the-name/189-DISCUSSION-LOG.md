# Phase 189: Free the Name - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-13
**Phase:** 189-Free the Name
**Areas discussed:** Submodule change scope, Proving the fresh clone, Meta main's `.gitmodules`, 189 vs 192 boundary

**Area selection:** all four offered areas were selected.

---

## Submodule change scope

### Q1 — What exactly changes inside `.gitmodules`?

| Option | Description | Selected |
|--------|-------------|----------|
| URL only | Section stays `[submodule "firestarter"]`, path stays `firestarter/`, only the url changes. Keeps GATE-03's `git config submodule.firestarter.url` workaround valid; leaves `.planning/` path citations and `meta_presence.py`'s parent arithmetic intact. | ✓ |
| URL + section name | Rename the section, keep the path. Breaks GATE-03's workaround string, needs `.git/modules/` surgery, gains nothing observable. | |
| URL + section + path | Full rename; working-tree dir becomes `firestarter_fw/`. Blast radius far beyond the phase. | |

**User's choice:** URL only
**Notes:** Recommended option. Confirmed by external mechanics: `git submodule set-url` rewrites `.gitmodules` alone and touches neither `path` nor the section name, so the supported command path and the chosen scope coincide.

### Q2 — Change the SSH transport while in the file?

| Option | Description | Selected |
|--------|-------------|----------|
| Keep SSH | Change only the slug. Smallest diff; the clone demo runs as the operator, who has keys. | ✓ |
| Switch to HTTPS | A fresh clone would then work for anyone — fits the findable-front-door motive, but changes operator push ergonomics and rides a second change into the same file. | |
| Switch to relative URLs | `../firestarter_fw.git` inherits the parent's transport. Cleanest technically, but a behavioural change to submodule resolution, and it breaks if the meta repo moves org. | |

**User's choice:** Keep SSH
**Notes:** Recorded in CONTEXT.md as a deferred idea rather than a closed door — worth revisiting if the front door starts attracting outside clones.

---

## Proving the fresh clone

Framing established before the questions: the milestone branch is local-only (GSD pushes at ship; D-7 gates every push), and the meta gitlinks currently sit on the **pushed** beta tips `10ec1b0e` / `f926e362` set by `05bd22a5`. A per-phase gitlink advance carrying the README fix would retarget the gitlink at an unpushed commit.

### Q1 — Where does the RENAME-03 demonstration clone from?

| Option | Description | Selected |
|--------|-------------|----------|
| `file://` meta + real remotes | `git clone file:///workspaces --branch v1.38-repository-rename --recurse-submodules`. Meta from the local tip; submodules resolve against the real `henols/firestarter_fw` over SSH. Needs no push. | ✓ |
| Operator pushes first, clone from GitHub | Most literal reading of "fresh clone at the milestone tip", but needs a mid-milestone push of all three branches against standing policy and D-7. | |
| Fully local clone | Overrides both submodule URLs to local paths. Proves clone plumbing but not that `firestarter_fw` resolves — the entire point of the criterion. | |

**User's choice:** `file://` meta + real remotes

### Q2 — How is the unpushed-gitlink trap handled?

| Option | Description | Selected |
|--------|-------------|----------|
| Demo against pushed gitlinks, advance after | Capture the evidence while the gitlinks still point at fetchable beta tips, then advance the fw gitlink as the normal per-phase step. | ✓ |
| Advance gitlink first, accept a local-only submodule fetch | Demonstrates the milestone tip exactly, but the submodule leg stops proving the renamed remote resolves. | |
| Don't advance the fw gitlink in 189 | Simplest, but breaks the per-phase gitlink convention followed since v1.36. | |

**User's choice:** Demo against pushed gitlinks, advance after
**Notes:** Rated `costly` in CONTEXT.md (D-05) — the ordering is what makes the evidence non-vacuous, so reversing it would require regenerating the evidence from a re-wound gitlink.

### Q3 — Reusable script or one-off evidence?

| Option | Description | Selected |
|--------|-------------|----------|
| Reusable script in the phase dir | Clones into a temp dir, asserts both submodules initialised, prints resolved URLs. Phase 193's GATE-03 can extend it. | ✓ |
| One-off transcript in `evidence/` | Lighter, matches how most infrastructure criteria close here, but Phase 193 starts from nothing. | |
| Promote to a repo-level tool | Outlives the milestone, but broader than the phase asks; `tools/` currently holds `catalog/` alone. | |

**User's choice:** Reusable script in the phase dir

---

## Meta main's `.gitmodules`

Framing established before the questions: meta `main` is the GitHub **default branch** (verified via API), so it is the `.gitmodules` handed out by the front door's Clone button — and the ROADMAP's v1.38 branch-model paragraph names only `firestarter_app`'s main as the deliberate exception, omitting meta main, which RENAME-02 requires.

### Q1 — Where does the meta repo's main-branch `.gitmodules` change land?

| Option | Description | Selected |
|--------|-------------|----------|
| Its own PR in Phase 189 | One-line branch off `origin/main`, PR'd and merged. RENAME-02 scopes it here; 189 runs first; main is the default branch. | ✓ |
| Batch with Phase 191's app-main PR | Fewer operator gates, but makes RENAME-02 depend on Phase 191, contradicting the roadmap's stated phase-independence invariant. | |
| Defer meta main to milestone close | Fewest interruptions, but 189 then cannot close RENAME-02, and the close tail is the weakest-verified part of the process. | |

**User's choice:** Its own PR in Phase 189
**Notes:** Rated `costly` in CONTEXT.md (D-07) — undoing a merge to a protected default branch needs a second PR, and clones taken in the interval already carry it.

### Q2 — What does 189 assert for criterion 2's `beta` half?

| Option | Description | Selected |
|--------|-------------|----------|
| Milestone branch + merged main PR; beta declared close-carried | Verifies on its own branch and on main, records the beta half as landing at milestone merge. Prevents a verifier misreading it as incomplete. | ✓ |
| Assert only the milestone branch; main and beta both close-carried | Narrowest reading; leaves the default branch stale all milestone and only pairs with deferring the main PR. | |
| Require the beta merge before 189 verifies | Literal satisfaction, but merging to beta mid-milestone fires a pre-release cut in both sub-repos and publishes to PyPI. Not acceptable under D-7. | |

**User's choice:** Milestone branch + merged main PR; beta declared close-carried

---

## 189 vs 192 boundary

Framing established before the questions: the firmware repo has exactly **two** live tracked bare-slug references — `README.md:47` (the Releases link, literally criterion 4's "release links") and `tests/meta_presence.py:22`, a module docstring. Everything else in that README addresses `firestarter_prom` and must stay under D-1.

### Q1 — Who owns the firmware repository's slug references?

| Option | Description | Selected |
|--------|-------------|----------|
| 189 owns the whole fw repo | Fixes both refs and claims "the firmware repo is clean", checkable with one grep. 192 sweeps meta + app and re-verifies fw. | ✓ |
| 189 does README only; 192 sweeps the rest | Literal split of criterion 4 vs SWEEP-01, but the docstring is named by neither by path and can fall through both. | |
| 192 owns all three repos; 189 does none | Cleanest single-owner sweep, but empties criterion 4 and leaves the renaming phase advertising the old Releases URL. | |

**User's choice:** 189 owns the whole fw repo

### Q2 — Regression guard in 189?

| Option | Description | Selected |
|--------|-------------|----------|
| No guard in 189 — leave it to 192 | Prove cleanliness with a grep at verification time; a standing repo-wide check belongs to SWEEP-01/02. | ✓ |
| Add a pytest guard in the firmware repo now | Durable, but firmware CI is `native` + `native_nodevtools` + `pytest tests/` only, and source-scanning gates here have a history of failing **open** after renames. | |
| Guard in the meta repo covering all three | Broadest coverage, but squarely SWEEP territory and pre-empts Phase 192's design. | |

**User's choice:** No guard in 189 — leave it to 192

---

## Claude's Discretion

Decided without asking, as mechanical calls settled by precedent — recorded in CONTEXT.md as D-12 and D-03:

- **RENAME-01 verification anchors on both `.id` and `.full_name`** from `gh api repos/henols/firestarter`. The numeric id (`810276812`) is rename-stable and is what makes "if it ever resolves to a *different* repository, D-1 has been violated" checkable; the name alone cannot distinguish a live redirect from a re-occupied slug.
- **The D-03 observable for RENAME-02** is the superproject's `.git/config` *and* the submodule's own `remote.origin.url` after `git submodule sync --recursive` — not the `.gitmodules` file alone.

Left open for the planner and executor:

- Shape, name and temp-dir strategy of the RENAME-03 script.
- Where the evidence transcript lands under the phase directory.
- Wording of the repointed Releases link beyond the slug.
- Commit granularity across the firmware, meta-milestone-branch and meta-`main` legs.

## Deferred Ideas

- **HTTPS or relative submodule URLs** — declined here (Q2 of area 1); revisit if the front door starts attracting outside clones.
- **`firestarter/tests/meta_presence.py`'s GSD-provenance docstring** (`Requirements: PCB-01…`, `Decisions covered: D-03, D-04`) — exactly what the `CLAUDE.md` hard rule targets, already tracked as todo `2026-08-27-strip-gsd-provenance-comments-from-source.md`. This phase changes the slug inside it and nothing else.
- **The ROADMAP's v1.38 branch-model paragraph omits meta `main`** from its protected-branch exceptions while RENAME-02 requires a write there. D-07 resolves it for this phase; the text could be corrected at milestone close.

## Todos Reviewed, Not Folded

`todo.match-phase 189` returned three matches, all scoring 0.9 on the keyword `firestarter` alone. None concern a repository rename:

- *Skip VPP error/warning checks when VPP is unused (reads/blank-checks)* — firmware behaviour; v1.38 changes no firmware source.
- *Drive outputs/pins to a safe state ASAP on power-up and on ANY fault* — firmware behaviour; same reason.
- *Strip residual GSD provenance comments from product source* — adjacent, but a repo-wide hygiene sweep; folding it would widen a three-requirement infrastructure phase.
