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
- **A push to `beta` in either sub-repo PUBLISHES.** Neither trigger has a path filter, so a
  documentation-only push cuts a pre-release and uploads a new PyPI version. A PyPI version can
  never be reused. Decide the scope of a beta push before making it.

A push to `main` currently publishes **nothing**: the version-bump auto-commit is rejected by the
`Protect main` ruleset and aborts the job before the release step. Do not read that as a safety
net — it is a broken release path that fails closed, and it re-arms the moment the bump is fixed.
`RELEASING.md` has the detail and the promotion runbook.

## System Overview

Firestarter programs EPROM, Flash and SRAM devices. It uses an Arduino and the RURP
(Relatively-Universal-ROM-Programmer) shield. The system has two parts:

1. **Python CLI** (`firestarter_app/`)
2. **Arduino firmware** (`firestarter_fw/`)

## Writing Style (ASD-STE100)

Use the `asd-ste100` skill when it is relevant.
