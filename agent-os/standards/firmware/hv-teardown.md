# HV Teardown

Any function with more than one exit that can leave an HV bit set uses the body + wrapper form.

```cpp
static void eprom_internal_write_init_body(firestarter_handle_t* handle) {
    ... // may `return` anywhere
}

void eprom_write_init(firestarter_handle_t* handle) {
    eprom_internal_write_init_body(handle);
    if (handle->response_code == RESPONSE_CODE_ERROR) {
        handle->firestarter_set_control_register(handle, EPROM_HV_ALL_OFF_MASK, 0);
    }
}
```

- The wrapper is the only place that decides the clear. A new `return` in the body cannot skip it.
- Clear on error only. A successful block keeps the route on so the next block does not pay the settle time. `command_done()` clears at the end.
- A single-exit helper that raises HV (chip-ID A9, erase, VPP check) clears `EPROM_HV_ALL_OFF_MASK` as its last statement.
- Use the shared composites `EPROM_HV_ALL_OFF_MASK` / `EPROM_HV_ROUTE_MASK` (`rurp_pinout.h`). Do not build a local mask.
- Name `CTRL_VPE_ENABLE`, never `CTRL_VPP_P1_ENABLE`. The EPROM interposer swaps VPE for P1 when `using_p1_as_vpp()`. Naming P1, or adding it to `ALL_OFF`, leaves physical VPE on.
