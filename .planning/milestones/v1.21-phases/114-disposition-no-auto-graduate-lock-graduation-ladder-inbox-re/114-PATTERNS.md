# Phase 114: Disposition / No-Auto-Graduate Lock + Graduation Ladder + Inbox Reconciliation - Pattern Map

**Mapped:** 2026-07-03
**Files analyzed:** 6 (2 new tools, 2 new tests, 1 modified module, 1 new doc)
**Analogs found:** 6 / 6

> All code lives in the `firestarter_app/` submodule (branch `v1.21-community-chip-validation-command`). Firmware untouched. RESEARCH.md already carries most grounded excerpts with `file:line` — this file is the file→analog mapping the planner consumes; excerpts below are the load-bearing anchors, not a re-derivation.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `tools/check_no_community_support_status_write.py` **(NEW, DISP-01)** | utility (AST gate) | transform (source→verdict) | `tools/check_devtest_orchestrator.py` | exact (sibling checker) |
| `tests/test_check_no_community_support_status_write.py` **(NEW, DISP-01)** | test (anti-hollow) | request-response (subprocess) | `tests/test_check_devtest_orchestrator.py` | exact |
| `tools/parse_devtest_issue.py` **(NEW, INBOX-01)** | utility (stdlib CLI parser) | transform (issue body→DB-diff + N-count) | `tools/diff_db.py` (CLI shape) + `firestarter/submit.py` (fenced-JSON/`dedup_fingerprint`) | role-match |
| `tests/test_parse_devtest_issue.py` **(NEW, INBOX-01)** | test (units + negative) | request-response | `tests/test_diagnostic_report.py` (fixture style) | role-match |
| `firestarter/diagnostic_report.py` **(MODIFY, GRAD-01)** | model (report) | transform (verdicts→ladder-state) | itself — extend `DbDiff`/`build_db_diff`/`to_dict` in place | self (extend) |
| `doc/community-validation.md` **(NEW, GRAD-01 docs)** | config/docs | n/a | `doc/protocol-id.md`, `doc/infoic-field-dictionary.md` | role-match (established `doc/` locus) |

## Pattern Assignments

### `tools/check_no_community_support_status_write.py` (utility, AST gate — DISP-01)

**Analog:** `tools/check_devtest_orchestrator.py` (mirror precisely — this is the SAFE-03 template D-05 mandates). 431 lines, read in full via grep this session.

**Env-override fixture-injection seam** (lines 80-114) — copy this idiom, rename to `FIRESTARTER_DISP01_*`, scope targets to the report/parse path (`diagnostic_report.py`, the new `tools/parse_devtest_issue.py`, any new ladder module). Do NOT scan `build_db.py` (allowed write locus) or `eprom_info.py` (display-dict copy — Pitfall 1):
```python
_HERE = os.path.dirname(__file__)
_DEFAULT_CHIP_TEST = os.path.join(_HERE, "..", "firestarter", "chip_test.py")
FIRESTARTER_DEVTEST_SRC = os.environ.get("FIRESTARTER_DEVTEST_SRC", _DEFAULT_CHIP_TEST)
```

**Visitor structure** (lines 182-246, `_OrchestratorDenyVisitor(ast.NodeVisitor)` with `visit_Call`/`visit_Dict`/`visit_Constant`, `frozenset` deny-vocab constants at 126/145/162). For DISP-01 swap the deny concept to *writes*: `visit_Assign`/`visit_AnnAssign` where the target is `support_status` (an `ast.Attribute.attr == "support_status"` OR a subscript `x["support_status"] = ...`). Sketch already in RESEARCH.md §"DISP-01 write-detector visitor sketch".

**Fail-closed empty-scan guard** (lines 397-403) — the anti-hollow backstop; copy verbatim (rename the message):
```python
if not scanned:
    print("FAIL: no orchestrator source files found to scan ...")
    sys.exit(1)
```

**Host-only guard + exit discipline** (`_assert_host_only` L307-322 rejects any path resolving into the firmware sub-repo; PASS line names every scanned file at L425, `sys.exit(1)` on violations at L422). Keep both — the "PASS names files" line is what the anti-skip test asserts.

---

### `tests/test_check_no_community_support_status_write.py` (test, anti-hollow — DISP-01)

**Analog:** `tests/test_check_devtest_orchestrator.py` (370 lines). Copy the whole harness shape.

**Subprocess harness** (lines 46-65):
```python
_FA_DIR = Path(__file__).parent.parent
def _run_checker(env_overrides=None):
    env = {**os.environ, **(env_overrides or {})}
    return subprocess.run([sys.executable, "tools/check_no_community_support_status_write.py"],
                          cwd=str(_FA_DIR), capture_output=True, text=True, env=env)
```

**Required test quartet** (mirror L67-186):
- `test_..._exits_zero_on_clean_source` — real source, `returncode == 0`, `"PASS:" in stdout` (L67-78).
- `test_..._exits_nonzero_on_planted_write` — `tmp_path` fixture writing `chip["support_status"] = "community-reported"`, injected via env-override → `returncode != 0`, `"FAIL:" in stdout` (mirror L87-106).
- `test_env_override_points_at_a_clean_fixture_still_passes` — seam-isolation, exit 0 (L173-186).
- `test_pass_line_names_scanned_files` — anti-skip assertion (the v1.12 hollow-GATE-03 lesson).

---

### `tools/parse_devtest_issue.py` (utility, stdlib CLI parser — INBOX-01)

**Analogs:**
- **CLI shape:** `tools/diff_db.py` / `tools/build_db.py` (argparse, stdlib-only `tools/` script conventions; survives `gsd update` per D-04).
- **Fenced-JSON + dedup key:** `firestarter/submit.py` and `firestarter/diagnostic_report.py`.

**Detection markers** (D-04): `[dev test]` title marker + fenced-JSON `schema_version` (NOT labels). Title marker produced by `submit.py:build_title` (`firestarter/submit.py:141-151`); `SUBMIT_REPO = "henols/firestarter_app"` at `submit.py:53`. Detection sketch already in RESEARCH.md §"Parser detection + JSON extraction sketch" (`_FENCE = re.compile(r"```json\s*\n(.*?)\n```", re.DOTALL)`).

**The JSON shape it consumes:** `DiagnosticReport.to_dict()` (`diagnostic_report.py:380-398`) → `schema_version` (marker), `db_diff` (`current_support_status`/`proposed_disposition`), `dedup_fingerprint`. `to_json_block()` (L476-478) is the exact fence written into the issue.

**N-agreeing (D-03):** reuse `dedup_fingerprint(report)` (`diagnostic_report.py:171-196`) — read `to_dict()["dedup_fingerprint"]` from each of several issue bodies, group, count matches. Do NOT hand-roll a new hash; do NOT conflate with Phase-108 per-run N≥2 (Pitfall 5).

**Untrusted-input discipline (V5):** defensive `json.loads` (catch `JSONDecodeError`, return `None`), size-bound, no `eval`/`exec`, no `shell=True` — mirror `submit.py`'s argv-list `subprocess.run([...])` discipline.

---

### `tests/test_parse_devtest_issue.py` (test, units + negative — INBOX-01)

**Analog:** `tests/test_diagnostic_report.py` (existing fixture style; `dedup_fingerprint` determinism test at L210). Build saved-JSON fixtures by reusing a real `to_dict()` output. Required cases (RESEARCH Test Map): detect (title+`schema_version`), db_diff surface, N-agreeing count, malformed/oversized/missing-JSON negative path. Must run without `gh` (bench-free).

---

### `firestarter/diagnostic_report.py` (model — GRAD-01, MODIFY in place)

**Analog:** itself — this is Pattern 3 (single-source report model). Never add a second field list.

**Ladder-state names already present as prose** (L206-211): `_DISPOSITION_COMMUNITY_FAIL`, `_DISPOSITION_CANDIDATE` ("community-reported"), `_DISPOSITION_INCONCLUSIVE`, `_DISPOSITION_NO_CHANGE`. `community-confirmed` is NOT yet a string — GRAD-01 introduces it as the human-gated target (never auto-assigned).

**Extend `build_db_diff(name, db, results)`** (L230-260) — the verdict→disposition mapper; add the derived report-side `ladder_state` here. **Extend `DbDiff`** (L214-227, fields `current_support_status`/`proposed_disposition`; docstring: "NEVER writes it back to the database" — preserve that invariant, D-02). **Add the field once to `to_dict()`** (L386-404) so both `render()` and `to_json_block()` pick it up. If the JSON shape changes, bump `SCHEMA_VERSION` (L55) and update the parser's accepted versions (Open Question 2).

**Hard constraint:** report-side only. No `support_status` write anywhere here — the DISP-01 gate scans this module.

---

### `doc/community-validation.md` (docs — GRAD-01)

**Analog:** `doc/protocol-id.md`, `doc/infoic-field-dictionary.md` (established operator-canonical `doc/` locus). Document: the four ladder states, the auto-tag derivation (`community-reported`/`community-fail` from sweep verdicts), the N≥2-via-`dedup_fingerprint` cross-report promotion criterion (distinct from Phase-108 per-run N≥2), and the manual promotion process (maintainer edits `build_db.py` → `support_status="supported"` — the sole write locus).

## Shared Patterns

### Anti-hollow gate (AST checker + planted-fixture subprocess test)
**Source:** `tools/check_devtest_orchestrator.py` + `tests/test_check_devtest_orchestrator.py`
**Apply to:** DISP-01 checker + its test. Fail-closed on empty scan (checker L397-403); ship a planted-violation fixture and a PASS-line-names-file assertion. Wire ONLY via pytest — NO CI YAML step (Pitfall 2; checkers are never named in `ci.yml`, they run under `pytest tests/ --cov-fail-under=70`).

### Single-source report model
**Source:** `firestarter/diagnostic_report.py:380` (`to_dict()`)
**Apply to:** any GRAD-01 field addition — add once to `to_dict()`, both renders inherit it.

### `dedup_fingerprint` as the sole agreement key
**Source:** `firestarter/diagnostic_report.py:171-196`
**Apply to:** the parser's N-agreeing count (D-03). Reuse; never re-hash.

### Read-guard invariant (why D-02 exists)
**Source:** `firestarter/chip_resolver.py:54-57` (`support_status != "supported"` → `ChipNotImplementedError`)
**Apply to:** all GRAD-01 work — community-* must never reach `chip_database.json`, or it silently disables the chip. The DISP-01 gate is the machine backstop.

### Allowed write locus (DISP-01 allow-list)
**Source:** `tools/build_db.py:714` (`"support_status": _support_status`, values at L491/510/544/603/682) — the ONLY persistent write. Human-authored, unchanged. The DISP-01 audit must exclude this and `eprom_info.py:150` (display-dict copy, Pitfall 1).

## No Analog Found

None — every Phase 114 artifact has a strong existing analog. This phase is composition/formalization of Phases 108-113 code.

## Planner Flags (from RESEARCH, not pattern-mapping)

- **SAFE-04** (absent-chip hard-fail) is mapped to Phase 114 in REQUIREMENTS.md traceability but is OUT of CONTEXT scope (DISP-01/GRAD-01/INBOX-01 only). Reconcile explicitly — do not silently absorb (RESEARCH A1 / Open Question 1).
- **`ladder_state` field vs prose-only** is discretionary (D-01/D-02); RESEARCH recommends a derived `ladder_state` string on `DbDiff`/`to_dict()` (Open Question 2) — bump `SCHEMA_VERSION` if the shape changes.
- **`submit.py:183` labeling hand-off** is discretionary; if picked up it is a maintainer-side `gh` action only, never a community capability.

## Metadata

**Analog search scope:** `firestarter_app/tools/`, `firestarter_app/tests/`, `firestarter_app/firestarter/`, `firestarter_app/doc/`
**Files scanned this session:** tools listing, `check_devtest_orchestrator.py` (grep-mapped), `test_check_devtest_orchestrator.py` (grep-mapped), plus RESEARCH.md's full in-file reads of `diagnostic_report.py`, `submit.py`, `chip_resolver.py`, `build_db.py`, `check_dispatch.py`, `eprom_info.py`.
**Pattern extraction date:** 2026-07-03
