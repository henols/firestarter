---
phase: "200"
slug: "an-elevated-programming-supply-is-stated"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-09-19"
---

# Phase 200 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

Register origin: `register_authored_at_plan_time: true` — all three plans
(`200-01`, `200-02`, `200-03`) carry a parseable `<threat_model>` block. Verification ran at
ASVS L1 (grep depth) with `workflow.security_block_on: high`, per the Step 3 short-circuit:
zero open threats at or above the block threshold, register authored at plan time, level 1.
No auditor subagent was spawned; mitigations were verified directly against the shipped source.

This audit covers the phase **including** the post-UAT rewording commit `b3a777e` (gap G-200-1),
which shortened the elevated-VCC warning to one line. Two threats touch that commit directly
(T-200-03, T-200-05) and were re-verified against the reworded code, not the originally shipped
text.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| `~/.firestarter/database.json` → `EpromDatabase` → presenter | Operator-supplied JSON merged over the packaged database unless `skip_local_override=True`. The only untrusted input this change reads. | Chip metadata incl. `electrical.vdd_mv` (untrusted, operator-owned) |
| `firestarter/data/chip_database.json` → presenter / census tests | Generated build artifact, read-only for this phase. Never hand-edited. | Chip metadata (trusted, generated) |
| `tools/datasheet_overrides.json` → census test module | Human-authored evidence file, read-only. Carries the `UNSOURCED` sentinel the provenance leg depends on. | Datasheet provenance (trusted, in-repo) |
| presenter → operator stdout | Rendered advisory text. | Two voltages + fixed prose. No secrets, paths or PII. |
| PATH's `firestarter` entry point → snapshot harness | `shutil.which` resolves whatever is installed; a stale or sibling-tree editable install would pin foreign output. | Rendered CLI output into a committed `.ambr` |
| recorded `.ambr` → future reviewers | The durable record of what an operator sees. | Snapshot text |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-200-01 | Denial of Service | `programming_vcc_over_rail_mv` in `firestarter/eprom_info.py` | medium | mitigate | `int((raw.get("electrical") or {}).get("vdd_mv", 0) or 0)` inside `try/except (TypeError, ValueError)`, returning `None`. Present and correct for all nine plan-enumerated cases (re-run this audit: `None`/`{}`/`{"electrical":{}}`/`0`/`5000`/non-numeric all return `None`). **Incomplete:** a *truthy non-dict* `electrical` (`"bogus"`, `123`, `[1,2]`) raises `AttributeError` — the `.get` is called on the string/int/list before the `int()` ever runs, so the except tuple never sees it. | open — below high threshold (non-blocking) |
| T-200-02 | Spoofing | `electrical.vdd_mv` from `~/.firestarter/database.json` | low | accept | Operator-owned file already authoritative for `vcc_mv`/`vpp_mv`; no new trust boundary. Recorded in `200-01-SUMMARY.md` § flagged assumptions. | closed (accepted) |
| T-200-03 | Information Disclosure | the elevated-VCC `logger.warning` line | low | mitigate | **Re-verified against `b3a777e`.** The reworded line interpolates only `_format_v_prose(int)` output and the module constant `_SHIELD_FIXED_VCC_MV` — grep for `part_number`/`chip_name`/`path`/`Name` inside the warning block returns 0. Format-string injection through a chip name stays closed by construction; the shortening removed text, it added no new interpolation. | closed |
| T-200-04 | Repudiation | the elevated-supply predicate regressing to silence | high | mitigate | Exact-string in-process test (`test_info_elevated_programming_vcc_warns`), its silence counterpart (`test_info_five_volt_part_emits_no_programming_vcc_warning`), two subprocess snapshots, and the 284-row census equality. All updated to the new wording and green: full suite **2100 passed / 36 snapshots**. Negative case re-run live (`W27C512`: no row, no warning). | closed |
| T-200-05 | Tampering | `tests/__snapshots__/test_characterization.ambr` | high | mitigate | Every re-record scoped to single node ids and gated on a reviewed `git diff --numstat`. **Re-exercised this audit** for the G-200-1 reword: `--snapshot-update` limited to `test_info_mbm27c1000` and `test_info_mbm27c4001`, numstat **2 insertions / 4 deletions**, and the full textual diff read to confirm both hunks are the warning block and nothing else. See deviation note below. | closed |
| T-200-06 | Spoofing | the `firestarter` entry point resolved by `shutil.which` | medium | mitigate | The harness resolves `shutil.which("firestarter")` and `pytest.skip`s when absent, but **no committed assertion pins the resolved install to this tree** — the plan's `firestarter.__file__` check was a plan-time verify leg, not a durable guard. Confirmed satisfied at audit time (`firestarter.__file__` = `/workspaces/firestarter_app/firestarter/__init__.py`), so no foreign output was recorded; the property is verified-at-the-time, not enforced. | open — below high threshold (non-blocking) |
| T-200-07 | Information Disclosure | recorded snapshot content | low | accept | Harness pins `FIRESTARTER_CONFIG_DIR` to a clean dir per run; recorded output is packaged-database chip metadata plus the warning sentence only. | closed (accepted) |
| T-200-08 | Tampering | `firestarter/data/chip_database.json` | high | mitigate | Census module mutates only `copy.deepcopy(db)` (three sites); no write path to the generated file exists in the module. Database confirmed byte-identical across a full module run. | closed |
| T-200-09 | Repudiation | the 284-row equality and its sibling counts | high | mitigate | 11 tests including three in-module planted mutations (synthetic row → 285, rewritten `vdd_mv`, rewritten `support_status`) plus an external planted mutation on `_EXPECTED_TOTAL_ROWS`, all observed to fail. Counts are exact equalities, not floors. | closed |
| T-200-10 | Tampering | the census module's own assertions over time | medium | mitigate | Source-shape guard (`test_module_source_shape_guards_against_weakening`) refuses the expected-failure marker, the skip marker, subset comparison and `>=` against the two load-bearing counts; its own literals are `+`-joined so it cannot match itself. | closed |
| T-200-SC | Tampering | npm/pip/cargo installs | low | accept | No package-manager install step in any of the three plans. `200-RESEARCH.md` § Package Legitimacy Audit records the gate as not applicable; only stdlib plus `pytest`/`syrupy` already pinned in `pyproject.toml`. | closed (accepted) |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above `workflow.security_block_on` (high) count toward `threats_open`*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

### Deviation note — T-200-05's numstat shape

Plan `200-02` specified the mitigation as "insertions with **zero deletions**", which was the
correct shape while the phase was only *adding* snapshot entries. The G-200-1 reword *replaces*
two lines with one, twice, so a zero-deletion numstat was structurally impossible. The mitigation's
intent — that no unrelated drift is laundered into the commit — was preserved by the stricter
substitute of reading the full diff: exactly two hunks, both the warning block, every other line in
the 36-entry file untouched. Recording this so a future reader does not read `2 4` as a violation
of the plan-time wording.

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-200-01 | T-200-02 | A local `~/.firestarter/database.json` is operator-owned and already the sole authority for `vcc_mv`/`vpp_mv`. Rendering an absurd operator-supplied `vdd_mv` verbatim crosses no new trust boundary. | Plan 200-01 (disposition: accept); recorded in `200-01-SUMMARY.md` | 2026-09-19 |
| R-200-02 | T-200-07 | Snapshot content is packaged-database metadata plus fixed prose, captured under a clean `FIRESTARTER_CONFIG_DIR`. No operator path, port or override can be recorded. | Plan 200-02 (disposition: accept) | 2026-09-19 |
| R-200-03 | T-200-SC | No package-manager install step exists in this phase. | Plans 200-01/02/03 (disposition: accept) | 2026-09-19 |

---

## Open Items (non-blocking — both below the `high` block threshold)

Neither item blocks phase advancement. Both are recorded so they are not rediscovered as novel.

1. **T-200-01 — `programming_vcc_over_rail_mv` fail-open is narrower than its docstring claims.**
   This is the same defect the phase's own code review filed as **CR-01** and the verifier scored as
   truth 10 (the single non-verified must-have, 9/10). Currently unreachable through `info`, because
   `database.py` calls `electrical.get("pin_count")` on the same raw record one layer earlier and
   would raise first; reachable only by a direct caller. Fix is one line — widen the except tuple to
   include `AttributeError`, or test `isinstance(electrical, dict)` — plus a test. **Disposition:
   backlog hardening item**, consistent with the verifier's and the code review's rulings.

2. **T-200-06 — no durable guard pins the snapshot harness to this source tree.**
   `shutil.which("firestarter")` will happily snapshot a sibling-worktree or stale editable install;
   the plan's `firestarter.__file__` containment check ran once at plan time and was never committed.
   Verified satisfied at this audit, so no recorded snapshot is suspect. A durable fix is a
   module-level assertion in `tests/test_characterization.py` that `firestarter.__file__` resolves
   inside the repo root. **Disposition: backlog hardening item.**

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-09-19 | 11 | 9 | 2 (both medium, below `high` threshold) | `/gsd-secure-phase 200` — orchestrator, ASVS L1 short-circuit (no auditor subagent) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed — no open threat at or above `workflow.security_block_on: high`
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-09-19
