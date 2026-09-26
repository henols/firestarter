<!--
  Phase 157 RESEARCH — v1.33 Source Hygiene & Firmware Size Reduction.

  Every figure in this document that is labelled MEASURED was produced in this
  research session, on this machine, at firmware `1151dc4` with a clean tree.
  Every figure labelled UNVERIFIED was NOT reproduced here and the plan is told
  to measure it.

  ⚠ CITATION STALENESS: this document's own `file:LINE` citations were measured
  against the CURRENT tree (post-Phase-154 sweep). They will themselves be
  remapped by Phase 159 (REMAP-01..04). Do not trust any `json_parser.c:NNN`
  citation you find in a `.planning/` document written BEFORE Phase 154 —
  `json_parser.c` lost 198 of 198 citations in the sweep.
-->

# Phase 157: Command-Decode Table + Handle Type Narrowing — Research

**Researched:** 2026-08-23
**Domain:** AVR C firmware — PROGMEM data-table refactor, struct field narrowing, fail-closed input validation, size measurement
**Confidence:** **HIGH** — the headline figure (−1148 B flash / −5 B RAM on all three AVR targets) was reproduced end to end in this session, and so were the stub-cost ledger, the string-duplication ledger, the struct offsets, the native pass, the gate blast radius and the safety hole. Two findings materially change the phase's shape (see §Headline findings).

---

## Summary

Phase 157 finishes a half-done refactor in `src/json_parser.c`: `key_parsers[]` matches a wire
key, then dispatches through a PROGMEM function pointer to a `get_*` stub that **re-matches the
same key**. The opacity of the function pointer is what costs the bytes — I measured the eleven
stubs at **exactly 1012 B** on `uno` while the five structurally identical siblings called
directly with a literal key (`get_r1`, `get_r2`, `get_rev`, `get_rw_pin`, `get_vpp_pin`) cost
**zero**, because they inline. Replacing the table with `{key, offset, width, clamp}` plus one
inlined `store_field`, and narrowing `handle->protocol` to `uint8_t` and `handle->ctrl_flags` to
`uint16_t`, measures **−1148 B flash and −5 B RAM on `uno`, `uno328pb` and `leonardo` alike** —
the ROADMAP's headline figure, confirmed exactly.

The reference implementation already exists, in
[`.planning/notes/firmware-size-reduction-measured.patch`](../../notes/firmware-size-reduction-measured.patch)
lines 1–30 (`include/firestarter.h`) and 98–311 (`src/json_parser.c`). It does **not** apply
cleanly at this tree position — Phase 154's provenance sweep deleted the two comment lines its
substantive hunk removes — and it carries **two real defects** the plan must fix. This research
built it by hand, measured it on all three targets, ran both native envs, ran the full host
suite, and reverted the tree to `1151dc4` clean.

**Primary recommendation:** take the reference patch as a *specification, not an applier*.
Hand-transcribe the field table, then make three changes to it before committing: (1) keep the
table identifier `key_parsers` so the host-repo parity gate stays green, (2) **mask, never
saturate, `ctrl_flags`** — saturating a bitmask sets `FLAG_FORCE | FLAG_SKIP_ERASE |
FLAG_SKIP_BLANK_CHECK` simultaneously, which is a fail-*open* regression in the phase whose
headline criterion is fail-closed, and (3) strengthen the compile-time assertion from one field
to all eleven.

### Headline findings

| # | Finding | Consequence |
|---|---|---|
| **F-1** | **The reference patch's `ctrl_flags` saturation is a safety defect.** `FIELD(key_flags, ctrl_flags, 0)` with a 2-byte member saturates a wire `flags` value > 0xFFFF to `0xFFFF`, setting *every* control flag including `FLAG_FORCE` (0x01), `FLAG_SKIP_ERASE` (0x04) and `FLAG_SKIP_BLANK_CHECK` (0x08). Today (`uint32_t ctrl_flags`) the same input stores 0x10000 — no defined flag set, harmless. | The plan MUST give bitmask fields mask-semantics, not saturate-semantics. This is a plan-level design decision, not an implementation detail. |
| **F-2** | **The phase is NOT firmware-only.** Renaming `key_parsers[]` → `FIELDS[]` turns `firestarter_app/tests/test_json_key_parity.py::test_page_size_key_string_matches_constants_py` **RED** and makes `::test_every_dispatched_identifier_has_a_declared_key_string` pass **vacuously** (its extractor returns an empty set on regex miss — fail-open). MEASURED: 3 failures on the changed tree, 1 of them substantive. | Either keep the identifier `key_parsers` (recommended — zero host edits, zero fail-open) or accept a host-repo commit, which contradicts the ROADMAP's "Phases 155–158 are firmware-only" claim. |
| **F-3** | **`src/json_parser.c` IS inside the native build.** `build_src_filter = +<proms/> +<boards/rurp_serial_utils.cpp> +<json_parser.c> +<operation_utils.cpp>` on `[env:native]`, `[env:native_nodevtools]` and all four v131 envs (`platformio.ini`). `configure_memory` is in via `+<proms/>`. `test/native/avr/test_read_timing/` already calls `json_parse` directly against a real `jsmn_parse`. | DECODE-05's and DECODE-06's tests are **fully runnable natively, in CI**. No substitute oracle is needed — this is the opposite of Phase 155's `rurp_common.cpp` situation. |
| **F-4** | **DECODE-05's blindness claim is PROVEN experimentally.** I narrowed `protocol`/`ctrl_flags` with the saturation block **deleted** and ran `pio test -e native`: **172/172 passed**. | The suite is genuinely blind to the truncation hole. Criterion 5's "all 172 existing tests passed against the broken version" is confirmed at this position, not inherited. |
| **F-5** | **Eleven of eleven wire keys are stored twice today**, not ten of eleven — including `flags`. And after the refactor all eleven appear **exactly once** on both `uno` and `leonardo`. MEASURED by an offset-resolved `strings` dump. | DECODE-02 is *mechanically provable*, and the oracle is a string-occurrence count on the ELF. Details and the trap in §DECODE-02. |
| **F-6** | **The pre-existing BASE-01 RED masks nothing.** The canonical `--policy merge05 --baseline scripts/baseline/size_baseline_base01.json --rebuild` run at `1151dc4` fails with **exactly two lines**, both native case counts (`141` vs `172`). No AVR flash or RAM leg fails. | Phase 157 can rely on the merge05 flash/RAM legs being informative. But adding native cases moves the count off 172 and reddens the *default* baseline mode's count leg too — see §Gate blast radius. |

---

## User Constraints

**There is no `157-CONTEXT.md`.** Phases 155 and 156 of this milestone were also planned without
one. The authoritative scope is therefore:

- `.planning/ROADMAP.md` — the `## v1.33` milestone entry (line 29), the milestone framing block
  (lines 181–197, carrying D-01…D-05), and Phase 157's own section (lines 360–383).
- `.planning/REQUIREMENTS.md` — DECODE-01…DECODE-07 (lines 56–62), the traceability table
  (lines 114–120), the 999.35 overlap note (line 150).
- `/workspaces/CLAUDE.md` and `/workspaces/firestarter/CLAUDE.md`.

### Locked decisions carried from the milestone framing (verbatim substance)

| ID | Decision | Bearing on Phase 157 |
|----|----------|----------------------|
| **D-01** | Phase 154 sweeps source and **builds** the remap tool; Phase 159 applies it **exactly once**, over the composite pre-154→post-158 diff. | Phase 157 does **not** remap any citation. It writes citations against the current tree and hands them forward. |
| **D-02** | No success criterion in this milestone requires a physical board. | Every DECODE criterion is discharged by build + native test + source inspection. No bench leg. |
| **D-03** | No exemption is authored for a reduction; the MERGE-05 pass is recorded **as one-sided** so nobody later reads a green run as "no size change". | Confirmed in source: `scripts/check_size_baseline.py:697` is `if flash_delta > allowance`, `:709` is `if ram_delta > ram_tolerance`. |
| **D-04** | No phase may attribute a native-suite failure to its own change on N=1; re-run on an idle machine first. | I observed 19.8 s / 25.3 s / 54.6 s for three 172/172 runs this session. Duration varies 2.8× with load; the result did not. |
| **D-05** | The `.planning/` citation staleness between 154 and 159 is temporary, marked, and **close-blocking** (`REMAP-04`, marker at `.planning/v1.33/CITATIONS-STALE.md`). | `firestarter/src/json_parser.c` is named in that marker (`CITATIONS-STALE.md:61`). This document's citations will be remapped. |
| **MERGE-05 one-sidedness** | A shrink passes with **no** named exemption — the first size movement in this project's history that doesn't. | Phase 157 authors **no** new exemption constant. |
| **Out of scope: binary command protocol** | Operator decision 2026-08-22. Filed as v1.28 / Backlog **999.35**. | See §The 999.35 overlap. Propose no step toward it. |
| **Firmware-only asymmetry** | "Phases 155–158 are firmware-only — no host file moves, no wire change, no `chip_database.json` change, no protocol-parity constant moves." | **CONTRADICTED by measurement** — see F-2 / C-12. The plan must resolve this explicitly. |

### Claude's discretion (inferred, since no CONTEXT.md locks it)

- The exact field-table row layout and the `store_field` implementation shape.
- The mechanism and strength of the compile-time assertion.
- The out-of-range semantic per field (saturate / mask / reject) — **but see F-1**; this is a
  safety decision the planner should surface to the operator rather than settle silently.
- Where the new tests live and how many cases they add.
- Whether to re-measure DECODE-07's +18 B or record the original with provenance.

### Deferred ideas (OUT OF SCOPE for this phase)

- Converting `configure_memory`'s if-chain to a `switch` — DECODE-07 **rejects** this; recording
  the measurement is the whole requirement.
- Re-anchoring `scripts/baseline/size_baseline.json` — that is Phase 158 / LAND-01.
- Fixing the BASE-01 native case-count mismatch — Phase 158 / LAND-03.
- The `jsmntok_t` 8→6 B narrowing, the `flash_5v_page` modulo, `NUMBER_JSNM_TOKENS` — Phase 158.
- Narrowing `eprom_params_for(uint32_t protocol)` / `eprom_block_budget_s(uint32_t protocol,…)`
  signatures. Not required by DECODE-04 and it widens the blast radius into `include/eprom_params.h`,
  `include/eprom_budget.h` and their v131 native suites. Recorded as a lead, not taken. See
  §DECODE-04.

---

## Phase Requirements

| ID | Description (from REQUIREMENTS.md) | Research support |
|----|-----------------------------------|------------------|
| **DECODE-01** | `key_parsers[]` + eleven `get_*` stubs → one `{key, offset, width, clamp}` data table. Stubs cost **1012 B**; five directly-called siblings cost **zero**. Measured −976 B. | §DECODE-01 — stub ledger MEASURED at exactly 1012 B; five siblings confirmed absent from the symbol table; the **−976 B split is corrected to −890 B** (C-4). Reference implementation in the patch, hunk-by-hunk applicability in §Prior art. |
| **DECODE-02** | Every wire key appears **once** in flash. Ten of eleven stored twice. `get_flags` stays a real function (two direct call sites). | §DECODE-02 — **eleven of eleven** stored twice (C-3); after the refactor all eleven appear once on `uno` and `leonardo` (MEASURED); the two `get_flags` sites are `json_parse_config:160` **and** `json_get_cmd:191`, not two in `json_parse_config` (C-1). A `strings`-based oracle is specified. |
| **DECODE-03** | `width` derived via `sizeof(((firestarter_handle_t*)0)->member)`; a **compile-time assertion** prevents a reorder from truncating an offset. Fields at 3–37, `data_buffer` at 38. | §DECODE-03 — offsets MEASURED before **and** after, on **both** AVR and native. Before: 3–37, `data_buffer` 38, `sizeof` 600. After: 3–32, `data_buffer` 33, `sizeof` 595. `_Static_assert` **compiles on all three AVR targets and on native** (verified by building). The reference assertion is **weaker than the criterion claims** (C-14). |
| **DECODE-04** | `protocol` → `uint8_t`, `ctrl_flags` → `uint16_t`. 19 protocol comparisons, 45 `is_flag_set` sites. | §DECODE-04 — counts corrected to **17** comparisons + 1 `switch` = 18 protocol-keyed sites, and **40** `is_flag_set` textual uses in `src/` (**59** post-preprocessor) (C-5). Promotion, format-specifier, EEPROM-layout and host-parity surfaces all checked; **not wire-visible**. |
| **DECODE-05** | An out-of-range wire `algorithm` fail-closes rather than truncating, **proven by a new test**. Fix saturates in `store_field`, covering `pins`, `chip_id`, `vpp_mv`, `page_size`. | §DECODE-05 — the hole is located exactly; the fail-closed tail is `configure_not_implemented` (`memory.cpp:143`); blindness **PROVEN** (F-4); per-field fail-closed semantics analysed one by one; **`ctrl_flags` must not saturate (F-1)**; the four "newly covered" fields **already truncate today** (C-6); test spec given, native-runnable (F-3). |
| **DECODE-06** | The Phase-44 `READ_TIMING_MAX_US` clamp survives, **proven by a test**; the `#define` must be hoisted above the table. | §DECODE-06 — a clamp test **already exists** for `read-settling-delay` (`test_read_timing_params.cpp:121`) but **none** for `read-strobe-us` (C-8). Hoist confirmed necessary: the `#define` currently sits at `json_parser.c:47`, the table lands at ~`:68`. |
| **DECODE-07** | Record the rejected `switch` alternative with its measurement: **+18 B worse** (`uno` 25696 vs 25678). | §DECODE-07 — record-only, no code change. The absolute figures are **stale by 1444 B** (C-10). Recommendation and cost of re-measuring given. |

---

## Architectural Responsibility Map

| Capability | Primary tier | Secondary tier | Rationale |
|------------|--------------|----------------|-----------|
| Wire-key → handle-field decode | **Firmware — `src/json_parser.c`** | — | This is the whole phase. The host emits JSON; the firmware owns the mapping. |
| Out-of-range wire value refusal | **Firmware — `src/json_parser.c` (`store_field`)** | Firmware — `src/proms/memory.cpp` (`configure_memory` fail-closed tail) | Validation at the parse boundary is a *new* seam this phase creates. The existing fail-closed tail stays the backstop. |
| Protocol dispatch | **Firmware — `src/proms/memory.cpp`** | — | Untouched. DECODE-07 keeps the if-chain, so `firestarter/CLAUDE.md`'s line-for-line dispatch-order contract stays valid. |
| Read-timing clamp (T-44-01) | **Firmware — `src/json_parser.c` table `clamp` column** | Firmware — `src/proms/memory.cpp` (`memory_get_data` consumes the values) | Moves *within* the same tier: from a per-stub literal to a table column. |
| Wire-key/host-constant parity | **Host — `firestarter_app/tests/test_json_key_parity.py`** | Firmware source text (scanned) | A **cross-tier gate**. It scans firmware source by regex, so a firmware rename is a host-tier failure. This is why F-2 exists. |
| Flag-bit / command-constant parity | **Host — `firestarter_app/tests/test_revision_constants_parity.py`** | `include/firestarter.h` `#define`s (scanned) | Unaffected — Phase 157 changes field *types*, not `#define`s. Verified GREEN on the changed tree. |
| Size / RAM budget enforcement | **Local run — `scripts/check_size_baseline.py`** | — | In **no** CI workflow (verified: `grep -rn check_size_baseline .github/` returns nothing). A local-run obligation. |

---

## Prior Art — two carriers, and exactly what applies

### Carrier 1: the applyable patch

`.planning/notes/firmware-size-reduction-measured.patch` — 10 file diffs. Phase 157's subset is
exactly **two**:

| Patch lines | File | Belongs to |
|---|---|---|
| 1–30 | `include/firestarter.h` | Hunks **1 and 2** are Phase 157 (`protocol` u32→u8, `ctrl_flags` u32→u16). Hunk **3** (`void* progress_data` removal) is Phase 155 / DEAD-01, **already landed**. |
| 98–311 | `src/json_parser.c` | All of it is Phase 157. |
| 31–97, 312–671 | `memory_utils.h`, `rurp_common.cpp`, `eeprom_28c.cpp`, `eprom.cpp`, `flash_intel.cpp`, `flash_utils.cpp`, `memory.cpp`, two test files | Phases 155 and 156. **Already landed.** |

### Carrier 2: the preserved branch

`wip/v1.33-size-reduction-survey-preserved` @ **`a6b46f8`** ("wip(v1.33): preserve
size-reduction-survey working tree before the provenance sweep"). Confirmed to exist and to be
the ref carrying the work — the branch named in the `## v1.33` ROADMAP entry
(`size-reduction-survey`) does **not**. Same finding Phase 156's research recorded; re-confirmed
this session by `git log --oneline -1 wip/v1.33-size-reduction-survey-preserved`.

### Applying the subset — MEASURED, hunk by hunk, at `1151dc4`

```
$ sed -n '98,311p' .../firmware-size-reduction-measured.patch > /tmp/157-json.patch
$ for C in 0 1 2 3; do git apply --check -C$C /tmp/157-json.patch; done
error: patch failed: src/json_parser.c:76
error: src/json_parser.c: patch does not apply        # ALL FOUR context levels

$ patch -p1 --dry-run -F3 < /tmp/157-json.patch
Hunk #3 FAILED at 58.
Hunk #4 succeeded at 115 (offset -1 lines).
Hunk #5 succeeded at 290 (offset -1 lines).
Hunk #6 succeeded at 329 with fuzz 1 (offset -1 lines).
Hunk #7 succeeded at 341 with fuzz 2.
1 out of 7 hunks FAILED

$ git apply --3way /tmp/157-json.patch
Applied patch to 'src/json_parser.c' with conflicts.   # one conflict region, lines 84-123
```

**Why hunk #3 fails, and why `-C` cannot fix it.** Hunk #3 is the substantive one — it deletes
`key_parser_t` / `key_parsers[]` and inserts `field_desc_t` / `FIELDS[]` / `_Static_assert` /
`store_field`. Its **removal** lines include two provenance comments that **Phase 154's sweep
deleted**:

```
-    /* Phase 44 — read-timing sweep knobs (RCA-01 causal proof, D-04) */
-    /* Phase 149 — page-size seam (PGSZ-01/PGSZ-02) */
```

The current tree carries `/* Read-timing sweep knobs. */` and `/* Page-size seam. */` instead
(`json_parser.c:164`, `:79`). `-C` reduces *context* lines; it cannot reconcile a `-` line that no
longer exists. `[VERIFIED: four `git apply --check` runs and one `patch -F3` dry-run, this session]`

`include/firestarter.h`:

```
$ patch -p1 --dry-run < /tmp/157-hdr.patch
Hunk #3 FAILED at 223.
1 out of 3 hunks FAILED          # hunk 3 = progress_data, already removed by Phase 155
```

Hunks 1 and 2 apply **cleanly** (no fuzz, no offset).

**Recommendation to the plan:** treat the patch as a **specification**. Apply
`include/firestarter.h` hunks 1–2 with `patch -p1` (dropping hunk 3's `.rej`), then either
`git apply --3way` the json hunk and resolve the single conflict by taking `theirs`, or
hand-transcribe hunk #3. Hand-transcription is preferable because the plan has to modify the
reference anyway (F-1, F-2, C-14). **Never** re-apply the whole composed patch.

---

## Measured Figures — all three targets, this session

All builds warm-incremental unless stated. Tree restored to `1151dc4` clean afterwards
(`git status --short` empty, and the three before-figures reproduced byte-for-byte on the
restored tree).

### Git anchors

| Repo | Branch | SHA | Tree |
|---|---|---|---|
| `firestarter` | `gsd/v1.33-source-hygiene-firmware-size-reduction` | **`1151dc4`** `test(156-06): pin the boolean convention with a non-vacuous source contract` | clean |
| `firestarter_app` | `gsd/v1.33-source-hygiene-firmware-size-reduction` | **`38f0d83`** `refactor(154): strip planning provenance from host source` | 7 pre-existing untracked entries only |
| meta | `gsd/v1.33-source-hygiene-firmware-size-reduction` | `c01bc1ff` | — |
| reference | `wip/v1.33-size-reduction-survey-preserved` | `a6b46f8` | — |

### The before position — Phase 157's baseline

| target | flash_used | RAM used | Caterina / ceiling headroom |
|---|---|---|---|
| `uno` | **24234** | **1567** | 32768 − 24234 = 8534 |
| `uno328pb` | **24282** | **1573** | 32768 − 24282 = 8486 |
| `leonardo` | **26378** | **2008** | **Caterina cliff 28672 − 26378 = 2294 B** |

### After the composed Phase 157 change (reference implementation, unmodified)

| target | flash_used | Δ flash | RAM used | Δ RAM |
|---|---|---|---|---|
| `uno` | **23086** | **−1148** | **1562** | **−5** |
| `uno328pb` | **23134** | **−1148** | **1568** | **−5** |
| `leonardo` | **25230** | **−1148** | **2003** | **−5** |

**The ROADMAP's `−1148 B flash / −5 B RAM` is CONFIRMED EXACTLY on all three targets.**
Leonardo Caterina headroom after: **28672 − 25230 = 3442 B** (the ROADMAP says 3440 — see C-13).

### The decomposition — MEASURED, and it does NOT match the ROADMAP's split

| Variant | `uno` flash | Δ from before | `uno` RAM | `leonardo` flash |
|---|---|---|---|---|
| before (`1151dc4`) | 24234 | — | 1567 | 26378 |
| **field table + saturation only** (no narrowing) | 23344 | **−890** | 1567 (unchanged) | 25488 (−890) |
| **+ narrowing** (`protocol` u8, `ctrl_flags` u16) | 23086 | **−1148** | 1562 (−5) | 25230 (−1148) |
| narrowing **without** saturation (probe only) | 22926 | −1308 | 1562 | — |

Derived: the **saturation block alone costs +160 B** on `uno` in the narrowed variant
(23086 − 22926). The ROADMAP's split (`field table −976, narrowing + saturation −172`) is
**wrong at this position**; the measured split is **−890 / −258**. The *total* is exact. (C-4)

### Per-symbol ledger, `uno` — before

`avr-nm --print-size --size-sort --radix=d .pio/build/uno/firestarter_uno.elf`:

| symbol | bytes |
|---|---|
| `get_read_settling` | 110 |
| `get_read_strobe` | 110 |
| `get_address` | 90 |
| `get_algorithm` | 90 |
| `get_delay` | 90 |
| `get_flags` | 90 |
| `get_memory_size` | 90 |
| `get_chip_id` | 86 |
| `get_page_size` | 86 |
| `get_vpp_mv` | 86 |
| `get_pin_count` | **84** |
| **eleven-stub total** | **1012** ✅ |
| `key_parsers` (PROGMEM table) | 44 (11 × 4 B) |
| `jsoneq_` | 108 |
| `simple_strtoul` | 68 |
| `get_cmd.constprop.31` | 102 |
| `get_r1` / `get_r2` / `get_rev` / `get_rw_pin` / `get_vpp_pin` | **absent from the symbol table — 0 B, fully inlined** ✅ |

### Per-symbol ledger, `uno` — after

| symbol | bytes | note |
|---|---|---|
| `FIELDS` (PROGMEM table) | **66** | 11 × 6 B; +22 B vs `key_parsers`' 44 B |
| `store_field` | **absent — fully inlined** | the whole point of the refactor |
| `get_flags.constprop.33` | **82** | survives; still called at `json_parse_config` and `json_get_cmd` |
| `get_cmd.constprop.32` | 102 | unchanged |
| `jsoneq_` | 108 | unchanged |
| `simple_strtoul` | 68 | unchanged |
| all ten other `get_*` | **gone** | ✅ |

### Native and gate results at `1151dc4`

| Leg | Result | Note |
|---|---|---|
| `pio test -e native` | **172 cases / 17 suites / 172 succeeded**, 19.8 s | |
| `pio test -e native_nodevtools` | **172 / 17 / 172**, 29.9 s | |
| `pio test -e native` **with the change** | **172 / 172**, 54.6 s | |
| `pio test -e native` **narrowed, saturation deleted** | **172 / 172**, 25.3 s | **F-4: the suite is blind** |
| `pytest tests/` (host, full) | **1976 passed / 0 failed / 0 skipped**, 241 s | matches the Phase 154 record exactly |
| AVR build warnings, changed tree | **0** on all three targets | the gate's AVR rule is `== 0` |
| `check_size_baseline.py --policy merge05 --baseline …base01.json --rebuild` | **FAIL, exactly two lines**: `native: cases baseline=141 observed=172`, `native_nodevtools: cases baseline=141 observed=172` | **F-6: no AVR flash or RAM leg fails** |

### Struct offsets — MEASURED on both architectures, before and after

Method: a generated TU of `char off_<m>[offsetof(firestarter_handle_t, m)+1];` compiled with
`avr-gcc -mmcu=atmega328p` and with host `gcc`, offsets read back from `nm --print-size`.
`DATA_BUFFER_SIZE=512`, `-DHARDWARE_REVISION -DDEV_TOOLS`.

| member | AVR before | AVR after | native before | native after |
|---|---|---|---|---|
| `cmd` | 0 | 0 | 0 | 0 |
| `operation_state` | 1 | 1 | 1 | 1 |
| `response_code` | 2 | 2 | 2 | 2 |
| **`protocol`** | 3 (u32) | **3 (u8)** | 4 | 3 |
| **`pins`** | 7 | 4 | 8 | 4 |
| **`mem_size`** | 8 | 5 | 12 | 8 |
| **`address`** | 12 | 9 | 16 | 12 |
| **`vpp_mv`** | 16 | 13 | 20 | 16 |
| **`pulse_delay`** | 18 | 15 | 24 | 20 |
| **`read_settling_us`** | 22 | 19 | 28 | 24 |
| **`read_strobe_us`** | 26 | 23 | 32 | 28 |
| **`ctrl_flags`** | 30 (u32) | **27 (u16)** | 36 | 32 |
| **`chip_id`** | 34 | 29 | 40 | 34 |
| **`page_size`** | 36 | 31 | 42 | 36 |
| `data_buffer` | **38** | **33** | 44 | 38 |
| `data_size` | 550 | 545 | 556 | 552 |
| `bus_config` | 554 | 549 | 560 | 556 |
| **`sizeof(firestarter_handle_t)`** | **600** | **595** | **655** | **655** |

Four things follow, and all four matter to the plan:

1. **The ROADMAP's "all eleven fields currently sit at offsets 3–37, below `data_buffer` at 38"
   is CONFIRMED exactly** on AVR. After the change they sit at **3–32** with `data_buffer` at 33.
2. **The −5 B RAM saving is AVR-only.** `sizeof` is **655 both before and after on native** — the
   five bytes are absorbed by the 8-byte alignment padding before the function-pointer block. A
   native test asserting the RAM saving would be **vacuously false**; state this ceiling.
3. **Native and AVR offsets differ at every field from `protocol` down.** Any test or assertion
   that hard-codes a numeric offset is wrong on one of the two. The `offsetof`-derived table is
   correct on both — that is DECODE-03's real value, not just drift protection.
4. `sizeof(firestarter_handle_t)` measures **600 B** before on `uno`-class.
   `155-after-figures.md` records the post-DEAD-01 handle at **601 B**. **1 B discrepancy,
   UNRESOLVED** — different flag set or a different `DATA_BUFFER_SIZE` is the likely cause. The
   plan should re-derive rather than quote either number blind. (Open question OQ-1.)

---

## Corrections to ROADMAP / REQUIREMENTS

**Convention (established by Phases 155 and 156): `.planning/v1.33/157-before-figures.md`
supersedes the ROADMAP criteria where they disagree.** Every correction below is stated as `C-N`
with the measurement that produced it. All measurements at `firestarter` `1151dc4`.

### C-1 — `get_flags`'s two direct call sites are in **two different functions**

ROADMAP criterion 2 and DECODE-02 both say "`json_parse_config` calls it directly at two sites".
MEASURED (`grep -rn get_flags src/ include/ test/`):

```
src/json_parser.c:164   {key_flags, get_flags}          <- the table row
src/json_parser.c:348  } else if (get_flags(...))      <- inside json_parse_config
src/json_parser.c:379  } else if (get_flags(...))      <- inside json_get_cmd
src/json_parser.c:497  bool get_flags(...) {           <- the definition
```

One call in `json_parse_config`, one in `json_get_cmd`. The *conclusion* survives — `get_flags`
must stay a real function — but the reason must name both functions. A record saying
"`json_parse_config` calls it twice" is factually wrong and would mislead anyone auditing the
exception.

### C-2 — the stub cost is exactly 1012 B ✅ but the per-stub range is **84–110 B**, not 86–110 B

`get_pin_count` measures **84 B**, below the stated floor. Every other figure in criterion 1 is
confirmed: total 1012 B, ceiling 110 B (`get_read_settling`, `get_read_strobe`), five siblings at
zero.

### C-3 — **eleven** of eleven wire keys are stored twice today, not ten of eleven

MEASURED by an offset-resolved `strings -a -n 2 -t d` dump of `firestarter_uno.elf`, cross-keyed
against `avr-nm` symbol addresses (`.text` file offset 0x94 = 148, so vaddr = fileoff − 148):

| vaddr block | contents |
|---|---|
| **104 – 221** (118 B) | the named `key_*` PROGMEM arrays: `key_page_size` 104, `key_read_strobe` 114, `key_read_settling` 129, `key_algorithm` 149, `key_vpp_mv` 159, `key_pulse_delay` 166, `key_pin_count` 178, `key_chip_id` 188, **`key_flags` 196**, `key_address` 202, `key_mem_size` 210 |
| **226 – 343** (118 B) | the anonymous `PSTR` duplicates emitted inside the eleven stubs — **including `flags` at 226** |

`flags` is duplicated exactly like the other ten. The reason a naive count misses it is a `strings`
artifact: the byte immediately before the second copy is `0x55`, so `strings` reports the token as
`Uflags`, and an exact-match filter (`awk '$2=="flags"'`) drops it. **This is a live trap for the
DECODE-02 oracle** — see §DECODE-02 for the correct form.

### C-4 — the ROADMAP's −976 / −172 split is wrong; measured is **−890 / −258**

See §Measured figures → decomposition. The **total −1148 B is exact on all three targets**; the
attribution is not. DECODE-01's "Measured: −976 B" should be restated as **−890 B** (field table
including its saturation logic, RAM unchanged) and the remaining **−258 B / −5 B RAM** attributed
to DECODE-04's narrowing. If the plan wants a saturation-free field-table number it must measure a
third variant; I measured only the two above plus the narrowed-no-saturation probe.

### C-5 — DECODE-04's two counts are both UNRECONCILED

| ROADMAP | Measured | Method |
|---|---|---|
| "19 protocol comparisons" | **17** `handle->protocol ==` occurrences (all in `src/proms/memory.cpp`, on 9 lines) **+ 1** `switch (handle->protocol)` (`src/proms/eprom.cpp:70`) = **18** protocol-keyed sites; **20** total `handle->protocol` reads across `src/` (the other two are `eprom_params_for(handle->protocol)` ×3, `eprom_block_budget_s(handle->protocol,…)` ×1, `LOG_ERROR_ID_U8(…, (uint8_t)handle->protocol)` ×2 — 20 reads in total) | `grep -ro "handle->protocol ==" src/` and `grep -rn "\->protocol" src/ include/` |
| "45 `is_flag_set` call sites" | **40** textual uses in `src/` (dev_tools 9, eprom 8, firestarter 7, flash_intel 5, flash_nor_unlock 3, eeprom_28c 3, flash_5v_page 2, memory 1, flash_utils 1, eprom_operations 1); **+19** more created post-preprocessor by `LOG_INFO_ID*` call sites (each `LOG_INFO_ID*` macro body contains one `is_flag_set(FLAG_VERBOSE)`; there are 19 such call sites in `src/`) = **59** post-preprocessor uses. `include/firestarter.h:191` is the definition and `include/memory_utils.h:69` is a prose mention — neither is a call site. | `grep -o is_flag_set <file> \| wc -l` per file; `grep -rno "LOG_INFO_ID[A-Z_0-9]*" src/` |

Neither 40 nor 59 is 45. **Do not restate 19/45.** Use 18 (or 20) and 40 (or 59), each with its
stated derivation.

### C-6 — DECODE-05's "which the per-stub form could not" is misleading for four of the five fields

`pins` (u8), `chip_id` (u16), `vpp_mv` (u16) and `page_size` (u16) are **already narrow today**,
and `extract_int` is a straight alias of `extract_long` (`json_parser.c:482`), so
`simple_strtoul`'s `unsigned long` result is **already silently truncated** into them on the
current tree. Saturation for these four is a **behaviour change on out-of-range input**, not the
closing of a hole the narrowing opens.

Only **`protocol`** gains a genuinely new hole from the narrowing — and **`ctrl_flags` gains one
too**, which criterion 5 does not mention. See C-7.

### C-7 — ⚠ SAFETY DEFECT in the reference patch: `ctrl_flags` must not saturate

`FIELD(key_flags, ctrl_flags, 0)` with `sizeof(ctrl_flags) == 2` after narrowing makes
`store_field` compute `max = 0xFFFF` and saturate. `handle->ctrl_flags` is a **bitmask**:

```c
#define FLAG_FORCE            0x01   /* include/firestarter.h:172 */
#define FLAG_CAN_ERASE        0x02
#define FLAG_SKIP_ERASE       0x04
#define FLAG_SKIP_BLANK_CHECK 0x08
#define FLAG_VPE_AS_VPP       0x10
#define FLAG_OUTPUT_ENABLE    0x20
#define FLAG_CHIP_ENABLE      0x40
#define FLAG_VERBOSE          0x80
#define FLAG_SKIP_SDP_UNLOCK  0x100
```

Saturating to `0xFFFF` sets **all nine**, including `FLAG_FORCE`, `FLAG_SKIP_ERASE` and
`FLAG_SKIP_BLANK_CHECK`. `is_flag_set(flag)` is `((handle->ctrl_flags & flag) == flag)`
(`firestarter.h:191-192`), so every one of the 40 call sites reads true.

Today, `flags: 65536` stores `0x10000` into a `uint32_t` and **no defined flag is set** — the
input is harmless. After the reference patch it would enable force-write, skip-erase and
skip-blank-check simultaneously. **That is a fail-open regression introduced by the phase whose
headline criterion is fail-closed**, and it applies to the one field whose out-of-range value a
buggy host is most likely to produce (flags are OR-composed host-side).

**Recommendation:** give `ctrl_flags` **mask** semantics (`v &= max`, i.e. preserve today's
truncation) with a named comment, and document that saturation is the correct semantic only for
*ordinal* fields. Do not reject the command: a rejection needs a new message id, which means
editing `tools/catalog/messages.toml` in the **meta** repo and regenerating `include/messages.h`
(codegen-generated, never hand-edited) — a cross-repo codegen step this firmware-only phase should
not take. Saturate-vs-mask should be a **per-row property of the table**, not a global rule.

Note that with `get_flags` still handling the `json_parse_config` and `json_get_cmd` paths via
`extract_long`, `flags` arriving on **those** two paths is truncated (not saturated) regardless —
so mask-semantics in the table is also the choice that keeps the three paths consistent.

### C-8 — DECODE-06's clamp is already half-tested; the other half does not exist

`test/native/avr/test_read_timing/test_read_timing_params.cpp:121`
`test_read_settling_us_capped_at_max` sends `{"cmd":1,"read-settling-delay":9999}` and asserts
`h.read_settling_us <= READ_TIMING_MAX_US`. So the clamp on **`read-settling-delay` IS covered
today** and would go RED if deleted.

Three gaps:
1. **No test at all for `read-strobe-us`.** The suite's own header comment (`:21`) documents only
   "T4 — value above cap (T-44-01) → `read_settling_us` clamped to cap".
2. The assertion is `<=`, not `==`. A regression that set the value to `0` — the semantically
   loaded value ("no settling delay" / "use default 3 µs", per `json_parser.c:44`) — would
   pass.
3. The suite **re-defines** `#define READ_TIMING_MAX_US 1000UL` locally at
   `test_read_timing_params.cpp:46`. Hoisting the production `#define` does not affect it, but the
   two constants can drift silently in either direction.

DECODE-06's "proven by a test rather than by inspection" therefore needs: a `read-strobe-us` cap
case, and `==` assertions on both. I verified both existing knob tests **still pass** with the
reference table applied (172/172).

### C-9 — the `#define READ_TIMING_MAX_US` hoist IS required ✅

Today it sits at **`src/json_parser.c:47`**, immediately above the two stubs it serves. The field
table lands at roughly `:68` (after the `key_page_size` declaration at `:66`). The `#define` must
move above it or the `FIELD(key_read_settling, read_settling_us, READ_TIMING_MAX_US)` row will not
compile. Confirmed by building the reference implementation, which does exactly this hoist.

### C-10 — DECODE-07's absolute figures are stale by 1444 B; the +18 B delta is UNVERIFIED

The criterion cites `uno` **25696** (switch) vs **25678** (if-chain). Measured at this position:
`uno` is **24234** before the phase and **23086** after. The survey's absolutes predate Phases 155
and 156 (which together removed ~1792 B) and predate the flash-ceiling quick task. **The +18 B
delta is not verifiable from any number I measured** — I did not build the `switch` variant.

### C-11 — the reference patch does not apply cleanly at this position

See §Prior art. Hunk #3 of the `json_parser.c` subset **FAILS at every `-C` level** because
Phase 154's sweep deleted the two provenance comments its removal lines expect;
`include/firestarter.h` hunk 3 fails because Phase 155 already applied it. Phase 156's research
recorded that its own subset applied with `git apply -C1` — **that does not generalise to
Phase 157**, and the difference is caused by the sweep having touched `json_parser.c` (198 of 198
citations) while leaving `eprom.cpp` and `flash_intel.cpp` byte-unchanged.

### C-12 — ⚠ the phase is NOT firmware-only: one host gate goes RED, one goes silently fail-open

MEASURED. With the reference change applied to the firmware sibling:

```
$ cd firestarter_app && python3 -m pytest tests/test_json_key_parity.py \
      tests/test_revision_constants_parity.py -q -o addopts=""
FAILED tests/test_json_key_parity.py::test_page_size_key_string_matches_constants_py
FAILED tests/test_json_key_parity.py::test_planted_key_string_drift_is_detected
FAILED tests/test_json_key_parity.py::test_planted_undispatched_key_is_detected
3 failed, 21 passed
```
(baseline on the unchanged tree: **24 passed**)

Triage:

| Leg | Verdict |
|---|---|
| `test_page_size_key_string_matches_constants_py` | **REAL RED.** `_KEY_PARSERS_TABLE_RE = r"key_parsers\s*\[\s*\]\s*PROGMEM\s*=\s*\{(?P<body>.*?)\};"` (`test_json_key_parity.py:114`) no longer matches, so `_extract_dispatch_identifiers()` returns `set()`, so the page-size identifier is judged "declared but never dispatched". |
| `test_every_dispatched_identifier_has_a_declared_key_string` | **PASSES — VACUOUSLY.** Same empty set; `sorted(dispatched - set(key_map))` is empty, so the assertion is trivially satisfied. This is the documented fail-open class: *host-side gates that scan firmware source text fail OPEN when firmware symbols are renamed.* |
| `test_scan_targets_are_non_vacuous`, `test_the_exemption_tuple_is_complete_and_has_no_stale_entries`, both `JSON_KEY_*` legs | GREEN — `_KEY_STRING_RE` still matches the eleven `const char key_*[] PROGMEM = "…";` declarations, which the refactor keeps. |
| the two `test_planted_*` legs | **ARTIFACT, not a real red.** They assert the sibling firmware repo is **porcelain-clean** (`test_json_key_parity.py:491`) and my experiment left it dirty. Same class as the `test_flash_path_record_sync` hazard. |
| `test_revision_constants_parity.py` (all 9 `FLAG_*`/`CMD_*` legs) | GREEN. It scans `#define` lines only; the field-type change is invisible to it. It also **confirms** the narrowing is sound: it asserts "exactly nine `FLAG_*` defines on each side, maximum **0x100**" (`:513`, `:517`) — so `uint16_t` is provably sufficient and provably parity-checked. |

**Two ways out.** (a) **Keep the identifier `key_parsers` and the `[] PROGMEM = {` shape**, with
the `key_*` identifier as the first member of each row — both regexes then keep matching, both
legs stay green, and **zero host files change**. (b) Update the host gate, which means a
`firestarter_app` commit and an explicit ROADMAP correction to the "firmware-only" claim.
**(a) is strongly recommended**: it costs one identifier choice and it also removes the fail-open,
which (b) would have to fix separately.

### C-13 — Leonardo Caterina headroom after this phase is **3442 B**, not 3440 B

28672 − 25230 = 3442. The 2 B difference is consistent with the guard-constant delta Phase 155
recorded in its OQ-1 (`−1366` vs the ROADMAP's `−1364`).

### C-14 — the reference `_Static_assert` is weaker than criterion 3 claims

The patch emits exactly one assertion:

```c
_Static_assert(offsetof(firestarter_handle_t, page_size) < 256,
               "firestarter_handle_t reordered: a FIELDS offset no longer fits uint8_t");
```

That guards **`page_size` only**. Criterion 3 claims the assertion "prevents a future struct
reorder from silently truncating an offset" — but a reorder that moved, say, `mem_size` below
`data_buffer` would put it at offset ≥ 545 (AVR) / ≥ 552 (native), truncate to 33 / 40, and this
assertion would still pass. Nor does asserting `offsetof(data_buffer) < 256` help, for the same
reason.

**Recommendation:** assert **all eleven** offsets. Two workable idioms:

- eleven explicit `_Static_assert(offsetof(firestarter_handle_t, m) < 256, "…")` lines, generated
  from the same list as the table by a second macro pass; or
- fold the check into `FIELD()` itself using the classic negative-array-size trick, which is legal
  inside an initializer expression:
  `+ 0 * sizeof(char[1 - 2 * (offsetof(firestarter_handle_t, member) > 255)])`.

`_Static_assert` availability is **VERIFIED**: the reference implementation compiled clean (zero
warnings) on `uno`, `uno328pb`, `leonardo` **and** in `[env:native]` (172/172). `json_parser.c` is
a C translation unit in every environment — PlatformIO routes `-std=gnu++17` to `CXXFLAGS`, so the
native build compiles it as C too. There is **one** pre-existing static-assert in the tree,
`include/eprom_params.h:62`, and it is the **C++** `static_assert` in a header only C++ TUs
include — so `_Static_assert` in `json_parser.c` establishes a **new** idiom for this repo. Say so.

### C-15 — adding native cases moves the case count off 172 and reddens both baseline gates

`scripts/baseline/size_baseline.json` records `native_envs.native.cases = 172` (and
`native_nodevtools.cases = 172`); `size_baseline_base01.json` records `141`. Phase 156 added **no
net native cases** (172 before, 172 after). Phase 157 needs at least two or three new cases
(DECODE-05, DECODE-06). Consequences:

- **Default mode** (`check_size_baseline.py` with no `--policy`, against `size_baseline.json`) —
  already RED on `flash_used` byte-identity because of Phases 155/156; will gain
  `native: cases baseline=172 observed=N`.
- **`--policy merge05`** against BASE-01 — already RED on the count leg (141 vs 172); the number
  changes, the leg does not.

Phase 158's LAND-01 re-records `size_baseline.json`. Phase 157 must therefore **record its new
case count as a handoff to LAND-01**, not fix the baseline itself. Also note the lexical/actual
mismatch: `grep -ro "RUN_TEST(" test/native/avr/<17 suites>/` totals **173** while the runner
reports **172** — one occurrence is not an executed case. **Trust the runner, never the grep.**

### C-16 — `check_size_baseline.py` runs in NO CI workflow ✅ CONFIRMED

`grep -rn check_size_baseline .github/` returns nothing. CI (`build.yml:142,155`;
`beta-build.yml:122,128`) runs exactly `pio test -e native`, `pio test -e native_nodevtools`,
then `pytest tests/` and `pio run`. Every size figure in this phase is a **local-run obligation**
(LAND-04, re-verified).

---

## DECODE-01 — the field table

### What exists today, with file:line (measured against the CURRENT tree)

| # | wire key | PROGMEM decl | table row | stub decl | stub def | target member | member type |
|---|---|---|---|---|---|---|---|
| 1 | `memory-size` | `:52` | `:74` | `:18` | `:300` | `mem_size` | `uint32_t` |
| 2 | `address` | `:53` | `:74` | `:19` | `:304` | `address` | `uint32_t` |
| 3 | `flags` | `:54` | `:74` | `:17` | `:296` | `ctrl_flags` | `uint32_t` |
| 4 | `chip-id` | `:55` | `:75` | `:20` | `:308` | `chip_id` | `uint16_t` |
| 5 | `pin-count` | `:56` | `:75` | `:21` | `:312` | `pins` | `uint8_t` |
| 6 | `pulse-delay` | `:57` | `:75` | `:22` | `:316` | `pulse_delay` | `uint32_t` |
| 7 | `vpp_mv` | `:57` | `:76` | `:23` | `:320` | `vpp_mv` | `uint16_t` |
| 8 | `algorithm` | `:58` | `:76` | `:24` | `:324` | `protocol` | `uint32_t` |
| 9 | `read-settling-delay` | `:60` | `:78` | `:25` | `:362` | `read_settling_us` | `uint32_t` |
| 10 | `read-strobe-us` | `:61` | `:78` | `:26` | `:371` | `read_strobe_us` | `uint32_t` |
| 11 | `page-size` | `:66` | `:80` | `:27` | `:389` | `page_size` | `uint16_t` |

Supporting machinery: `key_parser_t` at `:68-71`, `key_parsers[] PROGMEM` at `:73-81`, the
dispatch loop at `:125-133`, `simple_strtoul` at `:38-46`, `jsoneq`/`jsoneq_` at `:48-49` /
`:276-282`, `extract_num`/`extract_long`/`extract_int` at `:284-294`.

The **five zero-cost siblings**, all called with a literal key from a direct `else if` chain:
`get_rw_pin` (`:328`, called at `:261`), `get_vpp_pin` (`:332`, called at `:264`), `get_r1`
(`:336`, called at `:169`), `get_r2` (`:340`, called at `:172`), `get_rev` (`:344`, called at
`:164`, `#ifdef HARDWARE_REVISION`). **None appears in the `uno` symbol table.** That is the proof
criterion 1 asserts, and it holds. `get_cmd` (`:202`) is a sixth direct-call function but is
structurally different (returns a value, matches two keys) and is emitted at 102 B as
`get_cmd.constprop.31`; it is **not** part of the eleven and must not be touched.

### Why the opacity, not the logic, is the cost

`parser_func` is read with `pgm_read_ptr` at `json_parser.c:318` and called through. gcc cannot
see the callee, so it cannot inline it, cannot constant-propagate the literal key into `jsoneq_`,
and must emit each stub with the full four-argument AVR ABI prologue for one `simple_strtoul` and
one store. The five direct-call siblings have identical bodies and cost nothing because the same
`extract_num` macro expands **at the call site**. `[VERIFIED: avr-nm symbol sizes, both variants,
this session]`

### Reference implementation — and the three changes the plan must make to it

The patch's shape (patch lines 155–200) is sound: a 6-byte PROGMEM row
`{PGM_P key; uint8_t offset; uint8_t width; uint16_t clamp;}`, a `FIELD(k, member, cl)` macro
deriving `offset` from `offsetof` and `width` from `sizeof(((firestarter_handle_t*)0)->member)`,
one `_Static_assert`, and a `store_field` that clamps, saturates, then
`memcpy((uint8_t*)handle + offset, &v, width)`.

Required deltas:

1. **Name the table `key_parsers`** (and keep `[] PROGMEM = {`, with the `key_*` identifier as the
   first member of each row) — C-12 / F-2. The row *type* can be renamed freely; only the array
   identifier and the initializer shape are scanned.
2. **Mask, do not saturate, `ctrl_flags`** — C-7 / F-1. This needs a per-row semantic, e.g. a
   `bool is_mask` column or a sentinel in `clamp`. A `bool` column costs 11 B of PROGMEM; folding
   it into a spare bit of `width` costs nothing. Measure whichever is chosen.
3. **Strengthen the assertion to all eleven fields** — C-14.

Two incidental notes on the reference:

- `store_field`'s `if (width < sizeof(v))` guard is what keeps `1UL << (width * 8)` out of
  undefined-behaviour territory on AVR (`sizeof(unsigned long) == 4`, and `1UL << 32` is UB). Keep
  the guard. But see the AVR/native divergence in §DECODE-05.
- `memcpy` of the low `width` bytes is a **little-endian assumption**, correct on AVR, on x86-64
  and on the PY32F071 ARM port. The patch's own comment says so. Keep that comment.
- The refactor adds `#include <stddef.h>` (for `offsetof`) and `#include <string.h>` (for
  `memcpy`) at the top of `json_parser.c`. **Those two lines shift every citation in the file** —
  they are two of the four `#include` lines the milestone framing blames for 41% of the remap
  work. Expected and already accounted for by D-01; no action beyond Phase 159.

---

## DECODE-02 — every wire key once in flash

### The measurement, and the oracle it implies

MEASURED before (`uno`): two 118 B blocks of key strings, vaddr 104–221 (named `key_*`) and
226–343 (anonymous stub `PSTR`s). MEASURED after: **one** block, vaddr 104–221; the second block
is **gone**.

Post-change, offset-resolved dump of the region (`uno`):

```
252 page-size   262 read-strobe-us   277 read-settling-delay   297 algorithm
307 vpp_mv      314 pulse-delay      326 pin-count             336 chip-id
344 flags       350 address          358 memory-size
```

Eleven strings, eleven copies. Independently confirmed on `leonardo` (all ten multi-word keys at
count 1). `[VERIFIED: strings + avr-nm on both ELFs, this session]`

**Including `flags`** — which the reference patch leaves as `extract_long("flags", …)` inside
`get_flags`, i.e. with its own `PSTR("flags")`. The duplicate nevertheless disappears. I did not
establish the mechanism (a gcc/binutils merge of identical `.progmem.data` objects in the same TU
is the likely cause, and the surviving copy is `key_flags`, at the address `avr-nm` reports for
that symbol). **Record this as measured-but-unexplained**, and — because it is a toolchain
behaviour rather than a source property — **re-measure it on all three targets after the real
change lands**. Do not assume it.

If a plan wants belt and braces, changing `get_flags` to call
`jsoneq_(json, &tokens[pos], key_flags)` directly (instead of the `extract_long` macro's
`jsoneq(…, "flags")`) makes single-storage a **source-level property** rather than a
toolchain outcome. Cheap, and it is the honest way to satisfy "appears once in flash".

### The oracle — and its trap

```bash
# CORRECT: offset-resolved, then eyeball the block structure
strings -a -n 2 -t d .pio/build/uno/firestarter_uno.elf | awk '$1>=200 && $1<=560'

# WRONG — silently undercounts:
#   strings -a -t d <elf> | awk '$2=="flags"{c++} END{print c}'     -> reports 1, truth is 2
#   strings -a <elf> | grep -c flags                                -> reports 4 on leonardo
```

`strings` glues a preceding non-NUL printable byte onto the token (`Uflags`), and substring
matching catches unrelated blobs. **The oracle must be an offset-block comparison, not an
exact-string count.** State this in the plan or the criterion will be "proven" by a broken script.

### `get_flags`' exception, stated properly

`get_flags` stays a real function because it is called directly from **`json_parse_config`**
(`:160`, the `CMD_*` config path) and **`json_get_cmd`** (`:191`, the pre-parse command sniff) —
neither of which walks the field table. MEASURED after: `get_flags.constprop.33` = **82 B** (down
from 90 B, because gcc now clones it for its two remaining call shapes). Record it as a deliberate
exception with both call sites named (C-1).

---

## DECODE-03 — width derivation and the compile-time assertion

Everything for this requirement is in §Measured figures → struct offsets and §C-14. Summary of the
answers to the research questions:

| Question | Answer |
|---|---|
| Real current offsets of the eleven fields? | AVR: `protocol` 3, `pins` 7, `mem_size` 8, `address` 12, `vpp_mv` 16, `pulse_delay` 18, `read_settling_us` 22, `read_strobe_us` 26, `ctrl_flags` 30, `chip_id` 34, `page_size` 36 → **3–37**. MEASURED. |
| `data_buffer` offset? | **38** on AVR, **44** on native. MEASURED. |
| After narrowing? | AVR **3–32**, `data_buffer` **33**. Native **3–37**, `data_buffer` **38**. MEASURED. |
| Is `json_parser.c` C or C++? | **C**, in every environment including native (PlatformIO routes `-std=gnu++17` to `CXXFLAGS`). |
| Is `_Static_assert` available? | **YES** — the reference implementation compiled clean on `uno`, `uno328pb`, `leonardo` and `native`. Zero AVR warnings. VERIFIED by building. |
| Existing static-assert idiom in the tree? | Exactly one: `include/eprom_params.h:62`, the **C++** `static_assert`. So `_Static_assert` in a `.c` TU is a **new** idiom here. |
| Portability across the three AVR targets + native? | Verified for all four. The PY32F071 ARM port (`firestarter_app_py32` / `firestarter_py32_ci`) is out of this milestone's scope but is C11-capable and little-endian, so the idiom carries. UNVERIFIED there — not built. |
| Is a `uint8_t` offset safe? | Yes **while every table field sits below `data_buffer`**. The margin is large (33 vs 256 after the change) but the failure mode is silent, hence C-14's stronger assertion. |

---

## DECODE-04 — narrowing `protocol` and `ctrl_flags`

### Value-range justification, verified two ways

- `protocol`: the largest dispatched value is **0x39** (`PROTO_PHANTOM_0x39`,
  `include/proto_constants.h:38`). The full set is `0x05, 0x06, 0x07, 0x08, 0x0B, 0x0D, 0x0E,
  0x10, 0x11, 0x27, 0x28, 0x29, 0x2A, 0x2B, 0x2C, 0x34, 0x35, 0x39`. `uint8_t` suffices. ✅
- `ctrl_flags`: max **0x100** (`FLAG_SKIP_SDP_UNLOCK`, `firestarter.h:188`). And this is not just
  read off the header — `firestarter_app/tests/test_revision_constants_parity.py:513,517` asserts
  *bidirectionally* that the firmware and host `FLAG_*` maxima are both exactly `0x100` and that
  there are exactly nine on each side. `uint16_t` suffices, and a future tenth flag above 0xFFFF
  would trip that gate first. ✅

### Consumers checked, one surface at a time

| Surface | Finding |
|---|---|
| **19 protocol comparisons / 45 `is_flag_set`** | Counts corrected — see C-5. |
| **Promotion / comparison semantics** | All comparisons are against unsigned constants ≤ 0x39; `uint8_t` promotes to `int`, so every `handle->protocol == PROTO_*` keeps identical truth. `is_flag_set` is `((handle->ctrl_flags & flag) == flag)` — `uint16_t & int` promotes to `int`; all nine flags fit in `int` on AVR (16-bit `int`, max flag 0x100). ✅ No semantic change. |
| **Format specifiers / log payloads** | `handle->protocol` reaches logging only via `LOG_ERROR_ID_U8(MSG_ERR_PROTOCOL_NOT_IMPLEMENTED, (uint8_t)handle->protocol)` at `not_implemented.cpp:17` and `eprom.cpp:87` — **already explicitly cast to `uint8_t`**, so the emitted byte is unchanged. `ctrl_flags` is never logged. The project's logging is id-and-typed-params (`LOG_ID_U8/U16/U24/U32`), not printf, so there are no format strings to desync. ✅ |
| **`sizeof` in a wire or EEPROM layout** | `sizeof(firestarter_handle_t)` appears in no wire frame and no EEPROM record. `rurp_configuration_t` (the EEPROM-persisted struct: `r1`, `r2`, `hardware_revision`) contains **neither** `protocol` nor `ctrl_flags`. ✅ **Not EEPROM-visible.** |
| **Wire visibility** | `handle->protocol` is written only by the `algorithm` key and read only for dispatch, for `eprom_params_for` / `eprom_block_budget_s`, and for the two `(uint8_t)`-cast error payloads. `handle->ctrl_flags` is written by `flags` and by two `= 0x80` verbose defaults (`firestarter.cpp:59`, `:134`) and read only by `is_flag_set`. **Neither is serialised into any response frame.** ✅ **Purely internal — the ROADMAP's "no wire change" claim holds.** |
| **Host protocol-parity constants** | `firestarter_app/firestarter/constants.py` duplicates the `FLAG_*` **values**, not the C field type. No constant moves. `test_revision_constants_parity.py` GREEN on the changed tree (MEASURED). ✅ |
| **`uint32_t` parameter signatures** | `eprom_params_for(uint32_t protocol)` (`include/eprom_params.h:79`) and `eprom_block_budget_s(uint32_t protocol, …)` (`include/eprom_budget.h:135`) keep 32-bit parameters. Call sites at `eprom.cpp:85,297,341` and `firestarter.cpp:242` now implicitly promote `uint8_t → uint32_t` — semantically identical, but the 4-byte compare survives *inside* those functions. Narrowing them is a **lead, not taken** (see Deferred ideas): it reaches `include/eprom_params.h`, `include/eprom_budget.h`, `src/proms/eprom_params.cpp`, `src/proms/eprom_budget.cpp` and the `native_params_v131` / `native_loop_v131` suites, and DECODE-04 does not ask for it. If a plan wants the extra bytes it must measure them separately. |
| **`configure_memory`'s if-chain** | Untouched (DECODE-07). `firestarter/CLAUDE.md` documents the dispatch order as a **line-for-line source-of-truth contract**; keeping the if-chain keeps that document valid with zero edits. If a plan ever took the `switch`, `CLAUDE.md` would need updating too — an extra reason the rejection is right. |

---

## DECODE-05 — the fail-closed hole (the safety criterion)

### Where the truncation happens, exactly

`json_parser.c:503-503`:
```c
bool get_algorithm(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle) {
    extract_long("algorithm", handle->protocol);
}
```
`extract_long` → `extract_num(element, register, simple_strtoul)` (`:284-292`) →
`register = simple_strtoul(...)`. `simple_strtoul` returns `unsigned long`. With
`protocol` as `uint32_t` there is no truncation. With `protocol` as `uint8_t`, `0x105` becomes
`0x05`. **`json_parser.c` applies no range check anywhere** — confirmed by reading the whole file.

### What `0x05` then does

`src/proms/memory.cpp:114`:
```c
if (handle->protocol == PROTO_FLASH_5V_PAGE || handle->protocol == PROTO_PHANTOM_0x35 ||
    handle->protocol == PROTO_PHANTOM_0x39) {
    configure_flash_5v_page(handle);
    return;
}
```
So a wire `algorithm: 261` dispatches into the **page-write flash handler** instead of reaching
the tail.

### The pre-narrowing fail-closed tail — what it actually does

`src/proms/memory.cpp:139-143`:
```c
// Generic fail-closed guard: every remaining protocol value — including
// protocol == 0 — is unrecognized and reaches not-implemented.
configure_not_implemented(handle);
```
`configure_not_implemented` (`src/proms/not_implemented.cpp:17`) emits
`MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` (**0xBB**) with `(uint8_t)handle->protocol` as its payload and
performs **zero hardware side effects** — no VPP regulator, no control-register write. That
zero-side-effect property is why the hole matters: `configure_flash_5v_page` is a 5 V path, but
the same truncation of e.g. `0x107` → `0x07` would reach `configure_eprom`, **which enables the
12 V/13 V VPP route**. The hazard class is the one `firestarter/CLAUDE.md`'s BLOCKER-2 note and
Phase 64's DISP-01 exist to prevent.

Note the pleasing detail: the error payload is **already** `(uint8_t)handle->protocol`, so today a
`0x105` command that reaches the tail already *reports* `0x05` — the truncation is visible in the
message but not in the dispatch.

### The blindness — PROVEN, not inherited

I applied the narrowing **with the saturation block deleted** and ran the suite:

```
$ pio test -e native
================ 172 test cases: 172 succeeded in 00:00:25.321 ================
```

**172/172 green against the broken tree.** Criterion 5's claim is confirmed experimentally at this
position. `[VERIFIED: pio test -e native on the probe tree, this session]`

### Per-field fail-closed analysis — saturate vs mask vs reject

`store_field`'s saturation sends an out-of-range value to the member's maximum. Whether that is
*fail-closed* is a per-field question, and the answers differ:

| field | width | saturated value | Is that fail-closed? | Today's behaviour on out-of-range | Verdict |
|---|---|---|---|---|---|
| **`protocol`** | 1 | `0xFF` | **YES.** 0xFF is in no dispatch arm (`memory.cpp:99-135`), so it reaches `configure_not_implemented` → 0xBB, zero side effects. It is also outside `eprom_params_for`'s table, whose `NULL` return is `configure_eprom`'s own refusal 1 (`eprom.cpp:85-90`). | no truncation (u32) | **SATURATE** ✅ |
| **`ctrl_flags`** | 2 | `0xFFFF` | **NO — actively dangerous.** Sets all nine flags incl. `FLAG_FORCE`, `FLAG_SKIP_ERASE`, `FLAG_SKIP_BLANK_CHECK`. | stores 0x10000, no flag set — harmless | **MASK** ⚠ (C-7 / F-1) |
| **`pins`** | 1 | `0xFF` (255) | **Weakly.** `mem_util_calculate_top_address_register` (`memory.cpp:199`) tests `pins < 32` → false, so 255 takes the *Rev-2-class preserve* arm; `pins == 28` (`:231`) → false; `memory_utils.h:76-78`'s `is_vpp_pin_present` rejects 255. Today's truncation of `256` → `0` takes the **opposite** arm (`0 < 32` true). So saturating is a **behaviour change**, in the safer direction for VPP-drop but not a refusal. | truncates | SATURATE, with the arm change **stated** |
| **`chip_id`** | 2 | `0xFFFF` | Yes-ish. A `0xFFFF` expectation cannot match a real device id, so `mem_util_report_chip_id` reports mismatch (warn or error per `warn_only`). | truncates | SATURATE |
| **`vpp_mv`** | 2 | `0xFFFF` (65535 mV) | **Weakly — a WARNING, not a refusal.** `eprom.cpp:713` / `flash_intel.cpp:39`: `measured > expected + 500` never fires; `:718` / `:44`: `measured < expected * 95/100` = 62262 always fires → `MSG_WARN_VPP_LOW`, `RESPONSE_CODE_WARNING`. The operation **proceeds**. Today's truncation can silently yield a *plausible* value (e.g. `0x12EE0` → 12000 mV). Saturation is strictly better but not a refusal. | truncates | SATURATE, ceiling **stated** |
| **`page_size`** | 2 | `0xFFFF` | **YES.** `eeprom28c_page_mask` (`eeprom_28c.cpp:628-636`) requires `requested <= AT28C_PAGE_SIZE_MAX && (requested & (requested-1)) == 0`; 0xFFFF fails both → silent `AT28C_PAGE_SIZE_FALLBACK`. Today's truncation of `0x10040` → `64`, a **valid** page size, is worse. | truncates | SATURATE ✅ |
| `mem_size`, `address`, `pulse_delay`, `read_settling_us`, `read_strobe_us` | 4 | n/a on AVR | no narrowing; `width == sizeof(unsigned long)` on AVR so the saturation branch is not taken | unchanged | unaffected |

**Recommendation:** *saturate* is the right default and is genuinely fail-closed for `protocol`
and `page_size`; *mask* is required for `ctrl_flags`; *reject* should be declined because it needs
a new message id (meta-repo `messages.toml` + codegen — out of scope for a firmware-only phase).
**Saturating and rejecting are different safety semantics and the plan must say which it chose and
why**; the criterion's own wording ("fail-closes rather than truncating") is satisfied by
saturation only because 0xFF happens to be unmapped — that is a *contingent* property of the
dispatch table and should be recorded as such, ideally pinned by a test that asserts 0xFF reaches
`configure_not_implemented`.

### ⚠ An AVR/native divergence that constrains the test

`simple_strtoul` returns `unsigned long`: **32-bit on AVR, 64-bit on native x86-64**. Therefore:

- `store_field`'s `if (width < sizeof(v))` is `width < 4` on AVR and `width < 8` on native — so on
  native the **4-byte** members saturate too, while on AVR they do not.
- Any test input ≥ 2³² behaves differently: AVR wraps inside `simple_strtoul` itself; native does
  not.

**Test-design rule: confine DECODE-05's cases to the narrow fields (`protocol`, `ctrl_flags`,
`pins`, `chip_id`, `vpp_mv`, `page_size`) and to input values < 2³².** Those saturate identically
on both. A case like `{"algorithm":261}` is safe; `{"memory-size":4294967296}` is not a valid
oracle. Consider making `store_field` take a `uint32_t` instead of `unsigned long` to remove the
divergence outright — measure the byte cost if so.

### The new test — specification

**Location:** `test/native/avr/test_read_timing/test_read_timing_params.cpp`. It is already inside
the `native` / `native_nodevtools` `test_filter`, already includes `json_parser.h` + `jsmn.h`,
already has a real `parse_json` helper calling `jsmn_parse` with the true `NUMBER_JSNM_TOKENS`
budget, and `configure_memory` is linkable from the same env (`+<proms/>`). No new env, no new
`-I` entry, no `platformio.ini` change. **This is the cheapest possible home.** (If the plan
prefers a dedicated suite it must add it to *both* `test_filter` lists and both `-I` lists in
lockstep — see the `[env:native_nodevtools]` comment — and it will still move the case count.)

**Cases (minimum):**

| # | Input | Assertion | Proves |
|---|---|---|---|
| S1 | `{"cmd":1,"algorithm":261}` | `h.protocol == 0xFF` | the saturation fires; 261 does **not** become 5 |
| S2 | as S1, then `configure_memory(&h)` | `h.response_code == RESPONSE_CODE_ERROR` **and** `h.firestarter_operation_main` is not `flash_5v_page`'s | the **dispatch** fail-closes, not merely the stored byte. This is the case that would have caught the defect. |
| S3 | `{"cmd":1,"algorithm":5}` | `h.protocol == 5`, and `configure_memory` still reaches `configure_flash_5v_page` | a non-regression guard so S1/S2 cannot be satisfied by breaking every algorithm |
| S4 | `{"cmd":2,"flags":65536}` | `h.ctrl_flags == 0` (mask) — **never** `0xFFFF` | C-7 / F-1: the bitmask must not fail open |
| S5 | `{"cmd":2,"page-size":65600}` | `h.page_size == 0xFFFF`, and `eeprom28c_page_mask` falls back | the truncation-to-a-valid-value hole |

S2 is the load-bearing one. Note the existing suite's `setUp` already stubs `Serial.write`/`flush`
so `LOG_ERROR_ID_*` on the refusal path will not abort.

**Anti-tautology check the plan must perform:** author S1/S2/S4 **RED first** against a probe tree
with the narrowing applied and the saturation/mask removed, capture the RED, then land the fix and
capture GREEN. I have already proven the RED direction is reachable (F-4: 172/172 green on the
broken tree means the *existing* suite cannot see it — so a new case that goes RED there is a real
oracle, not a tautology).

---

## DECODE-06 — the T-44-01 clamp survives

| Item | Location | Status |
|---|---|---|
| `#define READ_TIMING_MAX_US 1000UL` | `src/json_parser.c:47` | must be **hoisted** above the table (~`:68`). Confirmed necessary (C-9). |
| `get_read_settling` | `src/json_parser.c:362-369` | deleted; clamp moves to the table's `clamp` column |
| `get_read_strobe` | `src/json_parser.c:371-378` | deleted; same |
| Existing clamp test | `test/native/avr/test_read_timing/test_read_timing_params.cpp:121` `test_read_settling_us_capped_at_max` | **EXISTS** — sends 9999, asserts `<= 1000`. Verified still GREEN with the reference table applied. |
| Test for `read-strobe-us` cap | — | **DOES NOT EXIST** (C-8) |
| Local duplicate constant | `test_read_timing_params.cpp:46` | `#define READ_TIMING_MAX_US 1000UL` — a second, independent copy |

**What the plan must add:** a `read-strobe-us` cap case, and tighten both to `==` rather than
`<=` (so a "clamped to 0" regression is caught — 0 is the semantically loaded value for both
knobs: "no settling delay" / "use default 3 µs", `json_parser.c:348-350`). Optionally, remove the
test's local `#define` in favour of the production one now that it is hoisted — but only if
`json_parser.c`'s internals are reachable from the test, which they are not (it is a `.c` static
scope constant, not a header). Leaving the duplicate and *noting* the drift risk is the honest
option.

---

## DECODE-07 — the rejected `switch`, recorded

**This is a record-only requirement. No code changes.** The if-chain at `src/proms/memory.cpp:99-143`
stays exactly as it is.

**What discharges it:** a section in `.planning/v1.33/157-after-figures.md` (and a corresponding
line in the ROADMAP/REQUIREMENTS correction block) stating the alternative, its measurement, its
provenance, and its staleness.

**Should the +18 B be re-measured?** The absolute numbers (`uno` 25696 vs 25678) are **certainly
stale** — current `uno` is 24234 before and 23086 after this phase, so both figures are ~1.4–2.6 KB
off (C-10). Whether the *delta* still holds is unknown; gcc's choice between a jump table and a
comparison chain depends on value density (`0x05`–`0x39` over 18 values, i.e. ~31% density in a
53-wide span), which the narrowing changes (`switch` on `uint8_t` vs `uint32_t`).

**Recommendation: re-measure the delta.** It is cheap — one `sed` to convert the chain, three
`pio run`s, `git checkout` — perhaps 15 minutes, and it converts a stale third-party number into a
first-party one at the position where the decision actually applies. Record it as
`switch: <n> / if-chain: <m> / Δ +<k> B on uno, measured at 157's post-change position`, and
explicitly note that the original survey's 25696/25678 pair is superseded as absolutes while its
*direction* was independently reproduced (or not). If the plan declines to re-measure, it **must**
label the +18 B `[UNVERIFIED at this position]` and cite the survey as provenance — never restate
it as measured.

A second reason the rejection is right, which the criterion does not give: `firestarter/CLAUDE.md`
documents `configure_memory`'s dispatch order as a **line-for-line source-of-truth contract**
(§Protocol Dispatch, steps 1–7 plus 6a/6b). Converting to a `switch` would require rewriting that
section. The if-chain is not just cheaper; it is the shape the project's own documentation pins.

---

## The 999.35 / v1.28 overlap — named, as required

DECODE-01's field table is **superseded** if the binary command protocol ever lands. Backlog
**999.35** / milestone slot **v1.28** measures at **−3728 B flash / −512 B RAM on `leonardo`** and
would delete `lib/jsmn/` and `src/json_parser.c` outright. Therefore:

- The **−890 B** measured here and 999.35's **−3728 B** are **NOT additive**.
- 999.35 must be **re-measured from the post-v1.33 position** before anyone quotes a combined
  saving. `.planning/ROADMAP.md:4255` already carries this warning; Phase 157's own record must
  repeat it, because a reader of `157-after-figures.md` will not necessarily reach the backlog.
- **The operator ruled the binary protocol OUT of v1.33 on 2026-08-22.** Propose no step toward it.
  In particular: do **not** "prepare" the field table for a future binary frame, do not add a
  version/length prefix, and do not touch `NUMBER_JSNM_TOKENS` (Phase 158 / LAND-07 closes that
  lead as not-reducible).

---

## Gate blast radius — what goes RED, measured

### Host repo (`firestarter_app`) — the one that matters

Baseline at `38f0d83`, clean tree: **`pytest tests/` → 1976 passed / 0 failed / 0 skipped** in
241 s (32 syrupy snapshots passed). Matches the Phase 154 landing record exactly.

With the reference firmware change applied (see C-12 for the full triage):

| Leg | Verdict |
|---|---|
| `test_json_key_parity.py::test_page_size_key_string_matches_constants_py` | **REAL RED** if the table identifier changes. **GREEN if `key_parsers` is kept.** |
| `test_json_key_parity.py::test_every_dispatched_identifier_has_a_declared_key_string` | **SILENT FAIL-OPEN** on a rename. Never relied on again unless the identifier is kept. |
| `test_json_key_parity.py` — the two `test_planted_*` legs | Fail on a **dirty sibling firmware repo**. Run `pytest tests/` only **after** the firmware change is committed. |
| `test_revision_constants_parity.py` — all 9 legs | **GREEN.** Verified. |
| everything else | Not exercised by this change. `test_json_key_parity.py` and `test_revision_constants_parity.py` are the only two of the 15 `fw_path()`-using modules that scan `src/json_parser.c` or `include/firestarter.h`. |

The complete list of host modules that scan firmware source (`grep -rln "fw_path(" tests/`):
`fw_presence.py`, `test_cap03_ack_layout_parity.py`, `test_check_is_memory_cmd_no_ifdef.py`,
`test_check_no_log_in_sdp_window.py`, `test_dispatch_mirror.py`,
`test_erase_blank_step_nonregression.py`, `test_fw_presence.py`, `test_gen_validation_header.py`,
**`test_json_key_parity.py`**, `test_parse_gate_admission.py`, `test_py32_asset_name_host.py`,
`test_py32_flash_map_host.py`, **`test_revision_constants_parity.py`**,
`test_sdp_bus_config_drift.py`, `test_sdp_table_parity.py`. Their scan targets are enumerated in
`tests/scan_paths.py`; `src/json_parser.c` is registered at `scan_paths.py:133` with exactly one
consumer, `test_json_key_parity.py`. `test_dispatch_mirror.py` scans `doc/PROTOCOLS.md` and a
firmware **test** file, not `memory.cpp`, so DECODE-07's if-chain is not its business.
`test_parse_gate_admission.py` scans `src/firestarter.cpp` (the command-admission gate) — Phase 157
does not touch that file. `[VERIFIED: pytest runs before and after, this session]`

### Firmware repo

| Leg | Verdict |
|---|---|
| `pio run -e uno / uno328pb / leonardo` | GREEN, **0 warnings on all three** with the change. The warnings gate's AVR rule is `== 0` (`size_baseline.json` → `warnings.policy.avr_rule`), so this is not slack. |
| `pio test -e native` | 172/172 with the change. Will move to 172+N once DECODE-05/06 cases land. |
| `pio test -e native_nodevtools` | 172/172 at baseline. Must be re-run — the two envs must stay in lockstep. |
| `scripts/check_build_warnings.py` | **UNVERIFIED** — not run this session. Native watermark is **1166** macro-redefinitions with `<=` policy and (per project memory) ~zero headroom. New test cases in an existing suite are unlikely to add redefinitions, but the plan must run it. |
| `scripts/check_no_heap_or_64bit_symbols.py` | Should stay GREEN (Phase 157 adds no `malloc`, no 64-bit arithmetic — `1UL << (width*8)` is 32-bit on AVR). **UNVERIFIED** — run it. |
| `check_size_baseline.py` default mode | Already RED on `flash_used` byte-identity (Phases 155/156). Will gain a `cases` line. Phase 158 / LAND-01 owns the re-record. |
| `check_size_baseline.py --policy merge05 --baseline …base01.json` | RED **only** on the two native `cases` lines (MEASURED, F-6). Flash and RAM legs pass and are informative. **Record the pass as one-sided (D-03).** |
| `firestarter/tests/golden/protocol_branch_inventory.json` (host module `test_protocol_branch_inventory.py`) | Pins `src/proms/eprom.cpp` by blob SHA and branch inventory. Phase 157 touches neither `eprom.cpp` nor `memory.cpp` → **GREEN**. This was Phase 156's main red; it is **not** Phase 157's. |
| `tests/test_checker_convention.py::test_scope_is_firmware_only` | Hard-codes the directory name `firestarter`. **Any throwaway worktree must be named `firestarter`** (e.g. `/tmp/probe/firestarter`) or this fails spuriously. Carried forward from Phase 156's research. |

---

## Project Constraints (from CLAUDE.md)

From `/workspaces/CLAUDE.md` and `/workspaces/firestarter/CLAUDE.md`:

| Directive | Bearing on Phase 157 |
|---|---|
| Meta repo tracks only `.planning/` and `.claude/`; sub-repos are not committed here | All source edits are committed **inside** `firestarter/`, on `gsd/v1.33-source-hygiene-firmware-size-reduction`. |
| "**Serial protocol changes** must be kept in sync between `serial_comm.py` and `firestarter.cpp`" | **Not triggered.** No frame, payload or message id changes. `handle->protocol` / `ctrl_flags` are never serialised (verified — §DECODE-04). |
| "**Constants/flag bits** are duplicated between `constants.py` and `firestarter.h`. Change both together" | **Not triggered.** No `#define` is added, removed or renumbered. `test_revision_constants_parity.py` GREEN (verified). |
| ⚠ **The wire-key parity gate** — `constants.py:151,163` names `json_parser.c` (`key_read_settling`, `key_read_strobe`, `key_page_size`) as a "Firmware sync" surface, enforced by `test_json_key_parity.py` | **TRIGGERED, and the ROADMAP does not anticipate it.** See F-2 / C-12. Keep the `key_parsers` identifier and this stays a zero-edit surface. |
| `include/messages.h` is **codegen-generated — DO NOT EDIT**; edit `tools/catalog/messages.toml` in the **meta** repo and regenerate | **Not touched, by design.** This is the decisive argument against "reject the command" semantics for out-of-range fields (C-7): a rejection needs a new id, which needs meta-repo codegen, which breaks the firmware-only property. |
| Dispatch reads named `PROTO_*` constants; `protocol` is the sole algorithm axis (GATE-01, TABLE-05); `configure_memory`'s order is a **line-for-line source-of-truth** | Untouched. DECODE-07 keeps the if-chain; `CLAUDE.md` needs no edit. |
| Build commands: `pio run -e {uno,uno328pb,leonardo}`, `pio test -e native` | Used as-is. **All three** AVR targets must be measured, and both native envs run. |
| Board differences: Uno 512 B buffer, Leonardo 1024 B | `sizeof(firestarter_handle_t)` differs per target; the `offsetof`-derived table is correct on both without a per-target branch. |
| Never work on `beta`/`main`; nothing is pushed by an executor | Milestone branch only. Pushing is the operator's call. |

### Project skills

`/workspaces/.claude/skills/` carries `devtest-rootcause`, `devtest-triage`, `find-skills`,
`skill-creator`, plus the GSD clusters. **None applies** — this is a pure firmware refactor with no
chip-validation, database, datasheet or issue-triage surface. There are no `rules/*.md` files. No
project skill pattern constrains this phase.

### Knowledge graph

`.planning/graphs/graph.json` exists (23.8 MB) but is dated **2026-07-01** — roughly seven weeks
and three milestones stale. I deliberately did **not** query it: every relationship it could
suggest about `json_parser.c` predates Phase 154's sweep, so its line anchors are wrong by
construction and its file relationships predate two of this milestone's own phases. Direct
measurement replaced it. **The plan should not query it either without a `graphify` rebuild.**

---

## Standard Stack

There are **no new dependencies**. This phase is a pure-C refactor inside an existing PlatformIO
project.

### Core (already present, versions verified this session)

| Component | Version | Purpose | Why standard |
|---|---|---|---|
| PlatformIO Core | **6.1.19** (`pio --version`) | build/test orchestration | the project's only build system |
| `platform-atmelavr` | 5.1.0 | AVR platform | pinned by `platformio.ini` |
| `toolchain-atmelavr` (avr-gcc) | **1.70300.191015 → gcc 7.3.0** | compiler | fixes `_Static_assert` availability (C11, gcc ≥ 4.6) and the inlining behaviour the whole measurement rests on |
| `framework-arduino-avr` | 5.3.0 | Arduino core | |
| `jsmn` (vendored, `lib/jsmn/`) | vendored | JSON tokenizer | untouched by this phase |
| Unity (via PlatformIO `test_framework = unity`) | bundled | native test framework | 17-suite `test_filter` on both native envs |
| ArduinoFake | `fabiobatsilva/ArduinoFake@^0.4.0` | native Arduino stubs | already a `lib_deps` of every native env |

### Supporting (measurement tools, all already installed)

| Tool | Path | Use |
|---|---|---|
| `avr-nm` | `~/.platformio/packages/toolchain-atmelavr/bin/avr-nm` | per-symbol size ledger. **Not on `PATH`** — must be invoked by full path. |
| `avr-objdump` | same dir | section headers, disassembly |
| `avr-gcc` | same dir | the offset-probe TU technique in §Measured figures |
| `strings` | system | the DECODE-02 key-duplication oracle |
| `patch`, `git apply --3way` | system | reference-patch application |

### Alternatives considered

| Instead of | Could use | Tradeoff |
|---|---|---|
| `_Static_assert` in C | `typedef char x[cond ? 1 : -1]` negative-array trick | Works pre-C11 and works *inside an initializer* — which is exactly what C-14's per-field variant needs. Use `_Static_assert` at file scope where possible and the trick inside `FIELD()`. |
| a 6-byte PROGMEM row with a `uint16_t clamp` | a `uint32_t clamp` (8-byte row) | +22 B PROGMEM for range no clamp needs — `READ_TIMING_MAX_US` is 1000. Reject. |
| `memcpy` of the low `width` bytes | a `switch (width)` with typed stores | measurably worse on AVR (a jump table plus three stores) and no more portable, since the endianness assumption is identical. Reject. |
| `offsetof`-derived offsets | hand-written offsets | hand-written offsets are **wrong on native** (different alignment — see §struct offsets). This is not a style preference; it is a correctness requirement. |

## Package Legitimacy Audit

**Not applicable.** This phase installs **zero** external packages. No `npm install`, no
`pip install`, no `platformio lib install`, no `lib_deps` change. Every tool and library it uses is
already vendored or already pinned in `platformio.ini` at a version verified in this session.
No package-legitimacy check was required and none was run.

**Packages removed due to a `[SLOP]` verdict:** none.
**Packages flagged as suspicious `[SUS]`:** none.

---

## Architecture Patterns

### System architecture — how a wire key becomes a handle field, before and after

```
  HOST (firestarter_app)                    FIRMWARE (firestarter)
  ─────────────────────                     ──────────────────────

  eprom_operations.py                       firestarter.cpp
    builds {"cmd":N,"algorithm":7,   ──►      jsmn_parse(...)  ── static jsmntok_t tokens[64]
            "flags":128, ...}                       │
    over COBS @250000 baud                          ▼
                                            json_get_cmd()  ── get_cmd + get_flags (direct)
                                                    │
                                                    ▼
                                            json_parse()
                                                    │
                                    ┌───────────────┴──────────────────┐
                                    │                                  │
                       ┌────────────▼───────────┐        ┌─────────────▼────────────┐
                       │  BEFORE (today)        │        │  AFTER (Phase 157)       │
                       │                        │        │                          │
                       │  for row in            │        │  for row in              │
                       │    key_parsers[11]:    │        │    key_parsers[11]:      │
                       │      jsoneq_(key)  ◄─┐ │        │      jsoneq_(key)        │
                       │        │             │ │        │        │                 │
                       │        ▼             │ │        │        ▼                 │
                       │  pgm_read_ptr(fn)    │ │        │  store_field(handle,row, │
                       │        │             │ │        │     simple_strtoul(v))   │
                       │        ▼      OPAQUE │ │        │        │  (INLINED)      │
                       │  get_xxx() ──────────┘ │        │        ├─ clamp?         │
                       │    jsoneq_(SAME key)   │        │        ├─ saturate/mask  │
                       │    strtoul + store     │        │        └─ memcpy(width)  │
                       │    ── 84..110 B each   │        │     ── 0 B (inlined)     │
                       └────────────┬───────────┘        └─────────────┬────────────┘
                                    │                                  │
                                    └───────────────┬──────────────────┘
                                                    ▼
                                          firestarter_handle_t
                                            .protocol   u32 → u8    ◄── the narrowing
                                            .ctrl_flags u32 → u16
                                                    │
                     ┌──────────────────────────────┼──────────────────────────────┐
                     ▼                              ▼                              ▼
        memory.cpp configure_memory()     is_flag_set(FLAG_*)          eprom_params_for(u32)
          17 `protocol ==` compares        40 call sites in src/        (signature unchanged;
          + fail-closed tail               (+19 via LOG_INFO_ID*)        u8 promotes)
                     │
        ┌────────────┴──────────────┐
        ▼                           ▼
  configure_<family>()      configure_not_implemented()
   (may enable 12/13 V)      0xBB, ZERO side effects  ◄── the fail-closed backstop
                                                          a truncated 0x105→0x05 BYPASSES

  ══════ CROSS-REPO GATE (scans firmware source text, not behaviour) ══════
  firestarter_app/tests/test_json_key_parity.py
     regex  `key_parsers\[\]\s*PROGMEM\s*=\s*\{ … \};`   ◄── breaks on a rename (F-2)
     regex  `const char (\w+)[] PROGMEM = "…";`          ◄── survives
```

### Pattern 1 — replace an opaque dispatch with a data descriptor

**What:** when a table of `{key, function pointer}` dispatches to N structurally identical
functions, replace it with `{key, <the data those functions differ in>}` plus one shared body.
**When to use:** when the functions differ only in *which field they write* and *what bound they
apply* — i.e. when the difference is data, not logic.
**Why it wins here:** a PROGMEM function pointer is an optimisation barrier. The 1012 B vs 0 B
comparison between the eleven table stubs and the five direct-call siblings is a *controlled
experiment* the codebase performed on itself.
**Counter-indication:** if any one function had real divergent logic, this pattern forces it into a
flag column and the table stops being a description. Here exactly two of eleven diverge (the two
read-timing clamps) and one column absorbs both — that is the signal the pattern fits.

### Pattern 2 — derive width from the member, never from a literal

```c
#define FIELD(k, member, cl)                                        \
    { k, (uint8_t)offsetof(firestarter_handle_t, member),           \
      (uint8_t)sizeof(((firestarter_handle_t*)0)->member), (cl) }
```
`sizeof(((T*)0)->member)` needs no instance and no C11 feature. This is not stylistic: hand-written
offsets would be **wrong on native** (see §struct offsets — every field from `protocol` down
differs between AVR and x86-64), so the whole table would be untestable natively.

### Pattern 3 — validate at the parse boundary, once, for every field

The per-stub form could not share a bound check because each stub was its own function. One
`store_field` gives every narrow field a single validation site. **But the *semantic* must be
per-field** (saturate for ordinals, mask for bitmasks — C-7), so the table needs a column for it.
"One site, per-row policy" is the shape; "one site, one global policy" is the bug.

### Pattern 4 — prove a compiler-dependent claim by measurement, per target

DECODE-02's "appears once in flash" and DECODE-01's byte figures are **toolchain outcomes**, not
source properties. Every such claim in the phase record must carry the target it was measured on
and be measured on all three. The `flags` duplicate vanishing without a source change (§DECODE-02)
is the cautionary case: a claim that reads like a source property was actually a link-time one.

### Anti-patterns to avoid

- **Saturating a bitmask.** C-7. `0xFFFF` is not "the largest flags value"; it is "every flag on".
- **Asserting one offset and calling it a reorder guard.** C-14.
- **Counting ELF strings with an exact-match filter.** C-3 — `strings` glues the preceding byte on.
- **Re-applying the whole composed patch.** C-11 — it carries Phases 155/156, already landed.
- **Hard-coding a struct offset in a test.** Wrong on one of the two architectures.
- **Quoting the ROADMAP's `−976 / −172` split, `19`, `45`, `ten of eleven`, `3440 B`, or
  `25696/25678`.** All corrected (C-2…C-5, C-10, C-13).
- **Running `pytest tests/` on a dirty firmware sibling.** Two legs assert sibling porcelain.
- **Pinning a `.constprop.NN` suffix.** `get_flags.constprop.33` and `get_cmd.constprop.32` are
  gcc-assigned and moved between the before and after trees (`.31` → `.32`). Phase 156's C-5
  established this rule; it applies here too.

---

## Don't Hand-Roll

| Problem | Don't build | Use instead | Why |
|---|---|---|---|
| Field offsets in the table | a hand-maintained offset list | `offsetof()` from `<stddef.h>` | wrong on native vs AVR; silent |
| Field widths in the table | a literal `1`/`2`/`4` column | `sizeof(((firestarter_handle_t*)0)->member)` | this **is** DECODE-03 |
| Compile-time struct guard | a runtime `if (offset > 255) return;` | `_Static_assert` (verified available on all four envs) | a runtime check costs flash and fires in the field instead of at build time |
| Byte-width store | a `switch (width)` with typed stores | `memcpy(dst, &v, width)` | smaller on AVR, and gcc lowers a constant-width `memcpy` to plain stores |
| String→integer | a new parser | the existing `simple_strtoul` (`json_parser.c:30`) | already there, 68 B, unchanged by this phase. **Do not** reach for avr-libc `strtoul` — that is exactly the kind of library pull-in Phase 155 spent a phase removing. |
| Size measurement | eyeballing `pio run` output | `scripts/check_size_baseline.py --rebuild` + `avr-nm --print-size --size-sort` | the project already owns both, and the gate encodes MERGE-05's bands |
| Key-duplication proof | reading the source and asserting | `strings -a -n 2 -t d` on the ELF, offset-resolved | the duplicate is a *link-time* artifact; source inspection cannot see it |
| Out-of-range refusal reporting | a new message id | the existing `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` (0xBB) reached via saturation | a new id means meta-repo `messages.toml` + codegen, breaking firmware-only |

**Key insight:** every quantity this phase asserts is a *compiler or linker outcome*, not a source
fact. The project's own tooling (`avr-nm`, `check_size_baseline.py`, `strings`) already measures
all of them. Reasoning about avr-gcc's inlining from source is precisely the error that left the
half-done refactor in place for as long as it stood.

---

## Runtime State Inventory

Phase 157 is **not** a rename/refactor of persisted identifiers, but it *does* narrow two fields of
a struct, so the persistence question is live and is answered explicitly rather than skipped.

| Category | Items found | Action required |
|---|---|---|
| **Stored data** | **None.** `handle->protocol` and `handle->ctrl_flags` are never persisted. The only persisted firmware struct is `rurp_configuration_t` (AVR EEPROM: `r1`, `r2`, `hardware_revision`) and it contains neither field. `chip_database.json` stores `programming.algorithm` as an integer on the **host** side; the wire value is unchanged. Verified by grep over `src/`, `include/` and the struct definition. | none |
| **Live service config** | **None.** No external service holds a copy of these field widths. | none |
| **OS-registered state** | **None.** No task, service or launch agent references them. | none |
| **Secrets / env vars** | **None.** | none |
| **Build artifacts / installed packages** | **`.pio/build/{uno,uno328pb,leonardo,native,native_nodevtools}`** hold object files compiled against the old `firestarter.h`. PlatformIO's dependency tracking handles a header change correctly (verified — the incremental rebuild after editing `firestarter.h` produced the expected new figures), **but Phase 158's LAND-01 cold-build convention (`rm -rf .pio/build/<env>` then exactly one `pio run -e <env>`) is the right thing for any figure that goes into a record.** Every figure in this document is WARM; state that. | cold-rebuild before recording final figures |
| **Flashed devices** | Any bench board carrying pre-157 firmware has the old struct layout. Irrelevant: the layout is not wire-visible and no bench criterion exists (D-02). | none |

**The canonical question, answered:** after every file in the repo is updated, the only runtime
system holding the old field widths is a **flashed board**, and the change is invisible across the
wire, so nothing needs migrating. There is **no data migration** in this phase — only code edits.

---

## Common Pitfalls

### Pitfall 1 — the reference patch's hunk #3 fails, and the failure looks bigger than it is
Only **one** of seven `json_parser.c` hunks fails, and only because Phase 154's sweep removed two
comment lines. `git apply --3way` produces exactly one conflict region. Do not conclude the patch
is unusable. (C-11)

### Pitfall 2 — cherry-picking from the wrong ref
The ROADMAP's `## v1.33` entry names `size-reduction-survey`. That branch does **not** carry the
work. Use `wip/v1.33-size-reduction-survey-preserved` @ `a6b46f8`, or the patch.

### Pitfall 3 — ⚠ saturating `ctrl_flags`
The single most dangerous thing a plan can copy verbatim from the reference. See C-7 / F-1.

### Pitfall 4 — renaming `key_parsers[]`
Silently breaks a cross-repo gate one way and turns a sibling leg fail-open the other. Keep the
identifier. (C-12 / F-2)

### Pitfall 5 — running `pytest tests/` on a dirty firmware sibling
`test_json_key_parity.py:491` asserts `_git_porcelain(FW_ROOT) == ""`. Two legs fail on any
uncommitted firmware change, including untracked `.orig`/`.rej` files left by `patch`. **Commit the
firmware change first, and delete `.rej`/`.orig` files.**

### Pitfall 6 — adding a native case to `native` / `native_nodevtools`
Moves the case count off 172 and reddens both baseline gates' count legs. Expected, not a defect —
but it must be **recorded as a handoff to LAND-01**, and both envs must be re-run so the counts
stay in lockstep. (C-15)

### Pitfall 7 — trusting `grep -c "RUN_TEST("`
Lexical count across the 17 filtered suites is **173**; the runner reports **172**. Trust the
runner.

### Pitfall 8 — a throwaway worktree named anything but `firestarter`
`tests/test_checker_convention.py::test_scope_is_firmware_only` hard-codes the directory name. Use
`/tmp/probe/firestarter`.

### Pitfall 9 — `avr-nm` / `avr-objdump` are not on `PATH`
`~/.platformio/packages/toolchain-atmelavr/bin/avr-{nm,objdump,gcc}`. Invoke by full path.

### Pitfall 10 — the native suite is load-flaky (D-04)
Three 172/172 runs this session took 19.8 s, 25.3 s and 54.6 s. Duration varied 2.8×; the result
did not. Never attribute a failure to the change on N=1.

### Pitfall 11 — counting ELF strings with an exact-match filter
`awk '$2=="flags"'` reports 1 where the truth is 2, because `strings` emits `Uflags`. `grep -c` on
`leonardo` reports 4. Use an offset-resolved block dump. (C-3)

### Pitfall 12 — assuming `unsigned long` is 32-bit
It is on AVR; it is **64-bit** on native. `store_field`'s `width < sizeof(v)` guard therefore
behaves differently, and any test input ≥ 2³² is not a valid cross-architecture oracle. Confine
DECODE-05's cases to narrow fields and values < 2³², or change `store_field` to take `uint32_t`.

### Pitfall 13 — pinning a `.constprop.NN` suffix
`get_cmd.constprop.31` before, `.32` after. Never assert one.

### Pitfall 14 — quoting a WARM figure as a cold baseline
Every figure in this document is warm-incremental. `size_baseline.json`'s own documented convention
is cold (`rm -rf .pio/build/<env>` then one `pio run`). Final record figures must be cold.

### Pitfall 15 — reading a green `--policy merge05` run as "nothing moved"
It is **one-sided** (`:697`, `:709`). D-03 requires the pass be recorded as one-sided.

### Pitfall 16 — writing a `json_parser.c:NNN` citation from a pre-Phase-154 document
`json_parser.c` lost 198 of 198 citations in the sweep. Every citation in this document was
re-measured. Any citation the plan copies from an older `.planning/` file must be re-verified or
discarded. And this document's own citations will be remapped by Phase 159 — that is expected, not
a defect (D-05).

### Pitfall 17 — believing an existing parity test is an oracle without auditing it
The project has at least one tautological "parity" test (`MAX_27C020_SIZE`, `@requires_fw` against
a `#define` that does not exist). I audited the two tests this phase depends on:
`test_read_settling_us_capped_at_max` is **non-vacuous** (it would go RED if the clamp were
deleted — the input 9999 exceeds the bound), and `test_json_key_parity.py`'s dispatch leg is
**vacuous after a rename** (C-12). Do not extend that trust to any other parity test without the
same audit.

---

## Code Examples

All commands below were **run in this session** unless marked otherwise.

### Extracting only this phase's hunks from the composed patch

```bash
cd /workspaces/firestarter
P=/workspaces/.planning/notes/firmware-size-reduction-measured.patch
sed -n '1,30p'   "$P" > /tmp/157-hdr.patch     # include/firestarter.h  (hunks 1,2 apply; 3 is Phase 155)
sed -n '98,311p' "$P" > /tmp/157-json.patch    # src/json_parser.c      (hunk 3 FAILS -- Phase 154 swept its context)

patch -p1 --no-backup-if-mismatch < /tmp/157-hdr.patch   # expect: "Hunk #3 FAILED at 223"
rm -f include/firestarter.h.rej include/firestarter.h.orig
git apply --3way /tmp/157-json.patch                     # expect: "Applied ... with conflicts"
grep -n '<<<<<<<\|=======\|>>>>>>>' src/json_parser.c    # one region; resolve by taking "theirs"
```

### Measuring the phase delta, all three targets

```bash
cd /workspaces/firestarter
for e in uno uno328pb leonardo; do
  printf '%-10s ' "$e"
  pio run -e $e 2>&1 | grep -E 'RAM:|Flash:' | tr '\n' ' '; echo
done
# before (1151dc4): uno 24234/1567  uno328pb 24282/1573  leonardo 26378/2008
# after            : uno 23086/1562  uno328pb 23134/1568  leonardo 25230/2003
# For a RECORD figure, do it cold:  rm -rf .pio/build/$e && pio run -e $e
```

### DECODE-01's mechanical criterion: the eleven-stub ledger

```bash
NM=~/.platformio/packages/toolchain-atmelavr/bin/avr-nm
$NM --print-size --size-sort --radix=d .pio/build/uno/firestarter_uno.elf \
  | grep -iE ' t ' | grep -E 'get_|key_parser|FIELDS|store_field|jsoneq|simple_strtoul'
# BEFORE: eleven get_* summing to exactly 1012; key_parsers 44
# AFTER : no get_* except get_flags.constprop.NN (82) and get_cmd.constprop.NN (102);
#         FIELDS 66; store_field ABSENT (inlined)
# The five siblings (get_r1/r2/rev/rw_pin/vpp_pin) are ABSENT in BOTH -> 0 B, the criterion's proof.
```

### DECODE-02's oracle: offset-resolved key-string blocks

```bash
# vaddr = file offset - 148 (.text starts at file offset 0x94)
strings -a -n 2 -t d .pio/build/uno/firestarter_uno.elf | awk '$1>=200 && $1<=560'
# BEFORE: TWO 118 B blocks -- vaddr 104-221 (named key_*) and 226-343 (stub PSTR duplicates)
# AFTER : ONE block, vaddr 104-221. Eleven keys, eleven copies.
# Cross-check the first block against the symbol table:
NM=~/.platformio/packages/toolchain-atmelavr/bin/avr-nm
$NM --print-size --radix=d .pio/build/uno/firestarter_uno.elf | grep -E ' key_' | sort -n
# DO NOT use:  strings -a -t d <elf> | awk '$2=="flags"'    <- reports 1, truth is 2 ("Uflags")
# DO NOT use:  strings -a <elf> | grep -c flags             <- reports 4 on leonardo
# Repeat on all three ELFs: this is a link-time property, not a source property.
```

### DECODE-03's struct offsets, both architectures

```bash
cat > /tmp/off.c <<'EOF'
#include <stddef.h>
#include "firestarter.h"
#define P(m) char off_##m[offsetof(firestarter_handle_t, m)+1];
P(cmd) P(operation_state) P(response_code) P(protocol) P(pins) P(mem_size)
P(address) P(vpp_mv) P(pulse_delay) P(read_settling_us) P(read_strobe_us)
P(ctrl_flags) P(chip_id) P(page_size) P(data_buffer) P(data_size) P(bus_config)
char total[sizeof(firestarter_handle_t)];
EOF
D='-DDATA_BUFFER_SIZE=512 -DMONITOR_SPEED=250000 -DHARDWARE_REVISION -DDEV_TOOLS -DRURP_BOARD_NAME="x"'
GCC=~/.platformio/packages/toolchain-atmelavr/bin/avr-gcc
NM=~/.platformio/packages/toolchain-atmelavr/bin/avr-nm
$GCC -mmcu=atmega328p $D -I include -c /tmp/off.c -o /tmp/off.o
$NM --print-size --radix=d /tmp/off.o | awk '{printf "%s %s\n",$2-1,$4}' | sed 's/off_//' | sort -n
# AVR before: protocol 3 ... page_size 36, data_buffer 38, sizeof 600
# AVR after : protocol 3 ... page_size 31, data_buffer 33, sizeof 595   (-5 B)
gcc $D -I include -c /tmp/off.c -o /tmp/offn.o && nm --print-size --radix=d /tmp/offn.o | ...
# native sizeof is 655 BOTH ways -- the -5 B is AVR-only. Do NOT assert it natively.
```

### Proving the suite is blind (F-4) — the RED-first probe

```bash
# Apply the narrowing, then DELETE the saturation block from store_field:
python3 - <<'EOF'
p='src/json_parser.c'; s=open(p).read()
old="""    if (width < sizeof(v)) {
        unsigned long max = (1UL << (width * 8)) - 1UL;
        if (v > max) {
            v = max;
        }
    }
"""
assert old in s
open(p,'w').write(s.replace(old,""))
EOF
pio test -e native
# ==> 172 test cases: 172 succeeded.  The suite CANNOT see the hole.
# That is the RED baseline the new DECODE-05 cases must go RED against.
```

### Running the size gate, and reading its one-sidedness

```bash
cd /workspaces/firestarter
python3 scripts/check_size_baseline.py --policy merge05 \
    --baseline scripts/baseline/size_baseline_base01.json --rebuild
# At 1151dc4 this prints EXACTLY:
#   FAIL:
#     native: cases baseline=141 observed=172
#     native_nodevtools: cases baseline=141 observed=172
# No AVR flash or RAM line -> the pre-existing RED masks NOTHING (F-6).
# :697 `if flash_delta > allowance` and :709 `if ram_delta > ram_tolerance` are GROWTH-ONLY,
# so a reduction passes with no named exemption (D-03). Record the pass AS one-sided.
```

### Confirming the host blast radius (run only on a COMMITTED firmware tree)

```bash
cd /workspaces/firestarter_app
python3 -m pytest tests/test_json_key_parity.py tests/test_revision_constants_parity.py \
    -q -o addopts=""
# baseline (unchanged firmware): 24 passed
# with key_parsers[] RENAMED   : 1 real RED (test_page_size_key_string_matches_constants_py)
#                                + 1 SILENT FAIL-OPEN (test_every_dispatched_identifier_...)
# with the identifier KEPT     : 24 passed  <- the recommended outcome
python3 -m pytest tests/ -q -o addopts=""      # full suite baseline: 1976 passed / 0 failed / 0 skipped
```

### Verifying no CI runs the size gate (LAND-04, re-confirmed)

```bash
cd /workspaces/firestarter
grep -rn check_size_baseline .github/ || echo "NONE in .github/"    # prints NONE
grep -rn 'pio test' .github/workflows/
#   build.yml:142  pio test -e native
#   build.yml:155  pio test -e native_nodevtools
#   beta-build.yml:122,128  same two
```

---

## Environment Availability

| Dependency | Required by | Available | Version | Fallback |
|---|---|---|---|---|
| PlatformIO Core | every build and native test | ✓ | 6.1.19 (`/usr/local/bin/pio`) | — |
| `platform-atmelavr` + `toolchain-atmelavr` | the three AVR builds | ✓ | 5.1.0 / gcc **7.3.0** | — |
| `framework-arduino-avr` | AVR builds | ✓ | 5.3.0 | — |
| `avr-nm` / `avr-objdump` / `avr-gcc` | the symbol ledger, the offset probe | ✓ | in `~/.platformio/packages/toolchain-atmelavr/bin/` | **not on `PATH`** — use full paths |
| host `gcc` + `nm` | native offsets, `[env:native]` | ✓ | system | — |
| ArduinoFake | both native envs | ✓ | 0.4.0 (cached) | — |
| Unity | both native envs | ✓ | PlatformIO-bundled | — |
| `strings` (binutils) | DECODE-02's oracle | ✓ | system | `avr-objdump -s` |
| `patch` / `git apply` | reference-patch application | ✓ | system | hand-transcribe |
| Python 3 + `pytest` for `firestarter_app` | host gate legs | ✓ | editable install resolves to `/workspaces/firestarter_app/firestarter/__init__.py`; full suite 1976 passed in 241 s | ⚠ CI runs **Python 3.11 only**; the devcontainer default is 3.12. This phase adds **no** host code, so the divergence is not load-bearing here — but if a host edit becomes necessary (F-2 option b), run it under `uv venv --python 3.11`. |
| sibling firmware checkout at `../firestarter` | every `@requires_fw` host leg | ✓ | `/workspaces/firestarter` | absent → the legs **skip**, which would silently hide F-2 |
| Physical RURP board | — | ✗ | — | **Not needed.** D-02: no criterion in this milestone requires silicon. |
| `graphify` graph | optional context | ⚠ stale | `.planning/graphs/graph.json` dated 2026-07-01 | do not query without a rebuild |

**Missing dependencies with no fallback:** none.
**Missing dependencies with a fallback:** none blocking. The two watch-items are the `PATH` gap for
the AVR binutils (use full paths) and the stale graph (ignore it).

---

## Validation Architecture

`.planning/config.json` does not set `workflow.nyquist_validation`, so it is **enabled** by
default. This section is required for the planner to produce `VALIDATION.md`.

### Test framework

| Property | Value |
|---|---|
| Framework | **Unity**, via PlatformIO `test_framework = unity` (`platformio.ini`), plus **ArduinoFake 0.4.0** for Arduino stubs |
| Config file | `platformio.ini` — `[env:native]` and `[env:native_nodevtools]`, each with a **17-entry `test_filter`** and a matching 17-entry `-I` list that must stay in lockstep |
| Production TUs compiled into the native envs | `build_src_filter = +<proms/> +<boards/rurp_serial_utils.cpp> +<json_parser.c> +<operation_utils.cpp>` — **`src/json_parser.c` is IN** (Phase 44 Plan 02), and so is `src/proms/memory.cpp` via `+<proms/>` |
| Quick run command | `pio test -e native -f "*test_read_timing*"` (the suite this phase extends) |
| Full suite command | `pio test -e native && pio test -e native_nodevtools` |
| Host gate command | `cd /workspaces/firestarter_app && python3 -m pytest tests/ -q -o addopts=""` (run only on a committed firmware tree) |
| Build gate | `pio run -e uno && pio run -e uno328pb && pio run -e leonardo` — AVR warning policy is `== 0` |
| Size gate | `python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json --rebuild` — **local-run only, in no CI workflow** |

### Measured baselines, today, at `1151dc4` on a clean tree

| Leg | Baseline |
|---|---|
| `pio test -e native` | **172 cases / 17 suites / 172 succeeded** (19.8 s) |
| `pio test -e native_nodevtools` | **172 / 17 / 172** (29.9 s) |
| `pytest tests/` (host) | **1976 passed / 0 failed / 0 skipped** (241 s), 32 syrupy snapshots |
| AVR warnings | 0 / 0 / 0 |
| `test_read_timing` cases | 9 (`RUN_TEST` at `:185-193`) |
| `size_baseline.json` `native.cases` | 172 |
| `size_baseline_base01.json` `native.cases` | 141 (frozen at Phase 124 — LAND-03's pre-existing red) |

### Phase requirements → test map

| Req | Behaviour | Test type | Automated command | File exists? |
|---|---|---|---|---|
| **DECODE-01** | the eleven stubs and `key_parsers`' function-pointer column are gone; the five siblings still cost zero | build + symbol ledger | `avr-nm --print-size --size-sort --radix=d .pio/build/uno/firestarter_uno.elf \| grep -E 'get_\|FIELDS\|key_parsers'` | ✅ tool exists; **the assertion is a record, not a test** — no automated gate pins symbol names. Ceiling. |
| **DECODE-01** | −890 B (table) and −1148 B (total) on all three targets | build measurement | `for e in uno uno328pb leonardo; do pio run -e $e; done` | ✅ |
| **DECODE-02** | every wire key appears once in flash, on all three targets | ELF string-block diff | `strings -a -n 2 -t d <elf> \| awk '$1>=200 && $1<=560'` | ✅ tool exists; **record, not a gate** |
| **DECODE-02** | `get_flags` is still a real function, called from `json_parse_config` and `json_get_cmd` | source + symbol | `grep -rn get_flags src/` + `avr-nm \| grep get_flags` | ✅ |
| **DECODE-03** | `width` derives from the member; a reorder cannot truncate an offset | **compile-time** | `pio run -e uno && pio run -e uno328pb && pio run -e leonardo && pio test -e native` — the `_Static_assert` **is** the test. Verified to compile on all four. | ✅ |
| **DECODE-03** | the guard actually fires | negative proof | plant a reorder in a throwaway worktree named `firestarter`; the build must FAIL with the assertion's message | ❌ **Wave 0** — a planted-negative probe |
| **DECODE-04** | `protocol` u8 / `ctrl_flags` u16; no behavioural change | full native suite, both envs | `pio test -e native && pio test -e native_nodevtools` | ✅ 172/172 verified with the change |
| **DECODE-04** | flag-bit host parity unaffected | host gate | `pytest tests/test_revision_constants_parity.py -q` | ✅ GREEN verified |
| **DECODE-04** | −258 B / −5 B RAM attributable to the narrowing alone | two-variant build | build the table-only variant, then add the narrowing | ✅ |
| **DECODE-05** | out-of-range `algorithm` saturates, not truncates | unit | `pio test -e native -f "*test_read_timing*"` | ❌ **Wave 0** — case S1 |
| **DECODE-05** | and the **dispatch** fail-closes (`configure_memory` refuses) | unit | same | ❌ **Wave 0** — case S2, the load-bearing one |
| **DECODE-05** | a valid algorithm still dispatches (non-regression) | unit | same | ❌ **Wave 0** — case S3 |
| **DECODE-05** | `flags` **masks**, never saturating to all-flags-set | unit | same | ❌ **Wave 0** — case S4 (F-1 / C-7) |
| **DECODE-05** | `page-size` out-of-range no longer yields a *valid* page size | unit | same | ❌ **Wave 0** — case S5 |
| **DECODE-05** | the existing suite is blind to the hole (the RED baseline) | probe | narrow + delete saturation, `pio test -e native` → 172/172 | ✅ **already performed** (F-4) |
| **DECODE-06** | `read-settling-delay` still clamps to 1000 | unit | `pio test -e native -f "*test_read_timing*"` | ✅ **exists** (`test_read_timing_params.cpp:121`), verified GREEN with the table |
| **DECODE-06** | `read-strobe-us` clamps to 1000 | unit | same | ❌ **Wave 0** — does not exist (C-8) |
| **DECODE-06** | both clamp to **exactly** 1000, not to 0 | unit | same | ❌ **Wave 0** — tighten `<=` to `==` |
| **DECODE-07** | the `switch` alternative is recorded with its measurement | **record only** | none | n/a — `157-after-figures.md` discharges it |
| **cross-cutting** | the host wire-key parity gate stays green | host gate | `pytest tests/test_json_key_parity.py -q` (committed tree) | ✅ exists; **must be run** (F-2) |
| **cross-cutting** | no size/RAM regression, recorded as one-sided | size gate | `check_size_baseline.py --policy merge05 --baseline …base01.json --rebuild` | ✅ |
| **cross-cutting** | zero AVR build warnings | build gate | `python3 scripts/check_build_warnings.py` | ✅ exists; **UNVERIFIED this session** |
| **cross-cutting** | still heap-free and 64-bit-runtime-free (Phase 155 non-regression) | symbol gate | `python3 scripts/check_no_heap_or_64bit_symbols.py` | ✅ exists; **UNVERIFIED this session** |

### ⚠ The honest coverage ceilings — stated, not implied

1. **`src/json_parser.c` IS natively covered** (F-3) — unlike Phase 155's `rurp_common.cpp`. Every
   behavioural criterion in this phase is reachable by a native test that CI runs. **This phase has
   no coverage gap of Phase 155's kind, and its record must not borrow that phrasing.**
2. **`src/firestarter.cpp` and `src/eprom_operations.cpp` are OUTSIDE the native `src_filter`.**
   Between them they hold 8 of the 40 `is_flag_set` uses and the `eprom_block_budget_s` call. The
   narrowing's effect on those files is proven only by **compilation**, never by execution. State it.
3. **`src/dev_tools.cpp` is outside too**, and holds 9 `is_flag_set` uses plus 7 `LOG_INFO_ID*`
   expansions — the single largest concentration. Compile-only coverage.
4. **DECODE-01 and DECODE-02 have no automated gate.** They are measurements recorded in
   `157-after-figures.md`. No test asserts that the eleven stubs stayed deleted or that a key is
   stored once. A future phase could silently reintroduce either. **Do not describe them as gated.**
5. **The −5 B RAM saving is unobservable natively** (`sizeof` is 655 both ways). AVR-only.
6. **The `flags` string-dedup is a toolchain outcome, not a source property**, and I did not
   establish its mechanism. Re-measure per target; do not assert it as a source contract unless
   `get_flags` is changed to reference `key_flags` directly.
7. **Saturation-as-fail-closed is contingent on `0xFF` being unmapped** in `configure_memory`'s
   chain. That is true today and pinned by no test unless case S2 is written. It is a property of
   the dispatch table, not of `store_field`.
8. **No bench coverage, by design** (D-02). No criterion needs silicon; nothing here is claimed of
   real hardware.
9. **`_Static_assert` proves the offsets fit `uint8_t` at build time — it does not prove the table
   writes the right member.** Only the native parse tests do that, and only for the fields they
   exercise (today: `read_settling_us`, `read_strobe_us`, `page_size`; after Wave 0: `protocol`,
   `ctrl_flags` too). `mem_size`, `address`, `pulse_delay`, `chip_id`, `vpp_mv`, `pins` will have
   **no native round-trip test** of the new store path. **Consider adding one case per field** — a
   cheap, high-value addition given that a wrong `offsetof` in one row is the refactor's most
   plausible silent defect.

### Sampling rate

- **Per task commit:** `pio run -e uno` (0.5 s warm) + `pio test -e native -f "*test_read_timing*"`.
- **Per wave merge:** all three `pio run` + `pio test -e native` + `pio test -e native_nodevtools`
  + `python3 scripts/check_build_warnings.py`.
- **Phase gate (before `/gsd-verify-work`):** cold rebuild of all three targets;
  `check_size_baseline.py --policy merge05 --baseline …base01.json --rebuild`;
  `check_no_heap_or_64bit_symbols.py`; both native envs green; **and** `pytest tests/` in
  `firestarter_app` on a **committed** firmware tree (expect 1976 passed, or an explained delta).
- **Record:** `.planning/v1.33/157-before-figures.md` and `157-after-figures.md`, per the
  155/156 convention.

### Wave 0 gaps

- [ ] `test/native/avr/test_read_timing/test_read_timing_params.cpp` — DECODE-05 cases **S1, S2,
      S3, S4, S5** (S2 is load-bearing; S4 encodes F-1). Author **RED-first** against the
      saturation-deleted probe tree.
- [ ] same file — DECODE-06: a `read-strobe-us` cap case, and `==` tightening on both knobs.
- [ ] same file — *recommended*: one store-round-trip case per remaining table field (`mem_size`,
      `address`, `pulse_delay`, `chip_id`, `vpp_mv`, `pins`) to close ceiling 9.
- [ ] a planted-negative probe for the `_Static_assert` (throwaway worktree **named
      `firestarter`**): reorder a field below `data_buffer`, confirm the build FAILS with the
      assertion's message, then discard. A never-seen-to-fire assertion is not evidence.
- [ ] `.planning/v1.33/157-before-figures.md` — the before ledger (this document's §Measured
      figures is its raw material).
- [ ] `.planning/v1.33/157-after-figures.md` — the after ledger, the corrections index C-1…C-16,
      DECODE-07's record, and the LAND-01 case-count handoff.
- [ ] **No framework install needed** — every tool is present.

---

## Security Domain

`security_enforcement` is not set to `false` in `.planning/config.json`, so this section is
required. **This phase contains the milestone's single safety requirement (DECODE-05), so it is not
a formality.**

### Applicable ASVS categories

| ASVS category | Applies | Standard control, as it lands here |
|---|---|---|
| **V5 Input Validation** | **YES — this is the phase's core security surface** | The wire `algorithm`/`flags`/`pin-count`/`chip-id`/`vpp_mv`/`page-size` values are attacker- or bug-controlled integers written directly into a dispatch key. Control: **bound every narrow field at the parse boundary** in `store_field` — saturate ordinals, **mask bitmasks** (C-7) — plus the pre-existing `configure_not_implemented` backstop. Never hand-roll a per-field ad-hoc check; that is exactly the form this phase deletes. |
| **V2 Authentication** | no | No authentication surface. The transport is a local USB serial link with no identity model. |
| **V3 Session Management** | no | The three-phase INIT→MAIN→END state machine is not touched. |
| **V4 Access Control** | **partially** | `FLAG_FORCE`, `FLAG_SKIP_ERASE` and `FLAG_SKIP_BLANK_CHECK` are *the* privilege-escalation surface in this firmware — they suppress safety checks before a destructive write. C-7's saturation defect is precisely a V4 violation: an out-of-range input granting every privilege. Control: mask, never saturate. |
| **V6 Cryptography** | no | None present; none added. |
| **V7 Error Handling / Logging** | yes, weakly | The fail-closed path emits `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` (0xBB). Deliberately **no new message id** (avoids meta-repo codegen). The out-of-range case is therefore reported as "protocol not implemented", which is honest but does not distinguish "you sent 261" from "you sent 0x34" — an accepted, stated limitation. |
| **V12 Files / Resources** | no | Phase 155 made the firmware heap-free; nothing here allocates. |
| **V13 API / Web Service** | n/a | Not a web surface. The wire contract is unchanged (verified). |

### Known threat patterns for this stack (AVR C, serial JSON command decode)

| Pattern | STRIDE | Standard mitigation | Status in this phase |
|---|---|---|---|
| **Integer truncation on narrowing an externally-supplied dispatch key** | **Elevation of Privilege / Tampering** | bound-check or saturate at the trust boundary before the narrow store | **THE phase's central risk.** `0x105 → 0x05` dispatches into a different algorithm handler; `0x107 → 0x07` would reach the 12/13 V VPP path. Mitigated by `store_field`'s saturation, proven by DECODE-05 case S2. |
| **Bitmask saturation granting all privileges** | **Elevation of Privilege** | mask (or reject) — never clamp a bitmask to its type maximum | **UNMITIGATED in the reference patch.** C-7 / F-1. The plan must fix it. |
| **Unbounded delay from a wire-supplied timing value** | **Denial of Service** | clamp at parse time | Already mitigated (T-44-01, `READ_TIMING_MAX_US` 1000 µs). DECODE-06 preserves it; C-8 notes only half of it is tested. |
| **Out-of-bounds write via an attacker-influenced struct offset** | **Tampering** | derive offsets from the type; assert at compile time | Mitigated by `offsetof` + `_Static_assert`. **Note the residual:** `store_field`'s `memcpy((uint8_t*)handle + offset, &v, width)` is a raw pointer write into a struct. It is safe only because *both* `offset` and `width` come from the compiler. Any future hand-written row breaks that. This is why C-14's stronger assertion matters and why the `FIELD()` macro must be the **only** way to add a row. |
| **Token-count exhaustion / desync from a malformed frame** | DoS | fixed token budget + forward-compatible unknown-key skip | Pre-existing and untouched (`NUMBER_JSNM_TOKENS` 64; `json_parse`'s `token_idx += 2` unknown-key skip). Two existing tests cover the desync case (`test_unknown_key_before_a_known_key_does_not_desync_the_token_walk` and its page-size sibling) — **both must stay green**, since the refactor rewrites the loop they exercise. |
| **Silent page-size downgrade producing a plausible-but-wrong flush granularity** | Tampering | validate power-of-two and range at the consumer | Pre-existing (`eeprom28c_page_mask`). Saturation *improves* it: today `0x10040` truncates to a **valid** 64, whereas `0xFFFF` fails the power-of-two test and falls back. |
| **Endianness assumption in a byte-width store** | Tampering (portability) | document the assumption at the site | Documented in the reference patch's own comment. AVR, x86-64 and PY32F071 ARM are all little-endian. Keep the comment. |
| **Undefined behaviour from `1UL << 32`** | correctness | guard with `width < sizeof(v)` | Present in the reference. Keep it, and prefer `uint32_t` over `unsigned long` to remove the AVR/native asymmetry entirely (Pitfall 12). |

**Threat-model boundary, stated:** the adversary here is *our own host CLI with a bug*, or a
hand-crafted serial frame from someone with physical USB access. There is no remote attacker and no
authentication boundary to cross. The consequence of the mitigated defect is **a destroyed chip or
a 13 V rail on a 5 V part**, not data disclosure. That is the right frame for judging
saturate-vs-reject: the cost of a wrongly-refused command is one error message; the cost of a
wrongly-dispatched one is hardware.

---

## State of the Art

| Old approach | Current approach | When changed | Impact here |
|---|---|---|---|
| `{key, function pointer}` PROGMEM dispatch table | `{key, offset, width, policy}` data descriptor + one shared inlined store | this phase | the whole −890 B. On AVR a PROGMEM function pointer is an inlining barrier; a data descriptor is not. |
| Per-getter ad-hoc validation (two of eleven clamp, nine do not) | one validation site with a per-row policy column | this phase | DECODE-05/06 |
| Hand-written struct offsets | `offsetof` + `sizeof(((T*)0)->member)` | C89 / C11 respectively | mandatory, not stylistic — AVR and native layouts differ at every field from `protocol` down |
| Runtime layout checks / comments | `_Static_assert` (C11, avr-gcc ≥ 4.6; here gcc 7.3.0) | C11 | zero flash cost; **new idiom for this repo** — the only existing static assert is the C++ one at `include/eprom_params.h:62` |
| `uint32_t` for every handle field | width matched to the value range | this phase | −5 B RAM on AVR; **zero on native** (padding absorbs it) |
| JSON command frame | *(queued)* binary command frame, v1.28 / 999.35, −3728 B / −512 B | **NOT in v1.33** (operator, 2026-08-22) | supersedes DECODE-01. **Not additive.** |

**Deprecated / superseded by this research:**
- The ROADMAP's `−976 / −172` split → **−890 / −258** (C-4).
- "Ten of eleven keys stored twice" → **eleven of eleven** (C-3).
- "19 protocol comparisons / 45 `is_flag_set`" → **18 (or 20) / 40 (or 59)** (C-5).
- "`json_parse_config` calls `get_flags` at two sites" → one there, one in `json_get_cmd` (C-1).
- "Leonardo headroom 3440 B" → **3442 B** (C-13).
- "`uno` 25696 vs 25678" → stale by ~1.4–2.6 KB (C-10).
- "Phases 155–158 are firmware-only" → **contradicted for Phase 157** unless `key_parsers` is
  kept (C-12).
- Phase 156's "the subset applies with `git apply -C1`" → **does not generalise** (C-11).

---

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|---|---|---|
| **A1** | The reference patch's `field_desc_t` / `FIELDS[]` shape is the intended DECODE-01 design (the ROADMAP describes `{key, offset, width, clamp}` and the patch implements exactly that). | Prior art, DECODE-01 | Low. If the operator wanted a different shape the byte figures would change; the −1148 B total is measured for *this* shape only. |
| **A2** | Keeping the identifier `key_parsers` is acceptable naming for a table that no longer holds parsers. | C-12, F-2 | Low-moderate. It is a slightly stale name for a zero-cost gate save. The alternative is a host commit plus a ROADMAP correction. **Surface this to the operator** — it is a genuine trade, not a mechanical call. |
| **A3** | Mask semantics for `ctrl_flags` is what the operator wants (as opposed to rejecting the command outright with a new message id). | C-7, F-1 | **Moderate — this is a safety decision.** Mask preserves today's exact behaviour and needs no codegen; reject is stricter but breaks firmware-only. **Recommend surfacing at `/gsd-discuss-phase`.** |
| **A4** | Saturating `pins` (256 → 255 instead of today's → 0) is acceptable, even though it flips which VPP-drop arm `mem_util_calculate_top_address_register` takes. | DECODE-05 table | Low. No real host sends `pin-count` > 255; both outcomes are wrong-input handling. But it **is** a behaviour change in a milestone premised on byte-level equivalence, so it must be *stated*, not discovered. |
| **A5** | `_Static_assert` will remain available on any future target this firmware gains. | DECODE-03 | Low for AVR/native (verified). UNVERIFIED for the PY32F071 ARM port — not built here. That port is out of v1.33 scope. |
| **A6** | The `flags` string-duplicate disappearing is a stable toolchain behaviour rather than a fluke of this exact code shape. | DECODE-02 | **Moderate.** It is the one criterion whose satisfaction I cannot explain. Mitigation: change `get_flags` to reference `key_flags` directly, making it a source property. |
| **A7** | DECODE-07's +18 B delta still holds at this position. | DECODE-07 | Moderate, and cheap to eliminate — build the `switch` variant. **Recommend re-measuring.** |
| **A8** | `check_build_warnings.py` and `check_no_heap_or_64bit_symbols.py` stay green. Raw AVR warning count is 0 with the change (verified by grep over the build output), but I did not run either script. | Gate blast radius | Low-moderate. The native macro-redefinition watermark (1166) reportedly has near-zero headroom. **Run both.** |
| **A9** | `sizeof(firestarter_handle_t)` is 600 B before, not the 601 B `155-after-figures.md` records. | Measured figures §4 | Low. My method (`avr-gcc -mmcu=atmega328p`, `DATA_BUFFER_SIZE=512`, `-DHARDWARE_REVISION -DDEV_TOOLS`) is stated; the discrepancy is 1 B and does not affect the −5 B delta, which is measured two independent ways (`sizeof` and `ram_used`). **Re-derive rather than quote either.** |
| **A10** | New native cases go in `test_read_timing` rather than a new suite. | DECODE-05 test spec | Low. A new suite would need lockstep edits to two `test_filter` lists and two `-I` lists, and would move the *suite* count from 17 as well as the case count — reddening `compare_native` on two legs instead of one. |

---

## Open Questions (ALL RESOLVED at plan time — 2026-08-23)

> **Every OQ below is closed.** OQ-3 and OQ-4 were put to the operator during
> `/gsd-plan-phase 157` and answered; the remaining five were settled by the orchestrator taking
> this document's own recommendation, each being a mechanical question with a clear one. The
> resolutions are the `OD-N` decisions, and every one of them is threaded into the seven plans'
> frontmatter, actions and prohibitions.
>
> | OQ | Resolution | Decision id |
> |---|---|---|
> | OQ-1 — `handle` 600 B or 601 B | Re-derive with the real `pio run -v` flags; record ONE number with its method. The −5 B delta is independently confirmed by `ram_used`, so nothing downstream depends on the absolute. | **OD-7** |
> | OQ-2 — why the `flags` PROGMEM duplicate vanishes | Do not depend on the toolchain outcome. Point `get_flags` at `key_flags` so single-key-storage is a **source property** (~3 lines), then re-measure per target. | **OD-3** |
> | OQ-3 — saturate, mask, or reject, per field | **Operator answered:** saturate for ordinals, **MASK** for bitmasks, reject for nothing. `ctrl_flags` masks — saturating it to `0xFFFF` would set `FLAG_FORCE` / `FLAG_SKIP_ERASE` / `FLAG_SKIP_BLANK_CHECK`, i.e. fail-OPEN. `reject` declined because it needs a new message id → meta `messages.toml` → codegen → would break firmware-only; the declined option is recorded with that cost. | **OD-1** |
> | OQ-4 — keep `key_parsers`, or accept a host commit | **Operator answered:** keep the name. Zero `firestarter_app` commits, the cross-repo parity gate stays honest, and the milestone's firmware-only property holds. The record states the identifier is now slightly stale and why it was kept. | **OD-2** |
> | OQ-5 — re-measure DECODE-07's +18 B, or record as stale | Re-measure at this phase's position; record the original with its provenance **and** the fresh figure. | **OD-4** |
> | OQ-6 — store-round-trip cases for the six untested fields | Take them. A wrong `offsetof` in one row is the refactor's most plausible silent defect, and the case count already moves. Closes ceiling 9. | **OD-5** |
> | OQ-7 — `check_build_warnings.py` / native watermark | Run both it and `check_no_heap_or_64bit_symbols.py`. Do not assume. Neither is in CI; the watermark has zero headroom. | **OD-6** |
>
> **Three further corrections were found during planning and extend the C-series:** **C-17** —
> `#define READ_TIMING_MAX_US` is at `src/json_parser.c:60`, not `:352`, and this document's
> DECODE-01 table lists the first seven `key_*` declarations one line high (`memory-size` is
> `:51`). **C-18** — the claim that one saturation-deleted probe reddens S1/S2/**S4** is wrong: with
> `ctrl_flags` narrowed and no saturation, `flags: 65536` truncates to 0 and S4's `== 0` assertion
> passes **vacuously**; S4's only non-vacuous negative is a *saturating*-bitmask probe. Two probes
> are required. **C-19** — the −890 / −1148 figures were measured on a table with **no policy
> column**; OD-1 adds one, so a post-change figure still reading exactly −1148 is the *suspicious*
> outcome and must not be chased.

1. **OQ-1 — `handle` is 600 B or 601 B?**
   - What we know: my probe measures `sizeof(firestarter_handle_t) == 600` before and `595` after,
     on `avr-gcc -mmcu=atmega328p` with `DATA_BUFFER_SIZE=512`, `-DHARDWARE_REVISION -DDEV_TOOLS`.
     `155-after-figures.md` records 601 B post-DEAD-01.
   - What's unclear: which flag set or buffer size produces 601.
   - Recommendation: the plan re-derives with the exact `pio` command line (`pio run -v` to capture
     the real flags) and records one number with its method. The **−5 B delta** is independently
     confirmed by `ram_used` (1567 → 1562 on `uno`), so nothing downstream depends on resolving it.

2. **OQ-2 — why does the `flags` PROGMEM duplicate vanish?**
   - What we know: before, `flags` occupies vaddr 196 (`key_flags`) **and** vaddr 226 (a stub
     `PSTR`). After, only vaddr 196. `get_flags` still contains `PSTR("flags")` via `extract_long`.
   - What's unclear: the mechanism (constant merging in `.progmem.data`? a CSE of the `__c` static
     once the function is cloned rather than pointer-called?).
   - Recommendation: do not depend on it. Change `get_flags` to `jsoneq_(json, &tokens[pos],
     key_flags)` so single-storage is a source property, then re-measure on all three targets. Cost:
     three lines. (A6)

3. **OQ-3 — saturate, mask, or reject, per field?**
   - What we know: saturate is genuinely fail-closed for `protocol` (0xFF is unmapped) and
     `page_size` (fails the power-of-two test); it is **fail-open for `ctrl_flags`**; it is a
     warning-only improvement for `vpp_mv`; and it flips an arm for `pins`. Reject needs a new
     message id → meta-repo `messages.toml` → codegen → not firmware-only.
   - What's unclear: whether the operator wants any field to *refuse* rather than clamp.
   - Recommendation: **surface at `/gsd-discuss-phase`.** Default to saturate-for-ordinals,
     mask-for-bitmasks, reject-for-nothing, and record the alternative with its cost.

4. **OQ-4 — keep the name `key_parsers`, or accept a host commit?**
   - What we know: keeping it makes the cross-repo gate a zero-edit surface and closes a fail-open.
     Renaming means one `firestarter_app` commit, an explicit ROADMAP correction to
     "firmware-only", and a separate fix for the fail-open leg.
   - Recommendation: keep the name; note in the record that the identifier is now slightly stale
     and why. **But surface it** — "Phases 155–158 are firmware-only" is an operator-visible
     property of the milestone. (A2)

5. **OQ-5 — re-measure DECODE-07's +18 B, or record it as stale?**
   - What we know: the absolutes are stale by ~1.4–2.6 KB; the delta is unverified; re-measuring is
     ~15 minutes.
   - Recommendation: re-measure. (A7)

6. **OQ-6 — should the phase add a store-round-trip test for the six untested table fields?**
   - What we know: a wrong `offsetof` in one row is the refactor's most plausible silent defect, and
     only three of eleven fields have any native parse test today.
   - What's unclear: whether the case-count movement (see C-15) makes the planner reluctant.
   - Recommendation: add them. The count already moves; six more cases cost nothing extra in gate
     terms and close ceiling 9.

7. **OQ-7 — does `check_build_warnings.py` still pass, and is the native watermark at zero headroom?**
   - What we know: raw AVR `warning:` count is 0 with the change; the native watermark is 1166 with
     a `<=` policy.
   - Recommendation: the plan runs it. Do not assume. (A8)

---

## Sources

### Primary (HIGH confidence — measured or executed in this session)

- `pio run -e {uno,uno328pb,leonardo}` before and after, plus the table-only and
  narrowed-no-saturation variants — the four size/RAM measurement sets.
- `pio test -e native` ×3 and `pio test -e native_nodevtools` ×1 — case counts, durations, the
  blindness proof.
- `avr-nm --print-size --size-sort --radix=d` on `firestarter_uno.elf`, before and after — the
  1012 B stub ledger, `FIELDS` 66 B, `key_parsers` 44 B, the five-sibling absence,
  `get_flags.constprop` 90 → 82 B.
- `strings -a -n 2 -t d` on `firestarter_uno.elf` and `firestarter_leonardo.elf`, cross-keyed to
  `avr-nm` symbol addresses — the two-blocks-to-one key-string result.
- A generated `offsetof` probe TU compiled with `avr-gcc -mmcu=atmega328p` and host `gcc`, before
  and after — all 17 member offsets on both architectures, both `sizeof` values.
- `git apply --check -C{0,1,2,3}`, `git apply --3way`, `patch -p1 --dry-run -F3` on both patch
  subsets — the hunk-by-hunk applicability result.
- `python3 scripts/check_size_baseline.py --policy merge05 --baseline
  scripts/baseline/size_baseline_base01.json --rebuild` — the exact two-line failure.
- `python3 -m pytest tests/test_json_key_parity.py tests/test_revision_constants_parity.py` before
  and after, and `python3 -m pytest tests/` (1976 passed) — the host blast radius.
- `grep -rn check_size_baseline .github/` (empty) and `grep -rn 'pio test' .github/workflows/` —
  the CI coverage facts.
- `pio --version` (6.1.19) and the platform/toolchain versions printed by the build.

### Primary (HIGH confidence — read in this session)

- `firestarter/src/json_parser.c` (all 391 lines), `firestarter/include/firestarter.h`,
  `firestarter/include/proto_constants.h`, `firestarter/include/logging_id.h` (macro bodies),
  `firestarter/src/proms/memory.cpp` (`configure_memory`,
  `mem_util_calculate_top_address_register`), `firestarter/src/proms/eprom.cpp:60-95`,
  `firestarter/src/proms/eeprom_28c.cpp:615-665`, `firestarter/src/proms/not_implemented.cpp`.
- `firestarter/platformio.ini` (all envs, all `build_src_filter` and `test_filter` lists).
- `firestarter/test/native/avr/test_read_timing/test_read_timing_params.cpp`.
- `firestarter/scripts/check_size_baseline.py` (docstring, `:697`, `:709`),
  `firestarter/scripts/baseline/size_baseline.json`, `…/size_baseline_base01.json`.
- `firestarter/CLAUDE.md` (§Protocol Dispatch, §Algorithm Handlers), `/workspaces/CLAUDE.md`.
- `firestarter_app/tests/test_json_key_parity.py` (all 500+ lines),
  `firestarter_app/tests/scan_paths.py`, `firestarter_app/tests/test_revision_constants_parity.py`
  (the `FLAG_*` legs).
- `.planning/ROADMAP.md` (v1.33 entry, framing block D-01…D-05, Phase 157 and 158 sections),
  `.planning/REQUIREMENTS.md` (DEAD/DEDUP/DECODE/LAND/REMAP blocks, traceability, out-of-scope),
  `.planning/notes/firmware-size-reduction-measured.patch` (all ten file diffs),
  `.planning/v1.33/156-before-figures.md` and `156-after-figures.md` (structure),
  `.planning/phases/156-*/156-RESEARCH.md` (structure and gate-blast-radius conventions),
  `.planning/v1.33/CITATIONS-STALE.md`, `.planning/config.json`.

### Secondary (MEDIUM confidence)

- `.planning/notes/firmware-size-reduction-survey.md` — the origin of the ROADMAP's figures. Not
  read line-by-line this session; its numbers were **re-measured** rather than trusted, and four of
  them are corrected above.
- Project memory (`~/.claude/projects/-workspaces/memory/`) — the pitfall inventory (native trace
  stubs, tautological parity tests, host gates failing open on firmware renames, `messages.h`
  codegen, porcelain-asserting tests, `.constprop` suffixes, load-flakiness, CI Python 3.11).
  Each item that bears on this phase was **independently re-verified** here and is cited as
  measured; the rest is carried as MEDIUM.

### Tertiary (LOW confidence — flagged, not relied upon)

- The ROADMAP's DECODE-07 figures (`uno` 25696 / 25678) — stale absolutes, unverified delta (C-10).
- The ROADMAP's `−976 / −172` split, `19`/`45` counts, "ten of eleven", `3440 B` — all superseded
  by measurement (C-2…C-5, C-13).
- `.planning/graphs/graph.json` — 2026-07-01, three milestones stale. **Deliberately not queried.**
- The claim that `_Static_assert` works on the PY32F071 ARM port — not built, ASSUMED (A5).

---

## Metadata

**Confidence breakdown:**

| Area | Level | Reason |
|---|---|---|
| Headline size/RAM figure (−1148 / −5, all three targets) | **HIGH** | Built and measured end to end this session; matches the ROADMAP exactly. |
| Stub ledger (1012 B, five siblings at zero) | **HIGH** | `avr-nm`, exact sum. |
| Key-string duplication and its removal | **HIGH** for the counts, **MEDIUM** for the mechanism | Offset-resolved dump on two ELFs; the `flags` case is unexplained (OQ-2). |
| Struct offsets, both architectures, both variants | **HIGH** | Compiler-derived, not read off a header. |
| Native coverage of `json_parser.c` (F-3) | **HIGH** | `platformio.ini` `build_src_filter`, plus a working test that calls `json_parse`. |
| Blindness of the existing suite (F-4) | **HIGH** | Executed against a deliberately broken tree. |
| Host gate blast radius (F-2) | **HIGH** | pytest run before and after, three failures triaged individually. |
| The `ctrl_flags` saturation defect (F-1) | **HIGH** | Read from the reference patch and the flag `#define`s; arithmetic is trivial and checkable by inspection. |
| Size-gate obligation and the pre-existing RED (F-6) | **HIGH** | The gate was actually run. |
| Requirement counts (18/20, 40/59) | **HIGH** for the numbers, **MEDIUM** for reconciling them with the ROADMAP's 19/45 | I could not reproduce 19 or 45 by any counting rule I tried. |
| DECODE-07's +18 B delta | **LOW** | Not measured; the `switch` variant was never built. |
| Architecture patterns and the recommended fixes | **HIGH** | Each is grounded in a measurement above. |
| PY32F071 portability of `_Static_assert` | **LOW** | Not built. Out of milestone scope. |

**Research date:** 2026-08-23
**Firmware position:** `1151dc4` (clean; verified restored after every probe — the before figures
were reproduced byte-for-byte on the restored tree)
**Host position:** `38f0d83`
**Valid until:** **until Phase 158 lands.** Every absolute size figure here is invalidated by
LAND-01's cold baseline re-record; every `file:LINE` citation here is invalidated by Phase 159's
remap (D-05). The *deltas*, the ledgers and the findings remain valid.







