#!/usr/bin/env python3
"""scripts/check_size_baseline.py — BASE-01 non-regression gate (Phase 123 Plan 02, D-01)
and MERGE-05's one-shot band comparator (Phase 124 Plan 02).

Two modes, selected by the presence/absence of `--policy merge05`:

  - **Default (no `--policy`):** strict byte-identity. Every AVR figure
    (flash_used, flash_total, ram_used, ram_total) and every native fact
    (cases, suites, all_passed) must match the baseline EXACTLY. This mode
    reads `scripts/baseline/size_baseline.json` by default (the LIVE
    baseline, which Phase 124 Plan 10 rewrites to the post-landing figures)
    and turns MERGE-06's rule ("both native envs report the recorded case
    and suite counts") into an exit code, so a later phase cites a number by
    reading a file rather than comparing two numbers by eye. This mode's
    behaviour and output text are UNCHANGED by the addition of `--policy`.

  - **`--policy merge05`:** the band mode. Turns MERGE-05's rule ("Leonardo
    flash must not grow; Uno-class flash growth <= 64 B; RAM unchanged")
    into an exit code for the first time. Since the v1.31 Phase 145
    adjudication it enforces those base bands PLUS one named, SHA-attributed
    defect-fix exemption of MERGE05_DEFECT_FIX_EXEMPTION_BYTES (96 B, commits
    eb563d2 and ebe9cb3) on all three AVR targets -- see that constant's
    comment for what the bytes are and which three alternatives (re-anchoring
    BASE-01 a third time, widening the bands, shrinking the fix) were
    considered and rejected. The exemption is additive and flash-only: the RAM
    clause keeps zero tolerance, the band literals are unchanged, BASE-01's
    recorded figures are unchanged, and the deltas are printed with their
    decomposition so the admitted +96 B stays visible in both the PASS and the
    FAIL text. This is a one-shot assertion meant
    to be run against the FROZEN `scripts/baseline/size_baseline_base01.json`
    record (Phase 124 Plan 02) — the pre-landing figures — never against
    whatever `scripts/baseline/size_baseline.json` says after Plan 124-10
    re-baselines it to the post-landing figures. Always pass `--baseline
    scripts/baseline/size_baseline_base01.json` explicitly with this policy;
    relying on the default baseline path here would silently compare against
    a moving target.

This script supersedes the retired Uno-only RAM-ceiling shell gate (Plan 123-02;
see `scripts/baseline/size_baseline.json`'s `meta.supersedes` field for the full
provenance): that gate asserted only Uno free RAM against a single hardcoded
floor, itself stale — measured free RAM today is 475 B. This comparator is
strictly stronger: it covers flash as well as RAM, all three AVR envs rather
than `uno` alone, both native envs' case/suite/status facts, and it reads a
recorded measurement from a committed JSON rather than a hand-maintained
constant.

Exit codes (identical taxonomy in both modes):
  0 — every env supplied compared clean against the baseline/policy (gate passes)
  1 — an env's observed figures diverge from the baseline (default mode) or
      fall outside MERGE-05's effective allowance (`--policy merge05`; base
      band plus the named defect-fix exemption), OR zero envs were
      compared (the never-vacuous guard: a comparator that compares nothing
      must not report success — not bypassed by `--policy`)
  2 — a supplied log could not be parsed (no `RAM:`/`Flash:` report found, or no
      `N test cases:` summary line, or no per-suite SUMMARY rows), or the CLI
      invocation itself is malformed (e.g. an unrecognised `--policy` value) —
      a tool/format failure, categorically distinct from a size regression,
      and never silently reported as a pass

Anti-hollow contract: this checker's mandatory paired pytest is
`tests/test_check_size_baseline.py`, which invokes this script as a real
subprocess against committed fixtures under `tests/fixtures/` (`captured_*` for
the clean-control arms, `planted_size_baseline_*` for one deliberate violation
per exit-taxonomy arm) via list-form `subprocess.run` — never `shell=True` and
never an in-process import. A passing pytest suite proves THIS script fails
the build on a real violation, not merely that the test asserts it should.
The baseline is read through the `FIRESTARTER_SIZE_BASELINE` env seam (default
resolving to the committed `scripts/baseline/size_baseline.json`), the same
seam name `check_build_warnings.py` (Plan 123-03) reads.

Non-claim: a green run proves the recorded numbers still hold for the log it
was given. It does NOT prove that log came from a clean build — only
`--rebuild` guarantees that, by invoking `pio` itself.

Non-claim: a green `--policy merge05` run proves the deltas are inside the
effective allowance -- the band the requirement licenses plus the exemption
this project adjudicated and recorded. It does NOT prove the deltas are
inside MERGE-05's original v1.23-era band (they are not: v1.31 ships +96 B
over it, admitted deliberately), it proves nothing about whether the deltas
are desirable, and nothing about the log having come from a clean build
(only `--rebuild` guarantees that).

Usage:
    python3 scripts/check_size_baseline.py --avr-log leonardo=path/to/build.log
    python3 scripts/check_size_baseline.py --native-log native=path/to/test.log
    python3 scripts/check_size_baseline.py --rebuild
    python3 scripts/check_size_baseline.py --baseline path/to/other.json --avr-log uno=...
    # Canonical MERGE-05 invocation (the frozen BASE-01 record, not the live default):
    python3 scripts/check_size_baseline.py --policy merge05 \\
        --baseline scripts/baseline/size_baseline_base01.json \\
        --avr-log leonardo=path/to/build.log --avr-log uno=path/to/build.log \\
        --avr-log uno328pb=path/to/build.log
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# Resolve the repo root from this file's location so the gate behaves
# identically regardless of the caller's working directory (mirrors
# firestarter_app/tools/check_mypy_watermark.py:23).
# Layout: <repo>/scripts/check_size_baseline.py -> repo root is one parent up.
REPO_ROOT = Path(__file__).resolve().parent.parent

# Single-target env seam (a default IS appropriate here, unlike a list-valued
# seam): mirrors check_no_log_in_sdp_window.py's FIRESTARTER_SDP_SRC idiom.
FIRESTARTER_SIZE_BASELINE = os.environ.get(
    "FIRESTARTER_SIZE_BASELINE", str(REPO_ROOT / "scripts" / "baseline" / "size_baseline.json")
)

AVR_ENVS = ("uno", "uno328pb", "leonardo")
NATIVE_ENVS = ("native", "native_nodevtools")

# MERGE-05's uno-class flash-growth band, in bytes. See
# .planning/milestones/v1.23-REQUIREMENTS.md:56 (MERGE-05's exact wording, now
# archived and complete -- it was true at v1.23's close and is NOT edited by the
# v1.31 adjudication recorded below) and that milestone's "Operator Decisions
# Locked at Definition" item 4 (why the band is 64 B rather than zero growth).
# The single place this literal lives -- _merge05_flash_allowance() is the only
# consumer.
MERGE05_UNO_CLASS_FLASH_BAND = 64

# The adjudicated, SHA-attributed defect-fix exemption, in bytes, ADDED to each
# target's base band to form that target's EFFECTIVE flash-growth allowance.
# Applies to all three AVR targets alike -- uno, uno328pb AND leonardo (whose
# base band is 0 B must-not-grow). The single place this literal lives --
# _merge05_flash_allowance() is the only consumer, the same single-consumer
# property MERGE05_UNO_CLASS_FLASH_BAND has.
#
# What the 96 bytes ARE: eprom_internal_program_pulse() plus its two VPP settle
# constants, from firmware commits eb563d2 ("assert the program-voltage route
# around every program pulse") and ebe9cb3 ("raise the VPP settles to
# 1000us/100us on bench evidence"). Measured at exactly +96 B on all three AVR
# targets against BASE-01; RAM did not move (1573/1579/2014, unchanged). The two
# commits restore behaviour the pre-v1.31 firmware had -- a correctness fix, not
# new feature surface.
#
# WHY an exemption. All three alternatives were considered and rejected in the
# v1.31 Phase 145 adjudication:
#   - NOT a third re-anchor of scripts/baseline/size_baseline_base01.json.
#     Phase 144 / D-11 moved that anchor once already, and the green that
#     produced was the anchor moving, not growth shrinking (D-14 says so in the
#     file itself). A second move would hide growth behind the same mechanism
#     twice and would erase the delta entirely. BASE-01's avr_targets therefore
#     stay byte-unchanged: uno 24824, uno328pb 24874, leonardo 26906.
#   - NOT a widening of MERGE05_UNO_CLASS_FLASH_BAND, and NOT a widening of the
#     leonardo 0 B band. Either would silently admit any future 96 B of
#     unrelated feature growth and destroy the tripwire. Both band literals are
#     unchanged.
#   - NOT shrinking the fix. Micro-optimising a correctness fix to make it fit a
#     band set before the per-protocol parameter table existed is the wrong
#     incentive and risks the fix.
# The exemption is instead NAMED here, so the growth is admitted in one visible,
# attributable place rather than laundered into a moved reference point.
#
# The tripwire stays ARMED at the new floor: a delta of one byte beyond the
# effective allowance still FAILS. That is a machine-checked negative control,
# not a claim -- tests/test_check_size_baseline.py's
# test_policy_merge05_admits_the_documented_defect_fix feeds a planted +97 B
# leonardo log and asserts exit 1.
#
# SCOPE: flash only. compare_avr_policy_merge05's ram_used clause keeps its
# zero tolerance and is deliberately NOT widened by this constant -- RAM did not
# move, so any RAM delta must still fail.
MERGE05_DEFECT_FIX_EXEMPTION_BYTES = 96

# Matches both the RAM: and Flash: report lines in one pattern. Anchored at
# column 0, multiline. Does NOT capture the percentage or the bar-graph
# column -- they vary run to run and are not the datum.
SIZE_RE = re.compile(
    r"^(?P<kind>RAM|Flash):\s+\[[^\]]*\]\s+[\d.]+%\s+"
    r"\(used (?P<used>\d+) bytes from (?P<total>\d+) bytes\)",
    re.MULTILINE,
)

# Matches the "N test cases: N succeeded" summary line.
CASES_RE = re.compile(r"^=+\s+(?P<total>\d+) test cases:\s+(?P<ok>\d+) succeeded", re.MULTILINE)

# Matches per-suite SUMMARY rows: captures the native/avr/<suite> path and the
# status word. Suite count is NOT printed as a number anywhere by pio -- it
# must be derived by counting these rows.
SUITE_RE = re.compile(
    r"^\s*\S+\s+(?P<suite>native/avr/\S+)\s+(?P<status>PASSED|FAILED|ERRORED|IGNORED)\s",
    re.MULTILINE,
)


class ParseError(Exception):
    """A build/test log could not be parsed into the expected shape.

    Caught only in main() and converted to exit 2 -- never exit 1 and never
    exit 0. A parse failure is a tool/format failure, categorically distinct
    from a size regression: a pio output-format change must never be silently
    reported as a clean tree.
    """


def parse_sizes(text):
    """Parse RAM:/Flash: report lines. Returns {"RAM": (used, total), "Flash": (used, total)}.

    Raises ParseError if the set of found kinds is not exactly {RAM, Flash} --
    this is the exit-2 arm the retired shell gate's exit code 2 carries forward.
    """
    found = {
        m.group("kind"): (int(m.group("used")), int(m.group("total")))
        for m in SIZE_RE.finditer(text)
    }
    if set(found) != {"RAM", "Flash"}:
        raise ParseError(f"expected RAM and Flash lines, found {sorted(found)}")
    return found


def parse_native(text):
    """Parse a native pio-test log. Returns cases, succeeded, suites, all_passed.

    Raises ParseError if either the "N test cases:" summary line or the
    per-suite SUMMARY rows are absent. Asserts nothing itself -- comparison
    against the baseline happens in compare_native.
    """
    m = CASES_RE.search(text)
    if not m:
        raise ParseError("no 'N test cases:' summary line found")
    suites = SUITE_RE.findall(text)
    if not suites:
        raise ParseError("no per-suite SUMMARY rows found")
    return {
        "cases": int(m.group("total")),
        "succeeded": int(m.group("ok")),
        "suites": len(suites),
        "all_passed": all(status == "PASSED" for _suite, status in suites),
        "statuses": suites,
    }


def load_baseline(path):
    """Load and return the baseline JSON as a dict."""
    with open(path) as f:
        return json.load(f)


def compare_avr(env, parsed, baseline):
    """Compare a parsed AVR size report against the recorded baseline for `env`.

    Asserts flash_used and ram_used equal the recorded values, and that
    flash_total/ram_total are unchanged (a changed total means the board or
    framework moved -- a finding, not a pass). Returns a list of failure
    message strings; empty list means clean.
    """
    rec = baseline["avr_targets"][env]
    ram_used, ram_total = parsed["RAM"]
    flash_used, flash_total = parsed["Flash"]
    failures = []
    if flash_used != rec["flash_used"]:
        failures.append(
            f"{env}: flash_used baseline={rec['flash_used']} observed={flash_used}"
        )
    if flash_total != rec["flash_total"]:
        failures.append(
            f"{env}: flash_total baseline={rec['flash_total']} observed={flash_total} "
            "(board or framework moved)"
        )
    if ram_used != rec["ram_used"]:
        failures.append(f"{env}: ram_used baseline={rec['ram_used']} observed={ram_used}")
    if ram_total != rec["ram_total"]:
        failures.append(
            f"{env}: ram_total baseline={rec['ram_total']} observed={ram_total} "
            "(board or framework moved)"
        )
    return failures


def _merge05_flash_allowance(env):
    """Resolve `env`'s MERGE-05 flash-growth figures. Returns
    (band, exemption, allowance, band_label).

    Sole consumer of BOTH MERGE05_UNO_CLASS_FLASH_BAND and
    MERGE05_DEFECT_FIX_EXEMPTION_BYTES -- compare_avr_policy_merge05 (the FAIL
    arm) and main()'s PASS-line builder both call this rather than each
    recomputing the band, so neither literal is ever read in two places and the
    pass/fail arms can never disagree about the allowance. (Before the exemption
    was added, main() DID recompute `band` itself, quietly falsifying the band
    literal's own "single place this literal lives" comment; that duplication is
    removed here.)

    `allowance` is the effective ceiling actually enforced: base band plus the
    named defect-fix exemption. `band` and `exemption` are returned separately
    so every message can show the decomposition instead of only the sum -- the
    +96 B stays visible in the output rather than being absorbed into one
    widened number.
    """
    band = 0 if env == "leonardo" else MERGE05_UNO_CLASS_FLASH_BAND
    band_label = "leonardo" if env == "leonardo" else "uno-class"
    exemption = MERGE05_DEFECT_FIX_EXEMPTION_BYTES
    return band, exemption, band + exemption, band_label


def compare_avr_policy_merge05(env, parsed, baseline):
    """Compare a parsed AVR size report against MERGE-05's BAND policy for `env`
    (not strict equality -- see compare_avr for the default mode).

    Rules:
      - leonardo: base band 0 B -- flash_used must not grow at all beyond the
        exemption (it may shrink).
      - uno / uno328pb: base band MERGE05_UNO_CLASS_FLASH_BAND bytes over the
        recorded value.
      - all three: the effective flash ceiling is that base band PLUS
        MERGE05_DEFECT_FIX_EXEMPTION_BYTES -- the named, SHA-attributed
        defect-fix exemption adjudicated in v1.31 Phase 145 (see the constant's
        own comment for what the bytes are, which three alternatives were
        rejected, and why). Both figures are resolved in one place by
        _merge05_flash_allowance(). Every message prints the decomposition
        (`band N B + defect-fix exemption 96 B`) so the admitted growth stays
        visible rather than disappearing into a single widened number.
      - all three: ram_used must be exactly unchanged. The exemption is a FLASH
        allowance only and does not touch this clause. MERGE-05's text binds
        RAM equality on Uno/Leonardo only; equality is enforced on uno328pb
        too because it is measured equal -- deliberately stronger than the
        requirement text, never weaker.
      - all three: flash_total and ram_total must be unchanged (a changed
        total means the board or framework moved -- a finding, not a pass),
        reusing compare_avr's existing message text verbatim.

    Returns a list of failure message strings; empty list means clean --
    same shape as compare_avr. Every failure names the env, the baseline
    figure, the observed figure and the computed delta.
    """
    rec = baseline["avr_targets"][env]
    ram_used, ram_total = parsed["RAM"]
    flash_used, flash_total = parsed["Flash"]
    failures = []

    band, exemption, allowance, band_label = _merge05_flash_allowance(env)
    flash_delta = flash_used - rec["flash_used"]
    if flash_delta > allowance:
        failures.append(
            f"{env}: flash_used baseline={rec['flash_used']} observed={flash_used} "
            f"delta={flash_delta:+d} exceeds MERGE-05 {band_label} allowance of "
            f"{allowance} B (band {band} B + defect-fix exemption {exemption} B)"
        )

    if ram_used != rec["ram_used"]:
        ram_delta = ram_used - rec["ram_used"]
        failures.append(
            f"{env}: ram_used baseline={rec['ram_used']} observed={ram_used} "
            f"delta={ram_delta:+d} (MERGE-05 requires ram_used unchanged)"
        )

    if flash_total != rec["flash_total"]:
        failures.append(
            f"{env}: flash_total baseline={rec['flash_total']} observed={flash_total} "
            "(board or framework moved)"
        )
    if ram_total != rec["ram_total"]:
        failures.append(
            f"{env}: ram_total baseline={rec['ram_total']} observed={ram_total} "
            "(board or framework moved)"
        )
    return failures


def compare_native(env, parsed, baseline):
    """Compare a parsed native test log against the recorded baseline for `env`.

    Asserts all three of A-4's facts: cases equals the recorded value, suites
    equals the recorded value, AND every suite status is PASSED. A run with 17
    suites all ERRORED still has 17 suites -- asserting only the count
    reproduces this project's own "assert counts, never tests pass"
    anti-pattern in mirror image, so all three are asserted explicitly.
    """
    rec = baseline["native_envs"][env]
    failures = []
    if parsed["cases"] != rec["cases"]:
        failures.append(f"{env}: cases baseline={rec['cases']} observed={parsed['cases']}")
    if parsed["suites"] != rec["suites"]:
        failures.append(f"{env}: suites baseline={rec['suites']} observed={parsed['suites']}")
    if not parsed["all_passed"]:
        bad = [f"{suite}={status}" for suite, status in parsed["statuses"] if status != "PASSED"]
        failures.append(
            f"{env}: not all suites PASSED (baseline requires all_passed=true); "
            f"non-PASSED: {', '.join(bad[:20])}"
        )
    return failures


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


def _print_pass(compared):
    """Print the anti-skip PASS: line naming every env compared and its figures.

    A run that compared nothing must never reach this function -- see the
    never-vacuous guard in main().
    """
    parts = ", ".join(compared)
    print(f"PASS: {parts}")


def _print_fail(failures, bucketed_label=""):
    """Print FAIL: lines, one per divergence, capped at 20 rows."""
    print(f"FAIL: {bucketed_label}".rstrip() if bucketed_label else "FAIL:")
    for line in failures[:20]:
        print(f"  {line}")
    if len(failures) > 20:
        print(f"  ... and {len(failures) - 20} more")


def _parse_argv(argv):
    """Manual argv parser (no third-party/argparse dependency; house convention,
    mirrors check_permitted_claims.py's resolve_targets(argv) style).

    Recognises --baseline PATH, repeated --avr-log ENV=PATH, repeated
    --native-log ENV=PATH, the --rebuild flag, and --policy VALUE (the only
    recognised VALUE is "merge05"). Raises SystemExit(2) on a malformed
    invocation (unknown flag, a flag missing its value, or an unrecognised
    --policy value) -- a CLI usage error is itself a tool/format failure, not
    a size regression.
    """
    baseline = None
    avr_logs = []
    native_logs = []
    rebuild = False
    policy = None
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--baseline":
            i += 1
            if i >= len(argv):
                print("ERROR: --baseline requires a PATH argument", file=sys.stderr)
                raise SystemExit(2)
            baseline = argv[i]
        elif arg == "--avr-log":
            i += 1
            if i >= len(argv):
                print("ERROR: --avr-log requires an ENV=PATH argument", file=sys.stderr)
                raise SystemExit(2)
            avr_logs.append(argv[i])
        elif arg == "--native-log":
            i += 1
            if i >= len(argv):
                print("ERROR: --native-log requires an ENV=PATH argument", file=sys.stderr)
                raise SystemExit(2)
            native_logs.append(argv[i])
        elif arg == "--rebuild":
            rebuild = True
        elif arg == "--policy":
            i += 1
            if i >= len(argv):
                print("ERROR: --policy requires a VALUE argument", file=sys.stderr)
                raise SystemExit(2)
            value = argv[i]
            if value != "merge05":
                print(
                    f"ERROR: unrecognized --policy value: {value!r} "
                    "(only 'merge05' is recognised)",
                    file=sys.stderr,
                )
                raise SystemExit(2)
            policy = value
        else:
            print(f"ERROR: unrecognized argument: {arg}", file=sys.stderr)
            raise SystemExit(2)
        i += 1
    return baseline, avr_logs, native_logs, rebuild, policy


def main(argv):
    baseline_arg, avr_log_specs, native_log_specs, rebuild, policy = _parse_argv(argv)

    baseline_path = baseline_arg or FIRESTARTER_SIZE_BASELINE
    baseline = load_baseline(baseline_path)

    # Never-vacuous guard: if zero envs will be compared (no logs supplied and
    # --rebuild absent), fail closed BEFORE the per-env loop. A comparator
    # that compares nothing must not print PASS:.
    if not avr_log_specs and not native_log_specs and not rebuild:
        print(
            "FAIL: no envs compared -- supply --avr-log/--native-log or --rebuild "
            "(never-vacuous guard: a comparator that compares nothing must not pass)"
        )
        return 1

    compared = []
    all_failures = []
    parse_errors = []

    avr_sources = {}
    for spec in avr_log_specs:
        env, _, path = spec.partition("=")
        avr_sources[env] = Path(path).read_text()
    native_sources = {}
    for spec in native_log_specs:
        env, _, path = spec.partition("=")
        native_sources[env] = Path(path).read_text()

    if rebuild:
        for env in AVR_ENVS:
            avr_sources[env] = _rebuild_avr(env)
        for env in NATIVE_ENVS:
            native_sources[env] = _rebuild_native(env)

    for env, text in avr_sources.items():
        try:
            parsed = parse_sizes(text)
        except ParseError as e:
            print(f"ERROR: {env}: {e}", file=sys.stderr)
            parse_errors.append(env)
            continue
        if policy == "merge05":
            failures = compare_avr_policy_merge05(env, parsed, baseline)
        else:
            failures = compare_avr(env, parsed, baseline)
        if failures:
            all_failures.extend(failures)
        else:
            u, t = parsed["Flash"]
            ru, rt = parsed["RAM"]
            if policy == "merge05":
                rec = baseline["avr_targets"][env]
                band, exemption, allowance, _label = _merge05_flash_allowance(env)
                flash_delta = u - rec["flash_used"]
                compared.append(
                    f"{env}(flash={u}/{t}"
                    f"[{flash_delta:+d}<={allowance}=band{band}+exempt{exemption}],"
                    f"ram={ru}/{rt}[=])"
                )
            else:
                compared.append(f"{env}(flash={u}/{t},ram={ru}/{rt})")

    for env, text in native_sources.items():
        try:
            parsed = parse_native(text)
        except ParseError as e:
            print(f"ERROR: {env}: {e}", file=sys.stderr)
            parse_errors.append(env)
            continue
        failures = compare_native(env, parsed, baseline)
        if failures:
            all_failures.extend(failures)
        else:
            compared.append(f"{env}(cases={parsed['cases']},suites={parsed['suites']})")

    if parse_errors:
        print(
            f"ERROR: could not parse output for: {', '.join(parse_errors)} -- "
            "treating as a tool/format failure, not a clean tree or a regression.",
            file=sys.stderr,
        )
        return 2

    if all_failures:
        _print_fail(all_failures)
        return 1

    if not compared:
        # Every requested env failed to parse and was already handled above;
        # this branch only reachable if avr_sources/native_sources were both
        # empty despite --rebuild somehow yielding nothing -- fail closed.
        print("FAIL: no envs compared -- never-vacuous guard")
        return 1

    _print_pass(compared)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
