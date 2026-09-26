# Phase 156: Duplicated-Report Extraction + Boolean-Convention Repair (firmware-only) — Research

**Researched:** 2026-08-23
**Domain:** AVR C/C++ firmware de-duplication under LTO; PlatformIO/Unity native test coverage; committed source-contract gates
**Confidence:** **HIGH** — every headline figure in this document was measured in this session, in a throwaway worktree off `adf1a31`, and the tree was returned clean and verified clean afterwards. Nothing here is transcribed from the survey without re-measurement.

---

## Summary

Phase 156 lands three things into `firestarter/`: two shared report helpers in `src/proms/memory.cpp`
that replace eight copy-pasted blocks across four translation units, and the removal of the
`return !op_execute_*_operation(...)` convention in `src/eprom_operations.cpp`. All of it is
already implemented in two places — the applyable patch and a preserved git ref — **except**
DEDUP-04, which exists nowhere and must be authored.

The de-duplication half is fully de-risked. It applies to today's tree with `git apply -C1`,
it builds, it measures **exactly −426 B flash on all three AVR targets with RAM unchanged**, and
both CI native environments plus the non-CI `native_loop_v131` VPP suite stay green. The survey's
per-function attribution reproduces to the byte (`eprom_check_vpp` 524→280, `flash_intel_write_init`
562→348, helper 190 B), and `__udivmodhi4` call sites fall to 13.

The risk is entirely elsewhere, in three places the ROADMAP does not mention. **(1)** Committing the
edit turns **two legs of `tests/test_protocol_branch_inventory.py` RED** — a CI-visible gate that
pins `src/proms/eprom.cpp`'s blob SHA and its branch-predicate inventory positionally. It must be
re-derived in the same commit as the source change, per that golden's own `how_to_update`. **(2)** The
DEDUP-04 flip is size-neutral but **not** byte-identical — the `.hex` SHA changes on all three
targets — so an oracle asserting image identity would fail; the claim is a size claim. **(3)** The flip
turns one native case RED and silently guts a second into a vacuous pass, which means
REQUIREMENTS' claim that DEAD-06 is "the only requirement in Phases 155–158 that touches a test
file" is false.

And for DEDUP-03 the coverage ceiling is now measured rather than argued: four planted
transpositions show that the VPP over-voltage severity fork is caught only by a suite CI never
runs, while **the under-voltage severity pairing and the chip-ID message-id fork are caught by
nothing at all**.

**Primary recommendation:** land DEDUP-01 and DEDUP-02 as **two separate commits** (so each
requirement gets its own measured figure, since the −268/−158 split is unverified at this
position), re-derive `tests/golden/protocol_branch_inventory.json` in the same commit as the
`eprom.cpp` edit, close the two measured DEDUP-03 blind spots with new cases in
`test_vpp_eprom_v131` (whose gate is a floor, not an equality) plus one case in the CI-visible
`test_eeprom28c_sdp`, and land DEDUP-04 last as a stand-alone commit whose oracle is
`flash_used`/`ram_used` identity on all three targets — never `.hex` identity.

---

<user_constraints>
## User Constraints

**There is no `156-CONTEXT.md`, by design (OD-1).** The operator chose "continue without context"
at the plan-phase §4 gate, on the Phase 155 precedent. The hand-authored ROADMAP §156 criteria and
the DEDUP-01…04 requirement texts **are** the decision record. Their absence is not an open
question and must not be researched as one.

### Locked Decisions

**From the operator, this session:**

- **OD-1** — No CONTEXT.md. ROADMAP §156 + REQUIREMENTS §3 are the decision record.
- **OD-2 — DEDUP-04 is RESOLVED: REMOVE the inversions.** The plan must invert the 6 return paths
  inside `op_execute_stateful_operation`, drop all 9 `!` at the `eprom_*` wrapper call sites, and
  delete the defensive comment about the load-bearing `!`. The "or explicitly declined with the
  measurement cited" half of criterion 4 is **dead** and must not be researched as a live option.
  What must be researched instead — and is, in §DEDUP-04 below — is how the plan re-proves the flip
  is byte-for-byte zero on all AVR targets from *this* position, and what could make it come out
  non-zero now that Phase 155 has landed underneath it.

**From ROADMAP §v1.33, binding on every phase:**

- **D-01** Phase 154 sweeps source and *builds* the remap tool; **Phase 159 applies it once** over
  the composite diff. 723 citations would otherwise be remapped twice; 41 % of that rework traces
  to four added `#include` lines.
- **D-02** No success criterion requires a physical board.
- **D-03** MERGE-05 is one-sided (`check_size_baseline.py:697` is `if flash_delta > allowance`), so
  a shrink needs **no** named exemption — recorded *as* one-sided so nobody reads the green run as
  "nothing moved".
- **D-04** The native suite is **load-flaky** (172/172 at ~35 s ×5; 171/172 at 1:13;
  158-cases-2-ERRORED at 1:44 — failure tracks run *duration*, not tree content). No phase may
  blame its own change on N=1.
- **D-05** The Phase-154→159 citation staleness is temporary, **marked, and close-blocking** via
  REMAP-04.

**From ROADMAP §156 (the phase's own criteria):** quoted in full in `## Phase Requirements` below.

### Claude's Discretion

- The **shape** of the DEDUP-03 mismatch test — which suite it lives in, how many cases, and
  whether the planted-transposition demonstrations are committed or run-and-recorded. §DEDUP-03
  lays out three options with their measured consequences and recommends one.
- Whether `mem_util_report_voltage` keeps the reference implementation's 5-parameter
  `(handle, measured, expected, msg_id, response_code)` signature or moves to a transposition-proof
  shape. §DEDUP-03 Option 3 costs this out. The default is to keep the reference signature,
  because that is the signature the −426 B was measured against.
- Plan/commit decomposition, wave structure, and which gate runs sit at which commit.
- Whether the `−268 / −158` per-requirement split is measured (two commits) or left unquoted.

### Deferred Ideas (OUT OF SCOPE)

- **Re-anchoring `scripts/baseline/size_baseline.json`.** That is Phase 158 / LAND-01. Do not do it
  here, and do not soften a gate to avoid it.
- **BASE-01's pre-existing `cases baseline=141 observed=172` mismatch.** Phase 158 / LAND-03.
- **The `jsmntok_t` 8→6 B narrowing**, the `flash_5v_page` modulo→mask trade, and `NUMBER_JSNM_TOKENS`.
  Phase 158 / LAND-05…07.
- **`json_parser.c`'s field table and the `protocol`/`ctrl_flags` narrowing.** Phase 157 / DECODE-01…07.
  The measured patch contains these hunks; they are **not** this phase's.
- **Citation remap.** Phase 159 / REMAP-01…05. Line-number staleness this phase creates in
  `.planning/` is EXPECTED and close-blocked by REMAP-04 (D-05). Do not remap here.
- **Shipping raw mV over the wire instead of pre-formatted decimal digits.** The survey notes the
  host could do the division for free, but that is a wire change (`messages.toml` + host parity).
  Out of scope: criterion 1 requires the emitted 8-byte payload be **unchanged**.
- **A binary command protocol.** v1.28 / Backlog 999.35.
</user_constraints>

---

## Phase Requirements

| ID | Description (abridged from REQUIREMENTS §3) | Research support |
|----|---------------------------------------------|------------------|
| **DEDUP-01** | One `mem_util_report_voltage()` replaces four byte-identical VPP packing blocks; 8-byte payload unchanged; arithmetic preserved exactly including the `uint16 + 50` promotion; `__udivmodhi4` 30 → 13; measured −268 B | §DEDUP-01 (promotion analysed at the C level; payload byte map derived; `__udivmodhi4` counted live at **31 → 13** — see C-2); §Measured Figures |
| **DEDUP-02** | One `mem_util_report_chip_id()` replaces four chip-ID blocks; the copies had drifted; the resolved single semantic is **stated, not silently chosen**; measured −158 B | §DEDUP-02 (all four sites quoted verbatim, six divergences enumerated, one semantic proposed with per-divergence reasoning) |
| **DEDUP-03** | The WARNING/ERROR fork is proven preserved **by a test that can see it**. A golden trace matching on id alone cannot detect a swapped `response_code`. A mismatch test is required | §DEDUP-03 — four planted transpositions run against both CI native envs and the non-CI `native_loop_v131`; two blind spots located; three options costed |
| **DEDUP-04** | The nine `return !op_execute_*_operation(...)` inversions are **removed** (OD-2). Re-prove the flip is byte-for-byte zero | §DEDUP-04 — the flip authored and measured on all three targets; 6 return sites enumerated including two non-literal traps; test blast radius measured (1 RED + 1 silent vacuity) |

---

## Architectural Responsibility Map

| Capability | Primary tier | Secondary tier | Rationale |
|------------|--------------|----------------|-----------|
| Packing a VPP-mismatch report payload and setting `response_code` | **Firmware — shared memory-utility layer** (`src/proms/memory.cpp`, declared in `include/memory_utils.h`) | Protocol handlers (`eprom.cpp`, `flash_intel.cpp`) supply the readings and choose the severity | The packing is protocol-independent; the *policy* (which severity a given reading earns) is protocol-dependent. Splitting there is what makes the extraction a de-duplication rather than a behaviour change. |
| Deciding VPP severity (over / under / in-range, FLAG_FORCE downgrade) | **Firmware — protocol handler** | — | The thresholds differ per family (`+500` absolute high edge, `×95/100` relative low edge) and the FLAG_FORCE downgrade is a per-call-site policy. Must not move into the helper. |
| Comparing a read chip ID against the expected one and reporting a mismatch | **Firmware — shared memory-utility layer** | Handlers pass `warn_only` | The comparison and the 4-byte payload are identical at all four sites; only the *derivation* of `warn_only` differs (see §DEDUP-02). |
| Choosing WARN vs ERROR **severity encoding** | **Firmware — message catalog** (`include/messages.h`, codegen'd from meta's `tools/catalog/messages.toml`) | — | Every `LOG_{WARN,ERROR}_ID_BYTES` macro is the same alias of `LOG_ID_BYTES` (verified: `include/logging_id.h:105,119`), so severity rides **entirely** in the message id. This is what makes the consolidation cheap and what makes it dangerous. |
| Signalling "this command is finished" to `loop()` | **Firmware — op layer** (`src/operation_utils.cpp`) | Command wrappers (`src/eprom_operations.cpp`), `switch` in `src/firestarter.cpp:309-354` | DEDUP-04 moves the polarity from the 9 wrappers into the 6 engine returns. The wrappers' own early-exit `return true;` literals are unaffected (they already mean "done"). |
| Human-facing decimal formatting of a millivolt reading | **Firmware** today (4 × `uint16` BE over the wire) — could be host | — | Recorded because it is the obvious next reduction and is explicitly out of scope: moving it is a wire change. |

---

## Prior Art — two carriers, and exactly what applies

DEDUP-01/02 are **already implemented**, in two independent places. DEDUP-04 is in **neither**.

| Carrier | What it holds | State |
|---------|---------------|-------|
| `.planning/notes/firmware-size-reduction-measured.patch` | 11 files, composing survey findings 1+2+3+4+5+8. Findings **3 and 4 = DEDUP-01/02** are present. Finding **7 = DEDUP-04 is absent.** | `[VERIFIED: hunk enumeration + git apply --check, this session]` |
| `wip/v1.33-size-reduction-survey-preserved` @ `a6b46f8` (firmware repo) | Committed. Carries `mem_util_report_voltage` (memory.cpp + memory_utils.h + 2 sites each in eprom.cpp / flash_intel.cpp) and `mem_util_report_chip_id` (memory.cpp + 4 call sites). Still carries **all 9** `return !op_execute_` inversions. | `[VERIFIED: git grep against the ref, this session]` |

⚠ **`size-reduction-survey` (the branch named in the survey's front-matter and in ROADMAP §v1.33) does
NOT carry this work.** `git diff HEAD size-reduction-survey -- src/proms/eprom.cpp
src/proms/flash_intel.cpp include/memory_utils.h` is **empty**. The survey left its changes
uncommitted; `wip/v1.33-size-reduction-survey-preserved` @ `a6b46f8` is the ref that preserved
them. Use that one. `[VERIFIED: git diff, this session]`

### Applying the patch — measured, hunk by hunk

The Phase-156 subset is six files. `git apply --check` on the whole subset **fails on one file
only**:

```
include/memory_utils.h      OK   (blob 524f407 — byte-unchanged since the survey)
src/proms/eprom.cpp         OK   (blob 838aca4 — byte-unchanged; Phase 154's sweep did not touch it)
src/proms/flash_intel.cpp   OK   (blob 057bf44 — byte-unchanged)
src/proms/flash_utils.cpp   OK
src/proms/memory.cpp        OK   (hunk 1 only, applies at offset +4)
src/proms/eeprom_28c.cpp    FAIL at :300 — trailing context "// FIX-01: a 0x0D-local…" was
                                 swept to "// A 0x0D-local…" by Phase 154 (2ad5b32)
```

`git apply -C1` and `git apply --3way` both apply the **whole subset cleanly** (the eeprom_28c
fragment lands at 289, offset −11). `[VERIFIED: git apply --check / -C1 / --3way, this session]`

**Scope fence — which hunks are NOT this phase's:**

| Patch hunk | Owner |
|------------|-------|
| `include/firestarter.h` @@206 / @@214 (`protocol` → `uint8_t`, `ctrl_flags` → `uint16_t`) | **Phase 157** (DECODE-04) |
| `include/firestarter.h` @@223 (`progress_data` removal) | **Phase 155** — already landed (`98e70af`) |
| `src/boards/rurp_common.cpp` @@61 (32-bit voltage) | **Phase 155** — already landed (`46dd574`) |
| `src/json_parser.c` (all 6 hunks) | **Phase 157** (DECODE-01…06) |
| `src/proms/memory.cpp` @@386 and @@399 (blank-check static) | **Phase 155** — already landed |
| `test/native/avr/test_eeprom28c_sdp/…` and `test_val_5v_page/…` | **Phase 155** (DEAD-06) — already landed |
| `include/memory_utils.h` @@48, `src/proms/memory.cpp` @@230, and all of `eprom.cpp` / `flash_intel.cpp` / `flash_utils.cpp` / `eeprom_28c.cpp` | **Phase 156** — this phase |

---

## Measured Figures — all three targets, measured this session

**Anchor:** `firestarter` @ `adf1a31`, branch `gsd/v1.33-source-hygiene-firmware-size-reduction`,
tree clean. Measured in `git worktree` `/tmp/fw156`, removed and pruned afterwards; the real tree
was verified clean before and after (`git status --porcelain` empty both times).

Figures are **WARM** (`pio run -e <env>` against a warm `.pio/build/`), matching the Phase 155
convention. LAND-01 / Phase 158 owns the cold re-record.

### The before position (reproduces `155-after-figures.md` §2 exactly)

| Target | Flash | RAM |
|---|---|---|
| `uno` | 24660 | 1567 |
| `uno328pb` | 24708 | 1573 |
| `leonardo` | 26804 | 2008 |

### DEDUP-01 + DEDUP-02 applied

| Target | Flash before | Flash after | Δ flash | RAM before | RAM after | Δ RAM |
|---|---|---|---|---|---|---|
| `uno` | 24660 | **24234** | **−426** | 1567 | **1567** | **0** |
| `uno328pb` | 24708 | **24282** | **−426** | 1573 | **1573** | **0** |
| `leonardo` | 26804 | **26378** | **−426** | 2008 | **2008** | **0** |

**−426 B reproduces exactly from this phase's own starting position.** That was not a given: the
survey measured −426 twice, once in isolation from the pristine baseline and once composed *after*
findings 2, 5 and 1, and Phase 156's actual position is a **third** composition (findings 2 and 8
landed, 5 and 1 not). The survey's own warning — "Composition is NOT additive, and the ordering
matters", with a measured 176 B gap elsewhere — made this worth measuring rather than assuming.
`[VERIFIED: pio run ×3 targets, this session]`

Leonardo Caterina headroom (28672 B cliff): 1868 B → **2294 B**.

### DEDUP-04 (the flip) alone

| Target | Flash | RAM | vs before |
|---|---|---|---|
| `uno` | 24660 | 1567 | **0 / 0** |
| `uno328pb` | 24708 | 1573 | **0 / 0** |
| `leonardo` | 26804 | 2008 | **0 / 0** |

### All three requirements composed

| Target | Flash | RAM | vs DEDUP-01+02 alone |
|---|---|---|---|
| `uno` | 24234 | 1567 | **0 / 0** |
| `uno328pb` | 24282 | 1573 | **0 / 0** |
| `leonardo` | 26378 | 2008 | **0 / 0** |

The flip is size-neutral both in isolation and in composition, on all three targets — one more
target than the survey claimed. `[VERIFIED: pio run ×3 targets ×2 compositions, this session]`

### Per-symbol ledger, `uno`, DEDUP-01 + DEDUP-02

`avr-nm -S` on `firestarter_uno.elf`, before and after:

| Symbol | Before | After | Δ |
|---|---|---|---|
| `eprom_check_vpp` | 524 (`0x20c`) | **280** (`0x118`) | −244 |
| `flash_intel_write_init` | 562 (`0x232`) | **348** (`0x15c`) | −214 |
| `mem_util_report_voltage` | — | **190** (`0xbe`) | +190 |
| `flash_util_check_chip_id_execute` | 192 (`0xc0`) | **118** (`0x76`) | −74 |
| `flash_intel_check_chip_id` | 220 (`0xdc`) | **146** (`0x92`) | −74 |
| `eeprom28c_write_init` | 430 (`0x1ae`) | **374** (`0x176`) | −56 |
| `eprom_internal_check_chip_id` | 260 (`0x104`) | **absent** (inlined away) | −260 |
| `eprom_check_chip_id_execute` | 6 | **24** (`0x18`) | +18 |
| `mem_util_report_chip_id` | — | **90** (`0x5a`) | +90 |

`eprom_check_vpp` 524→280, `flash_intel_write_init` 562→348 and the 190 B helper reproduce the
survey's figures **to the byte**. The DEDUP-01 arithmetic closes exactly: `−244 −214 +190 = −268`.

⚠ **The full ledger does NOT close, and that is expected.** These symbols sum to −624 against an
image delta of −426; the 198 B difference is LTO redistribution — `eprom_internal_check_chip_id`
(260 B) stopped existing as a symbol and was inlined into its two callers, one of which is inside
`main` (5–6 KB, having swallowed `loop()` and the whole dispatch switch). The survey's structural
finding 1 says this outright: "per-object size attribution is impossible … always measure, never
estimate". **Quote −426 as the phase total.** See C-3 for what this means for the −268/−158 split.

### `__udivmodhi4` call sites, `uno`

`avr-objdump -d | grep -cE '(r?call|jmp).*__udivmodhi4'`:

| | Sites |
|---|---|
| Before (at `adf1a31`) | **31** |
| After DEDUP-01 + DEDUP-02 | **13** |

Net −18; the four blocks held 24 and the helper adds 6, so `24 − 6 = 18` ✓. The **"24 of them"
claim in criterion 1 survives intact**; only the total moves. See C-2.

---

## Corrections to ROADMAP / REQUIREMENTS

Phase 155's research corrected the ROADMAP's own figures where they were wrong; this section does
the same. Each correction is measured, not argued.

### C-1 — `flash_intel.cpp`'s two VPP blocks are NOT in `flash_intel_write_init`

Criterion 1 and DEDUP-01 both say the two `flash_intel.cpp` copies sit "inside
`flash_intel_write_init`". **They sit inside `static void flash_intel_check_vpp(firestarter_handle_t*)`
at `src/proms/flash_intel.cpp:26`**, which `flash_intel_write_init` calls. The attribution to
`flash_intel_write_init` is a *symbol-table* fact, not a lexical one: `flash_intel_check_vpp` is
`static` and gets fully inlined, so its bytes are billed to its caller. Both statements are true of
different things; the requirement's wording conflates them. A plan that greps
`flash_intel_write_init` for the blocks will not find them.
`[VERIFIED: source read + patch hunk header + avr-nm, this session]`

### C-2 — `__udivmodhi4` is **31 → 13** from this phase's position, not 30 → 13

Criterion 1 and DEDUP-01 say 30. Measured at `adf1a31`: **31**. The extra site is almost certainly
Phase 155's own — the 32-bit voltage reformulation (`46dd574`) replaced 64-bit division with 32- and
16-bit arithmetic. So "30" was correct at the survey's baseline and is stale by one at Phase 156's.
The **derived** claim ("those four blocks held 24 of them") is unaffected and confirmed: 31 − 13 = 18
net, +6 in the helper, 24 removed. Restate the total; keep the 24.
`[VERIFIED: avr-objdump count before and after, this session]`

### C-3 — the `−268 / −158` split is UNVERIFIED at this position

`−426` is measured here. The `−268` (DEDUP-01) / `−158` (DEDUP-02) split is not: this session
measured the two together, and the per-symbol ledger does not decompose (see above). This is the
same posture Phase 155 landed on for its own `−650 / −714` split, which REQUIREMENTS explicitly
labels UNVERIFIED. Two options: **(a)** land DEDUP-01 and DEDUP-02 in **two commits** and measure
each — recommended, since they are separate requirements and the milestone's own rationale for
sequencing 155 before 156 is "keep each phase's measured delta attributable"; or **(b)** quote only
−426 and label the split UNVERIFIED. Do not quote −268 and −158 as if measured here.

### C-4 — DEDUP-04 is size-neutral but the image is **NOT** byte-identical

The survey says "**Byte-for-byte identical on both targets**", and criterion 4 / DEDUP-04 inherit
that phrasing. What the survey actually compared was the *figures* (`flash=28170 ram=2016`). Measured
this session, on a build proven reproducible (same source rebuilt cold twice → identical `.hex`
SHA):

| Target | flash / RAM | `.hex` SHA-256 (first 16) baseline → flipped |
|---|---|---|
| `uno` | identical | `ab8374136111605f` → `378ff4b0776bbe1e` |
| `uno328pb` | identical | `0d84cff391eed626` → `be6fbc8505bacf56` |
| `leonardo` | identical | `b73dafc71056bf99` → `b342bcabfc1fd3ba` |

`avr-objdump -d` differs on **5450 lines** — mostly a uniform +2 B relocation of everything above a
point (`__vector_16` 0x47b8 → 0x47ba, `main` 0x48fc → 0x48fe), plus the expected branch-polarity
swaps (`brne .+2` → `breq .+2` inside `op_execute_stateful_operation.constprop.42`). Some function
grew 2 B and another shrank 2 B, netting zero.

**Consequence for the plan: DEDUP-04's oracle must be `flash_used` and `ram_used` identity on all
three targets. An oracle asserting `.hex` or ELF byte-identity WILL go RED.** That is the single
most likely way this measurement "comes out non-zero this time" — not because the flip costs
bytes, but because someone chose the wrong identity predicate. `[VERIFIED: sha256sum + avr-objdump
diff + reproducibility control, this session]`

### C-5 — the clone suffix is `.constprop.42`, not `.constprop.44`

DEDUP-04 and survey finding 7 name `op_execute_stateful_operation.constprop.44`. Live at
`adf1a31` it is **`op_execute_stateful_operation.constprop.42`**, 216 B (`0xd8`), and there is
exactly one such clone. Clone renumbering across unrelated changes is documented in this project
(the survey's own finding 6 records `.constprop.76` → `.61`). **Never pin a clone suffix in a
gate.** `[VERIFIED: avr-nm, this session]`

### C-6 — the "ten-line comment at `eprom_operations.cpp:57-63`" is mostly NOT about the `!`

Criterion 4 and OD-2 describe an eleven-line block at `:57-67` as the comment that exists "to
explain why a `!` is load-bearing". Read live, `:57-67` is the **LOCK-01/LOCK-02** block, and only
its final two-and-a-bit lines are the `!` defence:

```
57  // LOCK-01/LOCK-02: standalone entry points for CMD_SDP_UNLOCK / CMD_SDP_LOCK
…   (why no LOG_DEBUG_ID_SUB line; why no precondition check; D-06's NULL-main guard)
65  // is exactly op_execute_simple_operation's single-step shape; op_execute_
66  // simple_operation returns true when FINISHED, so the `!` inversion here is
67  // load-bearing (mirrors eprom_erase/eprom_blank_check above).
```

Deleting `:57-67` wholesale would destroy LOCK-01/LOCK-02 rationale that has nothing to do with the
boolean convention. **Only the `:65-67` clause is dead after the flip.** `[VERIFIED: source read
with line numbers, this session]`

### C-7 — DEAD-06's "only requirement in Phases 155–158 that touches a test file" is FALSE

DEAD-06 states: "This is the only requirement in Phases 155–158 that touches a test file." Measured:
the DEDUP-04 flip turns `test_eeprom28c_sdp.cpp:1487` **RED** and turns
`test_eeprom28c_sdp.cpp:1582-1590` into a **vacuous pass**. Both must be edited. The claim was
written when DEDUP-04 was still an open question ("removed, or declined"); OD-2 resolves it toward
removal and thereby falsifies the claim. Record it; do not quietly touch the test files and leave
the sentence standing. `[VERIFIED: pio test -e native on the flipped tree, this session]`

---

## DEDUP-01 — the VPP report

### The four blocks, located

| # | File | Enclosing function | Arm |
|---|------|--------------------|-----|
| 1 | `src/proms/eprom.cpp:718` | `eprom_check_vpp` | over-voltage, FLAG_FORCE fork |
| 2 | `src/proms/eprom.cpp:720` | `eprom_check_vpp` | under-voltage, WARNING only |
| 3 | `src/proms/flash_intel.cpp:44` | **`flash_intel_check_vpp`** (see C-1) | over-voltage, FLAG_FORCE fork |
| 4 | `src/proms/flash_intel.cpp:46` | **`flash_intel_check_vpp`** (see C-1) | under-voltage, WARNING only |

All four are byte-identical in their packing arithmetic. Blocks 1 and 3 are byte-identical to each
other including their fork; 2 and 4 likewise.

### The `uint16 + 50` promotion — what it actually is

This is the single most likely way DEDUP-01 becomes a behaviour change by accident, so it is
resolved at the C level rather than by inspection.

Both operands are `uint16_t`, confirmed in source:

- `uint16_t vpp_mv = rurp_read_voltage_mv();` — `eprom.cpp:711`, `flash_intel.cpp:36`
- `uint16_t vpp_mv;` — `include/firestarter.h:214`

So `(vpp_mv + 50)` is `uint16_t + int`. Integer promotion promotes `uint16_t` to `int` **only if
`int` can represent every `uint16_t` value**; otherwise to `unsigned int`.

| Target | `sizeof(int)` | `(uint16_t) + 50` is | `/1000` compiles to | Wraps at |
|---|---|---|---|---|
| AVR (`uno`, `uno328pb`, `leonardo`) | **2** | `unsigned int` (16-bit) | `__udivmodhi4` | measured_mv ≥ 65486 |
| native (`x86_64`) | 4 | `int` (32-bit) | native 32-bit divide | never |

The 16-bit result is corroborated mechanically, not just by the language rule: the four blocks held
24 of the image's `__udivmodhi4` sites, and `__udivmodhi4` **is** the 16-bit helper (the 32-bit one
is `__udivmodsi4`). `[VERIFIED: avr-objdump symbol counts + source types, this session]`
`[CITED: ISO C integer promotions]`

**Therefore the helper's parameters must be exactly `uint16_t`:**

```c
void mem_util_report_voltage(firestarter_handle_t* handle, uint16_t measured_mv,
                             uint16_t expected_mv, uint8_t msg_id, uint8_t response_code);
```

Widening either parameter to `uint32_t` would (a) promote the arithmetic to 32-bit, replacing all
six `__udivmodhi4` calls with `__udivmodsi4` and erasing the size win, and (b) on AVR change the
wrap behaviour above 65485 mV. The reference implementation gets this right. **Any plan that
"improves" the signature must re-measure.** Note also that `(uint32_t)` casts *are* present at the
comparison sites (`vpp_mv > (uint32_t)handle->vpp_mv + 500`) — those are outside the extracted
block and must stay exactly where they are.

⚠ **Coverage ceiling:** the AVR-only 16-bit wrap is unobservable in every native environment,
because native `int` is 32-bit. It is identical before and after, so it is not a regression — but no
native test can attest the AVR arithmetic. State this; do not imply native coverage of it.

### The emitted payload — byte map

8 bytes, four `uint16` big-endian:

| Bytes | Value | Expression |
|---|---|---|
| 0–1 | measured volts (integer part, rounded to nearest 0.1 V then truncated) | `(measured_mv + 50) / 1000` |
| 2–3 | measured tenths digit | `((measured_mv + 50) / 100) % 10` |
| 4–5 | expected volts | `(expected_mv + 50) / 1000` |
| 6–7 | expected tenths digit | `((expected_mv + 50) / 100) % 10` |

The `+ 50` is a round-to-nearest-100-mV bias applied before both divisions. Every intermediate is
`uint16_t`. The reference helper reproduces all eight assignments character for character.

### `LOG_ID_BYTES` with a runtime id — verified safe

`include/logging_id.h:39-40`:

```c
#define LOG_ID_BYTES(id, buf_array, count) \
    rurp_log_id((id), (const uint8_t*)(buf_array), (uint8_t)(count))
```

A plain function call — a runtime `uint8_t msg_id` works. And `include/logging_id.h:105` /
`:119` confirm the severity aliasing:

```c
#define LOG_ERROR_ID_BYTES(id, b, n)   LOG_ID_BYTES((id), (b), (n))
#define LOG_WARN_ID_BYTES(id, b, n)    LOG_ID_BYTES((id), (b), (n))
```

Identical expansions. Severity is **entirely** in the id. `[VERIFIED: source read, this session]`

### No new message id is needed

All five ids the two helpers use already exist in the codegen'd catalog:
`MSG_WARN_VPP_LOW 0x81`, `MSG_WARN_VPP_HIGH 0x82`, `MSG_WARN_CHIP_ID_MISMATCH 0x83`,
`MSG_ERR_VPP_HIGH 0xB8`, `MSG_ERR_CHIP_ID_MISMATCH 0xB9`. **`include/messages.h` must not be
touched** — it is generated from meta's `tools/catalog/messages.toml`. This phase needs zero
catalog edits and zero `codegen.py` runs. `[VERIFIED: grep include/messages.h, this session]`

---

## DEDUP-02 — the chip-ID report, and the drift

Criterion 2 requires the resolved single semantic be **stated, not silently chosen**. Here are the
four sites verbatim, every divergence between them, and one semantic with per-divergence reasoning.

### The four sites

**Site A — `src/proms/flash_utils.cpp:104` `flash_util_check_chip_id_execute`**
(callers: `flash_5v_page.cpp:159`, `flash_nor_unlock.cpp:145`)

```c
uint16_t chip_id = flash_util_get_chip_id(handle);
if (chip_id != handle->chip_id) {
    uint8_t _b[4];
    _b[0] = (uint8_t)((chip_id >> 8) & 0xFF);       /* … */
    if (is_flag_set(FLAG_FORCE)) { LOG_WARN_ID_BYTES(MSG_WARN_CHIP_ID_MISMATCH, _b, 4);
                                   handle->response_code = RESPONSE_CODE_WARNING; }
    else                         { LOG_ERROR_ID_BYTES(MSG_ERR_CHIP_ID_MISMATCH, _b, 4);
                                   handle->response_code = RESPONSE_CODE_ERROR; }
}
```

**Site B — `src/proms/flash_intel.cpp:153` `flash_intel_check_chip_id`** — identical to A.
Additionally this file **has no `#include "memory_utils.h"` problem** (it already includes it at
`:14`).

**Site C — `src/proms/eeprom_28c.cpp:292` (inside `static eeprom28c_check_chip_id`, defined at `:268`)**
— identical to A **except** it carries redundant `(uint16_t)` casts on all four bytes and wraps the
body in a superfluous extra `{ … }` brace level:

```c
_b[0] = (uint8_t)(((uint16_t)chip_id >> 8) & 0xFF);
_b[2] = (uint8_t)(((uint16_t)handle->chip_id >> 8) & 0xFF);
```

`chip_id` is already `uint16_t` (`:288`) and `handle->chip_id` is `uint16_t`
(`firestarter.h:223`), so the casts are no-ops.

**Site D — `src/proms/eprom.cpp:768` `eprom_internal_check_chip_id(handle, uint8_t error_code)`**
— identical payload, but the fork is keyed on the **parameter**, not the flag:

```c
if (error_code == RESPONSE_CODE_WARNING) { LOG_WARN_ID_BYTES(…); response_code = WARNING; }
else                                     { LOG_ERROR_ID_BYTES(…); response_code = ERROR; }
```

### Every divergence, and how it resolves

| # | Divergence | Sites | Resolution | Reasoning |
|---|---|---|---|---|
| 1 | Severity keyed on `is_flag_set(FLAG_FORCE)` **inline** vs on an `error_code` **parameter** | A, B, C vs D | Helper takes **`bool warn_only`**. Callers A/B/C pass `is_flag_set(FLAG_FORCE)`; caller D passes `error_code == RESPONSE_CODE_WARNING` | **This divergence must NOT be collapsed.** `eprom.cpp` has *two* callers of D with *different* policies: `eprom_check_chip_id_execute` (`:119`) passes `RESPONSE_CODE_ERROR` **unconditionally**, while `eprom_generic_init` (`:791`) passes the FLAG_FORCE-derived value. Folding `is_flag_set(FLAG_FORCE)` into the helper would silently make the standalone `CMD_CHECK_CHIP_ID` command honour `--force`, which today it does not. That is a behaviour change, and criterion 2 forbids one |
| 2 | Redundant `(uint16_t)` casts | C only | **Dropped** | Provably no-ops: both operands are already `uint16_t`. Zero behaviour delta, zero size delta |
| 3 | Superfluous extra brace level | C only | **Dropped** | Lexical only |
| 4 | The `if (chip_id != handle->chip_id)` guard lives at the call site | all four | **Moved into the helper as an early `return`** | Byte-identical at all four sites; hoisting it collapses each call site to one line and is what buys most of the −158 B. Consequence tracked in §Gate blast radius: it removes one predicate from `eprom.cpp`'s pinned branch inventory |
| 5 | Which function is `static` / which has a header declaration | C is `static`, A/B/D are external | **Unchanged** | Out of scope; the helper is called from inside each, whatever its linkage |
| 6 | `#include "memory_utils.h"` present? | A **absent**, B/C/D present | **One `#include` added to `flash_utils.cpp`** | Required for the declaration. ⚠ This single line is one of the four includes ROADMAP D-01 measures as causing 41 % of the milestone's citation rework — it shifts **all 97** of `flash_utils.cpp`'s `.planning/` citations. Expected, close-blocked by REMAP-04; do not remap here |

### The resolved single semantic — stated

```c
/* Reports a chip-ID mismatch, or returns without emitting anything if the ids match.
 * Severity is the CALLER's decision, passed as warn_only, because the four former
 * copies did not agree on how to derive it and one of them must not: eprom.cpp's
 * standalone CMD_CHECK_CHIP_ID path refuses unconditionally, independent of
 * FLAG_FORCE. The helper unifies the COMPARISON and the PAYLOAD; it deliberately
 * does not unify the POLICY. */
void mem_util_report_chip_id(firestarter_handle_t* handle, uint16_t actual, bool warn_only);
```

**No divergence requires a behaviour change to resolve.** Divergence 1 is preserved by
parameterisation; 2 and 3 are provable no-ops; 4 is a pure relocation; 5 is untouched; 6 is
additive.

⚠ **One structural asymmetry worth recording**, because it bears directly on DEDUP-03:
`mem_util_report_chip_id` derives **both** the id and the `response_code` from the single
`warn_only` boolean, so a transposition is impossible by construction on one side and needs a
matched pair of edits on the other. `mem_util_report_voltage` takes `msg_id` and `response_code` as
**two independent parameters**, so a caller can pair them wrongly and nothing in the signature
objects. That is exactly the defect class DEDUP-03 exists for.

---

## DEDUP-03 — the mismatch test, and the coverage ceiling that makes it necessary

DEDUP-03 asserts a golden trace cannot see a swapped `response_code`. That is correct and now
demonstrated. But the more useful result is *which* forks are covered today and which are not — so
this session planted four transpositions on the DEDUP-applied tree and ran both CI native
environments plus the non-CI `native_loop_v131`.

### The four probes — measured

| Probe | Planted mutation | `pio test -e native` (**in CI**) | `pio test -e native_loop_v131` (**NOT in CI**) |
|---|---|---|---|
| **A** | `eprom.cpp` over-voltage arm: `force ? WARNING : ERROR` → `force ? ERROR : WARNING` | **172/172 GREEN — BLIND** | **RED, 3 cases** |
| **B** | Under-voltage arm: `MSG_WARN_VPP_LOW, RESPONSE_CODE_WARNING` → `…, RESPONSE_CODE_ERROR` (both files) | **172/172 GREEN — BLIND** | **80/80 GREEN — BLIND** |
| **C** | `mem_util_report_chip_id`: `warn_only ? WARNING : ERROR` → `warn_only ? ERROR : WARNING` | **RED, 2 cases** | 80/80 green |
| **D** | `mem_util_report_chip_id`: `warn_only ? MSG_WARN_… : MSG_ERR_…` → transposed (`response_code` left correct) | **172/172 GREEN — BLIND** | **80/80 GREEN — BLIND** |

Probe A's three RED cases (`test/native/avr/test_vpp_eprom_v131/test_vpp_eprom_v131.cpp`):
`:639 test_vpp04_a_overvoltage_refusal_fires_by_id_with_payload_shape`,
`:706 test_vpp04_c_flag_force_downgrades_to_warning_and_still_clears_the_route`,
`:1358 test_vpp02_e1_write_init_error_exit_leaves_no_route_asserted`.

Probe C's two RED cases: `test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp:814
test_case7_mismatching_chip_id_with_force_warns` and
`test/native/avr/test_sdp_harness/test_sdp_harness.cpp:619
test_migrated_mismatching_chip_id_errors`.

`[VERIFIED: four planted mutations, each built and run against two/three envs, this session]`

### What this means

1. **The VPP over-voltage fork already has a real mismatch test** — `test_vpp04_a` and
   `test_vpp04_c` assert the `response_code` **and** both message ids in both directions
   (`count_logged_id(MSG_ERR_VPP_HIGH) == 1` **and** `count_logged_id(MSG_WARN_VPP_HIGH) == 0`, then
   the mirror image under FLAG_FORCE). `test_vpp04_a` additionally asserts
   `logged_id_param_count(idx) == 8` — the payload **length**, not its bytes. That suite was
   authored in Phase 142 precisely because "MSG_ERR_VPP_HIGH and MSG_WARN_VPP_HIGH appear in NO
   test anywhere" (its own comment at `:602`). **DEDUP-03 is already half-satisfied by existing
   coverage — but that coverage lives in `native_loop_v131`, which no CI workflow runs.**
2. **Blind spot 1 — the under-voltage severity pairing (probe B).** Nothing anywhere asserts
   `MSG_WARN_VPP_LOW` is emitted or that it carries `RESPONSE_CODE_WARNING`. The only reference is a
   negative (`count_logged_id(MSG_WARN_VPP_LOW) == 0` on an in-range reading, `test_vpp04_d:748`).
   This is precisely the two-independent-parameters hazard: the caller passes
   `(MSG_WARN_VPP_LOW, RESPONSE_CODE_WARNING)` and no oracle checks the pair.
3. **Blind spot 2 — the chip-ID message id (probe D).** `grep -rn 'MSG_WARN_CHIP_ID_MISMATCH\|
   MSG_ERR_CHIP_ID_MISMATCH' test tests scripts` returns **zero hits**. The chip-ID `response_code`
   *is* covered, in CI; the **id** is not covered anywhere. Since severity rides entirely in the id,
   a transposed id ships an ERROR-severity frame to the host on a `--force` run and the WARNING
   frame on a refusal — invisible to the whole suite.
4. **A green golden trace really is insufficient**, exactly as DEDUP-03 says. The trace goldens in
   scope (`tests/golden/eprom_v131_trace_inventory.json`,
   `test/native/avr/_shared/sdp_expected.h`) match on ids and blob SHAs, and probes B and D show ids
   alone leaving both blind spots open. This corroborates the project's own memory note
   `reference_golden_trace_misses_severity_fork.md`, which `test_eeprom28c_sdp.cpp:788` cites by name.

### Options for the required mismatch test

| Option | Where | CI-visible? | Cost / consequence |
|---|---|---|---|
| **1 — extend `test_vpp_eprom_v131`** (recommended for the VPP half) | `test/native/avr/test_vpp_eprom_v131/test_vpp_eprom_v131.cpp`, env `native_loop_v131` | **No** | **Zero gate friction.** `check_size_baseline.py`'s `compare_native` only reads `native` / `native_nodevtools`, and `tests/test_requirement_case_mapping_v131.py`'s per-suite check is a **floor** (`>= 32`; live is 33), not an equality — verified. The harness already exists (`set_mock_vpp_mv`, `count_logged_id`, `find_logged_id`, `logged_id_param_count`, `drive_vpp_init`). Must be labelled NO CI COVERAGE, per that env's own comment block and the DEAD-05 precedent |
| **2 — extend a CI-visible suite** (recommended for the chip-ID half) | `test_eeprom28c_sdp` or `test_sdp_harness`, env `native` | **Yes** | ⚠ **`check_size_baseline.py::compare_native` asserts `cases == 172` by EXACT equality** (`scripts/check_size_baseline.py:745`, `scripts/baseline/size_baseline.json` `native_envs.native.cases = 172`). Adding one case turns the default-baseline gate RED until Phase 158 / LAND-01 re-records. Verified. That is a *decision*, not an accident — record it and its Phase-158 hand-off, or restructure an existing case instead of adding one |
| **3 — make `mem_util_report_voltage` transposition-proof by construction** | `src/proms/memory.cpp` | n/a | Derive `response_code` from `msg_id` (the catalog splits cleanly: WARN `0x80-0x87`, ERR `0xA0-0xBE` — verified). Removes the two-independent-parameters hazard entirely. **But** it embeds a catalog-range assumption in the memory layer, it does not fit the under-voltage path any better than the 5-parameter form, and — decisively — **the −426 B was measured against the reference signature.** Any deviation requires a full re-measurement. Recorded as considered; not recommended |

**Recommended combination:** Option 1 for both VPP blind spots (over-voltage regression legs already
exist; add the under-voltage `(MSG_WARN_VPP_LOW, RESPONSE_CODE_WARNING)` pairing for both
`eprom.cpp` and `flash_intel.cpp`), plus Option 2 restructured to add the missing chip-ID **id**
assertions to the two cases probe C already reddens (`test_case7_mismatching_chip_id_with_force_warns`
and `test_migrated_mismatching_chip_id_errors`) — **strengthening existing cases rather than adding
new ones keeps `cases` at 172 and the size gate green.** That is the cheapest path to a CI-visible
mismatch test.

Whichever is chosen, the evidence DEDUP-03 demands is a **planted-transposition run**: each new
assertion must be seen RED against a deliberately transposed tree and GREEN against the real one,
in the plan's own SUMMARY. Probes A–D above are the template and the four mutations are recorded
verbatim so a plan can re-run them.

---

## DEDUP-04 — the convention flip

### The 6 return sites inside `op_execute_stateful_operation` (`src/operation_utils.cpp:63`)

| # | Line region | Today | After the flip | Trap? |
|---|---|---|---|---|
| 1 | `:70` | `return true;   // Not finished yet, waiting for final ACK` | `return false;` | literal |
| 2 | `:72` | `return false;  // Received final ACK (or junk), command is finished.` | `return true;` | literal |
| 3 | `:77` | `return res == RETURN;` | `return res != RETURN;` | ⚠ **not a literal** — an expression |
| 4 | `:80` | `return callback(handle);` | `return !callback(handle);` | ⚠⚠ **not a literal, and it does not remove the `!`** |
| 5 | `:82` | `return true;` (MAIN phase not yet started) | `return false;` | literal |
| 6 | `:164` | `return false;` (the D-06 NULL-main refusal) | `return true;` | literal |

**Site 4 is the honest cost of DEDUP-04.** `op_execute_stateful_operation` delegates to a callback
whose own convention is documented as "true on success/continue, false on error"
(`eprom_operations.cpp:84`, and `_single_step_operation_callback` likewise). Flipping the engine
without flipping all three callbacks means site 4 becomes `return !callback(handle);`. **The `!` is
not eliminated — it moves from 9 call sites to 1**, and the engine ends up with a convention
opposite to its own callback's. Flipping the callbacks too would cascade into their multiple return
sites and into `set_operation_to_done`, which is a materially larger change than criterion 4
describes and was never measured.

That 9 → 1 reduction is still the readability win OD-2 asked for, and it is honest to state it that
way rather than as "the inversion is gone". The plan should say which it is.

`op_execute_simple_operation` (`:59-61`) is a bare forward and needs **no** change.

### The 9 wrapper call sites (`src/eprom_operations.cpp`)

`eprom_read` `:20`, `eprom_write` `:25`, `eprom_verify` `:31`, `eprom_erase` `:40`,
`eprom_check_chip_id` `:49`, `eprom_blank_check` `:54`, `eprom_sdp_unlock` `:69`,
`eprom_sdp_lock` `:73`, `eprom_lock_status` `:86`. Drop the `!` from each.

⚠ **The early-return literals inside those wrappers must NOT change.** `eprom_erase:37`
(`FLAG_CAN_ERASE` refusal) and `eprom_check_chip_id:46` (`chip_id == 0` refusal) both
`return true;` today, meaning "done, refuse and finish". Under both conventions the wrapper's
`true` means finished, so those two literals are already correct and flipping them would break the
refusals. Verified against `src/firestarter.cpp:309-354`, where every arm assigns to a local named
`finished`.

### The comment blast radius — 6 places, all measured

| Location | What it says today | Action |
|---|---|---|
| `src/eprom_operations.cpp:65-63` | "`op_execute_simple_operation` returns true when FINISHED, so the `!` inversion here is load-bearing" | **Delete these 3 lines only** — not the whole `:57-67` block (C-6) |
| `src/operation_utils.cpp:98-100` | "Every `eprom_*` caller inverts that return (`return !op_execute_stateful_operation(...)`), so the command reported 'finished'" | Rewrite — this is the D-06 mega-comment's mechanism narrative |
| `src/operation_utils.cpp:~171` | "The `return false` semantics are UNCHANGED — every `eprom_*` caller still inverts it" | Rewrite; this sentence becomes false |
| `include/operation_utils.h:71` | `@return true if the operation is still ongoing …, false when fully completed` (`op_execute_simple_operation`) | Invert |
| `include/operation_utils.h:85` | `@return true if the operation is still ongoing, false when fully completed` (`op_execute_stateful_operation`) | Invert |
| `test_eeprom28c_sdp.cpp:1469`, `:1492` | quote the `return !op_execute_…` form as the contract under test | Update both quotes |

### The test blast radius — MEASURED, and one half is a silent false green

Running `pio test -e native` on the flipped tree:

```
173 test cases: 1 failed, 171 succeeded
198:test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp:1487:
    test_case24_null_main_refusal_emits_not_supported_and_error_response … [FAILED]
```

**(1) Case 24 goes RED** — `TEST_ASSERT_FALSE_MESSAGE(still_in_progress, "…must return false on a
NULL main…")` at `:1426`. Must become `TEST_ASSERT_TRUE_MESSAGE`, with the message rewritten (it
currently says "every `eprom_*` caller inverts this return", which stops being true).

**(2) Case 25 stays GREEN and becomes VACUOUS.** `test_case25_cmd_erase_on_0x0d_dispatches_and_succeeds_erase03`
(`:1524-1534`) drives `while (still_in_progress && calls < MAX_CALLS) { still_in_progress =
op_execute_simple_operation(&h); calls++; }` then asserts `TEST_ASSERT_FALSE(still_in_progress)`.
Under the flipped convention the first call returns `false`, the loop exits immediately, and the
assertion passes — for the wrong reason. Proven by inserting a probe:

```
test_eeprom28c_sdp.cpp:1590: test_case25_… : Expected 4 Was 1.
    RESEARCH PROBE: Case 25 must take exactly 4 op_execute_simple_operation calls
```

The case's own comment documents that reaching completion "needs FOUR calls". After the flip it
takes one and still reports PASSED. **The plan must flip the loop condition to
`while (!finished && …)` AND add a `calls == 4` assertion**, so the vacuity can never recur
silently. `[VERIFIED: pio test with and without a planted probe, this session]`

Note: `src/eprom_operations.cpp` compiles in **no** native environment (`[env:native]`'s
`build_src_filter = +<proms/> +<boards/rurp_serial_utils.cpp> +<json_parser.c>
+<operation_utils.cpp>`), so the 9 dropped `!` have no behavioural oracle at all — only the
size-identity build and source inspection. `src/operation_utils.cpp` **is** in the filter, so the 6
flipped returns do have native coverage, and Cases 24/25 are it.

### Also observed: a failing case inflates the reported count

The flipped run reported "**173** test cases: 1 failed, 171 succeeded" against a 172-case baseline,
and the failure line appears twice in the log. PlatformIO appears to double-count a failing case in
its summary. Consequence: a genuine assertion failure will *also* surface as a
`compare_native: cases baseline=172 observed=173` mismatch. Read the failure, not the count.

---

## Gate blast radius — what goes RED, measured on a committed tree

`pytest tests/` (the third CI leg) was run against the DEDUP-01/02 change both **uncommitted** and
**committed**, because several modules read `git rev-parse HEAD:<path>` rather than the working
tree.

### Committed DEDUP-01/02 tree: exactly 2 real failures

```
FAILED tests/test_protocol_branch_inventory.py::test_blob_shas_match_the_recorded_inventory
FAILED tests/test_protocol_branch_inventory.py::test_branch_sites_match_the_recorded_inventory
3 failed, 313 passed, 32 skipped
```

The third, `tests/test_checker_convention.py::test_scope_is_firmware_only`, is a **worktree
artifact, not a real red** — see the trap below.

`tests/golden/protocol_branch_inventory.json` pins `src/proms/eprom.cpp` two ways: whole-file blob
SHA, and a positional `(line, predicate, keyed_on, tier)` inventory. Live blob SHA today is
`838aca47986103969be4caca3cef71a033bac069`, matching the record exactly — so the gate is **GREEN
on arrival** and this phase's edit is what breaks it. (Phase 154's sweep left `eprom.cpp` and
`flash_intel.cpp` byte-unchanged; verified against `2ad5b32`'s file list.)

### The new inventory, derived with the gate's own extractor

```
total_sites            23 → 21
protocol_keyed_sites    1 →  1   (unchanged: `switch (handle->protocol)` at :70 — TABLE-05 intact)
other_sites            22 → 20
```

Two sites removed, **none added**, no predicate re-keyed or re-tiered:

| Removed | Was at | Cause |
|---|---|---|
| `if (is_flag_set(FLAG_FORCE))`, `keyed_on: [ctrl_flags]`, tier `other` | `:728`, inside `eprom_check_vpp`'s over-voltage arm | Becomes `bool force = is_flag_set(FLAG_FORCE);` plus two ternaries; the extractor's `_is_relevant` does not count the assignment as a branch predicate |
| `if (chip_id != handle->chip_id)`, `keyed_on: [chip_id]`, tier `other` | `:798`, inside `eprom_internal_check_chip_id` | **Relocated into `mem_util_report_chip_id`'s early return in `src/proms/memory.cpp`, a file this gate does not scan** |

Line shifts of surviving sites: `:713` unchanged · `:736 → :720` (−16) · `:787 → :758`,
`:790 → :761`, `:791 → :762`, `:815 → :773` (−29). `[VERIFIED: the module's own
`_extract_predicates()` run against the patched file, this session]`

⚠ **The re-record note must say the second predicate MOVED, not vanished.** A record reading
"a `chip_id != handle->chip_id` safety branch was deleted from `eprom.cpp`" would be materially
misleading, and "duplication merely relocated somewhere else" is the exact concern the sibling gate
`tests/test_hv_routing_source_contract_v142.py` was built to catch. The golden's own
`how_to_update` demands the extractor be re-run (never a hand-edited line number) and the commit
message name which site changed and why.

⚠ **The one-commit property.** This golden's `meta.recorded_by` field documents four prior
re-derivations and the convention that the source change and the golden land in the **same commit**,
so the gate goes RED once, for one reason. It also documents the one time that could not be honoured
and says so plainly. Follow the convention.

### Gates confirmed GREEN on the DEDUP tree

`tests/test_hv_routing_source_contract_v142.py` (scans `eprom.cpp` structurally) ·
`tests/test_write_path_source_contract_v131.py` (scans `eprom.cpp` + `memory.cpp`) ·
`tests/test_progress_emission_is_leonardo_only.py` (scans `eprom.cpp`) ·
`tests/test_check_erase_no_vpp.py` + `scripts/check_erase_no_vpp.py` (scan `eeprom_28c.cpp`) ·
`tests/test_golden_trace_identity*.py` · `tests/test_eprom_params_citations.py` ·
`tests/test_requirement_case_mapping_v131.py` (per-suite **floor** ≥ 32/47/9; live 33/47/9) ·
`tests/test_trace_segment_exhaustiveness_v131.py`.

### ⚠ The throwaway-worktree trap

`tests/test_checker_convention.py::test_scope_is_firmware_only` asserts
`Path(scripts_dir).resolve().parts[-2:] == ("firestarter", "scripts")` — it hard-codes the
**directory name**. In a worktree at `/tmp/fw156` it fails with
`got ('fw156', 'scripts')`. **Any throwaway worktree this phase creates for a planted-negative
proof must be named `firestarter`** (e.g. `/tmp/probe/firestarter`), or this leg fails spuriously
and looks like a real red. `[VERIFIED: pytest run in a worktree named `fw156`, this session]`

### Gates that must be run but are NOT in CI

- **`scripts/check_size_baseline.py` runs in NO CI workflow at all.** `grep -rn` over
  `.github/workflows/` returns nothing. Every size gate this phase leans on is a **local-run
  obligation** (LAND-04). Verified.
- **`pio test -e native_loop_v131` is not in CI** either. `.github/workflows/build.yml:142,155,161`
  and `beta-build.yml:122,128,134` run exactly `pio test -e native`, `pio test -e native_nodevtools`,
  `pytest tests/ -v`, then `pio run`. The v131 envs are local-only by design and say so in their own
  comment blocks.
- The canonical `--policy merge05 --baseline scripts/baseline/size_baseline_base01.json` invocation
  is **already RED on `beta`** for a pre-existing unrelated reason (`native: cases baseline=141
  observed=172`, BASE-01 frozen at Phase 124). That is Phase 158 / LAND-03's problem, not this
  phase's — but it will bite anyone who runs the canonical invocation here.

### The default (non-merge05) baseline mode will go RED — expected

`compare_avr` in default mode requires exact equality of `flash_used`, and this phase reduces it by
426 B. That is LAND-01's re-record, not a defect. Under `--policy merge05` the flash and RAM legs
are one-sided (`:697` `if flash_delta > allowance`, `:709` `if ram_delta > ram_tolerance`), so a
**reduction passes with no named exemption** — D-03, verified in source. Record the green run *as*
one-sided, so nobody reads it as "nothing moved".

---

## Project Constraints (from CLAUDE.md)

From `/workspaces/CLAUDE.md` and `/workspaces/firestarter/CLAUDE.md`:

| Directive | Bearing on this phase |
|---|---|
| Meta repo tracks only `.planning/` and `.claude/`; sub-repos are not committed here | All source edits are committed **inside** `firestarter/`, on `gsd/v1.33-source-hygiene-firmware-size-reduction` |
| "Serial protocol changes must be kept in sync between `serial_comm.py` and `firestarter.cpp`" | **No wire change.** The 8-byte and 4-byte payloads and all five message ids are unchanged, so `firestarter_app` is untouched. This is a firmware-only phase |
| "Constants/flag bits are duplicated between `constants.py` and `firestarter.h`. Change both together" | **Not triggered.** No constant, flag bit or message id is added, removed or renumbered |
| Build commands: `pio run -e {uno,uno328pb,leonardo}`, `pio test -e native` | Used as-is; all three AVR targets must be measured, not just two |
| Dispatch reads named `PROTO_*` constants; `protocol` is the sole algorithm axis (GATE-01, TABLE-05) | Untouched. `protocol_keyed_sites` stays at exactly 1 (line 70) — verified |
| `firestarter/CLAUDE.md` documents `eprom_check_vpp()` and the write path sharing `eprom_hv_route_mask()` as a **source contract** | The VPP extraction must not disturb `eprom_hv_route_mask` or the `EPROM_HV_ALL_OFF_MASK` clear. Verified: `tests/test_hv_routing_source_contract_v142.py` stays green |
| `include/messages.h` is **codegen-generated — DO NOT EDIT** | Not touched. Zero new ids needed |
| Never work on `beta`/`main`; nothing is pushed by an executor | Milestone branch only; pushing is the operator's call |

### Project skills

`/workspaces/.claude/skills/` contains `devtest-rootcause`, `devtest-triage`, `find-skills`,
`skill-creator`. None applies: this phase is a pure firmware refactor with no chip-validation,
database or issue-triage surface. There are no `rules/*.md` files. No skill pattern constrains it.

---

## Standard Stack

No new dependency is introduced. This phase edits existing firmware C/C++ and existing test
infrastructure.

### Core

| Component | Version | Purpose | Why standard |
|---|---|---|---|
| PlatformIO Core | **6.1.19** (verified installed) | Build and test driver | Pinned in `size_baseline.json` `meta.platformio_core`; the project's only build entry point |
| `toolchain-atmelavr` / `avr-gcc` | **7.3.0** (`1.70300.191015`) | AVR compiler; `-flto` on | Pinned in `size_baseline.json` |
| `framework-arduino-avr` | 5.3.0 | Arduino core | Pinned |
| Unity (via PlatformIO `test_framework`) | bundled | Native test framework | Every one of the 24 suites under `test/native/avr/` uses it |
| ArduinoFake | `^0.4.0` | Arduino API mocks for the native envs | `lib_deps` in `[env:native]`, `[env:native_nodevtools]` and all four v131 envs |
| pytest | 9.1.1 (verified) | The source-contract / golden gate layer | 38 modules under `tests/`; the third CI leg |

### Supporting

| Component | Purpose | When |
|---|---|---|
| `avr-nm -S` | Per-symbol size attribution | Building the flash ledger; note the LTO caveat |
| `avr-objdump -d` | `__udivmodhi4` call-site counting; instruction-level diffing | DEDUP-01's criterion; DEDUP-04's C-4 nuance |
| `sha256sum` on `firestarter_<env>.hex` | Image identity | Only as a **negative** control for DEDUP-04 (C-4) |
| `scripts/check_size_baseline.py` | MERGE-05 policy and native-count comparison | Local-run obligation; not in CI |

Both `avr-nm` and `avr-objdump` live in
`~/.platformio/packages/toolchain-atmelavr/bin/` and are **not on `PATH`** — invoke by full path.

### Alternatives considered

| Instead of | Could use | Tradeoff |
|---|---|---|
| `git apply -C1` of the extracted subset | `git apply --3way` (also verified clean) or hand-transcribing from `wip/v1.33-size-reduction-survey-preserved` | `-C1` is the least-surprise mechanical route and its one context divergence is understood. `--3way` also works. Cherry-picking from the preserved ref does **not** — it forks `8695ee5`, before Phase 154's sweep |
| 5-parameter `mem_util_report_voltage` | Derive `response_code` from `msg_id`'s catalog range | §DEDUP-03 Option 3: structurally safer, but invalidates the −426 B measurement and embeds a catalog assumption in the memory layer |

---

## Package Legitimacy Audit

**Not applicable — this phase installs no external package.** No `npm`, `pip`, `cargo` or
`lib_deps` entry is added, removed or version-bumped; `platformio.ini`'s `lib_deps` is untouched
(`fabiobatsilva/ArduinoFake@^0.4.0` in the native envs, unchanged). The Package Legitimacy Gate was
therefore not run, and no `[SLOP]` / `[SUS]` verdict exists to report.

| Package | Registry | Age | Downloads | Source repo | Verdict | Disposition |
|---|---|---|---|---|---|---|
| *(none — no package is installed by this phase)* | — | — | — | — | — | — |

**Packages removed due to `[SLOP]` verdict:** none.
**Packages flagged as suspicious `[SUS]`:** none.

---

## Architecture Patterns

### System architecture — how a VPP report and a chip-ID report flow

```
                    host command (JSON, 250000 baud)
                              │
                    json_parse / json_parse_config      (src/json_parser.c)
                              │
                    configure_memory  ── protocol ──►  configure_eprom / configure_flash_intel /
                              │                        configure_eeprom28c / configure_flash_5v_page /
                              │                        configure_flash_nor_unlock            (memory.cpp)
                              │   sets firestarter_operation_{init,main,end}
                              ▼
       firestarter.cpp loop() ──► dispatch switch (:309-354) ──► eprom_read / eprom_write / …
                                                                   (src/eprom_operations.cpp)
                                            │  ◄── DEDUP-04 flips the polarity of this edge
                                            ▼
                              op_execute_stateful_operation          (src/operation_utils.cpp)
                                 INIT ──► MAIN ──► END, each gated on op_wait_for_ack
                                            │
                    ┌───────────────────────┴───────────────────────┐
                    ▼                                               ▼
        eprom_check_vpp (eprom.cpp)                    flash_intel_check_vpp (flash_intel.cpp)
        flash_intel_write_init                                      │
                    │                                               │
        rurp_read_voltage_mv() ──► uint16_t vpp_mv                  │
                    │                                               │
        threshold decision:  > expected+500  →  ERROR, or WARNING under FLAG_FORCE
                             < expected*95/100 →  WARNING
                             otherwise         →  nothing
                    │                                               │
                    └──────────────► mem_util_report_voltage ◄──────┘        [DEDUP-01: NEW]
                                     (src/proms/memory.cpp)
                                        packs 4 × uint16 BE
                                        LOG_ID_BYTES(msg_id, _b, 8)
                                        handle->response_code = response_code
                                                    │
        flash_utils.cpp ─┐                          │
        flash_intel.cpp ─┤                          │
        eprom.cpp       ─┼──► mem_util_report_chip_id ──┤                     [DEDUP-02: NEW]
        eeprom_28c.cpp  ─┘   early-return if ids match  │
                             packs 2 × uint16 BE        │
                             id AND severity from warn_only
                                                        ▼
                                          rurp_log_id  (COBS + CRC8 frame)
                                                        ▼
                                          host: serial_comm.py  →  "WARNING:" / "ERROR:" line
```

The severity a user sees is decided **entirely** by which id enters `rurp_log_id`, and
`response_code` independently decides whether the command aborts. Those two must agree. Nothing in
the type system enforces it. That is DEDUP-03's whole subject.

### Pattern 1 — extract the shared *mechanism*, parameterise the divergent *policy*

Both helpers follow it: the payload packing and the emit are shared; the severity decision stays at
the call site (`msg_id` + `response_code`, or `warn_only`). This is what makes the change a
de-duplication rather than a behaviour change, and it is why divergence 1 in §DEDUP-02 must be
preserved rather than collapsed.

```c
// Source: wip/v1.33-size-reduction-survey-preserved:src/proms/memory.cpp (verified this session)
void mem_util_report_chip_id(firestarter_handle_t* handle, uint16_t actual, bool warn_only) {
    if (actual == handle->chip_id) {
        return;                                  // the guard hoisted from 4 call sites
    }
    uint8_t _b[4];
    _b[0] = (uint8_t)((actual >> 8) & 0xFF);
    _b[1] = (uint8_t)(actual & 0xFF);
    _b[2] = (uint8_t)((handle->chip_id >> 8) & 0xFF);
    _b[3] = (uint8_t)(handle->chip_id & 0xFF);
    LOG_ID_BYTES(warn_only ? MSG_WARN_CHIP_ID_MISMATCH : MSG_ERR_CHIP_ID_MISMATCH, _b, 4);
    handle->response_code = warn_only ? RESPONSE_CODE_WARNING : RESPONSE_CODE_ERROR;
}
```

### Pattern 2 — collapse a severity fork into one call with a selected id

The enabler for the whole phase, and the project's own idiom now that severity is proven to ride
entirely in the id:

```c
bool force = is_flag_set(FLAG_FORCE);
mem_util_report_voltage(handle, vpp_mv, handle->vpp_mv,
                        force ? MSG_WARN_VPP_HIGH : MSG_ERR_VPP_HIGH,
                        force ? RESPONSE_CODE_WARNING : RESPONSE_CODE_ERROR);
```

Two parallel ternaries on one boolean. Readable, and — measured — 244 B cheaper than the
`if`/`else` pair it replaces. Its cost is that the pairing is a convention, not a type.

### Pattern 3 — preserve the integer type exactly when hoisting arithmetic into a function

Parameter types are part of the arithmetic. `uint16_t` in, `uint16_t` out; see §DEDUP-01.

### Pattern 4 — the committed source-contract scan

This repo's established way to pin a structural claim CI cannot execute: a pytest module that
comment-strips a source file, re-parses it, and compares against a committed golden re-derived by
the module's own extractor. `test_protocol_branch_inventory.py` is the instance this phase must
update. Its discipline is worth copying, not just satisfying: two independent mechanisms read the
same file and are compared, and the golden records *why* each figure moved.

### Anti-patterns to avoid

- **Asserting `.hex` or ELF byte-identity for DEDUP-04.** Size-identical ≠ byte-identical (C-4).
- **Hand-editing `tests/golden/protocol_branch_inventory.json`.** The golden forbids it in its own
  `how_to_update`; re-derive with the extractor.
- **Pinning a `.constprop.NN` clone suffix** (C-5).
- **Folding `is_flag_set(FLAG_FORCE)` into `mem_util_report_chip_id`.** Silently makes
  `CMD_CHECK_CHIP_ID` honour `--force`. A behaviour change criterion 2 forbids.
- **Widening the voltage helper's parameters to `uint32_t`** — erases the win and changes AVR
  overflow behaviour.
- **Treating a green golden trace as DEDUP-03 evidence.** Probes B and D measured it blind.
- **Deleting `eprom_operations.cpp:57-63` wholesale** (C-6).
- **Blaming a single failing native run on this change** (D-04). Phase 155 ran the suite seven
  times.
- **Re-anchoring `size_baseline.json`** — Phase 158's job.

---

## Don't Hand-Roll

| Problem | Don't build | Use instead | Why |
|---|---|---|---|
| Re-deriving `eprom.cpp`'s branch inventory | A bespoke regex over the file | `tests/test_protocol_branch_inventory.py::_extract_predicates`, imported and run | It is the gate's own parser. Anything else can agree with the file and disagree with the gate |
| Counting `__udivmodhi4` call sites | Reading the source and reasoning | `avr-objdump -d <elf> \| grep -cE '(r?call\|jmp).*__udivmodhi4'` | The count is a codegen fact; the source shows `/` and `%`, not helper calls |
| Per-function size attribution | Estimating from line counts | `avr-nm -S` on the ELF — and expect it not to close under LTO | The survey's structural finding 1: per-object attribution is impossible with `-flto` |
| Asserting an emitted frame's id and payload length in a native test | A new capture harness | `count_logged_id`, `find_logged_id`, `logged_id_param_count` in `test_vpp_eprom_v131/host_stubs.cpp` | Already exist and are the only place in the tree that can assert a frame by id — its own comment (`:268`) says so |
| Proving a new assertion is non-vacuous | Asserting it passes | A **planted transposition**, run and recorded RED, then GREEN on the real tree | The project's established discipline; §DEDUP-03's four probes are the template. And Case 25 is the live proof that a green assertion can be vacuous |
| Reproducible build comparison | Assuming a rebuild is deterministic | Verify it: rebuild the same source cold twice and compare SHAs | Done this session — the build **is** reproducible (`ab8374136111605f` twice), which is what makes C-4's negative result trustworthy |

**Key insight:** every mechanical question this phase raises already has a tool committed in the
repo that answers it. The failure mode is not missing tooling — it is reasoning where a committed
tool would have measured.

---

## Runtime State Inventory

This is a refactor phase, so the inventory is mandatory. Each category is answered explicitly.

| Category | Items found | Action required |
|---|---|---|
| **Stored data** | **None.** No database, EEPROM record, collection name or persisted key encodes any identifier this phase renames or removes. Verified: the removed `blank_check_progress_data_t` was Phase 155's; this phase removes no field of `firestarter_handle_t` and no `rurp_configuration_t` member. Hardware calibration in Arduino EEPROM is untouched | none |
| **Live service config** | **None.** No n8n workflow, dashboard, tag or external service references `mem_util_report_voltage`, `mem_util_report_chip_id`, `op_execute_stateful_operation` or any of the nine `eprom_*` wrappers | none |
| **OS-registered state** | **None.** No task-scheduler entry, pm2 process name or systemd unit references any symbol this phase touches | none |
| **Secrets / env vars** | **None.** No SOPS key, `.env` value or CI variable names a firmware symbol. `platformio.ini` build flags are untouched | none |
| **Build artifacts / installed packages** | **`.pio/build/{uno,uno328pb,leonardo,native,native_nodevtools,native_loop_v131}` hold stale objects.** PlatformIO recompiles changed TUs correctly (verified across ~10 rebuilds this session, all figures consistent), so no manual clean is required for correctness. `rm -rf .pio/build/<env>` **is** required for the *cold* convention — but that is LAND-01 / Phase 158, not here. Phase 156's figures are WARM by design | none for this phase; note the cold requirement is Phase 158's |
| **Wire / host lockstep** | **None.** Zero protocol change, zero constant change, zero message-id change (verified). `firestarter_app` needs no edit and its 1976-case suite is not in this phase's blast radius | none |
| **Committed goldens and source-contract records** | **`tests/golden/protocol_branch_inventory.json` — 2 legs RED, measured.** This is the one "runtime state" this phase genuinely invalidates: a committed record of the source's shape | **Re-derive with the gate's own extractor, in the same commit as the `eprom.cpp` edit**, and state which sites moved and why |
| **`.planning/` line citations** | ~317 citations shift (`flash_utils.cpp` 97/97 — all of them, from one added `#include` at line 9 · `flash_intel.cpp` 147 · `eeprom_28c.cpp` 71 · `eprom.cpp` 2 of 840), plus part of `memory.cpp`'s 199. Source-internal citations shift too — e.g. `eeprom_28c.cpp:265` already cites `flash_intel.cpp:112-121` for a function that lives at `:187` | **None here.** Expected staleness, close-blocked by REMAP-04 (D-05). Do **not** remap in this phase. Per-file figures `[CITED: ROADMAP.md:181]`, which attributes them to Phases 155–157 collectively |

---

## Common Pitfalls

### Pitfall 1 — `git apply` of the whole patch fails, and the failure looks bigger than it is
Only `src/proms/eeprom_28c.cpp` fails, and only on one swept trailing context line. `-C1` or
`--3way` apply the whole Phase-156 subset cleanly. **Warning sign:** concluding the patch is
unusable and hand-transcribing eight blocks.

### Pitfall 2 — cherry-picking from the wrong ref
`size-reduction-survey` does **not** carry this work.
`wip/v1.33-size-reduction-survey-preserved` @ `a6b46f8` does. Neither carries DEDUP-04. And neither
can be cherry-picked onto today's tree — both fork `8695ee5`, before Phase 154's sweep. Use them as
semantic references.

### Pitfall 3 — quoting `−268` / `−158` as measured here
They are not (C-3). Either land two commits and measure each, or quote only `−426`.

### Pitfall 4 — asserting byte-identity for DEDUP-04
The `.hex` SHA changes on all three targets while the sizes do not (C-4). The oracle is
`flash_used` and `ram_used`.

### Pitfall 5 — thinking Case 25 passing means DEDUP-04 is safe
Measured: it passes while taking 1 call instead of 4. **A green suite is not evidence for this
change** until the loop condition is flipped and a `calls == 4` assertion pins it.

### Pitfall 6 — adding a native case to `native` / `native_nodevtools`
`compare_native` asserts `cases == 172` by **exact equality**, both directions. One added case
reddens the default-baseline gate until Phase 158 re-records. Prefer strengthening existing cases,
or add to `native_loop_v131` (floor-gated, not equality-gated) and record the CI gap.

### Pitfall 7 — a throwaway worktree named anything but `firestarter`
`test_checker_convention.py::test_scope_is_firmware_only` hard-codes the directory name and fails
with `got ('<yourname>', 'scripts')`. Measured. Name it `firestarter`.

### Pitfall 8 — running `pytest tests/` on a dirty tree
Four modules assert `git status --porcelain == ""` after their planted-mutation tests, and several
read `git rev-parse HEAD:<path>` rather than the working tree. On an uncommitted tree you get 6
failures, 4 of them spurious and one (`test_blob_shas_match…`) a **false GREEN** that turns RED once
you commit. **Commit, then run.**

### Pitfall 9 — the native suite is load-flaky (D-04)
172/172 at ~21–35 s here, but 171/172 and 158-with-2-ERRORED have both been observed at 1:13 and
1:44. Never blame this change on N=1. And note a real failure inflates the reported total
(173 vs 172), so read the failure line, not the count.

### Pitfall 10 — `avr-nm` / `avr-objdump` are not on `PATH`
`~/.platformio/packages/toolchain-atmelavr/bin/avr-{nm,objdump}`.

### Pitfall 11 — the LTO ledger will not close
−624 B of symbol deltas against a −426 B image. `eprom_internal_check_chip_id` stops existing and
is inlined into `main`. Expected; do not fudge the difference or hunt for a bug.

### Pitfall 12 — searching `flash_intel_write_init` for the VPP blocks
They are lexically in `static flash_intel_check_vpp` (C-1).

---

## Code Examples

### Extracting only this phase's hunks from the composed patch

```bash
# Source: written and run for this research. Produces a 6-file, Phase-156-only patch
# from the 11-file composed reference, keeping only hunk 1 of memory.cpp (the two
# helpers) and dropping Phase 155's already-landed blank-check hunks.
python3 - <<'PY'
import re
src = open('.planning/notes/firmware-size-reduction-measured.patch').read()
want = {'include/memory_utils.h': None, 'src/proms/eeprom_28c.cpp': None,
        'src/proms/eprom.cpp': None, 'src/proms/flash_intel.cpp': None,
        'src/proms/flash_utils.cpp': None,
        'src/proms/memory.cpp': ['@@ -230,6 +230,52 @@']}
out = []
for p in re.split(r'(?m)^(?=diff --git )', src):
    if not p.startswith('diff --git'):
        continue
    f = re.match(r'diff --git a/(\S+) b/', p).group(1)
    if f not in want:
        continue
    keep = want[f]
    if keep is None:
        out.append(p)
        continue
    hs = re.split(r'(?m)^(?=@@ )', p)
    out.append(hs[0] + ''.join(h for h in hs[1:] if any(h.startswith(k) for k in keep)))
open('/tmp/dedup156.patch', 'w').write(''.join(out))
PY

cd firestarter
git apply --check -C1 /tmp/dedup156.patch && git apply -C1 /tmp/dedup156.patch
```

### Measuring the phase delta, all three targets

```bash
# Source: run this session. Warm figures, matching 155-after-figures.md's convention.
cd firestarter
pio run -e uno -e uno328pb -e leonardo 2>&1 | grep -E '^(RAM|Flash):'
# before: 24660/1567  24708/1573  26804/2008
# after:  24234/1567  24282/1573  26378/2008     -> -426 / 0 on all three
```

### DEDUP-01's mechanical criterion: `__udivmodhi4` call sites

```bash
# Source: run this session. 31 before (NOT 30 -- see C-2), 13 after.
OBJDUMP=~/.platformio/packages/toolchain-atmelavr/bin/avr-objdump
$OBJDUMP -d .pio/build/uno/firestarter_uno.elf | grep -cE '(r?call|jmp).*__udivmodhi4'
```

### DEDUP-04's oracle — size identity, never image identity

```bash
# Source: written and run this session. Records BOTH results, because the size
# claim holds and the byte-identity claim does NOT (C-4).
for e in uno uno328pb leonardo; do
  pio run -e "$e" 2>&1 | grep -E '^(RAM|Flash):' | sed "s/^/$e /"
  sha256sum ".pio/build/$e/firestarter_$e.hex"      # WILL differ -- expected, not a failure
done
```

### Re-deriving the branch inventory with the gate's own extractor

```bash
# Source: written and run this session. Yields total_sites 23 -> 21,
# protocol_keyed_sites 1 -> 1, other_sites 22 -> 20, two sites removed and none added.
cd firestarter && python3 - <<'PY'
import importlib.util, json
spec = importlib.util.spec_from_file_location("pbi", "tests/test_protocol_branch_inventory.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
live = m._extract_predicates(open('src/proms/eprom.cpp').read())
rec  = json.load(open('tests/golden/protocol_branch_inventory.json'))
print("live", len(live), "recorded", len(rec['sites']), rec['counts'])
for s in live:
    print(s)
PY
```

### The four DEDUP-03 planted transpositions (the mismatch-test template)

```bash
# Source: written and run this session against the DEDUP-applied tree.
# A: RED in native_loop_v131 (3 cases), BLIND in native
sed -i 's/force ? RESPONSE_CODE_WARNING : RESPONSE_CODE_ERROR/force ? RESPONSE_CODE_ERROR : RESPONSE_CODE_WARNING/' src/proms/eprom.cpp
# B: BLIND EVERYWHERE  <-- blind spot 1
sed -i 's/MSG_WARN_VPP_LOW, RESPONSE_CODE_WARNING/MSG_WARN_VPP_LOW, RESPONSE_CODE_ERROR/' src/proms/eprom.cpp src/proms/flash_intel.cpp
# C: RED in native (2 cases)
sed -i 's/warn_only ? RESPONSE_CODE_WARNING : RESPONSE_CODE_ERROR/warn_only ? RESPONSE_CODE_ERROR : RESPONSE_CODE_WARNING/' src/proms/memory.cpp
# D: BLIND EVERYWHERE  <-- blind spot 2
sed -i 's/warn_only ? MSG_WARN_CHIP_ID_MISMATCH : MSG_ERR_CHIP_ID_MISMATCH/warn_only ? MSG_ERR_CHIP_ID_MISMATCH : MSG_WARN_CHIP_ID_MISMATCH/' src/proms/memory.cpp
```

### The DEDUP-04 flip, authored (no patch exists for this)

```c
/* Source: written and measured this session. src/operation_utils.cpp,
 * op_execute_stateful_operation -- 6 return sites. Sites 3 and 4 are NOT literals. */
-                return true;   // Not finished yet, waiting for final ACK
+                return false;  // Not finished yet, waiting for final ACK
-            return false;      // Received final ACK (or junk), command is finished.
+            return true;       // Received final ACK (or junk), command is finished.
-            return res == RETURN;
+            return res != RETURN;
-            return callback(handle);
+            return !callback(handle);        /* the callback keeps its own convention */
-        return true;                          /* MAIN not yet started */
+        return false;
-    return false;                             /* the D-06 NULL-main refusal */
+    return true;
```

```bash
# and the 9 wrapper call sites (src/eprom_operations.cpp), verified count == 9:
grep -c 'return !op_execute_' src/eprom_operations.cpp   # 9
sed -i 's/return !op_execute_/return op_execute_/' src/eprom_operations.cpp
```

---

## Environment Availability

| Dependency | Required by | Available | Version | Fallback |
|---|---|---|---|---|
| PlatformIO Core | every build and test leg | ✓ | 6.1.19 (`/usr/local/bin/pio`) | — |
| `toolchain-atmelavr` (`avr-gcc`, `avr-nm`, `avr-objdump`) | all three AVR builds; symbol and disassembly evidence | ✓ | avr-gcc 7.3.0 | — |
| `framework-arduino-avr` / `-minicore` | `uno`/`leonardo` and `uno328pb` | ✓ | 5.3.0 / 3.1.2 | — |
| ArduinoFake | every native env | ✓ | 0.4.0 (`.pio/libdeps/native/`) | — |
| Python 3 | `pytest tests/`, the extractor re-derivation | ✓ | 3.12.13 | ⚠ CI uses a different minor; these gates are stdlib-only, so low risk |
| pytest | the third CI leg | ✓ | 9.1.1 | — |
| git ≥ 2.x with `worktree` | throwaway planted-negative proofs | ✓ | — | — |
| Physical RURP shield / EPROM | **not required** (D-02) | ✗ | — | No criterion needs one; no bench claim is made |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** none.

Verified this session: all three AVR targets build; `pio test -e native` 172/172 in 21 s;
`pio test -e native_nodevtools` 172/172 in 71 s; `pio test -e native_loop_v131` 80/80 in 8 s;
`pytest tests/` 313 passed / 32 skipped on a clean committed tree (plus the 2 expected
branch-inventory reds and 1 worktree artifact on the patched tree).

---

## Validation Architecture

`workflow.nyquist_validation` is not `false` in `.planning/config.json`, so this section is required
and the plan-phase orchestrator will lift it into `156-VALIDATION.md`.

### Test framework

| Property | Value |
|---|---|
| Native framework | Unity via PlatformIO `test_framework = unity` |
| Gate framework | pytest 9.1.1 over `firestarter/tests/` (38 modules) |
| Config file | `firestarter/platformio.ini` (10 envs; 6 native) |
| **CI legs, exhaustively** | `pio test -e native` · `pio test -e native_nodevtools` · `pytest tests/ -v` · `pio run` — `.github/workflows/build.yml:142,155,161,193` and `beta-build.yml:122,128,134,145`. **Nothing else.** |
| Quick run (per task commit) | `pio test -e native` (~21–35 s) |
| Full suite (per wave merge) | `pio test -e native && pio test -e native_nodevtools && pytest tests/ -q` |
| Size measurement | `pio run -e uno -e uno328pb -e leonardo` + `grep -E '^(RAM\|Flash):'` |
| Phase gate | all of the above green, plus `scripts/check_size_baseline.py --policy merge05` (local-run only) |

### Measured baselines, today, at `adf1a31` on a clean tree

| Leg | Result |
|---|---|
| `pio test -e native` | **172 cases / 17 suites / 172 succeeded**, 21 s |
| `pio test -e native_nodevtools` | **172 / 17 / 172**, 71 s |
| `pio test -e native_loop_v131` (**not in CI**) | **80 / 2 suites / 80 succeeded**, 8 s (`test_loop_eprom_v131` 47 + `test_vpp_eprom_v131` 33) |
| `pytest tests/` | **313 passed / 0 failed / 32 skipped** (committed clean tree) |
| `pio run` × 3 targets | 24660/1567 · 24708/1573 · 26804/2008 |
| `tests/golden/protocol_branch_inventory.json` blob-SHA leg | GREEN (`838aca47…` matches) |

### Phase requirements → test map

| Req | Behaviour to prove | Test type | Automated command | Exists? |
|---|---|---|---|---|
| DEDUP-01 | One helper replaces 4 blocks; **8-byte payload unchanged**; arithmetic and `uint16` promotion preserved | native behavioural | `pio test -e native_loop_v131` — `test_vpp04_a` asserts `logged_id_param_count == 8` | ✅ exists (payload **length** only) |
| DEDUP-01 | Payload **byte values** unchanged | native behavioural | *no oracle exists* | ❌ **Wave 0** — optional; see ceiling below |
| DEDUP-01 | `__udivmodhi4` call sites fall to 13 | mechanical | `avr-objdump -d …\|grep -cE '(r?call\|jmp).*__udivmodhi4'` → `13` | ✅ command verified; **no committed gate** |
| DEDUP-01 | −426 B flash, RAM unchanged, all 3 targets | measurement | `pio run -e uno -e uno328pb -e leonardo` | ✅ verified |
| DEDUP-01 | No behaviour change on the four VPP paths | native regression | `pio test -e native_loop_v131` (80/80) + `pio test -e native` (172/172) | ✅ both verified green on the patched tree |
| DEDUP-02 | One helper replaces 4 chip-ID blocks; the four sites and six divergences are enumerated and the semantic **stated** | documentary + native regression | §DEDUP-02 of this file → the plan's own record; `pio test -e native` 172/172 | ✅ |
| DEDUP-02 | `response_code` fork preserved | native behavioural | `pio test -e native` — `test_case7_mismatching_chip_id_with_force_warns` (`:803`) + `test_migrated_mismatching_chip_id_errors` (`:619`); **proven able to fail** by probe C | ✅ exists, **in CI** |
| DEDUP-02 | The standalone `CMD_CHECK_CHIP_ID` path still refuses **unconditionally**, independent of FLAG_FORCE (divergence 1) | native behavioural | *no oracle exists* | ❌ **Wave 0** — the one place divergence 1 could silently regress |
| **DEDUP-03** | A transposed VPP **over-voltage** `response_code` fails a test | native, planted-negative | `pio test -e native_loop_v131` (probe A → 3 RED) | ✅ exists — but **NOT in CI** |
| **DEDUP-03** | A transposed VPP **under-voltage** severity fails a test | native, planted-negative | *nothing catches probe B* | ❌ **Wave 0 — BLIND SPOT 1** |
| **DEDUP-03** | A transposed chip-ID **`response_code`** fails a test | native, planted-negative | `pio test -e native` (probe C → 2 RED) | ✅ exists, **in CI** |
| **DEDUP-03** | A transposed chip-ID **message id** fails a test | native, planted-negative | *nothing catches probe D* | ❌ **Wave 0 — BLIND SPOT 2** |
| DEDUP-04 | Flip is **size**-neutral on all 3 targets | measurement | `pio run -e uno -e uno328pb -e leonardo`, compare `flash_used`/`ram_used` | ✅ verified `0/0` ×3 |
| DEDUP-04 | 9 `!` gone, 6 engine returns flipped, defensive comment removed | source-scan | `grep -c 'return !op_execute_' src/eprom_operations.cpp` → `0` | ✅ command verified; **no committed gate** |
| DEDUP-04 | The op-layer contract still holds after the flip | native behavioural | `pio test -e native` — Case 24 (`:1426`) must be **flipped**; Case 25 (`:1524`) must be **de-vacuumed** with `calls == 4` | ⚠ **both must be edited**; measured 1 RED + 1 silent vacuity |
| all | `eprom.cpp`'s pinned branch inventory matches after the edit | pytest source-contract | `pytest tests/test_protocol_branch_inventory.py -q` | ⚠ **2 legs RED until re-derived** |
| all | No other committed gate regressed | pytest | `pytest tests/ -q` | ✅ 313 pass on the patched+committed tree, modulo the 2 above |

### ⚠ The honest coverage ceilings — stated, not implied

1. **`src/eprom_operations.cpp` compiles in NO native environment.** `[env:native]`'s
   `build_src_filter = +<proms/> +<boards/rurp_serial_utils.cpp> +<json_parser.c>
   +<operation_utils.cpp>`. So the nine dropped `!` have **no behavioural oracle** — only the
   size-identity build and source inspection. `src/operation_utils.cpp` **is** in the filter, so
   the 6 flipped returns are covered, by Cases 24/25 and nothing else. No phase artifact may imply
   native coverage of the wrappers.
2. **`test_vpp_eprom_v131` and `test_flash_intel_vpp` are in no CI leg.** `test_vpp_eprom_v131`
   runs only under `pio test -e native_loop_v131`, a local-only env whose own comment says
   "**NO CI COVERAGE**". `test_flash_intel_vpp` is in **no env's `test_filter` at all** — a
   KNOWN-FLAKY suite disabled since Phase 17, whose own SAF-04 assertions "have never been observed
   to execute". So the entire `flash_intel.cpp` VPP path — two of DEDUP-01's four blocks — has
   **zero executing test coverage in any environment**, and its regression evidence is the
   `eprom.cpp` twin's plus the source-level byte-identity of the two blocks.
3. **The AVR 16-bit promotion is unobservable natively.** Native `int` is 32-bit, so no native test
   can attest the AVR arithmetic or its wrap above 65485 mV. Identical before and after; not a
   regression; not covered.
4. **The 8-byte payload's byte *values* have no oracle anywhere.** `test_vpp04_a` asserts the
   length is 8. Criterion 1's "the emitted 8-byte payload is unchanged" is therefore established by
   **source-level identity of the arithmetic** (the extracted expressions are character-identical to
   the four originals, and the parameter types are identical) plus the length assertion — **not by a
   value comparison**. Say so; do not let the record read as if the bytes were compared.
5. **`scripts/check_size_baseline.py` runs in no CI workflow at all** (LAND-04). Every size gate is
   a local-run obligation.
6. **No bench claim.** D-02. Nothing here is attested on silicon.

### Sampling rate

- **Per task commit:** `pio test -e native` (~21–35 s). For a commit touching `eprom.cpp` or
  `flash_intel.cpp`, also `pio test -e native_loop_v131` (~8 s) — it is the only suite that
  executes those VPP paths.
- **Per wave merge:** `pio test -e native` + `pio test -e native_nodevtools` + `pytest tests/ -q`,
  plus `pio run -e uno -e uno328pb -e leonardo` with the figures recorded.
- **Per commit touching `eprom.cpp`:** `pytest tests/test_protocol_branch_inventory.py -q` **in the
  same commit** as the re-derived golden (the one-commit property).
- **Phase gate:** every leg above green; `check_size_baseline.py --policy merge05` run and its
  one-sidedness recorded (D-03); each new DEDUP-03 assertion seen RED against its planted
  transposition and GREEN against the real tree; native suite not trusted at N=1 (D-04).

### Wave 0 gaps

- [ ] **`test/native/avr/test_vpp_eprom_v131/test_vpp_eprom_v131.cpp`** — the under-voltage
      `(MSG_WARN_VPP_LOW, RESPONSE_CODE_WARNING)` pairing, for both `eprom.cpp` and
      `flash_intel.cpp` if reachable. Closes **blind spot 1** (probe B). Env
      `native_loop_v131`; gate is a floor (≥ 32), so adding cases is free. **Not CI-visible** —
      must be recorded as such.
- [ ] **`test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp` and/or
      `test_sdp_harness.cpp`** — chip-ID **message-id** assertions
      (`count_logged_id(MSG_WARN_CHIP_ID_MISMATCH)` / `MSG_ERR_CHIP_ID_MISMATCH`) added to the two
      cases that already assert `response_code`. Closes **blind spot 2** (probe D), **in CI**, and
      keeps `cases == 172` by strengthening rather than adding. ⚠ Requires an id-capture helper in
      those suites' stubs; verify one exists before committing to this shape (`test_vpp_eprom_v131`'s
      `count_logged_id` lives in its own `host_stubs.cpp` and may not be shared).
- [ ] **`test_eeprom28c_sdp.cpp:1487`** — Case 24's polarity assertion **must** flip
      (`TEST_ASSERT_FALSE` → `TEST_ASSERT_TRUE`) with its message rewritten. Measured RED.
- [ ] **`test_eeprom28c_sdp.cpp:1582-1590`** — Case 25's drive loop **must** be flipped and a
      `calls == 4` assertion added. Measured: passes vacuously after the flip.
- [ ] **`tests/golden/protocol_branch_inventory.json`** — re-derive with the module's own
      extractor: `total_sites` 23 → 21, `protocol_keyed_sites` 1 → 1, `other_sites` 22 → 20; two
      sites removed, none added; record that the `chip_id` predicate **moved into `memory.cpp`**.
- [ ] *(optional, high value)* a source-scan gate for DEDUP-04 —
      `grep -c 'return !op_execute_' src/eprom_operations.cpp == 0` plus the six flipped engine
      returns — following `tests/test_write_path_source_contract_v131.py`'s idiom. This is the only
      mechanical check possible on a TU that compiles in no native env. ⚠ Must be non-vacuous: a
      zero-match grep passes trivially against a deleted file, so pair it with a non-vacuity leg
      (the project has been bitten by exactly this — see Pitfall 8 in `155-RESEARCH.md`).
- [ ] *(optional)* a `mem_util_report_voltage` payload-**value** oracle, closing ceiling 4.
      Not required by any criterion; recorded so the gap is visible.

Framework install: **none needed** — everything is present and verified.

---

## Security Domain

`security_enforcement` is not `false`, so this section is required. This is embedded firmware with
no network surface, no authentication and no cryptography.

### Applicable ASVS categories

| ASVS category | Applies | Standard control here |
|---|---|---|
| V2 Authentication | **no** | No user or credential concept; the device trusts whatever is on the serial line by design |
| V3 Session Management | **no** | The three-phase INIT/MAIN/END state machine is a transfer protocol, not a session. DEDUP-04 changes the **polarity** of its completion signal but not its states — and the polarity is covered by Cases 24/25 |
| V4 Access Control | **no** | No principals |
| V5 Input Validation | **yes, and untouched** | `json_parser.c` silently skips unknown fields (deliberate forward-compat) and `configure_memory`'s fail-closed tail refuses unknown protocols. **This phase adds no wire field and validates no new input.** The known fail-closed breach (`extract_long("algorithm", …)` with no range check) is **Phase 157 / DECODE-05's** requirement, not this phase's — do not fix it here |
| V6 Cryptography | **no** | The only primitive is CRC8-CCITT for framing integrity, not security. Untouched |
| V7 Error handling / logging | **yes — this is the phase's whole subject** | Severity rides entirely in the message id (`logging_id.h:105,119`). Both helpers must pair id and `response_code` correctly. Controls: the DEDUP-03 planted-transposition tests |
| V10 Malicious code | **no** | No dependency added; no `postinstall` surface |
| V12 Files / resources | **no** | No filesystem |
| V14 Configuration | **partial** | `platformio.ini` build flags are untouched. `HARDWARE_REVISION` and `DEV_TOOLS` gating unchanged; both native envs still exercised |

### Known threat patterns for this stack

| Pattern | STRIDE | Standard mitigation | Status in this phase |
|---|---|---|---|
| A refusal downgraded to a warning by a transposed severity, so unsafe high voltage is applied to a part the firmware just measured as out of range | **Tampering / Repudiation** | Assert the (id, `response_code`) pair in both directions, per path, with a planted-negative proof | ⚠ **The core risk.** Over-voltage: covered (non-CI). Under-voltage: **BLIND**. Chip-ID id: **BLIND**. Wave 0 closes both |
| A silent-success command reporting OK having done nothing (DEVTEST-01's phantom erase) | Repudiation | The D-06 NULL-main refusal at `operation_utils.cpp:173` | ⚠ DEDUP-04 flips **exactly that return**. Case 24 is its only oracle and it goes RED by construction — flip the assertion, never delete the case |
| An assertion that passes for the wrong reason after a semantic change | Repudiation | Non-vacuity legs and planted negatives | ⚠ **Measured live**: Case 25 passes taking 1 call instead of 4 |
| High voltage left asserted on a refusal path | Tampering | `EPROM_HV_ALL_OFF_MASK` unconditional clear; `test_vpp04_b` / `test_vpp02_e1` | ✅ Unchanged by this phase and verified green; probe A confirms `test_vpp02_e1` is live |
| Buffer overrun in payload packing | Tampering | Fixed-size local arrays, fixed indices | ✅ `uint8_t _b[8]` / `_b[4]`, 8 and 4 literal writes, count passed as a literal. Unchanged |
| Integer overflow changing a reported voltage | Tampering | Preserve operand types exactly | ✅ §DEDUP-01; `uint16_t` parameters are load-bearing |
| A dependency-supply-chain compromise | Tampering | Package legitimacy gate | ✅ N/A — no package installed |

---

## State of the Art

| Old approach | Current approach | When changed | Impact on this phase |
|---|---|---|---|
| Four `LOG_{WARN,ERROR}_*` macro families believed to encode severity | Every severity macro is a **pure alias** of `LOG_ID`; severity lives only in the message id | v1.2 catalog (`logging_id.h`) | The enabler. Also the hazard: a fork collapses to one call with a selected id, and no oracle checks the id/`response_code` pair |
| Per-object size attribution | Impossible — `-flto` is on; every `.o` has empty `.text` and 35 `.gnu.lto_*` sections; `main` has swallowed `loop()`, the parsers and all 9 wrappers | PlatformIO AVR default | Always measure the image; the symbol ledger will not close (−624 vs −426) |
| `size_baseline.json` default byte-identity mode as the size gate | `--policy merge05` with four named growth exemptions, one-sided | v1.31–v1.32 | A reduction passes with no exemption (D-03). The default mode will still go RED — LAND-01's job |
| Requirement claims verified by inspection | Committed source-contract gates (blob SHA + positional re-parse) | Phases 140–143 | `test_protocol_branch_inventory.py` must be re-derived, not argued with |
| Golden traces as sufficient regression evidence | Insufficient for severity forks — documented in `reference_golden_trace_misses_severity_fork.md` and cited in-source at `test_eeprom28c_sdp.cpp:788` | v1.16 Phase 89 CR-01 | Exactly DEDUP-03's premise, and now measured (probes B and D) |

**Deprecated / outdated:**

- **`size-reduction-survey` as the reference branch** (named in the survey front-matter and ROADMAP
  §v1.33) — it does not carry this work. Use `wip/v1.33-size-reduction-survey-preserved` @ `a6b46f8`.
- **"30 `__udivmodhi4` call sites"** — 31 at this phase's start (C-2).
- **`op_execute_stateful_operation.constprop.44`** — `.constprop.42` today (C-5).
- **"the blocks are inside `flash_intel_write_init`"** — lexically inside `flash_intel_check_vpp` (C-1).
- **"byte-for-byte identical" for the DEDUP-04 flip** — size-identical only (C-4).
- **"DEAD-06 is the only requirement in Phases 155–158 that touches a test file"** — false once
  OD-2 resolves DEDUP-04 toward removal (C-7).

---

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|---|---|---|
| **A1** | The 31st `__udivmodhi4` call site (vs the survey's 30) was introduced by Phase 155's 32-bit voltage reformulation | C-2 | **Low.** The *count* (31 → 13) and the derived "24 in the four blocks" are both measured; only the *attribution* of the extra site is inferred. A plan may confirm it in one command (`avr-objdump -d` before/after `46dd574`) or simply not claim a cause |
| **A2** | `avr-gcc`'s `int` is 16-bit on all three AVR targets, so `uint16_t + 50` promotes to `unsigned int` | DEDUP-01 | **Very low.** Corroborated mechanically: the blocks compile to `__udivmodhi4` (the 16-bit helper), not `__udivmodsi4`. If somehow wrong, the promotion analysis is wrong but the *conclusion* — keep the parameters `uint16_t`, do not widen — is unchanged, since it rests on type identity, not on the width |
| **A3** | Adding cases to `test_vpp_eprom_v131` trips no gate | DEDUP-03 Option 1 | **Low.** `check_size_baseline.py`'s `compare_native` reads only the three envs in `native_envs`, and `test_requirement_case_mapping_v131.py`'s check is a floor (≥ 32, live 33) — both verified by reading the code. Not verified by *actually adding* a case; a plan should confirm empirically before relying on it |
| **A4** | `test_eeprom28c_sdp` / `test_sdp_harness` can assert a frame **id** (needed for DEDUP-03 Option 2) | Wave 0 | **Medium — the biggest open risk in the plan shape.** Probe C proves those suites see `response_code`; it does **not** prove they can see ids. `count_logged_id` lives in `test_vpp_eprom_v131/host_stubs.cpp`, whose own comment says asserting "by id" is something "nothing else in the tree does". If no id-capture exists there, blind spot 2 can only be closed non-CI (Option 1) or by porting the capture. **Verify before planning the shape.** |
| **A5** | `git apply -C1` will still apply cleanly at plan time | Prior Art | **Low.** Verified at `adf1a31`; only invalidated if something else edits these six files first. Re-run `--check` at plan time |
| **A6** | Case 25's post-flip 1-call exit means the ACK sequence is unexercised, not merely shorter | DEDUP-04 | **Low.** Measured `Expected 4 Was 1` with the case's own comment stating four are required. The remedy (flip the loop + assert `calls == 4`) is correct either way |
| **A7** | `test_flash_intel_vpp` runs in no environment and its SAF-04 assertions have never executed | Ceiling 2 | **Low.** Its absence from every `test_filter` is verified by reading `platformio.ini`; the "never observed to execute" clause is `[CITED: test_vpp_eprom_v131.cpp:602-612]`, not independently re-derived here |
| **A8** | Per-file `.planning/` citation-shift counts (97 / 147 / 71 / 2) | Runtime State Inventory | **Low, and inconsequential.** `[CITED: ROADMAP.md:181]`, which attributes them to Phases 155–157 collectively. The plan does nothing with these numbers — REMAP-01 owns them |

---

## Open Questions

1. **Where does the chip-ID message-id mismatch test live?**
   - **What we know:** blind spot 2 is real and measured (probe D). The chip-ID `response_code` is
     already covered *in CI* by two cases. `test_vpp_eprom_v131` has a proven id-capture harness but
     no CI coverage. Adding a case to `native` reddens the exact-equality case-count gate.
   - **What's unclear:** whether `test_eeprom28c_sdp` / `test_sdp_harness` can capture frame **ids**
     (A4).
   - **Recommendation:** first command of Wave 0 — grep those two suites' `host_stubs.cpp` for an
     id-capture facility. If present, **strengthen the two existing cases** (CI-visible, case count
     unchanged — the best outcome). If absent, close blind spot 2 in `test_vpp_eprom_v131` and
     record the CI gap explicitly, exactly as DEAD-05 recorded its ceiling.

2. **One commit or two for DEDUP-01 and DEDUP-02?**
   - **What we know:** −426 B combined is measured; the −268/−158 split is not (C-3). They are
     separate requirements. The milestone's own reason for sequencing 155 before 156 is "keep each
     phase's measured delta attributable".
   - **Recommendation:** **two commits**, DEDUP-01 then DEDUP-02, each measured on all three
     targets. That is the only way each requirement's stated figure becomes evidence rather than
     inheritance. Both commits must precede the `protocol_branch_inventory.json` re-record — or,
     better, the re-record rides whichever commit touches `eprom.cpp` last, so the gate goes RED
     once. **Note this makes the one-commit property and the two-commit split interact: decide the
     ordering explicitly.**

3. **Does DEDUP-04 land in this phase's own commit sequence, or last?**
   - **What we know:** it is size-neutral in isolation and in composition (measured), and its test
     blast radius (2 native cases) is disjoint from DEDUP-01/02's.
   - **Recommendation:** **last, alone.** A stand-alone commit lets its "zero bytes" claim be a
     direct before/after on an otherwise-unchanged tree, which is exactly what criterion 4 asks
     for, and keeps the two test edits attributable.

4. **Is a committed source-scan gate for DEDUP-04 in scope?**
   - **What we know:** `eprom_operations.cpp` has no native coverage, so a source scan is the only
     mechanical check available. The repo has three precedents.
   - **Recommendation:** **yes, if it fits the plan budget** — but only with a non-vacuity leg
     (a zero-match grep passes against a deleted file). If not taken, state plainly that the nine
     dropped `!` are attested by inspection and the size-identity build alone.

5. **Should the `eeprom_28c.cpp:265` stale in-source citation (`flash_intel.cpp:112-121` → `:187`)
   be repaired here?**
   - **What we know:** it is already stale, in a file this phase edits, and Phase 159's remap
     targets `.planning/` citations — not source-internal ones. D-05 bounds `.planning/` staleness;
     it says nothing about in-source comments.
   - **Recommendation:** **repair it as part of the DEDUP-02 edit to that file** (it is one line, in
     a comment being touched anyway) and record it as an incidental fix, not as scope creep. If the
     plan prefers zero incidental edits, note it and hand it to Phase 159 — but do not leave it
     unrecorded.

---

## Sources

### Primary (HIGH confidence — measured or executed in this session)

- `pio run -e uno -e uno328pb -e leonardo` — before, DEDUP-only, flip-only, and combined: all
  twelve flash/RAM figures
- `pio test -e native` (172/172), `-e native_nodevtools` (172/172), `-e native_loop_v131` (80/80)
  — on the baseline tree and on the DEDUP tree
- `pio test -e native` on the **flipped** tree — 1 RED (`test_case24…:1426`) + the planted
  `Expected 4 Was 1` probe proving Case 25 vacuous
- Four planted transpositions (probes A–D) × two/three envs — the DEDUP-03 coverage matrix
- `pytest tests/` on the DEDUP tree, uncommitted (6 failures) and committed (3, of which 1 is a
  worktree artifact)
- `avr-nm -S` before/after — the nine-symbol flash ledger, including the 190 B and 90 B helpers
- `avr-objdump -d | grep -cE '(r?call|jmp).*__udivmodhi4'` — **31** before, **13** after
- `avr-objdump -d` full diff — 5450 differing lines for the flip; the +2 B relocation and the
  `brne`/`breq` swaps
- `sha256sum` on all three `.hex` files × four tree states, plus a same-source cold-rebuild
  reproducibility control
- `git apply --check` / `-C1` / `--3way` on the extracted six-file subset
- `git hash-object` on nine source files vs every `tests/golden/*.json` `blob_shas` record
- `test_protocol_branch_inventory.py::_extract_predicates` run against the patched `eprom.cpp` —
  the re-derived 21-site inventory
- `git diff`/`git grep` against `size-reduction-survey` and
  `wip/v1.33-size-reduction-survey-preserved` — establishing which ref carries what
- `command -v` / `--version` for pio 6.1.19, python 3.12.13, pytest 9.1.1, the AVR toolchain

### Primary (HIGH confidence — read in this session)

- `firestarter/src/proms/{eprom,flash_intel,flash_utils,eeprom_28c,memory}.cpp`,
  `src/{eprom_operations,operation_utils,firestarter}.cpp`
- `firestarter/include/{firestarter,logging_id,messages,memory_utils,operation_utils}.h`
- `firestarter/platformio.ini` — all 10 envs, both `test_filter` allowlists, every `build_src_filter`
- `firestarter/scripts/check_size_baseline.py` (`_merge05_flash_allowance`, `compare_avr_merge05`,
  `compare_native`) and `scripts/baseline/size_baseline.json`
- `firestarter/.github/workflows/{build,beta-build}.yml` — the four CI legs
- `firestarter/tests/golden/protocol_branch_inventory.json` and the four gate modules that scan
  `eprom.cpp`
- `firestarter/test/native/avr/{test_vpp_eprom_v131,test_eeprom28c_sdp}/…`
- `.planning/notes/firmware-size-reduction-{survey.md,measured.patch}` (in full)
- `.planning/{REQUIREMENTS,ROADMAP,STATE,config.json}` · `.planning/v1.33/155-after-figures.md`
- `.planning/phases/155-*/155-RESEARCH.md` (structure precedent)
- `/workspaces/CLAUDE.md` and `/workspaces/firestarter/CLAUDE.md`

### Secondary (MEDIUM confidence)

- `.planning/ROADMAP.md:181` — the per-file citation-shift counts (attributed to Phases 155–157
  collectively, not re-derived here)
- `test_vpp_eprom_v131.cpp:602-612` — the claim that `test_flash_intel_vpp` "runs in no PlatformIO
  environment and SIGABRTs after case 1"; the *no-environment* half is independently verified,
  the SIGABRT half is cited
- The project memory notes on golden-trace severity blindness, gates asserting repo porcelain, and
  worktree traps — each independently corroborated by a measurement above

### Tertiary (LOW confidence — flagged, not relied upon)

- The survey's `−268` / `−158` split (not reproducible at this position — C-3)
- The survey's attribution of the extra `__udivmodhi4` site (A1)

No external documentation lookup was performed: this phase touches no third-party library, adds no
dependency, and every question it raises is answerable from the repository and its toolchain. The
one language-level claim (integer promotion) is `[CITED: ISO C]` and independently corroborated by
the emitted helper calls.

---

## Metadata

**Confidence breakdown:**

| Area | Level | Reason |
|---|---|---|
| DEDUP-01 / DEDUP-02 size and symbol figures | **HIGH** | Measured on all three targets from this phase's exact anchor; the survey's per-function figures reproduce to the byte |
| The `uint16 + 50` promotion analysis | **HIGH** | Language rule plus mechanical corroboration (`__udivmodhi4` vs `__udivmodsi4`) |
| The DEDUP-02 four-site enumeration and the six divergences | **HIGH** | Read verbatim from source, with the two `eprom.cpp` caller policies traced to their call sites |
| DEDUP-03's coverage matrix | **HIGH** | Four planted mutations, each built and run; both blind spots reproduced |
| DEDUP-04's size-neutrality | **HIGH** | Measured on three targets, in isolation and composed |
| DEDUP-04's non-byte-identity | **HIGH** | Three `.hex` SHAs plus a reproducibility control |
| DEDUP-04's test blast radius | **HIGH** | One RED observed; the vacuity proven with a planted probe |
| Gate blast radius | **HIGH** | `pytest tests/` run on a **committed** tree; the new inventory derived with the gate's own extractor |
| Where the new DEDUP-03 cases should live | **MEDIUM** | Option 1's gate-freedom is verified by code reading, not by adding a case (A3); Option 2 depends on an unverified id-capture facility (A4) |
| The `−268` / `−158` split | **LOW** | Not measured at this position (C-3) — do not quote as measured |

**Research date:** 2026-08-23
**Anchor:** `firestarter` @ `adf1a31`, tree clean before and after; throwaway worktree removed and
pruned; `git worktree list` shows only `firestarter` and the pre-existing, untouched
`firestarter_py32_ci`.
**Valid until:** **until anything edits `src/proms/{eprom,flash_intel,flash_utils,eeprom_28c,memory}.cpp`,
`src/{eprom_operations,operation_utils}.cpp`, `platformio.ini`, `scripts/baseline/size_baseline.json`
or `tests/golden/protocol_branch_inventory.json`.** Every figure here is anchored to `adf1a31`; a
new commit under it invalidates the before-position and the two RED gate legs must be re-checked.
Re-run `git apply --check -C1` and `pio run` at plan time rather than trusting these numbers if the
firmware HEAD has moved.
