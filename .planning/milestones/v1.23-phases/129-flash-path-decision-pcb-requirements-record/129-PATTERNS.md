# Phase 129: Flash-Path Decision & PCB Requirements Record — Pattern Map

**Mapped:** 2026-08-02
**Files analyzed:** 7 (5 new, 2 modified)
**Analogs found:** 7 / 7

This document does **not** re-derive RESEARCH.md's F-14 (where the gate can live / how it fails
open), F-15 (document-shape precedent), or §"Architecture Patterns" 1–3. Those are prose
conclusions and stand. What follows is the layer research did not produce: **verbatim excerpts
from the analog files**, so the executor copies real structure rather than a description of it.

Repo scope: meta (`.planning/`) + `firestarter` only. `firestarter_app` is **read-only** (D-04) —
it appears below solely as a source of analog code.

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `.planning/v1.23-FLASH-PATH-DECISION.md` *(name is planner's call)* — **new** | doc / decision record (authoritative layer) | transform (facts → citable record) | `.planning/v1.9-COBS-DECISION.md` (section skeleton + claim tags); `.planning/v1.7-SHIELD-REVS.md` (layering) | exact |
| `firestarter/platform/py32f071/FLASH-PATH-AND-PCB.md` *(name is planner's call)* — **new** | doc / design record (subset layer) | transform | `firestarter/platform/py32f071/CONFIG-STORAGE.md` | exact |
| `firestarter/tests/test_flash_path_record_sync.py` — **new** | test (cross-repo parity gate) | file-I/O + parse/compare | `firestarter_app/tests/test_py32_asset_name_host.py` (check direction, non-vacuity, planted RED, porcelain guard); `firestarter/tests/test_config_storage_design_vendored.py` (same repo, path idiom, no-CI disposition, single-helper rule) | exact (two complementary analogs) |
| `firestarter/tests/meta_presence.py` — **new** | utility (presence probe, imported by the gate) | config/env resolution | `firestarter_app/tests/fw_presence.py` | exact |
| `firestarter/platform/py32f071/linker/PY32F071xB_FLASH.ld` — **modified** (comment only, D-11 + C-1) | config / linker script | n/a | the file itself (lines 10–20) | self |
| `.planning/seeds/py32f071-no-external-tool-fw-install.md` — **modified** (frontmatter, D-17) | doc / seed | n/a | the file itself (lines 1–6) | self |
| `.planning/phases/129-…/129-NONREGRESSION.md` — **new** | doc / evidence sweep | transform | `128-NONREGRESSION.md` (closest: publication-only claim ceiling), `126-NONREGRESSION.md` (criterion-by-criterion shape) | exact |

**Not modified this phase (recorded so no plan drifts into them):**
`firestarter/platform/py32f071/src/usb_cdc.c` (D-06), anything under `firestarter_app/` (D-04),
`REQUIREMENTS.md` / `ROADMAP.md` prose (CLOSE-01 owns the C-1/C-2 wording sweep).

---

## Pattern Assignments

### 1. `.planning/v1.23-FLASH-PATH-DECISION.md` (doc, authoritative layer)

**Analog A — `.planning/v1.9-COBS-DECISION.md`** (section skeleton; the closest ADR-shaped
precedent). Its complete heading tree, measured:

```
# v1.9 COBS Decision — Serial Robustness Framing Evaluation      (line 1)
## 1. Context                                                     (10)
### 1.1 The Serial Data Path (4 framings, one 250000-baud line)   (12)
### 1.2 The Resync Motivation                                     (30)
### 1.3 Uno RAM Baseline (re-measured 2026-06-01) [VERIFIED]      (43)
### 1.4 The SERIAL_ON_IO `0x00` Bus-Aliasing Risk (Uno only) [VERIFIED]  (57)
### 1.5 CRC8-CCITT Integrity Layer [VERIFIED]                     (83)
## 2. Decision                                                    (98)
### 2.0 Revision Note (2026-06-01) — why DEFER became ADOPT       (108)
### Rationale summary                                             (131)
## 3. Consequences                                                (152)
### What stays the same                                           (154)
### Future path if auto-resync becomes necessary                  (162)
## 4. Candidate Survey                                            (198)
### 4.1 … 4.7  (one subsection per rejected option)               (204–400)
### Comparative Verdict Table                                     (400)
## 5. Open Questions for Future Milestone                         (427)
```

Two things to copy literally:

1. **The confidence tag goes in the heading**, not only in the body — `### 1.3 Uno RAM Baseline
   (re-measured 2026-06-01) [VERIFIED]`. RESEARCH F-15 counted 12 `[VERIFIED…]`, 1 `[CITED: …]`,
   1 `[ASSUMED — …]` across the four precedent docs. Add `[UNVERIFIED-UNTIL-SILICON]` as the
   fifth tag.
2. **A `Revision Note` subsection under `## 2. Decision`** is the established place to record a
   position that changed. This is where C-1 ("has a VTOR") and C-2 ("`0x36B7` is Puya's, not
   unallocated") belong — the doc's own precedent already has a slot for "why X became Y".

**Analog B — `.planning/v1.7-SHIELD-REVS.md`** (the D-01 layering pattern; header block, lines 1–7):

```markdown
# v1.7 SHIELD REVS — Authoritative RURP Shield Revision Reference

**Milestone:** v1.7 RURP Shield Hardware Investigation & Version Detection
**Source upstream:** `https://github.com/…` (cloned to `.planning/v1.7/upstream-rurp/`, gitignored)
**Cross-phase accretion:** Phase 31 (inventory …) → Phase 32 (…) → Phase 35 (close)
**Schema:** D-10 9-column inventory schema is locked across all v1.7 phases.

## Summary
```

Note `**Milestone:**` + a `## Summary` immediately after the metadata block. Its value here is the
*layering*, not the section list (F-15) — see the reciprocal excerpt in §2 below.

---

### 2. `firestarter/platform/py32f071/FLASH-PATH-AND-PCB.md` (doc, subset layer)

**Analog — `firestarter/platform/py32f071/CONFIG-STORAGE.md`** (Phase 126, single-file commit in
exactly this directory).

**Opening, lines 1–3 — copy this form verbatim:**

```markdown
# PY32F071 Flash-Persistent Configuration — Design Record

**Phase 126 Plan 01. Requirements: CFG-01, CFG-02.**
```

→ Phase 129's is `# PY32F071 Flash Path & PCB Requirements — Design Record` /
`**Phase 129 Plan NN. Requirements: PCB-01, PCB-02, PCB-03, PCB-04, PCB-05.**`

**Closing, lines 275–284 — the `## Claim ceiling` section, which defers by reference:**

```markdown
## Claim ceiling

No PY32F071 hardware exists as a physical board. Nothing recorded in this document is a claim
about behaviour observed on that silicon; every figure above is either quoted from the reference
manual, corroborated from the pinned SDK's own header, or derived from source already in this
tree. Any ARM build evidence this milestone produces is a CI workflow run URL plus a head SHA,
never a local build — `arm-none-eabi-gcc`, `cmake` and `ninja` are absent from this environment.
The full list of claims this milestone may and may not make is recorded once, in
`.planning/REQUIREMENTS.md` §"Validation Ceiling"; this document defers to that list by reference
rather than restating its wording.
```

⚠ **Do not copy sentence 3 verbatim.** RESEARCH C-3 executed a local ARM build successfully in
this devcontainer, and D-13 *requires* one. Copy the shape (blanket ceiling + defer-by-reference
to `REQUIREMENTS.md` §"Validation Ceiling") and re-word the toolchain sentence to a
delta-claims-only statement. The ceiling-wording correction itself belongs to Phase 130 CLOSE-01.

**Heading shape** (topic sections, no numbering — contrast with the meta layer's numbered ADR
sections): `## Configuration storage (vendored, in scope)` · `## SUPERSEDED by …` ·
`## Out of scope` · `## Flash geometry` · `## Reserved flash map` · `## Amendment to D-16 …` ·
`## CONFIG_MAGIC` · … · `## Host contract` · `## Claim ceiling`.

**The reciprocal pointer** — how a subset doc names its authoritative parent. From
`firestarter/doc/SHIELD-REVISIONS.md` (the v1.7 sub-repo subset), closing paragraph:

```markdown
Full investigation history (git mine, inter-rev electrical/mechanical deltas,
detect-HW schematic narrative, bench measurement evidence): see
`.planning/v1.7-SHIELD-REVS.md` in the Firestarter meta-repo (sections §2
through §5 and §8 — operator does not need these for normal use).
```

Its opening also does reader-routing (`If you have a shield in hand and want to know "…", read
§1 + §2`), which suits a schematic author working from the checklist.

**The sync-obligation note** goes in *both* sub-repo `CLAUDE.md` files in the v1.7 precedent;
`firestarter/CLAUDE.md` §"Hardware Revision Documentation" is the exact analog sentence:

> "…is a subset clone of the Firestarter meta-repo investigation document at
> `.planning/v1.7-SHIELD-REVS.md`. It contains the inventory (§1), … If any of those sections
> changes in the meta-repo, update the sub-repo doc in lockstep (Phase 35 / v1.7 — close)."

Phase 129 additionally has a machine gate (D-03), which v1.7 did not — so the note should say
"enforced by `tests/test_flash_path_record_sync.py`", not "update in lockstep" alone.

---

### 3. `firestarter/tests/test_flash_path_record_sync.py` (test, cross-repo parity gate)

Two analogs. **Take the module docstring + path idiom from the same-repo one; take the assertion
architecture from the app-repo one.**

#### 3a. Same-repo shape — `firestarter/tests/test_config_storage_design_vendored.py`

**Module docstring, lines 1–35 (the three paragraphs an executor must reproduce):**

```python
"""
Project Name: Firestarter
Copyright (c) 2024 Henrik Olsson

Permission is hereby granted under MIT license.

Phase 126 Plan 01 -- CFG-01's mechanical gate over
platform/py32f071/CONFIG-STORAGE.md, the in-scope flash-config design
vendored from closed-PR blob 4b1a441, plus a first mechanical check on
CFG-02's flash-geometry record.

Requirements: CFG-01, CFG-02
Decisions covered: D-01, D-13, D-16, D-17, D-18, D-19

This module executes in NO CI leg on this branch: `pytest tests/ -v` runs
only in build.yml (push/PR to main) and beta-build.yml (push to beta) --
neither fires on this firmware milestone branch, and py32f071.yml has no
pytest step at all. The local run recorded in this phase's evidence
artifact is the only evidence this module's assertions were ever
exercised.

Self-contained path resolution below -- NOT in conftest.py (firestarter/
tests/ has no conftest.py anywhere in the repo, and none of pytest.ini,
pyproject.toml, setup.cfg or tox.ini exist either; a recorded house-rule
pattern, not an omission, per tests/test_vpp_seam_manual_on_every_board.py's
own docstring). Stdlib and pytest only -- no third-party import, no
PlatformIO import, nothing under .pio/, because a dependency on
.pio/libdeps/ passes on a warm tree and fails on a clean checkout (the
fail-open shape this milestone has already paid for once, A-7).

All nine test functions below are built on ONE module-level helper,
_find_design_doc_violations(text), so the positive tests and the
planted-violation RED demonstration (Coverage 8) exercise the same
checking code rather than a second, parallel implementation that could
silently drift from what the positive tests actually check.
"""
```

Then a numbered `Coverage:` block, one line per test, naming the test function.

**The no-conftest path idiom, lines 68–74 — copy exactly:**

```python
from pathlib import Path

import pytest  # noqa: F401 -- imported for parity with the house convention; no fixtures of its own are used beyond tmp_path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
_DOC_PATH = _REPO_ROOT / "platform" / "py32f071" / "CONFIG-STORAGE.md"
```

**The section extractor, lines 104–125 — reuse it; do not write a second one:**

```python
def _extract_section(text, heading_prefix):
    """Return the text spanning from the line starting with heading_prefix
    up to (but not including) the next top-level '## ' heading, or None if
    heading_prefix is not found as a heading line. This is what makes the
    SUPERSEDED check section-scoped rather than a file-wide substring
    search -- a document that merely mentions the seven module names
    somewhere while silently following them must fail, which a file-wide
    search alone would not catch."""
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.startswith(heading_prefix):
            start = i
            break
    if start is None:
        return None
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("## ") and not lines[j].startswith(heading_prefix):
            end = j
            break
    return "\n".join(lines[start:end])
```

Note it returns `None` on a renamed heading — that is F-14 failure mode 4, and it is exactly why
the non-vacuity assertion in 3b must be a **separate test per parse**.

**Needle-tuple convention, lines 76–94** — module-level constants naming the requirement that
demands them:

```python
_GEOMETRY_NEEDLES = ("256", "8192", "§4.1", "§4.2.1", "Table 4-1", "0ed2f4b4")
_RESERVED_MAP_NEEDLES = ("0x0801E000", "0x0801E100", "120K", "8K", "256")
```

**Single-helper rule, line 128:** every test — positive and RED — calls one module-level
`_find_..._violations(text)`. Two parallel implementations drift and the RED then proves nothing.

#### 3b. Assertion architecture — `firestarter_app/tests/test_py32_asset_name_host.py` (Phase 128, `cc9452f`)

**The non-vacuity guard, lines 148–159 — the `vacuously true` phrase is load-bearing, the RED
tests match on it:**

```python
def _assert_non_vacuous_name(value: str, source: str) -> None:
    """Non-vacuity guard (research finding A-7), run BEFORE any value is
    compared: a parse that found nothing (or captured whitespace) must be an
    `AssertionError`, never a silent pass -- an empty (or shape-invalid)
    value would make every downstream comparison VACUOUSLY TRUE. The exact
    phrase `vacuously true` is load-bearing: the RED tests match on it."""
    assert value and _NAME_SHAPE_RE.match(value), (
        f"parsed value {value!r} from {source} -- expected a name matching "
        f"^firestarter_[a-z0-9_]+\\.hex$. A parse that found nothing (or "
        "captured whitespace) would make every downstream comparison "
        "vacuously true (research finding A-7)."
    )
```

**A parser that refuses to guess, lines 135–145 — the shape for "two candidate section spans":**

```python
    matches = re.findall(r"\bEXPECTED=(firestarter_[A-Za-z0-9_]*\.hex)\b", text)
    distinct = sorted(set(matches))
    if len(distinct) > 1:
        raise AssertionError(
            f"workflow parse found {len(distinct)} distinct "
            f"firestarter_*.hex EXPECTED= candidates: {distinct!r} -- "
            "refusing to guess which one binds REL-04. A workflow "
            "restructure introduced a second candidate; resolve which one "
            "is the real transcription before this parser can proceed."
        )
    return distinct[0] if distinct else ""
```

**The git helpers, lines 162–192 — `git` resolved fail-closed, never skipped:**

```python
def _git_hash_object(path: Path) -> str:
    """Resolve `git` fail-closed and hash-object `path` inside FW_ROOT."""
    git_bin = shutil.which("git")
    assert git_bin is not None, (
        "`git` binary not found on PATH. This must FAIL the suite, never "
        "be silently skipped."
    )
    result = subprocess.run(
        [git_bin, "-C", str(FW_ROOT), "hash-object", str(path)],
        capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()


def _git_porcelain(path: Path) -> str:
    """Resolve `git` fail-closed and return `git status --porcelain` for
    `path`. Empty output means a clean tree (D-19 / F-16's precondition)."""
    ...
    result = subprocess.run(
        [git_bin, "-C", str(path), "status", "--porcelain"],
        capture_output=True, text=True, check=True,
    )
    return result.stdout
```

**The planted-mutation RED, lines 265–326 — the full ceremony (capture path BEFORE monkeypatch;
hash before; assert the replacement actually changed something; write under `tmp_path`;
`monkeypatch.setattr` the module's own constant; assert parity now fails; assert blob SHA
unchanged; assert porcelain clean):**

```python
        real_path = _CMAKELISTS  # captured BEFORE any monkeypatch
        before_blob = _git_hash_object(real_path)
        real_text = real_path.read_text()

        mutated_text = real_text.replace(
            'set(HEX_FILE "${CMAKE_CURRENT_BINARY_DIR}/firestarter_py32f071.hex")',
            'set(HEX_FILE "${CMAKE_CURRENT_BINARY_DIR}/firestarter_mutated999.hex")',
        )
        assert mutated_text != real_text, (
            "planted mutation did not actually differ from the real text "
            "-- the replacement target string was not found (the real "
            "CMakeLists.txt's formatting may have changed)"
        )

        planted_path = tmp_path / "planted-CMakeLists.txt"
        planted_path.write_text(mutated_text)
        monkeypatch.setattr(sys.modules[__name__], "_CMAKELISTS", planted_path)

        cmake_name = _parse_emitted_hex_name(_CMAKELISTS.read_text())
        ...
        assert cmake_name != workflow_name, (
            "expected the planted mutation to break parity, but "
            f"{cmake_name!r} == {workflow_name!r}"
        )

        after_blob = _git_hash_object(real_path)
        assert after_blob == before_blob, (
            "the planted mutation touched the REAL CMakeLists.txt -- it "
            "must only ever be written under tmp_path"
        )
        assert _git_porcelain(FW_ROOT) == "", (
            "the firmware repo's working tree is no longer clean after the "
            "planted-copy test -- it is a read-only input to this phase"
        )
```

The `assert mutated_text != real_text` line is the part most often dropped and is what stops the
RED from passing when the replacement target string no longer exists.

**The two-class split, lines 195–198 and 329–332** — one class for legs needing the sibling repo,
one for the pure REDs that need nothing:

```python
class TestPy32AssetNameParity:
    """D-09's live legs. Every method carries `@requires_fw`. Every method
    re-reads and re-parses (no caching across tests) and calls the
    non-vacuity guard before comparing anything."""

class TestPy32AssetNameFailsClosedOnBadInput:
    """The pure RED demonstrations (D-09). None carries `@requires_fw` --
    these need no firmware sibling and are therefore the only legs of this
    module that actually run in app CI (F-8)."""
```

**The honest CI-ceiling paragraph, lines 67–72 — copy the *form*, substitute the 129 facts:**

```
F-8 ceiling, stated plainly: neither app CI workflow
(`.github/workflows/ci.yml`, `beta-release.yml`) checks out the firmware
sibling, so every `@requires_fw` leg in this module SKIPS in app CI -- only
tests 7-10 above actually run there. This binding is enforced by a local run
(observed PASS-not-SKIP, per T-128-23/A-7) and by developer discipline, NOT
by app CI. Claiming CI enforcement would be false.
```

**Two mechanical notes for the planner, measured in the firmware repo:**

- `firestarter/tests/__init__.py` exists, but **no existing firmware test module imports a
  sibling helper** — `from tests.meta_presence import …` would be the first. Every current module
  self-resolves with `Path(__file__).resolve().parent`. The plan should either verify the package
  import resolves under `pytest tests/ -v` from the repo root, or have the gate import via the
  same `_HERE`-relative idiom. Do not add a `conftest.py` to make it work.
- `tests/test_checker_convention.py` globs `check_*.py` in `firestarter/scripts/` **only,
  non-recursively**. A pytest module (not a `check_*.py` script) is therefore *not* auto-covered
  by BASE-08's meta-test — the planted-violation fixture obligation here is satisfied in-module,
  as `test_config_storage_design_vendored.py` Coverage 8 does, not by adding a script.

---

### 4. `firestarter/tests/meta_presence.py` (utility, presence probe)

**Analog — `firestarter_app/tests/fw_presence.py`** (140 lines). Mirror all four load-bearing
parts. Excerpts verbatim:

**The env seam + unrenameable marker, lines 65–102:**

```python
# The one seam: only the ROOT path is overridable, never the marker name.
# ...
# Making the marker name overridable too would be one more knob that can be
# set wrong in a real run.
_APP_REPO_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_FW_ROOT = _APP_REPO_ROOT.parent / "firestarter"

FW_ROOT: Path = Path(os.environ.get("FIRESTARTER_FW_ROOT", str(_DEFAULT_FW_ROOT)))

# The repo-presence marker. A worktree or submodule checkout stores `.git`
# as a FILE, not a directory ... -- so this probes existence, never `.is_dir()`.
FW_REPO_MARKER: Path = FW_ROOT / ".git"

FW_REPO_PRESENT: bool = FW_REPO_MARKER.exists()

# ONE canonical reason string, shared by every caller.
FW_ABSENT_REASON: str = (
    f"firestarter firmware checkout absent (no {FW_REPO_MARKER} marker)"
)

requires_fw = pytest.mark.skipif(not FW_REPO_PRESENT, reason=FW_ABSENT_REASON)
```

→ 129 substitution: `_FW_REPO_ROOT = Path(__file__).resolve().parent.parent`;
`_DEFAULT_META_ROOT = _FW_REPO_ROOT.parent`; `FIRESTARTER_META_ROOT` env var;
`META_MARKER = META_ROOT / ".git"`; `requires_meta`.
**`.git` existence-not-`is_dir()` matters more here than in the analog** — the firmware repo is a
*submodule of* the meta repo, so the relationship is parent-not-sibling, and the superproject's
`.git` is a real directory while a submodule checkout's is a file. Probe existence only.

**`MissingScanTargetError`, lines 105–114 — raise, never skip:**

```python
class MissingScanTargetError(Exception):
    """Raised when the firmware repo IS present but a named path under it
    is not.

    This is the hard-failure half of the BASE-02 split: under a present
    repo, a missing scan target means the scan target (or the D-11 scan-path
    inventory) needs to be updated to match a real rename -- it must never
    be silently downgraded to a skip, because that is exactly the fail-open
    behaviour A-7 measured and this milestone exists to remove.
    """
```

**The accessor, lines 117–140 — raises only when the repo is present:**

```python
def fw_path(*parts: str) -> Path:
    """...
    - If the firmware repo is present (`FW_REPO_PRESENT`) and the resulting
      path does not exist, raises `MissingScanTargetError` naming the
      resolved absolute path, the repo marker that proved the repo present,
      and the instruction to update the path ... rather than deleting the gate.
    - If the firmware repo is absent, returns the path WITHOUT raising: the
      caller is expected to be behind `requires_fw` ... already, and raising
      here too would turn an honest skip into a collection-time error.
    """
    resolved = FW_ROOT.joinpath(*parts)
    if FW_REPO_PRESENT and not resolved.exists():
        raise MissingScanTargetError(
            f"{resolved} does not exist, but the firmware repo IS present "
            f"(marker found at {FW_REPO_MARKER}). This scan target was "
            "renamed or moved -- update this path (or the cross-repo "
            "scan-path inventory) rather than removing or bypassing this "
            "gate."
        )
    return resolved
```

**The import-binding trap, docstring lines 35–45 — reproduce this warning in the new module:**

```
**Import-time binding -- read this before writing a test against this
module.** `FW_ROOT`, `FW_REPO_MARKER`, `FW_REPO_PRESENT`, `FW_ABSENT_REASON`
and `requires_fw` are all evaluated once, at import (the `FIRESTARTER_FW_ROOT`
env seam below is read at module scope, and `pytest.mark.skipif`
binds at collection). `monkeypatch.setenv` runs *after* import and
collection have already happened, so it has **no effect** on any of these
names. A test that needs a different `FW_ROOT` must invoke pytest (or a
checker script) in a **subprocess**, with `FIRESTARTER_FW_ROOT` set in the
child process's environment -- never an in-process monkeypatch ...
```

This is precisely how F-14 failure mode 3 gets fixtured: a **subprocess** pytest invocation with
`FIRESTARTER_META_ROOT` pointed at an empty directory, plus a present-root-missing-target case
asserting `MissingScanTargetError`.

**Name-collision note worth mirroring** (analog docstring lines 47–55): the app module warns that
`firestarter/` means two different things. The 129 equivalent hazard is the reverse direction —
from inside the firmware repo, `../.planning` is the *superproject*, and under
`actions/checkout` of `henols/firestarter` it does not exist at all. State it in the docstring.

---

### 5. `firestarter/platform/py32f071/linker/PY32F071xB_FLASH.ld` (config, comment-only)

**Analog: the file itself.** The `BOOTLOADER` block, lines 10–20, **verbatim as it stands today**
— this is the text D-11 edits and C-1 corrects:

```
    /* D-13 -- NAMED SEAM ONLY, ZERO LENGTH, for Phase 129 (PCB-03/FUT-N05) to cite.
     *
     * READ THIS BEFORE GIVING IT A SIZE. Unlike the CONFIG region below -- which
     * sits at the TOP of flash and can grow downward without moving anything --
     * giving BOOTLOADER a non-zero length MOVES the application's ORIGIN. That is
     * a flash-map MIGRATION, not a resize: every previously flashed unit's vector
     * table address changes, on a part with no VTOR. Phase 129 must record the
     * bootloader budget as an INTENT WITH THAT COST ATTACHED, never as a number
     * that looks already paid for.
     */
    BOOTLOADER (rx) : ORIGIN = 0x08000000, LENGTH = 0
```

Two comment conventions this file uses that the edit must preserve:

- **Every comment names the decision that owns it** (`D-13`, `D-10`, `D-18`, `CFG-06`) — e.g.
  line 22: `/* Shrunk from 128K so .text/.rodata physically CANNOT reach CONFIG (D-10). ... */`
- **Cross-references are by path + section, not by prose**, as in lines 3–7:
  ```
  /* Flash map. Geometry is NOT guessed here -- see platform/py32f071/CONFIG-STORAGE.md
   * §"Flash geometry": Puya PY32F07X Reference Manual V0.2 §4.1/§4.2.1/Table 4-1,
   * page = 256 B, sector = 8192 B, main flash 0x08000000..0x0801FFFF (128 KiB).
   * That record landed in a commit PRECEDING this file's first edit (CFG-02).
   */
  ```
  D-11's added cross-reference should take exactly this `see <path> §"<Heading>"` form.

⚠ `LINK_DEPENDS` binds the target to this file, so any edit forces a relink — which is what makes
the D-13 byte-identity comparison non-vacuous (RESEARCH C-3 executed it: `.bin` and `.hex` SHA256
unchanged).

---

### 6. `.planning/seeds/py32f071-no-external-tool-fw-install.md` (doc, frontmatter edit)

**Analog: the file itself.** Current frontmatter, lines 1–6, verbatim:

```markdown
---
title: PY32F071 firmware install with no external tools (self-flash bootloader over the existing transport)
trigger_condition: v1.28 PY32F071 Port is activated, OR the first PY32F071 PCB/schematic is specified — whichever comes first, because this decision imposes PCB requirements
planted_date: 2026-07-28
status: dormant
---
```

Field set is exactly `title` / `trigger_condition` / `planted_date` / `status`. D-17 changes
`status:` and records that the seed stays live for FUT-N05. If a new field is added (e.g. a
`fired_date` or a pointer to the record), it is a **schema change to the seed format** — confirm
against other files in `.planning/seeds/` before inventing one; preferring prose in the body over
a novel frontmatter key matches D-02's "don't ride a convention change on one document".

Also in the body, line 24 — the sentence C-4 supersedes and D-18 must point away from:

> "A small bootloader in the first few KB of the 128 KiB flash, speaking the **same USB CDC +
> COBS framing** the firmware already uses."

Body cross-reference style already in the file (line 20):
`[`notes/py32f071-port-branch-state.md`](../notes/py32f071-port-branch-state.md)` — a relative
markdown link. Use the same form to point at the new record.

---

### 7. `.planning/phases/129-…/129-NONREGRESSION.md` (doc, evidence sweep)

**Analog A — `128-NONREGRESSION.md`** (closest: the only prior phase whose ceiling is
"publication, not behaviour"). Header block + ceiling + re-execution pledge, lines 1–25:

```markdown
# Phase 128 Non-Regression Sweep — closing plan (128-10)

**Written:** 2026-08-01
**Firmware branch (`firestarter`):** `v1.23-py32f071-integration` · **HEAD at this sweep:**
`0de57da3c9edfb40f86eee8b0964e0f1bcdd8559`
**Host branch (`firestarter_app`):** `v1.23-py32f071-integration` · **HEAD at this sweep:**
`cc9452f4db9a814ffb221bab767c24db67288365`
**Meta branch:** `gsd/v1.23-py32f071-integration`

> **No PY32F071 hardware exists.** Nothing in this milestone has ever run on this silicon,
> and nothing in it can. Everything below is about **publication**: … Nothing here says the
> published image runs, boots, or installs. The permitted claim is exactly one sentence wide.

**Re-execution pledge.** Every row in §2 was executed in **this session** (Plan 128-10's
Task 1), against the trees exactly as they now stand — nothing is copied from any of this
phase's nine prior plans' … SUMMARY files. Where a prior SUMMARY made a claim (an exit code, a
test count, a parsed literal), this document re-checked it independently against the live tree
and says so below.
```

Heading tree: `## 1. The claim, as precise statements` → `## 2. Locally provable, executed now`
→ `## 3. CI-only, discharged by …` → `## 4. The operator dispatch procedure` →
`## 5. What this phase does NOT claim` → `## 6. Precedent and prior art` →
`## 7. Criterion discharge` → `## 8. Deviations recorded during …`.

For Phase 129, **§3 and §4 collapse to nothing** (D-13: no CI dispatch, no operator gate) — the
byte-identity evidence moves *into* §2 as a locally-executed row. That is the one intentional
structural deviation from the 128 analog, and it should be stated as such in the doc.

**Analog B — `126-NONREGRESSION.md`** for the two sections 128 shapes differently:

- `## 3. The gate table — command, expected, observed` with per-repo subsections
  (`### Firmware repo (/workspaces/firestarter)`, `### Meta repo`, `### ARM row (re-queried
  read-only in this session)`). Phase 129 touches two repos, so use this per-repo split.
- `## 4. Success criteria — one subsection each, quoting the ROADMAP verbatim`
  (`### Criterion 1 — …`, `### Criterion 3 — … (AMENDED — read this carefully)`). The `AMENDED`
  suffix is the established way to record a criterion that could not be met as written — which
  is exactly what C-1 forces for ROADMAP criterion 3 ("a part with no VTOR").
- `## 5. Decision coverage — all nineteen, D-01…D-19` → Phase 129 has D-01…D-18.
- `## 7. Claim ceiling` and a closing `## Sweep Summary`.

⚠ **Phase 125 self-reference trap** (CONTEXT §Existing Code Insights): a `NONREGRESSION.md` that
quotes the claim-ceiling's forbidden phrases inside its own compliance paragraph trips the claim
gate when the file is scanned directly. Paraphrase or reference the forbidden phrases; do not
reproduce them.

---

## Shared Patterns

### S1. Fail-closed gate, with a fixture that proves it can go RED

**Source:** `firestarter_app/tests/fw_presence.py` + `firestarter_app/tests/test_py32_asset_name_host.py`
**Apply to:** `test_flash_path_record_sync.py`, `meta_presence.py`

The composite rule, in the order the analogs implement it:

1. Presence decided **once**, from a marker no rename can move (`<root>/.git`), behind a single
   env seam that overrides the **root only**, never the marker name.
2. Present-root + missing-target ⇒ `MissingScanTargetError`, never `pytest.skip`.
3. One non-vacuity assertion **per parse**, in its **own test**, before any comparison.
4. A shape regex, not merely `is not None` (Pitfall 8 in the analog docstring).
5. A parser that **raises rather than guesses** on multiple candidates.
6. Planted mutation under `tmp_path` only, with blob-SHA-unchanged + `git status --porcelain`
   empty asserted afterwards.
7. `shutil.which("git")` asserted non-None — a missing binary fails, never skips.
8. Two test classes: presence-gated legs vs pure REDs that need no sibling.

### S2. Module docstring states its own CI coverage, honestly

**Source:** `firestarter/tests/test_config_storage_design_vendored.py:15-20`;
`firestarter_app/tests/test_py32_asset_name_host.py:67-72`
**Apply to:** `test_flash_path_record_sync.py`, `meta_presence.py`

```
This module executes in NO CI leg on this branch: `pytest tests/ -v` runs
only in build.yml (push/PR to main) and beta-build.yml (push to beta) --
neither fires on this firmware milestone branch, and py32f071.yml has no
pytest step at all. The local run recorded in this phase's evidence
artifact is the only evidence this module's assertions were ever
exercised.
```

Copy this **verbatim in form** (F-14's explicit instruction). Never imply CI coverage.

### S3. Per-module path resolution; no shared test config

**Source:** `firestarter/tests/test_config_storage_design_vendored.py:22-29, 68-74`
**Apply to:** both new test files

`_HERE = Path(__file__).resolve().parent` / `_REPO_ROOT = _HERE.parent`, stdlib + pytest only,
nothing under `.pio/`. The repo has **no** `conftest.py`, `pytest.ini`, `pyproject.toml`,
`setup.cfg` or `tox.ini` — a recorded house rule, not an omission. Do not introduce one.

### S4. Requirements + decisions declared in the docstring, and only the closing plan ticks

**Source:** `test_config_storage_design_vendored.py:12-13`; `test_py32_asset_name_host.py:9-13`
**Apply to:** every new file, and every plan's action text

```
Requirements: CFG-01, CFG-02
Decisions covered: D-01, D-13, D-16, D-17, D-18, D-19
```

and the explicit non-closure disclaimer the 128 module carries (lines 9–13):

> "Requirements: REL-04 (cross-repo binding slice only — … this module does **NOT** close REL-04
> on its own — REL-04 is not marked complete in REQUIREMENTS.md from this plan)."

That parenthetical is the Phase 116 premature-tick guard in its most copyable form. Every
non-closing 129 plan should carry the equivalent sentence naming PCB-01…PCB-05.

### S5. Every claim carries an inline confidence tag

**Source:** `.planning/v1.9-COBS-DECISION.md` (headings 1.3/1.4/1.5 and body); measured across
the four precedent docs: 12 `[VERIFIED…]`, 1 `[CITED: …]`, 1 `[ASSUMED — …]`
**Apply to:** both new `.md` records

Vocabulary: `[VERIFIED]` · `[VERIFIED: <specific evidence>]` · `[CITED: <url-or-path>]` ·
`[ASSUMED — <reason>]` · **new fifth tag** `[UNVERIFIED-UNTIL-SILICON]`. Tags go in headings as
well as mid-sentence. Keep the blanket `## Claim ceiling` too — complements, not alternatives.
This resolves the CONTEXT "Claude's Discretion" sourcing question by precedent.

### S6. Two-layered doc, with the subset naming its parent and a stated sync obligation

**Source:** `.planning/v1.7-SHIELD-REVS.md` + `firestarter/doc/SHIELD-REVISIONS.md` +
`firestarter/CLAUDE.md` §"Hardware Revision Documentation"
**Apply to:** the meta record + the firmware subset

The v1.7 precedent names the shared sections **by number** in three places (both docs and the
`CLAUDE.md` note): "§1 (inventory) / §6 (capability matrix) / §7 (alias table) / §9 (ADC band
table)". Phase 129 should do the same for its four shared sections — the sync gate needs stable
heading strings to key on, and a numbered/quoted list is what makes both the gate and the human
instruction unambiguous.

---

## No Analog Found

None. All seven files have a close in-repo precedent.

One item is **precedent-thin rather than absent**, and the planner should treat it as a risk:

| Item | Role | Gap |
|---|---|---|
| `from tests.meta_presence import …` inside `firestarter/tests/` | utility import | `tests/__init__.py` exists, but **no current firmware test module imports a sibling helper** — every one self-resolves from `__file__`. The app repo does this routinely; the firmware repo has never done it. Prove the import resolves under `pytest tests/ -v` from the repo root as a first task, or use the `_HERE`-relative idiom instead. Adding a `conftest.py` to make it work is forbidden. |

---

## Metadata

**Analog search scope:** `.planning/` (root decision docs, `seeds/`, `phases/125|126|128/`),
`firestarter/tests/` (21 modules), `firestarter/platform/py32f071/`,
`firestarter/doc/`, `firestarter_app/tests/` (read-only).
**Files read in full or in targeted ranges:** 12
**Pattern extraction date:** 2026-08-02
