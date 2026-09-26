---
phase: "181"
slug: "report-fidelity-schema-2-0-canonical-naming-hygiene-close"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
block_on: high
created: "2026-09-09"
register_authored_at_plan_time: true
threats_total: 36
threats_closed: 36
---

# Phase 181 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

Register authored at plan time — all ten `181-*-PLAN.md` files carry a line-anchored
`<threat_model>` block. The auditor's constraint was therefore **verify the stated mitigations
exist**, not scan for new threats. Verdict: `## SECURED`, 36/36 closed.

---

## Scope, stated proportionately

This is a **local-only host CLI** that programs EPROMs over a serial port. There is no network
service, no authentication, no session, no credential store, and no multi-tenant surface. Untrusted
input is limited to the operator's own `argv` and a chip they physically hold. Recording that plainly
matters: it is why 7 of 36 threats are `low` and why the register concentrates on integrity rather
than access control.

Two things in this system genuinely deserve scrutiny, and both are covered below:

1. **The filed GitHub issue body** — the one outward trust-boundary crossing, scrubbed by
   `sanitize_dict`. Several plans claim they neither widen nor bypass it; that claim was checked
   against the diff, not accepted.
2. **Dedup-hash integrity** — a filed issue body carries its own `dedup_fingerprint`, and
   `count_agreeing` reads that embedded hash and never re-hashes. A silent re-key is therefore
   **permanent for the historical corpus**. This is why so many Tampering rows point at the same 19
   frozen literals, and why D-16 committed the phase to zero re-keys.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| operator `argv` + the socketed chip → report object | The only untrusted content reaching a report is the operator's own chip and their own typed token. | Chip part-number token, chip contents |
| report object → filed GitHub issue body | **The one outward crossing.** `sanitize_dict` scrubs it; no plan in this phase widens or bypasses that path. | Diagnostic report JSON, dedup fingerprint |
| meta repo `.planning/` / `.claude/` → `firestarter_app` submodule | Two app-side tests read meta-tree fixtures. Guarded by `pytest.skip`; an unguarded reach-out is the measured defect that once sent app CI to `13 failed, 13 passed`. | Frozen schema-1.2/1.4 fixtures |
| first-party source → `ast.parse` in a test | Test-time only. Parsed text is never executed and no file is written. | Python source text |
| host → serial device | Operator-owned hardware, physically present. No remote actor. | Command frames, chip data |

---

## Threat Register

36 threats, IDs `T-181-01` … `T-181-36`. Severity: 14 high, 15 medium, 7 low.
Disposition: 32 `mitigate`, 4 `accept`. **All 36 CLOSED.**

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-181-01 | Tampering | 19 `FROZEN_HASHES` literals | high | mitigate | `report_shapes.py:729-747` byte-identical to `04fd982`; 19-way parametrized test, 106 passed | closed |
| T-181-02 | Tampering | frozen `devtest-triage` fixtures | medium | mitigate | Last touched phase 147 (`8b18ce74`); zero phase-181 commits | closed |
| T-181-03 | Repudiation | `evidence/*.txt` transcripts | low | mitigate | Flat `key=value` + verbatim command + explicit `rc=` on every leg | closed |
| T-181-04 | Tampering | firmware submodule, `chip_database.json` | low | mitigate | Both diff-empty; firmware porcelain-clean | closed |
| T-181-05 | Information Disclosure | `is_uv` in the filed body | low | **accept** | A bool describing the operator's own chip; `sanitize_dict` diff-empty | closed |
| T-181-06 | Tampering | `plan_shapes.json` | high | mitigate | `_generated_by` banner present; drift test, 6 passed | closed |
| T-181-07 | Tampering | `derive_plan`'s `write_scope` | high | mitigate | No default → bare call raises `TypeError`; independent AST scan found 0 bare calls | closed |
| T-181-08 | Repudiation | the 93-site census | medium | mitigate | Per-file `file:line` census in evidence, matching the SUMMARY | closed |
| T-181-09 | Tampering | firmware / generated DB | low | mitigate | As T-181-04 | closed |
| T-181-10 | Spoofing | `pyproject.toml` path resolution | medium | mitigate | Resolved from `__file__`, existence-asserted | closed |
| T-181-11 | Tampering | runtime dependency set | medium | mitigate | Set-equality pin + 2 bidirectional planted-RED + vacuity leg, 4 passed | closed |
| T-181-12 | Repudiation | dependency-pin evidence | low | mitigate | Transcript read verbatim, correct format | closed |
| T-181-13 | Tampering | the write-op selector | high | mitigate | Reads `write_scope` only; AST pin (`is_uv not in names`), 33 passed | closed |
| T-181-14 | Tampering | `sdp_oracle_applicable` | high | mitigate | Single arm; removal measured zero-effect; 145 passed | closed |
| T-181-15 | Tampering | HYG-04 allow-list | medium | mitigate | `_resolve_write_scope` removed from the allow-list in the same commit as its deletion (`0d2bb97`) | closed |
| T-181-16 | Information Disclosure | meta-tree fixture reach-out | low | **accept** | Forward-only parse test ran and PASSED — not skipped | closed |
| T-181-17 | Repudiation | CONTEXT.md amendment | medium | mitigate | Amendment marker present; falsified claim returns zero hits | closed |
| T-181-18 | Tampering | `ac.chip` raw token | high | mitigate | `cli_handlers.py:2417-2421` assigns the raw token; no reassignment anywhere in `firestarter/` | closed |
| T-181-19 | Spoofing | canonical part-number selector | medium | mitigate | Mirrors `get_eprom_config`'s ladder; 5 passed incl. whole-database agreement | closed |
| T-181-20 | Tampering | HYG-04 registration | medium | mitigate | `_canonical_part_number` registered at HEAD, gate exits 0. **See discrepancy note below.** | closed |
| T-181-21 | Information Disclosure | canonical name in the body | low | **accept** | `build_body` reads it off `sanitized_dict` | closed |
| T-181-22 | Tampering | `elapsed` | high | mitigate | Plain attribute read, no call node; `elapsed_expr_has_call_node=false` | closed |
| T-181-23 | Repudiation | `elapsed` without CLI context | medium | mitigate | Returns `None` absent context — measured, not assumed | closed |
| T-181-24 | Tampering | `duration_s` mean | medium | mitigate | Divisor is `len(ran)`; timing wrapper closes the only divergence case | closed |
| T-181-25 | Tampering | divergence `reason` | high | mitigate | Keyed on the boolean outcome, not mapping existence — the exact bug the wave-6 red gate caught | closed |
| T-181-26 | Denial of Service | fingerprint `evidence` dict | medium | mitigate | Structurally bounded; body 8,172 B against a 131,072 B cap | closed |
| T-181-27 | Repudiation | renamed divergence test | medium | mitigate | Old name absent, new name present, untouched sibling intact | closed |
| T-181-28 | Spoofing | `chip_id_actual` on a pass | high | mitigate | **The honesty ceiling.** `check_eprom_id` echoes the host's own expected id on a pass; the docstring says so rather than hiding it behind a passing equality | closed |
| T-181-29 | Tampering | the write-refusal predicate | high | mitigate | Fourth arm gated by `not write_refused`; 2 planted-RED legs + vacuity leg | closed |
| T-181-30 | Repudiation | slots arithmetic | medium | mitigate | Same shared predicate; planted-missing-condition leg reddens | closed |
| T-181-31 | Tampering | voltage-field deletion | high | mitigate | Attribute-scoped AST census (not textual), 4 passed; no surviving assignment | closed |
| T-181-32 | Tampering | frozen fixtures post-deletion | high | mitigate | Fixture porcelain; forward-only test re-run post-deletion, PASSED | closed |
| T-181-33 | Repudiation | `SKILL.md` disclosure | medium | mitigate | Sentence added at `:330`; the datasheet cross-check row left untouched — confirmed by reading the hunk | closed |
| T-181-34 | Repudiation | the green-tree battery | high | mitigate | 7 legs each with explicit `rc=`; reconciliation `2285 = collected(2285)` exact | closed |
| T-181-35 | Tampering | REQUIREMENTS.md edit scope | high | mitigate | Exactly 36 insertions / 36 deletions, only phase 181's 18 IDs; ROADMAP.md absent from that commit | closed |
| T-181-36 | Elevation of Privilege | outward-facing actions | medium | **accept** | `pushed=false, tagged=false, pr_opened=false, branch_cut=false` — all four measured | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above `high` count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

### Supply chain (`T-181-SC`)

A `T-181-SC` row recurs once per plan and is not part of the 36-count register, per the phase's own
accounting. Nine of ten are boilerplate low/accept ("no package installed") — **confirmed true**:
`pyproject.toml`'s only diff across the entire phase is the single `syrupy` bound line. The tenth
(plan 03) is a real high/mitigate row, `syrupy>=5.0,<7`, present in `pyproject.toml` and backed by
`tests/test_runtime_dependencies.py`.

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-181-01 | T-181-05 | `is_uv` is a boolean describing the operator's own chip, reaching a body they choose to file. No third-party data. | Phase 181 plan 01 threat model | 2026-09-09 |
| AR-181-02 | T-181-16 | The meta-tree fixture read is test-time only and `pytest.skip`-guarded. The guard was exercised — the test ran and passed rather than silently skipping. | Phase 181 plan 04 threat model | 2026-09-09 |
| AR-181-03 | T-181-21 | The canonical part number is read off `sanitized_dict`, so it crosses the boundary already scrubbed. | Phase 181 plan 05 threat model | 2026-09-09 |
| AR-181-04 | T-181-36 | The phase deliberately performs no outward action; the four negatives are measured in evidence rather than asserted. Shipping is a separate, operator-gated step. | Phase 181 plan 10 threat model (D-22) | 2026-09-09 |

*Accepted risks do not resurface in future audit runs.*

---

## Discrepancy noted, not rounded away

**T-181-20 — "same commit" wording.** The mitigation text says `_canonical_part_number` is registered
in HYG-04's allow-list *in the same commit* as its introduction. It is not: the helper landed in
`9019c53` and the registration in `2c1ebc2`, two commits later. The final state is correct and the
gate exits 0, so the threat is genuinely closed — but the register's own wording overstates the
discipline that was applied, and that is recorded here rather than quietly marked closed.

**WR-01 is not a threat.** The code review's one warning — `_is_interactive` left dead after 181-04
removed its only caller, with two tests named `..._on_a_tty` patching it under the belief they gate
TTY behaviour — was checked against all 36 rows. None of the register's threats treats
TTY/interactive gating as a security control, so this is a test-fidelity defect, not a mitigation
gap. Filed at `.planning/todos/pending/2026-09-08-is-interactive-dead-after-181-04.md`.

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-09-09 | 36 | 36 | 0 | `gsd-security-auditor` (ASVS L1, block_on high) |

**Method.** All ten `<threat_model>` blocks were read verbatim from the PLAN files rather than from
a summary. Every `mitigate` disposition was cross-referenced against live `firestarter_app` source at
HEAD via `git diff 04fd982..HEAD` plus targeted `git show`. The specific pytest modules each threat
cites were executed, matching the orchestrator's independently measured 2285/0 full suite. Two
claims were re-derived by AST scan rather than trusted from a transcript: T-181-07's zero-bare-calls
count, and T-181-26's evidence dict never carrying a list.

No `## Threat Flags` section exists in any of the ten SUMMARY files, so no implementation-time
surface was flagged that the register does not already cover.

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-09-09
