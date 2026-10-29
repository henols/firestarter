# Duplicated Host/Firmware Constants

Some wire values exist on both sides. Change both sides in one change pair.

| Host (`firestarter_app/firestarter/`) | Firmware (`firestarter_fw/`) |
|---|---|
| `constants.py` `COMMAND_*` | `include/firestarter.h` `CMD_*` |
| `constants.py` `FLAG_*` | `include/firestarter.h` `FLAG_*` |
| `constants.py` `CTRL_*` | `include/rurp_pinout.h` `CTRL_*` |
| `constants.py` `BUFFER_SIZE`, `CMD_FRAME_MAX` | `firestarter.h` `DATA_BUFFER_SIZE`, `CMD_FRAME_MAX` |

- Edit both files and commit both on the same milestone branch.
- A change to one side only is incomplete, even if all tests pass.
- The command frame layout is not duplicated: it is generated. See `command-frame.md`.
