# Phase 108: Test-Plan Engine + Address-Derived Pattern + Fingerprint - Pattern Map

**Mapped:** 2026-07-02
**Files analyzed:** 3 (2 new, 1 modified)
**Analogs found:** 3 / 3

> **Path note:** CONTEXT.md/RESEARCH.md cite short paths like `firestarter/eprom_operations.py:671`. The real files live in the **`firestarter_app/` submodule**: `firestarter_app/firestarter/eprom_operations.py`. All line numbers below are verified against source read this session. Executors commit INSIDE the `firestarter_app/` submodule on the milestone branch.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `firestarter_app/firestarter/chip_test.py` | service (orchestration engine) | transform + request-response | `dev_validate_family` (cli_handlers.py:1474) + `consistency_check_eprom` (eprom_operations.py:671) | role-match (compose-not-reimpl sibling) |
| `firestarter_app/firestarter/exceptions.py` | model (exception hierarchy) | — (data holder) | existing `EpromOperationError` (exceptions.py:37) | exact (same file, additive kwarg) |
| `firestarter_app/tests/test_chip_test.py` | test | request-response (mock) | `tests/test_validate_family_cmd.py` + `tests/test_consistency_check.py` | exact (two proven seams) |

Also **modified (one-line pass-through):** `firestarter_app/firestarter/eprom_operations.py:70` `_raise_for_error_response` — thread `error_code=response.id` (RPT-03 / D-07).

## Pattern Assignments

### `firestarter_app/firestarter/exceptions.py` — RPT-03 / D-07 (do this FIRST — foundational)

**Analog:** the file itself. `EpromOperationError` is today a bare `pass` subclass (exceptions.py:37-40):

```python
class EpromOperationError(Exception):
    """Custom exception for EPROM operation failures."""

    pass
```

**Change to copy (from RESEARCH § error_code Seam, D-07 — backward-compatible by construction):**

```python
class EpromOperationError(Exception):
    """Custom exception for EPROM operation failures."""

    def __init__(self, *args: object, error_code: int | None = None) -> None:
        super().__init__(*args)
        self.error_code = error_code
```

- **Subclasses inherit the kwarg automatically:** `ProtocolNotImplementedError` (exceptions.py:43) and `ChipNotImplementedError` (exceptions.py:49) both subclass `EpromOperationError` — no change needed to them.
- **`exceptions.py` is in the strict-mypy set (8-module gate, CLAUDE.md v1.8).** The kwarg MUST be annotated `error_code: int | None = None` and the method `-> None`. Do NOT use `Optional[int]` here — this file uses PEP 604 `|` union style (see `chip_resolver.py:16` `EpromDatabase | None`).
- Existing `raise EpromOperationError("…")` sites (eprom_operations.py:86, 526, 546) keep working with `error_code=None` — no edit required at those sites.

### `firestarter_app/firestarter/eprom_operations.py:70` — RPT-03 chokepoint (single-site edit)

**Analog / target:** `_raise_for_error_response` — the ONE place that already reads `response.id` for typed dispatch. Current code (lines 82-86):

```python
    from firestarter.messages import MSG_ERR_PROTOCOL_NOT_IMPLEMENTED

    if response.id == MSG_ERR_PROTOCOL_NOT_IMPLEMENTED:
        raise ProtocolNotImplementedError(response.message)
    raise EpromOperationError(message)                      # ← discards response.id today
```

**Change (D-07):** `raise EpromOperationError(message, error_code=response.id)`. `Response` is a namedtuple with `.id` = firmware message-id byte (frame_parser.py:18). Optionally also pass `error_code=response.id` to `ProtocolNotImplementedError` for symmetry (discretionary; there `.id` is always `0xBB`).

---

### `firestarter_app/firestarter/chip_test.py` (NEW — orchestration engine)

**Analogs:** `dev_validate_family` (cli_handlers.py:1474, compose-not-reimpl + resolve_chip execution path) and `consistency_check_eprom` (eprom_operations.py:671, runs-guard + SHA divergence math).

**Imports pattern** (copy the in-repo import style from eprom_operations.py:9-24 — stdlib first, then `firestarter.*` absolute imports; project uses `from typing import Optional, Tuple` in eprom_operations but PEP-604 `|` in the strict-mypy files — `chip_test.py` is NOT in the strict-8 set, so either style passes, prefer `|` for new code):

```python
import hashlib
from dataclasses import dataclass, field
from typing import Optional

from firestarter.chip_resolver import resolve_chip
from firestarter.constants import FLAG_CAN_ERASE  # 0x02 — do NOT redefine; import
from firestarter.database import EpromDatabase
from firestarter.eprom_operations import EpromOperator
from firestarter.exceptions import (
    ChipNotFoundError,
    ChipNotImplementedError,
    EpromOperationError,
)
```

**Pattern 1 — Plan derivation BYPASSES the support-status guard (SWEEP-01, D-02).**
Source: database.py:506 (`get_eprom`) + database.py:535 (`convert_to_programmer`). The guard lives ONLY inside `resolve_chip` (chip_resolver.py:16), which derivation never calls:

```python
full = db.get_eprom(name)                    # database.py:506 — full dict or None
prog = db.convert_to_programmer(full)        # database.py:535 — {} on empty
protocol  = prog["algorithm"]                # == full["protocol-id"]
etype     = full["electrical-type"]          # "UV-EPROM"|"EEPROM"|"Flash/EEPROM"|"SRAM"|"FRAM"
can_erase = bool(prog["flags"] & FLAG_CAN_ERASE)   # 0x02
```

`convert_to_programmer` (database.py:582-595) sets `FLAG_CAN_ERASE` only when `electrical-type ∈ {"EEPROM","Flash/EEPROM"}` AND `algorithm != 5`. So for protocol **0x05 (flash4) the flag is deliberately CLEAR** → the derived erase step MUST be `NA` (auto-erase per page; setting the flag would route 12V on a 5V part — hazard, RESEARCH Pitfall 6). Trust the flag; never re-invoke build-time `classify()`.

**Pattern 2 — Execution routes EVERY op through the guard-honoring path (SWEEP-02, RESEARCH Pitfall 2).**
Source: cli_handlers.py:1566 (`dev_validate_family`) — the compose-not-reimplement precedent:

```python
eprom_data = resolve_chip(rep_chip, db=app.db)      # guard-HONORING; raises ChipNotImplementedError/ChipNotFoundError
verdict_int = app.eprom_operator.write_cycle_eprom( # compose existing method, no re-impl
    rep_chip, eprom_data, source_image_path=source, runs=1, output_dir=..., operation_flags=0)
```

For `chip_test.py`: derivation used `get_eprom`/`convert_to_programmer`; each executed step RE-CALLS `resolve_chip(name, db)`. If it raises `ChipNotImplementedError`/`ChipNotFoundError`, that step's verdict is `SKIPPED`/`NA` with the reason recorded (the op was still listed, so the report shows "protocol supports write, but host guard refuses it"). The engine sets NO VPP and builds NO wire dict — it only calls the six `EpromOperator` methods.

**Operator methods the steps call** (eprom_operations.py — all take `(eprom_name, eprom_data_dict, ...)`; return `bool` except id):
- `check_eprom_id(name, data)` → `Tuple[bool, Optional[int]]` (line 1695) — id-first gate; precedent for non-bool verdict
- `read_eprom(...)` (line 622)
- `write_eprom(name, data, input_file_path, ...)` → `bool` (line 1555)
- `verify_eprom(name, data, input_file_path, ...)` → `bool` (line 1592)
- `erase_eprom(name, data, ...)` → `bool` (line 1628)
- `check_eprom_blank(name, data, ...)` → `bool` (line 1658) — has its OWN SRAM/FRAM short-circuit (lines 1667-1669), but derive_plan should mark SRAM/FRAM blank-check `NA` up front (RESEARCH § nuance recommendation (a)).

**Pattern 3 — `runs < 2` reject guard BEFORE any state-machine call (SWEEP-04, D-05).**
Source: `consistency_check_eprom` (eprom_operations.py:703-709). Mirror this exactly, but DEFAULT N=2 (not 3):

```python
def run_plan(..., runs: int = 2) -> ...:
    if runs < 2:            # D-05 — reject BEFORE any operator call
        logger.error(f"runs must be >= 2 (got {runs}); ...")
        return <error verdict>
```

**Pattern 4 — N-run SHA-256 divergence verdict → `marginal` (SWEEP-04, D-06).**
Source: eprom_operations.py:808-819:

```python
sha = hashlib.sha256(run_bytes).hexdigest()
distinct = sorted({r_sha for r_sha in results})
diverged = len(distinct) != 1        # destructive/verify: report `marginal`, NOT PASS/FAIL
```

`marginal` applies to **destructive/verify steps ONLY** (D-06). Read-step disagreement is a byte-level divergence metric (Pattern 5), NOT a verdict flip.

**Pattern 5 — byte-diff-offset math REUSED for the fingerprint (PATT-02, D-04).**
Source: `consistency_check_eprom` (eprom_operations.py:841-863). Do NOT write a parallel divergence impl (D-04 mandate). Extract this exact math into a shared helper the classifier calls; for the fingerprint the two arrays are **expected-pattern vs read-back**:

```python
cmp_len = min(len(expected), len(actual))
diff_offsets = [o for o in range(cmp_len) if expected[o] != actual[o]]
pct = 100.0 * len(diff_offsets) / cmp_len if cmp_len else 0.0
first = diff_offsets[0] if diff_offsets else None
```

**Pattern 6 — non-fatal per-step try/except (SWEEP-02, RESEARCH Pitfall 1 — the W29C040 locked-boot-block lesson).**
No shipped analog wraps steps this way (validate-family aborts per family). NEW code: each step gets its OWN `try/except` mapping any `EpromOperationError` → `BAD` verdict + captured `err.error_code` (from Pattern D-07), then CONTINUES. One step's failure must never abort the rest. Also capture `ChipNotImplementedError`/`ChipNotFoundError` → `SKIPPED`/`NA`.

**Pattern 7 — id-first destructive gate (SWEEP-03, RESEARCH Pitfall 4).**
No shipped analog. NEW: step 1 is `check_eprom_id`; on mismatch (`is_ok == False` OR `detected_id != expected`) set a `destructive_gate=CLOSED` flag that every destructive/write/erase step checks first, marking itself `SKIPPED` (chip left pristine). Non-destructive id/read/blank findings still recorded.

**Pure functions (NEW, no analog — pure compute, unit-test with hand-built arrays).** Copy verbatim from RESEARCH § Code Examples (D-01/D-02):

```python
def address_fold_byte(addr: int) -> int:
    return (addr ^ (addr >> 8) ^ (addr >> 16) ^ (addr >> 24)) & 0xFF

def generate_pattern(start: int, length: int) -> bytes:   # region-parameterized (D-02)
    return bytes(address_fold_byte(start + i) for i in range(length))

def prepass_images(length: int) -> tuple[bytes, bytes]:   # cheap all-0x00 / all-0xFF pre-pass
    return b"\x00" * length, b"\xFF" * length
```

Classifier contract (Claude's discretion on exact shape/thresholds; four buckets locked by D-03; direction by D-04). Must accept `addr_base` (region start) and cluster on `addr_base + offset` (RESEARCH Pitfall 3) — else the high-address-line signal is computed against the wrong bits. Buckets in order: `blank/contact` (near-all 0xFF) → `address-line` (power-of-two high-bit clustering) → `transport` (scattered + non-repeatable across N≥2 runs) → `indeterminate` (fallback, NEVER coerce — D-03).

---

### `firestarter_app/tests/test_chip_test.py` (NEW — engine unit tests, bench-free)

**Seam (a) — CLI/engine level `make_app_context()`** (tests/test_validate_family_cmd.py:28-54). Copy verbatim: `EpromDatabase(skip_local_override=True)` (no `~/.firestarter`, no serial) + `Mock(spec=EpromOperator)`:

```python
from unittest.mock import Mock
from firestarter.database import EpromDatabase
from firestarter.eprom_operations import EpromOperator

db = EpromDatabase(skip_local_override=True)
eprom_operator = Mock(spec=EpromOperator)
eprom_operator.check_eprom_id.return_value = (True, 0x1234)   # drive verdicts
eprom_operator.write_eprom.return_value = True
```

Set `.return_value` / `.side_effect` on the mock methods to drive OK/BAD/NA/SKIPPED/marginal and assert the plan/step results. `side_effect=EpromOperationError("x", error_code=0xA4)` proves the non-fatal capture (Pattern 6/7).

**Seam (b) — operator-internals monkeypatch** (tests/test_consistency_check.py:54-108). For tests that exercise the classifier against synthetic read-back streams and `error_code` propagation, monkeypatch `EpromOperator._operation_context` with a `@contextmanager fake_ctx` yielding `(cmd_data, buffer_size, op_name)` and `_run_state_machine` with a `fake_state_machine` that invokes `process_data_chunk_callback(0, payload)` then returns `(True, None)` / `(False, "timeout")` / raises `EpromOperationError(msg, error_code=0xA4)`:

```python
from contextlib import contextmanager

@contextmanager
def fake_ctx(self, eprom_name, eprom_data_dict, cmd, *a, **kw):
    yield {"address": 0, "memory-size": 65536}, 512, "READ"

def fake_state_machine(self, op_name, **kwargs):
    kwargs["process_data_chunk_callback"](0, payload)
    return (True, None)
```

**Pure-function tests (no mock):** `address_fold_byte`, `generate_pattern`, `classify_fingerprint` — hand-built arrays (flip bit A8 across a region → assert `address-line`; 98% 0xFF → `blank/contact`; scattered+non-repeatable → `transport`; ambiguous → `indeterminate`).

Test-file docstring/taxonomy style: copy the enumerated `D-10 Test 1..N` header block from test_consistency_check.py:13-52 (map to the Req→Test table in RESEARCH § Validation Architecture: SWEEP-01..04, PATT-01/02, RPT-03).

## Shared Patterns

### Compose-don't-reimplement
**Source:** `dev_validate_family` cli_handlers.py:1566 + `consistency_check_eprom` eprom_operations.py:696-699 ("Do NOT refactor into a parallel read implementation").
**Apply to:** every op step in `chip_test.py`. Zero new firmware dispatch, zero VPP-set, zero wire-dict build (Phase 109 CI-gates this).

### Guard bypass (derivation) vs guard honor (execution)
**Source:** `resolve_chip` chip_resolver.py:16-77 (the guard) + database.py:506/535 (the bypass path).
**Apply to:** `derive_plan` uses `get_eprom`/`convert_to_programmer` ONLY; `run_plan` re-calls `resolve_chip` per executed op. Never reuse the derivation dict as the execution dict (RESEARCH Pitfall 2).

### SHA-256 divergence + `runs<2` guard
**Source:** `consistency_check_eprom` eprom_operations.py:703-709 (guard), :808-819 (verdict), :841-863 (offset/pct math).
**Apply to:** SWEEP-04 marginal policy, D-06 read divergence metric, PATT-02 transport signal. Reuse — do not duplicate (D-04).

### error_code preservation
**Source:** `_raise_for_error_response` eprom_operations.py:70-86 (single chokepoint) + `Response.id` frame_parser.py:18.
**Apply to:** the `EpromOperationError.__init__` kwarg (exceptions.py) and every step's except-handler that captures `err.error_code`.

### Bench-free test seam
**Source:** `make_app_context()` test_validate_family_cmd.py:28-54 + monkeypatch seam test_consistency_check.py:54-108.
**Apply to:** all of `test_chip_test.py`. No hardware, no serial.

## No Analog Found

| Pattern | Role | Data Flow | Reason (build NEW, guided by RESEARCH) |
|---------|------|-----------|----------------------------------------|
| Non-fatal per-step executor (SWEEP-02) | orchestration | transform | No shipped code runs independent non-fatal steps; validate-family aborts per family. Build per RESEARCH Pitfall 1 + § Non-Fatal Step Execution. |
| id-first destructive gate (SWEEP-03) | orchestration | request-response | No shipped id→gate flag. Build per RESEARCH Pitfall 4. |
| `address_fold_byte` / `generate_pattern` (PATT-01) | pure compute | transform | Greenfield pure functions; copy from RESEARCH § Code Examples (D-01/D-02). |
| `classify_fingerprint` 4-bucket classifier (PATT-02) | pure compute | transform | Greenfield; reuses divergence math (Pattern 5) but the bucket logic is new. RESEARCH § Fingerprint Classifier gives candidate contract + thresholds (thresholds = Claude's discretion, D-04). |

## Metadata

**Analog search scope:** `firestarter_app/firestarter/` (eprom_operations.py, database.py, chip_resolver.py, exceptions.py, cli_handlers.py, frame_parser.py) + `firestarter_app/tests/` (test_validate_family_cmd.py, test_consistency_check.py).
**Files scanned:** 8 source + 2 test (5 strong analogs — early-stopped per protocol).
**Pattern extraction date:** 2026-07-02
**Constraints (CLAUDE.md v1.8):** `exceptions.py` is in the strict-8 mypy set → annotate the kwarg. `chip_test.py` is NOT (broader ruff+format gate applies). No firmware change, no `chip_database.json` hand-edit, no `messages.h` touch, no new dependency. Validate `ruff check` + `ruff format --check` against py39/3.11 (devcontainer py312 masks CI); watch f-string backslashes.
