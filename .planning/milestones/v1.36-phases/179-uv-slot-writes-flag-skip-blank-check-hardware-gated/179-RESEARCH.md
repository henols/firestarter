# Phase 179: UV Slot Writes — `FLAG_SKIP_BLANK_CHECK` (hardware-gated) - Research

**Researched:** 2026-09-06
**Domain:** `firestarter_app` `dev test` engine (`chip_test.py`) — UV masked slot writes, wire-flag emission, verdict adjudication, dedup blast radius
**Confidence:** HIGH for every call chain and measurement below (all measured in-tree this session with `firestarter_app/.venv311`); MEDIUM for the bench-part availability question, which is an operator fact this research can only bound.

**There is NO CONTEXT.md for this phase** — the operator chose to plan without one. Every design gray area is recorded under `## Open questions / decisions the planner must make explicit`, and the planner must surface each as an explicit assumption or a `checkpoint:decision`.

---

## Summary

Phase 179 has **two independent defects to fix, not one**, and both were measured end to end this session against a firmware-faithful double. First, `_dispatch_multi_run` calls `operator.write_eprom(...)` with **no** `operation_flags` argument (`firestarter_app/firestarter/chip_test.py:3189-3193`), so `FLAG_SKIP_BLANK_CHECK` (`0x08`) is never on the wire and the firmware's write-init pre-flight (`firestarter/src/proms/eprom.cpp:143-145`) refuses the write on a non-blank UV part; that refusal carries an `error_code`, which trips `hardware_refused` (`chip_test.py:1648-1652`) and aborts cycle 2, collapsing `run_count` to 1. Second — and this is the half a "the write went OK" criterion would miss — the plan's own **standalone `blank-check` step** returns `VERDICT_BAD` on a non-blank UV part (`chip_test.py:2626-2641`), and `submit.overall_verdict` is FAIL-dominant on any `BAD` (`submit.py:164-171`), so the title reads `FAIL` even when the write and verify are green.

**One prior claim is falsified.** `.planning/research/PITFALLS.md:186-188` states that the standalone blank-check's `error_code` is what trips `hardware_refused` and aborts cycle 2. It does not: for a UV plan the blank-check sits at index 2, **outside** the cycle block, which is `(3, 6)` — measured for `m27c512`, `am27c020` and `tms27c512`. The abort comes from the **write step's own** firmware refusal. The consequence for the plan is the same (both must be fixed) but the mechanism the planner must instrument is different, and `RK-174-04`'s recorded mechanism ("the `blank-check` verdict triple moving from OK to BAD") is the accurate one.

**A second prior claim is falsified.** The milestone research prescribes the witness as `target.masked and target.current is not None and target.current_source == "probe read"` (`.planning/research/SUMMARY.md:89`). Exact equality **fails on every real cycle run**: the staged tranche targets that actually reach `write_eprom` carry `current_source == "probe read (tranche 1/2)"` (`chip_test.py:1518`). Measured. A witness written that way would silently never fire, and the phase would ship green and inert.

The change is **host-only**: the firmware already honours the flag at write-init and needs no edit. The blast radius is one frozen report shape (`m27c512-full-blank-check-bad`, ledger row `RK-174-04-p179-uv-blank-check-abort`, pre-seeded and waiting) plus the registration of the last reserved shape id, `uv-slot-write-pass`, across the eight gate-enforced sites Phase 178 exercised. There is **no precedent in this repo for a hardware-gated pytest test** — zero of `ALLOWED_SKIP_REASONS`' four entries is board-presence — so criterion 4 needs an explicit route, and that is the single largest open decision.

**Primary recommendation:** derive the flag from a **structural** monotonicity witness (not a string compare, not `region_policy`), pass it **positionally** as the fourth argument to `write_eprom`, adjudicate the UV blank-check verdict at **execution time** (not by flipping `Step.supported` in `derive_plan`, which re-keys `plan_shapes.json` for 301 chips), and split criterion 4 into a committed firmware-faithful-double regression test that runs in CI plus a `blocking-human` bench wave on the ST M27C512 that produces a committed measurement artifact.

---

## What UV-01/02/03 actually require

### UV-01 — "A UV part holding data outside the target slot accepts a slot write."

| | |
|---|---|
| **State today** | **BROKEN on real hardware.** `chip_test.py:3186-3194` calls `operator.write_eprom(name, eprom_data, tmp_source_path, address_str=...)` — `operation_flags` defaults to `0` (`eprom_operations.py:1967-1975`). The firmware's `eprom_internal_write_init_body` then runs `mem_util_blank_check(handle)` unconditionally (`firestarter/src/proms/eprom.cpp:143-145`) and emits `MSG_ERR_NOT_BLANK` (`0xB0`, `firestarter/include/messages.h:93`). |
| **What must change** | One call site: add the flag as a positional 4th argument, gated on the witness. |
| **Firmware change needed?** | **No.** `eprom.cpp:143-145` already reads the bit. Verified. |
| **Blind spot today** | `tests/fake_chip.py:133-153` — `FakeChip.write_eprom` models UV AND-physics but **not** the firmware pre-flight refusal, so the entire suite is blind to UV-01. This is why criterion 4 says "no such test exists today." |

### UV-02 — "`overall_verdict == "PASS"` with `run_count == 2`."

**MEASURED baseline, real-hardware shape** (in-tree simulation, `m27c512`, `write_scope="full"`, `runs=2`, non-blank at `0x0000-0x00FF`, target slot `0xFF00`, using a `FakeChip` subclass that refuses a non-blank write unless the flag is set — exactly `eprom.cpp:143-145`):

```
  id             verdict=OK        run_count=1 err=None
  read           verdict=OK        run_count=2 err=None
  blank-check    verdict=BAD       run_count=1 err=161 reason='Not blank'
  write          verdict=BAD       run_count=1 err=161 reason='Not blank'
  verify         verdict=SKIPPED   run_count=0 err=None reason='Not blank'
overall_verdict: FAIL
```

**MEASURED with the flag passed on the witness** (same run, witness gate simulated at the write call site):

```
  blank-check    verdict=BAD       run_count=1 err=161
  write          verdict=OK        run_count=2 err=None
  verify         verdict=OK        run_count=2 err=None
write flags seen: ['0x8', '0x8']
overall_verdict: FAIL          <-- STILL FAIL
```

So the flag alone buys `run_count == 2` and nothing else. `overall_verdict` stays `FAIL` because `submit.overall_verdict` folds every result and any `BAD` wins (`firestarter_app/firestarter/submit.py:164-171`, verbatim):

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

**Three consequences the planner must internalise:**

1. **`overall_verdict` is not a report field.** It is `submit.overall_verdict(report.results)` and reaches the world only through the issue title (`submit.build_title`, `submit.py:174-186`). `DiagnosticReport.to_dict()` (`diagnostic_report.py:893-907`) has `run_status`, not `overall_verdict`. The regression test's assertion target is `submit.overall_verdict(report.results) == "PASS"`, or `build_title(...)` ending in `— PASS (<hash>)`.
2. **Phase 178's status axis is NOT the route to PASS.** Any result carrying `STATUS_ERROR` returns `INCONCLUSIVE (harness)` — the guard at `submit.py:165` runs *ahead* of the verdict fold. Routing the UV blank-check through the status axis produces `INCONCLUSIVE (harness)`, which is not `PASS`. What Phase 178 actually gave this phase is the **vocabulary and the precedent** (an additive axis, kept out of the hash), not a mechanism that lands on PASS.
3. **`PASS` requires the blank-check step's `verdict` to be one of `OK` / `NA` / `SKIPPED`** — nothing else clears the fold. That is a design decision with no obviously-correct answer; see the Open Questions.

**`run_count` semantics.** `_aggregate_cycle_results` sets `run_count=len(ran)` where `ran` is the cycles that reached the operator (`chip_test.py:1346-1396`, the assignment at `:1395`). It is a **per-step** field; UV-02's `run_count == 2` means the write step's (and the verify step's). The blank-check step is hard-coded `run_count=1` (`chip_test.py:2640`) and is not in `_REPEAT_POLICY_OPS` (`chip_test.py:1139`), so that is correct and must not be "fixed."

### UV-03 — "The `FLAG_SKIP_BLANK_CHECK` pass is witness-form — not gated on `region_policy`."

The safety argument is monotonicity: `mask_write_pattern` computes `P = C & D` per byte, which can only clear `1 → 0`, and that property holds **only because `C` is a real probe read of the exact target region**. `region_policy == "uv-slot"` and "the mask came from a probe read" are *currently* coextensive but are not the same predicate — and were provably not coextensive one design iteration ago (the retired D-C "chip reported blank → mask taken as all-`0xFF`, device never read again" branch, whose removal is recorded at `chip_test.py:2905-2917`). Applying the skip to a target whose `current` was **assumed** rather than read is a non-monotone write on a part the operator has no eraser for.

**The witness's raw materials, all on `WriteTarget` (`chip_test.py:2327-2413`):**

| Field | Set where | Value on a real UV cycle write |
|---|---|---|
| `masked: bool` | `chip_test.py:2959` (probe), `:1515` (tranche) | `True` |
| `current: bytes` | `chip_test.py:2963` (probe), `:1521` (tranche, carried through) | the 256 probed bytes |
| `current_source: str` | `chip_test.py:2962` = `"probe read"` | **`"probe read (tranche 1/2)"`** — see `chip_test.py:1518` |
| `bits_cleared` / `bits_retained` | `:2960-2961`, `:1513-1514` | ≥ `_UV_MIN_CLEARED_BITS` (64) each |
| `region_policy` | carried from `Step.region_policy` | `"uv-slot"` |

The four `current_source` literals in the tree, verbatim:

- `chip_test.py:2962` — `current_source="probe read",` (`masked=True`, `current` set)
- `chip_test.py:1518` — `current_source=f"{target.current_source} (tranche {cycle}/{cycles})",` (`masked=True`, `current` carried)
- `chip_test.py:2892` — `current_source="address-derived pattern (unmasked)",` (`masked=False`, `current=b""`)
- `chip_test.py:1475` — `current_source="address-derived pattern, bit-inverted (cycle complement)",` (`masked=False`, `current=b""`)

**MEASURED**, `_plan_cycle_targets("m27c512", …, cycles=2)` on a probed UV part:

```
0 ((65280, 256), masked=True, 'probe read (tranche 1/2)', len(current)=256, 'uv-slot')
1 ((65280, 256), masked=True, 'probe read (tranche 2/2)', len(current)=256, 'uv-slot')
```

So `current_source == "probe read"` is **false on every real run**. `masked and bool(current)` is true on exactly the two probe-derived shapes and false on both unmasked shapes — but it would also be true for the retired D-C branch if it ever returned, which is the exact case the witness exists to refuse. That tension is the phase's one genuinely open design question.

---

## Call chains

### 1. `FLAG_SKIP_BLANK_CHECK` — definition and every consumer

**Host:**
- `firestarter_app/firestarter/constants.py:122` — `FLAG_SKIP_BLANK_CHECK = 0x08`
- `firestarter_app/firestarter/eprom_operations.py:286-287` — the ONE place the bit is mapped from a boolean:
  ```python
        if not blank_check:
            flags |= FLAG_SKIP_BLANK_CHECK
  ```
  (inside `build_flags`, `eprom_operations.py:269-308`; its own comment insists every wire-flag bit stays mapped here)
- `firestarter_app/firestarter/serial_comm.py:632` — debug-log rendering only
- `firestarter_app/firestarter/cli_handlers.py:298-340` — `_build_op_flags(blank_check=…)`, the `write`/`erase` CLI route

**Firmware** (`firestarter/`, protocols `0x07`/`0x08`/`0x0B` → `configure_eprom`, per `include/proto_constants.h:13-15` and `src/proms/memory.cpp:108-111`):
- `include/firestarter.h:139` — `#define FLAG_SKIP_BLANK_CHECK 0x08`
- `src/proms/eprom.cpp:143-145` — **the write-init pre-flight**:
  ```c
      if (!is_flag_set(FLAG_SKIP_BLANK_CHECK)) {
          mem_util_blank_check(handle);
      }
  ```
- `src/proms/eprom.cpp:51-54` — `CMD_ERASE`'s end-op blank-check (**unreachable for UV**: `derive_plan` marks erase NA for UV, `chip_test.py:797-798`)
- `src/proms/eprom.cpp:56-58` — **`CMD_BLANK_CHECK` does NOT read the flag**:
  ```c
          case CMD_BLANK_CHECK:
              handle->firestarter_operation_main = mem_util_blank_check;
              break;
  ```
- Non-EPROM families that read it: `src/proms/flash_nor_unlock.cpp:104`, `src/proms/flash_intel.cpp:94`. Out of scope for UV.
- `src/proms/memory.cpp:487` — `LOG_ERROR_ID_BYTES(MSG_ERR_NOT_BLANK, _b, 4)`; `MSG_ERR_NOT_BLANK` is `0xB0` (`include/messages.h:93`).

**Answer to research question 1: UV-02's claim is CONFIRMED at the firmware level.** The flag governs the write-init pre-flight and the erase end-op only. A standalone `CMD_BLANK_CHECK` is structurally unskippable by this bit.

### 2. The standalone `blank-check` step — emission, verdict, and what it does NOT do

**Emission** (`derive_plan`, `chip_test.py:684-725`). Case 4 of a four-case ladder: everything not SRAM/FRAM and not auto-erase-on-write, **including UV-EPROM**, gets `Step(op=OP_BLANK_CHECK, supported=True, reason="")` at `chip_test.py:720`, appended at `chip_test.py:725` — *before* the write, because `erase_is_executable` is False for UV (`chip_test.py:681`). The in-source rationale at `chip_test.py:695-698` states the intent verbatim: *"Everything else, including UV-EPROM -- supported, at this position. UV keeps it here deliberately: the write is irrecoverable and only UV light erases, so 'not blank' is a real pre-write finding."*

**MEASURED plan order** (`m27c512`, `am27c020`, `tms27c512`, all `write_scope="full"`, all `is_uv=True`):

```
[('id', True), ('read', True), ('blank-check', True), ('write', True), ('verify', True),
 ('erase', False), ('write-baseline-b', False), ... six SDP steps, all False]
cycle_block: (3, 6)
```

**Verdict** (`_dispatch_step`, `chip_test.py:2626-2641`):

```python
    if step.op == OP_BLANK_CHECK:
        is_ok = operator.check_eprom_blank(name, eprom_data)
        ...
        code, message = (None, "") if is_ok else _firmware_error(operator)
        return StepResult(
            op=step.op,
            verdict=VERDICT_OK if is_ok else VERDICT_BAD,
            reason=message,
            error_code=code,
            run_count=1,
        )
```

Note `operator.check_eprom_blank(name, eprom_data)` — **no `operation_flags`** either, which is correct and must stay: the flag would be ignored by the firmware anyway (`eprom.cpp:56-58`).

**Where the abort actually happens** — `_run_cycle_block`, `chip_test.py:1648-1652`:

```python
                if result.error_code is not None:
                    hardware_refused = True
            if hardware_refused:
                break
```

`_CYCLE_BLOCK_OPS` (`chip_test.py:1292-1294`) does contain `OP_BLANK_CHECK`, but `cycle_block_bounds` (`chip_test.py:1302-1330`) requires the block to **start** at a write op (`_CYCLE_BLOCK_START_OPS`, `chip_test.py:1299`) and to be contiguous. The in-source comment at `chip_test.py:1288-1291` says so explicitly: *"…which is what keeps a UV plan's pre-write blank-check (emitted BEFORE the write, deliberately, as a once-only operator-actionable finding) outside the cycle while an erasable plan's post-erase blank-check lands inside it."*

`run_plan`'s per-step path (`chip_test.py:1826-1854`) has **no `hardware_refused` mechanism at all**; a BAD blank-check there only sets `write_context.chip_is_blank = False` (`chip_test.py:1846-1854`).

> **[VERIFIED: measured this session]** For a UV plan the standalone blank-check runs on the per-step path and **cannot** trip `hardware_refused`. `.planning/research/PITFALLS.md:186-188` step 2 is falsified as written; `RK-174-04`'s own provenance note in `firestarter_app/tests/fixtures/rekey_ledger.py:56-65` already carries the corrected mechanism. **Phase 178 changed nothing on this path** — `error_code` is still set at `chip_test.py:2639`, exactly as before.

### 3. `run_count`, the cycle, and `overall_verdict`

- `run_plan(plan, operator, db, runs=2)` — `chip_test.py:1663-1671`; `runs < 2` fails the whole plan unless `allow_single_run=True` (`chip_test.py:1710-1725`).
- `cycle_block_bounds(plan.steps)` — `chip_test.py:1786`; for UV = `(3, 6)` (write, verify, erase-NA).
- `_run_cycle_block(..., cycles=runs)` — `chip_test.py:1541-1662`. Pre-gates unsupported → NA and gated-destructive → SKIPPED once (`:1581-1588`), then loops cycles, breaking on `hardware_refused`.
- `_plan_cycle_targets` — `chip_test.py:1404-1457`; resolves the target **once** before cycle 1 and stages `_uv_cycle_targets` tranches for `CYCLE_PAYLOAD_UV_TRANCHE` (`:1443-1446`).
- `_aggregate_cycle_results` — `chip_test.py:1346-1396`; `run_count=len(ran)` at `:1395`, `error_code`/`reason` are the first non-empty (`:1391-1393`).
- `repeat_policy_tag` — `chip_test.py:1147-1164`; fires only on `run_count == 1` for a `_REPEAT_POLICY_OPS` member, appending `REPEAT_POLICY_DEGRADED_TAG` into the dedup hash. **A firmware-refused write today reads `run_count == 1` and therefore silently degrades an accurate run's dedup group.**
- `submit.overall_verdict` — `submit.py:149-171`; status-axis guard, then FAIL-dominant fold.
- `_dev_test_exit_code` — `cli_handlers.py:2132-2165`; precedence-map based, not `max()`.

### 4. The write call site to change, and its precedent

**Target** — `chip_test.py:3186-3194`:

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

`resolved_target` is in scope at this point (assigned at `chip_test.py:3123` or `:3126-3135`), so the witness is available with zero new plumbing.

**Precedent** — the SDP leg already passes flags **positionally** through the same operator method, `chip_test.py:3437-3443`:

```python
        wrote_ok = operator.write_eprom(
            name,
            eprom_data,
            tmp_source_path,
            flags,
            address_str=_address_arg(region_start),
        )
```

> **[VERIFIED: measured this session]** Positional is not a style choice, it is **load-bearing**. Two of the three write-capable test doubles name that parameter `flags`, not `operation_flags`:
> - `tests/fake_chip.py:133-139` — `def write_eprom(self, name, eprom_data, input_file_path, operation_flags=0, address_str=None, pulse_us=0)`
> - `tests/test_chip_test.py:1067` — `def _write_eprom(name, eprom_data, source_path, flags=0, address_str=None, **_kw):`
> - `tests/fixtures/report_shapes.py:432` — `def _write_eprom(name, eprom_data, source_path, flags=0, address_str=None, **_kw):`
>
> A keyword call `operation_flags=…` would land in `**_kw` on two of the three, leaving `flags` at `0` — a silent no-op that passes every assertion about the *result*. Pass it positionally.

### 5. `region_policy` — where it is decided and read

- Constants: `chip_test.py:422-424` — `REGION_POLICY_FIXED = "fixed"`, `REGION_POLICY_FULL_DEVICE = "full-device"`, `REGION_POLICY_UV_SLOT = "uv-slot"`.
- Decided **once**, in `derive_plan`, `chip_test.py:608-643`; UV takes `chip_test.py:614-621`. `Plan.is_uv` comes from `is_uv_eprom(full)` — `chip_test.py:506-519`, whose body is `return full.get("electrical-type", "") == "UV-EPROM"` and whose docstring warns that the `algorithm == 0x0B` proxy matches only 32 of 301 UV parts.
- Read at execution time in `_resolve_write_target`, `chip_test.py:2881-2883`:
  ```python
      region_policy = step.region_policy if step is not None else REGION_POLICY_FIXED

      if region_policy != REGION_POLICY_UV_SLOT:
  ```
  This is the **only** branch keyed on the policy string. UV-03 forbids adding a second one for the flag.
- Also read by `_dispatch_multi_run`'s verify arm (`chip_test.py:3146-3148`), by `coverage_tag` (`chip_test.py:1173-1195`, structurally via `result.write_target`), and by `_write_coverage_line` (`diagnostic_report.py:547-600`).

### 6. Report surface already carrying the provenance

`diagnostic_report._step_dict`, `:838-843` — five write-target keys already exported per step, including:

```python
            "write_current_source": target.current_source if target else None,
            "write_coverage": _write_coverage_line(result, step),
```

So a triager can already read `"probe read (tranche 1/2)"` off a filed report. Whether the *flag* itself gets a disclosure key is an open question (below).

---

## Blast radius — dedup hashes and frozen artifacts

### `dedup_fingerprint` inputs

`diagnostic_report.py:263-310`. The hash input is an explicit allow-list — chip name, protocol, then per step `f"{result.op}={result.verdict}:{cls}"` (`:290-291`), then `repeat_policy_tag` and `coverage_tag` when non-empty. **Additive fields cannot move it**; a **verdict** change moves it.

**Two of this phase's likely changes move hashes:**

| Change | Moves the hash? | Why |
|---|---|---|
| Passing `FLAG_SKIP_BLANK_CHECK` on the write | **No** — flags are not hashed | but see next row |
| Write `run_count` 1 → 2 on a refused run | **Yes, indirectly** | `repeat_policy_tag` stops firing (`chip_test.py:1161`) |
| UV blank-check verdict `BAD` → anything else | **Yes** | the `op=verdict:cls` triple at `:291` |
| A new exported `write_flags`/disclosure key | **No** | not in the allow-list |
| `Step.supported` flipped for UV blank-check | **Yes**, plus `plan_shapes.json` | verdict becomes `NA`, and the plan-shape family changes |

### Baseline, MEASURED this session (all 18 shapes reproduce their frozen values)

```
OK  at28c256-full-all-ok-sdp        050ad3830704     OK  m27c512-full-runs-1            e4838f7bb1d3
OK  attr01-status-axis-transport-fault 93cef8030c40  OK  prune03-synthesized-fingerprint-match 3b83a55efb3a
OK  gh20-at28c256-fail              00e121446ceb     OK  sst27sf512-full-all-ok         14d306256076
OK  gh23-w27e257-fail               7a89fcea856a     OK  sst27sf512-six-step            7fb88e0b07d6
OK  gh28-m27c512-fail               31547956e56b     OK  sst27sf512-six-step-readback-gated ff974e416dca
OK  gh47-sst27sf512-pass            f9dbc31dcd27     OK  synthetic-arm4-empty-results   8d6208d00be7
OK  m27c512-full-all-ok             6d3afbc52315     OK  synthetic-arm4-no-ok           f90dfe1a44f7
OK  m27c512-full-blank-check-bad    077a32d1a5c4     OK  w27e257-full-all-ok            3a9f95aba65e
OK  m27c512-full-canonical-name     776846bf2dc8
OK  m27c512-full-comma-joined-name  37ad34d39a19
```

### The pre-seeded ledger row this phase owns

`firestarter_app/tests/fixtures/rekey_ledger.py:149-154`, verbatim:

```python
    (
        "m27c512-full-blank-check-bad",
        "077a32d1a5c4",
        None,
        "RK-174-04-p179-uv-blank-check-abort",
    ),
```

Its provenance note (`rekey_ledger.py:56-65`) states the mechanism correctly and names Phase 179 as owner. The bound `MILESTONES.md` row is `.planning/MILESTONES.md:39`. The checker is `tools/rekey/check_rekey_ledger.py`, run **from `/workspaces`** (it is not under `firestarter_app/tools/`), and today prints `OK: 8 ledger row(s), 8 MILESTONES.md row(s) bound`.

**Ledger discipline inherited from Phase 178 D-09:** declaring a non-move is a bookkeeping error — `after_hash` stays `None` unless the hash actually moved. `tests/test_rekey_ledger.py` enforces both directions.

### MEASURED projections for the `m27c512-full-blank-check-bad` shape

Its current step triples are `[('id','OK',1), ('read','OK',2), ('blank-check','BAD',1), ('write','SKIPPED',0), ('verify','SKIPPED',0)]`. Mutating only the blank-check verdict:

| blank-check verdict | resulting `dedup_fingerprint` |
|---|---|
| `BAD` (today) | `077a32d1a5c4` |
| `NA` | `559bb7d81a92` |
| `SKIPPED` | `e42f1567967a` |
| `OK` | `6d3afbc52315` — **collides with `m27c512-full-all-ok`** |

> **[VERIFIED: measured this session]** Re-measure before freezing — these are mutation projections over the existing report object, not builds through a modified `derive_plan`/`run_plan`. But the **collision under `OK` is structural**: `m27c512-full-all-ok` and `m27c512-full-blank-check-bad` differ in *nothing but* the blank-check verdict, so choosing `OK` would make two frozen corpus entries hash-identical and redden the distinctness assertion in `tests/test_blast_radius_invariance.py`. **`OK` is not available.**

### `plan_shapes.json` — the second, larger frozen surface

`firestarter_app/tests/fixtures/plan_shapes.json`, generated by `tools/measure_plan_shapes.py`, guarded by `tests/test_plan_shapes_drift.py`. It keys each of 677 chips onto one of 8 families named by `(op, supported)` — e.g. `id-bcpre-eraseNA-sdpNA` (180 chips) vs `id-bcpreNA-eraseNA-sdpNA` (27 chips). Aggregates pinned absolutely: `distinct_part_numbers: 677`, `distinct_shape_families: 8`, `plans: 1354`, `rows: 746`, `total_steps: 16248`, `unsupported_steps: 9304`.

> **[VERIFIED: tests/fixtures/plan_shapes.json, measured this session]** Flipping the UV blank-check step to `supported=False` in `derive_plan` moves **all 301 UV chips** from a `bcpre` family to a `bcpreNA` family, changing `unsupported_steps`, every affected `chips` entry and every affected `chip_count`. Adjudicating the verdict at **execution time instead** leaves `plan_shapes.json` byte-unchanged, because it is derived from `derive_plan` alone.

### The last reserved shape id

`tests/fixtures/report_shapes.py:709-713`:

```python
RESERVED_SHAPE_IDS: frozenset[str] = frozenset(
    {
        "uv-slot-write-pass",
    }
)
```

`uv-slot-write-pass` is Phase 179's, and it is the only reservation left. Phase 178's plan 178-03 established the protocol: registering a reserved id is an **eight-gate-enforced-site, single-commit** operation — `_BUILDERS`, `FROZEN_HASHES`, removal from `RESERVED_SHAPE_IDS`, `LADDER_PINS`, `_PINNED_SHAPE_ID_SET`, `tests/fixtures/shape_ids.json`, the generated `tests/fixtures/reports/<id>.json` snapshot, plus the prose repairs. Any partial state is red by construction because `SHAPE_IDS` derives from `_BUILDERS`. Snapshots are generated by `tools/snapshot_report_shapes.py` (`--check` verifies), never hand-written.

> **[VERIFIED: tests/fixtures/report_shapes.py:383-403, measured this session]** The default double will not work for this shape. `_build_m27c512_full_all_ok` is a **misnomer**: its write and verify steps are `SKIPPED` with `run_count=0`, because `_fixed_return_operator`'s `read_eprom` returns `True` while writing no file, so `_read_region` gets `b""`, every UV slot is unevaluable, and `_resolve_write_target` refuses. **No frozen shape in the corpus exercises a real UV masked write.** `uv-slot-write-pass` needs a chip-modelling double — `FakeChip` (which is already imported into `conftest.make_app_context`'s type surface) or an `_sdp_aware_operator`-shaped stateful `Mock`.

---

## Open questions / decisions the planner must make explicit

There is no CONTEXT.md. Each of these is `[ASSUMED]` until the operator confirms; the planner should surface them as `checkpoint:decision` tasks or as explicitly-named assumptions in the plan.

### Q1 — What does a non-blank UV part's `blank-check` step *mean*? **(the phase's central decision)**

`PASS` requires the step to be `OK`, `NA` or `SKIPPED`. `OK` is unavailable (hash collision, above, and it is a lie). Candidates:

| Option | Where | Cost | Notes |
|---|---|---|---|
| **A.** `derive_plan` emits the UV blank-check `supported=False` | `chip_test.py:684-725` | re-keys `plan_shapes.json` for 301 chips; reddens `tests/test_chip_test_blank_check_order.py::test_am27512_uv_blank_check_position_is_unchanged` (which asserts `blank_check_step.supported is True`); contradicts the in-source rationale at `chip_test.py:695-698` | Loses the finding entirely — the operator can no longer see that the part is not blank. |
| **B.** Keep the step supported; adjudicate the **verdict** at execution time — a non-blank *UV* part yields `NA` or `SKIPPED` with the firmware's reason preserved | `chip_test.py:2626-2641` | re-keys one shape (`RK-174-04`); leaves `plan_shapes.json` untouched; leaves `test_am27512_uv_blank_check_position_is_unchanged` green | Needs a UV signal at the dispatch site. `_dispatch_step` receives `step`, not `plan` — so either `Step` gains a field or the decision is keyed on something already there. |
| **C.** Keep `BAD`, and change the *fold* so a UV blank-check `BAD` does not dominate the title | `submit.py:164-171` | touches a consumer four inherited tests pin | Narrow special-casing in the fold is the kind of thing this codebase repeatedly refuses; likely rejected. |

The milestone research's own recommendation (`.planning/research/SUMMARY.md:135-138`) is B in spirit: *"a finding, not a FAIL, and it must not set `error_code`."* Note that under B, whether `error_code` is also cleared is a **separate** sub-decision — measured this session, clearing it is *not required* for cycle 2 on a UV plan (the step is outside the block), but leaving a non-`None` `error_code` on a non-BAD step would be novel in this tree and would still reach the exported `steps[].error_code` (`diagnostic_report.py:831`).

**Sub-question Q1a:** which value — `NA` or `SKIPPED`? `NA` suppresses the reason in both the markdown table and the exported JSON (`diagnostic_report.py:830-834` renders `""` for `VERDICT_NA`; `submit.py:222-243` renders `-`, keyed on the verdict at `:241-242`), which would **destroy the finding** the option exists to preserve. `SKIPPED` preserves it. Phase 178's D-01 reasoned identically for the status axis. The planner should probably prefer `SKIPPED`, but must say so and measure the resulting hash.

**Sub-question Q1b:** how does `_dispatch_step` learn the step is on a UV plan? `Step` has `region_policy` — but UV-03's spirit (don't key behaviour on the policy string) arguably extends here. `Plan.is_uv` is decided once (`is_uv = is_uv_eprom(full)` at `chip_test.py:579`, carried at `:895`) and is not threaded to `_dispatch_step`. An additive `Step` field set only by `derive_plan` would follow the existing derive-once/read-many discipline.

### Q2 — What exactly is the monotonicity witness?

Three candidate forms, none free:

| Form | Fires on real runs? | Refuses the retired D-C branch? | Cost |
|---|---|---|---|
| `t.current_source == "probe read"` (research's prescription) | **No** — measured `"probe read (tranche 1/2)"` | yes | inert; would ship green and do nothing |
| `t.current_source.startswith("probe read")` | yes (measured) | yes | string-prefix matching on provenance prose — brittle in exactly the family UV-03 warns about |
| `t.masked and bool(t.current)` | yes | **no** — a D-C-style assumed-`0xFF` masked target would pass | structural, no strings |
| **A new structural field**, e.g. `current_is_probe_read: bool`, set `True` only at `chip_test.py:2962` and carried through at `:1518` alongside `slots_remaining`/`slots_total`/`region_policy` | yes | yes | one additive `WriteTarget` field; matches the carry-through discipline already documented at `chip_test.py:2372-2385` |

The fourth is the only one that is both live and fail-closed. It is a new field on a frozen-ish dataclass, but `WriteTarget` is not exported wholesale — `_step_dict` cherry-picks five keys (`diagnostic_report.py:838-843`) — so it does not grow the report surface unless the planner wants it to.

**Sub-question Q2a:** where does the fail-closed assertion live? PITFALLS recommends refusing to set the flag when the witness is absent — which is what "derive from the witness" already means. A separate *positive* assertion (refuse to *write* a masked target whose witness is absent) would be stronger; the planner must decide whether that is in scope.

### Q3 — Where does the flag get *composed*?

`build_flags` (`eprom_operations.py:269-308`) is documented as the one function that maps wire flags. But it maps from a **CLI boolean**, and `chip_test.py` is an orchestrator that "builds NO wire dict" (`chip_test.py:2609-2612`). The SDP leg's precedent (`chip_test.py:3405-3414`) composes the bit **inline in `chip_test.py`** as a bare int. `tools/check_devtest_orchestrator.py` bans a *dict literal* whose keys intersect the wire vocabulary (including `flags`) — a positional int is not a dict literal and is compliant. **Recommendation: follow the SDP-leg precedent inline.** But the planner should record the choice, because PITFALLS `:449` recommends routing through `build_flags` instead, and the two recommendations conflict.

### Q4 — How is criterion 4 satisfied? **(the second-largest decision)**

> **[VERIFIED: tests/test_skip_census.py:114-140, measured this session]** There is **no hardware-gated pytest test in this repo**. `ALLOWED_SKIP_REASONS` has exactly four entries: `FW_ABSENT_REASON` (sibling firmware repo absent), `"firestarter entry point not found on PATH"`, `"meta-repo ledger not available at"`, `"EVIDENCE.json not found at"`. None is board- or chip-presence. The module's own note records the inverse hazard: *"with a programmer board attached, some tests in this suite behave differently (a recorded, known environment artifact)."*

Routes:

- **R1 (recommended split).** Commit a **firmware-faithful double** regression test that runs everywhere — a `FakeChip` subclass whose `write_eprom` refuses a non-blank device unless `FLAG_SKIP_BLANK_CHECK` is set, exactly mirroring `eprom.cpp:143-145` — and assert `submit.overall_verdict(...) == "PASS"` and write `run_count == 2`. Then satisfy "passes against real UV hardware" with a `blocking-human` bench wave producing a committed measurement artifact, on the Phase 176-05 precedent (`176-MEASUREMENT.md`). **Honest cost, which the plan must state:** the committed test proves the *host* logic; the bench artifact proves the *hardware* claim. Neither alone is criterion 4.
- **R2.** Add a genuinely skipping hardware test plus a fifth `ALLOWED_SKIP_REASONS` entry. This makes the test *committed to the suite* literally, but it is **skipped in CI forever** and is therefore a permanently-dormant assertion — the "fixture-passing selftests ≠ working tooling" failure this project has recorded before.
- **R3.** A shell script beside `firestarter_test.sh` / `write_test.sh`. Not "committed to the suite" in the pytest sense.

R1 needs the operator's agreement that the split satisfies criterion 4. **The planner must not decide this silently.**

### Q5 — Does the report disclose that the harness set a flag the product does not?

`.planning/research/PITFALLS.md:236-247` (Pitfall 7) argues for a disclosure key: after this phase, `dev test m27c512` passes on a non-blank part while `firestarter write -a 0x…` on the identical part is still refused by the identical firmware. Additive keys do not move the dedup hash. But every exported key grows the frozen-key surface, and RPT-A4 (`plan.is_uv`) is explicitly Phase 181's. Pitfall 7's own verdict is *"Both, or neither."* `write_current_source` is already exported (`diagnostic_report.py:842`) and already discloses the probe; whether that is sufficient is a judgement call.

### Q6 — Which chip is the bench part, and is it in a usable state?

See `## Bench hardware` below. The operator must confirm on-hand state; Claude cannot handle chips.

### Q7 — Is `MSG_ERR_NOT_BLANK` propagation still wanted on the blank-check step?

`chip_test.py:2628-2635` deliberately captures the firmware's address+value for a failing blank-check ("the single most useful datum in a `dev test` failure"). If Q1's answer changes the verdict, the plan must state explicitly whether that diagnostic survives. `tests/test_devtest_firmware_error_propagation.py` exists and will have an opinion.

### Q8 — Bundle the stale UV-prompt comment?

`.planning/todos/pending/2026-09-04-stale-uv-prompt-comment-in-cli-handlers.md` records a stale design-history comment at `cli_handlers.py:2295-2303` describing the reverted `260821-wna` UV consent prompt. It is UV-adjacent and Phase 175 could not take it (test-only boundary). This phase touches product code and could. **Note the HARD RULE below:** the fix is *deletion*, never a rewritten comment.

---

## Landmines

1. **NO comments in source, at all.** Project hard rule, absolute; a plan cannot override it. Phase 178's verify blocks assert `phase_added_comments=0` by diffing `^\+[[:space:]]*#`. Do not propose explanatory comments — put the reasoning in the plan and in docstrings only where the tree already does so.
2. **`operation_flags` must be passed POSITIONALLY.** Two of three write-capable doubles name it `flags` (`tests/test_chip_test.py:1067`, `tests/fixtures/report_shapes.py:432`). A keyword call silently no-ops on both.
3. **`current_source == "probe read"` never matches on a real run.** Measured `"probe read (tranche 1/2)"`. A witness written that way ships green and inert.
4. **`write -b` polarity is INVERTED between commands.** `write -b`/`--no-blank-check` **sets** `FLAG_SKIP_BLANK_CHECK`; `erase -b`/`--blank-check` **clears** it (`cli_handlers.py:602`, `:832-833`). `-b` is a CLI ergonomics flag on the *user-facing* `write` path and is **not** the mechanism this phase uses — `dev test` never parses `-b`. Do not conflate them. (The older "`write -b` also skips erase" trap has been **fixed**: `cli_handlers.py:324-325` now states `-b` does not imply skip-erase. The memory note recording that trap is stale for the current tree.)
5. **`grep` in this devcontainer is ugrep and honours `.gitignore`.** It silently under-scans. Use `/usr/bin/grep` for anything that becomes gate evidence — every 178 verify block does.
6. **The devcontainer default python is 3.12; CI is 3.11.** Use `firestarter_app/.venv311/bin/python` for every command. 3.12 masks real CI failures.
7. **`firestarter_app/build/lib/firestarter/` is a stale build artifact** containing a full copy of the package (it matched `FLAG_SKIP_BLANK_CHECK` in the first scan). Never edit it; never cite it.
8. **`chip_database.json` is GENERATED.** Never hand-edit; fixes go in `tools/build_db.py`'s decode function. This phase should not touch it at all — assert it clean.
9. **`firestarter/src/messages.h` does not exist**; the ids live in `firestarter/include/messages.h` and are CODEGEN-GENERATED and ID-ONLY (edit the meta repo's `messages.toml` and regenerate). This phase needs **no** firmware change, so this should not arise.
10. **`plan_shapes.json` re-keys for 301 chips** if `derive_plan`'s UV blank-check `supported` flips. Prefer execution-time adjudication.
11. **`m27c512-full-all-ok` does not exercise a UV write.** Its write/verify are `SKIPPED` (measured). Do not model `uv-slot-write-pass` on `_fixed_return_operator`.
12. **`blank-check=OK` collides with an existing frozen hash** (`6d3afbc52315`). That option is structurally unavailable.
13. **Declaring a non-move in the re-key ledger is a bookkeeping error** (Phase 178 D-09, `tests/test_rekey_ledger.py`). `RK-174-04`'s `after_hash` stays `None` unless the hash genuinely moves.
14. **`tools/rekey/check_rekey_ledger.py` runs from `/workspaces`**, not from `firestarter_app/`. Running it from the sub-repo gives `Errno 2`.
15. **`test_flash_path_record_sync` asserts whole-repo porcelain.** Commit before running the full suite.
16. **`pytest` addopts are `-ra -q`;** a count line needs `-o addopts=""`.
17. **The two sub-repos are git submodules** of this meta repo. Executors commit **inside** them on the milestone branch `gsd/v1.36-dev-test-fidelity`. Both are on that branch and clean as of this research.
18. **Any new `dev_test` helper in `cli_handlers.py` must be added to `_HANDLER_FUNCTION_NAMES`** (`tools/check_devtest_orchestrator.py:152-164`) or the gate silently does not scan it — it fails **open**. HYG-04 already names this.
19. **`tools/check_devtest_orchestrator.py` bans a dict literal in `chip_test.py`/`cli_handlers.py`/`submit.py` whose keys intersect the wire vocabulary, `flags` included.** Never build a flags dict; a bare positional int is compliant.
20. **A UV write is physically irreversible and the operator has no UV eraser** (`project_v118_phase99_bench_defer`). Every bench run consumes one 256-byte slot permanently. Budget slots explicitly in the plan.

---

## Bench hardware

**Chip insertion and removal are OPERATOR-ONLY.** Claude can drive the serial port and run the CLI, but cannot handle a chip. The plan must include a `blocking-human` checkpoint for seating the part, not an autonomous bench step.

### What the database supports

> **[VERIFIED: measured this session via `is_uv_eprom` + `uv_slot_starts`]** 301 UV rows: protocol `0x07` × 163, `0x08` × 106, `0x0B` × 32. **All 301 are slot-capable** at the 256-byte slot width (`_UV_WRITE_REGION_LENGTH = 256`, `chip_test.py:2105`).

| CLI token | DB `name` | proto | mem | slots | VPP | chip-id |
|---|---|---|---|---|---|---|
| `m27c512` | `M27C512,M27V512` | 0x07 | 65536 | 256 | 13000 mV | 0x203D |
| `tms27c512` | `SMJ27C512,TMS27C512,TMS27PC512` | 0x07 | 65536 | 256 | 13000 mV | 0x9785 |
| `am27c020` | `AM27C020` | 0x08 | 262144 | 1024 | 13000 mV | 0x0197 |
| `m27c256b` | `M27C256B` | 0x07 | 32768 | 128 | 13000 mV | 0x208D |

`uv_slot_starts` is **top-down**, so slot 1 is the highest address — `0xFF00` for a 64 KiB part, `0x3FF00` for `am27c020` (both measured via `derive_plan`).

### What the operator plausibly has

- **ST M27C512** (`m27c512`, 0x07, 13 V, 28-pin) — **the recommended part.** Bench-proven writing cleanly in Phase 83 (`project_phase83_shipped`): *"write 16B@0x0000 RC=0, verify RC=0."* That 16-byte write at `0x0000` is **data outside the top slot** — precisely UV-01's precondition, already present. The CLI token is `M27C512`; "ST M27C512" is a human label that does not resolve.
- **AM27C020** (`am27c020`, 0x08, 32-pin) — **not recommended.** Its 0x08 write path is recorded marginal/unreliable *on this bench* (`project_v118_phase99_bench_defer`, FUT-08; `project_phase83_shipped` ANOMALY: 0 bits programmed across three attempts). A failure here would be uninterpretable — chip, bench or this phase's change.
- **No UV eraser.** Slots spent are gone.

### Why an erasable proxy will NOT work here

`reference_erasable_parts_are_uv_firmware_proxies` establishes that an electrically-erasable part is a full *firmware-path* proxy for a UV part on the same protocol. **That does not apply to this phase.** The `uv-slot` policy is a **host/database** decision keyed on `electrical-type == "UV-EPROM"` (`chip_test.py:519`). A W27C512 or W27E257 is `EEPROM`, takes `REGION_POLICY_FIXED`, never resolves a masked target, and never produces a witness. The host path under test is unreachable from a proxy. **A genuine UV part is mandatory for criterion 1.**

---

## Proven verify command shapes

Copy these verbatim; they are the shapes Phase 178's plans used and every one is re-measured green as of this research.

### Baseline (all measured this session, clean tree, `gsd/v1.36-dev-test-fidelity` in both sub-repos)

| Gate | Command | Current value |
|---|---|---|
| full suite | `./.venv311/bin/python -m pytest tests/ -o addopts="" -q` | `2241 passed`, `32 snapshots passed`, ~330 s |
| ruff lint | `./.venv311/bin/python -m ruff check firestarter/ tests/` | `All checks passed!` |
| ruff format | `./.venv311/bin/python -m ruff format --check firestarter/ tests/` | rc=0 |
| mypy watermark | `./.venv311/bin/python tools/check_mypy_watermark.py` | `checked 173 source files` / `mypy errors: 35 (watermark: 35)` |
| report snapshots | `./.venv311/bin/python tools/snapshot_report_shapes.py --check` | `OK: 18 snapshot(s) … match a fresh regeneration` |
| orchestrator gate | `./.venv311/bin/python tools/check_devtest_orchestrator.py` | `PASS: scanned … 0 VPP-set, 0 raw-wire-dict, 0 --force, 0 broad-except` |
| report-claims gate | `./.venv311/bin/python tools/check_diagnostic_report_claims.py` | `PASS: scanned … 216 string literals checked, zero forbidden matches` |
| re-key ledger | `python3 tools/rekey/check_rekey_ledger.py` **(from `/workspaces`)** | `OK: 8 ledger row(s), 8 MILESTONES.md row(s) bound` |

### Per-commit hygiene block (from `178-01-PLAN.md:436`, adapt the snapshot count)

```bash
cd /workspaces/firestarter_app && test "$(git diff HEAD~1 -- firestarter/ tests/ | /usr/bin/grep -E '^\+' | /usr/bin/grep -vE '^\+\+\+' | /usr/bin/grep -vE '^\+[[:space:]]*["'"'"']' | /usr/bin/grep -cE '^\+[[:space:]]*#')" -eq 0 && ./.venv311/bin/python -m ruff check firestarter/ tests/ && ./.venv311/bin/python -m ruff format --check firestarter/ tests/ && ./.venv311/bin/python tools/check_mypy_watermark.py | /usr/bin/grep -qx 'mypy errors: 35 (watermark: 35)' && test -z "$(git -C /workspaces/firestarter status --porcelain)" && test -z "$(git status --porcelain firestarter/data/chip_database.json)"
```

### Named-leg collection proof (from `178-01-PLAN.md:505`)

```bash
(cd firestarter_app && ./.venv311/bin/python -m pytest -o addopts="" -q --collect-only tests/test_chip_test.py) > /tmp/179-collect.txt 2>&1
for t in test_<name_1> test_<name_2>; do echo "leg_${t}=$(/usr/bin/grep -c "$t" /tmp/179-collect.txt)"; done
```
Fails when any `leg_<name>=0` line appears (the test function was never collected). Pair it with `! /usr/bin/grep -q 'no tests ran'` and `! /usr/bin/grep -qE '[0-9]+ (failed|error)'`.

### Phase-seal shape (from `178-04-PLAN.md:389`, abridged)

The eight `rc=0` legs are: ruff check, ruff format, mypy watermark, `snapshot_report_shapes.py --check`, `check_devtest_orchestrator.py`, `check_diagnostic_report_claims.py`, `check_rekey_ledger.py`, full suite. Plus `firmware_diff=clean`, `chip_database_diff=clean`, `app_tree=clean`, `phase_added_comments=0`, and a `full_suite_passed` floor — **use `>= 2241`** for Phase 179.

### The UV-03 disagreement seam, PROVEN

`WriteContext.cycle_targets` is a zero-probe injection seam: set it and `_cycle_target` (`chip_test.py:1330-1345`) short-circuits `_resolve_write_target`, so a test can hand `_dispatch_multi_run` a hand-built `WriteTarget` that **disagrees** with `step.region_policy`. Measured working this session:

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
# measured: verdict=OK, run_count=1, exactly one write_eprom call, ZERO probe reads
```

That is the cheapest honest construction for UV-03's "the two signals disagree and the witness wins": policy says `uv-slot`, witness is absent, the flag must **not** be set. The converse leg — a masked probe-read target under a `fixed` policy, where the flag **must** be set — uses the same seam with `masked=True, current=<bytes>` and a `fixed`-policy `Step`. Assert on the flags the double recorded, not on the verdict.

---

## Don't hand-roll

| Problem | Don't build | Use instead | Why |
|---|---|---|---|
| A UV chip model for tests | a fresh `Mock` | `tests/fake_chip.py` `FakeChip` | It models UV AND-physics (`existing & incoming`) and absolute-offset reads (`file_handle.seek(address)`), the two properties a `Mock` cannot fake and without which the tests are theatre. Subclass it to add the firmware refusal. |
| The firmware blank-check refusal in a test | a bespoke exception plumbing path | a `FakeChip` subclass raising `EpromOperationError("…", error_code=0xB0)` when `not (operation_flags & FLAG_SKIP_BLANK_CHECK)` and the device is not blank | Mirrors `eprom.cpp:143-145` exactly; the existing `except EpromOperationError` arm (`chip_test.py:2576-2583`) does the rest. |
| Injecting a write target into a test | monkeypatching `_resolve_write_target` | `WriteContext(cycle_targets=[t])` | Public dataclass field, no patching, proven above. |
| A frozen-shape snapshot | hand-written JSON | `tools/snapshot_report_shapes.py` | The `--check` gate compares against a fresh regeneration; a hand-written file is red by construction. |
| Declaring a re-key | editing `FROZEN_HASHES` alone | fill `after_hash` in `tests/fixtures/rekey_ledger.py` **and** the bound `.planning/MILESTONES.md` row in the same commit | `tools/rekey/check_rekey_ledger.py` binds them; either alone fails. |
| Computing a wire flag | a new helper | the SDP leg's inline positional int (`chip_test.py:3405-3414`) | Zero new surface; compliant with the orchestrator gate. |

---

## Project Constraints (from CLAUDE.md and project skills)

From `/workspaces/CLAUDE.md`:
- `firestarter/` (firmware) and `firestarter_app/` (host CLI) are the two sub-repos; this meta repo tracks only `.planning/`, `.claude/`, `tools/`, `.github/`.
- Serial-protocol changes must be kept in sync between `firestarter_app/firestarter/serial_comm.py` and `firestarter/src/firestarter.cpp`. **Not triggered by this phase** — no new command, no new field.
- Constants/flag bits are duplicated between `firestarter_app/firestarter/constants.py` and `firestarter/include/firestarter.h`; change both together. **Not triggered** — `0x08` already exists on both sides and is unchanged.
- Board buffer sizes (Uno 512 B, Leonardo 1024 B) affect chunked transfer. A 256-byte slot fits either.
- `main` is protected in all three repos; this project's close targets `beta`.

From `.claude/skills/devtest-rootcause/SKILL.md` and `devtest-triage/SKILL.md`:
- `firestarter_app/firestarter/data/chip_database.json` is **generated** and must never be hand-edited; database defects are fixed in the generator's decode function.
- `.claude/skills/devtest-triage/SKILL.md` is a downstream consumer of the issue title and verdict tokens. Phase 178's D-05 deliberately reused the existing `INCONCLUSIVE` token so the triage regex needed zero change. **If Phase 179 changes what a UV run's title reads, check this file** — though a UV run reaching `PASS` uses an existing token and should need no triage change.

From operator standing rules:
- **NO comments in source code, at all**, ever. A plan cannot override this.
- Decide mechanical gray areas rather than asking; ask on anything that spends a UV slot or seats a chip.
- Bench boards are a firmware-flash testbed (standing OK to flash) — but **chips are operator-only**.
- Verify `controller:` identity per port each task; `ttyACM*` numbers shuffle across replug.

---

## Security Domain

`security_enforcement` is not disabled in `.planning/config.json`, so this section is included. Phase 178's own `<threat_model>` set the precedent: ASVS level 1, blocking threshold high.

| ASVS Category | Applies | Standard control |
|---|---|---|
| V2 Authentication | no | no auth surface; local CLI over USB serial |
| V3 Session Management | no | none |
| V4 Access Control | no | none |
| V5 Input Validation | **yes** | `WriteTarget.__post_init__` (`chip_test.py:2390-2413`) is the structural vacuous-pass guard; `_MULTI_RUN_OPS` / `_SDP_OPS` fail-closed allow-lists (`chip_test.py:3095-3105`, `:2681`, `:1022`) and the terminal fail-closed `return` (`chip_test.py:2687-2695`); `derive_plan`'s `ValueError` on an unrecognised `write_scope` (`chip_test.py:566-570`) |
| V6 Cryptography | no | `dedup_fingerprint` is a non-secret dedup id (sha256 truncated for distribution), explicitly not a security control (`diagnostic_report.py:270-272`) |

**Domain threat, non-ASVS but the one that matters:** this phase deliberately *disables a firmware safety pre-flight*. The mitigation is the monotonicity witness — the write may only skip the blank check when the pattern is provably `current & desired`, derived from a real probe read of the exact region. The failure mode if the witness is wrong is a **physically unrecoverable** part (no UV eraser on this bench). This argues for the fail-closed structural form of Q2 and for the disagreement test of UV-03 being a **blocking** verification leg, not a nice-to-have.

*(`workflow.nyquist_validation` is `false` in `.planning/config.json`, so no Validation Architecture section is included.)*

---

## Environment Availability

| Dependency | Required by | Available | Version | Fallback |
|---|---|---|---|---|
| `firestarter_app/.venv311` | every host command | ✓ | py3.11 (CI-matching) | none — do not use the 3.12 default |
| `ruff` | lint/format gates | ✓ | via `.venv311` | — |
| `mypy` | watermark gate | ✓ | watermark 35/35 | — |
| `pytest` + `syrupy` | suite (2241 passed, 32 snapshots) | ✓ | — | — |
| `tools/rekey/check_rekey_ledger.py` | ledger binding | ✓ | run from `/workspaces` | — |
| PlatformIO / `pio` | firmware build | not probed | — | **not needed** — this phase requires no firmware change |
| Real UV EPROM + programmer board | criteria 1, 2, 4 | **operator-gated** | — | none for the hardware claim; a firmware-faithful double covers the host claim |

**Blocking:** the bench part. Everything else is present.

---

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|---|---|---|
| A1 | The operator's ST M27C512 is still on hand, is not saturated, and holds data outside the top slot | Bench hardware | The phase's hardware wave cannot run; a different part must be chosen and `am27c020`'s 0x08 path is recorded unreliable |
| A2 | A committed firmware-faithful-double test plus a bench measurement artifact together satisfy criterion 4 | Q4 | Criterion 4 is not met as the operator reads it; the phase would need a genuinely-skipping CI test and a fifth `ALLOWED_SKIP_REASONS` entry |
| A3 | The UV blank-check should become `SKIPPED` (finding preserved) rather than `NA` (finding suppressed) | Q1a | The finding the step exists to surface is destroyed by `NA`'s render-layer suppression |
| A4 | Composing the flag inline in `chip_test.py` (SDP-leg precedent) is preferred over routing through `build_flags` | Q3 | Conflicts with `.planning/research/PITFALLS.md:449`; a reviewer may read it as a wire-flag mapping escaping its one home |
| A5 | A disclosure key for "the harness set a flag the product does not" is Phase 181's, not this phase's | Q5 | A UV `PASS` ships with no evidence a shortcut was taken (Pitfall 7's stated failure) |
| A6 | The projected post-change hashes measured here (`559bb7d81a92` / `e42f1567967a`) reproduce from a real modified `derive_plan`/`run_plan` build | Blast radius | The declared `after_hash` in `RK-174-04` is wrong; the ledger checker and the invariance oracle both redden |
| A7 | No firmware change is needed | UV-01 | If the operator wants `firestarter write` to gain the same behaviour, that is a firmware+host change and a different phase (999.44's other half) |

---

## Sources

### Primary (HIGH confidence — measured in-tree this session)
- `firestarter_app/firestarter/chip_test.py` — `derive_plan`, `run_plan`, `_run_cycle_block`, `_dispatch_step`, `_dispatch_multi_run`, `_resolve_write_target`, `_plan_cycle_targets`, `_uv_cycle_targets`, `WriteTarget`, `WriteContext`, `cycle_block_bounds`, `repeat_policy_tag`, `coverage_tag`, `is_uv_eprom`
- `firestarter_app/firestarter/eprom_operations.py` — `build_flags`, `write_eprom`, `check_eprom_blank`
- `firestarter_app/firestarter/submit.py` — `overall_verdict`, `build_title`
- `firestarter_app/firestarter/diagnostic_report.py` — `dedup_fingerprint`, `_step_dict`, `_write_coverage_line`, `to_dict`
- `firestarter_app/firestarter/cli_handlers.py` — `_resolve_write_scope`, `_build_op_flags`, `_dev_test_exit_code`, `dev_test`
- `firestarter_app/firestarter/constants.py:122`
- `firestarter/src/proms/eprom.cpp`, `firestarter/src/proms/memory.cpp`, `firestarter/include/firestarter.h:139`, `firestarter/include/messages.h:93`, `firestarter/include/proto_constants.h:13-15`
- `firestarter_app/tests/fake_chip.py`, `tests/fixtures/report_shapes.py`, `tests/fixtures/rekey_ledger.py`, `tests/fixtures/shape_ids.json`, `tests/fixtures/plan_shapes.json`, `tests/test_skip_census.py`, `tests/test_chip_test_blank_check_order.py`
- Live measurements: plan derivation for three UV chips; two end-to-end `run_plan` simulations (with and without the flag) against a firmware-faithful double; all 18 frozen hashes recomputed; three hash projections; the `cycle_targets` injection seam; full suite `2241 passed`; all seven gates green

### Secondary (MEDIUM confidence — project record, cross-checked against source)
- `.planning/research/SUMMARY.md:29`, `:89`, `:135-138`, `:200`, `:218`
- `.planning/research/PITFALLS.md:164-247` (Pitfalls 5, 6, 7) — **Pitfall 5 step 2 falsified this session**; **SUMMARY:89's witness form falsified this session**
- `.planning/research/ARCHITECTURE.md:531-548` (§6.7), `:549-561` (§6.8)
- `.planning/phases/178-*/178-CONTEXT.md`, `178-DECISIONS.md`, `178-03-SUMMARY.md`, `178-01-PLAN.md`, `178-04-PLAN.md`
- `.planning/MILESTONES.md:36-53`
- `.planning/quick/260821-wna-*/` — SUMMARY and VERIFICATION (confirmed: the quick task never touched `FLAG_SKIP_BLANK_CHECK`)
- `.planning/todos/pending/2026-09-04-stale-uv-prompt-comment-in-cli-handlers.md`

### Tertiary (project memory — operator facts, not independently verifiable in-tree)
- `project_phase83_shipped` — ST M27C512 bench PASS with a 16 B write at `0x0000`; AM27C020 0x08 write anomaly
- `project_v118_phase99_bench_defer` — AM27C020 marginal; **operator has no UV eraser**
- `reference_erasable_parts_are_uv_firmware_proxies` — proxy table; **shown above not to apply to this phase's host path**

---

## Metadata

**Confidence breakdown:**
- Call chains and line citations: **HIGH** — every cited line opened and read this session; every quoted value is verbatim
- Measured baselines (hashes, suite count, gate outputs, plan shapes): **HIGH** — produced by command this session
- Hash projections for candidate designs: **MEDIUM** — mutation over an existing report object, not a build through modified production code; re-measure before freezing
- Bench part availability and state: **MEDIUM** — project memory, operator must confirm
- The two falsifications (PITFALLS Pitfall 5 step 2, SUMMARY:89's witness form): **HIGH** — both measured directly

**Research date:** 2026-09-06
**Valid until:** 2026-10-06 for the in-repo facts (this is a fast-moving branch — re-verify the suite count and frozen hashes at plan time if any commit lands first); the operator bench facts have no expiry but need confirmation before the hardware wave.
