# Phase 183: Flash4 Erase Refusal & the AE29F2008 Classification - Pattern Map

**Mapped:** 2026-09-11
**Files analyzed:** 7 (2 new, 5 modified) + 3 record-only edits
**Analogs found:** 6 / 7

> **Tracked-source gate:** every analog path below was verified with `git ls-files` inside its owning
> repository (meta / `firestarter` / `firestarter_app` submodules). No gitignored mirror paths appear.
>
> **HARD RULE — no comments in product source** (`/workspaces/CLAUDE.md`). Every C++ and Python excerpt
> quoted below is from a **heavily commented legacy file**. The comments are shown so the planner can see
> the reasoning; **new code must carry none of them**. Click docstrings in `firestarter_app` are
> user-facing `--help` text and are exempt. This applies to the new `flash4_erase_gate.py` module too:
> its module docstring and function docstrings are allowed; `#` comments are not.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `firestarter_app/firestarter/flash4_erase_gate.py` **(NEW)** | policy module (pure predicate) | transform (dict → bool/str) | `firestarter_app/firestarter/jp5_gate.py` | exact (with a stated polarity inversion) |
| `firestarter_app/tests/test_flash4_erase_gate.py` **(NEW)** | test | transform + CLI integration | `firestarter_app/tests/test_jp5_gate.py` | exact |
| `firestarter_app/firestarter/cli_handlers.py` (`erase`) | controller / CLI handler | request-response | the `jp5_gate` call already in the same function | exact (in-file) |
| `firestarter/src/proms/flash_5v_page.cpp` | firmware handler (dispatch + ops) | event-driven (fn-pointer dispatch) | `firestarter/src/proms/eeprom_28c.cpp` `configure_eeprom28c` | role-match |
| `firestarter/test/native/avr/test_val_5v_page/test_val_5v_page.cpp` | test (native AVR) | transform + bus recording | `firestarter/test/native/avr/test_val_nor_unlock/test_val_nor_unlock.cpp` | exact |
| `firestarter/scripts/check_erase_no_vpp.py` | gate script (docstring repair) | file-I/O source scan | `firestarter/tests/test_boolean_convention_source_contract_v133.py` | partial (citation discipline only) |
| `firestarter/tests/fixtures/planted_erase_no_vpp_ctrl_write.cpp` | test fixture (prose repair) | n/a | same as above | partial |
| `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md` (D-08, D-15) | record | n/a | — | no analog needed |

---

## Pattern Assignments

### `firestarter_app/firestarter/flash4_erase_gate.py` (NEW — policy module, pure predicate)

**Primary analog:** `firestarter_app/firestarter/jp5_gate.py` (154 lines, read in full)
**Secondary analog (for the reason-constant discipline):** `firestarter_app/firestarter/sdp_capability.py`

**Module-docstring + import-purity pattern** (`jp5_gate.py:1-38` — copy the *shape*, drop the hazard prose):

```python
"""
Project Name: Firestarter
Copyright (c) 2024 Henrik Olsson

Permission is hereby granted under MIT license.

<one-paragraph statement of what the policy is>

No I/O, no environment reads, no serial access -- the wire dict and the
operation name are the whole input, which is what makes the policy testable
without a board and keeps eprom_operations.py and cli_handlers.py free of
the reasoning.
"""

import sys
from typing import Any, Callable, Optional

from rich.prompt import Confirm

from firestarter.database import pin_conversions
from firestarter.exceptions import Pin1HazardRefusedError

SOCKET_PIN_1_BUS_LINE = pin_conversions[32][1]
GATED_ADDRESS_BIT = 19
DAMAGE_CAPABLE_OPERATIONS = frozenset({"write", "erase"})
```

**Copy from this:** the header block, the "no I/O / no serial" docstring clause, and module-level
frozen constants above the functions.
**Do NOT copy from this:** `import sys`, `rich.prompt.Confirm`, the `firestarter.exceptions` import, or
the `pin_conversions` import. RESEARCH §D.1 is explicit: this gate needs **no TTY logic, no prompt, no
exception type**. Aim instead at `sdp_capability.py`'s stricter purity —

`sdp_capability.py:17-24` (the purity statement, the model for the new module's head):
```python
from __future__ import annotations

# Import purity: the module's top-level import set is a subset of
# {"__future__", "typing"} — no click, no serial, no firestarter.* imports.
from typing import Any, Mapping  # noqa: UP035
```
(The `# noqa: UP035` is a real ruff directive, not commentary, and may be carried if `Mapping` is used.
Note the `#` prose lines above it must NOT be reproduced.)

**Protocol-constant pattern** — `sdp_capability.py:26-31` names its bucket as a module constant:
```python
SDP_PROTOCOL_ID = 13
```
New module: `FLASH4_PROTOCOL_ID = 0x05`. Define it **locally**, not by importing
`chip_test._PROTOCOL_FLASH4` (`chip_test.py:325`) — `chip_test.py` is not import-pure.

**Pure-predicate pattern** (`jp5_gate.py:58-66`):
```python
def is_affected(bus_config: Optional[dict]) -> bool:
    """True when socket pin 1 carries an address line at or above A19.

    The comparison is `>=`, not `==`: address-bit index is a genuinely
    ordered scale, ...
    """
    bit = socket_pin1_address_bit(bus_config)
    return bit is not None and bit >= GATED_ADDRESS_BIT
```
Shape to copy: single-argument `Optional[dict]` wire dict → `bool`, docstring states the rule and why the
comparison is the comparison it is, no side effects.

**⚠️ POLARITY IS INVERTED vs the analog — state this in the plan and in the docstring.**
`jp5_gate` is **fail-CLOSED** (`jp5_gate.py:50-54` and `:98-103`):
```python
    if not bus_config:
        return None
...
    if not bus_config or not bus_config.get("bus"):
        raise Pin1HazardRefusedError(
            f"{chip_name.upper()}: refusing to {operation} -- no bus "
            "configuration is available to prove socket pin 1 is safe, and "
            "absent evidence is never treated as safe."
        )
```
`sdp_capability` is likewise fail-closed (`sdp_capability.py:185-194` raises `KeyError` rather than
defaulting on a missing `protocol-id`).
**The new gate must fail-OPEN:** a missing/`None`/empty dict, or a missing `algorithm` key, means "we
cannot prove this is flash4", and refusing every unknown part would break `erase` for every chip.
RESEARCH §D.1/§D.3 recommended shape:
```python
def is_flash4(programmer_data) -> bool:
    if not programmer_data:
        return False
    return programmer_data.get("algorithm") == FLASH4_PROTOCOL_ID
```

**Message-constant pattern** (`sdp_capability.py:143-149` — copy this, not `jp5_gate.hazard_text`):
```python
# Reason-fragment constants — tests assert on these stable substrings rather
# than whole sentences.
REASON_NOT_FOUND = "not found in the chip database"
REASON_WRONG_PROTOCOL = "SDP lock/unlock applies only to protocol 0x0D parallel EEPROMs"
```
The D-07 one-liner goes behind a module constant / `refusal_text(chip_name)` so the test pins the shape,
not a whole sentence. `jp5_gate.hazard_text` (`:69-80`) is the f-string-builder shape to mirror
structurally, but its multi-clause text is exactly what D-07 forbids here.

**Which key to read — pinned by the call site, not by a second DB lookup:** `eprom_data["algorithm"]`
(`database.py:532`, mirrored from `protocol-id`) is already in the dict `resolve_chip` returns.
`sdp_capability.py:26-30`'s note ("never `algorithm` from `resolve_chip()`") is about the **`protocol-id`
key name**, not this value — do not let it mislead the implementation.

---

### `firestarter_app/firestarter/cli_handlers.py` — the `erase` handler (controller, request-response)

**Analog:** the `jp5_gate` call **already in this function** (`cli_handlers.py:871-883`, verbatim):

```python
    eprom_data = resolve_chip(eprom, db=app.db)

    if not jp5_gate.confirm_or_refuse(eprom, eprom_data.get("bus-config"), "erase"):
        sys.exit(1)

    ok = app.eprom_operator.erase_eprom(
        eprom,
        eprom_data,
        operation_flags=_build_op_flags(blank_check=blank_check, force=force),
        address_str=sector_address,
        pin1_hazard_acknowledged=True,
    )
    sys.exit(0 if ok else 1)
```

**Insertion point (D-02):** between `resolve_chip` (pure DB lookup, no serial) and
`app.eprom_operator.erase_eprom` (where the port opens) — i.e. beside the `jp5_gate` line. Pattern for
the new lines:
```python
    if flash4_erase_gate.is_flash4(eprom_data):
        click.echo(flash4_erase_gate.refusal_text(eprom))
        sys.exit(0 if ignore_unsupported else 1)
```

**Click option pattern** — copy from `erase`'s own existing options (`cli_handlers.py:834-841`):
```python
@click.option(
    "-b",
    "--blank-check",
    "blank_check",
    is_flag=True,
    default=False,
    help="Do a blank check after erase.",
)
```
New flag is **long-form only** (`erase` already binds `-f`, `-b`, `-s`): `--ignore-unsupported`,
`is_flag=True, default=False`.

**Docstring pattern** — the `erase` docstring (`cli_handlers.py:858-870`) is user-facing `--help` text and
is the **one place** the new flag's exit-code semantics get documented. It already uses this style:
```
    ``-b``/``--blank-check`` requests a blank check performed **after** the erase.
```
Add one sentence in that register. This is exempt from the no-comments rule.

---

### `firestarter_app/tests/test_flash4_erase_gate.py` (NEW — test)

**Analog:** `firestarter_app/tests/test_jp5_gate.py` (454 lines, 31 `def test_`).

**Docstring-enumerates-the-properties pattern** (`test_jp5_gate.py:1-27`):
```python
"""
Project Name: Firestarter
...
Phase 182 — socket-pin-1 (JP5/A19) destructive-operation gate (SAFE-01/02/04).

...Four things are proved here:

  1. `socket_pin1_address_bit` / `is_affected` / `require_acknowledged` -- the
     pure policy, covering every case a bus-config can present.
  2. The gate's coupling to the REAL database -- ...
  3. Integration through `EpromOperator.write_eprom` -- the refusal fires
     before `_operation_context` is ever entered.
  ...
  5. The affected-part set is DERIVED from `pinouts.json`, never hand-listed
     (SAFE-01, success criterion 2) ... and the module carries no literal
     8 Mbit part-number list.
"""
```

**Import block to copy** (`test_jp5_gate.py:29-51`) — `CliRunner`, `Mock`/`patch`, `EpromDatabase`, and
the named-symbol import from the module under test.

**Pure-predicate + parametrized-absent-evidence pattern** (`:71-91`):
```python
@pytest.mark.parametrize(
    "bus_config",
    [{}, None, {"bus": []}, NO_PIN1_BUS_CONFIG],
)
def test_socket_pin1_address_bit_absent_evidence_returns_none(bus_config):
    assert socket_pin1_address_bit(bus_config) is None
```
Reuse verbatim in shape for `{}`, `None`, missing-`algorithm` — but assert **False (fail-open)**, not a
raise.

**CLI-integration pattern — proves the refusal fires pre-connect (D-02)** (`:272-293`, the single most
important excerpt to copy):
```python
def _cli_app_context(eprom_operator):
    return AppContext(
        db=Mock(),
        config_manager=ConfigManager(),
        eprom_operator=eprom_operator,
        hardware_manager=Mock(spec=HardwareManager),
        firmware_manager=Mock(spec=FirmwareManager),
        eprom_presenter=Mock(spec=EpromConsolePresenter),
    )


def test_cli_erase_with_force_on_affected_part_still_refuses_off_tty():
    runner = CliRunner()
    eprom_operator = Mock(spec=EpromOperator)
    app = _cli_app_context(eprom_operator)
    with patch.object(
        cli_handlers,
        "resolve_chip",
        return_value={"bus-config": AFFECTED_BUS_CONFIG},
    ):
        result = runner.invoke(cli, ["erase", "DIP32_27C801", "-f"], obj=app)
    assert result.exit_code == 1
    eprom_operator.erase_eprom.assert_not_called()
```
`erase_eprom.assert_not_called()` **is** the D-02 proof. The `--ignore-unsupported` leg is the same body
with `exit_code == 0` and the same `assert_not_called()`.

**Derived-from-the-real-database pattern (D-4 — never a hand list)** (`:302-325`):
```python
def _derived_sets(db: EpromDatabase) -> tuple[set[str], set[str]]:
    structural = set()
    gated = set()
    for key in db.pin_maps:
        ...
    return structural, gated


def test_gated_set_over_the_real_shipped_data_is_exactly_dip32_27c801():
    db = EpromDatabase(skip_local_override=True)
    _structural, gated = _derived_sets(db)
    assert gated == {"DIP32_27C801"}
```
Adapt: iterate the real DB rows and assert the derived flash4 set equals
`{rows where programming.algorithm == 5}` — **27 rows** per RESEARCH §D.5.
`EpromDatabase(skip_local_override=True)` is mandatory (it is what keeps `~/.firestarter/database.json`
out of the assertion).

**Module-source scan pattern — "no part-number literal in the module"** — no such assertion exists in
`test_jp5_gate.py`; take it from `firestarter_app/tests/test_op_registration_parity.py:191-197`:
```python
def _module_source(module: Any) -> str:
    path = inspect.getsourcefile(module)
    assert path is not None, f"could not resolve a source file for {module!r}"
    return Path(path).read_text(encoding="utf-8")


_CHIP_TEST_SOURCE = _module_source(chip_test_mod)
```
Use it for the D-07 **negative** message assertions (`"write"`, `"self-eras"`, `"page"`, `"--force"` must
not appear in the rendered line) and for the no-literal-part-number check.

---

### `firestarter/src/proms/flash_5v_page.cpp` (firmware handler — three deletions, D-12)

**Analog for the post-deletion shape:** `firestarter/src/proms/eeprom_28c.cpp`, `configure_eeprom28c`
(`:136`ff). It is the file that already documents **why a missing arm is the correct shape**:

```c
void configure_eeprom28c(firestarter_handle_t* handle) {
    LOG_DEBUG_ID_SUB(DBG_CONFIGURING_EEPROM_28C);
    handle->pulse_delay = 0;
    switch (handle->cmd) {
        case CMD_WRITE:
            handle->firestarter_operation_init = eeprom28c_write_init;
            handle->firestarter_operation_main = eeprom28c_write_execute;
            break;
        case CMD_BLANK_CHECK:
            handle->firestarter_operation_main = mem_util_blank_check;
            break;
        ...
    }
}
```
Its comment block states the contract the post-deletion `configure_flash_5v_page` inherits:
*"Unsupported commands are refused generically by the operation layer's NULL-main guard instead"*
(`operation_utils.cpp:82`). **Do not reproduce that comment** in `flash_5v_page.cpp` — record the
rationale in the plan/SUMMARY instead.

**What the deletion removes** (`flash_5v_page.cpp:48-50`, verbatim):
```c
        case CMD_ERASE:
            handle->firestarter_operation_main = flash_5v_page_erase_execute;
            break;
```
plus the forward declaration at `:33` (`void flash_5v_page_erase_execute(firestarter_handle_t* handle);`
— RESEARCH §C.1's fourth site, which D-12's text does not name), the definition at `:193-225`, and the
erase-on-write block at `:79-85` (**not** `:80-86`).

**Analog for "an arm that survives untouched":** `flash_intel.cpp:50-70` `configure_flash_intel` keeps its
`CMD_ERASE` arm — the contrast that makes the deletion protocol-scoped, and the file to check against if
the planner is tempted to widen the edit.

**Analog for the empty-body disposition (RESEARCH §C.3 option (a), recommended):** `sram.cpp:15-17`:
```c
void configure_sram(firestarter_handle_t* handle) {
    LOG_DEBUG_ID_SUB(DBG_CONFIGURING_SRAM);
}
```
A configure function whose body is effectively a log line only is already precedent in this tree. Option
(b) (NULL init) has NULL-assignment precedent at `flash_5v_page.cpp:55`, `flash_intel.cpp:65`,
`not_implemented.cpp:14`, `memory.cpp:49` — but breaks `test_val_5v_page.cpp:332`'s unguarded
`h.firestarter_operation_init(&h)`.

---

### `firestarter/test/native/avr/test_val_5v_page/test_val_5v_page.cpp` (test — D-17 vacuity)

**Analog for the recommended replacement case:**
`firestarter/test/native/avr/test_val_nor_unlock/test_val_nor_unlock.cpp:144-152`, verbatim:

```c
/* configure-only: CMD_ERASE must record zero VPP-enable bits */
void test_nor_unlock_erase_configure_no_vpp(void) {
    firestarter_handle_t h = make_handle(CMD_ERASE);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,
        "configure_memory must not error on 0x06 CMD_ERASE");
    assert_no_vpp_in_recording(
        "configure_flash_nor_unlock CMD_ERASE must NOT set any VPP-enable CTL bit");
}
```
This is the **non-vacuous** shape the ERASE-02 third assertion degrades into after D-12: assert on
`configure_memory` + `CMD_ERASE` + `assert_no_vpp_in_recording`, keyed to a real dispatch outcome rather
than to a branch that no longer exists.

**The case being repaired** (`test_val_5v_page.cpp:327-358`) and its three assertions are analysed
case-by-case in RESEARCH §C.5 — keep assertions 1 and 2, re-point assertion 3, rename the case to drop
`with_flag_clear`.

**Prose citations to delete/re-point in the same file:** the NOTE at `:20-24` (names
`flash_5v_page_erase_execute`), the `flash_5v_page.cpp:80-86` citation at `:234` (already wrong — real
range is 79-85), and the five `flash_5v_page_write_init` mentions at `:225,231,317,336,355`.

---

### `firestarter/scripts/check_erase_no_vpp.py` (gate script — D-14 docstring repair)

**Analog for the citation discipline (symbol + enclosing scope, never a line number):**
`firestarter/tests/test_boolean_convention_source_contract_v133.py:56-57` and `:341-342`, verbatim:

```
     Asserted on the enclosing function name and the returned literal,
     never on a line number -- Phases 157 and 158 move this file again.
```
```python
    """Coverage 4 -- ... Asserted on the enclosing function name and the returned literal, never on a line
    number -- Phases 157/158 move this file again."""
    stripped = _strip_comments(_SCAN_WRAPPERS.read_text())

    erase_body = _extract_function_body(stripped, "eprom_erase")
```

**What to repair** (`check_erase_no_vpp.py:26-38`, verbatim — the stale citation *and* the rationale that
D-12 falsifies):
```
**Proximity, not absence, is the risk.** The hardware 12V-on-OE erase path
already exists in this tree today, at `firestarter/src/proms/flash_5v_page.cpp`
lines 196-231 (`flash_5v_page_erase_execute`, which asserts
`CTRL_VPE_ENABLE` and the VPP boost regulator around a `rurp_chip_enable()`
/ `rurp_chip_disable()` bracket) -- in the very file an executor also edits
during this phase (ERASE-02). Copying that shape into `eeprom_28c.cpp`'s
erase handler by mistake is exactly the failure mode this checker exists to
catch...
```
The file is 225 lines, so `lines 196-231` **cannot exist**. After D-12 the function does not exist either
— the rationale must be rewritten to say the copy-source hazard is gone while the gate stays armed.

**Keep intact:** the non-vacuity anchor block (`:60-70`) — it is scoped to `eeprom28c_erase_execute`'s
body (`handle->firestarter_set_data(` + `delay(AT28C_TEC_MAX_MS)`) and `--function` defaults to the `0x0D`
symbol, so the gate does **not** break functionally. Only the prose is false.

**Same two repairs, second and third site** (missed by CONTEXT, found by RESEARCH §C.4):
`firestarter/tests/fixtures/planted_erase_no_vpp_ctrl_write.cpp:15-17` carries the **identical impossible
citation**, and `:28` carries the provenance prose naming the function.

**Note:** this file is a `scripts/` gate, not product source. Its docstring is the artifact under repair;
the no-comments rule does not remove it, but no *new* `#` commentary should be added either.

---

## Shared Patterns

### Pure-policy-module contract (applies to `flash4_erase_gate.py`)
**Source:** `jp5_gate.py:20-23` (docstring clause) + `sdp_capability.py:18-19` (import purity)
```
No I/O, no environment reads, no serial access -- the wire dict and the
operation name are the whole input, which is what makes the policy testable
without a board and keeps eprom_operations.py and cli_handlers.py free of
the reasoning.
```
Exactly one deliberate deviation: **fail-open, not fail-closed** (see the module section).

### Pre-connect placement (applies to `cli_handlers.erase`)
**Source:** `cli_handlers.py:873`
```python
    if not jp5_gate.confirm_or_refuse(eprom, eprom_data.get("bus-config"), "erase"):
        sys.exit(1)
```
**Apply to:** the new gate — same slot, after `resolve_chip`, before `app.eprom_operator.*`.

### Exit-code shape
**Source:** `cli_handlers.py:883` — `sys.exit(0 if ok else 1)`. The new refusal mirrors the idiom as
`sys.exit(0 if ignore_unsupported else 1)`; the printed line is identical on both legs (D-06).

### Test-file structure for a policy module
**Source:** `tests/test_jp5_gate.py` — properties enumerated in the module docstring, pure-predicate
parametrized cases, a `_derived_sets`-style real-database coupling test, and one `CliRunner` +
`Mock(spec=EpromOperator)` integration test whose assertion is `*.assert_not_called()`.

### Citation discipline (symbol + enclosing scope)
**Source:** `firestarter/tests/test_boolean_convention_source_contract_v133.py:56-57`
**Apply to:** every prose repair in this phase — `check_erase_no_vpp.py`, the planted fixture,
`test_val_5v_page.cpp`, `firestarter/CLAUDE.md:118-120`, `firestarter/PROTOCOLS.md:110`.

### NO COMMENTS IN PRODUCT SOURCE
**Source:** `/workspaces/CLAUDE.md` § "Source code comments — hard rule"
**Apply to:** all new/edited lines under `firestarter/src/`, `firestarter/include/`, and
`firestarter_app/firestarter/`. Every analog quoted in this document is legacy-commented; the comments
are context, not licence. Docstrings (module, function, Click) are not comments.

---

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| `.planning/REQUIREMENTS.md` / `.planning/ROADMAP.md` (D-08, D-15) | record | n/a | Record amendments, not code; no codebase analog applies. |
| SAFE-09 verdict (D-19/D-20 branch) | record | n/a | RESEARCH §B settles it with **no code change** — no `build_db.py` rule, no regeneration, no `chip_database.json` diff. The `RULE_PHASE182_A19_PINOUT` analog in `build_db.py` is **not** needed because D-21's branch does not fire. |
| `firestarter/tests/fixtures/{planted,clean}_no_heap_or_64bit_symbols_*/avr-nm-uno.txt` | frozen fixture | n/a | Historical `avr-nm` dumps naming `flash_5v_page_erase_execute`. **Must stay byte-unchanged** — there is no "update" pattern to follow, and applying one would be the defect. |

## Metadata

**Analog search scope:** `firestarter_app/firestarter/`, `firestarter_app/tests/`, `firestarter/src/proms/`,
`firestarter/scripts/`, `firestarter/tests/`, `firestarter/test/native/avr/`
**Files read this session:** `jp5_gate.py` (full), `sdp_capability.py` (head + predicate), `cli_handlers.py`
(`blank`/`erase` region), `test_jp5_gate.py` (docstring, pure-predicate, CLI, derived-set legs),
`test_op_registration_parity.py` (source-scan helper), `flash_5v_page.cpp` (declarations + configure),
`flash_intel.cpp`, `eeprom_28c.cpp` (configure), `sram.cpp`, `memory.cpp`/`eprom.cpp` (configure shapes),
`test_val_5v_page.cpp` (NOTE, ERASE-02 factory + case), `test_val_nor_unlock.cpp` (configure-only cases),
`check_erase_no_vpp.py` (docstring), `test_boolean_convention_source_contract_v133.py` (citation rule)
**Tracked-source verification:** `git ls-files` run in both submodules over all 13 analog paths — all tracked.
**Pattern extraction date:** 2026-09-11
