---
phase: 52
slug: lockstep-contract-round-trip-tests
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-02
---

# Phase 52 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> This is a **test-only** phase — every artifact is a *pin* on the frozen COBS framing
> contract, never a behavior change. "Validation" here = the golden-vector suites + the
> per-repo codegen drift gate + the constant-parity guard staying green in both repos.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework (firmware)** | Unity via PlatformIO `[env:native]` |
| **Framework (host)** | pytest |
| **Firmware config file** | `firestarter/platformio.ini` (`[env:native]` — positive `test_filter` allowlist) |
| **Host config file** | `firestarter_app/pyproject.toml` (pytest config) |
| **Firmware quick run** | `pio test -e native -f "*test_frame_vectors*"` |
| **Firmware full suite** | `pio test -e native` |
| **Host quick run** | `pytest tests/test_frame_vectors.py tests/test_revision_constants_parity.py -x` |
| **Host full suite** | `pytest tests/ --cov=firestarter --cov-fail-under=70` |
| **Estimated runtime** | ~10 s firmware native suite · ~15 s host suite |

---

## Sampling Rate

- **After every task commit (firmware):** Run `pio test -e native -f "*test_frame_vectors*"`
- **After every task commit (host):** Run `pytest tests/test_frame_vectors.py tests/test_revision_constants_parity.py -x`
- **After every plan wave:** Run the full suite in each repo (`pio test -e native` + `pytest tests/ --cov=firestarter --cov-fail-under=70`)
- **Before `/gsd-verify-work`:** Both full suites green AND both per-repo codegen drift gates clean (`<regen> && git diff --exit-code`)
- **Max feedback latency:** ~15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| (planner) | — | 1 | LOCK-01 | — / SAFE-01 (full-frame consume before parse — pinned indirectly, valid-only set) | host-encode → frame bytes == golden vector (leg 1, both repos) | unit | `pio test -e native -f "*test_frame_vectors*"` + `pytest tests/test_frame_vectors.py -k encode` | ❌ W0 | ⬜ pending |
| (planner) | — | 1 | LOCK-01 | — | frame bytes → decode == payload (leg 2, both repos) | unit | `pio test -e native -f "*test_frame_vectors*"` + `pytest tests/test_frame_vectors.py -k decode` | ❌ W0 | ⬜ pending |
| (planner) | — | 1 | LOCK-01 / LOCK-02 (SC4) | — | CRC8-CCITT poly 0x07 known-answer (`CRC8([0x01])==0x07`) asserted byte-for-byte | unit | `pio test -e native -f "*test_frame_vectors*"` + `pytest tests/test_frame_vectors.py -k crc8` | ❌ W0 | ⬜ pending |
| (planner) | — | 1 | LOCK-02 (SC2) | — | new `frame-vectors` catalog codegen drift gate (firmware) | CI gate | `python3 tools/catalog/codegen_vectors.py --check && git diff --exit-code` | ❌ W0 | ⬜ pending |
| (planner) | — | 1 | LOCK-02 (SC2) | — | new `frame-vectors` catalog codegen drift gate (host) | CI gate | `python3 tools/catalog/codegen_vectors.py --check && git diff --exit-code` | ❌ W0 | ⬜ pending |
| (planner) | — | 1 | LOCK-02 (SC3) | — | `CMD_FRAME_MAX` host==firmware-floor (512) parity | unit | `pytest tests/test_revision_constants_parity.py -k cmd_frame_max` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky. Exact task IDs assigned by the planner.*

---

## Wave 0 Requirements

All test/vector artifacts for this phase are new. The following must exist before the
contract assertions can run (the planner should sequence catalog + codegen + scaffold first):

**Firmware (`firestarter/`):**
- [ ] `tools/catalog/frame-vectors.toml` — vector catalog (SINGLE SOURCE; byte-identical to host copy per D-04/D-09)
- [ ] `tools/catalog/codegen_vectors.py` — vector codegen mirroring the v1.2 determinism contract (sorted, no timestamps, LF, upper-case hex) + `--check` drift gate
- [ ] `include/frame_vectors.h` (or planner-chosen name) — codegen'd PROGMEM output
- [ ] `test/native/avr/test_frame_vectors/` suite registered in BOTH `test_filter` AND `build_flags -I` (positive-allowlist gotcha — else silently skipped)

**Host (`firestarter_app/`):**
- [ ] `tools/catalog/frame-vectors.toml` — byte-identical copy of firmware's
- [ ] `tools/catalog/codegen_vectors.py` — byte-identical copy of firmware's
- [ ] `firestarter/frame_vectors.py` (or planner-chosen name) — codegen'd Python module
- [ ] `tests/test_frame_vectors.py` — pytest vector suite
- [ ] `tests/test_revision_constants_parity.py` — EXTEND existing skipif-guarded file with `CMD_FRAME_MAX`

**CI (both repos):**
- [ ] `firestarter/.github/workflows/*` — add vector codegen drift gate + native suite (if not already covered)
- [ ] `firestarter_app/.github/workflows/*` — add vector codegen drift gate + vector suite

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Cross-repo catalog byte-identity (`frame-vectors.toml` + `codegen_vectors.py` identical in both repos) | LOCK-02 / D-09 | No CI structurally diffs the two vendored copies (operator chose per-repo CI + paired-commit discipline, 2026-06-02) | At phase close, `diff firestarter/tools/catalog/frame-vectors.toml firestarter_app/tools/catalog/frame-vectors.toml` and same for `codegen_vectors.py` — both must be empty. Commit both repos in lockstep on `v1.10-serial-transport-hardening`. |
| "CI green across both repos" | LOCK-02 / D-08 | Two independent sub-repo CI pipelines; meta-repo has no CI | Confirm both `firestarter` and `firestarter_app` CI runs pass on the branch before marking the phase verified. |

*Bench / real-hardware byte-exactness is explicitly Phase 53 (XACT-01/02/03), NOT a Phase 52 verification.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (catalog + codegen + scaffolds)
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
