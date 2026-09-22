# Phase 205 Plan 07 — Bench Matrix: criteria 3 and 5 on silicon, the D-07 skew leg, `erase -b` end to end

**Date:** 2026-09-22
**Plan:** 205-07 — the bench plan closing FWBLANK-01, FWBLANK-02 and FWBLANK-04's silicon obligations
(criteria 3 and 5), the D-04 skew regression (D-07), and `erase -b`'s measured added wall-clock for
Phase 206's SESS-01.

This record follows `204-BENCH-MATRIX.md`'s executed format: a rig-identity section, a firmware-roles
table naming the commit sha and the local `.hex` digest for each role, one row per bench leg with its
exact command, verbatim output, exit code and wall-clock duration, the whole-device digest chain, and a
stated-coverage-gaps section.

**One honest limit shapes every UV-handler leg in this record: no true UV part is available.** A
W27C512 is seated. It is electrically erasable (`FLAG_CAN_ERASE`) and rides the UV handler
(`eprom.cpp`, protocol `0x07`) — the file FWBLANK-01 and FWBLANK-02 both change — so the code path
under test is identical and the silicon is not. **Every leg below that stands in for UV silicon is
marked PROXY.**

---

## Task 1 — the operator's answer, recorded verbatim

The blocking-human checkpoint (Task 1) was answered by the operator before any bench command ran. The
answer is reproduced here exactly as given:

> - **Shield revision: Rev 2.0.**
> - **JP4 and JP5: both intact** (neither cut).
> - **Seated part: W27C512**, confirmed, and the operator is content to erase and rewrite it several
>   times.
> - **Board: the Arduino Leonardo on `/dev/ttyACM0`**, confirmed, and may be reflashed twice during
>   this plan.
>
> Orchestrator's read-only port probe immediately before dispatch: exactly one board present,
> `usb-Arduino_LLC_Arduino_Leonardo-if00 -> ../../ttyACM0`. No other board attached.
>
> Task 1's remaining acceptance criterion — "no bench command has run before this answer" — is
> satisfied: the only thing run was the read-only `ls /dev/serial/by-id/` probe above.

**A note on chip identity, distinct from `WINDOWS.md` entry 3.** The operator's statement above is a
direct physical confirmation — the operator seated the part and knows what it is. This is independent
evidence from the firmware's own chip-ID probe, which (per the open item below, § Rig identity)
continues to read `0x1818` rather than the database's expected `0xda08` on this rig, for the same
reason `WINDOWS.md` entry 3 already records: the rig's VPP monitor does not reliably route to the
socket, and chip-ID sensing needs VPP driven onto A9 to work. That firmware-side finding is **not
re-investigated or forced past in this plan** — it is recorded here as still open, with the operator's
direct statement recorded as a second, independent line of evidence about the same physical part,
not as a resolution of the open firmware-side finding. Every claim below is stated as
chip-identity-independent where it can be, per the same discipline `204-BENCH-MATRIX.md` established.

Neither JP4 nor JP5 being cut is consistent with a 28-pin part with no A19 on socket pin 1 — the
`jp5_gate` module (§ below) predicate confirms `is_affected()` is `False` for this part's bus
configuration, so no interactive JP5 hazard prompt fired at any `erase`/`write` call in this session,
and none was expected to.

---

## Rig identity (re-derived this session, B0)

```
$ python3 -c "import glob,os; hits=[d for d in glob.glob('/sys/bus/usb/devices/*/') if os.path.exists(d+'idVendor') and open(d+'idVendor').read().strip()=='2341' and open(d+'idProduct').read().strip()=='8036']; assert len(hits)==1, 'expected exactly one 2341:8036 device, found %d' % len(hits); assert os.path.exists('/dev/ttyACM0'), '/dev/ttyACM0 is absent'; print('rig confirmed:', hits[0])"
rig confirmed: /sys/bus/usb/devices/3-3.1.2.2/
```

- Exactly one USB device enumerated with vendor:product `2341:8036` (Arduino Leonardo), at sysfs path
  `/sys/bus/usb/devices/3-3.1.2.2/` — the identical sysfs path `204-BENCH-MATRIX.md` recorded for the
  same rig.
- `/dev/serial/by-id/usb-Arduino_LLC_Arduino_Leonardo-if00 -> ../../ttyACM0`, confirmed by
  `readlink -f`.
- `/dev/ttyACM0` exists and is the node used for every command in this record.
- No other USB serial device is present (`ls /dev/serial/by-id/` shows exactly one entry).
- `firestarter_fw` has no `.gitmodules` — the detached worktree used for B1 below checks out
  completely; the worktrees-leave-submodules-empty hazard does not apply.
- **Exit: 0.** `Duration: <1s` (a single sysfs glob, no serial traffic).

**Chip-ID open item, carried forward, not re-investigated:** every unforced `read`/`erase`/`write`
attempt against the seated part this session reported `Chip ID 0x1818 does not match expected ID
0xda08` before `-f`/`--force` was applied — the identical reading `WINDOWS.md` entry 3 and
`204-BENCH-TRACER.md` already recorded for this same physical part. `-f` was required throughout this
session for the same documented reason: the rig's VPP monitor is a known-noisy proxy that does not
reliably route to the socket, and forcing past it is safe for a plain read/write/erase because
chip-ID sensing is the only VPP-dependent precondition check and does not itself gate array-content
transfer. **Every claim below is chip-identity-independent by construction** — every leg addresses the
same physical part in the same socket across the whole session, whatever species of chip a firmware
chip-ID sense would report, and the operator's own direct statement (Task 1) is recorded as
independent evidence about the same physical part.

---

## Firmware and host roles

Neither firmware build carries a distinguishing version string: `include/version.h`'s `VERSION` is a
hand-set literal bumped at a release cut, not per commit, and REL-01's `3.1.0b1` bump is Phase 207's,
not this plan's. **The host cannot read back which firmware is on the board** — `_probe_port`'s
`[\d.x]+` regex truncates a prerelease suffix — so the commit shas and local `.hex` digests below are
the only record of which artifact played which role at each step. "pre-205" and "post-205" are
documented label substitutions, not version strings either firmware or host emits.

| Role | Artifact | Commit sha | `.hex` sha256 | Built/installed at |
|---|---|---|---|---|
| **pre-205 firmware** | `firestarter_fw` detached worktree | `a4e002f2da0b44e7545ab43180951538e64022c1` (`fix(205-02): repair stale .planning path citations in flash-path sync gate` — the phase-entry tree per `205-FLASH-RAM.md`'s baseline; no `src/`/`include/` diff against `24e3fdf`, Phase 204's own "post-204 firmware" role, confirmed by `git diff --stat` before building) | `8beeb731831d04347c75528bebe2a7cdc04e1eeb1d3da76a3933dc8809ec710b` — **identical** to `205-FLASH-RAM.md`'s recorded phase-entry leonardo `.hex` digest, confirming the local build reproduces the phase-entry artifact exactly | `/home/vscode/.local/share/gsd205-fw-pre205-worktree`, flashed to the board via `pio run -e leonardo -t upload` |
| **post-205 firmware** | `firestarter_fw` working tree HEAD | `6e11d057b59977dd870c1ddcc588dd2f6f3ea1db` (`feat(205-05): refuse a negative wire address instead of clamping to 0` — carries FWBLANK-01 through FWBLANK-04's removal plus plan 05's fix; this plan's own phase-exit figure in `205-FLASH-RAM.md`) | `38ed1da7f7a754472a85ec49c18341064120e8cc8c03465a82d7c1ad185db5b2` (per `205-FLASH-RAM.md`'s phase-exit table; reproduced at B4 below) | `/workspaces/firestarter_fw`, flashed to the board via `pio run -e leonardo -t upload` |
| **post-205 host** | `firestarter_app` working tree HEAD, editable install | `c7c1d9a1c8207e77cf539ca0c68b6a01d317e888` | `/workspaces/firestarter_app/.venv-ci-188` (Python 3.11.16), driving every command in this record |

`firestarter_fw` never left branch `v1.41-verification-to-host` and was never checked out to a
different commit — the pre-205 build happened entirely inside the detached worktree, outside both
`/workspaces` and `firestarter_fw`'s own working directory, and the tree's cleanliness is re-verified
at B0/B1 and again at B4.

---

## B0 — rig identity, re-confirmed

See "Rig identity" above. **Exit 0**, exactly one `2341:8036` device, `/dev/ttyACM0` present, no other
board attached. Duration: <1s.

## B1 — build and flash the pre-205 artifact

```
$ cd /workspaces/firestarter_fw && git worktree add --detach \
    /home/vscode/.local/share/gsd205-fw-pre205-worktree a4e002f2
Preparing worktree (detached HEAD a4e002f)
HEAD is now at a4e002f fix(205-02): repair stale .planning path citations in flash-path sync gate

$ cd /home/vscode/.local/share/gsd205-fw-pre205-worktree && pio run -e leonardo
...
bootloader-guard: leonardo 23810/28672 B (83.0% of the safe ceiling, 4862 B margin, 4096 B bootloader reserved)
RAM:   [=======   ]  71.8% (used 1839 bytes from 2560 bytes)
Flash: [=======   ]  72.7% (used 23810 bytes from 32768 bytes)
========================= [SUCCESS] Took 3.00 seconds =========================

$ sha256sum .pio/build/leonardo/firestarter_leonardo.hex
8beeb731831d04347c75528bebe2a7cdc04e1eeb1d3da76a3933dc8809ec710b  .pio/build/leonardo/firestarter_leonardo.hex
```

Matches `205-FLASH-RAM.md`'s recorded phase-entry leonardo `.hex` digest exactly — the local build
from the detached worktree reproduces the phase-entry artifact byte for byte. **The pre-205 artifact
is a local build of the phase-entry sha, not a downloaded release asset — it IS the pre-205 source.**

```
$ pio run -e leonardo -t upload
...
avrdude: 23810 bytes of flash written
avrdude: verifying flash memory against .pio/build/leonardo/firestarter_leonardo.hex:
avrdude: 23810 bytes of flash verified
avrdude done.  Thank you.
========================= [SUCCESS] Took 5.87 seconds =========================
```

**Exit 0.** No avrdude verification mismatch. `fw --install` was NOT used (it flashes the attached
board and ignores `--board`, per the standing project finding) — `pio run -e leonardo -t upload` was
used throughout, as Phase 204 did.

**Live tree check, immediately after:**

```
$ cd /workspaces/firestarter_fw && git status --porcelain && git rev-parse --abbrev-ref HEAD && git rev-parse HEAD
v1.41-verification-to-host
6e11d057b59977dd870c1ddcc588dd2f6f3ea1db
```

Empty porcelain output, branch unchanged, HEAD unchanged. The live `firestarter_fw` tree was never
checked out to a different commit — the pre-205 build happened entirely inside the detached worktree.

**Label substitution, stated explicitly:** "pre-205 firmware" means commit
`a4e002f2da0b44e7545ab43180951538e64022c1`. Neither this build nor the post-205 build (B4) carries the
literal `3.1.0b1` string — that bump is Phase 207's. The host's port probe cannot read back which
firmware is on the board (`_probe_port`'s regex truncates the prerelease suffix), so this commit sha
and its `.hex` digest are the only record of which artifact was actually flashed at this step.

**Exit 0. Duration: ~9s** (`pio run` build 3.00s + `pio run -t upload` 5.87s, sequential).

## B2 — put the part into a known non-blank state

Using the Phase 201-06 `--skip-erase` rehearsal mechanism (`.planning/notes/201-region-blank-check-latency-and-divergence.md`
§ 1): erase the whole device, then write a known 64-byte pattern at address `0x000000` with
`--skip-erase` so the write-init blank check (still present and region-scoped on this pre-205
firmware) sees a genuinely blank target and succeeds, leaving the device deliberately non-blank at
exactly the address B3/B5 will target. **PROXY leg** — this is the W27C512 riding the UV handler
(`eprom.cpp`, protocol `0x07`) standing in for a true UV part; the code path is identical, the silicon
is not.

```
$ firestarter -p /dev/ttyACM0 erase w27c512 -f
Connecting...Connecting... OK
Erasing EPROM W27C512
WARN: VPP is high: 13.0V > 12.0V
Programmer warning: VPP is high: 13.0V > 12.0V
  [progress bar elided]
Erase for W27C512 successful (5.13s). (main done)
```

- **Exit 0. Duration: 8.70s** (wall-clock around the subprocess; the command's own reported internal
  time is 5.13s).
- `-f`/`--force` was required: the rig's VPP monitor is a known-noisy proxy that does not reliably
  route to the socket (the documented project-wide finding), and an unforced attempt is refused at the
  chip-ID precheck (`ERROR: Chip ID 0x1818 does not match expected ID 0xda08`) before any chip content
  is exchanged — recorded, not silently discarded, in "Rig identity" above. Forcing past it changes
  nothing about which ordinal or command is sent on the wire.

```
$ firestarter -p /dev/ttyACM0 write w27c512 patA.bin -a 0x000000 --skip-erase -f
Connecting...Connecting... OK
WARN: VPP is high: 13.0V > 12.0V
Programmer warning: VPP is high: 13.0V > 12.0V
[host-side pre-write guard read of the target region -- Phase 203's requires_blank_check,
 re-armed by --skip-erase per D-03; the region reads blank, so the guard passes]
Progress: +64 steps
EPROM read complete.
Connecting...Connecting... OK
Writing patA.bin to W27C512
WARN: VPP is high: 13.0V > 12.0V
Programmer warning: VPP is high: 13.0V > 12.0V
  [progress bar elided, denominator 0x0040]
Write to W27C512 successful (0.82s).
```

`patA.bin` is 64 bytes of `0x11 0x22 0x33 0x44` repeated 16 times (non-`0xFF`).

- **Exit 0. Duration: 7.86s** (wall-clock; command's own reported time 0.82s for the write itself,
  the remainder is the host-side guard's own read-then-connect-again cycle).

**Whole-device read, anchor digest:**

```
$ firestarter -p /dev/ttyACM0 read w27c512 b2_wholedevice.bin -f
Connecting...Connecting... OK
Reading EPROM W27C512, saving to b2_wholedevice.bin
WARN: VPP is high: 13.0V > 12.0V
  [progress bar elided]
Read complete (7.40s). Data saved to b2_wholedevice.bin

$ sha256sum b2_wholedevice.bin
839017bc0a270d316ceafca359ad71ce49e57353303044ec37c3e0980b6df1d7  b2_wholedevice.bin
```

- **65536 bytes.** First 64 bytes: `11 22 33 44` x16. Remaining 65472 bytes: `0xFF` (blank). Non-`0xFF`
  byte count: 64 — exactly the written region.
- **This digest (`839017bc...`) is the B2 anchor** — every later comparison in this record either
  matches it (proving no side effect) or differs from it in a stated, expected way (proving a write or
  erase actually landed).
- **Exit 0. Duration: 11.03s** (wall-clock; command's own reported time 7.40s).

## B3 — the D-07 skew leg, on the pre-205 firmware, BEFORE any reflash

With the post-205 host, `write -b` against the now-non-blank target region at `0x000000`, using
`--skip-erase` so the firmware's own erase-then-write path cannot mask the result. **This is the leg
that makes REL-04's claim an observation rather than an argument — the pre-205 firmware is on the
board only once, and this leg runs before B4's reflash, or not at all.**

```
$ firestarter -p /dev/ttyACM0 write w27c512 patB.bin -a 0x000000 -b --skip-erase -f
Connecting...Connecting... OK
Writing patB.bin to W27C512
WARN: VPP is high: 13.0V > 12.0V
Programmer warning: VPP is high: 13.0V > 12.0V
ERROR: Not blank, at 0x000000, v: 0x11
Programmer error during WRITE: Programmer error during init: Not blank, at 0x000000, v: 0x11
Write to W27C512 failed.
```

`patB.bin` is 64 bytes of `0xAA 0xBB 0xCC 0xDD` repeated 16 times — deliberately different content
from `patA.bin`, so a later successful overwrite (B5) is visibly distinguishable from B3's refused
attempt.

- **Exit code: 1.**
- **Duration: 3.81s** (wall-clock around the subprocess; the command failed before printing its own
  internal timing).
- **The refusal line is captured VERBATIM, not paraphrased:** `ERROR: Not blank, at 0x000000, v:
  0x11` / `Programmer error during WRITE: Programmer error during init: Not blank, at 0x000000, v:
  0x11` / `Write to W27C512 failed.` This is `MSG_ERR_NOT_BLANK` (0xB0) rendered as a full sentence —
  its catalog format string is `"Not blank, at 0x%06x, v: 0x%02x"` (`tools/catalog/messages.toml:571`)
  — a rendered sentence, not an unknown-id placeholder. `0x11` is `patA.bin`'s first byte, the content
  already sitting at `0x000000` from B2; this is the load-bearing line proving the check ran against
  genuine non-blank content, not a stale or wrong address.
- **Why this happened:** `write -b` used to mean "compose `FLAG_SKIP_BLANK_CHECK` (`0x08`) on the
  wire, so the firmware's own write-init check never runs." D-04 fully retires `0x08` — the post-205
  host never composes it, on any firmware. Pre-205 firmware still HAS its own region-scoped write-init
  blank check (from Phase 201) and, receiving no skip bit, runs it — and the target region genuinely
  is non-blank (B2's `patA.bin`), so it genuinely refuses. **This is the accepted D-04 cost, observed
  on silicon rather than argued from code structure.**

**Confirm no side effect — re-read the whole device:**

```
$ firestarter -p /dev/ttyACM0 read w27c512 b3_postrefusal.bin -f
...
Read complete (7.40s). Data saved to b3_postrefusal.bin

$ sha256sum b3_postrefusal.bin
839017bc0a270d316ceafca359ad71ce49e57353303044ec37c3e0980b6df1d7  b3_postrefusal.bin

$ cmp b2_wholedevice.bin b3_postrefusal.bin && echo "IDENTICAL to B2 -- no side effect"
IDENTICAL to B2 -- no side effect
```

**Digest unchanged from B2** (`839017bc...`, byte for byte over all 65536 bytes) — the refused write
had no hardware side effect.

**Label substitution, restated:** this leg ran against `a4e002f2da0b44e7545ab43180951538e64022c1`
("pre-205 firmware"), driven by the post-205 host (`c7c1d9a1c8207e77cf539ca0c68b6a01d317e888`). Neither
carries the literal `3.1.0b1` string; the commit sha is the only witness to which firmware produced
this refusal.

**PROXY note, restated:** this is the W27C512 riding the UV handler (protocol `0x07`) standing in for
a true UV part. The code path FWBLANK-01/FWBLANK-04 change is exercised identically to how a true UV
part would exercise it; the silicon itself is not UV-erasable-only.

---

*(This record continues with B4 through B7, the coverage-gaps section and the closing digest chain
in this plan's second commit.)*
