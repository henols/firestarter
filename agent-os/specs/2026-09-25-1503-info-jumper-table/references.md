# References for the info Jumper Table

## Similar Implementations

### JP5 destructive-operation gate (v1.37 Phase 182)

- **Location:**
  - `firestarter_app/firestarter/jp5_gate.py`
  - `.planning/milestones/v1.37-phases/182-jp5-destructive-operation-gate/`
- **Relevance:** this is the nearest precedent for a jumper rule keyed on pin maps. The phase also
  removed the old Rev 2.2 "JP5" renderer, because JP5 is a bridged solder jumper, not a header.
- **Key patterns:**
  - A pure policy module with its operator text in module-level constants.
  - Silkscreen text quoted exactly.
  - `tests/test_jp5_gate.py:302-330` loops over every pin map in `pinouts.json`.
- **Evidence:** `evidence/182-06-bench-readings.md` gives the Rev 2.2 JP4 continuity results:
  - The common pad connects to socket pin 1.
  - The pole toward the ZIF socket connects to socket pin 3 (the 28-pin pole).
  - The pole toward the board edge connects to socket pin 25 (the 24-pin pole).
  - JP5 is factory-bridged.

### RURP schematics

- **Location:**
  - `.planning/milestones/v1.7-artifacts/upstream-rurp/hardware/`, which has the Rev 2.3 KiCad
    schematic, the PDF and the board render.
  - `firestarter_fw/document/rurp_schematics_rev1.pdf`, whose title block says "Rev: 0".
- **Relevance:** the Rev 0/1 JP1/JP2/JP3 values come from the rev1 PDF (JMP-08). The Rev 2.x routing
  comes from the KiCad netlist.

### Jumper ground truth and draft table

- **Location:**
  - `.planning/notes/jumper-display-ground-truth.md`
  - `.planning/research/SUMMARY.md:162-190`, the draft table for the 16 pin maps
- **Relevance:** the source of the table cells and of the `[PP]` (probe-pending) marks.

### Pin-map loop precedent

- **Location:** `firestarter_app/tests/test_hw_revision_gate.py:338-352`
- **Key pattern:** `for key in db.pin_maps:`, with the pin count taken from the key name.

### Current `info` jumper code (replaced)

- **Location:**
  - `firestarter_app/firestarter/ic_layout.py:133-184` (the renderers) and `:601-638` (the
    heuristic)
  - `firestarter_app/firestarter/eprom_info.py:368-374` (the printing)
