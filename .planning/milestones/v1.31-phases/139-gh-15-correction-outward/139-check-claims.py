#!/usr/bin/env python3
"""Forbidden-overclaim / required-caveat scanner for Phase 139's two named
outward-facing artifacts: `139-GH15-COMMENT.md` (the gh#15 correction
comment -- THE deliverable) and `139-GH15-BODY-AMENDMENT.md` (its optional,
default-skipped issue-body replacement).

This module is a Phase-139-scoped REPLACEMENT for, not a copy, fork,
subclass or env-seam of, the v1.30 checker hosted in Phase 137's own
directory. Research proved by five executed probes that the v1.30 checker
cannot perform this phase's D-05 check: its default targets resolve to
four v1.30 filenames that do not exist here, which makes an unmodified copy
scan nothing and report success; an explicitly-targeted run against this
milestone's draft fails on a required caveat this milestone's comment has
no business asserting; and, most importantly, its forbidden-phrase
detection is scoped to a proximity window keyed on tokens (a silicon-lock
part-family name, a three-letter protection acronym, and one specific
protocol id) that never appear in this milestone's `0x07`/`0x08`/`0x0B`
vocabulary -- so a file carrying four planted overclaims was measured to
scan clean under that window. This module carries none of that: no
proximity window of any kind, this milestone's own forbidden vocabulary,
and this milestone's own required caveat -- the ~6.25 V program-VCC
ceiling, which ISSUE-02 already requires the correction comment to state,
making this gate and that requirement the same check.

Only the pure mechanics below are adapted from the Phase 137 donor script
(read for reference, never imported, subclassed, or env-seamed): the
`_HERE` construction, `resolve_targets`'s argv/env/defaults precedence, the
hoisted never-vacuous guard, the fail-closed missing-target branch,
`_print_bucket`, and the shape of the `PASS:` line. Its vocabulary, its
proximity window, its required caveat, and its early-return branch that
reports readiness before its own target artifacts are authored are all
absent from this module by design -- see this plan's own SUMMARY for the
executed, recorded proof.

Exit codes:
  0 -- every resolved target exists on disk, contains zero forbidden-phrase
       matches anywhere in its text, and carries both required caveats (a
       `PASS:` line naming every scanned file, by path relative to this
       module's own directory, is printed).
  1 -- the default-targets self-check fails (a `_DEFAULT_TARGETS` entry is
       not local to this module's own directory, or does not carry this
       phase's own "139-" prefix), OR zero targets resolved (never-vacuous),
       OR a resolved target is missing from disk (fail-closed), OR at least
       one forbidden-phrase match was found anywhere in a scanned file, OR
       a scanned file is missing one or both required caveats. A bucketed
       `FAIL:` summary is printed for every failure case except the
       self-check, which prints its own `FAIL:` line per offending entry.

**Explicit non-claim #1 (load-bearing):** a green run of this gate -- at
any point in this phase -- is the mechanizable half of the ISSUE-02 / D-05
honesty discipline only. It cannot detect an implied overclaim, a
misleading omission, or wrong tone. That is ISSUE-03's blocking operator
wording review, in plan 139-05. A green run of this gate must never be
reported, in any SUMMARY, citation register, or Phase 139 artifact itself,
as by itself satisfying that discipline.

**Explicit non-claim #2 (scope, load-bearing):** this script is
*compliance* with the spirit of Phase 146's CLOSE-01 claim gate, and is
**not a build of it** -- CLOSE-01 is a Deferred Idea for this phase. It
forbids and requires nothing beyond what ISSUE-02 and D-05 already state,
and it scans exactly two files.
"""

import os
import re
import sys

# Module-top path constant. This is the ONLY directory `_DEFAULT_TARGETS`
# below is ever built from -- never a sibling-directory string constant.
# This construction is what stops the cross-phase-copy defect where a
# checker's defaults silently resolved to a stale sibling phase directory
# and passed vacuously with nothing actually scanned.
_HERE = os.path.dirname(os.path.abspath(__file__))

# Explicit two-element default target list -- this phase's own two named
# outward artifacts. Never a wildcard expansion, never a recursive
# directory walk of any kind.
_DEFAULT_TARGETS = [
    os.path.join(_HERE, "139-GH15-COMMENT.md"),
    os.path.join(_HERE, "139-GH15-BODY-AMENDMENT.md"),
]

# Env-override seam, SUFFIXED `_V131`: three prior checkers in this project
# already use the bare or `_V130`-suffixed name, and a collision would let
# one phase's seam silently retarget another phase's gate.
# `os.environ.get(...)` with NO default is deliberate: it must return None
# when the variable is absent from the environment so resolve_targets()
# below can tell "absent -> use defaults" apart from "present but empty ->
# zero targets, never a silent fall-back to defaults".
FIRESTARTER_CLAIMSCAN_TARGETS_V131 = os.environ.get(
    "FIRESTARTER_CLAIMSCAN_TARGETS_V131"
)

# Twelve forbidden-phrase labels/patterns, all case-insensitive, carrying
# this milestone's own vocabulary. No proximity window and no relational
# rule of any kind gates any of these -- every match anywhere in a scanned
# file's text is a violation, full stop.
FORBIDDEN_PATTERNS = [
    ("datasheet-conformant", re.compile(r"datasheet[-\s]conformant", re.IGNORECASE)),
    ("datasheet-correct", re.compile(r"datasheet[-\s]correct", re.IGNORECASE)),
    ("algorithm-accurate", re.compile(r"algorithm[-\s]accurate", re.IGNORECASE)),
    (
        "datasheet-compound-unqualified",
        re.compile(
            r"datasheet[-\s](?:conforming|compliant|faithful|exact|perfect|true)",
            re.IGNORECASE,
        ),
    ),
    (
        "verified-on-silicon",
        re.compile(
            r"verified\s+(?:on|against)\s+(?:real\s+)?silicon", re.IGNORECASE
        ),
    ),
    ("silicon-verified", re.compile(r"silicon[-\s]verified", re.IGNORECASE)),
    ("confirmed-working", re.compile(r"confirmed\s+working", re.IGNORECASE)),
    (
        "works-on-silicon",
        re.compile(r"works?\s+on\s+(?:\w+\s+){0,2}silicon", re.IGNORECASE),
    ),
    (
        "proven-on-silicon",
        re.compile(r"proven\s+on\s+(?:\w+\s+){0,2}silicon", re.IGNORECASE),
    ),
    ("proven-unqualified", re.compile(r"\bproven\b", re.IGNORECASE)),
    ("now-works", re.compile(r"now\s+works?\b", re.IGNORECASE)),
    ("should-now-work", re.compile(r"should\s+now\s+work", re.IGNORECASE)),
]

# Two required-caveat labels, each of which must match at least once in
# EACH scanned file. This is the design choice that makes this gate and
# ISSUE-02 the same check: ISSUE-02 requires the ~6.25 V program-VCC
# ceiling stated plainly, so the gate requires it too.
REQUIRED_CAVEAT_PATTERNS = [
    (
        "ceiling-voltage",
        "the ~6.25 V program-VCC ceiling",
        re.compile(r"6\.25\s*V"),
    ),
    (
        "ceiling-narrowing",
        "the silicon-margin narrowing that ceiling implies",
        re.compile(r"silicon[-\s]margin", re.IGNORECASE),
    ),
]


def _assert_default_targets_are_local():
    """Startup self-check -- called first thing in main(), before target
    resolution or any scanning. Fails loudly, naming the offending entry
    and the exact defect, for every `_DEFAULT_TARGETS` entry that either
    does not resolve inside this module's own directory (`_HERE`) or does
    not carry this phase's own "139-" prefix.

    This is the run-time equivalent of a paired-test suite's mandatory
    cross-phase-copy legs, moved inside the script itself so a future copy
    of this file into another phase's directory fails loudly the first
    time it is run, rather than silently scanning nothing and reporting
    success.

    Returns True iff every `_DEFAULT_TARGETS` entry passes both checks;
    every failing entry is printed (not just the first) before this
    returns False.
    """
    all_local = True
    for entry in _DEFAULT_TARGETS:
        if os.path.dirname(entry) != _HERE:
            print(
                f"FAIL: _DEFAULT_TARGETS entry {entry!r} does not resolve "
                "inside this phase's own directory -- this is the exact "
                "cross-phase-copy defect this self-check exists to catch"
            )
            all_local = False
        if not os.path.basename(entry).startswith("139-"):
            print(
                f"FAIL: _DEFAULT_TARGETS entry {entry!r} does not carry "
                "this phase's own 139- prefix -- this is the exact "
                "stale-name defect this self-check exists to catch"
            )
            all_local = False
    return all_local


def resolve_targets(argv):
    """Resolve the scan target list.

    Precedence: explicit positional `argv` paths win; else the
    FIRESTARTER_CLAIMSCAN_TARGETS_V131 env seam if the variable is present
    in os.environ (checked via `is not None`, not truthiness -- an
    explicitly empty value must resolve to zero targets, never a silent
    fall-back to defaults); else `_DEFAULT_TARGETS`.

    Returns (targets, used_defaults): `used_defaults` is True only when
    neither argv nor the env seam was used.
    """
    if argv:
        return list(argv), False
    if FIRESTARTER_CLAIMSCAN_TARGETS_V131 is not None:
        return [
            p for p in FIRESTARTER_CLAIMSCAN_TARGETS_V131.split(os.pathsep) if p
        ], False
    return list(_DEFAULT_TARGETS), True


def scan_text(text, path):
    """Scan `text` (the full contents of the file at `path`) for forbidden-
    phrase matches and required-caveat presence.

    Carries NO proximity window and NO context condition of any kind:
    every regex match in FORBIDDEN_PATTERNS anywhere in `text` is recorded
    as a violation, full stop -- see the module docstring for why a
    proximity window is exactly what this milestone must not repeat.

    `path` is accepted so each call site threads the file it is scanning
    through explicitly and self-descriptively; the return shape below does
    not otherwise require it.

    Returns (forbidden_hits, missing_caveat_labels):
      forbidden_hits -- list of (label, matched_text, lineno) tuples, one
        per match, 1-based lineno.
      missing_caveat_labels -- set of REQUIRED_CAVEAT_PATTERNS labels whose
        regex did not match anywhere in `text` -- the caveats this file is
        missing, not the ones it has.
    """
    lines = text.splitlines()
    forbidden_hits = []
    for label, pattern in FORBIDDEN_PATTERNS:
        for lineno, line in enumerate(lines, start=1):
            for m in pattern.finditer(line):
                forbidden_hits.append((label, m.group(0), lineno))

    missing_caveat_labels = {
        label
        for label, _prose, pattern in REQUIRED_CAVEAT_PATTERNS
        if not pattern.search(text)
    }

    return forbidden_hits, missing_caveat_labels


def _print_bucket(label, violations):
    print(f"FAIL: {len(violations)} {label}:")
    for v in violations[:20]:
        print(f"  {v}")
    if len(violations) > 20:
        print(f"  ... and {len(violations) - 20} more")


def main(argv):
    """Entry point.

    Order of operations: the default-targets self-check FIRST, before any
    target resolution; resolve targets; the hoisted never-vacuous guard;
    partition into existing/missing; the fail-closed missing-target
    branch; then scan every existing target and report.

    Deliberately absent: any early-return branch that reports readiness
    when every default target is missing. Phase 139 authors its two named
    artifacts in the same task that writes this gate, so there is no
    pre-authored window to protect, and keeping an exit-0-on-nothing-
    scanned path here would cost real detection for no benefit.
    """
    if not _assert_default_targets_are_local():
        return 1

    targets, _used_defaults = resolve_targets(argv)

    if not targets:
        print(
            "FAIL: no scan targets resolved -- the gate cannot vacuously "
            "pass with nothing scanned"
        )
        return 1

    missing = [t for t in targets if not os.path.isfile(t)]

    if missing:
        print(
            "FAIL: scan target(s) not found on disk -- the gate cannot "
            f"vacuously pass with a target silently skipped: {missing}"
        )
        return 1

    forbidden_violations = []
    caveat_violations = []
    scanned = []
    caveat_present_count = 0
    caveat_prose_by_label = {
        label: prose for label, prose, _pattern in REQUIRED_CAVEAT_PATTERNS
    }

    for t in targets:
        with open(t, encoding="utf-8") as f:
            text = f.read()
        scanned.append(t)
        hits, missing_labels = scan_text(text, t)
        for label, matched_text, lineno in hits:
            forbidden_violations.append(
                f"{t}:{lineno}: forbidden phrase match [{label}]: {matched_text!r}"
            )
        if missing_labels:
            for label in sorted(missing_labels):
                caveat_violations.append(
                    f"{t}: missing required caveat [{label}]: expected a "
                    f"phrase matching {caveat_prose_by_label[label]!r}"
                )
        else:
            caveat_present_count += 1

    if forbidden_violations or caveat_violations:
        if forbidden_violations:
            _print_bucket("forbidden phrase match(es)", forbidden_violations)
        if caveat_violations:
            _print_bucket(
                "file(s) missing a required 6.25 V ceiling caveat",
                caveat_violations,
            )
        return 1

    print(
        f"PASS: scanned {', '.join(os.path.relpath(s, _HERE) for s in scanned)}; "
        f"{caveat_present_count} file(s) carry both required caveats "
        "(this PASS is the mechanizable half of the ISSUE-02 / D-05 "
        "discipline only -- see the module docstring's explicit non-claim)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
