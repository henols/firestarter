# Phase 202: One comparison engine, on the host - Pattern Map

**Mapped:** 2026-09-20
**Files analyzed:** 7 (2 created, 5 modified)
**Analogs found:** 7 / 7
**Path convention:** every path below is relative to `/workspaces/firestarter_app/` and was confirmed
git-tracked in that submodule (`git ls-files`). No gitignored mirror paths appear.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `firestarter/compare.py` (NEW) | utility / pure library | streaming transform | `firestarter/sdp_honesty.py` (import-lightness + docstring) + `firestarter/transport_counters.py` (accumulate → `snapshot()`) | role-match (two complementary analogs) |
| new test module (engine + D-03 corpus) | test | batch / parametrised | `tests/test_chip_test.py:306-324` (parametrize), `:173-275` (bucket cases) | exact |
| `firestarter/eprom_operations.py` `verify_eprom` | service | request-response → streaming | `read_eprom` (`:940-971`) — the chunk-callback drive | exact |
| `firestarter/eprom_operations.py` `check_eprom_blank` | service | request-response → streaming | `read_eprom` (`:940-971`); short-circuit stays as at `:2325-2343` | exact |
| `firestarter/eprom_operations.py` `_main_phase_read_data` | service (protocol loop) | streaming | itself (`:869-921`) — no analog for the abort seam | **no analog for the abort** |
| `firestarter/chip_test.py` `classify_fingerprint` | utility | batch → delegation | `sdp_honesty.emission_summary` (delegate rather than duplicate) | partial |
| `firestarter/cli_handlers.py` `verify` / `blank` | controller (CLI) | request-response | `read` (`:529-557`) for options; `dev_consistency_check` (`:1558-1588`) for exit 2 | exact |
| `tests/test_eprom_operations.py` | test | event capture | `_capture_written_frames` (`:1164-1179`) + `find_and_connect` capture (`:1196-1216`) | exact |

---

## Pattern Assignments

### `firestarter/compare.py` (NEW — utility, streaming transform)

**Analog A — import-light module at birth: `firestarter/sdp_honesty.py:1-25`**

This is the module `compare.py` should look like on day one. Note three copyable conventions:
a module docstring that states *why the module exists separately*, an explicit machine-checkable
import-set invariant comment, and `from __future__ import annotations` first.

```python
"""Shared honesty carrier for SDP (Software Data Protection) wording.

Holds the unreadable-state caveat and the unknown-command-to-outdated-firmware
mapping. Neither can live in the operation layer: `serial_comm.get_response()`
filters the entire INFO band, so that layer never sees the firmware duration
frame the caveat exists to disclaim.

`unreadable_state_caveat()`'s TEXT is load-bearing at seven call sites and is
pinned by tests -- extend this module additively rather than re-authoring what
is here.
"""

from __future__ import annotations

# Import-set invariant (checked by an AST-based test):
# this module's top-level import set is a subset of
# {"__future__", "firestarter.exceptions", "firestarter.messages"}, both leaf
# modules (`exceptions.py` has zero top-level imports; `messages.py` imports
# only `dataclasses`). In particular, no `click` -- the caller performs the
# echo, so a `click` dependency here would make this module unusable from the
# report layer, which has no CLI context of its own.
from firestarter.exceptions import EpromOperationError, FirmwareOutdatedError
from firestarter.messages import MSG_ERR_UNKNOWN_CMD
```

**Copy for `compare.py`:** the docstring naming D-01's reason (`eprom_operations` is 2502 lines and
pulls `serial_comm`; `chip_test` is 3774 lines and pulls `database`), and an import-set invariant
comment naming the allowed set — for `compare.py` that is stdlib only (`__future__`, `dataclasses`,
`typing`). **Type-annotation density:** every public function in `sdp_honesty` is fully annotated
(`-> str`, `mode: str, chip_name: str`) even though the module is in the mypy strict list. Write
`compare.py` the same way; RESEARCH Open Question 2 recommends adding `"firestarter.compare"` to
`pyproject.toml`'s strict-island list from birth, exactly as `sdp_honesty` joined (that file's own
comment records the precedent).

**Analog B — accumulate-then-finalise: `firestarter/transport_counters.py:129-147`**

The repo's existing separation of a mutable counter sink from an immutable result snapshot:

```python
def reset() -> None:
    """Zero every counter in the sink. ..."""
    for key in _counters:
        _counters[key] = 0


def snapshot() -> dict[str, int]:
    """Return a fresh dict of every counter, keyed in fixed sorted order.

    A new dict is built on every call, so a caller mutating the returned
    object can never reach back into the sink -- key order is deterministic
    (sorted), never insertion-dependent.
    """
    return {key: _counters[key] for key in sorted(_counters)}
```

Also note its module docstring's explicit **"Import purity"** paragraph (`:21-25`) — the same
paragraph `compare.py` needs for D-01.

**Copy:** `Accumulator.feed(...)` mutates; `Accumulator.finalise() -> CompareResult` builds a fresh
object; a caller mutating the result cannot reach back. Deterministic key order in the emitted
`bit_clustering` dict (RESEARCH Pitfall 3 — emit only `range(8, max_bit)`, ascending).

**Analog C — result dataclass with documented not-measured / derived fields:
`firestarter/diagnostic_report.py:123-174` (`TransportHealth`)**

```python
@dataclass
class TransportHealth:
    """Best-effort transport-health counters.

    Every counter defaults to `None` -- "not measured". ...
    `transport_suspect` defaults `False` and can only be set `True` by
    `_is_transport_suspect` below -- never inferred from absent data.
    """

    cobs_errors: int | None = None
    ...
    transport_suspect: bool = False
```

**Copy for `CompareResult` (D-05):** plain `@dataclass`, field-wise `==` for free, every derived or
capped field carrying a docstring line saying how it is derived and what it does **not** claim. This
is directly what D-09 (compared-prefix range must be explicit) and D-16 (`extra_ranges`/`extra_bytes`
come from counters, never `len(list)`) need.

**The dataclass the engine must reproduce exactly — `firestarter/chip_test.py:155-163`:**

```python
@dataclass
class Fingerprint:
    """Verdict + raw evidence for a single expected-vs-actual byte compare."""

    total: int
    bad: int
    bad_pct: float
    classification: str
    evidence: dict = field(default_factory=dict)
```

---

### `firestarter/chip_test.py` — `classify_fingerprint` / `_diff_offsets` (utility, batch → delegation)

**Analog:** `sdp_honesty.emission_summary` (`sdp_honesty.py:38-59`) — the repo's stated
"compose by calling the single source, never duplicate" idiom:

> *"Composed by calling `unreadable_state_caveat()` rather than duplicating its wording, so the two
> can never drift."*

**The rule comment to preserve and re-point, `chip_test.py:106-116`** (it currently justifies copying
the math *into* `chip_test`; after D-01 it must justify importing it *from* `compare.py`):

```python
# ---------------------------------------------------------------------------
# Shared byte-diff-offset helper -- reused, not reimplemented
# ---------------------------------------------------------------------------
#
# Mirrors the exact divergence math in `consistency_check_eprom`
# (eprom_operations.py:842-863): cmp_len / diff_offsets / pct / first
# divergence offset. This is the ONE divergence primitive `classify_fingerprint`
# consumes -- do NOT add a second parallel divergence implementation
# elsewhere in this codebase. The math is small enough to
# copy rather than import, keeping this module import-light (no dependency
# on eprom_operations.py).
```

**The exact semantics the delegating wrapper must keep** (`chip_test.py:118-131`, `:189-275`):

```python
def _diff_offsets(expected, actual) -> tuple[int, list[int], float, int | None]:
    cmp_len = min(len(expected), len(actual))
    diff_offsets = [o for o in range(cmp_len) if expected[o] != actual[o]]
    pct = 100.0 * len(diff_offsets) / cmp_len if cmp_len else 0.0
    first = diff_offsets[0] if diff_offsets else None
    return cmp_len, diff_offsets, pct, first
```

```python
    ff_count = sum(1 for b in actual[:cmp_len] if b == 0xFF)
    ff_ratio = (ff_count / cmp_len) if cmp_len else 0.0

    evidence: dict = {
        "ff_ratio": ff_ratio,
        "repeat_divergent": repeat_divergent,
        "first_offset": first_offset,
        "bit_clustering": {},
    }
```

Address-line clustering, the part that must become online counters
(`chip_test.py:205-227` — note `addr_base + o`, the `cmp_len > (1 << 8)` guard, and `score > best_score`
scanning `k` ascending so ties resolve to the **lowest** bit):

```python
    if bad and cmp_len > (1 << 8):
        max_bit = (cmp_len - 1).bit_length()
        for k in range(8, max_bit):
            mask = 1 << k
            set_count = sum(1 for o in diff_offsets if (addr_base + o) & mask)
            clear_count = bad - set_count
            score = max(set_count, clear_count) / bad
            evidence["bit_clustering"][k] = score
            if score > best_score:
                best_score = score
                suspected_line = k
```

Return shape, repeated identically at all five bucket exits (`:210-275`) — copy verbatim so the
delegating path builds the same object:

```python
        return Fingerprint(
            total=cmp_len,
            bad=bad,
            bad_pct=bad_pct,
            classification=FP_BLANK_CONTACT,
            evidence=evidence,
        )
```

---

### `firestarter/eprom_operations.py` — `verify_eprom` / `check_eprom_blank` (service, streaming)

**Analog: `read_eprom` (`eprom_operations.py:923-971`)** — the canonical chunk-callback drive, and
the exact shape both rewritten methods should take.

```python
    def read_eprom(
        self,
        eprom_name: str,
        eprom_data_dict: dict,
        output_file: str | None = None,
        operation_flags: int = 0,
        address_str: str | None = None,
        size_str: str | None = None,
    ) -> bool:
        with self._operation_context(
            eprom_name,
            eprom_data_dict,
            COMMAND_READ,
            operation_flags,
            address_str,
            size_str,
        ) as (cmd_data, _, op_name):
            if not cmd_data:
                return False
            ...
            start_time = time.time()

            try:
                with open(actual_output_file, "wb") as file_handle:

                    def _write_to_file(address, data_chunk):
                        file_handle.seek(address)
                        file_handle.write(data_chunk)

                    is_ok, _ = self._run_state_machine(
                        op_name,
                        main_phase_handler=self._main_phase_read_data,
                        start_addr=cmd_data.get("address", 0),
                        end_addr=cmd_data.get("memory-size", 0),
                        process_data_chunk_callback=_write_to_file,
                    )
                ...
            except IOError as e:  # noqa: UP024
                logger.error(f"File I/O error with {actual_output_file}: {e}")
                return False
```

**Copy exactly:** `COMMAND_READ` (not `COMMAND_VERIFY`/`COMMAND_BLANK_CHECK`) as the ordinal passed
to `_operation_context`; the `if not cmd_data: return False` guard; `address_str`/`size_str`
positional pass-through (this is how CMP-08's `-a`/`-s` reach `_setup_operation` with zero new
plumbing); the closure-as-callback shape; `is_ok, _ = self._run_state_machine(...)`; the
`# noqa: UP024` on `IOError`.

**Second worked example — `consistency_check_eprom` (`eprom_operations.py:1066-1087`)**, which shows a
callback closing over *loop* state via default args (the shape a compare callback closing over the
accumulator can use), plus the absolute-vs-relative offset trap called out in its own comment:

```python
                                def _writer(
                                    address,
                                    data_chunk,
                                    _fh=fh,
                                    _start=cmd_data.get("address", 0),
                                ):
                                    # Mirror read_eprom's _write_to_file inner closure
                                    # ... Use relative-from-start
                                    # offset so the file fills from byte 0 regardless of
                                    # absolute start_addr.
                                    _fh.seek(address - _start)
                                    _fh.write(data_chunk)
```

**D-04's expected-side pull callback: no analog found.** Nothing in the repo takes an
`expected(offset, length) -> bytes` pull callback. New ground. The push direction
(`process_data_chunk_callback(address, payload)`) is the only callback contract that exists.

**`check_eprom_blank`'s short-circuit to preserve (`eprom_operations.py:2325-2343`)** — keep the
warning text and the pre-wire position; change only the return/exit per D-12:

```python
        etype = eprom_data_dict.get("electrical-type", "")
        proto = eprom_data_dict.get("protocol-id", 0)
        if etype in ("SRAM", "FRAM") or proto in self._SRAM_PROTO_IDS:
            logger.warning(
                f"Blank check is not applicable to {eprom_name.upper()} "
                f"(electrical type: {etype or 'unknown'}, protocol: 0x{proto:02X}). "
                "SRAM/FRAM are volatile or byte-rewritable — they have no "
                "factory-blank state and the firmware has no blank-check op for them."
            )
            return False
```

**`verify_eprom`'s existing region-length computation to carry forward (`:2153-2160`)** — D-17 keeps
the file-length default:

```python
        try:
            region_length = os.path.getsize(input_file_path)
        except OSError:
            region_length = None
```

---

### `firestarter/eprom_operations.py` — `_main_phase_read_data` abort seam (service, streaming)

**Analog: the function itself, `:869-921`.** Confirmed by reading it: the callback's return value
**is** discarded (bare statement at `:909`) and `send_ack()` **is** unconditional at `:912`.
Verbatim, `:905-912`:

```python
                if response.payload is not None:
                    # MSG_DATA_CHUNK: the raw chip bytes are in response.payload.
                    payload = response.payload
                    if not payload:
                        logger.warning("Received MSG_DATA_CHUNK with empty payload.")
                        continue
                    process_data_chunk_callback(start_addr, payload)
                    start_addr += len(payload)
                    progress.update(len(payload))
                    self.comm.send_ack()
```

Signature, `:869-875`:

```python
    def _main_phase_read_data(
        self,
        progress: ClassProgressHandler,
        start_addr: int,
        end_addr: int,
        process_data_chunk_callback: Callable,
    ):
```

The four call sites pass it by keyword to `_run_state_machine(..., main_phase_handler=self._main_phase_read_data, start_addr=..., end_addr=..., process_data_chunk_callback=...)` — `:952-963`
(`read_eprom`), `:1081-1087` and a second in `consistency_check_eprom`, and a hexdump path at `:1887`.

**No analog found for an abort/stop-acking signal.** No optional-keyword-controlled early exit exists
in any main-phase handler in this file. This is the phase's one genuinely new seam (RESEARCH Open
Question 1). The nearest structural precedent for *adding an optional keyword to a handler without
touching existing callers* is `read_eprom`'s own `address_str`/`size_str` defaults
(`:928-931`, all `= None`) — additive, defaulted, invisible to callers that omit it. The planner
should decide between "honour `is False` from the callback" and "new `abort_predicate` keyword"
explicitly; the keyword route matches that additive-default precedent and leaves the four existing
`None`-returning callbacks untouched.

---

### `firestarter/cli_handlers.py` — `verify` / `blank` (controller, request-response)

**Analog for options: `read` (`cli_handlers.py:529-557`), verbatim.** This is the spelling CMP-08
must match:

```python
@cli.command(name="read")
@click.argument("eprom", shell_complete=_complete_eprom)
@click.argument("output_file", required=False)
@click.option(
    "-f", "--force", is_flag=True, help="Force, even if the chip id doesn't match."
)
@click.option("-a", "--address", default=None, help="Read start address in dec/hex")
@click.option("-s", "--size", default=None, help="Size of the data to read in dec/hex")
@click.pass_obj
@map_typed_errors
def read(
    app: AppContext,
    eprom: str,
    output_file: str | None,
    force: bool,
    address: str | None,
    size: str | None,
) -> None:
    """Reads the content from an EPROM."""
    eprom_data = resolve_chip(eprom, db=app.db)
    ok = app.eprom_operator.read_eprom(
        eprom,
        eprom_data,
        output_file,
        operation_flags=_build_op_flags(force=force),
        address_str=address,
        size_str=size,
    )
    sys.exit(0 if ok else 1)
```

**Current `verify` (`:794-822`) — already has `-a/--address`, lacks `-s/--size` and `--full`:**

```python
@cli.command(name="verify")
@click.argument("eprom", shell_complete=_complete_eprom)
@click.argument("input_file")
@click.option("-a", "--address", default=None, help="Verify start address in dec/hex")
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="Force, even if the VPP or chip id doesn't match.",
)
@click.pass_obj
@map_typed_errors
def verify(
    app: AppContext,
    eprom: str,
    input_file: str,
    address: str | None,
    force: bool,
) -> None:
    """Verifies the content of an EPROM."""
    eprom_data = resolve_chip(eprom, db=app.db)
    ok = app.eprom_operator.verify_eprom(
        eprom,
        eprom_data,
        input_file,
        address_str=address,
        operation_flags=_build_op_flags(force=force),
    )
    sys.exit(0 if ok else 1)
```

**Current `blank` (`:824-841`) — has only `-f/--force`:**

```python
@cli.command(name="blank")
@click.argument("eprom", shell_complete=_complete_eprom)
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="Force, even if the VPP or chip id doesn't match.",
)
@click.pass_obj
@map_typed_errors
def blank(app: AppContext, eprom: str, force: bool) -> None:
    """Checks if an EPROM is blank."""
    eprom_data = resolve_chip(eprom, db=app.db)
    ok = app.eprom_operator.check_eprom_blank(
        eprom, eprom_data, operation_flags=_build_op_flags(force=force)
    )
    sys.exit(0 if ok else 1)
```

Note both are fully annotated (`-> None`, every param typed) — `cli_handlers` is in the mypy
strict-island list, so new options must be too. Both keep `@click.pass_obj` before `@map_typed_errors`.

**Analog for the exit-2 path: `dev_consistency_check` (`cli_handlers.py:1556-1588`), verbatim —
the only command in the file that exits on a service-returned int:**

```python
    @click.pass_obj
    @map_typed_errors
    def dev_consistency_check(
        app: AppContext,
        eprom: str,
        runs: int,
        ...
    ) -> None:
        """Read EPROM N consecutive times and report SHA-256 divergence.

        Exits 0 on PASS, 1 on FAIL, 2 on hardware error. The three are distinct: a
        hardware error is not reported as a failed comparison.
        """
        eprom_data = resolve_chip(eprom, db=app.db)
        verdict_int = app.eprom_operator.consistency_check_eprom(
            eprom,
            eprom_data,
            runs=runs,
            ...
        )
        sys.exit(verdict_int)
```

**Copy exactly for D-10/D-11:** the service method returns `int`, the command does
`sys.exit(verdict_int)`, and the **docstring states the three codes** (that docstring is user-facing
`--help` text). `@map_typed_errors` stays on the command — it only converts *raised* typed
exceptions; an `int` return flows straight past it. This is how exit 2 is produced without touching
`map_typed_errors` (D-11) and without hitting RESEARCH Pitfall 4.

**The service-side counterpart, `eprom_operations.consistency_check_eprom:973-1018`** — its
signature ends `-> int` and its docstring carries the convention and the reason for the departure:

```python
    ) -> int:
        """Run N consecutive read_eprom passes and report SHA-256 divergence.

        Returns:
            0 -- all N reads byte-identical (PASS)
            1 -- one or more reads diverge (FAIL -- bug detected)
            2 -- hardware / serial / timeout error (could not complete N reads)

        This is the ONLY EpromOperator method that returns int rather than bool;
        the 3-way verdict (PASS / FAIL / hardware-error) cannot fit in a bool.
        Same exit-code convention as grep(1). ...
        """
```

**Note for the planner:** that docstring's *"the ONLY EpromOperator method that returns int"* claim
becomes false when `verify_eprom`/`check_eprom_blank` change return type. Amend it in the same
commit, or it is a stale in-source claim of exactly the kind this repo repairs rather than tolerates.

The exit-2-before-the-port-opens return path (`:1005-1010`) is the D-17 refusal shape:

```python
        if runs < 2:
            logger.error(
                f"--runs must be >= 2 (got {runs}); "
                f"a consistency check requires at least 2 reads to compare."
            )
            return 2
```

`map_typed_errors` itself (`cli_handlers.py:190-229`) is the file D-11 forbids changing — its
docstring is *"Map service-layer typed exceptions to ClickException + stable exit codes."* and all
eleven handlers raise `click.ClickException` (exit 1).

---

### Test modules (test, batch / event capture)

**(a) `command_dict` capture — `tests/test_eprom_operations.py:1191-1216`, read and confirmed
verbatim.** This is criterion 1's harness:

```python
        captured: dict = {}

        def _fake_find_and_connect(command_dict, config, **kwargs):
            captured["command_dict"] = command_dict
            return make_comm()

        fake_serial.feed(build_frame(MSG_INIT_DONE, b""))
        fake_serial.feed(build_frame(MSG_MAIN_DONE, b""))
        fake_serial.feed(build_frame(MSG_END_DONE, b""))
        written = _capture_written_frames(fake_serial)

        operator = EpromOperator(ConfigManager())
        with patch(
            "firestarter.serial_comm.SerialCommunicator.find_and_connect",
            side_effect=_fake_find_and_connect,
        ):
            ok = operator.sdp_unlock("at28c256", _at28c256_programmer_dict())

        assert ok is True
        assert captured["command_dict"]["cmd"] == 9
        # No `#`-prefixed data frame and no "DONE" round-trip were written.
        assert not any(chunk.startswith(b"#") for chunk in written)
        assert not any(b"DONE" in chunk for chunk in written)
```

Note the enclosing class docstring style (`:1181-1186`) — it names the requirement ids the class
proves. Copy that: a `TestVerifyIssuesReadOrdinal` class whose docstring names CMP-01/CMP-02.
RESEARCH's strengthening note applies: collect into a `list` rather than a single key, so the
assertion is "no call was VERIFY" not "the last call was READ".

**The write recorder — `tests/test_eprom_operations.py:1164-1179`, verbatim:**

```python
def _capture_written_frames(fake_serial):
    """Wrap fake_serial.write to record every chunk the host writes.

    Returns the list the wrapper appends to; the original write behavior
    (buffering into the BytesIO-backed fake) is preserved so the state
    machine's own send_ack()/get_response() flow is unaffected.
    """
    written: list = []
    original_write = fake_serial.write

    def _wrapped(data: bytes) -> int:
        written.append(bytes(data))
        return original_write(data)

    fake_serial.write = _wrapped
    return written
```

This is also the seam for D-06's abort test: **assert the ack writes stop** after the first
mismatching chunk. That is the only in-repo way to observe "stopped acking".

**(b) Parametrised-corpus model — `tests/test_chip_test.py:306-324`, verbatim.** Note the per-row
comment explaining *why each row is in the table*; the D-03 corpus should carry the same per-bucket
rationale:

```python
@pytest.mark.parametrize(
    "name,expected",
    [
        # ST M27C512 -- genuine UV-EPROM, algorithm 0x07. The execution-time
        # algorithm proxy would MISS this (0x07 is not 0x0B).
        ("M27C512", True),
        # AM27C020 -- genuine UV-EPROM, algorithm 0x08. Same miss as above.
        ("AM27C020", True),
        ("W27C512", False),
        # Atmel AT28C256 -- ordinary EEPROM, not UV.
        ("AT28C256", False),
    ],
)
def test_is_uv_eprom_four_chip_table(name, expected):
```

The five bucket inputs to lift into that table are `tests/test_chip_test.py:173-275`
(`test_fp_blank_near_all_ff`, `test_fp_address_line_bit_a8`,
`test_fp_address_line_absolute_addr_base`, `test_fp_transport_scattered_repeatable`,
`test_fp_indeterminate_ambiguous`, `test_fingerprint_evidence_fields`), plus
`_SCATTERED_OFFSETS` (`:214-231`) — reuse that list, do not re-derive it.

**(c) Constructing fake chip data.** Two idioms, both read:
- **Pure byte construction** — the bucket tests build inputs with
  `expected = generate_pattern(start, length)` then `actual = bytearray(expected)` and flip bytes
  (`test_chip_test.py:183-197`). This is the right idiom for the engine's unit tests and the D-03
  corpus: no operator, no serial, no fixtures.
- **`tests/fake_chip.py` `FakeChip`** — an `EpromOperator`-shaped double with real absolute-offset
  read semantics. Its docstring states the property that matters for a compare test:
  > *"`read_eprom` writes the requested bytes at their ABSOLUTE offset, reproducing
  > `eprom_operations._write_to_file`'s `file_handle.seek(address)` ... A double that wrote the
  > payload at offset 0 would make the engine's region-slice `[start:start+length]` look correct
  > while testing nothing -- this is the single most important property of this double."*

  It is **not** collected by pytest (no `test_` prefix) and is imported by name. Use it only if a
  test needs an operator-level double; the accumulator itself should be driven by a synthetic
  `(address, bytes)` generator per RESEARCH.

**(d) Import-purity enforcement for D-01 — `tests/test_diagnostic_report.py:538-569`, verbatim.**
This is the AST scan that should be pointed at `compare.py`, and its docstring states *why* a grep
is not acceptable:

```python
def test_report_module_is_orchestrator_only():
    """AST-based structural scan (mirrors the Phase-109 SAFE-02 lesson: a raw
    substring grep false-positives on docstring prose describing the safety
    property itself, e.g. "imports no SerialCommunicator"). This test parses
    the module's AST and asserts no import statement names either forbidden
    symbol, ..."""
    import ast

    import firestarter.diagnostic_report as diagnostic_report_mod

    src = inspect.getsource(diagnostic_report_mod)
    tree = ast.parse(src)

    imported_names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported_names.update(alias.name for alias in node.names)

    assert "SerialCommunicator" not in imported_names
    assert "HardwareManager" not in imported_names
```

**Copy for D-01:** assert `compare.py`'s top-level import set is a subset of the stdlib allow-list,
i.e. that it names neither `firestarter.eprom_operations` nor `firestarter.chip_test` nor
`firestarter.serial_comm`. Caveat to carry into the plan: `ast.walk` here catches *nested* imports
too (`_main_phase_read_data:877` has a deliberate function-local import), which for `compare.py` is
what you want — a lazy import would defeat D-01 just as thoroughly.

---

## Shared Patterns

### Reason-carrying comments at the site (applies to every file this phase touches)
**Source:** `chip_test.py:106-116`, `transport_counters.py:21-25`, `diagnostic_report.py:123-162`,
`eprom_operations.py:2327-2332`.
**Apply to:** `compare.py`, both rewritten service methods, both CLI commands.
This codebase's dominant convention is a comment or docstring paragraph that states the *rejected
alternative and why*, not what the code does. D-02, D-08, D-12 and D-16 each carry exactly such
reasoning and each belongs at its site. Comments in product source are permitted again as of
2026-09-19.

### `# noqa` codes (applies to all modified product files)
**Source:** `eprom_operations.py:969` (`# noqa: UP024`), `:2186` (`# noqa: E501`), `:2362`
(`# noqa: UP006`).
Ruff's select set is `E,F,I,UP` with `E501` extend-ignored. Only `E`, `F`, `I`, `UP` noqa codes do
anything; any other is inert text. `I` is live, so `compare.py`'s import order is gated.

### Operation entry guard (applies to both rewritten service methods)
**Source:** `eprom_operations.py:951` and `:2170` and `:2350` — identical three lines:
```python
        ) as (cmd_data, _, op_name):
            if not cmd_data:
                return False
```
Under D-10 this becomes `return 2` (setup failure is a hardware/transport condition, matching
`consistency_check_eprom:1063` which returns `2` from the same guard).

### Timing + logging around an operation
**Source:** `eprom_operations.py:2174-2189`, `:2354-2359`, `:947-966` — all three use
`start_time = time.time()` then
`logger.info(f"... ({time.time() - start_time:.2f}s)")` on success and `logger.error(...)` on
failure. Keep it; the D-13/D-14 output lines are `click.echo`-class operator output and are a
*separate* concern per D-05, not logger calls.

---

## No Analog Found

| File / seam | Role | Data Flow | Reason |
|-------------|------|-----------|--------|
| `_main_phase_read_data` abort signal | service | streaming | No main-phase handler in `eprom_operations.py` has any early-stop or predicate seam. All four `process_data_chunk_callback` callers return `None` and the return is discarded at `:909`. New ground — planner must choose the mechanism (RESEARCH Open Question 1). Nearest structural precedent is additive defaulted keywords (`read_eprom:928-931`). |
| D-04 `expected(offset, length) -> bytes` pull callback | utility | streaming | No pull-shaped callback exists anywhere in the package; every callback in this codebase is push-shaped. New ground. |
| `tracemalloc` peak-memory assertion (criterion 2) | test | measurement | RESEARCH's exhaustive `os.walk` found **zero** hits for `tracemalloc|getsizeof|getrusage|psutil` in either sub-repo's own source. No precedent; use the stdlib directly. |
| D-16's capped-list-plus-exact-counter output | utility | transform | `consistency_check_eprom`'s `max_diffs=10` truncates its diff report, but it does **not** report an exact "and M more" from counters. Partial precedent only; the honest-tail-count shape is new. |

---

## Metadata

**Analog search scope:** `firestarter_app/firestarter/` (all modules), `firestarter_app/tests/`
(targeted: `test_eprom_operations.py`, `test_chip_test.py`, `test_diagnostic_report.py`,
`test_sdp_capability.py`, `test_sdp_honesty.py`, `fake_chip.py`, `conftest.py`).
**Files opened this session:** 11 product/test files, all at targeted line ranges (the two large
modules were read only at cited ranges via `sed`, never whole).
**Tracked-source check:** `git ls-files` run inside the `firestarter_app` submodule; every analog path
above is tracked. `firestarter/compare.py` is correctly absent (the file this phase creates).
**Pattern extraction date:** 2026-09-20
