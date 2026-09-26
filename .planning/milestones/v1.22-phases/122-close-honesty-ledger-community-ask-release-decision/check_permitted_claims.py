#!/usr/bin/env python3
"""Forbidden-overclaim / required-silicon-caveat scanner for Phase 122's five
closing artifacts (`122-LEDGER.md`, `122-RELEASE-NOTES-fw.md`,
`122-RELEASE-NOTES-app.md`, `122-GH11-COMMENT.md`, `122-GH12-COMMENT.md`).

Distilled from `.planning/REQUIREMENTS.md` §"Validation Ceiling"'s permitted
claim ("the SDP lock and unlock sequences are emitted exactly as specified,
verified byte-exact by golden register trace across all four `0x0D`
pinouts, with a documented and measured host-side timing assumption") and its
forbidden claim ("SDP lock/unlock works on an AT28C256"). Research C-5 proved
an overclaim of exactly this shape already reached a *locked* project
decision (D-14), so this gate exists to mechanically catch the same class of
mistake in the phase's own outward-facing prose before it reaches a
stranger.

Exit codes:
  0 -- every resolved target exists on disk, carries the required silicon
       caveat, and contains zero forbidden-phrase matches (a `PASS:` line
       naming every scanned file is printed).
  1 -- a resolved target is missing from disk (fail-closed), OR zero targets
       resolved (never-vacuous), OR at least one forbidden-phrase match was
       found, OR a target lacks the required caveat (a bucketed `FAIL:`
       summary is printed).

**Explicit non-claim (load-bearing):** a green run of this gate is the
mechanizable half of ROADMAP criterion 4 ONLY. It cannot detect an implied
overclaim, a misleading omission, or wrong tone -- criterion 4 is closed by
this gate PLUS the D-16 blocking operator wording review (plan 122-11). A
green run of this gate must never be reported, in any SUMMARY or ledger
entry, as by itself satisfying criterion 4.
"""

import os
import re
import sys

# Module-top path constant (mirrors check_note_append_only.py's shape and
# check_no_community_support_status_write.py's `_HERE` idiom).
_HERE = os.path.dirname(os.path.abspath(__file__))

# Explicit five-element default target list -- NEVER pattern-based and
# NEVER discovered by walking a directory tree. The `fixtures/`
# subdirectory deliberately contains violating text
# (planted_forbidden_claim.md, planted_missing_caveat.md) and must never be
# reachable from this default set, the same discipline
# `firestarter_app/tests/fixtures/planted_log_in_window.cpp` observes
# relative to its own checker's scan targets. If a future edit turns this
# into a wildcard-expanded or tree-walked set, the fixtures directory would
# poison every default-mode run.
_DEFAULT_TARGETS = [
    os.path.join(_HERE, "122-LEDGER.md"),
    os.path.join(_HERE, "122-RELEASE-NOTES-fw.md"),
    os.path.join(_HERE, "122-RELEASE-NOTES-app.md"),
    os.path.join(_HERE, "122-GH11-COMMENT.md"),
    os.path.join(_HERE, "122-GH12-COMMENT.md"),
]

# Env-override seam (mirrors check_no_community_support_status_write.py's
# FIRESTARTER_DISP01_REPORT and check_devtest_orchestrator.py's
# FIRESTARTER_DEVTEST_SRC): lets the paired pytest point this checker at
# deliberately-violating fixtures under fixtures/ without editing a real
# closing artifact. `os.environ.get(...)` with NO default is deliberate --
# it must return None when FIRESTARTER_CLAIMSCAN_TARGETS is absent from the
# environment, and the (possibly empty) raw string when present, so
# resolve_targets() below can tell "absent -> use defaults" apart from
# "present-but-empty -> zero targets, never a silent fall-back to
# defaults". Values are split on os.pathsep; empty segments are dropped.
FIRESTARTER_CLAIMSCAN_TARGETS = os.environ.get("FIRESTARTER_CLAIMSCAN_TARGETS")

# Eight forbidden-phrase labels/patterns, all case-insensitive.
# `122-VALIDATION.md`'s example list is prefixed "e.g." -- this table is a
# closed set distilled from it, not a verbatim copy. Two entries
# (`works-on-silicon`, `proven-on-silicon`) are deliberately NARROWED to a
# silicon/AT28C object so the gate stays a real signal instead of firing on
# unrelated prose such as "works on the merged tree"; `now-works` is kept
# broad on purpose because C-5's actual near-miss ("AT28C parts should now
# work") had no object qualifier to anchor on.
FORBIDDEN_PATTERNS = [
    ("verified-fixed", re.compile(r"verified\s+fixed", re.IGNORECASE)),
    ("confirmed-working", re.compile(r"confirmed\s+working", re.IGNORECASE)),
    ("silicon-verified", re.compile(r"silicon[-\s]verified", re.IGNORECASE)),
    (
        "verified-on-silicon",
        re.compile(
            r"verified\s+(?:on|against)\s+(?:real\s+)?(?:at28c\w*|silicon)",
            re.IGNORECASE,
        ),
    ),
    (
        "works-on-silicon",
        re.compile(
            r"works?\s+on\s+(?:\w+\s+){0,2}(?:at28c\w*|silicon)", re.IGNORECASE
        ),
    ),
    ("now-works", re.compile(r"now\s+works?\b", re.IGNORECASE)),
    ("should-now-work", re.compile(r"should\s+now\s+work", re.IGNORECASE)),
    (
        "proven-on-silicon",
        re.compile(
            r"proven\s+on\s+(?:\w+\s+){0,2}(?:at28c\w*|silicon)", re.IGNORECASE
        ),
    ),
]

# Canonical required-caveat sentence fragment, and its whitespace-tolerant
# regex. Deliberate interaction, recorded here rather than "fixed" by
# weakening the pattern set above: an honest negated phrasing such as
# "nothing is silicon-verified here" WILL trip the `silicon-verified`
# forbidden pattern. The correct response when that happens is to reword the
# artifact to use the canonical caveat sentence below, not to narrow
# FORBIDDEN_PATTERNS to dodge the false alarm.
REQUIRED_CAVEAT_PROSE = "no AT28C silicon was tested"
REQUIRED_CAVEAT_PATTERN = re.compile(
    r"no\s+AT28C\s+silicon\s+was\s+tested", re.IGNORECASE
)


def scan_text(text):
    """Scan `text` for forbidden-phrase matches and required-caveat presence.

    Returns (forbidden_hits, caveat_present):
      forbidden_hits -- list of (label, matched_substring) tuples, one entry
        per match (a label may appear more than once if its pattern matches
        multiple times in the text).
      caveat_present -- bool, True iff REQUIRED_CAVEAT_PATTERN matches
        anywhere in the text.
    """
    forbidden_hits = []
    for label, pattern in FORBIDDEN_PATTERNS:
        for m in pattern.finditer(text):
            forbidden_hits.append((label, m.group(0)))
    caveat_present = bool(REQUIRED_CAVEAT_PATTERN.search(text))
    return forbidden_hits, caveat_present


def resolve_targets(argv):
    """Resolve the scan target list.

    Precedence: explicit positional `argv` paths win; else the
    FIRESTARTER_CLAIMSCAN_TARGETS env seam if the variable is present in
    os.environ (checked via `is not None`, not truthiness -- an explicitly
    empty value must resolve to zero targets, never a silent fall-back to
    defaults); else `_DEFAULT_TARGETS`.
    """
    if argv:
        return list(argv)
    if FIRESTARTER_CLAIMSCAN_TARGETS is not None:
        return [p for p in FIRESTARTER_CLAIMSCAN_TARGETS.split(os.pathsep) if p]
    return list(_DEFAULT_TARGETS)


def _print_bucket(label, violations):
    print(f"FAIL: {len(violations)} {label}:")
    for v in violations[:20]:
        print(f"  {v}")
    if len(violations) > 20:
        print(f"  ... and {len(violations) - 20} more")


def main(argv):
    """Entry point: resolve targets, scan each, exit non-zero on any violation."""
    targets = resolve_targets(argv)

    missing = [t for t in targets if not os.path.isfile(t)]
    if missing:
        print(
            "FAIL: scan target(s) not found on disk -- the gate cannot "
            f"vacuously pass with a target silently skipped: {missing}"
        )
        return 1

    if not targets:
        # Defense in depth: reached only when the env seam is explicitly set
        # to the empty string (or argv resolves to an empty list some other
        # way) -- the missing-target guard above is vacuously satisfied by
        # an empty list, so this is the real never-vacuous guard.
        print(
            "FAIL: no scan targets resolved -- the gate cannot vacuously "
            "pass with nothing scanned"
        )
        return 1

    forbidden_violations = []
    caveat_violations = []
    scanned = []
    caveat_present_count = 0

    for t in targets:
        with open(t, encoding="utf-8") as f:
            text = f.read()
        scanned.append(t)
        hits, caveat_present = scan_text(text)
        for label, substr in hits:
            forbidden_violations.append(
                f"{t}: forbidden phrase match [{label}]: {substr!r}"
            )
        if caveat_present:
            caveat_present_count += 1
        else:
            caveat_violations.append(
                f"{t}: missing required silicon caveat "
                f"(expected a phrase matching {REQUIRED_CAVEAT_PROSE!r})"
            )

    if forbidden_violations or caveat_violations:
        if forbidden_violations:
            _print_bucket("forbidden phrase match(es)", forbidden_violations)
        if caveat_violations:
            _print_bucket("missing required silicon caveat", caveat_violations)
        return 1

    print(
        f"PASS: scanned {', '.join(os.path.relpath(s, _HERE) for s in scanned)}; "
        f"{caveat_present_count} file(s) carry the required silicon caveat "
        "(this PASS is the mechanizable half of criterion 4 only -- see the "
        "module docstring's explicit non-claim)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
