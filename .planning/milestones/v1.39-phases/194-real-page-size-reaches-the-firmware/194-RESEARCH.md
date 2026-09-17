# Phase 194: Real Page Size Reaches the Firmware — Research

**Researched:** 2026-09-15
**Domain:** AVR firmware page-write arithmetic; a generated chip-database emit rule; dual-repo lockstep gates
**Confidence:** HIGH — every numeric claim below was measured in-session against the pinned upstream XML, the two sub-repo working trees, and real `pio` builds. Two CONTEXT.md claims are corrected; both corrections are in this phase's favour.

## Summary

All four research questions resolve cleanly and no blocker was found. **R1's join holds 27/27** — every `algorithm: 5` row in `chip_database.json` is upstream-native protocol `0x05` in the pinned `infoic.xml`, so D-02's emit condition needs no amendment. Every figure in CONTEXT.md's measured table reproduced exactly, and the projected carrier count of **45** was independently re-derived (18 + 27 + 0).

**R2 delivers one corrected expectation.** CONTEXT.md hoped the mask-for-`%` swap "may free flash rather than cost it". It does not. `__udivmodsi4` has **seven** callers in the linked `uno` ELF, of which `flash_5v_page_write_execute` is one — removing that one caller leaves the 68-byte helper linked for the other six. A measured before/after build of the full D-05/D-06 shape costs **+6 bytes on both envs**. Headroom is `uno` 10658 B and `leonardo` 4956 B, both comfortable. The refusal id itself is **free in flash**: `include/messages.h` is ID-only and `LOG_ERROR_ID(id)` expands to `rurp_log_id(id, NULL, 0)` — there is no firmware-side PROGMEM format string for an `id_frame` message.

**R3 and R4 each surfaced a constraint CONTEXT.md did not name.** R3: the `ERROR` id band `0xA0–0xBF` has exactly **one** free id left, `0xBF`. R4: the sweep found **two** further host gates and **two** firmware native test cases that move, beyond the three CONTEXT.md named — most consequentially `tests/test_wire_dict_equivalence.py`, which compares a live 746-chip wire capture against a golden plus three named delta layers and will fail on 25 changed records unless a fourth delta layer is authored.

**R5 is the most valuable finding.** `flash_5v_page_write_execute` is already reachable from a CI-run native suite with a recording-bus oracle — no `host_stubs` addition is needed. But the recording buffer is capped at **256 entries with silent truncation**, and the measured density is **3 entries per written byte plus 11 for the SDP prefix**, so the buffer saturates at roughly **81 bytes of data**. Any multi-page boundary assertion past that point is vacuous today. The buffer cap must be raised and given a saturation signal before D-08's firmware test can prove anything.

**Primary recommendation:** sequence the phase as *(1) branch + buffer-cap prerequisite → (2) generator + regenerate → (3) the five host gates and two golden layers → (4) firmware consumption + refusal + the two existing native cases → (5) the new 7-pair native boundary test → (6) the 27-row record → (7) the `W29C020` no-regression bench run*. Do not let (5) precede the buffer-cap fix in (1), or it will pass vacuously.

---

## User Constraints (from CONTEXT.md)

### Locked Decisions

> - **D-01: No hand-curated page sizes at all — `build_db.py` reflects infoic ground truth and the database is generated from that truth.** `_PAGE_SIZE_BY_PART` (`build_db.py:102`) is **removed**, along with its two entries and the emit arm that reads it. This is output-neutral: both entries are `0x05`, and both already equal their raw upstream value, so no emitted number changes as a consequence of the removal. — **Reversibility:** reversible — the table is 14 lines and its two values are recorded here and in `git log`.
>
> - **D-02: Provenance keying is KEPT and extended to `0x05`.** The emit condition becomes: the row's **own upstream** `protocol_id` is `0x0D` **or** `0x05` → emit `raw_page_size`. It does **not** go flat across every row. [...] **Result: 20 → 45 `page_size` carriers** (18 `0x0D`-native + 27 `0x05`-native + 0 curated). — **Reversibility:** costly — the emitted database is a published artifact consumed by every installed host, and three gates plus a golden pin the current count.
>
> - **D-03: The generator asserts what it emits, fail-closed.** `build_db.py` raises and writes **no database** if an emitted `page_size` is not a power of two within range — the same shape as `interpret_timing`'s existing fatal on an unparseable `pulse_delay` (`build_db.py:378-384`), and the shape backlog **999.57** proposes for `size_bytes`. It costs nothing today: all 45 emitted values are already 64/128/256/512. Its purpose is that a future infoic refresh cannot ship a value the firmware would refuse. — **Reversibility:** reversible.
>
> - **D-04: `infoic_page_size_raw` is untouched** and stays the raw provenance axis, per Phase 149's D-02. It is not read on the wire and not read by the host.
>
> - **D-05: Fail closed — no page size, no write.** When `handle->page_size` is absent, `0`, or fails validation on a `0x05` write, the firmware **refuses with a named error** and performs no write. It does not fall back to a derivation, and it does not guess. [...] — **Reversibility:** costly.
>
> - **D-06: `flash_5v_page_page_size()` is REMOVED, not retained as a fallback.** (`firestarter_fw/src/proms/flash_5v_page.cpp:27-31`.) The silent-corruption path leaves the binary rather than lingering behind a condition. Its block comment is removed with it — and per `CLAUDE.md`'s hard rule, no replacement comment is written into the source. — **Reversibility:** reversible.
>
> - **D-07: The refusal is enforced in BOTH the host and the firmware.** The host refuses a `0x05` write **before any serial byte** when the resolved chip carries no `page_size` — the fail-closed in-host guard pattern established in v1.12 (`ProtocolNotImplementedError`) and v1.20 (the algorithm-presence guard). The firmware refuses independently, because it is the only layer that can protect the silicon from any caller. The host's message names the chip. The firmware's message is an error id. — **Reversibility:** reversible.
>
> - **D-08: A host data test over all 27 rows AND a native firmware consumption test.** Both, not either. **Host:** extend `firestarter_app/tests/test_page_size_invariants.py` to a 27-row table that asserts, for every `algorithm: 5` part, (a) the emitted `page_size` equals the part's real page, **and** (b) for exactly the 18, that it also equals what the old derivation produced. **Firmware:** a native test that drives `flash_5v_page_write_execute` over the 27 `(mem_size, page_size)` pairs and asserts the page-start and page-commit boundaries land where the real page says.
>
> - **D-09: The firmware INFO log is NOT funded in this phase.** [...] The todo stays pending, unmodified, with its `resolves_phase` tag intact.
>
> - **D-10: PAGE-03 cannot be met from current inventory — a `W29C512` is being ordered.** [...] ⚠ **Name-collision hazard:** `W29C512` is a **third distinct part** from `W27C512` and `M27C512`. Check the seated part by **chip-ID**, never by the marking.
>
> - **D-11: The software half lands now. PAGE-03's hardware leg is held OPEN.** [...] Until the part arrives that split reads **0 of 9 on hardware, 9 of 9 on the database comparison**.
>
> - **D-12: The new-host / old-firmware skew is filed, not fixed.** [...] File it as a backlog item.

### Claude's Discretion

> - **Where the 27-row record lives** — the operator said "you decide". Decision: a **committed artifact under `.planning/v1.39/`**, a 27-row table (part · size · derived · real · verdict · evidence class) following the `.planning/v1.33/sweep-outcome-record.md` precedent, with `194-SUMMARY.md` citing it rather than duplicating it.
>
> - **The mask-vs-`%` implementation shape** (see Existing Code Insights) and the naming of the refusal error id are left to research and planning.

### Deferred Ideas (OUT OF SCOPE)

> - **New-host / old-firmware version skew for `0x05` writes** (D-12) — file as a backlog item.
> - **A firmware INFO log naming the effective page size** (D-09) — stays as the pending todo, `resolves_phase` tag intact.
> - **The same defect class in the other 12 protocols** — out of scope per `REQUIREMENTS.md`. If found, file it.
> - **The 11 promoted `0x0D` rows at raw 16/32** whose 64-byte floor safety is unproven — Phase 149's D-04, unchanged by this phase, still pending.

---

## Phase Requirements

| ID | Description (verbatim, `.planning/REQUIREMENTS.md:45-51`) | Research Support |
|----|------------|------------------|
| PAGE-01 | "The page size used by the protocol `0x05` write path is the part's recorded page size from the chip database, not a value derived from the device's total size." | §R2 gives the exact mask form, resolve point, validation constant and ceiling. §R3 gives the refusal id and the host guard insertion point. The wire seam needs no work — §Integration Points. |
| PAGE-02 | "For **all 27** protocol `0x05` parts, the page size the firmware uses equals the part's recorded real page. This is measured across the whole set, not asserted for the 9 known to be wrong — a fix that corrects those 9 while breaking one of the other 18 is not a fix." | §R1 supplies the measured 27-row table (both halves of the claim: real page, and the old derivation's value) and the 7 distinct `(mem_size, page_size)` pairs. §R5 supplies the firmware-side measurement mechanics and the vacuity hazard that must be closed first. |
| PAGE-03 | "A contiguous multi-page write to one of the 9 previously under-sized parts reads back byte-identical on real silicon." | §R1 names the 9 exactly and confirms `W29C512` (D-10's ordered part) is one of them — real page 128, derived 64. Held OPEN per D-11. |

---

## R1 — The all-27 upstream provenance join

### The pinned input

`firestarter_app/tools/build_db.py` fetches its input over HTTP from a SHA-pinned URL. There is **no vendored or cached copy in either repository** — verified by `/usr/bin/find` over the whole tree; the only local `infoic` artefacts are documentation notes and `.claude/skills/devtest-rootcause/scripts/infoic_lookup.py`, which downloads and caches the same URL on demand.

`[VERIFIED: firestarter_app/tools/build_db.py:10-17]` — quoted verbatim:

```python
# Pinned to the SHA recorded in tools/DECODE-NOTES.md §0/§3 so the fetch is
# deterministic and the baseline re-pin is reproducible. Was /-/raw/master/ —
# switched to the pinned commit at DECODE-NOTES.md §3 discretion. Short form:
# a8efaedc.
MINIPRO_XML_URL = (
    "https://gitlab.com/DavidGriffith/minipro/-/raw/"
    "a8efaedc236c1d9718bd28299dfbb99536b010ff/infoic.xml"
)
```

`[VERIFIED: firestarter_app/tools/build_db.py:390-398]` — the fetch is `requests.get(MINIPRO_XML_URL, timeout=30)` then `ET.fromstring(r.content)`; there is no local-path fallback and no `--xml` argument.

**Pin:** minipro `a8efaedc236c1d9718bd28299dfbb99536b010ff`.
**Fetched this session:** 17,861,009 bytes, `sha256 = cdd21319ae6cce2316ca2361a9fb82cba89b27b66bb78d58b01032a441106b8a`.
**Planner note:** a task that regenerates the database needs network egress to gitlab.com. It worked in this session.

### The join

Method (independent re-derivation, not an inference from `classify()`): index every `<ic>` under `database[@type='INFOIC2PLUS']` by `(manufacturer/@name, canonical_part_number)` where `canonical_part_number` is built with build_db's own rule — comma-split, `@PACKAGE` suffix stripped per alias, deduped, rejoined (`[VERIFIED: firestarter_app/tools/build_db.py:648-654]`). Then join each of the 27 `algorithm: 5` rows to its upstream records and read their own `protocol_id`. **The index deliberately applies no DIP/SMD/pin-count filter**, so every upstream record sharing the part number — including the SMD and serial variants build_db discards — is included. That makes the claim stronger, not weaker.

**11,481** `<ic>` records scanned.

| # | mfg | part_number | size | raw page | `page_size` today | derived | verdict | own upstream `protocol_id` |
|---|-----|-------------|------|----------|-------------------|---------|---------|----------------------------|
| 1 | ASD | AE29F1008 | 131072 | 128 | — | 128 | equal | `0x5` (n=4, all pages 128) |
| 2 | ASD | AE29F2008 | 262144 | 128 | — | 128 | equal | `0x5` (n=4, 128) |
| 3 | ASD | AE29F4008 | 524288 | 256 | — | 256 | equal | `0x5` (n=4, 256) |
| 4 | ATMEL | AT29BV010A,AT29LV010A | 131072 | 128 | — | 128 | equal | `0x5` (n=4, 128) |
| 5 | ATMEL | AT29BV020,AT29LV020 | 262144 | 256 | — | 128 | **UNDER 2×** | `0x5` (n=4, 256) |
| 6 | ATMEL | AT29BV040,AT29LV040 | 524288 | 512 | — | 256 | **UNDER 2×** | `0x5` (n=4, 512) |
| 7 | ATMEL | AT29BV040A,AT29LV040A | 524288 | 256 | — | 256 | equal | `0x5` (n=4, 256) |
| 8 | ATMEL | AT29C010A | 131072 | 128 | — | 128 | equal | `0x5` (n=4, 128) |
| 9 | ATMEL | AT29C020 | 262144 | 256 | — | 128 | **UNDER 2×** | `0x5` (n=4, 256) |
| 10 | ATMEL | AT29C040 | 524288 | 512 | — | 256 | **UNDER 2×** | `0x5` (n=4, 512) |
| 11 | ATMEL | AT29C040A | 524288 | 256 | — | 256 | equal | `0x5` (n=4, 256) |
| 12 | ATMEL | AT29C256 | 32768 | 64 | — | 64 | equal | `0x5` (n=2, 64) |
| 13 | ATMEL | AT29C257 | 32768 | 64 | — | 64 | equal | `0x5` (n=2, 64) |
| 14 | ATMEL | AT29C512 | 65536 | 128 | — | 64 | **UNDER 2×** | `0x5` (n=4, 128) |
| 15 | ATMEL | AT29LV256 | 32768 | 64 | — | 64 | equal | `0x5` (n=2, 64) |
| 16 | ATMEL | AT29LV512 | 65536 | 128 | — | 64 | **UNDER 2×** | `0x5` (n=4, 128) |
| 17 | SST | SST29EE010 | 131072 | 128 | — | 128 | equal | `0x5` (n=4, 128) |
| 18 | SST | SST29EE020 | 262144 | 128 | — | 128 | equal | `0x5` (n=4, 128) |
| 19 | SST | SST29EE512 | 65536 | 128 | — | 64 | **UNDER 2×** | `0x5` (n=4, 128) |
| 20 | SST | SST29LE010,SST29VE010 | 131072 | 128 | — | 128 | equal | `0x5` (n=4, 128) |
| 21 | SST | SST29LE020,SST29VE020 | 262144 | 128 | — | 128 | equal | `0x5` (n=4, 128) |
| 22 | SST | SST29LE512,SST29VE512 | 65536 | 128 | — | 64 | **UNDER 2×** | `0x5` (n=4, 128) |
| 23 | WINBOND | W29C010,W29C011,W29C011A,W29EE010,W29EE012 | 131072 | 128 | — | 128 | equal | `0x5` (n=1, 128) |
| 24 | WINBOND | W29C020,W29C020C,W29C022 | 262144 | 128 | **128** | 128 | equal | `0x5` (n=4, 128) |
| 25 | WINBOND | W29C040,W29C042 | 524288 | 256 | **256** | 256 | equal | `0x5` (n=2, 256) |
| 26 | WINBOND | W29C512,W29EE512 | 65536 | 128 | — | 64 | **UNDER 2×** | `0x5` (n=4, 128) |
| 27 | WINBOND | W29EE011 | 131072 | 128 | — | 128 | equal | `0x5` (n=1, 128) |

### Verdict on D-02's claim

**The claim HOLDS, 27 of 27.** `[VERIFIED: in-session join against minipro a8efaedc]` — script output verbatim:

```
upstream <ic> records scanned (INFOIC2PLUS, all): 11481
algorithm:5 rows in chip_database.json: 27
total rows in db: 746; rows carrying programming.page_size: 20
carrying infoic_page_size_raw (non-zero): 27/27
carrying page_size today: 2
raw == derived: 18; raw > derived (under-sized): 9; raw < derived (over): 0
FALSIFYING rows (upstream proto not exactly 0x05, or no match): NONE — 27/27 upstream-native 0x05
current carriers by upstream provenance: 0x0D-native=18 0x05-native=2 other/curated=0
PROJECTED carriers under D-02 (own upstream proto in 0x0D|0x05, raw non-zero): 45 (0x0D=18, 0x05=27)
  rows matching provenance but raw==0 (would be omitted / or would trip D-03): []
  emitted values failing power-of-two-in-[1,512]: none
```

**No row falsifies D-02.** Not a single `algorithm: 5` row arrives by promotion, and no upstream record sharing one of these part numbers carries any protocol other than `0x05`. D-02's emit condition needs no amendment.

### CONTEXT.md's measured table — re-derived, agrees on every figure

| Figure | CONTEXT.md | This session | Agree? |
|---|---|---|---|
| `algorithm: 5` rows | 27 | 27 | ✅ |
| carrying `infoic_page_size_raw` | 27 of 27 | 27 of 27 | ✅ |
| carrying `page_size` today | 2 (`W29C020` 128, `W29C040` 256) | 2, same two, same values | ✅ |
| derived == real | 18 | 18 | ✅ |
| derived < real (always 2×) | 9 | 9, every one exactly 2× | ✅ |
| derived > real | 0 | 0 | ✅ |
| `page_size` carriers across 746 rows | 20 | 20 | ✅ |
| Projected carriers | 45 (18 + 27 + 0) | 45 (18 + 27 + 0) | ✅ |

**No disagreement to report.** CONTEXT.md's §Phase Boundary table is sound and may be cited as measured.

### Corroborations worth reusing

1. **The 0x0D side of the rule is untouched and re-proven.** Joining all 84 `algorithm: 13` rows to their own upstream `protocol_id` gives `{0xd: 18, 0x7: 17, 0xb: 14, (0x7,0xa): 30, (0xa,0xb): 5}` = 18 native + 66 promoted. `[VERIFIED: in-session join]` Exactly Phase 149's split. D-02's projected `0x0D` contribution of 18 is therefore the same 18, not a recount.
2. **An in-repo independent pin of the 27 already exists.** `[VERIFIED: firestarter_app/tests/test_lock_status_class_partition.py:296-327]` defines `_ALGORITHM_0X05_KEYS: frozenset[str]` with a module-level `assert len(_ALGORITHM_0X05_KEYS) == 27`. Its 27 `MFG/part_number` strings match this join's 27 exactly. Reuse this frozenset as the identity source for the new 27-row host table rather than re-authoring the list — but **import or duplicate it, do not move it**, because that module's own leg 3 asserts the live DB population against it.
3. **The 9 under-sized parts are:** `AT29BV020,AT29LV020`; `AT29BV040,AT29LV040`; `AT29C020`; `AT29C040`; `AT29C512`; `AT29LV512`; `SST29EE512`; `SST29LE512,SST29VE512`; `W29C512,W29EE512`.
4. **D-10's ordered bench part is confirmed to be one of the 9.** `WINBOND/W29C512,W29EE512` — 65536 B, real page **128**, derived page **64**, under by exactly 2×. The bench choice is sound and will exercise the fix, not just the no-regression case. `[VERIFIED: in-session join; firestarter_app/firestarter/data/chip_database.json]`
5. **D-03 costs nothing and would not have fired.** All 45 projected emitted values pass "power of two in [1, 512]"; the set is `{64, 128, 256, 512}`. No candidate row has `infoic_page_size_raw == 0`.

### Not-fixed-on-beta spot-check

`[VERIFIED: git rev-parse, blob shas]` — after `git fetch origin beta` in both sub-repos:

| File | `origin/beta` blob | working-branch blob | |
|---|---|---|---|
| `firestarter_fw/src/proms/flash_5v_page.cpp` | `11d5fef6` | `11d5fef6` | IDENTICAL |
| `firestarter_app/tools/build_db.py` | `57579767` | `57579767` | IDENTICAL |
| `firestarter_app/firestarter/data/chip_database.json` | `1977e171` | `1977e171` | IDENTICAL |
| `firestarter_app/tests/test_page_size_invariants.py` | `cd2b3628` | `cd2b3628` | IDENTICAL |
| `firestarter_app/tests/test_wire_dict_equivalence.py` | `f3ce8021` | `f3ce8021` | IDENTICAL |
| `firestarter_app/tests/golden/chip_database_field_inventory.json` | `78a6cda8` | `78a6cda8` | IDENTICAL |

CONTEXT.md's claim confirmed by content hash, not by diff inspection.

---

## R2 — The mask-vs-`%` implementation shape in `flash_5v_page.cpp`

### Correction: there are TWO `%` sites, not three

The research brief and CONTEXT.md both cite `flash_5v_page.cpp:82,92,100` as "the three `%` sites". `[VERIFIED: firestarter_fw/src/proms/flash_5v_page.cpp:82,92,100]` — verbatim:

```
 82	    uint32_t page_size = flash_5v_page_page_size(handle->mem_size);
 92	        bool is_page_start = (address % page_size) == 0;
100	        bool reached_page_end = ((address + 1) % page_size) == 0;
```

Line 82 is the **derivation call** (removed by D-06), not a modulo. There are exactly **two** `%`-by-variable-divisor sites: lines 92 and 100. `[VERIFIED: /usr/bin/grep -n "%" on the file returns only 92 and 100 in executable code]` Every other CONTEXT.md firmware citation verified correct: `:27-31` is `flash_5v_page_page_size`, its block comment is `:19-26`, `firestarter.h:186` is `uint16_t page_size`.

### The reference implementation, verbatim

`[VERIFIED: firestarter_fw/src/proms/eeprom_28c.cpp:28-29, 402-410, 412-418, 455]`

```c
#define AT28C_PAGE_SIZE_FALLBACK 64
#define AT28C_PAGE_SIZE_MAX 512
```

```c
static uint32_t eeprom28c_page_mask(uint16_t requested) {
    if (requested == 0) {
        return (uint32_t)AT28C_PAGE_SIZE_FALLBACK - 1;
    }
    if (requested <= AT28C_PAGE_SIZE_MAX && (requested & (requested - 1)) == 0) {
        return (uint32_t)requested - 1;
    }
    return (uint32_t)AT28C_PAGE_SIZE_FALLBACK - 1;
}
```

```c
    const uint32_t page_mask = eeprom28c_page_mask(handle->page_size);
```

```c
        bool page_end = ((address + 1) & page_mask) == 0;
```

**Citation correction:** CONTEXT.md's `<canonical_refs>` gives `eeprom_28c.cpp:392-410` for `eeprom28c_page_mask()`. The function body is `402-410`; `387-401` is its doc comment; the resolve-once site is `418`. The research brief's `392-418` spans comment + function + resolve site and is the more useful range.

### The mask form to adopt

Two sites, one mask, resolved once. The transformation is mechanical:

| Site | Now | Becomes |
|---|---|---|
| `:82` | `uint32_t page_size = flash_5v_page_page_size(handle->mem_size);` | resolve-or-refuse: `uint32_t page_mask; if (!flash_5v_page_mask(handle->page_size, &page_mask)) { LOG_ERROR_ID(<id>); handle->response_code = RESPONSE_CODE_ERROR; return; }` |
| `:92` | `bool is_page_start = (address % page_size) == 0;` | `bool is_page_start = (address & page_mask) == 0;` |
| `:100` | `bool reached_page_end = ((address + 1) % page_size) == 0;` | `bool reached_page_end = ((address + 1) & page_mask) == 0;` |

**Signature shape differs from `eeprom_28c` by necessity.** `eeprom28c_page_mask` returns a `uint32_t` mask because it always has one — it falls back. `flash_5v_page` must **refuse** (D-05), so it has no in-band value to return: a returned mask of `0` is indistinguishable from a legitimate 1-byte page, and `0xFFFFFFFF` is the dangerous direction `eeprom_28c`'s own comment warns about. Use an out-parameter with a `bool` success return (the shape measured below), or a sentinel the caller checks before use. **Do not reuse `eeprom28c_page_mask`'s return-a-mask contract on this path.**

### Resolve point: `operation_main`, confirmed for this file's actual control flow

`eeprom_28c.cpp:413-417`'s comment gives two reasons; both hold here, and a third applies:

1. **`write_init` returns early.** `[VERIFIED: firestarter_fw/src/proms/flash_5v_page.cpp:69-79]` — `flash_5v_page_write_init` returns on `handle->response_code == RESPONSE_CODE_ERROR` before doing anything else. A mask resolved there would be skipped on that path.
2. **The native suites drive `operation_main` directly.** `[VERIFIED: firestarter_fw/test/native/avr/test_val_5v_page/test_val_5v_page.cpp:263-292]` — both `write_execute` tests call `configure_memory(&h)` then `h.firestarter_operation_main(&h)`; `operation_init` is never called. A mask resolved in `write_init` would be structurally unobservable from the suite that is supposed to prove D-08.
3. **`operation_main` is called once per chunk, and `handle` is a file-scope global with a per-command reset.** `[VERIFIED: firestarter_fw/src/json_parser.c:271-280]` — `handle->page_size = 0` is reset per command, with the comment explaining why. Resolving in `operation_main` means every chunk re-validates against the value actually parsed for this command, with no cross-command carry.

**Therefore: resolve at the top of `flash_5v_page_write_execute`, replacing line 82. CONTEXT.md's instruction holds.**

### Validation shape and the ceiling

- **Reject `0` first, before the power-of-two test.** `(0 & (0 - 1)) == 0` is true on an unsigned type, so the power-of-two test alone admits zero. `eeprom_28c.cpp:391-396` documents exactly this. Copy the ordering.
- **Ceiling: 512, board-invariant.** The largest real page among the 27 is **512** (`AT29BV040,AT29LV040` and `AT29C040`) `[VERIFIED: §R1 table]`. So 512 is both necessary and sufficient. Use a board-invariant literal, **not** `DATA_BUFFER_SIZE` — that is 512 on Uno and 1024 on Leonardo `[VERIFIED: firestarter_fw/include/firestarter.h:16-17 gives the 512 default; the board differences are set per-env]`, which would make the validation rule differ by board for no reason. `eeprom_28c.cpp:24` states the same principle verbatim: "`AT28C_PAGE_SIZE_MAX` is a board-INVARIANT validation ceiling, deliberately".
- **Can an existing constant be reused? No — introduce a new one.** `AT28C_PAGE_SIZE_MAX` is a `#define` local to `eeprom_28c.cpp:29`, not in any header. `[VERIFIED: /usr/bin/grep -rn "AT28C_PAGE_SIZE" firestarter_fw/ → only eeprom_28c.cpp and three native test files' comments]`. Three options, in preference order:
  1. **Introduce `FLASH_5V_PAGE_SIZE_MAX 512` local to `flash_5v_page.cpp`.** Zero flash cost (a compile-time literal), zero coupling, and the two handlers stay independently readable. This is what the measurement below used. **Recommended.**
  2. Hoist a shared `PAGE_SIZE_VALIDATION_MAX` into `include/`. Cleaner in principle but couples two handlers whose ceilings happen to agree today for unrelated reasons (28C parts top out at 512; `0x05` parts top out at 512) — a future part in either family would force an unwanted decision.
  3. Reuse `AT28C_PAGE_SIZE_MAX` by including `eeprom_28c.cpp`'s define — not possible; it is in a `.cpp`.
- **A wire value above the type maximum is already handled.** `[VERIFIED: firestarter_fw/src/json_parser.c:108-110, 156, 230-253]` — `FIELD(key_page_size, page_size, 0)` uses `clamp == 0` ("no clamp", `:82`) with SATURATE width policy, so `store_field` saturates any value above `0xFFFF` to `0xFFFF` before it reaches the handler. 65535 is not a power of two, so the validator rejects it and D-05's refusal fires. Fail-closed holds end to end; no additional host-side bound is needed.

### The flash measurement — CONTEXT.md's hope is refuted

**Baseline, both envs `[VERIFIED: pio run, in-session]`:**

```
bootloader-guard: uno 21598/32256 B (67.0% of the safe ceiling, 10658 B margin, 512 B bootloader reserved)
bootloader-guard: leonardo 23716/28672 B (82.7% of the safe ceiling, 4956 B margin, 4096 B bootloader reserved)
```

The `leonardo` ceiling is **28672**, not 32768, exactly as the brief states — the guard applies it and reports against it.

**The division helpers are linked, and will stay linked.** `[VERIFIED: avr-nm --print-size -t x on .pio/build/uno/firestarter_uno.elf]`

| symbol | size |
|---|---|
| `__udivmodhi4` | `0x28` = 40 B |
| `__udivmodsi4` | `0x44` = 68 B |
| `__divmodsi4` | `0x2e` = 46 B |

**Total 154 B.** Callers, recovered from the linked disassembly because LTO erases per-object symbol references `[VERIFIED: avr-objdump -d, call/jmp target scan]`:

```
__udivmodsi4 <- eprom_check_vpp, flash_intel_write_init, flash_5v_page_write_execute,
                __divmodsi4, main, mem_util_delay_us, rurp_read_voltage_mv
__udivmodhi4 <- main, mem_util_report_voltage
__divmodsi4  <- main
```

**`flash_5v_page_write_execute` is one of seven callers of `__udivmodsi4`.** Removing its two `%` operations cannot unlink the helper.

**Measured before/after, full D-05/D-06 shape.** A reversible experiment applied the removal of `flash_5v_page_page_size()` and its block comment, a `FLASH_5V_PAGE_SIZE_MAX 512` define, a `flash_5v_page_mask(uint16_t, uint32_t*)` validator, the refusal branch (reusing the existing `MSG_ERR_FL4_VERIFY_TIMEOUT` id, so no new id cost), and both `&` substitutions. Both envs were rebuilt; the file was then restored to its exact original (`md5` re-verified, `git status --porcelain` empty) and the baseline builds reproduced byte-for-byte.

| env | before | after | delta | margin after |
|---|---|---|---|---|
| `uno` | 21598 B | 21604 B | **+6 B** | 10652 B of 32256 |
| `leonardo` | 23716 B | 23722 B | **+6 B** | 4950 B of 28672 |

After the change `__udivmodsi4` remains linked at `0x44`, with `flash_5v_page_write_execute` gone from its caller list and the other six intact. `[VERIFIED: avr-objdump -d, post-change scan]`

**Conclusion.** The mask-for-`%` swap is **flash-neutral-to-slightly-negative (+6 B)**, not a saving. CONTEXT.md's §Established Patterns hope — "Adopting the mask form may **free** flash rather than cost it — worth measuring, because it bears on whether D-09's INFO log could ever be funded" — is **refuted by measurement**. The swap frees no flash, and creates no headroom for D-09. That does not reopen D-09 (locked, out of scope); it removes the one stated premise on which a future phase might have expected it to be cheap.

The `%` avoidance is still worth doing: the call-site bytes, the hot-loop cycle cost of two 32-bit software divisions per byte, and consistency with the reviewed `eeprom_28c` pattern. Just do not sell it as a flash saving.

**Headroom verdict:** both envs have comfortable room. `uno` 10.6 KB, `leonardo` 4.95 KB. Nothing in this phase is flash-constrained.

---

## R3 — The refusal error id

### The firmware side costs no PROGMEM string

`[VERIFIED: firestarter_fw/include/messages.h — 177 lines, every one an id `#define`]`

```
#define MSG_ERR_FL4_VERIFY_TIMEOUT        0xB3
#define MSG_ERR_ENERGY_CAP                0xBE
```

`[VERIFIED: firestarter_fw/include/logging_id.h:28, 105]`

```c
#define LOG_ID(id) rurp_log_id((id), NULL, 0)
...
#define LOG_ERROR_ID(id)               LOG_ID(id)
```

A parameterless `id_frame` ERROR message carries **only its numeric id** on the wire. The format string lives in the host's generated `firestarter/messages.py`, never in the firmware. So a new id costs **one compile-time `#define` (0 B) plus the call site**. The "PROGMEM string against the Leonardo ceiling" cost is real for the legacy `LOG_*_MSG` text path and for `ascii_str` payloads — it is **not** a cost for the refusal id this phase needs.

### Is there an existing id to reuse? Recommendation: introduce one.

The full ERROR inventory `[VERIFIED: tools/catalog/messages.toml, in-session parse]` — 131 messages total, band `0xA0–0xBF` holds 31 of them:

```
ERROR band 0xA0-0xBF used: a0 a1 a2 a3 a4 a5 a6 a7 a8 a9 aa ab ac ad ae af
                           b0 b1 b2 b3 b4 b5 b6 b7 b8 b9 ba bb bc bd be
ERROR band FREE: ['0xbf']
```

**⚠ The ERROR band has exactly ONE free id left: `0xBF`.** The band `0xC0–0xDF` is entirely unused (32 ids) but no message occupies it today and severity is carried as an explicit field rather than derived from the id range `[VERIFIED: tools/catalog/codegen.py Rule 7 validates the severity string only; firestarter_app/firestarter/messages.py carries `severity=SEVERITY_*` per entry]`, so extending ERROR into `0xC0+` is *possible* but is a band-convention decision this phase should not make unilaterally. **Flag for the planner:** if `0xBF` is consumed here, the next error message anywhere in the project forces the band question.

Reuse candidates examined and rejected:

| Candidate | Verbatim format | Why not |
|---|---|---|
| `MSG_ERR_NOT_SUPPORTED` `0xA5` | `"Not supported"` | Says nothing about a page size; the host renders a bare three-word line with no diagnostic value on a silent-corruption defect. |
| `MSG_ERR_OUT_OF_RANGE` `0xA7` | `"Out of range"` | Parameterless and generic; already used elsewhere for address bounds. Collides in meaning. |
| `MSG_ERR_FL4_VERIFY_TIMEOUT` `0xB3` | `"Timeout verifying 0x%02x at 0x%06lx (got 0x%02x)"` | Same file, but the wording claims a verify timeout that did not happen, and its three params would be fabricated. Actively misleading. |
| `MSG_ERR_MEM_SIZE_TOO_SMALL` `0xBA` | `"Memory size %lu too small for chip-id check"` | Wrong field, wrong operation. |
| `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` `0xBB` | `"Protocol 0x%02x not implemented"` | Untrue — the protocol *is* implemented; the chip's page size is missing. Reusing this would send the operator down the firmware-upgrade path. |

**Recommendation: add one new id.** D-05 requires a *named* error and the whole point of the milestone (D-1: "never claims success over bytes it erased") is that the operator can tell what happened. A misleading reuse defeats that for 0 B of savings.

**Proposed name and stanza.** Follow the file's existing `MSG_ERR_FL4_*` prefix for this handler (`MSG_ERR_FL4_VERIFY_TIMEOUT`, `MSG_ERR_FL4_BOOT_BLOCK_LOCKED`):

```toml
[[messages]]
id          = 0xBF
name        = "MSG_ERR_FL4_PAGE_SIZE"
severity    = "ERROR"
format      = "No valid page size for this chip (%u) -- refusing to write"
params      = [{ type = "u16", render = "dec" }]
wire_format = "id_frame"
```

A `u16` param echoing the rejected value costs 2 wire bytes and makes the refusal diagnosable (0 = absent, 65535 = saturated, anything else = not a power of two in range). If the planner prefers zero params, use `params = []` and drop the `%u` — codegen Rule 9 enforces that the format-spec count matches the non-`bytes` param count.

**Insert position:** immediately after the `MSG_ERR_ENERGY_CAP` (`0xBE`) stanza, before the `# DATA (0xE0..0xEF)` banner. `[VERIFIED: tools/catalog/messages.toml, the `0xBE` stanza is the last ERROR entry and is followed directly by the DATA banner]` The file's own header states "DO NOT REORDER ENTRIES. Codegen sorts by id ascending; the source file order is preserved for human-edit diff readability."

### The exact commands, verbatim, run from the meta-repo root `/workspaces`

**1. Edit the canonical catalog — this file and no other:**

```
tools/catalog/messages.toml
```

`[VERIFIED: tools/catalog/messages.toml:1-8]` verbatim:

```
# Firestarter v1.2 log-message catalog (canonical source — meta-repo authoritative)
#
# DO NOT REORDER ENTRIES. Codegen sorts by id ascending; the source file order
# is preserved for human-edit diff readability.
#
# Distribution: copied byte-identically into firestarter/tools/catalog/ and
# firestarter_app/tools/catalog/ by tools/catalog/sync_to_subrepos.sh.
# Edit ONLY this meta-repo copy; run the sync script after every edit.
```

**2. Validate before generating (optional but cheap):**

```bash
python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check
```

**3. Regenerate and sync into both sub-repos — one command does both:**

```bash
bash tools/catalog/sync_to_subrepos.sh
```

`[VERIFIED: tools/catalog/sync_to_subrepos.sh]` — this script rewrites **exactly two files**:

| File rewritten | How |
|---|---|
| `firestarter_fw/include/messages.h` | `python3 codegen.py --catalog messages.toml --language cpp --target <tmp>` then `cp` |
| `firestarter_app/firestarter/messages.py` | `python3 codegen.py --catalog messages.toml --language python --target <tmp>`, `cp`, then `cd firestarter_app && ruff format -q firestarter/messages.py && ruff check -q --add-noqa firestarter/messages.py` |

**`ruff` must be on PATH** or the script prints `WARNING: ruff not found -- messages.py written WITHOUT normalization` and the committed file shows pure-formatting drift. `[VERIFIED: sync_to_subrepos.sh, the `command -v ruff` branch]`

**⚠ The two commands above are the whole of it. Do not hand-edit `firestarter_fw/include/messages.h` or `firestarter_app/firestarter/messages.py`.** Both are generated artefacts.

**Drifted citation to repair.** `.planning/todos/pending/runtime-info-log-naming-the-effective-page-size.md` names the edit point as "`firestarter/tools/catalog/messages.toml:1124`" and lists `firestarter/tools/catalog/messages.toml` in its `files:` frontmatter. **That path does not exist.** `[VERIFIED: ls firestarter_fw/tools/catalog/ → "No such file or directory"; ls firestarter_app/tools/catalog/ → only __pycache__]` The sub-repos carry **no** catalog copy — only the generated artefacts. The canonical path is `tools/catalog/messages.toml` in the meta repo. D-09 keeps that todo "pending, unmodified", so this phase should **not** edit it; record the drift in `194-SUMMARY.md` so a future phase that funds D-09 does not chase a dead path.

**Second drifted claim in the same todo:** it argues the INFO log's cost is "an entry in `messages.toml` plus a PROGMEM string". As measured above, an `id_frame` message has no firmware PROGMEM string. Noted for the record; again, do not edit the todo.

**No catalog drift gate exists in CI.** `[VERIFIED: /usr/bin/grep -rln "messages" over both sub-repos' .github/workflows/ → only a comment in firestarter_fw/.github/workflows/build.yml:114; the meta repo has no .github/workflows/ at all]` The todo's claim of "a CI drift gate against messages.toml" is not currently true. Running the sync script is a discipline obligation, not a CI-enforced one. **Planner: make the sync run an explicit task step with a `git status` check afterwards, because nothing will catch a forgotten sync.**

### The host-side half (D-07)

**The pattern to follow is `firestarter/flash4_erase_gate.py` — inverted.** `[VERIFIED: firestarter_app/firestarter/flash4_erase_gate.py:1-79]` It is already a protocol-`0x05`-specific, pre-connect, pure-predicate refusal module whose message names the chip:

```python
FLASH4_PROTOCOL_ID = 5

_REFUSAL_FORMAT = "Erase not supported for {chip_name}"
...
def is_flash4(programmer_data: Mapping[str, Any] | None) -> bool:
    if not programmer_data:
        return False
    return programmer_data.get("algorithm") == FLASH4_PROTOCOL_ID
...
def refusal_text(chip_name: str) -> str:
    return _REFUSAL_FORMAT.format(chip_name=chip_name.upper())
```

Its own docstring states the one thing that must be inverted here `[VERIFIED: flash4_erase_gate.py:22-29]`:

> "The one deliberate deviation from both of those precedents: this gate FAILS OPEN. `jp5_gate.require_acknowledged` and `sdp_capability` both refuse when their input cannot prove a part is safe [...] Absence of evidence is treated as 'not flash4' rather than as 'not provably safe'."

**D-05/D-07 require fail-CLOSED.** So follow `jp5_gate`'s two-layer structure instead, reusing `flash4_erase_gate`'s `FLASH4_PROTOCOL_ID` constant so the `0x05` predicate stays single-sourced.

**The two-layer shape, with exact insertion points:**

| Layer | File:line | What is there now | What to add |
|---|---|---|---|
| CLI pre-flight | `firestarter_app/firestarter/cli_handlers.py:758` | `if not jp5_gate.confirm_or_refuse(eprom, eprom_data.get("bus-config"), "write"): sys.exit(1)` | A sibling guard immediately before or after it. `eprom_data` is already the fully-resolved wire dict at this point and **no port has been opened** — `app.eprom_operator.write_eprom(...)` at `:761` is the first line that touches serial. |
| Operator-layer belt-and-braces | `firestarter_app/firestarter/eprom_operations.py:2002-2007` | `require_acknowledged(eprom_name, eprom_data_dict.get("bus-config"), "write", pin1_hazard_acknowledged)` | A sibling `require_page_size(...)` call. This sits immediately before `with self._operation_context(...)` at `:2009`, which is where the port opens. **This layer is the one that matters** — it also covers `dev test` and every non-CLI entry point, which the CLI layer does not. |

**The exception type.** Add a new class to `firestarter_app/firestarter/exceptions.py`. The model to copy is `ChipNotImplementedError` `[VERIFIED: exceptions.py:74-89]`, whose docstring already states the exact property D-07 wants:

> "The guard fires BEFORE any wire dict is built or serial byte emitted — the host will not drive hardware for a non-supported chip."

Subclass `EpromOperationError` (as `ChipNotImplementedError` does) so `cli_handlers.map_typed_errors` renders it. **⚠ Ordering matters:** `map_typed_errors` `[VERIFIED: cli_handlers.py:190-221]` catches `ChipNotImplementedError` at `:203` **before** the generic `EpromOperationError` arm at `:216` which would prefix the message with `"Programmer error: "`. A new subclass of `EpromOperationError` therefore needs **its own `except` arm placed above `:216`**, rendering `str(e)` verbatim, or the chip-naming message gets a generic prefix.

**Suggested name:** `PageSizeUnavailableError`. Message shape: `f"{chip_name.upper()}: no page size recorded for this chip — refusing a protocol 0x05 write"`. It names the chip, per D-07.

**Nothing in the wire path needs work.** `[VERIFIED: firestarter_app/firestarter/database.py:413-415 and :553-554]` — both the internal carry and the wire emit are algorithm-agnostic truthiness tests:

```python
        page_size_val = programming.get("page_size")
        if page_size_val:
            data["page_size"] = int(page_size_val)
```

```python
        if full_eprom_data.get("page_size"):
            programmer_data["page-size"] = full_eprom_data["page_size"]
```

CONTEXT.md's "no change is expected here" is correct. **Consequence worth stating for the plan:** the 25 newly-emitting rows will start sending `page-size` with **zero host code change** — which is precisely why `test_wire_dict_equivalence.py` will go RED (see §R4).

---

## R4 — The gates and goldens that move

Every hit below was found with `/usr/bin/grep` driven from a `bash` script (`/tmp/.../sweep.sh`), **never** the devcontainer's `grep`, which is ugrep and honours `.gitignore`. Scope: `firestarter_app/`, `firestarter_fw/`, `tools/`, `.github/`. Python-bytecode and `.pytest_cache` hits filtered.

**Verified starting state:** all five affected host modules are green on Python **3.11** today. `[VERIFIED: firestarter_app/.venv311/bin/python -m pytest tests/test_page_size_invariants.py tests/test_vcc_margin_rail.py tests/test_chip_database_field_inventory.py tests/test_wire_dict_equivalence.py tests/test_lock_status_class_partition.py -o addopts="" -q` → `44 passed in 3.27s`, interpreter `Python 3.11.16`.] The devcontainer default is 3.12; 3.11 is the app's CI floor and is what was used.

### Gate 1 — `tests/test_page_size_invariants.py` (CONTEXT.md named it)

The module has **11 legs**, not one. Only two move.

**Leg 4 `[VERIFIED: tests/test_page_size_invariants.py:237-246]` — the 20 → 45 change:**

```python
def test_exactly_20_page_size_carriers_across_all_746_rows() -> None:
    db = _load_db(_DB_FILE)
    total_rows = sum(len(chips) for chips in db.values())
    assert total_rows == 746, f"expected 746 total rows, found {total_rows}"
    carriers = _select_page_size_carriers(db)
    assert len(carriers) == 20, (
        f"expected exactly 20 page_size carriers (18 native + 2 curated) "
        f"across all 746 rows, found {len(carriers)}: "
        f"{[(m, c.get('part_number', '?')) for m, c in carriers]}"
    )
```

New assertion: `== 45`, with the parenthetical becoming `(18 0x0D-native + 27 0x05-native)`. Rename the function too — its name encodes the number. **Re-derivation, not a hand edit:** the 45 was independently produced this session by joining every row's own upstream `protocol_id` against minipro `a8efaedc` — §R1's `PROJECTED carriers under D-02 ... 45 (0x0D=18, 0x05=27)`. That derivation is reproducible with the §R1 script; cite it in the commit.

**Leg 6 `[VERIFIED: tests/test_page_size_invariants.py:265-272 and the identity sets at :69-108]` — the provenance allow-list grows from 20 identities to 45.** `_CURATED_PAGE_SIZE_IDENTITIES` (2 entries) is subsumed: both are `0x05`-native, so they arrive in the new 27-entry `0x05` set and the "curated" concept disappears with `_PAGE_SIZE_BY_PART`. The new shape is `_NATIVE_0X0D_PAGE_SIZE_IDENTITIES (18) | _NATIVE_0X05_PAGE_SIZE_IDENTITIES (27)`, and the 27 identities are already written down in-repo at `tests/test_lock_status_class_partition.py:296-327` (see §R1 corroboration 2 — same `MFG/part` shape, `/` separator vs this module's tuple, so a small adapter is needed).

**Legs that do NOT move:** 1 (84 `0x0D` rows), 2 (18 of 84, the named set), 3 (15 at 128 / 3 at 64), 5 (power of two in [1, 512] — verified to still hold for all 45), 7 (AT28C256 unchanged — it is a promoted `0x07` row and this phase cannot touch it), 8 (`support_status` byte-unchanged across the 84), 9 (`extra_chips.json` carries no `page_size`), 10 and 11 (the two synthetic non-vacuity legs — **keep both; they are what stop the new 45-identity allow-list from passing vacuously**).

**D-08's new host leg** — a 27-row table asserting (a) emitted `page_size == infoic_page_size_raw` for all 27, and (b) for the 18, that it also equals `64 if size<=65536 else 128 if size<=262144 else 256`. §R1's table is the oracle; the derivation function must be written out in the test, because D-06 deletes it from the firmware and there will be nothing left to compare against otherwise.

### Gate 2 — `tests/test_vcc_margin_rail.py:245-248` (CONTEXT.md named it)

`[VERIFIED: tests/test_vcc_margin_rail.py:231-248]` verbatim:

```python
def test_vcc_voltages_table_unedited_and_no_new_part_keyed_dict():
    """VCC_VOLTAGES[0x02] still decodes to 4000 -- the margin-rail
    substitution sits AFTER the decode table, never inside it (D-01). And
    _PAGE_SIZE_BY_PART still has exactly 2 entries -- no new
    part-number-keyed sibling dict was introduced (DATA-04)."""
    from tools import build_db

    assert build_db.VCC_VOLTAGES[0x02] == 4000, (
        "VCC_VOLTAGES[0x02] must still decode to 4000 -- the decode table "
        "itself must never be edited by the margin-rail substitution"
    )
    assert build_db._VCC_MARGIN_RAIL_MV == 4000, (
        "_VCC_MARGIN_RAIL_MV must be single-sourced from VCC_VOLTAGES[0x02]"
    )
    assert len(build_db._PAGE_SIZE_BY_PART) == 2, (
        "_PAGE_SIZE_BY_PART must still have exactly 2 entries -- the "
        "margin-rail rule must not introduce a new part-number-keyed dict"
    )
```

**What replaces the third assertion: assert ABSENCE, do not delete the leg.**

```python
    assert not hasattr(build_db, "_PAGE_SIZE_BY_PART"), (
        "build_db must carry no part-number-keyed page-size table -- the "
        "page size is generated from upstream provenance, never curated"
    )
```

Reasoning, for the plan:
- **Deleting the leg loses the guarantee.** The leg's stated purpose (its own docstring) is "no new part-number-keyed sibling dict was introduced". D-01 makes that stronger, not moot: the operator's framing is *"no curated rows, the build_db.py must reflect the ground truth from infoic"*. An absence assertion is the machine-checked form of exactly that instruction, and it is the thing that stops a future agent quietly reintroducing the table.
- **`hasattr` is the right predicate** because the name is a module-level global; after D-01 removes it, `len(build_db._PAGE_SIZE_BY_PART)` would raise `AttributeError` — a test *error*, not a clean assertion failure with a readable message.
- The other two assertions in the same function are untouched (`VCC_VOLTAGES[0x02] == 4000`, `_VCC_MARGIN_RAIL_MV == 4000`).
- The docstring's third sentence and the module header at `:31` (`_PAGE_SIZE_BY_PART` still has exactly 2 entries (no new...)`) both need rewording. **Note: this is a Python docstring, not a `#` comment**, so the citation gate does not scan it (see §Project Constraints) — but the no-comments rule in `CLAUDE.md` still means: reword the existing text, do not add new explanatory prose.

### Gate 3 — `tests/golden/chip_database_field_inventory.json` (CONTEXT.md named it, with a drifted line number)

**⚠ CITATION DRIFT.** CONTEXT.md's `<canonical_refs>` says "`tests/golden/chip_database_field_inventory.json:14` — records the count of 20". Line 14 is **prose that mentions** 20; the machine-read count is at **line 42**. `[VERIFIED: /usr/bin/grep -n "page_size" on the file]`

Three places in this file carry the number, and all three must move:

| Line | Kind | Current content |
|---|---|---|
| **42** | **the gate value** | `      "page_size": 20` (inside `levels.programming`) |
| 14 | prose (`meta.phase_149_update`) | `"...re-derived programming.page_size from 2 to 20 via the same independent traversal..."` |
| 9 | prose (`meta.why_counts_not_names`) | `"...page_size (2 of 746) and five sparse top-level keys..."` — the "(2 of 746)" illustration is already stale from Phase 149 and becomes doubly so |

**`how_to_update`, verbatim `[VERIFIED: tests/golden/chip_database_field_inventory.json:12]`:**

> "Re-derive every number in this file with an independent traversal of the live chip_database.json (two levels deep: {manufacturer: [chip, ...]}) -- never hand-edit a count to make a surprise disappear. State in the commit message which key changed, on which level, and why. If tools/build_db.py's chip_entry construction or tools/extra_chips.json changed, also re-derive generator_emitted_chip_entry_keys the same way (an ast walk over chip_entry plus a key scan of extra_chips.json) rather than editing the list by hand."

**The re-derivation command.** The gate that reads this golden is `tests/test_chip_database_field_inventory.py`, and it contains the traversal. The honest re-derivation is to run the module's own helpers against the regenerated DB:

```bash
cd /workspaces/firestarter_app && .venv311/bin/python - <<'PY'
import collections, json
from pathlib import Path
db = json.loads(Path("firestarter/data/chip_database.json").read_text(encoding="utf-8"))
top, prog, elec = collections.Counter(), collections.Counter(), collections.Counter()
for chips in db.values():
    for c in chips:
        top.update(c.keys())
        prog.update(c.get("programming", {}).keys())
        elec.update(c.get("electrical", {}).keys())
print("manufacturers", len(db), "chips", sum(len(v) for v in db.values()))
print("top", dict(top)); print("programming", dict(prog)); print("electrical", dict(elec))
PY
```

Then transcribe **every** number it prints into the golden — not just `page_size` — and name the changed key, its level and the reason in the commit message. `[VERIFIED: how_to_update, quoted above]` The expected `programming.page_size` value is **45**; `infoic_page_size_raw` stays **744**, and every other count stays put, but the instruction is to re-derive all of them rather than trust that.

**⚠ AST hazard for the same module.** `test_chip_database_field_inventory.py` has a sixth leg, `test_generator_emits_no_key_outside_the_frozen_inventory`, which **ast-walks `build_db.py`'s `chip_entry` construction**. `[VERIFIED: tests/test_chip_database_field_inventory.py:86, 194-258]` — `_collect_dict_keys` handles `ast.IfExp` branches specifically:

```python
            if isinstance(value_node, ast.IfExp):
                for branch in (...):
                    if isinstance(branch, ast.Dict):
```

The current emit arm is a **nested `IfExp` inside a `**{...}` unpacking** `[VERIFIED: firestarter_app/tools/build_db.py:707-715]`. If the planner restructures D-02's arm as a statement-level `if` writing `chip_entry["programming"]["page_size"] = ...` after the dict literal, the key path changes and this ast leg's behaviour changes with it — `_is_chip_entry_subscript_chain` (`:214-219`) does handle `chip_entry[...][...]` subscript assignment, so that shape is covered, but the two shapes are not interchangeable without checking. **Keep D-02's arm as an `IfExp` inside the same `**{...}` unpacking** and this leg is unaffected. State that constraint in the task.

### Gate 4 — `tests/test_wire_dict_equivalence.py` — NOT named by CONTEXT.md, and the largest change

This is the fourth-gate-nobody-named that the brief anticipated.

`test_live_capture_matches_golden_plus_the_149_and_153_and_182_deltas` captures a live wire dict for all 746 chips and asserts it equals a frozen golden plus three named delta layers `[VERIFIED: tests/test_wire_dict_equivalence.py:193-320]`:

```python
    expected = copy.deepcopy(recorded)
    for key, delta_wire in deltas_149.items():
        expected[key].update(delta_wire)
    for key, delta_wire in deltas_153.items():
        expected[key].update(delta_wire)
    for key, delta_wire in deltas_182.items():
        expected[key].update(delta_wire)

    live = _capture_wire_dicts(_REAL_DB)
    assert expected == live, (...)
```

Because `database.py`'s wire emit is algorithm-agnostic (§R3), the 25 rows that newly gain `programming.page_size` will newly emit a `page-size` wire key, and `expected == live` **fails on 25 records**.

**What must be authored: a fourth delta layer, `tests/golden/wire_dict_expected_deltas_194.json`.** `[VERIFIED: tests/golden/wire_dict_expected_deltas_149.json — top-level keys are `deltas` and `meta`; delta keys are `MFG|part_number|index`; values are `{"page-size": N}`; n = 18]` Sample, verbatim:

```json
{
 "ATMEL|AT28C010,AT28C010E|22": {
  "page-size": 128
 },
 "ATMEL|AT28C040,AT28C040E|25": {
  "page-size": 128
 }
}
```

**The 25 new deltas, derived in-session.** Exactly the 27 `algorithm: 5` rows minus the 2 that already carry `page-size`:

```json
{
  "ASD|AE29F1008|0": { "page-size": 128 },
  "ASD|AE29F2008|1": { "page-size": 128 },
  "ASD|AE29F4008|2": { "page-size": 256 },
  "ATMEL|AT29BV010A,AT29LV010A|39": { "page-size": 128 },
  "ATMEL|AT29BV020,AT29LV020|40": { "page-size": 256 },
  "ATMEL|AT29BV040,AT29LV040|41": { "page-size": 512 },
  "ATMEL|AT29BV040A,AT29LV040A|42": { "page-size": 256 },
  "ATMEL|AT29C010A|46": { "page-size": 128 },
  "ATMEL|AT29C020|47": { "page-size": 256 },
  "ATMEL|AT29C040|48": { "page-size": 512 },
  "ATMEL|AT29C040A|49": { "page-size": 256 },
  "ATMEL|AT29C256|43": { "page-size": 64 },
  "ATMEL|AT29C257|44": { "page-size": 64 },
  "ATMEL|AT29C512|45": { "page-size": 128 },
  "ATMEL|AT29LV256|50": { "page-size": 64 },
  "ATMEL|AT29LV512|51": { "page-size": 128 },
  "SST|SST29EE010|10": { "page-size": 128 },
  "SST|SST29EE020|11": { "page-size": 128 },
  "SST|SST29EE512|12": { "page-size": 128 },
  "SST|SST29LE010,SST29VE010|13": { "page-size": 128 },
  "SST|SST29LE020,SST29VE020|14": { "page-size": 128 },
  "SST|SST29LE512,SST29VE512|15": { "page-size": 128 },
  "WINBOND|W29C010,W29C011,W29C011A,W29EE010,W29EE012|6": { "page-size": 128 },
  "WINBOND|W29C512,W29EE512|9": { "page-size": 128 },
  "WINBOND|W29EE011|10": { "page-size": 128 }
}
```

`[VERIFIED: derived in-session from firestarter_app/firestarter/data/chip_database.json by enumerating each manufacturer's chip list with its positional index]` **⚠ The trailing integer is the chip's position in its manufacturer's array and is the fragile part — re-derive it against the regenerated database rather than copying these, in case row order shifts.** The count must be 25, and each value must equal that row's `infoic_page_size_raw`.

**Four further edits inside the same test, all in `test_live_capture_matches_golden_plus_the_149_and_153_and_182_deltas`:**

1. **Rename the test** — its name enumerates the layers.
2. **Add the non-vacuity pair for the new layer**, mirroring `(b)` at `:216-226`: every 194 delta key must exist in the golden, and the golden's record for it must NOT already carry `page-size`. This is what catches a delta naming a row that already had the value — and it is the leg that would have caught `W29C020`/`W29C040` being wrongly included.
3. **Add the exact-count guard**, mirroring `(c)` at `:228-234`: `assert len(deltas_194) == 25`. **Equality, never a floor** — the existing comment at `:228-230` says so explicitly: "not 'at least' -- the 149 layer's own exact-count guard; must stay an equality, not a floor, even now that a second layer exists alongside it."
4. **Extend `layer_pairs` at `:280-284` to six pairs.** `[VERIFIED: tests/test_wire_dict_equivalence.py:280-298]` — the field-disjointness check is what makes `dict.update` composition order-independent. **⚠ 194 × 149 is the dangerous pair:** both layers carry the field `page-size`. They must be **key-disjoint** (194 touches `0x05` rows, 149 touches `0x0D` rows — verified disjoint by §R1's provenance split), because the existing check only flags a collision when the layers share a *key* **and** a *field*. Add the pair and let the check prove it.

**What does NOT move in this module:**
- `_GOLDEN_PAGE_SIZE_RECORD_KEYS` / the leg at `:201-211`. It asserts a property of the **frozen golden**, not of the live DB — "the golden's own page-size-carrying record set drifted from Phase 148's original two". The golden is never re-captured (D-17). Leave it.
- `test_wire_key_union_is_exactly_nine_keys` (`:326+`). `page-size` is already one of the nine, since two rows carry it today.

### Gate 5 — `firestarter_fw/test/native/avr/test_val_5v_page/test_val_5v_page.cpp` — NOT named by CONTEXT.md, and it is in a CI-run leg

**Two existing, currently-green test cases drive `flash_5v_page_write_execute` with `page_size` left at zero and will turn RED the moment D-05's refusal lands.**

`[VERIFIED: test_val_5v_page.cpp:185-199]` — the shared fixture, verbatim:

```c
static firestarter_handle_t make_write_handle_with_data(void) {
    firestarter_handle_t h = {};
    h.protocol   = 0x05;
    h.cmd        = CMD_WRITE;
    h.response_code = RESPONSE_CODE_OK;
    h.chip_id    = 0; /* skip chip-id branch in write_init */
    h.mem_size   = 524288; /* 512 KB (W29C040) */
    h.address    = 0;
    h.data_size  = 4; /* small: 4 zero bytes at page 0; poll passes immediately */
    ...
}
```

`h.page_size` is never set, so `{}` zero-initialises it. Both consumers assert `RESPONSE_CODE_OK`:

- `test_5v_page_write_execute_emits_sdp` `[VERIFIED: :263-274]` — `TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_OK, h.response_code, "flash_5v_page_write_execute must not error on 4-byte zero write")`
- `test_5v_page_write_execute_no_vpp` `[VERIFIED: :281-292]` — same assertion

**Fix:** set `h.page_size = 256;` in `make_write_handle_with_data()` (256 is `W29C040`'s real page and is what the fixture's `mem_size = 524288` comment already claims to model). One edit, both cases green.

**This suite runs in CI.** `[VERIFIED: firestarter_fw/.github/workflows/build.yml:124, 137, 143]` — the firmware CI legs are `pio test -e native`, `pio test -e native_nodevtools`, and `pytest tests/ -v`. `[VERIFIED: firestarter_fw/platformio.ini:97]` — `native/avr/test_val_5v_page` is in `[native_base] test_filter`, inherited by both native envs. **Current state 15/15 green** `[VERIFIED: pio test -e native -f "*test_val_5v_page*"` → `15 test cases: 15 succeeded in 00:00:06.246`].

### Complete sweep results — everything else, and why it does not move

`[VERIFIED: /usr/bin/grep -rln -E "page_size|page-size|PAGE_SIZE" over firestarter_app/{tests,tools}, firestarter_fw/{tests,test,scripts,include,src}, tools/, .github/]`

| File | Verdict |
|---|---|
| `firestarter_app/tools/build_db.py` | **MOVES** — D-01/D-02/D-03. Lines 96-115 (delete), 435-440 (comment naming `0x0D` becomes false), 697-715 (emit arm). |
| `firestarter_app/firestarter/data/chip_database.json` | **MOVES** — regenerated, never hand-edited. 25 rows gain `programming.page_size`. |
| `firestarter_app/tests/test_page_size_invariants.py` | **MOVES** — Gate 1. |
| `firestarter_app/tests/test_vcc_margin_rail.py` | **MOVES** — Gate 2 (`:31` docstring, `:231-248`). |
| `firestarter_app/tests/golden/chip_database_field_inventory.json` | **MOVES** — Gate 3 (`:42` value, `:9` and `:14` prose). |
| `firestarter_app/tests/test_chip_database_field_inventory.py` | **DOES NOT MOVE**, but see the AST hazard above — it reads the golden and ast-walks `build_db.py`. |
| `firestarter_app/tests/test_wire_dict_equivalence.py` | **MOVES** — Gate 4, plus a new `wire_dict_expected_deltas_194.json`. |
| `firestarter_app/tests/golden/wire_dict_baseline.json` | **MUST NOT MOVE** — D-17 forbids re-capture. Add a delta layer instead. |
| `firestarter_app/tests/golden/wire_dict_expected_deltas_149.json` | **MUST NOT MOVE** — its 18 are `0x0D` rows; key-disjoint from the new 25. |
| `firestarter_fw/test/.../test_val_5v_page.cpp` | **MOVES** — Gate 5, two cases plus the new D-08 boundary test. |
| `firestarter_app/firestarter/database.py:401-415, 545-554` | Logic unchanged. **Comments at `:403-409` and `:545-552` become factually false** — both say "algorithm 13 / 0x0D only" and "other algorithms' handlers never consume this key". See §Unresolved. |
| `firestarter_app/firestarter/constants.py:140-148` | Same — `"provenance-keyed for upstream-native 0x0D rows"` and `"algorithm 13 / 0x0D only"` become false. See §Unresolved. |
| `firestarter_fw/src/json_parser.c:150-155` | Comment says validation "still live[s] in the 0x0D handler (eeprom28c_page_mask)". Becomes incomplete — a second handler will validate. Same question. |
| `firestarter_fw/include/firestarter.h:186-189` | Comment says `"0 = absent, so the 0x0D handler applies its own named fallback floor"`. Becomes incomplete. Same question. |
| `firestarter_app/tests/test_lock_status_class_partition.py:296-327` | **DOES NOT MOVE.** Pins the 27 `0x05` identities and asserts the live population against them; `page_size` is not in scope. Reuse the frozenset, do not relocate it. |
| `firestarter_app/tests/test_b15_page_size_corroboration.py` | **DOES NOT MOVE.** Compares `protect_on_after` against `infoic_page_size_raw > 1` over the 84 `0x0D` rows. D-04 leaves `infoic_page_size_raw` untouched. |
| `firestarter_app/tests/test_erase_flag_invariants.py:212-241` | **DOES NOT MOVE.** Asserts algorithm-5 rows never carry the erase capability bit. Orthogonal, and must stay green. |
| `firestarter_app/tests/test_protect_flags_doc_measurements.py` | **DOES NOT MOVE.** Mentions `page_size` only by analogy in its header. |
| `firestarter_app/tools/validation_matrix_spec.json:74-76` | **DOES NOT MOVE.** Names `configure_flash_5v_page` as the handler; the handler name is unchanged. |
| `firestarter_fw/src/proms/eeprom_28c.cpp` | **MUST NOT MOVE.** The `0x0D` rule is explicitly out of scope (D-02). Used as reference only. |
| `firestarter_fw/test/.../test_read_timing_params.cpp:136-419` | **DOES NOT MOVE.** `page-size` **parse** tests; the wire key and its FIELD row are unchanged. |
| `firestarter_fw/test/.../test_val_eeprom28c.cpp`, `test_eeprom28c_sdp.cpp` | **DO NOT MOVE.** `AT28C_PAGE_SIZE_*` consumers on the `0x0D` path. |
| `firestarter_fw/tests/test_flash_geometry_recorded_before_linker.py`, `test_py32_flash_map.py`, `test_flash_path_record_sync.py` | **DO NOT MOVE.** "page size" here means MCU **flash** page geometry, an unrelated sense of the word. |
| `firestarter_fw/tests/fixtures/merge05_*.log` | **DO NOT MOVE.** Frozen build-log fixtures that merely list `flash_5v_page.cpp.o` as compiled. |
| `firestarter_fw/scripts/check_cmake_manifest.py`, `check_erase_no_vpp.py` | **DO NOT MOVE**, but both name `flash_5v_page.cpp`. `check_erase_no_vpp.py:28` asserts the file writes "no control-register bit at all" — the change adds no register write, so it stays green. **`check_cmake_manifest.py` should be re-run after any file-level change**, per the memory that an ARM-only TU rename dies at the manifest gate first. |
| `tools/catalog/messages.toml` | **MOVES** — §R3. |
| `firestarter_fw/include/messages.h`, `firestarter_app/firestarter/messages.py` | **MOVE, but only via `sync_to_subrepos.sh`.** Never hand-edited. |

**No watermark gate was found that pins a `page_size` carrier count.** The `mypy` watermark (`firestarter/ tests/`, py3.11) does not scope `tools/`, so `build_db.py` is outside it — and outside `ruff check`/`ruff format` too, which cover `firestarter/ tests/` only `[VERIFIED: firestarter_app/.github/workflows/ci.yml:70-74]`. `size_baseline.json`'s `compare_native` case/suite-count assertion was retired 2026-09-13 `[CITED: firestarter_fw/CLAUDE.md §"Reuse pattern for future native tests"]`, so adding a native suite no longer trips it.

---

## R5 — The native firmware consumption test (D-08's second half)

### Which test tree, and what CI actually runs

`firestarter_fw` has **two** test trees, and the distinction matters:

| Tree | Nature | Runs in CI? |
|---|---|---|
| `test/native/avr/<suite>/` | PlatformIO **Unity C++** suites, cross-compiled against host libc + ArduinoFake | **Yes** — `pio test -e native` and `pio test -e native_nodevtools` |
| `tests/*.py` | Python **source-scanner / record-sync** suite, 31 modules | **Yes** — `pytest tests/ -v` |

`[VERIFIED: firestarter_fw/.github/workflows/build.yml:99, 124, 137, 143, 175]` — the CI legs in order are: `python3 tools/planning_citation_gate.py src include test tests scripts platform tools name_firmware.py zero_bootloader_reserve.py bootloader_guard.py`, `pio test -e native`, `pio test -e native_nodevtools`, `pip install pytest`, `pytest tests/ -v`, `pio run`.

**D-08's firmware test belongs in `test/native/avr/`**, because it must *execute* `flash_5v_page_write_execute` and observe its side effects — a Python source-scanner cannot do that.

### The closest existing analog: extend it, do not create a new suite

**`firestarter_fw/test/native/avr/test_val_5v_page/`** is the harness to use. It already:

- drives `flash_5v_page_write_execute` through the dispatched pointer (`configure_memory(&h)` then `h.firestarter_operation_main(&h)`) `[VERIFIED: :263-292]`
- activates the recording bus with a one-line opt-in `[VERIFIED: test_val_5v_page/host_stubs.cpp:22-24]`:

```c
/* Activate recording bus stub (opt-IN). No other overrides needed. */
#define HOST_STUBS_RECORD_BUS

#include "../_shared/host_stubs_common.inc"
```

- carries a page-start oracle already: `recording_contains_sdp_signature()` `[VERIFIED: :240-258]` scans the recording for the `FLASH_ENABLE_WRITE` MSB pattern `{0x55, 0x2A, 0x55}` — and `flash_execute_command(FLASH_ENABLE_WRITE)` is emitted **exactly once per page start** `[VERIFIED: firestarter_fw/src/proms/flash_5v_page.cpp:92-96]`. Counting SDP signatures and recording their positions gives page starts directly.
- is registered in **both** native envs (`test_filter` at `platformio.ini:97`, `-I` at `:122`), so no `platformio.ini` change is needed. This is the exception to the "a new suite needs four new lines in two envs" rule in `firestarter_fw/CLAUDE.md` — by extending an existing registered suite, there is nothing to register.

**`flash_5v_page_write_execute` is reachable from a native suite today. No `host_stubs` addition is required.** That answers the brief's last R5 question directly: zero.

### ⚠ The measured vacuity hazard, and it is decisive

`[VERIFIED: firestarter_fw/test/native/avr/_shared/host_stubs_common.inc:168-189]` verbatim:

```c
#elif defined(HOST_STUBS_RECORD_BUS)
#define HOST_STUBS_MAX_RECORDING 256

struct bus_record_entry_t {
    uint8_t reg;
    uint8_t data;
};
static bus_record_entry_t s_bus_recording[HOST_STUBS_MAX_RECORDING];
static int s_bus_recording_count = 0;
...
extern "C" void rurp_write_to_register(uint8_t reg, rurp_register_t data) {
    if (s_bus_recording_count < HOST_STUBS_MAX_RECORDING) {
        s_bus_recording[s_bus_recording_count].reg  = reg;
        s_bus_recording[s_bus_recording_count].data = (uint8_t)data;
        s_bus_recording_count++;
    }
}
```

Two properties: the cap is **256**, defined **unconditionally** (no `#ifndef`, so a suite cannot raise it without editing the shared `.inc`), and overflow is **silently dropped** — no flag, no assert, no saturation signal.

**Measured density.** A reversible probe drove `flash_5v_page_write_execute` at increasing `data_size` and read `bus_recording_count()` back through a forced assertion. `[VERIFIED: pio test -e native -f "*test_val_5v_page*"`, output verbatim]:

```
test_probe_ds4:   Expected -1 Was 23   [FAILED]
test_probe_ds16:  Expected -1 Was 59   [FAILED]
test_probe_ds64:  Expected -1 Was 203  [FAILED]
test_probe_ds256: Expected -1 Was 256  [FAILED]
test_probe_ds512: Expected -1 Was 256  [FAILED]
```

(The probe was then removed and the file restored; `md5sum` matches the pre-probe copy and `git status --porcelain` is empty.)

The density is **exactly 3 records per written byte, plus 11 for the SDP prefix** — `11 + 64*3 = 203` ✅, `11 + 16*3 = 59` ✅, `11 + 4*3 = 23` ✅.

**Therefore the buffer saturates at ~81 bytes of data** (`11 + 81*3 = 254`), and `data_size = 256` and `512` both report exactly `256` — saturated. **A multi-page boundary assertion over any real page size in the set (64…512) is VACUOUS today past byte ~81.** A test that counted SDP signatures over a 512-byte write would see only the first page's and silently pass whatever the page size was.

**This must be fixed before the D-08 firmware test is written, or the test proves nothing.** Concretely:

1. Make the cap overridable: `#ifndef HOST_STUBS_MAX_RECORDING` / `#define HOST_STUBS_MAX_RECORDING 4096` / `#endif`, so a suite can raise it and existing suites are byte-unchanged at the default. At 2 B/entry, 4096 entries is 8 KB of host RAM — irrelevant on a native build, and the `.inc` compiles into no production target (`build_src_filter = +<proms/> ...` excludes `test/`, `[VERIFIED: platformio.ini:107]`).
2. **Add a saturation signal** — `extern "C" bool bus_recording_saturated()` returning `s_bus_recording_count >= HOST_STUBS_MAX_RECORDING`, and assert `!bus_recording_saturated()` in every new boundary case. This is what makes non-vacuity *checkable* rather than *argued*. Without it, a future page-size increase silently re-vacuums the test.
3. Sizing: the largest single call is `data_size = 512` (see the `DATA_BUFFER_SIZE` constraint below) → `11 + 512*3 ≈ 1547` records, and a two-call sequence for the 512-byte-page case → ~3100. **4096 is the right default.**

### ⚠ `DATA_BUFFER_SIZE` caps one call at 512 bytes

`[VERIFIED: firestarter_fw/include/firestarter.h:16-17, 190]`

```c
#ifndef DATA_BUFFER_SIZE
#define DATA_BUFFER_SIZE 512
```
```c
    char data_buffer[DATA_BUFFER_SIZE];
```

On the native build `DATA_BUFFER_SIZE` is the 512 default. So a **512-byte page cannot be exercised as a multi-page write in one `write_execute` call** — `data_size` cannot exceed the buffer. **Do not raise `DATA_BUFFER_SIZE` for the suite**; it is a struct member and changing it changes `firestarter_handle_t`'s layout, which `json_parser.c`'s compiler-derived `offsetof`/`sizeof` FIELD rows and its `_Static_assert` layout guards depend on `[VERIFIED: firestarter_fw/src/json_parser.c:99-110, 159-161]`.

**Instead, drive `write_execute` repeatedly with an advancing `handle->address`, which is what the real chunked path does.** `[CITED: CONTEXT.md §Integration Points]` — "The host chunk size is `firmware_max_chunk` = `DATA_BUFFER_SIZE` exactly (512 Uno / 1024 Leonardo, `eprom_operations.py:416-429`)". For a 512-byte page: call 1 at `address = 0` with `data_size = 512` (exactly one page), call 2 at `address = 512`. Page-start detection on call 2 evaluates `512 & 511 == 0` → true, so the boundary is observable. This is also the faithful model of production behaviour.

### The other two measured blind spots, and how to design around each

**1. Register-write elision is NOT modelled under `HOST_STUBS_RECORD_BUS`.** `[VERIFIED: host_stubs_common.inc:44-63, 69-74]` — the shared file documents an opt-in, `HOST_STUBS_REAL_REGISTER_UTILS`, whose purpose is verbatim:

> "(b) Why: it exists so a suite can additionally `#include "rurp_register_utils.h"` (AFTER this file) and drive production's real cache-compare elision + latch-strobe sequencing directly, instead of a hand-maintained replica that can silently drift from `rurp_write_to_register` / `rurp_internal_write_to_register`."

`test_val_5v_page/host_stubs.cpp` defines only `HOST_STUBS_RECORD_BUS`, so it gets the **replica** stub, which performs no elision. Consequence: the recording contains register writes production would elide, so the **record count is not production-faithful**.

**How to make this not matter:** key the oracle on the **SDP signature sequence**, not on a record count or a per-byte register pattern. `flash_execute_command(FLASH_ENABLE_WRITE)` is a *deliberate, non-elidable* three-address command sequence (the addresses `0x5555 / 0x2AAA / 0x5555` differ from each other and from the data addresses, so no cache-compare can elide the MSB writes that `recording_contains_sdp_signature()` keys on). Count SDP occurrences and note the data-address write index at which each occurs. That oracle is invariant under elision. **Do not assert a record count.** `[VERIFIED: host_stubs_common.inc:63 — "(e) No existing suite may define this flag -- flag off is byte-exact"]`, so do not switch this suite to `HOST_STUBS_REAL_REGISTER_UTILS` either; that flag also redefines six symbols and pulls in `HOST_STUBS_CUSTOM_DATA_BUFFER`, changing the existing 15 green cases.

**2. The stubs record NO time; `delay()` is unstubbed.** A trace diff cannot prove timing, and the brief states this. It does not bite here, because **D-08's oracle is addresses, not time** — page-start and page-commit *positions*, which are pure arithmetic on `address & page_mask`. Two practical notes:
- `flash_5v_page_wait_for_page_write` `[VERIFIED: flash_5v_page.cpp:110-132]` polls up to 1024 times with `delayMicroseconds(10)` and exits on the first match. Keep `data_buffer` all-zero: the shared stub's `rurp_read_data_buffer()` returns 0 `[VERIFIED: host_stubs_common.inc:223]`, so the poll converges on iteration 1. A non-zero buffer never converges and the test becomes a 512 × 1024-iteration crawl before failing.
- Do **not** assert anything about elapsed time, `delayMicroseconds` call counts, or ordering-in-time. Assert only on the recorded address/register stream.

**3. A matching-id golden trace can miss a WARN/ERROR fork — so the refusal needs its own MISMATCH test.** The refusal path emits an ERROR id and sets `RESPONSE_CODE_ERROR`; a test that only checked "the expected ids appear" would pass whether or not the refusal fired. Author the refusal cases as **explicit negative assertions**, at minimum four:

| Case | `h.page_size` | Must assert |
|---|---|---|
| absent | `0` | `h.response_code == RESPONSE_CODE_ERROR` **and** `bus_recording_count() == 0` after `clear_bus_recording()` — zero writes, no partial page load |
| not a power of two | `96` | same |
| above the ceiling | `1024` | same |
| saturated wire value | `65535` | same |

**`bus_recording_count() == 0` is the load-bearing half** — "refuses" without "performs no write" is not D-05. Add a positive control in the same block (`page_size = 128`, same handle otherwise) asserting `RESPONSE_CODE_OK` and a non-zero recording, so the negative cases cannot pass because the harness is broken.

### The 27 pairs collapse to 7 distinct cases

`[VERIFIED: in-session enumeration of the 27 rows' `(size_bytes, infoic_page_size_raw)`]`:

```
distinct (mem_size, real_page) pairs among the 27: [(32768, 64), (65536, 128), (131072, 128),
  (262144, 128), (262144, 256), (524288, 256), (524288, 512)] -> 7 distinct
pairs where real != derived: [(65536, 128, 64), (262144, 256, 128), (524288, 512, 256)]
```

D-08 asks for 27 pairs; **7 distinct values cover them exhaustively**, and 3 of the 7 are the cases where the old derivation was wrong. A table-driven Unity case over the 7 pairs is the honest and complete form. **Say so in the test's own docstring-equivalent** — and since firmware comments are forbidden and the citation gate scans `test/`, record the 27→7 collapse in `194-SUMMARY.md` and in the 27-row record artefact, not in the `.cpp`.

**Note on `mem_size`:** after D-06, `flash_5v_page_write_execute` reads `handle->page_size` and never `handle->mem_size` for page arithmetic. So the 7 pairs' `mem_size` component becomes **decorative** for the boundary oracle — which is itself a finding worth asserting: a case with the *right* `page_size` and a *deliberately wrong* `mem_size` must still produce the right boundaries. Include one such case; it is the cheapest possible proof that PAGE-01 is actually satisfied and the derivation is truly gone.

---

## Integration Points (unchanged, and tested)

```
build_db.py emit arm  →  regenerated chip_database.json  →  database.py _map_data (:413-415)
  →  convert_to_programmer (:553-554)  →  wire "page-size"  →  json_parser.c FIELD row (:156)
  →  handle->page_size (firestarter.h:186)  →  flash_5v_page_write_execute
```

Every link but the first and last already exists and is exercised. `[VERIFIED: the citations above]` The consequence, stated plainly for the plan: **the host already sends `page-size: 128` on every `w29c020` write today, and `flash_5v_page.cpp` throws it away.** This phase is two small seams, not a new transport.

---

## Project Constraints (from CLAUDE.md and the citation gates)

### The no-comments hard rule

`[VERIFIED: /workspaces/CLAUDE.md §"Source code comments — hard rule"; /workspaces/firestarter_fw/CLAUDE.md §same; /workspaces/firestarter_app/CLAUDE.md:5]`

- **Write no comments into product source** under `firestarter_fw/` or `firestarter_app/`. Not overridable by a plan, task, skill or subagent instruction.
- Planners: **do not** write "add a comment citing X" into a plan, and **do not** make "a comment exists" an acceptance criterion.
- D-06 already applies this: `flash_5v_page_page_size()`'s block comment (`:19-26`) is removed with the function and **no replacement comment is written**.
- Rationale goes in `194-SUMMARY.md`, `.planning/REQUIREMENTS.md` traceability, or the commit message.
- **Click docstrings are user-facing `--help` text**, not comments — do not treat them as such.

### The planning-citation gates (both repos, both in CI)

`[VERIFIED: firestarter_app/tools/planning_citation_gate.py:53-77; firestarter_app/.github/workflows/ci.yml:67-68; firestarter_fw/.github/workflows/build.yml:99]`

Forbidden patterns, verbatim from the source:

```python
RULES = (
    ("planning-path", re.compile(r"\.planning\b")),
    ("gsd-artifact", re.compile(... r"|\b(?:ROADMAP|REQUIREMENTS|STATE|PROJECT|BACKLOG)\.md\b")),
    ("phase-or-plan-ref", re.compile(r"\b[Pp]hases?\s+\d{2,3}\b" ...)),
    ("decision-id", re.compile(r"(?<![A-Za-z0-9_])(?:D|C|F|L|S|OD|WR|LOCK)-\d{1,2}(?![0-9A-Za-z_])")),
    ("requirement-id", re.compile(r"(?<![A-Za-z0-9_-])[A-Z]{2,12}-\d{2}(?![0-9A-Za-z_])")),
)
```

Scope: app = `firestarter tests tools`; firmware = `src include test tests scripts platform tools name_firmware.py zero_bootloader_reserve.py bootloader_guard.py`. Both currently green (app: `OK: 140 files scanned, no planning citations.`).

**Critical scope detail `[VERIFIED: tools/planning_citation_gate.py:14-15]`:**

> "bytes, can never read as a comment. Python docstrings are string expressions, not comments, and are never scanned: Click command docstrings are the user's"

So: **`Phase 194`, `PAGE-01`, `D-02` may appear in a Python docstring** (which is how `test_page_size_invariants.py:1` legitimately says "Phase 149 Plan 03 (PGSZ-01 / D-07)"). They may **not** appear in a Python `#` comment, and may not appear in **any** C/C++ comment — where the no-comments rule forbids the comment outright anyway.

### Other standing constraints honoured by this research

- `chip_database.json` is **GENERATED**. Never hand-edited. Fix `build_db.py` and regenerate.
- The generator may not invent a field with no infoic proof. D-02's rule reads `raw_page_size` from the record's own attribute, so this holds.
- `build_db.py` lives in `tools/`, which is **outside** `ruff check`, `ruff format --check` and the `mypy` watermark `[VERIFIED: firestarter_app/.github/workflows/ci.yml:70-74 scopes `firestarter/ tests/`]` — but **inside** the citation gate. A `build_db.py` edit will not be lint-checked; hold it to the same standard by hand.
- App CI floor is Python **3.11** `[VERIFIED: firestarter_app/.github/workflows/ci.yml:50-53]`; coverage gate `--cov-fail-under=70` `[VERIFIED: :77]`. Use `firestarter_app/.venv311/bin/python` (3.11.16, present and working) rather than the devcontainer default 3.12.
- Firmware archaeology compares against `origin/beta`, not `main`. Done — §R1.

---

## ⚠ Wave-0 prerequisite: the sub-repos are on the WRONG branch

`[VERIFIED: git status -sb in both sub-repos]`

| Repo | Current branch |
|---|---|
| `/workspaces` (meta) | `v1.39-protocol-0x05-write-correctness` ✅ |
| `firestarter_fw` | `v1.38-repository-rename` ❌ |
| `firestarter_app` | `v1.38-repository-rename` ❌ |

The standing project rule is to fork a `v1.X-slug` branch off `beta` in **all three** repositories and never work on `beta` or `main`. Both sub-repos still sit on the previous milestone's branch. **The plan's first task must create the `v1.39-*` branches in both sub-repos off `origin/beta`**, before any code edit. `firestarter_fw` HEAD is `e6888a9` with a clean tree; `firestarter_app` likewise clean.

Related: the gitlink has been advanced per-phase since v1.36, superseding the older leave-it-alone rule — expect to advance it in the meta repo as part of this phase's commits.

---

## Suggested task sequence (dependency-ordered)

| # | Task | Why this position |
|---|---|---|
| 1 | Fork `v1.39-*` branches in both sub-repos off `origin/beta` | Nothing may be committed to `v1.38-repository-rename`. |
| 2 | `host_stubs_common.inc`: `#ifndef`-guard `HOST_STUBS_MAX_RECORDING`, default 4096, add `bus_recording_saturated()` | **Must precede task 8** or the D-08 firmware test is vacuous. Byte-neutral for existing suites at the default. Verify all native suites still green. |
| 3 | `build_db.py`: D-01 (delete `_PAGE_SIZE_BY_PART` + its arm), D-02 (extend provenance to `0x05`), D-03 (fail-closed emit assertion). Keep the arm as an `IfExp` in the `**{...}` unpacking. | Upstream of everything data-shaped. |
| 4 | Regenerate `chip_database.json` (network egress to gitlab.com required). Verify 45 carriers, 25 changed rows, no other field moved. | Depends on 3. |
| 5 | Host gates: `test_page_size_invariants.py` legs 4 + 6 + the new 27-row D-08 leg; `test_vcc_margin_rail.py` absence assertion; `chip_database_field_inventory.json` re-derived per its own `how_to_update` | Depends on 4. |
| 6 | New `wire_dict_expected_deltas_194.json` (25 entries, indices re-derived) + the four edits inside `test_wire_dict_equivalence.py` | Depends on 4. The largest single gate change. |
| 7 | Catalog: add `MSG_ERR_FL4_PAGE_SIZE` at `0xBF`; run `bash tools/catalog/sync_to_subrepos.sh`; commit the two regenerated artefacts | Needed by 8 and 9. No CI gate catches a forgotten sync. |
| 8 | `flash_5v_page.cpp`: D-06 removal, the validator + ceiling, the refusal, both `&` substitutions. Fix `make_write_handle_with_data()` to set `page_size`. Build both envs and record the delta against 21598 / 23716. | Depends on 2 and 7. |
| 9 | New native cases: the 7 distinct pairs, the wrong-`mem_size` proof, and the four refusal mismatch cases with `bus_recording_count() == 0` and `!bus_recording_saturated()` | Depends on 2 and 8. |
| 10 | Host D-07 guard: `PageSizeUnavailableError` in `exceptions.py`, its `except` arm **above** the generic `EpromOperationError` arm in `map_typed_errors`, `require_page_size` at `eprom_operations.py:2002`, optional CLI pre-flight at `cli_handlers.py:758` | Independent of 8; can run parallel. |
| 11 | The 27-row record artefact under `.planning/v1.39/`, following the `.planning/v1.33/sweep-outcome-record.md` precedent. Include the evidence-class split: **0 of 9 on hardware, 9 of 9 on the database comparison**. | Depends on 4 and 9. |
| 12 | `W29C020` no-regression bench run (part from the correct 18), transcript committed. D-12 filed as a backlog item. | Last. PAGE-03's hardware leg stays OPEN for the `W29C512`. |

---

## Unresolved — planner must decide

**U1. The four now-false comments in shipped source.** `firestarter_app/firestarter/database.py:403-409` and `:545-552`, `firestarter_app/firestarter/constants.py:141-145`, `firestarter_fw/src/json_parser.c:150-155`, and `firestarter_fw/include/firestarter.h:186-189` all assert that `page_size` is consumed by "algorithm 13 / 0x0D only" and that "other algorithms' handlers never consume this key". After this phase all four are factually wrong. The `CLAUDE.md` hard rule says "**Write no comments into product source**" — which forbids *adding* prose but does not obviously forbid *deleting* a false clause, and does not say what to do with an inherited comment the change falsifies. Three routes:
  - (a) **delete the falsified clauses** (writing nothing new) — consistent with the rule's letter and with "if code needs explaining, make the code clearer";
  - (b) leave them, and record the known-stale list in `194-SUMMARY.md`;
  - (c) reword them, which is writing a comment and appears to be forbidden.
  I did not settle this because it is a rule-interpretation question about a rule the operator marked non-overridable, and a researcher should not decide it. **Recommendation: (a), with the deletions itemised in `194-SUMMARY.md`.** Note that `firestarter_fw/include/firestarter.h:186-189` also carries a *live* cross-reference (`Reset per command in json_parse, exactly like chip_id above`) that is still true, so any deletion there must be surgical.

**U2. Whether `0xBF` is the right id to spend.** §R3 establishes that `0xBF` is the **only** free id in the `ERROR` band `0xA0–0xBF`, that the band `0xC0–0xDF` is entirely unallocated, and that severity is an explicit catalog field rather than an id-range derivation — so extending ERROR past `0xBF` is mechanically possible. Spending the last in-band id here is defensible (this is a silent-data-corruption refusal; there is no better claimant) but it hands the band question to the next phase that needs an error. **The planner should either spend it deliberately and note the consequence, or raise the band question now.** I did not decide it because it is a project-convention decision with consequences outside this phase.

**U3. The refusal id's parameter shape.** §R3 proposes a `u16` echoing the rejected value (2 wire bytes, makes 0 / 65535 / not-a-power-of-two distinguishable). A parameterless form is cheaper and matches most of the band. Both satisfy D-05's "named error". Recommendation: take the `u16`; the whole milestone is about the operator being able to tell what happened.

**U4. Where the `FLASH_5V_PAGE_SIZE_MAX` constant lives.** §R2 recommends a `#define` local to `flash_5v_page.cpp` (option 1 of 3) and gives the reasoning against hoisting it into `include/`. Not a blocker, but it is a real choice and the planner owns it.

---

## Security Domain

`security_enforcement` is not set to `false` in `.planning/config.json`, so this section is present. `workflow.nyquist_validation` **is** explicitly `false` `[VERIFIED: .planning/config.json:11]`, so the Validation Architecture section is omitted.

### Applicable ASVS categories

| ASVS Category | Applies | Standard control in this phase |
|---|---|---|
| V2 Authentication | no | Local USB-serial tool; no identity boundary. |
| V3 Session Management | no | Stateless three-phase command protocol. |
| V4 Access Control | no | No multi-principal surface. |
| **V5 Input Validation** | **yes** | This phase *is* an input-validation change. `handle->page_size` arrives over the wire and is now validated fail-closed in the consuming handler: reject `0` before the power-of-two test, accept only a power of two in `[1, 512]`, refuse otherwise with no write. The transport already saturates above `0xFFFF` (`json_parser.c` SATURATE policy), and the generator asserts fail-closed on emit (D-03), giving three independent layers. Do not hand-roll a fourth. |
| V6 Cryptography | no | None involved. |

### Threat patterns for this stack

| Pattern | STRIDE | Mitigation in this phase |
|---|---|---|
| Trusted-input assumption on a wire field | Tampering | The firmware validates independently of the host, because it is the only layer that can protect the silicon from any caller (D-07). |
| Silent data destruction reported as success | Tampering / Repudiation | D-05 refuses rather than guessing; both wrong directions are unsafe and neither is a degraded mode (CONTEXT.md D-05's reasoning). |
| Integer wrap on an unsigned mask (`0 - 1` → all-ones) | Tampering | `eeprom_28c.cpp:391-396`'s documented ordering is copied: reject `0` **before** the subtraction. An all-ones mask flushes almost never — the dangerous direction. |
| Out-of-band value indexing memory | Tampering | The mask is only ever ANDed with an address, never used to index `data_buffer`. Preserve that property; it is what bounds the blast radius of a bad value. |
| Vacuous test giving false assurance | Repudiation | §R5's measured 256-entry silent-truncation hazard, and the `bus_recording_saturated()` signal that closes it. |

---

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|---|---|---|
| A1 | `MSG_ERR_FL4_PAGE_SIZE` is a suitable name, following the file's existing `MSG_ERR_FL4_*` prefix | R3 | Cosmetic. The prefix is verified in the catalog; the specific noun is my proposal. |
| A2 | `PageSizeUnavailableError` is a suitable exception name | R3 | Cosmetic. |
| A3 | `4096` is the right new default for `HOST_STUBS_MAX_RECORDING` | R5 | Low. Derived from the measured 3-records-per-byte density × the 512-byte `DATA_BUFFER_SIZE` cap × 2 calls ≈ 3100, rounded up. If the planner adds longer cases, re-derive. |
| A4 | A task regenerating `chip_database.json` will have network egress to gitlab.com | R1 | Medium. The fetch succeeded in this session and there is no local-path fallback in `build_db.py`. If a sandboxed executor lacks egress, task 4 blocks — mitigate by caching the XML to a scratch path in task 3 and passing it in, which would require a small `build_db.py` change not currently in scope. |
| A5 | The 25 wire-delta positional indices in §R4 will be unchanged after regeneration | R4 | Low but real. Row order is stable for a pinned XML, but the indices are the fragile part — re-derive rather than copy, as stated. |

---

## Sources

### Primary (HIGH confidence — measured in-session)

- minipro `infoic.xml` @ `a8efaedc236c1d9718bd28299dfbb99536b010ff` — fetched, 17,861,009 B, `sha256 cdd21319…6b8a`; 11,481 `<ic>` records joined against all 746 database rows
- `firestarter_app/firestarter/data/chip_database.json` — read directly, 59 manufacturers / 746 rows
- `pio run -e uno` and `-e leonardo` — baseline and post-change builds, both envs, with restoration verified by `md5sum` and `git status --porcelain`
- `avr-nm --print-size -t x` and `avr-objdump -d` on both linked ELFs — helper sizes and caller sets
- `pio test -e native -f "*test_val_5v_page*"` — 15/15 green baseline; the recording-density probe
- `firestarter_app/.venv311/bin/python -m pytest` (3.11.16) — 44/44 green on the five affected host modules
- `git fetch origin beta` + `git rev-parse` blob shas in both sub-repos
- `/usr/bin/grep` sweep driven from a `bash` script (never the devcontainer's ugrep)
- `python3 tools/planning_citation_gate.py firestarter tests tools` — `OK: 140 files scanned`

### Secondary (source read this session, cited by path and line)

- `firestarter_fw/src/proms/flash_5v_page.cpp`, `eeprom_28c.cpp`, `src/json_parser.c`, `include/firestarter.h`, `include/logging_id.h`, `include/messages.h`, `platformio.ini`, `.github/workflows/build.yml`, `test/native/avr/_shared/host_stubs_common.inc`, `test/native/avr/test_val_5v_page/`
- `firestarter_app/tools/build_db.py`, `tools/planning_citation_gate.py`, `firestarter/{database,constants,cli_handlers,eprom_operations,exceptions,flash4_erase_gate}.py`, `tests/{test_page_size_invariants,test_vcc_margin_rail,test_wire_dict_equivalence,test_chip_database_field_inventory,test_lock_status_class_partition,test_b15_page_size_corroboration,test_erase_flag_invariants}.py`, `tests/golden/{chip_database_field_inventory.json,wire_dict_expected_deltas_149.json}`, `.github/workflows/ci.yml`
- `tools/catalog/{messages.toml,codegen.py,sync_to_subrepos.sh}`
- `/workspaces/CLAUDE.md`, `firestarter_fw/CLAUDE.md`, `firestarter_app/CLAUDE.md`
- `.planning/{REQUIREMENTS.md,config.json}`, `.planning/todos/pending/runtime-info-log-naming-the-effective-page-size.md`, `.planning/phases/194-real-page-size-reaches-the-firmware/194-CONTEXT.md`

### Not consulted

No external documentation, web search or package registry was needed: this phase installs no packages, and every claim is answerable from the pinned upstream XML and the two working trees. The AT29C020 datasheet corroboration in CONTEXT.md §Specific Ideas was not re-verified — it is already recorded there and §R1's join reaches the same value (256) by an independent route.

---

## Metadata

**Confidence breakdown:**

| Area | Level | Reason |
|---|---|---|
| R1 — the all-27 join | **HIGH** | Executed against the pinned upstream XML with a from-scratch index; every CONTEXT.md figure reproduced; the 0x0D 18+66 split independently reproduced as a cross-check; an in-repo frozenset independently agrees on the 27 identities. |
| R2 — mask shape and flash delta | **HIGH** | Both envs built before and after; helper sizes and caller sets read from the linked ELFs; file restored and baseline reproduced byte-for-byte. The one non-measured element is the *final* code shape the planner chooses, which may differ from my experiment by a few bytes. |
| R3 — refusal id | **HIGH** on the mechanics (band occupancy, zero PROGMEM cost, exact commands and rewritten files, host insertion points all read from source); **MEDIUM** on the naming, which is a proposal (A1, A2) and on U2's band decision, which is the planner's. |
| R4 — gates and goldens | **HIGH**. Five host gates and one firmware suite identified with file:line and verbatim assertions; current state verified green on the CI interpreter; the sweep used `/usr/bin/grep` from a script. Two gates and two firmware cases beyond CONTEXT.md's three. |
| R5 — native test mechanics | **HIGH**. Reachability confirmed by running the suite; the recording density and its saturation point measured by probe with the exact numbers pasted; both documented blind spots traced to their source lines with a concrete design that avoids each. |

**Corrections issued against CONTEXT.md / the brief:**

1. `flash_5v_page.cpp` has **two** `%` sites (92, 100), not three — `:82` is the derivation call.
2. The mask swap **costs +6 B**, it does not free flash. `__udivmodsi4` has seven callers.
3. `chip_database_field_inventory.json`'s machine-read count of 20 is at **line 42**, not line 14 (line 14 is prose).
4. `eeprom28c_page_mask()` is at `eeprom_28c.cpp:402-410`, not `:392-410`.
5. Two host gates and two firmware native cases move beyond the three CONTEXT.md named.
6. An `id_frame` message costs **no** firmware PROGMEM string — `messages.h` is ID-only.
7. The pending todo's `firestarter/tools/catalog/messages.toml` path does not exist; the sub-repos carry no catalog. (Do not edit the todo — D-09.)
8. No CI drift gate exists between the catalog and the generated artefacts.

**Research date:** 2026-09-15
**Valid until:** 2026-10-15 for the measured figures (they are pinned to a fixed upstream SHA and two clean working trees). **Re-measure immediately** if `origin/beta` advances in either sub-repo, or if `MINIPRO_XML_URL`'s pin moves.

## RESEARCH COMPLETE
