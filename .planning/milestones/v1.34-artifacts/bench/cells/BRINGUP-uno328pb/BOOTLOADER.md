# BRINGUP-uno328pb — Bootloader Interrogation & Judged-Span-Policy Derivation

**Target:** `uno328pb` (ATmega328PB, `urboot 384 B` bootloader, `urclock` programmer)
**Port:** `/dev/ttyUSB0` (CH340 USB-serial bridge — see "Board identity" below)
**Purpose:** Resolve `rig-pins.json` `targets.uno328pb.judged_span_policy`'s deliberate
`PENDING-xshowvector` placeholder **before** anything on this target is judged
(`judge_readback.py` refuses to run while the policy is still that placeholder). This is the
milestone's single sharpest false-RED risk (T-160-63): on a vector bootloader, avrdude's
urclock programmer patches the application's reset vector — and one designated interrupt
vector — before writing, so a naive `[0, span)` compare would report MISMATCH at 0x0000 on
**every** correctly-flashed board.

---

## Board identity (signature probe, cross-checked against the operator's declaration)

Operator's silkscreen declaration (task 1, verbatim): `"ATmega328PB"`.

`probe_board.py --target uno328pb --port /dev/ttyUSB0 --show-urclock` (full record:
`probe.json`):

- `connected_part`: `atmega328pb`
- `board_signature`: `0x1e9516` (the project's own known-good mapping for this exact board —
  see `probe_board.py`'s module docstring: a v1.7 bench note once mislabeled this board's
  silicon as a plain Uno, corrected only by this same direct signature measurement)
- `mcu_matches`: `true`
- `signature_route`: `route1`

**Agreement:** the operator's silkscreen declaration (`ATmega328PB`) and the avrdude signature
probe (`atmega328pb`, `0x1e9516`) **agree**. No disagreement to stop on.

**Corroborating signal (recorded separately, as the plan requires):** the `arduino` programmer
was attempted against this exact board and port (`logs/05_corroborating_arduino_programmer_open_attempt.stderr.log`):

```
Warning: attempt 1 of 10: not in sync: resp=0xa0
Warning: attempt 2 of 10: not in sync: resp=0xfc
... (10 attempts, alternating 0xfc/0xfe)
Error: unable to open port /dev/ttyUSB0 for programmer arduino
```

`rc=1`. This matches `probe_board.py`'s own docstring note ("`-c arduino` against the 328PB
board fails 'unable to open programmer'") — a second, independent signal that this board is
not a plain ATmega328P (which would open fine under `-c arduino`).

**Also recorded (present, non-authoritative port-identity datum, PROCEDURE.md P-02):** no `hw`
command was run against this board in this bring-up — this plan needs no chip and no arm
binary invocation for the interrogation itself; the arm binary is first invoked in task 3's
flash step, and `hw`'s `controller:` line has already been shown non-diagnostic in
`BRINGUP-uno` (host-app limitation, D-16, out of scope here).

---

## The four urclock bootloader interrogation queries — full raw output

Two invocations were required to obtain a clean four-probe set (Rule 1 deviation — see
"Tool defect found and fixed" below). The **first** invocation used the wrong option name for
the boot-size query (`-xshowbootsize`, copied from 160-RESEARCH.md's own speculative,
never-run Code Example 5) and it errored; the **second**, corrected invocation
(`-xshowboot`) is the one whose four results are the ones this determination stands on. Both
are quoted below in full — the plan requires recording "any that return an error, because
'this bootloader does not support that query' is itself part of the answer," and this
error is exactly that shape (a wrong option name is its own kind of answer: it says nothing
about the *bootloader*, but a great deal about the tool that asked it wrong).

Both invocations ran as `avrdude -C <pinned avrdude.conf> -c urclock -p atmega328pb -b 115200
-P /dev/ttyUSB0 -n -xshow*`, via `probe_board.py`'s `run_urclock_probes()` (source of truth:
`probe.json`'s `urclock_probes` field, current/corrected state; the pre-fix logs are preserved
separately in `logs/`).

### Query 1 — `-xshowall` (everything at once)

```
=== rc=0 ===
STDOUT:
ffffffffffff 2026-08-21 20.05 firestarter_uno328pb.hex 25598 store 6750 meta 36 boot 384 u7.7 weu-jPrac vector 25 (SPM_Ready) ATmega328PB

STDERR:

Avrdude done.  Thank you.
```

This single line already carries the answer to every other query: `boot 384` (bootloader
size, matching `rig-pins.json`'s recorded `"urboot 384 B"`), `u7.7 weu-jPrac` (bootloader
version string), and — decisively — `vector 25 (SPM_Ready)`.

### Query 2 — `-xshowvector` ← THE Pitfall-3 question

```
=== rc=0 ===
STDOUT:
vector 25 (SPM_Ready)

STDERR:

Avrdude done.  Thank you.
```

**This is the determination.** A non-vector (BOOTRST) urboot build reports no vector line at
all (or an explicit "not a vector bootloader" text) under this query; this board's urboot
build reports `vector 25 (SPM_Ready)` — a named designated vector — which is only printed
because this build **is** a vector bootloader (per the `urboot`/avrdude `-x?` documentation
quoted in 160-RESEARCH.md Pitfall 3: "The interrupt vector table of every application burned
with a vector bootloader needs to be patched before being uploaded ... Avrdude's urclock
programmer will patch the application automatically").

**Determination: this IS a vector bootloader.** The designated vector is interrupt vector 25,
named `SPM_Ready`.

### Query 3 — `-xshowboot` (bootloader size; corrected option name, see below)

```
=== rc=0 ===
STDOUT:
384

STDERR:

Avrdude done.  Thank you.
```

384 bytes, matching `rig-pins.json`'s `targets.uno328pb.bootloader: "urboot 384 B"` and
`-xshowall`'s own `boot 384` field.

**Pre-fix attempt (`-xshowbootsize`, the wrong option name — recorded because an error is part
of the answer):**

```
=== rc=1 ===
STDOUT:
(empty)
STDERR:
Error: invalid extended parameter -x showbootsize
avrdude -c urclock extended options:
  -x showall         Show all info for connected part and exit
  -x showid          Show Urclock ID and exit
  -x showdate        Show last-modified date of flash application and exit
  -x showfilename    Show filename of last written application and exit
  -x showapp         Show application size and exit
  -x showstore       Show store size and exit
  -x showmeta        Show metadata size and exit
  -x showboot        Show bootloader size and exit
  -x showversion     Show bootloader version and capabilities and exit
  -x showvector      Show vector bootloader vector # and name and exit
  -x id=<str>        Location of Urclock ID, eg, F.12345.6
  -x title=<str>     Title stored and shown in lieu of a filename
  -x bootsize=<n>    Override/set bootloader size
  -x vectornum=<n>   Treat bootloader as vector b/loader using vector <n>
  -x eepromrw        Assert bootloader EEPROM read/write capability
  -x emulate_ce      Emulate chip erase
  -x restore         Restore a flash backup and trim the bootloader
  -x initstore       Fill store with 0xff on writing to flash
  -x nofilename      Do not store filename on writing to flash
  -x nodate          Do not store application filename and no date either
  -x nostore         Do not store metadata except a flag saying so
  -x nometadata      Do not support metadata at all
  -x noautoreset     Do not reset the board after opening the serial port
  -x delay=<n>       Additional <n> ms delay after reset, can be negative
  -x strict          Use strict synchronisation protocol
  -x help            Show this help menu and exit
Error: unable to parse list of -x parameters

Avrdude done.  Thank you.
```

This is itself the answer to a different question than the one intended: the bootloader does
support a boot-size query, but under the name `showboot`, not `showbootsize` — the error's own
printed help menu is what revealed the correct name (full logs:
`logs/01_probe_board_show_urclock.stdout.log` / `.stderr.log`).

### Query 4 — `-xshowversion` (bootloader caps, incl. read)

```
=== rc=0 ===
STDOUT:
u7.7 weu-jPrac

STDERR:

Avrdude done.  Thank you.
```

Bootloader version `u7.7`, capability flags `weu-jPrac` — recorded verbatim; no further
decode is needed by this plan (the read-chain capability is proven empirically in task 3, not
inferred from this string).

---

## Tool defect found and fixed (Rule 1 — auto-fixed bug)

`tools/probe_board.py`'s `_URCLOCK_PROBES` constant carried `"-xshowbootsize"`, copied
verbatim from 160-RESEARCH.md's Code Example 5 — itself explicitly marked `"NOT RUN — no
board attached"` at authoring time, i.e. a guess, never bench-verified. Run live against this
real board, `-xshowbootsize` is not a recognized urclock extended option at all (see the
Query 3 error above); the option's real name, per avrdude's own printed help menu, is
`showboot`. Fixed in `tools/probe_board.py` (`_URCLOCK_PROBES = ["-xshowall", "-xshowvector",
"-xshowboot", "-xshowversion"]`), and the corrected four-probe set re-run (results above,
current `probe.json` state). The original wrong-option error is preserved above and in
`logs/01_probe_board_show_urclock.stdout.log` / `.stderr.log`, satisfying the plan's own
"any that return an error ... is itself part of the answer" requirement literally: the boot-
size *query* the plan's own Code Example 5 specified did, in fact, error, and that error is
recorded here in full — the corrected re-run alongside it is what actually answers the
underlying question (bootloader size).

---

## Vector determination and judged-span-policy decision

**This is a vector bootloader** (Query 2's `vector 25 (SPM_Ready)` line is the specific
output line establishing it). Per the plan's own named-alternative branch: `judged_span_policy`
is set to the **vector-exclusion** policy, and `vector_exclusions` is populated with the
specific offset/length windows for the reset vector and the designated vector — derived from a
**direct measurement**, not from a formula recalled from a datasheet, so the derivation is
falsifiable on its own terms rather than trusted by assertion.

### Derivation: a real flash + read-back, diffed against the raw hex, BEFORE the comparator was armed

With the judged-span policy still a placeholder, `judge_readback.py` refuses to run (by
construction) — so the derivation below used a **separate, ad hoc, unjudged** diagnostic
read-back (not the phase's judging tool, and not a position record): the control arm was
flashed via the pinned PlatformIO path (task 3's own first action, reused here since the board
had to be flashed exactly once regardless), then read back directly with the pinned avrdude
binary (`-A -U flash:r:...:r`, the identical mechanism `judge_readback.py` itself uses
internally), then diffed byte-for-byte against `avr-objcopy`'s normalization of the control
arm's own `.hex` over its full 26074 B extent. This is the plan's own sanctioned
"inconclusive → resolve by measurement" path, applied here not because the vector/non-vector
*category* question was inconclusive (it was not — Query 2 settled that outright) but because
the category answer alone does not hand over concrete byte *offsets*, and a measured offset is
strictly more defensible than one computed from a recalled datasheet vector-table ordering.

Commands (full record: `logs/03_pio_upload_control_event1.std{out,err}.log`,
`logs/04_diag_avrdude_read.std{out,err}.log`):

```
git -C /workspaces/firestarter checkout 8695ee52c27a4bee4387c5c489afd5f3d7275e8a   # cwd: /workspaces
/usr/local/bin/pio run -t upload -e uno328pb --upload-port /dev/ttyUSB0            # cwd: /workspaces/firestarter
/home/vscode/.platformio/packages/tool-avrdude/avrdude \
  -C /home/vscode/.platformio/packages/tool-avrdude/avrdude.conf \
  -c urclock -p atmega328pb -b 115200 -P /dev/ttyUSB0 -A \
  -U flash:r:.planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-uno328pb/diag_readback.bin:r           # cwd: /workspaces
/home/vscode/.platformio/packages/toolchain-atmelavr/bin/avr-objcopy \
  -I ihex -O binary \
  .planning/milestones/v1.34-artifacts/images/firestarter_uno328pb.control.hex \
  .planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-uno328pb/diag_expected_control.bin                # cwd: /workspaces
```

PlatformIO's own build report for this flash: `Flash: [========  ]  79.6% (used 26074 bytes
from 32768 bytes)` — confirms the control arm's own known span (26074 B) was actually written.

**Result — a byte-for-byte diff of the full 26074 B judged extent:**

Exactly **5 bytes** differ, at offsets `0, 1, 2, 3, 102` — and every one of them falls inside
one of exactly two 4-byte windows:

```
reset vector (vector 0)       [0:4)     expected = 0c 94 cf 01   actual = 3f cf 75 72
vector 25 (SPM_Ready) slot    [100:104) expected = 0c 94 f7 01   actual = 0c 94 cf 01
```

Both the expected and actual bytes at each window decode as a 2-word AVR `JMP` instruction
(opcode word `0x940C`, encoded little-endian as bytes `0c 94`) — exactly the instruction shape
urclock's vector-patching mechanism produces (a `JMP` to a new target address), confirming both
windows are genuinely vector-table slots, not coincidental noise. **Zero bytes differ anywhere
else in the 26074 B judged extent** — i.e. every discrepancy between the correctly-flashed
board's read-back and its own compiled hex is accounted for by these two windows, and nothing
is left unexplained.

- **Reset vector, offset 0, length 4:** all 4 bytes differ (`0c 94 cf 01` → `3f cf 75 72`) —
  urclock redirects the application's own reset vector to jump into the `urboot` bootloader
  entry point, exactly as Pitfall 3 predicts.
- **Vector 25 (SPM_Ready), offset 100, length 4:** offset derived as `vector_number * 4` bytes
  (RESET = vector 0, each subsequent AVR interrupt vector occupies a 4-byte slot on a
  JMP-capable device such as the ATmega328PB, whose 32 KiB flash exceeds the 8 KiB `RJMP`-only
  ceiling) = `25 * 4 = 100`. 1 of the 4 bytes differs (offset 102, `f7` → `cf`) — urclock uses
  this slot to store a copy of the application's *original* reset target (so the bootloader
  can still reach the application), and only the byte that actually encodes part of the jump
  target address changed; the opcode word (`0c 94`) and the target's high byte (`01`) happened
  to already match. The full 4-byte slot is excluded regardless, because the *slot* — not the
  one byte that happened to differ on this particular build — is what urclock's mechanism
  patches by design; a future rebuild could shift which byte(s) within the slot actually
  change.

**Resolved value:** `targets.uno328pb.judged_span_policy = "vector-exclusion"`,
`vector_exclusions = [{"offset": 0, "length": 4, "reason": "reset vector ..."}, {"offset": 100,
"length": 4, "reason": "designated interrupt vector 25 (SPM_Ready) ..."}]` (full reason text in
`rig-pins.json`).

### Stated limits (SC#2's own requirement)

- **Bytes excluded:** 8 (two 4-byte windows).
- **Bytes remaining judged, control arm:** 26074 − 8 = **26066** of 26074 (99.97%).
- **Bytes remaining judged, v1.33 arm:** 23000 − 8 = **22992** of 23000 (99.97%).
- **Why the check stays falsifiable at that strength:** task 3's own D-03 cross-flash measures
  the two arms' `uno328pb` images diverging by far more than 8 bytes across the judged
  span — an excluded 8 bytes out of a 26000+-byte judged region cannot plausibly mask a
  wrong-arm flash; the detector's post-exclusion strength is stated as a number in
  `CROSSFLASH.md`, not asserted as a given.

---

## Metadata-suppression confirmation

urclock writes a filename + date block into flash below the bootloader **unless**
`-xnometadata` is passed. This target is flashed only through the PlatformIO upload path
(`pio run -t upload -e uno328pb`), never through the host app's own firmware-install path
(forbidden — see `rig-pins.json` `forbidden_argv0` / PROCEDURE.md's forbidden-invocations
table). Read directly from the PlatformIO builder source (not from a repeated live probe,
since the option is unconditionally appended for this protocol and does not depend on which
arm is being flashed):

```
$ grep -n "nometadata" ~/.platformio/platforms/atmelavr/builder/main.py
220:        env.Append(UPLOADERFLAGS=["-xnometadata"])
```

This line runs unconditionally whenever `upload_protocol == "urclock"` (this target's only
protocol) — confirming the suppression option is present on every PlatformIO upload of this
target, control or v1.33.

**Consequence if it were ever absent:** urclock would write a filename + last-modified-date
block below the bootloader (per `-xshowall`'s own printed fields, e.g. `firestarter_uno328pb.hex`
and a date like `2026-08-21 20.05`, visible in Query 1's raw output above — this board's
*current* content, from a prior write, still carries exactly such a block). That block sits
inside the flash's unjudged region (near the bootloader, well above the judged
`[0, hex_span)` prefix this plan's judge compares), so it would make the **whole-flash
unjudged SHA** (`sha_whole_flash_unjudged`) date-dependent and non-reproducible from one flash
to the next — while the **judged** span, which this plan's exclusion windows sit entirely
within (offsets 0–103, far below the 384 B bootloader's own base near the top of the used
region), would stay clean and unaffected either way. This is exactly why `sha_whole_flash_unjudged`
is recorded as an explicitly **unjudged** datum (D-02) and never consulted in the
`judged_match` decision.
