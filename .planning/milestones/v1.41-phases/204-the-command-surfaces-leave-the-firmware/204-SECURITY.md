---
phase: "204"
slug: "the-command-surfaces-leave-the-firmware"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-09-24"
---

# Phase 204 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

Register origin: the five plan-time `<threat_model>` blocks in `204-01-PLAN.md` through
`204-05-PLAN.md` (30 threats). No SUMMARY carries a `## Threat Flags` section, so no threat was
added at execution time. Verified at L1 (grep) depth against `firestarter_fw` `4b14111`,
`firestarter_app` `5302f63` and the meta repo, all on `v1.41-verification-to-host`.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| host → firmware (serial, 250000 baud, COBS-framed JSON) | Every command ordinal crosses here. A frame from an already-shipped host is untrusted input the firmware cannot negotiate with. | command ordinals, JSON parameters |
| already-published host → live hardware | The `3.0.0b49` wheel cannot be changed and composes ordinals 4 and 6, which the firmware no longer implements. | retired ordinals |
| PyPI → this machine | The pinned old-host wheel is fetched into a throwaway venv. | third-party package |
| firmware image → attached board | On Leonardo the linker no longer protects the top of flash, so an oversized image overwrites the bootloader. | firmware image |
| throwaway host → operator `~/.firestarter/` | The app writes its config under the home directory regardless of the environment variable. | local config |
| firmware source → source-scan gates and golden | Each gate reads source text as untrusted input. A mis-resolved path or an un-re-derived golden must fail. | source text |
| stubbed hardware → native test | A stub that does nothing produces an empty frame capture. | captured frames |
| meta catalog → sub-repo generated artifacts | `tools/catalog/messages.toml` is the only source of truth. Neither sub-repo may regenerate. | message ids |
| two constant ladders ↔ each other | Duplicated state across two repositories, held together only by the same-commit-pair rule. | ordinal numbers |
| documentation / planning record → future author | A stale citation or nomination is untrusted input to a later implementer or planner. | prose |
| bench observation → phase record | An unrecorded measurement is indistinguishable from an argument. | digests, transcripts |
| executor → `beta` branches | A push to `beta` publishes in both sub-repos and uploads to PyPI from the app. | releases |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-204-01 | Tampering | `is_memory_cmd` in `include/firestarter.h` | high | mitigate | `is_memory_cmd` admits only READ, WRITE, ERASE, CHECK_CHIP_ID, SDP_UNLOCK, SDP_LOCK, LOCK_STATUS (`include/firestarter.h:134-146`). Ordinal 6 is absent. The source-contract gate's `test_neither_retired_ordinal_appears_in_the_admission_predicate` guards it. On-part byte-identity is in `204-BENCH-TRACER.md` (`cmp tracer-pre.bin tracer-post.bin` exits 0 over 65536 bytes). | closed |
| T-204-02 | Spoofing | two command ladders | medium | mitigate | Never-reuse notes sit at the gap on both ladders: `include/firestarter.h:65-73` and `firestarter_app/firestarter/constants.py:56-69`. | closed |
| T-204-03 | Denial of Service | dispatch `default:` arm | medium | mitigate | `src/firestarter.cpp:332-338`: `default:` logs `MSG_ERR_UNKNOWN_CMD`, sets `finished`, calls `command_done()`. Old-host runs were bounded by `timeout 300` (`204-BENCH-MATRIX.md:184,206`). | closed |
| T-204-04 | Tampering | `rurp_pinmap_refuses` in `include/rurp_pinmap_guard.h` | low | accept | See the Accepted Risks Log. Delegation is compiled only under `RURP_PINMAP_PROVISIONAL`, which defaults to 0 (`include/rurp_pinmap_guard.h:46-52`). | closed |
| T-204-05 | Tampering | seated W27C512 during refusal legs | high | mitigate | `204-BENCH-TRACER.md:94-196`: before/after reads of 65536 bytes each, `cmp` exits 0. | closed |
| T-204-SC | Tampering | `uv pip install 'firestarter==3.0.0b49'` | high | mitigate | The operator approved it at the human-verify gate on 2026-09-22 (`204-BENCH-TRACER.md:20-21`). The version was pinned exactly and installed into a throwaway venv outside both sub-repos (`:115`). The install location and version were asserted (`:121`). | closed |
| T-204-06 | Elevation of Privilege | `beta` branches, all three repos | high | mitigate | All three HEADs are absent from `origin/beta` (`git merge-base --is-ancestor` false). `v1.41-verification-to-host` is not on any remote. | closed |
| T-204-07 | Tampering | `tests/test_verify_survival_source_contract.py` | high | mitigate | Containment is brace-matched (module docstring, Coverage 1-2). Both violation shapes, deleted and moved, were planted into the real file and their REDs captured verbatim (`204-02-SUMMARY.md:46,65,93`). | closed |
| T-204-08 | Spoofing | gate scan-target resolution | medium | mitigate | `_HERE = Path(__file__).resolve().parent` (`:177`). The non-vacuity leg recomputes the default path fresh from the repository root, never from the environment seam (docstring `:78`). | closed |
| T-204-09 | Repudiation | native id assertions | high | mitigate | `test/native/avr/test_verify_error_ids/test_verify_error_ids.cpp` asserts `verify_ids_frame_count > 0` before each id group (`:205,248,300,329,359,389`). The single `== 0` leg at `:270` is a deliberate emits-nothing case. Three transposed-id REDs were observed (`204-02-SUMMARY.md:65`). | closed |
| T-204-10 | Denial of Service | `platformio.ini` `[native_base]` | medium | mitigate | The suite is registered in the shared `[native_base]` `test_filter` (`platformio.ini:106,133`) and inherited by both native environments. It ran 8/8 under `native_nodevtools` (`204-02-SUMMARY.md:61`). | closed |
| T-204-11 | Tampering | `src/proms/eprom.cpp` during planted runs | high | mitigate | `git status --porcelain` / `git diff` confirmed empty after each restore, before commit (`204-02-SUMMARY.md:69,93`). | closed |
| T-204-12 | Tampering | admission predicate | high | mitigate | Neither ordinal 4 nor 6 is in `is_memory_cmd`. `CMD_VERIFY` and `CMD_BLANK_CHECK` identifiers appear nowhere in `include/firestarter.h` or `src/firestarter.cpp`. Committed absence legs 7-9 are in the source-contract gate. | closed |
| T-204-13 | Spoofing | two command ladders (gated) | medium | mitigate | Firmware: gate leg `test_all_three_reserved_gaps_carry_a_recorded_reason`. Host: `test_neither_retired_ordinal_is_defined_or_named_on_the_host_ladder` (`firestarter_app/tests/test_eprom_operations.py:2192`) asserts absence plus at least 2 reserved-marker occurrences. | closed |
| T-204-14 | Repudiation | `tests/golden/protocol_branch_inventory.json` | high | mitigate | Re-derived by the gate's own extractor. A positional diff showed 22 sites, zero non-line divergences, and counts unchanged. It landed in the same commit as `src/proms/eprom.cpp` (`204-03-SUMMARY.md:17,32,123-127`). | closed |
| T-204-15 | Tampering | `test_val_eprom` chunking contract | high | mitigate | Re-keyed to a direct function-pointer assignment in the same commit as the arm deletion, then run green (`204-03-SUMMARY.md:87,201`). | closed |
| T-204-16 | Denial of Service | three-commit boundary | medium | mitigate | All four CI legs (native, native_nodevtools, pytest) ran green immediately after each commit (`204-03-SUMMARY.md:87`). | closed |
| T-204-17 | Elevation of Privilege | `beta` branches | high | mitigate | Same evidence as T-204-06. | closed |
| T-204-18 | Tampering | `tools/catalog/messages.toml` + synced artifacts | high | mitigate | The validator exited 0. Two mktemp regenerations came out byte-identical to `messages.h` and `messages.py`. Both sub-repo porcelains were clean, and the sync script was not run (`204-04-SUMMARY.md:59-63`). | closed |
| T-204-19 | Spoofing | two orphaned debug ids | medium | mitigate | Both kept, each with a retired-emit-site and never-reuse comment (`tools/catalog/messages.toml:896-898,922-924`). | closed |
| T-204-20 | Repudiation | `firestarter_fw/PROTOCOLS.md` invariant table | medium | mitigate | The fabricated `test_inv05_eprom_vpp_skip_on_read` (0 `git grep` hits) was repointed to `test_eprom_0x07_read_configure_only_does_not_enable_vpp`. That test exists in `test_val_eprom.cpp`, and PROTOCOLS.md cites it. The real-test outcome is recorded in `204-04-SUMMARY.md:152`. | closed |
| T-204-21 | Information Disclosure | none applicable | low | accept | See the Accepted Risks Log. | closed |
| T-204-22 | Elevation of Privilege | `beta` branches (docs-only commits) | high | mitigate | Same evidence as T-204-06. | closed |
| T-204-23 | Tampering | seated W27C512 across swap and refusals | high | mitigate | Three whole-device reads (pre-swap, post-swap, post-refusal) of 65536 bytes share one SHA-256, `a094e902…ae43` (`204-BENCH-MATRIX.md:413-421,461`). | closed |
| T-204-24 | Denial of Service | published host's command drive | high | mitigate | Both refusal legs were bounded by `timeout 300`. Measured durations were 11.00 s (verify) and 4.92 s / 4.85 s (blank), so neither leg stalled (`204-BENCH-MATRIX.md:184-220`). | closed |
| T-204-25 | Repudiation | `204-BENCH-MATRIX.md` | high | mitigate | The role table names every role by sha or pinned version (for example, pre-204 firmware `e5842d8c…`). Commands are recorded verbatim (`204-BENCH-MATRIX.md:48-82,184,206`). | closed |
| T-204-26 | Tampering | attached board's USB bootloader | high | mitigate | Every build line carries a `bootloader-guard:` assertion. Leonardo came in at 24134/28672 B with a 4538 B margin (`204-BENCH-MATRIX.md:103-119,287`). | closed |
| T-204-27 | Information Disclosure | operator `~/.firestarter/` | medium | mitigate | Snapshotted by move, restored by move, never deleted. The final state matches the phase start (`204-BENCH-MATRIX.md:313-319`). | closed |
| T-204-28 | Spoofing | pre-204 firmware artifact | medium | mitigate | Built from a detached worktree at `e5842d8ceacac45e8640cd274947e7ee6c88fb58`, never a downloaded asset (`204-BENCH-MATRIX.md:48-49,69`). | closed |
| T-204-29 | Elevation of Privilege | `beta` branches | high | mitigate | Same evidence as T-204-06. | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-204-01 | T-204-04 | Narrowing `is_memory_cmd` makes `rurp_pinmap_refuses(6)` false. The guard runs only inside `configure_memory`, which a retired ordinal never reaches. `RURP_PINMAP_PROVISIONAL` defaults to 0 in every AVR environment. | plan-time disposition (204-01-PLAN.md) | 2026-09-21 |
| AR-204-02 | T-204-21 | Plan 04 touches only documentation and a message catalog. No secret, credential or user data crosses any boundary it changes. | plan-time disposition (204-04-PLAN.md) | 2026-09-21 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-09-24 | 30 | 30 | 0 | /gsd-secure-phase orchestrator (L1 grep, auditor skipped by short-circuit: register authored at plan time, ASVS 1) |

## Security Audit 2026-09-24
| Metric | Count |
|--------|-------|
| Threats found | 30 |
| Closed | 30 (28 mitigated, 2 accepted) |
| Open | 0 |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-09-24
