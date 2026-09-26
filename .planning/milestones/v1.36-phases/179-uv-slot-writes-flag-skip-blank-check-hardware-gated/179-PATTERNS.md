# Phase 179: UV Slot Writes — `FLAG_SKIP_BLANK_CHECK` (hardware-gated) - Pattern Map

**Mapped:** 2026-09-06
**Files analyzed:** 12 (11 modified, 3 created — two files are both)
**Analogs found:** 12 / 12
**Submodule scope:** all product/test paths are inside `firestarter_app` (the Python host CLI submodule). `firestarter` (the Arduino firmware submodule) is **read-only reference** this phase — the research proves no firmware edit is required.

---

## HARD RULES the planner must carry into every plan

These are project standing rules, not phase preferences. A plan cannot override any of them.

1. **NO comments in source code, at all, ever.** Every excerpt below is quoted *with* its surrounding comments because that is what the tree contains — **do not copy the comments**. Copy the code shape only. Rationale belongs in the PLAN.md and (only where the tree already does so) in docstrings. Phase 178's verify blocks assert `phase_added_comments=0` by diffing `^\+[[:space:]]*#`; reuse that leg verbatim (see `## Shared Patterns → Per-commit hygiene block`).
2. **`firestarter_app/firestarter/data/chip_database.json` is GENERATED** — never hand-edited. This phase must not touch it; assert it clean in every hygiene block.
3. **Flag bits are duplicated** in `firestarter_app/firestarter/constants.py` (Python) and `firestarter/include/firestarter.h` (C++) — a flag *change* is always a two-file, two-submodule change. **This phase changes no flag bit**: `FLAG_SKIP_BLANK_CHECK = 0x08` already exists on both sides, verified identical. The rule is recorded so the planner does not accidentally propose a new bit.
4. **`firestarter/src/messages.h` does not exist.** Message ids live in `firestarter/include/messages.h`, which is **codegen-generated and ID-only**; the source of truth is the meta repo's `messages.toml`. This phase needs no message change.
5. **The app's test env is `firestarter_app/.venv311` (python 3.11).** The devcontainer default 3.12 masks CI failures. Every command in every plan must use `./.venv311/bin/python`.
6. **`grep` in this devcontainer is ugrep and honors `.gitignore`** — it silently under-scans. Use `/usr/bin/grep` for anything that becomes gate evidence.
7. **`operation_flags` must be passed POSITIONALLY.** Two of the three write-capable doubles name the parameter `flags`, not `operation_flags`. A keyword call lands in `**_kw` and silently no-ops. See `## Shared Patterns → Positional flags`.

---

## File Classification

All paths are relative to the `firestarter_app` submodule root unless prefixed. `firestarter/…` inside that table means `firestarter_app/firestarter/…` (the package dir), matching how the existing plans cite it.

| New/Modified File | Submodule | New? | Role | Data Flow | Closest Analog | Match |
|---|---|---|---|---|---|---|
| `firestarter/chip_test.py` — write call site flag | `firestarter_app` | mod | service (orchestrator) | request-response | `firestarter/chip_test.py:3437-3443` (SDP leg) | **exact** |
| `firestarter/chip_test.py` — `WriteTarget` witness field | `firestarter_app` | mod | model (frozen dataclass) | transform | `WriteTarget.region_policy`, `chip_test.py:2327-2413` | **exact** |
| `firestarter/chip_test.py` — tranche carry-through | `firestarter_app` | mod | service | transform | `_uv_cycle_targets`, `chip_test.py:1500-1530` | **exact** |
| `firestarter/chip_test.py` — UV blank-check verdict | `firestarter_app` | mod | service (dispatch) | request-response | `_dispatch_step`'s `OP_BLANK_CHECK` arm, `chip_test.py:2626-2641` | **exact** (in-place edit) |
| `tests/test_chip_test_uv_slot_write.py` | `firestarter_app` | **new** | test (unit) | request-response | `tests/test_chip_test_sdp_leg.py` | **exact** |
| `tests/fake_chip.py` (or a subclass local to the new test) | `firestarter_app` | mod/new | test double (model) | transform | `FakeChip.write_eprom`, `tests/fake_chip.py:133-155` | **exact** |
| `tests/fixtures/report_shapes.py` | `firestarter_app` | mod | test fixture registry | batch | `_build_attr01_status_axis_transport_fault` + `_BUILDERS`/`FROZEN_HASHES`, `report_shapes.py:643-713` | **exact** (Phase 178) |
| `tests/fixtures/shape_ids.json` | `firestarter_app` | mod | fixture anchor (data) | batch | same file, Phase 178's 17→18 edit | **exact** |
| `tests/fixtures/reports/uv-slot-write-pass.json` | `firestarter_app` | **new (generated)** | fixture snapshot | batch | `tests/fixtures/reports/attr01-status-axis-transport-fault.json` | **exact** |
| `tests/test_blast_radius_invariance.py` | `firestarter_app` | mod | test (oracle) | batch | its own `LADDER_PINS` / `_PINNED_SHAPE_ID_SET` blocks | **exact** |
| `tests/fixtures/rekey_ledger.py` | `firestarter_app` | mod | ledger (data-only module) | batch | `RK-174-01` / `RK-174-05` declared rows, `rekey_ledger.py:28-45`, `:70-80` | **exact** |
| `/workspaces/.planning/MILESTONES.md:39` | meta | mod | record | batch | the already-declared `RK-174-01`/`RK-174-05` rows in the same table | **exact** |
| `firestarter/cli_handlers.py:2295-2303` (Q8, optional) | `firestarter_app` | mod | controller | request-response | any prior stale-comment deletion | partial — **deletion only** |
| `179-MEASUREMENT.md` (bench artifact) | meta | **new** | record | batch | `.planning/phases/176-*/176-MEASUREMENT.md` | role-match |

**Deliberately NOT in this list** (the research proves each is out of scope, and the planner should state so explicitly rather than let an executor drift into them):

| File | Why not |
|---|---|
| `firestarter/src/proms/eprom.cpp` (firmware) | already honors the flag at `:143-145`; **no firmware change** |
| `firestarter_app/firestarter/constants.py` + `firestarter/include/firestarter.h` | `0x08` already exists on both sides, unchanged |
| `firestarter/eprom_operations.py` (`build_flags`) | Q3/A4 — the SDP-leg precedent composes inline; see Shared Patterns |
| `firestarter/diagnostic_report.py` | Q5/A5 — the disclosure key is Phase 181's |
| `tests/fixtures/plan_shapes.json` | only moves if `derive_plan`'s `supported` flips; Q1 Option B keeps it byte-unchanged |
| `firestarter/data/chip_database.json` | GENERATED (hard rule 2) |
| `firestarter_app/build/lib/firestarter/` | stale build artifact — never edit, never cite |

---

## Pattern Assignments

### 1. `firestarter/chip_test.py` — the write call site (service, request-response)

**Analog:** `firestarter_app/firestarter/chip_test.py:3437-3443` — the SDP leg, which already passes flags through the identical operator method.

**The pattern to copy** (SDP leg, verbatim; note the bare positional int in the 4th slot):

```python
        wrote_ok = operator.write_eprom(
            name,
            eprom_data,
            tmp_source_path,
            flags,
            address_str=_address_arg(region_start),
        )
```

**The site to change** (`chip_test.py:3186-3194`, verbatim — today's shape, missing the 4th positional):

```python
            if op in (OP_WRITE, OP_WRITE_PARTIAL):
                _sample(sampler, "before")
                outcomes.append(
                    operator.write_eprom(
                        name,
                        eprom_data,
                        tmp_source_path,
                        address_str=_address_arg(region_start),
                    )
                )
```

**Flag composition pattern** (SDP leg, `chip_test.py:3405-3414`) — a bare local int assigned in a branch, never a dict:

```python
    if op == OP_WRITE_BASELINE_B:
        source_payload, expected_readback, flags = pattern_b, pattern_b, 0
    elif op == OP_WRITE_INHIBITED:
        source_payload, expected_readback, flags = (
            pattern_b,
            pattern_a,
            FLAG_SKIP_SDP_UNLOCK,
        )
```

`resolved_target` is in scope at `:3186` (assigned at `:3123` / `:3126-3135`), so the witness needs zero new plumbing.

**Gate constraint:** `tools/check_devtest_orchestrator.py` bans a **dict literal** in `chip_test.py`/`cli_handlers.py`/`submit.py` whose keys intersect the wire vocabulary, `flags` included. A bare positional int is compliant; **never build a flags dict.**

---

### 2. `firestarter/chip_test.py` — the monotonicity witness field (model, transform)

**Analog:** `WriteTarget.region_policy`, `chip_test.py:2327-2413`. It is the most recently added additive field on this frozen dataclass and it establishes the whole discipline: *derive once, carry through unchanged, default to the pre-existing behaviour.*

**Additive-field pattern** (code only — the tree's 20-line comment above it is exactly what hard rule 1 forbids reproducing):

```python
    current: bytes = b""
    slots_remaining: int | None = None
    slots_total: int | None = None
    region_policy: str = REGION_POLICY_FIXED
```

A new `current_is_probe_read: bool = False` follows this shape exactly: defaulting to `False` is **fail-closed** (every existing direct `WriteTarget(...)` construction in the suite keeps working *and* keeps the flag off).

**Set-site pattern** (`_resolve_write_target`'s UV probe arm, `chip_test.py:2955-2970`) — the one place the probe read actually happens:

```python
                target = WriteTarget(
                    region=(slot_start, slot_length),
                    pattern=masked,
                    masked=True,
                    bits_cleared=cleared,
                    bits_retained=retained,
                    current_source="probe read",
                    current=current,
                    slots_remaining=slots_total - slot_index,
                    slots_total=slots_total,
```

**Carry-through pattern** (`_uv_cycle_targets`, `chip_test.py:1510-1530`) — the staged tranches are the only targets that ever reach the report, so a field not carried here is invisible on exactly the family it exists for:

```python
                WriteTarget(
                    region=target.region,
                    pattern=image,
                    masked=True,
                    bits_cleared=cleared,
                    bits_retained=sum(byte.bit_count() for byte in image),
                    current_source=f"{target.current_source} (tranche {cycle}/{cycles})",
                    current=target.current,
                    slots_remaining=target.slots_remaining,
                    slots_total=target.slots_total,
```

**Second carry site the planner must not forget:** `_alternating_cycle_targets`' complement (`chip_test.py:~1475`), which builds an **unmasked** target (`current_source="address-derived pattern, bit-inverted (cycle complement)"`). It must carry `current_is_probe_read=False` — i.e. it simply does not set the field, and the default does the work.

**Structural-refusal pattern** (`WriteTarget.__post_init__`, `chip_test.py:2390-2413`) — the analog for any fail-closed assertion Q2a decides to add:

```python
        if self.masked and self.bits_cleared < _UV_MIN_CLEARED_BITS:
            raise ValueError(
                f"WriteTarget: masked target clears only {self.bits_cleared} "
                f"bits, below _UV_MIN_CLEARED_BITS ({_UV_MIN_CLEARED_BITS}) "
                "-- this slot is saturated under this pattern"
            )
```

> **Landmine from RESEARCH, restated here because it is the phase's single easiest silent failure:** `current_source == "probe read"` is **false on every real cycle run** — the staged tranche reads `"probe read (tranche 1/2)"`. A witness written as string equality ships green and inert.

---

### 3. `firestarter/chip_test.py` — the UV blank-check verdict (service, request-response)

**Analog:** the arm being edited, `_dispatch_step`, `chip_test.py:2626-2641`. There is no closer analog; this is an in-place shape change, and the pattern is the existing `StepResult(...)` construction.

```python
    if step.op == OP_BLANK_CHECK:
        is_ok = operator.check_eprom_blank(name, eprom_data)
        code, message = (None, "") if is_ok else _firmware_error(operator)
        return StepResult(
            op=step.op,
            verdict=VERDICT_OK if is_ok else VERDICT_BAD,
            reason=message,
            error_code=code,
            run_count=1,
        )
```

Constraints the planner must honor at this site:
- `operator.check_eprom_blank(name, eprom_data)` takes **no** `operation_flags` and must keep taking none — firmware's `CMD_BLANK_CHECK` does not read the bit (`firestarter/src/proms/eprom.cpp:56-58`).
- `run_count=1` is hard-coded and **correct** — `OP_BLANK_CHECK` is not in `_REPEAT_POLICY_OPS`. Do not "fix" it.
- `VERDICT_OK` is **structurally unavailable** for the non-blank UV case: it collides with the frozen `m27c512-full-all-ok` hash `6d3afbc52315`.
- Q1b (how the arm learns the plan is UV) is an open decision; the tree's own precedent is the `Step` additive-field discipline shown in pattern 2 — `derive_plan` decides once, `_dispatch_step` reads.

**The fold this must clear** — `firestarter_app/firestarter/submit.py:164-171`, verbatim. Note the status guard runs **ahead** of the verdict fold, which is why routing through Phase 178's status axis lands on `INCONCLUSIVE (harness)`, not `PASS`:

```python
    if any(getattr(r, "status", STATUS_COMPLETE) == STATUS_ERROR for r in results):
        return _TITLE_VERDICT_HARNESS
    verdicts = {r.verdict for r in results}
    if "BAD" in verdicts:
        return "FAIL"
    if "marginal" in verdicts:
        return "INCONCLUSIVE"
    return "PASS"
```

**Assertion-target pattern** — `overall_verdict` is not a report field. `submit.build_title` (`submit.py:174-186`) is the only thing that reaches the world:

```python
    d = report.to_dict()
    shorthash = d["dedup_fingerprint"]
    verdict = overall_verdict(report.results)
    return f"[dev test] {chip} — {verdict} ({shorthash})"
```

So the regression test asserts `submit.overall_verdict(report.results) == "PASS"`, or `build_title(...)` ending in `— PASS (<hash>)`.

---

### 4. `tests/test_chip_test_uv_slot_write.py` (test, request-response) — **new**

**Analog:** `firestarter_app/tests/test_chip_test_sdp_leg.py`. It is the closest existing "construct a plan, run it against a double, assert on the `StepResult`" module, and it is the right structural precedent for a new leg-focused test module (module docstring carrying a test taxonomy, a local operator-double harness, no syrupy capture, no skip marker).

**Operator-double harness** (`test_chip_test_sdp_leg.py:219-262`, verbatim):

```python
_REAL_DB = EpromDatabase(skip_local_override=True)

_OPERATOR_METHODS = [
    "check_eprom_id",
    "read_eprom",
    "check_eprom_blank",
    "write_eprom",
    "verify_eprom",
    "erase_eprom",
    "sdp_lock",
    "sdp_unlock",
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

`Mock(spec=[...])` is load-bearing: it makes a typo'd operator method an `AttributeError` rather than a silently-`True` `Mock` — the absent-chip false-green family this project refuses.

**Injection-seam pattern** for the UV-03 disagreement legs — `WriteContext.cycle_targets` short-circuits `_resolve_write_target` (`_cycle_target`, `chip_test.py:1330-1345`), so a test hands `_dispatch_multi_run` a hand-built target that disagrees with `step.region_policy`, with **zero probe reads and zero monkeypatching**. Measured working in RESEARCH:

```python
step = ct.Step(op=ct.OP_WRITE, supported=True, reason="", destructive=True,
               write_region=(0xFF00, 256), region_policy=ct.REGION_POLICY_UV_SLOT,
               full_device_permitted=False, cycle_payload=ct.CYCLE_PAYLOAD_UV_TRANCHE)
t = ct.WriteTarget(region=(0xFF00, 256), pattern=ct.generate_pattern(0xFF00, 256),
                   masked=False, bits_cleared=0, bits_retained=0,
                   current_source="address-derived pattern (unmasked)",
                   region_policy=ct.REGION_POLICY_UV_SLOT)
wc = ct.WriteContext(); wc.cycle_targets = [t]; wc.cycle_index = 0
r = ct._dispatch_multi_run(ct.OP_WRITE, name, ed, chip, runs=1, step=step, write_context=wc)
```

Assert on **the flags the double recorded**, not on the verdict. Both directions: policy `uv-slot` + witness absent → flag must **not** be set; policy `fixed` + `masked=True, current=<bytes>, current_is_probe_read=True` → flag **must** be set.

**Named-leg collection proof** (from `178-01-PLAN.md:505`) — pair every new test with it, so a never-collected function cannot read green:

```bash
(cd firestarter_app && ./.venv311/bin/python -m pytest -o addopts="" -q --collect-only tests/test_chip_test_uv_slot_write.py) > /tmp/179-collect.txt 2>&1
for t in test_<name_1> test_<name_2>; do echo "leg_${t}=$(/usr/bin/grep -c "$t" /tmp/179-collect.txt)"; done
```
Fails when any `leg_<name>=0` appears. Pair with `! /usr/bin/grep -q 'no tests ran'` and `! /usr/bin/grep -qE '[0-9]+ (failed|error)'`.

---

### 5. `tests/fake_chip.py` — the firmware-faithful double (test double, transform)

**Analog:** `FakeChip.write_eprom`, `tests/fake_chip.py:133-155`, verbatim:

```python
    def write_eprom(
        self,
        name: str,
        eprom_data: dict[str, Any],
        input_file_path: str,
        operation_flags: int = 0,
        address_str: str | None = None,
        pulse_us: int = 0,
    ) -> bool:
        self.calls.append(("write_eprom", {"address_str": address_str}))
        start = _parse_addr_or_size(address_str) or 0
        incoming = Path(input_file_path).read_bytes()
        end = start + len(incoming)
        if start < 0 or end > self.memory_size:
            return False
        if self.uv:
            existing = bytes(self.data[start:end])
            merged = bytes(c & d for c, d in zip(existing, incoming))
            self.data[start:end] = merged
        else:
            self.data[start:end] = incoming
        return True
```

Two properties a bare `Mock` cannot fake and without which the tests are theatre: **UV AND-physics** (`c & d`) and **absolute-offset addressing**. Subclass — do not re-implement.

**The refusal to add**, mirroring `firestarter/src/proms/eprom.cpp:143-145` exactly (that firmware source, verbatim):

```c
    if (!is_flag_set(FLAG_SKIP_BLANK_CHECK)) {
        mem_util_blank_check(handle);
    }
```

The Python subclass raises `EpromOperationError("…", error_code=0xB0)` when `not (operation_flags & FLAG_SKIP_BLANK_CHECK)` and the device region is not blank. The existing `except EpromOperationError` arm at `chip_test.py:2576-2583` does the rest — **no bespoke exception plumbing.**

> The subclass overrides `write_eprom`, whose parameter is named `operation_flags`. That is *why* the production call must be positional: `tests/test_chip_test.py:1067` and `tests/fixtures/report_shapes.py:432` both name it `flags`. Positional satisfies all three.

---

### 6. `tests/fixtures/report_shapes.py` + friends — registering `uv-slot-write-pass`

**Analog:** Phase 178's registration of `attr01-status-axis-transport-fault`. `uv-slot-write-pass` is the **last** entry in `RESERVED_SHAPE_IDS` (`report_shapes.py:709-713`) and this phase owns it.

**Builder pattern** (`report_shapes.py:643-663`) — a module-level `_build_<slug>()` returning a `DiagnosticReport`, with the whole rationale in the **docstring** (never `#` comments):

```python
def _build_attr01_status_axis_transport_fault() -> DiagnosticReport:
    """The shape D-04 reserved this name for … Uses chip
    `m27c512`, already exercised by a registered all-OK real-path shape
    above, so `derive_plan` coverage is understood rather than novel."""
    operator = _fixed_return_operator()
    operator.check_eprom_id.side_effect = SerialError("synthetic transport fault")
    return _build_real_path_report(
        chip="m27c512", write_scope="full", operator=operator, runs=2
    )
```

> **Do NOT model `uv-slot-write-pass` on `_fixed_return_operator`.** `_build_m27c512_full_all_ok` is a misnomer: its write/verify are `SKIPPED` with `run_count=0`, because `_fixed_return_operator.read_eprom` returns `True` while writing no file, so `_read_region` gets `b""`, every UV slot is unevaluable and `_resolve_write_target` refuses. **No frozen shape in the corpus exercises a real UV masked write.** This builder needs a chip-modelling double — the `FakeChip` subclass from pattern 5, or an `_sdp_aware_operator`-shaped stateful `Mock` (`report_shapes.py:425-445`).

#### The EIGHT gate-enforced edit sites — enumerated so the planner does not rediscover them

All eight land in **ONE commit**. Any partial state is red by construction, because `SHAPE_IDS = tuple(sorted(_BUILDERS))` and a five-way closure test cross-checks every registry. **Ordering within the commit is load-bearing:** `tools/snapshot_report_shapes.py` rejects a `--shape` value absent from `SHAPE_IDS`, so sites 1 and 2 must be on disk before site 3 can be *measured* and before site 8 can be *generated at all*.

| # | Site | File | Edit |
|---|---|---|---|
| 1 | `_build_uv_slot_write_pass()` | `tests/fixtures/report_shapes.py` (`~:643-663` for shape) | new builder fn, docstring-only rationale |
| 2 | `_BUILDERS` | `tests/fixtures/report_shapes.py:665-685` | add `"uv-slot-write-pass": _build_uv_slot_write_pass,` (18 → 19) |
| 3 | `FROZEN_HASHES` | `tests/fixtures/report_shapes.py:688-707` | add the **measured** 12-hex hash (18 → 19) — measure, never predict |
| 4 | `RESERVED_SHAPE_IDS` | `tests/fixtures/report_shapes.py:709-713` | remove `"uv-slot-write-pass"` → the frozenset becomes **empty**; the assert at `:715-718` then guards nothing, so check whether that assert and its docstring at `:22-27` need a prose repair |
| 5 | `LADDER_PINS` | `tests/test_blast_radius_invariance.py:~200-256` | add the entry with its disposition/`ladder_state` pair |
| 6 | `_PINNED_SHAPE_ID_SET` | `tests/test_blast_radius_invariance.py:~534-566` | add in **sorted** position (18 → 19) |
| 7 | `tests/fixtures/shape_ids.json` | `tests/fixtures/shape_ids.json` | add to the committed sorted anchor (18 → 19) |
| 8 | the snapshot | `tests/fixtures/reports/uv-slot-write-pass.json` | **generate** with `./.venv311/bin/python tools/snapshot_report_shapes.py --shape uv-slot-write-pass` — never hand-write |

Plus the **prose repairs**: every hard-coded count sentence (`test_build_shape_raises_for_every_reserved_shape_id`'s count sentence at `~:700-770`, the module docstring at `report_shapes.py:22-27`, `snapshot_report_shapes.py --check`'s expected `18`). Sites 5–7 are two *different* files enforced by two *different* tests — that is why the count is eight, not seven.

**Verify-leg pattern** (adapt `178-03-PLAN.md`'s block, bumping every `18` to `19`): three `rc=0` legs, plus `shape_count=19`, `snapshot_count=19`, `pinned_set_len=19`, `pinned_set_matches=True`, `anchor_matches=True`, `registered=True`, `unreserved=True`, `reserved_left=` (now **empty** — Phase 178's line read `reserved_left=uv-slot-write-pass`; this phase inverts it), `inherited_count=18`, `inherited_drifted=` empty, `new_hash=[0-9a-f]{12}`.

---

### 7. `tests/fixtures/rekey_ledger.py` + `.planning/MILESTONES.md:39` (ledger, batch)

**Analog:** the two already-declared rows, `RK-174-01` (`rekey_ledger.py:28-45`) and `RK-174-05` (`:70-80`). This phase's row is **pre-seeded and waiting** at `rekey_ledger.py:149-154`:

```python
    (
        "m27c512-full-blank-check-bad",
        "077a32d1a5c4",
        None,
        "RK-174-04-p179-uv-blank-check-abort",
    ),
```

**Declaration pattern:** fill the third slot (`after_hash`) with the **measured** post-change hash and update the bound `.planning/MILESTONES.md:39` row **in the same commit**. `tools/rekey/check_rekey_ledger.py` binds them; either alone fails.

**Module constraints** (`rekey_ledger.py:1-20`): plain four-tuples, **no dataclass, no enum, no computed expression** — the meta-side checker uses `ast.parse` + `ast.literal_eval` rather than importing. Append, never edit prior rows; `before_hash` never leaves the tree.

**Ledger discipline (Phase 178 D-09):** declaring a **non-move** is a bookkeeping error. `after_hash` stays `None` unless the hash genuinely moved. `tests/test_rekey_ledger.py` enforces both directions (`test_no_declared_row_has_after_hash_equal_to_before_hash` at `:332`, `test_undeclared_after_hash_routes_to_before_hash_and_never_abstains` at `:358`), and pins the row count and ascending ids at `:290-400`.

**Checker invocation — from `/workspaces`, NOT from the submodule** (running it from `firestarter_app/` gives `Errno 2`):

```bash
python3 tools/rekey/check_rekey_ledger.py
```

Projections to re-measure before freezing (`SKIPPED` → `e42f1567967a`, `NA` → `559bb7d81a92`); `OK` → `6d3afbc52315` is **structurally unavailable** (collides with `m27c512-full-all-ok`).

---

### 8. `179-MEASUREMENT.md` — the bench artifact (record, batch)

**Analog:** `.planning/phases/176-*/176-MEASUREMENT.md` (Phase 176-05 precedent). The `blocking-human` bench wave produces a committed measurement artifact.

Constraints to encode: **chip seating and removal are OPERATOR-ONLY** (Claude can drive the serial port and CLI but cannot handle a chip); a UV write is **physically irreversible** and the operator has **no UV eraser**, so the plan must budget slots explicitly; `ttyACM*` numbers shuffle across replug, so verify `controller:` identity per port each task. Recommended part is `m27c512` (the CLI token; "ST M27C512" does not resolve). **`am27c020` is not recommended** — its 0x08 write path is recorded marginal on this bench, and a failure there would be uninterpretable.

---

## Shared Patterns

### Positional flags
**Source:** `chip_test.py:3437-3443`
**Apply to:** every `operator.write_eprom(...)` call this phase touches.
Pass `operation_flags` as the bare **4th positional** argument. Two of three write-capable doubles name it `flags` (`tests/test_chip_test.py:1067`, `tests/fixtures/report_shapes.py:432`); a keyword call lands in `**_kw` on both and silently leaves the flag at `0` — a no-op that passes every assertion about the *result*.

### No flags dict — the orchestrator gate
**Source:** `firestarter_app/tools/check_devtest_orchestrator.py`
**Apply to:** `chip_test.py`, `cli_handlers.py`, `submit.py`.
A dict literal whose keys intersect the wire vocabulary (`flags` included) is banned. A bare positional int is compliant. Separately: any new `dev_test` helper added to `cli_handlers.py` **must** be added to `_HANDLER_FUNCTION_NAMES` (`check_devtest_orchestrator.py:152-164`) or the gate silently does not scan it — **it fails open.**

### Docstring-carried rationale
**Source:** `WriteTarget` (`chip_test.py:2329-2347`), `overall_verdict` (`submit.py:150-163`), `test_chip_test_sdp_leg.py:1-70`
**Apply to:** every file this phase touches.
This tree carries its reasoning in **docstrings**, and only where docstrings already exist. Hard rule 1 forbids `#` comments absolutely. Where an excerpt above shows a comment, the comment is *context for you*, not a pattern to copy.

### Don't hand-roll
| Problem | Don't build | Use instead |
|---|---|---|
| a UV chip model for tests | a fresh `Mock` | `tests/fake_chip.py` `FakeChip` (UV AND-physics + absolute-offset reads) |
| the firmware refusal in a test | bespoke exception plumbing | a `FakeChip` subclass raising `EpromOperationError(..., error_code=0xB0)`; `chip_test.py:2576-2583` does the rest |
| injecting a write target | monkeypatching `_resolve_write_target` | `WriteContext(cycle_targets=[t])` |
| a frozen-shape snapshot | hand-written JSON | `tools/snapshot_report_shapes.py` |
| declaring a re-key | editing `FROZEN_HASHES` alone | `rekey_ledger.py` `after_hash` **and** the bound `MILESTONES.md` row, one commit |
| computing a wire flag | a new helper | the SDP leg's inline positional int |

### Per-commit hygiene block
**Source:** `178-01-PLAN.md:436`. Copy verbatim; it enforces hard rules 1, 2, 5 and 6 at once (`phase_added_comments=0`, generated-DB clean, `.venv311`, `/usr/bin/grep`, firmware submodule clean):

```bash
cd /workspaces/firestarter_app && test "$(git diff HEAD~1 -- firestarter/ tests/ | /usr/bin/grep -E '^\+' | /usr/bin/grep -vE '^\+\+\+' | /usr/bin/grep -vE '^\+[[:space:]]*["'"'"']' | /usr/bin/grep -cE '^\+[[:space:]]*#')" -eq 0 && ./.venv311/bin/python -m ruff check firestarter/ tests/ && ./.venv311/bin/python -m ruff format --check firestarter/ tests/ && ./.venv311/bin/python tools/check_mypy_watermark.py | /usr/bin/grep -qx 'mypy errors: 35 (watermark: 35)' && test -z "$(git -C /workspaces/firestarter status --porcelain)" && test -z "$(git status --porcelain firestarter/data/chip_database.json)"
```

### Phase-seal gate set
**Source:** `178-04-PLAN.md:389`. Eight `rc=0` legs — ruff check, ruff format, mypy watermark, `snapshot_report_shapes.py --check`, `check_devtest_orchestrator.py`, `check_diagnostic_report_claims.py`, `check_rekey_ledger.py` (from `/workspaces`), full suite. Plus `firmware_diff=clean`, `chip_database_diff=clean`, `app_tree=clean`, `phase_added_comments=0`, and a `full_suite_passed >= 2241` floor. Note `test_flash_path_record_sync` asserts whole-repo porcelain — **commit before running the full suite**; and `pytest` addopts are `-ra -q`, so a count line needs `-o addopts=""`.

### Submodule commit discipline
Executors commit **inside** `firestarter_app` (and `firestarter`, if it were touched — it is not) on the milestone branch `gsd/v1.36-dev-test-fidelity`, then the meta repo advances the gitlink. Both submodules are on that branch and clean as of research.

---

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| a hardware-gated pytest test (Q4/R2 route only) | test | request-response | **There is no hardware-gated pytest test in this repo.** `ALLOWED_SKIP_REASONS` (`tests/test_skip_census.py:114-140`) has exactly four entries and **none** is board- or chip-presence. If the planner takes R2, it must add a fifth entry with no precedent to copy — and inherits a permanently-dormant CI assertion, the "fixture-passing selftests ≠ working tooling" failure this project has already recorded. **R1 (committed firmware-faithful-double test + `blocking-human` bench artifact) is the recommended split, and A2 makes it an assumption the operator must confirm.** |
| `179-MEASUREMENT.md` | record | batch | role-match only (`176-MEASUREMENT.md`); the content is bench-specific and has no structural analog for a UV slot budget. |

---

## Open decisions the planner must surface (from RESEARCH, unresolved — there is no CONTEXT.md)

Each is `[ASSUMED]` and must appear as a named assumption or a `checkpoint:decision`. Pattern mapping does **not** resolve any of them; it only records which analog each choice would follow.

| # | Decision | Pattern consequence |
|---|---|---|
| Q1 | What a non-blank UV `blank-check` step *means* | Option B (execution-time verdict) uses pattern 3 and leaves `plan_shapes.json` byte-unchanged; Option A re-keys 301 chips and reddens `test_chip_test_blank_check_order.py::test_am27512_uv_blank_check_position_is_unchanged` |
| Q1a | `NA` vs `SKIPPED` | `NA` renders `""` / `-` and **destroys the finding**; `SKIPPED` preserves it (A3 prefers `SKIPPED`) |
| Q1b | how `_dispatch_step` learns the plan is UV | pattern 2's additive-field discipline, on `Step` rather than `WriteTarget` |
| Q2 | the exact witness form | pattern 2's new structural field is the only form that is both live and fail-closed |
| Q2a | a separate positive fail-closed assertion | `WriteTarget.__post_init__`'s `raise ValueError` shape (pattern 2) |
| Q3 | inline vs `build_flags` | A4 takes the SDP-leg inline precedent; conflicts with `PITFALLS.md:449` — record the choice |
| Q4 | how criterion 4 is satisfied | see **No Analog Found** — the largest open decision |
| Q5 | a report disclosure key | A5 defers to Phase 181; would touch `diagnostic_report.py`, currently out of scope |
| Q7 | does `MSG_ERR_NOT_BLANK` propagation survive | `tests/test_devtest_firmware_error_propagation.py` will have an opinion |
| Q8 | bundle the stale UV-prompt comment deletion (`cli_handlers.py:2295-2303`) | the fix is **deletion**, never a rewritten comment (hard rule 1) |

---

## Metadata

**Analog search scope:** `firestarter_app/firestarter/`, `firestarter_app/tests/`, `firestarter_app/tools/`, `firestarter/src/proms/`, `firestarter/include/`, `.planning/phases/178-*/`
**Files read this session:** 11 (targeted, non-overlapping ranges)
**Tracked-source gate:** every analog path verified with `git ls-files` from within its owning submodule. No gitignored mirror paths emitted. `firestarter_app/build/lib/firestarter/` is a stale build artifact and is explicitly excluded.
**Pattern extraction date:** 2026-09-06
