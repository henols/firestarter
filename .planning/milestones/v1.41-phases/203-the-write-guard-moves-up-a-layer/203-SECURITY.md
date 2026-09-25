---
phase: "203"
slug: "the-write-guard-moves-up-a-layer"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-09-21"
---

# Phase 203 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

Register origin: **authored at plan time**. All four PLAN.md files
(`203-01`, `203-02`, `203-03`, `203-04`) carry a `<threat_model>` block, so this audit
verified the mitigations named there rather than building a register retroactively.
No SUMMARY.md raised a `## Threat Flags` entry.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| operator CLI arguments → host | `-a`/`--address`, `--verify`, `--full`, the input file path and its length are the only untrusted inputs on this path. | signed integer string, file path, file length |
| host → programmer (serial) | The composed command dict crosses at `SerialCommunicator.find_and_connect`. A wrong region here drives real hardware. | command dict (address, memory-size, flags), binary payload |
| chip database (shipped or `~/.firestarter` override) → predicate | A user-supplied override can introduce a protocol id the shipped database does not contain. | `algorithm` / `flags` fields of the wire dict |
| host exit code → calling script or CI job | A published contract. A wrong code here is acted on by automation that cannot see the message. | exit code 0 / 1 / 2 |
| host → operator (help text and refusals) | `--help` is the only place an operator learns what the tool will and will not check before writing. | user-facing prose |
| this phase's record → Phase 206 | `203-SESSION-COST.md` is consumed by a later phase as a baseline it compares a real measurement against. | measured vs derived timing figures |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-203-01 | Tampering | `write_blank_guard.is_guarded_protocol` / the whole predicate | critical | mitigate | Predicate keys on `algorithm`/`flags` only. `test_predicate_module_reads_only_algorithm_and_flags_keys` (`tests/test_write_blank_guard.py:172`) proves it by key perturbation — injecting a foreign key must not change the verdict — which is stronger than the planned AST subset assertion. `test_predicate_fires_against_real_resolve_chip_dicts` (`:759`) drives the predicate with dicts from the genuine `resolve_chip`. A module comment at `write_blank_guard.py:186-192` records why: `check_eprom_blank`'s SRAM short-circuit is inert in production because it reads keys the wire dict never carries. | closed |
| T-203-02 | Tampering | `_run_write_blank_guard` region arithmetic | high | mitigate | Region is `address → address + region_length`, where `region_length` is the same `os.path.getsize(input_file_path)` the write itself uses (`eprom_operations.py:2335`). `if not region_length` (`:2367`) skips the guard for a `None` or zero region rather than comparing over a degenerate one. Strengthened beyond plan by 203-CR-01: the guard's own resolved port is captured and the write's connect is pinned to it (`restrict_to_port=True`), so the region proved blank and the region written cannot diverge onto two boards. | closed |
| T-203-03 | Information disclosure | `write_blank_guard.refusal_text` | medium | mitigate | Single line built from `_REFUSAL_FORMAT`, no remedy clause. `test_refusal_text_message_shape_is_pinned_by_equality_and_carries_no_forbidden_content` (`tests/test_write_blank_guard_pinning.py:237`) pins the exact sentence by equality and asserts a forbidden-substring list including `bypass`. | closed |
| T-203-04 | Elevation of privilege | `--force` interaction with the guard | medium | mitigate | `FLAG_FORCE` appears nowhere in `write_blank_guard.py` except one docstring line stating it is deliberately not consulted; the predicate never reads it. See also T-203-08. | closed |
| T-203-05 | Denial of service | the extra port open the guard costs | low | accept | Accepted — see Accepted Risks Log R-01. | closed |
| T-203-06 | Tampering | `address_parser.parse_address` → `write_eprom` region arithmetic | high | mitigate | `require_non_negative_address` gates both tiers: `cli_handlers.py:862` before the operator is invoked, and `eprom_operations.py:2327` immediately after `require_page_alignment` and before `os.path.getsize`, so it fires before any port opens. `NegativeStartAddressError` is mapped above the generic `EpromOperationError` arm (`cli_handlers.py:228` vs `:234`). Pinned pre-connect by `test_write_eprom_negative_start_address_refuses_before_operation_context` and on both guarded and unguarded families (`test_write_blank_guard_pinning.py:417,483,487`). | closed |
| T-203-07 | Tampering | `write_blank_guard.GUARDED_PROTOCOL_IDS` drift | critical | mitigate | Four independent pins in `tests/test_write_blank_guard_pinning.py`: exact-set equality (`:88`), named-exempt exact set (`:97`), disjointness of the two sets (`:107`), and database coupling — `test_predicate_matches_real_database_guarded_rows_exactly` (`:120`) plus a per-row census (`:185`). Narrowing and widening both fail. `test_is_guarded_protocol_fails_closed_on_absent_evidence` (`:362`) covers the missing-evidence arm. | closed |
| T-203-08 | Elevation of privilege | `FLAG_FORCE` | medium | mitigate | `test_write_blank_guard_pinning.py:259` asserts `requires_blank_check(guarded, FLAG_FORCE) is True`. Only `FLAG_SKIP_BLANK_CHECK` bypasses, and `test_build_op_flags_blank_check_false_sets_only_the_skip_blank_check_bit` (`:262`) pins that the real flag builder sets no other bit. | closed |
| T-203-09 | Spoofing | a `~/.firestarter` override introducing an unknown protocol id | low | accept | Accepted — see Accepted Risks Log R-02. | closed |
| T-203-10 | Repudiation | the `--verify` verdict lines | high | mitigate | Both operator methods suppress their own verdict line under `suppress_verdict_line` (`eprom_operations.py:2535`, `:2820`), keyword-only and defaulting false (pinned at `test_write_verify.py:580`). `test_verdict_constants_never_contain_the_forbidden_word` (`:880`) asserts all four CLI verdict constants are free of the success word, and `test_could_not_verify_line_absent_from_the_other_six_arms` (`:830`) closes the cross-arm leak. A caller cannot be told a write succeeded when it was never compared. | closed |
| T-203-11 | Tampering | the exit-code branch in `cli_handlers.write` | high | mitigate | One dedicated test per arm of the seven-arm contract (`test_write_verify.py:664,681,705,726,745,764,780`), including the three that separate a transport or hardware cause from a decided one — guard read (arm 2), write (arm 3), read-back (arm 5). Both cause channels (`last_write_guard_verdict`, `last_write_attempt_verdict`) have their own classification tests (`:356`–`:507`), plus a structural pin that `_setup_operation` has exactly three `None`/0 returns (`:559`). No transport failure is reported as a plain failure. | closed |
| T-203-12 | Information disclosure | the compare report under `--full` | low | accept | Accepted — see Accepted Risks Log R-03. Premise re-verified this audit; see the note below the table. | closed |
| T-203-13 | Denial of service | the third port open `--verify` adds | low | accept | Accepted — see Accepted Risks Log R-04. | closed |
| T-203-14 | Spoofing | the `write` help text | high | mitigate | The `write` docstring now attributes the blank check to the host ("the host — not the firmware — checks that the target region is blank") and names all four unguarded families (0x0D 28C parallel, 0x05 flash4, SRAM, FRAM), stating plainly that `-b` has nothing to skip on them. No stale "firmware checks" claim survives anywhere in the file or the snapshots. | closed |
| T-203-15 | Repudiation | the two `write --help` snapshots | medium | mitigate | Both snapshot bodies in `tests/__snapshots__/test_characterization.ambr` (`test_help_write`, `test_no_blank_check_polarity`) carry the new text; a grep for the superseded claim returns nothing. All 36 snapshots pass against the live help output, so the hand-edit matches reality rather than having been regenerated over. | closed |
| T-203-16 | Repudiation | `203-SESSION-COST.md` | high | mitigate | Every figure in the §5 summary table carries a `Measured or derived` column and a source artifact with section (`176-MEASUREMENT.md` §4a/§4b for the connect medians; this document §1/§3 for the derived open counts). §4 states in plain words: "**Phase 203 took no new hardware measurement.**" and warns SESS-02 to treat the guard-read/read-back traffic component as unknown until measured. | closed |
| T-203-SC | Tampering | package-manager installs | n/a | accept | Verified rather than assumed: no Phase 203 commit touches `pyproject.toml` (the most recent dependency commit predates the phase), and `write_blank_guard.py` imports only stdlib (`typing`) and first-party `firestarter.*` modules. No external package was installed by any of the four plans. | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

**Scope note on T-203-12.** The threat text says the plan "does not touch" the compare
renderer. Plan 01 did touch `compare.py`, adding `CompareResult.first_actual` and populating
it in `CompareAccumulator.feed` — and `first_actual` is a byte value. The security property
still holds: `render_compare_lines` (`compare.py:516-553`) emits only coalesced ranges, byte
counts and a bucket line, and its docstring records "Emits no expected value and no actual
value anywhere". `first_actual` is read at exactly one site,
`eprom_operations.py:2235-2240`, to build the guard refusal line. So one byte value is
disclosed — at the refusal, to the operator who owns the chip, mirroring the evidence the
firmware's own `MSG_ERR_NOT_BLANK` has always carried (D-10) — and none in the `--full`
report. Recorded here so a future audit does not read the plan's wording as still literally
true.

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-01 | T-203-05 | Three port opens per guarded `write --verify` is a known, measured cost accepted for this phase (D-17). Phase 206 SESS-01 owns collapsing it. The derivation and its provenance caveats are in `203-SESSION-COST.md`. | Operator (D-17, plan 01) | 2026-09-21 |
| R-02 | T-203-09 | Fork A resolves an unknown protocol id from a `~/.firestarter` override as unguarded, matching "preserve today's coverage". The operator who supplies an override database is the same operator who owns the chip. `test_is_guarded_protocol_false_for_an_id_in_neither_set` pins the behaviour, and the reasoning is recorded at the site. | Operator (Fork A, plan 02) | 2026-09-21 |
| R-03 | T-203-12 | `--full` reports coalesced address ranges and byte counts, never byte values. Verified this audit against the live renderer, not inherited from the plan text — see the scope note above. | Operator (plan 03) | 2026-09-21 |
| R-04 | T-203-13 | The third port open is an opt-in cost: `--verify` is not the default, so default write time is unchanged. Measured and recorded (D-17) for Phase 206 SESS-02 to act on. | Operator (D-17, plan 03) | 2026-09-21 |
| R-05 | T-203-SC | This phase installs no external package. Confirmed against the commit range and the new module's import list rather than accepted on the plan's word. | This audit | 2026-09-21 |

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-09-21 | 17 | 17 | 0 | /gsd-secure-phase (orchestrator, ASVS L1) |

**Method.** Register taken from the four PLAN.md `<threat_model>` blocks
(`register_authored_at_plan_time: true`). Each mitigate-disposition threat was checked against
the implementation and its pinning test, not against the SUMMARY's account of it. The four
accept-disposition threats had their premises re-checked before being logged as accepted; one
(T-203-12) needed the scope note above. Test evidence: `tests/test_write_blank_guard.py`,
`tests/test_write_blank_guard_pinning.py`, `tests/test_write_verify.py` and
`tests/test_characterization.py` run together — 126 passed, 36 snapshots passed.

Per the ASVS L1 short-circuit (`threats_open: 0`, register authored at plan time, level 1),
no separate auditor subagent was spawned; grep-depth verification is sufficient at this level.

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-09-21
