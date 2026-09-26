# Phase 162: CHIP — 11-Part `dev test` Sweep on the Reference Rig - Pattern Map

**Mapped:** 2026-08-27
**Files analyzed:** 8 (4 new, 4–5 modified)
**Analogs found:** 8 / 8

> Scope reminder: every target file lives under `.planning/v1.34/`. Nothing in
> `/workspaces/firestarter/`, `/workspaces/firestarter_app/` or `/workspaces/.v1.34-arms/` is a
> target — those are read-only reference only.

## File Classification

| New/Modified File | New? | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|---|
| `.planning/v1.34/tools/append_chip_evidence.py` | new | tool / record-writer | file-I/O + transform (derive → validate → append) | `.planning/v1.34/tools/append_evidence.py` | exact |
| `.planning/v1.34/tools/render_chip_evidence.py` | new | tool / renderer | batch transform (JSONL → Markdown), `--check` | `.planning/v1.34/tools/render_evidence.py` | exact |
| `.planning/v1.34/bench/CHIP-EVIDENCE.jsonl` | new | data / schema header + append-only rows | append-only record | `.planning/v1.34/bench/EVIDENCE.jsonl` line 1 | exact |
| `.planning/v1.34/bench/CHIP-EVIDENCE.md` | new | generated document | rendered artifact, byte-compared | `.planning/v1.34/bench/EVIDENCE.md` | exact |
| `.planning/v1.34/tools/run_gates.sh` | modified | gate runner / config | batch, accumulate-then-report | its own existing live-gate blocks | exact (self-analog) |
| `.planning/v1.34/tools/capture_provenance.py` | modified | tool / provenance capture | request-response (argparse → probes → JSON) | its own `_CHIP_CHOICES` + `pins["chips"][args.chip]` | exact (self-analog) |
| `.planning/v1.34/rig-pins.json` | modified | config / pin data | static config | its own `chips` map (2 entries today) | exact (self-analog) |
| `.planning/v1.34/PROCEDURE.md` | modified | procedure document | prose + step list | Amendments 1–3, `P-01/P-02/P-04/P-06/P-11` | exact |
| `.planning/v1.34/tools/render_steps.py` | modified (optional, R6 option A) | tool / parser+renderer | transform | its own `_STEP_ID_RE` / `extract_step_list_section` / `validate_steps` | exact (self-analog) |

---

## Pattern Assignments

### `append_chip_evidence.py` (tool, derive → validate → append)

**Analog:** `.planning/v1.34/tools/append_evidence.py` (982 lines; 13 selftest legs today — 3 positive, 10 negative. RESEARCH R3 asks for 16 on the sibling.)

#### Module skeleton and sibling-import idiom (`append_evidence.py:59-138`)

```python
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_MILESTONE_DIR = _HERE.parent
_DEFAULT_PINS = _MILESTONE_DIR / "rig-pins.json"
_DEFAULT_IMAGE_PLAN = _MILESTONE_DIR / "bench" / "IMAGE-PLAN.json"
_DEFAULT_JSONL = _MILESTONE_DIR / "bench" / "EVIDENCE.jsonl"

RECORD_KEYS = [
    "chip", "family", "board", "shield", "blank_state", "op", "sha256", "verdict",
    "anomalies", "position_id", ...
]

def _load_sibling(name: str):
    spec = importlib.util.spec_from_file_location(name, _HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod

def _gate_record():
    return _load_sibling("gate_record")

def _render_evidence():
    return _load_sibling("render_evidence")
```

Copy verbatim, changing only `_DEFAULT_JSONL` → `bench/CHIP-EVIDENCE.jsonl`, `RECORD_KEYS` → the
9 locked columns + the chip extension set, and adding a `_render_chip_evidence()` sibling loader.
**Note the beware:** `_HERE` here is correct (it resolves the *tool's* directory and the sibling
lives beside it). This is not the `check_permitted_claims.py` `_HERE` defect — do not "fix" it.

#### Accumulate-then-report cross-check (`append_evidence.py:144-215`)

```python
def validate_position(position_id, provenance, wrv, readback, image_plan_row, pins) -> list[str]:
    violations: list[str] = []

    def _check(label: str, a: object, b: object) -> None:
        if a != b:
            violations.append(f"{label}: {a!r} != {b!r}")

    _check("position_id vs provenance.position_id", position_id, provenance.get("position_id"))
    _check("position_id vs wrv.position_id", position_id, wrv.get("position_id"))
    ...
    chip = provenance.get("chip")
    if chip not in pins.get("chips", {}):
        violations.append(f"rig-pins.json has no chips entry for chip {chip!r}")
    return violations
```

The chip sibling's equivalent cross-checks (from the source artifacts it *does* have): the
`dev test` report's own chip token vs `provenance.chip` vs `--chip-token`; the report's
`fw_board_identity` vs the position's provenance board fields; `provenance.arm` vs
`readback.flashed_arm`; the copied-out artifact's sha vs a sha recomputed from the copy.

#### The derived-never-input outcome (`append_evidence.py:218-228`)

```python
def _derive_outcome(wrv: dict) -> str:
    """Never accepted as input -- always derived. Outside this function, no code path may
    ever assign 'validated' to a row's outcome."""
    if (
        wrv.get("sha_verdict_judged") == "match"
        and not wrv.get("verdict_disagreement")
        and not wrv.get("size_violations")
    ):
        return "validated"
    return "skipped-with-reason"
```

Chip sibling: derive `outcome` from the `dev test` report's per-step verdicts / exit code, never
from a flag. Keep the two-value domain (`validated` / `skipped-with-reason`) — `gate_record.check_outcome`
rejects a third state.

#### The refuse-an-incomplete-position pipeline (`append_evidence.py:393-479`)

```python
def process_position(...) -> tuple[int, list[str], dict | None]:
    violations: list[str] = []
    ok, pins, detail = _load_json(pins_path, "pins file")
    if not ok:
        violations.append(detail)
    ...
    if violations:
        return 1, violations, None

    gr = _gate_record()
    violations.extend(validate_position(position_id, provenance, wrv, readback, image_plan_row, pins))
    violations.extend(
        gr.check_required_fields(
            {"blank_state": human["blank_state"], "verdict": human["verdict"],
             "anomalies": human["anomalies"]},
            ["blank_state", "verdict", "anomalies"],
        )
    )
    ...
    violations.extend(gr.check_commands({"commands": combined_commands}, pins))

    outcome = _derive_outcome(wrv)
    if outcome == "skipped-with-reason" and not _names_symptom(human["verdict"]):
        violations.append(
            "outcome derives as 'skipped-with-reason' but --verdict-file names no observed "
            "symptom (P-H2 record contract)"
        )
    if violations:
        return 1, violations, None
    ...
    re_mod = _render_evidence()
    try:
        re_mod.append_row_to_file(jsonl_path, row)
    except re_mod.RenderError as exc:
        return 1, [str(exc)], None
    return 0, [], row
```

Two load-bearing properties to preserve: **`gate_record` runs before the write, not after**, and
the write is delegated to `render_*.append_row_to_file` — the appender never hand-rolls a JSONL
append. The `dev test` sibling adds one step before all of this: **copy
`<config dir>/reports/dev-test-<chip>.{json,md}` to the per-position artifact path** (D-09), and
that copy must happen (and be sha'd) before any control re-run can overwrite the fixed path.

#### Distinct absent/unparseable branches (`append_evidence.py:321-336`)

```python
def _load_json(path: Path, label: str) -> tuple[bool, dict | None, str]:
    if not path.exists():
        return False, None, f"{label} not found at {path}"
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return False, None, f"{label} at {path} could not be read: {exc}"
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        ...
```

RESEARCH R7/Security V5 flags `.get(…, 0)` silent-defaulting at `append_evidence.py:261`
(`chip_cfg.get("algorithm", 0)`) as the path **not** to copy — the sibling should refuse an
unexpected report shape rather than default it.

#### `--selftest` routed before the full parse (`append_evidence.py:511-521`)

```python
def main() -> int:
    # --selftest is scanned for BEFORE the full parse, deliberately: several arguments here
    # are required=True with no default, so a normal ap.parse_args() would itself refuse
    # `--selftest` alone with a missing-required-argument error ...
    if "--selftest" in sys.argv[1:]:
        return _run_selftest()

    ap = build_argparser()
    args = ap.parse_args()
```

Mandatory: `run_gates.sh` greps for the literal token `"--selftest"` in the file *and* runs
`python3 <tool> --selftest` with no other argument. Any `required=True` argument makes the naive
route fail — copy this pre-scan.

#### `--selftest` structure: tmpdir discipline + accumulate + named-reason assertions (`append_evidence.py:731-985`)

```python
def _run_selftest() -> int:
    import shutil
    import tempfile

    ok_overall = True

    def report(name: str, passed: bool, detail: str = "") -> None:
        nonlocal ok_overall
        status = "PASS" if passed else "FAIL"
        if not passed:
            ok_overall = False
        suffix = f" -- {detail}" if detail else ""
        print(f"{status}: {name}{suffix}")

    tmp = Path(tempfile.mkdtemp(prefix="append_evidence_selftest_"))
    try:
        leg = tmp / "pos1"; leg.mkdir()
        paths = _write_leg_fixtures(leg)
        jsonl_path = _write_jsonl(leg)
        rc, violations, row = process_position(...)
        report("positive 1: ... derives all 40 record_keys in schema order and round-trips ...",
               rc == 0 and not violations and list(row.keys()) == RECORD_KEYS and len(row) == 40,
               f"rc={rc} violations={violations}")
        ...
        report("negative 1 ...: --position-id disagreeing with provenance AND wrv is refused, "
               "both disagreements named in one pass",
               rc == 1
               and any("position_id vs provenance.position_id" in v for v in violations)
               and any("position_id vs wrv.position_id" in v for v in violations),
               str(violations))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"append_evidence.py --selftest overall: {'ok' if ok_overall else 'FAILED'}")
    return 0 if ok_overall else 1
```

Rules the sibling copies: every leg gets its **own** subdirectory under one `mkdtemp`; every
negative leg asserts on the **named reason substring**, never merely `rc == 1`; every leg drives
the real `process_position`, never a stub; `finally: shutil.rmtree(...)`; one overall line at the
end and `return 0/1`.

Fixture module constants to mirror: `_SELFTEST_POSITION_ID`, `_BASE_PINS`, `_BASE_PROVENANCE`,
`_BASE_WRV`, `_BASE_READBACK`, `_BASE_IMAGE_PLAN`, `_BASE_HUMAN`, plus
`_write_leg_fixtures(base_dir, **overrides)` (deep-copies the base dicts and `.update()`s) and
`_write_jsonl(base_dir, existing_rows=())` which writes a minimal `_schema` line 1.

#### What the chip sibling must NOT copy

- **`_CHIP_LABEL = {"w27c512": "EPROM_STD", "w29c020": "FLASH_5V_PAGE"}`** (`append_evidence.py:92`)
  — a hardcoded two-part chip table. With eleven parts this is exactly the arm-agnostic-constant
  defect class that recurred four times in Phase 160. Derive the label from
  `rig-pins.json`'s `chips` map (extended per R7), not from a literal in the tool.
- **`chip_cfg.get("algorithm", 0)`** — a missing algorithm must be a named refusal, not `0x00`.
- **The five-human-fields count.** `append_evidence.py`'s human set is
  `blank_state`/`verdict`/`anomalies`/two write durations (+ optional `--shield-note`). The chip
  sibling's human set is different (D-09: verdict prose, `anomalies`, the operator's meter
  reading, plus the VPP figures per D-11/D-12) — do not carry the WRV durations across.
- **The WRV vocabulary** (`written_sha`, `read_shas`, `sha_verdict_judged`, `image_mask`,
  `expect_size`) — none of it exists in a `dev test` report.
- **The docstring's GSD citations.** `append_evidence.py`'s module docstring cites `D-05`, `D-16`,
  `PD-1`, `P-04`, `RIG-02`, and inline comments cite `Rule 1 fix (found live, 160-09)` etc. See
  **Hard-Rule Conflict** below before copying that style.

---

### `render_chip_evidence.py` (tool, batch transform + `--check`)

**Analog:** `.planning/v1.34/tools/render_evidence.py`

#### The determinism contract, stated in the docstring (`render_evidence.py:31-43`)

```
DETERMINISM CONTRACT (mirrors tools/catalog/codegen.py's LCAT-05 contract)
---------------------------------------------------------------------------
Two consecutive renders of the same JSONL produce byte-identical Markdown. Achieved by:
  - rows emitted in a deterministic order derived from the record (sorted by position_id)
  - no timestamp, no hostname, and no value not derived from the JSONL's own schema/rows
  - LF line endings, written explicitly (open(..., newline="\n"))
  - every hash/numeric/list field formatted identically on every run (json.dumps with a
    fixed separator, no key-sorting inside a row -- record_keys order is preserved)
The prior milestone's evidence Markdown (.planning/v1.18/bench/EVIDENCE.md) carries a
`**Generated:** <ISO-8601 timestamp>` line -- that is the SPECIFIC thing not to copy here,
because a timestamp would make the render non-reproducible and `--check` permanently red.
```

The four non-determinism sources and how they are neutralised:
| Source | Mitigation in the analog |
|---|---|
| timestamp / hostname | none emitted anywhere, in the header *or* the rows (`jsonl_convention` says so too) |
| dict / row ordering | `sorted(..., key=lambda r: str(r.get("position_id", "")))`; cells emitted in `record_keys` order |
| nested value formatting | `json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)` in `_format_cell` |
| line endings / locale | `open(tmp_path, "w", encoding="utf-8", newline="\n")` in `atomic_write` |

#### `--check` regenerate-and-byte-compare (`render_evidence.py:363-386`)

```python
    rendered = render_markdown(schema, rows)

    if args.check:
        target_path = Path(args.target)
        if not target_path.exists():
            print(f"FAIL: --check target does not exist: {target_path}", file=sys.stderr)
            return 1
        committed = target_path.read_text(encoding="utf-8")
        if committed == rendered:
            print(f"OK: {target_path} matches a fresh render of {args.jsonl} (--check green)")
            return 0
        diff = "\n".join(
            difflib.unified_diff(
                committed.splitlines(), rendered.splitlines(),
                fromfile=str(target_path), tofile="<fresh render>", lineterm="",
            )
        )
        print("FAIL: committed target diverges from a fresh render -- hand-edit suspected", file=sys.stderr)
        print(diff, file=sys.stderr)
        return 1

    atomic_write(Path(args.target), rendered)
    print(f"OK: rendered {args.jsonl} -> {args.target}")
    return 0
```

Note the three exit shapes: `0` green, `1` on drift **with the unified diff printed to stderr**,
`1` on a missing target. Nothing is written under `--check`.

#### Atomic write (`render_evidence.py:221-226`)

```python
def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(path.name + ".tmp")
    with open(tmp_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)
    os.replace(tmp_path, path)
```

#### `append_row_to_file` — the appender's write path (`render_evidence.py:234-306`)

Contract the chip renderer must reproduce (the chip appender delegates to it):
- refuses a missing / empty JSONL, a line 1 without `_schema`, a `_schema` without `record_keys`
- `raise RenderError(f"row omits declared key(s): {missing}")` and
  `raise RenderError(f"row carries key(s) not declared in record_keys: {extra}")`
- refuses a duplicate `position_id` (the selftest asserts on `"already exists"`)
- re-reads and asserts the existing prefix is byte-unchanged, then:

```python
    ordered_row = {k: new_row[k] for k in record_keys}
    new_content = original
    if not new_content.endswith("\n"):
        new_content += "\n"
    new_content += json.dumps(ordered_row, ensure_ascii=False, separators=(",", ":")) + "\n"
    atomic_write(jsonl_path, new_content)
    return new_position_id
```

- `_pre_write_hook` is an injectable seam the selftest uses to simulate a concurrent modification
  without a real race. Keep it.

#### Document body shape (`render_evidence.py:161-218`)

`render_markdown` emits: H1 `# {milestone} Bench Evidence — {phase_pinned}`, a generated-by
blockquote naming the exact `--check` command, a provenance paragraph, `## Close-out counting rule`
(printing `schema["close01_counting_rule"]` verbatim), a main `## Positions (excludes bring-up rows)`
table, an excluded-rows table, and `## Reconciliation`:

```python
def _reconciliation_text(schema: dict, nonbringup_rows: list[dict]) -> str:
    expected = schema.get("position_count_expected", 0)
    validated = sum(1 for r in nonbringup_rows if r.get("outcome") == "validated")
    skipped = sum(1 for r in nonbringup_rows if r.get("outcome") == "skipped-with-reason")
    accounted = validated + skipped
    missing = expected - accounted
    return (
        f"{validated} validated + {skipped} skipped-with-reason = {accounted} of "
        f"{expected} positions accounted for ({missing} not yet recorded)."
    )
```

The chip renderer's reconciliation is SC#4's `10 + N` arithmetic — same shape, different equation,
and it must state the deviation from the roadmap's `11 + N` (D-06).

**Do not copy:** `bringup_cell_id_prefix = "BRINGUP-"` as a hardcoded default. The analog does
`schema.get("bringup_cell_id_prefix", "BRINGUP-")` — schema-driven with a literal fallback. The
chip file's exclusion mechanism (named absence, control re-runs) is different; drive it entirely
from the chip schema, with no literal fallback that could silently mis-count.

---

### `bench/CHIP-EVIDENCE.jsonl` line 1 `_schema` (data, append-only)

**Analog:** `.planning/v1.34/bench/EVIDENCE.jsonl` line 1.

**The 9 `locked_columns`, byte-copy these:**

```json
"locked_columns": ["chip","family","board","shield","blank_state","op","sha256","verdict","anomalies"]
```

They are the first 9 entries of `record_keys`, in that order. `locked_columns_note` explains why:

> "locked_columns is the nine-column core pinned verbatim from .planning/v1.15/bench/EVIDENCE.json
> and .planning/v1.18/bench/EVIDENCE.json, where it is byte-identical … The two-tier shape exists
> so the close-out phase (166) can assert on the locked core across every milestone's evidence file
> uniformly, while each sweep phase adds only the columns its own oracle produces — observed
> extension keys in this file's rows are exactly the evid_extension_columns list, never the
> locked_columns list, and never a key outside either list."

**Counting rule and expected count** (the sibling models its own on these, with its own numbers):

```json
"position_count_expected": 20,
"close01_counting_rule": "Computed over the non-bring-up rows only: (number of rows with outcome=='validated') + (number of rows with outcome=='skipped-with-reason') == position_count_expected (20). The first term is 'positions holding a result'; the second is 'positions holding a named reason for absence' (a recorded skip, never a blank). Phase 166's CLOSE-01 close-out arithmetic is this equation evaluated as a script over rows, not a human count -- a silent gap between the row count and 20 is structurally visible as a nonzero remainder rather than something a reader has to notice."
```

**The exclusion mechanism** (the model for the chip file's own):

```json
"bringup_cell_id_prefix": "BRINGUP-",
"bringup_row_exclusion": "A row whose cell_id begins with the bring-up prefix 'BRINGUP-' is rig evidence produced by Phase 160's own bring-up plans (08-12), not sweep evidence produced by Phases 161-163 -- it is excluded from the 20-position close-out reconciliation. ..."
```

A prefix on an existing field, a named default in the schema, and a prose clause saying *what* is
excluded and *why* — three parts, all present. The chip file needs the same three for its
control-re-run rows and its named-absence row.

**`not_measured_convention`** (verbatim, the anti-fabrication contract):

```json
"not_measured_convention": "A reading that tooling blocks -- because a bootloader interrogation has not yet been recorded (judged_span_policy: PENDING-xshowvector on uno328pb), because a CLI path does not exist for a value, or for any other named reason -- is recorded as the string 'not measured — <reason>' (em dash or double-hyphen separator) with its blocking reason on the SAME line, never as a blank, null, or omitted field. tools/gate_record.py's field-presence check treats this exact shape as a valid, non-null value and rejects a bare 'not measured' with no reason."
```

**`negative_control_convention`** (verbatim):

```json
"negative_control_convention": "A negative control (the W27C512 VPP-high init guard firing; the deliberate wrong-arm cross-flash producing a MISMATCH) is recorded as having FIRED -- the record states the guard/mismatch actually occurred and what happened next -- never merely as having been configured or made available. A mechanism that was present but never observed to fire is not evidence that it works."
```

The chip file's own negative-control examples: the `MSG_ERR_VPP_HIGH` guard, and D-10's
"nothing was filed" proof (which must be an issue-count before/after, not an assertion).

**Also copy, adjusting values:** `schema_version: 1`, `purpose`, `milestone: "v1.34"`,
`phase_pinned`, `outcome_domain` **and** `outcome_values` carrying the identical two-value list
(`outcome_values_note` explains the duplication — `gate_record.check_outcome` reads
`outcome_values`, the plan pins `outcome_domain`), `jsonl_convention`, `artifact_volume_policy_ref`.

`jsonl_convention` is the determinism half of the pair with `render_*.py --check`:

> "One JSON object per line, LF line terminators, UTF-8 without ASCII escaping (ensure_ascii=False).
> Rows are emitted with keys in exactly record_keys order and are never sorted. … **No timestamp is
> recorded anywhere in this file** … A row is never rewritten once appended."

**Do not copy:** the 31 `evid_extension_columns` (all WRV), and `position_count_expected: 20`.
`EVIDENCE.jsonl`'s 20 is untouched by this phase (D-08).

---

### `run_gates.sh` (modified — two new live gates)

**Analog:** its own existing gate blocks.

**Discovery + the `--selftest` advertisement check that fails the suite** (`run_gates.sh`, Step 1):

```bash
PY_TOOLS=()
while IFS= read -r -d '' f; do
    PY_TOOLS+=("$f")
done < <(find "$TOOLS_DIR" -maxdepth 1 -name '*.py' -print0 | sort -z)

if [ "${#PY_TOOLS[@]}" -eq 0 ]; then
    echo "FAIL: discovery found zero *.py files under $TOOLS_DIR -- a suite that finds nothing must fail, not pass" >&2
    exit 2
fi

for tool in "${PY_TOOLS[@]}"; do
    name="$(basename "$tool")"
    if ! grep -q -- '"--selftest"' "$tool"; then
        echo "FAIL: $name does not advertise a --selftest mode" >&2
        FAILURES+=("$name: does not advertise a --selftest mode")
        continue
    fi
    echo "--- selftest: $name ---"
    if python3 "$tool" --selftest; then
        SELFTEST_COUNT=$((SELFTEST_COUNT + 1))
        echo "selftest PASS: $name"
    else
        FAILURES+=("$name: --selftest exited non-zero")
        echo "selftest FAIL: $name" >&2
    fi
done
```

The advertisement check is a **grep for the literal `"--selftest"` with double quotes** — the
`ap.add_argument("--selftest", ...)` line satisfies it. Both new tools are discovered automatically
(no registration needed for step 1); the suite goes 12/12 → 14/14.

**An existing live gate, the exact shape to copy twice** (`run_gates.sh`, Step 2):

```bash
echo "--- live gate: render_evidence.py --check (bench/EVIDENCE.md vs a fresh render) ---"
if python3 "$TOOLS_DIR/render_evidence.py" --jsonl "$BENCH_DIR/EVIDENCE.jsonl" --target "$BENCH_DIR/EVIDENCE.md" --check; then
    echo "live gate PASS: render_evidence.py --check"
else
    FAILURES+=("render_evidence.py --check: bench/EVIDENCE.md diverges from a fresh render")
    echo "live gate FAIL: render_evidence.py --check" >&2
fi

echo "--- live gate: gate_record.py (bench/EVIDENCE.jsonl record-shape gate) ---"
if python3 "$TOOLS_DIR/gate_record.py" --jsonl "$BENCH_DIR/EVIDENCE.jsonl" --pins "$PINS_FILE"; then
    echo "live gate PASS: gate_record.py"
else
    FAILURES+=("gate_record.py: bench/EVIDENCE.jsonl failed its own record-shape gate")
    echo "live gate FAIL: gate_record.py" >&2
fi
```

Four-part shape: an `echo "--- live gate: …"` banner, an `if python3 …; then` (never `&&`, never a
pipe), a `FAILURES+=("<tool>: <named reason>")` on the else branch, and a `>&2` FAIL echo. The two
new gates are `render_chip_evidence.py --check` against `CHIP-EVIDENCE.md` and `gate_record.py
--jsonl "$BENCH_DIR/CHIP-EVIDENCE.jsonl" --pins "$PINS_FILE"`.

**Placement:** both new gates go outside the `--quick` block (as the two analogs do — neither
touches an arm binary or an image file), so `--quick` still runs them.

**Exit code, read directly and never through a pipe** (Summary block):

```bash
if [ "${#FAILURES[@]}" -eq 0 ]; then
    echo "ALL GATES PASSED"
    exit 0
else
    echo "FAILURES (${#FAILURES[@]}):" >&2
    for f in "${FAILURES[@]}"; do
        echo "  - $f" >&2
    done
    exit 1
fi
```

Documented codes: `0` all passed, `1` one or more failed, `2` bad usage / zero tools discovered.
Note `set -euo pipefail` at the top: any `bash run_gates.sh | tee …` in a plan's `<automated>` leg
would read `tee`'s status, not the suite's. CONTEXT.md's discretion section says exactly this.

**Also update:** the `WHAT THIS RUNS` header comment's live-gate list (a–e today) — Amendment
discipline applies to this file's own docstring too.

---

### `capture_provenance.py` (modified — `_CHIP_CHOICES` derived from pins)

**Analog:** itself. Exactly two sites, with an ordering constraint between them.

Site 1 — the hardcoded literal (`capture_provenance.py:77`, in the block at `:74-77`):

```python
_SHIELD_REV_CHOICES = ["Rev 2.0", "Rev 2.2", "Modified Rev 0"]
_ARM_CHOICES = ["control", "v133"]
_TARGET_CHOICES = ["uno", "uno328pb", "leonardo"]
_CHIP_CHOICES = ["w27c512", "w29c020"]
```

Site 2 — the argparse consumer (`capture_provenance.py:141`):

```python
    ap.add_argument("--chip", required=True, choices=_CHIP_CHOICES)
```

Site 3 — the hard index that reads the pins (`capture_provenance.py:613`):

```python
    try:
        arm_cfg = pins["arms"][args.arm]
        chip_cfg = pins["chips"][args.chip]
        avrdude_cfg = pins["avrdude"]
    except KeyError as exc:
        print(f"FAIL: rig-pins.json missing expected key: {exc}", file=sys.stderr)
        return 1
```

**The ordering constraint:** argparse validates `--chip` against `_CHIP_CHOICES` and exits **2**
at parse time, *before* `main()` ever reaches line 613 and reads `rig-pins.json`. So a part added
to `rig-pins.json`'s `chips` map alone is still rejected at exit 2 with an argparse usage message,
never with the tool's own named `FAIL:`. `_CHIP_CHOICES` must therefore be *derived from the pins
file at import time* (module-level load of `_DEFAULT_PINS`, keys of `chips`, sorted) so the two
lists cannot drift. Add a selftest leg asserting `set(_CHIP_CHOICES) == set(pins["chips"])` and one
asserting an unknown token is refused.

Two cautions for the derived form: `_DEFAULT_PINS` must still resolve when `--pins` overrides it
(the override is a runtime path, the choices list is import-time — state which wins), and an
unreadable pins file at import time must fail loudly, not fall back to an empty choices list (an
empty `choices=[]` makes *every* `--chip` invalid — a fail-open-looking fail-closed).

**Do not copy:** the literal list itself. It is the same hardcoded-constant class as
`_CHIP_LABEL`.

**Path-containment discipline to reuse in the new appender** (`capture_provenance.py:228-237`):

```python
def resolve_out_path(candidate: str, milestone_dir: Path) -> tuple[bool, Path | None, str]:
    resolved = Path(candidate).resolve()
    milestone_resolved = milestone_dir.resolve()
    parent = resolved.parent
    if parent != milestone_resolved and milestone_resolved not in parent.parents:
        return False, None, (
            f"--out {candidate!r} resolves to {resolved}, whose parent is outside "
            f"{milestone_resolved} -- refusing a path that traverses out of the milestone dir"
        )
    return True, resolved, ""
```

Also reusable as-is (`_cell_id_type`, `capture_provenance.py:125-131`): an argparse `type=` callable
raising `argparse.ArgumentTypeError` for `..`/leading-`/`/odd characters.

---

### `rig-pins.json` (modified — `chips` map 2 → 11 entries, `chip_token` added)

**Analog:** its own two entries.

```json
"chips": {
  "w27c512": { "size_bytes": 65536, "pin_count": 28, "package": "DIP28", "vpp_mv": 12000, "algorithm": 7, "stamp_width": 16 },
  "w29c020": { "size_bytes": 262144, "pin_count": 32, "package": "DIP32", "vpp_mv": 12000, "algorithm": 5, "stamp_width": 32 }
}
```

Six fields per part today. R7 adds `chip_token` (the DB token `dev test` takes, e.g. `M27C512`
vs the key `m27c512`). Consumers already reading this map: `capture_provenance.py:613`
(`pins["chips"][args.chip]`), `append_evidence.py:191-193` (`chip not in pins.get("chips", {})`)
and `append_evidence.py:261` (`chip_cfg.get("algorithm", 0)`).

Cautions:
- `stamp_width` is a **WRV-image** field with no meaning for a `dev test` part. Either record it as
  a real value where a part is also a WRV part, or omit it — do not invent a plausible number.
  `append_evidence.py` reads it only via the image-plan cross-check, which chip rows do not have.
- `vpp_mv` here must match the app DB target the run will actually use (D-11/D-12 records
  `vpp_target_mv` per part) — a divergence between this pin and the DB is a finding, not something
  to smooth over in the pin file.
- The two existing entries are byte-frozen inputs to Phase 161's twelve recorded positions.
  **Extend the map; do not reformat or reorder the two existing entries.**

---

### `PROCEDURE.md` (modified — Amendment 4)

**Analog:** Amendments 1–3 (`PROCEDURE.md:555-632`) and the `P-NN` step bodies.

**The amendment house style**, from Amendment 2's opener:

```markdown
**Amendment 2 — 2026-08-27, Phase 160 Plan 13:** (a) What changed: `P-11`'s teardown gained a
literal command block for the `probe_board.py` re-run its prose already prescribed ...
(b) Why: RIG-05's D-17 fresh-context reconstruction ... surfaced this as a prescription
ambiguity ... (c) Which cells ran under which text: every bring-up cell that has run so far
(`BRINGUP-uno`, `BRINGUP-uno328pb`, `BRINGUP-leonardo`, `BRINGUP-wrv`) ran under the OLD
(prose-only) `P-11` text ... No `## Step list` text outside `P-11`'s own body moved, and the
arm-agnostic empty-diff render gate (`render_steps.py --arm control` vs `--arm v133`) was
re-confirmed empty after this edit — the new command block carries no arm-dependent token
(`probe_board.py` takes no `$ARM_BIN`).
```

Fixed elements: bold `**Amendment N — <date>, Phase NNN Plan MM:**`; inline `(a) What changed:`
with numbered clauses `(1)…(4)` when there is more than one; `(b) Why:` mirroring the same numbers;
`(c) Which cells ran under which text:` naming *every* cell explicitly; and a closing sentence
**re-confirming the `render_steps.py` empty-diff gate** and stating why the new text is
arm-agnostic. Amendment 3 also demonstrates pinning concrete measured values inline (path, byte
count, sha256, mtime) rather than by reference.

Amendment 4's `(c)` clause has a fact the earlier ones did not: Phase 161's twelve positions
(`A1`, `A2`, `A3/B2`) ran under the Amendment-3 text; Amendment 4 lands before the first chip-sweep
part. Say so, and re-pin the `~/.firestarter/config.json` mtime (RESEARCH open question 5 measured
`1787854674` against Amendment 3's pinned `1787817565` — record it as the fourth recurrence, do not
silently overwrite).

**The `P-NN` step body shape** (`P-02`, the fullest example):

```markdown
### P-02 — Re-verify port identity

Claude re-verifies port identity for **this cell**, never inheriting it from a previous task:

```
python3 .planning/v1.34/tools/probe_board.py --target $TARGET --port $PORT \
  --pins .planning/v1.34/rig-pins.json --out $CELL_DIR/board_probe.json
FIRESTARTER_CONFIG_DIR=$FIRESTARTER_CONFIG_DIR $ARM_BIN -p $PORT hw
```

The signature probe (`probe_board.py`) is the **authoritative** board identity; ... Performer:
Claude. Record fields: `board_signature`, `controller_string`.
```

Every step carries: an `### <ID> — <Title>` heading, prose, a **literal fenced command block**
(Amendment 2 made this mandatory — no prose-only steps), a `Performer:` clause naming operator or
Claude, and a `Record field(s):` clause. `P-06` additionally shows the operator/Claude split and
the never-bypassed guard language.

**§Scope, the text Amendment 4 must correct** (`PROCEDURE.md:13-27`):

> "One cell run covers **both arms** (`control` then `v133`) and **both bench chips** (W27C512
> DIP28, then W29C020 DIP32) … A cell therefore holds **four positions** … This document is
> executed **unchanged** by Phases 161–163."

Both sentences are false for Phase 162 (CONTEXT.md domain fact 1). The correction is part of
Amendment 4's `(a)`.

**Constraints on the `C-NN` ids, from `render_steps.py:58` and `validate_steps` (`:123-148`):**

```python
_STEP_ID_RE = re.compile(r"^P-(?P<num>\d\d)$")
_ANNOTATION_RE = re.compile(r"\[\s*arm\s*:\s*(?P<arm>[A-Za-z0-9_]+)\s*\]")
```

```python
def validate_steps(steps: list[dict]) -> None:
    """Raise ProcedureParseError on: a non-P-NN id, a duplicate id, ids out of ascending
    numeric order, or an annotation naming an arm outside _ARM_CHOICES."""
    for step in steps:
        m = _STEP_ID_RE.match(step["id"])
        if not m:
            raise ProcedureParseError(f"step id {step_id!r} does not match the P-NN pattern")
        ...
        if prev_num is not None and num <= prev_num:
            raise ProcedureParseError(
                f"step ids are not in strictly ascending order: ...")
```

and the section extractor (`render_steps.py:66-77`):

```python
def extract_step_list_section(text: str) -> str:
    """Return the text strictly between the '## Step list' heading and the next '## ' heading."""
    m = _STEP_LIST_HEADING_RE.search(text)
    if not m:
        raise ProcedureParseError("no '## Step list' section found in the procedure")
```

Consequences the planner must design around, both already named in RESEARCH open question 1:
a `C-NN` heading placed **inside** `## Step list` reds the existing gate at
`does not match the P-NN pattern`; a `C-NN` list under a **new H2** is invisible to the tool and
therefore ungated — the vacuous-pass shape. R6 option (A) (teach `render_steps.py` an optional
second section, with two new selftest legs) is the recommendation, and it is what makes D-07's
"re-confirm the gate" non-vacuous. Ids must be two-digit and strictly ascending; the arm annotation
vocabulary is `_ARM_CHOICES` (`control`, `v133`).

---

## Shared Patterns

### Anti-fabrication: `"not measured — <reason>"`
**Source:** `gate_record.py:72,95,113-124`
**Apply to:** every human-supplied field in `append_chip_evidence.py`, every cell in the chip schema.

```python
_NOT_MEASURED_RE = re.compile(r"^not measured\s*(?:—|--)\s*\S.*$", re.IGNORECASE)

def check_required_fields(record: dict, required_keys: list) -> list[str]:
    violations: list[str] = []
    for key in required_keys:
        if key not in record:
            violations.append(f"required field {key!r} is missing")
            continue
        value = record[key]
        if _is_acceptable_not_measured(value):
            continue
        if _is_blank_or_placeholder(value):
            violations.append(f"required field {key!r} is null/blank/placeholder: {value!r}")
    return violations
```

Import it via `_load_sibling("gate_record")` — never re-derive the regex.

### Outcome domain (two states, never three)
**Source:** `gate_record.py:246-258`
**Apply to:** the chip schema's `outcome_values`/`outcome_domain` and the appender's derivation.

```python
def check_outcome(record: dict, schema: dict | None) -> list[str]:
    if "outcome" not in record:
        return []
    outcome_values = schema.get("outcome_values") if isinstance(schema, dict) else None
    if not outcome_values:
        return ["record carries 'outcome' but the schema has no outcome_values domain to check it against"]
    if record["outcome"] not in outcome_values:
        return [
            f"outcome {record['outcome']!r} is outside the two-state domain "
            f"{sorted(outcome_values)} -- a third state belongs only to Phase 165's triage "
            "classification of a failure after the fact, never to a cell result"
        ]
    return []
```

This is **schema-driven, not hardcoded** — it reads the domain from whichever JSONL's `_schema`
it was handed, so it gates `CHIP-EVIDENCE.jsonl` unmodified. Note the failure mode: a chip schema
that omits `outcome_values` produces the "no outcome_values domain to check it against" violation,
not a silent pass.

### Forbidden-flag re-parse over recorded argv
**Source:** `gate_record.py:177-245`
**Apply to:** the chip appender's `commands` field, before writing.

```python
def check_commands(record: dict, pins: dict) -> list[str]:
    ...
    allowed_argv0 = _allowed_argv0_set(pins)
    forbidden_flags = set(pins.get("forbidden_flags", []))
    avrdude_binary = pins.get("avrdude", {}).get("binary")

    def _forbidden_flags_for(token0: object) -> set:
        if avrdude_binary and token0 == avrdude_binary:
            return forbidden_flags - {"-b"}
        return forbidden_flags

    for i, entry in enumerate(commands):
        argv = entry.get("argv") if isinstance(entry, dict) else entry
        ...
        token0 = argv[0]
        if not (isinstance(token0, str) and os.path.isabs(token0)):
            violations.append(
                f"commands[{i}]: first token {token0!r} is not an absolute path -- a bare "
                "invocation would resolve to the un-named user-site editable install"
            )
```

Two properties chip rows inherit for free: an argv0 must be an **absolute** pinned path (this is
what catches the bare-`firestarter`-on-PATH third arm), and `-b` is exempted **only** for the
pinned avrdude binary. `FIRESTARTER_CONFIG_DIR=… ` prefixes never appear in argv — CONTEXT.md is
explicit that the only detector for a missing prefix is the `~/.firestarter` teardown assertion.

### `gate_record.py`'s reusability verdict for a second JSONL

`validate_jsonl_file(path, pins)` / `validate_object` / `load_schema_and_record` read `record_keys`,
`outcome_values` and the header from **the file they are given** — `--jsonl` and `--pins` are the
only inputs (`gate_record.py:427-441`). It gates `CHIP-EVIDENCE.jsonl` **as-is, with no new
argument**, provided the chip schema carries `record_keys` and `outcome_values`.

One caveat, already documented in `append_evidence.py`'s own docstring and worth restating in the
chip schema: `check_cross_oracle()` reads three keys (`written_image_sha256`, `read_sha256`,
`app_dev_consistency_verdict`) that exist in **neither** file's schema and is therefore
**structurally inert** on every row either appender writes. A green `gate_record` run is not a
cross-oracle check. If the chip row wants a cross-oracle (report sha vs the copied artifact's
recomputed sha), the appender must perform it — `gate_record` will not.

### Delegate the write; never hand-roll a JSONL append
**Source:** `render_evidence.append_row_to_file` (see above), used by `append_evidence.process_position`.
**Apply to:** `append_chip_evidence.py`.

### Sibling import via `spec_from_file_location`
**Source:** `append_evidence.py:121-137`, mirrored at `gate_record._load_check_arms()` and in
`capture_provenance.py`. The house idiom for tool-to-tool reuse in this directory — these files are
not a package and are never imported by name.

### Entry point
**Source:** `rig-pins.json` `tool_conventions.entry_point_idiom`, quoted in `render_evidence.py`'s
docstring: `sys.exit(main())`. Both new tools use it.

---

## Hard-Rule Conflict — flagged, not smoothed over

The prompt's hard rule forbids GSD provenance citations (`D-NN`, `Phase NNN`, `LOCK-NN`) in tool
code, JSON and shell. **Every analog in `.planning/v1.34/tools/` violates it densely**, and does so
deliberately:

- `append_evidence.py` module docstring: `"the deriving evidence-row writer (D-05)"`,
  `"D-16 boundary"`, `"PER-POSITION ARTIFACT LAYOUT (PD-1)"`, `"judge_readback.py at PROCEDURE.md P-04"`.
- `gate_record.py:138-143,189-198`: `"Rule 1 fix (found live, 160-11 BRINGUP-wrv …)"`,
  `"Phase 145 D-17's withdrawn permission"`.
- `capture_provenance.py`: `"RIG-02's 'before any test step' ordering"`, `"161-02 seam"`.
- `run_gates.sh` header: `"the full host-side gate suite for Phase 160 (RIG-01..05)"`.
- Selftest leg names embed `D-05`, `P-H2`, `Pitfall 5`; `EVIDENCE.jsonl`'s `_schema` prose strings
  embed `D-12`, `D-15/D-18`, `RIG-02`, `CLOSE-01`, phase numbers.

The recorded rule in the operator's memory scopes the prohibition to **product code** (firmware and
host app). These files are meta-repo bench records under `.planning/`, where the citation *is* the
record — and `close01_counting_rule`, `bringup_row_exclusion` and the amendment `(c)` clauses are
load-bearing prose that cannot be written without naming phases.

**The planner must resolve this explicitly rather than let an executor guess.** Recommendation:
copy the analogs' style inside `.planning/v1.34/` (consistency with eleven sibling files and the
schema prose that Phase 166 reconciles against), state the exemption in the plan so it reads as a
decision rather than a lapse, and hold the prohibition absolutely for anything in
`/workspaces/firestarter/` or `/workspaces/firestarter_app/` — where this phase writes nothing
anyway.

---

## No Analog Found

None. Every file in scope has a sibling in the same directory.

Two near-gaps worth naming:

| Concern | Nearest thing | Gap |
|---|---|---|
| Copying an artifact out before it is overwritten (D-09) | `capture_provenance.resolve_out_path` + `check_arms.compute_config_dir_sha` | No existing rig tool copies a file. The containment check and the hashing exist; the copy-then-sha-then-verify sequence is new code. RESEARCH names `compute_config_dir_sha` as the digest to reuse rather than re-implement. |
| A second gated section in `PROCEDURE.md` | `render_steps.extract_step_list_section` | Hardcoded to `## Step list`, single section. R6 option (A) generalises it; there is no prior two-section precedent to copy. |

---

## Metadata

**Analog search scope:** `.planning/v1.34/tools/` (13 files), `.planning/v1.34/bench/`,
`.planning/v1.34/PROCEDURE.md`, `.planning/v1.34/rig-pins.json`.
**Files scanned:** 9 read in depth (`append_evidence.py`, `render_evidence.py`, `gate_record.py`,
`capture_provenance.py`, `run_gates.sh`, `render_steps.py`, `PROCEDURE.md`, `rig-pins.json`,
`EVIDENCE.jsonl` line 1).
**Pattern extraction date:** 2026-08-27
