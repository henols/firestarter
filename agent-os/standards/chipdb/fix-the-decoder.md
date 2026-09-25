# Fix the Decoder, Not the Row

`firestarter/data/chip_database.json` is generated output. Never hand-edit it. The next regen overwrites it.

When a generated value is wrong, choose in this order:

1. **Decoder.** If a whole class is misread, fix the function that reads the field: `classify()`, `resolve_pinout_key()`, `interpret_timing()`, `VPP_MV` / `VCC_VOLTAGES`.
2. **Override.** If one row has an upstream data error, add an entry to `tools/datasheet_overrides.json`.
3. **Report.** If neither can be proven, report the defect. Do not guess.

```bash
python tools/build_db.py   # regenerate; commit chip_database.json in the same change
```

- Never special-case a part number in the decoder.
- Commit the regenerated `chip_database.json` with the decoder change.
