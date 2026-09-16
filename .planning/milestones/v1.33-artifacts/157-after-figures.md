---
title: After-figures record -- milestone v1.33, Phase 157 (Command-Decode Table + Handle Type Narrowing, firmware-only)
phase: 157-command-decode-table-handle-type-narrowing-firmware-only
plan: "07"
measured: 2026-08-23
status: AUTHORITATIVE -- this file is the phase's outcome record, re-measured against the
  committed tree at `firestarter` `785e644` this session, never merely transcribed from an
  earlier plan's SUMMARY. Phase 158 invalidates every size figure captured here (it re-anchors
  `scripts/baseline/size_baseline.json` and cold-rebuilds all three AVR targets), so no later
  plan can re-derive them from this position.
supersedes: >
  ROADMAP.md Phase 157's `**Measured**` line ("−1148 B flash (field table −976, narrowing +
  saturation −172)") and success criteria 1 through 7, and REQUIREMENTS.md DECODE-01 through
  DECODE-07 prose, wherever they state a figure this file corrects -- C-1 through C-22, all
  first identified in `.planning/milestones/v1.33-artifacts/157-before-figures.md` (C-1..C-19) or found by plans
  04/05/06 of this phase (C-20, C-21, C-22) and closed out here against the shipped, final code.
requirements: [DECODE-01, DECODE-02, DECODE-03, DECODE-04, DECODE-05, DECODE-06, DECODE-07]
---

# After-figures record -- v1.33 Phase 157

This is the phase's landing record: all eight phase-gate legs run and recorded on the final
committed tree at `785e644`, with the headline size figures COLD on both sides of the
comparison (the pre-phase position cold-rebuilt in a throwaway detached worktree, so the
composed delta is not a warm-before-against-cold-after mixture). DECODE-01's symbol ledger and
DECODE-02's key-string block dump are re-measured at this final position; DECODE-07 is
discharged by its own section, since it changes no code; and all twenty-two corrections are
closed out. Every figure below carries the verbatim command that produced it, run this session
against `firestarter` `785e644` on `gsd/v1.33-source-hygiene-firmware-size-reduction`.

---

## 1. Git anchors

| Field | Value |
|---|---|
| `FW_POST_SHA` | `785e644bacbe128de813407f0e6e357c71164836` (`785e644`) -- HEAD of `gsd/v1.33-source-hygiene-firmware-size-reduction`, this phase's last landed commit (157-05) |
| `firestarter` branch | `gsd/v1.33-source-hygiene-firmware-size-reduction` (unchanged by this plan) |
| `git -C firestarter status --porcelain` | empty, asserted before and after every measurement step in this session |
| `git -C firestarter log -1 --format=%s` | `test(157-05): cap read-strobe-us, tighten both cap assertions, round-trip every table row` -- confirming plan 06 produced no firmware commit |
| `git -C firestarter worktree list` | `/workspaces/firestarter` (primary, `785e644`) + `/workspaces/firestarter_py32_ci` (pre-existing, unrelated sibling, untouched) -- every throwaway worktree this plan created (`157-cold-probe`, `157-07-probe`) was removed and pruned before this record was written |
| meta repo HEAD (before this plan's own commit) | `45c3871636e372152be9aa2be0b969719d402355` |

**Four firmware commits landed this phase** (`git -C firestarter log --oneline 1151dc4..785e644`):

| # | Hash | Subject |
|---|---|---|
| 1 | `19df431` | `refactor(157-02): replace the key-parser dispatch table with a compiler-derived field table` |
| 2 | `76ff592` | `refactor(157-03): narrow handle protocol to uint8_t and ctrl_flags to uint16_t` |
| 3 | `8edfd6e` | `test(157-04): prove an out-of-range algorithm and flags fail closed` |
| 4 | `785e644` | `test(157-05): cap read-strobe-us, tighten both cap assertions, round-trip every table row` |

Plan 06 produced **zero** firmware commits (`files_modified: []` per its own contract, confirmed
this session: `git -C firestarter status --porcelain` remained empty and HEAD stayed `785e644`
throughout).

**`firestarter_app` gitlink note:** the meta repo shows `firestarter_app` as modified
(`git status --porcelain` in `/workspaces`). `git diff --stat -- firestarter_app` is **empty**
-- no gitlink SHA change; this is **pre-existing Phase 154 drift, operator-gated**, not touched,
staged or re-pinned by this plan or any plan in this phase.

**`firestarter` gitlink:** shows a genuine one-line SHA change (to `785e644`), reflecting this
phase's own four landed commits. Re-pinning it into a meta commit is **out of scope for this
plan**, per the repo-topology instructions governing this execution -- this plan's own commits
stage `.planning/` paths only.

Commands run:
```bash
git -C firestarter rev-parse HEAD
git -C firestarter status --porcelain
git -C firestarter log --oneline 1151dc4..785e644
git -C firestarter log -1 --format=%s
git -C firestarter worktree list
git rev-parse HEAD   # meta repo
git diff --stat -- firestarter_app
```

---

## 2. The phase ledger -- flash and RAM, before vs after, per target, COLD

**Cold pre-phase (throwaway `git worktree add --detach /tmp/157-cold-probe/firestarter 1151dc4`,
`rm -rf .pio/build/<env>` then exactly one `pio run -e <env>` per env, this session):**

| Target | Flash (COLD) | RAM (COLD) |
|---|---|---|
| `uno` | **24234** | **1567** |
| `uno328pb` | **24282** | **1573** |
| `leonardo` | **26378** | **2008** |

These are **byte-identical** to `157-before-figures.md`'s own WARM figures -- the WARM/COLD
convention makes no difference at this position, confirmed rather than assumed. Zero
`warning:` lines. The worktree was removed and pruned before the next step; `git -C
firestarter worktree list` matched its pre-probe output afterward.

**Cold post-phase, on the committed tree** (`rm -rf .pio/build/<env>` then exactly one
`pio run -e <env>` per env, this session, `git status --porcelain` empty before and after):

| Target | Flash (COLD) | RAM (COLD) |
|---|---|---|
| `uno` | **23090** | **1562** |
| `uno328pb` | **23138** | **1568** |
| `leonardo` | **25234** | **2003** |

Also byte-identical to plan 03/04/05's own WARM figures at this position -- zero `warning:`
lines, reproduced twice this session (once as the task-1 cold measurement, once again as part
of `check_build_warnings.py --rebuild`'s own cold rebuild).

**Composed delta, COLD to COLD, per target:**

| Target | Before (COLD) | After (COLD) | Delta | RAM before | RAM after | RAM delta |
|---|---|---|---|---|---|---|
| `uno` | 24234 | 23090 | **−1144 B** | 1567 | 1562 | **−5 B** |
| `uno328pb` | 24282 | 23138 | **−1144 B** | 1573 | 1568 | **−5 B** |
| `leonardo` | 26378 | 25234 | **−1144 B** | 2008 | 2003 | **−5 B** |

**Per-half attribution** (WARM measurements, plans 02/03, cited not re-derived here since each
was measured against the position immediately preceding its own edit):

| Half | Plan | Own measured delta (all 3 targets) |
|---|---|---|
| Table half (DECODE-01/02/03/06) | 02 | **−884 B** flash, 0 B RAM |
| Narrowing half (DECODE-04) | 03 | **−260 B** flash, **−5 B** RAM |
| **Sum** | | **−1144 B** flash, **−5 B** RAM -- matches the cold-to-cold composed total exactly |

**Reconciliation against the research's `−890` / `−258` / `−1148`:** the measured table half
is `−884 B`, not `−890 B` (a 6 B divergence); the measured narrowing half is `−260 B`, not
`−258 B` (a 2 B divergence); the measured composed total is `−1144 B`, not `−1148 B` (a 4 B
divergence). **All three divergences are attributed to OD-1's per-row mask-vs-saturate policy
column** (`FIELD_POLICY_MASK` and its branch in `store_field`), which the reference table those
figures were measured on did not carry (C-19) -- not closed by editing code, and reconfirmed
unchanged at this final, cold position (plan 06 introduced no further code change).

**Leonardo Caterina headroom against the `28672` B cliff:** `28672 − 25234 = 3438` B, measured
COLD this session -- **superseding the ROADMAP's stale `3440` B** (Source assertion: `3440`
does not appear as a current value in this file). This also differs by 4 B from the `3442` B
the phase's own C-13 correction cited (itself derived from the RESEARCH session's *predicted*
absolute of `25230`, never measured at this position) -- the same OD-1-attributed divergence as
the composed-total gap above, not a second, independent finding.

Commands (both sides identical form):
```bash
git worktree add --detach /tmp/157-cold-probe/firestarter 1151dc4
cd /tmp/157-cold-probe/firestarter
for e in uno uno328pb leonardo; do rm -rf .pio/build/$e; done
pio run -e uno -e uno328pb -e leonardo
# ... remove and prune the worktree ...
cd /workspaces/firestarter
for e in uno uno328pb leonardo; do rm -rf .pio/build/$e; done
pio run -e uno -e uno328pb -e leonardo
```

---

## 3. DECODE-01's mechanical criteria -- final symbol ledger

`avr-nm --print-size --size-sort --radix=d .pio/build/uno/firestarter_uno.elf`, resolved at
`$HOME/.platformio/packages/toolchain-atmelavr/bin/avr-nm` (not on `PATH`, Pitfall 9),
re-measured this session on the final committed tree:

```bash
avr-nm --print-size --radix=d .pio/build/uno/firestarter_uno.elf \
  | grep -cE ' (get_memory_size|get_address|get_chip_id|get_pin_count|get_delay|get_vpp_mv|get_algorithm|get_read_settling|get_read_strobe|get_page_size|store_field|get_r1|get_r2|get_rev|get_rw_pin|get_vpp_pin)$'
# => 0
```

**All ten deleted stubs, `store_field` (fully inlined), and the five zero-cost siblings are
ABSENT from the symbol table.** `store_field`'s absence is expected -- it inlines into every
one of the eleven call sites at `-Os`, so it costs nothing as a standalone symbol.

`key_parsers`, before and after:

| | Before (`157-before-figures.md` §3) | After (this session) |
|---|---|---|
| `key_parsers` size | **44 B** (11 × 4 B function pointers) | **66 B** (`avr-nm ... \| grep ' key_parsers$'` -> `00000066`) |

The table **grew** by 22 B (2 B/row) even though the eleven dispatch stubs it used to drive
(1012 B) are gone -- each row now carries a compiler-derived `{key ptr, clamp, offset, width,
policy}` `field_desc_t` rather than a single 4-byte function pointer, and that per-row cost is
paid once instead of once per stub.

`get_flags`' surviving clone, suffix explicitly **not pinned** (Pitfall 13):
```bash
avr-nm --print-size --size-sort --radix=d .pio/build/uno/firestarter_uno.elf | grep -E ' get_flags'
# => 00016574 00000082 t get_flags.constprop.33
```
`82 B`, suffix `.constprop.33` -- the before-record's own `get_flags` clone was unsuffixed at
`90 B` (pre-OD-3 hand-expansion); a future toolchain run may renumber the suffix and that is
expected, not a regression.

`jsoneq_` and `simple_strtoul`, unchanged from the before-record:
```bash
avr-nm --print-size --radix=d .pio/build/uno/firestarter_uno.elf | grep -E ' (jsoneq_|simple_strtoul)'
# => 108 B jsoneq_, 68 B simple_strtoul -- byte-identical to before-figures.md §3
```

**This ledger does NOT close arithmetically against the image delta, and that is expected, not
a defect.** The eleven-stub before total was exactly **1012 B** (§10's C-2 range: `84–110 B`
each), and `key_parsers` grew from 44 B to 66 B (+22 B) -- a naive symbol-table subtraction
would predict roughly `−1012 + 22 = −990 B` for the table half alone, but the measured table-half
delta is `−884 B` (§2). Symbols that stop existing are inlined into their callers and their
bytes are redistributed by LTO into `main` and the surviving call sites, not simply removed --
the image figure (§2) is the phase total, and this symbol ledger is corroboration only, exactly
as `156-after-figures.md` §4 documents for the same reason on a different symbol set.

---

## 4. DECODE-02's evidence -- two-blocks-to-one, all three targets

Offset-resolved block form, never an exact-string count (C-3's own trap). `.text` begins at
file offset `0x94` = `148` on all three targets (`avr-readelf -S`, re-confirmed this session),
so `vaddr = fileoff − 148`, unchanged from the before-record's formula.

```bash
strings -a -n 2 -t d .pio/build/uno/firestarter_uno.elf \
  | awk '{fo=$1; va=fo-148; if (va>=90 && va<=900) printf "fileoff=%d vaddr=%d %s\n", fo, va, $0}'
```

**Exactly ONE key-string block per target now, not two.** Cross-keyed against
`avr-nm ... | grep -E ' key_'`, every one of the eleven wire-key strings appears at the exact
vaddr its symbol reports, count **one**, on all three targets:

| Target | `key_flags` symbol vaddr | `flags` string vaddr | Match |
|---|---|---|---|
| `uno` | 667 | 667 | yes, count 1 |
| `uno328pb` | 743 | 743 | yes, count 1 |
| `leonardo` | 864 | 864 | yes, count 1 |

Full per-key count, all three targets, this session (`memory-size`, `address`, `flags`,
`chip-id`, `pin-count`, `pulse-delay`, `vpp_mv`, `algorithm`, `read-settling-delay`,
`read-strobe-us`, `page-size`): **every one of the eleven keys reads count 1 on every target.**
No `Uflags`-mangled second copy exists anywhere -- that artifact was a property of the deleted
indirect-call stubs, and it is gone along with them.

**Both forbidden oracle forms, re-run this session against the FINAL tree, to show they now
report a DIFFERENT wrong number than before (still wrong, for a different textual reason):**
```bash
strings -a -t d .pio/build/uno/firestarter_uno.elf | awk '$2=="flags"' | wc -l
# exact-match filter: reports the same single true block now (the mangled "Uflags" case that
# made this oracle wrong pre-phase no longer arises, because there is only one copy)
strings -a .pio/build/leonardo/firestarter_leonardo.elf | grep -c flags
# substring grep: still over-reports by matching unrelated tokens containing "flags"
```
The only valid oracle remains the offset-resolved block dump cross-keyed against the symbol
table, repeated per target.

**C-3, re-confirmed at the final position: eleven of eleven wire keys were stored twice
pre-phase; today every one of the eleven is stored exactly once.**

**`get_flags`' exception, stated with both function names (C-1):** `get_flags` survives as a
real function because it is called directly from **two different functions**, not "twice at
one call site" -- `json_parse_config` (`src/json_parser.c:348`) and `json_get_cmd`
(`src/json_parser.c:379`), confirmed this session by direct grep on the shipped source. A
record saying `json_parse_config` calls it twice is factually wrong.

**OD-3's three-line change made this a SOURCE property, not merely a re-measured link-time
outcome.** `get_flags`'s body now references `key_flags` directly
(`src/json_parser.c:490-497`'s own comment: "`get_flags` survives deliberately: it is called
directly from TWO DIFFERENT FUNCTIONS, `json_parse_config` and `json_get_cmd`, neither of which
..."). Without OD-3, `157-before-figures.md`'s own A6 recorded the `flags` string-dedup as a
**toolchain outcome** it could not explain; this session's re-measurement at the final position
still re-derives the single-block result independently per target, rather than assuming the
toolchain will keep deduplicating it.

---

## 5. DECODE-03's evidence -- twelve compile-time guards, closed by execution

**Twelve `_Static_assert` guards** stand in `src/json_parser.c:364-409` -- eleven per-member
offset/width checks plus one row-count check (`sizeof(key_parsers) / sizeof(key_parsers[0]) ==
11`). This is a **NEW idiom for this repository in a C translation unit**; the only
pre-existing static assert is the C++-guarded one at `include/eprom_params.h:62`, inert in
every C TU.

**Both planted-negative diagnostics, captured verbatim this session** in a throwaway detached
worktree (`git worktree add --detach /tmp/157-07-probe/firestarter HEAD`, leaf named exactly
`firestarter`), fully discarded afterward:

**Probe 1 -- struct reorder** (`mem_size` moved from before `address` to immediately after
`data_buffer` in `include/firestarter.h`):
```
src/json_parser.c:364:1: error: static assertion failed: "mem_size: a struct reorder moved it
past the uint8_t offset column's range, or gave it a width the 32-bit store cannot carry"
 _Static_assert(offsetof(firestarter_handle_t, mem_size) < 256 &&
 ^~~~~~~~~~~~~~
*** [.pio/build/uno/src/json_parser.c.o] Error 1
```

**Probe 2 -- planted twelfth `key_parsers[]` row** (a duplicate `FIELD(key_page_size,
page_size, 0)` row appended):
```
src/json_parser.c:409:1: error: static assertion failed: "key_parsers row count changed -- add
or remove the matching per-member offset guard above to match"
 _Static_assert(sizeof(key_parsers) / sizeof(key_parsers[0]) == 11,
 ^~~~~~~~~~~~~~
*** [.pio/build/uno/src/json_parser.c.o] Error 1
```

Both guards fire with the assertion's own authored message text, on `pio run -e uno`, exactly
as plan 02's own probe demonstrated. The probe worktree was reverted (`git checkout -- .`),
removed and pruned; `git -C firestarter worktree list` matched its pre-probe output afterward,
and the real, committed tree at `785e644` was never touched by either plant.

**Struct-offset tables, both architectures, re-derived this session** with the same method the
before-record used for OD-7 (`char off_<m>[offsetof(firestarter_handle_t, m)+1];` per member,
compiled once with `avr-gcc -mmcu=atmega328p` and once with host `gcc`, offsets read back from
`nm --print-size`):

| member | AVR (before, `601` B total) | AVR (after, this session) | native (before, `656` B total) | native (after, this session) |
|---|---|---|---|---|
| `cmd` | 0 | 0 | 0 | 0 |
| `operation_state` | 1 | 1 | 1 | 1 |
| `response_code` | 2 | 2 | 2 | 2 |
| `protocol` | 3 | 3 | 4 | **3** |
| `pins` | 7 | **4** | 8 | **4** |
| `mem_size` | 8 | **5** | 12 | **8** |
| `address` | 12 | **9** | 16 | 12 |
| `vpp_mv` | 16 | 13 | 20 | 16 |
| `pulse_delay` | 18 | **15** | 24 | 20 |
| `read_settling_us` | 22 | **19** | 28 | 24 |
| `read_strobe_us` | 26 | **23** | 32 | 28 |
| `ctrl_flags` | 30 | **27** | 36 | **32** |
| `chip_id` | 34 | **29** | 40 | 34 |
| `page_size` | 36 | **31** | 42 | 36 |
| `data_buffer` | 38 | **33** | 44 | 38 |
| `data_size` | 550 | **545** | 556 | 552 |
| `bus_config` | 554 | **549** | 560 | 556 |
| **total** | **601** | **596** | **656** | **656** |

**Confirmed exactly:** the eleven table members sit at AVR offsets **3–32** (`protocol` at 3
through `page_size` occupying 31-32), with `data_buffer` at **33** -- matching plan 03's own
measurement byte for byte. The native table shifts too (`protocol` moves from offset 4 to 3,
`ctrl_flags` from 36 to 32) but the native **total is unchanged at 656 B**, because the five
narrowed bytes are absorbed by alignment padding ahead of the struct's trailing
function-pointer block -- ceiling 5, re-confirmed.

**OD-7's `sizeof` figure, re-derived one final time, both architectures, same captured
compiler flags:**
```bash
avr-gcc -std=gnu11 -mmcu=atmega328p -Os -DPLATFORMIO=60119 -DARDUINO_AVR_UNO \
  -DMONITOR_SPEED=250000 -DHARDWARE_REVISION -DDEV_TOOLS -DRURP_BOARD_NAME=\"uno\" \
  -DSERIAL_ON_IO -DF_CPU=16000000L -DARDUINO_ARCH_AVR -DARDUINO=10808 -Iinclude -c off.c -o off.o
avr-nm --print-size --radix=d off.o | grep ' total$'
# => 00000596 00000596 C total
```
```bash
g++ -std=gnu++17 -DMONITOR_SPEED=250000 -DHARDWARE_REVISION -DDEV_TOOLS \
  -DRURP_BOARD_NAME=\"native\" -Iinclude -c off.c -o off.o && nm --print-size --radix=d off.o | grep ' total$'
# => 0000000000001600 0000000000000656 B total
```
**AVR `596` B (5 B below the before-record's `601` B); native `656` B, unchanged.** The
`600`-versus-`601` reconciliation is the before-record's own OD-7 finding (`601` matches
`155-after-figures.md`, superseding `157-RESEARCH.md`'s `600`); this session's re-derivation at
the final position starts from the already-reconciled `601` and confirms the `−5 B` delta.

**The six round-trip cases plus the localisation probe from plan 05 close ceiling 7 by
execution, not by assertion.** `_Static_assert` proves an offset **fits** the `uint8_t` column
and a width fits the 32-bit store -- it does not prove the table writes the **right** member.
Plan 05's six new cases (`mem_size`, `address`, `pulse_delay`, `chip_id`, `vpp_mv`, `pins`)
plus plan 04's two (`protocol`, `ctrl_flags` via the DECODE-05 safety cases) plus the
pre-existing three (`read_settling_us`, `read_strobe_us`, `page_size`) give all **eleven** table
rows an executing native test. Plan 05's own localisation probes (`key_vpp_mv` row's member
swapped to `chip_id`; `key_pin_count` row's member swapped to `page_size`) each reddened
**exactly** their own round-trip case and no other -- proof that a wrong `offsetof` is
detectable by execution, which `_Static_assert` structurally cannot see.

`_Static_assert` in a C translation unit is confirmed as a **new idiom for this repository** --
the only pre-existing static assert is the C++-guarded one at `include/eprom_params.h:62`,
inert in every C TU (re-confirmed this session, unchanged from the before-record).

---

## 6. DECODE-04's evidence -- narrowing, site counts, ceilings

**Two narrowed members**, `include/firestarter.h`, unchanged since plan 03's commit:
`firestarter_handle_t.protocol` is `uint8_t` (bound: largest dispatched value `0x39`,
`PROTO_PHANTOM_0x39`); `.ctrl_flags` is `uint16_t` (bound: largest flag `0x100`,
`FLAG_SKIP_SDP_UNLOCK`), pinned bidirectionally by
`firestarter_app/tests/test_revision_constants_parity.py` at exactly nine flags.

**Measured site counts (plan 03), explicitly superseding the ROADMAP's `19`/`45`:**
```bash
grep -ro "handle->protocol ==" src/ | wc -l          # => 17
grep -rn "switch (handle->protocol)" src/            # => src/proms/eprom.cpp:70
grep -rn -- "->protocol" src/ include/ | wc -l       # => 21 (20 in src/, 1 comment in include/)
```
**18 protocol-keyed dispatch sites** (17 equality comparisons + 1 `switch`), **20 total
`handle->protocol` reads** in `src/`. Neither `19` is reproducible by any counting rule.

```bash
grep -ro is_flag_set src/ | wc -l                                     # => 40
grep -rno "LOG_INFO_ID[A-Z_0-9]*" src/ | wc -l                        # => 19
```
**40 textual `is_flag_set` uses**, **59 post-preprocessor uses** (40 + 19 `LOG_INFO_ID*`
expansions, each expanding to one `is_flag_set(FLAG_VERBOSE)`). Neither `45` is reproducible.

**The five audited consumer surfaces** (plan 03): comparison semantics (identical truth values
via integer promotion on both narrowed members); log payloads (both `protocol` sites already
cast to `uint8_t`; `ctrl_flags` never logged); wire visibility (neither field is serialised
into any response frame -- verified, not assumed); persistence (`rurp_configuration_t` contains
neither field -- explicit "no migration exists" conclusion); and the `uint32_t` parameter
surfaces (`eprom_params_for`, `eprom_block_budget_s` left untouched, recorded as a lead not
taken).

**The `−5 B` RAM saving, confirmed two independent ways, AVR-only (ceiling 5):**
`ram_used` from the build (§2: `1567→1562`, `1573→1568`, `2008→2003`) and the `sizeof`
re-derivation (§5: `601→596`). The native `sizeof` is unchanged at `656` B -- the saving is
unobservable natively, and no native test asserts it, because such a test would be vacuously
false.

**OD-1's mask policy confirmed load-bearing at this final position:** `FIELD_MASK(key_flags,
ctrl_flags)` is still the row's policy (`grep -n 'FIELD_MASK(key_flags' src/json_parser.c` ->
one hit, line 139), preventing a saturate-to-`0xFFFF` that would set `FLAG_FORCE`,
`FLAG_SKIP_ERASE` and `FLAG_SKIP_BLANK_CHECK` simultaneously -- a fail-open in the phase whose
headline criterion is fail-closed (C-7).

---

## 7. DECODE-05's evidence -- the safety requirement

Five native Unity cases in `test_read_timing`, landed by plan 04:

| Case | ID | What it proves |
|---|---|---|
| S1 | `test_out_of_range_algorithm_saturates_not_truncates` | an out-of-range wire `algorithm` saturates to `0xFF`, never truncates to a real handler's protocol value |
| **S2** | `test_out_of_range_algorithm_dispatch_fail_closes` | **load-bearing**: `configure_memory`'s dispatch actually fail-closes (`RESPONSE_CODE_ERROR`, all three operation pointers NULL) -- a correct stored byte (S1) is a different claim from the dispatch refusing the command |
| S3 | `test_in_range_algorithm_still_dispatches` | non-regression guard: S1/S2 cannot be satisfied by breaking every algorithm |
| S4 | `test_out_of_range_flags_masks_never_sets_every_flag` | an out-of-range wire `flags` masks to 0, never saturates to `0xFFFF` (three per-bit assertions plus the equality) |
| S5 | `test_out_of_range_page_size_saturates_not_truncates_to_a_valid_size` | an out-of-range wire `page-size` saturates to `0xFFFF`, not a plausible valid power-of-two size |

**S2 is named load-bearing** because it is the only thing in the repository pinning the
dispatch-table-contingent claim (ceiling 6: saturation-as-fail-closed is contingent on `0xFF`
being unmapped in `configure_memory`'s chain today, a property of the dispatch table, not of
`store_field`).

**Both probe transcripts, verbatim (from `157-04-SUMMARY.md`, captured in a throwaway probe
worktree, fully discarded):**

Probe A (saturation branch deleted from `store_field`):
```
test_read_timing_params.cpp:552:test_out_of_range_algorithm_saturates_not_truncates:FAIL: Expected 255 Was 5. 261 must saturate to 0xFF, not truncate to 0x05 -- 0x05 is PROTO_FLASH_5V_PAGE, a real handler configure_memory would dispatch into
test_read_timing_params.cpp:213:test_out_of_range_algorithm_dispatch_fail_closes:FAIL: Expected 0 Was 1. this is the case that would have caught the defect: the stored byte being right (S1) is not the same claim as the dispatch fail-closing -- a saturated 0xFF must reach configure_memory's generic fail-closed tail
test_read_timing_params.cpp:310:test_out_of_range_flags_masks_never_sets_every_flag:PASS   <- VACUOUS, see C-18
test_read_timing_params.cpp:289:test_out_of_range_page_size_saturates_not_truncates_to_a_valid_size:FAIL: Expected 65535 Was 64. 65600 must saturate to 0xFFFF, not truncate to 64 -- 64 is a perfectly valid page size, which is what makes the hole silent
-----------------------
14 Tests 3 Failures 0 Ignored
FAIL
```

Probe B (`key_flags` row switched from `FIELD_MASK` to `FIELD`, i.e. saturate):
```
test_read_timing_params.cpp:260:test_out_of_range_flags_masks_never_sets_every_flag:FAIL: Expected 0 Was 65535. an out-of-range wire flags value must mask to the width-limited truncation, never saturate to 0xFFFF -- saturating a bitmask turns on every flag at once, a fail-open in a fail-closed phase
-----------------------
14 Tests 1 Failures 0 Ignored
FAIL
```

**C-18, confirmed in practice, not merely cited:** `157-VALIDATION.md`'s Wave-0 row claimed a
single saturation-deleted probe reddens S1, S2 AND S4. Probe A's own run above shows this is
false for S4: it **passes vacuously** there, because a truncating (non-saturating) store
reduces a wire `flags` of `65536` to `0` before any policy check runs, and S4's `ctrl_flags ==
0` equality holds by coincidence. Two distinct probes are required and are not interchangeable
-- Probe A reddens S1/S2/S5, Probe B reddens only S4.

**C-20:** S5's consumer-side half is recorded as source-level evidence only, not an assertion:
`eeprom28c_page_mask` is `static` in `src/proms/eeprom_28c.cpp` and unreachable from any test.
`0xFFFF` fails both its guards (exceeds `AT28C_PAGE_SIZE_MAX` 512, and fails the power-of-two
test), so the function returns `AT28C_PAGE_SIZE_FALLBACK − 1` (63), a mask, not the size (64).

**Ceiling 6, stated explicitly:** saturation-as-fail-closed is contingent on `0xFF` being
unmapped in `configure_memory`'s dispatch chain -- a property of the dispatch table, not of
`store_field` -- true only today, and pinned by S2 and by nothing else.

---

## 8. DECODE-06's evidence -- the read-timing cap

`#define READ_TIMING_MAX_US 1000UL` is hoisted above `key_parsers[]` (`src/json_parser.c:71`,
above the table at `:133`) -- the `clamp` column now folds T-44-01's requirement directly into
the table.

**The strobe cap case that did not exist before (C-8), landed by plan 05:**
`test_read_strobe_us_capped_at_max` -- parses `{"cmd":1,"read-strobe-us":9999}` and asserts an
**equality** against `READ_TIMING_MAX_US`. The pre-existing `test_read_settling_us_capped_at_max`
was tightened from `TEST_ASSERT_TRUE(<=)` to `TEST_ASSERT_EQUAL_UINT32`.

**The equality-RED / upper-bound-GREEN contrast (probe C2, verbatim from `157-05-SUMMARY.md`),
on `store_field`'s clamp step changed to store `0` instead of the clamp value:**
```
test_read_timing_params.cpp:161: test_read_settling_us_capped_at_max: Expected 1000 Was 0. ... [FAILED]
test_read_timing_params.cpp:178: test_read_strobe_us_capped_at_max: Expected 1000 Was 0. ... [FAILED]
============ 16 test cases: 2 failed, 13 succeeded ============
```
Same broken tree, `test_read_settling_us_capped_at_max` temporarily reverted to its old
upper-bound form:
```
test_read_timing_params.cpp:331: test_read_settling_us_capped_at_max	[PASSED]
test_read_timing_params.cpp:175: test_read_strobe_us_capped_at_max: Expected 1000 Was 0. ...	[FAILED]
============ 16 test cases: 1 failed, 14 succeeded ============
```
**The upper-bound form PASSES on the identical clamp-to-zero-broken tree that reddens the
equality form** -- the measured (not merely asserted) justification that tightening the
assertion added real coverage: `0` passes an upper bound, and `0` is the loaded value for
**both** knobs (`read_settling_us == 0` means no settling delay; `read_strobe_us == 0` means
use the firmware default of 3 microseconds), so the weaker form was dangerous, not merely
loose.

**C-21, the unremovable duplicate:** two `READ_TIMING_MAX_US` definitions exist (the
production `#define` at `src/json_parser.c:71`, a file-scope constant in a `.c` translation
unit; the test-local `#define` in `test_read_timing_params.cpp`) with no header export linking
them -- the test cannot reference the production constant directly. Recorded in a drift-risk
comment above the test-local definition, not fixed.

---

## 9. DECODE-07 -- the rejected alternative, recorded

**This section is what discharges DECODE-07. No code changed to discharge it.**

**Fresh three-target `switch`-vs-if-chain measurement (plan 06), built once in a throwaway
detached worktree at `785e644`, discarded before this record was written:**

| Target | `switch` (probe) | if-chain (committed) | Delta | RAM (both) |
|---|---|---|---|---|
| `uno` | 23108 | 23090 | **+18 B** | 1562 |
| `uno328pb` | 23156 | 23138 | **+18 B** | 1568 |
| `leonardo` | 25252 | 25234 | **+18 B** | 2003 |

Behavioural-equivalence check, same probe tree: `pio test -e native` -> `184 test cases: 184
succeeded`, identical to the committed tree's own count. `src/proms/memory.cpp` is
byte-identical to its blob at `1151dc4`, confirmed again this session
(`git diff --quiet 1151dc4 HEAD -- src/proms/memory.cpp` exits 0) -- the `switch` form exists in
no commit anywhere.

**The survey's original pair, named with provenance and marked SUPERSEDED as absolutes, never
in place of the fresh pair:** `.planning/notes/firmware-size-reduction-survey.md` cites `uno`
**25696** (switch) vs **25678** (if-chain), a `+18 B` claim. Those absolutes predate Phases 155
and 156 and this phase's own reductions -- `157-before-figures.md` records `uno` at `24234`
before Phase 157 even begins, and the committed if-chain figure at this final position is
`23090`, stale by roughly 1.4-2.6 KB (C-10). **The magnitude coincides (+18 B both times); the
absolutes do not.** The survey's pair was measured on a `switch (handle->protocol)` where
`protocol` was still `uint32_t` (pre-narrowing); this plan's pair is measured on the now-`uint8_t`
`protocol` at Phase 157's near-final position. Two measurements landing on the identical delta
despite a materially different switched-expression width and absolute baseline is a coincidence
of magnitude, not a confirmation of the same measurement.

**The dispatched value set, from source:** 17 distinct protocol values reach a non-generic arm
-- 13 named `PROTO_*` constants plus 4 raw-hex named-infeasibility literals, spanning `0x05` to
`0x39` (range 53), density **17/53 ≈ 32%**. This sparse, wide spread is exactly the property
gcc's jump-table-versus-comparison-chain decision turns on.

**Second rejection argument:** `firestarter/CLAUDE.md` §Protocol Dispatch pins
`configure_memory`'s if-chain dispatch order as a source-of-truth contract (seven numbered
steps matching the file's structure). `git diff --quiet 1151dc4 HEAD -- CLAUDE.md` exits 0 this
session -- the document needed no edit, because the if-chain was never converted. A `switch`
conversion would require rewriting that section too.

**C-22, the single-configuration ceiling:** one compiler (avr-gcc 7.3.0), one optimisation
level (`-Os`), one dispatched value set, one tree position (`785e644`). Not a general claim
about `switch` versus if-chain dispatch.

---

## 10. The gate ledger -- all eight legs

| # | Leg | Command | Result | In CI? |
|---|---|---|---|---|
| 1 | Cold AVR build, all 3 targets | `rm -rf .pio/build/<env>; pio run -e uno -e uno328pb -e leonardo` | flash 23090/23138/25234, RAM 1562/1568/2003, **zero** `warning:` lines | yes (build) |
| 2 | `pio test -e native` | `pio test -e native` | **184 test cases: 184 succeeded**, 17 suites | yes |
| 3 | `pio test -e native_nodevtools` | `pio test -e native_nodevtools` | **184 test cases: 184 succeeded**, 17 suites | yes |
| 4 | `check_build_warnings.py` | `python3 scripts/check_build_warnings.py --rebuild` | **PASS**: `macro_redefinition=0` on all three AVR targets; `native`/`native_nodevtools` both `998` warnings, `168` below the `1166` watermark (INFO only) | **NO CI workflow** |
| 5 | `check_no_heap_or_64bit_symbols.py` | `python3 scripts/check_no_heap_or_64bit_symbols.py` | **PASS**: `heap=0,64bit=0,anchors=2/2` on all three AVR targets | **NO CI workflow** |
| 6 | `check_size_baseline.py --policy merge05` | `python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json --rebuild` | exit 1: `FAIL: native: cases baseline=141 observed=184` / `native_nodevtools: cases baseline=141 observed=184` -- **exactly two lines, both native case counts; no AVR flash or RAM leg fails** | **NO CI workflow** |
| 7 | `check_size_baseline.py` (default mode) | `python3 scripts/check_size_baseline.py --rebuild` | exit 1: `uno: flash_used baseline=25548 observed=23090`, `uno: ram_used baseline=1575 observed=1562`, `uno328pb: flash_used baseline=25598 observed=23138`, `uno328pb: ram_used baseline=1581 observed=1568`, `leonardo: flash_used baseline=27630 observed=25234`, `leonardo: ram_used baseline=2016 observed=2003`, `native: cases baseline=172 observed=184`, `native_nodevtools: cases baseline=172 observed=184` -- **the pre-existing `flash_used`/`ram_used` byte-identity failures Phases 155 and 156 already caused, plus the native case-count growth this phase and its predecessors added** | **NO CI workflow** |
| 8 | Host suite | `python3 -m pytest tests/ -q -o addopts=""` (`/workspaces/firestarter_app`, on the committed firmware tree, no `.rej`/`.orig` file present) | **1976 passed, 0 failed, 0 skipped**, 32 snapshots, 234.89 s | yes |

**Legs 4, 5, 6 and 7 run in NO CI workflow.** Every gate in this phase beyond the four CI legs
(`pio test -e native`, `pio test -e native_nodevtools`, `pytest tests/`, `pio run`) is a
**local-run obligation**. A green CI run is not evidence that the size gate passed.

**Legs 6 and 7's expected shape, confirmed exactly:** leg 6 fails on the native `cases` lines
only, with no AVR flash or RAM leg among the failures. Leg 7 (default mode, checked against the
stale `size_baseline.json` last re-anchored before Phase 155) fails on every AVR `flash_used`/
`ram_used` line **because the image shrank**, which is the pre-existing byte-identity failure
Phases 155 and 156 already caused (their own reductions already made `size_baseline.json` stale
before Phase 157 touched anything), plus the native case-count lines this phase's own new tests
(172→177→184) additionally moved.

---

## 11. The one-sidedness, quoted from source

```bash
sed -n '697p;709p' scripts/check_size_baseline.py
```
```
697:    if flash_delta > allowance:
709:    if ram_delta > ram_tolerance:
```
**Both strict-inequality, growth-only comparisons.** A reduction in flash or RAM passes with
**no named exemption** -- this phase's `−1144 B` / `−5 B` reduction is recorded as a
**ONE-SIDED** pass on leg 6 above, so nobody later reads that green run as "no size change"
(D-03). No exemption constant was authored.

---

## 12. The coverage ceilings -- final form

All ten from the plan's own frontmatter, plus C-20, C-21, C-22 as ceilings in their own right:

1. **`src/json_parser.c` IS natively covered (F-3), stated as a NEGATIVE ceiling.**
   `build_src_filter` includes `+<json_parser.c>`, and `test_read_timing` drives `json_parse`
   against a real `jsmn_parse`. Every behavioural criterion in this phase is reachable by a
   native test that CI runs. **This phase has no coverage gap of Phase 155's kind, and this
   record does not borrow that phrasing.**
2. **`src/firestarter.cpp` and `src/eprom_operations.cpp` are OUTSIDE the native `src_filter`.**
   Between them they hold 8 of the 40 `is_flag_set` uses and the `eprom_block_budget_s` call.
   The narrowing's effect there is proven only by compilation, never by execution.
3. **`src/dev_tools.cpp` is outside too** -- 9 `is_flag_set` uses plus 7 `LOG_INFO_ID*`
   expansions, the single largest concentration. Compile-only coverage.
4. **DECODE-01 and DECODE-02 have NO automated gate.** They are the measurements in §3 and §4
   of this record. No test asserts that the ten deleted stubs stayed deleted or that a key is
   stored once. A future phase could silently reintroduce either. Not described as gated
   anywhere in this record.
5. **The `−5 B` RAM saving is unobservable natively** (native `sizeof` is `656` either way).
   AVR-only.
6. **Saturation-as-fail-closed is CONTINGENT on `0xFF` being unmapped** in `configure_memory`'s
   dispatch chain -- a property of the dispatch table, not of `store_field`, true only today,
   pinned by S2 and by nothing else.
7. **`_Static_assert` proves offsets fit `uint8_t` at build time -- it does NOT prove the table
   writes the right member.** Only the native parse tests do that (§5); plan 05 closed this for
   all eleven rows, by execution, not by assertion.
8. **No bench coverage, by design (D-02).** No criterion needs silicon; nothing here is claimed
   of real hardware.
9. **`check_size_baseline.py` and `check_build_warnings.py` run in NO CI workflow**
   (re-confirmed §10). Every gate in this phase beyond the four CI legs is a local-run
   obligation.
10. **The reference patch does not apply cleanly (C-11)**: hunk #3 fails at every `-C` level
    because Phase 154's sweep changed its context. The implementation was a hand-port.
11. **C-20**: S5's consumer-side half (`eeprom28c_page_mask`) is source-level evidence only --
    the function is `static` and unreachable from any test.
12. **C-21**: the two `READ_TIMING_MAX_US` definitions are an unremovable duplicate with an
    ungated drift risk -- the production constant has no header export.
13. **C-22**: the `switch` delta is a single-configuration measurement -- one compiler version,
    one optimisation level, one dispatched value set, one tree position.

---

## 13. The corrections ledger -- every row closed out

| # | ROADMAP / REQUIREMENTS says | Measured (this phase) | Outcome |
|---|---|---|---|
| C-1 | `json_parse_config` calls `get_flags` "directly at two sites" | `get_flags` is called once in `json_parse_config` (`:348`) and once in `json_get_cmd` (`:379`) -- two DIFFERENT functions | **CLOSED**, re-confirmed final position, §4 |
| C-2 | Per-stub cost is "86-110 B each" | **84-110 B** -- `get_pin_count` measures 84 B, below the stated floor | **CLOSED**, §3 |
| C-3 | "Ten of eleven were stored twice" | **Eleven** of eleven, including `flags` (pre-phase, mangled to `Uflags`); today **zero** of eleven are stored twice | **CLOSED**, §4 |
| C-4 | ROADMAP split "field table −976, narrowing + saturation −172" | Measured: table half **−884 B**, narrowing half **−260 B**, composed **−1144 B** (cold-to-cold, this session) | **CLOSED**, §2 |
| C-5 | "19 protocol comparisons" and "45 `is_flag_set` call sites" | **18** protocol-keyed sites / **20** total `->protocol` reads; **40** textual `is_flag_set` / **59** post-preprocessor | **CLOSED**, §6 |
| C-6 | DECODE-05's per-stub form "could not" saturate `pins`/`chip_id`/`vpp_mv`/`page_size` | Those four are already narrow and already silently truncated by `extract_int`/`extract_long`; only `protocol` and `ctrl_flags` gain a genuinely new hole | **CLOSED**, §7 |
| C-7 | (omission) saturating `ctrl_flags` would set every dangerous flag | `ctrl_flags` uses `FIELD_MASK`, never saturates (OD-1); confirmed load-bearing at final position, §6 | **CLOSED** |
| C-8 | DECODE-06 "proven by a test" | `read-strobe-us` had NO cap test before this phase; plan 05 added one and tightened both assertions to equality | **CLOSED**, §8 |
| C-9 | (implicit) the `#define` must move | Hoisted to `src/json_parser.c:71`, above the table at `:133`, confirmed this session | **CLOSED**, §8 |
| C-10 | DECODE-07 cites `uno` 25696 (switch) vs 25678 (if-chain) | Fresh pair at this position: `uno` 23108 (switch) vs 23090 (if-chain), +18 B, coincidentally matching magnitude only | **CLOSED**, §9 |
| C-11 | (implicit) patch applies like Phase 156's | Does NOT apply cleanly: hunk #3 fails at every `-C` level (before-record §7); implementation is a hand-port | **CLOSED** (before-record) |
| C-12 | (implicit) phase is firmware-only | With the reference change, one host gate would go RED and its sibling pass vacuously unless `key_parsers` kept (OD-2) -- kept, zero `firestarter_app` files changed this phase | **CLOSED**, plan 02/03 SUMMARYs |
| C-13 | Leonardo Caterina headroom "3440 B" | **3438 B**, measured cold at the final position (`28672 − 25234`) | **CLOSED**, §2 |
| C-14 | Criterion 3's compile-time assertion "prevents a future struct reorder" | The reference patch's single assert guards `page_size` only; the shipped implementation carries all eleven per-member guards plus the row-count guard (twelve total) | **CLOSED**, §5 |
| C-15 | (implicit) case count stays 172 | Moved **172 -> 177 -> 184** on both native envs, 17 suites unchanged | **CLOSED**, handed to Phase 158 / LAND-01, §14 |
| C-16 | (implicit) some CI leg might run the size gate | `check_size_baseline.py` runs in NO CI workflow, re-confirmed this session | **CLOSED**, §10 |
| C-17 | RESEARCH cites `#define READ_TIMING_MAX_US` at `:352`; DECODE-01 table off-by-one line listing | Pre-phase it sat at `:360`; post-hoist (plan 02, DECODE-06) it sits at `:60`, above the table | **CLOSED** |
| C-18 | VALIDATION's Wave-0 row: a single saturation-deleted probe reddens S1, S2 AND S4 | FALSE for S4 -- Probe A leaves S4 passing vacuously; a second, saturating-bitmask probe is required and reddens only S4 | **CLOSED**, §7, confirmed in practice by plan 04 |
| C-19 | (implicit) the `−890`/`−258`/`−1148` figures apply unconditionally | Measured on a reference table with no per-row policy column; OD-1's `FIELD_POLICY_MASK` column costs the observed 6 B/2 B/4 B divergences | **CLOSED**, §2 |
| C-20 | (found by plan 04) S5's consumer-side rejection has no oracle | `eeprom28c_page_mask` is `static`, unreachable from any test; recorded as an in-file comment | **CLOSED**, §7 |
| C-21 | (found by plan 05) the two `READ_TIMING_MAX_US` definitions could drift silently | Confirmed unremovable -- the production `#define` is a `.c`-TU file-scope constant with no header export; recorded in a drift-risk comment, not fixed | **CLOSED**, §8 |
| C-22 | (found by plan 06) the `switch` measurement might generalise | It does not -- single compiler, single optimisation level, single dispatched value set, single tree position; stated as such | **CLOSED**, §9 |

---

## 14. The seven decisions OD-1 through OD-7

- **OD-1 -- out-of-range policy: saturate for ordinals, MASK for bitmasks.** `ctrl_flags` masks
  (`v &= max`), never saturates -- saturating to `0xFFFF` would set `FLAG_FORCE`,
  `FLAG_SKIP_ERASE` and `FLAG_SKIP_BLANK_CHECK` simultaneously (C-7), a fail-open regression in
  the phase whose headline criterion is fail-closed. **Declined: `reject` semantics.** Rejecting
  an out-of-range command needs a new message id, meaning editing `tools/catalog/messages.toml`
  in the **meta** repo and regenerating `include/messages.h` -- codegen-generated, never
  hand-edited. That cross-repo codegen step would break this phase's firmware-only property.
  This same policy column costs the `−884`/`−260`/`−1144` divergences from the reference's
  `−890`/`−258`/`−1148` (C-19), a cost this record states rather than engineers away.
- **OD-2 -- the identifier `key_parsers` is KEPT, now slightly stale.** Renaming it turns
  `firestarter_app/tests/test_json_key_parity.py::test_page_size_key_string_matches_constants_py`
  RED and makes its sibling leg pass vacuously (measured: 3 failures against a 24-passed
  baseline, C-12). **Declined: renaming to something more accurate, e.g. `field_table`.** After
  plan 02, `key_parsers` is a data table of `{key, clamp, offset, width}`, not a table of
  parsers -- the name is now stale, and it was kept anyway because renaming costs a
  `firestarter_app` commit and an explicit ROADMAP abandonment of the firmware-only claim.
  Keeping it costs nothing at build time and keeps this phase's `firestarter_app` commit count
  at zero.
- **OD-3 -- `get_flags` is pointed at `key_flags` directly, making single-key-storage a source
  property.** Without this, the before-record's own A6 records the `flags` string-dedup as a
  toolchain outcome it could not explain. **Declined: depending on the toolchain to keep
  deduplicating `flags` indefinitely.** That would leave DECODE-02's single-storage claim
  un-provable by source inspection; this session's own §4 measurement is a re-derivation, not an
  assumption, precisely because OD-3 makes it a source property.
- **OD-4 -- DECODE-07's `switch` alternative is re-measured at this phase's final position, not
  quoted from the stale survey absolutes.** §9's fresh pair (`uno` 23108/23090) supersedes the
  survey's `25696`/`25678`. **Declined: quoting the original absolutes as current.** That would
  misstate the delta's magnitude even though its sign happens to still be correct.
- **OD-5 -- six additional store-round-trip cases** (`mem_size`, `address`, `pulse_delay`,
  `chip_id`, `vpp_mv`, `pins`), closing coverage ceiling 7. **Declined: leaving those six fields
  with no native round-trip oracle.** The case count already moved for DECODE-05/06 (C-15), so
  six more cost nothing additional in gate terms.
- **OD-6 -- run both `check_build_warnings.py` and `check_no_heap_or_64bit_symbols.py`
  explicitly, rather than assuming they stay green.** Confirmed this session (§10, legs 4-5)
  both PASS. **Declined: inferring from the raw AVR `warning:` grep count (0) that both scripts
  would also pass.** The native macro-redefinition watermark has near-zero headroom (998
  observed, 168 below 1166); assuming rather than running risks silently crossing it.
- **OD-7 -- `sizeof(firestarter_handle_t)` is re-derived from the real `pio run -v` compiler
  flags, yielding ONE number per architecture at every position: `596` B AVR / `656` B native at
  this final position** (§5). **Declined: quoting either the research probe's `600` B or a
  stale `655` B native figure without re-deriving.** Re-deriving at each plan's own position
  (before-record: `601`/`656`; plan 03: `596`/`656`; this record: confirms `596`/`656` unchanged
  since plan 03, since plans 04-06 touch no struct member) keeps every figure first-party.

---

## 15. The 999.35 / v1.28 non-additivity warning

`REQUIREMENTS.md`'s Backlog **999.35** entry states DECODE-01's field table is **superseded** if
the binary command protocol (v1.28) ever lands -- the field table is the JSON-decode surface the
binary protocol would replace outright. **This phase's `−1144 B` (§2) and 999.35's own
`leonardo` figures (`−3728 B` / `−512 B`, cited from that backlog entry) are NOT additive.** If
999.35 is ever taken, it must be **re-measured from the post-v1.33 position** before anyone
quotes a combined saving -- quoting `−1144 − 3728` as a single number would double-count
whatever this phase's field table already removed. The operator ruled the binary command
protocol **out of v1.33 scope** on 2026-08-22; this record proposes no step toward it (a
standing prohibition carried in this plan's own frontmatter). Stated here because a reader of
this figures record will not necessarily reach the backlog entry that carries this caveat.

---

## 16. Handoffs

**To Phase 158:**
- The native case-count trajectory **172 -> 177 -> 184** on BOTH `native` and `native_nodevtools`,
  in lockstep, suite count unchanged at **17**. `scripts/baseline/size_baseline.json` still
  records `172` today (confirmed this session, leg 7) -- **LAND-01** owns the cold re-record.
- `scripts/baseline/size_baseline_base01.json` records `141`, frozen at Phase 124 -- **LAND-03**
  owns the native-case-count-mismatch resolution (currently `184` observed against `141` frozen).
- **Every headline figure in this record is COLD** (§2); every intermediate plan figure (02
  through 06's own SUMMARYs) was WARM at the moment it was measured, though every WARM figure
  this session re-verified turned out byte-identical to its COLD counterpart at the same tree
  position -- stated as an observation, not a general guarantee for Phase 158 to rely on.
- The MERGE-05 pass is **ONE-SIDED** (§11, D-03) -- a green run on leg 6 proves only that
  flash/RAM did not grow past the allowance, never that "nothing changed".
- Leonardo's Caterina headroom against `28672` is **3438 B** at the final Phase 157 position
  (§2) -- Phase 158's own cold re-anchor will move this further if it lands any further size
  change.

**To Phase 159:**
- Every `file:LINE` citation in this record and in `157-before-figures.md` was measured against
  the current, post-Phase-154 tree and will be remapped **once**, over the composite diff
  (D-01, D-05). This record's own §3-§9 citations (e.g. `src/json_parser.c:71`, `:133`,
  `:176-221`, `:348`, `:379`) are current as of `785e644` and will shift again once Phase 158
  lands its own edits.
- Plan 02's two new `#include` lines (`<stddef.h>`, `<string.h>`) shifted every citation in
  `src/json_parser.c` by `+2` from plan 02 onward, per the before-record's own §"This document's
  own file:LINE citations" note -- expected, not a defect.

---

## Self-verification of this record

`git -C firestarter status --porcelain` is empty and `git -C firestarter rev-parse HEAD` equals
`785e644bacbe128de813407f0e6e357c71164836` at the end of this task -- this plan's own
measurement work edited no tracked file under `firestarter/`. Every probe in this record (the
cold-before worktree at §2, the two planted-negative diagnostics at §5) was planted in a
throwaway `git worktree add --detach` (leaf directory named exactly `firestarter`), reverted,
and the worktree removed and pruned; `git -C firestarter worktree list` matched its pre-probe
output after each. Every figure above can be re-derived by running the exact command quoted
beside it, on the committed tree at `785e644`, with no other tree state assumed.
