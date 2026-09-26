"""Tests for check_record_corrections.py (Phase 130 Plan 02, D-08/BASE-08).

This is the MANDATORY anti-hollow pairing for the new planning-record staleness
checker: a checker with no negative-fixture test is exactly this project's
v1.12 hollow-GATE-03 failure mode -- a declared-empty detector that could
never fail because nothing concrete was asserted against it. Every planted-
violation test below invokes the checker as a real subprocess against a
committed fixture file via the FIRESTARTER_RECORDSCAN_TARGETS env seam --
never an in-process import for the scan/violation behaviour -- so a passing
test suite proves the checker itself (not the test) fails the build on a
real violation. The sole in-process import exception is
`test_all_five_default_targets_exist_on_disk` (test 13), which is the
falsifiable form of the module docstring's claim that no arming branch is
needed.

Coverage:
  1. clean_record_control.md exits 0 with PASS:.
  2. Planted stale figure (planted_stale_figure.md) flips the checker to a
     non-zero exit, naming the leonardo-headroom-2992 label.
  3. mislabeled_block.md flips the checker to a non-zero exit, naming the
     same label -- proving an unrecognised bold lead-in does not exempt.
  4. labeled_correction_control.md exits 0 -- the negative direction for the
     block-label path.
  5. Suppression is real (block): relocating the needle line ABOVE the
     block opener (in tmp_path) makes the identical text FAIL.
  6. labeled_history_control.md exits 0 -- the negative direction for the
     inline-history path.
  7. Suppression is real (history marker): stripping the inline marker (in
     tmp_path) makes the identical text FAIL.
  8. selfreference_control.md exits 0 -- the negative direction for the C-8
     self-reference exemption.
  9. Suppression is real (self-reference marker): stripping the
     recordscan:allow marker (in tmp_path) makes the identical text FAIL.
  10. A marker with the keyword but no reason text does NOT exempt: a bare
      `<!-- recordscan:history -->` (in tmp_path) FAILS.
  11. Never-vacuous: an explicitly empty FIRESTARTER_RECORDSCAN_TARGETS
      exits non-zero and prints the specific never-vacuous message.
  12. Fail-closed: a nonexistent named target exits non-zero and names the
      missing path.
  13. test_all_five_default_targets_exist_on_disk: the falsifiable form of
      the module docstring's "no arming branch is needed" claim (in-process
      import, the sole exception to the subprocess-only rule above).
  14. test_positional_argv_overrides_the_env_seam: documented precedence
      pinned against a future silent inversion.
  15. test_pass_line_names_every_scanned_file: pointing the checker at two
      clean fixtures at once produces one PASS: line naming both basenames.

Mechanism-3 tests (Plan 130-09, `recordscan:supersedes` retroactive
supersession -- see the module docstring's "Why a fourth mechanism exists"
paragraph in check_record_corrections.py):

  16. superseded_section_control.md (one of two occurrences named) still
      FAILs on the uncovered line -- the narrow-scoping negative direction.
  17. superseded_section_full_control.md (both occurrences named) exits 0
      -- the positive direction.
  18. Suppression is real: stripping the recordscan:supersedes marker from
      the full-control fixture (in tmp_path) makes BOTH lines FAIL again.
  19. An unrecognised/misspelled needle label in the marker exempts nothing
      -- fails closed on a typo rather than silently passing.
  20. A recordscan:supersedes marker with no reason text does not exempt,
      mirroring test 10's requirement for mechanisms 1/2.
"""

import os
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).parent
_CHECKER = _HERE / "check_record_corrections.py"


def _run_checker(targets=None, argv=None):
    """Invoke the checker as a real subprocess.

    `targets`, when not None, sets FIRESTARTER_RECORDSCAN_TARGETS to that
    exact string (so the empty string is reachable, per test 11) -- when
    None, the env var is left absent from the child's environment entirely,
    reaching the "variable absent -> use real defaults" path."""
    env = {**os.environ}
    if targets is not None:
        env["FIRESTARTER_RECORDSCAN_TARGETS"] = targets
    else:
        env.pop("FIRESTARTER_RECORDSCAN_TARGETS", None)
    return subprocess.run(
        [sys.executable, str(_CHECKER), *(argv or [])],
        cwd=str(_HERE),
        capture_output=True,
        text=True,
        env=env,
    )


# ---------------------------------------------------------------------------
# Test 1: clean-pass baseline via the seam
# ---------------------------------------------------------------------------


def test_clean_record_control_exits_zero():
    result = _run_checker(targets="fixtures/clean_record_control.md")
    assert result.returncode == 0, (
        f"checker exited {result.returncode} on a clean fixture.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS:" in result.stdout


# ---------------------------------------------------------------------------
# Test 2: planted stale figure (anti-hollow)
# ---------------------------------------------------------------------------


def test_planted_stale_figure_flips_checker_to_failure():
    result = _run_checker(targets="fixtures/planted_stale_figure.md")
    assert result.returncode != 0, (
        f"checker exited 0 on a planted stale figure.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "FAIL:" in result.stdout
    assert "leonardo-headroom-2992" in result.stdout, (
        f"Expected the leonardo-headroom-2992 label in output but got:\n{result.stdout}"
    )


# ---------------------------------------------------------------------------
# Test 3: mislabeled block does not exempt
# ---------------------------------------------------------------------------


def test_mislabeled_block_flips_checker_to_failure():
    result = _run_checker(targets="fixtures/mislabeled_block.md")
    assert result.returncode != 0, (
        f"checker exited 0 on a mislabeled block (neutral bold lead-in must "
        f"not exempt).\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "FAIL:" in result.stdout
    assert "leonardo-headroom-2992" in result.stdout


# ---------------------------------------------------------------------------
# Test 4: labeled_correction_control.md negative direction (block path)
# ---------------------------------------------------------------------------


def test_labeled_correction_control_exits_zero():
    fixture_text = (_HERE / "fixtures" / "labeled_correction_control.md").read_text()
    assert "2992" in fixture_text, (
        "fixture must actually contain the needle for this test to prove "
        "suppression rather than mere absence"
    )
    result = _run_checker(targets="fixtures/labeled_correction_control.md")
    assert result.returncode == 0, (
        f"checker exited {result.returncode} on a properly labeled "
        f"correction block.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS:" in result.stdout


# ---------------------------------------------------------------------------
# Test 5: block suppression is real, not accidental
# ---------------------------------------------------------------------------


def test_block_suppression_is_real_not_accidental(tmp_path):
    """Relocate the needle line to ABOVE the block opener. Without this
    test, test 4 could pass merely because the needle pattern never matches
    this fixture's text at all, rather than because block-awareness
    actively suppressed a real match. This test proves suppression is real:
    moving the needle line outside the block makes the identical text
    FAIL."""
    original = (_HERE / "fixtures" / "labeled_correction_control.md").read_text()
    lines = original.splitlines()
    needle_idx = next(i for i, line in enumerate(lines) if "2992" in line)
    opener_idx = next(
        i for i, line in enumerate(lines) if line.startswith("**⚠ CORRECTION")
    )
    assert needle_idx > opener_idx, "fixture must start with needle inside the block"

    needle_line = lines.pop(needle_idx)
    lines.insert(opener_idx, needle_line)
    mutated = "\n".join(lines) + "\n"
    target = tmp_path / "mutated_correction_control.md"
    target.write_text(mutated)

    result = _run_checker(targets=str(target))
    assert result.returncode != 0, (
        "expected the mutated fixture (needle line moved above the block "
        "opener) to FAIL -- if it still passes, block-awareness in test 4 "
        f"cannot be distinguished from the pattern simply never matching.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "FAIL:" in result.stdout
    assert "leonardo-headroom-2992" in result.stdout


# ---------------------------------------------------------------------------
# Test 6: labeled_history_control.md negative direction (inline-history path)
# ---------------------------------------------------------------------------


def test_labeled_history_control_exits_zero():
    fixture_text = (_HERE / "fixtures" / "labeled_history_control.md").read_text()
    assert "2992" in fixture_text
    assert "recordscan:history" in fixture_text
    result = _run_checker(targets="fixtures/labeled_history_control.md")
    assert result.returncode == 0, (
        f"checker exited {result.returncode} on a properly marked history "
        f"line.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS:" in result.stdout


# ---------------------------------------------------------------------------
# Test 7: history-marker suppression is real, not accidental
# ---------------------------------------------------------------------------


def test_history_marker_suppression_is_real_not_accidental(tmp_path):
    original = (_HERE / "fixtures" / "labeled_history_control.md").read_text()
    assert "<!-- recordscan:history" in original
    mutated = original.replace(
        " <!-- recordscan:history true when written, preserved as accurate "
        "archive text per RESEARCH C-7 -->",
        "",
    )
    assert mutated != original, "the marker substring must actually be present to strip"
    target = tmp_path / "mutated_history_control.md"
    target.write_text(mutated)

    result = _run_checker(targets=str(target))
    assert result.returncode != 0, (
        "expected the mutated fixture (inline history marker stripped) to "
        f"FAIL.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "FAIL:" in result.stdout
    assert "leonardo-headroom-2992" in result.stdout


# ---------------------------------------------------------------------------
# Test 8: selfreference_control.md negative direction (C-8 exemption)
# ---------------------------------------------------------------------------


def test_selfreference_control_exits_zero():
    fixture_text = (_HERE / "fixtures" / "selfreference_control.md").read_text()
    assert "recordscan:allow" in fixture_text
    result = _run_checker(targets="fixtures/selfreference_control.md")
    assert result.returncode == 0, (
        f"checker exited {result.returncode} on a properly marked "
        f"self-reference line.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS:" in result.stdout


# ---------------------------------------------------------------------------
# Test 9: self-reference-marker suppression is real, not accidental
# ---------------------------------------------------------------------------


def test_selfreference_marker_suppression_is_real_not_accidental(tmp_path):
    original = (_HERE / "fixtures" / "selfreference_control.md").read_text()
    assert "<!-- recordscan:allow" in original
    mutated = original.replace(
        " <!-- recordscan:allow this line defines three of the needle "
        "table's own entries, exactly as ROADMAP.md:2468 does (RESEARCH C-8) -->",
        "",
    )
    assert mutated != original, "the marker substring must actually be present to strip"
    target = tmp_path / "mutated_selfreference_control.md"
    target.write_text(mutated)

    result = _run_checker(targets=str(target))
    assert result.returncode != 0, (
        "expected the mutated fixture (recordscan:allow marker stripped) "
        f"to FAIL.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "FAIL:" in result.stdout


# ---------------------------------------------------------------------------
# Test 10: a marker with the keyword but no reason text does not exempt
# ---------------------------------------------------------------------------


def test_bare_marker_with_no_reason_does_not_exempt(tmp_path):
    original = (_HERE / "fixtures" / "labeled_history_control.md").read_text()
    mutated = original.replace(
        "<!-- recordscan:history true when written, preserved as accurate "
        "archive text per RESEARCH C-7 -->",
        "<!-- recordscan:history -->",
    )
    assert mutated != original, "the full marker must actually be present to replace"
    assert "<!-- recordscan:history -->" in mutated
    target = tmp_path / "bare_marker.md"
    target.write_text(mutated)

    result = _run_checker(targets=str(target))
    assert result.returncode != 0, (
        "expected a bare recordscan:history marker (no stated reason) to "
        f"NOT exempt.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "FAIL:" in result.stdout
    assert "leonardo-headroom-2992" in result.stdout


# ---------------------------------------------------------------------------
# Test 11: never-vacuous on an explicitly empty target list
# ---------------------------------------------------------------------------


def test_never_vacuous_on_explicitly_empty_target_list():
    result = _run_checker(targets="")
    assert result.returncode != 0, (
        f"checker exited 0 with an explicitly empty target list.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS:" not in result.stdout
    assert "no scan targets resolved" in result.stdout, (
        f"Expected the never-vacuous message in output but got:\n{result.stdout}"
    )


# ---------------------------------------------------------------------------
# Test 12: fail-closed on a nonexistent scan target
# ---------------------------------------------------------------------------


def test_fail_closed_on_nonexistent_target():
    result = _run_checker(targets="fixtures/does_not_exist.md")
    assert result.returncode != 0, (
        f"checker exited 0 with a missing scan target.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "FAIL:" in result.stdout
    assert "not found on disk" in result.stdout, (
        f"Expected a not-found message in output but got:\n{result.stdout}"
    )


# ---------------------------------------------------------------------------
# Test 13: all five default targets exist on disk (falsifiable no-arming claim)
# ---------------------------------------------------------------------------


def test_all_five_default_targets_exist_on_disk():
    """The sole in-process import in this module: asserts all five
    `_DEFAULT_TARGETS` are files on disk, which is the falsifiable form of
    the module docstring's claim that no D-15-style arming branch is
    needed (all five targets always exist)."""
    import check_record_corrections as m

    assert len(m._DEFAULT_TARGETS) == 5
    for t in m._DEFAULT_TARGETS:
        assert os.path.isfile(t), f"expected default target to exist: {t}"


# ---------------------------------------------------------------------------
# Test 14: positional argv overrides the env seam (precedence pin)
# ---------------------------------------------------------------------------


def test_positional_argv_overrides_the_env_seam():
    result = _run_checker(
        targets="fixtures/planted_stale_figure.md",
        argv=["fixtures/clean_record_control.md"],
    )
    assert result.returncode == 0, (
        f"checker exited {result.returncode} even though argv should have "
        f"overridden the env seam.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS:" in result.stdout


# ---------------------------------------------------------------------------
# Test 15: PASS line names every scanned file (anti-skip)
# ---------------------------------------------------------------------------


def test_pass_line_names_every_scanned_file():
    result = _run_checker(
        targets=os.pathsep.join(
            [
                "fixtures/clean_record_control.md",
                "fixtures/labeled_correction_control.md",
            ]
        )
    )
    assert result.returncode == 0, (
        f"checker exited {result.returncode} on two clean/exempt controls.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "clean_record_control.md" in result.stdout
    assert "labeled_correction_control.md" in result.stdout, (
        f"Expected both basenames in the PASS: line but got:\n{result.stdout}"
    )


# ---------------------------------------------------------------------------
# Mechanism 3 (Plan 130-09): recordscan:supersedes retroactive supersession.
#
# `.planning/notes/py32f071-port-branch-state.md` is a dated D-05 append-only
# capture: stale lines in its ORIGINAL body cannot be edited or annotated
# in place, yet must still go green. Mechanisms 1/2 are both forward- or
# same-line-scoped and cannot reach backwards across an appended section, so
# this mechanism lets a trailing section declare "(needle label, line
# number)" pairs elsewhere in the SAME file as retroactively covered --
# scoped narrowly by requiring a real needle label AND an explicit,
# enumerated line-number list AND a stated reason (tests 19/20 below prove
# each guard independently).
# ---------------------------------------------------------------------------


def test_superseded_section_control_fails_on_the_uncovered_line_only():
    """superseded_section_control.md plants the SAME needle on two lines but
    its recordscan:supersedes marker names only one of them (line 12) --
    the narrow-scoping negative direction: naming one line must not exempt
    a sibling occurrence of the same label elsewhere in the file."""
    result = _run_checker(targets="fixtures/superseded_section_control.md")
    assert result.returncode != 0, (
        f"checker exited 0 on a fixture with a deliberately uncovered "
        f"occurrence.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "FAIL:" in result.stdout
    assert "superseded_section_control.md:14" in result.stdout, (
        f"expected the UNCOVERED line (14) to be named in the FAIL bucket:\n{result.stdout}"
    )
    assert "superseded_section_control.md:12" not in result.stdout, (
        f"the COVERED line (12) must not appear in the FAIL bucket -- mechanism 3 "
        f"exempted it, so only line 14 should surface:\n{result.stdout}"
    )


def test_superseded_section_full_control_exits_zero():
    """superseded_section_full_control.md names BOTH occurrences in one
    marker -- the positive direction."""
    fixture_text = (
        _HERE / "fixtures" / "superseded_section_full_control.md"
    ).read_text()
    assert "recordscan:supersedes" in fixture_text
    assert "lines=12,14" in fixture_text
    result = _run_checker(targets="fixtures/superseded_section_full_control.md")
    assert result.returncode == 0, (
        f"checker exited {result.returncode} on a fully-covered supersession "
        f"fixture.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS:" in result.stdout


def test_supersedes_marker_suppression_is_real_not_accidental(tmp_path):
    """Strip the recordscan:supersedes marker entirely from the full-control
    fixture. Without this test, the previous test could pass merely because
    the needle never matches this fixture's text at all, rather than
    because mechanism 3 actively exempted both lines. Stripping the marker
    must make BOTH lines FAIL again."""
    original = (
        _HERE / "fixtures" / "superseded_section_full_control.md"
    ).read_text()
    marker_line = (
        "Both claims above are corrected: the imaginary branches are now 0 "
        "behind. <!-- recordscan:supersedes needle=branches-27-behind "
        "lines=12,14 reason: fixture proves mechanism 3 retroactively "
        "exempts every named line in one marker, not just the first -->"
    )
    assert marker_line in original, "the full marker line must actually be present to strip"
    mutated = original.replace(
        marker_line,
        "Both claims above are corrected: the imaginary branches are now 0 behind.",
    )
    assert mutated != original
    target = tmp_path / "mutated_full_control_no_marker.md"
    target.write_text(mutated)

    result = _run_checker(targets=str(target))
    assert result.returncode != 0, (
        "expected the mutated fixture (recordscan:supersedes marker stripped) "
        f"to FAIL on both lines.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "FAIL:" in result.stdout
    assert ":12" in result.stdout
    assert ":14" in result.stdout


def test_supersedes_marker_with_unknown_needle_label_does_not_exempt(tmp_path):
    """A misspelled/unrecognised needle= label in the marker must exempt
    NOTHING -- fails closed on a typo rather than silently passing, per the
    module docstring's guard (a). This is exactly the shape of failure this
    milestone's research kept finding elsewhere (fail-open on a renamed/
    misspelled subject), so it gets its own explicit proof here."""
    original = (
        _HERE / "fixtures" / "superseded_section_full_control.md"
    ).read_text()
    assert "needle=branches-27-behind" in original
    mutated = original.replace(
        "needle=branches-27-behind", "needle=branches-27-behnid"
    )
    assert mutated != original
    target = tmp_path / "mutated_full_control_bad_label.md"
    target.write_text(mutated)

    result = _run_checker(targets=str(target))
    assert result.returncode != 0, (
        "expected a misspelled needle label to exempt nothing (both lines "
        f"FAIL).\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "FAIL:" in result.stdout
    assert ":12" in result.stdout
    assert ":14" in result.stdout


def test_supersedes_marker_with_no_reason_does_not_exempt(tmp_path):
    """A recordscan:supersedes marker with the needle/lines fields present
    but no reason text does NOT exempt -- mirrors test 10's requirement for
    mechanisms 1/2: an exemption with no stated reason is the fail-open
    shape this milestone keeps finding, and mechanism 3 must not reintroduce
    it."""
    original = (
        _HERE / "fixtures" / "superseded_section_full_control.md"
    ).read_text()
    marker_full = (
        "<!-- recordscan:supersedes needle=branches-27-behind lines=12,14 "
        "reason: fixture proves mechanism 3 retroactively exempts every "
        "named line in one marker, not just the first -->"
    )
    assert marker_full in original
    mutated = original.replace(
        marker_full,
        "<!-- recordscan:supersedes needle=branches-27-behind lines=12,14 -->",
    )
    assert mutated != original
    target = tmp_path / "mutated_full_control_no_reason.md"
    target.write_text(mutated)

    result = _run_checker(targets=str(target))
    assert result.returncode != 0, (
        "expected a bare recordscan:supersedes marker (no stated reason) to "
        f"NOT exempt.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "FAIL:" in result.stdout
    assert ":12" in result.stdout
    assert ":14" in result.stdout
