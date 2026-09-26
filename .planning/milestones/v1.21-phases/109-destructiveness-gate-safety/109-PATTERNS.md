# Phase 109: Destructiveness Gate + Safety - Pattern Map

**Mapped:** 2026-07-02
**Files analyzed:** 3 (1 MODIFY, 2 CREATE)
**Analogs found:** 3 / 3

> **Repo note:** all source paths below are relative to the `firestarter_app/`
> submodule (host CLI Python). CONTEXT.md writes them without the prefix; the
> real files are `firestarter_app/firestarter/chip_test.py`,
> `firestarter_app/tools/check_dispatch.py`,
> `firestarter_app/tests/test_check_dispatch_invariants.py`, etc. Check the
> `v1.21` submodule branch is checked out before executors touch anything
> (see memory: submodule branch forked off v1.20, not beta).

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `firestarter/chip_test.py` (MODIFY) | service (test-plan engine) | transform / batch | *self* (Phase 108 in-place) | exact (evolving own contract) |
| `tools/check_devtest_orchestrator.py` (CREATE) | utility (CI checker) | batch / static-analysis | `tools/check_dispatch.py` | role-match (checker shape) |
| `tests/test_..._orchestrator...py` (CREATE) | test | subprocess request-response | `tests/test_check_dispatch_invariants.py` | exact (checker + neg-fixture) |

**Important analog caveat for the AST checker (D-02):** `tools/check_dispatch.py`
is a **DB-scanning** checker, NOT an AST checker — there is no existing
`import ast` tool anywhere in `tools/` or `tests/` (verified). D-02 says to
mirror check_dispatch's **tool _shape_** (module structure, exit-code
discipline, `if __name__ == "__main__": main()`, env-overridable path
constants, buckets-then-print-then-`sys.exit(1)`), while the **mechanism**
(walking `ast.parse(...)` over `chip_test.py` source) is new to this codebase.
The planner must supply the AST walk itself; only the surrounding tool skeleton
is copied.

---

## Pattern Assignments

### `firestarter/chip_test.py` (MODIFY — service, transform)

**Analog:** itself (Phase 108). This is an in-place evolution of three
functions plus one module-constant block. Below are the exact current forms the
planner must change.

#### Change 1 — `derive_plan()` : annotate-only → strip + advisory list (D-01)

Current signature and the write/erase append sites (`firestarter/chip_test.py:307-383`):

```python
def derive_plan(name: str, db: Any, *, destructive: bool = False) -> Plan:
    ...
    # write: always supported, always flagged destructive. Listed
    # regardless of the `destructive` kwarg (annotate-only, Task 2 `done`).
    steps.append(Step(op=OP_WRITE, supported=True, reason="", destructive=True))   # line 362
    steps.append(Step(op=OP_VERIFY, supported=True, reason=""))                    # line 364
    ...
    if can_erase and protocol != _PROTOCOL_FLASH4:
        steps.append(Step(op=OP_ERASE, supported=True, reason="", destructive=True))  # line 371
    else:
        ...
        steps.append(Step(op=OP_ERASE, supported=False, reason=reason, destructive=True))  # line 380
    return Plan(name=name, steps=steps, reason="")
```

**Required change (D-01):** when `destructive=False`, the destructive steps
(`OP_WRITE`, `OP_ERASE` — the `_DESTRUCTIVE_OPS` set already exists at line 409)
must be **omitted from `Plan.steps`** and instead recorded in a **new advisory
field** on `Plan` (e.g. `locked_destructive: list[tuple[str, str]]` of
`(op, reason)`). The executable `steps` list literally lacks them so `run_plan`
can never iterate them. `destructive` is read only from this call's kwarg —
never config, never env (see the `dev_validate_family` seam which reads
`--destructive`-style flags off the CLI invocation, not config).

**Preserve the guard-bypass split (SAFE-02):** derivation still reads only
`db.get_eprom(name)` (line 319) + `db.convert_to_programmer(full)` (line 323) —
NEVER `resolve_chip`. This is asserted by existing tests
(`test_derive_plan_never_calls_resolve_chip`,
`test_derive_plan_reads_via_get_eprom_and_convert_to_programmer_only` in
`tests/test_chip_test.py`) — do not break them.

**`Plan` dataclass to extend** (`firestarter/chip_test.py:298-304`):

```python
@dataclass
class Plan:
    name: str
    steps: list[Step] = field(default_factory=list)
    reason: str = ""
    # ADD (D-01): advisory-only; run_plan MUST NOT iterate this.
    # locked_destructive: list[tuple[str, str]] = field(default_factory=list)
```

#### Change 2 — UV small-region write cap (PATT-03) replaces the stand-in

Current stand-in (`firestarter/chip_test.py:556-562`):

```python
# Region used for the write/verify address-derived pattern fingerprint
# (Task 3, PATT-01/02 wiring). A small fixed region keeps the bench-free
# engine's write/verify step cheap and matches the region-parameterized
# generator contract (D-02) -- Phase 109 owns the concrete UV small-region
# window; this default is a reasonable stand-in for non-UV chips.
_WRITE_REGION_START = 0
_WRITE_REGION_LENGTH = 256
```

Consumed at (`firestarter/chip_test.py:721` and `768`):

```python
expected = generate_pattern(_WRITE_REGION_START, _WRITE_REGION_LENGTH)   # line 721
...
fingerprint = classify_fingerprint(
    expected, actual, repeat_divergent=diverged, addr_base=_WRITE_REGION_START,  # line 768
)
```

**Required change (PATT-03, D-93/Claude's-discretion default):** for
**UV-EPROM** chips only, the write region becomes **top-anchored**:
`start = mem_size - 256`, `length = 256`, i.e. `[mem_size-256, mem_size)`. Non-UV
chips keep the engine default region. Key constraints:
- `length` is an **engine module constant** (recommended `_UV_WRITE_REGION_LENGTH = 256`)
  — **never** read a region size from any DB field (SC4: a malicious/misconfigured
  DB entry must not widen it). `mem_size` is a *placement* input (bounds the top
  anchor), not a *width* input.
- `mem_size` source: `full.get("memory-size")` (also mirrored into the
  programmer dict). Verified present: `AM2716` (UV-EPROM) → `memory-size == 2048`,
  so the UV window is `[1792, 2048)`.
- UV detection axis: `etype == "UV-EPROM"` — the exact string already used at
  `firestarter/chip_test.py:375`. `etype` is `full.get("electrical-type", "")`
  (line 325).
- The high-address base (all high bits set) makes `generate_pattern`'s
  address-XOR-fold exercise the upper-address decode (the Bug-A upper-address
  read-path fault surface — see CONTEXT `<specifics>`).
- The concrete region must flow into **both** `generate_pattern(start, length)`
  and `classify_fingerprint(..., addr_base=start)` (Pitfall 3 — addr_base must be
  the ABSOLUTE region start, else the address-line clustering in
  `classify_fingerprint` lines 192-215 computes against the wrong bits).
- `generate_pattern` itself (`firestarter/chip_test.py:59-67`) is already
  region-parameterized (D-02) — **do NOT modify it**; only choose different
  `start`/`length` per chip. This means the region selection likely needs to be
  computed inside `_dispatch_multi_run` / `_run_step` where the chip's
  `eprom_data` (with `memory-size`) is available, or passed down from `run_plan`.

#### Change 3 — N-of-M applicable count for the SWEEP-05 banner data

There is currently no M/N counting. Required (SWEEP-05, applicable-only default):
- **M** = steps a `--destructive` run would **execute** for this chip = supported
  steps in the *destructive* derivation, i.e. `sum(1 for s in steps if s.supported)`
  **plus** the applicable entries in the new `locked_destructive` advisory list.
  NA/inapplicable steps are excluded (blank-check NA on SRAM/FRAM — line 346;
  id NA when `chip_id == 0` — line 337; erase NA on UV / non-`FLAG_CAN_ERASE` —
  lines 370-381).
- **N** = steps this non-destructive run actually executed (ran, any verdict —
  a ran-but-`BAD` step counts as ran; `NA`/`SKIPPED` do not).
- This phase produces the **banner data** (N, M, and the locked-step list);
  banner *rendering* is Phase 110/112. Do not render here.

#### SAFE-02 property to preserve (verify, do not weaken)

`run_plan` / `_run_step` / `_dispatch_*` (`firestarter/chip_test.py:468-791`):
- every executed op re-resolves via `resolve_chip(name, db=db)`
  (`_resolve_or_none`, line 461) — the guard-HONORING path.
- sets no VPP, builds no wire dict, passes no `--force`; only calls existing
  `EpromOperator` public methods (`check_eprom_id`, `read_eprom`,
  `check_eprom_blank`, `write_eprom`, `verify_eprom`, `erase_eprom`).
- one step's exception/BAD never aborts the loop (per-step try/except, line 582).
This is the exact behaviour the new SAFE-03 checker asserts mechanically.

---

### `tools/check_devtest_orchestrator.py` (CREATE — utility, AST static-analysis)

**Analog:** `tools/check_dispatch.py` — copy the **tool skeleton**, supply a new AST body.

**Module skeleton to mirror** (`tools/check_dispatch.py:1-33, 174-176, 505-506`):

```python
"""<docstring: purpose + explicit Exit codes block>"""

import ast
import os
import sys

# env-overridable path constants, mirroring check_dispatch.py:24-33
_HERE = os.path.dirname(__file__)
_CHIP_TEST = os.path.join(_HERE, "..", "firestarter", "chip_test.py")
# (Phase 112 will add the dev-test handler path; scope to tolerate its absence now.)

def main():
    """Entry point: parse target sources, collect violations, exit non-zero on any."""
    ...

if __name__ == "__main__":
    main()
```

**Exit-code discipline to mirror** (`tools/check_dispatch.py:375-502`): collect
into named violation buckets; if any bucket is non-empty, print a per-bucket
`FAIL:` summary and `sys.exit(1)`; otherwise print a `PASS:` line and return 0.

**Deny-list the AST walk must flag (D-02):**
- VPP-set call sites (e.g. attribute calls whose name sets/enables VPP —
  planner defines the exact symbol set; there are currently **zero** in
  `chip_test.py`, which is what makes the gate meaningfully green today).
- raw command-dict / wire-JSON construction (a dict literal carrying wire keys
  like `"cmd"`, `"algorithm"`, `"vpp_mv"`, `"bus-config"` — see the wire example
  in `firestarter_app/CLAUDE.md`).
- `force=True` keyword args and any `"--force"` string literal / `force=`
  pass-through.

**Assert (host-only framing, D-02):** the checker also asserts zero new firmware
dispatch entries — naturally satisfied because this is host-only Python (no
firmware repo change); the *real* risk it guards is a VPP-set / raw-command /
`--force` call sneaking into the host orchestrator.

**Anti-hollow mandate (D-02 / SC / v1.12 GATE-03 lesson):** the checker MUST be
genuinely populated and build-failing on a planted violation — NOT a
declared-empty detector. Prove this via the paired pytest's negative fixture
(below). Reference the memory: v1.12 hollow-GATE-03 is the exact failure mode to
avoid.

**Scope tolerance (Integration Points):** the Phase-112 `@dev.command("test")`
handler does not exist yet — the checker must tolerate its absence now and cover
it when added (or defer the handler-scan to Phase 112; planner's call).

---

### `tests/test_..._orchestrator...py` (CREATE — test, subprocess)

**Analog:** `tests/test_check_dispatch_invariants.py` — copy the subprocess
invocation + clean-pass + planted-fail contract (D-03).

**Clean-pass pattern** (`tests/test_check_dispatch_invariants.py:21-69`):

```python
import subprocess
import sys
from pathlib import Path

_FA_DIR = Path(__file__).parent.parent  # absolute firestarter_app dir, cwd-independent

def test_checker_exits_zero_on_clean_source() -> None:
    result = subprocess.run(
        [sys.executable, "tools/check_devtest_orchestrator.py"],
        cwd=str(_FA_DIR),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"checker exited {result.returncode}.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS:" in result.stdout
```

**Planted-fail pattern (the anti-hollow contract, D-03 — the part
check_dispatch's test does via synthetic in-process fixtures at
`test_check_dispatch_invariants.py:126-190`, but here MUST be a real
subprocess-level violation):** write a deliberately-violating fixture source
file (e.g. a temp `.py` containing a VPP-set call / `force=True` /
raw-wire-dict), point the checker at it via the env-override path constant, and
assert **non-zero** exit:

```python
def test_checker_exits_nonzero_on_planted_violation(tmp_path) -> None:
    bad = tmp_path / "planted_bad.py"
    bad.write_text("def h(op):\n    op.set_vpp(12000)\n    return {'cmd': 2, 'vpp_mv': 12000}\n")
    result = subprocess.run(
        [sys.executable, "tools/check_devtest_orchestrator.py"],
        cwd=str(_FA_DIR),
        capture_output=True,
        text=True,
        env={**os.environ, "FIRESTARTER_DEVTEST_SRC": str(bad)},  # env-override, mirrors check_dispatch DB_FILE
    )
    assert result.returncode != 0
    assert "FAIL:" in result.stdout
```

The env-override seam mirrors `check_dispatch.py:26` (`FIRESTARTER_DB_FILE`) —
plumb an equivalent `FIRESTARTER_DEVTEST_SRC` (name is planner's call) so the
negative fixture can be injected without editing the real source. This is the
enforcement point: `.github/workflows/ci.yml` runs
`pytest tests/ --cov=firestarter --cov-fail-under=70` (line 69), which executes
this test; a dedicated `ci.yml` step is optional (D-03).

---

## Shared Patterns

### Unit-test seam (mock operator + skip_local_override)
**Source:** `tests/test_chip_test.py:276, 488-508` and `cli_handlers.py:1474-1624`
**Apply to:** every `chip_test.py` change

```python
_REAL_DB = EpromDatabase(skip_local_override=True)          # no ~/.firestarter, no serial
# Mock(spec=[...]) stand-in for EpromOperator — drives each step bench-free:
op = Mock(spec=["check_eprom_id", "read_eprom", "check_eprom_blank",
                "write_eprom", "verify_eprom", "erase_eprom"])
op.write_eprom.return_value = True
```
`dev_validate_family` (`cli_handlers.py:1566-1576`) is the sibling handler that
uses the same `resolve_chip(name, db=app.db)` + compose-existing-operator-method
pattern that `run_plan`/`_run_step` follow — keep `dev test` (Phase 112)
structurally identical (no VPP, no wire dict, no `--force`).

### Exit-code + bucket discipline (CI checker)
**Source:** `tools/check_dispatch.py:174-176, 375-502, 505-506`
**Apply to:** `tools/check_devtest_orchestrator.py`
Collect named buckets → print `FAIL:` per bucket + `sys.exit(1)` if any non-empty
→ else print `PASS:` line. `if __name__ == "__main__": main()`.

### Env-overridable path constant
**Source:** `tools/check_dispatch.py:26-33` (`FIRESTARTER_DB_FILE`)
**Apply to:** the new checker's target-source path — enables the negative-fixture
injection without editing real source.

### Region-parameterized pattern generator (do NOT reimplement)
**Source:** `firestarter/chip_test.py:59-67` (`generate_pattern`) + 138-236
(`classify_fingerprint`, `addr_base`)
**Apply to:** PATT-03 — choose `start`/`length` per chip; never touch the generator;
always pass `addr_base == region start` (Pitfall 3).

---

## No Analog Found

None. All three work items have a concrete in-repo analog. The only novelty is
the **AST-walk mechanism** inside the new checker (no `import ast` tool exists in
this codebase) — the tool *shape* is copied from `check_dispatch.py`; the AST
body is written fresh per D-02.

## Metadata

**Analog search scope:** `firestarter_app/firestarter/`, `firestarter_app/tools/`,
`firestarter_app/tests/`, `firestarter_app/.github/workflows/`
**Files scanned:** chip_test.py, check_dispatch.py, test_check_dispatch_invariants.py,
cli_handlers.py (dev_validate_family), test_chip_test.py (seam), ci.yml, constants
& DB spot-checks (AM2716 memory-size)
**Pattern extraction date:** 2026-07-02
