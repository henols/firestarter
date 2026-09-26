# Phase 178: Fault Attribution — the Two-Axis Vocabulary - Pattern Map

**Mapped:** 2026-09-06
**Files analyzed:** 12 (4 source, 5 test, 2 fixture modules, 1 fixture JSON corpus)
**Analogs found:** 12 / 12 (every file in play already exists; this phase modifies, it creates no new module)
**Measured on:** `firestarter_app` @ `0a29d8b`, branch `gsd/v1.36-dev-test-fidelity`. Every path below verified tracked with `git ls-files`. All scans used `/usr/bin/grep`.

---

## Standing constraint that overrides every excerpt below

**The project rule is: no comments in source, at all.** Nearly every analog in this file states its rationale in a `#` comment block, because those blocks predate the rule. **Do not copy the comment mechanism — copy the wording and relocate it.** This codebase already has two comment-free carriers for exactly this content, and the planner should use them:

1. **Bare string literal immediately above a module constant.** Shipped idiom, `tests/test_blast_radius_invariance.py:88-186` — seven consecutive pinned lists, each introduced by a `"""..."""` expression statement, zero `#`. This is the carrier for the new `STATUS_*` block.
2. **The class docstring.** `StepResult`'s contract sentence for `verdict` lives at `chip_test.py:1066-1079` in the docstring, while `duration_s`'s lives in a `#` comment at `:1088-1093`. The docstring is the compliant half. New field rationale goes there.

---

## File Classification

| File to modify | Role | Data Flow | Closest Analog (same file unless noted) | Match |
|---|---|---|---|---|
| `firestarter/chip_test.py` — `STATUS_*` constants | config / vocabulary | in-process constant | `SDP_HOLD_*` block, `:1962-1967` | exact |
| `firestarter/chip_test.py` — `StepResult.status` | model (dataclass field) | transform | `StepResult.duration_s`, `:1082-1099` | exact |
| `firestarter/chip_test.py` — transport-fault arm | service (exception handler) | event-driven | the `EpromOperationError` arm directly below it, `:2542-2549` | exact |
| `firestarter/diagnostic_report.py` — `run_status` | model (derived top-level) | transform | `sdp_hold_state` field, `:634-648` | exact |
| `firestarter/diagnostic_report.py` — `to_dict` export | serializer | transform | `to_dict`, `:849-869` + `_step_dict`, `:768-808` | exact |
| `firestarter/diagnostic_report.py` — ATTR-06 sentence | serializer + renderer | transform | `_write_coverage_line`, `:520-...` + `render()` `:995-1007` | role-match |
| `firestarter/diagnostic_report.py` — `build_db_diff` guard | service (ladder) | transform | `build_db_diff`, `:365-384` | exact |
| `firestarter/diagnostic_report.py` — `SCHEMA_VERSION` 1.7→1.8 | config | — | `:48` | exact |
| `firestarter/submit.py` — `overall_verdict` | utility (title fold) | transform | `:140-152` | exact |
| `firestarter/cli_handlers.py` — exit code | controller | request-response | `_dev_test_exit_code`, `:2130-2157` | exact |
| `firestarter/cli_handlers.py` — assignment seam | controller | transform | `report.sdp_hold_state = ...`, `:2446-2450` | exact |
| `tests/fixtures/report_shapes.py` + `tests/test_blast_radius_invariance.py` + 2 fixture JSONs | test fixture registry | batch | the `prune03-synthesized-fingerprint-match` registration, commit `693c0c3` | exact |
| `tests/test_diagnostic_report.py` — Leg B exclusion test | test | transform | `test_durations_do_not_perturb_dedup_fingerprint`, `:1698-1716` | exact |
| `tests/test_dev_test_cmd.py:2014-2037` | test | request-response | itself (repair forward) | exact |

---

## Move 1 — an additive report field kept OUT of the dedup hash

**The canonical precedent is `duration_s` (schema 1.5). Here is its complete round trip, all four hops.**

### Hop 1 — dataclass declaration, `firestarter/chip_test.py:1082-1099`

```python
    op: str
    verdict: str
    reason: str = ""
    error_code: int | None = None
    fingerprint: Fingerprint | None = None
    run_count: int = 0
    divergence: dict[str, Any] | None = None
    # Wall-clock seconds for the whole step, stamped by `_run_step`'s timing
    # wrapper (operator asked for timings captured/presented/filed,
    # 2026-08-21). `None` for a step that never ran (NA/SKIPPED) -- a `0.0`
    # there would read as "ran, took no time" rather than "did not run".
    # Deliberately NOT part of `dedup_fingerprint`, which excludes every
    # volatile field so two runs of the same chip still dedup.
    duration_s: float | None = None
```

The load-bearing sentence to mirror for `status` is *"Deliberately NOT part of `dedup_fingerprint`"* — **relocated into the `StepResult` class docstring** (`:1066-1079`, which already carries the `verdict` contract sentence `` `verdict` is one of OK/BAD/NA/SKIPPED/marginal. ``). Add the sibling sentence there: `status` is one of COMPLETE/ERROR/SKIP, plus the D-02 `support_status` disambiguation.

### Hop 2 — `to_dict()` export, `firestarter/diagnostic_report.py:800-802`

```python
            # Schema 1.5: wall-clock seconds for the step, or `None` when it
            # did not run. Additive -- every pre-1.5 consumer ignores it.
            "duration_s": result.duration_s,
```

Per-step keys go in `_step_dict` (`:768-808`). A **top-level** key goes in `to_dict` (`:849-869`), which is the single place `SCHEMA_VERSION` is baked in:

```python
        return {
            "schema_version": SCHEMA_VERSION,
            ...
            "db_diff": self._db_diff_dict(),
            "sdp_hold_state": self.sdp_hold_state,
        }
```

### Hop 3 — every registry a new exported key must be added to

| Key location | Registry to edit | Current count |
|---|---|---|
| top-level (`run_status`, and the ATTR-06 sentence if top-level) | `_TO_DICT_KEYS`, `tests/test_blast_radius_invariance.py:92-104` | 11 → 12 (or 13) |
| inside `steps[]` (`status`) | `_STEPS_ELEMENT_0_KEYS`, `tests/test_blast_radius_invariance.py:175-189` | 13 → 14 |
| inside `voltage` (only if the ATTR-06 sentence lands there) | `_VOLTAGE_KEYS`, `:106-116` | 6 → 7 |
| all 17 committed snapshots | `tests/fixtures/reports/*.json` — regenerate, do not hand-edit | 17 files |
| version stamp | `SCHEMA_VERSION`, `diagnostic_report.py:48` | `"1.7"` → `"1.8"` (D-07) |

**Not** a registry: `dedup_fingerprint`. That is Hop 4.

### Hop 4 — the exclusion test, `tests/test_diagnostic_report.py:1698-1716` — clone verbatim for Leg B (D-10)

```python
def test_durations_do_not_perturb_dedup_fingerprint():
    """Two reports identical except for their step durations MUST produce
    the SAME `dedup_fingerprint`.

    This is the load-bearing property: the fingerprint deliberately excludes
    every volatile field so a second run of the same chip still groups with
    the first. Wall-clock timings are the most volatile field yet added, so
    a fingerprint that read them would make every single run unique and
    silently destroy duplicate detection."""
    from firestarter.diagnostic_report import dedup_fingerprint

    fast = _minimal_report(step_specs=[("read", VERDICT_OK, None, "")])
    fast.results[0].duration_s = 0.5

    slow = _minimal_report(step_specs=[("read", VERDICT_OK, None, "")])
    slow.results[0].duration_s = 987.654

    assert dedup_fingerprint(fast) == dedup_fingerprint(slow)
```

**Structural note the planner must preserve:** both reports use the same `verdict` (`VERDICT_OK`). If the Leg B clone varies the verdict alongside the status, the assertion becomes false and the test proves nothing. Vary the status axis **only**.

### Hop 5 (negative) — the thing NOT to write

`dedup_fingerprint`, `diagnostic_report.py:272-300`, is a positive allow-list. The whole of ATTR-04 is writing **no** line of this shape for the status field:

```python
    for result in report.results:
        cls = result.fingerprint.classification if result.fingerprint else ""
        parts.append(f"{result.op}={result.verdict}:{cls}")
```

---

## Move 2 — registering the frozen shape `attr01-status-axis-transport-fault`

### The research says seven. **My measured count is EIGHT gate-enforced edit sites, plus two prose repairs.**

I did not inherit the count. I diffed the last real registration — commit `693c0c3` (`test(177-02): ... register the reserved match shape`), which registered `prune03-synthesized-fingerprint-match` — and enumerated its hunks (`git show 693c0c3 --stat`; `git show 693c0c3 -- tests/fixtures/report_shapes.py tests/test_blast_radius_invariance.py | grep '^@@'`).

Where the research is right: `177-02-SUMMARY.md`'s "four registries" is a genuine undercount, and it is the same four the module's own docstring names at `report_shapes.py:26-28` (`_BUILDERS`, `FROZEN_HASHES`, `LADDER_PINS`, `shape_ids.json`).

Where the research is off by one: item 6 bundles `_PINNED_SHAPE_ID_SET` **and** `tests/fixtures/shape_ids.json` into a single item. They are two different files, edited in two different hunks in `693c0c3`, and enforced by two different tests (`:559-564` and `:707-723`). Counting edit *sites*, the cost is eight.

| # | Edit site | File:line anchor | Enforced by |
|---|---|---|---|
| 1 | `_build_attr01_status_axis_transport_fault()` builder fn | `tests/fixtures/report_shapes.py`, beside `:618` | `build_shape` dispatch |
| 2 | `_BUILDERS` entry | `tests/fixtures/report_shapes.py:641-659` | `SHAPE_IDS` derives from it (`:661`) |
| 3 | `FROZEN_HASHES` entry — **measured, never transcribed** | `tests/fixtures/report_shapes.py:663-682` | `test_dedup_fingerprint_is_frozen` (`:256`) |
| 4 | removal from `RESERVED_SHAPE_IDS` | `tests/fixtures/report_shapes.py:683-688` | disjointness assert, `:564` |
| 5 | `LADDER_PINS` entry | `tests/test_blast_radius_invariance.py:222-252` | five-way closure, `:748` |
| 6 | `_PINNED_SHAPE_ID_SET` entry | `tests/test_blast_radius_invariance.py:538-556` | `test_shape_id_set_is_pinned_and_disjoint_from_reserved`, `:560` |
| 7 | `tests/fixtures/shape_ids.json` | whole file (LIST equality, sorted) | `:716-723` |
| 8 | `tests/fixtures/reports/attr01-status-axis-transport-fault.json` | new file | `test_committed_snapshot_matches_a_fresh_regeneration` (`:590`) + closure (`:752`) |
| P1 | module docstring prose naming the reserved set | `tests/fixtures/report_shapes.py:19-32` | none (prose; `693c0c3` updated it anyway) |
| P2 | stale `"all three RESERVED_SHAPE_IDS names"` docstring | `tests/test_blast_radius_invariance.py:761` | none (already stale; two names now, one after this phase) |

**Ordering constraint, measured:** `tools/snapshot_report_shapes.py:125-135` rejects a `--shape` value not in `SHAPE_IDS`, and `SHAPE_IDS` is `tuple(sorted(_BUILDERS))` (`report_shapes.py:661`). **Edit 8 is only runnable after edits 1-2 land.** Command:

```bash
cd /workspaces/firestarter_app && ./.venv311/bin/python \
  tools/snapshot_report_shapes.py --shape attr01-status-axis-transport-fault
```

Also note edits 1-2 must land before edit 3 can be *measured* rather than guessed.

### The builder to copy — `report_shapes.py:618-639`

```python
def _build_prune03_synthesized_fingerprint_match() -> DiagnosticReport:
    """The shape D-04 reserved this name for (Phase 177). Pins the exact
    lowercase `match` literal inside `dedup_fingerprint`'s pre-image
    grammar directly, independent of the engine that produces it, so a
    later phase that respells the bucket (a typo, a case change, a rename)
    reddens here first rather than only inside `chip_test.py`'s own
    behaviour tests. Hand-specified with a chip/protocol pair no other
    registered shape uses (`PRUNE03-SYNTH-CHIP`/`0`), so this hash cannot
    collide with any real-path or hand-specified builder above."""
    return build_shape_from_step_specs(
        chip="PRUNE03-SYNTH-CHIP",
        protocol="0",
        step_specs=[
            ("id", "OK", None, ""),
            ("read", "OK", None, ""),
            ...
        ],
    )
```

`build_shape_from_step_specs` (`:112-179`) takes `step_specs` as `(op, verdict, cls, reason)` **4-tuples with no status slot**. Extending it is part of this phase. Its post-construction stamping seam is the pattern to reuse — `run_counts` and `coverage_policy` are both applied by mutating the built `StepResult`s after the loop (`:141-168`), which is the least-invasive way to add a status without widening the tuple and re-touching all 17 builders:

```python
    if run_counts:
        for result in results:
            if result.op in run_counts:
                result.run_count = run_counts[result.op]
```

---

## Move 3 — a non-verdict term on the exit code, as a PRECEDENCE CANDIDATE

**Analog:** `firestarter/cli_handlers.py:2130-2157`, `_dev_test_exit_code`. Quoted in full — mirror its exact shape.

```python
def _dev_test_exit_code(results: list[StepResult], *, sdp_oracle_not_run: bool) -> int:
    """Exit floor for an ALLOW-chip run whose SDP oracle did not run, so
    `dev test` cannot return 0 on a run that never exercised the oracle at all.

    Composed as a precedence CANDIDATE, never as a numeric max against the
    observed code. A max of 1 (BAD) and 2 (the floor) returns 2, which would
    launder a BAD run into an inconclusive one -- exactly the inversion the
    precedence map exists to prevent. A run that is both BAD and NOT-RUN still
    exits 1.

    Cost, stated: `dev test`'s exit code is no longer a pure function of step
    verdicts -- it gains exactly this one non-verdict term.

    The not-run oracle stays SKIPPED rather than becoming `marginal`, because
    `marginal` counts as *ran* and would hold N == M in the applicable ratio,
    defeating the point.

    ALLOW-only: callers gate this at the call site. A REFUSE chip reads NOT-RUN
    legitimately, and flooring its exit code would misrepresent a correct
    refusal as inconclusive.
    """
    codes = {_verdict_code(r.verdict) for r in results}
    if sdp_oracle_not_run:
        codes.add(2)
    for code in _EXIT_CODE_PRECEDENCE:
        if code in codes:
            return code
    return 0
```

**The three things to copy exactly:**
1. The extra term arrives as a **keyword-only `bool` parameter**, computed by the caller — not derived inside the helper.
2. It is added with `codes.add(2)` **into the same set** the verdict codes went into, then the single unchanged `for code in _EXIT_CODE_PRECEDENCE` walk decides. **No `max()`, no second branch.** Adding a status `ERROR` term means one more `codes.add(2)` guarded by one more keyword arg.
3. The docstring carries a **"Cost, stated:"** paragraph naming the widening as a debt. D-06's second non-verdict term must extend that sentence (it will no longer be "exactly this one").

Supporting constants, `cli_handlers.py:2107-2112`:

```python
_EXIT_CODE_PRECEDENCE: tuple[int, ...] = (1, 2, 0)
```

Call site to widen, `cli_handlers.py:2522-2529` — note the ALLOW-only gating is computed *at the call site*, which is where a `run_status == STATUS_ERROR` term belongs too:

```python
    code = _dev_test_exit_code(
        results,
        sdp_oracle_not_run=sdp_oracle_applicable(plan)
        and report.sdp_hold_state.startswith(SDP_HOLD_NOT_RUN),
    )
    sys.exit(code)
```

`_dev_test_exit_code` is inside the **mypy strict island** — the new parameter needs a full annotation.

---

## Move 4 — the new constants block beside `VERDICT_*`

### The block to sit next to, `firestarter/chip_test.py:933-939` (verbatim, including its comment header)

```python
# Verdict vocabulary. `MARGINAL` is destructive/verify-only -- never forced
# onto read-step disagreement.
VERDICT_OK = "OK"
VERDICT_BAD = "BAD"
VERDICT_NA = "NA"
VERDICT_SKIPPED = "SKIPPED"
VERDICT_MARGINAL = "marginal"
```

### The rationale idiom to copy — `SDP_HOLD_*`, `chip_test.py:1962-1970` (verbatim)

```python
# Three-valued hold-state REPORT VALUES. These are report values, NOT op
# strings -- they
# carry no `OP_` prefix and must never join `_ALL_OPS`/`_MULTIWORD_OP_VALUES`
# in tests/test_op_registration_parity.py; a later reader must not
# "helpfully" register them there.
SDP_HOLD_HELD = "HELD"
SDP_HOLD_NOT_HELD = "NOT-HELD"
SDP_HOLD_NOT_RUN = "NOT-RUN"
```

**Both analogs use `#`. The compliant carrier is the bare-string-literal-above-the-constant idiom already shipped in this tree** — `tests/test_blast_radius_invariance.py:88-104`:

```python
"""D-07's first pin: `DiagnosticReport.to_dict()`
(`firestarter/diagnostic_report.py:771-790`) emits eleven top-level keys
today."""
_TO_DICT_KEYS = [
    "auto_capture",
    ...
]
```

So the new block reads: a `"""..."""` expression statement carrying (a) the OCP `TestStatus` provenance, (b) the D-02 `support_status` disambiguation, (c) the `SDP_HOLD_*` warning that these are **report values, not op strings**, and must never join `_ALL_OPS`/`_MULTIWORD_OP_VALUES` — then the three `STATUS_* = "..."` assignments.

### The `support_status` collision is real — the exact colliding read site

`diagnostic_report.py:364`:

```python
    current = (raw_config or {}).get("support_status", "supported")
```

### The top-level derived-field declaration to copy — `diagnostic_report.py:634-648`

```python
    db_diff: DbDiff | None = None
    # the carriage half only --
    # a plain `str`, NEVER a `bool` ...
    # Defaults to `""` (unassigned); the VALUE is
    # assigned by `cli_handlers.py` from `chip_test.sdp_hold_state(plan,
    # results)` -- this class only
    # carries and serialises whatever string it is given, never derives one
    # (this is a declared non-registry, re-measured every run by
    # `test_non_registry_still_has_no_ops`'s AST inversion guard to carry
    # zero op vocabulary).
    sdp_hold_state: str = ""
```

`run_status` should follow this shape — a plain `str`, carried and serialised, with the fold computed elsewhere (see Shared Pattern B).

---

## Move 5 — where the ATTR-06 sentence is RENDERED (D-14)

### The render site, `firestarter/diagnostic_report.py:1001-1007`

```python
        v = d["voltage"]
        table.add_row(
            "vpp (before/after)", _rail_cell(v["vpp_before_mv"], v["vpp_after_mv"])
        )
        table.add_row(
            "vpe (before/after)", _rail_cell(v["vpe_before_mv"], v["vpe_after_mv"])
        )
```

### The prose-disclosure analog: `write_coverage`

`write_coverage` is the closest structural match — a **prose sentence computed once, exported into `steps[]`, and rendered as a conditional row, never recomputed at the render site**. Both halves:

`diagnostic_report.py:995-999` (render half):

```python
        write_idx = self._write_step_index()
        if write_idx is not None and write_idx < len(d["steps"]):
            coverage = d["steps"][write_idx].get("write_coverage")
            if coverage:
                table.add_row("write coverage", coverage)
```

`diagnostic_report.py:806` (export half, inside `_step_dict`):

```python
            "write_coverage": _write_coverage_line(result, step),
```

`_write_coverage_line` (`:520`) is the single computation, a `str | None` returning module-level function. Its comment block at `:989-994` states the discipline verbatim — *"Read straight off `d["steps"]` ... Never a second computation here, and never a re-parse of the JSON string -- single-sourced, same discipline every other render() row uses."* **Copy that discipline: one function computes the ATTR-06 string, `to_dict` exports it, `render()` reads the exported value.**

For an unconditional **top-level** string (which the ATTR-06 sentence is), the closer analog is `sdp_hold_state`: declared `:648`, exported `to_dict:868`, rendered `:979` as `table.add_row("sdp_hold_state", _state_cell(d["sdp_hold_state"]))`. Taking the top-level route moves `_TO_DICT_KEYS` (11 → 12); taking the `voltage` route moves `_VOLTAGE_KEYS` (6 → 7). Both are expected pin moves, not violations.

### The closest existing "this reading does not prove X" honesty sentence — measured

**There is no rendered "does not prove" sentence anywhere in `diagnostic_report.py` today.** I scanned every string literal in the module (`/usr/bin/grep -n 'add_row(\|does not prove\|not measured\|advisory'`). The ATTR-06 sentence will be the first of its kind. The three nearest honesty idioms, in descending closeness:

1. `diagnostic_report.py:49` — the strongest existing precedent, an *absence* disclosure:
   ```python
   NOT_MEASURED = "not measured"  # honest fallback, never a false 0
   ```
   and its sibling at `:51-53`, `NOT_REPORTED = "not reported"`, whose comment reads *"Distinct from NOT_MEASURED: this field was never ASKED, rather than asked and empty. Reusing NOT_MEASURED would conflate the two."*

2. `diagnostic_report.py:310-314` — the *epistemic-status suffix* idiom, and the only shipped example of a hedge word inside rendered/filed report prose:
   ```python
   _DISPOSITION_COMMUNITY_FAIL = (
       "suggests: community-fail signal (advisory -- human triage required)"
   )
   _DISPOSITION_CANDIDATE = "suggests: candidate for community-reported (advisory)"
   _DISPOSITION_INCONCLUSIVE = "inconclusive -- needs N>=2 agreement (advisory)"
   _DISPOSITION_NO_CHANGE = "no change suggested (advisory)"
   ```
   `suggests: ... (advisory)` is the house register for "this is not proof". The ATTR-06 sentence should read in the same voice.

3. `_is_transport_suspect`'s guard, `diagnostic_report.py:189-193` — the absent-counter honesty rule, in code rather than prose:
   ```python
       for name in _SUSPECT_SCANNED_FIELDS:
           value = getattr(th, name)
           if value is not None and value >= _SUSPECT_THRESHOLD:
               return True
       return False
   ```
   docstring `:165-168`: *"True only when a counter is PRESENT (not None) AND elevated. Absent counters can never fabricate suspicion -- mirrors the honest `indeterminate` fingerprint bucket."* **Mirror both conjuncts and their order in any status fold.**

**Wording gate to clear:** `tools/check_diagnostic_report_claims.py:106-148` AST-scans every string literal in `diagnostic_report.py` against 14 case-insensitive forbidden patterns. Avoid `proven`, `verified`, `now works`, `dev test proves`. A sentence of the form *"a rail reading does not show whether the socket is connected"* trips none of them.

---

## Shared Patterns

### A. The transport-fault handler re-point — `chip_test.py:2524-2541`

The arm to change, and the arm directly below it that must stay a chip verdict (`:2542-2549`):

```python
    except (SerialError, HardwareOperationError) as exc:
        return StepResult(
            op=step.op,
            verdict=VERDICT_BAD,
            reason=str(exc),
            run_count=1,
        )
    except EpromOperationError as exc:
        return StepResult(
            op=step.op,
            verdict=VERDICT_BAD,
            reason=str(exc),
            error_code=exc.error_code,
            run_count=1,
        )
```

The edit is `verdict=VERDICT_SKIPPED, status=STATUS_ERROR` on the **first** arm only (D-01/D-12). The clause ordering (`ProgrammerNotFoundError` et al. re-raised at `:2504-2523` **before** this one) is load-bearing and must not move. `error_code` stays omitted — neither exception class carries it.

**Apply to:** the D-12 trigger. `transport_suspect` is never read here.

### B. Derive in the engine, assign in the handler — `cli_handlers.py:2440-2450`

```python
    report.transport.decode_failures = transport_snapshot["decode_failures"]
    ...
    report.sdp_hold_state = sdp_hold_state(plan, results)
```

**Apply to:** `run_status`. The fold function lives in `chip_test.py` (or as a `DiagnosticReport` method beside `_is_transport_suspect`); `cli_handlers.py` only assigns. Never compute inline in `dev_test`.

### C. The status-axis-before-verdict widening, three sites

`submit.py:140-152` — the title fold (D-05: return the existing `"INCONCLUSIVE"` token, qualifier in the body; a new bare token would break `devtest_issues.py`'s `SOFT` set):

```python
def overall_verdict(results: Any) -> str:
    """FAIL-dominant title verdict -- NOT the handler's exit-code
    `max()` ordering (`cli_handlers.py`, where `marginal=2 > BAD=1`).

    `FAIL` if any step verdict is `BAD`; else `INCONCLUSIVE` if any is
    `marginal`; else `PASS`. Human-legible ordering for the issue title.
    """
    verdicts = {r.verdict for r in results}
    if "BAD" in verdicts:
        return "FAIL"
    if "marginal" in verdicts:
        return "INCONCLUSIVE"
    return "PASS"
```
Note it reads **bare literals**, not the `VERDICT_*` constants (`submit.py` imports only `VERDICT_NA`). A status guard must go **ahead of** the `"BAD"` test.

`diagnostic_report.py:371-383` — the ladder (D-04: an `ERROR` guard arm ahead of arm 1, or a `SKIPPED` transport step falls through arm 3 into `community-reported`):

```python
    if "BAD" in verdicts:
        proposed = _DISPOSITION_COMMUNITY_FAIL
        ladder_state = _LADDER_COMMUNITY_FAIL
    elif "marginal" in verdicts or has_indeterminate_fingerprint:
        proposed = _DISPOSITION_INCONCLUSIVE
        ladder_state = _LADDER_NONE
    elif "OK" in verdicts and verdicts <= {"OK", "NA", "SKIPPED"}:
        proposed = _DISPOSITION_CANDIDATE
        ladder_state = _LADDER_COMMUNITY_REPORTED
    else:
        proposed = _DISPOSITION_NO_CHANGE
        ladder_state = _LADDER_NONE
```

`cli_handlers.py:2130-2157` — Move 3 above.

### D. Verdict-keyed reason suppression — the two sites `NA` would have broken (D-01 evidence, both left UNCHANGED)

`submit.py:203-217` and `diagnostic_report.py:793`:

```python
            "reason": "" if result.verdict == VERDICT_NA else result.reason,
```
`_reason_text`'s docstring already states the `SKIPPED` carve-out this phase depends on: *"`SKIPPED` is deliberately NOT suppressed: a SKIPPED reason is frequently the real disclosure (e.g. 'no target resolved'), so it keeps rendering exactly like every other non-NA verdict."* Cite this as the standing proof that D-01's `VERDICT_SKIPPED` preserves the fault reason.

### E. Test repaired forward, not relaxed — `tests/test_dev_test_cmd.py:2014-2037`

```python
        assert steps["id"]["verdict"] == "BAD", steps["id"]
        operator.sdp_lock.assert_not_called()
        hold_state = data["sdp_hold_state"]
        assert hold_state == SDP_HOLD_NOT_RUN, hold_state
        normalized = _normalize_console_text(result.output)
        assert f"sdp_hold_state {SDP_HOLD_NOT_RUN}" in normalized, normalized
```

Repair: line 1 becomes `"SKIPPED"` **plus** a new `steps["id"]["status"] == "ERROR"` assertion. **The remaining four assertions must not change** — they are the safety-gate proof. The docstring's `"degrades the id step to BAD"` sentence also needs repairing.

### F. Verify commands (py3.11, count line visible)

```bash
cd /workspaces/firestarter_app
./.venv311/bin/python -m pytest tests/test_blast_radius_invariance.py \
  tests/test_rekey_ledger.py -o addopts="" -q          # baseline: 118 passed
./.venv311/bin/python tools/snapshot_report_shapes.py --check
./.venv311/bin/python tools/check_diagnostic_report_claims.py
cd /workspaces && python3 tools/rekey/check_rekey_ledger.py   # OK: 8 rows bound
```

---

## No Analog Found

| Item | Role | Data Flow | Reason |
|---|---|---|---|
| The ATTR-06 "does not prove" sentence, as rendered prose | serializer | transform | Measured: no existing rendered honesty sentence of this form in `diagnostic_report.py`. Closest carriers are `NOT_MEASURED` (`:49`) and the `(advisory)` disposition suffixes (`:310-314`) — voice analogs only, not structural ones. The `write_coverage` / `sdp_hold_state` pair supplies the *plumbing* analog; the *wording* is new. |
| A status parameter on `build_shape_from_step_specs` | test fixture | batch | The builder's `step_specs` is a fixed 4-tuple (`report_shapes.py:116`). The nearest analog is its own post-construction stamping seam (`run_counts`, `:141-145`) — extend by that route, not by widening the tuple across all 17 builders. |
| A rationale carrier for a new module constant block that is comment-free | config | — | `VERDICT_*` and `SDP_HOLD_*` both use `#`. The compliant idiom exists only in the **test** tree (`test_blast_radius_invariance.py:88-186`); this would be its first use in `firestarter/`. Flagged for the planner as a deliberate, defensible port. |

## Metadata

**Analog search scope:** `firestarter_app/firestarter/`, `firestarter_app/tests/`, `firestarter_app/tools/`
**Files scanned:** 14 tracked; 6 read in depth
**Tracked-source gate:** all 11 cited paths confirmed via `git ls-files` in `firestarter_app` (a git submodule; checks run from inside it). No gitignored mirror paths emitted.
**Pattern extraction date:** 2026-09-06 @ `0a29d8b`
