---
phase: 02
slug: naming-cleanup-wire-key-minipro-references
status: planned
nyquist_compliant: true
wave_0_complete: true
created: 2026-05-12
updated: 2026-05-12
---

# Phase 02 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `02-RESEARCH.md` §"Validation Architecture". Task IDs filled in
> by gsd-planner after the 3-plan split was finalized.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework (firmware)** | PlatformIO + Unity (`pio test -e native`) |
| **Framework (Python)** | None established — `check_dispatch.py` (stdlib + post-augment `firestarter` package import) static scan + CLI smoke is the contract |
| **Config file (firmware)** | `firestarter/platformio.ini` `[env:native]` |
| **Config file (Python)** | — |
| **Quick run command** | `cd firestarter_app && python tools/check_dispatch.py` (~1s; 743-chip iteration) |
| **Full suite command** | `cd firestarter_app && python tools/check_dispatch.py && firestarter --help && firestarter info W27C512 && firestarter info --adapter W27C512` plus `cd firestarter && pio test -e native` |
| **Estimated runtime** | Python ≈3s; firmware native ≈15-20s |

---

## Sampling Rate

- **After every task commit:** Run `cd firestarter_app && python tools/check_dispatch.py` (Python-side changes) OR `cd firestarter && pio test -e native` (firmware-side changes).
- **After every plan wave:** Run the full Python smoke + firmware native test suite.
- **Before `/gsd-verify-work`:** Full suite must be green AND all three CLAUDE.md files manually reviewed for consistency.
- **Max feedback latency:** ~25s (Python ≈3s + firmware native ≈20s).

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 01 | 1 | WIRE-01 (firmware parse) | T-02-01 (stale-wire over-voltage) | Firmware parses `"vpp_mv"` into `handle->vpp_mv`; three-site flip lands in one commit; SAF-04 traps stale-key partial upgrade | grep + compile | `cd firestarter && grep -nv '^[[:space:]]*//' src/json_parser.c \| grep -c key_vpp_mv` >= 2 AND `grep -c '"vpp"' src/json_parser.c` == 0; optional `pio run -e uno && pio run -e leonardo` | ✅ existing | ⬜ pending |
| 02-01-02 | 01 | 1 | WIRE-01 (Python emit + doc) | T-02-01 | Python emits ONLY `"vpp_mv"`; CLAUDE.md wire example shows only `"vpp_mv"` | grep | `cd firestarter_app && grep -nE '"vpp_mv":\s*vpp_mv' firestarter/database.py \| grep ':518:'` AND `! grep -F '"vpp": 12000' firestarter_app/CLAUDE.md` | ✅ existing | ⬜ pending |
| 02-02-01 | 02 | 2 | CLEAN-01 (file rename + 7 callsites) | — | Zero remaining references to `minipro_complete_db.json`; blame preserved via `git mv` | grep + git history | `! grep -rn 'minipro_complete_db' firestarter_app/ firestarter/ CLAUDE.md` AND `cd firestarter_app && git log --follow --format='%H' -- firestarter/data/chip_database.json \| wc -l` >= 2 | ✅ existing | ⬜ pending |
| 02-02-02 | 02 | 2 | WIRE-01 internal (`vpp_volts` rename + 2 consumers) | — | `_map_data()` writes `"vpp_volts"`; consumers in `eprom_info.py:271` + `ic_layout.py:513` updated; upstream-schema read at `:373-381` PRESERVED | grep | `cd firestarter_app && grep -nE '"vpp_volts":\s*vpp,' firestarter/database.py \| grep ':417:'` AND `grep -nE "'vpp_volts'" firestarter/eprom_info.py firestarter/ic_layout.py` >= 2 hits AND `grep -nE 'electrical\.get\("vpp",\s*"0"\)' firestarter/database.py` STILL hits near `:375` | ✅ existing | ⬜ pending |
| 02-02-03 | 02 | 2 | CLEAN-01 (package-data alignment) | — | `pyproject.toml`+`MANIFEST.in` reference the actual shipping files including `chip_database.json`; wheel build succeeds | smoke | `cd firestarter_app && pip install -e . && firestarter info W27C512` exit 0 | ✅ existing | ⬜ pending |
| 02-03-01 | 03 | 3 | CLEAN-02 (Python comment scrub) | — | Zero `minipro` mentions in `database.py` + `check_dispatch.py`; `MINIPRO_XML_URL` survives at `build_db.py:10`; `:23` comment softened | grep | `! grep -F minipro firestarter_app/firestarter/database.py` AND `! grep -F minipro firestarter_app/tools/check_dispatch.py` AND `grep -F MINIPRO_XML_URL firestarter_app/tools/build_db.py` == 1 hit at `:10` | ✅ existing | ⬜ pending |
| 02-03-02 | 03 | 3 | WIRE-02 (regression scan, augmented) | T-02-01 | `check_dispatch.py` asserts `"vpp_mv" in wire ∧ "vpp" ∉ wire` for all 743 chips via `db.convert_to_programmer` round-trip; exits 0 with `0 wire-key regressions` in PASS line | static scan + dynamic | `cd firestarter_app && python tools/check_dispatch.py` exit 0 AND stdout matches `^PASS:` AND contains `0 wire-key regressions` | ✅ existing (augmented in this task) | ⬜ pending |
| 02-03-03 | 03 | 3 | CLEAN-02 (doc-side minipro reduction) + SC#5 CLI smoke | — | `firestarter_app/CLAUDE.md` has exactly 1 attribution line at `:69`; `firestarter/CLAUDE.md` has 0; meta `CLAUDE.md` has 0; `firestarter --help` + `firestarter info W27C512` + `firestarter info --adapter W27C512` all exit 0 | grep + CLI smoke | `cd firestarter_app && grep -cF minipro CLAUDE.md` == 1 AND `grep -cF minipro firestarter/CLAUDE.md` == 0 AND `grep -cF minipro CLAUDE.md` == 0 AND all four CLI smoke invocations exit 0 with no `FileNotFoundError` / `stale-path` warnings | ✅ existing | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

**Existing infrastructure covers all phase requirements.** Phase 2 reuses:

- `firestarter_app/tools/check_dispatch.py` (regression scanner — augmented in Task 02-03-02 with `wire_regressions` failure list inside the existing 743-chip iteration; no new test file).
- `firestarter/test/native/avr/test_dispatch/` (PlatformIO native dispatch tests — already cover the post-parse `configure_*` handlers).
- `firestarter` CLI (smoke target — already installed via `pip install -e .` in the dev env; Plan 02-02 fixes the packaging metadata so the renamed DB ships under built wheels too).

No new test framework, fixtures, or stub files needed. `wave_0_complete: true`.

**Identified gap (DEFERRED):** Phase 2 leaves a pre-existing v1.0 gap intact — `json_parser.c` has no native PlatformIO test. The atomic-flip three-line edit is small enough that careful code review + `check_dispatch.py` Shape A round-trip + Phase 4 hardware verification are sufficient. Native parser tests are tracked as a v1.2 hardening candidate (see RESEARCH.md §"Wave 0 Gaps"); not in Phase 2 scope.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Three-CLAUDE.md consistency (meta + 2 sub-repo) | CLEAN-01 / CLEAN-02 | No automated tool checks cross-doc semantic consistency (filename + attribution line counts can be greped, but reading flow + wording cannot) | At phase close, open meta `CLAUDE.md`, `firestarter_app/CLAUDE.md`, `firestarter/CLAUDE.md` side-by-side; confirm: (1) all three use `chip_database.json`; (2) `firestarter_app/CLAUDE.md` has exactly one attribution line at `:69`; (3) `firestarter/CLAUDE.md` has zero `minipro` mentions; (4) wire-JSON example in `firestarter_app/CLAUDE.md` shows only `"vpp_mv"`. |
| Real hardware end-to-end (Uno + Leonardo with RURP shield) | WIRE-01 + CLEAN-01 | Requires Arduino board + RURP shield — not available in devcontainer | **Deferred to Phase 4 / HW-* tasks** per Phase 2 CONTEXT.md "Out of scope". `check_dispatch.py` simulator paths cover the static contract; Phase 4 owns physical-write validation. |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies — every task in the per-task map above has at least one automated command.
- [x] Sampling continuity: no 3 consecutive tasks without automated verify — every task carries its own grep / smoke / static-scan command.
- [x] Wave 0 covers all MISSING references — none missing; existing infra covers everything.
- [x] No watch-mode flags — all commands are one-shot.
- [x] Feedback latency < 30s — Python scan ≈3s; firmware native ≈20s.
- [x] `nyquist_compliant: true` set in frontmatter.

**Approval:** ready for execution (gsd-plan-checker to confirm).
