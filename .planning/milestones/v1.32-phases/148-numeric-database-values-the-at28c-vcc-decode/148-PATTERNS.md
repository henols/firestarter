# Phase 148: Numeric Database Values & the AT28C VCC Decode - Pattern Map

**Mapped:** 2026-08-19
**Files analyzed:** 16 (6 new, 10 modified)
**Analogs found:** 16 / 16
**Scope:** host-only. Every path below is relative to `/workspaces/firestarter_app` unless stated.

> **Read `148-RESEARCH.md` §"Edit Sites — exact current code" first.** It already carries the
> verified line numbers and verbatim current code for every *modified* file. This document does
> **not** repeat it. For modified files, this document adds only the surrounding **convention** an
> executor must imitate (comment/citation style, constant placement, error idiom, import order).
> Its primary contribution is the **six new files**, which RESEARCH.md names but does not model.

---

## File Classification

### New files (Wave 0 — no prior art in the tree)

| New file | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `tests/test_vcc_margin_rail.py` | test (data invariant) | batch / whole-DB scan | `tests/test_sdp_db_invariant.py` | **exact** |
| `tests/test_wire_dict_equivalence.py` | test (golden byte-identity) | transform / batch | `tests/test_audit_coverage_matrix.py::test_golden_file_matches` (:576) + `tests/test_variant_decode_evidence_stability.py` (per-record naming) | **exact** (composite) |
| `tests/golden/wire_dict_baseline.json` | golden fixture (data) | file-I/O | `tests/golden/chip_database_field_inventory.json` — the **only** golden JSON in the tree carrying a `meta` block | **exact** |
| `test_info_at28c256` (new test in `tests/test_characterization.py`) + its `.ambr` entry | test (CLI snapshot) | request-response (subprocess) | `tests/test_characterization.py::test_info_known_chip` (:347) | **exact** |
| A unit test for `interpret_timing`'s fatal branch (suggest `tests/test_build_db_interpret_timing.py`) | test (unit, tools import) | transform | `tests/test_check_mypy_watermark.py` legs 1–4 + `_load_checker` (:126) | **role-match** |
| Source-scan / AST assertions (suggest `tests/test_numeric_schema_source_scan.py`) | test (source scan + AST) | file-I/O / static analysis | `tests/test_dev_gate_reads_no_firmware_source.py` (source scan) + `tests/test_chip_database_field_inventory.py::_generator_chip_entry_keys` (:234-262, AST walk of `build_db.py`) | **exact** (composite) |

### Modified files

| Modified file | Role | Data Flow | In-tree convention analog | Match Quality |
|---|---|---|---|---|
| `tools/build_db.py` (emitter + D-03 rule + D-08 fatal) | generator | transform / batch | itself — SRAM block `:807-821`, `_PAGE_SIZE_BY_PART` `:140-159`, `VCC_VOLTAGES` `:192-200` | **exact** (self) |
| `tools/diff_db.py` (`RULE_VCC_MARGIN_RAIL` + canonicalizer) | gate tooling | transform / batch | itself — `PROV01_PROTECT_METADATA` (the newest complete 3-place rule: `:213`, `:365`, `:563-585`) | **exact** (self) |
| `firestarter/database.py` (delete coercion, add render helper) | model / host DB layer | CRUD / transform | itself — `_parse_pulse_duration` `:128-143` is the module-level-helper placement being reversed | **exact** (self) |
| `tools/audit_coverage_matrix.py` (delete `parse_pulse_us`) | tooling | batch | itself — `:106-110` def, 7 call sites, `_members_with_parseable_pulse` `:1717-1734` | **exact** (self) |
| `firestarter/ic_layout.py` `:571`, `:592-597` | component (presentation) | transform | itself + `eprom_info.py` — the two are already kept in WR-02 parity | **exact** (self) |
| `firestarter/eprom_info.py` `:391-403` | component (presentation) | transform | `ic_layout.py:592-597` (its own parity twin) | **exact** |
| `tools/extra_chips.json` | authored data supplement | file-I/O | itself — both records are byte-symmetric; edit them identically | **exact** (self) |
| `tests/test_diff_db_gate.py` `:86-91`, `:118-123` | test fixture literals | — | itself (`_make_chip` at `:80-91`) | **exact** (self) |
| `tests/golden/chip_database_field_inventory.json` | golden (re-derived) | file-I/O | itself — `meta.how_to_update` is the binding protocol | **exact** (self) |
| `tests/golden/v1.3-COVERAGE-MATRIX.md` | golden (regenerated) | file-I/O | itself — header says "DO NOT EDIT BY HAND. Re-run the tool." | **exact** (self) |

---

## Pattern Assignments — NEW FILES

### 1. `tests/test_vcc_margin_rail.py` (test, whole-DB data invariant)

**Analog:** `tests/test_sdp_db_invariant.py` (701 lines). Same role (whole-database data
invariant), same data flow (direct JSON load → select → count → assert), same milestone-era house
style. Copy its **five structural moves** verbatim.

**Move 1 — path anchoring, self-contained, NOT in conftest** (`test_sdp_db_invariant.py:70-83`):

```python
import json
from pathlib import Path

from firestarter.sdp_capability import sdp_capability_for_entry

# Absolute path to the firestarter_app directory (independent of cwd)
_FA_DIR = Path(__file__).parent.parent
_DB_FILE = _FA_DIR / "firestarter" / "data" / "chip_database.json"

# Upstream protocol_id / firmware dispatch key for configure_eeprom28c (0x0D).
_ALGORITHM_0X0D = 13
```

For the "no `vcc_mv` decreased" guard this file **also** needs the baseline. Take the second path
constant from `tests/test_variant_decode_evidence_stability.py:48-66` — the `FIRESTARTER_*` env
seam idiom used across the suite:

```python
_BASELINE_FILE = os.environ.get(
    "FIRESTARTER_BASELINE_FILE",
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "tools",
        "baseline",
        "chip_database.baseline.json",
    ),
)
```

**Move 2 — a shared selector helper with an explicit anti-vacuity docstring**
(`test_sdp_db_invariant.py:86-100`). Note it names the exact failure it prevents:

```python
def _select_0x0d_chips(db: dict) -> list[tuple[str, dict]]:
    """Select every (manufacturer, chip) pair with programming.algorithm == 13.

    The DB shape is {manufacturer: [chip, ...]}, and the fields live in a
    nested "programming" object. A top-level scan on db (rather than this
    nested per-chip access) finds nothing and would make every downstream
    assertion pass vacuously.
    """
    selected = []
    for _mfr, chips in db.items():
        for chip in chips:
            if chip["programming"]["algorithm"] == _ALGORITHM_0X0D:
                selected.append((_mfr, chip))
    return selected
```

**Move 3 — an offender-naming assertion helper, shared by the real test AND the non-vacuity leg**
(`:102-115`). Never a bare `assert a == b`:

```python
def _assert_chip_id_check_false(selected: list[tuple[str, dict]]) -> None:
    """Raise AssertionError naming every offending chip if any selected
    entry's programming.chip_id_check is not exactly False."""
    offenders = [
        f"{mfr}/{chip.get('part_number', '?')}"
        for mfr, chip in selected
        if chip["programming"]["chip_id_check"] is not False
    ]
    assert not offenders, (
        "TRACE-05: every algorithm==13 (0x0D) chip must carry "
        "chip_id_check: false -- the identity gate must be provably dead "
        f"across the whole 0x0D bucket. Offending chips: {offenders}"
    )
```

**Move 4 — the count assertion, with the "what a count change means" clause** (`:267-284`). This
is the shape for "exactly 56 movers":

```python
def test_exactly_84_algorithm_0x0d_entries() -> None:
    """TRACE-05 / CLOSE-01: exactly 84 chip_database.json entries have
    programming.algorithm == 13.

    A count change means a chip was added to or removed from the 0x0D
    bucket and every trace-coverage assumption in this milestone needs
    re-checking. ...
    """
    db = json.loads(_DB_FILE.read_text(encoding="utf-8"))
    selected = _select_0x0d_chips(db)
    assert len(selected) == 84, (
        "TRACE-05/CLOSE-01: expected exactly 84 chip_database.json entries "
        f"with programming.algorithm == 13, found {len(selected)}. A count "
        "change means a chip was added to or removed from the 0x0D bucket "
        "-- re-check every Phase 116+ trace-coverage assumption before "
        "proceeding."
    )
```

**Move 5 — a non-vacuity leg driving the SAME helper with a synthetic in-memory DB** (`:337-370`).
This is mandatory house style for any data gate; without it the 56-count could be passing for the
wrong reason:

```python
def test_synthetic_chip_id_check_true_is_flagged_non_vacuous() -> None:
    """Non-vacuity proof: a synthetic algorithm==13 chip with
    chip_id_check: True MUST make the shared helper raise. ...
    Exercises the exact same _select_0x0d_chips / _assert_chip_id_check_false
    helpers the real-DB test above calls, not a parallel reimplementation.
    """
    synthetic_db = {
        "SYNTHETIC_MFR": [
            {
                "part_number": "SYNTHETIC_0x0D_VIOLATION",
                "programming": {"algorithm": 13, "chip_id_check": True, ...},
            }
        ]
    }
    selected = _select_0x0d_chips(synthetic_db)
    assert len(selected) == 1, "Synthetic fixture setup error: expected 1 selected chip"

    try:
        _assert_chip_id_check_false(selected)
    except AssertionError:
        pass
    else:
        raise AssertionError(
            "Non-vacuity failure: the shared helper did not raise on a "
            "synthetic chip_id_check: True row -- the TRACE-05 invariant "
            "gate is vacuous."
        )
```

**`VCC_VOLTAGES[0x02]` unchanged (DATA-04):** import the table, do not re-read the source text.
The in-process import idiom is proven at `tests/test_build_db_inclusion.py:524`:

```python
from tools import build_db
...
assert synthetic_vpp > build_db.RURP_VPP_CEILING_MV, (
    "test precondition: synthetic VPP must exceed the ceiling"
)
```

(Verified live 2026-08-19: `from tools import build_db` resolves via the `tests/__init__.py`
namespace-package path and exposes `VCC_VOLTAGES`, `interpret_timing`, `_PAGE_SIZE_BY_PART`.
Importing `build_db` performs **no** network fetch — only `open(PINOUT_FILE)` at `:206`.)

---

### 2. `tests/test_wire_dict_equivalence.py` (test, golden byte-identity over 746 records)

**Analog A — the byte-identity assertion and its "if this is legitimate" instruction:**
`tests/test_audit_coverage_matrix.py::test_golden_file_matches` (`:576-648`):

```python
        # Byte-identity assertion — the load-bearing regression gate.
        produced = out.read_bytes()
        golden = golden_file.read_bytes()
        assert produced == golden, (
            "regenerated matrix drifted from golden fixture; "
            f"produced {len(produced)} bytes vs golden {len(golden)} bytes; "
            "if this is a legitimate change, regenerate the golden file "
            "alongside the matrix commit"
        )
```

…and its golden-missing guard (`:620-623`), which fails loudly rather than skipping:

```python
        assert golden_file.exists(), (
            f"golden fixture missing at {golden_file}; "
            "Wave 4 Task 2 must snapshot the matrix to this path"
        )
```

> **Do NOT copy that test's `pytest.skip` when the meta-repo ledger is absent** (`:614-619`). That
> skip exists only because its input lives *outside* the sub-repo. `wire_dict_baseline.json` lives
> **inside** `tests/golden/`, so there is no standalone-CI case and no skip is warranted. A skip
> here would make the phase's central proof invisible in CI.

**Analog B — per-record diff naming (better diagnostics than one 325 KB blob compare):**
`tests/test_variant_decode_evidence_stability.py:104-131` — load, index, project the protected
field set, compare per record:

```python
def _load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _all_chips(db):
    for mfg, chips in db.items():
        if isinstance(chips, list):
            for chip in chips:
                yield mfg, chip


_WIRE_FIELDS = ("algorithm", "vpp_mv", "pinout")
```

**The capture idiom (must run as task 1, pre-change).** Module-level real DB, exactly as
`tests/test_chip_test_sdp_leg.py:217` and `tests/test_chip_test_blank_check_order.py:47` do:

```python
_REAL_DB = EpromDatabase(skip_local_override=True)
```

`skip_local_override=True` is **mandatory** — `tests/test_characterization.py:501` states the rule
verbatim: *"skip_local_override=True is MANDATORY (phase 36 rule, Pitfall-4): a ~/.firestarter
override would leak a spurious row."*

The 746-chip loop itself already exists in production as `tools/check_dispatch.py:368-370` — reuse
its shape (`db.get_eprom(part)` → `db.convert_to_programmer(mapped)`), do not invent a new one:

```python
            mapped = db.get_eprom(part)
            if mapped:
                wire = db.convert_to_programmer(mapped)
```

**Key-count guard (RESEARCH F-8):** assert the wire-key union is exactly the 9 measured keys
`{algorithm, bus-config, chip-id, flags, memory-size, page-size, pin-count, pulse-delay, vpp_mv}`
and that `vcc` / `vpp_volts` are **absent** — this is D-06's load-bearing claim and it belongs in
this file, not in prose.

---

### 3. `tests/golden/wire_dict_baseline.json` (new committed golden)

**Analog:** `tests/golden/chip_database_field_inventory.json` — verified to be the **only** golden
JSON in the tree with a `meta` block (`grep -rln "how_to_update\|recorded_at_head" --include=*.json`
returns exactly that one file). The convention is a top-level `meta` object whose values are
**prose sentences**, not tags. Match it verbatim in shape:

```json
{
  "meta": {
    "source": "firestarter/data/chip_database.json",
    "generator": "tools/build_db.py",
    "recorded_by": "Phase 140 Plan 03",
    "requirement": "TABLE-05",
    "decision": "D-12",
    "recorded_at_head": "4d18b645ab18a2d2465f0f623062e9249eb24132",
    "why_counts_not_names": "A field added to a subset of chips slips past a names-only assertion ...",
    "why_not_diff_db": "tools/diff_db.py's GATE-02 (_diff_field_paths) already unions both key sets ... regenerating that baseline silences the comparison ...",
    "how_to_update": "Re-derive every number in this file with an independent traversal of the live chip_database.json (two levels deep: {manufacturer: [chip, ...]}) -- never hand-edit a count to make a surprise disappear. State in the commit message which key changed, on which level, and why. ...",
    "db_is_generated": "firestarter/data/chip_database.json is produced by tools/build_db.py from the upstream tools/infoic.xml (plus the hand-curated tools/extra_chips.json supplement) and is never hand-edited, which is why this gate also reads the generator.",
    "generator_scan_scope": "..."
  },
  "totals": { "manufacturers": 59, "chips": 746 },
  "levels": { ... },
  ...
}
```

**Required `meta` keys for `wire_dict_baseline.json`** (the executor must author the prose, but the
key set is fixed by the analog): `source`, `generator`, `recorded_by`, `requirement`, `decision`,
`recorded_at_head`, `how_to_update`. Add one phase-specific key naming the D-06 non-claim
(e.g. `why_nine_keys` — recording that a five-key capture would miss `bus-config`, `flags` and
`page-size`, per RESEARCH F-8).

**Mechanical facts for this file:**
- Path: `tests/golden/wire_dict_baseline.json`. `tests/golden` is in ruff's `extend-exclude`
  (`pyproject.toml`), so nothing formats or reformats it.
- Measured: 746/746 resolvable, 0.43 s, 332,716 bytes, canonical SHA-256
  `027a43a0dcef1085afa6a35d2500bd35556140dde4b838dfcd65bfae8cac7dab`
  (RESEARCH §"D-14 — 746-chip wire-dict equivalence, measured").
- Canonical serialization the SHA was measured against: `json.dumps(out, sort_keys=True, indent=2)`
  — matching the generator's own `indent=2, sort_keys=True` convention for
  `chip_database.json`. Do not change it, or the recorded SHA becomes unverifiable.
- Record key: `f"{mfg}|{pn}|{i}"` (part numbers are **not** unique — `diff_db.py:246-266`'s CR-01
  comment documents that 65-69 records share a part_number; a `pn`-only key silently shadows ~9%).

---

### 4. New `firestarter info AT28C256` snapshot (in `tests/test_characterization.py`)

**Analog:** `tests/test_characterization.py::test_info_known_chip` (`:347-353`) — verbatim:

```python
def test_info_known_chip(snapshot):
    """Pin info output for W27C512 (known chip).

    Phase 69 Plan 01 fixed the ic_layout list-vs-int crash; exit code is now 0
    and stdout shows the formatted chip layout.
    """
    stdout, stderr, rc = run_firestarter("info", "W27C512")
    assert rc == 0
    # Pin stdout (chip info layout) and stderr (should be empty after fix)
    assert stdout == snapshot
    assert stderr == snapshot(name="test_info_known_chip_stderr")
```

**How the `.ambr` entry is keyed** (measured in `tests/__snapshots__/test_characterization.ambr`):

- Default stdout snapshot → `# name: test_info_known_chip` (line **423**).
- Named second snapshot → `# name: test_info_known_chip[test_info_known_chip_stderr]` (line **474**)
  — i.e. syrupy renders `snapshot(name="X")` as `# name: <test_name>[X]`.
- Parametrized tests key the same way: `# name: test_help_fw[test_help_fw_stable]` (line 216).
- Body is a `'''`-quoted block, each content line indented two spaces.

**The harness is `run_firestarter`, not `CliRunner`** (`:143-162`). It resolves the installed entry
point via `shutil.which("firestarter")` (`:73`), pipes through `normalize_output()` (`:96-140`),
and forces `FIRESTARTER_CONFIG_DIR=_CLEAN_CONFIG_DIR` (an empty tmpdir, `:89`) so no
`~/.firestarter/database.json` override leaks in. The new test must call `run_firestarter` — nothing
else.

**Two phase-specific constraints (RESEARCH F-3):**
1. This is a **new** snapshot entry, never a re-baseline. `git diff` on the `.ambr` must show
   **only additions** of the new `# name: test_info_at28c256` block(s).
2. Every other `.ambr` byte must be unchanged. The phase gate is
   `git diff --stat tests/__snapshots__/test_characterization.ambr` showing insertions only —
   zero deletions.

**Captured before-state** (RESEARCH, run live): `VCC: 4.0v` / `VPP: 12.0v` / `Chip ID: -`, exit 0.
After the D-03 rule: `VCC: 5.0v`, VPP row unchanged.

---

### 5. Unit test for `interpret_timing`'s fatal branch (D-08)

**Analog:** `tests/test_check_mypy_watermark.py` — the only module in the tree that drives a
`tools/` function **in-process** and asserts a raise. Four properties to copy.

**Property A — the in-process loader, with its own justification comment** (`:126-131`):

```python
def _load_checker():
    """Load tools/check_mypy_watermark.py in-process. `tests/__init__.py`
    exists, so the repo root is on `sys.path` and `tools` resolves as a
    namespace package -- the same import path already proven at
    tests/test_check_devtest_orchestrator.py:395-397."""
    return importlib.import_module("tools.check_mypy_watermark")
```

For `build_db`, `from tools import build_db` (the `test_build_db_inclusion.py:524` form) is
equally house-standard and simpler; either is acceptable.

**Property B — assert the CODE *and* the MESSAGE. An exit-code-only assertion is explicitly
called out in this repo as insufficient** (`:152-165`):

```python
def test_truncated_run_exits_2(capsys: pytest.CaptureFixture[str]) -> None:
    """A truncated mypy run (returncode 2, no completion clause) must raise
    SystemExit(2) via the returncode guard, naming the offending exit code --
    not merely raising, but raising for the stated reason."""
    mod = _load_checker()

    with pytest.raises(SystemExit) as exc:
        mod.classify_mypy_result(2, TRUNCATED_OUTPUT)
    assert exc.value.code == 2

    captured = capsys.readouterr()
    assert "mypy exited 2" in captured.err, (
        f"expected the failure message to name exit code 2, got:\n{captured.err}"
    )
```

Per D-08's discretion clause the failure "must stop the build and name the protocol and the
unparseable value" — so the message assertion must check **both** (e.g. `"0x07"` and the repr of
the bad value), not just that something was raised.

**Property C — control legs.** The module docstring states the rule explicitly (`:48-51`):

> *"Controls 7-8 exist so that legs 1-4 are not passing merely because `classify_mypy_result` raises
> unconditionally -- without them, four raising legs prove nothing about which inputs are supposed
> to raise."*

So pair the fatal leg with at least two controls: a parseable `pulse_delay` on a 0x07/0x08/0x0B
protocol returning the int µs, and one on a non-pulse protocol returning the algorithm-controlled
sentinel `0`.

**Property D — canned inputs as module-level constants with a measurement comment**
(`:83-123`), not inline literals.

**Reachability note the plan must carry:** RESEARCH §"D-08 reachability" measured the branch as
**provably dead against the pinned XML** (27,862 `<ic>` elements, 0 missing, 0 unparseable). A
green `python3 tools/build_db.py` therefore proves nothing about this branch — **only** this unit
test does. Verified live 2026-08-19: `build_db.interpret_timing(None, 0x07)` reaches the branch
today and prints the WARN.

---

### 6. Source-scan + AST assertions (DATA-03 / DATA-04)

**Analog A — source scan for an ABSENT token:**
`tests/test_dev_gate_reads_no_firmware_source.py` (110 lines). It is the tree's cleanest in-test
source scan and its docstring already argues the scoping rule this phase needs.

Forbidden-token constant with a rationale comment (`:51-60`):

```python
# Forbidden tokens naming a firmware path or file extension -- CHAN-07's own
# touch note says "channel.py reads the package's own __version__ and opens
# no file at all"; these are the shapes a firmware-source read would take if
# one were ever added.
_FORBIDDEN_TOKENS: tuple[str, ...] = (
    "firestarter/include",
    '.h"',
    ".ino",
    "serial_comm",
    "frame_parser",
)
```

Whole-module scan via `inspect.getsource(module)` (`:103-110`):

```python
def test_channel_module_source_contains_no_open_call_anywhere() -> None:
    """The stronger, file-wide claim CHAN-07's own touch note asks for ...
    -- checked across the WHOLE file, not just the four callables
    parametrized above ..."""
    source = inspect.getsource(channel)
    assert "open(" not in source
```

Parametrization so a failure **names** the violator (`:73-87`):

```python
@pytest.mark.parametrize(
    ("label", "fn"), _GATE_CALLABLES, ids=[label for label, _ in _GATE_CALLABLES]
)
def test_gate_callable_source_contains_no_open_call(
    label: str, fn: Callable[..., object]
) -> None:
    """Parametrized so a failure names exactly which callable violated the
    property, rather than one monolithic assertion hiding which one."""
```

> **Scoping warning this analog states outright (`:24-32`):** a whole-file scan of a large,
> pre-existing module *"would trivially fail vacuously-in-the-other-direction (false positive) the
> moment any unrelated handler in the same file legitimately …"* — For this phase:
> `database.py` (732 lines) is small and focused enough that a **whole-file** scan for
> `_parse_pulse_duration` and `.replace("V"` is correct and is what DATA-03 asks for.
> `audit_coverage_matrix.py` (1942 lines) is large — but `parse_pulse_us` is a distinctive
> project-local identifier, so a whole-file scan for that exact token is still safe. Do **not**
> whole-file-scan for a generic token like `float(` in either.

**Analog B — the AST walk of `build_db.py` (for `_PAGE_SIZE_BY_PART` still == 2 entries):**
`tests/test_chip_database_field_inventory.py:234-262`. It is already the tree's AST reader of this
exact file. Copy the walk's shape:

```python
def _generator_chip_entry_keys(source_text: str) -> "set[str]":
    """ast-walk `source_text` (tools/build_db.py's own source) and collect
    every string key literal reaching a variable literally named
    `chip_entry` ... This is the D-12/T-140-10 half: chip_database.json is
    GENERATED, so a new key reaching `chip_entry` here becomes a new database
    field the moment anyone regenerates -- reachable without ever executing
    the generator.
    """
    tree = ast.parse(source_text)
    keys: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "chip_entry":
                if isinstance(node.value, ast.Dict):
                    _collect_dict_keys(node.value, keys)
            ...
    return keys
```

Its module-level path constants (`:93-106`) show the env-seam + non-overridable split; reuse the
`_APP_ROOT` anchoring:

```python
_HERE = Path(__file__).resolve().parent
_APP_ROOT = _HERE.parent
_DB_REL = "firestarter/data/chip_database.json"
_GEN_REL = "tools/build_db.py"
_GOLDEN = _HERE / "golden" / "chip_database_field_inventory.json"
_DB_PATH = Path(os.environ.get("FIRESTARTER_CHIP_DB_JSON", str(_APP_ROOT / _DB_REL)))
```

For the "no new part-number-keyed dict" half of DATA-04, a module-level-constant AST scan analog
also exists at `tests/test_sdp_capability.py:640-661` (walk `tree.body`, inspect top-level nodes,
assert a set relation with a message naming what was found):

```python
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    imported_modules: set[str] = set()
    for node in tree.body:
        ...
    assert imported_modules <= {"__future__", "typing"}, (
        "HOST-04/D-03: sdp_capability.py's top-level imports must be a "
        f"subset of {{'__future__', 'typing'}}; found {imported_modules}."
    )
```

Simplest correct assertion for `_PAGE_SIZE_BY_PART`: `from tools import build_db` then
`assert len(build_db._PAGE_SIZE_BY_PART) == 2` (verified live: it is 2 today) — plus the AST leg
for "no *new* part-number-keyed dict", which an import cannot see.

---

## Pattern Assignments — MODIFIED FILES (convention only)

### `tools/build_db.py` — where the D-03 rule goes and how it must be written

**Analog is in the same file:** the shipped SRAM normalization, `:807-821`. Copy its
*placement*, its *comment shape* and its *scoping caveat*:

```python
                # SRAM/FRAM/NVRAM vcc normalization.
                # Static-memory parts have a single supply rail — there is no
                # separate elevated programming voltage, so the minipro "vcc"
                # (read-rail) vs "vdd" (program-rail) split is meaningless here.
                # Upstream infoic.xml records a lower vcc test-rail (3.3V/4V) for
                # these 5V NVRAM/FRAM families (FM16xx, DS1230, M48Txx, BQ40xx),
                # which misrepresents the chip's nominal supply. The RURP shield
                # supplies a fixed 5V VCC for SRAM-class parts regardless, so the
                # operating voltage firestarter actually applies is vdd. Align
                # vcc to vdd so `firestarter info` reports the true supply.
                # Type-keyed (SRAM only): UV-EPROM and Flash/EEPROM keep their
                # vcc as the correct read voltage (vdd there is the elevated
                # program rail, e.g. 6.5V — must NOT be surfaced as operating Vcc).
                if _etype == "SRAM":
                    chip_entry["electrical"]["vcc"] = chip_entry["electrical"]["vdd"]
```

**Structural facts an executor must honour** (RESEARCH §A "Ordering note"): the emitter builds
`vcc`/`vdd` inline inside the `chip_entry` dict literal at `:747-755`, so the D-03 rule **cannot**
sit inside the literal — it must be a post-construction mutation right here, running **after** the
SRAM block, before `chips.append(chip_entry)` at `:823`. (Measured non-interaction: no SRAM part
has `vdd == 4000`.)

**Constant placement + citation style.** Module-level constants live in the CONFIGURATION /
LOGIC MAPPERS bands near the top, each preceded by a `[VERIFIED: …]` or `[CITED: …]` tag. The two
in-file templates:

```python
# [VERIFIED: minipro database.c#L130-L135 @ a8efaedc — tl866ii_vcc_voltages[]]
VCC_VOLTAGES = {
    0x00: "5V",
    0x01: "3.3V",
    0x02: "4V",  # BUG-1 fix: was missing from v1.12
    ...
}
```

```python
# PGSZ-01 / CR-01: datasheet-sourced per-chip page size map.
# Keyed on the canonical part number (first alias in the comma-separated list).
# Each entry carries a [CITED:] datasheet reference — DO NOT author [ASSUMED] values.
# ...
_PAGE_SIZE_BY_PART: dict[str, int] = {
    # [CITED: firestarter/datasheets/0x05-FLASH-AMD-STD/W29C040.pdf §6.2
    #         "Every page contains 256 bytes of data."]
    "W29C040": 256,
```

`_VCC_MARGIN_RAIL_MV = 4000` belongs beside `VCC_VOLTAGES` with a comment naming index `0x02` and
carrying the same `[VERIFIED: minipro database.c#L130-L135 @ a8efaedc]` citation. **`VCC_VOLTAGES`
itself is not edited** (D-01) — only its values become mV ints per D-07.

**Error idiom for D-08.** The current branch (`:412-432`) already carries the WR-05 comment
explaining *why* it was narrowed; extend that comment rather than replacing it, and keep the
`except (TypeError, ValueError):` narrow — a broad `except Exception:` is gated by **nothing**
here (ruff `select = ["E","F","I","UP"]`; every `# noqa: BLE001` in this repo is inert):

```python
    try:
        val = int(raw_hex, 16)
    except (TypeError, ValueError):
        # WR-05 (98-03): narrowed from bare `except Exception` so an unparseable
        # pulse_delay is visible (not silently masked as a valid 0 us timing) —
        # an upstream infoic.xml decode fault would otherwise ship wrong timing
        # to the firmware unnoticed.
        print(
            f"WARN: chip with protocol {protocol_id:#04x} has unparseable "
            f"pulse_delay {raw_hex!r} — defaulting to 0 us",
            file=sys.stderr,
        )
        val = 0
```

Keep the `{protocol_id:#04x}` + `{raw_hex!r}` formatting when the branch becomes fatal — that is
exactly the "name the protocol and the unparseable value" D-08 asks for.

**Imports** (`:1-8`) are stdlib → third-party → first-party, ruff-`I` ordered; `build_db.py`
already imports from the package (`from firestarter.constants import MAX_27C020_SIZE`), so a new
first-party import is in-convention.

---

### `tools/diff_db.py` — the `RULE_VCC_MARGIN_RAIL` branch needs THREE edits, not one

**Analog: `PROV01_PROTECT_METADATA`** — the most recently added rule and the only one that
demonstrates all three places at once. Copy it in all three.

**(a) `_RATIONALES` entry** (`:213-237`) — multi-line string, phase + requirement in line 1,
mechanism, an explicit "no other delta" sentence, then `[VERIFIED:]` / `[CITED:]` blocks:

```python
    "PROV01_PROTECT_METADATA": (
        "Phase 136.1 PROV-01 — flags bit 14/15 + raw page_size decode added to the\n"
        "  programming block. Three new keys, decoded directly from each <ic> element's\n"
        "  own flags/page_size attributes (never a cross-reference or token match):\n"
        ...
        "  Metadata only — no algorithm / pinout / vpp / electrical.type delta; the\n"
        "  84/43/41 SDP ALLOW/REFUSE partition (tests/test_sdp_db_invariant.py) is\n"
        "  unchanged.\n"
        "  [VERIFIED: minipro src/database.c#L39-L50 @ a8efaedc236c1d9718bd28299dfbb99536b010ff —\n"
        "   https://gitlab.com/DavidGriffith/minipro/-/blob/a8efaedc236c1d9718bd28299dfbb99536b010ff/src/database.c#L39]\n"
        "  [CITED: doc/infoic-field-dictionary.md CONFIRMED bit 14/15 row;\n"
        "   .planning/phases/136.1-sdp-partition-provenance/136.1-01-PLAN.md;\n"
        "   .planning/phases/136.1-sdp-partition-provenance/136.1-01-BLAST-RADIUS.md]"
    ),
```

The permalink base is documented once at `:44`:
`https://gitlab.com/DavidGriffith/minipro/-/blob/a8efaedc/src/database.c`

The narrowest voltage-rule precedent for wording is `BUG3_VCC_VDD` (`:75-81`):

```python
    "BUG3_VCC_VDD": (
        "BUG-3 vcc/vdd label swap only — inverted field labels corrected.\n"
        "  bits 11-8 = vcc (VCC supply voltage), bits 15-12 = vdd (VDD programming voltage).\n"
        "  Previously the decode had these reversed.\n"
        "  [VERIFIED: minipro database.c#L921-L923 @ a8efaedc —\n"
        "   https://gitlab.com/DavidGriffith/minipro/-/blob/a8efaedc/src/database.c#L921]"
    ),
```

**(b) `_RULE_FIELD_PATHS` entry** (`:365-370`) — a preceding comment stating the scope, then the
exact tuple set:

```python
    # Phase 136.1 PROV-01: flags bit 14/15 + raw page_size decode added. Scoped to
    # exactly these three new programming.* keys — no other field changes.
    "PROV01_PROTECT_METADATA": {
        ("programming", "protect_off_before"),
        ("programming", "protect_on_after"),
        ("programming", "infoic_page_size_raw"),
    },
```

For reference, the two tuples this phase **renames** (`:313`, and `BUG2_AND_BUG3` at `:308-311`):

```python
    "BUG3_VCC_VDD": {("electrical", "vcc"), ("electrical", "vdd")},
```

`RULE_VCC_MARGIN_RAIL` needs `{("electrical", "vcc_mv")}`.

**(c) The `_classify_diff` priority branch** (`:563-585`) — this is the edit D-11's own text
omits and RESEARCH measured as required (its Option B; Option A leaves the 56 movers as
undifferentiated compound notes on another phase's rationale). The template, showing the
`and not <other>_diff` exclusivity chain and the trailing rationale comment:

```python
    elif (
        (
            bl_prog.get("protect_off_before") != cu_prog.get("protect_off_before")
            or bl_prog.get("protect_on_after") != cu_prog.get("protect_on_after")
            or bl_prog.get("infoic_page_size_raw")
            != cu_prog.get("infoic_page_size_raw")
        )
        and not algo_diff
        and not timing_diff
        and not voltage_diff
        and not pinout_diff
        and not type_diff
        and not vpp_diff
        and bl_prog.get("page_size") == cu_prog.get("page_size")
    ):
        # PROV01_PROTECT_METADATA: Phase 136.1 PROV-01 — only the three new
        # protect_off_before/protect_on_after/infoic_page_size_raw keys changed
        # (added). No other field changes, including the curated page_size (kept
        # distinct from infoic_page_size_raw by the explicit page_size equality
        # check above). Placed LAST (most specific: exactly these three new keys)
        # to avoid shadowing any compound changes detected by prior rules.
        label = "PROV01_PROTECT_METADATA"
```

**The value-scoped-branch precedent is `RC1_DIP32_27C020`** (`:483-497`) — the only existing rule
that keys on a *decoded value* rather than a field name, which is exactly the `RULE_VCC_MARGIN_RAIL`
shape (`bl.vcc_mv == 4000 and cu.vcc_mv == cu.vdd_mv != 4000`). Note its explicit
"scope is now ENFORCED here (not just asserted in prose)" comment:

```python
    elif (
        pinout_diff
        and not algo_diff
        ...
        and cu_chip.get("pinout") == "DIP32_27C020"
    ):
        # RC1_DIP32_27C020 (before SRAM_PINOUT): Phase 98 RC-1 fix — 0x08 ≤256K chips
        # reassigned from DIP32_STD to DIP32_27C020. Scoped to the new pinout value so
        # SRAM_PINOUT (which handles 28-pin pm_idx=0 re-routes) is not masked.
        # WR-03 (98-03): pinout-only scope is now ENFORCED here (not just asserted in
        # prose) — a co-occurring voltage/type/vpp change on a DIP32_27C020 chip falls
        # through to a more specific/generic rule instead of being absorbed silently.
        label = "RC1_DIP32_27C020"
```

**Placement:** RESEARCH is explicit — the new branch **must precede `BUG3_VCC_VDD`** (`:473`),
otherwise a mover whose only other delta were `vdd` is attributed to the Phase 57/58 label-swap
rationale. Also update the docstring's numbered "Priority order:" list at `:418-437` — every
existing rule has an entry there.

**The canonicalizer hook** (`:603-615` `_load_db` → `_make_index`). Its docstring convention
(`_load_db`, `:601-615`) shows the exit-code discipline to preserve:

```python
def _load_db(path, label):
    """Load a chip-database JSON, exiting 2 (infra error) on any load failure.

    WR-04: a missing/malformed input is an infrastructure problem, NOT a diff
    BLOCK -- it must use a distinct exit code (2) so a CI consumer keying on the
    exit status does not misreport it as a real gate failure (exit 1).
    """
```

**`_diff_field_paths` (`:373-392`) needs no edit** — it is key-name agnostic, which is precisely
*why* an un-renamed classifier escalates the 56 movers to `unexplained`.

---

### `firestarter/database.py` — the render helper (D-16) and the deletion

**Helper placement analog is the function being deleted.** `_parse_pulse_duration` sits at
`:128-143` — module level, after `logger = logging.getLogger("Database")` (`:126`), before
`_read_config_file` (`:146`) and the class. Put the new render helper in that same band: same
level, same neighbourhood, one clean reversal.

```python
def _parse_pulse_duration(pulse_str: str) -> int:
    """Parse a pulse_duration string from chip_database.json into microseconds.

    Accepts values like "100 us", "1000 us", "Algorithm Controlled", or "".
    Returns the integer microsecond value, or 0 for unknown / algorithm-controlled.
    """
```

**Naming:** the helper is imported by two other modules, so it is **public** (no leading
underscore) — unlike `_parse_pulse_duration`. Both consumers already carry the import line to
extend (`ic_layout.py:12`, `eprom_info.py:15`):

```python
from firestarter.database import EpromDatabase  # Changed import
```

**Render contract** (RESEARCH §"Render Contract", all 13 distinct DB values verified byte-exact):
`f"{mv / 1000:.1f}v"`. Do not change the format; D-15 makes byte-identity load-bearing.

**Deletion sites to reverse** — `:379-393`. Note the two `except` bodies are the bare expression
`None` (not `pass`, not a log); they go with the layer:

```python
        vpp_str = electrical.get("vpp", "0").replace("V", "")
        vcc_str = electrical.get("vcc", "0").replace("V", "")
        try:
            vpp = float(vpp_str)
        except (ValueError, TypeError):
            None
            # logger.warning(f"Invalid VPP value for {ic.get('part_number')}: {vpp_str}")  # noqa: E501
```

**D-10's direct-indexing rule** applies to the replacement reads: `chip["electrical"]["vcc_mv"]`,
never `.get(key, 0)`. The mapped dict at `:410-424` is where they land.

**The dead fallback to delete** (`:544-547`):

```python
        # Use vpp_mv directly when available (integer millivolts from build_db.py)
        vpp_mv = full_eprom_data.get("vpp_mv") or int(
            full_eprom_data.get("vpp_volts", 0) * 1000
        )
```

---

### `firestarter/ic_layout.py` + `firestarter/eprom_info.py` — the two render sites are a parity pair

They are **already** kept in deliberate parity and each carries a WR-02 comment saying so. Change
them together or the parity comment becomes a lie.

`ic_layout.py:588-597`:

```python
        # D-07-VPP: gate on vpp_mv > 0, not the always-zero flags & 0x08.
        # Coerce defensively: user-override entries may supply vpp_mv as a string.
        # ...
        try:
            _vpp_mv = int(eprom_data.get("vpp_mv", 0) or 0)
        except (TypeError, ValueError):
            _vpp_mv = 0
        if etype not in {"SRAM", "FRAM"} and _vpp_mv > 0:
            output_data["vpp_str"] = f"{eprom_data.get('vpp_volts', 'N/A')}v"
```

`eprom_info.py:396-403`:

```python
        if _etype not in {"SRAM", "FRAM"} and _vpp_mv > 0:
            # WR-02: mirror the info view's fallback ('N/A') so the two views
            # produce identical output when vpp_mv > 0 but vpp_volts is absent
            # (e.g. operator-override entries). Previously the list view fell
            # back to '-' here, diverging from info's 'N/A' (D-03 parity).
            vpp_str = f"{ic.get('vpp_volts', 'N/A')}v"
        else:
            vpp_str = "-"
```

**Open edge RESEARCH flags (not a locked decision):** the `'N/A'` fallback renders `N/Av` today.
With `vpp_volts` deleted the helper receives `vpp_mv` (always present, gated `> 0`), so the DB path
cannot reach it — but a user-override could still supply a non-int. Decide whether the helper
mirrors the existing `try/except` tolerance, and say so in the plan.

**Needs no change** (verified): `ic_layout.py:603-607` already omits the pulse row on `0`.

---

### `tools/extra_chips.json` — hand edit to an AUTHORED supplement

Both records are byte-symmetric; the two blocks to migrate are identical in shape:

```json
      "electrical": {
        "type": "UV-EPROM",
        "size_bytes": 2048,
        "pin_count": 24,
        "vpp": "25V",
        "vpp_mv": 25000,
        "vcc": "5V",
        "vdd": "6.5V"
      },
      "programming": {
        "algorithm": 11,
        "pulse_duration": "500 us",
        "chip_id_check": false,
        "chip_id_value": "0x00000000"
      },
```

Migration: drop `vpp`, `vcc: "5V"` → `vcc_mv: 5000`, `vdd: "6.5V"` → `vdd_mv: 6500`,
`pulse_duration: "500 us"` → `pulse_duration_us: 500`. Both records, identically.

**State it in the plan as a hand edit to an authored supplement — not a hand edit to generated
JSON.** The provenance fields (`source`, `datasheet`, `provenance`, `verification_status`,
`verification_note`) are untouched, and the existing `provenance` prose asserts *"Wire values match
the v1.15 user-override DECODE-AUDIT.md exactly … NOT silently moved (SAFE-04)"* — a representation
change keeps that true; a value change would not. `tests/test_extra_chips_supplement.py:105-118`
pins those wire values and must still pass unchanged in meaning.

---

### `tests/test_diff_db_gate.py` — the only test fixture with old-schema literals

`_make_chip` at `:80-91` (plus the inline literal at `:113-126`):

```python
    def _make_chip(self, etype, part_number="FM1608"):
        return {
            "part_number": part_number,
            "electrical": {
                "type": etype,
                "vcc": "5V",
                "vdd": "5V",
                "vpp": "12V",
                "vpp_mv": 12000,
            },
            "programming": {"algorithm": 40, "pulse_duration": "Algorithm Controlled"},
            "support_status": "supported",
        }
```

Its subprocess seam (`:51-58`) is what a `RULE_VCC_MARGIN_RAIL` bucket-count test should reuse:

```python
        result = subprocess.run(
            [sys.executable, "tools/diff_db.py"],
            cwd=str(firestarter_app_dir),
            capture_output=True,
            text=True,
            check=False,
        )
```

`FIRESTARTER_DB_FILE` / `FIRESTARTER_BASELINE_FILE` (`diff_db.py:32-39`) allow a scratch-DB variant
without touching the real files.

---

### `tools/audit_coverage_matrix.py` — the deletion and its knock-on

Definition to delete (`:106-110`):

```python
def parse_pulse_us(s):
    """'10000 us' -> 10000. Raise on shape mismatch (Pitfall 3 fail-fast)."""
    if not isinstance(s, str) or not s.endswith(" us"):
        raise ValueError(f"Unexpected pulse_duration shape: {s!r}")
    return int(s[:-3])
```

Call-site replacement shape (`:307` is representative — direct indexing, per D-10):

```python
        pulse_us = parse_pulse_us(chip["programming"]["pulse_duration"])
```
→ `pulse_us = chip["programming"]["pulse_duration_us"]`

Filter to rewrite as `!= 0` (`:1717-1734`):

```python
def _members_with_parseable_pulse(members):
    """Subset of `members` whose `pulse_duration` is a 'N us' string. ..."""
    out = []
    for mfg, chip in members:
        pd = chip.get("programming", {}).get("pulse_duration", "")
        if isinstance(pd, str) and pd.endswith(" us"):
            try:
                parse_pulse_us(pd)
            except ValueError:
                continue
            out.append((mfg, chip))
    return out
```

The eighth read is a **render**, not a parse (`:537`, inside `_enum_row`) — it survives an int but
changes the rendered cell from `100 us` to `100`, which is what forces the
`tests/golden/v1.3-COVERAGE-MATRIX.md` regeneration (**297** ` us` value cells; the 6
`pulse_bucket` label lines are unchanged).

---

## Shared Patterns

### S-1. Test module docstring — numbered `Coverage:` list keyed to requirement IDs

**Source:** `tests/test_chip_database_field_inventory.py:1-84`; `tests/test_sdp_db_invariant.py:1-68`;
`tests/test_check_mypy_watermark.py:1-65`.
**Apply to:** all four new test modules.

Shape: MIT header (older files) or a direct opener; phase + plan + requirement line; a
"**Defect class this closes**" paragraph; a numbered `Coverage:` list, one entry per test naming the
test function; then the environment seams and any trap warnings.

```
Phase 140 Plan 03 -- TABLE-05 (D-12)

Requirements: TABLE-05

Defect class this closes: a new chip_database.json field entering through
the generator ... invisible to a names-only assertion or one that can be
silenced by regenerating tools/baseline/chip_database.baseline.json.

Coverage:
  1. test_top_level_field_inventory_matches -- live top-level per-key
     occurrence counts equal the frozen golden exactly; on mismatch the
     message names added, removed and count-changed keys separately.
  ...
```

### S-2. Self-contained path resolution — never in `conftest.py`

**Source:** `tests/test_chip_database_field_inventory.py:81-84` states the rule verbatim:

> *"Self-contained path resolution below — NOT in conftest.py, mirroring the firmware repo's own
> tests/ house rule (no shared path-resolution helper) so this module's target resolution is
> independently auditable."*

**Apply to:** all four new test modules. Two accepted spellings, both live in the tree:
`_FA_DIR = Path(__file__).parent.parent` (`test_sdp_db_invariant.py:74`,
`test_check_mypy_watermark.py:79`) and `_HERE/_APP_ROOT`
(`test_chip_database_field_inventory.py:93-94`).

### S-3. Env seams bind at import → set them in a CHILD PROCESS, never `monkeypatch`

**Source:** `tests/test_chip_database_field_inventory.py:44-51` + `:99-106`.
**Apply to:** every planted-violation leg in the D-13 transcripts.

```
Environment seams: FIRESTARTER_CHIP_DB_JSON and FIRESTARTER_BUILD_DB_SOURCE
override the database and generator targets respectively. Both bind at
import (module-level Path resolution below), so they must be set in a
child process environment, never monkeypatched.
```

And the deliberately non-overridable third path (`:103-106`) — the "unreachable leg" guard:

```python
# Deliberately NOT environment-overridable -- see "Generator scan scope"
# above. Always the real tree's supplement file, regardless of
# FIRESTARTER_BUILD_DB_SOURCE.
_EXTRA_CHIPS_PATH = _APP_ROOT / _EXTRA_CHIPS_REL
```

The gate that keeps a stray CI redirect RED rather than silently green
(`test_default_targets_resolve_inside_this_repository`, `:397-420`) is worth mirroring if a new
module adds its own env seam.

### S-4. Assertion messages name the offenders and say what a change MEANS

**Source:** `test_sdp_db_invariant.py:110-115`, `:277-284`, `:399-435`;
`test_chip_database_field_inventory.py:171-191` (`_describe_counter_diff`).
**Apply to:** every assertion in all four new modules.

Two rules: (a) collect `offenders` / `violations` and assert `not offenders` with the list in the
message — never `assert a == b` on a collection; (b) the message states what a failure *means*
("A count change means a chip moved between ALLOW and REFUSE and must be justified by a decode
reason, never a test-outcome reason").

The added/removed/changed splitter is directly reusable for the wire-dict and mover diffs
(`test_chip_database_field_inventory.py:171-191`):

```python
def _describe_counter_diff(recorded: dict, live: dict) -> str:
    """Explain a level-inventory mismatch by naming added, removed and
    count-changed keys SEPARATELY, each with its counts, rather than a bare
    "dicts differ"."""
    ...
    parts = []
    if added:
        parts.append(f"added={added}")
    if removed:
        parts.append(f"removed={removed}")
    if changed:
        parts.append(f"count_changed={changed}")
    return "; ".join(parts) if parts else "(no difference detected)"
```

### S-5. Every data gate carries a non-vacuity leg driving the SAME helper

**Source:** `test_sdp_db_invariant.py:337-370` and `:439+`; `test_chip_database_field_inventory.py:343-374`.
**Apply to:** `test_vcc_margin_rail.py`, `test_wire_dict_equivalence.py`, the source-scan module.

The rule as stated in-tree: *"Proves the invariant gate is capable of failing — not a vacuous
always-pass check … Exercises the exact same helpers the real-DB test above calls, not a parallel
reimplementation."*

### S-6. Citation format for any decode claim

**Source:** `tools/diff_db.py:42-44`; `tools/build_db.py:192`, `:140-159`.
**Apply to:** the `build_db.py` D-03 comment, the `diff_db.py` `RULE_VCC_MARGIN_RAIL` rationale,
and `148-DB-DIFF.md`.

- `[VERIFIED: minipro database.c#L130-L135 @ a8efaedc — tl866ii_vcc_voltages[]]` for an upstream
  source claim, with a full permalink on the next line inside `diff_db.py`.
- `[CITED: <in-repo path> §<section> "<quote>"]` for a datasheet or planning-doc claim.
- `[ASSUMED: …]` is **forbidden** in `_PAGE_SIZE_BY_PART`-adjacent code and by extension in any new
  decode rule ("DO NOT author [ASSUMED] values", `build_db.py:142`).

### S-7. Narrow `except` clauses — nothing lints a broad one

**Source:** `pyproject.toml` `[tool.ruff.lint] select = ["E", "F", "I", "UP"]`;
`build_db.py:416` WR-05 comment.
**Apply to:** every new/edited `except` in this phase. `BLE001` is not selected, so every
`# noqa: BLE001` in the repo is inert and `except Exception:` is gated by nothing. Keep excepts
narrow by hand and comment *why* the branch exists.

### S-8. Python-version floor for annotations

**Source:** `pyproject.toml` `target-version = "py39"` (CI pins 3.11; devcontainer runs 3.12).
**Apply to:** all new test modules.

`list[str]` / `tuple[str, dict]` / `dict[str, int]` are fine unquoted (PEP 585, 3.9+). `X | None`
is **not** — either add `from __future__ import annotations` (as
`test_check_mypy_watermark.py:67` and `test_dev_gate_reads_no_firmware_source.py:42` do) or quote
the annotation (as `test_chip_database_field_inventory.py:114`, `:234` do: `"Counter[str]"`,
`"set[str]"`). Import order is ruff-`I` enforced; `E501` is disabled (formatter owns width 88).

### S-9. Running the suite

**Source:** `pyproject.toml` `addopts = "-ra -q"`; VALIDATION.md.
**Apply to:** every `<automated>` verify block in every plan.

Always `python3 -m pytest <target> -o addopts="" -q`. A second `-q` **suppresses the count line**,
so a run that collected nothing looks identical to a run that passed. Full suite ≈ 280 s / 1616
tests — budget ≥ 600 s.

---

## No Analog Found

None. Every file in this phase has a working in-tree analog.

Two near-misses worth recording so a planner does not go looking:

| Thing | Why there is no analog | What to do instead |
|---|---|---|
| A *tolerant/legacy-schema reader* for the migrated keys | D-07 locks a clean break — no such reader exists anywhere in the tree, by design | Direct indexing per D-10; absent key ⇒ exception |
| A second golden JSON carrying a `meta` block | `chip_database_field_inventory.json` is the only one (`grep` verified) | It is therefore the sole convention source for `wire_dict_baseline.json` |

---

## Metadata

**Analog search scope:** `/workspaces/firestarter_app/tests/` (106 test modules),
`/workspaces/firestarter_app/tools/`, `/workspaces/firestarter_app/firestarter/`,
`/workspaces/firestarter_app/tests/golden/`, `/workspaces/firestarter_app/tests/__snapshots__/`
**Files read for extraction:** 18
**Firmware repo (`/workspaces/firestarter`):** out of scope, not searched
**Pattern extraction date:** 2026-08-19
**Tree state at extraction:** `firestarter_app` @ `9701209`, branch
`gsd/v1.32-at28c-write-path-root-cause-report-provenance`
