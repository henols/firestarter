# No Invented Fields

The generator emits only values it decodes from `infoic.xml` attributes:

`flags` (0x10 = erasable) · `voltages` · `protocol_id` · `variant` · `pin_map` · `type` · `code_memory_size` · `page_size`

- No table keyed by part number that supplies a value. A wrong value is a decode defect (see `fix-the-decoder`).
- If `infoic.xml` does not carry the information, report that. Do not add a field.
- If the T56/T76 data (e.g. `variant >> 8`, the T56/T76 `algo_number`) is more accurate than the TL866 field, use it, and cite the upstream source. This replaces the old "high byte is not an input" rule in `classify()` and `DECODE-NOTES.md` §2. Update both when you first use it.
