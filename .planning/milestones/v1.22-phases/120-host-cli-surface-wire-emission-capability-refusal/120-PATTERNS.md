# Phase 120: HOST — CLI surface, wire emission, capability refusal - Pattern Map

**Mapped:** 2026-07-29
**Files analyzed:** 14 (3 new source/test, 6 modified source, 4 extended/rewritten test, 1 new fixture, 3 meta-repo docs)
**Analogs found:** 13 / 14 with an exact or role-match analog

All source work is in `/workspaces/firestarter_app` (branch `v1.22-at28c-software-data-protection-lifecycle`, confirmed). `/workspaces/firestarter` is READ-ONLY reference.

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `firestarter/sdp_capability.py` | **NEW** — domain predicate module | transform (pure) | `firestarter/eprom_operations.py:1655-1676` (`_SRAM_PROTO_IDS` + `check_eprom_blank` short-circuit) | **wording-only** — data access is an ANTI-pattern (F-06) |
| `firestarter/constants.py` | config / wire-protocol mirror | — | its own `COMMAND_*` / `COMMAND_NAMES` / `FLAG_*` blocks at `:55-99` | exact (in-file) |
| `firestarter/cli_handlers.py` — `dev sdp` handler | controller (Click) | request-response | `dev test` at `:1753-1850` | exact ⚠ **ordering inverted** |
| `firestarter/cli_handlers.py` — `write --skip-sdp-unlock` + `_build_op_flags` kwarg | controller | request-response | `write` at `:463-530` + `_build_op_flags` at `:242-281` (`--skip-erase` is the shape) | exact (in-file) |
| `firestarter/eprom_operations.py` — `sdp_unlock` / `sdp_lock` | service (operator method) | request-response, payload-free | `erase_eprom` at `:1628-1650` | **exact** |
| `firestarter/eprom_operations.py` — `build_flags` kwarg | utility | transform | `build_flags` at `:168-183` (`skip_erase=` is the shape) | exact (in-file) |
| `firestarter/serial_comm.py` — INFO promotion | middleware (transport) | event-driven | `_log_rurp_feedback` at `:228-247` (its own `ERROR`/`WARN` arms) | exact (in-file) |
| `firestarter/serial_comm.py` — `0x86` ack record | middleware | event-driven | `_decode_id_frame` at `:249-280` (Phase 55 `firmware_max_chunk`) | **exact** |
| `firestarter/submit.py` — repo target | config constant | — | **NO CHANGE NEEDED — already correct** (see § Already-Landed) | n/a |
| `tests/test_sdp_capability.py` | **NEW** — invariant gate | batch (reads shipped DB) | `tests/test_sdp_db_invariant.py` | **exact** |
| `tests/test_dev_sdp_cmd.py` | **NEW** — CLI test | request-response | `tests/test_dev_test_cmd.py` + `tests/test_hardware.py:56-60` | **exact** (two analogs) |
| `tests/test_revision_constants_parity.py` | REWRITE — parity gate | batch (source scan) | `tools/check_is_memory_cmd_no_ifdef.py` + `tests/test_check_is_memory_cmd_no_ifdef.py` | role-match |
| `tests/fixtures/planted_constants_drift.h` | **NEW** — fixture | — | `tests/fixtures/planted_ifdef_in_predicate.h` | **exact** |
| `tests/test_eprom_operations.py`, `tests/test_serial_comm.py`, `tests/test_submit.py` | EXTEND | — | in-file idioms; `test_submit.py:301-320` for argv | exact |
| `.planning/ROADMAP.md` / `REQUIREMENTS.md` / `PROJECT.md` | migration (doc amendment) | — | `.planning/phases/119-.../119-09-PLAN.md` | **exact** |

---

## Two Things Checked (reported, not assumed)

### 1. `firestarter_app/tests/fixtures/` — EXISTS, 2 files, clear convention

```
tests/fixtures/planted_ifdef_in_predicate.h     (Phase 119 LOCK-03)
tests/fixtures/planted_log_in_window.cpp        (Phase 118/119)
```

**Convention, verbatim from `planted_ifdef_in_predicate.h:1-26`:** a long block comment as the *entire* first ~30 lines that states (a) which pytest owns it, (b) which phase/decision/requirement id it proves, (c) that the file is *never compiled* and not in `platformio.ini`, (d) exactly which env seam points at it, (e) **which single assertion it trips and which it deliberately does NOT trip** ("a fixture that failed for two reasons at once could not prove which check fired"), and (f) a "fixing this file would hollow the gate" warning naming the anti-hollow contract.

`planted_constants_drift.h` must follow all six. Its isolation requirement: plant **one** drift (e.g. a single `#define CMD_*` whose value disagrees with `constants.py`) so the failure names the value-drift leg, not the missing-`COMMAND_NAMES` leg.

### 2. `firestarter_app/tests/test_submit.py` — EXISTS (31,603 B), argv idiom is explicit

**Idiom A — whole-argv equality** (`tests/test_submit.py:275-291`):
```python
    run_fn.assert_called_once_with(
        ["gh", "issue", "create", "--repo", submit.SUBMIT_REPO,
         "--title", "My Title", "--body-file", "-"],
        input="My Body", text=True, capture_output=True, check=False,
    )
```

**Idiom B — negative argv assertion** (`:301-320`), the one that matches the memory record:
```python
def test_submit_via_gh_argv_carries_nothing_permission_gated():
    # D-1/T-ahy-05: the ONE assertion a mocked run_fn can honestly make
    # about the real-world failure -- no permission-gated argument is ever
    # sent on the create path. A mocked run_fn cannot prove GitHub accepts
    # the create call; it CAN prove the argv never carries the label flag.
    submit.submit_via_gh("My Title", "My Body", run_fn=run_fn)
    argv = run_fn.call_args[0][0]
    assert isinstance(argv, list)
    assert argv[0] == "gh"
    assert "--label" not in argv
    assert submit.GSD_INBOX_LABEL not in argv
    assert "gsd-inbox" not in " ".join(argv)
    assert "shell" not in run_fn.call_args.kwargs
```

**Existing repo-target pins already present:** `:217`, `:234`, **`:237` `assert submit.SUBMIT_REPO == "henols/firestarter_prom"`**, `:281`, `:392`, `:532`, `:649`, `:772`.

---

## Already-Landed: the `submit.py` repo retarget needs NO code change

The operator's item 6 was pulled in from Phase 121 as a MODIFY. **It is already done on this branch.**

- `firestarter/submit.py:73` → `SUBMIT_REPO = "henols/firestarter_prom"`, with a 7-line rationale comment at `:67-72` citing `firestarter_prom#6`.
- Landed in commit **`e615b4c` `fix(quick-260728-ahy): retarget SUBMIT_REPO to the project-wide tracker`** (was `henols/firestarter_app` at `94df3fa`, Phase 113).
- Present on `beta` as well (`git show beta:firestarter/submit.py` → `:73` same value).
- `v1.21` tag still carries the wrong value → this is why **`3.0.0b11` in the wild misfiles**. That is a *released-artifact* fact, not a source defect.

**Planner action:** convert this from a MODIFY task to a **verification-only task** — assert `submit.SUBMIT_REPO == "henols/firestarter_prom"` (already pinned at `test_submit.py:237`) and record in the SUMMARY that the fix pre-landed at `e615b4c` and reaches users only at the next beta cut. Do not re-fix. `tests/test_submit.py` needs no extension unless the planner wants an additional negative argv leg; if added, copy Idiom B.

---

## Pattern Assignments

### `firestarter/eprom_operations.py` → `sdp_unlock` / `sdp_lock` (service, payload-free request-response)

**Analog:** `erase_eprom`, `firestarter/eprom_operations.py:1628-1650` — **exact, copy verbatim shape twice.**

```python
    def erase_eprom(
        self,
        eprom_name: str,
        eprom_data_dict: dict,
        operation_flags: int = 0,
        address_str: Optional[str] = None,
    ) -> bool:
        with self._operation_context(
            eprom_name,
            eprom_data_dict,
            COMMAND_ERASE,
            operation_flags,
            address_str,
        ) as (cmd_data, _, op_name):
            if not cmd_data:
                return False
            logger.info(f"Erasing EPROM {eprom_name.upper()}")
            start_time = time.time()
            is_ok, final_msg = self._run_state_machine(op_name)   # ← NO main handler
            if is_ok:
                logger.info(
                    f"Erase for {eprom_name.upper()} successful ({time.time() - start_time:.2f}s). {final_msg or ''}"  # noqa: E501
                )
            return is_ok
```

Copy notes for the executor:
- Drop `address_str` (SDP takes no address). Keep `operation_flags: int = 0`.
- `_run_state_machine(op_name)` with no `main_phase_handler` → `_main_phase_simple`. Correct and intended.
- The success `logger.info` is where D-10's caveat text goes if the summary is emitted at this layer; RESEARCH F-11 recommends the **Click handler** instead — decide once, don't do both.
- The `noqa: E501` on the long f-string is the in-file convention for these log lines.

---

### `firestarter/eprom_operations.py` → `build_flags` new keyword-only param (utility, transform)

**Analog:** the same function, `:168-183` — `skip_erase` is the shape to mirror; D-19 requires the new one be keyword-only.

```python
def build_flags(
    blank_check=True, force=False, vpe_as_vpp=False, verbose=False, skip_erase=False
):
    flags = 0
    if not blank_check:
        flags |= FLAG_SKIP_BLANK_CHECK
    if skip_erase:
        flags |= FLAG_SKIP_ERASE
    if force:
        flags |= FLAG_FORCE
    ...
    return flags
```

⚠ Both production callers pass the **first four positionally** (`cli_handlers.py:275` and `:184-190`). Add `*, skip_sdp_unlock: bool = False` **after** `skip_erase`. Re-run `tests/test_bug_characterization.py` in the same plan.

---

### `firestarter/cli_handlers.py` → `dev sdp` handler (controller, request-response)

**Analog:** `dev test`, `firestarter/cli_handlers.py:1751-1847`.

**Group registration** (`:962-969`) — the `dev sdp` command hangs off this existing group; do not create a second group:
```python
@cli.group(name="dev")
@map_typed_errors
def dev() -> None:
    """Debug command for development purposes.

    USR button will break command and return.
    """
```

**TTY seam — import and call, do not re-implement** (`:1719-1726`):
```python
def _is_interactive() -> bool:
    """TTY check factored into its own function so tests can monkeypatch it
    directly (D-02) -- `click.testing.CliRunner.invoke` replaces `sys.stdin`
    with its own stream for the duration of the call, so a test-time
    `patch("sys.stdin.isatty", ...)` applied before `invoke()` does not
    survive; patching `firestarter.cli_handlers._is_interactive` does.
    """
    return sys.stdin.isatty()
```

**Consent gate + absent-chip hard-fail, verbatim from `:1829-1850`:**
```python
    interactive = _is_interactive()

    # SAFE-03: the ONLY interactive input left in this handler is the
    # --destructive safety confirm -- it is a safety gate, not tester-input
    # collection, and MUST stay. On a TTY (and not -y/--yes), require an
    # explicit "yes" before sacrificing the chip. Off-TTY, --destructive
    # itself is consent (no confirm possible without a TTY, D-02).
    if interactive and destructive and not assume_yes:
        proceed = Confirm.ask(
            "--destructive will sacrifice the chip. Continue?", default=False
        )
        if not proceed:
            click.echo("Aborted -- chip left untouched.")
            sys.exit(0)

    # SAFE-04: hard-fail BEFORE any hardware is energized when the chip name
    # is absent from the DB entirely (case A). Keyed strictly off
    # `get_eprom` emptiness -- NEVER a `resolve_chip` support-status refusal
    # -- so an in-DB-but-unsupported chip (case B, e.g. adapter-required)
    # still runs the full community-validation sweep below.
    if not app.db.get_eprom(chip):
        raise ChipNotFoundError(f"{chip}: not found in database")
```

## ⚠⚠ ORDERING INVERSION — READ BEFORE COPYING ⚠⚠

**The excerpt above is in the WRONG ORDER for `dev sdp`.** In-tree, `dev test` runs **confirm (`:1836-1842`) BEFORE absent-chip (`:1844-1850`)**. Phase 120's **D-08 requires the exact reverse**:

```
absent-chip  →  capability  →  support-status  →  confirm  →  serial
```

A verbatim copy prompts the user to consent to mutating a chip that is then refused — precisely what D-08's final clause forbids. **Copy the three mechanisms (`_is_interactive`, `Confirm.ask`+`sys.exit(0)`, `get_eprom`-emptiness `ChipNotFoundError`); re-sequence them; and ship a test that fails on the wrong order** (`mock_confirm.ask.assert_not_called()` for absent / capability-refused / `adapter-required`).

Two further deltas from the analog, both locked:
- **Drop the `--destructive` mode flag** (`:1755-1763`) — D-05. The subcommand is the mode.
- **Invert the off-TTY behaviour.** `dev test` *proceeds* off-TTY (`if interactive and destructive and not assume_yes` — the flag is the consent). D-06 requires `dev sdp` to **refuse** off-TTY without `-y`.
- Keep `sys.exit(0)` on an explicit user decline — a decline is not an error. D-11's `0/1` is about the *operation*.

---

### `firestarter/cli_handlers.py` → `write --skip-sdp-unlock` + `_build_op_flags` kwarg

**Analog:** `--skip-erase` on `write`, `:481-489` — same shape, same warning-in-help register:
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

**`_build_op_flags` (`:242-281`)** — the new kwarg is keyword-only by construction (`*` is already first) and threads into `build_flags`, **not** OR-ed after it (D-19 rejects the OE/CE style at `:276-279`):
```python
def _build_op_flags(
    *,
    blank_check: bool = True,
    force: bool = False,
    verbose: bool = False,
    vpe_as_vpp: bool = False,
    skip_erase: bool = False,
    input_enable: Optional[bool] = None,
    chip_disable: Optional[bool] = None,
) -> int:
    ...
    flags = build_flags(blank_check, force, vpe_as_vpp, verbose, skip_erase=skip_erase)
    if input_enable is not None:
        flags |= 0 if input_enable else FLAG_OUTPUT_ENABLE
    ...
    return flags
```

**`write`'s body (`:518-530`)** — the D-04 auto-set + report line belongs here, because this is the last place with the chip *name* and `app.db` (`resolve_chip`'s dict has neither — F-06):
```python
    eprom_data = resolve_chip(eprom, db=app.db)
    ok = app.eprom_operator.write_eprom(
        eprom, eprom_data, input_file,
        address_str=address,
        operation_flags=_build_op_flags(
            blank_check=blank_check, force=force,
            vpe_as_vpp=vpe_as_vpp, skip_erase=skip_erase,
        ),
    )
    sys.exit(0 if ok else 1)
```

Note the in-file docstring convention: long `TRAP #N / D-NN` explanation blocks documenting flag polarity (`write`'s docstring at `:502-517`). The `--skip-sdp-unlock` docstring must carry D-18's "no effect on non-`0x0D` protocols — warns and proceeds" in the same register.

---

### `firestarter/sdp_capability.py` (NEW — domain predicate, pure transform)

**Analog (WORDING ONLY):** `check_eprom_blank`'s pre-wire short-circuit, `firestarter/eprom_operations.py:1652-1677`:

```python
    # Protocol IDs whose firmware handler (configure_sram) leaves a NULL
    # firestarter_operation_main for CMD_BLANK_CHECK, causing 0xA4
    # MSG_ERR_EMPTY_INPUT.  These are all SRAM families (D-30 host-side fix).
    _SRAM_PROTO_IDS = frozenset({0x0E, 0x27, 0x28, 0x29})

    def check_eprom_blank(self, eprom_name, eprom_data_dict, operation_flags=0) -> bool:
        # D-30: SRAM/FRAM blank-check short-circuit — detect before issuing any
        # firmware command. ... Short-circuit with a clear message; do NOT touch
        # the wire protocol or firmware (D-11/D-30 bound).
        etype = eprom_data_dict.get("electrical-type", "")      # ← ANTI-PATTERN
        proto = eprom_data_dict.get("protocol-id", 0)           # ← ANTI-PATTERN
        if etype in ("SRAM", "FRAM") or proto in self._SRAM_PROTO_IDS:
            logger.warning(
                f"Blank check is not applicable to {eprom_name.upper()} "
                f"(electrical type: {etype or 'unknown'}, protocol: 0x{proto:02X}). "
                "SRAM/FRAM are volatile or byte-rewritable — they have no "
                "factory-blank state and the firmware has no blank-check op for them."
            )
            return False
```

**COPY:** the four-part reason wording register — name the chip (upper-cased), name the observed field values, state the mechanism, state the consequence. Also copy the module-constant-with-a-comment-explaining-why shape of `_SRAM_PROTO_IDS`.

**DO NOT COPY (anti-pattern, RESEARCH F-06):** the two `.get()` lines. Both production callers (`cli_handlers.py:576`, `chip_test.py:737`) pass `resolve_chip`'s **programmer dict**, whose measured keys are `{memory-size, algorithm, pin-count, vpp_mv, pulse-delay, chip-id, flags, bus-config}` — **no `protocol-id`, no `electrical-type`, no `name`.** Measured `False` for a real SRAM part this session. **This short-circuit is vacuous in production.** A dict-keyed `sdp_capability` reproduces that vacuity silently.

**Required shape instead:** `sdp_capability(chip_name: str, db) -> tuple[bool, str]`, reading `db.get_eprom(chip_name)` and keying on that dict's `name` (alias-joined `part_number`) + `protocol-id`. Keep `_SRAM_PROTO_IDS` in place unmodified (PROJECT.md SIXTH CORRECTION keep-disposition; only its *stated reason* is being corrected).

---

### `firestarter/serial_comm.py` → INFO-band promotion (middleware, event-driven)

**Analog:** the function's own existing arms, `:228-247` — add one `elif` in the same style:
```python
    def _log_rurp_feedback(self, response: Response) -> None:
        """Logs feedback from the programmer based on the parsed Response object."""
        if not response or not response.type:
            return

        message = response.message
        level = logging.DEBUG
        if response.type == "ERROR":
            level = logging.ERROR
        elif response.type == "WARN":
            level = logging.WARNING
        # ← D-09: add `elif response.type == "INFO": level = logging.INFO` HERE.
        #   Promote INFO ONLY. OK/INIT/MAIN/END/DATA stay on the DEBUG default
        #   (protocol-phase frames — promoting them floods default output).

        # Shorten prefix for debug, full for others
        log_prefix = (
            response.type[:1]
            if rurp_logger.isEnabledFor(logging.DEBUG)
            and response.type in NON_RESPONSE_PREFIXES
            else response.type
        )
        rurp_logger.log(level, f"{log_prefix}: {message}")
```

Note ⚠ the prefix side-effect: promoting `INFO` changes the rendered prefix from `I:` to `INFO:` under `-v`. A test asserting on the rendered string must expect that. (CONTEXT calls this function `_log_response`; the real name is `_log_rurp_feedback` — line numbers match.)

---

### `firestarter/serial_comm.py` → `0x86` ack observation (middleware, event-driven)

**Analog:** `_decode_id_frame`, `:249-280` — the documented override seam, with Phase 55's `firmware_max_chunk` as the identical precedent:
```python
    def _decode_id_frame(self, frame_len: int, body: bytes) -> Optional[LogMessage]:
        """Compatibility wrapper — see codec.decode_id_frame.

        CAP-01 (Phase 55): after decoding, when the message is MSG_OK_READY and
        the param region is exactly 2 bytes, extract the big-endian u16 and store
        it as firmware_max_chunk ...

        The GATE-1.8d ring-fenced _read_and_parse_lines body is not touched —
        only this override seam is used (Pitfall 4 / Open Question 3).
        """
        result = codec.decode_id_frame(frame_len, body)
        if result is not None and len(body) >= 2:
            ...
```
Copy the docstring register: name the phase + requirement id, state the trigger condition, state the graceful-degradation behaviour on old firmware, and restate the ring-fence non-touch. Record `0x86` into a per-connection `seen_message_ids: set[int]`; read it in `write_eprom` after `_run_state_machine` returns, gated on "the flag was set on this invocation".

---

### `firestarter/constants.py` (config)

**Analog:** in-file, `:55-99`. Three insertions, all in existing blocks:
```python
# Wire-protocol command codes — Firmware sync: firestarter.h
COMMAND_READ = 1
...
COMMAND_DEV_ADDRESS = 7
COMMAND_DEV_REGISTERS = 8      # NOTE: plural host-side, singular CMD_DEV_REGISTER in firmware
# ← COMMAND_SDP_UNLOCK = 9 / COMMAND_SDP_LOCK = 10 go HERE (fill the 9/10 gap)
COMMAND_READ_VPP = 11
...
COMMAND_NAMES = {
    COMMAND_READ: "READ",
    ...
    COMMAND_DEV_REGISTERS: "DEV_REGISTERS",
    # ← two new entries MANDATORY: _setup_operation does COMMAND_NAMES[cmd]
    #   at eprom_operations.py:301 AND :377 — two KeyError sites
    COMMAND_READ_VPP: "READ_VPP",
}

# Control Flags — Firmware sync: firestarter.h
FLAG_FORCE = 0x01
...
FLAG_VERBOSE = 0x80
# ← FLAG_SKIP_SDP_UNLOCK = 0x100 goes HERE, with a one-line comment
#   distinguishing it from CTRL_VPP_VPE_DROP_ENABLE = 0x100 at :117
#   (control-register namespace, not a wire flag)
```
The `# ... — Firmware sync: firestarter.h` banner comment above each block is the in-file convention; keep it accurate.

---

### `tests/test_sdp_capability.py` (NEW — invariant gate, batch)

**Analog:** `tests/test_sdp_db_invariant.py` — **copy verbatim structure.**

**Module docstring shape** (`:1-29`) — numbered Coverage list ending in an explicit non-vacuity item, plus the no-skip-marker paragraph:
```python
"""
DB invariant for the AT28C SDP `0x0D` identity gate (Phase 116 TRACE-05).

Reads firestarter/data/chip_database.json directly (not through EpromDatabase),
so this measures the shipped data rather than the loader's interpretation.

Coverage:
  1. Real-DB count: exactly 84 chip_database.json entries have
     programming.algorithm == 13 ...
  4. Non-vacuous proof: a synthetic in-memory DB dict ... IS flagged by the
     same shared helper the real test calls -- proves the invariant is capable
     of failing, not a vacuous always-pass check (RESEARCH F9's "hollow in one
     direction" warning).

This module intentionally carries NO FW_ABSENT-style skip marker: it reads
only the packaged chip_database.json, which is always present in host-only
CI. Keeping this concern in its own file ... prevents that skip marker from
leaking in here and silently making TRACE-05 vacuous in CI.
"""
```

**Path + constant + shared-helper block** (`:31-58`):
```python
import json
from pathlib import Path

_FA_DIR = Path(__file__).parent.parent
_DB_FILE = _FA_DIR / "firestarter" / "data" / "chip_database.json"
_ALGORITHM_0X0D = 13

# ---------------------------------------------------------------------------
# Shared helpers -- both the real-DB tests and the non-vacuity test call
# these, so the non-vacuity leg exercises the same code the real test does.
# ---------------------------------------------------------------------------

def _select_0x0d_chips(db: dict) -> list[tuple[str, dict]]:
    """... The DB shape is {manufacturer: [chip, ...]}, and the fields live in
    a nested "programming" object. A top-level scan on db ... finds nothing and
    would make every downstream assertion pass vacuously."""
    selected = []
    for _mfr, chips in db.items():
        for chip in chips:
            if chip["programming"]["algorithm"] == _ALGORITHM_0X0D:
                selected.append((_mfr, chip))
    return selected
```

**Non-vacuity leg** (`:151-184`) — copy the try/except/else inversion exactly; it is the shape that cannot silently pass:
```python
def test_synthetic_chip_id_check_true_is_flagged_non_vacuous() -> None:
    """Non-vacuity proof: ... Exercises the exact same _select_0x0d_chips /
    _assert_chip_id_check_false helpers the real-DB test above calls, not a
    parallel reimplementation."""
    synthetic_db = {"SYNTHETIC_MFR": [{"part_number": "SYNTHETIC_0x0D_VIOLATION",
        "programming": {"algorithm": 13, "chip_id_check": True,
                        "chip_id_value": "0x00000000"}}]}
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

**One leg with no analog in the tree — write it fresh (RESEARCH F-06):** the *dict-shape* leg asserting `"protocol-id" not in resolve_chip(...)` and `"name" not in resolve_chip(...)`, so the predicate can never become the vacuous `_SRAM_PROTO_IDS`-style check. Every `sdp_capability` test must get its dict from a real `EpromDatabase(skip_local_override=True)`, **never a literal** — `tests/test_chip_test.py` has 11 literal `protocol-id` dict constructions that are correct *there* and would prove nothing here.

---

### `tests/test_dev_sdp_cmd.py` (NEW — CLI test, request-response)

**Analog A:** `tests/test_dev_test_cmd.py` — the whole file's scaffolding.

Module docstring (`:1-24`) states the hardware-free contract and the `_is_interactive`-not-`sys.stdin.isatty` reason. Copy it.

`make_app_context` (`:68-91`) — the DB + `Mock(spec=...)` seam:
```python
def make_app_context(**overrides: object) -> AppContext:
    """Mirrors test_validate_family_cmd.py's make_app_context: EpromDatabase
    uses skip_local_override=True and every manager is Mock(spec=...) unless
    the caller overrides it. No real serial port or bench access is ever
    opened (SC4)."""
    db = overrides.pop("db", None)
    if db is None:
        db = EpromDatabase(skip_local_override=True)
    ...
    return AppContext(
        db=db, config_manager=config_manager,
        eprom_operator=overrides.pop("eprom_operator", Mock(spec=EpromOperator)),
        hardware_manager=overrides.pop("hardware_manager", Mock(spec=HardwareManager)),
        ...
    )
```

TTY seams (`:141-150`, `:315`) and the `Confirm` mock (`:301`, `:305-318`):
```python
@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()

def _off_tty():
    """Context manager forcing the off-TTY branch (D-02)."""
    return patch("firestarter.cli_handlers._is_interactive", return_value=False)

# TTY branch + confirm assertion:
        with (
            patch("firestarter.cli_handlers._is_interactive", return_value=True),
            patch("firestarter.cli_handlers.Confirm") as mock_confirm,
        ):
            mock_confirm.ask.return_value = True
            result = runner.invoke(cli, ["dev", "sdp", CHIP, "enable"], obj=app)
        assert result.exit_code == 0, result.output
        mock_confirm.ask.assert_not_called()   # ← for refusal cases
```

**Analog B — the load-bearing "no port opened" assertion:** `tests/test_hardware.py:56-60`:
```python
    with patch(
        "firestarter.serial_comm.SerialCommunicator.find_and_connect",
        return_value=comm,
    ):
        ok = hw.get_hardware_revision()
```
`find_and_connect` is where `_setup_operation` opens the port (`eprom_operations.py:332-336`), so `mock_find_and_connect.assert_not_called()` is the only assertion that distinguishes "refused **before** the wire" from "refused after connecting". **Exit-code-only refusal tests are a known false-green here** — an absent chip, a capability refusal and a support-status refusal all exit non-zero identically. Also assert on the *reason text* to prove **which** gate fired (an `adapter-required` `0x0D` part with no SDP must hear the capability message, not the adapter message — that is D-08's whole purpose).

---

### `tests/test_revision_constants_parity.py` (REWRITE — parity gate, source scan)

**Current state to be replaced** — 100% hollow, never reads the header (`:100-146`):
```python
    assert COMMAND_READ == 0x01  # CMD_READ
    ...
    # CMD_DEV_ADDRESS and CMD_DEV_REGISTER are #ifdef DEV_TOOLS in firmware —
    # assert Python values as standalone literals only:
    assert COMMAND_DEV_ADDRESS == 0x07  # #ifdef DEV_TOOLS in firmware
```
This is why `CMD_SDP_UNLOCK 9` / `CMD_SDP_LOCK 10` landed in Phase 119 unnoticed.

**Keep verbatim** — the `FW_ABSENT` guard block and its comment (`:47-58`), which doubles as the fixture-injection point:
```python
# ---------------------------------------------------------------------------
# Firmware-checkout presence guard (Phase 36 TEST-04 extension)
#
# The firmware sub-repo may be absent in CI environments. If firestarter.h is
# absent the three new parity functions skip cleanly. ...
# ---------------------------------------------------------------------------
FIRMWARE_HEADER = (
    Path(__file__).parent.parent.parent / "firestarter" / "include" / "firestarter.h"
)
FW_ABSENT = not FIRMWARE_HEADER.exists()

@pytest.mark.skipif(FW_ABSENT, reason="firestarter firmware checkout absent")
```
Also keep untouched: `test_revision_byte_values_match_firmware_enum` (`:61-75`, host-literals-only, deliberately unskipped) and `test_cmd_frame_max_parity` (`:188-214`, `CMD_FRAME_MAX`'s own D-07-acceptance gate — the parity extractor must treat `CMD_FRAME_MAX` as an enumerated exemption, not re-check it).

**Analog for the new parser:** `tools/check_is_memory_cmd_no_ifdef.py`.

REUSE `_strip_comments` (`:159-195`) — load-bearing, not hygiene: `firestarter.h`'s comment block above `CMD_SDP_UNLOCK` literally contains the strings `constants.py CMD_SDP_*`, `COMMAND_NAMES` and `#ifdef DEV_TOOLS`. Length- and line-preserving, so computed line numbers still map 1:1. Do **not** reuse `_find_function_body` / `_predicate_def_pattern` — they brace-match a function body; these are file-scope `#define`s.

**Fail-closed seam pattern** (`:85-94`) — for a pytest-hosted gate, translate the env var to a module-level path constant + `monkeypatch.setattr`, but keep the fail-closed comment verbatim in intent:
```python
# Env-override seam: lets the paired pytest point this checker at a
# deliberately-violating fixture file (tests/fixtures/planted_ifdef_in_predicate.h)
# without editing the real, clean firestarter.h (anti-hollow contract, D-04).
# This seam is FAIL-CLOSED: a path that does not exist is an ERROR, never a
# silent pass -- see main() below.
FIRESTARTER_CMD_ADMISSION_SRC = os.environ.get(
    "FIRESTARTER_CMD_ADMISSION_SRC", _DEFAULT_CMD_ADMISSION_SRC
)
```

**Exemption-table model** (`:99-118`) — a **frozen**, deliberately-edited set, explicitly NOT auto-derived, with a comment saying why. This is exactly the model for D-12's exemption *pair mapping*:
```python
# The frozen expected command set (D-02/D-04). Adding a ninth memory command
# is a DELIBERATE act that must edit this line -- it is not auto-derived from
# the header, because the whole point of this gate is to catch an
# accidental/unreviewed enumeration drift, not just mirror it.
# CMD_DEV_ADDRESS and CMD_DEV_REGISTER must NEVER appear here: they are
# conditionally defined (#ifdef DEV_TOOLS) in the firmware header ...
_EXPECTED_CMD_NAMES = frozenset({
    "CMD_READ", "CMD_WRITE", "CMD_ERASE", "CMD_BLANK_CHECK",
    "CMD_CHECK_CHIP_ID", "CMD_VERIFY", "CMD_SDP_UNLOCK", "CMD_SDP_LOCK",
})
```
⚠ D-12's exemption table must be a name-**pair** map, not a skip-set: firmware `CMD_DEV_REGISTER` (singular) ↔ host `COMMAND_DEV_REGISTERS` (plural). A naive `CMD_X → COMMAND_X` map reports a false gap and invites renaming a host constant that has callers.

---

### `tests/fixtures/planted_constants_drift.h` (NEW)

**Analog:** `tests/fixtures/planted_ifdef_in_predicate.h:1-30`. Six mandatory docstring elements listed in § "Two Things Checked" above. Its paired-test usage idiom (`tests/test_check_is_memory_cmd_no_ifdef.py:53`, `:123`):
```python
_FIXTURE = _FA_DIR / "tests" / "fixtures" / "planted_ifdef_in_predicate.h"
...
    result = _run_checker({"FIRESTARTER_CMD_ADMISSION_SRC": str(_FIXTURE)})
```
That file also carries the fail-closed legs to mirror (`:303-320`): a nonexistent path → exit 1 + `ERROR:` on stderr; a path with no target → exit 1.

---

### `.planning/ROADMAP.md` / `REQUIREMENTS.md` / `PROJECT.md` (D-20 amendment)

**Analog:** `.planning/phases/119-lock-sdp-enable-command-surface-fw-half/119-09-PLAN.md` — copy its frontmatter and prohibition shape:
```yaml
files_modified:
  - .planning/ROADMAP.md
  - .planning/REQUIREMENTS.md
  - .planning/PROJECT.md
  - .planning/STATE.md
autonomous: true
requirements: [DEVTEST-01]
```
```yaml
  prohibitions:
    - "MUST NOT tick DEVTEST-01's checkbox in REQUIREMENTS.md. Its host half is Phase 121."
    - "MUST NOT edit LOCK-04's or LOCK-06's requirement WORDING ... Only the ... mapping row and the traceability table may change"
    - "MUST NOT remove Phase 121 from ROADMAP.md or renumber any phase. Amend its scope text and criteria; the phase stays."
    - "MUST NOT touch either submodule. This plan is meta-repo only and both sub-repo working trees must stay clean."
    - "MUST NOT run `gsd roadmap phases.clear` or any destructive ROADMAP mutation. This project has 50-plus preserved phase directories that such a call would hard-delete."
```
Mechanics to copy: meta-repo-only commit staging explicit `.planning/` paths, never a submodule gitlink; **`Edit` for scoped replacements, never a wholesale rewrite** (`ROADMAP.md` is 2206 lines); `state.record-session` FIRST then progress/metric/decision, then hand-verify `current_phase_name` and `progress.percent`; never trust the returned `updated` array. Place this in the **last** wave so the correction block can cite this phase's own findings.

---

## Shared Patterns

### Refuse before the wire, with a spoken reason
**Source:** `firestarter/eprom_operations.py:1661-1676`
**Apply to:** `sdp_capability.py`, the `dev sdp` handler, the `write`-path auto-set
Four-part wording register: name the chip (upper-cased), name the observed field values, state the mechanism, state the consequence. `logger.warning`, then return `False` / raise — never a silent no-op, never a fabricated success.

### Honesty in the message text, never in a status code
**Source:** established over Phase 117 D-05 → 118 D-02 → 119 D-12
**Apply to:** the `dev sdp` summary line (D-10), the exit code (D-11), the D-15 missing-ack report
`sys.exit(0 if ok else 1)` is the universal in-tree shape (`cli_handlers.py:530` and every other command). A `0x87` WARN prints and does not change the code. Do not invent a tri-state.

### Every gate ships a planted-violation fixture proving it fails
**Source:** `tests/fixtures/planted_ifdef_in_predicate.h` + `tools/check_is_memory_cmd_no_ifdef.py`
**Apply to:** the rebuilt parity gate (fixture), the allow-set gate (synthetic non-vacuity dict)
Two flavours in-tree: an on-disk fixture behind a fail-closed path seam (source-scanning gates), and an in-memory synthetic dict fed to the *same shared helper* (data gates). Use the flavour matching the gate's input.

### Test seams that make gate ORDER provable, not just gate presence
**Source:** `tests/test_dev_test_cmd.py` (`_is_interactive` patch, `Confirm` mock) + `tests/test_hardware.py:56-60` (`find_and_connect` patch)
**Apply to:** every `dev sdp` refusal test
Three assertions per refusal case: `mock_confirm.ask.assert_not_called()`, `find_and_connect.assert_not_called()`, and an assertion on the reason **text**. Exit code alone is a known false-green.

### Argv assertions, never exit codes, for subprocess-shaped calls
**Source:** `tests/test_submit.py:275-291` (positive whole-argv) and `:301-320` (negative)
**Apply to:** any `test_submit.py` extension
State in the test comment what a mocked `run_fn` can and cannot honestly prove.

### `# ... — Firmware sync: <header>` banner on every mirrored constant block
**Source:** `firestarter/constants.py:55, 88`
**Apply to:** all three new constants
The meta `CLAUDE.md` duplication rule is enforced by this banner plus the parity gate.

### `noqa: E501` on long operator log f-strings
**Source:** `firestarter/eprom_operations.py:1648`
**Apply to:** the two new SDP operator methods' success lines
CI-scoped lint is `ruff check firestarter/ tests/` — validate against py3.9/3.11, not the devcontainer's 3.12.

---

## No Analog Found

| File / element | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `sdp_capability.py`'s **allow-set data table** (63 tokens with per-token provenance strings) | domain data | — | No curated part-number allow-table exists anywhere in the tree. `_SRAM_PROTO_IDS` (4 protocol ints) and `_EXPECTED_CMD_NAMES` (8 name strings) are the nearest in *shape* (frozen module constant + a why-comment) but neither is a token→provenance mapping. Use RESEARCH § F-01's enumerated 37/47 partition as the data source and § "Code Examples" as the container sketch. |
| `sdp_capability.py`'s **whole-entry unanimity rule** over comma-split aliases | domain logic | transform | No in-tree precedent. `database.py:488-504` does alias resolution but returns the *first* match; it never evaluates all tokens of an entry against a set. Fresh logic; see RESEARCH § F-02 rules 1-3. |
| The **dict-shape anti-vacuity test leg** | test | — | Nothing in the suite currently asserts the *absence* of a key to prove a predicate is not vacuous. Fresh; RESEARCH § "Code Examples" → `test_predicate_never_reads_a_programmer_dict_shape`. |
| **D-14's `MSG_ERR_UNKNOWN_CMD` → "firmware too old" mapping** | controller | request-response | No in-tree message-id→user-guidance remap exists. Nearest seam: `Response.id` populated at `serial_comm.py:398`, raised through `_raise_for_error_response` (`eprom_operations.py:447-451`, `:502-503`). Key on the **id**, never the text. |

---

## Metadata

**Analog search scope:** `firestarter_app/firestarter/`, `firestarter_app/tests/`, `firestarter_app/tools/`, `firestarter_app/tests/fixtures/`, `.planning/phases/119-*/`
**Files read this session:** `eprom_operations.py` (3 ranges), `cli_handlers.py` (5 ranges), `constants.py`, `serial_comm.py`, `submit.py` (grep), `tests/test_sdp_db_invariant.py` (2 ranges), `tests/test_revision_constants_parity.py` (3 ranges), `tests/test_dev_test_cmd.py` (4 ranges), `tests/test_submit.py` (3 ranges), `tests/test_hardware.py`, `tests/fixtures/planted_ifdef_in_predicate.h`, `tools/check_is_memory_cmd_no_ifdef.py`, `tests/test_check_is_memory_cmd_no_ifdef.py` (grep), `119-09-PLAN.md`
**Read-only constraint honoured:** no source file modified; `120-PATTERNS.md` is the only file written.
**Pattern extraction date:** 2026-07-29
