# Phase 206: `dev test` keeps its fidelity, on one session - Pattern Map

**Mapped:** 2026-09-23
**Files analyzed:** 10 (6 source, 4+ test)
**Analogs found:** 10 / 10 (every new file/edit has an in-tree analog; nothing here needs a RESEARCH.md-only pattern)
**Substrate:** `firestarter_app` HEAD `2756ef0` on `v1.41-verification-to-host`. **Every `file:LINE` below was re-opened and confirmed this session** (the research's approximate numbers were checked; corrections are noted inline). All paths are git-TRACKED (`git ls-files` inside the submodule, verified).

---

## File Classification

| Modified file | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `firestarter_app/firestarter/chip_test.py` (new `compare_path_tag` + tag constant) | service (engine) | transform | `chip_test.py:1054-1079` `coverage_tag` / `COVERAGE_TAG_FULL_DEVICE` | **exact** (same file, same function family) |
| `firestarter_app/firestarter/chip_test.py` (new non-hashed `StepResult` field) | model | transform | `StepResult.write_target` / `duration_s` (`chip_test.py:1003-1009`) + `_step_dict`'s `fingerprint_*` siblings | **exact** |
| `firestarter_app/firestarter/chip_test.py` (`_aggregate_cycle_results` status fold) | service | transform | `run_status` (`chip_test.py:1992`) — the existing any-ERROR fold | role-match |
| `firestarter_app/firestarter/chip_test.py` (0/1/2 verdict migration, 2 sites) | service | request-response | `cli_handlers.py:1153-1187` `blank` handler — the shipped 0/1/2 consumer | role-match |
| `firestarter_app/firestarter/diagnostic_report.py` (tag append + report-dict key) | service (serializer) | transform | `dedup_fingerprint:307-325` coverage append; `_step_dict:924-935` | **exact** |
| `firestarter_app/firestarter/eprom_operations.py` (lease conditional) | service | event-driven | `_drive_region_compare`'s `on_result` (`:2592`) — default-`None` opt-in seam | role-match |
| `firestarter_app/firestarter/serial_comm.py` (`setup_command` extraction) | service (transport) | request-response | `_probe_port` (`:806-905`) — the code being split | **exact** (self-analog) |
| `firestarter_app/firestarter/cli_handlers.py` (`with … lease():`) | controller | request-response | `dev_test`'s `run_plan(...)` call (`:2940-2947`) — the `allow_single_run` opt-in pair | **exact** |
| `firestarter_app/tests/test_blast_radius_invariance.py` (new tag legs) | test | transform | `test_dedup_fingerprint_is_frozen` (`:313`) + `test_planted_mutation_clearing_write_fingerprint_reddens_the_gate` (`:771`) | **exact** |
| `firestarter_app/tests/test_chip_test*.py`, `test_dev_test_cmd.py` (verdict/lease legs) | test | request-response | `tests/test_wire_dict_equivalence.py:675` non-vacuity leg shape | role-match |

---

## Pattern Assignments

### `firestarter/chip_test.py` — the empty-default discriminator (DEVTEST-02)

**Analog:** `firestarter_app/firestarter/chip_test.py:1051-1079` (`COVERAGE_TAG_FULL_DEVICE` / `coverage_tag`). Second exemplar at `:1027-1049` (`REPEAT_POLICY_DEGRADED_TAG` / `repeat_policy_tag`). **Both confirmed at the lines the research gave.**

**Copy this shape exactly** (`chip_test.py:1051-1079`, verbatim):

```python
# The write-coverage discriminator (quick-devtest-coverage-dedup, follow-up
# to 260821-wna). Spelled as the `WriteTarget.region_policy` value it
# describes, not a bare "full-device" string repeated at call sites.
COVERAGE_TAG_FULL_DEVICE = "cov=full-device"


def coverage_tag(results: list[StepResult]) -> str:
    """`"cov=full-device"` when the run's write step resolved a full-device
    target; `""` on fixed/uv-slot, or when there is no write step.
    ...
    Locates the write step STRUCTURALLY, via `result.write_target is not None`
    -- set only on a write step's own result. This function must never compare
    `result.op` against an op-name constant.

    Returning `""` for fixed/uv-slot is load-bearing for the same reason as
    `repeat_policy_tag` above: only the strictly-stronger full-device shape gets
    tagged, so no historical grouping is re-keyed.
    """
    for result in results:
        if result.write_target is not None:
            if result.write_target.region_policy == REGION_POLICY_FULL_DEVICE:
                return COVERAGE_TAG_FULL_DEVICE
            return ""
    return ""
```

Four properties the new `compare_path_tag` must reproduce, each visible above:
1. A module-level `*_TAG` constant, never a bare string at the call site.
2. A `list[StepResult] -> str` free function, returning `""` for the **old/weaker** shape.
3. A docstring paragraph stating that the empty default is **load-bearing**, naming `dedup_fingerprint`'s skip-when-empty append and "no historical grouping is re-keyed".
4. **Structural** detection off a `StepResult` field whose default is falsy — `coverage_tag` keys on `write_target is not None`; `repeat_policy_tag` keys on `run_count == 1`. Never on `result.op`.

**The second exemplar's shorter body** (`chip_test.py:1044-1049`) is the closer template when the new tag needs no two-way branch:

```python
    for result in results:
        if result.op in _REPEAT_POLICY_OPS and result.run_count == 1:
            return REPEAT_POLICY_DEGRADED_TAG
    return ""
```

---

### `firestarter/diagnostic_report.py` — appending the tag to the hash

**Analog:** `diagnostic_report.py:302-327` (`dedup_fingerprint` body). **Confirmed; the research's `:302-325` is one line short of the `canonical`/`return` pair.**

**Call-site pattern to copy** (`diagnostic_report.py:307-309` and `:323-325`, verbatim):

```python
    policy = repeat_policy_tag(report.results)
    if policy:
        parts.append(policy)
    ...
    coverage = coverage_tag(report.results)
    if coverage:
        parts.append(coverage)
    canonical = "|".join(parts)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:12]
```

The new append goes **after** `coverage`, in the identical three-line shape, with a preceding block comment matching the one at `:310-322` (which is the in-source statement of the discipline itself and should be cited, not restated). The allow-list is exactly five entries — `chip`, `protocol`, the per-step `op=verdict:cls` triple, `repeat_policy_tag`, `coverage_tag` — and the loop is at `:298-301`:

```python
    for result in report.results:
        cls = result.fingerprint.classification if result.fingerprint else ""
        parts.append(f"{result.op}={result.verdict}:{cls}")
```

**This loop is the whole reason Pitfall 1 exists.** Any new `Fingerprint` on a step that has none today moves `cls` from `""` to a real string.

---

### `firestarter/chip_test.py` + `diagnostic_report.py` — additive, NON-hashed evidence (DEVTEST-01)

**Analog:** `diagnostic_report.py:848-858` (the `_step_dict` docstring paragraph) and `:924-935` (the emission).

**The argument to copy** (`diagnostic_report.py:848-855`, verbatim):

```
        The four `fingerprint_*` siblings (RPT-A2) are read straight off the
        `Fingerprint` the classifier already produced -- `total`, `bad`,
        `bad_pct`, `evidence` -- so this is a serialization change with no
        new computation and no second classifier. `fingerprint` keeps
        carrying the classification string alone, because that string is
        the only fingerprint component `dedup_fingerprint` hashes; the four
        siblings are therefore additive and cannot re-key a filed report.
```

**The emission** (`diagnostic_report.py:924-936`, verbatim):

```python
            "fingerprint": (
                result.fingerprint.classification if result.fingerprint else None
            ),
            "fingerprint_total": (
                result.fingerprint.total if result.fingerprint else None
            ),
            "fingerprint_bad": (result.fingerprint.bad if result.fingerprint else None),
            "fingerprint_bad_pct": (
                result.fingerprint.bad_pct if result.fingerprint else None
            ),
            "fingerprint_evidence": (
                result.fingerprint.evidence if result.fingerprint else None
            ),
            "divergence": result.divergence,
```

Note the unconditional keying — **every** step element carries the key, `None` when inapplicable. A new blank-check evidence key follows that rule.

**The `StepResult` field pattern** (`chip_test.py:988-1009`, verbatim — the three additive fields all carry an in-field comment saying why they are NOT hashed):

```python
    # Wall-clock seconds for the whole step, stamped by `_run_step`'s timing
    # wrapper ...
    # Deliberately NOT part of `dedup_fingerprint`, which excludes every
    # volatile field so two runs of the same chip still dedup.
    duration_s: float | None = None
    # The write step's resolved `WriteTarget`
    # -- additive, `None` on every step that isn't a write ...
    write_target: WriteTarget | None = None
    status: str = STATUS_COMPLETE
```

`class StepResult` is at `chip_test.py:949`; the field block runs `:986-1009`. **A new field must default to `None`/falsy** — that is what makes the 19 frozen hashes provably immobile for hand-built and JSON-reconstructed `StepResult`s.

---

### `firestarter/chip_test.py` — the two `== 0` adapters (DEVTEST-01/03)

**Blank-check adapter, confirmed at `chip_test.py:2592-2624`** (research said ~2600; the `is_ok` line is `:2600`, the `StepResult` is `:2619-2625` — both correct). Verbatim, the shape the migration replaces:

```python
        is_ok = operator.check_eprom_blank(name, eprom_data) == 0
        ...
        code, message = (None, "") if is_ok else _firmware_error(operator)
        if is_ok:
            verdict = VERDICT_OK
        elif step.uv_prewrite:
            verdict = VERDICT_SKIPPED
        else:
            verdict = VERDICT_BAD
        return StepResult(
            op=step.op,
            verdict=verdict,
            reason=message,
            error_code=code,
            run_count=1,
        )
```

Five keywords, **no `fingerprint=`**. Confirmed.

**Verify adapter, confirmed at `chip_test.py:3247-3260`:**

```python
            elif op == OP_VERIFY:
                # 202-01 D-10: verify_eprom now returns an int (0 == match),
                # not a bool. The == 0 adapter here is what keeps `outcomes`
                # a list of bools ...; the real migration is phase 206's job.
                outcomes.append(
                    operator.verify_eprom(...) == 0
                )
```

**Verdict/status construction analog for the verdict-2 arm** — `_run_step_untimed`'s transport arm (`chip_test.py:2521-2528`, confirmed) is the shipped precedent for a two-axis "did not really run" outcome:

```python
    except (SerialError, HardwareOperationError) as exc:
        return StepResult(
            op=step.op,
            verdict=VERDICT_SKIPPED,
            status=STATUS_ERROR,
            reason=str(exc),
            run_count=1,
        )
```

**Copy `status=STATUS_ERROR` alongside `verdict=VERDICT_SKIPPED`, never one without the other** — `VERDICT_SKIPPED` alone exits 0.

---

### `firestarter/chip_test.py` — `_aggregate_cycle_results` (Pitfall 2)

**Confirmed at `chip_test.py:1248-1311`.** The `len(results) == 1` early return is `:1279-1280`; the nine-keyword constructor is `:1297-1311` and carries **no `status=`**:

```python
    return StepResult(
        op=op,
        verdict=verdict,
        reason=reason,
        error_code=next(
            (r.error_code for r in results if r.error_code is not None), None
        ),
        fingerprint=next((r.fingerprint for r in reversed(ran) if r.fingerprint), None),
        run_count=len(ran),
        divergence=next((r.divergence for r in reversed(ran) if r.divergence), None),
        duration_s=round(sum(durations) / len(durations), 3) if durations else None,
        write_target=next(
            (r.write_target for r in reversed(ran) if r.write_target is not None), None
        ),
    )
```

**Fold analog for the fix:** `run_status` (`chip_test.py:1992`) — the existing any-step-ERROR-wins reduction. Mirror its polarity here with a `next((… STATUS_ERROR …), STATUS_COMPLETE)` in the same `next(...)` idiom every sibling keyword already uses.

---

### `firestarter/eprom_operations.py` — the lease seam (SESS-01)

**Teardown confirmed at `eprom_operations.py:698-710`** (the research's `:701-705`/`:707-710` are correct):

```python
        operation_name = COMMAND_NAMES[cmd]
        try:
            # Yield the necessary data to the 'with' block
            yield command_dict, buffer_size, operation_name
        finally:
            # This block ensures disconnection happens even if errors occur
            self._disconnect_programmer()

    def _disconnect_programmer(self):
        if self.comm:
            self.comm.disconnect()
            self.comm = None
```

**Default-off opt-in analog — use `on_result` (`eprom_operations.py:2584-2624`).** It is the closest shipped seam: keyword-only, default `None`, with a docstring that states byte-identical behaviour when unset.

```python
    def _drive_region_compare(
        self, cmd_data: dict, op_name: str, expected: Callable[[int, int], bytes],
        *, full: bool, region_length: int | None,
        on_result: Callable[[CompareResult], None] | None = None,
    ) -> int:
```
```
        `on_result` (Phase 203, WRITE-01): keyword-only, default `None`.
        When `None`, behaviour is byte-identical to before this parameter
        existed ... `verify_eprom` and `check_eprom_blank` pass nothing and
        stay byte-identical.
```

**Second default-off analog — `allow_outdated_firmware` (`serial_comm.py:812`, doc at `:817-823` and `:886-905`).** Its governing sentence is the one to copy for the lease flag: *"The waiver is an explicit caller opt-in, never inferred from the command dict, so a chip operation cannot acquire it by accident or by crafting a command."*

**Third — the belt-and-braces pair at the caller**, `cli_handlers.py:2933-2947`, which is the exact call the lease `with` wraps:

```python
    # fail-closed guard. Both are required deliberately -- a caller that
    # passes `runs=1` alone still fails the whole plan, so the weaker policy
    # can only ever be reached on purpose. The default path passes neither
    # and is byte-for-byte the pre-existing call.
    results = run_plan(
        plan,
        app.eprom_operator,
        app.db,
        runs=1 if fast else _DEFAULT_RUNS,
        allow_single_run=fast,
        sampler=sampler,
    )
```

`_DEFAULT_RUNS = 3` at `cli_handlers.py:2845`; `def dev_test` at `:2876`. Confirmed.

---

### `firestarter/serial_comm.py` — extracting `setup_command` from `_probe_port`

**Self-analog: `_probe_port` at `serial_comm.py:806-905+`.** The half to extract begins at `:849`:

```python
            communicator.send_json_command(command_to_send)
            is_ok, msg = communicator.expect_ack()

            if msg == GENERIC_FRAME_DECODE_ERROR_TEXT:
                ...
                setup_ack_deadline = time.time() + SETUP_ACK_RECOVERY_TIMEOUT_S
                while msg == GENERIC_FRAME_DECODE_ERROR_TEXT:
                    remaining = setup_ack_deadline - time.time()
                    if remaining <= 0:
                        break
                    is_ok, msg = communicator.expect_ack(timeout=remaining)

            if not is_ok:
                logger.debug(f"Port {port_name} responded but not with OK: {msg}")
                communicator.disconnect()
                return None
```

Then the firmware-version gate (`:868-905`) and the hardware-revision gate below it. `find_and_connect` signature at `:966-976`. `CONNECTION_STABILIZE_DELAY = 2.0` at `:84`, slept at `:204`. `SETUP_ACK_RECOVERY_TIMEOUT_S = 2.0` at `:86`. **All confirmed.**

**Drain analog (Pitfall 4):** `consume_remaining_input` at `serial_comm.py:597-612` and its use inside `disconnect` at `:617`:

```python
    def consume_remaining_input(self, timeout: float = 0.5) -> None:
        """Consumes and logs any pending input from the serial buffer."""
        if not self.is_connected():
            return
        ...
        original_timeout = self.connection.timeout
        self.connection.timeout = 0.05
        try:
            for _ in self._read_and_parse_lines(timeout):
                pass
        finally:
            self.connection.timeout = original_timeout
```

A leased setup must call this **before** each reuse, because `disconnect()` is the only caller today.

---

### `firestarter/compare.py` — consumed, not modified

**Read-only for this phase.** The blank/contact-first ordering is at `compare.py:444-454` (research said `:447-454`; the governing comment starts at `:444`):

```python
    # 1. blank/contact: read-back is near-all 0xFF (un-driven bus / contact
    # fault). Checked first regardless of whether there are zero mismatches
    # (a perfect verify) or the pattern never matched at all.
    if ff_ratio >= _FF_RATIO_THRESHOLD:
        return Fingerprint(..., classification=FP_BLANK_CONTACT, ...)
```

This is the mechanical reason a blank-check `Fingerprint` would classify `blank/contact`, not `match`. `compare.py` is AST-enforced import-pure — **no plan may widen it.**

---

### `tests/test_blast_radius_invariance.py` — the DEVTEST-02 gate + non-vacuity

**Analog 1 — the absolute-literal gate** (`tests/test_blast_radius_invariance.py:312-327`, verbatim):

```python
@pytest.mark.parametrize("shape_id,expected", sorted(FROZEN_HASHES.items()))
def test_dedup_fingerprint_is_frozen(shape_id: str, expected: str) -> None:
    """A GATE, not a claim. Pinning the literal -- rather than asserting two
    shapes agree with each other -- is what makes a re-key visible instead
    of silently forking every historical count_agreeing group."""
    from firestarter.diagnostic_report import dedup_fingerprint

    report = build_shape(shape_id)
    computed = dedup_fingerprint(report)
    assert computed == expected, (
        f"{shape_id} re-keyed: expected {expected}, got {computed}. If "
        "deliberate, land the behaviour change and the re-key of this "
        "literal as SEPARATE commits, so the re-key stays a reviewable unit."
    )
```

**Gate on this module, never on `tests/test_diagnostic_report.py`** — the module docstring (`:1-16`) states that eleven relational comparisons there *"pass vacuously through ANY change to the hash function itself"*.

**Analog 2 — the planted-mutation non-vacuity leg, and the better precedent than `test_the_197_delta_layer_is_capable_of_failing`** because it is in the same module, against the same hash (`tests/test_blast_radius_invariance.py:771-794`, verbatim):

```python
def test_planted_mutation_clearing_write_fingerprint_reddens_the_gate() -> None:
    """Leg 2 of the anti-vacuity contract, in-process axis 1: clearing the
    write step's fingerprint is the exact change Phase 177 will make ...
    Asserts inequality against the frozen literal, never against a second
    computed value."""
    from firestarter.diagnostic_report import dedup_fingerprint

    report = build_shape(_TRACER_SHAPE_ID)
    write_result = next(r for r in report.results if r.op == "write")
    write_result.fingerprint = None
    assert dedup_fingerprint(report) != FROZEN_HASHES[_TRACER_SHAPE_ID]


def test_planted_mutation_lowering_chip_name_reddens_the_gate() -> None:
    """Leg 2, in-process axis 2: mutating `auto_capture.chip` shows the gate
    sensitive on the OTHER axis `dedup_fingerprint` reads ..."""
    report = build_shape(_TRACER_SHAPE_ID)
    report.auto_capture.chip = "sst27sf512"
    assert dedup_fingerprint(report) != FROZEN_HASHES[_TRACER_SHAPE_ID]
```

Wave 0's "the new tag is capable of moving the hash" leg is this shape with `_TRACER_SHAPE_ID`'s relevant step's new field **set**, asserting `!=` the frozen literal. Its sibling, "a default `StepResult` is untagged", is `test_dedup_fingerprint_is_frozen` itself, already parametrized over all 19.

**Analog 3 — the additive-key-does-not-re-key test** (`:329-347` `test_schema_bump_rekeys_no_frozen_hash`) is the template for a DEVTEST-01 leg asserting the new **non-hashed** evidence field re-keys nothing. Copy its `assert len(FROZEN_HASHES) == 19` count pin and its failure message naming "the allow-list grew a reflective read".

**Analog 4 — the pure non-vacuity idiom**, `tests/test_wire_dict_equivalence.py:675-711`, for a leg outside the frozen-hash corpus: compose the real state, deep-copy, mutate exactly one field, then assert **both** that a diff appears *and* that it names exactly the mutated key:

```python
    assert diff != "(no difference detected)", (
        "non-vacuity failure: ... the 197 delta layer's gate is "
        "incapable of failing"
    )
    assert diff == f"changed={{'{some_key}': ['pulse-delay']}}", (
        f"the failure-capability leg must report EXACTLY the one mutated "
        f"record {some_key!r} and no other -- got: {diff}"
    )
```

---

### Plan-shape analog — `205-01-PLAN.md` (the closest prior host-routing change)

**Source:** `/workspaces/.planning/phases/205-the-pre-flights-leave-the-firmware/205-01-PLAN.md`

That plan moved `erase -b`'s blank check onto the Phase 202 host engine with a 0/1/2 exit contract — the same migration shape DEVTEST-01/03 needs. Copy four things:

**1. The `<read_first>` block is exhaustive and reasoned, not a file list** (`205-01-PLAN.md:222-238`). Each entry names the line range *and why*, e.g.:

```
    - `firestarter_app/firestarter/eprom_operations.py:2971-3059` — `check_eprom_blank` in full. Read its return contract (0 all-blank, 1 at least one non-blank byte, 2 setup or transport failure or refusal), its `full: bool = False` default, and its pre-wire SRAM/FRAM short-circuit which returns 2 rather than 1. Erase never runs on SRAM, so that arm is inert here — read it so the inertness is a measured fact rather than an assumption.
```

It also points back at its own PATTERNS.md by section name (`:238`) — do the same for this file.

**2. `<behavior>` enumerates one line per outcome of the verdict contract** (`:241-246`) — one bullet per 0/1/2 arm plus the untouched default path. The 206 verdict migration should enumerate its arms the same way.

**3. `<verify>` pairs every `<automated>` with a `<fails_when>` that names the fail-open modes explicitly** (`:311-321`). The reusable legs, verbatim:

```
    <automated>cd /workspaces/firestarter_app && .venv311/bin/python -m pytest tests/test_cli_handlers.py -k erase -o addopts="" -p no:cacheprovider -v</automated>
    <fails_when>non-zero exit, or any line in the per-test listing reads FAILED or ERROR, or the summary reads "no tests ran" — a `-k` filter that silently matches nothing exits 0 and must be treated as failure</fails_when>
    <automated>cd /workspaces/firestarter_app && .venv311/bin/python -m pytest tests/ -o addopts="" -p no:cacheprovider -q</automated>
    <fails_when>non-zero exit, or any FAILED line, or a passed count below the 2309 baseline recorded in 205-VALIDATION.md § Measured baselines</fails_when>
    <automated>cd /workspaces/firestarter_app && .venv311/bin/ruff check firestarter/ tests/ && .venv311/bin/ruff format --check firestarter/ tests/</automated>
    <fails_when>non-zero exit, or any line matching "would reformat", or any diagnostic code printed by the check pass</fails_when>
```

Note `.venv311/bin/python`, `-o addopts=""`, `-p no:cacheprovider`, and a **numeric passed-count baseline** — all four are required by project constraints (`-o addopts=""` because the project's `-ra -q` hides the count line).

**4. The source-assertion leg** (`:320-321`) — a `python -c` that opens the file and asserts named symbols are present/absent, each with its own AssertionError message, ending in a printed confirmation line that `<fails_when>` also requires:

```
    <automated>cd /workspaces/firestarter_app && .venv311/bin/python -c "import pathlib; s=pathlib.Path('firestarter/cli_handlers.py').read_text(); assert '_ERASE_SECTOR_BLANK_REFUSAL' in s, 'the refusal format constant is absent'; assert '_erase_sector_blank_refusal_exit_code' in s, 'the refusal helper is absent'; print('OQ-1 refusal present')"</automated>
    <fails_when>non-zero exit — an AssertionError names the missing symbol — or the confirmation line is missing from stdout</fails_when>
```

**Also copy `<reversibility rating=…>` per task** (`:217`, `:328`) — SESS-01's lease task is the natural place, and its rating should be the opposite (`reversible`, with the one-commit revert stated).

---

## Shared Patterns

### Empty-default discrimination
**Source:** `chip_test.py:1027-1079` (two exemplars) + `diagnostic_report.py:310-325` (the discipline, stated in-source).
**Apply to:** every DEVTEST-02 change. The direction is fixed: **old/firmware/unknown → `""`, new/host → a literal tag.**

### Additive-but-unhashed evidence
**Source:** `diagnostic_report.py:848-855` + `:924-936`; `chip_test.py:988-1009`.
**Apply to:** every DEVTEST-01 field. Field defaults falsy; report-dict key emitted unconditionally with `None`; an in-field comment stating it is deliberately outside `dedup_fingerprint`.

### Default-off, explicitly-opted-in seam
**Source:** `eprom_operations.py:2584-2624` (`on_result`), `serial_comm.py:812/886-905` (`allow_outdated_firmware`), `cli_handlers.py:2933-2947` (`allow_single_run` + the fail-closed pair comment).
**Apply to:** SESS-01's lease. Keyword-only, default off, **one** caller opts in, docstring asserts the unset path is byte-identical.

### Comments are load-bearing design records
**Source:** every excerpt above. The no-comments rule was removed 2026-09-19. Each of these functions carries a paragraph explaining *why* the shape is what it is; new code in these files must match that density.

### Verification idioms
**Source:** `205-01-PLAN.md:311-321`.
`.venv311/bin/python` (never bare `python3`), `-o addopts=""`, `-p no:cacheprovider`, numeric count baselines, `<fails_when>` naming the fail-open mode, `ruff check` + `ruff format --check` on `firestarter/ tests/` only. **mypy is not a CI gate.**

---

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| `firestarter_app/firestarter/eprom_operations.py` — `EpromOperator.lease()` contextmanager | service | event-driven | **No lease/reuse seam exists anywhere in the host tree.** `preferred_port`/`restrict_to_port` (`eprom_operations.py:577-592`) are a port-*identity* workaround, not a lease. The nearest structural analog is `_operation_context` itself (`:655-705`), which is a `@contextmanager` on the same class — copy its decorator/`try/finally` shape, but the semantics are new. |
| `206-SESSION-COST.md` | doc | — | Structural analog exists and must be followed: `/workspaces/.planning/phases/205-the-pre-flights-leave-the-firmware/205-SESSION-COST.md` (§1 what is counted, §2 measured with N + min/max, §3 derivation labelled as such, §4 explicit non-measurement statement, §5 provenance). Not a code analog. |
| SESS-02's bench leg | test (manual) | — | No automatable analog by construction — `checkpoint:human-verify`, never `<automated>`. |

---

## Metadata

**Analog search scope:** `firestarter_app/firestarter/` (chip_test, diagnostic_report, compare, eprom_operations, serial_comm, cli_handlers), `firestarter_app/tests/` (blast_radius_invariance, wire_dict_equivalence, fixtures/report_shapes), `.planning/phases/205-*/`.
**Scan method:** `git grep` and `sed -n` from inside the submodule — **never** the devcontainer's ugrep-backed `grep`.
**Tracked-source gate:** every source path above confirmed by `git ls-files` inside `firestarter_app`. No gitignored mirror paths emitted.
**Citation re-verification:** all line ranges re-opened this session against `firestarter_app` `2756ef0`. Three of the research's approximations were tightened (`diagnostic_report.py:302-325`→`:302-327`; `compare.py:447-454`→`:444-454`; `_step_dict` docstring `:849-855`→`:848-855`). The rest were exact.
**Pattern extraction date:** 2026-09-23
