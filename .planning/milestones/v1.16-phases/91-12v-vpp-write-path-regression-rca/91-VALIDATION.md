---
phase: 91
slug: 12v-vpp-write-path-regression-rca
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-26
---

# Phase 91 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> This phase's deliverable is a **root-cause attribution + a working SST39SF040 write
> path proven on silicon**, not a large code change. The firmware-causality verdict is
> bench-only (real-silicon SHA gate); native Unity can only prove the *bus sequence* is
> unchanged, not that the rail/timing on real hardware succeeds — the irreducible HIL gap.
> The Validation Architecture section of 91-RESEARCH.md is the authoritative source.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework (firmware)** | PlatformIO Unity, `[env:native]` (host-side, no board) — `firestarter/platformio.ini` |
| **Framework (host)** | pytest (`firestarter_app`, `pip install -e '.[test]'`; validate against CI **py3.11**, not devcontainer py3.12) |
| **Config file** | `firestarter/platformio.ini` + `firestarter_app/pyproject.toml` |
| **Quick run command** | `pio test -e native -f "*test_val_flash3*"` (0x06 bus sequence) |
| **Full suite command** | `pio test -e native` (all native firmware suites) + host `pytest` + `check_ledger.py` |
| **Silicon oracle** | Leonardo on /dev/ttyACM0 + RURP Rev 2.0 + seated SST39SF040; SHA byte-identity vs v1.15 baseline `a38b13b4…` (image B) |
| **Estimated runtime** | ~30 s native unit; bench write-cycle ~3–6 min/op (flash3 is a slow path, ~177–240 s/write), operator-paced segments deferred |

---

## Sampling Rate

- **After every task commit:** Run the relevant native suite
  (`pio test -e native -f "*test_val_flash3*"` and/or `*test_val_eprom*`) — sub-30 s, no board.
- **After every plan wave:** Run full `pio test -e native` + host `pytest` + `check_ledger.py`.
- **Before `/gsd-verify-work`:** All native + host gates green; the SST39SF040 bench
  write+verify is byte-identical to `a38b13b4…`; `check_ledger.py` RC=0.
- **Max feedback latency:** ~30 s for unit gates; bench latency is the slow-path write
  time (out of the automated loop).

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 91-01-01 | 01 | 1 | RCA-91 | — | N/A | host analysis | `python3` byte-compare of post-fail capture vs image B | ❌ W0 (forensic) | ⬜ pending |
| 91-01-02 | 01 | 1 | RCA-91 | — | flash3 0x06 write bus sequence unchanged | unit (native) | `pio test -e native -f "*test_val_flash3*"` | ✅ `test/native/avr/test_val_flash3/` | ⬜ pending |
| 91-01-03 | 01 | 1 | RCA-91 | — | eprom 0x07 write+chip-id sequence unchanged | unit (native) | `pio test -e native -f "*test_val_eprom*"` | ✅ `test/native/avr/test_val_eprom/` | ⬜ pending |
| 91-02-01 | 02 | 2 | RCA-91 | T-91-VPP | VPP guard unmodified during A/B | bench A/B (manual, silicon) | `firestarter write -b SST39SF040 …` under each fw | ❌ manual — BENCH-LOG | ⬜ pending |
| 91-03-01 | 03 | 3 | FIX-91 | T-91-VPP | SST39SF040 write+verify == v1.15 SHA | bench gate (silicon) | `firestarter verify SST39SF040 img_B` + `dev consistency-check --runs 3` | ❌ manual — silicon | ⬜ pending |
| 91-03-02 | 03 | 3 | FIX-91 | — | 0x06/0x07 ledger rows dispositioned + checker green | host | `python3 .planning/v1.16/ledger/check_ledger.py` | ✅ `check_ledger.py` | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] One-off forensic script: byte-compare `bench/SST39SF040-wcB/run_01.bin` (`ebca6266…`,
      read back from the chip) vs `SST39SF040_img_B.bin` — is the wrong content a partial
      program, a transform, or noise? Covers RCA-91 Open Q1. No test file today.
- [ ] If a host code/DB fix lands: a pytest assertion pinning 0x06/0x07 wire-param parity
      (currently proven ad-hoc in research) — covers FIX-91.
- [ ] No framework install needed — native Unity + pytest infra already present (Phase 88
      golden traces + Phase 90 `check_ledger.py`).

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| b10-vs-recompose firmware attribution | RCA-91 | Requires real silicon under each firmware build; no automation possible without a board | Build+flash `firestarter@a1953c2` (b10) via a `/tmp/fs-b10` worktree (disambiguate by flash byte count: recompose 25136 B vs b10 25654 B); re-run the `write -b` cycle on SST39SF040; record outcome in BENCH-LOG |
| SST39SF040 write+verify byte-identical to v1.15 | FIX-91 | Silicon SHA-identity gate (HIL); the irreducible truth oracle | `write -b A`→`verify A`→`write -b B`→`verify B`→`dev consistency-check --runs 3`; final SHA must == `a38b13b4…` |
| W27C512 0x07 bench re-validation | FIX-91 | **DEFERRED** — requires a chip swap, operator-only | Leave a ready-to-run operator bench checklist; do not attempt this session |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or are explicitly bench/manual with a recorded reason
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify (HIL bench gates are the documented exception)
- [ ] Wave 0 covers the forensic + parity-pin gaps
- [ ] No watch-mode flags
- [ ] Feedback latency < 30 s for unit gates
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
