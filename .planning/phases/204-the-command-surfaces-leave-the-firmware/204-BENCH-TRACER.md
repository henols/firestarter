# Phase 204 Plan 01 — Bench Tracer Record

**Date:** 2026-09-22
**Task:** 204-01 Task 3 — flash the tracer firmware and watch a real published host be refused

## D-07 label substitution — stated explicitly

Neither side of this bench run carries a `3.1.0` version string, because REL-01's version bump is
Phase 207's, not this plan's. The labels below are documentation, not mechanism — nothing in
`verify` or `blank` gates on a version string; the refusal is `MSG_ERR_UNKNOWN_CMD` either way.

- **"Tracer firmware" / "post-204 firmware"** means the `firestarter_fw` working tree at commit
  `268d844b5c664e472527158d00a9bd342a39b0dc` (`feat(204-01): retire ordinal 6 (CMD_VERIFY) from the
  firmware`), built locally and flashed to the bench board. `include/version.h` still reads
  `3.0.0b33` — the ordinal-6 sweep does not touch it, and REL-01's bump is Phase 207's.
- **"Post-204 host"** means the `firestarter_app` working tree at commit
  `f6d37240ee99573d262cf6e03ec497f526b6adca` (`feat(204-01): retire ordinal 6 (COMMAND_VERIFY) from
  the host`), installed editable into `/workspaces/firestarter_app/.venv311`.
- **"Pre-3.1.0 host" / "old host"** means the published PyPI package `firestarter` at pinned version
  `3.0.0b49`, installed into a throwaway venv at `$HOME/.local/share/gsd-204-oldhost-venv`, approved
  at the Task 2b package-legitimacy checkpoint (human response: "approved", 2026-09-22).
- The meta repository's gitlink advance for this commit pair is `5e675d35eaefb149d6075da31094c9e4cc56f650`.

## Rig identity (re-derived this session, per D-10)

- Exactly one USB device enumerated with vendor:product `2341:8036` (Arduino Leonardo), at sysfs
  path `/sys/bus/usb/devices/3-3.1.2.2/`.
- `/dev/ttyACM0` exists and is the node used for every command below.
- No ambiguity: this is the only serial device on the bus this session, confirmed by a fresh
  `/sys/bus/usb/devices/*/idVendor` + `idProduct` sweep immediately before flashing, not assumed from
  a prior session's port number.

## Environment note — runtime reset since Task 1/2

Between the Task 2b checkpoint and this task, the devcontainer's `$HOME/.local/share` tree (an
ephemeral path, unlike the `/workspaces` bind mount) was empty on resume: the durable Python 3.11.16
install and the `.venv311` interpreter Task 1 built were both gone, though `/workspaces` and all git
history were intact. This is consistent with the prior interruption's account of an infrastructure
failure between agent runs. Rebuilt before this task's bench work, identically to Task 1's recipe
(`uv python install 3.11`; `uv venv --python 3.11 /workspaces/firestarter_app/.venv311`; `uv pip
install --python .venv311/bin/python -e '/workspaces/firestarter_app[test]'`), and re-verified against
Task 1's own acceptance command before proceeding — interpreter resolves to
`/home/vscode/.local/share/uv/python/cpython-3.11.16-linux-x86_64-gnu`, editable install resolves
under `/workspaces/firestarter_app/`. No source file and no commit from Task 1 or Task 2 was affected;
`.venv311` is self-ignoring and was never a committed artifact.

## (b) Flash — the A5 probe

Command, run from `firestarter_fw` at commit `268d844`:

```
pio run -e leonardo -t upload
```

Exit code: **0**. Relevant output:

```
bootloader-guard: leonardo 24082/28672 B (84.0% of the safe ceiling, 4590 B margin, 4096 B bootloader reserved)
RAM:   [=======   ]  71.8% (used 1839 bytes from 2560 bytes)
Flash: [=======   ]  73.5% (used 24082 bytes from 32768 bytes)
Auto-detected: /dev/ttyACM0
Forcing reset using 1200bps open/close on port /dev/ttyACM0
...
avrdude: writing flash (24082 bytes):
Writing | ################################################## | 100% 1.89s
avrdude: 24082 bytes of flash written
avrdude: verifying flash memory against .pio/build/leonardo/firestarter_leonardo.hex:
avrdude: reading on-chip flash data:
Reading | ################################################## | 100% 0.22s
avrdude: verifying ...
avrdude: 24082 bytes of flash verified
avrdude done.  Thank you.
========================= [SUCCESS] Took 7.00 seconds =========================
```

No upload port was passed — PlatformIO auto-detected the bootloader re-enumeration itself, as the
plan specifies. **This is the first `pio run -t upload` ever attempted from this devcontainer, and it
succeeded on the first try.** Every REL-02 and REL-03 leg in the phase depended on this being true.

## (c) Baseline read — post-204 host

```
/workspaces/firestarter_app/.venv311/bin/firestarter read -f W27C512 tracer-pre.bin
```

`-f`/`--force` was required: the rig's VPP monitor does not route to the socket and its reading is a
known-noisy proxy (fluctuated 4.9V too low on the first attempt, 13.0V too high on later attempts,
across the same session with no operator intervention), which without `-f` aborts the read at the
chip-ID check before any array data is transferred. Forcing past it is safe for a plain read: chip-ID
sensing is the only VPP-dependent step in the read path, and it does not gate the actual array-content
transfer.

- Exit: 0
- **`tracer-pre.bin`: 65536 bytes**
- **SHA-256: `a094e902a30b4fa3369ee493338351e11a8b6667f7539460b63f78dce896ae43`**
- Content confirmed non-blank (not all `0xFF`); first bytes `18 18 1a 18 1c 18 1e 18 ...`

## (d) Pre-3.1.0 host provisioned

```
uv venv --python 3.11 "$HOME/.local/share/gsd-204-oldhost-venv"
uv pip install --python "$HOME/.local/share/gsd-204-oldhost-venv/bin/python" 'firestarter==3.0.0b49'
```

Verified before trusting it to play the role:

```
pre-3.1.0 host 3.0.0b49 at /home/vscode/.local/share/gsd-204-oldhost-venv/lib/python3.11/site-packages/firestarter
```

`eprom_operations.py` in the installed wheel still composes both `COMMAND_VERIFY` and
`COMMAND_BLANK_CHECK` — confirmed present in source before the legs below were run, so the legs are
meaningful rather than vacuous. Installed nowhere but this throwaway venv — never into `.venv311`,
never into the project environment.

## (e) Shared config protected

`~/.firestarter/` did not exist before this task started. The post-204 host's own baseline read at
step (c) created `~/.firestarter/config.json` (`{"port": "/dev/ttyACM0"}`). That file was moved aside
to a scratch location before the two old-host legs below, restored immediately afterward (overwriting
whatever the old host itself wrote there), and the whole `~/.firestarter/` directory was deleted at
the end of this task — see "Final state" below.

## (f) Negative control — old host, retired ordinal 6

```
"$HOME/.local/share/gsd-204-oldhost-venv/bin/firestarter" verify -f W27C512 tracer-pre.bin
```

- **Exit code: 1**
- **Duration: 3.55 s**
- Transcript:

```
Connecting...Connecting... OK
Verifying tracer-pre.bin against W27C512
ERROR: Unknown command: 6
Programmer error during VERIFY: Programmer error during init: Unknown command: 6
Verify for W27C512 failed.
```

Refused promptly (3.55 s, well inside the bounding timeout), not after a stall — matches the traced
refusal path (`204-RESEARCH.md` § "The Refusal Path, Traced End To End"): `is_memory_cmd(6)` is now
false, `configure_memory` never runs, the dispatch `default:` arm emits `MSG_ERR_UNKNOWN_CMD` naming
ordinal 6, and the old host's own exception handling turns that into a coded, non-hanging failure.

## (g) Positive control — old host, still-live ordinal 4

```
"$HOME/.local/share/gsd-204-oldhost-venv/bin/firestarter" blank -f W27C512
```

- **Exit code: 1** (the CLI's own convention for a "not blank" verdict — not a refusal)
- **Duration: 3.8 s**
- Transcript:

```
Connecting...Connecting... OK
Blank checking EPROM W27C512
WARN: VPP is high: 13.0V > 12.0V
Programmer warning: VPP is high: 13.0V > 12.0V
ERROR: Not blank, at 0x000000, v: 0x18
Programmer error during BLANK_CHECK: Not blank, at 0x000000, v: 0x18
```

No "Unknown command" line anywhere in this transcript. The firmware served the request end to end —
`configure_memory` ran, `configure_eprom` reported the first non-blank byte — because ordinal 4 has
not been retired yet (that is plan 03's work). This is the control that rules out "the old host fails
against this firmware for some unrelated reason": the same host, the same firmware, the same session,
one ordinal refused and the adjacent one served.

## (h) Read-back equivalence

`~/.firestarter/` restored to its step-(c) state, then:

```
/workspaces/firestarter_app/.venv311/bin/firestarter read -f W27C512 tracer-post.bin
```

- **`tracer-post.bin`: 65536 bytes**
- **SHA-256: `a094e902a30b4fa3369ee493338351e11a8b6667f7539460b63f78dce896ae43`** — identical to
  `tracer-pre.bin`
- `cmp tracer-pre.bin tracer-post.bin` exits 0: **byte-identical over all 65536 bytes**

Neither the refused `verify` nor the served `blank` wrote or erased anything on the part. This is
observed on silicon, not argued from where the refusal fired, per D-09.

## Final state

`~/.firestarter/` was deleted after step (h) — it did not exist before this task and does not exist
after it:

```
$ ls -la ~/.firestarter
ls: cannot access '/home/vscode/.firestarter': No such file or directory
```

## Coverage gap — stated, not hidden

**Both bench legs in this task ran on a Leonardo only.** Its buffer is 1024 bytes, not the Uno's 512,
and progress emission during read is Leonardo-only in this firmware. This proves nothing about the
Uno-class / 512-byte-buffer path. No Uno-class board is attached to this devcontainer. If Uno-class
coverage of FWCMD-06 is wanted, it needs a separate board and a separate leg.

## Summary of what this task proves

1. `pio run -e leonardo -t upload` reaches the attached board from this devcontainer — the phase's
   single largest unproven assumption at plan-authoring time, now observed rather than assumed.
2. A real published host (`3.0.0b49`) that still composes the retired ordinal is explicitly refused
   by name (`Unknown command: 6`), promptly, with no hang.
3. The same host, same session, same firmware, is still served on the ordinal not yet retired
   (`blank`, ordinal 4) — ruling out "fails for an unrelated reason."
4. The refused command left the part byte-identical across a whole-device read taken before and after
   — the failure mode a blank-check ordinal retiring badly would produce did not occur.
