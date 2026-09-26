# Phase 106: HOST — Host `mem_type` Removal - Research

**Researched:** 2026-07-02
**Domain:** Python host CLI cleanup — remove the numeric `type`/`mem_type` dispatch axis from `firestarter_app/`, mirroring the Phase 105 firmware removal
**Confidence:** HIGH (all findings verified against live source at HEAD of `v1.20-protocol-only-dispatch`)

## Summary

This is a pure-cleanup, mechanical phase with all substantive decisions already locked in `106-CONTEXT.md` (D-01..D-06). The host must (1) stop emitting the `type` wire key [HOST-01], (2) delete `_ALGO_MEM_TYPE` + the derived `mem_type` (`determined_type`) + the `"type"` mapped-dict key from `database.py` [HOST-02], (3) drop the `mem_type`-keyed numeric display-label fallback (`type_map` + the `type_int` parameter) from `ic_layout.py` and its callers [HOST-03], and (4) reject any chip lacking a usable (present-and-non-zero) `algorithm` at the `chip_resolver.resolve_chip` chokepoint, reusing `ChipNotImplementedError`, before any serial byte [HOST-04].

The blast radius is **wider than the sites named in CONTEXT.md's canonical_refs**. The runtime edit sites are confirmed and correctly located. But there are **four additional test/tool files** that reference `mem_type` / `_ALGO_MEM_TYPE` / the numeric `type` key and will break or drift if not addressed: `tests/test_eprom_database.py` (asserts `"type"` is a required wire key — inverts like the `test_val_wire_*` suite), `tests/test_chip_resolver.py:43` (same assertion), `tests/test_ic_layout.py:180` (calls `get_chip_type_string(0, pid)` positionally — the `type_int` param removal is a compile-forcing ripple), and the **`check_dispatch.py` tool leg** (`tools/check_dispatch.py` + `tests/test_dispatch_mirror.py` + `tests/test_decoder.py` + `tests/test_build_db_inclusion.py`), which maintains its OWN `_ALGO_MEM_TYPE` and a `dispatch(protocol, mem_type)` simulation.

**Primary recommendation:** Treat `database.py::_ALGO_MEM_TYPE` (the *runtime* copy, D-04) and `check_dispatch.py::_ALGO_MEM_TYPE` (the *GATE tool* copy) as two distinct entities. Phase 106 removes the runtime copy per D-04; the tool copy is a deliberate deadness-proving simulation whose scope CONTEXT.md left implicit (canonical_refs say it "stays green ... unaffected"). Surface this as the single decision the planner must resolve explicitly before writing tasks (see Open Question #1). Everything else is mechanical delete-and-invert, gated by py3.11-target `ruff`/`ruff format`/`mypy`/`pytest`.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Wire command emission (`type` removal) | Host / DB conversion (`database.py::convert_to_programmer`) | Host / ops (`eprom_operations.py` copies verbatim) | The ONE emit site; ops does `command_dict = eprom_data_dict.copy()` with no independent `type` injection |
| `mem_type` derivation removal | Host / DB mapping (`database.py::_map_data`) | — | `determined_type` + `_ALGO_MEM_TYPE` live only here in the runtime |
| Display-label resolution | Host / presentation (`ic_layout.py::resolve_type_label`/`get_chip_type_string`) | Host / views (`eprom_info.py`, `build_specifications`) | Single shared helper feeds both `info` and `list`/`search` |
| Algorithm-presence refusal | Host / resolver chokepoint (`chip_resolver.py::resolve_chip`) | Host / exceptions (`ChipNotImplementedError`) | Single pre-serial chokepoint; already the home of the `support_status` guard |
| Dispatch-deadness verification | Dev tooling (`tools/check_dispatch.py`) | Tests (`test_dispatch_mirror`, `test_decoder`, `test_build_db_inclusion`) | Static simulation of host+firmware dispatch — a GATE, not the runtime |

## Standard Stack

Not applicable — no new packages. This phase edits existing Python source in `firestarter_app/`. Toolchain is already pinned (see Environment Availability). No `## Package Legitimacy Audit` needed (zero installs).

## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01 (rejection rule):** "Usable `algorithm`" = **present and non-zero**. Reject only when `algorithm` is absent or `0` — mirrors firmware `protocol == 0 → 0xBB`. Do NOT add a stricter "not in `KNOWN_PROTOCOLS`" gate (a non-zero-but-unknown protocol falls through to firmware fail-closed 0xBB).
- **D-02 (guard site + surface):** Extend `chip_resolver.resolve_chip` and **reuse `ChipNotImplementedError`**. Guard lands alongside the existing `support_status` refusal (fires BEFORE `convert_to_programmer`). No new exception type. Message must name the chip and state a protocol/`algorithm` is required. `info`/`list`/`search`/`id` display paths bypass `resolve_chip` and stay unaffected.
- **D-03 (label + signature):** `resolve_type_label`/`get_chip_type_string` derive the label from `electrical.type` first, then protocol-based name; when neither resolves, show **`"Unknown"`**. **Drop the `type_int` (mem_type) parameter** from both signatures and delete the numeric `type_map` (`{1: EPROM, 2: Flash type 2, …}`). No behavior regression for any chip that already resolved via `electrical.type`/protocol.
- **D-04 (full removal):** Delete the `"type"` key from `_map_data`'s output entirely (the `determined_type` block at `database.py:~418–428, 445` goes away with `_ALGO_MEM_TYPE`). Clean up **every** `.get("type", 0)` consumer: `convert_to_programmer` (`database.py:585`), `ic_layout.py:561`, `eprom_info.py:408`. No vestigial internal field.
- **D-05 (wire-val tests — delete-and-invert):** Flip each `tests/test_val_wire_*.py` to positively assert `"type"` is NOT in the emitted command. Absence IS HOST-01's proof.
- **D-06 (HOST-04 test — SC#4):** Add a test in `tests/test_chip_resolver.py` exercising a deliberately-broken user-override entry (no `algorithm` / `algorithm == 0`) → asserts `ChipNotImplementedError` raised, **no serial byte** emitted.

### Claude's Discretion

- Exact wording of the HOST-04 rejection message (must name the chip + state a protocol/`algorithm` is required — clear/actionable).
- Exact grouping of edits into commits, and whether the `type_int` param removal ripples into other `ic_layout`/`eprom_info` call sites discovered during planning (mechanical, forced by the signature change).
- Whether `eprom_info.py:69`'s raw-JSON `"type": "unknown"` **string** field (a different, string-typed key unrelated to numeric `mem_type`) needs any touch — planner to confirm it is NOT the `mem_type` axis and leave it unless it consumes the removed integer `type`.

### Deferred Ideas (OUT OF SCOPE)

- **Phase 107 (this milestone, close):** Doc updates (`firestarter/CLAUDE.md` dispatch steps 7–11 + the `"type": 1` wire example, `firestarter/doc/PROTOCOLS.md`, JSON wire-field docs, sub-repo README/changelog breaking-change record) + full non-regression re-verification (GATE-01/02, SAFE-01).
- **LEGACY-01 (v2):** `FLAG_VPE_AS_VPP (0x10)` removal — out of the `mem_type`-axis scope.
- **LEGACY-02 (v2):** Rename `EPROM_LEGACY (0x0B)` label + scrub remaining "legacy fallback" prose.
- **Beta release cut (operator-gated):** `3.0.0bXX` tag + gitlink bump — NOT a phase; gitlinks stay PINNED at b10 pending manual operator authorization.

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| HOST-01 | Host emits no `type` key in any serial command payload | Emit site is exactly ONE: `database.py:585` (`convert_to_programmer`). `eprom_operations.py:307` `command_dict = eprom_data_dict.copy()` with NO independent `type` injection (verified — grep for `"type"`/`mem_type` in `eprom_operations.py` returns 0 hits). Proven by inverted `test_val_wire_*` (D-05). |
| HOST-02 | `database.py` drops `_ALGO_MEM_TYPE`, derived `mem_type`, "Generic Flash (legacy fallback only)" default | `_ALGO_MEM_TYPE` at `database.py:48`; `determined_type` block at `:418–428` (the `"Flash" in type_str → 2 # Generic Flash (legacy fallback only)` at `:426`); mapped-dict `"type": determined_type` at `:445`. All runtime consumers enumerated below. |
| HOST-03 | `mem_type`-keyed legacy display-label fallbacks removed from `ic_layout.py`/`eprom_info.py` | `type_map` at `ic_layout.py:222`; `type_int` param at `:204` (`get_chip_type_string`) and `:505` (`resolve_type_label`); callers `ic_layout.py:562-566` (`build_specifications`) and `eprom_info.py:406-410` (list/search). `electrical.type` → `_ELECTRICAL_TYPE_LABEL` → `_PROTOCOL_DISPLAY_NAME` tiers stay; only the numeric fallback tier + param go. |
| HOST-04 | Chip lacking usable `algorithm` rejected with clear error before any serial byte | Guard lands in `chip_resolver.resolve_chip` (`:54-57` region), reusing `ChipNotImplementedError`. Structurally pre-serial: guard is upstream of `convert_to_programmer` (`:60`) and all serial I/O. Test pattern mirrors existing `test_resolve_chip_guard_fires_before_convert_to_programmer` (patches `convert_to_programmer`, asserts not called). |

## Runtime State Inventory

> Rename/refactor phase — required. This is a code-only host refactor; no persisted runtime state stores the `mem_type`/`type` axis.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | **None** — `chip_database.json` stores `programming.algorithm` + `electrical.type` (string), never a numeric `mem_type`. The numeric `type`/`mem_type` is a *derived*, in-memory value produced by `_map_data`, never persisted. Verified: `grep '"type":' firestarter/data/chip_database.json` returns only string `electrical.type` values, and the DB is keyed on `algorithm`. `diff_db.py` must show no value change (GATE-01) — this phase edits code, not the generated DB. | None (code edit only; do NOT regenerate `chip_database.json`) |
| Live service config | **None** — no external service holds the axis. Host talks to firmware over serial per-invocation; nothing cached. | None |
| OS-registered state | **None** — no OS-registered names embed `mem_type`. | None |
| Secrets/env vars | **None** — no env var / secret references the axis. `~/.firestarter/database.json` user overrides may contain entries lacking `algorithm`; those are the *intended breaking change* (D-01 refuses them), not state to migrate. | None (accepted breaking change per CONTEXT.md domain note) |
| Build artifacts | **None** stale from THIS phase. `firestarter/messages.py` (codegen from `tools/catalog/messages.toml`) still defines `MSG_ERR_MEM_TYPE_UNSUPPORTED = 0xAE` (host-side mirror of the retired firmware message) — see Open Question #2 for scope. If touched, regeneration via `tools/catalog/codegen.py` is required (never hand-edit `messages.py`). | Conditional — see Open Question #2 |

**The canonical question — after every host source file is updated, what still carries the old axis?**
Two categories remain: (a) the `check_dispatch.py` GATE tool's own `_ALGO_MEM_TYPE`+`dispatch(protocol, mem_type)` deadness-simulation (Open Question #1), and (b) the host `MSG_ERR_MEM_TYPE_UNSUPPORTED = 0xAE` message-catalog mirror (Open Question #2). Both are candidates the planner must explicitly scope in-or-out, not leave ambiguous.

## Verified Edit-Site Blast Radius

All line numbers verified against live source at HEAD of `v1.20-protocol-only-dispatch`. CONTEXT.md line numbers were accurate; drift notes below.

### Runtime source (in-scope, D-02/D-03/D-04) `[VERIFIED: source read]`

| File:line | Site | Action | Note |
|-----------|------|--------|------|
| `database.py:46-65` | `_ALGO_MEM_TYPE` dict + header comment | DELETE (D-04) | Comment `:46-47` says "kept consistent for fallback paths" — now false |
| `database.py:415-428` | `determined_type` derivation block | DELETE (D-04) | `:426` = the "Generic Flash (legacy fallback only)" substring default |
| `database.py:445` | `"type": determined_type,` in `_map_data` mapped dict | DELETE key (D-04) | The `"electrical-type"` key at `:456` STAYS (D-04 canonical ground truth) |
| `database.py:585` | `"type": full_eprom_data.get("type", 0),` in `convert_to_programmer` | DELETE line (D-04, HOST-01) | THE single wire-emit site |
| `ic_layout.py:203-223` | `get_chip_type_string(self, chip_type_int, protocol_id=None)` + `type_map` | Drop `chip_type_int` param; delete `type_map`; return `"Unknown"` when protocol unresolved (D-03) | Rename note: CONTEXT.md calls the param `type_int`; source names it `chip_type_int` on `get_chip_type_string` and `type_int` on `resolve_type_label` |
| `ic_layout.py:499-531` | `resolve_type_label(self, electrical_type, type_int=0, protocol_id=None)` | Drop `type_int` param; update docstring; delegate to `get_chip_type_string(protocol_id)` (D-03) | |
| `ic_layout.py:562-566` | `build_specifications` caller (passes `eprom_data.get("type", 0)`) | Drop the `.get("type",0)` positional arg (D-03/D-04) | |
| `eprom_info.py:406-410` | `print_eprom_list_table` caller (passes `ic.get("type", 0)`) | Drop the `.get("type",0)` positional arg (D-03/D-04) | list/search Type column |
| `chip_resolver.py:54-57` | `support_status` guard region | ADD algorithm-presence guard AFTER the `support_status` check, still before `get_eprom`/`convert_to_programmer` (D-01/D-02, HOST-04) | See Pitfall 3 for exact placement |

### Confirmed NON-targets (leave untouched)

| File:line | Why NOT touched |
|-----------|-----------------|
| `eprom_info.py:69` | `"type": "unknown"` is a **string-typed** raw-JSON display field (in `_clean_config`'s `key_map`), distinct from the numeric `mem_type` axis. Verified: it maps to `raw_config.get("type", ...)` display default, never consumes the removed integer. Claude's-discretion confirm → **leave**. |
| `ic_layout.py:469-482` | `_PROTOCOL_DISPLAY_NAME` — protocol-based labels; the surviving fallback tier. |
| `ic_layout.py:491-497` | `_ELECTRICAL_TYPE_LABEL` — `electrical.type` ground-truth map; the primary label source. |
| `database.py:434-435` | `info_flags` erase-derivation keys on `electrical.type in ("EEPROM","Flash/EEPROM")` — NOT on `mem_type`. Unaffected. |
| `constants.py` | Verified: no `TYPE_*`/`mem_type`/`0xAE` constant — no dual-repo parity member to remove (Phase 105 already retired the firmware `TYPE_*`/`0xAE`). Do NOT introduce one. |

### Test surface (in-scope + newly-discovered ripples)

| File | Sites | Action | Named in CONTEXT.md? |
|------|-------|--------|----------------------|
| `tests/test_val_wire_eprom.py` | `:86-87` `mem_type = wire.get("type",0)` → `dispatch(algo, mem_type)` | D-05 delete-and-invert: assert `"type" not in wire`; call `dispatch(algo)` (see OQ#1 re: `dispatch` signature) | YES (D-05) |
| `tests/test_val_wire_flash_intel.py` | `:84-85` | D-05 | YES |
| `tests/test_val_wire_nor_unlock.py` | `:84-85` | D-05 | YES |
| `tests/test_val_wire_5v_page.py` | `:91-92` | D-05 | YES |
| `tests/test_val_wire_eeprom28c.py` | `:84-85` | D-05 | YES |
| `tests/test_val_wire_sram.py` | `:88-89` AND `:111-115` (TWO test functions) | D-05 — both | YES (note: two sites) |
| `tests/test_chip_resolver.py` | `:43` asserts `"type"` in required-keys tuple; ADD D-06 broken-override test | Remove `"type"` from the required-keys assertion; add HOST-04 test | Partially — D-06 named; `:43` inversion NOT named |
| `tests/test_eprom_database.py` | `:101` asserts `"type"` in required-keys tuple (`test_convert_to_programmer_required_keys_present`) | Remove `"type"` from the required-keys assertion | **NOT named in CONTEXT.md — NEW** |
| `tests/test_ic_layout.py` | `:180` `get_chip_type_string(0, pid)` positional call | Update to `get_chip_type_string(pid)` after param drop (D-03 ripple) | **NOT named — forced by D-03 signature change** |

### GATE tool leg (scope decision required — Open Question #1)

| File | Sites | Nature |
|------|-------|--------|
| `tools/check_dispatch.py` | `:38` own `_ALGO_MEM_TYPE`; `:133` `dispatch(protocol, mem_type)`; `:151-157` mem_type fallback chain; `:229-238` mirrors `_map_data`'s mem_type derivation | GATE-01 deadness-proving **simulation** of host+firmware dispatch. Imports `EpromDatabase` (`:22`) but keeps its OWN copy of `_ALGO_MEM_TYPE`. |
| `tests/test_dispatch_mirror.py` | `:151,166-167` consume `check_dispatch._ALGO_MEM_TYPE` + `dispatch(hex, mem_type)` | Doc↔tool dispatch-mirror guard |
| `tests/test_decoder.py` | `:697-744` (`TestDispatchGate02`) exercise `dispatch(0,1)`, `dispatch(0,99)` mem_type fallback | Pins the `dispatch()` fallback-chain behavior |
| `tests/test_build_db_inclusion.py` | `:725,738-739` import + use `check_dispatch._ALGO_MEM_TYPE` | Inclusion-hazard gate |

## Non-Regression Gates (must stay green)

| Gate | Command | Status baseline (this session) |
|------|---------|-------------------------------|
| `check_dispatch.py` | `python tools/check_dispatch.py` (exit 0) | Green post-Phase-105 (746 chips, 0 violations, per 105 SUMMARY) `[VERIFIED: 105-01-SUMMARY]` |
| `diff_db.py` | no `chip_database.json` value change | This phase edits code only; DB untouched |
| `test_dispatch_mirror.py` | `pytest tests/test_dispatch_mirror.py` | Green (depends on decision in OQ#1) |
| ruff check | `ruff check firestarter/ tests/ tools/` (py39 target) | `All checks passed!` on the 4 runtime files `[VERIFIED: ran]` |
| ruff format | `ruff format --check firestarter/ tests/` | `already formatted` `[VERIFIED: ran]` |
| mypy | `mypy <8 strict modules>` (py3.9 config) | `chip_resolver.py`: `Success: no issues found` `[VERIFIED: ran]` |
| pytest | `pytest` | wire + resolver suites green `[VERIFIED: ran]` |

## Common Pitfalls

### Pitfall 1: The py3.12-masks-CI-3.11 ruff/mypy trap
**What goes wrong:** The devcontainer runs Python 3.12.13 + ruff 0.15.20 + mypy 2.1.0, but CI targets **py3.11** (both `ci.yml` and `beta-release.yml` set `python-version: '3.11'`) while ruff/mypy configs pin the *analysis* target to `py39` (`pyproject.toml:92` `target-version = "py39"`, `:111` `python_version = "3.9"`). `[VERIFIED: ran]`
**Why it happens:** py3.12 syntax/idioms that pass locally can trip py3.11 CI; ruff auto-fixes to py39-incompatible forms are gated by `target-version`. The `mypy 2.1.0` output even prints `[mypy]: python_version: Python 3.9 is not supported (must be 3.10 or higher)` as a warning while still succeeding — do not mistake this for a failure. `[VERIFIED: ran]`
**How to avoid:** Validate `ruff check` + `ruff format --check` + `mypy <strict list>` + `pytest` against the target config, not just local success. This phase's edits are deletions (lower syntax risk), but the HOST-04 guard is net-new code — keep it py3.11/py39-idiom clean (no `match`, no py3.10+ union sugar beyond what the file already uses; `chip_resolver.py` already uses `EpromDatabase | None`, which is fine because `from __future__ import annotations` is not required for the runtime path since it's a default-arg annotation — but confirm the existing file style).
**Warning signs:** Local green, CI red on ruff/mypy.

### Pitfall 2: `eprom_info.py:69` false-positive
**What goes wrong:** A blind grep for `"type"` flags `eprom_info.py:69` `"type": "unknown"`, tempting removal.
**Why it happens:** It shares the literal key name but is a **string** display field in `_clean_config`'s `key_map`, unrelated to the numeric `mem_type`. `[VERIFIED: source read]`
**How to avoid:** Leave it (Claude's-discretion in CONTEXT.md confirmed → untouched). Removing it would regress the `info`/`id` display path.
**Warning signs:** `info`/`id` output loses a Type line.

### Pitfall 3: HOST-04 guard placement — before OR after `support_status`?
**What goes wrong:** Placing the algorithm-presence check in the wrong spot either double-refuses a supported chip or lets an unusable entry through.
**Why it happens:** `resolve_chip` has a specific order: not-found (`:48-49`) → support_status (`:54-57`) → `get_eprom` + `convert_to_programmer` (`:59-63`). The `algorithm` value lives in the *mapped* dict (`protocol-id` key) produced by `_map_data`/`get_eprom`, not in `raw_config`. `[VERIFIED: source read]`
**How to avoid:** Two viable placements — (a) read `raw_config.get("programming",{}).get("algorithm",0)` alongside the `support_status` read (matches D-02 "alongside the existing support_status refusal" literally, before `get_eprom`), or (b) check `data.get("algorithm",0)` after `convert_to_programmer` at `:60-63`. D-02 says "alongside the existing `support_status` refusal ... BEFORE `convert_to_programmer` builds any wire dict" → **placement (a)** is the CONTEXT-faithful choice. Note `raw_config` is the un-mapped DB record, so read `algorithm` from `raw_config["programming"]["algorithm"]` (the same path `check_dispatch.py:218` and `chip_resolver` neighbors use), NOT the mapped `protocol-id` key.
**Warning signs:** A supported chip with a valid non-zero algorithm gets refused; or the guard reads a key that only exists post-mapping.

### Pitfall 4: `dispatch()` signature coupling in `test_val_wire_*` inversion (D-05)
**What goes wrong:** The `test_val_wire_*` tests currently do `mem_type = wire.get("type",0); handler = dispatch(algo, mem_type)`. After D-05 inverts the assertion to `"type" not in wire`, the `dispatch(algo, mem_type)` call still needs a second arg — but `wire.get("type",0)` now always returns `0`.
**Why it happens:** `dispatch()` lives in `check_dispatch.py` and takes `(protocol, mem_type)`. With `algo` non-zero for every real chip, `dispatch()` never consults `mem_type` (the fallback chain is `protocol==0`-only, `:149-157`). So `dispatch(algo, 0)` still returns the correct handler. `[VERIFIED: source read]`
**How to avoid:** The inverted tests can keep the handler-dispatch assertion by passing `0` (or whatever OQ#1 resolves for the `dispatch` signature). If OQ#1 keeps `dispatch(protocol, mem_type)`, pass `0`; if it drops the param, update call sites. Do NOT read `wire.get("type")` post-inversion — the whole point is `type` is gone.
**Warning signs:** `test_val_wire_*` handler assertions fail after `type` removal.

### Pitfall 5: mypy strict-island scope
**What goes wrong:** Assuming all four edited files are under strict mypy.
**Why it happens:** Only `chip_resolver.py` is in the 8-module strict island (`pyproject.toml:134-143`). `database.py`, `ic_layout.py`, `eprom_info.py` are in the non-strict `follow_imports = "silent"` list (`:151-162`). `[VERIFIED: source read]`
**How to avoid:** The HOST-04 guard code in `chip_resolver.py` MUST be fully type-annotated (`disallow_untyped_defs`). The `type_int`-param removal in `ic_layout.py` is not strict-gated but should still keep clean signatures. Run `mypy` against the strict list to confirm the guard passes.
**Warning signs:** `mypy` red only after touching `chip_resolver.py`.

## Validation Architecture

> Nyquist enabled (`workflow.nyquist_validation` not `false` in config → treated as enabled).

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (with pytest-cov; `--cov-fail-under=70` in CI) `[VERIFIED: pyproject/CLAUDE.md]` |
| Config file | `firestarter_app/pyproject.toml` (`[tool.pytest.ini_options]`, `[tool.coverage.*]`) |
| Quick run command | `cd firestarter_app && python -m pytest tests/test_val_wire_eprom.py tests/test_chip_resolver.py tests/test_eprom_database.py -q` |
| Full suite command | `cd firestarter_app && python -m pytest` |
| Static gates | `ruff check firestarter/ tests/ tools/` · `ruff format --check firestarter/ tests/` · `mypy firestarter/main.py firestarter/cli_handlers.py firestarter/chip_resolver.py firestarter/frame_parser.py firestarter/codec.py firestarter/address_parser.py firestarter/exceptions.py firestarter/serial_comm.py` |
| Dispatch gate | `python tools/check_dispatch.py` (exit 0, 0 violations) |

### Phase Requirements → Test Map (SC#1–SC#4)
| SC | Behavior | Test Type | Automated Command | Site |
|----|----------|-----------|-------------------|------|
| SC#1 | No `type` key on the wire | unit (inverted) | `pytest tests/test_val_wire_*.py -q` | 6 files, 7 test fns — assert `"type" not in wire` (D-05) |
| SC#1 | Wire required-keys no longer include `type` | unit | `pytest tests/test_eprom_database.py::TestConvert...::test_convert_to_programmer_required_keys_present tests/test_chip_resolver.py -q` | `test_eprom_database.py:101` + `test_chip_resolver.py:43` — remove `"type"` from tuple |
| SC#2 | `database.py` has no `_ALGO_MEM_TYPE`/`determined_type`/"Generic Flash" default | grep gate | `! grep -n "_ALGO_MEM_TYPE\|determined_type\|Generic Flash (legacy fallback only)" firestarter/database.py` | Verification step (mirrors Phase 105's grep gates) |
| SC#3 | `ic_layout.py`/`eprom_info.py` no numeric `type_map`/`type_int` fallback; labels from `electrical.type`/protocol | unit + grep | `pytest tests/test_ic_layout.py -q` (existing `resolve_type_label`/`get_chip_type_string` coverage — `test_resolve_type_label_fram`, `:168` single-source, `:188` coverage) + `! grep "type_map\|type_int" firestarter/ic_layout.py` | Existing tests pin no-regression; update `:180` call site |
| SC#4 | Chip lacking usable `algorithm` refused with clear error, no serial byte | unit (net-new) | `pytest tests/test_chip_resolver.py -q` | D-06 test — broken user-override (`algorithm` absent / `0`) → `ChipNotImplementedError`; patch `convert_to_programmer` + assert not called (mirror `test_resolve_chip_guard_fires_before_convert_to_programmer:122`) |

### Sampling Rate
- **Per task commit:** the SC-mapped quick command for the touched file(s) + `ruff check` on touched files.
- **Per wave merge:** full `pytest` + `ruff`/`ruff format`/`mypy` strict list + `python tools/check_dispatch.py`.
- **Phase gate:** full suite green + all four SC grep/test gates green before `/gsd-verify-work`.

### Wave 0 Gaps
- None — all four SCs are covered by existing test files that need edit-and-invert, plus one net-new D-06 test in the existing `tests/test_chip_resolver.py`. No new test file or fixture infrastructure required (`db` fixture at `test_chip_resolver.py:28` already provides `EpromDatabase(skip_local_override=True)`; the D-06 broken-override test can construct a minimal override dict or monkeypatch `get_eprom_config` to return an entry with `algorithm: 0`).

## Security Domain

> `security_enforcement` absent in config → treated as enabled. This is a code-cleanup phase with no auth/session/crypto/network surface. The one safety-relevant axis:

| Concern | Applies | Standard Control |
|---------|---------|------------------|
| Fail-closed dispatch (no silent fallback to a dangerous handler) | yes | HOST-04 guard refuses missing/zero `algorithm` in-host BEFORE serial I/O, exactly mirroring firmware `protocol==0 → 0xBB` fail-close (D-01). Prevents an unusable entry from silently reaching a 12V-VPP hazard path. |
| Over-voltage stays blocked | yes (unchanged) | Firmware VPP ceiling check is untouched; removing `type` does not alter any voltage path. `check_dispatch.py` structural VPP-pin guard stays green (GATE-01/SAFE-01, re-verified Phase 107). |
| Input validation | n/a-changed | No new external input parsed; the `algorithm` presence check tightens (not loosens) validation. |

STRIDE: the only relevant vector is **Elevation-of-privilege / Tampering via a hand-crafted or legacy user-override DB entry** that lacks `algorithm`. Pre-106 such an entry would derive a `mem_type` and could dispatch; post-106 it is refused in-host. This is a security *improvement* and the intended breaking change.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Dual dispatch axis (`algorithm` + `mem_type` fallback) | `algorithm`-only dispatch, firmware fail-closes on `protocol==0` | Phase 105 (firmware, landed 2026-07-02) | Host must stop emitting `type` (this phase) to complete WIRE-01 |
| `type_map` numeric label fallback | `electrical.type` → `_PROTOCOL_DISPLAY_NAME` → `"Unknown"` | This phase (D-03) | Numeric mem_type label tier removed |

**Deprecated/outdated after this phase:**
- Host `database.py::_ALGO_MEM_TYPE` — removed (runtime).
- The `"type": 1` example in `firestarter_app/CLAUDE.md` "Wire Protocol" — becomes stale; its update is Phase 107 / DOC-01, NOT this phase (do not touch docs here). `[VERIFIED: CLAUDE.md read]`

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `check_dispatch.py`'s `_ALGO_MEM_TYPE` (tool leg) is intentionally OUT of Phase 106 scope (deadness-simulation, kept per canonical_refs "stays green ... unaffected") | Open Question #1 | If it should be removed, `test_dispatch_mirror.py`/`test_decoder.py`/`test_build_db_inclusion.py` all need edits too — larger scope. Planner MUST confirm. |
| A2 | The host `MSG_ERR_MEM_TYPE_UNSUPPORTED = 0xAE` mirror in `messages.py`/`messages.toml` is Phase 107 (or later) territory, not Phase 106 | Open Question #2 | If in-scope, requires codegen regen (`codegen.py`), not hand-edit — a distinct workstream. 105-SUMMARY explicitly flagged it as "Phase 106/107 territory" (ambiguous). |
| A3 | HOST-04 guard reads `algorithm` from `raw_config["programming"]["algorithm"]` (un-mapped DB path), matching `check_dispatch.py:218` | Pitfall 3 | If read from the mapped `protocol-id` key, placement must move after `get_eprom` (still pre-serial, but not "alongside support_status"). |

## Open Questions

1. **Does Phase 106 remove `tools/check_dispatch.py::_ALGO_MEM_TYPE` + the `dispatch(protocol, mem_type)` mem_type fallback chain, or leave them?**
   - What we know: CONTEXT.md D-04 scopes only `database.py`'s `_ALGO_MEM_TYPE`; canonical_refs list `check_dispatch.py` and `test_dispatch_mirror.py` under "Non-regression gates (must stay green)" and say they are "unaffected by `type` removal." The tool keeps its OWN copy deliberately — it's a static simulation that models the *historical* host+firmware dispatch to prove the fallback was dead for all real chips. Phase 105 already deleted the firmware fallback, yet `check_dispatch.py` passed 0 violations post-105 with its `dispatch()` fallback chain intact.
   - What's unclear: SC#2 ("no derived `mem_type`") and D-04 ("no vestigial internal field left behind") could be read to demand the tool's copy also go. A plan-checker or code-reviewer may flag the tool's `_ALGO_MEM_TYPE` as stale.
   - **Recommendation:** LEAVE the tool leg untouched in Phase 106 (matches canonical_refs literally; the tool is a *verification artifact* simulating history, not runtime dispatch). Confirm this reading in the plan's decision log so the reviewer doesn't re-litigate it. If the operator wants the tool copy removed too, that is a scope addition the planner should raise explicitly (it cascades into 3 test files). This is the ONE decision the planner must nail down before writing tasks.

2. **Is the host `MSG_ERR_MEM_TYPE_UNSUPPORTED = 0xAE` mirror (`firestarter/messages.py:99,538` + `tools/catalog/messages.toml:458`) removed in Phase 106?**
   - What we know: 105-SUMMARY says the firmware retired `0xAE`; the host mirror was "intentionally NOT touched" and flagged as "Phase 106/107 territory." CONTEXT.md D-01..D-06 do NOT mention it. `messages.py` is codegen-generated (edit `messages.toml` + run `codegen.py`, per the memory note — NEVER hand-edit).
   - What's unclear: neither Phase 106 nor Phase 107 CONTEXT/requirements explicitly claim it. It's a dead message code the host no longer receives (firmware never emits it now).
   - **Recommendation:** Treat as OUT of Phase 106 (CONTEXT.md is silent; Phase 106 is scoped to the wire-emit + label + guard, not message-catalog cleanup). Flag for the operator/Phase 107 close as a loose-end. If pulled in, it requires the `messages.toml` → `codegen.py` regen path (drift-gate aware), not a source edit — a materially different task type.

3. **D-06 broken-override test construction:** how to inject an entry with `algorithm` absent/`0` without a real `~/.firestarter/database.json`?
   - What we know: `test_chip_resolver.py` uses `EpromDatabase(skip_local_override=True)` and the existing guard tests use real DB chips (`X88C64P`, `AT28C04`) plus `unittest.mock.patch`.
   - Recommendation: monkeypatch `db.get_eprom_config` (and/or `db.get_eprom`) to return a synthetic raw entry with `programming.algorithm` missing/`0` and `support_status == "supported"` (so the algorithm guard, not the support_status guard, is what fires), then assert `ChipNotImplementedError` + `convert_to_programmer` not called. Mirrors `test_resolve_chip_guard_fires_before_convert_to_programmer:122-132`.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | host tests + tooling | ✓ | 3.12.13 (CI target 3.11) | — |
| pytest | validation | ✓ (`python -m pytest` runs) | — | — |
| ruff | lint/format gate | ✓ | 0.15.20 | — |
| mypy | type gate | ✓ | 2.1.0 | — |
| firestarter (editable install) | `from firestarter...` imports | ✓ (imports + tests resolve) | 3.0.0bXX dev | `pip install -e '.[test]'` if toolchain wiped (per memory note) |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** if the toolchain is ever wiped, restore with `pip install -e '.[test]'` from `firestarter_app/` (the hardened mypy gate prints OK even when mypy is MISSING — verify mypy actually present).

## Project Constraints (from CLAUDE.md)

From `/workspaces/CLAUDE.md` and `/workspaces/firestarter_app/CLAUDE.md`:
- **Dual-repo constants parity** (`constants.py` ↔ `firestarter.h`): no `TYPE_*`/`mem_type` member exists to touch this phase (verified) — do not introduce one.
- **`chip_database.json` is generated** — do NOT hand-edit; this phase changes code, not the DB (`diff_db.py` must show no value change).
- **`messages.py` is codegen-generated** from `tools/catalog/messages.toml` via `codegen.py` — never hand-edit (relevant only if OQ#2 is pulled in).
- **Tooling gate (v1.8):** `ruff check` + `ruff format --check` + `mypy` (strict on 8 modules incl. `chip_resolver.py`) + `pytest --cov-fail-under=70`, all enforced by CI on every PR; `pre-commit` mirrors the hook order locally.
- **CI targets py3.11** while ruff/mypy analysis pins py39 — validate against target, not local py3.12.
- Firmware/host submodule commits land INSIDE `firestarter_app/` on branch `v1.20-protocol-only-dispatch`; meta-repo gitlinks stay PINNED (operator-gated).

## Sources

### Primary (HIGH confidence)
- Live source at HEAD of `v1.20-protocol-only-dispatch` (`firestarter_app/`): `database.py`, `chip_resolver.py`, `ic_layout.py`, `eprom_info.py`, `eprom_operations.py`, `exceptions.py`, `constants.py`, `tools/check_dispatch.py`, `pyproject.toml`, `.github/workflows/ci.yml`+`beta-release.yml`, all `tests/test_val_wire_*.py`, `test_chip_resolver.py`, `test_eprom_database.py`, `test_ic_layout.py`, `test_decoder.py`, `test_build_db_inclusion.py`, `test_dispatch_mirror.py` — all read directly.
- Ran: `ruff check`, `ruff format --check`, `mypy firestarter/chip_resolver.py`, `pytest tests/test_val_wire_eprom.py tests/test_chip_resolver.py` — all green baseline.
- `.planning/phases/106-host-host-mem-type-removal/106-CONTEXT.md` (locked decisions D-01..D-06).
- `.planning/phases/105-fw-firmware-mem-type-removal/{105-CONTEXT.md,105-01-SUMMARY.md}` (firmware-half symmetry + the flagged host message-mirror loose-end).
- `.planning/{REQUIREMENTS.md,ROADMAP.md}` (HOST-01..04, SC#1–#4).
- `/workspaces/CLAUDE.md`, `/workspaces/firestarter_app/CLAUDE.md` (project constraints).

### Secondary (MEDIUM confidence)
- MEMORY.md notes (py3.12-masks-CI, codegen-generated `messages.py`, firestarter_app test env) — corroborated against live config.

### Tertiary (LOW confidence)
- None.

## Metadata

**Confidence breakdown:**
- Edit sites / blast radius: HIGH — every site read in source; CONTEXT.md line numbers confirmed accurate; 3 additional ripple sites (`test_eprom_database.py:101`, `test_ic_layout.py:180`, the `check_dispatch` tool leg) discovered beyond CONTEXT.md's named list.
- Validation architecture: HIGH — all four SCs map to existing tests needing edit-and-invert + one net-new D-06 test; no Wave 0 gaps.
- Pitfalls: HIGH — py3.12/py3.11 trap, `eprom_info.py:69` false-positive, and guard placement all verified against live config/source.
- Open Questions: two genuine scope decisions (tool-leg `_ALGO_MEM_TYPE`, host `0xAE` mirror) the planner must resolve; both are scope-boundary calls, not blockers.

**Research date:** 2026-07-02
**Valid until:** 2026-07-09 (source is a live milestone branch under active edit; re-verify line numbers if planning slips a week)
