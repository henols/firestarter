# Binary Command Frame

The host sends each command as one binary frame. The layout has one source:
`tools/protocol/command_frame.toml` in the meta repo. Generate the artifacts only there.

```bash
# edit tools/protocol/command_frame.toml, then:
tools/protocol/sync_to_subrepos.sh   # writes firestarter_fw/include/command_frame.h,
                                     # firestarter_fw/test/native/avr/test_command_decode/command_vectors.h,
                                     # firestarter_app/firestarter/command_frame.py,
                                     # firestarter_app/tests/golden/command_vectors.json
```

```
[0xF5 magic][version u8][cmd u8][flags u16 BE][length u16 BE][payload]
```

- Never hand-edit a generated artifact. Never regenerate in a sub-repo.
- Every field has a fixed width and offset. Never reorder or resize a field inside a version. A layout change is a new `version`.
- `0` in a numeric field means "not sent". `0xFF` in a bus-line field means "no line".
- The firmware checks the whole frame before it writes any handle field. A refusal is `MSG_ERR_BAD_FRAME` (`0xA0`) for the header, or `MSG_ERR_BAD_COMMAND` (`0xC2`) with a `[[refusals]]` code. Append refusal codes; never renumber them.
- The host encoder (`command_codec.py`) refuses an unknown key and an out-of-range value before it opens a port. Keep its checks the same as the decoder's.
- Each new refusal gets a `[[refused_vectors]]` entry, and each new field gets an accepting `[[vectors]]` entry. Both test suites run every vector.
- No path sends JSON, except the firmware-update read of a JSON-era board's version (`{"state":13}`, after `0xA0`).
