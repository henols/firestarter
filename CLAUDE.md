# CLAUDE.md

This file gives guidance to Claude Code (claude.ai/code) for work in this repository.

## Repository Structure

This is the meta repository for the Firestarter EPROM programmer project. The code is in two
submodules:

- `firestarter_fw/` — Arduino C++ firmware (PlatformIO). Read `firestarter_fw/CLAUDE.md`.
- `firestarter_app/` — Python host CLI application (pip package). Read `firestarter_app/CLAUDE.md`.

User documentation is only in the `firestarter` GitHub wiki. `README.md` links to it.

## Release Hazards

Two rules that are costly to get wrong, because getting them wrong publishes something.

- **The meta repository must never publish a GitHub Release — bare milestone tags only.** A tag
  like `v1.42` parses as PEP 440 `1.42`. `Version("3.1.1") >= Version("1.42")` then reads true, so
  `fw` reports firmware already up to date for every stranded CLI, silently and permanently. The
  risk is latent and is armed by a single future action.
- **A version-tag push in either sub-repo PUBLISHES.** A tag `X.Y.ZbN` or `X.Y.ZrcN` cuts a
  pre-release, and a tag `X.Y.Z` cuts a stable release, marked Latest when it is the highest. For the app, both upload to
  PyPI, and a PyPI version can never be reused. Push a version tag only when the operator asks for
  a release.

Each sub-repo has one working branch, `main`. Branch from `main` and open pull requests to `main`.
A fix for an older line goes to its maintenance branch `release/X.Y` instead. No `release/3.2`
branch exists: firmware `main` carries the 3.2.x line, and the 3.3 work (the binary command frame
and the firmware offload) is on `perf/fw-offload` in all three repositories. A merge to `main` or `release/X.Y` publishes nothing. The tag is the version: no file holds it, and no bot commits a bump.
The two sub-repos release independently. `RELEASING.md` has the runbook.

## System Overview

Firestarter programs EPROM, Flash and SRAM devices. It uses an Arduino and the RURP
(Relatively-Universal-ROM-Programmer) shield. The system has two parts:

1. **Python CLI** (`firestarter_app/`)
2. **Arduino firmware** (`firestarter_fw/`)

## Writing Style (ASD-STE100)

Use the `asd-ste100` skill when it is relevant.
