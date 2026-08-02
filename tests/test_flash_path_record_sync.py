"""
Project Name: Firestarter
Copyright (c) 2024 Henrik Olsson

Permission is hereby granted under MIT license.

Phase 129 Plan 01 (fail-closed half) + Plan 02 (parity half) -- D-03's
fail-closed sync gate over the two copies of the v1.23 flash-path and PCB
requirements record.

Requirements: PCB-01, PCB-02, PCB-03, PCB-04, PCB-05 (mechanical
content-gate slice only -- this module does NOT close any of them, and no
requirement is marked complete in REQUIREMENTS.md from this plan).

Decisions covered: D-01, D-03, D-04, D-11, D-16, D-17

**The shared-section contract.** The two copies are
`.planning/v1.23-FLASH-PATH-DECISION.md` in the meta repo (authoritative)
and `platform/py32f071/FLASH-PATH-AND-PCB.md` in this repo (subset). Five
stable keys name the sections both copies must carry, each appearing as a
suffix on a `## ` heading line in both copies: `S1` three-tier flash path
(`[SHARED:S1]`), `S2` PCB checklist (`[SHARED:S2]`), `S3` flash budget
(`[SHARED:S3]`), `S4` USB VID/PID (`[SHARED:S4]`), `S5` socket-empty
instruction (`[SHARED:S5]`). Only the **body** below each heading is
compared -- the meta copy numbers its headings and the subset does not, so
heading text itself is never part of the comparison. The same five keys are
named in `firestarter/CLAUDE.md` so the human instruction and the machine
gate cannot drift apart (v1.7 precedent).

**CI coverage, stated honestly.** This module executes in NO CI leg on this branch:
`pytest tests/ -v` runs only in `build.yml` (push/PR to `main`) and
`beta-build.yml` (push to `beta`) -- neither fires on this firmware
milestone branch, and `py32f071.yml` has no pytest step at all. The local
run recorded in this phase's evidence artifact is the only evidence this
module's assertions were ever exercised. Never imply CI coverage.

**Single-helper rule.** Every test -- positive legs and planted-violation
legs alike -- goes through the one module-level `_extract_shared_section` /
`_shared_sections` pair, so the RED demonstrations exercise the same
checking code the positive legs do. Two parallel implementations drift and
the RED then proves nothing.

**The RED-first disposition.** This module was committed before either
record existed. Plan 02's parity legs were therefore RED-by-construction on
arrival, and the RED took the form of `MissingScanTargetError` -- the
hard-failure half of the split -- not a skip.

**No conftest.py.** This module resolves its own paths, the same
`_HERE`-relative idiom every other module in this directory uses. No
`conftest.py`, `pytest.ini`, `pyproject.toml`, `setup.cfg` or `tox.ini`
exists anywhere in this repository -- a recorded house rule, not an
omission.

Coverage (this plan's fail-closed half only -- Plan 02 adds the parity and
content class, `TestFlashPathRecordSync`, to this same module):
  1. test_absent_meta_root_skip_is_auditable_not_silent -- F-14 mode 3.
  2. test_absent_meta_claim_can_never_be_false -- the census assertion: a
     skip claiming absence while the marker exists must be impossible.
  3. test_present_root_with_missing_target_raises_not_skips -- F-14 mode
     3's hard half: a missing scan target under a present repo raises.
  4. test_marker_name_is_not_overridable -- the seam overrides the root
     only, never the marker name.
  5. test_empty_extraction_is_not_a_vacuous_pass -- F-14 mode 2.
  6. test_renamed_marker_yields_a_refusal_not_a_guess -- F-14 mode 4.
  7. test_duplicate_marker_refuses_to_guess -- a parser that refuses to
     guess between two candidates.
  8. test_planted_divergence_in_synthetic_copies_is_detected -- F-14 mode
     1.
  9. test_dirty_tree_is_detected -- F-14 mode 5.
  10. test_git_binary_is_required_not_optional.

Plan 02's parity and content class, `TestFlashPathRecordSync` (12 test
functions, 31 collected legs -- RED by construction on arrival, since
neither record exists yet):
  11. test_meta_extract_is_non_vacuous -- parametrized over _SHARED_KEYS (5
      legs).
  12. test_fw_extract_is_non_vacuous -- parametrized over _SHARED_KEYS (5
      legs).
  13. test_shared_sections_match -- parametrized over _SHARED_KEYS (5 legs).
  14. test_three_tiers_and_non_retirement -- parametrized over
      ("meta", "fw") (2 legs). PCB-01.
  15. test_pcb_checklist_rows_are_wellformed -- parametrized over
      ("meta", "fw") (2 legs). PCB-02.
  16. test_flash_budget_cites_reserved_map -- parametrized over
      ("meta", "fw") (2 legs). PCB-03.
  17. test_bootloader_figure_carries_its_cost -- parametrized over
      ("meta", "fw") (2 legs). D-10's proximity gate.
  18. test_vid_pid_decision_and_ship_gate -- parametrized over
      ("meta", "fw") (2 legs). PCB-04.
  19. test_socket_empty_instruction_present -- parametrized over
      ("meta", "fw", "readme") (3 legs). PCB-05.
  20. test_linker_comment_cross_references_record (1 leg). D-11 / C-1.
  21. test_seed_status_is_no_longer_dormant (1 leg). D-17 / D-18.
  22. test_planted_mutation_of_the_real_subset_is_detected (1 leg). F-14
      mode 1 against the real artifact.

Expected-RED ledger on arrival. All 31 legs added by Plan 02 are RED when
this module is committed -- neither `.planning/v1.23-FLASH-PATH-DECISION.md`
nor `platform/py32f071/FLASH-PATH-AND-PCB.md` exists yet. The RED for every
`meta`-side leg is `MissingScanTargetError` (never a skip): `_meta_doc()`
routes through `meta_presence.meta_path()`, which raises under a present
meta repo with a missing target. The RED for every `fw`-side and `readme`
leg is a plain `AssertionError` from the `.exists()` guard in
`_fw_doc_text()` / `_readme_text()`, or (once the firmware subset exists) a
content `AssertionError` from a needle/literal miss. Discharging plan per
group: `129-03` discharges S1 (test 14); `129-04` discharges S2 and S3
(tests 15, 16, 17); `129-05` discharges S4 and S5 (tests 18, 19); `129-06`
discharges every `fw` and `readme` parametrization not already covered, all
five `test_shared_sections_match` legs (test 13) and the planted-mutation
leg (test 22); `129-07` discharges the linker leg (test 20); `129-08`
discharges the seed leg (test 21). Tests 11 and 12 (the per-copy
non-vacuity legs) are discharged incrementally as each record's content
lands.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

# This sibling-package import was proved to resolve at plan time under both
# `python -m pytest tests/ -v` and the bare `pytest tests/ -v` console
# script, run from the firmware repo root. It is the FIRST sibling-helper
# import in this repo's test suite -- every other module self-resolves via
# `Path(__file__)`. It works because `tests/__init__.py` exists and
# pytest's prepend import mode inserts the repo root onto `sys.path`. No
# `conftest.py` is added to make this work.
from tests.meta_presence import (
    META_ABSENT_REASON,
    META_MARKER,
    META_PRESENT,
    META_ROOT,
    MissingScanTargetError,
    meta_path,
    requires_meta,
)

_HERE = Path(__file__).resolve().parent
_FW_REPO_ROOT = _HERE.parent
_FW_DOC = _FW_REPO_ROOT / "platform" / "py32f071" / "FLASH-PATH-AND-PCB.md"

# _META_DOC_REL and _SEED_REL are resolved through
# meta_presence.meta_path(".planning", ...), never by string concatenation,
# so a missing target under a present meta repo raises instead of skipping.
_META_DOC_REL = "v1.23-FLASH-PATH-DECISION.md"
_LINKER = _FW_REPO_ROOT / "platform" / "py32f071" / "linker" / "PY32F071xB_FLASH.ld"
_SEED_REL = "seeds/py32f071-no-external-tool-fw-install.md"

_SHARED_KEYS = ("S1", "S2", "S3", "S4", "S5")

# Built PROGRAMMATICALLY from _SHARED_KEYS, not five hand-typed literal
# regexes -- so a typo in one of the five cannot silently produce a pattern
# that matches nothing. Matches a full line starting with "## " and ending
# with "[SHARED:<key>]" (trailing whitespace allowed).
_SHARED_MARKER_RE = {
    key: re.compile(r"^## .*\[SHARED:" + re.escape(key) + r"\]\s*$", re.MULTILINE)
    for key in _SHARED_KEYS
}


def _extract_shared_section(text, key):
    """Return the body between the unique '## ' heading line carrying the
    `[SHARED:<key>]` marker and the next '## ' heading line (exclusive),
    with the heading line itself excluded and trailing blank lines
    stripped. Adapted from
    tests/test_config_storage_design_vendored.py's analogous
    section-extraction helper: span-scoping matters because a document
    that merely mentions a marker
    somewhere while silently following it must fail, which a file-wide
    substring search alone would not catch.

    Returns `None` when no `## ` heading line carries the marker -- a
    renamed marker is F-14 mode 4, a refusal rather than a silent empty
    match, and is exactly why the non-vacuity assertion below is a
    separate test per parse.

    Raises `AssertionError` containing the phrase 'refusing to guess' when
    two or more `## ` heading lines carry the same marker -- a parser that
    refuses to guess which one is authoritative rather than silently
    picking the first.
    """
    pattern = _SHARED_MARKER_RE[key]
    matches = list(pattern.finditer(text))
    if len(matches) > 1:
        matched_lines = [m.group(0) for m in matches]
        raise AssertionError(
            f"{len(matches)} heading lines carry the [SHARED:{key}] marker "
            f"in this document: {matched_lines!r} -- refusing to guess "
            "which one is authoritative. A document restructure introduced "
            "a second candidate; resolve which one is real before this "
            "parser can proceed."
        )
    if not matches:
        return None

    lines = text.splitlines()
    match_start = matches[0].start()
    start_line_idx = text.count("\n", 0, match_start)
    end = len(lines)
    for j in range(start_line_idx + 1, len(lines)):
        if lines[j].startswith("## "):
            end = j
            break
    body_lines = lines[start_line_idx + 1 : end]
    while body_lines and body_lines[-1].strip() == "":
        body_lines.pop()
    return "\n".join(body_lines)


def _shared_sections(text):
    """Return a dict mapping each key in _SHARED_KEYS to
    `_extract_shared_section(text, key)`. No filtering, no defaults: a
    missing key maps to None so the non-vacuity legs can see it."""
    return {key: _extract_shared_section(text, key) for key in _SHARED_KEYS}


def _assert_non_vacuous(value, source):
    """Non-vacuity guard (research finding A-7), run BEFORE any value is
    compared: a parse that found nothing (or captured only whitespace) must
    be an AssertionError, never a silent pass -- an empty value would make
    every downstream comparison vacuously true. The exact phrase
    'vacuously true' is load-bearing: the RED tests match on it."""
    assert value is not None and value.strip(), (
        f"parsed value {value!r} from {source} -- a parse that found "
        "nothing (or captured only whitespace) would make every "
        "downstream comparison vacuously true (research finding A-7)."
    )


def _git_hash_object(path: Path) -> str:
    """Resolve `git` fail-closed and hash-object `path`."""
    git_bin = shutil.which("git")
    assert git_bin is not None, (
        "`git` binary not found on PATH. This must FAIL the suite, never "
        "be silently skipped."
    )
    result = subprocess.run(
        [git_bin, "hash-object", str(path)],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def _git_porcelain(path: Path) -> str:
    """Resolve `git` fail-closed and return `git status --porcelain` for
    `path`. Empty output means a clean tree."""
    git_bin = shutil.which("git")
    assert git_bin is not None, (
        "`git` binary not found on PATH. This must FAIL the suite, never "
        "be silently skipped."
    )
    result = subprocess.run(
        [git_bin, "-C", str(path), "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def _run_gate_in_subprocess(env_overrides, node_id=None):
    """Run `[sys.executable, "-m", "pytest", <this module's path>, "-q",
    "-rs"]` (optionally scoped to `node_id`) with `cwd=_FW_REPO_ROOT` and
    `os.environ` merged with `env_overrides`, capturing text output, and
    return the `CompletedProcess`.

    A subprocess is mandatory here because `meta_presence`'s names bind at
    import and `pytest.mark.skipif` binds at collection, so
    `monkeypatch.setenv` has no effect on either.

    Guards against infinite recursion by refusing to run (raising
    `AssertionError`) when the environment variable
    `FIRESTARTER_129_GATE_CHILD` is already set in the CURRENT process, and
    sets that variable in the child's environment. Callers that themselves
    run inside a nested child (i.e. that see the variable already set) must
    check for it and skip BEFORE calling this function, rather than relying
    on this guard alone -- see
    `test_absent_meta_root_skip_is_auditable_not_silent`.
    """
    assert os.environ.get("FIRESTARTER_129_GATE_CHILD") is None, (
        "refusing to spawn a nested gate subprocess -- "
        "FIRESTARTER_129_GATE_CHILD is already set in this process; this "
        "would recurse indefinitely if it were allowed to proceed."
    )
    module_path = str(_HERE / "test_flash_path_record_sync.py")
    target = f"{module_path}::{node_id}" if node_id else module_path
    env = dict(os.environ)
    env.update(env_overrides)
    env["FIRESTARTER_129_GATE_CHILD"] = "1"
    return subprocess.run(
        [sys.executable, "-m", "pytest", target, "-q", "-rs"],
        cwd=str(_FW_REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
    )


def _synthetic_record(bodies):
    """Build a minimal markdown document string with a title line and, for
    each key in _SHARED_KEYS, a '## ' heading line ending in that key's
    marker followed by that key's body from the `bodies` mapping. Used by
    every synthetic fixture in this module so no fixture hand-rolls
    document text."""
    lines = ["# Synthetic Flash-Path Record (test fixture)", ""]
    for key in _SHARED_KEYS:
        lines.append(f"## {key} Heading [SHARED:{key}]")
        lines.append(bodies[key])
        lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Plan 02 additions: the gated literals, needle sets and accessors the
# parity/content class (TestFlashPathRecordSync, below) is built on. Every
# leg still goes through the single _extract_shared_section /
# _shared_sections / _assert_non_vacuous trio above -- no second extractor
# is introduced here (the single-helper rule, PATTERNS S3a).
# ---------------------------------------------------------------------------

_README = _FW_REPO_ROOT / "platform" / "py32f071" / "README.md"

# Three exact literals. Every character matters -- these are what plans
# 129-03/05/06 must reproduce verbatim in the two records. U+2014 EM DASH is
# used wherever an em dash appears, never a double hyphen. Each assertion
# against these constants is a plain substring test, so the records may wrap
# the sentence in `**` bold markers without breaking it.

# PCB-01: the three-tier flash path does not retire the self-flash seed.
_L1_NON_RETIREMENT = (
    "Landing the factory USB DFU path in v1.23 does not retire the "
    "self-flash bootloader seed."
)

# PCB-04: the hard ship gate -- no board ships, no release advertises a USB
# identity, until a real PID is allocated under VID 0x1209 (pid.codes).
_L2_SHIP_GATE = (
    "Ship gate: no PY32F071 board ships, and no release advertises a USB "
    "identity, until a PID allocated under VID 0x1209 exists."
)

# PCB-05: the socket-empty-before-install instruction.
_L3_SOCKET_EMPTY = (
    "Before any PY32F071 firmware install — DFU, SWD or otherwise — "
    "the PROM socket must be empty."
)

# Needle tuples, one module constant per shared section. Each comment names
# its source finding in 129-RESEARCH.md.

# PCB-01, RESEARCH S"Three-Tier Flash Path".
_S1_NEEDLES = (
    "self-flash bootloader",
    "CDC",
    "COBS",
    "factory USB DFU",
    "SWD",
    "intended primary",
    "maintainer/manufacturing recovery",
    "last resort",
)

# PCB-02, F-5/F-8/F-9/F-10/F-11.
_S2_NEEDLES = (
    "PF8",
    "nBOOT1",
    "PA13",
    "PA14",
    "nRST",
    "PB0",
    "PB7",
    "LQFP64",
    "CSP64",
    "QFN64",
    "LQFP48",
    "QFN48",
    "QFN56",
    "QFN32",
    "HSE",
    "PA4",
    "ADC",
    "PA11",
    "PA12",
    "1.5 kΩ",
)

# CONTEXT S"Specifics" -- "the record should state its own edges".
_S2_UNDECIDED_NEEDLES = ("socket", "ZIF", "connector", "power budget")

# PCB-03, F-1/F-3/C-1/C-4.
_S3_NEEDLES = (
    "0x08000000",
    "0x0801DFFF",
    "0x0801E000",
    "0x0801E100",
    "0x08020000",
    "120K",
    "8K",
    "256",
    "8192",
    "Sector 15",
    "__config_page_size",
    "__config_slot_a_start",
    "__config_slot_b_start",
    "__config_region_end",
    "24 KiB",
    "3 sectors",
    "14.6 KiB",
    "27,372",
    "192 B",
    "__VTOR_PRESENT",
    "SCB->VTOR",
)

# The bootloader reservation figure, in either of its two written forms:
# "24" + optional whitespace + "KiB", or "3" + whitespace + optional "whole"
# + whitespace + "sectors". Case-insensitive.
_S3_FIGURE_RE = re.compile(r"24\s*KiB|3\s+(?:whole\s+)?sectors", re.IGNORECASE)

# D-10: at least one of these must appear within a two-line window either
# side of every _S3_FIGURE_RE match, so the figure never appears without its
# migration cost attached.
_S3_COST_TOKENS = ("ORIGIN", "migration", "re-flash")

# PCB-04, C-2/F-6/F-7/F-12/F-17.
_S4_NEEDLES = (
    "0x1209",
    "1209:0001",
    "pid.codes",
    "0x36B7",
    "0xFFFF",
    "Puya Semiconductor",
    "usbd_cdc_if.c",
    "pycdc.inf",
    "0ed2f4b4d3391eccfd4491006a30295fd78e32c2",
    "0x0448",
    "py32_dfu.py",
    "0xFE/0x01",
)

# PCB-05, F-13.
_S5_NEEDLES = (
    "provisional",
    "RURP_PY32F071_PINMAP_PROVISIONAL",
    "direction",
    "BOOT0",
    "three board revisions",
)

# D-11, C-1.
_LINKER_NEEDLES = (
    "FLASH-PATH-AND-PCB.md",
    "v1.23-FLASH-PATH-DECISION.md",
    "__VTOR_PRESENT",
    "SCB->VTOR",
    "BOOTLOADER (rx) : ORIGIN = 0x08000000, LENGTH = 0",
)

# The two-word clause C-1 requires the linker script's BOOTLOADER comment to
# no longer carry: this part declares __VTOR_PRESENT 1 and the compiled
# SystemInit writes SCB->VTOR at every boot (RESEARCH C-1), so "on a part
# with no VTOR" is factually false. The record -- not this repo's
# REQUIREMENTS.md or ROADMAP.md -- is where the correction is stated;
# Phase 130's CLOSE-01 sweep owns that prose.
_LINKER_FORBIDDEN_RE = re.compile(r"no\s+VTOR", re.IGNORECASE)


def _meta_doc() -> Path:
    """Resolve the meta repo's authoritative flash-path record through
    meta_presence.meta_path() -- never a string concatenation onto
    META_ROOT -- so a missing target under a present meta repo raises
    MissingScanTargetError instead of silently skipping."""
    return meta_path(".planning", _META_DOC_REL)


def _fw_doc_text() -> str:
    """Assert the firmware subset record exists (naming the resolved
    absolute path), then return its text. A missing subset must fail the
    suite, never be skipped."""
    assert _FW_DOC.exists(), (
        f"{_FW_DOC} does not exist. This must FAIL the suite, never be "
        "silently skipped."
    )
    return _FW_DOC.read_text()


def _readme_text() -> str:
    """Assert platform/py32f071/README.md exists (naming the resolved
    absolute path), then return its text. A missing README must fail the
    suite, never be skipped."""
    assert _README.exists(), (
        f"{_README} does not exist. This must FAIL the suite, never be "
        "silently skipped."
    )
    return _README.read_text()


def _linker_text() -> str:
    """Assert the PY32F071 linker script exists (naming the resolved
    absolute path), then return its text. A missing linker script must fail
    the suite, never be skipped."""
    assert _LINKER.exists(), (
        f"{_LINKER} does not exist. This must FAIL the suite, never be "
        "silently skipped."
    )
    return _LINKER.read_text()


def _seed_text() -> str:
    """Read the py32f071 no-external-tool-fw-install seed through
    meta_presence.meta_path(), so a missing seed under a present meta repo
    raises MissingScanTargetError instead of silently skipping."""
    return meta_path(".planning", _SEED_REL).read_text()


def _copy_text(copy_id: str) -> str:
    """Dispatch to the text of the named copy: 'meta' -> the authoritative
    record, 'fw' -> the firmware subset, 'readme' -> platform/py32f071's
    README. Any other id is a programmer error, not a test outcome."""
    if copy_id == "meta":
        return _meta_doc().read_text()
    if copy_id == "fw":
        return _fw_doc_text()
    if copy_id == "readme":
        return _readme_text()
    raise AssertionError(
        f"unknown copy_id {copy_id!r} -- expected 'meta', 'fw' or 'readme'"
    )


def _frontmatter(text):
    """Return an ordered dict of the top-level `key: value` pairs in the
    YAML block delimited by the first two lines equal to '---', requiring
    the opening delimiter on line 1. Raises AssertionError containing
    'refusing to guess' when the opening '---' is not line 1 or the closing
    '---' is absent -- D-17's seed format is a fixed four-field schema and
    this parser must not silently guess its shape."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise AssertionError(
            "expected the opening '---' frontmatter delimiter on line 1 -- "
            "refusing to guess where the frontmatter starts."
        )
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        raise AssertionError(
            "no closing '---' frontmatter delimiter found -- refusing to "
            "guess where the frontmatter ends."
        )
    result = {}
    for line in lines[1:end_idx]:
        if not line.strip() or ":" not in line:
            continue
        key, _, value = line.partition(":")
        result[key.strip()] = value.strip()
    return result


# A checklist row header: "- [ ] **R<digit> -- <title>". The Why and
# Breaks-if-omitted lines must begin after EXACTLY two leading spaces.
_ROW_HEADER_RE = re.compile(r"^- \[ \] \*\*R(\d+) — (.+)$")
_ROW_WHY_RE = re.compile(r"^  - \*Why:\*(.{20,})")
_ROW_BREAKS_RE = re.compile(r"^  - \*Breaks if omitted:\*(.{20,})")


def _checklist_rows(body):
    """Return a list of (row_id, title, why_line, breaks_line) tuples
    parsed from `body`'s '- [ ] **R<digit> -- <title>' row headers, each
    required to be followed by its two-space-indented '- *Why:*' and
    '- *Breaks if omitted:*' lines (each carrying at least twenty
    characters of text). Raises AssertionError naming the offending row id
    when the shape is violated.

    D-16: checkbox + one line of rationale + one line of what breaks. The
    shape exists so Phase 130's CLOSE-02 honesty ledger can cite specific
    rows."""
    lines = body.splitlines()
    rows = []
    for i, line in enumerate(lines):
        m = _ROW_HEADER_RE.match(line)
        if not m:
            continue
        row_id = f"R{m.group(1)}"
        title = m.group(2)
        following = [ln for ln in lines[i + 1 :] if ln.strip() != ""]
        if len(following) < 2:
            raise AssertionError(
                f"row {row_id} ({title!r}) is not followed by both its "
                "Why and Breaks-if-omitted lines."
            )
        why_line, breaks_line = following[0], following[1]
        if not _ROW_WHY_RE.match(why_line):
            raise AssertionError(
                f"row {row_id} ({title!r})'s Why line does not match the "
                f"required '  - *Why:*<20+ chars>' shape. Got: {why_line!r}"
            )
        if not _ROW_BREAKS_RE.match(breaks_line):
            raise AssertionError(
                f"row {row_id} ({title!r})'s Breaks-if-omitted line does "
                "not match the required '  - *Breaks if omitted:*<20+ "
                f"chars>' shape. Got: {breaks_line!r}"
            )
        rows.append((row_id, title, why_line, breaks_line))
    return rows


class TestFlashPathRecordSyncFailsClosed:
    """The pure RED demonstrations: none carries `@requires_meta`, none
    needs either real record to exist. These are the legs that make this
    gate a gate rather than a comment."""

    def test_absent_meta_root_skip_is_auditable_not_silent(self, tmp_path):
        """Coverage 1 -- F-14 mode 3. Point a subprocess's
        `FIRESTARTER_META_ROOT` at an empty tmp_path directory (no `.git`)
        and assert the run exits 0, reports a skip, names the resolved
        absent marker path, and never reports a failure.

        This test targets ONLY ITSELF as the subprocess's node id, so no
        other test in this module (some of which assume the real,
        present meta root) runs inside the child. The child re-enters this
        same function; the `FIRESTARTER_129_GATE_CHILD` check below fires
        on that second entry and turns it into the very skip this test is
        proving is auditable -- its reason is the child's own
        `META_ABSENT_REASON`, which names the resolved (absent) marker
        path, because that name is bound fresh in the child's own process
        from the overridden environment, not inherited via monkeypatch.
        """
        if os.environ.get("FIRESTARTER_129_GATE_CHILD"):
            pytest.skip(META_ABSENT_REASON)
            return

        empty_root = tmp_path / "empty-meta-root"
        empty_root.mkdir()
        result = _run_gate_in_subprocess(
            {"FIRESTARTER_META_ROOT": str(empty_root)},
            node_id=(
                "TestFlashPathRecordSyncFailsClosed::"
                "test_absent_meta_root_skip_is_auditable_not_silent"
            ),
        )
        output = result.stdout + result.stderr
        assert result.returncode == 0, (
            f"expected exit 0 from the absent-meta-root subprocess run, "
            f"got {result.returncode}. Output:\n{output}"
        )
        assert "skipped" in output, (
            f"expected the subprocess output to report a skip -- an "
            f"absent meta root must be auditable, never silent. "
            f"Output:\n{output}"
        )
        expected_marker = str(empty_root / ".git")
        assert expected_marker in output, (
            f"expected the subprocess output to name the resolved absent "
            f"marker path {expected_marker!r} so the skip claim is "
            f"auditable. Output:\n{output}"
        )
        assert "failed" not in output, (
            f"expected no failure in the absent-meta-root subprocess run. "
            f"Output:\n{output}"
        )

    def test_absent_meta_claim_can_never_be_false(self):
        """Coverage 2 -- the census assertion, in-process against this
        process's own already-imported, real bindings: if
        `META_MARKER.exists()` then `META_PRESENT` must be `True`, and
        `str(META_MARKER)` must be a substring of `META_ABSENT_REASON`. A
        skip claiming the meta checkout is absent while its marker exists
        is the A-7 shape and must be impossible by construction."""
        if META_MARKER.exists():
            assert META_PRESENT is True, (
                f"{META_MARKER} exists but META_PRESENT is False -- an "
                "absent claim while the marker exists would be a false "
                "skip (research finding A-7's exact shape)."
            )
        assert str(META_MARKER) in META_ABSENT_REASON, (
            f"expected the resolved marker path {str(META_MARKER)!r} to be "
            f"a substring of META_ABSENT_REASON {META_ABSENT_REASON!r} so "
            "any skip claiming absence is auditable against what was "
            "actually resolved."
        )

    def test_present_root_with_missing_target_raises_not_skips(self):
        """Coverage 3 -- F-14 mode 3's hard half. Under the real present
        meta root, a missing scan target raises `MissingScanTargetError`
        rather than ever being downgraded to a skip. The filename is
        deliberately one that will never exist so this leg is stable
        across every later wave that adds real files under `.planning/`."""
        assert META_PRESENT, (
            "this leg assumes the real meta root is present in this "
            "devcontainer checkout -- the whole phase's premise (a "
            "submodule checkout under a meta repo) does not hold otherwise."
        )
        with pytest.raises(MissingScanTargetError) as exc_info:
            meta_path(".planning", "__definitely_not_a_real_file__.md")
        message = str(exc_info.value)
        expected_path = META_ROOT / ".planning" / "__definitely_not_a_real_file__.md"
        assert str(expected_path) in message, (
            f"expected the MissingScanTargetError message to name the "
            f"resolved absolute path {str(expected_path)!r}. Got: "
            f"{message!r}"
        )
        assert "update" in message, (
            f"expected the MissingScanTargetError message to instruct the "
            f"reader to update the path rather than deleting the gate. "
            f"Got: {message!r}"
        )

    def test_marker_name_is_not_overridable(self):
        """Coverage 4. Reads `tests/meta_presence.py`'s own source and
        asserts `os.environ` appears exactly once, that
        `FIRESTARTER_META_ROOT` appears, and that no other
        `FIRESTARTER_META_` identifier appears -- the seam overrides the
        root only, never the marker name."""
        source = (_FW_REPO_ROOT / "tests" / "meta_presence.py").read_text()
        assert source.count("os.environ") == 1, (
            "expected exactly one os.environ read in meta_presence.py -- "
            "the seam overrides the root only."
        )
        assert "FIRESTARTER_META_ROOT" in source
        assert "FIRESTARTER_META_MARKER" not in source, (
            "the marker name must never be overridable -- one more knob "
            "that can be set wrong in a real run."
        )

    def test_empty_extraction_is_not_a_vacuous_pass(self):
        """Coverage 5 -- F-14 mode 2. A synthetic document with no markers
        at all maps every key to None, and the non-vacuity guard raises on
        both a None parse and a whitespace-only one, naming
        'vacuously true' both times."""
        text = "# Title\n\nSome unrelated prose with no shared markers.\n"
        sections = _shared_sections(text)
        for key in _SHARED_KEYS:
            assert sections[key] is None, (
                f"expected key {key!r} to extract to None from a "
                f"marker-free document, got {sections[key]!r}"
            )
        with pytest.raises(AssertionError, match="vacuously true"):
            _assert_non_vacuous(None, "synthetic marker-free document")
        with pytest.raises(AssertionError, match="vacuously true"):
            _assert_non_vacuous("   \n", "synthetic whitespace-only body")

    def test_renamed_marker_yields_a_refusal_not_a_guess(self):
        """Coverage 6 -- F-14 mode 4. Mutating S3's marker to
        `[SHARED:S3x]` makes S3 extract to None while the other four keys
        still extract non-empty bodies, and the non-vacuity guard raises
        on the S3 result."""
        original = _synthetic_record(
            {key: f"Body text for {key}." for key in _SHARED_KEYS}
        )
        mutated = original.replace("[SHARED:S3]", "[SHARED:S3x]")
        assert mutated != original, (
            "planted mutation did not actually change the text -- the "
            "replacement target '[SHARED:S3]' was not found."
        )
        sections = _shared_sections(mutated)
        assert sections["S3"] is None, (
            f"expected the renamed S3 marker to extract to None, got "
            f"{sections['S3']!r}"
        )
        for key in ("S1", "S2", "S4", "S5"):
            assert sections[key], (
                f"expected key {key!r} to still extract a non-empty body "
                f"after only S3 was renamed, got {sections[key]!r}"
            )
        with pytest.raises(AssertionError, match="vacuously true"):
            _assert_non_vacuous(sections["S3"], "mutated synthetic document, key S3")

    def test_duplicate_marker_refuses_to_guess(self):
        """Coverage 7. Two '## ' heading lines both ending in
        `[SHARED:S2]` make the extractor refuse to guess rather than
        silently picking one."""
        text = (
            "# Title\n\n"
            "## First S2 Heading [SHARED:S2]\n"
            "First body.\n\n"
            "## Second S2 Heading [SHARED:S2]\n"
            "Second body.\n"
        )
        with pytest.raises(AssertionError, match="refusing to guess"):
            _extract_shared_section(text, "S2")

    def test_planted_divergence_in_synthetic_copies_is_detected(self):
        """Coverage 8 -- F-14 mode 1. Two synthetic documents built from
        identical bodies extract equal; mutating one copy's S3 body makes
        the two compare unequal, located in S3 specifically, not merely
        somewhere."""
        bodies = {key: f"Shared body text for {key}." for key in _SHARED_KEYS}
        doc_a = _synthetic_record(bodies)
        doc_b = _synthetic_record(bodies)
        sections_a = _shared_sections(doc_a)
        sections_b = _shared_sections(doc_b)
        assert sections_a == sections_b, (
            "expected two synthetic documents built from identical bodies "
            "to extract identically."
        )

        mutated_bodies = dict(bodies)
        mutated_bodies["S3"] = bodies["S3"] + " MUTATED."
        assert mutated_bodies["S3"] != bodies["S3"], (
            "planted mutation did not actually change the S3 body."
        )
        doc_c = _synthetic_record(mutated_bodies)
        sections_c = _shared_sections(doc_c)

        assert sections_a != sections_c, (
            "expected the mutated copy to compare unequal to the original."
        )
        diverging_keys = [k for k in _SHARED_KEYS if sections_a[k] != sections_c[k]]
        assert diverging_keys == ["S3"], (
            f"expected the divergence to be located in S3 specifically, "
            f"got {diverging_keys!r}"
        )

    def test_dirty_tree_is_detected(self, tmp_path):
        """Coverage 9 -- F-14 mode 5. A throwaway git repo under tmp_path
        with an untracked file reports non-empty porcelain; calling
        `_git_porcelain` against the real firmware repo must not raise
        (its cleanliness is not asserted here -- a mid-plan working tree
        is legitimately dirty)."""
        git_bin = shutil.which("git")
        assert git_bin is not None
        repo = tmp_path / "throwaway-repo"
        repo.mkdir()
        subprocess.run(
            [git_bin, "init"],
            cwd=str(repo),
            capture_output=True,
            text=True,
            check=True,
        )
        subprocess.run(
            [
                git_bin,
                "-c",
                "user.email=test@example.com",
                "-c",
                "user.name=Test",
                "commit",
                "--allow-empty",
                "-m",
                "empty",
            ],
            cwd=str(repo),
            capture_output=True,
            text=True,
            check=True,
        )
        (repo / "untracked.txt").write_text("untracked content\n")

        porcelain = _git_porcelain(repo)
        assert porcelain, (
            "expected a non-empty porcelain status for a repo with an "
            "untracked file."
        )

        real_porcelain = _git_porcelain(_FW_REPO_ROOT)
        assert isinstance(real_porcelain, str), (
            "calling _git_porcelain against the real firmware repo must "
            "not raise."
        )

    def test_git_binary_is_required_not_optional(self):
        """Coverage 10. `git` must be present and required -- reads this
        module's own source to assert the first `shutil.which("git")`
        call is followed closely by an `assert`, so a future edit cannot
        silently convert it into a skip."""
        assert shutil.which("git") is not None, (
            "`git` binary not found on PATH. This must FAIL the suite, "
            "never be silently skipped."
        )
        own_source = Path(__file__).read_text()
        which_git = 'shutil.which("git")'
        idx = own_source.find(which_git)
        assert idx != -1, (
            f"expected at least one {which_git} call in this module."
        )
        window = own_source[idx : idx + 200]
        assert "assert" in window, (
            f"expected an `assert` to follow {which_git} closely so a "
            "missing binary fails the suite rather than silently "
            "degrading."
        )
