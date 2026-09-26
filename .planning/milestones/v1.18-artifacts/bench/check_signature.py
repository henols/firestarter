#!/usr/bin/env python3
"""Phase-97 RCA-01 signature-completeness gate.

Verifies the AM27C020 (0x08) cell in .planning/milestones/v1.18-artifacts/bench/EVIDENCE.json has its
failure-signature fields filled with real captures (no "TBD" placeholders) and that
the pre/post read SHAs are consistent with the recorded bits_flipped (chip pristine
when 0 bits flipped). Exits non-zero on any unfilled/contradictory field.
"""
import json
import sys

EV = ".planning/milestones/v1.18-artifacts/bench/EVIDENCE.json"
REQ = [
    "bad_bytes",
    "retries",
    "bits_flipped",
    "vpp_adc_mv",
    "dmm_pin1_v",
    "dmm_pin31_v",
    "post_read_sha256",
]


def main() -> int:
    d = json.load(open(EV))
    cells = [c for c in d["cells"] if c["chip"] == "AM27C020"]
    if not cells:
        print("FAIL: no AM27C020 cell", file=sys.stderr)
        return 1
    a = cells[0]
    missing = [k for k in REQ if "TBD" in str(a.get(k, "TBD"))]
    if missing:
        print(f"FAIL: signature fields unfilled: {missing}", file=sys.stderr)
        return 1
    bits = a.get("bits_flipped")
    pristine_ok = a.get("pre_read_sha256") == a.get("post_read_sha256")
    if str(bits) in ("0", "0.0") and not pristine_ok:
        print(
            "FAIL: 0 bits flipped but pre/post read SHA differ (chip not pristine)",
            file=sys.stderr,
        )
        return 1
    print(f"RCA-01 signature complete; bits_flipped={bits}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
