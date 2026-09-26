# Phase 114: Disposition / No-Auto-Graduate Lock + Graduation Ladder + Inbox Reconciliation - Research

**Researched:** 2026-07-03
**Domain:** Python host-CLI safety invariant (AST audit), report-side taxonomy vocabulary, stdlib issue parser, gsd-inbox triage integration
**Confidence:** HIGH — every claim below is grounded in a direct read of the current `firestarter_app/` source on the `v1.21-community-chip-validation-command` branch.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01 (mechanism depth — Docs + auto-tag only):** No new promotion tool/CLI. The ladder is (a) a *documented* taxonomy vocabulary and (b) an *automatic report-side tag* (`community-reported` / `community-fail`) derived from the sweep verdicts via the existing `DbDiff`/`build_db_diff` (Phase 110). Human promotion into `community-confirmed`/`supported` is a **manual maintainer action**, made actionable by INBOX-01's triage surfacing (which shows the N-agreeing count). SC2's "explicit human step" = that manual action; "reachable once N≥2 agree" = triage exposes the agreement count and the human decides — nothing in code performs or gates a state write.
- **D-02 (Report-side only):** `community-reported` / `community-confirmed` / `community-fail` exist **only** on the report / `DbDiff` as a ladder-state label. `chip_database.json`'s `support_status` **never** carries a community-* value; a chip reaches the existing `supported` state only via the unchanged human-authored `build_db.py` path. Rationale: (a) makes DISP-01's grep/AST audit trivially true (the only `support_status` write locus stays `build_db.py`); (b) avoids a footgun — every read guard treats `support_status != "supported"` as non-dispatchable, so a community-* value in a DB would silently disable a chip.
- **D-03 (dedup_fingerprint match):** Two reports "agree" iff their existing Phase-113 `dedup_fingerprint` (chip + per-op verdict signature) matches. Triage counts matching fingerprints across issues and surfaces "N agreeing." Reuses shipped code; deterministic. This cross-report N≥2 is **explicitly distinct** from the sweep's *internal* per-run N≥2 (Phase 108 multi-run of the same op on one bench) — the two Ns must not be conflated.
- **D-04 (firestarter_app `tools/` parser):** A stdlib parser in `firestarter_app/tools/` (e.g. `tools/parse_devtest_issue.py`) reads an issue body and emits the DB-diff (current `support_status` vs. the report's advisory proposed-disposition) + the N-agreeing count. It owns/mirrors the report schema (co-located with `diagnostic_report.py`'s `schema_version`), is stdlib-only + unit-testable via the established seams, and survives `gsd update` (it lives in the app repo, not the installed gsd-core workflow). `gsd-inbox` / the maintainer *invokes* it during triage — **do not edit the installed `.claude/gsd-core/workflows/inbox.md` in place** (fragile; overwritten on update). Target repo `henols/firestarter_app`. Detection markers = `[dev test]` issue-title marker + fenced-JSON `schema_version` (NOT GitHub labels — community testers lack write access).
- **D-05 (AST audit test, anti-hollow):** Add an AST-based audit test that asserts no code writes `support_status` as a result of parsing a community report — the only write sites remain the human-authored `build_db.py` path. Mirror the established SAFE-03 pattern (`tests/test_check_devtest_orchestrator.py`): AST scan (not raw substring grep) + a paired anti-hollow test with planted-violation fixtures so the gate can't silently pass. D-02 (report-side only) is what makes this a clean, provable invariant.

### Claude's Discretion
- Exact AST-checker scope for D-05 (which modules to scan; extend the existing SAFE-03 checker vs. a sibling checker) — follow SAFE-03 conventions.
- The precise `tools/parse_devtest_issue.py` CLI shape (stdin vs. file/`--issue` arg; how the N-agreeing count is gathered — e.g. scan multiple saved JSON bodies vs. a `gh`-fetched list) — planner's call, must reuse `dedup_fingerprint` per D-03.
- The exact report-side ladder-state representation (a derived `ladder_state` field vs. formalizing the current advisory prose into an enum) — honor D-02 (report-side only).
- Where the ladder taxonomy is documented (app `README` / `CLAUDE.md` / a `doc/`) — use the established doc location.
- Whether to pick up the maintainer-side auto-labeling `submit.py:183` hands to this phase — discretionary; if done it is a maintainer-side `gh` action during triage, never a community-side capability.

### Deferred Ideas (OUT OF SCOPE)
- **Maintainer promotion CLI/tool** (the rejected D-01 alternative): a helper that ingests ≥2 agreeing reports and *prints* a proposed status change. Explicitly out of scope now (close phase, over-build risk).
- **Human-written community-* in a user-override DB** (the rejected D-02 alternative): would require read-path handling of community-* as a state distinct from "non-supported." Deferred.
- SAFE-04 (`dev test` hard-fail on absent chip) is mapped to Phase 114 in REQUIREMENTS.md but is NOT in this phase's CONTEXT scope (CONTEXT covers DISP-01/GRAD-01/INBOX-01 only). Flag to the planner: reconcile whether SAFE-04 belongs in this phase or is tracked separately. [ASSUMED — needs confirmation]
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DISP-01 | No code path writes a chip's `support_status` from a parsed community report — graduation is flag-only and human-gated (locked anti-feature: no auto-graduation). | Confirmed the ONLY DB write locus is `build_db.py:714` (`"support_status": _support_status`). SAFE-03 AST-checker + anti-hollow test pattern (`tools/check_devtest_orchestrator.py` + `tests/test_check_devtest_orchestrator.py`) is the exact template to mirror. §Standard Stack, §DISP-01 Audit Design. |
| GRAD-01 | `support_status` taxonomy gains community ladder states (`community-reported`/`community-confirmed`/`community-fail`); transition to `confirmed`/`supported` requires a human step keyed on N≥2 consistency. | The three names already exist as advisory prose (`_DISPOSITION_*`, `diagnostic_report.py:203-208`). `build_db_diff` (L230) already maps verdicts→advisory disposition. `dedup_fingerprint` (`diagnostic_report.py:171`) is the N≥2 agreement key. §GRAD-01 Ladder Design. |
| INBOX-01 | `gsd-inbox` triage auto-parses the report's fenced JSON and surfaces its DB-diff against the current DB for maintainer review. | `to_dict()`/`to_json_block()` fenced-JSON shape (`diagnostic_report.py:380,470`); detection via `[dev test]` title + `schema_version`; parser home `tools/`; inbox.md integration seam (invoke, don't edit). §INBOX-01 Parser Design. |
</phase_requirements>

## Summary

Phase 114 is a **pure host-side + planning/tooling phase** — zero firmware changes, zero new runtime code paths that touch hardware, and (per the milestone's reuse-first mandate) **zero new third-party packages**. Everything it needs already ships: the advisory `DbDiff`/`build_db_diff` pipeline (Phase 110), the deterministic `dedup_fingerprint` (Phase 113), the single-source `to_dict()` fenced-JSON report shape (Phase 110), and — crucially — the SAFE-03 AST-checker + anti-hollow planted-fixture test pattern (Phase 109) that DISP-01 must mirror almost exactly.

The three requirements decompose into three independently-testable, bench-free work items: (1) **DISP-01** — a new AST checker (`tools/check_no_community_support_status_write.py` or an extension of the SAFE-03 checker) that proves no `support_status` write results from report parsing, plus its paired planted-violation test; (2) **GRAD-01** — formalize the already-present `community-reported`/`community-confirmed`/`community-fail` vocabulary as a report-side ladder-state (derived from sweep verdicts, never a DB write) and document the N≥2-human-gated promotion process; (3) **INBOX-01** — a stdlib `tools/parse_devtest_issue.py` that detects a `dev test` issue (`[dev test]` title + fenced-JSON `schema_version`), extracts the embedded JSON, renders the current-vs-proposed DB-diff, and counts matching `dedup_fingerprint`s across a set of issue bodies to surface "N agreeing."

The single most important structural fact the planner must internalize: **the DISP-01 gate is wired into CI via pytest, not via a dedicated CI YAML step.** The existing SAFE-03 checker is *never* named in `.github/workflows/ci.yml`; it runs because `pytest tests/` executes `tests/test_check_devtest_orchestrator.py`, which shells out to the checker as a subprocess. The DISP-01 gate follows the identical pattern — a checker tool in `tools/` plus a subprocess-driving test in `tests/`, and CI picks it up automatically through `pytest tests/ --cov-fail-under=70`. No CI YAML edit is required (and would be wrong to add — it would double-run the gate).

**Primary recommendation:** Mirror SAFE-03 precisely. Build `tools/check_no_community_support_status_write.py` (AST scan for `support_status` writes outside the allowed `build_db.py` locus, with an env-override seam for fixture injection), pair it with `tests/test_<name>.py` carrying clean-baseline + planted-violation fixtures; formalize the ladder as a report-side derived field on `DbDiff` (never a `chip_database.json` write); ship `tools/parse_devtest_issue.py` as a stdlib CLI the maintainer/gsd-inbox invokes; document the taxonomy in `firestarter_app/doc/`.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| DISP-01 no-auto-graduate lock (AST audit) | Build/CI tooling (`tools/` + `tests/`) | — | It is a static-analysis gate over host source; it runs in CI via pytest, touches no runtime path and no hardware. |
| GRAD-01 ladder-state tag derivation | Host CLI report model (`firestarter/diagnostic_report.py`) | Docs (`doc/`) | Report-side only (D-02). The tag is a pure function of sweep verdicts, computed where `DbDiff` already lives; the promotion *process* is documentation, not code. |
| GRAD-01 N≥2 agreement key | Host CLI (`dedup_fingerprint`, already shipped) | Triage tooling (`tools/parse_devtest_issue.py`) | The key exists in the report model; counting agreement across reports is a triage-tool concern. |
| INBOX-01 issue parse + DB-diff surface | Triage tooling (`tools/parse_devtest_issue.py`) | Installed gsd-inbox workflow (invoke-only) | Parser lives in the app repo (survives `gsd update`, D-04); the gsd-core workflow only *calls* it. |
| `support_status` DB write | Build pipeline (`tools/build_db.py`) — UNCHANGED | — | The sole write locus; Phase 114 must not add another. This is the invariant DISP-01 protects. |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python `ast` (stdlib) | 3.9+ | AST scan for DISP-01 write-site detection | Already the SAFE-03 checker's mechanism (`tools/check_devtest_orchestrator.py`); AST beats substring grep (D-05). |
| Python `json` (stdlib) | 3.9+ | Parse the fenced-JSON block from an issue body | Report already serializes via `json.dumps` in `to_dict()`/`to_json_block()`. |
| Python `re` (stdlib) | 3.9+ | Extract the ```` ```json ```` fenced block and match the `[dev test]` title marker | Same idiom already used by `submit.py`'s `_SCRUBS`. |
| `pytest` | >=8.0 (dev), >=7.0 (runtime extra) | Drive the checker subprocess + parser unit tests; the CI seam for the gate | Established: SAFE-03 gate runs through pytest, not a dedicated CI step. |
| `rich` | already a dependency | Optional pretty-render of the parser's DB-diff table | Report model already uses `rich.table.Table`; reuse if a human-facing render is wanted. |

**No new third-party packages.** REQUIREMENTS.md "Out of Scope" explicitly forbids new Python third-party deps: *"Reuse-first — `click`/`rich`/`requests` + stdlib cover everything; `gh` is an optional runtime tool, not a pip dep."* `[VERIFIED: REQUIREMENTS.md L98]`

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `gh` CLI | optional runtime tool | Fetch issue bodies for the N-agreeing count in a maintainer-side triage flow | Only if the parser gathers multiple issues live; the unit-test path uses saved JSON fixtures instead. Never a pip dependency. |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Extend the existing `check_devtest_orchestrator.py` with a 4th deny-bucket | A sibling `check_no_community_support_status_write.py` | Sibling checker keeps concerns separable (SAFE-03 = orchestrator-only; DISP-01 = no-community-write) and gives the new gate its own clean anti-hollow test file. Recommended, but D-05 discretion allows either. |
| A derived `ladder_state` enum field on `DbDiff` | Keep the current `_DISPOSITION_*` advisory prose only | An explicit enum makes the parser's job trivial and the taxonomy machine-checkable; prose-only keeps the diff smaller. Discretionary (D-01/D-02). |

**Installation:** None required. All stdlib + existing dev deps (`pip install -e .[test]`).

## Package Legitimacy Audit

> Not applicable. Phase 114 installs **zero** external packages (stdlib-only per D-04 and the milestone "no new third-party dependencies" out-of-scope rule). No registry verification needed.

## Architecture Patterns

### System Architecture Diagram

```
COMMUNITY TESTER SIDE (already shipped — Phases 108–113, UNCHANGED)
  firestarter dev test <chip>  ──► DiagnosticReport (diagnostic_report.py)
                                      │  to_dict()  ──► fenced ```json``` block
                                      │  build_db_diff() ──► DbDiff (advisory proposed_disposition)
                                      │  dedup_fingerprint() ──► 12-hex shorthash
                                      ▼
                                 submit.py --submit
                                   ├─ gh issue create  (title "[dev test] <chip> — <verdict> (<hash>)")
                                   └─ browser issues/new?title=…&body=…
                                      ▼
                             GitHub issue on henols/firestarter_app
                             (title marker + fenced-JSON schema_version)

MAINTAINER / TRIAGE SIDE (Phase 114 NEW work)
  gsd-inbox triage ──invokes──► tools/parse_devtest_issue.py   (NEW, stdlib)
                                   │ detect: "[dev test]" title + fenced-JSON schema_version
                                   │ extract embedded JSON
                                   │ DB-diff: current support_status  vs  proposed_disposition
                                   │ count matching dedup_fingerprint across issues → "N agreeing"
                                   ▼
                             maintainer reads actionable diff + N-count
                                   │ (explicit HUMAN decision — no code writes state)
                                   ▼
                             manual build_db.py edit → support_status="supported"
                             (UNCHANGED human-authored path — the ONLY write locus)

CI GATE (Phase 114 NEW work, DISP-01)
  pytest tests/ ──► tests/test_<disp01>.py ──subprocess──► tools/check_<disp01>.py
                       │ AST-scan firestarter/ + tools/parse_devtest_issue.py
                       │ assert: no support_status write outside build_db.py locus
                       │ planted-violation fixtures prove the gate can fail (anti-hollow)
                       ▼
                    exit 0 = PASS (green) / exit 1 = FAIL (red)
```

### Recommended Project Structure
```
firestarter_app/
├── firestarter/
│   └── diagnostic_report.py     # EXTEND: formalize ladder-state on DbDiff (report-side only)
├── tools/
│   ├── build_db.py              # UNCHANGED — the sole support_status write locus
│   ├── check_devtest_orchestrator.py   # SAFE-03 template to mirror
│   ├── check_no_community_support_status_write.py   # NEW (DISP-01 AST gate)
│   └── parse_devtest_issue.py   # NEW (INBOX-01 stdlib parser CLI)
├── tests/
│   ├── test_check_devtest_orchestrator.py   # anti-hollow template to mirror
│   ├── test_check_no_community_support_status_write.py   # NEW (DISP-01 anti-hollow)
│   └── test_parse_devtest_issue.py          # NEW (parser units via saved-JSON fixtures)
└── doc/
    └── community-validation.md  # NEW/updated (GRAD-01 taxonomy + N≥2 process)
```

### Pattern 1: AST checker with env-override fixture-injection seam (mirror SAFE-03)
**What:** A `tools/check_*.py` that `ast.parse`s target source, walks it with an `ast.NodeVisitor` collecting violation strings, prints `PASS:`/`FAIL:` and `sys.exit(0/1)`. Target paths are module constants overridable via an environment variable so the paired test can inject a deliberately-violating fixture without editing real source.
**When to use:** Every machine-enforced invariant in this repo (SAFE-03, GATE-03, check_dispatch).
**Example:**
```python
# Source: tools/check_devtest_orchestrator.py (real, current)
_HERE = os.path.dirname(__file__)
_DEFAULT_CHIP_TEST = os.path.join(_HERE, "..", "firestarter", "chip_test.py")
FIRESTARTER_DEVTEST_SRC = os.environ.get("FIRESTARTER_DEVTEST_SRC", _DEFAULT_CHIP_TEST)

class _OrchestratorDenyVisitor(ast.NodeVisitor):
    def visit_Call(self, node): ...   # collect deny-list hits into buckets
    def visit_Dict(self, node): ...
    def visit_Constant(self, node): ...

def main():
    ...
    if not scanned:               # fail-closed: never vacuously pass
        print("FAIL: no ... files found to scan ..."); sys.exit(1)
    if violations: _print_bucket(...); sys.exit(1)
    print("PASS: ..."); # exit 0
```

### Pattern 2: Anti-hollow paired test — planted-violation fixtures via subprocess (mirror SAFE-03)
**What:** The test writes a temp `.py` file containing a REAL violation, points the checker at it via the env-override, runs the checker **as a subprocess** (`subprocess.run([sys.executable, "tools/check_*.py"], env=...)`), and asserts `returncode != 0` + `"FAIL:"` in stdout. A clean-fixture test through the same seam asserts `returncode == 0` (proves the seam is a faithful re-target, not the source of the failure). Plus a clean-baseline test on the REAL source, and a test asserting the PASS line names the scanned file (proving it was not silently skipped — the v1.12 hollow-GATE-03 failure mode).
**When to use:** Every checker in this repo ships this pairing. D-05 mandates it for DISP-01.
**Example:**
```python
# Source: tests/test_check_devtest_orchestrator.py (real, current)
def _run_checker(env_overrides=None):
    env = {**os.environ, **(env_overrides or {})}
    return subprocess.run([sys.executable, "tools/check_devtest_orchestrator.py"],
                          cwd=str(_FA_DIR), capture_output=True, text=True, env=env)

def test_checker_exits_nonzero_on_planted_vpp_set(tmp_path):
    bad = tmp_path / "planted.py"
    bad.write_text("def orchestrate(op):\n    op.set_vpp(12000)\n")
    result = _run_checker({"FIRESTARTER_DEVTEST_SRC": str(bad)})
    assert result.returncode != 0 and "FAIL:" in result.stdout
```

### Pattern 3: Single-source report model — never a second field list (respect when extending)
**What:** `DiagnosticReport.to_dict()` is the ONE canonical mapping; both `render()` (rich table) and `to_json_block()` consume it. Any new ladder-state field must be added to `to_dict()` once and both renders pick it up. The `dedup_fingerprint` deliberately excludes volatile fields so a clean re-test dedups identically.
**When to use:** GRAD-01's report-side ladder-state addition.
**Example:**
```python
# Source: firestarter/diagnostic_report.py:380 (real, current)
def to_dict(self) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,        # detection marker for the parser (D-04)
        ...
        "dedup_fingerprint": dedup_fingerprint(self),   # N≥2 agreement key (D-03)
        "db_diff": self._db_diff_dict(),         # extend HERE for ladder_state
    }
```

### Anti-Patterns to Avoid
- **Writing a community-* value into `chip_database.json` or a user-override DB.** Every read guard (`chip_resolver.py:55`, `eprom_info.py:148`, `check_dispatch.py:242`) treats `support_status != "supported"` as non-dispatchable → a community-* value would silently disable the chip. This is exactly the footgun D-02 exists to prevent.
- **Editing `.claude/gsd-core/workflows/inbox.md` in place.** It is installed gsd-core, overwritten on `gsd update`. The parser must live in the app repo and be *invoked*, not embedded (D-04).
- **Adding a dedicated CI YAML step for the DISP-01 checker.** The gate runs through `pytest tests/` (like SAFE-03). A YAML step would double-run it and drift from the SAFE-03 convention.
- **A hollow gate.** A checker that scans nothing, or a test with no planted-violation fixture, is the v1.12 GATE-03 tech-debt the project explicitly rejects. Fail-closed on an empty scan; prove the gate can go red.
- **Conflating the two N≥2 rules.** Phase 108's per-run N≥2 (same op re-run on one bench → `marginal` on disagreement) is INTERNAL to one report. GRAD-01's N≥2 is CROSS-report agreement via matching `dedup_fingerprint`. Do not reuse one for the other (D-03).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Detect a `support_status` write in source | Regex/substring grep | `ast` walk with `NodeVisitor` (SAFE-03 pattern) | Substring grep false-positives on comments/docstrings/reads; AST distinguishes an assignment target from a read. D-05 mandates AST. |
| Report dedup / agreement key | A new hash over report fields | `dedup_fingerprint(report)` (`diagnostic_report.py:171`) | Already deterministic, volatile-field-free, 12-hex; reusing it IS the D-03 rule. |
| Current-vs-proposed DB-diff | A new DB reader | `build_db_diff(name, db, results)` (`diagnostic_report.py:227`) | Already reads `support_status` via the exact `chip_resolver.py:54` read site and emits advisory (never-write) disposition text. |
| Ladder-state names | Invent new strings | The existing `_DISPOSITION_*` prose (`diagnostic_report.py:203-208`) | Phase 114 *formalizes*, does not invent (CONTEXT Specifics). |
| Checker subprocess test harness | New test scaffolding | The `_run_checker()` + env-override idiom (`test_check_devtest_orchestrator.py:49`) | Proven, and its clean/planted/PASS-line-naming trio is the anti-hollow contract. |

**Key insight:** This phase is almost entirely *composition and formalization* of code that already shipped in Phases 108–113. The only genuinely new artifacts are the DISP-01 AST checker (a near-clone of the SAFE-03 checker) and the stdlib issue parser.

## Grounded Code Findings (the load-bearing facts for the planner)

### `diagnostic_report.py` — ladder names, DbDiff, dedup, schema, to_dict
- **The three ladder-state names already exist as advisory prose** `[VERIFIED: firestarter/diagnostic_report.py:203-208]`:
  ```python
  _DISPOSITION_COMMUNITY_FAIL = "suggests: community-fail signal (advisory -- human triage required)"   # L206-208
  _DISPOSITION_CANDIDATE = "suggests: candidate for community-reported (advisory)"                       # L209
  _DISPOSITION_INCONCLUSIVE = "inconclusive -- needs N>=2 agreement (advisory)"                          # L210
  _DISPOSITION_NO_CHANGE = "no change suggested (advisory)"                                              # L211
  ```
  Note: `community-fail` and `community-reported` appear verbatim; `community-confirmed` is NOT yet a string here (it only appears in the "needs N>=2 agreement" prose). GRAD-01 must introduce/formalize `community-confirmed` as the human-gated target state. `[VERIFIED: grep — community-confirmed absent from diagnostic_report.py]`
- **`DbDiff` dataclass** `[VERIFIED: L214-227]`: fields `current_support_status: str = "supported"` and `proposed_disposition: str = ""`. Docstring explicitly states `proposed_disposition` is "NEVER a concrete `support_status` value and this module NEVER writes it back to the database." This is the object the ladder-state attaches to (D-02).
- **`build_db_diff(name, db, results)`** `[VERIFIED: L230-260]`: the current advisory-disposition emitter. Reads `db.get_eprom_config(name)` (returns `(config_dict, manufacturer)` tuple), takes `(raw_config or {}).get("support_status", "supported")`, then maps the set of step verdicts → one of the four `_DISPOSITION_*` strings. Branch logic: any `BAD`→community-fail; any `marginal`/indeterminate-fingerprint→inconclusive; all-`OK` (subset of {OK,NA,SKIPPED})→candidate; else no-change. This is the exact seam GRAD-01 extends into a formal ladder-state tag.
- **`dedup_fingerprint(report)`** `[VERIFIED: L174-199]`: reads ONLY `auto_capture.chip`/`.protocol` + per-step `op=verdict:fingerprint_classification`, joins with `|`, `sha256`, truncates to 12 lowercase hex. Deterministic, excludes all volatile fields. This IS the D-03 agreement key — two reports agree iff this string matches.
- **`SCHEMA_VERSION = "1.0"`** `[VERIFIED: L55]` baked into `to_dict()` output at L394. The parser's detection marker (D-04).
- **`to_dict()`** `[VERIFIED: L386-404]`: canonical mapping; includes `schema_version`, `auto_capture` (with `chip`, `protocol`), `steps` (each with `op`/`verdict`/`fingerprint`), `dedup_fingerprint`, and `db_diff` (`current_support_status`/`proposed_disposition`). `to_json_block()` (L476-478) wraps `json.dumps(self.to_dict(), indent=2)` in a ```` ```json ```` fence — exactly what the parser reads back.

### `submit.py` — dedup key wiring, SUBMIT_REPO, build_issue_url, the L183 hand-off
- **`SUBMIT_REPO = "henols/firestarter_app"`** `[VERIFIED: submit.py:53]` — hardcoded, never remote-inferred (D-01). Confirms D-04 target repo.
- **`GSD_INBOX_LABEL = "gsd-inbox"`** `[VERIFIED: L54]` — used only on the `gh issue create --label` path (L226), which requires write access. The browser-URL path deliberately omits labels.
- **`build_title()`** `[VERIFIED: L141-151]` — produces `[dev test] {chip} — {verdict} ({shorthash})` where `shorthash = report.to_dict()["dedup_fingerprint"]`. This is where the `[dev test]` title marker + the dedup hash both enter the issue title (the two triage-detection anchors).
- **`build_issue_url()`** `[VERIFIED: L175-186]` — the ~L183 hand-off, quoted verbatim:
  > *"Deliberately OMITS the `labels` query param (RESEARCH Pitfall 1): GitHub silently drops or 404s the `labels` param for community testers without write access on `henols/firestarter_app` -- triage relies on the `[dev test]` title marker plus the fenced-JSON `schema_version` instead. **Server-side template-based labeling is deferred to Phase 114.**"*
  Interpretation for the planner: the deferred item is *maintainer-side* auto-labeling during triage (a `gh` action), never a community capability. Picking it up is discretionary (D-05 discretion bullet).
- **`overall_verdict()`** `[VERIFIED: L126-138]` — FAIL/INCONCLUSIVE/PASS title verdict (distinct from the handler's exit-code `max()` ordering). Useful context for how a report's headline maps to a ladder-state.

### `check_devtest_orchestrator.py` + its test — the SAFE-03 template (D-05)
- **Mechanism** `[VERIFIED: tools/check_devtest_orchestrator.py]`: `ast.parse` → `_OrchestratorDenyVisitor(ast.NodeVisitor)` collecting three violation buckets via `visit_Call`/`visit_Dict`/`visit_Constant`. Two scan modes: `_scan_file` (whole file, for fresh modules like `chip_test.py`/`submit.py`) and `_scan_target_functions` (name-filtered `FunctionDef` walk, for the large pre-existing `cli_handlers.py` to avoid false-positives on unrelated `--force` flags). Deny vocabularies are `frozenset` module constants.
- **Fail-closed guards** `[VERIFIED: L397-403]`: if `scanned` is empty → `FAIL` + `sys.exit(1)` ("the gate cannot vacuously pass with nothing scanned"). `_scan_target_functions` returns `None` (→ treated as not-scanned) if the module contains none of the named functions — so a rename without updating the checker fails closed. `_assert_host_only` (L307) rejects any path resolving into the firmware sub-repo.
- **Env-override seams** `[VERIFIED: L86,98,113]`: `FIRESTARTER_DEVTEST_SRC` / `_HANDLER` / `_SUBMIT` let the paired test inject fixtures. Mirrors `check_dispatch.py`'s `FIRESTARTER_DB_FILE` seam.
- **Exit discipline** `[VERIFIED: L66-72,422,424-427]`: exit 0 = `PASS:` line naming every scanned file; exit 1 = per-bucket `FAIL:` summary (first 20 each).
- **Anti-hollow test structure** `[VERIFIED: tests/test_check_devtest_orchestrator.py]`: `_run_checker(env_overrides)` runs the tool as a subprocess with `cwd=_FA_DIR`. Tests: (1) clean baseline exits 0 with `PASS:`; (2-5) planted violations via env-override exit non-zero with `FAIL:`; (6) clean fixture through the same seam still passes (isolates the seam); (7) handler-shaped + (8) submit-shaped planted violations for each leg; plus explicit "PASS line names the scanned file" assertions proving no leg was silently skipped.
- **DISP-01 translation:** the new checker's deny concept is different (a `support_status` *write* — i.e. an `ast.Assign`/`ast.AnnAssign` whose target is `support_status` as a Name, or a subscript `x["support_status"] = ...`, occurring in any scanned module OTHER than the allowed `build_db.py` locus). The visitor should target `visit_Assign`/`visit_AnnAssign` (and dict-key subscript assignment). See §DISP-01 Audit Design below for the exact write-site inventory it must allow.

### `chip_resolver.py` — the read guard proving D-02
- **`support_status != "supported"` guard** `[VERIFIED: chip_resolver.py:54-57]`:
  ```python
  support_status = raw_config.get("support_status", "supported")
  if support_status != "supported":
      reason = raw_config.get("unsupported_reason", "unsupported on this hardware")
      raise ChipNotImplementedError(f"{name}: {reason}")
  ```
  Any non-`supported` value (including a hypothetical `community-reported`) makes the chip non-dispatchable BEFORE any wire dict is built. This is the concrete reason community-* must stay off the DB (D-02).

### `build_db.py` — the sole write locus (the DISP-01 allow-list)
- **The ONLY persistent `support_status` write** `[VERIFIED: tools/build_db.py:714]`: `"support_status": _support_status,` inside the `chip_entry` dict literal. The value comes from `_support_status`, assigned at:
  - L491 `_support_status = "supported"` (default)
  - L510 `= "protocol-not-implemented"` (proto 0x34)
  - L544 `= "adapter-required"`
  - L603 `= "adapter-required"`
  - L682 `= "vpp-exceeds-max"`
  - L694 (comment — leaves default)
  All are human-authored classification, driven by frozen DB fields, never by a community report. `[VERIFIED: grep support_status across firestarter/ + tools/]`

### Full `support_status` write-site inventory (what the audit must allow / recognize)
`[VERIFIED: grep -rn "support_status" firestarter/ tools/ --include=*.py]`

| Site | Kind | Disposition for DISP-01 audit |
|------|------|-------------------------------|
| `tools/build_db.py:491/510/544/603/682/694` → `:714` | **WRITE** (into generated DB entry) | ALLOWED locus — human-authored, unchanged. |
| `firestarter/eprom_info.py:150` `combined_data["support_status"] = ss` | Write to an **in-memory display dict**, value READ from `raw_config_data` (L148) | Not a DB write, not report-parsing-driven. The audit must NOT false-positive here (it copies a value already in the DB into a display dict for `firestarter info`). Scope the audit to exclude this, or exclude `eprom_info.py`. |
| `firestarter/chip_resolver.py:54` | READ (guard) | Read — no concern. |
| `firestarter/diagnostic_report.py:243` | READ (`build_db_diff`) | Read — no concern. |
| `firestarter/eprom_info.py:148,245-247` | READ (display) | Read — no concern. |
| `tools/check_dispatch.py:242` | READ (CI gate iterates) | Read — no concern; stays green under D-02 (see below). |
| `firestarter/diagnostic_report.py:223` `current_support_status: str = "supported"` | Dataclass field default (a `DbDiff` attribute, NOT the `support_status` key) | Different identifier — should not match a `support_status`-key write detector, but note the near-name so the audit's matching is precise. |

**Planner action:** the DISP-01 checker's write-detector must (a) treat `build_db.py` as the allowed locus, (b) scan the report/parse path (`diagnostic_report.py`, the new `tools/parse_devtest_issue.py`, and any new ladder code) for a `support_status` DB-write, and (c) NOT flag the `eprom_info.py:150` display-dict copy (either by scoping the scanned target set to the report/parse modules only, or by a precise "assigns a community-* value / writes to a persisted DB object" rule). Recommend scoping the scan to the report + parser modules (mirrors how SAFE-03 scopes its targets) rather than trying to whitelist by value.

### `check_dispatch.py` — stays green under D-02
- **`chip_ss = chip.get("support_status", "supported")`** `[VERIFIED: tools/check_dispatch.py:242]` — iterates every chip in `chip_database.json` and asserts non-`supported` chips carry `unsupported_reason` + are non-dispatchable. Because community-* never enters `chip_database.json` (D-02), this gate is entirely unaffected. Confirmed. `[VERIFIED: L242-300]`

### Inbox integration seam (INBOX-01, D-04)
- **`.claude/gsd-core/workflows/inbox.md`** `[VERIFIED]` — the triage workflow. It fetches issues via `gh issue list ... --json number,title,labels,body,...`, classifies by label/body pattern (`<step name="fetch_issues">`, L45-69), reviews against templates, and writes a report to `.planning/INBOX-TRIAGE.md`. It has NO `dev test` awareness and MUST NOT be edited (installed gsd-core, `gsd update` overwrites).
- **`.claude/commands/gsd-inbox.md`** `[VERIFIED]` — the command entry; `<execution_context>` `@`-includes the workflow file. Also installed gsd-core; not editable in place.
- **The seam (given "invoke, don't edit"):** `tools/parse_devtest_issue.py` must be a **self-contained CLI** the maintainer runs during triage (e.g. `python tools/parse_devtest_issue.py --body-file issue.json` or piping a `gh issue view <n> --json body -q .body` output to stdin). It: detects a `dev test` report (`[dev test]` in title + a fenced-JSON block whose parsed object has `schema_version`), extracts + parses the JSON, prints the DB-diff (current `support_status` from the live DB vs. the report's `db_diff.proposed_disposition` / derived ladder-state), and — given a set of issue bodies — counts matching `dedup_fingerprint`s to print "N agreeing." The integration is **documentation** (the new `doc/community-validation.md` tells the maintainer to run it during `gsd-inbox` triage), not a code edit to the workflow. `[VERIFIED: D-04 CONTEXT + inbox.md structure]`
- Optional (discretionary): a project-local convention could have the maintainer append the parser's output to `.planning/INBOX-TRIAGE.md` after running `gsd-inbox` — but that is a manual/documented step, not an in-place workflow edit.

## DISP-01 Audit Design (concrete recommendation)

- **New tool:** `tools/check_no_community_support_status_write.py` (sibling to the SAFE-03 checker; keeps concerns separable).
- **Scan targets (module constants + env-override seams):** the report/parse path — `firestarter/diagnostic_report.py`, the new `tools/parse_devtest_issue.py`, and any new ladder module. Explicitly NOT `build_db.py` (allowed locus) and NOT `eprom_info.py` (display-dict copy). Provide `FIRESTARTER_DISP01_*` env overrides mirroring SAFE-03 for fixture injection.
- **Deny rule:** an AST `Assign`/`AnnAssign` (or a subscript assignment `obj["support_status"] = ...`) that writes the `support_status` key/attribute within a scanned module — i.e. any *write* of `support_status` in the report/parse path is a violation, since by construction that path must only READ it (via `db.get_eprom_config`). This is the cleanest formulation because D-02 guarantees the report path never legitimately writes `support_status`. A secondary rule can flag any string literal equal to a community-* value being assigned to a `support_status` target.
- **Fail-closed:** empty scan → `FAIL` + exit 1 (mirror SAFE-03 L397-403); PASS line names each scanned file.
- **Paired anti-hollow test:** `tests/test_check_no_community_support_status_write.py` with: clean-baseline (real source, exit 0, PASS names files); planted violation (a fixture that does `chip["support_status"] = "community-reported"`, via env-override → exit non-zero, `FAIL:`); clean-fixture-through-seam (exit 0, isolates the seam); PASS-line-names-file assertion (anti-skip).

## GRAD-01 Ladder Design (concrete recommendation)

- **Formalize the vocabulary** (report-side only, D-02): introduce the missing `community-confirmed` name and, optionally, a `ladder_state` derived field on `DbDiff` (or a small enum/constant set alongside the `_DISPOSITION_*` strings). The auto-tag a single report can carry is `community-reported` (all-OK candidate) or `community-fail` (any BAD) — derived by `build_db_diff` from sweep verdicts. `community-confirmed` is NEVER auto-assigned; it is the human-gated target reachable only when N≥2 reports agree.
- **The N≥2 rule is triage-side, not report-side:** a single `DiagnosticReport` cannot know about other reports. The N-agreeing count is computed by `tools/parse_devtest_issue.py` over multiple issue bodies by counting matching `dedup_fingerprint`s (D-03). Nothing in `diagnostic_report.py` performs or gates a state write — SC2's "explicit human step" is the maintainer editing `build_db.py`.
- **Documentation (the ladder itself, D-01):** `doc/community-validation.md` documents the four states, the auto-tag derivation, the N≥2-via-dedup_fingerprint promotion criterion, and the manual promotion process (maintainer edits `build_db.py` → `support_status="supported"`). Use `doc/` — the established operator-canonical doc location (existing files: `infoic-field-dictionary.md`, `protocol-id.md`, etc.).

## INBOX-01 Parser Design (concrete recommendation)

- **`tools/parse_devtest_issue.py`, stdlib-only.** CLI shape (discretionary, D-04): accept an issue body from `--body-file <path>`/stdin (unit-testable via saved-JSON fixtures) and, for the N-count, either a directory/glob of saved bodies or a `gh`-fetched list (maintainer-side).
- **Detection:** title contains `[dev test]` AND the body has a ```` ```json ```` fence whose parsed object contains `schema_version`. Both markers required (defensive against a stray fenced block).
- **DB-diff surface:** parse the embedded JSON → read `db_diff.current_support_status` (or re-derive from the live DB via the same `get_eprom_config` read for freshness) and `db_diff.proposed_disposition`; render current-vs-proposed. Reuse `rich` if a table render is wanted (matches the report's own style).
- **N-agreeing:** collect `to_dict()["dedup_fingerprint"]` from each provided body; group; report the count of issues sharing the fingerprint under test (D-03). Emphasize in output that this count is a *maintainer decision input*, not an auto-promotion trigger.
- **Untrusted input:** the issue body is attacker-controllable (any community member can open an issue). The parser must `json.loads` defensively (catch `JSONDecodeError`, bound size, never `eval`), treat all string fields as data (never execute/interpolate into a shell), and tolerate malformed/oversized/missing fields without crashing. See §Security Domain.

## Runtime State Inventory

Not a rename/refactor/migration phase — no stored data, service config, OS-registered state, or build artifacts carry a string this phase renames. This phase ADDS files (a checker, a parser, a test, a doc) and extends one module (`diagnostic_report.py`); it renames nothing and migrates no data. **None — verified by scope review (all work is additive host/tooling code).**

## Common Pitfalls

### Pitfall 1: The DISP-01 gate false-positives on `eprom_info.py:150`
**What goes wrong:** `combined_data["support_status"] = ss` (`eprom_info.py:150`) is a subscript assignment to the `support_status` key — a naive write-detector flags it.
**Why it happens:** It writes the key, but into a display dict, using a value READ from the DB (not a community report).
**How to avoid:** Scope the checker's scan targets to the report/parse path (`diagnostic_report.py`, the new parser, new ladder code) and exclude `eprom_info.py` and `build_db.py`. This mirrors how SAFE-03 scopes its own targets rather than scanning the whole tree.
**Warning signs:** The gate goes red on unchanged, unrelated display code.

### Pitfall 2: Adding a redundant CI YAML step for the checker
**What goes wrong:** Adding `- name: DISP-01 gate / run: python tools/check_...py` to `ci.yml` double-runs the gate and diverges from the SAFE-03 convention.
**Why it happens:** Assuming checkers are wired as CI steps — but `.github/workflows/ci.yml` never names `check_dispatch.py` or `check_devtest_orchestrator.py`; they run via `pytest tests/`.
**How to avoid:** Wire the gate ONLY through a pytest test that subprocess-runs the checker. CI's `pytest tests/ --cov-fail-under=70` step picks it up automatically.
**Warning signs:** The gate name appears in `ci.yml`.

### Pitfall 3: A hollow gate (the v1.12 GATE-03 tech-debt)
**What goes wrong:** A checker that scans nothing (or a test with no planted-violation fixture) always passes and proves nothing.
**Why it happens:** Skipping the anti-hollow pairing D-05 mandates.
**How to avoid:** Fail-closed on empty scan (SAFE-03 L397-403); ship planted-violation fixtures + a "PASS line names the scanned file" assertion so a silently-skipped leg is caught.
**Warning signs:** No `tmp_path` fixture writing a deliberately-bad `.py` in the test file.

### Pitfall 4: Writing a community-* value anywhere near the DB
**What goes wrong:** Any `support_status` = a community-* value reaching `chip_database.json` or a user-override silently disables the chip (read guards refuse `!= "supported"`).
**Why it happens:** Treating the ladder-state as a DB state rather than a report-side label.
**How to avoid:** Keep community-* strictly on the report / `DbDiff` (D-02). The DISP-01 audit is the machine backstop.
**Warning signs:** A community-* string literal assigned to a DB-bound `support_status`.

### Pitfall 5: Conflating the two N≥2 rules
**What goes wrong:** Reusing Phase 108's per-run `marginal` N≥2 logic for cross-report agreement (or vice versa).
**Why it happens:** Both are "N≥2" but at different scopes.
**How to avoid:** Cross-report agreement = matching `dedup_fingerprint` across DISTINCT issues (D-03). Per-run N≥2 stays inside one sweep. Document both in `doc/community-validation.md` to prevent future confusion.
**Warning signs:** The parser reads step-level run counts instead of comparing fingerprints across reports.

### Pitfall 6: Parser trusts the issue body
**What goes wrong:** A malformed/oversized/hostile issue body crashes the parser or is mis-parsed.
**Why it happens:** Community issue bodies are untrusted input.
**How to avoid:** Defensive `json.loads` (catch `JSONDecodeError`), size bounds, treat all fields as inert data, no shell interpolation of body content. Test with malformed-fixture cases.
**Warning signs:** No negative-path unit tests for the parser.

## Code Examples

### DISP-01 write-detector visitor sketch (mirror SAFE-03 visitor structure)
```python
# Pattern-source: tools/check_devtest_orchestrator.py:182-245 (adapt visit_* for writes)
import ast

class _SupportStatusWriteVisitor(ast.NodeVisitor):
    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.violations: list[str] = []

    def _is_support_status_target(self, target: ast.expr) -> bool:
        # x.support_status = ...   OR   x["support_status"] = ...
        if isinstance(target, ast.Attribute) and target.attr == "support_status":
            return True
        if (isinstance(target, ast.Subscript)
                and isinstance(target.slice, ast.Constant)
                and target.slice.value == "support_status"):
            return True
        return False

    def visit_Assign(self, node: ast.Assign) -> None:
        for t in node.targets:
            if self._is_support_status_target(t):
                self.violations.append(
                    f"{self.filename}:{node.lineno}: writes support_status "
                    "in the report/parse path (DISP-01: only build_db.py may write it)"
                )
        self.generic_visit(node)
```

### Parser detection + JSON extraction sketch (stdlib)
```python
# Pattern-source: submit.py fenced-block handling + diagnostic_report.to_json_block()
import json, re

_FENCE = re.compile(r"```json\s*\n(.*?)\n```", re.DOTALL)

def parse_devtest_body(title: str, body: str) -> dict | None:
    if "[dev test]" not in title:
        return None
    m = _FENCE.search(body)
    if not m:
        return None
    try:
        obj = json.loads(m.group(1))
    except json.JSONDecodeError:
        return None
    if "schema_version" not in obj:   # D-04 detection marker
        return None
    return obj
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Interactive tester-provenance prompts before the sweep (RPT-04, old D-04/05/06) | Auto-capture only; zero provenance prompts; `is_submittable` derived from auto-capture completeness | Phase 112 Plan 04 (operator-approved, 112-UAT.md) | The design note `dev-test-design-decisions.md` §"Must-ask the tester" is HISTORICAL — do not resurrect prompts. The parser/report deal only in auto-captured fields. |
| Legacy `mem_type`/`type` dispatch axis | Protocol-only dispatch | v1.20 (Phases 105-107) | Not directly in Phase 114 scope, but the report's `protocol` field is the post-v1.20 dispatch key. |

**Deprecated/outdated:**
- Provenance-prompt collector, human-input dataclass, enumerated choice constants in `diagnostic_report.py`: DELETED in Phase 112 Plan 04. Do not reference.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | SAFE-04 (absent-chip hard-fail), mapped to Phase 114 in REQUIREMENTS.md traceability, is NOT in this phase's CONTEXT scope and should be reconciled by the planner. | User Constraints / Deferred | If SAFE-04 is meant to ship here, the plan would omit a required item. LOW-MEDIUM — CONTEXT is authoritative for scope; flag it. |
| A2 | `community-confirmed` is not yet a string in the codebase and GRAD-01 introduces it as the human-gated target state. | Grounded Findings | LOW — verified by grep; if a hidden reference exists, formalization still applies. |
| A3 | The gsd-inbox integration is achieved by documenting a maintainer-invoked CLI (not any editable workflow hook), because inbox.md must not be edited and no project-local override mechanism was found. | INBOX-01 Design | LOW-MEDIUM — if a supported project-local inbox-extension seam exists, a cleaner hook is possible; none observed in the installed workflow/command. |

## Open Questions

1. **Should SAFE-04 be implemented in Phase 114?**
   - What we know: REQUIREMENTS.md traceability maps SAFE-04 → Phase 114 (added mid-milestone 2026-07-03). CONTEXT.md scopes Phase 114 to DISP-01/GRAD-01/INBOX-01 only.
   - What's unclear: whether SAFE-04 is expected in this phase's plan or tracked as separate handler-hardening.
   - Recommendation: planner asks the operator, or explicitly defers SAFE-04 with a note; do not silently absorb it into DISP-01/GRAD-01/INBOX-01 work.

2. **`ladder_state` field vs. prose-only?**
   - What we know: D-01/D-02 allow either; the parser is simpler with an explicit field.
   - What's unclear: operator preference on report-schema surface area (adds a `schema_version` bump consideration).
   - Recommendation: add a derived `ladder_state` string to `DbDiff`/`to_dict()`; if it changes the JSON shape, bump `SCHEMA_VERSION` and update the parser's accepted versions.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.9+ (`ast`/`json`/`re` stdlib) | DISP-01 checker + parser | ✓ | 3.11 in CI, 3.12 devcontainer | — |
| `pytest` (+`pytest-cov`) | Gate + unit tests | ✓ | >=8.0 dev | — |
| `gh` CLI | Optional live N-count in triage | optional | — | Saved-JSON fixtures / `--body-file`; parser must not require `gh`. |
| `rich` | Optional DB-diff table render | ✓ | existing dep | Plain-text print. |

**Missing dependencies with no fallback:** None.
**Missing dependencies with fallback:** `gh` — the parser and all its unit tests must work from saved JSON bodies without `gh` (bench-free, per the milestone discipline).

## Validation Architecture

> nyquist_validation not disabled in config → included.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | `pytest` >=8.0 (+ `pytest-cov` >=7.1) |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` |
| Quick run command | `cd firestarter_app && pytest tests/test_check_no_community_support_status_write.py tests/test_parse_devtest_issue.py -x` |
| Full suite command | `cd firestarter_app && pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| DISP-01 | Checker exits 0 on real source (no community write in report/parse path) | unit (subprocess) | `pytest tests/test_check_no_community_support_status_write.py::test_checker_exits_zero_on_clean_source -x` | ❌ Wave 0 |
| DISP-01 | Planted `support_status="community-reported"` write flips checker to non-zero (anti-hollow) | unit (subprocess) | `pytest tests/test_check_no_community_support_status_write.py::test_checker_exits_nonzero_on_planted_write -x` | ❌ Wave 0 |
| DISP-01 | Clean fixture through env-override still passes (seam isolation) | unit (subprocess) | `pytest tests/test_check_no_community_support_status_write.py::test_clean_fixture_env_override_passes -x` | ❌ Wave 0 |
| DISP-01 | PASS line names each scanned file (anti-skip) | unit | `pytest tests/test_check_no_community_support_status_write.py::test_pass_line_names_scanned_files -x` | ❌ Wave 0 |
| GRAD-01 | `build_db_diff` maps verdicts → correct ladder-state tag (community-reported / community-fail / inconclusive / no-change) | unit | `pytest tests/test_diagnostic_report.py -k ladder -x` | ⚠️ extend existing `tests/test_diagnostic_report.py` |
| GRAD-01 | Two reports with identical outcome shape produce matching `dedup_fingerprint` (N≥2 agreement key) | unit | `pytest tests/test_diagnostic_report.py::test_dedup_fingerprint_deterministic_same_shape -x` | ✅ exists (L210) |
| GRAD-01 | No community-* value is ever assigned to a DB-bound `support_status` | covered by DISP-01 gate | (see DISP-01) | ❌ Wave 0 |
| INBOX-01 | Detects a `dev test` issue via `[dev test]` title + fenced-JSON `schema_version`; rejects non-matching bodies | unit (saved-JSON fixtures) | `pytest tests/test_parse_devtest_issue.py -k detect -x` | ❌ Wave 0 |
| INBOX-01 | Emits current-vs-proposed DB-diff from the embedded JSON | unit | `pytest tests/test_parse_devtest_issue.py -k db_diff -x` | ❌ Wave 0 |
| INBOX-01 | Counts matching `dedup_fingerprint` across N issue bodies → "N agreeing" | unit | `pytest tests/test_parse_devtest_issue.py -k agreeing -x` | ❌ Wave 0 |
| INBOX-01 | Malformed / oversized / missing-JSON body handled without crashing | unit (negative) | `pytest tests/test_parse_devtest_issue.py -k malformed -x` | ❌ Wave 0 |
| GRAD-01/docs | Taxonomy doc exists and documents the four states + N≥2 process | presence/manual | `test -f firestarter_app/doc/community-validation.md` + review | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** the quick run command (the two new test files).
- **Per wave merge:** full suite `pytest tests/ --cov-fail-under=70` + `ruff check` + `ruff format --check` + `python tools/check_mypy_watermark.py`.
- **Phase gate:** full suite green before `/gsd-verify-work`. Note the 3 known-RED environment artifacts on a live-board bench session (`test_no_programmer_found_read/erase`, `test_audit_coverage_matrix` golden) are pre-existing and not this phase's regressions.

### Wave 0 Gaps
- [ ] `tools/check_no_community_support_status_write.py` — the DISP-01 checker (new).
- [ ] `tests/test_check_no_community_support_status_write.py` — clean-baseline + planted-violation + seam-isolation + anti-skip (covers DISP-01).
- [ ] `tools/parse_devtest_issue.py` — the INBOX-01 stdlib parser (new).
- [ ] `tests/test_parse_devtest_issue.py` — detection, DB-diff, N-agreeing, malformed-body cases (covers INBOX-01); needs saved-JSON fixtures (reuse a real `to_dict()` output as a fixture).
- [ ] Extend `tests/test_diagnostic_report.py` — ladder-state derivation cases (covers GRAD-01).
- [ ] `firestarter_app/doc/community-validation.md` — taxonomy + N≥2 process (covers GRAD-01 docs).

## Security Domain

> security_enforcement not disabled in config → included. This phase parses **untrusted, attacker-controllable GitHub issue bodies**, so input validation is a genuine (V5) concern.

### Applicable ASVS Categories
| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | No auth surface; `gh` handles its own auth. |
| V3 Session Management | no | No sessions. |
| V4 Access Control | yes (design invariant) | The no-auto-graduate lock IS an access-control invariant: a community report has zero authority to change project claims. Enforced by DISP-01 (D-02 + AST gate). |
| V5 Input Validation | **yes** | Parser must defensively `json.loads` (catch `JSONDecodeError`), bound body/JSON size, treat all fields as inert data, never `eval`/`exec`, never shell-interpolate body content. `submit.py` already scrubs PII on the outbound side; the inbound parser validates on the way in. |
| V6 Cryptography | no | `dedup_fingerprint` uses `sha256` as a non-secret distribution function only (explicitly "not a security control", `diagnostic_report.py:183-189`) — do not re-purpose it as one. |

### Known Threat Patterns for this stack
| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Malicious/oversized issue JSON crashes or mis-drives triage | Denial of Service / Tampering | Defensive parse, size bounds, negative-path tests; parser fails soft (returns `None`/skips), never raises to the caller. |
| A community report auto-promotes a chip (spoofed authority) | Elevation of Privilege | D-02 (report-side only) + DISP-01 AST gate: no code path writes `support_status` from a report; promotion is a manual human `build_db.py` edit. |
| Community-* value leaks into the DB and silently disables a chip | Tampering | Read guards refuse `!= "supported"`; DISP-01 gate backstops; `check_dispatch.py` iterates the DB and stays green because community-* never enters it. |
| Body content injected into a shell during triage | Tampering / EoP | Parser treats body as data; if any `gh` shell-out is added, use argv lists (never `shell=True`) — mirror `submit.py`'s `subprocess.run([...])` + no-`shell` discipline (T-113-01). |

## Sources

### Primary (HIGH confidence)
- `firestarter_app/firestarter/diagnostic_report.py` — DbDiff, build_db_diff, dedup_fingerprint, SCHEMA_VERSION, to_dict/to_json_block, `_DISPOSITION_*` prose (read in full).
- `firestarter_app/firestarter/submit.py` — SUBMIT_REPO, build_title, build_issue_url (the L183 hand-off), gh/browser tiers (read in full).
- `firestarter_app/tools/check_devtest_orchestrator.py` + `firestarter_app/tests/test_check_devtest_orchestrator.py` — the SAFE-03 checker + anti-hollow pattern (read in full).
- `firestarter_app/firestarter/chip_resolver.py` — the `!= "supported"` read guard (L54-57).
- `firestarter_app/tools/build_db.py` — the sole `support_status` write locus (L491-714).
- `firestarter_app/tools/check_dispatch.py` — the DB-iterating CI gate (L242+).
- `firestarter_app/firestarter/eprom_info.py` — the display-dict `support_status` copy (L148-150) that the audit must not false-positive on.
- `.claude/gsd-core/workflows/inbox.md` + `.claude/commands/gsd-inbox.md` — triage workflow + entry (read in full).
- `firestarter_app/.github/workflows/ci.yml` + `pyproject.toml` — the gate runs via `pytest tests/`, not a dedicated CI step (verified by grep: checkers never named in ci.yml).
- `.planning/phases/114-.../114-CONTEXT.md`, `.planning/REQUIREMENTS.md`, `.planning/notes/dev-test-design-decisions.md` — scope, requirements, design rationale.
- Grep: `support_status` across `firestarter/` + `tools/` (full write-site inventory).

### Secondary (MEDIUM confidence)
- None required — all claims verified against source this session.

### Tertiary (LOW confidence)
- SAFE-04 scope reconciliation (A1) — inferred from a REQUIREMENTS/CONTEXT mismatch; flagged as an open question.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — stdlib-only, forbidden-new-deps rule verified in REQUIREMENTS.md, dev deps read from `pyproject.toml`.
- Architecture: HIGH — every seam (DbDiff, dedup_fingerprint, to_dict, SAFE-03 checker, read guard, write locus, inbox workflow) read directly.
- Pitfalls: HIGH — each grounded in a specific line (eprom_info false-positive, CI-via-pytest, hollow-gate lesson, read-guard footgun).

**Research date:** 2026-07-03
**Valid until:** 2026-08-02 (stable — internal codebase, no fast-moving external deps; re-check if `diagnostic_report.py` or the SAFE-03 checker is refactored before planning).
