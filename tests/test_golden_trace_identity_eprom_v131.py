"""
Project Name: Firestarter
Copyright (c) 2024 Henrik Olsson

Permission is hereby granted under MIT license.

Phase 138 Plan 05 -- PREP-03 / D-04's per-array golden-trace identity pin for
the v1.31 pre-change 27C write-loop trace fixture
(EPROM_V131_TRACE_PROTO_07/_08/_0B in test/native/avr/_shared/
eprom_v131_expected.h). This is a PARALLEL module to
test_golden_trace_identity.py (the pre-existing Phase 124 SDP pin), never a
refactor of it and never an import from it -- see Coverage item 6 below for
why a shared-helper refactor would disarm that module's own self-scan.

Requirements: PREP-03

Defect class this closes: a frozen array in eprom_v131_expected.h could be
deleted TOGETHER with the v131_assert_stream_equals() call in
test_trace_eprom_v131.cpp that consumes it, leaving `pio test -e
native_trace_v131`'s case count and PASSED status completely unchanged --
a count or status assertion cannot see that class of change. This module
adds the same two independent checks the SDP pin already proved out: whole-
file blob identity, and a per-array name + entry-count inventory, each
independently re-parsed from the fixture file rather than trusted from any
prior record (including this module's own committed JSON) -- the point of
an inventory pin is that the file and the recorded expectation are read by
two separate mechanisms and compared, so a change to either alone is
visible.

Coverage:
  1. test_blob_sha_matches_the_recorded_inventory -- `git rev-parse
     HEAD:test/native/avr/_shared/eprom_v131_expected.h` equals `meta.
     blob_sha` in the committed inventory JSON.
  2. test_array_names_match_the_recorded_inventory -- the ordered list of
     array names parsed from the live file equals the ordered list of names
     in the JSON.
  3. test_array_entry_counts_match_the_recorded_inventory -- per-array entry
     counts match, positionally; the assertion message names the FIRST
     diverging array and both counts (never a bare "lists differ").
  4. test_inventory_is_non_vacuous -- the JSON records at least 3 arrays and
     every recorded `entries` is >= 1; an empty or truncated inventory must
     FAIL, not silently pass.
  5. test_consuming_suites_still_include_the_fixture -- the single consuming
     suite, test/native/avr/test_trace_eprom_v131/test_trace_eprom_v131.cpp,
     still contains the literal `_shared/eprom_v131_expected.h` include.
     This is the link that makes the fixture load-bearing: if the consumer
     stopped including it, the blob could stay byte-identical while nothing
     exercised it.
  6. test_git_is_required_not_optional -- this module's own source contains
     no runtime skip-bypass call and no skip-marker decorator anywhere: the
     fail-closed contract (a missing `git` binary must FAIL the suite, never
     silently skip it) is self-enforcing.

This module never imports check_*.py machinery: it is a standalone pytest
module asserting directly against the committed inventory JSON and the live
firmware tree via `git` subprocess calls (list-form argv, invoked directly
rather than through a shell) and plain file reads. `_parse_arrays()`
deliberately duplicates the derivation used to author the JSON, rather than
importing a shared helper -- the inventory and the file are meant to be
compared by two INDEPENDENT readings, not by one parser trusting its own
prior output. It also does not parameterise, import from, or edit the
pre-existing SDP identity-pin module in any way.

Self-contained path resolution below -- NOT in conftest.py (firestarter/
tests/ has no conftest.py anywhere in the repo; a recorded house-rule
pattern decision, not an omission). Stdlib and pytest only.
"""

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
_FIXTURE_PATH = "test/native/avr/_shared/eprom_v131_expected.h"
_INVENTORY_JSON = _HERE / "golden" / "eprom_v131_trace_inventory.json"
_CONSUMERS = (
    _REPO_ROOT / "test" / "native" / "avr" / "test_trace_eprom_v131" / "test_trace_eprom_v131.cpp",
)

_ARRAY_DECL_RE = re.compile(
    r"static const v131_trace_entry_t\s+(\w+)\[\]\s*=\s*\{(.*?)\};",
    re.DOTALL,
)
_ENTRY_RE = re.compile(r"\{[^{}]*\}")


def _resolve_git():
    """Resolve the `git` binary, fail-closed.

    Deliberately never bypassed via any decorator or runtime call that would
    mark this outcome as skipped, anywhere in this module: a missing `git`
    turning this pin into a silent skip would be exactly the defect class
    the pre-existing SDP identity pin's own T-124-11 finding named. If `git`
    (or $GIT) cannot be resolved via shutil.which, this raises via a plain
    assert, which the test runner reports as a FAILURE, never a skipped
    outcome.
    """
    git_bin = shutil.which(os.environ.get("GIT", "git"))
    assert git_bin is not None, (
        "git not found on PATH (checked $GIT, falling back to 'git'). This "
        "must FAIL the suite, never be silently skipped -- a missing git "
        "would otherwise turn PREP-03's blob-identity pin into a silent "
        "no-op."
    )
    return git_bin


def _git(*args):
    """Run `git <args>` as a real subprocess (list-form argv, invoked
    directly rather than through a shell) against _REPO_ROOT, and assert a
    clean exit. Returns stdout, stripped."""
    git_bin = _resolve_git()
    result = subprocess.run(
        [git_bin, *args],
        cwd=str(_REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (
        f"git {' '.join(args)} failed (exit {result.returncode}).\n"
        f"stderr:\n{result.stderr}"
    )
    return result.stdout.strip()


def _parse_arrays(text):
    """Re-derive the ordered (name, entries) pairs from eprom_v131_expected.h's
    raw text, independently of the committed inventory JSON. Strips C-style
    comments first so a commented-out entry -- or a provenance banner's prose
    -- can never inflate a count."""
    arrays = []
    for m in _ARRAY_DECL_RE.finditer(text):
        name = m.group(1)
        body = m.group(2)
        body_nc = re.sub(r"/\*.*?\*/", "", body, flags=re.DOTALL)
        body_nc = re.sub(r"//[^\n]*", "", body_nc)
        entries = _ENTRY_RE.findall(body_nc)
        arrays.append((name, len(entries)))
    return arrays


def _load_inventory():
    return json.loads(_INVENTORY_JSON.read_text())


def _live_fixture_text():
    return (_REPO_ROOT / _FIXTURE_PATH).read_text()


def test_blob_sha_matches_the_recorded_inventory():
    inventory = _load_inventory()
    recorded_sha = inventory["meta"]["blob_sha"]
    observed_sha = _git("rev-parse", f"HEAD:{_FIXTURE_PATH}")
    assert observed_sha == recorded_sha, (
        f"{_FIXTURE_PATH} blob SHA changed -- recorded={recorded_sha} "
        f"observed={observed_sha}. If this file legitimately changed, "
        "re-derive tests/golden/eprom_v131_trace_inventory.json from the new "
        "file (never hand-edit the SHA) and state in the commit message "
        "which array changed and why."
    )


def test_array_names_match_the_recorded_inventory():
    inventory = _load_inventory()
    recorded_names = [a["name"] for a in inventory["arrays"]]
    live_names = [name for name, _entries in _parse_arrays(_live_fixture_text())]
    assert live_names == recorded_names, (
        f"array name list diverged.\nrecorded={recorded_names}\nlive={live_names}"
    )


def test_array_entry_counts_match_the_recorded_inventory():
    inventory = _load_inventory()
    recorded = [(a["name"], a["entries"]) for a in inventory["arrays"]]
    live = _parse_arrays(_live_fixture_text())

    n = min(len(recorded), len(live))
    for i in range(n):
        rec_name, rec_entries = recorded[i]
        live_name, live_entries = live[i]
        if rec_name != live_name or rec_entries != live_entries:
            raise AssertionError(
                f"first divergence at index {i} -- "
                f"recorded={{'name': {rec_name!r}, 'entries': {rec_entries}}}, "
                f"live={{'name': {live_name!r}, 'entries': {live_entries}}}"
            )
    assert len(recorded) == len(live), (
        f"array count diverged after {n} matching entries -- "
        f"recorded_count={len(recorded)} live_count={len(live)}"
    )


def test_inventory_is_non_vacuous():
    inventory = _load_inventory()
    arrays = inventory["arrays"]
    assert len(arrays) >= 3, (
        f"non-vacuous guard: expected >= 3 recorded arrays, got {len(arrays)} "
        "-- an empty or truncated inventory must FAIL, not silently pass."
    )
    for a in arrays:
        assert a["entries"] >= 1, (
            f"non-vacuous guard: array {a['name']!r} records entries="
            f"{a['entries']}, expected >= 1."
        )


def test_consuming_suites_still_include_the_fixture():
    for consumer in _CONSUMERS:
        text = consumer.read_text()
        assert "_shared/eprom_v131_expected.h" in text, (
            f"{consumer} no longer includes _shared/eprom_v131_expected.h -- "
            "if the consumer stopped including this fixture, the blob could "
            "stay byte-identical while nothing exercised it."
        )


def test_git_is_required_not_optional():
    """Self-checking: this module's own source contains no runtime
    skip-bypass call and no skip-marker decorator, i.e. the fail-closed
    contract for a missing `git` (see _resolve_git) is self-enforcing
    rather than merely documented."""
    this_source = Path(__file__).read_text()
    for line in this_source.splitlines():
        stripped = line.strip()
        # Real usage of either construct is always a statement/decorator
        # start-of-line -- never embedded mid-string -- so startswith()
        # correctly identifies actual code while never self-matching this
        # very check's own prose (docstring text, f-string messages, and
        # this assertion's own condition text never START a line with
        # either literal). Mirrors the pre-existing SDP pin's own fix for
        # the same self-matching-string-assertion class of bug.
        assert not stripped.startswith("pytest.skip"), (
            f"found a skip-bypass call at: {line!r} -- git absence must "
            "FAIL this suite, never take this bypass."
        )
        assert not stripped.startswith("@pytest.mark.skipif"), (
            f"found a skip-marker decorator at: {line!r} -- git "
            "absence must FAIL this suite, never skip it."
        )
