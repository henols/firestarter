---
created: 2026-09-20T00:00:00Z
title: Pre-flash firmware version guard — refuse a firmware whose feature version exceeds the CLI's
area: host
resolves_phase: null
source: .planning/notes/stable-3.0.0-release-gate.md (explore session 2026-09-20); gates .planning/seeds/stable-3.0.0-promotion.md
files:
  - firestarter_app/firestarter/firmware.py (FirmwareManager._compare_versions and its caller — the guard site on both the 2.0.x and 3.0.x lines)
  - firestarter_app/firestarter/constants.py (2.0.x only — FIRESTARTER_RELEASE_URL, the endpoint that flips)
  - firestarter_app/firestarter/__init__.py (the CLI version the guard compares against)
---

## Problem

The published 2.0.9 wheel resolves firmware through a hard-coded endpoint
(`git show 2.0.9:firestarter/constants.py`):

```
"https://api.github.com/repos/henols/firestarter_fw/releases/latest"
```

`/releases/latest` excludes pre-releases. Today it returns a matched pair —
`gh api repos/henols/firestarter_fw/releases/latest` gives `tag_name: 2.0.6`, `prerelease: false`,
with `firestarter_uno.hex` and `firestarter_leonardo.hex`. A 2.0.9 user running `firestarter fw`
gets 2.0.6 firmware and everything works.

**The first stable 3.0.0 firmware release flips that endpoint for every 2.0.9 CLI in the field.**
Per the wiki's Breaking-Changes page, "a new CLI cannot drive old firmware, and old firmware cannot
be driven by a new CLI."

The CLI does not merely permit this — it recommends it. `FirmwareManager._compare_versions` reads:

```python
current = tuple(map(int, current_version_str.split(".")))
latest  = tuple(map(int, latest_version_str.split(".")))
return current >= latest
```

`(2,0,6) >= (3,0,0)` is `False`, which the caller reads as "out of date". The user is prompted to
flash, accepts, and ends up with a programmer their installed CLI cannot talk to, no error that
explains why, and no hint that the fix is `pip install --upgrade firestarter`.

Sequencing the app release before the firmware release does not fix this: a user who never upgrades
the CLI still walks into it. **The guard has to be on the stable channel before any stable firmware
release**, which means a `2.0.10` release cut from `main`.

## The rule

Compare feature versions — `(major, minor)`, patch ignored:

```
refuse when (fw.major, fw.minor) > (cli.major, cli.minor)
```

| CLI | firmware | result | rationale |
|---|---|---|---|
| 2.0.10 | 3.0.0 | refuse | the case at hand |
| 3.0.0 | 3.1.0 | refuse | generic to any future minor bump |
| 3.0.0 | 3.0.5 | allow | patches flow freely |
| 3.0.0b50 | 3.0.0b35 | allow | same wire protocol |
| 3.1.0 | 3.0.0 | allow | reverse mismatch — out of scope, see below |

The guard must work from release metadata alone. The CLI is deciding whether to download a `.hex` it
has not run yet, so no handshake is available and the release tag is the only signal.

## Decisions already made

Taken in the explore session of 2026-09-20; reasons recorded so they are not relitigated.

- **Hand-roll the parser; do not add `packaging`.** 2.0.9 depends on `pyserial`, `requests`, `tqdm`,
  `argcomplete`, `rich` and nothing else (`git show 2.0.9:pyproject.toml`). Adding a dependency to a
  branch 1060 commits stale, whose CI carries its own release-cutting hazards, buys nothing.
  `^v?(\d+)\.(\d+)` suffices and tolerates the `b35` pre-release suffix that the existing `int()`
  parse raises `ValueError` on.
- **Fail closed on an unparseable version, either side.** This project has a documented history of
  gates that fail open. "I could not read the firmware tag" must refuse, not proceed. Give the
  CLI-side parse failure a distinct message — it indicates a packaging fault, not a mismatch.
- **Ship a `--force` escape hatch.** Mismatched pairs are flashed deliberately at the bench; a
  refusal with no override breaks the operator's own workflow.
- **The message is the feature.** The refusal must name `pip install --upgrade firestarter`
  verbatim. This guard converts "CLI first, then firmware" from prose in the wiki into a contract
  enforced in code, permanently — every future minor firmware bump blocks users until they upgrade
  the CLI, so the refusal will be seen often and must be self-explanatory.

## Scope

Lands twice, with the same rule and the same message:

1. **`2.0.10`**, cut from `main`. The guard is the *only* change. This is the release that closes
   the trap, and it must reach PyPI before any stable firmware release.
2. **The 3.0.x line** on `beta`, so the rule is permanent rather than a one-off patch to a dead
   branch.

**Explicitly out of scope, by operator decision on 2026-09-20:** the mirror case — a new CLI driving
old firmware already on a board. It is detectable at runtime, since `check_current_firmware()`
already returns the board's version string, but it is a different mechanism in a different place and
was deferred rather than filed.

## Caution

`main` in `firestarter_app` is 1060 commits stale and cutting `2.0.10` from it means exercising that
branch's release path. Check `release.yml` and `publish.yml` behaviour there first — see
`.planning/todos/pending/2026-09-13-publish-yml-release-published-never-fires.md` and
`.planning/todos/pending/2026-09-13-release-yml-autocommit-vs-ruleset.md`, both of which concern
exactly this branch's publishing machinery.
