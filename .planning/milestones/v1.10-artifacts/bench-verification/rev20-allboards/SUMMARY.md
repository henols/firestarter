# Rev 2.0 all-boards transport test — 2026-06-03

All three boards exercised on the SAME Rev 2.0 shield + the SAME (blank) W27C512, on the hardened
v1.10 transport with all fixes (blank com_mode, write/verify -2, systemic buffer-and-flush,
per-board buffer negotiation). vpp/vpe confirmed safe (no socket routing).

| Board | fw | id | blank | N=5 read | verify | buffer (adv->chunk) |
|-------|----|----|-------|----------|--------|---------------------|
| Uno (ATmega328P) /dev/ttyACM* | bafbe8a* | PASS | SUCCESS 5.34s | PASS (1 SHA) | PASS 13.95s | 512 -> 510 |
| Leonardo (ATmega32u4) | 8731017 | VPP-gated** | SUCCESS 4.73s | PASS (1 SHA) | PASS 5.61s | **1024 -> 1022** |
| uno328pb (ATmega328PB) /dev/ttyUSB0 | 8731017 | PASS x3 | SUCCESS 5.42s | PASS (1 SHA) | PASS (after 1 retry) | 512 -> 510 |

\* Uno tested before the FW-identity commit; fw bafbe8a (no advertise) -> host falls back to 510 (correct for 512 buffer). Re-flash to 8731017 would have it advertise :512 (same 510 result).
\** Leonardo id safety-gated by VPP=13.1V>12.0V (calibration: VCC reads 5.5V; same R1/R2 as Uno's 12.1V). -f downgrades to warning; transport unaffected.

## Verdict
The hardened COBS transport + all fixes work on ALL THREE boards. Per-board buffer negotiation
validated end-to-end (Leonardo 1022-byte chunks, 64x1030B frames; Uno/uno328pb 510). The uno328pb
read clean here (no timeouts/drift) BUT on a BLANK chip + Rev 2.0 — NOT a replication of its
historical data-chip instability and NOT a substitute for XACT-03.

## Caveat (applies to all three)
N=5 byte-identity is on a BLANK chip (all 0xff) -> consistency proof, not a varied-data stress of
the transport. A strong byte-identity / write-path proof needs a programmed chip with varied data
(write a known pattern to a blank chip -> read-back/verify); deferred (W27C512 erase "Not supported"
blocks rewriting a non-blank chip; a fresh blank chip + write would work and drives VPP-by-design).
