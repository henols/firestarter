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
- The firmware checks the whole frame before it writes any handle field. A refusal is `MSG_ERR_BAD_FRAME` (`0xA0`) for a short frame or a wrong magic, `MSG_ERR_FRAME_VERSION` (`0xC3`) for another frame version, or `MSG_ERR_BAD_COMMAND` (`0xC2`) with a `[[refusals]]` code. Append refusal codes; never renumber them.
- Every frame version answers a version mismatch with `MSG_ERR_FRAME_VERSION` and its own `version` as the `u8` parameter. Never change this answer: it is how a host of any frame version finds the older side.
- A command without a memory payload clears `protocol` and `pulse_delay`, so no field of an earlier chip stays in the handle.
- The write-time columns of the 27C EPROM rows (`max_pulses`, `energy_cap_us`, the fallback pulse width) come from `tools/protocol/eprom_rows.toml`. The same sync generates `eprom_rows.h` for the firmware and `eprom_rows.py` for the host's write timeout. Never copy one of these values by hand.
- `[frame] min_feature` is the first feature version (major.minor) that may carry the frame. The meta release script and `release.yml` in both sub-repos refuse a tag below it, and `fw_release_gate.py` refuses to install firmware below it. Raise it with every new frame `version`.
- The host uses the generated `command_frame.KEY_*` for command-dict keys. Never copy a key string into another module.
- The host encoder (`command_codec.py`) refuses an unknown key and an out-of-range value before it opens a port. Keep its checks the same as the decoder's.
- Each new refusal gets a `[[refused_vectors]]` entry, and each new field gets an accepting `[[vectors]]` entry. Both test suites run every vector.
- No path sends JSON, except the firmware-update read of a JSON-era board's version (`{"state":13}`, after `0xA0`).
