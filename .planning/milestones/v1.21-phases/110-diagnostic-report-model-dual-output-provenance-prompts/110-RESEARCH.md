# Phase 110: Diagnostic Report Model + Dual Output + Provenance Prompts - Research

**Researched:** 2026-07-02
**Domain:** Python host-side data assembly — single-source dual-rendered dataclass (`rich` table + fenced JSON), `rich.prompt` provenance component, read-only DB-diff, honest-fallback transport-health section
**Confidence:** HIGH (all findings verified against the actual `firestarter_app/` source this session; zero external packages introduced)

## Summary

Phase 110 builds a pure host-side `DiagnosticReport` model that wraps the Phase-108 `Plan`/`StepResult`/`Fingerprint` objects plus four new sub-objects (auto-capture identity, provenance, transport-health, DB-diff), and renders that one source object two ways — a `rich` table and a fenced ```` ```json ```` block — from a **single set of field accessors**. It also builds the `Provenance` model, the `rich.prompt`-based prompt component, and the `is_submittable` predicate (Phase 112 invokes them). Everything is bench-free and unit-testable via `EpromDatabase(skip_local_override=True)` + a `Mock(spec=[...])` operator — the exact seam `test_chip_test.py` already uses.

The single hard research question — **what transport counters are actually reachable during a sweep?** — has a definitive answer: **none.** `serial_comm.py` accumulates zero COBS-error / CRC-failure / retry / timeout counters. It logs `warning()` on truncation and re-sync, arms a one-shot fault-injection hook, and raises `SerialTimeoutError`, but nothing is *counted* or *exposed* on the `SerialCommunicator` or `EpromOperator`. This **legitimizes the XPORT-01 `"not measured"` fallback for every counter today** (D-03's ACCEPTED outcome), and `transport-suspect` correctly never trips. Do NOT add counters to the hot serial path.

**Primary recommendation:** One frozen-ish `@dataclass DiagnosticReport` composing existing + new sub-dataclasses; a single `to_dict()` (module-level `SCHEMA_VERSION` constant baked in) is canonical; `render()` builds the `rich` table by reading the SAME field accessors (never re-parsing the JSON, never a second field list). Provenance uses `rich.prompt.Prompt.ask`/`Confirm.ask` behind an injectable prompt-function seam. Transport-health emits `"not measured"` for all counters this phase. DB-diff reads `support_status` via `db.get_eprom_config(name)[0].get("support_status","supported")` and emits an advisory proposed-disposition string derived purely from sweep verdicts — never a write.

## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** One composed `@dataclass DiagnosticReport` composing Phase-108 `Plan`, `list[StepResult]`, per-step `Fingerprint` + new sub-dataclasses (`AutoCapture`/identity, `Provenance`, `TransportHealth`, `DbDiff`). A single `to_dict()` → `json.dumps(..., indent=2)` in a fenced ```` ```json ```` block; a single `render()` builds the `rich` table **from the same dataclass field accessors**. The table is NEVER built from a second hand-maintained field list and NEVER parsed back out of the JSON string. Add a field once → both renders pick it up. Rejected: assembling JSON dict independently from table rows.
- **D-02:** `schema_version` is a single-source module/class constant (recommend `SCHEMA_VERSION = "1.0"`) serialized into `to_dict()`. MUST be present in the JSON and single-sourced.
- **D-03:** NO new transport instrumentation. Capture ONLY counters the serial/COBS layer *already* exposes; unavailable ⇒ explicit `"not measured"` sentinel (never a false `0`); `transport-suspect` trips ONLY from *present, elevated* counters — never inferred from absent ones. Mirrors Phase 108's honest-`indeterminate` bucket. Rejected: instrumenting the transport layer this phase.
- **D-04:** Build the `Provenance` model + prompt component + `is_submittable` predicate in THIS phase; Phase 112 only calls it. Mirrors Phase 109's data/rendering split.
- **D-05:** "not sure" is a *filled* (submittable) answer; only an unanswered/blank field blocks submission. Shield revision offers explicit "not sure" and NEVER auto-derives from the `hw_revision` byte.
- **D-06:** Prompt field set — (a) **shield revision**: enumerated (Rev 2.2 / Rev 2.0 / modified Rev 0) + free-text/"other" escape + explicit "not sure"; community-tolerant, not a closed whitelist; (b) **chip origin**: new/blank vs pulled/used (+ "owns a UV eraser?" only when chip is UV-EPROM); (c) **pot adjustments**: touched vs not-touched (+ optional free-text note). Uses `rich.prompt` behind the mock-operator seam so it stays unit-testable.
- **D-07:** Advisory, read-only proposed-disposition string derived purely from sweep verdicts — never a DB write, never the taxonomy state-machine. Shows current `support_status` (read via existing `chip_resolver`/`get_eprom` path) beside a plainly-labeled human-readable proposal. Rejected: emitting a concrete target `support_status` value.

### Claude's Discretion
- Exact dataclass/sub-object names and decomposition (`AutoCapture`, `TransportHealth`, `DbDiff`, `Provenance`, field names) — planner's call, constrained by D-01.
- `schema_version` starting value/format — recommend `"1.0"`; MUST be single-sourced and present in JSON.
- JSON representation of absent/NA fields — recommend `null` for genuinely-absent scalars, string `"not measured"` for transport-health-unavailable so human + machine renders agree.
- `transport-suspect` elevated-threshold numbers AND which specific counters are reachable — researcher/planner detail (this research resolves: none reachable today).
- DB-diff proposed-disposition exact wording/branching — planner's call within D-07's advisory/read-only constraint.

### Deferred Ideas (OUT OF SCOPE)
None from the discussion. Adjacent concerns owned elsewhere: measured VPP/VPE mV sampler = Phase 111 (leave a report slot); `@dev.command("test")` CLI surface + prompt *invocation* + terminal/`--output-dir` render = Phase 112; `--submit` flow = Phase 113; `support_status` taxonomy + N≥2 promotion + grep/AST no-auto-write lock = Phase 113/114.

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| RPT-01 | One self-contained report rendered two ways from one source object (`rich` table + fenced JSON with `schema_version`) | `_write_validation_matrix_artifact` (cli_handlers.py:1371) is the json+md dual-serialization *shape* precedent; the single-source-render pattern (§Pattern 1) makes both renders read the same `to_dict()`/field accessors. `rich>=14.0` [VERIFIED: pyproject.toml:51]. |
| RPT-02 | Auto-capture FW+board+host version, chip-ID expected-vs-actual, protocol path, per-op exact firmware error code, byte-mismatch fingerprint | Host version = `firestarter.__version__` = `"3.0.0b10"` [VERIFIED: __init__.py:1]. FW+board = `SerialCommunicator.programmer_info` (`version:board` from MSG_OK) [VERIFIED: serial_comm.py:686]. Per-op error code + fingerprint already on `StepResult.error_code`/`.fingerprint` [VERIFIED: chip_test.py:471-472]. chip-ID expected-vs-actual: §Pitfall 2. |
| RPT-04 | Provenance prompted before sweep; blank provenance ⇒ not submittable | `rich.prompt.Confirm` already imported in firmware.py:20 [VERIFIED]. `Prompt.ask`/`Confirm.ask` are the standard `rich` API. §Pattern 3 gives the injectable-seam unit-test approach. |
| RPT-05 | Embed DB-diff (`support_status` at test time + proposed change) for flag-only triage | `support_status` read via `db.get_eprom_config(name)[0].get("support_status","supported")` — the exact site chip_resolver.py:54 uses [VERIFIED]. §Pattern 4 maps verdicts → advisory string. |
| XPORT-01 | Capture COBS/CRC/retry/timeout counters; `transport-suspect` when elevated; "not measured" when unavailable | **No counters reachable today** (§Transport Counter Survey) — every field is `"not measured"`, flag never trips. This is D-03's ACCEPTED outcome, not a gap. |

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| `DiagnosticReport` dataclass + `to_dict()`/`render()` | Host (new report module) | — | Pure host-side data assembly; wraps engine results, sets no VPP, builds no wire dict (SAFE-02). Model belongs beside chip_test.py, not in serial/operator layer. |
| Auto-capture identity (FW+board+host version) | Host (report module reads captured strings) | serial_comm (source of `programmer_info`) | Host owns `__version__`; FW+board comes from the transient `programmer_info` string the operator's `comm` holds — must be threaded to the report, not re-fetched by the report itself. |
| chip-ID expected-vs-actual | Host (from `StepResult`/engine) | firmware (detected id) | Expected id is a DB field; detected id is firmware-reported via `check_eprom_id`. Report composes both from engine output. |
| Per-op error code / fingerprint | Host (report reads `StepResult`) | firmware (`response.id`) | Already captured by Phase 108 `StepResult`; report is a pure consumer. |
| Provenance prompt + `is_submittable` | Host (report module) | — | Human-only data; `rich.prompt` at the terminal tier, but the model/predicate are host data — Phase 112 owns the *invocation*. |
| Transport-health section | Host (report module) | serial_comm (would-be source) | Report reads counters IF exposed; today none are — emits `"not measured"`. Never adds counters to serial hot path (D-03). |
| DB-diff (`support_status` read + proposed string) | Host (report module reads DB) | database.py (`get_eprom_config`) | Read-only DB access; the proposed string is pure host logic over verdicts. Never a DB write (Phase 113/114 owns that). |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `rich` | `>=14.0` [VERIFIED: pyproject.toml:51] | `rich.table.Table` + `rich.console.Console` for human render; `rich.prompt.Prompt`/`Confirm` for provenance | Already a declared dependency; already used for prompts (firmware.py:20). No new dependency. |
| `dataclasses` | stdlib | `DiagnosticReport` + sub-objects | Phase 108/109 already model everything as `@dataclass` (`Fingerprint`, `Step`, `Plan`, `StepResult`, `BannerCounts`); consistency + `dataclasses.asdict` availability. |
| `json` | stdlib | `json.dumps(obj, indent=2)` for the fenced JSON block | Exact precedent: `_write_validation_matrix_artifact` (cli_handlers.py:1392) uses `json.dumps(artifact, indent=2)`. |
| `datetime` | stdlib | `generated` UTC timestamp on the report | Precedent: cli_handlers.py:1384 `datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")`. |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `unittest.mock.Mock` | stdlib | `Mock(spec=[...])` operator + prompt-function stub in unit tests | The `_mock_operator` seam already in test_chip_test.py:570; extend the same pattern to a mock prompt callable. |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `to_dict()` hand-written + `render()` reading same accessors | `dataclasses.asdict()` for JSON | `asdict()` recurses through nested dataclasses automatically (less code) BUT it serializes ALL fields verbatim — you lose control over the `"not measured"` sentinel substitution, `null`-vs-string absent-field policy, and `schema_version` injection. Recommend a **hand-written `to_dict()`** so D-02/D-03 sentinel policy is single-sourced and explicit. If `asdict()` is used for the leaf sub-objects, wrap it and post-process sentinels. |
| Single `render()` reading dataclass fields | Render table by iterating `to_dict()` output | Both satisfy "no second field list" IF the table iterates the SAME dict `to_dict()` produces. But D-01 explicitly forbids the table being "parsed back out of the JSON string" — reading the *dict* (not the JSON string) is acceptable and arguably the cleanest single-source. Recommend: `to_dict()` returns the canonical dict; `render()` consumes that dict (or shared accessors), and `json.dumps` also consumes it. One dict, two renders. |

**Installation:** No new packages. `rich>=14.0` already present.

**Version verification:**
```bash
# Host version (auto-capture source for RPT-02):
python -c "import firestarter; print(firestarter.__version__)"   # -> 3.0.0b10  [VERIFIED]
grep -n '"rich' firestarter_app/pyproject.toml                    # rich>=14.0  [VERIFIED]
```

## Package Legitimacy Audit

> This phase installs **zero** external packages. It uses only `rich` (already a declared, in-use dependency) and Python stdlib (`dataclasses`, `json`, `datetime`, `unittest.mock`). No legitimacy gate required.

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| (none — no new installs) | — | — | — | — | — | — |

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

## Transport Counter Survey (XPORT-01 / D-03 — the critical research task)

**Question:** What COBS-decode-error / CRC-failure / retry / timeout counters are actually reachable from an `EpromOperator` / `SerialCommunicator` handle during a sweep today?

**Answer: NONE are reachable. There are no transport counters in the codebase.** [VERIFIED: grep + full read of serial_comm.py, eprom_operations.py, hardware.py this session]

Evidence, per counter category:

| Counter | What exists | Reachable as a count? |
|---------|-------------|------------------------|
| **COBS decode errors** | `cobs_encode` is used for outgoing frames (serial_comm.py:190). Incoming decode is `codec.decode_id_frame` via `_decode_id_frame`. A decode failure returns `None` → the reader silently re-syncs. | **No.** No counter. The fault-injection subclass (`FaultInjectingSerialCommunicator`) is dev-only and one-shot; it counts nothing. |
| **CRC failures** | `_crc8_ccitt` computes CRC; a mismatch inside `codec.decode_id_frame` yields `None` (re-sync). | **No.** No `crc_fail_count`. The mismatch is invisible to callers — just a dropped frame. |
| **Retries** | `find_and_connect` loops over *ports* (a connection-time port probe, not a per-frame retry). The ONLY `retry_count` field in the app is a per-cell field in the `validate-family` harness, and it is **hardcoded `0`** (cli_handlers.py:1353, 1366, 1418). | **No.** No transport-level retry counter exists; the harness `retry_count` is a placeholder, not a real signal. |
| **Timeouts** | `_read_and_parse_lines` uses a wall-clock `timeout` window; on expiry `get_response` raises `SerialTimeoutError`. Truncated frames log `logger.warning(... re-syncing)` (serial_comm.py:358, 373). | **No.** Timeouts are raised as exceptions or logged as warnings, never *counted* or accumulated on the communicator. |

**Design consequence for Phase 110:**
- The `TransportHealth` sub-object's fields (cobs_errors, crc_failures, retries, timeouts) all render the explicit `"not measured"` sentinel this phase. This is D-03's **ACCEPTED outcome**, not a gap to paper over.
- `transport-suspect` is a computed boolean that can ONLY be `True` when at least one counter is *present and elevated*. Since no counter is ever present today, the flag is **always `False`** now — and that is correct (never fabricate suspicion from absent data; mirrors Phase 108's `indeterminate`).
- **Do NOT** add counters to `serial_comm.py`. The `_read_and_parse_lines` body is ring-fenced (GATE-1.8d, serial_comm.py:279-289) as v1.9 RCA baseline territory — touching it is explicitly forbidden and would also violate the milestone's zero-firmware-touch / SAFE-02 posture.
- **Recommended API shape:** make `TransportHealth` accept an optional counters-source that defaults to "nothing available" so that IF a future phase adds real counters (behind the ring-fence, elsewhere), the report picks them up without a redesign. The threshold constants for `transport-suspect` should be module constants (like chip_test.py's `_FF_RATIO_THRESHOLD`) — declared but effectively dormant.

## Architecture Patterns

### System Architecture Diagram

```
 Phase 112 dev-test handler (NOT this phase)
        │  invokes provenance prompt (before sweep)  ┌─────────────────────────┐
        │────────────────────────────────────────────▶│  prompt_provenance()    │  ◀── rich.prompt
        │                                              │  (injectable seam)       │      Prompt.ask/
        │  ◀───────────── Provenance ──────────────────│  returns Provenance      │      Confirm.ask
        │                                              └─────────────────────────┘
        │  runs sweep: derive_plan() + run_plan()  [Phase 108/109, existing]
        │       │
        │       ├─▶ Plan (steps + locked_destructive)
        │       ├─▶ list[StepResult]  (op/verdict/error_code/fingerprint/divergence)
        │       ├─▶ BannerCounts      (n_ran / m_applicable / locked_steps)
        │       └─▶ programmer_info   ("version:board" from comm, threaded in)
        │
        ▼   assemble
 ┌──────────────────────────────────────────────────────────────────────┐
 │  DiagnosticReport  (@dataclass — THIS phase)                            │
 │    ├─ AutoCapture   (host_version, fw_version, board, protocol path,    │
 │    │                 chip-id expected/actual)                           │
 │    ├─ Provenance    (shield_rev, chip_origin, pot_adjust, is_submittable)│
 │    ├─ TransportHealth (all "not measured" today; transport_suspect=False)│
 │    ├─ DbDiff        (current support_status  +  proposed disposition str)│
 │    ├─ Plan / list[StepResult] / BannerCounts   (composed from Phase 108/109)│
 │    ├─ vpp_vpe slot  (None — Phase 111 fills)                            │
 │    └─ SCHEMA_VERSION constant                                           │
 │                                                                          │
 │   one canonical to_dict() ───┬──▶ json.dumps(indent=2) → ```json block   │
 │                              └──▶ render() → rich.Table  (SAME accessors) │
 └──────────────────────────────────────────────────────────────────────┘
        │                                    (Phase 112 renders to terminal / --output-dir)
        ▼
   Phase 113 gsd-inbox parses fenced JSON via schema_version (read-only)
```

### Recommended Project Structure
```
firestarter_app/firestarter/
├── chip_test.py            # Phase 108/109 engine — UNCHANGED (report is a NEW consumer)
├── diagnostic_report.py    # NEW: DiagnosticReport + sub-dataclasses + prompt_provenance + is_submittable
                            #   (co-located with chip_test.py; pure host data assembly)
firestarter_app/tests/
└── test_diagnostic_report.py  # NEW: bench-free tests via Mock operator + Mock prompt seam
```
Rationale: a dedicated `diagnostic_report.py` keeps SAFE-02 clean (report module contains no VPP-set / raw-command / `--force` — the Phase-109 SAFE-03 AST checker scans Phase-112's handler that renders it). Do NOT put render logic in chip_test.py (it is documented as "emits no print/render/CLI output", chip_test.py:884).

### Pattern 1: Single-source dual-render (D-01, RPT-01)
**What:** One dataclass; one canonical `to_dict()`; the `rich` table reads the SAME dict/accessors, never a second field list, never re-parsing the JSON string.
**When to use:** Whenever a report must be both machine-parseable and human-readable and the two must never drift.
**Example:**
```python
# Source: pattern derived from firestarter cli_handlers.py:1371-1418 (json+md dual-serialization)
#         + rich official docs (Table API). Adapted for single-source.
import json
from dataclasses import dataclass, field
from rich.table import Table
from rich.console import Console

SCHEMA_VERSION = "1.0"          # D-02: single source of truth
NOT_MEASURED = "not measured"   # D-03: honest sentinel

@dataclass
class DiagnosticReport:
    # ... composed sub-objects (AutoCapture, Provenance, TransportHealth, DbDiff),
    #     plan, results, banner, vpp_vpe slot ...

    def to_dict(self) -> dict:
        """CANONICAL serializable mapping. Both renders read from here (or shared
        accessors). schema_version baked in once; absent scalars -> None; the
        transport section substitutes NOT_MEASURED for any unavailable counter."""
        return {
            "schema_version": SCHEMA_VERSION,
            "generated": self._utc_now(),
            "auto_capture": self._auto_capture_dict(),   # host/fw/board/version/ids/protocol
            "provenance": self._provenance_dict(),
            "transport_health": self._transport_dict(),  # all NOT_MEASURED today
            "db_diff": self._db_diff_dict(),
            "steps": [self._step_dict(s) for s in self.results],
            "banner": {"n_ran": self.banner.n_ran, "m_applicable": self.banner.m_applicable},
            "vpp_vpe_mv": self.vpp_vpe_mv,                # None -> Phase 111 fills the slot
        }

    def render(self, console: Console | None = None) -> Table:
        """Human table built from the SAME dict to_dict() produces — never a
        second hand-maintained field list, never re-parsed from json.dumps output."""
        d = self.to_dict()
        table = Table(title=f"dev test — {d['auto_capture']['chip']}")
        table.add_column("Field"); table.add_column("Value")
        for op_row in d["steps"]:
            table.add_row(op_row["op"], f"{op_row['verdict']} (err={op_row['error_code']})")
        # ... identity / provenance / transport / db_diff rows all read `d` ...
        return table

    def to_json_block(self) -> str:
        """Fenced ```json block for the self-contained issue body."""
        return "```json\n" + json.dumps(self.to_dict(), indent=2) + "\n```"
```
**Load-bearing:** `render()` reads `self.to_dict()` (or a shared `_fields()` accessor). This is the "add a field once, both renders pick it up" contract. Never build a `rows = [...]` list independent of `to_dict()`.

### Pattern 2: Injectable provenance prompt seam (D-04/D-06, RPT-04)
**What:** A `prompt_provenance(prompt=Prompt.ask, confirm=Confirm.ask)` function whose I/O callables are parameters, so tests inject a mock and never touch a real terminal.
**When to use:** Any interactive component that must stay unit-testable behind the mock-operator seam (mirrors the `Mock(spec=[...])` operator pattern).
**Example:**
```python
# Source: rich.prompt API (Prompt.ask / Confirm.ask) — precedent firmware.py:20,613
from rich.prompt import Prompt, Confirm

SHIELD_REV_CHOICES = ["Rev 2.2", "Rev 2.0", "modified Rev 0", "other", "not sure"]

def prompt_provenance(is_uv: bool, *, ask=Prompt.ask, confirm=Confirm.ask) -> "Provenance":
    """Collect human-only provenance BEFORE the sweep. `ask`/`confirm` are
    injectable so unit tests pass stubs (no terminal). 'not sure' is a FILLED,
    submittable answer (D-05); only a truly-empty field fails is_submittable."""
    shield = ask("Shield revision", choices=SHIELD_REV_CHOICES, default="not sure")
    if shield == "other":
        shield = ask("Describe shield revision") or ""     # free-text escape (D-06)
    chip_origin = ask("Chip origin", choices=["new/blank", "pulled/used"])
    owns_eraser = confirm("Do you own a UV eraser?") if is_uv else None   # UV-only (D-06)
    pot_touched = confirm("Did you adjust the voltage pot?")
    pot_note = ask("Pot note (optional)", default="") if pot_touched else ""
    return Provenance(shield_rev=shield, chip_origin=chip_origin,
                      owns_eraser=owns_eraser, pot_touched=pot_touched, pot_note=pot_note)
```
`is_submittable` (D-05): every prompted field must be non-empty; `"not sure"` counts as filled. Only `None`/`""` on a required field fails.
```python
def is_submittable(p: "Provenance") -> bool:
    # 'not sure' is a valid filled answer (D-05); blank/None is what fails.
    return bool(p.shield_rev) and bool(p.chip_origin) and p.pot_touched is not None
```

### Pattern 3: Read-only DB-diff (D-07, RPT-05)
**What:** Read current `support_status` at test time; compute an advisory proposed-disposition STRING from sweep verdicts. Never write.
**Example:**
```python
# Source: chip_resolver.py:54 (the exact support_status read site) + chip_test.py verdict vocab
def build_db_diff(name: str, db, results: list) -> "DbDiff":
    raw_config, _ = db.get_eprom_config(name)                 # read-only DB access
    current = (raw_config or {}).get("support_status", "supported")
    verdicts = {r.verdict for r in results}
    if "BAD" in verdicts:
        proposed = "suggests: community-fail signal (advisory — human triage required)"
    elif verdicts <= {"OK", "NA", "SKIPPED"} and "OK" in verdicts:
        proposed = "suggests: candidate for community-reported (advisory)"
    elif "marginal" in verdicts or any(getattr(r, "fingerprint", None) and
             r.fingerprint.classification == "indeterminate" for r in results):
        proposed = "inconclusive — needs N>=2 agreement (advisory)"
    else:
        proposed = "no change suggested (advisory)"
    return DbDiff(current_support_status=current, proposed_disposition=proposed)
```
**Load-bearing:** `proposed_disposition` is DESCRIPTIVE TEXT, never a concrete `support_status` value and never written back. The `community-reported/-confirmed/-fail` taxonomy + N≥2 rule + no-auto-write lock are Phase 113/114.

### Anti-Patterns to Avoid
- **Two parallel field lists** (a `rows=[...]` for the table AND an independent dict for JSON): the exact drift RPT-01 forbids. The table MUST read `to_dict()`/shared accessors.
- **`dataclasses.asdict()` as the whole `to_dict()`:** it can't inject `schema_version` or substitute the `"not measured"` sentinel without post-processing — you'd re-introduce sentinel logic in a second place. Hand-write `to_dict()` (or wrap `asdict` per leaf + post-process).
- **Fabricating a transport counter of `0`** when nothing is measured: XPORT-01 explicitly forbids the false zero. Use `"not measured"`.
- **Auto-deriving shield revision from `hw_revision`:** forbidden by D-05 (the byte cannot distinguish Rev 2.2 / 2.0 / modified Rev 0 — the Bug A lesson).
- **Adding counters to `serial_comm.py` / `_read_and_parse_lines`:** ring-fenced GATE-1.8d territory; violates SAFE-02 and D-03.
- **Putting render/print logic in chip_test.py:** it is documented DATA-ONLY (chip_test.py:884). Rendering lives in the report module / Phase 112.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Human table rendering | Manual column alignment / ASCII tables | `rich.table.Table` | Already a dep; used across the app; handles wrapping/alignment. |
| JSON pretty-print | Custom serializer | `json.dumps(d, indent=2)` | Exact precedent cli_handlers.py:1392. |
| Byte-mismatch classification | New fingerprint logic | Phase 108 `Fingerprint` on `StepResult.fingerprint` | Already computed; report is a consumer (chip_test.py:127). |
| N-of-M banner counting | Recount steps | Phase 109 `count_applicable()` → `BannerCounts` | Already single-derivation-safe (chip_test.py:925). |
| support_status lookup | New DB parse | `db.get_eprom_config(name)[0].get("support_status","supported")` | Identical site chip_resolver.py:54 uses. |
| Interactive prompts | `input()` + validation | `rich.prompt.Prompt.ask`/`Confirm.ask` | Choice validation, defaults, styling; precedent firmware.py:20. |
| UTC timestamp | strftime by hand each time | `datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")` | Exact precedent cli_handlers.py:1384. |

**Key insight:** This phase is almost entirely *composition* of already-built, already-tested Phase 108/109 objects plus thin `rich`/`json` rendering. The only genuinely new logic is the provenance prompt seam, `is_submittable`, and the advisory DB-diff string — all pure and unit-testable.

## Common Pitfalls

### Pitfall 1: FW+board identity (`version:board`) is transient and per-operation
**What goes wrong:** The report can't "just call" for `version:board` — `SerialCommunicator.programmer_info` lives on the `comm` object that `EpromOperator` creates and tears down (`self.comm = None`) per operation (eprom_operations.py:268, 386-388). By the time the report assembles, the comm may be gone.
**Why it happens:** Each op opens/closes its own connection via `find_and_connect`; `programmer_info` is the OK message captured at connect (serial_comm.py:686). It is not persisted anywhere durable.
**How to avoid:** The report must RECEIVE the identity string as captured input (threaded from the sweep loop / Phase 112 handler), not fetch it. Design `AutoCapture` to accept `fw_board_identity: str | None` (None ⇒ render `null`/"unknown"). Do NOT make the report open a serial connection — that would violate the bench-free / SAFE-02 posture. **This is a real cross-phase seam: the planner should note that Phase 112's handler must capture `operator.comm.programmer_info` (or equivalent) and pass it in.**
**Warning signs:** A design that has `DiagnosticReport` importing `SerialCommunicator` or `HardwareManager`.

### Pitfall 2: chip-ID "expected vs actual" is asymmetric in the existing operator
**What goes wrong:** `check_eprom_id` returns `(is_ok, detected_id)` where on SUCCESS `detected_id` is actually the *expected* DB `chip-id` (`cmd_data.get("chip-id")`, eprom_operations.py:1717), and only on FAILURE does it return the truly firmware-detected id (extracted from the error message, eprom_operations.py:1721). So "expected vs actual" both-distinct values only exist on a mismatch.
**Why it happens:** The firmware returns OK without echoing the id on success; the host substitutes the expected value.
**How to avoid:** For RPT-02, source `expected` from the DB (`eprom_data["chip-id"]`) independently, and `actual` from the id `StepResult`. On OK, `actual == expected` (report both, equal); on BAD, `_dispatch_id` already records the mismatch reason string (chip_test.py:728) — the report can surface that reason verbatim rather than trying to re-derive two numbers.
**Warning signs:** Report showing `expected == actual` on a passing chip and treating that as suspicious.

### Pitfall 3: `dataclasses.asdict` on nested Phase-108 objects loses sentinel control
**What goes wrong:** `asdict(report)` recurses into `Fingerprint`, `Step`, `StepResult` and dumps every field — including `evidence` dicts and `None`s — with no place to inject `schema_version` or the `"not measured"` substitution, so D-02/D-03 policy ends up duplicated or lost.
**How to avoid:** Hand-write `to_dict()` (per Pattern 1). If you use `asdict` for leaf sub-objects, wrap and post-process. Keep `NOT_MEASURED` substitution in ONE place.
**Warning signs:** Two functions that both know the string `"not measured"`.

### Pitfall 4: Provenance prompts that block unit tests
**What goes wrong:** Calling `Prompt.ask(...)` directly at module/function top level makes the component untestable without a TTY, breaking the CI gate (`pytest --cov-fail-under=70`).
**How to avoid:** Inject the `ask`/`confirm` callables (Pattern 2). Tests pass `ask=Mock(side_effect=[...])`. Mirrors the `_mock_operator` seam (test_chip_test.py:570).
**Warning signs:** A test that would hang waiting for stdin.

## Code Examples

### Composing the report from existing engine output
```python
# Source: chip_test.py public API (derive_plan/run_plan/count_applicable), VERIFIED this session
from firestarter.chip_test import derive_plan, run_plan, count_applicable

plan = derive_plan(name, db, destructive=destructive)   # Plan + locked_destructive
results = run_plan(plan, operator, db, runs=2)           # list[StepResult] (error_code+fingerprint)
banner = count_applicable(plan, results)                 # BannerCounts (n_ran/m_applicable)
report = DiagnosticReport(
    auto_capture=AutoCapture(host_version=firestarter.__version__,
                             fw_board_identity=captured_identity,   # threaded in — Pitfall 1
                             chip=name, protocol=prog.get("algorithm")),
    provenance=provenance,          # collected before the sweep (Phase 112 invokes)
    transport=TransportHealth(),    # all NOT_MEASURED today (Transport Survey)
    db_diff=build_db_diff(name, db, results),
    plan=plan, results=results, banner=banner, vpp_vpe_mv=None,     # Phase 111 slot
)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Fixed test pattern (all-0x55) blind to address faults | Address-derived XOR-fold pattern + 4-bucket fingerprint | Phase 108 (v1.21) | Report's fingerprint field is already meaningful; no new classification logic needed. |
| Fail-fast sweep aborts on first BAD | Non-fatal per-step `run_plan` (W29C040 lesson) | Phase 108 | Report can show partial results; every step has a verdict. |
| `EpromOperationError` discarded `response.id` | `error_code` seam preserves it | Phase 108 (RPT-03, Complete) | RPT-02 per-op exact code is already captured — report just reads it. |

**Deprecated/outdated:**
- FW identity string used to carry buffer size as a 3rd colon-field; removed in Phase 55 (CAP-01). Identity is now `"<version>:<board>"` only (serial_comm.py:656-659). The report parses exactly two colon fields.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `programmer_info` string format is `"<version>:<board>"` (two colon-separated fields post-CAP-01) | Pitfall 1 / RPT-02 | Low. If a board omits the colon, parse defensively (whole string = version, board = None). The report should not assume a strict split. Verified the CAP-01 removal comment (serial_comm.py:656-659) but did not observe a live `programmer_info` string this session (bench-free). |
| A2 | The advisory DB-diff verdict→string mapping wording (D-07) | Pattern 3 | Low. Wording is explicitly Claude's discretion; only the read-only/never-write constraint is locked. Planner refines wording. |
| A3 | `transport-suspect` threshold constants are dormant (never trip today) | Transport Survey | None — this is the verified state (no counters exist). If a future phase adds counters, thresholds activate. |

## Open Questions

1. **How does Phase 112 thread `version:board` into the report?**
   - What we know: `programmer_info` is on the transient per-op `comm`; the report must receive it, not fetch it (Pitfall 1).
   - What's unclear: whether Phase 112 captures it once at sweep start (a dedicated fw/hw probe) or opportunistically off the first operation's `comm`.
   - Recommendation: Phase 110 designs `AutoCapture.fw_board_identity: str | None` accepting a captured string (defaults to `None` → `null`/"unknown"). Phase 112 owns the capture mechanism. This keeps Phase 110 bench-free and testable.

2. **Should the report carry the Phase-109 `locked_destructive` list explicitly for the banner "pass --destructive for the rest" message?**
   - What we know: `BannerCounts.locked_steps` already carries `plan.locked_destructive` verbatim (chip_test.py:922).
   - Recommendation: compose `BannerCounts` into the report; the "only N of M ran" banner rendering is Phase 112, but the DATA (n_ran/m_applicable/locked_steps) belongs in the report's `to_dict()`.

## Environment Availability

> This phase is host-only, bench-free, code-only. No external tools/services/hardware are required.

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `rich` | table + prompt render | ✓ | `>=14.0` [VERIFIED: pyproject.toml:51] | — |
| Python stdlib (`dataclasses`,`json`,`datetime`,`unittest.mock`) | model + tests | ✓ | py3.9+ | — |
| `pytest` + `pytest-cov` | CI gate (`--cov-fail-under=70`) | ✓ | (`.[test]`) | — |

**Missing dependencies with no fallback:** none
**Missing dependencies with fallback:** none

## Validation Architecture

> `nyquist_validation` is enabled (not `false` in config). This section maps each requirement to its automated validation.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | `pytest` + `pytest-cov` (via `pip install -e '.[test]'`) |
| Config file | `firestarter_app/pyproject.toml` (`[tool.pytest]` + CI `--cov-fail-under=70`) |
| Quick run command | `cd firestarter_app && python -m pytest tests/test_diagnostic_report.py -x` |
| Full suite command | `cd firestarter_app && python -m pytest -q` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| RPT-01 | `to_dict()` and `render()` derive from the SAME source; adding a field appears in both; JSON has `schema_version` | unit | `pytest tests/test_diagnostic_report.py::test_dual_render_single_source -x` | ❌ Wave 0 |
| RPT-01 | fenced JSON block round-trips via `json.loads` and contains `schema_version` | unit | `pytest tests/test_diagnostic_report.py::test_json_block_parseable -x` | ❌ Wave 0 |
| RPT-02 | auto-capture surfaces host `__version__`, threaded `version:board`, chip-id expected/actual, protocol, per-op `error_code`, fingerprint | unit (Mock operator) | `pytest tests/test_diagnostic_report.py::test_auto_capture_fields -x` | ❌ Wave 0 |
| RPT-04 | `prompt_provenance` collects all fields via injected `ask`/`confirm`; "not sure" is submittable; blank field ⇒ `is_submittable False` | unit (Mock prompt) | `pytest tests/test_diagnostic_report.py::test_provenance_submittable -x` | ❌ Wave 0 |
| RPT-04 | shield revision is NEVER auto-derived from `hw_revision` (assert the report/prompt never reads that byte) | unit / structural | `pytest tests/test_diagnostic_report.py::test_shield_rev_not_autoderived -x` | ❌ Wave 0 |
| RPT-05 | DB-diff reads `support_status` read-only; advisory string maps from verdicts; asserts NO DB write (Mock DB `set_*`/write never called) | unit (Mock DB) | `pytest tests/test_diagnostic_report.py::test_db_diff_readonly -x` | ❌ Wave 0 |
| XPORT-01 | every transport counter renders `"not measured"` (never `0`); `transport_suspect` is `False` when counters absent | unit | `pytest tests/test_diagnostic_report.py::test_transport_not_measured -x` | ❌ Wave 0 |

### Honest-fallback contracts (explicit test assertions)
- **"not measured"** (XPORT-01): assert `report.to_dict()["transport_health"][*] == "not measured"` and NOT `0` for every counter; assert `transport_suspect is False`.
- **"not sure"** (RPT-04/D-05): assert `is_submittable(Provenance(shield_rev="not sure", ...)) is True`; assert `is_submittable(Provenance(shield_rev="", ...)) is False`.
- **read-only-never-writes-DB** (RPT-05): pass a `Mock(spec=["get_eprom","get_eprom_config","convert_to_programmer"])` DB (spec has NO write method) — any write attempt raises `AttributeError`, proving read-only by construction. Additionally assert the module contains no `support_status =` assignment / no `.write`/`set_*` call (structural, mirrors chip_test.py's no-resolve-chip assertion test_chip_test.py:308).

### Sampling Rate
- **Per task commit:** `pytest tests/test_diagnostic_report.py -x` (< 5s, no serial, no bench)
- **Per wave merge:** `pytest -q` full suite
- **Phase gate:** full suite green + `ruff check` + `ruff format --check` + `mypy` (report module should be added to the strict-typed set per CLAUDE.md tooling gate) before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `tests/test_diagnostic_report.py` — covers RPT-01/02/04/05, XPORT-01 (new file)
- [ ] Reuse existing fixtures: `EpromDatabase(skip_local_override=True)` + `_mock_operator` pattern from `test_chip_test.py` (no new conftest needed)
- [ ] Framework install (if toolchain wiped): `pip install -e '.[test]'`

## Project Constraints (from CLAUDE.md)

- **Constants duplicated Python↔C++:** N/A this phase — host-only, no firmware change, touches no `constants.py` flag bits.
- **Tooling gate (v1.8):** `ruff check` + `ruff format --check` + `mypy` (strict on a named module set) + `pytest --cov-fail-under=70`, enforced by `.github/workflows/ci.yml`. Recommend adding `diagnostic_report.py` to the mypy-strict module set (it is new, pure, and type-clean-friendly).
- **`skip_local_override` seam:** all DB-touching unit tests MUST use `EpromDatabase(skip_local_override=True)` (no `~/.firestarter`, no serial).
- **SAFE-02 / orchestrator-only (milestone invariant):** report module sets no VPP, builds no wire dict, passes no `--force`, adds zero firmware dispatch entries. Keep the module import-light and free of `SerialCommunicator`/`HardwareManager` imports (Pitfall 1).
- **Devcontainer Python note:** validate against py3.9/3.11 target semantics (CI runs those), not just the devcontainer's 3.12 — avoid 3.10+-only syntax if the module joins the strict set.

## Sources

### Primary (HIGH confidence — verified in codebase this session)
- `firestarter_app/firestarter/chip_test.py` — Phase 108/109 engine: `Fingerprint`(127), `Step`/`Plan`+`locked_destructive`(281-315), `StepResult`(453-475), `derive_plan`(318), `run_plan`(501), `count_applicable`/`BannerCounts`(908-949), DATA-ONLY note (884)
- `firestarter_app/firestarter/serial_comm.py` — `programmer_info` set at connect (686), `version:board` post-CAP-01 (656-659), NO transport counters, ring-fenced `_read_and_parse_lines` (279-289), re-sync warnings (358,373)
- `firestarter_app/firestarter/cli_handlers.py` — `_write_artifact` json+md dual-serialization (1373-1420), `datetime` UTC pattern (1386), hardcoded `retry_count:0` (1353,1366,1418), `dev_validate_family` seam (1452-1510)
- `firestarter_app/firestarter/chip_resolver.py` — `support_status` read site (54), guard raises for non-supported (16-77)
- `firestarter_app/firestarter/database.py` — `get_eprom_config`(465), `get_eprom`(506), `convert_to_programmer`(535)
- `firestarter_app/firestarter/eprom_operations.py` — `EpromOperator.__init__`/per-op `comm` (257-388), `check_eprom_id` asymmetric expected-vs-actual (1695-1731)
- `firestarter_app/firestarter/hardware.py` — `_execute_simple_command`/`programmer_info` (39-68), `get_hardware_revision` (80)
- `firestarter_app/firestarter/firmware.py` — `rich.prompt.Confirm` import (20), usage (613)
- `firestarter_app/firestarter/__init__.py` — `__version__ = "3.0.0b10"` (1)
- `firestarter_app/pyproject.toml` — `rich>=14.0` (51), mypy/ruff/cov gate (112)
- `firestarter_app/tests/test_chip_test.py` — `_mock_operator` seam (570), `EpromDatabase(skip_local_override=True)` (282), no-resolve-chip structural assertion (308)
- `.planning/notes/dev-test-design-decisions.md` — two-tier diagnostic contract, provenance-before-sweep rationale
- `.planning/REQUIREMENTS.md` — RPT-01/02/04/05, XPORT-01, RPT-03 (34-46)

### Secondary (MEDIUM confidence)
- `rich` `Table`/`Prompt`/`Confirm` public API (training knowledge of a stable, in-use dependency; not re-fetched from docs this session — the API surface used is minimal and already exercised in firmware.py)

### Tertiary (LOW confidence)
- None.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — every library verified present/in-use; zero new packages.
- Architecture (single-source dual-render, injectable prompt seam, read-only DB-diff): HIGH — patterns derived directly from existing verified precedents (`_write_artifact`, `_mock_operator`, chip_resolver read site).
- Transport survey: HIGH — exhaustively verified NO counters exist; `"not measured"` is the correct + accepted state.
- Pitfalls: HIGH — each grounded in a specific verified source line (transient `comm`, asymmetric `check_eprom_id`).

**Research date:** 2026-07-02
**Valid until:** ~2026-08-01 (stable host codebase; re-verify `__version__` and `programmer_info` format if a serial/CAP change lands)
