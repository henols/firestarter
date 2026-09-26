---
phase: "206"
slug: "dev-test-keeps-its-fidelity-on-one-session"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-09-23"
---

# Phase 206 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

Register origin: **authored at plan time**. All four PLAN.md files (`206-01` to `206-04`) carry a
`<threat_model>` block. This audit verified the mitigations named there. It did not build a
register retroactively. No SUMMARY.md raised a new `## Threat Flags` entry: `206-01`, `206-02` and
`206-03` each state "None beyond what the PLAN's `<threat_model>` already declared", and `206-04`
has no Threat Flags section.

Scope: `firestarter_app` range `2756ef0..d723cf7` (commits `5a772eb`, `c22287a`, `555c69d`,
`81ff585`, `fa6c8e8`, `3853b55`, `d723cf7`), plus the meta-repo bench record commits `069a34fc`
and `59b519cf`. ASVS L1, block on `high`. At L1 with no open threats the short-circuit rule
applies, so no auditor subagent was spawned. Verification is grep-depth, plus a run of the
mitigation tests: **119 passed**. The test files were `tests/test_session_lease.py`,
`tests/test_blast_radius_invariance.py` and `tests/test_chip_test_cycle.py`, plus these named
tests:

- `test_blank_check_verdict_2_is_skipped_with_status_error`
- `test_a_transport_failed_cycle_block_step_exits_2_not_0`
- `test_step_dict_emits_compare_evidence_and_compare_path_keys`

T-206-01 and T-206-SC are each declared in more than one plan. Each declaration is listed as its
own row, with a plan suffix, because the disposition differs between plans.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| firmware → host (serial) | COBS-framed responses and `MSG_*` ids, parsed by `frame_parser` with CRC8. Under a lease, a second setup ack crosses on an already-open link and must pass the same validation as the first. | acks, compare bytes, firmware identity |
| host → public GitHub (`henols/firestarter_prom`) | `dev test --submit` files a public issue whose body derives from `report.to_dict()`, keyed on `dedup_fingerprint`. | report body, including the new `compare_evidence` and `compare_path` keys |
| host → local disk | Reports persisted under `<config dir>/reports/`, each carrying a baked `dedup_fingerprint`. | historical report artifacts |
| host → device (electrical) | An open port holds DTR asserted. Closing it resets the Leonardo. `dev test` energizes VPP and VPE. | reset cadence, rail state |
| operator → CLI | Local chip name and flags. The "session" is a serial link, not an authenticated session. ASVS V2/V3/V4 do not apply. | CLI arguments |
| planner → operator | The keep-or-revert threshold is registered before the number exists. | decision criteria |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-206-06 | Tampering | `chip_test._aggregate_cycle_results` | high | mitigate | `status` is folded over the full `results` list, not over `ran` (docstring at `chip_test.py:1347-1352`). Tests: `test_a_transport_failed_cycle_keeps_the_run_status_error`, `test_fast_and_default_runs_agree_on_a_transport_failed_step_status`, and `test_a_transport_failed_cycle_block_step_exits_2_not_0`, which asserts exit 2 end-to-end. All pass. | closed |
| T-206-07 | Repudiation | `chip_test._dispatch_step` / `_dispatch_multi_run` | medium | mitigate | For verdict 2 the step becomes `VERDICT_SKIPPED` + `STATUS_ERROR`, with the message "blank check did not complete (setup, transport or hardware failure) -- blankness unknown" (`chip_test.py:2741-2751`). The verify path uses `verify_transport_failed = any(v == 2 ...)` (`chip_test.py:3459`). Test: `test_blank_check_verdict_2_is_skipped_with_status_error`. | closed |
| T-206-08 | Tampering | `tests/fixtures/report_shapes.py` / `diagnostic_report.dedup_fingerprint` | high | mitigate | `git log 2756ef0..d723cf7 -- tests/fixtures/report_shapes.py` is empty, and `git status` on `tests/fixtures/` is clean. `test_dedup_fingerprint_is_frozen` (`test_blast_radius_invariance.py:319`) passes. The evidence field sits outside the hashed allow-list, and the `compare_path` tag is empty by default, so no re-key occurs. | closed |
| T-206-09 | Tampering | `chip_test.compare_path_tag` | high | mitigate | `test_planted_compare_path_host_reddens_the_gate` (`test_blast_radius_invariance.py:417`) sets `compare_path=COMPARE_PATH_HOST` and asserts inequality against the frozen literal `FROZEN_HASHES[...]`, not against a second computed value. Passes. | closed |
| T-206-01 (206-02) | Information disclosure | `submit.sanitize_dict` / `build_body` | medium | mitigate | `compare_evidence` holds integers-or-`None` and a single classification from a fixed enum. `compare_path` takes one of two values, `""` or `"host"`. `206-02-SUMMARY.md` § Threat Flags records that Task 1 ran `compare_evidence` through `sanitize_dict`. `test_step_dict_emits_compare_evidence_and_compare_path_keys` pins the emitted shape. | closed |
| T-206-01 (206-04) | Information disclosure | `dev test --submit` during a bench run | high | mitigate | `206-SESSION-COST.md:50` records that both arms ran with "**never `--submit`**". `206-04-SUMMARY.md` § Verification confirms, by inspecting each of the six commands, that no `--submit` was passed. | closed |
| T-206-04 | Elevation of privilege | `eprom_operations._setup_operation` leased branch | high | mitigate | The leased branch (`eprom_operations.py:657-665`) calls `self.comm.setup_command(...)`. That method carries the firmware-version gate and the hardware-revision gate internally (`serial_comm.py:805` onward). Only an explicit `allow_outdated_firmware` caller opt-in waives the version gate. Test: `test_a_leased_setup_runs_the_firmware_and_hardware_gates` (`test_session_lease.py:240`). Passes. | closed |
| T-206-02 | Tampering | leased link input buffer | high | mitigate | `self.comm.consume_remaining_input()` (`eprom_operations.py:663`) runs before `setup_command` (`:665`). `test_a_leased_setup_drains_input_before_sending_the_setup_command` (`test_session_lease.py:190`) asserts the order. Passes. | closed |
| T-206-12 | Denial of service | leased link failure policy | medium | mitigate | Under D-06, a `SerialError` disconnects the link and the next operation cold-connects (docstring at `eprom_operations.py:783-786`). Test: `test_a_mid_plan_serial_error_drops_the_lease_and_the_plan_continues` (`test_session_lease.py:290`). Passes. | closed |
| T-206-14 | Repudiation | `206-SESSION-COST.md` | medium | mitigate | Each figure is labelled measured or derived. See § 2, "The measured wall-clock", and the § 3 connect census, "totals DERIVED, never measured". § 4 is an explicit non-measurement statement. | closed |
| T-206-15 | Tampering | the keep-or-revert decision | high | mitigate | Commit `069a34fc` (2026-09-23 10:42:25Z) registered the threshold. Commit `59b519cf` (11:51:44Z) recorded the measurement. The threshold commit is the earlier of the two. | closed |
| T-206-17 | Tampering | `firestarter_app` branch state | high | mitigate | The lease was KEPT, so no revert commit exists: `git log 2756ef0..HEAD` has no "revert" subject. The `firestarter_app` branch is `v1.41-verification-to-host`, confirmed live on 2026-09-23. | closed |
| T-206-01 (206-01) | Information disclosure | `submit.build_body` / `sanitize_dict` | medium | accept | See the Accepted Risks Log. | closed |
| T-206-10 | Repudiation | `submit.find_prior_report` | medium | accept | See the Accepted Risks Log. | closed |
| T-206-11 | Information disclosure | `firestarter/compare.py` | low | accept | See the Accepted Risks Log. `git log 2756ef0..d723cf7 -- firestarter/compare.py` is empty. | closed |
| T-206-05 | Spoofing | leased link port identity | low | accept | See the Accepted Risks Log. | closed |
| T-206-13 | Tampering | `firestarter/constants.py` and the firmware headers | low | accept | See the Accepted Risks Log. `git log 2756ef0..d723cf7 -- firestarter/constants.py` is empty. No firmware file is in the range diff. | closed |
| T-206-16 | Denial of service | the bench board | medium | accept | See the Accepted Risks Log. | closed |
| T-206-SC | Tampering | npm/pip/cargo installs | low | accept | See the Accepted Risks Log. | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-206-01 | T-206-01 (206-01) | Plan 01 adds no report field and no free-text source, and leaves `sanitize_dict` unchanged. Plan 02 owns the new fields and re-tests this boundary under its own T-206-01 row, which is mitigated and closed. | planner (206-01-PLAN.md `<threat_model>`) | 2026-09-23 |
| AR-206-02 | T-206-10 | Host-path reports form new `count_agreeing` groups. Issues already filed keep their old ids and cannot be rejoined. A human accepted this at the 206-02 decision checkpoint, and the affected population is named in the phase record. | operator at the 206-02 `blocking-human` checkpoint | 2026-09-23 |
| AR-206-03 | T-206-11 | `compare.py` is consume-only this phase and import-pure by an AST check. Its diff in the range is empty. | planner (206-02-PLAN.md `<threat_model>`) | 2026-09-23 |
| AR-206-04 | T-206-05 | Port spoofing cannot happen while the leased port never closes. The 203-CR-01 `preferred_port` pin is now redundant under a lease. It is kept in place and not deleted. | planner (206-03-PLAN.md `<threat_model>`) | 2026-09-23 |
| AR-206-05 | T-206-13 | The lease adds no wire constant and no flag bit, so the rule that host and firmware constants change together does not trigger. Both diffs are empty. | planner (206-03-PLAN.md `<threat_model>`) | 2026-09-23 |
| AR-206-06 | T-206-16 | `dev test` is destructive by design. The operator has standing permission to flash and exercise the bench boards. The seated part was confirmed before any rail was energized. | operator (standing bench permission) | 2026-09-23 |
| AR-206-07 | T-206-SC | This phase installs no packages. `206-RESEARCH.md` § Package Legitimacy Audit records that no package-manager command appears in the phase. | planner (all four PLAN.md `<threat_model>` blocks) | 2026-09-23 |

*Accepted risks do not resurface in future audit runs.*

**Non-security review findings, recorded for traceability.** `206-REVIEW.md` has two open findings,
WR-01 and WR-02. WR-01: `captured_compare[0]` silently truncates if the compare callback ever
fires more than once. WR-02: the verify multi-run loop continues after a verdict-2 result. Both
are robustness and code-quality warnings. Neither maps to a register threat, and neither weakens
any mitigation above. WR-01 is not live today, because `on_result` fires at most once per call.
WR-02 still classifies the step as `VERDICT_SKIPPED`/`STATUS_ERROR` from run 1 alone, so T-206-07
holds. Both findings stay open in the code-review track, not this one.

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-09-23 | 19 (17 unique ids; T-206-01 declared in three plans) | 19 | 0 | /gsd-secure-phase orchestrator (L1 short-circuit, no auditor spawned) |

## Security Audit 2026-09-23
| Metric | Count |
|--------|-------|
| Threats found | 19 |
| Closed | 19 |
| Open | 0 |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-09-23
