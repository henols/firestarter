# Phase 141 Plan 01 — Pre-Measurement Predictions

**Written:** 2026-08-10, before Task 3 commits, and before any `src/proms/eprom.cpp` or
`src/proms/memory.cpp` byte moves anywhere in this phase (plan 141-04 owns that rewrite).

**Why this document exists (Phase 140's precedent, `140-PREDICTIONS.md` / `140-PARAM-TABLE-RECORD.md`
§6):** a flash/RAM delta or a D-13 inventory-count movement is only evidence of what LOOP-01…08
actually did if the number was committed to git *before* the change that produces it — otherwise a
number that happens to look reasonable after the fact is indistinguishable from one quietly adjusted
to fit whatever was observed. This document is committed to the meta repo (branch
`gsd/v1.31-27c-programming-algorithm-fidelity`) as this plan's Task 3, strictly after Task 1
(catalog) and Task 2 (sync/regen) — neither of which touches `firestarter/src/`. The exact commit SHA
that carries this document is intentionally **not** written into the document itself (a commit cannot
contain its own resulting hash); plan 141-09, the measurement plan, records that SHA and this file's
"Observed" section when it quotes this document — `git log --oneline -1 --
.planning/phases/141-per-byte-program-loop/141-PREDICTIONS.md` is the authoritative source for it in
the interim, so the ordering is auditable from git alone without a self-referential edit.

---

## P1. AVR flash delta — per-target signed prediction, plus resulting absolute vs BASE-01

**Baseline used:** `scripts/baseline/size_baseline_base01.json` (**BASE-01**) — `uno` **23932**,
`uno328pb` **23976**, `leonardo` **26072** flash bytes. This is the baseline `check_size_baseline.py
--policy merge05` compares against, named explicitly via `--baseline`; it is **not** the live branch
tip and **not** `origin/beta`'s drifted tip.

**Live branch-tip measurement (this session, cold, unchanged since Phase 140 — confirmed by re-running
`pio run` for all three targets before writing this file):** `uno` 23954 (+22 vs BASE-01),
`uno328pb` 24004 (+28 vs BASE-01), `leonardo` 26016 (−56 vs BASE-01). These three numbers are **not**
this phase's prediction — they are Phase 140's already-measured, already-explained state (the
`EPROM_PARAMS[]`/`EPROM_PARAM_KEYS[]` table exists in `src/proms/eprom_params.cpp` but is still
**`--gc-sections`-collected**, because nothing in `src/` calls `eprom_params_for()` yet). This plan
predicts what **Phase 141's own change** (plan 141-04's rewrite, landing after this document is
committed) adds on top of that live tip.

**Growth budget each target must respect, from BASE-01, per MERGE-05 (`check_size_baseline.py:107`,
`MERGE05_UNO_CLASS_FLASH_BAND = 64`):**

| Target | BASE-01 | Live tip (Phase 140 state) | Delta vs BASE-01 already spent | Growth budget remaining for Phase 141 |
|---|---|---|---|---|
| `uno` | 23932 | 23954 | +22 | **42 B** |
| `uno328pb` | 23976 | 24004 | +28 | **36 B** — binding constraint |
| `leonardo` | 26072 | 26016 | −56 | **56 B** (absolute must stay ≤ 26072 — "must not grow") |

**`uno328pb` is the binding constraint**: it has the least remaining headroom (36 B) of the three.

**Prediction — Phase 141's own signed flash delta, on top of the live tip:**

| Target | Predicted Phase-141-only delta | Predicted resulting absolute | Predicted total delta vs BASE-01 | Within budget? |
|---|---|---|---|---|
| `uno` | **+30 B** | 23954 + 30 = 23984 | **+52 B** | Yes — 12 B of the 42 B budget left unused |
| `uno328pb` | **+30 B** | 24004 + 30 = 24034 | **+58 B** | Yes, but only 6 B of the 36 B budget left unused — the tightest margin of the three, consistent with `uno328pb` being named the binding constraint |
| `leonardo` | **+18 B** | 26016 + 18 = 26034 | **−38 B** (i.e. 38 B under the 26072 must-not-grow ceiling) | Yes, comfortably — 38 of the 56 B allowance unused |

**Not F-138-02's headroom.** F-138-02's 8 B / 2 B figure describes `origin/beta`'s drifted tip, which
is **not** in this branch's ancestry — re-verified as part of writing this document:
`git -C /workspaces/firestarter merge-base --is-ancestor 6fab4ea HEAD` exits **non-zero** (1), i.e.
**NO**, `6fab4ea` is not an ancestor of this branch's `HEAD`. F-138-02 becomes relevant only once
`origin/beta`'s drift merges in — Phase 144 / TEST-08's problem, not this plan's.

**Methodology / ingredients ledger the +30/+30/+18 figures rest on** (read against the live
`firestarter/src/proms/eprom.cpp` and `eprom_params.h`/`eprom_params.cpp` this session, not recalled):

*Adds* (funded, first `src/` reference of Phase 140's table — `--gc-sections` stops collecting it the
moment anything calls it):
- `EPROM_PARAMS[]` 3 rows × 12 B `PROGMEM` (36 B) + `EPROM_PARAM_KEYS[]` 3 × 1 B (3 B) = 39 B of data
  that exists today but is dropped at link time; referencing it via `eprom_params_for()` makes the
  linker keep it.
- `eprom_params_for()`'s linear-scan accessor body (`src/proms/eprom_params.cpp:51-58`) — a ≤3-iteration
  loop with one `pgm_read_byte` compare per iteration — newly linked for the same reason, ~30-40 B.
- Six hoisted `pgm_read_*` reads at the loop's setup (one per `eprom_params_t` column) — a handful of
  bytes each on AVR, ~30-40 B total.
- The per-byte loop body itself replacing `eprom_write_execute`'s current `for (int w = 0; w <
  NUMBER_OF_RETRIES; w++)` block-retry loop (`eprom.cpp:163-179`, 17 lines) with a byte-indexed
  pulse→verify loop carrying four new predicates (byte-loop bound, `0xFF` skip, already-matching skip,
  budget checks) — net new control flow, ~90-110 B.
- `eprom_overprogram_us()` (new pure function per D-08, `(pulse_count, pulse_us, factor, cap_us) → us`,
  with a clamp and 32-bit-overflow-safe arithmetic) — ~50-70 B, gated by `overprogram_factor` (0 on
  every live row today, so its *body* is linked but its *effect* is inert — see P1's caveat below).
- `mem_util_delay_us` / `mem_util_split_delay` (the ms/µs-split safe delay helper, D-06) plus its two
  call sites replacing the bare `delayMicroseconds(handle->pulse_delay)` at `memory.cpp:329` and
  `delayMicroseconds(handle->pulse_delay)` at `eprom.cpp:283` — ~40-60 B including both call-site diffs.
- Three new `LOG_ERROR_ID_*` call sites (D-03's `MSG_ERR_PULSE_TOO_WIDE`, LOOP-04's
  `MSG_ERR_MAX_PULSES` and `MSG_ERR_ENERGY_CAP`) — ~10-14 B per call site, ~30-42 B total.
- The `pins >= 32` branch (D-09's guarded path in `eprom_internal_set_control_register` or the loop
  itself) — ~14-18 B.
- The `verify_mode == VERIFY_PER_PULSE_PLUS_FINAL` gated final full-block pass (`0x07`/`0x08` only,
  reusing `memory_get_data` in a loop) — ~40-60 B, mostly loop overhead since the read primitive
  already exists.

*Removes* (all currently present, read directly from `eprom.cpp` this session):
- `program_mismatched_bytes()` (`eprom.cpp:114-126`, 13 lines incl. the `handle->firestarter_set_data`
  call and the bitmask test) — ~45-60 B.
- `verify_and_update_mask()` (`eprom.cpp:129-141`, 13 lines incl. the compare and the two bitmask
  writes) — ~50-65 B.
- The `NUMBER_OF_RETRIES` block loop and its adaptive-growth arithmetic
  (`handle->pulse_delay = org_delay + (org_delay * retries / NUMBER_OF_RETRIES)`, `eprom.cpp:163-179`)
  — a `uint32_t` multiply and a divide-by-a-compile-time-constant(20), plus the loop control itself.
  **Named uncertainty:** AVR has no hardware 32-bit multiply/divide; `avr-gcc` may either call
  `__mulsi3`/a division-helper from `libgcc`, or (for the constant divisor 20) strength-reduce the
  divide into a multiply-by-reciprocal-and-shift. Either routine, if **already linked** elsewhere in
  the same binary for an unrelated reason, is not reclaimed by removing this one call site — only the
  call-site overhead is. This prediction assumes the routine is *not* uniquely kept alive by this one
  site (no other 32-bit multiply/divide was found elsewhere in `src/` by a live grep this session), so
  removing this site reclaims the loop control plus a genuine share of the arithmetic, ~80-110 B.
- `memset(mismatch_bitmask, 0xFF, sizeof(mismatch_bitmask))` (`eprom.cpp:157`) — the call site only,
  ~10-14 B; `memset` itself is a shared libc routine almost certainly already linked elsewhere (e.g.
  Arduino's own runtime init), so its body is not reclaimed.
- Two now-orphaned `LOG_*_ID` call sites, `MSG_INFO_RETRIES` (`eprom.cpp:170`) and
  `DBG_PULSE_DELAY_MISMATCH` (`eprom.cpp:178`) — ~10-14 B each, ~20-28 B total. (Their catalog IDs
  themselves stay assigned per this plan's Task 1 action — deleting an id is a separate, rejected
  option; see this plan's `<action>` text.)
- `eprom_internal_ensure_regulator_enabled` (`eprom.cpp:327-332`) reclaims **0 B** — it is already
  `--gc-sections`-collected (zero callers today); do not count it in either ledger.

Net of the ranges above lands in the same neighbourhood as the point estimates in the table (+30 /
+30 / +18 B) but the ranges themselves are wide enough that the actual measured number could
plausibly land anywhere from roughly break-even to the edge of `uno328pb`'s 36 B budget — which is
exactly why `uno328pb` is flagged as binding rather than assumed safe.

## P2. AVR RAM delta — exactly 0 on all three targets

**Prediction:** RAM-used stays at `1573` / `1579` / `2014` bytes (`uno` / `uno328pb` / `leonardo`) —
an exact-zero delta, not merely a small one. MERGE-05's own comparator enforces this as an
equality, not a band, on every AVR target (`check_size_baseline.py:224-227`).

**Mechanical basis:** the only stack allocation this rewrite removes is
`uint8_t mismatch_bitmask[DATA_BUFFER_SIZE / 8]` (`eprom.cpp:155`) — **64 B on Uno-class**
(`DATA_BUFFER_SIZE` 512 / 8) and **128 B on Leonardo** (1024 / 8). A stack array never appears in the
linker's static `ram_used` figure (it is neither `.data` nor `.bss`), so removing it will **not
show up as a RAM win** in `avr-size` output — but it genuinely removes 64/128 B of peak stack depth
on parts with only 475 B (`uno`) / 469 B (`uno328pb`) / 546 B (`leonardo`) of static RAM headroom at
BASE-01. Recorded here as a non-metric safety improvement, not as part of the RAM delta claim. The
new loop's own locals (six hoisted `eprom_params_t` column values, a `pulses` counter, an
`accumulated` energy total, the saved `org_delay`) are a handful of registers/stack slots — far
smaller than what they replace, and none of them are static (`.data`/`.bss`) allocations, so none of
them can move `ram_used` either. `EPROM_PARAMS[]` / `EPROM_PARAM_KEYS[]` are `PROGMEM` (never copied
to `.data`/`.bss` at startup), so referencing them for the first time costs 0 RAM regardless of the
flash cost predicted in P1.

## P3. D-13 protocol-branch-inventory movement — tier-1 unchanged, tier-2 net growth predicted

**Before (measured this session, `tests/golden/protocol_branch_inventory.json`, unchanged since Phase
140 recorded it):** **24** total sites — **3** tier-1 (protocol-keyed) at lines `71`, `145`, `218`;
**21** tier-2 (handle-field-keyed).

**Prediction: tier-1 stays exactly 3; tier-2 grows, it does not shrink.** CONTEXT.md D-11's framing
("record the shrinkage") assumed removals would dominate; this plan's own read of the live source
shows the new loop adds more handle-field-keyed predicates than the old block loop had, so **growth is
the predicted, legitimate outcome** — only a **fourth tier-1 site** would be a real TABLE-05
violation. `configure_eprom`'s `:71` switch (the `pulse_delay == 0` fallback, kept verbatim) and
`eprom_check_vpp`'s `:218` predicate (untouched, line only shifts) are unaffected. `eprom_write_execute`'s
`:145` VPP predicate (`protocol == 0x0B || FLAG_VPE_AS_VPP`) is **kept verbatim** this phase — replacing
it with the table's `vpp_path` column is Phase 142 / VPP-01, not this phase's rewrite.

**Tier-2 sites predicted to disappear** (all read directly from the live file this session):
- `eprom.cpp:119` — `for (uint32_t i = 0; i < handle->data_size; i++)` inside
  `program_mismatched_bytes()` (deleted whole).
- `eprom.cpp:131` — `for (uint32_t i = 0; i < handle->data_size; i++)` inside
  `verify_and_update_mask()` (deleted whole).
- `eprom.cpp:132` — the verify-byte comparison inside the same function (deleted whole).
- `eprom.cpp:144` (`handle->firestarter_get_control_register(handle, CTRL_VPP_REGULATOR_ENABLE) == 0`)
  is **predicted to survive unchanged** — nothing in LOOP-01…08 requires restructuring this
  idempotency guard, and VPP-routing consolidation is explicitly Phase 142's job, not this phase's. It
  is named here (per this plan's own instruction) only to record that the prediction is "kept", not
  "removed".

Predicted removed count: **3**.

**Tier-2 sites the new loop is predicted to add** (one site per natural `if`/`for` span, matching
`_extract_predicates`'s one-span-per-keyword rule — a compound `&&`/`||` inside one `if` still counts
as one site):
1. The byte-loop bound (`for` over `handle->data_size`, replacing the two removed block-loop bounds
   above with one byte-indexed one).
2. The `0xFF` skip (LOOP-06 — a not-yet-erased byte needs zero pulses only if already `0xFF`; this is
   a fresh pre-check, not part of the old loop).
3. The already-matching skip (LOOP-06 — a pre-pulse read-compare against `data_buffer[i]`).
4. The `pulses >= max_pulses` check (LOOP-04/LOOP-05, reading the table's `max_pulses` column).
5. The `energy_cap_us && accumulated >= energy_cap_us` check (LOOP-04, one `if` span despite the
   internal `&&` — D-04 requires this and #4 to report *distinct* message IDs, which is why this
   prediction assumes two separate `if`s rather than one combined condition).
6. The `pins >= 32` branch (D-09's guarded path).
7. The `row == NULL` fail-closed refusal (D-05, the first live `src/` check of `eprom_params_for()`'s
   return value).
8. D-03's pre-flight refusal, `energy_cap_us > 0 && pulse_delay > energy_cap_us`, in `configure_eprom`
   (one `if` span; also counted here because the D-13 scanner scans the whole `eprom.cpp` file, not
   only `eprom_write_execute`).
9. The `overprogram_factor` / `op_us` guard gating the overprogram pulse (D-07/D-08).
10. The `verify_mode == VERIFY_PER_PULSE_PLUS_FINAL` check gating the final full-block pass.
11. The final pass's own loop bound (a second `for` over the block, `0x07`/`0x08` only).
12. The final pass's own byte comparison (the `if` inside that loop).

Predicted added count: **12** (methodology-dependent — see the named uncertainty below).

**Predicted after-count:** tier-2 `21 − 3 + 12 = 30`; tier-1 stays `3`; **predicted total = 33**
(up from 24 — net growth of 9 sites, all tier-2, zero tier-1).

**Named uncertainty, stated plainly rather than smoothed over:** `_extract_predicates`
(`tests/test_protocol_branch_inventory.py:277`) counts **one site per `if`/`for`/`while`/`switch`
keyword occurrence**, taking the *entire* parenthesised span as one predicate string regardless of
how many `&&`/`||` sub-clauses it contains. Items 4 and 5 above are predicted as two separate `if`
statements (not one combined condition) specifically because D-04 requires the two budget limits to
report distinct message IDs, which is naturally expressed as two separate checks — but plan 141-04
could legitimately implement it either way, and item 7 (`row == NULL`) could plausibly appear in
either `configure_eprom` or `eprom_write_execute` (or, less likely, both), which would shift the count
by ±1. **This prediction's after-count of 33 is the falsifiable central estimate; plan 141-09 records
the measured pair (before/after) against this document once the rewrite lands, and a divergence from
33 is not itself a violation** — only a fourth **tier-1** site is.

---

## Reconciliation

P1-P3 above are predictions recorded **before** measurement, committed to this file's first version
in the meta repo, strictly before plan 141-04 (or any later plan in this phase) changes a single byte
of `firestarter/src/proms/eprom.cpp` or `firestarter/src/proms/memory.cpp`. This document does not
receive an "Observed" section from this plan — Task 3's own `<done>` criterion is that the prediction
exists and is committed first, not that it is reconciled here. Plan 141-09 (the measurement plan) is
where the cold `pio run` figures and the re-derived `protocol_branch_inventory.json` counts are
measured and compared against P1-P3, and where any divergence — including a divergence this document
already flags as plausible (P1's wide ranges, P3's ±1 count uncertainty) — is named rather than
silently absorbed. Phase 144 / TEST-08 is where the full-phase (138-143) flash/RAM delta is
reconciled against the sum of every phase's individual predictions, including this one.
