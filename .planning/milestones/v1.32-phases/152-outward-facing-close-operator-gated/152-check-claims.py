#!/usr/bin/env python3
"""Forbidden-overclaim / required-caveat scanner over Phase 152's own claim
contract, `152-CLAIM-CLASSES.md`, and (once later plans extend the list)
every other artifact this phase publishes.

**This module IS OUT-05's phase-local claim gate.** OUT-05 asks for a
fail-provable machine gate armed against the real artifacts this phase
writes, seen to fail on a planted violation before any pass is believed;
this script is that gate's scanning half, and the paired suite plus the
committed plant-and-revert transcript (`152-CLAIM-GATE-TRANSCRIPTS.md`) are
its two proofs.

It is a Phase-152-scoped **sibling** of Phase 149's gate, not a copy, fork,
subclass or env-seam of it. Source: `149-check-claims.py` in
`.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/`, read in
full. The pure mechanics adapted from it are the module-top
`__file__`-derived directory constant, `resolve_targets`'s argv/env/defaults
precedence with its load-bearing `is not None` env check, the hoisted
never-vacuous guard and the fail-closed missing-target branch,
`_print_bucket`'s 20-entry display cap, and seventeen of its own forbidden
patterns plus the module skeleton itself, transcribed unchanged.

**Mandatory renames distinguish this sibling from its donor**, exactly as
the donor itself required of Phase 146's gate before it:

1. `_DEFAULT_TARGETS` is this phase's own claim contract, `152-CLAIM-CLASSES.md`
   — one entry, enumerated, never a wildcard expansion and never a recursive
   directory traversal. Later plans extend this list only once their own
   artifact exists on disk (149's own ordering trap: an entry absent from
   disk makes this gate return rc=1, with no exit-0-on-nothing-scanned escape
   hatch to protect it). The phase's final `152-NN-SUMMARY.md` is instead
   scanned via positional argv, once written — see `152-RESEARCH.md` §C-7.
   A wildcard `152-`-prefixed default set would sweep in `152-CONTEXT.md`,
   `152-RESEARCH.md`, `152-DISCUSSION-LOG.md`, `152-VALIDATION.md` and
   `152-PATTERNS.md` (each carrying the forbidden vocabulary as discussion
   prose), the fixtures directory (whose planted files exist precisely to be
   violations), and `152-CLAIM-GATE-TRANSCRIPTS.md` itself (whose RED blocks
   necessarily quote forbidden text as evidence). Every `152-NN-PLAN.md` is
   out for the same reason. All of those stay permanently out of
   `_DEFAULT_TARGETS`, by design, not by oversight.
2. The self-check's phase-number prefix literal is `"152-"` in **both**
   places -- the `startswith` call and the failure message it prints. The
   donor carries its own prefix in both; changing only the call leaves a
   message that names the wrong phase, which is a silent documentation
   defect no fixture leg can observe.
3. The env-override seam is `FIRESTARTER_CLAIMSCAN_TARGETS_152`. The donor's
   `_149`-suffixed name is a distinct live checker in a sibling phase
   directory -- reusing either it or a bare/milestone-suffixed name would let
   one phase's seam retarget another phase's gate, or let one test suite aim
   two live checkers at once. The suffix is the phase number rather than the
   milestone for exactly that reason.
4. This docstring and its explicit non-claim are retargeted at **OUT-05** and
   at **D-03's per-artifact blocking operator gates** -- the review this gate
   does not discharge. The donor's own closing paragraph names PGSZ-05 and
   plan 08's human wording review; this one names OUT-05 and D-03.

**The fifth forbidden class -- the hardest problem this phase's table
carries, per `152-RESEARCH.md` §C-4.** Criterion 4 *requires* the two
release-note bodies to name `write --sdp-relock` explicitly, as withdrawn.
Criterion 5 *forbids* naming it as shipped. The same literal string is
mandatory in one framing and forbidden in another. Three approaches were
rejected before this one: a bare pattern on the string rejects criterion 4's
own mandated sentence outright; a verb allow-list (forbidding it only near
"ships"/"available"/"use") **fails OPEN by construction** -- any unlisted
phrasing, e.g. "Protecting a part: `write --sdp-relock`", passes; and a
proximity window is explicitly refused by this project's own D-14 precedent
(Phase 139 measured a windowed scanner passing four planted overclaims). The
solution is a **negative lookahead requiring an adjacent withdrawal
predicate immediately after the command name** -- one row, same table shape,
fails CLOSED, and mandates one canonical word order. A *lookbehind* cannot be
used here: Python's `re` module requires fixed-width lookbehinds, and the
natural prose order puts the withdrawal predicate *after* the command name,
not before it, so only a (variable-width-capable) lookahead can express the
constraint.

⚠ **The optional backtick must live INSIDE the lookahead, never in the
consumed part.** A first derivation wrote the backtick as part of the
consumed literal, ahead of the lookahead; the engine then backtracked off
that consumed backtick, the lookahead inspected the backtick itself, the
withdrawal alternation failed to match a bare backtick, and the pattern
permitted **nothing** -- measured as 7/7 false HITs on every allowed
withdrawal sentence in the derivation session. This bug is not obvious and a
re-derivation will hit it again; the fix is keeping `` `? `` inside the
lookahead's own alternation, as written below. `[VERIFIED: python3 re, 18
assertions (11 reject + 7 allow), 0 failures, 2026-08-21]`

**The bare-flag companion row** guards the same claim without the word
`write` in front of it -- "the `--sdp-relock` option is available" -- using
the SAME lookahead shape, but distinguished from the row above by a
**fixed-width negative lookbehind** `(?<!write )` so it cannot double-fire on
text the row above already caught. This is what preserves per-label leg
isolation in the paired suite's meta test. `152-RESEARCH.md` records this
companion as designed-but-untested at derivation time (Assumptions Log A3);
this plan's fixtures test it in both directions.

**`issue-closed` is MODIFIED, not transcribed unchanged.** `152-RESEARCH.md`
§C-5 measured a second inherited-row collision CONTEXT did not flag: D-05
requires this phase to state that gh#32 was closed (a measured 2026-08-08
fact, not a claim this milestone is making), and the donor's row --
`gh#(?:21|32|11|12)\b...` -- blocks the natural phrasings of that fact. `32`
is dropped from the alternation. This is a narrowing to the true claim class
("claiming an issue this milestone did not close is closed"), not a
loosening: gh#21, gh#11 and gh#12 must all still fire, and are proven by
three dedicated fixtures.

**The `proven-unqualified` row is kept VERBATIM, unlike `issue-closed`.**
`152-RESEARCH.md` §C-6 recommends no change: "software-proven and
unvalidated on silicon" is this milestone's established vocabulary in three
measured places (149's own required-caveat row, `153-RECORD.md`'s "What was
NOT proven" section, and `firestarter/README.md`'s Protocol Notes), so
re-deriving a different spelling would only re-derive the same lookbehind
narrowing risk the donor's own docstring already warns against. Do not widen
the `(?<!software-)` lookbehind past exactly that one prefix -- doing so
would silently also permit "bench-proven", "datasheet-proven" and
"silicon-proven".

**This scan carries no window and no exclusion mechanism**, per the donor's
own D-14 precedent. No proximity window, no context condition, no
exclusion-by-heading quarantine, no inline allow-marker: every match anywhere
in a scanned file's text is a violation. Phase 139 measured why -- a windowed
scanner keyed on tokens absent from this milestone's vocabulary passed a file
carrying four planted overclaims. That measurement is Phase 139's, cited here
rather than re-made.

Exit codes:
  0 -- every resolved target exists on disk, contains zero forbidden-phrase
       matches anywhere in its text, and carries every caveat this phase's
       own per-file rule demands of it (a `PASS:` line naming every scanned
       file, by path relative to this module's own directory, is printed).
  1 -- the default-targets self-check fails (a `_DEFAULT_TARGETS` entry is
       not local to this module's own directory, or does not carry this
       phase's own "152-" prefix), OR zero targets resolved (never-vacuous),
       OR a resolved target is missing from disk (fail-closed), OR at least
       one forbidden-phrase match was found anywhere in a scanned file, OR a
       scanned file is missing a caveat its own rule requires. A bucketed
       `FAIL:` summary is printed for every failure case except the
       self-check, which prints its own `FAIL:` line per offending entry.

There is deliberately **no branch that exits 0 when nothing was scanned.**
Phase 137's checker carried one (`check_permitted_claims.py:302-312`) to
protect a window before its own targets were authored; it is not ported
here, because an exit-0-on-nothing-scanned path is a green that proves
nothing, and because this gate's whole purpose is to be armed against files
that must exist.

**Explicit non-claim (load-bearing, transcribed from the donor):** a green
run of this gate, at any point in this phase, is compliance with the
forbidden-phrase table and the per-file caveat rule **only**. It cannot
detect an implied overclaim, a misleading omission, a wrong tone, or a true
statement placed where it misleads. That non-claim is why D-03's per-artifact
blocking operator wording review is not optional and is not discharged by a
green run of this script alone.
"""

import os
import re
import sys

# Module-top path constant. This is the ONLY directory `_DEFAULT_TARGETS`
# below is ever built from -- never a sibling-directory string constant.
# This construction is what stops the cross-phase-copy defect where a
# checker's defaults silently resolved to a stale sibling phase directory
# and passed vacuously with nothing actually scanned.
# Source: `149-check-claims.py:128`, copied verbatim.
_HERE = os.path.dirname(os.path.abspath(__file__))

# EIGHT entries as of Plan 152-19: this phase's own claim contract, the six
# outward drafts, and now `152-LEDGER.md` itself -- the three GitHub comment
# drafts, both release-note bodies, the merge record, and the honesty
# ledger. Plan 152-01 armed this gate at the one artifact that existed in
# wave 1; Plan 152-13 extended it to the six real outward artifacts the
# phase had written by wave 7; this plan (152-19) adds the seventh real
# artifact and eighth entry, `152-LEDGER.md`, per `152-RESEARCH.md` §C-7 and
# `152-PATTERNS.md` Pattern F, and per D-12's own reasoning: the ledger is
# where the narrowed pairing discipline now lives, which is exactly why it
# must itself be gate-scanned.
#
# ORDERING RULE (Pattern F, restated here because a future editor WILL need
# it): an entry is added to this list only once its artifact exists on disk,
# because the never-vacuous and fail-closed-on-missing branches below have NO
# exit-0-on-nothing-scanned escape hatch -- any entry absent from disk makes
# this gate return rc=1 with no recovery branch. `152-LEDGER.md` now exists
# on disk (written by this same plan, before this edit) and is added here.
# `_CAVEAT_RULES` already carries a pre-populated entry for it (Plan 152-01),
# so this is a one-line addition with no accompanying caveat-map edit. The
# phase's own `152-NN-SUMMARY.md` files are added only in the FINAL plan
# (152-20), and even then the last one is scanned via positional argv rather
# than added here, because that plan is still writing it when it runs -- see
# `152-CLAIM-GATE-TRANSCRIPTS.md`'s "Final target list" section.
#
# Never a wildcard expansion, never a recursive directory traversal: a
# wildcard `152-`-prefixed default set would sweep in `152-CONTEXT.md`,
# `152-RESEARCH.md`, `152-DISCUSSION-LOG.md`, `152-VALIDATION.md`,
# `152-PATTERNS.md` and `152-CLASS-SIZES.md` (each carrying the forbidden
# vocabulary as discussion prose), the fixtures directory (whose planted
# files exist precisely to be violations), `152-CLAIM-GATE-TRANSCRIPTS.md`
# (whose RED blocks quote forbidden text as evidence by design), every
# `152-NN-PLAN.md`, and every `.diff`. All of those stay permanently out of
# this list, by design, not by oversight.
_DEFAULT_TARGETS = [
    os.path.join(_HERE, "152-CLAIM-CLASSES.md"),
    os.path.join(_HERE, "152-GH12-COMMENT.md"),
    os.path.join(_HERE, "152-GH21-COMMENT.md"),
    os.path.join(_HERE, "152-GH11-COMMENT.md"),
    os.path.join(_HERE, "152-RELEASE-NOTES-app.md"),
    os.path.join(_HERE, "152-RELEASE-NOTES-fw.md"),
    os.path.join(_HERE, "152-MERGE-RECORD.md"),
    os.path.join(_HERE, "152-LEDGER.md"),
    # Every plan SUMMARY through 152-19. `152-20-SUMMARY.md` is DELIBERATELY
    # ABSENT: it does not exist while Plan 152-20 runs, and the fail-closed
    # missing-target branch would drive this gate non-zero for the remainder of
    # the phase. It is scanned instead via positional argv, after 152-20's own
    # SUMMARY is written -- see the transcript's "Final target list" section.
    # Do NOT "fix" this by adding a twentieth entry or by globbing.
    os.path.join(_HERE, "152-01-SUMMARY.md"),
    os.path.join(_HERE, "152-02-SUMMARY.md"),
    os.path.join(_HERE, "152-03-SUMMARY.md"),
    os.path.join(_HERE, "152-04-SUMMARY.md"),
    os.path.join(_HERE, "152-05-SUMMARY.md"),
    os.path.join(_HERE, "152-06-SUMMARY.md"),
    os.path.join(_HERE, "152-07-SUMMARY.md"),
    os.path.join(_HERE, "152-08-SUMMARY.md"),
    os.path.join(_HERE, "152-09-SUMMARY.md"),
    os.path.join(_HERE, "152-10-SUMMARY.md"),
    os.path.join(_HERE, "152-11-SUMMARY.md"),
    os.path.join(_HERE, "152-12-SUMMARY.md"),
    os.path.join(_HERE, "152-13-SUMMARY.md"),
    os.path.join(_HERE, "152-14-SUMMARY.md"),
    os.path.join(_HERE, "152-15-SUMMARY.md"),
    os.path.join(_HERE, "152-16-SUMMARY.md"),
    os.path.join(_HERE, "152-17-SUMMARY.md"),
    os.path.join(_HERE, "152-18-SUMMARY.md"),
    os.path.join(_HERE, "152-19-SUMMARY.md"),
]

# POSTED-MODE BASENAME RULE (recorded here because this is where the
# mechanism lives): `_required_caveats_for()` below is keyed on
# `os.path.basename(path)` and fails closed to the FULL caveat set for any
# basename absent from `_CAVEAT_RULES`. A posted GitHub comment body carries
# no release-note caveat requirement (see `_CAVEAT_RULES["152-GH12-COMMENT.md"]`
# etc. above, each an empty or narrow subset) -- so when a posting plan writes
# the just-posted body out to a temp file to re-verify it byte-for-byte, that
# temp file MUST be written under the SAME basename as the draft it verifies
# (e.g. a posted-mode copy of the gh#12 comment is named `152-GH12-COMMENT.md`
# in its own temp directory, not `posted-gh12.md` or similar). Any other
# basename resolves to the fail-closed full caveat set and would report a
# false missing-caveat failure against a comment body that was never required
# to carry a release-note qualifier in the first place. The posting plans
# (152-14 through 152-18) are the consumers of this rule.

# Env-override seam, SUFFIXED `_152`: the donor's `_149` name is a distinct
# live checker in a sibling phase directory, and bare/milestone-suffixed
# names are already live in yet other phases of this project -- a collision
# would let one phase's seam silently retarget another phase's gate, or let
# one test suite aim two live checkers at once. The suffix is the phase
# number rather than the milestone for exactly that reason.
# `os.environ.get(...)` with NO default is deliberate: it must return None
# when the variable is absent from the environment so resolve_targets() below
# can tell "absent -> use defaults" apart from "present but empty -> zero
# targets, never a silent fall-back to defaults".
FIRESTARTER_CLAIMSCAN_TARGETS_152 = os.environ.get(
    "FIRESTARTER_CLAIMSCAN_TARGETS_152"
)

# Nineteen forbidden-phrase labels/patterns, all case-insensitive, carrying
# this milestone's own vocabulary. The first seventeen rows are the donor's
# table transcribed unchanged EXCEPT for `issue-closed` (see the module
# docstring and `152-RESEARCH.md` §C-5); the final two rows are this phase's
# own additions for the fifth forbidden class. No proximity window and no
# relational rule of any kind gates any of these -- every match anywhere in a
# scanned file's text is a violation, full stop.
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
    # MODIFIED (Plan 152-13): a fixed-width negative lookbehind `(?<!un)` was
    # added ahead of `verified`. The donor's row, with no leading word
    # boundary, false-positived on the NON-claim "UNVERIFIED on silicon" --
    # reproduced empirically in this plan and recorded in
    # `152-CLAIM-GATE-TRANSCRIPTS.md`. This milestone's three canonical
    # required caveats all phrase the non-claim as "stays UNVERIFIED in
    # PROTOCOL-LEDGER" (not "...on silicon"), so no shipped artifact hit this
    # before now -- but any future outward text stating the non-claim in the
    # most natural English ("still UNVERIFIED on silicon") would have tripped
    # a forbidden-phrase failure for saying the OPPOSITE of the forbidden
    # claim. `(?<!un)` is a 2-character fixed-width lookbehind (Python's `re`
    # requires fixed width), case-insensitive by the compiled flag, so it
    # also suppresses "UNVERIFIED" and "Un-verified"'s "verified" half is
    # still adjacent (no space/hyphen between "un" and "verified" in this
    # milestone's own usage, confirmed by fixture). Do not widen this
    # lookbehind past exactly "un" -- the same over-widening risk the
    # `proven-unqualified` row's docstring warns against applies here.
    (
        "verified-on-silicon",
        re.compile(
            r"(?<!un)verified\s+(?:on|against)\s+(?:real\s+)?silicon",
            re.IGNORECASE,
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
    # Kept VERBATIM (152-RESEARCH.md §C-6): "software-proven and unvalidated
    # on silicon" is this milestone's established vocabulary in three
    # measured places (149's own required-caveat row, `153-RECORD.md`'s
    # "What was NOT proven" section, and `firestarter/README.md`'s Protocol
    # Notes). Still fires on a bare "proven", on "proven on silicon", on "the
    # write path is proven", on "bench-proven", on "silicon-proven" -- every
    # one of those is a DIFFERENT sequence of characters immediately before
    # the word than "software-", so the lookbehind does not suppress them.
    # Do not widen this past exactly the "software-" prefix below -- a
    # bare-hyphen form would silently also permit "bench-proven" and
    # "silicon-proven".
    ("proven-unqualified", re.compile(r"(?<!software-)\bproven\b", re.IGNORECASE)),
    ("now-works", re.compile(r"now\s+works?\b", re.IGNORECASE)),
    ("should-now-work", re.compile(r"should\s+now\s+work", re.IGNORECASE)),
    (
        "page-size-proven",
        re.compile(
            r"page[-\s]size\s+(?:is\s+)?(?:proven|verified|validated)",
            re.IGNORECASE,
        ),
    ),
    (
        "graduation",
        re.compile(
            r"(?:graduat\w+|promot\w+)\s+(?:\w+\s+){0,3}(?:0x0[Dd]|protocol\s+13)",
            re.IGNORECASE,
        ),
    ),
    (
        "support-status-change",
        re.compile(
            r"support_status\s*(?:[:=]|changed|updated|now)", re.IGNORECASE
        ),
    ),
    # MODIFIED (152-RESEARCH.md §C-5): `32` dropped from the alternation.
    # 149's row: r"gh#(?:21|32|11|12)\b(?:\s+\w+){0,3}\s+(?:closed|resolved|fixed)"
    # D-05 REQUIRES this phase to state that gh#32 is closed; the inherited
    # row blocked the natural phrasings of that measured 2026-08-08 fact.
    # Narrowing to the true claim class ("claiming an issue this milestone
    # did not close is closed"), not a loosening -- gh#21/#11/#12 all still
    # fire, proven by three fixture legs.
    (
        "issue-closed",
        re.compile(
            r"gh#(?:21|11|12)\b(?:\s+\w+){0,3}\s+(?:closed|resolved|fixed)",
            re.IGNORECASE,
        ),
    ),
    (
        "at28c256-fixed",
        re.compile(
            r"AT28C256\b(?:\s+\w+){0,4}\s+(?:fixed|works|now)", re.IGNORECASE
        ),
    ),
    # ADDED -- this phase's fifth forbidden class (152-RESEARCH.md §C-4):
    # criterion 5 forbids naming `write --sdp-relock` as shipped or
    # available. A bare pattern on the string would reject criterion 4's own
    # mandated withdrawal sentence; a verb allow-list (forbidding it only
    # near "ships"/"available"/"use") FAILS OPEN by construction, since any
    # unlisted phrasing passes; a Python lookbehind cannot be used because
    # `re` requires fixed-width lookbehinds while the natural prose order
    # puts the withdrawal predicate AFTER the command name. This negative
    # LOOKAHEAD -- reject unless a withdrawal predicate immediately follows
    # -- fails CLOSED and was measured 11/11 reject, 7/7 allow on
    # 2026-08-21. The optional backtick lives INSIDE the lookahead, never in
    # the consumed part -- see the module docstring for the 7/7 false-HIT bug
    # a misplaced backtick produces.
    (
        "sdp-relock-as-shipped",
        re.compile(
            r"write\s+--sdp-relock"
            r"(?!`?\s*(?:(?:is|stays|remains|was)\s+)?(?:still\s+)?"
            r"(?:withdrawn|deferred|not\s+shipped|not\s+shipping|unavailable|absent))",
            re.IGNORECASE,
        ),
    ),
    # ADDED -- the bare-flag companion to `sdp-relock-as-shipped`, for text
    # naming `--sdp-relock` as available without the word "write" in front
    # of it (e.g. "the `--sdp-relock` option is available"). Same withdrawal
    # lookahead, but distinguished by a FIXED-WIDTH negative lookbehind
    # `(?<!write )` so it cannot double-fire on the same text the row above
    # already caught -- this is what preserves per-label leg isolation in
    # the paired suite's meta test. `152-RESEARCH.md` records this companion
    # as designed-but-untested at derivation time (Assumptions Log A3); this
    # plan's fixtures test it in both directions.
    (
        "sdp-relock-flag-as-shipped",
        re.compile(
            r"(?<!write )--sdp-relock"
            r"(?!`?\s*(?:(?:is|stays|remains|was)\s+)?(?:still\s+)?"
            r"(?:withdrawn|deferred|not\s+shipped|not\s+shipping|unavailable|absent))",
            re.IGNORECASE,
        ),
    ),
]

# Three required-caveat labels (152-RESEARCH.md §C-6, refined): D-11's
# content -- "no AT28C part tested" and "0x0D stays UNVERIFIED" -- is split
# into two INDEPENDENTLY enforced rows rather than proposed as one, so each
# half has its own fixture and its own named failure. `software-proven-
# unvalidated` is the donor's row, transcribed verbatim.
#
# ⚠ D-11's word "once" (each release-note body carries the non-claim ONCE)
# is a CARDINALITY constraint this presence-only mechanism cannot express --
# 152-RESEARCH.md Assumptions Log A7. Presence is what is enforced here;
# "once" is a wording convention for the human review, not a machine rule.
# Do not imply a count is enforced when it is not.
REQUIRED_CAVEAT_PATTERNS = [
    (
        "software-proven-unvalidated",
        "the software-proven / unvalidated-on-silicon qualifier",
        re.compile(
            r"software[-\s]proven\s+and\s+unvalidated\s+on\s+silicon",
            re.IGNORECASE,
        ),
    ),
    (
        "no-at28c-part-tested",
        'the "no AT28C part was tested" qualifier',
        re.compile(
            r"no\s+at28c\s+part\s+was\s+tested",
            re.IGNORECASE,
        ),
    ),
    (
        "zero-d-stays-unverified",
        'the "0x0D stays UNVERIFIED in PROTOCOL-LEDGER" qualifier',
        re.compile(
            r"protocol\s+`?0x0[Dd]`?\s+stays\s+unverified\s+in\s+protocol-ledger",
            re.IGNORECASE,
        ),
    ),
]

# The full label set, derived from the table above rather than restated, so a
# new required-caveat pattern cannot be added without the fail-closed
# default below picking it up. Must not be restated.
_ALL_CAVEAT_LABELS = frozenset(
    label for label, _prose, _pattern in REQUIRED_CAVEAT_PATTERNS
)

# Per-basename caveat map. Keys are BASENAMES so the map cannot drift from
# `_DEFAULT_TARGETS`' `_HERE`-relative directory construction. Pre-populated
# now with EVERY basename this phase will ever scan, so no later plan has to
# edit this map and no two wave-3 plans collide on this file. Entries for
# files that do not exist yet are inert -- the map is keyed on basename and
# touches no disk. The fail-closed default in `_required_caveats_for()`
# below means an omitted entry demands the FULL caveat set anyway, so
# silence can never produce a silent exemption.
_CAVEAT_RULES = {
    "152-CLAIM-CLASSES.md": frozenset(
        {"software-proven-unvalidated", "no-at28c-part-tested", "zero-d-stays-unverified"}
    ),
    "152-GH12-COMMENT.md": frozenset({"no-at28c-part-tested"}),
    "152-GH21-COMMENT.md": frozenset({"no-at28c-part-tested"}),
    "152-GH11-COMMENT.md": frozenset({"no-at28c-part-tested"}),
    "152-RELEASE-NOTES-app.md": frozenset(
        {"software-proven-unvalidated", "no-at28c-part-tested", "zero-d-stays-unverified"}
    ),
    "152-RELEASE-NOTES-fw.md": frozenset(
        {"software-proven-unvalidated", "no-at28c-part-tested", "zero-d-stays-unverified"}
    ),
    "152-LEDGER.md": frozenset(
        {"software-proven-unvalidated", "no-at28c-part-tested", "zero-d-stays-unverified"}
    ),
    # A captured git/gh handoff record, not a claim register -- mirroring
    # the donor's own transcript exemption. Unlike the donor's, this one is
    # a LIVE target, so the exemption mechanism is behaviourally exercised,
    # not just introspected.
    "152-MERGE-RECORD.md": frozenset(),
    # Mirrors the donor's own D-11 exemption for its transcript file: a
    # committed evidence register of RED/GREEN gate runs, each block a
    # literal command plus its literal output, not a claim about the change
    # itself. Inert in normal operation -- this file is never a member of
    # `_DEFAULT_TARGETS` and is never passed via argv or the env seam by any
    # real invocation of this gate; it exists so the exemption mechanism
    # itself stays behaviourally proven rather than only introspected.
    "152-CLAIM-GATE-TRANSCRIPTS.md": frozenset(),
    "152-01-SUMMARY.md": frozenset({"software-proven-unvalidated"}),
    "152-02-SUMMARY.md": frozenset({"software-proven-unvalidated"}),
    "152-03-SUMMARY.md": frozenset({"software-proven-unvalidated"}),
    "152-04-SUMMARY.md": frozenset({"software-proven-unvalidated"}),
    "152-05-SUMMARY.md": frozenset({"software-proven-unvalidated"}),
    "152-06-SUMMARY.md": frozenset({"software-proven-unvalidated"}),
    "152-07-SUMMARY.md": frozenset({"software-proven-unvalidated"}),
    "152-08-SUMMARY.md": frozenset({"software-proven-unvalidated"}),
    "152-09-SUMMARY.md": frozenset({"software-proven-unvalidated"}),
    "152-10-SUMMARY.md": frozenset({"software-proven-unvalidated"}),
    "152-11-SUMMARY.md": frozenset({"software-proven-unvalidated"}),
    "152-12-SUMMARY.md": frozenset({"software-proven-unvalidated"}),
    "152-13-SUMMARY.md": frozenset({"software-proven-unvalidated"}),
    "152-14-SUMMARY.md": frozenset({"software-proven-unvalidated"}),
    "152-15-SUMMARY.md": frozenset({"software-proven-unvalidated"}),
    "152-16-SUMMARY.md": frozenset({"software-proven-unvalidated"}),
    "152-17-SUMMARY.md": frozenset({"software-proven-unvalidated"}),
    "152-18-SUMMARY.md": frozenset({"software-proven-unvalidated"}),
    "152-19-SUMMARY.md": frozenset({"software-proven-unvalidated"}),
    "152-20-SUMMARY.md": frozenset({"software-proven-unvalidated"}),
}


def _required_caveats_for(path):
    """Return the set of required-caveat labels that `path` must satisfy.

    Keyed on `os.path.basename(path)`, so an argv- or env-supplied absolute
    path resolves to the same rule as the `_DEFAULT_TARGETS` entry for the
    same artifact.

    Fails CLOSED on an unknown basename: a target with no `_CAVEAT_RULES`
    entry gets the FULL caveat set, never the empty set. An empty-set default
    would let a future edit disable the caveat check for a real artifact by
    renaming it -- silently, and with the gate still reporting PASS.
    """
    return _CAVEAT_RULES.get(os.path.basename(path), _ALL_CAVEAT_LABELS)


def _assert_default_targets_are_local():
    """Startup self-check -- called first thing in main(), before target
    resolution or any scanning. Fails loudly, naming the offending entry
    and the exact defect, for every `_DEFAULT_TARGETS` entry that either
    does not resolve inside this module's own directory (`_HERE`) or does
    not carry this phase's own "152-" prefix.

    This is the run-time equivalent of a paired-test suite's mandatory
    cross-phase-copy legs, moved inside the script itself so a future copy
    of this file into another phase's directory fails loudly the first
    time it is run, rather than silently scanning nothing and reporting
    success. Source: `149-check-claims.py:341-357`; the prefix literal is
    this phase's own in both the comparison and the printed message.

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
        if not os.path.basename(entry).startswith("152-"):
            print(
                f"FAIL: _DEFAULT_TARGETS entry {entry!r} does not carry "
                "this phase's own 152- prefix -- this is the exact "
                "stale-name defect this self-check exists to catch"
            )
            all_local = False
    return all_local


def resolve_targets(argv):
    """Resolve the scan target list.

    Precedence: explicit positional `argv` paths win; else the
    FIRESTARTER_CLAIMSCAN_TARGETS_152 env seam if the variable is present
    in os.environ (checked via `is not None`, not truthiness -- an
    explicitly empty value must resolve to zero targets, never a silent
    fall-back to defaults); else `_DEFAULT_TARGETS`.

    Returns (targets, used_defaults): `used_defaults` is True only when
    neither argv nor the env seam was used.
    """
    if argv:
        return list(argv), False
    if FIRESTARTER_CLAIMSCAN_TARGETS_152 is not None:
        return [
            p for p in FIRESTARTER_CLAIMSCAN_TARGETS_152.split(os.pathsep) if p
        ], False
    return list(_DEFAULT_TARGETS), True


def scan_text(text, path, required_caveats):
    """Scan `text` (the full contents of the file at `path`) for forbidden-
    phrase matches and for the presence of the caveats `required_caveats`
    demands of this particular file.

    Carries NO proximity window and NO context condition of any kind: every
    regex match in FORBIDDEN_PATTERNS anywhere in `text` is recorded as a
    violation, full stop -- see the module docstring for the measured reason
    (Phase 139's, cited not re-made) why a proximity window is exactly what
    this milestone must not repeat. There is likewise no exclusion-by-heading
    quarantine and no inline allow-marker.

    `path` is accepted so each call site threads the file it is scanning
    through explicitly and self-descriptively; the return shape below does
    not otherwise require it.

    `required_caveats` is the resolved per-file rule set, passed in rather
    than looked up here so the caller owns rule resolution and this function
    stays a pure scan. A label absent from `required_caveats` is not demanded
    of this file and can never appear in the returned missing set.

    Returns (forbidden_hits, missing_caveat_labels):
      forbidden_hits -- list of (label, matched_text, lineno) tuples, one
        per match, 1-based lineno.
      missing_caveat_labels -- set of the labels this file was REQUIRED to
        carry whose regex did not match anywhere in `text` -- the caveats
        this file is missing, not the ones it has, and never a caveat its own
        rule did not ask for.
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
        if label in required_caveats and not pattern.search(text)
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

    Order of operations, from `149-check-claims.py:434-447`: the
    default-targets self-check FIRST, before any target resolution; resolve
    targets; the hoisted never-vacuous guard; partition into
    existing/missing; the fail-closed missing-target branch; then scan every
    existing target against its own per-file caveat rule and report.

    Deliberately absent: any early-return branch that reports readiness when
    every default target is missing. An exit-0-on-nothing-scanned path costs
    real detection for no benefit, and this gate exists to be armed against
    files that must exist.
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
    caveat_required_count = 0
    caveat_satisfied_count = 0
    caveat_exempt_count = 0
    caveat_prose_by_label = {
        label: prose for label, prose, _pattern in REQUIRED_CAVEAT_PATTERNS
    }

    for t in targets:
        with open(t, encoding="utf-8") as f:
            text = f.read()
        scanned.append(t)
        required = _required_caveats_for(t)
        hits, missing_labels = scan_text(text, t, required)
        for label, matched_text, lineno in hits:
            forbidden_violations.append(
                f"{t}:{lineno}: forbidden phrase match [{label}]: {matched_text!r}"
            )
        if required:
            caveat_required_count += 1
        else:
            caveat_exempt_count += 1
        if missing_labels:
            for label in sorted(missing_labels):
                caveat_violations.append(
                    f"{t}: missing required caveat [{label}]: expected a "
                    f"phrase matching {caveat_prose_by_label[label]!r}"
                )
        elif required:
            caveat_satisfied_count += 1

    if forbidden_violations or caveat_violations:
        if forbidden_violations:
            _print_bucket("forbidden phrase match(es)", forbidden_violations)
        if caveat_violations:
            _print_bucket(
                "file(s) missing a required caveat",
                caveat_violations,
            )
        return 1

    # The caveat count is reported as satisfied-of-required plus an explicit
    # exempt count, mirroring the donor: under a future `_CAVEAT_RULES`
    # extension a target could legitimately carry no caveat requirement at
    # all, and this shape reports that honestly rather than as an
    # unearned pass or an unexplained gap.
    print(
        f"PASS: scanned {', '.join(os.path.relpath(s, _HERE) for s in scanned)}; "
        f"{caveat_satisfied_count} of {caveat_required_count} caveat-required "
        f"file(s) carry every caveat their own rule demands; "
        f"{caveat_exempt_count} file(s) carry no caveat requirement "
        "(this PASS is compliance with the forbidden-phrase table and the "
        "per-file caveat rule only -- see the module docstring's explicit "
        "non-claim, and note that a green run alone does not discharge "
        "D-03's per-artifact blocking operator wording review)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
