---
title: W29C020 no-regression bench transcript — protocol 0x05, milestone v1.39 Phase 194
phase: 194-real-page-size-reaches-the-firmware
plan: "07"
measured: 2026-09-15
status: AUTHORITATIVE — the silicon no-regression half of D-11. Not authoritative for any of the 9 previously under-sized parts. See §5.
pairs_with: .planning/v1.39/194-page-size-27-row-record.md
requirements: [PAGE-03 (hardware no-regression half only — hardware leg for the 9 held OPEN)]
---

# W29C020 no-regression bench transcript — Phase 194 Plan 07

Every figure below carries the verbatim command that produced it. Nothing here is carried
forward from research or from another plan without a citation.

---

## 1. The rig, as the operator described it

The operator supplied all four answers task 1 asked for, before any operation ran:

1. **Seated part:** a `W29C020` was placed in the socket. (Operator-confirmed.)
2. **Shield revision:** **Rev 2.0 (operator-stated)**. The reported `hw` value cannot
   distinguish the three shields the operator owns, so this project's rule is that the
   revision is asked, never inferred or probed. It is recorded here as an operator
   statement, not as a measurement.
3. **Serial port:** `/dev/ttyACM1` at the time of the operator's answer.
4. **Availability of any part from the 9 previously under-sized parts:** none of the 9 was
   on hand, and the ordered `W29C512` had not yet arrived. This matches D-10's assumption
   exactly. Nothing was discovered that would let PAGE-03's hardware leg close sooner.

---

## 2. Rig identity, re-confirmed (not merely trusted)

**Command:** `ls -la /dev/ttyACM*` — exactly one serial device present: `/dev/ttyACM1`.

**Command:** reading the USB sysfs descriptor tree for that device
(`/sys/class/tty/ttyACM1/device` → `/sys/devices/pci0000:00/0000:00:14.0/usb3/3-3/3-3.1/3-3.1.2/3-3.1.2.2`,
then `cat idVendor idProduct manufacturer product` on that path):

```
idVendor: 2341
idProduct: 8036
manufacturer: Arduino LLC
product: Arduino Leonardo
```

This is a **Leonardo**, not an Uno-class board. Per this project's chip-out-before-sideload
rule, the chip-removal requirement applies to Uno-class boards only. A Leonardo is exempt.
The `W29C020` therefore stayed seated across the firmware flash in §3.

**Command:** `firestarter -p /dev/ttyACM1 fw` (pre-flash) — result: `INFO: Buf val: 0x7b` /
`ERROR: Bad JSON`, the documented signature of firmware predating the current command
framing (every 2.x release, and every 3.0.0 pre-release before b8).

**Port re-identification after the flash (device numbers shuffle across a replug — the
Leonardo bootloader touch causes exactly this):** after `avrdude`'s 1200bps-touch reset, the
device disappeared and re-enumerated as `/dev/ttyACM0`. Re-checked the USB sysfs path for
the new device node — same physical path,
`/sys/devices/pci0000:00/0000:00:14.0/usb3/3-3/3-3.1/3-3.1.2/3-3.1.2.2` — confirming this is
the same physical board under a new device-number assignment, not a different board. Every
operation from §3 onward targeted `/dev/ttyACM0`, the port the board actually answered on.

---

## 3. Firmware flashed, and the version under test

This phase's own firmware was **built from source and flashed via PlatformIO**, not
downloaded from a GitHub release (the app's `fw --install` route downloads the latest public
release, `3.0.0b31`, which does not carry this phase's changes as a distinguishable release —
see the note below on why the version string is unchanged).

**Command:** `cd firestarter_fw && pio run -e leonardo`

```
bootloader-guard: leonardo 23734/28672 B (82.8% of the safe ceiling, 4938 B margin, 4096 B bootloader reserved)
```

Byte-identical to the figure `194-06-SUMMARY.md` recorded for the same environment,
confirming this is a from-source build of the committed tree at
`firestarter_fw@aabd0dd` (the tip of this session's `v1.39-protocol-0x05-write-correctness`
branch at flash time), not a stale artifact.

**Command:** `pio run -t upload -e leonardo --upload-port /dev/ttyACM0`

```
avrdude: 23734 bytes of flash written
avrdude: 23734 bytes of flash verified
========================= [SUCCESS] Took 6.94 seconds =========================
```

**Command (post-flash, confirming the board answers):** `firestarter --port /dev/ttyACM0 fw`

```
Current firmware version: 3.0.0b31, for controller: leonardo on port /dev/ttyACM0
```

**Note on the version string:** `include/version.h` defines `VERSION "3.0.0b31"` as a static
string literal. Phase 194 changed no line in that file and this phase's own plans never
called for a version bump — the change is internal to page-size derivation and never
touched the firmware's version identity. The reported `3.0.0b31` is therefore exactly this
phase's committed firmware, confirmed by the byte-identical flash-size figure above, not a
stale or mismatched build. Attributing the run to a specific commit rather than to the
version string: `firestarter_fw@aabd0dd`.

**Host version under test.** `firestarter --version` → `Firestarter, version 3.0.0b44`, run
from the pinned Python 3.11 venv named in this plan's required reading
(`/tmp/claude-1000/-workspaces/ca7dfea4-70ae-41b2-8b03-4a9743e17e1d/scratchpad/venv311/bin/firestarter`).

---

## 4. Chip-ID confirmation, write, and read-back

### 4a. Chip-ID (never the printed marking)

**Command:** `firestarter -v --port /dev/ttyACM0 id W29C020`

The host resolved the database row and sent `chip-id: 55877` (`0x0000da45`) as part of the
`CHECK_CHIP_ID` command, matching `firestarter_app/firestarter/data/chip_database.json`'s
`WINBOND` row `W29C020,W29C020C,W29C022` (`programming.chip_id_value == "0x0000da45"`,
confirmed by direct read of the regenerated database — see command below). The firmware
returned `END: (end done)` and the host reported:

```
Chip ID check passed for W29C020: (main done) (0.03s)
```

**Command confirming the expected database value independently:**

```
cd firestarter_app && python3 -c "
import json, pathlib
db = json.loads(pathlib.Path('firestarter/data/chip_database.json').read_text(encoding='utf-8'))
row = [c for c in db['WINBOND'] if c['part_number'].startswith('W29C020')][0]
p = row['programming']
assert p['algorithm'] == 5 and p['page_size'] == 128 and row['electrical']['size_bytes'] == 262144
print('BENCH-TARGET-OK part=' + row['part_number'] + ' page=128 size=262144 chip_id=' + str(p.get('chip_id_value')))
"
```

```
BENCH-TARGET-OK part=W29C020,W29C020C,W29C022 page=128 size=262144 chip_id=0x0000da45
```

The seated part is confirmed by chip-ID, not by its printed marking. `W29C020` belongs to
none of the three-way 512-designation collision named in D-10 — that hazard applies to the
`W29C512` family this run does not touch.

### 4b. Test pattern — generation rule and size

**Size:** 2048 bytes = 16 physical pages of 128 bytes each (`W29C020`'s real page size,
per §4a's database read).

**Generation rule:** for byte index `i` (0-based) in the output file,
`byte[i] = ((i // 128) * 17 + (i % 128)) & 0xFF`. The `(i % 128)` term varies the value
within every 128-byte page. The `(i // 128) * 17` term differs between every pair of
adjacent pages. A page-boundary landed at the wrong offset (the exact defect class this
phase's fix addresses) would show up as a run of unexpected — typically erased, `0xFF` —
bytes at a regular interval, because the pattern does not repeat across a page boundary.

**Command generating the file:**

```
python3 -c "
page_size = 128
n_pages = 16
data = bytearray()
for page in range(n_pages):
    for offset in range(page_size):
        data.append((page * 17 + offset) & 0xFF)
open('w29c020_pattern.bin', 'wb').write(bytes(data))
"
sha256sum w29c020_pattern.bin
```

```
d7a3b21b5e1adb089bbe05215990f7a85c0062545a07c84236d711eb82cd5070  w29c020_pattern.bin
```

### 4c. The write

**Command:** `firestarter --port /dev/ttyACM0 write W29C020 w29c020_pattern.bin`

No `-b`/`--no-blank-check` flag was passed, and no `--skip-erase` flag was passed. Per this
project's own bench rules and the app's own `write --help` text, this project's hard rule is
never to pass the blank-check-skip flag on this path, because on some firmware/protocol
combinations that flag has skipped the pre-write erase and corrupted a non-blank chip while
still reporting success. A plain write was run instead, letting the pre-write erase run
unconditionally.

```
Writing w29c020_pattern.bin to W29C020
  0x0000/0x0800 bytes ... 100%|██████████| 0x0800/0x0800 bytes
Write to W29C020 successful (0.37s).
```

Wall-clock elapsed (measured with `time`): 4.092s total (includes process startup and
connection handshake. The reported in-band write duration is 0.37s).

### 4d. The read-back comparison

**Command:** `firestarter --port /dev/ttyACM0 read W29C020 w29c020_readback.bin -s 2048`

```
Reading EPROM W29C020, saving to w29c020_readback.bin
  0x0000/0x0800 bytes ... 100%|██████████| 0x0800/0x0800 bytes
Read complete (0.36s).
```

**Command comparing the two files:** `cmp w29c020_pattern.bin w29c020_readback.bin`

Result: **no output — the files are byte-identical.** Confirmed independently by hash:

```
sha256sum w29c020_pattern.bin w29c020_readback.bin
d7a3b21b5e1adb089bbe05215990f7a85c0062545a07c84236d711eb82cd5070  w29c020_pattern.bin
d7a3b21b5e1adb089bbe05215990f7a85c0062545a07c84236d711eb82cd5070  w29c020_readback.bin
```

Both hashes match. No mismatched range exists to report.

**Additional corroboration (not required by the plan, run because it was available at no
extra risk to the part):** `firestarter --port /dev/ttyACM0 verify W29C020 w29c020_pattern.bin`
→ `Verify for W29C020 successful (0.31s).`, using the app's own independent verify path
rather than a second host-side diff of the same two files.

### 4e. Negative control — recorded as skipped, with the reason

The plan makes this control optional and names the exact condition under which it should be
skipped: "If no such route exists without editing the shipped database, skip it and say so,
because the host guard in plan 05 already refuses before any serial byte and the database no
longer contains such a row."

**Command checked before skipping:**

```
cd firestarter_app && python3 -c "
import json, pathlib
db = json.loads(pathlib.Path('firestarter/data/chip_database.json').read_text(encoding='utf-8'))
missing = []
count5 = 0
for vendor, rows in db.items():
    if not isinstance(rows, list):
        continue
    for row in rows:
        p = row.get('programming', {})
        if p.get('algorithm') == 5:
            count5 += 1
            if 'page_size' not in p:
                missing.append(row['part_number'])
print('alg5 rows:', count5, 'missing page_size:', missing)
"
```

```
alg5 rows: 27 missing page_size: []
```

All 27 `algorithm: 5` rows in the shipped, regenerated database carry `page_size`. No
supported route exists to drive a protocol `0x05` write against a chip carrying no page size
without editing the shipped database, which this plan prohibits. **Skipped, per the plan's
own named condition.** The refusal path itself is already proven natively (four rejected
classes plus one positive control, `194-02`), and the host-side guard (`page_size_gate.py`,
`194-05`) refuses before any serial byte is sent whenever the resolved database row carries
no page size — a condition that no longer exists in the shipped database for protocol `0x05`.

---

## 5. What this transcript proves, and what it does not

**This run proves no regression.** `W29C020` is one of the **18** protocol `0x05` parts
whose old capacity-derived page size was already correct (`.planning/v1.39/194-page-size-27-row-record.md`,
row 24: `WINBOND | W29C020,W29C020C,W29C022 | 262144 | 128 | 128 | equal (already correct
pre-Phase-194)`). It is also the exact part both reported defects (gh#67, gh#68) were
originally reproduced on. A contiguous, multi-page, chip-ID-confirmed write on this part,
with this phase's firmware and host, read back byte-identical. That is a genuine
before-and-after no-regression proof on the part the original defects came from.

**This run proves nothing about the 9 previously under-sized parts.** None of the 9 named
parts below was on the rig for this run:

1. `AT29BV020,AT29LV020`
2. `AT29BV040,AT29LV040`
3. `AT29C020`
4. `AT29C040`
5. `AT29C512`
6. `AT29LV512`
7. `SST29EE512`
8. `SST29LE512,SST29VE512`
9. `W29C512,W29EE512`

This run is **structurally incapable** of proving any of the 9 were fixed, because
`W29C020`'s derived page size was never wrong. A reader who takes this transcript as
evidence for the 9 has been misled by the transcript rather than by their own reading — this
section exists to foreclose that reading. Per D-10, the ordered `W29C512` (one of the 9) has
not yet arrived. PAGE-03's hardware leg for the 9 stays at **0 of 9 on hardware** after this
run, unchanged from `194-page-size-27-row-record.md` §2. Only the no-regression half of the
picture moved.

---
*Phase: 194-real-page-size-reaches-the-firmware*
*Transcript measured and committed: 2026-09-15*
