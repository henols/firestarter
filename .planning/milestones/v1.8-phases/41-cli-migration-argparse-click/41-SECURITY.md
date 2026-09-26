---
phase: 41
slug: cli-migration-argparse-click
status: verified
threats_open: 0
asvs_level: 1
created: 2026-05-28
mode: retroactive-stride
register_authored_at_plan_time: false
---

# Phase 41 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.
>
> **RETROACTIVE-STRIDE notice:** No `<threat_model>` block was authored in any
> of the four Phase 41 PLAN files (41-01..41-04). This register was built
> post-implementation from a STRIDE walk of the changed surface and verified
> against the implementation in the same pass. The phase is a pure-software
> CLI refactor (argparse → Click) on a local desktop tool with no network
> server, no auth, no multi-tenant model; the threat register is intentionally
> modest. New surface introduced by this phase is enumerated below; pre-existing
> surface in `firmware.py` / `eprom_operations.py` / `serial_comm.py` is
> explicitly out of scope (GATE-1.8a/d) and audited in the phases that
> introduced it.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| User shell -> Click parser | CLI invocation parsed by Click 8.x (`cli` group + 15 commands) | argv strings: command name, flag values, EPROM name, file paths, firmware version literal, hex/dec address strings |
| Click parser -> handler body | Validated kwargs delivered via `@click.pass_obj` + `AppContext` | Typed Python values: bool flags, Optional[str] paths, int port/timeout, validated firmware-version string |
| Handler -> chip DB (read) | `_resolve_or_exit(name, app.db)` → `EpromDatabase.resolve_chip` → JSON file | Chip name (user input); returns dict from `chip_database.json` (packaged or `~/.firestarter/database.json` override) |
| Handler -> filesystem | `read_eprom(..., output_file)` / `write_eprom(..., input_file)` / `dev consistency-check --output-dir` open user-supplied paths | Binary EPROM dump bytes; path strings come straight from argv |
| Handler -> Arduino over serial | Via `EpromOperator` / `HardwareManager` / `FirmwareManager` → `SerialCommunicator` (untouched this phase; GATE-1.8a/d) | JSON command frames at 250000 baud; binary payloads in chunked transfer |
| Shell completion subprocess -> chip DB | `_complete_eprom(ctx, param, incomplete)` runs out-of-process when shell invokes `_FIRESTARTER_COMPLETE=<shell>_source firestarter`; instantiates its own `EpromDatabase()` | Partial chip-name string from shell; returns `List[CompletionItem]` |
| `fw` handler -> network (GitHub releases) | `FirmwareManager.manage_firmware_update` → `requests.get(FIRESTARTER_RELEASE_URL, ...)` — PRE-EXISTING, not changed in Phase 41 | HTTP GET, JSON release index, binary .hex download |
| `fw` handler -> avrdude subprocess | `FirmwareManager` shells out to `avrdude` with the downloaded .hex — PRE-EXISTING, not changed in Phase 41 | argv to avrdude including user-supplied `--avrdude-path` / `--avrdude-config-path` / `--board` |

---

## Threat Register

| Threat ID | Category | Component | Disposition | Mitigation | Status |
|-----------|----------|-----------|-------------|------------|--------|
| T-41-01 | Tampering (input validation) | `_FirmwareVersionType.convert` (cli_handlers.py:219-255) | mitigate | Regex anchor `^[0-9]+\.[0-9]+\.[0-9]+((b\|rc)[0-9]+)?\Z` (`firmware.py:51`) applied to `--firmware-version`; mismatch → `self.fail(...)` → `click.BadParameter` → SystemExit(2). Behaviour-equivalent to the argparse `ArgumentTypeError` form removed this phase. | closed |
| T-41-02 | Tampering (semantic / business rule) | `fw` 3-way mutex (cli_handlers.py:791-804) | mitigate | Post-parse check: enumerates which of `pre`/`firmware-version`/`stable` are truthy; if >1 raises `click.UsageError` → exit 2. WR-03 rewrite removed an earlier per-option callback that depended on Click's left-to-right option-processing order. Covered by `test_fw_mutex_*` tests. | closed |
| T-41-03 | Tampering (semantic / business rule) | `fw --json` requires `--list` (cli_handlers.py:807-808) | mitigate | `if json_output and not list_releases: raise click.UsageError("--json requires --list")` (D-14 narrow upgrade). Exit 2 preserved from the argparse `fw_parser.error()` form. | closed |
| T-41-04 | Spoofing / Tampering (chip lookup) | `_resolve_or_exit(name, db)` (cli_handlers.py:98-113) | mitigate | Routes through `chip_resolver.resolve_chip` (Phase 39 D-01..D-03 — single chokepoint); `ChipNotFoundError` logged + None returned; 9 chip-op handlers `sys.exit(1)` on None. No string interpolation into the JSON command frame at this layer. | closed |
| T-41-05 | Information disclosure (verbose logging) | `_setup_logging(verbose)` (cli_handlers.py:41-61) | mitigate | `-v/--verbose` opt-in only; default is `INFO`. Formatter exposes `levelname/name/lineno/message` only when `verbose=True`. No secrets are logged because the system has no secrets (local desktop tool, no auth tokens, no API keys). | closed |
| T-41-06 | Information disclosure (chip DB exposure via completion) | `_complete_eprom` shell-completion callback (cli_handlers.py:80-95) | accept | Callback instantiates `EpromDatabase()` and returns every name matching the case-insensitive prefix. The chip DB is shipped in the pip package and is public (not a secret). Equivalent to argcomplete's `EpromCompleter` semantics that this phase replaces. | closed |
| T-41-07 | Denial of service (completion subprocess slow / DB-load cost) | `_complete_eprom` instantiates EpromDatabase per completion invocation | accept | DB load is fast (<100 ms) and runs in a forked subprocess invoked by the user's own shell. Local-only; no remote actor can trigger. Matches argcomplete's prior behaviour. | closed |
| T-41-08 | Tampering / path traversal (output_file / input_file / output_dir args) | `read`/`write`/`verify`/`dev read`/`dev consistency-check` accept user paths verbatim | accept | The user IS the only actor and is invoking their own shell with their own privileges. Click does not wrap the strings; `eprom_operations.py` calls `open(path, "rb"/"wb")` directly. No sandbox is asserted; the tool is a local desktop CLI and "the user can write where the user can write" is the intended model. Phase 41 does not regress this (argparse path was identical). | closed |
| T-41-09 | Elevation of privilege (Click option callbacks firing in unexpected order) | 3-way mutex implementation choice | mitigate | WR-03 fix replaced the per-option callback `_check_install_mutex` with a single post-parse check in the `fw` body (cli_handlers.py:791-804). Eliminates the order-dependence latent in Click's left-to-right callback processing that an earlier draft had. Verified by `test_fw_mutex_*` exercising every (pre,fwv,stable) ordering. | closed |
| T-41-10 | Repudiation / silent failure (argparse → Click error path swallowing) | `sys.exit(0 if op() else 1)` per handler | mitigate | Phase 36 characterization tests + `test_cli_handlers.py` happy-path + error-path tests (≥40 functions) lock the exit-code contract. Click raises `SystemExit` directly; nothing is "returned and dropped" the way an argparse-era `return 1` could have been if the dispatcher caller forgot to `sys.exit` it. `dev consistency-check` explicitly uses `sys.exit(verdict_int)` (cli_handlers.py:1076) to preserve the 3-way 0/1/2 contract — bool-to-int wrap would have collapsed the hardware-error case. | closed |
| T-41-11 | Information disclosure (env-var-driven completion mechanism) | `_FIRESTARTER_COMPLETE=<shell>_source firestarter` activation incantation (autocomplete.md) | accept | Click's documented completion mechanism. The env var is read by the SAME `firestarter` entry point the user invokes; no privilege boundary is crossed. The variable name is constant `_FIRESTARTER_COMPLETE` regardless of shell — there is no untrusted-input-to-env-var path. | closed |
| T-41-12 | Supply chain (new runtime dep `click>=8.1`) | pyproject.toml:50 | transfer | Click is the canonical, widely-used Python CLI framework (Pallets project); inherited via Python packaging ecosystem trust. Pinning `>=8.1` accepts security updates within the 8.x line. No SCA gate is configured at v1.8; this is a known accepted posture for the milestone. Compensating: `argcomplete` runtime dep was simultaneously removed (net dep count unchanged); `--help` smoke-tests at CI time. | closed |
| T-41-13 | Pre-existing surface in `fw` install path (HTTP fetch of release JSON + .hex; avrdude subprocess shell-out) | `FirmwareManager.manage_firmware_update` — NOT modified in Phase 41 | n/a | Out of scope for this phase per GATE-1.8a (wire protocol untouched). The HTTP fetch and avrdude exec live in `firmware.py`, which is in the no-touch list (41-CONTEXT.md line 219). Phase 41 only re-plumbs the CLI options into the existing call signature; no new authentication, transport, or shell-quoting code is introduced. Any audit of this surface belongs to whatever phase introduced `firmware.py` (out-of-scope for v1.8 host-CLI cleanup). | n/a |

*Status: open · closed · n/a*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-41-A | T-41-06 | Shell-completion exposes packaged chip-DB names. Chip names are public catalog data (shipped in the pip package; visible via `firestarter list`). Equivalent to the prior argcomplete behaviour this phase replaces — no posture change. | henrik@predictly.se (operator; standing v1.8 "minimize churn" stance) | 2026-05-28 |
| R-41-B | T-41-07 | Per-completion DB-load cost is sub-100ms and runs in the user's own forked shell-completion subprocess. Not remotely triggerable. | henrik@predictly.se | 2026-05-28 |
| R-41-C | T-41-08 | User-supplied output/input/output-dir paths are not sandboxed. Local desktop CLI; the user invokes with their own privileges to write where they choose. Identical to argparse-era behaviour. | henrik@predictly.se | 2026-05-28 |
| R-41-D | T-41-11 | Click's `_FIRESTARTER_COMPLETE=<shell>_source firestarter` env-var protocol is the canonical Pallets-documented mechanism; no privilege-boundary issue. | henrik@predictly.se | 2026-05-28 |
| R-41-E | T-41-12 | New runtime dep `click>=8.1` accepted via the v1.8 milestone decision (PROJECT.md "CLI framework = Click", locked 2026-05-27). Net dep count unchanged (argcomplete removed in the same wave). | henrik@predictly.se | 2026-05-27 |

*Accepted risks do not resurface in future audit runs.*

---

## Unregistered Flags (new surface detected during implementation, no pre-existing threat-model mapping)

None. SUMMARY.md files for 41-01..41-04 do not contain `## Threat Flags` sections (none authored at plan time). All new surface introduced by Phase 41 (`_FirmwareVersionType`, `_check_install_mutex` → post-parse mutex, `_complete_eprom` shell-completion callback, env-var-driven `_FIRESTARTER_COMPLETE` activation, the argparse → Click exit-code shift) has been mapped to T-41-01..T-41-11 above as part of the retroactive STRIDE walk.

---

## Verification Notes (per-threat evidence)

- **T-41-01 (firmware version validator):** Regex `FIRMWARE_VERSION_RE` confirmed at `firestarter/firmware.py:51` (anchored: `^...\Z`). `_FirmwareVersionType.convert` at `cli_handlers.py:239-255` calls `FIRMWARE_VERSION_RE.match(value)`; on mismatch raises via `self.fail(...)` (Click's `BadParameter`-throw path). Bound to `--firmware-version` at `cli_handlers.py:712`. Test pin: `test_cli_handlers.py::test_fw_invalid_firmware_version` (per 41-VERIFICATION.md Truth #2).
- **T-41-02 (3-way mutex):** Post-parse check at `cli_handlers.py:791-804` — enumerates the truthy subset of `(pre, firmware-version, stable)` and raises `click.UsageError` with a deterministic message on `len > 1`. Note: this is the WR-03 rewrite from the per-option `_check_install_mutex` callback (still referenced in 41-VERIFICATION.md Truth #2 — that text predates the WR-03 fix at lines 255/738/747/753; the live implementation is the post-parse form at 793-806).
- **T-41-03 (--json requires --list):** Verified at `cli_handlers.py:807-808`. Single line raises `click.UsageError("--json requires --list")` before any `list_releases` branch.
- **T-41-04 (chip lookup chokepoint):** `_resolve_or_exit` at `cli_handlers.py:98-113`. Called by 9 chip-op handlers (read/write/verify/blank/erase/id/dev_read/dev_addr/dev_consistency_check). Routes through `resolve_chip(name, db=db)` — single chokepoint inherited from Phase 39 D-01..D-03.
- **T-41-05 (logging level):** `_setup_logging` at `cli_handlers.py:41-61`. Defaults to INFO (line 49: `log_level = logging.DEBUG if verbose else logging.INFO`). Formatter at lines 55-59 includes `lineno`/`levelname`/`name` only when verbose; otherwise message-only.
- **T-41-06 (chip-DB completion):** `_complete_eprom` at `cli_handlers.py:80-95`. Calls `db.get_eproms(False)` (unverified chips INCLUDED — same as argcomplete behaviour). Case-insensitive prefix filter at line 94.
- **T-41-09 (mutex order-independence):** Post-parse implementation at `cli_handlers.py:791-804` does NOT depend on Click's callback firing order. WR-03 commit removed the order-dependent per-option callback approach.
- **T-41-10 (exit-code preservation):** Grep `sys.exit(0 if .* else 1)` pattern + `sys.exit(verdict_int)` for `dev consistency-check`. `dev_consistency_check` explicitly uses `verdict_int = ...; sys.exit(verdict_int)` at `cli_handlers.py:1066-1076` — 3-way 0/1/2 contract preserved.
- **T-41-12 (click dep):** `pyproject.toml:50` shows `"click>=8.1"`. `grep -c argcomplete pyproject.toml` returns 0 (per 41-VERIFICATION.md Truth #9).
- **T-41-13 (firmware.py out-of-scope):** Per 41-CONTEXT.md no-touch list (line 219) and 41-VERIFICATION.md GATE-1.8a (Truth #10): `firmware.py` is not modified this phase. Confirmed `git diff HEAD~4 HEAD -- firestarter/firmware.py` empty.

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-05-28 | 13 (12 in-scope + 1 marked n/a) | 12 | 0 | Claude (gsd-security-auditor, RETROACTIVE-STRIDE mode) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer / n/a)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-05-28
