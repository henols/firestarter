#!/usr/bin/env python3
r"""
Unit tests for the v1.33 citation-manifest toolchain (Phase 154 plan 04).

Two modules under test, both siblings of this file:

  * `citation_paths.py`      -- the shared five-step path-resolution rule
                               (SWEEP-09, D-09, research F5). Imported by BOTH
                               `build_citation_manifest.py` (this plan) and
                               `remap_citations.py` (plan 05), so the same
                               citation cannot resolve two different ways.
  * `build_citation_manifest.py` -- the pre-sweep manifest generator
                               (SWEEP-09, D-07, Ruling F).

Enumerated legs, each with the exit code or outcome it pins and the
requirement it discharges (the enumerated-docstring shape is copied from
`.planning/milestones/v1.16-artifacts/ledger/tools/test_check_ledger.py`, the house analog):

  RESOLVE LEGS (task 1 -- citation_paths.py, D-09 / research F5)
   1. test_resolve_exact_repo_relative_path            -> "exact"
   2. test_resolve_unique_path_suffix                  -> "suffix"
   3. test_resolve_suffix_tie_is_broken_by_fixture_exclusion -> "suffix"
   4. test_resolve_bare_basename_skips_planted_fixture -> "basename", not a fixture
   5. test_resolve_firestarter_h_is_not_the_fake_fixture -> the name-collision trap
   6. test_resolve_host_stubs_is_ambiguous             -> "ambiguous", no path
   7. test_resolve_database_c_is_unresolved            -> "unresolved", no path
   8. test_resolve_parent_traversal_is_rejected        -> "rejected", recorded
   9. test_resolve_absolute_path_is_rejected           -> "rejected", recorded
  10. test_fixture_guard_raises_on_fixtures_inclusive_index -> raises (T-154-13)
  11. test_resolve_fixture_only_basename_falls_back    -> "basename" via fallback
  12. test_declared_fixture_exclusion_globs_are_present -> source assertion
  13. test_citation_paths_module_has_no_here_derived_root -> source assertion (D-09)

  GENERATOR LEGS (task 2 -- build_citation_manifest.py, SWEEP-09 / D-07)
  14. test_variant_colon_single_is_extracted
  15. test_variant_colon_range_is_extracted
  16. test_variant_colon_list_yields_two_independent_records
  17. test_variant_anchor_L_point_and_range_are_extracted
  18. test_backticked_wrapper_is_not_a_fifth_variant
  19. test_range_record_carries_both_endpoints_and_both_texts (REMAP-03)
  20. test_every_record_is_retarget_false                (D-08 pre-sweep)
  21. test_regeneration_is_byte_identical                (idempotence)
  22. test_zero_record_input_exits_two                   -> exit 2 (fail closed)
  23. test_header_record_is_first_and_self_describing
  24. test_generator_module_has_no_here_derived_root     -> source assertion (D-09)
  25. test_generator_imports_the_shared_resolver         -> source assertion
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

import pytest

# `_HERE` is CORRECT in a test -- the D-09 ban is on the TOOL deriving its scan
# root from its own location, not on a test locating its own siblings. Same
# reading as `test_check_ledger.py`, the house analog.
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import citation_paths  # noqa: E402

_CITATION_PATHS_SRC = os.path.join(_HERE, "citation_paths.py")
_GENERATOR = os.path.join(_HERE, "build_citation_manifest.py")


# ---------------------------------------------------------------------------
# Synthetic candidate set. It DELIBERATELY includes the firmware-repo planted
# fixture copies that the real candidate set does not contain (the firmware
# repo's `tests/` -- plural -- is outside the sweep globs, so its fixtures
# never enter the real candidate set). Putting them in here is what makes the
# fixture-exclusion rule testable at all: on the real tree the rule is
# defence in depth, and a test that only used the real set would prove
# nothing about it.
# ---------------------------------------------------------------------------
_SYNTHETIC_CANDIDATES = [
    "firestarter/src/proms/eeprom_28c.cpp",
    "firestarter/src/firestarter.cpp",
    "firestarter/include/firestarter.h",
    "firestarter/src/boards/uno_rurp_shield.cpp",
    "firestarter/test/native/avr/test_a/host_stubs.cpp",
    "firestarter/test/native/avr/test_b/host_stubs.cpp",
    "firestarter/tests/fixtures/planted_cmake_manifest_missing_source/src/proms/eeprom_28c.cpp",
    "firestarter/tests/fixtures/planted_cmake_manifest_extra/src/firestarter.cpp",
    "firestarter_app/tests/fixtures/fake_firestarter/include/firestarter.h",
    "firestarter_app/tests/fixtures/planted_log_in_window.cpp",
    "firestarter_app/firestarter/database.py",
]


@pytest.fixture()
def roots(tmp_path):
    """Two explicit root directories -- never derived from __file__ by the tool."""
    fw = tmp_path / "firestarter"
    app = tmp_path / "firestarter_app"
    fw.mkdir()
    app.mkdir()
    return {"firestarter": fw, "firestarter_app": app}


@pytest.fixture()
def index(roots):
    return citation_paths.CandidateIndex(roots, _SYNTHETIC_CANDIDATES)


# ---------------------------------------------------------------------------
# 1-13: the resolve legs
# ---------------------------------------------------------------------------

def test_resolve_exact_repo_relative_path(index):
    r = index.resolve("firestarter/src/proms/eeprom_28c.cpp")
    assert r.resolution == citation_paths.EXACT
    assert r.path == "firestarter/src/proms/eeprom_28c.cpp"


def test_resolve_unique_path_suffix(index):
    r = index.resolve("src/boards/uno_rurp_shield.cpp")
    assert r.resolution == citation_paths.SUFFIX
    assert r.path == "firestarter/src/boards/uno_rurp_shield.cpp"


def test_resolve_suffix_tie_is_broken_by_fixture_exclusion(index):
    # `src/proms/eeprom_28c.cpp` is a suffix of BOTH the real firmware file and
    # the planted-CMake-manifest fixture copy. The tie must break toward the
    # real file, never toward the fixture.
    r = index.resolve("src/proms/eeprom_28c.cpp")
    assert r.resolution == citation_paths.SUFFIX
    assert r.path == "firestarter/src/proms/eeprom_28c.cpp"
    assert "fixtures/" not in r.path


def test_resolve_bare_basename_skips_planted_fixture(index):
    r = index.resolve("eeprom_28c.cpp")
    assert r.resolution == citation_paths.BASENAME
    assert r.path == "firestarter/src/proms/eeprom_28c.cpp"
    assert "fixtures/" not in r.path


def test_resolve_firestarter_h_is_not_the_fake_fixture(index):
    # The `firestarter` name-collision trap in citation form: the app's own
    # fixture tree carries an include/firestarter.h.
    r = index.resolve("firestarter.h")
    assert r.resolution == citation_paths.BASENAME
    assert r.path == "firestarter/include/firestarter.h"
    assert "fake_firestarter" not in r.path


def test_resolve_host_stubs_is_ambiguous(index):
    r = index.resolve("host_stubs.cpp")
    assert r.resolution == citation_paths.AMBIGUOUS
    assert r.path is None
    assert len(r.candidates) == 2


def test_resolve_database_c_is_unresolved(index):
    # infoic's external decompiled source -- out of repo by design.
    r = index.resolve("database.c")
    assert r.resolution == citation_paths.UNRESOLVED
    assert r.path is None


def test_resolve_parent_traversal_is_rejected(index):
    r = index.resolve("../firestarter/include/rurp_shield.h")
    assert r.resolution == citation_paths.REJECTED
    assert r.path is None
    assert r.reason  # the rejection is RECORDED, not raised


def test_resolve_absolute_path_is_rejected(index):
    r = index.resolve("/workspaces/firestarter/src/firestarter.cpp")
    assert r.resolution == citation_paths.REJECTED
    assert r.path is None
    assert r.reason


def test_fixture_guard_raises_on_fixtures_inclusive_index(roots):
    # T-154-13: a resolution onto a planted-fixture copy would round-trip green
    # against the WRONG file. Feeding a deliberately fixtures-INCLUSIVE index
    # must raise, because such a result is a bug and not a value.
    bad = citation_paths.CandidateIndex(
        roots,
        [
            "firestarter/tests/fixtures/planted_cmake_manifest_missing_source/src/proms/eeprom_28c.cpp",
        ],
        _exclude_fixtures=False,
    )
    with pytest.raises(citation_paths.FixtureResolutionError):
        bad.resolve("eeprom_28c.cpp")


def test_resolve_fixture_only_basename_falls_back(index):
    # A citation whose target genuinely IS a fixture file resolves, via the
    # explicitly-labelled fixture-inclusive fallback, rather than being lost as
    # a false `unresolved`.
    r = index.resolve("planted_log_in_window.cpp")
    assert r.resolution == citation_paths.BASENAME
    assert r.path == "firestarter_app/tests/fixtures/planted_log_in_window.cpp"
    assert "fallback" in r.reason


def test_declared_fixture_exclusion_globs_are_present():
    src = open(_CITATION_PATHS_SRC, encoding="utf-8").read()
    assert "**/fixtures/**" in src
    assert "**/fixture/**" in src


def test_citation_paths_module_has_no_here_derived_root():
    src = open(_CITATION_PATHS_SRC, encoding="utf-8").read()
    assert "_HERE" not in src


# ---------------------------------------------------------------------------
# 14-26: the generator legs
# ---------------------------------------------------------------------------

# A candidate swept file needs (a) a provenance hit line so survey_provenance.py
# counts it into the candidate set, and (b) enough body lines for the fixture
# citations to point at.
_FW_SRC = "\n".join(
    ["// Phase 149 Plan 05: provenance stamp making this a candidate swept file."]
    + [f"// fw body line {n}" for n in range(2, 41)]
) + "\n"

_APP_SRC = "\n".join(
    ["# Phase 121: provenance stamp making this a candidate swept file."]
    + [f"# app body line {n}" for n in range(2, 31)]
) + "\n"

# One document carrying all four live syntax variants plus a backticked
# wrapper, an unresolved target and a parent-traversal target.
_DOC_ALL_VARIANTS = """\
Exact single: firestarter/src/proms/eeprom_28c.cpp:5 is the point form.
Suffix range: src/proms/eeprom_28c.cpp:7-9 is the range form.
List: hardware.py:11,13 is two independent point citations, not a range.
Anchor point [x](hardware.py#L15) and anchor range [y](hardware.py#L17-L19).
Backticked wrapper `eeprom_28c.cpp:21` must resolve to the inner colon form.
Unresolved: database.c:611 is infoic's external decompiled source.
Traversal: ../firestarter/include/rurp_shield.h:3 escapes the roots.
"""

_DOC_NO_CITATIONS = """\
This document deliberately carries no citation of any live variant.
It names files without line references, which is not a citation.
"""


def _make_tree(tmp_path, doc_text):
    meta = tmp_path / "meta"
    planning = meta / ".planning"
    planning.mkdir(parents=True)
    (planning / "doc.md").write_text(doc_text, encoding="utf-8")

    fw = tmp_path / "fw"
    (fw / "src" / "proms").mkdir(parents=True)
    (fw / "src" / "proms" / "eeprom_28c.cpp").write_text(_FW_SRC, encoding="utf-8")

    app = tmp_path / "app"
    (app / "firestarter").mkdir(parents=True)
    (app / "firestarter" / "hardware.py").write_text(_APP_SRC, encoding="utf-8")
    return meta, fw, app


def _run_generator(meta, fw, app, out, *extra):
    return subprocess.run(
        [
            sys.executable,
            _GENERATOR,
            str(meta),
            "--fw-root",
            str(fw),
            "--app-root",
            str(app),
            "--out",
            str(out),
            *extra,
        ],
        capture_output=True,
        text=True,
    )


def _generate(tmp_path, doc_text=_DOC_ALL_VARIANTS):
    meta, fw, app = _make_tree(tmp_path, doc_text)
    out = tmp_path / "manifest.jsonl"
    result = _run_generator(meta, fw, app, out)
    assert result.returncode == 0, (
        f"Expected exit 0 but got {result.returncode}.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    lines = out.read_text(encoding="utf-8").splitlines()
    parsed = [json.loads(line) for line in lines]
    return result, parsed[0], parsed[1:]


def _one(records, **match):
    hits = [r for r in records if all(r[k] == v for k, v in match.items())]
    assert len(hits) == 1, f"expected exactly 1 record matching {match}, got {hits}"
    return hits[0]


def test_variant_colon_single_is_extracted(tmp_path):
    _, _, records = _generate(tmp_path)
    r = _one(records, variant="colon_single", target_line=5)
    assert r["target_file_cited"] == "firestarter/src/proms/eeprom_28c.cpp"
    assert r["resolution"] == citation_paths.EXACT
    assert r["source_text"] == "// fw body line 5"
    assert r["target_line_end"] is None
    assert r["source_text_end"] is None


def test_variant_colon_range_is_extracted(tmp_path):
    _, _, records = _generate(tmp_path)
    r = _one(records, variant="colon_range")
    assert r["target_file_cited"] == "src/proms/eeprom_28c.cpp"
    assert r["resolution"] == citation_paths.SUFFIX
    assert r["target_line"] == 7
    assert r["target_line_end"] == 9


def test_variant_colon_list_yields_two_independent_records(tmp_path):
    _, _, records = _generate(tmp_path)
    listed = [r for r in records if r["variant"] == "colon_list"]
    assert len(listed) == 2, listed
    assert sorted(r["target_line"] for r in listed) == [11, 13]
    for r in listed:
        assert r["target_line_end"] is None, "a list element is a POINT, not a range"
        assert r["source_text_end"] is None
        assert r["target_file_resolved"] == "firestarter_app/firestarter/hardware.py"


def test_variant_anchor_L_point_and_range_are_extracted(tmp_path):
    _, _, records = _generate(tmp_path)
    point = _one(records, variant="anchor_L")
    assert point["target_line"] == 15
    assert point["target_line_end"] is None
    assert point["source_text"] == "# app body line 15"
    rng = _one(records, variant="anchor_L_range")
    assert rng["target_line"] == 17
    assert rng["target_line_end"] == 19
    assert rng["source_text"] == "# app body line 17"
    assert rng["source_text_end"] == "# app body line 19"


def test_backticked_wrapper_is_not_a_fifth_variant(tmp_path):
    _, _, records = _generate(tmp_path)
    r = _one(records, target_line=21)
    assert r["variant"] == "colon_single"
    assert r["target_file_cited"] == "eeprom_28c.cpp", "backticks are a WRAPPER"
    assert r["resolution"] == citation_paths.BASENAME


def test_range_record_carries_both_endpoints_and_both_texts(tmp_path):
    _, _, records = _generate(tmp_path)
    ranges = [r for r in records if r["variant"] in ("colon_range", "anchor_L_range")]
    assert ranges
    for r in ranges:
        assert r["target_line_end"] is not None
        assert r["source_text_end"] is not None


def test_unresolved_and_rejected_records_are_kept_not_dropped(tmp_path):
    _, _, records = _generate(tmp_path)
    unresolved = _one(records, target_file_cited="database.c")
    assert unresolved["resolution"] == citation_paths.UNRESOLVED
    assert unresolved["target_file_resolved"] is None
    assert unresolved["text_status"] == "unresolved_target"
    rejected = _one(
        records, target_file_cited="../firestarter/include/rurp_shield.h"
    )
    assert rejected["resolution"] == citation_paths.REJECTED
    assert rejected["resolution_reason"]


def test_every_record_is_retarget_false(tmp_path):
    _, _, records = _generate(tmp_path)
    assert records
    assert all(r["retarget"] is False for r in records)


def test_regeneration_is_byte_identical(tmp_path):
    meta, fw, app = _make_tree(tmp_path, _DOC_ALL_VARIANTS)
    out = tmp_path / "manifest.jsonl"
    first = _run_generator(meta, fw, app, out)
    assert first.returncode == 0, first.stderr
    blob_one = out.read_bytes()
    second = _run_generator(meta, fw, app, out)
    assert second.returncode == 0, second.stderr
    blob_two = out.read_bytes()
    assert blob_one == blob_two, "regeneration over an unchanged tree must be byte-identical"


def test_zero_record_input_exits_two(tmp_path):
    meta, fw, app = _make_tree(tmp_path, _DOC_NO_CITATIONS)
    out = tmp_path / "manifest.jsonl"
    result = _run_generator(meta, fw, app, out)
    assert result.returncode == 2, (
        f"Expected exit 2 on a zero-record input but got {result.returncode}.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert "zero" in (result.stdout + result.stderr).lower()


def test_header_record_is_first_and_self_describing(tmp_path):
    _, header, records = _generate(tmp_path)
    assert "_schema" in header
    schema = header["_schema"]
    for key in (
        "schema_version",
        "record_keys",
        "source_text_convention",
        "source_text_unreadable_sentinel",
        "candidate_set",
        "ordering_resolution",
        "resolution_rule",
        "variants",
        "retarget",
        "generating_command",
        "pre_sweep_shas",
        "counts",
    ):
        assert key in schema, f"header record is missing {key!r}"
    assert schema["counts"]["records"] == len(records)
    assert list(records[0].keys()) == schema["record_keys"]


def test_generator_module_has_no_here_derived_root():
    src = open(_GENERATOR, encoding="utf-8").read()
    assert "_HERE" not in src


def test_generator_imports_the_shared_resolver():
    src = open(_GENERATOR, encoding="utf-8").read()
    assert "import citation_paths" in src
    # The fixture-exclusion rule must live in ONE place only.
    assert "fixtures/**" not in src
