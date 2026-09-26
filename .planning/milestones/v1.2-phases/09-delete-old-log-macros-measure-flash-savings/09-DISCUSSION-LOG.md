# Phase 9: Delete Old Log Macros + Measure Flash Savings - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-19
**Phase:** 09-delete-old-log-macros-measure-flash-savings
**Areas discussed:** LFW-05 bootstrap path, dev_tools send_ack("") sites, Version bump shape, Flash measurement scope

---

## Gray Area Selection

| Option | Description | Selected |
|--------|-------------|----------|
| LFW-05 bootstrap path | How to handle the FW-version text emit; inline vs preserve send_ack_const | ✓ |
| dev_tools send_ack("") sites | Two dev-tool wait-prompt callers; inline / new ID / reuse MSG_OK_READY | ✓ |
| Version bump shape | 2.0.11-dev → 3.0.0 / 3.0.0-dev / 3.0.0-rc1 | ✓ |
| Flash measurement scope | Phase 8→9 incremental / v1.1→v1.2 milestone / both | ✓ |

**User's choice:** All four areas selected for discussion (multiSelect).
**Notes:** No areas deferred to Claude's full discretion upfront. Wrap-up sub-decisions (catalog entry fate, env-var fate, debug_setup/log_debug fate, file deletion, commit cadence) were captured under "Claude's Discretion" in CONTEXT.md per the user's "work without stopping" directive.

---

## LFW-05 bootstrap path

| Option | Description | Selected |
|--------|-------------|----------|
| Inline a 2-line Serial.print | Replace `send_ack_const(FW_VERSION)` with inline `SERIAL_PORT.print(F("OK: FW: ")); SERIAL_PORT.println(FW_VERSION); SERIAL_PORT.flush();`. Lets all of `send_ack`, `send_ack_const`, `rurp_log`, `rurp_log_P`, `_firestarter_log_ram`, `_firestarter_log_progmem`, `LOG_OK_MSG` be deleted. Max SC#1/SC#2 cleanliness. | ✓ |
| Keep send_ack_const only | Delete `send_ack` + `rurp_log` + `_firestarter_log_ram`. Retain `send_ack_const` + `rurp_log_P` + `_firestarter_log_progmem` + `LOG_OK_MSG` for the LFW-05 site only. Thin legacy slice survives. | |
| Keep both send_ack flavors | Delete only unreferenced helpers; keep both ack macros + LOG_OK_MSG. Smaller diff; LOG_OK_MSG needs documented SC#1 exemption. Goes against LFW-03/04 spirit. | |

**User's choice:** Inline a 2-line Serial.print (Option A).
**Notes:** Maximum cleanup chosen. The trade-off accepted: one hand-coded `F("OK: FW: ")` literal survives in `fw_get_version()` but is exempt from SC#1's "log-only PROGMEM" criterion because it's inline-bound to the bootstrap function (same exemption class as `MAGIC_PREAMBLE` / `CRC8_TABLE`). Host-side `_probe_port` text-prefix parse continues to consume the byte-identical line.

---

## dev_tools.cpp send_ack("") sites

| Option | Description | Selected |
|--------|-------------|----------|
| Inline Serial.println(F("OK:")) | One-liner replacement at each site; preserves byte-identical wire output; no catalog change. | |
| New catalog ID MSG_OK_DEV_PROMPT | Add a 0-param OK-band entry (e.g. 0x07); emit via LOG_OK_ID. Catalog grows by 1; semantically clean. | |
| Reuse MSG_OK_READY | Use existing 0x01 entry. Same wire frame, no catalog growth; minor semantic stretch (dev-tool wait vs hardware-ready). | ✓ |

**User's choice:** Reuse MSG_OK_READY (Option C).
**Notes:** Semantic stretch accepted as minor — both contexts ("hardware ready" startup ack and "dev tool finished setup, waiting on user button") share the same operational meaning of "I'm idle; host may proceed". CONTEXT.md D-04 directs researcher to verify the host-side `MSG_OK_READY` consumer does not assume single emit-site; if it does, planner adds a sub_id discriminator or a dedicated catalog entry then.

---

## Version bump shape

| Option | Description | Selected |
|--------|-------------|----------|
| 3.0.0-dev | Matches existing `-dev` suffix convention. Phase 10 strips `-dev` on release tag. | ✓ |
| 3.0.0 | Clean major bump with no suffix. Implies Phase 9 = release; Phase 10 = doc-only. | |
| 3.0.0-rc1 | Release-candidate marker. Phase 10 strips `-rc1` on tag. Conveys "feature complete, not yet released". | |

**User's choice:** 3.0.0-dev.
**Notes:** Matches the prior `2.0.11-dev` development-line convention. Major bump satisfies host's `major < 3` refusal guard at `serial_comm.py:761` — SC#3 PASS without any host code change. Phase 10 owns the `-dev` strip on release tag (DOC-02).

---

## Flash measurement scope

| Option | Description | Selected |
|--------|-------------|----------|
| Both, in 09-MEASUREMENT.md | Single artifact captures Phase 8→9 incremental delta + v1.1→Phase 9 milestone comparison. Extends the anchor table from 08-MEASUREMENT.md. Phase 10 DOC-02 quotes it verbatim. | ✓ |
| Incremental only | Just Phase 8→9 delta; defer milestone comparison to Phase 10. Cleaner separation but Phase 10 recomputes. | |
| Milestone comparison only | Skip the (tiny) Phase 8→9 increment. Smallest artifact. Loses the attribution chain. | |

**User's choice:** Both, in 09-MEASUREMENT.md.
**Notes:** Single source of truth chosen. CONTEXT.md D-08/D-09 captures the structure (extend the existing 5-column anchor table). D-10 captures the bench-rerun requirement post-3.0.0-bump per project memory `[[feedback_always-mirror-uno-leonardo-tests]]`.

---

## Claude's Discretion

The following were not explicitly asked of the user; Claude made the calls and documented them in CONTEXT.md `<decisions>` §"Claude's Discretion" for downstream agent review:

- **MSG_OK_FW_VERSION (0x03) catalog entry fate:** KEEP with `wire_format="text"`. Rationale: host's WR-03 reject-id-frame guard depends on the entry. Defense in depth; near-zero firmware cost.
- **Host `FIRESTARTER_DEV_ALLOW_PRE_V12` env-var:** KEEP, update comment. Useful escape hatch for regression-testing the host against historical firmware builds. The "until then" comment language goes; the mechanism stays.
- **`debug_setup` / `log_debug` SERIAL_DEBUG functions:** DELETE both. Their only remaining caller (`rurp_log()` line 84 in `uno_rurp_shield.cpp` per Phase 8 comment) goes with the Phase 9 deletion.
- **`logging.h` file fate:** DELETE the file outright if no symbols remain after macro deletions. Planner verifies and cleans up `#include "logging.h"` sites.
- **`logging.c` file fate:** DELETE the file. `LOG_OK_MSG` was the only symbol post-Phase-8.
- **Commit cadence:** Recommended waves W1 (dev_tools conversions), W2 (LFW-05 inline + legacy infra deletion + version bump as atomic), W3 (host_stubs / native-test cleanup), W4 (`09-MEASUREMENT.md` + bench rerun). Planner may differ.
- **Phase 8 SC#2/SC#3 chip-seated UAT carry-over:** Recommended bundling into Phase 9 bench step since both boards are on the operator's bench for D-10 anyway.

## Deferred Ideas

See CONTEXT.md `<deferred>` for the full list. Highlights:
- Strip `-dev` to `3.0.0` on release tag → Phase 10 (DOC-02)
- Phase 10 milestone-close documentation (MILESTONES.md entry + PROJECT.md/STATE.md roll-forward)
- v1.1 leftovers (FM1608, WARNING-4, DOC-01) — carried in STATE.md
- Future cleanup of `FIRESTARTER_DEV_ALLOW_PRE_V12` once support drops for pre-Phase-6 firmware
- Catalog `MSG_OK_FW_VERSION` (0x03) entry deletion if the WR-03 host guard ever goes
- Phase 8 SC#2/SC#3 hardware UAT (pending chip-seated verification)
