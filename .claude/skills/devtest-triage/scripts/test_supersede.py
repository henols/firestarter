#!/usr/bin/env python3
"""Self-test for the three-leg supersede rule. stdlib only, no network.

    python3 test_supersede.py

Cases 1-2 are the two real closes from 2026-08-31 (issues #26 and #41);
cases 3-6 are the traps the rule exists to catch. Run this after touching
`supersedes()` or `version_key()`.
"""
import sys

from devtest_issues import supersedes, version_key


def rep(host, fw, generated, failing=(), steps=None):
    return {
        "number": 0, "chip": "x", "host": host, "fw": fw,
        "generated": generated[:10], "generated_full": generated,
        "failing": list(failing), "steps": steps or {},
    }


ALL_OK = {"id": "OK", "read": "OK", "write": "OK", "verify": "OK",
          "erase": "OK", "blank-check": "OK"}

CASES = [
    # (name, fail, pass, expect_supersede, expect_substring)
    ("#26 w27c020 -> #51 W27E020 (real close)",
     rep("3.0.0b15", "", "2026-08-06T09:39:32Z", ["blank-check", "write"]),
     rep("3.0.0b33", "3.0.0b22:leonardo", "2026-08-30T20:56:07Z", steps=ALL_OK),
     True, "firmware not comparable"),

    ("#41 w27c512 -> #42 (real close, same firmware)",
     rep("3.0.0b27", "3.0.0b20:leonardo", "2026-08-22T12:02:49Z",
         ["write", "verify", "erase", "blank-check"]),
     rep("3.0.0b28", "3.0.0b20:leonardo", "2026-08-22T15:15:10Z", steps=ALL_OK),
     True, ""),

    ("TRAP: failing step comes back NA, not OK",
     rep("3.0.0b20", "3.0.0b20:leonardo", "2026-08-01T00:00:00Z",
         ["blank-check"]),
     rep("3.0.0b33", "3.0.0b22:leonardo", "2026-08-30T00:00:00Z",
         steps={**ALL_OK, "blank-check": "NA"}),
     False, "not OK"),

    ("TRAP: same host and firmware — flaky, not fixed",
     rep("3.0.0b33", "3.0.0b22:leonardo", "2026-08-30T10:00:00Z", ["write"]),
     rep("3.0.0b33", "3.0.0b22:leonardo", "2026-08-30T20:00:00Z", steps=ALL_OK),
     False, "same host and firmware"),

    ("TRAP: later report, but on an OLDER host",
     rep("3.0.0b33", "3.0.0b22:leonardo", "2026-08-22T00:00:00Z", ["write"]),
     rep("3.0.0b15", "3.0.0b22:leonardo", "2026-08-30T00:00:00Z", steps=ALL_OK),
     False, "OLDER host"),

    ("TRAP: PASS predates the failure",
     rep("3.0.0b33", "3.0.0b22:leonardo", "2026-08-30T00:00:00Z", ["write"]),
     rep("3.0.0b28", "3.0.0b20:leonardo", "2026-08-01T00:00:00Z", steps=ALL_OK),
     False, "not later"),
]


def main() -> int:
    # version_key must order prereleases, and rank a final release above them.
    assert version_key("3.0.0b27") < version_key("3.0.0b28")
    assert version_key("3.0.0b22:leonardo") == version_key("3.0.0b22")
    assert version_key("3.0.0b33") < version_key("3.0.0")
    assert version_key("") is None and version_key("not reported") is None

    bad = 0
    for name, fail, ok, want, substr in CASES:
        got, notes = supersedes(fail, ok)
        joined = "; ".join(notes)
        ok_verdict = got == want and (not substr or substr in joined)
        print(f"{'PASS' if ok_verdict else 'FAIL'}  {name}\n"
              f"      -> supersede={got}  {joined or '(no notes)'}")
        if not ok_verdict:
            bad += 1
    print(f"\n{len(CASES) - bad}/{len(CASES)} cases behaved as specified")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
