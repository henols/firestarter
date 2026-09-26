#!/usr/bin/env python3
"""
pytest coverage for check_dead05_phrasing.py -- OQ-5's whole proof burden.

The tool is BUILT in Phase 155 plan 03 and RUN against the real, complete
corpus only in plan 06, after plans 04-05 have authored the artefacts the
corpus still lacks today. Every property the requirement names is therefore
proven here against committed and synthetic fixtures, not against the real
corpus, and several tests exist purely to prove the proofs are
DISCRIMINATING rather than accidentally green.

Tests (leg name -- expected exit code / requirement or anti-vacuity property
discharged):

  1. test_planted_violation_exits_one_and_names_the_paragraph -- exit 1 /
     DEAD-05 negative half, T-155-08. The committed planted fixture's first
     paragraph is flagged, naming the file and its start line.
  2. test_paragraph_not_naming_the_function_is_not_flagged -- exit 1 (same
     run) / T-155-11, anti-noise. The fixture's third paragraph carries a
     forbidden word but no trigger token, and must not add a second
     violation.
  3. test_clean_corpus_with_the_phrasing_exits_zero -- exit 0 / DEAD-05 both
     halves. Proves exit 0 is reachable at all.
  4. test_below_paragraph_floor_exits_two -- exit 2 / T-155-09, anti-vacuity.
     Proves an emptied or shrunken corpus cannot report success.
  5. test_missing_required_positive_target_exits_two -- exit 2 / DEAD-05
     positive half, OQ-5. A required target absent from disk is
     infrastructure, not a pass.
  6. test_present_target_without_the_phrasing_exits_one -- exit 1 / DEAD-05
     positive half, OQ-5. A required target that exists but lacks the
     mandated phrasing is a real failure, not a pass.
  7. test_malformed_argv_exits_two -- exit 2 / fail-closed argument parsing.
  8. test_tool_source_does_not_contain_its_own_needles -- n/a (source) /
     proves the concatenation trick in _forbidden_needles is actually in
     force, in both this module and the tool.
  9. test_this_module_cannot_be_silently_skipped -- n/a (source) / the
     concatenation-built-needle anti-skip leg, same technique as
     firestarter/tests/test_write_path_source_contract_v131.py.

`_HERE` IS correct in this file -- the ban (155-dead05-phrasing-corpus.md
section 5 / TOOLS_DIR_REL) is on the TOOL deriving its OWN scan root from
its own location as a default with no override; this test module locating
its sibling fixture is unrelated.
"""

import shutil
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_TOOL = _HERE / "check_dead05_phrasing.py"
_FIXTURES = _HERE / "fixtures"
_FIXTURE = _FIXTURES / "planted_dead05_phrasing_violation.md"

if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import check_dead05_phrasing as cd  # noqa: E402 -- sys.path is prepared above

_PHASE_DIR = "155-dead-weight-removal-the-heap-allocator-and-the-64-bit-runtim"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _run(argv):
    return subprocess.run(
        [sys.executable, str(_TOOL), *argv],
        capture_output=True,
        text=True,
        check=False,
    )


def _shown(result, expected):
    return (
        f"Expected exit {expected} but got {result.returncode}.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _clean_paragraph(n):
    """An in-scope, non-violating paragraph: names the trigger token and
    contains none of the six forbidden phrasings."""
    return (
        f"Clean paragraph {n} names `rurp_read_voltage_mv` and makes no "
        "coverage claim beyond what the committed host-side oracle "
        "actually establishes."
    )


def _target_paragraph():
    """An in-scope paragraph carrying the mandated correct phrasing --
    doubles as both a corpus paragraph and a required-target satisfier."""
    return "This paragraph names `rurp_read_voltage_mv`: " + cd.CORRECT_PHRASING


def _build_clean_corpus(tmp_path, *, omit_target=None, blank_target=None):
    """A synthetic corpus with 7 in-scope paragraphs (>= PARAGRAPH_FLOOR)
    and all four required-positive targets satisfied by default.

    omit_target / blank_target select one of "validation", "after_figures",
    "rurp_common", "oracle" to, respectively, not create that target file at
    all, or create it with a clean paragraph but WITHOUT the mandated
    phrasing. Every other clean paragraph stays present either way, so the
    floor is never the confounding variable when a target is broken on
    purpose.
    """
    meta = tmp_path / "meta"
    fw = tmp_path / "fw"
    phase_dir = meta / ".planning" / "phases" / _PHASE_DIR
    v133_dir = meta / ".planning" / "v1.33"
    boards_dir = fw / "src" / "boards"
    oracle_dir = fw / "tests"
    phase_dir.mkdir(parents=True)
    v133_dir.mkdir(parents=True)
    boards_dir.mkdir(parents=True)
    oracle_dir.mkdir(parents=True)

    _write(
        phase_dir / "155-09-PLAN.md",
        _clean_paragraph(1) + "\n\n" + _clean_paragraph(2) + "\n",
    )
    _write(
        v133_dir / "155-scratch.md",
        _clean_paragraph(3) + "\n\n" + _clean_paragraph(4) + "\n",
    )

    if omit_target != "validation":
        body = (
            "placeholder text with no trigger token"
            if blank_target == "validation"
            else "This file defines the forbidden list. " + cd.CORRECT_PHRASING
        )
        _write(phase_dir / "155-VALIDATION.md", body + "\n")

    if omit_target != "after_figures":
        body = _clean_paragraph(5)
        if blank_target != "after_figures":
            body += "\n\n" + _target_paragraph()
        _write(v133_dir / "155-after-figures.md", body + "\n")

    if omit_target != "rurp_common":
        body = _clean_paragraph(6)
        if blank_target != "rurp_common":
            body += "\n\n" + _target_paragraph()
        _write(boards_dir / "rurp_common.cpp", body + "\n")

    if omit_target != "oracle":
        body = _clean_paragraph(7)
        if blank_target != "oracle":
            body += "\n\n" + _target_paragraph()
        _write(oracle_dir / "test_voltage_reformulation_oracle.py", body + "\n")

    return meta, fw


# ---------------------------------------------------------------------------
# 1-2. The committed planted violation
# ---------------------------------------------------------------------------
def _run_against_planted_fixture(tmp_path):
    meta = tmp_path / "meta"
    fw = tmp_path / "fw"
    v133_dir = meta / ".planning" / "v1.33"
    v133_dir.mkdir(parents=True)
    fw.mkdir()
    shutil.copyfile(_FIXTURE, v133_dir / "155-planted-check.md")
    return _run(["--corpus-root", str(meta), "--fw-root", str(fw)])


def test_planted_violation_exits_one_and_names_the_paragraph(tmp_path):
    result = _run_against_planted_fixture(tmp_path)
    assert result.returncode != 0
    assert result.returncode == 1, _shown(result, 1)
    assert "FAIL:" in result.stdout, result.stdout
    assert "155-planted-check.md:9" in result.stdout, result.stdout


def test_paragraph_not_naming_the_function_is_not_flagged(tmp_path):
    result = _run_against_planted_fixture(tmp_path)
    assert result.returncode == 1, _shown(result, 1)
    # Exactly one violation reported: paragraph one's forbidden word.
    # Paragraph three carries the same forbidden word but no trigger token,
    # so if the trigger scoping were incidental rather than real, a second
    # violation line would appear here.
    assert result.stdout.count(" -- needle ") == 1, result.stdout
    assert "Paragraph three" not in result.stdout, result.stdout


# ---------------------------------------------------------------------------
# 3. Exit 0 is reachable
# ---------------------------------------------------------------------------
def test_clean_corpus_with_the_phrasing_exits_zero(tmp_path):
    meta, fw = _build_clean_corpus(tmp_path)
    result = _run(["--corpus-root", str(meta), "--fw-root", str(fw)])
    assert result.returncode == 0, _shown(result, 0)
    assert "PASS:" in result.stdout, result.stdout
    for name in (
        "155-09-PLAN.md",
        "155-scratch.md",
        "155-after-figures.md",
        "rurp_common.cpp",
        "test_voltage_reformulation_oracle.py",
    ):
        assert name in result.stdout, result.stdout


# ---------------------------------------------------------------------------
# 4. The floor cannot be passed vacuously
# ---------------------------------------------------------------------------
def test_below_paragraph_floor_exits_two(tmp_path):
    meta = tmp_path / "meta"
    fw = tmp_path / "fw"
    phase_dir = meta / ".planning" / "phases" / _PHASE_DIR
    v133_dir = meta / ".planning" / "v1.33"
    boards_dir = fw / "src" / "boards"
    oracle_dir = fw / "tests"
    phase_dir.mkdir(parents=True)
    v133_dir.mkdir(parents=True)
    boards_dir.mkdir(parents=True)
    oracle_dir.mkdir(parents=True)

    # Only 4 in-scope paragraphs total -- below PARAGRAPH_FLOOR (6) -- while
    # every required target is present and correct, so ONLY the floor trips.
    _write(phase_dir / "155-09-PLAN.md", _clean_paragraph(1) + "\n")
    _write(phase_dir / "155-VALIDATION.md", "reference only, no trigger token\n")
    _write(v133_dir / "155-after-figures.md", _target_paragraph() + "\n")
    _write(boards_dir / "rurp_common.cpp", _target_paragraph() + "\n")
    _write(oracle_dir / "test_voltage_reformulation_oracle.py", _target_paragraph() + "\n")

    result = _run(["--corpus-root", str(meta), "--fw-root", str(fw)])
    assert result.returncode == 2, _shown(result, 2)
    assert "ERROR" in result.stdout, result.stdout
    assert "PARAGRAPH_FLOOR" in result.stdout, result.stdout
    assert "4" in result.stdout, result.stdout


# ---------------------------------------------------------------------------
# 5-6. The positive half is real, not decorative
# ---------------------------------------------------------------------------
def test_missing_required_positive_target_exits_two(tmp_path):
    meta, fw = _build_clean_corpus(tmp_path, omit_target="oracle")
    result = _run(["--corpus-root", str(meta), "--fw-root", str(fw)])
    assert result.returncode == 2, _shown(result, 2)
    assert "ERROR" in result.stdout, result.stdout
    assert "test_voltage_reformulation_oracle.py" in result.stdout, result.stdout


def test_present_target_without_the_phrasing_exits_one(tmp_path):
    meta, fw = _build_clean_corpus(tmp_path, blank_target="rurp_common")
    result = _run(["--corpus-root", str(meta), "--fw-root", str(fw)])
    assert result.returncode == 1, _shown(result, 1)
    assert "FAIL:" in result.stdout, result.stdout
    assert "rurp_common.cpp" in result.stdout, result.stdout


# ---------------------------------------------------------------------------
# 7. Malformed argv fails closed
# ---------------------------------------------------------------------------
def test_malformed_argv_exits_two():
    result = _run(["--not-a-real-flag"])
    assert result.returncode == 2, _shown(result, 2)
    result_missing_value = _run(["--corpus-root"])
    assert result_missing_value.returncode == 2, _shown(result_missing_value, 2)


# ---------------------------------------------------------------------------
# 8-9. Structural self-checks
# ---------------------------------------------------------------------------
def test_tool_source_does_not_contain_its_own_needles():
    """Coverage 8 -- the concatenation trick in _forbidden_needles is
    actually in force: neither the tool's own source nor this test module's
    own source contains any of the six forbidden phrasings as a literal,
    contiguous substring."""
    tool_text = _TOOL.read_text(encoding="utf-8").lower()
    own_text = Path(__file__).read_text(encoding="utf-8").lower()
    for needle in cd._forbidden_needles():
        assert needle not in tool_text, (
            f"{needle!r} appears literally in {_TOOL} -- the concatenation "
            "trick has been silently undone"
        )
        assert needle not in own_text, (
            f"{needle!r} appears literally in this test module's own "
            "source"
        )


def test_this_module_cannot_be_silently_skipped():
    """Coverage 9 -- this module's own source contains no runtime
    skip-bypass call, no skip-marker decorator, and no dependency-skip call
    anywhere, matching the convention in
    firestarter/tests/test_write_path_source_contract_v131.py. The three
    needle strings are built via concatenation so this very assertion's own
    source cannot match its own check."""
    own_text = Path(__file__).read_text(encoding="utf-8")
    skip_call = "pytest" + ".skip"
    skipif_marker = "mark" + ".skipif"
    dependency_skip_call = "importor" + "skip"
    assert skip_call not in own_text, (
        "expected no " + skip_call + " call anywhere in this module -- a "
        "missing or broken corpus must FAIL, never SKIP"
    )
    assert skipif_marker not in own_text, (
        "expected no @pytest." + skipif_marker + " decorator anywhere in "
        "this module"
    )
    assert ("pytest." + dependency_skip_call) not in own_text, (
        "expected no pytest." + dependency_skip_call + " call anywhere in "
        "this module"
    )
