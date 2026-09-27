# The retired `.planning/` tree

`.planning/` was the state directory of GSD, the planning system this project used until
2026-09-25. GSD was uninstalled and replaced by `agent-os/`. The tree itself was removed from the
working tree on **2026-09-27**.

Nothing was lost. Every one of its 5460 files stays in history, reachable by name:

```bash
git show 'archive/planning-tree-final:.planning/ROADMAP.md'
git show 'archive/planning-tree-final:.planning/milestones/v1.23-FLASH-PATH-DECISION.md'
git ls-tree -r --name-only archive/planning-tree-final .planning   # list everything
```

The tag `archive/planning-tree-final` points at meta commit `179b600a`, the last commit carrying
the complete tree. It is pushed, so the command above works in any clone.

## Reading a citation that names a `.planning/` path

Many documents in `agent-os/` — specs, standards and todos — cite `.planning/` paths, often with
line numbers. Those citations are still correct; they describe files that exist at the tag, not in
the working tree. Prefix the path with the tag and they resolve.

**Line numbers are valid as of the tag and no later.** The tree is frozen, so they will not drift
again, but a citation written before 2026-09-27 may name a line from an earlier revision of the
same file. When a line number does not match, search for the quoted text instead.

The same applies to `.planning/` paths cited in docstrings and comments inside `firestarter_app`
and `firestarter_fw`. Those are provenance notes, not reads — no test resolves them at runtime,
and `firestarter_fw/tests/test_flash_path_record_sync.py::test_no_test_reads_outside_this_repo`
now enforces that none ever will.

## What moved instead of being archived

The 46 **pending** todos were working state, not history, so they moved to `agent-os/todos/`
rather than being frozen. The 40 completed ones stayed behind at the tag.

The authoritative PY32F071 flash-path record and its fw-install seed were vendored into
`firestarter_fw/platform/py32f071/`, because a test compared them and
`standards/testing/standalone-checkout.md` forbids a test reading the meta repo. That vendoring
landed in `firestarter_fw` PR #77.

The three full-resolution shield photographs, which had never been committed anywhere, were
preserved to `agent-os/evidence/shield-revisions/`.

## Why a tag and not a branch

A branch moves; a tag does not. The tree is finished, and a name that cannot drift is the point.

Note also that `5b9e41ab` appears in
`specs/2026-09-25-2218-3-1-x-release-readiness/references.md` as an earlier pin for the same
purpose — the tip of `origin/beta` on 2026-09-25. It remains valid. Prefer
`archive/planning-tree-final` in new citations: it is legible, and it carries the tree's final
state rather than a mid-retirement snapshot.
