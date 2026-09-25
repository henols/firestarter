# Phase 203: The write guard moves up a layer - Pattern Map

**Mapped:** 2026-09-21
**Files analyzed:** 9 (1 new product module, 5 modified product modules, 1 new test module, 2 modified test/snapshot artifacts)
**Analogs found:** 8 / 9 (one has no in-repo analog — see § No Analog Found)

All paths are relative to `/workspaces`. Every product path below was confirmed git-tracked
inside the `firestarter_app` submodule (`git ls-files` from `/workspaces/firestarter_app`).

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `firestarter_app/firestarter/<new>_gate.py` (NEW — blank-guard predicate, D-06) | pure predicate module (5th sibling) | transform (dict in → decision/text out) | `firestarter_app/firestarter/flash4_erase_gate.py` | exact (same input, same refusal-constant shape; opposite polarity) |
| `firestarter_app/firestarter/exceptions.py` (MOD — new refusal exception) | model / exception type | — | `PageSizeUnavailableError` / `PageAlignmentError` in the same file | exact |
| `firestarter_app/firestarter/eprom_operations.py` (MOD — guard call in `write_eprom`, `--verify` drive) | service / operator | request-response over serial | `verify_eprom` (`:2400-2460`), `_drive_region_compare` (`:2230-2333`) | exact |
| `firestarter_app/firestarter/compare.py` (MOD — additive `first_actual`) | service / data model | streaming transform | the existing `first_offset` capture in `CompareAccumulator.feed` tier-3 | exact |
| `firestarter_app/firestarter/cli_handlers.py` (MOD — `write` gains `--verify`/`--full`, exit contract) | controller (Click command) | request-response | the `verify` command (`:906-966`) + `map_typed_errors` (`:192-233`) | exact |
| `firestarter_app/firestarter/address_parser.py` or `page_size_gate.py` (MOD — negative address, folded todo) | utility / pure gate | transform | `require_page_alignment`'s `ValueError`→`PageAlignmentError` idiom | exact |
| `firestarter_app/tests/test_<new>_gate.py` (NEW) | test (board-free pinning) | — | `firestarter_app/tests/test_flash4_erase_gate.py` | exact |
| `firestarter_app/tests/test_write_blank_guard.py` (NEW — host-path + ordering) | test (fake-serial harness) | request-response | `_drive_write_eprom_for_ack_check` (`tests/test_eprom_operations.py:2244`) + `test_region_end_emitted_on_write` (`:393`) | role-match (WRITE path only; see No Analog) |
| `firestarter_app/tests/__snapshots__/test_characterization.ambr` (MOD — 2 help blocks) | test fixture | — | the two existing byte-identical blocks (lines 363-415, 1394-1446) | exact |

## Pattern Assignments

### `firestarter/<new>_gate.py` — the fifth sibling (pure predicate, transform)

**Analog:** `firestarter_app/firestarter/flash4_erase_gate.py` (read in full).

**Module docstring shape** (`flash4_erase_gate.py:1-35`) — four required movements, in this order:
title, *why this policy exists at all*, *why it is a pure predicate*, *why its fail polarity is what
it is*, *which constant it single-sources*:

```python
"""
Project Name: Firestarter
Copyright (c) 2024 Henrik Olsson

Permission is hereby granted under MIT license.

Flash4 (protocol 0x05) erase-refusal policy.
...
Like `jp5_gate.py` and `sdp_capability.py`, this is a pure predicate: no I/O,
no environment reads, no serial access -- a wire dict is the whole input,
which is what keeps the policy testable without a board and keeps
`eprom_operations.py` and `cli_handlers.py` free of the reasoning.

The one deliberate deviation from both of those precedents: this gate FAILS
OPEN. `jp5_gate.require_acknowledged` and `sdp_capability` both refuse when
their input cannot prove a part is safe, because guessing wrong there risks
hardware damage or a corrupted write. Here, guessing wrong in the same
direction ... would instead break `erase` ..., which is an availability
regression, not a safety one.

`FLASH4_PROTOCOL_ID` is the same `algorithm` value
`database.convert_to_programmer`'s `algo not in (5,)` exclusion reads when it
clears `FLAG_CAN_ERASE`, so this predicate and that flag derivation share one
source of truth and cannot drift apart.
"""
```

**Convention to match:** the new module writes the *mirror* of that fourth paragraph — it fails
CLOSED, and must name `flash4_erase_gate`'s opposite polarity explicitly, exactly as
`page_size_gate.py:33-38` already does for its own case:

```python
# page_size_gate.py:33-38
The polarity here is the deliberate OPPOSITE of `flash4_erase_gate.is_flash4`.
That gate fails open on absent evidence, because guessing wrong there merely
breaks availability. Here, guessing wrong risks silently destroying an
operator's chip, so absent or zero evidence about the page size is treated
as "not provably safe", never as "probably fine".
```

**Import block + constant reuse** (`flash4_erase_gate.py:37-43`; the `from … import` line is
`page_size_gate.py:52`):

```python
from __future__ import annotations

import os
from typing import Any, Mapping  # noqa: UP035

from firestarter.address_parser import parse_address
from firestarter.constants import JSON_KEY_PAGE_SIZE
from firestarter.exceptions import PageAlignmentError, PageSizeUnavailableError
from firestarter.flash4_erase_gate import FLASH4_PROTOCOL_ID
```

`# noqa: UP035` on the `typing.Mapping` import is **live** (`ruff` select is `E,F,I,UP`) and must be
carried if the same import form is used.

**Refusal-as-format-constant** (`flash4_erase_gate.py:43,68-79`) — D-12's exact shape:

```python
_REFUSAL_FORMAT = "Erase not supported for {chip_name}"


def refusal_text(chip_name: str) -> str:
    """The one-line, cause-free refusal text.

    Built from `_REFUSAL_FORMAT` rather than assembled inline, so a test can
    assert the exact shape instead of a whole sentence. Carries no cause
    clause, no alternative command, and no mention of the `--force`
    forged-identity workaround -- an operator who reads a cause here could
    route around a correct refusal ...
    """
    return _REFUSAL_FORMAT.format(chip_name=chip_name.upper())
```

The new module's format constant carries `{chip_name}`, `{address}` and `{value}` (D-10) and keeps
the no-remedy property; the `.upper()` on the chip name is the house style at all three sites
(`flash4_erase_gate:79`, `page_size_gate:125`, `jp5_gate:101`).

**Predicate keyed on `algorithm` only, with its reasoning at the site** (`flash4_erase_gate.py:46-65`):

```python
def is_flash4(programmer_data: Mapping[str, Any] | None) -> bool:
    """True when the wire dict's `algorithm` value is the flash4 protocol id.

    The comparison is against `algorithm`, not `flags & FLAG_CAN_ERASE`. The
    flag is also clear for UV-EPROM and SRAM parts that have no erase
    command of any kind, so a flag-based predicate would silently widen this
    refusal past its flash4-only scope ...
    """
    if not programmer_data:
        return False
    return programmer_data.get("algorithm") == FLASH4_PROTOCOL_ID
```

**Hard-fail on a key the wire dict does not carry** — the pattern RESEARCH §4.2.1 names as mandatory.
Source: `firestarter_app/firestarter/sdp_capability.py:186-195`:

```python
    if "protocol-id" not in entry:
        raise KeyError(
            f"sdp_capability_for_entry: entry for {display_name.upper()!r} has no "
            "'protocol-id' key. This is very likely the *programmer* dict "
            "returned by resolve_chip()/convert_to_programmer(), which carries "
            "neither 'protocol-id' nor 'name' — pass the full dict returned by "
            "db.get_eprom() instead. A silent default here is exactly how "
            "check_eprom_blank's _SRAM_PROTO_IDS short-circuit became vacuous "
            "in production (RESEARCH F-06); this predicate hard-fails instead."
        )
```

**Convention:** the new predicate may read `algorithm` / `flags` / `memory-size` and nothing else.
Any other key must be a `raise KeyError` in this shape, never `.get(key, default)`.

**Raise-on-refusal guard function** (`page_size_gate.py:99-133`) — the shape for
`require_blank(...)` if the exception route is chosen; note the guard-clause early returns *before*
any work, and the refusal built from the format constant:

```python
def require_page_size(
    chip_name: str,
    programmer_data: Mapping[str, Any] | None,
    operation: str,
) -> None:
    """The fail-closed, pre-connect guard. Raises on refusal, returns on pass.
    ...
    This is the fail-CLOSED direction, the opposite of
    `flash4_erase_gate.is_flash4`'s documented fail-open polarity ...
    """
    if operation not in _WRITE_OPERATIONS:
        return
    if not requires_page_size(programmer_data):
        return
    page_size = (programmer_data or {}).get(JSON_KEY_PAGE_SIZE)
    if not page_size:
        raise PageSizeUnavailableError(
            _REFUSAL_FORMAT.format(chip_name=chip_name.upper())
        )
```

Compare `jp5_gate.require_acknowledged` (`jp5_gate.py:97-107`) for the fail-closed
absent-evidence arm the new module's D-05 polarity follows:

```python
    if operation not in DAMAGE_CAPABLE_OPERATIONS:
        return
    if not bus_config or not bus_config.get("bus"):
        raise Pin1HazardRefusedError(
            f"{chip_name.upper()}: refusing to {operation} -- no bus "
            "configuration is available to prove socket pin 1 is safe, and "
            "absent evidence is never treated as safe."
        )
```

`frozenset` module constants for the operation/id sets: `page_size_gate.py:54`
(`_WRITE_OPERATIONS = frozenset({"write"})`), `jp5_gate.py:38`
(`DAMAGE_CAPABLE_OPERATIONS = frozenset({"write", "erase"})`) — the guarded protocol-id set takes
this same form.

---

### `firestarter/exceptions.py` (model) — the new refusal exception

**Analog:** `PageSizeUnavailableError` / `PageAlignmentError`, `exceptions.py:92-115`. Subclass
`EpromOperationError`; the docstring states *who raises it*, *what it happens before*, and *why
absent evidence is not safe*:

```python
class PageSizeUnavailableError(EpromOperationError):
    """Raised when a protocol 0x05 write targets a chip with no recorded page size.

    Fired by page_size_gate.require_page_size before any wire dict reaches the
    transport and before any serial byte is emitted — the host will not drive
    hardware for a protocol 0x05 chip whose page size is unknown. A guessed
    page size on this protocol destroys data in both directions, so absent
    evidence is never treated as safe.
    """

    pass
```

**Convention:** a new arm must be added to `map_typed_errors` **above** the generic
`EpromOperationError` arm, or the message is rendered with a `"Programmer error: "` prefix.
Source `cli_handlers.py:222-227`:

```python
        except PageSizeUnavailableError as e:
            raise click.ClickException(str(e)) from e
        except PageAlignmentError as e:
            raise click.ClickException(str(e)) from e
        except EpromOperationError as e:
            raise click.ClickException(f"Programmer error: {e}") from e
```

`ClickException.exit_code == 1` — this route delivers exit 1 only (RESEARCH §7.B). Exit 2 must be a
return value.

---

### `firestarter/eprom_operations.py` — `write_eprom` (service, request-response)

**Analog for the guard's placement:** the existing pure-gate block in the same function,
`eprom_operations.py:2115-2134`. Excerpt, verbatim, including the comment style D-08's insertion
must match:

```python
        require_acknowledged(
            eprom_name,
            eprom_data_dict.get("bus-config"),
            "write",
            pin1_hazard_acknowledged,
        )
        require_page_size(eprom_name, eprom_data_dict, "write")
        require_page_alignment(
            eprom_name, eprom_data_dict, "write", address_str, input_file_path
        )

        # BLANK-01 / D-05: guarded so a missing file keeps surfacing exactly
        # where it does today (_main_phase_send_data, after connecting, for
        # non-0x05 parts that require_page_alignment returns early for)
        # rather than moving earlier. An unguarded getsize would change that
        # ordering, which this plan is not authorised to do.
        try:
            region_length = os.path.getsize(input_file_path)
        except OSError:
            region_length = None

        with self._operation_context(
            eprom_name,
            eprom_data_dict,
            COMMAND_WRITE,
            operation_flags,
            address_str,
            region_length=region_length,
        ) as (cmd_data, buf_size, op_name):
            if not cmd_data:
                return False
```

**Convention:** the guard goes between the `except OSError` block and the `with
self._operation_context(...)` line. Its comment carries the D-01/D-03/D-05 reasoning at the site
(comments in source are permitted again).

**The verdict-line shape D-14 must suppress** (`:2222-2229`):

```python
            if is_ok:
                logger.info(
                    f"Write to {eprom_name.upper()} successful ({time.time() - start_time:.2f}s)."  # noqa: E501
                )
            else:
                logger.error(f"Write to {eprom_name.upper()} failed.")
            return is_ok
```

**Analog for a `_drive_region_compare` call site** — `verify_eprom`, `eprom_operations.py:2421-2460`.
This is the exact shape the guard read and `--verify` both copy: open a **COMMAND_READ**
`_operation_context`, build the pull callback, call, then map the verdict:

```python
        with self._operation_context(
            eprom_name,
            eprom_data_dict,
            COMMAND_READ,
            operation_flags,
            address_str,
            resolved_size_str,
        ) as (cmd_data, _, op_name):
            if not cmd_data:
                return 2

            logger.info(f"Verifying {input_file_path} against {eprom_name.upper()}")
            start_time = time.time()
            region_start = cmd_data.get("address", 0)

            try:
                with open(input_file_path, "rb") as file_handle:

                    def _expected(offset: int, length: int) -> bytes:
                        file_handle.seek(offset - region_start)
                        return file_handle.read(length)

                    verdict = self._drive_region_compare(
                        cmd_data,
                        op_name,
                        _expected,
                        full=full,
                        region_length=region_length,
                    )
            except IOError as e:  # noqa: UP024
                logger.error(f"File I/O error with {input_file_path}: {e}")
                return 2

            if verdict == 0:
                logger.info(
                    f"Verify for {eprom_name.upper()} successful ({time.time() - start_time:.2f}s)."  # noqa: E501
                )
            else:
                logger.error(f"Verify for {eprom_name.upper()} failed.")
            return verdict
```

For the guard, the pull callback is the already-module-level
`_blank_expected_bytes` (`eprom_operations.py:332-341`) instead of the file-seeking closure.

**`_drive_region_compare` — full signature and the render call site that D-11 must gate**
(`:2230-2237` and `:2318-2322`):

```python
    def _drive_region_compare(
        self,
        cmd_data: dict,
        op_name: str,
        expected: Callable[[int, int], bytes],
        *,
        full: bool,
        region_length: int | None,
    ) -> int:
```

```python
        result = accumulator.finalise(aborted=aborted)
        if region_length is not None:
            result.total = region_length
        for line in render_compare_lines(result):
            logger.info(line)
```

Its docstring (`:2239-2254`) is the standing one-compare-drive rule and states the
"deliberately does not log a caller-specific success/failure line" convention — the new
keyword-only switch must be additive and keep `verify`/`blank` byte-identical by default, matching
the existing keyword-only (`*,`) parameter style.

---

### `firestarter/compare.py` — the additive `first_actual` field

**Analog:** the existing `first_offset` capture in the tier-3 branch of `CompareAccumulator.feed`
(`compare.py:245-247`), the field declaration beside it (`:147-150`), and the `finalise()` kwarg list
(`:315-327`):

```python
        offs = [o for o in range(chunk_len) if expected[o] != actual[o]]
        if not offs:
            self._close_open_range()
            return

        if self._first_offset is None:
            self._first_offset = address + offs[0] - self._addr_base
        self._bad += len(offs)
```

```python
    first_offset: int | None = None
    """Offset of the first mismatching byte, relative to the accumulator's
    `addr_base` -- `None` when `bad == 0`. Matches the batch
    `classify_fingerprint`'s `evidence["first_offset"]` exactly (202-03)."""
```

```python
            aborted=aborted,
            ff_count=self._ff_count,
            first_offset=self._first_offset,
            bit_set_counts=dict(self._set_count),
        )
```

**Conventions to match:** every `CompareResult` field carries its own docstring paragraph naming the
decision it implements; the assignment goes inside the existing tier-3 `if self._first_offset is
None:` branch (adding no `for` loop, so `test_fast_path_precedes_per_offset_loop`'s AST gate holds);
`compare.py` is on the mypy strict list, so the field needs a full annotation.

---

### `firestarter/cli_handlers.py` — `write` gains `--verify` / `--full` (controller)

**Analog for the `--full` option declaration and the exit contract:** the `verify` command,
`cli_handlers.py:919-966`:

```python
@click.option(
    "--full",
    is_flag=True,
    help="Report every mismatching range, not just the first.",
)
@click.pass_obj
@map_typed_errors
def verify(
    app: AppContext,
    eprom: str,
    input_file: str,
    address: str | None,
    size: str | None,
    force: bool,
    full: bool,
) -> None:
    """Verifies the content of an EPROM.

    Exits 0 on a match, 1 on a mismatch, 2 on a transport, hardware, setup,
    or region failure. The three are distinct: a transport failure is not
    reported as a mismatch, and a region refusal -- an explicit --size
    longer than the input file, or a region running past the chip's end --
    is reported before the serial port ever opens.
    ...
    """
    eprom_data = resolve_chip(eprom, db=app.db)
    refusal = _region_refusal_exit_code(
        eprom=eprom,
        eprom_data=eprom_data,
        address=address,
        size=size,
        input_file=input_file,
    )
    if refusal is not None:
        sys.exit(refusal)
    verdict = app.eprom_operator.verify_eprom(...)
    sys.exit(verdict)
```

**Conventions:** the 0/1/2 contract is stated in the docstring's **first paragraph** (that docstring
is user-facing `--help`); the pre-port region refusal runs before the operator call;
`sys.exit(verdict)` on the raw int — no re-mapping.

**How `write` currently ends** (`cli_handlers.py:775-793`):

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
        pulse_us=pulse_us or 0,
        pin1_hazard_acknowledged=True,
    )
    sys.exit(0 if ok else 1)
```

**Analog for a new pre-port region refusal helper** (if `--verify` needs one):
`_region_refusal_exit_code` (`cli_handlers.py:796-902`) — returns `int | None`, always `2` on
refusal, `None` to proceed, refuses with `click.echo` (not `logger`), and its docstring explains why
a malformed address is deliberately *not* its job:

```python
    if mem_size is not None and start >= mem_size:
        click.echo(
            f"{eprom.upper()}: refused -- the start address 0x{start:X} is "
            f"at or past this chip's declared size (0x{mem_size:X})."
        )
        return 2
```

**Option-block style for a warning-carrying option** — `write`'s own `--skip-erase`
(`cli_handlers.py:583-592`) is the precedent for D-13's mandated "this changes the exit contract"
sentence living in the `help=` string:

```python
@click.option(
    "--skip-erase",
    "skip_erase",
    is_flag=True,
    default=False,
    help="Also skip the pre-write erase (for already-blank or non-erasable/pre-erased parts). "
    "WARNING: skipping erase on a non-blank electrically-erasable chip leaves un-erased bits "
    "that cannot be reprogrammed.",
)
```

**Docstring sentence to rewrite** (`cli_handlers.py:651-653`, mirrored verbatim in both `.ambr`
blocks):

> On protocols 0x0D and 0x05 the write path performs no pre-write blank
> check at all, so -b is a no-op on those families and is not needed to
> write a non-blank part. It remains effective on every other protocol.

---

### `firestarter/address_parser.py` / `page_size_gate.py` — the folded negative-address todo

**Current state** (`address_parser.py:11-18`) — a two-line function with no sign check; both callers'
error contracts hang on `ValueError`:

```python
def parse_address(s: str | None) -> int | None:
    """Parse a hex or decimal address string.

    Returns None for None input. Raises ValueError on bad format.
    """
    if s is None:
        return None
    return int(s, 16) if "0x" in s.lower() else int(s)
```

**Analog for the refusal, whichever site is chosen** — `require_page_alignment`'s
parse-then-translate idiom (`page_size_gate.py:160-182`), which is the established way this repo
turns a bad address into a named, pre-connect refusal:

```python
    try:
        start = parse_address(address_str) or 0
    except ValueError as e:
        raise PageAlignmentError(
            f"{chip_name.upper()}: could not parse address {address_str!r}"
        ) from e
    ...
    if start % page_size != 0 or length % page_size != 0:
        raise PageAlignmentError(
            _ALIGNMENT_REFUSAL_FORMAT.format(
                chip_name=chip_name.upper(),
                page_size=page_size,
                start=start,
                length=length,
            )
        )
```

**Convention:** `raise … from e`, a format constant for the sentence, `chip_name.upper()`, and the
refusal fires before any wire dict is built.

---

### `tests/test_<new>_gate.py` — the board-free pinning test

**Analog:** `firestarter_app/tests/test_flash4_erase_gate.py` (read in full). It is the only test in
the suite that asserts a **whole refusal sentence** and a **whole output line list**.

**Module docstring = a numbered coverage map** (`:1-35`):

```python
"""
...
Coverage:
  1. THE PURE PREDICATE -- `is_flash4` parametrized over every `algorithm`
     value the shipped database actually contains: True for 5, False for
     every other value present.
  2. FAIL-OPEN -- a missing, `None`, or empty wire dict ...
  3. COUPLING TO THE REAL DATABASE -- the set of part numbers for which the
     predicate fires, driven through `resolve_chip` against
     `EpromDatabase(skip_local_override=True)`, is exactly the set of
     shipped rows whose `programming.algorithm` is 5.
  4. NO PART-NUMBER LITERAL IN THE MODULE ...
  5. THE MESSAGE SHAPE ...
  6. NOT A BLANKET REFUSAL ...
"""
```

**Whole-sentence refusal assertion + forbidden-substring negative** (`:196-232`) — D-12's test shape:

```python
FORBIDDEN_REFUSAL_SUBSTRINGS = (
    "force", "firestarter write", "write", "workaround", "route around",
    "because", "reason", "cause", "alternative", "instead", "try",
)


def test_refusal_text_is_one_line_and_carries_no_forbidden_content():
    text = refusal_text("ae29f2008")

    assert "\n" not in text
    assert text == "Erase not supported for AE29F2008"

    lowered = text.lower()
    for forbidden in FORBIDDEN_REFUSAL_SUBSTRINGS:
        assert forbidden not in lowered, (
            f"refusal text {text!r} contains forbidden substring {forbidden!r}"
        )
```

**Whole-output assertion at CLI level** (`:70-83`) — this is how D-11's "one line and nothing else"
is pinned; note `lines == [refusal_text(...)]`, an equality on the full line list, not a substring:

```python
def test_cli_erase_on_flash4_part_refuses_pre_connect_with_one_line():
    runner = CliRunner()
    eprom_operator = Mock(spec=EpromOperator)
    app = _cli_app_context(eprom_operator)
    with patch.object(
        cli_handlers,
        "resolve_chip",
        return_value={"algorithm": 5, "bus-config": NO_PIN1_BUS_CONFIG},
    ):
        result = runner.invoke(cli, ["erase", "AE29F2008"], obj=app)

    assert result.exit_code == 1
    lines = result.output.splitlines()
    assert lines == [refusal_text("AE29F2008")]
    eprom_operator.erase_eprom.assert_not_called()
```

**The D-02 "exact guarded set, narrows or widens" test** — the analog is
`test_predicate_matches_real_database_algorithm_5_rows_exactly` (`:156-189`), which derives **both**
sides from the shipped database and asserts set equality with a symmetric-difference message:

```python
    db = EpromDatabase(skip_local_override=True)
    expected = set()
    all_part_numbers = set()
    for vendor_chips in db.proms.values():
        for chip in vendor_chips:
            part_number = chip.get("part_number", "")
            ...
            if chip.get("programming", {}).get("algorithm") == FLASH4_PROTOCOL_ID:
                expected.add(part_number)

    actual = set()
    for name in all_part_numbers:
        try:
            programmer_data = resolve_chip(name, db=db)
        except (ChipNotFoundError, ChipNotImplementedError):
            continue
        if is_flash4(programmer_data):
            actual.add(name)

    assert actual == expected, (
        f"predicate fired for {len(actual)} part number(s) against "
        f"{len(expected)} shipped algorithm-5 row(s); symmetric difference: "
        f"{sorted(actual ^ expected)}"
    )
```

**Convention:** set equality (which fails on both narrowing and widening, as D-02 requires), both
sides derived from `EpromDatabase(skip_local_override=True)` + `resolve_chip`, no literal part-number
list, and a `NOT A BLANKET REFUSAL` counter-leg so a fail-closed regression cannot pass the file.

---

### `tests/test_write_blank_guard.py` — the host-path + ordering test

**Analog (harness setup):** `_drive_write_eprom_for_ack_check`,
`firestarter_app/tests/test_eprom_operations.py:2244-2296`. All three harnesses RESEARCH §2.4 names
are this same shape; this is the one with the fullest docstring:

```python
def _drive_write_eprom_for_ack_check(
    tmp_path, make_comm, fake_serial, *, skip_sdp_unlock: bool, ack_present: bool,
):
    """Drive a full, otherwise-successful write_eprom() against a real
    protocol-0x0D chip (at28c256) through a fake serial port.
    ...
    """
    from firestarter.eprom_operations import EpromOperator, build_flags
    from firestarter.messages import MSG_OK_REQ_DATA, MSG_WARN_SDP_UNLOCK_SKIPPED

    input_file = tmp_path / "at28c256.bin"
    input_file.write_bytes(b"\x01\x02\x03\x04")

    fake_serial.feed(build_frame(MSG_INIT_DONE, b""))
    fake_serial.feed(build_frame(MSG_OK_REQ_DATA, b""))
    fake_serial.feed(build_frame(MSG_MAIN_DONE, b""))
    fake_serial.feed(build_frame(MSG_END_DONE, b""))

    def _fake_find_and_connect(command_dict, config, **kwargs):
        return make_comm()

    operator = EpromOperator(ConfigManager())
    operation_flags = build_flags(skip_sdp_unlock=skip_sdp_unlock)
    with patch(
        "firestarter.serial_comm.SerialCommunicator.find_and_connect",
        side_effect=_fake_find_and_connect,
    ):
        ok = operator.write_eprom(
            "at28c256",
            _at28c256_programmer_dict(),
            str(input_file),
            operation_flags=operation_flags,
        )
    return ok
```

Fixtures used: `tmp_path`, `make_comm`, `fake_serial` (`tests/conftest.py:133-220`). **Feed the whole
frame script before the drive** — `_FakeSerial.feed()` and `.write()` share one `BytesIO` and one
`_write_pos`, and all three existing harnesses pre-load for that reason.

**Analog (capture at the command-ordering seam):** `test_region_end_emitted_on_write`,
`tests/test_eprom_operations.py:393-424`. This is the idiom criterion 1's wire-level ordering
assertion adapts (replace the single-dict capture with an append to a list):

```python
def test_region_end_emitted_on_write(make_comm, fake_serial) -> None:
    """... Captured at the wire boundary (the dict SerialCommunicator.find_and_connect
    receives), the same boundary TestSdpOperationsWireShape above uses.
    """
    from firestarter.constants import COMMAND_WRITE, JSON_KEY_REGION_END

    captured: dict = {}

    def _fake_find_and_connect(command_dict, config, **kwargs):
        captured["command_dict"] = command_dict
        return make_comm()

    operator = EpromOperator(ConfigManager())
    with patch(
        "firestarter.serial_comm.SerialCommunicator.find_and_connect",
        side_effect=_fake_find_and_connect,
    ):
        operator._setup_operation(...)

    assert captured["command_dict"][JSON_KEY_REGION_END] == 0x1000 + 256
```

**Variant harness worth copying for a self-checking test:** `tests/test_pulse_us_override.py:128-167`
returns `(ok, captured)` from the drive so a test asserts on both the verdict and the composed
command dict — the natural shape for "refused, and `opened == [COMMAND_READ]`".
`tests/test_write_progress.py:162-262` adds the delegating-`patch.object` wrapper convention (never a
stub, because stubbing breaks MAIN-phase flow control) and the "test authoring error" assertion that
checks the *script itself* before asserting behaviour:

```python
    expected_chunks = -(-file_size // _BUFFER_SIZE)  # ceiling division
    assert len(chunk_progress_frames) == expected_chunks, (
        f"test authoring error: file_size={file_size} needs "
        f"{expected_chunks} chunk(s) against the {_BUFFER_SIZE}-byte Uno "
        f"floor, but chunk_progress_frames has {len(chunk_progress_frames)} entries"
    )
```

**CLI-tier exit-code assertions** for `--verify`'s three codes: `tests/test_cli_handlers.py:470-497`,
one test per code, `Mock(spec=EpromOperator)` with a fixed `return_value`:

```python
    operator = Mock(spec=EpromOperator)
    operator.verify_eprom.return_value = 2
    app = make_app_context(eprom_operator=operator)
    result = runner.invoke(cli, ["verify", "W27C512", "in.bin"], obj=app)
    assert result.exit_code == 2
```

## Shared Patterns

### Pure-gate polarity statement
**Source:** `firestarter_app/firestarter/page_size_gate.py:33-41`
**Apply to:** the new predicate module (mandatory — D-05 requires the reasoning at the site)
Every sibling gate names the *other* siblings' opposite polarity in its own docstring. The new module
is the fifth instance of that convention and must name `flash4_erase_gate.is_flash4` explicitly.

### Refusal-as-format-constant
**Source:** `firestarter_app/firestarter/flash4_erase_gate.py:43,68-79`; also `page_size_gate.py`'s
`_REFUSAL_FORMAT` / `_INVALID_PAGE_SIZE_FORMAT` / `_ALIGNMENT_REFUSAL_FORMAT`
**Apply to:** the new module's refusal, and its test (whole-sentence equality + forbidden-substring
negative list).

### Typed exception → `map_typed_errors` → exit 1
**Source:** `firestarter_app/firestarter/cli_handlers.py:222-227`, `exceptions.py:92-115`
**Apply to:** the guard refusal only. It cannot carry exit 2 (`ClickException.exit_code == 1`), so
D-13's transport arm must be a return value, following `verify`/`blank`'s `sys.exit(verdict)`
(`cli_handlers.py:966`, `:1023`).

### Keyword-only additive parameters on operator methods
**Source:** `_drive_region_compare`'s `*, full, region_length` (`eprom_operations.py:2230-2237`);
`verify_eprom`'s `full=` threading
**Apply to:** the render-suppression switch on `_drive_region_compare` and any `verify=`/`full=`
kwarg on `write_eprom`. Default values must keep `verify`/`blank` byte-identical.

### Reasoning-at-the-site comments
**Source:** `eprom_operations.py:2125-2130` (the `region_length` getsize block),
`cli_handlers.py:745-757` (the `--skip-erase` 0x0D arm)
**Apply to:** every carve-out in the new predicate and the guard's insertion point. Comments in
product source are permitted again (2026-09-19); the house style is a labelled block
(`# BLANK-01 / D-05: …`) stating what would break if the code were written the other way.

### Fake-serial drive of the genuine operator
**Source:** `tests/test_eprom_operations.py:2244`, `tests/test_pulse_us_override.py:128`,
`tests/test_write_progress.py:162`
**Apply to:** every test that claims host-path coverage. Never `tests/fake_chip.py` — `FakeChip` does
not subclass `EpromOperator` (`fake_chip.py:47`), so the product `write_eprom` is absent from its
call graph.

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| the **read-phase frame script** inside `tests/test_write_blank_guard.py` | test fixture | streaming | No test in the suite drives a genuine `_main_phase_read_data` over `_FakeSerial`. `grep -rn "MSG_DATA_SENDING\|MSG_DATA_CHUNK"` across `tests/` matches only `test_decoder.py`, `test_compare.py`, `test_characterization.py`, `test_protocol_not_implemented_production_path.py` and `test_write_response_budget.py` — none of them feeds a read main-phase to a real `EpromOperator`; every `read_eprom` / `verify_eprom` / `check_eprom_blank` test site uses a `Mock(spec=EpromOperator)` or `FakeChip`. The three existing harnesses are **write**-phase scripts (`MSG_INIT_DONE → MSG_OK_REQ_DATA → MSG_MAIN_DONE → MSG_END_DONE`) and give the frame-feeding and `find_and_connect`-patching shape but not the ack-per-chunk read script. Treat this as new construction (RESEARCH §2.5 Option A, assumption A2); build the negative control first. |

## Metadata

**Analog search scope:** `firestarter_app/firestarter/` (product source),
`firestarter_app/tests/` (all test modules and `__snapshots__/`). Firmware read only as evidence,
per the phase's app-only scope; no firmware analog is assigned.
**Files scanned:** ~20 read or grepped; 12 read for excerpts.
**Pattern extraction date:** 2026-09-21
