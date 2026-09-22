---
phase: 205-the-pre-flights-leave-the-firmware
verified: 2026-09-22T20:00:00Z
status: gaps_found
score: 8/9 must-haves verified (1 blocked by CR-01)
covered_files:
  - .planning/phases/205-the-pre-flights-leave-the-firmware/205-01-PLAN.md
  - .planning/phases/205-the-pre-flights-leave-the-firmware/205-01-SUMMARY.md
  - .planning/phases/205-the-pre-flights-leave-the-firmware/205-02-PLAN.md
  - .planning/phases/205-the-pre-flights-leave-the-firmware/205-02-SUMMARY.md
  - .planning/phases/205-the-pre-flights-leave-the-firmware/205-03-PLAN.md
  - .planning/phases/205-the-pre-flights-leave-the-firmware/205-03-SUMMARY.md
  - .planning/phases/205-the-pre-flights-leave-the-firmware/205-04-PLAN.md
  - .planning/phases/205-the-pre-flights-leave-the-firmware/205-04-SUMMARY.md
  - .planning/phases/205-the-pre-flights-leave-the-firmware/205-05-PLAN.md
  - .planning/phases/205-the-pre-flights-leave-the-firmware/205-05-SUMMARY.md
  - .planning/phases/205-the-pre-flights-leave-the-firmware/205-06-PLAN.md
  - .planning/phases/205-the-pre-flights-leave-the-firmware/205-06-SUMMARY.md
  - .planning/phases/205-the-pre-flights-leave-the-firmware/205-07-PLAN.md
  - .planning/phases/205-the-pre-flights-leave-the-firmware/205-07-SUMMARY.md
  - .planning/phases/205-the-pre-flights-leave-the-firmware/205-BENCH-MATRIX.md
  - .planning/phases/205-the-pre-flights-leave-the-firmware/205-CONTEXT.md
  - .planning/phases/205-the-pre-flights-leave-the-firmware/205-FLASH-RAM.md
  - .planning/phases/205-the-pre-flights-leave-the-firmware/205-REVIEW.md
  - .planning/phases/205-the-pre-flights-leave-the-firmware/205-SESSION-COST.md
  - .planning/phases/205-the-pre-flights-leave-the-firmware/deferred-items.md
  - firestarter_app/firestarter/chip_test.py
  - firestarter_app/firestarter/cli_handlers.py
  - firestarter_app/firestarter/constants.py
  - firestarter_app/firestarter/eprom_operations.py
  - firestarter_app/firestarter/serial_comm.py
  - firestarter_app/firestarter/write_blank_guard.py
  - firestarter_fw/include/firestarter.h
  - firestarter_fw/include/memory_utils.h
  - firestarter_fw/src/firestarter.cpp
  - firestarter_fw/src/json_parser.c
  - firestarter_fw/src/proms/eeprom_28c.cpp
  - firestarter_fw/src/proms/eprom.cpp
  - firestarter_fw/src/proms/flash_5v_page.cpp
  - firestarter_fw/src/proms/flash_intel.cpp
  - firestarter_fw/src/proms/flash_nor_unlock.cpp
  - firestarter_fw/src/proms/memory.cpp
  - tools/catalog/messages.toml
covered_digest: "v1:sha256:de8243fcf133189569cd822e8a6dd4da85a937b2d626312ad7a803d0e7c1987d"
gaps:
  - truth: "The host-side write guard fully owns the safety property the removed firmware write-init blank check used to provide, for every protocol family the guard claims to cover."
    status: failed
    reason: >
      CR-01 (205-REVIEW.md, independently confirmed by the orchestrator and re-confirmed in this
      verification): `write_blank_guard.is_erase_exempt` is a pure flag test
      (`FLAG_CAN_ERASE && !FLAG_SKIP_ERASE`), address-blind. For protocol 0x06
      (`flash_nor_unlock.cpp`, AMD/JEDEC NOR-unlock family, 190 shipped chips, all
      `FLAG_CAN_ERASE`-eligible via `database.py`'s `electrical.type == "Flash/EEPROM"` rule),
      `flash_nor_unlock_erase_execute` performs a whole-chip erase only when `handle->address == 0`;
      any non-zero address (i.e. any `write -a <addr>`) performs a SECTOR erase instead
      (`flash_nor_unlock.cpp:111-119`). `is_erase_exempt` cannot tell the two cases apart, so
      `requires_blank_check` returns `False` and `write_eprom` skips its own host-side blank-check
      read entirely (`eprom_operations.py:2385-2401`) — for a write whose target region may not be
      inside the sector that was actually erased.

      Confirmed as a regression this phase introduces, not a pre-existing, already-priced-in
      defect: `git show 1cf1b22 -- firestarter_fw/src/proms/flash_nor_unlock.cpp` shows plan 205-03
      deleted an unconditional `mem_util_blank_check(handle)` call (the WHOLE-DEVICE wrapper, `(0,
      mem_size)`) from `flash_nor_unlock_write_init`, which ran unconditionally after the
      address-dependent erase on every pre-205 write. That whole-device scan — which necessarily
      covers whatever sub-region the sector erase missed — was the backstop that made the host
      guard's address-blind exemption safe in practice before this phase. Phase 205 removes that
      backstop and nothing on the host replaces it for this specific case.

      The phase's own code recognises the identical hazard shape elsewhere and declines to leave it
      open: `cli_handlers.py`'s `_erase_sector_blank_refusal_exit_code` (built in plan 205-01) refuses
      `erase -s <addr> -b` for exactly this "sector erase, not whole-device" reason. That refusal
      protects only the standalone `erase` command. `write`'s pre-write guard reaches the identical
      firmware branch through the identical field (`handle->address`, from `write`'s `-a`) with no
      equivalent refusal or region-awareness — `write_blank_guard.py`'s own docstring calls itself
      "the whole safety net" now that the firmware pre-flight is gone, and for this combination it
      is not one.

      This directly contradicts the phase's and milestone's own stated safety property (CONTEXT.md:
      "the roadmap's ordering rule requires the host to gain the capability before the firmware
      loses it") for one of the five protocol families (`0x06`) WRITE-02 names as guarded, and it
      is a live, silent data-integrity hazard on 190 shipped chips reachable through the ordinary
      `-a` option — not a coverage gap the phase already stated and accepted (D-06's stated 0x06
      gap is about bench coverage of the removed write-init call, proven safe by native test; it does
      not anticipate or cover this host-side exemption gap).
    artifacts:
      - path: firestarter_app/firestarter/write_blank_guard.py
        issue: "is_erase_exempt (line ~156) takes no address parameter and cannot distinguish a whole-chip erase from a protocol-0x06 sector erase; requires_blank_check therefore returns False (no check at all) for a non-zero-address write on any FLAG_CAN_ERASE protocol-0x06 chip."
      - path: firestarter_app/firestarter/eprom_operations.py
        issue: "write_eprom's guard-skip branch (2385-2401) reads is_erase_exempt without threading the write's resolved start address, so the exemption is applied without regard to whether the erase that ran actually covered the target region."
      - path: firestarter_app/tests/test_write_blank_guard.py
        issue: "WR-02 (205-REVIEW.md): the only three direct tests of is_erase_exempt never pass an algorithm/protocol id or a non-zero address, so this gap has zero regression coverage and would ship silently even after a fix."
    missing:
      - "Address-aware (or protocol-0x06-aware) logic in is_erase_exempt or its caller, mirroring cli_handlers.py's own sector/whole-device distinction, so a non-zero-address write on a FLAG_CAN_ERASE protocol-0x06 chip is not silently exempted from the host's blank-check read."
      - "A test pinning that is_erase_exempt (or requires_blank_check) returns False for algorithm=0x06 with a non-zero write address even when FLAG_CAN_ERASE is set and FLAG_SKIP_ERASE is clear, alongside a companion case confirming the exemption still holds at address 0 and for algorithm=0x10 regardless of address."
      - "A decision on whether the fix lands in this phase (205) before FWBLANK-01 is considered complete in substance, or is explicitly deferred with the accepted-risk window stated in the phase record the way D-04's write -b skew was — this phase's own precedent for handling a known regression is to state it, not to silently carry it."
human_verification: []
---

# Phase 205: The pre-flights leave the firmware — Verification Report

**Phase Goal:** The write-init and erase-end blank checks, their shared machinery and the
`FLAG_SKIP_BLANK_CHECK` bit leave the firmware, and the flash that frees is a measured number
rather than an estimate.
**Verified:** 2026-09-22
**Status:** gaps_found
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|---|---|---|
| 1 | No caller of `mem_util_blank_check` or `mem_util_blank_check_region` remains, and both functions plus `blank_check_saved_address` and `BLANK_CHECK_CHUNK_SIZE` are deleted (SC1 / FWBLANK-03). | ✓ VERIFIED | `git grep -n "mem_util_blank_check\b\|mem_util_blank_check_region\|blank_check_saved_address\|BLANK_CHECK_CHUNK_SIZE" -- 'src/*' 'include/*' 'test/*'` in `firestarter_fw` returns zero hits. `memory.cpp` diff (`git show 1cf1b22`) removes the block; `uint32_to_bytes` (orphaned by the sweep) removed with it. Firmware CI (orchestrator-measured): `pio run` 3/3, `pio test -e native`/`-e native_nodevtools` 244/244, `pytest tests/` 316/316. |
| 2 | `FLAG_SKIP_BLANK_CHECK` is gone from `firestarter.h` and `constants.py`, with `0x08` recorded as reserved on both sides (SC2 / FWBLANK-04). | ✓ VERIFIED | `git grep "FLAG_SKIP_BLANK_CHECK" -- 'src/*' 'include/*'` in `firestarter_fw` returns zero hits (the macro definition is gone). `firestarter.h:47-55` and `constants.py:130-138` both carry matching reserved-gap comments naming the release, phase, counterpart and never-reuse mechanism, landed as a same-commit pair (`205-04-SUMMARY.md`). |
| 3 | A write to a non-blank UV part reaches the firmware unrefused and programs the region it was given — confirmed on silicon (SC3). | ✓ VERIFIED | `205-BENCH-MATRIX.md` B5: `write w27c512 patB.bin -a 0x000000 -b --skip-erase -f` exits 0 against a genuinely non-blank target (established at B2/B3), read-back verify matches (0 bad of 64), whole-device digest shows only the target region changed. Marked PROXY (W27C512 stands in for a true UV part on protocol `0x07`) — stated, not hidden. This criterion is scoped to the UV handler and is unaffected by the CR-01 gap below, which is scoped to protocol `0x06`. |
| 4 | Flash and RAM deltas are reported per AVR target as measured numbers for uno, uno328pb and leonardo (SC4 / FWBLANK-05). | ✓ VERIFIED | `205-FLASH-RAM.md`: entry 21452/21496/23810 → exit 20956/21000/23314 (uno/uno328pb/leonardo), net −496 B flash / −4 B RAM per target after netting in the 205-05 fix's +22 B. Twelve `.elf`/`.hex` sha256 digests recorded, each build reproduced twice byte-identical. Leonardo quoted against both denominators (81.3% of the real 28672 B ceiling, 5358 B margin). Measured, not estimated, at every step. |
| 5 | A bench regression across at least one UV part and one erasable part shows no behaviour change other than where the refusal now comes from (SC5). | ✓ VERIFIED | `205-BENCH-MATRIX.md` B6 (erasable leg, plain `write`, `FLAG_CAN_ERASE` exemption path): exit 0, digest shows only the target region changed, no behaviour change from pre-205 (the exemption always existed on both sides of this phase). Combined with B5 for the UV role. Both marked PROXY per D-06's stated coverage limit. |
| 6 | `write -init` bodies in `eprom.cpp`, `flash_intel.cpp`, `flash_nor_unlock.cpp` no longer call a blank check, and `configure_eprom`'s `CMD_ERASE` arm assigns no `firestarter_operation_end` (FWBLANK-01/02). | ✓ VERIFIED | `git show 1cf1b22` diff confirmed for all three files; `configure_eprom`'s `CMD_ERASE` arm (`eprom.cpp:50-51`) has no assignment. `test_verify_survival_source_contract.py` carries the absence legs, run RED-then-GREEN per `205-03-SUMMARY.md`. |
| 7 | `mem_util_operation_end` survives with exactly two callers and the `region-end` wire key stays live for `CMD_WRITE` (D-7 / OQ-2). | ✓ VERIFIED | Orchestrator-measured and independently confirmed: `eprom_operations.cpp:85`, `eprom.cpp:317` (two callers). `MSG_ERR_VERIFY` (0xAF), `memory_verify_execute`, `eeprom28c_verify_page_readback`, `flash_util_verify_operation` all present and reachable. |
| 8 | `erase -b` is re-implemented host-side through `check_eprom_blank`, existing *before* the firmware sweep lands, with the 0/1/2 exit contract and `erase -s -b` refused pre-wire (Plan 01 / FWBLANK-02's host half). | ✓ VERIFIED | `205-01-SUMMARY.md` + `git log` ordering: plan 205-01 (`erase -b` host implementation) committed before plan 205-03 (firmware deletion). `cli_handlers.py`'s `erase` handler calls `sys.exit(verdict)` against `check_eprom_blank`'s 0/1/2 contract; `_erase_sector_blank_refusal_exit_code` refuses `erase -s <addr> -b` pre-wire. |
| 9 | The host-side write guard fully owns the safety property the removed firmware write-init blank check used to provide, for every protocol family the guard claims to cover. | ✗ FAILED | See CR-01 gap above. `write_blank_guard.is_erase_exempt` (`write_blank_guard.py:156-170`) is address-blind and silently exempts protocol-`0x06` writes at a non-zero address from any check at all, a case the now-deleted firmware whole-device blank check used to catch. Confirmed via `git show 1cf1b22` that the deleted call was the whole-device wrapper, and via the chip database (190 protocol-0x06 rows, all `Flash/EEPROM`-typed and therefore `FLAG_CAN_ERASE`-eligible) that the affected surface is not a one-chip edge case. |

**Score:** 8/9 truths verified, 1 failed (blocking).

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `firestarter_fw/src/proms/memory.cpp` | Blank-check machinery deleted, `mem_util_operation_end` and its comment intact | ✓ VERIFIED | Confirmed by diff and grep census above |
| `firestarter_fw/include/memory_utils.h` | Declarations removed, `mem_util_operation_end` declaration intact | ✓ VERIFIED | Grep census clean |
| `firestarter_fw/src/proms/eprom.cpp`, `flash_intel.cpp`, `flash_nor_unlock.cpp` | No write-init blank-check call, no `CMD_ERASE` end-op assignment | ✓ VERIFIED | Diff-confirmed |
| `firestarter_fw/include/firestarter.h` | `FLAG_SKIP_BLANK_CHECK` gone, reserved-gap comment present | ✓ VERIFIED | Read directly |
| `firestarter_app/firestarter/constants.py` | `FLAG_SKIP_BLANK_CHECK` gone, reserved-gap comment present | ✓ VERIFIED | Read directly |
| `firestarter_app/firestarter/write_blank_guard.py` | `-b` reaches the guard as an explicit keyword-only signal | ✓ VERIFIED (mechanism) / ✗ substantively incomplete for one protocol | `blank_check_requested` keyword-only param confirmed present and threaded; **but `is_erase_exempt`'s address-blindness is the CR-01 gap** — the module exists and is wired, but does not fully deliver the safety property it claims (own docstring: "the whole safety net") |
| `.planning/phases/.../205-FLASH-RAM.md` | Complete FWBLANK-05 record | ✓ VERIFIED | Reviewed in full above |
| `.planning/phases/.../205-BENCH-MATRIX.md` | Executed bench matrix, criteria 3/5, D-07 skew | ✓ VERIFIED | Reviewed in full above |
| `tools/catalog/messages.toml` | `MSG_ERR_NOT_BLANK` and `DBG_FLAG_SKIP_BLANK` kept + annotated | ✓ VERIFIED (via 205-06-SUMMARY and D-07 leg's dependence on 0xB0 rendering as a sentence in B3) | Not independently re-diffed byte-for-byte in this verification pass; consistent with B3's observed rendered sentence |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `erase -b` (CLI) | `check_eprom_blank` (`eprom_operations.py`) | direct call, `sys.exit(verdict)` | ✓ WIRED | Confirmed in `cli_handlers.py` and exercised on silicon (B7) |
| `write -b` (CLI) | `write_blank_guard.requires_blank_check` | `blank_check_requested` keyword | ✓ WIRED | Confirmed threaded per 205-04-SUMMARY; exercised on silicon (B3, B5) for protocol `0x07` |
| `write -a <addr>` on protocol `0x06` | `write_blank_guard.is_erase_exempt` → host blank-check read | flag-only predicate, no address input | ✗ NOT WIRED (gap) | The link exists mechanically but the predicate ignores the one input (`address`) that determines whether the exemption is actually safe. This is CR-01. |
| `mem_util_operation_end` | `eprom_operations.cpp:85`, `eprom.cpp:317` | direct calls | ✓ WIRED | Orchestrator-confirmed, re-confirmed here |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| FWBLANK-01 | 205-03, 205-01 | Write-init blank check removed from `eprom.cpp`, `flash_intel.cpp`, `flash_nor_unlock.cpp` | ✓ SATISFIED (literal removal) / ⚠️ regression created (CR-01) | Removal itself is complete and gated; but the removal's own safety precondition — "host already owns the capability" — is not fully true for protocol `0x06` at a non-zero write address |
| FWBLANK-02 | 205-03, 205-01 | Erase-end blank check removed from `eprom.cpp` | ✓ SATISFIED | `CMD_ERASE` arm assigns no end-op; host-side `erase -b` replaces it, confirmed on silicon (B7) and gated to land before the firmware deletion |
| FWBLANK-03 | 205-03 | `mem_util_blank_check`, `mem_util_blank_check_region`, `blank_check_saved_address`, `BLANK_CHECK_CHUNK_SIZE` deleted, no caller remains | ✓ SATISFIED | Grep census clean; golden re-derived and verified positionally per SUMMARY |
| FWBLANK-04 | 205-04 | `FLAG_SKIP_BLANK_CHECK` retired from firmware and `constants.py`, recorded as reserved on both sides | ✓ SATISFIED | Confirmed by direct read of both files |
| FWBLANK-05 | 205-02, 205-06 | Flash/RAM freed measured per AVR target, reported as a number | ✓ SATISFIED | `205-FLASH-RAM.md` reviewed in full; twelve digests, three shas, arithmetic checked (reclaim + cost = net) |

**No orphaned requirements** — REQUIREMENTS.md maps exactly FWBLANK-01..05 to Phase 205, and all five appear in at least one plan's `requirements:` frontmatter field (verified against the phase's PLAN frontmatter).

### Anti-Patterns Found

No debt markers (`TBD`/`FIXME`/`XXX`) found in the firmware or host files this phase modified. No unreferenced `TODO`/`HACK`/`PLACEHOLDER` found. The comment-rewrite obligations (D-05's reserved-gap notes, the `eeprom_28c.cpp`/`flash_5v_page.cpp` anti-regression comment rewrites) were checked against the code review's findings — the review found only prose/documentation staleness (WR-01, IN-01), not a stub or a placeholder.

**One finding is elevated above anti-pattern severity and treated as a phase-goal gap:** CR-01, see Gaps Summary below.

### Human Verification Required

None. Every truth resolves to VERIFIED or FAILED on code/git/database evidence; no item requires subjective judgment, visual inspection, or hardware access beyond what the bench matrix already captured on silicon.

### Gaps Summary

**The phase's mechanical work (FWBLANK-01 through FWBLANK-05, as literally worded — code removed, bit retired, machinery gone, numbers measured) is complete, carefully executed, and well-evidenced.** The firmware sweep, the golden re-derive, the reserved-bit records, the negative-address defence-in-depth fix, and the FWBLANK-05 measurement are all independently confirmed against the codebase, not merely asserted by the SUMMARYs. Success criteria 3, 4 and 5 are backed by real silicon evidence in `205-BENCH-MATRIX.md`, correctly scoped and honestly gapped (0x06/0x10 not benched, stated why; no Uno board attached, stated why).

**The one gap (CR-01) is a genuine regression in the safety property this phase's removal depends on, not a cosmetic or documentation issue.** Before this phase, `flash_nor_unlock_write_init` ran an unconditional whole-device blank check after its address-dependent erase (confirmed by diffing commit `1cf1b22`), which caught the case where a sector erase at a non-zero `-a` address left the write's own target region non-blank. Phase 205 removes that check as part of FWBLANK-01, on the documented premise that the host-side guard (Phase 203's `write_blank_guard.py`) already owns the equivalent protection. For protocol `0x06` (AMD/JEDEC NOR-unlock, 190 shipped chips, essentially all `FLAG_CAN_ERASE`-eligible) at a non-zero write address, it does not: `is_erase_exempt` cannot distinguish a whole-chip erase from a sector erase, so it exempts the write from any check at all. This is not a hypothetical — the phase's own `erase -s -b` refusal (built in plan 205-01) shows the sector/whole-device distinction was already understood and handled for the sibling `erase` command; it was never extended to `write`.

This defeats a specific, load-bearing part of the phase's stated safety property ("the host must own the capability before the firmware loses it") for one of the five protocol families the host guard is documented to cover, and it is a live, silent, irreversible-overwrite-class hazard on a large chip family reachable through the ordinary `-a` option on `write` — not a corner the phase already named and accepted (D-06's `0x06` gap is about bench coverage of the *removal*, not about this exemption defect, and is proven safe there by native test rather than exposed to it).

**Recommendation:** Land a fix for `is_erase_exempt` (or its caller) before this phase is considered closed — the code review's suggested patch (address-aware exemption for protocol `0x06`) is concrete and small, and WR-02's companion test gap should close in the same change. This is squarely inside FWBLANK-01's scope (the write-init removal this exemption exists to backstop) rather than a new, separately-scoped defect, so it belongs in this phase's closure rather than filed to backlog.

No deferred items apply — this gap is not addressed by any later phase's stated goal or success criteria (Phase 206 is `dev test`/session-lease work, Phase 207 is a version bump and wiki page; neither's stated scope touches `write_blank_guard.py`'s exemption logic).

---

_Verified: 2026-09-22_
_Verifier: Claude (gsd-verifier)_
