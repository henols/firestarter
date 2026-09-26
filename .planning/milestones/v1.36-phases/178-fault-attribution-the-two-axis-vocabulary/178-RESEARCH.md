# Phase 178: Fault Attribution — the Two-Axis Vocabulary - Research

**Researched:** 2026-09-06
**Domain:** Host-side Python (`firestarter_app/`) — diagnostic report vocabulary, dedup-hash invariance, verdict-keyed control flow
**Confidence:** HIGH (every path, symbol and line citation below was opened with `Read`/`sed` this session on branch `gsd/v1.36-dev-test-fidelity` @ `0a29d8b`)

**No CONTEXT.md exists for this phase.** The contract is the ROADMAP goal + the five success criteria + ATTR-01..06 verbatim. Where a choice is open (the name of the status field, which existing `verdict` a transport fault carries) this document names candidates and the consequences of each, and marks the choice as the planner's / operator's to make.

---

## Summary

`dev test` today has exactly **one** verdict axis with **five** values, and the transport-fault handler at `firestarter/chip_test.py:2524-2541` is forced to spend `VERDICT_BAD` — a chip verdict — on "a half-seated cable", which its own comment says out loud. Phase 178 adds a second, orthogonal **status** axis and re-points that handler.

The good news, and the single most important finding for the planner: **`dedup_fingerprint` is a positive allow-list, not a reflection over fields.** It builds a `parts` list by explicit `append` (`firestarter/diagnostic_report.py:272-300`) and hashes `"|".join(parts)`. A new field is excluded by *not writing an append for it* — exclusion is the default, and ATTR-04 is satisfied by construction rather than by a suppression rule. Phase 174 already seeded the confirmation anchor: ledger row `RK-174-09-p178-status-axis-must-not-rekey-reanchored` (`firestarter_app/tests/fixtures/rekey_ledger.py:174-179`) pins `sst27sf512-full-all-ok` at `14d306256076` with `after_hash=None`, and Phase 178 confirms ATTR-04 by leaving that `None` and the gate green.

The hard news, and the thing that will decide whether this phase ships correctly: **moving the transport-fault step off `VERDICT_BAD` silently changes four verdict-keyed control decisions, one of which is a safety gate.** `_id_step_closes_gate` (`chip_test.py:1930-1941`) closes the destructive gate only on `(VERDICT_BAD, VERDICT_SKIPPED)`. If a transport fault on the `id` step becomes `marginal` or `NA`, the gate **stays open** and a write proceeds against a chip whose identity was never confirmed. There is a shipped test (`tests/test_dev_test_cmd.py:2014-2037`) that exists precisely to prove that gate closes on this path; it will go RED and must be *repaired forward*, never relaxed.

**Primary recommendation:** add a `status` field (OCP `TestStatus` vocabulary: `COMPLETE` / `ERROR` / `SKIP`) as an additive `StepResult` field plus a derived top-level `run_status` on `DiagnosticReport`; re-point the `(SerialError, HardwareOperationError)` arm to `verdict=VERDICT_SKIPPED, status=ERROR` (SKIPPED is the only existing value that keeps `_id_step_closes_gate` closed and keeps the run out of `_RAN_VERDICTS`); widen `build_db_diff` and `submit.overall_verdict` to read the status axis *first*; and never touch `is_submittable`.

---

## User Constraints

No `178-CONTEXT.md` exists. The binding constraints are:

### Locked (from REQUIREMENTS.md lines 67-72, verbatim)

- **ATTR-01**: A run carries a **status** axis (did the run execute validly) separate from the **result** axis (the verdict on the part), following the OCP Test & Validation two-axis model.
- **ATTR-02**: A step that failed for a tool or transport reason is not reported as a chip verdict.
- **ATTR-03**: The overall verdict and the filed issue title reflect the status axis — a run that did not execute validly does not file as `[dev test] <chip> — FAIL`.
- **ATTR-04**: **No sixth `verdict` value is introduced.** The status axis is a separate additive field kept out of the dedup hash — a cardinality change inside `op=verdict:cls` would re-key every group that hits it.
- **ATTR-05**: Auto-classification never suppresses the submit prompt. It changes the title and disposition only; the offer to file always stands.
- **ATTR-06**: The report states what a rail reading does **not** prove. `sample_vpp_mv` → `hw_read_voltage` sets `CTRL_VPP_REGULATOR_ENABLE` and no socket-routing bits, so a rig with VPP unhooked still reads a healthy `vpp_before_mv: 11800`. No requirement here may claim to detect that fault.

### Out of scope (deferred, cited by this phase)

- **RIG-01** (`REQUIREMENTS.md:127`): a rig-sanity leg proving the socket is connected. Deferred *because of* ATTR-06. Phase 178 must not re-open it.
- Replying to / closing gh#21, #23, #28, #31, #45, #50 — milestone-level Out of Scope.
- `.claude/skills/devtest-triage/SKILL.md` updates — **Phase 181 criterion 2 owns them.**
- `SCHEMA_VERSION` → `2.0` — **Phase 181 owns it** (RPT-E1 / D-3). See Open Question 3 for the 1.7-vs-1.8 question this phase raises.

---

## Project Constraints (from CLAUDE.md)

| Directive | Source | Consequence for this phase |
|---|---|---|
| **NO comments in source, at all** — hard rule, a plan cannot override | operator memory `feedback_never_put_gsd_provenance_comments_in_source.md`, broadened 2026-08-29 | Every rationale this phase adds goes in a **docstring**, never a `#` comment. This matches 177-PATTERNS.md §"Rationale goes in a docstring, never a comment". Existing comments in `chip_test.py` are pre-existing and are not this phase's to sweep. |
| Serial-protocol / constants dual-repo lockstep | `/workspaces/CLAUDE.md` | **Not triggered.** This is host-only; no wire field, no firmware constant changes. |
| Tooling gate: `ruff check` + `ruff format --check` + mypy watermark + `pytest --cov-fail-under=70` | `firestarter_app/CLAUDE.md` §Tooling gate; `.github/workflows/ci.yml:80-87` | All four must stay green. mypy watermark is **35** (measured, see Environment Availability). |
| mypy strict-island includes `cli_handlers.py` | `firestarter_app/CLAUDE.md`; `pyproject.toml` overrides | New helpers in `cli_handlers.py` need full annotations. `chip_test.py`, `diagnostic_report.py`, `submit.py` are **not** strict islands. |
| `chip_database.json` is GENERATED — never hand-edit | `firestarter_app/CLAUDE.md` | Not triggered. |
| Devcontainer default py3.12 masks CI (py3.11) | operator memory `reference_devcontainer_py312_masks_ci_py39.md` | **Every** verify command below uses `./.venv311/bin/python`. |
| `grep` in this devcontainer is ugrep and honors `.gitignore` | operator memory | Every evidence-grade scan in this document used `/usr/bin/grep`. Verify commands in the plan must too. |

**Project skills present:** `.claude/skills/devtest-triage/`, `.claude/skills/devtest-rootcause/`, `find-skills`, `skill-creator`. No `rules/*.md` directory exists. The two devtest skills are *consumers* of the report format — see "Downstream consumers" below.

---

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| ATTR-01 | Status axis separate from result axis, OCP model | §1 (the five existing verdicts, all assignment + all read sites), §10 (OCP `TestStatus` vocabulary verbatim, candidate field names) |
| ATTR-02 | A tool/transport failure is not a chip verdict | §1 (the exact handler, `chip_test.py:2524-2541`), §6 (what distinguishes transport from chip), §11 (the four verdict-keyed decisions that break when the verdict moves) |
| ATTR-03 | Overall verdict + issue title reflect the status axis | §4 (`submit.overall_verdict:140-153`, `build_title:156-168`), §11 (exit-code map) |
| ATTR-04 | No sixth verdict; status axis out of the dedup hash | §2 (the exact `parts` allow-list), §3 (the Phase-174 oracle, the `RK-174-09` anchor, the five-registry shape-registration cost) |
| ATTR-05 | Auto-classification never suppresses the submit prompt | §5 (every existing suppressor in `submit_report`), **Finding F-1** (the milestone research's T3 contradicts ATTR-05 — ATTR-05 wins) |
| ATTR-06 | State what a rail reading does not prove | §8 (firmware source read; **the requirement's own wording is incomplete — correction C-1**), the render site for the sentence |

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|---|---|---|---|
| Detecting a transport fault | `chip_test.py` engine (exception arm) | `transport_counters.py` sink | The exception is raised inside `_dispatch_step`; the counters are a *corroborating* signal, never the trigger |
| Naming the status-axis value | `chip_test.py` (`StepResult` + constants) | — | The verdict vocabulary already lives there (`:935-939`); a second module owning the sibling axis would let the two drift |
| Folding step statuses into a run status | `diagnostic_report.py` (derived, like `_is_transport_suspect`) | — | `DiagnosticReport` already owns every derived report-level value; `dedup_fingerprint` lives in the same module and must be able to *not* read it |
| Title + disposition | `submit.py` (`overall_verdict`, `build_title`) and `diagnostic_report.build_db_diff` | — | These are the two ATTR-03/ATTR-05 surfaces and they are already separate from the engine |
| Exit code | `cli_handlers.py` (`_VERDICT_EXIT_CODES`, `_dev_test_exit_code`) | — | Already the sole exit-code authority |
| The ATTR-06 sentence | `diagnostic_report.py` (`render()` + `to_dict()`) | — | It must land in the actual report output, not a docstring; `render()` is where the `vpp (before/after)` row is emitted |

---

## §1 — The `verdict` axis as it exists today

### The five values, verbatim

`firestarter/chip_test.py:934-939` [VERIFIED: firestarter/chip_test.py:934-939]

```python
# onto read-step disagreement.
VERDICT_OK = "OK"
VERDICT_BAD = "BAD"
VERDICT_NA = "NA"
VERDICT_SKIPPED = "SKIPPED"
VERDICT_MARGINAL = "marginal"
```

Note the casing asymmetry: four are UPPERCASE, `VERDICT_MARGINAL` is lowercase `"marginal"`. Any new constant must not "fix" that — the four literals are in `dedup_fingerprint`'s pre-image and in seventeen frozen hashes.

The docstring above them reads `# Verdict vocabulary. `MARGINAL` is destructive/verify-only -- never forced onto read-step disagreement.` (`chip_test.py:933-934`).

`StepResult.verdict`'s own contract, `chip_test.py:1070` [VERIFIED: firestarter/chip_test.py:1066-1103]:
> "`verdict` is one of OK/BAD/NA/SKIPPED/marginal."

### Every assignment site (measured, `/usr/bin/grep` over `firestarter/`)

| Site | Value | Meaning |
|---|---|---|
| `chip_test.py:1105-1106` `_skip_result` | `SKIPPED` (default), `NA` via kwarg | not-supported / gated |
| `chip_test.py:1356` `_aggregate_cycle_results` | `MARGINAL` | cycles disagreed |
| `chip_test.py:1692` | `BAD` | `runs < 2` fail-closed guard |
| `chip_test.py:2538` | **`BAD`** | **the ATTR-02 target: `(SerialError, HardwareOperationError)`** |
| `chip_test.py:2545` | `BAD` | `EpromOperationError` (a firmware finding — legitimately a chip verdict) |
| `chip_test.py:2604` | `OK`/`BAD` | blank-check |
| `chip_test.py:2661`, `:2682-2690` | `BAD`/`OK` | `_dispatch_id` |
| `chip_test.py:2734` | `OK`/`BAD` | `_dispatch_read` (last run's return) |
| `chip_test.py:3065`, `:3107`, `:3127` | `BAD`/`SKIPPED` | `_dispatch_multi_run` fail-closed + refusal arms |
| `chip_test.py:3215-3231` | `MARGINAL`/`OK`/`BAD` | `_dispatch_multi_run` verdict fold |
| `chip_test.py:3260`, `:3288`, `:3347` | `BAD`/`OK` | SDP dispatch arms |
| `chip_test.py:3434`, `:3479`, `:3510`, `:3534` | `BAD`/`MARGINAL` | SDP-leg read-back arms |

### The ATTR-02 target, verbatim

`firestarter/chip_test.py:2524-2541` [VERIFIED: firestarter/chip_test.py:2524-2541]:

```python
    except (SerialError, HardwareOperationError) as exc:
        # A half-seated cable or other transport-level fault
        # (SerialError itself, SerialTimeoutError, or HardwareOperationError
        # -- a sibling of Exception, not an EpromOperationError subclass, so
        # the existing `except EpromOperationError` clause below never
        # reaches it) degrades THIS ONE step to a recorded BAD result;
        # `run_plan` still returns a full report for every other step.
        # `error_code` is deliberately omitted: neither SerialError nor
        # HardwareOperationError carries that attribute -- only
        # EpromOperationError does -- so copying the existing handler
        # wholesale would raise AttributeError at the moment this handler is
        # supposed to be recovering.
        return StepResult(
            op=step.op,
            verdict=VERDICT_BAD,
            reason=str(exc),
            run_count=1,
        )
```

> **Stale citation, for the planner's awareness.** `REQUIREMENTS.md:64-65` and `.planning/research/FEATURES.md:59` both cite this as `chip_test.py:2461`. On the current branch line 2461 is a bare `runs: int,` parameter in `_run_step_untimed`'s signature. The live anchor is **2524-2541**. Fix the citation in the same commit that changes the code (project rule: repair `.planning/` `file:LINE` citations, never accept staleness).

### The escape hatch immediately above it

`chip_test.py:2504-2523` re-`raise`s `ProgrammerNotFoundError`, `FirmwareOutdatedError`, `HardwareRevisionUnsupportedError` — run-fatal host-setup conditions. Its docstring already states the reasoning this phase generalises: these "are run-fatal host-setup conditions ... not chip findings". **The project already built half a status axis by hand; it has only two settings — abort the run, or blame the chip.** gh#23's "VPP wasn't hooked up" falls in the gap. [CITED: .planning/research/FEATURES.md:60-66]

---

## §2 — `dedup_fingerprint` composition (ATTR-04's mechanism)

`firestarter/diagnostic_report.py:248-300` [VERIFIED: firestarter/diagnostic_report.py:248-300]. The hash input, verbatim:

```python
    ac = report.auto_capture
    parts = [ac.chip or "", str(ac.protocol or "")]
    for result in report.results:
        cls = result.fingerprint.classification if result.fingerprint else ""
        parts.append(f"{result.op}={result.verdict}:{cls}")
    ...
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

**The inclusion mechanism is an explicit `parts.append(...)` and nothing else.** There is no `dataclasses.fields()` walk, no `to_dict()` hash, no `__dict__` iteration. A field is in the hash if and only if a line appends it.

**Exactly five inputs, in order:**

1. `auto_capture.chip` (raw CLI token)
2. `str(auto_capture.protocol)` (the DB `algorithm`)
3. one `f"{op}={verdict}:{cls}"` triple per `StepResult`, in `results` order — `cls` is `fingerprint.classification` or `""`
4. `repeat_policy_tag(results)` — appended **only when non-empty**; the one non-default value is the literal `"runs=1"` (`chip_test.py:1120` `REPEAT_POLICY_DEGRADED_TAG = "runs=1"`)
5. `coverage_tag(results)` — appended **only when non-empty**

Serialization: `"|".join(parts)`, UTF-8, `sha256`, `[:12]` plain slice. The tracer pre-image is pinned literally at `tests/test_blast_radius_invariance.py:191-194` [VERIFIED: firestarter_app/tests/test_blast_radius_invariance.py:191-194]:

```python
_TRACER_CANONICAL = (
    "SST27SF512|7|id=OK:|read=OK:|write=OK:match|"
    "verify=OK:match|erase=OK:|blank-check=OK:"
)
```

**Already excluded** (stated in the function's own docstring, `:279-283`): timestamps, `host_version`, measured mV, `error_code`, free-text `reason`. Also excluded in fact: `duration_s` (`chip_test.py:1050-1052` says so, and `test_durations_do_not_perturb_dedup_fingerprint` at `tests/test_diagnostic_report.py:1698-1716` proves it), `run_count` (except through `repeat_policy_tag`), `write_target`/`write_coverage` (`diagnostic_report.py:760-766` says so explicitly), `divergence`, `transport_health`, `sdp_hold_state`, `banner`, `db_diff`, `schema_version`.

### What the planner must write

> **Add the status field to `StepResult` (and/or `DiagnosticReport`). Do not add a `parts.append` for it. That is the whole of ATTR-04.**

The op-registration-parity suite already declares `dedup_fingerprint` a **non-registry** — "generic over `StepResult.op` ... it hashes whatever op string each result carries without comparing it against any specific `OP_*` constant" (`tests/test_op_registration_parity.py:334-341`). That declaration is re-measured every run by an AST inversion guard (`test_non_registry_still_has_no_ops`), so adding op-shaped string literals to `diagnostic_report.py` would redden it. Status-axis constants are *verdict-shaped*, not op-shaped — the same category as `SDP_HOLD_HELD`/`NOT-HELD`/`NOT-RUN`, which `chip_test.py:1963-1967` explicitly warns "must never join `_ALL_OPS`/`_MULTIWORD_OP_VALUES`". **Follow that precedent exactly**, including the warning docstring.

**The one real re-key risk is not the field — it is the verdict.** If the transport-fault step's `verdict` moves from `BAD` to anything else, every *already-filed* report that carried a transport-faulted step re-keys. That is unavoidable and correct (it is the whole point of ATTR-02), but it is a **declared re-key** and none of the seventeen frozen shapes carries a transport-faulted step, so *no frozen hash moves*. Confirmed: the only shapes reaching the exception arm would be new ones.

---

## §3 — Phase 174's blast-radius invariance oracle

### What it is

**`firestarter_app/tests/test_blast_radius_invariance.py`** — a pytest module, 785 lines, not a standalone script. [VERIFIED: firestarter_app/tests/test_blast_radius_invariance.py]

**Invocation (verified to run this session):**

```bash
cd /workspaces/firestarter_app && ./.venv311/bin/python -m pytest \
  tests/test_blast_radius_invariance.py tests/test_rekey_ledger.py -o addopts="" -q
```

Observed output: `118 passed in 1.43s`.

There is also a **meta-repo cross-tree checker**, which is the *primary* runner per D-13:

```bash
cd /workspaces && python3 tools/rekey/check_rekey_ledger.py
```

Observed output: `OK: 8 ledger row(s), 8 MILESTONES.md row(s) bound` (exit 0). Registered CI leg: `/workspaces/.github/workflows/rekey-ledger-check.yml` (triggers on `beta` and `gsd/**`). [VERIFIED: /workspaces/.github/workflows/rekey-ledger-check.yml:1-45]

### The gates it enforces

| Gate | Test | What it pins |
|---|---|---|
| Absolute hash | `test_dedup_fingerprint_is_frozen` (`:256`), parametrized over `FROZEN_HASHES` | 17 shape ids → 12-hex literal |
| Pre-image | `test_dedup_fingerprint_truncation_is_a_plain_slice` (`:279`) | the tracer's exact canonical string |
| Schema key lists | `_TO_DICT_KEYS` (11), `_VOLTAGE_KEYS` (6), `_BANNER_KEYS` (3), `_AUTO_CAPTURE_KEYS` (8), `_TRANSPORT_HEALTH_KEYS` (9), `_DB_DIFF_KEYS` (3), `_STEPS_ELEMENT_0_KEYS` (13) | `:92-186` — **a new exported key moves one of these and the pin fails** |
| Ladder | `LADDER_PINS` (`:222-254`) + a four-distinct-arms sentinel | `(proposed_disposition, ladder_state)` per shape |
| Snapshot drift | `test_committed_snapshot_matches_a_fresh_regeneration` (`:590`) | `tests/fixtures/reports/<shape_id>.json` byte-compare |
| Five-way closure | `test_shape_ids_frozen_hashes_ladder_pins_and_snapshots_agree` (`:727`) | `SHAPE_IDS == FROZEN_HASHES == LADDER_PINS == snapshot stems` |
| Pinned id set | `test_shape_id_set_is_pinned_and_disjoint_from_reserved` (`:559`) | `_PINNED_SHAPE_ID_SET` (`:538-556`) and disjointness from `RESERVED_SHAPE_IDS` |

### The fixture corpus, and the reserved name Phase 178 owns

`tests/fixtures/report_shapes.py:683-688` [VERIFIED: firestarter_app/tests/fixtures/report_shapes.py:683-688]:

```python
RESERVED_SHAPE_IDS: frozenset[str] = frozenset(
    {
        "attr01-status-axis-transport-fault",
        "uv-slot-write-pass",
    }
)
```

**`attr01-status-axis-transport-fault` is Phase 178's, reserved by Phase 174 D-04.** Registering it costs **seven** coordinated edits (177-02-SUMMARY.md says "four registries"; that count omits `_PINNED_SHAPE_ID_SET` and the snapshot file — measured, both are required by tests at `:559` and `:727`):

1. `tests/fixtures/report_shapes.py` — a `_build_attr01_status_axis_transport_fault()` builder
2. `tests/fixtures/report_shapes.py` — `_BUILDERS` entry (`:641-658`)
3. `tests/fixtures/report_shapes.py` — `FROZEN_HASHES` entry (`:663-682`), **measured, never transcribed**
4. `tests/fixtures/report_shapes.py` — removal from `RESERVED_SHAPE_IDS` (`:683-688`)
5. `tests/test_blast_radius_invariance.py` — `LADDER_PINS` entry (`:222-254`)
6. `tests/test_blast_radius_invariance.py` — `_PINNED_SHAPE_ID_SET` entry (`:538-556`) **and** `tests/fixtures/shape_ids.json`
7. `tests/fixtures/reports/attr01-status-axis-transport-fault.json` — generated by `./.venv311/bin/python tools/snapshot_report_shapes.py --shape attr01-status-axis-transport-fault`

Builder helpers available: `build_shape_from_step_specs(chip=, protocol=, step_specs=[(op, verdict, cls, reason)], run_counts=, coverage_policy=)` (`:112-179`) for a hand-specified shape, or `_build_real_path_report(chip=, write_scope=, operator=, runs=)` (`:464-500`) which runs the real `derive_plan` + `run_plan`. A transport-fault shape is most honestly built **real-path with an operator double whose method raises `SerialError`** — that exercises the actual handler rather than hand-asserting its output. Note `build_shape_from_step_specs` currently has **no status parameter**; extending it is part of this phase.

### The ATTR-04 anchor, and what "confirmation" means

`tests/fixtures/rekey_ledger.py:174-179` [VERIFIED: firestarter_app/tests/fixtures/rekey_ledger.py:174-179]:

```python
    (
        "sst27sf512-full-all-ok",
        "14d306256076",
        None,
        "RK-174-09-p178-status-axis-must-not-rekey-reanchored",
    ),
```

`sst27sf512-full-all-ok` is a **real-path, all-OK, non-SDP** shape (`report_shapes.py:599-606`) — no transport fault, so its hash must not move.

> **Design trap the planner must not walk into.** Criterion 3 says the exclusion is "confirmed by Phase 174's oracle reporting zero unexpected hash changes **when the status axis is exercised**". An all-OK shape does not exercise the status axis. Leaving the seventeen frozen hashes green proves *nothing moved*; it does not prove *the status axis was excluded*. The honest confirmation is **two** legs:
> - **Leg A (invariance):** all 17 `FROZEN_HASHES` unchanged, `RK-174-09` still green with `after_hash=None`, `check_rekey_ledger.py` exit 0.
> - **Leg B (exclusion, non-vacuous):** a test in the `test_durations_do_not_perturb_dedup_fingerprint` idiom (`tests/test_diagnostic_report.py:1698-1716`) building **two reports identical except for their status-axis values** and asserting equal fingerprints. Without Leg B, Leg A passes vacuously through a change that never wired the field at all.

**The ledger row must stay `after_hash=None`.** `test_no_declared_row_has_after_hash_equal_to_before_hash` (`tests/test_rekey_ledger.py:332-340`) *forbids* declaring `after_hash == before_hash` — "a declared re-key that moved nothing is a bookkeeping error, not a re-key". `test_undeclared_after_hash_routes_to_before_hash_and_never_abstains` (`:358-380`) asserts an undeclared row's `before_hash` still reproduces from a fresh build, which **is** the confirmation. Phase 178 therefore confirms ATTR-04 by leaving the row alone and the gate green.

**`test_ledger_has_exactly_eight_rows_after_the_177_declaration` (`:297-310`) pins `len(LEDGER) == 8`.** If Phase 178 appends a row (it should not need to), that count and the test's docstring both move. `test_ledger_id_order_is_ascending` (`:385`) also constrains any append. Note `RK-174-08` does not exist — the sequence is 01-07, 09.

---

## §4 — The issue title

`firestarter/submit.py:140-168` [VERIFIED: firestarter_app/firestarter/submit.py:140-168]:

```python
def overall_verdict(results: Any) -> str:
    """FAIL-dominant title verdict -- NOT the handler's exit-code
    `max()` ordering (`cli_handlers.py`, where `marginal=2 > BAD=1`).

    `FAIL` if any step verdict is `BAD`; else `INCONCLUSIVE` if any is
    `marginal`; else `PASS`. Human-legible ordering for the issue title.
    """
    verdicts = {r.verdict for r in results}
    if "BAD" in verdicts:
        return "FAIL"
    if "marginal" in verdicts:
        return "INCONCLUSIVE"
    return "PASS"


def build_title(report: Any, chip: str) -> str:
    """`[dev test] <chip> — <PASS/FAIL/INCONCLUSIVE> (<shorthash>)`.
    ...
    """
    d = report.to_dict()
    shorthash = d["dedup_fingerprint"]
    verdict = overall_verdict(report.results)
    return f"[dev test] {chip} — {verdict} ({shorthash})"
```

**Exactly three title variants today:** `PASS`, `FAIL`, `INCONCLUSIVE`. The em-dash is U+2014. `overall_verdict` reads **bare string literals** `"BAD"` / `"marginal"`, not the `VERDICT_*` constants — the module imports only `VERDICT_NA` (`submit.py:48`).

**Where the title flows:** `build_title` is called once, at `submit.py:681` inside `submit_report`, and the result reaches `build_issue_url` (browser tier), `submit_via_gh` (the `gh issue create --title` argv), and `submit_via_browser`. `dev test` calls `submit_report` **unconditionally** on every run — `cli_handlers.py:2515-2519` says so verbatim: "Unconditional: every run reaches the filing ask, not only an explicit `--submit` run". There is **no `--submit` flag** any more.

**Pitfall 10 already supplies the recommended shape:** `[dev test] AM27C020 — INCONCLUSIVE (harness)`. [CITED: .planning/research/PITFALLS.md:336]

**Downstream title consumers (informational — both out of scope, but the planner should know):**
- `firestarter_app/tools/parse_devtest_issue.py` matches only the literal `"[dev test]"` marker (`:59`) plus a fenced-JSON block. It parses **no verdict**. Safe under any new token.
- `.claude/skills/devtest-triage/scripts/devtest_issues.py:69-75`:
  ```python
  TITLE_RE = re.compile(
      r"^\[dev test\]\s+(?P<chip>\S+)\s+[—-]\s+(?P<verdict>[A-Za-z]+)"
  ...
  BAD = {"BAD", "FAIL"}
  SOFT = {"MARGINAL", "INCONCLUSIVE"}
  ```
  A title reading `INCONCLUSIVE (harness)` parses to verdict `INCONCLUSIVE` (the regex stops at the first non-alpha) and lands in `SOFT` — **already handled**. A brand-new bare token such as `ERROR` would parse but match neither `BAD`, `SOFT` nor `"PASS"`, and the triage script's supersede logic would silently treat it as un-classifiable. **This argues strongly for reusing `INCONCLUSIVE` with a parenthetical qualifier rather than minting a new title token.** Phase 181 owns the SKILL.md update; this phase should pick the shape that does not *need* one.

---

## §5 — The submit prompt (ATTR-05)

`firestarter/submit.py:590-761`, `submit_report()`. The offer to file is `confirm_fn(f"Submit this report to {SUBMIT_REPO}?", default=False)` at **`submit.py:735`**. Three existing paths reach a `return` without asking it:

| # | Site | Condition | Is it a suppressor? |
|---|---|---|---|
| S-1 | `submit.py:659-676` | `not is_submittable(report.auto_capture)` — any of `chip` / `protocol` / `host_version` falsy | **Yes, a hard early return.** Prints `Cannot submit -- missing required field(s): ...` and files nothing. |
| S-2 | `submit.py:687-702` | `not isatty_fn()` — off-TTY | Prints the prefilled URL and returns. This is v1.21 SUB-01's deliberate ban on silent off-TTY submission — **not** an auto-classification suppression. |
| S-3 | `submit.py:704-730` | `prior_url` found by the dedup query | Asks a **different** question ("add this run's evidence as a comment?"). Still an offer. |

`is_submittable` itself (`diagnostic_report.py:212-226`) [VERIFIED: firestarter_app/firestarter/diagnostic_report.py:212-226]:

```python
    return bool(ac.chip) and bool(ac.protocol) and bool(ac.host_version)
```

### Finding F-1 — the milestone research contradicts ATTR-05

`.planning/research/SUMMARY.md:132` (the Phase 178 plan) says this phase delivers *"a run-validity term added to the existing `is_submittable`"*, and `FEATURES.md:348` lists **T3. ERROR run is not submittable**. [CITED: .planning/research/SUMMARY.md:132; .planning/research/FEATURES.md:348]

**ATTR-05, the locked requirement, forbids exactly that:** "Auto-classification never suppresses the submit prompt. It changes the title and disposition only; the offer to file always stands." Success criterion 4 restates it: "A run with a genuine chip fault and a run with a transport-only fault **both still offer the submit prompt**."

Pitfall 10 adjudicates in ATTR-05's favour and explains why: *"Never let auto-classification silence the report. ... Suppression converts a visible wrong verdict into an invisible missing one."* and lists as an explicit risk *"Auto-classifier suppressing the submit prompt when it decides 'rig fault' → A real chip or firmware defect never reaches the tracker — the Firefox flaky-dismissal failure mode."* [CITED: .planning/research/PITFALLS.md:336, :469]

> **Recommendation: the requirement wins. T3 is void.** `is_submittable` must be left **byte-unchanged** by this phase, and the plan should carry an explicit test asserting that a transport-faulted report still reaches `confirm_fn` — the inverse-of-suppression leg. Recording T3 as a superseded claim (the project's own `MILESTONES.md` corrections-table discipline) is the honest disposal.

### Where the "disposition" changes instead

`diagnostic_report.build_db_diff` (`:349-384`) [VERIFIED: firestarter_app/firestarter/diagnostic_report.py:365-384]:

```python
    if "BAD" in verdicts:
        proposed = _DISPOSITION_COMMUNITY_FAIL
        ladder_state = _LADDER_COMMUNITY_FAIL
    elif "marginal" in verdicts or has_indeterminate_fingerprint:
        proposed = _DISPOSITION_INCONCLUSIVE
        ladder_state = _LADDER_NONE
    elif "OK" in verdicts and verdicts <= {"OK", "NA", "SKIPPED"}:
        proposed = _DISPOSITION_CANDIDATE
        ladder_state = _LADDER_COMMUNITY_REPORTED
    else:
        proposed = _DISPOSITION_NO_CHANGE
        ladder_state = _LADDER_NONE
```

This is the "disposition" ATTR-05 permits changing. **Danger, measured:** the third arm admits `verdicts <= {"OK", "NA", "SKIPPED"}`. If a transport-faulted step becomes `SKIPPED` and every other step is `OK`, the run lands on `_DISPOSITION_CANDIDATE` / `community-reported` — **a run that did not execute validly would be proposed for graduation.** Whichever verdict is chosen, `build_db_diff` must gain a status-axis guard *ahead of* the existing ladder, e.g. an `ERROR` run routes to `_DISPOSITION_INCONCLUSIVE` / `_LADDER_NONE`. This edit moves `LADDER_PINS` only for the new shape.

---

## §6 — Phase 176's transport counters

`firestarter/transport_counters.py` — process-lifetime module-level sink. `_counters` (`:53-59`) [VERIFIED: firestarter_app/firestarter/transport_counters.py:53-59]:

```python
_counters: dict[str, int] = {
    "decode_failures": 0,
    "probe_timeouts": 0,
    "resync_body_truncated": 0,
    "resync_length_missing": 0,
    "timeouts": 0,
}
```

API: `record_decode_failure()`, `record_resync_length_missing()`, `record_resync_body_truncated()`, `record_response_timeout()`, `probe_scope()` (contextmanager), `reset()`, `snapshot()`.

They land on the report through `firestarter/diagnostic_report.py:98-149`, `TransportHealth` — **nine fields**, every counter `int | None` defaulting to `None` = "not measured":

| Field | Wired? | Notes (from the dataclass docstring, `:105-149`) |
|---|---|---|
| `decode_failures` | ✅ Phase 176 | real int after a run |
| `timeouts` | ✅ Phase 176 | non-probe `get_response` timeouts |
| `probe_timeouts` | ✅ Phase 176 | scoped by `probe_scope()`; **deliberately excluded from suspicion** |
| `resync_length_missing` | ✅ Phase 176 | wire re-sync event |
| `resync_body_truncated` | ✅ Phase 176 | wire re-sync event |
| `cobs_errors` | ❌ permanently `None` | COBS on this link is **outbound only**; `cobs_decode` has zero production call sites |
| `crc_failures` | ❌ permanently `None` | `codec.decode_id_frame` returns `None` for five distinct causes; naming it `crc_failures` "would claim a precision it does not have" |
| `retries` | ❌ permanently `None` | **there is no host-side transport retry loop**; routing firmware write-pulse retries here "would report a marginal chip … as a LINK fault" |
| `transport_suspect` | derived `bool` | `False` unless `_is_transport_suspect(th)` |

Populated in `cli_handlers.py:2404` (`transport_counters.reset()` before the run) and `:2440-2445` (five assignments from `snapshot()`).

`_is_transport_suspect` (`:164-193`) [VERIFIED: firestarter_app/firestarter/diagnostic_report.py:189-193]:

```python
    for name in _SUSPECT_SCANNED_FIELDS:
        value = getattr(th, name)
        if value is not None and value >= _SUSPECT_THRESHOLD:
            return True
    return False
```

`_SUSPECT_THRESHOLD = 5` (`:54`). `_SUSPECT_SCANNED_FIELDS` (`:151-159`) = `cobs_errors, crc_failures, decode_failures, resync_body_truncated, resync_length_missing, retries, timeouts`. `_SUSPECT_EXCLUDED_FIELDS = ("probe_timeouts",)` (`:160`).

### What actually distinguishes "the transport failed to execute validly" from "the chip is bad"

Ranked by evidential strength, measured against this codebase:

| Signal | Strength | Why |
|---|---|---|
| **`SerialError` / `SerialTimeoutError` / `HardwareOperationError` raised from `_dispatch_step`** | **Decisive.** This is the trigger. | These exception classes describe the *link*, structurally. `EpromOperationError` is the sibling that carries a firmware `error_code` and *is* a chip/firmware finding — the two are already separate `except` arms (`:2524` vs `:2542`). ATTR-02 is satisfiable purely by re-pointing the first arm. |
| `transport_suspect == True` | **Corroborating only.** | Threshold-based, whole-run scoped, not per-step. A `True` here on a run with no exception is a *hint*, never a status. Note the honest asymmetry: `False` can never mean "the link is healthy" — three of seven scanned counters are permanently `None`. |
| `Fingerprint.classification == "blank/contact"` | **Corroborating, and the only signal for the gh#23 shape.** | `ff_ratio >= 0.98` — an undriven bus reads all-`0xFF`. Pitfall 10 names this as *the* honest available signal for "VPP not connected", not the voltage sampler. |
| `chip_id_actual == 0x303` (floating bus) | **Corroborating.** | Project-recorded floating-chip-ID signature (`reference_vpp_vpe_no_socket_routing.md`). |
| `vpp_before_mv` / `vpe_before_mv` | **NOT A SIGNAL. See §8.** | Physically blind to the socket. Reading it as evidence about the rig is exactly Pitfall 10. |

> **Where no honest signal exists, emit `unknown`, not a guess.** [CITED: .planning/research/PITFALLS.md:335]

---

## §7 — Phase 177's fingerprint gate

`classify_fingerprint(expected, actual, *, repeat_divergent=None, addr_base=0) -> Fingerprint` at `chip_test.py:163-271` [VERIFIED: firestarter_app/firestarter/chip_test.py:138-142, 163-271].

**Five classification values** (`chip_test.py:138-142`):
```python
FP_BLANK_CONTACT = "blank/contact"
FP_ADDRESS_LINE = "address-line"
FP_TRANSPORT = "transport"
FP_INDETERMINATE = "indeterminate"
FP_MATCH = "match"
```

Returns a `Fingerprint(total, bad, bad_pct, classification, evidence)` (`:154-161`). Locked classification order (docstring `:180-187`): blank/contact → address-line → match → transport → indeterminate. Phase 177 (D-177-2) added `FP_MATCH` **after** the `ff_ratio` and address-line tests, deliberately, so the `blank/contact` population was not re-keyed.

`_synthesized_match_fingerprint(region_length)` (`:275-305`) is Phase 177's zero-I/O constructor for a clean step; its `evidence["ff_ratio"]` is `None`, "not `0.0`: it was never measured, and reporting `0.0` would present a fabricated measurement as if it were real evidence."

The gate itself, `chip_test.py:3181-3199`:
```python
        if collect_fingerprint and op in (OP_WRITE, OP_WRITE_PARTIAL, OP_VERIFY):
            step_failed = prior_cycles_failed or (
                not all(outcomes) if outcomes else False
            )
            if step_failed:
                actual = _read_region(...)
                if actual:
                    diverged = len(set(outcomes)) != 1 if outcomes else False
                    fingerprint = classify_fingerprint(
                        expected, actual, repeat_divergent=diverged, addr_base=region_start,
                    )
            else:
                fingerprint = _synthesized_match_fingerprint(region_length)
```

### Finding F-2 — `FP_TRANSPORT` is still DEAD CODE on this branch. CONFIRMED.

The operator memory (`reference_classify_fingerprint_transport_bucket_unreachable.md`) says the `transport` bucket is unreachable because `runs=1` always. **That is still true on `gsd/v1.36-dev-test-fidelity` @ `0a29d8b`.**

Structural proof, read this session:
- `FP_TRANSPORT` is returned only when `repeat_divergent is True` (`chip_test.py:257`).
- The only production call site passing `repeat_divergent` is `chip_test.py:3195`, with `diverged = len(set(outcomes)) != 1 if outcomes else False`.
- `outcomes` is appended once per iteration of `for _ in range(runs)` inside `_dispatch_multi_run`.
- Every fingerprint-bearing op (`OP_WRITE`, `OP_WRITE_PARTIAL`, `OP_VERIFY`) is inside the repeat-cycle block: `_CYCLE_BLOCK_START_OPS = frozenset({OP_WRITE, OP_WRITE_PARTIAL})` (`:1275`), and `cycle_block_bounds` (`:1278-1303`) takes the maximal consecutive run from `_CYCLE_BLOCK_OPS`.
- `_run_cycle_block` calls `_run_step(..., runs=1, ...)` — **hard-coded**, `chip_test.py:1598`. Its own docstring (`:1548-1553`) states this: "this loop calls `_run_step` with `runs=1`, so the final cycle's own `outcomes` is a one-element list".
- Therefore `len(outcomes) == 1` ⇒ `len(set(outcomes)) == 1` ⇒ `diverged is False` ⇒ `FP_TRANSPORT` unreachable.

**Empirical falsification attempt (run this session, `firestarter_app/.venv311`).** I instrumented `chip_test._dispatch_multi_run` to record the `runs` value it actually receives during a real `run_plan(..., runs=2)` on three chips:

```
sst27sf512 -> [('write', 1, False), ('verify', 1, False), ('erase', 1, False), ('write', 1, True), ('verify', 1, True), ('erase', 1, True)]
at28c256   -> [('write', 1, False), ('verify', 1, False), ('erase', 1, False), ('write', 1, True), ('verify', 1, True), ('erase', 1, True)]
w27e257    -> [('write', 1, False), ('verify', 1, False), ('erase', 1, False), ('write', 1, True), ('verify', 1, True), ('erase', 1, True)]
```

Every fingerprint-bearing dispatch receives `runs=1`. The falsification attempt failed to falsify. [VERIFIED: firestarter/chip_test.py:1598, 3181-3199, 1275-1303 + measured probe]

**What would make it reachable:** `_run_cycle_block` would have to pass `runs>1` to `_run_step`, or `_dispatch_multi_run`'s `diverged` would have to be computed across *cycles* rather than across intra-step runs (the same information `prior_cycles_failed` already carries down). The second is a small, honest change — `_run_cycle_block` could thread a `prior_cycles_disagreed` sibling alongside `prior_cycles_failed`, using the same `per_step[i]` list it already builds.

**Is that in scope for ATTR-01..06? No.** None of the six requirements mentions the fingerprint classifier, and success criterion 1 turns on the *step verdict*, not on a fingerprint bucket. Reviving `FP_TRANSPORT` is a separate concern that belongs in the backlog or in Phase 181's fingerprint work. **But the planner must not build the status-axis classification on top of `FP_TRANSPORT`** — it will never fire. Build it on the exception arm (§6).

> **Consequence for the ROADMAP's dependency claim.** The ROADMAP says Phase 178's "fault-mode reasoning consumes" Phase 177's fingerprint gate. What Phase 178 can actually consume is the `blank/contact` bucket (reachable, and the gh#23 signal per Pitfall 10) and `FP_MATCH`/`FP_INDETERMINATE`. It cannot consume `FP_TRANSPORT`. The dependency is real but narrower than the ROADMAP sentence implies.

---

## §8 — ATTR-06: the report text surface

### Correction C-1 — the requirement's own wording is incomplete (the conclusion still holds)

ATTR-06 says: *"`sample_vpp_mv` → `hw_read_voltage` sets `CTRL_VPP_REGULATOR_ENABLE` and no socket-routing bits."*

The firmware source, `firestarter/src/hardware_operations.cpp:25-32` [VERIFIED: firestarter/src/hardware_operations.cpp:25-32, branch `gsd/v1.36-dev-test-fidelity`]:

```cpp
        rurp_set_programmer_mode();
        if (handle->cmd == CMD_READ_VPP) {
            LOG_DEBUG_ID_SUB(DBG_SETTING_UP_VPP);
            rurp_write_to_register(CONTROL_REGISTER, CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE);
        } else if (handle->cmd == CMD_READ_VPE) {
            LOG_DEBUG_ID_SUB(DBG_SETTING_UP_VPE);
            rurp_write_to_register(CONTROL_REGISTER, CTRL_VPP_REGULATOR_ENABLE);
        } else {
```

The **VPP** branch sets `CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE` — two bits, not one. Only the **VPE** branch sets `CTRL_VPP_REGULATOR_ENABLE` alone.

**The substantive claim is nonetheless correct.** The socket-routing bits are `CTRL_VPP_A9_ENABLE`, `CTRL_VPE_ENABLE`, `CTRL_VPP_P1_ENABLE`, defined at `firestarter/include/rurp_pinout.h:72-80` (legacy arm) / `:84-93` (`HARDWARE_REVISION` arm) [VERIFIED: firestarter/include/rurp_pinout.h:70-95]:

```c
#define CTRL_VPP_VPE_DROP_ENABLE      0x01
#define CTRL_ADDRESS_LINE_16          CTRL_VPP_VPE_DROP_ENABLE
#define CTRL_VPP_A9_ENABLE            0x02
#define CTRL_VPE_ENABLE               0x04
#define CTRL_VPP_P1_ENABLE            0x08
#define CTRL_ADDRESS_LINE_17          0x10
#define CTRL_ADDRESS_LINE_18          0x20
#define CTRL_READ_WRITE               0x40
#define CTRL_VPP_REGULATOR_ENABLE     0x80
```

`hw_read_voltage` sets **none** of `CTRL_VPP_A9_ENABLE`, `CTRL_VPE_ENABLE`, `CTRL_VPP_P1_ENABLE` on either branch. `CTRL_VPP_VPE_DROP_ENABLE` is the regulator drop divider, not a socket route (`rurp_pinout.h:117`: `EPROM_HV_ROUTE_MASK (CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE)` — the HV *route*, i.e. rail composition, as distinct from `CTRL_VPP_P1_ENABLE`, which `rurp_shield.h:35-38` documents as the pin-1 redirect: "`using_p1_as_vpp()` … redirects `CTRL_VPE_ENABLE` → `CTRL_VPP_P1_ENABLE`"). It measures the boost-regulator rail via ADC; the high voltage never reaches the socket pins.

> **Action for the planner:** repair ATTR-06's parenthetical in `REQUIREMENTS.md` to name **both** bits on the VPP branch, in the same commit that lands the report sentence. Do **not** weaken the conclusion — the "no socket-routing bits" claim is verified.

Corroborated independently by the operator record: `reference_vpp_vpe_no_socket_routing.md` ("vpp/vpe monitors don't route to the socket; blank/0x303 = contact fault") and `.planning/research/PITFALLS.md:316-341` (Pitfall 10, "MEASURED against firmware behaviour").

### The host chain, verified

| Hop | Site |
|---|---|
| `report.vpp_before_mv = vpp` | `firestarter/cli_handlers.py:2234-2241`, inside `_make_sampler`'s `_sampler(phase)` closure |
| `app.hardware_manager.sample_vpp_mv()` | `firestarter/hardware.py:440-443` → `self._sample_one_voltage(COMMAND_READ_VPP, n=n)` |
| `_sample_one_voltage` | `firestarter/hardware.py:~380-440`; median of `n` samples, `None` on any transport error — "honest fallback, never a fabricated 0" |
| Field declaration | `firestarter/diagnostic_report.py:629-632` (`vpp_before_mv` / `vpp_after_mv` / `vpe_before_mv` / `vpe_after_mv`) |
| JSON export | `firestarter/diagnostic_report.py:700-730` `_voltage_dict()`, `NOT_MEASURED` substitution |

`_make_sampler`'s own docstring already says "energize+measure only" (`cli_handlers.py:2225-2228`) — it does **not** say what that fails to prove. That is the ATTR-06 gap.

### Where the sentence must land

**The report render**, `firestarter/diagnostic_report.py:1000-1007` [VERIFIED: firestarter_app/firestarter/diagnostic_report.py:1000-1007]:

```python
        v = d["voltage"]
        table.add_row(
            "vpp (before/after)", _rail_cell(v["vpp_before_mv"], v["vpp_after_mv"])
        )
        table.add_row(
            "vpe (before/after)", _rail_cell(v["vpe_before_mv"], v["vpe_after_mv"])
        )
```

Criterion 5 says "**The report states in words**". A docstring is not the report. The sentence has to reach at least one of:

1. `render()` — a `table.add_row(...)` beside the two rail rows (the console surface every run prints), and/or
2. `to_dict()` — a named additive string key, which carries it into the saved `dev-test-<chip>.json`, the saved `.md`'s fenced block, and the filed issue body. **This moves `_TO_DICT_KEYS` or `_VOLTAGE_KEYS`** (`tests/test_blast_radius_invariance.py:92-127`) — expected, allowed, and must be updated in the same commit. It does **not** move `dedup_fingerprint` (§2).
3. `submit.build_body`'s markdown — reached automatically if (2) is taken, since the body derives from the sanitized `to_dict()`.

**Recommendation: do both (1) and (2).** (1) satisfies "the report states in words" for the operator running the command; (2) makes the disclosure travel with the filed issue, which is the surface a triager reads.

### Wording gate

`firestarter_app/tools/check_diagnostic_report_claims.py` is an AST scanner over **every string literal in `diagnostic_report.py`**, with a 14-entry `FORBIDDEN_PATTERNS` table (all `re.IGNORECASE`): `verified\s+fixed`, `confirmed\s+working`, `silicon[-\s]verified`, `verified\s+(on|against)\s+(real\s+)?(at28c\w*|silicon)`, `works?\s+on\s+(\w+\s+){0,2}(at28c\w*|silicon)`, `now\s+works?\b`, `should\s+now\s+work`, `proven\s+on\s+(\w+\s+){0,2}(at28c\w*|silicon)`, `lock\s+inhibited\s+the\s+write`, `\bthe\s+lock\s+held\b`, `proven\s+behaviou?r`, `behaviou?rally\s+verified`, `now\s+proven\b`, `dev\s+test\s+proves\b`. [VERIFIED: firestarter_app/tools/check_diagnostic_report_claims.py:106-148]

A sentence of the form *"a rail reading does not prove the socket is connected"* trips none of them. Avoid the words `proven`, `verified` and the phrase `dev test proves`.

---

## §9 — Test surface and verify commands

### Layout

| File | Lines | Scope |
|---|---|---|
| `tests/test_chip_test.py` | — | engine core, read-back counting (Phase 177 criterion 1) |
| `tests/test_chip_test_cycle.py` | — | the repeat-cycle block, cycle-1-fail/cycle-2-pass |
| `tests/test_chip_test_blank_check_order.py` | — | blank-check ordering |
| `tests/test_chip_test_sdp_leg.py` | — | the six SDP-leg ops |
| `tests/test_chip_test_timing.py` | — | `duration_s` |
| `tests/test_dev_test_cmd.py` | — | the CLI handler end-to-end (CliRunner); **the R2b transport test lives here, `:2014-2037`** |
| `tests/test_diagnostic_report.py` | — | `dedup_fingerprint`, render, `to_dict` |
| `tests/test_submit.py` | — | title, body, sanitizer, `submit_report` |
| `tests/test_blast_radius_invariance.py` | 785 | the Phase 174 oracle |
| `tests/test_rekey_ledger.py` | — | ledger structure + the meta checker subprocess legs |
| `tests/test_op_registration_parity.py` | — | 7 policed registries + 5 declared non-registries |
| `tests/test_check_devtest_orchestrator.py` | — | the orchestrator-only AST gate |
| `tests/test_devtest_firmware_error_propagation.py` | — | `error_code` propagation |

### Copy-pasteable commands — every one below was RUN this session

```bash
# Interpreter (py3.11, matching CI; the devcontainer default 3.12 masks it)
cd /workspaces/firestarter_app && ./.venv311/bin/python --version
# -> Python 3.11.16
./.venv311/bin/python -c "import firestarter; print(firestarter.__file__)"
# -> /workspaces/firestarter_app/firestarter/__init__.py   (editable install resolves to the worktree)

# The Phase 174 oracle + the ledger (fast; the per-task gate)
./.venv311/bin/python -m pytest tests/test_blast_radius_invariance.py tests/test_rekey_ledger.py -o addopts="" -q
# -> 118 passed in 1.43s

# The meta-side cross-tree ledger checker (PRIMARY runner, D-13) -- run from /workspaces
cd /workspaces && python3 tools/rekey/check_rekey_ledger.py
# -> OK: 8 ledger row(s), 8 MILESTONES.md row(s) bound   (exit 0)

# Full suite (the phase gate)
cd /workspaces/firestarter_app && ./.venv311/bin/python -m pytest tests/ -o addopts="" -q -p no:randomly
# -> 32 snapshots passed. / 2216 passed, 1 warning in 320.13s (0:05:20)

# The three CI gate legs
./.venv311/bin/python -m ruff check firestarter/ tests/
# -> All checks passed!
./.venv311/bin/python -m ruff format --check firestarter/ tests/
# -> 171 files already formatted
./.venv311/bin/python tools/check_mypy_watermark.py
# -> checked 173 source files / mypy errors: 35 (watermark: 35) / OK: error count at watermark.

# The two AST gates this phase's edits pass through
./.venv311/bin/python tools/check_devtest_orchestrator.py
# -> PASS: scanned ../firestarter/chip_test.py, ../firestarter/cli_handlers.py,
#    ../firestarter/submit.py; 0 VPP-set, 0 raw-wire-dict, 0 --force,
#    0 broad-except; firmware untouched (host-only, asserted)   (exit 0)
./.venv311/bin/python tools/check_diagnostic_report_claims.py
# -> PASS: scanned .../firestarter/diagnostic_report.py, 205 string literals
#    checked, zero forbidden matches   (exit 0)

# Snapshot drift + regeneration for a newly registered shape
./.venv311/bin/python tools/snapshot_report_shapes.py --check
# -> OK: 17 snapshot(s) under .../tests/fixtures/reports match a fresh regeneration
./.venv311/bin/python tools/snapshot_report_shapes.py --shape attr01-status-axis-transport-fault
```

> `-o addopts=""` is required to see the count line: `pyproject.toml:107` sets `addopts = "-ra -q"` and a second `-q` suppresses it. [VERIFIED: firestarter_app/pyproject.toml:105-107]
>
> There is exactly one venv: `firestarter_app/.venv311/`. Use `./.venv311/bin/python` for every command; the devcontainer default `python3` is 3.12 and masks CI.

### Tests that will go RED and must be repaired FORWARD

| Test | Why | Repair |
|---|---|---|
| `tests/test_dev_test_cmd.py:2014-2037` `test_r2_transport_error_during_id_check_closes_gate_and_renders_notrun` | Asserts `steps["id"]["verdict"] == "BAD"` on a `SerialError("half-seated cable")` — **this is the exact behaviour ATTR-02 deletes** | Re-point to the new verdict + assert the **new status field**, and **keep** the two load-bearing assertions unchanged: `operator.sdp_lock.assert_not_called()` and `hold_state == SDP_HOLD_NOT_RUN`. Those prove the safety gate still closes. |
| `tests/test_blast_radius_invariance.py` `_TO_DICT_KEYS` / `_STEPS_ELEMENT_0_KEYS` / `_VOLTAGE_KEYS` | Any new exported key moves a pinned list | Update the pin in the same commit; that is the pin working as designed. |
| `tests/test_blast_radius_invariance.py` `_PINNED_SHAPE_ID_SET`, five-way closure, `LADDER_PINS` | Registering `attr01-status-axis-transport-fault` | The seven-edit list in §3. |
| `tests/test_blast_radius_invariance.py:758-764` `test_build_shape_raises_for_every_reserved_shape_id` | Its docstring says "all three `RESERVED_SHAPE_IDS` names"; there are two now, and after this phase there will be one | Stale docstring already (Phase 177 registered `prune03`). Fix the count while touching the file. The assertion itself sweeps `sorted(RESERVED_SHAPE_IDS)` and stays correct. |
| Anything asserting `overall_verdict(...) == "FAIL"` on a transport-faulted double | ATTR-03 | Search `tests/test_submit.py` for `"FAIL"` before planning. |

---

## §10 — Naming the status field

### The prior art, verbatim

The OCP Test & Validation output specification (`opencomputeproject/ocp-diag-core`, `json_spec/README.md`), as quoted in the milestone research [CITED: .planning/research/FEATURES.md:20-45]:

| Axis | Enum | Spec wording |
|---|---|---|
| **TestStatus** — *did the run execute validly?* | `COMPLETE` | "The diagnostic completed execution normally." |
| | `ERROR` | "The diagnostic did not complete execution normally due to an exception." |
| | `SKIP` | "The diagnostic was skipped or did not run to normal completion as part of its execution." |
| **TestResult** — *what is the verdict on the DUT?* | `PASS` / `FAIL` / `NOT_APPLICABLE` | — |

The spec locks the legal cross-product to four cells and states: *"Any other combination of TestResult and TestStatus shall be considered invalid."* Reference implementations exist in Python (`ocptv` on PyPI), Rust, Go, C++. [CITED: https://github.com/opencomputeproject/ocp-diag-core/blob/main/json_spec/README.md, via .planning/research/FEATURES.md:509]

> **No new runtime dependency.** Phase 181's success criterion 5 says "no new runtime dependency is added", and `.planning/REQUIREMENTS.md:139` already rules out schema libraries as "measured unnecessary". Adopt the **vocabulary**, never the `ocptv` package. [CITED: .planning/REQUIREMENTS.md:139]

### Candidate names

| # | Field name | Values | For | Against |
|---|---|---|---|---|
| **N-1** | `status` on `StepResult`; `run_status` derived on `DiagnosticReport` | `"COMPLETE"` / `"ERROR"` / `"SKIP"` | Matches OCP's own field name and enum exactly, so a reader can look it up; ATTR-01 says "following the OCP Test & Validation two-axis model" — this is the most literal compliance. Constants `STATUS_COMPLETE` / `STATUS_ERROR` / `STATUS_SKIP` sit naturally beside `VERDICT_*` at `chip_test.py:935-939`. | `status` is a generic word; a future reader could confuse it with `support_status` (the DB field `build_db_diff` reads at `diagnostic_report.py:363`). |
| **N-2** | `run_status` on both | same | Unambiguous against `support_status`; reads well in JSON (`"run_status": "ERROR"`). | Per-*step* `run_status` reads oddly — the step is not the run. Would force two different names for the two levels. |
| **N-3** | `execution` / `exec_status` | same | Very unambiguous. | Invents a name; loses the "this is OCP's `TestStatus`" pointer that ATTR-01 asks for. |

> **Recommendation: N-1.** `StepResult.status`, defaulting to `STATUS_COMPLETE`, with a derived `DiagnosticReport` top-level `run_status`. Disambiguate `support_status` in the field's docstring rather than in its name — the same discipline `sdp_hold_state` uses ("This field is a report VALUE, not an op string"). This is a **Claude's-discretion** call in the absence of CONTEXT.md; the operator may override at plan-check.

### The four legal cells, mapped onto this codebase

| OCP `TestStatus` | OCP `TestResult` | This codebase's `verdict` | When |
|---|---|---|---|
| `COMPLETE` | `PASS` | `OK` | step ran, chip conformed |
| `COMPLETE` | `FAIL` | `BAD`, `marginal` | step ran, chip did not conform (or cycles disagreed) |
| `SKIP` | `NOT_APPLICABLE` | `SKIPPED`, `NA` | gated, unsupported, refused target |
| **`ERROR`** | **`NOT_APPLICABLE`** | **?** ← the ATTR-02 decision | `SerialError` / `HardwareOperationError` |

---

## §11 — Which existing `verdict` a transport fault must carry (the highest-risk decision)

ATTR-04 forbids a sixth value. Criterion 1 forbids `BAD`. So the transport-faulted step must carry one of `OK`, `NA`, `SKIPPED`, `marginal`. **Every one of those four changes at least one downstream decision.** Complete consumer census, measured by `/usr/bin/grep` over `firestarter/` and `tools/`:

| # | Consumer | Site | Keyed on | Effect if transport fault → `SKIPPED` | → `marginal` | → `NA` |
|---|---|---|---|---|---|---|
| C-1 | `_id_step_closes_gate` — **SAFETY** | `chip_test.py:1930-1941` — `return result.verdict in (VERDICT_BAD, VERDICT_SKIPPED)` | `(BAD, SKIPPED)` | ✅ gate still closes | ❌ **gate opens — write to an unidentified chip** | ❌ **gate opens** |
| C-2 | `_baseline_closes_sdp_gate` | `chip_test.py:1944-1960` — `return result.verdict != VERDICT_OK` | `!= OK` | ✅ closes | ✅ closes | ✅ closes |
| C-3 | `sdp_hold_state` | `chip_test.py:2017-2021` | `OK`→HELD, `BAD`→NOT_HELD | ✅ → `NOT-RUN` (correct: a transport fault proves nothing about the lock) | ✅ → `NOT-RUN` | ✅ → `NOT-RUN` |
| C-4 | `sdp_left_writable` | `chip_test.py:2029-2040` — `== VERDICT_OK` | `== OK` | ✅ False | ✅ False | ✅ False |
| C-5 | `write_context.chip_is_blank` | `chip_test.py:1614-1618`, `:1822-1829` — set only on `(OK, BAD)` | `(OK, BAD)` | ✅ stays `None` (the safe default) | ✅ stays `None` | ✅ stays `None` |
| C-6 | `_RAN_VERDICTS` → `count_applicable` banner, `_run_step` duration stamp, `_aggregate_cycle_results` | `chip_test.py:3575` — `frozenset({OK, BAD, MARGINAL})` | membership | step counts as **not ran** → banner N<M fires (arguably correct); `duration_s` becomes `None` | counts as **ran** | not ran |
| C-7 | `_VERDICT_EXIT_CODES` | `cli_handlers.py:2093-2099` — `{OK:0, NA:0, SKIPPED:0, MARGINAL:2, BAD:1}` | value | ⚠️ **exit 0** on a run that did not execute validly | exit 2 | ⚠️ exit 0 |
| C-8 | `build_db_diff` ladder | `diagnostic_report.py:365-384` | `"BAD"`, `"marginal"`, `<= {OK,NA,SKIPPED}` | ⚠️ **third arm → `community-reported`** (a broken run proposed for graduation) | ✅ `INCONCLUSIVE` | ⚠️ third arm |
| C-9 | `submit.overall_verdict` → title | `submit.py:140-153` | `"BAD"`, `"marginal"` | ⚠️ title reads `PASS` | title reads `INCONCLUSIVE` | ⚠️ `PASS` |
| C-10 | `submit._reason_text` | `submit.py:203-217` — `if verdict == VERDICT_NA: return "-"` | `NA` | ✅ reason preserved | ✅ preserved | ❌ **the transport-fault reason is suppressed to `-` in the filed markdown table** |
| C-11 | `_step_dict` reason suppression | `diagnostic_report.py:793` — `"reason": "" if result.verdict == VERDICT_NA else result.reason` | `NA` | ✅ preserved | ✅ preserved | ❌ **suppressed in the exported JSON** |
| C-12 | `dedup_fingerprint` | `diagnostic_report.py:276` | `result.verdict` | re-keys only reports that carried a transport fault (none frozen) | same | same |

### Reading of the table

- **`NA` is disqualified.** C-10 and C-11 would delete the transport-fault reason from both the filed table and the exported JSON — the report would say a step did not apply and give no cause. That is the opposite of ATTR-02's intent.
- **`marginal` alone is disqualified by C-1.** The safety gate would stop closing. It is *also* semantically wrong: the `VERDICT_MARGINAL` docstring (`chip_test.py:933-934`) says it is "destructive/verify-only -- never forced onto read-step disagreement", and its established meaning is "the N runs disagreed", not "the link failed".
- **`SKIPPED` keeps C-1 closed** and preserves the reason (C-10, C-11) — it is the strongest single-value candidate — **but it needs three explicit widenings** (C-7 exit code, C-8 ladder, C-9 title), each of which must read the *status axis*, not the verdict. That is exactly what ATTR-01 exists to make possible, and each widening is a small, testable edit.
- **`OK` is disqualified** on its face: a failed run reading OK is a false-green.

> **Recommendation:** `verdict=VERDICT_SKIPPED` **plus** `status=STATUS_ERROR`, with C-7, C-8 and C-9 widened to consult `status` **before** the verdict fold. Concretely:
> - C-9 `overall_verdict`: `if any(status == ERROR) -> "INCONCLUSIVE"` (reusing the existing token so the devtest-triage regex and its `SOFT` set keep working — §4), with a qualifier in the title body per Pitfall 10's `INCONCLUSIVE (harness)`.
> - C-8 `build_db_diff`: an `ERROR` guard arm ahead of the existing ladder → `_DISPOSITION_INCONCLUSIVE` / `_LADDER_NONE`.
> - C-7 exit code: `_dev_test_exit_code` already has the precedent for a **non-verdict term** — `sdp_oracle_not_run` is added as a code-2 *candidate* (never a `max`), `cli_handlers.py:2130-2157`. Add the `ERROR` status the same way, as a code-2 candidate through `_EXIT_CODE_PRECEDENCE`, never as a numeric max. That helper's own docstring already names and defends the pattern.
>
> **Every one of these is the planner's to confirm.** There is no CONTEXT.md; if the operator prefers `marginal`, the plan MUST additionally widen C-1 (`_id_step_closes_gate`) and prove the widening with the existing R2b test.

---

## Architecture Patterns

### Pattern 1: an additive report field, kept out of the hash

**What:** declare the field on the dataclass, export it in `to_dict()`, update the pinned key list, and write **no** `parts.append` in `dedup_fingerprint`.
**When:** every additive field this milestone ships.
**Precedents in this tree:** `duration_s` (schema 1.5, `chip_test.py:1046-1053` + `diagnostic_report.py:800`), `run_count` (schema 1.7, `diagnostic_report.py:768-780`), `write_target`/`write_coverage` (`diagnostic_report.py:760-766`). Each declares its exclusion **in its own docstring** and each has a paired "does not perturb the fingerprint" test.

### Pattern 2: the empty-default tag (do **not** use it here)

`repeat_policy_tag` and `coverage_tag` are appended *only when non-empty*, so the default path leaves every historical fingerprint byte-identical (`diagnostic_report.py:277-300`). This is the pattern for a field that **is** in the hash but must not re-key. **ATTR-04 needs the stronger thing — not in the hash at all — so this pattern is the wrong one to copy.** Recording the distinction matters because the two look alike.

### Pattern 3: a report VALUE that is not an op string

`SDP_HOLD_HELD` / `SDP_HOLD_NOT_HELD` / `SDP_HOLD_NOT_RUN`, `chip_test.py:1962-1967`:

> "Three-valued hold-state REPORT VALUES. These are report values, NOT op strings -- they carry no `OP_` prefix and must never join `_ALL_OPS`/`_MULTIWORD_OP_VALUES` in tests/test_op_registration_parity.py; a later reader must not 'helpfully' register them there."

**Copy this docstring shape verbatim for the status constants**, so `test_non_registry_still_has_no_ops`'s AST inversion guard and a future reader both stay correct.

### Pattern 4: derive in the engine, assign in the handler

`sdp_hold_state(plan, results)` is computed in `chip_test.py` and only **assigned** in `cli_handlers.py:2450` — the handler never computes a derived report value inline. `report.transport.*` follows the same shape (`:2440-2445`). A run-level status fold belongs in `chip_test.py` (or as a `DiagnosticReport` method beside `_is_transport_suspect`), never inline in `dev_test`.

### Pattern 5: a non-verdict term added to the exit code as a precedence *candidate*

`_dev_test_exit_code` (`cli_handlers.py:2130-2157`) — its docstring states the rule and the reason: "Composed as a precedence CANDIDATE, never as a numeric max against the observed code. A max of 1 (BAD) and 2 (the floor) returns 2, which would launder a BAD run into an inconclusive one." It also states the cost honestly: "`dev test`'s exit code is no longer a pure function of step verdicts -- it gains exactly this one non-verdict term." Adding the status term makes it two; **state that cost in the docstring too.**

### Pattern 6: two-commit, two-repo re-key declaration (D-11)

`.planning/MILESTONES.md:49` [VERIFIED: /workspaces/.planning/MILESTONES.md:49]:
> "first, a behaviour change lands on its own and turns the frozen gate for that row's `shape_id` RED; second, a separate commit touching only that row's `after_hash` … makes the gate green again, so the re-key is a reviewable unit and an executor cannot reflexively repair the test inside the same commit that changed the behaviour; third, the `before` cell is never overwritten."

Phase 178 should need **no** declaration (ATTR-04 asserts no re-key). If a frozen gate goes red, that is the phase failing its own criterion 3 — **not** a bookkeeping task.

### Anti-patterns

- **A5 — a sixth `verdict` value.** Forbidden by ATTR-04 and by `.planning/research/FEATURES.md:339`: "a new `verdict` value re-keys every group that hits it, exactly the Sentry fork, exactly the gh#20 orphan. And it makes the illegal states representable again."
- **A7 — suppressing the report on suspicion.** Forbidden by ATTR-05. "Suppress only on *evidence* of an invalid run (an `ERROR`-status step actually occurred). Never on suspicion or heuristic." [CITED: .planning/research/FEATURES.md:341]
- **A1 — a softer FAIL / confidence percentages.** "Hedging is not honesty." Emit `unknown`, not a graded belief. [CITED: .planning/research/FEATURES.md:330]
- **Classifying on `vpp_before_mv`.** Pitfall 10. Physically blind (§8).
- **Building on `FP_TRANSPORT`.** Dead code (§7 F-2).
- **`#` comments in source.** Project hard rule. Docstrings only.

---

## Don't Hand-Roll

| Problem | Don't build | Use instead | Why |
|---|---|---|---|
| A status vocabulary | An invented three/four-value enum | OCP `TestStatus` names `COMPLETE`/`ERROR`/`SKIP` | ATTR-01 names the model; a published consortium spec with four legal cells is already adjudicated |
| A schema validator for the new field | `jsonschema` / `pydantic` | Nothing — key-list pins already exist | `REQUIREMENTS.md:139` measured these unnecessary; Phase 181 forbids a new runtime dependency; `_TO_DICT_KEYS` et al. already gate key drift |
| A "did the hash move" checker | A new script | `tests/test_blast_radius_invariance.py` + `tools/rekey/check_rekey_ledger.py` | Both exist, both have anti-vacuity legs observed RED, both run in CI |
| A second submittability gate | A parallel `is_run_valid()` | Nothing — ATTR-05 forbids gating at all | `.planning/research/FEATURES.md:353`: "A second gate would let the two disagree" |
| A transport-fault detector | A heuristic over counters/voltages | The existing `except (SerialError, HardwareOperationError)` arm | The exception *is* the evidence; a heuristic is Pitfall 10 |
| A divergence primitive | A second `_diff_offsets` | `chip_test._diff_offsets` (`:118-130`) | Its own docstring: "do NOT add a second parallel divergence implementation elsewhere in this codebase" |
| Report snapshots | Hand-written JSON | `tools/snapshot_report_shapes.py` | `test_committed_snapshot_matches_a_fresh_regeneration` byte-compares against a fresh regeneration |

**Key insight:** this milestone has already built the measurement apparatus (Phase 174), the licence (175), the counters (176) and the fingerprint gate (177). Phase 178's whole job is a **vocabulary change plus four small widenings**, measured against instruments that already exist. Anything that looks like new infrastructure is almost certainly a re-implementation.

---

## Common Pitfalls

### P-1: Moving the verdict and silently opening the destructive gate
**What goes wrong:** the transport-faulted `id` step stops reading `BAD`, `_id_step_closes_gate` (`chip_test.py:1941`) stops returning `True`, and a write proceeds against a chip whose identity was never confirmed.
**Why it happens:** the gate reads a two-element tuple `(VERDICT_BAD, VERDICT_SKIPPED)`, not "non-OK"; the coupling is invisible from the exception handler.
**How to avoid:** choose `VERDICT_SKIPPED`, or widen the predicate to consult the status axis — and keep `tests/test_dev_test_cmd.py:2014-2037`'s `operator.sdp_lock.assert_not_called()` and `hold_state == SDP_HOLD_NOT_RUN` assertions unchanged as the proof.
**Warning sign:** the R2b test is "fixed" by deleting or relaxing those two assertions rather than by re-pointing the verdict.

### P-2: A broken run promoted to `community-reported`
**What goes wrong:** `build_db_diff`'s third arm admits `verdicts <= {"OK", "NA", "SKIPPED"}` (`diagnostic_report.py:377`). A `SKIPPED` transport fault on an otherwise clean run lands there.
**How to avoid:** an `ERROR`-status guard arm ahead of the ladder.
**Warning sign:** `LADDER_PINS` for the new shape reads `("suggests: candidate for community-reported (advisory)", "community-reported")`.

### P-3: Vacuous ATTR-04 confirmation
**What goes wrong:** the 17 frozen hashes stay green and the phase declares ATTR-04 satisfied — but the status field was never actually populated on any hashed report, so the gate proved nothing.
**How to avoid:** Leg B in §3 — two reports differing **only** in status, asserted equal, in the `test_durations_do_not_perturb_dedup_fingerprint` idiom.
**Warning sign:** no test in the phase constructs two reports that differ only in the status axis.

### P-4: The ATTR-06 sentence in a docstring
**What goes wrong:** criterion 5 says "the report **states in words**". A `"""..."""` in `diagnostic_report.py` never reaches a user.
**How to avoid:** land it in `render()` and/or `to_dict()` (§8). Assert its presence in the **rendered output / exported dict**, not in `__doc__`.

### P-5: Reviving `FP_TRANSPORT` by accident
**What goes wrong:** the phase wires classification to `Fingerprint.classification == "transport"`, ships green unit tests built on hand-constructed `Fingerprint` objects, and the branch never fires in production.
**How to avoid:** §7 F-2. The trigger is the exception arm.
**Warning sign:** any test that hand-constructs `Fingerprint(classification="transport")` and calls it end-to-end coverage.

### P-6: Suppressing the reason via `NA`
**What goes wrong:** `NA` looks like the OCP-faithful `NOT_APPLICABLE`, but `submit._reason_text` (`:203-217`) and `_step_dict` (`diagnostic_report.py:793`) both blank the reason for `NA`. The filed report would show a step that "did not apply" with no cause.
**How to avoid:** do not use `NA`. If the operator insists, both suppressions must be re-keyed on the status axis.

### P-7: A new title token the triage tooling cannot classify
**What goes wrong:** a title reading `[dev test] <chip> — ERROR (<hash>)` parses in `devtest_issues.py`'s `TITLE_RE` but matches neither `BAD = {"BAD","FAIL"}` nor `SOFT = {"MARGINAL","INCONCLUSIVE"}` nor `"PASS"`.
**How to avoid:** reuse `INCONCLUSIVE` with a parenthetical qualifier (Pitfall 10's own example). The regex `(?P<verdict>[A-Za-z]+)` stops before the parenthesis, so `INCONCLUSIVE (harness)` already classifies as `SOFT`.

### P-8: Re-key discipline collapsed into one commit
**What goes wrong:** an executor sees a red frozen gate and repairs it in the same commit as the behaviour change, defeating D-11's reviewability rule (`MILESTONES.md:49`).
**How to avoid:** for this phase there should be **no** re-key. If one appears, stop and treat it as a criterion-3 failure, not as a task.

### P-9: py3.12 masking the gate
**What goes wrong:** running `pytest` with the devcontainer default interpreter passes locally and CI (py3.11) fails.
**How to avoid:** every command uses `./.venv311/bin/python`. [operator memory `reference_devcontainer_py312_masks_ci_py39.md`]

### P-10: `grep` under-scanning
**What goes wrong:** the devcontainer `grep` is ugrep and honors `.gitignore`, so an evidence scan silently misses files.
**How to avoid:** `/usr/bin/grep` in every `<automated>` block. Also note `firestarter_app/build/lib/` holds a **stale copy** of `diagnostic_report.py` and `chip_test.py` — a naive recursive grep hits it first. It is not tracked by git; always confirm a path with `git ls-files`.

---

## Code Examples

### The exclusion test (Leg B), cloned from the shipped `duration_s` idiom

```python
# Source: tests/test_diagnostic_report.py:1698-1716 (the shipped idiom)
def test_durations_do_not_perturb_dedup_fingerprint():
    from firestarter.diagnostic_report import dedup_fingerprint

    fast = _minimal_report(step_specs=[("read", VERDICT_OK, None, "")])
    fast.results[0].duration_s = 0.5

    slow = _minimal_report(step_specs=[("read", VERDICT_OK, None, "")])
    slow.results[0].duration_s = 987.654

    assert dedup_fingerprint(fast) == dedup_fingerprint(slow)
```

### The non-verdict exit-code term, as a precedence candidate

```python
# Source: firestarter/cli_handlers.py:2144-2157 (shipped)
    codes = {_verdict_code(r.verdict) for r in results}
    if sdp_oracle_not_run:
        codes.add(2)
    for code in _EXIT_CODE_PRECEDENCE:
        if code in codes:
            return code
    return 0
```

`_EXIT_CODE_PRECEDENCE: tuple[int, ...] = (1, 2, 0)` (`:2111`) — most-severe first, "an explicit precedence list, never a numeric `max`".

### The report-value-not-op-string docstring, to copy

```python
# Source: firestarter/chip_test.py:1962-1967 (shipped)
# Three-valued hold-state REPORT VALUES. These are report values, NOT op
# strings -- they
# carry no `OP_` prefix and must never join `_ALL_OPS`/`_MULTIWORD_OP_VALUES`
# in tests/test_op_registration_parity.py; a later reader must not
# "helpfully" register them there.
SDP_HOLD_HELD = "HELD"
```

(Reproduce the *content* as a docstring, not as `#` comments — project hard rule.)

### The absent-counter honesty guard, to mirror for the status fold

```python
# Source: firestarter/diagnostic_report.py:189-193 (shipped)
    for name in _SUSPECT_SCANNED_FIELDS:
        value = getattr(th, name)
        if value is not None and value >= _SUSPECT_THRESHOLD:
            return True
    return False
```

Its docstring states the rule this phase must inherit: *"Absent counters can never fabricate suspicion -- mirrors the honest `indeterminate` fingerprint bucket."*

---

## State of the Art

| Old approach | Current approach | When changed | Impact on this phase |
|---|---|---|---|
| One verdict axis, `BAD` for everything non-OK | OCP two-axis `TestStatus` × `TestResult`, four legal cells | OCP spec, current | The model ATTR-01 names |
| `FP_INDETERMINATE` on a clean write/verify | `FP_MATCH`, synthesized with zero I/O | Phase 177 (`RK-174-01/05/07`) | Three shapes re-keyed; the `RK-174-09` re-anchor exists because of it |
| `transport_health` counters all dormant | five of nine wired live | Phase 176 plans 01-03 | The corroborating signals of §6 |
| `--submit` flag | unconditional filing ask on every run | pre-v1.36 (`cli_handlers.py:2515-2519`) | ATTR-05's surface is already always-on |
| `--destructive` flag | deleted; every run writes | pre-v1.36 (`_make_sampler` docstring) | The sampler is built on every run |
| `_overall_exit_code` | superseded by `_dev_test_exit_code` | Phase with the SDP oracle floor | **`_overall_exit_code` (`cli_handlers.py:2114-2127`) has zero production call sites today** — only `_dev_test_exit_code` (`:2526`) is live. Do not wire the status axis into the dead one. |

**Deprecated / do not use:**
- `voltage.vpp_mv` / `voltage.vpe_mv` / `banner.locked_steps` — Phase 181 deletes them (RPT-B1/B2). Do not build on them.
- `firestarter_app/build/lib/` — a stale build copy; never cite it.
- The `chip_test.py:2461` anchor in `REQUIREMENTS.md` / `FEATURES.md` — stale, now `:2524-2541`.

---

## Environment Availability

| Dependency | Required by | Available | Version | Fallback |
|---|---|---|---|---|
| Python 3.11 venv at `firestarter_app/.venv311/` | every verify command (CI is py3.11-only) | ✅ | 3.11.16 | none needed |
| `firestarter` editable install resolving to the worktree | all tests | ✅ | `/workspaces/firestarter_app/firestarter/__init__.py` | none needed |
| `pytest` + `syrupy` snapshots | full suite | ✅ | 2216 tests, 32 snapshots, 320 s | none needed |
| `ruff` | CI gate | ✅ | `All checks passed!` / `171 files already formatted` | none needed |
| `mypy` watermark checker | CI gate | ✅ | **watermark 35**, 173 files checked, currently AT watermark | none needed |
| `python3` (system, meta repo) for `tools/rekey/check_rekey_ledger.py` | ATTR-04 primary gate | ✅ | exit 0, 8/8 rows bound | none needed |
| Firmware source `/workspaces/firestarter/` | ATTR-06 verification | ✅ | branch `gsd/v1.36-dev-test-fidelity` | none needed |
| PlatformIO / an Arduino board | — | **not required** | — | This is a **host-only** phase; nothing here needs hardware. |
| `.planning/graphs/graph.json` | optional context | ✅ present | — | — |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** none.

---

## Security Domain

`security_enforcement` is absent from `.planning/config.json` (treated as enabled). This phase is a host-side CLI change with no network listener, no auth surface, and no new external input.

| ASVS category | Applies | Standard control |
|---|---|---|
| V2 Authentication | no | no auth surface |
| V3 Session management | no | no sessions |
| V4 Access control | no | local CLI |
| V5 Input validation | **yes, narrowly** | The status axis becomes part of the **filed issue body** on a public tracker. `submit.sanitize_dict` (`submit.py:113-135`) deep-scrubs every string leaf via `_SCRUBS` (`:80-88`: home dirs, `/dev/tty*`, `COM\d+`, `/tmp/*`, the current username). Any new string field this phase exports **must** pass through `to_dict()` so the sanitizer sees it — that is automatic if it is a `to_dict()` key and never automatic if it is only rendered. |
| V6 Cryptography | no (non-security use) | `dedup_fingerprint`'s own docstring: "A non-secret dedup id, not a security control: sha256 is used for its distribution, truncated to 12 hex chars." |

| Threat pattern | STRIDE | Mitigation |
|---|---|---|
| A `reason` string from an exception leaking a device path (`/dev/ttyACM0`) into a public issue | Information disclosure | Already mitigated by `_SCRUBS` — but the status-axis *reason* text is new payload through the same sanitizer. `.planning/research/PITFALLS.md:470` names this: "Re-run the sanitizer's tests against a 1.8 body; confirm every new key is sanitizer-visible." |
| A misattributed public `FAIL` against a manufacturer's part | Repudiation / reputational | This phase's entire purpose. `PITFALLS.md:468` |
| Auto-classification hiding a real defect | Denial (of information) | ATTR-05; `PITFALLS.md:469` |

---

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|---|---|---|
| A1 | `INCONCLUSIVE (harness)` is the operator's preferred title shape for a transport fault | §4, §11 | Pitfall 10 supplies the example, but no operator decision exists. A different token needs the devtest-triage `SOFT` set widened (Phase 181's file). **Confirm at discuss/plan-check.** |
| A2 | `StepResult.status` (N-1) is the preferred field name | §10 | Pure naming; cheap to change before the shape is frozen, expensive after (the frozen snapshot pins the key). **Confirm before the shape is registered.** |
| A3 | `VERDICT_SKIPPED` is the right result-axis value for a transport fault | §11 | The table names the consequences of each alternative exhaustively; the choice is an operator call. Getting it wrong is a safety issue (C-1), not a cosmetic one. **Confirm at plan-check.** |
| A4 | Phase 178 does **not** bump `SCHEMA_VERSION` | §3, Open Q3 | Phase 181 owns `2.0` per D-3/RPT-E1, but an additive field arguably wants `1.8` first. Both parsers match `schema_version` by presence only and the dedup hash never reads it, so either is mechanically safe. **Confirm.** |
| A5 | `attr01-status-axis-transport-fault` is best built real-path (operator double raising `SerialError`) rather than hand-specified | §3 | A hand-specified shape would freeze a hash for a StepResult combination the engine might never produce. Real-path is more honest but couples the frozen hash to `derive_plan`. |
| A6 | Reviving `FP_TRANSPORT` is out of scope | §7 | If the operator reads criterion 1 as requiring a *fingerprint* status too, scope grows. The requirement text does not say so. **Confirm if in doubt.** |

---

## Open Questions

1. **Does "the overall verdict" in ATTR-03 include the process exit code?**
   - What we know: `submit.overall_verdict` (`submit.py:140`) is the *title* verdict; `_dev_test_exit_code` (`cli_handlers.py:2130`) is the *process* verdict. They already use different orderings, deliberately (`overall_verdict`'s docstring says so).
   - What's unclear: criterion 2 names only "the overall verdict and the auto-generated issue title". The exit code is not named.
   - Recommendation: widen **both**. An exit 0 on a run that did not execute validly is a false-green in scripts, and `_dev_test_exit_code`'s non-verdict-candidate pattern already exists to hold it (§11 C-7).

2. **Does `RK-174-09`'s `after_hash` stay `None` forever, or does Phase 178 "declare" something?**
   - What we know: `test_no_declared_row_has_after_hash_equal_to_before_hash` (`tests/test_rekey_ledger.py:332`) forbids `after == before`. `test_undeclared_after_hash_routes_to_before_hash_and_never_abstains` (`:358`) asserts the undeclared row still reproduces, and it guards against an *empty* undeclared subset — so at least one row must remain undeclared.
   - What's unclear: the ledger prose says `after_hash` "stays `None` until Phase 178 lands its own confirmation".
   - Recommendation: **leave it `None`.** The confirmation is the green gate plus MILESTONES.md prose recording that ATTR-04 was measured and held. If `RK-174-09` were declared, `test_undeclared_after_hash_routes_to_before_hash_and_never_abstains` would have `RK-174-02/03/04` left, so it would not go vacuous — but declaring a non-move is exactly what `:332` calls "a bookkeeping error, not a re-key".

3. **`SCHEMA_VERSION`: stay at `1.7`, or bump to `1.8`?**
   - What we know: `SCHEMA_VERSION = "1.7"` (`diagnostic_report.py:48`). Phase 181 sets `2.0` (RPT-E1, D-3, reversing 999.36's `1.8`). D-3's rationale: "both parsers accept `schema_version` by **presence only** … and the dedup hash never reads it."
   - Recommendation: **bump to `1.8`** — an exported key was added and the version should say so — and let Phase 181 take it to `2.0` on the deletions. But it costs nothing to stay at `1.7` either, and Phase 181's criterion 4 pins "the frozen schema-1.2 fixtures still parse unchanged". Operator call.

4. **Should `transport_suspect` participate in the status fold at all?**
   - What we know: it is threshold-based and whole-run scoped; three of its seven scanned counters are permanently `None` (§6).
   - Recommendation: **no** — report it, never derive status from it. Deriving status from a counter that can never be complete would fabricate the confidence Pitfall 10 warns about. The exception arm is the trigger.

5. **Does the status axis need a per-step *reason code* (the milestone's T4 "machine-readable reason key")?**
   - What we know: `.planning/research/SUMMARY.md:132` lists T4 as a Phase 178 deliverable. **No ATTR requirement mentions it.**
   - Recommendation: out of scope unless the operator asks. ATTR-01..06 is the contract; T4 has no requirement ID and adding an unrequested field grows the frozen-key surface. Record the deferral.

---

## Sources

### Primary (HIGH confidence) — opened with `Read`/`sed`/`git ls-files` this session

- `firestarter_app/firestarter/chip_test.py` — `:118-305` (`_diff_offsets`, `classify_fingerprint`, `_synthesized_match_fingerprint`), `:933-939` (verdicts), `:956-1042` (op frozensets), `:1046-1120` (`StepResult`, `_skip_result`, `REPEAT_POLICY_DEGRADED_TAG`), `:1268-1400` (cycle block bounds, `_aggregate_cycle_results`), `:1517-1650` (`_run_cycle_block`), `:1740-1830` (`run_plan` splice), `:1930-2045` (gate predicates, `sdp_hold_state`), `:2400-2560` (`_run_step`, the exception arms), `:2694-2740` (`_dispatch_read`), `:2990-3110`, `:3150-3240` (`_dispatch_multi_run`), `:3400-3540` (SDP-leg read-back), `:3575-3619` (`_RAN_VERDICTS`, `count_applicable`)
- `firestarter_app/firestarter/diagnostic_report.py` — `:40-160` (constants, `AutoCapture`, `TransportHealth`), `:160-226` (`_is_transport_suspect`, `is_submittable`), `:236-300` (`dedup_fingerprint`), `:309-384` (dispositions, `build_db_diff`), `:603-730` (`DiagnosticReport`, `_transport_dict`, `_voltage_dict`), `:760-800` (`_step_dict`, `to_dict`), `:940-1015` (`render`, `to_json_block`)
- `firestarter_app/firestarter/submit.py` — `:1-50` (module contract), `:80-135` (sanitizer), `:140-217` (`overall_verdict`, `build_title`, cell formatters), `:590-761` (`submit_report`)
- `firestarter_app/firestarter/cli_handlers.py` — `:2086-2160` (exit-code map and helpers), `:2209-2245` (`_is_interactive`, `_make_sampler`), `:2370-2531` (`dev_test`)
- `firestarter_app/firestarter/transport_counters.py` — `:1-60`
- `firestarter_app/firestarter/hardware.py` — `:380-450` (`_sample_one_voltage`, `sample_vpp_mv`, `sample_vpe_mv`)
- `firestarter_app/tests/test_blast_radius_invariance.py` — `:1-260`, `:520-620`, `:727-785`
- `firestarter_app/tests/test_rekey_ledger.py` — `:290-400`
- `firestarter_app/tests/fixtures/rekey_ledger.py` — full file (docstring + `LEDGER`)
- `firestarter_app/tests/fixtures/report_shapes.py` — `:112-185`, `:464-530`, `:599-701`
- `firestarter_app/tests/fixtures/shape_ids.json` — full file
- `firestarter_app/tests/test_op_registration_parity.py` — `:60-120`, `:320-375`
- `firestarter_app/tests/test_diagnostic_report.py` — `:207-330`, `:1698-1730`
- `firestarter_app/tests/test_dev_test_cmd.py` — `:2005-2060`
- `firestarter_app/tools/check_devtest_orchestrator.py` — `:1-60`, `:152-175`
- `firestarter_app/tools/check_diagnostic_report_claims.py` — `:1-160`
- `firestarter_app/tools/snapshot_report_shapes.py` — `:88-150`
- `firestarter_app/pyproject.toml` — `:76-190`
- `firestarter_app/.github/workflows/ci.yml` — `:45-115`
- `firestarter/src/hardware_operations.cpp` — `:1-60`
- `firestarter/include/rurp_pinout.h` — `:55-135`
- `firestarter/include/rurp_shield.h` — `:20-60`
- `/workspaces/tools/rekey/check_rekey_ledger.py` (run), `/workspaces/.github/workflows/rekey-ledger-check.yml`
- `/workspaces/.planning/MILESTONES.md` — `:32-49`
- `/workspaces/.planning/REQUIREMENTS.md` — `:20`, `:60-100`, `:127`, `:139`
- `/workspaces/.planning/ROADMAP.md` — `:340-430`
- `/workspaces/.planning/phases/177-evidence-gated-read-back/177-DECISIONS.md`, `177-02-SUMMARY.md`, `177-PATTERNS.md`
- `.claude/skills/devtest-triage/scripts/devtest_issues.py` — `:69-95`
- Measured probe (this session): `_dispatch_multi_run` receives `runs=1` on every fingerprint-bearing dispatch across `sst27sf512` / `at28c256` / `w27e257`

### Secondary (MEDIUM confidence) — milestone research, itself citing primary sources

- `/workspaces/.planning/research/FEATURES.md` — `:15-90` (the OCP two-axis table, quoted verbatim from `ocp-diag-core` `json_spec/README.md`), `:330-345` (anti-features A1-A9), `:346-380` (dependency graph), `:509` (source list)
- `/workspaces/.planning/research/PITFALLS.md` — `:316-341` (Pitfall 10, MEASURED against firmware), `:466-472` (risk table)
- `/workspaces/.planning/research/SUMMARY.md` — `:45-50`, `:125-140`

### Tertiary (LOW confidence)

- The OCP spec text is reproduced from `.planning/research/FEATURES.md`; the upstream `opencomputeproject/ocp-diag-core` `json_spec/README.md` was **not** re-fetched this session. The vocabulary names (`COMPLETE`/`ERROR`/`SKIP`, `PASS`/`FAIL`/`NOT_APPLICABLE`) are `[CITED: .planning/research/FEATURES.md:20-45]`, not independently `[VERIFIED]`. If the exact enum spelling becomes load-bearing (it will — it goes in a frozen snapshot), re-fetch the spec before freezing.

---

## Metadata

**Confidence breakdown:**

| Area | Level | Reason |
|---|---|---|
| Verdict vocabulary + all call sites | **HIGH** | Every constant and every read site opened and quoted verbatim; consumer census done with `/usr/bin/grep` |
| `dedup_fingerprint` composition | **HIGH** | Function read in full; pre-image pinned literally in a shipped test; exclusion mechanism is an explicit allow-list |
| Phase 174 oracle + ledger | **HIGH** | Both runners executed this session; 118 tests green; checker exit 0 |
| Issue title + submit prompt | **HIGH** | Both functions read in full; every early-return path enumerated |
| Phase 176 counters | **HIGH** | Sink and `TransportHealth` read in full, including the three permanently-`None` fields and their reasons |
| `FP_TRANSPORT` dead-code claim | **HIGH** | Structural proof by reading + a measured probe across three chips; falsification attempt failed to falsify |
| ATTR-06 firmware claim | **HIGH** | Firmware source read; correction C-1 raised; conclusion (no socket-routing bits) verified against the bit definitions |
| Verify commands | **HIGH** | All executed; outputs transcribed |
| Naming recommendation | **MEDIUM** | Grounded in OCP prior art, but no operator decision exists and there is no CONTEXT.md |
| OCP enum spelling | **MEDIUM** | Quoted from milestone research, not re-fetched from the spec |
| Which verdict a transport fault carries | **MEDIUM** | The *consequences* are HIGH (measured, table in §11); the *choice* is an operator call |

**Research date:** 2026-09-06
**Valid until:** 2026-10-06 for the codebase facts (stable, single active branch); the line citations are valid only against `gsd/v1.36-dev-test-fidelity` @ `0a29d8b` — re-verify after any commit to `chip_test.py`, `diagnostic_report.py` or `submit.py`.
