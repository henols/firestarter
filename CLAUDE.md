# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Structure

This is a meta-repo / planning repo for the Firestarter EPROM programmer project. The actual code lives in two sub-repos:

- `firestarter_fw/` — Arduino C++ firmware (PlatformIO). See `firestarter_fw/CLAUDE.md`.
- `firestarter_app/` — Python host CLI application (pip package). See `firestarter_app/CLAUDE.md`.

This repo tracks `.planning/` (GSD project management artifacts), `.claude/` (project settings), `tools/` and `.github/` (repo-level tooling and CI). Neither sub-repo is committed here. Documentation lives only in the `firestarter` GitHub wiki. No in-repo copy exists.

The `tools/wiki/` checkers validated a clone of that wiki. Commit `5426d7ef` retired them on 2026-09-02. A later commit deleted `tools/wiki/` on 2026-09-08. Its last occupant, `MIGRATION-TABLE.md`, moved to `.planning/milestones/v1.35-MIGRATION-TABLE.md` as a record of the completed migration. **No automated wiki guard exists now.**

`tools/` holds two directories:

- `tools/catalog/` — messages codegen and sub-repo sync tooling.
- `tools/adoption/` — the PyPI per-version download-share instrument.

**Nothing mechanically enforces the source-comment rule.** Each sub-repo used to run a
`planning_citation_gate.py` in CI. Both scripts and all three CI steps were removed by operator
decision on 2026-09-17. The rule now rests entirely on the per-repo `CLAUDE.md` text and the
pre-commit check it carries. Restore points, if the gate is ever wanted back:
`firestarter_fw` `876a223`, `firestarter_app` `c77ff2e`.

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

## Source code comments — hard rule

**Write no comments into product source.** This covers everything under `firestarter_fw/` and
`firestarter_app/`, and it is not overridable by a plan, task, skill, or subagent instruction.

- Forbidden: `// Phase NNN (REQ-NN):`, `// D-06`, `// LOCK-04`, any plan, task or milestone
  citation, and any block explaining why a phase decided something. Rationale goes in the commit
  message or in `.planning/`, never in source.
- **The rule is not "no GSD citations".** You delete `Phase 194` from a comment and keep the
  comment. This still breaks the rule. Add no `#`, `//` or `/* */` line, for any reason, however
  helpful it seems. State the rule in these words when you spawn a subagent that touches source.
- **Planners:** do not write "add a comment citing X" into a plan, and do not make "a comment
  exists" an acceptance criterion. Both generate exactly what this rule forbids.
- **Executors:** if an existing plan instructs a source comment, do not add it. Record the
  deviation in the plan's `SUMMARY.md` instead.
- If code needs explaining, make the code clearer — better names, smaller functions, a named
  constant — rather than annotating it.
- Docstrings are a separate question. Click docstrings in `firestarter_app` are user-facing
  `--help` text, not commentary, and must not be treated as comments.
- Before each commit, run the check for that repo. It must print nothing. **The pathspec is
  load-bearing** — without it each pattern also matches markdown, and the check reports a file it
  does not govern:
  - Python: `git -C firestarter_app diff --cached -- '*.py' | /usr/bin/grep -E '^\+\s*#' | /usr/bin/grep -v '^\+\s*#!'`
  - C/C++: `git -C firestarter_fw diff --cached -- '*.c' '*.cpp' '*.cc' '*.h' '*.hpp' '*.inc' '*.ino' | /usr/bin/grep -E '^\+\s*(//|/\*|\*)'`
- Deleting one clause from an existing comment reflows the rest. Read the remainder. Confirm it
  still parses and that every pronoun still has an antecedent.

## Milestone close and branch protection

- **Milestone work forks off `beta`, in all three repositories** — the meta repo and both sub-repos. Branch name: `v1.X-slug`. Never commit to `beta` directly. Never commit to `main`.
- **`main` is protected in all three repositories** — pull request required, no direct push, no force-push, no deletion. `current_user_can_bypass` is `never`, so no person can bypass.
- **This project's close targets `beta`, not `main`.** `.planning/config.json` sets `git.base_branch` to `beta`, so `/gsd-complete-milestone` and `/gsd-ship` both point there.
- **Before running `/gsd-ship`, recreate local `beta` from `origin/beta`** — `ship.md` anchors its audit range on `RANGE_BASE=$(git merge-base "${BASE_BRANCH}" HEAD)` and local `beta` goes stale. Cited by content, not line number: `workflows/ship.md` is installer-owned and a GSD version bump moves its lines.
- **The meta repository must never publish a GitHub Release — bare milestone tags only.** A tag like `v1.36` parses as PEP 440 `1.36`. `Version("3.0.0b29") >= Version("1.36")` then reads true, so `fw` reports firmware already up to date for every stranded CLI, silently and permanently. This risk is latent today and armed by a single future action. Cited by content, not line number: see `.planning/notes/999.9-repo-rename-impact-analysis.md` § "Standing rule this must produce" for the full mechanism.
- **The mechanics, the blocked stable-release route and the consumer sites are in `.planning/notes/v135-close-procedure-under-protection.md`.**
