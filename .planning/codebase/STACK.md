---
last_mapped_commit: b1311abd
last_mapped_at: 2026-09-14T04:59:59.314Z
mapped_paths: .claude,.devcontainer,.github,.gitignore,.gitmodules,.vscode,CLAUDE.md
---
# Technology Stack

**Analysis Date:** 2026-09-14 (meta-repo / dev-environment layer)
**Prior analysis:** 2026-05-08 (submodule layer — preserved below, not re-verified this run)

## Repository Shape

This is the **meta / planning repo** (`/workspaces`, GitHub `henols/firestarter_prom`). It tracks
only `.planning/` (GSD artifacts) and `.claude/skills/`. The two code repos are git submodules
declared in `.gitmodules`:

| Submodule path | Remote | Contents |
|----------------|--------|----------|
| `firestarter_fw/` | `git@github.com:henols/firestarter_fw.git` | Arduino/AVR C++ firmware (PlatformIO) |
| `firestarter_app/` | `git@github.com:henols/firestarter_app.git` | Python host CLI (pip package) |

The submodule's own name and path are still `firestarter` — only the remote was repointed at the
`firestarter_fw` rename (v1.38). Guidance for both is in `CLAUDE.md` (77 lines) plus each
submodule's own `CLAUDE.md`.

---

# Part 1 — Meta-repo / dev environment (verified 2026-08-26)

## Development Container

**Definition:** `.devcontainer/devcontainer.json`, `.devcontainer/Dockerfile`,
`.devcontainer/devcontainer-lock.json`

**Base image:** `mcr.microsoft.com/devcontainers/python:3.12`

> Note: the container ships **Python 3.12**, while the host app's CI targets Python 3.11.
> This mismatch is a known source of masked CI failures — create a 3.11 venv inside the
> container for anything CI-comparable.

**apt packages added** (`.devcontainer/Dockerfile`):
- `udev`, `libusb-1.0-0` — serial/USB device support
- `avrdude` — AVR flashing (required at runtime by the host CLI's `fw` command)
- `unzip` — needed by the Bun installer

**pip-installed system-wide in the image:**
- `platformio` — firmware build/upload/test CLI (present: PlatformIO Core 6.1.19)
- `uv` — used to install other tooling
- `graphifyy` (via `uv pip install --system`) — knowledge-graph tool backing
  `/gsd-graphify` (present: graphify 0.9.50)

**Bun:** installed by the official `https://bun.sh/install` script with
`BUN_INSTALL=/usr/local`, so the binary is at `/usr/local/bin/bun` and resolvable from
non-login, non-interactive shells (present: 1.4.0). It was installed solely because the
Discord channel plugin's MCP server declares the bare command `bun`. **That plugin was
removed 2026-08-26 (commit `3e2f7d89`), so this install is now vestigial** — nothing else
in the repo uses Bun. The `Dockerfile` lines were deliberately left in place.

**Devcontainer features** (pinned by digest in `.devcontainer/devcontainer-lock.json`):
- `ghcr.io/devcontainers/features/github-cli:1` @ 1.1.0 — `gh` CLI
- `ghcr.io/devcontainers/features/node:1` @ 1.7.1, `version: 22` (present: Node v22.23.2)
- `ghcr.io/anthropics/devcontainer-features/claude-code:1` @ 1.0.5

**Hardware access:** `runArgs: ["--privileged"]` plus a `/dev` bind mount; `vscode` is added
to the `dialout` group. This is what makes real serial access to the Arduino programmer
possible from inside the container.

**Named volumes** (survive a container rebuild): `firestarter-platformio` →
`~/.platformio`, `firestarter-config` → `~/.config`, `firestarter-pip-cache` →
`~/.cache/pip`, `firestarter-claude` → `~/.claude`.

**Environment set by the container:**
- (`containerEnv.DISCORD_STATE_DIR` removed 2026-08-26, commit `3e2f7d89`; `containerEnv` had no other keys and is gone)
- `remoteEnv.PATH` appends `/home/vscode/.local/bin` (pip user scripts, incl. the
  `firestarter` entry point)

**Workspace layout:** `workspaceMount` binds the repo root at `/workspaces` and
`workspaceFolder` is `/workspaces`, so `firestarter_fw/`, `firestarter_app/` and `.planning/`
are all top-level.

**ARM toolchain:** not installed in the image. (`arm-none-eabi` is absent; it is
installable on demand but is not part of the provisioned stack.)

## Post-create provisioning

`.devcontainer/post-create.sh` (run via `postCreateCommand`, 22 lines) performs, in order:

1. `python3 .devcontainer/gen-platformio-ini.py` — generates the repo-root
   `platformio.ini` wrapper (gitignored) that redirects `src_dir`/`include_dir`/`lib_dir`/
   `test_dir`/`build_dir` into `firestarter_fw/`, so PlatformIO IDE works from the root.
2. `pip install -e /workspaces/firestarter_app` — editable install of the host CLI.
3. `cd /workspaces/firestarter && pio pkg install` — firmware library deps.
4. `graphify install` — installs the graphify skill/references into the `~/.claude` volume.
5. `npx -y --package=@opengsd/gsd-core@1.13.0 -- gsd-core --claude --local` — installs GSD
   project-locally, pinned to a fixed version. GSD is deliberately **not** installed globally;
   a prior global 1.1.0 install was removed.

Steps that previously provisioned the Discord channel plugin (state dir,
`enabledPlugins`/`extraKnownMarketplaces` config-as-code, and repointing the plugin's
`.mcp.json` at `discord-singleton.sh`) were **removed 2026-08-26, commit `3e2f7d89`**.

## Agent tooling runtime (`.claude/`)

**Tracked vs local — this split matters.** `.gitignore` ignores `.claude/*` with a single
un-ignore for `!.claude/skills/`. Only **8 files** are tracked under `.claude/`:

- `.claude/skills/devtest-triage/` — `SKILL.md`, `fixtures/*.md` (2 files),
  `scripts/devtest_issues.py`, `scripts/eprom_families.py`
- `.claude/skills/devtest-rootcause/` — `SKILL.md`, `scripts/infoic_lookup.py`,
  `scripts/diff_db.py`

Everything else under `.claude/` is **local runtime state** and is not reproducible from
this repo alone:
- `.claude/gsd-core/` — vendored GSD runtime, VERSION `1.13.0` (project-local install,
  pinned by `.devcontainer/post-create.sh`; global installs are deliberately not used);
  entry points `.claude/gsd-core/bin/gsd-tools.cjs`, `check-latest-version.cjs`,
  `verify-reapply-patches.cjs`, plus `workflows/`, `templates/`, `contexts/`, `references/`
- `.claude/agents/` — 35 GSD subagent definitions (`gsd-planner.md`, `gsd-executor.md`,
  `gsd-codebase-mapper.md`, …)
- `.claude/hooks/` — 30 Node (`.js`/`.cjs`) and Bash hook scripts
  (`gsd-workflow-guard.js`, `gsd-validate-commit.sh`, `gsd-statusline.js`, …)
- `.claude/commands/`, `.claude/scripts/changeset`, `.claude/worktrees/`
- `.claude/package.json` — `{"type":"commonjs"}`, which is what lets the `.js` hooks load
- `.claude/settings.json` — keys: `permissions`, `remoteControlAtStartup`, `autoMode`
- `.claude/settings.local.json` — keys: `permissions`, `hooks` (SessionStart, PostToolUse,
  PreToolUse, SubagentStop, Stop, PreCompact, FileChanged), `worktree`,
  `extraKnownMarketplaces`
- ~~`.claude/channels/discord/`~~ — Discord bridge state, **deleted 2026-08-26** (commit
  `3e2f7d89`) along with `.claude/channels/`. One copy of the bot token survives at
  `~/.claude/channels/discord/.env`, outside the repo and **not revoked** — never read or
  transcribe it.
- `.claude/.gsd-profile` (`full`), `.claude/gsd-file-manifest.json`,
  `.claude/gsd-install-state.json`, `.claude/gsd-migration-journal`

**Marketplace-installed skills are deliberately NOT vendored** (`.gitignore`):
`.claude/skills/find-skills/` (carries `source.json`) and `.claude/skills/skill-creator`
(a symlink into `.agents/skills/`, installed by `npx skills add anthropics/skills@…`).
`.agents/` and `skills-lock.json` are ignored too.

**Tracked skill script dependencies:** stdlib only (`subprocess`, `json`, `urllib`, `ast`,
`xml`, `pathlib`, `argparse`, …) — no third-party imports. `devtest_issues.py` shells out
to `gh` with a fixed argv list (never a shell).

## VS Code configuration

- `.vscode/c_cpp_properties.json` and `.vscode/launch.json` are **PlatformIO
  auto-generated** and contain absolute host paths (`/home/henrik/...`) — machine-specific,
  regenerated by PlatformIO, do not hand-edit. They record the AVR build reality: `avr-gcc`
  from `toolchain-atmelavr`, `gnu11`/`gnu++11`, `-mmcu=atmega328p`, `F_CPU=16000000L`, and
  defines `MONITOR_SPEED=250000`, `HARDWARE_REVISION`, `DEV_TOOLS`,
  `RURP_BOARD_NAME="uno"`, `SERIAL_ON_IO`.
- `.vscode/extensions.json` — recommends `platformio.platformio-ide`; explicitly
  **unwants** `ms-vscode.cpptools-extension-pack`.
- `.vscode/settings.json` — a single machine-local `clang-tidy` path.
- Devcontainer-installed extensions (`devcontainer.json`): `ms-python.python`,
  `ms-python.pylint`, `ms-python.black-formatter`, `platformio.platformio-ide`,
  `anthropic.claude-code` (pinned to `workspace` extension kind). Format-on-save is on with
  black as the Python formatter.

## Generated / ephemeral artifacts (from `.gitignore`)

Useful as a map of what is regenerable and must never be committed:
- `platformio.ini` at the repo root (generated by `gen-platformio-ini.py`), `.pio/`
- `__pycache__/`, `*.py[cod]`
- Knowledge graphs: `.planning/graphs/graph.json`,
  `.planning/graphs/.last-build-snapshot.json`, `graphify-out/` (only
  `.planning/graphs/GRAPH_REPORT.md` is tracked)
- `.planning/research/.cache/` — researcher web/Context7 fetch cache
- Bench/diagnostic output: `firestarter-runs/`, `consistency-check-*/`, `write-cycle-*/`,
  `chip-test/`, root-level `/*.bin`
- Extra submodule worktrees: `firestarter_app_py32/`, `firestarter_py32_ci/`
- `node_modules`, `skills-lock.json`, root `/package.json` + `/package-lock.json`
- `.planning/milestones/v1.7-artifacts/**` except directories and `.md` files; `.planning/milestones/v1.7-artifacts/upstream-rurp`
  is ignored in **both** the bare and trailing-slash forms (the bare form is what prevents
  it being recorded as an orphan gitlink)

---

# Part 2 — Submodule stacks (from 2026-05-08 analysis; not re-verified this run)

All statements in this part are carried forward verbatim from the prior mapping and are
`[unverified in 2026-08-26 scoped remap]`.

## Languages

**Primary:**
- Python 3.11+ - Host application (CLI tool, `firestarter_app/`)
- C/C++ (Arduino/AVR) - Firmware (`firestarter_fw/src/`)

**Secondary:**
- Bash - Integration/test scripts (`firestarter_test.sh`, `write_test.sh`)
- Python (scripting) - Build helper (`name_firmware.py`), CI version scripts

## Runtime

**Environment:**
- Python 3.11+ (classifiers: 3.11-3.12; CI tests 3.11; system Python 3.13 present in dev)
- Arduino AVR microcontroller (ATmega328P / ATmega32U4)

**Package Manager:**
- pip with virtualenv (`.venv/` present in `firestarter_app/`)
- Lockfile: not present (only `requirements.txt` and `pyproject.toml`)

## Frameworks

**Core:**
- setuptools >= 45 - Python packaging
- setuptools_scm >= 6.2 - Version management from git tags
- Arduino framework (via PlatformIO) - Firmware build target

**Testing:**
- Bash test scripts (`firestarter_test.sh`, `write_test.sh`) - Hardware integration tests (require physical hardware)
- PlatformIO `pio test` - Firmware unit tests

**Build/Dev:**
- PlatformIO - Firmware build, upload, and test system for Arduino targets
- `python3 -m build` - Python wheel/sdist packaging (used in CI)

## Key Dependencies

**Critical:**
- pyserial >= 3.5 - Serial communication with Arduino programmer hardware
- requests >= 2.20 - HTTP client for fetching firmware releases from GitHub API
- tqdm >= 4.60 - Progress bars for read/write operations
- argcomplete >= 3.6.2 - Bash/shell tab-completion for CLI
- rich >= 14.0 - Rich terminal output (confirmation prompts via `rich.prompt.Confirm`)

**Infrastructure:**
- jsmn (vendored C lib, `firestarter_fw/lib/`) - Lightweight JSON parser used in firmware
- avrdude (external system tool) - Required at runtime for flashing firmware to Arduino
  (provisioned in the devcontainer image — verified 2026-08-26)
- Arduino standard library (`<Arduino.h>`) - Firmware hardware abstraction

## Configuration

**Environment:**
- User config directory: `~/.firestarter/` (JSON files)
- Configurable via `firestarter config` CLI command
- Key runtime config: serial port, baud rate (250000), hardware revision, resistor calibration values (R1/R2)
- EPROM database overrides: `~/.firestarter/database.json` and `~/.firestarter/pin-maps.json`

**Build:**
- `firestarter_app/pyproject.toml` - Python package metadata, dependencies, entry points
- `firestarter_fw/platformio.ini` - Firmware build environments and flags
- Build flags: `MONITOR_SPEED`, `HARDWARE_REVISION`, `DEV_TOOLS`, `SERIAL_DEBUG` (opt-in), `DATA_BUFFER_SIZE`

## Platform Requirements

**Development:**
- Python 3.11+ with pip
- PlatformIO CLI (for firmware development)
- avrdude (for firmware flashing)
- Physical RURP Arduino shield hardware for integration testing

**Production:**
- Cross-platform Python application (OS Independent per PyPI classifiers)
- Arduino Uno or Leonardo with RURP shield
- USB serial port access

---

*Meta-repo / dev-environment analysis: 2026-09-14. Submodule stack analysis: 2026-05-08.*
