#!/usr/bin/env python3
"""Forbidden-overclaim / required-silicon-caveat scanner for v1.23's four
named closing artifacts (`130-LEDGER.md`, `130-DECISION.md`,
`130-RELEASE-NOTES-fw.md`, `130-RELEASE-NOTES-app.md`).

Distilled from `.planning/REQUIREMENTS.md` §"Validation Ceiling": *"No
PY32F071 PCB exists. Nothing in this milestone has ever run on this
silicon, and nothing in it can."* The permitted claims are that the target
builds clean; the native and host suites pass at their recorded case and
suite counts; the DFU sequence is exercised against device descriptors and
mocks; host-side timing and sizes are measured where a tool exists to
measure them. The forbidden claims are the eight patterns in
FORBIDDEN_PATTERNS below. This is a direct v1.23 adaptation of Phase 122's
`check_permitted_claims.py` (BASE-07) -- Research C-5 there proved an
overclaim of exactly this shape already reached a *locked* project decision
once, so this gate exists to mechanically catch the same class of mistake
in the phase's own outward-facing prose before it reaches a stranger.

Exit codes:
  0 -- either (a) every resolved target exists on disk, carries the
       required PY32F071 caveat, and contains zero forbidden-phrase matches
       within proximity of a py32 token (a `PASS:` line naming every
       scanned file is printed), or (b) the default target set was used and
       NONE of the four named v1.23 closing artifacts exists yet -- an
       `UNARMED:` notice naming Phase 130 is printed, per D-15's
       all-or-nothing arming (the close has not started).
  1 -- a resolved target is missing from disk (fail-closed), OR zero
       targets resolved (never-vacuous), OR the default target set is
       ARMED (at least one of the four named artifacts exists) but not
       every one of the four exists (D-15: the close is half written), OR
       at least one forbidden-phrase match co-occurs with a py32 token
       within the proximity window (D-16), OR a target lacks the required
       caveat (a bucketed `FAIL:` summary is printed in every failure
       case).

**Explicit non-claim (load-bearing):** a green run of this gate is the
mechanizable half of the milestone's honesty criterion ONLY. It cannot
detect an implied overclaim, a misleading omission, or wrong tone. A green
run of this gate must never be reported, in any SUMMARY, ledger entry, or
Phase 130 artifact itself, as by itself satisfying the milestone's honesty
criterion.

**Phase 130 coupling (load-bearing):** the four names in `_DEFAULT_TARGETS`
below are a contract recorded seven phases before anyone writes them. Phase
130 must either produce exactly these four artifact names, or amend this
list **in the same commit** that renames or adds one -- D-15's
all-or-nothing arming makes a renamed-but-not-reflected artifact a hard
failure by design, and that coupling is the entire point of naming the
targets this early. The four names now resolve inside the sibling Phase 130
directory (named by `_PHASE_130_DIRNAME` below), not `_HERE` (this module's
own Phase 123 directory) -- RESEARCH C-2 reproduced the old `_HERE`-relative
form as an `UNARMED:` + exit-0 run that scanned nothing, because the
artifacts are Phase 130's, not Phase 123's. This relocation is itself the
sanctioned same-commit amendment this paragraph requires, taken in Phase
130 plan 130-01 ahead of the artifacts so the gate is armed *before* the
first one lands rather than after.

**Why line-scoped proximity, not sentence segmentation (D-16):** markdown
tables, bullet lists and code blocks have no reliable sentence terminators,
and a naive `re.split(r'[.!?]')` mangles version numbers (`v1.23`), file
names (`check_permitted_claims.py`) and decimals. A 3-line window (one line
either side of a match) is simple, deterministic, has no tokenizer to get
wrong, and matches how these artifacts are actually written -- tables and
bullets, one claim per line.

**RESEARCH assumption A3 (env-var-name reuse):** this checker reuses v1.22's
`FIRESTARTER_CLAIMSCAN_TARGETS` env-var name verbatim rather than suffixing
it for v1.23. The two checkers live in different phase directories and
never coexist in one process, so this is safe today. If a future run ever
needed to scan both phases' artifacts in one process, one seam would aim
both checkers at once -- the fix at that point is to suffix the name (e.g.
`_V123`), not to reuse a single seam across two live scanners.
"""

import os
import re
import sys

# Module-top path constant (mirrors v1.22's `check_permitted_claims.py` and
# `check_note_append_only.py`'s shape).
_HERE = os.path.dirname(os.path.abspath(__file__))

# Explicit four-element default target list -- the v1.23 closing artifacts,
# NAMED NOW per D-15, seven phases before Phase 130 writes them. NEVER
# pattern-based and NEVER discovered by walking a directory tree. The
# `fixtures/` subdirectory deliberately contains violating text
# (planted_py32_overclaim.md, planted_missing_caveat.md) and must never be
# reachable from this default set -- if a future edit turns this into a
# wildcard-expanded or tree-walked set, the fixtures directory would poison
# every default-mode run. See the module docstring's "Phase 130 coupling"
# paragraph: Phase 130 must produce exactly these four names, or amend this
# list in the same commit that renames one.
#
# RESEARCH C-2 fix: this list used to resolve onto `_HERE` (this module's
# OWN Phase 123 directory), so a default-mode run scanned four paths that
# could never exist -- `UNARMED:` + exit 0, a green run that scanned
# nothing. The four names now resolve into the SIBLING Phase 130 directory
# instead, because that is where the artifacts actually land. The fix is a
# repoint of this list, deliberately NOT a switch to `argv` or
# `FIRESTARTER_CLAIMSCAN_TARGETS`: `main()`'s `used_defaults` branch below
# means D-15's all-or-nothing arming guarantee applies only to the DEFAULT
# target set, so routing this through an explicit seam instead would lose
# that guarantee for the one call site that matters most (an unqualified
# `python3 check_permitted_claims.py` in CI or by hand).
_PHASE_130_DIRNAME = "130-close-honesty-ledger-claim-gate-release-decision"
_CONTRACTED_ARTIFACT_NAMES = (
    "130-LEDGER.md",
    "130-DECISION.md",
    "130-RELEASE-NOTES-fw.md",
    "130-RELEASE-NOTES-app.md",
)
_PHASE_130_DIR = os.path.normpath(
    os.path.join(_HERE, os.pardir, _PHASE_130_DIRNAME)
)
_DEFAULT_TARGETS = [
    os.path.join(_PHASE_130_DIR, name) for name in _CONTRACTED_ARTIFACT_NAMES
]

# Env-override seam (mirrors check_no_community_support_status_write.py's
# FIRESTARTER_DISP01_REPORT and v1.22's own FIRESTARTER_CLAIMSCAN_TARGETS,
# reused verbatim -- see RESEARCH assumption A3 above): lets the paired
# pytest point this checker at deliberately-violating fixtures under
# fixtures/ without editing a real closing artifact. `os.environ.get(...)`
# with NO default is deliberate -- it must return None when
# FIRESTARTER_CLAIMSCAN_TARGETS is absent from the environment, and the
# (possibly empty) raw string when present, so resolve_targets() below can
# tell "absent -> use defaults" apart from "present-but-empty -> zero
# targets, never a silent fall-back to defaults". Values are split on
# os.pathsep; empty segments are dropped.
FIRESTARTER_CLAIMSCAN_TARGETS = os.environ.get("FIRESTARTER_CLAIMSCAN_TARGETS")

# Eight forbidden-phrase labels/patterns, all case-insensitive. Distilled
# from REQUIREMENTS.md's Validation Ceiling and cross-checked against
# research's independently-supplied table -- both sources agree on all
# eight. `flashed-a-py32` is research's own narrowing of the end-to-end
# claim (no direct REQUIREMENTS quote, but the same class of overclaim).
# `runs-on-py32` and `flashed-a-py32` are deliberately NARROWED to an
# explicit py32 object baked into the pattern itself (belt-and-braces with
# D-16's proximity scoping below); `works-end-to-end`, `silicon-verified`,
# `bench-validated`, `hardware-validated`, `closed-loop-vpp` and
# `pin-map-correct` are deliberately BROAD/unqualified, exactly as
# REQUIREMENTS quotes them ("unqualified"), and rely entirely on D-16's
# proximity window to avoid firing on the milestone's many true AVR
# sentences.
FORBIDDEN_PATTERNS = [
    ("runs-on-py32", re.compile(r"runs\s+on\s+(?:a\s+|the\s+)?py32", re.IGNORECASE)),
    (
        "works-end-to-end",
        re.compile(r"works\s+end[-\s]to[-\s]end", re.IGNORECASE),
    ),
    ("silicon-verified", re.compile(r"silicon[-\s]verified", re.IGNORECASE)),
    ("bench-validated", re.compile(r"bench[-\s]validated", re.IGNORECASE)),
    ("hardware-validated", re.compile(r"hardware[-\s]validated", re.IGNORECASE)),
    (
        "flashed-a-py32",
        re.compile(r"flashed\s+(?:a\s+|the\s+)?py32", re.IGNORECASE),
    ),
    (
        "closed-loop-vpp",
        re.compile(r"closed[-\s]loop\s+vpp\s+(?:works|verified)", re.IGNORECASE),
    ),
    (
        "pin-map-correct",
        re.compile(
            r"pin\s+map\s+(?:is\s+)?(?:correct|verified|validated)", re.IGNORECASE
        ),
    ),
]

# Canonical required-caveat sentence fragment, and its whitespace-tolerant
# regex. Deliberate interaction, recorded here rather than "fixed" by
# weakening the pattern set above (carried forward from v1.22, sharpened for
# D-16): an honest negated phrasing such as "nothing about the PY32F071 is
# silicon-verified" contains BOTH a py32 token and a forbidden phrase in the
# same proximity window, so it WILL trip the `silicon-verified` forbidden
# pattern. The correct response when that happens is to reword the artifact
# to use the canonical caveat sentence below, not to narrow FORBIDDEN_PATTERNS
# or PY32_TOKEN_RE to dodge the alarm -- the canonical caveat exists
# precisely so authors have an approved way to say this.
REQUIRED_CAVEAT_PROSE = "no PY32F071 hardware exists"
REQUIRED_CAVEAT_PATTERN = re.compile(
    r"no\s+PY32F071\s+hardware\s+exists", re.IGNORECASE
)

# D-16 proximity scoping. A forbidden-phrase match on line N is reported
# only if a py32 token appears on line N itself or within PROXIMITY_WINDOW
# lines either side (a 3-line window when PROXIMITY_WINDOW == 1). See the
# module docstring's "Why line-scoped proximity, not sentence segmentation"
# paragraph for why this is line-scoped rather than sentence-scoped.
PY32_TOKEN_RE = re.compile(r"py32", re.IGNORECASE)
PROXIMITY_WINDOW = 1


def scan_text(text):
    """Scan `text` for forbidden-phrase matches proximity-scoped to a py32
    token (D-16), and for required-caveat presence.

    Returns (forbidden_hits, caveat_present):
      forbidden_hits -- list of (label, matched_substring, line_number)
        tuples, one entry per match that co-occurs with a py32 token within
        PROXIMITY_WINDOW lines (1-indexed line_number). A label may appear
        more than once if its pattern matches multiple qualifying lines.
        A forbidden match with NO py32 token in its window is deliberately
        NOT reported -- this is D-16's suppression of true AVR statements
        such as "the Leonardo target remains bench-validated from v1.15".
      caveat_present -- bool, True iff REQUIRED_CAVEAT_PATTERN matches
        anywhere in the text (caveat presence is NOT proximity-scoped: the
        caveat is a document-level property, not a per-claim one).
    """
    lines = text.splitlines()
    py32_lines = {i for i, line in enumerate(lines) if PY32_TOKEN_RE.search(line)}

    forbidden_hits = []
    for label, pattern in FORBIDDEN_PATTERNS:
        for lineno, line in enumerate(lines):
            for m in pattern.finditer(line):
                window = range(
                    max(0, lineno - PROXIMITY_WINDOW),
                    min(len(lines), lineno + PROXIMITY_WINDOW + 1),
                )
                if any(w in py32_lines for w in window):
                    forbidden_hits.append((label, m.group(0), lineno + 1))

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
    """Entry point: resolve targets, scan each, exit non-zero on any
    violation.

    Deliberate hardening over v1.22's ordering: the never-vacuous guard (an
    explicitly empty resolved target list) is checked FIRST, above the
    missing-target guard, rather than after it. v1.22 ran the missing-target
    check first, which is vacuously satisfied by an empty list, with a
    second guard catching the empty case afterward -- correct but fragile,
    since a later early-return inserted between the two guards could
    silently reintroduce the vacuous pass. Hoisting removes that fragility;
    observable behaviour (both exit 1, with distinguishable messages) is
    unchanged.
    """
    targets = resolve_targets(argv)

    if not targets:
        # Universal never-vacuous guard: reached when argv or the env seam
        # explicitly resolves to zero targets. The gate can never vacuously
        # pass with nothing scanned. Note `_DEFAULT_TARGETS` above always
        # has 4 entries, so this branch is never reached via the default
        # path -- D-15 arming (below) is what governs that path instead.
        print(
            "FAIL: no scan targets resolved -- the gate cannot vacuously "
            "pass with nothing scanned"
        )
        return 1

    used_defaults = not argv and FIRESTARTER_CLAIMSCAN_TARGETS is None
    if used_defaults:
        # D-15 all-or-nothing arming. Arming applies ONLY to the default
        # target set -- when targets come from argv or the env seam, the
        # caller has named them explicitly and the ordinary fail-closed
        # guard below applies instead. This is the difference between "the
        # close has not started" (zero of the four named artifacts exist;
        # UNARMED, exit 0) and "the close is half written" (one or more
        # exist but not all four; hard failure).
        existing_count = sum(1 for t in targets if os.path.isfile(t))
        if existing_count == 0:
            print(
                "UNARMED: none of the 4 named v1.23 closing artifacts for "
                "Phase 130 exist yet (130-LEDGER.md, 130-DECISION.md, "
                "130-RELEASE-NOTES-fw.md, 130-RELEASE-NOTES-app.md) -- the "
                "close has not started, so the claim gate has nothing to "
                "scan yet. This is expected before Phase 130 runs."
            )
            return 0
        missing = [t for t in targets if not os.path.isfile(t)]
        if missing:
            print(
                "FAIL: armed (at least one of the 4 named v1.23 closing "
                "artifacts exists) but not all 4 exist -- a half-written "
                f"close is a hard failure (D-15). Missing: {missing}"
            )
            return 1
    else:
        # Ordinary fail-closed guard for explicitly-named targets (argv or
        # env seam) -- the caller named these paths explicitly, so a
        # missing one is always a hard failure, never a skip.
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
        "(this PASS is the mechanizable half of the honesty criterion only "
        "-- see the module docstring's explicit non-claim)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
