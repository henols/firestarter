#!/usr/bin/env python3
"""Phase-99 EVIDENCE graduation gate (anti-fabrication).

Verifies the AM27C020 (0x08) Phase-99 cell in .planning/milestones/v1.18-artifacts/bench/EVIDENCE.json
(the graduation-or-defer cell added in plan 99-04, `op` starting with "phase99") has
its bench-discipline + signature fields filled with real captures (no "TBD"
placeholders) and is SHA-self-consistent:

- PASS (graduation): write_image_sha256 == readback_sha256 (the graduation oracle).
- DEFER (deferral): bits_flipped + post_read_sha256 present (the failing-vs-fixed
  differential); write==readback is NOT required (there is nothing to match).

Deliberately does NOT read the Phase-97 `tier0_microprobe+rca01` cell — that is the
pre-fix failure signature, checked by check_signature.py, and must not be conflated
with the post-fix Phase-99 graduation-or-defer cell.

Exits 1 (not 0) when no phase99* AM27C020 cell exists yet -- this is the expected
pre-bench state; the gate only turns green after plan 99-04 fills the cell in.
No raw SHA is ever hardcoded here -- all SHAs are read from the cell fields.
"""

import json
import sys

EV = ".planning/milestones/v1.18-artifacts/bench/EVIDENCE.json"

# Fields required regardless of PASS/DEFER outcome (bench-discipline + signature).
REQ_COMMON = [
    "controller",
    "port",
    "r1_readback",
    "r2_readback",
    "fw_commit",
    "vpp_adc_mv",
    "verdict",
]

# PASS-branch-only required fields (the graduation oracle).
REQ_PASS = ["write_image_sha256", "readback_sha256"]

# DEFER-branch-only required fields (the failing-vs-fixed differential).
REQ_DEFER = ["bits_flipped", "post_read_sha256"]


def _is_tbd(value: object) -> bool:
    """True if the field is missing or still carries a TBD placeholder."""
    return "TBD" in str(value if value is not None else "TBD")


def main() -> int:
    d = json.load(open(EV))
    cells = [
        c
        for c in d.get("cells", [])
        if c.get("chip") == "AM27C020" and str(c.get("op", "")).startswith("phase99")
    ]
    if not cells:
        print("MISSING: no phase99 AM27C020 cell yet", file=sys.stderr)
        return 1

    cell = cells[0]

    missing_common = [k for k in REQ_COMMON if _is_tbd(cell.get(k))]
    if missing_common:
        print(
            f"FAIL: bench-discipline fields unfilled: {missing_common}", file=sys.stderr
        )
        return 1

    verdict = str(cell.get("verdict", ""))

    if verdict.startswith("PASS"):
        missing = [k for k in REQ_PASS if _is_tbd(cell.get(k))]
        if missing:
            print(
                f"FAIL: PASS verdict missing graduation fields: {missing}",
                file=sys.stderr,
            )
            return 1
        write_sha = cell.get("write_image_sha256")
        readback_sha = cell.get("readback_sha256")
        if write_sha != readback_sha:
            print(
                "FAIL: PASS verdict but write_image_sha256 != readback_sha256 "
                f"({write_sha!r} != {readback_sha!r}) -- graduation oracle contradicted",
                file=sys.stderr,
            )
            return 1
        print("PASS: phase99 AM27C020 graduation cell complete and SHA-self-consistent")
        return 0

    if verdict.startswith("DEFER"):
        missing = [k for k in REQ_DEFER if _is_tbd(cell.get(k))]
        if missing:
            print(
                f"FAIL: DEFER verdict missing differential fields: {missing}",
                file=sys.stderr,
            )
            return 1
        print(
            "PASS: phase99 AM27C020 deferral cell complete (failing-vs-fixed differential)"
        )
        return 0

    print(
        f"FAIL: verdict does not start with PASS or DEFER: {verdict!r}", file=sys.stderr
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
