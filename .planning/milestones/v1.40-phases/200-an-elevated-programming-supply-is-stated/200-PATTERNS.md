# Phase 200: An elevated programming supply is stated - Pattern Map

**Mapped:** 2026-09-19
**Files analyzed:** 4 to be created/modified (+2 read-only context files)
**Analogs found:** 4 / 4

All paths below are in the `firestarter_app` sub-repo at `/workspaces/firestarter_app/`, on branch
`v1.40-program-parameter-fidelity`. Every analog named here was confirmed git-TRACKED with
`git ls-files` from inside that repo. No meta-repo source is touched; no firmware file is touched.

**Two corrections carried forward (do not map against stale text):**
1. `firestarter/eprom_presenter.py` **does not exist**. The renderer is `firestarter/eprom_info.py`.
   CONTEXT.md § Existing Code Insights cites the non-existent file; RESEARCH.md § G-2 documents it.
2. D-04's warning verb is **"decodes to"**, amended by the operator 2026-09-19. The RESEARCH.md
   § D / § Code Examples blocks written before the amendment still show "programs at" in places.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `firestarter/eprom_info.py` — injection block in `prepare_detailed_eprom_data` | presenter (data prep) | transform | **same file**, `eprom_info.py:138-147` (the `support_status` injection) | exact (in-file, 6 lines away) |
| `firestarter/eprom_info.py` — field row in `present_eprom_details` | presenter (render) | request-response | **same file**, `eprom_info.py:249-251` (the `VCC:` / `VPP:` rows) | exact |
| `firestarter/eprom_info.py` — warning block in `present_eprom_details` | presenter (advisory) | request-response | **same file**, `eprom_info.py:259-266` (`no_pinout_warning`) | exact |
| `tests/test_programming_vcc_census.py` (NEW; name is planner's call) | test (census/non-vacuity) | batch | `tests/test_vpp_rail_classification.py` (426 lines, Phase 199) | exact — structural template |
| `tests/test_characterization.py` + `tests/__snapshots__/test_characterization.ambr` | test (subprocess snapshot) | request-response | `test_info_at28c256` at `test_characterization.py:337-349`, snapshot at `.ambr:395-445` | exact |
| *(optional)* in-process warning assertion in `tests/test_cli_handlers.py` | test (CliRunner) | request-response | `test_info_chip_resolution_happy_path` at `tests/test_cli_handlers.py:106-117` | exact |
| `firestarter/database.py` | service (data access) | — | **READ-ONLY this phase.** Cited only for `format_mv` (`:115-122`) and to show `vdd_mv` is absent from the wire dict (`:527-536`). Do not modify. | n/a |

## Pattern Assignments

### `firestarter/eprom_info.py` — injection (presenter data-prep, transform)

**Analog:** the same file, `prepare_detailed_eprom_data`, lines 138-147. The new block goes
**immediately after** it.

**Imports pattern** (`eprom_info.py:10-18`) — `format_mv` is ALREADY imported; no new import needed,
and note there is **no `click` import in this module** (that is the argument against `click.echo`):

```python
import json
import logging
import re
from typing import Dict  # noqa: UP035

from firestarter.database import EpromDatabase, format_mv  # Changed import
from firestarter.ic_layout import EpromSpecBuilder  # Import renamed class

logger = logging.getLogger("EpromConsolePresenter")
```

**Gated-injection pattern to mirror** (`eprom_info.py:138-147`, VERBATIM):

```python
        # Inject support_status + unsupported_reason into combined_data for
        # non-supported chips. Gated on support_status != "supported"
        # so supported chips get no new line, which would be a snapshot regression.
        if raw_config_data:
            ss = raw_config_data.get("support_status", "supported")
            if ss != "supported":
                combined_data["support_status"] = ss
                combined_data["unsupported_reason"] = raw_config_data.get(
                    "unsupported_reason", ""
                )
```

The gate is the load-bearing part: it is simultaneously D-06's fail-open and the reason the 462
at-or-below-5000 rows keep byte-stable snapshots.

**Defensive coercion pattern** — copy from `firestarter/ic_layout.py:569-573`, the same shape
`build_specifications` uses for `vpp_mv` (analog in a different file, same idiom):

```python
        # Coerce defensively: user-override entries may supply vpp_mv as a string.
        try:
            _vpp_mv = int(eprom_data.get("vpp_mv", 0) or 0)
        except (TypeError, ValueError):
            _vpp_mv = 0
        if etype not in {"SRAM", "FRAM"} and _vpp_mv > 0:
```

Applied here: read `(raw_config_data.get("electrical") or {}).get("vdd_mv", 0) or 0` with chained
`.get()` (NOT `_map_data`'s direct indexing — RESEARCH.md § F-3), then `> _SHIELD_FIXED_VCC_MV`.
`_SHIELD_FIXED_VCC_MV = 5000` is a NEW module-level constant in `eprom_info.py`, **not** in
`constants.py` (that module is the firmware-mirror block, C-11).

**Voltage-string pattern** — never format mV inline. `firestarter/database.py:115-122`:

```python
def format_mv(mv: int) -> str:
    """Render a millivolt integer as the project's one human-facing voltage string.

    This is the single definition of the millivolt-to-human render used by every
    display call site (`ic_layout.py`'s `vcc_str`/`vpp_str` and `eprom_info.py`'s
    `vpp_str`). ...
    """
    return f"{mv / 1000:.1f}v"
```

---

### `firestarter/eprom_info.py` — field row (presenter render, request-response)

**Analog:** the same function, `present_eprom_details`, lines 232-257.

**Aligned-row pattern** (`eprom_info.py:232-257`, VERBATIM — note the single `pos` variable):

```python
        pos = 20  # For alignment
        logger.info(f"{'Eprom Info': <{pos}}{chip_data.get('verified_str', '')}")
        logger.info(f"{'Name:': <{pos}}{chip_data.get('name')}")
        logger.info(f"{'Manufacturer:': <{pos}}{chip_data.get('manufacturer')}")
        ...
        logger.info(f"{'VCC:': <{pos}}{chip_data.get('vcc_str')}")
        if "vpp_str" in chip_data:
            logger.info(f"{'VPP:': <{pos}}{chip_data.get('vpp_str')}")
        if "chip_id_hex" in chip_data:
            logger.info(f"{'Chip ID:': <{pos}}{chip_data.get('chip_id_hex')}")
        if "pulse_delay_us_str" in chip_data:
            logger.info(
                f"{'Pulse delay:': <{pos}}{chip_data.get('pulse_delay_us_str')}"
            )
```

Insert the new row between `VCC:` (`:249`) and the `if "vpp_str"` guard (`:250`), guarded by
`if "programming_vcc_str" in chip_data:`. `'Programming VCC:'` is 16 chars, inside `pos = 20`.

**ANTI-PATTERN in the same function — do NOT copy** (`eprom_info.py:238-244`). These two rows
hardcode their pad and land one column right of every `pos`-formatted row:

```python
        if chip_data.get("support_status"):
            support_status = chip_data["support_status"]
            logger.warning("Support status:      " + support_status)
            unsupported_reason = chip_data.get("unsupported_reason", "")
            if unsupported_reason:
                logger.warning("Reason:              " + unsupported_reason)
```

Fixing those two is **out of scope** — it would move the existing `test_info_*` snapshots and
destroy the zero-deletions gate (§E-1). File as backlog.

**Log level:** `logger.info` for the row (matches `VCC:`/`VPP:`; the subprocess snapshot pins it).

---

### `firestarter/eprom_info.py` — warning block (presenter advisory, request-response)

**Analog:** the same function, `no_pinout_warning`, lines 259-266. This is the in-repo shape
template VCC-02 generalises — it is non-refusing, `WARNING: `-prefixed, and already on this surface.

**Advisory-warning pattern** (`eprom_info.py:259-266`, VERBATIM):

```python
        if chip_data.get("no_pinout_warning"):
            logger.warning("")
            logger.warning(
                "WARNING: No pinout defined for this chip — hardware operations will fail."  # noqa: E501
            )
            logger.warning(
                "Add a pin-map entry to ~/.firestarter/pin-maps.json to enable it."
            )
```

Shape to copy exactly: **blank `logger.warning("")` separator → `WARNING: ` condition + consequence
→ a follow-on line stating what happens next.** D-04's wording is structurally identical.

**Mechanism:** `logger.warning`, measured to reach stdout at default verbosity with no level prefix
(`_setup_logging` sets root to INFO — `cli_handlers.py:103-123`). Do **not** use `click.echo`: all
10 `click.echo` sites live in `cli_handlers.py`, and `eprom_info.py` has no `click` import.

**Wording (amended D-04, use this verb):**
`WARNING: this part's programming supply decodes to <X>; the shield supplies a fixed 5.0 V.`
`Programming will be attempted at 5.0 V.`
Open point for the planner's human-verify checkpoint: prose `6.0 V` (space, capital V) versus the
row's `format_mv` `6.0v`.

---

### `tests/test_programming_vcc_census.py` (test, batch) — NEW

**Analog:** `tests/test_vpp_rail_classification.py` (426 lines). Structural drop-in.

**Imports + module constants pattern** (`test_vpp_rail_classification.py:91-110`, VERBATIM):

```python
import collections
import copy
import json
from pathlib import Path

_FA_DIR = Path(__file__).parent.parent
_DB_FILE = _FA_DIR / "firestarter" / "data" / "chip_database.json"

_VPP_CENSUS_FLOOR_MV = 18000

_ALGORITHM_TO_VPP_PATH = {
    0x07: "drop-resistor",
    0x08: "drop-resistor",
    0x0B: "direct-vpe",
}

_UNMAPPED_PATH_LABEL = "unmapped"

_EXPECTED_TOTAL_ROWS = 30
_EXPECTED_VOLTAGE_HISTOGRAM = {18000: 21, 21000: 3, 25000: 6}
_EXPECTED_PATH_HISTOGRAM = {"drop-resistor": 10, "direct-vpe": 20}
```

Phase 200's measured equivalents (all measured in RESEARCH.md §A-1/§A-2/§H):
`_SHIELD_FIXED_VCC_MV = 5000`, `_EXPECTED_TOTAL_ROWS = 284`,
`_EXPECTED_VDD_HISTOGRAM = {5500: 164, 6000: 8, 6250: 7, 6500: 105}`,
`_EXPECTED_ALGORITHM_HISTOGRAM = {7: 161, 8: 102, 11: 21}`,
`_EXPECTED_TYPE_HISTOGRAM = {"UV-EPROM": 284}`, `_EXPECTED_VENDOR_COUNT = 34`.

**Single-census-helper pattern** (`:112-135`, VERBATIM) — every test calls this one helper:

```python
def _load_db() -> dict:
    return json.loads(_DB_FILE.read_text(encoding="utf-8"))


def _all_chips(db: dict):
    for mfg, chips in db.items():
        for chip in chips:
            yield mfg, chip


def _census(db: dict):
    """Return `(rows, voltage_histogram, path_histogram, status_histogram)`
    ... The one census helper every test in this module
    calls, so a failure names which property moved rather than which
    reimplementation disagreed with which.
    """
    rows = [
        (mfg, chip)
        for mfg, chip in _all_chips(db)
        if chip.get("electrical", {}).get("vpp_mv", 0) >= _VPP_CENSUS_FLOOR_MV
    ]
```

Phase 200's predicate is **strictly above** (`> _SHIELD_FIXED_VCC_MV`), per D-03 — the opposite of
this module's at-or-above floor. The boundary test's naming must reflect that.

**Synthetic-row boundary pattern** (`:246-282`, VERBATIM excerpt) — this is how D-06's fail-open
cases get exercised, since the live DB has ZERO rows with absent/null/zero `vdd_mv` (§F-1) and C-1
forbids hand-editing the DB:

```python
def test_boundary_is_at_or_above_not_strictly_above() -> None:
    """The census filter is at-or-above the floor, not strictly above: a
    synthetic row one millivolt below the floor is excluded, and a
    synthetic row sitting exactly on the floor is counted.
    """
    below_floor = {
        "SYNTH": [
            {
                "part_number": "SYNTH-BELOW",
                "support_status": "supported",
                "electrical": {"vpp_mv": _VPP_CENSUS_FLOOR_MV - 1, "pin_count": 28},
                "programming": {"algorithm": 0x07},
            }
        ]
    }
    ...
    below_rows, _, _, _ = _census(below_floor)
```

Phase 200 cover set: key absent, `None`, `0`, exactly `5000`, `5001`.

**Non-vacuity deep-copy mutation pattern** (`:285-313`, VERBATIM) — the DB on disk is never written:

```python
def test_injecting_a_synthetic_row_makes_the_total_go_to_31() -> None:
    """Non-vacuity, defect class closed: a census helper that silently
    matched anything -- an empty row list, a swallowed exception, a filter
    that never selected -- would pass every other test in this module.
    ... The original database on disk is never written to.
    """
    db = _load_db()
    mutated = copy.deepcopy(db)
    manufacturer = next(iter(sorted(mutated)))
    mutated[manufacturer].append(
        {
            "part_number": "SYNTHETIC-THIRTY-FIRST-ROW",
            "support_status": "supported",
            "electrical": {"vpp_mv": _VPP_CENSUS_FLOOR_MV, "pin_count": 28},
            "programming": {"algorithm": 0x07},
        }
    )

    baseline_rows, _, _, _ = _census(db)
    mutated_rows, _, _, _ = _census(mutated)

    assert len(baseline_rows) == 30
    assert len(mutated_rows) == 31, (...)
```

**Source-shape guard pattern** (`:365-426`, VERBATIM) — note EVERY literal is `+`-joined:

```python
_REQUIRED_TEST_NAMES = (
    "test_row_total_and_voltage_histogram_match_post_override_state",
    ...
)

_DEFINITION_GUARD_COUNTS = {
    "_EXPECTED_TOTAL_ROWS" + " = 30": 1,
    "_EXPECTED_VOLTAGE_HISTOGRAM" + " = {18000: 21, 21000: 3, 25000: 6}": 1,
    "_EXPECTED_PATH_HISTOGRAM" + ' = {"drop-resistor": 10, "direct-vpe": 20}': 1,
    "=" + "= 30": 1,
    "=" + "= 31": 1,
}

_WEAKENING_IDIOMS = (
    "x" + "fail",
    "pytest.mark." + "skip",
    "issub" + "set",
    "firestarter" + "_fw",
    ">" + "= 30",
    ">" + "= 10",
    ">" + "= 20",
)


def test_module_source_shape_guards_against_weakening() -> None:
    """...Every entry in `_DEFINITION_GUARD_COUNTS` and `_WEAKENING_IDIOMS` above
    is assembled from two or more string fragments joined with `+`, rather
    than written as one contiguous literal. A guard written as one
    contiguous literal would count or match itself...
    """
    source = Path(__file__).read_text(encoding="utf-8")

    for name in _REQUIRED_TEST_NAMES:
        needle = "def " + name + "("
        assert needle in source, f"expected test {name!r} to exist by name"

    for literal, expected_count in _DEFINITION_GUARD_COUNTS.items():
        actual_count = source.count(literal)
        assert actual_count == expected_count, (...)

    for idiom in _WEAKENING_IDIOMS:
        assert idiom not in source, f"weakening idiom {idiom!r} found in module source"
```

**Module-docstring pattern:** the analog opens with a numbered "Coverage:" list, one entry per test
leg, plus named exceptions and a rationale for what the test can and cannot detect
(`:1-89`). Phase 200's module should carry the same, including the §F-2 sentence that the
fail-open branch is live via `~/.firestarter/database.json` overrides so a reviewer does not delete
it as dead code.

---

### `tests/test_characterization.py` + `.ambr` (test, request-response)

**Analog:** `test_info_at28c256`, `tests/test_characterization.py:337-349`.

**Snapshot-test pattern** (VERBATIM, `:337-349`) — note the paired `_stderr` snapshot:

```python
def test_info_at28c256(snapshot):
    """Pin info output for AT28C256 (Phase 148 DATA-01 criterion 1).

    This is the ONLY coverage criterion 1 ... has: no AT28C VCC line exists in any
    pre-existing snapshot ...
    """
    stdout, stderr, rc = run_firestarter("info", "AT28C256")
    assert rc == 0
    assert stdout == snapshot
    assert stderr == snapshot(name="test_info_at28c256_stderr")
```

**Harness note** (`:126-146`): `run_firestarter` shells out to `shutil.which("firestarter")` — the
entry point on PATH, not a venv python — with `FIRESTARTER_CONFIG_DIR` pointed at a clean dir. A
plan leg should ASSERT that PATH's `firestarter` resolves to `/workspaces/firestarter_app/firestarter/__init__.py`
rather than assume it (the sibling-worktree editable-install trap).

**Snapshot entry shape** (`.ambr:395-406`) — what the new entry will look like, with the new row
between `VCC:` and `VPP:`:

```
# name: test_info_at28c256
  '''
  Eprom Info          
  Name:               AT28C256,AT28C256E,...
  Manufacturer:       ATMEL
  Number of pins:     28
  Memory size         0x8000
  Type:               EEPROM
  Can be erased:      yes (electrically erasable)
  VCC:                5.0v
  VPP:                12.0v
```

Existing `info` snapshot entries live at `.ambr:395`, `:444`, `:447`, `:498`. Both existing chips
have `vdd_mv == 5000`, so **both stay byte-identical**; the change is purely additive.

**Scoped re-record pattern** (`.planning/phases/199-.../199-01-PLAN.md:203`, VERBATIM — adapt the
node id and the numstat expectation):

```bash
cd /workspaces/firestarter_app && .venv/ci-replica/bin/python -m pytest \
  "tests/test_characterization.py::test_list" -o addopts="" -q -p no:randomly \
  --snapshot-update >/dev/null 2>&1; \
  NS=$(git diff --numstat -- tests/__snapshots__/test_characterization.ambr) && \
  printf '%s\n' "$NS" && printf '%s\n' "$NS" | /usr/bin/grep -qP '^1\t1\t'
```

For Phase 200 the expectation is **insertions only, zero deletions**; a non-zero deletion count is
fail-closed. The leg must run on the UNCOMMITTED tree, before the commit.

---

### *(optional)* `tests/test_cli_handlers.py` (test, request-response)

**Analog:** `tests/test_cli_handlers.py:106-117`. Under CliRunner with `obj=app`, `_setup_logging`
is short-circuited and the root logger stays at pytest's `WARNING` — so **only the
`logger.warning` lines appear**, giving a clean assertion seam for the shortfall warning with no
field-row noise.

```python
def test_info_chip_resolution_happy_path(runner: CliRunner) -> None:
    """`firestarter info W27C512` resolves the chip and displays the layout.

    ... Injects a REAL EpromConsolePresenter(db) — Pitfall 1: the default Mock
    presenter returns None from prepare_detailed_eprom_data and masks the fix.
    """
    db = EpromDatabase(skip_local_override=True)
    app = make_app_context(db=db, eprom_presenter=EpromConsolePresenter(db))
    result = runner.invoke(cli, ["info", "W27C512"], obj=app)
    assert "not found in database" not in result.output
    assert result.exit_code == 0
```

Critical detail to copy: pass a **real** `EpromConsolePresenter(db)`, not the default Mock, or the
new code never runs. And `EpromDatabase(skip_local_override=True)` for hermeticity.

## Shared Patterns

### Constants placement
**Source:** RESEARCH.md C-11 / `firestarter/constants.py`
**Apply to:** the new `_SHIELD_FIXED_VCC_MV = 5000`
Module-level private constant in `eprom_info.py`. **Not** `constants.py` — that module is the
firmware-mirror block and this value has no firmware counterpart (D-07).

### Voltage rendering
**Source:** `firestarter/database.py:115-122` (`format_mv`)
**Apply to:** the field row, and the numbers in the warning prose
Already imported at `eprom_info.py:15`. Never an inline f-string.

### Logging as the only output channel
**Source:** `firestarter/eprom_info.py:232-266`
**Apply to:** both the row and the warning
`logger.info` for field rows, `logger.warning` for advisories. No `click`, no `print`.

### Fail-open coercion
**Source:** `firestarter/ic_layout.py:569-573`
**Apply to:** the `vdd_mv` read
`try: int(x or 0) except (TypeError, ValueError): 0`, then one `>` comparison collapses all four
D-06 cases.

### Exact counts, never floors, proved non-vacuous
**Source:** `tests/test_vpp_rail_classification.py` (whole module)
**Apply to:** the census test module
Equalities against `_EXPECTED_*` constants + planted-mutation legs + a `+`-joined source-shape guard.

### CI gates every changed Python file must pass
**Source:** `firestarter_app/CLAUDE.md` § What CI runs (RESEARCH.md C-2/C-3/C-4)
**Apply to:** every file this phase touches
`ruff check firestarter/ tests/` → `ruff format --check firestarter/ tests/` → `pytest tests/
--cov-fail-under=70`, on **Python 3.11** (`.venv311`, 3.11.16, or `.venv/ci-replica`). Ruff select
is `E,F,I,UP` with `E501` ignored — a `# noqa` outside that set is inert. `eprom_info.py` is **not**
on the mypy-strict list; `cli_handlers.py` is, which is a reason to keep the change out of it.

## No Analog Found

None. Every file in this phase has a same-role, same-data-flow analog, and three of the four
injection points have their analog **in the same function or six lines away**.

## Metadata

**Analog search scope:** `/workspaces/firestarter_app/firestarter/`,
`/workspaces/firestarter_app/tests/`, `/workspaces/firestarter_app/tests/__snapshots__/`
**Files scanned:** 8 read (`eprom_info.py`, `cli_handlers.py`, `database.py`, `ic_layout.py`,
`test_vpp_rail_classification.py`, `test_characterization.py`, `test_cli_handlers.py`,
`test_characterization.ambr`)
**Tracked-source gate:** all seven source/test paths confirmed via `git ls-files` inside
`firestarter_app`. No gitignored mirror path appears in this document.
**Pattern extraction date:** 2026-09-19
