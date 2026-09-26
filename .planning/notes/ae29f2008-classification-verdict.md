---
title: AE29F2008 classification verdict — algorithm 5 is correct, and gh#62 is correct too
date: 2026-09-11
context: v1.37 Phase 183, SAFE-09 — re-verified in this session against 183-RESEARCH.md §B
---

# AE29F2008 classification verdict (SAFE-09)

## THE VERDICT

**AE29F2008 is classified `algorithm 5` CORRECTLY. gh#62's reporter is ALSO correct that the chip
can be chip-erased. Both are true at once: the `0x05` firmware path simply does not implement the
chip-erase this silicon supports.**

**This verdict is equivalence-based, not a direct datasheet reading.** No primary AE29F2008
datasheet was retrieved or read — none is retrievable; ASD is a re-badge vendor and no
AE29F2008-branded datasheet surfaces from any search this project ran. The conclusion instead
rests on two things, checked independently in this session: (1) an upstream-declared identity
between the `AE29F2008` row and the `W29C020,W29C020C,W29C022` row inside the pinned
`infoic.xml`, and (2) the W29C020C datasheet, which is retrievable, read against every field the
DB derives from that upstream row. If a future reader wants a direct AE29F2008 vendor-datasheet
confirmation, this record is not that — it is the best evidence this project could obtain, and it
says so plainly.

## THE EVIDENCE CHAIN

Three legs, each re-verified in this session (commands and outputs below), matching
`183-RESEARCH.md` §B on every fact and every citation.

**Leg (a) — the classification is an upstream transcription, not a generator decision.** The
pinned upstream `infoic.xml` at commit `a8efaedc236c1d9718bd28299dfbb99536b010ff` (pinned by
`MINIPRO_XML_URL` in `firestarter_app/tools/build_db.py`) carries ASD's `AE29F2008@DIP32` record
with `protocol_id="0x05"` directly on the XML element. `build_db.py`'s `classify()` function has a
flash-family branch, re-verified this session:

```
$ cd /workspaces/firestarter_app && /usr/bin/grep -n '0x05, 0x06, 0x0D, 0x10' tools/build_db.py
356:    if proto_id in {0x05, 0x06, 0x0D, 0x10}:
```

— which returns `proto_id` **unchanged** for the flash-family set `{0x05, 0x06, 0x0D, 0x10}`
(`build_db.py:355-357`, "# 4. Flash families." / `return "Flash/EEPROM", proto_id, pinout_key`).
There is no decode step between upstream's `protocol_id="0x05"` and the DB's `algorithm: 5` — the
value is carried through unmodified. `algorithm: 5` is therefore an upstream transcription, and
there is nothing in `build_db.py` for a correction to land in.

**Leg (b) — upstream's own database declares AE29F2008 and W29C020C the same die.** The two rows
were extracted from `chip_database.json` and compared in this session, not merely re-cited from
RESEARCH.md:

```
$ cd /workspaces/firestarter_app && .venv311/bin/python -c "..."
AE29F2008: {"algorithm": 5, "chip_id_value": "0x0000da45", "size_bytes": 262144,
            "infoic_page_size_raw": 128, "pinout": "DIP32_SST39SF040", "support_status": "supported"}
W29C020,W29C020C,W29C022: {"algorithm": 5, "chip_id_value": "0x0000da45", "size_bytes": 262144,
            "infoic_page_size_raw": 128, "pinout": "DIP32_SST39SF040", "support_status": "supported"}
```

Both rows agree on `algorithm` (5), `chip_id_value` (`0x0000da45`), `size_bytes` (262144),
`infoic_page_size_raw` (128), and `pinout` (`DIP32_SST39SF040`). `AE29F2008`'s `support_status`
was confirmed to read `supported` before any other action in this session, and no edit was made to
it (D-22 — see below). RESEARCH.md §B.3 independently derived the same identity directly from the
upstream `infoic.xml` XML elements (ASD's block at pinned-file lines 17642-17662, WINBOND's block
at lines 228452-228471), reporting all thirteen decode-relevant XML attributes — not just the five
that survive into the JSON — as byte-identical between the two rows, including the shared
`chip_id="0x0000da45"`. Upstream's own database, not this project's inference, treats the two part
numbers as the same silicon.

**Leg (c) — the W29C020C datasheet independently confirms every DB field.** RESEARCH.md §B.4
fetched the Winbond W29C020C datasheet (octopart PDF, converted to text with `pdftotext`, 3,619
lines) and quoted it verbatim. It confirms: 256K x 8 organization ("256K × 8 CMOS FLASH MEMORY"),
5 V-only operation with no external VPP ("VPP is not required."), 128-byte page write (matching
`infoic_page_size_raw: 128`), a 50 ms fast chip-erase, and manufacturer code `DA` / device code
`45` (matching `chip_id_value: 0x0000da45`). Every field the DB carries for this row has an
independent datasheet confirmation, not just an upstream cross-reference.

## WHY THE REPORTER'S `--force` ERASE WORKED, AND WHY THAT IS NOT A LICENCE

**(Material for Phase 187's REPLY-03, per D-09.)**

gh#62's reporter ran `firestarter erase SST39SF020 --force` against a real AE29F2008 part and
reported success in 0.14 s, followed by a clean `blank` scan. `SST39SF020,SST39SF020A` is
`algorithm 6` in the DB (chip_id_value `0x0000bfb6`, same pinout `DIP32_SST39SF040`) — which is
why the reporter's own `WARN: Chip ID 0xda45 does not match expected ID 0xbfb6` line names both
chip IDs. Driving `erase` under that identity dispatches to `flash_nor_unlock_erase_execute`
(`firestarter/src/proms/flash_nor_unlock.cpp:121-129`), which for a zero address calls
`flash_execute_command(FLASH_ERASE)`. Re-verified this session:

```
$ cd /workspaces/firestarter && /usr/bin/grep -n '0x5555, 0x10' include/flash_utils.h
40:        {0x5555, 0x10},
```

`FLASH_ERASE` (`include/flash_utils.h:34-41`) is the six-cycle sequence
`{0x5555,0xAA} {0x2AAA,0x55} {0x5555,0x80} {0x5555,0xAA} {0x2AAA,0x55} {0x5555,0x10}` — cycle for
cycle identical to the W29C020C datasheet's own "Command Codes for Software Chip Erase" table. The
reporter's erase was real: it used the exact byte sequence this silicon documents as its software
chip-erase, and the 50 ms internal erase plus serial round-trips is consistent with the observed
0.14 s.

**Why it was electrically benign here — and why that is a coincidence, not a property of
`--force`.** Both identities (`SST39SF020` under `algorithm 6`, `AE29F2008` under `algorithm 5`)
sit on the same pinout `DIP32_SST39SF040` and the same `size_bytes` 262144, so the bus config was
identical when misdeclared; and `configure_flash_nor_unlock`'s `CMD_ERASE` arm energises no VPP
rail (pinned by `test_val_nor_unlock.cpp:151`: "configure_flash_nor_unlock CMD_ERASE must NOT set
any VPP-enable CTL bit"). **This benignity is a coincidence of this particular chip pair sharing a
pinout and a voltage class — it is not a property of `--force` in general.** Forging a different
identity onto a different real part could route a genuinely mismatched bus config or energize a
rail the target part does not expect. REPLY-03 should carry this paragraph verbatim: the erase
worked because the reporter accidentally chose an identity whose command sequence this silicon
happens to document as its own, not because `--force` is safe to use for identity forgery in
general.

## D-23, SETTLED — NOT A HARDWARE-LIVE DEFECT ON ALGORITHM 5

The row's `"vpp_mv": 12000` looks wrong on a part the datasheet calls 5 V-only ("VPP is not
required."). Traced end to end and re-verified in this session:

1. **Origin.** `voltages="0x0000"` upstream decodes via `VPP_MV[0x00] = 12000`
   (`build_db.py:70-72`), keyed on `(voltages & 0xF0)` per the minipro/tl866 VPP-voltage table
   cited in that file. This is a faithful decode of an upstream field — the generator invents
   nothing here.
2. **Wire.** `convert_to_programmer` emits `vpp_mv` unconditionally into the wire dict
   (`database.py:527`, `:534`).
3. **Firmware field.** It lands in `firestarter_handle_t.vpp_mv` (`firestarter.h:178`), a live
   parsed field.
4. **Firmware consumers — the decisive step, re-verified this session:**

   ```
   $ cd /workspaces/firestarter && /usr/bin/grep -n 'vpp_mv' src/proms/flash_5v_page.cpp
   $ echo "exit=$?"
   exit=1
   ```

   `/usr/bin/grep` (not the devcontainer's default `grep`, which is ugrep and honours
   `.gitignore` and would silently under-scan) was used deliberately, and it finds **no reader**
   of `vpp_mv` anywhere in `flash_5v_page.cpp`. `vpp_mv` is read in exactly two other files —
   `eprom.cpp` (protocols 0x07/0x08/0x0B) and `flash_intel.cpp` (protocol 0x10) — neither of which
   handles algorithm 5. On algorithm 5, the field drives no comparison, no register write, and no
   rail.
5. **Host live check.** `check_dispatch.py` excludes `configure_flash_5v_page` from the one
   DB-level VPP invariant check, deliberately and by name, re-verified this session:

   ```
   85:    "configure_flash_5v_page": (0, 6000),  # AMD/SST flash 5V only (WP-pin 12V exempt)
   ...
   90-96: # VPP-INVARIANT ENFORCEMENT SCOPE: ... For 5V-only handlers, the DB's
          # electrical.vpp_mv encodes WP-pin voltage (not programming VPP), so
          # checking vpp_mv > 6000 would produce false positives on every AMD/SST
          # flash chip. ...
          _DB_CHECKED_VPP_INVARIANTS: frozenset[str] = frozenset({"configure_flash_intel"})
   ```

   The project already records exactly this reading: the 12 V referent on this silicon is the
   datasheet's `VHH = 12V`, used for the A9-based hardware product-ID read and hardware
   data-protection modes — not a programming VPP.

**D-23 verdict: the `[WARNING: new finding]` branch does NOT fire.** The field is not live as a
hardware check, a register write, or a `dev test` assertion on algorithm 5. It is a faithful
decode of an upstream field with a real (non-programming) physical referent on this silicon.

**The residual is filed, not fixed here.** `firestarter info`'s display path (`eprom_info.py:396`
and `ic_layout.py:573`) calls the field "VPP" with no equivalent of `check_dispatch.py`'s WP-pin
carve-out, so 301 rows across three 5 V-only families print an elevated VPP that is not a
programming voltage. This is a pre-existing, cross-family labelling question — not an AE29F2008
defect, and not a `build_db.py` correction, since the decode itself is correct. Filed as backlog
**999.65**. A second, adjacent contributor to gh#62 reading as a malfunction: the same `info`
output prints `Can be erased: yes (electrically erasable)` for this part — derived from
`electrical.type`, not from protocol (`ic_layout.py:555-559`) — and the tool then refuses to erase
it. That observation is captured alongside 999.65, not fixed in this phase.

## D-22, RECORDED

`support_status` for AE29F2008 stays `supported` and was not edited by this plan. The part writes,
reads, blank-checks and verifies correctly; only the standalone `erase` command is refused, and
that refusal is correct given what the `0x05` firmware path implements. Confirmed by the Task 1
re-derivation above, before any other action in this session.

## WHAT THIS PHASE DID NOT DO, AND WHY (D-21)

D-21's misclassification-override mechanism — a named `build_db.py` rule with its evidence, a
`diff_db.py` run proving exactly the expected changed rows, and a `DECODE-NOTES.md` update — was
held ready by CONTEXT.md and RESEARCH.md as the response *if* the classification proved wrong. It
was not used. This session confirmed:

```
$ cd /workspaces/firestarter_app && git status --porcelain -- firestarter/data/chip_database.json tools/build_db.py tools/DECODE-NOTES.md
(no output)
```

No `build_db.py` rule was added, no `diff_db.py` run was made, no regeneration occurred, no
`DECODE-NOTES.md` edit was made, and `chip_database.json` is byte-unchanged. This absence is
deliberate, not an oversight: the misclassification branch did not fire because the classification
is correct. A later reader of this record should not mistake the absence of a DB diff for the
question having gone unasked — it was asked, tested against every leg of D-19's projection, and
answered CORRECT.

## Software chip-erase for the `0x05` family — recorded, backlogged, not built (D-20)

The W29C020C datasheet documents a six-byte software chip-erase — the same `FLASH_ERASE` sequence
quoted above under the REPLY-03 section — and a fast (50 ms) chip-erase timing. A future firmware
capability could implement this for the `0x05` family using the `0x0D` family's
`eeprom28c_erase_execute` (AN-0544B six-byte software chip erase, 0 B RAM via inline literal
writes) as its template. The datasheet also documents a boot-block caveat that any such
implementation must handle: **"Once the boot block programming lockout feature is activated, the
chip erase function will be disabled."** — so a correct `0x05` chip-erase needs to account for the
two 8 KB boot blocks, not merely replay the six-cycle command. This capability is deliberately not
built in this phase (milestone boundary, and it would reverse SAFE-06's refusal for this family —
an explicit scope decision, not a quiet follow-on). Filed as backlog **999.63**.

## Summary of backlog items this verdict generates

- **999.63** — software chip-erase for the `0x05` family (D-20), with the boot-block caveat.
- **999.65** — the display-labelling residual from D-23 (elevated VPP shown for 301 rows across
  three 5 V-only families; not a `build_db.py` correction).

(999.64 and 999.66 are filed by this plan's Task 3 as well, on separate findings from this phase —
generalizing the erase refusal beyond flash4, and a `PROTOCOLS.md` citation to a non-existent
datasheet path. They are not generated by the SAFE-09 classification question itself and are
recorded here only for completeness of the backlog picture.)
