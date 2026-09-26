---
phase: 91-12v-vpp-write-path-regression-rca
plan: 03
subsystem: firmware-rca
tags: [fix, sst39sf040, erase, write-b-footgun, fix-91, silicon-confirmed, safe-04]
requires:
  - phase: 91-02
    provides: RCA-91 attribution (recompose innocent) + the bench A/B substrate
provides:
  - TRUE root cause: `write -b` sets FLAG_SKIP_ERASE -> flash3 (NOR) never erases -> bits can't be set
  - FIX-91 confirmed: SST39SF040 write+verify == a38b13b4 (3/3 consistency-check) via plain `write`
  - firmware reverted to byte-identical recompose a296195 (no code edit needed)
  - SAFE-04 re-verified intact (vpp_check_window +500mV present + unmodified)
affects: [phase-91-wave4-disposition, sst39sf040, w27c512, host-b-flag-hardening-recommendation]
key-files:
  created:
    - .planning/v1.16/ledger/bench/SST39SF040-fix/SHA256SUMS.txt
  modified:
    - .planning/v1.16/ledger/rca/91-RCA.md
key-decisions:
  - "TRUE root cause: `firestarter write -b` => build_flags(skip_erase=not blank_check) => FLAG_SKIP_ERASE; flash3_write_init skips the erase that SST39SF040 (NOR) REQUIRES. The chip looked 99.99% correct only because it already held imgB; the 3 stuck bytes @0x0-0x2 needed bits set (erase). DQ7-only poll masked it -> false 'write successful'."
  - "Intermediate erase-TIMING hypothesis (105->500ms) DISPROVEN on silicon (write B still failed @0x0); the erase block is never entered on -b. Firmware change REVERTED -> recompose byte-identical/innocent."
  - "FIX = erase-enabled plain `firestarter write` (NOT `write -b`). Confirmed: writeA->verifyA->writeB->verifyB->consistency-check N=3 all PASS == a38b13b4 (1 distinct SHA); neg-control verify(imgA) RC=1. No firmware/host code change."
  - "Phase-90 '12V-VPP write-path regression' was a TEST-METHOD error: `write -b` used for NOR/erase-required chips silently skipped the required erase. Both b10 and recompose fail identically with -b -> no v1.16 regression."
  - "Recommended future hardening (NOT applied; touches D-13.3-locked -b semantics): WARN when -b/FLAG_SKIP_ERASE is used on a FLAG_CAN_ERASE chip. Left for operator decision."
  - "post-reflash Leonardo re-enumerates (ACM0<->ACM1); a 10s sleep + `firestarter fw` poll loop avoids the first-op 'Operation timed out' glitch."
requirements-completed: [FIX-91 (SST39SF040 / 0x06)]
duration: ~40min (multiple ~4-16min bench cycles)
completed: 2026-06-26
---

# Phase 91 Plan 03: Fix + SST39SF040 Working-Write Confirmation — Summary

**FIX-91 met: SST39SF040 writes byte-identical to the v1.15 baseline a38b13b4 (3/3
consistency-check) on STOCK recompose firmware. The true root cause is that `write -b` sets
FLAG_SKIP_ERASE, so flash3 (NOR, erase-required) never erases — the fix is the erase-enabled
plain `write` path. No firmware/host code change; the recompose is fully innocent.**

## The investigation (and a corrected hypothesis)
1. Reproduced the failure (write B "successful" but verify `0x1c != 0x04 @0x0`) on recompose AND
   b10 — identical → recompose innocent (Wave 2).
2. Intermediate hypothesis: marginal 105 ms chip-erase timing → applied 105→500 ms. **Silicon
   disproved it** (still failed @0x0): the erase block is never entered on `-b`.
3. Traced the host: `write -b` → `build_flags(skip_erase=not blank_check)` → `FLAG_SKIP_ERASE`;
   flash3_write_init skips erase. SST39SF040 is NOR — programming can't set 0→1 without erase →
   the 3 stuck bytes (which `== imgA & imgB`); the bulk looked fine only because the chip already
   held imgB. DQ7-only poll masked it.
4. **Reverted** the firmware change (byte-identical to a296195) and confirmed the fix with the
   erase-enabled plain `write`.

## FIX-91 confirmation (stock recompose, Leonardo + Rev 2.0)
- writeA RC=0 / verifyA RC=0 (erase proof) → writeB RC=0 / verifyB RC=0 → consistency-check N=3
  **PASS, 1 distinct SHA = a38b13b4…970b96b** == v1.15 gate; neg-control verify(imgA) RC=1.
- Evidence: `bench/SST39SF040-fix/SHA256SUMS.txt`.

## Verification
- `grep a38b13b4… bench/SST39SF040-fix/SHA256SUMS.txt` ✓ ; 91-RCA.md has Working-Write
  Confirmation + Fix Applied + Board Restore + SAFE-04 ✓
- `git -C firestarter status --porcelain src include` empty (firmware byte-identical; SAFE-04
  vpp_check_window +500mV intact) ✓ ; board left on milestone fw a296195 ✓
- /tmp/fs-b10 + /tmp/fsa-b8 worktrees removed; meta gitlinks NOT bumped (D-06) ✓

## Deviations
- The applied "fix" is a usage/method correction (plain `write` vs `write -b`) + documentation, not
  a code change — because the tool already supports the correct erase-enabled path and the recompose
  is innocent. A code hardening (warn-on-skip-erase-for-erasable-flash) is RECOMMENDED but not
  applied (D-13.3 `-b` semantics are rationale-locked; left for operator).
- Bench Tool 2-min foreground limit + post-reflash port shuffle handled via background runs +
  port-ready poll.

## Self-Check: PASSED — FIX-91 (0x06) met
SST39SF040 is bench-confirmed working (write+verify byte-identical to v1.15) on stock milestone
firmware, no safety guard weakened. Ledger disposition + W27C512 deferral → Plan 04.
