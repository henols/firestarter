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

- **The meta repository must never publish a GitHub Release — bare milestone tags only.** A meta
  release such as `v1.42` makes `fw` report the firmware as up to date for every older CLI,
  silently and permanently.
- **A version-tag push in either sub-repo PUBLISHES.** For the app it also uploads to PyPI, and a
  PyPI version can never be reused. Push a version tag only when the operator asks for a release.

To make a release, use the `release` skill. `RELEASING.md` is the runbook for a person.

Each sub-repo has one working branch, `main`. Branch from `main` and open pull requests to `main`.
`main` is the 3.3 line: the binary command frame and the firmware offload. A merge to `main`
publishes nothing. The tag is the version: no file holds it. The two sub-repos release
independently.

## System Overview

Firestarter programs EPROM, Flash and SRAM devices. It uses an Arduino and the RURP
(Relatively-Universal-ROM-Programmer) shield.

## Writing Style (ASD-STE100)

Use the `asd-ste100` skill when it is relevant.
