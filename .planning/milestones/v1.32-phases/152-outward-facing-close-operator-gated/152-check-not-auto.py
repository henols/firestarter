#!/usr/bin/env python3
"""Fail-closed guard against an auto/chained run reaching a public post.

**This module answers `152-RESEARCH.md`'s Open Questions §5 with a
mechanism, not a restatement.** That question asked whether the
`--auto`/`--chain` prohibition is mechanically enforceable at all; the
project's own measurements say `--auto`/`--chain` **auto-approve**
human-verify checkpoints, and that `autonomous: false` alone is **not**
self-protecting (see `152-CONTEXT.md` D-03's accepted-cost note and this
project's own `reference_auto_mode_autoapproves_outward_facing_gates`
finding). This script is the one thing in this phase that actually READS
the live configuration and fails the process before a post can happen, run
as the FIRST automated check in every posting plan (152-14 through
152-18).

Behaviour:
  - Reads `.planning/config.json`'s `workflow._auto_chain_active` key --
    the exact key name confirmed against the live configuration file, not
    an assumed one (`152-RESEARCH.md` Open Questions §5; also load-bearing
    in this milestone's own memory record of the `--auto`/`--chain`
    auto-approval finding).
  - Exits **non-zero** if that key is truthy: an auto or chained run
    auto-approves the human-verify checkpoints this phase's D-03 relies on
    as its primary control, so a truthy flag means this run cannot be
    trusted to have had a human review any of the outward artifacts.
  - Exits **non-zero**, not zero, on EVERY uncertain path: the configuration
    file missing, unreadable, unparseable as JSON, lacking a `workflow`
    object, or lacking the `_auto_chain_active` key entirely. An unknown
    state is not a safe state -- this is the same fail-closed discipline
    `152-check-claims.py` uses for a missing scan target, and it is the
    entire value of this guard. Every failure message names the key, the
    value (or the absence/error), and the file path it was read from.
  - Exits **0** only when the key is present, the value is `False` (or
    another value this script's `_is_falsy()` recognises as explicitly
    falsy), and the whole read path completed without error.

⚠ **Explicit non-claim, load-bearing, must be understood before this guard
is trusted for more than it is:** this guard fails closed **if** the
orchestrator writes `workflow._auto_chain_active` truthy into
`.planning/config.json` before an auto/chained run reaches this phase's
posting plans. This project has **not observed the write path** for that
flag -- it is read here, never written, and no measurement in this phase
confirms which code path sets it or when. This script is therefore a REAL
control over a REAL read of a REAL configuration value, and it is **NOT** a
proof that an auto/chained run cannot reach a public post through some
other path this project has not yet measured. D-03's per-artifact blocking
operator checkpoints, and the operator's own discipline in never invoking
`--auto`/`--chain` on this phase, remain the primary controls. This
docstring states that residual risk rather than dissolving it into an
implied guarantee.

Exit codes:
  0 -- the key was read successfully and is explicitly falsy.
  1 -- the key is truthy, OR the configuration file is missing/unreadable/
       unparseable, OR the `workflow` object or the key itself is absent.
       Every case prints a message naming the key, the offending value (or
       error), and the file path.
"""

import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))

# The live configuration file this guard defaults to when --config is not
# given: three levels up from this phase directory
# (`.planning/phases/152-.../` -> `.planning/phases/` -> `.planning/`), i.e.
# `.planning/config.json`. Fixtures pass their own --config path instead, so
# this default is exercised only by the "live repo state" leg.
_DEFAULT_CONFIG_PATH = os.path.normpath(
    os.path.join(_HERE, "..", "..", "config.json")
)

_KEY_PATH = ("workflow", "_auto_chain_active")


def _is_falsy(value):
    """Return True iff `value` is explicitly and unambiguously falsy.

    Only `False` (the JSON `false` literal) is treated as falsy. Every other
    value -- `True`, a truthy string like `"true"`, a nonzero number, `None`,
    an empty string, an empty dict -- is NOT recognised as falsy here and
    therefore does not clear this guard. This is deliberately narrower than
    Python's own truthiness: an ambiguous value (e.g. the string `"false"`,
    which is truthy in Python) must not silently pass as safe. Only the
    unambiguous boolean `False` clears the guard.
    """
    return value is False


def _read_flag(config_path):
    """Read `workflow._auto_chain_active` from `config_path`.

    Returns (state, detail):
      state  -- one of "falsy", "truthy", "missing_file", "read_error",
                "missing_key".
      detail -- the value read (for "falsy"/"truthy"), or a short string
                describing the failure (for the other three states).

    Never raises -- every failure mode is caught and reported as a state,
    because this function's whole job is to turn every possible failure into
    an explicit, named, non-exceptional outcome the caller can act on.
    """
    if not os.path.isfile(config_path):
        return "missing_file", f"no such file: {config_path!r}"

    try:
        with open(config_path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        return "read_error", f"{type(exc).__name__}: {exc}"

    if not isinstance(data, dict):
        return "read_error", (
            f"top-level JSON is a {type(data).__name__}, expected an object"
        )

    node = data
    for segment in _KEY_PATH:
        if not isinstance(node, dict) or segment not in node:
            return "missing_key", (
                f"{'.'.join(_KEY_PATH)!r} is absent from {config_path!r} "
                f"(stopped at {segment!r})"
            )
        node = node[segment]

    if _is_falsy(node):
        return "falsy", node
    return "truthy", node


def main(argv):
    config_path = _DEFAULT_CONFIG_PATH
    if argv:
        if argv[0] == "--config" and len(argv) >= 2:
            config_path = argv[1]
        elif argv[0].startswith("--config="):
            config_path = argv[0].split("=", 1)[1]
        else:
            print(
                f"FAIL: unrecognised argv {argv!r} -- expected "
                "'--config PATH' or '--config=PATH', or no arguments at "
                "all (defaults to the live configuration)"
            )
            return 1

    key_name = ".".join(_KEY_PATH)
    state, detail = _read_flag(config_path)

    if state == "falsy":
        print(
            f"PASS: {key_name!r} is explicitly False in {config_path!r} -- "
            "no auto/chained run is active according to this read"
        )
        return 0

    if state == "truthy":
        print(
            f"FAIL: {key_name!r} is {detail!r} in {config_path!r} -- an "
            "auto or chained run auto-approves human-verify checkpoints, "
            "and every outward requirement in this phase is "
            "operator-reviewed before posting (152-CONTEXT.md D-03). "
            "Refusing to proceed."
        )
        return 1

    if state == "missing_file":
        print(
            f"FAIL: cannot determine {key_name!r} -- {detail} -- an unknown "
            "state is not a safe state. Refusing to proceed."
        )
        return 1

    if state == "read_error":
        print(
            f"FAIL: cannot determine {key_name!r} from {config_path!r} -- "
            f"{detail} -- an unknown state is not a safe state. Refusing "
            "to proceed."
        )
        return 1

    # state == "missing_key"
    print(
        f"FAIL: cannot determine {key_name!r} -- {detail} -- an unknown "
        "state is not a safe state. Refusing to proceed."
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
