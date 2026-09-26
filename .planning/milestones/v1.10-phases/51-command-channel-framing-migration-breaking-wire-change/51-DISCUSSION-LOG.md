# Phase 51: Command-Channel Framing Migration (breaking wire change) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-02
**Phase:** 51-command-channel-framing-migration-breaking-wire-change
**Areas discussed:** Version/handshake guard, Legacy `{`-peek path fate, Probe framing, Garbled command-frame handling

---

## Version/handshake guard (SC3)

| Option | Description | Selected |
|--------|-------------|----------|
| Raise version floor | Reuse existing `CMD_FW_VERSION` probe + `_validate_firmware_version`; bump the required-firmware floor to the v1.10 framing version. Host refuses old fw at handshake. | |
| Explicit framing-capability negotiation | New handshake field/flag where firmware advertises "I speak COBS frames"; host enables framing only on positive ack. | |
| Version-bump + document only | Bump `FW_VERSION` + document the breaking cut; no runtime refusal. | |

**User's choice:** Free text — "don't care about backwards compatibility, this protocol is the only supported."
**Notes:** This steer overrides the menu: no interop machinery, no capability negotiation, no dual-protocol/fallback. The framed protocol is THE protocol; backwards compatibility is an explicit non-goal. A mismatched old↔new pair is unsupported and simply fails — acceptable. Documentation of the breaking cut becomes the SC3 "guard equivalent". Recorded as D-01/D-02; optional host version-floor bump demoted to Claude's discretion (D-03).

---

## Probe framing (chicken-and-egg)

(Resolved by the guard answer above — not asked as a separate question.)

**Resolution:** The `CMD_FW_VERSION` version probe is framed like every other host→fw command (D-04). No unframed plaintext escape hatch. No chicken-and-egg problem because there is no old peer to detect or speak to (consequence of D-01). The fw→host version *response* stays text (out of scope).

---

## Legacy `{`-peek path fate (SC2)

| Option | Description | Selected |
|--------|-------------|----------|
| Delete outright | Remove the `{`-peek loop entirely; firmware command ingest accepts ONLY COBS frames (decode → CRC8 → `parse_json`). | ✓ |
| Keep `{`-peek as dev fallback | Firmware tries frame decode but still accepts a raw leading `{` as an explicit, documented debug path (no CRC8). | |

**User's choice:** Delete outright.
**Notes:** Cleanest, matches the only-supported-protocol stance, smallest attack/maintenance surface, avoids reintroducing a CRC-less ingest path that conflicts with the CRC8-before-parse mandate. Recorded as D-05.

---

## Garbled / incomplete command-frame handling

| Option | Description | Selected |
|--------|-------------|----------|
| Mirror Phase 50 + size cap | On COBS/CRC8 failure drain to next `0x00` + existing error (fail-fast); bound partial frames with a max-frame-size cap; no new idle timer; non-blocking accumulation. | ✓ |
| Dedicated ingest receive-timeout | Start a receive timer on the first frame byte; if no `0x00` within N ms, drain + error. | |

**User's choice:** Mirror Phase 50 + size cap.
**Notes:** Reuses the Phase-50 D-01 fail-fast + resync-to-next-`0x00` posture and the existing firmware error surface; the size cap bounds the never-completing-frame case without adding new timer state to the idle loop. Recorded as D-06.

---

## Claude's Discretion

- Firmware command-frame receive-buffer strategy / where decoded JSON lands (Uno-RAM constraint respected).
- Concrete value/name of the max-frame-size cap (`CMD_FRAME_MAX`).
- Whether to bump the host version-floor constant (incidental UX, D-03).
- Reuse vs thin-wrapper for the shared Phase-50 COBS+CRC8 helpers.
- New firmware/host encode/decode symbol names.

## Deferred Ideas

- Capability negotiation / dual-protocol support / runtime interop guard — explicit **non-goal** (not a future phase).
- Framing the fw→host command-response direction — out of scope per ADR §4.2 (Framing 4 unchanged).
- Block-level retransmit / ACK on the command channel — D-06 chose fail-fast; its own phase if ever wanted.
- Full byte-compat round-trip / lockstep contract tests (pathological all-delimiter command payloads) → Phase 52.
- Bench verification (Uno/Leonardo/uno328pb, operator-gated) → Phase 53.
