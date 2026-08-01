#!/usr/bin/env python3
"""scripts/check_release_assets.py — REL-03/REL-02 AVR-assets-present gate
(Phase 128 Plan 01, D-11, D-12).

Asserts that every AVR target named in the recorded baseline's `avr_targets`
keys has a present, non-empty `firestarter_<key>.hex` under the build root.
This is D-11's checker: `beta-build.yml`'s ARM steps are soft-contained
(`continue-on-error: true`, Phase 128 D-05/D-06/D-07), so a broken ARM build
must never be able to block the three AVR release assets. Three inline
`test -s` lines in the release YAML would be unprovable outside a
`workflow_dispatch` (REL-03's own wording is *"demonstrably fails"*) — this
script is a call site the workflow invokes, and it is provable locally
without CI.

The required set is D-12's rule: derived from `scripts/baseline/size_baseline.json`'s
`avr_targets` keys — never three hardcoded filenames — so a fourth AVR target
added to that file updates this gate for free. An empty `avr_targets` key set
is a never-vacuous-guard failure (exit 1), never a silent pass: a gate that
requires nothing must not print PASS: (A-7's lesson, mirrored from
check_size_baseline.py's own never-vacuous guard).

This script deliberately never mentions, requires, or looks for the py32f071
image. Its absence is REL-03's whole point — the clean control fixture
(`tests/fixtures/clean_release_assets_all_three/`) contains no py32 image and
this checker still exits 0 against it. D-11 rejected a do-everything checker
that would also own the filename equality (REL-04) and the SDK pin, precisely
because bundling a gate that must HARD-fail (AVR missing) with one that must
TOLERATE absence (the py32 image, when the ARM build is contained) would force
internal severity logic into a script whose whole value is that it is
unambiguous.

Two env seams, both read with committed defaults, both documented as SET IN
THE CHILD ENVIRONMENT (mirrors `test_check_size_baseline.py`'s `env_overrides`
convention): `FIRESTARTER_SIZE_BASELINE` (reused from `check_size_baseline.py`
and `check_build_warnings.py`; default `scripts/baseline/size_baseline.json`)
and `FIRESTARTER_PIO_BUILD_ROOT` (new; default `.pio/build`). The new seam
exists because a fixture tree cannot contain a real `.pio/build/...` layout —
`.gitignore` line 1 is the bare pattern `.pio`, which matches at any depth, so
`git add` on such a path exits 0 while staging nothing (research finding F-6).
Each seam is also overridable by an argv flag — `--baseline <path>` and
`--build-root <path>` — with argv winning over env, env winning over the
default.

Exit codes:
  0 — every key in the baseline's `avr_targets` has a present, non-empty
      `<build_root>/<key>/firestarter_<key>.hex` (gate passes)
  1 — at least one required hex is missing or zero bytes, OR the baseline's
      `avr_targets` key set parses empty (the never-vacuous guard: a gate that
      requires nothing must not print PASS:) — never bypassed
  2 — the baseline file could not be read/parsed, is not a JSON object, has no
      `avr_targets` key, or `avr_targets` is not an object, OR the CLI
      invocation itself is malformed (unknown flag, or a flag missing its
      value) — a tool/format failure, categorically distinct from a missing
      asset, and never silently reported as a pass

Anti-hollow contract: this checker's mandatory paired pytest is
`tests/test_check_release_assets.py`, which invokes this script as a real
subprocess (list-form argv, never `shell=True`, never an in-process import)
against the committed fixtures `tests/fixtures/clean_release_assets_all_three/`,
`tests/fixtures/planted_release_assets_missing_uno328pb/` and
`tests/fixtures/planted_release_assets_zero_byte_leonardo/`. A passing pytest
suite proves THIS script fails the build on a real missing/zero-byte asset,
not merely that the test asserts it should.

Non-claim: a green run proves the required AVR hexes are present and non-empty
under the given build root. It proves nothing about whether those hexes were
built from a clean tree, whether the py32f071 image was produced, or whether
any published asset actually runs on real hardware — no PY32F071 PCB exists,
and this script's whole point is REL-03's tolerance for that image's absence.

Usage:
    python3 scripts/check_release_assets.py
    python3 scripts/check_release_assets.py --build-root .pio/build
    python3 scripts/check_release_assets.py --build-root tests/fixtures/clean_release_assets_all_three/pio_build
    python3 scripts/check_release_assets.py --baseline scripts/baseline/size_baseline.json --build-root .pio/build
"""
import json
import os
import sys
from pathlib import Path

# Resolve the repo root from this file's location so the gate behaves
# identically regardless of the caller's working directory (mirrors
# check_size_baseline.py:87-91).
# Layout: <repo>/scripts/check_release_assets.py -> repo root is one parent up.
REPO_ROOT = Path(__file__).resolve().parent.parent

# Reused seam (check_size_baseline.py / check_build_warnings.py already read
# this exact name). Default resolves to the committed, live baseline.
FIRESTARTER_SIZE_BASELINE = os.environ.get(
    "FIRESTARTER_SIZE_BASELINE", str(REPO_ROOT / "scripts" / "baseline" / "size_baseline.json")
)

# New seam (Phase 128, research finding F-6): a fixture tree cannot contain a
# real .pio/build/... layout because .gitignore line 1 is the bare pattern
# ".pio", which matches at any depth -- git add on such a path exits 0 while
# staging nothing. Defaults to the real build root for a real invocation;
# tests point this (or --build-root) at a committed pio_build/ fixture tree.
FIRESTARTER_PIO_BUILD_ROOT = os.environ.get(
    "FIRESTARTER_PIO_BUILD_ROOT", str(REPO_ROOT / ".pio" / "build")
)


def _print_pass(build_root, compared):
    """Print the anti-skip PASS: line naming every env compared and the
    resolved build root.

    A run that compared nothing must never reach this function -- see the
    never-vacuous guard in main().
    """
    parts = ", ".join(compared)
    print(f"PASS: {parts} (build_root={build_root})")


def _print_fail(failures):
    """Print FAIL: lines, one per violation."""
    print("FAIL:")
    for line in failures:
        print(f"  {line}")


def _parse_argv(argv):
    """Manual argv parser (no third-party/argparse dependency; house
    convention, mirrors check_size_baseline.py's _parse_argv).

    Recognises --baseline PATH and --build-root PATH. Raises SystemExit(2) on
    a malformed invocation (unknown flag, or a flag missing its value) -- a
    CLI usage error is itself a tool/format failure, not a missing-asset
    finding.
    """
    baseline = None
    build_root = None
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--baseline":
            i += 1
            if i >= len(argv):
                print("ERROR: --baseline requires a PATH argument", file=sys.stderr)
                raise SystemExit(2)
            baseline = argv[i]
        elif arg == "--build-root":
            i += 1
            if i >= len(argv):
                print("ERROR: --build-root requires a PATH argument", file=sys.stderr)
                raise SystemExit(2)
            build_root = argv[i]
        else:
            print(f"ERROR: unrecognized argument: {arg}", file=sys.stderr)
            raise SystemExit(2)
        i += 1
    return baseline, build_root


def main(argv):
    baseline_arg, build_root_arg = _parse_argv(argv)

    baseline_path = baseline_arg or FIRESTARTER_SIZE_BASELINE
    build_root = Path(build_root_arg or FIRESTARTER_PIO_BUILD_ROOT)

    try:
        with open(baseline_path) as f:
            baseline = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"FAIL: could not read/parse baseline {baseline_path}: {e}")
        return 2

    if not isinstance(baseline, dict):
        print(f"FAIL: baseline {baseline_path} is not a JSON object")
        return 2

    avr_targets = baseline.get("avr_targets")
    if "avr_targets" not in baseline or not isinstance(avr_targets, dict):
        print(f"FAIL: baseline {baseline_path} has no object-valued 'avr_targets' key")
        return 2

    # Never-vacuous guard, run BEFORE the per-env loop (mirrors
    # check_size_baseline.py's own never-vacuous guard): a gate that requires
    # nothing must not print PASS:.
    keys = sorted(avr_targets.keys())
    if not keys:
        print(
            "FAIL: baseline 'avr_targets' parsed empty -- never-vacuous guard "
            "(a gate that requires nothing must not report success)"
        )
        return 1

    failures = []
    compared = []
    for key in keys:
        expected = build_root / key / f"firestarter_{key}.hex"
        if not expected.exists():
            failures.append(f"{key}: missing {expected}")
            continue
        size = expected.stat().st_size
        if size <= 0:
            failures.append(f"{key}: {expected} is 0 bytes")
            continue
        compared.append(f"{key}({size} bytes)")

    if failures:
        _print_fail(failures)
        return 1

    _print_pass(build_root, compared)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
