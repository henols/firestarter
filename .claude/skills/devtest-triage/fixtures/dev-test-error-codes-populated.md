<!-- HAND-AUTHORED TEST FIXTURE (260916-nbc). This is NOT a real community report and is NOT evidence about w27c512 or any other chip -- it is synthetic test data modelled on the shape of the ten `dev test` issues open today: `steps[].error_code` populated with real firmware CATALOG ids, and no `steps[].error_name` key anywhere (that field is a later addition -- sibling item 260916-nb9 -- these ten pre-existing bodies never carry it). Used by `firmware_messages.resolve_error()`'s wiring test to prove `show` renders a resolved name for a real, non-null error code. -->

| Step | Verdict | Reason |
| ---- | ------- | ------ |
| id | OK | - |
| read | OK | - |
| blank-check | BAD | chip not blank |
| write | BAD | write did not verify |
| verify | BAD | mismatch at multiple addresses |
| erase | NA | not applicable to this family |

```json
{
  "schema_version": "2.0",
  "generated": "2026-09-16T09:00:00Z",
  "dedup_fingerprint": "aa11bb22cc33",
  "auto_capture": {
    "host_version": "3.0.0b29",
    "fw_board_identity": "3.0.0b22:leonardo",
    "hw_revision": "Rev 2.2",
    "chip": "w27c512",
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
      "verdict": "BAD",
      "reason": "chip not blank",
      "error_code": 185
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
    "vpe_before_mv": 13000,
    "vpe_after_mv": 13000
  }
}
```
