# Rollout and Compatibility

Firmware ships first. The host may require the latest firmware.

- Release the firmware before the host that depends on it.
- If the firmware is too old, the host raises `FirmwareOutdatedError`, and the message tells the user to run `firestarter fw --install`. The host has no fallback paths for old firmware.
- New ack and blob fields go at the end. The host finds them by frame length, never by version string. Compute offsets from the length bytes (`ver_len`), never from a literal index.
- A numeric field has a plausibility range, and `0` means "not sent" (e.g. `write_budget_s` accepts `[1, 14400]`). Never read `0` as a real value.
