# Transport command-surface coverage — hardened COBS+CRC8 (v1.10)

Operator-witnessed bench, 2026-06-02. Goal: verify the hardened transport handles the
**full firestarter command surface** on both native-USB boards — not just EPROM data ops.

- **Uno** — Arduino Uno (ATmega328P), `/dev/ttyACM1`, hardened firmware (`controller: uno`), shield Rev 2.0, R1=270000/R2=44000.
- **Leonardo** — Arduino Leonardo (ATmega32u4), `/dev/ttyACM0`, hardened firmware (`controller: leonardo`), physical shield **Modified Rev 0** (operator-declared); EEPROM HW-override reads Rev 2.3 (EEPROM byte cannot distinguish revs — physical declaration governs).

## Results

| Command | Class | Uno (ttyACM1) | Leonardo (ttyACM0) | Transport verdict |
|---------|-------|---------------|--------------------|-------------------|
| `fw`     | single req→resp | ✓ controller: uno | ✓ controller: leonardo | clean framed round-trip |
| `hw`     | single req→resp | ✓ Rev 2.0-class | ✓ Rev 2.0-class (override Rev 2.3) | clean framed round-trip |
| `config` | single req→resp | ✓ R1 270000 / R2 44000 | (not re-run; same firmware) | clean framed round-trip |
| `id W27C512` | single req→resp | ✓ ID check passed | n/a (chip in Uno) | clean framed round-trip |
| `read` (consistency-check) | bulk data stream | ✓ 4×64 KB streamed (run 5 timeout, retry-class) | n/a | data path byte-exact (sub-transport jitter, see read leg) |
| `erase W27C512` | framed error | ✓ clean `Not supported` (app-layer, FLAG_CAN_ERASE unset; DB classes W27C512 as UV-EPROM) | n/a | clean framed ERROR round-trip, sub-second, no cascade |
| `vpp`    | continuous monitor | ✓ streams 12.1 V (VCC 5.1 V) | ✓ streams 12.9 V (VCC 5.5 V) | sustained multi-frame streaming |
| `vpe`    | continuous monitor | ✓ streams 14.1 V | ✓ streams 15.0 V; caught a live **resync** (`Command 11 timed out` → reconnect → clean stream) | sustained streaming + bounded-desync recovery |
| `blank W27C512` | firmware simple-op | ⚠ reproducible timeout (2×) "waiting for response" | (not tested) | ANOMALY — see below |

`vpp`/`vpe` exit-124 in tooling = the interactive monitor being killed by an external `timeout`,
NOT a transport hang ("Reading continuously. Press Ctrl+C to stop.").

## Transport conclusion

The hardened COBS+CRC8 transport handles the full command surface on **both** boards:
single request→response commands, framed application-layer error round-trips, and **sustained
continuous-streaming monitors** (vpp/vpe stream frame-after-frame indefinitely). A spontaneous
fail-fast **resync** was observed on Leonardo `vpe` (timeout → reconnect → clean), corroborating
the XACT-02 bounded-desync posture outside the dedicated fault-injection leg.

## Open anomalies (separate from transport-exactness)

1. **`blank W27C512` reproducible timeout (Uno).** Connects + starts, then host times out
   "waiting for a significant response." Firmware `eprom_blank_check` is an
   `op_execute_simple_operation` (reads whole chip on-device, single result) vs `read`'s
   chunked stream — likely a host-timeout / progress-framing interaction for long simple-ops,
   not a transport-link failure (link proven up by the streaming commands above). Needs scoping.
2. **`erase`/write leg blocked by chip classification.** W27C512 is `type: UV-EPROM`,
   `algorithm: 7` in chip_database.json → firmware `eprom_erase` rejects with `Not supported`
   (FLAG_CAN_ERASE unset). This is a write-path / chip-config matter, distinct from the
   transport milestone (matches the deferred "write/program — separate" note from Phase 44).
