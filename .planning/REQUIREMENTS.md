# Requirements: Firestarter — v1.38 Repository Rename

**Defined:** 2026-09-13
**Milestone:** v1.38 — "Free the name, don't claim it yet"
**Core Value (this milestone):** The project gets a findable front door and a firmware repository that does
not own the unqualified name, and no already-installed copy of the CLI stops being able to update its
firmware as a result.

**Scope:** All three repositories, but asymmetrically. `firestarter` is renamed. `firestarter_app` changes
three constants on two branches and ships a stable. The meta repository changes `.gitmodules`, its README
and five `.planning/codebase/` documents, and gains one standing rule. No firmware source, no protocol, no
dual-repo behavioural lockstep.

**What this milestone deliberately leaves undone:** claiming `henols/firestarter` for the meta repository.
That is the one destructive act in Backlog 999.9 — it deletes the firmware repository's redirect — and it is
deferred to [`seeds/SEED-claim-firestarter-slug.md`](seeds/SEED-claim-firestarter-slug.md) behind an adoption
trigger. Everything here is safe to ship without it.

---

## Decisions taken at activation (operator, 2026-09-13)

Settled here so no phase re-litigates them. Full text and rationale in `PROJECT.md` § Current Milestone.

| ID | Decision |
|---|---|
| **D-1** | **v1.38 stops before the claim.** The milestone may close with the front door still named `firestarter_prom`. |
| **D-2** | **Firmware releases stay in the firmware repository** — no mirroring onto the meta repo, not even for a bounded window. This rules out the only continuity mechanism, and therefore implies D-1. |
| **D-3** | **`main` and `beta` are separate changes**, and `main` is the one that reaches users: `pip install firestarter` resolves to **2.0.7**. |
| **D-4** | **The meta repository must never publish a GitHub Release.** Bare milestone tags only. |
| **D-5** | **The 672 archived references under `.planning/milestones/` are not swept** — historical-by-intent. |
| **D-6** | **The `.gitmodules` history trap is documented, not solved** — history cannot be fixed. |
| **D-7** | **Every outward-facing step stays operator-gated** — the GitHub rename, the stable cut, every push. |

---

## v1 Requirements

### RENAME — free the name

- [x] **RENAME-01**: The firmware repository is named `henols/firestarter_fw` on GitHub, and
      `henols/firestarter` is left **unclaimed** — verified by an API call showing the old slug still
      redirecting to the new one rather than resolving to a different repository.
- [x] **RENAME-02**: `.gitmodules` names `firestarter_fw` on both `beta` and `main`, and
      `git submodule sync --recursive` has been run so an existing clone resolves the new URL without
      relying on the redirect.
- [x] **RENAME-03**: A fresh clone of the meta repository at the milestone tip initialises **both**
      submodules successfully from the URLs recorded at that tip — demonstrated, not reasoned about.

### URL — endpoints that must not depend on a redirect

- [x] **URL-01**: On `beta`, all three `FIRESTARTER_*_URL` constants in
      `firestarter_app/firestarter/constants.py` address `henols/firestarter_fw`. No code path depends on
      GitHub's rename redirect.
- [x] **URL-02**: On `main`, the same three constants address `henols/firestarter_fw`. This is a **separate
      change from URL-01** against a branch 948 commits behind `beta`, and it is the one that reaches the
      default install (D-3).
- [x] **URL-03**: The two hardcoded API URLs in `firestarter_app/tests/test_firmware_install.py` are derived
      from the constants rather than repeated as literals, so a future retarget cannot leave tests green
      while the shipped endpoint is stale.
- [x] **URL-04**: `fw` reports a clear, actionable error when the firmware release endpoint is unreachable
      or returns no asset matching the board — and that state is distinguishable in the output from
      "already up to date". 999.9's goal text requires this; it is also what makes a mistaken retarget
      visible instead of silent.

### STABLE — reach the default install

- [x] **STABLE-01**: A stable release cut from `main` and carrying URL-02 is published to PyPI, so that
      `pip install firestarter` — which resolves to the stable channel, today **2.0.7** — yields a version
      addressing `firestarter_fw`.
- [x] **STABLE-02**: The clean-environment validation named in 999.9 is run **against that stable**, not
      against `beta`: install → query → locate release → download asset → update-check. Running it against
      a prerelease would reproduce the blindness D-3 identifies.

### SWEEP — live references only

- [ ] **SWEEP-01**: Every **live tracked** reference to `henols/firestarter` across the three repositories
      addresses `firestarter_fw` — the meta `README.md`, both sub-repo READMEs, and the five
      `.planning/codebase/` documents (`STRUCTURE.md`, `STACK.md`, `INTEGRATIONS.md`, `ARCHITECTURE.md`,
      `TESTING.md`).
- [ ] **SWEEP-02**: **No file under `.planning/milestones/` is modified** by this milestone — proved by a
      diff over that path returning empty, not by intent. Those 672 references record what the repository
      was called when the record was written (D-5).
- [ ] **SWEEP-03**: **All seven `.planning/codebase/` documents** — `STACK.md`, `ARCHITECTURE.md`,
      `STRUCTURE.md`, `INTEGRATIONS.md`, `TESTING.md`, `CONCERNS.md` and `CONVENTIONS.md` — no longer
      describe a catalog-sync workflow that checks out the sub-repos via `actions/checkout`, nor the
      two retired wiki workflows, nor the removed wiki-tooling directory. None of them exists, and
      the meta repository has no `.github/workflows/` at all. Found while measuring 999.9's
      "CI/release workflows" clause, which is itself a no-op. Widened from `STACK.md` alone to all
      seven during Phase 192, because `CONCERNS.md` and `CONVENTIONS.md` carried the same stale claim
      and were named by neither the original requirement nor the ROADMAP's criterion 4.

### GATE — make the deferred claim measurable

- [ ] **GATE-01**: An adoption instrument reports per-version download share for the `firestarter` PyPI
      package, so the seed's trigger is a number with a stated threshold rather than a judgement call. It
      must state plainly what it does **not** measure — installed base is not observable, and users who
      never upgrade are unreachable by any threshold.
- [ ] **GATE-02**: The standing rule — the meta repository never publishes a GitHub Release — is recorded
      where a future milestone will encounter it before acting, together with the `_compare_versions`
      mechanism that makes violating it silent: a `v1.36` tag parses as PEP 440 `1.36`, so
      `3.0.0b29 >= 1.36` reads true and the firmware is reported current forever.
- [ ] **GATE-03**: The `.gitmodules` history trap is documented with a workaround demonstrated for **both**
      cases: an existing clone (`git config submodule.firestarter.url`) and a fresh clone at a pre-rename
      ref (`--no-recurse-submodules` plus a manual URL set).

---

## Out of Scope

| Item | Reason |
|---|---|
| Claiming `henols/firestarter` for the meta repository | D-1. The single destructive act in 999.9; deferred to a seed behind an adoption trigger, not a date. |
| Renaming `firestarter_app` | 999.9's prose says "all three repositories" but names only two mappings. The host repository keeps its name. |
| Mirroring firmware releases onto the meta repository | D-2. Would split the release surface permanently to solve a temporary problem. |
| Repairing the 672 archived `.planning/milestones/` references | D-5. Historical-by-intent; repairing them destroys the evidence. |
| Re-sweeping v1.35's wiki and README links (phases 169/170/172) | Those break only when the claim fires. The re-sweep travels with the claim. |
| Eliminating stranding for users who never upgrade | Not achievable by any sequencing. Bounded instead by blast radius: the three endpoints are consumed only by `firmware.py`, so only `fw` breaks. |
| Resolving the PyPI/GitHub name incoherence | After the eventual claim, PyPI `firestarter` is the app while GitHub `firestarter` is the meta repo. Noted, not resolved. |
| Firmware source, protocol or behaviour | The firmware repository is renamed and its README repointed. Nothing else. |

---

## Traceability

Which phases cover which requirements. Populated at roadmap creation.

| Requirement | Phase | Status |
|---|---|---|
| RENAME-01 | Phase 189 | Complete |
| RENAME-02 | Phase 189 | Complete |
| RENAME-03 | Phase 189 | Complete |
| URL-01 | Phase 190 | Complete |
| URL-02 | Phase 191 | Complete |
| URL-03 | Phase 190 | Complete |
| URL-04 | Phase 190 | Complete |
| STABLE-01 | Phase 191 | Complete |
| STABLE-02 | Phase 191 | Complete |
| SWEEP-01 | Phase 192 | Pending |
| SWEEP-02 | Phase 192 | Pending |
| SWEEP-03 | Phase 192 | Pending |
| GATE-01 | Phase 193 | Pending |
| GATE-02 | Phase 193 | Pending |
| GATE-03 | Phase 193 | Pending |

**Coverage:**

- v1 requirements: 15 total
- Mapped to phases: 15
- Unmapped: 0 ✓

---
*Requirements defined: 2026-09-13*
*Last updated: 2026-09-13 at v1.38 activation*
