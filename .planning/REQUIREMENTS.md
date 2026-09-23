# Requirements: Firestarter — v1.41 Verification Moves to the Host

**Defined:** 2026-09-20
**Milestone:** v1.41 — "The Arduino programs; the host decides whether it worked"
**Core Value (this milestone):** Every comparison the product makes runs in one place, on the host,
where it can say *why* a chip failed instead of naming one address — and the firmware keeps only the
verification its programming algorithms cannot run without.

**Scope:** The host comparison path (`firestarter_app/firestarter/eprom_operations.py`,
`cli_handlers.py`, `chip_test.py`, `diagnostic_report.py`), the firmware command surfaces and
in-algorithm pre-flight blank checks (`firestarter_fw/src/firestarter.cpp`, `eprom_operations.cpp`,
`proms/memory.cpp`, `proms/eprom.cpp`, `proms/flash_intel.cpp`, `proms/flash_nor_unlock.cpp`,
`include/firestarter.h`, `include/memory_utils.h`), and a version bump in both repositories. No
protocol dispatch changes beyond the retirement of two command ordinals. No chip database change.

**Provenance:** Pending todo
[`2026-08-30-remove-cmd-verify-from-firmware-compare-in-app.md`](todos/pending/2026-08-30-remove-cmd-verify-from-firmware-compare-in-app.md)
(filed 2026-08-30) scoped the verify half and named the constraint that governs this whole milestone:
`memory_verify_execute` must survive, because `eprom.cpp` calls it for `VERIFY_PER_PULSE_PLUS_FINAL`.
The blank-check half is provoked by
[`2026-08-30-write-init-blank-check-is-whole-device.md`](todos/pending/2026-08-30-write-init-blank-check-is-whole-device.md)
and by v1.40 Phase 201's review finding
[`2026-09-20-blank-check-region-fails-open-on-start-greater-than-end.md`](todos/pending/2026-09-20-blank-check-region-fails-open-on-start-greater-than-end.md),
which observed that the blank check's safety property was enforced in a different function in a
different file from the one that needed it. Moving the whole check to the host settles that by
removing the split rather than patching it. Seed
[`dev-test-adaptive-sequencing`](seeds/dev-test-adaptive-sequencing.md) R4 is pulled in because this
milestone provokes it: a pre-write blank check, a write and a `--verify` are three separate serial
port opens under today's `EpromOperator.comm`-is-`None`-after-every-call shape.

**Measured today:** the firmware's `memory_verify_execute` aborts at the first mismatching byte and
reports one address. The host's `classify_fingerprint` / `_diff_offsets` in `chip_test.py` already
name *why* a compare failed across four buckets and count total against bad — so `dev test` has been
strictly more informative than `firestarter verify` since v1.21. Test surfaces that move with this
change: **13 firmware test files, 17 app test files**, and the `protocol_branch_inventory.json`
golden.

## Decisions taken at activation (operator, 2026-09-20)

| | Decision |
|---|---|
| **D-1** | **All of it, both halves.** The standalone `CMD_BLANK_CHECK` / `CMD_VERIFY` command surfaces AND the in-algorithm write-init and erase-end pre-flight blank checks leave the firmware. This retires `mem_util_blank_check_region` five weeks after Phase 201 created it, and re-lands the region property on the host. |
| **D-2** | **The host pre-write blank check is exempt on erasable parts.** A part carrying `FLAG_CAN_ERASE` is erased immediately before the write, so the check has always passed trivially. Only UV parts pay the read. The consequence is accepted deliberately: with the device-side refusal gone, this host check is the whole safety net, with no second line of defence. Its reasoning must be explicit in the code and pinned by a test, not left as a remembered argument. |
| **D-3** | **Post-write verify is opt-in.** `write --verify` chains a read-back compare of the written region. Default write time is unchanged. |
| **D-4** | **Clean break on the protocol.** Ordinals 4 and 6 are retired outright, not deprecated. A new host against old firmware is safe without a version gate, because it only ever sends `CMD_READ`. |
| **D-5** | **`3.1.0b1` in both repositories.** A minor bump, beta series, stable line untouched. The first version-string movement since `3.0.0b48` / `3.0.0b33`. |
| **D-6** | **Seed R4 rides along.** One leased serial session per `dev test` plan instead of one open per call. |
| **D-7** | **Removing a command surface is not removing verification.** The per-pulse verify inside the EPROM program loop, `eeprom28c_verify_page_readback`, `flash_util_verify_operation` and `MSG_ERR_VERIFY` (0xAF) are load-bearing and untouched. A UV program loop cannot decide whether to pulse again without its verify. |

## v1 Requirements

### CMP — one comparison engine, on the host (D-1, D-7)

- [x] **CMP-01**: `firestarter verify <chip> <file>` compares the chip against the file by reading the chip; no `CMD_VERIFY` is sent on the wire.
- [x] **CMP-02**: `firestarter blank <chip>` compares the chip against a constant `0xFF` through that same engine; no `CMD_BLANK_CHECK` is sent on the wire.
- [x] **CMP-03**: the comparison runs on each chunk as it arrives; the device image is never materialised whole in host memory, and peak host memory for a compare is bounded independently of device size.
- [x] **CMP-04**: by default the comparison stops at the first mismatching byte — the host breaks the read in flight rather than draining it — and reports that mismatch as a single `start–end` range with a byte count, in the same one-line form `--full` uses. **No expected or actual byte values are printed** (operator decision, 2026-09-20, recorded as D-13 in `phases/202-one-comparison-engine-on-the-host/202-CONTEXT.md`; this requirement previously asked for the expected value and the value read).
- [x] **CMP-05**: `--full` scans the whole region and reports every mismatching span as a coalesced `start–end` range with a byte count, instead of one address.
- [x] **CMP-06**: a failed comparison is classified through the existing `classify_fingerprint`, naming one of its honest buckets with total and bad counts — computed from streamed accumulation, never from a materialised image.
- [x] **CMP-07**: `verify` and `blank` keep their exit-code contract — `0` on match, `1` on mismatch — and a hardware or transport failure is distinguishable from a mismatch.
- [x] **CMP-08**: both accept `--address` and `--size`, and a region-scoped comparison reads and compares only that region.

### FWCMD — the command surfaces leave the firmware (D-1, D-4, D-7)

- [x] **FWCMD-01**: `CMD_VERIFY` (6) and `CMD_BLANK_CHECK` (4) are gone from the `firestarter.cpp` dispatch switch, from `is_memory_cmd`, and from `configure_memory`'s switch.
- [x] **FWCMD-02**: the `eprom_verify()` and `eprom_blank_check()` wrappers and their declarations are deleted.
- [x] **FWCMD-03**: ordinals 4 and 6 are recorded as reserved and never reused, with the reason stated where a future author will read it before reaching for a free slot.
- [x] **FWCMD-04**: `memory_verify_execute` still exists and is still called for `VERIFY_PER_PULSE_PLUS_FINAL` on protocols `0x07` / `0x08`; a test fails if that call disappears.
- [x] **FWCMD-05**: each in-algorithm verify still raises its own failure id on failure, proven by test and not by inspection: `memory_verify_execute` and `eeprom28c_verify_page_readback` raise `MSG_ERR_VERIFY` (0xAF); the per-pulse verify's budget exits raise `MSG_ERR_MAX_PULSES` (0xBD) and `MSG_ERR_ENERGY_CAP` (0xBE); `flash_util_verify_operation` is a DQ7 data-poll wait and raises `MSG_ERR_OP_TIMEOUT` (0xB7) — it can never raise 0xAF, and asserting that it does would be a false pin. Each assertion names the id, not merely a generic error response code (operator decision, 2026-09-21, recorded as D-03 in `phases/204-the-command-surfaces-leave-the-firmware/204-CONTEXT.md`; this requirement previously claimed `MSG_ERR_VERIFY` (0xAF) was still raised by all three named sites — measurement against the live source showed only `eeprom28c_verify_page_readback` actually raises 0xAF, the per-pulse verify's budget exits raise two different ids, and `flash_util_verify_operation` has no compare-and-report path at all and can never raise 0xAF).
- [x] **FWCMD-06**: a host that sends ordinal 4 or 6 to `3.1.0b1` firmware receives an explicit refusal with no hardware side effect — never silence, never a hang. Proven on real hardware in `phases/204-the-command-surfaces-leave-the-firmware/204-BENCH-MATRIX.md` (plan 05): the published `3.0.0b49` host is refused with `Unknown command: 6` and `Unknown command: 4` against post-204 firmware, both promptly (~3.5s), both non-empty; three whole-device reads before and after both refusals share one SHA-256 digest, ruling out a silent erase. Per D-07, neither side carries the literal `3.1.0b1` string yet — that bump is Phase 207's — so this is proven via the documented label substitution, not against a build carrying that exact version.

### FWBLANK — the in-algorithm pre-flights leave the firmware (D-1, D-2)

- [x] **FWBLANK-01**: the write-init blank check is removed from `eprom.cpp`, `flash_intel.cpp` and `flash_nor_unlock.cpp`.
- [x] **FWBLANK-02**: the erase-end blank check is removed from `eprom.cpp`.
- [x] **FWBLANK-03**: `mem_util_blank_check`, `mem_util_blank_check_region`, `blank_check_saved_address` and `BLANK_CHECK_CHUNK_SIZE` are deleted, and no caller remains.
- [x] **FWBLANK-04**: `FLAG_SKIP_BLANK_CHECK` (`0x08`) is retired from the firmware and from `constants.py`, and the bit is recorded as reserved on both sides.
- [x] **FWBLANK-05**: the flash and RAM freed is measured per AVR target (uno, uno328pb, leonardo) and reported as a number, not an estimate.

### WRITE — the host takes over the write guard (D-2, D-3)

- [x] **WRITE-01**: before writing to a part that does not carry `FLAG_CAN_ERASE`, the host reads the target region and refuses the write if it is not blank, naming the first non-blank address and its value.
- [x] **WRITE-02**: the guard applies to exactly the protocol families whose firmware write-init blank-checks today — `0x07`, `0x08`, `0x0B`, `0x06`, `0x10` — and within those, a part whose erase actually ran is exempt from the read; SRAM/FRAM and protocol `0x05` are named exemptions whose reasoning is stated at the exemption site, and a test pins that exact guarded set and fails if it **narrows or widens** (operator decision, 2026-09-21, recorded as D-01/D-02 in `phases/203-the-write-guard-moves-up-a-layer/203-CONTEXT.md`; this requirement previously exempted any part carrying `FLAG_CAN_ERASE` and pinned only against widening beyond that flag — measurement across every firmware write-init path showed that wording would make the host start refusing non-blank writes on protocol `0x05` and on every SRAM/FRAM part, families the firmware has never checked).
- [x] **WRITE-03**: `write -b` / `--no-blank-check` skips the host check and still does not skip erase.
- [x] **WRITE-04**: `write --verify` runs a read-back comparison of the written region through the CMP engine, and reports through it.
- [x] **WRITE-05**: a `write --verify` whose comparison fails exits non-zero and says the write landed but did not verify — never "successful".
- [x] **WRITE-06**: a non-blank, non-erasable part accepts a region write into a blank region — and still does after the firmware check is gone. v1.40 Phase 201 already region-scoped the firmware pre-flight, so this passes today; the 2026-08-30 todo's "must be seen RED first" framing predates that fix and does not apply. The risk this pins is **silent re-breakage** when the guard moves to the host, so the test must exercise the host path and fail if the host refuses a blank region on a non-blank part.

### DEVTEST — `dev test` keeps its fidelity (D-6)

- [x] **DEVTEST-01**: `OP_VERIFY` and `OP_BLANK_CHECK` route through the rewritten host methods and produce a fingerprint at least as informative as today's.
- [x] **DEVTEST-02**: a report from the host-side comparison path is distinguishable from one produced by the firmware path, using the established empty-default discriminator discipline, so no already-filed `dedup_fingerprint` group is silently re-keyed and no two mechanically different runs silently merge.
- [x] **DEVTEST-03**: `dev test`'s step verdicts for a physically identical outcome do not change meaning; where a classification does change, the change is stated and justified rather than absorbed.

### SESS — one leased serial session per plan (D-6, seed R4)

- [x] **SESS-01**: a `dev test` plan opens one validated serial link and reuses it across its steps, instead of one open and teardown per call.
- [ ] **SESS-02**: the wall-clock saving is measured on a real run and reported as a number; if it is not worth the structural change, that is recorded and the change is reverted rather than kept on principle.

### REL — version, compatibility and the record (D-4, D-5)

- [ ] **REL-01**: both repositories carry `3.1.0b1`, and the two version strings are bumped in the same commit pair.
- [x] **REL-02**: a `3.1.0b1` host against pre-`3.1.0` firmware performs `verify` and `blank` correctly, because it only sends `CMD_READ`. Proven, not assumed. Proven on real hardware in `phases/204-the-command-surfaces-leave-the-firmware/204-BENCH-MATRIX.md` (plan 05): the post-204 host's `verify` matches (exit 0) and `blank` reports not-blank (exit 1, via the documented abort-predicate fast path) against pre-204 firmware, with no unknown-command line in either output. Per D-07, "3.1.0b1" here means the post-204 host label, not the literal version string, which is Phase 207's bump.
- [x] **REL-03**: a pre-`3.1.0` host against `3.1.0b1` firmware fails `verify` and `blank` with a refusal the user can act on, and with no hardware side effect. Proven on real hardware in `phases/204-the-command-surfaces-leave-the-firmware/204-BENCH-MATRIX.md` (plan 05): the published `3.0.0b49` host is refused with `Unknown command: 6` and `Unknown command: 4` against post-204 firmware, both captured verbatim with exit code and duration; three whole-device reads share one digest, proving no hardware side effect. Per D-07, "3.1.0b1" here means the post-204 firmware label, not the literal version string, which is Phase 207's bump.
- [ ] **REL-04**: the breaking change and the `write --verify` / `--full` surfaces are documented in the wiki, which is the only documentation home.

## Future Requirements

Tracked, not in this milestone.

| ID | Requirement | Why deferred |
|---|---|---|
| **CMP-F1** | A protocol-level abort for a read in flight, so a first-mismatch stop saves time and not only output | No abort message exists and the END phase must still run to leave the port clean. Adding one is a protocol change of its own, and this milestone is already retiring two ordinals. **Measured at Phase 204 (D-12):** a cheaper `DONE`-based clean stop was offered there and declined. The firmware half genuinely is one line — `op_wait_for_ack` returns on `OP_MSG_ACK` and `OP_MSG_ERROR`, and `OP_MSG_DONE` falls through to the retry delay and the existing one-second timeout. The host half is not one line — today's host aborts by withholding acknowledgements, sending nothing at all, and `_drive_region_compare`'s four-condition discrimination keys on `last_firmware_error_code == MSG_ERR_TIMEOUT`, a code a clean stop would no longer produce; both sides must move together, and the surface they would rework is `verify`, the one Phase 202 had just built. What makes deferring free: pre-`3.1.0` firmware's `op_get_message` already parses `"DONE"` into its own `OP_MSG_DONE` enumeration value and `op_wait_for_ack` already ignores it, so a future host that sends it to pre-`3.1.0` firmware degrades to exactly today's one-second timeout path. The change is forward-compatible by construction and can land in any later phase with the same properties |
| **CMP-F2** | Reach or retire `classify_fingerprint`'s `transport` bucket | Dead code because `_dispatch_multi_run` is always called with `runs=1`; it belongs to the Phase 178 fault-attribution design, not here |
| **PROTO-F1** | Replace the jsmn/JSON command layer with fixed-layout binary frames | Seed `binary-command-protocol` triggered on this milestone and was deliberately left planted — ~512 B RAM and ~1–1.5 KB flash, but its own milestone, not a rider |

## Out of Scope

| Feature | Reason |
|---------|--------|
| Removing any in-algorithm verify | D-7. A UV program loop cannot decide whether to pulse again without its verify; `eprom.cpp` calls `memory_verify_execute` directly |
| Removing `MSG_ERR_VERIFY` (0xAF) | Still raised by three surviving in-algorithm verifies. `messages.h` is codegen-generated from meta's `messages.toml` and is never hand-edited |
| A deprecation window for ordinals 4 and 6 | D-4. Keeping them working keeps the flash, which is the thing being reclaimed |
| A host firmware-version gate on `verify` / `blank` | Unnecessary in the direction that matters, and the host structurally cannot read a firmware pre-release suffix anyway |
| Making `write --verify` the default | D-3 |
| Chip database or generator changes | v1.40 owns that axis; nothing here reads a decoded parameter |
| A stable `3.1.0` release | D-5. Stable stays operator-gated |

## Traceability

Every requirement maps to exactly one phase.

| Requirement | Phase | Status |
|-------------|-------|--------|
| CMP-01 | Phase 202 | Complete |
| CMP-02 | Phase 202 | Complete |
| CMP-03 | Phase 202 | Complete |
| CMP-04 | Phase 202 | Complete |
| CMP-05 | Phase 202 | Complete |
| CMP-06 | Phase 202 | Complete |
| CMP-07 | Phase 202 | Complete |
| CMP-08 | Phase 202 | Complete |
| WRITE-01 | Phase 203 | Complete |
| WRITE-02 | Phase 203 | Complete |
| WRITE-03 | Phase 203 | Complete |
| WRITE-04 | Phase 203 | Complete |
| WRITE-05 | Phase 203 | Complete |
| WRITE-06 | Phase 203 | Complete |
| FWCMD-01 | Phase 204 | Complete |
| FWCMD-02 | Phase 204 | Complete |
| FWCMD-03 | Phase 204 | Complete |
| FWCMD-04 | Phase 204 | Complete |
| FWCMD-05 | Phase 204 | Complete |
| FWCMD-06 | Phase 204 | Complete |
| REL-02 | Phase 204 | Complete |
| REL-03 | Phase 204 | Complete |
| FWBLANK-01 | Phase 205 | Complete |
| FWBLANK-02 | Phase 205 | Complete |
| FWBLANK-03 | Phase 205 | Complete |
| FWBLANK-04 | Phase 205 | Complete |
| FWBLANK-05 | Phase 205 | Complete |
| DEVTEST-01 | Phase 206 | Complete |
| DEVTEST-02 | Phase 206 | Complete |
| DEVTEST-03 | Phase 206 | Complete |
| SESS-01 | Phase 206 | Complete |
| SESS-02 | Phase 206 | Pending |
| REL-01 | Phase 207 | Pending |
| REL-04 | Phase 207 | Pending |

**Coverage:**

- v1 requirements: 34 total
- Mapped to phases: 34
- Unmapped: 0 ✓

---
*Requirements defined: 2026-09-20*
*Last updated: 2026-09-20 at milestone activation*
