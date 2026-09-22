# Phase 204 Plan 05 — Four-Role Bench Matrix

**Date:** 2026-09-22
**Plan:** 204-05 — the full four-role skew matrix, both retired ordinals (6 and 4), both skew
directions, on real hardware.

This record supersedes nothing in `204-BENCH-TRACER.md` (plan 01's single-ordinal tracer with ordinal
4 as a live control) — it repeats that recipe with both ordinals retired and produces the full D-07
role table, three whole-device digests, and two refusal transcripts this plan's `must_haves` require.

## Open question carried, not resolved (WINDOWS.md entry 3)

**The seated part's identity is NOT independently confirmed.** Every `read` in this matrix — this
plan's and plan 01's before it — reports `Chip ID 0x1818 does not match expected ID 0xda08` (the
database's `chip_id_value` for `W27C512,W27E512`). The array's first bytes are
`18 18 1a 18 1c 18 1e 18 ...`, and the reported "chip ID" is exactly those first two bytes — consistent
with a read that landed on ordinary array data rather than a true ID-mode sense (ID sensing needs A9
held high via VPP, and this rig's VPP monitor is on record as not routing to the socket). That is
inference, not a measured cause, and it is **not re-investigated or forced past in this plan** per the
orchestrator's explicit instruction — it needs the operator, who physically placed the part.

This binds the record as follows:
- The task 1 precondition's "W27C512 carrying non-blank content is seated" is treated as verified on
  the *non-blank content* half only. The *W27C512* half is UNCONFIRMED.
- Every substantive claim in this matrix — refused vs. served on each ordinal, in each skew direction,
  and byte-identity of the part across the whole matrix — is chip-identity-**independent** by
  construction: every leg addresses the same physical part in the same socket, whatever species of chip
  it actually is.
- The part is referred to throughout as "the seated part (identity unconfirmed — WINDOWS.md entry 3)",
  never asserted as a confirmed W27C512.

## D-07 label substitution — stated explicitly

Neither side of this bench run carries a `3.1.0b1` version string, because REL-01's version bump is
Phase 207's, not this plan's. **Nothing in the refused commands (`verify`, `blank`) gates on a version
string** — the refusal mechanism is purely ordinal-based (`is_memory_cmd()` on the firmware side, the
dispatch `default:` arm emitting `MSG_ERR_UNKNOWN_CMD`). The labels below are documentation of which
artifact played which role, not a claim about what either artifact's own version string says.

**The host cannot read back which firmware is on the board.** Its port probe truncates the prerelease
suffix, so `b33`, `b34`, and any post-204 build are indistinguishable to it at runtime. The commit shas
recorded in the role table below — not anything the host reports — are the only record of which
artifact played which role in this matrix.

- **"Pre-204 firmware"** means the `firestarter_fw` repository at commit
  `e5842d8ceacac45e8640cd274947e7ee6c88fb58` (`test(201-05): source-contract gate over all nine
  blank-check reference sites`) — the last commit before ANY ordinal was retired in this phase, and the
  parent of wave 1's `268d844`. Built from a **detached worktree** at
  `/home/vscode/.local/share/gsd204-fw-pre204-worktree`, never a downloaded release asset.
  `include/version.h` at this commit reads `3.0.0b33`.
- **"Post-204 firmware"** means the `firestarter_fw` working tree HEAD at the time this plan ran,
  `24e3fdf9bc78446761244ae08dc42225881dde31` (`docs(204-04): repair five citations the ordinal-4/6
  sweep staled`) — both ordinal 6 (plan 01) and ordinal 4 (plan 03) retired.
- **"Post-204 host"** means the `firestarter_app` working tree HEAD,
  `2a17fd7bd650274361e5730bd9e2eebb753ef069`, installed editable into
  `/workspaces/firestarter_app/.venv311`.
- **"Published host" / "old host" / "pre-3.1.0 host"** means the published PyPI package `firestarter`
  at pinned version `3.0.0b49`, installed into the throwaway venv
  `$HOME/.local/share/gsd-204-oldhost-venv` (provisioned by plan 01, re-verified present and functional
  at the start of this plan).
- **Not a role, but a probe cited for comparison:** the tracer firmware plan 01 flashed,
  `firestarter_fw` commit `268d844b5c664e472527158d00a9bd342a39b0dc` (ordinal 6 retired only, ordinal 4
  still live) — this plan's post-204 firmware supersedes it.

## Role table

| Role | Artifact | Commit sha / pinned version | Installed at |
|---|---|---|---|
| Pre-204 firmware | `firestarter_fw` detached worktree | `e5842d8ceacac45e8640cd274947e7ee6c88fb58` | `/home/vscode/.local/share/gsd204-fw-pre204-worktree`, flashed to board |
| Post-204 firmware | `firestarter_fw` working tree HEAD | `24e3fdf9bc78446761244ae08dc42225881dde31` | `/workspaces/firestarter_fw`, flashed to board |
| Post-204 host | `firestarter_app` working tree HEAD, editable install | `2a17fd7bd650274361e5730bd9e2eebb753ef069` | `/workspaces/firestarter_app/.venv311` |
| Published host | PyPI `firestarter` pinned version | `3.0.0b49` | `$HOME/.local/share/gsd-204-oldhost-venv` |
| (probe, not a role) Tracer firmware (plan 01) | `firestarter_fw` | `268d844b5c664e472527158d00a9bd342a39b0dc` | superseded by post-204 firmware in this plan |

## Rig identity (re-derived this session, per D-10)

- Exactly one USB device enumerated with vendor:product `2341:8036` (Arduino Leonardo), at sysfs path
  `/sys/bus/usb/devices/3-3.1.2.2/`.
- `/dev/ttyACM0` exists and is the node used for every command below.
- Confirmed by a fresh sweep of `/sys/bus/usb/devices/*/idVendor` + `idProduct` at the start of this
  plan, not assumed from a prior session's port number.
- `firestarter_fw` has no `.gitmodules` — no nested submodules — so the detached worktree used below
  checks out completely; the worktrees-leave-submodules-empty hazard does not apply here.

## Task 1 — Build and flash the pre-204 firmware, and baseline the part

### (b) Build the pre-204 firmware from its own commit

```
$ cd /workspaces/firestarter_fw && git worktree add --detach \
    /home/vscode/.local/share/gsd204-fw-pre204-worktree e5842d8
Preparing worktree (detached HEAD e5842d8)
HEAD is now at e5842d8 test(201-05): source-contract gate over all nine blank-check reference sites
```

Worktree HEAD: `e5842d8ceacac45e8640cd274947e7ee6c88fb58`.

Build command and pre-sweep flash/RAM figures (Leonardo target, from the pre-204 worktree):

```
$ cd /home/vscode/.local/share/gsd204-fw-pre204-worktree && pio run -e leonardo
...
bootloader-guard: leonardo 24134/28672 B (84.2% of the safe ceiling, 4538 B margin, 4096 B bootloader reserved)
RAM:   [=======   ]  71.8% (used 1839 bytes from 2560 bytes)
Flash: [=======   ]  73.7% (used 24134 bytes from 32768 bytes)
========================= [SUCCESS] Took 3.04 seconds =========================
```

Pre-sweep figures for the other two AVR targets, same worktree (recorded here per task 1's action item,
consumed by task 2's per-target size table below):

```
$ pio run -e uno -e uno328pb
...
bootloader-guard: uno 21850/32256 B (67.7% of the safe ceiling, 10406 B margin, 512 B bootloader reserved)
RAM:   [=======   ]  68.3% (used 1398 bytes from 2048 bytes)
Flash: [=======   ]  66.7% (used 21850 bytes from 32768 bytes)
...
bootloader-guard: uno328pb 21894/32384 B (67.6% of the safe ceiling, 10490 B margin, 384 B bootloader reserved)
RAM:   [=======   ]  68.6% (used 1404 bytes from 2048 bytes)
Flash: [=======   ]  66.8% (used 21894 bytes from 32768 bytes)
========================= 2 succeeded in 00:00:02.380 =========================
```

### (c) Flash it

```
$ pio run -e leonardo -t upload
...
avrdude: writing flash (24134 bytes):
Writing | ################################################## | 100% 1.89s
avrdude: 24134 bytes of flash written
avrdude: verifying flash memory against .pio/build/leonardo/firestarter_leonardo.hex:
avrdude: 24134 bytes of flash verified
avrdude done.  Thank you.
========================= [SUCCESS] Took 5.99 seconds =========================
```

No upload port was passed — PlatformIO auto-detected the bootloader re-enumeration (the 1200-baud touch
reset), exactly as plan 01 observed and this plan's environment notes predicted.

### (d) Baseline the part

```
$ cd /workspaces/firestarter_app && .venv311/bin/firestarter read -f W27C512 \
    /home/vscode/.local/share/gsd204-scratch/pre.bin
Connecting...Connecting... OK
Reading EPROM W27C512, saving to /home/vscode/.local/share/gsd204-scratch/pre.bin
WARN: VPP is low: 4.9V < 12.0V
Programmer warning: VPP is low: 4.9V < 12.0V
WARN: Chip ID 0x1818 does not match expected ID 0xda08
Programmer warning: Chip ID 0x1818 does not match expected ID 0xda08
... [progress bar elided] ...
Read complete (7.40s). Data saved to /home/vscode/.local/share/gsd204-scratch/pre.bin
```

- Exit: 0
- **`pre.bin`: 65536 bytes**
- **SHA-256: `a094e902a30b4fa3369ee493338351e11a8b6667f7539460b63f78dce896ae43`**
- Non-erased bytes: 65408 of 65536 — confirmed non-blank.
- First bytes: `18 18 1a 18 1c 18 1e 18 10 18 12 18 14 18 16 18`.

This digest is **identical to plan 01's `tracer-pre.bin` digest**, and the chip-ID warning is
byte-identical too (`0x1818` vs expected `0xda08`) — consistent with the same physical part, still
seated, unmoved, since plan 01's session. The `-f`/`--force` flag was required for the same reason plan
01 recorded: the rig's VPP monitor does not route to the socket and its reading is a known-noisy proxy
that would otherwise abort the read at the chip-ID check before any array data transfers. Forcing past
it is safe for a plain read — chip-ID sensing is the only VPP-dependent step in the read path and does
not gate array-content transfer.

*(Task 1 complete. Task 2 — the new-host-against-old-firmware direction, then the firmware swap — and
task 3 — the published-host refusal legs — continue this record below in later commits.)*
