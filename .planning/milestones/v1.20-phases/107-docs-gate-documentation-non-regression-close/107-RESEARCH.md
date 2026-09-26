# Phase 107: DOCS + GATE — Documentation & Non-Regression Close - Research

**Researched:** 2026-07-02
**Domain:** Documentation scrub + non-regression gate re-verification (docs/close phase, zero new behavior)
**Confidence:** HIGH (all findings verified against the actual repo state on `v1.20-protocol-only-dispatch`)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Record the breaking wire-contract change (`type` field removed) and the "every chip entry needs a usable `algorithm`" requirement as a **dedicated section in both sub-repo READMEs** (`firestarter/README.md`, `firestarter_app/README.md`), plus a note in the agent-facing `firestarter/CLAUDE.md` / `firestarter_app/CLAUDE.md`. **Do NOT create new CHANGELOG.md files** — neither sub-repo has one; README is the established public-facing surface.
- **D-02:** The `type`/`mem_type` scrub is confined to **`firestarter/CLAUDE.md`** (dispatch narrative ~lines 21–62 describing steps 7–11 + the legacy `type` wire-field bullet ~line 90) and **`firestarter/doc/PROTOCOLS.md`**. `firestarter/README.md`, `firestarter_app/CLAUDE.md`, and `firestarter_app/README.md` are verify-only for wire `type`/`mem_type` refs (they still receive the D-01 breaking-change note, but need no scrub). **[RESEARCH CORRECTION — see Open Question #1: the CONTEXT's "grep-confirmed clean" claim for the host docs is NOT accurate; `firestarter_app/CLAUDE.md` still contains a live `"type": 1` wire example. Planner must resolve.]**
- **D-03:** In `firestarter/CLAUDE.md`, delete steps 7–11 and rewrite the dispatch narrative so `protocol == 0` (and any unrecognized arm) fail-closes to `configure_not_implemented()` (0xBB) — no `mem_type` fallback described. **Preserve the v1.16 `electrical.type` STRING semantics** (INV-08/INV-09 and the `electrical.type == "EEPROM"` derivations in PROTOCOLS.md are OUT of scope — do not touch them; only the *numeric* `mem_type` / `type`-wire references go).
- **D-04:** If ANY non-regression gate surfaces a **real regression** (`diff_db.py` value change on a real chip, `check_dispatch.py` violation, golden-trace / dispatch-mirror mismatch, or a failing native/host test caused by Phase 105/106), **STOP and surface it as a blocking finding.** Do NOT auto-fix, silence, or regenerate baselines.
- **D-05:** Golden register traces + the dispatch-mirror guard are **RUN as-is for re-verification only — never regenerated** in this phase.

### Claude's Discretion
- Exact prose of doc edits and section headings.
- Ordering of the gate runs.
- Whether to leave the **meta-repo** `/workspaces/CLAUDE.md` untouched — default is untouched (touch only if a dangling `mem_type` reference is discovered there; none was found — see Environment/verify).

### Deferred Ideas (OUT OF SCOPE)
- **Meta-repo `/workspaces/CLAUDE.md` scrub** — out of scope (roadmap names only sub-repo docs).
- **LEGACY-01 / LEGACY-02 (v2):** `FLAG_VPE_AS_VPP (0x10)` removal and `EPROM_LEGACY` naming cleanup — deferred to v2.
- **Skip VPP checks when VPP unused** — firmware behavior change; own phase.
- **avrdude MCU-detection fallback** — host recovery feature; own phase.
- **COBS decoder frame-level deadline (WR-01)** — firmware transport change; own phase.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DOC-01 | Firmware `CLAUDE.md` dispatch section (steps 7–11 removed), `PROTOCOLS.md`, and JSON wire-field docs drop `type`/`mem_type`; breaking change + "every entry needs `algorithm`" recorded in sub-repo READMEs | Exact edit sites enumerated below (`## Doc Edit Sites`). Breaking-change record has an existing template (`## Breaking Changes (v1.10)` in both READMEs). |
| GATE-01 | Golden traces + dispatch-mirror stay green; `check_dispatch.py` 0 violations; `diff_db.py` no real-chip value change | All four gates RUN GREEN this session (`## Gate Command Inventory`). "Golden traces" naming is imprecise — resolved below. |
| GATE-02 | Full native (`pio test -e native`) + host (`pytest`) pass; dual-repo constants parity; py3.11-target CI clean (ruff/ruff-format/mypy) | Native 80/80 GREEN; host pytest 710 pass / **1 pre-existing failure** + pre-existing ruff/format dirt (all in files untouched by v1.20). Central D-04 disposition — see `## Common Pitfalls` #1. |
| SAFE-01 | Over-voltage stays blocked; every dispatchable DB chip routes to identical handler via `protocol` alone | Covered by EXISTING gates (native dispatch tests + `check_dispatch.py` + dispatch-mirror). No new test needed — see `## SAFE-01 Verification Approach`. |
</phase_requirements>

## Summary

Phase 107 is a documentation-scrub + gate-re-verification close phase with **zero new code behavior**. Phases 105 (firmware) and 106 (host) already removed the `mem_type`/`type` dispatch axis. This phase (1) rewrites the now-false firmware doc prose that still describes the deleted steps 7–11 fallback chain, (2) records the breaking wire-contract change in both sub-repo READMEs following an existing template, and (3) re-runs every non-regression gate to prove the removal changed no dispatch outcome.

I verified the entire gate surface live this session. **The four GATE-01 gates and the native suite are fully green** (native `pio test -e native` = 80/80; `check_dispatch.py` = 0 violations, 746 chips; `diff_db.py` = 0 unexplained changes; dispatch-mirror test passes). The doc edit sites are precisely located and small: `firestarter/CLAUDE.md` lines ~19–63 (dispatch narrative) and ~90 (legacy `type` bullet); `firestarter/doc/PROTOCOLS.md` needs **no numeric-`type` scrub** — its only `type=` strings are `electrical.type`/infoic identity tuples that are explicitly out of scope (D-03).

**Three findings require planner decisions and were NOT anticipated by CONTEXT** (see Open Questions + Assumptions Log): (a) the host `firestarter_app/CLAUDE.md` still carries a live `"type": 1` wire example, contradicting CONTEXT's "grep-confirmed clean" claim; (b) `pytest` is **not** absolute-green — there is one pre-existing golden-fixture failure and pre-existing ruff/format dirt, all in files untouched by v1.20 (a GATE-02 "green" scoping question, not a real regression); (c) the meta-repo canonical `messages.toml` and the host `messages.py`/`messages.toml` still define the retired `MSG_ERR_MEM_TYPE_UNSUPPORTED (0xAE)` — a real cross-repo codegen desync left by Phase 105, borderline in/out of DOC-01 scope.

**Primary recommendation:** Plan as two waves — (Wave 1) the firmware doc scrub + breaking-change records (edits confined to `firestarter/CLAUDE.md`, `firestarter/doc/PROTOCOLS.md`-verify, both READMEs, and the two CLAUDE.md notes); (Wave 2) a single verification task running every gate in sequence and asserting each is green *or matches the documented pre-existing baseline* (D-04). Surface the three findings to the operator before treating them as scope; do NOT auto-fix any of them.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Firmware dispatch-narrative scrub | Docs (firmware sub-repo) | — | Prose describes `memory.cpp` behavior; lives in `firestarter/CLAUDE.md` + `doc/PROTOCOLS.md` |
| Breaking-change / migration record | Docs (both sub-repo READMEs) | Docs (both CLAUDE.md) | Public-facing surface per D-01; agent-facing note secondary |
| Golden-trace / dispatch-mirror gate | Firmware test tier (`pio test -e native`) + host test tier (`pytest`) | — | Mirror test lives host-side but binds all three legs (doc/tool/firmware) |
| Chip-dispatch identity gate | Host tooling (`check_dispatch.py`, `diff_db.py`) | — | Cross-repo scanners run from `firestarter_app/` |
| Constants parity | Host test tier (`pytest`) | Reads firmware headers | `test_revision_constants_parity.py` reads `firestarter/include/*.h` |
| Over-voltage block (SAFE-01) | Firmware (VPP check in handlers) | Firmware native dispatch tests | Verified by existing dispatch-arm tests, not re-implemented here |

## Doc Edit Sites (DOC-01) — Verified Line-by-Line

All line numbers `[VERIFIED: grep/read of the actual files on v1.20-protocol-only-dispatch this session]`.

### `firestarter/CLAUDE.md` — PRIMARY scrub target

| Lines | Current (false) content | Required edit |
|-------|-------------------------|---------------|
| 20–24 | "dispatches on `handle->protocol` … **before** dispatching on `handle->mem_type` … many chip families have `mem_type=1` (TYPE_EPROM) … SRAM chips with `mem_type=1` MUST NOT reach `configure_eprom`" | Rewrite: firmware dispatches **solely** on `handle->protocol`. Drop the "before dispatching on mem_type" clause and the `mem_type=1` examples. The SRAM-must-not-reach-configure_eprom hazard note can survive rephrased in protocol terms (SRAM protocols 0x0E/0x27/0x28/0x29 route to `configure_sram`). |
| 28–31 | "The `mem_type` chain is retained as a backward-compatibility fallback for hand-crafted JSON commands or older host versions that omit `algorithm`; … the protocol-prefix chain always fires first." | Delete entirely. Replace with: there is no `mem_type` fallback; a command with no recognized protocol (incl. `protocol == 0`) fail-closes. |
| 49–53 | Steps **7–11** (`protocol == 0` only: `mem_type == TYPE_EPROM (1)` → configure_eprom; `mem_type == TYPE_SRAM (4)`; `mem_type == TYPE_FLASH_TYPE_3 (3)`; `mem_type == TYPE_FLASH_TYPE_4 (5)`; step 11 error `firestarter_error_response_format("Memory type 0x%02x not supported", handle->mem_type)`) | **Delete steps 7–11 outright.** Renumber so the terminal arm is: `protocol == 0` (and any unrecognized protocol) → `configure_not_implemented()` → `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED (0xBB)`. This matches the shipped `memory.cpp` (Phase 105 SUMMARY: single terminal unconditional `configure_not_implemented(handle)`). |
| 55–57 | "There is no `mem_type == 2` dispatch case … Any chip with `algorithm == 0` and an unrecognized `mem_type` reaches step 11." | Delete — step 11 no longer exists; `algorithm == 0` now reaches `configure_not_implemented()`. |
| 59–63 | "**Fail-closed invariant (Phase 64):** Steps 6a and 6b … never falls through to the `mem_type` chain. The `mem_type` fallback (steps 7–11) is unreachable for any non-zero `protocol` value." | Simplify: keep the fail-closed invariant statement (6a/6b arms remain in the shipped firmware) but drop all "…never falls through to the mem_type chain / mem_type fallback (steps 7–11) is unreachable" language — there is no mem_type chain to fall through to anymore. |
| **90** | `- \`type\` — legacy \`mem_type\` integer (fallback when algorithm is absent)` | **Delete this bullet** from the "JSON Wire Protocol → Key fields" list. Optionally add a one-line note that `type` is no longer parsed (silently skipped as an unknown field). |

**Cross-check against shipped firmware (Phase 105 SUMMARY, `105-01-SUMMARY.md`):** `configure_memory()` now has a single terminal `configure_not_implemented(handle)`; `protocol == 0` and any unrecognized non-zero protocol share the identical fail-closed exit (proven by `test_protocol_zero_fail_closes_not_implemented`). `firestarter_handle_t.mem_type` removed; `json_parser.c` no longer parses `type` (4 touchpoints removed → unknown-field-skip). `MSG_ERR_MEM_TYPE_UNSUPPORTED (0xAE)` + `TYPE_*` `#define`s retired from firmware `messages.h`/`memory.cpp`. The rewritten narrative MUST describe this reality. `[VERIFIED: 105-01-SUMMARY.md + grep of firestarter/src/proms/memory.cpp on branch]`

### `firestarter/doc/PROTOCOLS.md` — VERIFY-ONLY (no numeric-`type` scrub needed)

`[VERIFIED: grep -nE 'type=[0-9]|mem_type' doc/PROTOCOLS.md]` — the **only** `type=` hits are:
- Line 277: `type=4 / proto=0x07 / variant=0x4126 → resolved to SRAM_STD (0x28) / electrical.type FRAM` (FM1608 infoic identity tuple)
- Line 333: `type=1 / proto=0x34 / variant=0x3100 / flags=0x00414200` (X88C64 infoic identity tuple)

Both are **raw `infoic.xml` identity tuples / `electrical.type` string references** — the classification axis explicitly **preserved** by D-03/scope. There is **no numeric wire-`type`/`mem_type` field reference in PROTOCOLS.md to remove.** The INV-08/INV-09 rows (lines 418–419) and `electrical.type == "EEPROM"` derivations (lines 110, 130, 188, 329, 338) are ALL out of scope — do not touch. **Net PROTOCOLS.md edit: likely none** (or an optional clarifying note that these `type=N` tokens are infoic-XML raw fields, not the deleted wire field). Planner should treat PROTOCOLS.md as verify-only unless a reader-confusion clarification is desired (Claude's discretion).

### `firestarter/README.md` — breaking-change record (D-01), verify-clean of wire refs

`[VERIFIED: grep type/mem_type → 0 wire-field hits]` — clean of the wire axis. Add a **new `## Breaking Changes (v1.20)` section** (or a `###` subsection under a combined heading) mirroring the existing `## Breaking Changes (v1.10)` template at lines 17–35.

### `firestarter_app/README.md` — breaking-change record (D-01)

Has `type` references at lines 465 (`Type: EPROM` display output — `electrical.type` string, out of scope), 514/601 (`"type": "memory"` — a `_clean_config` raw-JSON string field, DIFFERENT axis, explicitly left untouched per Phase 106-02 D), and 586 (docs mentioning copying `type` among config params — the string field). **None of these are the numeric wire `type`.** Add the D-01 breaking-change section mirroring its existing `## Breaking Changes (v1.10)` (line 61). `[VERIFIED: read of README.md lines 455–605]`

### `firestarter/CLAUDE.md` + `firestarter_app/CLAUDE.md` — agent-facing D-01 note

Add a short note recording the wire-contract break. **`firestarter_app/CLAUDE.md` also has an unresolved live wire example — see Open Question #1.**

## Breaking-Change Record Wording (D-01)

The record should convey (from CONTEXT `<specifics>` + verified firmware behavior):

1. **`type` field removed from the wire.** The host→firmware JSON command no longer carries `type` (formerly the `mem_type` integer). `algorithm` (upstream minipro `protocol_id`) is the sole dispatch key.
2. **Every chip entry now requires a usable `algorithm`.** A built-in or user-override chip lacking a non-zero `algorithm` is **refused in-host** (`chip_resolver.resolve_chip` raises before any serial byte — HOST-04, Phase 106-03) — no silent fallback dispatch.
3. **Pre-v1.20 hosts emitting a stray `type` key remain SAFE.** The firmware silently skips unknown JSON fields (`json_parser.c` allowlist behavior — Phase 105). The break is not a crash: `type` simply **no longer does anything**, and a chip lacking `algorithm` is now refused rather than falling back to a `mem_type`-derived handler.
4. **Lockstep, no mixed-version hazard beyond loss-of-fallback.** Consistent with the existing v1.10 note's "upgrade both together" framing.

**Template to mirror:** `firestarter/README.md` lines 17–35 and `firestarter_app/README.md` lines 61+ already have a `## Breaking Changes (v1.10)` → `### <subsystem> (breaking change)` structure with an **Upgrade:** line. Reuse that exact shape for a `## Breaking Changes (v1.20)` entry. `[VERIFIED: read of both README breaking-changes sections]`

## Gate Command Inventory (GATE-01, GATE-02)

All commands RUN this session with the exact results shown. `[VERIFIED: executed on v1.20-protocol-only-dispatch, 2026-07-02]`

| Gate | Command (cwd) | This-session result | Requirement |
|------|---------------|---------------------|-------------|
| Native suite (incl. dispatch + frame-vector golden + not_implemented) | `pio test -e native` (in `firestarter/`) | **80/80 PASS** in ~18s | GATE-02, GATE-01, SAFE-01 |
| Native dispatch-only | `pio test -e native -f "*test_dispatch*"` (in `firestarter/`) | PASS (subset of above) | SAFE-01 |
| Dispatch-mirror guard | `python -m pytest tests/test_dispatch_mirror.py -q` (in `firestarter_app/`) | **PASS** (2 tests) | GATE-01 |
| Dispatch scanner | `python tools/check_dispatch.py` (in `firestarter_app/`) | **PASS exit 0** — 746 chips, 736 supported, 0 non_supported_dispatchable, 0 dispatch regressions, 0 consistency violations | GATE-01, SAFE-01 |
| DB value-diff | `python tools/diff_db.py` (in `firestarter_app/`) | **PASS exit 0** — 2 changed chips (W29C020/W29C040 page_size, from Phase 94, pre-explained), 0 unexplained, 0 new, 0 removed | GATE-01 |
| Host suite | `python -m pytest -q` (in `firestarter_app/`) | **710 passed, 1 FAILED** (pre-existing — see Pitfall #1) in ~40s | GATE-02 |
| Constants parity | Runs inside `pytest` as `tests/test_revision_constants_parity.py` (reads `firestarter/include/firestarter.h`, `rurp_pinout.h`, `rurp_shield.h`) | PASS (within the 710) | GATE-02 |
| ruff lint | `ruff check firestarter/ tests/ tools/` (in `firestarter_app/`) | **4 errors — ALL pre-existing** in `tools/catalog/codegen_vectors.py` + `tools/audit_coverage_matrix.py` (untouched by v1.20) | GATE-02 |
| ruff format | `ruff format --check firestarter/ tests/` (in `firestarter_app/`) | **1 file would reformat** — `tests/test_validate_family_cmd.py` (pre-existing, untouched by v1.20) | GATE-02 |
| mypy | `mypy` (strict on 8 modules per Phase 42 D-06) | mypy 2.1.0 present at `~/.local/bin/mypy`; run per `firestarter_app/CLAUDE.md` tooling gate | GATE-02 |

### "v1.16 golden register traces" — naming clarification (IMPORTANT for planner)

The CONTEXT/roadmap references `firestarter/tests/golden/stable-*.h` as the "v1.16 golden register traces." **This is imprecise.** `[VERIFIED: cat of those files]`:
- `firestarter/tests/golden/stable-expected.h` = `#define VERSION "1.2.4"` and `stable-baseline.h` = `#define VERSION "1.2.3"` — these are **VERSION-string fixtures** consumed by `firestarter_app/tests/test_update_version.py`, NOT register traces.
- The actual **frozen golden vectors** live in `firestarter/test/native/avr/test_frame_vectors/test_frame_vectors.cpp` + `firestarter/include/frame_vectors.h` (COBS frame + CRC8 known-answer vectors, Phase 52/54). These run inside `pio test -e native` (the `test_frame_vectors` suite — PASSED this session).
- The **dispatch non-regression signal** GATE-01 actually depends on is: (a) `test_dispatch/test_configure_memory.cpp` (one RUN_TEST per KNOWN_PROTOCOLS arm), and (b) the three-way `test_dispatch_mirror.py` guard.

**Planner action:** "re-verify golden traces" is satisfied by running `pio test -e native` (covers `test_frame_vectors` + `test_dispatch`) and `test_dispatch_mirror.py`. Do NOT hunt for a separate register-trace harness — it does not exist under that name. D-05 "never regenerate" applies to leaving `frame_vectors.h` / the dispatch tests / baselines (`tools/baseline/*.json`) unmodified.

## SAFE-01 Verification Approach

SAFE-01 = (a) over-voltage stays blocked at the firmware VPP check, and (b) every dispatchable DB chip routes to its identical handler via `protocol` alone.

**Recommendation: cover SAFE-01 entirely by RUNNING existing gates — add no new tests** (this is a docs/close phase; Phase 105 already proved SAFE-01 with a passing gate).

- **(b) Identical-handler routing** is proven by `check_dispatch.py` (746 chips, 0 non_supported_dispatchable, 0 dispatch regressions — GREEN this session) + the native dispatch suite (one arm per KNOWN_PROTOCOLS entry) + the dispatch-mirror three-way bind. Phase 105 SUMMARY coverage item D4 already asserts "every dispatchable DB chip still routes to its identical handler via protocol alone; the removed fallback was dead for all 746 chips" via these same gates.
- **(a) Over-voltage block** is structurally guaranteed by the fail-closed dispatch (unknown/`protocol==0` → `configure_not_implemented()`, zero hardware side effects, no VPP regulator engagement) plus `check_dispatch.py`'s structural guard "no chip routes to `configure_eprom` on a pinout with no vpp-pin" and the WARNING-5 type-keyed guard (both asserted GREEN by `check_dispatch.py` this session). The firmware VPP ADC check (SAF-04) and the SRAM/EEPROM paths never reaching the VPP regulator are exercised by the native handler-validation suites (`test_val_eprom`, `test_val_sram`, `test_val_eeprom28c`, `test_val_nor_unlock`, `test_val_5v_page`, `test_val_flash_intel` — all PASSED).

**No net-new test is needed or wanted.** Adding a test would violate "no new behavior" and risk a D-05 baseline touch. Phase 107's SAFE-01 task is: run the gates, confirm green, cite the coverage.

## Runtime State Inventory

> Rename/refactor-adjacent (the milestone removed an axis). Documentation reflects removed state — check for stale runtime artifacts that the doc scrub must not miss.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None — no datastore keys on `type`/`mem_type`. `chip_database.json` never carried a wire `type` field; `diff_db.py` confirms 0 value changes. | None (verified by `diff_db.py` GREEN). |
| Live service config | None — no external service configuration references `mem_type`. This is a firmware/CLI project. | None. |
| OS-registered state | None — no OS registrations embed the string. | None. |
| Secrets/env vars | None reference `type`/`mem_type`. (Test seams `FIRESTARTER_BASELINE_FILE`, `FIRESTARTER_CONFIG_DIR` exist but are unrelated.) | None. |
| Build artifacts / codegen | **FOUND (real desync):** meta-repo canonical `tools/catalog/messages.toml` (line 450) and host `firestarter_app/tools/catalog/messages.toml` (line 458) + generated `firestarter_app/firestarter/messages.py` (lines 99, 538–540) STILL define `MSG_ERR_MEM_TYPE_UNSUPPORTED = 0xAE`. Firmware `messages.h`/`messages.toml` already removed it (Phase 105). | **Open Question #3 — planner must decide scope.** This is a CODE/codegen artifact, not documentation. Reconciling it touches `sync_to_subrepos.sh`-managed codegen files (a code change), which the phase's scope guardrail forbids. Surface, do not auto-fix. |

## Common Pitfalls

### Pitfall 1: Treating pre-existing red as a Phase-105/106 regression (D-04 misfire)
**What goes wrong:** GATE-02 says "full `pytest` passes" and "ruff/ruff-format clean," but the repo is NOT absolute-green. Running the gates naively produces a red result that looks like a regression and could trigger a false D-04 STOP — or worse, tempt an auto-fix that violates scope.
**What is actually pre-existing (all in files NOT in the `beta..HEAD` v1.20 diff — `[VERIFIED: git diff --name-only beta..HEAD]`):**
- `pytest`: **`tests/test_audit_coverage_matrix.py::test_golden_file_matches` FAILS** (186034 vs 184631 bytes — a coverage-matrix golden-fixture drift). Documented in `106-*/deferred-items.md`; reproduced pre-105 via `git stash` in Phase 106. **Unrelated to `mem_type`.**
- `ruff check`: 4 errors, all in `tools/catalog/codegen_vectors.py` + `tools/audit_coverage_matrix.py`.
- `ruff format --check`: `tests/test_validate_family_cmd.py` would reformat.
**How to avoid:** The GATE-02 verification task must assert **"no NEW failure introduced by v1.20"**, not absolute green. Baseline the exact pre-existing set above and diff against it. A red result is a D-04 blocker ONLY if the failing artifact is in the v1.20 diff or newly broken. **Planner: bake the pre-existing baseline into the verification task's acceptance criteria.** (See Open Question #2 — operator should confirm whether these pre-existing items are acceptable at milestone close.)
**Warning signs:** A gate command returns non-zero but the failing file is one of the four listed above.

### Pitfall 2: Scrubbing `electrical.type` / infoic `type=N` tuples (scope violation)
**What goes wrong:** A blanket `grep type | delete` would destroy the v1.16 classification axis (INV-08/09, EEPROM derivations, FM1608/X88C64 identity tuples) that D-03 explicitly preserves.
**How to avoid:** Only the **numeric wire `type` (= `mem_type`)** references go. The distinguishing test: does the reference describe a **JSON wire field the firmware parses** (scrub it) or an **`electrical.type` string / infoic-XML `type=N` classification** (keep it)? PROTOCOLS.md's two `type=N` hits are the latter — keep both.
**Warning signs:** An edit touches line 277 or 333 of PROTOCOLS.md, or any `electrical.type` string.

### Pitfall 3: py3.12-masks-CI-py3.11 trap
**What goes wrong:** The devcontainer runs Python 3.12.13 (`[VERIFIED: python3 --version]`); CI targets py3.11 (and lint targets py3.9/3.11). `ruff`/`ruff format` behavior and some type-check outcomes can differ; claiming "CI green" from a 3.12-only run is unsafe. `python3.11` binary is **absent** in this devcontainer (consistent with the Phase-98/106-03 precedent).
**How to avoid:** Run `ruff check` + `ruff format --check` explicitly (ruff pins its target-version from `pyproject.toml`, so it is target-accurate regardless of interpreter). For mypy, run against the py3.9/3.11 config as `firestarter_app/CLAUDE.md`'s tooling gate specifies. Record the run as "structurally-green under py3.12.13 analysis target, py3.11 binary absent" — the same disposition Phase 106-03 used. `[CITED: MEMORY reference_devcontainer_py312_masks_ci_py39; 106-03-SUMMARY.md "py3.11 static gate" note]`

### Pitfall 4: firestarter_app test-env toolchain quirks
**What goes wrong:** The `firestarter_app` Python env can be in a wiped/foreign state; the hardened mypy gate prints OK even when mypy is missing.
**How to avoid:** Use `/usr/local` python; if the toolchain is wiped, restore with `pip install -e '.[test]'`. Verify mypy actually runs (do not trust a bare "OK"). Ignore any foreign `.venv/`. `[CITED: MEMORY reference_firestarter_app_python_test_env]` — this session `mypy 2.1.0` and `ruff`/`pytest` all ran cleanly, so the env is currently healthy.

### Pitfall 5: `check_dispatch.py` still has its OWN `_ALGO_MEM_TYPE` — do NOT flag it as stale
**What goes wrong:** Phase 106 removed `_ALGO_MEM_TYPE` from `database.py` (runtime). But `firestarter_app/tools/check_dispatch.py` INTENTIONALLY keeps its own `_ALGO_MEM_TYPE` table + `dispatch(protocol, mem_type)` model (lines 35–157). This is the **"tool leg" of the dispatch-mirror three-way bind** — it models firmware behavior for verification, it is not runtime dispatch. A doc scrub or "cleanup" that deletes it would break the dispatch-mirror gate.
**How to avoid:** Treat `check_dispatch.py`'s `_ALGO_MEM_TYPE`/`dispatch()` as a verification artifact, NOT stale code. Do not touch it. `[VERIFIED: grep of tools/check_dispatch.py + read of test_dispatch_mirror.py docstring]`

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Two-axis dispatch: `protocol` first, `mem_type` fallback (steps 7–11) | Single-axis: `protocol` only; `protocol==0`/unknown → `configure_not_implemented()` (0xBB) | Phase 105 (firmware) / 106 (host), v1.20 | Docs describing the fallback are now false — the DOC-01 scrub target |
| Wire carries `type` (mem_type) field | Wire carries `algorithm` only; `type` unknown-field-skipped | Phase 105/106, v1.20 | Breaking change — the D-01 record subject |
| `MSG_ERR_MEM_TYPE_UNSUPPORTED (0xAE)` + `TYPE_*` constants (firmware) | Retired from firmware; **still present in host mirror + meta canonical toml** | Phase 105 (firmware only) | Cross-repo codegen desync — Open Question #3 |

**Deprecated/outdated:**
- `firestarter/CLAUDE.md` dispatch narrative lines 20–63 + line 90: describe deleted behavior — must be rewritten.
- Roadmap phrase "v1.16 golden register traces = `stable-*.h`": imprecise; those are version-string fixtures (see clarification above).

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The `## Breaking Changes (v1.10)` README template is the intended shape for the new v1.20 record | Breaking-Change Record Wording | Low — matches D-01's "established public-facing surface" framing; wording is Claude's discretion |
| A2 | PROTOCOLS.md needs **no** edit (its only `type=N` are out-of-scope identity tuples) | Doc Edit Sites | Low — verified by grep; but planner may still want a clarifying note (discretion) |
| A3 | The pre-existing pytest/ruff failures are acceptable at milestone close (not a blocker) | Pitfall #1 / Open Q#2 | Medium — GATE-02 literally says "full pytest passes"; operator must confirm the pre-existing carve-out is acceptable |
| A4 | Host-side `MSG_ERR_MEM_TYPE_UNSUPPORTED (0xAE)` + meta canonical toml desync is OUT of Phase 107 scope (code/codegen, not docs) | Open Q#3 | Medium — it is FW-03-adjacent; leaving it is a documented near-miss (MEMORY), but reconciling it is a code change the scope guardrail forbids |
| A5 | SAFE-01 is fully covered by existing gates; no new test needed | SAFE-01 Verification Approach | Low — Phase 105 coverage item D4 already asserts this via the same gates |

## Open Questions

1. **Host `firestarter_app/CLAUDE.md` carries a live `"type": 1` wire example (lines ~55–68) — CONTEXT's "grep-confirmed clean" is inaccurate.**
   - What we know: `firestarter_app/CLAUDE.md`'s "Wire Protocol" section shows an example write command with `"type": 1,` on the wire (`[VERIFIED: read of firestarter_app/CLAUDE.md]`). CONTEXT D-02 states this file is "verify-only … carry no `type`/`mem_type` wire references." That is not true — this is a numeric wire `type` in a documented example.
   - What's unclear: Whether this was overlooked in CONTEXT's grep (which may have keyed only on the literal `mem_type` or the word-boundary `\btype\b` missing the JSON `"type"`), or whether the operator intends it left. The firmware no longer parses `type`, so the example is now misleading.
   - Recommendation: **Include `firestarter_app/CLAUDE.md`'s Wire Protocol example in the DOC-01 scrub** (remove the `"type": 1,` line, matching the firmware CLAUDE.md scrub). This is the same numeric-wire axis, not `electrical.type`. Surface to operator since it contradicts a stated decision. Do NOT touch line 58's later `electrical.type` refs.

2. **GATE-02 "full pytest passes / ruff clean" vs. the pre-existing red baseline.**
   - What we know: `pytest` = 710 pass / 1 fail (`test_golden_file_matches`); `ruff check` = 4 errors; `ruff format` = 1 file — all pre-existing, all in files untouched by v1.20 (`[VERIFIED: git diff beta..HEAD]`).
   - What's unclear: Whether the milestone close accepts these pre-existing items as documented debt, or whether GATE-02 demands they be fixed (which would be out-of-scope code changes).
   - Recommendation: Scope the GATE-02 acceptance to "no NEW regression from Phase 105/106." Surface the pre-existing baseline to the operator for an explicit accept-as-debt decision at close (mirrors how Phase 106 logged them to `deferred-items.md`). Do not fix them in this docs/gate phase.

3. **Retired `MSG_ERR_MEM_TYPE_UNSUPPORTED (0xAE)` still in meta canonical `messages.toml` + host `messages.py`/`messages.toml` (firmware already clean).**
   - What we know: Phase 105 removed 0xAE from firmware `messages.h`/`messages.toml` but left the **meta-repo canonical** `tools/catalog/messages.toml` (line 450) and the host copies stale (`[VERIFIED: grep across all three toml + messages.py]`). This matches MEMORY `reference_firmware_messages_h_is_codegen_generated` ("v1.20 P105 hand-edit left canonical toml stale (FW-03 near-miss)").
   - What's unclear: Whether reconciling this (edit meta canonical toml → run `sync_to_subrepos.sh` → regen `messages.py`) belongs in Phase 107. It is a codegen/code change, which the scope guardrail forbids; but the retired constant is milestone cleanup.
   - Recommendation: **Surface as a finding; default OUT of Phase 107 scope** (it is code, not docs, and touching codegen risks the D-05/no-behavior-change guardrail). If the operator wants it reconciled, it should be a small dedicated task explicitly authorized, NOT folded silently into the docs scrub. Note that it does NOT affect any dispatch gate (0xAE is a now-unemitted message id, not a dispatch key) — so it is not a D-04 blocker.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| PlatformIO (`pio`) | `pio test -e native` (GATE-01/02, SAFE-01) | ✓ | at `/usr/local/bin/pio` | — |
| Python | pytest + gate tools | ✓ | 3.12.13 (`/usr/local`) | — (py3.11 binary absent — see Pitfall #3) |
| pytest | Host suite (GATE-02) | ✓ | ran 711 tests this session | — |
| ruff | Lint/format gate (GATE-02) | ✓ | ran this session | — |
| mypy | Type gate (GATE-02) | ✓ | 2.1.0 at `~/.local/bin/mypy` | verify it actually runs (Pitfall #4) |
| `check_dispatch.py` / `diff_db.py` | GATE-01 | ✓ | in `firestarter_app/tools/` | — |
| Hardware (Arduino/RURP) | — | N/A | — | **Not needed — this phase is 100% docs + host-side gates + native (host-compiled) tests. No bench.** |

**Missing dependencies with no fallback:** None that block Phase 107.
**Missing dependencies with fallback:** `python3.11` binary absent → validate via ruff's pinned target-version + record the py3.12-analysis disposition (Pitfall #3).

## Validation Architecture

> `workflow.nyquist_validation` is absent in `.planning/config.json` → treated as ENABLED.

### Test Framework
| Property | Value |
|----------|-------|
| Framework (firmware) | PlatformIO + Unity, `[env:native]` (host-compiled, no board) |
| Framework (host) | pytest (+ syrupy snapshots, ruff, mypy) |
| Config file | `firestarter/platformio.ini`; `firestarter_app/pyproject.toml` + `.github/workflows/ci.yml` |
| Quick run command | `pio test -e native -f "*test_dispatch*"` (firmware) / `python -m pytest tests/test_dispatch_mirror.py -q` (host) |
| Full suite command | `pio test -e native` (firmware) + `python -m pytest -q` (host, from `firestarter_app/`) |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| DOC-01 | Docs reflect removed axis; breaking change recorded | manual review + grep | `grep -nE 'mem_type\|steps 7' firestarter/CLAUDE.md` returns 0 fallback-chain hits after scrub | ✅ (grep) |
| GATE-01 | Golden/frame vectors + dispatch-mirror green; check_dispatch 0; diff_db 0 | integration | `pio test -e native` + `pytest tests/test_dispatch_mirror.py` + `python tools/check_dispatch.py` + `python tools/diff_db.py` | ✅ all exist, all GREEN this session |
| GATE-02 | Full native + host suites; constants parity; ruff/format/mypy | unit + integration | `pio test -e native` + `python -m pytest -q` + `ruff check` + `ruff format --check` + `mypy` | ✅ (1 pre-existing host failure — Pitfall #1) |
| SAFE-01 | Over-voltage blocked; identical-handler routing | integration | `python tools/check_dispatch.py` + `pio test -e native -f "*test_val*"` | ✅ GREEN this session |

### Sampling Rate
- **Per doc-edit commit:** grep the scrubbed file for residual `mem_type`/steps-7–11 refs (fast).
- **Per wave merge:** full gate sweep (native + host + check_dispatch + diff_db).
- **Phase gate:** all GATE-01 gates green + GATE-02 green-or-matches-pre-existing-baseline before close.

### Wave 0 Gaps
- None — all test infrastructure exists and was exercised green this session. No new test files needed (SAFE-01 covered by existing gates; adding tests would violate "no new behavior").

## Security Domain

> `security_enforcement` absent in config → treated as enabled. This is a docs/gate close phase with NO new code, so the security surface is verification-only.

### Applicable ASVS Categories
| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V5 Input Validation | yes (verify-only) | Firmware `json_parser.c` allowlist silently skips unknown fields (incl. now-removed `type`) — a stray `type` from a pre-v1.20 host is safely ignored, not acted on. Verified by native suite + WIRE-01. |
| V6 Cryptography | no | No crypto in scope. |
| Others (V2/V3/V4) | no | No auth/session/access-control surface in an offline USB-serial CLI + firmware. |

### Known Threat Patterns for firmware/host CLI
| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Over-voltage on a 5V part (12V VPP on wrong pin) — hardware-damage hazard | Tampering / Denial | Fail-closed dispatch (`protocol==0`/unknown → `configure_not_implemented()`, no regulator engagement) + `check_dispatch.py` structural + WARNING-5 guards + firmware VPP ADC check (SAF-04). All GREEN this session (SAFE-01). |
| Malformed/hand-crafted JSON with stray `type` | Tampering | Unknown-field-skip in `json_parser.c`; host-side `algorithm`-presence guard (HOST-04) refuses before any serial byte. |

**No new security controls needed** — Phase 107 re-verifies existing mitigations via the SAFE-01 gate run.

## Sources

### Primary (HIGH confidence)
- `firestarter/CLAUDE.md`, `firestarter/doc/PROTOCOLS.md`, `firestarter/README.md`, `firestarter_app/README.md`, `firestarter_app/CLAUDE.md` — read directly this session (edit-site enumeration).
- `firestarter_app/tools/check_dispatch.py`, `tools/diff_db.py`, `tests/test_dispatch_mirror.py` — read + executed (GREEN).
- `pio test -e native` — executed, 80/80 PASS.
- `python -m pytest -q` (firestarter_app) — executed, 710 pass / 1 pre-existing fail.
- `.planning/phases/105-*/105-01-SUMMARY.md`, `106-*/106-0{1,2,3}-SUMMARY.md`, `deferred-items.md` — authoritative record of what 105/106 removed.
- `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md` (Phase 107 section), `107-CONTEXT.md`.
- `git diff --name-only beta..HEAD` (both sub-repos) — confirmed pre-existing failures are outside v1.20 scope.

### Secondary (MEDIUM confidence)
- MEMORY notes: `reference_firmware_messages_h_is_codegen_generated` (FW-03 near-miss / stale canonical toml), `reference_devcontainer_py312_masks_ci_py39`, `reference_firestarter_app_python_test_env`, `project_v120_milestone_seed`.

### Tertiary (LOW confidence)
- None.

## Metadata

**Confidence breakdown:**
- Doc edit sites: HIGH — every line verified by direct read/grep against the branch.
- Gate inventory: HIGH — every gate executed this session with recorded output.
- Pitfalls / pre-existing baseline: HIGH — reproduced and cross-checked against `git diff beta..HEAD` + Phase 106 deferred-items.
- Open questions (host CLAUDE.md `type`, messages 0xAE desync): HIGH that they exist; MEDIUM on the correct scope disposition (operator decision).

**Research date:** 2026-07-02
**Valid until:** ~2026-07-09 (fast-moving — the branch is under active close; re-verify gate state if any further commits land on `v1.20-protocol-only-dispatch` before planning).
