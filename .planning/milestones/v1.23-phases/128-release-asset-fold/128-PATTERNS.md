# Phase 128: Release-Asset Fold - Pattern Map

**Mapped:** 2026-08-01
**Files analyzed:** 9 (8 in `firestarter`, 1 in `firestarter_app`)
**Analogs found:** 8 / 9 (one genuinely new pattern: the composite action)

> **Dual-repo.** All paths below are relative to `/workspaces/firestarter/` unless prefixed
> `firestarter_app/`, in which case they are relative to `/workspaces/firestarter_app/`.
> Neither sub-repo is tracked by the meta-repo; both were read live this session.

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match |
|-------------------|------|-----------|----------------|-------|
| `.github/workflows/beta-build.yml` (modify) | CI workflow / release job | batch, artifact-publish | itself (steps 68-103) + `.github/workflows/py32f071.yml:28-60` | in-place |
| `.github/actions/build-py32f071/action.yml` (**new**) | CI composite action | batch build | **none in repo** — verbatim move of `py32f071.yml:28-60` | no-analog (steps have an analog; the *file kind* does not) |
| `.github/workflows/py32f071.yml` (modify) | CI workflow / gate | batch build | itself | in-place |
| `scripts/check_release_assets.py` (**new**) | checker script | file-I/O → exit code | `scripts/check_size_baseline.py` (487 L) | exact |
| `tests/test_check_release_assets.py` (**new**) | pytest (subprocess harness) | file-I/O, subprocess | `tests/test_check_size_baseline.py` (377 L) | exact |
| `tests/fixtures/planted_release_assets_*/pio_build/…` (**new**) | fixture tree | static data | `tests/fixtures/planted_cmake_manifest_missing_source/` (tree) | exact (tree, not `.log`) |
| `tests/fixtures/clean_release_assets_all_three/pio_build/…` (**new**) | fixture tree | static data | `tests/fixtures/clean_cmake_manifest_excluded/` | exact |
| `tests/test_checker_convention.py` (modify) | meta-test | static scan | itself (lines 123-124) | in-place |
| `platform/py32f071/README.md` (modify) | doc | — | `ad47c3b`'s unmerged diff | **see MISMATCH-1** |
| `firestarter_app/tests/test_py32_asset_name_host.py` (**new**) | pytest (cross-repo gate) | file-I/O, parse | `firestarter_app/tests/test_py32_flash_map_host.py:136-390` | exact sibling |

---

## Verification of upstream claims (read the mismatches before planning)

### MISMATCH-1 (HIGH) — `platform/py32f071/README.md` has **no** "Release integration" section

CONTEXT D-15 and canonical-refs both say the README's *release section* "correctly argues for a
glob and then supplies the literal", framing D-15 as a **correction**. Verified live: the shipped
file is 67 lines and its only headings are

```
1:# Firestarter on PY32F071
5:## Implemented
24:## Provisional example pin map
55:## Build
65:## Hardware validation still required
```

There is **no `## Release integration`**. The section D-15 describes exists only inside the
**unmerged** commit `ad47c3b` (`git show ad47c3b -- platform/py32f071/README.md`). So D-15 is
**add-the-section-in-corrected-form**, not edit-in-place. The plan's task wording must say "add"
or the executor will look for a section that is not there. Line 63 is the only line the section
replaces:

```
63: Generated outputs are ELF, BIN, HEX, linker map, size report, and SHA-256 checksums.
```

### MISMATCH-2 (MEDIUM) — `ad47c3b`'s own commit message repeats the R-16 error

`ad47c3b`'s message says the rename "also means beta-build.yml's `firestarter_*.hex` release glob
needs **no new pattern**", and the README diff it lands says the same. That is false for the same
reason R-16 records: the shipped glob is `.pio/build/**/firestarter_*.hex` (line 92, verified) and
CMake writes to `build/py32f071/`. When D-14 re-applies the README prose, both that sentence **and**
the glob-vs-literal justification (F-1) must be rewritten, not copied.

### MISMATCH-3 (LOW) — `ad47c3b`'s README supplies a literal *inside* a block that says "glob"

Verbatim from the unmerged diff — this is the exact text D-15 corrects:

```yaml
+          files: |
+            .pio/build/**/firestarter_*.hex
+            build/py32f071/firestarter_py32f071.hex     <-- literal, under a heading saying "a glob, not a literal"
```

### CONFIRMED — everything else CONTEXT/RESEARCH asserted about existing files

| Claim | Status |
|-------|--------|
| `beta-build.yml` is 103 L (CONTEXT says 104) | 103 lines. Off by one; harmless. |
| `beta-build.yml:92` `files: .pio/build/**/firestarter_*.hex` | **exact** (single-line scalar, not a block list — the fold must convert it to `files: \|`) |
| `tag_name: ${{ steps.version.outputs.version }}` at line 93 | exact |
| Step order `version` → `git-auto-commit-action@v5` → `Build PlatformIO Project` → `Resolve release target SHA` → `Release` | exact (lines 68, 74, 76, 79, 89) |
| `py32f071.yml` is 125 L, MERGE-03 comment names Phase 128 | 124 L + no trailing newline; comment at lines 4-8 |
| `test_checker_convention.py` `FLOOR = 5`, `FIXTURE_FLOOR = 10` at lines 123-124 | **exact** |
| Actual `scripts/check_*.py` count = 5, actual `planted_*` count = **13** | **exact** (`ls -d tests/fixtures/planted_* \| wc -l` → 13) |
| `size_baseline.json` `avr_targets` keys = `uno`, `uno328pb`, `leonardo` | exact |
| SDK `GIT_TAG 0ed2f4b4d3391eccfd4491006a30295fd78e32c2` at `CMakeLists.txt:16` | exact |
| CMake still hyphenated: `TARGET_NAME` L25, `-Wl,-Map=` L173, `BIN_FILE` L184, `HEX_FILE` L185 | exact — all four still `firestarter-py32f071.*` |
| `asset_candidates("py32f071")[0] == "firestarter_py32f071.hex"` | exact (`firmware.py:116-132`) |
| `FW_ABSENT_REASON` already in `ALLOWED_SKIP_REASONS`, imported not retyped | exact (`test_skip_census.py:92`, `:117`) |

---

## Pattern Assignments

### 1. `scripts/check_release_assets.py` (checker, file-I/O → exit code)

**Analog:** `scripts/check_size_baseline.py`. Copy structurally; the module docstring is ~70 lines
and is not optional house furniture — `test_checker_convention.py` test 5 greps the paired test for
the checker's filename, and the docstring is where the exit taxonomy lives.

**Docstring shape** (`check_size_baseline.py:1-79` — reproduce all six blocks):
title line naming phase/plan/decision, mode description, **`Exit codes:` taxonomy**,
**`Anti-hollow contract:`**, one or more **`Non-claim:`** paragraphs, **`Usage:`** examples.

Exit taxonomy verbatim (lines 37-47) — mirror the wording, substitute the new conditions:

```python
Exit codes (identical taxonomy in both modes):
  0 — every env supplied compared clean against the baseline/policy (gate passes)
  1 — an env's observed figures diverge from the baseline ... OR zero envs were
      compared (the never-vacuous guard: a comparator that compares nothing
      must not report success ...)
  2 — a supplied log could not be parsed ..., or the CLI
      invocation itself is malformed ... —
      a tool/format failure, categorically distinct from a size regression,
      and never silently reported as a pass
```

Anti-hollow paragraph (lines 49-58) — this is the sentence that names the fixture convention:

```python
Anti-hollow contract: this checker's mandatory paired pytest is
`tests/test_check_size_baseline.py`, which invokes this script as a real
subprocess against committed fixtures under `tests/fixtures/` (`captured_*` for
the clean-control arms, `planted_size_baseline_*` for one deliberate violation
per exit-taxonomy arm) via list-form `subprocess.run` — never `shell=True` and
never an in-process import. A passing pytest suite proves THIS script fails
the build on a real violation, not merely that the test asserts it should.
```

**Repo-root + env-seam block** (lines 87-97) — copy verbatim, add the second seam:

```python
# Resolve the repo root from this file's location so the gate behaves
# identically regardless of the caller's working directory (mirrors
# firestarter_app/tools/check_mypy_watermark.py:23).
# Layout: <repo>/scripts/check_size_baseline.py -> repo root is one parent up.
REPO_ROOT = Path(__file__).resolve().parent.parent

# Single-target env seam (a default IS appropriate here, unlike a list-valued
# seam): mirrors check_no_log_in_sdp_window.py's FIRESTARTER_SDP_SRC idiom.
FIRESTARTER_SIZE_BASELINE = os.environ.get(
    "FIRESTARTER_SIZE_BASELINE", str(REPO_ROOT / "scripts" / "baseline" / "size_baseline.json")
)
```

Seam naming is uniform across all five checkers (grepped): `FIRESTARTER_SIZE_BASELINE`,
`FIRESTARTER_MANIFEST_ROOT` (`check_cmake_manifest.py:131`), `FIRESTARTER_RANGE_ROOT` /
`FIRESTARTER_RANGE_FORK` (`check_landing_range.py:110,114`), `FIRESTARTER_PROVISIONAL_ROOT`
(`check_orphan_provisional.py:172`). `FIRESTARTER_PIO_BUILD_ROOT` (F-6) fits the family exactly.
Note the recurring **in-child-environment-only** comment, e.g. `check_cmake_manifest.py:130`:

```python
# ... set in the CHILD environment.
FIRESTARTER_MANIFEST_ROOT = os.environ.get("FIRESTARTER_MANIFEST_ROOT", str(REPO_ROOT))
```

**Manual argv parser** (lines 329-386) — the house convention, with its own docstring justifying
the absence of argparse and its `raise SystemExit(2)` on every malformed form:

```python
def _parse_argv(argv):
    """Manual argv parser (no third-party/argparse dependency; house convention,
    mirrors check_permitted_claims.py's resolve_targets(argv) style).
    ...
    Raises SystemExit(2) on a malformed invocation (unknown flag, a flag missing
    its value, ...) -- a CLI usage error is itself a tool/format failure, not
    a size regression.
    """
```

**Never-vacuous guard, placed BEFORE the loop** (lines 395-403) — D-12's "fail if `avr_targets`
parses empty" is this exact shape:

```python
    # Never-vacuous guard: if zero envs will be compared (no logs supplied and
    # --rebuild absent), fail closed BEFORE the per-env loop. A comparator
    # that compares nothing must not print PASS:.
    if not avr_log_specs and not native_log_specs and not rebuild:
        print(
            "FAIL: no envs compared -- supply --avr-log/--native-log or --rebuild "
            "(never-vacuous guard: a comparator that compares nothing must not pass)"
        )
        return 1
```

**Output prefixes and entrypoint** (lines 310-326, 486-487):

```python
def _print_pass(compared):
    parts = ", ".join(compared)
    print(f"PASS: {parts}")

def _print_fail(failures, bucketed_label=""):
    print(f"FAIL: {bucketed_label}".rstrip() if bucketed_label else "FAIL:")
    for line in failures[:20]:
        print(f"  {line}")
    if len(failures) > 20:
        print(f"  ... and {len(failures) - 20} more")

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

Imports are stdlib only: `json, os, re, subprocess, sys, pathlib.Path`. **Every failure message
names the env, the expectation and the observation** — the paired test asserts on those substrings.

---

### 2. `tests/test_check_release_assets.py` (test, subprocess + fixtures)

**Analog:** `tests/test_check_size_baseline.py`.

**Module docstring** (lines 1-105) has four mandatory blocks:
1. MIT header + `Phase N Plan NN — <what this pairing is>` + `Requirements:` + `Decisions covered:`
2. The anti-hollow paragraph (lines 12-18).
3. A numbered **`Coverage:`** list, one line per test.
4. A **derivation block**: every `planted_*` fixture stated as *"= <captured source> with <single
   stated edit>"*. Lines 54-101. For a *tree* fixture, `planted_cmake_manifest_missing_source/README.md`
   carries the equivalent statement inside the fixture directory instead.
5. The recorded no-conftest note (lines 102-104), copy verbatim:

```python
Self-contained path resolution below — NOT in conftest.py (firestarter/tests/ has no
conftest.py anywhere in the repo; this is a recorded house-rule pattern decision, per
test_update_version.py's own comment, not an omission). Stdlib and pytest only.
```

**Path constants + subprocess harness** (lines 113-135) — copy exactly, renaming `_CHECKER`:

```python
_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
_CHECKER = _REPO_ROOT / "scripts" / "check_size_baseline.py"
_FIXTURES = _HERE / "fixtures"

def _run_checker(argv=None, env_overrides=None):
    """Invoke check_size_baseline.py as a real subprocess (list argv, never shell=True).

    `env_overrides`, when given, is merged into the child's environment on top of
    the current process environment -- used by the baseline-seam-precedence test to
    set FIRESTARTER_SIZE_BASELINE without mutating this process's own environment.
    """
    env = {**os.environ, **(env_overrides or {})}
    return subprocess.run(
        [sys.executable, str(_CHECKER), *(argv or [])],
        cwd=str(_REPO_ROOT),
        capture_output=True,
        text=True,
        env=env,
    )
```

**The seam-precedence test** (lines 245-264) — F-6 requires one per seam; this is the template:

```python
def test_baseline_seam_precedence_flips_clean_log_to_fail(tmp_path):
    """Coverage 7 — pointing FIRESTARTER_SIZE_BASELINE at a temp JSON whose Leonardo
    flash figure differs must make the previously-clean captured_build_leonardo.log
    FAIL. Proves the checker genuinely reads its baseline through the env seam rather
    than embedding the recorded numbers in the script itself."""
    real_baseline = json.loads(_BASELINE.read_text())
    real_baseline["avr_targets"]["leonardo"]["flash_used"] = 1
    tampered = tmp_path / "tampered_size_baseline.json"
    tampered.write_text(json.dumps(real_baseline))

    result = _run_checker(
        ["--avr-log", f"leonardo={_FIXTURES / 'captured_build_leonardo.log'}"],
        env_overrides={"FIRESTARTER_SIZE_BASELINE": str(tampered)},
    )
    assert result.returncode != 0, (...)
    assert "FAIL:" in result.stdout, ...
```

**Assertion style, universal in this module:** every assert carries an f-string message echoing
`stdout` and `stderr`. The literal `returncode != 0` must appear (convention test 6). Where the
taxonomy matters, assert the *literal* code, not just non-zero (lines 191-209):

```python
    assert result.returncode == 2, (
        f"expected the literal exit code 2 (parse failure), got {result.returncode}.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    ...
    assert "PASS:" not in result.stdout, (
        f"A parse failure must never print PASS:. Got:\n{result.stdout}"
    )
```

---

### 3. `tests/fixtures/planted_release_assets_*/` + `clean_release_assets_all_three/` (tree fixtures)

**Analog:** `tests/fixtures/planted_cmake_manifest_missing_source/` — the only *directory-tree*
planted fixtures in the repo (the `size_baseline` ones are flat `.log` files, so they are the wrong
analog for layout). Its layout:

```
tests/fixtures/planted_cmake_manifest_missing_source/
├── README.md                                  <- the single-stated-edit derivation
├── platform/py32f071/CMakeLists.txt
├── platform/py32f071/src/main.cpp
├── src/firestarter.cpp
└── src/proms/eeprom_28c.cpp
```

Its clean control is `tests/fixtures/clean_cmake_manifest_excluded/` with the same shape. Both are
reached by the checker through `FIRESTARTER_MANIFEST_ROOT` set in the **child** environment — which
is exactly how `FIRESTARTER_PIO_BUILD_ROOT` must be used, and why the fixture directory can be named
`pio_build/` rather than `.pio/`.

**Naming contract** — `tests/fixtures/README.md:8-16`, verbatim:

```markdown
- **`captured_*`** — verbatim tool output, committed **unedited**. ...
- **`planted_*`** — a deliberate violation, each derived from a named `captured_` (or otherwise real)
  file by a single stated edit, used to prove a checker fails closed rather than passing vacuously.
- **`clean_*`** — a control that must pass a checker cleanly, proving the checker does not fire on
  legitimate input.
```

**The `git ls-files` rule** — `tests/fixtures/README.md:27-34`, the paragraph F-6/Pitfall 2 depend on:

```markdown
Fixture presence in this directory is verified with `git ls-files`, **never** with `git add`'s exit
code. Git refuses to stage any path containing a `.git` path component ... and does
so **silently at exit 0** — `git add` reports success while staging nothing. `git ls-files` is the
only check that reflects what is actually tracked in the index.
```

A zero-byte AVR hex is a required planted case (F-1's `statSync().isFile()` observation). Git tracks
zero-byte files fine; no seam issue there.

---

### 4. `tests/test_checker_convention.py` (modify — the floors)

**Exact current text, lines 121-124:**

```python
# Hardcoded floors -- see module docstring for what each counts and why a
# future checker addition must raise these in the same commit.
FLOOR = 5
FIXTURE_FLOOR = 10
```

Glob (lines 116-119), non-recursive, `scripts/` only:

```python
CHECKER_GLOB = "check_*.py"
```

Fixture glob (line 219): `_FIXTURES_DIR.glob("planted_*")`, counting **files and directories**.
Measured today: 5 checkers, **13** planted entries. So `FLOOR` 5→6; `FIXTURE_FLOOR` must be counted
after the fixtures land, not predicted (13 + however many `planted_release_assets_*` entries).

The docstring block that must also be updated in the same commit is lines 53-66 — it enumerates the
five checkers by name and states the FIXTURE_FLOOR provenance:

```python
FLOOR = 5 -- the number of `check_*.py` files actually shipped into
`firestarter/scripts/` across Phases 123-124: `check_size_baseline.py`, ...
A later phase that adds a firmware checker under
`firestarter/scripts/` raises both floors deliberately in the SAME commit
that adds the checker; lowering a floor is never the correct response to a
red gate here -- it means a checker, test, or fixture went missing.
```

Convention tests the new triple must satisfy (all seven currently green):
`test_every_checker_has_paired_test_module` (name pairing), `test_every_checker_has_planted_fixture`
(`planted_release_assets*` glob on the stem after `check_`), `test_paired_test_module_names_its_checker`
(the literal string `check_release_assets.py` must appear in the test module),
`test_paired_test_module_asserts_nonzero_exit` (the literal `returncode != 0`).

---

### 5. `firestarter_app/tests/test_py32_asset_name_host.py` (cross-repo gate)

**Analog:** `firestarter_app/tests/test_py32_flash_map_host.py`, lines 136-390. Copy structurally.

**Imports + module-scope path constant** (lines 39-51, 151):

```python
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from firestarter import py32_dfu
from tests.fw_presence import FW_ROOT, fw_path, requires_fw
...
_LINKER_SCRIPT = fw_path("platform", "py32f071", "linker", "PY32F071xB_FLASH.ld")
```

For D-08(b) the two module-scope constants become
`fw_path("platform", "py32f071", "CMakeLists.txt")` and
`fw_path(".github", "workflows", "beta-build.yml")`, and the import becomes
`from firestarter.firmware import asset_candidates`.

**The A-7 header comment justifying `fw_path` over a hand-built path** (lines 136-150) — reproduce
with the new targets named:

```python
# The path is resolved through `fw_path()` -- a hand-built relative path out
# of `tests/` is deliberately never constructed here. `fw_path` raises
# `MissingScanTargetError` when the sibling repo is present but this file is
# not, so a Phase-129 rename of the linker script becomes a hard failure at
# collection/call time, never a silent skip (research finding A-7: ...).
# `@requires_fw` -- imported from tests/fw_presence.py ... -- is the ONLY skip
# marker this module uses, and it fires only when the sibling repo itself
# is genuinely absent (no `../firestarter/.git` marker), never on a
# present-but-renamed scan target.
```

**Non-vacuity guard, one per parse** (lines 190-200) — D-09 needs **two** of these, and the message
must contain the phrase `vacuously true` because the RED test greps for it:

```python
def _assert_non_vacuous(regions: dict[str, tuple[int, int]], source: str) -> None:
    """Non-vacuity guard (research finding A-7), run BEFORE any value is
    compared: a parse that found neither FLASH nor CONFIG must be an
    AssertionError, never a silent pass -- an empty (or partial) region
    dict would make every downstream comparison VACUOUSLY TRUE."""
    assert "FLASH" in regions and "CONFIG" in regions, (
        f"parsed {len(regions)} region(s) ({sorted(regions)!r}) from {source} "
        "-- expected to find both FLASH and CONFIG. A parse that found "
        "neither region would make every downstream comparison vacuously "
        "true (research finding A-7)."
    )
```

**Fail-closed `git` helpers** (lines 216-244) — copy verbatim:

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
```

(`_git_porcelain` is the same shape with `status --porcelain`.)

**Class split — this is the load-bearing structure:**
- `class TestLinkerScriptParity:` (line 247) — every method carries `@requires_fw`, and every method
  re-parses and calls `_assert_non_vacuous` **before** comparing (lines 253-321). Coverage 1
  (`test_parse_is_non_vacuous`) runs first and does nothing else.
- `class TestLinkerScriptParityFailsClosedOnBadInput:` (line 324) — *"The three RED demonstrations
  (D-14). **None carries `@requires_fw`.**"* These run in app CI, where the firmware sibling is
  absent (F-8), which is the only reason anything in this module is enforced there.

**The planted-mutation RED test** (lines 336-380) — monkeypatch the *module's own* path constant,
write under `tmp_path`, assert the real blob SHA unchanged and the firmware tree clean:

```python
        real_path = _LINKER_SCRIPT  # captured BEFORE any monkeypatch
        before_blob = _git_hash_object(real_path)
        real_text = real_path.read_text()
        mutated_text = real_text.replace("CONFIG (r)  : ORIGIN = 0x0801E000, ...", "...0x0801FE00...")
        assert mutated_text != real_text, (
            "planted mutation did not actually differ from the real text "
            "-- the replacement target string was not found ..."
        )
        planted_path = tmp_path / "planted-PY32F071xB_FLASH.ld"
        planted_path.write_text(mutated_text)
        monkeypatch.setattr(sys.modules[__name__], "_LINKER_SCRIPT", planted_path)
        ...
        after_blob = _git_hash_object(real_path)
        assert after_blob == before_blob, (
            "the planted mutation touched the REAL linker script -- it "
            "must only ever be written under tmp_path"
        )
        assert _git_porcelain(FW_ROOT) == "", (
            "the firmware repo's working tree is no longer clean after "
            "the planted-copy test -- it is a read-only input to this "
            "phase"
        )
```

The last assertion is F-16 / Pitfall 7: **the app test is RED whenever the firmware tree is dirty.**

**`fw_presence.py` mechanics** the new module binds to (read-only, `fw_presence.py:77-140`):

```python
_APP_REPO_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_FW_ROOT = _APP_REPO_ROOT.parent / "firestarter"
FW_ROOT: Path = Path(os.environ.get("FIRESTARTER_FW_ROOT", str(_DEFAULT_FW_ROOT)))
FW_REPO_MARKER: Path = FW_ROOT / ".git"
FW_REPO_PRESENT: bool = FW_REPO_MARKER.exists()
FW_ABSENT_REASON: str = f"firestarter firmware checkout absent (no {FW_REPO_MARKER} marker)"
requires_fw = pytest.mark.skipif(not FW_REPO_PRESENT, reason=FW_ABSENT_REASON)
```

Two constraints from its docstring (lines 34-55): **everything binds at import**, so
`monkeypatch.setenv("FIRESTARTER_FW_ROOT", ...)` has *no effect* — a different root needs a
subprocess pytest run; and `FW_ROOT` is the **sibling repo**, never the in-repo `firestarter/`
package (the name-collision trap). `fw_path()` raises `MissingScanTargetError` when the repo is
present but the target is missing (lines 117-140) — that is the anti-A-7 mechanism.

**Skip census:** `test_skip_census.py:92` does `from tests.fw_presence import FW_ABSENT_REASON, ...`
and line 117 has it inside `ALLOWED_SKIP_REASONS`. **Confirmed present — do not add an entry** (D-09).
Confirm by running the module, not by reading it.

---

### 6. `.github/workflows/beta-build.yml` (modify — the fold target)

**The trigger + the one existing dispatch input** (lines 15-20) — the `rehearsal` input is added here:

```yaml
  workflow_dispatch:
    inputs:
      beta_version:
        description: 'Explicit PEP 440 pre-release version (e.g. 3.1.0b1). Leave blank for auto-increment via git-tag scan.'
        required: false
        type: string
```

**The REL-01 boundary — lines 68-77 verbatim. All ARM steps go after line 74:**

```yaml
      - name: Generate release version
        id: version
        env:
          BETA_VERSION: ${{ github.event.inputs.beta_version }}
        run: .github/scripts/update_version.py

      - uses: stefanzweifel/git-auto-commit-action@v5

      - name: Build PlatformIO Project
        run: pio run
```

Note the `env:`-passing pattern: `BETA_VERSION: ${{ github.event.inputs.beta_version }}` — **an
env var, not an argv flag**, and it is F-2's whole mechanism. The auto-commit step is bare, with no
`with:` block at all.

**A step that emits an output** (lines 79-87) — the shape the composite action's `hex_path`/`sdk_sha`
and any new id-carrying step should follow, including the citing comment style:

```yaml
      - name: Resolve release target SHA
        id: release_target
        run: |
          # Phase 20 E2E-03 (firmware mirror): pin the tag to the post-auto-
          # commit HEAD so the Pre-release points at the version-bumped
          # commit, not the trigger commit.
          SHA=$(git rev-parse HEAD)
          echo "sha=$SHA" >> "$GITHUB_OUTPUT"
          echo "Release target SHA: $SHA"
```

**The `Release` step as shipped** (lines 89-103) — note `files:` is a **single-line scalar** today
and must become a `|` block; `fail_on_unmatched_files` is absent (F-1's real invariant); and the
`env:` block already carries a long provenance comment, which is the precedent for pinning the
`fail_on_unmatched_files` omission with a comment:

```yaml
      - name: Release
        uses: softprops/action-gh-release@v2
        with:
          files: .pio/build/**/firestarter_*.hex
          tag_name: ${{ steps.version.outputs.version }}
          target_commitish: ${{ steps.release_target.outputs.sha }}
          prerelease: true
          make_latest: false
        env:
          # Phase 20 E2E-05: PERSONAL_ACCESS_TOKEN is not configured on the
          # firmware repo. Unlike the app, the firmware Release has no
          # downstream workflow that needs `release.published` to cascade
          # (no PyPI publish step), so the built-in GITHUB_TOKEN is
          # sufficient and avoids requiring a PAT.
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

`permissions: contents: write` is already set at job level (lines 25-26) — draft-release creation
needs nothing more.

---

### 7. `.github/actions/build-py32f071/action.yml` (**new file kind**) + `py32f071.yml` (modify)

**No `.github/actions/` exists.** `find .github -type f` returns exactly four files:
`scripts/update_version.py`, `workflows/{py32f071,build,beta-build}.yml`. The composite-action
*file format* has no in-repo analog; RESEARCH §Pattern 2 is the substitute and its two traps
(`shell:` required on every `run:`; `continue-on-error` at the **call site only**) are first-use
hazards here.

**The steps that move in, verbatim from `py32f071.yml:28-60`** — this is the text to lift, with
`shell: bash` added to each:

```yaml
      - name: Install GNU Arm toolchain and build tools
        run: |
          sudo apt-get update
          sudo apt-get install -y \
            cmake \
            ninja-build \
            gcc-arm-none-eabi \
            binutils-arm-none-eabi

      - name: Record tool versions
        run: |
          set -o pipefail
          {
            arm-none-eabi-gcc --version
            arm-none-eabi-ld --version
            cmake --version
            ninja --version
          } | tee tool-versions.txt

      - name: Configure
        run: |
          set -o pipefail
          cmake \
            -S platform/py32f071 \
            -B build/py32f071 \
            -G Ninja \
            -DCMAKE_BUILD_TYPE=Release \
            2>&1 | tee configure.log

      - name: Build
        run: |
          set -o pipefail
          cmake --build build/py32f071 2>&1 | tee build.log
```

D-17 (unpinned `apt-get install -y`) is satisfied by copying this literally.

**What stays in `py32f071.yml` and gets renamed hyphen→underscore (D-14):** every one of the
following lines currently spells `firestarter-py32f071` and must not be missed —
`:66` diagnostics artifact name, `:79` `arm-none-eabi-size` on the `.elf`, `:86-95` the
`test -s` + `sha256sum` block (7 occurrences), `:100-103` the manifest block, `:113` artifact
name, `:116-120` the artifact path list. D-16 keeps only the single-hex upload, so `:110-125`
collapses; `:62-73` (failure diagnostics) is unaffected by D-16's wording and should be preserved
unless the plan says otherwise.

The MERGE-03 comment at lines 4-8 is what Integration-Points says to *update, not delete*:

```yaml
  # MERGE-03/D-10: implemented literally as specified -- push: branches: [beta]
  # with no paths filter, so any change anywhere that breaks the ARM configure
  # is caught on beta. Phase 128 will later fold the ARM build into
  # beta-build.yml, creating a double-ARM-build question on a beta push; that
  # is recorded for Phase 128 to resolve, not pre-solved here.
```

---

### 8. `128-NONREGRESSION.md` (D-18 evidence artifact)

**Analogs:** `.planning/phases/{123,124,125,126,127}-*/1NN-NONREGRESSION.md`. The house shape,
from `127-NONREGRESSION.md:1-30`:

```markdown
# Phase 127 Non-Regression Sweep — closing plan (127-12)

**Written:** 2026-08-01 (Plan 127-12)
**Host branch (`firestarter_app`):** `v1.23-py32f071-integration` · **HEAD at this sweep:** `<sha>`
**Firmware branch (`firestarter`):** `v1.23-py32f071-integration` · **HEAD:** `<sha>` ...
**Meta branch:** `gsd/v1.23-py32f071-integration`

**No PY32F071 hardware exists.** Nothing in this milestone has ever run on this silicon, and
nothing in it can.

**Re-execution pledge.** Every row below was executed in **this session** ... — nothing is copied
from any of this phase's ... prior plans' SUMMARY files. ...

---

## 1. The claim, as precise statements
1. ... 2. ... 3. ...
```

Then numbered `## 2..N` sections, each a table of `| # | Mechanism | Command | Expected | Observed |`
(122's shape) or per-criterion sections (127's). The **explicit non-claim** paragraph is the
"No PY32F071 hardware exists" block, hoisted above §1 — that is where D-18's non-claim goes.

---

## Shared Patterns

### S-1. Exit code, never a human reading output
**Source:** `check_size_baseline.py` (whole file); `123-CONTEXT.md` `<specifics>`.
**Apply to:** the AVR-asset gate, the SDK-pin assertion, the filename equality, the REL-01
`strings` check. Every one of them ends in `exit 1` / `exit 2`, not an `echo`.

### S-2. Fail-closed non-vacuity before any comparison
**Source:** `check_size_baseline.py:395-403` (checker side);
`test_py32_flash_map_host.py:190-200` (test side).
**Apply to:** `avr_targets` empty key set, both app-side parses, the `GIT_TAG` 40-hex guard, the
bash `${#MATCHES[@]}` glob-expansion guard.

### S-3. Env seam with a committed default, set only in the CHILD environment
**Source:** `check_size_baseline.py:95-97` + `test_check_size_baseline.py:121-135` (`env_overrides`).
**Apply to:** `FIRESTARTER_PIO_BUILD_ROOT` (new) and the reused `FIRESTARTER_SIZE_BASELINE`. Each
seam gets its own precedence test.

### S-4. Subprocess, list-form argv, `cwd=_REPO_ROOT`, never `shell=True`, never in-process import
**Source:** `test_check_size_baseline.py:129-135`.
**Apply to:** every arm of the new paired test.

### S-5. Comments cite the decision/requirement/phase that produced the line
**Source:** `beta-build.yml:82-84` ("Phase 20 E2E-03…"), `:98-102` ("Phase 20 E2E-05…"),
`py32f071.yml:4-8` ("MERGE-03/D-10…"), `check_cmake_manifest.py:33-45`.
**Apply to:** every new YAML step, the `fail_on_unmatched_files` omission, the `continue-on-error`
call site, the transcription literal, and the composite action's `description:`.

### S-6. Cross-repo tests bind through `@requires_fw` + `fw_path()`, never a local `.exists()` proxy
**Source:** `fw_presence.py` (whole module).
**Apply to:** the one new app-repo test. RED-demonstration tests deliberately carry **no** marker.

### S-7. No `conftest.py` in `firestarter/tests/` — resolve paths in-module
**Source:** `test_checker_convention.py:100-114`, `test_check_size_baseline.py:102-118`.
Verified: no `conftest.py` anywhere under `firestarter/tests/`.

---

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `.github/actions/build-py32f071/action.yml` | composite action | batch build | **No `.github/actions/` directory exists in `firestarter`** (nor in `firestarter_app`). The *steps* have an exact analog (`py32f071.yml:28-60`, liftable verbatim), but the `runs: using: composite` file format, the `outputs:` → `steps.<id>.outputs` wiring, and the mandatory `shell:` on each `run:` have no in-repo precedent. Use 128-RESEARCH.md §Pattern 2 and §Pitfall 5. |

---

## Metadata

**Analog search scope:** `/workspaces/firestarter/{scripts,tests,tests/fixtures,.github,platform/py32f071}`,
`/workspaces/firestarter_app/tests`, `.planning/phases/12[0-7]-*/`
**Files read in full:** `check_size_baseline.py`, `test_check_size_baseline.py`,
`test_checker_convention.py`, `beta-build.yml`, `py32f071.yml`, `tests/fixtures/README.md`,
`firestarter_app/tests/test_py32_flash_map_host.py`, `firestarter_app/tests/fw_presence.py`
**Files read in part:** `check_cmake_manifest.py` (1-60), `platform/py32f071/README.md` (35-67),
`platform/py32f071/CMakeLists.txt` (grep), `firestarter_app/firestarter/firmware.py` (112-135),
`127-NONREGRESSION.md` (1-30), `git show ad47c3b -- platform/py32f071/README.md`
**Pattern extraction date:** 2026-08-01
