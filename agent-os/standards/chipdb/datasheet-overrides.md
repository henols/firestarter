# Datasheet Overrides

`tools/datasheet_overrides.json` corrects one decoded field on one row, with evidence.

```json
"FUJITSU/MBM27128": {
  "datasheet": "datasheets/MBM27128.pdf",
  "note": "Figure 3, the Quick Pro flow chart on page 4-20, specifies TPW = 1 ms ...",
  "fields": {
    "programming.pulse_duration_us": { "was": 200, "is": 1000 }
  }
}
```

- Commit the datasheet PDF under `firestarter_app/datasheets/`. The path is relative to the app root.
- `note` names the page, figure or table, and says why that reading applies (e.g. initial pulse, not conventional pulse).
- Only six fields can be overridden: `electrical.size_bytes`, `pin_count`, `vpp_mv`, `vcc_mv`, `vdd_mv`, `programming.pulse_duration_us`. An algorithm, pinout or support-status error is a decoder fix.
- The loader enforces the rest: key `MFG/ALIAS`, sorted keys, `was` equals the live decode, no no-op, every key matches a row.
