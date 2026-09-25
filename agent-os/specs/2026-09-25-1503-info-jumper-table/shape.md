# info Jumper Table — Shaping Notes

## Scope

`firestarter info` gets its jumper guidance from one explicit table with an entry for each pin map.
The table is keyed on where the pin map's VPP lands (socket pin 1, 3 or 25, the OE line, or none)
and on what socket pin 1 carries. It replaces the pin-count / `"vpp-pin" in pin_map` heuristic in
`ic_layout.py`. `info` prints three revision blocks for every chip: Rev 0/1 (JP1–JP3), Rev 2.0/2.1
(two-position JP4) and Rev 2.2/2.3 (three-position JP4).

This spec also covers the other `info` text fixes of the same phase:

- INFO-01: no WP-pin voltage shown as VPP.
- INFO-02: "Can be erased" agrees with `erase`.
- INFO-03: the 0x0B description, and the JP4 wording in the firmware docs.

Requirements: `.planning/REQUIREMENTS.md` JMP-01..08 and INFO-01..03 (roadmap Phase 209).

## Decisions

- **D-A. Scope** is roadmap items 2 and 3. Host code changes only, plus two firmware doc edits. No
  firmware code, no wire-protocol change, and no new write gate. The wiki tables (item 7) are out of
  scope.
- **D-B. PROBE-01 is not done.** The Rev 2.0 JP4 continuity probe has not been made. The inferred
  Rev 2.0/2.1 JP4 cells ship now and carry `probe_pending` in the table source:
  - DIP28_2764 and DIP28_27256 are `Closed`.
  - The 24-pin maps are "does not matter".
  `info` prints "Not measured on a Rev 2.0 board." under such a cell. After the probe, correct the
  cells.
- **D-C.** The INFO-03 firmware doc fixes (`PROTOCOLS.md`, `CLAUDE.md`) are in scope. They are
  committed in `firestarter_fw` on `v1.42-jumper-display`.
- **D-D.** The `info` view keeps `logger.info`, which goes to stdout at default verbosity. It is a
  recorded deviation from `host/echo-vs-logger`. A migration of the full view goes to the backlog.
- **D-E. Fail closed.** A pin map with no table entry, for example a user map from
  `~/.firestarter`, prints "No jumper data" and never a guessed setting.
- **D-F. Mechanical decisions:**
  - The table is a Python module, not JSON.
  - The list/search VPP column uses the same predicate as `info`.
  - One erase predicate feeds both `FLAG_CAN_ERASE` and the `info` erase line.
- **D-G. Board drawings (operator, after the first build).** Each header is drawn with its silkscreen pin
  names, and the jumper is drawn only where the chip needs one. The layouts come from the Phase 182
  photos, and the operator must confirm them on the boards.
- **D-H.** The block titles are "Rev 0 & 1", "Rev 2.0 & 2.1" and "Rev 2.2 & 2.3".
- **D-I.** DIP32_27C801 gets a JP5 note ("Cut for ROMs with A19 on P1") in the Rev 2.x blocks.
- Shield revision cannot be read reliably from the board (REQUIREMENTS D-2). So `info` always shows
  all three blocks.
- The Rev 0/1 values come from `rurp_schematics_rev1.pdf`, not from a probe (REQUIREMENTS D-4).

## Context

- **Visuals:** `visuals/` has three shield photographs from the v1.37 Phase 182 bench (Rev 2, Rev
  2.2 and the modified Rev 0), and the upstream Rev 2.3 board render. The three photographs are
  also the source of the drawn header layouts (D-G).
- **References:** see `references.md`.
- **Product alignment:** the Mission's "honest claims" rule, so unmeasured cells are marked. The
  scope is DIP 24/28/32 only. No shield senses JP4 or JP5. Every new check has a test that proves
  it can fail.

## Standards Applied

- host/refusal-text — the new operator text is STE100 and in module-level constants. The JP4 text
  quotes the silkscreen "Only for ROMs with VPP on P1".
- host/gate-polarity — an unknown pin map, or an unknown protocol, shows no jumper setting and no
  VPP.
- host/echo-vs-logger — considered. It is not applied, because of D-D.
- testing/non-vacuity — planted pin maps with no entry, exact row counts.
- testing/no-source-introspection — tests render the `info` data. They do not scan source.
- testing/standalone-checkout — no test reads the firmware PDF or `.planning/`.
