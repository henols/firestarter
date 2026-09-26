# Phase 180: Read-Step Sampling (conditional on Phase 176) - Pattern Map

**Mapped:** 2026-09-08
**Files analyzed:** 5 (1 new, 4 modified)
**Analogs found:** 5 / 5

This is a **documentary close**. Zero lines of sampling code ship. Zero product-source
(`firestarter_app/firestarter/`) edits. The only executable artifacts are additive pytest functions.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| **NEW** `.planning/phases/180-read-step-sampling-conditional-on-phase-176/180-PRUNE-08-CLOSURE.md` | planning record (closing document) | transform (evidence → verdict) | `.planning/phases/177-evidence-gated-read-back/177-READBACK-INVENTORY.md` § "PRUNE-04's closure" | exact — CONTEXT.md names it as the house form |
| **MOD** `firestarter_app/tests/test_chip_test.py` (2 additive tests) | test (behavioural) | request-response (mock operator → `run_plan` → verdict) | `test_read_step_disagreement_is_divergence_metric_not_marginal` (:2141), `test_read_step_agreement_no_divergence_recorded` (:2166) | exact |
| **MOD** `firestarter_app/tests/test_readback_inventory.py` (2 additive pins + planted-RED legs) | test (structural / AST census) | transform (source string → AST → assertion) | same module's `test_engine_has_exactly_two_read_eprom_call_sites` (:101) + `test_a_planted_third_call_site_reddens_the_census` (:109) | exact — same module |
| **MOD** `.planning/seeds/dev-test-adaptive-sequencing.md` (frontmatter `status:`, R3 body, R4 sentence) | design record | transform (in-place amendment) | same file's `## Status: Phase 177 amendment` (:162-177) | exact |
| **MOD** `.planning/REQUIREMENTS.md` (2 lines: :60, :175) | requirements ledger | CRUD (two-field flip) | Phase 177's identical PRUNE-01..04 markings in the same file | exact |
| **NEW** `.planning/phases/180-.../evidence/*.txt` | evidence transcript | batch (command → scalars) | `.planning/phases/177-evidence-gated-read-back/evidence/177-03-readback-census.txt`, `177-03-seed-amendment.txt` | exact |

**Tracked-source gate:** all five paths verified via `git ls-files` — `.planning/REQUIREMENTS.md`,
`.planning/seeds/dev-test-adaptive-sequencing.md`,
`.planning/phases/177-evidence-gated-read-back/177-READBACK-INVENTORY.md` in the meta repo;
`tests/test_chip_test.py`, `tests/test_readback_inventory.py` in the `firestarter_app` submodule.
No analog cited here is a gitignored mirror.

---

## BINDING: comment discipline overrides every excerpt below

`/workspaces/CLAUDE.md` § "Source code comments — hard rule" — **no `#` comments in product source at
all, and `firestarter_app/tests/` counts as product source.**

RESEARCH.md correction **C-3** (line 236) records that the exact analog test the planner is told to
sit beside carries **four** `#` comments, two of them trailing and two citing `(D-06)` — a GSD
decision identifier in product source. Those are **pre-existing, must not be "fixed"** (out of scope,
widens the diff) and **must not be copied**.

**Every excerpt in this document has had its comments stripped.** Where the analog carried a comment,
the rationale goes in the **docstring** instead — which is how these modules already carry their
reasoning (`test_readback_inventory.py`: 0 comments, 4 docstrings; its module docstring carries
several paragraphs of rationale, including the anti-vacuity argument and the
"resolved from `chip_test.__file__`, never from this test file's own directory" reasoning).

**The inherited regex gate cannot see this failure mode.** `/usr/bin/grep -cE '^\+[[:space:]]*#'`
counts only lines whose first non-space char is `#`; a trailing comment ships green. Use the
`tokenize` delta gate from RESEARCH.md § Comment Discipline, baselines
`tests/test_chip_test.py = 621`, `tests/test_readback_inventory.py = 0` at app HEAD `ffb0060`.

`grep` in this devcontainer is **ugrep and honours `.gitignore`** — use `/usr/bin/grep` for any
evidence-grade scan.

---

## Pattern Assignments

### 1. `180-PRUNE-08-CLOSURE.md` (planning record, new)

**Analog:** `.planning/phases/177-evidence-gated-read-back/177-READBACK-INVENTORY.md` § "PRUNE-04's
closure" (:66-77). Verbatim, in full:

```markdown
## PRUNE-04's closure

Once D-1's exclusion (row 1) and the seed's own SDP carve-out (row 2) apply,
**the `dev test` engine's in-engine population of read-whole-device-to-
compare-a-held-buffer sites is measured EMPTY.** Row 6, the one genuine match
in the whole package, is outside the engine and is named-and-excluded with its
own reason: it is the uno328pb read-repeatability oracle, and converting it
would repeat, one layer down, the exact error D-1 corrects at the engine
layer. PRUNE-04 therefore closes as **measured-empty, with the named-and-
excluded reason recorded** — the same standing this milestone grants
PRUNE-08 for closing as *measured, not worth doing*. The census gate reddens
if a third `operator.read_eprom` site ever appears in `chip_test.py`.
```

**The four moves to copy, in order:**

1. **State the verdict** in the requirement's own vocabulary — bolded, mid-paragraph, not as a
   heading. (177: *"is measured EMPTY"*. 180: *PRUNE-08 closes as **measured, not worth doing***,
   roadmap criterion 2, citing MEAS-01 §4a/§4b and §7.)
2. **Name the excluded thing and give its reason** rather than leaving it implicit. (180: the
   bit-structured sample, excluded because 10 connects > 1 connect on both board classes at every
   reference size; plus criterion 4 named N/A with its unmet precondition per D-10; plus the
   size-gated variant named-and-declined per D-05.)
3. **State the standing** the milestone grants the close — 177 already granted PRUNE-08 the same
   standing in the sentence above; quote it back.
4. **Name the gate that would redden** if the situation changed. (180: D-06's three tests — and,
   stronger, **R4-01 as the design change that would invalidate the close** (D-08), which is more
   honest than a reddening gate because no test can detect a design change that has not happened.)

**Also mirror 177's `## Search method` section** (:12-32): it states how the population was
enumerated so a reader can re-run it. Phase 180's analogue is the **connect arithmetic and the block
enumeration** — write them so they can be recomputed, not merely believed.

**Filename convention:** `NNN-TOPIC.md`, matching `176-MEASUREMENT.md`, `177-READBACK-INVENTORY.md`,
`177-REKEY-MAPPING.md`, `179-MEASUREMENT.md`.

**Content constraints inherited from RESEARCH.md corrections (do not re-derive):**
- **C-1:** write *"of 746 database rows, 484 are ≤128 KiB, 148 are 256 KiB and 114 are ≥512 KiB;
  every row at 256 KiB and above is `supported`."* Drop the blanket "all" — 10 of the 484 ≤128 KiB
  rows are not `supported`.
- **C-4:** state the block list by **enumeration**
  (`0x0000 0x0100 0x0200 0x0400 0x0800 0x1000 0x2000 0x4000 0x8000 0xFF00`), never by re-quoting the
  seed's loose `8..log2(size)` range, which read literally contradicts the seed's own "10 blocks".
- **C-5:** cite `chip_test.py:2767` (`_dispatch_read`) and `:2851` (`_read_region`). Do **not**
  inherit 177's `:2642`/`:2843` when quoting that inventory as the form precedent.
- **C-6:** lead with the model-free connect-count form (10 vs 1). The 2.5× factor rests on a
  D-04-bounded modelled read rate — label it "modelled, not measured", or omit.
- **Never blend** the two per-board-class connect figures (2.518 s / 2.607 s); 176-MEASUREMENT.md
  forbids a combined number by name.

---

### 2. `firestarter_app/tests/test_chip_test.py` — two additive behavioural legs

**Analog:** `test_read_step_disagreement_is_divergence_metric_not_marginal` (:2141-2164).
Below **with its four comments stripped** per C-3 — the two trailing ones (`# never a verdict flip`,
`# never marginal (D-06)`) and the two leading ones citing `(D-06)`:

```python
def test_read_step_disagreement_is_divergence_metric_not_marginal():
    operator = _mock_operator()
    call_results = [b"\x00" * 64, b"\xff" * 64]
    call_count = {"n": 0}

    def _read_side_effect(_name, _eprom_data, output_file=None, **_kwargs):
        data = call_results[call_count["n"] % len(call_results)]
        call_count["n"] += 1
        if output_file:
            Path(output_file).write_bytes(data)
        return True

    operator.read_eprom.side_effect = _read_side_effect
    plan = _plan_with_steps(Step(op=OP_READ, supported=True, reason=""))
    results = run_plan(plan, operator, _REAL_DB, runs=2)

    read_result = _result(results, OP_READ)
    assert read_result.verdict == VERDICT_OK
    assert read_result.verdict != VERDICT_MARGINAL
    assert read_result.divergence is not None
    assert read_result.divergence["bad"] > 0
```

The stripped rationale (*"two runs write DIFFERENT bytes — byte-level divergence, never a verdict
flip, never marginal"*) belongs in the **docstring** of each new test.

**Sibling for the agreeing case** (:2166-2174), the minimal shape:

```python
def test_read_step_agreement_no_divergence_recorded():
    operator = _mock_operator()
    operator.read_eprom.side_effect = _writes_bytes_to_output_file(b"\xaa" * 32)
    plan = _plan_with_steps(Step(op=OP_READ, supported=True, reason=""))
    results = run_plan(plan, operator, _REAL_DB, runs=2)

    read_result = _result(results, OP_READ)
    assert read_result.verdict == VERDICT_OK
    assert not read_result.divergence
```

**Helpers to reuse — never hand-roll a double** (`_mock_operator` is `Mock(spec=_OPERATOR_METHODS)`;
a hand-rolled fake drifts from the spec and silently stops constraining the call signature):

```python
def _mock_operator(**returns):                       # tests/test_chip_test.py:1019
    op = Mock(spec=_OPERATOR_METHODS)
    op.check_eprom_id.return_value = (True, 0x1234)
    op.read_eprom.return_value = True
    ...

def _plan_with_steps(*steps):                        # :1103
    return Plan(name="M8720", steps=list(steps))

def _result(results, op):                            # :1107
    for r in results:
        if r.op == op:
            return r
    raise AssertionError(f"no result for op {op!r} in {[r.op for r in results]}")
```

`_REAL_DB = EpromDatabase(skip_local_override=True)` at :307.

**The one adaptation the new legs require.** `_mock_operator` presets
`read_eprom.return_value = True`, and `_writes_bytes_to_output_file` (:1428) **hard-codes
`return True`** — neither can vary the return per call. Keep the disagreement test's
`call_count = {"n": 0}` counter-dict idiom but make the **return value** the per-call variable:

```python
    call_returns = [True, False]
    call_count = {"n": 0}

    def _read_side_effect(_name, _eprom_data, output_file=None, **_kwargs):
        ok = call_returns[call_count["n"] % len(call_returns)]
        call_count["n"] += 1
        if output_file:
            Path(output_file).write_bytes(b"\x00" * 64)
        return ok
```

Side-effect signature must be `(_name, _eprom_data, output_file=None, **_kwargs)`, and it **must
write bytes when `output_file` is truthy** — a leg that writes no file leaves `run_bytes` empty and
silently changes what is under test.

**Naming convention:** flat module-level `def test_<subject>_<claim>()`; no class, no fixture, no
parametrize; long names that assert the claim. Suggested pair (from RESEARCH.md):
`test_read_step_last_run_failure_yields_bad` and
`test_read_step_first_run_failure_with_passing_last_run_yields_ok`.

**Placement:** immediately after `test_read_step_agreement_no_divergence_recorded` (ends :2172),
before `test_write_step_attaches_fingerprint_with_region_start_addr_base` (:2177).

**Both legs go through the real `run_plan`** — proven this research session that Phase 178's status
axis does not intercept a `False` return (`run_plan`'s dispatcher returns `_dispatch_read(...)`
directly for `OP_READ`; ATTR-02's transport arm keys on exceptions, not on `False`). Do not call
`_dispatch_read` directly.

**Do not duplicate the two existing tests** — CONTEXT.md is explicit: cite them, do not re-assert.

---

### 3. `firestarter_app/tests/test_readback_inventory.py` — two additive structural pins

Two pins go here (the second is the orchestrator's settled ruling on RESEARCH.md's C-7):
**(a)** D-06 leg 3 — `_dispatch_read`'s `verdict=` expression reads only `last_ok`;
**(b)** one `read_eprom` call costs exactly one connect.

**Module-path resolution — reuse verbatim, write no second resolver** (:95-98):

```python
def _engine_source() -> str:
    source = pathlib.Path(ct.__file__).read_text(encoding="utf-8")
    assert len(source) > 1000
    return source
```

The `assert len(source) > 1000` is the non-empty guard — the census cannot pass on a file it never
read. Resolution is from `firestarter.chip_test.__file__`, **never** from the test file's own
directory: this project has a recorded checker that resolved directory-relative, scanned nothing and
**exited 0**.

**Imports already present** (:33-40) — the new pins need **no new import**:

```python
import ast
import inspect
import pathlib

import pytest

from firestarter import chip_test as ct
from firestarter.eprom_operations import EpromOperator
```

`EpromOperator` is already imported and already reached into by
`test_verify_eprom_signature_names_the_replacement_primitive` (:123) — precedent that this module
legitimately pins `eprom_operations`, which is what pin (b) needs. For pin (b), resolve
`eprom_operations`' source the same way `_engine_source()` does (`pathlib.Path(...__file__)` +
non-empty guard), as a sibling helper — do not reuse `_engine_source()` for a different module.

**Assertion style — whole sets and exact lists, never `in`** (:101-106, :123-131):

```python
def test_engine_has_exactly_two_read_eprom_call_sites():
    _assert_census(
        _engine_source(),
        expected_count=2,
        expected_enclosing={"_dispatch_read", "_read_region"},
    )


def test_verify_eprom_signature_names_the_replacement_primitive():
    params = list(inspect.signature(EpromOperator.verify_eprom).parameters)[1:]
    assert params == [
        "eprom_name",
        "eprom_data_dict",
        ...
    ]
```

Pitfall 3 in RESEARCH.md: a pin asserting `"last_ok" in names` stays **green** on
`VERDICT_OK if last_ok and not divergence else VERDICT_BAD` — the exact failure criterion 3 names.
Assert the exact sorted set `["VERDICT_BAD", "VERDICT_OK", "last_ok"]`.

**Planted-mutation idiom — the D-07 pattern, in-memory strings only, no fixture files** (:109-115):

```python
_PLANTED_ANCHOR = (
    "            last_ok = operator.read_eprom(name, eprom_data, "
    "output_file=out_path)\n"
)


def test_a_planted_third_call_site_reddens_the_census():
    source = _engine_source()
    assert source.count(_PLANTED_ANCHOR) == 1
    mutated = source.replace(_PLANTED_ANCHOR, _PLANTED_ANCHOR + _PLANTED_ANCHOR, 1)
    count, enclosing = _read_eprom_census(mutated)
    assert count == 3
    assert enclosing == {"_dispatch_read", "_read_region"}
```

Three load-bearing details to reproduce for each new pin's RED leg:
1. **Anchor uniqueness is asserted first** (`source.count(...) == 1`) so the mutation cannot silently
   no-op.
2. `replace(..., 1)` **bounds** the mutation.
3. Everything is **strings in memory** — no file written.

The Phase 180 anchor is verified unique in `chip_test.py`:
`"        verdict=VERDICT_OK if last_ok else VERDICT_BAD,\n"`. The discriminating mutant is
`... if last_ok and not divergence else ...` — RESEARCH.md proved GREEN-at-HEAD / RED-at-mutant this
session.

**AST extraction skeleton for pin (a)** (verified to run):

```python
tree = ast.parse(source)
fn = next(n for n in ast.walk(tree)
          if isinstance(n, ast.FunctionDef) and n.name == "_dispatch_read")
call = next(c for c in ast.walk(fn) if isinstance(c, ast.Call)
            and isinstance(c.func, ast.Name) and c.func.id == "StepResult")
kw = next(k for k in call.keywords if k.arg == "verdict")
names = sorted({n.id for n in ast.walk(kw.value) if isinstance(n, ast.Name)})
assert names == ["VERDICT_BAD", "VERDICT_OK", "last_ok"]
```

**The vacuity leg to mirror** (:118-120) — assert the gate fails when its expectation is emptied:

```python
def test_an_empty_enclosing_allow_list_fails_rather_than_passing_vacuously():
    with pytest.raises(AssertionError):
        _assert_census(_engine_source(), expected_count=2, expected_enclosing=set())
```

**Source for pin (b) — the one-connect premise.** `firestarter_app/firestarter/eprom_operations.py`,
verified exact to the line:

```python
    def _operation_context(                                          # :515
        self,
        ...
        command_dict, buffer_size = self._setup_operation(           # :531
            ...
        )
        ...
        try:                                                         # :545
            yield command_dict, buffer_size, operation_name          # :547
        finally:                                                     # :548
            self._disconnect_programmer()                            # :550

    def _disconnect_programmer(self):                                # :552
        if self.comm:
            self.comm.disconnect()
            self.comm = None
```

with `self.comm = SerialCommunicator.find_and_connect(` inside `_setup_operation` at **:499**
(`_setup_operation` defined :454), and `read_eprom` at **:896** whose entire body is a single
`with self._operation_context(...)` opened at **:905** — no loop, no second context, no re-entry.

Pin (b) must assert **structure**, not string presence (a grep for `find_and_connect` fails open on a
rename and proves nothing). All three clauses:
1. `read_eprom`'s `FunctionDef` contains **exactly one** `ast.With` item whose `context_expr` is a
   `Call` on `Attribute(attr="_operation_context")`. *This is the clause that carries the arithmetic.*
2. `_operation_context`'s body calls `_setup_operation`, and `_setup_operation`'s body calls
   `find_and_connect`.
3. `_operation_context` has a `Try` node with a non-empty `finalbody`, and `_disconnect_programmer`
   is called **within that `finalbody`** — not merely somewhere in the function. Asserting the call
   site is inside `finalbody` is the difference between a real pin and a decorative one.

**Its honest ceiling belongs in the docstring:** this is a *static* pin. It proves the code is shaped
so one call opens one context that connects and disconnects; it does **not** prove at runtime that
exactly one serial open occurred, and it says nothing about `find_and_connect`'s internal
retry-across-ports walk. That ceiling is sufficient — the closing argument needs "N region reads cost
N connects, not 1", a statement about shape.

**Module docstring must be extended**, not left stale: its current text says "Two anti-vacuity legs
prove the gate is a gate" (:26-30). Adding pins changes that count.

---

### 4. `.planning/seeds/dev-test-adaptive-sequencing.md` (design record, in-place amendment)

**Analog:** the same file's `## Status: Phase 177 amendment` (:162-177), verbatim:

```markdown
## Status: Phase 177 amendment

**Phase 177, 2026-09-05.** R1's final paragraph swept the fingerprint
read-back into the same rule that legitimately excludes the SDP leg, which
directly contradicted R2's own promise of byte-identical fidelity on a
failing run: `verify_eprom` returns a bool and one mismatch address, while
`classify_fingerprint` needs the whole mismatch distribution. Decision `D-1`
(`.planning/REQUIREMENTS.md`) settled the contradiction in R2's favour, and
this amendment replaces R1's paragraph **in place** rather than merely
annotating it, so the destructive reading is not outvoted but absent — a
planner reading only this seed can no longer regenerate it. R2 is corrected
so its own gate predicate consults outcomes across all cycles, not the final
cycle alone, and states that a passing step still reports a synthesized
`match` fingerprint. **Not touched by this amendment:** R3, R4, the
projected-effect table, the per-class characteristics section and the
out-of-scope section above.
```

**Six moves to copy:**
1. `## Status: Phase 180 amendment` heading **appended at the end of the file**, after
   `## Explicitly out of scope` — a **sibling** to the 177 section. **Do not edit the 177 section.**
2. Open `**Phase 180, 2026-09-08.**` — bold phase number and date.
3. State **what was wrong** with the amended text and why, with the technical reason.
4. Name the **deciding authority** (here: MEAS-01's measurement + PRUNE-08's own close text in
   `.planning/REQUIREMENTS.md`).
5. State the **in-place principle** in the precedent's own words: *"replaces R3's paragraph **in
   place** rather than merely annotating it, so the destructive reading is not outvoted but absent —
   a planner reading only this seed can no longer regenerate it."*
6. Close with an explicit **"Not touched by this amendment:"** list.

**Item 6 is the one to get right.** 177's list says *"R3, R4 … not touched"* — Phase 180's section
must state that R3 (and R4's one sentence) **are** now amended, so the two sections do not contradict
each other. Phase 180's own list reads approximately: *R1, R2, the projected-effect table, the
per-class characteristics section, the sequencing note and the out-of-scope section.*

**Three edit sites (verified line numbers):**
- **:5** frontmatter `status:` — the clause `R3 remains for Phase 180 (PRUNE-08)` becomes false and
  must change. Keep **exactly 4 frontmatter fields** (`title`, `trigger_condition`, `planted_date`,
  `status`) — Phase 177's evidence asserts `frontmatter_fields=4`. Line 3's stale
  `trigger_condition` is **out of scope; do not touch it**.
- **:70-93** R3's body — amend the second paragraph (:75-81), the live instruction *"Replace the read
  step's second full run with a bit-structured sample…"*, in place. **Preserve the connect-count
  objection** in the amended text so the design cannot be regenerated without meeting it.
- **:105-107** R4's sentence *"Per-connect cost is unmeasured — the counts are validated, the seconds
  are not."* — now false; corrected **minimally** per the orchestrator's ruling. (Note: D-09
  attributes the "measure a connect first" instruction to R3; it is actually in R4.)

**Evidence-file analog:** `.planning/phases/177-evidence-gated-read-back/evidence/177-03-seed-amendment.txt`
— flat `key=value` scalars. Phase 180 inverts `r3_intact=1` → `r3_intact=0` / `r3_amended=1`, adds
`r4_amended=1`, and keeps `frontmatter_fields=4` and `projection_table_intact=1`.

---

### 5. `.planning/REQUIREMENTS.md` (requirements ledger, two-line flip)

**Analog:** Phase 177's identical PRUNE-01..04 markings in this same file — hand edits, never the
`gsd-tools` requirements verbs (recorded: those verbs reformat the whole file).

**Exactly two edits, verified verbatim:**

```
:60   - [ ] **PRUNE-08**: The read step's second full sweep is replaced by ...
         → - [x]

:175  | PRUNE-08 | Phase 180 | Pending |
         → | PRUNE-08 | Phase 180 | Complete |
```

**Scope-verification counts to pin absolutely** (measured this research session):

| Metric | Before | After |
|---|---|---|
| Unchecked `- [ ]` v1 boxes | 19 | **18** |
| Checked `- [x]` v1 boxes | 27 | **28** |
| Traceability rows `\| Pending \|` | 19 | **18** |
| `git diff --numstat` on `.planning/REQUIREMENTS.md` | — | **2 changed lines, nothing else** |

**Do not touch** MEAS-01 (:103, already Complete), R4-01 (:122, reference only), the Coverage block
(:195-199), or any RPT/HYG row (Phase 181's).

**Ordering rule (recorded executor failure mode):** the requirement marking is the **last** task,
gated on the closing document being committed. Executors in this project have a recorded habit of
marking requirements Complete prematurely.

---

## Shared Patterns

### Docstring-carried rationale (applies to every new test)
**Source:** `firestarter_app/tests/test_readback_inventory.py:1-31` (module docstring) and
`:52-59` (`_read_eprom_census` docstring).
**Apply to:** all four new test functions and any new helper.
The module docstring carries the requirement it closes, the reason `ast` is used over `grep`, the
path-resolution failure mode, and the anti-vacuity argument — all in prose, zero `#` comments. Each
new test's docstring should state its claim **and its ceiling**.

### Anti-vacuity: every gate gets a planted-mutation RED proof (D-07)
**Source:** `test_readback_inventory.py:109-115` (planted anchor) and `:118-120` (emptied
expectation).
**Apply to:** both new structural pins.
Assert anchor uniqueness first; bound the replacement with `replace(..., 1)`; strings only, no files.
A pre-authored gate leg can be **unreachable** — RED proves nothing until it has been *observed*.
Record the transcript in `evidence/`.

### Evidence transcript form
**Source:** `.planning/phases/177-evidence-gated-read-back/evidence/177-03-readback-census.txt`
```
== 1 the census itself
source_nonempty=True
engine_read_sites=2
enclosing=_dispatch_read,_read_region
rc=0
== 2 the census module
......                                                                   [100%]
6 passed in 0.33s
rc=0
comments_test_readback_inventory=0
```
**Apply to:** every Phase 180 evidence file. Numbered `== N label` sections, flat `key=value`
scalars, verbatim pytest tail, explicit `rc=0` after each command. Every claim is a scalar a reader
can diff — never prose. Naming: `<phase>-<plan>-<topic>.txt`. The
`.planning/phases/180-.../evidence/` directory does not exist yet.

### Gate battery — SEVEN legs, floor 2239
**Source:** `.planning/MILESTONES.md` first section (aimed by name at *"a phase 180/181 plan"*),
re-measured green this research session.
**Apply to:** the phase-seal verify block.
1. `./.venv311/bin/python -m ruff check firestarter/ tests/`
2. `./.venv311/bin/python -m ruff format --check firestarter/ tests/`
3. `./.venv311/bin/python tools/check_mypy_watermark.py` → match exactly `mypy errors: 35 (watermark: 35)` (mypy prints "OK" when *missing*)
4. `./.venv311/bin/python tools/snapshot_report_shapes.py --check` (19 snapshot files)
5. `./.venv311/bin/python tools/check_devtest_orchestrator.py`
6. `./.venv311/bin/python tools/check_diagnostic_report_claims.py`
7. `./.venv311/bin/python -m pytest tests/ -o addopts="" -q` → floor **2239** (+3 or +4 new)

Plus cleanliness: `test -z "$(git -C /workspaces/firestarter status --porcelain)"` and the same for
`firestarter/data/chip_database.json`.

**Do NOT copy `179-PATTERNS.md:453`'s eight-leg set or `179-02-PLAN.md:39`'s 2242 floor.**
`tools/rekey/check_rekey_ledger.py` **does not exist** — the leg is retired, and 2242 reads RED
against a healthy 2239 tree. Warning sign: any verify block mentioning `rekey`, `ledger`, `2241` or
`2242`. Always `./.venv311/bin/python` (devcontainer default is 3.12; app CI is 3.11 only).
Commit before running the suite — `test_flash_path_record_sync` asserts whole-repo porcelain.

---

## No Analog Found

None. Every artifact has a close in-repo precedent; this phase is deliberately a re-run of Phase
177's documentary-close shape against a different requirement.

---

## Metadata

**Analog search scope:** `.planning/phases/176-*`, `.planning/phases/177-*`, `.planning/phases/179-*`,
`.planning/seeds/`, `.planning/REQUIREMENTS.md`, `firestarter_app/tests/`,
`firestarter_app/firestarter/{chip_test,eprom_operations}.py`.
**Analogs read this session:** `177-READBACK-INVENTORY.md` (:60-77), the seed (:160-177),
`REQUIREMENTS.md` (:60, :175), `tests/test_readback_inventory.py` (full, 139 lines),
`tests/test_chip_test.py` (:1019-1035, :1100-1112, :1428-1442, :2135-2180),
`eprom_operations.py` (:515-555, :896-912). Line numbers otherwise inherited from 180-RESEARCH.md,
which verified them this same day.
**Line-number validity:** perishable. Re-verify if `chip_test.py`, `eprom_operations.py`,
`test_chip_test.py`, `test_readback_inventory.py`, `REQUIREMENTS.md` or the seed moves.
**Measured against:** `firestarter_app @ ffb0060`, meta `@ f031be81`.
**Pattern extraction date:** 2026-09-08
