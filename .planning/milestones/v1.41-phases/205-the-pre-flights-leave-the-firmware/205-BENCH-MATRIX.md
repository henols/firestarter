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

## B4 — flash post-205 firmware

```
$ cd /workspaces/firestarter_fw && git status --porcelain && git rev-parse --short HEAD
6e11d05

$ pio run -e leonardo -t upload
...
avrdude: 23314 bytes of flash written
avrdude: verifying flash memory against .pio/build/leonardo/firestarter_leonardo.hex:
avrdude: 23314 bytes of flash verified
avrdude done.  Thank you.
========================= [SUCCESS] Took 5.90 seconds =========================

$ sha256sum .pio/build/leonardo/firestarter_leonardo.hex
38ed1da7f7a754472a85ec49c18341064120e8cc8c03465a82d7c1ad185db5b2  .pio/build/leonardo/firestarter_leonardo.hex
```

**Exit 0.** No avrdude verification mismatch. `.hex` digest matches `205-FLASH-RAM.md`'s phase-exit
leonardo digest exactly. Live tree porcelain empty before and after; branch and HEAD unchanged
(`6e11d057b59977dd870c1ddcc588dd2f6f3ea1db`, `v1.41-verification-to-host`).

**Label substitution, restated:** "post-205 firmware" means commit
`6e11d057b59977dd870c1ddcc588dd2f6f3ea1db`. Like the pre-205 build, it carries no `3.1.0b1` string —
the commit sha and this `.hex` digest are the only record.

**A limit stated plainly, not glossed over:** no whole-device read was taken between B3 (the last
chip-content-affecting event, on pre-205 firmware) and this reflash. Chip content on an EEPROM is not
expected to be affected by an AVR firmware flash — the flash operation addresses the ATmega32U4's own
program memory, not the external RURP-bus-driven part — but this record does not assert survival by
inference where a read-back could have proven it. B5 below re-establishes what matters for criterion
3 regardless: it targets the same address B2/B3 already established as non-blank, and its own
pre-condition (a refusal on B3, an acceptance on B5) does not depend on whether the exact byte values
survived the intervening reflash unread.

**Exit 0. Duration: 5.90s** (`pio run -t upload`, no separate clean build needed — `.pio/build`
cache from the live tree's own prior build already matched).

## B5 — criterion 3, the UV leg

Against the same target address (`0x000000`) B2/B3 already exercised, the identical `write -b`
invocation B3 ran, with `--skip-erase`, on post-205 firmware. **PROXY leg** — W27C512 riding the UV
handler, protocol `0x07`, the file FWBLANK-01/FWBLANK-04 both change; the code path is the one under
test, the silicon is not UV.

```
$ firestarter -p /dev/ttyACM0 write w27c512 patB.bin -a 0x000000 -b --skip-erase -f
Connecting...Connecting... OK
Writing patB.bin to W27C512
WARN: VPP is high: 13.0V > 12.0V
Programmer warning: VPP is high: 13.0V > 12.0V
  [progress bar elided, denominator 0x0040]
Write to W27C512 successful (0.81s).
```

- **Exit code: 0.** **Duration: 4.27s** (wall-clock; command's own reported time 0.81s).
- **Reaches the firmware UNREFUSED** — the write-init blank check FWBLANK-01 removes no longer
  exists on this firmware at all (not merely bypassed by a flag), so `-b`'s host-side skip signal and
  the firmware's now-total absence of the check agree, and the write proceeds against a target region
  that is genuinely non-blank (still `patA.bin`'s `0x11223344` content from B2, unless the untested
  reflash-survival question above resolved otherwise — either way, the write programmed the region it
  was given).

**Read-back proof — the region now holds exactly what was written:**

```
$ firestarter -p /dev/ttyACM0 verify w27c512 patB.bin -a 0x000000 -f
Connecting...Connecting... OK
Verifying patB.bin against W27C512
match, 0 bad of 64 compared of 64 (0x000000-0x00003F)
Verify for W27C512 successful (0.30s).
```

- **Exit code: 0. Duration: 3.76s** (wall-clock; command's own reported time 0.30s). Clean match,
  0 bad of 64 compared — the region reads back exactly `patB.bin`'s content.

**Whole-device digest:**

```
$ firestarter -p /dev/ttyACM0 read w27c512 b5_wholedevice.bin -f
...
Read complete (7.40s). Data saved to b5_wholedevice.bin

$ sha256sum b5_wholedevice.bin
88fc2b445d991d23f78f2ea7338f22de0b9aa9d4867a06779fdfeb793c880fdd  b5_wholedevice.bin
```

- **65536 bytes.** First 64 bytes: `aa bb cc dd` x16 (`patB.bin`'s content). Remaining 65472 bytes:
  `0xFF`. Non-`0xFF` byte count: 64 — exactly the target region, and no more.
- **This digest DIFFERS from B2/B3's anchor (`839017bc...`) — expected, and exactly the difference
  criterion 3 predicts:** the target region's content changed from `patA.bin` to `patB.bin`; nothing
  outside it moved. **Exit 0. Duration: 10.82s** (command's own reported time 7.40s).

**This is the leg criterion 3 rests on.** A write to a non-blank target region on the UV handler now
reaches the firmware unrefused and programs the region it was given — observed here on silicon via a
read-back match and a whole-device digest showing exactly the expected, and only the expected,
change — not argued from where the check used to live in the dispatch loop.

## B6 — criterion 5, the erasable leg

The same part, plain `write` (no `-b`, no `--skip-erase`) — the `FLAG_CAN_ERASE` exemption path.
**PROXY leg**, same coverage limit as B5.

```
$ firestarter -p /dev/ttyACM0 write w27c512 patC.bin -a 0x000000 -f
Connecting...Connecting... OK
Writing patC.bin to W27C512
WARN: VPP is high: 13.0V > 12.0V
Programmer warning: VPP is high: 13.0V > 12.0V
  [progress bar elided, denominator 0x0040]
Write to W27C512 successful (1.11s).
```

- **Exit code: 0. Duration: 4.68s** (wall-clock; command's own reported time 1.11s). No refusal, no
  visible separate erase step in the CLI output — the erase-capable part's own auto-erase-before-write
  behaviour is unchanged from what an erasable part has always done on this path, and this leg's
  entire value is in having been run, since criterion 5 is a claim about an ABSENCE of a behaviour
  change.

**Whole-device digest:**

```
$ firestarter -p /dev/ttyACM0 read w27c512 b6_wholedevice.bin -f
...
Read complete (7.40s). Data saved to b6_wholedevice.bin

$ sha256sum b6_wholedevice.bin
1d3dd56a00aac3c057d6f20bd87d35059458df3192eb78a09ea8f450a203411b  b6_wholedevice.bin
```

- **65536 bytes.** First 64 bytes: `77 66 55 44` x16 (`patC.bin`'s content). Remaining 65472 bytes:
  `0xFF`. Non-`0xFF` byte count: 64.
- **Differs from B5's digest** (`88fc2b44...`) — expected: only the target region's content changed
  again, from `patB.bin` to `patC.bin`. `cmp` confirms the two files differ starting at byte 1 (the
  region's own first byte), nothing else. The erase-exempt behaviour this leg exercises shows **no
  behaviour change other than where a refusal would have come from on pre-205 firmware** — there was
  never a refusal on this path either before or after this phase, because `FLAG_CAN_ERASE` parts were
  always exempted (Phase 203's `test_write_on_erase_exempt_part_pays_no_guard_read` and siblings, host
  side; the firmware's own erase-before-check ordering, firmware side, now simply removed rather than
  bypassed).

## B7 — `erase -b` end to end, and the session-cost measurement

`erase -b`'s full contract (Phase 205 Plan 01, FWBLANK-02) exercised end to end against real silicon,
then timed against plain `erase` to measure the added wall-clock D-01's second port open costs. Full
timing detail, the derivation over Phase 203's cited medians, and the "why the measured figure is
larger than the connect-term derivation" explanation live in `205-SESSION-COST.md`; this section
carries the bench transcript itself.

```
$ firestarter -p /dev/ttyACM0 erase w27c512 -b -f      [x3 runs]
Connecting...Connecting... OK
Erasing EPROM W27C512
WARN: VPP is high: 13.0V > 12.0V
Programmer warning: VPP is high: 13.0V > 12.0V
Erase for W27C512 successful (0.58s). (main done)
Connecting...Connecting... OK
Blank checking EPROM W27C512
WARN: VPP is high: 13.0V > 12.0V
Programmer warning: VPP is high: 13.0V > 12.0V
  [progress bar elided]
blank/contact, 0 bad of 65536 compared of 65536 (0x000000-0x00FFFF)
Blank check for W27C512 successful (7.40s).
```

- **All three runs: exit 0.** Erased, then a whole-device host-side check (the second port open, D-01)
  confirms blank across all 65536 bytes — `erase -b` running end to end, on real silicon, three times,
  with the check itself being the only post-erase check in the system (probe A2's own reading, this
  plan's `<probe_disposition>`).
- **Timing (wall-clock, `time` around the subprocess), plain `erase` vs. `erase -b`, alternated
  before/after (all plain runs first, then all `-b` runs), same part, same board, no reflash between:**

| | Plain `erase` | `erase -b` |
|---|---|---|
| Run 1 | 4.138s | 14.753s |
| Run 2 | 3.946s | 14.543s |
| Run 3 | 3.929s | 14.578s |
| Median | **3.946s** | **14.578s** |

**MEASURED added wall-clock: 10.632s (Leonardo-class, N=3, this 64 KiB PROXY part).** Full derivation
and provenance in `205-SESSION-COST.md`.

**Closing whole-device digest:**

```
$ firestarter -p /dev/ttyACM0 read w27c512 b7_wholedevice.bin -f
...
Read complete (7.40s). Data saved to b7_wholedevice.bin

$ sha256sum b7_wholedevice.bin
71189f7fb6aed638640078fba3a35fda6c39c8962e74dcc75935aac948da9063  b7_wholedevice.bin
```

- **All 65536 bytes are `0xFF`** — the whole-device erase left the part genuinely blank, confirmed by
  an independent `read` (not only the `erase -b` check's own verdict), closing the digest chain on an
  erased, blank part.

## Digest chain, closed

| Step | Digest | Relative to prior | Why |
|---|---|---|---|
| B2 (anchor) | `839017bc0a27...df1d7` | — | patA at `0x000000`, rest blank |
| B3 (post-refusal) | `839017bc0a27...df1d7` | **same as B2** | refused write had no side effect |
| B5 (post-write) | `88fc2b445d99...80fdd` | **differs from B2/B3** | expected — patB overwrote the target region on post-205 firmware, nothing else moved |
| B6 (post-write) | `1d3dd56a00aa...3411b` | **differs from B5** | expected — patC overwrote the same target region again, exercising the erase-exempt path |
| B7 (post-erase) | `71189f7fb6ae...9063` | **all-0xFF, differs from B6** | expected — whole-chip erase, confirmed independently by a `read`, not only by `erase -b`'s own verdict |

No digest is unaccounted for; every difference above is one this record predicted before taking the
read, and every "unchanged" digest (B3 vs. B2) is the one place a silent side effect would have shown
up and did not.

## Stated coverage gaps

**1. An erasable part stood in for a UV one on every UV-handler leg (B2, B3, B5, B7).** No true UV
part is available on this bench (per the operator's Task 1 decision, `205-RESEARCH.md` § "Bench
parts"). The seated W27C512 is electrically erasable (`FLAG_CAN_ERASE` set) and rides the UV handler
(`eprom.cpp`, protocol `0x07`) — the file FWBLANK-01 and FWBLANK-02 both change — via the Phase 201-06
`--skip-erase` rehearsal mechanism, so the CODE PATH under test is identical to what a true UV part
would exercise. **The silicon is not.** Every UV-handler leg above is marked PROXY for this reason.

**2. `flash_intel.cpp` (protocol `0x10`) has zero validated chips in the registry and cannot be
benched at all, regardless of parts on hand.** `VALIDATED-EPROMS.md`'s Families table lists no
`PROTO_FLASH_INTEL` row — the protocol has no validated member. Its whole-device write-init call
(FWBLANK-01) is proven removed by native test (`test_val_flash_intel`) and the source-contract gate
only, never on silicon.

**3. `flash_nor_unlock.cpp` (protocol `0x06`) has exactly one validated part, `SST39SF020`, which is
not seated on this bench.** `VALIDATED-EPROMS.md` line 16 confirms it as the family's sole validated
member. Its whole-device write-init call (FWBLANK-01) is likewise proven removed by native test
(`test_val_nor_unlock`) and the source-contract gate only.

Quoted rather than re-derived, because it is the reasoning that makes removing that site safe rather
than risky — `.planning/notes/201-region-blank-check-latency-and-divergence.md` § 1, verbatim:

> "**Named non-claim: these two sites are not safely latent. They are one flag deep.**
> `firestarter write --skip-erase` sets `FLAG_SKIP_ERASE`... Passing `--skip-erase` against an
> electrically-erasable part on either of these two protocols suppresses the erase and makes the
> identical whole-device `mem_util_blank_check` refusal fire on a genuinely non-blank part — the exact
> defect BLANK-01/BLANK-02 fix on `eprom.cpp`, unfixed here by design... Of the four [validated
> Flash/EEPROM chips], only `SST39SF020` sits on one of D-11's two named sites
> (`firestarter_fw/src/proms/flash_nor_unlock.cpp:105`) and is reachable by it today."

That finding was about the LATENCY these two sites carried before this phase deleted them outright;
it is quoted here as the reasoning basis for treating their removal (rather than their region-scoping,
as `0x07`'s eprom.cpp site received in Phase 201) as safe — a full deletion of a site that was never
observed to be "safely latent" removes the latency rather than papering over it.

**4. No Uno-class board is attached to this devcontainer.** Every leg in this bench matrix ran on the
Leonardo (`DATA_BUFFER_SIZE=1024`, per `platformio.ini`'s `[env:leonardo]`), matching Phase 204's own
recorded gap. A pass here demonstrates nothing about the Uno's 512-byte chunked-transfer path — closing
that gap needs a separate board and a separate bench session. This gap is inherited unchanged from
Phase 204's bench matrix and is not narrowed by this plan.

## Chip-identity independence, stated per claim

Following `204-BENCH-MATRIX.md`'s discipline: every substantive claim above is evaluated against
whether it depends on the seated part's species being genuinely a W27C512, as opposed to depending
only on "the same physical part occupied the same socket throughout."

- **B0/B1 (rig, firmware roles):** chip-identity-independent — no chip content is involved.
- **B2 (non-blank setup), B3 (refusal), B5 (acceptance), B6 (erasable leg), B7 (erase -b):**
  chip-identity-independent by construction. Every claim is about behaviour observed against
  whichever physical part occupies the socket — a refusal, an acceptance, a digest match or mismatch —
  not about a chip-ID value. The `FLAG_CAN_ERASE` bit and the UV-handler code path (`eprom.cpp`,
  protocol `0x07`) are properties the host database assigns from the resolved chip name
  (`w27c512`, as typed on every command line above), not from a firmware-read chip-ID — so even if the
  firmware-reported chip-ID (`0x1818`, per the open item in "Rig identity") turned out to name a
  different part entirely, every command above still dispatched through the identical protocol
  handler and identical flag set, because the host resolves those from the CLI argument, not from the
  firmware's chip-ID read.
- **The one claim that IS chip-identity-DEPENDENT:** the PROXY characterization itself ("this is a
  W27C512, therefore FLAG_CAN_ERASE and protocol 0x07 apply") rests on the operator's Task 1
  statement and the CLI argument `w27c512` typed on every command — not on the firmware's own
  chip-ID probe, which (per the open item above) does not currently corroborate it. This is recorded
  as the record's one load-bearing identity assumption, distinct from every behavioural claim listed
  above, which would hold regardless of which part actually occupies the socket.

---
*Phase: 205-the-pre-flights-leave-the-firmware*
*Bench session: 2026-09-22*
