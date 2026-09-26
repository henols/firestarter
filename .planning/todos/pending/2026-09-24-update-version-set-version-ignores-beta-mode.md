---
created: 2026-09-24
source: .planning/milestones/v1.41-phases/207.1-address-v1-41-tech-debt/207.1-REVIEW.md § WR-03 (pre-existing; filed at the v1.41 milestone close)
resolves_phase:
severity: major
area: release tooling
---

# `update_version.py --set-version` does not enter beta mode

`firestarter_app/.github/scripts/update_version.py`'s `--set-version` help text calls it an "Alias
for BETA_VERSION env var". The env var turns on beta mode (`is_beta_mode`, `:61`). The alias does
not: `is_beta_mode` never reads `args.set_version`.

Run `update_version.py --set-version 3.0.0b50` on a ref other than `beta`, without `--beta` or
`BETA_VERSION`. It takes the STABLE branch (`:181-199`), discards the requested version, increments
the patch, and writes a stable `X.Y.(Z+1)` into `firestarter/__init__.py` and `$GITHUB_OUTPUT`.

**Why this matters more than its size.** The script is on the publish path. PyPI never accepts
the same version twice, and a stable release is operator-gated (root `CLAUDE.md`). No test covers
the script (`grep -rl update_version tests/` is empty), and it is outside every CI gate. v1.41
Phase 207.1 D-12 touched the file, but only to reformat it.

**Needs an operator decision:** fix it, or move it to the backlog. The v1.41 re-audit recorded it
as open for that reason.

## Fix

Treat an explicit `--set-version` as a beta request, or refuse the combination:

```python
def is_beta_mode(args) -> bool:
    if args.beta or args.set_version:
        return True
    ...
```

Add a test that runs the script with `--set-version` on a non-beta ref and asserts that either a
beta version or a refusal is the result, never a stable patch bump.

## Status (2026-09-24)

The code fix is in `firestarter_app` `11c9a8c`. `is_beta_mode` now returns True for an explicit
`--set-version`. A manual `--dry-run --set-version 3.0.0b99` run on a non-beta ref printed
`3.0.0b99`. The automated test that this todo asks for is not written yet. That test is the only
open item.
