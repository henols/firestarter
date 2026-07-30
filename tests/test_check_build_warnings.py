"""
Project Name: Firestarter
Copyright (c) 2024 Henrik Olsson

Permission is hereby granted under MIT license.

Phase 123 Plan 03 — the BASE-08 anti-hollow pairing for scripts/check_build_warnings.py.

Requirements: BASE-06, BASE-08
Decisions covered: D-13, D-14

Coverage:
  1. Real compiler still emits the diagnostic — planted_build_warnings_macro_redef.cpp
     compiled with a real, resolved host compiler in syntax-only mode; MACRO_REDEF_RE
     matches the captured stderr and the captured `macro` group equals the fixture's
     distinctive name, derived from the fixture source at test time (never hardcoded
     as a second literal a re-plant could silently desync from).
  2. Clean control emits nothing — clean_build_warnings_no_redef.cpp compiles with
     zero `warning:` lines, proving the parser is discriminating rather than
     universally matching.
  3. The gate's parser consumes real compiler output end to end — the stderr
     captured in coverage 1 is fed to check_build_warnings.py through a temp log
     file and a `--log uno=...` argument; asserts non-zero exit and that the
     output names the offending macro. This is the compiler -> parser -> exit
     code half of D-14.
  4. Parser survives pio's own framing — MACRO_REDEF_RE and WARNING_LINE_RE are
     asserted directly against the committed captured_native_warnings_excerpt.log
     (real `pio test -e native` output, including its `Processing`/`Building...`
     preamble and the compiler's own `In file included from ...`/`note:` lines),
     proving the parser is not merely proven against a bare compiler invocation.
     This closes the gap D-14 records as open.
  5. AVR exact-zero fires — planted_build_warnings_avr_redef.log (one genuine
     redefinition inserted into a real uno build log) exits non-zero naming the
     env, the observed count (1) and the rule (0).
  6. AVR clean control passes — each of the three captured_build_*.log files
     exits 0 with a PASS: line.
  7. Native watermark fires — planted_build_warnings_native_excess.log (363
     `warning:` lines against a 360 watermark) exits non-zero naming both the
     observed count and the watermark.
  8. Native clean control passes at the watermark — captured_test_native_summary.log
     is 123-01's truncated SUMMARY-tail capture, which carries 0 warning lines,
     not 360 (the 360 real warnings occur earlier in a `pio test` run, during
     compilation, and were never captured in that file — see 123-01-SUMMARY.md's
     "Native capture truncation point"). Asserting this file against the real
     360 watermark would therefore report the (correct, but here misleading)
     "352 below watermark" INFO arm rather than exercising the OK-at-watermark
     branch. This test instead points the gate at a temp baseline (via
     `--baseline`) whose native watermark is set to 0 — the actual count this
     truncated tail contains — proving the OK-at-exact-watermark arm fires.
     This adjustment is the one place 123-01 Task 2's truncation has a visible
     consequence in this plan; stating it here rather than silently working
     around it is deliberate (the whole point of this phase).
  9. Never-vacuous — no --log and no --rebuild exits non-zero with the
     never-vacuous message and prints no PASS:.
  10. Unknown env is a configuration error — a log supplied for an env absent
      from the baseline's warnings block exits exactly 2.

Fixture derivation record (single stated edit per planted fixture, diffable
against its named source):

  planted_build_warnings_avr_redef.log
    = captured_build_uno.log with ONE line inserted immediately after the
      "Compiling .pio/build/uno/src/proms/memory.cpp.o" line: the verbatim
      `.pio/libdeps/native/ArduinoFake/src/arduino/pgmspace.h:34:9: warning:
      "PSTR" redefined` diagnostic, copied character-for-character from
      captured_native_warnings_excerpt.log (a genuine compiler line, not
      invented text).

  planted_build_warnings_native_excess.log
    = captured_test_native_summary.log with 361 synthetic `warning:` lines
      prepended before the untouched 21-line SUMMARY tail (355 macro-
      redefinition-shaped, using distinctive `SYNTHETIC_MACRO_NNNN` names
      that cannot collide with any real project or ArduinoFake macro; 6
      non-macro-shaped, an unused-variable diagnostic form). None of these
      361 lines were emitted by a real compiler. Because
      captured_test_native_summary.log itself carries 0 warning lines (see
      coverage 8 above), reaching the required >360 total meant appending
      the full excess rather than "a small number" of lines on top of an
      already-near-360 base, as this plan's task text assumed — recorded
      here as the deviation, per the same house convention 123-01-SUMMARY.md
      used for its own truncation-framing correction.

This module never imports check_build_warnings for its exit-code-level
assertions (coverage 3, 5, 6, 7, 8, 9, 10): every one of those invokes the
script as a real subprocess with a LIST argv (never shell=True), so a
passing suite proves check_build_warnings.py itself fails the build on a
real violation, not merely that this test module asserts it should. Only
the two parser/regex-level checks (coverage 1's `.search()` and coverage 4)
import the module directly, to assert against MACRO_REDEF_RE /
WARNING_LINE_RE as objects rather than against a CLI's exit code.

No `pio` invocation happens anywhere in this module: every log parsed is a
committed fixture (`captured_*` for the clean-control arms,
`planted_build_warnings_*` for one deliberate violation per exit-taxonomy
arm). Paying a cold-toolchain `pio` cost inside pytest would make this
suite non-hermetic and slow.

Self-contained path resolution below — NOT in conftest.py (firestarter/tests/
has no conftest.py anywhere in the repo; a recorded house-rule pattern
decision per test_update_version.py's own comment, not an omission).
Stdlib and pytest only.
"""

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
_CHECKER = _REPO_ROOT / "scripts" / "check_build_warnings.py"
_FIXTURES = _HERE / "fixtures"
_BASELINE = _REPO_ROOT / "scripts" / "baseline" / "size_baseline.json"

# Self-contained sys.path injection -- NOT in conftest.py per the house-rule
# precedent recorded in test_update_version.py. Only used by the two
# parser/regex-level tests (coverage 1, 4); every exit-code-level test below
# invokes scripts/check_build_warnings.py as a real subprocess instead.
sys.path.insert(0, str(_REPO_ROOT / "scripts"))
import check_build_warnings  # noqa: E402


def _resolve_compiler():
    """Resolve the host C++ compiler, fail-closed.

    Deliberately never bypassed via any decorator or runtime call that would
    mark this outcome as skipped, anywhere in this module: doing so would
    recreate the exact BASE-02/BASE-03 absence-proxy failure class inside
    the very phase that removes it. If $CXX (or 'g++') cannot be resolved
    via shutil.which, this raises via a plain assert, which the test runner
    reports as a FAILURE, never a skipped outcome.
    """
    compiler = shutil.which(os.environ.get("CXX", "g++"))
    assert compiler is not None, (
        "host C++ compiler not found on PATH (checked $CXX, falling back to "
        "'g++'). This must FAIL the suite, never be silently skipped -- the "
        "AVR cross-compiler is never invoked here: both firmware CI workflows "
        "run `pytest tests/ -v` BEFORE `pio run` installs the AVR toolchain."
    )
    return compiler


def _fixture_macro_name():
    """Return the distinctive macro name #define'd by
    planted_build_warnings_macro_redef.cpp, derived from the fixture's own
    source text at test time rather than hardcoded as a second literal a
    future re-plant could silently desync from."""
    text = (_FIXTURES / "planted_build_warnings_macro_redef.cpp").read_text()
    m = re.search(r"#define\s+(\S+)", text)
    assert m, f"expected at least one #define directive in the fixture.\nGot:\n{text}"
    return m.group(1)


def _compile_fixture(compiler, fixture_name):
    """Compile a fixture in syntax-only mode with the resolved host compiler.
    Returns captured stderr text (where gcc/g++ emit warnings)."""
    result = subprocess.run(
        [compiler, "-fsyntax-only", str(_FIXTURES / fixture_name)],
        capture_output=True,
        text=True,
    )
    return result.stderr


def _run_checker(argv=None, env_overrides=None):
    """Invoke check_build_warnings.py as a real subprocess (list argv, never
    shell=True). `env_overrides` merges into the child's environment on top
    of the current process environment -- used by coverage 8's temp-baseline
    test to set FIRESTARTER_SIZE_BASELINE without mutating this process."""
    env = {**os.environ, **(env_overrides or {})}
    return subprocess.run(
        [sys.executable, str(_CHECKER), *(argv or [])],
        cwd=str(_REPO_ROOT),
        capture_output=True,
        text=True,
        env=env,
    )


def test_real_compiler_emits_the_planted_diagnostic():
    """Coverage 1 — a real host compiler still emits the diagnostic the parser
    matches, and the captured macro name is the fixture's distinctive name."""
    compiler = _resolve_compiler()
    macro_name = _fixture_macro_name()
    stderr = _compile_fixture(compiler, "planted_build_warnings_macro_redef.cpp")

    m = check_build_warnings.MACRO_REDEF_RE.search(stderr)
    assert m, f"expected MACRO_REDEF_RE to match real compiler stderr.\nGot:\n{stderr}"
    assert m.group("macro") == macro_name, (
        f"expected the captured macro group to equal the fixture's own "
        f"#define'd name.\nGot:      {m.group('macro')!r}\n"
        f"Expected: {macro_name!r}"
    )


def test_clean_control_emits_nothing():
    """Coverage 2 — the paired clean control compiles with zero warnings,
    proving the parser is discriminating rather than universally matching."""
    compiler = _resolve_compiler()
    stderr = _compile_fixture(compiler, "clean_build_warnings_no_redef.cpp")

    assert not check_build_warnings.MACRO_REDEF_RE.search(stderr), (
        f"expected no MACRO_REDEF_RE match on the clean control.\nGot:\n{stderr}"
    )
    assert "warning:" not in stderr, f"expected zero warnings. Got:\n{stderr}"


def test_parser_consumes_real_compiler_output_end_to_end(tmp_path):
    """Coverage 3 — the end-to-end half of D-14: a real compiler's stderr is
    fed through the gate's own CLI (a temp log + --log), asserting non-zero
    exit and that the offending macro is named in the output."""
    compiler = _resolve_compiler()
    macro_name = _fixture_macro_name()
    stderr = _compile_fixture(compiler, "planted_build_warnings_macro_redef.cpp")

    log_path = tmp_path / "real_compiler_output.log"
    log_path.write_text(stderr)

    result = _run_checker(["--log", f"uno={log_path}"])
    assert result.returncode != 0, (
        f"expected non-zero exit feeding a real compiler redefinition to an "
        f"AVR env (exact-zero rule).\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert macro_name in result.stdout, (
        f"expected the offending macro {macro_name!r} named in the gate's "
        f"output. Got:\n{result.stdout}"
    )


def test_parser_survives_pio_test_framing():
    """Coverage 4 — MACRO_REDEF_RE and WARNING_LINE_RE are proven against real
    `pio test -e native` framing (Processing/Building preamble, the
    compiler's own `In file included from ...` chain, and trailing `note:`
    lines) rather than only a bare compiler invocation. Closes D-14's
    recorded gap."""
    text = (_FIXTURES / "captured_native_warnings_excerpt.log").read_text()

    macro_matches = check_build_warnings.MACRO_REDEF_RE.findall(text)
    assert "PSTR" in macro_matches, (
        f"expected MACRO_REDEF_RE to find the real PSTR redefinition despite "
        f"pio's own framing. Matches found: {macro_matches}"
    )
    assert len(macro_matches) == 8, (
        f"expected exactly 8 macro-redefinition diagnostics in the captured "
        f"excerpt (one per pgmspace.h macro). Got: {macro_matches}"
    )

    warning_lines = check_build_warnings.WARNING_LINE_RE.findall(text)
    assert len(warning_lines) == 8, (
        f"expected WARNING_LINE_RE to count 8 warning: lines in the excerpt, "
        f"undisturbed by the surrounding `note:` lines and framing. "
        f"Got {len(warning_lines)}:\n{warning_lines}"
    )


def test_avr_exact_zero_fires_on_planted_redefinition():
    """Coverage 5 — one genuine redefinition inserted into a real uno build
    log must exit non-zero, naming the env, the observed count (1) and the
    rule (0)."""
    result = _run_checker(
        ["--log", f"uno={_FIXTURES / 'planted_build_warnings_avr_redef.log'}"]
    )
    assert result.returncode != 0, (
        f"expected non-zero exit on a planted AVR redefinition.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "uno" in result.stdout
    assert "observed=1" in result.stdout, f"Expected observed=1. Got:\n{result.stdout}"
    assert "rule==(0)" in result.stdout, f"Expected rule==(0). Got:\n{result.stdout}"


def test_avr_clean_controls_pass_all_three_envs():
    """Coverage 6 — each captured_build_*.log exits 0 with a PASS: line."""
    for env_name, fixture in (
        ("uno", "captured_build_uno.log"),
        ("uno328pb", "captured_build_uno328pb.log"),
        ("leonardo", "captured_build_leonardo.log"),
    ):
        result = _run_checker(["--log", f"{env_name}={_FIXTURES / fixture}"])
        assert result.returncode == 0, (
            f"{env_name}: expected exit 0 on a clean captured log.\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
        assert "PASS:" in result.stdout, f"{env_name}: expected PASS:. Got:\n{result.stdout}"
        assert env_name in result.stdout


def test_native_watermark_fires_on_planted_excess():
    """Coverage 7 — 363 warning: lines against a 360 watermark exits
    non-zero, naming both the observed count and the watermark."""
    result = _run_checker(
        ["--log", f"native={_FIXTURES / 'planted_build_warnings_native_excess.log'}"]
    )
    assert result.returncode != 0, (
        f"expected non-zero exit when total warnings exceed the watermark.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "363" in result.stdout, f"Expected observed count 363. Got:\n{result.stdout}"
    assert "360" in result.stdout, f"Expected watermark 360. Got:\n{result.stdout}"


def test_native_clean_control_passes_at_its_actual_watermark(tmp_path):
    """Coverage 8 — captured_test_native_summary.log is 123-01's truncated
    SUMMARY-tail capture and carries 0 warning: lines, not the real 360 (see
    this module's docstring). A temp baseline pins native.native's
    total_watermark to 0 -- what this truncated tail actually contains --
    proving the OK-at-exact-watermark arm fires rather than exercising the
    (also correct, but here beside the point) below-watermark INFO arm."""
    real_baseline = json.loads(_BASELINE.read_text())
    real_baseline["warnings"]["native"]["native"]["total_watermark"] = 0
    real_baseline["warnings"]["native"]["native"]["macro_redefinition"] = 0
    tampered = tmp_path / "native_truncated_tail_baseline.json"
    tampered.write_text(json.dumps(real_baseline))

    result = _run_checker(
        ["--log", f"native={_FIXTURES / 'captured_test_native_summary.log'}"],
        env_overrides={"FIRESTARTER_SIZE_BASELINE": str(tampered)},
    )
    assert result.returncode == 0, (
        f"expected exit 0 -- the truncated tail's real warning count (0) "
        f"equals the adjusted watermark (0).\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS:" in result.stdout, f"Expected PASS:. Got:\n{result.stdout}"


def test_never_vacuous_with_no_logs_and_no_rebuild():
    """Coverage 9 — no --log and no --rebuild must exit non-zero, print the
    never-vacuous message, and print no PASS:."""
    result = _run_checker([])
    assert result.returncode != 0, (
        f"expected non-zero exit with zero envs supplied.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS:" not in result.stdout, (
        f"A vacuous run must never print PASS:. Got:\n{result.stdout}"
    )
    assert "no" in result.stdout.lower() and "examined" in result.stdout.lower(), (
        f"Expected the never-vacuous message naming 'no ... examined'. Got:\n{result.stdout}"
    )


def test_unknown_env_is_a_configuration_error():
    """Coverage 10 — a log supplied for an env absent from the baseline's
    warnings block must exit exactly 2, the literal configuration-error
    code, not merely non-zero."""
    result = _run_checker(
        ["--log", f"nosuchenv={_FIXTURES / 'captured_build_uno.log'}"]
    )
    assert result.returncode == 2, (
        f"expected the literal exit code 2 (configuration error), got "
        f"{result.returncode}.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS:" not in result.stdout, (
        f"An unknown env must never print PASS:. Got:\n{result.stdout}"
    )
