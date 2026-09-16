"""Pin `devtest_issues.py`'s untrusted-body parser and the three-leg supersede
rule (SKILL.md sec3a), with mutation guards proving each guard can fail.

Run standalone:

    python3 test_devtest_issues.py -v

Or via the repo-wide discovery loop published in both skills' SKILL.md:

    for d in $ROOT/.claude/skills/*/scripts/tests; do
      python3 -m unittest discover -s "$d" -t "$d" || break
    done

No network, no `gh`, no shelling out, no writes outside a temp directory --
this suite only ever calls the private `_summarize()` and pure functions.
"""

from __future__ import annotations

import json
import os
import sys
import unittest

_SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

import devtest_issues as di  # noqa: E402
from _mutation import load_mutant  # noqa: E402

MODULE_PATH = os.path.join(_SCRIPTS_DIR, "devtest_issues.py")


def issue(number, chip, verdict, generated, host, fw, steps):
    """Build the {"number","title","body"} shape `gh issue list --json ...`
    produces, with the report embedded in a fenced ```json block carrying
    `schema_version`. `steps` is a list of (op, verdict) pairs.

    Every supersede assertion in this file goes through `di._summarize()` on
    the dict this returns -- never a hand-built summary dict.
    """
    report = {
        "schema_version": "2.0",
        "generated": generated,
        "dedup_fingerprint": "0123456789ab",
        "auto_capture": {"host_version": host, "fw_board_identity": fw},
        "steps": [{"op": op, "verdict": v, "reason": ""} for op, v in steps],
    }
    body = "```json\n" + json.dumps(report) + "\n```"
    title = f"[dev test] {chip} — {verdict}"
    return {"number": number, "title": title, "body": body}


# The failure under test, measured during planning: host 3.0.0b27, firmware
# 3.0.0b20:leonardo, generated 2026-08-22T10:00:00Z, failing write and verify.
FAIL = issue(
    1, "sst39sf040", "FAIL", "2026-08-22T10:00:00Z",
    "3.0.0b27", "3.0.0b20:leonardo",
    [("read", "OK"), ("blank-check", "OK"), ("write", "BAD"), ("verify", "BAD")],
)


class TestUntrustedBodyParser(unittest.TestCase):
    """`extract_report`, `parse_title`, `is_devtest`, `fingerprint`."""

    def test_extract_report_finds_first_qualifying_block(self):
        body = (
            "```\nnot json at all\n```\n\n"
            "```json\n" + json.dumps({"schema_version": "2.0", "ok": True}) + "\n```"
        )
        report = di.extract_report(body)
        self.assertIsInstance(report, dict)
        self.assertTrue(report.get("ok"))

    def test_extract_report_requires_schema_version_key(self):
        body = "```json\n" + json.dumps({"foo": "bar"}) + "\n```"
        self.assertIsNone(di.extract_report(body))

    def test_extract_report_over_max_body_neither_raises_nor_hangs(self):
        body = "x" * (di.MAX_BODY + 50_000)
        self.assertIsNone(di.extract_report(body))
        self.assertFalse(di.is_devtest("[dev test] chip — FAIL", body))

    def test_is_devtest_requires_both_markers(self):
        self.assertFalse(di.is_devtest("no marker here", FAIL["body"]))
        self.assertFalse(di.is_devtest(FAIL["title"], "no report here"))
        self.assertTrue(di.is_devtest(FAIL["title"], FAIL["body"]))

    def test_parse_title_accepts_plain_hyphen(self):
        parsed = di.parse_title("[dev test] at28c256 - FAIL")
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["chip"], "at28c256")
        self.assertEqual(parsed["verdict"], "FAIL")

    def test_fingerprint_falls_back_to_raw_body_regex(self):
        body = 'stray text "dedup_fingerprint": "abc123def456" more text'
        self.assertEqual(di.fingerprint(None, body), "abc123def456")

    def test_fingerprint_returns_dash_when_neither_carries_one(self):
        self.assertEqual(di.fingerprint(None, "nothing here"), "-")


class TestVersionKey(unittest.TestCase):
    def test_final_release_outranks_prerelease(self):
        self.assertLess(di.version_key("3.0.0b22"), di.version_key("3.0.0"))

    def test_board_suffix_excluded_from_version(self):
        self.assertEqual(di.version_key("3.0.0b22:leonardo")[:4], (3, 0, 0, 22.0))

    def test_unparseable_returns_none(self):
        self.assertIsNone(di.version_key("unknown"))
        self.assertIsNone(di.version_key(""))


class TestSupersedesNineOutcomes(unittest.TestCase):
    """All nine documented `supersedes()` outcomes (SKILL.md sec3a), each
    exercised through the real path: issue dict -> `_summarize()` ->
    `supersedes()`."""

    def test_later_all_ok_supersedes(self):
        ok = issue(2, "sst39sf040", "PASS", "2026-08-30T10:00:00Z",
                   "3.0.0b33", "3.0.0b22:leonardo",
                   [("write", "OK"), ("verify", "OK")])
        result, notes = di.supersedes(di._summarize(FAIL), di._summarize(ok))
        self.assertTrue(result)
        self.assertEqual(notes, [])

    def test_earlier_report_does_not_supersede(self):
        ok = issue(3, "sst39sf040", "PASS", "2026-08-01T00:00:00Z",
                   "3.0.0b33", "3.0.0b22:leonardo",
                   [("write", "OK"), ("verify", "OK")])
        result, notes = di.supersedes(di._summarize(FAIL), di._summarize(ok))
        self.assertFalse(result)
        self.assertIn("not later than the failure by report timestamp", notes[0])

    def test_same_host_and_firmware_does_not_supersede(self):
        ok = issue(4, "sst39sf040", "PASS", "2026-08-23T10:00:00Z",
                   "3.0.0b27", "3.0.0b20:leonardo",
                   [("write", "OK"), ("verify", "OK")])
        result, notes = di.supersedes(di._summarize(FAIL), di._summarize(ok))
        self.assertFalse(result)
        self.assertIn("same host and firmware as the failure", notes[0])

    def test_older_host_does_not_supersede(self):
        ok = issue(5, "sst39sf040", "PASS", "2026-08-23T10:00:00Z",
                   "3.0.0b20", "3.0.0b22:leonardo",
                   [("write", "OK"), ("verify", "OK")])
        result, notes = di.supersedes(di._summarize(FAIL), di._summarize(ok))
        self.assertFalse(result)
        self.assertIn("ran an OLDER host", notes[0])

    def test_older_firmware_does_not_supersede(self):
        ok = issue(6, "sst39sf040", "PASS", "2026-08-23T10:00:00Z",
                   "3.0.0b33", "3.0.0b10:leonardo",
                   [("write", "OK"), ("verify", "OK")])
        result, notes = di.supersedes(di._summarize(FAIL), di._summarize(ok))
        self.assertFalse(result)
        self.assertIn("ran OLDER firmware", notes[0])

    def test_write_na_does_not_supersede(self):
        ok = issue(7, "sst39sf040", "PASS", "2026-08-23T10:00:00Z",
                   "3.0.0b33", "3.0.0b22:leonardo",
                   [("write", "NA"), ("verify", "OK")])
        result, notes = di.supersedes(di._summarize(FAIL), di._summarize(ok))
        self.assertFalse(result)
        self.assertIn("step `write` is NA in the PASS, not OK", notes[0])

    def test_write_absent_does_not_supersede(self):
        ok = issue(8, "sst39sf040", "PASS", "2026-08-23T10:00:00Z",
                   "3.0.0b33", "3.0.0b22:leonardo",
                   [("verify", "OK")])
        result, notes = di.supersedes(di._summarize(FAIL), di._summarize(ok))
        self.assertFalse(result)
        self.assertIn("step `write` is absent in the PASS, not OK", notes[0])

    def test_firmware_null_still_supersedes_with_caveat(self):
        ok = issue(9, "sst39sf040", "PASS", "2026-08-23T10:00:00Z",
                   "3.0.0b33", None,
                   [("write", "OK"), ("verify", "OK")])
        result, notes = di.supersedes(di._summarize(FAIL), di._summarize(ok))
        self.assertTrue(result)
        self.assertTrue(any("firmware not comparable on both sides" in n for n in notes))

    def test_host_null_does_not_supersede(self):
        ok = issue(10, "sst39sf040", "PASS", "2026-08-23T10:00:00Z",
                   None, "3.0.0b22:leonardo",
                   [("write", "OK"), ("verify", "OK")])
        result, notes = di.supersedes(di._summarize(FAIL), di._summarize(ok))
        self.assertFalse(result)
        self.assertIn("host version not comparable", notes[0])


class TestMutationGuards(unittest.TestCase):
    """Each guard loads a deliberately broken copy of `devtest_issues.py` and
    proves the intact-code answer flips to WRONG on the mutant. The third
    guard is the one that matters most: it is exactly the hazard SKILL.md
    sec3a leg 3 exists to prevent -- closing a live `blank-check BAD` against
    a later `blank-check NA`."""

    def test_leg1_generated_comparison_guard(self):
        mutant = load_mutant(
            MODULE_PATH,
            'ok["generated_full"] > fail["generated_full"]',
            'ok["generated_full"] != fail["generated_full"]',
        )
        ok = issue(11, "sst39sf040", "PASS", "2026-08-01T00:00:00Z",
                   "3.0.0b33", "3.0.0b22:leonardo",
                   [("write", "OK"), ("verify", "OK")])

        real_result, _ = di.supersedes(di._summarize(FAIL), di._summarize(ok))
        self.assertFalse(real_result, "sanity: intact code must block an earlier PASS")

        mutant_result, _ = mutant.supersedes(mutant._summarize(FAIL), mutant._summarize(ok))
        self.assertTrue(mutant_result, "mutant should wrongly let the earlier PASS supersede")

    def test_leg2_advanced_flag_guard(self):
        mutant = load_mutant(
            MODULE_PATH,
            "advanced = oh > fh or (ff is not None and of is not None and of > ff)",
            "advanced = True",
        )
        ok = issue(12, "sst39sf040", "PASS", "2026-08-23T10:00:00Z",
                   "3.0.0b27", "3.0.0b20:leonardo",
                   [("write", "OK"), ("verify", "OK")])

        real_result, _ = di.supersedes(di._summarize(FAIL), di._summarize(ok))
        self.assertFalse(real_result, "sanity: intact code must block a same-build PASS")

        mutant_result, _ = mutant.supersedes(mutant._summarize(FAIL), mutant._summarize(ok))
        self.assertTrue(mutant_result, "mutant should wrongly let the same-build PASS supersede")

    def test_leg3_na_not_ok_guard(self):
        mutant = load_mutant(
            MODULE_PATH,
            'if got != "OK":',
            'if got not in ("OK", "NA"):',
        )
        ok = issue(13, "sst39sf040", "PASS", "2026-08-23T10:00:00Z",
                   "3.0.0b33", "3.0.0b22:leonardo",
                   [("write", "NA"), ("verify", "OK")])

        real_result, _ = di.supersedes(di._summarize(FAIL), di._summarize(ok))
        self.assertFalse(real_result, "sanity: intact code must not accept NA for a failing step")

        mutant_result, _ = mutant.supersedes(mutant._summarize(FAIL), mutant._summarize(ok))
        self.assertTrue(
            mutant_result,
            "mutant should wrongly close a live defect behind an NA step",
        )

    def test_version_key_prerelease_ordering_guard(self):
        mutant = load_mutant(
            MODULE_PATH,
            'float(pre) if pre is not None else float("inf")',
            "float(pre) if pre is not None else 0.0",
        )
        self.assertLess(di.version_key("3.0.0b22"), di.version_key("3.0.0"))
        self.assertFalse(
            mutant.version_key("3.0.0b22") < mutant.version_key("3.0.0"),
            "mutant should wrongly rank a prerelease above the final release",
        )


if __name__ == "__main__":
    unittest.main()
