# Phase 9: Delete Old Log Macros + Measure Flash Savings - Context

**Gathered:** 2026-05-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Strip the last legacy log infrastructure from firmware, bump the firmware major version, and record the milestone-level flash measurement. After Phase 9, the only text the firmware emits is one hand-coded `OK: FW: <version>` bootstrap line at LFW-05 handshake — every other byte on the wire is an ID frame.

**Deleted in Phase 9 (firmware):**
- `send_ack` / `send_ack_const` macros (`logging.h`)
- `rurp_log` / `rurp_log_P` (weak defaults + Uno strong override)
- `_firestarter_log_ram` / `_firestarter_log_progmem` helpers (`rurp_serial_utils.cpp`)
- `LOG_OK_MSG[] PROGMEM = "OK"` (`logging.c`)
- `debug_setup()` + `log_debug()` (SERIAL_DEBUG-only; no remaining callers after `rurp_log` goes)
- Function declarations in `rurp_shield.h` / `rurp_serial_utils.h` for the above

**Touched in Phase 9 (firmware):**
- `fw_get_version()` in `hardware_operations.cpp` — `send_ack_const(FW_VERSION)` replaced with an inline `SERIAL_PORT.print(F("OK: FW: ")); SERIAL_PORT.println(FW_VERSION); SERIAL_PORT.flush();` three-liner.
- `dt_dump_register` + `dt_set_address` in `dev_tools.cpp` — two `send_ack("")` sites converted to `LOG_OK_ID(MSG_OK_READY)`.
- `version.h` — bump `VERSION` from `"2.0.11-dev"` to `"3.0.0-dev"` (LFW-05 major bump; `-dev` stays until Phase 10 release tag).

**NOT in Phase 9:**
- Phase 10 milestone-close documentation (DOC-02). Phase 9 produces `09-MEASUREMENT.md`; Phase 10 quotes its numbers.
- Stripping `-dev` to `3.0.0` on tag — Phase 10 release operation.
- v1.1 leftover items (FM1608, WARNING-4, DOC-01).

Phase 9 owns LFW-03, LFW-04, LMIG-04 (3 requirements). Success Criteria SC#1 (PROGMEM exemption audit), SC#2 (legacy macros zero hits), SC#3 (FW version handshake = `3.0.0-dev` + host pre-Phase-6 guard regression), SC#4 (Leonardo Flash < 90% with measurable headroom), SC#5 (Uno Flash recorded alongside).

</domain>

<decisions>
## Implementation Decisions

### LFW-05 bootstrap path

- **D-01: Inline the FW-version text emit directly in `fw_get_version()`.** Replace `send_ack_const(FW_VERSION)` at `hardware_operations.cpp:86` with:
  ```cpp
  SERIAL_PORT.print(F("OK: FW: "));
  SERIAL_PORT.println(FW_VERSION);
  SERIAL_PORT.flush();
  ```
  This is the ONLY remaining text-format emit in production firmware. It must produce a byte-identical line to today's output so the host's existing `_probe_port` "OK: FW: ..." text-prefix parsing (and the `FIRESTARTER_DEV_ALLOW_PRE_V12` escape hatch) continue to work without host-side changes. The `F(...)` macro keeps the `"OK: FW: "` literal in PROGMEM, but the string exists **inside the bootstrap function**, not as a separate named-symbol PROGMEM table — SC#1 explicitly exempts non-log PROGMEM and the `DATA:` marker; this inline literal falls in the same exemption category as `MAGIC_PREAMBLE` / `CRC8_TABLE`.
- **D-02:** Because of D-01, **all of** `send_ack`, `send_ack_const`, `rurp_log`, `rurp_log_P`, `_firestarter_log_ram`, `_firestarter_log_progmem`, and `LOG_OK_MSG` are deleted in Phase 9 (D-04 handles the prerequisite `send_ack("")` conversion). The entire `logging.h` macro tower collapses to a header that only re-exports `<avr/pgmspace.h>` + `firestarter.h` + `rurp_shield.h` (or possibly deletes `logging.h` outright — researcher to determine whether anything in `logging.h` is still referenced after this phase; the file itself may go).
- **D-03:** Test surface follow-on: `firestarter/test/native/avr/test_dispatch/host_stubs.cpp` references the deleted `LOG_*_MSG` PROGMEM strings as no-op resolution targets (per `firestarter/CLAUDE.md`'s "Native (Host) Test Environment" notes). After Phase 9 deletion, host_stubs.cpp must drop those symbols or stop referencing them; planner verifies `pio test -e native` still passes.

### dev_tools.cpp `send_ack("")` sites

- **D-04: Reuse `MSG_OK_READY` (0x01).** Convert both `send_ack("")` sites at `dev_tools.cpp:108` (`dt_dump_register`) and `dev_tools.cpp:154` (`dt_set_address`) to `LOG_OK_ID(MSG_OK_READY)`. The semantic stretch is minor — both functions are signalling "I've finished the setup phase and am now blocking on the user button; the host can proceed". No catalog growth. **Host-side verification (researcher):** confirm the host's existing consumer of `MSG_OK_READY` (currently emitted from `hardware_operations.cpp:42` `hw_read_voltage` startup ack) does not assume only that one emit-site — if it does, planner adds a sub_id discriminator or a dedicated catalog entry. If host treats it as a context-free ack token, the reuse is clean.
- **D-05:** With D-04 done, every `send_ack` / `send_ack_const` caller is gone, unblocking D-02's deletions.

### Version bump shape

- **D-06: `VERSION = "3.0.0-dev"`.** Bump in `firestarter/include/version.h:11` from `"2.0.11-dev"` to `"3.0.0-dev"`. Matches the existing `-dev` convention used throughout v1.0/v1.1/v1.2 development. The `-dev` suffix gets stripped to `"3.0.0"` on the release tag in Phase 10 (DOC-02 milestone close). Major bump = 3 satisfies the host's `major < 3` guard at `serial_comm.py:761` — SC#3 PASS without host code changes.
- **D-07:** SC#3 regression test wording: after Phase 9 firmware lands, running any non-`COMMAND_FW_VERSION` command against a pre-Phase-9 firmware (major < 3) MUST raise `FirmwareOutdatedError` with the "Please upgrade the firmware to v3.0.0 or later" message that the host has had wired since Phase 6. Test is exercised by a unit test that mocks a pre-v1.2 FW handshake reply OR by manual regression against an older firmware build (planner to choose; both already exist in `firestarter_app/tests/test_fwguard.py`).

### Flash measurement scope

- **D-08: Write `09-MEASUREMENT.md` with BOTH deltas.** Single artifact captures:
  1. **Phase 8 → Phase 9 incremental delta** — Leonardo + Uno + SRAM (attributes the legacy-deletion win precisely). Expected magnitude: ~50–300 B Flash (LOG_OK_MSG = 3 B + `_firestarter_log_*` helpers ~100–200 B + macro expansion at deleted call-sites). SRAM unchanged (the Phase 8 `response_msg` win was the only SRAM lever).
  2. **v1.1 (98.7%) → Phase 9 close milestone comparison** — the LMIG-04 acceptance number. Phase 10's DOC-02 quotes this row verbatim into `MILESTONES.md`.
- **D-09:** Extend the anchor table that already exists in `08-MEASUREMENT.md` (lines 308–319). Phase 9 close becomes the new bottom row; Phase 8 close becomes the prior reference. The anchor table format already includes the 5 columns Phase 10 will need (Snapshot, Leonardo Flash, Uno Flash, SRAM, Notes).
- **D-10:** Bench verification ordering follows project memory `[[feedback_always-mirror-uno-leonardo-tests]]`: every Uno hardware test gets a paired Leonardo run as the control. The chipless wire-protocol bench session from `08-MEASUREMENT.md` (lines 322–384) is **already** the LFW-05 + W-04 regression matrix; Phase 9 re-runs it post-3.0.0-bump to confirm the inlined `OK: FW: 3.0.0-dev:...` still parses on both boards. Project memory `[[project_leonardo-shield-socket-wonky]]` continues to apply if SC#2/SC#3 (Phase 8's pending chip-seated UAT) carries forward.

### Claude's Discretion

The operator did not lock the following — researcher and planner should propose concrete choices grounded in Phase 9's scope, surface them in RESEARCH.md / PLAN.md, and proceed without re-asking:

- **`MSG_OK_FW_VERSION` (0x03) catalog entry fate.** Decision (Claude): **KEEP** with `wire_format = "text"`. The host's WR-03 reject-id-frame guard at `serial_comm.py:398-410` uses this entry to refuse a malicious peer emitting `id=0x03` as a binary frame and bypassing the FW-version text-path check. Defense in depth — near-zero firmware cost (catalog generates a 1-byte `#define` constant that's never referenced from firmware after D-01; the format string lives only in host `messages.py`). Researcher confirms this is still load-bearing on the host side after D-01.
- **Host `FIRESTARTER_DEV_ALLOW_PRE_V12` env-var fate.** Decision (Claude): **KEEP**, update comment. The escape hatch at `serial_comm.py:755-762` exists for bench scripts that need to talk to pre-Phase-6 firmware. After Phase 9 ships `3.0.0-dev`, the same hatch lets developers point a new host at a historical firmware build for regression checks. The "until then [Phase 9 firmware bump], bench scripts use..." comment language updates to drop the "until then" framing; the mechanism stays. Out-and-out deletion would force operators to downgrade the host to test old firmware — undesirable.
- **`debug_setup` / `log_debug` SERIAL_DEBUG functions.** Decision (Claude): **DELETE both.** After `rurp_log` goes, the only caller of `log_debug` (`uno_rurp_shield.cpp:rurp_log` line 84 per Phase 8 comment) goes with it. `debug_setup()` is a SoftwareSerial-port init for the Uno SERIAL_DEBUG build with no remaining purpose. The `#ifdef SERIAL_DEBUG` branch in `logging.h` collapses to nothing. Researcher confirms no other `log_debug` / `debug_setup` callers exist.
- **`logging.h` file fate after deletion.** Decision (Claude, tentative): **DELETE the file outright** if nothing remains after the macro deletions. Every `#include "logging.h"` site (use `grep` to enumerate) either drops the include entirely or migrates to `logging_id.h`. Planner to verify and execute the include cleanup.
- **`logging.c` file fate after `LOG_OK_MSG` deletion.** Decision (Claude, tentative): **DELETE the file** — `LOG_OK_MSG` was the only symbol it defined post-Phase-8. The `platformio.ini` `src_filter` for `[env:native]` already excludes `src/logging.c`; production build picks it up automatically via the default build pattern and will not miss the removed source file.
- **Commit cadence.** Phase 9 has small surface (~6 files touched in firmware: `version.h`, `hardware_operations.cpp`, `dev_tools.cpp`, `logging.h`, `logging.c`, `rurp_serial_utils.cpp` + `uno_rurp_shield.cpp` + `rurp_shield.h` + `rurp_serial_utils.h`). Recommended waves: (W1) D-04 dev_tools `send_ack` → `LOG_OK_ID(MSG_OK_READY)` conversions (atomic; precondition for W2). (W2) D-01 LFW-05 inline + D-02 legacy infra deletion + D-06 version bump (atomic — the inline emit + deletion must land together to keep firmware compiling; the version bump rides along so the host guard regression test runs against the same artifact). (W3) host_stubs.cpp + native test fix-up (if needed). (W4) `09-MEASUREMENT.md` + bench rerun. Planner may differ; rationale above explains the dependency edges.
- **Phase 8 pending UAT (SC#2/SC#3) carry-over.** Phase 8 SC#2 (write end-to-end on a chip) and SC#3 (byte-identical readback) are still PENDING per `08-MEASUREMENT.md`. Recommended (Claude): bundle them into Phase 9's bench-verification step since Phase 9 already requires both boards on the operator's bench (D-10) and the version bump invalidates any prior chip-seated test. Planner should explicitly cite Phase 8 SC#2/SC#3 closure in Phase 9's verification artifact.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope + requirements (authoritative)
- [.planning/ROADMAP.md](.planning/ROADMAP.md) §"Phase 9: Delete Old Log Macros + Measure Flash Savings" — phase goal locked; Phase D of the locked migration.
- [.planning/REQUIREMENTS.md](.planning/REQUIREMENTS.md) §"Logging Firmware-side" (LFW-03, LFW-04) and §"Logging Migration" (LMIG-04) — the 3 acceptance criteria Phase 9 owns.
- [.planning/PROJECT.md](.planning/PROJECT.md) §"Phased migration" — locked phase ordering A→B→C→D→Close; Phase 9 is D.
- [.planning/STATE.md](.planning/STATE.md) §"v1.2 Decisions" — lockstep upgrade, no backwards compatibility, ID width = 1 byte, raw byte params.

### Phase 8 outputs to extend (the immediate predecessor)
- [.planning/phases/08-convert-state-machine-prefix-call-sites-ok-init-main-end/08-CONTEXT.md](.planning/phases/08-convert-state-machine-prefix-call-sites-ok-init-main-end/08-CONTEXT.md) — locked wire-format W-01..W-04, populate-site patterns R-01..R-03, P-01..P-04, B-01..B-04. Phase 9 inherits all of these; nothing is re-litigated.
- [.planning/phases/08-convert-state-machine-prefix-call-sites-ok-init-main-end/08-MEASUREMENT.md](.planning/phases/08-convert-state-machine-prefix-call-sites-ok-init-main-end/08-MEASUREMENT.md) §"Anchor for Plan 9" (lines 306–319) — the 5-snapshot anchor table Phase 9 extends. Also §"Phase 8 Close — Logging Housekeeping Pass" (lines 388 onward) — Task 1's deletion list documents what's already gone vs what remains for Phase 9.
- [.planning/phases/08-convert-state-machine-prefix-call-sites-ok-init-main-end/08-MEASUREMENT.md](.planning/phases/08-convert-state-machine-prefix-call-sites-ok-init-main-end/08-MEASUREMENT.md) §"Bench Verification — Chipless Wire-Protocol Validation" (lines 322–384) — the bench matrix Phase 9 re-runs post-3.0.0-bump to confirm LFW-05 inline emit + W-04 frame still parse on both boards.

### Phase 6 LFW-05 origin + host guard
- [.planning/phases/06-logging-infrastructure/06-CONTEXT.md](.planning/phases/06-logging-infrastructure/06-CONTEXT.md) — LFW-05 (FW-handshake text exemption) + LHOST-04 (host pre-v1.2 refuse guard) origin. Phase 9 ships the firmware version-bump side of LFW-05; the host guard side was wired in Phase 6 Plan 04.
- [firestarter_app/firestarter/serial_comm.py:735-783](firestarter_app/firestarter/serial_comm.py#L735-L783) — `_probe_port` FW-version check + `FIRESTARTER_DEV_ALLOW_PRE_V12` escape hatch. SC#3 regression test target.
- [firestarter_app/firestarter/serial_comm.py:398-410](firestarter_app/firestarter/serial_comm.py#L398-L410) — WR-03 reject-id-frame guard for `wire_format="text"` entries. Reason `MSG_OK_FW_VERSION` (0x03) stays in the catalog after D-01.
- [firestarter_app/tests/test_fwguard.py](firestarter_app/tests/test_fwguard.py) — existing 4 unit tests for the host-side fw-guard. Planner uses these as the SC#3 regression vehicle.

### Firmware deletion targets (Phase 9 surface)
- [firestarter/include/version.h:11](firestarter/include/version.h#L11) — `VERSION = "2.0.11-dev"` — bump target (D-06).
- [firestarter/src/hardware_operations.cpp:82-88](firestarter/src/hardware_operations.cpp#L82-L88) — `fw_get_version()` containing the `send_ack_const(FW_VERSION)` call to inline (D-01).
- [firestarter/src/dev_tools.cpp:108](firestarter/src/dev_tools.cpp#L108), [:154](firestarter/src/dev_tools.cpp#L154) — `send_ack("")` sites for conversion to `LOG_OK_ID(MSG_OK_READY)` (D-04).
- [firestarter/include/logging.h](firestarter/include/logging.h) — entire file; macros `send_ack`, `send_ack_const`, `debug_setup`, `log_debug` declarations + `LOG_OK_MSG extern` to delete (D-02, D-08 Claude's discretion).
- [firestarter/src/logging.c](firestarter/src/logging.c) — `LOG_OK_MSG[] PROGMEM = "OK"` to delete; file likely deleted entirely (D-08 Claude's discretion).
- [firestarter/src/boards/rurp_serial_utils.cpp:11-25](firestarter/src/boards/rurp_serial_utils.cpp#L11-L25) — `_firestarter_log_ram` + `_firestarter_log_progmem` to delete (D-02).
- [firestarter/src/boards/rurp_serial_utils.cpp:243-248](firestarter/src/boards/rurp_serial_utils.cpp#L243-L248) — `rurp_log` + `rurp_log_P` weak defaults to delete (D-02).
- [firestarter/src/boards/uno_rurp_shield.cpp:77-87](firestarter/src/boards/uno_rurp_shield.cpp#L77-L87) — Uno strong overrides of `rurp_log` + `rurp_log_P` to delete (D-02).
- [firestarter/include/rurp_shield.h:127-128](firestarter/include/rurp_shield.h#L127-L128) — `rurp_log` + `rurp_log_P` declarations to delete (D-02).
- [firestarter/include/rurp_serial_utils.h:14-17](firestarter/include/rurp_serial_utils.h#L14-L17) — `_firestarter_log_ram` + `_firestarter_log_progmem` declarations to delete (D-02).

### Catalog (Phase 9 leaves the catalog mostly untouched)
- [tools/catalog/messages.toml](tools/catalog/messages.toml):49-60 — `MSG_OK_FW_VERSION` (0x03) `wire_format = "text"` — KEEP per Claude's Discretion (WR-03 guard).
- [tools/catalog/messages.toml](tools/catalog/messages.toml):33-47 — `MSG_OK_READY` (0x01) — the catalog entry reused for `dev_tools` conversions (D-04). Researcher verifies host-side consumers tolerate an additional emit context.

### Test surface impact
- [firestarter/test/native/avr/test_dispatch/host_stubs.cpp](firestarter/test/native/avr/test_dispatch/host_stubs.cpp) — references deleted `LOG_*_MSG` PROGMEM symbols (per `firestarter/CLAUDE.md` §"Native (Host) Test Environment"). Planner cleans up the stale symbol references so `pio test -e native` stays green (D-03).
- [firestarter/test/native/avr/test_messages/](firestarter/test/native/avr/test_messages/) — Phase 6/8 wire-frame Unity suite. Should remain green unchanged (Phase 9 does not touch wire format).
- [firestarter_app/tests/test_decoder.py](firestarter_app/tests/test_decoder.py) — host decoder regression. Unchanged by Phase 9 (no catalog ID changes that touch decode behavior).
- [firestarter_app/tests/test_fwguard.py](firestarter_app/tests/test_fwguard.py) — host fw-guard. The "expects v1.2+ firmware" message path is the SC#3 regression vehicle (D-07).

### Project memory (always-on guidance)
- `[[feedback_always-mirror-uno-leonardo-tests]]` — every Uno hardware test gets a paired Leonardo run as the control (D-10).
- `[[project_leonardo-shield-socket-wonky]]` — suspect bad chip contact first when Leonardo readbacks look corrupted but Uno is clean (relevant if SC#2/SC#3 carry over from Phase 8).
- `[[feedback_ic-removal-autonomy]]` — IC removal autonomy granted; bench cycles do not require per-cycle chip-removal confirmation.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`LOG_OK_ID(MSG_OK_READY)` macro** — already in `logging_id.h` (Phase 7); the macro family `LOG_OK_ID_*` was added in Phase 8 Plan 04. Zero new firmware infrastructure needed for D-04.
- **`F(...)` Arduino macro** — keeps the `"OK: FW: "` literal in PROGMEM without a named `extern const char[] PROGMEM` symbol. Idiomatic + already used elsewhere in `rurp_serial_utils.cpp` (e.g., `SERIAL_PORT.print(F(": "))` at line 17–18 before deletion).
- **Anchor table format in `08-MEASUREMENT.md`** — 5-column snapshot (Snapshot | Leonardo Flash | Uno Flash | SRAM | Notes) — directly reused as the `09-MEASUREMENT.md` structure (D-08, D-09).
- **`firestarter_app/tests/test_fwguard.py`** — 4 existing pytest cases that validate the host pre-v1.2 refusal path. Phase 9 SC#3 regression rides on this suite (no new test infrastructure).

### Established Patterns

- **Bootstrap exemption pattern** — Phase 6 LFW-05 + Phase 8 P-01 already locked "the FW-version handshake is the lone text-format survivor". Phase 9 inlines the emit but keeps the wire shape byte-identical. No new exemption class.
- **Weak/strong override pattern in `rurp_serial_utils.cpp` + `uno_rurp_shield.cpp`** — Phase 6 introduced this for `rurp_log_id`. After deletion of `rurp_log` / `rurp_log_P`, the pattern survives ONLY for `rurp_log_id` / `rurp_log_id_wide` — verify the override mechanism stays consistent for the ID-frame path.
- **PROGMEM exemption documentation** — Phase 8's catalog audit (08-MEASUREMENT.md §"Catalog Orphan Audit" + §"Phase 8 Close — Logging Housekeeping Pass") established the precedent of enumerating remaining PROGMEM hits with category labels (LOG_OK_MSG = log; json_parser keys = parser; MAGIC_PREAMBLE/CRC8_TABLE = frame infra). Phase 9's SC#1 verification artifact follows the same enumeration format.
- **`-dev` suffix convention** — `2.0.11-dev` shipped throughout v1.0/v1.1/v1.2 development; Phase 10 strips the suffix on release tag. Phase 9 ships `3.0.0-dev`.

### Integration Points

- **Host `_probe_port` text-prefix parse** — consumes the inlined `OK: FW: <version>` line byte-identically. No host code change required (D-01).
- **Host fw-guard** at `serial_comm.py:735-783` — already expects major ≥ 3 to pass. After Phase 9 bump, the guard flips from "always-warn pending firmware bump" to "actively load-bearing against pre-Phase-9 firmware" (D-06, D-07).
- **WR-03 reject-id-frame guard** at `serial_comm.py:398-410` — uses the `MSG_OK_FW_VERSION` catalog entry's `wire_format = "text"` to refuse `id=0x03` frames. Reason the catalog entry stays after firmware stops emitting it (Claude's Discretion).
- **PlatformIO `[env:native]` `src_filter`** — already excludes `src/logging.c`; deleting the file does not require build-system changes.

</code_context>

<specifics>
## Specific Ideas

- **"Maximum SC#1/SC#2 cleanliness"** — the user's explicit choice (D-01 over alternatives) of inlining the FW-version emit instead of preserving even a thin `send_ack_const` slice. The goal is to leave LFW-05 as a single 3-line bootstrap in `fw_get_version()` and nothing else legacy-shaped anywhere in firmware. SC#1's "enumerate remaining PROGMEM hits" verification artifact then lists only `MAGIC_PREAMBLE`, `CRC8_TABLE`, and the `json_parser.c` parser keys — every other PROGMEM string is gone.
- **MSG_OK_READY reused, not extended** — D-04 deliberately does NOT grow the catalog. The dev-tool wait-prompt semantic is implicit in the catalog entry's existing meaning ("ready/idle/done"); host-side verification confirms this is operationally OK before the conversion lands.
- **3.0.0-dev, not 3.0.0 yet** — Phase 10 owns the release-tag strip. Phase 9 ships a development-marker version so any pre-tag bench testing makes it obvious which firmware build is in flight.
- **Both deltas in one artifact** — `09-MEASUREMENT.md` is the milestone-comparison single source of truth; Phase 10 DOC-02 quotes it directly. The Phase 8 → Phase 9 incremental row preserves attribution chain (Phase 8 → "macro tower deletion"; the line missing in 08-MEASUREMENT.md's anchor table).

</specifics>

<deferred>
## Deferred Ideas

- **Strip `-dev` from VERSION → ship `3.0.0`** — Phase 10 release-tag operation (DOC-02). Phase 9 ships `3.0.0-dev` so bench builds during the phase-close UAT are unambiguous.
- **Phase 10 milestone-close documentation** — DOC-02 owns the v1.2 MILESTONES.md entry, the v1.1 baseline vs v1.2 final comparison, and the PROJECT.md/STATE.md roll-forward. Phase 9's `09-MEASUREMENT.md` is the input; Phase 10 is the publication.
- **v1.1 leftover items** (FM1608 hw bug, WARNING-4 test-script drift, v1.1 DOC-01 milestone close) — carried in STATE.md; resumed after v1.2 ships per the operator's current intent. No Phase 9 scope.
- **Future host-side cleanup of `FIRESTARTER_DEV_ALLOW_PRE_V12`** — once a future milestone drops support for pre-Phase-6 firmware entirely, the escape hatch can go. Not Phase 9 scope.
- **Catalog `MSG_OK_FW_VERSION` (0x03) entry deletion** — possible if a future milestone removes the WR-03 defense-in-depth guard. Phase 9 keeps the entry; future cleanup if the guard ever goes.
- **Phase 8 SC#2/SC#3 chip-seated UAT** — STILL pending per `08-MEASUREMENT.md`; Phase 9's bench step is recommended (Claude's Discretion) as the closure venue since both boards are on the operator's bench for D-10 anyway. Planner should explicitly cite this in the Phase 9 verification artifact.

</deferred>

---

*Phase: 09-delete-old-log-macros-measure-flash-savings*
*Context gathered: 2026-05-19*
