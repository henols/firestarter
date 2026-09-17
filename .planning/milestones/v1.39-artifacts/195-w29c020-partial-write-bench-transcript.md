---
title: W29C020 partial-write bench transcript — protocol 0x05, milestone v1.39 Phase 195
phase: 195-partial-writes-stop-destroying-the-page
plan: "05"
measured: 2026-09-16
status: AUTHORITATIVE — the silicon evidence for WRITE-01, WRITE-02 and WRITE-03 on one protocol 0x05
  part. Not authoritative for the two 512-byte-page parts (no silicon evidence exists for either), not
  authoritative for any other protocol, and not authoritative for SST39SF020 (algorithm 6, never
  traverses this write path — see §5). See §5 for the full scope statement.
pairs_with: .planning/v1.39/195-partial-write-refusal-record.md
requirements: [WRITE-01, WRITE-02, WRITE-03]
---

# W29C020 partial-write bench transcript — Phase 195 Plan 05

Every figure below carries the verbatim command that produced it. Nothing here is carried
forward from research or from another plan without a citation.

---

## 1. The rig, as the operator described it

The operator supplied all four answers task 1 asked for, before any operation ran:

1. **Seated part:** a `W29C020` was placed in the socket. (Operator-confirmed.)
2. **Shield revision:** **Rev 2.0 (operator-stated)**. The reported `hw` value cannot distinguish
   the three shields the operator owns, so this project's rule is that the revision is asked, never
   inferred or probed. It is recorded here as an operator statement, not as a measurement.
3. **Serial port:** `/dev/ttyACM0`, confirmed by the operator.
4. **Destructive write permitted:** the operator confirmed the seated part may be written
   destructively — nothing on it was needed. The reproduction leg exists specifically to erase bytes
   it was not asked to touch.

Orchestrator probes taken before this dispatch corroborated but did not establish these facts:
`/dev/ttyACM0` was the only serial device present, `firestarter -p /dev/ttyACM0 fw` reported
firmware `3.0.0b31` for controller `leonardo`, and `firestarter -p /dev/ttyACM0 hw` reported
`Rev 2.0-class` (a value that cannot distinguish the operator's three shields). No operation had run
against the socket before this plan began.

---

## 2. Rig identity, re-confirmed (not merely trusted)

**Command:** `ls -la /dev/ttyACM*` — exactly one serial device present: `/dev/ttyACM0`.

**Command:** walking the USB sysfs descriptor tree for that device
(`readlink -f /sys/class/tty/ttyACM0/device`, then `cat idVendor idProduct manufacturer product` on
the resolved USB device directory,
`/sys/devices/pci0000:00/0000:00:14.0/usb3/3-3/3-3.1/3-3.1.2/3-3.1.2.2`):

```
idVendor: 2341
idProduct: 8036
manufacturer: Arduino LLC
product: Arduino Leonardo
```

This is a **Leonardo**, not an Uno-class board — matching the operator's statement and the previous
phase's rig at the identical physical USB path. Per this project's chip-out-before-sideload rule, the
chip-removal requirement applies to Uno-class boards only; a Leonardo is exempt, so the `W29C020`
stayed seated across both firmware flashes in §3.

**Command (pre-revert baseline):** `firestarter --port /dev/ttyACM0 fw` —
`Current firmware version: 3.0.0b31, for controller: leonardo on port /dev/ttyACM0` — confirms the
controller identity on the operator's named port before any operation ran.

**Command confirming which `firestarter` package resolves:**
`/workspaces/firestarter_app/.venv311/bin/python3 -c "import firestarter; print(firestarter.__file__)"`
→ `/workspaces/firestarter_app/firestarter/__init__.py` — the editable install under the working
tree being reverted, not a relocated or stale checkout. Host version:
`/workspaces/firestarter_app/.venv311/bin/firestarter --version` → `Firestarter, version 3.0.0b44`.
All commands in this transcript used this exact binary.

**Port re-identification after each flash** (device numbers shuffle across a replug — the Leonardo
bootloader touch causes exactly this): after both the pre-fix flash (§3) and the post-fix flash (§3),
the board re-enumerated at the same physical USB path,
`/sys/devices/pci0000:00/0000:00:14.0/usb3/3-3/3-3.1/3-3.1.2/3-3.1.2.2`, and in both cases retained the
node `/dev/ttyACM0` — confirming the same physical board under (in this run) an unchanged node
assignment, not a different board. Every operation in §4 targeted `/dev/ttyACM0`, re-checked after
each flash.

---

## 3. Firmware built and flashed — recorded twice, once per build

### 3a. Pre-fix build (the reproduction leg)

**Scoped revert.** Baseline `git status --porcelain` immediately before the revert:
`firestarter_fw` empty; `firestarter_app` carried only three pre-existing untracked datasheet PDFs
(`datasheets/LST62832I.pdf`, `datasheets/MBM27128.pdf`, `datasheets/MBM27C4001.pdf`) unrelated to
this plan and left untouched throughout.

**Command:** `git -C firestarter_fw checkout c2b8baa -- src/proms/flash_5v_page.cpp`

**Command:** `git -C firestarter_app checkout 3140172 -- firestarter/page_size_gate.py firestarter/exceptions.py firestarter/cli_handlers.py firestarter/eprom_operations.py`

`git status --porcelain` immediately after the revert:

```
firestarter_fw:
 M src/proms/flash_5v_page.cpp

firestarter_app:
 M firestarter/cli_handlers.py
 M firestarter/eprom_operations.py
 M firestarter/exceptions.py
 M firestarter/page_size_gate.py
?? datasheets/LST62832I.pdf
?? datasheets/MBM27128.pdf
?? datasheets/MBM27C4001.pdf
```

The four host files were reverted together (not `page_size_gate.py` alone) because
`eprom_operations.py` and `cli_handlers.py` call `require_page_alignment`, which the pre-195 blob of
`page_size_gate.py` does not define — reverting one without the others would raise `AttributeError`
at the call site rather than reproduce pre-195 behaviour. Confirmed clean import after the revert:
`python3 -c "import firestarter; import firestarter.cli_handlers; import firestarter.eprom_operations; import firestarter.page_size_gate; print('IMPORT-OK')"` → `IMPORT-OK`. The generated message
artefacts (`include/messages.h`, `firestarter/messages.py`) were deliberately **not** reverted — an
extra unused message id costs nothing on either side.

Both pre-195 tips: firmware `c2b8baa` ("docs: cite memory.cpp repo-relative, not through the old
submodule name"), host `3140172` ("docs: point the firmware header paths at firestarter_fw").

**Command:** `cd firestarter_fw && pio run -e leonardo`

```
bootloader-guard: leonardo 23734/28672 B (82.8% of the safe ceiling, 4938 B margin, 4096 B bootloader reserved)
```

Byte-identical to the figure `.planning/v1.39/194-w29c020-bench-transcript.md` §3 recorded for the
same environment on the same pre-195 source — confirming this is a genuine from-source build of the
pre-fix blob, not a stale artifact.

**Command:** `pio run -t upload -e leonardo --upload-port /dev/ttyACM0` →
`avrdude: 23734 bytes of flash written` / `avrdude: 23734 bytes of flash verified` / `[SUCCESS]`.

**Post-flash confirmation:** `firestarter --port /dev/ttyACM0 fw` →
`Current firmware version: 3.0.0b31, for controller: leonardo on port /dev/ttyACM0` (the version
string is unchanged — this phase's plans never call for a version bump; the build is attributed by
the byte-identical flash-size figure above, not by the version string).

**Restoration (end of the reproduction leg).** `git -C firestarter_fw checkout HEAD -- src/proms/flash_5v_page.cpp` and `git -C firestarter_app checkout HEAD -- firestarter/page_size_gate.py firestarter/exceptions.py firestarter/cli_handlers.py firestarter/eprom_operations.py`. `git status --porcelain` afterward:

```
firestarter_fw: (empty)

firestarter_app:
?? datasheets/LST62832I.pdf
?? datasheets/MBM27128.pdf
?? datasheets/MBM27C4001.pdf
```

Identical to the pre-revert baseline captured above — zero tracked-file drift. `git diff --stat HEAD`
in both sub-repos reports no output. The three untracked datasheet PDFs are pre-existing, unrelated
project noise (present before this plan began and after it ended) and were never staged, modified, or
deleted, per this project's standing instruction to leave them alone.

### 3b. Post-fix build

**Command:** `cd firestarter_fw && pio run -e leonardo` (from the restored, committed tree)

```
bootloader-guard: leonardo 23798/28672 B (83.0% of the safe ceiling, 4874 B margin, 4096 B bootloader reserved)
```

+64 bytes over the pre-fix build (23734 → 23798 B) — matching `195-01-SUMMARY.md`'s recorded flash
delta for the `leonardo` environment exactly. This is the attribution evidence that the two builds in
this transcript really are different firmware.

**Command:** `pio run -t upload -e leonardo --upload-port /dev/ttyACM0` →
`avrdude: 23798 bytes of flash written` / `avrdude: 23798 bytes of flash verified` / `[SUCCESS]`.

**Post-flash confirmation:** `firestarter --port /dev/ttyACM0 fw` →
`Current firmware version: 3.0.0b31, for controller: leonardo on port /dev/ttyACM0` (version string
unchanged, same reasoning as §3a). Host version under test throughout:
`firestarter --version` → `Firestarter, version 3.0.0b44`.

---

## 4. The measurements

### 4a. Chip-ID confirmation for each build (never the printed marking)

**Command (pre-fix build):** `firestarter -v --port /dev/ttyACM0 id W29C020` →
`INFO: Chip ID check passed for W29C020: (main done) (0.03s)`, chip id `55877` (`0x0000da45`) sent as
part of `CHECK_CHIP_ID`.

**Command (post-fix build):** `firestarter -v --port /dev/ttyACM0 id W29C020` →
`INFO: Chip ID check passed for W29C020: (main done) (0.03s)`.

**Command confirming the expected database value independently:**

```
python3 -c "
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

The seated part is confirmed by chip-ID both times, not by its printed marking.

### 4b. Pattern rule and sizes used

Reusing `194-w29c020-bench-transcript.md`'s generation rule, designed to expose a misplaced page
boundary: for byte index `i` (0-based), `byte[i] = ((i // 128) * 17 + (i % 128)) & 0xFF`. Two sizes
were used: 512 bytes (4 pages) for the leading/trailing probes, and 2048 bytes (16 pages) for the
interior probe and the no-regression case.

`sha256sum` of the 512-byte pattern: `0c4bed3c7fed8f6b1d5a4a21010af4750eeec3064a2cfa57fedf6db39232031a`.
`sha256sum` of the 2048-byte pattern: `d7a3b21b5e1adb089bbe05215990f7a85c0062545a07c84236d711eb82cd5070`
— identical to `194-w29c020-bench-transcript.md` §4b's hash for the same generation rule and size, an
independent cross-check that both transcripts generated the same bytes.

### 4c. Baseline write and read-back hashes (pre-fix build)

**Command:** `firestarter --port /dev/ttyACM0 write W29C020 baseline512.bin` →
`Write to W29C020 successful (0.12s).`

**Command:** `firestarter --port /dev/ttyACM0 read W29C020 baseline512_readback.bin -s 512` →
`Read complete (0.12s).`

`sha256sum` of both files: `0c4bed3c7fed8f6b1d5a4a21010af4750eeec3064a2cfa57fedf6db39232031a` (both) —
identical. The rig and the part are good before any probe ran.

### 4d. Pre-fix trailing-loss probe (step B)

**Command:** `firestarter --port /dev/ttyACM0 write W29C020 probe_trailing_64.bin` (64 bytes of
`0x55`, no address) →

```
Writing probe_trailing_64.bin to W29C020
  0%|          | 0x0000/0x0040 bytes 100%|██████████| 0x0040/0x0040 bytes
Write to W29C020 successful (0.05s).
```

**Host outcome line: printed** (`Write to W29C020 successful`), exit code 0.

**Command:** `firestarter --port /dev/ttyACM0 read W29C020 readback_trailing.bin -s 512`

Exact ranges observed:

- `0x000`–`0x03F`: all `0x55` (the new content — matches the probe file exactly)
- `0x040`–`0x07F`: all `0xFF` (erased, though the baseline pattern had held this range) — **the
  trailing loss direction**
- `0x080`–`0x1FF`: unchanged, byte-identical to the baseline pattern

### 4e. Pre-fix leading-loss probe (step C)

Baseline re-applied (`write W29C020 baseline512.bin`, read-back hash re-confirmed identical to
`0c4bed3c…`) before this probe.

**Command:** `firestarter --port /dev/ttyACM0 write W29C020 probe_leading_64.bin -a 0x40` (64 bytes of
`0x66`) →

```
Writing probe_leading_64.bin to W29C020
  0%|          | 0x0000/0x0040 bytes 100%|██████████| 0x0040/0x0040 bytes
Write to W29C020 successful (0.04s).
```

**Host outcome line: printed**, exit code 0.

**Command:** `firestarter --port /dev/ttyACM0 read W29C020 readback_leading.bin -s 512`

Exact ranges observed:

- `0x000`–`0x03F`: all `0xFF` (erased **before** the start address the operator gave, though the
  baseline pattern had held this range) — **the leading loss direction**
- `0x040`–`0x07F`: all `0x66` (the new content — matches the probe file exactly)
- `0x080`–`0x1FF`: unchanged, byte-identical to the baseline pattern

### 4f. Blast-radius confirmation

In both 4d and 4e, pages at `0x080` and beyond read back byte-identical to the baseline pattern. The
damage in both directions is confined to the single 128-byte page the unaligned boundary touched,
which independently re-confirms the part's real page size (128 bytes).

### 4g. Interior direction (D-06) — attempted, with a corrected payload size, positive result

The plan's literal step size (a 1024-byte payload at `0x40` against a 2048-byte baseline) was tried
first: `firestarter -v --port /dev/ttyACM0 write W29C020 probe_interior_1024.bin -a 0x40` produced
exactly **one** `Request data` cycle in the verbose transcript — the Leonardo's 1024-byte transfer
buffer accepted the entire 1024-byte payload in a single chunk, so no second chunk ever re-opened a
shared page. The read-back showed only the already-characterized leading loss (`0x000`–`0x03F` → `0xFF`)
and trailing loss (`0x440`–`0x47F` → `0xFF`) on that one chunk — **not** the interior mechanism, which
requires a payload strictly larger than the chunk size (`L > C`, per `195-RESEARCH.md` §1c). This is
recorded as a deviation from the plan's literal instruction (Rule 1 — the literal size cannot exercise
its own stated goal on this rig's buffer size), not as "not attempted."

**Corrected probe:** a 2048-byte payload at `0x40` against the same 2048-byte baseline, which is
strictly larger than the Leonardo's 1024-byte chunk and so must cross a chunk boundary.

**Command:** `firestarter -v --port /dev/ttyACM0 write W29C020 probe_interior_2048.bin -a 0x40` —
3 `Request data` cycles observed (multi-chunk transfer confirmed) →
`Write to W29C020 successful (0.38s).` **Host outcome line: printed**, exit code 0.

**Command:** `firestarter --port /dev/ttyACM0 read W29C020 readback_interior_wide.bin -s 2176`
(a wider window than the 2048-byte request, to also capture the tail past the write's end address).

**Result — a genuine, previously-unobserved interior loss:**

- `0x400`–`0x43F` (the first half of page 8, `0x400`–`0x47F`): reads back all `0xFF`, even though
  this range is **strictly inside** the requested write (`0x40` to `0x83F`) and had been legitimately
  loaded by the first 1024-byte chunk. Expected content (from the probe file) was
  `595a5b…97 98` (hex) — entirely erased.
- `0x440`–`0x47F` (the second half of the same page): holds the second chunk's data
  (`999a9b…d7 d8` hex), matching the probe file exactly at that offset.
- Every other page strictly between the start and end of the write (`0x080`–`0x3FF` and
  `0x480`–`0x7FF`) matched the probe file exactly — the interior loss is confined to the single page
  straddled by the chunk boundary, consistent with the mechanism `195-RESEARCH.md` §1c predicts.
- Page 0 (`0x000`–`0x07F`) showed the expected leading loss (`0x000`–`0x03F` → `0xFF`) and the page
  beyond the write's end (`0x800`–`0x87F`) showed the expected trailing loss (`0x840`–`0x87F` → `0xFF`)
  — both already characterized in 4d/4e, not new findings.

This is the first silicon observation of direction 3 (interior chunk-boundary loss) named in
`195-RESEARCH.md` §1c and `195-partial-write-refusal-record.md` §2 — previously derived from source
and the datasheet only, never run. It demonstrates that a page fully inside the requested write range
can be destroyed by a chunk boundary the operator never asked about, and that the host still reported
success over it.

### 4h. Post-fix repeats — refusal, exit codes, and the device-unchanged proof

Post-fix baseline established first: `write W29C020 baseline512.bin` → `Write to W29C020 successful
(0.12s).`; read-back hash `0c4bed3c7fed8f6b1d5a4a21010af4750eeec3064a2cfa57fedf6db39232031a`,
identical to the pattern file.

**Command (repeat of step B):** `firestarter --port /dev/ttyACM0 write W29C020 probe_trailing_64.bin` →

```
Error: W29C020: write refused -- page size is 128 bytes, start address is 0x0, and payload length is 64 bytes. Both the start address and the length must be a whole multiple of the page size, because a partial page write erases every byte of the touched page that was not sent.
```

Exit code: **1**. No success line printed. No `Connecting...` line preceded the error — the refusal
fired before the serial port opened, i.e. this is the **host** layer's message, not the firmware's.

**Command (repeat of step C):** `firestarter --port /dev/ttyACM0 write W29C020 probe_leading_64.bin -a 0x40` →

```
Error: W29C020: write refused -- page size is 128 bytes, start address is 0x40, and payload length is 64 bytes. Both the start address and the length must be a whole multiple of the page size, because a partial page write erases every byte of the touched page that was not sent.
```

Exit code: **1**. No success line. Host-layer refusal, same reasoning.

**Device-unchanged proof:** `firestarter --port /dev/ttyACM0 read W29C020 postfix_afterrefusals_readback.bin -s 512` →
`sha256sum` `0c4bed3c7fed8f6b1d5a4a21010af4750eeec3064a2cfa57fedf6db39232031a` — **identical** to the
post-fix baseline hash recorded moments earlier. A refusal that still touched the device would show
here and nowhere else; it does not.

**Interior repeat (step E, since it was attempted in §4g):** post-fix 2048-byte baseline established
(`write W29C020 baseline2048.bin` → success; read-back hash
`d7a3b21b5e1adb089bbe05215990f7a85c0062545a07c84236d711eb82cd5070`, identical to the pattern).

**Command:** `firestarter --port /dev/ttyACM0 write W29C020 probe_interior_2048.bin -a 0x40` →

```
Error: W29C020: write refused -- page size is 128 bytes, start address is 0x40, and payload length is 2048 bytes. Both the start address and the length must be a whole multiple of the page size, because a partial page write erases every byte of the touched page that was not sent.
```

Exit code: **1**. No success line. Read-back (`-s 2048`) hashed
`d7a3b21b5e1adb089bbe05215990f7a85c0062545a07c84236d711eb82cd5070` — identical to the post-fix
2048-byte baseline. The device is unchanged after this refusal too.

**Layer attribution (step 9):** all three post-fix refusals were produced by the host pre-connect
predicate (`page_size_gate.require_page_alignment`) — none of the three CLI invocations printed a
`Connecting...` line before the error, meaning the serial port never opened. The firmware's own
per-chunk guard is reachable only when the host predicate is bypassed; its evidence is the native
suite (`195-01-SUMMARY.md`, `195-02-SUMMARY.md`), not this bench run. This transcript does not present
the host refusal as evidence that the firmware guard works, or the reverse.

### 4i. Aligned no-regression write

**Command:** `firestarter --port /dev/ttyACM0 write W29C020 baseline2048.bin` (2048 bytes, 16 pages of
128 bytes, address 0 — the same case `194-w29c020-bench-transcript.md` §4 recorded on this rig) →

```
Writing baseline2048.bin to W29C020
  0%|          | 0x0000/0x0800 bytes 100%|██████████| 0x0800/0x0800 bytes 100%|██████████| 0x0800/0x0800 bytes
Write to W29C020 successful (0.37s).
```

**Command:** `firestarter --port /dev/ttyACM0 read W29C020 noregression_readback.bin -s 2048` →
`sha256sum` `d7a3b21b5e1adb089bbe05215990f7a85c0062545a07c84236d711eb82cd5070` (both files) — identical.
The fix did not cost the aligned, multi-page case that works today.

---

## 5. What this transcript proves, and what it does not

**This run proves both loss directions named by WRITE-03**, on `W29C020` — the exact part both
originating defects (gh#67, gh#68) were reproduced on, and one of the 18 protocol `0x05` parts whose
derived page size was already correct before Phase 194, which isolates this result from PAGE-01/PAGE-02.
Both the leading and trailing directions were captured against a pre-fix build of this same tree (§4d,
§4e), with the host's own success line recorded beside each (§4d, §4e) — the WRITE-02 half of the
evidence. With the fix in place, the identical commands refuse, exit non-zero, print no success line,
and a full read-back is byte-identical to the baseline (§4h) — the WRITE-01 refusal branch, with the
device-unchanged half proved by hash rather than asserted. The aligned, multi-page case still succeeds
and reads back byte-identical (§4i), so the fix did not break the case that works today. The third,
derived loss direction (interior chunk-boundary loss, D-06) was also attempted and, with a payload
size corrected to actually cross a chunk boundary, was observed on silicon for the first time (§4g),
and its post-fix repeat also refuses with the device unchanged (§4h).

**This run proves nothing about the two parts whose recorded page size is 512**
(`AT29BV040,AT29LV040` and `AT29C040`) — neither has ever been on this or any rig, and no silicon
evidence exists for either. It proves nothing about any protocol other than `0x05`. And per the scope
correction recorded in `195-partial-write-refusal-record.md` §5, it says nothing about `SST39SF020`,
the sector-erase NOR part the ROADMAP's fourth criterion also names — that part is algorithm 6
(`PROTO_FLASH_NOR_UNLOCK`), never traverses `flash_5v_page.cpp`, and cannot regress from this phase's
change at all.

A reader who takes this transcript as evidence for the two 512-byte-page parts, for any protocol other
than `0x05`, or for `SST39SF020`, has been misled by the transcript rather than by their own reading —
this section exists to foreclose that reading.

---
*Phase: 195-partial-writes-stop-destroying-the-page*
*Transcript measured and committed: 2026-09-16*
