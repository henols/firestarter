#!/usr/bin/env python3
"""Phase-97 PRE-01 pre-flight capture gate.

Verifies the AM27C020 (0x08) cell in .planning/milestones/v1.18-artifacts/bench/EVIDENCE.json has the
PRE-01 pre-flight fields captured with real values (no "TBD"): the blank-state read
SHA and the bench-discipline identity (controller). Exits non-zero if unfilled.
"""
import json
import sys

EV = ".planning/milestones/v1.18-artifacts/bench/EVIDENCE.json"


def main() -> int:
    d = json.load(open(EV))
    cells = [c for c in d["cells"] if c["chip"] == "AM27C020"]
    if not cells:
        print("FAIL: no AM27C020 cell", file=sys.stderr)
        return 1
    a = cells[0]
    for key, label in (("pre_read_sha256", "blank-state SHA"), ("controller", "controller identity")):
        if "TBD" in str(a.get(key, "TBD")) or not a.get(key):
            print(f"FAIL: {label} not captured ({key})", file=sys.stderr)
            return 1
    print("PRE-01 pre-flight captures present (blank-state SHA + controller identity)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
