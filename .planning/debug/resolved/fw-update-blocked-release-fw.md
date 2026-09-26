---
status: resolved
resolved: 2026-08-19
trigger: "it doesent seams that the latetest pre release of the firestarter app cant update the firmware on the uno if the is a release firmware installed, there are 3 boards cinnected that you can run the tests automaticly without asking me"
created: 2026-08-19
updated: 2026-08-19
related_phase: 149 (not started) — surfaced during v1.32
milestone: v1.32
sub_repo: firestarter_app (primary) + firestarter (firmware ack contract)
goal: find_and_fix
---

# Debug Session: fw-update-blocked-release-fw

## Symptoms

DATA_START

**User report (verbatim, treat as data):** "it doesent seams that the latetest pre release of
the firestarter app cant update the firmware on the uno if the is a release firmware installed,
there are 3 boards cinnected that you can run the tests automaticly without asking me"

**Expected behavior:** A pre-release build of the host app (`firestarter` 3.0.0b20/b21) running
`firestarter fw` / `firestarter fw --install` against an Uno that currently has **release
(stable-channel) firmware** installed should read the current firmware version, compare it to the
latest available firmware, and offer/perform the update. The stable→pre-release firmware upgrade
path must be reachable — that is the only way a user on stable firmware gets onto a beta build.

**Actual behavior (reproduced by the orchestrator on the bench, 2026-08-19):** the command aborts
before it ever reaches the update decision. Both Uno-class boards fail identically:

```
$ python -m firestarter.main --port /dev/ttyACM1 fw
Reading current firmware version...
Connecting...Connecting... Failed
Error: Firmware outdated: Programmer did not report a firmware version in its operation-setup ack.
This host requires firmware that carries the version and hardware revision in that ack.
Please upgrade the firmware using 'firestarter fw --install'.

$ python -m firestarter.main --port /dev/ttyUSB0 fw
(identical error)
```

The Leonardo, which carries **pre-release** firmware, works fine:

```
$ python -m firestarter.main fw
Current firmware version: 3.0.0b17, for controller: leonardo on port /dev/ttyACM0
Firmware is already up to date (version 3.0.0b17 for leonardo). Use --force to reinstall.
```

Note the self-referential dead end: the error tells the user to run `firestarter fw --install`,
which is the very command suspected of hitting the same gate. **Whether `--install`/`--force`
actually bypasses the gate is the first thing to establish empirically — it decides whether this is
a hard deadlock (no upgrade path at all) or only a bad/misleading error message on the bare `fw`
path.**

DATA_END

## Environment / bench inventory (verified 2026-08-19, ports were free, no stale processes)

| Port | `by-id` identity | Firmware | `fw` result |
|---|---|---|---|
| `/dev/ttyACM0` | `Arduino_LLC_Arduino_Leonardo` | 3.0.0b17 (pre-release) | works, reports version |
| `/dev/ttyACM1` | `Arduino__www.arduino.cc__0043_...` (genuine Uno R3) | unknown — refused | FirmwareOutdatedError |
| `/dev/ttyUSB0` | `1a86_USB_Serial` (CH340 clone Uno) | unknown — refused | FirmwareOutdatedError |

- Host app: source tree `firestarter_app` on branch `gsd/v1.32-at28c-write-path-root-cause-report-provenance`, `firestarter.__version__ = 3.0.0b21`, installed dist metadata `3.0.0b20`. Both are PEP 440 pre-releases, so `is_prerelease_build()` is True and D-23 auto-routes to the `--pre` channel.
- Port identity must be re-verified per task; `/dev/ttyACM*` numbers shuffle across replug.

## Fault locus already narrowed by the orchestrator

`firestarter_app/firestarter/serial_comm.py:860-878` — the port-detection/connect path reads
`communicator.firmware_identity` from the operation-setup ack (`MSG_OK_READY`) and applies
`re.match(r"[\d.x]+", identity)`. When the ack carries **no** identity blob, `version_match is
None` and it raises `FirmwareOutdatedError` with the message above.
`firestarter_app/firestarter/cli_handlers.py:202` (`map_typed_errors`) turns that into a
`ClickException`, which aborts the `fw` command.

The version-in-ack contract is a **v1.31 (beta) firmware feature** — `MSG_OK_READY` was extended
into a length-discriminated blob carrying version + hardware revision (CAP-01/CAP-02) with zero
codegen. Release/stable firmware predates that extension, so it legitimately sends a bare ack. The
suspicion is therefore an **ordering/layering defect, not a protocol defect**: the host applies a
beta-only capability gate on the *connect* path that `fw` shares with chip operations, so the one
command whose entire job is to *replace* the outdated firmware is blocked by the outdatedness of
that firmware.

Secondary candidate (independent, may also be live — do not let it mask the primary): the
PEP 440 direction of `FirmwareManager._compare_versions` at `firmware.py:257-272`
(`Version(current) >= Version(latest)`). If the installed firmware is a *final* release
(`3.0.0`) and the latest pre-release firmware is `3.0.0b18`, PEP 440 orders `3.0.0 > 3.0.0b18`, so
`is_up_to_date` is True and `fw --install` would report "already up to date" and refuse — a second,
distinct way a release firmware cannot be updated by a pre-release app. Note the Leonardo run above
already printed "already up to date" while sitting on `3.0.0b17` when `origin/beta` firmware is
`3.0.0b18`, which is itself suspicious and worth explaining.

Also observed, cosmetic: `fw` rejects `-v` (`Error: No such option: -v`) — the global verbose flag
must precede the subcommand. Not the bug; do not chase it.

## Hard constraints for this investigation

1. **Operator pre-authorized autonomous bench testing on all 3 boards** — run read-only and
   diagnostic commands freely, no confirmation needed.
2. **DO NOT flash an Uno-class board (`/dev/ttyACM1`, `/dev/ttyUSB0`).** An Uno-class firmware
   upload drives the shield bus, so a chip left seated in the socket can be damaged. Nobody has
   confirmed the sockets are empty, and with the firmware gate active the host cannot probe for a
   seated chip. The Leonardo (`/dev/ttyACM0`) is exempt from that hazard. If end-to-end proof
   genuinely requires an Uno flash, stop and report it as a blocked verification step for the
   operator rather than flashing.
3. **`fw --install` / `--force` is not a dry run.** `manage_firmware_update` computes
   `board_to_use = current_board or board_override`, so the *detected* board beats `--board`, and it
   resolves a **GitHub release asset** — on a milestone branch with no release it silently flashes
   *beta*. Use `fw` (bare), `fw --list`, `fw --dfu-probe` for read-only probing. Prove the decision
   path with unit tests / monkeypatched installer rather than real flashes.
4. `chip_database.json` is generated — never hand-edit it (not expected to be involved here).
5. Firmware branch archaeology compares against `beta`, not `main` (`main` lags ~224 commits).

## Current Focus

hypothesis: (both confirmed and fixed — see Resolution)
test: (complete)
expecting: (complete)
next_action: none — ALL FOUR defects fixed and hardware-verified. (1) the CAP-02 ack-identity deadlock and the stable-channel auto-route (this session's original scope, commit `ebbc299`); then, found while exercising the full update-path matrix and fixed on operator request: (A) `--port` restricted nothing, so the app could flash board A with board B's asset, (B) genuine 2.x stable firmware was unupdatable because the update path demanded a readable version it can never get, and (C) a one-shot `--port` leaked into the persisted config. The operator's original "release firmware installed" report is now genuinely closed: reproduced with real stable 2.0.6 firmware and upgraded to 3.0.0b19 via `fw --board uno --install`. Commits are unpushed and submodule pointers deliberately not bumped, so a later phase owns the lockstep decision.

## Evidence

- timestamp: 2026-08-19 — bare `fw` on both Uno-class ports raises FirmwareOutdatedError from `serial_comm.py:867`; bare `fw` on the pre-release-firmware Leonardo succeeds. Confirms the failure correlates with the firmware's ack capability, not with the board type or the port driver (one Uno is genuine ACM, the other a CH340 USB-serial clone, and both fail the same way).
- timestamp: 2026-08-19 H1 static — `manage_firmware_update` (firmware.py:752) calls `check_current_firmware` as its FIRST statement with NO try/except; `check_current_firmware` (firmware.py:216-217) has `except FirmwareOutdatedError: raise`. The `fw` Click handler (cli_handlers.py:1257) does not catch it either, so `map_typed_errors` (cli_handlers.py:200-201) renders it as a ClickException. Implication: --install/--force cannot possibly reach the download/flash decision.
- timestamp: 2026-08-19 H1 empirical (all flash paths stubbed with 4 independent tripwires: `_download_firmware_file`, `_install_firmware`, `_install_with_avrdude`, `Avrdude.__init__`) — `fw --install`, `fw --force`, `fw --install --pre`, `fw --firmware-version 3.0.0b19` on /dev/ttyACM1 AND /dev/ttyUSB0: all exit 1 with `Firmware outdated: Programmer did not report a firmware version...`, and FLASH-PATH CALLS == [] in every one of the 6 runs. H1 CONFIRMED — hard deadlock, no in-app upgrade path.
- timestamp: 2026-08-19 raw ack dump (spy on the real `_decode_id_frame`; sends only CMD_FW_VERSION, read-only):
    - /dev/ttyACM1: ack body `01 02 00 41` (id=MSG_OK_READY, params=`02 00`=512 buffer, crc) — 2 param bytes only, NO CAP-02 tail. firmware_identity=None, hw_revision=None. **Second ack on the same connection carries `FW: 3.0.0b11:uno`.**
    - /dev/ttyUSB0: ack body `01 02 00 41`, identity None. Second ack `FW: 3.0.0b11:uno328pb`.
    - /dev/ttyACM0: ack body `01 04 00 02 11 "3.0.0b17:leonardo" 00 00 c2` — full CAP-02 tail (hw_rev=2, ver_len=0x11), identity `3.0.0b17:leonardo`.
  Implication A: the ack genuinely LACKS the identity blob on both Unos; the host is not mis-parsing an identity that is present. Implication B (decisive): the version the update path needs is ALREADY on the wire one ack later, in the CMD_FW_VERSION text payload that `check_current_firmware` is written to read — the connect-path gate aborts before that payload is read. Implication C: the boards do not carry a *stable* release (latest stable firmware is 2.0.6); they carry pre-release 3.0.0b11, which predates CAP-02. The user's "release firmware" framing is imprecise but the defect class is identical and strictly broader — every stable release (<=2.0.6) and every beta up to ~b16 lacks CAP-02.
- timestamp: 2026-08-19 channel resolution measured on /dev/ttyACM0 with a spy on `fetch_release_info` + `_compare_versions`:
    - bare `fw`  -> channel='stable', latest_version='2.0.6', `_compare_versions('3.0.0b17','2.0.6')`=True -> "already up to date". EXPLAINS THE ANOMALY: the verdict is against the STABLE channel, so 3.0.0b19 is invisible.
    - `fw --force` -> channel='stable', resolved URL `.../2.0.6/firestarter_leonardo.hex` and the download stub WAS reached. Without the stub this would have flashed **2.0.6 — a downgrade** to firmware that lacks CAP-02, i.e. the escape hatch bricks the pairing.
    - `fw --install` -> channel='pre', latest 3.0.0b19, is_up_to_date=False, correct download URL. Only `--install` auto-routes.
  Cause: `_maybe_auto_route_to_pre` (cli_handlers.py:282-288) gates the D-23 auto-route on `install=True`, so neither bare `fw` nor `fw --force` gets the pre channel.
- timestamp: 2026-08-19 `fw --list` against GitHub: latest stable firmware = **2.0.6** (2025-11-16); latest prerelease = **3.0.0b19**. There is NO stable 3.x firmware, so the `_compare_versions` scenario in the session's secondary candidate ("installed 3.0.0 final vs latest 3.0.0b18") cannot occur today.
- timestamp: 2026-08-19 seam survey — `check_current_firmware` is the ONLY production caller of `find_and_connect` with `{"state": COMMAND_FW_VERSION}`, and `manage_firmware_update` is its only caller. `serial_comm.py:1040` is the module `__main__` demo; `eprom_operations.py:1616` builds a bare `SerialCommunicator` and never goes through the gate. So a relaxation parameter threaded caller->`find_and_connect`->`_probe_port` reaches exactly one production call site.
- timestamp: 2026-08-19 POST-FIX bench verification (same 4 flash-path tripwires armed; nothing flashed):
    - `--port /dev/ttyACM1 fw`   -> exit 0, "Current firmware version: 3.0.0b11, for controller: uno", channel='pre', latest 3.0.0b19, is_up_to_date=False, prompts "New firmware 3.0.0b19 available for uno (current: 3.0.0b11). Update now?", answered n -> cancelled. FLASH-PATH CALLS [].
    - `--port /dev/ttyUSB0 fw`   -> same, board resolved as `uno328pb`, asset `firestarter_uno328pb.hex`.
    - `--port /dev/ttyACM1 fw --install` -> reaches the download boundary with `.../3.0.0b19/firestarter_uno.hex`.
    - `--port /dev/ttyUSB0 fw --force`   -> reaches the download boundary with `.../3.0.0b19/firestarter_uno328pb.hex`.
    - `--port /dev/ttyACM0 fw`   -> now reports "New firmware 3.0.0b19 available for leonardo (current: 3.0.0b17)" instead of the false "already up to date".
    - `--port /dev/ttyACM0 fw --force` -> now resolves 3.0.0b19, was resolving the 2.0.6 DOWNGRADE.
- timestamp: 2026-08-19 POST-FIX negative control on live hardware — `firestarter --port <p> hw` (a non-update path that shares `find_and_connect`) STILL refuses on both Unos with the unchanged "did not report a firmware version" message, and still succeeds on the Leonardo ("Hardware revision: Rev 2.0-class"). The waiver did not leak.
- timestamp: 2026-08-19 RED proof — with `git checkout -- firestarter/` (fix reverted) the new suite is 10 failed / 9 passed; the 9 that pass are exactly the twins asserting the strict path and the D-23/D-24 opt-outs, i.e. the tests that must be green both before and after. With the fix reapplied: 19/19.
- timestamp: 2026-08-19 CI-equivalent gates, run as `.github/workflows/ci.yml` runs them:
    - `ruff check firestarter/ tests/` -> All checks passed. `ruff format --check firestarter/ tests/` -> 140 files already formatted.
    - codegen drift gate (messages.py) -> catalog valid, 76 messages, `git diff --exit-code` ZERO diff. Vector codegen -> 12 vectors, ZERO diff. Confirms no protocol/message change was made.
    - mypy: `tools/check_mypy_watermark.py` exits 2 in this devcontainer for an ENVIRONMENTAL reason — py3.12's numpy `__init__.pyi:737` uses a `type` statement that mypy rejects under the repo's `python_version = "3.10"`. Verified pre-existing: the same failure occurs with the fix stashed. To get a real, complete run, `mypy --python-version 3.12 firestarter/ tests/` -> "Found 33 errors in 13 files (checked 142 source files)" — 142 checked (floor is 120), and 33 both WITH and WITHOUT the fix, i.e. zero new type errors. The 3 pre-existing firmware.py errors are at :309/:807/:875, none in the edited region.
    - `pytest tests/ --cov=firestarter --cov-fail-under=70` -> **1660 passed**, 1 warning, 32 snapshots passed, coverage **83.61%**. Zero failures. (`tests/test_flash_path_record_sync.py` does not exist on this branch of firestarter_app.)

## Eliminated

- hypothesis: The host is mis-parsing an identity that IS present in the ack (regex / offset defect).
  evidence: raw `_decode_id_frame` dump on both Unos shows the MSG_OK_READY body is exactly `01 02 00 41` — id + 2 CAP-01 buffer bytes + CRC, len(params_bytes)==2, so the `len(params_bytes) >= 4` arm at serial_comm.py:407 is not even entered. The identity is genuinely absent on the wire; the Leonardo's 25-byte body proves the decoder reads a present identity correctly.
  timestamp: 2026-08-19

- hypothesis: (session secondary candidate, as literally stated) `FirmwareManager._compare_versions` has its PEP 440 comparison the wrong way round (`Version(current) >= Version(latest)`).
  evidence: The direction is correct — "current >= latest" IS the definition of up-to-date. The scenario the candidate describes (installed final `3.0.0` vs latest pre-release `3.0.0b18` reading as up-to-date) (a) cannot occur today because no stable 3.x firmware exists — latest stable is 2.0.6 per `fw --list`, and (b) is the semantically right answer anyway: a final 3.0.0 IS newer than 3.0.0b18, and silently downgrading a final release to a beta would be the defect. The measured "already up to date" anomaly on the Leonardo is fully explained by CHANNEL resolution (latest resolved to 2.0.6, the stable channel), not by comparison direction. `_compare_versions` is left untouched.
  timestamp: 2026-08-19

- hypothesis: Board type or USB-serial driver is implicated (genuine ACM Uno vs CH340 clone).
  evidence: Both Unos fail identically with byte-identical ack bodies (`01 02 00 41`) and both report firmware 3.0.0b11; the Leonardo on the same host succeeds. The discriminator is the firmware's CAP-02 capability, nothing else.
  timestamp: 2026-08-19

- hypothesis: `FIRESTARTER_DEV_ALLOW_PRE_V12=1` offers a usable workaround.
  evidence: `_probe_port` raises on `version_match is None` at serial_comm.py:867-872 BEFORE `_validate_firmware_version` is called at :877, and that env var is only consulted by the latter's `allow_pre_v12` argument. The bypass is structurally unreachable for a missing-identity ack.
  timestamp: 2026-08-19

## Resolution

root_cause: |
  TWO independent host-side defects in `firestarter_app`. Neither is a protocol defect and the
  firmware is not at fault.

  **D1 (primary, the deadlock).** `SerialCommunicator._probe_port` (serial_comm.py:865-872 pre-fix)
  refuses any operation-setup ack that carries no CAP-02 identity tail. That refusal is applied to
  EVERY connect, including the one made by `FirmwareManager.check_current_firmware`, which
  `manage_firmware_update` calls as its FIRST statement (firmware.py:752) and which re-raises
  `FirmwareOutdatedError` (firmware.py:216-217). Nothing between there and `map_typed_errors`
  (cli_handlers.py:200-201) catches it. Causal chain: pre-CAP-02 firmware sends the bare 4-byte
  MSG_OK_READY body `01 02 00 41` -> `firmware_identity` stays None -> the identity regex is
  skipped -> `version_match is None` -> FirmwareOutdatedError -> ClickException -> `fw` aborts
  with a message telling the operator to run `fw --install`, which re-enters the same line. The
  version was never unobtainable: the firmware answers the SAME connection's CMD_FW_VERSION with
  `OK: FW: 3.0.0b11:uno` one ack later, which `check_current_firmware` is already written to parse.
  So the one command whose job is to replace outdated firmware was blocked by that firmware's
  outdatedness.

  **D2 (independent).** `_maybe_auto_route_to_pre` (cli_handlers.py:282-288 pre-fix) gated the D-23
  beta-app pre-channel auto-route on `install=True`. On a pre-release app every other `fw`
  invocation therefore resolved the STABLE channel: bare `fw` compared the board against the newest
  stable firmware (2.0.6) and printed "already up to date", hiding 3.0.0b19; and `fw --force`
  resolved `.../2.0.6/firestarter_<board>.hex` -- a DOWNGRADE onto firmware that lacks CAP-02, i.e.
  the reinstall escape hatch would have bricked the very pairing it was invoked to repair.

  Note on the report's framing: neither Uno carries a *stable* release. Both run pre-release
  **3.0.0b11**. The defect class is identical and strictly broader than reported -- it covers every
  stable release (<= 2.0.6) and every beta up to ~b16.

fix: |
  D1 -- an explicit, caller-declared `allow_outdated_firmware` waiver (default **False**) threaded
  `check_current_firmware` -> `find_and_connect` -> `_probe_port`. It waives exactly two things: the
  missing-identity refusal and the pre-v3 version floor. It does NOT touch
  `_validate_hardware_revision` (still refuses; None is a reject there). Intent is declared by the
  caller, never inferred from the command dict, so no chip operation can acquire it -- and a
  source-level tripwire test pins the set of production modules allowed to pass it. Justification
  for the layer: the gate exists so this host never DRIVES firmware it cannot speak to, and
  `{"state": COMMAND_FW_VERSION}` engages no bus line and no VPP/VPE rail -- it reads one text ack
  and disconnects.

  D2 -- the auto-route condition is now "the operator pinned no channel" instead of "the operator
  typed --install". D-23 (stable-installed app unaffected) and D-24 (`--stable` /
  `--firmware-version` opt out) are unchanged and each gained a new install=False test.

  `_compare_versions` was deliberately NOT changed -- see Eliminated.

verification: |
  - Live bench, all four flash paths stubbed with independent tripwires: both Unos now read
    3.0.0b11, resolve channel='pre', latest 3.0.0b19, the right per-board asset
    (`firestarter_uno.hex` / `firestarter_uno328pb.hex`), verdict not-up-to-date, and reach the
    download boundary under `--install` / `--force`. Leonardo now reports the available b19 instead
    of a false "already up to date", and `fw --force` no longer resolves the 2.0.6 downgrade.
  - Negative control on live hardware: `firestarter hw` (a non-update path sharing
    `find_and_connect`) STILL refuses on both Unos with the unchanged message, and still succeeds
    on the Leonardo.
  - New suite `tests/test_fw_update_path_gate.py`: 19 tests. Proven RED-before/GREEN-after -- 10
    fail against the pre-fix tree, and the 9 that pass there are exactly the twins asserting the
    strict path and the D-23/D-24 opt-outs.
  - Full suite 1660 passed / 0 failed, coverage 83.61% (gate 70%). ruff check + ruff format clean.
    Both codegen drift gates zero-diff. mypy 33 errors before and after (142 files checked).
  - **CLOSED 2026-08-19 — the real Uno-class flash was authorized by the operator and performed
    end-to-end on `/dev/ttyACM1`** (genuine Uno R3, `usb-Arduino__www.arduino.cc__0043_55736303739351B040E1`).
    `python -m firestarter.main -v --port /dev/ttyACM1 fw --install` produced, in one run:
    the waiver firing at its intended site — `SerialComm:907: /dev/ttyACM1: ack carries no firmware
    identity (pre-CAP-02 firmware); proceeding because this is the firmware-update read path` —
    then `OK: FW: 3.0.0b11:uno` read off the *same* connection (confirming the version was never
    unobtainable), channel auto-routed to `pre`, `latest: 3.0.0b19`, the correct asset
    `releases/download/3.0.0b19/firestarter_uno.hex` (70120 bytes), and
    `avrdude 7.1 -p atmega328p -c arduino -b 115200 -P /dev/ttyACM1 -D -U flash:w:...:i`
    reporting success in **8.39s**. The avrdude leg is proven; no step of this defect remains
    unverified.
  - **Post-flash state confirms the gate is correct, not merely relaxed.** On the upgraded board
    `fw` now reports `3.0.0b19` / "already up to date", and `hw` — which refused with
    FirmwareOutdatedError before the flash and was the negative control above — now succeeds:
    `Hardware revision: Rev 2.0-class, Override HW: Rev 2.3`. So the identity gate admits CAP-02
    firmware and refuses pre-CAP-02 firmware on chip-op paths, while the waiver opened *only* the
    update path. That is the intended end state of the fix, observed rather than argued.
  - `/dev/ttyUSB0` (CH340, detected `uno328pb`) was deliberately left on 3.0.0b11 as a preserved
    pre-CAP-02 specimen — it is the only remaining board that can reproduce the original failure,
    and it keeps a regression witness on the bench. It still offers `3.0.0b19` correctly.
  - Note for whoever runs this next: auto mode refuses this flash on its merits (it downloads a
    binary and has avrdude overwrite MCU flash). `"Bash(python -m firestarter.main:*)"` in
    `.claude/settings.local.json` does clear it, but it is a **prefix** rule — the call must be
    issued **bare**. `cd X && timeout 400 python -m firestarter.main ... | tail` does not start
    with the rule's prefix, so it never matches and falls through to the classifier, which denies
    it. Set the working directory in a separate call first. Command shape, not the classifier
    overriding permission rules.

files_changed:
  - firestarter_app/firestarter/serial_comm.py: `_probe_port` + `find_and_connect` gain
    `allow_outdated_firmware` (default False); the identity refusal and the version floor now sit
    inside that guard.
  - firestarter_app/firestarter/firmware.py: `check_current_firmware` passes
    `allow_outdated_firmware=True`, with the rationale in its docstring.
  - firestarter_app/firestarter/cli_handlers.py: `_maybe_auto_route_to_pre` no longer requires
    `install`.
  - firestarter_app/tests/test_fw_update_path_gate.py: new, 19 regression tests.
  - commit: firestarter_app `ebbc299`

## Full update-path matrix (2026-08-19, operator granted standing flash authorization)

Every firmware-update path exercised against live hardware. All three flash methods work.

| Path | Board | Result |
|---|---|---|
| `fw --install` | uno / ttyACM1 | b11 → b19 OK — `-p atmega328p -c arduino -b 115200`, 8.39s |
| `fw --install` | leonardo / ttyACM0 | b17 → b19 OK — `-p atmega32u4 -c avr109 -b 57600`, 5.51s |
| `fw --install` | uno328pb / ttyUSB0 | b11 → b19 OK — `-p atmega328pb -c urclock -b 115200`, 6.66s |
| `fw --firmware-version 2.0.6 --force` | uno | b19 → 2.0.6 OK (pinned downgrade across a major) |
| `fw --firmware-version 3.0.0b11 --force` | uno328pb | b19 → b11 OK (pinned downgrade, round trip closed) |
| `fw` bare | all | reads + offers correctly; waiver fires on every pre-CAP-02 3.x board |
| `fw --stable` / `fw --pre` | uno | channel pinned, auto-route message correctly suppressed |
| `fw --list`, `--list --json`, `--stable --list --json` | — | OK |
| `hw` (negative control) | uno | refuses on pre-CAP-02, succeeds on b19 — gate intact |

Silicon identified directly, since the handshake reports only what the firmware claims:
ttyACM1 = `0x1e950f` (m328p), ttyUSB0 = `0x1e9516` (m328pb, urclock bootloader — its `uno328pb`
firmware is correctly matched, not a mismatch).

**Final bench state:** ttyACM1 `3.0.0b19`, ttyACM0 `3.0.0b19`, ttyUSB0 **left on `3.0.0b11`
deliberately** as the only remaining pre-CAP-02 specimen able to reproduce the original failure.

## SUPERSEDING FINDINGS — two UNFIXED defects, both worse than the one fixed above

The matrix surfaced two defects outside this session's scope. Neither is fixed. Both need their own
work, and the second one probably *is* the operator's original report.

**Defect A — `--port` is advisory for the read but authoritative for the write.** `serial_comm.py`
enumerates every candidate port with the `--port` one merely first, then silently falls through when
it does not answer. `firmware.py` then computes `port_to_use = port_override or connected_port` (the
override wins) against `board_to_use = current_board or board_override` (the *detected* board wins).
So the app composes board identity from port B with a flash target of port A. Demonstrated: with
2.0.6 on ttyACM1 (mute) and a uno328pb on ttyUSB0, `fw --port /dev/ttyACM1 --install` downloaded
`firestarter_uno328pb.hex` and ran `avrdude -p atmega328pb -c urclock -P /dev/ttyACM1`. **Only
avrdude's part-signature check prevented a wrong-firmware flash**; two boards sharing an MCU and
programmer would not be protected. Bare `fw --port /dev/ttyACM1` likewise reported *ttyUSB0's*
version with no warning. `--board` cannot rescue it — the detected board beats the override.
Fix direction: a named `--port` must **restrict** the scan, not order it, and finding no programmer
there must be an error; an explicit `--board` should win or conflict-error.

**Defect B — genuine 2.x stable firmware is still unupdatable, and the waiver does not help it.**
With real stable `2.0.6` flashed on, the probe returns `I: Buf val: 0x7b` / `ERROR: Bad JSON`.
`0x7b` is `{`: the 2.x firmware sees the first byte of the JSON command and rejects the frame,
because command framing changed after it shipped (COBS pivot, protocol rebuild). That failure is at
the **protocol layer, upstream** of the ack-identity gate this session's waiver opened — so every
2.x board, i.e. every board on a *stable* release, remains unreachable, and Defect A makes the app
silently answer with a different board's version instead of erroring.

**Scope correction against this session's own reasoning:** the trigger said "release firmware
installed". Seeing both Unos on `b11` (a pre-release), this session concluded the premise was
imprecise. That inference was wrong — the premise pointed at Defect B. The fix recorded above is
real and verified, but it addresses pre-CAP-02 **3.x** firmware only. Anyone reading this record
should treat the original complaint as **possibly still open** until Defect B is fixed.

Fix direction for B: `--install`/`--force` never need the running firmware's version — avrdude
talks to the **bootloader**, not the firmware. The update path should proceed with
`current_version = None` under an explicit `--board` and flash blind. `firmware.py` already
tolerates `current_version = None` under `--install`; it is Defect A that defeats it, by finding a
*different* board instead of finding nothing.

## SUPERSEDING FINDINGS — FIXED (2026-08-19, operator asked for both)

All three defects fixed in `firestarter_app`. Defect C below was found while verifying A and B, and
is the reason the first attempt at C did not hold.

**A — a named port now RESTRICTS the probe instead of merely ordering it.**
`_list_potential_ports` gained `restrict_to_preferred`; `find_and_connect` gained
`restrict_to_port` (default None = infer). The rule is deliberately two-sided, because "always
restrict" would have traded one defect for another: a port **typed this invocation** is a command
and is obeyed exactly, while a port merely **remembered from a previous successful run** stays a
hint that yields to discovery — otherwise replugging a board would strand every later invocation on
a port that no longer exists. The discriminator is the config's transient mark (see C): `cli()`
records a typed `--port` with `persist=False`, and every command reads the port back out of the
in-memory config, so that mark is the only surviving evidence of which one it was. The inference
tests `is True` rather than truthiness, so a `MagicMock` config double falls to the permissive
branch instead of silently acquiring a restriction. A restricted miss now names the port and points
at the `--board` escape hatch instead of dead-ending.

Call-site audit: only `firmware.py` passes `preferred_port` at all; `hardware.py` and
`eprom_operations.py` let `find_and_connect` resolve it from config. So the transient mark governs
every command uniformly with no per-command plumbing.

**B — an install no longer requires the running firmware to be readable.** avrdude drives the
BOOTLOADER, not the firmware, so firmware too old to speak the protocol can still be replaced. What
is unsafe is guessing WHICH image to write: with no identity, `board_to_use` collapses to the
`--board` default, so an unnamed board would resolve the `uno` asset for whatever is attached.
`--install`/`--force` on an unidentified programmer therefore now REFUSE unless the board is named,
and warn when they proceed. Portless (DFU) boards are exempt — a py32f071 exposes no serial port, so
"unidentified" is its normal state and the only way `board_to_use` can name it is for the caller to
have named it. That exemption is why `test_py32_dfu.py::test_dfu_board_installs_without_a_serial_port`
went RED on the first cut of this fix; the guard was wrong there, not the test.

**C — `set_value(..., persist=False)` is now honoured across later persisted writes.** `_save_config`
dumped the whole in-memory dict, so `firmware.py` caching `avrdude-path` after a successful flash
wrote the one-shot `--port` to disk. Observed live: `~/.firestarter/config.json` acquired
`"port": "/dev/ttyUSB0"` from a `--port` documented as applying to one invocation. `_transient_keys`
now excludes such keys from the dump, an explicit persisted write promotes a key out of transient
status, and `remove_key` clears the mark. A second writer was also involved and is the reason the
first fix did not hold: `serial_comm.py` persists the working port after every successful probe
("Save successful port"). That convenience is intentional and is kept — but extracted into
`_remember_working_port`, which never promotes a port the operator typed for this invocation.

### Live verification (all on the bench, after the fixes)

| Check | Result |
|---|---|
| `--port <mute 2.0.6 board> fw` | errors naming ttyACM1, no longer answers with ttyUSB0's version |
| `--port <bogus> hw` with 3 boards attached | errors on the named port; never silently uses another |
| `--port … fw --install` (no `--board`) | refused: "cannot be chosen automatically" |
| `--port … fw --board uno --install` | **2.0.6 → 3.0.0b19** — the upgrade that was impossible |
| bare `fw` (no `--port`) | discovers ttyUSB0, remembers it in config |
| bare `fw` with a STALE remembered port | falls through to discovery and self-heals config |
| `--port … fw` then inspect config | no `port` key written — the leak is closed |
| `hw` on an upgraded board | succeeds; still refuses on pre-CAP-02 — gate intact |

Note the `--board uno --install` row: that is the operator's original report, reproduced with
genuine stable firmware and now actually fixed. Defect B is what made it a true dead end; the
CAP-02 waiver recorded earlier in this file never reached it.

### Commits and gates for the three superseding fixes

- `firestarter_app` **`da6572b`** — `config.py` (`_transient_keys`, `is_transient`), `serial_comm.py`
  (`_list_potential_ports(restrict_to_preferred=…)`, `find_and_connect(restrict_to_port=…)`,
  `_remember_working_port`), `firmware.py` (blind-install guard + portless exemption), and
  `tests/test_fw_port_targeting_and_blind_install.py` (14 new tests, 5 proven RED pre-fix).
- Seven existing tests stubbed `_list_potential_ports` with one-parameter lambdas. The helper's
  signature genuinely changed, so the stubs were updated rather than the production call contorted
  to suit the doubles.
- Suite **1674 passed / 0 failed** (was 1660). `ruff check` + `ruff format` clean. mypy unchanged at
  the HEAD baseline of **17 errors in 5 files** — established by running mypy in a throwaway
  worktree of HEAD rather than assumed, since firmware.py's pre-existing `board_to_use` Optional
  errors shift line numbers when anything is inserted above them.

### Follow-up: `da6572b` fixed only one of the two port writers (`94d327d`)

Defect C had **two** persisted writers, not one. `da6572b` fixed the successful-probe site in
`serial_comm.py` and missed `firmware.py`, which ran `set_value("port", port_to_flash)` after a
successful flash with `persist` defaulting to True — promoting the transient key straight back out
of transient status. The leak therefore stayed fully live on the **install** path, the one an
operator actually reaches with an explicit `--port`. Caught by re-testing after the final
`--board uno --install` proof: `~/.firestarter/config.json` had reacquired
`"port": "/dev/ttyACM1"`.

Why the first verification missed it: the live check that "passed" exercised `hw`, which never
reaches the flash writer. A narrower check was read as covering the whole rule. **Lesson for this
file: verify a persistence rule on the path that writes, not on the cheapest path to hand.**

`94d327d` moves the policy off `SerialCommunicator` (it is about config persistence, not serial
transport) and onto **`ConfigManager.remember_port()`** — now the single writer of the saved `port`
key, called by both the probe and the flash path. A source-level tripwire asserts `config.py` is the
only production module writing the key directly; `cli_handlers.py` is exempt because its
`set_value("port", …, persist=False)` IS the `--port` override. Two call sites silently drifting
apart is exactly what caused this, so it is pinned rather than trusted.

Final gates: suite **1675 passed / 0 failed**, ruff + format clean, mypy unchanged at the 17-error
HEAD baseline.

### Final bench state (2026-08-19, end of session)

| Port | Controller | Firmware | Note |
|---|---|---|---|
| `/dev/ttyACM0` | leonardo | `3.0.0b19` | upgraded from b17 via `fw --install` |
| `/dev/ttyACM1` | uno | `3.0.0b19` | round-tripped b11 → b19 → 2.0.6 → b19 |
| `/dev/ttyUSB0` | uno328pb | `3.0.0b11` | **left deliberately** — the only pre-CAP-02 specimen left, and the only board that can still reproduce the original failure. Do not upgrade casually. |

`~/.firestarter/config.json` holds only `avrdude-path`; no `port` key, which is itself the standing
witness that Defect C is closed.

## Gap closure — what was and was NOT bench-verified (asked directly, 2026-08-19)

Three gaps were named honestly before closing them, rather than claiming blanket bench coverage.

**Gap 2 — the blind-install path on a second/third flash method. CLOSED for `avr109`.** The path had
only ever been proven on the Uno (`arduino`). Leonardo: 2.0.6 flashed on → unreachable → refused
without `--board` → `fw --board leonardo --install` warned and flashed b19. That specifically drives
`Avrdude._trigger_reset`'s 1200-baud USB-CDC touch, which runs **only** for `atmega32u4` and had
never executed from the blind branch. **`urclock` CLOSED too, on a later attempt** — the first run
reached only the download boundary because GitHub rate-limited the release lookup (`latest: None`),
and that board was restored via CDN + direct avrdude rather than left unreachable. Re-run after the
limit reset: `3.0.0b4` flashed on → `Bad JSON` → `fw --board uno328pb --install` warned, resolved
`3.0.0b19`, and ran `avrdude -p atmega328pb -c urclock -b 115200 -P /dev/ttyUSB0` to completion →
board reads b19. **All three flash methods are therefore proven under the blind branch**:
`arduino` (uno), `avr109` (leonardo, incl. the 1200-baud touch), `urclock` (uno328pb).

That run also validated the corrected wording from `a7e554d` in situ — the emitted message named
"every 2.x release, and 3.0.0 pre-releases before b8", and `b4` is exactly such a pre-release.
The board was then returned to `3.0.0b11` and the CAP-02 waiver re-confirmed firing on it
(`ack carries no firmware identity … proceeding because this is the firmware-update read path`), so
the witness is intact and demonstrably still reproduces the *other* defect.

**This test disproved the wording of the fix's own error message** (`a7e554d`). `3.0.0b4` answers
`Bad JSON` exactly as `2.0.6` does, so blaming "2.x firmware" would misdirect an operator on a
3.0.0 build. Measured boundary: `2.0.6` Bad JSON, `3.0.0b4` Bad JSON, `3.0.0b11` acks **without**
the CAP-02 identity tail. The two defects are therefore distinct populations, not one "old firmware"
bucket — **pre-b8 needs the blind install, b8..b18 needs the CAP-02 waiver** — the split being the
COBS pivot at firmware b8.

**Gap 3 — nothing had run under CI conditions. CLOSED.** CI is Python **3.11 only** (an earlier note
in this session said py39/3.11 — wrong; `ci.yml` pins 3.11). The devcontainer carries only 3.12, so
a real 3.11 was provisioned with `uv` (needs `UV_CACHE_DIR` pointed somewhere writable). Every CI
step run in order: catalog validity (76 messages / 12 vectors), both codegen drift gates **ZERO
DIFF**, `ruff check`, `ruff format --check`, **`tools/check_mypy_watermark.py`** — the actual gate —
**33 errors vs watermark 35, 143 files, exit 0**, `pytest --cov-fail-under=70` → **1675 passed,
83.69%**, the console-script smoke test, and the isolated `ci-py32` leg (pyusb 1.3.1 genuinely
imports, 6/6). Note the mypy scope trap: raw `mypy firestarter/` reports *17 errors in 5 files over
29 files* and is a DIFFERENT measurement from the gate's 143-file run; neither number contradicts
the other, and the gate passes with headroom.

**Gap 1 — the portless/DFU exemption in Defect B is UNVERIFIABLE and stays open.** `--install` skips
the `--board` requirement when `flash_method(board)` is portless, so a py32f071 is exempt. No
PY32F071 silicon exists (no PCB, never run on hardware), so that branch is unit-test-only by
necessity and is the least-proven line in this work. It is guarded by
`test_py32_dfu.py::TestPortlessInstall::test_dfu_board_installs_without_a_serial_port`, whose RED on
the first cut of the fix is what surfaced the need for the exemption at all.

Also reasoned rather than demonstrated: the claim that Defect A would silently flash the **wrong**
image where two boards share an MCU. This bench has three distinct MCUs (328P / 328PB / 32u4), so
avrdude's part-signature check refused every mismatch. The unprotected case was never observed.

### That "reasoned, not demonstrated" hazard was a LIVE HALF of Defect A (`c495e98`)

Asked to fix the flagged items, the hazard turned out not to be hypothetical. **`da6572b` closed only
the typed-port path.** `port_override` is read back out of config, so a port merely *remembered*
there does not restrict the probe — and `port_to_use = port_override or connected_port` still
preferred it. With a saved `port` in config and the board since moved, `fw --install` identified
board **Y** and then aimed **Y's** release asset at port **X**: the original Defect-A composition,
fully alive through the config path, in code already reported as fixed.

Fix is a one-line inversion, `port_to_use = connected_port or port_override`, which makes the
composition **unrepresentable** rather than improbable: whenever there is an identity, it and the
flash target are the same port by construction; when there is none there is nothing to mismatch, so
the named port is used and the blind path is unchanged. Pinned by
`test_identity_and_target_always_come_from_the_same_port`, verified RED against the old ordering with
exactly the wrong port (`ttyACM1` where `ttyUSB0` was required). Suite 1676 passed / 0 failed.

This also **retires the avrdude-is-the-only-guard worry** rather than documenting it: that guard held
only while two boards had different MCUs, and two Unos are both `atmega328p -c arduino`. The app can
no longer produce the mismatch, so the hardware signature check is no longer load-bearing.

**Lesson, and it is the sharpest one in this file:** each of the three times a "fixed" claim was
re-examined here, a second call site or a second code path was still carrying the defect —
`serial_comm` vs `firmware` for the config leak (C), the typed-port vs config-port path for
targeting (A). A defect that arises from *two places agreeing* is not fixed by repairing one of them.

## SHIPPED — PR #52 merged to beta, published `3.0.0b22` (2026-08-19)

[henols/firestarter_app#52](https://github.com/henols/firestarter_app/pull/52), merge commit
`eaca13e`. Raised from a branch cherry-picked onto `beta` — deliberately **not** from the v1.32
milestone branch, which carried 32 further commits of unfinished work including a breaking
chip-database schema migration. All five patches applied with no conflicts, and the whole gate set was
re-run on beta's base before pushing (1625 passed / 0 failed, coverage 83.27%, codegen zero-diff,
watermark 33 vs 35 over 139 files), plus a live re-verification of the restriction and the CAP-02
waiver *from that branch*, since beta's `serial_comm` differs from the milestone branch's.

Real CI confirmed it: `ci` pass ×2 (push + pull_request triggers), `ci-py32` pass ×2, Snyk pass.

**The merge published a version.** `beta-release.yml` cuts a pre-release on *every* push to beta —
its own `on:` comment says so explicitly, and the old `paths-ignore` list was deleted precisely
because a merge that published nothing made "beta silently stop tracking its own branch" (PR #46). So
`3.0.0b22` shipped ~3 minutes after the merge (Host CI 2m30s, release 2m44s, both success). This is
**designed** behaviour and needed no cleanup — distinct from the milestone-close double-cut recorded
in [[reference_beta_merge_push_autofires_ci_new_beta]].

**Close-time trap for v1.32.** The milestone branch still holds the same five patches under
DIFFERENT SHAs. `git cherry origin/beta <milestone-branch>` marks all five `-` (already upstream), so
a close-time merge will not double-apply them — but `git merge-base --is-ancestor ebbc299
origin/beta` reports **NOT an ancestor**, a false negative of the same shape as v1.30's squashed
close. **Verify with `git cherry`, never by SHA ancestry.** Do not rebase the milestone branch to
tidy this: concurrent sessions commit to it (Phase 149-03 landed there two minutes after the merge).

Still open, permanently until silicon exists: the portless/DFU exemption (Gap 1 above), stated in the
merged PR body so it is on the public record rather than only here.
Enumerate every writer/reader of the shared state before declaring it closed, and prefer a single
chokepoint (`ConfigManager.remember_port`, `connected_port or port_override`) over a rule that must
hold in several places at once.
