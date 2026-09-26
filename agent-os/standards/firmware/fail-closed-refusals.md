# Fail-Closed Refusals

Unknown or out-of-range input is refused with an error ID. Never clamp, never pick a default row.

```cpp
const eprom_params_t* row = eprom_params_for(handle->protocol);
if (row == NULL) {                       // never &EPROM_PARAMS[0]
    LOG_ERROR_ID_U8(MSG_ERR_PROTOCOL_NOT_IMPLEMENTED, (uint8_t)handle->protocol);
    handle->response_code = RESPONSE_CODE_ERROR;
    return;
}
if (energy_cap_us > 0 && handle->pulse_delay > energy_cap_us) {  // 0 = uncapped
    LOG_ERROR_ID_U32(MSG_ERR_PULSE_TOO_WIDE, handle->pulse_delay);
    handle->response_code = RESPONSE_CODE_ERROR;
    return;
}
```

Why: a fallback can put HV on a part that cannot take it. A silent clamp gives a verify failure that looks like bad silicon. The host needs an explicit error ID as evidence.

- Refuse pre-flight, before any HV bit is set.
- Every refusal = `LOG_ERROR_ID_*` + `RESPONSE_CODE_ERROR` + `return`. Change no hardware state.
- Lookups return NULL on no match; callers check it.
- Unknown protocol values end in `configure_not_implemented()` (`0xBB`). No other path.
- Only exception: a `0` on the wire means "use the handler default" (`pulse_delay`, AT28C `page_size`). Resolve the default first, then run the refusal checks.
- Guard sentinels: `0` in a cap field means "uncapped", not "cap at zero".
