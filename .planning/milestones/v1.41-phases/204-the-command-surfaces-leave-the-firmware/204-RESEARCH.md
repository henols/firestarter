# Phase 204: The command surfaces leave the firmware - Research

**Researched:** 2026-09-21
**Domain:** AVR C++ firmware surface removal (wire-ordinal retirement) + Python host constant ladder + source-contract / golden gate re-anchoring + two-direction bench compatibility proof
**Confidence:** HIGH (every structural claim below was measured this session against the live tree; the bench legs are designed but not yet run)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

Copied verbatim from `204-CONTEXT.md` `<decisions>`. The planner MUST honour these.

- **D-01:** **Full sweep of both ordinals in 204.** FWCMD-01 names three sites; the tree carries
  **eleven firmware sites plus the host mirror**, measured during discussion. All of them go in this
  phase:

  | # | Site | What it is |
  |---|---|---|
  | 1 | `firestarter_fw/include/firestarter.h:52,54` | the two `#define`s |
  | 2 | `firestarter_fw/include/firestarter.h:117,119` | `is_memory_cmd` arms |
  | 3 | `firestarter_fw/src/firestarter.cpp:270-272,276-278` | dispatch switch arms |
  | 4 | `firestarter_fw/src/eprom_operations.cpp:30-33,53-56` | the two wrappers |
  | 5 | `firestarter_fw/include/eprom_operations.h:10,13` | their declarations |
  | 6 | `firestarter_fw/src/proms/memory.cpp:73-75` | `configure_memory`'s `CMD_VERIFY` arm |
  | 7 | `firestarter_fw/src/proms/eprom.cpp:56-58` | `configure_eprom`'s `CMD_BLANK_CHECK` arm |
  | 8 | `firestarter_fw/src/proms/flash_nor_unlock.cpp:43-45` | same, NOR unlock |
  | 9 | `firestarter_fw/src/proms/flash_intel.cpp:61` | same, Intel flash |
  | 10 | `firestarter_fw/src/proms/flash_5v_page.cpp:46` | same, flash4 |
  | 11 | `firestarter_fw/src/proms/eeprom_28c.cpp:150` | same, 28C parallel |
  | 12 | `firestarter_fw/src/operation_utils.cpp:231-…` | `_single_step_operation_callback`'s whole `CMD_BLANK_CHECK` emit-and-ack block |
  | 13 | `firestarter_fw/src/proms/memory.cpp:500,529` | the two `handle->cmd == CMD_BLANK_CHECK` branches **inside** `mem_util_blank_check_region` |

  Sites 12 and 13 exist **only** to serve the standalone command … **This is a behaviour-preserving
  collapse for every remaining caller**, and it must be proven so rather than assumed.
  — **Reversibility:** costly.

- **D-02:** **FWCMD-03's reserved record lives on BOTH ladders**, mirroring the shape FWBLANK-02
  already specifies for `0x08` in Phase 205. `#define CMD_BLANK_CHECK 4` / `#define CMD_VERIFY 6`
  leave `firestarter_fw/include/firestarter.h`, and `COMMAND_BLANK_CHECK` / `COMMAND_VERIFY` plus
  their `COMMAND_NAMES` rows leave `firestarter_app/firestarter/constants.py`. Each ladder gains a
  comment at the gap naming the version the ordinals were retired in and why they must never be
  reused.
  Two consequences: the Phase 202 inline comments in `eprom_operations.py` go stale and must be
  corrected in the same change; `eprom_operations.py:628` is a **live use** and deleting the
  constant forces the expression to change.
  — **Reversibility:** one-way.

- **D-03:** **FWCMD-05 is factually wrong and must be amended before planning.** Pin each site to
  the id it actually raises. Amend **both** `.planning/REQUIREMENTS.md` FWCMD-05 and
  `.planning/ROADMAP.md` Phase 204 success criterion 3. Record the before/after text in the phase
  record.

- **D-04:** **Proof instrument is split by property type.** FWCMD-04 is a **source-contract gate**
  (the eighth). The amended FWCMD-05 is **native behavioural tests** under
  `firestarter_fw/test/native/avr/`.

- **D-05:** **The existing generic refusal is accepted; no new message is minted.** The dispatch
  `default:` arm emits `LOG_ERROR_ID_U8(MSG_ERR_UNKNOWN_CMD, handle.cmd)` and calls
  `command_done()`. Accepted cost recorded: the operator sees `unknown`.

- **D-06:** **The orphaned debug ids stay in the catalog.** `DBG_VERIFY_PROM` (0x08) and
  `DBG_BLANK_CHECK_PROM` (0x0B) keep their `tools/catalog/messages.toml` entries, each gaining a
  comment. **This keeps 204 a two-repo phase.** — **Reversibility:** reversible.

- **D-07:** **`3.1.0b1` is a substituted label at 204, and the phase record names the real shas.**
  `3.1.0b1 host` / `3.1.0b1 firmware` mean the **post-204 working-tree builds**; `pre-3.1.0` means
  the **pre-204 artifacts**. **The phase record must state the substitution explicitly and name the
  commit sha that played each of the four roles.**

- **D-08:** **The pre-`3.1.0` host is the published wheel, not a reconstruction.**
  `pip install firestarter==3.0.0b49` into a throwaway venv. Two traps: the venv must be built on
  **3.11**; the app writes `~/.firestarter/config.json` regardless of `FIRESTARTER_CONFIG_DIR`.

- **D-09:** **"No hardware side effect" is proven by read-back equivalence on a socketed part.**
  Socket a non-blank part, checksum, run the refused `verify` and `blank`, checksum again, prove
  byte-identical. Empty socket rejected. Rail observation rejected outright.

- **D-10:** **The rig is an Arduino Leonardo carrying a Rev 2.0 shield with a W27C512 seated, on
  `/dev/ttyACM0`, and the operator has given standing permission to drive and flash it without
  asking.** Leonardo is exempt from chip-out-before-sideload; buffer is 1024; progress emission is
  Leonardo-only; flash ceiling 28672. **Coverage gap to state, not hide:** Leonardo only, no
  Uno-class board.

- **D-11:** **Criterion 4 (REL-02) needs no refusal at all.** The leg proves the *absence* of a
  compatibility problem; its value is entirely in being run rather than assumed.

- **D-12:** **The `DONE`-based clean stop does NOT land in 204. It stays filed as CMP-F1.**
  Record on CMP-F1 that old firmware already ignores `DONE` gracefully, so the change is
  forward-compatible by construction.

### Claude's Discretion

- The exact amendment wording for FWCMD-05 and ROADMAP criterion 3 (within D-03's per-site-id
  content), and whether the amendment lands as one commit or alongside the phase's first plan.
- The source-contract gate's module name, and whether FWCMD-04's gate is a new module or a leg added
  to an existing one — provided it fails when the `VERIFY_PER_PULSE_PLUS_FINAL` call disappears and
  that RED is **seen**, not pre-authored and assumed reachable.
- The mechanism for asserting an emitted message id in a native test (a log capture seam versus a
  trace diff), and whether `flash_util_verify_operation`'s timeout leg needs a `millis` stub or can
  be proven another way.
- The wording of the reserved-ordinal comments on both ladders and of the two catalog comments.
- Whether the Phase 201-05 nine-site source-contract gate is re-anchored to its four survivors in
  204 or retired here because 205 deletes the functions it guards. Not discussed — decide it in
  planning and state the reasoning.
- The bench sequence order, the number of chip swaps, and how the pre-204 firmware `.hex` is
  obtained (a released asset versus a local build of the pre-204 sha).
- Whether the `region-end` guard at `eprom_operations.py:628` becomes `cmd == COMMAND_WRITE` or
  keeps a one-member tuple.

### Deferred Ideas (OUT OF SCOPE)

- **The `DONE`-based clean stop in `op_wait_for_ack`.** Offered and declined (D-12). Best home:
  Phase 206.
- **A dedicated retired-command message** naming the version boundary instead of
  `Unknown command: 4` (D-05). Best home: Phase 207.
- **Retiring the orphaned `DBG_VERIFY_PROM` / `DBG_BLANK_CHECK_PROM` catalog entries** (D-06). Best
  home: any later phase already touching `tools/catalog/messages.toml`.
- **The firmware half of the negative-address todo** (`json_parser.c`'s `simple_strtoul` dropping
  the sign). Still **Phase 205**.

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description (verbatim from `.planning/REQUIREMENTS.md:65-70,103-104`) | Research Support |
|----|-------------|------------------|
| FWCMD-01 | "`CMD_VERIFY` (6) and `CMD_BLANK_CHECK` (4) are gone from the `firestarter.cpp` dispatch switch, from `is_memory_cmd`, and from `configure_memory`'s switch." | §Measured Site Census — 17 in-source sites enumerated with exact line numbers, all read this session |
| FWCMD-02 | "the `eprom_verify()` and `eprom_blank_check()` wrappers and their declarations are deleted." | §Measured Site Census sites 4-5; §Gate Impact — deleting them breaks `test_boolean_convention_source_contract_v133` (9→7), measured |
| FWCMD-03 | "ordinals 4 and 6 are recorded as reserved and never reused, with the reason stated where a future author will read it before reaching for a free slot." | §Both Ladders — the two gaps, the existing precedent comments, and the stale-citation repair list |
| FWCMD-04 | "`memory_verify_execute` still exists and is still called for `VERIFY_PER_PULSE_PLUS_FINAL` on protocols `0x07` / `0x08`; a test fails if that call disappears." | §Pattern 1 (source-contract gate) — the pinned call site `eprom.cpp:497`, the seven existing analogues, the planted-violation recipe |
| FWCMD-05 | "the per-pulse verify, `eeprom28c_verify_page_readback` and `flash_util_verify_operation` are behaviourally unchanged, and `MSG_ERR_VERIFY` (0xAF) is still raised by each." | §D-03 Amendment Evidence — the three real ids measured with file:line and verbatim quotes; §Pattern 2 (native id-capture) with the in-tree precedent |
| FWCMD-06 | "a host that sends ordinal 4 or 6 to `3.1.0b1` firmware receives an explicit refusal with no hardware side effect — never silence, never a hang." | §The Refusal Path, Traced End To End — the eight-step trace, the `Unknown command: %d` format string on both sides, the old host's exception handling |
| REL-02 | "a `3.1.0b1` host against pre-`3.1.0` firmware performs `verify` and `blank` correctly, because it only sends `CMD_READ`. Proven, not assumed." | §Bench Legs — the four roles, the artifact for each, the Leonardo identity verified at the port |
| REL-03 | "a pre-`3.1.0` host against `3.1.0b1` firmware fails `verify` and `blank` with a refusal the user can act on, and with no hardware side effect." | §Bench Legs — `3.0.0b49` installed and its command composition verified to still send ordinals 6 and 4 |

</phase_requirements>

---

## Summary

This phase is **structural removal with mechanical proof**, not design. There is nothing to choose a
library for, no new dependency, and no new algorithm. Almost all of the planning risk is in three
places: (a) exactly which committed gates go RED when the sweep lands, (b) whether the "proven, not
assumed" instruments can actually reach the properties they claim, and (c) whether the bench artifacts
exist and behave as the two REL requirements assume. All three were **measured this session**, not
reasoned about.

The headline result is that the blast radius is smaller and more precisely known than CONTEXT.md
estimates, and the two hardest-looking discretion items already have working in-tree precedents.
I built a full simulated post-sweep firmware tree (all 13 D-01 sites removed, including the site-12
and site-13 collapses) and ran the entire `tests/` suite against it beside an identical unmodified
control. **The delta is exactly four pytest legs, in three modules** — plus one blob-SHA leg that a
non-git scratch tree cannot exercise. Three of those four were predicted by CONTEXT; **one was not**
(`test_boolean_convention_source_contract_v133.py`, which counts the nine `eprom_*` wrapper bodies
FWCMD-02 deletes two of). Two things CONTEXT names as breakage do **not** break:
`test_progress_emission_is_leonardo_only.py` is untouched (it scans `eprom.cpp` + `platformio.ini`,
never `memory.cpp` or `operation_utils.cpp`), and the branch-inventory gate pins **one** tier-protocol
site at literal line **70**, not three at 71/145/218 — the re-anchor is `[70]` → `[67]`, measured by
running the gate's own extractor over the swept file.

The two "how do I even prove this?" discretion items are cheaper than they look. A native test that
asserts an **emitted message id** already exists — `test_eeprom28c_sdp.cpp` captures Serial bytes,
walks `rurp_log_id`'s wire layout, and asserts exactly the WARN/ERROR severity fork D-04 worries
about. And a **`millis()` seam exists** in the native environment: `test_cobs_cmd_frame.cpp` and
`test_cobs_data_frame.cpp` both install an advancing `millis()` through ArduinoFake. CONTEXT's "no
millis seam" is true only of `_shared/host_stubs_common.inc`; it is not true of the environment.
Both of `flash_util_verify_operation`'s and `eeprom28c_verify_page_readback`'s legs are therefore
reachable — with one caveat the planner must design around: `eeprom28c_verify_page_readback` is
`static`, so it can only be driven through `eeprom28c_write_execute`.

The bench legs are executable today. `/dev/ttyACM0` is present and enumerates as USB `2341:8036
Arduino Leonardo`, confirming D-10. The `firestarter==3.0.0b49` wheel installs cleanly into a 3.11
venv provisioned by `uv` (Python 3.11 is **not** on this machine; `uv python install 3.11` fetches it,
but `UV_CACHE_DIR` must be redirected because `~/.cache/uv` is unwritable). Most importantly, I opened
the installed wheel and confirmed it **still composes the retired ordinals** — `verify_eprom` passes
`COMMAND_VERIFY` and `check_eprom_blank` passes `COMMAND_BLANK_CHECK` into `_operation_context`.
`3.0.0b49` is the v1.40 cut, i.e. pre-Phase-202, so REL-03's leg is meaningful rather than vacuous.
That single fact is the load-bearing premise of the whole REL-03 half and it is now verified rather
than assumed.

**Primary recommendation:** Sequence the phase as *amend requirement → firmware sweep + gate
re-anchors in one commit → host ladder mirror in the paired commit → two new proof instruments with
seen-RED → bench matrix last*, and treat the four measured gate breaks in §Gate Impact as the
definition of done for the sweep rather than re-deriving them during execution.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Wire-ordinal admission (`is_memory_cmd`) | Firmware / AVR | — | It is a hardware-safety access-control gate: it decides what may call `configure_memory` and so energise the bus. `firestarter.h:108-113` states this in the code itself. |
| Command dispatch (`switch (handle.cmd)`) | Firmware / AVR | — | The only place a wire ordinal becomes an operation. Criterion 1 is a property of this switch. |
| Refusal of a retired ordinal | Firmware / AVR | — | D-05: the existing `default:` arm. No host tier participates; the old host cannot be changed. |
| In-algorithm verify (per-pulse, page read-back, DQ7 poll) | Firmware / AVR | — | D-7 (milestone): these are *inside* programming algorithms and cannot move to the host. |
| Whole-region compare (`verify`, `blank`) | Host / Python | — | Phase 202 already moved this. Nothing in this phase changes it. |
| Command-ordinal constant ladder | **Both**, in lockstep | — | `/workspaces/CLAUDE.md` § Cross-repo obligations: "Change both sides in the same commit pair." D-02 mirrors that. |
| Message catalog ids (`DBG_*`, `MSG_ERR_*`) | Meta repo (`tools/catalog/messages.toml`) | Both sub-repos consume synced artifacts | D-06 keeps 204 out of the meta tier deliberately — a catalog change would make this a three-repo lockstep. |
| Compatibility-skew evidence | Bench (Leonardo + W27C512) | — | Criteria 4 and 5 say "observed on the bench"; no tier below the physical one can answer them. |

---

## Measured Site Census — 17 in-source sites, not 11

Everything in this table was read this session with `sed -n`/`awk` against the live working tree at
`firestarter_fw` HEAD `e5842d8` on branch `v1.41-verification-to-host`. Line numbers are current.

### Firmware (`firestarter_fw`)

| # | Path:line | Verbatim text | Disposition |
|---|-----------|---------------|-------------|
| 1 | `include/firestarter.h:52` | `#define CMD_BLANK_CHECK 4` | delete, leave a reserved-gap comment (D-02) |
| 2 | `include/firestarter.h:54` | `#define CMD_VERIFY 6` | delete, leave a reserved-gap comment (D-02) |
| 3 | `include/firestarter.h:117` | `        case CMD_BLANK_CHECK:` | delete |
| 4 | `include/firestarter.h:119` | `        case CMD_VERIFY:` | delete |
| 5 | `src/firestarter.cpp:270-272` | `        case CMD_VERIFY:` / `            finished = eprom_verify(&handle);` / `            break;` | delete |
| 6 | `src/firestarter.cpp:276-278` | `        case CMD_BLANK_CHECK:` / `            finished = eprom_blank_check(&handle);` / `            break;` | delete |
| 7 | `src/eprom_operations.cpp:30-32` | `bool eprom_verify(firestarter_handle_t* handle) {` / `    LOG_DEBUG_ID_SUB(DBG_VERIFY_PROM);` / `    return op_execute_stateful_operation(_process_incoming_data, handle);` | delete whole wrapper (+ its `// Return true if the operation is done, otherwise false` comment at `:29`) |
| 8 | `src/eprom_operations.cpp:53-56` | `bool eprom_blank_check(firestarter_handle_t* handle) {` / `    LOG_DEBUG_ID_SUB(DBG_BLANK_CHECK_PROM);` / `    return op_execute_simple_operation(handle);` / `}` | delete whole wrapper |
| 9 | `include/eprom_operations.h:10` | `    bool eprom_verify(firestarter_handle_t* handle);` | delete |
| 10 | `include/eprom_operations.h:13` | `    bool eprom_blank_check(firestarter_handle_t* handle);` | delete |
| 11 | `src/proms/memory.cpp:73-75` | `        case CMD_VERIFY:` / `            handle->firestarter_operation_main = memory_verify_execute;` / `            break;` | delete |
| 12 | `src/proms/eprom.cpp:56-58` | `        case CMD_BLANK_CHECK:` / `            handle->firestarter_operation_main = mem_util_blank_check;` / `            break;` | delete |
| 13 | `src/proms/flash_nor_unlock.cpp:43-45` | `    case CMD_BLANK_CHECK:` / `        handle->firestarter_operation_main = mem_util_blank_check;` / `        break;` | delete (note: this file indents `case` by 4, not 8) |
| 14 | `src/proms/flash_intel.cpp:61-63` | `        case CMD_BLANK_CHECK:` / `            handle->firestarter_operation_main = mem_util_blank_check;` / `            break;` | delete |
| 15 | `src/proms/flash_5v_page.cpp:46-48` | `        case CMD_BLANK_CHECK:` / `            handle->firestarter_operation_main = mem_util_blank_check;` / `            break;` | delete |
| 16 | `src/proms/eeprom_28c.cpp:150-152` | `        case CMD_BLANK_CHECK:` / `            handle->firestarter_operation_main = mem_util_blank_check;` / `            break;` | delete |
| 17 | `src/operation_utils.cpp:231` (block runs to `:251`) | `    if (handle->cmd == CMD_BLANK_CHECK) {` … brace-matched block containing `LOG_ERROR_ID_BYTES(MSG_ERR_NOT_BLANK, …)`, `LOG_DATA_ID_U32_U32(MSG_DATA_PROGRESS, handle->address, handle->mem_size)` and `if (!op_wait_for_ack(handle)) { return false; }` | delete whole block (D-01 site 12) |
| 18 | `src/proms/memory.cpp:500-508` | `            if (handle->cmd == CMD_BLANK_CHECK) {` … `            } else {` / `                LOG_ERROR_ID_BYTES(MSG_ERR_NOT_BLANK, _b, 4);` / `            }` | collapse to the `else` arm (D-01 site 13a) |
| 19 | `src/proms/memory.cpp:529-531` | `    if (handle->cmd != CMD_BLANK_CHECK) {` / `        LOG_DATA_ID_U32_U32(MSG_DATA_PROGRESS, handle->address, end);` / `    }` | collapse to the unconditional emit (D-01 site 13b) |

**Two comment-only sites CONTEXT does not list**, both of which go stale and are in scope for
`/workspaces/CLAUDE.md`'s repair-citations rule:

| Path:line | Verbatim text |
|---|---|
| `src/proms/eeprom_28c.cpp:141` | `    // main for CMD_READ/CMD_WRITE/CMD_VERIFY before calling this, so a blanket` |
| `include/memory_utils.h:21` | ` * Defined in src/proms/memory.cpp as the CMD_VERIFY operation_main. */` |

`[VERIFIED: firestarter_fw src/include tree, read line-by-line 2026-09-21]`

### Firmware documentation (three more sites, not in CONTEXT)

| Path:line | What it says | Why it goes stale |
|---|---|---|
| `firestarter_fw/CLAUDE.md` (§ Protocol Dispatch) | "Second, a `switch (handle->cmd)` assigns the main operation for `CMD_READ`, `CMD_WRITE` and `CMD_VERIFY`." | `CMD_VERIFY` leaves that switch (site 11) |
| `firestarter_fw/PROTOCOLS.md:180` | "VPP is NOT enabled for CMD_READ or CMD_BLANK_CHECK operations." | ordinal 4 no longer exists |
| `firestarter_fw/PROTOCOLS.md:321` | "`blank` remains available as its own independent command through the unaffected `CMD_BLANK_CHECK` arm." | that arm is site 16 |
| `firestarter_fw/PROTOCOLS.md:549` | INV-05 row naming `CMD_BLANK_CHECK` and `test_inv05_eprom_vpp_skip_on_read` | the named test does not exist under that name in `test/native/avr/test_val_eprom/` — a pre-existing stale citation worth repairing while here |

`[VERIFIED: firestarter_fw/CLAUDE.md, PROTOCOLS.md grep + read 2026-09-21]`

### Host (`firestarter_app`) — complete census

| Path:line | Verbatim text | Disposition |
|---|---|---|
| `firestarter/constants.py:52` | `COMMAND_BLANK_CHECK = 4` | delete + reserved-gap comment |
| `firestarter/constants.py:54` | `COMMAND_VERIFY = 6` | delete + reserved-gap comment |
| `firestarter/constants.py:91` | `    COMMAND_BLANK_CHECK: "BLANK_CHECK",` | delete |
| `firestarter/constants.py:93` | `    COMMAND_VERIFY: "VERIFY",` | delete |
| `firestarter/eprom_operations.py:45` | `    COMMAND_VERIFY,` (the import) | delete |
| `firestarter/eprom_operations.py:628` | `            and cmd in (COMMAND_WRITE, COMMAND_VERIFY)` | **live use** — must change (discretion) |
| `firestarter/eprom_operations.py:2705` | `verify ordinal (COMMAND_VERIFY stays in constants.py; nothing on this` | stale comment — correct |
| `firestarter/eprom_operations.py:2743` | `# cmd in (COMMAND_WRITE, COMMAND_VERIFY) (_setup_operation's guard),` | **stale comment not in CONTEXT** — correct |
| `firestarter/eprom_operations.py:2959` | `# firestarter_operation_main for CMD_BLANK_CHECK, causing 0xA4` | **stale comment not in CONTEXT** — correct |
| `firestarter/eprom_operations.py:2978` | `COMMAND_BLANK_CHECK (COMMAND_BLANK_CHECK stays in constants.py;` | stale comment — correct |
| `firestarter/eprom_operations.py:2984` | `firmware handler leaves CMD_BLANK_CHECK's main-op NULL) has no blank` | **stale comment not in CONTEXT** — after 204 *every* protocol leaves it NULL; the `_SRAM_PROTO_IDS` rationale needs rewording |
| `firestarter/eprom_operations.py:3002` | `# CMD_BLANK_CHECK, so the firmware emits 0xA4 MSG_ERR_EMPTY_INPUT.` | **stale comment not in CONTEXT** — correct |
| `tests/test_eprom_operations.py:493` | `from firestarter.constants import COMMAND_READ, COMMAND_VERIFY` | **ImportError after deletion** |
| `tests/test_eprom_operations.py:1772` | `from firestarter.constants import COMMAND_BLANK_CHECK, COMMAND_READ` | **ImportError after deletion** |
| `tests/test_eprom_operations.py:1999-2001` | imports both constants | **ImportError after deletion** |
| `tests/test_erase_blank_step_nonregression.py:6,143` | prose only; `# Leg 4:` is a bare comment header with no test function beneath it (file is 146 lines and ends there) | comment repair only — **no gate breaks** |

`[VERIFIED: firestarter_app tree, grep + read 2026-09-21]`

**Two structural findings on the host side, both useful:**

1. **No app test scans firmware source for the CMD ladder.** The recorded hazard "app gates scan
   FIRMWARE source — renames break them, they fail OPEN" does **not** apply to this phase. A full
   grep for `firestarter.h`, `firestarter_fw`, `CMD_VERIFY` and `CMD_BLANK_CHECK` across
   `firestarter_app/tests/` and `firestarter_app/firestarter/` found only Python imports and prose.
   `[VERIFIED: firestarter_app grep 2026-09-21]`
2. **`constants.py:69` cites a test module that does not exist.** The comment reads
   "`test_command_names_dereferences_both_sdp_commands` in `tests/test_revision_constants_parity.py`,
   which pins both dereferences" — `ls firestarter_app/tests/` has no such file. The same comment
   block's line-number citations (`eprom_operations.py:329` and `:405`) are also stale: the real
   `COMMAND_NAMES[cmd]` dereferences are at `eprom_operations.py:584` and `:693`. Repair per
   `/workspaces/CLAUDE.md`'s "never accept staleness" rule while editing the ladder.
   `[VERIFIED: firestarter_app/firestarter/constants.py:59-69 and grep for COMMAND_NAMES 2026-09-21]`

---

## Gate Impact — measured, not predicted

### Method

I copied `git ls-files` from `firestarter_fw` into two scratch trees, applied **all** of D-01's
removals (including sites 17-19, the collapses) to one of them, and ran
`pytest tests/ -q -o addopts="" -p no:cacheprovider --ignore=tests/test_update_version.py` on both
with Python 3.11.16. Eleven failures are common to both trees and are artifacts of a non-git scratch
directory (`git -C … status --porcelain` exits 128). The **delta is the finding**.

- Control (unmodified): `11 failed, 259 passed, 32 skipped`
- Post-sweep: `15 failed, 255 passed, 32 skipped`

`[VERIFIED: pytest run 2026-09-21, both trees, same interpreter and flags]`

### The four real breaks

| # | Module::leg | Today | Post-204 | Re-anchor |
|---|---|---|---|---|
| G1 | `test_blank_check_region_source_contract.py::test_exactly_six_whole_device_function_pointer_assignments_and_zero_region_form_ones` | `assert len(wrapper_hits) == 6` | **found 1** | change the literal to `1`; update the docstring's "six function-pointer assignments" census |
| G2 | `test_boolean_convention_source_contract_v133.py::test_the_nine_forwarding_calls_are_present` | 9 (4 stateful, 5 simple) | **found 7 (2 stateful, 5 simple)** | change to `7`; rename the function; update the "nine `eprom_*` wrappers" prose in the docstring. **Not named in CONTEXT.md.** |
| G3 | `test_protocol_branch_inventory.py::test_branch_sites_match_the_recorded_inventory` | 22 sites at lines `[45, 52, 69, 70, 101, 130, 132, 136, 137, 144, 158, 247, 257, 275, 424, 519, 556, 561, 591, 594, 595, 610]` | 22 sites at `[45, 52, 66, 67, 98, 127, 129, 133, 134, 141, 155, 244, 254, 272, 421, 516, 553, 558, 588, 591, 592, 607]` | re-derive the golden with the module's own `_extract_predicates` |
| G4 | `test_protocol_branch_inventory.py::test_exactly_one_protocol_keyed_site_at_the_pinned_line` | `assert protocol_lines == [70]` | **`[67]`** | change the pinned literal to `[67]` |

Plus **G5**, which a non-git scratch tree cannot exercise but which is certain in the real repo:
`test_protocol_branch_inventory.py::test_blob_shas_match_the_recorded_inventory` —
`meta.blob_shas["src/proms/eprom.cpp"]` is `e3b53d9d2f7bf7925d1c1fc16bc4a0aaee17884b` and must be
re-recorded with `git hash-object src/proms/eprom.cpp` on the working tree **before staging**.
`meta.blob_shas["src/proms/eprom_params.cpp"]` (`b1e7188660ca0c3435ce871e4898b3697fd16057`) is
**untouched** — 204 does not edit that file. `[VERIFIED: tests/golden/protocol_branch_inventory.json meta.blob_shas, read 2026-09-21]`

### Three CONTEXT claims corrected

**C-1. The branch-inventory gate pins ONE protocol site at line 70, not three at 71/145/218.**
CONTEXT § Known traps says "test 3 pins literal line numbers 71, 145 and 218". Measured: the test is
named `test_exactly_one_protocol_keyed_site_at_the_pinned_line` and its body is

```python
    protocol_lines = sorted(s["line"] for s in live if s["tier"] == "protocol")
    assert protocol_lines == [70], (
```

with a docstring stating "This locator is now STRICTLY STRONGER than its three-site predecessor".
The 71/145/218 shape was retired by Phase 142 Plan 04. The golden's `counts` block reads
`{"total_sites": 22, "protocol_keyed_sites": 1, "other_sites": 21}`.
`[VERIFIED: firestarter_fw/tests/test_protocol_branch_inventory.py:441-460 and tests/golden/protocol_branch_inventory.json counts]`

**C-2. `test_progress_emission_is_leonardo_only.py` is NOT affected.** CONTEXT says it "names
`blank_check`, and is about exactly the emit block D-01 site 12 deletes". Measured: its only two
`blank` references (`:106`, `:590`) are **prose** inside Coverage 6's payload-contract rationale; its
scan targets are `src/proms/eprom.cpp` and `platformio.ini` only, and the emit it pins is
`eprom.cpp:414`'s per-byte **write-loop** emit, not `mem_util_blank_check`'s. All 11 of its legs pass
against the swept tree. *Secondary effect worth noting:* its Coverage 6 prose says 0xE0 has "two
emitters"; today there are **three** (`eprom.cpp:414`, `memory.cpp:530`, `operation_utils.cpp:235`),
so D-01 site 17's deletion makes that prose true rather than breaking it.
`[VERIFIED: grep + full-leg run against the swept tree 2026-09-21]`

**C-3. `test_hv_routing_source_contract_v142.py` (16 legs), `test_write_path_source_contract_v131.py`
(13 legs) and `test_ack_layout_source_contract_v143.py` (10 legs) are all unaffected** — 0 failures
each against the swept tree. `test_golden_trace_identity.py` pins the blob SHA of
`test/native/avr/_shared/sdp_expected.h`, which 204 does not touch.
`[VERIFIED: leg-by-leg run 2026-09-21]`

### The native (Unity) tree — four files stop compiling

`pio test -e native` on the unmodified tree is the baseline: **19 suites, 237 test cases, 237
succeeded, 57.9 s, exit 0**. `[VERIFIED: pio test -e native run 2026-09-21, PlatformIO Core 6.2.0]`

Once `CMD_VERIFY` and `CMD_BLANK_CHECK` leave `firestarter.h`, these files **fail to compile**:

| File:line | Verbatim | What to do |
|---|---|---|
| `test_dispatch/test_configure_memory.cpp:193` | `    static const uint8_t cmds[] = {CMD_READ, CMD_WRITE, CMD_VERIFY};` | drop `CMD_VERIFY` **and** the literal loop bound at `:196` (`for (size_t c = 0; c < 3; c++)`) — the bound is hard-coded, not `sizeof`-derived, so dropping an element alone reads past the array |
| `test_dispatch/test_configure_memory.cpp:194` | `    static const char* cmd_names[] = {"CMD_READ", "CMD_WRITE", "CMD_VERIFY"};` | drop the third entry |
| `test_dispatch/test_configure_memory.cpp:321` | `        firestarter_handle_t h_blank = make_handle(protocol, 0, CMD_BLANK_CHECK);` | Case group 5's SRAM blank-check assertion; it is now about a retired ordinal — decide delete vs. re-key to a surviving cmd |
| `test_val_eprom/test_val_eprom.cpp:387` | `    h.cmd           = CMD_BLANK_CHECK;` (inside `test_shadow_seed_is_address_keyed_not_modulo_aliased`) | re-key to a surviving ordinal |
| `test_val_eprom/test_val_eprom.cpp:478` | `    firestarter_handle_t h = make_region_handle(0x07, CMD_BLANK_CHECK, 16384);` then `h.firestarter_operation_main(&h);` | **Highest-risk item.** With the `configure_eprom` arm gone, `firestarter_operation_main` stays NULL and this test **null-dereferences**, not merely fails. This is BLANK-02's chunking contract (`test_blank_check_resumes_across_chunks_and_restores_the_cursor`), which survives until Phase 205 — re-key it to assign `mem_util_blank_check` directly, or drive it through the erase-end path |
| `test_val_nor_unlock/test_val_nor_unlock.cpp:132` | `    firestarter_handle_t h = make_handle(CMD_BLANK_CHECK);` | `test_nor_unlock_blank_check_configure_no_vpp` — after removal this would pass **vacuously**; delete or re-key |
| `test_val_eeprom28c/test_val_eeprom28c.cpp:170` | `    firestarter_handle_t h = make_handle(CMD_BLANK_CHECK);` | `test_eeprom28c_blank_check_configure_no_vpp` — same |

And **`test_cmd_admission/test_cmd_admission.cpp` compiles but asserts the wrong thing**, because its
truth table uses bare integers:

```c
void test_admission_truth_table_over_every_cmd_value(void) {
    for (int c = 0; c <= 255; c++) {
        bool expected;
        switch (c) {
            case 1:
            case 2:
            case 3:
            case 4:      /* <- CMD_BLANK_CHECK: must be removed */
            case 5:
            case 6:      /* <- CMD_VERIFY: must be removed */
            case 9:
            case 10:
            case 16:
                expected = true;
```

and

```c
void test_admission_count_is_exactly_nine(void) {
    …
    TEST_ASSERT_EQUAL_MESSAGE(9, count,
        "is_memory_cmd() must admit exactly nine of the 256 possible uint8_t values (Phase 151, LOCK-02)");
```

**9 → 7**, plus the function name and the message. `[VERIFIED: test/native/avr/test_cmd_admission/test_cmd_admission.cpp:41-77, read 2026-09-21]`

Note also `include/firestarter.h:108-110`'s own comment — "All nine named macros are unconditionally
defined. A source-scan gate checks this." — becomes "seven". I could not find that source-scan gate:
`grep -rn is_memory_cmd tests/ scripts/ tools/ platform/` in `firestarter_fw` returns **only**
`test_cmd_admission.cpp`. Treat the comment's "a source-scan gate checks this" as a stale claim and
repair it. `[VERIFIED: grep across firestarter_fw tests/, scripts/, tools/, platform/ 2026-09-21]`

### Adding a native suite costs 2 lines, not 4

`firestarter_fw/CLAUDE.md` says "A new suite must appear in **both** environments' `test_filter` and
`-I` lists, which is four new lines". Measured: `platformio.ini` defines `test_filter` **once** in
`[native_base]` and the `-I` list once in `[native_base].shared_build_flags`; both `[env:native]` and
`[env:native_nodevtools]` `extends = native_base` and reference `${native_base.shared_build_flags}`.
So it is **one `test_filter` line and one `-I` line**. CLAUDE.md is stale here.
`[VERIFIED: firestarter_fw/platformio.ini [native_base] block, read 2026-09-21]`

**CI consequence the planner must respect:** per `firestarter_fw/CLAUDE.md` § What CI runs,
`pio test -e native` is **pull-requests-only** while `pio test -e native_nodevtools` **always** runs.
Because both envs share one `test_filter`, a new suite runs in both — which is what you want. Do not
"optimise" by giving one env its own filter.

---

## D-03 Amendment Evidence — the three real error ids

Every row below was read from the live source this session. The quoted lines are verbatim.

| Named site | File:line | The raise, verbatim | Real id | Value |
|---|---|---|---|---|
| `memory_verify_execute` (FWCMD-04's survivor) | `src/proms/memory.cpp:391` | `                LOG_ERROR_ID_BYTES(MSG_ERR_VERIFY, _b, 5);` | `MSG_ERR_VERIFY` | `#define MSG_ERR_VERIFY                    0xAF` (`include/messages.h:93`) |
| per-pulse verify, budget exits | `src/proms/eprom.cpp:462` | `            eprom_internal_report_budget_failure(handle, first_bad, pulses, MSG_ERR_MAX_PULSES);` | `MSG_ERR_MAX_PULSES` | `#define MSG_ERR_MAX_PULSES                0xBD` (`messages.h:107`) |
| per-pulse verify, budget exits | `src/proms/eprom.cpp:472` | `            eprom_internal_report_budget_failure(handle, first_bad, pulses, MSG_ERR_ENERGY_CAP);` | `MSG_ERR_ENERGY_CAP` | `#define MSG_ERR_ENERGY_CAP                0xBE` (`messages.h:108`) |
| `eeprom28c_verify_page_readback` | `src/proms/eeprom_28c.cpp:530` | `                LOG_ERROR_ID_BYTES(MSG_ERR_VERIFY, _b, 5);` | `MSG_ERR_VERIFY` ✔ | `0xAF` |
| `flash_util_verify_operation` | `src/proms/flash_utils.cpp:47` | `    LOG_ERROR_ID(MSG_ERR_OP_TIMEOUT);` | `MSG_ERR_OP_TIMEOUT` | `#define MSG_ERR_OP_TIMEOUT                0xB7` (`messages.h:101`) |

**D-03 is confirmed exactly as CONTEXT states it.** `[VERIFIED: firestarter_fw src/proms/*.cpp and include/messages.h, read 2026-09-21]`

Two refinements the amendment wording should carry:

- The **only** two `MSG_ERR_VERIFY` raise sites in the whole tree are `memory.cpp:391` and
  `eeprom_28c.cpp:530`. Every other tree-wide occurrence is a comment (`eprom.cpp:495`,
  `include/eprom.h:90`), the `#define`, or prose inside
  `tests/golden/protocol_branch_inventory.json:179`. **No test asserts `MSG_ERR_VERIFY` anywhere
  today** — CONTEXT is right about that. `[VERIFIED: grep -rn MSG_ERR_VERIFY across firestarter_fw 2026-09-21]`
- `flash_util_verify_operation` genuinely cannot raise `0xAF`. Its body is a DQ7 data-poll wait:
  `unsigned long timeout = millis() + 150;` then a loop comparing `(fu_flash_data_poll() & 0x80) ==
  (expected_data & 0x80)` twice, returning on success and falling through to `MSG_ERR_OP_TIMEOUT`.
  There is no compare-and-report path in it at all.
- The `VERIFY_PER_PULSE_PLUS_FINAL` arm FWCMD-04 pins is `src/proms/eprom.cpp:497`:
  `    if (verify_mode == VERIFY_PER_PULSE_PLUS_FINAL) {` followed by `        memory_verify_execute(handle);`.
  The rows that reach it are `eprom_params.cpp:31` (`0x07`) and `:32` (`0x08`); `:33` (`0x0B`) ships
  `VERIFY_PER_PULSE`. `enum { VERIFY_PER_PULSE = 0, VERIFY_PER_PULSE_PLUS_FINAL = 1 };`
  (`include/eprom_params.h:34`). `[VERIFIED: eprom.cpp:493-499, eprom_params.cpp:31-33, eprom_params.h:34]`

**Amendment wording recommendation (discretion item).** Replace FWCMD-05's single-id claim with a
per-site table naming three distinct ids, and add an explicit anti-regression clause:

> **FWCMD-05**: each in-algorithm verify still raises its own failure id on failure, proven by test
> and not by inspection: `memory_verify_execute` and `eeprom28c_verify_page_readback` raise
> `MSG_ERR_VERIFY` (0xAF); the per-pulse verify's budget exits raise `MSG_ERR_MAX_PULSES` (0xBD) and
> `MSG_ERR_ENERGY_CAP` (0xBE); `flash_util_verify_operation` is a DQ7 data-poll wait and raises
> `MSG_ERR_OP_TIMEOUT` (0xB7) — it can never raise 0xAF, and asserting that it does would be a false
> pin. Each assertion names the id, not merely `RESPONSE_CODE_ERROR`.

Land the amendment as **its own commit before the first implementation plan**, following Phase 203
D-02's precedent, so the sweep's commits are not carrying a requirements edit.

---

## The Refusal Path, Traced End To End (FWCMD-06 / criterion 5)

Traced against the live source; every step cites a line I read.

1. `loop()` idle branch decodes a COBS frame and calls `init_programmer_framed(&handle)`
   (`firestarter.cpp:249`).
2. `parse_json(handle)` succeeds; `handle->cmd` is 4 or 6.
3. `firestarter.cpp:74`: `    if (is_memory_cmd(handle->cmd) || handle->cmd < CMD_READ_VPP) {` —
   after the sweep `is_memory_cmd(4)` is **false**, but `4 < 11` is **true**, so the branch is taken
   and `json_parse(...)` runs.
4. `firestarter.cpp:84`: `        if (is_memory_cmd(handle->cmd)) {` is **false**, so control takes
   the `else` at `:93`, whose body is two `LOG_DEBUG_ID_SUB_U8` lines inside `#if DEV_TOOLS`.
   **`configure_memory` is never called.** All three operation pointers stay NULL.
5. `firestarter.cpp:142`: the second, independent guard `if (handle->cmd > CMD_IDLE && handle->cmd <
   CMD_READ_VPP)` still fires, emitting three `DBG_*` lines (verbose-gated).
6. `firestarter.cpp:202`: `        LOG_OK_ID_BYTES(MSG_OK_READY, _ready, (uint8_t)(4 + _vlen + 2));`
   — the ack is emitted for **every** command. `eprom_block_budget_s(handle->protocol, …)` returns 0
   because `configure_memory` never ran. `init_programmer_framed` returns `true`.
7. Next `loop()`: `handle.cmd` is 4 or 6, not `CMD_IDLE`, so the dispatch switch runs and falls to
   `firestarter.cpp:338-341`:
   ```c
        default:
            LOG_ERROR_ID_U8(MSG_ERR_UNKNOWN_CMD, handle.cmd);
            finished = true;
            break;
   ```
8. `finished` is true → `command_done(&handle)` (`firestarter.cpp:208-217`) sets programmer mode,
   `rurp_chip_disable()`, writes `0x00` to `CONTROL_REGISTER`, `LEAST_SIGNIFICANT_BYTE` and
   `MOST_SIGNIFICANT_BYTE`, sets `handle->cmd = CMD_IDLE` and returns to communication mode.

`[VERIFIED: firestarter_fw/src/firestarter.cpp:60-100, 114-217, 262-345, read 2026-09-21]`

**Why "no hardware side effect" is structurally true, and stronger than today.** The VPP boost
regulator is engaged only inside `firestarter_operation_init` → `eprom_generic_init` →
`eprom_check_vpp`, and `firestarter_operation_init` is only ever set by a `configure_*` handler,
which only `configure_memory` calls. Step 4 shows `configure_memory` is unreachable for a retired
ordinal. The firmware states this itself at `firestarter.cpp:179-183`:

> `// Emitting identity HERE is safe: configure_memory has run, but every`
> `// configure_* handler is pure function-pointer assignment and the VPP`
> `// regulator is not engaged until firestarter_operation_init, behind`
> `// op_wait_for_ack(). A host that reads this ack and refuses stops with the rail`
> `// still DOWN -- the compatibility gate cannot energise the part it protects.`

Today a standalone `CMD_BLANK_CHECK` on `0x07` **does** reach `configure_eprom`, which sets
`handle->firestarter_operation_init = eprom_generic_init` unconditionally at `eprom.cpp:43`, so it
does run `eprom_check_vpp`. After 204 that path is gone for ordinal 4. **The removal makes the
retired ordinals strictly safer, not merely equally safe** — worth stating in the phase record.

**What the operator actually sees.** `MSG_ERR_UNKNOWN_CMD = 0xAB` with
`format = "Unknown command: %d"` and `params = [{ type = "u8" }]`
(`/workspaces/tools/catalog/messages.toml:513-518`). The **published `3.0.0b49` wheel carries the
identical format string** at `firestarter/messages.py:591`, so the old host renders
`Unknown command: 4` / `Unknown command: 6`. `[VERIFIED: tools/catalog/messages.toml:512-518 and the installed 3.0.0b49 wheel's messages.py:587-591, both read 2026-09-21]`

**Why it does not hang.** The old host's `_run_state_machine` wraps the INIT/MAIN/END drive in
`except EpromOperationError as e:` → `self.last_firmware_error_code = e.error_code` →
`return False, str(e)` (`3.0.0b49` wheel, `eprom_operations.py:629-637`). An ERROR frame during
`_execute_phase("INIT")` therefore produces a logged, coded, non-hanging failure.
`[VERIFIED: installed 3.0.0b49 wheel, eprom_operations.py:587-640, read 2026-09-21]`

**Bonus precedent for Phase 207's wiki page:** the shipped host already models this exact situation.
`sdp_honesty.py:66` reads "`MSG_ERR_UNKNOWN_CMD` means the attached firmware predates …". Cite it
rather than inventing new language.

---

## Bench Legs — artifacts verified, sequence designed

### Rig, verified at the port

| Fact | Evidence |
|---|---|
| `/dev/ttyACM0` present | `crw-rw-rw-+ 1 root dialout 166, 0 Sep 21 21:17 /dev/ttyACM0` |
| It is a Leonardo | `/sys/bus/usb/devices/3-3.1.2.2/` → `2341:8036 Arduino Leonardo` |
| It is the **only** serial device | no other `ttyACM*`/`ttyUSB*` exists |
| PlatformIO available | `PlatformIO Core, version 6.2.0` |

`[VERIFIED: /dev listing, /sys/bus/usb/devices sweep, pio --version, all 2026-09-21]`

D-10's "no Uno-class coverage" gap is therefore **physically true right now**, not merely a caution.
`fw --install` flashes the attached board and ignores `--board`; with exactly one board attached this
is unambiguous, but a `--board` argument in any bench script is inert and must not be read as
targeting.

### The four roles and the artifacts that play them

| Role | Artifact | Verified? |
|---|---|---|
| post-204 host ("`3.1.0b1` host") | the `firestarter_app` working tree at the post-204 sha, editable-installed | n/a — does not exist yet |
| pre-204 firmware ("pre-`3.1.0` firmware") | either the published `3.0.0b34` `.hex` asset or a local `pio run -e leonardo` at `firestarter_fw` sha `e5842d8` | working-tree `include/version.h` reads `#define VERSION "3.0.0b33"`, one behind the published `b34` — the label is documentation, not mechanism (D-07) |
| post-204 firmware ("`3.1.0b1` firmware") | local `pio run -e leonardo` of the swept tree | n/a — does not exist yet |
| pre-204 host ("pre-`3.1.0` host") | `firestarter==3.0.0b49` from PyPI in a throwaway 3.11 venv | **verified installable and correct** — see below |

### The `3.0.0b49` wheel genuinely sends the retired ordinals

This is the premise the whole REL-03 leg rests on, so I installed and opened it rather than assuming.

```
version=3.0.0b49
…/site-packages/firestarter/eprom_operations.py:2165:            COMMAND_VERIFY,
…/site-packages/firestarter/eprom_operations.py:2348:            COMMAND_BLANK_CHECK,
```

Line 2165 is inside `verify_eprom`'s `with self._operation_context(eprom_name, eprom_data_dict,
COMMAND_VERIFY, …)`, and 2348 is inside `check_eprom_blank`'s `with self._operation_context(…,
COMMAND_BLANK_CHECK, …)`. `3.0.0b49` is the **v1.40** cut — Phase 202's host-side compare landed on
`v1.41-verification-to-host` and has never been published — so this wheel predates the rewiring and
still pushes the file to the firmware's verify ordinal.
`[VERIFIED: uv pip install firestarter==3.0.0b49 into a 3.11 venv, then read the installed eprom_operations.py:2150-2185 and :2335-2360, 2026-09-21]`

### The venv recipe, with the traps removed

Measured, working, on this machine:

```bash
# 1. ~/.cache/uv is NOT writable in this devcontainer. Redirect it or every uv call fails
#    with: "Failed to initialize cache at `/home/vscode/.cache/uv` … Permission denied".
export UV_CACHE_DIR=/tmp/claude-1000/<session>/scratchpad/uvcache
mkdir -p "$UV_CACHE_DIR"

# 2. Python 3.11 is NOT installed. The devcontainer has 3.12.14 (default) and 3.13.5.
#    App CI is 3.11-only (three `python-version: '3.11'` steps) and pyproject says
#    requires-python = ">=3.11". uv fetches it in ~1 s.
uv python install 3.11          # -> cpython-3.11.16-linux-x86_64-gnu

# 3. `uv venv` creates a venv WITHOUT pip. `./venv/bin/python -m pip` fails with
#    "No module named pip". Either add --seed or drive installs through uv.
uv venv --python 3.11 /tmp/.../oldhost-venv
uv pip install --python /tmp/.../oldhost-venv/bin/python 'firestarter==3.0.0b49'
```

`[VERIFIED: each command executed 2026-09-21; the install resolved pyserial 3.5, requests 2.34.2, rich 15.0.0, tqdm 4.70.1, urllib3 2.8.0, pygments 2.21.0]`

**The config trap is currently latent, not active.** `~/.firestarter/` does **not exist** on this
machine right now. The recorded behaviour is that the app writes `~/.firestarter/config.json`
regardless of `FIRESTARTER_CONFIG_DIR`, so the first bench run — from either host — will create it and
both hosts will then share it. Snapshot or move it between legs rather than trusting the env var.
`[VERIFIED: ls -la ~/.firestarter/ returned nothing, 2026-09-21]` `[ASSUMED: that the shared-config behaviour still holds in 3.0.0b49 — carried from the project memory record, not re-probed]`

### Recommended bench sequence (discretion item)

One chip insertion, one chip removal, two firmware flashes, no operator hands on the socket between
legs (Leonardo is exempt from chip-out-before-sideload).

| Step | Action | Proves |
|---|---|---|
| B0 | Verify port identity: confirm `/dev/ttyACM0` is the Leonardo (`2341:8036`) **this session** — ttyACM numbers shuffle across replug | prerequisite |
| B1 | Flash **pre-204** firmware. Read the seated W27C512 whole-device to `pre.bin`; record its SHA-256 | the content baseline |
| B2 | **post-204 host** → `verify` and `blank` against **pre-204 firmware** | **REL-02 / criterion 4.** Only `CMD_READ` is sent, which old firmware serves. D-11: this leg's value is entirely in being run |
| B3 | Flash **post-204** firmware (no chip removal needed) | — |
| B4 | **post-204 host** → `read` the chip to `mid.bin`; assert `mid.bin == pre.bin` | isolates any effect of the flash itself from the refusal legs |
| B5 | **pre-204 host (`3.0.0b49` venv)** → `verify <chip> <file>` against **post-204 firmware**. Capture stdout/stderr and exit code. Expect `Unknown command: 6` | **REL-03 / criterion 5**, refusal half |
| B6 | **pre-204 host (`3.0.0b49` venv)** → `blank <chip>`. Expect `Unknown command: 4` | **REL-03**, refusal half |
| B7 | **post-204 host** → `read` the chip to `post.bin`; assert `post.bin == mid.bin == pre.bin` byte-for-byte | **D-09's read-back equivalence** — the "no hardware side effect" half, observed on silicon |

Notes the planner should bake into the plan rather than discover:
- Both 204 legs are **read-only**, so the W27C512's write-path gotchas (plain `write` does erase;
  `-b` polarity is inverted) are not exercised. Only its ability to hold content across a firmware
  swap matters.
- **The host cannot tell you which firmware is on the board.** `_probe_port`'s `[\d.x]+` truncates the
  prerelease suffix, so `b33`, `b34` and a post-204 build are indistinguishable to the host. D-07's
  substituted labels plus the commit shas in the phase record are the **only** record of which
  firmware played which role. Log the flash command and its sha at each step.
- `test_no_programmer_found_*` in the app suite go RED with a live board attached. `/dev/ttyACM0` is
  attached, so those failures during a local app-suite run are **not** defects.
- `test_flash_path_record_sync` asserts whole-repo porcelain — commit before running the fw suite.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---|---|---|---|
| A gate that fails when the `VERIFY_PER_PULSE_PLUS_FINAL` call disappears | a fresh regex scanner | copy `tests/test_write_path_source_contract_v131.py`'s shape element for element (it is the closest analogue, and `test_blank_check_region_source_contract.py` says so explicitly in its own docstring) | Seven of these already exist. They share `_strip_comments` (shape-preserving whitespace so line numbers survive), `_find_matching_brace`, `_function_body_span`, `_REPO_ROOT`-relative targets, concatenation-built needles, a non-vacuity leg and a cannot-be-skipped leg |
| Asserting an emitted message id in a native test | a new trace format or a golden-diff harness | `test_eeprom28c_sdp.cpp`'s `captured_frames` + `sdp_captured_frame_ids()` + `sdp_ids_contains()` | It already walks `rurp_log_id`'s documented wire layout (4-byte magic, 2-byte BE length, id at `offset+6`, params, CRC) with no message-id lookup table, and it already asserts a WARN/ERROR **fork** — the exact trap D-04 names |
| Driving `flash_util_verify_operation`'s 150 ms timeout | a new `millis` seam in `_shared/host_stubs_common.inc` | ArduinoFake, as `test_cobs_cmd_frame.cpp:155-158` and `test_cobs_data_frame.cpp:149-152` already do | `When(Method(ArduinoFake(Function), millis)).AlwaysDo([]{ millis_counter += 100; return millis_counter; })` — an advancing counter, already in the tree, already passing in CI |
| Re-deriving the branch-inventory golden | hand-editing line numbers | the gate module's own `_extract_predicates()` | The golden's `meta.how_to_update` says so, and its `meta.recorded_by` records two occasions where a `(predicate, keyed_on, tier)` dict key collided and silently dropped sites. Match **positionally** |
| Comparing old sites to live sites | a dict keyed on `(predicate, keyed_on, tier)` | index-aligned zip, verified first that no site was added/removed | Three sites share `if (handle->response_code == RESPONSE_CODE_ERROR)` / `[response_code]` / `other`; a dict comprehension keeps only the last |
| Deciding whether a gate is affected | reasoning about which files it "probably" scans | run it against a swept scratch tree beside an unmodified control | That is how C-1, C-2 and G2 were found. Two of the three contradict the prose |

---

## Common Pitfalls

### Pitfall 1: `grep --no-ignore` silently returns zero matches
**What goes wrong:** A census sweep reports "no remaining references" when the flag was rejected.
**Why it happens:** `grep` in this devcontainer is a **bash function** wrapping Claude Code's bundled
ugrep 7.8.4 with `-G --ignore-files --hidden -I --exclude-dir=.git …`. ugrep has no `--no-ignore`
option — it errors with `ugrep: invalid option --no-ignore, did you mean …`. With `2>/dev/null` the
error vanishes and `| wc -l` reports `0`, and the pipeline's exit status is `wc`'s `0`.
**Measured:** `grep -rn --no-ignore -e CMD_VERIFY -e CMD_BLANK_CHECK src include test tests 2>/dev/null | wc -l` → **0**, while the same command without `--no-ignore` → **32**.
**How to avoid:** Never pass `--no-ignore`. Use `--ignore-files` (the wrapper already sets it) or
`command grep`. Never swallow stderr in a census. Never let a census gate's verdict be a `wc -l`.
`[VERIFIED: executed both forms and read the ugrep error text, 2026-09-21]`

### Pitfall 2: a pre-authored gate leg that cannot fail
**What goes wrong:** A new source-contract leg is written, goes green, and is recorded as proof —
but it was never reachable.
**How to avoid:** Both D-04 instruments need a **planted-violation run whose RED is seen**. For the
FWCMD-04 gate, delete `memory_verify_execute(handle);` from `eprom.cpp:498`, run, capture the
failure text, restore the file. `test_blank_check_region_source_contract.py`'s docstring records the
house preference: plant **directly into the real file** and restore, rather than using the env seam,
because the seams bind at **import** time and a post-import monkeypatch does nothing.

### Pitfall 3: `test_val_eprom.cpp:478` null-dereferences rather than failing
**What goes wrong:** Removing `configure_eprom`'s `CMD_BLANK_CHECK` arm leaves
`firestarter_operation_main` NULL, and `test_blank_check_resumes_across_chunks_and_restores_the_cursor`
calls `h.firestarter_operation_main(&h)` unguarded — a segfault, not a Unity failure, so the message
is unhelpful.
**How to avoid:** Re-key that test before or in the same commit as the sweep. It guards BLANK-02's
chunking contract, which survives until Phase 205, so do not simply delete it.

### Pitfall 4: the branch-inventory line shift depends on nothing else changing in `eprom.cpp`
**What goes wrong:** The plan pins `[67]`, then also adds a reserved-ordinal comment to `eprom.cpp`,
and the number is wrong again.
**Measured:** deleting exactly `eprom.cpp:56-58` shifts 20 of 22 sites by exactly −3 and leaves the
two sites above the cut (45, 52) untouched. **Any** other line added or removed above line 610 in
that file changes the answer. Re-derive with the extractor at commit time; do not carry `[67]`
forward as gospel if the diff grew.

### Pitfall 5: the golden and the source must land in ONE commit
**What goes wrong:** the gate is legitimately RED between two commits and a bisect lands there.
The golden's own `meta.recorded_by` records **two** prior deviations from this property and names
them as deviations. Re-record `blob_shas` with `git hash-object src/proms/eprom.cpp` on the working
tree **before staging**, and set `recorded_at_head` to the new commit's **parent**.

### Pitfall 6: running the app suite on the wrong interpreter
`python3` here is **3.12.14**; app CI is **3.11 only** and `pyproject.toml` says
`requires-python = ">=3.11"`. A green local run on 3.12 has broken app CI before. Also: `addopts` is
`-ra -q`, so a second `-q` hides the count line — use `-o addopts=""` when you need a count.

### Pitfall 7: gate idioms that fail open
Recorded and still applicable: BRE `\+\+\+`, `;`-chains, OR-grep, `grep -c`, `--stat`, unset-var
`rev-list`, and `grep -qF` with a dash-leading pattern (exits 2 → the gate passes). A new gate must
use none of them. Pitfall 1 above is a live instance of this class, found this session.

### Pitfall 8: pushing to `beta` publishes
`/workspaces/CLAUDE.md`: a push to `beta` in **either** sub-repo cuts a release, and
`firestarter_app`'s cuts to **PyPI**. Neither workflow has a path filter. Milestone work stays on
`v1.41-verification-to-host` in all three repositories. A PyPI version can never be reused.

---

## Code Examples

### The FWCMD-04 source-contract gate — the shape to copy

```python
# Source: firestarter_fw/tests/test_blank_check_region_source_contract.py (house shape)
_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent                      # never os.environ — closes the
_EPROM_REL = "src/proms/eprom.cpp"             # check_permitted_claims.py _HERE landmine

# Concatenation-built so this module cannot match itself (Coverage 9 asserts it).
_NEEDLE_CALL = "memory_verify_exec" + "ute"
_NEEDLE_MODE = "VERIFY_PER_PULSE_PLUS" + "_FINAL"

_ARM_RE = re.compile(
    r"if\s*\(\s*verify_mode\s*==\s*" + _NEEDLE_MODE + r"\s*\)\s*\{"
)
_CALL_RE = re.compile(r"\b" + _NEEDLE_CALL + r"\s*\(\s*handle\s*\)\s*;")

def test_the_final_verify_pass_is_still_called_for_plus_final():
    stripped = _strip_comments(_SCAN_EPROM.read_text())      # shape-preserving: line numbers survive
    span = _function_body_span(stripped, _ARM_RE)            # brace-matched, never line proximity
    assert span is not None, "the VERIFY_PER_PULSE_PLUS_FINAL arm is gone from eprom.cpp"
    body = stripped[span[0]: span[1] + 1]
    assert _CALL_RE.search(body), (
        "the VERIFY_PER_PULSE_PLUS_FINAL arm no longer calls the shared final-pass verify -- "
        "FWCMD-04's whole point is that removing the command surface did NOT remove this call."
    )
```

Pair it with the house's four standard belt-and-braces legs, all of which already exist verbatim in
the seven analogues: a **positive** leg (`eprom_params.cpp` still carries
`VERIFY_PER_PULSE_PLUS_FINAL` for `0x07` and `0x08`), a **non-vacuity** leg (scan targets exist,
non-empty, inside the repo), a **cannot-be-skipped** leg, and an **own-needles-absent** leg.

### Asserting an emitted message id in a native test

```c
/* Source: firestarter_fw/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp:87-118 */
static std::vector<uint8_t> captured_frames;

/* setUp: */
When(OverloadedMethod(ArduinoFake(Serial), write, size_t(uint8_t)))
    .AlwaysDo([](uint8_t b) -> size_t { captured_frames.push_back(b); return (size_t)1; });

/* Walks rurp_log_id()'s fixed layout: 4-byte magic, 2-byte BE length, 1 id byte,
   params, 1 crc byte, 1 anchor byte. Never reads a param count from a lookup table. */
static void sdp_captured_frame_ids(std::vector<uint8_t>* out_ids) {
    size_t offset = 0;
    while (offset + 7 <= captured_frames.size()) {
        uint16_t len_value = (uint16_t)(((uint16_t)captured_frames[offset + 4] << 8)
                                        | captured_frames[offset + 5]);
        size_t frame_size = 4 + 2 + (size_t)len_value + 1;
        if (offset + frame_size > captured_frames.size()) break;
        out_ids->push_back(captured_frames[offset + 6]);
        offset += frame_size;
    }
}

/* The severity-fork assertion pattern -- both directions, so a transposition is caught: */
TEST_ASSERT_TRUE_MESSAGE (sdp_ids_contains(ids, (uint8_t)MSG_ERR_VERIFY), "...");
TEST_ASSERT_FALSE_MESSAGE(sdp_ids_contains(ids, (uint8_t)MSG_ERR_OP_TIMEOUT), "...");
```

### The advancing `millis()` seam

```c
/* Source: firestarter_fw/test/native/avr/test_cobs_cmd_frame/test_cobs_cmd_frame.cpp:134-159 */
static unsigned long millis_counter;
/* setUp: */
millis_counter = 0;
When(Method(ArduinoFake(Function), millis))
    .AlwaysDo([]() -> unsigned long {
        millis_counter += 100;
        return millis_counter;
    });
```

Two ticks of 100 ms past a `millis() + 150` deadline is enough to drive
`flash_util_verify_operation`'s `MSG_ERR_OP_TIMEOUT` exit. Every other native suite pins
`millis()` to a constant 0 (`.AlwaysReturn(0)`), which is why the timeout arm is currently
unreachable there — not because a seam is missing.

### Re-deriving the branch-inventory golden

```python
# Run from firestarter_fw/ with the SWEPT working tree in place, BEFORE staging.
import sys, json; sys.path.insert(0, "tests")
import test_protocol_branch_inventory as m
from pathlib import Path

live = m._extract_predicates(Path("src/proms/eprom.cpp").read_text())
old  = json.load(open("tests/golden/protocol_branch_inventory.json"))

# Prove positional alignment is SAFE before using it (the golden's own instruction).
assert len(old["sites"]) == len(live)
for i, (a, b) in enumerate(zip(old["sites"], live)):
    assert (a["predicate"], a["keyed_on"], a["tier"]) == (b["predicate"], b["keyed_on"], b["tier"]), i
# Only then carry class/reason forward and write the new `line` values.
```

Measured expected outcome for a sweep that touches only `eprom.cpp:56-58`: 22 sites, zero non-`line`
divergences, 20 line shifts of exactly −3, `protocol_keyed_sites` still 1 at line **67**, `counts`
block unchanged.

---

## Runtime State Inventory

This is a removal/refactor phase, so the five categories are answered explicitly.

| Category | Items Found | Action Required |
|---|---|---|
| **Stored data** | **None** — no database, collection name, key or record anywhere stores `CMD_VERIFY`, `CMD_BLANK_CHECK`, `COMMAND_VERIFY` or `COMMAND_BLANK_CHECK`. `chip_database.json` is keyed on `part_number` and carries no command ordinals. Verified by grepping both sub-repos for the four identifiers and by inspecting `constants.py`'s consumers — the only dereference of an ordinal is `COMMAND_NAMES[cmd]` at `eprom_operations.py:584` and `:693`, computed per call. | none |
| **Live service config** | **None** — this project has no n8n/Datadog/Cloudflare surface. The one external service is GitHub (releases + issues), and no release metadata carries a command ordinal. | none |
| **OS-registered state** | **None for the ordinals.** The one OS-level item is the **flashed firmware image on `/dev/ttyACM0`**, which carries the pre-204 dispatch switch until B3 reflashes it. That is the phase's deliberate subject, not a leak. | flash as per §Bench Legs |
| **Secrets/env vars** | **None** reference either ordinal. The env vars in play are test seams only: `FIRESTARTER_BLANK_CHECK_REGION_SCAN_EPROM_SOURCE`, `FIRESTARTER_BRANCH_SCAN_SOURCE`, `FIRESTARTER_BRANCH_SCAN_PARAMS_SOURCE`, `FIRESTARTER_PROGRESS_SCAN_EPROM_SOURCE`, `FIRESTARTER_PROGRESS_SCAN_PIO_CONFIG`, `FIRESTARTER_META_ROOT`, `FIRESTARTER_FW_ROOT`, `FIRESTARTER_SIZE_BASELINE`, `GIT`. **All bind at import time** — a planted-violation run must set them in a child process. | none; but never monkeypatch a seam post-import |
| **Build artifacts / installed packages** | **Three.** (a) `firestarter_fw/.pio/` holds stale native build objects — `pio test` rebuilds, so no action, but a stale `.pio` can mask a header change; (b) `firestarter_app/firestarter.egg-info/` and the editable install — the deleted constants vanish from `constants.py` immediately under `-e`, so no reinstall is needed, but a **sibling worktree does not carry the editable install**; (c) **`~/.firestarter/config.json`**, which does not exist yet and will be created by the first bench run and then **shared between the two hosts**. | snapshot/move `~/.firestarter/` between bench legs; do not run the bench from a worktree |

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|---|---|---|---|---|
| PlatformIO Core | firmware build + `pio test -e native` | ✓ | 6.2.0 | — |
| `avr-gcc` toolchain | `pio run -e leonardo` | ✓ (via PlatformIO packages; the 237-case native run compiled cleanly) | — | — |
| Arduino Leonardo on `/dev/ttyACM0` | all bench legs | ✓ | USB `2341:8036`, `cdc_acm` | none — bench legs are blocking without it |
| Uno-class board | Uno-class FWCMD-06 coverage | ✗ | — | **No fallback.** D-10 states the gap; record it, do not close it |
| Python 3.12 (devcontainer default) | nothing in this phase | ✓ | 3.12.14 | — |
| Python 3.11 | app test suite + the D-08 throwaway venv | ✗ **not installed** | — | `uv python install 3.11` → 3.11.16, verified working |
| `uv` | provisioning 3.11 and the old-host venv | ✓ | at `/usr/local/bin/uv` | `UV_CACHE_DIR` **must** be redirected; `~/.cache/uv` is unwritable |
| PyPI network access | `firestarter==3.0.0b49` | ✓ | wheel resolved and installed | — |
| `pytest` | both repos' Python suites | ✓ in the app's editable env; installed 9.1.1 into the scratch venv for the fw suite | — | — |
| `git` with full history | `test_protocol_branch_inventory`, `test_pr45_non_ancestry`, `test_flash_geometry_recorded_before_linker` | ✓ | — | none — these gates fail closed without it, deliberately |
| Firmware size baseline gate | evidencing the flash reclaim | ✗ | — | `scripts/baseline/size_baseline.json` and `check_size_baseline.py` are **referenced by four modules but do not exist**. Measure `pio run -e leonardo` sizes by hand, before and after |

**Missing dependencies with no fallback:** an Uno-class board (scope-limits FWCMD-06 to Leonardo).
**Missing dependencies with fallback:** Python 3.11 (via `uv`); the size baseline (measure by hand).

---

## Package Legitimacy Audit

This phase installs **one** external package, and only into a throwaway venv for the D-08 bench leg.
No new dependency reaches either sub-repo.

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---|---|---|---|---|---|---|
| `firestarter==3.0.0b49` | PyPI | published `2026-09-13T21:52:13Z` | unknown (PyPI does not expose it to the seam) | `https://github.com/henols/firestarter_app` | **SUS** (`too-new`, `unknown-downloads`) | **Approved with the verdict recorded.** This is *this project's own published artifact*; `repoUrl` resolves to the project's own sub-repo, and D-08 names it explicitly. The heuristic's two reasons are both properties of a fast beta cadence, not of a slopsquat. |

**Packages removed due to `[SLOP]` verdict:** none.
**Packages flagged as suspicious `[SUS]`:** `firestarter` — see the disposition above. **No
`checkpoint:human-verify` is warranted**: the operator chose this artifact by name in D-08, and its
identity was confirmed by reading the installed code (`__version__ == "3.0.0b49"`, and the module
layout matches the sub-repo). The planner should still state in the plan that the install goes into a
**throwaway venv only** and never into the project environment.

`[VERIFIED: gsd-tools query package-legitimacy check --ecosystem pypi firestarter, 2026-09-21; plus reading the installed distribution]`

`pytest==9.1.1` and `cpython-3.11.16` were installed into scratch environments **by this research
session only**, to run the simulation. Neither is a phase dependency.

---

## Validation Architecture

`workflow.nyquist_validation` is `true` in `.planning/config.json`, so this section is required.

### Test Framework

| Property | Value |
|---|---|
| Framework (firmware, tree 1) | PlatformIO + Unity, `platform = native`, `test_framework = unity` |
| Framework (firmware, tree 2) | pytest (source-scan gates), stdlib-only modules, **no `conftest.py` anywhere** (a recorded house rule, not an omission) |
| Framework (host) | pytest with `conftest.py`, `addopts = -ra -q` |
| Config file (firmware) | `firestarter_fw/platformio.ini` — `[native_base]` carries the single `test_filter` and `-I` list |
| Quick run (firmware pytest) | `pytest tests/ -q -o addopts="" -p no:cacheprovider` (~6 s) |
| Quick run (firmware native) | `pio test -e native -f "*test_dispatch*"` (~2 s per suite) |
| Full suite (firmware) | `pio test -e native` **and** `pio test -e native_nodevtools` **and** `pytest tests/ -v` **and** `pio run` — the four `build.yml` steps, in order |
| Full suite (host) | `pytest` on **Python 3.11** |

**Measured baselines (unmodified tree, 2026-09-21):**
- `pio test -e native` → **19 suites, 237 test cases, 237 succeeded, 57.9 s, exit 0**
- `pytest tests/` in a git working tree → all green (the 11 failures I saw are artifacts of a
  non-git scratch copy)

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|---|---|---|---|---|
| FWCMD-01 | ordinals absent from the dispatch switch, `is_memory_cmd`, `configure_memory` | source-scan | `pytest tests/test_<new>_source_contract.py -q` | ❌ Wave 0 |
| FWCMD-01 | `is_memory_cmd` admits exactly seven values | unit (native) | `pio test -e native -f "*test_cmd_admission*"` | ✅ (re-anchor 9→7) |
| FWCMD-02 | both wrappers and declarations gone | source-scan | `pytest tests/test_boolean_convention_source_contract_v133.py -q` (re-anchored 9→7) + the new gate's own absence leg | ✅ (re-anchor) |
| FWCMD-03 | reserved-gap record on both ladders | source-scan | a leg asserting the two gaps and the comment text exist in `firestarter.h` and `constants.py` | ❌ Wave 0 (optional; discretion) |
| FWCMD-04 | `memory_verify_execute` still called for `VERIFY_PER_PULSE_PLUS_FINAL` | source-scan, **planted-RED seen** | `pytest tests/test_<new>_source_contract.py -q` | ❌ Wave 0 |
| FWCMD-05 | `memory_verify_execute` raises `MSG_ERR_VERIFY` (0xAF) | unit (native), id-asserting | `pio test -e native -f "*test_verify_ids*"` | ❌ Wave 0 |
| FWCMD-05 | `eeprom28c_verify_page_readback` raises 0xAF (driven via `eeprom28c_write_execute` — it is `static`) | unit (native), id-asserting | same | ❌ Wave 0 |
| FWCMD-05 | `flash_util_verify_operation` raises `MSG_ERR_OP_TIMEOUT` (0xB7), **not** 0xAF | unit (native), needs advancing `millis()` | same | ❌ Wave 0 |
| FWCMD-05 | per-pulse budget exits raise 0xBD / 0xBE | unit (native), id-asserting | same | ❌ Wave 0 (`test_val_eprom` drives the path already; the **id** assertion is new) |
| FWCMD-06 | retired ordinal → explicit refusal, no hardware effect, no hang | **manual (bench)** — `firestarter.cpp` and `eprom_operations.cpp` are excluded from `build_src_filter`, so **no native test can reach the dispatch switch** | bench steps B5/B6/B7 | n/a |
| REL-02 | post-204 host works against pre-204 firmware | **manual (bench)** | bench step B2 | n/a |
| REL-03 | pre-204 host refused by post-204 firmware, content intact | **manual (bench)** | bench steps B5-B7 | n/a |
| criterion 6 | golden re-derived, diffed field-by-field on `line` | source-scan | `pytest tests/test_protocol_branch_inventory.py -q` (re-anchored `[70]`→`[67]` + blob SHA) | ✅ (re-anchor) |

### Sampling Rate

- **Per task commit:** `pytest tests/ -q -o addopts="" -p no:cacheprovider` in `firestarter_fw` (~6 s), plus `pio test -e native -f "*<touched suite>*"`
- **Per wave merge:** `pio test -e native` + `pio test -e native_nodevtools` + `pytest tests/ -v` + `pio run`; in `firestarter_app`, `pytest` on **3.11**
- **Phase gate:** all four firmware legs green, host suite green on 3.11, and the bench matrix B0-B7 recorded, before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `firestarter_fw/tests/test_<name>_source_contract.py` — FWCMD-04's gate (the eighth). Needs a
      **seen** planted RED.
- [ ] `firestarter_fw/test/native/avr/test_verify_ids/` (name at discretion) — the FWCMD-05 id
      assertions: `test_verify_ids.cpp` + `host_stubs.cpp` + `avr/pgmspace.h` shim.
- [ ] `platformio.ini` — **one** `test_filter` line and **one** `-I` line in `[native_base]`.
- [ ] Re-anchors (not new files): `test_cmd_admission.cpp` (9→7 + truth table), `test_configure_memory.cpp`
      (drop `CMD_VERIFY` **and** the literal `c < 3`; dispose of Case group 5's blank arm),
      `test_val_eprom.cpp` (:387 and :478 — :478 null-derefs), `test_val_nor_unlock.cpp:132`,
      `test_val_eeprom28c.cpp:170`, `test_blank_check_region_source_contract.py` (6→1),
      `test_boolean_convention_source_contract_v133.py` (9→7),
      `test_protocol_branch_inventory.py` (`[70]`→`[67]`) + its golden (blob SHA + 20 line shifts),
      and the three `test_eprom_operations.py` import sites in the host repo.

**Recommendation on the three host guard tests** (`test_no_composed_command_dict_carries_the_verify_ordinal`
and its two siblings): rewrite them to assert against the **literal ordinals 6 and 4** rather than the
deleted symbols. The property those tests protect is about the wire, not about a Python name, so
literals make them *stronger* and keep them alive after the constants are gone. Name the literal in
the assertion message.

**Recommendation on the Phase 201-05 nine-site gate** (the un-discussed discretion item): **re-anchor
it, do not retire it.** Measured: only **one** of its nine legs breaks (Coverage 5, 6→1); the other
eight stay green, including Coverage 3, which is the D-10 fence keeping the region-scoped body at
exactly one call site. Retiring the module would drop that fence for the whole of 204→205, and 205 is
the phase most likely to widen it. The re-anchor is a one-number edit plus a docstring correction;
retirement costs a real guarantee to save nothing.

---

## Security Domain

`security_enforcement` is not set to `false` in `.planning/config.json`, so this section is included.
This is embedded firmware with a serial wire protocol and no network surface; most ASVS categories do
not apply.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---|---|---|
| V2 Authentication | no | no user identity exists on the serial link |
| V3 Session Management | no | the "session" is a single command's INIT/MAIN/END round trip; the leased-session work is Phase 206's |
| V4 Access Control | **yes** | `is_memory_cmd` is explicitly an **access-control gate**, not hygiene — `firestarter.h:108-113` says so. Narrowing it is a security-relevant change |
| V5 Input Validation | **yes** | `json_parser.c` (unchanged here); the dispatch `default:` arm is the fail-closed terminal for an unrecognised ordinal |
| V6 Cryptography | no | none present; the wire uses CRC8 for integrity, not authenticity, and that is unchanged |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation | Status after 204 |
|---|---|---|---|
| A retired ordinal reaching hardware configuration | Tampering / Denial of Service (a 12 V rail on a 5 V part) | `is_memory_cmd` gates `configure_memory`; `configure_memory` is the only setter of `firestarter_operation_init`, and only that pointer engages the VPP regulator | **Improved.** Ordinals 4 and 6 can no longer reach `configure_eprom` at all, so they can no longer reach `eprom_check_vpp` — a path that exists today for ordinal 4 on `0x07` |
| Ordinal reuse silently changing a command's meaning across versions | Spoofing (a stale host speaking a changed protocol) | FWCMD-03's reserved record on both ladders, D-02 | **Addressed by this phase**, provided the gap comments actually land |
| An unrecognised frame hanging the port | Denial of Service | `default:` → `MSG_ERR_UNKNOWN_CMD` → `finished = true` → `command_done()` → `CMD_IDLE`; plus `loop()`'s `timeout < millis()` 1000 ms `MSG_ERR_CMD_TIMEOUT` backstop | **Unchanged and sufficient** — traced in §The Refusal Path |
| Narrowing `is_memory_cmd` weakening the provisional-pinmap guard | Tampering | `rurp_pinmap_refuses(cmd)` delegates to `is_memory_cmd` (`include/rurp_pinmap_guard.h:50-56`) | **Harmless but must be stated.** `rurp_pinmap_refuses(4)` becomes `false`. This only matters under `-D RURP_PINMAP_PROVISIONAL`, which no AVR env defines (`#ifndef RURP_PINMAP_PROVISIONAL` / `#define RURP_PINMAP_PROVISIONAL 0`), and a retired ordinal never reaches `configure_memory` where the guard runs |
| A refused command silently erasing the part | Tampering | D-09's read-back equivalence on a socketed non-blank part | **This is exactly why D-09 rejected the empty socket.** Bench steps B1/B4/B7 |

`[VERIFIED: include/rurp_pinmap_guard.h:41-56 and include/firestarter.h:108-130, read 2026-09-21]`

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact on this phase |
|---|---|---|---|
| `verify` / `blank` push data to the firmware's own ordinals | host-side streaming compare through `compare.py`, driving `COMMAND_READ` | Phase 202 (v1.41, unshipped) | The removal breaks **no** host path — nothing in the working-tree app composes 4 or 6. It **does** break the published `3.0.0b49`, which is the point of REL-03 |
| firmware write-init refuses a non-blank part | host-side write guard | Phase 203 (v1.41, unshipped) | `mem_util_blank_check`'s write-init caller survives 204 and leaves in 205 |
| three tier-`protocol` branch sites pinned at 71/145/218 | **one** site pinned at line 70 | Phase 142 Plan 04 | CONTEXT's "three literal line numbers" trap is stale — see C-1 |
| `#ifdef DEV_TOOLS`-conditional ordinal admission guard | `is_memory_cmd()`, unconditional, enumerating nine names | Phase 151 (LOCK-02) | The sweep takes it to seven; the "nine" appears in a function name, an assertion message and a header comment |
| a `size_baseline.json` / `check_size_baseline.py` flash gate | **gone** | not recorded in-repo; four modules still cite it | The flash reclaim must be measured by hand |
| a `tests/test_revision_constants_parity.py` ladder-parity gate (cited by `constants.py:69`) | **does not exist** | unknown | No automated gate enforces CMD↔COMMAND ladder parity. `/workspaces/CLAUDE.md`'s same-commit-pair rule is the only control |

**Deprecated/outdated in the docs, needing repair while here:**
- `firestarter_fw/CLAUDE.md`: "a `switch (handle->cmd)` assigns the main operation for `CMD_READ`,
  `CMD_WRITE` and `CMD_VERIFY`" and "which is four new lines" (measured: two).
- `include/firestarter.h:108-110`: "All nine named macros" and "A source-scan gate checks this" (no
  such gate found).
- `firestarter_app/firestarter/constants.py:62-69`: names a non-existent test module and two stale
  line numbers.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|---|---|---|
| A1 | The app writes `~/.firestarter/config.json` regardless of `FIRESTARTER_CONFIG_DIR` in `3.0.0b49` specifically. Carried from the project memory record; the directory does not exist on this machine so the behaviour could not be observed without running the CLI. | Bench Legs | The two hosts share config during the bench; a stale port or chip entry could confuse a leg. Mitigation is cheap: snapshot and restore `~/.firestarter/` between legs regardless |
| A2 | The published `3.0.0b34` firmware `.hex` asset exists and carries the pre-204 dispatch switch. Not fetched this session; inferred from the working tree reading `3.0.0b33` and the memory record of the v1.40 beta cut. | Bench Legs | If the asset is missing or zero-asset (a recorded `beta-build` failure mode), fall back to a local `pio run -e leonardo` at sha `e5842d8` — which is the more honest choice anyway, since it is exactly the pre-204 source |
| A3 | `eeprom28c_verify_page_readback`'s mismatch arm can be driven from a native test through `eeprom28c_write_execute` with a stubbed read-back. The function is `static` and I did not build such a test. | Validation Architecture | If it turns out unreachable without a `HOST_STUBS_CUSTOM_READ_DATA_BUFFER`-style stateful read stub, the leg costs more than estimated. The opt-out already exists in `_shared/host_stubs_common.inc`, so the path is known |
| A4 | The post-204 firmware build fits the Leonardo's 28672-byte ceiling. A pure removal can only shrink, but I did not run `pio run -e leonardo` before and after. | Environment Availability | Near-zero risk in the shrink direction; measure anyway, since the milestone premise is flash reclaim and no gate measures it |
| A5 | `pio run -e leonardo` / `pio run -t upload` work against `/dev/ttyACM0` from inside this devcontainer. USB passthrough is recorded as working and the port is visible, but I ran no upload. | Bench Legs | If upload fails, every bench leg is blocked. Probe this **first**, before writing any bench plan detail |
| A6 | The two catalog comments (D-06) can be added to `tools/catalog/messages.toml` without triggering codegen or a sub-repo sync. Comments should be inert to the emitter, but I did not run codegen to confirm. | User Constraints / D-06 | If a comment changes generated output, 204 becomes a three-repo phase — exactly what D-06 exists to avoid. Verify by running codegen and diffing `messages.h`/`messages.py` before committing |

---

## Open Questions

1. **Does the `pio` upload path work from this devcontainer?**
   - What we know: `/dev/ttyACM0` exists with `crw-rw-rw-` permissions; `pio` 6.2.0 is installed; the
     project memory records USB passthrough as working for bench drives and flashes.
   - What's unclear: no upload was attempted this session.
   - Recommendation: make "flash the board once, round-trip a `read`" the plan's **first** bench task,
     before any of B1-B7, so a passthrough problem surfaces before the matrix is designed around it.

2. **One commit or two for the firmware sweep?**
   - What we know: the golden's one-commit property wants the source change and the golden in the same
     commit. The sweep also breaks two *other* gates (G1, G2) that live in the same test tree.
   - What's unclear: whether landing all of it — 19 source sites, 7 native test files, 3 pytest
     modules, 1 golden — in one commit is reviewable.
   - Recommendation: **one commit** for the firmware sweep plus every gate re-anchor and the golden
     re-derive, so the tree is green at every boundary and a bisect never lands RED. Then the paired
     host commit. State the size in the commit message and enumerate which gate moved and why, per
     `meta.how_to_update`.

3. **What happens to `test_configure_memory.cpp` Case group 5's blank-check arm?**
   - What we know: it asserts `configure_sram` leaves `firestarter_operation_main` NULL for
     `CMD_BLANK_CHECK`, and its own message says "correct Phase 120 disposition is KEEP".
   - What's unclear: after 204 it is a statement about an ordinal that no longer exists; it would pass
     vacuously.
   - Recommendation: delete the blank arm and say so in the phase record, keeping the `CMD_ERASE` and
     `CMD_CHECK_CHIP_ID` arms. Do not leave a vacuous assertion carrying a "KEEP" rationale that no
     longer applies.

4. **Should the `region-end` guard become `cmd == COMMAND_WRITE` or keep a one-member tuple?**
   - What we know: `eprom_operations.py:628` is `and cmd in (COMMAND_WRITE, COMMAND_VERIFY)`, and the
     surrounding comment block (`:614-624`) cites BLANK-01 / D-05 and the firmware's region-scoped
     blank check — **which Phase 205 removes**.
   - Recommendation: `cmd == COMMAND_WRITE`, and rewrite the comment rather than trimming it. A
     one-member tuple invites someone to "restore" a second member. Also flag that the comment's own
     premise expires in 205, so 205 will revisit this block again.

5. **Is the flash reclaim worth reporting at 204 at all?**
   - What we know: the milestone premise is reclaiming AVR flash, but Phase 205 owns the measured
     deltas (its criterion 4). No size gate exists.
   - Recommendation: record `pio run` sizes for uno/uno328pb/leonardo before and after **in the 204
     phase record** as a data point, without claiming it as a requirement. 205's criterion 4 then has
     a real 204 baseline rather than a 201-era one.

---

## Sources

### Primary (HIGH confidence) — the live tree, read this session

- `firestarter_fw/include/firestarter.h` (:40-130), `src/firestarter.cpp` (:60-100, :114-217, :262-345),
  `src/eprom_operations.cpp` (:1-95), `include/eprom_operations.h` (whole file),
  `src/operation_utils.cpp` (:85-150, :210-265), `src/proms/memory.cpp` (:55-95, :370-400, :480-545),
  `src/proms/eprom.cpp` (:40-70, :440-510), `src/proms/eeprom_28c.cpp` (:130-160, :505-540),
  `src/proms/flash_utils.cpp` (:1-60), `src/proms/flash_nor_unlock.cpp`, `flash_intel.cpp`,
  `flash_5v_page.cpp` (the `CMD_BLANK_CHECK` arms), `include/messages.h`, `include/eprom_params.h`,
  `src/proms/eprom_params.cpp`, `include/rurp_pinmap_guard.h`, `platformio.ini`, `CLAUDE.md`,
  `PROTOCOLS.md`
- `firestarter_fw/tests/` — `test_protocol_branch_inventory.py` (+ its golden's `meta`, `counts`,
  `sites`), `test_blank_check_region_source_contract.py`, `test_boolean_convention_source_contract_v133.py`,
  `test_write_path_source_contract_v131.py`, `test_progress_emission_is_leonardo_only.py`,
  `test_golden_trace_identity.py`
- `firestarter_fw/test/native/avr/` — `test_cmd_admission/`, `test_dispatch/test_configure_memory.cpp`,
  `test_val_eprom/`, `test_val_nor_unlock/`, `test_val_eeprom28c/`, `test_eeprom28c_sdp/`,
  `test_cobs_cmd_frame/`, `test_cobs_data_frame/`, `_shared/host_stubs_common.inc`
- `firestarter_app/firestarter/constants.py`, `eprom_operations.py`, `codec.py`;
  `firestarter_app/tests/test_eprom_operations.py`, `test_erase_blank_step_nonregression.py`;
  `firestarter_app/pyproject.toml`, `.github/workflows/*.yml`
- `/workspaces/tools/catalog/messages.toml` (:511-519)
- `/workspaces/CLAUDE.md`, `/workspaces/.planning/REQUIREMENTS.md`, `/workspaces/.planning/ROADMAP.md`
- The installed `firestarter==3.0.0b49` distribution (`constants.py`, `eprom_operations.py`,
  `messages.py`, `sdp_honesty.py`)

### Primary (HIGH confidence) — executed this session

- `pio test -e native` on the unmodified tree → 19 suites / 237 cases / 237 succeeded / 57.9 s / exit 0
- `pytest tests/` on a **swept** scratch tree vs. an identical **control** → 15 vs. 11 failures; the
  4-leg delta in §Gate Impact
- `test_protocol_branch_inventory._extract_predicates()` run over the swept `eprom.cpp` → 22 sites,
  `protocol_lines == [67]`, 20 shifts of −3, zero non-`line` divergences
- `test_blank_check_region_source_contract` legs run individually over the swept tree → 1 failure of 9
- `uv python install 3.11` → 3.11.16; `uv venv --python 3.11`; `uv pip install firestarter==3.0.0b49`
- `gsd-tools query package-legitimacy check --ecosystem pypi firestarter` → SUS / too-new,
  unknown-downloads
- `/dev` and `/sys/bus/usb/devices` sweep → `2341:8036 Arduino Leonardo` on `/dev/ttyACM0`
- `grep -rn --no-ignore …` vs. the plain form → 0 vs. 32 matches; ugrep's rejection text captured

### Secondary (MEDIUM confidence)

- `204-CONTEXT.md` — the locked decisions, reproduced verbatim above. Three of its structural claims
  are corrected in §Gate Impact (C-1, C-2) and §Measured Site Census (the un-listed sites); its
  decision content stands unchanged.
- Project memory records for the devcontainer Python skew, the `~/.firestarter/config.json` behaviour,
  the `_probe_port` prerelease truncation, the Leonardo flash ceiling, and the beta-publishing rule.

### Tertiary (LOW confidence)

- None. No web search was needed or performed: every question in this phase is answerable from the
  repository, and a web result would have been weaker evidence than the file.

---

## Metadata

**Confidence breakdown:**

- **Site census:** HIGH — every line quoted verbatim from a file opened this session.
- **Gate impact:** HIGH — measured by running the real suites against a real swept tree beside a
  control, not predicted. The 4-leg delta is reproducible.
- **D-03 amendment evidence:** HIGH — all five raise sites read, all four message ids read from
  `messages.h`.
- **Refusal path (FWCMD-06):** HIGH for the firmware trace and the message format on both sides;
  MEDIUM for the exact user-visible CLI rendering, which depends on the old host's log formatting and
  was not executed against hardware.
- **Proof-instrument feasibility (D-04):** HIGH for the source-contract gate and for the id-capture
  and `millis()` seams (working in-tree precedents); MEDIUM for
  `eeprom28c_verify_page_readback`'s drivability (A3).
- **Bench artifacts:** HIGH for the rig identity, the 3.11 venv and the `3.0.0b49` command
  composition — all executed; MEDIUM for the upload path (A5) and the `3.0.0b34` asset (A2).
- **Architecture patterns:** HIGH — seven existing source-contract modules and one id-asserting
  native suite give an unambiguous house shape.

**Research date:** 2026-09-21
**Valid until:** 2026-10-21 for the patterns and the environment; **invalidated by the first commit
that edits `src/proms/eprom.cpp`** — every line number in §Gate Impact and the `[67]` re-anchor is
computed against `firestarter_fw` HEAD `e5842d8` with that file untouched.
