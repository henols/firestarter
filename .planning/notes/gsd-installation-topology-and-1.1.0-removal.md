# GSD installation: one project-local install, and the removal of a dangerous global 1.1.0

**Date:** 2026-09-08
**Raised during:** `/gsd-explore "what files and directories can safely be removed from this project?"`
**Operator ruling:** *"the 1.1.0 must be removed it is dangerous. And only one installation of gsd can be installed."*
**Method:** direct measurement in the devcontainer. Every figure below came from a command run in that session.

## What was found

Two functional GSD installations, plus two inert artifacts.

| Path | Version | Status |
|---|---|---|
| `/workspaces/.claude/gsd-core` | 1.13.0 | live, correct |
| `/home/vscode/.claude/get-shit-done` | **1.1.0** (2026-05-25) | **REMOVED** — see below |
| `/home/vscode/.npm/_npx/…/@opengsd/gsd-core` | 1.13.0 | npx download cache, harmless |
| `/workspaces/.claude/gsd-local-patches/gsd-core` | 1.6.1 fragment | one-file backup; a trap, see below |

**1.13.0 is the newest published release** — `npm view @opengsd/gsd-core version` returns 1.13.0, so
there was nothing to update to. "Update GSD to make it solid" was not an available fix.

**The 1.13.0 install is faithful to what the GSD team shipped.** All 327 markdown files were diffed
against the pristine npm package; every difference is one of five installer transformations
(`@~/.claude/` and bare `~/.claude/` path rewrites, `/gsd:` -> `/gsd-` command style, the
`CLAUDE_CONFIG_DIR` default, and `<!-- gsd:section when="flag:…" -->` blocks pruned for features not
enabled here). **Zero injected instruction content.** The 72 commands match `commands/gsd/*` exactly.

## Why the 1.1.0 install was genuinely dangerous, not merely stale

Its runtime was unreachable — every launcher probe looks for `<dir>/gsd-core/bin/gsd-tools.cjs` and
it lived at `get-shit-done/bin/`; `gsd_run` was not on PATH; `CLAUDE_CONFIG_DIR` was unset and the
installer had rewritten the default to `/workspaces/.claude`. That part was dead weight.

**The hooks were not.** Its own 424-entry manifest claimed 15 files under `hooks/`, and
`~/.claude/settings.json` had **10 of them wired and executing**:

| event | matcher | hook |
|---|---|---|
| SessionStart | — | `gsd-check-update.js`, `gsd-session-state.sh` |
| PreToolUse | `Write\|Edit` | `gsd-prompt-guard.js`, `gsd-read-guard.js`, `gsd-workflow-guard.js` |
| PreToolUse | `Bash` | `gsd-validate-commit.sh` |
| PostToolUse | `Bash\|Edit\|Write\|MultiEdit\|Agent\|Task` | `gsd-context-monitor.js` |
| PostToolUse | `Read` | `gsd-read-injection-scanner.js` |
| PostToolUse | `Bash` | `gsd-graphify-update.sh` |
| PostToolUse | `Write\|Edit` | `gsd-phase-boundary.sh` |

Plus `statusLine` -> `gsd-statusline.js`. Most read `/workspaces/.planning/` **directly**, with
May-2026 logic, and three were `PreToolUse` guards able to **block** writes.

**All ten were duplicates.** The project already wires 19 hook invocations from its own 1.13.0
`hooks/` via `settings.local.json`, and Claude Code merges user- and project-level hooks — so every
`Write`/`Edit` ran through two guard sets, one seven releases old:

| hook | global 1.1.0 | project 1.13.0 |
|---|---|---|
| `gsd-workflow-guard.js` | 94 L | 388 L |
| `gsd-prompt-guard.js` | 97 L | 231 L |
| `gsd-statusline.js` | 537 L | 1081 L |

**Zero hooks existed only globally**, so removal cost no capability.

**And its skills were shadowing the project.** 67 `gsd-*` skill directories, **58 of them completely
empty**. GSD's own installer confirmed the effect in its output: *"67 triggers shadowed: the local
commands surface is unreachable through those triggers — global skills wins instead."* All 67 have
local command equivalents, verified name by name, including the 9 non-empty ones
(`gsd-graphify`, `gsd-ns-*`, `gsd-review-backlog`, `gsd-workstreams`).

## What was done

1. `statusLine` repointed at `/workspaces/.claude/hooks/gsd-statusline.js` (the only thing provided
   solely by the global install; the project copy is twice the size).
2. The whole `hooks` block deleted from `~/.claude/settings.json`, preserving
   `extraKnownMarketplaces`, `effortLevel`, `tui`, `theme`, `agentPushNotifEnabled`,
   `remoteControlAtStartup`.
3. `npx -y --package=@opengsd/gsd-core@1.13.0 -- gsd-core --claude --local` re-run from
   `/workspaces`. Note: **a `--local` install deliberately installs no skills** — for a local
   install the `/gsd-*` surface is `commands/`, which is why the global skill stubs shadowed it.
4. Removed from `~/.claude`: `get-shit-done/` (309 files), `agents/` (33, all `gsd-*`), `hooks/`
   (15, all `gsd-*`), `gsd-migration-journal/`, `skills/gsd-*` (67 dirs),
   `gsd-file-manifest.json`, `gsd-install-state.json`, `.gsd-profile`. **361 files + 67 dirs.**
5. Preserved and verified after: `.credentials.json`, `CLAUDE.md`, `skills/graphify`,
   `settings.json`, `sessions/`, and `projects/-workspaces/memory/` (278 files).
6. The install pinned in `.devcontainer/post-create.sh` at `GSD_VERSION=1.13.0`. It previously
   installed graphify but **not** GSD, which is why the install was hand-made and its drift went
   unnoticed for months.

`~/.claude/settings.json` backed up at
`scratchpad/gsd-removal-backup/settings.json.bak` alongside the old manifest (session-scoped).

## Why project-local, not global

- **Exactly one GSD project exists on this machine.** `firestarter/` has no `.planning/`;
  `firestarter_app/.planning` holds only `codebase/` and `config.json`. Global's one real
  advantage does not apply.
- **Global is empirically what rotted** — every defect above lived there; the project install was clean.
- **Version pinning matters here.** `.planning/config.json` is project-scoped
  (`nyquist_validation: false`); a global upgrade driven by unrelated work would shift this
  project's workflow mid-milestone.
- **No durability penalty.** `/workspaces` is a host bind mount
  (`/dev/nvme0n1p4[/henrik/dev/henrik/git/firestarter_prom]`), so a local install survives
  container rebuilds exactly as a global one would.

**Both `/workspaces` and `/home/vscode/.claude` are host bind mounts** — the removal changed the
host's `~/.claude`, not just this container. No other host directory is mounted, so no other
project's GSD install was ever reachable.

## `gsd-local-patches` — one real patch, now obsolete, still a trap

Correcting a wrong belief recorded earlier: this was **not** a false positive. A real modification
existed, in `gsd-core/bin/lib/model-resolver.cjs` against **1.6.1**. Proven by fetching pristine
1.6.1 from npm: its sha256 matches `backup-meta.json`'s recorded `pristine_hashes` exactly, and the
backed-up copy differs from it by **+16 lines**:

- imported `resolveRuntimeNameFromCandidates` from `runtime-name-policy.cjs`
- added `resolveModelRuntime(config)` detecting Codex via `CODEX_SESSION_ID` / `CODEX_THREAD_ID`
- rewired three `config['runtime']` call sites through it, and exported it

Its own comment states the goal: *"so a shared Claude/Codex project does not need a
provider-pinning `runtime` key in .planning/config.json."*

**Obsolete.** 1.13.0 reaches the same goal at `model-resolver.cjs:74` via
`readInstallRuntimeMarker()` reading `.gsd-runtime` (which is `claude` here). The live file is
**byte-identical to pristine 1.13.0** — no patch is applied.

**The trap is real and the installer keeps advertising it.** It re-detected the patch during this
session's install and again printed *"Run `/gsd-update --reapply` to merge them."* Doing so would
overwrite the live **839-line** file with the **483-line** 1.6.1 copy — **losing 356 lines** across
seven releases, including the install-marker resolution path itself. **Never run
`/gsd-update --reapply` in this project.** What is false is the recommendation, not the patch.
