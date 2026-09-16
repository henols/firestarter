"""Prove `eprom_ledger.py` round-trips, preserves Notes, and cannot drop a
validated-chip row silently.

Run standalone:

    python3 test_eprom_ledger.py -v

Or via the repo-wide discovery loop published in both skills' SKILL.md.

Every write in this file goes to a `tempfile.mkdtemp()` tree. The module's
`DEFAULT_LEDGER` / `DEFAULT_DB` constants -- which point straight at the real
`/workspaces/VALIDATED-EPROMS.md` -- are never touched; every call below
passes an explicit `--ledger`/`--db` path. `firestarter_app` is never read
except by the one guarded live test, which only calls `cmd_check` (read-only).
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
import unittest

_SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

import eprom_ledger as el  # noqa: E402
from _mutation import load_mutant  # noqa: E402

MODULE_PATH = os.path.join(_SCRIPTS_DIR, "eprom_ledger.py")

# A two-vendor, three-entry synthetic database. Covers: a chip with aliases
# and chip_id_check True (W29C040), and a family of two chips (W27C512,
# M27C512) sharing one (algorithm, pinout, vpp_mv) key with chip_id_check
# False and page_size None -- so the ledger renders "none" for chip id and
# "not used" for that family's page-size range.
DB = {
    "ATMEL": [
        {
            "part_number": "W29C040, W29C040A",
            "pinout": "DIP32_STD",
            "programming": {
                "algorithm": 5,
                "chip_id_check": True,
                "chip_id_value": "0x1F8C",
                "page_size": 128,
            },
            "electrical": {"size_bytes": 524288, "vcc_mv": 5000, "vpp_mv": 12000},
        },
    ],
    "WINBOND": [
        {
            "part_number": "W27C512",
            "pinout": "DIP28_27512",
            "programming": {
                "algorithm": 7,
                "chip_id_check": False,
                "chip_id_value": "0x0000",
                "page_size": None,
            },
            "electrical": {"size_bytes": 65536, "vcc_mv": 5000, "vpp_mv": 12500},
        },
        {
            "part_number": "M27C512",
            "pinout": "DIP28_27512",
            "programming": {
                "algorithm": 7,
                "chip_id_check": False,
                "chip_id_value": "0x0000",
                "page_size": None,
            },
            "electrical": {"size_bytes": 65536, "vcc_mv": 5000, "vpp_mv": 12500},
        },
    ],
}

# One row whose `issues` cell holds two references, one whose firmware is the
# `not reported` sentinel -- both traverse the `|`-delimited ROW_RE.
RECORDS = [
    {"chip": "W29C040", "host": "3.0.0b33", "firmware": "3.0.0b22",
     "issues": "#21, #48", "date": "2026-08-31"},
    {"chip": "W27C512", "host": "3.0.0b28", "firmware": el.NOT_REPORTED,
     "issues": "#42", "date": "2026-08-22"},
    {"chip": "M27C512", "host": "3.0.0b30", "firmware": "3.0.0b20",
     "issues": "#50", "date": "2026-08-10"},
]

NOTES_BODY = (
    "- W29C040 socket note: verify pin 1 orientation.\n"
    "- A table fragment for reference: | col1 | col2 |\n"
    "- Do not confuse this with a real ## heading marker inline."
)


class TestEpromLedger(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="gsd-eprom-ledger-")
        self.db_path = os.path.join(self.tmp_dir, "chip_database.json")
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(DB, f)
        self.ledger_path = os.path.join(self.tmp_dir, "VALIDATED-EPROMS.md")

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def _write_ledger(self, text: str) -> None:
        with open(self.ledger_path, "w", encoding="utf-8") as f:
            f.write(text)

    def _args(self, **kw):
        base = dict(ledger=self.ledger_path, db=self.db_path, chip="", host="",
                    firmware=el.NOT_REPORTED, issues="", date="", force=False)
        base.update(kw)
        return argparse.Namespace(**base)

    # -- Round trip -----------------------------------------------------

    def test_round_trip_recovers_every_authored_field(self):
        rendered = el.render(RECORDS, self.db_path, "")
        self._write_ledger(rendered)
        recovered = el.read_records(self.ledger_path)
        self.assertEqual(len(recovered), len(RECORDS))
        by_chip = {r["chip"]: r for r in recovered}
        for expected in RECORDS:
            got = by_chip[expected["chip"]]
            self.assertEqual(got["host"], expected["host"])
            self.assertEqual(got["firmware"], expected["firmware"])
            self.assertEqual(got["issues"], expected["issues"])
            self.assertEqual(got["date"], expected["date"])

    # -- Idempotence ------------------------------------------------------

    def test_render_is_idempotent_on_its_own_output(self):
        first = el.render(RECORDS, self.db_path, "Some operator note.")
        self._write_ledger(first)
        second = el.render(
            el.read_records(self.ledger_path), self.db_path, el.read_notes(self.ledger_path)
        )
        self.assertEqual(first, second)

    # -- Notes preservation ------------------------------------------------

    def test_notes_survive_rewrite_byte_for_byte(self):
        rendered = el.render(RECORDS, self.db_path, NOTES_BODY)
        self._write_ledger(rendered)
        self.assertEqual(el.read_notes(self.ledger_path), NOTES_BODY)

    def test_empty_notes_round_trips_through_none_sentinel(self):
        rendered = el.render(RECORDS, self.db_path, "")
        self._write_ledger(rendered)
        self.assertIn("- None.", rendered)
        reread_notes = el.read_notes(self.ledger_path)
        second = el.render(RECORDS, self.db_path, reread_notes)
        self.assertEqual(rendered, second)

    # -- Silent data loss is the failure mode this file exists to catch ----

    def test_dropped_row_is_reported_on_stderr_and_dropped_from_render(self):
        bad_records = RECORDS + [
            {"chip": "UNKNOWNCHIP123", "host": "3.0.0b1", "firmware": "3.0.0b1",
             "issues": "#1", "date": "2026-01-01"},
        ]
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            rendered = el.render(bad_records, self.db_path, "")
        self.assertNotIn("UNKNOWNCHIP123", rendered)
        self.assertIn(
            "WARN: not in the database, dropped: UNKNOWNCHIP123", stderr.getvalue()
        )

    # -- Table located by header row, not heading ---------------------------

    def test_read_records_locates_table_by_header_row_not_heading(self):
        rendered = el.render(RECORDS, self.db_path, "")
        renamed = rendered.replace("## Validated chips", "## Chips")
        self._write_ledger(renamed)
        recovered = el.read_records(self.ledger_path)
        self.assertEqual(len(recovered), len(RECORDS))

    def test_read_records_returns_empty_when_header_row_is_corrupted(self):
        rendered = el.render(RECORDS, self.db_path, "")
        corrupted = rendered.replace(
            "| Chip | Vendor | Family | Size | VCC | Chip ID | Host | Firmware | "
            "Issues | Validated |",
            "| NOPE | NOPE |",
        )
        self.assertNotEqual(rendered, corrupted, "the header row text must be present to corrupt")
        self._write_ledger(corrupted)
        self.assertEqual(el.read_records(self.ledger_path), [])

    # -- cmd_add refusals, through the real handler --------------------------

    def test_cmd_add_refuses_unknown_chip_without_writing(self):
        rc = el.cmd_add(self._args(chip="NOPE9999", host="3.0.0b1",
                                    issues="#1", date="2026-01-01"))
        self.assertEqual(rc, 1)
        self.assertFalse(os.path.exists(self.ledger_path))

    def test_cmd_add_refuses_duplicate_without_force_and_replaces_with_force(self):
        rc = el.cmd_add(self._args(chip="W27C512", host="3.0.0b28",
                                    issues="#42", date="2026-08-22"))
        self.assertEqual(rc, 0)
        before = el.read_records(self.ledger_path)

        rc = el.cmd_add(self._args(chip="W27C512", host="3.0.0b29",
                                    issues="#43", date="2026-08-23"))
        self.assertEqual(rc, 1)
        after = el.read_records(self.ledger_path)
        self.assertEqual(before, after)

        rc = el.cmd_add(self._args(chip="W27C512", host="3.0.0b29",
                                    issues="#43", date="2026-08-23", force=True))
        self.assertEqual(rc, 0)
        records = el.read_records(self.ledger_path)
        matches = [r for r in records if r["chip"] == "W27C512"]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["host"], "3.0.0b29")

    def test_cmd_add_omitting_firmware_records_sentinel_not_inferred_from_host(self):
        rc = el.cmd_add(self._args(chip="M27C512", host="3.0.0b30",
                                    issues="#50", date="2026-08-10",
                                    firmware=el.NOT_REPORTED))
        self.assertEqual(rc, 0)
        records = el.read_records(self.ledger_path)
        row = next(r for r in records if r["chip"] == "M27C512")
        self.assertEqual(row["firmware"], el.NOT_REPORTED)
        self.assertNotEqual(row["firmware"], row["host"])

    # -- Guarded live ledger check -------------------------------------------

    def test_live_ledger_matches_fresh_render_or_skips(self):
        if not (os.path.exists(el.DEFAULT_LEDGER) and os.path.exists(el.DEFAULT_DB)):
            self.skipTest(
                "firestarter_app submodule not checked out -- the real ledger "
                "cannot be rendered"
            )
        rc = el.cmd_check(argparse.Namespace(ledger=el.DEFAULT_LEDGER, db=el.DEFAULT_DB))
        self.assertEqual(rc, 0)

    # -- Mutation guards ------------------------------------------------------

    def test_mutation_guard_date_regex_breaks_round_trip(self):
        rendered = el.render(RECORDS, self.db_path, "")
        self._write_ledger(rendered)

        intact = el.read_records(self.ledger_path)
        self.assertEqual(len(intact), len(RECORDS), "sanity: intact code must parse every row")

        mutant = load_mutant(
            MODULE_PATH,
            r"(?P<date>\d{4}-\d{2}-\d{2})",
            r"(?P<date>\d{4}-\d{2}-\d{2}\d)",
        )
        mutated = mutant.read_records(self.ledger_path)
        self.assertEqual(
            mutated, [],
            "mutant's date group can no longer match a real date, so every row is lost",
        )

    def test_mutation_guard_notes_else_branch_loses_notes(self):
        intact = el.render(RECORDS, self.db_path, "Operator note: verify VPP before write.")
        self.assertIn("Operator note", intact, "sanity: intact code must preserve notes")

        mutant = load_mutant(
            MODULE_PATH,
            r'notes.strip("\n") if notes.strip() else "- None."',
            r'"- None."',
        )
        mutated = mutant.render(RECORDS, self.db_path, "Operator note: verify VPP before write.")
        self.assertNotIn("Operator note", mutated)
        self.assertIn("- None.", mutated)


if __name__ == "__main__":
    unittest.main()
