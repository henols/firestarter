---
last_mapped_commit: b1311abd
last_mapped_at: 2026-09-14T04:59:59.314Z
mapped_paths: .claude,.devcontainer,.github,.gitignore,.gitmodules,.vscode,CLAUDE.md
---
# External Integrations

**Analysis Date:** 2026-09-14 (meta-repo / dev-environment layer)
**Prior analysis:** 2026-05-08 (submodule layer — preserved below, not re-verified this run)

---

# Part 1 — Meta-repo integrations (verified 2026-09-14)

## Git remotes & submodules

`.gitmodules` declares two SSH submodule remotes:
- `firestarter` → `git@github.com:henols/firestarter_fw.git` (submodule name and path both
  remain `firestarter`; only the remote was repointed at the v1.38 rename)
- `firestarter_app` → `git@github.com:henols/firestarter_app.git`

SSH (not HTTPS) means local submodule operations require an SSH key/agent.

The meta repository has **no `.github/workflows/` directory at all** — `.github/` holds only
`CONTRIBUTING.md` and an `ISSUE_TEMPLATE/` directory of four files (`bug-report.yml`,
`config.yml`, `dev-test-report.md`, `feature-request.yml`). There is no meta-repo CI.

## GitHub API / `gh` CLI (agent tooling)

- The `gh` CLI is provisioned by the `ghcr.io/devcontainers/features/github-cli:1`
  devcontainer feature.
- `.claude/skills/devtest-triage/scripts/devtest_issues.py` drives the GitHub **Issues**
  API through `gh` with a fixed argv list (never a shell), for triaging community
  `dev test` chip-validation reports.
- `.claude/skills/devtest-triage/SKILL.md` and
  `.claude/skills/devtest-rootcause/SKILL.md` both instruct `gh issue`/`gh api` usage.
- Auth: whatever credential `gh auth` holds in the container (`~/.config`, a named volume).
  No token is stored in this repo.

## Upstream data oracle — minipro `infoic.xml`

`.claude/skills/devtest-rootcause/scripts/infoic_lookup.py` downloads and caches
(~17.8 MB) a **commit-pinned** upstream catalog:

```
https://gitlab.com/DavidGriffith/minipro/-/raw/a8efaedc236c1d9718bd28299dfbb99536b010ff/infoic.xml
```

The pin must match `build_db.py:MINIPRO_XML_URL` in the host app; the script has a
`--check`/DRIFT mode that fails when the two disagree. Unauthenticated GitLab raw fetch.

## Container image & package registries pulled at build time

`.devcontainer/Dockerfile` / `.devcontainer/devcontainer.json` reach out to:
- **Microsoft Container Registry** — `mcr.microsoft.com/devcontainers/python:3.12`
- **Debian apt repositories** — `udev`, `libusb-1.0-0`, `avrdude`, `unzip`
- **PyPI** — `platformio`, `uv`, and `graphifyy` (the last via `uv pip install --system`)
- **bun.sh** — `curl -fsSL https://bun.sh/install`, installed to `/usr/local`
- **GHCR (devcontainer features)**, digest-pinned in `.devcontainer/devcontainer-lock.json`:
  `ghcr.io/devcontainers/features/github-cli:1`,
  `ghcr.io/devcontainers/features/node:1`,
  `ghcr.io/anthropics/devcontainer-features/claude-code:1`
- **PlatformIO package registry** — via `pio pkg install` in `post-create.sh`
  (AVR toolchain + Arduino framework land in the `firestarter-platformio` volume)
- **VS Code Marketplace** — the five extensions listed in `devcontainer.json`

## Claude Code plugin marketplaces & skill installers

- `.claude/settings.local.json` registers `extraKnownMarketplaces` →
  `claude-plugins-official` from `https://github.com/anthropics/claude-plugins-official.git`,
  Previously it also enabled `discord@claude-plugins-official` and `post-create.sh`
  rewrote both entries idempotently; the Discord plugin was disabled and that
  provisioning block deleted on 2026-08-26 (commit `3e2f7d89`). The marketplace
  registration remains — it is generic, not Discord-specific.
- `.gitignore` documents two **marketplace-installed, deliberately un-vendored** skills:
  `.claude/skills/find-skills/` (carries `source.json`) and
  `.claude/skills/skill-creator` (installed via
  `npx skills add anthropics/skills@skill-creator`, real files under `.agents/skills/`).
  Reinstall rather than commit them. `skills-lock.json` is the `npx skills` manifest and
  stays local.
- An untracked root `package.json` pins `@mastra/mcp-docs-server` (npm), so npm is a
  further registry in play for MCP docs tooling.

## Discord bot bridge — **REMOVED 2026-08-26** (commit `3e2f7d89`)

The repo previously ran an inbound/outbound Discord DM bridge via the official Claude Code
`discord` channel plugin (MCP server on Bun), with a bot token on the host bind mount and an
`flock` single-instance gate. **It has been removed**: the plugin is disabled, the workspace
state dir `.claude/channels/discord/` is deleted, and the tracked re-provisioning wiring in
`post-create.sh` / `devcontainer.json` plus `.devcontainer/discord-singleton.sh` are gone.

Residual, outside this repo and NOT yet removed:
- `~/.claude/channels/discord/.env` — the last remaining copy of the bot token. The plugin
  falls back to this path when `DISCORD_STATE_DIR` is unset, so it is a live re-activation
  path. Deleting the file does **not** revoke the credential; that requires a token reset in
  the Discord Developer Portal.
- The plugin cache at `~/.claude/plugins/cache/claude-plugins-official/discord/0.0.4/`, and
  the Bun install in `.devcontainer/Dockerfile` (which existed only for this plugin).

## Other agent-runtime services

- **graphify** (`graphifyy` on PyPI, `graphify install` in post-create) — local
  knowledge-graph builder; output at `graphify-out/` and `.planning/graphs/` (both largely
  gitignored).
- **GSD core update check** — `.claude/gsd-core/bin/check-latest-version.cjs` and the
  `.claude/hooks/gsd-check-update*.js` hooks perform a version lookup for the vendored GSD
  runtime (`.claude/gsd-core/VERSION` = `1.13.0`, installed project-locally and pinned by
  `.devcontainer/post-create.sh`).
- **Researcher fetch cache** — `.planning/research/.cache/` (gitignored) holds
  web/Context7 responses, implying outbound web + Context7 documentation lookups during
  GSD research phases.

## Meta-repo secrets inventory

| Kind | Location | Notes |
|------|----------|-------|
| Discord bot token | ~~`.claude/channels/discord/.env`~~ — deleted 2026-08-26 | a copy survives at `~/.claude/channels/discord/.env`, outside the repo; **not revoked** |
| GitHub credential | `gh` CLI store under `~/.config` (named volume) | not in repo |
| Claude Code auth | `~/.claude` (named volume `firestarter-claude`) | not in repo |
| CI secrets | none — this repo has no `.github/workflows/` | N/A |

`.claude/settings.json` declares only `permissions`, `remoteControlAtStartup` and
`autoMode` — no `env` block and no inline keys.

## Webhooks & callbacks (meta-repo)

**Incoming:** none. There is no CI in this repo to receive `push`/`pull_request` triggers.
**Outgoing:** none. (The Discord gateway client was removed 2026-08-26; it was never a webhook emitter.)

---

# Part 2 — Submodule integrations (from 2026-05-08 analysis; not re-verified this run)

All statements in this part are carried forward verbatim, with one documented exception —
the firmware repository slug in the GitHub Releases endpoint below, corrected to
`firestarter_fw` for the v1.38 rename — and are
`[unverified in 2026-08-26 and 2026-09-14 scoped remaps]`.

## APIs & External Services

**GitHub Releases API:**
- GitHub REST API - Fetches latest firmware release metadata and binary download
  - SDK/Client: `requests` (Python HTTP library)
  - Auth: None (public API, unauthenticated)
  - Endpoint: `https://api.github.com/repos/henols/firestarter_fw/releases/latest`

## Data Storage

**Databases:**
- None (no SQL/NoSQL database)
- EPROM definitions stored as JSON flat files bundled with the package:
  - `firestarter/data/database_generated.json` - Main EPROM definitions
  - `firestarter/data/database_overrides.json` - Default overrides
  - `firestarter/data/pin-maps.json` - Pin mapping configurations

**File Storage:**
- Local filesystem only
- User config/override directory: `~/.firestarter/`
- Firmware binaries downloaded to `~/.firestarter/` on install
- EEPROM on Arduino stores hardware calibration config (persistent across power cycles)

**Caching:**
- None

## Authentication & Identity

**Auth Provider:**
- None - no user authentication
- GitHub API accessed without authentication (public repos, rate-limited at 60 req/hr)

## Monitoring & Observability

**Error Tracking:**
- None (no Sentry, Rollbar, etc.)

**Logs:**
- Python `logging` module with a custom `SingleLineStatusHandler` for single-line status updates in the terminal
- Log output to stdout; verbosity controlled via CLI flags
- Firmware logging via serial debug output (controlled by `SERIAL_DEBUG` build flag, disabled by default)

## CI/CD & Deployment

**Hosting:**
- Python package: PyPI (`https://pypi.org/project/firestarter/`)
- Firmware binaries: GitHub Releases (`.hex` files per board target)

**CI Pipeline:**
- GitHub Actions (both repos — these are the *sub-repos'* workflows, not this meta-repo's)
  - `firestarter_app`: Auto-creates patch release on push to `main`, publishes to PyPI on GitHub release
  - `firestarter` (firmware): Builds all PlatformIO environments on push to `main`, creates GitHub release with `.hex` files
  - Version management via custom Python scripts in `.github/scripts/`
  - Uses `stefanzweifel/git-auto-commit-action` for automated version commits
  - Uses `softprops/action-gh-release` for release creation
  - Uses `pypa/gh-action-pypi-publish` for PyPI publishing

## Environment Configuration

**Required env vars:**
- No required environment variables for runtime operation
- CI secrets: `PYPI_API_TOKEN` (for PyPI publishing in GitHub Actions, sub-repos only)

**Secrets location:**
- GitHub Actions repository secrets (CI only)
- No application-level secrets required

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None (the GitHub API call in `firmware.py` is a pull request for release info, not a webhook)

---

*Meta-repo integration audit: 2026-09-14. Submodule integration audit: 2026-05-08.*
