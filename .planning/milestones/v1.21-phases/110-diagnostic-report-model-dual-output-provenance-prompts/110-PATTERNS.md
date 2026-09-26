# Phase 110: Diagnostic Report Model + Dual Output + Provenance Prompts - Pattern Map

**Mapped:** 2026-07-02
**Files analyzed:** 2 (1 new source module + 1 new test file)
**Analogs found:** 2 / 2 (both strong; every sub-pattern has a verified in-repo precedent)

## Scope Note

HOST-ONLY phase in `firestarter_app/`. Pure host-side data assembly: a new
`diagnostic_report.py` composing Phase-108/109 dataclasses + four new
sub-objects, dual-rendered (rich table + fenced JSON) from a single source,
plus a `rich.prompt` provenance component and a read-only advisory DB-diff. No
firmware change, no VPP-set, no wire dict, bench-free, unit-testable. The
research (110-RESEARCH.md) is HIGH-confidence and already verified every analog
line this map cites.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `firestarter/diagnostic_report.py` (NEW) | model + utility | transform (compose engine output → dual serialization) | `firestarter/cli_handlers.py:1371` `_write_artifact` + `firestarter/chip_test.py` dataclasses | role-match (dual-serialize shape) + exact (dataclass composition style) |
| `tests/test_diagnostic_report.py` (NEW) | test | request-response (mock operator/prompt/DB) | `tests/test_chip_test.py:570` `_mock_operator` seam | exact |

Sub-object roles inside `diagnostic_report.py` (all `@dataclass`, D-01):
`DiagnosticReport` (aggregate model), `AutoCapture`, `Provenance`,
`TransportHealth`, `DbDiff` — plus `prompt_provenance()` (prompt component),
`is_submittable()` (predicate), `build_db_diff()` (read-only DB transform).

## Pattern Assignments

### `firestarter/diagnostic_report.py` (model + transform)

**Analog A (dual-serialization shape):** `firestarter/cli_handlers.py:1371-1418` `_write_artifact` / `_render_markdown`
**Analog B (dataclass style + composed objects):** `firestarter/chip_test.py` (`StepResult` L453, `Plan` L298, `BannerCounts` L908, `Fingerprint` L127)

---

#### JSON serialization + UTC timestamp pattern (RPT-01, D-01/D-02) — from `_write_artifact` (cli_handlers.py:1383-1392)

```python
artifact: Dict[str, Any] = {
    "generated": datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    ),
    "harness_version": "71",
    "cells": cells,
}
json_file = out_path / "validation-matrix.json"
json_file.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
```

**Copy this shape for `to_dict()`/`to_json_block()`:** a single dict literal with
a `generated` UTC timestamp (verbatim strftime format) and a version key —
here `schema_version` = a module-level `SCHEMA_VERSION = "1.0"` constant (D-02,
mirrors the analog's `"harness_version"`). Serialize with
`json.dumps(self.to_dict(), indent=2)`. **Divergence from analog:** the analog
writes two *files* from two functions; RPT-01 (D-01) requires the human render
(`render()` → `rich.Table`) to read the SAME `to_dict()` dict, NOT a second
hand-maintained field list (the analog's `_render_markdown` iterating its own
`cells` is acceptable only because `cells` IS the canonical dict — replicate
that: the table iterates the dict `to_dict()` produced, never re-parses the JSON
string).

**Anti-pattern (RPT-01 forbids):** the analog `_render_markdown` reads
`cell.get('retry_count', 0)` — a `0` default. For `TransportHealth` counters this
is EXACTLY the false-zero XPORT-01 forbids. Use the `NOT_MEASURED = "not measured"`
sentinel instead, substituted in ONE place inside `to_dict()`.

---

#### Composed dataclass style (RPT-01/RPT-02) — from `chip_test.py:453` `StepResult` + `:908` `BannerCounts`

```python
@dataclass
class StepResult:
    op: str
    verdict: str
    reason: str = ""
    error_code: int | None = None          # RPT-02 per-op exact firmware code — READ, don't re-derive
    fingerprint: Fingerprint | None = None  # RPT-02 byte-mismatch classification — READ
    run_count: int = 0
    divergence: dict[str, Any] | None = None
```

```python
@dataclass
class BannerCounts:
    n_ran: int
    m_applicable: int
    locked_steps: list[tuple[str, str]] = field(default_factory=list)
```

**Copy this style:** plain `@dataclass`, `X | None = None` for absent scalars
(matches CONTEXT recommendation: `null` for genuinely-absent scalars),
`field(default_factory=list)` for collections. The report is a pure CONSUMER —
`StepResult.error_code` and `.fingerprint` ARE the RPT-02 per-step auto-capture
fields; compose them, never recompute. `Fingerprint.classification`
(chip_test.py:134, one of blank/address-line/transport/indeterminate) feeds the
DB-diff "inconclusive" branch.

**Compose, don't recount (RPT banner data):** `count_applicable(plan, results)`
(chip_test.py:925) already produces `BannerCounts` from the ONE `plan` object
(`m_applicable = sum(supported steps) + len(locked_destructive)`). The report's
`to_dict()` emits `n_ran`/`m_applicable`/`locked_steps` from this — never a
second `derive_plan()` call (chip_test.py comment L305: `run_plan` MUST NOT
iterate `locked_destructive`; the report only reads it for banner counts).

---

#### DB-diff read-only support_status read (RPT-05, D-07) — from `chip_resolver.py:54`

```python
support_status = raw_config.get("support_status", "supported")
```

**Copy this exact read site.** Source the raw config via
`db.get_eprom_config(name)` → `(config_dict, manufacturer_str)` tuple
(database.py:465-468), then `(raw_config or {}).get("support_status", "supported")`.
`build_db_diff(name, db, results)` maps the sweep `{r.verdict for r in results}`
(vocab OK/BAD/NA/SKIPPED/marginal) to a plainly-labeled ADVISORY string
(exact wording is planner discretion, D-07). **Load-bearing constraint:** the
proposed disposition is DESCRIPTIVE TEXT, never a concrete `support_status`
value, never written back. `get_eprom_config` returns a tuple — unpack `[0]` for
the config dict.

---

#### rich.prompt provenance component (RPT-04, D-06) — from `firmware.py:613` (import at :20)

```python
if Confirm.ask(
    f"New firmware {latest_version} available for {board_to_use} (current: {current_version}). Update now?",
    default=False,
):
```

**Copy the `Confirm.ask(..., default=...)` call style** (and `Prompt.ask` with
`choices=`/`default=` for enumerated fields). But make the callables INJECTABLE
for unit-testability (Pattern 2 / Pitfall 4):
`prompt_provenance(is_uv, *, ask=Prompt.ask, confirm=Confirm.ask) -> Provenance`.
Field set (D-06): shield revision (enumerated `["Rev 2.2","Rev 2.0","modified Rev 0","other","not sure"]`
+ free-text escape on "other"), chip origin (new/blank vs pulled/used), UV-eraser
`Confirm` ONLY when `is_uv`, pot-touched `Confirm` + optional note.

**`is_submittable` predicate (D-05):** `"not sure"` is a FILLED answer;
only blank/`None` on a required field fails:
```python
def is_submittable(p: Provenance) -> bool:
    return bool(p.shield_rev) and bool(p.chip_origin) and p.pot_touched is not None
```

**Anti-pattern (D-05 forbids):** never auto-derive `shield_rev` from the
`hw_revision` byte (cannot distinguish Rev 2.2/2.0/modified Rev 0 — Bug A
lesson). The report module must NOT import `HardwareManager`/`SerialCommunicator`.

---

### `tests/test_diagnostic_report.py` (test)

**Analog:** `tests/test_chip_test.py:560-581` `_mock_operator` seam

```python
_OPERATOR_METHODS = [
    "check_eprom_id", "read_eprom", "check_eprom_blank",
    "write_eprom", "verify_eprom", "erase_eprom",
]

def _mock_operator(**returns):
    op = Mock(spec=_OPERATOR_METHODS)
    op.check_eprom_id.return_value = (True, 0x1234)
    ...
    for name, value in returns.items():
        getattr(op, name).return_value = value
        getattr(op, name).side_effect = None
    return op
```

**Copy this seam three ways:**
1. **Mock operator** — reuse the `_mock_operator(**returns)` pattern (or import
   the same fixture shape) to drive `run_plan` results into the report.
2. **Mock prompt** — pass `ask=Mock(side_effect=[...])`, `confirm=Mock(side_effect=[...])`
   into `prompt_provenance` (never touches a TTY; Pitfall 4).
3. **Mock DB, read-only proof (RPT-05)** — `Mock(spec=["get_eprom","get_eprom_config","convert_to_programmer"])`
   (spec has NO write method) so any write raises `AttributeError` by construction.

**DB fixture:** `EpromDatabase(skip_local_override=True)` for real-DB reads
(test_chip_test.py:282). **Structural assertion pattern:** mirror the
no-`resolve_chip` source-scan assertion (test_chip_test.py:308) to assert the
module contains no `support_status =` write and no `SerialCommunicator`/
`HardwareManager` import (SAFE-02 / D-05 / D-07).

---

## Shared Patterns

### Honest-fallback sentinel (XPORT-01, D-03)
**Source principle:** Phase-108 `indeterminate` fingerprint bucket (chip_test.py:134); NOT the analog `_render_markdown`'s `retry_count, 0` default (that is the anti-pattern).
**Apply to:** All `TransportHealth` counters.
Single module constant `NOT_MEASURED = "not measured"`; substitute in ONE place inside `to_dict()`. `transport_suspect` trips ONLY from present+elevated counters — since the Transport Counter Survey (RESEARCH §99-118) verified NONE are reachable today, all counters render `"not measured"` and the flag is always `False`. This is an ACCEPTED outcome, not a gap.

### Composed-dataclass + hand-written `to_dict()` (RPT-01, D-01/D-02)
**Source:** `chip_test.py` dataclass style + `_write_artifact` json shape.
**Apply to:** `DiagnosticReport` and all four sub-objects.
Hand-write `to_dict()` (NOT `dataclasses.asdict()` wholesale — it cannot inject `schema_version` or the `NOT_MEASURED` sentinel; Pitfall 3). Single `SCHEMA_VERSION` constant. `render()` and `json.dumps` both consume the ONE dict `to_dict()` returns.

### Injectable-callable test seam (RPT-04, Pitfall 4)
**Source:** `test_chip_test.py:570` `_mock_operator` (`Mock(spec=[...])`).
**Apply to:** `prompt_provenance` (`ask`/`confirm` params) and the DB param.
Keeps every interactive/DB-touching component unit-testable without a TTY or serial, satisfying the `--cov-fail-under=70` CI gate.

### SAFE-02 / orchestrator-only import discipline
**Source:** chip_test.py:884 DATA-ONLY note; milestone invariant.
**Apply to:** the whole `diagnostic_report.py` module.
No `SerialCommunicator`/`HardwareManager` import, no VPP-set, no wire dict, no `--force`, zero firmware dispatch. The Phase-112 handler (not this module) is what the SAFE-03 AST checker scans — keep the report module import-light and pure.

## No Analog Found

| File/Concern | Role | Data Flow | Reason → Fallback |
|--------------|------|-----------|-------------------|
| Transport counter capture | (would-be) instrumentation | event-driven | RESEARCH §Transport Survey verified NO COBS/CRC/retry/timeout counters exist in `serial_comm.py` (ring-fenced GATE-1.8d). XPORT-01 is a `"not measured"` fallback, NOT new instrumentation. Do NOT add counters. |
| `version:board` fetch inside the report | — | — | Pitfall 1: `programmer_info` lives on the transient per-op `comm` (serial_comm.py:686), gone by report-assembly time. `AutoCapture.fw_board_identity: str \| None` RECEIVES a threaded-in string (Phase 112 captures it); the report never opens serial. No analog for "report fetches identity" because it must not. |

## Cross-Phase Seams (planner note)

- **Phase 112** captures `operator.comm.programmer_info` at sweep start and threads it into `AutoCapture.fw_board_identity` (this module accepts `str | None`, defaults `None` → `null`/"unknown").
- **Phase 112** invokes `prompt_provenance()` before the sweep and calls `render()`/writes `to_json_block()` to `--output-dir`.
- **Phase 111** fills the `vpp_vpe_mv` slot (this module leaves it `None`).
- **Phase 113** parses the fenced JSON via `schema_version`; the RPT-05 DB-diff feeds Phase 114 as read-only advisory data.

## Metadata

**Analog search scope:** `firestarter_app/firestarter/` (cli_handlers.py, chip_test.py, chip_resolver.py, database.py, firmware.py) + `firestarter_app/tests/test_chip_test.py`
**Files scanned:** 6 (all analogs pre-verified in 110-RESEARCH.md this session)
**Pattern extraction date:** 2026-07-02
