# Phase 175: Structural Sentinel over `derive_plan` - Pattern Map

**Mapped:** 2026-09-04
**Files analyzed:** 5 new files (0 modified — this phase is TEST-ONLY, zero production diff)
**Analogs found:** 5 / 5 (all exact or role-match)
**Repo:** all analogs are git-TRACKED in the `firestarter_app` submodule (verified with `git ls-files`); none is a gitignored mirror.

All paths below are relative to `/workspaces/firestarter_app/` unless absolute.

---

## File Classification

| New file | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `tests/plan_corpus.py` | test helper module (shared fixture surface) | batch / transform (DB → 1,354 `Plan`s) | `tests/test_chip_test_sdp_leg.py:215-260` (`_REAL_DB`, `_OPERATOR_METHODS`, `_mock_operator`, `_plan_with_steps`) + `tests/fw_presence.py` (non-`test_`-prefixed shared-helper placement) | role-match |
| `tests/test_derive_plan_structural_sentinel.py` | test (closure + relational predicate + UV pins + anti-vacuity) | batch / transform | `tests/test_op_registration_parity.py` (fail-closed partition w/ reasons) + `tests/test_erase_flag_invariants.py` (whole-DB sweep) | exact (two analogs, one per axis) |
| `tests/test_derive_plan_no_drop_sweep.py` | test (execution sweep, ~37 s) | request-response through a mocked operator | `tests/test_chip_test_sdp_leg.py:827` (`run_plan` + `_mock_operator` + `len(results)==len(steps)`) | exact |
| `tests/fixtures/plan_shapes.json` | committed data artifact | file-I/O (frozen pin) | `tests/fixtures/part_number_delta.json` | exact |
| `tools/measure_plan_shapes.py` | generator script | file-I/O / CLI | `tools/measure_part_number_delta.py` | exact |
| `tests/test_plan_shapes_drift.py` | test (drift gate) | file-I/O + subprocess | `tests/test_part_number_delta_drift.py` | exact |

**Tooling scope per file** (Pitfall 8 — mypy watermark is 35/35, zero headroom):

| File | in `ruff check firestarter/ tests/`? | in mypy scope? | Consequence |
|---|---|---|---|
| `tests/plan_corpus.py` | **YES** | **YES** | Annotated helpers' bodies ARE checked (`check_untyped_defs=false` only spares *unannotated* defs). Keep annotated helpers trivial; run `tools/check_mypy_watermark.py` before commit. |
| `tests/test_derive_plan_structural_sentinel.py` | **YES** | **YES** | Same. Unannotated `def test_x():` bodies are unchecked; an `-> None` annotation opts the body in. |
| `tests/test_derive_plan_no_drop_sweep.py` | **YES** | **YES** | Same. |
| `tests/test_plan_shapes_drift.py` | **YES** | **YES** | The analog's test defs are unannotated — copying that keeps the watermark still. |
| `tests/fixtures/plan_shapes.json` | n/a | n/a | `tests/fixtures/` is excluded from **both** (`pyproject.toml:121` ruff `extend-exclude`, `:174` mypy `exclude`). Data only — never put a helper here. |
| `tools/measure_plan_shapes.py` | **NO** (CI lints `firestarter/ tests/` only) | **NO** | Unchecked, like its analog. Do not budget plan time on strictness there. |

---

## Pattern Assignments

### `tests/test_derive_plan_structural_sentinel.py` — axis 1: total fail-closed partition (D-01/D-06)

**Analog:** `tests/test_op_registration_parity.py` (a shipped `(op, registry) → member-or-reasoned-exemption` gate over the same 13-op vocabulary), with the discovery idiom from `tests/test_chip_test_sdp_leg.py:840-846`.

**Vocabulary discovery** (`test_op_registration_parity.py:130-140` — copy the comprehension, NOT the comment above it):
```python
_ALL_OPS: frozenset[str] = frozenset(
    value
    for name, value in vars(chip_test_mod).items()
    if name.startswith("OP_") and isinstance(value, str)
)
```

**Import-time count pin** (`:186-190`) — the shape to mirror for the new module's own census:
```python
assert len(_ALL_OPS) == 13, (
    f"measured {len(_ALL_OPS)} OP_* string constants in chip_test.py, "
    "expected 13 -- the census baked into this module's docstring and "
    "_POLICED_REGISTRIES/_OP_REGISTRY_EXEMPTIONS needs re-measuring"
)
```
Note for the planner: this line already makes a 14th `OP_*` fail **collection** of that module. The new closure's added value is the *verify-disposition reason*, not the detection. Say so in the new module's docstring (RESEARCH §A) so nobody deletes it as a duplicate.

**Reason table shape** (`:456`, `dict[tuple[str, str], str]` there; the new one is `dict[str, str]` keyed by op):
```python
_OP_REGISTRY_EXEMPTIONS: dict[tuple[str, str], str] = {
    ("id", "_DESTRUCTIVE_OPS"): _NOT_DESTRUCTIVE_REASON.format(op="id"),
    ("verify", "_DESTRUCTIVE_OPS"): (
        "verify reads back and compares without itself mutating the chip "
        "(the write it validates is separately gated); it was never a "
        "candidate for _DESTRUCTIVE_OPS membership."
    ),
    ...
}
```
Reasons are prose *values*, not comments — this is the house mechanism and it satisfies the no-comments rule.

**Empty-reason guard** (`:821-836`) — note the **positive control first**, which is the anti-vacuity discipline in miniature:
```python
def test_exemption_empty_reason_fails() -> None:
    _assert_op_parity(
        _POLICED_REGISTRIES, _OP_REGISTRY_EXEMPTIONS, _ALL_OPS, _PARITY_CONTEXT
    )
    sample_key = next(iter(_OP_REGISTRY_EXEMPTIONS))
    for bad_reason in ("", "   ", None):
        mutated = dict(_OP_REGISTRY_EXEMPTIONS)
        mutated[sample_key] = bad_reason  # type: ignore[assignment]
        with pytest.raises(AssertionError):
            _assert_op_parity(_POLICED_REGISTRIES, mutated, _ALL_OPS, _PARITY_CONTEXT)
```

**Stale-row guard** (`:843-858`):
```python
def test_stale_row_fails() -> None:
    assert (
        _stale_exemption_rows(_OP_REGISTRY_EXEMPTIONS, _POLICED_REGISTRIES, _ALL_OPS)
        == []
    )
    stale = dict(_OP_REGISTRY_EXEMPTIONS)
    stale[("op-does-not-exist", "_DESTRUCTIVE_OPS")] = "planted stale op row"
    stale[(OP_SDP_LOCK, "_registry_does_not_exist")] = "planted stale registry row"
    problems = _stale_exemption_rows(stale, _POLICED_REGISTRIES, _ALL_OPS)
    assert len(problems) == 2, f"expected exactly 2 stale-row problems, got: {problems}"
```

**Non-vacuity leg — the `try/except/else raise` shape** (`:903-928`), stronger than `pytest.raises` because the `else` branch names the exact defect:
```python
    try:
        _assert_op_parity(altered, _OP_REGISTRY_EXEMPTIONS, _ALL_OPS, _PARITY_CONTEXT)
    except AssertionError:
        pass
    else:
        raise AssertionError(
            "Non-vacuity failure: removing OP_WRITE (a real shipped op with "
            "no exemption against _DESTRUCTIVE_OPS) from the in-memory "
            "registry copy did not make the parity assertion fail -- the "
            "parity gate is vacuous."
        )
```

> **HOUSE-RULE WARNING — do NOT copy this analog's comment style.** `test_op_registration_parity.py` carries large `#` comment blocks (e.g. `:126-128`, `:143-152`, `:172-186`, `:815-817`) that predate the 2026-08-29 zero-comments rule. Copy the *structures* and the *docstrings*; move every explanatory sentence into a docstring or into a reason string. Same warning for `test_chip_test_sdp_leg.py:210-228, 264-275, 887-888` and `tests/conftest.py:326-333`.

---

### `tests/test_derive_plan_structural_sentinel.py` — axis 2: whole-database sweep (D-07/D-08/D-09)

**Analog:** `tests/test_erase_flag_invariants.py`. This is the module whose docstring documents the vacuous-pass trap D-09 exists to defeat.

**Database singleton** (`:96-98`) — copy THIS line, not `test_chip_test_cycle.py:24` (Pitfall 9: that one omits `skip_local_override` and is machine-dependent):
```python
_REAL_DB = EpromDatabase(skip_local_override=True)
```

**Two-level selector** (`:126-132`) — a one-level `for row in db.proms:` iterates manufacturer keys and every downstream assertion passes vacuously:
```python
def _all_rows(db: EpromDatabase) -> list[tuple[str, dict]]:
    """Every (manufacturer, chip_record) pair in the database, exhaustively."""
    rows = []
    for manufacturer, chips in db.proms.items():
        for chip in chips:
            rows.append((manufacturer, chip))
    return rows
```
Note it is `-> list[tuple[str, dict]]` — an annotated def, so mypy checks its body. It is currently error-free at watermark 35; a verbatim copy is safe.

**Anti-vacuity docstring** (`:1-22`) — the module-docstring rubric to reproduce (excerpt):
> "**Anti-vacuity rule, stated up front …** the generated database (`EpromDatabase.proms`) is a mapping of manufacturer to a *list* of chip records, never a flat list of chips. A selector that scans the top level only (`for row in db.proms: ...`) iterates manufacturer *keys* … so every downstream filter on it returns an empty set and every assertion built on that set passes vacuously"

**Element-wise op-order pin + absolute counts** (`:264-303`) — the idiom for the "simpler alternative" frozen-pin route in RESEARCH §F, and for the 81-chip carve-out count:
```python
_AT28C256_FULL_EXPECTED_OP_ORDER = [
    OP_ID, OP_READ, OP_WRITE, OP_VERIFY, OP_ERASE, OP_BLANK_CHECK,
    OP_WRITE_BASELINE_B, OP_WRITE_BASELINE_A, OP_SDP_LOCK,
    OP_WRITE_INHIBITED, OP_SDP_UNLOCK, OP_WRITE_RESTORED,
]

def test_at28c256_full_plan_shape_is_pinned() -> None:
    """... Asserted as a list equality on the op sequence so an inserted or
    reordered step fails loudly rather than being missed by a membership
    check."""
    plan = derive_plan(_AT28C256_CHIP_NAME, _REAL_DB, write_scope="full")
    ops = [step.op for step in plan.steps]
    assert ops == _AT28C256_FULL_EXPECTED_OP_ORDER, (
        f"AT28C256 write_scope='full' op order drifted from the pinned "
        f"shape; expected {_AT28C256_FULL_EXPECTED_OP_ORDER}, got {ops}"
    )
```

---

### `tests/test_derive_plan_structural_sentinel.py` — axis 3: the erase→blank-check leg (D-05) and its 81-chip carve-out

**Analog:** `tests/test_chip_test_blank_check_order.py:130-165`, `test_at28c256_blank_check_moves_after_erase_but_stays_na` — already pins Finding 1's exact case for **one** chip. The new leg generalizes it to the whole DB; it must **not** restate the AT28C256 index-5/index-4 assertions.
```python
def test_at28c256_blank_check_moves_after_erase_but_stays_na():
    """Case 3, Phase 153 revision: protocol 0x0D auto-erases per page
    during write, so no step in this plan can ever leave the device
    blank -- blank-check stays NA ..."""
    plan = derive_plan(_CHIP_AUTO_ERASE_28C, _REAL_DB, write_scope="full")
    ops = [s.op for s in plan.steps]
    assert OP_ERASE in ops, "fixture setup error: AT28C256 must have an erase step"
    blank_check_index = ops.index(OP_BLANK_CHECK)
    erase_index = ops.index(OP_ERASE)
    assert blank_check_index == 5, (...)
    assert blank_check_index > erase_index, (...)
    blank_check_step = next(s for s in plan.steps if s.op == OP_BLANK_CHECK)
    assert blank_check_step.supported is False
    assert "FLAG_CAN_ERASE" not in blank_check_step.reason
```
Two patterns to carry over: (a) the `"fixture setup error: ..."` message class, which distinguishes a broken premise from a broken invariant; (b) asserting on `step.reason` content — the new carve-out asserts all 81 chips carry the one `protocol 0x0D (28C family) auto-erases…` reason string, **and** the absolute count 81 chips / 162 plans (RESEARCH Pitfall 1, Open Question 5).

---

### `tests/plan_corpus.py` (test helper, batch/transform)

**Analog:** `tests/test_chip_test_sdp_leg.py:217-260` for the content; `tests/fw_presence.py` / `tests/scan_paths.py` / `tests/fixtures/report_shapes.py` for the placement convention (a shared helper never lives in a `test_*` module).

**Operator double + plan builder** (`:228-260`) — copy `tests/test_chip_test.py:1009`'s *fuller* variant (it sets `sdp_lock`/`sdp_unlock` return values); the excerpt below is the sdp_leg near-copy, shown because it is the one with `_plan_with_steps` alongside:
```python
_OPERATOR_METHODS = [
    "check_eprom_id", "read_eprom", "check_eprom_blank", "write_eprom",
    "verify_eprom", "erase_eprom", "sdp_lock", "sdp_unlock",
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
`Mock(spec=[...])` is load-bearing: without `spec=`, an out-of-spec attribute access silently returns a truthy Mock. These defs are **unannotated**, so mypy does not check their bodies — keep them that way to protect the 35/35 watermark. The fixed `check_eprom_id` return `(True, 0x1234)` is what makes 2,545 steps come back SKIPPED (Pitfall 5); the docstring must state that limit.

---

### `tests/test_derive_plan_no_drop_sweep.py` (test, request-response through a mock)

**Analog:** `tests/test_chip_test_sdp_leg.py:827-897` — the only shipped `run_plan` + alignment assertion outside single-chip tests.

**Alignment assertion, with a message that names the failure mode** (`:890-896`):
```python
    results = run_plan(plan, operator, _REAL_DB)

    sentinel.assert_not_called()
    assert len(results) == len(_SHIPPED_OP_STRINGS), (
        f"run_plan returned {len(results)} results for "
        f"{len(_SHIPPED_OP_STRINGS)} steps -- a step was silently dropped "
        "or added while the sentinel was active"
    )
```
Also from this analog: `tests/test_chip_test.py:2612` is the one-chip instance of the same assertion (`M8720` @ `full`) — cite it, leave it alone.

**Deltas from the analog the planner must apply:**
- Use `run_plan`'s default `runs=2` (or `runs=1, allow_single_run=True`). A bare `runs=1` returns a single `StepResult(op="__plan__")` and the alignment fires for a reason unrelated to PRUNE-05 (`chip_test.py:1631-1642`, Pitfall 4).
- **No `monkeypatch`.** The analog patches `_SDP_OPS` and `_dispatch_sdp`; the new sweep injects everything and patches nothing.
- Put Pitfall 3's argument (an alignment-only proof cannot catch a prune, because both sides shrink together) in this module's **docstring**, so a later "simplification" cannot delete the frozen half without reading why it exists.

---

### `tests/fixtures/plan_shapes.json` + `tools/measure_plan_shapes.py` + `tests/test_plan_shapes_drift.py`

**Analog trio:** `tests/fixtures/part_number_delta.json` ← `tools/measure_part_number_delta.py` → `tests/test_part_number_delta_drift.py`. This is Phase 174's committed-artifact pattern and all three files are tracked.

**Generator skeleton** (`tools/measure_part_number_delta.py:1-40`) — shebang, docstring stating **exit codes**, path constants, `sys.path.insert`:
```python
#!/usr/bin/env python3
"""
Generator for the raw-CLI-token -> `part_number` delta artifact ...

`db.proms` is descended two levels -- manufacturer key to a list of chip
records -- because a single-level scan iterates manufacturer names and every
downstream count would pass vacuously.

Exit codes:
  0 -- derivation valid, artifact emitted successfully (or --check found no
       drift)
  1 -- derived aggregate failed validation, or --check found the committed
       artifact stale or missing
  2 -- the --issues input path is missing or unparsable
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_TOOLS_DIR = Path(__file__).parent
_APP_ROOT = _TOOLS_DIR.parent
_TARGET_DEFAULT = _APP_ROOT / "tests" / "fixtures" / "part_number_delta.json"

sys.path.insert(0, str(_APP_ROOT))


class DerivationError(Exception):
    """The --issues input could not be read (exit code 2)."""
```

**Deterministic render** (`:220-221`) — this one line is what makes byte-identity a usable gate:
```python
def render(payload: dict) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"
```

**`main()` — derive → validate → render → (`--check` | write), validate BEFORE emit** (`:263-301`):
```python
def main() -> int:
    args = _build_argparser().parse_args()
    try:
        payload = derive(args.issues)
    except DerivationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    try:
        validate(payload)
    except ValidationError as exc:
        print(f"ERROR: derivation validation failed: {exc}", file=sys.stderr)
        return 1
    output = render(payload)
    if args.check:
        if not args.target.is_file():
            print(f"DRIFT: target does not exist: {args.target}", file=sys.stderr)
            return 1
        existing = args.target.read_text(encoding="utf-8")
        if existing != output:
            print(f"DRIFT: {args.target} differs from a fresh regeneration ...", file=sys.stderr)
            return 1
        print(f"OK: {args.target} matches a fresh regeneration")
        return 0
    args.target.parent.mkdir(parents=True, exist_ok=True)
    args.target.write_text(output, encoding="utf-8", newline="\n")
    print(f"OK: wrote {args.target}")
    return 0
```

**Drift test — four legs** (`tests/test_part_number_delta_drift.py`). Leg 1, the `_generated_by` banner (`:48-57`), because JSON has no comment syntax:
```python
def test_committed_artifact_exists_and_carries_the_generated_by_banner():
    """The committed delta artifact must exist and name its generator --
    JSON has no comment syntax, so the `_generated_by` key is the
    do-not-edit banner."""
    assert _COMMITTED_ARTIFACT.exists(), (
        f"part_number_delta.json not found: {_COMMITTED_ARTIFACT}\n"
        "Run: cd firestarter_app && python tools/measure_part_number_delta.py"
    )
    payload = json.loads(_COMMITTED_ARTIFACT.read_text(encoding="utf-8"))
    assert payload.get("_generated_by"), "missing _generated_by banner key"
```

Leg 2, aggregates asserted **absolutely** (`:32-46, 60-81`) — the exact shape for RESEARCH §F's six aggregates (`rows: 746`, `distinct_part_numbers: 677`, `plans: 1354`, `distinct_shape_families: 8`, `total_steps: 16248`, `unsupported_steps: 9304`):
```python
_EXPECTED_AGGREGATE = {
    "rows": 746,
    "vendors": 59,
    "distinct_part_numbers": 677,
    ...
}

def test_aggregate_numbers_are_asserted_absolutely_not_only_for_drift():
    """...a drift-only gate would let a silently-changed measurement through
    as long as it stayed internally consistent."""
    aggregate = json.loads(_COMMITTED_ARTIFACT.read_text(encoding="utf-8"))["aggregate"]
    assert set(aggregate) == set(_EXPECTED_AGGREGATE), (...)
    for key, expected in _EXPECTED_AGGREGATE.items():
        assert aggregate[key] == expected, (
            f"aggregate[{key!r}] = {aggregate[key]!r}, expected {expected!r} "
            f"-- a measured number moved without a deliberate regeneration"
        )
```

Leg 3, byte-identical regeneration into a tempdir (`:84-120`):
```python
def test_codegen_produces_byte_identical_output():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        result = subprocess.run(
            [sys.executable, str(_GEN_SCRIPT), "--target", str(tmp_path), ...],
            capture_output=True, text=True, cwd=str(_APP_DIR),
        )
        assert result.returncode == 0, (
            f"measure_part_number_delta.py failed (exit {result.returncode}):\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert tmp_path.read_bytes() == _COMMITTED_ARTIFACT.read_bytes(), (
            "part_number_delta.json is STALE -- re-run to update:\n"
            "  cd firestarter_app && python tools/measure_part_number_delta.py\n" ...
        )
    finally:
        tmp_path.unlink(missing_ok=True)
```

Leg 4, the planted-fault non-vacuity leg (`:122-170`): mutate the input through an override seam, assert non-zero exit **and** that nothing was written (validate-before-emit).

**Two deltas the new drift test must apply** (both stated in the analog's own docstring at `:1-18`): resolve the artifact from `Path(__file__).parent` one level (the artifact is in-repo), and carry **no skip marker at all** — the analog's ancestor `test_sdp_bus_config_drift.py` skips only because its artifact lives in the sibling firmware repo, and copying that would build the fail-open gate D-16 forbids. The new generator has no `--issues`-style external input, so leg 4 needs a different override seam (e.g. a `--db`-shaped injection or a planted-plan path) — flag this as the one leg without a 1:1 analog.

---

### `tests/conftest.py:make_app_context` — the AppContext double for D-12's handler leg

**Source:** `tests/conftest.py:241-345`. Do not hand-build an `AppContext`; its docstring records why (a hand-built one reintroduces a ~25-site mypy error splat).

**The call to make** (RESEARCH §G, measured 0.48 s over 677 names):
```python
app = make_app_context(db=_REAL_DB, config_manager=Mock())
```
`config_manager=Mock()` is not cosmetic: `make_app_context` constructs a **real** `ConfigManager()` when the argument is `None` (`conftest.py:314-315`), and that is where this project's documented `~/.firestarter/config.json` write leak lives. `_resolve_write_scope` never touches it.

---

## Shared Patterns

### Whole-DB singleton (applies to: all three new test modules and the generator)
**Source:** `tests/test_erase_flag_invariants.py:98`
```python
_REAL_DB = EpromDatabase(skip_local_override=True)
```
**Never** copy `tests/test_chip_test_cycle.py:24` (`EpromDatabase()`), which silently violates D-07 and makes results machine-dependent.

### Corpus mutation (applies to: every anti-vacuity leg)
**Source:** semantics measured in RESEARCH §D against `chip_test.py:406-445`; the discipline itself is Phase 174's CR-01 defect.
```python
mutant = dataclasses.replace(plan, steps=[s for s in plan.steps if s.op != OP_VERIFY])
```
- `copy.copy(plan)` **shares** `plan.steps` — forbidden.
- Never assign to a `Step` attribute in place; the corpus fixture is module-scoped and the `Step` objects are shared. Field-level mutation goes through `dataclasses.replace(step, ...)`.

### Production helper, never re-derived (applies to: the write→verify predicate)
**Source:** `firestarter/chip_test.py:1236` — `cycle_block_bounds(plan.steps)`. D-02 forbids a re-implementation and RESEARCH §C shows why: the helper's own docstring family list omits the NA `erase`, so a rule built from the docstring is wrong on 373 plans. Fail closed: a write whose index is **not** inside `[start, stop)` is a violation, never a skip (Pitfall 2).

### Assertion-message style (applies to: every new assertion)
Every shipped analog attaches an f-string message that names (a) the measured value, (b) the expected value, and (c) *what defect the divergence means*. Examples above: `"-- a measured number moved without a deliberate regeneration"`, `"-- a step was silently dropped or added"`, `"-- the parity gate is vacuous."` Also copy the `"fixture setup error: ..."` prefix for premise checks (`test_chip_test_blank_check_order.py:148`, `test_op_registration_parity.py:915`), which separates a broken premise from a broken invariant.

### Explanation lives in docstrings, never comments (applies to: all new source)
| Analog | Explanation mechanism | Copyable as-is? |
|---|---|---|
| `test_erase_flag_invariants.py` | module + function docstrings (the 40-line anti-vacuity docstring) | **YES — the model** |
| `test_chip_test_blank_check_order.py` | function docstrings | **YES** |
| `test_part_number_delta_drift.py` | module + function docstrings | **YES** |
| `tools/measure_part_number_delta.py` | module docstring w/ exit codes; `argparse` `help=` strings | **YES** |
| `test_op_registration_parity.py` | docstrings + **large `#` comment blocks** (`:126-128`, `:143-152`, `:172-186`) + prose reason strings | **STRUCTURE yes, comments NO** |
| `test_chip_test_sdp_leg.py` | docstrings + `#` blocks (`:210-228`, `:264-275`, `:887-888`) | **STRUCTURE yes, comments NO** |
| `tests/conftest.py` | a very long docstring + `#` blocks (`:326-333`) | **Docstring yes, comments NO** |

The zero-comments rule (broadened 2026-08-29) is a standing operator hard rule a plan cannot override. Where an analog explains in a comment, the new file puts the same sentence in a docstring or in a reason-string value.

### Evidence transcript shape (applies to: every "seen RED" leg)
**Source:** `.planning/phases/174-blast-radius-invariance-harness/evidence/174-06-duplicate-row-red-green.txt` (all 13 transcripts tracked in the meta repo).
```
== LEG A1 duplicate ledger_id against PRE-FIX blob 5c0c7c9 -- RED expected, it exits 0 where non-zero is required
OK: 6 ledger row(s), 6 MILESTONES.md row(s) bound
rc_prefix_dup=0
== LEG A2 the same file against the FIXED checker -- GREEN expected, exit 2 naming the duplicate
ERROR: duplicate MILESTONES.md row for ledger_id '...'
rc_fixed_dup=2
```
Transcripts go in `.planning/phases/175-structural-sentinel-over-derive-plan/evidence/175-<NN>-<slug>.txt`, committed in the **meta** repo (test code commits in `firestarter_app`). Capture every one with `-o addopts=""`, or pytest's `-ra -q` default suppresses the count line.

---

## No Analog Found

| File / leg | Role | Data Flow | Reason |
|---|---|---|---|
| Leg 4 (planted-fault) of `tests/test_plan_shapes_drift.py` | test | file-I/O + subprocess | The analog plants a fault through the generator's `--issues` input seam. The new generator's only input is the shipped database, which must not be mutated (D-11) — the planner must design an override seam (e.g. `--db` / a planted-plan fixture path) or substitute a different validate-before-emit fault. |
| A whole-database `derive_plan` sweep | test | batch | **None exists in the tree.** Every plan-shape assertion today is single-chip or four-chip (RESEARCH §A(iv), cross-product verified empty). The sweep composes two existing patterns (`_all_rows` + `derive_plan`) but has no precedent instance. |
| A `pytest.mark.slow` marker | config | — | No marker convention exists in this project (no `markers` key in `pyproject.toml`, no `mark.slow` in `tests/`). RESEARCH recommends the module split instead of inventing one — that is why `test_derive_plan_no_drop_sweep.py` is a separate file. |

---

## Metadata

**Analog search scope:** `/workspaces/firestarter_app/tests/`, `/workspaces/firestarter_app/tools/`, `/workspaces/firestarter_app/pyproject.toml`, and `.planning/phases/174-blast-radius-invariance-harness/`.
**Files scanned:** 13 candidate analogs verified tracked via `git ls-files`; 8 read in targeted ranges.
**Pattern extraction date:** 2026-09-04
**Extraction interpreter note:** all measurement figures cited here come from RESEARCH.md's py3.11 CI-replica venv (`firestarter_app @ c134530`); this document adds no new measurements.
