# Disposable artifact inventory — what can and cannot be removed from the meta-repo

**Date:** 2026-09-08
**Raised during:** `/gsd-explore "what files and directories can safely be removed from this project?"`
**Method:** direct measurement in the devcontainer at `/workspaces` on branch `gsd/v1.36-dev-test-fidelity-planning`. No research pass ran; every claim below is a local repo fact from a command executed in that session.

## Headline

The removable mass is **local scratch, not repo content**. Roughly **172M** of ignored/untracked
material can go with no loss that a re-clone or a regeneration cannot restore. The *tracked*
surface, by contrast, is 36 files outside `.planning/` and is essentially all live.

## Safe to remove — with the condition that makes each one safe

| Path | Size | Safety condition (measured) |
|---|---|---|
| `.v1.34-arms/` | 56M | Two clean checkouts of `firestarter_app`; `6bfa6453` (control) and `cb189a9b` (v133) are both reachable from `origin/beta`. Rebuildable by checkout. |
| `graphify-out/` | 48M | `graphify-out/graph.json` is byte-identical to `.planning/graphs/graph.json` (both md5 `684bd785fe6f3afb079d60a8284826d0`). `cache/` and `manifest.json` are graphify output. |
| `firestarter_app_py32/` | 24M | Branch `feature/py32f071-fw-install` @ `4ee64a14` is an **ancestor of `origin/beta`** — `rev-list --count origin/beta..HEAD` = 0. The work already landed. |
| `.planning/graphs/graph.json` | 23M | Untracked and ignored. Only `GRAPH_REPORT.md` is tracked in that directory. |
| `.planning/milestones/v1.7-artifacts/upstream-rurp/` | 16M | A full clone of the **public** `AndersBNielsen/Relatively-Universal-ROM-Programmer` @ `9178d84` (2025-11-28), incl. a 7.4M `.git`. Re-clonable. |
| `.mypy_cache/` + every `__pycache__` / `.pytest_cache` / `.ruff_cache` / `.cache-uv` | ~2.3M | Tool-generated; each self-ignores via its own `.gitignore`. |
| `firestarter-runs/` | 1.6M | AM27C020 consistency-check `run_NN.bin` from 2026-06-30. Operator ruled reconstructible. |
| `firestarter_py32_ci/` | 1.5M | 53 commits ahead of `origin/beta`, but the branch **is pushed** and tracks `origin/feature/py32f071-release-assets`. Nothing exists only locally. |
| `AM27C020.bin` | 256K | Zero citations anywhere in `.planning/`. |
| `chip-test/` | 40K | Operator ruled reconstructible. |
| `scratchpad/` | 0 | Empty directory, untracked. |

## Two traps — both are git-ignored, so an "delete what's ignored" sweep destroys them

1. **`.planning/state.json` and `.planning/milestone.lock`** are ignored at `.gitignore:78-79`.
   These are GSD's live state, not build output. Losing `state.json` loses session position — and
   note it scrapes the STATE.md **body**, not frontmatter, so it is not trivially reconstructible
   from the record.

2. **`.planning/milestones/v1.34-artifacts/bench/cells/**/reads/*.bin`** — 4.0M of ignored `run_NN.bin` and
   `written.bin`, per cell per arm (`A1`, `A3-B2`, `BRINGUP-wrv` × `control`/`v133` ×
   `w27c512`/`w29c020`). These are **measurements taken on hardware**, not artifacts of a build.
   Unlike `.v1.34-arms/`, no sha reproduces them: they need the rig and the physical chips.
   The distinction matters because both live under the same ignore rules as `__pycache__`.

Total ignored bytes under `.planning/` is 68M, of which the 23M duplicate graph and the 16M
`upstream-rurp` clone are the only large disposable parts.

## The tracked surface yields nothing

`git ls-files | grep -v '^\.planning/'` is 36 entries: the devcontainer, two **registered** CI
workflows (`catalog-sync-check.yml`, `rekey-ledger-check.yml`), the issue templates,
`tools/catalog/`, `tools/rekey/`, the two `devtest-*` skills, and `.planning/milestones/v1.35-MIGRATION-TABLE.md`.
All live.

`tools/wiki/` is the one place that *looks* retired and partly is: commit `5426d7ef` (2026-09-02)
deleted `wiki.py`, `honest01_claims.py`, `honest02_truth.py`, `provenance_footers.py`,
`dispatch_mirror.py`, `selftest.sh`, `claim-allowlist.json` and `claim-vocabulary.json`. Their
compiled `.pyc` files were left behind in `tools/wiki/__pycache__/` — orphaned bytecode for
sources that no longer exist, which is direct evidence that **no cleanup step ran at
retirement**. That residue is disposable; see the reclaim todo.

`MIGRATION-TABLE.md` survived that deletion and is the milestone's provenance record, not
tooling. Operator's call: *"it is done and does not belong in tools"*. It is cited **286 times
across 85 files** in path form (`.planning/milestones/v1.35-MIGRATION-TABLE.md`), plus 221 bare mentions, and
several citations are line-anchored (`:15`, `:18-19`, `:20`, `:45-58`, `:52-53`, `:68-80`,
`:104-105`). So it must be **relocated with a scripted path remap**, never deleted. Tracked
separately as a todo.

## `tools/rekey/check_rekey_ledger.py` reads like a GSD bypass and is not one

Raised during this exploration: *"isn't that something that is bypassing gsd?"* It is a fair first
impression — a hand-rolled Python checker with its own GitHub Actions workflow — and it is wrong.
Recording the refutation so a later cleanup sweep does not act on the same instinct.

- `.planning/MILESTONES.md` (line 49 as it then stood) designated the **local** invocation, `python3
  tools/rekey/check_rekey_ledger.py` run from `/workspaces`, as the **primary** gate, and states
  it "does not depend on CI registration to exist at all (D-13)". The registered workflow is the
  *additional* leg — its own `name:` field says so. When a row goes red, the local gate is
  checked first.
- It is produced by GSD, not around it: Phase 174, GATE-06, D-13. **43** `.planning/` files
  reference it, and `179-02-PLAN.md` names its exact output as an acceptance criterion
  (`OK: 8 ledger row(s), 8 MILESTONES.md row(s) bound`). Verified 2026-09-08: that is what it
  prints, exit 0.
- It covers a seam GSD structurally cannot: binding a `.planning/` record to a file **inside a
  submodule**. The meta tree holds only the gitlink (`160000 commit 9f398536`), and no GSD verb
  reads across it.
- It is hardened against three defects already recorded in this project: paths resolve from an
  explicit `--repo-root` and never from `__file__`'s parent (the `check_permitted_claims.py`
  `_HERE` failure, which scanned nothing and exited 0); the workflow resolves the gitlink sha with
  `git rev-parse HEAD:firestarter_app` and checks the sub-repo out explicitly rather than trusting
  a submodule fetch (the empty-submodule under-detection failure); and the ledger is read with
  `ast.parse` + `ast.literal_eval`, never imported, honouring the standing "skills must own their
  scripts" rule.

**The one genuine inversion**, worth knowing but not a bypass: the checker treats the app-side
ledger `firestarter_app/tests/fixtures/rekey_ledger.py` as **authoritative** and
`.planning/MILESTONES.md` as narrating it for a human. That reverses GSD's usual "`.planning/` is
the record" direction. It is a recorded decision (D-09/D-13), justified by the ledger being
machine-readable and co-located with the frozen test hashes it governs.

**Verdict, superseded the same day.** The paragraphs above answered "is this a bypass?" — no,
its provenance is GSD's own. They did **not** answer "should it exist?", and the operator's ruling
on that is the opposite: *"it's not the CI's job to do"*, and *"gsd shall not use it in any way at
all, it will just break the GSD's intended workflow."* Provenance is not justification. Two
measured defects settle it independently — the coupling turns app CI red (`13 failed, 13 passed`
on a bare checkout versus `26 passed` here), and three of the checker's own fail-closed proofs are
tautological, because `python3` on a missing script exits `2` exactly as the checker's
fail-closed path does, so they pass with their own subject deleted. Retirement scope is in
`.planning/todos/pending/2026-09-08-retire-the-rekey-cross-tree-checker.md`. After it lands,
`tools/` holds only `catalog/`.
