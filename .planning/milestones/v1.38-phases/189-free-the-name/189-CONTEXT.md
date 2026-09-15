# Phase 189: Free the Name - Context

**Gathered:** 2026-09-13
**Status:** Ready for planning

<domain>
## Phase Boundary

`henols/firestarter_fw` is the firmware repository, `henols/firestarter` is left vacant and still
redirecting, and the meta repository's submodule resolves the new URL directly rather than through
GitHub's rename redirect. Covers **RENAME-01, RENAME-02, RENAME-03**.

The phase runs **first** in v1.38 — nothing can point at a repository that does not exist yet.

**In scope:** the operator-performed GitHub rename and its verification; the `.gitmodules` URL change on
the milestone branch and on meta `main`; `git submodule sync --recursive`; a demonstrated fresh clone that
initialises both submodules; and the firmware repository's own slug references.

**Out of scope (settled at activation, not re-litigated here):** claiming `henols/firestarter` (D-1);
mirroring firmware releases onto the meta repo (D-2); the `firestarter_app` constants on either branch
(Phases 190/191); the archived `.planning/milestones/` references (D-5); solving the `.gitmodules` history
trap (D-6 — documented in Phase 193, not solved); the meta and app repositories' own reference sweep
(Phase 192).

</domain>

<decisions>
## Implementation Decisions

### Submodule change scope

- **D-01:** `.gitmodules` changes the **URL only**. The section stays `[submodule "firestarter"]` and the
  path stays `firestarter/`. RENAME-02's wording ("`.gitmodules` names `firestarter_fw`") is satisfied by
  the URL alone. Renaming the section would invalidate GATE-03's documented
  `git config submodule.firestarter.url` workaround and require surgery on `.git/modules/firestarter`;
  renaming the path would break `CLAUDE.md`, both sub-repo `CLAUDE.md` files, every `.planning/` path
  citation, `firestarter/tests/meta_presence.py`'s parent-directory arithmetic, and the devcontainer layout
  assumptions. Nothing in RENAME-01/02/03 asks for either.
- **D-02:** The **SSH transport is retained** — `git@github.com:henols/firestarter_fw.git`. Only the slug
  changes. Switching to HTTPS or to relative URLs was considered and declined: neither is required by any
  requirement, and this milestone is deliberately infrastructure-minimal.
- **D-03:** Mechanism is `git submodule set-url firestarter git@github.com:henols/firestarter_fw.git`
  followed by `git submodule sync --recursive`. `set-url` rewrites `.gitmodules` only; `sync` is what
  propagates the new URL into the superproject's `.git/config` and into the submodule's own
  `remote.origin.url`. **Both of those are the observable** for RENAME-02's "an existing clone resolves the
  new URL without relying on the redirect" — verify them, not just the file.

### Proving RENAME-03

- **D-04:** The demonstration clones **from the local meta repo over `file://`, with the submodules
  resolving against the real GitHub remotes**:
  `git clone file:///workspaces --branch v1.38-repository-rename --recurse-submodules <scratch-dir>`.
  The meta repo comes from the local milestone tip; the submodule leg hits
  `git@github.com:henols/firestarter_fw.git` for real, which is exactly the claim being made. This needs no
  push, so it does not violate D-7 or the standing GSD-pushes-at-ship-time rule.
- **D-05:** The demonstration runs **while the gitlinks still point at the pushed `beta` tips**, and the
  firmware gitlink is advanced to carry the README commit **afterwards**. Rationale: this phase commits
  inside the firmware submodule, and the per-phase gitlink advance (the norm since v1.36) would otherwise
  retarget the gitlink at an **unpushed** commit, making `submodule update --init` fail on any fresh clone.
  Proving the criterion against a commit a third party could actually fetch is the point; the gitlink
  advance afterwards is ordinary unpushed phase work like any other.
  — **Reversibility:** costly — the ordering is what makes the evidence non-vacuous. Advancing first and
  then demonstrating produces a transcript that proves the clone plumbing but not that `firestarter_fw`
  resolves, and the evidence would have to be regenerated from a re-wound gitlink to recover the claim.
- **D-06:** The demonstration is a **reusable script committed under the phase directory**, not a one-off
  transcript. It clones into a temp dir, asserts both submodules initialised, and prints the resolved URLs.
  Phase 193's GATE-03 must demonstrate the history-trap workaround for **two** clone cases and can extend
  this rather than reinvent it; a post-claim milestone can re-run it.

### Branch routing

- **D-07:** The meta repository's `main`-branch `.gitmodules` change lands as **its own pull request inside
  Phase 189** — a one-line branch off `origin/main`. RENAME-02 scopes it to this phase, 189 runs first, and
  meta `main` is the **GitHub default branch**, so it is the copy of the stale URL handed out by the front
  door's Clone button. Keeping it independent of Phase 191's `firestarter_app` main work preserves the
  roadmap's stated invariant that every phase depends on 189 and on nothing else of each other.
  — **Reversibility:** costly — undoing a merge to a protected default branch needs a second pull request
  through the same protection, and any clone taken in the interval already carries the change.
- **D-08:** Criterion 2's "on both `beta` and `main`" is asserted as **the milestone branch plus the merged
  `main` PR**, with the `beta` half explicitly recorded as **close-carried** — it lands when the milestone
  merges, the standard route for every change in this project. This is stated so a verifier does not read
  "`beta` does not have it yet" as an incomplete requirement mid-milestone. Merging to `beta` early is not
  an option: it fires a pre-release cut in both sub-repositories and publishes the host one to PyPI (D-7).
- **Note for the planner — a gap in the activation text, not a decision:** the ROADMAP's v1.38 branch-model
  paragraph names only `firestarter_app`'s `main` as the deliberate protected-branch exception. It omits
  meta `main`, which RENAME-02 requires. D-07 is the resolution; the roadmap paragraph is simply silent on
  it.

### Phase 189 / Phase 192 boundary

- **D-09:** **Phase 189 owns the firmware repository's slug references outright** — both of them. Phase 192
  sweeps the meta and app repositories and re-verifies the firmware repository as already-clean. This
  removes the overlap between criterion 4 ("the firmware repository's own README and release links") and
  SWEEP-01 ("both sub-repo READMEs"), under which
  `firestarter/tests/meta_presence.py:22` — named by neither criterion by path — could fall through both.
  189 is already committing inside that repository for the gitlink advance, so this costs nothing.
- **D-10:** **No regression guard is added in Phase 189.** Cleanliness is proved with a grep at verification
  time. A standing repo-wide check belongs to SWEEP-01/02 in Phase 192, which has to build a pattern that
  distinguishes the bare `firestarter` slug from `firestarter_fw` / `firestarter_app` / `firestarter_prom`
  regardless. A source-scanning gate inside the firmware repository was declined specifically: firmware CI
  is `native` + `native_nodevtools` + `pytest tests/` only, and source-scanning gates in this project have a
  history of failing **open** after renames.

### Sequencing and gates

- **D-11:** The GitHub rename itself is **operator-performed** (D-7). No plan may script it. Every criterion
  other than RENAME-01's rename act is agent-executable once the rename has landed, so plans must be
  written to **halt at the rename and resume after it**, not to assume it.
  — **Reversibility:** costly — renaming back is possible only while `henols/firestarter` stays vacant
  (which D-1 guarantees for this milestone), but the rename is immediately visible to 27 stargazers, 11
  forks and every existing clone's remote.
- **D-12:** RENAME-01's verification asserts on **both `.id` and `.full_name`** from
  `gh api repos/henols/firestarter`. The numeric id is the rename-stable identity anchor and is what makes
  the criterion's "if it ever resolves to a *different* repository, D-1 has been violated" checkable;
  `.full_name` is what proves the rename happened. Asserting on the name alone cannot distinguish a live
  redirect from a re-occupied slug.

### Claude's Discretion

- The exact shape and location of the RENAME-03 script (name, argument handling, temp-dir strategy), so
  long as it satisfies D-06.
- How the evidence transcript is captured and where under the phase directory it lands.
- The wording of the firmware README's repointed Releases link, beyond changing the slug.
- Commit granularity across the firmware, meta-milestone-branch and meta-`main` legs.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone scope and the decisions that bound this phase
- `.planning/REQUIREMENTS.md` — RENAME-01/02/03 verbatim, the D-1…D-7 activation decisions table, and the
  Out of Scope table. **The D-1…D-7 decisions are settled; no plan re-opens them.**
- `.planning/ROADMAP.md` § "Phase 189: Free the Name" (≈ lines 272–296) — goal, the four success criteria,
  and the operator-gated note. § v1.38 milestone header (≈ lines 190–262) — the ordering constraint, the
  branch model, and the "no bench" statement.
- `.planning/PROJECT.md` § "Current Milestone: v1.38 Repository Rename" (lines 41–112) — the five strands,
  the measured discovery-failure table, and the full D-1…D-7 rationale.

### The rename's measured impact — read before planning anything that touches a URL
- `.planning/notes/999.9-repo-rename-impact-analysis.md` — the whole note. §"The `.gitmodules` archaeology
  trap" (lines 94–100) is what D-01's section-name decision protects, and §"Ordered procedure" step 2
  (line 107) is this phase's mandate. §"Blast radius" establishes that only the `fw` command is at risk.

### The deferred destructive half — this phase must not advance it
- `.planning/seeds/SEED-claim-firestarter-slug.md` — the dormant seed. Its "Do not fire this while any of
  these is untrue" list names `.gitmodules` + `submodule sync` as a precondition this phase satisfies.
- `.planning/research/questions.md` — the open adoption-threshold question; Phase 193's subject, not this
  phase's.

### Branch protection and close mechanics — needed for D-07's `main` PR
- `.planning/notes/v135-close-procedure-under-protection.md` — how this project lands changes on protected
  branches, and the blocked stable-release route.
- `CLAUDE.md` § "Milestone close and branch protection" — `main` is protected in all three repositories
  (PR required, `current_user_can_bypass: never`); this project's close targets `beta`.

### Standing repository rules
- `CLAUDE.md` § "Source code comments — hard rule" — **no comments in product source, not overridable by a
  plan.** Relevant because this phase edits `firestarter/tests/meta_presence.py`: change the slug in the
  existing docstring, add nothing.

</canonical_refs>

<code_context>
## Existing Code Insights

### Measured facts — do not re-measure, cite these

Captured 2026-09-13 against the live GitHub API and the three working trees.

**GitHub repository identities** (`gh api repos/henols/<repo>`):

| repo | id | full_name | default_branch |
|---|---|---|---|
| firmware | `810276812` | `henols/firestarter` | `main` |
| host CLI | `810694376` | `henols/firestarter_app` | `main` |
| meta | `1232995399` | `henols/firestarter_prom` | `main` |

The firmware id `810276812` is the anchor for D-12. Meta's `default_branch` being `main` is why D-07
matters.

**`.gitmodules` is byte-identical on `beta` and on `main`** — two sections, absolute SSH URLs:

```
[submodule "firestarter"]      path = firestarter       url = git@github.com:henols/firestarter.git
[submodule "firestarter_app"]  path = firestarter_app   url = git@github.com:henols/firestarter_app.git
```

**Local clone state** — the superproject's `.git/config` carries `submodule.firestarter.url` and
`submodule.firestarter.active`, and `firestarter/`'s own `remote.origin.url` is still
`git@github.com:henols/firestarter.git`. Both must change under D-03's `sync --recursive`.

**Gitlinks at the v1.38 fork**, set by `05bd22a5` onto the pushed `beta` tips — these are what D-05's
demonstration relies on being fetchable:

- `firestarter` → `10ec1b0e24d98f04c3b4aa076b9d84231ac5da04`
- `firestarter_app` → `f926e36262c368633b50245a225478ef36aed885`

**The firmware repository has exactly two live tracked references to the bare slug**
(`git grep -InE 'henols/firestarter([^_a-zA-Z0-9]|$)'`):

- `firestarter/README.md:47` — `[Releases](https://github.com/henols/firestarter/releases)`. This is
  literally criterion 4's "release links".
- `firestarter/tests/meta_presence.py:22` — a module docstring describing an `actions/checkout` of
  `henols/firestarter` in isolation.

**Do not touch** `firestarter/README.md` lines 7, 75, 80 and 81 — they address `henols/firestarter_prom`,
which keeps its name under D-1. Line 1 addresses `henols/firestarter_app`, also unchanged.

### Established patterns this phase inherits

- **Executors commit inside the submodule**, on the milestone branch, and the meta repo re-pins the
  gitlink. All three repositories are already on `v1.38-repository-rename`.
- **The gitlink is advanced per phase** (the norm since v1.36; Phase 180 advanced it three times by name).
  D-05 keeps that norm but fixes its ordering relative to the clone demonstration.
- **Pushes happen at ship time, never ad hoc** — and D-7 makes every outward-facing step operator-gated.
  D-04 is chosen specifically so RENAME-03 needs no push.
- **Evidence lives under the phase directory** and is expected to be re-runnable where it reasonably can be
  (D-06).

### Integration points

- `.gitmodules` (meta, milestone branch) — D-01/D-02/D-03.
- `.gitmodules` (meta, `main`, via PR) — D-07.
- `firestarter/README.md:47` and `firestarter/tests/meta_presence.py:22` — D-09.
- The superproject `.git/config` and `firestarter/`'s `remote.origin.url` — the D-03 observable.
- The phase directory — D-06's script and its evidence.

### Explicitly NOT integration points for this phase

- `firestarter_app/firestarter/constants.py` — the three `FIRESTARTER_*_URL` constants belong to Phases
  190 (`beta`) and 191 (`main`).
- `firestarter_app/firestarter/submit.py` — `SUBMIT_REPO` targets `firestarter_prom`, whose redirect is
  permanent. It is correct as written and must not be changed here.
- Any `.github/workflows/` file in any repository — no workflow hardcodes a repo slug, and the meta
  repository has no `.github/workflows/` at all. 999.9's "CI/release workflows" clause is a **no-op**.
- Anything under `.planning/milestones/` — D-5, and Phase 192 must prove a diff over that path is empty.

</code_context>

<specifics>
## Specific Ideas

- The clone demonstration must **print the resolved submodule URLs**, not merely exit 0. An exit code
  cannot distinguish "resolved `firestarter_fw` directly" from "followed a redirect", and distinguishing
  those is the whole content of RENAME-02.
- The RENAME-01 evidence should capture the redirect **still being live** — the old slug resolving to the
  new repository — because that, not the rename alone, is what proves D-1 has been honoured.

</specifics>

<deferred>
## Deferred Ideas

- **Switching `.gitmodules` to HTTPS or relative URLs** so a fresh clone succeeds without SSH keys on the
  account. It fits v1.38's findable-front-door motive, but it is a transport change no requirement asks
  for, and relative URLs additionally break if the repositories ever move organisation. Considered and
  declined in discussion (D-02); worth its own decision if the front door ever attracts outside clones.
- **`firestarter/tests/meta_presence.py`'s module docstring carries GSD provenance** — `Requirements:
  PCB-01, PCB-02, …`, `Decisions covered: D-03, D-04`. That is exactly what `CLAUDE.md`'s hard rule
  targets, and it is already tracked as todo
  `2026-08-27-strip-gsd-provenance-comments-from-source.md`. **This phase changes the slug inside that
  docstring and nothing else** — stripping the provenance is that todo's job, not this phase's.
- **The ROADMAP's v1.38 branch-model paragraph omits meta `main`** from its list of protected-branch
  exceptions, while RENAME-02 requires a write there. D-07 resolves it for this phase; the roadmap text
  could be corrected at milestone close.

### Reviewed Todos (not folded)

`todo.match-phase 189` returned three matches, all scoring 0.9 on the keyword `firestarter` alone. None
touch a repository rename; all three are deferred, not folded:

- *Skip VPP error/warning checks when VPP is unused (reads/blank-checks)* — firmware behaviour; v1.38 is
  infrastructure-only and changes no firmware source.
- *Drive outputs/pins to a safe state ASAP on power-up and on ANY fault* — firmware behaviour; same reason.
- *Strip residual GSD provenance comments from product source* — genuinely adjacent (this phase edits a
  file carrying such a docstring), but it is a repo-wide hygiene sweep and folding it would widen a
  three-requirement infrastructure phase into a source-hygiene one. See the Deferred Ideas entry above.

</deferred>

---

*Phase: 189-Free the Name*
*Context gathered: 2026-09-13*
