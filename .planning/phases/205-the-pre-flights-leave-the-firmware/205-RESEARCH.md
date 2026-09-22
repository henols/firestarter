# Phase 205: The pre-flights leave the firmware - Research

**Researched:** 2026-09-22
**Domain:** Dual-repo firmware removal (AVR C/C++) + host CLI capability re-implementation (Python), bench-gated
**Confidence:** HIGH — every number below was measured this session against the live trees at
`firestarter_fw` HEAD `24e3fdf` and `firestarter_app` HEAD `2a17fd7`, both on `v1.41-verification-to-host`.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** **`erase -b` keeps its meaning and is re-implemented on the host**, through Phase 202's
  `check_eprom_blank`. Whole-device, not region-scoped. Opt-in behind `-b`, preserving today's
  polarity (inverted against `write -b`). The host check is a second port open, which resets an
  Uno-class board between the erase and the check — a wall-clock cost, not a correctness one. Phase
  206's SESS-01 is where it collapses; this phase hands it a measured number. **Reversibility:**
  one-way.
- **D-02:** **`erase -b` adopts the `0`/`1`/`2` exit-code contract.** `0` erased and blank, `1`
  erased but not blank, `2` transport or hardware failure during the check. Plain `erase` without
  `-b` keeps `0`/`1` unchanged. The two contracts must be stated in the `-b` help text rather than
  left as folklore. **Reversibility:** one-way.
- **D-03:** **A failed post-erase check prints one terse line and nothing else.** The check runs in
  first-mismatch mode and **`erase` gains no `--full` option**. The documented follow-up is
  `firestarter blank <chip> --full`. State that composition where the operator will read it.
- **D-04:** **Full retirement. FWBLANK-04 stands as written.** The constant leaves `constants.py`,
  the host stops composing `0x08`, and `0x08` appears nowhere on either side except the
  reserved-gap comment. `-b` reaches the Phase 203 guard as an explicit host-side signal rather
  than a wire bit. Accepted cost: a post-205 host driving pre-205 firmware no longer suppresses the
  firmware's surviving pre-flight. Two obligations follow: REL-04 (Phase 207) documents that a
  `3.1.0` CLI wants `3.1.0` firmware for `write -b`; and the regression is observed on silicon in
  this phase (D-07). A host firmware-version gate was considered and rejected. **Reversibility:**
  one-way.
- **D-05:** **The reserved record takes the shape Phase 204's D-02 already pre-committed to for this
  bit** — a comment at the gap in each ladder (`include/firestarter.h`'s control-flag block and
  `constants.py`'s flag block) naming the version the bit was retired in and why it must never be
  reused. The two ladders move in the **same commit pair**. Read `firestarter.h:45-66`'s existing
  ordinal-4 comment for the established wording shape. **One stale sentence this phase must
  correct, not inherit:** `firestarter.h:62-63`'s "survives this retirement … and leaves in Phase
  205."
- **D-06:** **One W27C512 in two roles; `0x06` and `0x10` are test-only, and the gap is stated.** UV
  leg (criterion 3) uses the Phase 201-06 `--skip-erase` rehearsal. Erasable leg (criterion 5) is
  the same part with the erase path on. `0x06` and `0x10` write-init calls are proven removed by
  native test and source-contract gate, not on silicon. **Reversibility:** reversible.
- **D-07:** **The D-04 skew regression is observed on silicon, as a rider on the criterion-3
  sequence — not as a second matrix.** Post-205 host + pre-205 firmware, `write -b` against the
  same non-blank W27C512: capture the firmware's `Not blank` refusal verbatim with its exit code
  and duration. 204's D-07 label discipline applies unchanged — "pre-205"/"post-205" are documented
  label substitutions and the phase record must name the commit sha that played each role.
- **D-08:** **`MSG_ERR_NOT_BLANK` (0xB0) and three orphaned debug ids are KEPT and annotated, in a
  meta-repo-only docs commit**, following 204's D-06 and commit `694acce3`. 0xB0 is not orphaned on
  the host: a post-205 host still *receives* it from pre-205 firmware.
  `DBG_FLAG_SKIP_BLANK` (0x2E) becomes a third orphaned debug id. **Reversibility:** reversible.
- **D-09:** **Full sweep: everything reachable only from the deleted machinery goes with it.**
  Re-verify each site against the live tree at planning time, with `git grep`. **Reversibility:**
  costly.
- **D-10:** **FWBLANK-05's measurement follows the v1.33 precedent verbatim.**
  `pio run -e uno -e uno328pb -e leonardo`, read each target's `Flash:` and `RAM:` summary lines,
  record before/after with the `.elf` and `.hex` sha256 alongside. The build config must be stated,
  not assumed. Leonardo's real ceiling is 28672 B, not the 32768 `platformio.ini` reports — quote
  both. No CI leg gates image size.

### Claude's Discretion

- **The internal mechanism for plumbing `-b`** to the Phase 203 guard once `0x08` is gone — a
  keyword-only bool through `write_eprom`, a parameter on `requires_blank_check`, or another shape
  — provided no `0x08` survives on the host. Two recorded hazards: `build_flags`' own docstring
  states that both production callers pass its first four parameters **positionally**; and
  `chip_test.py:3221` passes its flag positionally too. `write_eprom`'s signature is read by
  roughly forty bool-valued test sites.
- The exact wording of D-05's two reserved-gap comments, of D-08's three catalog annotations, and
  of the rewritten comments at sites 12, 17 and 18.
- Whether `erase -b`'s host check is a new method or a call into `check_eprom_blank` as it stands,
  and where the added wall-clock is measured for Phase 206's benefit.
- The bench sequence order and how the pre-205 firmware `.hex` is produced, within D-07's terms.
- Whether the folded negative-address firmware fix lands in its own plan (**preferred**) or
  alongside a removal plan.

### Deferred Ideas (OUT OF SCOPE)

- **Region-scoping the `0x06` and `0x10` write-init checks** instead of deleting them. Moot —
  this phase deletes them.
- **A dedicated retired-command / retired-flag message.** Best home: Phase 207.
- **Collapsing `erase -b`'s second port open into the erase's own session.** Best home: Phase 206,
  SESS-01. Hand it the measured number.
- **The `DONE`-based clean stop in `op_wait_for_ack`.** CMP-F1. Best home: Phase 206.
- **Retiring the orphaned catalog ids** — now four. Best home: any later phase already paying for a
  codegen run and two sub-repo syncs.

**Reviewed Todos (not folded):** `2026-09-20-region-end-wire-key-has-no-json-parse-coverage.md`,
`2026-09-21-blank-check-sram-fram-shortcircuit-is-inert.md`,
`2026-09-20-devtest-blank-check-folds-transport-failure-into-verdict-bad.md`,
`2026-09-20-preflight-firmware-version-compat-guard.md`,
`2026-09-08-uv-write-shortcut-disclosure-key.md`,
`2026-08-27-strip-gsd-provenance-comments-from-source.md` (**stale, do not action**).

**Folded Todos:** `2026-08-30-write-init-blank-check-is-whole-device.md` (closed by deletion),
`2026-09-20-blank-check-region-fails-open-on-start-greater-than-end.md` (closed by deletion, not by
the local clamp it suggests), `2026-09-16-reject-negative-write-start-address.md` (**firmware half
only**, preferably its own plan and its own commit).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| FWBLANK-01 | the write-init blank check is removed from `eprom.cpp`, `flash_intel.cpp` and `flash_nor_unlock.cpp` | § Measured Site Census rows 8/9/10 — all three verified at exact lines; § Gate Impact names the 8 native suites and 7 pytest legs the removal reddens |
| FWBLANK-02 | the erase-end blank check is removed from `eprom.cpp` | § Census row 7 (`eprom.cpp:52-54`); § Gate Impact identifies `test_erase_end_blank_check_scans_from_zero` as the one native test that asserts this contract and must be **deleted, not re-anchored**; § `erase -b` establishes what the host must gain first |
| FWBLANK-03 | `mem_util_blank_check`, `mem_util_blank_check_region`, `blank_check_saved_address` and `BLANK_CHECK_CHUNK_SIZE` are deleted, and no caller remains | § Census rows 1-6 with corrected line spans; § Survivors proves which neighbours must NOT go with them; § Orphaned-by-the-sweep names two more symbols CONTEXT does not |
| FWBLANK-04 | `FLAG_SKIP_BLANK_CHECK` (`0x08`) is retired from the firmware and from `constants.py`, and the bit is recorded as reserved on both sides | § Census rows 13-21 (firmware + host); § Gate Impact measures 17 host legs and a frozen `dedup_fingerprint` re-key; § Code Examples gives the ladder-comment shape |
| FWBLANK-05 | the flash and RAM freed is measured per AVR target (uno, uno328pb, leonardo) and reported as a number, not an estimate | § Flash and RAM — **the pre-deletion baseline and the post-deletion delta are both measured in this document**: −518 B flash and −4 B RAM, identical on all three targets |
</phase_requirements>

---

## Summary

This is a structural removal with mechanical proof, exactly like Phase 204, and the same method
earned its keep: I built a simulated post-sweep firmware tree beside an identical control, built
both for all three AVR targets, and ran all three test trees against both. Everything below is a
measurement, not an inference.

**The headline number FWBLANK-05 asks for is already in hand.** The sweep frees **518 bytes of
flash and 4 bytes of RAM, identically on `uno`, `uno328pb` and `leonardo`**. That identical-delta
result **contradicts CONTEXT D-10**, which predicted per-target divergence because "`SERIAL_ON_IO`
compiles the progress-emission block out on uno and uno328pb." `SERIAL_ON_IO` does not appear in
`memory.cpp` at all — the guard D-10 is thinking of is in `eprom.cpp`'s write-execute loop, which
this phase does not touch. Two further D-10 premises are also wrong: `DBG_FLAG_SKIP_BLANK` is
`SERIAL_DEBUG`-gated, not `DEV_TOOLS`-gated, and `SERIAL_DEBUG` is **commented out** in
`platformio.ini`'s `[env]` block, so that site contributes **zero** to any shipped build; and
`DEV_TOOLS` defaults to `0` (`firestarter.h:31-32`) and is set only in `[env:native]`, so the AVR
targets are non-DEV_TOOLS builds, the opposite of what D-10 states.

**The census is bigger than CONTEXT's 21 rows and two of its line spans are wrong.** The most
consequential correction is CONTEXT site 4: `mem_util_blank_check_region` is `memory.cpp:467-528`,
not `:467-533` — lines `530-534` are the doc comment belonging to `mem_util_blank_check`, and a
literal 467-533 cut would delete the wrapper's comment while leaving the wrapper. Equally
important, the deletion is **not one contiguous span**: the surviving `mem_util_operation_end` and
its doc comment sit at `memory.cpp:447-458`, *between* the two blocks that go.

**Two symbols are orphaned by the sweep that CONTEXT explicitly says survive.**
`set_operation_in_progress` and `clear_operation_in_progress` have their **only** callers inside
`mem_util_blank_check_region` (`memory.cpp:469` and `:474`). After the sweep nothing in the
firmware or in any test sets the `OPERATION_IN_PROGRESS` bit, so the whole multi-call INIT/END
state machine goes permanently quiescent and five surviving `is_operation_in_progress` guards
become always-true. CONTEXT's Integration Points says these "have callers beyond the blank check;
they survive" — true only for `is_operation_in_progress`.

**The gate impact is measured at 7 + 8 + 17.** Seven pytest legs in the firmware source-scan tree
(one of which, `test_config_schema_pinned.py`, CONTEXT does not predict — it pins literal line
numbers in `src/firestarter.cpp` that the `DBG_FLAG_SKIP_BLANK` deletion shifts). Eight native
Unity suites stop compiling — but **not the eight CONTEXT names**: `test_val_5v_page` survives
(prose only) and `test_verify_error_ids`, Phase 204's own new suite, breaks and is absent from
CONTEXT. And seventeen host legs go red across six modules, including three in
`test_blast_radius_invariance.py` that CONTEXT does not name and that carry an explicit instruction
to land the frozen-hash re-key as a **separate commit**.

**One real hazard D-01 creates and CONTEXT's reasoning misses:** `firestarter erase <0x06 part> -s
0x10000 -b`. D-01 argues a whole-device check is right because "erase on this family is
device-global — there is no region to scope to." That is measured true for the UV family and
**false for protocol `0x06`**, whose `flash_nor_unlock_erase_execute` branches on
`handle->address != 0` into a *sector* erase (`flash_nor_unlock.cpp:118-126`). A whole-device
post-erase check after a sector erase fails by construction. Today the combination is a silent
no-op; after D-01 it becomes an always-failing check with exit code 1.

**Primary recommendation:** sequence as *host gains `erase -b` first (D-01/D-02/D-03 + the `-b`
re-plumb, host-only commit pair) → firmware sweep with all gate re-anchors and the golden re-derive
in the matching commit → native-tree re-keys → catalog annotation (meta-only) → negative-address
firmware fix as its own plan and commit → bench last*, and treat §Gate Impact's measured break
lists as the definition of done rather than re-deriving them during execution.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Pre-write blank refusal | Host / Python | — | Phase 203 already moved it (`write_blank_guard.requires_blank_check`). FWBLANK-01 removes the firmware's duplicate. |
| Post-erase blank verdict | Host / Python | — | D-01. The firmware's `firestarter_operation_end` assignment (FWBLANK-02) is the last tier-misplacement in the milestone, and no earlier phase covered it. |
| Whole-region compare engine | Host / Python | — | Phase 202 (`_drive_region_compare` / `check_eprom_blank`). Unchanged by this phase; D-01 is a **call into it**, not a new path. |
| In-algorithm verify (per-pulse, page read-back, DQ7 poll) | Firmware / AVR | — | D-7 (milestone activation). These are *inside* programming algorithms and cannot move. FWCMD-04/05 pin them. |
| Operation-end resolution (`mem_util_operation_end`) | Firmware / AVR | — | The fail-closed clamp for `region_end`; still called by the write loop and by `eprom_operations.cpp`. **Survives.** |
| Wire control-flag ladder (`0x08`) | **Both**, in lockstep | — | `/workspaces/CLAUDE.md` § Cross-repo obligations: "Change both sides in the same commit pair." |
| Message catalog ids (`MSG_ERR_NOT_BLANK`, `DBG_FLAG_SKIP_BLANK`) | Meta repo (`tools/catalog/messages.toml`) | Both sub-repos consume synced artifacts | D-08 keeps this to a meta-only docs commit — no codegen, no sync. |
| Wire-address sign validation (folded negative-address fix) | **Both**, defence-in-depth | Host already refuses (Phase 203) | The firmware half guards against a non-firestarter host or a corrupted frame. |
| Compatibility-skew evidence (D-07) | Bench (Leonardo + W27C512) | — | No tier below the physical one can answer it. |
| Flash/RAM reclaim number | Build system (`pio run`) | — | No CI leg gates image size; a hand measurement is the only instrument. |

---

## Measured Site Census — 25 in-source sites, not 21

Read line-by-line with `git grep` (not the devcontainer's ugrep-backed `grep`, which honours
`.gitignore`) and `sed -n`/`awk` against the live working trees this session.
`[VERIFIED: firestarter_fw @ 24e3fdf, firestarter_app @ 2a17fd7, read 2026-09-22]`

### Firmware — CONTEXT's rows, verified and corrected

| CONTEXT # | CONTEXT says | Measured | Verdict |
|---|---|---|---|
| 1 | `memory.cpp:434` — `blank_check_saved_address` | `static uint32_t blank_check_saved_address;` at **:434**, with its doc comment at **:422-433** | ✅ correct; delete **:422-434** as a unit |
| 2 | `memory.cpp:439` — `BLANK_CHECK_CHUNK_SIZE` | `#define BLANK_CHECK_CHUNK_SIZE 8192` at **:439**, comment at **:436-438** | ✅ correct; delete **:436-439** |
| 3 | `memory.cpp:440` — `uint32_to_bytes`, orphaned | body **:440-445**; only callers `:511` and `:512`, both inside the `#ifdef RAW_DATA_PROGRESS` branch of the function being deleted; no header declares it; `git grep uint32_to_bytes` returns exactly those three lines repo-wide | ✅ **fully confirmed** |
| 4 | `memory.cpp:467-533` — `mem_util_blank_check_region` | the function is **:467-528**. **:530-534 is the doc comment for `mem_util_blank_check`**, not part of the region form. The region form's own doc comment is **:460-466** | ❌ **WRONG SPAN.** Correct deletion: **:460-528**. A literal 467-533 cut orphans the wrapper's comment and leaves 5 lines of the wrapper |
| 5 | `memory.cpp:535-537` — `mem_util_blank_check` | `:535-537` exactly | ✅ correct; delete **:530-537** with its comment |
| 6 | `memory_utils.h:18`, `:36-40` | `void mem_util_blank_check(...)` at **:18**; region-form comment **:36-39** + declaration **:40** | ✅ exact |
| 7 | `eprom.cpp:52-54` — `CMD_ERASE` arm | `if (!is_flag_set(FLAG_SKIP_BLANK_CHECK)) {` / `handle->firestarter_operation_end = mem_util_blank_check;` / `}` at **:52-54** | ✅ exact |
| 8 | `eprom.cpp:141-143` — write-init region call | **:141-143** exactly, inside `eprom_internal_write_init_body` | ✅ exact |
| 9 | `flash_intel.cpp:91-93` | **:91-93** exactly | ✅ exact |
| 10 | `flash_nor_unlock.cpp:101-103` | **:101-103** exactly | ✅ exact |
| 11 | `flash_nor_unlock.cpp:41` — commented-out assignment | `// handle->firestarter_operation_end = memory_blank_check;` at **:41**. Note the symbol it names, `memory_blank_check`, **already does not exist** — it was renamed to `mem_util_blank_check` long ago, so this is a doubly-dead reference | ✅ correct, with an extra staleness worth stating |
| 12 | `flash_nor_unlock.cpp:73-77` — 2 KB-per-call justification | the comment block is **:71-81**; the `mem_util_blank_check` mention is at **:75**. It is **already factually wrong**: it says "2KB per call" but `BLANK_CHECK_CHUNK_SIZE` is **8192** | ⚠️ span off by two lines, and the guard's status changes — see § Orphaned by the sweep |
| 13 | `firestarter.h:161` — `FLAG_SKIP_BLANK_CHECK` | `#define FLAG_SKIP_BLANK_CHECK 0x08` at **:161**, in the ladder at `:157-167` | ✅ exact |
| 14 | `firestarter.h:62-63` — the stale "leaves in Phase 205" sentence | the sentence begins mid-**:61** ("The region-scoped") and ends at **:64** ("and leaves in Phase 205.") | ⚠️ correct span is **:61-64** |
| 15 | `firestarter.cpp:89` — `DBG_FLAG_SKIP_BLANK` emit | **:89** exactly, inside the `is_memory_cmd` flag dump at `:85-94` | ✅ exact. **But see § Flash and RAM — this site is `SERIAL_DEBUG`-gated and compiles to nothing in all three AVR envs** |
| 16 | `json_parser.c:117-122` — `FIELD_MASK` comment | comment block **:117-126**; the `FLAG_SKIP_BLANK_CHECK` mention is at **:120** | ⚠️ block runs to :126 |
| 17 | `eeprom_28c.cpp:378-383` — anti-regression comment | **:378-383** exactly | ✅ exact |
| 18 | `flash_5v_page.cpp:69-74` — same comment | the comment block is **:71-74**; `:69-70` are the `is_operation_in_progress` guard's closing braces | ⚠️ correct span is **:71-74** |
| 19 | `firestarter_fw/CLAUDE.md:349` — the flag row | **:349** exactly | ✅ but incomplete — see below |
| 20 | `firestarter_fw/PROTOCOLS.md:321` | **:321** exactly. That single (very long) line names both `mem_util_blank_check` and the skip flag, and also asserts "`erase --blank-check` is a documented no-op on this protocol because no post-erase blank check is wired" — **D-01 makes that sentence false**, because the host-side check is protocol-agnostic | ✅ location correct; **the required rewrite is larger than "mentions the flag"** |
| 21 | host: 9 named sites | all 9 verified at the exact lines — `constants.py:129`, `eprom_operations.py:47`+`:314`, `chip_test.py:57`+`:3221`, `serial_comm.py:32`+`:639`, `write_blank_guard.py:46`+`:180` | ✅ exact, but **incomplete** — see below |

### Four in-source sites CONTEXT does not list

| # | Path:line | Verbatim text | Why it is in scope |
|---|---|---|---|
| 22 | `firestarter_fw/src/proms/eprom.cpp:394` | `* shape mem_util_blank_check emits, so 0xE0 keeps exactly one` | Inside the write-loop `MSG_DATA_PROGRESS` rationale. After the sweep 0xE0 has **one** emitter, so this cross-reference dangles. `/workspaces/CLAUDE.md`'s repair-citations rule applies. |
| 23 | `firestarter_fw/CLAUDE.md:165` | `` `mem_util_blank_check` uses. Two boundaries apply: `` | A second `CLAUDE.md` site. The paragraph states 0xE0's payload contract "the same contract `mem_util_blank_check` uses" — the referent disappears. |
| 24 | `firestarter_app/firestarter/eprom_operations.py:452` | `# `FLAG_SKIP_BLANK_CHECK`, erase-exempt, or an unguarded protocol).` | A production comment naming the retired bit. |
| 25 | `firestarter_app/firestarter/chip_test.py:2292` and `:2602` | `witness the `FLAG_SKIP_BLANK_CHECK` pass is derived from…` / `# matters most -- mem_util_blank_check emits MSG_ERR_NOT_BLANK with` | Two production comments; `:2602` also asserts a firmware behaviour that stops existing. |

**Also stale and in scope, discovered while verifying:** `firestarter_app/firestarter/write_blank_guard.py:60-62`
cites `eprom.cpp:144-145`, `flash_nor_unlock.cpp:104-105` and `flash_intel.cpp:94-95`. All three are
**already stale by exactly 3 lines** (Phase 204's deletion shifted them); the live sites are `:141-142`,
`:101-102` and `:91-92`. After this phase they do not exist at all, so the docstring must be rewritten
to the past tense, not merely re-numbered. `[VERIFIED: write_blank_guard.py:58-65 read 2026-09-22]`

### What survives — every survivor's caller set re-verified

CONTEXT is right that these survive. Each caller set below was derived from a whole-repo `git grep`,
so a sweep that over-reaches is detectable:

| Survivor | Defined at | Callers after the sweep | Evidence |
|---|---|---|---|
| `mem_util_operation_end` | `memory.cpp:453-458`, declared `memory_utils.h:35` | **exactly two**: `src/eprom_operations.cpp:85` and `src/proms/eprom.cpp:323` | `git grep mem_util_operation_end` returns 5 source hits; `eprom.cpp:142` is the third and is deleted. CONTEXT correct. ✅ |
| `memory_verify_execute` | `memory.cpp`, declared `memory_utils.h:26` | `eprom.cpp`'s `VERIFY_PER_PULSE_PLUS_FINAL` arm | Pinned by `tests/test_verify_survival_source_contract.py` (Phase 204) — untouched by the sweep, measured green. ✅ |
| `eeprom28c_verify_page_readback` | `eeprom_28c.cpp` (`static`) | driven via `eeprom28c_write_execute` | `test_verify_error_ids` asserts 0xAF. Suite breaks only on an unrelated `FLAG_SKIP_BLANK_CHECK` line (`:185`); its assertions are unaffected. ✅ |
| `flash_util_verify_operation` | `flash_util.cpp` | unchanged | Raises 0xB7, never 0xAF (FWCMD-05). Nothing in this sweep reaches it. ✅ |
| `MSG_ERR_VERIFY` (0xAF) | catalog | unchanged | Not touched. ✅ |
| `is_operation_in_progress` | `operation_utils.h:44` | **five**: `operation_utils.cpp:210`, `:243`; `eprom.cpp:127`; `flash_5v_page.cpp:66`; `flash_nor_unlock.cpp:82` | ✅ survives — but see the next section |
| `region-end` wire key | `json_parser.c` | still live for `CMD_WRITE` via the two `mem_util_operation_end` callers | ✅ |

### Orphaned by the sweep — two symbols CONTEXT says survive, and one guard that goes inert

`[VERIFIED: git grep '\b(set|clear)_operation_in_progress\b' over all tracked files, 2026-09-22 — 4 hits total]`

```
include/operation_utils.h:36:static inline void set_operation_in_progress(firestarter_handle_t* handle) {
include/operation_utils.h:40:static inline void clear_operation_in_progress(firestarter_handle_t* handle) {
src/proms/memory.cpp:469:        set_operation_in_progress(handle);
src/proms/memory.cpp:474:            clear_operation_in_progress(handle);
```

Both call sites are **inside `mem_util_blank_check_region`**. `OPERATION_IN_PROGRESS` (`0x40`) is
set nowhere else in the firmware and nowhere in any test. **CONTEXT's Integration Points claim —
"`is_operation_in_progress` / `set_operation_in_progress` have callers beyond the blank check; they
survive" — is false for `set_` and `clear_`.**

Consequences the planner must decide on explicitly rather than discover:

1. After the sweep, **the blank check was the firmware's only multi-call INIT/END operation.**
   `operation_utils.cpp:210`'s `if (is_operation_in_progress(handle)) return RETURN;` is always
   false, so an INIT or END phase always completes in one pass. `operation_utils.cpp:243`'s
   `if (!is_operation_in_progress(handle)) set_operation_to_done(handle);` is always true.
2. `eprom.cpp:127`, `flash_5v_page.cpp:66` and `flash_nor_unlock.cpp:82` all guard one-time init
   behind that always-true predicate. **`flash_nor_unlock.cpp:71-81`'s comment is the clearest
   statement of why they exist — and its reason disappears with the sweep.** CONTEXT site 12 says
   "The guard is still needed; only its cited justification dies." Measured, the guard is not
   *needed* any more; it is *vestigial-but-harmless*. Keeping it is defensible (defence against a
   future multi-call operation), but the rewritten comment must say that honestly rather than
   restate a live-mechanism claim that is no longer true.
3. **Recommended scope decision:** do **not** extend D-09's sweep into `operation_utils.h`.
   Deleting `set_`/`clear_operation_in_progress` and their three dependent guards changes
   `operation_utils.cpp`'s control flow, which is outside FWBLANK-01…05 and carries real behavioural
   risk for zero flash (they are `static inline` in a header; an uncalled one emits no code and GCC
   does not warn). Record the latency instead, and — if it is wanted gone — file it for a later
   phase. **The measured −518 B already assumes they stay.**

### Firmware documentation

| Path:line | What it says | Disposition |
|---|---|---|
| `firestarter_fw/CLAUDE.md:165` | 0xE0's payload is "the same contract `mem_util_blank_check` uses" | rewrite — referent deleted (site 23) |
| `firestarter_fw/CLAUDE.md:349` | `` - `FLAG_SKIP_BLANK_CHECK (0x08)` — skip the blank check. `` | delete the row, add the reserved note (site 19) |
| `firestarter_fw/PROTOCOLS.md:321` | names the flag, names `mem_util_blank_check`, and asserts `erase --blank-check` is a no-op on `0x0D` | rewrite all three clauses (site 20); D-01 makes the third false |
| `firestarter_fw/CLAUDE.md` (§ What CI runs) | "`tests/` holds a separate Python suite of about 286 tests" | measured **320 collected** today. Minor pre-existing staleness; repair while here |

---

## Flash and RAM — FWBLANK-05's number, measured both sides

### Build configuration, stated rather than assumed

`[VERIFIED: firestarter_fw/platformio.ini read in full 2026-09-22]`

- `default_envs = uno, uno328pb, leonardo`. **`DEV_TOOLS` is NOT set in any of them.**
  `include/firestarter.h:31-32` reads `#ifndef DEV_TOOLS` / `#define DEV_TOOLS 0`, and
  `-D DEV_TOOLS=1` appears only in `[env:native]`. **This contradicts CONTEXT D-10's "`DEV_TOOLS`
  is on by default."** The AVR figures below are release, non-DEV_TOOLS builds.
- `-D SERIAL_DEBUG` is present in `[env] build_flags` but **commented out** (`; -D SERIAL_DEBUG`).
  `include/logging_id.h:307-326` makes every `LOG_DEBUG_ID_SUB*` macro expand to nothing without
  it. **CONTEXT D-10 calls site 15 "`DEV_TOOLS`-gated"; it is `SERIAL_DEBUG`-gated, and that gate
  is off, so `firestarter.cpp:89` contributes 0 bytes to the shipped delta.**
- `SERIAL_ON_IO` is defined for `uno` and `uno328pb` only. **It does not appear in `memory.cpp` or
  `operation_utils.cpp`** — `git grep SERIAL_ON_IO -- src/ include/` returns hits only in
  `rurp_shield.h:62`, `eprom_operations.cpp:106` and `eprom.cpp:305/309/322/402`. **CONTEXT D-10's
  prediction that the per-target deltas "will legitimately differ" because of `SERIAL_ON_IO` is
  therefore wrong for this phase's code, and the measurement below confirms it.**

### Pre-deletion baseline (the before-figure the phase record needs)

`pio run -e uno -e uno328pb -e leonardo` at `firestarter_fw` HEAD `24e3fdf`, after
`pio run -t clean` on each env, reproduced twice with identical output.
`[VERIFIED: executed 2026-09-22]`

| Target | Flash used | of 32768 | % reported | RAM used | of | % |
|---|---|---|---|---|---|---|
| `uno` | **21452** | 32768 | 65.5% | **1398** | 2048 | 68.3% |
| `uno328pb` | **21496** | 32768 | 65.6% | **1404** | 2048 | 68.6% |
| `leonardo` | **23810** | 32768 | 72.7% | **1839** | 2560 | 71.8% |

**Leonardo against its real ceiling (D-10's second constraint):** 23810 / 28672 = **83.04%**,
**4862 B of true margin**. Phase 201's note recorded 24134 B (84.2%, 4538 B margin); Phase 204's
removal freed 324 B between then and now.

**Artifact hashes for the baseline row of the FWBLANK-05 table:**

| Target | `.elf` sha256 | `.hex` sha256 |
|---|---|---|
| `uno` | `046dac09ccd6f2b8ecb7c770f928700d86dde638797aa555a1a87234c587aea0` | `663a65bc0de129e72692af8a063a9f4a7193c3ccae049f0214ccc3a9c0231d1d` |
| `uno328pb` | `d3f9fc5e20ed2fbdd30012986a627007742e715723baad30888804136b628d07` | `e784f2b90f3eb49f41fdf2e6d525cbf49f440706e28dca9793222d12130402c2` |
| `leonardo` | `6d8771d226f8db869d67d272ca5a47c11e177f5fd541558915fd9633e256ac5b` | `8beeb731831d04347c75528bebe2a7cdc04e1eeb1d3da76a3933dc8809ec710b` |

### Measured post-deletion figures — the simulated sweep

Method: `git ls-files` copy of `firestarter_fw` into a scratch tree; the seven source/header edits
of D-09 rows 1-13 applied by exact line range; control copy built unmodified in the same session
with the same toolchain. The control reproduced the real tree's figures **byte for byte**, which is
what makes the delta trustworthy. `[VERIFIED: pio run on both scratch trees 2026-09-22]`

| Target | Flash after | Δ flash | % after | RAM after | Δ RAM |
|---|---|---|---|---|---|
| `uno` | 20934 | **−518 B** | 63.9% | 1394 | **−4 B** |
| `uno328pb` | 20978 | **−518 B** | 64.0% | 1400 | **−4 B** |
| `leonardo` | 23292 | **−518 B** | 71.1% | 1835 | **−4 B** |

- **The delta is identical on all three targets.** The 4 RAM bytes are
  `static uint32_t blank_check_saved_address`.
- Leonardo post-sweep against the real ceiling: 23292 / 28672 = **81.24%**, **5380 B of margin**
  (up from 4862 B).
- **Caveat the planner must carry into the record:** these figures come from a source sweep that
  makes the *code* changes only. The real phase also rewrites comments (sites 12, 14, 16, 17, 18,
  22, 23) and edits `firestarter.cpp:89`. Comments cost no flash and `:89` compiles to nothing
  under the shipped `SERIAL_DEBUG` setting, so the expected final number is **the same −518 B** —
  but the record must quote a `pio run` taken on the *actual* post-phase tree, not this simulation.
- No CI leg gates image size. `scripts/baseline/size_baseline.json` and `check_size_baseline.py`
  are cited by four firmware test modules and **do not exist**. This is a measurement, not an
  enforced pass. `[VERIFIED: ls firestarter_fw/scripts/ 2026-09-22; also recorded in 204-VALIDATION.md]`

---

## Gate Impact — measured against a simulated sweep, not predicted

### Firmware source-scan tree (`firestarter_fw/tests/`) — 7 legs + 1 blob-sha leg

Control vs sweep, same interpreter and flags. Control: `11 failed, 277 passed, 32 skipped`.
Sweep: `18 failed, 270 passed, 32 skipped`. The 11 common failures are non-git-scratch artifacts.
**The delta is 7.** `[VERIFIED: pytest on both scratch trees 2026-09-22]`

| # | Module::leg | Disposition |
|---|---|---|
| G1 | `test_blank_check_region_source_contract.py::test_region_form_is_defined_exactly_once_with_three_parameters` | module retires (see below) |
| G2 | `…::test_the_whole_device_wrapper_is_defined_exactly_once_and_passes_zero_and_device_size` | module retires |
| G3 | `…::test_eprom_cpp_calls_the_region_form_exactly_once_inside_write_init_body` | module retires |
| G4 | `…::test_exactly_one_whole_device_function_pointer_assignment_and_zero_region_form_ones` | module retires |
| G5 | `test_protocol_branch_inventory.py::test_branch_sites_match_the_recorded_inventory` | re-derive the golden (recipe below) |
| G6 | `test_protocol_branch_inventory.py::test_exactly_one_protocol_keyed_site_at_the_pinned_line` | change the pinned literal `[67]` → **`[64]`** |
| G7 | **`test_config_schema_pinned.py::test_the_seven_consumers_call_only_the_public_api`** | **NOT PREDICTED BY CONTEXT** — see below |
| G8 | `test_protocol_branch_inventory.py::test_blob_shas_match_the_recorded_inventory` | not exercisable in a non-git scratch tree, but certain in the real repo: re-record `meta.blob_shas["src/proms/eprom.cpp"]` with `git hash-object` on the working tree **before staging** |

**G7 in full.** `tests/test_config_schema_pinned.py` pins literal line numbers in a tuple:

```python
_C14_CONSUMER_SITES = (
    ("src/firestarter.cpp", 38, "rurp_load_config"),
    ("src/firestarter.cpp", 102, "rurp_get_config"),
    ("src/firestarter.cpp", 108, "rurp_save_config"),
    ...
)
```

Deleting `firestarter.cpp:89` (D-09 site 15) shifts everything below by −1, so `102`→**101** and
`108`→**107**. Site `38` is above the deletion and is unchanged. Measured failure text:
`src/firestarter.cpp:102 does not call rurp_get_config(); observed line: 'int res = json_parse_config(...)'`.
This is the same class of break 204 found and CONTEXT missed: a gate that pins a line number in a
file this phase edits for an unrelated reason.
`[VERIFIED: pytest tests/test_config_schema_pinned.py against the swept tree 2026-09-22]`

**A hole the "retire the module" instruction opens.** `test_blank_check_region_source_contract.py`
has **9 legs**, not 4. Four go red. Of the five that stay green, one is
**`test_operation_end_is_defined_exactly_once_and_reads_both_members` (`:411`)**, which pins
`mem_util_operation_end` — an explicit **survivor**. Retiring the module wholesale, as its own
docstring instructs, **loses the only mechanical fence around `mem_util_operation_end`'s
definition**. Recommended: migrate that leg (plus `test_scan_targets_are_non_vacuous` and
`test_this_module_cannot_be_silently_skipped`, which give it its anti-vacuity properties) into
`tests/test_verify_survival_source_contract.py` — the surviving Phase 204 module whose job is
already "prove the sweep did not over-reach" — in the same commit that deletes this one.

**Two CONTEXT claims about this tree that measurement CONFIRMS:**

- `test_progress_emission_is_leonardo_only.py` stays **green** — all its legs pass against the
  swept tree. Its scan targets are `src/proms/eprom.cpp` and `platformio.ini` only. Its Coverage 6
  prose (`:106` and `:588`) does say 0xE0 has "two emitters (this one and `mem_util_blank_check`'s
  pre-existing one in memory.cpp)", which becomes false; scope any "unchanged" claim to the
  assertions, never to a byte-identical file. ✅ CONTEXT correct.
- The two golden sites at `line: 52` and `line: 141` **do** share an identical
  `(predicate, keyed_on, tier)` signature — both are
  `("if (!is_flag_set(FLAG_SKIP_BLANK_CHECK))", ["ctrl_flags"], "other")`. ✅ CONTEXT correct, and
  positional matching is mandatory.

### The golden re-derive, executed

Run with the gate module's own `_extract_predicates` over the swept `eprom.cpp`:
`[VERIFIED: executed 2026-09-22]`

- `counts`: `total_sites` **22 → 20**, `other_sites` **21 → 19**, `protocol_keyed_sites` **stays 1**
  — exactly as CONTEXT predicts.
- Protocol-keyed site: line **67 → 64** (CONTEXT says it "shifts again" without giving the number).
- New `sites` line list:
  `[45, 63, 64, 95, 124, 126, 130, 131, 149, 238, 248, 266, 415, 510, 547, 552, 582, 585, 586, 601]`
- **Positional alignment verified safe:** removing golden indices for lines 52 and 141, then
  zipping old→live, gives **0 `(predicate, keyed_on, tier)` mismatches across all 20 pairs**. The
  full line map is:

```
45→45  66→63  67→64  98→95  127→124 129→126 133→130 134→131 155→149 244→238
254→248 272→266 421→415 516→510 553→547 558→552 588→582 591→585 592→586 607→601
```

### Firmware native (Unity) tree — 8 suites stop compiling, but not CONTEXT's 8

`pio test -e native` against the swept tree: **8 ERRORED, 12 PASSED**.
`[VERIFIED: executed 2026-09-22]`

| Suite | Breaks? | Why |
|---|---|---|
| `test_eeprom28c_sdp` | **ERRORED** | `:208`, `:232`, `:1151` — `h.ctrl_flags = FLAG_SKIP_BLANK_CHECK …` |
| `test_eprom_params_v131` | **ERRORED** | `:56` |
| `test_flash_intel_vpp` | **ERRORED** | `:82` |
| `test_read_timing` | **ERRORED** | `test_read_timing_params.cpp:245` — and this one **asserts the old behaviour**: `TEST_ASSERT_EQUAL_MESSAGE(0, h.ctrl_flags & FLAG_SKIP_BLANK_CHECK, …)` inside `test_out_of_range_flags_masks_never_sets_every_flag`. Re-key onto a surviving flag, do not just drop the line — the leg exists to prove `FIELD_MASK` does not saturate |
| `test_sdp_harness` | **ERRORED** | `:76`, `:414` |
| `test_val_eprom` | **ERRORED** | `:97`, `:316`, and `:497` `h.firestarter_operation_main = mem_util_blank_check;` |
| `test_val_flash_intel` | **ERRORED** | `:67` |
| **`test_verify_error_ids`** | **ERRORED** | `:185`. **Phase 204's own new suite — not named anywhere in CONTEXT.** Its 0xAF/0xB7/0xBD/0xBE assertions are FWCMD-05's proof and must stay green |
| **`test_val_5v_page`** | **PASSES** | CONTEXT names it as a file that "names `FLAG_SKIP_BLANK_CHECK`" — true, but only in `/* */` comments and `TEST_ASSERT` message strings (`:195-217`, `:798-817`). **No code use, no compile break.** Prose rewrite only |
| `test_val_eprom/host_stubs.cpp:136` | n/a | comment only |
| `test_val_nor_unlock`, `test_val_eeprom28c`, `test_cmd_admission`, `test_val_sram`, `test_dispatch`, `test_not_implemented`, `test_messages`, `test_data_input`, `test_cobs_*`, `test_hv_route_ceiling` | PASS | untouched |

**Exact compile-breaking lines — 12 in 8 files.** `[VERIFIED: git grep, comment/string-filtered, 2026-09-22]`

```
test_eeprom28c_sdp.cpp:208,232,1151   test_eprom_params_v131.cpp:56
test_flash_intel_vpp.cpp:82           test_read_timing_params.cpp:245
test_sdp_harness.cpp:76,414           test_val_eprom.cpp:97,316,497
test_val_flash_intel.cpp:67           test_verify_error_ids.cpp:185
```

**Four native tests in `test_val_eprom.cpp` need a disposition decision, not a re-anchor:**

| Test | Line | Disposition |
|---|---|---|
| `test_blank_check_resumes_across_chunks_and_restores_the_cursor` | `:484-525` | **DELETE.** It is BLANK-02's chunking contract for a function that ceases to exist. |
| `test_erase_end_blank_check_scans_from_zero` | `:544-564` | **DELETE.** It asserts `CMD_ERASE` assigns `firestarter_operation_end` — the exact contract FWBLANK-02 removes. |
| `test_write_init_accepts_blank_region_on_non_blank_part` | `:655-685` | **RE-KEY.** Stays green but becomes vacuous. Re-key it to FWBLANK-01's positive proof: write-init performs **no** blank check at all. |
| `test_write_init_still_refuses_when_target_region_is_non_blank` | `:686-…` | **INVERT or DELETE.** It asserts the refusal FWBLANK-01 removes. Inverting it is criterion 3's native-level counterpart and is the cheaper proof than the bench alone. |

Remove the matching `RUN_TEST(...)` lines at `:736`, `:737`, `:745`, `:746`.

`test_5v_page_write_init_no_blank_check_erase02` (`test_val_5v_page.cpp:789`) and
`test_case30_write_init_no_blank_check_with_flag_clear_erase01` (`test_eeprom28c_sdp.cpp:1319`)
both assert the **absence** of a blank check — they stay green and become the shape every protocol
now has. Their prose names the retired flag and must be rewritten (same treatment as D-09 sites 17
and 18).

### Host app tree — 17 legs across 6 modules, plus a hard collection cliff

**The collection cliff first, because it constrains commit shape.** Deleting
`constants.py:129` *alone* produces **65 collection errors** — `eprom_operations.py:47`,
`serial_comm.py:32`, `chip_test.py:57` and `write_blank_guard.py:46` all import the constant at
module level, and those modules are imported almost everywhere. **The constant, its five
production sites and `tests/fake_chip.py`'s import must move in one commit or the suite cannot
collect at all.** `[VERIFIED: pytest on the constant-only-deleted scratch tree 2026-09-22]`

With the five production sites swept and the constant re-exposed to tests as a research shim, the
real behaviour delta is **17 legs** (an eighteenth, `test_datasheet_overrides.py`, was confirmed to
be a non-git-scratch artifact by reproducing it on an unmodified control):
`[VERIFIED: .venv311 pytest, Python 3.11.16, 2026-09-22 — 18 failed / 2291 passed]`

| Module | Legs | Notes |
|---|---|---|
| **`test_blast_radius_invariance.py`** | **3** | **NOT PREDICTED BY CONTEXT.** `test_dedup_fingerprint_is_frozen[uv-slot-write-pass-927571e5110f]`, `test_schema_bump_rekeys_no_frozen_hash`, `test_build_db_diff_ladder_pin_for_all_shapes[uv-slot-write-pass-expected17]`. The frozen literal re-keys when `chip_test.py:3221` stops setting the bit. The gate's own message is an instruction: *"If deliberate, land the behaviour change and the re-key of this literal as SEPARATE commits, so the re-key stays a reviewable unit."* Budget a dedicated commit. |
| `test_chip_test_uv_slot_write.py` | 4 | `test_uv_slot_write_on_a_non_blank_part_reaches_pass_with_run_count_two`, `test_the_flag_reaches_the_wire_on_every_cycle`, `test_the_blank_check_adjudication_is_what_lifts_the_run_to_pass`, `test_fixed_policy_with_the_witness_sets_the_flag`. Note `:207/:217/:348` assert the literal `chip.write_flags_seen == [8, 8]` / `== [8]` — the bit value itself, not the symbol. |
| `test_cli_handlers.py` | 3 | `test_write_no_blank_check_polarity`, `test_write_b_decouples_skip_erase_phase92`, **`test_erase_blank_check_polarity`** (`:924-943`) — the last is directly in D-01/D-02's blast radius. |
| `test_write_blank_guard_pinning.py` | 4 | `test_requires_blank_check_flag_legs_for_a_flags_zero_guarded_part`, `test_build_op_flags_blank_check_false_sets_only_the_skip_blank_check_bit`, `test_requires_blank_check_skip_erase_rearms_the_guard_on_an_erase_capable_part`, `test_dev_test_uv_write_shortcut_keeps_working_and_the_unmasked_case_is_guarded`. |
| `test_write_blank_guard.py` | 2 | `test_requires_blank_check_false_with_skip_blank_check_flag`, `test_write_with_skip_blank_check_flag_pays_no_guard_read`. |
| `test_eprom_operations.py` | 1 | `test_build_flags_no_blank_check_sets_skip_bit`. |

**`tests/fake_chip.py` is the load-bearing harness.** `:34` imports the constant and `:315` reads
it to decide whether to simulate the firmware refusal. Because D-04 removes the wire bit entirely,
`fake_chip`'s firmware-pre-flight model must be re-keyed (or retired) — it currently models a
firmware that will no longer exist. `:318` and `:340` set
`last_firmware_error_code = MSG_ERR_NOT_BLANK`, which **stays correct** for the pre-205-firmware
skew D-08 preserves.

**Not affected, measured:** `test_devtest_firmware_error_propagation.py` (drives 0xB0 through a
fake operator), `test_dev_test_cmd.py`, `test_erase_flag_invariants.py` (about `FLAG_CAN_ERASE`),
`test_uv_mask.py` and `tests/fixtures/report_shapes.py:653` (prose only). All green.

**Snapshot.** `tests/__snapshots__/test_characterization.ambr::test_help_erase` carries the whole
`erase` docstring *and* the `-b` option help line. D-01, D-02 and D-03 all change it. Hand-edit
with the diff shown; **never `--snapshot-update`.** The current snapshot contains the sentence
*"On protocol `0x0D` the post-erase check is not wired, so `-b` has no effect there"* — which D-01
**makes false**, because the host check is protocol-agnostic.

---

## `firestarter erase -b` — what the host has to gain

### What Phase 202 shipped, verified

`check_eprom_blank` is at `firestarter_app/firestarter/eprom_operations.py:2971-3059`.
`[VERIFIED: read 2026-09-22]`

```python
def check_eprom_blank(
    self, eprom_name: str, eprom_data_dict: dict, operation_flags: int = 0,
    address_str: str | None = None, size_str: str | None = None, full: bool = False,
) -> int:
```

- Returns **0** all-blank, **1** at least one non-blank byte, **2** setup/transport failure or
  refusal. **D-02's contract is already this method's return contract** — no mapping layer needed.
- It opens `COMMAND_READ` through `_operation_context` and drives `_drive_region_compare(...,
  full=full, region_length=...)` against `_blank_expected_bytes`. `full=False` (the default) is
  first-mismatch mode — **D-03's terse behaviour is the existing default parameter**, not new code.
- It carries a pre-wire SRAM/FRAM short-circuit returning **2**. Erase never runs on SRAM, so this
  is inert for D-01 — but note it returns 2, not 1.

`_drive_region_compare` is at **`:2544`**, not `:2230-2334` as CONTEXT states. `write_eprom` is at
`:2248`. `[VERIFIED: git grep 'def …' 2026-09-22]` — CONTEXT's `:2230-2334` citation is wrong.

### The current `erase -b` path, end to end

`[VERIFIED: cli_handlers.py:1191-1262, :326-341, eprom_operations.py:296-334 read 2026-09-22]`

```
erase() @ cli_handlers.py:1224          # decorators from :1191; -b is "blank_check", default=False
  └─ _build_op_flags(blank_check=blank_check, force=force)   @ :326   (keyword-only)
       └─ build_flags(blank_check, force, vpe_as_vpp, verbose, skip_erase=...)  @ eprom_operations.py:296
            └─ if not blank_check: flags |= FLAG_SKIP_BLANK_CHECK      # :313-314
  └─ app.eprom_operator.erase_eprom(..., operation_flags=..., address_str=sector_address)  @ :2832
  └─ sys.exit(0 if ok else 1)                                          # :1262
```

So **plain `erase` SETS `0x08`** (suppressing the firmware's end-op) and **`erase -b` CLEARS it**
(arming it). That is the inversion CONTEXT describes, confirmed. `erase_eprom` (`:2832-2863`)
returns `bool`; D-02 requires the handler to widen to 0/1/2.

### ⚠️ Hazard: `erase -s <sector> -b` on protocol `0x06`

**Measured, and it contradicts D-01's stated reasoning.** D-01 argues whole-device is right because
"erase on this family is device-global — there is no region to scope to." That is true for the UV
family it measured. It is **false for protocol `0x06`**:

```c
void flash_nor_unlock_erase_execute(firestarter_handle_t* handle) {   // flash_nor_unlock.cpp:118
    if (handle->address != 0) {
        LOG_DEBUG_ID_SUB(DBG_SECTOR_ERASE);
        flash_nor_unlock_sector_erase(handle, handle->address);
    } else {
        LOG_DEBUG_ID_SUB(DBG_CHIP_ERASE);
        flash_execute_command(FLASH_ERASE);
    }
}
```

`firestarter erase SST39SF020 -s 0x10000 -b` erases **one sector** and, under an unconditional
whole-device host check, then reports the other 255 KiB as non-blank — a guaranteed false failure,
exit code 1 under D-02. **Today the combination is a silent no-op**, because `0x06`'s erase-end
assignment has been commented out at `flash_nor_unlock.cpp:41` for its whole life. So D-01 would
turn a harmless no-op into a reliable false negative on the one validated `0x06` part in the
registry (`SST39SF020`, `VALIDATED-EPROMS.md:16`).

Three dispositions, for the planner to choose and record:

1. **Refuse `-b` together with `-s`**, with a stated one-line reason. Cheapest, honest, and
   consistent with D-03's terseness. **Recommended.**
2. Scope the check to the erased sector. Blocked in practice: the host does not know the sector
   size — `-s` takes only an address, and no sector-size field is threaded to the CLI.
3. Silently skip the check when `-s` is given. Rejected: it reproduces exactly the
   "silently passes" defect class Phase 201 exists to fix.

### Where D-01 adds a capability CONTEXT does not mention

The same protocol-agnostic property that creates the `0x06` hazard also **closes the `0x0D` gap**:
after D-01 a host-side post-erase check works on AT28C parts, which the firmware never wired.
That is a behaviour *gain*, and it must be reflected in the docstring, the `-b` help line and the
`test_help_erase` snapshot — all three of which currently state the opposite.

### Recommended plumbing shape for `-b` (discretion item)

**Use a keyword-only parameter, following Phase 203's own precedent in this file.**
`write_eprom`'s signature already ends `..., pin1_hazard_acknowledged: bool = False, *,
suppress_verdict_line: bool = False) -> bool` (`:2248-2259`) — Phase 203 added exactly such a
parameter for WRITE-05 and left every existing caller byte-identical. Doing the same for the blank
signal:

- neutralises both hazards CONTEXT names: `build_flags`' four positional callers and
  `chip_test.py:3221`'s positional argument cannot be shifted by a keyword-only insertion;
- leaves the ~40 bool-valued positional test call sites of `write_eprom` untouched;
- keeps `requires_blank_check`'s signature stable if the new parameter is threaded to it as a
  third keyword argument with a `True` default.

`firestarter.cli_handlers` is in the mypy strict island (`disallow_untyped_defs = true`,
`pyproject.toml`), so every new function in `erase()` must carry full annotations.
`firestarter.eprom_operations` is **deliberately excluded** from that island.
`[VERIFIED: firestarter_app/pyproject.toml read 2026-09-22]`

### Session cost D-01 must hand Phase 206

`203-SESSION-COST.md` §2 gives the cited per-open medians (10 samples per board class, port pinned):
**Uno-class 2.518 s, Leonardo-class 2.607 s**, of which 2.500 s is a board-independent structural
floor (`CONNECTION_STABILIZE_DELAY` 2.0 s + `_CONSUME_REMAINING_INPUT_WINDOW_S` 0.5 s). D-01 adds
**exactly one** open to `erase -b`, so the derived added cost is **2.518 s (Uno-class) / 2.607 s
(Leonardo-class)**. Follow 203's discipline: label it a derivation over a cited measurement, never
blend the two board classes, and state that the check's own read traffic is additive to the connect
term. `[CITED: .planning/phases/203-the-write-guard-moves-up-a-layer/203-SESSION-COST.md §1-§3]`

---

## The folded negative-address firmware fix

`[VERIFIED: firestarter_fw/src/json_parser.c read 2026-09-22]`

```c
static unsigned long simple_strtoul(const char* s) {      // :30
    unsigned long val = 0;
    // Note: This simple implementation only handles positive decimal numbers.
    while (*s >= '0' && *s <= '9') { val = val * 10 + (*s - '0'); s++; }
    return val;                                            // "-256" -> 0
}
```

- The host half **already landed in Phase 203**: `write_blank_guard.require_non_negative_address`
  (`:221-259`) raising `NegativeStartAddressError` (`exceptions.py:118`). Only the firmware half
  remains, exactly as CONTEXT says.
- **Scoping decision the planner must make:** `simple_strtoul` has **8 call sites**
  (`json_parser.c:323, 398, 429, 448, 486, 501` plus the two inside `extract_num`), covering
  `ctrl_flags`, bus-config address lines and static-high lines — not just the address. It returns
  `unsigned long` with **no error channel**. A blanket rejection changes behaviour for every
  numeric field on the wire; a field-scoped rejection is narrower but needs a place to put the
  refusal. Decide and record which.
- **Native coverage is reachable.** `json_parser.c` is inside `build_src_filter`
  (`+<json_parser.c>` in `[native_base]`), and `test/native/avr/test_read_timing/test_read_timing_params.cpp`
  already drives `parse_json("{\"cmd\":2,\"flags\":65536}", &h)` and asserts on the resulting
  handle. That is the ready-made home CONTEXT names, confirmed.
- **Bonus alignment:** the same suite is where the not-folded todo
  `2026-09-20-region-end-wire-key-has-no-json-parse-coverage.md` says its ready-to-drop-in
  `region-end` cases would go. Taking them in the same plan is near-free. Permitted, not required.
- **Note for the plan structure:** this plan's own `<verify>` must run `pio test -e native` *and*
  `pio test -e native_nodevtools`, because `json_parser.c` is compiled in both.

---

## Bench — rig state and the minimal honest sequence

**Do not run bench hardware during research.** Nothing below was executed; this is what the plan
should instruct.

### Rig, probed at the port (read-only)

`[VERIFIED: ls /dev/serial/by-id/ 2026-09-22]`

```
usb-Arduino_LLC_Arduino_Leonardo-if00 -> ../../ttyACM0
```

**One board, a Leonardo, on `/dev/ttyACM0`.** No Uno-class device is present — identical to what
Phase 204's D-10 recorded. The Uno-class gap is physically real for this phase too, and
FWBLANK-05's `uno`/`uno328pb` numbers are **build-time measurements, not bench ones** (which is all
the requirement asks for).

### Sequence the plan should instruct

1. **B0 — rig identity.** Confirm the port and the attached board before anything else. The memory
   "verify `controller:` identity per port each task" applies: `ttyACM*` numbering shuffles across
   replug.
2. **B1 — build the pre-205 artifact.** `pio run -e leonardo` at branch HEAD **before** this
   phase's commits, flash it, and **record the commit sha in the phase record**. Per D-07's label
   discipline neither side carries `3.1.0b1`, and `_probe_port`'s `[\d.x]+` regex truncates a
   prerelease suffix, so the sha is the only witness of which firmware was on the board.
3. **B2 — put the W27C512 into a known non-blank state**, using the Phase 201-06 `--skip-erase`
   rehearsal (`.planning/notes/201-region-blank-check-latency-and-divergence.md` §1). Baseline it
   with a whole-device read and a SHA-256, 204's shape.
4. **B3 (D-07 rider) — the skew leg, on the PRE-205 firmware, before reflashing.** Post-205 host,
   `write -b` against the non-blank part: capture the firmware's `Not blank` refusal verbatim, its
   exit code and its duration. This must run *before* B4 because the pre-205 firmware is only on
   the board once.
5. **B4 — flash post-205 firmware.** The Leonardo is exempt from the chip-out-before-sideload rule,
   so no hands are needed.
6. **B5 (criterion 3) — UV leg.** Same non-blank part, `--skip-erase` so the erase cannot mask the
   result: the write must now reach the firmware **unrefused** and program the region it was given.
   Read the region back and compare.
7. **B6 (criterion 5) — erasable leg.** Same part, plain `write` with the erase path on,
   exercising the `FLAG_CAN_ERASE` exemption. Expect no behaviour change.
8. **B7 — `erase -b` on the new host path**, to exercise D-01/D-02 end to end and to take the
   measured extra-open wall-clock D-01 owes Phase 206.
9. **Post-bench:** confirm chip content with a digest before/after where a silent erase would be
   the failure mode, as 204-BENCH-MATRIX did.

### Stated coverage gaps (D-06, to be recorded not hidden)

- **An erasable part stands in for a UV one.** The code path is identical; the silicon is not.
- **`0x10` (`flash_intel.cpp`) cannot be benched at all** — zero validated chips in
  `VALIDATED-EPROMS.md`. Proven by native test and source-contract gate only.
- **`0x06` has exactly one validated part** (`SST39SF020`, `VALIDATED-EPROMS.md:16`) and is not
  seated. The Phase 201 note flags that site as "one flag deep", not safely latent — quote that
  finding in the phase record rather than re-deriving it.
- **Anything requiring an Uno-class board is not reachable** on this rig.

### Operator-gated items to flag in the plan

- `fw --install` flashes the **attached** board and ignores `--board`. The plan must use
  `pio run -e leonardo -t upload`, as 204 did.
- Chip handling, photographs and multimeter readings are operator-only. None of the sequence above
  needs a chip swap: one W27C512 plays every role.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---|---|---|---|
| Post-erase blank comparison | a new read-and-compare loop in `cli_handlers.erase` | `EpromOperator.check_eprom_blank` (`eprom_operations.py:2971`) | Already streaming, already chunk-bounded, already returns D-02's exact 0/1/2, already carries D-03's first-mismatch default. D-01 is a call, not a path. |
| Terse first-mismatch reporting | a bespoke message | `_drive_region_compare(..., full=False)` (`:2544`) | Its default is the terse mode; `--full` is the opt-in. A second renderer would drift from `blank --full`'s output. |
| The refusal sentence | assemble at the raise site | a module-level format constant, as `write_blank_guard._REFUSAL_FORMAT` / `refusal_text` (`:196-213`) does | Lets a test assert the whole sentence instead of a substring of a log line. |
| Re-deriving the branch-inventory golden | hand-editing `protocol_branch_inventory.json` | the gate module's own `_extract_predicates`, matched **positionally** | The golden's own `meta.recorded_by` documents the `(predicate, keyed_on, tier)` dict collision; this phase hits it. |
| A flash/RAM size gate | writing `scripts/baseline/check_size_baseline.py` | `pio run` output, recorded by hand | The script four test modules cite does not exist. FWBLANK-05 asks for a measurement, not a gate. |
| Regenerating `messages.h` / `messages.py` | running codegen in a sub-repo | a comment-only edit to `tools/catalog/messages.toml` in the **meta repo**, per commit `694acce3` | A toml comment does not reach the generated artifacts, so D-08 costs no codegen and no sync. |

---

## Common Pitfalls

### Pitfall 1: the firmware `tests/` tree is RED **today**, for an unrelated reason

`pytest tests/` in `firestarter_fw` **in this devcontainer** reports **17 failed, 303 passed**.
Every failure is `tests/test_flash_path_record_sync.py`, and the cause is:

```
tests.meta_presence.MissingScanTargetError: /workspaces/.planning/v1.23-FLASH-PATH-DECISION.md
does not exist, but the meta repo IS present (marker found at /workspaces/.git).
```

The document moved to `.planning/milestones/v1.23-FLASH-PATH-DECISION.md` under the canonical
`.planning` layout; `tests/test_flash_path_record_sync.py:77, 363, 1092, 1094` still resolve the old
root path. **In CI the gate SKIPS** (no meta-repo marker above a standalone checkout), which is why
`build.yml` is green and the devcontainer is not. Excluding that module, the tree is
**279 passed, 10.7 s**. The planner must either repair the four citations (arguably required by
`/workspaces/CLAUDE.md`'s never-accept-staleness rule) or state the 17 as a known pre-existing
baseline — but a plan whose `<fails_when>` says "the tree is green" is unrunnable as written.
`[VERIFIED: pytest run 2026-09-22]`

### Pitfall 2: deleting `constants.py:129` before its consumers breaks *collection*, not a test

65 modules fail to collect. There is no partial-credit intermediate state. The constant, the five
production sites, `tests/fake_chip.py` and the six test modules move together or the suite cannot
run at all. A plan that splits them across tasks has a commit boundary with no runnable verify.

### Pitfall 3: the frozen `dedup_fingerprint` re-key wants its own commit

`test_blast_radius_invariance.py`'s failure message is an instruction, not a hint: *"If deliberate,
land the behaviour change and the re-key of this literal as SEPARATE commits, so the re-key stays a
reviewable unit."* The measured simulation moved `927571e5110f → eba362ab0a75`, but the final value
depends on exactly how `-b` is re-plumbed — **re-derive it, do not copy my number.**

### Pitfall 4: `memory.cpp`'s deletion is two spans with a survivor between them

`mem_util_operation_end` (`:447-458`, with its doc comment) sits *between* the saved-address/chunk
block (`:422-445`) and the region form (`:460-537`). A single contiguous cut takes a survivor with
it. Delete descending and re-read the file before building.

### Pitfall 5: a source-contract gate that pins a line number in a file you edit incidentally

`test_config_schema_pinned.py` is red purely because `firestarter.cpp:89` goes. No amount of
reading CONTEXT would have predicted it. Assume there are others: after the sweep, run the **whole**
`tests/` tree, not just the modules CONTEXT names.

### Pitfall 6: `test_val_5v_page` looks like it breaks and does not

Grepping for the flag name finds nine hits in that file. All nine are in comments or
`TEST_ASSERT` message strings. The suite **passes** against the swept tree. Conversely
`test_verify_error_ids` breaks and is in no list anywhere.

### Pitfall 7: `grep --no-ignore` silently returns zero matches here

The devcontainer's `grep` is a bash function wrapping ugrep 7.8.4, which rejects `--no-ignore` and
exits with no output and status 0. **Every census command in this document used `git grep`.** Also:
`grep -qF` with a dash-leading pattern exits 2, which makes a gate fail open — use `-qFe`.

### Pitfall 8: run the host suite on 3.11, and unset the doubled `-q`

`firestarter_app/.venv311/bin/python` resolves to **Python 3.11.16** and works today
(204's finding that it was a dangling symlink no longer holds). `addopts = -ra -q`, so a bare `-q`
hides the count line — pass `-o addopts=""`.

### Pitfall 9: a pre-authored gate leg can be unreachable

RED proves nothing until it is *seen* to fail for the intended reason. Every new absence leg in
this phase must be run against the pre-sweep tree and observed red before the sweep lands.

### Pitfall 10: pushing to `beta` publishes

Both sub-repos are on `v1.41-verification-to-host`. A push to `beta` in `firestarter_app` uploads
to PyPI and a PyPI version can never be reused; a push to `beta` in `firestarter_fw` cuts a
pre-release. Neither carries a path filter.

---

## Code Examples

### The reserved-gap comment shape, from the live ordinal-4 record

```c
// Source: firestarter_fw/include/firestarter.h:53-64 (Phase 204's executed shape)
// Ordinal 4 -- the standalone blank-check command -- retired in 3.1.0
// (Phase 204). The host side -- firestarter_app/firestarter/constants.py's
// COMMAND_BLANK_CHECK and its COMMAND_NAMES row -- was retired in the same
// commit pair. This ordinal must NEVER be reused for any new command, flag
// or reserved meaning: an already-shipped host still composes it, and
// reassigning the number would make that stale host silently drive a
// different operation. ...
// The region-scoped blank-check machinery itself (mem_util_blank_check,
// mem_util_blank_check_region) survives this retirement -- it is reached
// only from write-init and erase-end now, and leaves in Phase 205.   <-- :61-64, DELETE
```

D-05's `0x08` note goes in the control-flag ladder at `firestarter.h:157-167` and mirrors this
shape: version retired in, why it must never be reused (a shipped host still composes it and would
silently turn on a different behaviour), and the host counterpart named.

### The golden re-derive, executed form

```bash
# Source: tests/golden/protocol_branch_inventory.json meta.how_to_update (house shape)
# Run from firestarter_fw/ with the SWEPT working tree in place, BEFORE staging.
python3 - <<'PY'
import json, pathlib, importlib.util
spec = importlib.util.spec_from_file_location("pbi", "tests/test_protocol_branch_inventory.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
g = json.load(open("tests/golden/protocol_branch_inventory.json"))
old  = [s for s in g["sites"] if s["line"] not in (52, 141)]   # the two deleted sites
live = m._extract_predicates(pathlib.Path("src/proms/eprom.cpp").read_text())
assert len(old) == len(live)
# Prove positional alignment is SAFE before using it (the golden's own instruction):
for o, l in zip(old, live):
    assert (o["predicate"], tuple(o.get("keyed_on") or []), o["tier"]) == \
           (l["predicate"], tuple(l.get("keyed_on") or []), l["tier"]), (o, l)
# Only then carry class/reason forward and write the new `line` values.
PY
git hash-object src/proms/eprom.cpp   # -> meta.blob_shas["src/proms/eprom.cpp"]
```

Executed this session against the swept tree: **0 mismatches across all 20 pairs.**

### The flash/RAM measurement command and what to record

```bash
# Source: .planning/milestones/v1.33-artifacts/sweep-outcome-record.md (executed template)
cd firestarter_fw
pio run -e uno -t clean && pio run -e uno328pb -t clean && pio run -e leonardo -t clean
pio run -e uno -e uno328pb -e leonardo 2>&1 | grep -E '^Processing|^RAM:|^Flash:'
for e in uno uno328pb leonardo; do
  for x in elf hex; do
    printf '%s %s %s\n' "$e" "$x" "$(sha256sum .pio/build/$e/firestarter_$e.$x | cut -d' ' -f1)"
  done
done
# Record BOTH leonardo denominators: x/32768 (what pio reports) and x/28672 (the real
# ATmega32U4-on-Caterina ceiling), with the margin in bytes. platformio.ini overrides
# board_upload.maximum_size to 32768 and its own comment states the linker no longer
# protects the top 4096 B.
```

### The keyword-only plumbing precedent already in the file

```python
# Source: firestarter_app/firestarter/eprom_operations.py:2248-2259 (Phase 203's executed shape)
def write_eprom(
    self, eprom_name: str, eprom_data_dict: dict, input_file_path: str,
    operation_flags: int = 0, address_str: str | None = None, pulse_us: int = 0,
    pin1_hazard_acknowledged: bool = False,
    *,
    suppress_verdict_line: bool = False,   # <- keyword-only; every existing caller unchanged
) -> bool:
```

---

## Runtime State Inventory

This phase is a removal plus a small host addition, not a rename — but the sweep does touch a wire
contract, so the categories are answered explicitly rather than skipped.

| Category | Items Found | Action Required |
|---|---|---|
| Stored data | **None.** `0x08` is composed per-command on the wire and is never persisted. `~/.firestarter/config.json` and `database.json` carry no flag bitmask. Verified by `git grep FLAG_SKIP_BLANK_CHECK` across `firestarter_app/firestarter/` — all five sites are compose-or-read-at-call-time. | none |
| Live service config | **None.** No n8n workflow, dashboard or external service references the blank-check flag or the deleted symbols. | none |
| OS-registered state | **None.** No scheduler task, systemd unit or pm2 process references them. | none |
| Secrets / env vars | **None.** No env var names the flag. | none |
| Build artifacts / installed firmware | **Yes — the flashed firmware on the bench board is the artifact that carries the old behaviour.** A post-205 host driving a board still running pre-205 firmware is precisely D-04's accepted skew and D-07's bench leg. Also: `.pio/build/*` is stale after the sweep — the FWBLANK-05 figures must come from a clean rebuild, not a cached one. | reflash for B4+; `pio run -t clean` before the after-figures |
| **Published artifacts (extra category, worth stating)** | The `firestarter==3.0.0b49` wheel on PyPI and the `3.0.0b34` firmware pre-release both still compose/read `0x08`. Neither can be changed. | REL-04 (Phase 207) documents the skew; this phase files the obligation |

---

## Environment Availability

`[VERIFIED: probed 2026-09-22]`

| Dependency | Required By | Available | Version | Fallback |
|---|---|---|---|---|
| PlatformIO Core | firmware build + native tests | ✓ | 6.2.0 (`/usr/local/bin/pio`) | — |
| `toolchain-atmelavr` | AVR builds | ✓ | 1.70300.191015 (gcc 7.3.0) | — |
| `framework-arduino-avr` | leonardo/uno | ✓ | 5.3.0 / MiniCore 3.1.2 | — |
| Python (devcontainer default) | firmware `tests/` tree | ✓ | 3.12.14 | — |
| `pytest` for the firmware tree | `pytest tests/` | ✓ | `/usr/local/py-utils/bin/pytest` 9.1.1 | a bare `python3 -m pytest` fails — module not found |
| Python 3.11 + app venv | host suite (CI is 3.11-only) | ✓ | `firestarter_app/.venv311` → 3.11.16 | `uv python install 3.11` with `UV_CACHE_DIR` redirected |
| Arduino Leonardo on `/dev/ttyACM0` | criteria 3 and 5 bench legs | ✓ | `usb-Arduino_LLC_Arduino_Leonardo-if00` | none — bench legs are unreachable without it |
| Uno-class board | none (FWBLANK-05 is a build measurement) | ✗ | — | build-time figures suffice; no criterion needs Uno silicon |
| `scripts/baseline/check_size_baseline.py` | an automated size gate | ✗ | — | measure by hand (this is what FWBLANK-05 asks for) |
| W27C512 part, seated | criteria 3 and 5 | **unconfirmed by research** | — | operator must confirm before the bench plan runs |

**Missing dependencies with no fallback:** none blocking. The seated-part question is an operator
confirmation, not an install.

---

## Package Legitimacy Audit

**This phase installs no external packages.** It deletes firmware code, retires a wire flag bit,
and adds host code composed entirely of existing in-repo modules (`check_eprom_blank`,
`_drive_region_compare`, `write_blank_guard`). No `npm install`, `pip install` or `lib_deps` change
appears anywhere in its scope.

| Package | Registry | Verdict | Disposition |
|---|---|---|---|
| *(none)* | — | — | — |

**Packages removed due to [SLOP] verdict:** none.
**Packages flagged as suspicious [SUS]:** none.

If a plan ends up adding a dependency (it should not), run
`gsd-tools query package-legitimacy check --ecosystem pypi <pkg>` before the install task and gate
it behind a `checkpoint:human-verify`.

---

## Validation Architecture

### Test Framework

Three trees, three frameworks. `firestarter_fw` has two python-visible suites; the host app is the
third. A task that edits firmware source must satisfy both firmware columns; a task that edits the
host app must satisfy the host column. **All runtimes below are measured this session, not
estimated.**

| Property | Firmware — native (tree 1) | Firmware — source-scan (tree 2) | Host app (tree 3) |
|---|---|---|---|
| **Framework** | PlatformIO 6.2.0 + Unity, `platform = native`, ArduinoFake 0.4.0 | pytest 9.1.1, stdlib-only, **no `conftest.py`** (house rule), Python 3.12.14 | pytest + syrupy snapshots, `conftest.py`, `addopts = -ra -q`, **Python 3.11.16** |
| **Config file** | `firestarter_fw/platformio.ini` — `[native_base]` holds the single `test_filter` and `-I` list (20 entries each) | none | `firestarter_app/pyproject.toml` |
| **Runner path** | `pio` on `PATH` | **`/usr/local/py-utils/bin/pytest`** (a bare `python3 -m pytest` fails) | **`/workspaces/firestarter_app/.venv311/bin/python -m pytest`** |
| **Quick run command** | `pio test -e native -f "*<touched suite>*"` | `/usr/local/py-utils/bin/pytest tests/<module> -o addopts="" -p no:cacheprovider -q` | `.venv311/bin/python -m pytest tests/<module> -o addopts="" -p no:cacheprovider -q` |
| **Full suite command** | `pio test -e native` **and** `pio test -e native_nodevtools` | `/usr/local/py-utils/bin/pytest tests/ -v` | `.venv311/bin/python -m pytest tests/ -o addopts="" -q` |
| **Measured full runtime** | **31.3 s** (`native`) / **40.3 s** (`native_nodevtools`) | **11.6 s** (320 collected) | **180.6 s** (3 m 01 s) |
| **Measured per-suite runtime** | 0.6 s – 4.7 s (median ~2.0 s) | ~0.1 s – 1 s per module | ~1 s – 20 s per module |

### Measured baselines — unmodified trees, 2026-09-22

`firestarter_fw` HEAD `24e3fdf`, `firestarter_app` HEAD `2a17fd7`, both clean.

| Leg | Result | Note |
|---|---|---|
| `pio test -e native` | **20 suites, 243 cases, 243 succeeded, 31.3 s, exit 0** | green |
| `pio test -e native_nodevtools` | **243 cases, 243 succeeded, 40.3 s, exit 0** | green |
| `pytest tests/` (firmware) | **17 failed, 303 passed, 11.6 s** | ⚠️ **17 PRE-EXISTING RED**, all `test_flash_path_record_sync.py`, cause in § Pitfall 1. **Not caused by this phase.** |
| `pytest tests/ --ignore=tests/test_flash_path_record_sync.py` | **279 passed, 10.7 s, exit 0** | the usable green baseline for tree 2 |
| host `pytest tests/` on 3.11 | **2309 passed, 0 failed, 36 snapshots passed, 180.6 s, exit 0** | green **with `/dev/ttyACM0` attached** — the recorded `test_no_programmer_found_*` trap did **not** fire; those two cases live in `test_characterization.py` and pass today |
| `pio run -e uno -e uno328pb -e leonardo` | 3 succeeded | figures in § Flash and RAM |

**The firmware phase gate is `build.yml`'s four steps, in order:** `pio test -e native`
(**pull requests only** — a branch push skips it), `pio test -e native_nodevtools` (always),
`pytest tests/ -v`, `pio run`. **The host phase gate is `ci.yml`'s four steps:**
`ruff check firestarter/ tests/`, `ruff format --check firestarter/ tests/`,
`pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70`, and a
`pip install -e .` + `firestarter --help` smoke test. **`mypy` is not a host CI gate** — it runs
only in pre-commit — but `firestarter.cli_handlers` is in the strict island, so D-01's new code
must be fully annotated or pre-commit blocks the commit. `ruff`'s selection is `E,F,I,UP` with
`E501` ignored; a `# noqa` outside that set is inert.

### Phase Requirements → Test Map

| Req | Behavior | Test Type | Automated Command | File Exists? |
|---|---|---|---|---|
| FWBLANK-01 | no write-init blank check remains in `eprom.cpp`, `flash_intel.cpp`, `flash_nor_unlock.cpp` | source-scan (absence leg) + native | `/usr/local/py-utils/bin/pytest tests/test_verify_survival_source_contract.py -o addopts="" -p no:cacheprovider -v`; `pio test -e native -f "*test_val_eprom*"` | ❌ new absence legs — **Wave 0** |
| FWBLANK-01 | a non-blank UV part accepts a write at firmware level | unit (native), **inverted from the existing leg** | `pio test -e native -f "*test_val_eprom*" -v` | ✅ `test_write_init_still_refuses_when_target_region_is_non_blank` exists and must be inverted |
| FWBLANK-02 | `configure_eprom`'s `CMD_ERASE` arm assigns no `firestarter_operation_end` | unit (native) | `pio test -e native -f "*test_val_eprom*" -v` | ✅ `test_erase_end_blank_check_scans_from_zero` exists and must be **deleted**, replaced by its negation |
| FWBLANK-03 | the four symbols are gone and no caller remains; **and the sweep did not take `mem_util_operation_end`** | source-scan | the migrated survivor leg (see § Gate Impact) + a four-symbol absence probe | ❌ **Wave 0** — migrate `test_operation_end_is_defined_exactly_once_and_reads_both_members` out of the retiring module |
| FWBLANK-04 | `FLAG_SKIP_BLANK_CHECK` absent from `firestarter.h` and `constants.py`; `0x08` recorded reserved on both sides | source-scan (firmware) + unit (host) | firmware absence probe; `.venv311/bin/python -m pytest tests/test_write_blank_guard_pinning.py -o addopts="" -q` | ❌ **Wave 0** (firmware side) / ✅ (host module exists, legs re-anchor) |
| FWBLANK-04 | `-b` still reaches the Phase 203 guard without a wire bit | unit (host) | `.venv311/bin/python -m pytest tests/test_write_blank_guard.py tests/test_write_blank_guard_pinning.py tests/test_cli_handlers.py -o addopts="" -q` | ✅ re-anchor |
| FWBLANK-05 | flash and RAM measured per AVR target | build measurement | `pio run -e uno -e uno328pb -e leonardo` + the sha256 loop in § Code Examples | n/a — produces the phase record's table |
| D-01/D-02/D-03 | `erase -b` runs a host post-erase check; exit 0/1/2; one terse line; no `--full` | unit + snapshot (host) | `.venv311/bin/python -m pytest tests/test_cli_handlers.py tests/test_characterization.py -o addopts="" -q` | ❌ new legs — **Wave 0**; the `test_help_erase` snapshot is hand-edited |
| D-01 hazard | `erase -s … -b` does not produce a false non-blank verdict | unit (host) | `.venv311/bin/python -m pytest tests/test_cli_handlers.py -k erase -o addopts="" -q` | ❌ new leg — **Wave 0** |
| D-08 | catalog annotations land with byte-identical codegen output | codegen diff (meta) | `python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check` + two `diff -u` regenerations | ✅ (204's executed shape) |
| Folded negative-address | firmware refuses a negative wire address instead of clamping to 0 | unit (native) | `pio test -e native -f "*test_read_timing*" -v` **and** the same under `native_nodevtools` | ❌ new cases in an existing suite — **Wave 0** |
| criterion 3 / 5 / D-07 | silicon behaviour | **bench (automated under standing permission)** | `pio run -e leonardo -t upload`; `timeout 300 .venv311/bin/firestarter …`; digest compares | ❌ produces `205-BENCH-MATRIX.md` |

### Sampling Rate

- **After every task commit:**
  - firmware-touching task → `/usr/local/py-utils/bin/pytest tests/ -o addopts="" -p no:cacheprovider -q --ignore=tests/test_flash_path_record_sync.py` (**~11 s**) plus
    `pio test -e native -f "*<touched suite>*"` (**~2 s**)
  - host-touching task → `.venv311/bin/python -m pytest tests/<touched modules> -o addopts="" -q` (**~1-20 s**)
- **After every plan wave:** all four firmware `build.yml` legs in order (**~85 s**), plus the full
  host suite on 3.11 (**~181 s**), plus `ruff check` and `ruff format --check`.
- **Before `/gsd-verify-work`:** all four firmware legs green, host suite green on 3.11, the
  FWBLANK-05 table filled from a clean `pio run`, and the bench matrix recorded.
- **Max feedback latency:** ~11 s (firmware source-scan) / ~2 s (a filtered native suite). The only
  legs above 60 s are the full native runs and the host suite, both run at wave boundaries.

### Wave 0 Gaps

- [ ] **Repair or ring-fence `tests/test_flash_path_record_sync.py`** (`:77`, `:363`, `:1092`,
      `:1094`) so tree 2 has a reachable green. Four string literals, `.planning/` →
      `.planning/milestones/`. **Owner: first firmware task.** Without this, every firmware
      `<fails_when>` that says "the tree is green" is false at the start.
- [ ] **Migrate the `mem_util_operation_end` survivor leg** out of
      `tests/test_blank_check_region_source_contract.py` before retiring that module — plus
      `test_scan_targets_are_non_vacuous` and `test_this_module_cannot_be_silently_skipped`, which
      give it its anti-vacuity guarantees. Destination:
      `tests/test_verify_survival_source_contract.py`. **Same commit as the deletion.**
- [ ] **FWBLANK-01/02/03/04 absence legs in `tests/test_verify_survival_source_contract.py`** — each
      seen RED against the pre-sweep tree before the sweep lands.
- [ ] **Host legs for D-01/D-02/D-03** in `tests/test_cli_handlers.py`: the 0/1/2 exit mapping, the
      terse single-line refusal, the absence of `--full` on `erase`, and the `-s` + `-b` hazard
      disposition.
- [ ] **`tests/fake_chip.py` re-key** (`:34`, `:315`): it models a firmware pre-flight that will not
      exist. Decide whether it models pre-205 firmware (keep, rename to say so) or is retired.
      `:318`/`:340`'s `MSG_ERR_NOT_BLANK` assignments stay correct either way.
- [ ] **Native suite re-keys — 12 lines in 8 files** (list in § Gate Impact), split so every commit
      boundary is green: `test_read_timing_params.cpp:245` re-keyed onto a surviving flag;
      `test_val_eprom.cpp`'s two deletions and two re-keys with their `RUN_TEST` lines;
      `test_verify_error_ids.cpp:185`, `test_eeprom28c_sdp.cpp` ×3, `test_sdp_harness.cpp` ×2,
      `test_eprom_params_v131.cpp`, `test_flash_intel_vpp.cpp`, `test_val_flash_intel.cpp`.
- [ ] **Gate re-anchors:** `test_config_schema_pinned.py` `_C14_CONSUMER_SITES` 102→101, 108→107;
      `test_protocol_branch_inventory.py` `[67]`→`[64]`; the golden re-derive and
      `meta.blob_shas["src/proms/eprom.cpp"]` — **all three in the ONE commit that carries the
      `eprom.cpp`/`firestarter.cpp` edits**.
- [ ] **The frozen-hash re-key in `test_blast_radius_invariance.py` as its own commit**, per the
      gate's own instruction.
- [ ] **Negative-address native cases** in `test/native/avr/test_read_timing/`, run under both
      native envs.
- [ ] No new PlatformIO suite directory is needed — the folded fix reuses `test_read_timing`, so
      `[native_base]`'s `test_filter` and `-I` lists do **not** change.

### Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|---|---|---|---|
| A write to a non-blank UV part reaches the firmware unrefused and programs the region it was given | criterion 3 | the outcome is a property of silicon; `firestarter.cpp` and `eprom_operations.cpp` are outside `build_src_filter`, so no native test links the dispatch path | bench B5, per § Bench |
| No behaviour change across one UV part and one erasable part other than where the refusal comes from | criterion 5 | same | bench B6 |
| The D-04 skew: pre-205 firmware refuses `write -b` from a post-205 host | D-04 / D-07 | needs two real firmware artifacts on real hardware | bench B3, **before** reflashing |
| `erase -b` added wall-clock | D-01 / Phase 206 SESS-01 | a real port open on a real board | bench B7, or `tests/test_connect_cost_harness.py` if a derivation is accepted |
| Flash/RAM reclaim | FWBLANK-05 | `scripts/baseline/check_size_baseline.py` does not exist; no CI leg gates image size | `pio run` before and after, by hand |

**Bench rig:** `/dev/ttyACM0` = `usb-Arduino_LLC_Arduino_Leonardo-if00`, the only serial device
present. The Uno-class gap is physically real and does not block any criterion.

---

## Security Domain

`security_enforcement` is not set to `false` in `.planning/config.json`, so this section is
included. The domain is an embedded serial protocol with a trusted local operator; most ASVS
categories do not apply.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---|---|---|
| V2 Authentication | no | no remote surface; a local USB serial link with a physically present operator |
| V3 Session Management | no | no sessions; one command per port open |
| V4 Access Control | **partly** | `is_memory_cmd` is the firmware's admission gate. This phase does **not** touch it — but it removes a *safety* pre-flight, which is why the ordering property (host gains before firmware loses) is a locked decision rather than a preference |
| V5 Input Validation | **yes** | `json_parser.c`'s `FIELD`/`FIELD_MASK` table, clamps at parse time. The folded negative-address fix is squarely here: `simple_strtoul` currently makes `-256` indistinguishable from `0` on the wire — a **fail-open** in a fail-closed parser |
| V6 Cryptography | no | none present; CRC8 is integrity, not security |
| V7 Error Handling / Logging | **yes** | D-02's 0/1/2 contract exists so a transport failure cannot masquerade as a chip verdict — the defect shape already filed against `dev test`'s blank step |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---|---|---|
| A safety check removed from one tier before the other tier gains it | Tampering / Denial of Service (device) | the roadmap's ordering rule; D-01 applies it to the one check no earlier phase covered |
| A silently-passing blank check (fail-open) | Spoofing (of a verdict) | this is the defect class Phase 201 exists to fix; the folded `start > end` todo is closed by deleting the split, not by patching it |
| A negative wire address clamping to 0 | Tampering (wrong destination) | the folded firmware-half fix; host half already landed in Phase 203 |
| Version skew: a new host driving old firmware | Denial of Service (usability) | D-04 accepts it knowingly and D-07 observes it on silicon; REL-04 documents it. A version gate was considered and ruled out of scope by activation decision D-4 |
| A whole-device check after a sector erase reporting a false failure | Spoofing (of a verdict) | the `erase -s … -b` hazard above — must be disposed of explicitly, not left to emerge |
| A retired flag bit reused later, silently changing a shipped host's behaviour | Tampering | D-05's reserved-gap comments in both ladders |

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|---|---|---|---|
| Firmware performs a whole-device blank check at write-init | Host reads the target region and refuses before the write (`write_blank_guard`) | Phase 203 (v1.41) | FWBLANK-01 removes the now-duplicate firmware half |
| Firmware performs a post-erase blank check as `firestarter_operation_end` | **Nothing yet** — this is the gap D-01 fills host-side | this phase | the one check no earlier phase covered |
| `blank` / `verify` as wire ordinals 4 and 6 | host-side streaming compare (`check_eprom_blank`, `verify_eprom`) | Phase 202, ordinals retired Phase 204 | `check_eprom_blank` is the engine D-01 reuses |
| `FLAG_SKIP_BLANK_CHECK` as the wire bypass for the firmware pre-flight | an explicit host-side signal to `requires_blank_check` | this phase (D-04) | the wire bit is retired entirely |
| A `malloc`'d 4-byte saved address in the blank check | a file-scope `static uint32_t` | pre-v1.41 | goes with the machinery; the 586 B allocator it once pulled in is already gone |

**Deprecated / already retired:**
- The no-comments-in-source rule — **removed by operator decision 2026-09-19.** Several decisions in
  this phase require comments in product source.
- `memory_blank_check` (the pre-rename symbol name) — still cited in a commented-out line at
  `flash_nor_unlock.cpp:41`.
- `scripts/baseline/size_baseline.json` and `check_size_baseline.py` — cited by four firmware test
  modules, never existed.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|---|---|---|
| A1 | The final post-phase flash figure will be the same −518 B as the simulation, because the remaining edits are comments plus a `SERIAL_DEBUG`-gated line | Flash and RAM | Low. The record must quote a real post-phase `pio run` anyway; if it differs, the real number is the one that counts |
| A2 | A W27C512 is seated on the bench rig and is the part criteria 3 and 5 will use | Bench | Medium — blocks the bench plan. **Needs operator confirmation before the bench plan is written.** Research did not touch hardware |
| A3 | `test_flash_path_record_sync.py` skips in CI (no meta-repo marker above a standalone checkout), which is why `build.yml` is green while the devcontainer is red | Pitfall 1 | Low. The skip logic was read; the CI run was not observed this session |
| A4 | Keeping `set_`/`clear_operation_in_progress` costs zero flash because they are uncalled `static inline` functions in a header | Orphaned by the sweep | Low — the measured −518 B was taken with them kept, so the number stands regardless |
| A5 | The new `dedup_fingerprint` value after the real re-plumb is not `eba362ab0a75` | Gate Impact | Low — flagged explicitly; the planner must re-derive it |
| A6 | Refusing `-b` together with `-s` is the right disposition for the `0x06` hazard | `erase -b` | Medium. This is a user-facing behaviour choice. Three options are laid out; the operator may prefer another |
| A7 | `firestarter.wiki/` (untracked in the meta repo) is not in this phase's scope — REL-04 is Phase 207's | scope | Low; CONTEXT states it |

---

## Open Questions

1. **How should `erase -s … -b` behave?**
   - What we know: a whole-device check after a sector erase fails by construction; today the
     combination is a silent no-op; the host has no sector-size knowledge.
   - What's unclear: which of refuse / scope / skip the operator wants.
   - Recommendation: **refuse `-b` together with `-s`** with one stated line, and record the choice
     in the phase record. Raise it at plan time; it is a user-facing contract change.

2. **Does `test_blank_check_region_source_contract.py` retire wholesale, or is it trimmed?**
   - What we know: its own docstring says it retires in Phase 205; 4 of its 9 legs go red; one
     surviving leg is the only mechanical fence around `mem_util_operation_end`.
   - Recommendation: retire the module **and** migrate the survivor leg plus its two anti-vacuity
     legs into `test_verify_survival_source_contract.py`, in the same commit. Do not simply delete.

3. **How wide is the negative-address firmware refusal?**
   - What we know: `simple_strtoul` has 8 call sites covering `ctrl_flags` and bus config, and no
     error channel.
   - Recommendation: scope the refusal to the address field rather than every numeric field, and
     state the scope in the plan. A blanket change is a wire-behaviour change for six other fields.

4. **Do `set_`/`clear_operation_in_progress` and the three now-inert guards go in this phase?**
   - What we know: they are orphaned by the sweep, cost zero flash, and their removal changes
     `operation_utils.cpp`'s control flow.
   - Recommendation: **no.** Record the latency, rewrite the guards' comments honestly, and file the
     removal for a later phase. Deleting them is outside FWBLANK-01…05 and carries behavioural risk
     for no measurable gain.

5. **Is the 17-failure firmware `tests/` baseline repaired here or ring-fenced?**
   - Recommendation: repair it — four string literals — under `/workspaces/CLAUDE.md`'s
     never-accept-staleness rule. It is cheap, and without it no firmware task can honestly assert
     a green tree.

---

## Sources

### Primary (HIGH confidence) — the live trees, read this session

- `firestarter_fw` @ `24e3fdf` (`v1.41-verification-to-host`): `src/proms/memory.cpp`,
  `src/proms/eprom.cpp`, `src/proms/flash_intel.cpp`, `src/proms/flash_nor_unlock.cpp`,
  `src/proms/flash_5v_page.cpp`, `src/proms/eeprom_28c.cpp`, `src/firestarter.cpp`,
  `src/operation_utils.cpp`, `src/json_parser.c`, `include/memory_utils.h`, `include/firestarter.h`,
  `include/operation_utils.h`, `include/logging_id.h`, `platformio.ini`, `CLAUDE.md`, `PROTOCOLS.md`
- `firestarter_fw/tests/`: `test_blank_check_region_source_contract.py`,
  `test_protocol_branch_inventory.py` + `golden/protocol_branch_inventory.json`,
  `test_config_schema_pinned.py`, `test_progress_emission_is_leonardo_only.py`,
  `test_flash_path_record_sync.py`, `meta_presence.py`
- `firestarter_fw/test/native/avr/`: `test_val_eprom/`, `test_val_5v_page/`, `test_read_timing/`,
  `test_eeprom28c_sdp/`, `test_sdp_harness/`, `test_verify_error_ids/`, `test_flash_intel_vpp/`,
  `test_eprom_params_v131/`, `test_val_flash_intel/`
- `firestarter_app` @ `2a17fd7`: `firestarter/cli_handlers.py`, `firestarter/eprom_operations.py`,
  `firestarter/constants.py`, `firestarter/write_blank_guard.py`, `firestarter/serial_comm.py`,
  `firestarter/chip_test.py`, `firestarter/exceptions.py`, `pyproject.toml`, `CLAUDE.md`
- `firestarter_app/tests/`: `fake_chip.py`, `test_blast_radius_invariance.py`,
  `test_chip_test_uv_slot_write.py`, `test_cli_handlers.py`, `test_write_blank_guard.py`,
  `test_write_blank_guard_pinning.py`, `test_eprom_operations.py`,
  `test_devtest_firmware_error_propagation.py`, `__snapshots__/test_characterization.ambr`
- meta: `/workspaces/CLAUDE.md`, `tools/catalog/messages.toml`, `VALIDATED-EPROMS.md`,
  `.planning/REQUIREMENTS.md`

### Primary (HIGH confidence) — executed this session

- `pio run -e uno -e uno328pb -e leonardo` on the real tree and on two scratch trees (control and
  swept), after `pio run -t clean`
- `pio test -e native` and `pio test -e native_nodevtools` on the real tree; `pio test -e native` on
  the swept tree
- `pytest tests/` on the real firmware tree and on both scratch trees
- `.venv311/bin/python -m pytest tests/` on the real app tree and on two app scratch trees
- `test_protocol_branch_inventory.py::_extract_predicates` run directly against the swept
  `eprom.cpp`, with a positional field-by-field alignment check
- `git grep` censuses over both sub-repos
- `ls /dev/serial/by-id/` (read-only port probe; no board was driven)

### Secondary (MEDIUM confidence)

- `.planning/phases/204-the-command-surfaces-leave-the-firmware/204-RESEARCH.md`,
  `204-VALIDATION.md` — the structural precedent and the command shapes
- `.planning/phases/203-the-write-guard-moves-up-a-layer/203-SESSION-COST.md` — the cited per-open
  medians (measured 2026-09-04, not re-measured here)
- `.planning/notes/201-region-blank-check-latency-and-divergence.md` §1 and §3 — the `--skip-erase`
  rehearsal and the flash-headroom trail
- `.planning/todos/pending/2026-09-16-reject-negative-write-start-address.md`,
  `2026-09-20-blank-check-region-fails-open-on-start-greater-than-end.md`

### Tertiary (LOW confidence)

- `.planning/graphs/graph.json` — present but last built **2026-09-18** (4 days stale); not relied
  on. Every relationship claim in this document comes from a direct read of the live trees instead.

---

## Metadata

**Confidence breakdown:**
- Site census: **HIGH** — every line read this session; three CONTEXT spans corrected, four sites added
- Flash/RAM measurement: **HIGH** — control tree reproduced the real tree byte for byte, so the
  −518 B / −4 B delta is a measurement, not an estimate
- Gate impact: **HIGH** — 7 + 8 + 17 legs measured by running the suites against a real swept tree
  beside an identical control
- Golden re-derive: **HIGH** — run with the gate's own extractor; positional alignment proved safe
  with 0 mismatches
- `erase -b` design: **MEDIUM** — the engine and the plumbing precedent are verified; the `0x06`
  disposition is a recommendation awaiting the operator
- Bench: **MEDIUM** — rig identity verified at the port; seated part unverified by design

**Research date:** 2026-09-22
**Valid until:** ~2026-10-06 for the stack facts; the **line numbers and gate counts are valid only
against `firestarter_fw` `24e3fdf` / `firestarter_app` `2a17fd7`** and must be re-verified if either
branch advances before planning.
</content>
</invoke>
