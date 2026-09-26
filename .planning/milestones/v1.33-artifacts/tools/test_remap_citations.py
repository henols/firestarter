#!/usr/bin/env python3
"""
pytest coverage for remap_citations.py -- SWEEP-11's whole proof burden.

The tool is BUILT in Phase 154 and APPLIED in Phase 159 (D-01/D-10), so nothing
else in the repository ever exercises it. Every property the requirement names
is therefore proven here against committed synthetic fixtures, and two of the
tests exist purely to prove that the proofs are DISCRIMINATING rather than
accidentally green.

Tests (expected exit code / requirement discharged):
   1. build_map on the committed fixture pair is EXACTLY the 20->15 map with two
      separated non-surviving runs -- n/a (unit) / SWEEP-11.
   2. A range spanning both deleted blocks SHRINKS: old 3-18 (span 16) becomes
      new 3-13 (span 11) -- n/a (unit) / SWEEP-11, REMAP-03.
   3. A constant-offset implementation FAILS test 2, so test 2 is not vacuous
      (it would produce -2-13) -- n/a (unit) / anti-vacuity for SWEEP-11.
   4. The fixture's map contains a CHAIN (map[a]=b and map[b]=c, c != b) and at
      least two separated non-surviving runs. Runs BEFORE the idempotency
      assertion, because a one-deletion-block fixture cannot produce a chain and
      would pass even against a blind implementation -- n/a (unit) / SWEEP-11.
   5. A BLIND remapper drifts along that chain (15 -> 10 -> 8 -> 6), so test 6 is
      not vacuous -- n/a (unit) / anti-vacuity for SWEEP-11.
   6. Idempotent on the chained map: run 1 rewrites, runs 2 and 3 are EXACT
      byte-for-byte no-ops -- exit 0 / SWEEP-11.
   7. A range whose BOTH endpoints chain keeps a STABLE span across runs 1, 2
      and 3 -- exit 0 / SWEEP-11, REMAP-03.
   8. A colon_list element does not drift (`10,15` stays `10,15`). This is the
      regression the chained fixture caught while this plan was executed --
      exit 0 / SWEEP-11.
   9. `manifest_empty.jsonl` (header only, zero records) exits 2 -- exit 2 /
      SWEEP-11, D-09.
  10. The module has no location-derived root: neither `_HERE` nor `__file__`
      appears in it, `autojunk=False` does, and the docstring carries the house
      `Exit codes:` block -- n/a (source) / SWEEP-11, D-09.
  11. The difflib map agrees EXACTLY with an independently-parsed `git diff -U0`
      unified-hunk map on a real ~500-line repository file -- n/a (unit) /
      SWEEP-11, T-154-18.
  12. `autojunk=True` really would corrupt the map on a real ~900-line source
      file, so `autojunk=False` is load-bearing rather than decorative --
      n/a (unit) / T-154-18.  Skips if the firmware sub-repo is not populated.
  13. `replace` is treated as non-surviving: a reflowed line maps to None and its
      citation is flagged retarget, not assigned a positional number --
      exit 0 / SWEEP-11.
  14. Dry run (no `--apply`) writes nothing at all -- exit 0 / SWEEP-11, D-01.
  15. An oracle violation exits 1 and writes NOTHING, not even the records that
      would have succeeded -- exit 1 / REMAP-02, T-154-17.
  16. A record whose `target_file_resolved` does not exist exits 1 -- exit 1 /
      D-09.
  17. An unloadable manifest exits 2, kept distinct from a real BLOCK -- exit 2 /
      D-09.
  18. A `..`-carrying `planning_file` is refused and nothing is written --
      exit 1 / ASVS V5.
  19. The tool was NOT applied to any real citation-bearing `.planning/`
      document in this phase -- n/a (repo) / SWEEP-11, D-01, D-10, T-154-21.

`_HERE` IS correct in this file: the ban is on the TOOL deriving its scan root,
not on a test locating its own sibling fixtures.
"""

import json
import os
import re
import shutil
import subprocess
import sys

import pytest

# ---------------------------------------------------------------------------
# Paths. `_HERE` is legitimate here -- see the module docstring.
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
_TOOL = os.path.join(_HERE, "remap_citations.py")
_FIXTURES = os.path.join(_HERE, "fixtures")
_CHAINED_OLD = os.path.join(_FIXTURES, "citations_chained_old.txt")
_CHAINED_NEW = os.path.join(_FIXTURES, "citations_chained_new.txt")
_MANIFEST_MIN = os.path.join(_FIXTURES, "manifest_min.jsonl")
_MANIFEST_EMPTY = os.path.join(_FIXTURES, "manifest_empty.jsonl")
_DOC_MIN = os.path.join(_FIXTURES, "doc_min.md")
_CITATION_PATHS = os.path.join(_HERE, "citation_paths.py")

if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import remap_citations as rc  # noqa: E402 -- sys.path is prepared above

#: The target the fixture manifest cites, and the two content sides.
_TARGET_REL = "firestarter/src/chained_demo.cpp"
_DOC_REL = ".planning/doc_min.md"

#: The map the committed fixture pair MUST produce. Stated here so a fixture
#: edit that silently changes the map fails loudly instead of weakening every
#: test below.
_EXPECTED_MAP = {
    1: 1, 2: 2, 3: 3, 4: None, 5: None, 6: 4, 7: 5, 8: 6, 9: 7, 10: 8,
    11: None, 12: None, 13: None, 14: 9, 15: 10, 16: 11, 17: 12, 18: 13,
    19: 14, 20: 15,
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _read_lines(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read().splitlines()


def _git(repo, *args):
    return subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "-c",
            "user.email=remap-test@example.invalid",
            "-c",
            "user.name=remap test",
            *args,
        ],
        capture_output=True,
        text=True,
        check=False,
    )


def _shown(result, expected):
    return (
        f"Expected exit {expected} but got {result.returncode}.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )


class Harness:
    """A throwaway git repository holding the fixture's pre- and post-sweep sides.

    The pre-sweep side is COMMITTED and then overwritten on disk, because the
    tool must read the old content from git -- by the time Phase 159 runs, the
    pre-sweep content exists nowhere on disk. No escape hatch is provided for
    the test, so the tested code path is the production code path.
    """

    def __init__(self, tmp_path, old_lines=None, new_lines=None, doc_text=None):
        self.root = tmp_path / "repo"
        (self.root / "firestarter" / "src").mkdir(parents=True)
        (self.root / ".planning").mkdir(parents=True)
        self.target = self.root / _TARGET_REL
        self.doc = self.root / _DOC_REL
        self.manifest = tmp_path / "manifest.jsonl"

        old = old_lines if old_lines is not None else _read_lines(_CHAINED_OLD)
        new = new_lines if new_lines is not None else _read_lines(_CHAINED_NEW)
        self.old_lines, self.new_lines = old, new

        self.target.write_text("\n".join(old) + "\n", encoding="utf-8")
        if doc_text is None:
            shutil.copyfile(_DOC_MIN, self.doc)
        else:
            self.doc.write_text(doc_text, encoding="utf-8")
        shutil.copyfile(_MANIFEST_MIN, self.manifest)

        assert _git(self.root, "init", "-q").returncode == 0
        assert _git(self.root, "add", "-A").returncode == 0
        assert _git(self.root, "commit", "-qm", "pre-sweep").returncode == 0
        self.sha = _git(self.root, "rev-parse", "HEAD").stdout.strip()
        assert len(self.sha) == 40, self.sha

        # The sweep: the pre-sweep content now exists only in git.
        self.target.write_text("\n".join(new) + "\n", encoding="utf-8")

    def load_manifest(self):
        header, records = None, []
        for line in self.manifest.read_text(encoding="utf-8").splitlines():
            obj = json.loads(line)
            if "_schema" in obj:
                header = obj
            else:
                records.append(obj)
        return header, records

    def write_manifest(self, header, records):
        with open(self.manifest, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(header, ensure_ascii=False) + "\n")
            for rec in records:
                handle.write(json.dumps(rec, ensure_ascii=False) + "\n")

    def run(self, *extra, manifest=None):
        return subprocess.run(
            [
                sys.executable,
                _TOOL,
                str(self.root),
                "--manifest",
                str(manifest or self.manifest),
                "--pre-sweep-sha",
                self.sha,
                *extra,
            ],
            capture_output=True,
            text=True,
            check=False,
        )

    def apply(self, *extra):
        return self.run("--apply", "--quiet-notes", *extra)

    def doc_text(self):
        return self.doc.read_text(encoding="utf-8")

    def cited(self, lineno):
        """The citation as it currently reads on `lineno` of the citing doc."""
        line = self.doc_text().splitlines()[lineno - 1]
        match = rc.CITATION_RE.search(line)
        assert match, f"no citation on line {lineno}: {line!r}"
        return match.group(0)


@pytest.fixture
def harness(tmp_path):
    return Harness(tmp_path)


def _naive_offset_range(map_, a, b):
    """A CONSTANT-OFFSET range mapping -- the wrong implementation, for contrast.

    It takes the offset measured at the range END and applies it to both
    endpoints, which is what "translate the citation" means. It must fail the
    shrink assertion.
    """
    offset = map_[b] - b
    return a + offset, b + offset


def _blind_apply(map_, number, runs):
    """A BLIND remapper: apply the map to whatever integer is found, every run."""
    seen = []
    for _ in range(runs):
        number = map_.get(number) or number
        seen.append(number)
    return seen


def _map_from_unified_diff(diff_text, n_old):
    """old 1-based line -> new 1-based line, parsed from `git diff -U0` hunks.

    An INDEPENDENT second implementation of the same mapping, used only to
    cross-check difflib on a real file. Removed lines map to None, exactly as
    the tool treats `delete`/`replace`.
    """
    hunk = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
    result, cursor, offset = {}, 1, 0
    for line in diff_text.splitlines():
        found = hunk.match(line)
        if not found:
            continue
        a = int(found.group(1))
        b = 1 if found.group(2) is None else int(found.group(2))
        d = 1 if found.group(4) is None else int(found.group(4))
        if b == 0:
            # Pure insertion AFTER old line `a`: that line keeps the old offset.
            for ln in range(cursor, a + 1):
                result[ln] = ln + offset
            cursor = a + 1
        else:
            for ln in range(cursor, a):
                result[ln] = ln + offset
            for ln in range(a, a + b):
                result[ln] = None
            cursor = a + b
        offset += d - b
    for ln in range(cursor, n_old + 1):
        result[ln] = ln + offset
    return result


def _none_runs(map_, n_old):
    """Maximal runs of non-surviving old lines, in order."""
    runs, current = [], []
    for line in range(1, n_old + 1):
        if map_.get(line) is None:
            current.append(line)
        elif current:
            runs.append(current)
            current = []
    if current:
        runs.append(current)
    return runs


def _record(planning_line, variant, cited, start, end, old_lines):
    return {
        "planning_file": _DOC_REL,
        "planning_line": planning_line,
        "variant": variant,
        "target_file_cited": cited,
        "target_file_resolved": _TARGET_REL,
        "resolution": "exact",
        "resolution_reason": "test-authored record",
        "target_line": start,
        "target_line_end": end,
        "source_text": old_lines[start - 1],
        "source_text_end": None if end is None else old_lines[end - 1],
        "text_status": "read",
        "text_status_end": None if end is None else "read",
        "retarget": False,
    }


# ---------------------------------------------------------------------------
# Test 1 -- the committed fixture pair produces exactly the expected map
# ---------------------------------------------------------------------------
def test_fixture_pair_produces_the_expected_map():
    old, new = _read_lines(_CHAINED_OLD), _read_lines(_CHAINED_NEW)
    assert len(old) == 20 and len(new) == 15, (len(old), len(new))
    assert rc.build_map(old, new) == _EXPECTED_MAP


# ---------------------------------------------------------------------------
# Test 2 -- SWEEP-11 / REMAP-03: a range spanning a deleted block SHRINKS
# ---------------------------------------------------------------------------
def test_range_spanning_deleted_block_shrinks():
    old, new = _read_lines(_CHAINED_OLD), _read_lines(_CHAINED_NEW)
    map_ = rc.build_map(old, new)
    start, end, retarget = rc.map_range(map_, 3, 18, len(old))
    assert (start, end, retarget) == (3, 13, False)
    old_span, new_span = 18 - 3 + 1, end - start + 1
    # The SPAN must change. This is the assertion a constant-offset
    # implementation fails -- see the next test.
    assert new_span != old_span, "the span did not change: this is a translate"
    assert old_span - new_span == 5, (old_span, new_span)
    deleted = sum(1 for line in range(3, 19) if map_[line] is None)
    assert old_span - new_span == deleted == 5


# ---------------------------------------------------------------------------
# Test 3 -- anti-vacuity: a constant-offset implementation FAILS test 2
# ---------------------------------------------------------------------------
def test_a_constant_offset_implementation_fails_the_shrink_leg():
    old, new = _read_lines(_CHAINED_OLD), _read_lines(_CHAINED_NEW)
    map_ = rc.build_map(old, new)
    naive = _naive_offset_range(map_, 3, 18)
    assert naive == (-2, 13), naive
    assert naive[1] - naive[0] + 1 == 18 - 3 + 1, "a translate preserves the span"
    assert naive != rc.map_range(map_, 3, 18, len(old))[:2]


# ---------------------------------------------------------------------------
# Test 4 -- the fixture's map really contains a CHAIN. MUST run before the
# idempotency assertion: a one-deletion-block fixture cannot produce a chain and
# would pass even against a blind implementation (research Pitfall 3).
# ---------------------------------------------------------------------------
def test_chained_map_has_a_chain():
    old, new = _read_lines(_CHAINED_OLD), _read_lines(_CHAINED_NEW)
    map_ = rc.build_map(old, new)
    chains = [
        (a, map_[a], map_[map_[a]])
        for a in sorted(map_)
        if map_[a] is not None
        and map_[a] in map_
        and map_[map_[a]] is not None
        and map_[map_[a]] != map_[a]
    ]
    assert chains, "the fixture map contains NO chain -- the idempotency leg would be vacuous"
    assert (15, 10, 8) in chains, chains

    runs = _none_runs(map_, len(old))
    assert len(runs) >= 2, f"only {len(runs)} non-surviving run(s): no chain possible"
    assert runs == [[4, 5], [11, 12, 13]], runs
    # The runs are SEPARATED by at least one surviving line.
    assert runs[1][0] - runs[0][-1] > 1


# ---------------------------------------------------------------------------
# Test 5 -- anti-vacuity: a BLIND remapper drifts along that chain
# ---------------------------------------------------------------------------
def test_a_blind_remapper_drifts_along_the_chain():
    old, new = _read_lines(_CHAINED_OLD), _read_lines(_CHAINED_NEW)
    map_ = rc.build_map(old, new)
    assert _blind_apply(map_, 15, 3) == [10, 8, 6]


# ---------------------------------------------------------------------------
# Test 6 -- SWEEP-11: idempotent on the chained map
# ---------------------------------------------------------------------------
def test_idempotent_on_chained_map(harness):
    before = harness.doc_text()
    assert harness.cited(3).endswith(":15")

    first = harness.apply()
    assert first.returncode == 0, _shown(first, 0)
    after_run_1 = harness.doc_text()
    assert after_run_1 != before
    assert harness.cited(3).endswith(":10"), harness.cited(3)
    assert "7 rewritten" in first.stdout, first.stdout

    second = harness.apply()
    assert second.returncode == 0, _shown(second, 0)
    assert harness.doc_text() == after_run_1, "run 2 was not an exact no-op"
    assert "0 rewritten" in second.stdout and "7 already at their fixed point" in second.stdout

    third = harness.apply()
    assert third.returncode == 0, _shown(third, 0)
    assert harness.doc_text() == after_run_1, "run 3 was not an exact no-op"
    assert harness.cited(3).endswith(":10")


# ---------------------------------------------------------------------------
# Test 7 -- SWEEP-11: a range whose BOTH endpoints chain keeps a stable span
# ---------------------------------------------------------------------------
def test_idempotent_range_span_is_stable(harness):
    old, new = harness.old_lines, harness.new_lines
    map_ = rc.build_map(old, new)
    # Both endpoints of old 10-20 chain: map[10]=8 with map[8]=6, and
    # map[20]=15 with map[15]=10. A blind implementation shrinks it again.
    assert map_[map_[10]] == 6 and map_[map_[20]] == 10

    assert harness.cited(5).endswith(":10-20")
    spans = []
    for _ in range(3):
        assert harness.apply().returncode == 0
        text = harness.cited(5)
        start, end = (int(n) for n in text.rsplit(":", 1)[1].split("-"))
        spans.append((start, end, end - start + 1))
    assert spans[0] == (8, 15, 8), spans
    assert spans[1] == spans[0] and spans[2] == spans[0], spans
    # A blind implementation would have gone 8-15 -> 6-10 on run 2.
    assert _blind_apply(map_, 8, 1)[0] == 6


# ---------------------------------------------------------------------------
# Test 8 -- regression the chained fixture caught: a colon_list element must not
# drift. After run 1 `:15,20` reads `:10,15`, and that `15` is the rewritten
# value of the record for old line 20 -- a number-keyed record lookup binds it to
# the record for old line 15 and rewrites it to 10, giving `10,10`.
# ---------------------------------------------------------------------------
def test_colon_list_element_does_not_drift(harness):
    assert harness.cited(6).endswith(":15,20")
    assert harness.apply().returncode == 0
    assert harness.cited(6).endswith(":10,15"), harness.cited(6)
    assert harness.apply().returncode == 0
    assert harness.cited(6).endswith(":10,15"), harness.cited(6)
    assert harness.apply().returncode == 0
    assert harness.cited(6).endswith(":10,15"), harness.cited(6)


# ---------------------------------------------------------------------------
# Test 9 -- SWEEP-11 / D-09: an empty input set exits 2
# ---------------------------------------------------------------------------
def test_exits_nonzero_on_empty_input(harness):
    result = harness.run(manifest=_MANIFEST_EMPTY)
    assert result.returncode == 2, _shown(result, 2)
    assert "ZERO records" in result.stderr
    assert result.returncode != 0, "silence must never be success"


def test_exits_nonzero_when_no_record_is_actionable(harness):
    header, records = harness.load_manifest()
    for rec in records:
        rec["retarget"] = True
    harness.write_manifest(header, records)
    result = harness.run()
    assert result.returncode == 2, _shown(result, 2)
    assert "NONE is" in result.stderr


# ---------------------------------------------------------------------------
# Test 10 -- SWEEP-11 / D-09: the module has no location-derived root
# ---------------------------------------------------------------------------
def test_here_is_absent_from_the_module():
    source = open(_TOOL, encoding="utf-8").read()
    assert source.count("_HERE") == 0, "the tool must not derive a root from its location"
    assert source.count("__file__") == 0, "no __file__-derived root is permitted"
    assert source.count("autojunk=False") >= 1, "autojunk=False is load-bearing"
    assert "autojunk=True" not in source.replace(
        "`autojunk=True`", ""
    ).replace("autojunk=True` ", ""), "the tool must never build a map with autojunk on"
    assert "Exit codes" in rc.__doc__
    for code in ("0 --", "1 --", "2 --"):
        assert code in rc.__doc__, code
    assert "import citation_paths" in source, "the shared resolver must be imported"
    assert source.count("fixtures/**") == 0, "no independent resolution logic"


def test_repo_root_is_a_required_positional_and_manifest_has_no_default():
    helped = subprocess.run(
        [sys.executable, _TOOL, "--help"], capture_output=True, text=True, check=False
    )
    assert helped.returncode == 0, _shown(helped, 0)
    assert "repo_root" in helped.stdout
    assert "--manifest MANIFEST" in helped.stdout
    assert "--apply" in helped.stdout

    no_manifest = subprocess.run(
        [sys.executable, _TOOL, os.sep], capture_output=True, text=True, check=False
    )
    assert no_manifest.returncode != 0
    assert "--manifest" in no_manifest.stderr


# ---------------------------------------------------------------------------
# Test 11 -- T-154-18: difflib agrees with an independent git diff -U0 map
# ---------------------------------------------------------------------------
def test_difflib_map_agrees_with_git_diff_u0(tmp_path):
    real = _read_lines(_CITATION_PATHS)
    assert len(real) > 200, "the cross-check needs a real file over difflib's junk threshold"

    # Two disjoint 6-line windows in which every line is unique in the file, so
    # the two diff algorithms cannot legitimately disagree about the alignment.
    seen = {}
    for index, text in enumerate(real):
        seen.setdefault(text, []).append(index)
    unique = {index for indexes in seen.values() if len(indexes) == 1 for index in indexes}
    windows = [
        start
        for start in range(len(real) - 6)
        if all(start + k in unique for k in range(6))
    ]
    assert len(windows) >= 2, "no unique 6-line window found"
    first = windows[0]
    later = [start for start in windows if start > first + 26]
    assert later, "no second unique window far enough from the first"
    second = later[0]
    dropped = set(range(first, first + 6)) | set(range(second, second + 6))
    edited = [text for index, text in enumerate(real) if index not in dropped]

    repo = tmp_path / "cross"
    repo.mkdir()
    target = repo / "citation_paths.py"
    target.write_text("\n".join(real) + "\n", encoding="utf-8")
    assert _git(repo, "init", "-q").returncode == 0
    assert _git(repo, "add", "-A").returncode == 0
    assert _git(repo, "commit", "-qm", "before").returncode == 0
    target.write_text("\n".join(edited) + "\n", encoding="utf-8")

    diff = _git(repo, "diff", "-U0", "HEAD", "--", "citation_paths.py")
    assert diff.returncode == 0, diff.stderr
    from_git = _map_from_unified_diff(diff.stdout, len(real))
    from_difflib = rc.build_map(real, edited)
    assert from_difflib == from_git, {
        line: (from_difflib.get(line), from_git.get(line))
        for line in sorted(set(from_difflib) | set(from_git))
        if from_difflib.get(line) != from_git.get(line)
    }
    assert sum(1 for v in from_difflib.values() if v is None) == 12


# ---------------------------------------------------------------------------
# Test 12 -- T-154-18: autojunk=True really does corrupt the map on a real file
# ---------------------------------------------------------------------------
def test_autojunk_true_would_corrupt_the_map_on_a_real_file():
    import difflib

    # A FROZEN pre-sweep copy of firestarter/src/proms/eeprom_28c.cpp, not the live
    # file. Reading the live file made this leg self-invalidating: plan 154-06 swept
    # that exact file later in this same phase, so the provenance-stripping edit below
    # became a no-op and the leg reported good=873 bad=873 -- proving nothing, and
    # failing on its own non-vacuity assertion. The frozen copy keeps the control
    # hermetic. It must stay a REAL file: research established that a purpose-built
    # 500-line synthetic equivalent does NOT diverge, which is the whole point --
    # autojunk only bites on real files, so a synthetic fixture would pass either way.
    candidate = os.path.join(_HERE, "fixtures", "autojunk_real_file_presweep.cpp")
    assert os.path.isfile(candidate), (
        "the frozen pre-sweep fixture is missing; it is committed alongside this "
        "test precisely so this leg cannot depend on live, sweepable source"
    )
    old = _read_lines(candidate)
    assert len(old) > 200
    new = [
        line
        for line in old
        if not re.search(r"(Phase \d+|D-\d\d|[A-Z]{3,}-\d\d)", line)
    ]
    assert new != old, "the realistic provenance-stripping edit changed nothing"

    def mapped(autojunk):
        matcher = difflib.SequenceMatcher(None, old, new, autojunk=autojunk)
        out = {}
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                for k in range(i2 - i1):
                    out[i1 + k + 1] = j1 + k + 1
            elif tag in ("delete", "replace"):
                for k in range(i1, i2):
                    out[k + 1] = None
        return out

    good, bad = mapped(False), mapped(True)
    assert good == rc.build_map(old, new), "the tool must use autojunk=False"
    survivors_good = sum(1 for v in good.values() if v is not None)
    survivors_bad = sum(1 for v in bad.values() if v is not None)
    assert survivors_good == len(new), (survivors_good, len(new))
    assert survivors_bad < survivors_good, (
        "autojunk=True did not diverge on this file, so this leg proves nothing; "
        f"good={survivors_good} bad={survivors_bad}"
    )


# ---------------------------------------------------------------------------
# Test 13 -- SWEEP-11: `replace` is non-surviving, exactly like `delete`
# ---------------------------------------------------------------------------
def test_replace_is_treated_as_non_surviving(tmp_path):
    # (a) the opcode itself: a changed line yields `replace` and maps to None.
    assert rc.build_map(["a", "b", "c"], ["a", "B", "c"]) == {1: 1, 2: None, 3: 3}

    # (b) end to end: a REFLOWED line's citation is flagged retarget and left
    # exactly as written -- never assigned a positional number.
    old = _read_lines(_CHAINED_OLD)
    new = _read_lines(_CHAINED_NEW)
    reflow_index = new.index("static uint8_t demo_state;")
    new = list(new)
    new[reflow_index] = "static uint8_t demo_state;  // reflowed by the sweep"
    doc = "A citation at the reflowed line: firestarter/src/chained_demo.cpp:6\n"
    harness = Harness(tmp_path, old_lines=old, new_lines=new, doc_text=doc)
    assert rc.build_map(old, new)[6] is None, "a reflowed line must not survive"

    header, _ = harness.load_manifest()
    harness.write_manifest(
        header, [_record(1, "colon_single", _TARGET_REL, 6, None, old)]
    )
    result = harness.run("--apply")
    assert result.returncode == 0, _shown(result, 0)
    assert harness.doc_text() == doc, "a retarget record must never be rewritten"
    assert "SUGGESTION for a human" in result.stdout
    assert "1 flagged retarget" in result.stdout


# ---------------------------------------------------------------------------
# Test 14 -- SWEEP-11 / D-01: dry run is the default and writes nothing
# ---------------------------------------------------------------------------
def test_dry_run_writes_nothing(harness):
    before = harness.doc_text()
    before_target = harness.target.read_text(encoding="utf-8")
    result = harness.run()
    assert result.returncode == 0, _shown(result, 0)
    assert "DRY RUN" in result.stdout and "would change" in result.stdout
    assert harness.doc_text() == before, "the dry run modified the citing document"
    assert harness.target.read_text(encoding="utf-8") == before_target
    # The sweep's own edit to the target file is the ONLY thing the working
    # tree carries; the dry run added nothing to it.
    listing = _git(harness.root, "status", "--porcelain")
    assert [row[3:] for row in listing.stdout.splitlines()] == [
        _TARGET_REL
    ], listing.stdout


# ---------------------------------------------------------------------------
# Test 15 -- REMAP-02 / T-154-17: an oracle violation exits 1 and writes nothing
# ---------------------------------------------------------------------------
def test_oracle_violation_exits_1_and_writes_nothing(harness):
    before = harness.doc_text()
    header, records = harness.load_manifest()
    for rec in records:
        if rec["target_line"] == 15 and rec["variant"] == "colon_single":
            rec["source_text"] = "this text is at no line of either side"
    harness.write_manifest(header, records)
    result = harness.run("--apply")
    assert result.returncode == 1, _shown(result, 1)
    assert "oracle violated" in result.stderr
    assert "nothing was written" in result.stderr
    assert harness.doc_text() == before, (
        "a violation must abort the WHOLE run, including records that would "
        "have succeeded"
    )


# ---------------------------------------------------------------------------
# Test 16 -- D-09: a missing resolved target is a real violation (exit 1)
# ---------------------------------------------------------------------------
def test_missing_resolved_target_exits_1(harness):
    harness.target.unlink()
    result = harness.run("--apply")
    assert result.returncode == 1, _shown(result, 1)
    assert "does not exist on disk" in result.stderr


# ---------------------------------------------------------------------------
# Test 17 -- D-09: infrastructure failures exit 2, not 1
# ---------------------------------------------------------------------------
def test_unloadable_manifest_exits_2(harness, tmp_path):
    absent = harness.run(manifest=tmp_path / "not-a-file.jsonl")
    assert absent.returncode == 2, _shown(absent, 2)
    assert "cannot load manifest" in absent.stderr

    broken = tmp_path / "broken.jsonl"
    broken.write_text('{"planning_file": nope}\n', encoding="utf-8")
    result = harness.run(manifest=broken)
    assert result.returncode == 2, _shown(result, 2)
    assert "not valid JSON" in result.stderr

    missing_root = subprocess.run(
        [
            sys.executable,
            _TOOL,
            str(tmp_path / "no-such-root"),
            "--manifest",
            str(harness.manifest),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert missing_root.returncode == 2, _shown(missing_root, 2)


# ---------------------------------------------------------------------------
# Test 18 -- ASVS V5: a traversal path is refused and nothing is written
# ---------------------------------------------------------------------------
def test_traversal_in_planning_file_is_refused(harness):
    before = harness.doc_text()
    header, records = harness.load_manifest()
    for rec in records:
        rec["planning_file"] = "../escaped.md"
    harness.write_manifest(header, records)
    result = harness.run("--apply")
    assert result.returncode != 0, _shown(result, 1)
    assert "parent-traversal" in result.stderr
    assert harness.doc_text() == before


# ---------------------------------------------------------------------------
# Test 19 -- SWEEP-11 / D-01 / D-10 / T-154-21: the tool was NOT applied here
#
# NARROWED in Phase 159 (159-01): the Phase-154 guard treated ANY citation-
# bearing path touched by ANYTHING as proof of production application, which
# breaks on ordinary Phase-159 execution noise -- STATE.md bookkeeping and a
# user's own COBS-decision relocation are not evidence a remap ran (research
# finding 4). The guard now (a) excludes that KNOWN-BENIGN bookkeeping from
# the "applied" set instead of treating it as proof, and (b) adds a DIRECT
# check: no production receipt under `.planning/milestones/v1.33-artifacts/` may record an apply
# event yet, which is what production application actually looks like.
# ---------------------------------------------------------------------------
#: Ordinary orchestrator bookkeeping and a user's own document relocation --
#: never evidence that this tool's `--apply` ran against real citations.
_KNOWN_BENIGN_PLANNING_PATHS = frozenset(
    {".planning/STATE.md", ".planning/v1.9-COBS-DECISION.md"}
)


def test_the_tool_is_not_applied_to_any_real_planning_document():
    meta = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
    real_manifest = os.path.join(
        meta, ".planning", "v1.33", "sweep-citation-manifest.jsonl"
    )
    if not os.path.isfile(real_manifest) or not os.path.isdir(
        os.path.join(meta, ".git")
    ):
        pytest.skip("the real manifest or the meta repository is not present here")

    citing = set()
    with open(real_manifest, encoding="utf-8") as handle:
        for line in handle:
            if '"_schema"' in line[:20]:
                continue
            citing.add(json.loads(line)["planning_file"])
    assert len(citing) > 100, "the citation-bearing set is implausibly small"

    changed = subprocess.run(
        ["git", "-C", meta, "diff", "--name-only", "HEAD", "--", ".planning"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert changed.returncode == 0, changed.stderr
    touched = {
        path
        for path in changed.stdout.split()
        if not path.startswith(".planning/milestones/v1.33-artifacts/")
        and path not in _KNOWN_BENIGN_PLANNING_PATHS
    }
    applied = sorted(touched & citing)
    assert not applied, (
        "the remap tool must be BUILT in Phase 154 and APPLIED in Phase 159 "
        f"(D-01/D-10), but these citation-bearing documents are modified: {applied}"
    )

    # The DIRECT check: production application looks like a receipt recording
    # at least one apply event, not like an arbitrary citation-bearing path
    # being dirty. No such receipt may exist anywhere under .planning/milestones/v1.33-artifacts/
    # at this point in the phase.
    v133_dir = os.path.join(meta, ".planning", "v1.33")
    for dirpath, _dirnames, filenames in os.walk(v133_dir):
        for fname in filenames:
            if "receipt" not in fname.lower() or not fname.endswith(".json"):
                continue
            fpath = os.path.join(dirpath, fname)
            try:
                with open(fpath, encoding="utf-8") as handle:
                    data = json.load(handle)
            except (OSError, json.JSONDecodeError):
                continue
            events = data.get("production_apply_events")
            assert not events, (
                f"{fpath} records {events} production apply event(s), but no "
                "production apply is authorized until Phase 159 plan 05"
            )


# ===========================================================================
# PHASE 159 HARDENING LEGS (159-01) -- REMAP-01/02/03/05
#
# Everything below exercises ADDITIVE surface only. None of it is applied
# against any real `.planning/` document (T-154-21/D-01/D-10): every fixture
# below is a disposable `tmp_path` repo or the committed unit-test fixtures,
# exactly like every Phase-154 leg above.
# ===========================================================================
import hashlib as _hashlib  # noqa: E402 -- appended module, after sys.path setup


# ---------------------------------------------------------------------------
# stable_record_id: deterministic identity
# ---------------------------------------------------------------------------
def test_stable_record_id_is_deterministic_and_order_independent():
    old = _read_lines(_CHAINED_OLD)
    rec_a = _record(3, "colon_single", _TARGET_REL, 15, None, old)
    rec_b = dict(rec_a)  # a fresh dict with the same content, different identity
    assert rc.stable_record_id(rec_a) == rc.stable_record_id(rec_b)
    assert rc.stable_record_id(rec_a).startswith("orig-")

    rec_c = _record(3, "colon_single", _TARGET_REL, 20, None, old)
    assert rc.stable_record_id(rec_a) != rc.stable_record_id(rec_c), (
        "two records at different pre-sweep coordinates must not collide"
    )


def test_stable_record_id_honours_an_explicit_record_id():
    old = _read_lines(_CHAINED_OLD)
    rec = _record(3, "colon_single", _TARGET_REL, 15, None, old)
    rec["record_id"] = "late-0042"
    assert rc.stable_record_id(rec) == "late-0042"


# ---------------------------------------------------------------------------
# The real REMAP-03 range proof: json_parser.c:128-131 -> 316-318, using the
# ACTUAL firestarter git blobs at the original and final anchors. This is a
# read-only `git show` against a real repository the executor's environment
# already has populated; it performs no write and touches no `.planning/`
# document.
# ---------------------------------------------------------------------------
_REAL_FW_OLD_SHA = "8695ee52c27a4bee4387c5c489afd5f3d7275e8a"
_REAL_FW_NEW_SHA = "2ccda8d43c8161a34fb5f83b9ab12c37a443bf22"
_REAL_FW_ROOT = os.path.abspath(
    os.path.join(_HERE, "..", "..", "..", "firestarter")
)


def _real_firmware_available():
    return (
        os.path.isdir(os.path.join(_REAL_FW_ROOT, ".git"))
        and rc.git_show(rc.Path(_REAL_FW_ROOT), _REAL_FW_OLD_SHA, "src/json_parser.c")
        is not None
        and rc.git_show(rc.Path(_REAL_FW_ROOT), _REAL_FW_NEW_SHA, "src/json_parser.c")
        is not None
    )


@pytest.mark.skipif(
    not _real_firmware_available(),
    reason="the real firestarter submodule or its historical blobs are not present here",
)
def test_real_json_parser_range_shrinks_128_131_to_316_318():
    old_text = rc.git_show(rc.Path(_REAL_FW_ROOT), _REAL_FW_OLD_SHA, "src/json_parser.c")
    new_text = rc.git_show(rc.Path(_REAL_FW_ROOT), _REAL_FW_NEW_SHA, "src/json_parser.c")
    old_lines = old_text.splitlines()
    new_lines = new_text.splitlines()

    assert old_lines[127] == "            if (jsoneq_(json, key_token, key) == 0) {"
    assert old_lines[130] == "                token_idx += 2; // Skip key and simple value"

    lm = rc.LineMap(old_lines, new_lines)
    new_start, new_end, retarget = lm.span(128, 131)
    assert (new_start, new_end, retarget) == (316, 318, False), (new_start, new_end, retarget)
    assert lm.text_at(new_start) == old_lines[127]
    assert lm.text_at(new_end) == old_lines[130]
    assert new_lines[315] == "            if (jsoneq_(json, key_token, key) == 0) {"
    assert new_lines[317] == "                token_idx += 2; // Skip key and simple value"

    old_span, new_span = 131 - 128 + 1, new_end - new_start + 1
    assert old_span == 4 and new_span == 3, (old_span, new_span)


# ---------------------------------------------------------------------------
# Multi-anchor: a record's own `source_sha` overrides the root-wide default,
# and the map cache is keyed by (target_file_resolved, source_sha) -- REMAP-01.
# ---------------------------------------------------------------------------
def test_wrong_original_app_anchor_is_rejected(harness):
    """A WRONG historical anchor produces an oracle VIOLATION, not a clean
    pass -- the general shape research measured for `bc9d592` against
    original app rows (787 violations), reproduced here on the synthetic
    fixture. The wrong blob is the POST-sweep content with one unrelated line
    prepended, so difflib still aligns cleanly but every coordinate is off by
    one -- old line 15 maps to new line 14, whose text is NOT the recorded
    `source_text`.
    """
    wrong_lines = ["-- unrelated wrong-anchor preamble --"] + list(harness.new_lines)
    harness.target.write_text("\n".join(wrong_lines) + "\n", encoding="utf-8")
    assert _git(harness.root, "add", "-A").returncode == 0
    assert _git(harness.root, "commit", "-qm", "wrong anchor content").returncode == 0
    wrong_sha = _git(harness.root, "rev-parse", "HEAD").stdout.strip()
    # Restore the working tree to the real post-sweep state: the commit above
    # only needed to exist in git history, not to persist on disk.
    harness.target.write_text("\n".join(harness.new_lines) + "\n", encoding="utf-8")

    header, records = harness.load_manifest()
    for rec in records:
        if rec["target_line"] == 15 and rec["variant"] == "colon_single":
            rec["source_sha"] = wrong_sha
    harness.write_manifest(header, records)

    result = harness.run("--apply")
    assert result.returncode == 1, _shown(result, 1)
    assert "oracle violated" in result.stderr, result.stderr


def test_correct_anchor_via_explicit_source_sha_passes(harness):
    """The CORRECT historical anchor, supplied per-record via `source_sha`
    instead of the root-wide `--pre-sweep-sha`, passes exactly like the
    default path."""
    header, records = harness.load_manifest()
    for rec in records:
        rec["source_sha"] = harness.sha
    harness.write_manifest(header, records)
    result = harness.run("--apply", "--quiet-notes")
    assert result.returncode == 0, _shown(result, 0)


def test_two_shas_for_the_same_target_produce_independent_maps(tmp_path):
    """Two SHAs for the SAME `target_file_resolved` must not share one
    path-keyed map: flipping every record's `source_sha` between a correct
    and a wrong anchor, on the SAME target file and SAME manifest, flips the
    outcome -- proof the cache key is `(target_file_resolved, source_sha)`,
    not path alone.
    """
    old = _read_lines(_CHAINED_OLD)
    new = _read_lines(_CHAINED_NEW)
    h = Harness(tmp_path, old_lines=old, new_lines=new)
    correct_sha = h.sha

    wrong_lines = ["-- unrelated wrong-anchor preamble --"] + list(new)
    h.target.write_text("\n".join(wrong_lines) + "\n", encoding="utf-8")
    assert _git(h.root, "add", "-A").returncode == 0
    assert _git(h.root, "commit", "-qm", "wrong anchor").returncode == 0
    wrong_sha = _git(h.root, "rev-parse", "HEAD").stdout.strip()
    h.target.write_text("\n".join(new) + "\n", encoding="utf-8")

    header, records = h.load_manifest()
    for rec in records:
        rec["source_sha"] = correct_sha
    h.write_manifest(header, records)
    ok = h.run("--apply", "--quiet-notes")
    assert ok.returncode == 0, _shown(ok, 0)

    # Re-seed the citing document (the successful apply above already rewrote
    # it) for the negative half of this same-target cross-check.
    shutil.copyfile(_DOC_MIN, h.doc)
    for rec in records:
        rec["source_sha"] = wrong_sha
    h.write_manifest(header, records)
    bad = h.run("--apply")
    assert bad.returncode == 1, _shown(bad, 1)
    assert "oracle violated" in bad.stderr, bad.stderr


# ---------------------------------------------------------------------------
# LocationResolver: planning-location reconciliation -- REMAP-01/02
# ---------------------------------------------------------------------------
def _init_repo(root):
    (root / ".planning").mkdir(parents=True, exist_ok=True)
    assert _git(root, "init", "-q").returncode == 0
    return root


def test_location_resolver_found_when_the_recorded_path_still_exists(tmp_path):
    root = _init_repo(tmp_path / "repo")
    (root / ".planning" / "doc.md").write_text("hello\n", encoding="utf-8")
    resolver = rc.LocationResolver(root)
    outcome = resolver.resolve(".planning/doc.md")
    assert outcome.status == "found"
    assert outcome.resolved_path == ".planning/doc.md"


def test_location_resolver_missing_with_no_overlay_or_rename(tmp_path):
    root = _init_repo(tmp_path / "repo")
    resolver = rc.LocationResolver(root)
    outcome = resolver.resolve(".planning/todos/pending/x.md")
    assert outcome.status == "missing"
    assert "no approved overlay or tracked rename" in outcome.reason


def test_location_resolver_tracked_rename_via_planning_base_sha(tmp_path):
    """A citing document renamed by a TRACKED git commit (e.g. the real
    pending -> completed todo rename research measured) resolves via
    `--planning-base-sha`, without any overlay authorization needed."""
    root = _init_repo(tmp_path / "repo")
    old_path = root / ".planning" / "todos" / "pending" / "task.md"
    old_path.parent.mkdir(parents=True)
    old_path.write_text("todo content\n", encoding="utf-8")
    assert _git(root, "add", "-A").returncode == 0
    assert _git(root, "commit", "-qm", "add pending todo").returncode == 0
    base_sha = _git(root, "rev-parse", "HEAD").stdout.strip()

    new_path = root / ".planning" / "todos" / "completed" / "task.md"
    new_path.parent.mkdir(parents=True)
    assert _git(root, "mv", str(old_path), str(new_path)).returncode == 0
    assert _git(root, "commit", "-qm", "mark todo completed").returncode == 0

    resolver = rc.LocationResolver(root, planning_base_sha=base_sha)
    outcome = resolver.resolve(".planning/todos/pending/task.md")
    assert outcome.status == "renamed", outcome
    assert outcome.resolved_path == ".planning/todos/completed/task.md"


def test_location_resolver_overlay_approved_by_matching_hash(tmp_path):
    root = _init_repo(tmp_path / "repo")
    current = root / ".planning" / "v1.33" / "relocated.md"
    current.parent.mkdir(parents=True)
    current.write_text("moved content\n", encoding="utf-8")
    digest = _hashlib.sha256(current.read_bytes()).hexdigest()

    overlay = [
        {
            "path": ".planning/old-name.md",
            "current_path": ".planning/milestones/v1.33-artifacts/relocated.md",
            "preapply_sha256": digest,
            "expected_postapply_sha256": digest,
        }
    ]
    resolver = rc.LocationResolver(root, overlays=overlay)
    outcome = resolver.resolve(".planning/old-name.md")
    assert outcome.status == "overlay"
    assert outcome.resolved_path == ".planning/milestones/v1.33-artifacts/relocated.md"


def test_location_resolver_rejects_a_third_overlay_state(tmp_path):
    """An overlay whose live bytes match NEITHER declared hash is a THIRD
    state and is REJECTED -- never guessed at."""
    root = _init_repo(tmp_path / "repo")
    current = root / ".planning" / "v1.33" / "relocated.md"
    current.parent.mkdir(parents=True)
    current.write_text("content that drifted after the overlay was approved\n", encoding="utf-8")

    overlay = [
        {
            "path": ".planning/old-name.md",
            "current_path": ".planning/milestones/v1.33-artifacts/relocated.md",
            "preapply_sha256": "0" * 64,
            "expected_postapply_sha256": "1" * 64,
        }
    ]
    resolver = rc.LocationResolver(root, overlays=overlay)
    outcome = resolver.resolve(".planning/old-name.md")
    assert outcome.status == "missing"
    assert "neither approved hash" in outcome.reason


# ---------------------------------------------------------------------------
# Fail-closed hardening engaged by `--exceptions` -- REMAP-02
#
# Without `--exceptions`, the original Phase-154 diagnostic behaviour (a
# dynamic retarget or an unmatched group is a NOTE, exit 0) is UNCHANGED --
# see `test_replace_is_treated_as_non_surviving` above, which still passes
# untouched. `--exceptions` engages hardening: the SAME class of outcome
# becomes a violation unless a reviewed ledger row covers it.
# ---------------------------------------------------------------------------
def test_unreviewed_dynamic_retarget_is_blocking_once_exceptions_engaged(tmp_path):
    old = _read_lines(_CHAINED_OLD)
    new = _read_lines(_CHAINED_NEW)
    reflow_index = new.index("static uint8_t demo_state;")
    new = list(new)
    new[reflow_index] = "static uint8_t demo_state;  // reflowed by the sweep"
    doc = "A citation at the reflowed line: firestarter/src/chained_demo.cpp:6\n"
    harness = Harness(tmp_path, old_lines=old, new_lines=new, doc_text=doc)

    header, _ = harness.load_manifest()
    rec = _record(1, "colon_single", _TARGET_REL, 6, None, old)
    harness.write_manifest(header, [rec])

    empty_ledger = tmp_path / "exceptions.jsonl"
    empty_ledger.write_text("", encoding="utf-8")

    result = harness.run("--apply", "--exceptions", str(empty_ledger))
    assert result.returncode == 1, _shown(result, 1)
    assert "blocking under fail-closed hardening" in result.stderr, result.stderr
    assert harness.doc_text() == doc, "a blocked run must write nothing"


def test_reviewed_retarget_is_applied_via_exceptions_ledger(tmp_path):
    old = _read_lines(_CHAINED_OLD)
    new = _read_lines(_CHAINED_NEW)
    reflow_index = new.index("static uint8_t demo_state;")
    new = list(new)
    new[reflow_index] = "static uint8_t demo_state;  // reflowed by the sweep"
    doc = "A citation at the reflowed line: firestarter/src/chained_demo.cpp:6\n"
    harness = Harness(tmp_path, old_lines=old, new_lines=new, doc_text=doc)

    header, _ = harness.load_manifest()
    rec = _record(1, "colon_single", _TARGET_REL, 6, None, old)
    harness.write_manifest(header, [rec])

    rid = rc.stable_record_id(rec)
    chosen_line = reflow_index + 1
    ledger = tmp_path / "exceptions.jsonl"
    ledger.write_text(
        json.dumps(
            {
                "record_id": rid,
                "status": "reviewed",
                "chosen_target_line": chosen_line,
                "chosen_target_line_end": None,
                "chosen_current_text": new[reflow_index],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = harness.run("--apply", "--exceptions", str(ledger))
    assert result.returncode == 0, _shown(result, 0)
    assert harness.cited(1).endswith(f":{chosen_line}"), harness.cited(1)


def test_reviewed_entry_with_stale_chosen_text_still_fails_the_oracle(tmp_path):
    """A reviewed row is RE-VERIFIED against its own `chosen_current_text`
    oracle -- a stale review (the chosen coordinate no longer reads the
    chosen text) is still a violation, never trusted blindly."""
    old = _read_lines(_CHAINED_OLD)
    new = _read_lines(_CHAINED_NEW)
    reflow_index = new.index("static uint8_t demo_state;")
    new = list(new)
    new[reflow_index] = "static uint8_t demo_state;  // reflowed by the sweep"
    doc = "A citation at the reflowed line: firestarter/src/chained_demo.cpp:6\n"
    harness = Harness(tmp_path, old_lines=old, new_lines=new, doc_text=doc)

    header, _ = harness.load_manifest()
    rec = _record(1, "colon_single", _TARGET_REL, 6, None, old)
    harness.write_manifest(header, [rec])

    rid = rc.stable_record_id(rec)
    ledger = tmp_path / "exceptions.jsonl"
    ledger.write_text(
        json.dumps(
            {
                "record_id": rid,
                "status": "reviewed",
                "chosen_target_line": reflow_index + 1,
                "chosen_target_line_end": None,
                "chosen_current_text": "this text is not actually there",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = harness.run("--apply", "--exceptions", str(ledger))
    assert result.returncode == 1, _shown(result, 1)
    assert "current-target-text oracle" in result.stderr, result.stderr
    assert harness.doc_text() == doc


# ---------------------------------------------------------------------------
# Phase 159-04 B1 -- a `retarget: true` row is normally inert BY NAME
# (FLAGGED_RETARGET, D-08) regardless of --exceptions. A reviewed ledger
# entry must now be consulted for it via the LiveOnlyMap bypass, making the
# human's approval actually take effect.
# ---------------------------------------------------------------------------
def test_reviewed_bypass_applies_to_a_retarget_true_row(tmp_path):
    old = _read_lines(_CHAINED_OLD)
    new = _read_lines(_CHAINED_NEW)
    doc = (
        "A citation AT a deleted line, hand-chosen retarget: firestarter/src/chained_demo.cpp:5\n"
        "A plain surviving citation, present only so the manifest is not "
        "ENTIRELY retarget-flagged (D-09's empty-input-set guard): "
        "firestarter/src/chained_demo.cpp:15\n"
    )
    def _manifest(h):
        header, _ = h.load_manifest()
        r = _record(1, "colon_single", _TARGET_REL, 5, None, old)
        r["retarget"] = True
        s = _record(2, "colon_single", _TARGET_REL, 15, None, old)
        h.write_manifest(header, [r, s])
        return r

    chosen_line = new.index(
        "// Two SEPARATED blocks are the whole point: one block cannot produce a chain."
    ) + 1

    def _ledger_row(rid):
        return json.dumps(
            {
                "record_id": rid,
                "status": "reviewed",
                "chosen_target_line": chosen_line,
                "chosen_target_line_end": None,
                "chosen_current_text": new[chosen_line - 1],
            }
        ) + "\n"

    # Without the fix: a retarget:true row is inert BY NAME even with a
    # reviewed ledger entry present -- FLAGGED_RETARGET, never a REWRITE,
    # nothing written. Proven first, on an INDEPENDENT harness/tmp_path (so
    # the survivor record's own natural rewrite in this baseline run cannot
    # contaminate the real assertion below), so the REWRITE assertion below
    # is not vacuous against a harness that would have passed anyway.
    baseline_harness = Harness(tmp_path / "baseline", old_lines=old, new_lines=new, doc_text=doc)
    baseline_rec = _manifest(baseline_harness)
    baseline_rid = rc.stable_record_id(baseline_rec)
    empty_ledger = tmp_path / "no_review.jsonl"
    empty_ledger.write_text("", encoding="utf-8")
    baseline = baseline_harness.run("--apply", "--exceptions", str(empty_ledger))
    assert baseline.returncode == 0, _shown(baseline, 0)
    assert baseline_harness.cited(1).endswith(":5"), (
        "an unreviewed retarget row must write nothing",
        baseline_harness.cited(1),
    )

    harness = Harness(tmp_path, old_lines=old, new_lines=new, doc_text=doc)
    rec = _manifest(harness)
    rid = rc.stable_record_id(rec)
    assert rid == baseline_rid
    ledger = tmp_path / "exceptions.jsonl"
    ledger.write_text(_ledger_row(rid), encoding="utf-8")

    result = harness.apply("--exceptions", str(ledger))
    assert result.returncode == 0, _shown(result, 0)
    assert harness.cited(1).endswith(f":{chosen_line}"), harness.cited(1)


def test_reviewed_bypass_retarget_row_is_idempotent_on_second_dry_run(tmp_path):
    """The 159-04 idempotency fix: a reviewed retarget row must NOT report a
    REWRITE forever on every subsequent dry run once its citation already
    reads the reviewed answer (REMAP-02/REMAP-05)."""
    old = _read_lines(_CHAINED_OLD)
    new = _read_lines(_CHAINED_NEW)
    doc = (
        "A citation AT a deleted line, hand-chosen retarget: firestarter/src/chained_demo.cpp:5\n"
        "A plain surviving citation, present only so the manifest is not "
        "ENTIRELY retarget-flagged (D-09's empty-input-set guard): "
        "firestarter/src/chained_demo.cpp:15\n"
    )
    harness = Harness(tmp_path, old_lines=old, new_lines=new, doc_text=doc)

    header, _ = harness.load_manifest()
    rec = _record(1, "colon_single", _TARGET_REL, 5, None, old)
    rec["retarget"] = True
    survivor = _record(2, "colon_single", _TARGET_REL, 15, None, old)
    harness.write_manifest(header, [rec, survivor])
    rid = rc.stable_record_id(rec)

    chosen_line = new.index(
        "// Two SEPARATED blocks are the whole point: one block cannot produce a chain."
    ) + 1
    ledger = tmp_path / "exceptions.jsonl"
    ledger.write_text(
        json.dumps(
            {
                "record_id": rid,
                "status": "reviewed",
                "chosen_target_line": chosen_line,
                "chosen_target_line_end": None,
                "chosen_current_text": new[chosen_line - 1],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    applied = harness.apply("--exceptions", str(ledger))
    assert applied.returncode == 0, _shown(applied, 0)
    after_apply = harness.doc_text()

    report_path = tmp_path / "second_dry.json"
    second = harness.run(
        "--exceptions", str(ledger), "--quiet-notes", "--report-json", str(report_path)
    )
    assert second.returncode == 0, _shown(second, 0)
    assert harness.doc_text() == after_apply, "a dry run must never write"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["totals"]["planned_rewrites"] == 0, report["totals"]
    assert report["totals"]["planned_documents"] == 0, report["totals"]
    assert report["totals"]["fixed_point"] >= 1, report["totals"]


# ---------------------------------------------------------------------------
# Phase 159-04 B3 -- a terminal RETIRED ledger status is an explicit no-op:
# never a violation, never open, never blocking --apply.
# ---------------------------------------------------------------------------
def test_retired_ledger_entry_is_a_terminal_noop(tmp_path):
    old = _read_lines(_CHAINED_OLD)
    new = _read_lines(_CHAINED_NEW)
    reflow_index = new.index("static uint8_t demo_state;")
    new = list(new)
    new[reflow_index] = "static uint8_t demo_state;  // reflowed by the sweep"
    doc = "A citation at the reflowed line: firestarter/src/chained_demo.cpp:6\n"
    harness = Harness(tmp_path, old_lines=old, new_lines=new, doc_text=doc)

    header, _ = harness.load_manifest()
    rec = _record(1, "colon_single", _TARGET_REL, 6, None, old)
    harness.write_manifest(header, [rec])
    rid = rc.stable_record_id(rec)

    ledger = tmp_path / "exceptions.jsonl"
    ledger.write_text(
        json.dumps(
            {
                "record_id": rid,
                "status": "retired",
                "retire_cause": "could_not_be_relocated",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    report_path = tmp_path / "retired.json"
    result = harness.run(
        "--apply", "--exceptions", str(ledger), "--quiet-notes", "--report-json", str(report_path)
    )
    assert result.returncode == 0, _shown(result, 0)
    assert harness.doc_text() == doc, "a retired row must never be rewritten"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["totals"]["retired"] == 1, report["totals"]
    assert report["actionable_counts"]["needs_review"] == 0, report["actionable_counts"]
    assert report["retired_by_cause"] == {"could_not_be_relocated": 1}, report["retired_by_cause"]
    assert report["open_ids"]["needs_review"] == [], report["open_ids"]


# ---------------------------------------------------------------------------
# Phase 159-05 blocker fix: `recordscan:supersedes`-protected lines (Plan
# 130-09 mechanism 3) must never be a remap target, general rule -- not a
# two-record special case. See remap_citations.py's `DELIBERATELY_SUPERSEDED_
# RECORD` / `parse_supersedes_protected_lines`.
# ---------------------------------------------------------------------------
def test_expand_supersedes_line_tokens_handles_single_list_and_range():
    assert rc._expand_supersedes_line_tokens("5") == {5}
    assert rc._expand_supersedes_line_tokens("1,3,7") == {1, 3, 7}
    assert rc._expand_supersedes_line_tokens("10-13") == {10, 11, 12, 13}
    assert rc._expand_supersedes_line_tokens("1, 3-5, 9") == {1, 3, 4, 5, 9}
    # Malformed tokens are skipped, not raised.
    assert rc._expand_supersedes_line_tokens("2,,x,7-3,9") == {2, 9}


def test_parse_supersedes_protected_lines_requires_a_stated_reason():
    text_with_reason = (
        "para\n"
        "<!-- recordscan:supersedes needle=foo lines=2 reason: because -->\n"
    )
    assert rc.parse_supersedes_protected_lines(text_with_reason) == {2: ["foo"]}

    text_no_reason = "para\n<!-- recordscan:supersedes needle=foo lines=2 -->\n"
    assert rc.parse_supersedes_protected_lines(text_no_reason) == {}


def test_supersedes_protected_line_is_never_a_remap_target(tmp_path):
    """A `recordscan:supersedes` marker protecting line 3 of the citing
    document must leave that line's citation byte-unchanged even though the
    identical citation shape (":15" on the chain) is exactly what every OTHER
    test in this module proves DOES rewrite (see
    `test_idempotent_on_chained_map`). Line 4's range citation is an
    unprotected control in the SAME document and must still rewrite
    normally -- proving the rule is line-scoped, not document-wide."""
    doc_min = open(_DOC_MIN, encoding="utf-8").read()
    marker = (
        "\n<!-- recordscan:supersedes needle=fake-needle lines=3 reason: "
        "line 3's citation is a deliberately preserved stale figure for "
        "this test; its correction is recorded elsewhere in this file -->\n"
    )
    h = Harness(tmp_path, doc_text=doc_min + marker)

    assert h.cited(3).endswith(":15")
    assert h.cited(4).endswith(":3-18")

    report_path = tmp_path / "supersedes.json"
    result = h.apply("--report-json", str(report_path))
    assert result.returncode == 0, _shown(result, 0)

    assert h.cited(3).endswith(":15"), (
        "a recordscan:supersedes-protected line must never be rewritten: "
        f"got {h.cited(3)!r}"
    )
    assert h.cited(4).endswith(":3-13"), (
        "an UNPROTECTED control citation in the same document must still "
        f"remap normally: got {h.cited(4)!r}"
    )

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["retired_by_cause"].get("deliberately_superseded_record") == 1, (
        report["retired_by_cause"]
    )
    assert report["actionable_counts"]["needs_review"] == 0, report["actionable_counts"]

    # Idempotent: a second apply is a byte-for-byte no-op on the protected line.
    after_run_1 = h.doc_text()
    assert h.apply().returncode == 0
    assert h.doc_text() == after_run_1
    assert h.cited(3).endswith(":15")


# ---------------------------------------------------------------------------
# Phase 159-05 preflight discovery: a `.gitignore`d citing document (found in
# the real corpus: `.planning/graphs/graph.json` /
# `.planning/graphs/.last-build-snapshot.json`, both regenerable graphify
# build caches) must never be a remap target -- general rule, matched by
# `git check-ignore`, not a two-path special case. See
# `GITIGNORED_CITING_DOCUMENT` / `_is_gitignored_citing_document`.
# ---------------------------------------------------------------------------
def test_gitignored_citing_document_is_never_a_remap_target(harness, tmp_path):
    """The harness's own default citing document (`.planning/doc_min.md`,
    8 records) is proven to rewrite normally by every other test in this
    module (e.g. `test_idempotent_on_chained_map`). Adding a `.gitignore`
    rule for that exact path must leave EVERY citation on it byte-unchanged,
    with each record reported RETIRED under the new cause -- never read,
    never written, no violation, no needs_review."""
    # Realistic shape of the real corpus's two graph-cache hits: UNTRACKED
    # and gitignored (git does not report an already-TRACKED path as
    # ignored, by design -- see `git help check-ignore`), so the harness's
    # pre-committed doc is un-tracked here first.
    assert _git(harness.root, "rm", "-q", "--cached", _DOC_REL).returncode == 0
    assert _git(harness.root, "commit", "-qm", "untrack doc_min.md for this test").returncode == 0
    with open(os.path.join(str(harness.root), ".gitignore"), "w", encoding="utf-8") as fh:
        fh.write(_DOC_REL + "\n")

    before = harness.doc_text()
    assert harness.cited(3).endswith(":15")

    report_path = tmp_path / "gitignored.json"
    result = harness.apply("--report-json", str(report_path))
    assert result.returncode == 0, _shown(result, 0)
    assert harness.doc_text() == before, (
        "a gitignored citing document must never be rewritten, even though "
        "the identical citation shape rewrites in every other test"
    )

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["retired_by_cause"].get(
        "citing_document_is_gitignored_generated_artifact"
    ) == 8, report["retired_by_cause"]
    assert report["actionable_counts"]["needs_review"] == 0, report["actionable_counts"]
    assert report["affected_documents"] == [], report["affected_documents"]


def test_reviewed_bypass_collapses_a_range_retarget_to_a_point_and_is_idempotent(tmp_path):
    """Phase 159-04: `hand_choice_retargeted_verbatim` (16 real decisions)
    supplies only a START for a record whose manifest citation is a RANGE
    (`target_line_end` not None) -- a deliberate collapse to a single
    relocated point, not a missing end. Proves: (1) the FIRST apply rewrites
    `path:START-END` to `path:START`; (2) a second dry run reports zero
    rewrites/documents, i.e. it does not regress into a permanent
    NO_MATCH_IN_DOCUMENT once the citation's own grammar has changed shape.
    """
    old = _read_lines(_CHAINED_OLD)
    new = _read_lines(_CHAINED_NEW)
    doc = (
        "A stale range citation over a vanished comment block: firestarter/src/chained_demo.cpp:4-5\n"
        "A plain surviving citation, present only so the manifest is not "
        "ENTIRELY retarget-flagged (D-09's empty-input-set guard): "
        "firestarter/src/chained_demo.cpp:15\n"
    )
    harness = Harness(tmp_path, old_lines=old, new_lines=new, doc_text=doc)

    header, _ = harness.load_manifest()
    rec = _record(1, "colon_range", _TARGET_REL, 4, 5, old)
    rec["retarget"] = True
    survivor = _record(2, "colon_single", _TARGET_REL, 15, None, old)
    harness.write_manifest(header, [rec, survivor])
    rid = rc.stable_record_id(rec)

    chosen_line = new.index("static uint8_t demo_state;") + 1
    ledger = tmp_path / "exceptions.jsonl"
    ledger.write_text(
        json.dumps(
            {
                "record_id": rid,
                "status": "reviewed",
                "chosen_target_line": chosen_line,
                "chosen_target_line_end": None,
                "chosen_current_text": new[chosen_line - 1],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    applied = harness.apply("--exceptions", str(ledger))
    assert applied.returncode == 0, _shown(applied, 0)
    cited_after_apply = harness.cited(1)
    assert cited_after_apply == f"firestarter/src/chained_demo.cpp:{chosen_line}", cited_after_apply

    report_path = tmp_path / "second_dry.json"
    second = harness.run(
        "--exceptions", str(ledger), "--quiet-notes", "--report-json", str(report_path)
    )
    assert second.returncode == 0, _shown(second, 0)
    assert harness.cited(1) == cited_after_apply, "a dry run must never write"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["totals"]["planned_rewrites"] == 0, report["totals"]
    assert report["totals"]["planned_documents"] == 0, report["totals"]
    assert report["open_ids"]["needs_review"] == []


def test_unmatched_in_document_is_blocking_once_exceptions_engaged(harness, tmp_path):
    header, records = harness.load_manifest()
    colon_list_recs = [
        r for r in records if r["planning_line"] == 6 and r["variant"] == "colon_list"
    ]
    assert len(colon_list_recs) == 2, colon_list_recs
    extra = dict(colon_list_recs[0])
    extra["target_line"] = 999  # a third record for a group with only 2 spans
    records.append(extra)
    harness.write_manifest(header, records)

    empty_ledger = tmp_path / "exceptions.jsonl"
    empty_ledger.write_text("", encoding="utf-8")

    result = harness.run("--apply", "--exceptions", str(empty_ledger))
    assert result.returncode == 1, _shown(result, 1)
    assert "unmatched rows are blocking" in result.stderr, result.stderr


def test_without_exceptions_the_same_scenarios_stay_legacy_exit_0(tmp_path):
    """Sanity anchor: `--exceptions` absent means the Phase-154 diagnostic
    behaviour is completely unchanged for the exact scenario that is blocking
    above."""
    old = _read_lines(_CHAINED_OLD)
    new = _read_lines(_CHAINED_NEW)
    reflow_index = new.index("static uint8_t demo_state;")
    new = list(new)
    new[reflow_index] = "static uint8_t demo_state;  // reflowed by the sweep"
    doc = "A citation at the reflowed line: firestarter/src/chained_demo.cpp:6\n"
    harness = Harness(tmp_path, old_lines=old, new_lines=new, doc_text=doc)
    header, _ = harness.load_manifest()
    rec = _record(1, "colon_single", _TARGET_REL, 6, None, old)
    harness.write_manifest(header, [rec])

    result = harness.run("--apply")
    assert result.returncode == 0, _shown(result, 0)
    assert harness.doc_text() == doc, "a retarget record must never be rewritten"


# ---------------------------------------------------------------------------
# BatchTransaction: receipted apply, injected-failure recovery -- REMAP-01/05
# ---------------------------------------------------------------------------
def test_successful_receipted_apply_records_one_production_event(harness, tmp_path):
    receipt_path = tmp_path / "receipt.json"
    bundle_dir = tmp_path / "bundle"
    result = harness.run(
        "--apply", "--quiet-notes",
        "--production-receipt", str(receipt_path),
        "--recovery-bundle", str(bundle_dir),
    )
    assert result.returncode == 0, _shown(result, 0)
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["status"] == "APPLIED"
    assert receipt["production_apply_events"] == 1
    assert receipt["rollback_status"] is None
    assert receipt["failure"] is None
    assert receipt["replaced_documents"] == [".planning/doc_min.md"]


def test_pre_existing_receipt_blocks_a_new_apply(harness, tmp_path):
    receipt_path = tmp_path / "receipt.json"
    bundle_dir = tmp_path / "bundle"
    first = harness.run(
        "--apply", "--quiet-notes",
        "--production-receipt", str(receipt_path),
        "--recovery-bundle", str(bundle_dir),
    )
    assert first.returncode == 0, _shown(first, 0)

    second = harness.run(
        "--apply", "--quiet-notes",
        "--production-receipt", str(receipt_path),
        "--recovery-bundle", str(bundle_dir),
    )
    assert second.returncode == 1, _shown(second, 1)
    assert "pre-existing receipt blocks a new apply" in second.stderr


def test_injected_mid_batch_failure_restores_every_preimage(tmp_path):
    """An injected write failure AFTER at least one successful replacement
    restores every already-replaced document from its preimage, marks the
    receipt FAILED / rollback_status COMPLETE, and writes nothing further --
    the batch-recovery contract REMAP-01/05 requires."""
    old = _read_lines(_CHAINED_OLD)
    new = _read_lines(_CHAINED_NEW)
    h = Harness(tmp_path, old_lines=old, new_lines=new)

    # A SECOND citing document, so the batch has two documents to replace --
    # one succeeds before the injected failure fires on the other.
    second_doc = h.root / ".planning" / "doc_second.md"
    second_doc.write_text(
        "Another point citation: firestarter/src/chained_demo.cpp:15\n",
        encoding="utf-8",
    )
    header, records = h.load_manifest()
    extra = dict(
        next(r for r in records if r["target_line"] == 15 and r["variant"] == "colon_single")
    )
    extra["planning_file"] = ".planning/doc_second.md"
    extra["planning_line"] = 1
    records.append(extra)
    h.write_manifest(header, records)

    before_first = h.doc_text()
    before_second = second_doc.read_text(encoding="utf-8")

    receipt_path = tmp_path / "receipt.json"
    bundle_dir = tmp_path / "bundle"
    result = h.run(
        "--apply", "--quiet-notes",
        "--production-receipt", str(receipt_path),
        "--recovery-bundle", str(bundle_dir),
        "--inject-write-failure-after", "1",
    )
    assert result.returncode == 1, _shown(result, 1)
    assert h.doc_text() == before_first, "the FIRST replaced document must be rolled back"
    assert second_doc.read_text(encoding="utf-8") == before_second, "never reached by the batch"

    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["status"] == "FAILED"
    assert receipt["rollback_status"] == "COMPLETE"
    assert receipt["production_apply_events"] == 0
    assert len(receipt["replaced_documents"]) == 1
    assert receipt["failure"]["message"].startswith("injected write failure")


def test_inject_write_failure_refuses_the_canonical_live_root(tmp_path):
    dummy_manifest = tmp_path / "manifest.jsonl"
    shutil.copyfile(_MANIFEST_MIN, dummy_manifest)
    result = subprocess.run(
        [
            sys.executable, _TOOL, "/workspaces",
            "--manifest", str(dummy_manifest),
            "--pre-sweep-sha", "0" * 40,
            "--inject-write-failure-after", "0",
        ],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 2, _shown(result, 2)
    assert "refuses the canonical live root" in result.stderr


def test_recover_receipt_restores_an_interrupted_applying_state_without_resuming(tmp_path):
    """If the PROCESS itself dies mid-`APPLYING` (so `apply()`'s own
    except/rollback block never runs), `--recover-receipt` restores from the
    preimage bundle and marks the receipt RECOVERED -- but it never resumes
    or replays the apply: the second document's PLANNED text is never
    written, only its ORIGINAL preimage is guaranteed."""
    root = tmp_path / "repo"
    (root / "docs").mkdir(parents=True)
    doc_a = root / "docs" / "a.md"
    doc_b = root / "docs" / "b.md"
    doc_a.write_text("original a\n", encoding="utf-8")
    doc_b.write_text("original b\n", encoding="utf-8")
    planned = {doc_a: "updated a\n", doc_b: "updated b\n"}

    receipt_path = tmp_path / "receipt.json"
    bundle_dir = tmp_path / "bundle"
    txn = rc.BatchTransaction(root, planned, receipt_path, bundle_dir, "fp-crash")
    txn.prepare()

    # Simulate the crash: hand-advance to APPLYING and replace ONLY doc_a,
    # exactly as `apply()` would have done before a kill -9 prevented it from
    # ever reaching its own except/rollback block.
    prepared = rc.read_receipt(receipt_path)
    prepared["status"] = "APPLYING"
    rc.write_json_report(receipt_path, prepared)
    rc.atomic_write(doc_a, "updated a\n")
    assert doc_a.read_text(encoding="utf-8") == "updated a\n"

    receipt = rc.recover_failed_receipt(receipt_path, root, bundle_dir)
    assert receipt["status"] == "RECOVERED"
    assert receipt["rollback_status"] == "COMPLETE"
    assert doc_a.read_text(encoding="utf-8") == "original a\n", (
        "recovery must restore from the preimage bundle"
    )
    assert doc_b.read_text(encoding="utf-8") == "original b\n"
    assert receipt.get("production_apply_events", 0) == 0, "recovery is not an apply event"


def test_recover_receipt_on_an_already_applied_receipt_is_a_no_op(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    doc_a = root / "a.md"
    doc_a.write_text("original\n", encoding="utf-8")
    planned = {doc_a: "updated\n"}
    receipt_path = tmp_path / "receipt.json"
    bundle_dir = tmp_path / "bundle"
    txn = rc.BatchTransaction(root, planned, receipt_path, bundle_dir, "fp-settled")
    txn.prepare()
    receipt = txn.apply()
    assert receipt["status"] == "APPLIED"

    recovered = rc.recover_failed_receipt(receipt_path, root, bundle_dir)
    assert recovered["status"] == "APPLIED", "recovery of a settled receipt is a no-op"
    assert doc_a.read_text(encoding="utf-8") == "updated\n"


# ---------------------------------------------------------------------------
# build_index_stage_plan / --index-plan -- REMAP-01
# ---------------------------------------------------------------------------
def test_index_plan_clean_tracked_file_is_citation_only(harness, tmp_path):
    plan_path = tmp_path / "index-plan.json"
    result = harness.run("--apply", "--quiet-notes", "--index-plan", str(plan_path))
    assert result.returncode == 0, _shown(result, 0)
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    rows = [row for row in plan if row["path"] == ".planning/doc_min.md"]
    assert len(rows) == 1, plan
    row = rows[0]
    assert row["index_mode"] == "tracked"
    assert row["staging_strategy"] == "citation_only_index_object"
    assert row["citation_only_blob"], row
    assert row["authorization_id"] is None

    blob_text = subprocess.run(
        ["git", "-C", str(harness.root), "cat-file", "-p", row["citation_only_blob"]],
        capture_output=True, text=True, check=False,
    )
    assert blob_text.returncode == 0, blob_text.stderr
    assert blob_text.stdout == harness.doc_text()


def test_index_plan_dirty_tracked_file_excludes_the_unrelated_edit(harness, tmp_path):
    """A tracked, DIRTY file's `citation_only_blob` must contain the citation
    rewrite but EXCLUDE an unrelated edit already sitting in the working
    tree -- staging the whole file would silently commit that unrelated
    edit alongside the remap."""
    unrelated_marker = "UNRELATED HAND EDIT, NOT PART OF THE REMAP\n"
    dirty_text = harness.doc_text() + unrelated_marker
    harness.doc.write_text(dirty_text, encoding="utf-8")

    plan_path = tmp_path / "index-plan.json"
    result = harness.run("--apply", "--quiet-notes", "--index-plan", str(plan_path))
    assert result.returncode == 0, _shown(result, 0)

    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    row = next(row for row in plan if row["path"] == ".planning/doc_min.md")
    assert row["staging_strategy"] == "citation_only_index_object"

    blob_text = subprocess.run(
        ["git", "-C", str(harness.root), "cat-file", "-p", row["citation_only_blob"]],
        capture_output=True, text=True, check=False,
    )
    assert blob_text.returncode == 0, blob_text.stderr
    assert unrelated_marker not in blob_text.stdout, (
        "the citation-only blob must not absorb the unrelated dirty edit"
    )
    # The LIVE on-disk file (after --apply), by contrast, DOES carry the
    # unrelated edit -- it was never asked to be excluded from the working
    # tree, only from what gets STAGED.
    assert unrelated_marker in harness.doc_text()
    assert harness.cited(3).endswith(":10"), harness.cited(3)


def test_index_plan_untracked_file_requires_authorization(tmp_path):
    old = _read_lines(_CHAINED_OLD)
    new = _read_lines(_CHAINED_NEW)
    h = Harness(tmp_path, old_lines=old, new_lines=new)
    untracked_doc = h.root / ".planning" / "untracked_doc.md"
    untracked_doc.write_text(
        "An untracked citation: firestarter/src/chained_demo.cpp:15\n",
        encoding="utf-8",
    )
    header, records = h.load_manifest()
    extra = dict(
        next(r for r in records if r["target_line"] == 15 and r["variant"] == "colon_single")
    )
    extra["planning_file"] = ".planning/untracked_doc.md"
    extra["planning_line"] = 1
    records.append(extra)
    h.write_manifest(header, records)

    plan_path = tmp_path / "index-plan.json"
    result = h.run("--quiet-notes", "--index-plan", str(plan_path))
    assert result.returncode == 0, _shown(result, 0)
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    row = next(row for row in plan if row["path"] == ".planning/untracked_doc.md")
    assert row["index_mode"] == "untracked"
    assert row["staging_strategy"] == "requires_authorization"
    assert row["citation_only_blob"] is None
    assert row["authorization_id"]


# ---------------------------------------------------------------------------
# --report-json -- structured report -- REMAP-02
# ---------------------------------------------------------------------------
def test_report_json_is_non_vacuous_and_lists_open_ids_for_a_dynamic_retarget(tmp_path):
    old = _read_lines(_CHAINED_OLD)
    new = _read_lines(_CHAINED_NEW)
    reflow_index = new.index("static uint8_t demo_state;")
    new = list(new)
    new[reflow_index] = "static uint8_t demo_state;  // reflowed by the sweep"
    doc = "A citation at the reflowed line: firestarter/src/chained_demo.cpp:6\n"
    harness = Harness(tmp_path, old_lines=old, new_lines=new, doc_text=doc)
    header, _ = harness.load_manifest()
    rec = _record(1, "colon_single", _TARGET_REL, 6, None, old)
    harness.write_manifest(header, [rec])

    report_path = tmp_path / "report.json"
    result = harness.run("--quiet-notes", "--report-json", str(report_path))
    assert result.returncode == 0, _shown(result, 0)

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["totals"]["examined"] == 1
    assert report["totals"]["retarget"] == 1
    # Phase 159-02: `open_ids` is category-keyed (adds a "needs_review"
    # bucket for tracked-pending ledger/overlay rows); the pre-existing
    # non-strict RETARGET outcome (no --exceptions given) lands under its own
    # outcome-named key, and every other category -- including
    # "needs_review" -- stays empty.
    assert report["open_ids"]["retarget"] == [rc.stable_record_id(rec)]
    for cat, ids in report["open_ids"].items():
        if cat != "retarget":
            assert ids == [], f"category {cat!r} expected empty, got {ids}"
    assert report["affected_documents"] == []
    assert report["corpus_fingerprint"]
    assert report["topology_digest"]
    assert report["range_proofs"] == []


def test_report_json_range_proofs_lists_the_real_shrink(harness, tmp_path):
    report_path = tmp_path / "report.json"
    result = harness.run("--apply", "--quiet-notes", "--report-json", str(report_path))
    assert result.returncode == 0, _shown(result, 0)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    shrink = [p for p in report["range_proofs"] if p["old_start"] == 3 and p["old_end"] == 18]
    assert len(shrink) == 1, report["range_proofs"]
    proof = shrink[0]
    assert proof["old_span"] == 16
    assert proof["new_span"] == 11
    assert proof["new_start"] == 3 and proof["new_end"] == 13


# ---------------------------------------------------------------------------
# source_sha_candidates: non-unique historical anchor, blocking until reviewed
# ---------------------------------------------------------------------------
def test_source_sha_candidates_blocks_until_a_reviewed_choice(harness, tmp_path):
    header, records = harness.load_manifest()
    picked = next(r for r in records if r["target_line"] == 15 and r["variant"] == "colon_single")
    picked["source_sha_candidates"] = [harness.sha, "f" * 40]
    harness.write_manifest(header, [picked])

    blocked = harness.run("--apply")
    assert blocked.returncode == 1, _shown(blocked, 1)
    assert "non-unique historical source anchor" in blocked.stderr

    rid = rc.stable_record_id(picked)
    ledger = tmp_path / "exceptions.jsonl"
    ledger.write_text(
        json.dumps({"record_id": rid, "status": "reviewed", "chosen_source_sha": harness.sha}) + "\n",
        encoding="utf-8",
    )
    resolved = harness.run("--apply", "--quiet-notes", "--exceptions", str(ledger))
    assert resolved.returncode == 0, _shown(resolved, 0)
    assert harness.cited(3).endswith(":10"), harness.cited(3)


def test_source_sha_candidates_rejects_a_choice_outside_the_candidate_set(harness, tmp_path):
    header, records = harness.load_manifest()
    picked = next(r for r in records if r["target_line"] == 15 and r["variant"] == "colon_single")
    picked["source_sha_candidates"] = [harness.sha, "f" * 40]
    harness.write_manifest(header, [picked])

    rid = rc.stable_record_id(picked)
    ledger = tmp_path / "exceptions.jsonl"
    ledger.write_text(
        json.dumps({"record_id": rid, "status": "reviewed", "chosen_source_sha": "9" * 40}) + "\n",
        encoding="utf-8",
    )
    result = harness.run("--apply", "--exceptions", str(ledger))
    assert result.returncode == 1, _shown(result, 1)
    assert "non-unique historical source anchor" in result.stderr


# ---------------------------------------------------------------------------
# Repeatable --manifest: multiple manifests are loaded and merged
# ---------------------------------------------------------------------------
def test_repeatable_manifest_merges_records_from_two_files(harness, tmp_path):
    header, records = harness.load_manifest()
    point_records = [r for r in records if r["target_line"] == 15 and r["variant"] == "colon_single"]
    other_records = [r for r in records if r not in point_records]

    manifest_a = tmp_path / "manifest_a.jsonl"
    manifest_b = tmp_path / "manifest_b.jsonl"
    with open(manifest_a, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(header) + "\n")
        for rec in point_records:
            fh.write(json.dumps(rec) + "\n")
    with open(manifest_b, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(header) + "\n")
        for rec in other_records:
            fh.write(json.dumps(rec) + "\n")

    # `Harness.run()` always injects exactly one `--manifest`, so the two
    # intended manifests are passed via a direct subprocess invocation
    # instead.
    result = subprocess.run(
        [
            sys.executable, _TOOL, str(harness.root),
            "--manifest", str(manifest_a),
            "--manifest", str(manifest_b),
            "--pre-sweep-sha", harness.sha,
            "--apply", "--quiet-notes",
        ],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, _shown(result, 0)
    assert harness.cited(3).endswith(":10"), harness.cited(3)


# ---------------------------------------------------------------------------
# --corpus-overlay flows through main(): a relocated citing document is found
# ---------------------------------------------------------------------------
def test_corpus_overlay_resolves_a_relocated_citing_document(tmp_path):
    old = _read_lines(_CHAINED_OLD)
    new = _read_lines(_CHAINED_NEW)
    h = Harness(tmp_path, old_lines=old, new_lines=new)

    relocated_dir = h.root / ".planning" / "v1.33"
    relocated_dir.mkdir(parents=True)
    relocated_doc = relocated_dir / "relocated_doc.md"
    relocated_doc.write_text(
        "A relocated point citation: firestarter/src/chained_demo.cpp:15\n",
        encoding="utf-8",
    )
    digest = _hashlib.sha256(relocated_doc.read_bytes()).hexdigest()

    header, records = h.load_manifest()
    extra = dict(
        next(r for r in records if r["target_line"] == 15 and r["variant"] == "colon_single")
    )
    extra["planning_file"] = ".planning/moved_from_here.md"  # never created on disk
    extra["planning_line"] = 1
    records.append(extra)
    h.write_manifest(header, records)

    overlay_path = tmp_path / "overlay.jsonl"
    overlay_path.write_text(
        json.dumps(
            {
                "path": ".planning/moved_from_here.md",
                "current_path": ".planning/milestones/v1.33-artifacts/relocated_doc.md",
                "preapply_sha256": digest,
                "expected_postapply_sha256": digest,
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = h.run("--apply", "--quiet-notes", "--corpus-overlay", str(overlay_path))
    assert result.returncode == 0, _shown(result, 0)
    assert relocated_doc.read_text(encoding="utf-8").rstrip("\n").endswith(":10")


# ---------------------------------------------------------------------------
# Phase 159-02: tracked-pending review rows are soft (reported, not blocking)
# -- REMAP-01/02.
# ---------------------------------------------------------------------------
def test_exceptions_entry_with_status_needs_review_is_soft_not_blocking(tmp_path):
    """A ledger row with status='needs_review' (not 'reviewed') is a KNOWN,
    tracked gap: it must be reported under open_ids['needs_review'] and the
    run must still write --report-json and exit 1 for THAT reason alone, not
    via the hard `violations` path that blocks the report entirely."""
    old = _read_lines(_CHAINED_OLD)
    new = _read_lines(_CHAINED_NEW)
    reflow_index = new.index("static uint8_t demo_state;")
    new = list(new)
    new[reflow_index] = "static uint8_t demo_state;  // reflowed by the sweep"
    doc = "A citation at the reflowed line: firestarter/src/chained_demo.cpp:6\n"
    harness = Harness(tmp_path, old_lines=old, new_lines=new, doc_text=doc)
    header, _ = harness.load_manifest()
    rec = _record(1, "colon_single", _TARGET_REL, 6, None, old)
    harness.write_manifest(header, [rec])
    rid = rc.stable_record_id(rec)

    exceptions_path = tmp_path / "exceptions.jsonl"
    exceptions_path.write_text(
        json.dumps({"record_id": rid, "status": "needs_review"}) + "\n",
        encoding="utf-8",
    )
    report_path = tmp_path / "report.json"
    result = harness.run(
        "--quiet-notes",
        "--exceptions",
        str(exceptions_path),
        "--report-json",
        str(report_path),
    )
    assert result.returncode == 1, _shown(result, 1)
    assert report_path.is_file(), "the report must still be written for a tracked-pending row"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["open_ids"]["needs_review"] == [rid]
    for cat, ids in report["open_ids"].items():
        if cat != "needs_review":
            assert ids == [], f"category {cat!r} expected empty, got {ids}"
    assert report["actionable_counts"]["needs_review"] == 1
    for k, v in report["actionable_counts"].items():
        if k != "needs_review":
            assert v == 0, f"actionable_counts[{k!r}] expected 0, got {v}"
    assert report["totals"]["examined_records"] > 0
    assert report["totals"]["examined_documents"] > 0
    assert report["totals"]["planned_documents"] == 0  # nothing is rewritten while pending


def test_unlisted_actionable_row_still_hard_blocks_under_exceptions(tmp_path):
    """A record with NO ledger entry at all is still a genuine surprise and
    remains a hard, report-blocking violation -- fail-closed default unchanged."""
    old = _read_lines(_CHAINED_OLD)
    new = _read_lines(_CHAINED_NEW)
    reflow_index = new.index("static uint8_t demo_state;")
    new = list(new)
    new[reflow_index] = "static uint8_t demo_state;  // reflowed by the sweep"
    doc = "A citation at the reflowed line: firestarter/src/chained_demo.cpp:6\n"
    harness = Harness(tmp_path, old_lines=old, new_lines=new, doc_text=doc)
    header, _ = harness.load_manifest()
    rec = _record(1, "colon_single", _TARGET_REL, 6, None, old)
    harness.write_manifest(header, [rec])

    exceptions_path = tmp_path / "exceptions.jsonl"
    exceptions_path.write_text(
        json.dumps({"record_id": "orig-not-this-record", "status": "needs_review"}) + "\n",
        encoding="utf-8",
    )
    report_path = tmp_path / "report.json"
    result = harness.run(
        "--quiet-notes",
        "--exceptions",
        str(exceptions_path),
        "--report-json",
        str(report_path),
    )
    assert result.returncode == 1, _shown(result, 1)
    assert not report_path.is_file(), "an undocumented surprise must block the report entirely"
    assert "unreviewed_retarget" in result.stderr or "BLOCK" in result.stderr


def test_apply_refuses_while_needs_review_is_nonzero(tmp_path):
    """--apply must refuse (exit 1, nothing written) while any record or
    overlay authorization remains tracked-pending."""
    old = _read_lines(_CHAINED_OLD)
    new = _read_lines(_CHAINED_NEW)
    reflow_index = new.index("static uint8_t demo_state;")
    new = list(new)
    new[reflow_index] = "static uint8_t demo_state;  // reflowed by the sweep"
    doc = "A citation at the reflowed line: firestarter/src/chained_demo.cpp:6\n"
    harness = Harness(tmp_path, old_lines=old, new_lines=new, doc_text=doc)
    header, _ = harness.load_manifest()
    rec = _record(1, "colon_single", _TARGET_REL, 6, None, old)
    harness.write_manifest(header, [rec])
    rid = rc.stable_record_id(rec)

    exceptions_path = tmp_path / "exceptions.jsonl"
    exceptions_path.write_text(
        json.dumps({"record_id": rid, "status": "needs_review"}) + "\n",
        encoding="utf-8",
    )
    before = harness.doc_text()
    result = harness.run("--apply", "--quiet-notes", "--exceptions", str(exceptions_path))
    assert result.returncode == 1, _shown(result, 1)
    assert harness.doc_text() == before, "nothing may be written while a decision is pending"


def test_dirty_overlap_overlay_row_surfaces_as_needs_review_without_blocking_resolution(
    tmp_path,
):
    """A corpus-overlay row explicitly marked `dirty_overlap: true` resolves
    the citing document's live location (as Phase 159-01's LocationResolver
    already does) AND is separately surfaced as a pending authorization in
    open_ids['needs_review'] -- it must not silently disappear."""
    h = Harness(tmp_path)
    relocated_dir = h.root / ".planning" / "v1.33"
    relocated_dir.mkdir(parents=True)
    relocated_doc = relocated_dir / "relocated_doc.md"
    relocated_doc.write_text(h.doc.read_text(encoding="utf-8"), encoding="utf-8")
    digest = __import__("hashlib").sha256(relocated_doc.read_bytes()).hexdigest()
    h.doc.unlink()

    header, records = h.load_manifest()
    for rec in records:
        rec["planning_file"] = ".planning/moved_from_here.md"
    h.write_manifest(header, records)

    overlay_path = tmp_path / "overlay.jsonl"
    overlay_path.write_text(
        json.dumps(
            {
                "path": ".planning/moved_from_here.md",
                "current_path": ".planning/milestones/v1.33-artifacts/relocated_doc.md",
                "preapply_sha256": digest,
                "expected_postapply_sha256": digest,
                "dirty_overlap": True,
                "approval_status": "pending",
                "authorization_id": "auth-relocated-doc",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    report_path = tmp_path / "report.json"
    result = h.run(
        "--quiet-notes", "--corpus-overlay", str(overlay_path), "--report-json", str(report_path)
    )
    assert result.returncode == 1, _shown(result, 1)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert "auth-relocated-doc" in report["open_ids"]["needs_review"]
    assert report["actionable_counts"]["needs_review"] >= 1
    # location resolution itself still worked -- the document WAS examined.
    assert report["totals"]["examined_documents"] >= 1


# ---------------------------------------------------------------------------
# Sanity anchor: this plan touches NEITHER the real manifest NOR any real
# citing document (T-154-21/D-01/D-10).
# ---------------------------------------------------------------------------
def test_real_manifest_hash_is_unchanged():
    real_manifest = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(_HERE))),
        ".planning", "v1.33", "sweep-citation-manifest.jsonl",
    )
    if not os.path.isfile(real_manifest):
        pytest.skip("the real manifest is not present here")
    digest = _hashlib.sha256(open(real_manifest, "rb").read()).hexdigest()
    assert digest == "ecdd0fc84be1627f893e30f6369c0b9eedf2a69ce3ec351064828d82e72d992e"
