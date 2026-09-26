# Phase 177: Evidence-Gated Read-Back - Pattern Map

**Mapped:** 2026-09-05
**Files analyzed:** 9 (2 source, 3 test, 3 fixture/anchor, 2 meta-repo docs — 10 rows total)
**Analogs found:** 10 / 10

**Repo boundary (matters for every path below):** paths under `firestarter/` and `tests/` are
in the **`firestarter_app` sub-repo** (`/workspaces/firestarter_app`, branch
`gsd/v1.36-dev-test-fidelity`). Paths beginning `.planning/` and `tools/rekey/` are in the
**meta repo** (`/workspaces`). All paths listed here were confirmed git-TRACKED in their own
tree via `git ls-files`.

**Standing project rule that overrides every excerpt below:** *no comments are to be written
into source, at all.* Several of the analogs quoted here **do** carry `#` comments (they
predate the rule). Copy their *structure*, never their comments. The project's sanctioned home
for rationale in these modules is a **docstring** — every excerpt below shows a docstring
carrying the "why", and that is the part to imitate.

---

## File Classification

| New/Modified File | Repo | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|---|
| `firestarter/chip_test.py` — gate at `:3100` | app | service (engine) | request-response (device I/O decision) | the same file's existing `collect_fingerprint` gate + `classify_fingerprint` returns | exact (self-analog) |
| `firestarter/chip_test.py` — `_synthesized_match_fingerprint` (new helper) | app | utility / factory | transform (no I/O) | `classify_fingerprint`'s four `return Fingerprint(...)` sites, `chip_test.py:200-260` | exact |
| `firestarter/chip_test.py` — `prior_cycles_failed` threading | app | service | request-response | the `collect_fingerprint` keyword-only chain, `:2349 → :2394 → :2493 → :2922` | exact |
| `firestarter/chip_test.py` — `FP_MATCH` constant | app | config/constant | — | `FP_BLANK_CONTACT`…`FP_INDETERMINATE`, `:138-141` | exact |
| `tests/test_chip_test.py` — inverted read-back count | app | test | request-response | `test_fingerprint_readback_happens_once_not_once_per_cycle`, `:1507-1521` | exact (this test IS the one to invert) |
| `tests/test_chip_test_cycle.py` — cycle-1-fail/cycle-2-pass test | app | test | event-driven (stateful double) | `_cycle_operator`, `:56-88`; `_run`, `:91-104` | exact |
| `tests/fixtures/report_shapes.py` — register `prune03-synthesized-fingerprint-match`, re-key 5 hashes, re-point the gated shape | app | test fixture | frozen-hash table | `_build_sst27sf512_six_step_readback_gated`, `:197-219` + `_BUILDERS`/`FROZEN_HASHES`/`RESERVED_SHAPE_IDS`, `:599-650` | exact |
| `tests/fixtures/rekey_ledger.py` — append `RK-174-07`/`-08`, fill `after_hash` | app | test fixture (ast-parsed data) | — | the 6 existing `LEDGER` rows + the provenance docstring, `:1-109` | exact |
| `tests/fixtures/shape_ids.json` + `tests/fixtures/reports/*.json` | app | committed anchor / snapshot | file-I/O | `tools/snapshot_report_shapes.py` (regenerator, never hand-edit the reports) | exact |
| `.planning/MILESTONES.md` — ledger row + falsified-projection correction | meta | doc | — | the "Corrections measured by plan 174-03" table + the 6-row ledger table, `:14-45` | exact |
| `.planning/seeds/dev-test-adaptive-sequencing.md` — R1/R2 amendment | meta | doc | — | commit `380210ed` amending `.planning/seeds/py32f071-no-external-tool-fw-install.md` | exact |

---

## Pattern Assignments

### 1. `tests/test_chip_test.py` — the read-back *counting* test (roadmap criterion 1)

**Analog:** `firestarter_app/tests/test_chip_test.py:1507-1521` — this is not merely a model,
it is the exact test PRUNE-01 inverts. It passes green today.

**The operator double it fakes with** (`tests/test_chip_test.py:990-1023`):

```python
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
    op.sdp_lock.return_value = True
    op.sdp_unlock.return_value = True
    for name, value in returns.items():
        getattr(op, name).return_value = value
        getattr(op, name).side_effect = None
    return op
```

Supporting helpers, same file: `_REAL_DB = EpromDatabase(skip_local_override=True)` (`:297`),
`_plan_with_steps(*steps) -> Plan(name="M8720", steps=list(steps))` (`:1093-1094`),
`_result(results, op)` (`:1097-1101`).

**The whole existing test, verbatim** (`:1507-1521`):

```python
def test_fingerprint_readback_happens_once_not_once_per_cycle():
    """`collect_fingerprint` is True only on the final cycle. Without that
    gate the write and verify steps would each add a region read-back per
    cycle -- real cost on a full-device region, for a fingerprint that only
    ever describes the device's FINAL state."""
    operator = _mock_operator()
    plan = _plan_with_steps(
        Step(op=OP_WRITE, supported=True, reason="", destructive=True),
        Step(op=OP_VERIFY, supported=True, reason=""),
    )
    run_plan(plan, operator, _REAL_DB, runs=3)

    # One read-back for the write step, one for the verify step. NOT 3 + 3.
    assert operator.read_eprom.call_count == 2
```

**What to copy, and the two departures:**
1. Copy the shape exactly: `_mock_operator()` → `_plan_with_steps(write, verify)` →
   `run_plan(..., runs=3)` → assert on `operator.read_eprom.call_count`. This plan carries no
   `read` step and M8720 is non-UV, so `read_eprom.call_count` is *exactly* the fingerprint
   read-back count — that is why this analog is the counting seam and not a coincidence.
2. The assertion becomes `== 0`. The count `2` moves to `0`, not to `1`.
3. **Drop the `#` comment.** Fold its content into the docstring instead. The existing
   docstring's justification (a fingerprint "only ever describes the device's FINAL state")
   stays true under PRUNE-01 and should be preserved beside the new "and a passing run needs
   none at all" sentence.

**Sibling in the same file showing a `side_effect` list driving per-run outcomes**
(`:1525-1538`, `test_cycle_disagreement_still_reports_marginal`):

```python
    operator = _mock_operator()
    operator.write_eprom.side_effect = [True, False]
```

That is the mechanism the cycle-1-fail test needs — but with the *stateful* double below, not
this `Mock`-only one.

---

### 2. `tests/test_chip_test_cycle.py` — the cycle-1-fail / cycle-2-pass test (criterion 2)

**Analog:** `firestarter_app/tests/test_chip_test_cycle.py:56-104`.

**Why this double and not `_mock_operator`:** its `read_eprom` side-effect *seeks to the
absolute address* before writing, which is the property `_read_region` depends on. A double
that writes at offset 0 makes every region slice come back short and the test passes for the
wrong reason.

```python
def _cycle_operator(name: str, *, blank: bool = False):
    """A chip double that answers a REGION read correctly.

    `_read_region` slices the read-back file at the ABSOLUTE offset, because a
    real region read produces a hole-padded file (`_write_to_file` seeks to the
    address first). A double that writes at offset 0 makes every UV slot probe
    come back short, which silently turns a masked write into a SKIPPED step --
    so this double seeks, and the tests below would not pass without it.
    """
    eprom_data = resolve_chip(name, db=_REAL_DB)
    writes: list[tuple[str | None, bytes]] = []
    operator = Mock(spec=_OPERATOR_METHODS)
    operator.check_eprom_id.return_value = (True, eprom_data.get("chip-id") or 0)
    operator.check_eprom_blank.return_value = blank
    for method in ("verify_eprom", "erase_eprom", "sdp_lock", "sdp_unlock"):
        getattr(operator, method).return_value = True

    def _read(_name, data, output_file=None, address_str=None, size_str=None, **_kw):
        start = int(address_str, 0) if address_str else 0
        size = int(size_str, 0) if size_str else int(data.get("memory-size", 4096))
        with open(output_file, "wb") as handle:
            handle.seek(start)
            handle.write(b"\xff" * size)
        return True

    def _write(_name, _data, path, address_str=None, **_kw):
        with open(path, "rb") as handle:
            writes.append((address_str, handle.read()))
        return True

    operator.read_eprom.side_effect = _read
    operator.write_eprom.side_effect = _write
    return operator, writes
```

**The invocation pattern** (`:91-104`):

```python
def _run(name: str, *, runs: int = 2):
    operator, writes = _cycle_operator(name)
    plan = ct.derive_plan(name, _REAL_DB, write_scope="full")
    results = ct.run_plan(
        plan, operator, _REAL_DB, runs=runs, allow_single_run=runs < 2
    )
```

**What to copy:** call `_cycle_operator("M8720")`, then override
`operator.write_eprom.side_effect = [False, True]` (this *replaces* the `_write` recorder — if
the test also needs the recorded writes, wrap `_write` instead of replacing it), then
`ct.derive_plan` + `ct.run_plan(..., runs=2)` and assert `operator.read_eprom.call_count > 0`.
Note the module's own `_REAL_DB = EpromDatabase()` (`:23`) differs from
`test_chip_test.py`'s `skip_local_override=True` — use whichever module you author in.

---

### 3. `firestarter/chip_test.py` — threading `prior_cycles_failed` down (PRUNE-02)

**Analog:** the `collect_fingerprint` keyword-only chain in the same file. This is the house
mechanism, it already exists end to end, and the new flag should ride the identical four hops.

**Hop 1 — `_run_step`** (`:2349-2392`), signature + pass-through:

```python
def _run_step(
    name: str,
    step: Step,
    operator: Any,
    db: Any,
    *,
    runs: int,
    sampler: Any = None,
    write_context: WriteContext | None = None,
    collect_fingerprint: bool = True,
) -> StepResult:
    """Time `_run_step_untimed` and stamp `duration_s` on its result.
    ...
    `write_context` is threaded through
    unchanged to `_run_step_untimed`; `None` is the default ...
    """
    start = time.monotonic()
    result = _run_step_untimed(
        name,
        step,
        operator,
        db,
        runs=runs,
        sampler=sampler,
        write_context=write_context,
        collect_fingerprint=collect_fingerprint,
    )
```

**Hops 2–4** repeat the identical `*,`-keyword-only + explicit-kwarg-forward shape:
`_run_step_untimed` (`:2394`, `:2403`), `_dispatch_step` (`:2493`, forwarded at `:2562`),
`_dispatch_multi_run` (`:2922`, `:2932`). Note house style: **keyword-only** (after `*`),
**explicitly typed**, **defaulted**, forwarded by name at every call — never `**kwargs`.

**The producer site — `_run_cycle_block`'s loop** (`:1538-1551`):

```python
        for cycle in range(cycles):
            write_context.cycle_index = cycle
            final = cycle == cycles - 1
            for i in live:
                step = steps[i]
                result = _run_step(
                    name,
                    step,
                    operator,
                    db,
                    runs=1,
                    sampler=sampler,
                    write_context=write_context,
                    collect_fingerprint=final,
                )
                per_step[i].append(result)
```

`per_step` is created at `:1514` as `[[] if r is None else [r] for r in pre]`, so at the moment
the final cycle calls `_run_step`, `per_step[i]` already holds cycles 1..N-1 — the predicate is
computable right there, exactly where `final` is.

**The membership set to filter on** — `_RAN_VERDICTS` (`:3495`), used for precisely this
discrimination by `_aggregate_cycle_results` (`:1306`):

```python
    ran = [r for r in results if r.verdict in _RAN_VERDICTS]
```

Copy that filter idiom; a SKIPPED/NA prior cycle is not a failure.

**Docstring precedent for the rationale** — `_run_cycle_block`'s own docstring (`:1500-1504`)
already records the fingerprint-gating "why" in prose, comment-free:

```python
    """...
    `collect_fingerprint` is True only on the FINAL cycle. Without that the
    write and verify steps would each add a region read-back per cycle,
    turning the fingerprint's one extra read into N -- real cost on a
    full-device region, for a fingerprint that only ever describes the
    device's final state anyway.
    """
```

**This paragraph is the model for where PRUNE-02's rationale goes.** Extend this docstring and
`_dispatch_multi_run`'s; write no `#` comment. (`_run_cycle_block`'s body at `:1516-1530` does
carry a long `#` block — that is pre-existing and must not be treated as licence.)

---

### 4. `firestarter/chip_test.py` — the synthesizing `Fingerprint` constructor (PRUNE-03)

**Analog:** the four terminal `return Fingerprint(...)` sites inside `classify_fingerprint`.
There is no separate factory in the module today, so these returns *are* the construction
house style: every field named, `evidence` a plain dict built up front.

**The dataclass** (`:151-159`):

```python
@dataclass
class Fingerprint:
    """Verdict + raw evidence for a single expected-vs-actual byte compare."""

    total: int
    bad: int
    bad_pct: float
    classification: str
    evidence: dict = field(default_factory=dict)
```

**The `evidence` key set to mirror exactly** (`:190-195`):

```python
    evidence: dict = {
        "ff_ratio": ff_ratio,
        "repeat_divergent": repeat_divergent,
        "first_offset": first_offset,
        "bit_clustering": {},
    }
```

**A construction site, verbatim** (`:254-260`, the `indeterminate` terminal):

```python
    return Fingerprint(
        total=cmp_len,
        bad=bad,
        bad_pct=bad_pct,
        classification=FP_INDETERMINATE,
        evidence=evidence,
    )
```

**The classification-constant block to extend** (`:138-141`):

```python
FP_BLANK_CONTACT = "blank/contact"
FP_ADDRESS_LINE = "address-line"
FP_TRANSPORT = "transport"
FP_INDETERMINATE = "indeterminate"
```

Add `FP_MATCH = "match"` in that block, same flat module-constant style, no comment.

**Ordering constraint the planner must respect (Pitfall 2 / Open Question 2):** the *first*
test in `classify_fingerprint` is `if ff_ratio >= _FF_RATIO_THRESHOLD:` (`:200-207`), and it is
first **deliberately** — the docstring at `:197-199` says so. A `bad == 0` early return placed
above it silently re-keys the `blank/contact` population. If `classify_fingerprint` gains the
bucket at all, it goes **after** the `ff_ratio` test and **after** the address-line test, and
`gh23-w27e257-fail` (the only frozen `blank/contact` shape) must be measured as unmoved.

---

### 5. `tests/fixtures/report_shapes.py` — the frozen-shape registration and re-key

**Analog for a hand-specified builder:** `_build_sst27sf512_six_step_readback_gated`
(`:197-219`) — note it exists *specifically* as this phase's projected after-shape, and
RESEARCH.md has falsified its value:

```python
def _build_sst27sf512_six_step_readback_gated() -> DiagnosticReport:
    """The PROJECTED after-shape of `RK-174-01-p177-readback-gating`
    (`tests/fixtures/rekey_ledger.py`) -- Phase 177 gates the fingerprint
    read-back on step failure, which empties the write/verify steps'
    `indeterminate` classification. ... This is NOT yet the declared
    after_hash -- the ledger row's `after_hash` stays `None` until Phase 177
    actually lands (D-11)."""
    return build_shape_from_step_specs(
        chip="SST27SF512",
        protocol="7",
        step_specs=[
            ("id", "OK", None, ""),
            ("read", "OK", None, ""),
            ("write", "OK", None, ""),
            ("verify", "OK", None, ""),
            ("erase", "OK", None, ""),
            ("blank-check", "OK", None, ""),
        ],
    )
```

The `step_specs` tuple grammar is `(op, verdict, fingerprint_classification, tag)`. A
post-PRUNE-03 passing write/verify has `"match"` in slot 3, not `None`. **This is where
Open Question 3 lands: re-point these `step_specs` to a genuinely distinct shape (a failing
write/verify keeping a real read-back classification) rather than deleting the builder.**

**Analog for a real-path builder** (`:590-596`):

```python
    return _build_real_path_report(
        chip="w27e257", write_scope="full", operator=_fixed_return_operator(), runs=2
    )
```

**The four-way closure the planner must edit together.** `tests/test_blast_radius_invariance.py`
enforces all four at once (`test_shape_ids_frozen_hashes_ladder_pins_and_snapshots_agree`),
so a new `shape_id` is never a one-file edit:

1. `_BUILDERS` (`:599-617`) — the dict of `shape_id -> callable`;
   `SHAPE_IDS = tuple(sorted(_BUILDERS))` (`:618`) derives from it.
2. `FROZEN_HASHES` (`:620-637`) — a flat `dict[str, str]` of 12-hex values.
3. `RESERVED_SHAPE_IDS` (`:639-645`) — **`"prune03-synthesized-fingerprint-match"` is already
   reserved for this phase**; registering it means *removing* it from this frozenset and adding
   it to `_BUILDERS`, or the `assert not (set(SHAPE_IDS) & RESERVED_SHAPE_IDS)` at `:647-650`
   fires by design.
4. `tests/fixtures/shape_ids.json` — the committed sorted anchor. Its own `_note` states the
   rule: *"Edited only in the same commit that adds or removes a builder in report_shapes.py --
   never on its own."*

**Editing one frozen hash looks like exactly this** (in `FROZEN_HASHES`, `:635-636`):

```python
    "sst27sf512-full-all-ok": "4b3e52cab987",
    "w27e257-full-all-ok": "22908e2954c3",
```

— one string literal replaced by the **re-measured** value. Never by a value transcribed from
RESEARCH.md; every number there is a projection of an unimplemented change.

**`tests/fixtures/reports/*.json` are never hand-edited.** Regenerate with
`firestarter_app/tools/snapshot_report_shapes.py`, which stamps a `_generated_by` key as its
do-not-edit banner and carries a `--check` drift mode (`:1-25`).

---

### 6. `tests/fixtures/rekey_ledger.py` — appending a ledger row

**Analog:** the six existing `LEDGER` rows plus the per-row provenance paragraph in the module
docstring (`:1-109`). The file is `ast.literal_eval`-parsed by the meta checker and must stay
logic-free.

**The row grammar** (`:79-109`):

```python
LEDGER = (
    ("sst27sf512-six-step", "4dc282a5d596", None, "RK-174-01-p177-readback-gating"),
    (
        "at28c256-full-all-ok-sdp",
        "52fb759dc48c",
        None,
        "RK-174-05-p177-match-bucket-d4d6",
    ),
    (
        "sst27sf512-full-all-ok",
        "4b3e52cab987",
        None,
        "RK-174-06-p178-status-axis-must-not-rekey",
    ),
)
```

Tuple is `(shape_id, before_hash, after_hash, ledger_id)`; `ledger_id` grammar is
`RK-174-<NN>-<owner>-<slug>`. `after_hash` is `None` until declared.

**The matching provenance paragraph** (docstring, `:27-34`) — every row has one, and a new row
needs one in the same voice:

```
  RK-174-01-p177-readback-gating -- shape_id `sst27sf512-six-step`. Owner:
  Phase 177. Mechanism: gating the fingerprint read-back on step failure
  empties the `write`/`verify` steps' `indeterminate` fingerprint
  classification. Measured PROJECTED `after_hash` (not yet declared):
  `60a031573aab`. A projected value belongs here in prose and in
  `MILESTONES.md`'s prose, never in the `after_hash` column ...
```

**Append, never edit** (D-09): new rows `RK-174-07-p177-…` / `RK-174-08-p177-…` for
`sst27sf512-full-all-ok` and `w27e257-full-all-ok`; the existing `RK-174-06` row's `before_hash`
is never overwritten. The `RK-174-01` provenance paragraph's `60a031573aab` is now a *falsified*
projection — correct it in prose, in the declaration commit.

---

### 7. `.planning/MILESTONES.md` — the meta-repo half of the declaration

**Analog:** `/workspaces/.planning/MILESTONES.md:38-44`. Two structures the planner reuses:

**The ledger table row** (`:39`):

```
| RK-174-01-p177-readback-gating | sst27sf512-six-step | gate the fingerprint read-back on step failure | Phase 177 | 4dc282a5d596 | (undeclared) | (pending) |
```

Columns: `ledger_id | shape_id | change | owner | before | after | declared`. Declaring means
`(undeclared)` → the measured hash and `(pending)` → the date, in the **same commit** as the
app-side `after_hash` edit *for its own tree* (they are two repos — Pitfall 7).

**The corrections table** (`:20-26`) is the sanctioned home for the falsified `60a031573aab`
projection — this project has a standing rule against silently absorbing a measured
disagreement, and that table exists for exactly this:

```
| Claim | As inherited | As measured |
|---|---|---|
| m27c512 canonical-naming pair | `a00791f1c2b4` → `a6f6c6354047` (not reproducible) | `6d3afbc52315` → `776846bf2dc8` (`m27c512` → `M27C512`), both measured this session |
```

**The protocol prose to obey** (`:41`, quoted in RESEARCH.md): behaviour commit lands and turns
the gate RED; a *separate* commit fills `after_hash` and this table's row; `before` is never
overwritten.

**Cross-tree acceptance evidence:** `python3 tools/rekey/check_rekey_ledger.py` run from
`/workspaces` against the populated `firestarter_app` submodule.

---

### 8. `.planning/seeds/dev-test-adaptive-sequencing.md` — the seed amendment (PRUNE-07)

**Analog:** commit `380210ed` (`docs(129-08): seed status reflects the fired trigger …`),
which amended `.planning/seeds/py32f071-no-external-tool-fw-install.md` — 50 insertions,
1 deletion. It is the only prior seed amendment of this shape in the tree.

**What the edit looked like — frontmatter, one field, schema unchanged:**

```diff
 title: PY32F071 firmware install with no external tools ...
 trigger_condition: v1.28 PY32F071 Port is activated, OR ...
 planted_date: 2026-07-28
-status: dormant
+status: partially realised — the factory-USB-DFU runner-up shipped in v1.23 (the trigger fired); the self-flash primary route has not, and the seed stays live for FUT-N05
 ---
```

**And the body — a dated, headed amendment block appended, not an in-place rewrite:**

```
+**Phase 129, 2026-08-02.** This trigger has now fired, and half of this seed
+shipped while the other half did not.
+
+1. **The trigger fired.** ...
```

**Current target frontmatter** (`dev-test-adaptive-sequencing.md:1-6`) has the identical
four-field schema and `status: dormant`, with `trigger_condition: Next milestone that touches
'dev test' / chip_test.py`. v1.36 **is** that milestone — RESEARCH.md flags flipping `status`
as a judgement the planner must make explicitly rather than leave.

**Two departures from the analog, forced by criterion 5:** PRUNE-07 requires R1's contradicting
paragraph to be *replaced in place* (an appended block alone would leave the destructive
sentence readable and regenerable), and R2 to be *extended*. So: in-place replacement of R1's
final paragraph + an append to R2, plus the analog's dated-block convention for the "why" if
the planner wants the provenance visible. RESEARCH.md `§The seed's self-contradiction` supplies
candidate wording for both.

**Commit-message shape from the analog:** `docs(177-NN): <what changed>` with a bulleted body
naming the decision IDs (`D-17`, `PCB-01` in the analog → `D-1`, `PRUNE-07` here) and an
explicit statement of what was *not* touched.

---

## Shared Patterns

### Keyword-only, defaulted, explicitly-forwarded flags
**Source:** `firestarter_app/firestarter/chip_test.py:2349-2392` (and the same shape at
`:2394`, `:2493`, `:2922`)
**Apply to:** the new `prior_cycles_failed` parameter, at all four hops
Flags in this engine are declared after `*`, typed, defaulted to the non-surprising value, and
forwarded **by name** at every call site. No `**kwargs`, no positional threading.

### Rationale goes in a docstring, never a comment
**Source:** `firestarter_app/firestarter/chip_test.py:1500-1504` (`_run_cycle_block`) and
`:197-199` (`classify_fingerprint`'s ordering justification)
**Apply to:** every source edit in this phase
The operator's standing rule forbids new `#` comments outright, and a plan cannot override it.
Existing comments in these files are pre-existing; leave them, do not add to them. Phase 175-05
audited "zero comments" as a phase-seal criterion — expect the same here.

### `_RAN_VERDICTS` is the "this cycle reached the operator" filter
**Source:** `firestarter_app/firestarter/chip_test.py:3495` (definition), `:1306` (canonical use
`ran = [r for r in results if r.verdict in _RAN_VERDICTS]`)
**Apply to:** the `prior_cycles_failed` predicate
Do not hand-roll a verdict test. A SKIPPED/NA prior cycle is not a failure.

### Shared primitives that must not be re-implemented
**Source / apply-to:**
- Region read-back → `chip_test._read_region` (`:2710`), *"the ONE place this slice lives"*
- Byte-diff math → `chip_test._diff_offsets` (`:125-129`)
- Buffer-vs-device compare → `EpromOperator.verify_eprom` (`eprom_operations.py:2094`)
- Freezing a report hash → `tests/fixtures/report_shapes.py` builder, never a hand-typed literal
- Regenerating a snapshot → `tools/snapshot_report_shapes.py`, never a hand edit

### Two-commit, two-repo re-key declaration
**Source:** `.planning/MILESTONES.md:41` (the protocol) + `tests/fixtures/rekey_ledger.py:17-20`
(append-never-edit) + `/workspaces/tools/rekey/check_rekey_ledger.py` (the binding checker)
**Apply to:** every hash that moves in this phase
Behaviour commit first (gate expected RED); declaration commit second, per tree.

### Measure, never transcribe
**Apply to:** every hash literal in every plan
Every number in RESEARCH.md's blast-radius table is a projection of an unimplemented change,
including the ledger's own `60a031573aab`. A plan whose acceptance criterion is a hash copied
from a document rather than produced by a run in `firestarter_app/.venv311` (py3.11 — the
devcontainer's 3.12 masks app CI) is wrong by construction.

---

## No Analog Found

None. Every file this phase touches has a same-role, same-data-flow analog in the tree —
several of them (the counting test, the reserved `shape_id`, the ledger rows) were built by
Phase 174/175 *specifically* to be the seam Phase 177 lands on.

Two adjacent items the planner should note are **decisions, not missing patterns**:

| Item | Why there is nothing to copy |
|---|---|
| PRUNE-04 call-site replacement | RESEARCH.md's exhaustive census finds **zero** in-engine sites once D-1 and the SDP carve-out apply. There is no analog because there is no work — unless the operator widens "the engine" to `eprom_operations.write_cycle_eprom`. Open with a `checkpoint:decision`. |
| Publishing the 18-row filed-corpus mapping | GATE-06 requires declaration; publication is a scope decision. The MILESTONES.md corrections table is the artifact home if it is taken. |

---

## Metadata

**Analog search scope:** `firestarter_app/firestarter/` (chip_test.py, diagnostic_report.py,
eprom_operations.py), `firestarter_app/tests/` (test_chip_test.py, test_chip_test_cycle.py,
fixtures/), `firestarter_app/tools/`, `/workspaces/.planning/` (MILESTONES.md, seeds/),
`/workspaces/tools/rekey/`, `/workspaces/.claude/skills/devtest-triage/`
**Files scanned:** 14
**Tracked-source check:** `git ls-files` run in both trees; all 10 analog paths confirmed
tracked, none is a gitignored mirror
**Consumer note (Open Question 5, answered):** `.claude/skills/devtest-triage/SKILL.md` reads
`dedup_fingerprint` as a **dedup key** at `:55-56`, `:80`, `:162`, `:193`, `:436`, and does
**not** read the `fingerprint` classification string or `ladder_state`. No skill edit is forced
by this phase; the 18-row re-key does orphan historical dedup groups the skill relies on, which
is worth one sentence in the plan.
**Pattern extraction date:** 2026-09-05
