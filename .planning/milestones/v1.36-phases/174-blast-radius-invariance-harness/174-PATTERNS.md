# Phase 174: Blast-Radius Invariance Harness - Pattern Map

**Mapped:** 2026-09-03
**Files analyzed:** 10 new (8 in `firestarter_app`, 2 in meta) + 0 modified production files
**Analogs found:** 9 / 10

All analog paths below were verified git-TRACKED (`git ls-files`) in their own repo — the app paths
inside the `firestarter_app` submodule, the meta paths in `/workspaces`. No gitignored mirror path is
named. All line numbers below were re-verified this session against `firestarter_app @ 49bac1a`
(branch `gsd/v1.36-dev-test-fidelity`); every line cited in CONTEXT.md / RESEARCH.md still resolves
except as noted in **Line-number corrections** below.

## Line-number corrections vs upstream citations

| Upstream citation | Verified | Note |
|---|---|---|
| `tests/test_diagnostic_report.py:1377` — frozen literal | **exact** (`:1377` and `:1381`, both `"a0a50436ae3d"`) | the docstring that argues the case starts at `:1360`; the test def is `:1359` |
| `tests/test_diagnostic_report.py:151` — `_minimal_report` | **exact** (`def _minimal_report(` at `:151`) | body runs `:151-198` |
| `tests/test_diagnostic_report.py:1311` — `_coverage_report` | **exact** | body `:1311-1338` |
| `tests/test_chip_test_sdp_leg.py:827` — closure sentinel | **exact** | its enumeration constant `_SHIPPED_OP_STRINGS` is at `:697` |
| `tests/test_erase_flag_invariants.py:280-296` — element-wise pin | **exact**; the pinned constant is `:264-278`, the assertion `:292-295`; a second instance at `:356` | |
| `tests/test_diagnostic_report.py:715` — `test_ladder_state_verdict_mapping` | **exact** | |
| `tools/parse_devtest_issue.py:164` — `count_agreeing` | **exact** | |
| `firestarter/chip_resolver.py:16` — `resolve_chip` | **exact** | |
| `firestarter/diagnostic_report.py` `:186` / `:287` / `:771` | **all exact** (`dedup_fingerprint`, `build_db_diff`, `to_dict`) | |

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `firestarter_app/tests/fixtures/report_shapes.py` | test fixture / builder module | transform (specs → object) | `firestarter_app/tests/test_diagnostic_report.py:151` (`_minimal_report`) + `:1311` (`_coverage_report`) | exact (role+flow) |
| `firestarter_app/tests/fixtures/rekey_ledger.py` | test data module | batch (declarative rows) | `firestarter_app/tests/test_erase_flag_invariants.py:264-278` (pinned module-level constant) | role-match |
| `firestarter_app/tests/fixtures/reports/<shape_id>.json` | test data (committed output snapshot) | file-I/O | no analog — see **No Analog Found** | none |
| `firestarter_app/tests/fixtures/devtest_issue_corpus.json` | test data (committed artifact) | file-I/O | no analog — see **No Analog Found** | none |
| `firestarter_app/tests/fixtures/part_number_delta.json` | generated committed artifact | file-I/O | committed-output side of `tools/gen_sdp_bus_config.py` → `tests/test_sdp_bus_config_drift.py` | partial (flow-match) |
| `firestarter_app/tests/fixtures/planted_rekey_mutation.py` | test fixture (counter-example) | transform | `firestarter_app/tests/fixtures/planted_diagnostic_report_claim.py` | exact |
| `firestarter_app/tests/test_blast_radius_invariance.py` | test | request-response (pure fn assert) | `firestarter_app/tests/test_diagnostic_report.py:1359-1381` + `tests/test_erase_flag_invariants.py:280-296` | exact |
| `firestarter_app/tests/test_rekey_ledger.py` | test | batch (row sweep) | `firestarter_app/tests/test_chip_test_sdp_leg.py:827` (closure sentinel) | role-match |
| `firestarter_app/tests/test_part_number_delta_drift.py` | test | file-I/O + subprocess | `firestarter_app/tests/test_sdp_bus_config_drift.py` | exact |
| `firestarter_app/tools/measure_part_number_delta.py` | CLI script / generator | transform → file-I/O | `firestarter_app/tools/gen_sdp_bus_config.py` | exact |
| `/workspaces/tools/rekey/check_rekey_ledger.py` | CLI checker (cross-tree) | file-I/O + validate | `/workspaces/tools/catalog/codegen.py` (`--check` shape) + `firestarter_app/tools/check_diagnostic_report_claims.py` (env-override seam) | role-match |
| `/workspaces/.planning/MILESTONES.md` (new re-key ledger section) | doc | — | `.planning/MILESTONES.md:361-400` (v1.33 §"Post-Close Correction") | exact |
| `/workspaces/.github/workflows/rekey-ledger-check.yml` (optional, D-13 CI leg) | config | event-driven | `.github/workflows/catalog-sync-check.yml` | role-match, **triggers must NOT be copied** |

## Pattern Assignments

### `firestarter_app/tests/fixtures/report_shapes.py` (fixture/builder, transform)

**Analog:** `firestarter_app/tests/test_diagnostic_report.py` — `_minimal_report` (`:151-198`) and
`_coverage_report` (`:1311-1338`). Generalize these; do not design fresh (RESEARCH §Don't Hand-Roll).

**Builder signature + step_specs contract** (`:151-166`):
```python
def _minimal_report(
    *,
    chip: str = "M8720",
    protocol: str = "0x08",
    host_version: str = "3.0.0b10",
    step_specs: list[tuple[str, str, str | None, str]] | None = None,
    vpp_before_mv: int | None = None,
    vpe_before_mv: int | None = None,
):
    """Directly-constructed DiagnosticReport (no derive_plan/run_plan) for
    precise dedup_fingerprint test control over step shape.

    `step_specs` is a list of `(op, verdict, fingerprint_classification,
    reason)` tuples; `fingerprint_classification=None` means no Fingerprint
    is attached (the non-destructive/graceful-degradation shape)."""
```

**Core construction pattern — the `cls is None` fork and the object assembly** (`:172-198`):
```python
    results = []
    for op, verdict, cls, reason in step_specs:
        fp = (
            Fingerprint(total=10, bad=0, bad_pct=0.0, classification=cls)
            if cls is not None
            else None
        )
        results.append(
            StepResult(op=op, verdict=verdict, reason=reason, fingerprint=fp)
        )

    auto_capture = AutoCapture(
        host_version=host_version,
        chip=chip,
        protocol=protocol,
    )
    return DiagnosticReport(
        auto_capture=auto_capture,
        transport=TransportHealth(),
        plan=Plan(name=chip),
        results=results,
        vpp_before_mv=vpp_before_mv,
        vpe_before_mv=vpe_before_mv,
    )
```

**Local imports inside the function** — note the analog imports `AutoCapture`/`DiagnosticReport`/
`TransportHealth` *inside* the builder (`:165-169`), not at module top. This is the house style in that
file and keeps import cost off collection. The new fixture module is imported by seven later phases
(D-03), so module-top imports are acceptable there, but the `from firestarter.diagnostic_report import
dedup_fingerprint` deferred-import idiom is used consistently at every assertion site
(`:1373`, `:1355`) and should be preserved in the test modules.

**Post-construction stamping seam** (`_coverage_report`, `:1336-1337`) — the sanctioned way to set a
field production sets deeper in the stack:
```python
    report.results[0].write_target = target
    return report
```
Its docstring (`:1312-1326`) states *why* direct construction rather than `derive_plan`/`run_plan` is
legitimate for a shape production cannot currently produce for one chip — reuse that argument verbatim
for the hand-specified table (D-02 table 1) and for the synthetic arm-4 shape.

**Real-path (D-02 table 2) construction:** mirror `firestarter/cli_handlers.py:2374-2431`, the sole
production construction site — `chip=<raw CLI token>`, `protocol=str(prog["algorithm"])`. RESEARCH
§"Building a shape end to end" reproduces the exact call sequence.

**Shared DB instance** — copy `tests/test_erase_flag_invariants.py:96-98`:
```python
# One shared, real, on-disk database instance -- no ~/.firestarter override,
# no serial, deterministic across developer machines.
_REAL_DB = EpromDatabase(skip_local_override=True)
```
(Comments are illustrative of the analog only — the project HARD RULE forbids writing new `#` comments;
put this reasoning in a docstring.)

---

### `firestarter_app/tests/test_blast_radius_invariance.py` (test, absolute-value assert)

**Analog A — the frozen-literal precedent:** `tests/test_diagnostic_report.py:1359-1381`.

**Docstring pattern that licenses the absolute assertion** (`:1360-1371`) — reusable argument, adapt the
noun:
```python
    """THE most important test in this group -- a GATE, not a claim.

    `coverage_tag` returns `""` for a slot/fixed run and `dedup_fingerprint`
    appends it only when non-empty ...
    Pinning the literal hash -- rather than merely asserting
    `uv-slot` and `fixed` agree with each other -- means a future change
    that starts tagging the default (untagged) case fails loudly HERE,
    instead of silently re-keying every historical `count_agreeing` group
    a maintainer has already promoted a chip through.
    """
```

**Assertion form** (`:1373-1381`):
```python
    from firestarter.diagnostic_report import dedup_fingerprint

    slot_report = _coverage_report(REGION_POLICY_UV_SLOT)
    fixed_report = _coverage_report(REGION_POLICY_FIXED)

    assert dedup_fingerprint(slot_report) == "a0a50436ae3d"
    assert dedup_fingerprint(fixed_report) == "a0a50436ae3d"
```
Generalize to `@pytest.mark.parametrize("shape_id,expected", sorted(FROZEN_HASHES.items()))` per
RESEARCH Pattern 1, keeping the failure message that names the D-11 separate-commit rule.

**Analog B — element-wise committed list pin (D-07 top-level/sub-object key lists, D-10 shape_id set):**
`tests/test_erase_flag_invariants.py:264-296`.

Pinned constant, one element per line, with a provenance docstring rather than a comment
(`:264-278`):
```python
_AT28C256_FULL_EXPECTED_OP_ORDER = [
    OP_ID,
    OP_READ,
    OP_WRITE,
    OP_VERIFY,
    OP_ERASE,
    OP_BLANK_CHECK,
    OP_WRITE_BASELINE_B,
    OP_WRITE_BASELINE_A,
    OP_SDP_LOCK,
    OP_WRITE_INHIBITED,
    OP_SDP_UNLOCK,
    OP_WRITE_RESTORED,
]
```

List-equality assertion with a drift-naming message (`:290-295`) — this is the exact idiom D-07 and
D-10 both use; a membership/subset check would let D-10's "quietly widen the oracle" through:
```python
    plan = derive_plan(_AT28C256_CHIP_NAME, _REAL_DB, write_scope="full")
    ops = [step.op for step in plan.steps]

    assert ops == _AT28C256_FULL_EXPECTED_OP_ORDER, (
        f"AT28C256 write_scope='full' op order drifted from the pinned "
        f"shape; expected {_AT28C256_FULL_EXPECTED_OP_ORDER}, got {ops}"
    )
```
Apply as `sorted(report.to_dict())` vs a committed list, and per sub-object (`voltage`, `banner`,
`auto_capture`, `transport_health`, `steps[0]`) — RESEARCH §"Schema pins available for D-07" has the
measured key lists.

**Anti-vacuity discipline the module docstring must carry** — `tests/test_erase_flag_invariants.py:1-68`
is the model. Two reusable structural elements:
1. An **"Anti-vacuity rule, stated up front"** block naming the specific way a lazy selector passes
   vacuously (`:11-23`).
2. A **"Reachability"** block that transcribes the observed RED per leg (`:64-68`, pointing at
   `153-12-SUMMARY.md`). Phase 174's summary must carry the same transcription.

**Error-handling / no-exception pattern:** these are pure-function gates. There is no try/except
anywhere in the analogs — assertions with `f`-string diagnostics are the whole error surface. Do not
introduce exception handling.

---

### `firestarter_app/tests/test_rekey_ledger.py` (test, row sweep + closure)

**Analog:** `tests/test_chip_test_sdp_leg.py:827-871` (`test_shipped_ops_never_reach_sdp_arm`) — the
closure-sentinel idiom D-10 needs.

**The closure pattern — derive the expected set from the module's own declarations so an added member
cannot escape by omission** (`:860-871`):
```python
    import firestarter.chip_test as chip_test_mod

    module_op_constants = {
        value
        for name, value in vars(chip_test_mod).items()
        if name.startswith("OP_") and isinstance(value, str)
    }
    shipped_op_set = module_op_constants - _SDP_OPS - _SDP_LEG_OPS
    assert set(_SHIPPED_OP_STRINGS) == shipped_op_set, (
        f"_SHIPPED_OP_STRINGS {sorted(_SHIPPED_OP_STRINGS)} does not equal "
        f"the module's shipped op set {sorted(shipped_op_set)} (all OP_* "
        "constants minus _SDP_OPS and minus _SDP_LEG_OPS) -- a shipped op "
        "was added to chip_test.py without extending this sentinel's "
        "enumeration (133-CONTEXT.md D-13b)"
    )
```
Map directly onto RESEARCH Pattern 5: assert `set(FROZEN_HASHES) == set(SHAPE_IDS) ==
{p.stem for p in reports_dir.glob("*.json")}` three ways, with the explicit committed sorted list as
the fourth anchor.

**Its explicit enumeration constant** lives at `:697` (`_SHIPPED_OP_STRINGS = [...]`) — the pattern is
*both* an explicit hand-written list *and* a derived-set equality against it. Copy both halves; either
alone is escapable.

**Docstring pattern worth copying** (`:828-856`): it names what would go wrong, and records that the
RED **was seen** ("this was SEEN to happen: see 133-03-SUMMARY.md's recorded mutation proof").

**Append-only assertion (D-09)** — no in-tree analog for the `after_hash or before_hash` fork; use
RESEARCH Pattern 3 as authored, wrapped in the list-equality message style above.

---

### `firestarter_app/tests/fixtures/planted_rekey_mutation.py` (fixture, counter-example)

**Analog:** `firestarter_app/tests/fixtures/planted_diagnostic_report_claim.py` (23 lines, whole file
read).

**Shape of every `planted_*` fixture in that directory** (all 20 verified by `ls`): a standalone,
**never-imported** module whose docstring states (a) which checker it feeds, (b) that it is
deliberately violating, (c) which named requirement/plan authored it, (d) the seam it is injected
through, and (e) that it must never be imported:
```python
"""Test fixture for check_diagnostic_report_claims.py -- NOT wired into any
CLI surface, never imported by production code.

Deliberately-violating fixture (CLOSE-03, v1.30 Phase 137 plan 137-02): a
small, standalone, syntactically-valid Python module -- NOT a copy of the
real `diagnostic_report.py` -- containing exactly one string literal that
trips the `dev-test-proves-unqualified` forbidden-phrase label. This file
must never be imported; it exists only as AST-scan input for the paired
pytest (`tests/test_check_diagnostic_report_claims.py`), injected via the
`FIRESTARTER_DIAGREPORT_SRC` env-override seam -- a real subprocess-level
planted violation, not an in-process synthetic.
"""
```

**How planted fixtures are consumed** — `tests/test_check_diagnostic_report_claims.py:73-84`, resolved
from `_FA_DIR = Path(__file__).parent.parent` (`:33`) and fed through a subprocess env override:
```python
def test_planted_violation_flips_checker_to_failure() -> None:
    """FIRESTARTER_DIAGREPORT_SRC pointed at the committed planted-violation
    fixture MUST flip the gate to a non-zero exit, naming the
    `dev-test-proves-unqualified` label in its FAIL: summary."""
    fixture = _FA_DIR / "tests" / "fixtures" / "planted_diagnostic_report_claim.py"
    result = _run_checker({"FIRESTARTER_DIAGREPORT_SRC": str(fixture)})
    assert result.returncode != 0, (
        f"checker exited 0 on a planted diagnostic_report.py-shaped claim "
        f"violation.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "FAIL:" in result.stdout
    assert "dev-test-proves-unqualified" in result.stdout
```

**The paired positive leg that proves the gate is not always-red** (`:52-66`) — copy this too, it is
half the anti-vacuity contract:
```python
    """python tools/check_diagnostic_report_claims.py must exit 0 on the
    real, clean `diagnostic_report.py` source -- proving the gate is not
    accidentally always-red."""
```

**Important divergence for this phase:** the env-override/subprocess seam fits the *meta-side checker*
(D-13) exactly. For the **in-process hash gate** the analogue is a builder-level mutation
(RESEARCH Pattern 4) — `report.results[2].fingerprint = None` then assert `!=` the frozen value.
Use the subprocess-fixture shape for `check_rekey_ledger.py`, the in-process shape for
`test_blast_radius_invariance.py`; do not force one onto the other.

---

### `firestarter_app/tools/measure_part_number_delta.py` (script, generator)

**Analog:** `firestarter_app/tools/gen_sdp_bus_config.py` (424 lines; targeted reads at `:1-36`,
`:343-424`). This is the shipped "script generates a committed artifact, test asserts no drift"
pattern, and it is repo-owned — satisfying D-16 and the standing "skills must own their scripts" rule.

**Module docstring contract block** (`:1-35`) — states the five properties the drift test then enforces:
```
Mirrors the established `tools/gen_validation_header.py` shape:
  - Validate-first: validate_rows() raises ValueError on any derivation
    violation BEFORE emission (T-116-02-STALE mitigation).
  - Deterministic: fixed chip order, no timestamps, LF endings.
  - Banner: DO NOT EDIT with re-run instructions.
  - Path.write_text(encoding="utf-8", newline="\n") for byte-identical output.

Exit codes:
  0 -- derivation valid, header emitted successfully (or --check found no drift)
  1 -- derived rows failed validation ...
```
It also records the load-bearing rule this phase's script needs verbatim: *"this generator's derivation
is the HOST'S OWN LIVE CODE PATH — it imports `EpromDatabase` ... It never reimplements
`convert_to_programmer` — a reimplementation is a second thing that can be wrong."* That is exactly
D-15's argument for going through `chip_resolver.resolve_chip`.

**Argparse seams — `--target`, an input override, and `--check`** (`:343-380`):
```python
    p.add_argument(
        "--target",
        type=Path,
        default=_TARGET_DEFAULT,
        help="Output path for the generated header ...",
    )
    p.add_argument(
        "--pinouts",
        type=Path,
        default=_PINOUTS_DEFAULT,
        help=(
            "Path to pinouts.json to derive from (default: the real ...). "
            "Fails closed when the given path is missing -- never silently "
            "falls back to the real file."
        ),
    )
    p.add_argument(
        "--check",
        action="store_true",
        help=(
            "Derive, validate, render, and compare against the existing "
            "--target file. Print a diff summary and return non-zero on "
            "mismatch without writing."
        ),
    )
```

**`main()` — validate-before-emit, `--check` drift mode, exit-code discipline** (`:383-421`):
```python
def main() -> int:
    """Entry point. Returns 0/1/2 for ok/validation-fail/chip-or-pinout-not-found."""
    args = _build_argparser().parse_args()

    try:
        rows = derive_rows(args.pinouts)
    except DerivationError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    try:
        validate_rows(rows)
    except ValueError as e:
        print(f"ERROR: derivation validation failed: {e}", file=sys.stderr)
        return 1

    output = emit_cpp_header(rows)

    if args.check:
        if not args.target.is_file():
            print(f"DRIFT: target does not exist: {args.target}", file=sys.stderr)
            return 1
        existing = args.target.read_text(encoding="utf-8")
        if existing != output:
            print(
                f"DRIFT: {args.target} differs from a fresh regeneration "
                f"({len(existing)} bytes committed vs {len(output)} bytes "
                f"regenerated)",
                file=sys.stderr,
            )
            return 1
        print(f"OK: {args.target} matches a fresh regeneration")
        return 0

    args.target.parent.mkdir(parents=True, exist_ok=True)
    args.target.write_text(output, encoding="utf-8", newline="\n")
    print(f"OK: wrote {args.target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```
Note `mkdir(parents=True, exist_ok=True)` before write, `newline="\n"`, and the fail-closed
`target does not exist` arm. For a JSON artifact, render with
`json.dumps(obj, indent=2, sort_keys=True) + "\n"` to preserve the byte-identical property; the
"no timestamps" rule is mandatory or the drift test self-reddens.

**Measurement path (D-15) — the mechanical detail that breaks a naive implementation:** `resolve_chip`
(`firestarter/chip_resolver.py:16-45`) returns `convert_to_programmer(...)`, whose keys are hyphenated
and which **does not contain `part_number`**. Read `part_number` from
`db.get_eprom_config(token)`'s raw config; call `resolve_chip` for the support-status verdict.
`resolve_chip`'s own docstring documents the DI seam this script must use:
```
    The ``db`` parameter is a dependency-injection seam: tests pass
    ``EpromDatabase(skip_local_override=True)`` so no ``~/.firestarter`` overrides
    or serial I/O are involved.
```

---

### `firestarter_app/tests/test_part_number_delta_drift.py` (test, drift)

**Analog:** `firestarter_app/tests/test_sdp_bus_config_drift.py` (164 lines, whole file read). Four-leg
structure to copy leg-for-leg.

**Module docstring naming the failure modes it catches** (`:1-11`):
```python
"""
Drift gate test for the SDP bus_config codegen (TRACE-02 / D-10 / D-11 /
T-116-02-EDIT / T-116-02-HOLLOW).

Asserts that re-running gen_sdp_bus_config.py produces a byte-identical copy
of the committed sdp_bus_config.h. Fails if pinouts.json is edited (or the
committed header hand-edited) without regenerating the header.
"""
```

**Path resolution + imports** (`:13-23`):
```python
import json
import subprocess
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).parent.parent.parent
_APP_DIR = _REPO_ROOT / "firestarter_app"
_GEN_SCRIPT = _APP_DIR / "tools" / "gen_sdp_bus_config.py"
```
**Adapt, do not copy verbatim:** the analog's `_REPO_ROOT`/`_APP_DIR` two-level climb and its
`fw_path`/`requires_fw` skip markers exist because the *committed artifact lives in the sibling firmware
repo*. This phase's artifact lives inside `firestarter_app/tests/fixtures/`, so use
`Path(__file__).parent` and **no skip marker at all** — a `requires_fw`-style skip here would be exactly
the fail-open gate the phase exists to prevent. Its own docstring (`:24-31`) warns about the same-repo
look-alike trap.

**Leg 1 — the artifact exists, with the regeneration command in the message** (`:42-49`):
```python
def test_committed_header_exists() -> None:
    """The committed header must exist in the firestarter submodule."""
    assert _COMMITTED_HEADER.exists(), (
        f"sdp_bus_config.h not found: {_COMMITTED_HEADER}\n"
        "Run: cd firestarter_app && python tools/gen_sdp_bus_config.py"
    )
```

**Leg 2 — the DO-NOT-EDIT banner** (`:52-58`). For a JSON artifact the equivalent is a
`"_generated_by"` key asserted absolutely, not a comment (JSON has none).

**Leg 3 — byte-identical regeneration into a tempfile** (`:61-98`):
```python
def test_codegen_produces_byte_identical_output() -> None:
    """Re-running the codegen must produce a byte-identical header (drift gate).

    This test fails when:
    - pinouts.json is edited but gen_sdp_bus_config.py is not re-run.
    - gen_sdp_bus_config.py emitter logic changes but the committed header is stale.
    - the committed header was hand-edited (T-116-02-EDIT).
    """
    with tempfile.NamedTemporaryFile(suffix=".h", delete=False) as tmp:
        tmp_path = Path(tmp.name)

    try:
        result = subprocess.run(
            [sys.executable, str(_GEN_SCRIPT), "--target", str(tmp_path)],
            capture_output=True,
            text=True,
            cwd=str(_APP_DIR),
        )
        assert result.returncode == 0, (
            f"gen_sdp_bus_config.py failed (exit {result.returncode}):\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        regenerated = tmp_path.read_bytes()
        committed = _COMMITTED_HEADER.read_bytes()
        assert regenerated == committed, (
            "sdp_bus_config.h is STALE -- re-run to update:\n"
            "  cd firestarter_app && python tools/gen_sdp_bus_config.py\n"
            f"\nRegenerated output ({len(regenerated)} bytes) differs from "
            f"committed header ({len(committed)} bytes).\n"
        )
    finally:
        tmp_path.unlink(missing_ok=True)
```

**Leg 4 — non-vacuity: planted bad input must fail closed AND write nothing** (`:101-163`). The whole
leg is the model; the load-bearing moves are the fixture-assumption guard, the deep copy, the deleted
target file, and the two assertions:
```python
    assert real_pinouts["DIP28_28C256"]["pins"]["rw-pin"] == [27], (
        "test fixture assumption stale -- DIP28_28C256 rw-pin is no longer [27]; "
        "update this planted-fault value"
    )
    broken_pinouts = json.loads(json.dumps(real_pinouts))  # deep copy
    broken_pinouts["DIP28_28C256"]["pins"]["rw-pin"] = [21]
    ...
        tmp_out.unlink()   # remove so we can detect if codegen writes to it
    ...
        assert result.returncode == 1, (...)
        assert not tmp_out.exists(), (
            "Script wrote output even though derivation was invalid "
            "(must validate before emission)"
        )
    finally:
        bad_pinouts_path.unlink(missing_ok=True)
        tmp_out.unlink(missing_ok=True)
```
Its docstring also records that this leg **runs unconditionally, with no skip marker**, because it never
touches the committed artifact — carry that reasoning.

---

### `firestarter_app/tests/fixtures/rekey_ledger.py` (test data, batch)

**Analog:** the pinned-constant half of `tests/test_erase_flag_invariants.py:264-278` (excerpted above),
plus the enumeration constant at `tests/test_chip_test_sdp_leg.py:697`.

There is **no dataclass-row ledger in the tree**. Nearest structural precedent for a declarative row
table with provenance is `/workspaces/tools/catalog/messages.toml` (data file + `--check` validator),
but its format is TOML and its validator is codegen. Author the four-tuple rows as a module-level
`tuple[Row, ...]` of a frozen `dataclass`, one row per line, each with a docstring-level provenance
note naming its owning phase and the *mechanism* of the re-key (RESEARCH C3: the UV row's mechanism is
the `blank-check` verdict triple, **not** `repeat_policy_tag`).

---

### `/workspaces/tools/rekey/check_rekey_ledger.py` (meta checker, cross-tree)

**Analog A (structure, `--check` + exit codes):** `/workspaces/tools/catalog/codegen.py:1-40`. It is the
only tracked meta-side Python script (`git ls-files tools/` returns exactly `tools/catalog/codegen.py`,
`tools/catalog/messages.toml`, `tools/catalog/sync_to_subrepos.sh`, `.planning/v1.35/MIGRATION-TABLE.md`).

Its docstring's two reusable contract blocks:
```
Determinism contract (LCAT-05): two consecutive runs against the same catalog
file produce byte-identical output. Achieved by:
  - sorting messages by id ascending before emission
  - no timestamps, hostnames, or hashes in the banner
  ...
Validation (LCAT-02 + LCI-04): the --check flag runs the full 10-rule catalog
validator and exits 1 on any violation. Validation also runs unconditionally
before emission, so an invalid catalog never produces output.

Stdlib only (Python 3.11+ for tomllib).
```
Stdlib-only + `argparse` + `sys.exit(main())` is the house shape for both repos' scripts.

**Analog B (the injectable-path seam that makes the planted RED possible):**
`firestarter_app/tools/check_diagnostic_report_claims.py`'s `FIRESTARTER_DIAGREPORT_SRC` env override,
consumed as shown in the planted-fixture section above. The meta checker needs the same:
overridable paths for **both** `MILESTONES.md` and the app-side ledger module, so a hand-broken copy
can be fed to it and the RED **seen**, without touching the real files.

**Fail-closed requirement, with a shipped precedent to copy:**
`firestarter_app/tests/test_check_diagnostic_report_claims.py:92-100`:
```python
def test_fail_closed_on_nonexistent_target(tmp_path: Path) -> None:
    """Pointing the scan target at a nonexistent path MUST fail closed (exit
    non-zero), never vacuously pass with a target silently skipped."""
    missing = tmp_path / "does_not_exist.py"
    result = _run_checker({"FIRESTARTER_DIAGREPORT_SRC": str(missing)})
    assert result.returncode != 0
    assert "not found" in result.stdout
```
This is directly relevant: project memory records `check_permitted_claims.py` resolving `_HERE` to the
*checker's* directory, scanning nothing and exiting 0. Resolve paths from an explicit repo root, not
from `__file__`'s parent, and assert the ledger module was actually found and parsed.

**Reading the app ledger from meta:** do **not** import the app module (cross-tree import + the
"skills must own their scripts" rule). Parse it with `ast` — the same technique
`check_diagnostic_report_claims.py` uses on `diagnostic_report.py`. That also means the ledger row
format must be `ast.literal_eval`-able (plain tuples/strings/`None`), which is a constraint on
`rekey_ledger.py`'s authoring.

---

### `/workspaces/.github/workflows/rekey-ledger-check.yml` (config, event-driven) — optional CI leg

**Analog:** `/workspaces/.github/workflows/catalog-sync-check.yml` — the **only** registered meta
workflow (verified by `ls .github/workflows/`).

**Copy the cross-tree checkout shape** (`:20-36`) — checkout meta to a subdirectory, then check the
sub-repo out explicitly at a resolved ref rather than relying on `submodules: recursive`. The workflow's
own comments record why:
```yaml
      # No `submodules: recursive` here: this job reads only
      # `meta/tools/catalog/messages.toml`, and it checks the sub-repos out
      # explicitly below at the ref it actually wants to compare. Fetching them
      # again as submodules was pure duplicate work -- and it re-armed a whole
      # failure class ... an accidentally committed gitlink at
      # `.planning/v1.7/upstream-rurp` with no `.gitmodules` entry made the
      # checkout die with `fatal: No url found for submodule path` before any
      # assertion ran.
      - name: Check out meta-repo
        uses: actions/checkout@v4
        with:
          path: meta
```

**Do NOT copy its triggers** (`:2-16`):
```yaml
on:
  push:
    branches:
    - main
    paths:
    - 'tools/catalog/**'
```
`branches: [main]` would make the checker fire zero times this milestone (`git.base_branch` is `beta`;
work happens on `gsd/v1.36-*`) — the documented `wiki-check.yml` fail-open shape. Use `beta` +
`gsd/**`, paths `.planning/MILESTONES.md` + `tools/rekey/**` + the app gitlink + the workflow's own
file. Also note the analog's own comment block (`:38-45`) documents that it "had never once succeeded
(5 runs, 5 failures)" — a red run there is not evidence a new leg fired.

---

### `/workspaces/.planning/MILESTONES.md` (doc) — GATE-06 re-key ledger section

**Analog:** `.planning/MILESTONES.md:361-400`, §"Post-Close Correction: The Sweep's Oracle Was Blind
(2026-08-24)" — the house precedent for recording a measurement that falsified a prior claim, which is
exactly what RESEARCH C2/C3 require this section to do.

**Structure to copy, in order:**
1. `### <Title> (YYYY-MM-DD)` heading with the date inline.
2. A bolded one-line finding attribution — `**Found by the operator, after close, by reading the code**`.
3. A bolded framing line separating instrument from procedure —
   `**The instrument, not the procedure.**`
4. The falsified artifact quoted literally (there, the regex; here, the three non-reproducing hashes).
5. **A before/after measurement table** — the load-bearing element:

```markdown
| Measurement | Old gate | Corrected |
|---|---|---|
| Hit lines, shipped source (both repos) | **43** | **1,174** |
| Hit lines, whole corpus | 198 | 4,214 |
| `D-#` in `firestarter/{src,include}` | 4 across 1 file | **87 across 21 files** |
```
6. A bolded statement of what the old number *actually* measured —
   `**SWEEP-03's headline evidence was an artifact of where the regex anchored.**`
7. `**What was done about it.**` — the remediation, ending with the reproducibility escape hatch
   (`--legacy-anchored` reproduces the historical figure exactly, "so every number already recorded in
   `.planning/` stays reproducible") and the RED-first note ("got its first **21 tests**, proven RED
   first").

The milestone-section format itself (for the v1.36 header, when close comes) is
`.planning/MILESTONES.md:3-30` (v1.35): `## vX.YZ <Name> (Shipped: date)` then bolded label lines
(`**Phases completed:**`, `**Requirements:**`, `**Code:**`, `**Close posture:**`), then `**Delivered:**`
prose, `**Key accomplishments:**` numbered list, `### Known Gaps`.

## Shared Patterns

### Anti-vacuity (applies to EVERY new test file)
**Sources:** `firestarter_app/tests/test_erase_flag_invariants.py:1-68` (module-docstring
anti-vacuity + Reachability blocks), `tests/test_sdp_bus_config_drift.py:101-124` (planted-input leg),
`tests/test_check_diagnostic_report_claims.py:52-100` (clean-passes + planted-fails + fail-closed trio).
**Apply to:** all four new app test modules and the meta checker.

Every gate in this phase needs *three* legs, which is what the three sources jointly establish:
```
1. clean input passes            (proves not always-red)
2. planted mutation fails        (proves not vacuous)  <- must be SEEN, transcribed in the SUMMARY
3. missing/unparsable input fails (proves fail-closed, not silently-skipped)
```

### Deterministic-DB access
**Source:** `firestarter_app/tests/test_erase_flag_invariants.py:96-98`
**Apply to:** every fixture, test and script that touches the database.
```python
_REAL_DB = EpromDatabase(skip_local_override=True)
```
Non-negotiable: without `skip_local_override=True` a developer's `~/.firestarter/database.json` can
change a frozen hash. `resolve_chip`'s docstring names this as its DI seam.

### Two-level DB descent
**Source:** `firestarter_app/tests/test_erase_flag_invariants.py:108-131` (`_select_algorithm_13_rows`,
`_all_rows`)
**Apply to:** the GATE-04 whole-DB aggregate script.
```python
    for manufacturer, chips in db.proms.items():
        for chip in chips:
            ...
```
`db.proms` is `{manufacturer: [chip_record, ...]}`. A top-level scan iterates manufacturer *keys* and
every downstream assertion passes vacuously — the module docstring (`:11-23`) states this as a rule.
Rows are keyed by `part_number`; there is **no** `name` key in the raw `proms` structure.

### Deferred production imports at assertion sites
**Source:** `firestarter_app/tests/test_diagnostic_report.py:1373`, `:721-727`, `:165-169`
**Apply to:** all new test modules.
```python
    from firestarter.diagnostic_report import dedup_fingerprint
```
Consistent house style in the analog file; also how the ladder test imports the private
`_LADDER_*` constants.

### Constants-not-literals for anything already exported
**Source:** `firestarter_app/tests/test_diagnostic_report.py:734-747`
```python
    assert diff_bad.ladder_state == _LADDER_COMMUNITY_FAIL == "community-fail"
```
The triple-equality idiom: assert against the imported constant *and* the literal in one expression, so
a constant rename and a value change are both caught. Note RESEARCH C8 — this test already pins all four
`ladder_state` values; GATE-03's genuinely new work is the `proposed_disposition` **text** and the
`shape_id` binding. Use the same triple-equality form against the `_DISPOSITION_*` constants and do not
duplicate the ladder-tag assertions.

### No comments, docstrings only
**Source:** project HARD RULE (user-global memory, broadened 2026-08-29); house style throughout the
analogs — `test_erase_flag_invariants.py`'s 68-line module docstring carries all reasoning.
**Apply to:** every new file. The excerpts above that contain `#` comments are quotations of existing
code, not templates. A plan cannot override this rule.

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `firestarter_app/tests/fixtures/reports/<shape_id>.json` | test data (committed `to_dict()` snapshot) | file-I/O | GATE-05's premise, re-verified: `tests/fixtures/` holds 23 entries, all `planted_*` / `synthetic_*` / `fake_firestarter`, and **zero report JSON**. The nearest thing is the schema-1.2 frozen fixtures RESEARCH marks as deprecated (placeholder tokens `deadnu11id00` etc.) — they prove parsing, not hash continuity, and must not be modelled on. Structure comes from RESEARCH §"Schema pins available for D-07" (the measured `to_dict()` key lists), not from an analog. |
| `firestarter_app/tests/fixtures/devtest_issue_corpus.json` | test data (26 `(issue, chip, 12-hex, part_number)` rows) | file-I/O | No committed GitHub-issue corpus exists. `tools/parse_devtest_issue.py:164-184` (`count_agreeing`) is the *consumer* idiom — it groups on the **embedded** hash and never re-hashes — but there is no shipped artifact of this shape to copy. Enumerate by the `[dev test]` title prefix, not the `dev-test` label (RESEARCH: label covers 15 of 26), and note C1: **26** rows, not 27. |
| `firestarter_app/tests/fixtures/rekey_ledger.py` | test data (four-tuple rows) | batch | Partial only — see its section. No dataclass-row ledger with a declared/undeclared fork exists in either tree; RESEARCH Pattern 3 is the authored design. |

## Metadata

**Analog search scope:** `firestarter_app/tests/`, `firestarter_app/tests/fixtures/`,
`firestarter_app/tools/`, `firestarter_app/firestarter/`, `/workspaces/tools/`,
`/workspaces/.github/workflows/`, `/workspaces/.planning/MILESTONES.md`
**Files scanned:** 18 `firestarter_app/tools/*.py` enumerated, 23 `tests/fixtures/` entries enumerated,
4 meta tracked `tools/` entries, 1 meta workflow; 11 files read (targeted ranges).
**Grep discipline:** all evidence greps run via `/usr/bin/grep`, never the devcontainer's ugrep shim.
**Tracked-source gate:** all 12 analog paths confirmed via `git ls-files` in their owning repo
(app paths inside the submodule, meta paths at `/workspaces`). Zero gitignored-mirror paths emitted.
**Pattern extraction date:** 2026-09-03
