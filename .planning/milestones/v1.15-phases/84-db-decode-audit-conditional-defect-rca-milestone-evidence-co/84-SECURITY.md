---
phase: 84-db-decode-audit-conditional-defect-rca-milestone-evidence-co
audited: 2026-06-25
auditor: gsd-security-auditor (claude-sonnet-4-6)
asvs_level: 1
block_on: high
threats_total: 20
threats_closed: 20
threats_open: 0
result: SECURED
---

# Phase 84 Security Audit — SECURED

**Phase:** 84 — DB Decode Audit + Conditional Defect RCA + Milestone Evidence Consolidation
**Threats Closed:** 20/20
**ASVS Level:** 1 (default)
**Result:** SECURED — threats_open: 0

---

## Threat Verification

| Threat ID | Category | Disposition | Status | Evidence |
|-----------|----------|-------------|--------|----------|
| T-84-01 | Tampering / Elevation (over-voltage) | mitigate | CLOSED | `firestarter/src/proms/eprom.cpp:294` — guard is `CMD_READ \|\| CMD_BLANK_CHECK` only; `eprom_check_vpp` at line 297 still executes for all other commands. Negative assertions at `test_configure_memory.cpp:288,300,311` (write/erase/chip-id still gate VPP). |
| T-84-02 | Denial (chip-id break) | accept-by-design | CLOSED | `eprom.cpp:294` guard explicitly excludes `CMD_CHECK_CHIP_ID`; `grep -c "CMD_CHECK_CHIP_ID" eprom.cpp` returns 1 (dispatch table only, not in skip condition). Negative test at `test_configure_memory.cpp:311` (`test_eprom_check_chip_id_still_runs_vpp_check`) confirms 12V-on-A9 path intact. Accept disposition is documented: chip-id requires 12V — correctly excluded. |
| T-84-03 | Tampering (wrong branch) | mitigate | CLOSED | `git -C firestarter rev-parse --abbrev-ref HEAD` → `v1.15-bench-validation-of-operator-inventory`. Meta committed gitlink (`git ls-tree HEAD firestarter`) → `a33513f` (pinned, not bumped this phase). Firmware delta lands on v1.15 branch off beta HEAD `a1953c2`, not on beta. |
| T-84-04 | Tampering (over-broad short-circuit) | mitigate | CLOSED | `firestarter_app/firestarter/eprom_operations.py:1543` — `_SRAM_PROTO_IDS = frozenset({0x0E, 0x27, 0x28, 0x29})`; guard at line 1556 fires ONLY for `etype in ("SRAM","FRAM") or proto in _SRAM_PROTO_IDS`. Negative control at `test_eprom_operations.py:977` (`test_eeprom_blank_check_still_reaches_setup`) asserts W27C512 (EEPROM / 0x07) still reaches `_setup_operation`. |
| T-84-05 | Info disclosure / wire change | accept-by-design (prevented) | CLOSED | `git -C firestarter_app log --since=2026-06-24 -- firestarter/messages.py` → empty (no messages.py commits this phase). Firmware commits limited to `eprom.cpp` and test files (cb947c7, c480d3f only). Wire protocol unchanged. Accept disposition: host-only fix; no new message constant or firmware protocol change introduced. |
| T-84-06 | Repudiation (masked CI gate) | mitigate | CLOSED | `firestarter_app/.github/workflows/ci.yml:60,63` gates `ruff check firestarter/ tests/` and `ruff format --check firestarter/ tests/`. Phase-84 SUMMARYs (84-02, 84-03, 84-06) each ran CI-scoped ruff and flagged (not masked) pre-existing `tools/` I001 findings. EXIT 0 confirmed for in-scope targets. |
| T-84-07 | Tampering (data-integrity FLAG_CAN_ERASE) | mitigate | CLOSED | `test_database_conversion.py:205` — `test_sst39sf040_flag_can_erase_unchanged` asserts SST39SF040 carries FLAG_CAN_ERASE. `test_database_conversion.py:218` — `test_fm1608_flag_can_erase_off` asserts FM1608 does NOT. SST39SF040 kept `Flash/EEPROM` (sst-keep decision, D-40); no CAN_ERASE regression. |
| T-84-08 | Tampering (over-voltage via relabel) | mitigate | CLOSED | `check_dispatch.py` exits 0 (734 supported, 0 violations — confirmed by 84-03 and 84-06 SUMMARYs). `diff_db.py:268` — `_PHASE84_RELABEL_PART_NUMBERS = frozenset({"FM1608"})` scopes relabel; no algorithm/pinout/vpp delta for any other chip. |
| T-84-09 | Info disclosure (misleading VPP display) | mitigate | CLOSED | `firestarter_app/firestarter/ic_layout.py:580` — gate is `etype not in {"SRAM", "FRAM"}`. `firestarter_app/firestarter/eprom_info.py:396` — `if _etype not in {"SRAM", "FRAM"} and _vpp_mv > 0`. FM1608 VPP row hidden after relabel (confirmed by `test_ic_layout.py::test_fm1608_vpp_row_hidden_after_relabel`). |
| T-84-10 | Tampering (codegen drift via hand-edit) | mitigate | CLOSED | `firestarter_app/tools/build_db.py:658` — `_PHASE84_RELABEL = {"FM1608": "FRAM"}` override in codegen pipeline (not hand-edit). `diff_db.py` guard preserved: exit 0 with 15 explained changes; no re-baseline. FM1608 `electrical.type = "FRAM"` confirmed in `chip_database.json`. |
| T-84-11 | Repudiation (overstated REWR traceability) | mitigate | CLOSED | `.planning/v1.15/DECODE-AUDIT.md` — 18 occurrences of EVIDENCE/REWR/D-41 cross-references. REWR-01/02/04 annotated in REQUIREMENTS.md definition + traceability rows with silicon FAIL/deferral dispositions (84-04 SUMMARY, commit 1e46e6c). |
| T-84-12 | Repudiation (dropped D-40 STOP observation) | mitigate | CLOSED | `.planning/v1.15/DECODE-AUDIT.md:138` — "SST39SF040 = sst-keep (D-40 STOPPED — explicit observation)" section present. Line 142 contains the verbatim D-40 observation text. Not omitted; recorded in Dispositions Part 2(iii). |
| T-84-13 | Elevation (irreversible consume of 2516) | mitigate | CLOSED | `.planning/v1.15/DECODE-AUDIT.md:100` — "No write / no preserve-dump (D-21 confirmed)". REQUIREMENTS.md GRAD-03 row states "DEFERRED best-effort (D-22)". 84-05 SUMMARY confirms: "No write / no preserve-dump (D-21). GRAD-03/FUT-03 DEFERRED best-effort (D-22)." |
| T-84-14 | Tampering (over-voltage post-VPP-skip re-bench) | accept (verified) | CLOSED | VPP-skip guard at `eprom.cpp:294` gates ONLY `CMD_READ/CMD_BLANK_CHECK`; write/erase paths reach `eprom_check_vpp` unchanged (line 297). Re-bench write ops (AM27C020 0x08, W29C040 flash4) ran through normal VPP-gated paths. Accept disposition: VPP safety for write/erase operations is verified by negative assertions in T-84-01 mitigation. |
| T-84-15 | Spoofing (untrusted oracle) | mitigate | CLOSED | `.planning/v1.15/bench/EVIDENCE.md` SAFE-01 gates present for Phase 84: controller=leonardo, Rev 2.0 operator-confirmed, r1=270000 live readback (lines 5-8 of EVIDENCE.md header + Phase 84 SAFE-01 section in 84-05 SUMMARY). |
| T-84-16 | Repudiation (lost prior evidence rows) | mitigate | CLOSED | `.planning/v1.15/bench/EVIDENCE.md` — `grep -c "Phase 81\|Phase 82\|Phase 83"` returns 32 occurrences; prior rows preserved verbatim. EVIDENCE.json `phase84` key added; earlier phase entries intact (append-only pattern confirmed by 84-05 SUMMARY). |
| T-84-17 | Repudiation (deferral-as-gap) | mitigate | CLOSED | REQUIREMENTS.md:40 — GRAD-03 "DEFERRED best-effort (D-22)"; line 102 — FUT-03 "OPEN best-effort (D-22)"; line 49 — FIX-01 "CLOSED per D-43". DECODE-AUDIT.md Part 2(v) and Part 4 explicitly flag all deferrals as "intentional — NOT a failure or gap." |
| T-84-18 | Tampering (masked gate) | mitigate | CLOSED | `check_dispatch.py:475` — `sys.exit(1)` on violation. `diff_db.py:415,570` — `sys.exit(2)` and `sys.exit(1)` on unexplained changes. All Phase-84 gate runs recorded with exit codes in SUMMARYs (84-03 Task 4, 84-06 Task 3). Out-of-scope `tools/` ruff findings flagged (not masked) in every plan SUMMARY that ran ruff. |
| T-84-19 | Elevation (premature milestone close) | accept-by-design (prevented) | CLOSED | No `v1.15` tag exists in meta repo (`git tag \| grep v1.15` returns empty). Meta log shows no "milestone" or "complete" commit for v1.15. REQUIREMENTS.md + DECODE-AUDIT.md both state "milestone close + firmware beta-cut operator-gated (D-12/D-43); not performed in this phase." |
| T-84-SC | Tampering (package installs) | n/a | CLOSED | Firmware commits limited to eprom.cpp + test files; no `pio lib install`. App commits limited to source + test files; no `pip install <new>`. Phase explicitly bound by D-52 (reuse-first). |

---

## Unregistered Threat Flags

All SUMMARY.md `## Threat Flags` sections in Plans 84-01 through 84-06 report: **None** — no new network endpoints, auth paths, file access patterns, or schema changes at trust boundaries introduced by any plan.

No unregistered flags.

---

## Accepted Risks Log

The following threats are accepted by design and do not require implementation mitigations:

| Threat ID | Acceptance Basis |
|-----------|-----------------|
| T-84-02 | CMD_CHECK_CHIP_ID requires 12V on A9 for chip identification — correctly excluded from VPP-skip guard; accepting this means chip-id operations remain VPP-gated as intended. Risk: none (desired behavior preserved). |
| T-84-05 | Host-only phase by design — no messages.py or firmware wire-protocol change was in scope. Wire protocol parity preserved by the no-new-constant constraint (A4 confirmed). |
| T-84-14 | VPP safety on write/erase operations is an existing invariant; re-bench write operations ran through the unchanged VPP-gated path. The VPP-skip fix does not affect any write/erase/chip-id path. |
| T-84-19 | Milestone close is operator-gated by standing policy (D-12); this phase delivers only the readiness documentation. No code or tag action was taken. |

---

*Audit completed: 2026-06-25*
*Auditor: gsd-security-auditor (claude-sonnet-4-6)*
*Phase verifier score: 3/3 (human_needed for two operator-judgment deferrals — not security gaps)*
