"""Detect drift between `infoic_lookup.py`'s owned `VPP_MV` table and the
generator's own copy in `firestarter_app/tools/build_db.py`.

Run standalone:

    python3 test_infoic_lookup.py -v

Or via the repo-wide discovery loop published in both skills' SKILL.md.

`infoic_lookup.py` deliberately owns a private copy of `VPP_MV` rather than
importing the generator, so this skill keeps working when `firestarter_app`
is absent. That ownership has a cost: nothing detects the two tables
drifting apart. This suite is that detector. It extracts the generator's
table with `ast.literal_eval` over the module-level assignment -- never
`import build_db`, which would defeat the whole self-contained property this
skill advertises -- and skips (with a printed reason) when the submodule is
not checked out.
"""

from __future__ import annotations

import ast
import os
import sys
import unittest

_SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

import infoic_lookup as il  # noqa: E402


def _find_build_db() -> str | None:
    """Locate build_db.py from this file's own path -- never the cwd."""
    root = os.path.normpath(os.path.join(_SCRIPTS_DIR, *[os.pardir] * 4))
    candidate = os.path.join(root, "firestarter_app", "tools", "build_db.py")
    return candidate if os.path.isfile(candidate) else None


def extract_vpp_mv_via_ast(path: str) -> dict[int, int]:
    """Pull the module-level `VPP_MV = {...}` dict out of `path` without
    importing it, using `ast.parse` + `ast.literal_eval` over the Assign
    node. Raises `LookupError` if no such assignment is found."""
    with open(path, encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=path)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "VPP_MV" for t in node.targets
        ):
            return ast.literal_eval(node.value)
    raise LookupError(f"no module-level VPP_MV assignment found in {path}")


def table_drift(a: dict[int, int], b: dict[int, int]) -> list[str]:
    """Return one line per key where `a` and `b` disagree, naming the key.
    Empty when the tables agree on every key."""
    out: list[str] = []
    for key in sorted(set(a) | set(b)):
        if a.get(key) != b.get(key):
            out.append(f"0x{key:02X}: {a.get(key)!r} != {b.get(key)!r}")
    return out


class TestVppTableDrift(unittest.TestCase):
    def test_vpp_table_matches_the_generator(self):
        build_db_path = _find_build_db()
        if build_db_path is None:
            self.skipTest(
                "firestarter_app submodule not checked out -- cannot compare "
                "against the generator's VPP_MV"
            )
        generator_table = extract_vpp_mv_via_ast(build_db_path)
        self.assertEqual(table_drift(il.VPP_MV, generator_table), [])

    def test_table_drift_negative_control(self):
        """The RED demonstration for the drift comparison itself: prove
        `table_drift` is not unconditionally empty by perturbing a copy."""
        self.assertEqual(table_drift(il.VPP_MV, dict(il.VPP_MV)), [])

        perturbed = dict(il.VPP_MV)
        some_key = next(iter(perturbed))
        perturbed[some_key] = perturbed[some_key] + 500
        drift = table_drift(il.VPP_MV, perturbed)
        self.assertNotEqual(drift, [])
        self.assertIn(f"0x{some_key:02X}", drift[0])


class TestFormatVpp(unittest.TestCase):
    def test_known_value_renders_with_v_suffix(self):
        self.assertEqual(il.format_vpp(12000), "12V")

    def test_unknown_index_renders_without_raising(self):
        self.assertIsNone(il.VPP_MV.get(0x99))
        self.assertEqual(il.format_vpp(il.VPP_MV.get(0x99)), "NOT IN TABLE")


class TestVppKeyInvariant(unittest.TestCase):
    def test_every_key_is_a_masked_high_nibble(self):
        """VPP_MV is keyed on `voltages & 0xF0` -- every key's low nibble
        must be zero. This is the decode invariant SKILL.md's troubleshooting
        table names: masking the full byte pushes the lookup off the table."""
        for key in il.VPP_MV:
            self.assertEqual(key & 0x0F, 0, f"key 0x{key:02X} is not a masked high nibble")


if __name__ == "__main__":
    unittest.main()
