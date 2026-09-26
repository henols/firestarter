# Phase 134: The Plan-Derived SDP Oracle in `dev test` - Pattern Map

**Mapped:** 2026-08-04
**Measurement basis:** `firestarter_app` @ `gsd/v1.30-sdp-surface-retirement` **`57e8eb5`** (re-verified
this session: `git rev-parse --abbrev-ref HEAD` / `git rev-parse --short HEAD`). Every line number below
was read directly, not inherited from CONTEXT.md or RESEARCH.md.
**Files analyzed:** 11 modified + 1 genuinely new
**Analogs found:** 12 / 12 (11 exact/role-match in-file, 1 sibling-module match for the new file)

> ⚠ **Path convention.** Every `firestarter/…` path in CONTEXT.md/RESEARCH.md means
> `firestarter_app/firestarter/…`. The top-level `firestarter/` directory is the **Arduino firmware
> submodule and is not touched by this phase.** All paths below are absolute-from-repo-root and
> unambiguous.

> ⚠ **`firestarter_app/firestarter/eprom_operations.py` is RING-FENCED.** It appears in this document
> only as a *called dependency* (`write_eprom`, `read_eprom`, `sdp_lock`, `sdp_unlock`). **No edit
> analog is offered for it and none may be planned.**

---

## File Classification

| New/Modified File | Role | Data Flow | mypy island | Closest Analog | Match |
|-------------------|------|-----------|-------------|----------------|-------|
| `firestarter_app/firestarter/chip_test.py` (op constants + B generator + `_SDP_LEG_OPS`) | engine / config-constants | transform (pure) | **neither** (`check_untyped_defs=false`) | same file: `OP_SDP_LOCK`/`OP_SDP_UNLOCK` block `:302-310`, `_SDP_OPS` `:692-703`, `_WRITE_REGION_LENGTH` `:988-994` | **exact** |
| `firestarter_app/firestarter/chip_test.py` (`derive_plan` SDP emission) | engine / plan derivation | transform | neither | same file: `derive_plan`'s erase arm `:553-588` (supported/NA fork) + write arm `:513-534` (`write_execute` gate + `locked_destructive`) | **exact** |
| `firestarter_app/firestarter/chip_test.py` (new leg dispatcher + truth table) | engine / dispatch | request-response (single-run + read-back) | neither | same file: `_dispatch_sdp` `:1423-1473`; guard shape from `_dispatch_multi_run` `:1320-1330` + `:1368-1370`; temp-file/read-back mechanics `:1336-1379` | **exact** |
| `firestarter_app/firestarter/chip_test.py` (`_baseline_closes_sdp_gate` + `run_plan` wiring) | engine / gate | event-driven (per-step) | neither | same file: `_id_step_closes_gate` `:974-985` + its init `:854` / guard `:881-883` / set `:920-921` | **exact** |
| `firestarter_app/firestarter/chip_test.py` (cleanup de-registration) | engine / lifecycle | event-driven | neither | same file: the registration block `:890-918` + drain `:967-971` | **exact** |
| `firestarter_app/firestarter/chip_test.py` (`sdp_hold_state()` pure fn — the `HELD` derivation) | engine / pure derivation | transform | neither | same file: `_id_step_closes_gate` `:974-985` (pure `StepResult`→value fn) | role-match |
| `firestarter_app/firestarter/diagnostic_report.py` (str field + `to_dict` key + `SCHEMA_VERSION` 1.3) | report / serialisation | transform | neither | same file: `SCHEMA_VERSION` `:55` + its additive-bump comment ladder `:56-64`; `to_dict` `:436-454`; `_db_diff_dict` `:426-434` | **exact** |
| `firestarter_app/firestarter/cli_handlers.py` (D-14 exit precedence) | CLI / exit contract | request-response | **STRICT** | same file: `_VERDICT_EXIT_CODES` `:1887-1897` + `_verdict_code` `:1900-1902` + exit site `:2216-2219` | **exact** |
| `firestarter_app/firestarter/cli_handlers.py` (D-09 notice rewrite, D-12 recovery constants, LEG-14 constants) | CLI / prose constants | (none — static) | **STRICT** | same file: `_ALWAYS_WRITES_NOTICE` `:2064-2078` + its echo site `:2123` | **exact** |
| `firestarter_app/firestarter/cli_handlers.py` (D-15 exit floor + `sdp_hold_state` call-through) | CLI / composition | request-response | **STRICT** | same file: `report.banner = count_applicable(...)` `:2166`, `report.db_diff = build_db_diff(...)` `:2178` — the derive-in-engine/assign-in-handler seam | **exact** |
| `firestarter_app/tests/test_op_registration_parity.py` (6 coupled edits) | test / structural gate | transform (AST) | n/a | same file (self-analog): `assert len(_ALL_OPS) == 9` `:150-154`, `_REGISTRY_CONSTANT_NAMES` `:138-140`, exemption rows `:422-427`, disposition pins `:792-805` | **exact** |
| `firestarter_app/tests/test_chip_test_sdp_leg.py` (oracle proofs) | test / unit | transform | n/a | same file: `_OPERATOR_METHODS` `:198-208`, `_mock_operator` `:210-222`, `_plan_with_steps` `:224`, `_result` `:228` | **exact** |
| `firestarter_app/tests/test_dev_test_cmd.py` (LEG-17 R1–R6, exit pins, derived count) | test / CLI integration | request-response | n/a | same file: `make_clean_operator` `:83-105`, `_off_tty` `:144`, `_load_report` `:153`, `write_eprom.assert_not_called()` `:662`, notice-first pin `:227-250` | **exact** |
| `firestarter_app/tests/test_diagnostic_report.py` (LEG-12 JSON + no-boolean) | test / unit | transform | n/a | same file (existing `to_dict` key assertions) | role-match |
| **`firestarter_app/tests/test_sdp_recovery_wording.py`** (**NEW FILE**, LEG-14) | test / string-constant gate | transform | n/a | `firestarter_app/tests/test_sdp_table_parity.py::test_altered_temp_copy_fails_parity_non_vacuous` `:301-341` (non-vacuity shape) + `tests/test_check_sdp_capability.py` `:125-160` (planted-fixture legs) | role-match |

**Not mapped, deliberately:** `firestarter_app/firestarter/constants.py` (import target only —
`FLAG_SKIP_SDP_UNLOCK = 0x100` at `:137`, verified), `sdp_capability.py` / `sdp_honesty.py` (call
targets only), `eprom_operations.py` (ring-fenced).

---

## Pattern Assignments

### `firestarter_app/firestarter/chip_test.py` — new op constants + `_SDP_LEG_OPS`

**Analog:** the same file's Phase-133 block, `:302-310`.

**Op-constant declaration pattern** (`chip_test.py:302-310`) — copy the "engine-local, not a wire
constant" comment discipline verbatim in shape; the last sentence is the reason **no firmware header
sync is triggered** by this phase:

```python
# SDP lock/unlock op strings (v1.30 Phase 133 D-02, LEG-09). Exactly two --
# Phase 133 defines only the two ops its own mechanism criteria exercise;
# Phase 134's other leg ops are deliberately NOT pre-defined here (`ruff`'s
# `F` rules do not flag unused module-level constants, so extra constants
# would be genuinely dead code for a whole phase). Engine-local op strings,
# NOT wire constants -- no `constants.py` / `firestarter.h` mirroring is
# triggered by adding these.
OP_SDP_LOCK = "sdp-lock"
OP_SDP_UNLOCK = "sdp-unlock"
```

**Frozenset-registry pattern** (`chip_test.py:692-703`) — the argument for a module constant over a DB
field, which is exactly `_SDP_LEG_OPS`'s justification, plus the "documented-but-dead frozenset" self-
warning that forces a live reference:

```python
# LIVE DISPATCH ALLOW-LIST for the SDP arm (v1.30 Phase 133 D-01/D-02,
# LEG-09). `_dispatch_sdp` refuses any op outside this frozenset. A module
# constant is used rather than a DB field because anything that widens a
# blast radius is an engine constant in this module (the
# `_WRITE_REGION_LENGTH` / `_UV_WRITE_REGION_LENGTH` precedent) -- a
# DB-supplied op string could otherwise smuggle in an op this module never
# vetted. This module's own known failure mode is a documented-but-dead
# frozenset -- `_MULTI_RUN_OPS` once shipped with ZERO references tree-wide
# ...
_SDP_OPS = frozenset({OP_SDP_LOCK, OP_SDP_UNLOCK})
```

**Import-extension site** (`chip_test.py:37`, verified verbatim this session):

```python
from firestarter.constants import FLAG_CAN_ERASE  # 0x02 -- do NOT redefine; import
```
→ extend to also import `FLAG_SKIP_SDP_UNLOCK` (`firestarter_app/firestarter/constants.py:136`,
`= 0x100`, verified). **No new operator method and no ring-fence edit:** `write_eprom`'s
`operation_flags` is already a defaulted 4th positional parameter.

**Pattern-B generator (D-19) — the source it must NOT reuse** (`chip_test.py:64-72` / `:53-61`):

```python
def address_fold_byte(addr: int) -> int:
    return (addr ^ (addr >> 8) ^ (addr >> 16) ^ (addr >> 24)) & 0xFF

def generate_pattern(start: int, length: int) -> bytes:
    """Region-parameterized address-derived pattern (D-02). ..."""
    return bytes(address_fold_byte(start + i) for i in range(length))
```
⚠ **P-01, the milestone's headline pitfall:** this is *pure* in `(start, length)`. Any B derived by
calling `generate_pattern` again for the plan's region makes `A == B` and the oracle a tautology.
D-19's own generator + the "differ at **every** byte" assertion is the structural proof.

---

### `firestarter_app/firestarter/chip_test.py` — `derive_plan` SDP emission (LEG-01/02, D-18)

**Analog:** `derive_plan`'s own erase arm, `chip_test.py:553-588` (the supported/NA fork) and its write
arm `:513-534` (the `write_execute` gate + `locked_destructive`).

**The `write_execute` gate D-18 keys on** (`chip_test.py:463`, verified):

```python
    write_execute = write_scope in (_WRITE_SCOPE_FULL, _WRITE_SCOPE_PARTIAL)
```

**Destructive-step emission + `locked_destructive` pattern** (`chip_test.py:520-534`) — the shape all
six SDP steps follow under D-18:

```python
    if write_execute:
        write_op = OP_WRITE_PARTIAL if write_scope == _WRITE_SCOPE_PARTIAL else OP_WRITE
        steps.append(
            Step(
                op=write_op,
                supported=True,
                reason="",
                destructive=True,
                write_region=write_region,
            )
        )
    else:
        locked_destructive.append(
            (OP_WRITE, 'write_scope="none": write omitted (D-01)')
        )
```

**NA-step emission pattern with user-facing prose** (`chip_test.py:564-588`) — LEG-02's template; the
reason string is what `sdp_capability()`'s 41 refusal reasons drop into:

```python
    else:
        if protocol == _PROTOCOL_FLASH4:
            reason = "flash4 (0x05) auto-erases per page; no separate erase op"
        elif etype == "UV-EPROM":
            reason = "UV-EPROM has no electrical erase (UV light only)"
        ...
        steps.append(
            Step(op=OP_ERASE, supported=False, reason=reason, destructive=True)
        )
```

**`write-partial` precedent — why a new OP STRING beats a new `StepResult` field** (`chip_test.py:517-519`,
the exact sentence D-07 leans on):

```python
    # write_scope="partial" emits `OP_WRITE_PARTIAL` instead of `OP_WRITE`
    # (D-06, Phase 121 Plan 06) so the partial-vs-full distinction is visible
    # in the op string itself, everywhere `StepResult.op` is read.
```
(Reinforced at `chip_test.py:290-293`, which explicitly *stops* the vocabulary where a partner string
would encode zero new information — the test any new op name must pass.)

---

### `firestarter_app/firestarter/chip_test.py` — the leg dispatcher + no-default truth table (LEG-04…08)

**Analog:** `_dispatch_sdp` (`chip_test.py:1423-1473`) — **verbatim, this is the shape to clone.**
D-08 forbids changing `_dispatch_sdp`'s signature, so the four write-shaped ops need their **own**
dispatcher wearing this same guard → branch → terminal-raise idiom.

```python
def _dispatch_sdp(
    op: str, name: str, eprom_data: dict[str, Any], operator: Any
) -> StepResult:
    """...Structurally clones `_dispatch_multi_run`'s guard -> branch -> terminal
    `raise AssertionError` shape (D-01) rather than importing/reusing it, so
    the module gains no new idiom and criterion 5's deliberate-break test
    gets a single choke point to attack."""
    if op not in _SDP_OPS:
        return StepResult(
            op=op,
            verdict=VERDICT_BAD,
            run_count=0,
            reason=(
                f"op {op!r} is not in the SDP dispatch allow-list "
                "(_SDP_OPS) — refused fail-closed rather than falling "
                "through to an operator mutation method"
            ),
        )

    if op == OP_SDP_LOCK:
        is_ok = operator.sdp_lock(name, eprom_data)
    elif op == OP_SDP_UNLOCK:
        is_ok = operator.sdp_unlock(name, eprom_data)
    else:
        # Unreachable in practice: the fail-closed `_SDP_OPS` guard above
        # already refused any op outside {OP_SDP_LOCK, OP_SDP_UNLOCK} ...
        # `AssertionError` is not a `SerialError`, `HardwareOperationError`,
        # or `EpromOperationError`, so `_run_step`'s D-08 except chain does
        # not catch it and it escapes loudly ...
        raise AssertionError(f"unreachable: op {op!r} passed the _SDP_OPS guard")

    return StepResult(op=op, verdict=VERDICT_OK if is_ok else VERDICT_BAD, run_count=1)
```

⚠ **The last line is exactly what the truth table must NOT be.** `VERDICT_OK if is_ok else VERDICT_BAD`
is the boolean oracle P-03 exists to keep the leg away from. Under D-01/D-03 the bool is a
**precondition** term only; the verdict comes from the read-back.

**The peer terminal-raise** (`_dispatch_multi_run`, `chip_test.py:1360-1370`) — the same idiom, and its
comment names the pre-Phase-121 regression the shape prevents:

```python
            else:
                # Unreachable in practice: the fail-closed `_MULTI_RUN_OPS`
                # guard at the top of this function already refused any op
                # outside {...} before this loop could start ...
                # Kept explicit rather than a bare `else: # OP_ERASE`
                # -- the pre-fix shape that silently routed an unmapped op to
                # `erase_eprom()` (RESEARCH Pitfall 1a).
                raise AssertionError(
                    f"unreachable: op {op!r} passed the _MULTI_RUN_OPS guard"
                )
```

**Temp-source-file + write-call mechanics to copy** (`chip_test.py:1336-1352`) — and the measured proof
that **no `operation_flags` is passed today**, which is what the `write-inhibited` step changes:

```python
    region_start, region_length = _write_region_for(step, eprom_data)
    expected = generate_pattern(region_start, region_length)
    if op in (OP_WRITE, OP_WRITE_PARTIAL, OP_VERIFY):
        tmp_fh = tempfile.NamedTemporaryFile(
            prefix="chip_test_pattern_", suffix=".bin", delete=False
        )
        try:
            tmp_fh.write(expected)
        finally:
            tmp_fh.close()
        tmp_source_path = tmp_fh.name
    ...
                outcomes.append(operator.write_eprom(name, eprom_data, tmp_source_path))
```

**Best-effort read-back precedent** (`chip_test.py:1372-1379`) — note the *opposite* policy applies to
the new dispatcher: here a read-back failure must not flip a verdict; in the oracle the read-back **is**
the verdict, and D-04's length gate must run *before* any `_diff_offsets`/`classify_fingerprint` call.

**Dispatch-arm placement** (`chip_test.py:1159-1190`) — the new arm goes **after** arm 5 and **above**
the terminal fail-closed `return`, or `test_shipped_ops_never_reach_sdp_arm` breaks:

```python
    if step.op in _MULTI_RUN_OPS:
        return _dispatch_multi_run(...)          # arm 4  (:1159-1162)
    ...
    if step.op in _SDP_OPS:
        return _dispatch_sdp(step.op, name, eprom_data, operator)   # arm 5  (:1180-1181)
    # <-- NEW ARM 6 HERE
    return StepResult(
        op=step.op,
        verdict=VERDICT_BAD,
        run_count=0,
        reason=(
            f"op {step.op!r} matched no dispatch arm — refused fail-closed "
            "rather than falling through to _dispatch_multi_run"
        ),
    )                                              # terminal, :1182-1190
```

---

### `firestarter_app/firestarter/chip_test.py` — `_baseline_closes_sdp_gate` (D-08 / D-20)

**Analog:** `_id_step_closes_gate`, `chip_test.py:974-985` — **the structural template**, verbatim:

```python
def _id_step_closes_gate(result: StepResult) -> bool:
    """SWEEP-03: close the destructive gate on an id-check failure/mismatch.

    Closes on `is_ok is False` (chip-ID check failed), a detected id that
    differs from the DB's expected `chip-id` (Pitfall 4's explicit mismatch
    case), OR the step itself erroring/being skipped -- ANY id-uncertainty
    gates destructive steps shut, not just an explicit numeric mismatch.
    A `NA` id step ... does NOT close the gate ...
    """
    return result.verdict in (VERDICT_BAD, VERDICT_SKIPPED)
```
D-08's variant closes on **any** non-OK verdict (BAD, marginal, SKIPPED, NA) — a strictly wider
predicate than the analog, so state the widening in the docstring rather than copying the analog's
narrow tuple.

**Its three wiring sites in `run_plan`** (all verified this session):

*Init, beside the existing flag* (`chip_test.py:853-854`):
```python
    results: list[StepResult] = []
    destructive_gate_closed = False
```

*Guard clause — the new one goes immediately after `:883`* (`chip_test.py:876-888`):
```python
        for step in plan.steps:
            if not step.supported:
                results.append(_skip_result(step.op, step.reason, verdict=VERDICT_NA))
                continue

            if step.op in _DESTRUCTIVE_OPS and destructive_gate_closed:
                results.append(_skip_result(step.op, _DESTRUCTIVE_GATE_REASON))
                continue
            # <-- NEW: `if step.op in _SDP_LEG_OPS and baseline_gate_closed:` here,
            #     with its OWN reason constant, never _DESTRUCTIVE_GATE_REASON
            result = _run_step(
                plan.name, step, operator, db, runs=runs, sampler=sampler
            )
            results.append(result)
```
⚠ **Order is load-bearing:** the ID gate fires first and renders its own wording. `_DESTRUCTIVE_GATE_REASON`
(`chip_test.py:705-707`) reads *"chip-ID mismatch — destructive steps gated (chip left pristine)"* — telling
a reader the chip ID closed the gate when the write path did is exactly what D-08 forbids. Author a
sibling `_SDP_BASELINE_GATE_REASON` module constant next to it.

*Set clause — the new one goes immediately after `:921`* (`chip_test.py:920-921`):
```python
            if step.op == OP_ID:
                destructive_gate_closed = _id_step_closes_gate(result)
```

**Cleanup de-registration (OQ-2)** — analog is the registration block itself (`chip_test.py:869`,
`:890-918`, `:967-971`). The registry declares itself **generic** at `:855-868` (*"deliberately GENERIC
rather than a hardcoded lock-to-unlock window"*), which is why `cleanup.remove(handle)` is correct and
`cleanup.clear()` over-reaches:

```python
    cleanup: list[Callable[[], None]] = []                       # :869
    ...
            if step.op == OP_SDP_LOCK and result.verdict == VERDICT_OK:   # :890
                def _unlock_cleanup() -> None:                   # :909  (a nested def,
                    _run_step(                                   #        NOT a lambda --
                        plan.name,                               #        the StepResult must
                        Step(op=OP_SDP_UNLOCK, supported=True, reason=""),
                        operator, db, runs=runs,                 #        be DISCARDED and the
                    )                                            #        inferred return type
                cleanup.append(_unlock_cleanup)                  # :918   must be None)
    finally:
        for cleanup_call in cleanup:                             # :967
            try:
                cleanup_call()
            except _UNLOCK_CLEANUP_SWALLOWED:
                continue
```
The `finally` block's comment at `:940-943` already names this phase: *"The registry is empty on every
currently-shipping run in this phase ... so this is LATENT here and would DETONATE in Phase 134."*

---

### `firestarter_app/firestarter/chip_test.py` — `sdp_hold_state()` (the `HELD` derivation)

**Analog:** `_id_step_closes_gate` `:974-985` — a small pure function over `StepResult`, module-level,
no logger, no I/O. `chip_test.py` has **no logger and no `logging` import** (stated at `:960-963`); keep
it that way.

⚠ **Structurally forced here, not a preference:** the derivation may **not** live inside
`DiagnosticReport`. See the inversion-guard shared pattern below.

---

### `firestarter_app/firestarter/diagnostic_report.py` — the `HELD`/`NOT-HELD`/`NOT-RUN` field (LEG-12, D-10)

**Analog:** the same file's `SCHEMA_VERSION` ladder and `to_dict`.

**Additive-bump precedent** (`diagnostic_report.py:54-64`, verified — this is the exact argument D-10
reuses for 1.2 → 1.3):

```python
SCHEMA_VERSION = "1.2"  # D-02: single-sourced, baked into to_dict() output
# 1.1 (Phase 114, GRAD-01): additive db_diff.ladder_state key -- backward
# compatible, existing consumers reading current_support_status/
# proposed_disposition are unaffected.
# 1.2 (Phase 121 Plan 06/07, D-06): the bump marks the seventh op string
# (`OP_WRITE_PARTIAL = "write-partial"`, chip_test.py) entering the report
```

**`to_dict()`'s nine keys** (`diagnostic_report.py:430-448`, verified — `to_dict` is at **`:436`**, not
`:444`; `:444` is the `schema_version` line *inside* it):

```python
    def to_dict(self) -> dict[str, Any]:
        """CANONICAL serializable mapping -- the single source both render()
        and to_json_block() consume (RPT-01, D-01). Hand-written (NOT
        `dataclasses.asdict()` wholesale, Pitfall 3) ..."""
        return {
            "schema_version": SCHEMA_VERSION,
            "generated": self._utc_now(),
            "auto_capture": self._auto_capture_dict(),
            "transport_health": self._transport_dict(),
            "steps": [self._step_dict(r) for r in self.results],
            "banner": self._banner_dict(),
            "voltage": self._voltage_dict(),
            "is_submittable": is_submittable(self.auto_capture),
            "dedup_fingerprint": dedup_fingerprint(self),
            "db_diff": self._db_diff_dict(),
        }
```
The new key is a **tenth**, carrying a plain assigned `str`. `_db_diff_dict` (`:426-434`) is the
precedent for a nullable, generically-serialised field.

**`render()`'s per-step row** (`diagnostic_report.py:471-476`, verified) — **D-07's entire basis:
`reason` is absent from the console**:

```python
        for step_row in d["steps"]:
            table.add_row(
                f"step: {step_row['op']}",
                f"{step_row['verdict']} (err={step_row['error_code']}, "
                f"fingerprint={step_row['fingerprint']})",
            )
```
`reason` reaches only `_step_dict` (`:406-415` → JSON) and the markdown table
(`cli_handlers.py:2197-2198`). Any "put the detail in `reason`" instinct is invisible to whoever reads
the terminal.

**Banner row** (`diagnostic_report.py:488-489`) — LEG-13's visible surface, the "4 of 4" → "5 of 10"
change; **no code edit here**:
```python
        banner = d["banner"]
        table.add_row("banner", f"{banner['n_ran']} of {banner['m_applicable']} ran")
```

---

### `firestarter_app/firestarter/cli_handlers.py` — exit precedence (D-14) and floor (D-15)

**Analog:** the same file's exit machinery. ⚠ **STRICT mypy island** (`disallow_untyped_defs = true`) —
any new helper needs full annotations. Headroom is **2** (33 vs watermark 35).

**Current shape** (`cli_handlers.py:1884-1899`, verified verbatim — note the comment is *false today*):

```python
# Per-verdict -> exit-code mapping (D-01): OK/NA/SKIPPED are exit-clean;
# `marginal` is an inconclusive result (exit 2); BAD beats marginal via
# `max` over the whole result set, mirroring dev_validate_family's own
# `if verdict_int > overall_verdict` pattern (cli_handlers.py:1620-1621).
_VERDICT_EXIT_CODES = {
    VERDICT_OK: 0, VERDICT_NA: 0, VERDICT_SKIPPED: 0,
    VERDICT_MARGINAL: 2, VERDICT_BAD: 1,
}

def _verdict_code(verdict: str) -> int:
    """Map a single StepResult verdict to its 0/1/2 exit-code contribution."""
    return _VERDICT_EXIT_CODES.get(verdict, 0)
```

**Exit site** (`cli_handlers.py:2213-2216`, verified):
```python
    if not results:
        sys.exit(0)
    code = max(_verdict_code(r.verdict) for r in results)
    sys.exit(code)
```
`max(1, 2) = 2` ⇒ marginal beats BAD. **The named in-repo precedent for explicit precedence** the
comment itself points at is `dev_validate_family`'s `if verdict_int > overall_verdict` at
`cli_handlers.py:1620-1621` — copy an explicit-precedence form, not another `max`.

⚠ `_verdict_code`'s `.get(verdict, 0)` is why **no sixth verdict status** may be introduced: an
unrecognised verdict exits **0**.

**Engine-derives / handler-assigns seam** (`cli_handlers.py:2161-2175`, verified) — the analog for
D-15's `sdp_hold_state` call-through; every derived value is computed in an engine module and *assigned*
here:
```python
    results = run_plan(plan, app.eprom_operator, app.db, sampler=sampler)
    report.results = results
    report.banner = count_applicable(plan, results)
    ...
    report.db_diff = build_db_diff(chip, app.db, results)
```

---

### `firestarter_app/firestarter/cli_handlers.py` — the notice (D-09) and recovery constants (D-12/D-13)

**Analog:** `_ALWAYS_WRITES_NOTICE` (`cli_handlers.py:2061-2075`, verified verbatim):

```python
# D-04: printed FIRST, unconditionally, before the SAFE-04 absent-chip
# hard-fail and before anything that touches hardware -- an unknown chip
# seeing this notice is harmless and honest, and printing first guarantees
# it precedes anything that could energise the shield. States the doubled
# run count truthfully (run_plan's runs>=2 default means every destructive
# step executes twice) and never calls any path non-destructive or
# read-only, because none is (D-04, RESEARCH Open Question 2).
_ALWAYS_WRITES_NOTICE = (
    "dev test ALWAYS WRITES to the chip -- run it only on a blank or "
    "scratch part you are willing to sacrifice. Every write/verify/erase "
    "step runs TWICE per invocation, so most chips receive the full device "
    "written twice; ..."
)
```

**Echo pattern** (`cli_handlers.py:2120`) — D-12's two recovery forms use the same `click.echo`, not a
logger, so they reach `CliRunner` capture regardless of log-level wiring:
```python
    click.echo(_ALWAYS_WRITES_NOTICE)
```
Its neighbours for a *late* echo (after the report exists) are `report.render(console)` at `:2181` and
`console.print(...)` at `:2207`.

⚠ **Two constraints on the rewritten prose, both structural:**
1. It must contain **no hyphenated op literal** (`sdp-lock`, `write-inhibited`, …) — see the inversion
   guard below. Write `SDP lock` (space, prose). The current notice survives only because
   *"write/verify/erase"* are single-word ops, which are deliberately excluded.
2. It cannot carry a per-chip derived count — it is echoed before `derive_plan` (`:2138`) and before
   `read_hardware_revision_value` (`:2150`, the first thing that energises). D-09's derived-count test
   pins the static number against a live `derive_plan` instead.

---

### `firestarter_app/tests/test_op_registration_parity.py` — six coupled edits (must ship in the same commits)

**Analog:** the file itself. ⚠ **There is no green intermediate state** — the module-level assert fires
at *collection*, so the first new `OP_*` constant turns all seven tests into collection errors.

**The collection-time assert** (`:150-154`, verified — `9` → `13`):
```python
assert len(_ALL_OPS) == 9, (
    f"measured {len(_ALL_OPS)} OP_* string constants in chip_test.py, "
    "expected 9 -- the census baked into this module's docstring and "
    "_POLICED_REGISTRIES/_OP_REGISTRY_EXEMPTIONS needs re-measuring"
)
```

**`_REGISTRY_CONSTANT_NAMES`** (`:138-140`) — a new `_SDP_LEG_OPS` frozenset will **not** resolve
transitively unless added here:
```python
_REGISTRY_CONSTANT_NAMES: frozenset[str] = frozenset(
    {"_DESTRUCTIVE_OPS", "_MULTI_RUN_OPS", "_SDP_OPS"}
)
```

**`_MULTIWORD_OP_VALUES`** (`:142-148`) — derived; all four new ops auto-join and become forbidden
substrings for every declared non-registry constant:
```python
_MULTIWORD_OP_VALUES: frozenset[str] = frozenset(v for v in _ALL_OPS if "-" in v)
```

**`_POLICED_REGISTRIES` / `_POLICED_REGISTRY_COUNT`** (`:231-246`) — if `_SDP_LEG_OPS` is policed, the
count goes 6 → 7:
```python
_POLICED_REGISTRIES: dict[str, frozenset[str]] = {
    "_DESTRUCTIVE_OPS": chip_test_mod._DESTRUCTIVE_OPS,
    "_MULTI_RUN_OPS": chip_test_mod._MULTI_RUN_OPS,
    "_SDP_OPS": chip_test_mod._SDP_OPS,
    "_dispatch_step": _op_names_referenced_in("_dispatch_step", _CHIP_TEST_SOURCE),
    "derive_plan": _op_names_referenced_in("derive_plan", _CHIP_TEST_SOURCE),
    "_dispatch_multi_run": _op_names_referenced_in("_dispatch_multi_run", _CHIP_TEST_SOURCE),
}
_POLICED_REGISTRY_COUNT = 6
```

**The two dischargeable exemption rows** (`:420-427`, verified — **two, not five**; the other "134"
mentions at `:388-394` (LEG-09's permanent asymmetry) and `:309-314` (a non-registry row) are **not**
dischargeable):
```python
    # --- derive_plan: this phase's real, deliberately-deferred omission
    # (D-11) -- Phase 134 discharges it. ---
    (OP_SDP_LOCK, "derive_plan"): (
        "Phase 134 surface -- not derived as a plan step in 133 (D-11)."
    ),
    (OP_SDP_UNLOCK, "derive_plan"): (
        "Phase 134 surface -- not derived as a plan step in 133 (D-11)."
    ),
```
**Test-7 disposition pins to flip** (`:801-802`, verified):
```python
        ("derive_plan", OP_SDP_LOCK): False,      # -> True
        ("derive_plan", OP_SDP_UNLOCK): False,    # -> True
```

**Exemption-row prose pattern to copy for the ~12 new rows** (`:400-411`) — every row is a real
sentence naming the decision, never a placeholder:
```python
    (OP_SDP_LOCK, "_MULTI_RUN_OPS"): (
        "D-03: SDP emissions are single-run and explicitly excluded from "
        "_MULTI_RUN_OPS -- a lock/unlock's result cannot be read back at "
        "all on this family (Phase 117 D-05, Phase 119 D-12), so the "
        "marginal-on-disagreement policy is meaningless for it."
    ),
```

**Non-vacuity leg to leave untouched but confirm still green** (`:753-778`) — the in-memory-altered-copy
shape; note the `try/except/else: raise` form, which is the house non-vacuity idiom:
```python
def test_altered_registry_copy_fails_parity_non_vacuous() -> None:
    altered = dict(_POLICED_REGISTRIES)
    altered["_DESTRUCTIVE_OPS"] = frozenset(
        op for op in altered["_DESTRUCTIVE_OPS"] if op != OP_WRITE
    )
    assert altered["_DESTRUCTIVE_OPS"] != _POLICED_REGISTRIES["_DESTRUCTIVE_OPS"], (
        "Fixture setup error: removing OP_WRITE from the altered copy did "
        "not change it -- this fixture needs updating."
    )
    try:
        _assert_op_parity(altered, _OP_REGISTRY_EXEMPTIONS, _ALL_OPS, _PARITY_CONTEXT)
    except AssertionError:
        pass
    else:
        raise AssertionError("Non-vacuity failure: ...")
```

---

### `firestarter_app/tests/test_chip_test_sdp_leg.py` — the oracle proofs (LEG-03…08, 16)

**Analog:** the module's own harness, `:186-232` (verified verbatim):

```python
_REAL_DB = EpromDatabase(skip_local_override=True)

_OPERATOR_METHODS = [
    "check_eprom_id", "read_eprom", "check_eprom_blank",
    "write_eprom", "verify_eprom", "erase_eprom",
    "sdp_lock", "sdp_unlock",
]

def _mock_operator(**returns):
    op = Mock(spec=_OPERATOR_METHODS)
    op.check_eprom_id.return_value = (True, 0x1234)
    op.read_eprom.return_value = True
    op.check_eprom_blank.return_value = True
    op.write_eprom.return_value = True
    op.verify_eprom.return_value = True
    op.erase_eprom.return_value = True
    for name, value in returns.items():
        getattr(op, name).return_value = value
        getattr(op, name).side_effect = None
    return op

def _plan_with_steps(*steps):
    return Plan(name="M8720", steps=list(steps))

def _result(results, op):
    for r in results:
        if r.op == op:
            return r
    raise AssertionError(f"no result for op {op!r} in {[r.op for r in results]}")
```
⚠ **`Mock(spec=_OPERATOR_METHODS)` is a name allow-list.** The oracle's read-back needs
`operator.read_eprom` to return *bytes-shaped* data, not `True` — the LEG-16 dead-write-path double
(`write_eprom → True`, `read_eprom` always yields `A`) and the four degenerate doubles must override
`read_eprom` explicitly. The module carries **no** syrupy capture and **no** firmware-sibling decorator
(stated in its header) — keep new legs the same so they run in standalone CI.

---

### `firestarter_app/tests/test_dev_test_cmd.py` — LEG-17 routes, exit pins, derived count

**Analog:** the module's own harness and existing exit tests.

**Operator double** (`:83-105`) — note `Mock(spec=EpromOperator)` (the **real class**), so `sdp_lock` /
`sdp_unlock` exist on it automatically and `sdp_lock.assert_not_called()` works with no builder change:
```python
def make_clean_operator() -> Mock:
    operator = Mock(spec=EpromOperator)
    operator.check_eprom_id.return_value = (True, None)
    operator.read_eprom.return_value = True
    ...
```
Its docstring points at `tests/conftest.py`'s `make_app_context` risk-A explanation for why the return
type is `Mock`, not `EpromOperator` — **do not "fix" that annotation**; it relocates errors onto every
mock-assertion site (and the strict-island headroom is 2).

**Helpers** (`:144-155`):
```python
def _off_tty():
    """Context manager forcing the off-TTY branch (D-03)."""
    return patch("firestarter.cli_handlers._is_interactive", return_value=False)

def _reports_dir() -> Path:
    return Path(get_config_dir()) / "reports"

def _load_report(chip: str) -> dict:
    return json.loads((_reports_dir() / f"dev-test-{chip}.json").read_text())
```

**The `assert_not_called()` idiom LEG-17's six routes extend** (`:650-662`) — note it pairs an exit-code
assertion with a *negative argv/call* assertion, which is what stops an exit-code-only false green:
```python
    def test_chip_id_mismatch_exits_1(self, runner: CliRunner) -> None:
        operator = make_clean_operator()
        operator.check_eprom_id.return_value = (True, 0xDEAD)
        app = make_app_context(
            eprom_operator=operator, hardware_manager=make_hardware_manager()
        )
        with _off_tty():
            result = runner.invoke(cli, ["dev", "test", _CHIP_WITH_ID], obj=app)
        assert result.exit_code == 1, result.output
        operator.write_eprom.assert_not_called()
```
LEG-17 requires **both** `sdp_lock.assert_not_called()` **and** a visible `NOT-RUN` reason — the second
half is the analog's missing leg, and it is what stops R6 (steps absent entirely) from passing.

**Exit-code tests D-14 must be audited against** (`:628-671`) — RESEARCH §4.6 discharged the audit:
`test_marginal_disagreement_exits_2` (`:639`) and the parametrised `marginal` row (`:669`) produce
**no BAD**, so D-14 has zero blast radius. Its non-vacuity leg must be a **new** mixed BAD+marginal test.

**Notice-first pin D-09 must keep green** (`:226-250`):
```python
class TestAlwaysWritesNotice:
    def test_always_writes_notice_is_the_first_line_unconditionally(...)
        ...
        first_line = next(line for line in result.output.splitlines() if line.strip())
        assert first_line == _ALWAYS_WRITES_NOTICE
```
It asserts identity against the imported constant, so a *rewrite* keeps it green — which is exactly why
D-09 additionally needs the derived-count test (P-08: this test checks no content).

**Fixture base** — `tests/conftest.py`'s `make_app_context` (`:229-321`, fully annotated, six
keyword-only params) and the `app_context` fixture (`:325-334`). `make_app_context`'s docstring
(`:275-285`) states that its own body is type-checked from birth because it is fully annotated, with
**zero `pyproject.toml` change** — reuse it; do not add a conftest fixture.

---

### `firestarter_app/tests/test_sdp_recovery_wording.py` — **NEW FILE** (LEG-14)

**Closest analogs (two, combined):**

**(a) The non-vacuity shape** — `tests/test_sdp_table_parity.py::test_altered_temp_copy_fails_parity_non_vacuous`
(`:301-341`, verified). Copy the *fixture-setup assertion → try/except/else: raise* structure:
```python
    original = _EEPROM_28C_CPP.read_text(encoding="utf-8")
    altered = original.replace("{0x5555, 0x20}", "{0x5555, 0x21}", 1)
    assert altered != original, (
        "Fixture setup error: the byte replacement did not apply -- ..."
    )
    ...
    try:
        _assert_pairs_equal(sdp_pairs, flash_pairs, _PARITY_CONTEXT)
    except AssertionError:
        pass
    else:
        raise AssertionError(
            "Non-vacuity failure: altering one byte in the temp fixture did "
            "not make the parity assertion fail -- the parser or the "
            "parity gate is vacuous."
        )
```
That module also carries the **fail-closed seam** precedent (`:349-354`): pointing the override env var
at a nonexistent path must **raise**, never silently pass.

**(b) The planted-fixture idiom** — `tests/fixtures/planted_permit_by_default.py` +
`tests/test_check_sdp_capability.py:125-160`. The fixture header states the contract to copy verbatim
in shape:
```
"""Deliberately-violating fixture for tools/check_sdp_capability_invariants.py.

This file must never be imported. It exists only as AST-scan input for
GATE-01's Class 1 (permit-by-default, D-14) planted-violation pytest leg ...
Never imports anything from the `firestarter` package -- it is scannable
standalone ...
"""
```
and its test leg (`test_check_sdp_capability.py:129-140`) injects it via an **env-var seam**
(`FIRESTARTER_SDP_CAPABILITY_SRC`), never by monkeypatching the checker. That module also carries the
positive-control legs this new file needs: `test_checker_exits_zero_on_clean_source` (`:76`),
`test_default_target_resolves_to_an_existing_file` (`:94`), `test_fail_closed_on_missing_target`
(`:217`), `test_fail_closed_on_zero_symbol_scan` (`:237`).

**Adaptation for LEG-14 (D-13):** the scan target is *named module-level constants in
`cli_handlers.py`*, not a whole report and not a `tools/` script (that scanner is Phase 137's CLOSE-03).
Import the constants directly and assert: `"rewrite"` present, `"erase"` absent, **plus** no hyphenated
op literal (folding OQ-5's hazard into the same place). The planted-violation leg plants a local
constant saying "erase" and asserts the scan function fails on it.

⚠ **Why a whole-report grep is ruled out (measured, three legitimate "erase" sites):**
`chip_test.py:577-580` (*"protocol 0x0D (28C family) has no erase operation; each page write
auto-erases internally"*), the `erase` op string itself in the markdown table and JSON, and
`_ALWAYS_WRITES_NOTICE`'s *"write/verify/erase step"* (`cli_handlers.py:2070`).

---

## Shared Patterns

### 1. Fail-closed dispatch: guard → branch → terminal `raise`, never a bare `else`
**Source:** `firestarter_app/firestarter/chip_test.py:1320-1330` + `:1368-1370` (`_dispatch_multi_run`),
cloned at `:1442-1471` (`_dispatch_sdp`).
**Apply to:** the new leg dispatcher, the truth table, and every new `run_plan` arm.
The comment at `:1361-1367` names the regression this prevents: the pre-Phase-121 bare `else: # OP_ERASE`
routed **any** unmapped op to `operator.erase_eprom()` and reported `VERDICT_OK`.
`AssertionError` is deliberately outside `_run_step`'s except chain, so it escapes loudly.

### 2. The op-parity **inversion guard** — three structural prohibitions
**Source:** `firestarter_app/tests/test_op_registration_parity.py:579-594` (`_count_op_vocabulary_references`),
`:608-652` (`_measure_op_vocabulary`), `:733-745` (`test_non_registry_still_has_no_ops`).
Failure message: *"A declared non-registry has acquired op vocabulary -- PROMOTE it to
`_POLICED_REGISTRIES`, do not loosen this guard."*

Declared non-registries in this phase's path (`:276-326`, verified): `count_applicable` (function),
`dedup_fingerprint` (function), **`DiagnosticReport`** (class locator, whole body), `_ALWAYS_WRITES_NOTICE`
(constant locator — a live **substring** test at `:613-617`).

**Therefore:**
- ❌ Do **not** compare op strings inside `DiagnosticReport` — including in `to_dict`, `render` or
  `_step_dict`. Derive `HELD`/`NOT-HELD`/`NOT-RUN` in `chip_test.py` and assign a plain `str`.
- ❌ Do **not** edit `count_applicable` (`chip_test.py:1520`, `M` at `:1536-1538`). Two independent
  reasons: D-15 measured the ratio already drops, and editing it trips this guard.
- ❌ Do **not** put a hyphenated op literal (`sdp-lock`, `write-inhibited`, …) in `_ALWAYS_WRITES_NOTICE`.

### 3. Module constants, never DB fields, for anything that widens a blast radius
**Source:** `firestarter_app/firestarter/chip_test.py:988-999` (`_WRITE_REGION_START` /
`_WRITE_REGION_LENGTH` / `_UV_WRITE_REGION_LENGTH`), argument restated at `:692-698`.
**Apply to:** `_SDP_LEG_OPS`, the pattern-B generator, `_SDP_BASELINE_GATE_REASON`, and the D-12/D-13
recovery strings.
```python
# UV-EPROM write-region WIDTH (PATT-03, SC4). This is an ENGINE MODULE
# CONSTANT, never sourced from any DB field -- a malicious/misconfigured DB
# entry must not be able to widen the write window.
```

### 4. `StepResult.op` is the axis — no new `Step`/`StepResult` field
**Source:** `firestarter_app/firestarter/chip_test.py:290-293` and `:517-519` (the `write-partial`
precedent); reinforced at `:1169-1172` (keying on `_SDP_OPS` membership *rather than* a new `Step.group`
field, which 133 D-05 rejected on exactly this ground).
**Apply to:** D-07's two baseline ops. `StepResult` is at `:711-731` and gains **no** field; D-10's
field is a `DiagnosticReport` field.

### 5. Derive in the engine, assign in the handler
**Source:** `firestarter_app/firestarter/cli_handlers.py:2161-2175`.
**Apply to:** `sdp_hold_state`. Reinforced by three independent constraints: P-07 (`chip_test.py` is
scanned in full; `cli_handlers.py` helpers sit behind a fail-open allow-list), the inversion guard
(§2 above), and the mypy budget — `cli_handlers.py` is **STRICT** with **2 errors of headroom**, while
`chip_test.py` bodies are unchecked and cost nothing.

### 6. Non-vacuity: a pre-authored gate proves nothing until it is seen to fail
**Sources:** `tests/test_op_registration_parity.py:753-778`, `tests/test_sdp_table_parity.py:301-341`,
`tests/test_chip_test_sdp_leg.py:490` (`test_precedence_matrix_deriver_is_non_vacuous`).
**Shape:** positive control first (the real, unmodified input does **not** raise) → mutate an in-memory
or temp copy → `try/except AssertionError: pass / else: raise AssertionError("Non-vacuity failure: …")`.
Note `test_exemption_empty_reason_fails` (`:671-685`) opens with an explicit positive control and says
why: *"Without this, the legs below could pass by always failing regardless of input."*

### 7. SDP honesty wording is a call, not an authoring task
**Source:** `firestarter_app/firestarter/sdp_honesty.py:33-43` (`unreadable_state_caveat`), `:45+`
(`emission_summary`). Its module header (`:25-28`) states it deliberately imports **no `click`**
*"so a `click` dependency here would make this module unusable from Phase 134's report layer"* — it was
built as this phase's forward contract.
```python
def unreadable_state_caveat() -> str:
    return (
        "The resulting protection state cannot be read back on this chip "
        "family, so this is not a claim about the chip's actual state."
    )
```
**Apply to:** every report row and both D-12 recovery forms. Do not re-author these sentences.
`sdp_honesty.py` is in the **STRICT** island — call it, don't extend it.

### 8. Reason strings are user-facing prose naming a family fact, never a mechanism
**Source:** `firestarter_app/firestarter/chip_test.py:569-580` — the comment explicitly rejects the
generic flag-keyed wording because *"a community tester can act on"* the family fact, not the flag name.
**Apply to:** `_SDP_BASELINE_GATE_REASON`, the six NA reasons from `sdp_capability()`, and D-20's
*"no lock was emitted — baseline gate closed"*.

---

## No Analog Found

| File / concern | Role | Data Flow | Reason |
|----------------|------|-----------|--------|
| the **read-back-equality truth table** itself | engine / decision | transform | **No non-boolean step oracle exists in the tree.** Every shipped dispatch arm maps an operator bool to a verdict (`_dispatch_sdp:1473`, `_dispatch_step:1146-1149`); `_dispatch_multi_run` adds a disagreement policy over bools and attaches a `Fingerprint` only decoratively. The *control-flow skeleton* is `_dispatch_sdp`'s (see above); the **decision content** has no analog and must come from RESEARCH §2.2's gate order (length ⇒ BAD, before any `_diff_offsets` call) plus D-01…D-04. |
| the **D-17 synthetic nonzero-`chip-id` DB entry** | test fixture | transform | No existing fixture substitutes a DB entry field. All 43 ALLOW chips have `chip-id == 0`, so `derive_plan:487-490` emits an NA id step and `_id_step_closes_gate` never fires — R1/R2 are structurally unreachable in production. Nearest shape is `tests/test_dev_test_cmd.py`'s `_CHIP_WITH_ID = "AS29F002T"` (`:64`) + `check_eprom_id.return_value = (True, 0xDEAD)` (`:655`), which drives the *gate* but not a synthetic entry. |
| the **LEG-18 gh#20 triage record + backlog item** | doc | — | No code. Follows the phase-record conventions, not a code analog. |

---

## Metadata

**Analog search scope:** `firestarter_app/firestarter/` (all 7 modules named in CONTEXT.md's
`<canonical_refs>`), `firestarter_app/tests/` (86 `test_*.py` files enumerated; 8 read),
`firestarter_app/tests/fixtures/` (8 fixtures listed, 1 read), `firestarter_app/tools/` (24 entries
listed, 1 grepped).
**Files read for excerpts:** 10 (`chip_test.py`, `diagnostic_report.py`, `cli_handlers.py`,
`constants.py`, `sdp_honesty.py`, `test_op_registration_parity.py`, `test_chip_test_sdp_leg.py`,
`test_dev_test_cmd.py`, `test_sdp_table_parity.py`, `conftest.py`, plus
`fixtures/planted_permit_by_default.py`).
**Anchor drift found vs CONTEXT.md, re-confirming RESEARCH §1:** `diagnostic_report.to_dict` is at
**`:436`** (not `:444`); `COMMAND_SDP_UNLOCK`/`COMMAND_SDP_LOCK` at **`:77-78`** (not `:72-73`) and
their `COMMAND_NAMES` entries at **`:95-96`** (not `:90-91`); `_DECLARED_REGISTRY_COUNT` **does not
exist** (real names: `_POLICED_REGISTRY_COUNT = 6` at `:246`, `_DECLARED_NON_REGISTRY_COUNT = 6` at
`:328`); only **two** parity exemption rows are dischargeable (`:422-427`), not five. All
`chip_test.py` and `cli_handlers.py` anchors re-verified exact.
**Pattern extraction date:** 2026-08-04
