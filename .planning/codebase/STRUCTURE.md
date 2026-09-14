---
last_mapped_commit: b1311abd
last_mapped_at: 2026-09-14T04:59:59.314Z
mapped_paths: .claude,.devcontainer,.github,.gitignore,.gitmodules,.vscode,CLAUDE.md
---
# Structure

**Analysis Date:** 2026-05-08 (submodule sections) / 2026-09-14 (meta-repo sections)

> **Scope note.** The 2026-08-26 and 2026-09-14 remaps covered only the meta-repo's own
> tracked infrastructure (`.claude`, `.devcontainer`, `.github`, `.vscode`, `.gitignore`,
> `.gitmodules`, `CLAUDE.md`). The `firestarter_fw/` and `firestarter_app/` sections
> below date from 2026-05-08 and were not re-verified —
> `[unverified in 2026-08-26 and 2026-09-14 scoped remaps]`. `tools/` is outside this
> remap's scope by decision, so it is not described here either.

## Repository Layout

This is **not a monorepo.** It is a **meta-repo with two git submodules**. `.gitmodules`
declares both code sub-projects as gitlinks pointing at independent GitHub repos:

```ini
[submodule "firestarter"]      path = firestarter        url = git@github.com:henols/firestarter_fw.git
[submodule "firestarter_app"]  path = firestarter_app    url = git@github.com:henols/firestarter_app.git
```

The submodule's own name and path are still `firestarter` — only the remote was repointed at
the `firestarter_fw` rename (v1.38).

The meta-repo itself tracks only planning and agent-tooling artifacts within this remap's
scope — `.planning/`, `.claude/skills/` (hand-authored skills only), `.devcontainer/`,
`.github/`, `.vscode/`, `CLAUDE.md`, `.gitignore`, `.gitmodules`. Everything else at the root
is gitignored local state. Evidence: `.gitmodules` (the two gitlinks) and `.gitignore`
(`.claude/*` with `!.claude/skills/`, plus the generated `platformio.ini`, `.pio/`,
`graphify-out/`, extra worktrees, and bench artifacts).

Consequence: code changes are committed **inside** the submodule; a meta-repo commit only
re-pins the gitlink. A fresh git worktree of the meta-repo leaves both submodule
directories empty.

### Top-level directory tree

```text
/workspaces/                          # meta-repo root (bind-mounted here in the devcontainer)
├── .claude/                          # GSD agent runtime — GITIGNORED except skills/
│   ├── commands/                     #   [ignored] 72 gsd-*.md slash commands
│   ├── agents/                       #   [ignored] 35 gsd-*.md subagent definitions
│   ├── gsd-core/                     #   [ignored] workflows, references, templates, bin/
│   ├── hooks/                        #   [ignored] 30 gsd-* hooks + lib/, registry
│   ├── scripts/                      #   [ignored] changeset/, lib/, fix-slash-commands.cjs
│   ├── worktrees/                    #   [ignored] parallel worktree area (empty)
│   ├── skills/                       #   TRACKED (devtest-triage, devtest-rootcause only)
│   ├── settings.json                 #   [ignored] shared permission allowlist (110) + autoMode
│   ├── settings.local.json           #   [ignored] hook wiring, worktree, marketplace registration
│   ├── gsd-file-manifest.json        #   [ignored] 759 managed files @ 1.13.0, mode "full"
│   ├── gsd-install-state.json        #   [ignored] schemaVersion 1, 5 migrations
│   ├── gsd-migration-journal/        #   [ignored] one JSON per applied migration
│   ├── .gsd-profile                  #   [ignored] "full"
│   └── package.json                  #   [ignored] {"type":"commonjs"}
├── .devcontainer/                    # TRACKED — dev environment definition
│   ├── devcontainer.json             #   mounts, features, containerEnv, postCreateCommand
│   ├── Dockerfile
│   ├── devcontainer-lock.json        #   pins the devcontainer features
│   ├── post-create.sh                #   provisioning: platformio.ini, pip -e, pio pkg, graphify, GSD install
│   ├── gen-platformio-ini.py         #   emits the gitignored root platformio.ini
│   └── README.md                     #   using-the-container guide
├── .github/                           # TRACKED — no workflows/ directory; no meta-repo CI
│   ├── CONTRIBUTING.md
│   └── ISSUE_TEMPLATE/                #   4 files: bug-report.yml, config.yml, dev-test-report.md, feature-request.yml
├── .vscode/                          # TRACKED — mostly PlatformIO-generated
│   ├── c_cpp_properties.json         #   AUTO-GENERATED; /home/henrik/... host paths
│   ├── launch.json                   #   AUTO-GENERATED; 3 platformio-debug configs (uno)
│   ├── settings.json                 #   one clang-tidy path (host-specific)
│   └── extensions.json               #   recommends platformio-ide; unwants cpptools pack
├── .planning/                        # TRACKED — the durable project record
├── CLAUDE.md                         # TRACKED — agent onboarding brief (77 lines)
├── .gitmodules                       # TRACKED
├── .gitignore                        # TRACKED
├── firestarter_fw/                      # SUBMODULE (gitlink) — Arduino firmware
├── firestarter_app/                  # SUBMODULE (gitlink) — Python host CLI
│
│   ── everything below is GITIGNORED local state ──
├── platformio.ini                    # GENERATED by gen-platformio-ini.py
├── .pio/                             # PlatformIO build cache
├── .agents/                          # npx-skills real install dir (skill-creator lives here)
├── skills-lock.json                  # npx-skills manifest
├── package.json / package-lock.json  # root tool artifacts
├── graphify-out/                     # knowledge-graph scratch output (~24 MB cache)
├── firestarter-runs/                 # dev-diagnostic run output
├── chip-test/                        # `dev test` reports + onboarding transcripts
├── consistency-check-* / write-cycle-*  # legacy ungrouped run dirs
├── firestarter_app_py32/             # extra worktree (never gitlinked)
├── firestarter_py32_ci/              # extra worktree (never gitlinked)
├── *.bin                             # raw chip dumps at root (e.g. W29C040.bin)
├── .mypy_cache/ .pytest_cache/ .ruff_cache/ __pycache__/
└── scratchpad/
```

Also gitignored inside tracked trees: `.planning/graphs/graph.json`,
`.planning/graphs/.last-build-snapshot.json`, `.planning/research/.cache/`, and everything
under `.planning/v1.7/**` except `*.md` (raw chat dumps and photo binaries stay local).

---

## Meta-Repo Key File Locations

| Need | File |
|------|------|
| Repo layout + cross-repo sync rules | `CLAUDE.md` |
| Which submodule points where | `.gitmodules` |
| Tracking policy (and why) | `.gitignore` — heavily commented |
| Add/modify a slash command | `.claude/commands/gsd-<name>.md` + `.claude/gsd-core/workflows/<name>.md` |
| Add/modify a subagent | `.claude/agents/gsd-<name>.md` |
| Deep-dive guidance loaded on demand | `.claude/gsd-core/references/*.md` (112) |
| Artifact skeletons | `.claude/gsd-core/templates/` (34) |
| Persona presets | `.claude/gsd-core/contexts/{dev,review,research}.md` |
| GSD state/query CLI | `.claude/gsd-core/bin/gsd-tools.cjs` (+ `bin/lib/*.cjs`) |
| Installed GSD version | `.claude/gsd-core/VERSION` (`1.13.0`, project-local) |
| Hook implementations | `.claude/hooks/gsd-*.{js,sh}` |
| Hook wiring | `.claude/settings.local.json` → `hooks` |
| Permission allowlist | `.claude/settings.json` → `permissions.allow` (110), `autoMode.allow` (3) |
| Project-specific skills | `.claude/skills/devtest-triage/`, `.claude/skills/devtest-rootcause/` |
| Release-note tooling | `.claude/scripts/changeset/cli.cjs` |
| Discord bridge state | removed 2026-08-26 (commit `3e2f7d89`); a token copy remains at `~/.claude/channels/discord/.env`, outside the repo — **never quote it** |
| Container definition | `.devcontainer/devcontainer.json`, `.devcontainer/Dockerfile` |
| Provisioning steps | `.devcontainer/post-create.sh` |
| Root PlatformIO wrapper generator | `.devcontainer/gen-platformio-ini.py` |
| Firmware debug launch | `.vscode/launch.json` |
| Firmware IntelliSense include paths | `.vscode/c_cpp_properties.json` |

### `.planning/` role

Not deep-scanned in this remap. It is the durable, tracked project record that every GSD
workflow reads and writes: roadmap, state, requirements, per-phase directories, the
`codebase/` documents (including this file), research output, and the distilled
`graphs/GRAPH_REPORT.md`. Treat it as the source of truth for project status, and never
`rm -rf` `firestarter_app/.planning/codebase/` — that submodule keeps its own copy.

---

## Meta-Repo Naming Conventions

**Slash commands** — `.claude/commands/gsd-<verb>-<noun>.md`, kebab-case, always the
`gsd-` prefix: `gsd-plan-phase.md`, `gsd-map-codebase.md`, `gsd-audit-uat.md`. Namespaced
clusters use `gsd-ns-<cluster>.md` (`gsd-ns-workflow`, `gsd-ns-context`, `gsd-ns-review`,
`gsd-ns-project`, `gsd-ns-ideate`, `gsd-ns-manage`). Frontmatter carries `name`,
`description`, `argument-hint`, `allowed-tools`, `requires`.

**Workflows** — `.claude/gsd-core/workflows/<name>.md`, the command name **without** the
`gsd-` prefix (`gsd-plan-phase.md` → `plan-phase.md`). A large workflow adds a sibling
directory of split steps (`execute-phase.md` + `execute-phase/`). A shell fragment uses
`_<name>.snippet.sh`.

**Agents** — `.claude/agents/gsd-<role>.md`, role as a noun-agent
(`gsd-planner`, `gsd-executor`, `gsd-verifier`, `gsd-codebase-mapper`,
`gsd-code-reviewer`, `gsd-security-auditor`).

**References** — `.claude/gsd-core/references/<topic>.md`, kebab-case, frequently prefixed
by the consumer (`planner-*.md`, `execute-phase-*.md`, `thinking-models-*.md`).

**Hooks** — `.claude/hooks/gsd-<purpose>.js` for Node, `.sh` for bash; shared code in
`hooks/lib/`. Guards are named `*-guard`, observers `*-monitor`/`*-scanner`.

**Node tooling** — `.cjs` extension for anything under `.claude/gsd-core/bin/` or
`.claude/scripts/` (`.claude/package.json` declares `{"type":"commonjs"}`).

**Skills** — `.claude/skills/<kebab-case-name>/SKILL.md`, with owned code in
`scripts/*.py` (snake_case) and test data in `fixtures/*.md`.

---

## Where to Add New Meta-Repo Code

**A new GSD command:** `.claude/commands/gsd-<name>.md` (dispatch shell) +
`.claude/gsd-core/workflows/<name>.md` (steps). Note both are gitignored — a durable
change belongs upstream in the GSD package, not here.

**A new project skill:** `.claude/skills/<name>/SKILL.md`, scripts copied into
`<name>/scripts/` (never imported from a submodule), fixtures in `<name>/fixtures/`.
This is the one part of `.claude/` that is tracked and reviewable.

**A new hook:** implement in `.claude/hooks/gsd-<purpose>.{js,sh}` and wire it under
`.claude/settings.local.json` → `hooks` with a tool matcher. Use the absolute nvm node
path — node is not on `PATH`.

**A new provisioning step:** append to `.devcontainer/post-create.sh`, idempotently
(it re-runs on every rebuild). Mounts, features, and env go in `.devcontainer/devcontainer.json`.

**A new CI check:** `.github/workflows/<name>.yml` — this repo currently has none. Check
out only what the job reads; do not add `submodules: recursive`; resolve sub-repo refs by
branch name with a `beta` fallback rather than hardcoding `main`.

**Firmware/host-app code:** not here. Commit inside `firestarter_fw/` or `firestarter_app/`
on the milestone branch; the meta-repo only re-pins the gitlink.

---

---

## Python Application: `firestarter_app/`

*[unverified in 2026-08-26 and 2026-09-14 scoped remaps — submodule contents, out of scope]*

```
firestarter_app/
├── pyproject.toml                   # Build config: setuptools, version from SCM, entry point
├── requirements.txt                 # Dev/test dependencies
├── CLAUDE.md                        # AI development guidance
├── README.md                        # User documentation
├── MANIFEST.in                      # Package file inclusion rules
├── firestarter_test.sh              # Comprehensive hardware test suite (bash)
├── write_test.sh                    # Write/verify focused test script (bash)
│
├── firestarter_fw/                     # Main Python package
│   ├── __init__.py                  # Version string: __version__ = "2.0.7_dev"
│   ├── main.py                      # CLI entry point; argparse + command dispatch
│   ├── eprom_operations.py          # EpromOperator: read/write/verify/erase/blank/id
│   ├── serial_comm.py               # SerialCommunicator: port discovery, protocol I/O
│   ├── database.py                  # EpromDatabase singleton: EPROM DB + pin translation
│   ├── config.py                    # ConfigManager singleton: ~/.firestarter/config.json
│   ├── firmware.py                  # FirmwareManager: version check, download, avrdude flash
│   ├── hardware.py                  # HardwareManager: VPP/VPE voltage, HW revision/config
│   ├── eprom_info.py                # EpromConsolePresenter: formats EPROM info for display
│   ├── ic_layout.py                 # EpromSpecBuilder: builds technical spec dictionaries
│   ├── logging_utils.py             # SingleLineStatusHandler: in-place console status lines
│   ├── constants.py                 # Command codes, flag bits, baud rate, buffer sizes
│   ├── utils.py                     # hex-string-to-decimal helper
│   ├── avr_tool.py                  # Avrdude wrapper: locate binary, flash .hex files
│   └── data/                        # Bundled data files (included in package)
│       ├── minipro_complete_db.json # Primary EPROM database (new format)
│       ├── database_generated.json  # Legacy generated database
│       ├── database_overrides.json  # Override entries for generated database
│       ├── pin-maps.json            # Legacy pin map configurations
│       └── pinouts.json             # Current pinout definitions keyed by variant name
│
├── doc/                             # Additional documentation
├── images/                          # Screenshot/diagram assets
├── tools/                           # Developer utilities
├── build/                           # Build artifacts (not committed)
├── firestarter.egg-info/            # Installed package metadata
│
└── .planning/                       # GSD planning documents
    └── codebase/                    # Codebase analysis (this directory)
        ├── ARCHITECTURE.md
        └── STRUCTURE.md
```

### Key Python Files by Role

| File | Class/Function | Role |
|------|---------------|------|
| `main.py` | `main()` | CLI entry, argparse, command routing |
| `eprom_operations.py` | `EpromOperator` | All EPROM hardware operations |
| `serial_comm.py` | `SerialCommunicator` | Serial port I/O and protocol |
| `database.py` | `EpromDatabase` | EPROM spec lookup and pin translation |
| `config.py` | `ConfigManager` | Persistent user config (~/.firestarter/) |
| `firmware.py` | `FirmwareManager` | Firmware version, download, flashing |
| `hardware.py` | `HardwareManager` | VPP/VPE voltage, HW revision |
| `eprom_info.py` | `EpromConsolePresenter` | Console display of EPROM details |
| `ic_layout.py` | `EpromSpecBuilder` | Technical spec dict construction |
| `constants.py` | (module-level) | All shared constants and flag bits |
| `avr_tool.py` | `Avrdude` | avrdude subprocess wrapper |

### User Config Location

```
~/.firestarter/
├── config.json        # Saved port, avrdude paths, hw config
├── database.json      # User EPROM database overrides (optional)
└── pin-maps.json      # User pin map overrides (optional)
```

---

## Arduino Firmware: `firestarter_fw/`

*[unverified in 2026-08-26 and 2026-09-14 scoped remaps — submodule contents, out of scope]*

```
firestarter_fw/
├── platformio.ini               # Build environments: uno, leonardo
├── name_firmware.py             # Pre-build script: names .hex by board
├── CLAUDE.md                    # AI development guidance
├── README.md                    # Firmware documentation
│
├── src/                         # Firmware source files
│   ├── firestarter.cpp          # Main loop, command dispatch, state machine
│   ├── eprom_operations.cpp     # read/write/verify/erase/blank_check/chip_id
│   ├── hardware_operations.cpp  # VPP/VPE voltage reading, HW revision, config
│   ├── json_parser.c            # JSON command parsing (C, not C++)
│   ├── logging.c                # Serial response formatting (prefix-tagged)
│   ├── operation_utils.cpp      # Shared operation helpers
│   ├── rurp_config_utils.cpp    # EEPROM-persisted hardware config (R1/R2/rev)
│   ├── dev_tools.cpp            # Dev commands: direct register/address access
│   │
│   ├── boards/                  # Board-specific hardware abstraction
│   │   ├── rurp_common.cpp      # Common RURP shield logic
│   │   ├── uno_rurp_shield.cpp  # Arduino Uno implementation
│   │   ├── leonardo_rurp_shield.cpp  # Arduino Leonardo implementation
│   │   └── rurp_serial_utils.cpp    # Serial utility functions
│   │
│   └── proms/                   # Memory device type handlers
│       ├── eprom.cpp            # UV-erasable EPROM support
│       ├── flash_type_3.cpp     # Flash memory type 3 (AMD standard)
│       ├── flash_type_4.cpp     # Flash memory type 4 (AMD alternate)
│       ├── flash_utils.cpp      # Shared flash operation utilities
│       ├── memory.cpp           # Generic memory operations base
│       └── sram.cpp             # SRAM device support
│
├── include/                     # Header files
│   ├── firestarter.h            # firestarter_handle_t, bus_config_t definitions
│   ├── eprom.h / eprom_operations.h  # EPROM op declarations
│   ├── hardware_operations.h    # Hardware op declarations
│   ├── json_parser.h            # JSON parser interface
│   ├── logging.h                # Logging/response interface
│   ├── memory.h / memory_utils.h     # Memory abstraction
│   ├── rurp_shield.h            # RURP shield register definitions
│   ├── rurp_types.h             # Shared type definitions
│   ├── rurp_register_utils.h    # Register manipulation helpers
│   ├── rurp_hw_rev_utils.h      # Hardware revision detection
│   ├── rurp_internal_register_utils.h
│   ├── rurp_serial_utils.h
│   ├── flash_type_3.h / flash_type_4.h / flash_utils.h / sram.h
│   ├── operation_utils.h
│   ├── dev_tools.h
│   └── version.h                # Firmware version constant
│
├── lib/                         # Local libraries (PlatformIO convention)
│
├── test/                        # Unit tests (pio test)
│   └── test_data/               # Test binary data files
│
├── test_data/                   # Test binary fixtures
│
└── .pio/                        # PlatformIO build cache (not committed)
```

### Key Firmware Files by Role

| File | Role |
|------|------|
| `src/firestarter.cpp` | Main loop, JSON dispatch, three-phase state machine |
| `src/eprom_operations.cpp` | Core EPROM/Flash/EEPROM operations |
| `src/hardware_operations.cpp` | Voltage measurement, revision detection |
| `src/json_parser.c` | Parses `{...}` JSON commands from serial |
| `src/logging.c` | Emits `OK:`, `DATA:`, `ERROR:`, `MAIN:`, etc. |
| `include/firestarter.h` | Central `firestarter_handle_t` state struct |
| `include/rurp_shield.h` | Hardware register and pin definitions |

---

## Build Environments

*[unverified in 2026-08-26 and 2026-09-14 scoped remaps — submodule contents, out of scope]*

### Python Application
- **Python:** 3.11+
- **Build:** `pip install -e .` (setuptools + setuptools_scm)
- **Entry point:** `firestarter` → `firestarter.main:main`
- **Runtime deps:** `pyserial`, `requests`, `tqdm`, `argcomplete`, `rich`

### Arduino Firmware
- **Build tool:** PlatformIO
- **Targets:** `uno` (ATmega328P, 512-byte buffer), `leonardo` (ATmega32U4, 1024-byte buffer)
- **Serial speed:** 250000 baud
- **Key flags:** `HARDWARE_REVISION` (enabled), `DEV_TOOLS` (enabled), `SERIAL_DEBUG` (commented out)

---

## Where to Find Things

*[unverified in 2026-08-26 and 2026-09-14 scoped remaps — submodule contents, out of scope]*

| Task | Location |
|------|----------|
| Add a new CLI command | `firestarter_app/firestarter/main.py` — add `create_*_args()` and dispatch in `main()` |
| Add a new EPROM operation | `firestarter_app/firestarter/eprom_operations.py` + corresponding firmware op |
| Change serial protocol | `firestarter_app/firestarter/serial_comm.py` + `firestarter_fw/src/firestarter.cpp` |
| Add an EPROM to the database | `firestarter_app/firestarter/data/minipro_complete_db.json` or `~/.firestarter/database.json` |
| Change pin-map / bus config | `firestarter_app/firestarter/data/pinouts.json` or `database.py::pin_conversions` |
| Modify firmware main loop | `firestarter_fw/src/firestarter.cpp` |
| Add a new memory device type | `firestarter_fw/src/proms/` (new .cpp + header) |
| Change board HAL | `firestarter_fw/src/boards/` |
| Adjust user config persistence | `firestarter_app/firestarter/config.py` |
| Modify firmware flash/install | `firestarter_app/firestarter/firmware.py` + `avr_tool.py` |
| Change constants/flags | `firestarter_app/firestarter/constants.py` + `firestarter_fw/include/firestarter.h` |

---

*Meta-repo structure analysis: 2026-09-14 (scoped remap)*
*Submodule structure analysis: 2026-05-08*
