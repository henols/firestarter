---
phase: 69
slug: cli-command-surface-robustness-audit
status: verified
threats_open: 0
asvs_level: 1
created: 2026-06-15
---

# Phase 69 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| local DB record → display renderer | `pinouts.json` / `chip_database.json` records (list-or-scalar pin fields) cross into `_generate_pin_names_for_display`. Packaged/operator-owned data; a malformed/edge-case record (list where scalar expected) previously caused an unhandled crash. | DB pin-field values (non-sensitive) |
| CLI arg (chip name) → command handler | User-supplied chip-name string flows into `get_eprom` / `resolve_chip` (arbitrary key lookup against local JSON; no SQL/eval). Edge-case records (list-valued pin, non-supported status) must produce a clean outcome, never a traceback. | chip-name string (untrusted key) |
| CI gate → merge | mypy watermark + characterization snapshot gates prevent the denial-of-display crash class from re-entering. A false watermark or stale snapshot would block merges spuriously or silently re-pin broken behavior. | gate thresholds / golden snapshots |

No network, auth, secrets, session, or crypto surface in this phase (read-only host display/CLI code + test-tooling realignment). Per 69-RESEARCH Security Domain, only V5 Input Validation applies, minimally.

---

## Threat Register

| Threat ID | Category | Component | Disposition | Mitigation | Status |
|-----------|----------|-----------|-------------|------------|--------|
| T-69-01 | Denial of Service (denial-of-display) | `ic_layout._generate_pin_names_for_display` | mitigate | Scalar-extract list-valued pin fields — `rw[0] if isinstance(rw, list) else rw` at all comparison/index sites (`ic_layout.py:394,399,405,410`). Regression-pinned by `tests/test_ic_layout.py` (W27C512, AT28C256, 2732, M2716). Commit a1b8a31. | closed |
| T-69-02 | Tampering | local `pinouts.json` / `chip_database.json` | accept | Packaged-with-app / operator-owned local data; no remote write path. Crash-safety delivered via T-69-01. | closed |
| T-69-03 | Denial of Service (denial-of-display) | every CLI command surface (info/list/search/read/write/verify/blank/erase/id/dev) | mitigate | Smoke audit asserts each surface reaches a clean outcome (success / typed error / support_status refusal), never a traceback. `tests/test_cli_handlers.py`: `test_info_2732_list_valued_pin_no_crash`, `test_info_vpp_exceeds_max_no_crash` (M2716), `test_info_adapter_required_no_crash` (AT28C16), `test_info_protocol_not_implemented_no_crash` (X88C64P), `test_read_non_supported_typed_refusal`, `test_read_protocol_not_implemented_typed_refusal`. REAL `EpromConsolePresenter(db)` injected (avoids mock-masking). Commits 4565342, c3631bd. | closed |
| T-69-04 | Tampering | non-supported chip → hardware op path | accept | Phase 66 `ChipNotImplementedError` guard at `chip_resolver.py:55-57` refuses `support_status != "supported"` before any wire dict; CLI-level typed refusal (exit 1, no traceback) pinned by T-69-03 tests, incl. protocol-not-implemented X88C64P read path. | closed |
| T-69-05 | Repudiation / gate integrity | `tools/check_mypy_watermark.py` + `test_characterization.ambr` | mitigate | Snapshot regenerated via `--snapshot-update`: `test_info_known_chip_stderr` snapshot is empty `''` (no traceback pinned), `test_characterization.py:253` asserts `rc == 0`. Watermark set to honest measured floor (`pyproject.toml:115` `# mypy_error_watermark = 29`). Commit a8fb281. | closed |
| T-69-06 | Tampering | gate loosening to pass CI | accept/avoid | Commit a8fb281 changes only the watermark comment line (26→29). No mypy config flags modified (`disallow_untyped_defs`, `follow_imports`, `disable_error_code` unchanged); no new `# type: ignore` added to phase-touched files. | closed |
| T-69-SC | Tampering | npm/pip/cargo installs | accept | No new packages installed this phase (69-RESEARCH Package Legitimacy Audit: N/A). pyproject.toml diff across all phase-69 commits shows no dependency additions. | closed |

*Status: open · closed*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-69-01 | T-69-02 | Local packaged/operator-owned DB JSON; no remote write path. Hardened to crash-safety only (T-69-01). | Henrik Olsson | 2026-06-15 |
| AR-69-02 | T-69-04 | Non-supported chips refused by Phase 66 `ChipNotImplementedError` guard before any wire dict; CLI degrades to clean exit 1. | Henrik Olsson | 2026-06-15 |
| AR-69-03 | T-69-06 | Watermark set to measured floor only; no mypy config loosening or `# type: ignore` additions permitted. | Henrik Olsson | 2026-06-15 |
| AR-69-SC | T-69-SC | No new package installs this phase. | Henrik Olsson | 2026-06-15 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-06-15 | 7 | 7 | 0 | gsd-security-auditor (sonnet) |
| 2026-06-15 | 7 | 7 | 0 | /gsd-secure-phase re-verify (mitigations spot-checked in code: ic_layout.py:394-410, chip_resolver.py:54-57, pyproject.toml:115, 6 CLI smoke tests) |
| 2026-06-15 | 7 | 7 | 0 | /gsd-secure-phase re-verify #2 — register matches plan-time STRIDE (3 PLAN `<threat_model>` blocks). All mitigations re-confirmed present: ic_layout list-scalar extract (396-412) + regression tests (W27C512/AT28C256/2732/M2716); chip_resolver `ChipNotImplementedError` guard (54-57); watermark=29 (pyproject:115) + characterization `rc == 0` asserts; 6 CLI smoke tests. No drift; threats_open: 0. |
| 2026-06-15 | 7 | 7 | 0 | /gsd-secure-phase re-verify #3 — register origin reconfirmed (3 PLAN `<threat_model>` blocks → authored at plan time; short-circuit applies). Live gates re-run (py3.12.13): `pytest test_ic_layout.py test_cli_handlers.py test_characterization.py` PASS (106 tests + 29 snapshots). Mitigation sites confirmed present: ic_layout list-scalar extract (`ic_layout.py:394,399,405,410`); chip_resolver `ChipNotImplementedError` guard (`chip_resolver.py:55-57`); watermark=29 (`pyproject.toml:115`). No drift; threats_open: 0. |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-06-15
