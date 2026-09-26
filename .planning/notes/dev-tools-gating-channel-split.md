---
title: Dev-tools gating — release channel IS the gate (supersedes gh#8's build-flag design)
date: 2026-07-28
context: /gsd-explore session on gating dev commands out of production; reworks Backlog 999.15 / gh#8
---

# Dev-tools gating via release channel

Design decisions from a `/gsd-explore` session on Backlog **999.15** / [gh#8](https://github.com/henols/firestarter_prom/issues/8)
("Gate development tools out of production builds"). The session **changed the mechanism**
and **resolved the recorded v1.21 conflict**. Read this before scoping 999.15 — the stub's
original design is partly superseded.

Anchor code: `dev` group at `firestarter_app/firestarter/cli_handlers.py:960`; `DEV_TOOLS`
guards at `firestarter/include/firestarter.h:42` and `firestarter/src/firestarter.cpp:75,90,230`;
shared `[env] build_flags` at `firestarter/platformio.ini:20-28`.

## The load-bearing finding: only 2 of 8 dev subcommands are firmware-gateable

The `dev` group has **eight** subcommands. Only **two** send a dev-only firmware command ID.
Every other one is assembled out of *production* command IDs, so a firmware flag cannot gate
it without disabling the production feature it rides on.

| `dev` subcommand | firmware command sent | FW-gateable? |
|---|---|---|
| `reg` | `CMD_DEV_REGISTER` (8) | ✅ dev-only ID |
| `addr` | `CMD_DEV_ADDRESS` (7) | ✅ dev-only ID |
| `read` | `COMMAND_READ` (1) — `eprom_operations.py:1428` | ❌ same ID as `firestarter read` |
| `consistency-check` | production reads | ❌ |
| `write-cycle` | production writes | ❌ |
| `fault-inject` | *deliberately malformed* production frames | ❌ gating is meaningless — sending garbage is the point |
| `validate-family` | orchestration over production commands | ❌ |
| `test` | production read / verify / chip-id / vpp / vpe | ❌ |

Consequence: the "install dev firmware to unlock the dev tools" framing only ever unlocks
`reg` + `addr`. The other six are a **host-side packaging decision with no firmware half at all**.

## The decision: split by release channel, not by build flag

**Operator decision (2026-07-28):** keep the production release and the pre-release
(`--pre`) channels separated, and let the channel be the gate.

- **Stable release** (`pip install firestarter`, stable `.hex` assets): exposes **only
  `dev read` and `dev test`**. All six others are absent. Firmware built **without** `DEV_TOOLS`.
- **Pre-release** (`pip install --pre firestarter`, prerelease `.hex` assets): full `dev`
  group. Firmware built **with** `DEV_TOOLS`.
- **Dev environment** (devcontainer / source checkout): firmware **always** builds with dev tools.

"If you want the dev tools you install the pre-release of the app."

## Why this is cheaper than gh#8's recorded design

**1. The firmware channel flag already exists and is bench-validated.**
`firestarter fw --pre` is shipped, with help text literally *"Fetch latest pre-release
firmware (mirrors pip install --pre)"* (`cli_handlers.py:797`), plus `--stable` as its
counterpart (`cli_handlers.py:808`). The prerelease-asset route was bench-validated in
v1.21 Phase 115. So:

- **No new `fw --dev` flag is needed.**
- **No `firestarter_uno_dev.hex` fourth naming axis is needed** — same asset name, different
  content per channel. This preserves the `RURP_BOARD_NAME` triple-lock (build flag = artifact
  filename = handshake `<board>` slot), which a `*_dev.hex` asset would have broken. See
  `firestarter/name_firmware.py` and the asset-name match at `firestarter/firmware.py:155`.

**2. The app can gate off its own version string.** `__version__ = "3.0.0b11"` is a single
importable string (`firestarter_app/firestarter/__init__.py:1`) that `pyproject.toml` reads
dynamically (`version = { attr = "firestarter.__version__" }`). Pre-release forms carry
`bN`/`rcN`; stable is a bare `X.Y.Z`. So Click registration can key off the package's own
version — **no env var, no config key, no new flag, no branch detection at runtime.**

**3. CI needs zero changes to fail safe.** Both firmware workflows run a bare `pio run`
with no `-e` (`firestarter/.github/workflows/build.yml:111`,
`.github/workflows/beta-build.yml:77`), so they build `default_envs = uno, uno328pb, leonardo`.
Keep those as the production envs and CI **cannot accidentally ship dev tools**. The inverse
(dev-by-default + explicit `-release` envs) requires editing both workflows and fails *open*
on any mistake.

**4. Nothing under `test/` references `DEV_TOOLS` or `CMD_DEV_*`** (verified by grep over the
whole firmware `test/` tree). So `[env:native]` does **not** need the flag — the current
inheritance from `[env] build_flags` is pure leak, not a dependency.

**5. The build marker comes for free.** Dev tools now only ever exist in `bN`/`rcN`-versioned
builds, so `3.0.0b11` *means* "has dev tools" and `3.0.1` *means* "doesn't". That distinction
already flows into `fw_board_identity` (`version:board`) in every `dev test` report
(`diagnostic_report.py:330`), which is what community submissions file into the tracker. **No
`+dev` version suffix and no handshake capability bit are required.** (Worth knowing what was
*not* needed: `fw_get_version` returns a bare `OK: FW: 3.0.0b11`
(`firestarter/src/hardware_operations.cpp:97-98`) and `MSG_OK_READY` carries only
`DATA_BUFFER_SIZE` — there is **no dev-capability bit in the handshake today**, and this design
means none has to be added. Adding one would be a wire change colliding with v1.23.)

## ⚠ Risks this design creates — all four must land in the phase's scope

**R1 — It permanently welds "beta channel" to "dev tools enabled."** Every future beta becomes
a dev-tools build, so community beta testers — exactly the people v1.21's `dev test` was built
for — get the full hazardous surface (`reg`, `addr`, `write-cycle`, `fault-inject`) whether they
want it or not. Defensible (running `--pre` is a deliberate act), but the gate then protects
stable users and no one else. Decide explicitly; don't let it be an accident.

**R2 — Mixed-channel pairs stop being corner cases.** The app and firmware channels are
installed independently (`pip install --pre` vs `firestarter fw --pre`), so **beta-app +
stable-firmware becomes a likely combination**, not an exotic one — and in that pair the app
offers `reg`/`addr` that the firmware will reject. This promotes gh#8's *"prove a production
build does not desynchronize the COBS/CRC stream when it rejects a dev command ID"* from
nice-to-have to **load-bearing**, and makes the explicit 2×2 app/firmware capability matrix
mandatory rather than documentation garnish.

**R3 — The editable-install trap.** If gating keys off `__version__`, the operator's own
devcontainer editable install obeys whatever `__init__.py` says. The moment that string is a
bare `X.Y.Z` — between betas, or at a stable cut — **the bench loses `dev reg`, which is
load-bearing project tooling**: `dev reg 0 0 0x86 -f` is the held-erase-rail DMM proxy (see
`reference_v114_bench_erase_rail_and_test_artifact`, `reference_held_rail_dtr_reset_hold_script`).
A deliberate source-checkout override must be designed up front, not discovered at a stable cut.

**R4 — Surface tests must assert the registered command set, not exit codes.** A "stable
rejects `dev reg`" test passes vacuously whether the command is *absent* or
*present-but-broken-for-an-unrelated-reason*. Same false-green trap class as the absent-chip
case in v1.21 Phase 114.1 (`reference_dev_test_absent_chip_false_green_trap`). The load-bearing
assertion is on the **set of registered Click commands / `--help` surface**, plus shell
completion.

## ⚠ Fail-open trap to design around (mechanism-level)

The obvious PlatformIO mechanism — `-D DEV_TOOLS=${sysenv.FIRESTARTER_DEV_TOOLS}` — is
**dangerous**: with the variable unset that plausibly expands to `-D DEV_TOOLS=`, which still
*defines* the macro, so `#ifdef DEV_TOOLS` stays true and the flag leaks into every release
build. That is precisely the bug class being removed. The safe shape is for the env var to
carry the **whole flag**:

```ini
build_flags =
	...
	${sysenv.FIRESTARTER_DEV_FLAGS}     ; devcontainer exports: -D DEV_TOOLS
```

so unset → nothing appended. **This must be proven by an actual build + symbol check, never
assumed** — see the paired todo `prove-pio-dev-flag-fails-closed.md`.

## Smaller items

- **The `dev` group docstring becomes misleading.** It reads *"Debug command for development
  purposes. USR button will break command and return."* (`cli_handlers.py:963`). If `dev read`
  + `dev test` are the supported stable surface, that text actively warns off the users they
  are being kept for. Either reword it per-channel or revisit the namespace.
- **The namespace question stays open but deferred.** The operator chose to keep both survivors
  under `dev` (`dev read`, `dev test`) rather than promoting them to a supported `diag`/top-level
  namespace. gh#8's own §5 deferred the namespace decision "to a later issue"; this session
  deferred it again, deliberately. Note that *both* survivors are read-path/production-ID
  commands with no direct bus poking — i.e. they are shaped like supported diagnostics, which is
  the argument for promoting them later.
- **Host version-compare regex.** `firmware.py:47` accepts stable `X.Y.Z` plus pre-release
  `X.Y.ZbN` / `X.Y.ZrcN`. This design does **not** add a `+dev` local-version segment, so that
  regex needs no widening — but any later decision to add a build marker would touch it.
- **`SERIAL_DEBUG` stays out.** gh#8 explicitly does not restore the removed `SERIAL_DEBUG`
  bootstrap. `SERIAL_DEBUG`, `DEBUG_ADDRESS` and `EXTRA_INFO_LOGGING` are already commented out
  in `[env] build_flags` — same flag class, and they are the reason the block deserves a
  deliberate policy rather than another ad-hoc edit.

## Relationship to gh#3's policy

gh#3 (closed 2026-07-27 as superseded by gh#8) required "central opt-in flags rather than
scattered hard-coded checks **or branch-dependent behavior**." A channel/branch-conditioned
*build default* is a much milder thing than what that warned about — one central flag chosen
once per pipeline, versus runtime checks scattered through the code — but it is the same words.
**The phase should state that distinction deliberately** rather than silently contradict its
own source issue.
