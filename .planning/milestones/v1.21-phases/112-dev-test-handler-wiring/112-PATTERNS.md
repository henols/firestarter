# Phase 112: `dev test` Handler Wiring - Pattern Map

**Mapped:** 2026-07-03
**Files analyzed:** 4 (1 new handler, 2 modified, 1 new test module)
**Analogs found:** 4 / 4 (all exact or role-match)

> Path note (meta-repo): every path below is under **`firestarter_app/`** on
> disk. CONTEXT.md writes `firestarter/…` as package shorthand; the top-level
> `firestarter/` dir is C++ firmware and is NOT in scope. No RESEARCH.md — pure
> integration phase (glue over existing 108-111 building blocks).

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| NEW `@dev.command("test")` handler in `firestarter_app/firestarter/cli_handlers.py` | controller (CLI orchestrator) | request-response (prompt→sweep→render→exit) | `dev_validate_family` (`cli_handlers.py:1474`) + `_write_artifact` (`:1373`) | exact |
| MODIFY `firestarter_app/firestarter/chip_test.py` `run_plan` (add `sampler`) | service (test engine) | batch (multi-step sweep) | `run_plan` itself (`:501`) + `_dispatch_multi_run` (`:783`) | self (in-place extension) |
| MODIFY `firestarter_app/tools/check_devtest_orchestrator.py` (+ paired pytest) | config (AST gate) | transform (AST walk) | `check_devtest_orchestrator.py` itself + `main()` (`:231`) | self (extend scan targets) |
| NEW handler unit tests in `firestarter_app/tests/` | test | request-response | `dev validate-family` test seam + `test_check_devtest_orchestrator.py` | role-match |

---

## Pattern Assignments

### NEW `@dev.command("test")` handler — `firestarter_app/firestarter/cli_handlers.py`

**Analog:** `dev_validate_family` (`cli_handlers.py:1450-1624`) — its conceptual twin.

**Decorator + signature pattern** (`cli_handlers.py:1450-1481`) — copy verbatim, adapt args:
```python
@dev.command(name="validate-family")
@click.argument("family", type=click.Choice([...]))
@click.option("--output-dir", "output_dir", type=str, default=None,
              help="Output directory for results artifact ...")
@click.pass_obj
@map_typed_errors
def dev_validate_family(app: AppContext, family: str, ..., output_dir: Optional[str]) -> None:
```
Adaptation for `dev test`:
- positional `chip` arg (use `_complete_eprom` shell-completion, see `cli_handlers.py:96`).
- `@click.option("--destructive", is_flag=True, ...)` — flag-only, CLI-only (D-02, SAFE-01: never from config/env).
- `@click.option("--output-dir", "output_dir", default=None)` — **default `None`, NOT `"."`** (D-05: no files unless given; the opposite of validate-family's default-cwd behavior).
- `-y/--yes` flag (D-03; naming is planner's call). Keep `@click.pass_obj` + `@map_typed_errors`.

**3-way `sys.exit` (verdict-int) pattern** (`cli_handlers.py:1620-1624`):
```python
if verdict_int > overall_verdict:
    overall_verdict = verdict_int
_write_artifact(hw_cells, output_dir)
sys.exit(overall_verdict)
```
Adaptation (D-01): compute exit as **`max` over per-verdict codes** — `1` if any `BAD` in `{r.verdict for r in results}` (BAD beats marginal), else `2` if any `marginal`/indeterminate, else `0`. Chip-ID mismatch surfaces as a `BAD` id step (`chip_test.py:724`) → naturally maps to `1`. N<M non-destructive clean run → `0`.

**Dual-artifact write pattern** (`cli_handlers.py:1371-1418` `_write_artifact`/`_render_markdown`):
```python
out_path = Path(output_dir) if output_dir else Path(".")
out_path.mkdir(parents=True, exist_ok=True)
json_file = out_path / "validation-matrix.json"
json_file.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
md_file = out_path / "validation-matrix.md"
md_file.write_text(_render_markdown(cells), encoding="utf-8")
```
Adaptation (D-05):
- Guard on `if output_dir:` — only write when given (do NOT fall back to `Path(".")`).
- Hyphenated names `dev-test-<chip>.{json,md}` (mirrors validate-family's hyphen convention, Pitfall 4). Sanitize `<chip>` token for FS safety.
- JSON body = `report.to_dict()` (`diagnostic_report.py:407`). MD body = human table + fenced JSON = `report.to_json_block()` (`diagnostic_report.py:509`) beneath a results table (the self-contained issue body Phase 113 uploads).
- Always call `report.render(console)` to stdout (`diagnostic_report.py:431`) regardless of `--output-dir`.

**TTY-aware prompt gating** (D-02) — use `sys.stdin.isatty()`:
- On TTY: `prompt_provenance(is_uv)` (`diagnostic_report.py:148`) BEFORE the sweep; one-line destructive `Confirm.ask(...)` (precedent: `firmware.py:20` `from rich.prompt import Confirm`, used at `firmware.py:613`).
- Off-TTY / mock seam: skip both, build blank `Provenance()` (`diagnostic_report.py:128`); `is_submittable` → `False` (correct, not a gap); treat `--destructive` flag itself as consent.
- `-y/--yes` bypasses ONLY the destructive confirm on a TTY (D-03), never the provenance prompts.

**Composition sourcing (Claude's Discretion — grounded)**:
- `is_uv`: `full = app.db.get_eprom(chip)`; `is_uv = full.get("electrical-type") == "UV-EPROM" or prog.get("algorithm") == 0x0B` — same signal as `chip_test._write_region_for` (`chip_test.py:635-638`, `_PROTOCOL_UV_EPROM = 0x0B` at `:612`).
- `derive_plan(chip, app.db, destructive=destructive)` (`chip_test.py:318`) → `run_plan(plan, app.eprom_operator, app.db, sampler=<thunk>)` (`:501`) → `count_applicable(plan, results)` (`chip_test.py:925`) for `BannerCounts`.
- `AutoCapture(host_version=version, fw_board_identity=<version:board>, chip=chip, protocol=..., chip_id_expected=..., chip_id_actual=...)` (`diagnostic_report.py:56`). `version` imported at `cli_handlers.py:32`.
- `TransportHealth()` best-effort → all `None`/`NOT_MEASURED` honest fallback (`diagnostic_report.py:83`).
- `build_db_diff(chip, app.db, results)` (`diagnostic_report.py:241`) — read-only, RPT-05.
- Assemble `DiagnosticReport(auto_capture=..., transport=..., plan=..., results=..., banner=..., provenance=..., db_diff=..., vpp_before_mv=..., ...)` (`diagnostic_report.py:277`).

---

### MODIFY `run_plan` sampler hook — `firestarter_app/firestarter/chip_test.py`

**Analog:** `run_plan` (`:501-572`) and `_dispatch_multi_run` (`:783-872`) themselves.

**Current signature** (`chip_test.py:501-507`) — add `sampler`:
```python
def run_plan(plan: Plan, operator: Any, db: Any, *, runs: int = 2) -> list[StepResult]:
```
Adaptation (D-04): add `sampler: Any = None` keyword param. **`sampler=None` default keeps every existing caller/test unchanged and bench-free.** Thread `sampler` down through `_run_step` → `_dispatch_step` → `_dispatch_multi_run` (all currently take `*, runs`).

**Bracket site — the OP_WRITE loop** (`chip_test.py:819-828`):
```python
for _ in range(runs):
    if op == OP_WRITE:
        outcomes.append(operator.write_eprom(name, eprom_data, tmp_source_path))
    elif op == OP_VERIFY:
        ...
```
Adaptation: invoke `sampler("before")`/`sampler("after")` (or two callbacks) **immediately around the `OP_WRITE` operator call** so `vpp_before/after_mv` + `vpe_before/after_mv` tightly bracket the write pulse (D-04). Rejected: bracketing the whole `run_plan` call (can't distinguish write droop from read droop).

**Decoupling constraint (hard):** `chip_test.py` must **NOT** `import hardware.py`. The handler passes a **thunk/closure** over `sample_vpp_mv()`/`sample_vpe_mv()` (`hardware.py:339/344`). Engine stays sampler-agnostic. SAFE-02: sampler reuses `COMMAND_READ_VPP`(11)/`COMMAND_READ_VPE`(12) monitor path (energize+measure only) — no VPP-set, no new dispatch → SAFE-03 AST checker still passes.

**Standalone non-destructive read** (Phase-111 D-04) lives in the *handler*, not the engine: single VPP+VPE read into `vpp_mv`/`vpe_mv`, with before/after = `NOT_MEASURED`.

---

### MODIFY SAFE-03 AST checker — `firestarter_app/tools/check_devtest_orchestrator.py`

**Analog:** the file itself. It ALREADY has the machinery; Phase 112 removes its scope-tolerance stub for the now-existing handler.

**Current stub** (`check_devtest_orchestrator.py:67-71`):
```python
# The not-yet-existing Phase-112 `@dev.command("test")` CLI handler...
_DEVTEST_CLI_HANDLER = os.path.join(_HERE, "..", "firestarter", "dev_test_cli.py")
```
Adaptation: **point this at the real handler location.** Phase 112 lands the handler in `cli_handlers.py` (sibling of `dev_validate_family`), NOT a new `dev_test_cli.py`. Update `_DEVTEST_CLI_HANDLER` → `.../firestarter/cli_handlers.py`. Scanning the whole `cli_handlers.py` is acceptable — the deny buckets (`_VPP_SET_NAMES` `:80`, `_WIRE_DICT_KEYS` `:97`, `force`/`--force` `:112-114`) must find ZERO hits there for the gate to stay green, which is the intended invariant across the entire host CLI.

**Anti-hollow requirement (Phase 109 D-02/D-03):** the checker must now *actually scan* the handler, not silently skip it. The missing-file tolerance in `_scan_file` (`:190`) and `main()` (`:254-257`) stays for the `chip_test.py` seam but the handler path must resolve to a real file. Keep the `scanned`-empty fail-closed guard (`:263-269`).

**Paired negative-fixture pytest** — `tests/test_check_devtest_orchestrator.py`:
Extend with a test that plants a violation (e.g. `set_vpp` / wire-dict / `force=True`) **in a handler-shaped fixture** injected via a new env-override (mirror `FIRESTARTER_DEVTEST_SRC` at `:65`, or add a `FIRESTARTER_DEVTEST_HANDLER` seam) and assert the checker flips non-zero. Existing clean-pass baseline test (`test_check_devtest_orchestrator.py:57`) must still pass against the real `cli_handlers.py`.

---

### NEW handler unit tests — `firestarter_app/tests/`

**Analog:** the `dev validate-family` test seam (`EpromDatabase(skip_local_override=True)` + mock operator + `@click.pass_obj` AppContext, `cli_handlers.py:78-92`) and `test_check_devtest_orchestrator.py`'s subprocess pattern.

**Seam pattern:** construct a fresh `AppContext(db=EpromDatabase(skip_local_override=True), eprom_operator=<Mock>, ...)` per test (AppContext docstring `cli_handlers.py:82` confirms "CliRunner tests construct a fresh AppContext per test"). Inject prompts via `prompt_provenance(ask=Mock(side_effect=[...]), confirm=Mock(...))` (`diagnostic_report.py:148-153`) and force off-TTY (`sys.stdin.isatty` monkeypatch) so tests never block. Pass `sampler=None` (or a mock) so no `hardware.py` / bench access is needed (SC4).

**Assert:** the 3-way exit codes (0/1/2 per D-01), TTY vs off-TTY prompt behavior (D-02), `--output-dir` writes exactly two hyphenated files vs terminal-only, and that `run_plan`'s `sampler` fires around OP_WRITE.

---

## Shared Patterns

### 3-way verdict `sys.exit`
**Source:** `cli_handlers.py:1620-1624` (`dev_validate_family`); same in `dev consistency-check`/`dev write-cycle`.
**Apply to:** the new handler. Compute as `max` over per-verdict codes; `1` (BAD) beats `2` (marginal). See D-01.

### Injectable prompts / bench-free test seam
**Source:** `diagnostic_report.py:148-153` (`prompt_provenance(ask=, confirm=)`) + `cli_handlers.py:82` (AppContext, mock-operator seam).
**Apply to:** handler + its unit tests. Keeps SC4 (wiring unit-testable, no bench).

### `rich.prompt.Confirm` precedent
**Source:** `firmware.py:20` `from rich.prompt import Confirm`, used `firmware.py:613`.
**Apply to:** the `--destructive` "this sacrifices the chip" TTY confirm (D-02/D-03).

### Orchestrator-only (SAFE-02/03)
**Source:** `chip_test.py:494` `resolve_chip(name, db=db)` guard-honoring path; deny vocab in `check_devtest_orchestrator.py:80-114`.
**Apply to:** handler + sampler thunk — set no VPP, build no wire dict, pass no `--force`. Every executed op routes through the existing `EpromOperator` methods.

### Single-source dual render
**Source:** `diagnostic_report.py:407` `to_dict()` (canonical), `:437` `render()`, `:515` `to_json_block()`, `SCHEMA_VERSION`/`NOT_MEASURED` (`:42-43`).
**Apply to:** stdout render (always) + `.json`/`.md` artifacts (when `--output-dir`). Never hand-maintain a second field list.

---

## No Analog Found

None. Every new/modified file has a strong in-repo analog — this is a pure-integration phase composing existing 108-111 building blocks.

## Metadata

**Analog search scope:** `firestarter_app/firestarter/` (cli_handlers.py, chip_test.py, diagnostic_report.py, hardware.py, chip_resolver.py, firmware.py), `firestarter_app/tools/`, `firestarter_app/tests/`
**Files scanned:** 7
**Pattern extraction date:** 2026-07-03
