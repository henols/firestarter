"""Coverage for the fail-closed provenance stripper.

The contract that matters is not "it removes tokens" -- a sed does that. It is
that it removes ONLY shapes it can prove safe and DECLINES everything else,
because the two defects the hand sweep produced (a dissolved opening paren whose
partner survived; a dangling `(157-03,`) were both punctuation-unaware strips.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("strip_provenance", _HERE / "strip_provenance.py")
sp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sp)


def t(line: str) -> str:
    return sp.transform_line(line)[0]


def declined(line: str) -> int:
    return sp.transform_line(line)[2]


# --- Shape 1: whole parenthetical is provenance -----------------------------


@pytest.mark.parametrize(
    "before,after",
    [
        (" * block -- already PADDED (D-09). A host-side",
         " * block -- already PADDED. A host-side"),
        ("# wire (Phase 149, PGSZ-01/PGSZ-02); 0 = absent",
         "# wire; 0 = absent"),
        ("# Dedup fingerprint (SUB-03, D-02) -- deterministic",
         "# Dedup fingerprint -- deterministic"),
        ("// WHY EXACTLY TWO FUNCTIONS (D-06):", "// WHY EXACTLY TWO FUNCTIONS:"),
    ],
)
def test_pure_provenance_parenthetical_is_removed(before, after):
    assert t(before) == after


# --- Shape 2: token inside a larger parenthetical ---------------------------


def test_token_removed_from_a_mixed_list_keeps_the_rest():
    assert t("# gate (FLAG_SKIP_SDP_UNLOCK, D-12) applies") == "# gate (FLAG_SKIP_SDP_UNLOCK) applies"


def test_leading_token_in_a_mixed_list_is_removed():
    assert t("# (D-12, FLAG_SKIP_SDP_UNLOCK) applies") == "# (FLAG_SKIP_SDP_UNLOCK) applies"


# --- Shape 3: trailing per/see clause ---------------------------------------


def test_trailing_per_clause_is_removed():
    assert t("        // EEPROM-override-absent sentinel per D-07.") == \
        "        // EEPROM-override-absent sentinel."


# --- Fail-closed: everything else is DECLINED, not mangled ------------------


def test_token_as_sentence_subject_is_declined_untouched():
    line = "     * WHY THE WRAP EXISTS AT ALL. Phase 141 rewrote eprom_write_execute as"
    assert t(line) == line
    assert declined(line) == 1


def test_multiline_parenthetical_is_declined_untouched():
    """The rurp_vpp.h defect: opener and closer on different lines."""
    line = " *   near an unregulated rail. This is Phase 124 D-14's lesson (a guard that"
    assert t(line) == line
    assert declined(line) == 1


def test_unbalanced_tail_is_declined_untouched():
    """The firestarter.h defect: a parenthetical that opens and does not close."""
    line = "     * future tenth flag above 0xFFFF trips that gate first (157-03,"
    assert t(line) == line
    assert declined(line) == 1


def test_cap0n_is_never_stripped():
    for line in ["// CAP-03 is emitted for EVERY command",
                 " * (CAP-01). */",
                 "# ack (CAP-02, D-06) carries"]:
        assert "CAP-0" in t(line)


def test_cap0n_parenthetical_is_left_whole_even_beside_another_token():
    line = "# ack (CAP-02, D-06) carries"
    assert t(line) == line


# --- Never touches code -----------------------------------------------------


def test_code_half_of_a_line_is_untouched(tmp_path):
    p = tmp_path / "a.py"
    p.write_text('LABEL = "D-02"  # note (D-09) here\n', encoding="utf-8")
    sp.process(p, apply=True)
    assert p.read_text(encoding="utf-8") == 'LABEL = "D-02"  # note here\n'


def test_a_pure_code_line_is_never_rewritten(tmp_path):
    p = tmp_path / "a.py"
    src = 'd = {"D-02": 1}\nx = Phase145 + 1\n'
    p.write_text(src, encoding="utf-8")
    sp.process(p, apply=True)
    assert p.read_text(encoding="utf-8") == src


# --- Idempotence ------------------------------------------------------------


def test_transform_is_idempotent():
    line = "# Dedup fingerprint (SUB-03, D-02) -- deterministic"
    once = t(line)
    assert t(once) == once


# --- Dry run really is dry --------------------------------------------------


def test_dry_run_does_not_write(tmp_path):
    p = tmp_path / "a.py"
    src = "# note (D-09) here\n"
    p.write_text(src, encoding="utf-8")
    sp.process(p, apply=False)
    assert p.read_text(encoding="utf-8") == src


def test_blob_pinned_files_are_never_edited(tmp_path):
    """Ruling B's four exempt files, and the reason they are exempt."""
    d = tmp_path / "src" / "proms"
    d.mkdir(parents=True)
    p = d / "eprom.cpp"
    src = "// Refusal 2 (D-03): a pulse wider than this row's per-byte\n"
    p.write_text(src, encoding="utf-8")
    removed, _, _ = sp.process(p, apply=True)
    assert removed == 0
    assert p.read_text(encoding="utf-8") == src


def test_a_non_pinned_neighbour_is_still_edited(tmp_path):
    d = tmp_path / "src" / "proms"
    d.mkdir(parents=True)
    p = d / "memory.cpp"
    p.write_text("// Refusal 2 (D-03): a pulse wider\n", encoding="utf-8")
    removed, _, _ = sp.process(p, apply=True)
    assert removed == 1
    assert p.read_text(encoding="utf-8") == "// Refusal 2: a pulse wider\n"


def test_a_parenthetical_that_opens_a_line_never_eats_the_indentation():
    """The serial_comm.py defect: `\\s*\\(` consumed a docstring line's leading
    indentation, leaving `. 0-byte param region ...` and taking the CAP-03
    parity gate to 0-of-6 facts found."""
    line = "        (T-55-05 / T-55-06). 0-byte param region (old firmware) leaves"
    assert t(line) == line
    assert declined(line) == 1


def test_indentation_is_preserved_when_the_paren_is_mid_line():
    assert t("        # narrow for mypy strict (D-06)") == "        # narrow for mypy strict"


def test_a_ringfenced_line_is_declined_not_edited(tmp_path):
    """test_read_and_parse_lines_ringfence_unchanged pins that body's SHA and
    its failure text says a change must be flagged and DEFERRED, not re-pinned."""
    p = tmp_path / "serial_comm.py"
    src = (
        "def _read_and_parse_lines(self, timeout):\n"
        '    """[ring-fenced - v1.9 RCA territory] byte-stream reader (Phase 6 D-05).\n'
        '    """\n'
        "    return None\n"
    )
    p.write_text(src, encoding="utf-8")
    removed, declined_n, _ = sp.process(p, apply=True)
    assert removed == 0
    assert declined_n == 1
    assert p.read_text(encoding="utf-8") == src


def test_trailing_pure_provenance_comment_fragment_is_removed():
    assert t("body = self.connection.read(n)  # type: ignore[union-attr]  # Phase 42 D-06") == \
        "body = self.connection.read(n)  # type: ignore[union-attr]"


def test_a_real_trailing_note_is_never_lost():
    line = "x = f()  # type: ignore[union-attr]  # narrow for mypy"
    assert t(line) == line


def test_trailing_shape_does_not_strip_a_lone_provenance_comment_to_nothing():
    """`# D-06` alone still leaves the code half intact."""
    assert t("x = f()  # D-06") == "x = f()"


def test_ringfence_protects_the_whole_region_not_just_the_marker_line(tmp_path):
    """The marker sits in the docstring; the editable comments are far below it
    with no marker of their own. Three such lines inside _read_and_parse_lines
    were edited and broke its pinned-SHA gate."""
    p = tmp_path / "serial_comm.py"
    src = (
        "class C:\n"
        "    def _read_and_parse_lines(self, timeout):\n"
        '        """[ring-fenced - v1.9 RCA territory] byte-stream reader.\n'
        '        """\n'
        "        x = 1  # type: ignore[union-attr]  # Phase 42 D-06\n"
        "        return x\n"
        "\n"
        "    def other(self):\n"
        "        y = 2  # narrow for mypy strict (D-06)\n"
        "        return y\n"
    )
    p.write_text(src, encoding="utf-8")
    sp.process(p, apply=True)
    out = p.read_text(encoding="utf-8")
    assert "# type: ignore[union-attr]  # Phase 42 D-06" in out, "fenced line must survive"
    assert "y = 2  # narrow for mypy strict\n" in out, "unfenced neighbour must still be swept"
