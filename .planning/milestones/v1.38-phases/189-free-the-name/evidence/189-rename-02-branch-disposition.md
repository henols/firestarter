# RENAME-02 branch disposition

ROADMAP criterion 2 requires `.gitmodules` to name `firestarter_fw` "on both `beta` and `main`".
This phase reaches those two named branches by two different routes, plus a third branch —
`beta` itself — whose disposition is a deliberate routing decision (D-08), not an omission. This
record states all three so a verifier reading criterion 2 mid-milestone does not misread the
`beta` row as incomplete.

## `v1.38-repository-rename` (milestone branch) — done

The firmware submodule URL was repointed on this branch via `git submodule set-url` followed by
`git submodule sync --recursive` (D-03), landing as commit `5aba9dbc8d760e530638931d19ede0a227dd1a60`
in plan `189-02`. All three D-03 observables — `.gitmodules`, the superproject's local
`submodule.firestarter.url`, and `firestarter/`'s own `remote.origin.url` — were read live and
recorded, alongside the untouched `firestarter_app` control, in
`.planning/phases/189-free-the-name/evidence/189-rename-02-observables.txt`.

## `main` — done via pull request

Per D-07, the meta repository's `main`-branch `.gitmodules` change lands as its own pull request
inside Phase 189, independent of Phase 191's `firestarter_app` `main` work: `main` is the meta
repository's GitHub default branch, so it is the copy of the submodule URL that the front door's
Clone button hands out, and keeping this pull request independent preserves the roadmap's stated
invariant that every phase depends on 189 and on nothing else of each other. `main` is protected
with `current_user_can_bypass: never`, so a pull request was the only route, and every
outward-facing step in this project is operator-gated (D-7): the agent prepared the branch
`v1.38-gitmodules-main` (one commit, one insertion and one deletion in `.gitmodules`, forked from
`origin/main`), and the operator pushed it, opened the pull request and merged it.

- **Prepared commit:** `d1a83997f6890f27455fc7a6e8fc5d5e4757d41a` on local branch
  `v1.38-gitmodules-main`, forked from `origin/main`.
- **Pull request:** `henols/firestarter_prom#79`, base `main`, head `v1.38-gitmodules-main`,
  1 file changed / 1 addition / 1 deletion.
- **Merged:** `merged: true`, merge commit sha `6b518c74831c6d3cf56513d80134684fbd673fef`.

**Verification, read from GitHub at `ref=main` (not from the local clone) — captured
2026-09-13T14:25:23Z:**

```
[submodule "firestarter"]
	path = firestarter
	url = git@github.com:henols/firestarter_fw.git
[submodule "firestarter_app"]
	path = firestarter_app
	url = git@github.com:henols/firestarter_app.git
```

- `git@github.com:henols/firestarter_fw.git` count: **1**.
- Bare-slug reference (`henols/firestarter` with no `_fw`/`_app`/`_prom` suffix) count: **0**.
- Positive control — `henols/firestarter_app` present — count: **1** (proves the zero above is a
  real absence, not an empty response).

This reading was taken with `gh api "repos/henols/firestarter_prom/contents/.gitmodules?ref=main"
-H "Accept: application/vnd.github.raw"`, i.e. against the protected default branch itself, which
is what "landed" means for this criterion — a local branch proves only what was prepared.

## `beta` — close-carried (D-08)

The `beta` half of criterion 2 is **close-carried**: it is a deliberate routing decision, not an
incomplete requirement. It lands when the milestone merges, which is the standard route for every
change in this project — `beta` is not touched by any plan in this phase. An early merge to `beta`
is not an option: it would fire a pre-release cut in both sub-repositories and publish the host
one to PyPI (D-7), which is exactly the outcome this milestone's operator-gated close procedure
exists to prevent. A verifier reading this phase mid-milestone should read "`beta` does not carry
the change yet" as this recorded routing decision, not as unfinished work.

## Summary

| Branch | Disposition | Evidence |
|---|---|---|
| `v1.38-repository-rename` | done | commit `5aba9dbc8d760e530638931d19ede0a227dd1a60`; `evidence/189-rename-02-observables.txt` |
| `main` | done via pull request | PR `henols/firestarter_prom#79`, merge sha `6b518c74831c6d3cf56513d80134684fbd673fef`; read back from GitHub above |
| `beta` | close-carried | lands at milestone close (D-08); not an incomplete requirement |
