---
phase: 53
slug: byte-exact-bench-verification-hardware-gated
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-02
---

# Phase 53 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Software parts (harness code, hooks, ring-fence compliance) are automated; bench parts are operator-witnessed and tracked under Manual-Only Verifications.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (project version; install via `pip install -e '.[test]'` in `firestarter_app/`) |
| **Config file** | `firestarter_app/pyproject.toml` |
| **Quick run command** | `pytest tests/ -x -q --no-header` |
| **Full suite command** | `pytest tests/ --cov=firestarter --cov-fail-under=70` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/ -x -q --no-header`
- **After every plan wave:** Run `pytest tests/ --cov=firestarter --cov-fail-under=70`
- **Before `/gsd-verify-work`:** Full suite must be green AND `.planning/v1.10/bench-verification/SUMMARY.md` exists
- **Max feedback latency:** ~30 seconds (software); bench legs are operator-gated (see Manual-Only)

---

## Per-Task Verification Map

> Filled in by the planner per the Validation Architecture split in 53-RESEARCH.md.
> Software-verifiable rows get `<automated>` commands; hardware-gated rows route to Manual-Only Verifications below.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 53-XX-XX | XX | 0 | XACT-01 | — | write_cycle_eprom returns 0/1/2 correctly | unit | `pytest tests/test_eprom_operations.py -k write_cycle -x` | ❌ W0 | ⬜ pending |
| 53-XX-XX | XX | 0 | XACT-02 | — | outgoing fault hook fires when set, no-op when None | unit | `pytest tests/test_serial_comm.py -k fault_inject -x` | ❌ W0 | ⬜ pending |
| 53-XX-XX | XX | 0 | XACT-02 | — | `_read_and_parse_lines` body unchanged (ring-fence) | code-review/lint | `git diff HEAD -- firestarter_app/firestarter/serial_comm.py` | n/a | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_eprom_operations.py` — `test_write_cycle_eprom_pass` / `_mismatch` / `_hw_error` (XACT-01 software part)
- [ ] `tests/test_serial_comm.py` — `test_fault_inject_outgoing_none` / `_corrupt_crc8` / `_drop_delimiter` / `_incoming_subclass` (XACT-02 software part)
- [ ] `tests/test_cli_handlers.py` — invocation smoke tests for the new `dev` subcommand(s) (if subcommand approach chosen)

---

## Manual-Only Verifications

> Hardware-gated, operator-witnessed. No automated command — bench-only. Each requires: chip OUT before sideload, per-port `controller:` identity verification, operator-confirmed silkscreen shield rev (Rev 2.0 target per D-07).

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| N=5 byte-identical framed reads on clean Uno (512 B) + Leonardo (1024 B) | XACT-01 / SC1 | Requires real bench hardware + RURP shield + operator authorization | `dev consistency-check W27C512 --runs 5 --output-dir .planning/v1.10/bench-verification/...`; all run SHA-256 identical; strong-form: match GATE-1.8d baseline if original chip present |
| N=5 write→read-back→compare cycles, read-back SHA == source SHA | XACT-01 / SC1 | Bench hardware; destructive write to real chip | `dev write-cycle W27C512 --runs 5 --source <image>`; independent host-side SHA compare (not firmware verify) |
| Corrupted host→fw command frame → sub-second clean error + next frame byte-exact | XACT-02 / SC2 | On-wire fault injection against firmware decoder | `dev fault-inject --direction outgoing` (corrupt CRC8 byte + drop 0x00 delimiter); assert immediate error (NOT 2 s cascade) + next transfer byte-exact |
| Mutated fw→host frame → host decoder resync + next frame byte-exact | XACT-02 / SC2 | Bench receive-path hook | `dev fault-inject --direction incoming`; same assertion |
| uno328pb re-test N=5 with timeout-retry logging + structured exoneration verdict | XACT-03 / SC3 | Unstable hardware; failure-shape capture is the deliverable | `dev consistency-check W27C512 --runs 5` on uno328pb; never abort on timeout (verdict 2, not 1); write D-10 verdict block citing v1.6-EVIDENCE.md before-shape |
| Milestone evidence artifact complete | SC4 | Composed from operator-witnessed bench output | `ls .planning/v1.10/bench-verification/` confirms per-run binaries, fault-injection log, uno328pb before/after, operator attestation, SUMMARY.md |

---

## Validation Sign-Off

- [ ] All software tasks have `<automated>` verify or Wave 0 dependencies
- [ ] All hardware-gated tasks marked `autonomous: false` and routed to Manual-Only
- [ ] Sampling continuity: no 3 consecutive software tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s (software)
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
