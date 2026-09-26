# Phase 133: SDP Leg Mechanism - Pattern Map

**Mapped:** 2026-08-04
**Files analyzed:** 5 (3 modified, 2 created)
**Analogs found:** 5 / 5 (all exact or in-file)
**Measured against:** `firestarter_app` @ `42a1971`, branch `gsd/v1.30-sdp-surface-retirement`
(meta repo on `gsd/v1.30-sdp-surface-retirement-behavioral-lock-proof` — divergence is deliberate)

> **Every line number below was independently re-measured this session, not inherited.** All of
> RESEARCH.md's 24 anchors still hold exactly at `42a1971`. **Re-verify at execute time anyway** —
> anchor on the **name**, never the number. This project's record is that these drift, and the
> `_run_step`/`run_plan` edits in this very phase will shift everything below `:863`.

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `firestarter/chip_test.py` (MOD) — `_SDP_OPS`, `OP_SDP_*`, `_dispatch_sdp` | service (engine dispatch) | request-response | **same file**: `_MULTI_RUN_OPS` `:654` + `_dispatch_multi_run` `:1039` | exact (in-file) |
| `firestarter/chip_test.py` (MOD) — 5th arm in `_dispatch_step` | service (dispatch router) | request-response | **same file**: `_dispatch_step` `:901-952`, arms `:924/:926/:931/:940`, terminal `return` `:944-952` | exact (in-file) |
| `firestarter/chip_test.py` (MOD) — cleanup registry `try/finally` in `run_plan` | service (plan orchestrator) | batch / transform | **same file**: `run_plan` `:709-794`; nearest existing `try/finally` idiom `_dispatch_multi_run:1104-1107` (tmp-file close) | role-match (in-file) |
| `firestarter/chip_test.py` (MOD) — widened `except` chain in `_run_step` | service (error mapper) | request-response | **same file**: `_run_step:883-898` existing 2-clause chain | exact (in-file) |
| `tools/check_devtest_orchestrator.py` (MOD) — `visit_ExceptHandler` + 4th bucket + exemption table | config / build-time gate | transform (AST walk) | **same file**: `visit_Dict` `:240-252`, `visit_Constant` `:254-259`, `main()` bucket wiring `:383-441` | exact (in-file) |
| `tests/test_check_devtest_orchestrator.py` (MOD) — ~4 subprocess legs | test | event-driven (subprocess) | **same file**: `_run_checker` `:70-80` + `test_checker_exits_nonzero_on_planted_vpp_set` `:174-194` | exact (in-file) |
| `tests/test_chip_test_sdp_leg.py` (NEW, D-15) | test | request-response | `tests/test_chip_test.py` `:793-900` (`_mock_operator`/`_plan_with_steps`/`_REAL_DB` + fault-injection test) | exact |
| `tests/test_op_registration_parity.py` (NEW, D-12) | test (parity gate) | transform (introspection) | `tests/test_sdp_table_parity.py` `:300-354`; naming precedent `tests/test_revision_constants_parity.py` | role-match (must drop `@requires_fw`) |

---

## Pattern Assignments

### `chip_test.py` — `_SDP_OPS` + `_dispatch_sdp` (service, request-response) — D-01/D-02/D-03

**Analog:** `firestarter/chip_test.py` itself — `_MULTI_RUN_OPS` (`:654`) and `_dispatch_multi_run`
(`:1039`). Clone **structurally**; do not import or reuse.

**Op-constant block pattern** (`:289-295`, measured verbatim — the seven shipped strings; the two new
constants append here):

```python
OP_ID = "id"
OP_READ = "read"
OP_BLANK_CHECK = "blank-check"
OP_WRITE = "write"
OP_WRITE_PARTIAL = "write-partial"
OP_VERIFY = "verify"
OP_ERASE = "erase"
```

**Frozenset-with-load-bearing-comment pattern** (`:626-654`, abridged — note the comment carries the
*safety argument*, not a description; both new-frozenset comments must do the same):

```python
# Ops that mutate the chip -- gated by the id-first destructive_gate (SWEEP-03)
# ... a write-shaped op absent from
# this frozenset would write to a misidentified chip ungated by the chip-ID
# mismatch check, which is a critical-severity correctness bug, not a
# cosmetic omission.
_DESTRUCTIVE_OPS = frozenset({OP_WRITE, OP_WRITE_PARTIAL, OP_ERASE})
...
_MULTI_RUN_OPS = frozenset({OP_WRITE, OP_WRITE_PARTIAL, OP_ERASE, OP_VERIFY})
```

**The guard to clone** (`:1082-1092`, verbatim) — returns a caller-visible `StepResult` refusal:

```python
    if op not in _MULTI_RUN_OPS:
        return StepResult(
            op=op,
            verdict=VERDICT_BAD,
            run_count=0,
            reason=(
                f"op {op!r} is not in the multi-run dispatch allow-list "
                "(_MULTI_RUN_OPS) — refused fail-closed rather than falling "
                "through to erase_eprom"
            ),
        )
```

**The per-op branch + terminal raise to clone** (`:1112-1132`, verbatim) — note the explicit
`else: raise`, deliberately **not** a bare `else`, and the comment explaining why:

```python
            if op in (OP_WRITE, OP_WRITE_PARTIAL):
                _sample(sampler, "before")
                outcomes.append(operator.write_eprom(name, eprom_data, tmp_source_path))
                _sample(sampler, "after")
            elif op == OP_VERIFY:
                outcomes.append(
                    operator.verify_eprom(name, eprom_data, tmp_source_path)
                )
            elif op == OP_ERASE:
                outcomes.append(operator.erase_eprom(name, eprom_data))
            else:
                # Unreachable in practice: the fail-closed `_MULTI_RUN_OPS`
                # guard at the top of this function already refused any op
                # outside {OP_WRITE, OP_WRITE_PARTIAL, OP_VERIFY, OP_ERASE}
                # before this loop could start (121-02, T-121-05; 121-06,
                # D-06). Kept explicit rather than a bare `else: # OP_ERASE`
                # -- the pre-fix shape that silently routed an unmapped op to
                # `erase_eprom()` (RESEARCH Pitfall 1a).
                raise AssertionError(
                    f"unreachable: op {op!r} passed the _MULTI_RUN_OPS guard"
                )
```

**Signature pattern** (`:1039-1048`, verbatim) — positional `op, name, eprom_data, operator` then
keyword-only extras. D-01's `_dispatch_sdp(op, name, eprom_data, operator)` matches the first four
exactly; this is the **forward contract** Phase 134 depends on:

```python
def _dispatch_multi_run(
    op: str,
    name: str,
    eprom_data: dict[str, Any],
    operator: Any,
    *,
    runs: int,
    sampler: Any = None,
    step: Step | None = None,
) -> StepResult:
```

**Operator-method call shape** (from `eprom_operations.py:1736` / `:1784` — **RING-FENCED, read-only,
never type-fix**): both are `(self, eprom_name: str, eprom_data_dict: dict, operation_flags: int = 0)
-> bool`. So `_dispatch_sdp`'s branches call `operator.sdp_lock(name, eprom_data)` /
`operator.sdp_unlock(name, eprom_data)` and get a `bool` — the same shape `operator.erase_eprom(name,
eprom_data)` returns at `:1121`. Verdict mapping follows `_dispatch_step`'s blank-check arm
(`:926-930`): `VERDICT_OK if is_ok else VERDICT_BAD`, `run_count=1`.

⚠ `tests/test_chip_test.py:793-801`'s `_OPERATOR_METHODS` list (the `Mock(spec=[...])` allow-list) does
**not** contain `sdp_lock`/`sdp_unlock`. The new test module needs its own list including them, or
`Mock(spec=...)` raises `AttributeError`.

---

### `chip_test.py` — the 5th `_dispatch_step` arm (service, request-response) — D-04

**Analog:** `_dispatch_step` itself, `:901-952`. **Measured arm order and the exact terminal return the
new arm goes immediately above** (`:924-952`, verbatim):

```python
    if step.op == OP_ID:
        return _dispatch_id(name, eprom_data, operator)
    if step.op == OP_BLANK_CHECK:
        is_ok = operator.check_eprom_blank(name, eprom_data)
        return StepResult(
            op=step.op, verdict=VERDICT_OK if is_ok else VERDICT_BAD, run_count=1
        )
    if step.op == OP_READ:
        return _dispatch_read(name, eprom_data, operator, runs=runs)
    # write / verify / erase: multi-run marginal policy (D-05/D-06). Dispatch
    # ONLY when `step.op` is on the live `_MULTI_RUN_OPS` allow-list --
    # anything else refuses fail-closed (121-02, T-121-07). ...
    if step.op in _MULTI_RUN_OPS:
        return _dispatch_multi_run(
            step.op, name, eprom_data, operator, runs=runs, sampler=sampler, step=step
        )
    return StepResult(                      # <-- NEW ARM GOES IMMEDIATELY ABOVE THIS
        op=step.op,
        verdict=VERDICT_BAD,
        run_count=0,
        reason=(
            f"op {step.op!r} matched no dispatch arm — refused fail-closed "
            "rather than falling through to _dispatch_multi_run"
        ),
    )
```

Arm order measured = `OP_ID` (`:924`) → `OP_BLANK_CHECK` (`:926`) → `OP_READ` (`:931`) →
`_MULTI_RUN_OPS` (`:940`) → terminal (`:944`). **Confirms D-04's premise:** all 7 shipped ops return
from arms 1–4 and never evaluate an arm-5 membership test. That is what D-13b's sentinel proves.

---

### `chip_test.py` — cleanup registry `try/finally` in `run_plan` (service, batch) — D-06/D-07/D-10

**Analog:** `run_plan` itself. **Measured current flat loop, verbatim `:763-794`** — the exact code the
`try/finally` wraps:

```python
    if runs < 2:
        return [
            StepResult(
                op="__plan__",
                verdict=VERDICT_BAD,
                reason=(
                    f"runs must be >= 2 (got {runs}); a destructive/verify "
                    "step requires at least 2 runs to compare (D-05)"
                ),
                run_count=0,
            )
        ]

    results: list[StepResult] = []
    destructive_gate_closed = False

    for step in plan.steps:
        if not step.supported:
            results.append(_skip_result(step.op, step.reason, verdict=VERDICT_NA))
            continue

        if step.op in _DESTRUCTIVE_OPS and destructive_gate_closed:
            results.append(_skip_result(step.op, _DESTRUCTIVE_GATE_REASON))
            continue

        result = _run_step(plan.name, step, operator, db, runs=runs, sampler=sampler)
        results.append(result)

        if step.op == OP_ID:
            destructive_gate_closed = _id_step_closes_gate(result)

    return results
```

Boundaries the planner must honor, all measured:
- The `runs < 2` early return (`:763-774`) stays **outside** the `try` — nothing is registered yet.
- `results` (`:776`) and `destructive_gate_closed` (`:777`) are created **before** the `try`.
- The destructive gate is the single `if step.op in _DESTRUCTIVE_OPS and destructive_gate_closed:` at
  `:784`. LEG-09 = `OP_SDP_UNLOCK` deliberately absent from `_DESTRUCTIVE_OPS` (`:636`), so it can never
  be gated. Per D-11 this is **forward-protection for Phase 134**, not a live 133 path.
- `return results` at `:794` stays unchanged, **inside** the `try`.

**⚠ Pitfall 2 is load-bearing and re-confirmed by measurement.** `results` is returned by reference; a
`results.append(...)` in the `finally` **is** visible to the caller. The consumer chain is real:
`cli_handlers.py:2161` `results = run_plan(plan, app.eprom_operator, app.db, sampler=sampler)` and
`:2166` `report.banner = count_applicable(plan, results)`, plus `report.results` `:2165`,
`build_db_diff` `:2178`, the markdown table `:2200`, `dedup_fingerprint`, and
`sys.exit(max(...))` `:2217-2219` — seven surfaces. **The drain must not append into `results`.**
Observe the drain through the operator double instead (see the test pattern below).

**Nearest in-file `try/finally` precedent** (`:1101-1108`, verbatim) — proves the module already uses a
bare `finally` with **no `except` clause**, which is exactly the shape criteria 1+2 require:

```python
        tmp_fh = tempfile.NamedTemporaryFile(
            prefix="chip_test_pattern_", suffix=".bin", delete=False
        )
        try:
            tmp_fh.write(expected)
        finally:
            tmp_fh.close()
```

**Best-effort-swallow precedent for the per-callable wrapper (D-10)** — `_sample` `:1026-1036`, and note
its docstring at `:750-761` is the "proven no-op" wording the new `cleanup=[]` empty-registry claim
should mirror.

---

### `chip_test.py` — widened `except` chain in `_run_step` (service, error mapper) — D-08

**Analog:** `_run_step` itself. **Measured verbatim `:876-898`** — the resolve call sits **outside** the
`try` (RESEARCH Pitfall 3; recommendation is to leave the `try` where it is and fix the over-claiming
docstring at `:868-869`):

```python
    eprom_data, skip_stub, reason = _resolve_or_none(name, db)
    if skip_stub is not None or eprom_data is None:
        if skip_stub is None:
            skip_stub = _skip_result(step.op, reason)
        skip_stub.op = step.op
        return skip_stub

    try:
        return _dispatch_step(
            name, step, eprom_data, operator, runs=runs, sampler=sampler
        )
    except EpromOperationError as exc:
        return StepResult(
            op=step.op,
            verdict=VERDICT_BAD,
            reason=str(exc),
            error_code=exc.error_code,
            run_count=1,
        )
    except (ChipNotImplementedError, ChipNotFoundError) as exc:
        # Belt-and-suspenders: a resolve-time-only exception raised instead
        # during dispatch (defensive; resolve_chip already ran above).
        return _skip_result(step.op, str(exc) or exc.__class__.__name__)
```

**The `StepResult(verdict=VERDICT_BAD, ...)` shape to copy for the two new clauses** is the
`except EpromOperationError` body above, minus `error_code` (neither `SerialError` nor
`HardwareOperationError` carries `.error_code` — only `EpromOperationError` does, per
`StepResult`'s docstring `:665-667`).

**Measured hierarchy** (`exceptions.py`, re-verified this session — D-08's whole basis):

```
SerialError(Exception)          :13
├── SerialTimeoutError          :19
├── ProgrammerNotFoundError     :25
└── FirmwareOutdatedError       :31
EpromOperationError(Exception)  :37   [carries .error_code]
├── ProtocolNotImplementedError :45
└── ChipNotImplementedError     :51
HardwareOperationError(Exception) :69  ← SIBLING of Exception, NOT an EpromOperationError
FirmwareOperationError(Exception) :75
ChipNotFoundError(Exception)      :81
```

`SerialError` has exactly three subclasses; no other class in the repo derives from it. **Clause order
is load-bearing:** `except (ProgrammerNotFoundError, FirmwareOutdatedError): raise` must come **first**,
then `except (SerialError, HardwareOperationError)`, and neither may be placed in a way that changes
which handler wins for `EpromOperationError`/`ChipNotImplementedError`. Pin today's precedence with a
test **before** editing (RESEARCH Pitfall 4).

---

### `tools/check_devtest_orchestrator.py` — `visit_ExceptHandler` + 4th bucket (config gate, transform) — D-09/D-14

**Analog:** the same file's existing visitor methods.

**Visitor-method shape to match** (`:240-259`, verbatim — note: append an f-string to a named `*_violations`
list, always end with `self.generic_visit(node)`):

```python
    def visit_Dict(self, node: ast.Dict) -> None:
        keys: list[str] = []
        for k in node.keys:
            if isinstance(k, ast.Constant) and isinstance(k.value, str):
                keys.append(k.value)
        hit_count = len(_WIRE_DICT_KEYS.intersection(keys))
        if hit_count >= _WIRE_DICT_KEY_THRESHOLD:
            matched = sorted(_WIRE_DICT_KEYS.intersection(keys))
            self.raw_wire_dict_violations.append(
                f"{self.filename}:{node.lineno}: raw wire-dict literal "
                f"(keys matched: {matched})"
            )
        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> None:
        if isinstance(node.value, str) and node.value == _FORCE_CLI_FLAG:
            self.force_violations.append(
                f'{self.filename}:{node.lineno}: literal "--force" string'
            )
        self.generic_visit(node)
```

**Bucket declaration** (`:211-215`, verbatim) — the 4th `broad_except_violations: list[str] = []` joins
here, and the class docstring at `:197-209` (which enumerates "three violation buckets") must be
updated to four:

```python
    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.vpp_set_violations: list[str] = []
        self.raw_wire_dict_violations: list[str] = []
        self.force_violations: list[str] = []
```

**Env-override seam idiom** (`:80-86`, verbatim) — read at **module import**, which is why every test
must shell out:

```python
_HERE = os.path.dirname(__file__)
_DEFAULT_CHIP_TEST = os.path.join(_HERE, "..", "firestarter", "chip_test.py")

# Env-override seam (mirrors check_dispatch.py's FIRESTARTER_DB_FILE): lets
# the paired pytest point this checker at a deliberately-violating fixture
# file without editing the real, clean chip_test.py source (D-03).
FIRESTARTER_DEVTEST_SRC = os.environ.get("FIRESTARTER_DEVTEST_SRC", _DEFAULT_CHIP_TEST)
```

**Bucket wiring in `main()`** (`:383-393` + `:419-436`, verbatim) — three extend-sites per scan leg
(the new bucket adds a fourth to each of the three legs), then one `_print_bucket` arm:

```python
    vpp_set_violations: list[str] = []
    raw_wire_dict_violations: list[str] = []
    force_violations: list[str] = []
    scanned: list[str] = []

    full_scan_visitor = _scan_file(FIRESTARTER_DEVTEST_SRC)
    if full_scan_visitor is not None:
        scanned.append(FIRESTARTER_DEVTEST_SRC)
        vpp_set_violations.extend(full_scan_visitor.vpp_set_violations)
        raw_wire_dict_violations.extend(full_scan_visitor.raw_wire_dict_violations)
        force_violations.extend(full_scan_visitor.force_violations)
    ...
    if (
        host_only_errors
        or vpp_set_violations
        or raw_wire_dict_violations
        or force_violations
    ):
        if host_only_errors:
            _print_bucket("host-only framing violation(s)", host_only_errors)
        ...
        if force_violations:
            _print_bucket("force=True / --force pass-through site(s)", force_violations)
        sys.exit(1)
```

**Fail-closed-on-empty-scan** (`:411-417`, verbatim — measured exactly where CONTEXT.md said; the new
bucket inherits it unchanged, but the planner must confirm no new early-exit path bypasses it):

```python
    if not scanned:
        print(
            "FAIL: no orchestrator source files found to scan "
            f"(checked: {targets}) -- the gate cannot vacuously pass with "
            "nothing scanned"
        )
        sys.exit(1)
```

**PASS line** (`:438-441`, verbatim — extend with a 4th counter; measured safe, existing tests only
assert `"PASS:" in result.stdout`):

```python
    print(
        f"PASS: scanned {', '.join(os.path.relpath(s, _HERE) for s in scanned)}; "
        "0 VPP-set, 0 raw-wire-dict, 0 --force; firmware untouched (host-only, asserted)"
    )
```

**D-14's exemption target — copy this verbatim into the plan so the gate is written to tolerate it**
(`chip_test.py:1026-1036`, measured verbatim; the `# noqa: BLE001` is **inert** — ruff `select` is
`["E","F","I","UP"]`):

```python
def _sample(sampler: Any, phase: str) -> None:
    """Best-effort sampler invocation (D-04) -- never lets an exception
    escape (Pitfall 1 extended to the sampler: it is a diagnostic hook, not
    part of the write contract). No-op when `sampler is None`.
    """
    if sampler is None:
        return
    try:
        sampler(phase)
    except Exception:  # noqa: BLE001 -- best-effort diagnostic, swallow all
        pass
```

Measured: this is the **only** broad handler in any of the three scan targets. The other
`chip_test.py` handlers are `(ChipNotImplementedError, ChipNotFoundError)` `:703`/`:895`,
`EpromOperationError` `:887`/`:1150`, `OSError` `:997`/`:1148`/`:1165`.

**Exemption-table + mandatory-reason + stale-row idiom to reuse for D-14 (and D-12):**
`_HANDLER_FUNCTION_NAMES` (`:138-150`) is the house frozenset-with-rationale shape, and its
fail-closed pairing is `test_handler_function_names_all_resolve_to_real_callables` — the exact
stale-row inversion D-14 guard (b) needs. `_EXEMPT_FW_TO_HOST` in
`tests/test_revision_constants_parity.py` is the second precedent: a *"frozen, deliberately-NOT-auto-derived
… name-PAIR map (never a skip-set)"*.

---

### `tests/test_check_devtest_orchestrator.py` — ~4 new subprocess legs (test, event-driven)

**Analog:** the same file. **`_run_checker` helper, verbatim `:70-80`** — reuse it, do not re-implement:

```python
_FA_DIR = Path(__file__).parent.parent


def _run_checker(
    env_overrides: dict[str, str] | None = None,
) -> subprocess.CompletedProcess:
    env = {**os.environ, **(env_overrides or {})}
    return subprocess.run(
        [sys.executable, "tools/check_devtest_orchestrator.py"],
        cwd=str(_FA_DIR),
        capture_output=True,
        text=True,
        env=env,
    )
```

**Planted-violation leg to clone, verbatim `:174-194`** — write to `tmp_path`, point the env seam at
it, assert non-zero **and** the bucket label appears in stdout:

```python
def test_checker_exits_nonzero_on_planted_vpp_set(tmp_path: Path) -> None:
    """A real subprocess-level VPP-set call site MUST fail the gate.

    This is the anti-hollow proof (D-03): the fixture is written to disk and
    the checker is pointed at it via the FIRESTARTER_DEVTEST_SRC env-override
    (mirrors check_dispatch.py's FIRESTARTER_DB_FILE seam) -- a real
    subprocess-level violation, not an in-process synthetic.
    """
    bad = tmp_path / "planted_vpp_set.py"
    bad.write_text(
        "def orchestrate(op):\n"
        "    op.set_vpp(12000)\n"
        "    return op.write_eprom('chip', {}, 'path')\n"
    )
    result = _run_checker({"FIRESTARTER_DEVTEST_SRC": str(bad)})
    assert result.returncode != 0, (
        f"checker exited 0 on a planted VPP-set violation.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "FAIL:" in result.stdout
    assert "VPP-set" in result.stdout
```

**Clean-source baseline that must stay green** (`:154-166`, verbatim) — this is the leg D-14's exemption
exists to keep passing:

```python
def test_checker_exits_zero_on_clean_source() -> None:
    result = _run_checker()
    assert result.returncode == 0, (
        f"checker exited {result.returncode} on clean source.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS:" in result.stdout, (
        f"Expected 'PASS:' in output but got:\n{result.stdout}"
    )
```

**Also copy:** the module docstring's numbered `Coverage:` list (`:13-54`) — the house convention is to
append a numbered entry per new leg. And the `_referenced_underscore_helpers_in_dev_test` helper
(`:95-146`) is the precedent for a **source-string-taking** derivation shared by a real leg and a
non-vacuity leg — *"taking `source: str` rather than a path is what lets a single helper serve both, so
the non-vacuity leg exercises the exact code the real leg does, not a re-implementation of the walk."*
D-14's stale-row leg should follow that shape.

---

### `tests/test_chip_test_sdp_leg.py` (NEW, test, request-response) — D-15

**Analog:** `tests/test_chip_test.py`. **No new fixture factory** — copy these three helpers.

**`_REAL_DB` + operator-double idiom, verbatim `:287` and `:788-818`:**

```python
_REAL_DB = EpromDatabase(skip_local_override=True)

# Bench-free: a Mock(spec=[...]) stand-in for EpromOperator drives each step's
# outcome; resolve_chip runs for real against EpromDatabase(skip_local_override
# =True) (no ~/.firestarter, no serial). M8720 is real+supported (protocol
# 0x08, EEPROM) so resolve_chip succeeds for every step by default.

_OPERATOR_METHODS = [
    "check_eprom_id",
    "read_eprom",
    "check_eprom_blank",
    "write_eprom",
    "verify_eprom",
    "erase_eprom",
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
```

⚠ **The new module's `_OPERATOR_METHODS` must add `"sdp_lock"` and `"sdp_unlock"`** or
`Mock(spec=...)` raises `AttributeError` on the new dispatch arm. **`"M8720"` is the house chip**
(protocol 0x08, EEPROM, resolves for every step) — reuse it, do not pick a new one.

**Planted-fault + non-fatal-continuation leg to clone, verbatim `:827-845`** — this is precisely the
LEG-11 shape (swap `EpromOperationError` for `SerialTimeoutError` / `HardwareOperationError`), and its
`_result(results, op)` lookup helper at `:820-824` is how every assertion locates its step:

```python
def _result(results, op):
    for r in results:
        if r.op == op:
            return r
    raise AssertionError(f"no result for op {op!r} in {[r.op for r in results]}")


def test_run_plan_non_fatal_raising_step_does_not_abort_later_steps():
    operator = _mock_operator()
    operator.read_eprom.side_effect = EpromOperationError(
        "boot block locked", error_code=0xA4
    )
    plan = _plan_with_steps(
        Step(op=OP_READ, supported=True, reason=""),
        Step(op=OP_WRITE, supported=True, reason="", destructive=True),
    )
    results = run_plan(plan, operator, _REAL_DB)

    read_result = _result(results, OP_READ)
    write_result = _result(results, OP_WRITE)
    assert read_result.verdict == VERDICT_BAD
    assert read_result.error_code == 0xA4
    # The later step still ran -- one step's exception never aborts the rest.
    assert write_result.verdict == VERDICT_OK
    operator.write_eprom.assert_called()
```

**Module-attribute monkeypatch idiom for D-13b's sentinel, verbatim `:869-874`:**

```python
def test_run_plan_resolver_refusal_maps_to_skipped(monkeypatch):
    import firestarter.chip_test as chip_test_mod

    spy = Mock(side_effect=ChipNotImplementedError("adapter-required"))
    monkeypatch.setattr(chip_test_mod, "resolve_chip", spy)
```

D-13b becomes `monkeypatch.setattr(chip_test_mod, "_dispatch_sdp", Mock(side_effect=AssertionError(...)))`
then drives all 7 shipped op strings. In-process is sufficient here — `chip_test.py` reads no env var at
import (RESEARCH Pitfall 5).

**How the drain is observed without touching `results`** (Pitfall 2): assert on the double —
`operator.sdp_unlock.assert_called_once_with("M8720", ANY)` / `assert_not_called()`. That is the
`operator.check_eprom_blank.assert_not_called()` idiom already used at `:858`.

`make_app_context` / the `app_context` fixture (`conftest.py:229-237`, `:325`) are available if a
handler-level test is wanted, but every LEG-09/10/11 + D-13 proof runs through `run_plan(plan,
operator, _REAL_DB)` directly and needs no fixture.

---

### `tests/test_op_registration_parity.py` (NEW, test/parity gate, transform) — D-12

**Analog:** `tests/test_sdp_table_parity.py`. **Naming precedent:** `test_revision_constants_parity.py`.

**Non-vacuity leg — the template, verbatim `:300-341`:**

```python
@requires_fw
def test_altered_temp_copy_fails_parity_non_vacuous(tmp_path: Path) -> None:
    """An altered temp copy of eeprom_28c.cpp (one pair's byte flipped) MUST
    make the parity assertion fail -- proves the gate is capable of failing,
    not a vacuous always-pass check.
    ...
    """
    original = _EEPROM_28C_CPP.read_text(encoding="utf-8")
    altered = original.replace("{0x5555, 0x20}", "{0x5555, 0x21}", 1)
    assert altered != original, (
        "Fixture setup error: the byte replacement did not apply -- "
        "eeprom_28c.cpp's EEPROM_SDP_DISABLE terminal pair text changed "
        "shape and this fixture needs updating."
    )
    fixture_path = tmp_path / "eeprom_28c_altered.cpp"
    fixture_path.write_text(altered, encoding="utf-8")

    with _env_override("FIRESTARTER_SDP_SRC", str(fixture_path)):
        sdp_pairs = _extract_byte_flip_pairs(
            _sdp_src_path().read_text(encoding="utf-8"), "EEPROM_SDP_DISABLE"
        )
    flash_pairs = _extract_byte_flip_pairs(
        _FLASH_UTILS_H.read_text(encoding="utf-8"),
        "FLASH_DISABLE_WRITE_PROTECTION",
    )

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

Three transferable properties: (1) the **fixture-setup assertion** (`altered != original`) so a stale
replacement string cannot make the leg vacuous; (2) the `try/except AssertionError: pass / else: raise`
inversion; (3) a named `_*_CONTEXT` constant (`:65-71`) carrying *why the parity matters* into the
failure message.

⚠ **Do NOT copy `@requires_fw`.** The new module is host-and-engine-local (every real op-keyed registry
lives in `chip_test.py`), so it must run in CI — unlike its template, which skips when the firmware
sibling is absent. Do not import `tests.fw_presence`, do not read any firmware path.

**Fails-closed seam leg, verbatim `:349-354`:**

```python
def test_missing_override_path_fails_closed() -> None:
    """Pointing FIRESTARTER_SDP_SRC at a nonexistent path MUST raise, never
    silently fall back to the real source or pass."""
    with _env_override("FIRESTARTER_SDP_SRC", "/nonexistent/path/does-not-exist.cpp"):
        with pytest.raises(FileNotFoundError):
            _sdp_src_path()
```

**Docstring convention** (`:1-46`): a numbered `Coverage:` list, then an explicit paragraph on *why the
extraction is not a bare regex*, then an explicit paragraph on the skip marker's scope. D-12's module
needs the equivalent three: the four guards enumerated, why introspection over grep-only, and an
explicit statement that this module carries **no** skip marker.

**Registries this test polices — re-measured this session, confirming RESEARCH's census:**

| Registry | Measured location | Real op-keyed? |
|---|---|---|
| `_DESTRUCTIVE_OPS` | `chip_test.py:636` | ✅ frozenset of op strings |
| `_MULTI_RUN_OPS` | `chip_test.py:654` | ✅ frozenset of op strings |
| `_dispatch_step` arms | `chip_test.py:924-952` | ✅ explicit comparisons + terminal refusal |
| `derive_plan`'s `Step(op=…)` | `chip_test.py:394`, sites `:473-572` | ✅ (exempt in 133 per D-11) |
| `_dispatch_multi_run` inner branches | `chip_test.py:1112-1132` | ✅ (not in P-23's table; recommended 6th) |
| `_SDP_OPS` | NEW this phase | ✅ |
| `_RAN_VERDICTS` / `count_applicable` | `:1209` / `:1229` | ⚠ verdict-keyed, not op-keyed |
| `dedup_fingerprint`, `diagnostic_report.py` renderer, `parse_devtest_issue.py`, `_ALWAYS_WRITES_NOTICE`, `_HANDLER_FUNCTION_NAMES` | — | ⚠ no op vocabulary at all |

Measured independently: the only op-keyed *line of code* outside `chip_test.py` is
`cli_handlers.py:1942` (`if r.op == OP_ID …`), which is `OP_ID`-specific and cannot be joined. So the
two exemption **reason kinds** RESEARCH identified are correct, and the inversion guard (a declared
non-registry must still contain zero op-string references) is the genuinely valuable leg.

---

## Shared Patterns

### Fail-closed refusal, never a bare `else`
**Source:** `chip_test.py:1082-1092` (guard returns a `StepResult`), `:1130-1132` (terminal `raise
AssertionError`), `:944-952` (`_dispatch_step`'s terminal `return`).
**Apply to:** `_dispatch_sdp`, the 5th `_dispatch_step` arm.
**Why:** the pre-Phase-121 shape routed any unmapped op to `operator.erase_eprom()` and reported OK.
Every new arm inherits the refusal. `AssertionError` is not a `SerialError`, `HardwareOperationError`,
or `EpromOperationError` — so D-08's new clauses do not catch it, and that must be **asserted**.

### Module constants, never DB fields, for anything that widens blast radius
**Source:** `chip_test.py:816-829` (`_WRITE_REGION_LENGTH` / `_UV_WRITE_REGION_LENGTH`, SC4) —
*"an ENGINE MODULE CONSTANT, never sourced from any DB field."*
**Apply to:** `_SDP_OPS`, `OP_SDP_LOCK`, `OP_SDP_UNLOCK`, both exemption tables.

### Comments that carry the safety argument, not a description
**Source:** `chip_test.py:626-654` (both frozensets), `:1069-1080` (`_dispatch_multi_run`'s fail-closed
paragraph), `:844-856` (`_write_region_for`'s deleted-guess paragraph),
`check_devtest_orchestrator.py:117-137` (`_HANDLER_FUNCTION_NAMES`).
**Apply to:** every new constant, frozenset, exemption row, and the new visitor bucket. The house style
records *what breaks if this is wrong*, with the phase/decision ID. Every exemption reason string must
meet this bar — an exemption whose reason is a restatement is what turns a fail-closed gate fail-open.

### Anti-hollow: a gate is proven by a real subprocess and a planted RED
**Source:** `tests/test_check_devtest_orchestrator.py:70-80` (`_run_checker`), `:174-194` (planted),
`:154-166` (clean baseline).
**Apply to:** all ~4 new broad-except legs. Env seams bind at module import, so `monkeypatch.setenv`
is defeated — subprocess only.

### Non-vacuity: alter a copy, prove the gate fails
**Source:** `tests/test_sdp_table_parity.py:300-341`.
**Apply to:** `test_op_registration_parity.py`, and D-14's stale-row leg.

### Bench-free engine testing: `Mock(spec=[...])` operator + real `_REAL_DB` + `"M8720"`
**Source:** `tests/test_chip_test.py:287`, `:788-818`, `:820-824`.
**Apply to:** every test in `test_chip_test_sdp_leg.py`. No new fixture factory; `make_app_context` /
`app_context` (`conftest.py:229-237`, `:325`) only if a handler-level test is wanted.

---

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| — | — | — | None. Every file in this phase has an in-file or house analog. |

Two *sub-patterns* have no direct precedent and need construction (both grounded in existing idioms, so
neither is a new concept):

| Sub-pattern | Nearest idiom | Gap |
|---|---|---|
| Cleanup-callable registry drained in a `finally` in `run_plan` | `_dispatch_multi_run:1104-1107`'s bare `try/finally`; `_sample:1033-1036`'s best-effort swallow | No list-of-callables registry exists anywhere in `chip_test.py`. Use a plain `list` + per-item narrow `try/except` — **not** `contextlib.ExitStack` (drains LIFO and re-raises out of the `finally`, masking the in-flight exception, which is what D-10 exists to prevent). |
| A `(file, function) → reason` exemption table inside an AST visitor | `_HANDLER_FUNCTION_NAMES:138-150` (frozenset + fail-closed pairing test); `test_revision_constants_parity.py`'s `_EXEMPT_FW_TO_HOST` name-PAIR map | The visitor has no enclosing-function context today. D-14 needs a `visit_FunctionDef` push/pop (~8 lines). Share one idiom with D-12's table so the phase adds **one** concept, not two. |

---

## Anchor Re-Verification Log

Re-measured this session at `42a1971`. **24/24 hold.** Notable:

| Symbol | RESEARCH said | **My measurement** |
|---|---|---|
| Op constants (7) | `:289-295` | ✅ `:289-295` |
| `_DESTRUCTIVE_OPS` / `_MULTI_RUN_OPS` / `_DESTRUCTIVE_GATE_REASON` | `:636` / `:654` / `:656` | ✅ all exact |
| `StepResult` / `_skip_result` / `_resolve_or_none` | `:661` / `:685` / `:689` | ✅ all exact |
| `run_plan` (guard `:763`, `results` `:776`, loop `:779`, gate `:784`, `return` `:794`) | `:709-794` | ✅ all exact |
| `_run_step` (`try` `:883`, `except EpromOperationError` `:887`, `:895`) | `:863-898` | ✅ all exact |
| `_dispatch_step` arms `:924/:926/:931/:940`, terminal `:944-952` | `:901-952` | ✅ all exact |
| `_sample` / its `except Exception:` | `:1026` / `:1035` | ✅ exact |
| `_dispatch_multi_run` guard `:1082-1092`, `AssertionError` `:1130-1132` | `:1039` | ✅ exact |
| `_RAN_VERDICTS` / `count_applicable` | `:1209` / `:1229` | ✅ exact |
| `exceptions.py` full hierarchy | `:13/19/25/31/37/45/51/69/75/81` | ✅ all exact |
| `check_devtest_orchestrator.py` seam `:86`, `_HANDLER_FUNCTION_NAMES` `:138-150`, visitor `:196`, `visit_Call` `:224`, `visit_Dict` `:240`, `visit_Constant` `:254`, `_scan_file` `:262`, `_scan_target_functions` `:281`, `_assert_host_only` `:321`, `_print_bucket` `:344`, `main` `:352`, empty-scan `:411-417`, PASS `:438-441` | as stated | ✅ all exact |
| `test_check_devtest_orchestrator.py` `_run_checker` `:70-80`, planted-VPP `:174-194` | `:72` | ✅ (helper `def` at `:70`) |
| `test_sdp_table_parity.py` non-vacuity `:301`, fails-closed `:349` | same | ✅ (decorator at `:300`) |
| `conftest.py` `make_app_context` `:229-237`, `app_context` `:324-325` | `:229` / `:325` | ✅ (`@pytest.fixture` at `:324`) |
| `eprom_operations.py` `sdp_unlock` `:1736`, `sdp_lock` `:1784` | same | ✅ — RING-FENCED, signature read only |
| `cli_handlers.py` `run_plan` call `:2164`, `count_applicable` `:2166` | same | ✅ exact |
| `test_chip_test.py` `run_plan(` call sites | RESEARCH said 20 (CONTEXT said 10) | **39** measured (`grep -c`). Blast radius is larger still — strengthens D-07's refusal to change the signature. |

Line counts: `chip_test.py` 1253 · `check_devtest_orchestrator.py` 445 ·
`test_check_devtest_orchestrator.py` 667 · `test_sdp_table_parity.py` 354 · `conftest.py` 334 ·
`test_chip_test.py` 1958 · `test_revision_constants_parity.py` 866.

**Marked re-verify-at-execute:** every number above. This phase edits `_run_step` and `run_plan`, which
shifts every anchor below `:863` in `chip_test.py`.

---

## Metadata

**Analog search scope:** `firestarter_app/firestarter/`, `firestarter_app/tools/`,
`firestarter_app/tests/` (read-only). Firmware repo `firestarter/` not touched, not read.
**Files read:** 8 (`chip_test.py`, `exceptions.py` [class list], `cli_handlers.py` [2 lines],
`eprom_operations.py` [2 signatures, ring-fenced], `tools/check_devtest_orchestrator.py`,
`tests/test_check_devtest_orchestrator.py`, `tests/test_sdp_table_parity.py`, `tests/conftest.py`,
`tests/test_chip_test.py`, `tests/test_revision_constants_parity.py` [header]).
**Not cited, deliberately:** `.planning/codebase/TESTING.md` (measured severely stale — claims "no
Python unit tests" against 88 test files / 1297 tests, and points at a foreign `/home/henrik/...` path).
**Pattern extraction date:** 2026-08-04
