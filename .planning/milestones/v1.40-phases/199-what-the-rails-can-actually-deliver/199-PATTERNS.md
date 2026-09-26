# Phase 199: What the rails can actually deliver — Pattern Map

**Mapped:** 2026-09-18
**Files analyzed:** 12 (5 new host/test files, 5 modified host files, 2 new `.planning/` artifacts)
**Analogs found:** 12 / 12
**Repo:** host-only. Every source path below is relative to `/workspaces/firestarter_app` (the
submodule). `.planning/` paths are relative to `/workspaces`.

**Tracked-source gate:** every analog named below was verified with `git ls-files` inside its own
repository. No path here is a gitignored mirror.

---

## Correction to the orchestrator's starting hypothesis

The hypothesis table is correct in all but two respects, both settled by RESEARCH.md:

1. **The `info` surface should NOT be `eprom_info.py`.** RESEARCH § D20 measured two insertion
   points and recommends **(A) `cli_handlers.info`**, immediately after
   `eprom_data_for_programmer = app.db.convert_to_programmer(...)` (`cli_handlers.py:485`), because
   `eprom_info.py` is a snapshot-pinned render path and touching it risks moving
   `test_info_known_chip[...stderr]` as well as `test_list`. `eprom_info.py`'s
   `Support status:` / `Reason:` block (lines 239–244) remains the **voice and level analog**
   (`logger.warning`, fixed-width label) but is **not necessarily a modified file**. Treat
   `eprom_info.py` as "analog, optionally modified".
2. **`eprom_operations.py` is NOT modified.** RESEARCH § D19 measured the only injection point as
   the `vpe_as_vpp=vpe_as_vpp` keyword already present in `cli_handlers.py:781`. `build_flags`'s
   signature is pinned by `tests/test_bug_characterization.py` (BUG-1) and must not move.
   `eprom_operations.py` is a **read-only reference**, not a target.

Everything else in the hypothesis holds, and two files must be added to it:
`.planning/phases/199-…/199-REGEN-DIFF.md` (one-row instance of `197-REGEN-DIFF.md`) and the
bench record, which per RESEARCH § A6 goes in the **phase directory**, not under
`.planning/milestones/v1.40-artifacts/` (that directory is the close's to make).

---

## File Classification

| New/Modified | File | Role | Data Flow | Closest Analog | Match |
|---|---|---|---|---|---|
| NEW | `firestarter/<rail>_gate.py` | policy module (pure) | transform | `firestarter/flash4_erase_gate.py` | exact |
| NEW | `tests/test_<rail>_gate.py` | test | transform | `tests/test_flash4_erase_gate.py` | exact |
| NEW | `tests/test_vpp_rail_classification.py` | test (census over generated DB) | batch/read-only | `tests/test_build_db_inclusion.py`, `tests/test_b15_page_size_corroboration.py` | exact |
| NEW | `tests/golden/wire_dict_expected_deltas_199.json` | fixture | data | `tests/golden/wire_dict_expected_deltas_198.json` | exact |
| MODIFIED | `tools/datasheet_overrides.json` | config/data | data | its own `FUJITSU/MBM27C1001` sibling entry | exact |
| MODIFIED | `firestarter/cli_handlers.py` (`write` + `info`) | controller / CLI | request-response | the three existing gate call sites at `cli_handlers.py:766-771` | exact |
| MODIFIED | `tests/test_wire_dict_equivalence.py` | test | batch | its own 197 and 198 layer legs | exact |
| MODIFIED | `tools/DECODE-NOTES.md` § 10 | documentation | — | § 9 (VOLT-01) | exact |
| MODIFIED | `tests/__snapshots__/test_characterization.ambr` | snapshot | — | the 197-04 one-line re-record | exact |
| REFERENCE only | `firestarter/eprom_info.py` | presenter | request-response | its own `Support status:` block | n/a |
| NEW | `.planning/phases/199-…/199-GH71-ANSWER.md` | doc | — | `197-GH70-ANSWER.md` | exact |
| NEW | `.planning/phases/199-…/199-BENCH-RECORD.md` + `199-REGEN-DIFF.md` | doc | — | `v1.18-artifacts/bench/hold_rail.py`, `197-REGEN-DIFF.md` | exact |

---

## Pattern Assignments

### `firestarter/<rail>_gate.py` (policy module, pure transform) — NEW

**Analog:** `firestarter/flash4_erase_gate.py` (79 lines, read in full). It is the newest and
simplest of the three precedents, and it is the right one because **it raises nothing** — the
caller decides. D-13's "this module never refuses" maps onto that split exactly.

**COMMENTS:** `flash4_erase_gate.py` contains **zero** `#` comments (its only `#` is
`# noqa: UP035` on an import, which is a linter directive, not a comment). All of its policy
prose lives in the **module docstring and per-function docstrings**, which CLAUDE.md permits.
Copy that arrangement literally: the new module must carry **no `#` line at all** beyond a
`noqa` directive if one is genuinely needed.

**Header + docstring pattern** (`flash4_erase_gate.py:1-36`) — the four-line MIT block, a blank
line, a one-line subject, then policy prose:

```python
"""
Project Name: Firestarter
Copyright (c) 2024 Henrik Olsson

Permission is hereby granted under MIT license.

Flash4 (protocol 0x05) erase-refusal policy.

The 0x05 firmware path does not implement a chip erase for the flash4
protocol class -- a real hardware limitation, not a database misclassification
...
Like `jp5_gate.py` and `sdp_capability.py`, this is a pure predicate: no I/O,
no environment reads, no serial access -- a wire dict is the whole input,
which is what keeps the policy testable without a board and keeps
`eprom_operations.py` and `cli_handlers.py` free of the reasoning.

The one deliberate deviation from both of those precedents: this gate FAILS
OPEN. ... Absence of evidence is treated as "not flash4" rather than as
"not provably safe".
"""
```

Three things to copy verbatim in structure: (a) the purity sentence — D-13 is quoting it;
(b) the **polarity paragraph**, which every one of the three precedents carries and which
*argues against the opposite choice by name*; (c) the single-sourcing paragraph
(`FLASH4_PROTOCOL_ID` … "cannot drift apart") — here it becomes the argument that the warned
condition and the routed condition are one predicate (D-09).

**Polarity for THIS gate: FAIL OPEN.** `page_size_gate.py:33-39` is the counter-precedent and
shows how to word the contrast:

```python
The polarity here is the deliberate OPPOSITE of `flash4_erase_gate.is_flash4`.
That gate fails open on absent evidence, because guessing wrong there merely
breaks availability. Here, guessing wrong risks silently destroying an
operator's chip, so absent or zero evidence about the page size is treated
as "not provably safe", never as "probably fine".
```

The new module's version of this paragraph must say: absent `vpp_mv` ⇒ no warning, no routing,
because failing closed would **raise a rail** on every part the predicate cannot classify.
*Absent evidence must never raise a rail.*

**Imports + module constants pattern** (`flash4_erase_gate.py:38-44`):

```python
from __future__ import annotations

from typing import Any, Mapping  # noqa: UP035

FLASH4_PROTOCOL_ID = 5

_REFUSAL_FORMAT = "Erase not supported for {chip_name}"
```

Operation-scoping frozenset, from `jp5_gate.py:39`:

```python
DAMAGE_CAPABLE_OPERATIONS = frozenset({"write", "erase"})
```

**Predicate pattern** (`flash4_erase_gate.py:47-68`) — docstring carries the polarity argument,
body is three lines:

```python
def is_flash4(programmer_data: Mapping[str, Any] | None) -> bool:
    """True when the wire dict's `algorithm` value is the flash4 protocol id.
    ...
    Returns False for a missing, `None`, or empty `programmer_data`, and for
    a dict carrying no `algorithm` key at all. ...
    """
    if not programmer_data:
        return False
    return programmer_data.get("algorithm") == FLASH4_PROTOCOL_ID
```

**Text-builder pattern** (`flash4_erase_gate.py:71-82`) — the format string is module-level so a
test can assert an exact shape:

```python
def refusal_text(chip_name: str) -> str:
    """The one-line, cause-free refusal text.

    Built from `_REFUSAL_FORMAT` rather than assembled inline, so a test can
    assert the exact shape instead of a whole sentence. ...
    """
    return _REFUSAL_FORMAT.format(chip_name=chip_name.upper())
```

Note `chip_name.upper()` — the house voice uppercases the part number.

**Message voice** — copy the shape of `cli_handlers.py:755-764`'s warn-and-proceed block, whose
closing clause is already RAIL-03's "and the operation still proceeds":

```python
            "flag to skip; each page write applies directly. The family "
            "does have a standalone erase, reachable as `firestarter "
            "erase`, which this flag does not affect. Proceeding with a "
            "normal write."
```

Extracted pattern: `{CHIP NAME UPPERCASED}: <measured fact>. <what the tool is doing>.
<what happens next>.` Em dashes for parenthetical cause; no exclamation; no advice the tool
cannot back. Forbidden per D-15/D-16: any pot target, any "this will/will not work", any wording
distinguishing the rescuable ten from the unreachable eight.

**Threshold constant:** a module constant with a `<bench-measured>` placeholder until the bench
plan fills it, every function taking `deliverable_mv` as a parameter defaulting to it. Precedent
for naming a hardware-derived figure explicitly: `page_size_gate`'s `_ACCEPTED_PAGE_SIZES` and its
docstring's citation of `firestarter_fw/src/proms/flash_5v_page.cpp`. **No plan may write `18000`
before the DMM reading exists** (D-07/D-08).

---

### `tests/test_<rail>_gate.py` (test) — NEW

**Analog:** `tests/test_flash4_erase_gate.py`.

**Docstring `Coverage:` list** (lines 1-34) — the numbered list names each test *and the defect
class it closes*. This is where the honesty limits go (docstring, permitted):

```python
"""
Project Name: Firestarter
Copyright (c) 2024 Henrik Olsson

Permission is hereby granted under MIT license.

Flash4 (protocol 0x05) erase-refusal gate.

Coverage:
  1. THE PURE PREDICATE -- `is_flash4` parametrized over every `algorithm`
     value the shipped database actually contains: ...
  2. FAIL-OPEN -- a missing, `None`, or empty wire dict, or one with no
     `algorithm` key, returns False rather than raising or refusing. This
     polarity is deliberately inverted against `jp5_gate` and
     `sdp_capability`, which both fail CLOSED on absent evidence.
  3. COUPLING TO THE REAL DATABASE -- ... driven through `resolve_chip`
     against `EpromDatabase(skip_local_override=True)` ...
  4. NO PART-NUMBER LITERAL IN THE MODULE -- no shipped `part_number` string
     occurs anywhere in `flash4_erase_gate.py`'s source, docstrings included ...
  5. THE MESSAGE SHAPE -- ... a forbidden-substring list ...
  6. NOT A BLANKET REFUSAL -- ...
"""
```

**Import block + board-free fixture** (lines 36-67) — the `Mock(spec=…)` `AppContext` is what
makes it board-free:

```python
import inspect
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from firestarter import cli_handlers
from firestarter.cli_handlers import AppContext, cli
from firestarter.config import ConfigManager
from firestarter.database import EpromDatabase
from firestarter.eprom_info import EpromConsolePresenter
from firestarter.eprom_operations import EpromOperator
from firestarter.firmware import FirmwareManager
from firestarter.hardware import HardwareManager


def _cli_app_context(eprom_operator):
    return AppContext(
        db=Mock(),
        config_manager=ConfigManager(),
        eprom_operator=eprom_operator,
        hardware_manager=Mock(spec=HardwareManager),
        firmware_manager=Mock(spec=FirmwareManager),
        eprom_presenter=Mock(spec=EpromConsolePresenter),
    )
```

**Prefer `tests/conftest.py`'s shared `make_app_context` / `app_context` factory** (Phase 132,
RETIRE-05) over hand-rolling a fourth `_cli_app_context` — RESEARCH § D18 names it as the
supersession.

**Message-shape test with a forbidden-substring list** (tail of the file):

```python
FORBIDDEN_REFUSAL_SUBSTRINGS = (
    "force", "firestarter write", "write", "workaround", "route around",
    "because", "reason", "cause", "alternative", "instead", "try",
)


def test_refusal_text_is_one_line_and_carries_no_forbidden_content():
    """THE MESSAGE SHAPE: exactly one line, names the chip, and carries none
    of a forbidden-substring list ... A NEGATIVE assertion on purpose -- it is
    what stops a later executor quietly re-adding the cause clause ...
    """
    text = refusal_text("ae29f2008")

    assert "\n" not in text
    assert text == "Erase not supported for AE29F2008"

    lowered = text.lower()
    for forbidden in FORBIDDEN_REFUSAL_SUBSTRINGS:
        assert forbidden not in lowered, (
            f"refusal text {text!r} contains forbidden substring {forbidden!r}"
        )
```

For this phase the forbidden list must include pot wording (D-15) and any wording that
distinguishes "VPE rescues this" from "nothing rescues this" (D-16).

**"Operation still proceeds" leg** — the critical inversion of the last test in the analog. Copy
the structure but assert the warning **and** the call in the same test:

```python
def test_cli_erase_on_non_flash4_part_still_reaches_operator():
    """NOT A BLANKET REFUSAL: ... Without this leg, a fail-closed regression
    in the FAIL-OPEN group would pass every other test in this file."""
    runner = CliRunner()
    eprom_operator = Mock(spec=EpromOperator)
    eprom_operator.erase_eprom.return_value = True
    app = _cli_app_context(eprom_operator)
    with patch.object(
        cli_handlers, "resolve_chip",
        return_value={"algorithm": 13, "bus-config": NO_PIN1_BUS_CONFIG},
    ):
        result = runner.invoke(cli, ["erase", "AM28C16A"], obj=app)

    assert result.exit_code == 0
    eprom_operator.erase_eprom.assert_called_once()
```

New-file version: `patch.object(cli_handlers, "resolve_chip", return_value={"vpp_mv": 21000, …})`,
invoke `["write", …]`, assert the shortfall text is in `result.output` **and**
`eprom_operator.write_eprom.assert_called_once()`. That single test is RAIL-03's proof.

**Also copy:** the no-part-number-literal test (`_module_source` via `inspect.getsourcefile` +
`Path.read_text`), and the database-driven parametrization idiom
(`@pytest.mark.parametrize` over values derived from `EpromDatabase(skip_local_override=True)`),
so the test never hardcodes the measured threshold either.

---

### `tests/test_vpp_rail_classification.py` (census test) — NEW

**Analogs:** `tests/test_build_db_inclusion.py` (its stated framing: *"loads
chip_database.json directly (not via EpromDatabase)"*) and
`tests/test_b15_page_size_corroboration.py` (the path-constant idiom):

```python
_DB_FILE = _FA_DIR / "firestarter" / "data" / "chip_database.json"
```

Use the direct `json.load` route — the claim is about the **generated artifact**, not about what
`EpromDatabase` resolves.

**The one thing with no analog to copy:** the algorithm→VPP-path mapping. It exists only in
`firestarter_fw/src/proms/eprom_params.cpp`, which is **not in `firestarter_app`'s CI checkout**
(no `submodules:` key on `actions/checkout@v4`). Encode it as a module constant and state the
limit in the module docstring:

```python
_ALGORITHM_TO_VPP_PATH = {0x07: "drop-resistor", 0x08: "drop-resistor", 0x0B: "direct-vpe"}
```

Docstring must say it is a deliberate mirror, that the host has no access to the firmware table,
and **that this test therefore detects a database-side change only**. Do not scan firmware source
— project memory records that such gates fail OPEN in CI while passing in the devcontainer.

**Exact-count assertions, never "at least":** `len(rows) == 30`,
`Counter(mv) == {18000: 21, 21000: 3, 25000: 6}` **post-override** (pre-override it is
`{18000: 22, 21000: 2, 25000: 6}` — sequence this task after the override task),
`Counter(path) == {"drop-resistor": 10, "direct-vpe": 20}`, and all rows `supported`.

---

### `tests/golden/wire_dict_expected_deltas_199.json` — NEW

**Analog:** `tests/golden/wire_dict_expected_deltas_198.json` (read in full). Two top-level keys,
`meta` carrying exactly five string keys:

```json
{
  "deltas": {
    "FUJITSU|MBM27C1001|7": { "vpp_mv": 12500 },
    "FUJITSU|MBM27C4001|12": { "vpp_mv": 12500 }
  },
  "meta": {
    "decision": "Phase 198: tests/golden/wire_dict_baseline.json is preserved byte-unchanged. This file is the committed, reviewable expected-delta list ... on the same terms as the 197 layer, the golden itself is never re-captured or re-baselined to make this phase's change disappear.",
    "honesty": "This layer records only that these two records' vpp_mv wire value moved ... It does not by itself establish that 12500 is electrically correct -- the figure was read visually from a datasheet page, not measured on a bench. ...",
    "how_to_update": "This layer is regenerated by the same script against the live database and never edited by hand. ...",
    "phase": "198-the-two-voltage-nibbles",
    "provenance": "... Generated programmatically from the live capture against the committed golden plus the 149, 153, 182, 194 and 197 delta layers -- never transcribed by hand, since the |<i> record-key suffix is a positional index within each manufacturer's list and would silently rot if any row is ever added or reordered."
  }
}
```

199's instance holds **exactly one** delta: `"FUJITSU|MBM27128|2": {"vpp_mv": 21000}`. It shares
its record key with the 197 layer and stays composable only because `vpp_mv` ≠ `pulse-delay`
(field-disjoint). **Generate it, never hand-transcribe** — the `|<i>` suffix is positional.

---

### `tools/datasheet_overrides.json` — MODIFIED

**Analog:** the entry's own siblings `FUJITSU/MBM27C1001` and `FUJITSU/MBM27C4001`, which already
use the `electrical.vpp_mv` field path. The existing entry (lines 51-58):

```json
  "FUJITSU/MBM27128": {
    "datasheet": "datasheets/MBM27128.pdf",
    "note": "Figure 3, the Quick Pro flow chart on page 4-20, specifies TPW = 1 ms +/- 50 us with VCC = 6V +/- 0.25V, VPP = 21V +/- 0.5V and an X = 20 pulse ceiling. ...",
    "fields": {
      "programming.pulse_duration_us": { "was": 200, "is": 1000 },
      "electrical.vdd_mv": { "was": 5500, "is": 6000 }
    }
  },
```

One line added inside `fields`, placed per sibling ordering (`programming.*` first, then
`electrical.vpp_mv`, then `electrical.vdd_mv`):

```json
      "electrical.vpp_mv": { "was": 18000, "is": 21000 }
```

`_EXPECTED_ENTRY_COUNT = 22` / `_EXPECTED_UNSOURCED_COUNT = 18` in
`tests/test_datasheet_overrides.py` **do not move** — this adds a field, not an entry. That is a
real difference from Plan 198-01, which had to bump both.

---

### `firestarter/cli_handlers.py` — MODIFIED (two sites)

**Analog:** the existing gate call sites, `cli_handlers.py:766-771`:

```python
    if not jp5_gate.confirm_or_refuse(eprom, eprom_data.get("bus-config"), "write"):
        sys.exit(1)
    page_size_gate.require_page_size(eprom, eprom_data, "write")
    page_size_gate.require_page_alignment(
        eprom, eprom_data, "write", address, input_file
    )
```

Note the convention: **a call in `cli_handlers`, the reasoning in the module, the operation name
passed as a literal string.**

**`write` injection point** — immediately after the block above, before `write_eprom`
(`cli_handlers.py:773-784`), leaving the existing `vpe_as_vpp=vpe_as_vpp` keyword untouched:

```python
    ok = app.eprom_operator.write_eprom(
        eprom,
        eprom_data,
        input_file,
        address_str=address,
        operation_flags=_build_op_flags(
            blank_check=blank_check,
            force=force,
            vpe_as_vpp=vpe_as_vpp,
            skip_erase=skip_erase,
            skip_sdp_unlock=skip_sdp_unlock,
        ),
```

New code goes above it and only ever **raises** the flag, so `--vpe-as-vpp` survives as a manual
override (D-11) and `build_flags`'s signature — pinned by `test_bug_characterization.py` BUG-1 —
never moves. **Do not add a second defence-in-depth layer in `eprom_operations.write_eprom`** the
way `jp5_gate.require_acknowledged` does; it would emit the warning twice.

**Output call:** `click.echo` on `write` (not `logger.info`), matching
`flash4_erase_gate`'s caller and the two existing warn-and-proceed blocks. The source's own stated
reason, at the `--skip-erase` and `--pulse-us` blocks: *"this must be visible at DEFAULT verbosity,
with no -v needed."*

**`info` injection point** (`cli_handlers.py:480-489`) — immediately after the wire dict lands:

```python
def info(app: AppContext, eprom: str, config: bool, adapter: bool) -> None:
    """EPROM info."""
    eprom_details = app.db.get_eprom(eprom)
    if not eprom_details:
        logger.error(f"EPROM '{eprom}' not found in database.")
        sys.exit(1)

    eprom_data_for_programmer = app.db.convert_to_programmer(eprom_details)
    raw_config_data, manufacturer = app.db.get_eprom_config(eprom)
```

Use `logger.warning` here (`logger = logging.getLogger("Firestarter")`), matching the
`Support status:` level D-14 names. `info` does not go through `resolve_chip`, so it works for
every row including non-`supported` ones.

**Voice/level analog, not necessarily modified — `eprom_info.py:238-244`:**

```python
        if chip_data.get("support_status"):
            support_status = chip_data["support_status"]
            logger.warning("Support status:      " + support_status)
            unsupported_reason = chip_data.get("unsupported_reason", "")
            if unsupported_reason:
                logger.warning("Reason:              " + unsupported_reason)
```

**Comment warning:** the three lines immediately above this block in `eprom_info.py` (236-238) are
`#` comments. They are **pre-existing**. If the planner takes option (B) and edits this region,
any staged `+`-prefixed `#` line — including a reflowed pre-existing comment — trips CLAUDE.md's
pre-commit check. This is a second, independent argument for option (A).

---

### `tests/test_wire_dict_equivalence.py` — MODIFIED

**Analog:** its own 197 and 198 layer handling. The module docstring states the rule:

> *"A future phase adding a SEVENTH layer should add a seventh delta file and a seventh set of legs
> here, rather than editing any existing delta file or folding a seventh layer's entries into one of
> these six."*

Four obligations, each named by that docstring: (1) extend the composition test name and legs to
include 199 with `len(deltas_199) == 1` exact, not "at least"; (2) add the pairwise
field-disjointness check — the **199-with-197** pair is the one that matters; (3) compose 199 into
`test_exactly_84_records_change_flags_and_no_other_field_moves`, or the count floats to 85;
(4) add `test_the_199_delta_layer_is_capable_of_failing`, mirroring tests 8/9/10.

---

### `tools/DECODE-NOTES.md` § 10 — MODIFIED

**Analog:** § 9 (VOLT-01, Phase 198). Its shape, in order: a bolded one-sentence **Verdict**; a
"What the decode does today" paragraph with inline `` [VERIFIED: <source> @ <sha>] `` provenance
markers; a positive-confirmation paragraph; a falsification-of-the-rival-reading paragraph; and
the carve-out/limit paragraphs. § 6 "Honest gaps" is the template for the named limits.

§ 10 must carry: the 25 V figure's theoretical status, the measured per-rail figures with method,
the paired ADC error, the 30-row classification table, the D-06 approximation disclosure
(pin-1 VPE figure applied to pin-21 rows across a different routing bit), the D-12 posture note,
and the C14 limit (the classification test detects database-side change only).

**Honesty-limit voice model** — `diagnostic_report.py`'s `_RAIL_READING_DISCLOSURE`:

> `vpp/vpe readings measure the regulator rail only -- they do not show whether the eprom socket is connected`

---

### `tests/__snapshots__/test_characterization.ambr` — MODIFIED

**Analog:** the 197-04 single-line re-record precedent. Exactly one line moves, line 757 inside
`# name: test_list`:

```
  | MBM27128            | FUJITSU          |   28 |            | UV-EPROM    | 18.0v|
```

`18.0v` → `21.0v`. Expected `git diff --numstat` is `1  1` (198's was `2 2`). Zero lines means the
override never applied; more than one pair means a blanket regeneration swept in drift.

---

### `.planning/phases/199-…/199-GH71-ANSWER.md` — NEW

**Analog:** `.planning/phases/197-…/197-GH70-ANSWER.md`. Five sections in order: `## Status`,
`## Internal provenance (project bookkeeping only — do not post)`, `## Comment Body`,
`## Held-pending deferral (internal — do not post)`. That last section is **the single
consolidated list** (D-20); gh#71 joins gh#70 and gh#66 there. Its four sub-bullets are
`What is held` / `Why` / `What releases the hold` / (the fourth, the posting steps). Add gh#71
to the existing list in `197-GH70-ANSWER.md` — do not start a second list.

### `.planning/phases/199-…/199-REGEN-DIFF.md` and `199-BENCH-RECORD.md` — NEW

**Analogs:** `197-REGEN-DIFF.md` (ten-part shape; collapses to a one-row instance: 746 in /
746 out / 1 changed / 0 `support_status` moved) and
`.planning/milestones/v1.18-artifacts/bench/hold_rail.py` (git-tracked, verified) plus
`.planning/milestones/v1.34-artifacts/PROCEDURE.md` § "Standing bench rules".
**Write bench evidence to the phase directory**, not `.planning/milestones/v1.40-artifacts/` —
that directory belongs to the close.

---

## Shared Patterns

### Module docstring instead of comments
**Source:** `firestarter/flash4_erase_gate.py` (zero `#` comments; ~36 lines of docstring).
**Apply to:** every new `.py` file in this phase, and to `_ALGORITHM_TO_VPP_PATH`'s honesty limit.
CLAUDE.md's hard rule forbids `#`, `//`, `/* */` in product source for any reason. Docstrings are
explicitly permitted; Click docstrings are `--help` text, not commentary.
Pre-commit check: `git -C firestarter_app diff --cached -- '*.py' | /usr/bin/grep -E '^\+\s*#' | /usr/bin/grep -v '^\+\s*#!'` must print nothing.

### The polarity paragraph
**Source:** `flash4_erase_gate.py:22-30` and `page_size_gate.py:33-39`.
**Apply to:** the new gate module and its test. Both precedents state the polarity AND argue
against the opposite by naming the sibling module. The new gate's polarity is **fail open**, and
the test must carry a dedicated polarity test whose docstring argues with a future reader.

### Single-sourcing shared values
**Source:** `page_size_gate.py` imports `FLASH4_PROTOCOL_ID` from `flash4_erase_gate`;
`jp5_gate.py` derives `SOCKET_PIN_1_BUS_LINE = pin_conversions[32][1]`.
**Apply to:** keep ONE predicate and derive both the warning condition and the routing condition
from it, so they cannot drift (D-09).

### Board-free CLI testing
**Source:** `tests/test_flash4_erase_gate.py` — `CliRunner()`,
`patch.object(cli_handlers, "resolve_chip", return_value={...})`, `Mock(spec=…)` `AppContext`.
**Apply to:** both new test modules that exercise a CLI path. Prefer `tests/conftest.py`'s
`make_app_context` / `app_context` fixture over a fourth local copy.

### CI-replica Python
**Apply to:** every pytest/mypy verify leg. Use `.venv/ci-replica/bin/python` (3.11.16), never
bare `python`/`python3` (devcontainer default is 3.12 and has broken beta CI before). Pass
`-o addopts=""` (project `addopts` is `-ra -q`; doubling `-q` hides the count line) and
`-p no:randomly` for determinism.

### Exact counts, never "at least"
**Source:** `tests/test_wire_dict_equivalence.py`'s non-vacuity legs;
`tests/test_datasheet_overrides.py`'s `_EXPECTED_ENTRY_COUNT`.
**Apply to:** the 30-row census test and the 199 delta layer's `len(...) == 1` leg.

---

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| the `_ALGORITHM_TO_VPP_PATH` mapping inside `tests/test_vpp_rail_classification.py` | test constant | — | `vpp_path` / `VPP_PATH_*` has **zero** occurrences anywhere in `firestarter/`, `tests/` or `tools/`. The concept exists only in `firestarter_fw/src/proms/eprom_params.cpp`, which is absent from the app's CI checkout. Mirror it in the test module with a docstring-stated limit; do not scan firmware source. |

Everything else has a tracked in-repo analog.

---

## Metadata

**Analog search scope:** `/workspaces/firestarter_app/{firestarter,tests,tools}`,
`/workspaces/.planning/{phases,milestones}`.
**Files read for excerpts:** `flash4_erase_gate.py` (full), `jp5_gate.py` (1-60),
`page_size_gate.py` (1-45), `test_flash4_erase_gate.py` (1-70 + tail 60),
`eprom_info.py` (230-250), `cli_handlers.py` (478-500, 760-790, grep index),
`wire_dict_expected_deltas_198.json` (full), `DECODE-NOTES.md` § 9,
`197-GH70-ANSWER.md` (§ Held-pending deferral).
**Tracked-source verification:** `git ls-files` run inside `/workspaces/firestarter_app` and
`/workspaces`; all 11 source/test/tool analogs and `hold_rail.py` returned tracked.
**Pattern extraction date:** 2026-09-18
