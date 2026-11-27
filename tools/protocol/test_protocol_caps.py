import tempfile
import unittest
from pathlib import Path

import protocol_caps as pc

SPEC = Path(__file__).with_name("protocol_caps.toml")


def _load_text(text):
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "s.toml"
        p.write_text(text)
        return pc.load(p)


class ProtocolCapsTest(unittest.TestCase):
    def test_real_spec_loads_and_emits_deterministically(self):
        rows = pc.load(SPEC)
        self.assertIn(0x10, [r["protocol"] for r in rows])
        for emit in pc.EMITTERS.values():
            self.assertEqual(emit(rows), emit(pc.load(SPEC)))

    def test_rejects_duplicate_protocol(self):
        row = '[[protocols]]\nprotocol = 7\nname = "{}"\ncommand_set = "x"\nvpp_route = "none"\n'
        with self.assertRaises(pc.SpecError):
            _load_text(row.format("A") + row.format("B"))

    def test_rejects_unknown_vpp_route(self):
        with self.assertRaises(pc.SpecError):
            _load_text('[[protocols]]\nprotocol = 7\nname = "A"\ncommand_set = "x"\nvpp_route = "pin9"\n')


if __name__ == "__main__":
    unittest.main()
