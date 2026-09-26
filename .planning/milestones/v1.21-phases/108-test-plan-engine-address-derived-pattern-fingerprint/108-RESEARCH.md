# Phase 108: Test-Plan Engine + Address-Derived Pattern + Fingerprint - Research

**Researched:** 2026-07-02
**Domain:** Host-side Python orchestration layer over existing `EpromOperator` service methods (chip capability sweep engine — bench-free, unit-testable)
**Confidence:** HIGH (every claim grounded in first-party source read this session)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01 (PATT-01):** Address-derived pattern generator is an **XOR-fold of the address bytes**: `byte = (addr ^ (addr >> 8) ^ (addr >> 16) ^ (addr >> 24)) & 0xFF`. Deterministic, reproducible, no RNG state. Every address line contributes so a stuck/shorted/aliased high line (A8+) produces systematically wrong bytes at aliased addresses. Rejected: low-byte-only pattern (blind above A7); address-keyed LFSR/PRNG (harder to map a flip back to an address line, overkill).
- **D-02 (PATT-01):** Pattern is preceded by a **cheap all-0x00 / all-0xFF pre-pass**. Generator MUST be **region-parameterized** (`start`/`length`) — it does NOT assume a full-chip write, because Phase 109 caps the UV write to a small high-address window. Do not bake full-chip assumptions in.
- **D-03 (PATT-02):** Classifier emits **four** outcomes: `blank/contact`, `address-line`, `transport`, and an explicit **`indeterminate`** bucket that fires when no signature dominates. Never force an ambiguous distribution into a confident label.
- **D-04 (PATT-02):** Signature direction: all/near-all `0xFF` → blank/contact; mismatches clustered in high address bits / power-of-two aliasing → address-line; scattered/non-repeatable → transport. **Reuse `consistency_check_eprom`'s divergence math** for the transport/scatter signal — do NOT write a parallel divergence implementation. Exact numeric thresholds are a planner/researcher detail; the honest-`indeterminate` fallback (D-03) is the locked part.
- **D-05 (SWEEP-04):** Default **N=2**, overridable via a `runs` parameter that **mirrors `consistency_check_eprom(runs=…)`** — minimum 2, reject `<2` BEFORE any state-machine call (same guard as the existing method). Keep the escalate-to-more-runs option for flaky boards (uno328pb).
- **D-06 (SWEEP-04):** `marginal` applies to **destructive/verify steps only** — not every repeated step. Read-step disagreement is measured as **byte-level divergence** (reuse the consistency divergence math), not a verdict flip.
- **D-07 (RPT-03):** Add an **optional `__init__` kwarg** to `EpromOperationError`: `EpromOperationError(*args, error_code=None)` storing `self.error_code`. Existing `raise EpromOperationError("…")` sites keep working untouched (kwarg defaults `None`); new raise sites pass the firmware `response.id` byte. Rejected: set-attribute-after-construction.

### Claude's Discretion
- Result/plan object shapes (`derive_plan()` return type, per-step result records) — constrained by verdict vocabulary (`OK`/`BAD`/`NA`/`SKIPPED`, plus `marginal`) and the four fingerprint outcomes.
- Exact numeric thresholds inside the fingerprint classifier (D-04).
- Module layout / helper decomposition within `chip_test.py`.

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope. Downstream phases own adjacent concerns: `--destructive` gate + UV small-region cap + orchestrator-only CI = **Phase 109**; report model + provenance prompts = **Phase 110**; measured-voltage sampler = **Phase 111**; CLI handler = **Phase 112**; submission = **Phase 113**; disposition/no-auto-graduate lock = **Phase 114**.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| SWEEP-01 | Derive per-chip plan from `protocol`/`electrical-type`/`FLAG_CAN_ERASE`, bypass `resolve_chip` guard for derivation only, never re-invoke `classify()` | § Plan-Derivation vs Execution Split — exact `get_eprom`/`convert_to_programmer` call sequence + protocol→ops table |
| SWEEP-02 | Each op runs as independent, non-fatal step with `OK`/`BAD`/`NA`/`SKIPPED` verdict; one failure never aborts the rest | § Non-Fatal Step Execution — per-op try/except boundary; W29C040 lesson |
| SWEEP-03 | id-check first; chip-ID mismatch hard-gates destructive steps (chip pristine) while recording id/read findings | § Id-First Gating — `check_eprom_id` returns `Tuple[bool, Optional[int]]`; gate flag threaded into plan execution |
| SWEEP-04 | Destructive/verify steps run N≥2; disagreement → `marginal` | § N≥2 / Marginal Policy — mirror `runs<2` guard; marginal derivation |
| PATT-01 | Address-derived pattern (XOR-fold) + all-0x00/all-0xFF pre-pass; region-parameterized | § Address-Derived Pattern Generator — exact function shape |
| PATT-02 | Byte-mismatch fingerprint classifier (4 buckets) coupled to the pattern | § Fingerprint Classifier — signature math + threshold candidates + return shape |
| RPT-03 | `EpromOperationError.error_code` seam preserving firmware `response.id` | § error_code Seam — single chokepoint `_raise_for_error_response` (eprom_operations.py:70) |
</phase_requirements>

## Summary

Phase 108 builds `firestarter/chip_test.py` — a NEW **orchestration engine** that composes the existing `EpromOperator` per-op service methods (`check_eprom_id`, `read_eprom`, `write_eprom`, `verify_eprom`, `erase_eprom`, `check_eprom_blank`) plus reuses `consistency_check_eprom`'s SHA-256 divergence math. It adds **zero new firmware dispatch, zero VPP-set calls, zero new third-party deps**. Architecturally it is a sibling of the shipped `dev validate-family` (which already demonstrates the exact "compose-don't-reimplement + `EpromDatabase(skip_local_override=True)` + `Mock(spec=EpromOperator)`" test seam this phase copies). The engine is fully unit-testable without a bench.

Five plannable unknowns were investigated against first-party source (`eprom_operations.py`, `database.py`, `chip_resolver.py`, `exceptions.py`, `cli_handlers.py`, `frame_parser.py`) and resolved with HIGH confidence:

1. **Plan derivation** reads the DB via `db.get_eprom(name)` → `db.convert_to_programmer(full)` — this path **structurally bypasses** the `resolve_chip` support-status guard (the guard lives only inside `resolve_chip`, which the derivation never calls). Op support is a pure function of the `algorithm` (protocol) int, `electrical-type`, and `FLAG_CAN_ERASE` bit — no runtime `classify()`. **Execution** of each op then routes through `resolve_chip(name, db)` (the guard-honoring path) exactly as `dev_validate_family` does at cli_handlers.py:1566.
2. **error_code seam** has a **single chokepoint**: `_raise_for_error_response(response, message)` at `eprom_operations.py:70`. It already reads `response.id` to dispatch `ProtocolNotImplementedError` vs `EpromOperationError` — passing `error_code=response.id` on the `EpromOperationError` raise is a one-line change plus the `__init__` kwarg.
3. **N≥2 / marginal** mirrors the `runs < 2` reject guard (`eprom_operations.py:703`) and the SHA-256 divergence verdict pattern (`eprom_operations.py:818`).
4. **Fingerprint classifier** reuses the exact byte-diff-offset math already present in `consistency_check_eprom` (`eprom_operations.py:842-863`): compute mismatch offsets, `pct = 100*len(diffs)/cmp_len`, then classify by *where* the offsets cluster (high-address / power-of-two aliasing) and *what* the read-back bytes are (all-0xFF).
5. **Unit-test seam** is `make_app_context()` in `tests/test_validate_family_cmd.py` — `EpromDatabase(skip_local_override=True)` + `Mock(spec=EpromOperator)`; and the operator-level monkeypatch of `_operation_context` + `_run_state_machine` from `tests/test_consistency_check.py`.

**Primary recommendation:** Build `chip_test.py` as three cohesive units — (a) `derive_plan(name, db, *, destructive=False)` → ordered list of step descriptors keyed off the protocol→ops table below; (b) a non-fatal `run_step(...)` executor that catches per-step exceptions and maps to `OK`/`BAD`/`NA`/`SKIPPED`/`marginal`; (c) pure functions `address_fold_byte(addr)`, `generate_pattern(start, length)`, and `classify_fingerprint(expected, actual)`. Add the `error_code` kwarg first (foundational sub-step). Keep every op call routed through the existing operator methods — the engine sets no VPP and builds no wire dicts.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Plan derivation (protocol → op list) | Host / DB-read (`database.py` via new `chip_test.py`) | — | Pure function of frozen DB fields; no firmware, no VPP |
| Address-derived pattern generation | Host / pure-compute (`chip_test.py`) | — | Deterministic byte-from-address; no I/O |
| Fingerprint classification | Host / pure-compute (`chip_test.py`) | — | Statistics over host-side expected-vs-actual byte arrays |
| Per-op execution (id/read/write/verify/erase/blank) | Host service layer (`EpromOperator`) | Firmware (existing dispatch) | Engine composes existing methods; firmware unchanged |
| Chip-ID gating | Host orchestration (`chip_test.py`) | Firmware id check | Gate decision is host-side; the id read is the existing `check_eprom_id` |
| error_code preservation | Host (`_raise_for_error_response`, `EpromOperationError`) | Firmware (emits `response.id`) | `.id` already crosses the wire; host just stops discarding it |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| stdlib `hashlib` | (stdlib) | SHA-256 per-run divergence (mirror `consistency_check_eprom`) | Already the divergence primitive in-repo |
| stdlib `dataclasses` / `typing` | (stdlib) | Step/plan/result record shapes | Matches `AppContext` DI dataclass + `Response` namedtuple precedent |
| existing `firestarter.eprom_operations.EpromOperator` | in-repo | The six per-op service methods the steps call | Compose-don't-reimplement (validate-family precedent) |
| existing `firestarter.database.EpromDatabase` | in-repo | `get_eprom` / `convert_to_programmer` for plan derivation | The guard-bypassing derivation path |
| existing `firestarter.chip_resolver.resolve_chip` | in-repo | Guard-honoring path for op **execution** | Keeps support-status guard authoritative for real hardware ops |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| stdlib `contextlib` | (stdlib) | test monkeypatch of `_operation_context` | Unit tests only (test_consistency_check.py pattern) |
| `unittest.mock.Mock(spec=EpromOperator)` | (stdlib) | mock operator in CLI-level tests | Unit tests only (test_validate_family_cmd.py pattern) |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Reuse `consistency_check_eprom` divergence math | New parallel divergence impl | D-04 explicitly forbids this; duplication drifts |
| Bypass guard via `get_eprom`/`convert_to_programmer` | Add `require_supported=False` seam to `resolve_chip` | Research SUMMARY recommends the no-shared-code-change bypass; a new seam changes the safety chokepoint |

**Installation:** No `pyproject.toml` change. Zero new third-party dependencies (confirmed by SUMMARY.md STACK stream + this session's source read).

**Version verification:** N/A — no external package added this phase. `python -c "import hashlib, dataclasses"` confirms stdlib availability (Python ≥3.9 target per CI matrix).

## Package Legitimacy Audit

> Not applicable — this phase installs **no external packages**. All capabilities are satisfied by Python stdlib + existing in-repo modules. No `pyproject.toml` change.

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

## Architecture Patterns

### System Architecture Diagram

```
 dev test <chip>  (CLI handler = Phase 112, NOT this phase)
        │
        ▼
 ┌──────────────────────── chip_test.py (THIS PHASE) ────────────────────────┐
 │                                                                            │
 │  derive_plan(name, db, destructive)                                        │
 │        │  db.get_eprom(name) ──► full dict {protocol-id, electrical-type,  │
 │        │                                    flags(FLAG_CAN_ERASE), chip-id}│
 │        │  db.convert_to_programmer(full) ──► programmer dict {algorithm,   │
 │        │                                    flags, memory-size, vpp_mv...}  │
 │        │  (NO resolve_chip → support-status guard BYPASSED for derivation) │
 │        ▼                                                                    │
 │  [ ordered step list ]  id → read → blank → (write → verify → erase →      │
 │                          blank)   built from protocol→ops table + CAN_ERASE│
 │        │                                                                    │
 │        ▼                                                                    │
 │  run_plan(plan, operator, db)                                              │
 │     step 1: check_eprom_id ──► (is_ok, detected_id)                        │
 │        │        mismatch? ──► set destructive_gate=CLOSED (chip pristine)  │
 │        ▼                                                                    │
 │     each remaining step (independent, non-fatal try/except):               │
 │        eprom_data = resolve_chip(name, db)   ◄── guard-HONORING execution   │
 │        operator.<method>(name, eprom_data, ...)                            │
 │        │  N≥2 for destructive/verify ──► marginal on disagreement          │
 │        │  write step: generate_pattern(start,len) ─► tmp file ─► write     │
 │        │              verify ─► read-back ─► classify_fingerprint()        │
 │        ▼                                                                    │
 │     [ per-step result: verdict, error_code, fingerprint, run_count ]       │
 └────────────────────────────────────────────────────────────────────────────┘
        │
        ▼
 DiagnosticReport model  (= Phase 110, NOT this phase)
```

File-to-implementation mapping (not in the diagram): see Component Responsibilities below.

### Recommended Project Structure
```
firestarter_app/firestarter/
├── chip_test.py          # NEW — derive_plan, run_step/run_plan, pattern gen, classifier
├── eprom_operations.py   # MODIFIED (small) — EpromOperationError kwarg + error_code pass-through
└── (unchanged)           # database.py, chip_resolver.py, exceptions.py consumed as-is

firestarter_app/tests/
├── test_chip_test.py     # NEW — engine unit tests (mock operator + skip_local_override DB)
└── (reference)           # test_validate_family_cmd.py, test_consistency_check.py (copy seams)
```

### Pattern 1: Compose-don't-reimplement (validate-family precedent)
**What:** The engine calls existing operator methods verbatim; it never rebuilds a read/write loop.
**When to use:** Every op step.
**Example:**
```python
# Source: firestarter_app/firestarter/cli_handlers.py:1566 (dev_validate_family)
eprom_data = resolve_chip(rep_chip, db=app.db)      # guard-honoring execution path
verdict_int = app.eprom_operator.write_cycle_eprom( # compose, no re-impl
    rep_chip, eprom_data, source_image_path=source, runs=1, ...)
```

### Pattern 2: Plan derivation bypasses the guard (SWEEP-01)
**What:** Read DB fields directly, never through `resolve_chip`.
**When to use:** `derive_plan()` only.
**Example:**
```python
# Source: firestarter_app/firestarter/database.py:506,535 + chip_resolver.py:16
full = db.get_eprom(name)                    # full dict: protocol-id, electrical-type, flags
prog = db.convert_to_programmer(full)        # programmer dict: algorithm, flags(FLAG_CAN_ERASE)
# resolve_chip is NOT called here → ChipNotImplementedError never raised for derivation.
protocol   = prog["algorithm"]               # == full["protocol-id"]
etype      = full["electrical-type"]         # "UV-EPROM" | "EEPROM" | "Flash/EEPROM" | "SRAM" | "FRAM"
can_erase  = bool(prog["flags"] & FLAG_CAN_ERASE)   # FLAG_CAN_ERASE == 0x02
```

### Pattern 3: N-run SHA divergence verdict (SWEEP-04 / D-05/06)
**What:** Run N≥2, collect SHA-256 per run, verdict on distinct-count.
**Example:**
```python
# Source: firestarter_app/firestarter/eprom_operations.py:703, 808, 818-819
if runs < 2:            # D-05 reject guard, BEFORE any state-machine call
    ...return error
sha = hashlib.sha256(run_bytes).hexdigest()
distinct = sorted({r_sha for r_sha in results})
diverged = len(distinct) != 1        # → destructive/verify: report `marginal` (not PASS/FAIL)
```

### Pattern 4: Byte-diff-offset math for fingerprint (PATT-02 / D-04)
**What:** Reuse the exact offset-collection + percentage math already in `consistency_check_eprom`.
**Example:**
```python
# Source: firestarter_app/firestarter/eprom_operations.py:842-863
cmp_len = min(len(expected), len(actual))
diff_offsets = [o for o in range(cmp_len) if expected[o] != actual[o]]
pct = 100.0 * len(diff_offsets) / cmp_len if cmp_len else 0.0
# Then classify by WHERE offsets cluster + WHAT actual bytes are (see Fingerprint Classifier).
```

### Anti-Patterns to Avoid
- **Fail-fast sweep:** one `BAD`/exception aborting the run hides the surprise (W29C040 locked-boot-block). Each step MUST be independent + non-fatal.
- **Fixed write pattern:** blind to address-line faults. Use the XOR-fold (D-01).
- **Re-invoking `classify()` at runtime:** `classify()` is a build-time function over `infoic.xml` ints (build_db.py); the DB already froze its result. Read the frozen fields.
- **Setting VPP / building raw wire commands:** reintroduces the v1.12/v1.20-removed 12V hazard. The engine sets no VPP and adds no dispatch (Phase 109 CI-gates this).
- **Passing `--force`:** never.
- **Forcing an ambiguous fingerprint into a confident label:** emit `indeterminate` (D-03).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| N-run divergence detection | New SHA/compare loop | `consistency_check_eprom` math (eprom_operations.py:703,808,842) | D-04 mandate; drift risk |
| Chip DB → programmer dict | Parse `chip_database.json` directly | `db.get_eprom` + `db.convert_to_programmer` | Canonical field derivation incl. FLAG_CAN_ERASE (database.py:582-595) |
| Per-op firmware dispatch | New serial command builder | `EpromOperator.{check_eprom_id,read,write,verify,erase,blank}` | Zero new dispatch = Phase 109 CI gate |
| Typed error dispatch by id | New per-raise-site id check | `_raise_for_error_response` chokepoint (eprom_operations.py:70) | Already centralizes id-keyed dispatch |
| CLI test scaffolding | New fake app harness | `make_app_context()` + `Mock(spec=EpromOperator)` (test_validate_family_cmd.py) | Established bench-free seam |

**Key insight:** This phase is 90% orchestration of code that already exists and is already tested; the genuinely-new code is three pure functions (address fold, pattern gen, classifier) plus a one-attribute exception change. Hand-rolling any of the composed pieces both duplicates tested code and risks reintroducing the VPP/dispatch hazards the last four milestones removed.

## Runtime State Inventory

> Not a rename/refactor/migration phase — greenfield engine module. **Omitted** per protocol (no stored data, live-service config, OS-registered state, secrets, or build artifacts carry a renamed string). One near-adjacent note: adding the `error_code` kwarg to `EpromOperationError` is additive and backward-compatible (D-07) — no existing raise site changes behavior; verified `EpromOperationError` is currently a bare `pass` subclass (exceptions.py:37-40).

## Deep-Dive: The Five Plannable Unknowns

### 1. Fingerprint Classifier Signature Math (D-04, PATT-02)

**Reused divergence math (the "transport/scatter signal"):** `consistency_check_eprom` (eprom_operations.py:842-863) already computes, for two byte arrays:
- `diff_offsets = [o for o in range(cmp_len) if a[o] != b[o]]`
- `pct = 100.0 * len(diff_offsets) / cmp_len`
- first-divergence offset and a head slice of offsets.

For the fingerprint the engine reuses this exact offset/percentage computation but the two arrays are **expected-pattern vs read-back** (not run1-vs-run2). For the transport bucket it ALSO uses the run1-vs-run2 divergence (non-repeatability across the N≥2 runs) — that is where `consistency_check_eprom`'s original semantic (read-repeatability) directly feeds PATT-02.

**Recommended classifier contract (Claude's discretion on exact shape — this is a candidate):**
```python
@dataclass
class Fingerprint:
    total: int              # bytes compared
    bad: int                # count of mismatches
    bad_pct: float          # 100*bad/total
    classification: str     # "blank/contact" | "address-line" | "transport" | "indeterminate"
    evidence: dict          # signature stats used (see below)

def classify_fingerprint(expected: bytes, actual: bytes,
                         *, repeat_divergent: Optional[bool] = None,
                         addr_base: int = 0) -> Fingerprint: ...
```

**Signature math per bucket (candidate thresholds — TUNABLE, HIGH-confidence on *direction*, MEDIUM on *exact numbers*):**

| Bucket | Signature | Candidate numeric test |
|--------|-----------|------------------------|
| `blank/contact` [CITED: dev-test-design-decisions.md] | Read-back is all/near-all `0xFF` (or all-`0x00` for some parts) | `sum(1 for b in actual if b == 0xFF) / total >= 0.98` → blank/contact. (A contact fault reads the un-driven bus = `0xFF`.) |
| `address-line` [CITED: US4876684, US7532526 via SUMMARY.md] | Mismatches cluster at addresses differing only in high bits / power-of-two-aliased pairs (A8+). With the XOR-fold, a stuck high line makes `expected != actual` precisely at addresses where that bit flips. | Detect power-of-two aliasing: for each candidate line `k` in `8..log2(total)`, count mismatches whose offset has bit `k` set vs clear; if mismatches concentrate on one polarity of a single high bit (e.g. `>= 0.9` of mismatches share `offset & (1<<k)` pattern) → address-line, and record the suspected line `k`. |
| `transport` | Mismatches scattered (no high-bit clustering) AND non-repeatable across the N≥2 runs (run1≠run2 via reused SHA/offset divergence). | `repeat_divergent is True` AND no dominant address-bit → transport. uno328pb signature. |
| `indeterminate` (D-03) | None of the above dominates (mixed, ambiguous, or repeatable-but-scattered). | Fallback — never coerce. |

**Ordering matters:** test blank/contact first (cheapest, most common false-PASS source), then address-line clustering, then transport (needs the repeat signal), else `indeterminate`. The `evidence` dict should carry the raw stats (`ff_ratio`, per-bit clustering scores, `repeat_divergent`) so Phase 110's report can show *why* — the project's false-PASS history (Bug A, ST-vs-Winbond, AM27C020) makes the "show the evidence" contract load-bearing.

`addr_base` matters because D-02 makes the pattern region-parameterized (Phase 109 caps UV writes to a high-address window): the classifier must map a read-back offset back to the **absolute chip address** (`addr_base + offset`) before doing high-bit clustering, or the address-line signal is computed against the wrong bits.

### 2. Plan-Derivation vs Execution Split (SWEEP-01/02)

**Derivation call sequence (guard bypassed — the guard lives ONLY inside `resolve_chip`, chip_resolver.py:16, which derivation never calls):**
```
full = db.get_eprom(name)                    # database.py:506 — returns _map_data() dict or None
prog = db.convert_to_programmer(full)        # database.py:535 — returns {} on empty
protocol  = prog["algorithm"]                # == full["protocol-id"]  (build-time protocol_id int)
etype     = full["electrical-type"]          # database.py:422
can_erase = bool(prog["flags"] & 0x02)       # FLAG_CAN_ERASE set in convert_to_programmer (database.py:582-595)
```
`convert_to_programmer` sets `FLAG_CAN_ERASE` when `electrical-type ∈ {"EEPROM","Flash/EEPROM"}` AND `algorithm != 5` (flash4 auto-erases per page; setting the flag on 0x05 routes a 12V erase on a 5V part — hazard, so it's deliberately clear for 0x05). **This means for protocol 0x05 (flash4), `FLAG_CAN_ERASE` is CLEAR even though the chip is electrically re-writable** — the plan's erase step for 0x05 must be `NA` (auto-erase during write), matching the flag.

**Op-support table (protocol → ops) — derived from live DB counts + operator-method semantics this session:**

| protocol (algorithm) | electrical types present | id | read | blank-check | write | verify | erase | Notes |
|---|---|---|---|---|---|---|---|---|
| 0x05 flash4 (FLASH_AMD_STD) | Flash/EEPROM (27) | ✓ | ✓ | ✓ | ✓ | ✓ | **NA** (auto-erase per page; FLAG_CAN_ERASE clear by design) | W29C040 locked-boot-block lives here |
| 0x06 | Flash/EEPROM (190) | ✓ | ✓ | ✓ | ✓ | ✓ | if CAN_ERASE | |
| 0x07 EPROM_STD | UV-EPROM (163), EEPROM (7) | ✓ | ✓ | ✓ | ✓ (destructive; UV small-region) | ✓ | **NA for UV-EPROM** (no electrical erase); if CAN_ERASE for the 7 EEPROMs | 12V VPP path |
| 0x08 | UV-EPROM (106), EEPROM (21) | ✓ | ✓ | ✓ | ✓ | ✓ | NA for UV; if CAN_ERASE for EEPROM | AM27C020 marginal-write lives here |
| 0x0B | UV-EPROM (32) | ✓ | ✓ | ✓ | ✓ (UV small-region) | ✓ | NA (UV) | |
| 0x0D EEPROM_POLL | EEPROM (66), Flash/EEPROM (18) | ✓ | ✓ | ✓ | ✓ | ✓ | if CAN_ERASE | 5V, configure_eeprom28c |
| 0x0E, 0x27, 0x28, 0x29 | SRAM (75), FRAM (1) | maybe | ✓ | **NA** (SRAM/FRAM short-circuit) | ✓ | ✓ | NA | `check_eprom_blank` returns False + warns for SRAM/FRAM (eprom_operations.py:1656-1676) |
| 0x10 | Flash/EEPROM (39) | ✓ | ✓ | ✓ | ✓ | ✓ | if CAN_ERASE | |
| 0x34 | EEPROM (1) | ✓ | ✓ | ✓ | ✓ | ✓ | if CAN_ERASE | X88C64 |
| 0x39, 0x40, 0x41 | (small counts) | ✓ | ✓ | ? | ✓ | ✓ | if CAN_ERASE | verify support against firmware dispatch during planning |

**Derivation rules (locked-field-driven, no `classify()`):**
- **id-check**: include if `full` carries `chip-id` (from `programming.chip_id_value`, database.py:425-427) — else `NA` (no expected id to compare). `programming.chip_id_check` also gates it. Always ordered FIRST (SWEEP-03).
- **read / verify**: always supported (every protocol reads).
- **blank-check**: `NA` when `electrical-type ∈ {"SRAM","FRAM"}` OR `protocol ∈ {0x0E,0x27,0x28,0x29}` (mirror the operator's own short-circuit, eprom_operations.py:1667-1669) — else supported.
- **write**: supported (destructive). UV-EPROM write is small-region (Phase 109 caps it via the region-parameterized generator).
- **erase**: supported only if `FLAG_CAN_ERASE` set AND `protocol != 0x05`; else `NA`. UV-EPROM never has the flag (electrical.type is "UV-EPROM", not in the EEPROM set) → erase `NA`.

**Execution path (guard-honoring):** each executed step calls `resolve_chip(name, db=app.db)` (chip_resolver.py:16) to get the programmer dict and then the operator method — identical to `dev_validate_family` (cli_handlers.py:1566). If `resolve_chip` raises `ChipNotImplementedError` / `ChipNotFoundError`, that step's verdict is `SKIPPED` (or `NA`) with the reason recorded — the guard stays authoritative for real hardware ops while derivation still listed the op.

**⚠ Planning nuance (important):** the programmer dict from `convert_to_programmer` does **NOT** contain `electrical-type` or `protocol-id` keys — but `check_eprom_blank` reads `eprom_data_dict.get("electrical-type")` / `.get("protocol-id")` (eprom_operations.py:1667-1668) for its SRAM/FRAM short-circuit. In the normal CLI path the operator receives the programmer dict, so those keys are ABSENT and the short-circuit only trips on the `protocol-id in _SRAM_PROTO_IDS` branch when `protocol-id` happens to be present, or not at all. The engine should either (a) let `derive_plan` mark SRAM/FRAM blank-check `NA` up front (recommended — the plan already knows the type), or (b) merge `electrical-type`/`protocol-id` into the dict it passes to `check_eprom_blank`. Recommend (a): the plan owns the NA decision, the operator call is only made for supported steps.

### 3. N≥2 / Marginal Policy (SWEEP-04, D-05/06)

- **`runs` param + guard:** mirror `consistency_check_eprom(runs: int = 3)` and its `if runs < 2:` reject BEFORE any state-machine call (eprom_operations.py:703-709). For this engine, D-05 sets the DEFAULT to N=2 (not 3). Reject `<2` early with a clear error, no operator call.
- **`marginal` (destructive/verify only, D-06):** run the write→verify (and read-back) N times; collect per-run SHA-256 (or per-run verify verdict). If the runs **disagree**, the step verdict is `marginal` — never PASS/FAIL. This is the AM27C020 case (write#1 60/64 vs write#2 0/64) made structural.
- **Read-step disagreement (D-06):** measured as **byte-level divergence** (reuse the offset/pct math), reported as a divergence metric on the read step — NOT a verdict flip and NOT `marginal` (marginal is destructive/verify-only per D-06).

### 4. error_code Seam (RPT-03, D-07)

- **Where `response.id` lives:** `Response` is a namedtuple `("Response", ["type","message","payload","id"])` (frame_parser.py:18) — `.id` is the firmware message-id byte (e.g. `0xA4`, `0xBB`, `0xB3`).
- **Single chokepoint:** `_raise_for_error_response(response, message)` at eprom_operations.py:70 already reads `response.id` to dispatch `ProtocolNotImplementedError` (for `0xBB`) vs `EpromOperationError`. This is the ONE place to thread the code:
```python
# Source: firestarter_app/firestarter/eprom_operations.py:82-86 (CURRENT)
if response.id == MSG_ERR_PROTOCOL_NOT_IMPLEMENTED:
    raise ProtocolNotImplementedError(response.message)
raise EpromOperationError(message)                      # ← discards response.id today
# PLANNED (D-07):
raise EpromOperationError(message, error_code=response.id)
```
- **Exception change (D-07):** `EpromOperationError` is a bare `pass` subclass today (exceptions.py:37-40). Add:
```python
class EpromOperationError(Exception):
    def __init__(self, *args, error_code=None):
        super().__init__(*args)
        self.error_code = error_code
```
Subclasses (`ProtocolNotImplementedError`, `ChipNotImplementedError`) inherit the kwarg automatically; existing `raise EpromOperationError("…")` sites (e.g. eprom_operations.py:526, 546) keep working with `error_code=None`. `ProtocolNotImplementedError(response.message)` could optionally also pass `error_code=response.id` for symmetry (discretionary — the id there is always `0xBB`).
- **Other raise sites:** eprom_operations.py:526 (`Input file not found` — no firmware response, leave `None`) and :546 (`did not request data chunk` — has a `response`, MAY pass `response.id`). The load-bearing one for the sweep is the `_raise_for_error_response` chokepoint.

### 5. Unit-Test Seam (SWEEP-03, bench-free)

Two proven seams to copy:

**(a) CLI/engine level — `make_app_context()` (tests/test_validate_family_cmd.py:28-55):**
```python
db = EpromDatabase(skip_local_override=True)          # no ~/.firestarter, no serial
eprom_operator = Mock(spec=EpromOperator)             # steps call mock methods
app = AppContext(db=db, config_manager=..., eprom_operator=eprom_operator, ...)
```
Set `eprom_operator.check_eprom_id.return_value = (True, 0x1234)` etc. to drive verdicts; assert the plan/step results. This exercises `derive_plan` + `run_plan` with zero hardware.

**(b) Operator-internals monkeypatch (tests/test_consistency_check.py):** replace `EpromOperator._operation_context` with a `@contextmanager fake_ctx` yielding `(cmd_data, buffer_size, op_name)` and `_run_state_machine` with a `fake_state_machine` that invokes `process_data_chunk_callback` with controlled payloads then returns `(True, None)` / `(False, "timeout")` / raises `EpromOperationError`. Use this to test the fingerprint classifier against synthetic read-back byte streams (stuck-high-line pattern, all-0xFF, scattered) and to test the `error_code` propagation (raise `EpromOperationError(msg, error_code=0xA4)` in the fake and assert the step captured `0xA4`).

**Pure-function tests (no mock needed):** `address_fold_byte(addr)`, `generate_pattern(start, length)`, `classify_fingerprint(expected, actual)` are pure — test with hand-constructed byte arrays (e.g. flip bit A8 across a region and assert `address-line`; set 98% to 0xFF and assert `blank/contact`).

## Common Pitfalls

### Pitfall 1: Fail-fast hides the surprise
**What goes wrong:** A `BAD` blank-check or an exception aborts the sweep, so the write/erase findings never run.
**Why it happens:** Natural Python control flow lets an exception propagate.
**How to avoid:** Wrap each step in its own try/except that maps any exception to a `BAD` verdict + captured `error_code`, and continues. The W29C040 locked-boot-block is the canonical case — the *surprise* is the value.
**Warning signs:** A test where step 2 raising prevents step 3 from executing.

### Pitfall 2: Guard bypass leaks into execution
**What goes wrong:** Plan derivation's guard bypass accidentally becomes the execution path, driving hardware for a non-supported chip.
**Why it happens:** Reusing the derivation dict for the operator call instead of re-resolving.
**How to avoid:** Derivation uses `get_eprom`/`convert_to_programmer` ONLY; every executed op re-calls `resolve_chip(name, db)` (guard-honoring). If `resolve_chip` refuses, the step is `SKIPPED`/`NA` with reason — the op was listed (so the report shows "this chip's protocol supports write, but the host guard refuses it").
**Warning signs:** No `resolve_chip` call inside `run_step`.

### Pitfall 3: Address-line signal computed on the wrong bits
**What goes wrong:** For a small-region UV write (Phase 109), the classifier clusters on offset-within-region bits, not absolute-address bits — missing the high-address-line fault the tool exists to catch.
**How to avoid:** Pass `addr_base` (region start) to `classify_fingerprint` and cluster on `addr_base + offset`.
**Warning signs:** Classifier signature ignores the region start.

### Pitfall 4: chip-ID mismatch doesn't actually gate destructive steps
**What goes wrong:** id mismatch is recorded but write still runs → a wrong chip gets written (false PASS / bricked part).
**How to avoid:** id-check is step 1; on mismatch (`is_ok == False` OR `detected_id != expected`) set a `destructive_gate=CLOSED` flag that every destructive/write/erase step checks first, marking itself `SKIPPED` (chip pristine). Non-destructive id/read/blank findings still recorded.
**Warning signs:** A test where id mismatch + a write step still calls `operator.write_eprom`.

### Pitfall 5: N=1 fluke reported as confident PASS/FAIL
**What goes wrong:** A single destructive run's disagreement-vs-nothing is reported as PASS.
**How to avoid:** Destructive/verify N≥2; disagreement → `marginal`. Reject `runs < 2` early (mirror the existing guard).

### Pitfall 6: FLAG_CAN_ERASE misread for flash4 (0x05)
**What goes wrong:** Assuming Flash/EEPROM always erases and emitting an erase step for 0x05, which routes a 12V bulk-erase on a 5V part.
**How to avoid:** Trust `FLAG_CAN_ERASE` (it is deliberately CLEAR for 0x05, database.py:585-594). erase step `NA` when the flag is clear.

## Code Examples

### Address-derived pattern generator (D-01, D-02)
```python
# Region-parameterized (D-02): no full-chip assumption.
def address_fold_byte(addr: int) -> int:
    return (addr ^ (addr >> 8) ^ (addr >> 16) ^ (addr >> 24)) & 0xFF

def generate_pattern(start: int, length: int) -> bytes:
    return bytes(address_fold_byte(start + i) for i in range(length))

# Pre-pass images (cheap all-0x00 / all-0xFF), same region params:
def prepass_images(length: int) -> tuple[bytes, bytes]:
    return b"\x00" * length, b"\xFF" * length
```

### error_code kwarg (D-07)
```python
# firestarter/exceptions.py  (EpromOperationError today is a bare `pass` subclass)
class EpromOperationError(Exception):
    """Custom exception for EPROM operation failures."""
    def __init__(self, *args, error_code=None):
        super().__init__(*args)
        self.error_code = error_code
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Fixed/checkerboard health pattern | Address-derived XOR-fold | This phase (D-01) | Detects stuck/aliased address lines instead of hiding them |
| 3-label fault classification | 4-label with explicit `indeterminate` | This phase (D-03) | No over-confident mis-diagnosis (project false-PASS history) |
| `response.id` discarded at raise | Preserved via `error_code` | This phase (D-07) | Per-step reports carry exact firmware code |

**Deprecated/outdated:** Do NOT call `classify()` at runtime — it is build-time only (`tools/build_db.py` over `infoic.xml` ints); the DB froze its output into `protocol`/`electrical.type`/`FLAG_CAN_ERASE`.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `blank/contact` reads as `0xFF` (un-driven bus). Some parts blank-erase to `0x00`. | Fingerprint Classifier | Classifier may bucket an all-`0x00` blank as `indeterminate`; mitigate by testing both 0xFF and 0x00 saturation. Non-fatal (falls to `indeterminate`, per D-03). |
| A2 | Candidate numeric thresholds (0.98 ff-ratio, 0.9 bit-clustering) | Fingerprint Classifier | Direction is HIGH-confidence; exact numbers are Claude's discretion (D-04) and bench-tunable. Wrong numbers → more `indeterminate`, never a false confident label. |
| A3 | Protocols 0x39/0x40/0x41 op-support (small DB counts) | Op-Support Table | Verify against firmware dispatch during planning; conservative default (read/verify always, erase gated by flag) is safe. |
| A4 | `programming.chip_id_check` + presence of `chip_id_value` gates the id step | Derivation Rules | If a chip has an id in DB but `chip_id_check=false`, plan may skip id gating; safe default is include id-check when `chip-id` present. |

**All four are LOW-risk:** each degrades toward `indeterminate`/`NA`/conservative-include, never toward a confident false PASS or a hardware hazard.

## Open Questions

1. **UV small-region window size/placement (Phase 109 owns the cap, but the generator is here).**
   - What we know: generator must be region-parameterized (D-02); a high-address contiguous window maximizes upper-address-line coverage from a small write.
   - What's unclear: exact byte size (bench-informed).
   - Recommendation: generator takes `(start, length)`; leave the concrete window to Phase 109. Test the generator against arbitrary `(start, length)`.

2. **Should `check_eprom_id` "no expected id in DB" be `NA` or a skipped-with-reason?**
   - Recommendation: `NA` (op genuinely not applicable — nothing to compare), record "no chip-id in DB entry."

## Environment Availability

> No external tools/services. The engine is pure host Python composing in-repo methods; unit tests run with pytest (already the CI framework). **No missing dependencies.**

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python stdlib (`hashlib`,`dataclasses`,`typing`,`contextlib`) | engine + tests | ✓ | ≥3.9 | — |
| pytest | unit tests | ✓ | existing CI | — |
| in-repo `EpromOperator`/`EpromDatabase`/`resolve_chip` | engine | ✓ | current | — |

## Validation Architecture

> `workflow.nyquist_validation` is absent in `.planning/config.json` → treated as **enabled**.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (with `pytest-cov`, `--cov-fail-under=70` enforced by CI) |
| Config file | `firestarter_app/pyproject.toml` (+ `.github/workflows/ci.yml`) |
| Quick run command | `cd firestarter_app && python -m pytest tests/test_chip_test.py -x -q` |
| Full suite command | `cd firestarter_app && python -m pytest -q` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SWEEP-01 | Plan derived from protocol/etype/CAN_ERASE; guard bypassed; no classify() | unit | `pytest tests/test_chip_test.py -k derive_plan -x` | ❌ Wave 0 |
| SWEEP-01 | Non-supported chip still yields a plan (bypass) | unit | `pytest tests/test_chip_test.py -k derive_bypasses_guard -x` | ❌ Wave 0 |
| SWEEP-02 | One step BAD/raises → remaining steps still run | unit | `pytest tests/test_chip_test.py -k non_fatal -x` | ❌ Wave 0 |
| SWEEP-02 | Verdict vocabulary OK/BAD/NA/SKIPPED | unit | `pytest tests/test_chip_test.py -k verdict_vocab -x` | ❌ Wave 0 |
| SWEEP-03 | id-first; mismatch gates destructive shut, id/read still recorded | unit | `pytest tests/test_chip_test.py -k id_mismatch_gate -x` | ❌ Wave 0 |
| SWEEP-04 | destructive/verify N≥2; disagreement → marginal | unit | `pytest tests/test_chip_test.py -k marginal -x` | ❌ Wave 0 |
| SWEEP-04 | runs<2 rejected before any op call | unit | `pytest tests/test_chip_test.py -k runs_boundary -x` | ❌ Wave 0 |
| PATT-01 | XOR-fold byte + region-parameterized pattern + pre-pass | unit | `pytest tests/test_chip_test.py -k pattern -x` | ❌ Wave 0 |
| PATT-02 | classifier → blank/contact | unit | `pytest tests/test_chip_test.py -k fp_blank -x` | ❌ Wave 0 |
| PATT-02 | classifier → address-line (stuck A8+) | unit | `pytest tests/test_chip_test.py -k fp_address_line -x` | ❌ Wave 0 |
| PATT-02 | classifier → transport (scattered + non-repeatable) | unit | `pytest tests/test_chip_test.py -k fp_transport -x` | ❌ Wave 0 |
| PATT-02 | classifier → indeterminate (no dominant signature) | unit | `pytest tests/test_chip_test.py -k fp_indeterminate -x` | ❌ Wave 0 |
| RPT-03 | EpromOperationError(error_code=…) stored; old sites still work | unit | `pytest tests/test_chip_test.py -k error_code -x` | ❌ Wave 0 |
| RPT-03 | `_raise_for_error_response` passes response.id | unit | `pytest tests/test_chip_test.py -k raise_for_error_carries_id -x` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `python -m pytest tests/test_chip_test.py -x -q`
- **Per wave merge:** `python -m pytest -q` (full app suite — must stay green; `ruff check` + `ruff format --check` + `mypy` on the strict-8 modules)
- **Phase gate:** full suite green + `--cov-fail-under=70` before `/gsd-verify-work`.

### Wave 0 Gaps
- [ ] `tests/test_chip_test.py` — covers SWEEP-01..04, PATT-01/02, RPT-03 (new file)
- [ ] Reuse existing `make_app_context()` seam — copy from `tests/test_validate_family_cmd.py` (no new conftest needed)
- [ ] Framework install: already present (pytest in `.[test]`); restore via `pip install -e '.[test]'` if the toolchain was wiped (see auto-memory note on devcontainer test env)

## Project Constraints (from CLAUDE.md)

From `/workspaces/CLAUDE.md` and `/workspaces/firestarter_app/CLAUDE.md`:
- **Constants sync:** `firestarter/constants.py` mirrors firmware `firestarter/include/firestarter.h`. This phase reads `FLAG_CAN_ERASE` (0x02) and `COMMAND_*` from `constants.py` — do not redefine; import. **No firmware change this phase** (no constant added).
- **Serial protocol sync:** no wire-protocol change (engine composes existing ops). Keep it that way — Phase 109 CI-gates zero new dispatch.
- **Do NOT edit `chip_database.json` by hand** — it is generated. This phase only reads it via `EpromDatabase`.
- **`messages.h` is codegen-generated** — not touched here (no new message).
- **Tooling gate (v1.8):** `ruff check` + `ruff format --check` + `mypy` (strict on 8 modules incl. `exceptions.py`) + `pytest --cov-fail-under=70`, enforced by `.github/workflows/ci.yml`. `exceptions.py` is in the strict-mypy set → the `error_code` kwarg must be type-annotated (`error_code: int | None = None`).
- **Devcontainer test env:** use `/usr/local` python; validate `ruff check` + `ruff format --check` against py39/3.11 target (devcontainer py312 masks CI); f-string backslashes are a known trap.
- **Submodule path:** all source lives in `firestarter_app/` — executors commit INSIDE the submodule on the milestone branch.

## Security Domain

> `workflow.security_enforcement` absent → treated as enabled. This phase is host-side Python composing existing hardware ops; the dominant risk class is **hardware safety / false-diagnosis**, not classic web ASVS.

### Applicable ASVS Categories
| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | — |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| V5 Input Validation | yes | Chip name → `EpromDatabase` lookup (existing, alias-matched); `runs<2` rejected early; region params bounded by caller |
| V6 Cryptography | no (SHA-256 used for equality, not security) | Reuse `hashlib` as-is |

### Known Threat Patterns for this stack (project-specific STRIDE)
| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Engine sets VPP / builds raw command → 12V hazard | Tampering / Elevation | Compose existing operator methods only; set no VPP; Phase 109 CI-gate (zero new dispatch + zero VPP-set sites) |
| Wrong chip written (false PASS) | Spoofing | id-first; mismatch hard-gates destructive (SWEEP-03) |
| Over-confident fault label mis-diagnoses (Bug A / ST-vs-Winbond) | Repudiation / Info | Explicit `indeterminate` bucket (D-03); classifier `evidence` dict |
| N=1 fluke → false conclusion (AM27C020) | Info | N≥2 + `marginal` (SWEEP-04) |
| UV full-region write bricks eraser-less chip | Denial (of the chip) | Region-parameterized generator; Phase 109 caps; erase `NA` for UV |
| Guard bypass leaks to execution | Elevation | Derivation uses `get_eprom`/`convert_to_programmer`; execution re-resolves via `resolve_chip` |

## Sources

### Primary (HIGH confidence)
- `firestarter_app/firestarter/eprom_operations.py` — `consistency_check_eprom` (divergence math :703/808/818/842-863), `write_eprom`/`verify_eprom`/`erase_eprom`/`check_eprom_blank`/`check_eprom_id` (:1555-1730), `_raise_for_error_response` (:70), `_operation_context`/`_setup_operation` (:287-347).
- `firestarter_app/firestarter/database.py` — `get_eprom` (:506), `convert_to_programmer` (:535, FLAG_CAN_ERASE derivation :582-595), `_map_data` (:365-434).
- `firestarter_app/firestarter/chip_resolver.py` — `resolve_chip` guard (:16).
- `firestarter_app/firestarter/exceptions.py` — `EpromOperationError` bare-`pass` today (:37-40).
- `firestarter_app/firestarter/frame_parser.py` — `Response` namedtuple with `.id` (:18).
- `firestarter_app/firestarter/constants.py` — `FLAG_CAN_ERASE=0x02` (:91), `COMMAND_*` (:56-61).
- `firestarter_app/tests/test_validate_family_cmd.py` — `make_app_context()` + `Mock(spec=EpromOperator)` seam.
- `firestarter_app/tests/test_consistency_check.py` — operator-internals monkeypatch seam.
- `firestarter_app/firestarter/data/chip_database.json` — live protocol×type combos (counted this session).
- `.planning/REQUIREMENTS.md` (SWEEP/PATT/RPT text), `.planning/phases/108-.../108-CONTEXT.md` (D-01..D-07), `.planning/notes/dev-test-design-decisions.md`, `.planning/research/SUMMARY.md`.

### Secondary (MEDIUM confidence)
- SUMMARY.md-cited patents US4876684 / US7532526 (address-in-data stuck-line detection) — informs the address-line signature direction; exact thresholds bench-tunable.

### Tertiary (LOW confidence)
- None adopted.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — zero new deps; every method read this session.
- Architecture: HIGH — mirrors the shipped `dev validate-family`; every file/function named.
- Pitfalls: HIGH — grounded in first-party RCA history (Bug A, ST-vs-Winbond, AM27C020, uno328pb, W29C040) + read source.
- Fingerprint thresholds: MEDIUM (direction HIGH, exact numbers discretionary/tunable per D-04).

**Research date:** 2026-07-02
**Valid until:** 2026-08-01 (stable — internal source + locked decisions; refresh if `eprom_operations.py`/`database.py` refactor)
