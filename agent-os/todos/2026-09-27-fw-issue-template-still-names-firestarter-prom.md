---
created: 2026-09-27
source: firestarter_fw PR #67 (closed as superseded — two of its three hunks had already landed)
resolves_phase:
severity: minor
area: repo hygiene
---

# `firestarter_fw` issue template still names the old `firestarter_prom` repo

`firestarter_fw/.github/ISSUE_TEMPLATE/config.yml:4` points the "Central Firestarter issue
tracker" contact link at:

```
https://github.com/henols/firestarter_prom/issues/new/choose
```

Stale on **`main`, `beta` and `release/3.1.x`** — all three. `firestarter_app`'s copy of the same
file already names `henols/firestarter`, so the two sub-repos disagree.

## Not urgent, and here is why

The old name still resolves: `henols/firestarter_prom/issues` returns **301** and lands correctly
on `henols/firestarter/issues` (measured 2026-09-27). Nothing is broken for anyone clicking it.

But a GitHub rename redirect is not a guarantee. It stops working permanently the moment anyone
creates a new repository named `firestarter_prom`, and the link sits in the issue-creation UI —
the one place a new contributor meets the project.

## Why it is a todo rather than a PR

Neither route is free for a one-line docs change:

- **Push to `beta`** publishes a firmware pre-release. `beta-build.yml` has no path filter, so a
  documentation-only push still cuts a release and burns a version number.
- **Push to `main`** fires `build.yml`, the stable publisher. `config.yml` is not covered by its
  `**.md` paths-ignore, so it is not skipped. The job currently dies at the version bump (GH013,
  rejected by the `Protect main` ruleset), so it publishes nothing — but it does go red.

## How to apply

Fold the one-line change into the **next `beta` change that is happening anyway** for other
reasons, so it rides along at zero extra cost. Then it flows to `main` and `release/3.1.x` by the
normal promotion path.

Two of PR #67's three hunks — `README.md` and `.github/CONTRIBUTING.md` — already landed via the
sibling branch `fix/point-at-firestarter-beta`. Only `config.yml` remains. Do not resurrect #67
wholesale; it was measured from a 2026-09-15 merge base and its other two hunks are no-ops now.
