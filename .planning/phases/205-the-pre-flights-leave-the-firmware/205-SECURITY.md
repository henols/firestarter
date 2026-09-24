---
phase: "205"
slug: "the-pre-flights-leave-the-firmware"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-09-24"
---

# Phase 205 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

Register origin: the eight plan-time `<threat_model>` blocks in `205-01-PLAN.md` through
`205-08-PLAN.md`, 45 rows holding 38 distinct threats. `T-205-SC` is declared in all eight plans
and is listed once. `205-08-PLAN.md`, the CR-01 gap-closure plan, reuses the ids `T-205-20` to
`T-205-25` for six threats that differ from the `205-05` and `205-06` threats that first carry
those ids, so every one of those ids is qualified by its plan below. No SUMMARY carries a
`## Threat Flags` section, so no threat was added at execution time.

Verified at L1 (grep) depth against `firestarter_fw` `4b14111`, `firestarter_app` `5302f63` and
the meta repo, all on `v1.41-verification-to-host`. Phase 207.1 has since edited
`write_blank_guard.py`, `cli_handlers.py` and `eprom_operations.py`, so every host citation below
is to the current tree, not the 205-era one.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| CLI arguments → the erase operation | `-s` and `-b` are untrusted operator input whose combination selects incompatible behaviours. The decision must happen before any port opens. | CLI options |
| host → firmware (serial) | The write-init and erase-end pre-flights and the `0x08` control flag crossed here. After this phase the firmware performs no blank check and reads no `0x08`, and the post-erase verdict is a second, host-owned read. | command frames, control flags |
| any host → firmware JSON parser | The parser is the firmware's whole input-validation tier. A non-firestarter host, a corrupted frame or a replayed capture crosses here with no host-side guard in front of it. | JSON fields, notably `address` |
| wire address → the bus | A silently clamped address selects a different destination on the chip from the one the frame named. | write address |
| already-published host → live hardware | A shipped `3.0.0b49` host still composes `0x08` and still expects the firmware to refuse a non-blank write. | retired control flag |
| post-205 host ↔ pre-205 firmware | The accepted D-04 skew, crossed deliberately at bench leg B3. `MSG_ERR_NOT_BLANK` (0xB0) still crosses from old firmware. | refusal message ids |
| the erased part → the verdict a user acts on | A verdict that conflates "the link failed" with "the chip is not blank" is a fabricated claim about silicon. | blank verdict (exit 0/1/2) |
| host guard verdict → the physical device | Since 205-03 removed the firmware's write-init check, `requires_blank_check` is the only thing between a `CMD_WRITE` and a non-blank region. | guard decision |
| operator `-a <addr>` → `handle->address` | On protocol `0x06` this one field decides whether the erase covers the whole chip or one sector. | write start address |
| `FLAG_CAN_ERASE` (capability) → "this region is blank" (state) | A bit describing what a part can do was read as evidence of what the device is. | capability flag |
| firmware erase-scope knowledge ↔ host predicate | Duplicated across two repositories with no automated parity gate; a comment on each side and a test named after the firmware branch hold them together. | protocol behaviour |
| two constant ladders ↔ each other | Duplicated state across two repositories, held together only by the same-commit-pair rule. | control-flag values |
| meta catalog → both sub-repositories | `tools/catalog/messages.toml` is the one source of truth. An edit that reaches a generated artifact without a sync is drift. | message ids |
| source tree → source-scan gates and golden | Each gate reads source and path text as untrusted input. A mis-resolved path or an un-re-derived golden must fail, never silently pass. | source text |
| the devcontainer → CI | The two environments disagree about whether a module runs at all. A repair that makes the local tree green by making the module skip would hide the gate in both. | test collection |
| the sweep → the survivors | `mem_util_operation_end`, the `region-end` key and every in-algorithm verify sit inside the blast radius of the blank-check deletion. | surviving firmware symbols |
| measured build output → phase record | FWBLANK-05's figures are evidentiary claims about an artifact. A figure not taken from the tree that shipped is a fabricated record. | flash/RAM figures, digests |
| bench transcript → phase record and REL-04 | Everything the wiki claims about what a real user sees is sourced here. A paraphrased refusal is a fabricated quote. | transcripts, digests |
| detached worktree → live `firestarter_fw` tree | Building a different commit is one `git checkout` away from invalidating every digest and sha the phase recorded. | working tree |
| future author → a free-looking bit or id | `0x08` and the ids 0xB0, 0x08, 0x0B and 0x2E all become unused-looking numbers in files someone reads when allocating a new one. | reserved numbers |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-205-01 | Spoofing | the `erase -b` verdict | high | mitigate | `cli_handlers.py:1386-1394` exits on `check_eprom_blank`'s 0/1/2 verdict directly, with no mapping layer. Legs in `tests/test_cli_handlers.py`: exit 0 `:970`, exit 1 `:984`, exit 2 when the check itself fails `:998`, and no check after a failed erase `:1073`. | closed |
| T-205-02 | Spoofing | `erase -s <addr> -b` on protocol `0x06` | high | mitigate | `_erase_sector_blank_refusal_exit_code` (`cli_handlers.py:1112-1150`) refuses the combination before the wire with exit 2 and one line, naming `flash_nor_unlock.cpp:118-126` in its docstring; call site `:1341-1345`. Legs `tests/test_cli_handlers.py:1109` (refused before the erase) and `:1134` (`-s` without `-b` still runs). | closed |
| T-205-03 | Denial of Service | `erase -b`'s second port open | low | accept | See the Accepted Risks Log (AR-205-01). | closed |
| T-205-04 | Tampering | the `test_help_erase` snapshot | medium | mitigate | `tests/__snapshots__/test_characterization.ambr:164`. Hand-edited against the printed diff both times; `--snapshot-update` never run; the top-level command-list snapshot did not move (`205-01-SUMMARY.md:138,182`). | closed |
| T-205-06 | Repudiation | `tests/test_flash_path_record_sync.py` | high | mitigate | Recorded 41 passed, 0 skipped, no `MissingScanTargetError`, and the whole tree 320/320 (`205-02-SUMMARY.md:70,73,109-110`). Live on 2026-09-24: this module plus the verify-survival and branch-inventory gates ran 63 passed, 0 skipped. | closed |
| T-205-07 | Repudiation | `205-FLASH-RAM.md` (phase entry) | high | mitigate | Taken at `firestarter_fw` `a4e002f2` (`205-FLASH-RAM.md:14`). Six `.elf`/`.hex` digests (`:92-104`); both `pio run` invocations produced the same digests and figures character for character (`:106-107`). | closed |
| T-205-08 | Tampering | the three AVR images | low | accept | See the Accepted Risks Log (AR-205-02). | closed |
| T-205-09 | Tampering | the three write-init paths | high | mitigate | `GUARDED_PROTOCOL_IDS` is pinned to the five pre-flighted families (`write_blank_guard.py:58`) by `tests/test_write_blank_guard.py:113` and `tests/test_write_blank_guard_pinning.py:97`, which fail if the set narrows or widens. On silicon, bench leg B5 wrote to a non-blank UV target region on post-205 firmware, exit 0 (`205-BENCH-MATRIX.md:348-403`). | closed |
| T-205-10 | Denial of Service | post-205 host driving pre-205 firmware | high | accept | See the Accepted Risks Log (AR-205-03). Observed on silicon at B3 (`205-BENCH-MATRIX.md:243-309`). | closed |
| T-205-11 | Repudiation | `tests/golden/protocol_branch_inventory.json` | high | mitigate | Re-derived in `firestarter_fw` `1cf1b22`, the same commit as `src/proms/eprom.cpp`, `flash_intel.cpp` and `flash_nor_unlock.cpp`. Matched positionally, with 0 mismatches across 20 surviving pairs, before any line value was carried forward (`205-03-SUMMARY.md:62,69`). | closed |
| T-205-12 | Tampering | `mem_util_operation_end` and the `region-end` clamp | high | mitigate | Both survive: `include/memory_utils.h:34`, `src/proms/memory.cpp:428`, `src/json_parser.c:75,186`. Fenced by `tests/test_verify_survival_source_contract.py:608` and `:636` (`test_operation_end_is_defined_exactly_once_and_reads_both_members`). | closed |
| T-205-13 | Denial of Service | the commit boundary between the two tasks | medium | mitigate | Both commit boundaries left all four firmware CI legs green in order: native 241/241, native_nodevtools 241/241, pytest 315/315, and `pio run` success for uno, uno328pb and leonardo (`205-03-SUMMARY.md:100-103,132`). | closed |
| T-205-14 | Repudiation | the new absence legs | high | mitigate | Every new leg was run against the pre-sweep tree and its RED read for the intended reason (`205-03-SUMMARY.md:31`, § RED Transcripts `:209`). The absence leg is `tests/test_verify_survival_source_contract.py:669`, and the non-vacuity leg `:730` covers the scan targets. | closed |
| T-205-15 | Tampering | the `0x08` gap in both ladders | high | mitigate | Firmware: a reserved record at `include/firestarter.h:159-162`, gated by `tests/test_verify_survival_source_contract.py:553` and `:703`. Host: `firestarter/constants.py:130-141` names the release, the counterpart ladder and the never-reuse mechanism, gated by `tests/test_eprom_operations.py:2226`. | closed |
| T-205-16 | Denial of Service | post-205 host against pre-205 firmware | high | accept | See the Accepted Risks Log (AR-205-04). Observed on silicon at B3 (`205-BENCH-MATRIX.md:256,268`). | closed |
| T-205-17 | Spoofing | the two anti-regression comments | medium | mitigate | Both were rewritten to warn about the behaviour, "the host owns this refusal instead -- do not restore a firmware-side conditional", and neither was deleted: `src/proms/eeprom_28c.cpp:381-382`, `src/proms/flash_5v_page.cpp:72-73`. `FLAG_SKIP_BLANK_CHECK` appears nowhere in `src/` or `include/`. | closed |
| T-205-18 | Repudiation | the frozen `dedup_fingerprint` literal | high | mitigate | Re-derived, not copied: `927571e5110f`, identical to the frozen value at `tests/fixtures/report_shapes.py:755`. A re-key was therefore a measured no-op, and no commit re-keyed a hash alongside a behaviour change (`205-04-SUMMARY.md:71,144`). `test_blast_radius_invariance.py` is absent from `9a82478`'s file list. | closed |
| T-205-19 | Denial of Service | the host collection cliff | high | mitigate | `firestarter_app` `9a82478` moves `constants.py`, the five production sites (`chip_test.py`, `cli_handlers.py`, `eprom_operations.py`, `serial_comm.py`, `write_blank_guard.py`) and the harness (`tests/fake_chip.py` plus five test modules) in one commit. | closed |
| T-205-05 | Tampering | `simple_strtoul` on the `address` field | high | mitigate | `FIELD_POLICY_REJECT_NEGATIVE` (`src/json_parser.c:119`), applied by `FIELD_REJECT_NEGATIVE` (`:153-155`) on the `key_address` row (`:163`), makes `json_parse` return -1 before conversion. Native leg: `test/native/avr/test_read_timing/test_read_timing_params.cpp:462`. | closed |
| T-205-20 (205-05) | Tampering | the other seven `simple_strtoul` sites | medium | mitigate | The policy bit is set on exactly one table row (`src/json_parser.c:163`). Scope-guard native case T9: `test_read_timing_params.cpp:498`. | closed |
| T-205-21 (205-05) | Repudiation | the FWBLANK-05 arithmetic | medium | mitigate | Pre-fix (`9061dd1`) and post-fix (`6e11d05`) builds are both measured, in the fix's own section (`205-FLASH-RAM.md:111-176`); the Delta states each claim separately (`:259-291`). | closed |
| T-205-22 (205-06) | Repudiation | `205-FLASH-RAM.md` (phase exit) | high | mitigate | Three `firestarter_fw` commits are cited: `a4e002f2` (`:14`), `9061dd1` (`:125-126`) and `6e11d05` (`:176`). Each carries six digests from two identical `pio run` invocations (`:106-107,172-173,238-240`), and the three arithmetic claims are stated separately (`:259-291`). | closed |
| T-205-23 (205-06) | Spoofing | `MSG_ERR_NOT_BLANK` (0xB0) | high | mitigate | Kept, with an annotation that the host deliberately still renders it for pre-3.1.0 firmware (`tools/catalog/messages.toml:556-571`). The rendered sentence was captured on silicon at B3: `ERROR: Not blank, at 0x000000, v: 0x11` (`205-BENCH-MATRIX.md:256`). | closed |
| T-205-24 (205-06) | Tampering | the four orphaned catalog ids | medium | mitigate | All four are annotated "Not free for reuse", with the hazard stated as a mechanism: `tools/catalog/messages.toml:567` (0xB0), `:902` (`DBG_VERIFY_PROM`), `:928` (`DBG_BLANK_CHECK_PROM`), `:1156` (`DBG_FLAG_SKIP_BLANK`). | closed |
| T-205-25 (205-06) | Tampering | `messages.h` and `messages.py` in the sub-repos | high | mitigate | Re-verified live on 2026-09-24: `tools/catalog/codegen.py` regenerated both artifacts to scratch, and each is byte-identical to the committed file. Both sub-repo working trees are clean. | closed |
| T-205-26 | Repudiation | the criterion 3 and 5 claims | high | mitigate | Every leg in `205-BENCH-MATRIX.md` is a verbatim command with an explicit exit code and duration, bracketed by whole-device digests. Each UV leg carries the erasable-proxy note, so the record cannot be read as a claim about UV silicon. | closed |
| T-205-27 | Spoofing | the two firmware roles | high | mitigate | The role table names each role by commit sha and local `.hex` sha256, and states the label substitution because the host's port probe truncates a prerelease suffix (`205-BENCH-MATRIX.md:89-102`). | closed |
| T-205-28 | Tampering | the seated part | high | mitigate | A closed digest chain covers B2, B3, B5, B6 and B7, and every predicted difference is explained. B3 equals B2, proving the refused write had no side effect (`205-BENCH-MATRIX.md:507-519`). | closed |
| T-205-29 | Denial of Service | the B3 opportunity | medium | mitigate | B3, "on the pre-205 firmware, BEFORE any reflash" (`205-BENCH-MATRIX.md:243`), precedes B4, the post-205 flash (`:310`). | closed |
| T-205-30 | Tampering | the live `firestarter_fw` working tree | high | mitigate | The pre-205 build ran in a detached worktree outside both `/workspaces` and `firestarter_fw`, at `/home/vscode/.local/share/gsd205-fw-pre205-worktree`. The plan named the session scratch directory; the protection is the same. `firestarter_fw` never left `v1.41-verification-to-host`, and its cleanliness was re-verified at B0/B1 and B4 (`205-BENCH-MATRIX.md:104-106,119-124`). | closed |
| T-205-31 | Elevation of Privilege | `fw --install` | medium | mitigate | Every flash used `pio run -e leonardo -t upload`, and `fw --install` was explicitly not used (`205-BENCH-MATRIX.md:140,149`). Rig identity was re-confirmed at B0 (`:57-88,111-114`). | closed |
| T-205-20 (205-08) | Tampering | `is_erase_exempt` on `0x06` at a non-zero address | high | mitigate | `is_erase_exempt` takes a keyword-only `address` (`write_blank_guard.py:177-181`) and withdraws the exemption when `algorithm == NOR_UNLOCK_PROTOCOL_ID and address != 0` (`:223`). Legs `tests/test_write_blank_guard.py:171`, `:181`, `:566`, `:1079`. | closed |
| T-205-21 (205-08) | Spoofing | the flag-derived blankness claim | high | mitigate | The erase scope is an explicit input, not inferred from `FLAG_CAN_ERASE` (`write_blank_guard.py:177-181`). A refusal is produced only after the region is read off the device: `tests/test_write_blank_guard.py:566` (the guard read is paid) and `:1079` (a non-blank region is refused). | closed |
| T-205-22 (205-08) | Denial of Service | the 190-row protocol-`0x06` family | medium | mitigate | The fix checks, it does not refuse. A blank non-zero-address region still writes after one guard read, `[COMMAND_READ, COMMAND_WRITE]` (`tests/test_write_blank_guard.py:566-594`); address 0 pays no read (`:1058`); `-b` still bypasses (`:224`). | closed |
| T-205-23 (205-08) | Repudiation | the phase record | medium | mitigate | `205-CR-01-DECISION.md` records the displaced alternative (§2), the regression provenance (§4) and the reversibility ratings (§5). | closed |
| T-205-24 (205-08) | Tampering | a future address-scoped guarded protocol | medium | mitigate | The constant's docstring records that `0x06` is the only guarded family whose erase reads `handle->address`, citing `flash_intel_erase_execute`'s hard-coded `0` and `eprom_internal_erase`'s missing address (`write_blank_guard.py:73-84`). Membership leg: `tests/test_write_blank_guard.py:237`. | closed |
| T-205-25 (205-08) | Information Disclosure | none applicable | low | accept | See the Accepted Risks Log (AR-205-05). | closed |
| T-205-SC | Tampering | npm/pip/cargo installs (all eight plans) | high | mitigate | `205-RESEARCH.md:958-963` records that the phase installs no external packages. No `(205-` commit in either sub-repo touches `pyproject.toml`, `requirements*`, `setup.*`, `platformio.ini` or a lock file. The bench drove the existing `.venv-ci-188`. | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-205-01 | T-205-03 | `erase -b` now opens a second port, which resets an Uno-class board between the erase and the check. An electrically erased part stays blank across a reset, so the cost is wall-clock only. The measured cost went to Phase 206 SESS-01. | planner (205-01-PLAN.md `<threat_model>`, D-01); confirmed by the operator in the `/gsd-secure-phase 205` prompt | 2026-09-24 |
| AR-205-02 | T-205-08 | No CI leg gates AVR image size. FWBLANK-05 asks for a measurement, not a gate, and `205-FLASH-RAM.md` records the measurement. | planner (205-02-PLAN.md `<threat_model>`); confirmed by the operator in the `/gsd-secure-phase 205` prompt | 2026-09-24 |
| AR-205-03 | T-205-10 | A post-205 host no longer composes the skip flag, so pre-205 firmware's surviving pre-flight refuses `write -b` on a non-blank UV part where it used to work. Observed on silicon at B3 and documented for users by REL-04 in Phase 207. A host firmware-version gate is out of scope under activation decision D-4. | operator: 205 D-04 at discussion ("Full retirement — requirement stands", with this cost stated; `205-DISCUSSION-LOG.md` § The `0x08` bit), confirmed in the `/gsd-secure-phase 205` prompt | 2026-09-24 |
| AR-205-04 | T-205-16 | `write -b` on a non-blank UV part and `dev test`'s masked UV slot writes are refused by pre-205 firmware where they used to work. Same D-04 skew as AR-205-03; the host structurally cannot read a firmware prerelease suffix, so no version gate could name it. | operator: 205 D-04 at discussion (`205-CONTEXT.md` D-04), confirmed in the `/gsd-secure-phase 205` prompt | 2026-09-24 |
| AR-205-05 | T-205-25 (205-08) | The CR-01 fix reads no new data, logs no new data and emits no new wire field. Its one extra read is of the operator's own device, into memory the guard already handles. | planner (205-08-PLAN.md `<threat_model>`); confirmed by the operator in the `/gsd-secure-phase 205` prompt | 2026-09-24 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-09-24 | 38 (45 plan rows; `T-205-SC` declared in all eight plans) | 38 | 0 | `/gsd-secure-phase` orchestrator in the main session, from `/gsd-execute-phase 207.1` plan 06 (L1 grep; no auditor spawned) |

## Security Audit 2026-09-24
| Metric | Count |
|--------|-------|
| Threats found | 38 |
| Closed | 38 (33 mitigated, 5 accepted) |
| Open | 0 |

The short-circuit did not apply. At classification, all 33 `mitigate` threats were closed on
evidence, but none of the five `accept` threats was yet documented in a SECURITY.md, so
`threats_open` was 2 (T-205-10 and T-205-16, both high). The workflow therefore stopped at its
user gate. The operator chose "Accept all open — document in accepted risks log", which produced
the five rows above. No auditor was spawned: the five had no mitigation to verify.

Live corroboration on 2026-09-24, on Python 3.11.16 with `pytest -o addopts="" -p no:cacheprovider`:

- `firestarter_app` `tests/test_write_blank_guard.py`, `tests/test_write_blank_guard_pinning.py`
  and the retired-flag leg in `tests/test_eprom_operations.py`: **75 passed**.
- `firestarter_app` `tests/test_cli_handlers.py -k erase`: **13 passed**.
- `firestarter_fw` `tests/test_flash_path_record_sync.py`,
  `tests/test_verify_survival_source_contract.py` and `tests/test_protocol_branch_inventory.py`:
  **63 passed, 0 skipped**.
- `messages.h` and `messages.py` regenerated from `tools/catalog/messages.toml` to scratch:
  byte-identical to the committed files.

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-09-24
