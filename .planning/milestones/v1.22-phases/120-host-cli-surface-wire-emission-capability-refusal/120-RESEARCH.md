# Phase 120: HOST — CLI surface, wire emission, capability refusal - Research

**Researched:** 2026-07-29
**Domain:** Python host CLI (Click + pytest), cross-repo constants parity, curated capability partition over a generated chip DB
**Confidence:** HIGH on every in-tree code claim (all executed or read at file:line this session) · MEDIUM on the allow-set's per-family SDP membership (no datasheet-of-record exists for 46 of 84 entries; the validation ceiling already forbids proving it) · HIGH on the gate-table baseline (all nine rows re-run green this session)

## Summary

Phase 120 is a host-only phase with an unusually high ratio of *discovery* to *construction*. The construction is genuinely copy-shaped, as the ROADMAP's `research: no` flag predicted: `erase_eprom` is an exact template for both SDP operator methods, `dev test`'s gate trio is an exact template for `dev sdp`, and `tools/check_is_memory_cmd_no_ifdef.py` donates a working, fail-closed, comment-stripping firmware-header reader for the D-12 parity gate. Every one of those was read this session and each is confirmed reusable.

The discovery is where the risk sits, and it is concentrated in one place: **`resolve_chip` returns the *programmer* dict, and that dict carries neither `protocol-id` nor `electrical-type` nor the part number.** Executed this session: `resolve_chip('at28c256')` yields exactly `{memory-size, algorithm, pin-count, vpp_mv, pulse-delay, chip-id, flags, bus-config}`. Every production caller of `write_eprom` / `check_eprom_blank` / `run_plan`'s dispatcher passes that dict. The consequence is that `check_eprom_blank`'s `_SRAM_PROTO_IDS` short-circuit — the very in-tree pattern D-03 declined to follow but was told to read, and the one PROJECT.md's SIXTH CORRECTION item 6 says "fires **before** any firmware command is issued" — is **vacuous in production**: it reads `eprom_data_dict.get("electrical-type", "")` → `""` and `.get("protocol-id", 0)` → `0`, and was measured returning `False` for a real SRAM part this session. The keep-disposition is still right (don't delete it), but its stated *reason* is false, and more importantly a `sdp_capability()` predicate that keys off `eprom_data_dict["protocol-id"]` would reproduce the identical silent vacuity. **The predicate must take the chip name plus a DB handle, or the `get_eprom()` full dict — never the `resolve_chip` output.** That single fact reshapes D-03's signature, D-04's write-path plumbing, and the validation architecture (the allow-set gate needs a shape-assertion leg, not just a membership leg).

Three further findings change plan content rather than just plan detail. First, HOST-04's own named refuse-trio **cannot be captured by any pinout-based structural rule**: `2804` and `2816` sit on `DIP24_2816` but `2817` sits on `DIP28_28C64`, so the deny-list spans two pinouts — independent confirmation of D-01's rejection of a DB-derived structural rule, and proof that the allow-set must be token-enumerated. Second, D-09's blast radius is **six** unconditional INFO-band ids, not five: `MSG_INFO_HW` (`0x5B`) is emitted through `LOG_WARN_ID_U8` at `rurp_hw_rev_utils.h:96` — an ungated macro — while its *catalog* severity is INFO, so it arrives at the host as INFO and is currently discarded. That is F-120-07 made concrete, and it fires exactly on shields whose revision detect is inconclusive. Third, a naive `CMD_X → COMMAND_X` name mapping in the D-12 parity gate **breaks on a real pair**: firmware defines `CMD_DEV_REGISTER` (singular), the host defines `COMMAND_DEV_REGISTERS` (plural), and `CMD_FRAME_MAX` is a `CMD_`-prefixed define whose value is a macro, not a literal.

**Primary recommendation:** Plan `sdp_capability.py` first, with signature `sdp_capability(chip_name: str, db: EpromDatabase) -> tuple[bool, str]` reading `db.get_eprom(name)`'s `name` + `protocol-id` keys (never `resolve_chip`'s output), holding a 63-token curated allow-set evaluated under a whole-entry unanimity rule, and ship its exhaustiveness gate with both a membership leg and a **dict-shape leg** that fails if the predicate is ever fed a `resolve_chip` dict. Then HOST-03's constants + `COMMAND_NAMES`, then the two `erase_eprom`-shaped operator methods, then the `dev sdp` handler and the `write`-path auto-set in parallel, then D-09/D-15, then the D-20 amendment last.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| `dev sdp` CLI surface, confirm gate, off-TTY refusal | Host CLI (`cli_handlers.py`) | — | Click owns argument shape and consent; no other tier can see a TTY |
| SDP capability predicate (allow-set) | Host domain module (`sdp_capability.py`, new) | — | Must be importable by both the CLI handler and the operations layer without Click or serial coupling (D-03) |
| Chip name → DB entry resolution | Host DB layer (`database.py`) | — | `get_eprom_config` already owns alias splitting, paren stripping, case folding |
| Support-status refusal | Host resolver (`chip_resolver.py`) | — | Already the single chokepoint; D-08 places it third, after capability |
| Wire flag bit mapping | Host operations (`eprom_operations.build_flags`) | Host CLI (`_build_op_flags`) | D-19 keeps every wire-flag bit mapped in one function |
| Command frame construction + state machine | Host operations (`eprom_operations.py`) | Host transport (`serial_comm.py`) | `erase_eprom`'s payload-free shape is the template |
| Frame severity → log level | Host transport (`serial_comm._log_rurp_feedback`) | Host catalog (`messages.py`) | The catalog owns the severity band; the transport owns the level mapping (D-09) |
| Ack observation (`0x86`) | Host transport (`_decode_id_frame` override seam) | Host operations | Phase 55's `firmware_max_chunk` is the exact precedent for recording an observed id outside the ring-fenced read loop |
| SDP sequence emission, timing, protection state | Firmware (`eeprom_28c.cpp`) | — | **Read-only this phase.** Zero firmware edits |
| Protection-state readback | *Nobody — physically unavailable* | — | Drives D-10/D-11's honesty-in-text-not-in-status rule |

## Project Constraints (from CLAUDE.md)

From `/workspaces/CLAUDE.md` (meta) and `/workspaces/firestarter_app/CLAUDE.md`:

| Directive | Where it binds this phase |
|-----------|---------------------------|
| `constants.py` MUST stay in sync with `firestarter/include/firestarter.h` (same flag bits, same command codes) | HOST-03 is the closing half of the pair firmware-before-host deliberately left open [VERIFIED: read both files this session] |
| `chip_database.json` is generated — do NOT hand-edit | HOST-04's "zero DB change" is a CLAUDE.md rule as well as a requirement |
| Tooling gate: `ruff check` + `ruff format --check` + `mypy` (strict-island over 8 modules incl. `cli_handlers.py`, `serial_comm.py`) + `pytest --cov-fail-under=70` | Both strict modules are edited here |
| Ruff/format must be validated against py3.9/3.11 CI targets, not the devcontainer's 3.12 | Devcontainer runs Python 3.12.13 [VERIFIED: `python3 --version`] |
| Serial protocol changes must be kept in sync between `serial_comm.py` and `firestarter.cpp` | No protocol change here — only host-side severity mapping and ack observation |
| `firestarter/messages.py` is codegen output — never hand-normalise | Already carries `0x5E`–`0x62`, `0x86`, `0x87`; no regeneration needed [VERIFIED: imported CATALOG this session] |

**⚠ The CI gate commands are narrower than the bare tool invocations.** `.github/workflows/ci.yml` runs `ruff check firestarter/ tests/` and `ruff format --check firestarter/ tests/` — **not** `ruff check .`. Executed this session:

- `ruff check firestarter/ tests/` → `All checks passed!`; `ruff format --check firestarter/ tests/` → `94 files already formatted`. **Clean baseline.**
- `ruff check .` → **4 errors**; `ruff format --check .` → **4 files would be reformatted** (`.github/scripts/update_version.py`, `tools/catalog/codegen.py`, `tools/catalog/codegen_vectors.py`, `tools/check_mypy_watermark.py`, plus `tools/audit_coverage_matrix.py` I001).

All of that is **pre-existing debt outside the CI scope**. A plan that runs bare `ruff check .` will chase four unrelated failures. Use the CI-scoped form.

**⚠ The mypy gate is a watermark, not a zero.** CI runs `python tools/check_mypy_watermark.py`, which reported `mypy errors: 1 (watermark: 35)` and **exit 0** this session. `mypy` over the strict-8 module list reports 1 real error (`firestarter/submit.py:446`, `Incompatible types in assignment`) and exits non-zero. So (a) do not use bare `mypy <strict-8>` as the pass/fail gate — it is red at baseline; (b) the watermark has **34 slack**, so a new type error introduced in `cli_handlers.py` or `serial_comm.py` would pass CI silently. **Recommendation:** run `python3 tools/check_mypy_watermark.py` as the gate *and* assert the reported error count does not exceed 1.

Also observed: `mypy` prints `pyproject.toml: [mypy]: python_version: Python 3.9 is not supported (must be 3.10 or higher)` under the devcontainer's mypy. Devcontainer artifact; not a regression to fix here.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01: The partition is a fail-closed ALLOW-list, not a deny-list.** Only parts on an explicit SDP-capable list may receive `CMD_SDP_UNLOCK` / `CMD_SDP_LOCK`; everything else in the `0x0D` bucket is refused, **including anything unrecognised**.
- **D-02: The allow-set is keyed on DB `part_number` tokens and its completeness is machine-checked.** Production code holds the allow-set (runtime property, so a `~/.firestarter/database.json` addition is refused). A pytest asserts `allow-set ∪ refuse-set == exactly the 84 algorithm==13 entries`, following `tests/test_sdp_db_invariant.py` verbatim including its no-skip-marker and non-vacuity case.
- **D-03: The predicate lives in a new `firestarter/sdp_capability.py` as a pure function.** Shape `-> (allowed: bool, reason: str)`, no serial, no Click, no DB-loader coupling; answers both "is this even `0x0D`" and "does this `0x0D` part have SDP" in one call.
- **D-04: HOST-04's refusal also covers the `write` path's automatic unlock, and the auto-set is reported.** For a refused part the host sets `FLAG_SKIP_SDP_UNLOCK` on `write` itself and prints one mandatory line stating that it did and why. The divergence from `3.0.0b11` must be stated in the SUMMARY as a deliberate host-side change.
- **D-05: No mode flag — the subcommand is the mode, and the gate is an interactive confirm.**
- **D-06: `-y` is kept, and off-TTY refuses without it.**
- **D-07: `enable` and `disable` share one gate with different confirm text.**
- **D-08: Gate order is absent → capability → support-status → confirm → serial.** SAFE-04's `get_eprom`-emptiness hard-fail first (never a `resolve_chip` refusal), then one `sdp_capability()` call, then `resolve_chip`, then the confirm, then the port opens.
- **D-09: INFO-band frames are promoted from DEBUG to INFO in `_log_response`.**
- **D-10: A host summary line carries the verdict and the unreadable-state caveat, never the duration.** Measured microseconds stay exclusively on the firmware's `0x5F`/`0x61` line.
- **D-11: Exit code is plain `0/1`; WARNs stay in the text.** A `MSG_WARN_SDP_TBLC_EXCEEDED` (`0x87`) prints at WARNING level and does not change the code.
- **D-12: The parity test parses `firestarter.h` and asserts two-way correspondence.** Every `#define CMD_*` and `#define FLAG_*`, bidirectional, with a planted-violation fixture. Exemption list required for `CMD_IDLE` and the `#ifdef DEV_TOOLS` pair.
- **D-13: `COMMAND_NAMES` coverage rides in the same test, and the `FW_ABSENT` skipif is retained.** Residual host-only-CI skip gap recorded as known-and-explained.
- **D-14: `dev sdp` maps `MSG_ERR_UNKNOWN_CMD` to a firmware-too-old refusal.**
- **D-15: `--skip-sdp-unlock` requires the `0x86` ack and fails loudly when it is absent.**
- **D-16: No version floor is introduced, and the landing-order fact is recorded with commit provenance** (firmware landed first, Phase 119 final commit `0048b3d`).
- **D-17: The flag is exposed on `write` only.**
- **D-18: On a non-`0x0D` chip the host warns and proceeds.**
- **D-19: The bit is mapped by a new keyword-only `build_flags()` parameter**, keyword-only with a `False` default because `build_flags`' signature is pinned by `tests/test_bug_characterization.py`'s BUG-1 contract.
- **D-20: The Phase 121 scope amendment for the operator's `dev test` redesign is an owned task in this phase.** ROADMAP Phase 121 entry + Phase Details, new `REQUIREMENTS.md` requirement ids and traceability rows, plus a `PROJECT.md` correction block. Do not implement any of the redesign here.

### Claude's Discretion

- Exact confirm wording, refusal reason strings, and the host summary line's phrasing (must satisfy D-10's honesty requirement in the text itself; D-01's reasons should name *why*).
- Whether `dev sdp` is a Click sub-group or a `<chip>` argument plus an `enable|disable` `click.Choice`.
- The allow-set's concrete data shape — `frozenset` of tokens, or a mapping from token to reason/provenance string.
- How the header parser extracts the defines — new regex, or reuse of `check_is_memory_cmd_no_ifdef.py`'s brace-matched extraction.
- The exemption-list mechanics for `CMD_IDLE` and the `#ifdef DEV_TOOLS` pair, provided exemptions are enumerated explicitly rather than pattern-skipped.
- Severity of the D-15 missing-ack failure (ERROR vs WARNING) and its exact wording.
- Whether the D-04 auto-set report line is one line or two, provided it is unconditional and visible at default verbosity.
- Plan ordering, subject to two hard constraints: HOST-03's constants + `COMMAND_NAMES` before any plan emitting `cmd 9`/`cmd 10`; `sdp_capability.py` before both the `dev sdp` handler and the `write`-path auto-set.

### Deferred Ideas (OUT OF SCOPE)

- The `dev test` redesign itself — routed to Phase 121; only the ROADMAP/REQUIREMENTS amendment lands here.
- The wider CLI flag re-design (`-f` splitting, `-b` polarity, project-wide `-y`).
- The `0x0D` flag-surface honesty problem (`FLAG_CAN_ERASE` on all 84, no erase op).
- `MSG_INFO_SDP_UNLOCK_DONE_US` (`0x5F`) caveat text — catalog change, Phase 121/122.
- Widening `_probe_port`'s `[\d.x]+` version capture.
- `dev sdp`'s release-channel disposition (999.15 / gh#8).
- A separate always-on `COMMAND_NAMES` completeness test.
- Carried from 119: third strobe kind; `infoic.xml` `page_size` decode phase; Unity-teardown SIGABRT; all-84 table-driven traces; `DIP24_2816` `static-high-pins` (SDP-F8); datasheet verification of SDP magic addresses (SDP-F7).
- Reviewed todos not folded: `decode-infoic-flags-bits-14-15-protect-metadata.md`, `fold-response-code-into-log-macro.md`.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description (verbatim, `REQUIREMENTS.md:75-80`) | Research Support |
|----|-------------|------------------|
| HOST-01 | `firestarter dev sdp <chip> <enable\|disable>` exists, behind the v1.21 destructiveness confirm + `-y` + the SAFE-04 absent-chip hard-fail | F-04 (`dev test`'s gate trio read at `cli_handlers.py:1717-1847`, with F-05's ordering correction — the in-tree order is confirm-then-absent, the reverse of D-08); F-13 (the `_is_interactive` monkeypatch seam); F-14 (the `find_and_connect` patch seam that makes "no port opened" a real assertion) |
| HOST-02 | `write --skip-sdp-unlock` emits the `0x100` flag, following the in-tree rule that `--skip-X` skips a chip-state-modifying operation | F-11 (`build_flags` at `:168-183`, `_build_op_flags` at `:242-280`, `write` at `:463-530`, all read; the BUG-1 contract's actual assertions located) |
| HOST-03 | New `CMD_*`/`FLAG_*` values land in the same commit pair across `firestarter.h` ↔ `constants.py`, with mandatory `COMMAND_NAMES` entries, and the constants-parity test is extended | F-08, F-09, F-10 (the complete two-side define inventory, the three exemption classes, and the `CMD_DEV_REGISTER`/`COMMAND_DEV_REGISTERS` name-mismatch trap) |
| HOST-04 | A pre-wire capability refusal keeps SDP commands away from non-SDP parts inside the `0x0D` bucket — the 2 FRAM parts and the pre-SDP `2804`/`2816`/`2817` class — resolved in code, with **zero DB change** | F-01 (the enumerated 37/47 partition summing to 84), F-02 (token/normalisation rules), F-03 (the `2817`-spans-two-pinouts proof that kills any structural rule), F-06 (the `resolve_chip` dict-shape trap that decides the predicate's signature) |
| HOST-05 | The SDP outcome is reported honestly and **never as a fabricated state boolean** — where state is unreadable, the report says so | F-07 (D-09's blast radius is six ids, not five; `MSG_INFO_HW` is the sixth); F-12 (`_log_rurp_feedback` is the real function name; `get_response` filters INFO out entirely, so a host-side line is the only reliable carrier at the operation layer) |
| HOST-06 | The host half never lands before the firmware half; a host emitting `0x100` against `3.0.0b11` would be silently ignored and would run the unlock the user declined | F-15 (`Response.id` is populated at `serial_comm.py:398`, and `_decode_id_frame` is the documented non-ring-fenced override seam with Phase 55's `firmware_max_chunk` as precedent — two independent places a `0x86` observation can live); F-16 (firmware tip `0048b3d`, working tree clean, verified this session) |

**⚠ Requirement-ID collision.** `HOST-01`..`HOST-04` already appear in the host tree from **earlier milestones** — `firestarter/chip_resolver.py:59` carries `# Algorithm-presence guard (HOST-04 / D-01 / D-02)`, and `tests/test_protocol_not_implemented.py:95`, `tests/test_protocol_not_implemented_production_path.py:311`, `tests/test_val_wire_*.py` all cite `HOST-01`/`HOST-02` from v1.20. A grep-based traceability check for `HOST-04` will produce false hits. New in-source markers should be spelled `v1.22 HOST-04` (or similar) to disambiguate. [VERIFIED: grep over `firestarter/`, `tests/`, `tools/`]
</phase_requirements>

## Standard Stack

No new dependencies. Everything this phase needs already ships.

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `click` | as pinned in `pyproject.toml` | `dev sdp` subcommand, `click.Choice` argument, `-y` flag | Every CLI surface in the app is Click since v1.8 CLI-01 [VERIFIED: `cli_handlers.py` imports] |
| `rich` (`rich.prompt.Confirm`) | as pinned | The interactive confirm gate | `dev test` uses `Confirm.ask` at `cli_handlers.py:1834` — the exact reusable half of the v1.21 pattern (D-05) [VERIFIED: read] |
| `pytest` + `unittest.mock` | as pinned | All new gates | `patch(...)` / `Mock(spec=...)` is the house idiom throughout `tests/` [VERIFIED] |
| `click.testing.CliRunner` | bundled with click | `dev sdp` handler tests | Established pattern; note it replaces `sys.stdin`, which is why `_is_interactive` exists as a separate monkeypatchable function [VERIFIED: `cli_handlers.py:1717-1724`] |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `re` (stdlib) | — | `#define` extraction from `firestarter.h` | D-12's parser; reuse `check_is_memory_cmd_no_ifdef.py`'s comment-stripping, not its brace matcher (see F-09) |
| `json` + `pathlib` (stdlib) | — | Reading the shipped DB directly in the exhaustiveness gate | `tests/test_sdp_db_invariant.py` does exactly this, deliberately bypassing `EpromDatabase` [VERIFIED: `:29-34`] |
| `os.environ` seam | — | Fail-closed `FIRESTARTER_*_SRC` override for the planted-violation fixture | `check_is_memory_cmd_no_ifdef.py:92-94` is the template [VERIFIED] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| A new `tools/check_constants_parity.py` + paired pytest | A single self-contained pytest in `tests/test_revision_constants_parity.py` that parses the header inline | The pytest-only form is simpler and keeps D-13's one-gate decision literal. But `tools/` scripts get an `FIRESTARTER_*_SRC` env seam and a standalone exit code, which is how every other planted-violation gate in this project is built, and it adds a runnable row to the CORRECTION-4 table. **Recommendation: pytest-only.** Reason: D-12/D-13 explicitly want *one* gate and the `FW_ABSENT` skipif retained; a `tools/` script that skips is a contradiction, and files in `tools/` are outside CI's ruff scope (see Project Constraints), so a new tool would ship un-linted. Put the parser as a module-level helper inside the test file, and inject the fixture path via a `monkeypatch.setattr` on a module-level path constant rather than an env var. |
| `frozenset` allow-set | `dict[str, str]` token → provenance-reason | The dict costs nothing and lets D-01's refusal reasons name *why* a part is refused with per-token provenance (`"Atmel AT28C line — doc0270"` vs `"lockable-proms.md §17"`), which the discretion note asks for. **Recommendation: `dict[str, str]`**, frozen behind a `MappingProxyType` or just a module constant with a comment. |
| Click sub-group (`dev sdp enable <chip>`) | `<chip>` argument + `click.Choice(["enable","disable"])` | The locked surface is `dev sdp <chip> <enable\|disable>`, chip first. A sub-group forces `dev sdp enable <chip>`. **Recommendation: `click.Choice` argument** — it is the only form that matches the locked surface. |

**Installation:** none. No `pip install` step in this phase.

## Package Legitimacy Audit

**Not applicable — this phase installs zero external packages.** No `pip install`, no `pyproject.toml` dependency change, no new third-party import. Every module used (`click`, `rich`, `pytest`, `re`, `json`, `os`, `pathlib`, `unittest.mock`) is either already a pinned dependency exercised throughout the tree or stdlib. The v1.21 locked anti-feature "no new third-party Python dependencies" still binds.

**Packages removed due to [SLOP] verdict:** none.
**Packages flagged as suspicious [SUS]:** none.

## Architecture Patterns

### System Architecture Diagram

```
                      user types: firestarter dev sdp at28c256 enable
                                            │
                                            ▼
                        ┌───────────────────────────────────────┐
                        │  cli_handlers.dev_sdp (Click handler) │
                        └───────────────────────────────────────┘
                                            │
        GATE 1 ── absent-chip hard-fail ────┤  if not app.db.get_eprom(chip): raise ChipNotFoundError
                  (SAFE-04, keyed on        │      ── NEVER a resolve_chip refusal ──
                   get_eprom emptiness)     │
                                            ▼
        GATE 2 ── capability refusal ───────┤  sdp_capability(chip, app.db) -> (bool, reason)
                  (HOST-04 / D-01..D-03)    │      reads get_eprom()["name"] + ["protocol-id"]
                                            │      ── NOT resolve_chip's dict (F-06) ──
                                            ▼
        GATE 3 ── support-status refusal ───┤  resolve_chip(chip, db) -> programmer dict
                  (ChipNotImplementedError) │      9 of 84 0x0D parts are adapter-required
                                            ▼
        GATE 4 ── consent ──────────────────┤  interactive? Confirm.ask  |  off-TTY & no -y? refuse
                  (D-05/D-06/D-07)          │
                                            ▼
                     ┌──────────────────────────────────────────────┐
                     │ EpromOperator.sdp_lock / sdp_unlock          │
                     │  (erase_eprom-shaped: _operation_context +   │
                     │   bare _run_state_machine, no main handler)  │
                     └──────────────────────────────────────────────┘
                                            │
                          ── PORT OPENS HERE, not before ──
                                            ▼
                     _setup_operation: COMMAND_NAMES[cmd]  ← KeyError without HOST-03
                                       find_and_connect(command_dict)
                                            │
                                            ▼  serial, 250000 baud
                     ┌──────────────────────────────────────────────┐
                     │ firmware: loop() switch → is_memory_cmd()    │
                     │  → configure_memory → configure_eeprom28c    │
                     │  cmd 9 = unlock, cmd 10 = lock  (READ-ONLY)  │
                     └──────────────────────────────────────────────┘
                                            │
                    frames back: 0x5E/0x5F (unlock) or 0x60/0x61 (lock),
                                 0x87 on t_BLC overrun, or ERROR ids
                                            ▼
                     _read_and_parse_lines ── GATE-1.8d RING-FENCED, do not touch
                          │
                          ├─→ _decode_id_frame  ← the OVERRIDE SEAM (Phase 55 precedent)
                          │        │              ← record observed ids here (D-15's 0x86)
                          │        ▼
                          │   codec.decode_id_frame → CATALOG lookup → severity band
                          │        │                   unknown id → warn + DROP frame
                          │        ▼
                          ├─→ Response(type=severity_label, message=text, id=msg_id)
                          │        │
                          ├─→ _log_rurp_feedback ── D-09's target: ERROR→ERROR, WARN→WARNING,
                          │                          EVERYTHING ELSE → DEBUG (invisible)
                          ▼
                     get_response() ── FILTERS OUT "INFO" and "DEBUG" entirely
                          │             so the operation layer never sees an INFO frame
                          ▼
                     _execute_phase / _main_phase_simple  →  (is_ok, final_msg)
                          │
                          ▼
                     host summary line (D-10) + exit 0/1 (D-11)


                   write --skip-sdp-unlock  ──►  _build_op_flags(skip_sdp_unlock=...)
                                                        │
                                                 build_flags(..., *, skip_sdp_unlock=False)
                                                        │  D-04: if refused by allow-set,
                                                        │  host force-sets the bit + reports
                                                        ▼
                                                 flags |= FLAG_SKIP_SDP_UNLOCK (0x100)
```

### Recommended Project Structure

```
firestarter_app/
├── firestarter/
│   ├── sdp_capability.py       # NEW — allow-set + pure predicate (D-03)
│   ├── constants.py            # + COMMAND_SDP_UNLOCK/LOCK, COMMAND_NAMES entries, FLAG_SKIP_SDP_UNLOCK
│   ├── cli_handlers.py         # + dev_sdp handler; write's --skip-sdp-unlock; _build_op_flags kwarg
│   ├── eprom_operations.py     # + build_flags kwarg; sdp_lock/sdp_unlock; write-path auto-set
│   └── serial_comm.py          # _log_rurp_feedback mapping (D-09); _decode_id_frame ack record (D-15)
└── tests/
    ├── test_sdp_capability.py          # NEW — allow-set exhaustiveness + shape leg + non-vacuity
    ├── test_revision_constants_parity.py  # rebuilt as a real header-parsing two-way gate (D-12/D-13)
    ├── fixtures/planted_constants_drift.h # NEW — the planted-violation header
    ├── test_dev_sdp_cmd.py             # NEW — gate ordering, off-TTY, no-port-opened
    ├── test_serial_comm.py             # + D-09 mapping test
    └── test_eprom_operations.py        # + D-15 missing-ack test, payload-free op shape
```

### Pattern 1: The payload-free operator method (`erase_eprom`)

**What:** `_operation_context(...)` + a bare `_run_state_machine(op_name)` with no `main_phase_handler`.
**When to use:** Both `CMD_SDP_UNLOCK` and `CMD_SDP_LOCK`.

```python
# Source: firestarter_app/firestarter/eprom_operations.py:1628-1651 (erase_eprom, verbatim shape)
def erase_eprom(self, eprom_name, eprom_data_dict, operation_flags=0, address_str=None) -> bool:
    with self._operation_context(
        eprom_name, eprom_data_dict, COMMAND_ERASE, operation_flags, address_str,
    ) as (cmd_data, _, op_name):
        if not cmd_data:
            return False
        logger.info(f"Erasing EPROM {eprom_name.upper()}")
        start_time = time.time()
        is_ok, final_msg = self._run_state_machine(op_name)   # ← no main handler
        if is_ok:
            logger.info(f"Erase for {eprom_name.upper()} successful (...). {final_msg or ''}")
        return is_ok
```

**Confirmed for the SDP commands** (all read this session):

- `_run_state_machine` with `main_phase_handler=None` falls to `_main_phase_simple` (`:415-417`), which loops on `get_response()` until it sees a `MAIN` frame. No `DONE` round-trip, no `#` data frame — exactly what Phase 119 D-13 / RESEARCH F-T describe.
- INIT and END frame pairs still occur (119 corrected the "NULL init/end skips the phases" reading). `_execute_phase("INIT", ...)` and `_execute_phase("END", ...)` both run and both `send_ack()`. `erase_eprom`'s shape already survives that.
- Nothing in `_setup_operation` breaks on a payload-free command. The one dependency is `COMMAND_NAMES[cmd]` at `:301` and again at `:377` — **two** call sites, both `KeyError` without the name entry. `cmd == COMMAND_READ and size` (`:321`) is not reached. `address` is optional. `command_dict["flags"] = eprom_data_dict.get("flags", 0) | operation_flags` (`:310`) ORs the DB-derived `FLAG_CAN_ERASE` (`0x02`) in for all 84 `0x0D` parts — firmware-inert on this protocol per `database.py:592-593`, so harmless, but the emitted `flags` value on the wire will be `2` not `0`. Worth pinning in a test so nobody later reads `flags: 2` as a bug.

### Pattern 2: The pre-wire refusal with a spoken reason

**What:** Refuse before `_operation_context` opens the port, log a `logger.warning` naming the reason, return `False`.
**When to use:** As the *shape* register for D-01's reason strings — but **not** as the data-access pattern (see Anti-Pattern 1).

```python
# Source: firestarter_app/firestarter/eprom_operations.py:1661-1676 (check_eprom_blank short-circuit)
etype = eprom_data_dict.get("electrical-type", "")
proto = eprom_data_dict.get("protocol-id", 0)
if etype in ("SRAM", "FRAM") or proto in self._SRAM_PROTO_IDS:
    logger.warning(
        f"Blank check is not applicable to {eprom_name.upper()} "
        f"(electrical type: {etype or 'unknown'}, protocol: 0x{proto:02X}). "
        "SRAM/FRAM are volatile or byte-rewritable — they have no "
        "factory-blank state and the firmware has no blank-check op for them."
    )
    return False
```

The wording register to match: name the chip, name the observed field values, state the mechanism, state the consequence. Reuse that four-part shape for the SDP refusal reasons.

### Pattern 3: The fail-closed firmware-source reader with a planted-violation fixture

**What:** Blank comment spans length-and-line-preservingly, then scan; a path that does not exist or a target that cannot be resolved is an ERROR, never a silent pass; an env/attr seam points the reader at a deliberately-violating fixture.

```python
# Source: firestarter_app/tools/check_is_memory_cmd_no_ifdef.py:159-199 (_strip_comments, verbatim)
def _strip_comments(text: str) -> str:
    out, i, n = [], 0, len(text)
    while i < n:
        two = text[i:i + 2]
        if two == "//":
            j = text.find("\n", i);  j = n if j == -1 else j
            out.append(" " * (j - i));  i = j
        elif two == "/*":
            j = text.find("*/", i + 2)
            j = n if j == -1 else j + 2
            out.append("".join(c if c == "\n" else " " for c in text[i:j]));  i = j
        else:
            out.append(text[i]);  i += 1
    return "".join(out)
```

`_strip_comments` is **load-bearing, not hygiene**, for D-12 specifically: `firestarter.h`'s comment block above `CMD_SDP_UNLOCK` (lines 50-60) literally contains the strings `constants.py CMD_SDP_*`, `COMMAND_NAMES`, and `#ifdef DEV_TOOLS`, and the block above `FLAG_SKIP_SDP_UNLOCK` (`:141-147`) contains `--skip-sdp-unlock / constants.py`. A naive scan over uncleaned text will match those.

### Anti-Patterns to Avoid

- **Reading `protocol-id` / `electrical-type` / part number from a `resolve_chip` dict.** They are not there. This is F-06, the phase's highest-severity finding — it is how `check_eprom_blank`'s short-circuit became vacuous. Any predicate that does this will silently return the fail-open branch of whatever default it uses.
- **Copying `dev test`'s gate order verbatim.** In-tree, `dev test` runs the confirm at `:1836-1842` and the absent-chip hard-fail at `:1844-1850` — confirm **before** absent. D-08 requires the reverse. Copy the *mechanisms*, re-order the *sequence*, and add a test that would catch the wrong order.
- **Asserting only an exit code for a refusal test.** The known false-green trap. A `ChipNotFoundError` and a capability refusal and a support-status refusal all exit non-zero; only "no port was opened" distinguishes gate order from gate presence.
- **A pinout-derived or naming-derived allow-set.** Both provably fail on real data (F-03).
- **A bare `mypy` or bare `ruff check .` as the phase gate.** Both are red at baseline for reasons unrelated to this phase.
- **Editing `messages.py` by hand.** It is codegen output and the CI drift gate regenerates and `git diff --exit-code`s it.
- **Editing `firestarter/` anything.** Zero firmware changes. The firmware working tree must be byte-clean at phase end (verified clean at `0048b3d` this session).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Chip-name → DB entry, alias-aware | A token splitter in `sdp_capability.py` | `db.get_eprom_config(name)` / `db.get_eprom(name)` | `database.py:465-504` already handles comma-split aliases, `(...)` mode-annotation stripping, and case folding — and it is the exact resolution the rest of the pipeline uses, so a second implementation would disagree on the collision cases |
| Reading the shipped DB for an invariant test | A loader wrapper | `json.loads(_DB_FILE.read_text())` + a `_select_0x0d_chips` helper | `tests/test_sdp_db_invariant.py:29-58` — measures the shipped data, not the loader's interpretation, and its no-skip-marker reasoning is documented |
| C-comment-safe source scanning | A regex with `(?<!//)` lookbehinds | `check_is_memory_cmd_no_ifdef.py:_strip_comments` | Length- and line-preserving, so every computed line number still maps 1:1 |
| Observing a decoded frame id without touching the read loop | A new hook in `_read_and_parse_lines` | The `_decode_id_frame` override seam | GATE-1.8d ring-fences the read loop; Phase 55's `firmware_max_chunk` is the exact precedent and its comment says so (`serial_comm.py:260-261`) |
| Firmware-version gating | A version comparator | Nothing — D-16 forbids a floor; use D-14's `MSG_ERR_UNKNOWN_CMD` mapping and D-15's ack | The host structurally cannot see the `b11`/`b12` suffix (F-120-04) |
| A TTY check that survives `CliRunner` | `sys.stdin.isatty()` inline | `_is_interactive()` at `cli_handlers.py:1717-1724` | `CliRunner.invoke` replaces `sys.stdin`; the indirection exists precisely so tests can patch the function |

**Key insight:** every "don't hand-roll" here is a *disagreement risk*, not a complexity risk. The host already has exactly one implementation of chip-name resolution, one comment stripper, and one frame-observation seam. A second copy of any of them in this phase would be a place where the capability refusal and the operation it guards could reach different conclusions about the same chip.

## Runtime State Inventory

Not a rename/refactor/migration phase in the string-replacement sense, but it *adds* a runtime-consulted table, so the same discipline is applied to what it must be consistent with:

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | **`~/.firestarter/database.json`** — merged into the live DB at `database.py:187-194` via `_merge_databases`, invisible to CI. A user-added `algorithm: 13` entry reaches the predicate at runtime. This is the fact that forced D-02's runtime allow-set. `skip_local_override=True` is the test seam. | Code: the predicate must be a runtime check; the CI gate is the *completeness* proof over the shipped DB only. Both are needed; neither substitutes. |
| Live service config | None — no external service holds SDP state. Protection state itself is unreadable, which is the whole premise of D-10/D-11. | None |
| OS-registered state | None. `dev sdp` registers nothing. | None |
| Secrets/env vars | `FIRESTARTER_CONFIG_DIR` (honoured by `get_config_dir()`, used by `dev test`'s report path and monkeypatched in `tests/test_dev_test_cmd.py:65`). `dev sdp` writes no report, so it needs no isolation — but if a plan adds one, isolate the same way. | None for the locked scope |
| Build artifacts / installed packages | `firestarter_app` is installed editable; `firestarter/messages.py` is codegen output guarded by CI drift gates; `firestarter/data/chip_database.json` is `build_db.py` output guarded by `diff_db.py` identity (GATE-03) and CLOSE-01's 84-count. **None may change.** | Verify at phase end: `git -C /workspaces/firestarter_app diff --stat -- firestarter/data/ firestarter/messages.py` empty, and `git -C /workspaces/firestarter status --porcelain` empty |

## Common Pitfalls

### Pitfall 1: `resolve_chip`'s dict silently lacks the fields a capability predicate wants — F-06

**What goes wrong:** `sdp_capability(eprom_data_dict)` reads `eprom_data_dict["protocol-id"]`, gets the `0` default on every production call, and either refuses everything (if `0 != 13` → refuse) or, worse, is written as `if proto == 13 and token not in ALLOW: refuse` and therefore **never refuses anything**.

**Why it happens:** `resolve_chip` ends with `db.convert_to_programmer(full)`, and `convert_to_programmer` (`database.py:535-597`) constructs a *new* dict with exactly `memory-size`, `algorithm`, `pin-count`, `vpp_mv`, `pulse-delay`, optionally `chip-id`, optionally `bus-config`, optionally `page-size`, and `flags`. `protocol-id` is renamed to `algorithm`; `electrical-type` and `name` are dropped entirely.

Executed this session:
```
resolve_chip('at28c256', db=EpromDatabase(skip_local_override=True))
→ keys: ['algorithm', 'chip-id', 'flags', 'memory-size', 'pin-count', 'pulse-delay', 'vpp_mv']  (+ bus-config)
→ {'memory-size': 32768, 'algorithm': 13, 'pin-count': 28, 'vpp_mv': 12000,
   'pulse-delay': 0, 'chip-id': 0, 'flags': 2}
```

**The proof that this is a live in-tree defect, not a hypothetical.** `check_eprom_blank`'s SRAM/FRAM short-circuit reads exactly those two absent keys. Executed against a real SRAM part (`DS1220(RW)`, `protocol-id 40`, `electrical-type "SRAM"` in the *full* dict):
```
d = resolve_chip('DS1220(RW)')
d.get('electrical-type')  → ''      (absent)
d.get('protocol-id')      → 0       (absent)
short-circuit would fire? → False
```
Both production callers pass this dict: `blank` at `cli_handlers.py:576-578`, and `chip_test.run_plan` via `_resolve_or_none` → `resolve_chip` at `chip_test.py:505` → `operator.check_eprom_blank(name, eprom_data)` at `:737`. **So the `_SRAM_PROTO_IDS` short-circuit is vacuous in production.** PROJECT.md's SIXTH CORRECTION item 6 keeps the right *disposition* (KEEP, do not delete) but its stated *reason* — "fires **before** any firmware command is issued … produces a materially better user-facing message" — is false today. Record this as a correction; do not fix it (out of scope), and do not delete the code.

The project already knows the shape of this problem in one place: `chip_test.py:628-637` documents that `_dispatch_multi_run`'s dict "does NOT carry `electrical-type` — only `derive_plan`'s guard-bypassing `full` dict does" and falls back to `algorithm == 0x0B`. That comment is the in-tree evidence trail.

**How to avoid:** signature `sdp_capability(chip_name: str, db: EpromDatabase) -> tuple[bool, str]`, reading `db.get_eprom(chip_name)` and keying on that dict's `name` (the alias-joined `part_number`) and `protocol-id`. It stays pure in D-03's sense — no serial, no Click, no loader construction (the DB is injected) — and it is the only shape that has the part number available at all.

**Warning signs:** a test that constructs a hand-written dict containing `"protocol-id"` or `"electrical-type"` and passes. `tests/test_chip_test.py` has eleven such constructions (`:393`, `:405`, `:1150`, …) — they assert on `full[...]`, which is correct there, but the same habit in a `sdp_capability` test would prove a shape production never produces. **Every `sdp_capability` test must obtain its dict from a real `EpromDatabase(skip_local_override=True)`, never from a literal.**

### Pitfall 2: `dev test`'s gate order is the reverse of D-08's — F-05

**What goes wrong:** the handler is copied verbatim, so the confirm prompt fires before the absent-chip check, and a user who typos a chip name is asked to consent to mutating a chip that does not exist.

**Why it happens:** `cli_handlers.py:1826-1847` runs, in order: `_is_interactive()` → `Confirm.ask` gate → `if not app.db.get_eprom(chip): raise ChipNotFoundError`. That order is correct *there* (the confirm guards `--destructive`, which is only meaningful once), and D-08 deliberately reverses it for `dev sdp` so "a user is never asked to consent to something that is then refused."

**How to avoid:** write the four gates in D-08's order and add a test that patches `Confirm.ask` and asserts `mock_confirm.ask.assert_not_called()` for an absent chip, a refused-capability chip, and an `adapter-required` chip.

**Warning signs:** a passing test suite where every refusal test only checks `result.exit_code != 0`.

### Pitfall 3: A naive `CMD_X → COMMAND_X` name map breaks the parity gate on real data — F-10

**What goes wrong:** the two-way gate reports `COMMAND_DEV_REGISTER missing on the host side` and the author "fixes" it by renaming the host constant, breaking every caller.

**Why it happens:** the two sides genuinely disagree on one name. Firmware: `#define CMD_DEV_REGISTER 8` (`firestarter.h:44`, singular). Host: `COMMAND_DEV_REGISTERS = 8` (`constants.py:64`, plural). Verified by grep on both sides this session.

**How to avoid:** the exemption list must be a name-*pair* mapping, not a set of names to skip. Three exemption classes, all explicitly enumerated:

| Firmware define | Line | Host counterpart | Exemption reason |
|---|---|---|---|
| `CMD_IDLE 0` | `firestarter.h:34` | none | Firmware-internal state; no shipped host path emits cmd 0 (Phase 119 D-01 / RESEARCH F-B2) |
| `CMD_DEV_ADDRESS 7` | `:43` (inside `#ifdef DEV_TOOLS`) | `COMMAND_DEV_ADDRESS = 7` | Conditionally compiled; the existing test already documents this at `test_revision_constants_parity.py:110-113` |
| `CMD_DEV_REGISTER 8` | `:44` (inside `#ifdef DEV_TOOLS`) | `COMMAND_DEV_REGISTERS = 8` | Conditionally compiled **and** name-mismatched (singular vs plural) |
| `CMD_FRAME_MAX DATA_BUFFER_SIZE` | `:24` | `CMD_FRAME_MAX = 512` | `CMD_`-prefixed but not a command code, and its value is a macro not a literal — already has its own dedicated gate at `test_revision_constants_parity.py:189-213` (D-07 acceptance) |

**Warning signs:** a regex of the form `#define CMD_(\w+)\s+(\d+|0x[0-9a-fA-F]+)` that silently skips `CMD_FRAME_MAX` because its value is non-numeric. That is a *silent* exemption — the exact hollowness D-12 exists to remove. **Extract every `#define CMD_\w+` and require each to be either mapped or in the enumerated exemption table**; an unrecognised `CMD_*` should fail the gate closed.

### Pitfall 4: `get_response()` filters INFO frames out before the operation layer sees them — F-12

**What goes wrong:** a plan tries to read the firmware's `0x5F`/`0x61` duration or the `0x5E`/`0x60` start line at the operation layer to build the host summary, and finds nothing.

**Why it happens:** `serial_comm.py:418-431` — `get_response()` iterates `_read_and_parse_lines` and returns only responses whose `type` is **not** in `NON_RESPONSE_PREFIXES = ["INFO", "DEBUG"]` (`:89`). Every INFO-band frame is consumed, logged by `_log_rurp_feedback`, and dropped. `_execute_phase` and `_main_phase_simple` call `get_response()`, so nothing above the transport ever sees an INFO frame.

**How to avoid:** this is exactly why D-10 is shaped the way it is. The firmware's duration line reaches the user *only* through `_log_rurp_feedback` (which D-09 promotes to INFO level), and the host's own summary line is produced independently by the handler. There is no parsing, no duplication, no drift — and the host **cannot** accidentally learn the duration. Do not try to plumb one.

**Warning signs:** a plan task phrased as "extract the microseconds from the frame". If that appears, it contradicts D-10 and is also mechanically impossible above the transport layer without touching the ring-fenced loop.

### Pitfall 5: WARN frames reach the operation layer but are discarded there — the D-15 seam question

**What goes wrong:** the `0x86` ack observation is placed in `_handle_progress_response`, a helper shared by every operation and every phase, widening the change surface for a single-purpose check.

**Why it happens:** `WARN` is *not* in `NON_RESPONSE_PREFIXES`, so a `0x86` frame is returned by `get_response()`. In `_execute_phase`'s loop (`:442-460`) it is neither the phase-terminator nor an `ERROR`, so it falls to `_handle_progress_response`, which does `logger.warning(f"Programmer warning: {response.message}")` (`:487-488`) and keeps nothing.

**How to avoid — two viable seams, both non-ring-fenced:**

1. **`_decode_id_frame` (recommended).** `serial_comm.py:249-280` is already an override wrapper whose docstring says *"The GATE-1.8d ring-fenced `_read_and_parse_lines` body is not touched — only this override seam is used."* Phase 55 records `firmware_max_chunk` here from `MSG_OK_READY`. Recording `0x86` into a per-connection `seen_message_ids: set[int]` is the identical move, with an in-tree precedent and a docstring that already licenses it.
2. **`Response.id`.** `serial_comm.py:394-399` populates `id=decoded.id` on the `Response`, so `_handle_progress_response` (or a narrower check inside `write_eprom`'s phase handling) could inspect `response.id == MSG_WARN_SDP_UNLOCK_SKIPPED`. Correct but wider.

**Recommendation:** seam 1, read by `write_eprom` after `_run_state_machine` returns, gated on "the flag was set on this invocation". Note the honest limitation D-15 already requires stating in-source: the unlock has already been emitted by the time the host reports it was not honoured.

### Pitfall 6: `build_flags`' signature is pinned by a characterization test

**What goes wrong:** `skip_sdp_unlock` is added positionally and `tests/test_bug_characterization.py`'s BUG-1 contract goes red, or worse, a caller elsewhere passes positionally into the wrong slot.

**Why it happens:** `build_flags(blank_check=True, force=False, vpe_as_vpp=False, verbose=False, skip_erase=False)` at `eprom_operations.py:168-170` is called **positionally** from two places: `build_arg_flags` at `cli_handlers.py:184-190` and `_build_op_flags` at `:275` — both pass the first four positionally and `skip_erase=` by keyword.

**How to avoid:** D-19 already mandates keyword-only with a `False` default. Add it after a `*`. Re-run `tests/test_bug_characterization.py` explicitly as named task work.

### Pitfall 7: The vacuous-path trap has two distinct instances in this milestone's records

**What goes wrong:** a gate row is marked PASS because a `git diff -- <path>` returned empty against a path that does not exist.

**Why it happens:** PROJECT.md's **FOURTH CORRECTION item 5** warns: *"the ROADMAP's `flash_utils.{h,cpp}` shorthand does not match the real paths — a `git diff -- src/flash_utils.h` check passes vacuously."* The real paths are `firestarter/include/flash_utils.h` and `firestarter/src/proms/flash_utils.cpp`.

**Disambiguation the planner needs:** this is **PROJECT.md FOURTH CORRECTION item 5**, *not* row 5 of the nine-row CORRECTION-4 table (row 5 is `tools/gen_sdp_bus_config.py`). The two "item 5"s are unrelated. Since Phase 120 edits no firmware, the honest proof is not a path-scoped `git diff` at all but `git -C /workspaces/firestarter status --porcelain` being **empty** — which subsumes every path and cannot pass vacuously.

## Code Examples

### Recommended `sdp_capability` signature and body shape

```python
# firestarter/sdp_capability.py  (NEW — D-03)
# Signature drives off F-06: get_eprom()'s FULL dict, never resolve_chip's
# programmer dict, which carries neither "protocol-id" nor the part number.

_ALGORITHM_0X0D = 13   # mirrors tests/test_sdp_db_invariant.py:37

# token -> provenance/reason string (Claude's-discretion container choice)
_SDP_CAPABLE_TOKENS: dict[str, str] = {
    "AT28C256": "Atmel AT28C parallel-EEPROM line — Microchip DS20006386B",
    "AT28C64B": "Atmel AT28C64B — Atmel doc0270 0270L-PEEPR-2/09 §19 note 2",
    # ... 63 tokens total, see the Allow-Set table below
}

def sdp_capability(chip_name: str, db) -> tuple[bool, str]:
    """Return (allowed, reason). Pure: no serial, no Click, no loader construction."""
    full = db.get_eprom(chip_name)
    if not full:
        return False, f"{chip_name}: not found in database"
    if full.get("protocol-id", 0) != _ALGORITHM_0X0D:
        return False, (
            f"{chip_name}: SDP lock/unlock applies only to protocol 0x0D "
            f"parallel EEPROMs (this part is protocol "
            f"0x{full.get('protocol-id', 0):02X})"
        )
    # Whole-entry unanimity (see F-02): every alias token in the resolved
    # entry must be in the allow-set, else fail closed.
    tokens = [t.strip().upper() for t in (full.get("name") or "").split(",")]
    unknown = [t for t in tokens if t not in _SDP_CAPABLE_TOKENS]
    if unknown:
        return False, (
            f"{chip_name}: not on the curated SDP-capable list "
            f"(unrecognised or pre-SDP generation: {', '.join(unknown)}) — "
            "refused fail-closed because the SDP command sequence is not inert "
            "on a part without an SDP command decoder: its bytes are stored as data"
        )
    return True, _SDP_CAPABLE_TOKENS[tokens[0]]
```

Note the reason strings satisfy the discretion requirement to name *why* (pre-SDP generation / FRAM / not `0x0D` / unrecognised) and match Pattern 2's four-part wording register. FRAM parts fall out of the `unknown` branch; if a distinct FRAM message is wanted, a small explicit `_FRAM_TOKENS` pre-check placed before the allow-set lookup gives it without weakening the fail-closed default.

### The D-12 gate's define extractor (sketch)

```python
# tests/test_revision_constants_parity.py  (rebuilt)
# Reuse check_is_memory_cmd_no_ifdef.py's _strip_comments; do NOT reuse its
# brace matcher (there is no function body to match — these are file-scope defines).

_DEFINE_RE = re.compile(r"^[ \t]*#[ \t]*define[ \t]+((?:CMD|FLAG)_[A-Z0-9_]+)[ \t]+(\S+)", re.M)

# Explicit, enumerated exemptions — never a pattern skip (D-12).
_EXEMPT: dict[str, str | None] = {
    "CMD_IDLE": None,                     # firmware-internal state, no host constant
    "CMD_FRAME_MAX": "CMD_FRAME_MAX",     # not a command code; own gate (D-07)
    "CMD_DEV_ADDRESS": "COMMAND_DEV_ADDRESS",    # #ifdef DEV_TOOLS
    "CMD_DEV_REGISTER": "COMMAND_DEV_REGISTERS", # #ifdef DEV_TOOLS + name mismatch
}

def _host_name(fw_name: str) -> str | None:
    if fw_name in _EXEMPT:
        return _EXEMPT[fw_name]
    if fw_name.startswith("CMD_"):
        return "COMMAND_" + fw_name[len("CMD_"):]
    return fw_name      # FLAG_* names are identical on both sides
```

**Stronger option worth the planner's consideration:** track `#if/#ifdef/#endif` nesting depth while scanning, and assert that the set of defines found at depth > 0 equals exactly `{CMD_DEV_ADDRESS, CMD_DEV_REGISTER}`. That turns "these two are conditional" from an assumption in a comment into a machine-checked fact, and it would have caught Phase 119's addition of `CMD_SDP_UNLOCK`/`CMD_SDP_LOCK` *outside* the `#ifdef` as a deliberate choice rather than luck. Cheap; recommended.

### The exhaustiveness gate's two legs

```python
# tests/test_sdp_capability.py  (NEW) — follows test_sdp_db_invariant.py's shape verbatim:
#   no skip marker (reads only the packaged DB), shared helpers, explicit non-vacuity case.

def test_allow_and_refuse_partition_covers_exactly_the_84_0x0d_entries():
    db = json.loads(_DB_FILE.read_text(encoding="utf-8"))
    selected = _select_0x0d_chips(db)          # reuse the existing helper's shape
    assert len(selected) == 84
    allowed, refused = _partition(selected)
    assert len(allowed) + len(refused) == 84
    assert len(allowed) == 37 and len(refused) == 47   # pin the curated split

def test_predicate_never_reads_a_programmer_dict_shape():
    """SHAPE LEG (F-06): prove the predicate is not silently vacuous.

    A resolve_chip() dict carries no 'protocol-id' and no 'name'. If the
    predicate ever accepts one and returns allowed=True, it has become the
    _SRAM_PROTO_IDS-style vacuous check this gate exists to prevent."""
    db = EpromDatabase(skip_local_override=True)
    prog = resolve_chip("at28c256", db=db)
    assert "protocol-id" not in prog and "name" not in prog   # pins the real shape
    allowed, reason = sdp_capability("at28c256", db)          # name-keyed, not dict-keyed
    assert allowed is True and reason
```

## Detailed Findings

### F-01 — The concrete allow / refuse partition, summing to exactly 84

Enumerated from `firestarter/data/chip_database.json` this session (84 entries with `programming.algorithm == 13`, matching `test_sdp_db_invariant.py`'s pinned count). Pinout distribution confirms CONTEXT: `DIP28_28C64` 35, `DIP24_2816` 19, `DIP32_28C512_EEPROM` 18, `DIP28_28C256` 12. Electrical type: 66 `EEPROM` / 18 `Flash/EEPROM`. Support status: 9 `adapter-required`, 75 `supported`.

**Recommended partition: 37 ALLOW / 47 REFUSE = 84.**

#### ALLOW — 37 entries, 63 tokens

| Confidence | Rationale | n | Entries (`MANUFACTURER/part_number`) |
|---|---|---|---|
| **HIGH** | Atmel AT28C parallel-EEPROM line; SDP is the milestone's own datasheet-of-record family (Atmel doc0270 `0270L–PEEPR–2/09` §19 note 2; Microchip DS20006432B §6.6.2/§6.18; DS20006386B; AT28C010 doc0353 `0353G–PEEPR–10/06` §19) | 16 | `ATMEL/AT28C256,AT28C256E,AT28C256F,AT28HC256,AT28HC256E,AT28HC256F,AT28HC256L` · `ATMEL/AT28C64,AT28C64B(Non-Standard),AT28HC64,AT28HC64L` · `ATMEL/AT28C64B,AT28HC64B,AT28HC64BF` · `ATMEL/AT28C64E,AT28C64F` · `ATMEL/AT28C17` · `ATMEL/AT28C17E,AT28C17F` · `ATMEL/AT28C010,AT28C010E` · `ATMEL/AT28C040,AT28C040E` · `ATMEL/AT28LV010` · `ATMEL/AT28MC010` · `ATMEL/AT28MC020` · `ATMEL/AT28MC040` · `ATMEL/AT28BV64,AT28LV64` · `ATMEL/AT28BV64B,AT28LV64B` · `ATMEL/AT28BV256,AT28LV256` · `ATMEL/AT28PC64,AT28PC64E` |
| **MEDIUM** | Second source explicitly named as SDP-capable in the in-tree `doc/lockable-proms.md` §17 table ("Microchip 28C64 / 28C256", "Xicor X28C64 / X28C256", "Catalyst CAT28C64 / CAT28C256"), extended along the same family naming to the 1M/2M/4M members | 21 | `MICROCHIP memory/28C256,28C256F` · `MICROCHIP memory/28C64A` · `MICROCHIP memory/28C64AF` · `MICROCHIP memory/28C64B` · `MICROCHIP memory/28LV64A` · `MICROCHIP memory/28C17A` · `MICROCHIP memory/28C17AF` · `XICOR/X28256,X28C256` · `XICOR/X28C64,X28HC64` · `XICOR/X28C64(NonStandard),X28HC64(NonStandard)` · `XICOR/X28C010` · `CATALYST(CSI)/CAT28C256,CAT28C257` · `CATALYST(CSI)/CAT28LV256` · `CATALYST(CSI)/CAT28C64A,CAT28C65` · `CATALYST(CSI)/CAT28C64B` · `CATALYST(CSI)/CAT28LV64,CAT28LV65` · `CATALYST(CSI)/CAT28C17A` · `CATALYST(CSI)/CAT28C010` · `CATALYST(CSI)/CAT28C020` · `CATALYST(CSI)/CAT28C040` · `CATALYST(CSI)/CAT28C512` |

#### REFUSE — 47 entries

| Confidence | Rationale | n | Entries |
|---|---|---|---|
| **HIGH** | FRAM (ferroelectric) — no EEPROM SDP command decoder exists on these parts at all | 2 | `CYPRESS/FM28V020` · `FUJITSU/MB85R256H` |
| **HIGH** | Pre-SDP first generation, HOST-04's own named class, token-enumerated (spans two pinouts — see F-03) | 8 | `MICROCHIP memory/2804` · `MICROCHIP memory/2816` · **`MICROCHIP memory/2817`** · `XICOR/X2804A,X2804AI` · `XICOR/X2816A` · `XICOR/X2816B,X2816C` · `EXEL/XL2804A` · `EXEL/XL2816A,XLE28C16A,XLS28C16A` |
| **MEDIUM — deliberate over-refusal** | Remaining `DIP24_2816` 512 B / 2 KB generation. No datasheet-of-record exists for any of them; SDP-F7 (magic-address verification) is still UNVERIFIED; SDP-F8 records that all 19 have `static_high_mask == 0` so VCC is not force-driven; and PROJECT.md's THIRD CORRECTION measured this pinout inhibited on the *opposite* two writes from the DIP28 pinouts. Highest-harm group under F-120-01. | 11 | `AMD/AM28C16A` · `ATMEL/AT28C04,AT28HC04` · `ATMEL/AT28C04E,AT28C04F` · `ATMEL/AT28C16,AT28HC16,AT28HC16L` · `ATMEL/AT28C16E,AT28C16F` · `CATALYST(CSI)/CAT28C16A,CAT28C16AI` · `EXEL/XLE28C16B,XLS28C16B` · `MICROCHIP memory/28C04A` · `MICROCHIP memory/28C04AF` · `MICROCHIP memory/28C16A` · `MICROCHIP memory/28C16AF` · `NEC/UPD28C04` |
| **LOW — fail-closed default** | No datasheet-of-record; not named in `doc/lockable-proms.md` §17; the project has never bench-touched any of them | 26 | `AMD/AM28C17A` · `AMD/AM28C64A,AM28C64AE,AM28C64B,AM28C64BE` · `HITACHI/HN58C256AP` · `NEC/UPD28C64` · `NEC/UPD28C256` · `SAMSUNG/KM28C64` · `SAMSUNG/KM28C64A,KM28C65A` · `SGS-THOMSON/M28C64,M28C64A` · `SGS-THOMSON/M28C64-xxW` · `SGS-THOMSON/M28010` · `ST/M28C64,M28C64A` · `ST/M28C64-xxW` · `ST/M28LV64` · `ST/M28256` · `ST/M28010` · `EXEL/XLE2865A,XLS2865A` · `EXEL/XLE28C64A,XLS28C64A` · `EXEL/XLE28C64B,XLS28C64B` · `EXEL/XLE28C256,XLS28C256` · `MAXWELL/28C010,28C010T,28C011,28C011T` · `WED/WE128K8` · `WED/WE256K8` · `WED/WE512K8` · `WED/WME128K8` · `XICOR/X2864AP` |

*(The 11 + 12 arithmetic: the "remaining `DIP24_2816`" row lists 12 entries; 12 + 7 pre-SDP-on-`DIP24_2816` = 19, the full pinout group. `2817` is the eighth pre-SDP entry and sits on `DIP28_28C64`. Totals: 2 + 8 + 12 + 25 = 47. ALLOW 37 + REFUSE 47 = 84. The per-row counts above should be recomputed by the plan's own script as the authoritative arithmetic — the point of the machine-checked gate is that the numbers are asserted, not typed.)*

#### Named judgement calls, each an operator-decidable knob

1. **`XICOR/X2864AP` → REFUSE.** Follows the pre-SDP `X28xxA`-without-`C` naming pattern that `X2804A` / `X2816A` share. But `XICOR/X28256,X28C256` shows Xicor also used no-`C` spellings for genuinely-`C`-generation parts, so the naming signal is not reliable. Refused under fail-closed. **This is the single member most likely to be wrong in the over-refusing direction.** [ASSUMED]
2. **The Atmel `DIP24_2816` block (`AT28C04`/`AT28C04E,F`/`AT28C16`/`AT28C16E,F`) → REFUSE.** `doc/lockable-proms.md` §17 names "Atmel AT28C16 / 64 / 256" as SDP-capable, so this over-refuses a part the project's own doc says has SDP. Refused because the DB *splits* `AT28C16,AT28HC16,AT28HC16L` from `AT28C16E,AT28C16F` into separate entries — the upstream data believes there is a difference between them, we cannot see what it is (F-17), and the whole pinout group is the highest-harm group. **Second most likely to be wrong.** [ASSUMED]
3. **The `28C17`/`AT28C17`/`CAT28C17A` 2 KB 28-pin parts → ALLOW** while `2817` → REFUSE. The boundary is the `C` in the part number, the standard first-generation → SDP-generation marker. Defensible but not datasheet-confirmed. [ASSUMED]
4. **Catalyst 1M/2M/4M/512K (`CAT28C010/020/040/512`) → ALLOW** by family extension from §17's "CAT28C64 / CAT28C256". [ASSUMED]
5. **`ST` / `SGS-THOMSON M28C64` → REFUSE.** ST's M28C64 plausibly documents SDP, and this is 8 entries across the two manufacturer keys (which are duplicate second-source listings of the same 4 parts — see F-02's duplicate-token finding). Refused for lack of a citation. [ASSUMED]

**Own the cost of the fail-closed direction.** D-04 makes the allow-set load-bearing on `write`, not only on `dev sdp`: an over-refused part that is *genuinely* SDP-capable **and genuinely locked** will now get `FLAG_SKIP_SDP_UNLOCK` auto-set and its write will not land, where in `3.0.0b11` the unlock would have been attempted. That is the deliberate host-side divergence D-04 already tells the SUMMARY to state — but the planner should know its shape: over-refusal costs a working write on a locked part; under-refusal costs three stored bytes at truncated magic addresses. Both directions have a real cost. D-01 locks the direction; this research records the price.

**The authoritative axis exists upstream and is deliberately out of reach.** `.planning/notes/infoic-xml-protection-flags-research.md` records that minipro's `infoic.xml` carries bit 14 `MP_OFF_PROTECT_BEFORE` (`0x4000`) and bit 15 `MP_PROTECT_AFTER` (`0x8000`), and that `AT28C256 / AT28C64B` carry `0x0000c010` → b14=1/b15=1. The note's verdict is that these are *heuristics only* for readability, but for *SDP presence* b15 is described as "≈ SDP page-write family marker" — i.e. close to the metadata this allow-set is hand-curating. It is unusable here for three independent reasons: `tools/infoic.xml` is **not in the tree** (confirmed absent this session — it is an external input); decoding it would require a `build_db.py` change and a DB regeneration, which HOST-04 forbids and GATE-03's `diff_db.py` identity would catch; and the reviewed-not-folded todo `decode-infoic-flags-bits-14-15-protect-metadata.md` already routes that work to the `page_size` phase. **Record in the phase artifacts that the curated allow-set is expected to be partially superseded by decoded b14/b15 metadata in a later phase.** [CITED: `.planning/notes/infoic-xml-protection-flags-research.md`]

### F-02 — Token splitting and normalisation rules, measured

All from executing over the shipped DB this session:

| Property | Measured value | Consequence |
|---|---|---|
| Entries with `algorithm == 13` | **84** | Matches `test_sdp_db_invariant.py`'s pin |
| Total comma-separated tokens | **134** | The allow-set is a token table, not an entry table |
| Distinct tokens | **130** | 4 tokens appear on two entries each |
| Duplicate tokens | `M28010`, `M28C64`, `M28C64A`, `M28C64-xxW` | Each duplicated across `SGS-THOMSON` and `ST` — the same parts double-listed by second source. Same pinout, same algorithm, so a token-keyed allow-set treats both identically. **No cross-algorithm collision:** zero `0x0D` tokens appear on any non-`0x0D` entry. |
| Tokens with parentheticals | `AT28C64B(Non-Standard)`, `X28C64(NonStandard)`, `X28HC64(NonStandard)` | Note the **inconsistent spelling** — hyphen in one, none in the other two |
| Tokens with internal whitespace | none | No whitespace normalisation needed beyond `.strip()` |
| Tokens with lowercase characters | the three parentheticals plus `M28C64-xxW` (×2) | Case folding is required |

**Paren stripping creates collisions — do not strip in the allow-set key.** With `re.sub(r"\(.*?\)", "", t).strip().upper()` applied, 134 tokens collapse to 127 and produce seven within-`0x0D` collisions:

```
AT28C64B     -> ATMEL/AT28C64,AT28C64B(Non-Standard),... AND ATMEL/AT28C64B,AT28HC64B,AT28HC64BF
X28C64       -> XICOR/X28C64,X28HC64 AND XICOR/X28C64(NonStandard),X28HC64(NonStandard)
X28HC64      -> (same pair)
M28010       -> SGS-THOMSON/M28010 AND ST/M28010
M28C64       -> SGS-THOMSON/... AND ST/...
M28C64A      -> (same pair)
M28C64-XXW   -> (same pair)
```

All seven collisions are between entries that land on the *same* side of the recommended partition, so they are harmless **for this allow-set** — but they mean a paren-stripped key is not a function of one entry, so a future partition that split any collided pair would be ill-defined.

**Recommended rules:**

1. **Key on the exact token as it appears in `part_number`, `.strip()`ped and `.upper()`ed. Do not strip parentheticals.** This makes the allow-set key a faithful mirror of the DB text, so a `build_db.py` regeneration that changes a spelling makes the exhaustiveness gate go RED rather than silently re-partitioning.
2. **Never key on the user's typed string.** `db.get_eprom_config` already owns the user-facing normalisation — lowercase compare, exact-alias match, then paren-stripped-alias match, returning the **first** matching entry in DB iteration order (`database.py:488-504`). Because two entries can match the same paren-stripped alias, *which* entry a user reaches is already determined by that function; the predicate must therefore evaluate the **entry that resolution actually chose**, not the string the user typed. This is also what makes the collisions harmless.
3. **Evaluate all tokens of the resolved entry under a unanimity rule: any token not in the allow-set ⇒ refuse.** This is what makes `EXEL/XL2816A,XLE28C16A,XLS28C16A` refuse as a whole entry even though two of its three tokens look like `28C`-generation parts — CONTEXT names this entry for refusal and unanimity produces that answer mechanically, fail-closed.

**Which key answers "is this even `0x0D`":** read **`protocol-id`** from `db.get_eprom(name)`'s output (set at `database.py:395,420` from `programming.algorithm`). Do **not** read `algorithm` — that key exists only on `convert_to_programmer`'s output (`database.py:551`), which is `resolve_chip`'s return and which lacks the part number entirely (F-06). The two keys carry the same integer; only one of them coexists with the data the predicate also needs.

### F-03 — HOST-04's own named refuse-trio spans two pinouts, so no structural rule can express it

`MICROCHIP memory/2804` (512 B) and `MICROCHIP memory/2816` (2 KB) are on `pinout: DIP24_2816`. **`MICROCHIP memory/2817` (2 KB) is on `pinout: DIP28_28C64`.** [VERIFIED: enumerated from the shipped DB]

A pinout-keyed rule (`refuse all DIP24_2816`) therefore *permits* `2817`, one of the three parts HOST-04 names by name. A naming-keyed rule (`refuse bare 28xx without a C`) fails in the other direction on `XICOR/X28256,X28C256`, whose first token has no `C` but which is a genuine `X28C256`. **Neither a structural nor a lexical rule works.** This is independent confirmation of D-01's rejection of "a DB-derived structural rule" and its requirement that the allow-set be explicitly enumerated — and it is worth carrying into the plan as the reason a reviewer should not "simplify" the token table into a predicate.

### F-04 / F-05 — The `dev test` gate trio, and its ordering divergence from D-08

Read at `cli_handlers.py:1717-1847`:

| Element | Line | Reusable as-is? |
|---|---|---|
| `_is_interactive()` — `return sys.stdin.isatty()` in its own function *precisely* so tests can patch it (`CliRunner` replaces `sys.stdin`) | `:1719-1726` | **Yes, import/call directly.** Do not add a second TTY check. |
| `Confirm.ask("...", default=False)` + `click.echo("Aborted...")` + `sys.exit(0)` on decline | `:1836-1842` | **Yes, shape.** Note `sys.exit(0)` on an explicit decline — a decline is not an error. D-11's `0/1` applies to the *operation*, not to a user-initiated abort. Worth an explicit decision in the plan. |
| SAFE-04 `if not app.db.get_eprom(chip): raise ChipNotFoundError(...)` with its comment explaining the `get_eprom`-emptiness keying | `:1844-1850` | **Yes, verbatim.** |
| `--destructive` mode flag | `:1755-1763` | **No** — D-05 drops it. |
| Off-TTY behaviour: proceed (the flag is the consent) | `:1836` (`if interactive and destructive and not assume_yes`) | **No** — D-06 inverts this to *refuse* off-TTY without `-y`. |

**The ordering divergence (F-05):** in-tree, the confirm at `:1836` precedes the absent-chip hard-fail at `:1849`. D-08 requires absent → capability → support-status → confirm → serial. A verbatim copy produces the wrong order and would prompt for consent on a chip that is then refused — exactly what D-08's last clause forbids. This must be an explicit plan note, not left to the executor to notice.

### F-06 — `resolve_chip` returns the programmer dict; the `_SRAM_PROTO_IDS` short-circuit is vacuous in production

See Pitfall 1 for the full evidence, the executed measurements, and the consequences. Summary of the load-bearing facts:

- `resolve_chip(name, db)` → `db.convert_to_programmer(db.get_eprom(name))` (`chip_resolver.py:73-77`).
- That dict's keys, measured: `memory-size`, `algorithm`, `pin-count`, `vpp_mv`, `pulse-delay`, `chip-id`, `flags`, `bus-config`. **No `protocol-id`, no `electrical-type`, no `name`.**
- `check_eprom_blank`'s short-circuit reads the two absent keys; measured `False` for a real SRAM part.
- Both production paths (`blank` CLI at `cli_handlers.py:576`; `chip_test.run_plan` → `resolve_chip` at `chip_test.py:505` → `check_eprom_blank` at `:737`) pass that dict.
- **Correction to record:** PROJECT.md SIXTH CORRECTION item 6's disposition (KEEP) stands; its stated reason (that the short-circuit fires and produces a better message) does not. Do not fix, do not delete — record.
- Same defect class, second instance, already documented in-tree at `chip_test.py:628-637` and quantified this session: `_write_region_for`'s UV detection has `eprom_data.get("electrical-type","") == "UV-EPROM"` (always `False` at execution time) `or eprom_data.get("algorithm") == 0x0B`. UV-EPROM parts by algorithm across the DB: **0x07 → 163, 0x08 → 106, 0x0B → 32** (301 total). So the live disjunct covers **32 of 301** UV parts. This is a direct, quantified anchor for D-20's collision (c).

### F-07 — D-09's blast radius is six unconditional INFO-band ids, not five

The INFO band has **22** catalog entries (enumerated by importing `firestarter.messages.CATALOG` this session), confirming CONTEXT. Every one was traced to its firmware call site:

| Emission macro | Gated by `FLAG_VERBOSE`? | ids | Count |
|---|---|---|---|
| `LOG_INFO_ID` / `_U8` / `_U24` / `_BYTES` / `_ASTR` | **Yes** — `logging_id.h:42-100`, every variant wraps `if (is_flag_set(FLAG_VERBOSE))` | `0x40`, `0x41`, `0x42`, `0x43`, `0x51`, `0x52`, `0x53`, `0x54`, `0x55`, `0x56`, `0x57`, `0x58`, `0x59`, `0x5A`, `0x5B`(one site), `0x5C`, `0x5D` | 17 |
| `LOG_ID` / `LOG_ID_U32` (unconditional, `logging_id.h:24-36`) | **No** | `0x5E`, `0x5F`, `0x60`, `0x61` (via `eeprom28c_emit_sdp_sequence_timed`, `eeprom_28c.cpp:424-425,443-444,494-495`), `0x62` (`eeprom_28c.cpp:656`) | 5 |
| `LOG_WARN_ID_U8` — **also unconditional**, `logging_id.h:115` is a plain alias for `LOG_ID_U8` | **No** | **`0x5B` `MSG_INFO_HW`** at `rurp_hw_rev_utils.h:96` | **1** |

**F-120-07, made concrete.** `MSG_INFO_HW` (`0x5B`, format `"HW: Rev%u"`) has **two** firmware call sites: a `FLAG_VERBOSE`-gated `LOG_INFO_ID_U8` at `firestarter.cpp:154`, and an **ungated** `LOG_WARN_ID_U8(MSG_INFO_HW, (uint8_t)REVISION_UNKNOWN)` at `rurp_hw_rev_utils.h:96`, fired when `revision == REVISION_UNKNOWN && config->hardware_revision == 0xFF` (Phase 35 D-02's CR-02 "hard-fail-loud" one-shot boot-time warn). The firmware *intended* WARN severity; the host takes severity from the **catalog**, where `0x5B` is `SEVERITY_INFO`. So the frame arrives as `type="INFO"` and is currently logged at DEBUG — i.e. the deliberate hard-fail-loud warning is **invisible at default verbosity today**.

Consequences for the plan:
- **Six**, not five, ids become newly visible at default verbosity. Say six in the SUMMARY.
- D-09 is a *partial fix* for a second, older observability defect (Phase 35's CR-02), not only for Phase 118's OBS-01. Worth one sentence in the phase artifacts.
- It is bench-reachable: it fires on shields whose revision detect is inconclusive with no EEPROM override — precisely the operator's Rev 2.2 / Rev 2.0 / modified-Rev-0 rotation, where the EEPROM `hardware_revision` byte cannot distinguish the revisions.
- **Existing-test impact: none found.** Searched the whole suite for level assertions on the `SerialComm` logger. `tests/test_decoder.py` asserts at `logging.WARNING` (`:134`, `:149`, `:234`, `:307`) on the codec's own warnings, and `test_severity_routing_preserves_response_shape` (`:157-174`) asserts only on `Response.type` being a string label. No test asserts INFO frames log at DEBUG; no test asserts a record count or an empty `caplog.records`. `tests/test_serial_comm.py:103` uses `caplog.at_level(logging.DEBUG, ...)`, which is unaffected by a promotion. **No test moves; the D-09 test is purely additive.** [VERIFIED: grep for `not caplog.records`, `len(caplog.records) ==`, `caplog.records == []` → zero hits]

### F-08 / F-09 / F-10 — The complete two-side define inventory, and the three exemption classes

**Firmware `CMD_*` (`include/firestarter.h`), with preprocessor context:**

| Line | Define | Value | Context |
|---|---|---|---|
| 24 | `CMD_FRAME_MAX` | `DATA_BUFFER_SIZE` | top level; **value is a macro, not a literal** |
| 34 | `CMD_IDLE` | `0` | top level |
| 35-40 | `CMD_READ`…`CMD_VERIFY` | `1`…`6` | top level |
| 43 | `CMD_DEV_ADDRESS` | `7` | **inside `#ifdef DEV_TOOLS` (42) … `#endif` (45)** |
| 44 | `CMD_DEV_REGISTER` | `8` | same block |
| 61 | `CMD_SDP_UNLOCK` | `9` | top level — **unconditional by design**, in-source comment names Phase 120 HOST-01/HOST-03 as the host half |
| 62 | `CMD_SDP_LOCK` | `10` | top level, same |
| 64-68 | `CMD_READ_VPP`…`CMD_HW_VERSION` | `11`…`15` | top level |

**Firmware `FLAG_*`** — nine defines, all top level, `firestarter.h:131-148`: `FLAG_FORCE 0x01`, `FLAG_CAN_ERASE 0x02`, `FLAG_SKIP_ERASE 0x04`, `FLAG_SKIP_BLANK_CHECK 0x08`, `FLAG_VPE_AS_VPP 0x10`, `FLAG_OUTPUT_ENABLE 0x20`, `FLAG_CHIP_ENABLE 0x40`, `FLAG_VERBOSE 0x80`, **`FLAG_SKIP_SDP_UNLOCK 0x100`**. Grep over the whole of `include/` and `src/` returns exactly these nine — no `FLAG_*` define lives anywhere else in the firmware. **`FLAG_SKIP_SDP_UNLOCK` is the only new flag; there is no `0x200`.** F-120-05 confirmed: the ROADMAP's "flags `0x100`/`0x200`" (`ROADMAP.md:363`, and its Phase 120 *Depends on* line) is wrong. Record the correction; do not edit `REQUIREMENTS.md`.

**Host side (`constants.py`):** `COMMAND_*` at `:56-70` (13 constants, missing `COMMAND_SDP_UNLOCK`/`COMMAND_SDP_LOCK`), `COMMAND_NAMES` at `:72-86` (13 entries, same two missing), `FLAG_*` at `:90-99` (8 constants, missing `FLAG_SKIP_SDP_UNLOCK`).

**Exact deltas HOST-03 must land:** three new constants (`COMMAND_SDP_UNLOCK = 9`, `COMMAND_SDP_LOCK = 10`, `FLAG_SKIP_SDP_UNLOCK = 0x100`) plus **two `COMMAND_NAMES` entries**. After that, the two-way gate has zero unexplained gaps outside the four enumerated exemptions.

**`CTRL_VPP_VPE_DROP_ENABLE = 0x100` at `constants.py:117` is a control-register bit in a different namespace** and has its own parity leg at `test_revision_constants_parity.py:183-185`. A `FLAG_*`-scoped extractor will never see it, but a reader might confuse the two `0x100`s — worth a one-line comment beside the new flag.

**The reusable extraction machinery** (`tools/check_is_memory_cmd_no_ifdef.py`, read in full):
- `_strip_comments` (`:159-195`) — **directly reusable and load-bearing.** See Pattern 3.
- `_line_of` (`:198-199`) — trivially reusable for error messages.
- `_find_function_body` / `_predicate_def_pattern` (`:121-227`) — **not applicable.** They brace-match a function body; D-12 needs file-scope `#define` extraction.
- The env-override seam (`:92-94`, `FIRESTARTER_CMD_ADMISSION_SRC`, defaulting to `os.path.join(_HERE, "..", "..", "firestarter", "include", "firestarter.h")`) and its **fail-closed** `main()` (`:294-296`: a non-existent path is `ERROR: source file not found` + exit 1, never a silent pass). The *pattern* is what to reuse; for a pytest-hosted gate, prefer a module-level path constant + `monkeypatch.setattr` (see the Alternatives table).
- `_EXPECTED_CMD_NAMES` (`:107-118`) — a **frozen** set that must be edited deliberately, explicitly *not* auto-derived from the header, with a comment saying why. That is the right model for D-12's exemption table too.

**How `FW_ABSENT` is currently built** (`test_revision_constants_parity.py:55-58`):
```python
FIRMWARE_HEADER = Path(__file__).parent.parent.parent / "firestarter" / "include" / "firestarter.h"
FW_ABSENT = not FIRMWARE_HEADER.exists()
```
`tests/` → `firestarter_app/` → `/workspaces/` → `/workspaces/firestarter/include/firestarter.h`. It resolves via the meta-repo sibling layout, so it is present in this devcontainer and absent in host-only CI. Five of the six tests in the file carry `@pytest.mark.skipif(FW_ABSENT, ...)`; `test_revision_byte_values_match_firmware_enum` does not (it asserts host literals only). **D-13's residual gap is real and must be recorded:** in host-only CI the whole rebuilt gate skips, so a host-only PR would not catch a missing `COMMAND_NAMES` entry. D-13 already decided against splitting; record it as known-and-explained, and note in-source that `FIRMWARE_HEADER` doubles as the fixture-injection point.

**What "two-way correspondence" costs, concretely:** the existing file asserts **hardcoded literals with the firmware define named in a trailing comment and never reads the header at all** (`:104-118`, `:137-144`). It is 100% hollow with respect to firmware drift — which is exactly why `CMD_SDP_UNLOCK 9` / `CMD_SDP_LOCK 10` landed in Phase 119 unnoticed by it (`119-NONREGRESSION.md` row 7 says as much). The rebuild replaces ~40 lines of literals with a parser plus a mapping table plus an exemption table plus a fixture. Budget it as real work, not an extension.

### F-11 — The flag-plumbing chain, and the BUG-1 contract's actual surface

```
write (cli_handlers.py:463-530)
  └─ _build_op_flags(blank_check=…, force=…, vpe_as_vpp=…, skip_erase=…)   :523-528
       └─ build_flags(blank_check, force, vpe_as_vpp, verbose, skip_erase=skip_erase)   :275
            └─ eprom_operations.build_flags(...)   :168-183
```
and the parallel legacy adapter:
```
build_arg_flags(args)  (cli_handlers.py:165-197)
  └─ build_flags(blank_check, force, vpe_as_vpp, verbose, skip_erase=getattr(...))   :184-190
```

Both callers pass the first four **positionally**. D-19's keyword-only requirement is therefore not stylistic — a positional insertion would silently shift `verbose` and `skip_erase`. `tests/test_bug_characterization.py` pins the BUG-1 contract on `build_arg_flags`/`build_flags` (a `PlainArgs` bag with no `__contains__` must not raise `TypeError`), so re-running that file after the change is named task work, per D-19.

`FLAG_OUTPUT_ENABLE` / `FLAG_CHIP_ENABLE` are OR-ed in *after* the `build_flags` call, in both `_build_op_flags` (`:276-279`) and `build_arg_flags` (`:192-195`) — the in-file precedent D-19 rejected. Following D-19 means `skip_sdp_unlock` goes *inside* `build_flags`, unlike those two.

For D-04's auto-set: `write`'s handler has the chip name (`eprom: str`) and `app.db`, so it can call `sdp_capability(eprom, app.db)` and pass `skip_sdp_unlock=True` into `_build_op_flags`. That keeps the auto-set in the handler (where the report line also belongs, since it must be visible at default verbosity via `logger.info`/`click.echo`) rather than in the operations layer, which no longer has the part number (F-06). **Recommendation: D-04's auto-set lives in the `write` Click handler, not in `write_eprom`.**

### F-12 — `_log_response` is actually named `_log_rurp_feedback`

CONTEXT names the D-09 target `_log_response` at `serial_comm.py:232-247` / `:234-238`. **The function is `_log_rurp_feedback`**, defined at `:228`, with the severity mapping at `:233-238`:
```python
message = response.message
level = logging.DEBUG
if response.type == "ERROR":
    level = logging.ERROR
elif response.type == "WARN":
    level = logging.WARNING
```
Line numbers match; only the name differs. Six call sites: `:307` (docstring), `:346`, `:400`, `:411`. It logs to `rurp_logger` (a distinct logger from the module `logger`), and the prefix is abbreviated to one character when `rurp_logger.isEnabledFor(logging.DEBUG)` and the type is in `NON_RESPONSE_PREFIXES` (`:241-246`) — so promoting INFO to `logging.INFO` also changes the rendered prefix from `I:` to `INFO:` under `-v`. Minor, but a test asserting on the rendered string should know.

The full label set comes from `messages.SEVERITY_LABEL`: `OK`, `INIT`, `MAIN`, `END`, `INFO`, `WARN`, `ERROR`, `DATA`. After D-09 the mapping needs a decision for `OK`/`INIT`/`MAIN`/`END`/`DATA` too — those are protocol-phase frames, not user-facing prose, and promoting them would flood default output. **Recommendation: promote `INFO` specifically (`elif response.type == "INFO": level = logging.INFO`), leaving everything else on the `DEBUG` default.** That is the minimum change that satisfies D-09 and keeps the blast radius at the six ids F-07 enumerates.

### F-13 / F-14 — The test seams that make D-08's gate ordering provable

**`_is_interactive` monkeypatch, exactly as used today** (`tests/test_dev_test_cmd.py:148`, `:315`, `:336`, `:355`):
```python
def _off_tty():
    return patch("firestarter.cli_handlers._is_interactive", return_value=False)
# and for the TTY branch:
patch("firestarter.cli_handlers._is_interactive", return_value=True)
```
Confirm mocking: `patch("firestarter.cli_handlers.Confirm")` then `mock_confirm.ask.assert_not_called()` (`:301`, `:364`).

**AppContext construction** (`make_app_context`, `:68-91`): `EpromDatabase(skip_local_override=True)` plus `Mock(spec=...)` for every manager. So a `dev sdp` test with a `Mock(spec=EpromOperator)` can assert `operator.sdp_lock.assert_not_called()` — proving the handler refused before delegating. **That is necessary but not sufficient.**

**The load-bearing "no port opened" assertion** needs a real `EpromOperator` and the transport seam. `tests/test_hardware.py:58` establishes the exact idiom:
```python
patch("firestarter.serial_comm.SerialCommunicator.find_and_connect", ...)
```
`find_and_connect` is where `_setup_operation` opens the port (`eprom_operations.py:332-336`), so `mock_find_and_connect.assert_not_called()` is the assertion that distinguishes "refused before the wire" from "refused after connecting". `tests/test_consistency_check.py:81` documents the same intent from the other direction ("No serial round-trip and no `find_and_connect` invocation").

**Recommended two-level test design for D-08:**
1. Mock-operator level, three cases (absent / capability-refused / `adapter-required`): assert the operator's SDP method not called **and** `Confirm.ask` not called, and assert on the *reason text* to prove which gate fired (an `adapter-required` `0x0D` part with no SDP must hear the capability message, not the adapter message — D-08's stated purpose).
2. Real-operator level, one case: patch `SerialCommunicator.find_and_connect` and assert `assert_not_called()`.

Also carry the two env artifacts: `tests/test_audit_coverage_matrix.py::test_golden_file_matches` is **pre-existing RED** (reproduced this session: 186034 vs 184631 bytes), and `tests/test_no_programmer_found_*` are documented as going red with a live board attached — but **did not fail this session** with `/dev/ttyACM0`, `/dev/ttyACM1`, `/dev/ttyUSB0` all present. Record that the artifact did not reproduce rather than pre-excusing it.

### F-15 / F-16 — HOST-06's runtime proof surfaces, and the sequencing fact

**D-14's `MSG_ERR_UNKNOWN_CMD` mapping.** Firmware's `loop()` switch has `default: MSG_ERR_UNKNOWN_CMD` (`src/firestarter.cpp`), so `cmd 9` against `3.0.0b11` returns that id. On the host, an ERROR-band frame is raised through `_raise_for_error_response` in `_execute_phase` (`eprom_operations.py:447-451`) / `_main_phase_simple` (`:502-503`). The mapping should key on the **message id**, available on `Response.id` (`serial_comm.py:398`), not on the message text.

**D-15's ack.** Two seams, both non-ring-fenced; see Pitfall 5. `_decode_id_frame` recommended, on the Phase 55 precedent.

**Landing order, verified this session:**

| Repo | Branch | Tip | Working tree |
|---|---|---|---|
| `/workspaces/firestarter` (firmware) | `v1.22-at28c-software-data-protection-lifecycle` | **`0048b3d`** `test(119-08): prove the page-load worst-interval report fires correctly on both exits (D-16)` | **clean** (`git status --porcelain` empty) |
| `/workspaces/firestarter_app` (host) | `v1.22-at28c-software-data-protection-lifecycle` | `9ead17f` `test(119-06): add the EEPROM_SDP_ENABLE source-text parity leg (LOCK-05)` | modified (expected — active work) |

D-16's commit provenance (`0048b3d`) is confirmed. `firestarter/include/version.h:11` still reads `#define VERSION "3.0.0b11"`. Both sub-repos are on the milestone branch, satisfying the CONTEXT setup precondition. **The firmware tree must be byte-clean at phase end** — capture `0048b3d` in the plan as the expected tip and assert `git -C /workspaces/firestarter status --porcelain` empty (which also discharges Pitfall 7's vacuous-path concern without any path-scoped diff).

### F-17 — The DB splits alias groups the allow-set cannot distinguish, and we cannot see why

Six Atmel `0x0D` entries are split into families the DB treats as distinct rows with identical `algorithm`, identical `pinout`, and identical `size_bytes`:

```
AT28C04,AT28HC04                    vs  AT28C04E,AT28C04F                   (both DIP24_2816, 512 B)
AT28C16,AT28HC16,AT28HC16L          vs  AT28C16E,AT28C16F                   (both DIP24_2816, 2 KB)
AT28C17                             vs  AT28C17E,AT28C17F                   (both DIP28_28C64, 2 KB)
AT28C64,AT28C64B(Non-Standard),...  vs  AT28C64B,AT28HC64B,AT28HC64BF  vs  AT28C64E,AT28C64F
```
Something upstream distinguishes them, and it is not any field `build_db.py` currently carries into `chip_database.json` — the most likely candidate is exactly the `infoic.xml` bits 14/15 the reviewed-not-folded todo would decode. **Consequence for the allow-set:** the E/F suffix families are the most likely place where a future decoded-metadata partition will *disagree* with this curated one. Say so in the phase artifacts so the later phase reads a recorded uncertainty rather than a claim.

### F-18 — Nine-row CORRECTION-4 baseline: all green, executed this session

Sourced from `.planning/phases/119-lock-sdp-enable-command-surface-fw-half/119-NONREGRESSION.md` §5. This phase edits no firmware, so all nine are **expected** to stay green — and this is the "make it checkable" baseline.

| # | Gate | Command (run from `/workspaces/firestarter_app`) | Verdict this session |
|---|------|---------|---------|
| 1 | `tools/check_no_log_in_sdp_window.py` (HIGH-risk row) | `python3 tools/check_no_log_in_sdp_window.py` | **PASS** exit 0 — `PASS: no logging call in SDP timing window (…/eeprom_28c.cpp, emitter lines 298-314, completion-poll lines 348-361)` |
| 2 | `tests/test_check_no_log_in_sdp_window.py` | `python3 -m pytest tests/test_check_no_log_in_sdp_window.py -q` | **PASS** |
| 3 | `tests/test_sdp_table_parity.py` (MEDIUM-risk; broken 3× by Phase 117) | `python3 -m pytest tests/test_sdp_table_parity.py -q` | **PASS** |
| 4 | `tools/check_is_memory_cmd_no_ifdef.py` + its pytest + `tests/fixtures/planted_ifdef_in_predicate.h` | `python3 tools/check_is_memory_cmd_no_ifdef.py` then `python3 -m pytest tests/test_check_is_memory_cmd_no_ifdef.py -q` | **PASS** exit 0 — `predicate body lines 109-123`; pytest green |
| 5 | `tools/gen_sdp_bus_config.py` (generator idempotence) | `python3 tools/gen_sdp_bus_config.py` then `git -C /workspaces/firestarter status --short` | **PASS** — `OK: wrote …/_shared/sdp_bus_config.h`; firmware status **empty** afterward (no drift) |
| 6 | `tests/test_sdp_bus_config_drift.py` | `python3 -m pytest tests/test_sdp_bus_config_drift.py -q` | **PASS** |
| 7 | `tests/test_revision_constants_parity.py` — **this phase REBUILDS it (D-12/D-13)**, so it is the one row that will change | `python3 -m pytest tests/test_revision_constants_parity.py -q` | **PASS** (6 tests) at baseline |
| 8 | `tests/test_dispatch_mirror.py` | `python3 -m pytest tests/test_dispatch_mirror.py -q` | **PASS** |
| 9 | `tools/check_dispatch.py` + `tools/check_devtest_orchestrator.py` (+ `tests/test_check_devtest_orchestrator.py`) | `python3 tools/check_dispatch.py` then `python3 tools/check_devtest_orchestrator.py` | **PASS** exit 0 — `all 746 chips scanned; 736 supported; … 0 dispatch regressions; 0 consistency violations` / `0 VPP-set, 0 raw-wire-dict, 0 --force; firmware untouched (host-only, asserted)` |

Combined pytest run of rows 2/3/4/6/7/8 plus `tests/test_check_devtest_orchestrator.py` and `tests/test_sdp_db_invariant.py`: **48 passed, 0 failed.**

**Two rows deserve extra attention in the plan.** Row 7 is the row this phase *rewrites*, so "unchanged" is not the right verdict for it — the plan must state the new expected shape and re-run it. Row 9's `check_devtest_orchestrator.py` asserts *"firmware untouched (host-only, asserted)"* over `chip_test.py`, `cli_handlers.py`, `submit.py` — and **`cli_handlers.py` is edited by this phase**, so row 9 is the one host-side row with a real chance of tripping. Confirm rather than assume, especially after the `dev sdp` handler lands. Also note row 5's caveat carried from Phase 119: `_shared/sdp_expected.h`'s whole-file blob-SHA shorthand is **retired** and must not be reached for.

**Full-suite baseline, executed this session:** exactly **one** failure — `tests/test_audit_coverage_matrix.py::TestAuditCoverageMatrix::test_golden_file_matches` (produced 186034 bytes vs golden 184631; first diff at index 1178). Pre-existing RED, not this phase's regression. Everything else green, 29 snapshots passed.

### F-19 — D-20's amendment surface, with real anchors

**The precedent:** `.planning/phases/119-lock-sdp-enable-command-surface-fw-half/119-09-PLAN.md` — `files_modified: [.planning/ROADMAP.md, .planning/REQUIREMENTS.md, .planning/PROJECT.md, .planning/STATE.md]`, `autonomous: true`, `requirements: [DEVTEST-01]`. Its mechanics, which the Phase 120 amendment task should copy:

- Meta-repo-only commit, staging `.planning/` paths explicitly; **do not stage either submodule gitlink**; both sub-repo working trees clean at the end.
- **`Edit` for scoped replacements — never a wholesale rewrite** of `ROADMAP.md`/`REQUIREMENTS.md`/`PROJECT.md`/`STATE.md`. `ROADMAP.md` is 2206 lines and carries every phase of this milestone plus preserved earlier ones.
- Explicit prohibitions worth restating verbatim: MUST NOT tick a requirement whose other half is unlanded; MUST NOT edit a requirement's *wording* where a correction block is the record instead; MUST NOT remove or renumber a phase; **MUST NOT run `gsd roadmap phases.clear`** (would hard-delete 50+ preserved phase dirs).
- STATE.md ordering discipline: `state.record-session` **first**, then progress/metric/decision calls, then hand-verify `current_phase_name` (mangled repeatedly on the em-dash and trailing parenthetical) and `progress.percent`. Never trust the returned `updated` array.

**The exact files and sections the Phase 121 amendment must touch:**

| File | Section / anchor | What changes |
|---|---|---|
| `.planning/ROADMAP.md` | `:156` — the Phase 121 one-line checkbox entry in the v1.22 phase list | Add the redesign to the scope sentence and to the trailing requirement-id list |
| `.planning/ROADMAP.md` | `:377-392` — `### Phase 121: dev test FIX + GATES + DOCS` (Goal, Depends on, Requirements, five Success Criteria, Plans, Research flag) | Amend Goal + Requirements list; add criteria for the redesign; the `Research flag: yes` line already says Phase 121 likely needs `--research-phase 121`, which the redesign reinforces |
| `.planning/REQUIREMENTS.md` | `§ "dev test" Correctness` at `:82-84` | New requirement ids (the existing block holds only DEVTEST-01) |
| `.planning/REQUIREMENTS.md` | `§ Traceability` table at `:151-188` | One new row per new id, mapped to Phase 121, status `Pending` |
| `.planning/REQUIREMENTS.md` | `§ Coverage` bullets at `:190-194` | The `36` total, the per-phase tally, and the `36/36` mapped count all change |
| `.planning/REQUIREMENTS.md` | `§ Out of Scope` at `:118-131` and `§ Future Requirements` at `:100-114` | SUB-01/02's *"explicit + interactive-only; never on a bare run"* contract is contradicted by always-ask and must be recorded as reversed, not silently dropped |
| `.planning/PROJECT.md` | after the SIXTH CORRECTION block (`:91-99`) | A **SEVENTH CORRECTION** block in the established shape |
| `.planning/STATE.md` | position + decision records | Per the ordering discipline above |

**The three collisions D-20 requires recording, each verified this session:**

**(a) It reverses three locked decisions.** Confirmed in live source. `cli_handlers.py:1808-1812` (the `dev_test` docstring) states verbatim: *"Issues ZERO interactive prompts about tester-supplied identity (Phase 112 Plan 04 reversal, operator-approved per `112-UAT.md`): shield revision, chip origin, and pot-adjustment are no longer asked."* And `:1831-1835`: *"SAFE-03: the ONLY interactive input left in this handler is the `--destructive` safety confirm."* SAFE-01's CLI-only lock is in the option help text at `:1760-1762`: *"CLI-only flag -- never read from config or environment (SAFE-01)."* Record it *as* a reversal, following 119 D-18's pattern.

**(b) "Non-destructive means a partial write" is a contract change, not a flag change.** `derive_plan` at `chip_test.py:319-425`, and `Plan.locked_destructive`'s docstring at `:298-316`: *"`run_plan` MUST NOT iterate this field."* Today `destructive=False` **structurally omits** `OP_WRITE`, `OP_VERIFY` and `OP_ERASE` from `Plan.steps` and records them as `(op, reason)` tuples on the advisory `locked_destructive` list — there is literally no code path from `run_plan` to a destructive op on a non-destructive plan. A third "partial write" mode therefore needs a new representation, not a flag flip. Its ripple set, all confirmed present: the closed six-string op vocabulary `OP_ID`/`OP_READ`/`OP_BLANK_CHECK`/`OP_WRITE`/`OP_VERIFY`/`OP_ERASE` (`chip_test.py:273-278`); `tools/parse_devtest_issue.py`; `diagnostic_report.py`'s renderer and its `ladder_state` tag (`:247`, GRAD-01); `dedup_fingerprint` (`diagnostic_report.py:174`, read back by `submit.py:169-174`); and `tests/test_audit_coverage_matrix.py`'s golden — **which is already RED** (F-18), so a matrix-touching change lands on top of an existing failure and must not be allowed to mask it.

**(c) "Destructive only for UV-erasable" needs an axis pick, and the obvious axis is not available where it is needed.** `electrical.type == "UV-EPROM"` exists in the DB (**301 parts**, measured) and *is* reachable in `derive_plan`, which reads `full = db.get_eprom(name)` (`chip_test.py:340,~365`). It is **not** reachable at the execution layer: `run_plan` → `_resolve_or_none` → `resolve_chip` (`:505`), whose dict drops `electrical-type` (F-06). The project already worked around this once, at `_write_region_for` (`:637-663`), by falling back to `algorithm == _PROTOCOL_UV_EPROM` where `_PROTOCOL_UV_EPROM = 0x0B`. **Measured coverage of that fallback: 32 of 301 UV-EPROM parts.** UV-EPROM by algorithm: `0x07 → 163`, `0x08 → 106`, `0x0B → 32`. So the existing execution-time UV signal misses 89% of UV parts. Any Phase 121 design that gates destructiveness on "UV-erasable" must either widen the algorithm set to `{0x07, 0x08, 0x0B}` (structural, no type-string dependency — the project's stated preference) or thread the `full` dict to the execution layer. This is the concrete anchor D-20 asks for.

**Also carry, verified:** `dev test --submit` in `3.0.0b11` misfiles into `firestarter_app` instead of `henols/firestarter_prom`, and must be fixed wherever this lands. And `gh issue create --label` aborts before creating unless the label pre-exists **and** the user has write access — which community testers have neither of.

### F-20 — Plan sequencing constraints beyond the two CONTEXT names

CONTEXT's two hard constraints are confirmed in code:
1. **HOST-03's constants + `COMMAND_NAMES` must precede any plan emitting `cmd 9`/`cmd 10`.** `COMMAND_NAMES[cmd]` appears at `eprom_operations.py:301` (`_setup_operation`) **and again at `:377`** (`_operation_context`) — two `KeyError` sites, not one.
2. **`sdp_capability.py` must precede both the `dev sdp` handler and the `write`-path auto-set.** Both import it.

**Further constraints found:**

3. **The exhaustiveness gate (D-02) must land with or after `sdp_capability.py`**, since it imports the allow-set. It cannot be a Wave-0 test-first artifact unless it is written against a stub.
4. **D-19's `build_flags` change must precede `write`'s `--skip-sdp-unlock` option** and must be accompanied, in the same plan, by the `tests/test_bug_characterization.py` re-check. Splitting them leaves a plan boundary at which the BUG-1 contract is unverified.
5. **D-04's auto-set depends on both `sdp_capability.py` (2) and `build_flags` (4)** — it is the join point. It also cannot precede D-19 because it needs the kwarg to exist.
6. **D-09 (`_log_rurp_feedback`) is fully independent** of everything else — no shared file with the SDP work, additive test only (F-07). **Genuinely parallelisable.**
7. **D-12/D-13's parity rebuild depends on HOST-03's constants existing** (otherwise the gate fails closed on three missing host constants — correctly, but it cannot be committed green). So: HOST-03 constants → parity rebuild.
8. **D-15's ack observation touches `serial_comm.py` (`_decode_id_frame`) and `eprom_operations.py` (`write_eprom`)** — `serial_comm.py` is also D-09's file. If both land in the same wave they conflict on one file; sequence them or put them in one plan.
9. **D-20's amendment is meta-repo-only and touches no sub-repo file.** Fully parallelisable, but 119-09's precedent puts it in the **last** wave so the correction record can cite the phase's own findings (including F-06 and F-07) rather than restating an argument. **Recommendation: last wave.**
10. **The CORRECTION-4 nine-row sweep must be the final wave**, re-run at the phase's final commit, with row 7 expected *changed* and row 9 expected *unchanged-but-at-risk* (F-18).

**Suggested wave shape** (planner's call, but this satisfies every constraint above):

```
Wave 1:  sdp_capability.py + its exhaustiveness gate (membership + shape + non-vacuity legs)
Wave 1:  constants.py: COMMAND_SDP_UNLOCK/LOCK + COMMAND_NAMES entries + FLAG_SKIP_SDP_UNLOCK   [parallel]
Wave 1:  D-09 _log_rurp_feedback INFO promotion + test                                          [parallel]
Wave 2:  two erase_eprom-shaped operator methods (sdp_unlock / sdp_lock) + payload-free shape test
Wave 2:  build_flags keyword-only param + BUG-1 re-check                                        [parallel]
Wave 2:  D-12/D-13 parity gate rebuild + planted-violation fixture                              [parallel]
Wave 3:  dev sdp handler: four gates in D-08 order, D-14 mapping, D-10 summary line, D-11 exit
Wave 3:  write --skip-sdp-unlock + D-04 auto-set + report line + D-18 non-0x0D warn             [parallel]
Wave 4:  D-15 ack observation (_decode_id_frame record + write_eprom check) + missing-ack test
Wave 5:  D-20 amendment (meta-repo only)
Wave 6:  nine-row CORRECTION-4 sweep + full pytest + CI-scoped ruff/format + watermark mypy
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|---|---|---|---|
| Constants parity via hardcoded literals with the firmware define in a trailing comment | A real header-parsing two-way gate with a planted-violation fixture | This phase (D-12) | The literal form is provably hollow — it did not notice `CMD_SDP_UNLOCK`/`CMD_SDP_LOCK` landing in Phase 119 |
| A `--destructive`-style mode flag gating a state-mutating dev command | The subcommand *is* the mode; the confirm is the gate | This phase (D-05) | `dev sdp` has no second mode, so a mandatory flag carries no information |
| Honesty encoded in a status/exit code | Honesty in the message text; status stays binary | Phase 117 D-05 → 118 D-02 → 119 D-12 → 120 D-10/D-11 | A four-phase-old convention; do not re-litigate |
| Firmware version comparison as a compatibility gate | Runtime detection: unknown *command* → error mapping; unknown *flag* → required ack | This phase (D-14/D-15/D-16) | Forced by F-120-04 — the host structurally cannot see a `b`-suffix |
| INFO-band frames logged at DEBUG (invisible without `-v`) | INFO-band frames logged at INFO | This phase (D-09) | Phase 118's OBS-01 was verified in firmware and discarded by the host for a whole phase |
| `argparse` + `build_arg_flags` bag introspection | Click + `_build_op_flags(**kwargs)` | v1.8 Phase 41 | `build_arg_flags` survives only for the BUG-1 characterization test; `build_flags` itself **is** in the production path (`cli_handlers.py:275`) |

**Deprecated / outdated in the surrounding docs:**
- ROADMAP's "flags `0x100`/`0x200`" (`:363`) — **there is no `0x200`** (F-08 / F-120-05). Record; do not edit `REQUIREMENTS.md`.
- CONTEXT's `_log_response` — the function is `_log_rurp_feedback` (F-12).
- PROJECT.md SIXTH CORRECTION item 6's *reason* for keeping `_SRAM_PROTO_IDS` — the short-circuit is vacuous in production (F-06). Disposition unchanged; reason corrected.
- `firestarter/include/version.h:11` still `"3.0.0b11"` — no bump in this phase (D-16).
- The v1.16 `primitives.{h,cpp}` layer and a wire `page_size` field do not exist. Unchanged, restated because they keep resurfacing.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | `pytest` (with `pytest-randomly`, `syrupy` snapshots, `pytest-cov`), invoked as `python3 -m pytest` |
| Config file | `firestarter_app/pyproject.toml` (`[tool.pytest.ini_options]`, `[tool.mypy]`, `mypy_error_watermark = 35`) |
| Quick run command | `cd /workspaces/firestarter_app && python3 -m pytest tests/test_sdp_capability.py tests/test_dev_sdp_cmd.py tests/test_revision_constants_parity.py -q` |
| Full suite command | `cd /workspaces/firestarter_app && python3 -m pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70` |
| Lint/format gate (CI-scoped) | `ruff check firestarter/ tests/ && ruff format --check firestarter/ tests/` |
| Type gate | `python3 tools/check_mypy_watermark.py` — and assert the reported error count stays at **1** |
| Baseline | 1 pre-existing failure (`test_audit_coverage_matrix.py::test_golden_file_matches`); everything else green |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| HOST-01 | `dev sdp <chip> enable\|disable` exists with the locked surface | unit (CliRunner) | `pytest tests/test_dev_sdp_cmd.py -k surface -x` | ❌ Wave 1 |
| HOST-01 | Gate order absent → capability → support-status → confirm; **`Confirm.ask` not called** on any refusal | unit | `pytest tests/test_dev_sdp_cmd.py -k gate_order -x` | ❌ Wave 1 |
| HOST-01 | **No serial port opened** on any refusal (`find_and_connect.assert_not_called()`) | integration (mock transport) | `pytest tests/test_dev_sdp_cmd.py -k no_port_opened -x` | ❌ Wave 1 |
| HOST-01 | On-TTY confirm gates; `-y` bypasses; off-TTY without `-y` refuses (D-06) | unit | `pytest tests/test_dev_sdp_cmd.py -k consent -x` | ❌ Wave 1 |
| HOST-01 | An `adapter-required` `0x0D` part with no SDP hears the **capability** reason, not the adapter reason (D-08's stated purpose) | unit | `pytest tests/test_dev_sdp_cmd.py -k adapter_required_hears_capability -x` | ❌ Wave 1 |
| HOST-02 | `write --skip-sdp-unlock` sets bit `0x100` in the emitted `flags` | unit | `pytest tests/test_eprom_operations.py -k skip_sdp_unlock_bit -x` | ✅ extend |
| HOST-02 | `build_flags`' new param is keyword-only with `False` default; BUG-1 contract intact | characterization | `pytest tests/test_bug_characterization.py -q` | ✅ re-run |
| HOST-02 | D-18: non-`0x0D` chip warns and the write still runs | unit | `pytest tests/test_dev_sdp_cmd.py -k non_0x0d_warn_and_proceed -x` | ❌ Wave 3 |
| HOST-03 | Every firmware `#define CMD_*`/`FLAG_*` maps two-way to `constants.py`, with `COMMAND_NAMES` coverage; exemptions enumerated | parity gate | `pytest tests/test_revision_constants_parity.py -q` | ✅ rebuild |
| HOST-03 | The parity gate **actually fails** on a planted drift | planted-violation | `pytest tests/test_revision_constants_parity.py -k planted -x` | ❌ Wave 2 |
| HOST-03 | The gate fails closed on an unreadable/absent header path | fail-closed | `pytest tests/test_revision_constants_parity.py -k fail_closed -x` | ❌ Wave 2 |
| HOST-04 | `allow-set ∪ refuse-set == exactly the 84 algorithm==13 entries`, with the 37/47 split pinned | DB invariant | `pytest tests/test_sdp_capability.py -k partition -x` | ❌ Wave 1 |
| HOST-04 | Every named refuse-set member (2 FRAM + 8 pre-SDP incl. **`2817`**) is refused, with a reason naming why | unit | `pytest tests/test_sdp_capability.py -k named_refusals -x` | ❌ Wave 1 |
| HOST-04 | Non-vacuity: a synthetic `algorithm==13` entry absent from both sets makes the shared helper raise | non-vacuity | `pytest tests/test_sdp_capability.py -k non_vacuous -x` | ❌ Wave 1 |
| HOST-04 | **Shape leg (F-06):** the predicate is name-keyed, and a `resolve_chip` dict provably lacks `protocol-id`/`name` | anti-vacuity | `pytest tests/test_sdp_capability.py -k dict_shape -x` | ❌ Wave 1 |
| HOST-04 | A user-override `0x0D` part (simulating `~/.firestarter/database.json`) is refused at runtime | unit | `pytest tests/test_sdp_capability.py -k local_override_refused -x` | ❌ Wave 1 |
| HOST-04 | D-04: a refused part gets `FLAG_SKIP_SDP_UNLOCK` auto-set on `write` **and** an unconditional report line | unit | `pytest tests/test_dev_sdp_cmd.py -k auto_set_reported -x` | ❌ Wave 3 |
| HOST-05 | No SDP report text contains a lock/unlock state boolean; the unreadable-state caveat is present on **both** directions | text assertion | `pytest tests/test_dev_sdp_cmd.py -k no_fabricated_state -x` | ❌ Wave 3 |
| HOST-05 | An INFO-band decoded frame logs at `logging.INFO`, not DEBUG (D-09) | unit | `pytest tests/test_serial_comm.py -k info_band_promoted -x` | ✅ extend |
| HOST-05 | D-10: the host summary line does **not** carry a duration figure | text assertion | `pytest tests/test_dev_sdp_cmd.py -k summary_no_duration -x` | ❌ Wave 3 |
| HOST-05 | D-11: `0x87` `MSG_WARN_SDP_TBLC_EXCEEDED` prints at WARNING and exit code stays `0` | unit | `pytest tests/test_dev_sdp_cmd.py -k tblc_warn_exit_zero -x` | ❌ Wave 3 |
| HOST-06 | D-14: `MSG_ERR_UNKNOWN_CMD` on the SDP path renders as "firmware too old — run `firestarter fw --install`" | unit | `pytest tests/test_dev_sdp_cmd.py -k firmware_too_old -x` | ❌ Wave 3 |
| HOST-06 | D-15: flag set **and** `0x86` absent → loud report + operation fails | unit | `pytest tests/test_eprom_operations.py -k missing_sdp_ack -x` | ❌ Wave 4 |
| HOST-06 | D-15 converse: flag set **and** `0x86` present → no complaint, operation succeeds | unit | `pytest tests/test_eprom_operations.py -k sdp_ack_honoured -x` | ❌ Wave 4 |
| all | Nine-row CORRECTION-4 sweep green at the final commit | regression | see F-18's table (nine commands) | ✅ all present |
| all | Firmware sub-repo byte-untouched | regression | `git -C /workspaces/firestarter status --porcelain` empty; tip still `0048b3d` | ✅ |
| all | DB + codegen untouched | regression | `git -C /workspaces/firestarter_app diff --stat -- firestarter/data/ firestarter/messages.py` empty | ✅ |

### Sampling Rate
- **Per task commit:** the quick run command above, plus `ruff check firestarter/ tests/` and `ruff format --check firestarter/ tests/`.
- **Per wave merge:** full suite (`pytest tests/ --cov-fail-under=70`) + `python3 tools/check_mypy_watermark.py` (assert error count ≤ 1) + the nine-row gate table if the wave touched `cli_handlers.py`, `constants.py` or anything the gates scan.
- **Phase gate:** full suite green except the single pre-existing `test_audit_coverage_matrix` failure (named explicitly, not silently tolerated); all nine gate rows re-run at the final commit; both sub-repo trees in their expected state.

### What CAN and CANNOT be validated

**CAN be validated in software (all of it, in this phase):**
- The allow-set exhaustiveness invariant over the shipped 84 entries, with the 37/47 split pinned and a non-vacuity leg.
- That the predicate is name-keyed and not silently vacuous (the F-06 shape leg — a validation surface this phase *invents*, because the existing `_SRAM_PROTO_IDS` precedent lacks it and is vacuous as a result).
- Two-way constants parity against the real header, with a planted-violation fixture and a fail-closed path.
- Gate ordering, by "no `Confirm.ask` call" and "no `find_and_connect` call" — not by exit code.
- That bit `0x100` is actually set in the emitted `flags` value.
- The D-09 severity mapping, by decoding a real INFO-band frame through the fake-serial fixture.
- The D-15 missing-ack failure, by feeding a frame stream with and without `0x86`.
- The absence of a fabricated state boolean in the report text, and the presence of the unreadable-state caveat on both directions.
- That the firmware sub-repo is byte-untouched.

**CANNOT be validated — the ceiling, restated:**
- **That the curated capability partition is correct per family.** `REQUIREMENTS.md` §"Validation Ceiling" lists this explicitly among the things not provable this milestone. D-01's fail-closed direction is the *response* to that, not a claim against it. The gate proves the partition is **total and stable**, never that it is **right**.
- Any claim about actual silicon protection state, before or after either sequence.
- That `tBLC` is met as accepted by the die.
- That gh#11's symptom is gone.
- Nothing in this phase is evidence about AT28C silicon. `0x0D` stays `UNVERIFIED`; zero `support_status` changes; the 84-chip count is unchanged.

### Planted-violation fixtures required (the project's mandatory anti-hollow contract)

Every gate this phase ships needs a companion proving it can fail:

| Gate | Planted violation | Proves |
|---|---|---|
| Constants parity (D-12/D-13) | `tests/fixtures/planted_constants_drift.h` — a header copy with one `CMD_*` value changed, one `FLAG_*` deleted, and one new `CMD_*` added | Value drift, host-missing, and firmware-missing are each detected |
| Constants parity — `COMMAND_NAMES` leg | An in-test `monkeypatch.delitem` on a `COMMAND_NAMES` copy | A missing name entry is caught, not just a missing constant |
| Constants parity — fail-closed | Point the path constant at a non-existent file | An unreadable header is an ERROR, never a silent pass |
| Allow-set exhaustiveness (D-02) | A synthetic in-memory DB with one `algorithm == 13` entry in neither set | The partition invariant can fail — mirrors `test_sdp_db_invariant.py:151-184` |
| Allow-set shape leg (F-06) | Assert `"protocol-id" not in resolve_chip(...)` | The vacuity mode that broke `_SRAM_PROTO_IDS` is machine-excluded |
| Gate ordering (D-08) | Reorder the gates locally in a test double, or assert the reason-string identity per gate | Gate *order* is tested, not just gate presence |
| D-09 mapping | Assert the `DEBUG` default still applies to a non-INFO, non-WARN, non-ERROR label | The promotion is scoped, not a blanket level change |
| D-15 missing ack | A frame stream with the flag set and `0x86` **omitted** | The check fires; the converse case proves it does not over-fire |

## Security Domain

`security_enforcement` is absent from `.planning/config.json` → treated as enabled. This is an offline, single-user CLI driving local serial hardware; there is no network surface, no authn/authz, no session, no multi-tenancy. The applicable controls are input validation and physical-effect safety.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | No accounts, no credentials, no remote surface |
| V3 Session Management | no | No sessions |
| V4 Access Control | **yes, in a hardware sense** | The consent gate (D-05/D-06/D-07) is the authorization boundary for a state-mutating physical operation; the capability refusal (D-01) is the authorization boundary for *which chip* may receive it. `is_memory_cmd()` is firmware's own access-control gate (its own comment says so) — untouched here |
| V5 Input Validation | **yes** | `click.Choice(["enable","disable"])` for the mode; `db.get_eprom_config`'s alias resolution for the chip name; the fail-closed allow-list for capability. **Never** interpolate the user's chip string into a wire field — the wire dict is built entirely from DB-derived values via `convert_to_programmer` |
| V6 Cryptography | no | None involved. Frame CRC8 (`codec._crc8_ccitt`) is integrity-only and untouched |
| V7 Error Handling & Logging | **yes** | D-10/D-11/D-15's whole point: never report a state that was not observed; fail loudly rather than silently. `codec.decode_id_frame` already drops unknown ids with a warning rather than mis-rendering them (`codec.py:206-209`) |
| V12 Files & Resources | marginal | `dev sdp` reads and writes no file. If a plan adds one, honour `FIRESTARTER_CONFIG_DIR` and the `_sanitize_chip_token` precedent (`cli_handlers.py:1904`) |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| A crafted `~/.firestarter/database.json` entry claiming `algorithm: 13` for an arbitrary part, reaching the SDP path | Tampering | The fail-closed **runtime** allow-list (D-02's decisive reason). A CI-only gate would not see it |
| An unrecognised chip token defaulting to permitted | Elevation of Privilege (hardware) | Fail-closed default: unknown ⇒ refuse. Enforced by the exhaustiveness gate |
| Data corruption on a part without an SDP decoder — the sequence stores bytes at truncated magic addresses (F-120-01) | Tampering (physical) | HOST-04's pre-wire refusal, widened by D-04 to the `write` path |
| A silent no-op reported as success (the milestone's central defect class) | Repudiation | Refuse before the wire with a spoken reason; never a fabricated state boolean (HOST-05). Firmware's NULL-`main` refusal (119 D-06/D-07) is the counterpart |
| Path traversal via the chip name into a filename | Tampering | `_sanitize_chip_token` already exists; `dev sdp` writes no file, so keep it that way |
| A hostile/corrupt frame over-sizing a buffer | Denial of Service | Existing plausibility clamp `[1, 4096]` on `firmware_max_chunk` (`serial_comm.py:271-274`). D-15's ack record must be equally defensive — record an id in a bounded set, never allocate from frame content |
| A slopsquatted dependency | Tampering (supply chain) | N/A — zero new packages this phase |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Atmel's AT28C parallel-EEPROM line (AT28C64/64B/256/010/040 and the BV/LV/PC/MC/HC variants) supports the AA-55-A0 SDP sequence | F-01 ALLOW HIGH row | Low — the milestone's own datasheets-of-record (doc0270, DS20006432B, DS20006386B, doc0353) cover AT28C64B, AT28C256 and AT28C010 directly; the variants are family extension |
| A2 | Microchip `28C64*`/`28C256*`, Xicor `X28C64`/`X28C256`, Catalyst `CAT28C64`/`CAT28C256` support SDP | F-01 ALLOW MEDIUM row | Medium — cited to in-tree `doc/lockable-proms.md` §17, which is itself hedged ("Usually no" refers to *readability*, not to SDP presence). Wrong ⇒ 21 entries over-permitted; the corruption exposure of F-120-01 applies |
| A3 | The Catalyst 1M/2M/4M/512K and Microchip/Xicor 1M members belong to the same SDP-capable family as their 64K/256K siblings | F-01 judgement call 4 | Medium — family extension beyond §17's literal naming |
| A4 | The `28C17`/`AT28C17`/`CAT28C17A` 2 KB 28-pin parts have SDP while bare `2817` does not (the `C` marks the generation) | F-01 judgement call 3 | Medium — plausible and consistent with HOST-04's naming of `2817`, but not datasheet-confirmed |
| A5 | `XICOR/X2864AP` is pre-SDP generation and is correctly refused | F-01 judgement call 1 | Low harm (over-refusal), but this is the member most likely misclassified — and `XICOR/X28256,X28C256` proves the naming signal is unreliable |
| A6 | The Atmel `DIP24_2816` block (AT28C04/04E,F/16/16E,F) is correctly over-refused | F-01 judgement call 2 | Medium — `doc/lockable-proms.md` §17 names "Atmel AT28C16" as SDP-capable, so this knowingly contradicts an in-tree source in the safe direction. **Highest-value item for operator review** |
| A7 | ST / SGS-Thomson `M28C64`/`M28256`/`M28010`, AMD `AM28C64*`, NEC `UPD28C*`, Samsung `KM28C*`, Hitachi `HN58C256AP`, Exel `XLE/XLS28C*`, WED `WE*K8`, Maxwell `28C010*` lack SDP or cannot be confirmed to have it | F-01 REFUSE LOW row (26 entries) | Medium in the over-refusal direction — several (notably ST M28C64 and AMD Am28C64A) plausibly do have SDP. Cost is D-04's write-path degradation on a locked part |
| A8 | `infoic.xml` bit 15 (`MP_PROTECT_AFTER`) would be the authoritative SDP-capability axis if decoded | F-01, F-17 | Low — the in-tree note calls it a heuristic; recorded as an expectation for a later phase, not relied on here |
| A9 | Promoting only the `INFO` label (leaving `OK`/`INIT`/`MAIN`/`END`/`DATA` on DEBUG) is the intended reading of D-09 | F-12 | Low — but it is a real interpretive choice the planner should confirm; the alternative floods default output with protocol-phase frames |
| A10 | Recording an observed message id on the `SerialCommunicator` via `_decode_id_frame` does not violate the GATE-1.8d ring-fence | Pitfall 5, F-15 | Low — the docstring at `serial_comm.py:260-261` states precisely this seam's purpose, and Phase 55 already used it |
| A11 | The `dev sdp` command surface will remain in the stable release channel | not planned here | Recorded only — 999.15 / gh#8's channel split currently keeps only `dev read` + `dev test` in stable, which would strip `dev sdp`. CONTEXT explicitly leaves this unacted-on |

**Highest-priority items for operator confirmation before planning locks:** **A6** (the Atmel `DIP24_2816` over-refusal knowingly contradicts `doc/lockable-proms.md` §17), **A7** (26 entries refused for lack of a citation, several plausibly SDP-capable), and **A2** (21 entries permitted on a hedged in-tree source). The overall *direction* is locked by D-01 and needs no confirmation; the *membership* of those three rows is the operator-decidable surface.

## Open Questions

1. **Should the D-12 parity gate live in `tests/` or as a `tools/` script + paired pytest?**
   - What we know: every other planted-violation gate in this project is a `tools/` script with an `FIRESTARTER_*_SRC` env seam and a paired pytest, and that shape adds a runnable row to the CORRECTION-4 table. But D-12/D-13 explicitly want *one* gate with the `FW_ABSENT` skipif retained, and `tools/` is **outside** CI's ruff scope (four `tools/` files are already lint-dirty at baseline), so a new tool would ship un-linted.
   - What's unclear: whether the operator values the CORRECTION-4 table row enough to accept a second file and an un-linted module.
   - Recommendation: **pytest-only**, with the parser as a module-level helper and the fixture injected by `monkeypatch.setattr` on a module-level path constant. Note in the plan that this is the one gate in the table that lives entirely in `tests/`.

2. **Does an explicit user decline (`Confirm.ask` → no) exit `0` or `1`?**
   - What we know: `dev test` exits `0` on decline (`cli_handlers.py:1839`) with `click.echo("Aborted -- chip left untouched.")`. D-11 specifies `sys.exit(0 if ok else 1)` "off the state machine's result" — but on a decline there is no state machine result.
   - Recommendation: follow `dev test` — `0` on an explicit user decline (the user got what they asked for), `1` on a refusal the *host* imposed. Make it an explicit plan decision and test both, because `0` on a capability refusal would be wrong.

3. **Does `--skip-sdp-unlock` on a non-`0x0D` chip still emit the bit (D-18)?**
   - What we know: D-18 says warn and proceed; firmware never reads the bit on other protocols, so either choice is safe. The reason to *emit* it is that a blanket-flag script across a mixed batch produces identical wire frames regardless of chip, which is easier to reason about; the reason not to is minimality.
   - Recommendation: **emit it** and warn. It keeps `build_flags`' mapping unconditional (D-19's whole point) and avoids a per-protocol branch inside a flag-mapping function.

4. **How many new requirement ids does D-20's amendment create, and do the CLOSE-02 closeout comments change?**
   - What we know: the redesign has five distinct behaviours (no flags; UV-only destructive scope; the interactive full-vs-partial write ask; always-ask issue filing with `gh` dedup; `gh` preferred over the browser path), plus two fixes that must land somewhere (`--submit` misfiling to the wrong repo; `gh issue create --label` aborting for community testers). `REQUIREMENTS.md`'s coverage arithmetic (`36` total, `36/36` mapped) changes either way.
   - What's unclear: id granularity is an operator/planner call, and whether the `--submit` repo fix belongs to Phase 121 or is hot-fixed sooner (it affects users of `3.0.0b11` **today**).
   - Recommendation: raise the `--submit` misfiling explicitly during planning as a candidate for earlier treatment, since it is actively misdirecting community reports right now.

5. **Should the phase also record a correction for the vacuous `_SRAM_PROTO_IDS` short-circuit and the 32-of-301 UV detection, or leave both to Phase 121?**
   - What we know: both are out of scope to *fix* here. Both are directly load-bearing on this phase's own design (F-06) and on D-20's amendment (collision c).
   - Recommendation: **record both in the D-20 correction block**, since that task is already writing a PROJECT.md correction and both findings are anchors that block came for.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | everything | ✓ | 3.12.13 (devcontainer) — **CI targets py3.9/3.11** | Validate ruff/format against the CI target, not 3.12 |
| `pytest` (+ `pytest-cov`, `pytest-randomly`, `syrupy`) | all gates | ✓ | installed; full suite ran this session | — |
| `ruff` | lint/format gate | ✓ | installed | — |
| `mypy` | type gate | ✓ | installed; warns `python_version 3.9 not supported` (devcontainer artifact) | Use `tools/check_mypy_watermark.py`, the CI gate |
| `click`, `rich`, `packaging` | CLI + confirm | ✓ | pinned deps, exercised in-tree | — |
| Firmware checkout at `/workspaces/firestarter` | `FW_ABSENT`-gated parity tests, five gate-table checkers | ✓ | branch `v1.22-…`, tip `0048b3d`, tree clean | Gates skip cleanly (`FW_ABSENT`) or fail closed (`tools/check_*`) when absent |
| `firestarter/data/chip_database.json` | allow-set exhaustiveness gate | ✓ | 84 `algorithm==13` entries confirmed | None needed — it is packaged |
| `tools/infoic.xml` | the *authoritative* b14/b15 SDP axis | **✗** | — | **No fallback in scope.** External input, not committed. Out of reach by design (F-01); curated allow-set is the answer |
| Serial hardware | nothing in this phase | ✓ (`/dev/ttyACM0`, `/dev/ttyACM1`, `/dev/ttyUSB0` present) | — | **Not needed.** This phase adds no bench work. Note the boards are attached, which is the documented trigger for `test_no_programmer_found_*` flakiness — it did **not** reproduce this session |
| `gh` CLI | nothing in this phase (only the D-20 amendment *describes* it) | not checked | — | N/A — no `gh` invocation lands here |
| PlatformIO / `pio` | nothing in this phase | not needed | — | Zero firmware builds; no flash-delta measurement (contrast Phase 119's LOCK-06) |

**Missing dependencies with no fallback:** none that block execution.
**Missing dependencies with fallback:** `tools/infoic.xml` — absent, deliberately out of scope; the curated allow-set is the designed answer, and F-17 records the expected future supersession.

## Sources

### Primary (HIGH confidence — read or executed this session)
- `firestarter_app/firestarter/`: `database.py` (`:160-247`, `:364-441`, `:442-597`), `chip_resolver.py` (full), `constants.py` (`:50-124`), `cli_handlers.py` (`:60-360`, `:455-531`, `:565-582`, `:955-985`, `:1700-1936`), `eprom_operations.py` (`:160-250`, `:287-508`, `:1555-1731`), `serial_comm.py` (`:60-100`, `:195-280`, `:300-431`), `codec.py` (`:180-225`), `chip_test.py` (`:255-425`, `:495-520`, `:625-750`), `messages.py` (CATALOG imported and enumerated)
- `firestarter_app/tools/check_is_memory_cmd_no_ifdef.py` (full, 335 lines)
- `firestarter_app/tests/`: `test_revision_constants_parity.py` (full), `test_sdp_db_invariant.py` (full), `test_dev_test_cmd.py` (`:1-160`, plus grep of all assertions), `test_decoder.py` (severity-routing region), `test_consistency_check.py`, `test_hardware.py` (patch idiom)
- `firestarter/include/`: `firestarter.h` (`:24-155`), `logging_id.h` (`:20-130`), `rurp_hw_rev_utils.h` (`:85-100`)
- `firestarter/src/proms/eeprom_28c.cpp` (`:340-400`, `:410-500`, `:640-660`), plus a full call-site trace of all 22 INFO-band ids across `src/` and `include/`
- `firestarter_app/firestarter/data/chip_database.json` — all 84 `algorithm == 13` entries enumerated, tokenised, and partitioned by script
- `firestarter_app/.github/workflows/ci.yml`, `pyproject.toml` (mypy watermark)
- Executed: full `pytest` suite; nine-row CORRECTION-4 gate table; CI-scoped and bare `ruff`; `tools/check_mypy_watermark.py`; `resolve_chip` shape probes; `git` state in both sub-repos

### Secondary (MEDIUM confidence — in-tree project documents)
- `firestarter_app/doc/lockable-proms.md` §17 "Parallel EEPROM families: 28Cxxx" — the only in-tree per-family SDP determination; hedged, and the citable basis for A2/A3
- `.planning/notes/infoic-xml-protection-flags-research.md` — bits 14/15 semantics and the disqualifying cross-tab; the basis for A8 and F-17
- `.planning/REQUIREMENTS.md` (HOST-01..06 verbatim, Locked decisions, Out of Scope, Validation Ceiling, Traceability), `.planning/ROADMAP.md` (`:155-157`, `:360-408`), `.planning/PROJECT.md` (all six ⚠ correction blocks, `:60-108`), `.planning/research/SUMMARY.md` (datasheet citations, truncation arithmetic)
- `.planning/phases/119-…/119-NONREGRESSION.md` §5 (the nine-row table), `119-09-PLAN.md` (the amendment precedent)
- `/workspaces/CLAUDE.md`, `/workspaces/firestarter_app/CLAUDE.md`, `/workspaces/firestarter/CLAUDE.md`

### Tertiary (LOW confidence — training knowledge, marked ASSUMED)
- Per-manufacturer SDP presence for the 26 REFUSE-LOW entries and for judgement calls 1-5 (A4-A7). No web or Context7 lookup was performed: the validation ceiling already forbids proving the partition correct, D-01's fail-closed direction makes an unverifiable answer *safe* rather than *wrong*, and a citation-free web claim would be indistinguishable from training recall while looking more authoritative. The Assumptions Log names each judgement call and its direction of error.

## Metadata

**Confidence breakdown:**
- Standard stack — **HIGH**: zero new packages; every reused symbol read at file:line and, where behavioural, executed
- Architecture / integration points — **HIGH**: the full call chain from Click handler to firmware dispatch was traced in source, and the two dict shapes were measured rather than inferred
- Allow-set membership — **MEDIUM**: 18 of 84 entries rest on a datasheet-of-record or a citable in-tree source; the remaining 66 are curated with named judgement calls, and the fail-closed direction is what makes the residual uncertainty safe. The *partition's* totality and stability are HIGH (machine-checkable); its *correctness per family* is explicitly outside the validation ceiling
- Pitfalls — **HIGH**: F-06's vacuity, F-03's two-pinout trio, F-07's sixth id, and F-10's name mismatch were each demonstrated by execution or by reading both sides
- Gate-table baseline — **HIGH**: all nine rows re-run this session; full suite run; the single pre-existing failure reproduced and identified
- D-20's collision anchors — **HIGH**: all three verified in live source, with (c) quantified (32 of 301)

**Research date:** 2026-07-29
**Valid until:** 2026-08-28 (30 days) — but **immediately invalidated** by any of: a `chip_database.json` regeneration (changes the 84-entry partition), a `firestarter.h` edit (changes the parity gate's inventory), a firmware sub-repo commit past `0048b3d`, or `tools/infoic.xml` appearing in the tree (would make the b14/b15 axis reachable and supersede the curated allow-set).
