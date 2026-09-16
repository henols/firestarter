"""Pin `firmware_messages.resolve_error()`'s render contract (DD-3,
260916-nbc PLAN.md) -- one test per documented input/output row -- plus the
ast-based drift check against the app's generated `messages.py` and the
runtime-coupling guard over this skill's own scripts (added in a later task
in this same module).

Run standalone:

    python3 test_firmware_messages.py -v

Or via the repo-wide discovery loop published in both skills' SKILL.md:

    for d in $ROOT/.claude/skills/*/scripts/tests; do
      python3 -m unittest discover -s "$d" -t "$d" || break
    done

No network, no `gh`, no writes outside `tempfile`.
"""

from __future__ import annotations

import os
import sys
import unittest

_SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

import firmware_messages as fm  # noqa: E402


class TestResolveErrorAbsentOrNull(unittest.TestCase):
    def test_none_code_renders_dash(self):
        self.assertEqual(fm.resolve_error(None), "-")

    def test_missing_error_code_key_renders_dash(self):
        step: dict = {}
        self.assertEqual(fm.resolve_error(step.get("error_code")), "-")


class TestResolveErrorKnownAndUnknown(unittest.TestCase):
    def test_known_code_resolves_table_name(self):
        self.assertEqual(fm.resolve_error(183), "183 MSG_ERR_OP_TIMEOUT")

    def test_unknown_in_range_code_renders_unknown(self):
        # 0x99 / 153 is a real gap in CATALOG -- not assigned to any message.
        self.assertNotIn(0x99, fm.MESSAGE_NAMES)
        self.assertEqual(fm.resolve_error(0x99), "153 unknown")


class TestResolveErrorRejectsUntrustedCode(unittest.TestCase):
    """Every case here must render `?` and must never echo the rejected
    value into the output."""

    def _assert_rejected(self, code):
        result = fm.resolve_error(code)
        self.assertEqual(result, "?")
        self.assertNotIn(str(code), result)

    def test_string_code_rejected(self):
        self._assert_rejected("183")

    def test_bool_true_rejected(self):
        # bool is an int subclass in Python -- True must NOT resolve to id 1.
        result = fm.resolve_error(True)
        self.assertEqual(result, "?")

    def test_negative_code_rejected(self):
        self._assert_rejected(-1)

    def test_out_of_range_code_rejected(self):
        self._assert_rejected(256)

    def test_bignum_code_rejected_and_not_echoed(self):
        huge = 10**40
        result = fm.resolve_error(huge)
        self.assertEqual(result, "?")
        self.assertNotIn(str(huge), result)


class TestResolveErrorWithReportedName(unittest.TestCase):
    def test_reported_name_agreeing_with_table(self):
        self.assertEqual(
            fm.resolve_error(183, "MSG_ERR_OP_TIMEOUT"), "183 MSG_ERR_OP_TIMEOUT"
        )

    def test_reported_name_disagreeing_with_table_shows_both(self):
        self.assertEqual(
            fm.resolve_error(183, "MSG_SOMETHING"),
            "183 MSG_SOMETHING (table: MSG_ERR_OP_TIMEOUT)",
        )

    def test_reported_name_for_code_not_in_table(self):
        self.assertNotIn(0x99, fm.MESSAGE_NAMES)
        self.assertEqual(fm.resolve_error(0x99, "MSG_BRAND_NEW"), "153 MSG_BRAND_NEW")


class TestResolveErrorRejectsHostileReportedName(unittest.TestCase):
    """A `reported_name` that is not a plain short identifier is discarded
    silently and the table's own answer is used -- the rejected text must
    never appear in the output."""

    def _assert_discarded(self, reported_name):
        result = fm.resolve_error(183, reported_name)
        self.assertEqual(result, "183 MSG_ERR_OP_TIMEOUT")

    def test_non_str_reported_name_discarded(self):
        self._assert_discarded(12345)

    def test_empty_string_reported_name_discarded(self):
        self._assert_discarded("")

    def test_41_char_reported_name_discarded(self):
        self._assert_discarded("A" * 41)

    def test_reported_name_with_space_discarded(self):
        self._assert_discarded("MSG SOMETHING")

    def test_reported_name_with_newline_discarded(self):
        hostile = "MSG_ERR\nrm -rf /"
        result = fm.resolve_error(183, hostile)
        self.assertEqual(result, "183 MSG_ERR_OP_TIMEOUT")
        self.assertNotIn(hostile, result)
        self.assertNotIn("rm -rf", result)

    def test_reported_name_with_backtick_discarded(self):
        hostile = "`whoami`"
        result = fm.resolve_error(183, hostile)
        self.assertEqual(result, "183 MSG_ERR_OP_TIMEOUT")
        self.assertNotIn(hostile, result)

    def test_reported_name_with_shell_metacharacter_discarded(self):
        hostile = "MSG_ERR$(id)"
        result = fm.resolve_error(183, hostile)
        self.assertEqual(result, "183 MSG_ERR_OP_TIMEOUT")
        self.assertNotIn(hostile, result)


if __name__ == "__main__":
    unittest.main()
