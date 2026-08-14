"""
Project Name: Firestarter
Copyright (c) 2024 Henrik Olsson

Permission is hereby granted under MIT license.

Phase 144 Plan 01 (D-01) -- authors the machine-checked requirement->case
mapping gate: a pytest module that parses the three v131 Unity suites under
test/native/avr/, extracts every RUN_TEST(...) case name, and asserts that
each of TEST-01...TEST-05 names cases which actually exist.

Requirements: TEST-01, TEST-02, TEST-03, TEST-04, TEST-05 (this plan does
NOT mark any of them Complete -- 144-01-PLAN.md's own scope note assigns
all eight requirement flips of Phase 144 to plan 144-07; this module is
evidence for that later flip, not the flip itself).

Defect class this closes: a requirement flipped Complete against a native
case that is later renamed or deleted, with nothing re-checking that the
case named in prose still exists. 144-CONTEXT.md's own D-01 names the
concrete instance: CONTEXT.md's prose nominates "the two fallback cases"
for TEST-05, which names no existing pair at all -- the real shape is SIX
cases in two families of three (C-04, corrected in _REQUIREMENT_CASES
below). A prose-only mapping table is the same shape as the hollow parity
legs a prior phase (120) had to rebuild -- this module exists so the map is
machine-checked instead.

This module maps requirements onto pre-existing coverage; it authors no new
native RUN_TEST case and edits no file under src/ (D-04). The 88 existing
cases across the three suites mapped here (test_loop_eprom_v131 47,
test_vpp_eprom_v131 32, test_eprom_params_v131 9) were authored across
Phases 140 and 141 and are exercised by `pio test -e native_loop_v131` and
`pio test -e native_params_v131` -- neither of which this module invokes;
this module scans their SOURCE TEXT only, independently of whatever a
PlatformIO run reports, so a case that compiles but was silently renamed in
a way that still compiles is still caught here.

Coverage:
  1. test_every_mapped_requirement_names_only_existing_cases -- D-01's core
     assertion: every case name each of TEST-01...TEST-05 is mapped against
     is proven to exist in the union of RUN_TEST names extracted from the
     three mapped suites. A missing case fails naming the requirement id,
     the missing case name, and the mapped-suite files scanned -- never a
     bare "lists differ".
  2. test_each_mapped_suite_meets_its_hardcoded_case_floor -- per-suite
     extracted count >= its hardcoded floor (47 / 32 / 9). A future
     deletion that still leaves every MAPPED case present (because the
     deleted case belonged to none of TEST-01...05) would slip past
     Coverage 1 alone; this floor catches it.
  3. test_extracted_case_names_are_unique -- a duplicate RUN_TEST name
     would silently inflate a suite's extracted count and could mask an
     unrelated rename hiding behind the duplicate's presence.
  4. test_trace_suite_is_deliberately_out_of_scope -- test_trace_eprom_v131
     is asserted absent from _MAPPED_SUITES, and (when its source is
     reachable under the current scan target) its source is asserted to
     still contain the #ifdef guard this exclusion's reasoning depends on --
     so the exclusion reason stays machine-checked rather than becoming
     folklore. test_trace_eprom_v131's sixth RUN_TEST sits inside
     `#ifdef EPROM_V131_TRACE_DUMP`, which no env defines (C-05); it proves
     TEST-06, not TEST-01...05, and belongs to a different plan entirely.
  5. test_scan_targets_are_non_vacuous -- self-protection, two halves. Part
     (a) recomputes the DEFAULT scan root fresh from _REPO_ROOT WITHOUT
     reading os.environ at all, and checks it is sane. Part (b) runs the
     extractor against whatever _SCAN_SUITES CURRENTLY resolves to (the
     SAME seam-aware target every leg above scans) and requires the union
     to meet the hardcoded _TOTAL_FLOOR (88) -- this is the half an
     emptied or misdirected scan root turns RED, proving that scenario
     fails closed here instead of making every membership check in
     Coverage 1 pass vacuously over an empty set.
  6. test_this_module_cannot_be_silently_skipped -- this module's own
     source contains no skip-bypass call, no skip-marker decorator, and no
     import-or-skip call anywhere, each needle concatenation-built.
  7. test_own_needles_do_not_appear_verbatim_in_this_module -- every
     concatenation-built needle from Coverage 6 appears NOWHERE verbatim in
     this module's own source.

Environment seams: (this repository has no central environment-variable
inventory -- this docstring is the only place a reader can discover them,
mirroring tests/test_ack_layout_source_contract_v143.py's own convention)
  - FIRESTARTER_CASE_MAP_SCAN_ROOT -- overrides the scanned suite ROOT
    (test/native/avr) ONLY -- never a floor literal, never a case name,
    never the mapped-suite set. Consulted by Coverage 1, 2, 3, 4's second
    half, and the SECOND half of Coverage 5. Binds at IMPORT time (the
    module-level `Path(os.environ.get(...))` expression below), so a
    planted-violation run must set it in a CHILD PROCESS environment
    before this module is imported, never via a post-import monkeypatch
    (monkeypatch.setenv has no effect on an already-bound module-level
    value).
  - Coverage 5's FIRST half, Coverage 6 and Coverage 7 deliberately never
    read this seam: Coverage 5's first half recomputes the default target
    directly from the repository root without ever reading os.environ (the
    check_permitted_claims.py `_HERE`-resolves-to-the-wrong-directory
    landmine, closed here by construction); 6 and 7 read only this
    module's own source. A stray seam value left set after a planted run
    cannot make Coverage 5's first half, 6 or 7 pass vacuously -- at worst
    Coverage 1-4 and Coverage 5's second half redirect to whatever the
    seam happens to point at, which fails loudly rather than silently.

CI framing, stated honestly: `pytest tests/ -v` appears in
`.github/workflows/build.yml:161` and `.github/workflows/beta-build.yml:134`,
so this module -- like every other file under tests/ -- WILL run in CI once
this branch reaches `main` or `beta`. It does not run in any CI leg on the
milestone branch itself; that is a statement about this branch's current CI
wiring, not a claim that this module is permanently invisible to CI.

This module is a standalone pytest module: it is not named check_*.py (see
tests/test_checker_convention.py's FLOOR=6 / FIXTURE_FLOOR=15, both at
exactly the current counts -- authoring a scripts/check_*.py checker here
would obligate raising both in the same commit, which this plan does not
do), it adds no shared pytest configuration or fixture-registration file
anywhere (firestarter/tests/ has none, by house convention, and this module
does not introduce one), and it imports nothing beyond the Python standard
library (os, re, pathlib in this plan's first task; subprocess, sys and
shutil are added by this same file's second task for the D-18 planted-
violation legs). It never imports, parametrizes against, or edits any other
existing test module -- the scanning logic below is its own independent
re-derivation of this plan's own gate specification, never a shared helper.

Self-contained path resolution below -- NOT in conftest.py (firestarter/
tests/ has no conftest.py anywhere in the repo; a recorded house-rule
pattern, not an omission). Stdlib and pytest only.
"""

import os
import re
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
_SUITES_REL = "test/native/avr"

# Environment seam -- binds at IMPORT time. See the module docstring's
# "Environment seams" section above. Overrides the scan ROOT only.
_SCAN_SUITES = Path(
    os.environ.get("FIRESTARTER_CASE_MAP_SCAN_ROOT", str(_REPO_ROOT / _SUITES_REL))
)

# Mapped suites -- exactly three, each named as <dirname>/<dirname>.cpp
# beneath the scan root. test_trace_eprom_v131 is DELIBERATELY EXCLUDED:
# its case set is build-flag dependent (its sixth RUN_TEST sits inside
# `#ifdef EPROM_V131_TRACE_DUMP`, which no env defines -- C-05), and it
# proves TEST-06, not TEST-01...05 (see test_trace_suite_is_deliberately_
# out_of_scope below).
_MAPPED_SUITES = (
    "test_loop_eprom_v131",
    "test_vpp_eprom_v131",
    "test_eprom_params_v131",
)
_EXCLUDED_TRACE_SUITE = "test_trace_eprom_v131"

# Hardcoded per-suite floors, as literal ints -- never derived. 88 is the
# THREE-SUITE MAPPING denominator this gate uses (47 + 32 + 9) and must
# never be confused with native_loop_v131's own per-PlatformIO-env figure
# of 79 (47 + 32 only -- that env pairs test_loop_eprom_v131 with
# test_vpp_eprom_v131 alone, never test_eprom_params_v131). The two numbers
# measure different things; conflating them is the Pitfall-2 labelling
# mistake 144-PATTERNS.md warns against.
_SUITE_FLOORS = {
    "test_loop_eprom_v131": 47,
    "test_vpp_eprom_v131": 32,
    "test_eprom_params_v131": 9,
}
_TOTAL_FLOOR = 88  # sum(_SUITE_FLOORS.values()) -- this gate's own denominator, not 79.


def _strip_comments(text):
    """Strip `//` line comments and `/* ... */` block comments, replacing
    each stripped span with whitespace of the SAME SHAPE (a newline stays a
    newline, everything else becomes a single space) so every line number
    in the result matches the original file exactly -- copied verbatim from
    tests/test_ack_layout_source_contract_v143.py's own copy (itself
    carried from tests/test_write_path_source_contract_v131.py:203-235 via
    tests/test_hv_routing_source_contract_v142.py). The three mapped
    suites carry no string or character literal outside of a comment or an
    #include/#ifdef directive (confirmed by inspection at authoring time),
    so literal-stripping is not needed here either."""
    out = []
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c == "/" and i + 1 < n and text[i + 1] == "/":
            while i < n and text[i] != "\n":
                out.append(" ")
                i += 1
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "*":
            out.append("  ")
            i += 2
            while i < n and not (text[i] == "*" and i + 1 < n and text[i + 1] == "/"):
                out.append("\n" if text[i] == "\n" else " ")
                i += 1
            if i < n:
                out.append("  ")
                i += 2
            continue
        out.append(c)
        i += 1
    return "".join(out)


def _line_of(text, idx):
    return text.count("\n", 0, idx) + 1


# ---------------------------------------------------------------------------
# Concatenation-built needles. Coverage 7 asserts none of these appear
# verbatim anywhere in this module's own source -- see the module
# docstring: a gate that quotes its forbidden tokens verbatim matches
# itself and can never pass.
# ---------------------------------------------------------------------------
_NEEDLE_SKIP_CALL = "pytest" + ".skip"
_NEEDLE_SKIPIF_MARKER = "mark" + ".skipif"
_NEEDLE_DEPENDENCY_SKIP_CALL = "importor" + "skip"

_ALL_SELF_CHECK_NEEDLES = (
    ("a pytest skip call", _NEEDLE_SKIP_CALL),
    ("a pytest skipif marker", _NEEDLE_SKIPIF_MARKER),
    ("a pytest dependency-skip call", _NEEDLE_DEPENDENCY_SKIP_CALL),
)

# ---------------------------------------------------------------------------
# RUN_TEST extraction -- the tolerant form (F-03): a future macro
# line-wrap or extra whitespace inside the parens cannot silently drop a
# case from the extracted set.
# ---------------------------------------------------------------------------
_RUN_TEST_RE = re.compile(r"RUN_TEST\(\s*([A-Za-z0-9_]+)\s*\)")


def _suite_path(suite):
    """Resolve `<suite>/<suite>.cpp` beneath the CURRENT (seam-aware) scan
    root."""
    return _SCAN_SUITES / suite / f"{suite}.cpp"


def _extract_run_test_names(path):
    """Read `path`, strip C-style comments, and return the ordered list of
    RUN_TEST(...) case names -- an independent re-derivation, never
    imported from any golden or other gate module.

    A MISSING scan target yields an empty list rather than raising: the
    higher-level floor and membership checks
    (test_scan_targets_are_non_vacuous, test_every_mapped_requirement_
    names_only_existing_cases) are what turn that emptiness into a
    locating, fail-closed AssertionError naming the observed count against
    the hardcoded floor -- an uncaught FileNotFoundError here would hide
    that locating message behind a bare traceback instead."""
    if not path.is_file():
        return []
    stripped = _strip_comments(path.read_text())
    return _RUN_TEST_RE.findall(stripped)


def _extract_all_mapped_names():
    """Return {suite: [case names]} for the three mapped suites, extracted
    fresh from whatever _SCAN_SUITES currently resolves to. Never cached at
    import time -- every leg below re-derives this on each call so a
    planted scan root is picked up correctly by a child-process run."""
    return {suite: _extract_run_test_names(_suite_path(suite)) for suite in _MAPPED_SUITES}


# ---------------------------------------------------------------------------
# The frozen requirement -> case map. Deliberately NOT auto-derived from
# the suites below: the whole point of this gate is to catch an UNREVIEWED
# RENAME OR DELETION, and a map derived FROM the suites could never detect
# that -- it would simply re-describe whatever the suites currently
# contain, which is the same failure shape D-01 exists to close (mirrors
# the wording precedent at
# firestarter_app/tests/test_revision_constants_parity.py:172-175's own
# "deliberately NOT auto-derived" comment for its firmware->host map).
# Adding, renaming or removing an entry here must be a deliberate edit to
# this dict literal.
# ---------------------------------------------------------------------------
_REQUIREMENT_CASES = {
    "TEST-01": (
        "test_each_protocol_resolves_to_its_own_distinct_row",
        "test_unknown_protocol_returns_null",
        "test_row_values_match_the_frozen_table",
    ),
    "TEST-02": (
        "test_loop01_pulse_width_never_grows_between_attempts",
        "test_loop01_each_byte_gets_exactly_the_seeded_number_of_fixed_width_pulses",
        "test_loop01_verify_read_follows_every_pulse",
        "test_loop01_a_byte_that_converges_on_its_last_permitted_pulse_succeeds",
    ),
    "TEST-03": (
        "test_loop03_overprogram_duration_is_three_times_the_pulse_count_times_the_width",
        "test_loop03_overprogram_is_zero_when_the_factor_is_zero",
        "test_loop03_overprogram_clamps_at_the_cap_rather_than_refusing",
        "test_loop03_overprogram_is_32_bit_safe_at_the_uint16_ceiling",
        "test_loop03_a_zero_cap_yields_no_overprogram_pulse",
        # D-03 non-claim, carried here so it travels with the map: the
        # arithmetic above is proven; the in-loop wiring on a LIVE row is
        # NOT, because no shipped row sets overprogram_factor
        # (eprom_params.cpp:50-52 -- all three rows carry 0). The next case
        # is what witnesses that gap rather than papering over it.
        "test_loop04_no_live_row_emits_an_overprogram_pulse",
    ),
    "TEST-04": (
        # The "reports the address" clause of TEST-04 is satisfied by the
        # u24 address + u8 pulse count payload asserted INSIDE this case --
        # not by a separate case of its own.
        "test_loop05_a_byte_that_misses_within_max_pulses_aborts_the_block",
        "test_loop05_the_loops_own_strobes_disable_the_high_voltage_route",
        "test_loop05_a_successful_block_does_not_disable_the_route",
        "test_vpp02_x3_the_energy_cap_exit_disables_the_route",
        "test_vpp02_x4_the_final_pass_verify_failure_disables_the_route",
        "test_vpp02_e1_write_init_error_exit_leaves_no_route_asserted",
    ),
    "TEST-05": (
        "test_loop06_an_ff_target_byte_is_never_read_and_never_pulsed",
        "test_loop06_an_already_matching_byte_is_read_once_and_never_pulsed",
        "test_loop06_a_block_of_only_skipped_bytes_emits_no_pulse_at_all",
        "test_loop06_the_ff_rule_does_not_suppress_the_final_verify_pass",
        # C-04: CONTEXT.md's own prose nominates "the two fallback cases"
        # for this requirement -- a phantom pair naming no existing case at
        # all. The real shape is TWO FAMILIES OF THREE: the three
        # test_0x0{7,8,B}_zero_pulse_delay_* cases below, plus their three
        # nonzero_pulse_delay negative controls, which are the non-vacuity
        # half (a fallback that fired unconditionally would pass the three
        # zero_ cases and fail these three). This corrected six-case shape
        # is what _REQUIREMENT_CASES freezes -- the phantom pair is not
        # propagated into this map.
        "test_0x07_zero_pulse_delay_takes_the_1000us_fallback",
        "test_0x08_zero_pulse_delay_takes_the_100us_fallback",
        "test_0x0B_zero_pulse_delay_takes_the_500us_fallback",
        "test_0x07_nonzero_pulse_delay_is_left_alone",
        "test_0x08_nonzero_pulse_delay_is_left_alone",
        "test_0x0B_nonzero_pulse_delay_is_left_alone",
    ),
}


# ---------------------------------------------------------------------------
# Tests -- requirement -> case membership (Coverage 1-4).
# ---------------------------------------------------------------------------


def test_every_mapped_requirement_names_only_existing_cases():
    """Coverage 1 -- D-01's core assertion. Union the extracted RUN_TEST
    names across the three mapped suites, then for each requirement id
    assert every mapped case name is present in that union. A missing case
    fails naming the requirement id, the missing case name, and the
    mapped-suite files scanned -- never a bare "lists differ"."""
    per_suite = _extract_all_mapped_names()
    all_names = set()
    for names in per_suite.values():
        all_names.update(names)
    scanned_files = [str(_suite_path(suite)) for suite in _MAPPED_SUITES]

    for requirement_id, case_names in _REQUIREMENT_CASES.items():
        for case_name in case_names:
            assert case_name in all_names, (
                f"{requirement_id} names case {case_name!r}, which does "
                "not exist in any of the three mapped suites' RUN_TEST "
                "sites -- it may have been renamed or deleted.\n"
                f"Scanned: {scanned_files}"
            )


def test_each_mapped_suite_meets_its_hardcoded_case_floor():
    """Coverage 2 -- per-suite extracted count >= its hardcoded floor
    (47 / 32 / 9). A future deletion that still leaves every MAPPED case
    present (because the deleted case belonged to none of TEST-01...05)
    would slip past Coverage 1 alone; this floor catches it."""
    per_suite = _extract_all_mapped_names()
    for suite, floor in _SUITE_FLOORS.items():
        observed = len(per_suite[suite])
        assert observed >= floor, (
            f"suite {suite!r} extracted {observed} RUN_TEST case(s) from "
            f"{_suite_path(suite)}, expected >= {floor} (hardcoded floor) "
            "-- a case may have been silently removed."
        )


def test_extracted_case_names_are_unique():
    """Coverage 3 -- len(set(names)) == len(names) across the union; a
    duplicate would silently inflate a suite's extracted count and could
    mask an unrelated rename hiding behind the duplicate's presence."""
    per_suite = _extract_all_mapped_names()
    all_names = []
    for names in per_suite.values():
        all_names.extend(names)

    if len(set(all_names)) == len(all_names):
        return

    seen = set()
    dup_locations = []
    for suite in _MAPPED_SUITES:
        path = _suite_path(suite)
        if not path.is_file():
            continue
        stripped = _strip_comments(path.read_text())
        for match in _RUN_TEST_RE.finditer(stripped):
            case_name = match.group(1)
            if case_name in seen:
                dup_locations.append(f"{suite}:{_line_of(stripped, match.start())}:{case_name}")
            seen.add(case_name)

    raise AssertionError(
        f"duplicate RUN_TEST case name(s) found across the three mapped "
        f"suites -- {len(all_names)} extracted, {len(set(all_names))} "
        f"unique. Second occurrence(s): {dup_locations}. A duplicate would "
        "inflate the extracted count and could mask a rename."
    )


def test_trace_suite_is_deliberately_out_of_scope():
    """Coverage 4 -- test_trace_eprom_v131 is asserted absent from
    _MAPPED_SUITES, and (only when its source is reachable under the
    CURRENT scan target -- a planted scratch root need not carry it) its
    source is asserted to still contain the `#ifdef EPROM_V131_TRACE_DUMP`
    guard this exclusion's reasoning depends on, so the exclusion reason
    stays machine-checked rather than becoming folklore (C-05)."""
    assert _EXCLUDED_TRACE_SUITE not in _MAPPED_SUITES, (
        f"{_EXCLUDED_TRACE_SUITE!r} must never be added to _MAPPED_SUITES "
        "-- its case set is build-flag dependent (its sixth RUN_TEST sits "
        "inside `#ifdef EPROM_V131_TRACE_DUMP`, which no env defines); it "
        "proves TEST-06, not TEST-01...05 (C-05)."
    )

    trace_path = _SCAN_SUITES / _EXCLUDED_TRACE_SUITE / f"{_EXCLUDED_TRACE_SUITE}.cpp"
    if not trace_path.is_file():
        # Skipped-free by construction -- no runtime skip call or marker
        # decorator of any kind is used here. A planted scratch root built
        # by a later planted-violation leg legitimately carries only the
        # three MAPPED suites, so this half of the check simply has
        # nothing to assert against there.
        return

    guard_needle = "#ifdef" + " EPROM_V131_TRACE_DUMP"
    text = trace_path.read_text()
    assert guard_needle in text, (
        f"{trace_path} no longer contains the {guard_needle!r} guard this "
        "exclusion's reasoning depends on -- if test_trace_eprom_v131's "
        "sixth RUN_TEST is no longer build-flag-guarded, the exclusion "
        "reason above must be re-examined, not silently kept."
    )


# ---------------------------------------------------------------------------
# Tests -- self-protection (Coverage 5-7).
# ---------------------------------------------------------------------------


def test_scan_targets_are_non_vacuous():
    """Coverage 5 -- structural self-check, two halves.

    Part (a): the DEFAULT scan root is recomputed fresh from _REPO_ROOT
    WITHOUT reading os.environ (the check_permitted_claims.py
    `_HERE`-resolves-to-the-wrong-directory landmine, closed here by
    construction): exists, and each mapped suite file beneath it exists and
    is non-empty.

    Part (b): the extractor, run against whatever _SCAN_SUITES currently
    resolves to (the SAME seam-aware target every leg above scans), must
    yield a union of at least _TOTAL_FLOOR (88) names. This is the half an
    emptied or misdirected scratch root turns RED, proving that scenario
    fails the gate's non-vacuity leg instead of making every membership
    check in Coverage 1 pass vacuously over an empty set."""
    # Part (a) -- default target, no os.environ read.
    default_root = _REPO_ROOT / _SUITES_REL
    assert default_root.is_dir(), (
        f"default scan root {default_root} does not exist on disk -- a "
        "missing scan root must FAIL, never silently pass."
    )
    assert default_root.resolve().is_relative_to(_REPO_ROOT), (
        f"default scan root {default_root} resolves outside _REPO_ROOT "
        f"({_REPO_ROOT}) -- a naive future copy of this module into "
        "another directory must fail loudly here, not scan nothing and "
        "exit 0."
    )
    for suite in _MAPPED_SUITES:
        default_suite_file = default_root / suite / f"{suite}.cpp"
        assert default_suite_file.is_file(), (
            f"default mapped suite file {default_suite_file} does not "
            "exist on disk."
        )
        assert default_suite_file.stat().st_size > 0, (
            f"default mapped suite file {default_suite_file} is empty."
        )

    # Part (b) -- seam-aware target, must extract >= _TOTAL_FLOOR names.
    per_suite = _extract_all_mapped_names()
    all_names = set()
    for names in per_suite.values():
        all_names.update(names)
    assert len(all_names) >= _TOTAL_FLOOR, (
        f"union of extracted RUN_TEST names from the CURRENT scan root "
        f"{_SCAN_SUITES} is {len(all_names)}, expected >= {_TOTAL_FLOOR} "
        "-- an emptied or misdirected scan root must fail HERE, not make "
        "every requirement-to-case membership check above pass vacuously "
        "over an empty set."
    )


def test_this_module_cannot_be_silently_skipped():
    """Coverage 6 -- this module's own source contains no runtime
    skip-bypass call, no skip-marker decorator, and no dependency-skip call
    anywhere, so the fail-closed contract this module documents is
    self-enforcing rather than merely stated. All three needles are built
    via concatenation so this test's own source and its own failure
    messages cannot match its own check."""
    own_text = Path(__file__).read_text()
    assert _NEEDLE_SKIP_CALL not in own_text, (
        "expected no " + _NEEDLE_SKIP_CALL + " call anywhere in this "
        "module -- a missing or empty scan target must FAIL, never SKIP."
    )
    assert _NEEDLE_SKIPIF_MARKER not in own_text, (
        "expected no @pytest." + _NEEDLE_SKIPIF_MARKER + " decorator "
        "anywhere in this module -- a missing or empty scan target must "
        "FAIL, never SKIP."
    )
    assert ("pytest." + _NEEDLE_DEPENDENCY_SKIP_CALL) not in own_text, (
        "expected no pytest." + _NEEDLE_DEPENDENCY_SKIP_CALL + " call "
        "anywhere in this module -- a missing dependency must FAIL, never "
        "SKIP."
    )


def test_own_needles_do_not_appear_verbatim_in_this_module():
    """Coverage 7 -- the concatenated-needle self-check: each of the three
    needles built by concatenation above (Coverage 6) must appear NOWHERE
    verbatim in this module's own source, including inside this very
    test's failure messages. Without this leg, a future edit could
    silently un-concatenate one of the needles (for example while
    "simplifying" the code) and this discipline would quietly stop being
    machine-checked."""
    own_text = Path(__file__).read_text()
    for label, needle in _ALL_SELF_CHECK_NEEDLES:
        assert needle not in own_text, (
            f"the concatenation-built needle for {label} appears verbatim "
            "in this module's own source -- rebuild it from at least two "
            "literal pieces so this gate cannot match itself."
        )
