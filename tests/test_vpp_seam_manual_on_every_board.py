"""
Project Name: Firestarter
Copyright (c) 2024 Henrik Olsson

Permission is hereby granted under MIT license.

Phase 125 Plan 02 -- VPP-02's parametrized compile-and-run proof that the VPP
control seam refuses (returns MANUAL_ADJUSTMENT_REQUIRED) on every board
macro-set this branch supports.

Requirements: VPP-02
Decisions covered: D-01, D-02, D-03, D-04, D-05, D-06, D-07, D-08

RURP_HAS_VPP_DAC has exactly two consumers: the header's `#if !defined(...)`
test in include/rurp_vpp.h, and the source file's `#if RURP_HAS_VPP_DAC`
value test in src/rurp_vpp.cpp. This module is what proves each of those two
guards can actually fire, rather than assuming it -- the direct antidote to
the hollow-guard shape Phase 124 D-14 had to restructure, where a `#define`
sat roughly thirty lines above the `#if` that tested it and the guard could
not fire under any build configuration.

What the four board legs below actually prove: the seam consults exactly two
macros -- __AVR__ and RURP_HAS_VPP_DAC -- and nothing in it distinguishes Uno
from Leonardo from uno328pb. The four legs prove uniformity across ONE
compiler-supplied AVR fact plus ONE explicit ARM declaration, not four
independent per-board facts. The real AVR-cross-compiler resolution is
discharged by the three `pio run` builds Plan 125-04 performs, not by this
module -- do not let a reader infer more than that from the four legs below.

This module executes in NO CI leg on this branch: `pytest tests/ -v` appears
only in build.yml (push/PR to main) and beta-build.yml (push to beta) --
neither fires on the firmware milestone branch, and py32f071.yml has no
pytest step at all. The local run recorded in this phase's evidence artifact
is the only evidence this module's assertions were ever exercised.

Self-contained path resolution below -- NOT in conftest.py (firestarter/tests/
has no conftest.py anywhere in the repo, and none of pytest.ini,
pyproject.toml, setup.cfg or tox.ini exist either; a recorded house-rule
pattern decision, not an omission). Stdlib and pytest only.

Coverage:
  1. test_manual_control_on_every_board_macro_set -- one parametrized test,
     four board macro-sets (uno, leonardo, uno328pb, py32f071): compiles AND
     runs the seam, asserting compile exit 0, zero stderr bytes under
     -Wall -Wextra, run exit 0, and the two values parsed from stdout equal
     the manual mode (0) and the manual-adjustment-required result (1).
  2. test_forced_capability_macro_fails_closed_in_the_source -- D-03 via
     RESEARCH C-4: forcing RURP_HAS_VPP_DAC=1 while compiling
     src/rurp_vpp.cpp produces a non-zero compile exit carrying that file's
     own #error text; the header alone cannot reject this value (measured
     exit 0), so this leg is what makes the harness non-vacuous.
  3. test_unset_and_non_avr_fails_closed_in_the_header -- D-08: compiling
     with neither __AVR__ nor an explicit RURP_HAS_VPP_DAC defined produces
     a non-zero compile exit carrying include/rurp_vpp.h's own #error text.
"""

import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
_INCLUDE = _REPO_ROOT / "include"
_SEAM_HEADER = _INCLUDE / "rurp_vpp.h"
_SEAM_SRC = _REPO_ROOT / "src" / "rurp_vpp.cpp"

_EXPECTED_MODE_MANUAL = 0
_EXPECTED_RESULT_MANUAL_REQUIRED = 1

# The four board macro-sets, hardcoded literals (D-04) -- kept honest by the
# drift leg (Coverage 4, added in this module's second authoring task) that
# asserts each anchor below is still literally present in the real build
# config. Values per RESEARCH's measured prototype.
_BOARD_MACRO_SETS = [
    pytest.param(
        ("__AVR__", "ARDUINO_AVR_UNO", 'RURP_BOARD_NAME="uno"', "SERIAL_ON_IO"),
        id="uno",
    ),
    pytest.param(
        (
            "__AVR__",
            "ARDUINO_AVR_LEONARDO",
            'RURP_BOARD_NAME="leonardo"',
            "DATA_BUFFER_SIZE=1024",
        ),
        id="leonardo",
    ),
    pytest.param(
        (
            "__AVR__",
            "ARDUINO_AVR_ATmega328PB",
            'RURP_BOARD_NAME="uno328pb"',
            "SERIAL_ON_IO",
        ),
        id="uno328pb",
    ),
    pytest.param(
        (
            "RURP_PLATFORM_PY32F071=1",
            "RURP_HAS_VPP_DAC=0",
            'RURP_BOARD_NAME="py32f071"',
        ),
        id="py32f071",
    ),
]


def _resolve_compiler():
    """Resolve the host C++ compiler, fail-closed.

    Deliberately never bypassed via any decorator or runtime call that would
    mark this outcome as skipped, anywhere in this module: doing so would
    recreate the exact BASE-02/BASE-03 absence-proxy failure class this
    milestone's Phase 123 removed. If $CXX (or 'g++') cannot be resolved via
    shutil.which, this raises via a plain assert, which the test runner
    reports as a FAILURE, never a skipped outcome. This module's harness
    runs in NO CI leg on this branch (RESEARCH C-7) -- the local run is the
    only evidence, which makes the fail-closed contract here even more
    load-bearing than in the CI-covered precedent.
    """
    compiler = shutil.which(os.environ.get("CXX", "g++"))
    assert compiler is not None, (
        "host C++ compiler not found on PATH (checked $CXX, falling back to "
        "'g++'). This must FAIL the suite, never be silently skipped -- no "
        "embedded toolchain is invoked here."
    )
    return compiler


def _write_shim_tu(tmp_path):
    """Write the measured RESEARCH shim into tmp_path, fresh every call --
    never a committed fixture translation unit (D-03 declined one). Includes
    rurp_vpp.h and <cstdio>, and its main prints the control mode and the
    result of rurp_set_vpp_target_mv(12000, 200, 50) in the exact form
    'mode=%d result=%d', each cast to int, then calls
    rurp_disable_vpp_control() and returns 0 unconditionally."""
    tu_path = tmp_path / "vpp_seam_main.cpp"
    tu_path.write_text(
        '#include "rurp_vpp.h"\n'
        "#include <cstdio>\n"
        "int main(void) {\n"
        '    printf("mode=%d result=%d\\n", (int)rurp_vpp_control_mode(),\n'
        "           (int)rurp_set_vpp_target_mv(12000, 200, 50));\n"
        "    rurp_disable_vpp_control();\n"
        "    return 0;\n"
        "}\n"
    )
    return tu_path


def _compile(compiler, defines, sources, output_path):
    """Compile (and, when a real main is present, link) the given source
    files with the given macro definitions into a real binary at
    output_path. List argv only, never a shell; always passes
    -std=gnu++17 -Wall -Wextra and the include/ path. A definition whose
    value contains double quotes needs no extra escaping here -- there is
    no shell in the way, so the literal Python string is exactly what the
    compiler receives as argv."""
    argv = [compiler, "-std=gnu++17", "-Wall", "-Wextra", "-I", str(_INCLUDE)]
    argv += [f"-D{define}" for define in defines]
    argv += [str(source) for source in sources]
    argv += ["-o", str(output_path)]
    return subprocess.run(argv, capture_output=True, text=True)


def _run_binary(binary_path):
    """Execute the compiled binary as a second subprocess, list argv,
    capturing output. The seam's result value crosses this process boundary
    on stdout, never this run's exit code (Trap 2): 1 is also the exit code
    of a compile failure, a link failure and a crash, so returning it from
    main would make the correct answer indistinguishable from every
    failure mode."""
    return subprocess.run([str(binary_path)], capture_output=True, text=True)


def _expected_header_error_text():
    """Read the #error message out of include/rurp_vpp.h at test time,
    rather than hardcoding it a second time here -- a literal that could
    silently desync from the real header on a future edit. Scoped to this
    one file: the header and src/rurp_vpp.cpp each carry a DIFFERENT #error
    message, so this "exactly one directive" assertion must never be
    reused across both files."""
    text = _SEAM_HEADER.read_text()
    m = re.search(r'#\s*error\s+"([^"]*)"', text)
    assert m, (
        f"expected exactly one #error directive with a quoted message in "
        f"{_SEAM_HEADER}.\nGot:\n{text}"
    )
    return m.group(1)


def _expected_source_error_text():
    """Read the #error message out of src/rurp_vpp.cpp at test time, rather
    than hardcoding it a second time here. Scoped to this one file -- see
    _expected_header_error_text's docstring for why the two are separate
    helpers rather than one shared "exactly one" assertion."""
    text = _SEAM_SRC.read_text()
    m = re.search(r'#\s*error\s+"([^"]*)"', text)
    assert m, (
        f"expected exactly one #error directive with a quoted message in "
        f"{_SEAM_SRC}.\nGot:\n{text}"
    )
    return m.group(1)


@pytest.mark.parametrize("defines", _BOARD_MACRO_SETS)
def test_manual_control_on_every_board_macro_set(tmp_path, defines):
    """Coverage 1 -- one parametrized test asserting the seam refuses
    (control mode MANUAL, result MANUAL_ADJUSTMENT_REQUIRED) across all
    four board macro-sets in one run (ROADMAP Criterion 2), compiled AND
    run -- never a single-board spot check. Parses the result from stdout,
    never the run subprocess's exit code (Trap 2)."""
    compiler = _resolve_compiler()
    tu_path = _write_shim_tu(tmp_path)
    binary_path = tmp_path / "seam_under_test"

    compile_result = _compile(compiler, defines, (tu_path, _SEAM_SRC), binary_path)
    assert compile_result.returncode == 0, (
        f"expected a clean compile for board macro-set {defines!r}.\n"
        f"stdout:\n{compile_result.stdout}\nstderr:\n{compile_result.stderr}"
    )
    assert compile_result.stderr == "", (
        f"expected zero bytes of -Wall -Wextra warning output for board "
        f"macro-set {defines!r}.\n"
        f"stdout:\n{compile_result.stdout}\nstderr:\n{compile_result.stderr}"
    )

    run_result = _run_binary(binary_path)
    assert run_result.returncode == 0, (
        f"expected the compiled binary to run cleanly for board macro-set "
        f"{defines!r}.\n"
        f"stdout:\n{run_result.stdout}\nstderr:\n{run_result.stderr}"
    )

    match = re.match(r"mode=(\d+) result=(\d+)\s*$", run_result.stdout)
    assert match, (
        f"expected stdout of the form 'mode=<int> result=<int>' for board "
        f"macro-set {defines!r}.\n"
        f"stdout:\n{run_result.stdout!r}\nstderr:\n{run_result.stderr!r}"
    )
    mode, result = int(match.group(1)), int(match.group(2))
    assert mode == _EXPECTED_MODE_MANUAL, (
        f"expected rurp_vpp_control_mode() == RURP_VPP_CONTROL_MANUAL "
        f"({_EXPECTED_MODE_MANUAL}) for board macro-set {defines!r}, got "
        f"mode={mode}.\nstdout:\n{run_result.stdout}"
    )
    assert result == _EXPECTED_RESULT_MANUAL_REQUIRED, (
        f"expected rurp_set_vpp_target_mv() == "
        f"RURP_VPP_MANUAL_ADJUSTMENT_REQUIRED "
        f"({_EXPECTED_RESULT_MANUAL_REQUIRED}) for board macro-set "
        f"{defines!r}, got result={result}.\nstdout:\n{run_result.stdout}"
    )


def test_forced_capability_macro_fails_closed_in_the_source(tmp_path):
    """Coverage 2 -- D-03 via RESEARCH C-4: the header's
    `#if !defined(...)` guard cannot reject an explicitly forced
    RURP_HAS_VPP_DAC=1 (measured: exits 0 with only the header present), so
    this leg compiles src/rurp_vpp.cpp itself -- whose own, separately
    authored #error is the one that must fire. This is what makes the
    harness non-vacuous: a header-only leg would pass vacuously and the
    "the macro is genuinely consulted" argument would evaporate."""
    compiler = _resolve_compiler()
    expected_text = _expected_source_error_text()
    binary_path = tmp_path / "forced_capability"

    result = _compile(compiler, ("__AVR__", "RURP_HAS_VPP_DAC=1"), (_SEAM_SRC,), binary_path)

    assert result.returncode != 0, (
        "expected a non-zero compile exit with RURP_HAS_VPP_DAC forced to 1 "
        "while compiling src/rurp_vpp.cpp (the header alone cannot reject "
        f"this value).\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert expected_text in result.stderr, (
        f"expected src/rurp_vpp.cpp's own #error text in stderr.\n"
        f"Expected substring: {expected_text!r}\nGot stderr:\n{result.stderr}"
    )


def test_unset_and_non_avr_fails_closed_in_the_header(tmp_path):
    """Coverage 3 -- D-08: with neither __AVR__ nor an explicit
    RURP_HAS_VPP_DAC defined, include/rurp_vpp.h's #else arm must fire.
    This is the arm every native translation unit would reach were the
    seam ever included from include/rurp_shield.h (measured: pio test
    -e native goes to 17 suites / 0 succeeded) -- this leg is the standing
    explanation for why that include does not exist."""
    compiler = _resolve_compiler()
    tu_path = _write_shim_tu(tmp_path)
    expected_text = _expected_header_error_text()
    binary_path = tmp_path / "unset_non_avr"

    result = _compile(compiler, (), (tu_path,), binary_path)

    assert result.returncode != 0, (
        "expected a non-zero compile exit with neither __AVR__ nor "
        "RURP_HAS_VPP_DAC defined.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert expected_text in result.stderr, (
        f"expected include/rurp_vpp.h's own #error text in stderr.\n"
        f"Expected substring: {expected_text!r}\nGot stderr:\n{result.stderr}"
    )
