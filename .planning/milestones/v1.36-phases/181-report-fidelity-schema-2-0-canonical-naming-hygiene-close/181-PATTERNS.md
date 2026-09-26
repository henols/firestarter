# Phase 181: Report Fidelity — Schema 2.0, Canonical Naming & Hygiene Close - Pattern Map

**Mapped:** 2026-09-09
**Files analyzed:** 12 (9 product source / test, 3 config-or-record)
**Analogs found:** 11 / 12
**Scan tool:** `/usr/bin/grep` (devcontainer `grep` is ugrep and honours `.gitignore`)
**Scope honoured:** host-only. Nothing under `/workspaces/firestarter/` was read.

---

## Anchor drift found (read this before the planner cites CONTEXT.md line numbers)

CONTEXT.md's anchors were gathered at discuss time. Re-measured today against
`gsd/v1.36-dev-test-fidelity-planning`:

| CONTEXT.md claim | Measured | Verdict |
|---|---|---|
| `tools/check_devtest_orchestrator.py:152-164` | **`firestarter_app/tools/check_devtest_orchestrator.py:152-165`** — the file does **not** exist in the meta-repo (`/workspaces/tools/` holds only `catalog/` and `wiki/`) | **WRONG REPO.** HYG-04 / D-19 edits a file *inside the app submodule*, so its commit lands in `firestarter_app`, not meta. This changes which repo the HYG-04 commit belongs to. |
| `get_eprom_config`'s ladder at `database.py:466-485` | `def get_eprom_config` at **`:446`**; `_strip_paren` at `:465`; ladder body `:469-486`; `return None, None` at `:486` | close; use `:446-486` for the whole function |
| `# ALWAYS WRITES` block at `cli_handlers.py:2331-2345` | The `# ALWAYS WRITES:` paragraph runs **`:2331-2349`**, and the `# REVERSAL (operator-specified 2026-07-29)` paragraph at **`:2351-2360`** *also* describes "the UV-only ask" / "that same UV ask" as present tense. The enclosing narrative block is `:2315-2364`, ending immediately before `@dev.command(name="test")` at `:2366`. | **UNDER-SCOPED.** Deleting only 2331-2345 leaves a second false statement about a prompt that does not exist. Folded-todo 3 is not discharged by the narrow cut. |
| "~69 `write_scope="none"` test uses across 7 files" | **78 occurrences across 9 files**: `chip_test.py` 14, `diagnostic_report.py` 1, `tests/test_chip_test.py` 32, `tests/test_chip_test_sdp_leg.py` 16, `tests/test_erase_flag_invariants.py` 5, `tests/test_chip_test_blank_check_order.py` 4, `tests/test_chip_test_timing.py` 4, `tests/plan_corpus.py` 1, `tests/test_derive_plan_structural_sentinel.py` 1 | **UNDER-COUNTED** by ~9 and by 2 files. D-08's blast radius is larger than stated. |
| two-commit `FROZEN_HASHES` rule at `test_blast_radius_invariance.py:278-280` | confirmed — failure message of `test_dedup_fingerprint_is_frozen`, `:276-280` | OK |
| `SCHEMA_VERSION == "1.8"` at `test_blast_radius_invariance.py:517` | confirmed, `:517`, inside `test_schema_version_is_pinned` — and its **docstring already names Phase 181 by number** (`:510-512`) | OK |
| `pyproject.toml` `dependencies` `:46-53`, `syrupy>=5.0` `:73` | confirmed exactly | OK |
| `SKILL.md:375` sole `vpp_mv` occurrence | confirmed — `/usr/bin/grep -n "vpp_mv\|vpe_mv\|locked_steps" .claude/skills/devtest-triage/SKILL.md` returns **exactly one line, `:375`** | OK |
| D-12: only `.vpp_mv`/`.vpe_mv` assignments are `tests/test_diagnostic_report.py:982-983` | confirmed. Census over `firestarter/ tests/ tools/` finds exactly two report-object assignments (`:982`, `:983`) plus two emit sites (`diagnostic_report.py:752-753`). Every other hit is a *database* `vpp_mv` (`ic_layout.py`, `test_check_dispatch_invariants.py`) — a **different field, same name**; the census MUST be attribute-on-report-object scoped, not textual, or it returns ~20 false positives. | **CONFIRMED, with a trap** |
| `slots_remaining=` at `chip_test.py:3014` | confirmed — `slots_remaining=slots_total - slot_index` at `:3014`, i.e. the off-by-one D-20 fixes is literally the missing `- 1` | OK |

Everything else in CONTEXT.md's `### Product source this phase edits` list verified line-exact
(`SCHEMA_VERSION:50`, `dedup_fingerprint:263`, `build_db_diff:364`, `AutoCapture:78`,
`DiagnosticReport:631`, `_voltage_dict:733`, `_step_dict:781`, `_banner_dict:846`, `to_dict:886`,
`render:909`, `Fingerprint:154`, `Plan:495`/`locked_destructive:514`/`is_uv:515`,
`derive_plan:540`, `StepResult:1096`, `_aggregate_cycle_results:1360`, `sdp_oracle_applicable:2012`,
`slots_remaining:2388`, `_dispatch_id:2744`, `_dispatch_read:2767`, `BannerCounts:3690`,
`count_applicable:3706`, `_chip_id_fields:2189`, `_make_sampler:2230`, `_is_uv_eprom:2257`,
`_resolve_write_scope:2272`, `derive_plan` call site `:2403`, `build_title:174`, caller `:698`).
One correction: `build_db_diff`'s arms are `:390-410`, not `:375-410` (`:375-389` is the
`run_errored` pre-arm).

---

## File Classification

| Modified file | Role | Data flow | Closest analog | Match |
|---|---|---|---|---|
| `firestarter_app/firestarter/diagnostic_report.py` | model + serializer | transform | commit **`ec1db5c`** (`feat(178-01)`) on this same file | exact |
| `firestarter_app/firestarter/chip_test.py` | service (engine) | batch / transform | `_aggregate_cycle_results` + `_dispatch_read`'s own `divergence` block, same file | exact |
| `firestarter_app/firestarter/cli_handlers.py` | controller (Click handler) | request-response | `_chip_id_fields` / `_make_sampler`, same file | exact |
| `firestarter_app/firestarter/submit.py` | utility (formatter) | transform | `build_title` itself (`:174-185`) | exact |
| `firestarter_app/firestarter/database.py` (read-only source of the ladder) | model | CRUD lookup | `get_eprom_config:446-486` | exact |
| **new** canonical-alias selector | utility | transform | `database.py:465-486` ladder (D-02 mirror) | exact |
| `firestarter_app/tests/test_blast_radius_invariance.py` | test (schema pins) | transform | `ec1db5c`'s diff of this very file | exact |
| **new** RPT-B1 source-census test | test (AST census) | transform | `tests/test_readback_inventory.py:57-148` | exact |
| `firestarter_app/tests/fixtures/report_shapes.py` | test fixture (frozen builders) | transform | itself — `_build_real_path_report:467-503` + `_BUILDERS:705-724` + `FROZEN_HASHES:729-750` | exact |
| `firestarter_app/pyproject.toml` | config | n/a | `py32` extra's bounded `pyusb>=1.3.1,<2` (`:68-70`) | exact |
| `firestarter_app/tools/check_devtest_orchestrator.py` | config (allow-list gate) | n/a | `_HANDLER_FUNCTION_NAMES:152-165` itself | exact |
| `.claude/skills/devtest-triage/SKILL.md` | doc (meta-repo) | n/a | **none** — single-row table edit, no prior precedent | none |

---

## Pattern Assignments

### `diagnostic_report.py` — additive keys (RPT-A2/A3/A4, RPT-D2, RPT-F1) + schema bump (RPT-E1)

**Analog: commit `ec1db5c` (`feat(178-01): fault attribution -- the two-axis status vocabulary`).**
This is the single best analog in the phase and the planner should read the whole commit. It did, in
**one commit**, exactly the four things RPT-A/RPT-E do: added a top-level `to_dict()` key
(`run_status`), added a `steps[]` key (`status`), bumped `SCHEMA_VERSION` 1.7 → 1.8, and moved
`_TO_DICT_KEYS` / `_STEPS_ELEMENT_0_KEYS` and the `test_schema_version_is_pinned` triple-equality in
the *same* commit — which is precisely the D-14 rule, already practised. Its counted-keys docstrings
("eleven top-level keys" → "twelve") were updated with the lists; D-14 must do the same
("twelve" → fourteen, "fourteen" step keys → more).

**Additive-inside-`steps[]` pattern** (`_step_dict`, `:781-845`) — the fingerprint siblings go here.
Note the existing precedent already in that function's own body: the schema-1.6 `write_*` block is
described as *"Additive INSIDE `steps[]` only, never a top-level key -- the top-level shape is pinned
elsewhere and `parse_devtest_issue.py` consumes it."* The current fingerprint emit that RPT-A2
replaces is a bare string:

```python
            "fingerprint": (
                result.fingerprint.classification if result.fingerprint else None
            ),
```

RPT-A2 is serialization-only: `Fingerprint` (`chip_test.py:154`) already carries `total`, `bad`,
`bad_pct`, `evidence`. Follow the `write_*` block's shape — sibling flat keys guarded by a
`if result.fingerprint else None`, **not** a nested dict, since `_STEPS_ELEMENT_0_KEYS` pins a flat
key list element-wise.

**`_voltage_dict` — the NOT_MEASURED sentinel helper** (`:733-754`), the two lines RPT-B1 deletes:

```python
            "vpp_mv": NOT_MEASURED if self.vpp_mv is None else self.vpp_mv,
            "vpe_mv": NOT_MEASURED if self.vpe_mv is None else self.vpe_mv,
```

**Field-deletion analog — nearest is `58b0670` (`feat(111-03)`), and it is only half a match.**
`58b0670` is the commit that *created* `vpp_mv`/`vpe_mv` and `_voltage_dict`; it removed the prior
combined `vpp_vpe_mv` field from the dataclass, from `to_dict()` and from the class docstring — the
three-place shape RPT-B1 repeats. **But it predates the key-list pins** (`_VOLTAGE_KEYS` was
introduced by `5693bf7`, `test(174-03)`, and `git log -S'_VOLTAGE_KEYS'` returns *that commit only*).
So: **no key-list pin has ever been shrunk.** Phase 181 is the first deletion through the Phase 174
pins, and the planner should say so rather than cite a precedent. The mechanical form to copy from
`58b0670` is: dataclass field line, helper emit line, and the class docstring sentence naming it
(`DiagnosticReport`'s docstring `:637-639` currently says *"plus standalone non-destructive readings
(`vpp_mv`/`vpe_mv`)"* — that sentence dies with the fields).

**`_banner_dict`** (`:846-855`) — RPT-B2 deletes `locked_steps` from **both** branches, including the
`None`-banner early return `{"n_ran": None, "m_applicable": None, "locked_steps": []}`. A deletion
that touches only the populated branch leaves the key present on a bannerless report and
`_BANNER_KEYS` will not catch it (that pin is taken off a shape with a banner).

**`render()`'s "steps total" row** (`:993-1007`) — the RPT-D2 removal. Its own comment already
concedes the under-report D-06/D-07 fix:

```python
        # Deliberately labelled "steps total", not "elapsed": it excludes the
        # identity read, plan derivation, report write and the submit prompt,
        total = sum(
            float(sr["duration_s"])
            for sr in d["steps"]
            if sr.get("duration_s") is not None
        )
        if total:
            table.add_row("steps total", _duration_cell(total))
```

The `elapsed` replacement row copies this shape but reads `d["elapsed"]` — **never recomputes**.
Precedent for read-off-the-dict-never-recompute is stated three times in `render()`: the `runs`
cell (*"Read off `d["steps"]`, never recomputed here"*), the `_RAN_VERDICTS` step gate, and
`rail_reading_disclosure`. D-06's "stored field, stamped once" is required because `to_dict()` calls
`self._utc_now()` on every invocation and is invoked three times per run.

**`render()`'s `chip_id` row** (`:951-967`) — **D-10 says do not touch this.** Quoted here so the
planner can see the row is already conditional and that the 2026-08-21 operator decision is recorded
in the source comment; RPT-A1 lands in `_chip_id_fields` and `to_dict()` only.

**`build_db_diff`'s fourth arm** (D-21 guard site, `:401-403`):

```python
    elif "OK" in verdicts and verdicts <= {"OK", "NA", "SKIPPED"}:
        proposed = _DISPOSITION_CANDIDATE
        ladder_state = _LADDER_COMMUNITY_REPORTED
```

The guard pattern to copy is the `run_errored` pre-arm immediately above (`:375-389`), which is the
project's own way of adding a disqualifying precondition to this ladder — a `getattr`-with-safe-
default `any(...)` computed before the chain and inserted as the **first** `if`:

```python
    run_errored = any(
        getattr(r, "status", STATUS_COMPLETE) == STATUS_ERROR for r in results
    )
```

D-21's "did a write actually run" predicate should be shaped identically (defaulted `getattr`, so a
duck-typed result folds safe) and inserted as an extra condition on the fourth arm rather than as a
UV special case.

---

### `chip_test.py` — `duration_s` mean (RPT-D1), `divergence` on agreement (D-11), `chip_id_detected` (RPT-A5/D-23), D-08/D-09 deletions

**`_aggregate_cycle_results`** (`:1360-1415`). The line RPT-D1 replaces, and the docstring line that
must move with it (*"`duration_s` -- the SUM across cycles, so \"steps total\" stays honest"* — note
the justification names the very row RPT-D2 deletes):

```python
    durations = [r.duration_s for r in results if r.duration_s is not None]
    return StepResult(
        ...
        run_count=len(ran),
        divergence=next((r.divergence for r in reversed(ran) if r.divergence), None),
        duration_s=round(sum(durations), 3) if durations else None,
```

Three patterns to reuse verbatim: the `if durations else None` guard is already exactly D-05's
"stays `None`, never `0.0`" rule; `run_count=len(ran)` is already "cycles that reached the operator",
so D-05's denominator is `len(ran)`, not `len(results)` — do not introduce a second notion; and the
field-by-field docstring bullet list is where D-05's stated caveat ("cycle 1 and cycle 2 are not the
same operation") belongs under D-26.

**Beware a second-order break:** `divergence=next((r.divergence for r in reversed(ran) if
r.divergence), None)` is **truthiness-filtered**. D-11's agreeing record is `{"repeat_divergent":
False, "bad": 0, ...}` — a non-empty dict, so truthy, fine. But if the agreeing shape were ever `{}`
the fold would silently discard it. The planner should pin the fold, not just the dispatch.

**`_dispatch_read`** (`:2767-2812`) — the divergence construction D-11 extends. The existing shape is
the one to mirror with `bad: 0`:

```python
    divergence: dict[str, Any] | None = None
    if len(run_bytes) >= 2 and any(run_bytes):
        shas = [hashlib.sha256(b).hexdigest() for b in run_bytes]
        diverged = len(set(shas)) != 1
        if diverged:
            cmp_len, diff_offsets, pct, first = _diff_offsets(...)
            divergence = {"repeat_divergent": True, "cmp_len": cmp_len,
                          "bad": len(diff_offsets), "pct": pct, "first_offset": first}
```

The `if len(run_bytes) >= 2 and any(run_bytes)` outer gate is what preserves D-11's `None`-means-
no-comparison semantics for `--fast` (one run) and a failed read (all-empty bytes) — the change is
to the inner `if diverged:` only. Same five keys on both branches, or `parse_devtest_issue.py` and
the triage skill see a ragged shape.

**`_dispatch_id`** (`:2744-2765`) — RPT-A5. `detected_id` is already in hand on line 1; the field is
one additive `StepResult` kwarg on the existing `return StepResult(op=OP_ID, verdict=verdict,
reason=reason, run_count=1)`. Precedent for exactly this move — an additive `StepResult` field kept
out of the hash by construction — is `ec1db5c`'s `status` field. D-23 forbids touching `reason`; the
mismatch prose at `:2760-2762` stays byte-identical.

**D-08/D-09 deletion sites, all measured:** `Plan.locked_destructive:514`;
`locked_destructive` local `:672` and its four appends `:763`, `:789`, `:807`, `:894` (note `:894` is
the **SDP** `OP_WRITE_INHIBITED` append — that is the one `sdp_oracle_applicable:2031` reads, and it
is *not* a `write_scope="none"` append, so it survives on the SDP axis and its removal must be
adjudicated separately from the three scope-driven ones); `Plan(...)` construction `:908-909`;
`count_applicable`'s `+ len(plan.locked_destructive)` at `:3722-3724` and `locked_steps=` at `:3729`;
`BannerCounts` docstring `:3697` and `count_applicable`'s docstring `:3716-3721`, both of which
explain the counting *in terms of* `write_scope="none"` and become false statements the moment D-09
lands. `sdp_oracle_applicable:2012-2031` reads `locked_destructive` for `OP_WRITE_INHIBITED` only —
that is the exit-code path CONTEXT.md flags as the risk concentration, and the deletion must keep
that one arm alive while removing the scope arm, or `_dev_test_exit_code`'s `sdp_oracle_not_run`
code-2 candidate changes behaviour.

**CONTEXT.md's two de-risking measurements — both re-verified:** every `report_shapes.py` builder
passes `write_scope="full"` (10 call sites, all `"full"`; the only non-`"full"` shapes are
`uv-slot-write-pass`, which builds its plan by a different route, and the two synthetic/`gh*` hand-
built shapes) — and `tests/plan_corpus.py:33-38` explicitly excludes `"none"` from `SWEEP_SCOPES`,
with the vacuity reason written out. Neither the invariance corpus nor the 175 sentinel sweep is
touched. **But** `tests/test_derive_plan_structural_sentinel.py:84` does
`from firestarter.cli_handlers import _resolve_write_scope` and `:1015`
`test_resolve_write_scope_returns_partial_for_every_uv_row` — that import breaks at **collection
time** when D-09 deletes the function, i.e. it reddens the whole module, not one test.

---

### New canonical-alias selector (RPT-F1, D-01/D-02/D-24)

**Analog: `firestarter_app/firestarter/database.py:446-486`, `get_eprom_config`.** D-02 says *mirror*
this ladder, do not write a second normalization. The ladder, verbatim:

```python
        def _strip_paren(s):
            # "DS1245AB(RW)" -> "DS1245AB"; preserves the canonical chip name.
            return re.sub(r"\([^)]*\)", "", s).strip().lower()

        query = chip_name.lower()
        query_stripped = _strip_paren(chip_name)
        ...
                part_number = ic_config.get("part_number", "")
                if query == part_number.lower():
                    return ic_config, manufacturer
                if "," in part_number or "(" in part_number:
                    aliases = [a.strip().lower() for a in part_number.split(",")]
                    if query in aliases:
                        return ic_config, manufacturer
                    aliases_stripped = [_strip_paren(a) for a in part_number.split(",")]
                    if query_stripped and query_stripped in aliases_stripped:
                        return ic_config, manufacturer
        return None, None
```

Four properties the selector must preserve, all readable above:
1. **The rung order is exact → alias-exact → alias-paren-stripped.** D-01's "case-insensitively
   equals the raw token" is rung 2; the paren-stripped rung is rung 3 and is why D-02's verbatim
   carry-through matters — the alias that *matched* may differ from the token by its parens.
2. **`.lower()` on both sides, `.strip()` on the alias** — the selector must not invent a different
   case rule, or it can pick an alias `get_eprom_config` did not match on.
3. **The split is `part_number.split(",")` with per-element `.strip()`** — "first alias" in D-01
   means `part_number.split(",")[0].strip()`, carried **verbatim** (not lowercased), since
   `canonical_part_number` is a display value.
4. **`return None, None` on no match** is the shape D-24's `None`-safety mirrors; `build_title` then
   falls back to the raw token.

`import re` is a **function-local** import here. Keep the mirror's imports local likewise if the
selector lands in `cli_handlers.py`, matching that module's stated local-import convention
(`cli_handlers.py:2419-2422` imports the three `submit` formatters locally, with the reason written
out: *"`submit` imports `diagnostic_report`, so a module-level import here would tighten an already-
layered graph"*).

---

### `cli_handlers.py` — `_chip_id_fields` (RPT-A1), sampler, deletions

**`_chip_id_fields`** (`:2189-2217`) — the scrape D-23 deletes:

```python
    for r in results:
        if r.op == OP_ID and r.reason and "mismatch" in r.reason.lower():
            mismatch_reason = r.reason
            # reason text: "chip-ID mismatch: expected 0x.., detected 0x.."
            try:
                detected_hex = r.reason.rsplit("0x", 1)[-1]
                chip_id_actual = int(detected_hex, 16)
            except (ValueError, IndexError):
                chip_id_actual = None
            break
```

Replacement reads `r.chip_id_detected` off the step. Note the loop must keep producing
`mismatch_reason` from `r.reason` (that stays prose per D-23) while sourcing the *number*
structurally — i.e. the `if` predicate can keep its `"mismatch" in r.reason.lower()` test for the
reason, but `chip_id_actual` must populate on a **passing** id step too (RPT-A1), so the single
combined loop becomes two independent reads over the id step. The function's docstring currently
asserts the opposite (*"on a clean/NA/SKIPPED id step there is no actual-id disagreement to surface,
so both stay `None`"*) and is a required edit.

**`_make_sampler`** (`:2230-2254`) — quoted as the D-12 proof, not as an edit target. It assigns
**only** the four before/after fields:

```python
        if phase == "before":
            report.vpp_before_mv = vpp
            report.vpe_before_mv = vpe
        elif phase == "after":
            report.vpp_after_mv = vpp
            report.vpe_after_mv = vpe
```

**Deletions:** `_is_uv_eprom:2257-2270` **survives** (it is `_resolve_write_scope`'s only content and
D-09 keeps the UV predicate available to `derive_plan`'s callers — but check whether it has any
remaining caller after `_resolve_write_scope` dies; if not, it must leave
`_HANDLER_FUNCTION_NAMES` too, or `test_handler_function_names_all_resolve_to_real_callables`
reddens for the *second* name as well as `_resolve_write_scope`). `_resolve_write_scope:2272-2312`
and its whole docstring go. Call site:

```python
    interactive = _is_interactive()
    write_scope = _resolve_write_scope(app, chip, interactive=interactive)
    plan = derive_plan(chip, app.db, write_scope=write_scope)
```

becomes `plan = derive_plan(chip, app.db)` — and `interactive = _is_interactive()` at `:2402` has no
other consumer on that path, so check before leaving a dead local (ruff F841 will catch it; ruff is
green-tree leg 1).

**The report heading** (`:2497`, `f"# dev test -- {chip}"`) is one of D-03's four canonical surfaces.
Its neighbour `diagnostic_report.py:826` (console table title) is the other rendering one.

---

### `submit.py` — `build_title` (RPT-F1, D-01/D-03)

**Analog: itself.** `:174-185`, one caller at `:698` (`title = build_title(report, chip)`):

```python
def build_title(report: Any, chip: str) -> str:
    """`[dev test] <chip> — <PASS/FAIL/INCONCLUSIVE> (<shorthash>)`.
    ...
    """
    d = report.to_dict()
    shorthash = d["dedup_fingerprint"]
    verdict = overall_verdict(report.results)
    return f"[dev test] {chip} — {verdict} ({shorthash})"
```

The pattern to copy: **the title already reads its variable parts off `report.to_dict()`, not off its
own parameters.** The canonical name should come the same way —
`d["auto_capture"]["canonical_part_number"] or chip` (D-24's fallback) — rather than by calling the
selector a second time inside `submit`. That is what keeps the title, the body's new
`canonical_part_number` line and the saved artifact from disagreeing, and it is the same single-
source argument `_duration_text`'s docstring makes for the two duration tables. The `chip` parameter
is retained as the fallback; the em dash `—` and the exact spacing are asserted by existing tests.

---

### New RPT-B1 source-census test (D-12)

**Analog: `firestarter_app/tests/test_readback_inventory.py:57-148`** — the closest existing
AST-census-with-planted-RED in the tree, and the one CONTEXT.md's `<code_context>` names. Copy this
three-test triad wholesale:

```python
import ast, pathlib, pytest
from firestarter import chip_test as ct

_TARGET_ATTR = "read_eprom"
_TARGET_OWNER = "operator"

def _read_eprom_census(source: str) -> tuple[int, set[str]]:
    """... Each call site is attributed to its innermost enclosing
    `FunctionDef` by comparing line-number containment ... correct regardless
    of `ast.walk` traversal order, which does not guarantee an
    outer-before-inner visit."""
    tree = ast.parse(source)
    functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    sites = [
        n for n in ast.walk(tree)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
        and n.func.attr == _TARGET_ATTR
        and isinstance(n.func.value, ast.Name) and n.func.value.id == _TARGET_OWNER
    ]
    ...

def _engine_source() -> str:
    source = pathlib.Path(ct.__file__).read_text(encoding="utf-8")
    assert len(source) > 1000      # the file-actually-loaded guard
    return source

def test_engine_has_exactly_two_read_eprom_call_sites():
    _assert_census(_engine_source(), expected_count=2,
                   expected_enclosing={"_dispatch_read", "_read_region"})

def test_a_planted_third_call_site_reddens_the_census():
    source = _engine_source()
    assert source.count(_PLANTED_ANCHOR) == 1          # the anchor is unique
    mutated = source.replace(_PLANTED_ANCHOR, _PLANTED_ANCHOR + _PLANTED_ANCHOR, 1)
    count, enclosing = _read_eprom_census(mutated)
    assert count == 3

def test_an_empty_enclosing_allow_list_fails_rather_than_passing_vacuously():
    with pytest.raises(AssertionError):
        _assert_census(_engine_source(), expected_count=2, expected_enclosing=set())
```

Five things to lift, in order of importance:
1. **`ast.Attribute` matching on `attr` *and* `value.id`, not text.** RPT-B1's census is over
   `ast.Attribute` **stores** (`ast.Assign` targets, and `ast.AnnAssign`) whose `attr` is
   `vpp_mv`/`vpe_mv` and whose `value` resolves to a report object. The measured trap above makes
   this mandatory: a textual `grep vpp_mv` returns ~20 hits that are all *database* fields
   (`ic_layout.py:583`, `test_check_dispatch_invariants.py` ×12, `test_ic_layout.py:133`). The
   honest census expects **zero assignments and zero emit sites** and must not count DB dicts.
2. **`assert len(source) > 1000`** — the guard that stops a mis-resolved path passing vacuously.
   Under D-12 the census also needs a positive control on the *dataclass*: assert the attribute is
   absent from `DiagnosticReport`'s field set, or a census over an empty attribute name passes.
3. **`assert source.count(_PLANTED_ANCHOR) == 1`** before mutating — the anti-vacuity leg's own
   anti-vacuity leg.
4. **In-memory `source.replace(...)`. No fixture file is ever written.** This is the pattern
   `<code_context>` mandates.
5. **The explicit vacuity test** (`test_an_empty_..._fails_rather_than_passing_vacuously`) as a
   third, separate test.

`test_blast_radius_invariance.py:523+` carries the in-memory-mutation form for a *dict* rather than a
source string (`test_to_dict_key_list_pins_are_sensitive_to_added_and_removed_keys` — *"an in-process
mutation of a real `to_dict()` mapping, never a change to production"*): use that one for the D-14
key-list pins and the `test_readback_inventory.py` one for the D-12 source census.

**Evidence convention** (`.planning/phases/174-*/evidence/`, `180-*/evidence/`): flat `.txt`
transcripts named `<phase>-<plan>-<slug>.txt`, e.g. `174-01-anti-vacuity-red-green.txt`,
`180-01-verdict-pin-red.txt`. Phase 181 should create
`.planning/phases/181-.../evidence/181-NN-<slug>.txt`.

---

### `test_blast_radius_invariance.py` — the six key-list pins (D-14) and the schema literal (D-13)

**Analog: `ec1db5c`'s own diff of this file** — the exact edit shape, already performed once:

```diff
-(`firestarter/diagnostic_report.py:771-790`) emits eleven top-level keys today."""
+(`firestarter/diagnostic_report.py:771-790`) emits twelve top-level keys today
+(Phase 178 plan 01 adds `run_status`, schema 1.8)."""
+    "run_status",
...
-    assert SCHEMA_VERSION == "1.7" == baked, (
+    assert SCHEMA_VERSION == "1.8" == baked, (
-        f"{baked!r}, expected '1.7' (RPT-E1 moves this to '2.0' in Phase 181)"
+        f"{baked!r}, expected '1.8' (RPT-E1 moves this to '2.0' in Phase 181)"
```

Line-exact pin locations measured today: `_TO_DICT_KEYS:94`, `_VOLTAGE_KEYS:114`, `_BANNER_KEYS:125`,
`_AUTO_CAPTURE_KEYS:135`, `_TRANSPORT_HEALTH_KEYS:149` (**does not move**), `_DB_DIFF_KEYS:167`
(**does not move**), `_STEPS_ELEMENT_0_KEYS:179`; assertion sites `:420`, `:447`, `:456`, `:465`,
`:478`, `:491`, `:500`; schema triple-equality `:513-519`. `_TRANSPORT_HEALTH_KEYS` additionally
carries a **length pin** (`assert len(_TRANSPORT_HEALTH_KEYS) == 9`, `:482`) — check whether any
moving list carries a companion length assertion, since a key-list edit that misses its length twin
leaves a contradiction.

The failure message that D-15 re-anchors RPT-E3 onto (`:276-280`), quoted so the planner cites the
surviving mechanism and not the retired ledger:

```python
    assert computed == expected, (
        f"{shape_id} re-keyed: expected {expected}, got {computed}. If "
        "deliberate, land the behaviour change and the re-key of this "
        "literal as SEPARATE commits, so the re-key stays a reviewable unit."
    )
```

---

### `tests/fixtures/report_shapes.py` — the 19 frozen shapes (D-16)

Structure measured: 764 lines. `_BUILDERS` dict `:705-724` (19 entries),
`SHAPE_IDS = tuple(sorted(_BUILDERS))` at `:727`, `FROZEN_HASHES` `:729-750` (19 literals),
`RESERVED_SHAPE_IDS = frozenset()` at `:751` — **fully drawn down**, plus a module-level
collision `assert` at `:753-756`, and `build_shape` `:759-764` raising `KeyError` naming `SHAPE_IDS`
rather than returning `None`.

The relationship D-16 rests on: `SHAPE_IDS` is *derived* from `_BUILDERS`, and `FROZEN_HASHES` is a
parallel hand-written dict; `test_dedup_fingerprint_is_frozen` is
`@pytest.mark.parametrize("shape_id,expected", sorted(FROZEN_HASHES.items()))`. So **all 19 hashes
are asserted individually** and D-16's headline leg is simply that this parametrization stays green
with zero literal edits — plus a completeness pin that `set(FROZEN_HASHES) == set(SHAPE_IDS)`.
The two D-02 tripwire rows are present and unchanged: `"m27c512-full-canonical-name":
"776846bf2dc8"` and `"m27c512-full-comma-joined-name": "37ad34d39a19"`.

`_build_real_path_report:467-503` is the shared builder — `write_scope` is one of its four keyword
parameters (`:468`) and it forwards to `derive_plan(chip, _REAL_DB, write_scope=write_scope)` at
`:485`. **D-09 changes this signature**: the parameter and all 10 `write_scope="full"` call sites go.
Its docstring claims it mirrors `cli_handlers.py:2374-2431` as *"the SOLE production
`DiagnosticReport` construction site"* — that citation must be re-anchored when D-09 shortens the
handler. The builders that must keep byte-identical output while this parameter disappears are the
whole D-16 claim, so this is the highest-risk mechanical edit in the phase: dropping the parameter
must not change `derive_plan`'s output for `"full"`, which is D-09's `not is_uv` equivalence.

Also note `tools/snapshot_report_shapes.py --check` is green-tree leg 4 and the `__snapshots__/`
syrupy snapshots are per-shape — `ec1db5c`'s commit message says it *"regenerate[d] all 17 frozen
report snapshots"*, so an additive key **does** move the syrupy snapshots even when it cannot move
the hashes. That is the precedent for how RPT-A's additive keys are landed without violating D-16.

---

### `pyproject.toml` (HYG-01, HYG-02)

**Analog: the `py32` extra, `:62-70`** — the only bounded dependency in the file, and it carries its
reasoning in comments above the pin (this file is not product source, so comments are fine here):

```toml
# Floor raised to 1.3.1 (HOST-07 / D-19): the current pyusb release at plan
# time, Requires-Python >=3.9.0, satisfiable on this project's py39 floor.
# Upper bound <2 refuses a future major that could reorder ctrl_transfer's
# parameters, which Plan 127-06's API-surface test pins against 1.3.1's shape.
py32 = [
    "pyusb>=1.3.1,<2",
]
```

HYG-01 applies the same `>=x,<y` form to `"syrupy>=5.0",` at `:73`, with the same style of
upper-bound justification. HYG-02's runtime list is `:46-53` exactly as CONTEXT.md states:
`pyserial>=3.5, requests>=2.20, tqdm>=4.60, click>=8.1, rich>=14.0, packaging>=21.0` — six entries.
HYG-02 wants that asserted **as a test**; the existing analog for a pyproject-parsing test is
`tests/test_check_dispatch_invariants.py`-style tooling tests, but the specific "pin the dependency
list" test has no precedent — see **No Analog Found**.

---

### `firestarter_app/tools/check_devtest_orchestrator.py` (HYG-04, D-19)

**Analog: the allow-list itself, `:152-165`** (measured; CONTEXT.md said `:152-164`), with its
fail-open warning written directly above it at `:145-151`:

```python
# name, and added `_resolve_write_scope` alongside it. Every future helper
# added to the `dev test` surface MUST be listed here, or this gate silently
# under-covers exactly that new code -- `tests/test_check_devtest_orchestrator
# .py::test_handler_function_names_all_resolve_to_real_callables` makes this
# a permanently-enforced invariant rather than a one-off fix.
_HANDLER_FUNCTION_NAMES = frozenset(
    {
        "dev_test", "_verdict_code", "_overall_exit_code", "_dev_test_exit_code",
        "_sanitize_chip_token", "_is_uv_eprom", "_resolve_write_scope",
        "_chip_id_fields", "_is_interactive", "_make_sampler",
    }
)
```

The comment block itself records the precedent D-19 repeats — *"a set pointing at nothing (a leftover
speculative name)"* was previously repaired by a two-way edit. **Consumer sites that break when
`_resolve_write_scope` leaves the set**, measured: `tests/test_check_devtest_orchestrator.py:518`
(docstring), `:525` (`assert "_resolve_write_scope" in ..._HANDLER_FUNCTION_NAMES`), `:555` (a
second literal list), `:577` (a docstring claim about the call graph). Four sites, one file. That
`:525` assertion is a **positive** membership assertion, so removing the name from the frozenset
without editing the test turns HYG-04 RED — this is the two-way edit D-19 is warning about, and it is
two-way in the *test* as well as the checker.

---

## Shared Patterns

### Additive-field-cannot-re-key (applies to every RPT-A change and to D-16)
**Source:** `diagnostic_report.py:263-320` (`dedup_fingerprint`) + `DiagnosticReport.run_status`'s
docstring at `:676-683`.
```python
    ac = report.auto_capture
    parts = [ac.chip or "", str(ac.protocol or "")]
    for result in report.results:
        cls = result.fingerprint.classification if result.fingerprint else ""
        parts.append(f"{result.op}={result.verdict}:{cls}")
    policy = repeat_policy_tag(report.results)
    if policy:
        parts.append(policy)
```
Two load-bearing properties: the pre-image is an **explicit allow-list with no reflection over
dataclass fields** (so absence from the list *is* the exclusion mechanism — this is what HYG-03/D-18
protects), and every discriminator appends **only when non-empty** (`if policy:`), which is how
already-filed fingerprints stayed byte-identical. Any new discriminator must follow the empty-default
direction. `run_status`'s docstring is the model for how to *state* an exclusion in a docstring:
> *"Deliberately excluded from `dedup_fingerprint`'s hash input (D-08) -- that function builds its
> hash from an explicit allow-list with no reflection over dataclass fields, so this field's absence
> from that list is the whole exclusion mechanism."*

### Absent data never fabricates confidence
**Source:** `_voltage_dict:733-738` docstring, `_transport_dict`'s `NOT_MEASURED` substitutions
(`:725-731`), `_aggregate_cycle_results`'s `if durations else None`.
**Apply to:** D-05 (`duration_s` stays `None`), D-24 (`canonical_part_number` is `None`-safe), D-11's
`None` = "no comparison possible". Note the module distinguishes `NOT_MEASURED` from `NOT_REPORTED`
(`:51-54`): *"this field was never ASKED, rather than asked and empty."* If `canonical_part_number`
needs a string sentinel rather than `None`, that distinction already exists — do not invent a third.

### Read off the exported dict, never recompute
**Source:** `render()`'s `runs` cell and `_RAN_VERDICTS` gate (`:970-989`), `build_title:181`.
**Apply to:** the `elapsed` console row (D-07), the canonical heading (D-03), the issue body's
`elapsed` line. This is what makes "the console and the saved artifact cannot disagree" structural
rather than a convention, and it is why D-06's `elapsed` must be a **stored** field.

### No comments, docstrings only (D-26)
**Source:** `/workspaces/CLAUDE.md` §"Source code comments — hard rule".
**Note the tension the planner must handle explicitly:** the files this phase edits are *dense* with
existing narrative comments (`cli_handlers.py:2315-2364` is 50 lines of it; `_step_dict:782-804` is
23). The rule is about comments *this phase writes*; the pre-existing ones are a separate sweep
(explicitly declined in CONTEXT.md's Reviewed Todos), **except** the `ALWAYS WRITES` block, which is
deleted because it is *false*, not because it is a comment. Every new rationale in this phase goes in
a docstring — which is exactly where these modules already carry it. `pyproject.toml` and
`tools/*.py` are not product source; comments there are fine and the `py32` pin is the model.

---

## No Analog Found

| Target | Role | Data flow | Reason |
|---|---|---|---|
| Shrinking a Phase-174 key-list pin (`_VOLTAGE_KEYS` −2, `_BANNER_KEYS` −1) | test pin | transform | **First deletion ever through these pins.** `git log -S'_VOLTAGE_KEYS' -- tests/test_blast_radius_invariance.py` returns exactly one commit — `5693bf7 test(174-03)`, the one that created it. `ec1db5c` is the additive precedent; the subtractive direction is unprecedented. The planner should treat "the pin shrinks and the suite is still non-vacuous" as its own verification leg, not as a copy of `ec1db5c`. |
| A "pin the runtime dependency list" test (HYG-02) | test | n/a | No existing test parses `pyproject.toml`. Nearest structural cousins are the tooling tests (`tests/test_check_*.py`) which import a checker module; a pyproject-reading test has no precedent and needs its own shape decision (`tomllib` is stdlib on py3.11, so no new dependency — which is itself HYG-02's claim). |
| `.claude/skills/devtest-triage/SKILL.md` row edit (RPT-F2 / D-5) | doc | n/a | Meta-repo markdown, single table row at `:375`. No code analog. The constraint is the **same-commit** rule with the `vpp_mv` deletion — which spans two repos, since the deletion is in `firestarter_app`. "Same commit" is therefore impossible literally; the planner must adjudicate this as two commits landed together (one per repo) and say so, or the D-5 criterion is unsatisfiable as written. |
| `MILESTONES.md` HYG-03 entry (D-18) | record | n/a | Prose, in the voice of the existing v1.36 corrections. Not code. |

---

## Metadata

**Analog search scope:** `firestarter_app/firestarter/`, `firestarter_app/tests/`,
`firestarter_app/tools/`, `firestarter_app/pyproject.toml`, `/workspaces/tools/`,
`/workspaces/.claude/skills/`, `.planning/phases/*/evidence/`, plus `git log -S` archaeology on
`firestarter_app`.
**Files scanned:** 14 read in whole or in part; 6 census/count greps via `/usr/bin/grep`.
**Not scanned (deliberately):** everything under `/workspaces/firestarter/` (firmware submodule,
out of scope), and `firestarter_app_py32/` + `.v1.34-arms/{v133,control}/`, which contain
gitignored/archived copies of `check_devtest_orchestrator.py` — the tracked source is
`firestarter_app/tools/check_devtest_orchestrator.py`.
**Pattern extraction date:** 2026-09-09
