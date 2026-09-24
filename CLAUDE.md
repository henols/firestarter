# CLAUDE.md

This file gives guidance to Claude Code (claude.ai/code) for work in this repository.

## Repository Structure

This is the meta repository for the Firestarter EPROM programmer project. The code is in two
submodules:

- `firestarter_fw/` — Arduino C++ firmware (PlatformIO). Read `firestarter_fw/CLAUDE.md`.
- `firestarter_app/` — Python host CLI application (pip package). Read `firestarter_app/CLAUDE.md`.

This repository tracks these items:

- The two submodule pointers.
- `.planning/` — GSD project management artifacts.
- `.claude/` — project settings.
- `tools/catalog/` — the messages codegen and the sub-repo sync script.
- `.github/` — issue templates and `CONTRIBUTING.md`. This repository has no CI.
- `.devcontainer/`, `.vscode/`, `README.md` and `VALIDATED-EPROMS.md`.

User documentation is only in the `firestarter` GitHub wiki. `README.md` links to it.

You can write comments in product source in both sub-repos. Many files in `.planning/` refer to an
old rule that did not allow comments. The operator removed that rule on 2026-09-19. Ignore those
references.

### Submodule URLs at old refs

`.gitmodules` records a submodule URL in each commit. Two kinds of ref still put the firmware at the
path `firestarter` with the old URL:

- The `main` branch of this repository.
- Each ref from before the firmware rename, for example `v1.35`.

At such a ref, a plain `git submodule update --init` clones *this* repository and stops with exit
code 128. Set the URL override BEFORE the first update. After a clone fails, the override alone does
not recover it. `.planning/notes/gitmodules-archaeology-trap.md` gives the workarounds and the
`git submodule sync` hazard.

## System Overview

Firestarter programs EPROM, Flash and SRAM devices. It uses an Arduino and the RURP
(Relatively-Universal-ROM-Programmer) shield. The system has two parts:

1. **Python CLI** (`firestarter_app/`) — runs on the host PC. It parses user commands, finds chip
   specs in a JSON database, and controls each operation over serial.
2. **Arduino firmware** (`firestarter_fw/`) — runs on the Arduino. It receives commands, drives
   the hardware bus, and sends data back through a three-phase state machine (INIT → MAIN → END).

The serial link runs at 250000 baud. The host sends each command as COBS-framed JSON with a CRC8.
The firmware sends INIT, MAIN, END and status messages as catalog message ID frames. It still sends
`OK:` and `DATA:` as text lines.

## Writing Style (ASD-STE100)

Use the `asd-ste100` skill when you write or change the text below. Do not use it for `.planning/`.

- **Strict mode:**
  - The `CLAUDE.md` files in all three repositories.
  - Message text in `tools/catalog/messages.toml`.
  - CLI `--help` text, which includes Click docstrings.
  - Error and log strings in product source.
  - Skill, agent and command prompts in `.claude/`.
- **STE-flavored mode:** `README.md`, `CONTRIBUTING.md`, the issue templates, wiki pages, and PR
  descriptions.

Before you commit the text, run the linter on each changed file:

```bash
python3 .claude/skills/asd-ste100/scripts/ste-lint.py <file>
```

The linter can flag a word that has a different function, for example "fixed" as an adjective, or
"verify" as a command name. Examine each finding. Do not change accurate text only to make the
linter pass.

## Development Commands

The `CLAUDE.md` file of each sub-repo gives its build, test and CI commands. Do not copy them here.

## Cross-repo obligations

Each item below applies to both sub-repos. Neither sub-repo can state it alone.

- **Serial protocol.** Keep `firestarter_app/firestarter/serial_comm.py` and
  `firestarter_fw/src/firestarter.cpp` the same when you change the protocol.
- **Constants and flag bits.** `firestarter_app/firestarter/constants.py` duplicates values from
  firmware headers and from `firestarter_fw/src/json_parser.c`. The Constants section of
  `firestarter_app/CLAUDE.md` has the table. Change both sides in the same pair of commits.
- **Messages.** `tools/catalog/messages.toml` is the source of truth. Codegen runs only in this
  repository. Both sub-repos use the synced output. Never generate or edit `messages.h` or
  `messages.py` inside a sub-repo.
- **Data buffer size.** The firmware sets `DATA_BUFFER_SIZE` for each board: 512 by default, 1024
  on Leonardo. The firmware sends the value in its `MSG_OK_READY` ack. The host sizes its chunks
  from that value. If the ack has no value, the host uses 512.

## Milestone close and branch protection

- **Start milestone work from `beta` in all three repositories.** Name the branch `v1.X-slug`. If
  the PRs of the previous milestone are not merged, start from the branch of that milestone.
  Never commit to `beta` or `main` directly.
- **A push to `beta` in a sub-repo PUBLISHES. Treat it as a release, not a merge.**
  - `firestarter_fw` — `beta-build.yml` creates a GitHub pre-release with the `.hex` assets.
  - `firestarter_app` — `beta-release.yml` creates a GitHub pre-release. Its `pypi` job then calls
    `publish.yml` directly and **uploads to PyPI**.
  - Neither workflow has a path filter. A documentation-only push publishes too.
  - PyPI never accepts the same version two times. Decide the scope of a beta push before you push.
- **A push to `main` in `firestarter_fw` publishes a stable release.** `build.yml` does this.
- **No rule protects `beta` in any of the three repositories.** A direct push, a force-push and a
  deletion all succeed. Only the publish consequence above stops a mistake.
- **The "Protect main" ruleset protects `main` in all three repositories.** It requires a pull
  request and blocks force-push and deletion. Only a deploy key can bypass it.
- **The milestone close targets `beta`, not `main`.** `.planning/config.json` sets
  `git.base_branch` to `beta`, so `/gsd-complete-milestone` and `/gsd-ship` both use `beta`.
- **Before you run `/gsd-ship`, make local `beta` again from `origin/beta`.** `workflows/ship.md`
  sets its audit range with `RANGE_BASE=$(git merge-base "${BASE_BRANCH}" HEAD)`. A stale local
  `beta` makes that range too wide.
- **Never publish a GitHub Release from the meta repository. Push bare milestone tags only.** PEP
  440 reads a tag like `v1.36` as `1.36`. `Version("3.0.0b29") >= Version("1.36")` is then true, so
  `fw` tells each stranded CLI that its firmware is up to date. Read
  `.planning/notes/999.9-repo-rename-impact-analysis.md`, section "Standing rule this must produce".
- `.planning/notes/v135-close-procedure-under-protection.md` gives the close procedure and the
  blocked route to a stable release.
