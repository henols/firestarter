---
created: 2026-08-31T00:00:00Z
title: Record which pin JP4's third position routes VPP to (Rev 2.2 / Rev 2.3)
area: hardware-docs
files:
  - firestarter_prom wiki Shield-Revisions (Notes column, Rev 2.2 and Rev 2.3 rows)
  - firestarter_app/firestarter/data/pinouts.json (DIP24_2716, DIP24_2532)
---

The wiki's Shield Revisions page states that JP4's third position reroutes VPP and
that this is what reaches the TI 2516 and 2532, but does not say **which pin** VPP
lands on. Operator will supply the value.

An earlier draft claimed the TI parts take VPP "on a different pin than the JEDEC
parts". That was removed on 2026-08-31 because it is false for the 2516: it uses the
`DIP24_2716` pinout with VPP on pin 21, exactly as the JEDEC 2716 does.

The pinout data does not explain why a reroute is needed, so the answer is in the
schematic or on the board, not in the repository. Unverified inference worth checking
when this is settled: the 2532 is the part that actually needs it — pin 21 is VPP on
`DIP24_2532` but A11 on the JEDEC `DIP24_2732`, and pin 18 flips the other way
(A11 vs /CE). A fixed JEDEC-wired socket would therefore need pin 21 switched from an
address line to VPP for a 2532, with the 2516 following because it shares protocol
`0x0B`.
