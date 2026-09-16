---
created: 2026-09-08T00:00:00Z
title: Reclaim ~172M of local scratch from the meta-repo working tree
area: meta
files:
  - .v1.34-arms/ (56M — two firestarter_app checkouts, both shas on origin/beta)
  - graphify-out/ (48M — duplicate graph.json + cache)
  - firestarter_app_py32/ (24M — branch is an ancestor of origin/beta)
  - .planning/graphs/graph.json (23M — untracked duplicate)
  - .planning/milestones/v1.7-artifacts/upstream-rurp/ (16M — clone of a public upstream)
  - firestarter-runs/ (1.6M), firestarter_py32_ci/ (1.5M), chip-test/ (40K)
  - AM27C020.bin (256K), scratchpad/ (empty)
  - .planning/notes/disposable-artifact-inventory.md (the evidence)
---

## Problem

The working tree carries ~172M of ignored/untracked scratch: two `.v1.34-arms` checkouts, a
duplicate 23M knowledge graph stored twice, a py32 clone whose branch already merged to `beta`,
a 16M clone of a public upstream buried in a closed milestone directory, and tool caches
including orphaned `.pyc` for five checkers deleted in `5426d7ef`.

None of it is tracked. Every item's safety condition is measured and recorded in
`.planning/notes/disposable-artifact-inventory.md`.

## Two carve-outs that MUST survive

These are git-ignored and therefore ride the same sweep as build junk. Do **not** remove them:

1. `.planning/state.json` and `.planning/milestone.lock` — ignored at `.gitignore:78-79`, but
   they are GSD's live state.
2. `.planning/milestones/v1.34-artifacts/bench/cells/**/reads/*.bin` — 4.0M of hardware **measurements**
   (`run_NN.bin`, `written.bin`). Irreproducible without the rig and the physical chips. No sha
   rebuilds these, unlike `.v1.34-arms/`.

## Approach

Remove by explicit path. Do **not** use a blanket `git clean -Xdf` — that would take both
carve-outs above.

## Acceptance

- [ ] Each path in `files:` above is gone from the working tree.
- [ ] `.planning/state.json` and `.planning/milestone.lock` still exist.
- [ ] `find .planning/milestones/v1.34-artifacts/bench -name '*.bin' | wc -l` is unchanged from its pre-task count.
- [ ] `git status --short` is still clean (nothing tracked was touched).
- [ ] `tools/wiki/__pycache__/` is gone but `.planning/milestones/v1.35-MIGRATION-TABLE.md` remains.
- [ ] Root `platformio.ini` still exists — it is **generated** by
      `.devcontainer/gen-platformio-ini.py` (invoked from `.devcontainer/post-create.sh:5`) and
      root-level `pio` needs it. If removed, regenerate with
      `python3 .devcontainer/gen-platformio-ini.py`.
- [ ] `W29C040.bin` still exists — 32 bytes, 3 citations in `.planning/`; zero gain in removing it.
- [ ] Reclaimed total reported against a measured before/after `du -sh /workspaces`.

## Notes

Regenerating afterwards, if needed: the graph via the graphify skill; the v1.34 arms via
`git checkout 6bfa6453` / `cb189a9b` in a fresh `firestarter_app` clone; `upstream-rurp` via
`git clone https://github.com/AndersBNielsen/Relatively-Universal-ROM-Programmer.git`;
`firestarter_py32_ci` via `git clone` + `git checkout feature/py32f071-release-assets`.
