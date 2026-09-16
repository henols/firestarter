<!-- HAND-AUTHORED TEST FIXTURE. This is NOT a real community report and is NOT evidence
about SST39SF040 -- it is synthetic test data modelled on the shape of issue #90: a
captured-log fenced `text` block sits between the reporter's step table and the fenced
`json` report block. Must not be regenerated from a live `to_dict()`. -->

canonical part number: SST39SF040
elapsed: 14.7s

| Step | Verdict | Runs | Took | Error | Reason |
| ---- | ------- | ---- | ---- | ----- | ------ |
| id | OK | 1 | 0.2s | - | - |
| read | OK | 1 | 3.1s | - | - |
| blank-check | OK | 1 | 1.8s | - | - |
| write | BAD | 1 | 6.4s | 183 | write did not verify |
| verify | BAD | 1 | 2.9s | 175 | mismatch at multiple addresses |
| erase | NA | 1 | - | - | - |

captured log lines (captured=4, dropped=0, truncated=0):
```text
[write] eprom_operations WARNING: retry after short read
[write] eprom_operations ERROR: write did not verify at 0x0040
[verify] eprom_operations ERROR: mismatch at 0x0040
[verify] eprom_operations ERROR: mismatch at 0x00A2
```

```json
{
  "schema_version": "2.2",
  "generated": "2026-09-15T14:00:00Z",
  "elapsed": 14.7,
  "dedup_fingerprint": "7f3ac91b02de",
  "auto_capture": {
    "host_version": "3.0.0b44",
    "fw_board_identity": "3.0.0b31:leonardo",
    "hw_revision": "Rev 2.2",
    "chip": "sst39sf040",
    "protocol": "0x05",
    "chip_id_expected": null,
    "chip_id_actual": null,
    "chip_id_mismatch_reason": null
  },
  "steps": [
    {
      "op": "id",
      "verdict": "OK",
      "reason": "",
      "error_code": null
    },
    {
      "op": "read",
      "verdict": "OK",
      "reason": "",
      "error_code": null
    },
    {
      "op": "blank-check",
      "verdict": "OK",
      "reason": "",
      "error_code": null
    },
    {
      "op": "write",
      "verdict": "BAD",
      "reason": "write did not verify",
      "error_code": 183
    },
    {
      "op": "verify",
      "verdict": "BAD",
      "reason": "mismatch at multiple addresses",
      "error_code": 175
    },
    {
      "op": "erase",
      "verdict": "NA",
      "reason": "not applicable to this family",
      "error_code": null
    }
  ],
  "voltage": {
    "vpp_before_mv": 12000,
    "vpp_after_mv": 12000,
    "vpe_before_mv": 12000,
    "vpe_after_mv": 12000
  },
  "log_capture": {
    "entries": [
      {
        "step": "write",
        "source": "eprom_operations",
        "level": "WARNING",
        "message": "retry after short read",
        "repeat": 1
      },
      {
        "step": "write",
        "source": "eprom_operations",
        "level": "ERROR",
        "message": "write did not verify at 0x0040",
        "repeat": 1
      },
      {
        "step": "verify",
        "source": "eprom_operations",
        "level": "ERROR",
        "message": "mismatch at 0x0040",
        "repeat": 1
      },
      {
        "step": "verify",
        "source": "eprom_operations",
        "level": "ERROR",
        "message": "mismatch at 0x00A2",
        "repeat": 1
      }
    ],
    "captured": 4,
    "dropped": 0,
    "truncated": 0
  }
}
```
