# Repo cleanup, 2026-09-27 — pre-cleanup inventory

State captured immediately before the branch pruning, `.planning/` retirement and disk reclaim.

## Starting state

| Repo | Local branches | Remote branches | Archive tags created |
|---|---|---|---|
| meta (`/workspaces`) | 79 | 37 | 6 |
| `firestarter_app` | 79 | 54 | 20 |
| `firestarter_fw` | 52 | 48 | 27 |

Total workspace on disk: **1.6 GB**. Per-item figures in `disk-before.txt`.

Full branch lists, with tip SHA and last-commit date, in `branches-meta.txt`,
`branches-firestarter_app.txt` and `branches-firestarter_fw.txt`.

## What the archive tags mean

53 tags under `archive/*`, one per distinct branch name that was **not** contained in `beta`,
`main`, `origin/main` or `origin/beta` — 68 unmerged refs in total, since local and remote copies
of the same branch often share a tip. A coverage gate confirmed 0 uncovered tips before any
deletion ran.

Each tag is annotated and points at the branch tip as it stood on 2026-09-27. To recover any
archived branch:

```bash
git checkout -b <name> archive/<name>
```

All 53 tags are pushed to their respective remotes. **Pushing them fired zero CI**, as designed:
every workflow in both sub-repos filters `push: branches: ['**']`, which matches branches but no
tags. Verified by comparing `gh run list` immediately before and after the push — identical run
IDs, no new runs, nothing published.

## Protected from deletion

`beta`, `main`, `release/3.1.x`, `v1.43-voltage-reading-accuracy`, `backmerge/3.1.0-to-beta`, and
`fix/point-at-firestarter` in `firestarter_fw` — the last because it is the head branch of open
PR #67, and deleting a remote head closes its PR.

## Preserved separately

The three full-resolution shield photographs were lifted out of the untracked `tmp/` directory to
`agent-os/evidence/shield-revisions/` before anything was deleted. See that directory's README.
