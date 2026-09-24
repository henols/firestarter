# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Structure

This is the meta repository for the Firestarter EPROM programmer project. The code lives in two
submodules:

- `firestarter_fw/` — Arduino C++ firmware (PlatformIO). See `firestarter_fw/CLAUDE.md`.
- `firestarter_app/` — Python host CLI application (pip package). See `firestarter_app/CLAUDE.md`.

This repository tracks the submodule pointers, `.planning/` (GSD project management artifacts),
`.claude/` (project settings), `tools/catalog/` (messages codegen and sub-repo sync),
`.github/` (issue templates and `CONTRIBUTING.md`, no CI), `.devcontainer/`, `.vscode/`,
`README.md` and `VALIDATED-EPROMS.md`.

User documentation lives only in the `firestarter` GitHub wiki. `README.md` points there.

Comments in product source are allowed in both sub-repos. `.planning/` still contains many
mentions of an old no-comments rule. The rule was removed on 2026-09-19, so ignore those mentions.

`.gitmodules` records a submodule URL per commit. This repository's `main`, and every ref from
before the firmware rename (such as `v1.35`), still has the firmware at path `firestarter` with the
old URL. A plain `git submodule update --init` at such a ref clones *this* repository and fails with
exit 128. Set the override BEFORE the first update, because once a clone has failed the override
alone does not recover it. See `.planning/notes/gitmodules-archaeology-trap.md` for the workarounds
and the `git submodule sync` hazard.

## System Overview

Firestarter is a two-part system for programming EPROMs, Flash, and SRAM devices using an
Arduino-based RURP (Relatively-Universal-ROM-Programmer) shield:

1. **Python CLI** (`firestarter_app/`) — runs on the host PC; parses user commands, looks up chip
   specs from a JSON database, and orchestrates operations via serial.
2. **Arduino firmware** (`firestarter_fw/`) — runs on the Arduino; receives commands, drives the
   hardware bus, and streams data back through a three-phase state machine (INIT → MAIN → END).

The link runs at 250000 baud. The host sends each command as COBS-framed JSON with a CRC8. The
firmware sends status and INIT/MAIN/END as catalog message ID frames, and still sends `OK:` and
`DATA:` as text prefixes.

## Development Commands

Each sub-repo's own `CLAUDE.md` owns its build, test and CI commands. Do not copy them here.

## Cross-repo obligations

These facts span both sub-repos, and neither can state them alone.

- **Serial protocol changes** must stay in sync between `firestarter_app/firestarter/serial_comm.py`
  and `firestarter_fw/src/firestarter.cpp`.
- **Constants and flag bits** are duplicated between `firestarter_app/firestarter/constants.py` and
  three firmware headers. `firestarter_app/CLAUDE.md` § Constants carries the per-block table.
  Change both sides in the same commit pair.
- **Messages are generated here and consumed there.** `tools/catalog/messages.toml` is the source of
  truth. Codegen runs in this repo only. Both sub-repos consume synced artifacts, so never
  regenerate or hand-edit `messages.h` or `messages.py` inside a sub-repo.
- **The data buffer size is set per board in the firmware** (`DATA_BUFFER_SIZE`: 512 by default,
  1024 on Leonardo). The firmware reports it in its `MSG_OK_READY` ack, and the host sizes its chunks
  from that report. When no size is reported, the host falls back to 512.

## Milestone close and branch protection

- **Milestone work forks off `beta` in all three repositories**, on a branch named `v1.X-slug`. If the
  previous milestone's PRs are still unmerged, fork off the previous milestone's branch instead.
  Never commit to `beta` or `main` directly.
- **A push to `beta` in either sub-repo PUBLISHES. Treat it as a release, not a merge.**
  - `firestarter_fw` — `beta-build.yml` cuts a GitHub pre-release carrying the `.hex` assets.
  - `firestarter_app` — `beta-release.yml` cuts a GitHub pre-release, then its `pypi` job calls
    `publish.yml` directly with `secrets: inherit` and **uploads to PyPI**.
  - Neither workflow has a path filter, so a documentation-only push publishes too.
  - A PyPI version can never be reused. Decide the scope of a beta push before making it.
- **`beta` has no protection in any of the three repositories.** A direct push, a force-push and a
  deletion all succeed. Only the publishing consequence above stands between you and a release.
- **`main` is protected in all three repositories** by the "Protect main" ruleset: pull request
  required, no force-push, no deletion. Only a deploy key can bypass it.
- **This project's close targets `beta`, not `main`.** `.planning/config.json` sets
  `git.base_branch` to `beta`, so `/gsd-complete-milestone` and `/gsd-ship` both point there.
- **Before running `/gsd-ship`, recreate local `beta` from `origin/beta`.** `workflows/ship.md`
  anchors its audit range on `RANGE_BASE=$(git merge-base "${BASE_BRANCH}" HEAD)`, and a stale
  local `beta` widens that range.
- **The meta repository must never publish a GitHub Release — bare milestone tags only.** A tag like
  `v1.36` parses as PEP 440 `1.36`, so `Version("3.0.0b29") >= Version("1.36")` reads true and `fw`
  reports the firmware as up to date for every stranded CLI. See
  `.planning/notes/999.9-repo-rename-impact-analysis.md` § "Standing rule this must produce".
- The close mechanics and the blocked stable-release route are in
  `.planning/notes/v135-close-procedure-under-protection.md`.
