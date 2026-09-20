---
title: Promote 3.0.x to stable — beta → main in all three repositories
trigger_condition: v1.41 closed AND the 2.0.10 pre-flash version guard released to PyPI AND at28c256 (#21/#11/#12) resolved or documented as unsupported
planted_date: 2026-09-20
status: dormant
---

# Promote 3.0.x to stable

Cut the first stable release of the 3.0 line: merge `beta` into `main` in the meta repository and
both sub-repos, publish `firestarter` 3.0.0 to PyPI, and cut a stable `firestarter_fw` release
carrying the `.hex` assets.

**Why this is a milestone and not a merge:** `main` has been frozen on the 2.0.x line while `beta`
served as trunk for fifty pre-releases. As of 2026-09-20 `beta` leads `main` by 1060 commits in
`firestarter_app`, 617 in `firestarter_fw` and 2055 in the meta repository. The merge itself is
mechanical. The consequences are not — the firmware merge *is* the stable release, because
`firestarter_fw`'s `build.yml` carries no path filter.

Full analysis, with the evidence behind every figure:
[`../notes/stable-3.0.0-release-gate.md`](../notes/stable-3.0.0-release-gate.md).

## Why the trigger conditions are what they are

**The 2.0.10 guard must ship first.** The published 2.0.9 wheel resolves firmware through
`repos/henols/firestarter_fw/releases/latest`, which excludes pre-releases and today returns the
matched 2.0.6. The first stable 3.0.0 firmware release flips that endpoint for every 2.0.9 CLI in the
field, and 2.0.9's own version comparison will recommend the flash that breaks the pair. Releasing
the guard afterwards does not help anyone already trapped. This ordering is not negotiable.

**v1.41 must close first** — it moves blank-check and verify to the host, so promoting mid-milestone
would ship a surface under active rewrite.

**AT28C256 is the highest-volume part in the audience** and carries an open FAIL. Resolve it, or state
plainly that it is unsupported, before it becomes stable-release support load.

## Scope when this fires

- Merge `beta` → `main` in the meta repository and both sub-repos.
- Publish `firestarter` 3.0.0 to PyPI; cut the stable `firestarter_fw` release with its `.hex` assets.
  **Sequence the app before the firmware**, so the upgrade path exists before the endpoint flips.
- Rewrite the wiki `Breaking-Changes` preamble — it currently reads "All of these are beta-only.
  Nothing is promoted to stable without operator authorization."
- Add a stable-install wiki page alongside `Install-Beta`.
- Decide whether either sub-repo gains a `CHANGELOG`; neither has one today.

## Standing hazards that apply to the execution

Both are recorded in the root `CLAUDE.md` and still hold at promotion time:

- The meta repository must never publish a GitHub Release — bare milestone tags only.
- `firestarter_fw`'s `build.yml` does not ignore `.github/**`, so any push to `main` cuts a stable
  release. There is no dry run.
