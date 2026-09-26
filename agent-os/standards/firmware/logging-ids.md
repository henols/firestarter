# Logging with Message IDs

Emit only catalog IDs through the `LOG_<SEV>_ID_*` macros in `logging_id.h`. Severity is in the ID; every macro calls `rurp_log_id`.

```cpp
bool force = is_flag_set(FLAG_FORCE);
mem_util_report_voltage(handle, vpp_mv, handle->vpp_mv,
                        force ? MSG_WARN_VPP_HIGH : MSG_ERR_VPP_HIGH,
                        force ? RESPONSE_CODE_WARNING : RESPONSE_CODE_ERROR);

uint8_t _b[4] = { addr >> 16, addr >> 8, addr, pulse_count };  // big-endian
LOG_ERROR_ID_BYTES(MSG_ERR_MAX_PULSES, _b, 4);
```

- A new message goes in the meta repo `tools/catalog/messages.toml`, then run codegen there. Never hand-edit `messages.h`.
- The payload matches the catalog shape: big-endian, exact byte count. Use `LOG_ID_U*` or the composites, or pack `_b[]` by hand.
- A `--force` downgrade forks the ID and the response code together. Both IDs must be in the catalog.
- An unrecognised raw chip value: send the raw byte + `0xFF` decode + `RESPONSE_CODE_WARNING`. Never coerce it to a known value.
- `LOG_INFO_ID_*` emits only with `FLAG_VERBOSE`. Data the host needs uses DATA/WARN/ERROR.
- Uno-class (`SERIAL_ON_IO`): frames sent in programmer mode go to a 4-slot buffer, and extra frames drop silently. Keep frames per operation to a minimum there. Guard periodic emits with `#ifndef SERIAL_ON_IO`.
