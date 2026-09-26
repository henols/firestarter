#!/usr/bin/env python3
"""Forbidden-overclaim / required-silicon-caveat scanner for v1.30's four
named closing artifacts (`137-LEDGER.md`, `137-DECISION.md`,
`137-RELEASE-NOTES-app.md`, `137-GH12-COMMENT.md`).

Distilled from `.planning/REQUIREMENTS.md`'s "Evidence Ceiling" section: no
AT28C part has ever been in operator inventory and protocol `0x0D` stays
`UNVERIFIED`. What is provable this milestone is the *plan derivation* (43
ALLOW / 41 REFUSE), the *read-back comparison logic* in native envs, and SDP
command *emission* only to the extent the host can observe it. What is NOT
provable is the causal claim "the lock inhibited the write" -- that is
reachable only from a community `dev test` report on real silicon, which by
design does not gate this milestone's close. This checker is a v1.30 fork of
`.planning/phases/122-close-honesty-ledger-community-ask-release-decision/check_permitted_claims.py`
(VOCABULARY donor -- the eight AT28C/silicon forbidden patterns and the
caveat shape) and
`.planning/phases/123-non-regression-baselines-gate-hardening/check_permitted_claims.py`
(MECHANICS donor -- the proximity-window scoping, the all-or-nothing arming
branch, and the hoisted never-vacuous guard), per PITFALLS.md P-11's exact
prescription. It is mechanically distinct from both: a suffixed env seam
(`FIRESTARTER_CLAIMSCAN_TARGETS_V130`), a renamed paired test module
(`test_check_permitted_claims_v130.py`), six added forbidden patterns plus a
relational self-verifying rule, and two dedicated tests proving its default
targets cannot resolve outside its own directory.

Exit codes:
  0 -- either (a) every resolved target exists on disk, carries the required
       AT28C caveat, and contains zero forbidden-phrase matches within
       proximity of an SDP/AT28C/0x0D context token (a `PASS:` line naming
       every scanned file is printed), or (b) the default target set was
       used and NONE of the four named v1.30 closing artifacts exists yet --
       an `UNARMED:` notice naming Phase 137 is printed (the close has not
       started; this is the expected, legitimate pre-authored state).
  1 -- a resolved target is missing from disk (fail-closed), OR zero targets
       resolved (never-vacuous), OR the default target set is ARMED (at
       least one of the four named artifacts exists) but not every one of
       the four exists (a half-written close is a hard failure -- a partial
       set is NEVER treated as UNARMED), OR at least one forbidden-phrase
       match co-occurs with an SDP/AT28C/0x0D context token within the
       proximity window, OR a target lacks the required caveat (a bucketed
       `FAIL:` summary is printed in every failure case).

**Explicit non-claim (load-bearing):** a green run of this gate -- at any
point in the phase -- is the mechanizable half of CLOSE-04's honesty ledger
discipline only. It cannot detect an implied overclaim, a misleading
omission, or wrong tone. That is CLOSE-06's blocking operator wording review
(plan 137-05). A green run of this gate must never be reported, in any
SUMMARY, ledger entry, or Phase 137 artifact itself, as by itself satisfying
the honesty ledger discipline.

**The `_HERE`-resolves-to-the-checker's-own-dir trap (load-bearing,
avoided by construction here):** a prior claim-gate checker (v1.23's copy,
hosted in Phase 123's own directory) named its four target artifacts against
a *sibling* phase directory via a hardcoded string constant
(`_PHASE_130_DIRNAME`). A naive future copy of that pattern into yet another
phase directory silently resolves its targets somewhere else entirely --
scanning nothing and exiting 0, a green that proves absolutely nothing (see
`reference_check_permitted_claims_here_resolves_wrong_phase_dir` in project
memory). This module avoids that trap by construction: it is authored AND
hosted inside Phase 137's own directory, `_DEFAULT_TARGETS` below is built
from `_HERE` alone -- this module's own directory, computed fresh from
`__file__` -- with no sibling-directory string constant anywhere in this
file. `test_check_permitted_claims_v130.py`'s two mandatory P-11 legs
(`test_default_targets_resolve_inside_this_phase_directory` and
`test_default_target_basenames_are_this_milestones`) exist specifically to
make a future naive copy of *this* file fail loudly instead of repeating the
same silent-vacuous-pass mistake a third time.
"""

import os
import re
import sys

# Module-top path constant (mirrors both donor checkers' shape). This is the
# ONLY directory `_DEFAULT_TARGETS` below is ever built from -- never a
# sibling-directory string constant, unlike the v1.23 copy this module's own
# docstring names as the anti-pattern to not repeat.
_HERE = os.path.dirname(os.path.abspath(__file__))

# Explicit four-element default target list -- the v1.30 closing artifacts.
# Never a wildcard expansion, never a recursive directory walk of any kind.
# The `fixtures/` subdirectory deliberately contains violating text and must
# never be reachable from this list -- if a future edit turns this into a
# wildcard-expanded or recursively-walked set, the fixtures directory would
# poison every default-mode run.
_DEFAULT_TARGETS = [
    os.path.join(_HERE, "137-LEDGER.md"),
    os.path.join(_HERE, "137-DECISION.md"),
    os.path.join(_HERE, "137-RELEASE-NOTES-app.md"),
    os.path.join(_HERE, "137-GH12-COMMENT.md"),
]

# Env-override seam, SUFFIXED (`_V130`) per PITFALLS P-11 point 5 to avoid
# colliding with the un-suffixed env-var name the two prior copies (Phase
# 122's and Phase 123's) already use -- a third scanner sharing one seam
# name would let one test suite's env var aim two live checkers at once.
# `os.environ.get(...)` with NO default is deliberate -- it must
# return None when FIRESTARTER_CLAIMSCAN_TARGETS_V130 is absent from the
# environment, and the (possibly empty) raw string when present, so
# resolve_targets() below can tell "absent -> use defaults" apart from
# "present-but-empty -> zero targets, never a silent fall-back to
# defaults". Values are split on os.pathsep; empty segments are dropped.
FIRESTARTER_CLAIMSCAN_TARGETS_V130 = os.environ.get(
    "FIRESTARTER_CLAIMSCAN_TARGETS_V130"
)

# D-16-style proximity-window context tokens (v1.23 mechanics, adapted from
# its `py32` token to this milestone's own domain): AT28C part numbers, the
# bare word "SDP", and the protocol id "0x0D".
_SDP_CONTEXT_TOKENS = re.compile(r"at28c\w*|\bsdp\b|0x0d", re.IGNORECASE)

# Fourteen forbidden-phrase labels/patterns, all case-insensitive. The first
# eight are forked VERBATIM from Phase 122's copy (same labels, same
# regexes) -- the vocabulary that already correctly detects the v1.22 C-5
# overclaim shape. The remaining six are v1.30-specific, distilled from
# PITFALLS.md P-11 point 2's own list and cross-checked against
# REQUIREMENTS.md's Evidence Ceiling section -- both sources agree.
FORBIDDEN_PATTERNS = [
    # -- forked verbatim from Phase 122's check_permitted_claims.py --
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
    # -- v1.30-specific additions, PITFALLS.md P-11 point 2 --
    (
        "lock-inhibited-the-write",
        re.compile(r"lock\s+inhibited\s+the\s+write", re.IGNORECASE),
    ),
    (
        # Do not confuse with the literal rendered enum values HELD/NOT-HELD
        # from chip_test.sdp_hold_state() -- those are permitted data, not a
        # prose causal claim. This pattern requires the words "the", "lock",
        # "held" in that order.
        "lock-held-unqualified",
        re.compile(r"\bthe\s+lock\s+held\b", re.IGNORECASE),
    ),
    ("proven-behaviour", re.compile(r"proven\s+behaviou?r", re.IGNORECASE)),
    (
        "behaviourally-verified",
        re.compile(r"behaviou?rally\s+verified", re.IGNORECASE),
    ),
    ("now-proven", re.compile(r"now\s+proven\b", re.IGNORECASE)),
    (
        "dev-test-proves-unqualified",
        re.compile(r"dev\s+test\s+proves\b", re.IGNORECASE),
    ),
]

# "self-verifying" is handled separately from FORBIDDEN_PATTERNS because its
# rule is RELATIONAL (absence of a nearby qualifier), not a bare match -- see
# scan_text() below.
_SELF_VERIFYING_PATTERN = re.compile(r"self-verifying", re.IGNORECASE)

# Canonical required-caveat sentence fragment, and its whitespace-tolerant
# regex -- reused verbatim from Phase 122's copy. The ceiling sentence is
# unchanged in substance for v1.30: "no AT28C silicon was tested" is still
# exactly right.
REQUIRED_CAVEAT_PROSE = "no AT28C silicon was tested"
REQUIRED_CAVEAT_PATTERN = re.compile(
    r"no\s+AT28C\s+silicon\s+was\s+tested", re.IGNORECASE
)


def scan_text(text):
    """Scan `text` for forbidden-phrase matches proximity-scoped to an
    SDP/AT28C/0x0D context token, and for required-caveat presence.

    Returns (forbidden_hits, caveat_present):
      forbidden_hits -- list of (label, matched_substring, line_number)
        tuples, one entry per match that co-occurs with an
        `_SDP_CONTEXT_TOKENS` hit (OR the required caveat pattern itself --
        mostly redundant with the token check since the caveat sentence
        names "AT28C", but kept explicit per the self-verifying rule below)
        within the proximity window (lines [i-1, i, i+1], clamped to
        bounds; 1-indexed line_number in the tuple). This is a recorded,
        accepted false-negative risk (a genuinely bad sentence with no
        nearby SDP/AT28C/0x0D token would be missed) -- deliberately
        accepted because all four of this phase's real target artifacts are
        entirely about this milestone's SDP work, matching v1.23's own
        accepted trade-off for its `py32` window.
      caveat_present -- bool, True iff REQUIRED_CAVEAT_PATTERN matches
        anywhere in the text (caveat presence is NOT proximity-scoped: the
        caveat is a document-level property, not a per-claim one).
    """
    lines = text.splitlines()
    n = len(lines)

    def _window(i):
        return range(max(0, i - 1), min(n, i + 2))

    def _sdp_context_in_window(i):
        return any(_SDP_CONTEXT_TOKENS.search(lines[w]) for w in _window(i))

    def _caveat_in_window(i):
        return any(REQUIRED_CAVEAT_PATTERN.search(lines[w]) for w in _window(i))

    def _emission_in_window(i):
        return any("emission" in lines[w].lower() for w in _window(i))

    forbidden_hits = []

    for label, pattern in FORBIDDEN_PATTERNS:
        for lineno, line in enumerate(lines):
            for m in pattern.finditer(line):
                if _sdp_context_in_window(lineno) or _caveat_in_window(lineno):
                    forbidden_hits.append((label, m.group(0), lineno + 1))

    # self-verifying rule (relational): a bare "self-verifying" near an SDP
    # context token is a violation UNLESS the immediately surrounding lines
    # also carry the qualifier "emission" or the required caveat itself --
    # e.g. "a self-verifying SDP lifecycle for lock EMISSION" is permitted;
    # bare "the new SDP lifecycle is self-verifying" with no nearby
    # qualifier is not.
    for lineno, line in enumerate(lines):
        for m in _SELF_VERIFYING_PATTERN.finditer(line):
            in_scope = _sdp_context_in_window(lineno) or _caveat_in_window(lineno)
            if not in_scope:
                continue
            qualified = _emission_in_window(lineno) or _caveat_in_window(lineno)
            if not qualified:
                forbidden_hits.append(("self-verifying", m.group(0), lineno + 1))

    caveat_present = bool(REQUIRED_CAVEAT_PATTERN.search(text))
    return forbidden_hits, caveat_present


def resolve_targets(argv):
    """Resolve the scan target list.

    Precedence: explicit positional `argv` paths win; else the
    FIRESTARTER_CLAIMSCAN_TARGETS_V130 env seam if the variable is present
    in os.environ (checked via `is not None`, not truthiness -- an
    explicitly empty value must resolve to zero targets, never a silent
    fall-back to defaults); else `_DEFAULT_TARGETS`.

    Returns (targets, used_defaults): `used_defaults` is True only when
    neither argv nor the env seam was used -- `main()` needs this to know
    whether the all-or-nothing arming branch applies (it applies ONLY to
    the default target set; explicitly-named targets always take the
    ordinary fail-closed branch).
    """
    if argv:
        return list(argv), False
    if FIRESTARTER_CLAIMSCAN_TARGETS_V130 is not None:
        return [
            p for p in FIRESTARTER_CLAIMSCAN_TARGETS_V130.split(os.pathsep) if p
        ], False
    return list(_DEFAULT_TARGETS), True


def _print_bucket(label, violations):
    print(f"FAIL: {len(violations)} {label}:")
    for v in violations[:20]:
        print(f"  {v}")
    if len(violations) > 20:
        print(f"  ... and {len(violations) - 20} more")


def main(argv):
    """Entry point: resolve targets, scan each, exit non-zero on any
    violation.

    Hoisted never-vacuous guard FIRST (v1.23 hardening, ahead of the
    missing-file check): an explicitly-empty resolved target list is always
    a hard failure, checked before anything else so a later inserted
    early-return cannot silently reintroduce a vacuous pass.
    """
    targets, used_defaults = resolve_targets(argv)

    if not targets:
        print(
            "FAIL: no scan targets resolved -- the gate cannot vacuously "
            "pass with nothing scanned"
        )
        return 1

    missing = [t for t in targets if not os.path.isfile(t)]

    # All-or-nothing arming (v1.23 D-15 mechanics) -- applies ONLY when the
    # default target set was used. A partial set (1, 2, or 3 of 4 present)
    # is NEVER armed -- that is the actually dangerous state a lone
    # UNARMED: would mask, so it falls through to the ordinary fail-closed
    # branch below, same as v1.23's own design.
    if used_defaults and len(missing) == len(targets):
        print(
            "UNARMED: none of Phase 137's 4 named closing artifacts exist "
            "yet ("
            + ", ".join(os.path.basename(t) for t in _DEFAULT_TARGETS)
            + ") -- Phase 137's four closing artifacts do not exist yet -- "
            "this is expected before they are authored, not a failure."
        )
        return 0

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

    for t in targets:
        with open(t, encoding="utf-8") as f:
            text = f.read()
        scanned.append(t)
        hits, caveat_present = scan_text(text)
        for label, substr, lineno in hits:
            forbidden_violations.append(
                f"{t}:{lineno}: forbidden phrase match [{label}]: {substr!r}"
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
        "(this PASS is the mechanizable half of the honesty ledger "
        "discipline only -- see the module docstring's explicit non-claim)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
