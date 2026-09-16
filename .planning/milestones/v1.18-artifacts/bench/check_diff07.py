#!/usr/bin/env python3
"""Phase-97 RCA-02 differential-control gate.

Verifies the W27C512 (0x07) differential-control cell in
.planning/milestones/v1.18-artifacts/bench/EVIDENCE.json is filled with a recorded verdict (no "TBD").
Exits non-zero if unfilled.
"""
import json
import sys

EV = ".planning/milestones/v1.18-artifacts/bench/EVIDENCE.json"


def main() -> int:
    d = json.load(open(EV))
    w = [c for c in d["cells"] if c["chip"] == "W27C512"]
    if not w:
        print("FAIL: no W27C512 differential cell", file=sys.stderr)
        return 1
    verdict = str(w[0].get("verdict", "TBD"))
    if "TBD" in verdict or not verdict:
        print("FAIL: W27C512 differential verdict not recorded", file=sys.stderr)
        return 1
    print(f"RCA-02 differential control recorded; W27C512 verdict={verdict}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
