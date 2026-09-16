---
last_mapped_commit: b1311abd
last_mapped_at: 2026-09-14T04:59:59.314Z
mapped_paths: .claude,.devcontainer,.github,.gitignore,.gitmodules,.vscode,CLAUDE.md
---
# Architecture

**Analysis Date:** 2026-05-08 (submodule sections) / 2026-09-14 (meta-repo sections)

> **Scope note.** The 2026-08-26 and 2026-09-14 remaps were scoped to the meta-repo's own
> tracked infrastructure (`.claude`, `.devcontainer`, `.github`, `.vscode`, `.gitignore`,
> `.gitmodules`, `CLAUDE.md`). Sections describing the two submodules
> (`firestarter_fw/`, `firestarter_app/`) date from 2026-05-08 and were not re-verified;
> they are marked `[unverified in 2026-08-26 and 2026-09-14 scoped remaps]`.

## Pattern Overview

**Overall:** Layered CLI application with hardware abstraction and singleton service objects, communicating with embedded firmware via a JSON-over-serial state machine protocol.

The repository is a **meta-repo with two git submodules** (`.gitmodules`), not a monorepo. The meta-repo itself tracks only planning and agent-tooling artifacts; both code sub-projects are gitlinks pointing at independent GitHub repos:
1. `firestarter_app/` - Python host-side CLI application (pip package)
2. `firestarter_fw/` - Arduino C++ firmware for the RURP shield (PlatformIO project)

**Key Characteristics:**
- Singleton pattern for shared services (EpromDatabase, ConfigManager)
- Command-pattern CLI dispatch via argparse subparsers in `main.py`
- Three-phase state machine protocol (INIT / MAIN / END) for all hardware operations
- Hardware abstraction separates EPROM operations, hardware management, and firmware management into distinct manager classes
- JSON commands sent to firmware; structured prefix-tagged text responses returned (`OK:`, `DATA:`, `ERROR:`, etc.)

## Layers

*[unverified in 2026-08-26 and 2026-09-14 scoped remaps — submodule internals, out of scope]*

**CLI / Entry Point Layer:**
- Purpose: Argument parsing, user input validation, command routing, logging configuration
- Location: `firestarter_app/firestarter/main.py`
- Contains: `main()` function, argparse subparser builders, `EpromCompleter` for tab-completion, `build_arg_flags()` helper
- Depends on: All manager/service classes, EpromDatabase, constants
- Used by: Console entry point `firestarter` (defined in `pyproject.toml`)

**Service / Manager Layer:**
- Purpose: Domain-specific business logic, serial communication orchestration, firmware management
- Location: `firestarter_app/firestarter/`
- Contains:
  - `EpromOperator` (`eprom_operations.py`) - read/write/erase/verify/blank-check/chip-id operations
  - `HardwareManager` (`hardware.py`) - VPP/VPE voltage reading, hardware revision and config
  - `FirmwareManager` (`firmware.py`) - firmware version check, download, and avrdude-based flashing
  - `EpromConsolePresenter` (`eprom_info.py`) - structured display of EPROM info
  - `EpromSpecBuilder` (`ic_layout.py`) - builds technical spec dictionaries for display
- Depends on: SerialCommunicator, EpromDatabase, ConfigManager, constants
- Used by: CLI layer

**Data / Repository Layer:**
- Purpose: EPROM database management, configuration persistence, pin-map translation
- Location: `firestarter_app/firestarter/`
- Contains:
  - `EpromDatabase` (`database.py`) - singleton, loads/merges JSON databases, translates pinouts to RURP bus config
  - `ConfigManager` (`config.py`) - singleton, persists app config to `~/.firestarter/config.json`
- Depends on: JSON data files in `firestarter_fw/data/`, `~/.firestarter/` user overrides
- Used by: All manager classes and CLI layer

**Communication Layer:**
- Purpose: Serial port discovery, connection, JSON command dispatch, response parsing
- Location: `firestarter_app/firestarter/serial_comm.py`
- Contains: `SerialCommunicator` class, custom exceptions (`SerialError`, `ProgrammerNotFoundError`, `FirmwareOutdatedError`), `Response` namedtuple
- Depends on: `pyserial`, ConfigManager, constants
- Used by: EpromOperator, HardwareManager, FirmwareManager

**Firmware Layer (Embedded C++):**
- Purpose: Direct hardware control of the RURP shield; processes JSON commands and drives address/data bus
- Location: `firestarter_fw/src/`
- Contains: `firestarter.cpp` (main loop + state machine), `eprom_operations.cpp`, `hardware_operations.cpp`, `json_parser.c`, board-specific HAL in `src/boards/`, device handlers in `src/proms/`
- Depends on: Arduino framework, PlatformIO build system
- Used by: Python host via serial port

## Data Flow

*[unverified in 2026-08-26 and 2026-09-14 scoped remaps — submodule internals, out of scope]*

**EPROM Write Operation:**

1. User runs `firestarter write W27C512 data.bin`
2. `main.py` parses args, fetches EPROM data from `EpromDatabase`, calls `EpromOperator.write_eprom()`
3. `EpromOperator._setup_operation()` builds JSON command dict (memory-size, type, vpp, bus-config, cmd=2, flags)
4. `SerialCommunicator.find_and_connect()` probes serial ports, sends command JSON, validates firmware version from `OK:` response
5. `EpromOperator._run_state_machine()` drives three phases:
   - INIT: sends ACK, waits for `INIT:` signal from firmware
   - MAIN: firmware requests data chunks via `OK:` messages; host sends `#<len><checksum>` header then binary data block (512 bytes at a time); firmware sends `MAIN:` when done
   - END: waits for `END:` signal, sends final ACK
6. File is read in 512-byte chunks (`BUFFER_SIZE`), XOR checksum computed per chunk, progress tracked via `tqdm`
7. Result (`bool`) returned up through layers to `main.py`, which sets process exit code

**EPROM Read Operation:**

1. Similar setup as write, `cmd=1`
2. During MAIN phase, firmware sends `DATA:` signals followed by a binary block (2-byte length + 1-byte checksum + data)
3. `SerialCommunicator.read_data_block()` reads length, validates checksum, returns bytes
4. Callback writes bytes to output file at correct offset
5. Host ACKs each block; firmware sends `MAIN:` when complete

**Firmware Update Flow:**

1. `FirmwareManager.check_current_firmware()` connects, sends `COMMAND_FW_VERSION` state command
2. Parses version and board name from response
3. `fetch_latest_release_info()` hits GitHub Releases API to find latest `.hex` asset URL
4. If update needed (or forced), downloads `.hex` via HTTP to `~/.firestarter/`
5. `Avrdude` wrapper (`avr_tool.py`) invokes `avrdude` process to flash the hex file

**State Management:**
- No persistent in-memory state between CLI invocations (stateless CLI)
- `ConfigManager` persists last-used serial port and avrdude paths to `~/.firestarter/config.json`
- `EpromDatabase` is a singleton initialized once per process; data is read-only after init
- Arduino firmware maintains its own EEPROM-persisted config (`rurp_configuration_t`) for hardware calibration values

## Key Abstractions

*[unverified in 2026-08-26 and 2026-09-14 scoped remaps — submodule internals, out of scope]*

**EpromOperator (context manager + state machine):**
- Purpose: Encapsulates the full lifecycle of a hardware operation (connect, run state machine, disconnect)
- Examples: `firestarter_app/firestarter/eprom_operations.py`
- Pattern: Context manager (`_operation_context`) wraps `_run_state_machine()`; main-phase behavior injected via `main_phase_handler` callable (strategy pattern)

**EpromDatabase (Singleton + data mapper):**
- Purpose: Authoritative source for EPROM specifications; translates generic DIP pin numbers to RURP hardware bus lines
- Examples: `firestarter_app/firestarter/database.py`
- Pattern: Singleton via `__new__`; `_map_data()` converts raw JSON schema to normalized dict; `convert_to_programmer()` produces the compact dict sent over serial

**SerialCommunicator (factory + protocol parser):**
- Purpose: Port auto-discovery, JSON command dispatch, prefix-tagged response parsing, binary data block I/O
- Examples: `firestarter_app/firestarter/serial_comm.py`
- Pattern: `find_and_connect()` class method probes ports; generator `_read_and_parse_lines()` yields parsed `Response` namedtuples; firmware version gating at connection time

**Three-Phase Serial Protocol:**
- Purpose: Reliable handshake between host and firmware for all operations
- Pattern: INIT phase (setup/config ACK), MAIN phase (data transfer with per-block ACK and checksum), END phase (completion confirmation); firmware uses prefix-tagged text lines (`OK:`, `DATA:`, `MAIN:`, `END:`, `ERROR:`)

**firestarter_handle_t (Firmware central state):**
- Purpose: Central state struct holding all operation context on the firmware side
- Examples: `firestarter_fw/include/firestarter.h`
- Pattern: Struct with function pointers for device-specific operations (polymorphic behavior without C++ vtables in C context)

## Entry Points

*[unverified in 2026-08-26 and 2026-09-14 scoped remaps — submodule internals, out of scope]*

**Python CLI:**
- Location: `firestarter_app/firestarter/main.py` — `main()` function
- Triggers: `firestarter` console script (defined in `pyproject.toml [project.scripts]`)
- Responsibilities: Argument parsing, logging setup, service instantiation, command dispatch

**Arduino Firmware Main Loop:**
- Location: `firestarter_fw/src/firestarter.cpp`
- Triggers: Arduino `setup()` / `loop()` framework calls
- Responsibilities: JSON command parsing, state machine dispatch, timeout management, serial I/O

## Error Handling

*[unverified in 2026-08-26 and 2026-09-14 scoped remaps — submodule internals, out of scope]*

**Strategy:** Layered exception hierarchy in Python; error prefix responses from firmware

**Patterns:**
- Custom exceptions in serial layer: `SerialError`, `SerialTimeoutError`, `ProgrammerNotFoundError`, `FirmwareOutdatedError` — caught at manager layer boundaries, converted to `logger.error()` + `False` return
- `EpromOperationError` raised within `_run_state_machine()` when firmware sends `ERROR:` response
- Context manager `_operation_context` ensures `SerialCommunicator.disconnect()` is always called via `finally`
- CLI layer receives `bool` return values from managers; maps `False` to exit code 1
- Firmware sends `ERROR:<message>` on hardware failures; `WARN:<message>` for non-fatal issues
- `SIGINT` handler in `main.py` logs warning and calls `sys.exit(1)` for clean keyboard interrupt

## Cross-Cutting Concerns

*[unverified in 2026-08-26 and 2026-09-14 scoped remaps — submodule internals, out of scope]*

**Logging:** Python standard `logging` module used throughout; custom `SingleLineStatusHandler` in `logging_utils.py` supports in-place status line updates (`status='start'`/`'end'` extras) for connection progress; verbose mode adds module/line info; `tqdm` progress bars used for data transfer with `logging_redirect_tqdm` integration

**Validation:** EPROM name validation at CLI (tab-completion via `EpromCompleter`, error if not found in DB); address/size string parsing accepts both decimal and hex (`0x` prefix); flag validation in dev commands; firmware version semver comparison on every connection

**Authentication:** None (local hardware access only); firmware version gating enforces minimum 2.0.0 requirement

---

*Submodule architecture analysis: 2026-05-08*

---

# Part 2 — Meta-Repo Architecture (agent tooling & dev environment)

**Analysis Date:** 2026-08-26
**Scope:** `.claude`, `.devcontainer`, `.github`, `.vscode`, `.gitignore`, `.gitmodules`, `CLAUDE.md`

## System Overview

```text
┌─────────────────────────────────────────────────────────────┐
│              Human operator (terminal / IDE)                 │
├─────────────────────────────────────────────────────────────┤
│              Slash commands (thin dispatch shells)           │
│   `.claude/commands/gsd-*.md`  (72 files)                    │
└────────────────────────┬────────────────────────────────────┘
                         │  `requires:` + frontmatter routing
                         ▼
┌─────────────────────────────────────────────────────────────┐
│        Orchestration specs (the actual workflow logic)       │
│   `.claude/gsd-core/workflows/*.md`      (89 files)          │
│   + `.claude/gsd-core/references/*.md`   (112, lazy-loaded)   │
│   + `.claude/gsd-core/templates/`        (34 artifacts)       │
│   + `.claude/gsd-core/contexts/`         (dev/review/research)│
└──────────┬──────────────────────────────┬───────────────────┘
           │ Agent/Task delegation        │ shell out
           ▼                              ▼
┌────────────────────────────┐  ┌────────────────────────────┐
│ Subagents (fresh context)  │  │ State CLI                  │
│ `.claude/agents/gsd-*.md`  │  │ `.claude/gsd-core/bin/`    │
│ (35: planner, executor,    │  │   `gsd-tools.cjs` (5070 ln)│
│  verifier, mapper, …)      │  │   + `bin/lib/*.cjs`        │
└────────────┬───────────────┘  └────────────┬───────────────┘
             │ write artifacts               │ read/write state
             ▼                               ▼
┌─────────────────────────────────────────────────────────────┐
│  `.planning/`  — the durable project record (tracked)        │
│  ROADMAP.md · STATE.md · REQUIREMENTS.md · phases/ ·         │
│  codebase/ · research/ · graphs/GRAPH_REPORT.md              │
└─────────────────────────────────────────────────────────────┘
             ▲ intercepted by
┌─────────────────────────────────────────────────────────────┐
│  Hooks (tool-call interception)  `.claude/hooks/gsd-*.{js,sh}`│
│  PreToolUse guards · PostToolUse monitors · SessionStart      │
└─────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| Submodule declaration | Pins the two code repos as gitlinks | `.gitmodules` |
| Tracking policy | Excludes all of `.claude/` except hand-authored skills; excludes generated `platformio.ini`, graph payloads, worktrees, bench artifacts | `.gitignore` |
| Agent onboarding brief | Repo layout, dev commands, cross-repo sync invariants | `CLAUDE.md` |
| Slash commands | Entry points; frontmatter declares `allowed-tools`, `argument-hint`, `requires` | `.claude/commands/gsd-map-codebase.md` (and 71 siblings) |
| Workflow specs | Step-by-step orchestration each command executes | `.claude/gsd-core/workflows/map-codebase.md` |
| Subagent definitions | Role prompt + output contract for each delegated worker | `.claude/agents/gsd-codebase-mapper.md` |
| Project skills | Hand-authored domain tooling (the only tracked part of `.claude/`) | `.claude/skills/devtest-triage/SKILL.md`, `.claude/skills/devtest-rootcause/SKILL.md` |
| State/query CLI | 40+ subcommands over `.planning/` (state, phase, roadmap, requirements, commit, validate…) | `.claude/gsd-core/bin/gsd-tools.cjs` |
| Hooks | Enforce invariants at tool-call boundaries | `.claude/hooks/` (30 hooks + `lib/`, `managed-hooks-registry.cjs`) |
| Changeset tooling | Release-note authoring/linting/rendering | `.claude/scripts/changeset/cli.cjs` |
| Install bookkeeping | Which GSD files are managed, at which version | `.claude/gsd-file-manifest.json`, `.claude/gsd-install-state.json`, `.claude/gsd-core/VERSION` |
| Permission/hook config | Allowlists, hook wiring, plugin enablement | `.claude/settings.json`, `.claude/settings.local.json` |
| Dev environment | Container image, mounts, features, post-create provisioning | `.devcontainer/devcontainer.json`, `.devcontainer/Dockerfile`, `.devcontainer/post-create.sh` |
| PlatformIO root wrapper generator | Emits the gitignored root `platformio.ini` mapping IDE paths into `firestarter_fw/` | `.devcontainer/gen-platformio-ini.py` |
| Editor/debug config | PlatformIO IntelliSense + debug launch targets | `.vscode/c_cpp_properties.json`, `.vscode/launch.json` |

## Pattern Overview

**Overall:** Orchestrator → subagent delegation over a file-based state machine.

**Key characteristics:**
- **Markdown-as-program.** Control flow lives in prose specs (`.claude/gsd-core/workflows/*.md`), not code. `.claude/commands/*.md` are thin dispatch shells whose frontmatter (`allowed-tools`, `requires`, `argument-hint`) constrains the run; the workflow file supplies the steps.
- **Context isolation by delegation.** Expensive exploration is pushed into subagents (`.claude/agents/gsd-*.md`) that write artifacts directly into `.planning/` and return only a short confirmation. The orchestrator never absorbs the explored material — this document's own producer (`gsd-codebase-mapper`) is an instance of the pattern.
- **`.planning/` is the single source of truth.** All durable state is plain Markdown/JSON on disk, so a workflow survives context resets and can be resumed by a different session.
- **Deterministic operations are shelled out.** Anything that must be exact — frontmatter edits, phase lookup, commit construction, validation — goes through `gsd-tools.cjs` rather than model text generation.
- **Guardrails as hooks, not instructions.** Invariants are enforced by process interception (`PreToolUse`), so they hold even when the model is wrong.
- **Config-as-code for local runtime.** `.claude/` is gitignored yet reproducible: `.devcontainer/post-create.sh` idempotently regenerates the required `settings.local.json` entries on every rebuild.
- **Two-tier settings.** `.claude/settings.json` holds the shared 110-entry permission allowlist plus `autoMode.allow`; `.claude/settings.local.json` holds machine-local hook wiring (absolute node paths), `worktree.baseRef`, and the plugin marketplace registration.

## Layers

**Command layer:**
- Location: `.claude/commands/` (69 `gsd-*.md` files)
- Contains: YAML frontmatter (`name`, `description`, `argument-hint`, `allowed-tools`, `requires`) + an `<objective>` block
- Depends on: the matching workflow spec in `gsd-core/workflows/`
- Used by: the human, via `/gsd-*`

**Workflow layer:**
- Location: `.claude/gsd-core/workflows/` (89 files; some commands have a sibling directory of split steps, e.g. `execute-phase.md` + `execute-phase/`)
- Contains: numbered orchestration steps, agent dispatch instructions, gate definitions
- Depends on: `gsd-core/references/` (112 lazy-loaded deep-dive docs such as `gates.md`, `planner-antipatterns.md`, `agent-contracts.md`, `model-profile-resolution.md`), `gsd-core/templates/` (34 artifact skeletons), `gsd-core/contexts/{dev,review,research}.md`
- Used by: command layer

**Agent layer:**
- Location: `.claude/agents/` (34 `gsd-*.md`)
- Contains: role definition, required reading, process steps, output contract. Roles cluster into planning (`gsd-planner`, `gsd-roadmapper`, `gsd-plan-checker`), execution (`gsd-executor`, `gsd-verifier`, `gsd-integration-checker`), research (`gsd-project-researcher`, `gsd-domain-researcher`, `gsd-phase-researcher`, `gsd-research-synthesizer`), review/audit (`gsd-code-reviewer`, `gsd-code-fixer`, `gsd-security-auditor`, `gsd-nyquist-auditor`, `gsd-eval-auditor`), docs (`gsd-doc-writer`, `gsd-doc-verifier`, `gsd-doc-classifier`, `gsd-doc-synthesizer`), UI (`gsd-ui-researcher`, `gsd-ui-auditor`, `gsd-ui-checker`), and mapping (`gsd-codebase-mapper`, `gsd-pattern-mapper`)
- Depends on: nothing at runtime except its prompt + the tools it is granted; each starts from a fresh context
- Used by: workflow layer via the Agent/Task tool

**Skill layer (the only tracked part of `.claude/`):**
- Location: `.claude/skills/`
- Contains: `devtest-triage/` (`SKILL.md`, `scripts/devtest_issues.py`, `fixtures/*.md`) and `devtest-rootcause/` (`SKILL.md`, `scripts/infoic_lookup.py`, `scripts/diff_db.py`)
- Constraint: a skill must own its scripts — no importing from `firestarter_app/tools/`; scripts are copied in with a drift check
- Also present but untracked: `find-skills/`, `skill-creator/` — marketplace-installed, explicitly gitignored (reinstall, don't vendor)

**Hook layer:**
- Location: `.claude/hooks/` plus `.claude/hooks/lib/` and `managed-hooks-registry.cjs`
- Wiring: `.claude/settings.local.json` → `hooks`
  - `SessionStart`: `gsd-check-update.js`, `gsd-session-state.sh`, `gsd-update-banner.js`
  - `PreToolUse`: `gsd-prompt-guard.js` + `gsd-read-guard.js` (`Write|Edit`), `gsd-workflow-guard.js` (`Bash|Edit|Write|MultiEdit`), `gsd-validate-commit.sh` (`Bash`), `gsd-worktree-path-guard.js` (`Write|Edit|MultiEdit`)
  - `PostToolUse`: `gsd-context-monitor.js` (`Bash|Edit|Write|MultiEdit|Agent|Task`), `gsd-read-injection-scanner.js` (`Read`), `gsd-phase-boundary.sh` (`Write|Edit`), `gsd-graphify-update.sh` (`Bash`)
  - `SubagentStop` / `Stop` / `PreCompact`: `gsd-context-monitor.js`
  - `FileChanged` (`config.json`): `gsd-config-reload.js`
- Not wired in this project: `gsd-cursor-*.js`, `gsd-ensure-canonical-path.js`, `gsd-check-update-worker.js`, `gsd-statusline.js`

**Tooling layer:**
- Location: `.claude/gsd-core/bin/` — `gsd-tools.cjs` (CLI entry, 5070 lines), `gsd_run`, `check-latest-version.cjs`, `verify-reapply-patches.cjs`, `bin/lib/*.cjs`, `bin/shared/`
- Contains: subcommand dispatch — `state`, `phase`, `phases`, `roadmap`, `requirements`, `milestone`, `find-phase`, `commit`, `check-commit`, `commit-to-subrepo`, `pr-subrepo`, `verify`, `verify-summary`, `verification`, `validate`, `template`, `frontmatter`, `task`, `eval`, `agent`, `agent-skills`, `skill-manifest`, `resolve-model`, `resolve-granularity`, `resolve-execution`, `config-*`, `migrate-config`, `gap-analysis`, `history-digest`, `generate-slug`, `current-timestamp`, `list-todos`, `list-seeds`, `verify-path-exists`, `project-instruction-file`
- Note: node is not on `PATH` in the devcontainer; invoke via the absolute nvm node path (the same one the hook wiring hardcodes)
- Sibling: `.claude/scripts/changeset/` (`cli.cjs`, `parse.cjs`, `render.cjs`, `serialize.cjs`, `lint.cjs`, `github-release-notes.cjs`, `new.cjs`), `.claude/scripts/fix-slash-commands.cjs`, `.claude/scripts/lib/allowlist-ratchet.cjs`

**Channel layer:** — **REMOVED 2026-08-26** (commit `3e2f7d89`)
- The Discord DM channel has been removed: `.claude/channels/` is deleted, the plugin is disabled, and the tracked wiring is gone. One copy of the bot token remains at `~/.claude/channels/discord/.env` (outside the repo) and is **not revoked**. The description below is historical.
- Former location: `.claude/channels/discord/` — `.env` (bot token, mode `600`), `access.json`, `approved/`
- `DISCORD_STATE_DIR` is set to this path by `.devcontainer/devcontainer.json` so the token and pairing survive a named-volume wipe; `.gitignore` keeps it out of git
- **Credential warning:** `.claude/settings*.json` may hold keys — never transcribe values from it. The former `.claude/channels/discord/.env` was deleted 2026-08-26 (commit `3e2f7d89`); one copy of that token remains at `~/.claude/channels/discord/.env`, outside the repo and **still valid** until reset in the Discord Developer Portal.

## Data Flow

### A slash command run

1. Operator types `/gsd-map-codebase` → `.claude/commands/gsd-map-codebase.md` frontmatter constrains `allowed-tools` and declares `requires: [config, new-project, plan-phase]`
2. `SessionStart` hooks have already stamped session state (`.claude/hooks/gsd-session-state.sh`) and checked for a GSD update
3. The command body points at `.claude/gsd-core/workflows/map-codebase.md`, which supplies the orchestration steps
4. The workflow reads current state via `.claude/gsd-core/bin/gsd-tools.cjs state`
5. The workflow spawns parallel `gsd-codebase-mapper` subagents (`.claude/agents/gsd-codebase-mapper.md`), one per focus area, each with a fresh context
6. Each subagent explores, then **writes its documents straight into `.planning/codebase/`** and returns a ~10-line confirmation
7. `PostToolUse` hooks fire per tool call: `gsd-context-monitor.js` tracks budget, `gsd-phase-boundary.sh` watches artifact writes
8. The orchestrator commits via `gsd-tools.cjs commit`, gated by the `PreToolUse` `gsd-validate-commit.sh` hook

### Container provisioning

1. `.devcontainer/devcontainer.json` builds `.devcontainer/Dockerfile`, binds the repo at `/workspaces` (not a nested folder, so both submodules sit top-level), runs `--privileged` with `/dev` bind-mounted for Arduino serial access
2. Named volumes persist `~/.platformio`, `~/.config`, `~/.cache/pip`, `~/.claude`; features add GitHub CLI, Node 22, and Claude Code
3. `postCreateCommand` runs `.devcontainer/post-create.sh` (22 lines), which:
   - generates the root `platformio.ini` via `gen-platformio-ini.py`
   - `pip install -e /workspaces/firestarter_app`
   - `pio pkg install` inside `firestarter_fw/`
   - `graphify install` (writes into the `~/.claude` volume, which only exists at runtime)
   - installs GSD project-locally, pinned to a fixed version, via `npx -y --package=@opengsd/gsd-core@1.13.0 -- gsd-core --claude --local`
   - (steps that provisioned the Discord state dir, force-wrote `enabledPlugins`/`extraKnownMarketplaces`, and repointed the plugin's `.mcp.json` at `discord-singleton.sh` were removed 2026-08-26, commit `3e2f7d89`)

There is **no** build, test, or release workflow in this repo — firmware and host-app CI live in the submodules.

**State management:**
- Durable workflow state is files under `.planning/`; nothing is held in memory across sessions
- `.claude/gsd-install-state.json` (`schemaVersion: 1`, 5 applied migrations) and `.claude/gsd-file-manifest.json` (`version: 1.13.0`, `mode: full`, 759 managed files) track the GSD install; `.claude/gsd-core/VERSION` is `1.13.0`; `.claude/.gsd-profile` is `full`
- `.claude/gsd-migration-journal/` holds one JSON record per applied migration
- `.claude/worktrees/` is the (currently empty) parallel-worktree area; `settings.local.json` sets `worktree.baseRef: head`

## Key Abstractions

**Slash command / workflow split:**
- Purpose: keep the always-loaded surface tiny while the real logic stays lazily loadable
- Examples: `.claude/commands/gsd-plan-phase.md` → `.claude/gsd-core/workflows/plan-phase.md`
- Pattern: dispatch shell + spec

**Subagent contract:**
- Purpose: a delegated worker with a fixed input brief and a fixed output artifact, returning minimal text
- Examples: `.claude/agents/gsd-codebase-mapper.md`, `.claude/agents/gsd-executor.md`, `.claude/gsd-core/references/agent-contracts.md`
- Pattern: role prompt + `<required_reading>` + success criteria + "return confirmation only"

**Reference indirection:**
- Purpose: keep workflows short by deferring detail
- Examples: `.claude/gsd-core/references/gates.md`, `execute-phase-context-guard.md`, `worktree-path-safety.md`
- Pattern: a workflow names a reference; the reference is read only when that branch is taken

**Guard hook:**
- Purpose: fail a tool call that would violate an invariant, regardless of model intent
- Examples: `.claude/hooks/gsd-validate-commit.sh`, `gsd-workflow-guard.js`, `gsd-worktree-path-guard.js`, `gsd-read-guard.js`
- Pattern: `PreToolUse` matcher + non-zero exit to block

**Generated-file wrapper:**
- Purpose: make an IDE that expects a project at the repo root work against a submodule
- Examples: `.devcontainer/gen-platformio-ini.py` → root `platformio.ini` (gitignored)
- Pattern: read the submodule's config, prepend a `[platformio]` path-redirect section, rewrite relative `-I` and `pre:`/`post:` script paths

**Singleton MCP launcher:** — **REMOVED 2026-08-26** (commit `3e2f7d89`)
- Purpose: one Discord bot per machine despite N Claude processes each initializing MCP
- Examples: `.devcontainer/discord-singleton.sh` (deleted; pattern retained here as prior art)
- Pattern: non-blocking `flock` on fd 9; the loser exits 0, which Claude Code reads as "this server produced nothing"

## Entry Points

**Slash commands:** `.claude/commands/gsd-*.md` — 72 operator-facing entry points.

**GSD CLI:** `.claude/gsd-core/bin/gsd-tools.cjs` — invoked from workflows/hooks with an absolute node path.

**Container provisioning:** `.devcontainer/post-create.sh`, via `postCreateCommand`.

**Firmware debug:** `.vscode/launch.json` — three `platformio-debug` configurations, all targeting `firestarter_fw/.pio/build/uno/firestarter_uno.elf` for the `uno` env.

**Discord DM:** **REMOVED 2026-08-26** (commit `3e2f7d89`) — was the channel plugin's MCP server, launched through `.devcontainer/discord-singleton.sh`. No longer an entry point.

## Architectural Constraints

- **Submodules, not subtrees.** `.gitmodules` gitlinks `firestarter` → `git@github.com:henols/firestarter_fw.git` (name and path both stay `firestarter`; only the remote was repointed for the v1.38 rename) and `firestarter_app` → `git@github.com:henols/firestarter_app.git`. Work destined for a sub-repo must be committed *inside* it; a meta-repo commit only re-pins the gitlink.
- **Worktrees leave submodules empty.** A fresh git worktree of the meta-repo has empty `firestarter_fw/` and `firestarter_app/`.
- **Manual cross-repo sync pairs.** `CLAUDE.md` records two: `serial_comm.py` ↔ `firestarter.cpp` (protocol) and `constants.py` ↔ `firestarter.h` (flag bits). Neither is CI-enforced.
- **`.claude/` is gitignored but must stay reproducible.** Anything required for a fresh clone to work has to be regenerated by tracked code (`post-create.sh`), not left in local state.
- **Hardware coupling.** `--privileged` plus a `/dev` bind mount are required for serial access; without them only builds work.
- **Machine-local absolute paths leak into config.** `settings.local.json` hardcodes `/usr/local/share/nvm/versions/node/v24.15.0/bin/node`, and `.vscode/c_cpp_properties.json`, `launch.json`, `settings.json` all carry `/home/henrik/...` host paths that do not exist inside the container.
- **Node is not on `PATH`** in the devcontainer; use the absolute node binary or `.claude/gsd-core/bin/gsd-tools.cjs` through a full path.
- **Single Discord bot per token.** (**REMOVED 2026-08-26** (commit `3e2f7d89`) — no longer applies; kept as prior art.) Multiple gateway connections on one token scatter inbound DMs; the flock in `discord-singleton.sh` is the only thing preventing one bot per subagent.

## Anti-Patterns

### Hand-editing a generated file

**What happens:** editing the root `platformio.ini`, or `.vscode/c_cpp_properties.json` / `launch.json`.
**Why it's wrong:** all three carry explicit "AUTO-GENERATED — do not modify" headers; the root `platformio.ini` is additionally gitignored, so edits are silently lost on the next `post-create.sh`.
**Do this instead:** change `firestarter_fw/platformio.ini` and re-run `python3 .devcontainer/gen-platformio-ini.py`; regenerate the `.vscode` files from PlatformIO.

### Vendoring a marketplace skill

**What happens:** committing `.claude/skills/find-skills/` or `.claude/skills/skill-creator`.
**Why it's wrong:** both are marketplace-installed (`skill-creator` is a symlink into the gitignored `.agents/`), and `.gitignore` names them individually to keep them out.
**Do this instead:** reinstall (`npx skills add anthropics/skills@skill-creator`). Only hand-authored skills — `devtest-triage`, `devtest-rootcause` — are tracked.

### Importing sub-repo code into a skill

**What happens:** a `.claude/skills/*/scripts/*.py` imports from `firestarter_app/tools/`.
**Why it's wrong:** the skill then breaks in any checkout where the submodule is uninitialized (worktrees, CI).
**Do this instead:** copy the script into the skill directory and add an AST drift check, as `devtest-triage/scripts/devtest_issues.py` does.

## Error Handling

**Strategy:** fail-closed at the tool boundary; the model is not trusted to self-police.

**Patterns:**
- `PreToolUse` hooks block a violating call before it runs (`gsd-validate-commit.sh` on `Bash`, `gsd-workflow-guard.js`, `gsd-worktree-path-guard.js`)
- `gsd-read-injection-scanner.js` scans read content post-hoc for prompt injection
- `.devcontainer/post-create.sh` runs `set -e`, but its two embedded Python blocks catch and log rather than abort (`FileNotFoundError`/`ValueError` on a missing `settings.local.json`; a bare `except` around the plugin `.mcp.json` patch, which no-ops when the plugin isn't installed yet)
- `discord-singleton.sh` (deleted 2026-08-26) used `set -uo pipefail` (deliberately not `-e`) and exits **0** on lock failure — a non-zero exit would surface as an MCP error in every worker
- There is no CI in this repo, so no in-repo error-handling pattern to describe there — firmware and host-app CI live in the submodules

## Cross-Cutting Concerns

**Logging/observability:** `post-create.sh` echoes a banner per provisioning stage and reports whether a Discord token is present without printing it; `gsd-context-monitor.js` tracks context budget on every tool call and at `Stop`/`SubagentStop`/`PreCompact`; `gsd-statusline.js` exists but is not wired.

**Validation:** command frontmatter (`allowed-tools`, `requires`) constrains each run; `gsd-tools.cjs validate` / `check` / `verify` assert `.planning/` integrity; `.claude/scripts/lib/allowlist-ratchet.cjs` guards permission-list growth.

**Secrets:** `.claude/settings*.json` is gitignored via `.claude/*`. Never quote its contents. (`.claude/channels/discord/.env` was deleted 2026-08-26; a copy remains at `~/.claude/channels/discord/.env`, outside the repo and still valid.)

**Reproducibility:** tracked provisioning code regenerates untracked local state; `.devcontainer/devcontainer-lock.json` pins the devcontainer features.

---

*Meta-repo architecture analysis: 2026-09-14 (scoped remap)*
