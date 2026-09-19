# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Structure

This is a meta-repo / planning repo for the Firestarter EPROM programmer project. The actual code lives in two sub-repos:

- `firestarter_fw/` — Arduino C++ firmware (PlatformIO). See `firestarter_fw/CLAUDE.md`.
- `firestarter_app/` — Python host CLI application (pip package). See `firestarter_app/CLAUDE.md`.

This repo tracks `.planning/` (GSD project management artifacts), `.claude/` (project settings), `tools/` and `.github/` (repo-level tooling and CI). Neither sub-repo is committed here. Documentation lives only in the `firestarter` GitHub wiki. No in-repo copy exists.

The `tools/wiki/` checkers validated a clone of that wiki. Commit `5426d7ef` retired them on 2026-09-02. A later commit deleted `tools/wiki/` on 2026-09-08. Its last occupant, `MIGRATION-TABLE.md`, moved to `.planning/milestones/v1.35-MIGRATION-TABLE.md` as a record of the completed migration. **No automated wiki guard exists now.**

`tools/` holds one directory:

- `tools/catalog/` — messages codegen and sub-repo sync tooling.

The PyPI per-version download-share instrument measured whether it was safe to claim the
`henols/firestarter` slug. The operator retired it on 2026-09-17, after the claim had already been
made without the trigger being met. The reason is recorded at
`.planning/notes/adoption-instrument-retirement.md`. **No instrument measures that download split
now.**

**The source-comment rule was REMOVED on 2026-09-19 by operator decision.** Comments in product
source are allowed again, in both sub-repos. This note exists because the rule ran for months and
`.planning/` is full of references to it: archived plans forbid comments, executor summaries report
comment deletions as compliance, and phase records cite it as binding. **Read all of that as
historical.** Source written before 2026-09-19 had comments deliberately stripped — notably the
roughly 6,600 lines a sweep deleted, and the 18 lines removed from `build_db.py` in Phase 197 whose
content was rescued to `.planning/notes/197-build-db-comment-provenance-rescued.md`. Their absence
is not a style anyone needs to preserve, and restoring explanatory comments to that code is allowed.

Its enforcement had already been dismantled in stages: each sub-repo ran a `planning_citation_gate.py`
in CI until both scripts and all three CI steps were removed on 2026-09-17, leaving only the per-repo
`CLAUDE.md` text and a pre-commit grep, both of which went on 2026-09-19. Restore points if any of it
is ever wanted back: the CI gates at `firestarter_fw` `876a223` and `firestarter_app` `c77ff2e`; the
rule text itself in this file and both sub-repo `CLAUDE.md` files immediately before the
2026-09-19 removal commit.

`.gitmodules` records a submodule URL per commit. Checking out a pre-rename ref such as `v1.35`, or bisecting firmware history, resurrects the old firmware URL from that commit. **Fixing the live branches does not fix history.** See `.planning/notes/gitmodules-archaeology-trap.md` for both workarounds, their executed transcripts, and the `git submodule sync` hazard that silently undoes one of them. **The trap is armed.** `henols/firestarter` was claimed for this repository on 2026-09-14, which destroyed the redirect it depended on. A plain `git submodule update --init` at a pre-rename ref now clones *this* repository into its own `firestarter/` directory and fails with exit 128. Set the override BEFORE the first update; once a clone has failed, the override alone will not recover it.

## System Overview

Firestarter is a two-part system for programming EPROMs, Flash, and SRAM devices using an Arduino-based RURP (Relatively-Universal-ROM-Programmer) shield:

1. **Python CLI** (`firestarter_app/`) — runs on the host PC; parses user commands, looks up EPROM specs from a JSON database, and orchestrates operations via serial.
2. **Arduino firmware** (`firestarter_fw/`) — runs on the Arduino; receives JSON commands, drives the hardware bus, and streams binary data back using a three-phase state machine protocol (INIT → MAIN → END).

The protocol runs at 250000 baud. Commands are JSON objects; responses are prefix-tagged lines (`OK:`, `DATA:`, `MAIN:`, `END:`, `ERROR:`).

## Development Commands

**Each sub-repo's own `CLAUDE.md` owns its build, test and CI commands.** Read
`firestarter_app/CLAUDE.md` or `firestarter_fw/CLAUDE.md` rather than a copy here. A copy in this
file drifts: it read `pip install -e .` for months after the app's CI moved to `pip install -e
'.[test]'`.

## Cross-repo obligations

These are the only architecture facts that belong in the meta repo, because each one spans both
sub-repos and neither can state it alone.

- **Serial protocol changes** must stay in sync between `firestarter_app/firestarter/serial_comm.py`
  and `firestarter_fw/src/firestarter.cpp`.
- **Constants and flag bits** are duplicated between `firestarter_app/firestarter/constants.py` and
  three firmware headers. `firestarter_app/CLAUDE.md` § Constants carries the per-block table.
  Change both sides in the same commit pair.
- **Messages are generated here and consumed there.** `tools/catalog/messages.toml` is the source of
  truth. Codegen runs in this repo only. Both sub-repos consume synced artifacts, so never
  regenerate or hand-edit `messages.h` or `messages.py` inside a sub-repo.
- **Board buffer sizes differ:** Uno has 512 bytes, Leonardo 1024. This changes chunked transfer on
  the host side, in `eprom_operations.py`.

## Milestone close and branch protection

- **Milestone work forks off `beta`, in all three repositories** — the meta repo and both sub-repos. Branch name: `v1.X-slug`. Never commit to `beta` directly. Never commit to `main`.
- **A push to `beta` in either sub-repo PUBLISHES. Treat it as a release, not a merge.**
  - `firestarter_fw` — `beta-build.yml` cuts a GitHub pre-release carrying the `.hex` assets.
  - `firestarter_app` — `beta-release.yml` cuts a GitHub pre-release, then its `pypi` job calls `publish.yml` directly with `secrets: inherit` and **uploads to PyPI**. It calls the workflow rather than relying on the `release: published` trigger, because a bot-created release cannot cascade on the default token.
  - **Neither carries a path filter**, so a documentation-only push publishes too. Verified on 2026-09-17: a docs-only push cut `firestarter_fw` `3.0.0b32` and `firestarter_app` `3.0.0b47`, and `3.0.0b47` reached PyPI.
  - A PyPI version can never be reused. Decide the scope of a beta push before making it, not after.
- **`main` is protected in all three repositories** — pull request required, no direct push, no force-push, no deletion. `current_user_can_bypass` is `never`, so no person can bypass.
- **`beta` is protected in all three repositories too, but does NOT require a pull request.** A direct push therefore succeeds. Protection is not a safety net here — the publishing consequence above is the reason to be careful.
- **This project's close targets `beta`, not `main`.** `.planning/config.json` sets `git.base_branch` to `beta`, so `/gsd-complete-milestone` and `/gsd-ship` both point there.
- **Before running `/gsd-ship`, recreate local `beta` from `origin/beta`** — `ship.md` anchors its audit range on `RANGE_BASE=$(git merge-base "${BASE_BRANCH}" HEAD)` and local `beta` goes stale. Cited by content, not line number: `workflows/ship.md` is installer-owned and a GSD version bump moves its lines.
- **The meta repository must never publish a GitHub Release — bare milestone tags only.** A tag like `v1.36` parses as PEP 440 `1.36`. `Version("3.0.0b29") >= Version("1.36")` then reads true, so `fw` reports firmware already up to date for every stranded CLI, silently and permanently. This risk is latent today and armed by a single future action. Cited by content, not line number: see `.planning/notes/999.9-repo-rename-impact-analysis.md` § "Standing rule this must produce" for the full mechanism.
- **The mechanics, the blocked stable-release route and the consumer sites are in `.planning/notes/v135-close-procedure-under-protection.md`.**
