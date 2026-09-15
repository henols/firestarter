#!/usr/bin/env python3
"""Phase-97 RCA-02/RCA-03 verdict-completeness gate.

Verifies the RCA exit bar (D-03): RC-1 AND RC-2 each carry a recorded confirm-or-exonerate
verdict in 97-RCA-FINDINGS.md, the W27C512 (0x07) differential control cell is filled, and a
named root cause + classification is recorded. Exits non-zero on any gap.
"""
import json
import re
import sys

FINDINGS = (
    ".planning/phases/"
    "97-pre-rca-tier-0-pre-flight-root-cause-the-0x08-0-bits-program/"
    "evidence/97-RCA-FINDINGS.md"
)
EV = ".planning/milestones/v1.18-artifacts/bench/EVIDENCE.json"
VALID_CLASS = {
    "firmware-algorithm",
    "host-pinout",
    "vpp-routing",
    "addressing",
    "silicon",
}


def main() -> int:
    text = open(FINDINGS).read().lower()
    failures = []

    # D-03: RC-1 and RC-2 must each carry a verdict (CONFIRMED or EXONERATED).
    for rc in ("rc-1", "rc-2"):
        block = "\n".join(ln for ln in text.splitlines() if rc in ln)
        if not re.search(r"confirm|exonerat|\bout\b|ruled", block):
            failures.append(f"{rc.upper()} has no recorded verdict (confirm/exonerate)")

    # A named classification must be present.
    if not any(c in text for c in VALID_CLASS):
        failures.append(
            "no root-cause classification found "
            "(firmware-algorithm/host-pinout/vpp-routing/addressing/silicon)"
        )

    # The 0x07 differential control cell must be filled.
    d = json.load(open(EV))
    w = [c for c in d["cells"] if c["chip"] == "W27C512"]
    if not w:
        failures.append("no W27C512 differential cell")
    else:
        verdict = str(w[0].get("verdict", "TBD"))
        if "TBD" in verdict or not verdict:
            failures.append("W27C512 differential verdict not recorded")

    if failures:
        for f in failures:
            print(f"FAIL: {f}", file=sys.stderr)
        return 1
    print("RCA verdict complete: RC-1 + RC-2 verdicted, classified, 0x07 differential filled")
    return 0


if __name__ == "__main__":
    sys.exit(main())
