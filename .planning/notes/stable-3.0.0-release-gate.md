# The gate on a public 3.0.x release

**Date:** 2026-09-20
**Raised during:** `/gsd-explore` — "when can I release 3.0.x to the public?"
**Status:** Analysis. No work planned from it yet. The promotion itself is seeded at
[`../seeds/stable-3.0.0-promotion.md`](../seeds/stable-3.0.0-promotion.md).
**Method:** Every figure below was read from the repositories and the GitHub API on 2026-09-20, with
the command noted beside it. Nothing here is inferred from the roadmap.

## The shape of the question

`beta` is the trunk and has been for fifty pre-releases. `main` is frozen at the 2.0.x line.

| repo | `main` | `beta` | `beta` ahead by |
|---|---|---|---|
| `firestarter_app` | 2.0.9 | 3.0.0b50 | 1060 |
| `firestarter_fw` | 2.0.6 | 3.0.0b35 | 617 |
| meta | — | — | 2055 |

Counts from `git rev-list --left-right --count origin/main...origin/beta` per repo. Sub-repo versions
from `firestarter/__init__.py` on each branch and from the firmware release tags.

So "move `beta` to `main`" is not a merge decision. It is a decision to cut 3.0.0 stable. The merge
across all three repositories is mechanical; what follows is not.

## The hard blocker — 2.0.9 users are trapped by the firmware release

The published 2.0.9 wheel hard-codes its firmware endpoint. From `git show 2.0.9:firestarter/constants.py`:

```
"https://api.github.com/repos/henols/firestarter_fw/releases/latest"
```

`/releases/latest` excludes pre-releases. Today it resolves to a matched pair —
`gh api repos/henols/firestarter_fw/releases/latest` returns `tag_name: 2.0.6`, `prerelease: false`,
carrying `firestarter_uno.hex` and `firestarter_leonardo.hex`, published 2025-11-16. A 2.0.9 user
running `firestarter fw` gets 2.0.6 firmware, and the pair works.

**The moment `firestarter_fw` cuts a stable 3.0.0 release, that endpoint flips**, and every 2.0.9 CLI
in the field starts resolving 3.0.0 firmware. By the project's own
[`Breaking-Changes`](https://github.com/henols/firestarter/wiki/Breaking-Changes) wiki page, "a new CLI
cannot drive old firmware, and old firmware cannot be driven by a new CLI."

It is worse than passive. `FirmwareManager._compare_versions` in 2.0.9 reads:

```python
current = tuple(map(int, current_version_str.split(".")))
latest  = tuple(map(int, latest_version_str.split(".")))
return current >= latest
```

`(2,0,6) >= (3,0,0)` is `False`, which the caller reads as "out of date". The 2.0.9 CLI will therefore
**actively recommend** the flash that breaks it, then leave the user with a programmer their installed
CLI cannot talk to and no error that explains why.

Sequencing the app release before the firmware release does not fix this. A user who never runs
`pip install --upgrade` still walks into it. The fix has to ship *before* the firmware release, in a
CLI on the stable channel.

## The guard — decided design

A `2.0.10` stable release whose only change is a pre-flash version guard.

The guard must work from release metadata alone. The CLI is deciding whether to download a `.hex` it
has not run yet, so no handshake is available and the release tag is the only signal.

**The rule.** Compare feature versions — `(major, minor)`, patch ignored:

```
refuse when (fw.major, fw.minor) > (cli.major, cli.minor)
```

| CLI | firmware | result | rationale |
|---|---|---|---|
| 2.0.10 | 3.0.0 | refuse | the case at hand |
| 3.0.0 | 3.1.0 | refuse | generic to any future minor bump — the operator's requirement |
| 3.0.0 | 3.0.5 | allow | patches flow freely |
| 3.0.0b50 | 3.0.0b35 | allow | same wire protocol |
| 3.1.0 | 3.0.0 | allow | reverse mismatch, deferred — see below |

Decisions made in the explore session, with their reasons:

- **Hand-roll the parser; do not add `packaging`.** 2.0.9's dependencies are `pyserial`, `requests`,
  `tqdm`, `argcomplete`, `rich` (`git show 2.0.9:pyproject.toml`). Adding a dependency to a
  1060-commit-stale branch whose CI carries its own release-cutting hazards buys nothing. `^v?(\d+)\.(\d+)`
  suffices, and it tolerates the `b35` pre-release suffix that the existing `int()` parse raises
  `ValueError` on.
- **Fail closed on an unparseable version, either side.** This project has a documented history of
  gates that fail open. "I could not read the firmware tag" must refuse, not proceed.
- **Ship a `--force` escape hatch.** Mismatched pairs are flashed deliberately at the bench; a refusal
  with no override would break the operator's own workflow.
- **The message is the feature.** The refusal must name the exact command — `pip install --upgrade
  firestarter` — because this guard converts "CLI first, then firmware" from prose in the wiki into a
  contract enforced in code, permanently. Every future minor firmware bump will block users until
  they upgrade the CLI.

The guard's natural home is `FirmwareManager._compare_versions` and its caller: the parse already
exists there, and the guard is a second comparison against `firestarter.__version__` in the opposite
direction. It lands in `2.0.10` and on the 3.0.x line.

**Deferred, by operator decision on 2026-09-20:** the mirror case — a new CLI driving old firmware
already on a board. It is detectable at runtime, because `check_current_firmware()` already returns
the board's version string, but it is out of scope for the trap guard and was not filed as work.

## The soft gate — the common parts are failing

`gh issue list -R henols/firestarter --state open` returns 22 open issues, 12 of them `dev test`
failures, 6 labelled `cause:firmware` and 5 `cause:database`. The ones that bear on a public launch
are not the exotic parts:

- **#21 `at28c256` — FAIL**, with #11 and #12 against the same family. This is the highest-volume
  part in the target audience.
- #28 `m27c512` — FAIL, #23 `w27e257` — FAIL
- #86 and #90 `SST39SF040` — FAIL, two independent reports

`VALIDATED-EPROMS.md` lists **11 bench-validated chips against 746 database rows**. That ratio is
honest and appropriate for a beta — the database is generated, so coverage is a claim, not a proof,
and the ledger says so. It is not by itself a release blocker. An open FAIL on AT28C256 is a
different matter, because it converts directly into support load.

## Other observations

- **Neither sub-repo carries a `CHANGELOG`.** The wiki `Breaking-Changes` page covers the ground well
  but is framed beta-only: "All of these are beta-only. Nothing is promoted to stable without operator
  authorization." That sentence has to change at promotion.
- The wiki has an `Install-Beta` page and no stable-install counterpart.
- v1.41 is in flight and moves blank-check and verify to the host. Cutting 3.0.0 mid-milestone would
  ship a surface that is being actively rewritten.

## What this adds up to

The commit-count divergence is not the problem and never was. Three things gate a public 3.0.x:

1. The 2.0.9 trap must be closed by a `2.0.10` guard released before any stable firmware release.
2. AT28C256 and the two SST39SF040 reports should be resolved or explicitly documented as unsupported.
3. v1.41 should close first.
