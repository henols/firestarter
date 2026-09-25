# Spec: `info` jumper table and `info` correctness (v1.42 Phase 209)

## Context

`firestarter info` tells the operator how to set the shield jumpers. Today
`EpromSpecBuilder.build_specifications` (`firestarter_app/firestarter/ic_layout.py:601-638`) guesses
from two inputs only: the pin count and `"vpp-pin" in pin_map`. It never looks at where VPP lands.
Result:

- `DIP28_27512` (45 rows) and `DIP32_27C801` (8 rows) are told JP3 `28pin`/`32pin` and JP4 `Closed`.
  Both are wrong: their VPP is on OE.
- `DIP32_STD` / `DIP32_27C020` (158 rows) are told JP4 `Closed`. The Rev 2 silkscreen says Open.
- JP4 reuses JP3's `28pin`/`32pin` labels.
- There is no Rev 2.2/2.3 block, and 24-pin maps get N/A for JP2–JP4.
- `DIP24_2716` gets no note that its VPP (socket pin 25) is unreachable before Rev 2.2.

The operator also asked for the rest of Phase 209 (INFO-01..03):
- `info` shows the WP-pin voltage as VPP on the 301 5 V-only rows (protocols 0x05, 0x06, 0x0D).
- "Can be erased" comes from `electrical.type` only. For example it says yes on 27 flash4 (0x05)
  rows, but `erase` refuses them.
- The 0x0B description says every part shares OE/VPP. The fw docs say "via JP4 jumper routing" and
  "project documents disagree about that jumper".

Outcome: one explicit per-pin-map jumper table drives three revision blocks for every chip. The VPP
line and the erase line come from real behavior.

Requirements: `.planning/REQUIREMENTS.md` JMP-01..08, INFO-01..03. Draft table:
`.planning/research/SUMMARY.md:162-190`.

## Shaping decisions (from this session)

- **D-A. Scope** = roadmap item 2 + item 3 = Phase 209 (JMP-01..08, INFO-01..03). No firmware code,
  no wire change, no write gate. The wiki (item 7) is out of scope.
- **D-B. PROBE-01 is not done.** Ship the inferred Rev 2.0/2.1 JP4 cells now, marked `probe_pending`
  in the table source. There are 7 maps: DIP28_2764, DIP28_27256 `Closed`, and the 24-pin maps
  "does not matter". `info` prints one line under such a cell: "Not measured on a Rev 2.0 board."
  The cell is corrected after the probe.
- **D-C. INFO-03 fw doc fixes are in scope.** They are committed in `firestarter_fw` on
  `v1.42-jumper-display`.
- **D-D. Output API.** Keep `logger.info`, the same as the other 44 lines of the info view. The
  deviation from `host/echo-vs-logger` goes in standards.md. A full click.echo migration goes to the
  backlog.
- **D-E. Unknown pin map (fail closed).** A pin map that has no table entry, for example a user map
  from `~/.firestarter`, prints "No jumper data for pin map X." It never prints a guessed setting.
- **D-F. Mechanical decisions (taken, not asked):**
  - The table is a Python module, not JSON in `pinouts.json`. Reasons: typed entries, citation
    comments, and no loader change.
  - VPP on the list/search column uses the same predicate as `info`.
  - The erase predicate is one function that both `FLAG_CAN_ERASE` and `info` call.

## Task 1: Save spec documentation

Create `agent-os/specs/2026-09-25-1503-info-jumper-table/` (make `agent-os/specs/` if it does not exist):

- `plan.md`: this plan.
- `shape.md`: scope, decisions D-A..D-F, context (visuals, references, product alignment: honest
  claims, DIP 24/28/32 only, no jumper sensing so all three blocks show, host-only code).
- `standards.md`: the full text of `host/refusal-text`, `host/gate-polarity`, `host/echo-vs-logger`
  (with the D-D deviation note), `testing/non-vacuity`, `testing/no-source-introspection`,
  `testing/standalone-checkout`.
- `references.md`:
  - The JP5 gate: `firestarter_app/firestarter/jp5_gate.py`, and
    `.planning/milestones/v1.37-phases/182-jp5-destructive-operation-gate/` (CONTEXT, RESEARCH,
    `evidence/182-06-bench-readings.md`: the Rev 2.2 JP4 continuity results).
  - The RURP schematics: `.planning/milestones/v1.7-artifacts/upstream-rurp/hardware/` (Rev 2.3
    KiCad + PDF) and `firestarter_fw/document/rurp_schematics_rev1.pdf` (the JMP-08 source).
  - `.planning/notes/jumper-display-ground-truth.md`.
  - The pin-map loop precedent: `tests/test_hw_revision_gate.py:338-352` and `tests/test_jp5_gate.py:302-330`.
- `visuals/`: copy `shield-rev2-jp4-jp5.jpg`, `shield-rev2.2-jp4-jp5-jp6-jp9.jpg` and
  `shield-rev0-modified-jp1-jp2-jp3.jpg` from the Phase 182 `evidence/`. Also copy
  `RelativelyUniversalROMProgrammerRev2.3.jpg`.

Commit in the meta repo on the current branch (`experiment/agent-os`).

## Task 2: The jumper table module (JMP-01, JMP-08)

New `firestarter_app/firestarter/jumper_table.py`. It is pure data plus lookup: no I/O and no click.

- `VppLanding` enum: `SOCKET_1`, `SOCKET_3`, `SOCKET_25`, `OE`, `NONE`.
- A frozen dataclass `JumperEntry` with these fields:
  - `vpp_lands`
  - `socket_pin1` (what socket pin 1 carries: `VPP`, `A15`, `A18`, `A19`, `NC`, ...)
  - `rev01`: JP1, JP2, JP3 settings
  - `rev20_jp4`: `OPEN`, `CLOSED` or `DOES_NOT_MATTER`
  - `rev22_jp4`: `NO_JUMPER`, `POLE_28` or `POLE_24`
  - `probe_pending: bool`
  - `notes`: note keys, for example `VPP_UNREACHABLE_BEFORE_2_2` and `CANNOT_DRIVE` (for DIP24_2532)
- `JUMPER_TABLE: Mapping[str, JumperEntry]` has the 16 entries from `SUMMARY.md:170-187`. Each
  Rev 0/1 entry has a comment that cites the `rurp_schematics_rev1.pdf` sheet/net (JMP-08). Each
  `probe_pending` entry cites PROBE-01.
- `derive_vpp_landing(pins: dict, pin_count: int) -> VppLanding`. It reads the `pinouts.json`
  `pins` dict:
  - no `vpp-pin` → `NONE`
  - `vpp-pin == oe-pin` → `OE`
  - otherwise the socket pin (24-pin +4, 28-pin +2, 32-pin +0). This is the same offset that
    `database.py` `pin_conversions` encodes. Reuse or derive from it, and do not retype it.
- `lookup(pin_map_key) -> JumperEntry | None`. It returns `None` for an unknown key (D-E).
- Operator text is in module-level constants. It is STE100, and it quotes the silkscreen
  "Only for ROMs with VPP on P1" (JMP-04). No constant holds "Open for 32 pin ROMs" or a
  `28pin`/`32pin` JP4 label. The Rev 2.2 poles are "28-pin pole (toward the ZIF socket)" and
  "24-pin pole (toward the board edge)". These descriptions come from the 182-06 bench readings.

## Task 3: Render three revision blocks from the table (JMP-03..07)

In `ic_layout.py`:
- Delete the heuristic at `:601-638`.
- Replace `_get_rev1_jumper_settings_data` / `_get_rev2_jumper_settings_data` (`:140-184`) with
  renderers that read the table. Keep `_select_jumper_label`'s display style (`●` glyphs).
- Block keys are `"0/1"`, `"2.0/2.1"` and `"2.2/2.3"`. Never `jp5`, never a JP5 renderer.
- JMP-06, DIP24_2716: the Rev 0/1 and Rev 2.0/2.1 blocks show the note "This shield revision
  cannot connect VPP to pin 21. To program this chip, use a Rev 2.2 or later shield." The Rev
  2.2/2.3 block shows the 24-pin pole. `write` is not changed.
- JMP-07: "does not matter" only where `rev20_jp4 == DOES_NOT_MATTER`. Rev 2.2/2.3 never prints it.
- D-B: a `probe_pending` entry adds the "Not measured on a Rev 2.0 board." line to the Rev 2.0/2.1
  block.
- D-E: no entry → one fail-closed line and no jumper blocks.

In `eprom_info.py:368-374`, print the new blocks and notes through `logger.info` (D-D). The header
is "Jumper config (Rev 2.2 & 2.3):" and follows the same style as the other blocks.

## Task 4: VPP line only for programming-VPP protocols (INFO-01)

- Add one predicate, `shows_programming_vpp(algorithm, electrical_type) -> bool`, next to the
  protocol constants. Candidate places: `firestarter/constants.py`, or a small `vpp_display.py`.
  - It is an explicit allow-set of protocols whose `vpp_mv` is a programming VPP: 0x07, 0x08,
    0x0B, 0x10. Import the named protocol IDs and never retype the literals.
  - Every other protocol returns False. That includes 0x05/0x06/0x0D (WP voltage), the SRAM
    protocols and unknown values.
- Use it at `ic_layout.py:569-577` and at the list/search copy (`eprom_info.py:468-484`). Remove the
  inline SRAM/FRAM type check.
- The explanatory comment cites the retired `check_dispatch.py` WP carve-out
  (`git show 7ebdef8^:tools/check_dispatch.py`).

## Task 5: "Can be erased" agrees with `erase` (INFO-02)

- Extract `database.py:577-579` (`FLAG_CAN_ERASE`: type EEPROM or Flash/EEPROM, and
  `algo not in (5,)`) into one pure function, for example `erase_accepted(electrical_type, algorithm)`.
  It imports `FLASH4_PROTOCOL_ID`. `convert_to_programmer` and `build_specifications` both call it.
  After this, the two cannot drift.
- `info` text (`ic_layout.py:555-562`):
  - supported and accepted → "yes (electrically erasable)"
  - UV-EPROM → "no (UV erase only)"
  - electrically erasable but refused (flash4) → "no (erase not supported for this chip)"
  - not `supported` → no yes line
  - SRAM → no line, as today
- The Flags block bit 0x10 (`database.py:368-369`) stays as it is. It states a chip property, not
  command support. Its label stays "Electrically erasable".

## Task 6: 0x0B description and fw docs (INFO-03)

- `ic_layout.py:266-273`: replace "Shares pins between OE/VPP so high voltage is common" with the
  per-map fact. VPP is on pin 21 (2716/2532), or it shares OE on pin 20 (2732 only).
- `firestarter_fw/PROTOCOLS.md`:
  - `:180`, `:183` (§0x07): write the measured routing. On Rev 2.x, VPP reaches socket pin 1
    through the bridged JP5. JP4 "Closed" (Rev 2.0/2.1) or the 28-pin pole (Rev 2.2/2.3) joins
    socket pin 1 to socket pin 3, which is pin 1 of a 28-pin part. Cite 182-06.
  - `:546` INV-02: limit the shared OE/VPP statement to `DIP24_2732`.
- `firestarter_fw/CLAUDE.md:225-226`: replace the "documents disagree" note with the measured
  routing and name JP4/JP5.
- Commit in `firestarter_fw`. It is docs only, so no size report is needed. Say so in the commit
  body.

## Task 7: Tests

In `firestarter_app/tests/`. All tests read only this repo, and all tests call production code.

- `test_jumper_table.py` (new):
  - JMP-02: loop over `db.pin_maps` (the `skip_local_override=True` fixture). Every key has a table
    entry with all three revision blocks set. Assert an exact key count of 16.
  - JMP-01: for every key, `entry.vpp_lands == derive_vpp_landing(...)`. So a `pinouts.json` edit
    that moves VPP goes red.
  - Non-vacuity: a synthetic pin map with no entry makes `lookup` return `None`, and the render
    prints the fail-closed line. A synthetic map with VPP moved gets a mismatched landing.
    `derive_vpp_landing` gets boundary tests for each branch.
  - JMP-04: render `build_specifications` for every supported row (746 rows, exact count).
    Assert that no rendered string contains "Open for 32 pin", "Closed for 28 pin", or a
    `28pin`/`32pin` label in any JP4 cell. This checks rendered output, not source.
  - JMP-05: exact row counts on the rendered output. 45 + 8 rows get neither JP3 `28pin`/`32pin`
    nor JP4 `Closed`. 158 rows get Rev 2.0/2.1 `Open` and Rev 2.2/2.3 "no jumper".
  - JMP-06: DIP24_2716 (15 rows) gets the unreachable note in two blocks and the 24-pin pole in
    Rev 2.2/2.3.
  - JMP-07: "does not matter" appears only on `DOES_NOT_MATTER` cells, and never in Rev 2.2/2.3.
  - JMP-08: an explicit expected Rev 0/1 tuple per map, transcribed from the PDF in the test with
    the citation. The test never reads the PDF.
- INFO-01: exactly 301 rows have no VPP line, and exactly 368 have one. A synthetic unknown protocol
  gets no line.
- INFO-02: for every row, the `info` erase line agrees with `FLAG_CAN_ERASE` from
  `convert_to_programmer` and with `flash4_erase_gate.is_flash4`. Assert 27 flash4 rows show "no".
  Extend the precedent at `test_ic_layout.py:240-268`.
- `test_ic_layout.py`:
  - Keep the JP5-absent test (`:271-278`).
  - Rewrite `:281-308` on purpose. The `"2.2/2.3"` block is now required, and no `jp5` key exists.
- Snapshots: regenerate `tests/__snapshots__/test_characterization.ambr` with `--snapshot-update`.
  Review the diff line by line. Only the jumper blocks, the AT28C256 VPP line and the list/search
  VPP column may change.

## Task 8: Close-out

- Update `agent-os/product/roadmap.md` "In Progress" items 2 and 3 to done, with PROBE-01 still
  pending for the `probe_pending` cells.
- Add backlog notes: (a) migrate the info view to click.echo, (b) update the `probe_pending` cells
  after PROBE-01.
- Commit per task in the owning repo. Do not push. Pushing happens at ship time.

## Verification

1. `cd firestarter_app && pytest` shows all tests green. `ruff check .`, `ruff format --check .`,
   and mypy on the strict module list: add `jumper_table.py` to that list.
2. Run a fresh clone with uv and a 3.11 venv (`testing/standalone-checkout`), then run `pytest`
   there.
3. Manual `firestarter info` on one chip per class:
   - AM27C040 (DIP32_STD): Open / no jumper
   - a DIP28_27512 row (W27C512): no `28pin`, no Closed
   - AM27C080 (DIP32_27C801): JP4 Open / no jumper
   - AM27C64 (DIP28_2764): Closed + "Not measured" line / 28-pin pole
   - AM2716 (DIP24_2716): unreachable note / 24-pin pole
   - AT28C256 (DIP28_28C256): no VPP line, "Can be erased: yes"
   - AE29F1008 (0x05 flash4): "Can be erased: no (erase not supported…)"
4. Run `.agents/skills/asd-ste100/scripts/ste-lint.py` over the new text constants.
5. Run `git -C firestarter_fw diff` and check that it is docs only.

## As built (2026-09-25)

The plan was executed. The points below record where the result differs from the text above.

- **Block titles** are "Rev 0 & 1", "Rev 2.0 & 2.1" and "Rev 2.2 & 2.3", not "0/1", "2.0/2.1" and
  "2.2/2.3". So the printer can use `f"Rev {key}"` for all three blocks.
- **Drawings in place of glyph lines (operator request, after Task 3).** Each block draws its headers
  the way they sit on the board, with the silkscreen pin names. A jumper (`═` or `║`) is drawn only
  where the chip needs one, with a one-line instruction ("Bridge B to A13.", "Fit the jumper on
  the 28-pin pole."). The layouts come from the Phase 182 photos (see `visuals/`). They are not yet
  confirmed on the boards. Each block is `{"jumpers", "drawing", "notes"}`.
- **JP5 note.** DIP32_27C801 (pin 1 = A19) gets a note in both Rev 2.x blocks. The note quotes
  "Cut for ROMs with A19 on P1".
- **Task 4/5 modules.** They are `firestarter/vpp_display.py` (`shows_programming_vpp`) and
  `firestarter/erase_support.py` (`erase_accepted`). Both are on the mypy strict list, with
  `jumper_table.py`.
- **Task 6 extra.** `PROTOCOLS.md` also had two wrong 2732 VPP-pin statements in its 0x0B section.
  They are corrected: VPP shares OE on pin 20.
- **Related clean-up (not in this plan).** Comments in both sub-repos cited checks that no longer
  exist. They are removed: `firestarter_fw` `6db9688` and `firestarter_app` `580ebc3`, which also
  deletes the dead text scan in `test_dfu_opcode_anchors.py`.

Commits:

| Repo | Commits |
|---|---|
| meta (`experiment/agent-os`) | `58e4e785` spec, `17ed91c4` CLAUDE.md |
| `firestarter_app` (`v1.42-jumper-display`) | `49cf199` table + INFO, `f0e23b7` drawings, `580ebc3` clean-up |
| `firestarter_fw` (`v1.42-jumper-display`) | `296b0a8` routing docs, `6db9688` comment clean-up |

Verification: ruff, format and mypy (new modules) are clean. 2441 tests pass on Python 3.11, and a
fresh-clone run passes too. STE100 lint: 0 violations. Nothing is pushed.

Open:

- PROBE-01. It corrects the 7 `probe_pending` pin maps.
- A check of the drawn header layouts on the Rev 0, Rev 2.0 and Rev 2.2 boards.
