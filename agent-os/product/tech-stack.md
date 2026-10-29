# Tech Stack

## Repository Layout

- Meta repo `henols/firestarter`: the single issue tracker. It holds the submodule pointers,
  `tools/catalog/` (message codegen), `VALIDATED-EPROMS.md`, `RELEASING.md` (the release
  runbook), `agent-os/` (mission, roadmap, tech stack, standards, specs), `.claude/skills/`, the
  devcontainer, and `agent-os/todos/` (open defect records). The GSD-era `.planning/` tree was
  retired on 2026-09-27; it is reachable at the tag `archive/planning-tree-final` and explained in
  `agent-os/PLANNING-ARCHIVE.md`.
- `firestarter_app/` (`henols/firestarter_app`): the host CLI and the chip database generator.
- `firestarter_fw/` (`henols/firestarter_fw`): the firmware.
- User documentation: the `firestarter` GitHub wiki, plus each repo's `README.md`. The only change
  log is `CHANGELOG.md` in the meta repo.
- Branches: `main` only, in all three repos. Work branches fork from `main` and return by PR.
  The `beta` branches were retired; their last state is at the tag `archive/beta`.
- All three repos carry an identical active `Protect main` ruleset, scoped to `~DEFAULT_BRANCH`,
  with `deletion`, `non_fast_forward` and `pull_request`. The only bypass actor is `DeployKey`;
  GitHub Actions is not one, and `current_user_can_bypass` is `never`, so the owner cannot push to
  `main` directly either. Changes go in as PRs.

## Host Application (`firestarter_app`)

- Python ≥ 3.11. CI uses 3.11 only. The devcontainer has 3.12, which can hide CI failures. A setuptools package named
  `firestarter`, entry point `firestarter.main:main`.
- Dependencies: click (CLI), pyserial, requests (GitHub release download), tqdm, rich, packaging.
  Optional `py32` extra: pyusb (USB DFU).
- Quality gates: pytest (coverage floor 70 %), syrupy snapshots, ruff (`E,F,I,UP`) and ruff format,
  mypy strict on a set of listed modules.
- Data: `firestarter/data/chip_database.json` (generated) and `pinouts.json`. User config and
  overrides are in `~/.firestarter/`.
- Generator: `tools/build_db.py` reads minipro `infoic.xml` from upstream at run time.
  `datasheet_overrides.json` and `extra_chips.json` supply corrections. `tools/baseline/` holds the
  regression anchor.

## Firmware (`firestarter_fw`)

- C/C++ with the Arduino framework on PlatformIO. AVR targets: `uno`, `uno328pb` and `leonardo`. The
  vendored jsmn library parses JSON.
- PY32F071 target: CMake and arm-none-eabi under `platform/py32f071/`, with the OpenPuya SDK and
  CherryUSB CDC. A fake Arduino core lets it share the command processor and the PROM algorithms.
- Tests: Unity native tests (`pio test -e native` and `-e native_nodevtools`), with golden
  register-trace recorders. A second Python test tree is in `tests/`.
- Flash is the main constraint. Leonardo has a 28672 B Caterina limit and is the tightest target.
  Record the RAM size together with the flash size for every change.
- Hardware calibration (R1/R2, shield revision) is in EEPROM on AVR. On PY32F071 it is in dual-slot
  CRC32 flash records.

## Wire Protocol

- USB serial at 250000 baud. JSON commands and binary data blocks. Both are framed with COBS
  (`0x00`) and CRC8.
- Data buffer: Uno-class and PY32F071 512 B, Leonardo 1024 B. The host reads the size from the
  firmware identity string.
- Message IDs have one byte and come from one catalog (`tools/catalog/messages.toml` in the meta
  repo). `codegen.py` generates `messages.h` and `messages.py`. Generate them in the meta repo only.
  Do not edit them by hand.

## CI and Release

- GitHub Actions in both sub-repos. The meta repo has no CI.
- Only a version-tag push publishes. A tag `X.Y.ZbN`/`X.Y.ZrcN` cuts a pre-release, and `X.Y.Z`
  cuts a stable release marked Latest. For the app, both go to GitHub and PyPI in one
  `release.yml` run. A merge to `main` publishes nothing.
- The tag is the version. The app uses `setuptools-scm`, and the firmware uses
  `version_from_git.py`. No file holds the version and no bot commits a bump.
- The two sub-repos release independently. The meta `release` skill
  (`.claude/skills/release/scripts/release.py`) releases both. `RELEASING.md` is the runbook.
- Stable firmware is built without `DEV_TOOLS`. Pre-release firmware is built with `DEV_TOOLS`.

## Architectural Decisions That Constrain Future Work

- The `algorithm` (minipro `protocol_id`) is the only dispatch key. The legacy `mem_type`/`type`
  axis is removed. `protocol == 0` and unknown protocols fail closed.
- Never hand-edit `chip_database.json`. Fix the generator or add an override that cites a datasheet.
- A serial protocol change needs matching edits in `serial_comm.py` and `firestarter.cpp`.
  `constants.py` and `firestarter.h` duplicate the flag bits, so change both files together. Ship
  firmware before the host that depends on it.
- The host refuses a non-`supported` chip before it sends a serial byte.
- The 27C protocols share one per-byte loop. The protocol sets the shape of the loop. The database
  sets the pulse. Do not add a second dispatch key.
- VPP is set by hand (potentiometer) on every board. On AVR boards this is permanent.
- Compare and blank-check logic runs on the host. The firmware only reads and writes.
- Every new check ships with a test that proves it fails on a planted violation.
- Evidence ceiling: no shield can reach the ~6.25 V program VCC that the vendor algorithms assume,
  and VPE tops out near 22.5 V. Claims state timing fidelity, not datasheet conformance.
