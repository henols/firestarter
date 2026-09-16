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

import contextlib
import io
import json
import os
import sys
import tempfile
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
    `schema_version`.

    `steps` is a list of tuples, each `(op, verdict)`, `(op, verdict,
    error_code)` or `(op, verdict, error_code, error_name)`. The `error_code`
    / `error_name` slots are optional so every pre-existing 2-tuple call site
    keeps working unchanged; omitting `error_code` (or passing `None`) omits
    the key entirely, which is the shape a pre-260916-nbc report carries.

    Every supersede assertion in this file goes through `di._summarize()` on
    the dict this returns -- never a hand-built summary dict.
    """
    step_dicts = []
    for s in steps:
        op, v = s[0], s[1]
        error_code = s[2] if len(s) > 2 else None
        error_name = s[3] if len(s) > 3 else None
        d = {"op": op, "verdict": v, "reason": ""}
        if error_code is not None:
            d["error_code"] = error_code
        if error_name is not None:
            d["error_name"] = error_name
        step_dicts.append(d)
    report = {
        "schema_version": "2.0",
        "generated": generated,
        "dedup_fingerprint": "0123456789ab",
        "auto_capture": {"host_version": host, "fw_board_identity": fw},
        "steps": step_dicts,
    }
    body = "```json\n" + json.dumps(report) + "\n```"
    title = f"[dev test] {chip} — {verdict}"
    return {"number": number, "title": title, "body": body}


def run_show(body: str, title: str = "[dev test] chip — FAIL") -> str:
    """Run `cmd_show` in offline `--body-file` mode and return captured
    stdout. `args.number = None` so no `gh` call is reachable."""
    args = di.argparse.Namespace(
        number=None, repo=di.REPO, title=title, body_file=None,
    )
    with contextlib.ExitStack() as stack:
        tmp = stack.enter_context(
            tempfile.NamedTemporaryFile(
                mode="w", suffix=".md", delete=False, encoding="utf-8"
            )
        )
        tmp.write(body)
        tmp.close()
        args.body_file = tmp.name
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            di.cmd_show(args)
        try:
            os.unlink(tmp.name)
        except OSError:
            pass
    return buf.getvalue()


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


class TestErrorColumnRendering(unittest.TestCase):
    """`cmd_show`'s step table carries a new `error` column (260916-nbc),
    between `verdict` and `reason`. Every case here goes through the real
    `cmd_show` in offline `--body-file` mode via `run_show()` -- never a
    hand-built string -- with `args.number = None` so no `gh` call is
    reachable."""

    def test_header_line_carries_error_between_verdict_and_reason(self):
        body = issue(
            20, "w27c512", "FAIL", "2026-09-16T09:00:00Z",
            "3.0.0b29", "3.0.0b22:leonardo",
            [("read", "OK")],
        )["body"]
        out = run_show(body)
        self.assertIn("  step         verdict    error                        reason",
                      out)

    def test_populated_codes_render_all_three_resolved_names(self):
        body = issue(
            21, "w27c512", "FAIL", "2026-09-16T09:00:00Z",
            "3.0.0b29", "3.0.0b22:leonardo",
            [
                ("blank-check", "BAD", 185),
                ("write", "BAD", 183),
                ("verify", "BAD", 175),
            ],
        )["body"]
        out = run_show(body)
        self.assertIn("185 MSG_ERR_CHIP_ID_MISMATCH", out)
        self.assertIn("183 MSG_ERR_OP_TIMEOUT", out)
        self.assertIn("175 MSG_ERR_VERIFY", out)

    def test_all_null_error_codes_render_dash_and_route_line_unchanged(self):
        body = issue(
            22, "sst39sf040", "FAIL", "2026-08-22T10:00:00Z",
            "3.0.0b27", "3.0.0b20:leonardo",
            [("read", "OK"), ("write", "BAD"), ("verify", "BAD")],
        )["body"]
        out = run_show(body)
        for line in out.splitlines():
            if line.strip().startswith(("read ", "write ", "verify ")):
                self.assertIn(" - ", line)
        self.assertIn(
            "  ROUTE: FAIL — datasheet cross-check needed. Failing: write, verify",
            out,
        )

    def test_reported_error_name_renders_in_the_cell(self):
        body = issue(
            23, "w27c512", "FAIL", "2026-09-16T09:00:00Z",
            "3.0.0b29", "3.0.0b22:leonardo",
            [("write", "BAD", 183, "MSG_ERR_OP_TIMEOUT")],
        )["body"]
        out = run_show(body)
        self.assertIn("183 MSG_ERR_OP_TIMEOUT", out)


if __name__ == "__main__":
    unittest.main()
