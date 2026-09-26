# Extra Chips

`tools/extra_chips.json` adds a real chip that `infoic.xml` does not list at all. It never changes a chip upstream has. Use `datasheet_overrides.json` for that.

- Check `infoic.xml` first. A name hit on a different part (e.g. `25160` SPI for `2516`) does not count as listed.
- Use the generated row schema, with the same keys as the existing entries. No new keys: the field-inventory test fails on any new key.
- Set `verification_status: "UNVERIFIED"` and a `verification_note` until a bench write proof exists.
