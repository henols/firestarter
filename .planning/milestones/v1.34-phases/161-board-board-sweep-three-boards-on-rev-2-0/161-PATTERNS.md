# Phase 161: BOARD — Board Sweep, Three Boards on Rev 2.0 — Pattern Map

**Mapped:** 2026-08-27
**Files analyzed:** 2 authored (1 new code file, 1 modified doc) + 1 directory-shape pattern
**Analogs found:** 2 / 2 authored (both exact)

This is a **hardware bench-execution phase**. `firestarter/` and `firestarter_app/` stay
byte-unchanged; no product-code file is mapped here. The file set is closed — CONTEXT D-05 and
D-06/D-12 name it in full.

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `.planning/v1.34/tools/append_evidence.py` (**NEW**) | utility / rig tool (deriving writer) | file-I/O → transform → append-only record | `.planning/v1.34/tools/judge_wrv.py` (overall shape) + `render_evidence.py` (the write path it delegates to) + `gate_record.py` (validation idioms it imports) | **exact** |
| `.planning/v1.34/PROCEDURE.md` — Amendment 3 (**MODIFIED**) | config / procedure doc | append at file bottom | Amendments 1 & 2, `PROCEDURE.md:499-529` | **exact** |
| Per-cell/per-position evidence artifacts (produced by tools at the bench) | data artifacts | tool-written | `.planning/v1.34/bench/cells/BRINGUP-wrv/` | **exact worked example** |

**Closest overall analog for `append_evidence.py`: `judge_wrv.py`.** Why: it is the only sibling
that is (1) a *deriving writer* — it produces a machine-derived record keyed on `--position-id`
rather than probing a device, (2) pure-function-at-the-core with a thin CLI shell, so its
`--selftest` exercises the real derivation logic and not a mock, (3) short enough (344 lines) to be
copied whole as a skeleton, and (4) already the tool `append_evidence.py` reads most of its fields
out of. `render_evidence.py` and `gate_record.py` are **not** the skeleton — they are libraries
`append_evidence.py` imports through the sibling-import idiom (see Shared Patterns).

---

## Pattern Assignments

### `.planning/v1.34/tools/append_evidence.py` (rig tool, deriving writer)

**Analog:** `.planning/v1.34/tools/judge_wrv.py` — copy its file skeleton verbatim and replace the
domain logic.

**Module docstring must open with the D-16 boundary paragraph** (`judge_wrv.py:2-12`, every tool
carries a variant):

```python
"""judge_wrv.py -- the full-device write->read->verify judge (D-10/D-11/RIG-04).

D-16 boundary: this is meta-repo BENCH TOOLING, not host source. It is authored and lives
only under .planning/v1.34/tools/ in the meta repo. It must NEVER be copied into
firestarter/ or firestarter_app/ -- this phase changes no firmware and no host source.
Nothing here is imported by, or imports from, either sub-repo.
"""
```

**Imports + path defaults** (`judge_wrv.py:56-66`):

```python
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_DEFAULT_PINS = _HERE.parent / "rig-pins.json"
```

Stdlib only (`rig-pins.json:175` `tool_conventions.import_policy`; `pyserial` in `touch_1200.py`
is the single permitted exception and does not apply here).

**Pure-core / thin-CLI split** — the comment banner is itself house style (`judge_wrv.py:69-72`):

```python
# ---------------------------------------------------------------------------
# Pure judging logic -- no subprocess, no device, no app invocation.
# Exercised directly by --selftest.
# ---------------------------------------------------------------------------
```

`append_evidence.py`'s equivalent core should be `build_row(provenance: dict, wrv: dict,
readback: dict, image_plan_row: dict, pins: dict, human: dict) -> tuple[dict, list[str]]` — a pure
function over already-parsed dicts returning `(row, violations)`, so the selftest drives the real
derivation and cross-checks with in-memory fixtures.

**Argparse construction** (`judge_wrv.py:157-169`) — `description=__doc__`, long flags only, no
positionals, `--pins` defaulting to `_DEFAULT_PINS`, `--selftest` last:

```python
def build_argparser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--written", help="path to the image that was written")
    ap.add_argument("--reads", help="directory dev consistency-check --keep-files filled")
    ap.add_argument("--expect-size", type=int, help="65536 (W27C512) or 262144 (W29C020)")
    ap.add_argument("--app-verdict", type=int, help="the exit code dev consistency-check returned (0/1/2)")
    ap.add_argument("--position-id", help="cell x arm x chip identifier for this position")
    ap.add_argument("--pins", default=str(_DEFAULT_PINS), help="path to rig-pins.json")
    ap.add_argument("--out", help="write the verdict JSON here")
    ap.add_argument("--selftest", action="store_true")
    return ap
```

The token **must be written `"--selftest"` with double quotes** — `run_gates.sh` greps for that
literal (see Shared Patterns → `--selftest` discovery).

**`main()` shape, selftest dispatched first, exit-code discipline** (`judge_wrv.py:172-204`):

```python
def main() -> int:
    ap = build_argparser()
    args = ap.parse_args()

    if args.selftest:
        return _run_selftest()

    required = [
        ("--written", args.written),
        ("--reads", args.reads),
        ("--expect-size", args.expect_size),
        ("--app-verdict", args.app_verdict),
        ("--position-id", args.position_id),
    ]
    missing = [name for name, val in required if val is None]
    if missing:
        print(f"FAIL: missing required argument(s): {missing}", file=sys.stderr)
        return 2

    written_path = Path(args.written)
    if not written_path.is_file():
        print(f"FAIL: --written file does not exist: {written_path}", file=sys.stderr)
        return 1
```

Exit-code contract, house-wide: **`0` ok · `1` real failure · `2` bad usage / missing required
argument**. Note `capture_provenance.py:514-520` is the *variant* to copy if any argument is
`required=True`, because argparse would otherwise refuse `--selftest` alone:

```python
    # --selftest is scanned for BEFORE the full parse, deliberately: --shield-rev is
    # required=True with no default (D-13), so a normal `ap.parse_args()` would itself
    # refuse `--selftest` alone with a missing-required-argument error before this
    # function ever got a chance to route to the selftest, which carries no device
    # arguments at all.
    if "--selftest" in sys.argv[1:]:
        return _run_selftest()
```

**`append_evidence.py` should use this variant** — its proposed surface (RESEARCH §Proposed
argument surface) marks `--position-id`, `--verdict-file`, `--anomalies-file`, `--blank-state` and
the two write durations as required.

**Entry point** (`judge_wrv.py:343-344`; `rig-pins.json:172` `tool_conventions.entry_point_idiom`):

```python
if __name__ == "__main__":
    sys.exit(main())
```

(`gen_addr_image.py`'s `raise SystemExit(main(sys.argv))` is the documented single exception —
do not follow it.)

**Failure reporting on the way out, and success line** (`judge_wrv.py:223-238`) — note the failure
message *names every contributing field*, it does not just say "failed":

```python
    if not success:
        print(
            f"FAIL: position {args.position_id} judged "
            f"sha_verdict_judged={result['sha_verdict_judged']!r} "
            f"read_count={result['read_count']} distinct_read_shas={result['distinct_read_shas']} "
            f"verdict_disagreement={result['verdict_disagreement']} "
            f"size_violations={result['size_violations']}",
            file=sys.stderr,
        )
        return 1

    print(
        f"OK: position {args.position_id} judged match "
        f"read_count={result['read_count']} distinct_read_shas={result['distinct_read_shas']}"
    )
    return 0
```

**Atomic JSON write** (`judge_wrv.py:211-215`) — temp sibling + `replace`, parents created first:

```python
    out_path = Path(args.out) if args.out else Path.cwd() / f"judge_wrv.{args.position_id}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = out_path.with_name(out_path.name + ".tmp")
    tmp_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    tmp_path.replace(out_path)
```

Same idiom, `os.replace` spelling, in `capture_provenance.py:441-444`:

```python
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = out_path.with_name(out_path.name + ".tmp")
    tmp_path.write_text(json.dumps(ordered, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    os.replace(tmp_path, out_path)
```

`append_evidence.py` should **not** hand-roll this for `EVIDENCE.jsonl` — delegate to
`render_evidence.append_row_to_file()`, which already owns it (below).

**`--selftest` structure — accumulate-then-report, named positive and negative legs**
(`judge_wrv.py:246-262`, and the `finally` cleanup at 337-340):

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

    tmp = Path(tempfile.mkdtemp(prefix="judge_wrv_selftest_"))
    try:
        ...
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    return 0 if ok_overall else 1
```

Negative legs are **named after the defect they prevent**, not numbered abstractly
(`judge_wrv.py:279-287`):

```python
        # --- negative 1: Pitfall 6 false green -- three IDENTICAL reads, all WRONG, app=0 ---
        r = judge_position(written, reads_of(other, other, other), expect_size, 0, "POS-2")
        report(
            "negative 1 (Pitfall 6): three self-consistent but wrong reads with app_verdict=0 "
            "-> mismatch AND verdict_disagreement true (the false green the app's own PASS "
            "would otherwise hide)",
            r["sha_verdict_judged"] == "mismatch" and r["verdict_disagreement"] is True,
            str(r),
        )
```

**Minimum negative legs `append_evidence.py`'s selftest must carry** (from D-05's own argument —
the failures `gate_record.py` structurally cannot see):
- a field transcribed from the **wrong position's** provenance (`position_id` disagreement across
  the three artifacts) is refused;
- `wrv.written_sha != provenance.image_sha` is refused;
- `provenance.arm != readback.flashed_arm` is refused;
- a `blank_state` of bare `"not measured"` (no reason) is refused; `"not measured — <reason>"` is
  accepted;
- an empty `verdict` / `anomalies` is refused;
- a `skipped-with-reason` outcome derived while the verdict prose names no symptom is refused;
- a duplicate `position_id` is refused (surface `render_evidence`'s own message);
- **positive:** a complete fixture triple derives all 40 columns and the row round-trips through
  `append_row_to_file` into a temp JSONL.

**Refusing to run without a required artifact — the canonical hard-refusal**
(`capture_provenance.py:311-328`). Copy this shape for each of the three source artifacts: named
path in the message, distinct branches for *absent*, *unparseable*, and *present but missing the
required keys*:

```python
    verdict_path = bench_dir / "cells" / cell_slug / "READBACK-VERDICT.json"
    if not verdict_path.exists():
        return False, None, (
            f"readback verdict artifact not found at {verdict_path} -- judge_readback.py "
            "must run and write this artifact before capture_provenance.py for this cell"
        )
    try:
        data = json.loads(verdict_path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        return False, None, f"readback verdict artifact unreadable: {exc}"
    judged = data.get("sha_actual_judged")
    whole = data.get("sha_whole_flash_unjudged")
    if not judged or not whole:
        return False, None, (
            f"readback verdict artifact at {verdict_path} is missing sha_actual_judged/"
            f"sha_whole_flash_unjudged: {data!r}"
        )
    return True, {"judged": judged, "whole": whole}, ""
```

…and its caller (`capture_provenance.py:447-466`), which is the "refuses to run at all" half:

```python
    if not out_path.exists():
        print(
            f"FAIL: --patch-readback requires an existing record at {out_path} "
            "(run --pending-readback first)",
            file=sys.stderr,
        )
        return 1
    ...
    ok, readback, detail = read_readback_verdict(bench_dir, cell_slug)
    if not ok:
        print(f"FAIL: readback-verdict probe: {detail}", file=sys.stderr)
        return 1
```

Note the `(bool, value|None, detail)` return triple — that is the house signature for a probe that
can refuse. `append_evidence.py` should instead **accumulate** (`gate_record.py`'s idiom, below),
because D-05 requires every gap named in one pass, not the first one only.

**Accumulate-then-report validation + the `"not measured — <reason>"` valid-non-null**
(`gate_record.py:72`, `94-122`) — **import these, never re-derive the regex**:

```python
_NOT_MEASURED_RE = re.compile(r"^not measured\s*(?:—|--)\s*\S.*$", re.IGNORECASE)


def _is_acceptable_not_measured(value: object) -> bool:
    return isinstance(value, str) and bool(_NOT_MEASURED_RE.match(value.strip()))


def _is_blank_or_placeholder(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        stripped = value.strip()
        if stripped == "":
            return True
        if stripped.upper() in _PLACEHOLDER_VALUES:
            return True
        if stripped.lower().startswith("not measured") and not _is_acceptable_not_measured(value):
            return True
    return False


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

Every `check_*` returns `list[str]` and the caller extends one list — that is the accumulate idiom.

**Two-state outcome domain, read from the schema not hardcoded** (`gate_record.py:246-258`):

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

**Sibling reuse — the import idiom** (`gate_record.py:81-87`, mirrored at
`capture_provenance.py:361-365`). Use this to reach `gate_record._NOT_MEASURED_RE` /
`gate_record.check_commands` and `render_evidence.append_row_to_file`:

```python
# ---------------------------------------------------------------------------
# check_arms.py reuse -- compute_config_dir_sha only. No SHA algorithm is
# re-derived here.
# ---------------------------------------------------------------------------


def _load_check_arms():
    spec = importlib.util.spec_from_file_location("check_arms", _HERE / "check_arms.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod
```

**The append path to delegate to, not re-implement** — `render_evidence.append_row_to_file`
(`render_evidence.py:234-306`). It already does record-key presence + extra-key rejection,
outcome-domain validation, duplicate-`position_id` refusal, the byte-unchanged-prefix re-read, and
the atomic whole-file replace:

```python
def append_row_to_file(jsonl_path: Path, new_row: dict, _pre_write_hook=None) -> str:
    """Appends new_row to jsonl_path. Returns the appended position_id. ..."""
    ...
    missing = [k for k in record_keys if k not in new_row]
    if missing:
        raise RenderError(f"row omits declared key(s): {missing}")
    extra = [k for k in new_row if k not in record_keys]
    if extra:
        raise RenderError(f"row carries key(s) not declared in record_keys: {extra}")
    if new_row.get("outcome") not in outcome_domain:
        raise RenderError(
            f"row outcome {new_row.get('outcome')!r} is outside the schema's outcome "
            f"domain {outcome_domain!r}"
        )
    ...
    new_position_id = new_row.get("position_id")
    if new_position_id in existing_position_ids:
        raise RenderError(
            f"position_id {new_position_id!r} already exists -- a row is never "
            "rewritten once appended"
        )

    if _pre_write_hook is not None:
        _pre_write_hook(jsonl_path)

    current = jsonl_path.read_text(encoding="utf-8")
    if current != original:
        raise RenderError(
            "existing rows changed on disk between read and append -- refusing to write "
            "(append-only integrity: the prefix must be byte-unchanged before replace)"
        )

    ordered_row = {k: new_row[k] for k in record_keys}
    new_content = original
    if not new_content.endswith("\n"):
        new_content += "\n"
    new_content += json.dumps(ordered_row, ensure_ascii=False, separators=(",", ":")) + "\n"
    atomic_write(jsonl_path, new_content)
    return new_position_id
```

Two properties the planner must carry into `append_evidence.py`:
- the row dict is **re-ordered to `_schema.record_keys`** before serialisation, and serialised with
  `separators=(",", ":")`, `ensure_ascii=False` — do not reproduce this, let the sibling do it;
- `_pre_write_hook` is a deliberate **injectable seam for the selftest** to simulate a concurrent
  modification without a real race. `append_evidence.py`'s own selftest can use the same seam.

**The paired re-render** (`render_evidence.py:355` — the `--append` branch `return`s before the
render path). Every append **must** be followed, in the same step, by a plain render, or
`run_gates.sh`'s fourth live leg (`render_evidence.py --check`) goes red:

```bash
python3 /workspaces/.planning/v1.34/tools/render_evidence.py \
  --jsonl /workspaces/.planning/v1.34/bench/EVIDENCE.jsonl \
  --target /workspaces/.planning/v1.34/bench/EVIDENCE.md
```

---

### `.planning/v1.34/PROCEDURE.md` — Amendment 3 (procedure doc, modified)

**Analog:** Amendments 1 and 2, `PROCEDURE.md:499-529`. Both are a single bold-led paragraph
appended at the bottom of the file, after the `*Procedure defined: …*` italic line, with three
labelled clauses **(a)** what changed · **(b)** why · **(c)** which cells ran under which text.

**Amendment 1 verbatim** (`PROCEDURE.md:503-510`):

> **Amendment 1 — 2026-08-27, Phase 160 Plan 09:** (a) Standing bench rule 1 and the `$PORT`
> token row were widened from `/dev/ttyACM*`-only wording to also name `/dev/ttyUSB*`. (b) The
> `uno328pb` bring-up board (this plan) enumerates via a CH340 USB-serial bridge as `ttyUSB0`,
> not `ttyACM*` — the rule's substance (never inherit a port across cells/sessions) was already
> node-class-agnostic, only the illustrative wording named one class. No mechanical step changed
> and no `## Step list` text moved, so this amendment does not affect the SC#3 empty-diff render
> gate. (c) Every bring-up cell before this one (`BRINGUP-uno`, plan 08) ran under the old
> wording; no real sweep cell (`A1`/`A2`/`A3-B2`/`B1`/`B3`) has run yet under either wording.

**Amendment 2 verbatim** (`PROCEDURE.md:512-529`):

> **Amendment 2 — 2026-08-27, Phase 160 Plan 13:** (a) What changed: `P-11`'s teardown gained a
> literal command block for the `probe_board.py` re-run its prose already prescribed ("re-run
> `probe_board.py` to confirm the board identity has not changed since `P-02`"), naming an
> explicit, distinct output path (`$CELL_DIR/board_probe_teardown.json`). Every other step in
> this list (`P-02`, `P-04`, `P-06`, `P-07`, `P-09`) already carried a literal command block; `P-11`
> was the one exception, describing the re-probe only in prose. (b) Why: RIG-05's D-17
> fresh-context reconstruction (`bench/cells/BRINGUP-wrv/RECONSTRUCTION.md`,
> `RECONSTRUCTION-DIFF.md`) surfaced this as a prescription ambiguity — a fresh context given
> only the provenance record and this procedure had to invent an output filename by analogy to
> `P-02`'s, because the procedure itself gave none. A step whose literal command must be inferred
> by analogy rather than read is exactly the failure mode this document's "prescriptive, not
> prose" contract exists to prevent. (c) Which cells ran under which text: every bring-up cell
> that has run so far (`BRINGUP-uno`, `BRINGUP-uno328pb`, `BRINGUP-leonardo`, `BRINGUP-wrv`) ran
> under the OLD (prose-only) `P-11` text; `BRINGUP-wrv`'s own teardown (Phase 160 Plan 12) in
> fact never re-ran `probe_board.py` at teardown at all, only the config-dir check — a genuine
> compliance gap against the prose prescription, discovered by this same reconstruction exercise
> and recorded, not backfilled, in `RECONSTRUCTION-DIFF.md` (backfilling it now would require an
> avrdude signature probe against a board this phase's own constraints forbid touching with a
> chip seated). No real sweep cell (`A1`/`A2`/`A3-B2`/`B1`/`B3`) has run yet under either text.
> No `## Step list` text outside `P-11`'s own body moved, and the arm-agnostic empty-diff render
> gate (`render_steps.py --arm control` vs `--arm v133`) was re-confirmed empty after this edit —
> the new command block carries no arm-dependent token (`probe_board.py` takes no `$ARM_BIN`).

**Shape properties Amendment 3 must copy:**

1. Header: `**Amendment 3 — <date>, Phase 161 Plan <NN>:**` — date, phase and plan number, all
   three. Amendment 2 spells clause (a) as `(a) What changed:` and clause (c) as
   `(c) Which cells ran under which text:`; Amendment 1 omits the labels. Follow **Amendment 2**,
   the more recent and more explicit form.
2. One paragraph, no sub-bullets in either existing amendment. With four clause-(a) items
   (RESEARCH §Amendment 3), a numbered list inside clause (a) is a justified extension — but keep
   (a)/(b)/(c) as the top-level spine.
3. Clause (c) must state the bring-up-vs-sweep split, in the established wording: *"No real sweep
   cell (`A1`/`A2`/`A3-B2`/`B1`/`B3`) has run yet under either text."* Amendment 3 additionally
   says the new text governs every sweep cell, because it lands before the first one.
4. **Both amendments close by naming the empty-diff gate explicitly and saying why it stays
   empty.** Amendment 2's wording is the template: *"the arm-agnostic empty-diff render gate
   (`render_steps.py --arm control` vs `--arm v133`) was re-confirmed empty after this edit — the
   new command block carries no arm-dependent token."*

**`$ARM_BIN` token check.** Both surrounding step bodies do use `$ARM_BIN` in their literal command
blocks (`P-02`, `P-06`, `P-07`, `P-09`); the amendments' own added text does not. Amendment 3's
four clauses add no `$ARM_BIN` and no `[arm: …]` marker; `$POSITION_ID` is already a declared,
arm-independent substitution token (`PROCEDURE.md:106-118`, declared at :112). The gate should stay
empty. **Re-confirm by running `bash .planning/v1.34/tools/run_gates.sh` (third live leg) after the
edit, exit code measured directly, never through a pipe** (D-04).

---

## Per-Cell / Per-Position Artifact Shape (produced by tools, not authored)

**Worked example:** `.planning/v1.34/bench/cells/BRINGUP-wrv/` — one complete position. Verified
directory listing:

```
bench/cells/BRINGUP-wrv/
├── provenance.json                  # capture_provenance.py --out
├── WRV-VERDICT.json                 # judge_wrv.py --out
├── READBACK-VERDICT.json            # judge_readback.py --out-dir   ← CELL-level, one per flash event
├── flash_readback.bin  (32768 B)    ┐
├── expected_span.bin   (22952 B)    │ judge_readback.py --out-dir writes these five together
├── judged_span.bin     (22952 B)    │
├── SHA256SUMS.txt                   │
├── avrdude_read.stderr.log          ┘
├── probe.json / probe.json.stderr.log     # probe_board.py --out (P-02)
├── check_arms_teardown.json               # check_arms.py --out (P-11)
├── written.bin  (65536 B, gitignored)
├── reads/run_01.bin run_02.bin run_03.bin (gitignored)
├── WRITE.md                         # the human narrative for this position
├── POT.md                           # P-06's record
├── RECONSTRUCTION.md / RECONSTRUCTION-DIFF.md   # D-17 one-off, not per-position
└── logs/NN_<verb>.stdout.log + NN_<verb>.stderr.log
```

**Log numbering convention** — zero-padded two digits from `00`, sequential across the whole cell
(not per step), one `.stdout.log` + `.stderr.log` pair per invocation, suffix names the verb. The
actual `BRINGUP-wrv` sequence, which is the template for a sweep position:

```
00_check_arms_pre_cell   01_probe_board            02_hw_probe_pre_flash
03_capture_provenance_pending                      04_fw_checkout_v133
05_pio_upload_v133       06_judge_readback_v133    07_capture_provenance_patch
08_vpp_confirming_read   09_gen_addr_image         10_write_w27c512
11_consistency_check     12_judge_wrv              13_check_arms_teardown
```

(`04_fw_checkout_v133` has a `.stdout.log` only — a command that produced no stderr does not get an
empty file. Every other index has both.)

**Twelve-position scaling.** A sweep cell is four positions in one cell dir, so the per-position
files must be keyed on `$POSITION_ID`:
- `provenance_<position_id>.json` — always pass `--out` explicitly; the default
  `bench/cells/<slug>/provenance.json` collides across four positions;
- `READBACK-VERDICT.json` stays **cell-level, one per flash event** (two per sweep cell, one per
  arm) — it is written by `judge_readback.py --out-dir` at `P-04`, and `capture_provenance.py`
  reads it at the fixed path `bench/cells/<slug>/READBACK-VERDICT.json`
  (`capture_provenance.py:311`). Per-arm re-flash overwrites it; the arm's two positions must be
  patched before the next `P-04` overwrites the file.
- `written.bin` and `reads/run_*.bin` must go per-position — see the gitignore trap below.

### The `.gitignore` trap — measured, and it contradicts the obvious layout

`bench/.gitignore:8-9` is exactly two patterns:

```
cells/*/reads/
cells/*/written.bin
```

`git check-ignore -v` run this session, from `.planning/v1.34/bench`:

| Candidate path | Ignored? |
|---|---|
| `cells/A1/reads/A1__control__w27c512/run_01.bin` | **YES** (`.gitignore:8`) |
| `cells/A1/reads/A1__control__w27c512/written.bin` | **YES** (`.gitignore:8`) |
| `cells/A1/positions/A1__control__w27c512/written.bin` | **NO** |
| `cells/A1/positions/A1__control__w27c512/reads/run_01.bin` | **NO** |
| `cells/A1/written_A1__control__w27c512.bin` | **NO** |

**Consequence:** the only per-position layout that stays ignored without editing `.gitignore` is
**everything under `cells/<slug>/reads/<position_id>/`** — including `written.bin`. A
`cells/<slug>/positions/<position_id>/` layout (as RESEARCH's proposed `--wrv` default suggests)
would silently commit up to 12 large binaries, ~6.5 MB of `run_*.bin` plus 12 written images.
The planner must either (a) put both `written.bin` and `run_*.bin` under
`cells/<slug>/reads/<position_id>/`, or (b) extend `bench/.gitignore` in the same change as
Amendment 3's clause (3). `WRV-VERDICT.json` and `provenance_<pos>.json` are **committed** and must
not land inside an ignored directory.

**Commit-on-failure exception** (`bench/.gitignore:11-18`, mirroring `IMAGE-PLAN.json`'s
`artifact_volume_policy`) — for a position whose judged verdict is not a clean match:

```
#     git add -f bench/cells/<cell_slug>/reads/run_01.bin  (etc.)
#     git add -f bench/cells/<cell_slug>/written.bin
```

Committed by default: the six `.hex` + `SHA256SUMS.txt`, `IMAGE-PLAN.json`, every
`flash_readback.bin`, every `provenance*.json`, `EVIDENCE.jsonl`, `EVIDENCE.md`, the text logs.

---

## Shared Patterns

### The `--selftest` discovery contract (applies to `append_evidence.py`, suite-fatal)

**Source:** `.planning/v1.34/tools/run_gates.sh:99-129`

```bash
PY_TOOLS=()
while IFS= read -r -d '' f; do
    PY_TOOLS+=("$f")
done < <(find "$TOOLS_DIR" -maxdepth 1 -name '*.py' -print0 | sort -z)

if [ "${#PY_TOOLS[@]}" -eq 0 ]; then
    echo "FAIL: discovery found zero *.py files under $TOOLS_DIR -- a suite that finds nothing must fail, not pass" >&2
    exit 2
fi
...
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

Three literal consequences for any new file dropped into `tools/`:
1. The source must contain the token **`"--selftest"` with double quotes** — a single-quoted
   `'--selftest'` fails the grep even with a perfectly working flag.
2. `python3 <tool> --selftest` must exit **0 with no other arguments and no device attached**.
3. Discovery is `-maxdepth 1`, so `tools/__pycache__/` is not scanned — but any stray `.py` file
   left in `tools/` (a scratch script, a backup) **fails the whole suite**. Do not park anything
   there.

The selftest count is asserted: after Phase 161 the suite goes from **11/11** to **12/12**.

### Failure style — `FAIL:` to stderr, named reason, never a silent empty artifact

**Source:** `render_evidence.py:46-51` (docstring, "FAIL CLOSED"), enforced everywhere.
**Apply to:** `append_evidence.py`, and to every `<automated>` verify leg in the plans.

```
A missing or empty `--jsonl`, a line 1 without the `_schema` header, or a parsed row count
that disagrees with the number of non-header lines in the file, each exit non-zero with a
named `FAIL:` reason. This tool never writes an empty target and exits 0 -- that failure
shape (a gate that discovers/renders nothing and reports success) has already shipped once
in this repo and this tool does not repeat it.
```

### argv recording — absolute paths only

**Source:** `gate_record.py:check_commands` / `_is_rig_tool_invocation`
**Apply to:** every `commands[]` entry `append_evidence.py` emits or merges via `--commands-extra`.

A recorded rig-tool command passes only when argv[0] is an **absolute** interpreter path and
argv[1] is an **absolute** script path containing `/.planning/v1.34/tools/`. `PROCEDURE.md`'s
literal blocks show *relative* paths for readability; the recorded argv must be absolute.
`forbidden_flags` (`--force`, `-f`, `-b`, `--no-blank-check`, `--skip-erase`) are rejected by exact
token match anywhere in a recorded argv, with a narrow `-b` exemption scoped **only** to
`pins.avrdude.binary` as argv0. `append_evidence.py` should re-validate every entry through
`gate_record.check_commands()` **before** the row is written (RESEARCH column 39).

### Constants come from `rig-pins.json` at runtime, never embedded

**Source:** `judge_wrv.py:64-65` + `--pins` default; `rig-pins.json` `hex_span_expected_by_arm`
**Apply to:** `append_evidence.py`'s derivations *and* every `<automated>` verify leg in all three
plans.

Phase 160 recorded a plan-authoring defect that **recurred 4×**: arm-agnostic constants hardcoded
into `<automated>` legs (plans 08/09/10/12). Across 12 positions one wrong constant is twelve false
results. Read `hex_span_expected_by_arm.<arm>` — **never the legacy scalar `hex_span_expected`**,
which equals the v133 value and silently rejects a correct control flash.

---

## No Analog Found

None. Every authored artifact in this phase has a close in-tree analog.

The one item with a *partial* analog: **Amendment 3 clause (a) item 3** (per-position
`--output-dir` / `--reads` / `written.bin` / `wrv_verdict.json` paths) has no precedent, because
every cell that has run so far was a single position. `BRINGUP-wrv`'s flat layout is the shape being
generalised, not copied. The gitignore table above is the evidence the planner needs to pick the
layout.

---

## Metadata

**Analog search scope:** `.planning/v1.34/tools/` (12 files, all inspected by grep; `judge_wrv.py`
read in full), `.planning/v1.34/PROCEDURE.md` (amendment block), `.planning/v1.34/bench/`
(`.gitignore`, `cells/`, `cells/BRINGUP-wrv/` listing).
**Files scanned:** 12 tools + 1 procedure + 1 gitignore + 2 directory listings.
**Live checks run (read-only):** `git check-ignore -v` on five candidate artifact paths. No
hardware command, no flashing, no `firestarter` invocation.
**Pattern extraction date:** 2026-08-27
