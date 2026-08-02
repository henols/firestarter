#!/usr/bin/env python3
"""scripts/check_build_warnings.py — BASE-06 warning gate (Phase 123 Plan 03, D-13/D-14).

Parses `pio run`/`pio test` output for compiler warnings and holds them to the
policy recorded in `scripts/baseline/size_baseline.json`'s `warnings` block
(the same file `check_size_baseline.py` reads, via the same
`FIRESTARTER_SIZE_BASELINE` env seam — one file, two consumers, D-13):

  - The three AVR envs (uno, uno328pb, leonardo) are held at **exact zero**
    macro-redefinition warnings (`== 0`, not `<= 0`) — they are measured
    genuinely clean today, so equality is strictly stronger than an
    inequality and is what `policy.avr_rule` records.
  - The two native envs (native, native_nodevtools) each carry a recorded
    **watermark of 360** total warnings (`policy.native_rule` == `<=
    total_watermark`), so any NEW warning of any kind on native fails, while
    the characterised pre-existing debt below does not.

**The 360 is characterised pre-existing debt, not damage.** Each native
suite ships its own `test/native/avr/<suite>/avr/pgmspace.h` host shim
defining 8 macros (PSTR, memcpy_P, pgm_read_byte, pgm_read_dword,
pgm_read_ptr, pgm_read_word, strcpy_P, strlen_P), and ArduinoFake's own
`pgmspace.h` then redefines every one of them across the 45 native
translation units — 8 x 45 = 360. This count was present on `beta` before
any v1.23 work; it is **not a regression** and it is not damage. Remediating
it would mean deduplicating those 17 suite-local shims, which touches 17
suite directories and breaches this phase's "no firmware code moves"
boundary — that remediation (RESEARCH's Option B) was considered and
rejected by the operator in favor of the exact-zero-on-AVR-plus-watermark
shape (Option A) implemented here. A reader who lowers the watermark must
re-measure the real count first, never guess it down.

Exit codes:
  0 — every env supplied held to its policy (AVR exact zero; native at or
      below its recorded watermark) — gate passes
  1 — an env's observed warning count violates its policy (a new AVR
      redefinition, or a native total/redefinition count above the
      recorded value), OR zero envs were examined (the never-vacuous
      guard: a gate that examined nothing must never report success)
  2 — an env name supplied via --log is not present in the baseline's
      `warnings` block, or the baseline itself could not be loaded/parsed —
      a configuration error, categorically distinct from a warning
      violation, and never silently reported as a pass

Anti-hollow contract: this checker's mandatory paired pytest is
`tests/test_check_build_warnings.py`, which invokes this script as a real
subprocess (list-form `subprocess.run`, never `shell=True`, never an
in-process import) against committed fixtures under `tests/fixtures/`
(`planted_build_warnings_*` for one deliberate violation per exit-taxonomy
arm, plus `captured_*` for the clean-control arms). The pytest also compiles
`planted_build_warnings_macro_redef.cpp` with a real host `g++` and feeds the
captured diagnostic straight through this module's own parser — a passing
suite therefore proves this parser matches a genuine compiler diagnostic, not
merely that the test asserts it should.

Non-claim: a green run proves the warning counts in the supplied logs are
within policy for the envs actually examined. It proves nothing about
warnings a build did not emit because it did not run — which is exactly why
the never-vacuous guard refuses to report PASS when it examined no env.

Usage:
    python3 scripts/check_build_warnings.py --log uno=path/to/build.log
    python3 scripts/check_build_warnings.py --log native=path/to/test.log
    python3 scripts/check_build_warnings.py --rebuild
    python3 scripts/check_build_warnings.py --baseline path/to/other.json --log uno=...
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# Resolve the repo root from this file's location so the gate behaves
# identically regardless of the caller's working directory (mirrors
# check_size_baseline.py:63 / check_mypy_watermark.py:23).
# Layout: <repo>/scripts/check_build_warnings.py -> repo root is one parent up.
REPO_ROOT = Path(__file__).resolve().parent.parent

# Shared seam with check_size_baseline.py (D-13: one baseline file, two
# consumers). Deliberately NOT a second constant pointing at a different
# path -- both checkers must read the exact same committed JSON.
FIRESTARTER_SIZE_BASELINE = os.environ.get(
    "FIRESTARTER_SIZE_BASELINE", str(REPO_ROOT / "scripts" / "baseline" / "size_baseline.json")
)

AVR_ENVS = ("uno", "uno328pb", "leonardo")
NATIVE_ENVS = ("native", "native_nodevtools")

# Anchored on the diagnostic TAIL only -- a `warning:` token, a double-quoted
# macro name, then the word `redefined`. Deliberately excludes any
# `:line:col:` prefix: gcc 7.3 (avr-g++) emits a `:2:0:` form and gcc 14
# (host g++) emits a `:2:9:` form for the identical diagnostic. A
# column-inclusive pattern would silently narrow if a future toolchain
# changed its column reporting (RESEARCH "Compiler choice for the D-14
# fixture — pinned").
MACRO_REDEF_RE = re.compile(r'warning:\s*"(?P<macro>[^"]+)"\s+redefined')

# Counts every diagnostic LINE carrying a `warning:` token -- mirrors the
# `grep -cE 'warning:'` counting command recorded in size_baseline.json's
# `warnings.counting_command` field, so the two counting mechanisms agree.
WARNING_LINE_RE = re.compile(r"^.*warning:.*$", re.MULTILINE)


class ParseError(Exception):
    """An env name or baseline could not be resolved into the expected shape.

    Caught only in main() and converted to exit 2 -- never exit 1 and never
    exit 0. An env absent from the baseline's `warnings` block is a
    configuration error, categorically distinct from a warning-count
    violation: supplying a log for an env the baseline does not know about
    must never be silently reported as a pass.
    """


def load_baseline(path):
    """Load and return the baseline JSON as a dict."""
    with open(path) as f:
        return json.load(f)


def check_env(env, text, baseline):
    """Check one env's build/test output against the baseline's warnings policy.

    Returns (status, message) where status is one of "OK", "INFO", "FAIL".
    "INFO" is not a failure -- it mirrors check_mypy_watermark.py's
    below-watermark arm, telling the reader to lower the native watermark
    (after re-measuring, never by guessing).

    Raises ParseError if `env` is present in neither `warnings.avr` nor
    `warnings.native` -- an unknown env is a configuration error (exit 2),
    never treated as a pass.
    """
    warnings_block = baseline.get("warnings", {})
    macro_count = len(MACRO_REDEF_RE.findall(text))
    total_count = len(WARNING_LINE_RE.findall(text))

    avr_block = warnings_block.get("avr", {})
    if env in avr_block:
        rule = avr_block[env]["macro_redefinition"]
        if macro_count != rule:
            names = sorted({m.group("macro") for m in MACRO_REDEF_RE.finditer(text)})
            names_str = ", ".join(names[:20]) if names else "(none)"
            return "FAIL", (
                f"{env}: macro_redefinition observed={macro_count} rule==({rule}) "
                f"names={names_str} "
                "(AVR envs are measured genuinely clean; the rule is exact equality, "
                "not an inequality)"
            )
        return "OK", f"{env}: macro_redefinition={macro_count} (== {rule})"

    native_block = warnings_block.get("native", {})
    if env in native_block:
        rec = native_block[env]
        watermark = rec["total_watermark"]
        recorded_macro = rec["macro_redefinition"]
        failures = []
        # Asserted independently of the total: a new redefinition must fail
        # even if some other warning disappeared and kept the total flat.
        if macro_count > recorded_macro:
            failures.append(
                f"{env}: macro_redefinition observed={macro_count} exceeds "
                f"recorded={recorded_macro}"
            )
        if total_count > watermark:
            failures.append(
                f"{env}: total warnings observed={total_count} exceeds "
                f"watermark={watermark}"
            )
        if failures:
            return "FAIL", "; ".join(failures)
        if total_count < watermark:
            return "INFO", (
                f"{env}: total warnings observed={total_count} is "
                f"{watermark - total_count} below watermark {watermark} -- "
                "re-measure and lower total_watermark in size_baseline.json; "
                "do not guess a new figure"
            )
        return "OK", f"{env}: total warnings={total_count} (== watermark {watermark})"

    raise ParseError(
        f"env {env!r} not found in baseline warnings.avr or warnings.native -- "
        "configuration error, not a pass"
    )


def _rebuild_avr(env):
    """Run `pio run -t clean -e <env>` then `pio run -e <env>`, return combined stdout+stderr."""
    subprocess.run(["pio", "run", "-t", "clean", "-e", env], cwd=str(REPO_ROOT), check=True)
    result = subprocess.run(
        ["pio", "run", "-e", env], cwd=str(REPO_ROOT), capture_output=True, text=True
    )
    return result.stdout + result.stderr


def _rebuild_native(env):
    """Run `pio test -e <env>`, return combined stdout+stderr."""
    result = subprocess.run(
        ["pio", "test", "-e", env], cwd=str(REPO_ROOT), capture_output=True, text=True
    )
    return result.stdout + result.stderr


def _print_pass(oks):
    """Print the anti-skip PASS: line naming every env examined and its counts.

    A run that examined nothing must never reach this function -- see the
    never-vacuous guard in main().
    """
    print(f"PASS: {', '.join(oks)}")


def _print_fail(failures):
    """Print FAIL: lines, one per violation, capped at 20 rows."""
    print("FAIL:")
    for line in failures[:20]:
        print(f"  {line}")
    if len(failures) > 20:
        print(f"  ... and {len(failures) - 20} more")


def _parse_argv(argv):
    """Manual argv parser (no third-party/argparse dependency; house convention,
    mirrors check_size_baseline.py's _parse_argv).

    Recognises --baseline PATH, repeated --log ENV=PATH, and the --rebuild
    flag. Raises SystemExit(2) on a malformed invocation (unknown flag or a
    flag missing its value) -- a CLI usage error is itself a configuration
    failure, not a warning violation.
    """
    baseline = None
    log_specs = []
    rebuild = False
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--baseline":
            i += 1
            if i >= len(argv):
                print("ERROR: --baseline requires a PATH argument", file=sys.stderr)
                raise SystemExit(2)
            baseline = argv[i]
        elif arg == "--log":
            i += 1
            if i >= len(argv):
                print("ERROR: --log requires an ENV=PATH argument", file=sys.stderr)
                raise SystemExit(2)
            log_specs.append(argv[i])
        elif arg == "--rebuild":
            rebuild = True
        else:
            print(f"ERROR: unrecognized argument: {arg}", file=sys.stderr)
            raise SystemExit(2)
        i += 1
    return baseline, log_specs, rebuild


def main(argv):
    baseline_arg, log_specs, rebuild = _parse_argv(argv)

    # Never-vacuous guard, BEFORE the per-env loop and before the baseline is
    # even consulted: if zero envs will be examined (no --log and no
    # --rebuild), fail closed. A gate that examines nothing must never
    # print PASS:.
    if not log_specs and not rebuild:
        print(
            "FAIL: no envs examined -- supply --log ENV=PATH or --rebuild "
            "(never-vacuous guard: a warning gate that examined nothing must not pass)"
        )
        return 1

    baseline_path = baseline_arg or FIRESTARTER_SIZE_BASELINE
    try:
        baseline = load_baseline(baseline_path)
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR: could not load baseline {baseline_path!r}: {e}", file=sys.stderr)
        return 2

    sources = {}
    for spec in log_specs:
        env, _, path = spec.partition("=")
        sources[env] = Path(path).read_text()

    if rebuild:
        for env in AVR_ENVS:
            sources[env] = _rebuild_avr(env)
        for env in NATIVE_ENVS:
            sources[env] = _rebuild_native(env)

    oks = []
    infos = []
    fails = []
    config_errors = []

    for env, text in sources.items():
        try:
            status, message = check_env(env, text, baseline)
        except ParseError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            config_errors.append(env)
            continue
        if status == "FAIL":
            fails.append(message)
        elif status == "INFO":
            infos.append(message)
            oks.append(message)
        else:
            oks.append(message)

    if config_errors:
        print(
            f"ERROR: unknown env(s) not found in baseline warnings block: "
            f"{', '.join(config_errors)} -- treating as a configuration failure, "
            "not a pass.",
            file=sys.stderr,
        )
        return 2

    if fails:
        _print_fail(fails)
        return 1

    if not oks:
        # Every requested env somehow yielded neither an OK/INFO nor a FAIL
        # nor a config error -- unreachable in practice, but fail closed.
        print("FAIL: no envs examined -- never-vacuous guard")
        return 1

    for info in infos:
        print(f"INFO: {info}")
    _print_pass(oks)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
