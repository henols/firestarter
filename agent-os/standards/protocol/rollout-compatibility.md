# Rollout and Compatibility

Firmware ships first. The host may require the latest firmware.

- Release the firmware before the host that depends on it.
- If the firmware is too old, the host raises `FirmwareOutdatedError`, and the message tells the user to run `firestarter fw --install`. The host has no fallback paths for old firmware.
- One exception: the firmware-update read path (`fw`) may read the version of firmware that predates the binary command frame. It resends only the version query, as JSON, after a `MSG_ERR_BAD_FRAME`. Without it, `fw` cannot find the board it must replace.
- A wire-breaking change needs a new feature version (major.minor). `fw_release_gate.py` refuses to install firmware whose feature version is above the CLI's, and that is the only thing that stops an old CLI from flashing firmware it cannot drive.
- The binary command frame starts at feature version 3.3. Version 3.2 is skipped, because 3.2.0b1 on PyPI is a JSON-era CLI and would pass the ceiling for a binary 3.2 firmware. `fw_release_gate.py` also refuses firmware below 3.3 (`BINARY_FRAME_MIN_FEATURE`, generated from `command_frame.toml` `min_feature`). No flag waives that refusal. The release scripts refuse to tag a commit that carries the frame below that floor, so every release below it is JSON-era.
- New ack and blob fields go at the end. The host finds them by frame length, never by version string. Compute offsets from the length bytes (`ver_len`), never from a literal index.
- A numeric field has a plausibility range, and `0` means "not sent" (e.g. `write_budget_s` accepts `[1, 14400]`). Never read `0` as a real value.
