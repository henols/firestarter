# Phase 206: `dev test` keeps its fidelity, on one session - Research

**Researched:** 2026-09-23
**Domain:** Host-side Python CLI (`firestarter_app`) — report-identity hashing, verdict vocabulary, and serial-session lifetime. **Single repo. No firmware change. No new dependency.**
**Confidence:** HIGH on the measured substrate (every file:line below was opened and quoted this session against `firestarter_app` HEAD `2756ef0` on `v1.41-verification-to-host`); MEDIUM on the projected session saving (a derivation over Phase 203/205 measured medians, not a measurement); the SESS-02 number itself does not exist yet and must be measured on silicon.

<user_constraints>
## User Constraints

**There is no `206-CONTEXT.md`.** The user chose to plan without `/gsd-discuss-phase`, so **there are NO locked decisions for this phase.** Every design choice below is OPEN. This document names each fork, gives a recommendation with its evidence, and does not assume the recommendation was taken.

### Locked Decisions
None for this phase.

**Inherited and still binding** (milestone-level, from `project_v141_milestone_activated` and `.planning/ROADMAP.md`):
- **D-6 (milestone activation, 2026-09-20):** seed `dev-test-adaptive-sequencing` **R4** — one leased serial session per plan — is in scope. `[VERIFIED: .planning/seeds/dev-test-adaptive-sequencing.md §R4, read 2026-09-23]`
- **D-7 (milestone activation):** removing a command surface is not removing verification.
- Phases 202–205 are CLOSED; their decisions are the substrate, not re-openable here.

### Claude's Discretion
Everything. Seven forks are enumerated in **§ Open Design Forks** below (F1…F7), each with a recommendation. The planner should either take the recommendation and record it, or route the fork to the user.

### Deferred Ideas (OUT OF SCOPE)
Carried forward from `205-CONTEXT.md` § Deferred Ideas, which names Phase 206 as the home for two of them:
- **Collapsing `erase -b`'s second port open into the erase's own session** — named "Best home: Phase 206, SESS-01". `205-SESSION-COST.md` hands this phase the measured number (§ SESS-02 below).
- **The `DONE`-based clean stop in `op_wait_for_ack` (CMP-F1)** — named "Best home: Phase 206". **This is a FIRMWARE change.** ROADMAP marks Phase 206 `Repo: app`. Recommend leaving CMP-F1 filed and out of scope; it is not named by any of this phase's five requirements.
- Retiring the four orphaned catalog message ids — explicitly deferred to "any later phase already paying for a codegen run and two sub-repo syncs". Phase 206 pays for neither.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DEVTEST-01 | `OP_VERIFY` and `OP_BLANK_CHECK` route through the rewritten host methods and produce a fingerprint at least as informative as today's. | § Q2 — **the routing already happened in Phase 202**; what is left is the 0/1/2 verdict migration (two in-source `phase 206's job` markers) and the fact that `OP_BLANK_CHECK` carries **no fingerprint at all** today. Forks F1/F2. |
| DEVTEST-02 | a report from the host-side comparison path is distinguishable from one produced by the firmware path, using the established empty-default discriminator discipline, so no already-filed `dedup_fingerprint` group is silently re-keyed and no two mechanically different runs silently merge. | § Q3 — the discipline is quoted verbatim from `diagnostic_report.py:302-325` with its two shipped exemplars (`repeat_policy_tag`, `coverage_tag`) and their exact empty-default returns. § Pitfall 1 names the one change that would break it. Fork F4. |
| DEVTEST-03 | `dev test`'s step verdicts for a physically identical outcome do not change meaning; where a classification does change, the change is stated and justified rather than absorbed. | § Q4 — the complete enumerated verdict/status/classification vocabulary with line-anchored definitions, plus the 2922-case behavioural corpus Phase 202 left behind as the checkable instrument. § Pitfall 2 is a live false-green defect this migration makes reachable. Fork F3. |
| SESS-01 | a `dev test` plan opens one validated serial link and reuses it across its steps, instead of one open and teardown per call. | § Q5 — the exact teardown site, the `find_and_connect` connect/setup fusion that makes this non-trivial, the firmware-side proof that a leased link is feasible, and the four risks. Forks F5/F6. |
| SESS-02 | the wall-clock saving is measured on a real run and reported as a number; if it is not worth the structural change, that is recorded and the change is reverted rather than kept on principle. | § Q6 and § Q7 — the rig is present and identified, the before-figures exist in `205-SESSION-COST.md`, the project has a shipped connect-cost instrument, and the revert shape is specified. **This is an operator-initiated bench leg and must be planned as `checkpoint:human-verify`, never `<automated>`.** Fork F7. |
</phase_requirements>

---

## Summary

**The headline correction: the routing DEVTEST-01 asks for already happened.** Phase 202 moved both `verify_eprom` and `check_eprom_blank` onto `COMMAND_READ` + the host `CompareAccumulator`, and Phase 204 retired the firmware ordinals they used to compose. `dev test` calls those same two methods and therefore already runs on the host engine today. What Phase 202 deliberately left behind are **two one-line adapters** that flatten the new int verdict back to the old bool, each carrying an in-source comment naming this phase as its owner:

- `chip_test.py:2600` — `is_ok = operator.check_eprom_blank(name, eprom_data) == 0`, preceded by *"The real migration to the 3-way (0/1/2) verdict is phase 206's job … this arm still folds 1 (not blank) and 2 (refusal) into the same "not ok" branch exactly as the old False did."*
- `chip_test.py:3247-3256` — `outcomes.append(operator.verify_eprom(...) == 0)`, preceded by *"the real migration is phase 206's job."*

So DEVTEST-01/03 are not a routing job. They are a **verdict-vocabulary job**: give verdict `2` (transport / hardware refusal) somewhere honest to land, without letting a transport failure keep reading as a chip finding, and without moving any already-filed report's hash.

**The single highest-risk move in the phase is adding a fingerprint to the blank-check step.** `_dispatch_step`'s `OP_BLANK_CHECK` arm (`chip_test.py:2619-2625`) constructs its `StepResult` with **no `fingerprint=` keyword at all** — so `dedup_fingerprint` hashes that step as `blank-check=OK:` with an empty classification slot (`diagnostic_report.py:300-301`). Attaching a real `Fingerprint` there changes the triple to `blank-check=OK:blank/contact` — **not** `match`, because `classify_streamed` checks the blank/contact bucket *first* and an all-0xFF read is `ff_ratio == 1.0` (`compare.py:447-454`). That single change re-keys **all 19 frozen literals** in `tests/fixtures/report_shapes.py` and orphans every already-filed `henols/firestarter_prom` issue group, which is exactly what DEVTEST-02 forbids. **The fix is structural and already has a shipped precedent:** carry the new evidence in additive `StepResult`/`_step_dict` fields that `dedup_fingerprint`'s explicit five-entry allow-list does not read — the identical argument `_step_dict` already makes for its four `fingerprint_*` siblings (`diagnostic_report.py:849-855`).

**The "established empty-default discriminator discipline" is a real, named, twice-shipped pattern**, not a phrase to interpret. It lives in `dedup_fingerprint` itself and reads, verbatim: *"The empty-default direction is the whole point and is deliberate. Slot/fixed runs stay untagged, so every ALREADY-FILED report's fingerprint remains byte-identical and no historical `count_agreeing` group is re-keyed or reset. Only the newer, strictly-stronger full-device shape gets a tag."* (`diagnostic_report.py:314-318`). Its two exemplars both return the empty string for the *old/weaker* shape and a literal tag for the *new* one: `REPEAT_POLICY_DEGRADED_TAG = "runs=1"` (`chip_test.py:1029`) and `COVERAGE_TAG_FULL_DEVICE = "cov=full-device"` (`chip_test.py:1054`). A third tag for this phase must follow that shape exactly, and must key off a `StepResult` field whose **default is falsy**, so a report reconstructed from an old JSON artifact hashes byte-identically.

**SESS-01 is feasible and the firmware imposes no obstacle — but `find_and_connect` fuses three things that must be separated.** `firestarter.cpp:206-215` shows `command_done()` returning `handle.cmd = CMD_IDLE`, and `loop()` at `:218-257` reads the *next* framed command off the same open link with no reconnect required. The blocker is entirely host-side: `SerialCommunicator.find_and_connect(command_to_send, …)` opens the port, **sends the operation's setup command as the probe**, and validates firmware version and hardware revision off the resulting `MSG_OK_READY` ack (`serial_comm.py:967`, `:806-905`). A lease therefore needs the "send setup command + validate ack" half extracted so it can run a second time on an already-open port. The teardown that must become conditional is one line: `_operation_context`'s `finally: self._disconnect_programmer()` (`eprom_operations.py:704-705`).

**SESS-02's before-figures already exist and the rig is attached.** `/dev/ttyACM0` is an **Arduino Leonardo** (VID `9025`/`0x2341`, PID `32822`/`0x8036`) — the same board class `205-BENCH-MATRIX.md` used. The measured Leonardo-class connect median is **2.607 s** (`203-SESSION-COST.md` §2, cited by `205-SESSION-COST.md` §4) and `205-SESSION-COST.md` §5 gives this phase an explicit, pre-registered expectation: *"The saving SESS-01 should expect to measure is closer to the derivation's ~2.6s than to this document's ~10.6s, because most of this document's measured figure is read traffic that a leased session does not eliminate."*

**Primary recommendation:** sequence as *(1) the 3-way verdict migration + the `_aggregate_cycle_results` status-loss fix, host-only, no hash change → (2) the additive non-hashed fingerprint evidence for blank-check → (3) the empty-default `cmp=host` discriminator as its own commit, with the frozen-hash non-movement proven, not assumed → (4) the session lease behind ONE feature seam in ONE commit → (5) the bench measurement as a `checkpoint:human-verify` gate → (6) keep or `git revert` the single lease commit, and record the number either way.* Structure step 4 so step 6 is `git revert <one sha>`, not an unpick.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Byte-compare + divergence classification | Host / `compare.py` | — | Phase 202. Import-pure (`{__future__, dataclasses}` only, AST-enforced). This phase **consumes** it; it must not be widened. |
| Verify / blank verdict (0/1/2) | Host / `eprom_operations.py` | — | Phase 202 D-10. `_drive_region_compare` is the single drive; both methods already return the int. **Unchanged by this phase.** |
| Step verdict vocabulary (OK/BAD/NA/SKIPPED/marginal) + status axis | Host / `chip_test.py` (engine) | — | The engine owns adjudication. `cli_handlers` only *assigns* derived values — the "derive-in-engine / assign-in-handler" seam (`cli_handlers.py:2957-2959`). |
| Report identity (`dedup_fingerprint`) | Host / `diagnostic_report.py` | — | One function, explicit allow-list, no reflection. A new discriminator goes here and nowhere else. |
| Report rendering / issue body | Host / `diagnostic_report.render` + `submit.py` | — | Both read `to_dict()`; never a second field list. |
| Serial link lifetime (the lease) | Host / `eprom_operations.EpromOperator` | Host / `serial_comm.SerialCommunicator` | The teardown is `_operation_context`'s `finally`; the connect/setup fusion is `find_and_connect`. Both sides move or neither works. |
| Voltage sampling connects (4 per write step) | Host / `hardware.HardwareManager` | — | A **separate** class with its own `find_and_connect` + `disconnect` per call (`hardware.py:404`, `:434`). Outside `EpromOperator` entirely — deciding whether the lease reaches it is fork F5. |
| Command dispatch after an operation ends | Firmware / AVR | — | `command_done()` → `CMD_IDLE` → `loop()` reads the next frame. **No firmware change needed for the lease.** |
| Wall-clock measurement on silicon | Bench (operator) | — | No tier below the physical one can answer SESS-02. |

---

## Standard Stack

**This phase adds no dependency, in any ecosystem.** Everything it needs is already in the tree.

### Core (already present — use these, do not add)
| Module | Purpose | Why it is the standard here |
|--------|---------|------------------------------|
| `firestarter/compare.py` | `CompareAccumulator`, `CompareResult`, `Fingerprint`, `classify_streamed`, `FP_*` | Phase 202's single engine. `CompareResult.fingerprint` is **already populated by every `finalise()` call** (`compare.py:137-140`) — the evidence DEVTEST-01 wants exists without new computation. |
| `firestarter/eprom_operations.py` | `_drive_region_compare(..., on_result=…)` | The `on_result` callback (`eprom_operations.py:2592`, keyword-only, default `None`) is the **already-shipped seam** for handing a caller the finalised `CompareResult` instead of rendering it. Phase 203's write guard uses it. |
| `firestarter/chip_test.py` | `repeat_policy_tag`, `coverage_tag` | The two empty-default discriminators DEVTEST-02 must copy. |
| `firestarter/diagnostic_report.py` | `dedup_fingerprint`, `_step_dict` | The hash and the additive-field precedent. |
| `tests/fixtures/report_shapes.py` | `FROZEN_HASHES` (19 literals) | The re-key detector. |
| `tests/test_blast_radius_invariance.py` | `test_dedup_fingerprint_is_frozen` | The gate that turns "no re-key" from an intention into a test. |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| A new `StepResult` field for the blank-check evidence | Reusing the existing `fingerprint` field | Simpler, but **re-keys all 19 frozen hashes and every filed issue group**. DEVTEST-02 forbids it. Rejected. |
| An empty-default `cmp=host` tag | A `schema_version` bump | `SCHEMA_VERSION = "2.2"` (`diagnostic_report.py:52`) is **not** in `dedup_fingerprint`'s pre-image, so bumping it distinguishes nothing for dedup. Does not satisfy DEVTEST-02. |
| A lease seam inside `EpromOperator` | A `contextlib` session context manager at `run_plan` | Equivalent; `run_plan` is the natural boundary the seed names. Either is acceptable — keep it to ONE seam either way (F7). |

**Installation:** none. `pip install -e '.[test]'` is the existing dev setup.

## Package Legitimacy Audit

**Not applicable — this phase installs zero external packages.** No `npm`/`pip`/`cargo` command appears anywhere in this document. The Package Legitimacy Gate was not run because there is nothing to submit to it. If a plan later proposes a dependency, run the gate then.

**Packages removed due to `[SLOP]` verdict:** none (none proposed).
**Packages flagged as suspicious `[SUS]`:** none (none proposed).

---

## Project Constraints (from CLAUDE.md)

Extracted from `/workspaces/CLAUDE.md`, `/workspaces/firestarter_app/CLAUDE.md`. Treat with the same authority as a locked decision.

| Directive | Source | Bearing on this phase |
|---|---|---|
| **Never commit to `beta` or `main`. Milestone work forks off `beta` on `v1.X-slug` in all three repos.** | meta CLAUDE.md § Milestone close | Work on `v1.41-verification-to-host`, which is already checked out. |
| **A push to `beta` in `firestarter_app` PUBLISHES to PyPI.** No path filter. A version can never be reused. | meta CLAUDE.md | Nothing in this phase pushes. GSD pushes at ship time only. |
| **App CI is Python 3.11 ONLY.** The devcontainer default is 3.12 and masks CI failures. | app CLAUDE.md | `firestarter_app/.venv311` exists and is **Python 3.11.16** `[VERIFIED: run this session]`. Every verification leg must run through it, never bare `python3`. |
| CI gates are exactly: `ruff check`, `ruff format --check`, `pytest --cov --cov-fail-under=70`, an install smoke test. **mypy is NOT a CI gate.** | app CLAUDE.md § What CI runs | A plan that gates on mypy is gating on something CI does not run. mypy *is* in local pre-commit. |
| `ruff` `select` is `[E,F,I,UP]`; `E501` ignored. A `# noqa` outside that selection is **inert**. | app CLAUDE.md | Do not add `# noqa: BLE001`; it does nothing. |
| `ruff` lints only `firestarter/` and `tests/`. **`tools/` is outside every CI gate.** | app CLAUDE.md | Do not put a measurement script in `firestarter_app/tools/` and call it covered. |
| `firestarter/data/chip_database.json` is **GENERATED** by `build_db.py`. Never hand-edit. | meta + app CLAUDE.md | This phase does not touch the DB. Named because the area is adjacent. |
| **Messages are generated ONLY in the meta repo** from `tools/catalog/messages.toml`. Never regenerate or hand-edit `messages.py`/`messages.h` in a sub-repo. | meta CLAUDE.md § Cross-repo obligations | `resolve_error_name` reads `messages.CATALOG`. Reading is fine; **adding a message id is a meta-repo codegen run plus two syncs** and would make this a three-repo phase. Avoid. |
| Constants and flag bits are duplicated host↔firmware; change both sides in the **same commit pair**. | meta CLAUDE.md | This phase introduces **no wire constant**. The op strings and tags are engine-local — `chip_test.py:267-273` states this explicitly: *"Engine-local op strings, NOT wire constants — no `constants.py` / `firestarter.h` mirroring is triggered by adding these."* Keep it that way. |
| The no-comments-in-source rule was **REMOVED 2026-09-19.** Comments are allowed again in both sub-repos. `.planning/` references to it are historical. | meta CLAUDE.md | This codebase is comment-dense and the comments are load-bearing design records. Write them. |
| Issue tracking is centralized in `henols/firestarter_prom`; `dev test --submit` files there. | meta CLAUDE.md | This is where a `dedup_fingerprint` re-key does its real-world damage. |
| **The meta repository must never publish a GitHub Release — bare tags only.** | meta CLAUDE.md | Not this phase's job, but do not let a plan add one. |

---

## Measured Substrate — the seven questions, answered with evidence

All line numbers verified against `firestarter_app` HEAD `2756ef0` and `firestarter_fw` working tree, read this session with `sed`/`awk` under `cat -n`-equivalent numbering. Scans used `git grep`, **never** the devcontainer's ugrep-backed `grep`, which honours `.gitignore` and silently under-scans.

### Q1 — Where `dev test` lives, and how a step verdict is produced today

| Concern | Location | Note |
|---|---|---|
| CLI command | `firestarter_app/firestarter/cli_handlers.py:2876` `def dev_test(app, chip, fast, submit)` | Click command registered at `cli_handlers.py:2849` as `@dev.command(name="test")`. |
| Default repeat count | `cli_handlers.py:2845` — `_DEFAULT_RUNS = 3` | **Three, not two.** `.planning/notes/dev-test-sequence-cost-model.md` models `runs=2`; it predates commit `b596249 feat(dev-test): default the run count to three`. Every figure in that note must be re-scaled. `[VERIFIED: cli_handlers.py:2845; git log --oneline -- tests/test_blast_radius_invariance.py]` |
| Plan derivation | `chip_test.py:426` `derive_plan(name, db, *, write_scope)` | Pure over frozen DB fields; never opens a port. |
| Plan execution | `chip_test.py:1574` `run_plan(plan, operator, db, *, runs=2, allow_single_run=False, sampler=None)` | One step at a time; each step's failure is non-fatal. |
| The repeat cycle | `chip_test.py:1452` `_run_cycle_block(...)` | **Calls `_run_step(..., runs=1, ...)` at `chip_test.py:1528-1533`** — the reason `runs` is effectively 1 inside `_dispatch_multi_run`. |
| Per-step timing wrapper | `chip_test.py:2402` `_run_step` | Stamps `duration_s`; wraps in `log_capture.step_scope`. |
| Exception→verdict mapping | `chip_test.py:2452` `_run_step_untimed` | Four arms — see Q4. |
| Op dispatch | `chip_test.py:2543` `_dispatch_step` | Six arms in a **locked order**: `OP_ID` → `OP_BLANK_CHECK` → `OP_READ` → `_MULTI_RUN_OPS` → `_SDP_OPS` → `_SDP_LEG_OPS` → terminal fail-closed refusal. |
| Multi-run dispatch (write/verify/erase) | `chip_test.py:3064` `_dispatch_multi_run` | Where `OP_VERIFY` lives. |
| Cycle fold | `chip_test.py:1248` `_aggregate_cycle_results` | Folds N per-cycle `StepResult`s into one. **See Pitfall 2.** |
| `dedup_fingerprint` | `diagnostic_report.py:273` | 12-char sha256 prefix. |
| `classify_fingerprint` | `chip_test.py:145` | A thin wrapper delegating to `compare.classify_streamed` since 202-03. |
| Report body / issue title | `submit.py:371` `build_body`, `submit.py:179` `build_title` | Title embeds the shorthash: `f"[dev test] {name} — {verdict} ({shorthash})"` (`submit.py:197`). |
| Dedup query against the tracker | `submit.py:538` `find_prior_report(fingerprint, …)` | Read-only `gh issue list` keyed on the fingerprint. **This is where a re-key becomes visible to the community.** |

**`dedup_fingerprint`'s exact hash input** — quoted verbatim from `diagnostic_report.py:297-327`:

```python
    ac = report.auto_capture
    parts = [ac.chip or "", str(ac.protocol or "")]
    for result in report.results:
        cls = result.fingerprint.classification if result.fingerprint else ""
        parts.append(f"{result.op}={result.verdict}:{cls}")
    …
    policy = repeat_policy_tag(report.results)
    if policy:
        parts.append(policy)
    …
    coverage = coverage_tag(report.results)
    if coverage:
        parts.append(coverage)
    canonical = "|".join(parts)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:12]
```

So the pre-image is exactly: `chip | protocol | (op=verdict:classification)×N | [runs=1] | [cov=full-device]`. **Five entries, explicit allow-list, zero reflection.** Everything else on the report — `status`, `duration_s`, `error_code`, `reason`, `chip_id_detected`, `is_uv`, the four `fingerprint_*` siblings, `write_*` — is excluded, and its exclusion is the *absence* from this list.

### Q2 — What `OP_VERIFY` and `OP_BLANK_CHECK` are today

**They are engine-local step-op *strings*, not firmware ordinals.** `chip_test.py:261` `OP_BLANK_CHECK = "blank-check"` and `chip_test.py:264` `OP_VERIFY = "verify"`. The firmware ordinals that used to back them — `CMD_BLANK_CHECK` (4) and `CMD_VERIFY` (6) — **were retired from both sides by Phase 204** (FWCMD-01/02/03, all `[x]` in `REQUIREMENTS.md:65-67`). Nothing anywhere composes them now.

**What each dispatches to today:**

| Op | Dispatch site | Operator method | Wire command | Returns |
|---|---|---|---|---|
| `OP_BLANK_CHECK` | `chip_test.py:2592-2625` | `EpromOperator.check_eprom_blank` (`eprom_operations.py:3011`) | `COMMAND_READ` | `int` — 0 blank / 1 not blank / 2 refusal-or-transport |
| `OP_VERIFY` | `chip_test.py:3247-3256` | `EpromOperator.verify_eprom` (`eprom_operations.py:2707`) | `COMMAND_READ` | `int` — 0 match / 1 mismatch / 2 setup/transport/IO |

Both already funnel into the one host drive, `EpromOperator._drive_region_compare` (`eprom_operations.py:2584`), whose docstring states it plainly: *"The one host-side compare drive `verify_eprom` and `check_eprom_blank` share (202-05 D-02)… everything past that point (the abort predicate, the D-08 abort-vs-fault discrimination, the D-13/D-14 rendering, and the D-10 int verdict) is identical for both."*

**What `dev test` currently receives back, and what it throws away:**

- **`OP_VERIFY`** — receives only the int, adapted to a bool by `== 0` (`chip_test.py:3252-3256`). Its `Fingerprint` comes from a **second, separate device read**: `chip_test.py:3278-3290` calls `_read_region` (`chip_test.py:2819` → `operator.read_eprom` into a temp dir) and re-classifies with `classify_fingerprint`. On a step that passed, no read happens at all — `chip_test.py:3292` substitutes `_synthesized_match_fingerprint(region_length)` (`chip_test.py:179`), classification `FP_MATCH`, `ff_ratio: None`.
- **`OP_BLANK_CHECK`** — receives only the int, adapted by `== 0` (`chip_test.py:2600`). **It attaches no `Fingerprint` whatsoever.** The `StepResult` at `chip_test.py:2619-2625` is constructed with exactly five keywords: `op`, `verdict`, `reason`, `error_code`, `run_count`. No `fingerprint=`.

**The discarded evidence.** `_drive_region_compare` finalises a `CompareResult` (`eprom_operations.py:2685`) and either renders it or hands it to `on_result` — and `CompareResult.fingerprint` is populated on **every** `finalise()` call. `compare.py:137-140`, verbatim:

```
    fingerprint: Fingerprint | None = None
    """Populated by `CompareAccumulator.finalise()` via `classify_streamed`
    (202-03) -- every `finalise()` call sets this, clean or mismatching, so a
    caller never has to ask separately."""
```

Plus, on the same object: `compared`, `compared_start`, `compared_end`, `bad`, `ranges` (coalesced, capped at `MAX_RETAINED_RANGES = 64`, `compare.py:33`), `extra_ranges`, `extra_bytes`, `aborted`, `ff_count`, `first_offset`, `first_actual`, `bit_set_counts`. **All of it is discarded today.** `verify_eprom` and `check_eprom_blank` both pass no `on_result`, so it is rendered to the log and dropped.

**Therefore "a fingerprint at least as informative as today's" has a concrete, checkable definition:**

| Step | Today's information | Floor the phase must not go below | Free upside available |
|---|---|---|---|
| `OP_VERIFY`, step passed | synthesized `match`, `total=region_length`, `bad=0`, `ff_ratio=None` | same five keys, same `match` classification | a **real measured** `ff_ratio` from the verify's own compare, at zero extra I/O |
| `OP_VERIFY`, step failed | real `Fingerprint` from a **whole-region** `_read_region` re-read, `repeat_divergent` supplied | full-region distribution; `bit_clustering` over every candidate bit | the verify's own `CompareResult` describes **the same read that produced the verdict** — but only if `full=True` (see Pitfall 3) |
| `OP_BLANK_CHECK` | **nothing** | nothing — any addition is strictly more | `bad`, `first_offset`, `first_actual`, `ranges` — the exact "which address, what value" datum the retired firmware `MSG_ERR_NOT_BLANK` used to carry, which `chip_test.py:2601-2611` records as *"the single most useful datum in a `dev test` failure"* |

### Q3 — The "established empty-default discriminator discipline"

It is an in-source, named, twice-applied pattern. **Where it is established:** `diagnostic_report.dedup_fingerprint`'s own body comments. Verbatim, `diagnostic_report.py:302-322`:

```
    # Repeat-policy discriminator. A single-run report is a strictly weaker test:
    # nothing can be marginal and no read divergence is computed. The tag keeps it
    # out of the promotion group, so two fast runs can never promote a chip no
    # accurate run ever passed. The tag is empty for the default policy and the
    # append is skipped, so accurate runs keep their existing fingerprints.
    …
    # The empty-default direction is the whole point and is deliberate.
    # Slot/fixed runs stay untagged, so every ALREADY-FILED report's
    # fingerprint remains byte-identical and no historical `count_agreeing`
    # group is re-keyed or reset. Only the newer, strictly-stronger
    # full-device shape gets a tag. This is the same discipline quick task
    # 260822-aq6 applied to `repeat_policy_tag` above ("returns `""` for
    # the default policy and the append is skipped entirely... no
    # historical group is re-keyed"), and the deliberate difference from
    # an accepted full re-key.
```

**Its two shipped exemplars**, both in `chip_test.py`:

```
1029: REPEAT_POLICY_DEGRADED_TAG = "runs=1"
1032: def repeat_policy_tag(results: list[StepResult]) -> str:
1047:             return REPEAT_POLICY_DEGRADED_TAG
1048:     return ""

1054: COVERAGE_TAG_FULL_DEVICE = "cov=full-device"
1057: def coverage_tag(results: list[StepResult]) -> str:
1077:                 return COVERAGE_TAG_FULL_DEVICE
1078:             return ""
1079:     return ""
```

Each function's docstring states the load-bearing property. `repeat_policy_tag`, `chip_test.py:1041-1044`: *"Returning `""` for the default is load-bearing: `dedup_fingerprint` appends this tag only when non-empty, so an accurate run's fingerprint stays byte-identical to those already filed and no historical grouping resets."* `coverage_tag`, `chip_test.py:1075-1077`: *"Returning `""` for fixed/uv-slot is load-bearing for the same reason as `repeat_policy_tag` above: only the strictly-stronger full-device shape gets tagged, so no historical grouping is re-keyed."*

**The direction the new discriminator must take.** Every already-filed report was produced by the **firmware** comparison path. Therefore:

- **firmware path / unknown / legacy → `""`** (untagged; append skipped; existing hashes unmoved)
- **host path → a literal tag** (e.g. `"cmp=host"`)

and it must be derived from a `StepResult` field whose **default is falsy**, so a `StepResult` reconstructed from a pre-206 JSON artifact — or hand-built in `tests/fixtures/report_shapes.py`, which is how all 19 frozen hashes are produced — takes the untagged branch automatically. That is what makes the 19 literals provably immobile rather than hopefully immobile.

**Confirmed: the 19 literals have not moved through Phases 202–205.** `git log --oneline -- tests/fixtures/report_shapes.py` shows the last hash-value change at `b35481c feat(179-02)`; commits `92f9cbe` (202-05), `9a82478` (205-04) and `c7c1d9a` touched the file with **zero** 12-hex-char value diffs. `[VERIFIED: git show 92f9cbe -- tests/fixtures/report_shapes.py | grep -E "^[-+].*[0-9a-f]{12}"` returned empty, run this session]`

**The 19 frozen literals** (`tests/fixtures/report_shapes.py:736-756`), verbatim:

```
FROZEN_HASHES: dict[str, str] = {
    "sst27sf512-six-step": "7fb88e0b07d6",
    "sst27sf512-six-step-readback-gated": "ff974e416dca",
    "gh47-sst27sf512-pass": "f9dbc31dcd27",
    "gh28-m27c512-fail": "31547956e56b",
    "gh20-at28c256-fail": "00e121446ceb",
    "gh23-w27e257-fail": "7a89fcea856a",
    "synthetic-arm4-no-ok": "f90dfe1a44f7",
    "synthetic-arm4-empty-results": "8d6208d00be7",
    "m27c512-full-all-ok": "6d3afbc52315",
    "m27c512-full-blank-check-bad": "e42f1567967a",
    "m27c512-full-canonical-name": "776846bf2dc8",
    "m27c512-full-comma-joined-name": "37ad34d39a19",
    "m27c512-full-runs-1": "e4838f7bb1d3",
    "at28c256-full-all-ok-sdp": "050ad3830704",
    "sst27sf512-full-all-ok": "14d306256076",
    "w27e257-full-all-ok": "3a9f95aba65e",
    "prune03-synthesized-fingerprint-match": "3b83a55efb3a",
    "attr01-status-axis-transport-fault": "93cef8030c40",
    "uv-slot-write-pass": "927571e5110f",
}
```

**The gate.** `tests/test_blast_radius_invariance.py:313` `test_dedup_fingerprint_is_frozen(shape_id, expected)` compares a real `dedup_fingerprint` output against an **absolute pre-declared literal**, never against a second computed value — the module's opening docstring states that relational comparisons "pass vacuously through ANY change to the hash function itself" and that eleven such relational comparisons already ship in `tests/test_diagnostic_report.py`. **A plan must gate on `test_blast_radius_invariance.py`, not on `test_diagnostic_report.py`.** The module also carries the two-commit rule verbatim in its own failure message: *"If deliberate, land the behaviour change and the re-key of this literal as SEPARATE commits, so the re-key stays a reviewable unit."*

**The accepted-re-key precedent, for contrast.** `diagnostic_report.py:255-270` records the SDP leg's deliberate full re-key: six new steps *"necessarily re-key every one of the 43 measured ALLOW chips through the hashed `op=verdict:cls` triples below — b14/b15-era reports stop grouping with v1.30-era ones and their accumulated N>=2 promotion counts reset; gh#20's orphaned id `00e121446ceb` is a recorded instance."* That is what an *accepted* re-key looks like — recorded, argued, with the two rejected alternatives named. DEVTEST-02 asks for the **opposite** disposition this time.

### Q4 — Every step verdict / classification `dev test` can emit today

Three orthogonal axes. Enumerating all three is what makes DEVTEST-03 checkable.

**Axis 1 — `StepResult.verdict`** (`chip_test.py:803-807`, verbatim):
```
VERDICT_OK = "OK"
VERDICT_BAD = "BAD"
VERDICT_NA = "NA"
VERDICT_SKIPPED = "SKIPPED"
VERDICT_MARGINAL = "marginal"
```
Five values. Their exit-code contribution (`cli_handlers.py:2621-2627`, verbatim):
```
_VERDICT_EXIT_CODES = {
    VERDICT_OK: 0,
    VERDICT_NA: 0,
    VERDICT_SKIPPED: 0,
    VERDICT_MARGINAL: 2,
    VERDICT_BAD: 1,
}
```
walked through `_EXIT_CODE_PRECEDENCE: tuple[int, ...] = (1, 2, 0)` (`cli_handlers.py:2639`) — **BAD (1) outranks marginal (2) outranks clean (0)**, an explicit precedence list, never `max()`. `_RAN_VERDICTS = frozenset({VERDICT_OK, VERDICT_BAD, VERDICT_MARGINAL})` (`chip_test.py:3664`) — NA and SKIPPED never counted as having run.

**Axis 2 — `StepResult.status`** (`chip_test.py:820-822`, verbatim):
```
STATUS_COMPLETE = "COMPLETE"
STATUS_ERROR = "ERROR"
STATUS_SKIP = "SKIP"
```
Folded to two values at run level by `run_status` (`chip_test.py:1992-2009`): `STATUS_ERROR` if any step's status is `STATUS_ERROR`, else `STATUS_COMPLETE`. That fold feeds `_dev_test_exit_code`'s `run_status_error` term (`cli_handlers.py:2658`, `codes.add(2)`).

**Axis 3 — `Fingerprint.classification`** (`compare.py:46-50`, verbatim):
```
FP_BLANK_CONTACT = "blank/contact"
FP_ADDRESS_LINE = "address-line"
FP_TRANSPORT = "transport"
FP_INDETERMINATE = "indeterminate"
FP_MATCH = "match"
```
Classification order is **LOCKED** in `classify_streamed` (`compare.py:396-511`): blank/contact → address-line → match → transport → indeterminate. Thresholds: `_FF_RATIO_THRESHOLD = 0.98`, `_BIT_CLUSTER_THRESHOLD = 0.9` (`compare.py:56-58`).

**The complete verdict-production map (every path a `StepResult` can take today):**

| # | Producer | Verdict | Status | Trigger |
|---|---|---|---|---|
| 1 | `_dispatch_id` `chip_test.py:2687` | OK / BAD | COMPLETE | `check_eprom_id` false **or** detected id ≠ DB expected |
| 2 | `_dispatch_step` blank-check `:2613-2618` | **OK** | COMPLETE | `check_eprom_blank(...) == 0` |
| 3 | same | **SKIPPED** | COMPLETE | `!= 0` **and** `step.uv_prewrite` (a non-blank UV part) |
| 4 | same | **BAD** | COMPLETE | `!= 0` otherwise — **folds verdict 1 and verdict 2 together.** This is the defect the todo names. |
| 5 | `_dispatch_read` `:2774` | OK / BAD | COMPLETE | last run's `read_eprom` return. Divergence is a metric, never a verdict flip. |
| 6 | `_dispatch_multi_run` `:3320` | OK / BAD | COMPLETE | `outcomes[0]` after the `== 0` adapters |
| 7 | same `:3307-3309` | **marginal** | COMPLETE | `len(set(outcomes)) != 1` — **unreachable under `_run_cycle_block`, see below** |
| 8 | same `:3180`, `:3202` | SKIPPED | **SKIP** | write target saturated/refused; verify with no inherited target |
| 9 | `_dispatch_multi_run` guard `:3138` | BAD | COMPLETE | op not in `_MULTI_RUN_OPS` (fail-closed) |
| 10 | `_dispatch_step` terminal `:2676` | BAD | COMPLETE | op matched no dispatch arm (fail-closed) |
| 11 | `_run_step_untimed` `:2521-2528` | **SKIPPED** | **ERROR** | `SerialError` / `HardwareOperationError` — the two-axis transport fault |
| 12 | `_run_step_untimed` `:2529-2536` | BAD | COMPLETE | `EpromOperationError` (carries `error_code`) |
| 13 | `_run_step_untimed` re-raise | *(propagates)* | — | `ProgrammerNotFoundError` / `FirmwareOutdatedError` / `HardwareRevisionUnsupportedError` — run-fatal, must stay first |
| 14 | `_skip_result` `:1012` | SKIPPED (or NA) | SKIP | unsupported step, closed destructive gate, resolve refusal |
| 15 | `_run_cycle_block` `:1494-1497` | NA / SKIPPED | SKIP | `not step.supported`; gated destructive op |
| 16 | `_aggregate_cycle_results` `:1288-1292` | **marginal** | **COMPLETE (bug, see Pitfall 2)** | cycles disagreed |
| 17 | `run_plan` `:1625` | BAD, op `__plan__` | COMPLETE | `runs < 2` without `allow_single_run` |
| 18 | `_dispatch_sdp` `:3381` / `_dispatch_sdp_leg` | OK / BAD / SKIPPED | varies | the six SDP-leg ops |

**The `transport` bucket and `_MULTI_RUN_OPS` marginal are structurally dead — measured, not assumed.** `_run_cycle_block` calls `_run_step(..., runs=1, ...)` at `chip_test.py:1528-1533`, so `outcomes` inside `_dispatch_multi_run` is always a one-element list, `diverged` is permanently `False` (`chip_test.py:3284`, `:3300`), `repeat_divergent=False` reaches `classify_streamed`, and `FP_TRANSPORT` at `compare.py:497-504` can never be selected. `VERDICT_MARGINAL` survives only via `_aggregate_cycle_results` (row 16), which compares *cycles*, not runs. This matches `reference_classify_fingerprint_transport_bucket_unreachable` (Phase 177 review finding WR-01, confirmed 2026-09-05).

**Does this phase touch it?** **Recommend NO.** None of DEVTEST-01/02/03 or SESS-01/02 names the transport bucket, and `repeat_divergent` is not something a leased session or a 3-way verdict changes. But the phase record should **state** the bucket is still dead after the phase, because a reader seeing "transport failure now has a distinct verdict" will reasonably assume `FP_TRANSPORT` became live, and it did not. Fixing it means re-plumbing `runs` through the cycle loop, which is a separate, larger change with its own fidelity argument.

**The instrument that makes DEVTEST-03 checkable rather than aspirational.** Phase 202-03 ran the real pre-refactor `classify_fingerprint` out of git against the new one over **2922 generated cases spanning all five buckets, with zero differences**, and the milestone memory records the explicit instruction: *"That corpus is what protects DEVTEST-03 when phase 206 routes `dev test` through this code — re-run it rather than trusting the in-suite 12-row corpus alone."* `[CITED: project_v141_phase202_closed memory; corpus lives in tests/test_compare.py D-03]` **The planner should make re-running that corpus an explicit task, not an assumption.**

### Q5 — How a serial link is opened today (SESS-01)

**Who owns the port.** `SerialCommunicator` (`serial_comm.py:114`) owns a `serial.Serial`. `EpromOperator` holds **at most one at a time**, in `self.comm`, declared `self.comm: SerialCommunicator | None = None` at `eprom_operations.py:435`.

**The per-call open.** `_operation_context` (`eprom_operations.py:657`) → `_setup_operation` (`:561`) → `SerialCommunicator.find_and_connect(command_dict, self.config, …)` at `eprom_operations.py:639`.

**The per-call teardown — one line, one place.** `eprom_operations.py:701-705`, verbatim:

```python
        try:
            # Yield the necessary data to the 'with' block
            yield command_dict, buffer_size, operation_name
        finally:
            # This block ensures disconnection happens even if errors occur
            self._disconnect_programmer()
```

and `eprom_operations.py:707-710`, verbatim:

```python
    def _disconnect_programmer(self):
        if self.comm:
            self.comm.disconnect()
            self.comm = None
```

`SerialCommunicator.disconnect()` (`serial_comm.py:613-624`) calls `consume_remaining_input()` then `self.connection.close()` and nulls `programmer_info`.

**Is there already a lease/reuse seam? No — and the near-misses prove the need.**
- `preferred_port` / `restrict_to_port` (203-CR-01, `eprom_operations.py:577-592`) pin a *later* connect to the *same port* a previous connect reached. `write_eprom` stores `self.last_write_port` (`:2478`) and `cli_handlers.write`'s `--verify` branch feeds it back. That is a **port-identity** workaround for the absence of a lease, not a lease. A leased link makes it structurally unnecessary.
- `EpromOperator` carries five transient per-invocation attributes (`last_firmware_error_code`, `last_firmware_error_message`, `last_write_guard_verdict`, `last_write_attempt_verdict`, `last_write_port`, `eprom_operations.py:445-503`) that exist precisely because `self.comm` is gone by the time a caller could read it. `reference_operator_comm_torn_down_ack_unobservable` records this as a measured fact.

**The real blocker: `find_and_connect` fuses three responsibilities.** `serial_comm.py:967` `find_and_connect(cls, command_to_send, config_manager, preferred_port=None, baud_rate=…, fault_inject_outgoing=None, allow_outdated_firmware=False, restrict_to_port=None)`. It (a) walks candidate ports, (b) **sends the operation's own setup command as the probe** — `_probe_port` at `serial_comm.py:806`, `communicator.send_json_command(command_to_send)` then `expect_ack()` — and (c) validates firmware version and hardware revision off the resulting `MSG_OK_READY` ack, which also populates `firmware_max_chunk`, `hw_revision`, `firmware_identity` and `write_block_budget_s` (`serial_comm.py:163-186`). `_probe_port`'s own comment names the fusion as deliberate: *"The dedicated CMD_FW_VERSION pre-probe this replaces cost a full command exchange (2 acks) on every single connect; MSG_OK_READY now carries the firmware identity AND the effective hardware revision, so both gates run off the ack this command was going to produce anyway."*

A leased link therefore needs **step (b)+(c) extracted so they can run a second, third, Nth time on an already-open port** — e.g. `SerialCommunicator.setup_command(command_dict, config) -> bool`, with `_probe_port` calling it for the cold path.

**Cost of the per-call open, measured.** `CONNECTION_STABILIZE_DELAY = 2.0` seconds (`serial_comm.py:84`), slept unconditionally inside `SerialCommunicator.__init__` at `serial_comm.py:204`. That 2.0 s is the bulk of the measured **2.607 s Leonardo-class / 2.518 s Uno-class** connect medians (`203-SESSION-COST.md` §2, N=10 per class, port pinned). Phase 205's own note states the structural floor as 2.500 s.

**The firmware does not require a reconnect.** `firestarter_fw/src/firestarter.cpp:206-215`:

```c
void command_done(firestarter_handle_t* handle) {
    LOG_DEBUG_ID_SUB(DBG_CMD_FINISHED);
    rurp_set_programmer_mode();
    rurp_chip_disable();
    rurp_write_to_register(CONTROL_REGISTER, 0x00);
    rurp_write_to_register(LEAST_SIGNIFICANT_BYTE, 0x00);
    rurp_write_to_register(MOST_SIGNIFICANT_BYTE, 0x00);
    handle->cmd = CMD_IDLE;
    rurp_set_communication_mode();
}
```

and `loop()` at `firestarter.cpp:218-257` reads the next COBS-framed command whenever `handle.cmd == CMD_IDLE`. **A second setup command on the same open link is exactly what the firmware already expects.** `[VERIFIED: firestarter_fw/src/firestarter.cpp:206-257, read 2026-09-23]`

**What DTR does — and why the lease changes board behaviour.** `reference_held_rail_dtr_reset_hold_script` (RCA'd v1.18 Phase 97) records, measured: *"Host `finally: _disconnect_programmer()` closes the port → pyserial de-asserts **DTR → resets the ATmega32u4** → control latch zeroes → rail drops to ~0V."* So on the attached Leonardo, **every step boundary today includes a board reset.** A lease removes ~30 resets from a plan. That is the saving — and it is also the fidelity risk: a step that passes today partly because the previous step's teardown reset the board would behave differently under a lease. `_probe_port` also carries an Uno-class DTR artifact: a spurious `GENERIC_FRAME_DECODE_ERROR_TEXT` frame that costs up to `SETUP_ACK_RECOVERY_TIMEOUT_S = 2.0` s to read past (`serial_comm.py:852-864`).

**The smallest honest "one leased link per plan".** Recommended shape, five edits, one feature flag:

1. Extract `_probe_port`'s send-setup-command-and-validate half into `SerialCommunicator.setup_command(command_dict, config_manager) -> bool`; `_probe_port` calls it. **Behaviour-identical, no lease yet — its own commit.**
2. Add `EpromOperator.lease()` — a context manager that sets `self._leased = True`.
3. In `_setup_operation`: when leased **and** `self.comm` is connected, call `self.comm.consume_remaining_input()` then `self.comm.setup_command(command_dict, self.config)` instead of `find_and_connect`. Otherwise cold-connect exactly as today.
4. In `_operation_context`'s `finally`: `if not self._leased: self._disconnect_programmer()`.
5. `cli_handlers.dev_test` wraps its `run_plan(...)` call in `with app.eprom_operator.lease():`.

**Four risks, each with a mitigation:**

| Risk | Why | Mitigation |
|---|---|---|
| A stale link across steps — a straggler frame from step N parsed as step N+1's ack | Today `disconnect()` drains via `consume_remaining_input()`; a lease skips it | Call `comm.consume_remaining_input()` (0.05 s read timeout, `serial_comm.py:605`) **before** each leased setup command. Cheap and explicit. |
| A board that needs a reset between operations | Today the port close resets it (measured, above) | This is the fidelity axis DEVTEST-03 covers. Must be observed on silicon, not argued. It is the reason SESS-02's bench leg is not optional. |
| A dead link mid-plan kills the whole plan | Today each call re-probes and can recover | On any `SerialError` during a leased op, tear the lease down and cold-connect for the next step. Matches `run_plan`'s invariant: *"One step's BAD verdict or raised exception NEVER aborts the rest."* |
| The lease does not reach `HardwareManager` | It is a different class with its own connects (`hardware.py:94, 135, 183, 241, 283, 404`), and the sampler alone costs 4 per write step | Fork F5. Leaving it out is honest and smaller; it also caps the measurable saving. State which was chosen. |

**Connect census — structure VERIFIED, totals DERIVED.** Each call site was read; the totals are arithmetic over them, not a measurement.

| Where | Connects | Evidence |
|---|---|---|
| `read_programmer_identity` (pre-plan) | 1 | `cli_handlers.py:2915`; `hardware.py:183` |
| id step | 1 | `check_eprom_id` → `_operation_context` (`eprom_operations.py:3104`) |
| read step | `runs` (= 3) | `_dispatch_read` loops `read_eprom` (`chip_test.py:2742-2744`) |
| write step, per cycle | 5–6 | sampler before 2 (`cli_handlers.py:2818-2819` → `hardware.py:404`) + `write_eprom` 1 + guard read 0–1 (`eprom_operations.py:2411`) + sampler after 2 |
| verify step, per cycle | 1, +1 on the final cycle if the step failed | `verify_eprom` 1; `_read_region` → `read_eprom` (`chip_test.py:3279`) |
| erase step, per cycle | 1 | `erase_eprom` (`eprom_operations.py:2887`) |
| blank-check step, per cycle | 1 | `check_eprom_blank` (`eprom_operations.py:3066`) |
| SDP leg (AT28C256 only) | 12 | six ops × (write + `_read_region`) |

**Derived total for an erasable full-device part at `runs=3`: ~29–33 connects.** The validated structural model in `.planning/notes/dev-test-sequence-cost-model.md` reports 22 (sst27sf512), 32 (at28c256), 18 (w29c040) **at `runs=2`**, with a 13-predicted/13-observed validation on a `--fast` run. Re-scale, do not quote directly. At the Leonardo-class 2.607 s median, ~30 connects is **~78 s of pure connect overhead per plan**.

### Q6 — How SESS-02's measurement can actually be taken

**The rig is attached and identified right now.** `/dev/ttyACM0`, VID `9025` (`0x2341`), PID `32822` (`0x8036`), `Arduino Leonardo`, manufacturer `Arduino LLC`. `[VERIFIED: pyserial list_ports enumeration, run this session 2026-09-23]` This is the same board class `205-BENCH-MATRIX.md` and `205-SESSION-COST.md` used, so the connect medians are comparable without re-measuring. **Per `feedback_verify_port_identity_each_task`, re-verify the `controller:` identity per port at execution time — `ttyACM*` numbers shuffle across replug.**

**What to measure.** Wall clock for a **complete `dev test <chip>` plan**, before vs after, same part, same board, same session, no reflash or reseat between arms, `time` around the whole subprocess, **N ≥ 3 per arm**, medians reported with min/max — the exact method `205-SESSION-COST.md` §2 used and whose table shape should be copied.

**On which board and part.** Leonardo + a part whose plan exercises the full cycle block. Two candidates with different value:
- **W27C512** — the rig's existing part, used throughout `205-BENCH-MATRIX.md`, erasable, 65536 B, protocol `0x07`, plan `id, read, [write, verify, erase, blank-check], sdp×6(NA)`. **Recommended** for continuity with the existing before-figures.
- **AT28C256** — the SDP-leg outlier at 32 connects for ~3 KB, *"overhead-dominated, not bandwidth-dominated — the opposite of every other part of the plan"* (cost-model note). This is where a lease pays most. If only one part can be run, W27C512; if two, add this one.

**A defensible "not worth it" threshold — pre-register it before the run, never after.** Recommendation:

> The lease is kept only if, on the reference part and board class, it removes **≥ 15 %** of the plan's median wall clock **and** the removed time is ≥ 5× the measurement's own spread (max − min). Below that, or if any step's verdict differs from the pre-lease arm for the same physical outcome, the lease commit is reverted and the number is recorded.

Rationale for 15 %: the derived connect-term saving at ~30 connects × 2.607 s ≈ 78 s against a modelled ~100–130 s plan is far above it, so a measured result *below* 15 % is itself evidence the lease is not doing what it was built to do. The second clause is what stops a noisy measurement from deciding a structural question. The third clause makes DEVTEST-03 a gate on SESS-01, not a separate concern.

**⚠ This is an OPERATOR-INITIATED bench measurement.** The plan must carry it as a **`checkpoint:human-verify`** task, never an `<automated>` command. Three independent reasons:
1. `dev test` **writes to the chip on every run** (`cli_handlers.py:2879`: *"Writes to the chip every run (no read-only mode)"*). It energizes VPP/VPE and mutates silicon.
2. A `dev test --submit` would file a public GitHub issue. The bench leg must never pass `--submit`.
3. The operator owns chip handling, shield-revision identification and pot adjustment (`user_shield_revisions`, `feedback_operator_adjusts_pot_solo`).

Standing permission does exist for *flashing* the bench boards (`feedback_bench_boards_are_fw_flash_testbed`), and USB passthrough means Claude can drive the port — but that does not make an automated destructive sweep the right shape for this gate.

**⚠ ROADMAP conflict the planner must resolve explicitly.** `.planning/ROADMAP.md:250` marks Phase 206 **`Bench: no`**, while ROADMAP success criterion 5 for the same phase says *"The wall-clock saving is measured on a real run."* These cannot both stand. Recommend: treat the table's `no` as stale (it was written before SESS-02's wording was finalised), plan the bench leg, and correct the table cell in the same phase. Do **not** silently satisfy SESS-02 with a derivation.

**The shipped instrument, if a connect-count/cost figure is wanted alongside.** `EpromOperator.measure_connect_cost(samples=10, port=…, output_dir=…)` (`eprom_operations.py:1919`) is the MEAS-01 harness that produced the 2.518/2.607 medians, reachable as `firestarter dev … --mode connect-cost --samples N` (`cli_handlers.py:2112-2167`). It pins one port with `restrict_to_port=True` and writes an artifact. Use it to re-anchor the connect median on the day of the run rather than citing a 2026-09-04 figure as current.

### Q7 — The revert path for SESS-02

**Make the revert `git revert <one sha>`.** Concretely:

- **Commit A** (permanent, kept regardless of the outcome): extract `SerialCommunicator.setup_command` out of `_probe_port`. Behaviour-identical, no lease, no new default. It is a readability improvement on its own and its tests do not depend on the lease existing.
- **Commit B** (the *only* thing a revert touches): `EpromOperator.lease()`, the two conditionals in `_setup_operation` and `_operation_context`, and the one `with` in `cli_handlers.dev_test`. **No other file.**
- **Default-off is what keeps commit B revertible.** If the lease ships behind `EpromOperator(..., lease_enabled=False)` with `dev_test` as the only caller that turns it on, then reverting is a one-line change even if the commit has been built on.
- **No test may be written that only passes under a lease.** Every lease test must assert the leased path *in addition to* the cold path, so reverting commit B does not redden a suite the revert cannot fix. This is the pattern that makes the difference between a revert and an unpick.
- **The phase record must be written either way.** Name the file now so it cannot be skipped: `206-SESSION-COST.md`, following `205-SESSION-COST.md`'s structure — §1 what is counted, §2 the measured figures with N and min/max, §3 the derivation beside it labelled as a derivation, §4 the explicit non-measurement statement, §5 a provenance table. **Do not blend a measurement and a derivation** (`205-SESSION-COST.md` §5's explicit rule).

---

## Open Design Forks

Seven. Each is Claude's discretion (no CONTEXT.md); each has a recommendation with its reason.

| # | Fork | Options | Recommendation |
|---|---|---|---|
| **F1** | Source of `OP_VERIFY`'s fingerprint | (a) keep the separate `_read_region` read-back; (b) source it from `verify_eprom`'s own `CompareResult` via the existing `on_result` seam | **(a) for this phase.** (b) is strictly better information *and* removes one whole-region read per failing verify — but it **requires `full=True`** (Pitfall 3) and is a behaviour change on the abort path that DEVTEST-01 does not ask for. File (b) as a todo naming Phase 206's own record as its evidence. |
| **F2** | Where `OP_BLANK_CHECK`'s new evidence lives | (a) the hashed `StepResult.fingerprint` slot; (b) a new additive field the hash does not read | **(b), decisively.** (a) re-keys all 19 frozen literals and every filed issue group — see Pitfall 1. (b) has a shipped precedent in `_step_dict`'s four `fingerprint_*` siblings. |
| **F3** | Where verdict `2` lands for `OP_BLANK_CHECK` / `OP_VERIFY` | (a) stay BAD (status quo); (b) `VERDICT_SKIPPED` + `STATUS_ERROR`, i.e. the existing two-axis transport vocabulary; (c) a sixth verdict | **(b).** It is the vocabulary path 11 already uses for exactly this class of fault, it keeps the exit code honest via `run_status_error`'s `codes.add(2)`, and it needs no new constant. **(c) is forbidden** — ROADMAP's own constraint, quoted at `cli_handlers.py:2647-2650`: *"an unrecognised verdict still contributes exit 0, so this helper introduces no sixth verdict status (ROADMAP's own constraint)."* **(b) requires Pitfall 2 fixed first.** |
| **F4** | The discriminator's shape | name, tag literal, keying field | Mirror the two exemplars exactly: a module constant (e.g. `COMPARE_PATH_HOST_TAG = "cmp=host"`), a `compare_path_tag(results) -> str` returning `""` by default, keyed on a new `StepResult` field with a **falsy default**. Append at the end of `parts`, after `coverage`. |
| **F5** | Lease scope | (a) `EpromOperator` only; (b) also `HardwareManager` | **(a).** Smaller, one class, one revert. But **state the cost in the record**: the sampler's 4 connects per write step × 3 cycles = 12 connects survive, capping the measurable saving at roughly 60 % of the theoretical. If the measurement lands near the threshold, (b) is the named follow-up, and the seed already offers the cheaper sub-step: *"fold `sample_vpp_mv` and `sample_vpe_mv` into one monitor read (−2 connects per write step)."* |
| **F6** | Leased-link failure policy | (a) fail the plan; (b) drop the lease and cold-connect for the next step | **(b).** (a) would make a lease *weaken* `run_plan`'s non-fatal-step invariant, which is a fidelity regression DEVTEST-03 would have to name. |
| **F7** | The "not worth it" threshold and who sets it | pre-registered by the planner vs decided after seeing the number | **Pre-registered, in the PLAN.md, before the bench task.** A threshold chosen after the number is not a threshold. Recommended wording in § Q6. |

---

## Don't Hand-Roll

| Problem | Don't build | Use instead | Why |
|---|---|---|---|
| Classifying a mismatch distribution | A second classifier for the blank-check step | `compare.classify_streamed`, reached via `CompareAccumulator.finalise()` | 202-03 collapsed two implementations into one and proved equality over 2922 cases. A second one re-opens that. |
| Getting the finalised compare result out of `verify_eprom`/`check_eprom_blank` | A new return type or an out-parameter | `_drive_region_compare(..., on_result=callback)` — **already exists**, keyword-only, default `None`, `eprom_operations.py:2592` | Phase 203's write guard already uses it. Changing the return type breaks ~40 bool/int-valued test doubles. |
| Distinguishing two report populations | A `schema_version` bump, a new top-level key, a nonce | A third empty-default tag in `dedup_fingerprint` | `SCHEMA_VERSION` is not in the hash pre-image. `generate_inhibited_pattern`'s docstring (`chip_test.py:110-112`) already records why a nonce is wrong: *"A nonce would break reproducibility and re-key `dedup_fingerprint` on every run."* |
| Proving the frozen hashes did not move | Asserting `dedup_fingerprint(a) == dedup_fingerprint(b)` | `tests/test_blast_radius_invariance.py::test_dedup_fingerprint_is_frozen` | The module's own docstring: relational comparisons *"pass vacuously through ANY change to the hash function itself, since both sides move together."* Eleven such comparisons already ship elsewhere. |
| Measuring per-connect cost | A fresh timing script | `EpromOperator.measure_connect_cost` (`eprom_operations.py:1919`) + `dev --mode connect-cost` | It is the MEAS-01 instrument that produced the cited medians, it pins the port, and it writes an artifact. A skill/tool copy would also land in `firestarter_app/tools/`, which is outside every CI gate. |
| A new error id for a transport-failed blank check | A `messages.toml` entry | The existing `STATUS_ERROR` axis | Adding a catalog id means a meta-repo codegen run plus two sub-repo syncs, turning a one-repo phase into three. |
| Per-step port pinning under a lease | Keeping `preferred_port`/`restrict_to_port` plumbed through leased calls | The lease itself | The pin exists *because* there is no lease. Under one, the "three different boards" hazard 203-CR-01 guards against cannot arise. |

**Key insight:** every capability this phase needs was built by Phases 202–204 and left with a seam pointing here. The phase's real difficulty is not building anything — it is **not disturbing a hash** while making three genuine improvements around it.

---

## Common Pitfalls

### Pitfall 1 — Attaching a `Fingerprint` to the blank-check step silently re-keys everything
**What goes wrong:** `dedup_fingerprint` hashes `f"{result.op}={result.verdict}:{cls}"` where `cls` is `result.fingerprint.classification if result.fingerprint else ""` (`diagnostic_report.py:300-301`). Today the blank-check step has no fingerprint, so its triple ends in an empty classification. Attach one and the triple changes for **every report on every chip**.
**Why it happens:** it reads like an additive improvement. It is not — the field is inside the allow-list.
**And it is worse than it looks:** a *passing* blank check reads an all-0xFF device, so `ff_ratio == 1.0`, and `classify_streamed` checks blank/contact **first** (`compare.py:447-454`). The classification would be `blank/contact`, not `match`. `classify_fingerprint`'s own docstring names this exact trap: *"match — zero mismatches, checked AFTER buckets 1 and 2 so an all-0xFF perfect compare stays blank/contact rather than silently re-keying that population."*
**How to avoid:** carry the evidence in a field outside the five-entry allow-list (fork F2), exactly as `_step_dict`'s four `fingerprint_*` siblings do — `diagnostic_report.py:849-855`, verbatim: *"`fingerprint` keeps carrying the classification string alone, because that string is the only fingerprint component `dedup_fingerprint` hashes; the four siblings are therefore additive and cannot re-key a filed report."*
**Warning sign:** any diff to `test_blast_radius_invariance.py`'s literals, or to `FROZEN_HASHES`, that is not a *deliberate, separately-committed* re-key.

### Pitfall 2 — `_aggregate_cycle_results` drops `status`, so the 3-way migration produces a false green
**What goes wrong:** `_aggregate_cycle_results` builds its folded `StepResult` at `chip_test.py:1297-1311` with nine keywords — `op`, `verdict`, `reason`, `error_code`, `fingerprint`, `run_count`, `divergence`, `duration_s`, `write_target` — and **no `status=`**, so the result defaults to `STATUS_COMPLETE` (`chip_test.py:1009`).
**Why it matters here:** fork F3 routes verdict 2 to `VERDICT_SKIPPED` + `STATUS_ERROR`. `VERDICT_SKIPPED` contributes **exit code 0** (`cli_handlers.py:2624`). The only thing that stops a transport-failed run exiting `0` is `run_status(results) == STATUS_ERROR` feeding `_dev_test_exit_code`'s `codes.add(2)`. If the step is inside the cycle block — and **`OP_VERIFY` always is, and `OP_BLANK_CHECK` is for every erasable part** (`cycle_block_bounds` docstring, `chip_test.py:1211`: *"erasable -- `id, read, [write, verify, erase, blank-check], sdp x6`"*) — the fold erases the status and the run exits `0`. A dropped USB connection would report a clean pass.
**Already reachable today** via the `SerialError`/`HardwareOperationError` arm (path 11), so this is a pre-existing defect, not one this phase introduces — but the migration makes it routine.
**Asymmetry that makes it hard to catch:** `_aggregate_cycle_results` returns `results[0]` **unchanged** when `len(results) == 1` (`chip_test.py:1279`), so `--fast` preserves the status and the default three-cycle run does not. A `--fast` reproduction would look green-on-green.
**How to avoid:** fix the fold first — propagate `STATUS_ERROR` if any ran cycle carried it — and make it the *first* task, before the verdict migration. Add a test that a cycle-block step with a transport failure yields exit 2.

### Pitfall 3 — Sourcing the fingerprint from the verify's own compare gives a truncated distribution
**What goes wrong:** the default (non-`--full`) verify passes `abort_predicate=lambda: accumulator.has_mismatch` (`eprom_operations.py:2639-2641`), so the read **stops at the first mismatching byte**. The resulting `CompareResult` has `compared` ≪ `total`, `bad == 1`, and `bit_set_counts` spanning a prefix only. Classifying that produces a confident-looking label from a one-byte sample.
**Why it happens:** the `CompareResult` is right there and looks free.
**It is the trap the codebase already named.** `_drive_region_compare`'s `on_result` docstring (`eprom_operations.py:2616-2621`): *"the guard aborts at the first non-blank byte, so a rendered range would always be one byte and the bucket would be classified from a one-byte sample, exactly the confident-verdict-from-a-short-prefix trap Phase 202's D-09 already named (D-11)."*
**How to avoid:** if fork F1 takes option (b), `dev test` must call `verify_eprom(..., full=True)` — which forfeits the abort's saving on failing verifies. Weigh that against the read-back it removes. If F1 stays at (a), this pitfall does not arise.

### Pitfall 4 — A leased link inherits the previous step's undrained input
**What goes wrong:** the drain lives in `SerialCommunicator.disconnect()` (`serial_comm.py:613-624`), which a lease skips. A trailing frame from step N then gets parsed as step N+1's setup ack.
**How to avoid:** call `comm.consume_remaining_input()` immediately before each leased setup command. It uses a 0.05 s read timeout and restores the original (`serial_comm.py:597-611`), so the cost is negligible.
**Warning sign:** intermittent `is_ok=False` on the second or later step of a leased plan, especially on Uno-class boards where `_probe_port` already documents a spurious decode-error frame around DTR resets.

### Pitfall 5 — A live board reddens the suite and a stale `grep` under-scans it
**What goes wrong:** `/dev/ttyACM0` is attached right now. `reference_characterization_no_programmer_tests_fail_with_live_board` records that `test_no_programmer_found_*` go RED when a board is present. A plan that treats "suite green" as the gate will chase a phantom.
**Also:** the devcontainer's `grep` is ugrep and honours `.gitignore`, so a coverage scan silently under-reports (`reference_devcontainer_grep_is_ugrep_honors_gitignore`).
**How to avoid:** use `git grep` or `grep --no-ignore`. Record the baseline: **2333 tests collected** on `.venv311` (Python 3.11.16) `[VERIFIED: pytest --collect-only -q, run this session]`. Run the suite with `-o addopts=""` — the project's `addopts` is `-ra -q` and doubling `-q` hides the count line (`reference_pytest_addopts_q_suppresses_count_line`).

### Pitfall 6 — Treating `.planning/notes/dev-test-sequence-cost-model.md` and the seed as current
**What goes wrong:** both are partly falsified by Phases 177/180/202 and by commit `b596249`.
Specifically: the note and seed R1 both say *"`verify_eprom` streams host→device and the firmware compares (`memory.cpp:377-396`)"* — **false since Phase 202**; verify now reads to the host. The note's waste pattern 1 ("the fingerprint read-back is unconditional") was **closed** by the `step_failed` gate at `chip_test.py:3274-3292` (todo `2026-08-30-gate-fingerprint-readback-on-step-failure.md` is in `todos/completed/`). Every figure is modelled at `runs=2`; the default is now `3`.
**What survives and is still good:** the connect *counts* (structurally derived, 13-predicted/13-observed validated), the per-primitive rates with their stated `0x07`-only caveat, and the AT28C256-is-overhead-dominated finding.
**How to avoid:** cite the note for structure, never for absolute seconds, and say which.

### Pitfall 7 — Assuming the `transport` bucket becomes live
**What goes wrong:** a reader of "transport failure now has its own verdict" reasonably infers `FP_TRANSPORT` is now reachable. It is not — `runs=1` under `_run_cycle_block` keeps `repeat_divergent` permanently `False`.
**How to avoid:** state in the phase record that the bucket remains dead after the phase and why. `reference_classify_fingerprint_transport_bucket_unreachable` already warns that Phase 178's design assumed it was live and the assumption *"is false on arrival."* Do not let Phase 206 repeat that.

---

## Code Examples

All patterns below are **copied in shape from code already in the tree**, with the source cited. None is invented.

### The empty-default discriminator (copy `coverage_tag` exactly)
```python
# Source shape: firestarter/chip_test.py:1054-1079 (COVERAGE_TAG_FULL_DEVICE / coverage_tag)

COMPARE_PATH_HOST_TAG = "cmp=host"


def compare_path_tag(results: list[StepResult]) -> str:
    """`"cmp=host"` when this run's compare steps ran on the host engine; `""`
    otherwise.

    Returning `""` by default is load-bearing for the same reason as
    `repeat_policy_tag` and `coverage_tag` above: `dedup_fingerprint` appends
    this tag only when non-empty, so every already-filed report -- all of which
    were produced by the firmware comparison path -- keeps a byte-identical
    fingerprint and no historical `count_agreeing` group is re-keyed or reset.
    Only the newer, mechanically different host-side shape gets a tag.
    """
    for result in results:
        if result.compare_path == COMPARE_PATH_HOST:
            return COMPARE_PATH_HOST_TAG
    return ""
```
and, in `dedup_fingerprint`, appended after `coverage` — the identical three-line shape as `diagnostic_report.py:307-309` and `:323-325`:
```python
    compare_path = compare_path_tag(report.results)
    if compare_path:
        parts.append(compare_path)
```

### Additive, non-hashed evidence on the blank-check step
```python
# Source shape: firestarter/diagnostic_report.py:849-855 -- the four
# `fingerprint_*` siblings, which are "additive and cannot re-key a filed
# report" precisely because dedup_fingerprint's allow-list does not read them.

# On StepResult (chip_test.py), NOT the existing `fingerprint` field:
    compare_evidence: dict[str, Any] | None = None
    """The finalised CompareResult's own numbers for a compare-driven step --
    `bad`, `compared`, `first_offset`, `first_actual`, `ff_count`, `aborted`.
    Deliberately NOT `fingerprint`: that field's `classification` string is the
    one fingerprint component `dedup_fingerprint` hashes, and populating it on a
    step that has never carried one would re-key every already-filed report.
    """
```

### Handing the finalised `CompareResult` back — the seam already exists
```python
# Source: firestarter/eprom_operations.py:2591 and :2612-2624 (on_result),
# used today by _run_write_blank_guard at :2224.

captured: dict = {}

def _on_result(result: CompareResult) -> None:
    captured["bad"] = result.bad
    captured["compared"] = result.compared
    captured["first_offset"] = result.first_offset
    captured["first_actual"] = result.first_actual
    captured["aborted"] = result.aborted
    captured["classification"] = (
        result.fingerprint.classification if result.fingerprint else None
    )
```
Note `first_actual`'s docstring (`compare.py:152-159`): it is *"the only place on the compare path that value exists"* and *"Never surfaced by `render_compare_lines`"* — it is the byte value the retired firmware `MSG_ERR_NOT_BLANK` used to report.

### The lease seam (default off, one revertible commit)
```python
# Source shapes: eprom_operations.py:657-705 (_operation_context) and
# serial_comm.py:806-905 (_probe_port's send-and-validate half).

@contextmanager
def lease(self):
    """Hold ONE validated link across every operation in this block.

    Default OFF and opt-in at exactly one call site (cli_handlers.dev_test),
    so reverting this feature is `git revert` of one commit rather than an
    unpick. On any SerialError inside a leased operation the lease is dropped
    and the next operation cold-connects, preserving run_plan's invariant that
    one step's failure never aborts the rest.
    """
    self._leased = True
    try:
        yield self
    finally:
        self._leased = False
        self._disconnect_programmer()
```
and, in `_operation_context`'s `finally` (`eprom_operations.py:701-705`), the one conditional:
```python
        finally:
            if not self._leased:
                self._disconnect_programmer()
```

---

## Runtime State Inventory

This is a refactor whose blast radius reaches state **outside** the repository. All five categories answered explicitly.

| Category | Items found | Action required |
|---|---|---|
| **Stored data** | **GitHub issues in `henols/firestarter_prom`, keyed on `dedup_fingerprint`.** `submit.find_prior_report` (`submit.py:538`) queries them; `submit.build_title` (`submit.py:197`) embeds the 12-char shorthash in the issue title. The N≥2 `count_agreeing` promotion ladder is computed over those groups. **A hash change is a data migration nobody can perform** — filed issues carry their old id forever. `gh#20`'s orphaned id `00e121446ceb` is the recorded precedent (`diagnostic_report.py:262-263`). | **No migration is possible.** The only control is not to change the hash for already-filed shapes. Empty-default discipline (DEVTEST-02) is that control. |
| **Stored data (local)** | Saved reports under `<config dir>/reports/dev-test-<chip>.{json,md}` (`cli_handlers.py:2987`-ff; honours `FIRESTARTER_CONFIG_DIR`, default `~/.firestarter/reports`). Each carries `schema_version` and a baked `dedup_fingerprint`. | **None.** They are historical artifacts, correct as filed. A new optional field is additive; every pre-existing consumer ignores it. Note `reference_app_writes_home_firestarter_config_despite_config_dir_env`. |
| **Stored data (repo fixtures)** | 19 JSON report fixtures in `tests/fixtures/reports/*.json`, each with a `"dedup_fingerprint"` value at line 23, mirrored by `FROZEN_HASHES` in `tests/fixtures/report_shapes.py:736-756`. Plus `tests/fixtures/shape_ids.json` (16-entry closure anchor). | **Must stay byte-identical** unless a re-key is deliberate — and then as its OWN commit, per `test_dedup_fingerprint_is_frozen`'s failure message. |
| **Live service config** | `VALIDATED-EPROMS.md` in the meta repo is the community chip ledger the `devtest-triage` skill writes. It is in git, not in a service. Label taxonomy in `henols/firestarter_prom` is GitHub-side. | **None** this phase. Note `feedback_no_gsd_references_in_validated_eproms_notes` if any ledger text is touched. |
| **OS-registered state** | **None.** No task scheduler, no pm2, no systemd unit references `dev test`. Verified by absence of any such reference in the host tree. |
| **Secrets / env vars** | `FIRESTARTER_CONFIG_DIR` (read by the report-persistence path). `GH_TOKEN`/`gh` auth for `--submit`. **Neither is renamed by this phase.** | **None.** |
| **Build artifacts / installed packages** | `firestarter_app/.venv311` holds an **editable** install; `firestarter/__pycache__` holds stale `.cpython-311.pyc` and `.cpython-312.pyc` for every module. A leased-session change to `serial_comm.py`/`eprom_operations.py` is picked up by the editable install without reinstall. | **None**, but see `reference_firestarter_app_worktree_editable_install_trap` if a worktree is used — `use_worktrees` is `false` in `.planning/config.json`, so it is not. |

**Nothing found in a category is stated, not left blank** — OS-registered state and secrets are explicitly *none*, verified by scan, not by assumption.

---

## State of the Art

| Old approach | Current approach | When changed | Impact on this phase |
|---|---|---|---|
| `verify` pushes the file to the firmware; firmware compares (`memory.cpp:377-396`) | Host reads `COMMAND_READ` and compares in `CompareAccumulator` | Phase 202, 2026-09-20 | **Falsifies seed R1 and the cost-model note's verify row.** Do not cite either for verify mechanics. |
| `check_eprom_blank` composes ordinal 4; returns `bool` | `COMMAND_READ` + host compare; returns `int` 0/1/2 | Phase 202-05 (`92f9cbe`) | The `== 0` adapter at `chip_test.py:2600` is this phase's job. |
| Firmware ordinals 4 and 6 exist | Retired from both sides, recorded as reserved | Phase 204 | `OP_VERIFY`/`OP_BLANK_CHECK` are host strings only. |
| Firmware write-init / erase-end blank-check pre-flights | Host-side `write_blank_guard`; `erase -b` host check | Phases 203 + 205 | `erase -b` now costs a **second port open** — the cost SESS-01 exists to collapse (`205-SESSION-COST.md`). |
| `FLAG_SKIP_BLANK_CHECK` (0x08) wire bit | Retired; reaches the guard as `blank_check_requested=` keyword | Phase 205-04 (`9a82478`) | `_dispatch_multi_run` already passes the keyword (`chip_test.py:3243`). |
| Fingerprint read-back on every run | Gated on `step_failed` (`chip_test.py:3274-3292`) | Phase 177 (PRUNE-02) | Cost-model waste pattern 1 is **closed**. |
| `dev test` default `runs=2` | `_DEFAULT_RUNS = 3` | commit `b596249` | Re-scale every modelled figure. |
| Source-introspecting AST tests over `chip_test.py` | Removed | 2026-09-14 (`088d2b7`) | Seed R2's "asserted structurally" claim is now **assumed, not asserted**. |
| mypy watermark gate in app CI | Retired (`0f251f0`) | — | App CI is ruff + pytest only. |

**Deprecated / stale, do not cite as current:**
- `.planning/notes/dev-test-sequence-cost-model.md` — verify mechanics, waste pattern 1, all `runs=2` figures.
- `.planning/seeds/dev-test-adaptive-sequencing.md` R1 — the firmware-compares claim and its `memory.cpp` line citation.
- `.planning/ROADMAP.md:250` — the `Bench: no` cell for Phase 206, which contradicts the same file's success criterion 5 (§ Q6).

---

## Environment Availability

| Dependency | Required by | Available | Version | Fallback |
|---|---|---|---|---|
| Python 3.11 (CI parity) | every test leg | ✓ | 3.11.16, at `firestarter_app/.venv311/bin/python` | none needed — **never use bare `python3` (3.12.14), it masks CI** |
| pytest | test suite | ✓ | 9.1.1 (in `.venv311`) | — |
| ruff | CI gate | ✓ (via `.[test]`) | as pinned | — |
| pyserial | any serial work | ✓ (in `.venv311`) | — | — |
| **Arduino Leonardo on `/dev/ttyACM0`** | **SESS-02 bench leg** | ✓ | VID `9025`/`0x2341`, PID `32822`/`0x8036`, `Arduino LLC` | **none** — SESS-02 cannot be satisfied by derivation |
| A test EPROM in the socket | SESS-02 bench leg | **unknown** — cannot be determined without energizing | — | **operator must confirm and seat the part** |
| `gh` CLI | `dev test --submit` | not checked | — | **not needed — the bench leg must NOT pass `--submit`** |
| `pio` / firmware toolchain | — | not checked | — | **not needed — this phase is app-only** |

**Missing dependencies with no fallback:** none for the code work. The **seated chip** is the one unknown, and it is operator-owned.

**Measured suite baseline:** `2333 tests collected in 2.68s` on `.venv311` `[VERIFIED: pytest tests/ -o addopts="" --collect-only -q, run this session]`. ⚠ With `/dev/ttyACM0` attached, `test_no_programmer_found_*` are expected RED — establish the failing-id set **before** the first change so a pre-existing red is never mistaken for a regression.

**Knowledge graph:** `.planning/graphs/graph.json` exists but is **stale** — 118 h old, built at `d11d37e`, **324 commits behind** `c5c9d00`. A discovery query (`"dev test serial session"`) returned zero nodes. Every finding in this document therefore comes from direct source reading, which is the stronger evidence anyway. Treat any semantic relationship from that graph as approximate.

---

## Validation Architecture

`workflow.nyquist_validation` is `true` in `.planning/config.json` `[VERIFIED: read this session]`.

### Test framework
| Property | Value |
|---|---|
| Framework | pytest 9.1.1 |
| Config file | `firestarter_app/pyproject.toml` (`addopts = "-ra -q"`, mypy strict-module overrides) |
| Interpreter | `firestarter_app/.venv311/bin/python` (3.11.16) — **CI parity is mandatory** |
| Quick run | `.venv311/bin/python -m pytest tests/test_chip_test.py tests/test_blast_radius_invariance.py -o addopts="" -q` |
| Full suite | `.venv311/bin/python -m pytest tests/ -o addopts="" --cov=firestarter --cov-report=term-missing --cov-fail-under=70` |

### Phase requirements → test map
| Req | Behaviour | Type | Automated command | Exists? |
|---|---|---|---|---|
| DEVTEST-01 | blank-check step carries compare evidence | unit | `pytest tests/test_chip_test.py -k blank_check -o addopts=""` | ⚠ module exists (23 `check_eprom_blank` refs); **new cases → Wave 0** |
| DEVTEST-01 | verify step's fingerprint is no less informative | unit | `pytest tests/test_chip_test.py -k fingerprint -o addopts=""` | ✅ partial |
| DEVTEST-01 | the 2922-case behavioural corpus still shows zero differences | integration | `pytest tests/test_compare.py -o addopts=""` | ✅ (D-03 corpus) |
| DEVTEST-02 | all 19 frozen literals unmoved | unit | `pytest tests/test_blast_radius_invariance.py::test_dedup_fingerprint_is_frozen -o addopts=""` | ✅ **the gate** |
| DEVTEST-02 | the new tag is reachable and actually re-keys when present | unit | new — a planted-mutation leg proving the tag moves the hash | ❌ **Wave 0** |
| DEVTEST-02 | a legacy/default `StepResult` takes the untagged branch | unit | new | ❌ **Wave 0** |
| DEVTEST-03 | verdict 1 vs verdict 2 land on distinct outcomes | unit | `pytest tests/test_chip_test.py tests/test_devtest_firmware_error_propagation.py -o addopts=""` | ⚠ new cases |
| DEVTEST-03 | a transport failure in a cycle-block step exits 2, not 0 | unit | new — **Pitfall 2's regression leg** | ❌ **Wave 0, and it must be seen RED first** |
| DEVTEST-03 | exit-code precedence unchanged | unit | `pytest tests/test_dev_test_cmd.py -o addopts=""` | ✅ |
| SESS-01 | a leased plan opens one link; a cold plan is byte-identical | unit | new — assert connect count on a fake transport, **both** paths | ❌ **Wave 0** |
| SESS-01 | a mid-plan `SerialError` drops the lease and the plan continues | unit | new | ❌ **Wave 0** |
| SESS-02 | measured wall clock, before vs after | **manual / bench** | **`checkpoint:human-verify` — NOT automatable** | ❌ operator |

### Sampling rate
- **Per task commit:** `pytest tests/test_chip_test.py tests/test_blast_radius_invariance.py tests/test_diagnostic_report.py -o addopts="" -q`
- **Per wave merge:** full suite on `.venv311`, diffed against the pre-phase failing-id set
- **Phase gate:** full suite + `ruff check` + `ruff format --check` green before `/gsd-verify-work`

### Wave 0 gaps
- [ ] A test that a `StepResult` with the new field at its default produces an **untagged** `dedup_fingerprint` — covers DEVTEST-02
- [ ] A planted-mutation leg proving the new tag is **capable** of moving the hash (non-vacuity; the `test_the_197_delta_layer_is_capable_of_failing` precedent)
- [ ] A cycle-block transport-failure → exit-2 regression test — **must be seen RED before the fix** (`reference_gate_authored_before_content_can_be_unreachable`)
- [ ] Lease tests that assert **both** the leased and the cold path, so reverting commit B cannot redden the suite
- [ ] The pre-phase failing-id set, recorded (live-board reds)

---

## Security Domain

`security_enforcement` is absent from `.planning/config.json`, so it is enabled.

### Applicable ASVS categories
| Category | Applies | Standard control |
|---|---|---|
| V2 Authentication | no | No authentication surface. `gh` auth is delegated and untouched. |
| V3 Session Management | **no, despite the word "session"** | SESS-01's "session" is a serial link, not an authenticated session. No token, no identity, no expiry semantics. |
| V4 Access Control | no | Local CLI over a local device node. |
| V5 Input Validation | **yes** | Firmware-supplied frames are parsed by `frame_parser` with CRC8 before any interpretation. Under a lease, a **second** setup ack must go through the identical validation as the first — see the pitfall below. `_decode_id_frame`'s existing defensive posture (the `firmware_max_chunk` plausibility clamp, `serial_comm.py:163`) is the pattern. |
| V6 Cryptography | **no** | `dedup_fingerprint` uses sha256 **as a non-secret distribution function**, truncated to 12 hex chars. Its own docstring says so: *"A non-secret dedup id, not a security control."* Do not treat it as one; equally, do not "strengthen" it — that would re-key everything. |
| V7 Error Handling / Logging | yes | `submit.sanitize_dict` scrubs user strings before a report is filed. Any new report field must pass through it. |

### Known threat patterns for this stack
| Pattern | STRIDE | Standard mitigation |
|---|---|---|
| A leased link skips the firmware-version / hardware-revision gates on operations 2..N | **Elevation of privilege** — a host drives firmware whose wire contract it has not verified | Run the **same** `_validate_firmware_version` + `_validate_hardware_revision` on every leased setup ack, or validate once on lease acquisition and refuse to lease if either gate fails. **Never** silently skip. `_probe_port`'s comment explains why the gate's placement is safe: the VPP regulator is not engaged until `firestarter_operation_init`, which blocks on `op_wait_for_ack()`. |
| A leased link lands on a different board mid-plan | **Spoofing** | Structurally impossible under a lease (the port never closes) — which is why 203-CR-01's `preferred_port` pin becomes redundant. State that, do not just delete the pin. |
| Undrained input from step N read as step N+1's ack | **Tampering** (accidental) | `consume_remaining_input()` before each leased setup command. Pitfall 4. |
| A scrubbable free-text value influencing report identity | Repudiation | Already mitigated: `dedup_fingerprint` excludes `reason` and every volatile field by allow-list. Keep the new field out of the allow-list unless it is the deliberate tag. |
| `dev test --submit` publishing unscrubbed data | Information disclosure | `sanitize_dict` (`submit.py:120`). **The bench leg must not pass `--submit`.** |

---

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|---|---|---|
| A1 | `run_plan` is the right lease boundary (rather than `dev_test` or `EpromOperator` construction) | Q5, F5 | Low. The seed names `run_plan` explicitly; the alternatives are equivalent in effect. Only affects where the `with` goes. |
| A2 | 15 % is a defensible "not worth it" threshold | Q6, F7 | **Medium — this is a judgement, not a measurement.** The number should be confirmed by the user or explicitly adopted as Claude's discretion and recorded. The *structure* (pre-registered, two-clause, plus a fidelity clause) matters more than the number. |
| A3 | W27C512 on the Leonardo is the right reference part for SESS-02 | Q6 | Low-medium. It gives continuity with `205-SESSION-COST.md`; AT28C256 would show a larger saving. Operator may prefer otherwise. |
| A4 | The derived ~29–33 connects per plan at `runs=3` | Q5 | Medium. Every call site was read, but the arithmetic is a derivation, not an observation, and the guard-read term is family-dependent. **Measure it; do not quote it as measured.** |
| A5 | CMP-F1 (the `DONE`-based clean stop) stays out of scope | User Constraints | Low. It is a firmware change and ROADMAP marks this phase `app`. But 205-CONTEXT named Phase 206 as its home, so the planner should say "deferred again" rather than silently omit it. |
| A6 | `VERDICT_SKIPPED` + `STATUS_ERROR` is the right landing for verdict 2 | F3 | **Medium.** It reuses an existing vocabulary and keeps the exit code honest **only if Pitfall 2 is fixed**. An operator might prefer verdict 2 to stay BAD for `dev test` specifically, on the grounds that a community tester should investigate either way. Worth one question. |
| A7 | No `messages.toml` entry is needed | Don't Hand-Roll | Low. The existing status axis carries the distinction. If a plan wants a named error id, the phase becomes three-repo. |
| A8 | The pre-existing live-board test reds are limited to `test_no_programmer_found_*` | Pitfall 5 | Low-medium. Sourced from memory, not re-measured this session. **Record the actual failing-id set before the first change.** |

---

## Open Questions

1. **Does the operator accept that every post-206 `dev test` report stops grouping with every pre-206 one?**
   - What we know: that is the *intended* effect of DEVTEST-02's "no two mechanically different runs silently merge", and the SDP leg set the precedent for an accepted community-ladder reset (`diagnostic_report.py:255-270`).
   - What is unclear: whether the operator wants the N≥2 promotion counts to reset for all 43 measured ALLOW chips a second time, this soon after the SDP leg did it.
   - Recommendation: **ask, or at minimum record the consequence explicitly in the phase record with the two rejected alternatives named**, exactly as the SDP-leg comment does.

2. **Should verdict `2` stay `BAD` for `dev test` specifically?** (A6)
   - What we know: the todo, the in-source comment and Phase 202's review all say the fold is wrong because it points a triager at the chip when the cause was the cable.
   - What is unclear: whether a community tester is better served by "investigate either way".
   - Recommendation: take fork F3 option (b), and make the *report* say plainly which it was. One question to the user would settle it.

3. **Does ROADMAP's `Bench: no` for Phase 206 stand?**
   - What we know: it contradicts the same file's success criterion 5 and SESS-02's own wording.
   - Recommendation: plan the bench leg; correct the table cell in this phase. Do not satisfy SESS-02 by derivation.

4. **Is `/dev/ttyACM0`'s socket occupied, and by what?**
   - Cannot be determined without energizing the board. Operator must confirm and seat the part before the bench leg.

---

## Sources

### Primary (HIGH confidence — read this session, quoted verbatim with line ranges)
- `firestarter_app/firestarter/chip_test.py` — `:145-206` `classify_fingerprint`/`_synthesized_match_fingerprint`; `:253-292` op vocabulary; `:803-822` verdict + status vocabulary; `:864` `_MULTI_RUN_OPS`; `:949-1010` `StepResult`; `:1029-1079` the two empty-default tags; `:1195-1229` `cycle_block_bounds`; `:1248-1311` `_aggregate_cycle_results`; `:1452-1571` `_run_cycle_block`; `:1574-1700` `run_plan`; `:2402-2686` `_run_step`/`_dispatch_step`; `:2716-2856` `_dispatch_read`/`_read_region`; `:3005-3063` `_firmware_error`/`_is_monotonic_masked_target`; `:3064-3320` `_dispatch_multi_run`; `:3664` `_RAN_VERDICTS`
- `firestarter_app/firestarter/diagnostic_report.py` — `:52` `SCHEMA_VERSION`; `:255-327` `dedup_fingerprint` and its empty-default block; `:843-947` `_step_dict`; `:989-1025` `to_dict`
- `firestarter_app/firestarter/compare.py` — `:33-58` cap + labels + thresholds; `:62-169` `Fingerprint`/`CompareResult`; `:396-511` `classify_streamed`
- `firestarter_app/firestarter/eprom_operations.py` — `:424-503` `EpromOperator.__init__`; `:561-710` `_setup_operation`/`_operation_context`/`_disconnect_programmer`; `:1919-1993` `measure_connect_cost`; `:2400-2470` `write_eprom` guard site; `:2584-2706` `_drive_region_compare`; `:2707-2871` `verify_eprom`; `:3011-3099` `check_eprom_blank`
- `firestarter_app/firestarter/serial_comm.py` — `:84-86` delays; `:114-214` `SerialCommunicator.__init__`; `:597-624` `consume_remaining_input`/`disconnect`; `:806-905` `_probe_port`; `:967-1083` `find_and_connect`
- `firestarter_app/firestarter/cli_handlers.py` — `:2621-2700` exit-code map + precedence + `_dev_test_exit_code`; `:2803-2846` `_make_sampler` + `_DEFAULT_RUNS`; `:2876-2990` `dev_test`
- `firestarter_app/firestarter/hardware.py` — `:82-443` the six `find_and_connect`/`disconnect` sites
- `firestarter_app/firestarter/submit.py` — `:179-197` `build_title`; `:371-447` `build_body`; `:538-600` `find_prior_report`
- `firestarter_app/tests/fixtures/report_shapes.py:736-756` — the 19 `FROZEN_HASHES`
- `firestarter_app/tests/test_blast_radius_invariance.py:1-80, :313` — the gate and its anti-vacuity contract
- `firestarter_fw/src/firestarter.cpp:206-257` — `command_done` + `loop`, the proof a leased link needs no firmware change
- `.planning/REQUIREMENTS.md:60-110`, `.planning/ROADMAP.md:240-275, :418-430`
- `.planning/phases/205-the-pre-flights-leave-the-firmware/205-SESSION-COST.md` (whole)
- `.planning/seeds/dev-test-adaptive-sequencing.md` (whole, incl. both amendments)
- `.planning/notes/dev-test-sequence-cost-model.md` (whole — **partly stale, see Pitfall 6**)
- `.planning/todos/pending/2026-09-20-devtest-blank-check-folds-transport-failure-into-verdict-bad.md`
- `/workspaces/CLAUDE.md`, `/workspaces/firestarter_app/CLAUDE.md`, `.planning/config.json`
- Tool observations this session: `git log`, `git show`, `git grep`, `pytest --collect-only` (2333), `pyserial list_ports` (Leonardo on `/dev/ttyACM0`), `.venv311` Python 3.11.16, `gsd-tools graphify status` (stale, 324 commits behind)

### Secondary (MEDIUM confidence — project memory, cross-checked against source where possible)
- `project_v141_milestone_activated` — D-6 (seed R4 in scope), D-7; ordering-is-a-safety-property
- `project_v141_phase202_closed` — the 2922-case corpus instruction; the three open findings; `compare.py`'s import purity
- `reference_classify_fingerprint_transport_bucket_unreachable` — **independently re-confirmed against `chip_test.py:1533` + `:3284` this session**
- `reference_operator_comm_torn_down_ack_unobservable` — **independently re-confirmed against `eprom_operations.py:701-710` this session**
- `reference_held_rail_dtr_reset_hold_script` — DTR-reset-on-close on Leonardo (v1.18 Phase 97 RCA)
- `reference_devcontainer_py312_masks_ci_py39`, `reference_pytest_addopts_q_suppresses_count_line`, `reference_devcontainer_grep_is_ugrep_honors_gitignore`, `reference_characterization_no_programmer_tests_fail_with_live_board`, `reference_devtest_exit_precedence_marginal_beats_bad`, `reference_devtest_duration_s_is_cycle_sum_not_op_cost`, `feedback_verify_port_identity_each_task`, `feedback_bench_boards_are_fw_flash_testbed`

### Tertiary (LOW confidence — not used for any load-bearing claim)
- `.planning/graphs/graph.json` — stale by 118 h / 324 commits; a discovery query returned zero nodes. Not relied on.

---

## Metadata

**Confidence breakdown:**
- **Standard stack / no-new-dependency:** HIGH — nothing is proposed for installation; the whole surface is in-tree and was read.
- **`dedup_fingerprint` mechanics and the empty-default discipline (DEVTEST-02):** HIGH — the pre-image, both exemplars and the 19 frozen literals were read and quoted verbatim; the non-movement through 202–205 was verified by `git show`.
- **Verdict/status/classification enumeration (DEVTEST-03):** HIGH — all three vocabularies quoted from source; all 18 production paths traced.
- **`OP_VERIFY`/`OP_BLANK_CHECK` current behaviour (DEVTEST-01):** HIGH — both dispatch arms and both operator methods read end to end; the two `phase 206's job` markers quoted.
- **Session-lease feasibility (SESS-01):** HIGH on the host structure and on the firmware's `CMD_IDLE` loop (both read). MEDIUM on the four risks, which are reasoned from measured facts rather than observed under a lease that does not exist yet.
- **Connect census totals:** MEDIUM — call sites verified, totals derived. Labelled as such.
- **SESS-02 saving:** the number **does not exist**. The before-figures are HIGH (measured, Phase 203/205); the projected saving is a MEDIUM derivation; the threshold is an ASSUMPTION (A2).

**Research date:** 2026-09-23
**Valid until:** 2026-10-23 for the in-tree facts (stable, single-repo, no external dependency); **invalidated immediately** by any commit touching `chip_test.py`, `diagnostic_report.py`, `compare.py`, `eprom_operations.py` or `serial_comm.py` — re-verify every file:LINE citation against the live tree at planning time, with `git grep`, exactly as Phase 205's D-09 required.
