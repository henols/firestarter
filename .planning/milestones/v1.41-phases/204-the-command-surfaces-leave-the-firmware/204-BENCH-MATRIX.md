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

## Task 2 — The new-host-against-old-firmware direction, then swap the firmware

### (a) The new-host leg — criterion 4 and REL-02

Both commands were run with `-f`/`--force`, for the identical documented reason task 1's read needed
it: the rig's VPP monitor is a known-noisy proxy that does not route to the socket, and its false
low/high readings would otherwise abort the command before any chip-content exchange happens. Forcing
past the VPP precheck changes nothing about which ordinal is sent on the wire — it is a host-side
precondition gate, not a protocol substitution.

**`verify` against the pre-204-firmware-baselined image:**

```
$ cd /workspaces/firestarter_app && timeout 300 .venv311/bin/firestarter verify -f w27c512 \
    /home/vscode/.local/share/gsd204-scratch/pre.bin
Connecting...Connecting... OK
Verifying /home/vscode/.local/share/gsd204-scratch/pre.bin against W27C512
WARN: VPP is high: 13.1V > 12.0V
Programmer warning: VPP is high: 13.1V > 12.0V
... [progress bar elided] ...
match, 0 bad of 65536 compared of 65536 (0x000000-0x00FFFF)
Verify for W27C512 successful (7.40s).
```

- **Exit code: 0**
- **Duration: 11.00 s** (wall-clock around the subprocess; the command's own reported internal time is
  7.40s)
- **Match, 0 bad of 65536 compared of 65536.**
- No `-f`-less first attempt: an un-forced run (recorded, not silently discarded) hit the VPP precheck
  and exited 2 with `ERROR: VPP is high: 13.1V > 12.0V` before any chip content was exchanged — the
  same rig-noise VPP-sensing unreliability already on record project-wide, not a protocol event.

**`blank` against the same firmware:**

```
$ cd /workspaces/firestarter_app && timeout 300 .venv311/bin/firestarter blank -f w27c512
Connecting...Connecting... OK
Blank checking EPROM W27C512
WARN: VPP is high: 13.1V > 12.0V
Programmer warning: VPP is high: 13.1V > 12.0V
  2%|▏ | 0x0400/0x10000 bytes  Read stopped in flight at 0x000400 (abort predicate fired).
                                ERROR: Timeout
Programmer error during READ: Programmer error during read: Timeout
Mismatch 0x000000-0x0003FF (1024 bytes)
indeterminate, 1024 bad of 1024 compared of 65536 (0x000000-0x0003FF)
Blank check for W27C512 failed.
```

- **Exit code: 1** (the CLI's "not blank" convention, not a refusal)
- **Duration: 4.92 s** (reproduced on a second run: 4.85 s, byte-identical transcript)
- Reports the part as **not blank**, which is the correct verdict for a part carrying non-blank content.
- The "abort predicate fired" / "ERROR: Timeout" sequence is the **designed early-stop mechanism**
  documented in `firestarter_app/firestarter/eprom_operations.py` `_main_phase_read_data` (202-04 D-06):
  once a mismatch is found and `--full` was not requested, the host stops acking further chunks; the
  firmware's own 1-second `op_wait_for_ack` then times out, `command_done()` still runs to leave the
  port clean, and the host reports the mismatch it already found. This is NOT a protocol failure and is
  NOT an unknown-command condition — it is the intended fast-exit path for a non-blank part, confirmed
  by reading the source before treating the transcript as evidence.

**Assertion, explicit:** neither output contains an "unknown command" line.

```
$ grep -i "unknown command" task2-verify-f.out task2-blank.out; echo "exit: $?"
exit: 1
```

Both outcomes are the "correct" outcomes REL-02 requires — the post-204 host only ever sends the read
ordinal, old firmware serves it normally either way, and what would have falsified the claim (an
unknown-command line, a protocol failure, or a stall) did not occur. Per D-11, this leg proves an
ABSENCE, and its whole value is in having been run on real silicon rather than argued from code
structure.

### (b) Swap the firmware

```
$ cd /workspaces/firestarter_fw && git rev-parse HEAD
24e3fdf9bc78446761244ae08dc42225881dde31
$ timeout 60 pio run -e leonardo -t upload
...
avrdude: writing flash (23810 bytes):
avrdude: 23810 bytes of flash written
avrdude: verifying flash memory against .pio/build/leonardo/firestarter_leonardo.hex:
avrdude: 23810 bytes of flash verified
avrdude done.  Thank you.
========================= [SUCCESS] Took 5.97 seconds =========================
```

Post-204 firmware sha: `24e3fdf9bc78446761244ae08dc42225881dde31`. No chip removal — the Leonardo is
exempt from the chip-out-before-sideload rule, and the part stayed seated throughout.

### (c) Isolate the firmware swap from the refusal legs

```
$ cd /workspaces/firestarter_app && .venv311/bin/firestarter read -f W27C512 \
    /home/vscode/.local/share/gsd204-scratch/mid.bin
... [same VPP-low / chip-ID warnings as task 1's baseline read] ...
Read complete (7.40s). Data saved to /home/vscode/.local/share/gsd204-scratch/mid.bin
```

- **`mid.bin`: 65536 bytes**
- **SHA-256: `a094e902a30b4fa3369ee493338351e11a8b6667f7539460b63f78dce896ae43`** — identical to `pre.bin`
- `cmp pre.bin mid.bin` exits 0: **content survived the firmware swap, byte-for-byte over all 65536
  bytes.**

This isolates the firmware swap itself from the refusal legs task 3 runs next: whatever happens there,
this digest proves the flash operation alone changed nothing on the part.

### (d) Per-target flash and RAM figures — pre-sweep vs. post-sweep

Pre-sweep figures are from task 1's pre-204 worktree build (`e5842d8`). Post-sweep figures are a clean
rebuild of the post-204 working tree (`24e3fdf`) for all three AVR targets:

```
$ cd /workspaces/firestarter_fw && pio run -e uno -e uno328pb -e leonardo -t clean
$ pio run -e uno -e uno328pb -e leonardo
...
bootloader-guard: uno 21452/32256 B (66.5% of the safe ceiling, 10804 B margin, 512 B bootloader reserved)
RAM:   68.3% (used 1398 bytes from 2048 bytes)
Flash: 65.5% (used 21452 bytes from 32768 bytes)
...
bootloader-guard: uno328pb 21496/32384 B (66.4% of the safe ceiling, 10888 B margin, 384 B bootloader reserved)
RAM:   68.6% (used 1404 bytes from 2048 bytes)
Flash: 65.6% (used 21496 bytes from 32768 bytes)
...
bootloader-guard: leonardo 23810/28672 B (83.0% of the safe ceiling, 4862 B margin, 4096 B bootloader reserved)
RAM:   71.8% (used 1839 bytes from 2560 bytes)
Flash: 72.7% (used 23810 bytes from 32768 bytes)
```

| Target | Pre-sweep Flash | Pre-sweep RAM | Post-sweep Flash | Post-sweep RAM | Flash delta |
|---|---|---|---|---|---|
| uno | 21850 / 32768 B | 1398 / 2048 B | 21452 / 32768 B | 1398 / 2048 B | −398 B |
| uno328pb | 21894 / 32768 B | 1404 / 2048 B | 21496 / 32768 B | 1404 / 2048 B | −398 B |
| leonardo | 24134 / 32768 B (24082 in plan 01's single-ordinal 268d844 build) | 1839 / 2560 B | 23810 / 32768 B | 1839 / 2560 B | −324 B |

**Leonardo bootloader-ceiling check: 23810 B < 28672 B** — well inside the real ATmega32U4 ceiling that
`platformio.ini`'s override exposes; the image does not encroach on the Caterina bootloader reservation.

## Task 3 — The published host is refused on both ordinals, and the part is unchanged

### (a) Isolate the shared config

`~/.firestarter/` existed at the start of this task (`config.json` containing `{"port":
"/dev/ttyACM0"}`) — created by this plan's own task 1/2 post-204-host reads, since it did not exist at
the *plan's* start per the orchestrator-verified rig state. Snapshotted by move to
`/home/vscode/.local/share/gsd204-scratch/firestarter-config-snapshot` before the two old-host legs,
restored by move immediately after (overwriting whatever the old host itself wrote there), then
**deleted entirely at the end of this task** — see "Final state" below — so the operator's machine ends
the phase exactly as it started: no `~/.firestarter/` at all. Never deleted mid-sequence; always moved.

### (b) The published host's own help — the invocation source and the version evidence

```
$ "$HOME/.local/share/gsd-204-oldhost-venv/bin/firestarter" --version
Firestarter, version 3.0.0b49

$ "$HOME/.local/share/gsd-204-oldhost-venv/bin/firestarter" verify --help
Usage: firestarter verify [OPTIONS] EPROM INPUT_FILE

  Verifies the content of an EPROM.

Options:
  -a, --address TEXT  Verify start address in dec/hex
  -f, --force         Force, even if the VPP or chip id doesn't match.
  --help              Show this message and exit.

$ "$HOME/.local/share/gsd-204-oldhost-venv/bin/firestarter" blank --help
Usage: firestarter blank [OPTIONS] EPROM

  Checks if an EPROM is blank.

Options:
  -f, --force  Force, even if the VPP or chip id doesn't match.
  --help       Show this message and exit.
```

Same option shape as the post-204 host (`-f`/`--force`, positional `EPROM` and `INPUT_FILE`) — the
invocation below is taken directly from this output, not assumed from the working tree's CLI.

### (c) The verify refusal

```
$ timeout 300 "$HOME/.local/share/gsd-204-oldhost-venv/bin/firestarter" verify -f w27c512 \
    /home/vscode/.local/share/gsd204-scratch/pre.bin
Connecting...Connecting... OK
Verifying /home/vscode/.local/share/gsd204-scratch/pre.bin against W27C512
ERROR: Unknown command: 6
Programmer error during VERIFY: Programmer error during init: Unknown command: 6
Verify for W27C512 failed.
```

- **Exit code: 1**
- **Duration: 3.56 s** — well inside the 300 s bounding timeout, not a stall.
- **Non-empty output**, naming the offending ordinal (`Unknown command: 6` — `CMD_VERIFY`, retired in
  plan 01).

This is byte-for-byte the same wording plan 01's tracer captured for the same ordinal (`204-BENCH-TRACER.md`
§ "(f) Negative control"), now against firmware where ordinal 4 is ALSO retired rather than left live as
a control — confirming the refusal path is unchanged by the second retirement.

### (d) The blank refusal

```
$ timeout 300 "$HOME/.local/share/gsd-204-oldhost-venv/bin/firestarter" blank -f w27c512
Connecting...Connecting... OK
Blank checking EPROM W27C512
ERROR: Unknown command: 4
Programmer error during BLANK_CHECK: Programmer error during init: Unknown command: 4
```

- **Exit code: 1**
- **Duration: 3.49 s** — well inside the 300 s bounding timeout, not a stall.
- **Non-empty output**, naming the offending ordinal (`Unknown command: 4` — `CMD_BLANK_CHECK`, retired
  in plan 03).

Where plan 01's positive control for this same ordinal reported `WARN: VPP is high` and then a served
`Not blank, at 0x000000, v: 0x18` verdict (ordinal 4 was still live then), this transcript instead
refuses at `init` before any VPP warning or chip interaction — this is now the SAME refusal shape ordinal
6 already showed, because `is_memory_cmd(4)` is now false and `configure_memory` never runs, exactly as
`204-RESEARCH.md` § "The Refusal Path, Traced End To End" describes.

**D-05 cost, recorded verbatim as required:** both refusals read as "unknown command" — a message that
would read to an operator more like a corrupt frame or garbled transport than a deliberate version
boundary. Neither the meta catalog's format string nor the published wheel's own catalog module softens
this; the pre-`3.1.0` host is shipped code this phase cannot change. This cost was accepted deliberately
at design time (D-05); Phase 207 owns naming the boundary for a human in the wiki, and the verbatim text
above is what it has to work from.

### (e) Read-back equivalence — the no-side-effect half

`~/.firestarter/` restored to its step-(a) snapshot, then:

```
$ cd /workspaces/firestarter_app && .venv311/bin/firestarter read -f W27C512 \
    /home/vscode/.local/share/gsd204-scratch/post.bin
... [same VPP-high warning as task 2's verify/blank runs; no chip-ID warning this time] ...
Read complete (7.40s). Data saved to /home/vscode/.local/share/gsd204-scratch/post.bin
```

- **`post.bin`: 65536 bytes**
- **SHA-256: `a094e902a30b4fa3369ee493338351e11a8b6667f7539460b63f78dce896ae43`**
- `cmp pre.bin post.bin` exits 0, `cmp mid.bin post.bin` exits 0 — **all three whole-device reads
  (pre-swap baseline, post-swap mid-point, post-refusal end) share one digest, over all 65536 bytes.**

```
$ python3 -c "... sha256 over pre.bin, mid.bin, post.bin ..."
three reads, one digest: a094e902a30b4fa3369ee493338351e11a8b6667f7539460b63f78dce896ae43
```

Neither the refused `verify` nor the refused `blank` wrote or erased anything on the part. This is
**observed on silicon** — three independent whole-device reads sharing one digest — not argued from
where the refusal fired in the dispatch loop, per D-09. This is specifically the property that rules out
a silent erase, the worst failure mode a blank-check ordinal retiring badly could produce.

### Final state — `~/.firestarter/`

```
$ rm -rf "$HOME/.firestarter"
$ ls -la ~/.firestarter
ls: cannot access '/home/vscode/.firestarter': No such file or directory
```

Absent at the end, exactly as it was absent at the plan's start (per the orchestrator-verified rig
state). Never deleted mid-sequence — only ever moved aside and restored — until this final cleanup step,
matching plan 01's own protocol.

## Coverage gap — stated, not hidden

**Both skew directions in this matrix ran on a Leonardo only.** Its buffer is 1024 bytes
(`DATA_BUFFER_SIZE=1024` in `platformio.ini`'s `[env:leonardo]`), not the Uno's 512, and the host sizes
its write chunks from the firmware's own reported buffer size. **No Uno-class board is attached to this
devcontainer.** A pass on this matrix demonstrates nothing about the 512-byte chunked-transfer path —
closing that gap needs a separate board and a separate leg. This gap is inherited unchanged from plan
01's tracer record and is not narrowed by this plan.

**What the host could not tell you, at any point in this matrix:** its port probe truncates the
prerelease suffix, so `3.0.0b33` (pre-204), the post-204 working-tree build, and any other prerelease
are indistinguishable to it at runtime. At no point in this matrix could either host confirm which
firmware was actually on the board — the commit shas recorded in the role table above, and the flash
commands recorded at each step, are the only record.

## Summary of what this plan proves

1. **REL-02 (criterion 1):** a post-204 host performs `verify` and `blank` correctly against pre-204
   firmware, observed on the bench — `verify` matches (exit 0), `blank` reports not-blank (exit 1 via
   the designed abort-predicate fast path), and neither output carries an unknown-command line.
2. **REL-03 / FWCMD-06 (criterion 2):** a published `3.0.0b49` host receives an explicit, coded refusal
   naming the offending ordinal on BOTH retired ordinals (6 and 4) from post-204 firmware — never
   silence, never a hang, both transcripts captured verbatim with exit code and duration.
3. **D-09 (criterion 3):** the seated part's 65536 bytes are byte-identical across the whole matrix —
   three reads (pre-swap, post-swap, post-refusal), one SHA-256 digest.
4. **D-07 (criterion 4):** every role is named by commit sha or pinned version; the label substitution
   is stated explicitly; the host's inability to read back which firmware is on the board is stated
   explicitly.
5. **Coverage gap (criterion 5):** the Leonardo-only limitation is stated plainly above, not papered
   over.
6. **Baseline for Phase 205 (criterion 6):** per-target flash and RAM figures recorded for both sides of
   the sweep, giving Phase 205's own measurement a real Phase 204 baseline instead of a Phase 201-era
   one.

**Open question NOT resolved by this plan, carried forward:** the seated part's identity
(`WINDOWS.md` entry 3) — see "Open question carried, not resolved" at the top of this record. Every
claim above is chip-identity-independent by construction, but the record does not assert the part is a
confirmed W27C512.
