# dev test -- SST27SF512

| Step | Verdict | Runs | Took | Reason |
| ---- | ------- | ---- | ---- | ------ |
| id | OK | 1 | 3.53s | - |
| read | OK | 2 | 21.2s | - |
| write | OK | 2 | 115.6s | - |
| verify | OK | 2 | 28.5s | - |
| erase | OK | 2 | 16.6s | - |
| blank-check | OK | 2 | 16.1s | - |
| write-baseline-b | NA | - | - | - |
| write-baseline-a | NA | - | - | - |
| sdp-lock | NA | - | - | - |
| write-inhibited | NA | - | - | - |
| sdp-unlock | NA | - | - | - |
| write-restored | NA | - | - | - |

```json
{
  "schema_version": "1.7",
  "generated": "2026-08-28T23:28:47Z",
  "auto_capture": {
    "host_version": "3.0.0b32",
    "fw_board_identity": "3.0.0b22:leonardo",
    "hw_revision": "Rev 2.0-class, Override HW: Rev 2.0-class",
    "chip": "SST27SF512",
    "protocol": "7",
    "chip_id_expected": 49060,
    "chip_id_actual": null,
    "chip_id_mismatch_reason": null
  },
  "transport_health": {
    "cobs_errors": "not measured",
    "crc_failures": "not measured",
    "retries": "not measured",
    "timeouts": "not measured",
    "transport_suspect": false
  },
  "steps": [
    {
      "op": "id",
      "verdict": "OK",
      "run_count": 1,
      "reason": "",
      "error_code": null,
      "fingerprint": null,
      "duration_s": 3.533,
      "write_region_start": null,
      "write_region_length": null,
      "write_bits_cleared": null,
      "write_bits_retained": null,
      "write_current_source": null,
      "write_coverage": null
    },
    {
      "op": "read",
      "verdict": "OK",
      "run_count": 2,
      "reason": "",
      "error_code": null,
      "fingerprint": null,
      "duration_s": 21.162,
      "write_region_start": null,
      "write_region_length": null,
      "write_bits_cleared": null,
      "write_bits_retained": null,
      "write_current_source": null,
      "write_coverage": null
    },
    {
      "op": "write",
      "verdict": "OK",
      "run_count": 2,
      "reason": "",
      "error_code": null,
      "fingerprint": "indeterminate",
      "duration_s": 115.592,
      "write_region_start": 0,
      "write_region_length": 65536,
      "write_bits_cleared": 0,
      "write_bits_retained": 0,
      "write_current_source": "address-derived pattern (unmasked)",
      "write_coverage": null
    },
    {
      "op": "verify",
      "verdict": "OK",
      "run_count": 2,
      "reason": "",
      "error_code": null,
      "fingerprint": "indeterminate",
      "duration_s": 28.54,
      "write_region_start": null,
      "write_region_length": null,
      "write_bits_cleared": null,
      "write_bits_retained": null,
      "write_current_source": null,
      "write_coverage": null
    },
    {
      "op": "erase",
      "verdict": "OK",
      "run_count": 2,
      "reason": "",
      "error_code": null,
      "fingerprint": null,
      "duration_s": 16.638,
      "write_region_start": null,
      "write_region_length": null,
      "write_bits_cleared": null,
      "write_bits_retained": null,
      "write_current_source": null,
      "write_coverage": null
    },
    {
      "op": "blank-check",
      "verdict": "OK",
      "run_count": 2,
      "reason": "",
      "error_code": null,
      "fingerprint": null,
      "duration_s": 16.13,
      "write_region_start": null,
      "write_region_length": null,
      "write_bits_cleared": null,
      "write_bits_retained": null,
      "write_current_source": null,
      "write_coverage": null
    },
    {
      "op": "write-baseline-b",
      "verdict": "NA",
      "run_count": 0,
      "reason": "",
      "error_code": null,
      "fingerprint": null,
      "duration_s": null,
      "write_region_start": null,
      "write_region_length": null,
      "write_bits_cleared": null,
      "write_bits_retained": null,
      "write_current_source": null,
      "write_coverage": null
    },
    {
      "op": "write-baseline-a",
      "verdict": "NA",
      "run_count": 0,
      "reason": "",
      "error_code": null,
      "fingerprint": null,
      "duration_s": null,
      "write_region_start": null,
      "write_region_length": null,
      "write_bits_cleared": null,
      "write_bits_retained": null,
      "write_current_source": null,
      "write_coverage": null
    },
    {
      "op": "sdp-lock",
      "verdict": "NA",
      "run_count": 0,
      "reason": "",
      "error_code": null,
      "fingerprint": null,
      "duration_s": null,
      "write_region_start": null,
      "write_region_length": null,
      "write_bits_cleared": null,
      "write_bits_retained": null,
      "write_current_source": null,
      "write_coverage": null
    },
    {
      "op": "write-inhibited",
      "verdict": "NA",
      "run_count": 0,
      "reason": "",
      "error_code": null,
      "fingerprint": null,
      "duration_s": null,
      "write_region_start": null,
      "write_region_length": null,
      "write_bits_cleared": null,
      "write_bits_retained": null,
      "write_current_source": null,
      "write_coverage": null
    },
    {
      "op": "sdp-unlock",
      "verdict": "NA",
      "run_count": 0,
      "reason": "",
      "error_code": null,
      "fingerprint": null,
      "duration_s": null,
      "write_region_start": null,
      "write_region_length": null,
      "write_bits_cleared": null,
      "write_bits_retained": null,
      "write_current_source": null,
      "write_coverage": null
    },
    {
      "op": "write-restored",
      "verdict": "NA",
      "run_count": 0,
      "reason": "",
      "error_code": null,
      "fingerprint": null,
      "duration_s": null,
      "write_region_start": null,
      "write_region_length": null,
      "write_bits_cleared": null,
      "write_bits_retained": null,
      "write_current_source": null,
      "write_coverage": null
    }
  ],
  "banner": {
    "n_ran": 6,
    "m_applicable": 6,
    "locked_steps": []
  },
  "voltage": {
    "vpp_before_mv": 12400,
    "vpp_after_mv": 12400,
    "vpe_before_mv": 14400,
    "vpe_after_mv": 14400,
    "vpp_mv": "not measured",
    "vpe_mv": "not measured"
  },
  "is_submittable": true,
  "dedup_fingerprint": "fe0ab4e6da24",
  "db_diff": {
    "current_support_status": "supported",
    "proposed_disposition": "inconclusive -- needs N>=2 agreement (advisory)",
    "ladder_state": ""
  },
  "sdp_hold_state": "NOT-RUN"
}
```
