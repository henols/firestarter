---
phase: "203"
slug: "the-write-guard-moves-up-a-layer"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: validated
nyquist_compliant: false
wave_0_complete: true
created: "2026-09-21"
reconstructed_from: artifacts
reconstruction_note: "State B — no VALIDATION.md existed at phase close. Reconstructed from the four PLAN/SUMMARY pairs, 203-VERIFICATION.md and 203-REVIEW.md, then gap-filled."
---

# Phase 203 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Reconstructed retroactively — this phase executed and closed before a VALIDATION.md existed.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x (+ syrupy for `.ambr` snapshots, Click `CliRunner` for CLI arms) |
| **Config file** | `firestarter_app/pyproject.toml` `[tool.pytest.ini_options]` (`testpaths = ["tests"]`, `addopts = "-ra -q"`) |
| **Quick run command** | `cd firestarter_app && python -m pytest tests/test_write_blank_guard.py tests/test_write_blank_guard_pinning.py tests/test_write_verify.py tests/test_write_guard_port_pinning.py -o addopts="" -q` |
| **Full suite command** | `cd firestarter_app && python -m pytest tests/ -o addopts="" -q` |
| **Estimated runtime** | ~25 s quick (130 tests incl. characterization) · ~7 min full suite |

**Infrastructure notes**

- `addopts` already carries `-q`. Always pass `-o addopts=""` or the pass/fail count line is
  suppressed and a run that collected nothing reads identically to a green one.
- Integration tests drive the genuine `EpromOperator.write_eprom` through a patched
  `SerialCommunicator.find_and_connect` seam. Every simulated connection needs its **own** fresh
  `_FakeSerial`; sharing one across a guard-read-then-write drive fails on the second connect
  with "Not connected".
- `tests/fake_chip.py`'s `WriteInitPreflightChip` models the **firmware** write-init pre-flight and
  is explicitly disqualified from providing host-path coverage for this phase.
- `--snapshot-update` is forbidden in this repo. Both `write --help` `.ambr` blocks were
  hand-edited and must stay byte-identical to each other.
- ruff `select` is `[E, F, I, UP]`, so a `# noqa: BLE001` added to a test here would be inert.

---

## Sampling Rate

- **After every task commit:** quick run command above
- **After every plan wave:** full suite command above
- **Before `/gsd-verify-work`:** full suite must be green
- **Max feedback latency:** ~25 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 203-01-01 | 01 | 1 | WRITE-01 | — | Guarded, non-erase-exempt write to a non-blank region is refused host-side; no `COMMAND_WRITE` reaches the connect seam | integration | `pytest tests/test_write_blank_guard.py -k test_write_to_non_blank_region_of_guarded_part_is_refused -o addopts="" -q` | ✅ | ✅ green |
| 203-01-02 | 01 | 1 | WRITE-01 | — | Refusal is exactly one line, names first non-blank address and its value, carries no remedy/bypass clause | unit | `pytest tests/test_write_blank_guard.py -k "refusal_text" -o addopts="" -q` | ✅ | ✅ green |
| 203-01-03 | 01 | 1 | WRITE-01 | T-203-inert-guard | Predicate reads **only** `algorithm` and `flags`; fails closed on absent/None evidence | unit + AST | `pytest tests/test_write_blank_guard.py -k "reads_only_algorithm_and_flags or fails_closed" -o addopts="" -q` | ✅ | ✅ green |
| 203-01-04 | 01 | 1 | WRITE-01 | T-203-inert-guard | Predicate fires against **real** `resolve_chip` wire dicts, not hand-built literals | integration | `pytest tests/test_write_blank_guard.py -k test_predicate_fires_against_real_resolve_chip_dicts -o addopts="" -q` | ✅ | ✅ green |
| 203-01-05 | 01 | 1 | WRITE-01 | T-203-short-read | **Incomplete** guard read (no divergence seen, region not fully covered) refuses the write; verdict 1 not 2; no `COMMAND_WRITE` on the wire | integration | `pytest tests/test_write_blank_guard.py -k incomplete -o addopts="" -q` | ✅ | ✅ green *(added by this audit — G1)* |
| 203-01-06 | 01 | 1 | WRITE-06 | — | Blank region of a **non-blank** part still writes: sequence is exactly `[COMMAND_READ, COMMAND_WRITE]` | integration | `pytest tests/test_write_blank_guard.py -k test_write_into_blank_region_of_non_blank_part_succeeds_via_host_path -o addopts="" -q` | ✅ | ✅ green |
| 203-01-07 | 01 | 1 | WRITE-01 | — | Guard reads only `address`..`address+len(file)`, never the whole device; zero-byte input pays no guard read | integration | `pytest tests/test_write_blank_guard.py -k "zero_byte or erase_exempt_part_pays_no_guard_read" -o addopts="" -q` | ✅ | ✅ green |
| 203-01-08 | 01 | 1 | WRITE-01 | — | `CompareResult.first_actual` additive; `render_compare_lines` output unchanged (`verify`/`blank` never pass `on_result`) | unit + AST | `pytest tests/test_write_blank_guard.py -k "first_actual or never_pass_on_result or still_emits_mismatch_line" -o addopts="" -q` | ✅ | ✅ green |
| 203-02-01 | 02 | 2 | WRITE-02 | T-203-set-drift | `GUARDED_PROTOCOL_IDS == {0x06,0x07,0x08,0x0B,0x10}` — pinned by **set equality**, so narrowing *or* widening reds | unit | `pytest tests/test_write_blank_guard_pinning.py -k five_firmware_pre_flighted -o addopts="" -q` | ✅ | ✅ green |
| 203-02-02 | 02 | 2 | WRITE-02 | T-203-set-drift | `NAMED_EXEMPT_PROTOCOL_IDS` pinned by equality; disjoint from the guarded set; every SRAM id exempt | unit | `pytest tests/test_write_blank_guard_pinning.py -k "six_named_ids or disjoint or every_sram_id" -o addopts="" -q` | ✅ | ✅ green |
| 203-02-03 | 02 | 2 | WRITE-02 | T-203-set-drift | Predicate matches the **database-derived** guarded row set exactly, both sides derived live from `EpromDatabase`/`resolve_chip` | integration | `pytest tests/test_write_blank_guard_pinning.py -k "real_database_guarded_rows or guarded_row_count" -o addopts="" -q` | ✅ | ✅ green |
| 203-02-04 | 02 | 2 | WRITE-03 | — | `-b` sets only `FLAG_SKIP_BLANK_CHECK`, never `FLAG_SKIP_ERASE`; pays no guard read end-to-end | unit + integration | `pytest tests/test_write_blank_guard_pinning.py tests/test_write_blank_guard.py -k "blank_check_false_sets_only or no_blank_check_via_build_op_flags" -o addopts="" -q` | ✅ | ✅ green |
| 203-02-05 | 02 | 2 | WRITE-03 | T-203-rearm | `--skip-erase` **re-arms** the guard on an erase-capable part (D-03); `--force` does not bypass it (D-09) | unit + integration | `pytest tests/test_write_blank_guard_pinning.py tests/test_write_blank_guard.py -k "skip_erase_rearms or skip_erase_on_erase_capable" -o addopts="" -q` | ✅ | ✅ green |
| 203-02-06 | 02 | 2 | WRITE-03 | — | `dev test` / `dev write-cycle` dispatch shapes unchanged; UV write shortcut still works and the unmasked case stays guarded | integration | `pytest tests/test_chip_test.py tests/test_chip_test_cycle.py tests/test_chip_test_uv_slot_write.py tests/test_chip_test_sdp_leg.py tests/test_dev_test_cmd.py -o addopts="" -q` | ✅ | ✅ green |
| 203-02-07 | 02 | 2 | WRITE-02 | T-203-signed-region | Negative `--address` refused before the port opens, at both the CLI and operator tiers, on guarded and unguarded families | unit + CLI | `pytest tests/test_write_blank_guard_pinning.py -k negative -o addopts="" -q` | ✅ | ✅ green |
| 203-03-01 | 03 | 3 | WRITE-04 | — | `write --verify` runs exactly one read-back over `address`..`address+len(file)` through `_drive_region_compare`; `--full` passes through | CLI + integration | `pytest tests/test_write_verify.py -k "full_flag_passed_through or verify_alone_passes_full_false or size_str_none" -o addopts="" -q` | ✅ | ✅ green |
| 203-03-02 | 03 | 3 | WRITE-04 | T-203-exit-collapse | Seven-arm exit contract: 0 verified · 1 host/firmware-decided · 2 transport/hardware **in any phase** incl. the write itself | CLI | `pytest tests/test_write_verify.py -k arm -o addopts="" -q` | ✅ | ✅ green |
| 203-03-03 | 03 | 3 | WRITE-04 | T-203-exit-collapse | `last_write_attempt_verdict` cause channel distinguishes a mid-write port drop (2) from a firmware error frame (1) | integration | `pytest tests/test_write_verify.py -k last_write_attempt_verdict -o addopts="" -q` | ✅ | ✅ green |
| 203-03-04 | 03 | 3 | WRITE-05 | T-203-false-success | The word "successful" appears on no `--verify` arm; the four verdict constants are pinned free of it | unit + CLI | `pytest tests/test_write_verify.py -k "verdict_constants_never_contain or suppress_verdict_line" -o addopts="" -q` | ✅ | ✅ green |
| 203-03-05 | 03 | 3 | WRITE-05 | T-203-false-success | The could-not-verify line fires on **exactly one** arm (write landed, read-back failed) and is absent from the other six | CLI | `pytest tests/test_write_verify.py -k could_not_verify_line_absent -o addopts="" -q` | ✅ | ✅ green |
| 203-03-06 | 03 | 3 | WRITE-04 | — | Plain `write` keeps its 0/1 contract; `verify`/`blank` byte-identical; `--full` without `--verify` is a usage error | CLI + snapshot | `pytest tests/test_write_verify.py tests/test_characterization.py -k "without_verify or full_without_verify" -o addopts="" -q` | ✅ | ✅ green |
| 203-03-07 | 03 | 3 | WRITE-01 | T-203-board-swap | **CR-01**: the write's connect is pinned to the guard's resolved port; a board that drops mid-sequence fails closed, never silently lands on board B | integration | `pytest tests/test_write_guard_port_pinning.py -o addopts="" -q` | ✅ | ✅ green |
| 203-04-01 | 04 | 4 | WRITE-03 | T-203-stale-help | `write --help` attributes the blank check to the **host** and names the unguarded families; both `.ambr` blocks identical and green without any snapshot-update | snapshot | `pytest tests/test_characterization.py -k "help_write or no_blank_check_polarity" -o addopts="" -q` | ✅ | ✅ green |
| 203-04-02 | 04 | 4 | WRITE-03 | T-203-stale-help | The help's unguarded-family prose is **coupled to the live** `NAMED_EXEMPT_PROTOCOL_IDS` / `SRAM_PROTOCOL_IDS` sets — an id added to or removed from either reds this test | CLI + coupling | `pytest tests/test_write_blank_guard_pinning.py -k live_exempt -o addopts="" -q` | ✅ | ✅ green *(added by this audit — G2)* |
| 203-04-03 | 04 | 4 | WRITE-04 | — | `write --help` documents `--verify`/`--full` and states all three exit codes plus the plain-`write`-unchanged clause | CLI | `pytest tests/test_write_verify.py -k help_lists_verify_and_full -o addopts="" -q` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements. pytest, syrupy and Click's `CliRunner` were
already installed and configured; this phase added four test modules to the existing `tests/` tree
and needed no framework work.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `write -b` still **erases** an erase-capable part | WRITE-03 (roadmap criterion 3) | The erase itself is a firmware behaviour. Phase 203 is app-only and bench-no; the host half — that `_build_op_flags(blank_check=False)` never sets `FLAG_SKIP_ERASE` — is automated (203-02-04), but nothing in this repo can observe the erase actually running. 203-02-SUMMARY.md scopes this explicitly rather than overclaiming it. | On the bench, with a W27C512 (or another `FLAG_CAN_ERASE` part) holding known non-blank data: `firestarter write -b w27c512 pattern.bin`, then `firestarter read` and confirm the whole region reads back as `pattern.bin` with no residue of the prior contents. Deferred to the Phase 205 bench gate, which already re-runs the erase path. |
| "Reasoning is stated at the exemption site" | WRITE-02 (roadmap criterion 2, structural half) | The reasoning lives in source comments/docstrings beside each exemption. An automated assertion would have to pattern-match prose and would red on ordinary rewording, while the property it guards is already enforced socially by review and structurally by the set-equality pin (203-02-02) — no id can enter or leave the set without a deliberate test edit. Routed to manual-only by operator decision during this audit. | Read `firestarter_app/firestarter/write_blank_guard.py` around `GUARDED_PROTOCOL_IDS` (~L53) and `NAMED_EXEMPT_PROTOCOL_IDS` (~L67-95). Confirm each of `0x05`, `0x0D` and the SRAM/FRAM block carries its own stated reason at its own site. Last confirmed 2026-09-21 in 203-VERIFICATION.md truth 2. |
| A second identical guarded write to the same region is refused | WRITE-01 | Declared `verification: backstop` in 203-02-PLAN.md's own frontmatter — it is a consequence of the primary refusal property (203-01-01), not an independent behaviour, and the plan classified it as documentation-level from the start. | Consequence of 203-01-01: the first write leaves the region non-blank, so the second is refused by the same path. Matches firmware behaviour today and is the correct outcome, not a regression. |
| Advisory WR-01 wording | WRITE-05 | A `--verify` run whose write physically landed but whose `--skip-sdp-unlock` ack check fails prints "did not complete — nothing was verified", which misdescribes that one state. Exit code (1) is correct. Recorded in 203-REVIEW.md as deliberately-not-fixed; the current behaviour **is** pinned by `test_last_write_attempt_verdict_zero_when_skip_sdp_unlock_ack_check_fails`, so this row tracks the accepted wording debt, not an untested path. | Only reachable with `--skip-sdp-unlock` against firmware old enough not to ack. Re-assess if Phase 207's REL-04 documents this arm in the wiki. |

---

## Validation Audit 2026-09-21

| Metric | Count |
|--------|-------|
| Gaps found | 5 |
| Resolved | 2 |
| Escalated | 0 |
| Routed to manual-only | 3 |

**Gaps resolved**

| Gap | Requirement | Test added | Non-vacuity proof |
|-----|-------------|-----------|-------------------|
| G1 | WRITE-01 | `tests/test_write_blank_guard.py::test_write_with_incomplete_guard_read_is_refused_and_no_write_reaches_the_wire` | Mutation probe: relaxing `_drive_region_compare`'s fail-closed branch to `if result.total > 0 and result.bad == 0:` (dropping the `compared == total` clause) reds the test — the write proceeds past the guard and exhausts the fixture's single-connection fake serial. Reverted; `git diff` clean. Re-proved independently by the orchestrator, not only by the auditor. |
| G2 | WRITE-03 | `tests/test_write_blank_guard_pinning.py::test_write_help_names_every_unguarded_family_in_the_live_exempt_set` | Mutation probe: adding a spare `0x99` to `NAMED_EXEMPT_PROTOCOL_IDS` reds the test with `protocol id 0x99 is in NAMED_EXEMPT_PROTOCOL_IDS but never named in 'write --help'`. Reverted; `git diff` clean. Re-proved independently by the orchestrator. |

**What G1 closes.** `_drive_region_compare` fails closed on an incomplete compare — `result.bad == 0`
but `result.compared != result.total` returns verdict 1, so a guarded write whose blank-check read
ended short is refused rather than treated as blank. That branch had no test. It is the exact arm
203-01-PLAN.md's standing prohibition names ("the guard must never become silently inert"), and after
Phase 205 removes the firmware pre-flight it is the only thing standing between a short read and an
irreversible UV overwrite. The test also characterizes — deliberately does **not** fix — advisory
WR-02: with no divergent byte ever observed the refusal line carries a synthesized
`0x<region_start>` / `0x00` pair rather than an observed one.

**What G2 closes.** `write --help`'s "Four protocol families never receive that check…" sentence was
pinned only by a syrupy snapshot of the prose against itself. Widening `NAMED_EXEMPT_PROTOCOL_IDS`
would red the set-equality pin (forcing a deliberate edit there) while leaving the help text green
and stale. The new test derives its expectation from the live sets — every non-SRAM exempt id must
appear as a hex literal, `SRAM`/`FRAM` must be named, and the prose's family count must match what
the live set implies.

**Verification of the audit's own work.** Both new tests were committed in `firestarter_app`
`4d5f878` (test files only — `git show --stat` confirms no implementation file in the commit). Both
mutation probes were re-run independently by the orchestrator and both reverted to a clean
`git diff`. Post-audit: 92 tests green across the four write-guard modules (baseline 90), 130 green
including `test_characterization.py`, 36/36 snapshots, `ruff check` and `ruff format --check` clean.

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references — n/a, existing infrastructure sufficed
- [x] No watch-mode flags
- [x] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter — **not set**: four behaviours remain
      manual-only (see the table above). Three are manual by construction (a firmware erase this
      app-only phase cannot observe, a source-prose property, and a plan-declared backstop); the
      fourth tracks accepted wording debt on an otherwise-pinned path. No requirement is left
      without automated verification of its host-side behaviour.

**Approval:** approved 2026-09-21 (partial — 2 gaps filled, 4 manual-only rows carried)
