# PROM Handler Shape

Each family has one `configure_<family>(handle)` in `src/proms/<family>.cpp`.

```cpp
void configure_flash_nor_unlock(firestarter_handle_t* handle) {
    LOG_DEBUG_ID_SUB(DBG_CONFIGURING_FLASH);
    handle->firestarter_operation_init = flash_nor_unlock_generic_init;
    switch (handle->cmd) {
    case CMD_WRITE:
        handle->firestarter_operation_init = flash_nor_unlock_write_init;
        handle->firestarter_operation_main = flash_nor_unlock_write_execute;
        break;
    case CMD_CHECK_CHIP_ID:
        handle->firestarter_operation_init = NULL;  // query: no preset init
        handle->firestarter_operation_main = flash_nor_unlock_check_chip_id_execute;
        break;
    }
}
```

- Dispatch key is `handle->protocol` only, via `PROTO_*` in `proto_constants.h`. No second axis.
- No `default:` arm. `configure_memory` presets main for `CMD_READ`/`CMD_WRITE`; a default overwrites it. Unsupported commands are refused by the NULL-main guard.
- If init is preset before the switch, null it in query arms (chip ID, lock status).
- Never reuse retired ordinals: commands 4 and 6, flag `0x08`.

When you add a family or a command arm, in the same change:
- Add a case to `test/native/avr/test_dispatch` (asserts `operation_main` + `response_code`).
- Update the `configure_memory` order list in `firestarter_fw/CLAUDE.md` and the Programming Protocols wiki page.
- Ship the host side too (chip DB, `constants.py`, `serial_comm.py`). Firmware releases first.
