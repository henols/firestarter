# Phase 183: Flash4 Erase Refusal & the AE29F2008 Classification - Research

**Researched:** 2026-09-11
**Domain:** Host-side CLI policy gates (Python/Click), AVR firmware dead-code deletion + flash budgeting, upstream chip-database provenance
**Confidence:** HIGH

> **Provenance note.** Every in-repo claim below was verified by `Read`/`sed` against the working tree
> **in this session**, and cited by `path:line-range` with the values quoted verbatim. The firmware
> submodule was at `c14f191`, clean, **0 commits ahead of `origin/beta` and 2 behind**; the only file
> differing between HEAD and `origin/beta` is `include/version.h`
> (`git diff --stat HEAD origin/beta` → `include/version.h | 2 +-`), so **every firmware line citation
> in this document also holds on `origin/beta`** [VERIFIED: measured this session].

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

Copied verbatim from `183-CONTEXT.md` § Implementation Decisions. **None of these is re-opened by this
research.** Where research found a decision's *supporting statement* to be imprecise, that is flagged as a
correction to the statement, never to the decision.

- **D-01:** SAFE-07 prices **all three** candidate mechanisms, not the two SAFE-07 names alone. The third is a **host pre-flight policy gate** — the pattern already shipped twice in this repo (`sdp_capability.py`, `jp5_gate.py`). Excluding the option the repo already uses twice would make D-3's pricing incomplete. The phase record states every figure and why the winner won.
- **D-02:** If a host-side refusal wins, it fires **before the serial port is opened** — the `sdp_capability.py` contract verbatim ("enforced by the caller before the serial port is even opened"). The operator must not see `Connecting... OK` followed by a refusal; that sequence is what read as a malfunction in gh#62.
- **D-03:** The refusal's reasoning lives in **its own policy module** — a third sibling to `sdp_capability.py` and `jp5_gate.py`: pure predicate, no I/O, no serial access, unit-testable with no board. It must NOT be folded into either existing module. It must NOT be inlined in `cli_handlers.erase`.
- **D-04:** **Firmware keeps refusing.** The host gate is the operator-facing refusal; `eprom_erase`'s `MSG_ERR_NOT_SUPPORTED` stays as the backstop. Defence in depth, not a replacement.
- **D-05:** **Scope is flash4 (`0x05`) only.**
- **D-06:** **Exit 1 by default; exit 0 only behind an explicit flag.**
- **D-07:** **The message is ONE LINE and nothing more** — of the shape `Erase not supported for <EPROM>`. It carries **no cause**, **no alternative**, and **no literal `firestarter write` command**.
- **D-08:** **Three documents must be amended by this phase to match D-07** — `.planning/REQUIREMENTS.md` § SAFE-06, `.planning/ROADMAP.md` Phase 183 **Goal**, `.planning/ROADMAP.md` Phase 183 **success criterion 1**. This is a deliverable, not a side effect.
- **D-09:** **The cause and the alternative are not lost — they move to REPLY-03** (Phase 187).
- **D-10:** **The CLI does not warn about the forged-identity `--force` workaround.** That warning is REPLY-03's alone.
- **D-11:** D-07 **weakens the new-firmware-id candidate specifically**. The three-way pricing in D-01 still runs as specified. A researcher or planner must not skip the measurement on the strength of this note.
- **D-12:** **Delete all of it:** `configure_flash_5v_page`'s `CMD_ERASE` arm, `flash_5v_page_erase_execute` itself, and `flash_5v_page_write_init`'s `is_flag_set(FLAG_CAN_ERASE)` erase-on-write block.
- **D-13:** **Precision required in the phase record.** The arm's *assignment* DOES execute; it is the *function pointer* that never fires.
- **D-14:** **`scripts/check_erase_no_vpp.py` is this phase's to fix.** Re-cite by **symbol and enclosing scope, never a line number**; update the "proximity, not absence" rationale; keep the gate armed.
- **D-15:** **Phase 185's baseline re-record now depends on Phase 183.** Amend the ROADMAP. A *shrink* authors **no new MERGE-05 exemption**.
- **D-16:** **The SAFE-07 measurement is a cold build of all three AVR targets**: `rm -rf .pio/build/<env>` then exactly one `pio run -e <env>`, for `uno`, `uno328pb` and `leonardo`. **Leonardo is the figure that decides D-3.**
- **D-17:** **Watch for tests going vacuous.** `test_val_5v_page.cpp`'s ERASE-02 cases must be adjudicated here, not left for a later sweep.
- **D-18:** **Datasheet-by-equivalence is acceptable evidence, AND the upstream `infoic.xml` row must be checked too.** The verdict must name itself as equivalence-based, never as a direct AE29F2008 datasheet reading.
- **D-19:** **Expected verdict — classification CORRECT — with the reporter also correct.** Stated as a projection to be falsified, NOT as a conclusion research may assume.
- **D-20:** **On the CORRECT branch, the software chip-erase is recorded and BACKLOGGED, not built.**
- **D-21:** **On the MISCLASSIFIED branch, the override mechanism is the Phase 182 named-root-cause-rule pattern.** A per-part exception table is **rejected**. `chip_database.json` is never hand-edited (D-6).
- **D-22:** **`support_status` for AE29F2008 is UNTOUCHED.**
- **D-23:** **One thing in the same row that looks wrong, for research to settle, not to fix blind:** `"vpp_mv": 12000` on a 5-volt-only part. If it proves live, it is a **new finding** — file it; do not widen this phase to fix it without an explicit scope decision.

### Claude's Discretion

> The operator expressed no preference on four items; the orchestrator's recommendation was taken and is
> recorded above as a decision rather than left open — **D-14**, **D-15**, **D-16** and **D-22**. Any of
> these may be revisited by the operator; a planner should treat them as locked.
>
> Wording of the one-line refusal (D-07) beyond its shape is planner discretion, provided it carries no
> cause, no alternative and no `--force` clause.

### Deferred Ideas (OUT OF SCOPE)

- **VPP-reroute confirmation gate for parts needing JP4's third position** (a different hazard on a different jumper; blocked on a database-derived predicate that does not exist).
- **Generalize the refusal beyond flash4** (D-05's other half; reuse `chip_test.py`'s per-family reason strings).
- **Software chip-erase for the `0x05` family** (D-20; excluded by milestone boundary; template is `eeprom28c_erase_execute`).
- **`vpp_mv: 12000` on a 5 V-only part** (D-23; see §SAFE-09 D-23 below — **settled as NOT a hardware-live defect**, with a residual display-labelling question filed at a wider scope than this row).
- **Reviewed Todos (not folded):** `todo.match-phase 183` returned 35 candidates and no genuine matches.

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description (verbatim from REQUIREMENTS.md) | Research Support |
|----|-------------|------------------|
| **SAFE-06** | "A refusal to erase a flash4 (`0x05`) part states its cause and its alternative — the part self-erases per page during the write, so `erase` is unnecessary rather than unavailable — instead of a bare `Not supported`." **(This text is amended by this phase per D-08.)** | §D — exact call site, predicate field, data path, module contract, flag naming, test template. |
| **SAFE-07** | "The firmware-flash cost of SAFE-06 is measured before the mechanism is chosen, and the zero-firmware-byte alternative (host-side text against the existing `MSG_ERR_NOT_SUPPORTED`) is priced against a new `messages.toml` id. The decision and both figures are recorded. (D-3)" | §A — the three mechanisms specified to the edit level, the measurement procedure verified runnable in this devcontainer, and the leonardo headroom claim measured. |
| **SAFE-08** | "`configure_flash_5v_page`'s `CMD_ERASE` arm — unreachable while the host clears `FLAG_CAN_ERASE` for every `0x05` part — is adjudicated explicitly: removed as dead weight, or kept with the reason it is kept recorded. It is not left undecided." | §C — all three deletion sites re-cited by symbol, a **complete** blast-radius list (CONTEXT's list was short by 6 sites), and the D-17 vacuity verdict with a recommended disposition. |
| **SAFE-09** | "Whether AE29F2008 is correctly classified `algorithm 5` is investigated against its datasheet and the reporter's evidence… The conclusion is recorded either way; any correction lands in `build_db.py`, never in `chip_database.json`. (D-6)" | §B — D-19's projection **tested and confirmed on every leg**, with upstream `infoic.xml` re-fetched and the W29C020C datasheet text-extracted. |

</phase_requirements>

---

## Summary

**SAFE-09 is answered and it does not generate code.** D-19's projection survived every falsification
attempt. The upstream pinned `infoic.xml` was re-fetched (HTTP 200, 17,861,009 bytes) and the ASD
`AE29F2008@DIP32` row reads `protocol_id="0x05"` verbatim — the `algorithm 5` classification is an
**upstream transcription, not a generator decision**, so there is nothing in `build_db.py` to fix. Better
than that: the upstream `WINBOND` row `W29C020,W29C020C,W29C022` is **field-for-field identical to the ASD
row on all thirteen decode-relevant attributes**, including the same `chip_id="0x0000da45"` — upstream's
own database declares the two parts the same silicon, which turns D-18's equivalence chain from an
inference into an upstream-declared identity (still equivalence-based, exactly as D-18 requires). The
W29C020C datasheet, extracted to text in this session, confirms every DB field and every reporter
observation. **Take the D-19/D-20 branch. D-21's misclassification branch does NOT fire: no
`build_db.py` rule, no regeneration, no `chip_database.json` diff, no `diff_db.py` run, no
`DECODE-NOTES.md` edit.**

**SAFE-08's blast radius is larger than CONTEXT recorded, and one consequence of D-12 is unadjudicated.**
CONTEXT named four affected sites; research found **six more**, including a second and third copy of the
same impossible `flash_5v_page.cpp:196-231` citation. Two of D-12's three line ranges are off by one
against the current tree. And after D-12, `flash_5v_page_write_init`'s body becomes *entirely
inert* — an `if` wrapping only an early `return` — which the planner must adjudicate (keep the empty stub,
or null the init pointer too, which would segfault `test_val_5v_page.cpp:332`'s unguarded
`h.firestarter_operation_init(&h)` call).

**SAFE-06's host gate has a cleaner data path than CONTEXT assumed.** `resolve_chip`'s returned dict
already carries `"algorithm"` — the same `protocol-id` value, under a different key
(`database.py:532`) — at the exact call site, before the serial port opens. The new module needs no
second DB lookup and no name-keyed `db` injection: it takes the wire dict, exactly like `jp5_gate`.
`erase`'s Click handler is a five-line body with the insertion point already obvious.

**Primary recommendation:** Plan five strands — (1) the new `flash4_erase_gate.py` sibling module plus its
test file and the `cli_handlers.erase` wiring with a new `--ignore-unsupported` flag; (2) the three-way
SAFE-07 cold-build measurement (the toolchain **is** present and working in this devcontainer); (3) the
`flash_5v_page.cpp` triple deletion with its full ten-site cascade; (4) the D-08 record amendments plus
D-15's Phase 185 dependency edit; (5) a SAFE-09 verdict record with **no code change**. Add a Wave-0 task
creating the missing firmware milestone branch.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Flash4 erase refusal (operator-facing) | **Host — policy module** (`firestarter_app/firestarter/flash4_erase_gate.py`, new) | Host — CLI (`cli_handlers.erase`) prints + exits | D-03 puts the reasoning in its own pure module; D-02 puts it before the port opens. The host already holds the whole input (`algorithm`) pre-connect. |
| Flash4 erase refusal (bypass backstop) | **Firmware — op layer** (`eprom_operations.cpp` `eprom_erase`) | — | D-04. Unchanged by this phase. |
| `FLAG_CAN_ERASE` derivation for algo 5 | **Host — database layer** (`database.py` `convert_to_programmer`) | — | Already the single derivation site; the new predicate keys on the same value so the two cannot drift. |
| 12 V bulk-erase routine for a 5 V part | **Deleted** (was Firmware — `flash_5v_page.cpp`) | — | D-12. Nothing calls it; the hazard stops existing rather than standing one policy line away from silicon. |
| Chip classification (`algorithm`) | **Upstream `infoic.xml`** → `build_db.py` transcription | — | Measured: `classify()` returns `proto_id` unchanged for `{0x05,0x06,0x0D,0x10}`. The host never decides algorithm 5. |
| Exit-code contract | **Host — CLI** (`sys.exit`) | — | D-06. A published contract; scripts depend on it. |
| Firmware flash budget | **Firmware — build** (`check_size_baseline.py` / `size_baseline.json`) | — | D-15/D-16. The default gate is byte-identity, so *any* firmware delta reddens it. |

---

## A. SAFE-07 — the three-way mechanism pricing (D-01, D-11, D-16)

### A.1 The three mechanisms, specified to the edit level

SAFE-07's own wording names two; D-01 adds the third. Read carefully, **SAFE-07's two are not the two a
planner would guess** — the second one is *post-connect host rendering*, which is a different thing from
D-01's *pre-connect host gate*:

> "the zero-firmware-byte alternative (**host-side text against the existing `MSG_ERR_NOT_SUPPORTED`**) is
> priced against a **new `messages.toml` id**" [VERIFIED: `.planning/REQUIREMENTS.md:77-79`, quoted
> verbatim]

| # | Mechanism | Where it fires | What must be written | Firmware bytes (a priori) |
|---|-----------|----------------|----------------------|---------------------------|
| **M1** | New firmware message id + `handle->protocol` compare-and-branch | Firmware, post-connect | 1 new `[[messages]]` entry in `/workspaces/tools/catalog/messages.toml`; `bash tools/catalog/sync_to_subrepos.sh`; regenerate `firestarter/include/messages.h` + `firestarter_app/firestarter/messages.py`; edit `eprom_erase` to branch on `handle->protocol == PROTO_FLASH_5V_PAGE` | **> 0 — MUST BE MEASURED** |
| **M2** | Host renders better text against the **existing** `0xA5` | Host, post-connect | Only `firestarter_app` — special-case id `0xA5` at the erase render site | **0 by construction** |
| **M3** | Host pre-flight policy gate (D-01) | Host, **pre-connect** | New `flash4_erase_gate.py` + test file + `cli_handlers.erase` wiring. Firmware untouched | **0 by construction** |

**Facts that make M1's cost specifically the branch, not the id** [all VERIFIED this session]:

- `MSG_ERR_NOT_SUPPORTED` is id `0xA5`, `severity = "ERROR"`, `format = "Not supported"`, `params = []`,
  `wire_format = "id_frame"` [VERIFIED: `/workspaces/tools/catalog/messages.toml:459-465`, quoted
  verbatim]. `id_frame` means the firmware transmits **only the id byte** — the format string lives on the
  host. A *new id used at an existing call site* therefore costs ≈0 firmware bytes (one `ldi` immediate
  changes value).
- The catalog is **meta-repo authoritative**: *"Distribution: copied byte-identically into
  `firestarter/tools/catalog/` and `firestarter_app/tools/catalog/` by `tools/catalog/sync_to_subrepos.sh`.
  Edit ONLY this meta-repo copy; run the sync script after every edit."* [VERIFIED:
  `/workspaces/tools/catalog/messages.toml:6-8`, quoted verbatim]. The catalog holds **131** `[[messages]]`
  entries [VERIFIED: `grep -c '^\[\['` = 131].
- The refusal site is protocol-blind today:
  ```c
  bool eprom_erase(firestarter_handle_t* handle) {
      LOG_DEBUG_ID_SUB(DBG_ERASE_PROM);
      if (!is_flag_set(FLAG_CAN_ERASE)) {
          LOG_ERROR_ID(MSG_ERR_NOT_SUPPORTED);
          return true;
      }
      return op_execute_simple_operation(handle);
  }
  ```
  [VERIFIED: `firestarter/src/eprom_operations.cpp:34-41`, quoted verbatim]. It fires for **every** part
  without `FLAG_CAN_ERASE` — UV-EPROM and SRAM included — so a flash4-specific id needs a
  compare-and-branch that does not exist. **That branch is the figure D-16 measures.**
- `PROTO_FLASH_5V_PAGE` exists as a named constant: `#define PROTO_FLASH_5V_PAGE 0x05` [VERIFIED:
  `firestarter/include/proto_constants.h:11`, quoted verbatim], and `handle->protocol` is a live handle
  field: `uint8_t protocol;` [VERIFIED: `firestarter/include/firestarter.h:173`, quoted verbatim]. So M1
  needs no new constant.

**M1 and M2 both violate D-02.** Both fire after `Connecting... OK` — the exact sequence gh#62's reporter
read as a malfunction. D-01 still requires all three priced; the decision record should cite the figures
**and** D-02, not the figures alone.

**A correction to D-11's supporting statement (not to D-11).** D-11 says the chip name "is host-side
context the firmware does not carry at the refusal site." True of the *firmware*. But because
`wire_format = "id_frame"` puts all rendering on the host, the host **does** have the chip name in scope
when it renders id `0xA5`, so M2 could in principle print `Erase not supported for AE29F2008`. D-11's
conclusion still holds for M1 (a *new* id buys nothing the host could not already do with the old one) —
which is a sharper argument than the one D-11 states, and strengthens rather than weakens it.

### A.2 The measurement procedure (D-16) — verified correct and runnable

D-16's procedure is documented by `size_baseline.json`'s own `meta`:

> "…each `rm -rf .pio/build/<env>` then exactly one `pio run -e <env>` invocation."
> [VERIFIED: `firestarter/scripts/baseline/size_baseline.json` → `meta.generated_by`, quoted verbatim]

**Environment availability — measured this session, NOT assumed:**

| Dependency | Available | Evidence |
|---|---|---|
| `pio` / `platformio` | ✓ | `/usr/local/bin/pio`, `/usr/local/bin/platformio` |
| `toolchain-atmelavr` | ✓ | `~/.platformio/packages/toolchain-atmelavr/bin/avr-gcc --version` → `avr-gcc (GCC) 7.3.0` — matches `meta.avr_gcc = "7.3.0"` |
| `framework-arduino-avr`, `framework-arduino-avr-minicore` | ✓ | present in `~/.platformio/packages` |
| Prior build dirs for all three envs | ✓ | `.pio/build/{uno,uno328pb,leonardo}` all exist |
| `pio test -e native` | ✓ green | Run this session: **184 test cases: 184 succeeded in 00:01:21** — matches `size_baseline.json` → `native_envs.native = {"cases": 184, "succeeded": 184, "suites": 17, "all_passed": true}` |

**The AVR builds are runnable here.** The planner may author the D-16 cold builds as ordinary executor
tasks. Per the research brief I did **not** run them.

**Toolchain-pin caveat for the planner.** `meta` pins `platformio_core = "6.1.19"`; the installed `pio`
prints *"There is a new version 6.2.0 of PlatformIO available."* The pin is recorded metadata, not an
enforced constraint, but a comparison against `size_baseline.json` is only honest if the toolchain matches
the recorded pins (`platform_atmelavr 5.2.0`, `toolchain_atmelavr 1.70300.191015`, `avr_gcc 7.3.0`,
`framework_arduino_avr 5.3.0`, `framework_arduino_avr_minicore 3.1.2`) [VERIFIED: `meta`, quoted]. A task
should record the observed versions alongside the figures.

### A.3 The "Leonardo has 0 B headroom" claim — MEASURED, and it needs restating

D-16 says *"Leonardo is the figure that decides D-3 (0 B flash and 0 B RAM headroom since v1.32 Phase
153)."* That is true **of the MERGE-05 band literal** and **false of the measured position**. Both halves
matter to the decision:

| Target | BASE-01 `flash_used` | live baseline `flash_used` | delta vs BASE-01 |
|---|---|---|---|
| uno | 24824 | 22952 | **−1872** |
| uno328pb | 24874 | 23000 | **−1874** |
| leonardo | 26906 | **25098** | **−1808** |

| Target | BASE-01 `ram_used` | live baseline `ram_used` | delta |
|---|---|---|---|
| leonardo | 2014 | **1875** | **−139** |

[VERIFIED: `firestarter/scripts/baseline/size_baseline_base01.json` → `avr_targets` and
`firestarter/scripts/baseline/size_baseline.json` → `avr_targets`, both read this session; live leonardo
row reads `{'flash_used': 25098, 'flash_total': 32768, 'flash_free': 7670, 'ram_used': 1875,
'ram_total': 2560, 'ram_free': 685}`]

- The **0 B** figure is the MERGE-05 *base band* literal: `band = 0 if env == "leonardo" else
  MERGE05_UNO_CLASS_FLASH_BAND` [VERIFIED: `firestarter/scripts/check_size_baseline.py:607`, quoted
  verbatim], with `MERGE05_UNO_CLASS_FLASH_BAND = 64` [VERIFIED: `:155`].
- Against that band, leonardo currently sits **1808 B below** BASE-01, with **724 B** of named exemptions
  stacked on top and unused. **Nothing in this phase is going to hit a flash cliff.**
- The Caterina-safe boundary on leonardo is `28672`; at `25098` the budget is **3574 B** (was 1042 B when
  `merge05_clause` was written at `27630`) [VERIFIED: the `28672` literal appears in
  `size_baseline.json`'s `merge05_clause`, quoted; the arithmetic is mine].

**Planner consequence:** D-16's measurement stays mandatory (it is SAFE-07's deliverable and D-3's
requirement), but a planner should **not** expect the leonardo figure to eliminate M1 on budget grounds.
D-02 is the constraint that decides this, not flash.

**`meta` prose is stale in this file.** `meta.native_case_count_revision_260822` asserts *"the avr_targets
flash_used/ram_used figures below still record the PRE-change position (uno 25548, uno328pb 25598,
leonardo 27630)"* — but the file's actual `avr_targets` now read 22952/23000/25098. The prose and the data
disagree. That is **Phase 185's CLAIM-04/05 work, not this phase's**; flagged so a 183 executor does not
try to reconcile it.

### A.4 What the winner's implementation looks like (M3)

See §D. M3 costs **0 firmware bytes** and is the only candidate that satisfies D-02.

---

## B. SAFE-09 — the AE29F2008 classification verdict (D-18, D-19, D-21, D-23)

### B.1 The DB row, verbatim

```json
{
  "electrical": {
    "pin_count": 32, "size_bytes": 262144, "type": "Flash/EEPROM",
    "vcc_mv": 5000, "vdd_mv": 5000, "vpp_mv": 12000
  },
  "part_number": "AE29F2008",
  "pinout": "DIP32_SST39SF040",
  "programming": {
    "algorithm": 5, "chip_id_check": true, "chip_id_value": "0x0000da45",
    "infoic_page_size_raw": 128, "protect_off_before": true,
    "protect_on_after": true, "pulse_duration_us": 0
  },
  "support_status": "supported"
}
```
[VERIFIED: `firestarter_app/firestarter/data/chip_database.json` → vendor `ASD`, read and dumped this
session. Every field above is quoted verbatim from that dump.]

### B.2 The upstream `infoic.xml` row — re-fetched, not inferred

`build_db.py` pins the source:
```python
MINIPRO_XML_URL = (
    "https://gitlab.com/DavidGriffith/minipro/-/raw/"
    "a8efaedc236c1d9718bd28299dfbb99536b010ff/infoic.xml"
)
```
[VERIFIED: `firestarter_app/tools/build_db.py:14-17`, quoted verbatim]

Fetched this session: **HTTP 200, 17,861,009 bytes**, sha256
`cdd21319ae6cce2316ca2361a9fb82cba89b27b66bb78d58b01032a441106b8a`. The `ASD` manufacturer block begins at
line 17555 (`name="ASD"`); the `AE29F2008@DIP32` record:

```xml
<ic
    name="AE29F2008@DIP32"
    type="1"
    protocol_id="0x05"
    variant="0x7500"
    read_buffer_size="0x1000"
    write_buffer_size="0x80"
    code_memory_size="0x40000"
    data_memory_size="0x00"
    data_memory2_size="0x00"
    page_size="0x0080"
    pages_per_block="0x0000"
    chip_id="0x0000da45"
    voltages="0x0000"
    pulse_delay="0x2710"
    flags="0x0040c078"
    chip_info="0x0000"
    pin_map="0x0000190b"
    package_details="0x20000000"
    config="NULL"
/>
```
[VERIFIED: pinned `infoic.xml` @ `a8efaedc`, lines 17642-17662, quoted verbatim]

**The generator invents nothing.** `classify()`'s flash branch returns `proto_id` unchanged:
```python
    # 4. Flash families.
    if proto_id in {0x05, 0x06, 0x0D, 0x10}:
        return "Flash/EEPROM", proto_id, pinout_key
```
[VERIFIED: `firestarter_app/tools/build_db.py:355-357`, quoted verbatim]. So `algorithm: 5` **is**
upstream's `protocol_id="0x05"`, transcribed. There is no decode step to be wrong.

### B.3 The equivalence chain, closed at the source

The upstream `WINBOND` block carries:

```xml
<ic
    name="W29C020,W29C020C,W29C022"
    type="1"
    protocol_id="0x05"
    variant="0x7500"
    read_buffer_size="0x1000"
    write_buffer_size="0x80"
    code_memory_size="0x40000"
    data_memory_size="0x00"
    data_memory2_size="0x00"
    page_size="0x0080"
    pages_per_block="0x0000"
    chip_id="0x0000da45"
    voltages="0x0000"
    pulse_delay="0x2710"
    flags="0x0040c078"
    chip_info="0x0000"
    pin_map="0x0000190b"
    package_details="0x20000000"
    config="NULL"
/>
```
[VERIFIED: pinned `infoic.xml` @ `a8efaedc`, lines 228452-228471, quoted verbatim; the enclosing
`<manufacturer name="WINBOND">` confirmed by reading the preceding `<manufacturer` opener]

**Every one of the thirteen decode-relevant attributes is byte-identical to the ASD row**, including
`chip_id="0x0000da45"`. Upstream's own database treats `AE29F2008` and `W29C020C` as the **same die**.
D-18's equivalence chain is therefore *upstream-declared*, not merely plausible — while still being
equivalence-based rather than a direct AE29F2008 datasheet reading, exactly as D-18 requires.

The DB reflects this: `WINBOND | W29C020,W29C020C,W29C022 | {"algorithm": 5, "chip_id_value":
"0x0000da45", "infoic_page_size_raw": 128, "page_size": 128, …} | pinout DIP32_SST39SF040 | supported`
[VERIFIED: `chip_database.json`, dumped this session].

### B.4 The W29C020C datasheet — extracted and read, not cited from memory

The octopart PDF was fetched and converted with `pdftotext` (3,619 lines). Verbatim extracts:

| Claim (D-18/D-19) | Datasheet text, verbatim | Line |
|---|---|---|
| 2 Mbit, 256K×8 | `W29C020C` / `256K × 8 CMOS FLASH MEMORY` | 1-2 |
| 5 V only | `Single 5-volt write (erase and program) operations` | 130-ish (Features) |
| **No external VPP** | `VPP is not required.` and `Automatic write (erase/program) timing with internal VPP generation` | 119, 165 |
| 128-byte page write | `128 bytes per page` / `Page write (erase/program) cycle: 10 mS (max.)` | Features |
| 50 ms fast chip erase | `Fast chip-erase operation: 50 mS` | 154 |
| Six-byte software chip erase | `The entire device can be erased by using a six-byte software command code.` | 682-683 |
| The exact sequence | `0 Write 5555H AAH / 1 Write 2AAAH 55H / 2 Write 5555H 80H / 3 Write 5555H AAH / 4 Write 2AAAH 55H / 5 Write 5555H 10H` | 1020-1055 |
| **Chip ID 0xDA45** | `A read from address "00000 hex" outputs the manufacturer code "DA hex." A read from address "00001 hex" outputs the device code "45 hex."` | 730-731 |
| Boot-block caveat | `Once the boot block programming lockout feature is activated, the chip erase function will be disabled.` | 695 |
| The 12 V that exists on this part | `high, and raising A9 to 12 volts.` / `VDD = 5V ±10 %, VSS = 0V, VHH = 12V` | 734, 742 |

[CITED: https://datasheet.octopart.com/W29C020C-90B-Winbond-datasheet-181529584.pdf — fetched, converted
to text with `pdftotext` and read this session. All quotes are verbatim from that extraction.]

### B.5 gh#62 — read, and the `0x06` explanation tested

gh#62 (`henols/firestarter_prom`, **state OPEN, zero comments, zero labels**) verbatim body, read via
`gh issue view 62`:

- `firestarter erase AE29F2008` → `ERROR: Not supported` / `Programmer error during ERASE: Programmer
  error during init: Not supported`
- *"Same error occurs if told to be treated as AT29C020 or W29C020C"* — consistent: `W29C020C` is
  `algorithm 5` in the DB, so it takes the identical refusal.
- `firestarter erase SST39SF020 --force` → `WARN: Chip ID 0xda45 does not match expected ID 0xbfb6` /
  `Erase for SST39SF020 successful (0.14s).`
- `firestarter blank AE29F2008` → clean over `0x40000` in `27.96s`.

**Does the `0x06` chip-erase explanation hold? YES — and it is byte-exact, not merely "compatible".**

`SST39SF020,SST39SF020A` is `{"algorithm": 6, …, "chip_id_value": "0x0000bfb6"}` on pinout
`DIP32_SST39SF040` [VERIFIED: `chip_database.json`, dumped this session — which is also why `0xbfb6`
appears in the reporter's warning]. Driving `erase` under that identity dispatches to:

```c
    case CMD_ERASE:
        handle->firestarter_operation_main = flash_nor_unlock_erase_execute;
```
[VERIFIED: `firestarter/src/proms/flash_nor_unlock.cpp:39-40`, quoted verbatim]

```c
void flash_nor_unlock_erase_execute(firestarter_handle_t* handle) {
    if (handle->address != 0) {
        LOG_DEBUG_ID_SUB(DBG_SECTOR_ERASE);
        flash_nor_unlock_sector_erase(handle, handle->address);
    } else {
        LOG_DEBUG_ID_SUB(DBG_CHIP_ERASE);
        flash_execute_command(FLASH_ERASE);
    }
}
```
[VERIFIED: `firestarter/src/proms/flash_nor_unlock.cpp:121-129`, quoted verbatim]

```c
    const byte_flip_t FLASH_ERASE[] = {
        {0x5555, 0xAA},
        {0x2AAA, 0x55},
        {0x5555, 0x80},
        {0x5555, 0xAA},
        {0x2AAA, 0x55},
        {0x5555, 0x10},
    };
```
[VERIFIED: `firestarter/include/flash_utils.h:34-41`, quoted verbatim]

That array is **identical, cycle for cycle, to the W29C020C datasheet's own "Command Codes for Software
Chip Erase" table** quoted in §B.4. The reporter's erase was real, it used the sequence the silicon
documents, and the 50 ms internal erase plus serial round-trips is consistent with the observed `0.14s`.
The subsequent clean `blank` over `0x40000` is the confirming oracle.

**Why it was electrically benign here (context for REPLY-03, Phase 187).** Both identities sit on the same
pinout `DIP32_SST39SF040` and the same `size_bytes 262144`, so the bus config was identical; and
`configure_flash_nor_unlock`'s `CMD_ERASE` arm energises no VPP rail, pinned by
`test_val_nor_unlock.cpp:151` (*"configure_flash_nor_unlock CMD_ERASE must NOT set any VPP-enable CTL
bit"*) [VERIFIED, quoted verbatim]. **This is a coincidence of this particular pair, not a property of
`--force`** — which is exactly the warning REPLY-03 owes. Research recommends the Phase 187 planner be
handed this paragraph.

### B.6 VERDICT

> **AE29F2008 is classified `algorithm 5` CORRECTLY. The reporter is also correct that the chip can be
> chip-erased. Both are true at once: the `0x05` firmware path does not implement the chip-erase this
> silicon supports.**
>
> **The verdict is equivalence-based.** No primary AE29F2008 datasheet was retrieved or read. The
> evidence is: (a) upstream `infoic.xml` @ `a8efaedc` declares `protocol_id="0x05"` directly, and
> `build_db.py`'s `classify()` passes it through unchanged; (b) the same upstream file carries the ASD row
> and the Winbond `W29C020,W29C020C,W29C022` row as thirteen-field-identical records with the same
> `chip_id="0x0000da45"`; (c) the W29C020C datasheet independently confirms every DB field
> (256K×8, 5 V only, 128-byte page, 50 ms software chip erase, manufacturer `DA` / device `45`).

**Which branch the plan takes: the D-19 / D-20 branch.**
- D-21's misclassification branch **does not fire**. No `build_db.py` rule, no `diff_db.py` run, no
  regeneration, no `DECODE-NOTES.md` edit, no `chip_database.json` diff.
- D-22 is upheld with independent support: `support_status: "supported"` is correct and untouched.
- D-20's backlog entry should carry the boot-block caveat: *"Once the boot block programming lockout
  feature is activated, the chip erase function will be disabled."* Any future `0x05` chip-erase must
  handle the two 8 KB boot blocks.
- SAFE-09's deliverable is a **record**, not a code change. Plan it as a phase-record/SUMMARY task with
  the evidence above, not as a task with a `git diff`.

### B.7 D-23 — `vpp_mv: 12000` traced. SETTLED. Not a new hardware defect.

**The call chain, end to end, all verified this session:**

1. **Origin.** `voltages="0x0000"` upstream → VPP index `0x00` → `VPP_MV[0x00] = 12000`:
   ```python
   VPP_MV = {
       0x00: 12000,
       0x10: 9000,
   ```
   [VERIFIED: `firestarter_app/tools/build_db.py:70-72`, quoted verbatim], keyed per
   *"Key on (voltages & 0xF0), NOT (voltages & 0xFF)… [minipro database.c + tl866a.c,
   tl866ii_vpp_voltages[]]"* [VERIFIED: `:59-63`, quoted verbatim]. **This is a faithful decode of an
   upstream field, not an invented one** — the standing "generator may not invent fields absent from
   infoic" rule is **not** violated.
2. **Wire.** `convert_to_programmer` emits it unconditionally: `vpp_mv = full_eprom_data["vpp_mv"]` and
   `"vpp_mv": vpp_mv,` [VERIFIED: `firestarter_app/firestarter/database.py:527` and `:534`, quoted
   verbatim].
3. **Firmware parse.** It lands in `uint16_t vpp_mv;` [VERIFIED: `firestarter/include/firestarter.h:178`],
   pinned by `test_vpp_mv_round_trips_through_the_field_table` asserting
   `"{\"cmd\":1,\"vpp_mv\":12000}"` → `12000` [VERIFIED:
   `firestarter/test/native/avr/test_read_timing/test_read_timing_params.cpp:477-482`, quoted verbatim].
4. **Firmware consumers — this is the decisive step.** `handle->vpp_mv` is read in **exactly two files**:
   `src/proms/eprom.cpp:530,532,535,536` (protocols `0x07`/`0x08`/`0x0B`) and
   `src/proms/flash_intel.cpp:39,41,44,45` (protocol `0x10`). A tree-wide `grep` for `vpp_mv` across
   `src/` and `include/` returns **no hit in `flash_5v_page.cpp`** [VERIFIED: measured this session].
   **On algorithm 5 the field drives no comparison, no register write and no rail.**
5. **Host live check.** The one DB-level VPP invariant gate **excludes this handler by name, deliberately,
   with the reason on the record**:
   ```python
   "configure_flash_5v_page": (0, 6000),  # AMD/SST flash 5V only (WP-pin 12V exempt)
   ```
   and
   ```python
   # VPP-INVARIANT ENFORCEMENT SCOPE:
   # DB-level invariant check (in the main() scan loop below) applies ONLY to
   # configure_flash_intel where the mismatch is detectable from the DB. For 5V-only
   # handlers, the DB's electrical.vpp_mv encodes WP-pin voltage (not programming VPP),
   # so checking vpp_mv > 6000 would produce false positives on every AMD/SST flash chip.
   # The 5V handler invariants are proven via synthetic fixture only.
   _DB_CHECKED_VPP_INVARIANTS: frozenset[str] = frozenset({"configure_flash_intel"})
   ```
   [VERIFIED: `firestarter_app/tools/check_dispatch.py:85` and `:90-96`, quoted verbatim]
6. **`dev test` assertions.** None. `grep -n "vpp" firestarter/chip_test.py` returns **zero matches**
   [VERIFIED: measured]. `check_devtest_orchestrator.py:19` lists `vpp_mv` only inside a *forbidden wire-key
   vocabulary*, asserting no value [VERIFIED: `:16-22`, read].
7. **Host display — the only place it is visible.** Observed, not inferred:
   ```
   $ FIRESTARTER_CONFIG_DIR=/tmp/fs-cfg .venv311/bin/firestarter info AE29F2008
   Type:               Flash/EEPROM
   Can be erased:      yes (electrically erasable)
   VCC:                5.0v
   VPP:                12.0v
   Protocol: Flash - 5V page-write (EEPROM-like) (ID: 0x05)
   ```
   [VERIFIED: command run this session; output quoted verbatim]. The gate is
   `if _etype not in {"SRAM", "FRAM"} and _vpp_mv > 0:` [VERIFIED:
   `firestarter_app/firestarter/eprom_info.py:396`, quoted verbatim] and its twin
   `if etype not in {"SRAM", "FRAM"} and _vpp_mv > 0:` [VERIFIED:
   `firestarter_app/firestarter/ic_layout.py:573`, quoted verbatim] — neither carries
   `check_dispatch.py`'s WP-pin carve-out.

**D-23 verdict.** **The field is NOT live as a hardware check, a register write, or a `dev test`
assertion on algorithm 5.** It is a faithful decode of an upstream field whose 12 V has a real physical
referent on this silicon — the datasheet's `VHH = 12V` used for the A9-based hardware product-ID and
hardware-data-protection modes, *not* a programming VPP (`VPP is not required.`). The project already
records exactly this reading, at `check_dispatch.py:90-95`. **The `[WARNING: new finding]` branch of D-23
does NOT fire.**

**Residual, at a wider scope than this phase — file, do not fix here.** The *display* path calls it
"VPP" with no carve-out, so `firestarter info` prints an elevated VPP for **301 rows** across three
5 V-only families [VERIFIED: measured this session, `(algorithm, vpp_mv, electrical.type) -> count` =
`{(6, 12000, 'Flash/EEPROM'): 189, (13, 12000, 'EEPROM'): 66, (5, 12000, 'Flash/EEPROM'): 27,
(13, 12000, 'Flash/EEPROM'): 18, (6, 9000, 'Flash/EEPROM'): 1}`, total **301**]. This is a
pre-existing, cross-family labelling question, not an AE29F2008 defect, and **not** a `build_db.py`
correction (the decode is right). Recommend a backlog item; D-6 does not apply.

**A second, adjacent observation worth the phase record.** The same `info` output says
`Can be erased: yes (electrically erasable)` — derived from `electrical.type`, not protocol
[VERIFIED: `firestarter_app/firestarter/ic_layout.py:555-559`, quoted: *"# 'Can be erased' is derived from
electrical.type, NOT protocol_id."*]. So the tool tells the operator the part can be erased and then
refuses to erase it. That is a second contributor to gh#62 reading as a malfunction, alongside the bare
`Not supported`. **It is out of D-05's scope and must not be fixed here**, but it belongs in the phase
record and in REPLY-03's material.

---

## C. SAFE-08 — the deletion's real blast radius (D-12, D-13, D-14, D-15, D-17)

### C.1 D-12's three sites, re-cited by symbol + enclosing scope

`firestarter/src/proms/flash_5v_page.cpp` is **225 lines** [VERIFIED: `wc -l`].

| # | CONTEXT said | Measured | Symbol + enclosing scope (cite this form, per D-14/CLAIM-06) |
|---|---|---|---|
| 1 | `:49` | **`:48-50`** ✓ close | the `case CMD_ERASE:` arm of the `switch (handle->cmd)` inside **`configure_flash_5v_page`** |
| 2 | `:193-225` | **`:193-225`** ✓ exact (`:225` is EOF) | the whole definition of **`flash_5v_page_erase_execute`** |
| 3 | `:80-86` | **`:79-85`** ✗ **off by one at both ends** | the `if (is_flag_set(FLAG_CAN_ERASE)) { … }` block inside **`flash_5v_page_write_init`**'s `if (!is_operation_in_progress(handle))` |

Verbatim, site 1:
```c
        case CMD_ERASE:
            handle->firestarter_operation_main = flash_5v_page_erase_execute;
            break;
```
[VERIFIED: `firestarter/src/proms/flash_5v_page.cpp:48-50`]

Verbatim, site 3 (note `:86` is the closing brace of the **outer** `if`, not of this block):
```c
        if (is_flag_set(FLAG_CAN_ERASE)) {
            if (!is_flag_set(FLAG_SKIP_ERASE)) {
                flash_5v_page_erase_execute(handle);
            } else {
                LOG_INFO_ID(MSG_INFO_SKIPPING_ERASE);
            }
        }
    }
```
[VERIFIED: `firestarter/src/proms/flash_5v_page.cpp:79-86`]

**A fourth site D-12 does not name but must include:** the forward declaration
`void flash_5v_page_erase_execute(firestarter_handle_t* handle);` [VERIFIED: `:33`]. Leaving it behind
gives a declaration with no definition (harmless to the linker, but it is exactly the kind of orphan a
later sweep re-cites).

### C.2 D-13 — the unreachability claim, with the two lines that make it precise

Both citations hold:
- `if (!op_execute_function(configure_memory, handle)) {` [VERIFIED:
  `firestarter/src/firestarter.cpp:91`, quoted verbatim] — the assignment **does** execute, during INIT.
- `        case CMD_ERASE:` / `            finished = eprom_erase(&handle);` [VERIFIED:
  `firestarter/src/firestarter.cpp:273-274`, quoted verbatim] — and `eprom_erase` refuses first
  (`eprom_operations.cpp:36-38`).

**Say it as:** the arm's *assignment* runs on every flash4 INIT; the *function pointer it installs* is
never invoked, because `eprom_erase` returns at the `FLAG_CAN_ERASE` check before
`op_execute_simple_operation` is reached. Do **not** write "the arm never runs".

Do not confuse this refusal with `operation_utils.cpp:82`'s: that one is the generic NULL-`main` refusal,
with the comment *"No main phase installed for this (command, protocol): refuse rather than fall through"*
[VERIFIED: `firestarter/src/operation_utils.cpp:78-84`, quoted verbatim].

### C.3 **UNADJUDICATED CONSEQUENCE OF D-12 — planner must decide**

After site 3 is deleted, `flash_5v_page_write_init` reduces to:

```c
void flash_5v_page_write_init(firestarter_handle_t* handle) {
    if (!is_operation_in_progress(handle)) {
        if (handle->response_code == RESPONSE_CODE_ERROR) {
            return;
        }
    }
}
```

**The body has no observable effect at all.** Two dispositions, with their consequences measured:

| Option | Consequence |
|---|---|
| **(a) Keep the empty function** and its `handle->firestarter_operation_init = flash_5v_page_write_init;` at `:45` | Zero risk. `test_val_5v_page.cpp:332`'s `h.firestarter_operation_init(&h)` keeps working. Costs a few bytes of dead call. **Recommended.** |
| **(b) Also delete it and set init to `NULL`** | NULL init is a supported value elsewhere (`flash_5v_page.cpp:55`, `flash_intel.cpp:65`, `not_implemented.cpp:14`, `memory.cpp:49` all assign `NULL`) and the engine routes it through `_execute_operation_house_keeping_func(handle->firestarter_operation_init, INIT, handle)` [VERIFIED: `operation_utils.cpp:184`]. **But** `test_val_5v_page.cpp:332` calls `h.firestarter_operation_init(&h)` **unguarded** — a NULL there segfaults the native suite. Option (b) forces a test rewrite. |

This is inside D-12's blast radius but is not decided by D-12's text. **The plan must state which, and why.**

### C.4 Complete reference inventory — CONTEXT's list was short by six

CONTEXT named four: `check_erase_no_vpp.py`, `test_val_5v_page.cpp` (×3 sites), `size_baseline.json`, and
the `0x0D` warning in `CLAUDE.md`/`PROTOCOLS.md`. A tree-wide `/usr/bin/grep -rn` (NOT devcontainer
`grep`, which is ugrep and honours `.gitignore`) for the three symbols across `firestarter/` found the
following. ✅ = CONTEXT named it; ⚠️ = **missed by CONTEXT**.

| Site | What it says | Action |
|---|---|---|
| ✅ `firestarter/scripts/check_erase_no_vpp.py:26-28` | *"lines 196-231 (`flash_5v_page_erase_execute`, which asserts `CTRL_VPE_ENABLE`…"* | D-14 job 1 + job 2 |
| ⚠️ **`firestarter/tests/fixtures/planted_erase_no_vpp_ctrl_write.cpp:15-17`** | *"copying `flash_5v_page_erase_execute`'s HARDWARE Chip Erase path (`flash_5v_page.cpp:196-231`, which asserts `CTRL_VPE_ENABLE`…"* — **the identical impossible citation, a second time** | Same two D-14 jobs. The fixture itself still works (standalone, never compiled) |
| ⚠️ **`firestarter/tests/fixtures/planted_erase_no_vpp_ctrl_write.cpp:28`** | *"PLANTED VIOLATION -- lifted from `flash_5v_page_erase_execute`'s hardware 12V-on-OE Chip Erase path"* | Provenance prose goes stale |
| ✅ `firestarter/CLAUDE.md:118-120` | *"reaching for `flash_5v_page_erase_execute` in `flash_5v_page.cpp` — that IS the 12 V path, and it belongs only to algorithm 5, which keeps its `FLAG_CAN_ERASE` exclusion for exactly that reason."* | Rewrite: the copy-source is gone; the `FLAG_CAN_ERASE` exclusion stays (D-04/§C.6) |
| ⚠️ **`firestarter/PROTOCOLS.md:110`** (§1.1, the `0x05` **Erase model** paragraph) | *"The capability-gated bulk erase described above is unchanged and remains **deliberately unadvertised** by the host: setting `FLAG_CAN_ERASE` for algorithm 5 would route a 12 V bulk erase onto this 5V-only part"* | **False after D-12** — there is no bulk erase left to route to. Must be rewritten |
| ⚠️ **`firestarter/PROTOCOLS.md:113`** | *"**VPP behavior:** None (5V-only operation)… the RURP VPP regulator is not used for this bucket."* | Becomes *more* true; no edit needed, but it is the sentence the D-12 record should point at |
| ✅ `firestarter/test/native/avr/test_val_5v_page/test_val_5v_page.cpp:20-24` | the NOTE: *"flash_5v_page_erase_execute (called from flash_5v_page_write_init) does use CTRL_VPP_REGULATOR_ENABLE for the OE=12V erase pulse…"* | Delete — describes a function that no longer exists |
| ✅ `…/test_val_5v_page.cpp:234` | *"the erase-on-write block at flash_5v_page.cpp:80-86 is not entered"* | Delete/re-point. **Also note the range was already wrong** (real: 79-85) — a third stale citation |
| ✅ `…/test_val_5v_page.cpp:316-358` | the ERASE-02 case | See §C.5 |
| ⚠️ `…/test_val_5v_page.cpp:225,231,317,336,355` | five more `flash_5v_page_write_init` mentions, all in prose | Review for staleness |
| ⚠️ **`firestarter/tests/fixtures/planted_no_heap_or_64bit_symbols_prechange_uno/avr-nm-uno.txt:216`** and **`…/clean_no_heap_or_64bit_symbols_postchange_uno/avr-nm-uno.txt:204`** | `t flash_5v_page_erase_execute(firestarter_handle*)` in frozen `avr-nm` symbol dumps | **Frozen fixtures — must stay byte-unchanged.** They record a historical build, not the live tree. **Do not "update" them.** Verify no gate diffs them against a live `nm` run |
| ⚠️ `firestarter/scripts/check_size_baseline.py:348` and `firestarter/tests/test_check_size_baseline.py:359` | prose citing `flash_5v_page_write_init` in a Phase-153 provenance narrative | Historical narrative; leave alone |
| — `firestarter/include/flash_5v_page.h` | declares only `configure_flash_5v_page` and `flash_5v_page_read_protection_execute` — **no erase symbol** [VERIFIED: read in full, 28 lines] | **No header change needed** |
| — `firestarter_app/tests/test_check_dispatch_invariants.py:113` | `"configure_flash_5v_page"` in `_FAMILY_VPP_INVARIANTS`'s expected handler set | **Unaffected** — `configure_flash_5v_page` survives D-12, and the table is a host-side dict, not a firmware source scan |

**No other firmware test drives `CMD_ERASE` on protocol `0x05`.** `test_configure_memory.cpp` covers
`0x05` only at `CMD_READ` (`:75-76`) and `CMD_CHECK_CHIP_ID` (`:152-158`); `test_val_5v_page.cpp` covers
`0x05`/`0x35`/`0x39` only at `CMD_READ` and `CMD_WRITE` (`:133,142,153,162,173,182`) [VERIFIED: measured].
So **no test goes red from deleting the arm.**

### C.5 D-17 — the vacuity question, answered case by case

`test_5v_page_write_init_no_blank_check_with_flag_clear_erase02` lives at **`:327-358`** (CONTEXT said
≈327-355 — close; the final `assert_no_vpp_in_recording` message runs to `:357` and the closing brace is
`:358`). It drives `h.firestarter_operation_init(&h)` (`:332`) after `configure_memory` with
`ctrl_flags = 0`, and asserts three things:

| # | Assertion | What it asserts **today** | What it asserts **after D-12** |
|---|---|---|---|
| 1 | `TEST_ASSERT_FALSE(is_operation_in_progress(&h))` (`:334`) | The Phase-153 blank-check deletion holds — `mem_util_blank_check` is *"the only setter of this flag on the write-INIT path"* (`:337-338`, quoted). **Already near-vacuous:** nothing in `write_init` can set it today; it is a *re-introduction* guard. | Unchanged in strength. **Still a legitimate re-introduction guard.** Keep. |
| 2 | `TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code)` (`:351`) | `response_code` is `RESPONSE_CODE_OK` on entry (`:218`) and nothing in `write_init` changes it. **Already tautological today.** | Tautological. Same. |
| 3 | `assert_no_vpp_in_recording("ERASE-02: with FLAG_CAN_ERASE clear, flash_5v_page_write_init must energise no VPP rail -- the erase-on-write branch above the deleted conditional must not be entered by this INIT call")` (`:354-357`, quoted verbatim) | **Non-vacuous today**: it proves the `FLAG_CAN_ERASE` guard actually gates the 12 V routine. With the flag set it would fail. | **TAUTOLOGICAL.** There is no branch left to not enter; no code path in `write_init` can write a control register. This is the D-17 / CLAIM-07 defect exactly. |

**Recommended disposition — re-point at a real anchor, do not merely delete.** Deleting assertion 3
silently removes the only coverage of the property D-12 delivers. Instead:

1. Keep assertions 1 and 2; rename the case to drop `with_flag_clear` (it no longer distinguishes
   anything) and rewrite its message to cite the blank-check axis only.
2. **Add a companion case with `FLAG_CAN_ERASE` SET** (`h.ctrl_flags |= FLAG_CAN_ERASE`), asserting
   `assert_no_vpp_in_recording` after one `firestarter_operation_init` call. Today that case would be
   **RED** (the branch fires and asserts `CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE |
   CTRL_VPE_ENABLE`, `flash_5v_page.cpp:199`). After D-12 it is **GREEN**, and it is a genuine,
   permanently non-vacuous regression guard on exactly the hazard D-12 removes: *even if the host wrongly
   sets `FLAG_CAN_ERASE` for an algorithm-5 part, no 12 V rail can be energised.* That is a stronger
   safety property than the tree has today, and it is observed-red-then-green rather than asserted.
3. Delete the file-header NOTE (`:20-24`) and the `:234` citation; both name deleted code.

### C.6 D-14 — both claims confirmed, plus a third site

**Job 1 — the citation is impossible.** `check_erase_no_vpp.py:26-28` reads verbatim:
> *"**Proximity, not absence, is the risk.** The hardware 12V-on-OE erase path already exists in this tree
> today, at `firestarter/src/proms/flash_5v_page.cpp` lines 196-231 (`flash_5v_page_erase_execute`, which
> asserts `CTRL_VPE_ENABLE` and the VPP boost regulator around a `rurp_chip_enable()` /
> `rurp_chip_disable()` bracket)"*

The file is **225 lines** and the function spans **193-225**. `231 > 225` — **the cited range cannot
exist** [VERIFIED]. ⚠️ **The identical range appears a second time**, in
`tests/fixtures/planted_erase_no_vpp_ctrl_write.cpp:15-17`, and a **third** wrong range
(`flash_5v_page.cpp:80-86`, real 79-85) appears at `test_val_5v_page.cpp:234`. D-14's fix must cover all
three, by symbol + enclosing scope.

**Job 2 — the gate stays green functionally. CONFIRMED BY RUNNING IT.**
```
$ python3 scripts/check_erase_no_vpp.py
PASS: eeprom28c_erase_execute() in /workspaces/firestarter/src/proms/eeprom_28c.cpp (lines 322-337, 16 lines scanned) contains no VPP/VPE control-register, chip-enable/disable, or bus-config-bypassing hazard token
rc=0
```
[VERIFIED: run this session, output quoted verbatim]

Its non-vacuity anchor is `0x0D`-scoped exactly as D-14 records: *"it requires the matched body to contain
at least one `handle->firestarter_set_data(` call and at least one `delay(AT28C_TEC_MAX_MS)` call — the two
source-level fingerprints of the real AN-0544B six-byte software chip erase"* [VERIFIED: `:58-70`, quoted
verbatim], with `--function` defaulting to `eeprom28c_erase_execute` and `--source` to
`src/proms/eeprom_28c.cpp` [VERIFIED: `:39-43`, `:96-97`]. **Nothing in the gate reads
`flash_5v_page.cpp`.** Only the prose is false — exactly as D-14 states.

**Standing disclosure the plan must preserve:** *"**No CI leg.** This module -- and its paired pytest --
executes in NO CI leg on this branch: `build.yml` and `beta-build.yml` run only `pio test -e native` and
`pio test -e native_nodevtools`"* [VERIFIED: `:88-93`, quoted verbatim]. So the phase record is the only
evidence it was exercised — the plan must run it explicitly and capture the output.

### C.7 D-15 — the byte-identity gate and the 724 B exemptions, both confirmed

**Default mode is byte-identity, and it fails on divergence and on emptiness.** Verbatim from the module
docstring:
> *"Exit codes (identical taxonomy in both modes): 0 — every env supplied compared clean against the
> baseline/policy (gate passes); 1 — an env's observed figures diverge from the baseline (default mode) or
> fall outside MERGE-05's effective allowance (`--policy merge05`…), OR zero envs were compared (the
> never-vacuous guard: a comparator that compares nothing must not report success — not bypassed by
> `--policy`); 2 — a supplied log could not be parsed…"*
[VERIFIED: `firestarter/scripts/check_size_baseline.py:74-87`, quoted verbatim]

Measured: a bare invocation exits **1**:
```
$ python3 scripts/check_size_baseline.py ; echo rc=$?
FAIL: no envs compared -- supply --avr-log/--native-log or --rebuild (never-vacuous guard: a comparator that compares nothing must not pass)
rc=1
```
[VERIFIED: run this session, quoted verbatim]. **A firmware shrink reddens it.** D-15 confirmed.

**The four exemptions total 724 B and are additive allowances.** The literals:
`MERGE05_DEFECT_FIX_EXEMPTION_BYTES = 96` (`:199`), `MERGE05_PAGE_SIZE_SEAM_EXEMPTION_BYTES = 210`
(`:257`), `MERGE05_LOCK_STATUS_READ_EXEMPTION_BYTES = 288` (`:331`),
`MERGE05_ERASE_STANDALONE_EXEMPTION_BYTES = 130` (`:421`) — **96+210+288+130 = 724** [VERIFIED: each
literal read at the cited line]. They are summed onto the band in `_merge05_flash_allowance`
(`:607-612`), and `size_baseline.json`'s leonardo `merge05_clause` states it as *"leonardo 0+96+210+288+130
= 724 B"* [VERIFIED, quoted]. Since the measured tree is **1808 B below BASE-01** on leonardo (§A.3), a
shrink stays inside the allowance with room to spare and **authors no new exemption**. CLAIM-05's "no new
exemption" clause survives. D-15 confirmed.

**The ROADMAP line D-15 must amend, verbatim:**
> `**Depends on:** — (independent; CLAIM-09's guard from 184 does not gate this)`

[VERIFIED: `.planning/ROADMAP.md`, the line following Phase 185's success criterion 5 — Phase 185's
section starts at line 350]

---

## D. SAFE-06 — the host gate's exact shape (D-02, D-03, D-06, D-07)

### D.1 The shared contract the new sibling must honour

Extracted from reading both precedents **in full**:

| Contract clause | `sdp_capability.py` | `jp5_gate.py` | New module must |
|---|---|---|---|
| Import purity | *"the module's top-level import set is a subset of `{"__future__", "typing"}` — no click, no serial, no `firestarter.*` imports"* [VERIFIED: `:18-19`, quoted verbatim] | Imports `sys`, `typing`, `rich.prompt.Confirm`, `firestarter.database.pin_conversions`, `firestarter.exceptions` [VERIFIED: `:27-33`] | **Follow `jp5_gate`, not `sdp_capability`.** The stricter rule is not achievable if the module needs a shared constant; the invariant that matters is *no serial, no Click, no file/env I/O at import or call time*. If the module needs only a local `int`, aim for `sdp_capability`'s purity. |
| Pure predicate | `sdp_capability_for_entry(entry, display_name) -> tuple[bool, str]`; *"Pure: no serial, no Click, no DB construction, no file I/O."* [VERIFIED: `:166-181`, quoted] | `is_affected(bus_config) -> bool`; *"No I/O, no environment reads, no serial access -- the wire dict and the operation name are the whole input"* [VERIFIED: `:21-24`, quoted] | Same. Return `(refused: bool, message: str)` or a bare predicate + a separate `refusal_text()`. |
| Fail-closed | *"a static fail-closed allow-list… is therefore REFUSED by default"* [VERIFIED: `:3-6`]; raises `KeyError` rather than defaulting on a missing `protocol-id` [VERIFIED: `:185-194`] | *"Raises `Pin1HazardRefusedError` when `bus_config` carries no `bus` list at all -- fail-closed, because absent evidence cannot prove socket pin 1 is safe"* [VERIFIED: `:91-95`, quoted] | **Note the polarity inversion.** For `jp5_gate`, *absent evidence → refuse*. Here, absent evidence means "we cannot prove it is flash4", and refusing every unknown part would break `erase` for every chip. **Fail-open on a missing key is correct here, and the plan must state that inversion explicitly** so the next reader does not "fix" it. |
| Injectable `isatty_fn` | n/a | `isatty_fn: Optional[Callable[[], bool]] = None` … `isatty_fn = isatty_fn or (lambda: sys.stdin.isatty())` [VERIFIED: `:121`, `:145`, quoted] — *"with its own injectable `isatty_fn` rather than importing `cli_handlers._is_interactive` (which Phase 185 deletes)"* | **This gate needs NO TTY logic at all.** D-07's refusal prints one line and exits; there is no prompt. Do **not** import `_is_interactive` (Phase 185 deletes it — CLAIM-07), and do not add an `isatty_fn` it will not use. |
| Stable reason substrings for tests | `REASON_NOT_FOUND`, `REASON_WRONG_PROTOCOL`, `REASON_FRAM`, `REASON_NOT_CAPABLE`, `REASON_ALLOWED` — *"tests assert on these stable substrings rather than whole sentences"* [VERIFIED: `:143-149`, quoted] | text built in `hazard_text()` | **Follow `sdp_capability`.** Put the D-07 line behind a module constant so the test pins the shape, not a whole sentence. |
| Injectable `console` / `_print` | n/a | `_print(msg, *, console=None)` [VERIFIED: `:110-114`] | Optional. `cli_handlers` already uses `click.echo` elsewhere; either is consistent. |

### D.2 The call site — verified, with the pre-connect boundary located

`erase`'s handler body is **five statements**:
```python
    eprom_data = resolve_chip(eprom, db=app.db)

    if not jp5_gate.confirm_or_refuse(eprom, eprom_data.get("bus-config"), "erase"):
        sys.exit(1)

    ok = app.eprom_operator.erase_eprom(
        eprom,
        eprom_data,
        operation_flags=_build_op_flags(blank_check=blank_check, force=force),
        address_str=sector_address,
        pin1_hazard_acknowledged=True,
    )
    sys.exit(0 if ok else 1)
```
[VERIFIED: `firestarter_app/firestarter/cli_handlers.py:871-883`, quoted verbatim. The `@cli.command(name="erase")` decorator starts at `:827`; `def erase(` at `:853`.]

- `resolve_chip(...)` at `:871` is a pure DB lookup — **no serial**.
- `app.eprom_operator.erase_eprom(...)` at `:876` is **where the port opens**.
- **The new gate goes between them, beside `jp5_gate` at `:873`.** D-02 satisfied. ✓
- The `sys.exit(0 if ok else 1)` D-06 modifies is at **`:883`**. ✓

### D.3 The predicate's field — a cleaner path than CONTEXT assumed

CONTEXT points at `database.py:556-584`'s `if algo not in (5,)` as *"the single place `FLAG_CAN_ERASE` is
cleared for flash4"*. Confirmed verbatim:
```python
        simple_flags = 0
        algo = programmer_data["algorithm"]  # already computed above from protocol-id
        if full_eprom_data.get("electrical-type", "") in ("EEPROM", "Flash/EEPROM"):
            if algo not in (5,):
                simple_flags |= FLAG_CAN_ERASE  # FLAG_CAN_ERASE is 0x02
        programmer_data["flags"] = simple_flags
```
[VERIFIED: `firestarter_app/firestarter/database.py:578-583`, quoted verbatim — CONTEXT's `:556-584` range
brackets this correctly, the comment block running `:556-577`]

**And the same value is already in the dict at the `erase` call site**, five lines above:
```python
            "algorithm": full_eprom_data.get("protocol-id", 0),
```
[VERIFIED: `firestarter_app/firestarter/database.py:532`, quoted verbatim]

**So `eprom_data["algorithm"]` at `cli_handlers.py:871` IS the flash4 discriminator, pre-connect, with no
second DB lookup.** This corrects a reading a planner might take from `sdp_capability.py:26-30`'s note
(*"never `algorithm` from `resolve_chip()` / `convert_to_programmer()`, which do not carry this key"*) —
that note is about the key name **`protocol-id`**, which the programmer dict genuinely lacks; the *value*
is present under **`algorithm`**. `sdp_capability` had to be name-keyed because it needed `part_number`;
**this predicate does not**.

**Recommended shape** (planner discretion on names):

```python
# firestarter_app/firestarter/flash4_erase_gate.py
FLASH4_PROTOCOL_ID = 0x05      # mirrors sdp_capability.SDP_PROTOCOL_ID = 13

def is_flash4(programmer_data) -> bool:
    """True when the wire dict's `algorithm` is the flash4 (0x05) page-write protocol."""
    if not programmer_data:
        return False                      # fail-OPEN: see §D.1 polarity note
    return programmer_data.get("algorithm") == FLASH4_PROTOCOL_ID

def refusal_text(chip_name: str) -> str:
    return f"Erase not supported for {chip_name.upper()}"
```

Wired at `cli_handlers.py:873`-ish:
```python
    if flash4_erase_gate.is_flash4(eprom_data):
        click.echo(flash4_erase_gate.refusal_text(eprom))
        sys.exit(0 if ignore_unsupported else 1)
```

**Why key on `algorithm` and not on `flags & FLAG_CAN_ERASE`:** the flag is clear for UV-EPROM and SRAM
too, so a flag-based predicate would silently widen the gate past D-05's flash4-only scope. Keying on
`algorithm` makes the predicate and `database.py:581`'s exclusion read the **same value**, so they cannot
drift — which is the D-4 "database-derived, never a hand-kept list" property, achieved structurally.
`FLAG_CAN_ERASE = 0x02` [VERIFIED: `firestarter_app/firestarter/constants.py:109`] and there is **no
algorithm-5 constant in `constants.py`** [VERIFIED: measured]; the nearest precedent is
`_PROTOCOL_FLASH4 = 0x05` [VERIFIED: `firestarter_app/firestarter/chip_test.py:325`], but `chip_test.py`
is not import-pure, so define the constant locally as `sdp_capability.py` does.

### D.4 D-06 — naming the flag, and whether Click makes it awkward

**Flag-vocabulary survey (the whole `cli_handlers.py` long-option set, measured this session):**

`--adapter --address --avrdude-config-path --avrdude-path --blank-check --board --chip --chip-disable
--config --dfu-probe --direction --fast --fault-form --firestarter --firmware-version --force --input-enable
--install --json --list --max-diffs --mode --no-blank-check --output-dir --port --pre --pulse-us --quiet
--read-settling --read-strobe --rev --runs --samples --sector-address --size --skip-erase
--skip-sdp-unlock --source --stable --timeout --usb-id --verbose --verified --vpe-as-vpp`

[VERIFIED: measured; 33 `is_flag=True` options total]

**There is no existing `--no-op` / `--ignore-unsupported` shape anywhere.** The nearest idioms are the
`--skip-*` family (`--skip-erase`, `--skip-sdp-unlock`) — but those skip a *step within* an operation, not
an exit code, so reusing that prefix would mislead.

**Recommendation: `--ignore-unsupported`, long-form only, `is_flag=True, default=False`.**
- It names the condition (`unsupported`) that the message names, so `--help` and the message agree.
- Long-only avoids a short-flag collision: `erase` already binds `-f`, `-b`, `-s`
  [VERIFIED: `cli_handlers.py:810-850`].
- Alternatives considered: `--no-op` (ambiguous with "no operation performed" vs "noop mode"),
  `--ok-if-unsupported` (reads as an assertion), `--allow-unsupported` (implies it will *try*).

**Click makes this trivial, not awkward.** The handler already calls `sys.exit` directly at `:874` and
`:883`; adding one `@click.option` and one parameter changes nothing structurally. The only subtlety is
**where the flag is documented** — the `erase` docstring is user-facing `--help` text
(`cli_handlers.py:860-870`, exempt from the no-comments rule) and should gain one sentence stating that
the default exit code is 1 and the flag makes it 0.

**Also record:** D-06's flag must NOT change the message or suppress it. Exit-code-only.

### D.5 Unit-testability with no board — the template and the file name

Both precedents have test files and they are the model:
- `firestarter_app/tests/test_jp5_gate.py` — **31 `def test_` functions**, a docstring enumerating the
  five properties proved, and `CliRunner` + `Mock`/`patch` for the CLI-integration leg
  [VERIFIED: read `:1-40`, counted].
- `firestarter_app/tests/test_sdp_capability.py` and `firestarter_app/tests/test_check_sdp_capability.py`.

Measured green this session:
```
$ .venv311/bin/python -m pytest tests/test_jp5_gate.py tests/test_sdp_capability.py -o addopts="" -q
53 passed in 0.66s
```

**The file the planner should have created: `firestarter_app/tests/test_flash4_erase_gate.py`.**
Properties it must prove, mirroring `test_jp5_gate.py`'s structure:
1. The pure predicate over every `algorithm` value present in the DB (0x05 → True; 0x06, 0x07, 0x08,
   0x0B, 0x0D, 0x0E, 0x10, 0x27/0x28/0x29 → False), plus `None`/`{}`/missing-key.
2. **Coupling to the REAL database, not a literal part list (D-4):** resolve `AE29F2008` through
   `EpromDatabase(skip_local_override=True)` + `resolve_chip` and assert the predicate fires; assert the
   module source carries **no** part-number literal. Then assert the derived set equals
   `{rows where programming.algorithm == 5}` — **27 rows** [VERIFIED: measured].
3. **The refusal fires before the port opens (D-02):** drive `cli` via `CliRunner` with
   `app.eprom_operator` a `Mock`, and assert `erase_eprom` was **never called** — the `test_jp5_gate.py`
   pattern ("the refusal fires before `_operation_context` is ever entered").
4. **Exit codes (D-06):** exit 1 by default; exit 0 with `--ignore-unsupported`; the printed line is
   byte-identical in both cases.
5. **Message shape (D-07):** the output is exactly one line, contains the chip name, and contains **none
   of** `"write"`, `"self-eras"`, `"page"`, `"--force"` — a negative assertion, so a later executor cannot
   quietly re-add the cause.
6. A non-flash4 part (`AT28C256`, algorithm 13) reaches `erase_eprom` normally — proving the gate is not
   a blanket refusal.

---

## E. The test and verify story — exact commands, with `<fails_when>` for each

Every command below was **run in this session** unless marked "not run".

### E.1 Host app (`firestarter_app/`)

| Command | Observed | `<fails_when>` |
|---|---|---|
| `cd /workspaces/firestarter_app && .venv311/bin/python -m pytest tests/test_flash4_erase_gate.py tests/test_jp5_gate.py tests/test_sdp_capability.py -o addopts="" -q` | `53 passed in 0.66s` (for the two existing files) | non-zero exit, or the final line is not `N passed`. **`-o addopts=""` is mandatory** — the repo's `addopts = "-ra -q"` [VERIFIED: `pyproject.toml:107`] doubles with a second `-q` and hides the count line. |
| `cd /workspaces/firestarter_app && .venv311/bin/python -m pytest tests/ -o addopts="" -q` | **2337 tests collected** (`--collect-only`; full run not executed) | non-zero exit. ⚠️ **Caveat:** `tests/test_flash_path_record_sync` asserts whole-repo porcelain — the meta working tree currently carries untracked `anything.txt` and `tmp/`, and modified `.planning/VALIDATED-EPROMS.md`. **Commit or stash before a full-suite run**, or this fails for reasons unrelated to the change. |
| Python interpreter | `.venv311/bin/python` → `3.11.16` [VERIFIED] | Do **not** use the devcontainer's `python3` (3.12.14) — it masks app CI, which is py3.11. |
| `cd /workspaces/firestarter_app && FIRESTARTER_CONFIG_DIR=/tmp/fs-cfg .venv311/bin/firestarter erase AE29F2008` | not run (needs no board **after** the gate lands; today it would try to connect) | after the change: stdout is exactly `Erase not supported for AE29F2008`, exit **1**, and **no `Connecting...` line appears**. The presence of `Connecting` is itself the D-02 failure. |

### E.2 Firmware (`firestarter/`)

| Command | Observed | `<fails_when>` |
|---|---|---|
| `cd /workspaces/firestarter && pio test -e native` | `================ 184 test cases: 184 succeeded in 00:01:21.022 ================` | the summary line shows any count other than `N succeeded` with `N` == case count, or a `FAILED` row appears. **This is one of only two envs CI runs** (`build.yml`, `beta-build.yml` run `native` and `native_nodevtools` only). |
| `cd /workspaces/firestarter && pio test -e native_nodevtools` | not run; baseline records `{"cases": 184, "succeeded": 184, "suites": 17, "all_passed": true}` | same. |
| `cd /workspaces/firestarter && python3 -m pytest tests/ -q` | `360 passed in 24.96s` | non-zero exit. **Note: this suite runs in NO CI leg** — the phase record is the only evidence. |
| `cd /workspaces/firestarter && python3 scripts/check_erase_no_vpp.py` | `PASS: eeprom28c_erase_execute() in …/eeprom_28c.cpp (lines 322-337, 16 lines scanned) contains no …hazard token` / `rc=0` | **exit 1** = a real hazard token found in the scanned body. **exit 2** = fail-closed (file missing, function unresolvable, unbalanced braces, or the non-vacuity anchor failed). The two codes mean different things and the plan must distinguish them. |
| `cd /workspaces/firestarter && python3 scripts/check_size_baseline.py` | `FAIL: no envs compared -- supply --avr-log/--native-log or --rebuild …` / `rc=1` | **This is the correct pre-change behaviour with no args.** Real use needs `--rebuild` or `--avr-log ENV=path`. exit 1 = divergence *or* zero envs; exit 2 = unparseable log or malformed CLI. |
| `cd /workspaces/firestarter && rm -rf .pio/build/leonardo && pio run -e leonardo` (and `uno`, `uno328pb`) | **not run** (per the research brief). Toolchain verified present. | a non-zero `pio` exit, or no `RAM:`/`Flash:` report line in the output for `check_size_baseline.py` to parse (that would be its exit 2). |

### E.3 Meta repo

| Command | `<fails_when>` |
|---|---|
| `bash /workspaces/tools/catalog/sync_to_subrepos.sh` (**only if M1 wins**) | the two sub-repo copies of `messages.toml` are not byte-identical to the meta copy afterwards. |
| `git diff --stat` over `firestarter/tests/fixtures/{planted,clean}_no_heap_or_64bit_symbols_*` | **must be empty.** These are frozen `avr-nm` fixtures; a non-empty diff means someone "updated" a historical record. |

---

## Standard Stack

No new external dependency is required by any part of this phase.

### Core (already present)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `click` | as pinned by `firestarter_app/pyproject.toml` | CLI option + handler for `--ignore-unsupported` | Every existing firestarter command uses it; the option is one decorator. |
| `pytest` | installed in `.venv311` | Gate unit tests | 2337 existing tests; `test_jp5_gate.py` is the template. |
| PlatformIO | `pio` 6.1.19 recorded / 6.2.0 available | AVR cold builds for D-16 | The only build system for this firmware. |
| `pdftotext` (poppler) | `/usr/bin/pdftotext` | Datasheet text extraction (used by this research) | Already installed; `WebFetch` cannot read the PDF. |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|---|---|---|
| A new `flash4_erase_gate.py` module | Inline the check in `cli_handlers.erase` | **Rejected by D-03.** Both precedents exist specifically to keep policy out of the CLI layer. |
| Keying on `algorithm` | Keying on `flags & FLAG_CAN_ERASE` | Rejected: the flag is also clear for UV-EPROM and SRAM, silently widening past D-05's scope. |
| Keying on `algorithm` | `db.get_eprom(name)["protocol-id"]` (the `sdp_capability` shape) | Works, but needs a second DB lookup for a value already in `eprom_data`. Use the wire dict, like `jp5_gate`. |

**No package install is required, so the Package Legitimacy Audit is not applicable to this phase.**

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---|---|---|---|
| "Which parts are flash4?" | A part-number list in the new module | `eprom_data["algorithm"] == 5`, already in the dict at the call site | **D-4 forbids a hand list.** And a DB-derived predicate cannot go stale when a row is added. |
| Determining AE29F2008's classification | Inferring from the part number or the vendor | The pinned upstream `infoic.xml` row + `classify()`'s pass-through | The classification is a transcription; there is no decode to second-guess. |
| Establishing part equivalence | Reasoning from "it looks like a re-badge" | Upstream's own thirteen-field-identical rows + the shared `chip_id` | Upstream *declares* the identity. Inference was unnecessary. |
| Measuring firmware flash cost | Estimating AVR instruction bytes | D-16's cold `rm -rf` + one `pio run` per env | The repo's own recorded procedure, and the gate compares against it byte-for-byte. |
| A refusal prompt / TTY handling | Copying `jp5_gate`'s `isatty_fn`/`Confirm.ask` plumbing | Nothing — D-07's refusal has no prompt | Copying it would import machinery the gate never uses and drag in the `_is_interactive` question Phase 185 is closing. |
| Reading the W29C020C datasheet | `WebFetch` on the PDF | `curl` + `pdftotext` | `WebFetch` returns "binary content… cannot reliably extract" on this PDF. |

**Key insight:** every hard question in this phase already had an authoritative in-repo or upstream answer.
The failure mode here is not building the wrong thing — it is *asserting* an answer that a five-minute
lookup would have settled, which is exactly what gh#62's open question was.

---

## Common Pitfalls

### Pitfall 1: Trusting CONTEXT's line numbers
**What goes wrong:** Two of D-12's three ranges are off (`:80-86` real `:79-85`), and three separate files
carry the impossible `flash_5v_page.cpp:196-231`.
**Why:** Line citations stale on every edit; CLAIM-06, D-14 and D-17 are three recorded instances.
**Avoid:** Re-verify every range in the executing session; cite symbol + enclosing scope thereafter.
**Warning sign:** a cited end-line greater than the file's `wc -l`.

### Pitfall 2: Using the devcontainer's `grep`
**What goes wrong:** it is `ugrep` and honours `.gitignore`, silently under-scanning.
**Avoid:** use `/usr/bin/grep` (as every measurement in this document did) for any completeness claim.
**Warning sign:** a "found all references" claim with suspiciously few hits.

### Pitfall 3: Running the full app suite with a dirty working tree
**What goes wrong:** `tests/test_flash_path_record_sync` asserts whole-repo porcelain; `anything.txt`,
`tmp/` and a modified `VALIDATED-EPROMS.md` are present right now.
**Avoid:** commit or stash first; a red here is not a code defect.

### Pitfall 4: "Updating" the frozen `avr-nm` fixtures
**What goes wrong:** `planted_no_heap_or_64bit_symbols_prechange_uno/avr-nm-uno.txt` and
`clean_no_heap_or_64bit_symbols_postchange_uno/avr-nm-uno.txt` both name
`flash_5v_page_erase_execute`. They are **historical records of a specific build**, not descriptions of the
live tree.
**Avoid:** `git diff --stat` over those paths must be empty at phase end.

### Pitfall 5: Deleting ERASE-02's third assertion outright
**What goes wrong:** it is the only test covering the property D-12 delivers. Deleting it removes coverage
rather than removing a tautology.
**Avoid:** §C.5's re-point — add the `FLAG_CAN_ERASE`-SET companion case, observed red before and green
after.

### Pitfall 6: Writing a comment
**What goes wrong:** `/workspaces/CLAUDE.md`'s hard rule forbids **all** comments in `firestarter/` and
`firestarter_app/`, not overridable by a plan. The files this phase edits are heavily commented; that is
not licence.
**Avoid:** rationale goes in the phase `SUMMARY.md` or the commit message. Click docstrings are `--help`
text and are exempt. **Deleting a now-false comment is not "writing a comment" and is required** — e.g.
`flash_5v_page.cpp:92-94`'s *"The erase-enable block above is a DIFFERENT thing and stays"* becomes false
the moment D-12 lands.

### Pitfall 7: Assuming the firmware milestone branch exists
See Environment Availability below. It does not.

---

## Runtime State Inventory

This is a deletion/refactor phase, so the five categories are answered explicitly.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| **Stored data** | **None.** The deleted firmware path stores nothing; `chip_database.json` is regenerated, not mutated, and SAFE-09's verdict requires **no** DB change (§B.6). Verified by reading the AE29F2008 row and `classify()`. | none |
| **Live service config** | **None.** No external service (n8n, Datadog, Tailscale, Cloudflare) carries `flash_5v_page_erase_execute` or a flash4 erase policy. Verified: the symbol's only occurrences are the ten in-repo sites of §C.4. | none |
| **OS-registered state** | **None.** No task-scheduler entry, pm2 process or systemd unit references any symbol or flag in scope. | none |
| **Secrets / env vars** | **None new.** Two env seams are *read* by tooling in scope and must keep working unchanged: `FIRESTARTER_SIZE_BASELINE` (`check_size_baseline.py`'s baseline path seam) and `FIRESTARTER_CONFIG_DIR` (used above to keep `info` off the real config). ⚠️ Known: the app writes `~/.firestarter/config.json` despite `FIRESTARTER_CONFIG_DIR`; do not delete that dir. | none |
| **Build artifacts / installed packages** | **Two, both real.** (1) `firestarter/.pio/build/{uno,uno328pb,leonardo}` hold stale objects — D-16's `rm -rf .pio/build/<env>` is precisely the required action. (2) `firestarter_app/.venv311` holds an editable install pointing at `/workspaces/firestarter_app/firestarter/__init__.py` [VERIFIED: printed `firestarter.__file__` this session] — a **new module file is picked up automatically** by an editable install, no reinstall needed. | (1) the cold-build task; (2) none |

---

## Environment Availability

| Dependency | Required By | Available | Version / evidence | Fallback |
|---|---|---|---|---|
| `pio` + `toolchain-atmelavr` | D-16 cold builds (SAFE-07) | ✓ | `pio` at `/usr/local/bin/pio`; `avr-gcc (GCC) 7.3.0` | — |
| `.venv311` (py3.11) editable install | All host tests | ✓ | `3.11.16`; `firestarter.__file__` resolves to the worktree | — |
| Network to `gitlab.com` (pinned `infoic.xml`) | SAFE-09 evidence | ✓ | HTTP 200, 17,861,009 B, sha256 `cdd21319…06b8a` | — (already fetched; evidence recorded above) |
| `gh` CLI against `henols/firestarter_prom` | Reading gh#62 | ✓ | issue 62 read; state OPEN, 0 comments, 0 labels | — |
| `pdftotext` | W29C020C datasheet | ✓ | `/usr/bin/pdftotext` | — (already extracted) |
| **`gsd/v1.37-…` branch in the `firestarter` submodule** | Any firmware commit (SAFE-08) | ✗ | HEAD is `gsd/v1.36-dev-test-fidelity`, **0 ahead / 2 behind `origin/beta`**; no v1.37 branch in `git branch -a` | **None — this blocks firmware commits.** |
| `datasheets/0x05-FLASH-AMD-STD/W29C020.pdf` | `PROTOCOLS.md:108,111,114` citations | ✗ | no such directory in either repo | Not needed by this phase (§B.4 used the octopart copy) |

**Missing dependencies with no fallback:**
- **The firmware milestone branch does not exist.** The meta repo is on
  `gsd/v1.37-operator-safety-answered-reports-claim-hygiene`; `firestarter_app` is on the same branch; the
  `firestarter` submodule is on **`gsd/v1.36-dev-test-fidelity`**, clean, an ancestor of `origin/beta`.
  **The plan needs a Wave-0 task:** in `/workspaces/firestarter`, `git fetch origin && git checkout -b
  gsd/v1.37-operator-safety-answered-reports-claim-hygiene origin/beta`, before any D-12 edit. (Confirmed
  safe: HEAD and `origin/beta` differ only in `include/version.h`, so no citation in this document moves.)

**Missing with fallback:**
- `PROTOCOLS.md`'s `datasheets/0x05-FLASH-AMD-STD/*.pdf` citations point at files that exist in **neither**
  repo. A CLAIM-class finding (a doc naming a file that is not there), adjacent to CLAIM-09 but not in
  SAFE-08's scope. **Report; do not fix here.**

---

## Project Constraints (from CLAUDE.md)

From `/workspaces/CLAUDE.md`, `/workspaces/firestarter/CLAUDE.md`, `/workspaces/firestarter_app/CLAUDE.md`:

1. **NO COMMENTS IN PRODUCT SOURCE — hard rule, not overridable by a plan.** Covers everything under
   `firestarter/` and `firestarter_app/`. No GSD identifiers (`// Phase NNN`, `// D-06`, `// SAFE-08`), no
   plan citations, no rationale blocks. **Planners: do not write "add a comment citing X" into a plan and
   do not make "a comment exists" an acceptance criterion.** Rationale goes in `SUMMARY.md`, REQUIREMENTS
   traceability, or the commit message.
2. **Click docstrings in `firestarter_app` are user-facing `--help` text**, not comments, and are exempt —
   this matters directly for D-06's flag documentation.
3. **Constants and flag bits are duplicated** between `firestarter_app/firestarter/constants.py` and
   `firestarter/include/firestarter.h`. **Change both together.** (Not triggered by the recommended M3
   design, which adds no wire constant.)
4. **Serial-protocol changes** must stay in sync between `serial_comm.py` and `firestarter.cpp`. **Not
   triggered by M3.**
5. **`chip_database.json` is generated** — never hand-edit; overrides live in `~/.firestarter/database.json`.
   **Not triggered: SAFE-09 requires no DB change.**
6. **`main` is protected in all three repositories**; this project's close targets **`beta`**, not `main`
   (`.planning/config.json` → `git.base_branch = "beta"`).
7. **`messages.h` is codegen-generated and ID-only** — edit `/workspaces/tools/catalog/messages.toml` and
   run `sync_to_subrepos.sh`, never the generated header. **Triggered only if M1 wins.**

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|---|---|---|
| A1 | M1's `handle->protocol` compare-and-branch costs "more than 0 bytes" of AVR flash — stated a priori, **not measured**. | §A.1 | Low. D-16 mandates the measurement; this research deliberately did not pre-empt it (D-11). |
| A2 | `--ignore-unsupported` is the best flag name. This is a **recommendation from a vocabulary survey**, not a constraint. | §D.4 | Nil — D-06 names no flag; the planner may choose otherwise. |
| A3 | Option (a) (keep the empty `flash_5v_page_write_init`) is the safer disposition. Reasoned, not measured against a build. | §C.3 | Low. Both options are viable; the plan must state which. |
| A4 | The Caterina cliff on leonardo is `28672`. The literal is quoted from `size_baseline.json`'s `merge05_clause`; the `28672 − 25098 = 3574` arithmetic is mine. | §A.3 | Low. Not load-bearing for any decision; leonardo has 1808 B under BASE-01 either way. |
| A5 | The `firestarter_app` full suite (2337 tests) currently passes. **Collected but not run** — only the 53-test gate subset was executed. | §E.1 | Medium. A pre-existing red would be attributed to this phase. **The plan should run the full suite once, on a clean tree, before the first edit, to establish the baseline.** |
| A6 | No firmware native test goes red from deleting the `CMD_ERASE` arm. Derived from a complete `CMD_ERASE` + `0x05` cross-grep; **not** from running the suite post-deletion. | §C.4 | Low. `pio test -e native` is in the verify story and will settle it. |
| A7 | 301 rows across `0x05`/`0x06`/`0x0D` display an elevated VPP. Measured from the DB, but "displays" is inferred from the two gate conditions plus one observed `info` run on AE29F2008, not from running `info` on all 301. | §B.7 | Nil — the residual is filed as a backlog item, not planned. |

---

## Open Questions

1. **Which D-12 disposition for the emptied `flash_5v_page_write_init`?**
   - What we know: both options work; option (b) forces a `test_val_5v_page.cpp:332` rewrite.
   - What's unclear: whether the operator wants the dead call removed.
   - Recommendation: option (a), recorded with the reason. Escalate only if the phase record needs it.

2. **Does D-15's ROADMAP amendment belong to 183 or 185?**
   - What we know: D-15 says "amend it to depend on Phase 183" and lists it under SAFE-08's decisions.
   - What's unclear: D-08 names *three* documents as this phase's deliverable and the Phase 185 line is not
     one of them.
   - Recommendation: land it here. D-15 is explicit, and Phase 185 cannot amend its own dependency
     honestly after the fact. ⚠️ Use a **hand edit**, not `roadmap.update-plan-progress` — that verb
     clobbers the dependency table by positional overwrite.

3. **Where does the residual VPP-display question get filed?**
   - Recommendation: a backlog item (`999.x`), scoped to the *display* label across all three 5 V-only
     families, explicitly noting that `check_dispatch.py:90-95` already records the correct reading and
     that this is **not** a `build_db.py` correction.

---

## Sources

### Primary (HIGH confidence — read in this session)
- `firestarter/src/proms/flash_5v_page.cpp` (225 lines), `src/proms/flash_nor_unlock.cpp`,
  `src/eprom_operations.cpp`, `src/operation_utils.cpp`, `src/firestarter.cpp`, `src/proms/memory.cpp`,
  `src/proms/eprom.cpp`, `include/flash_utils.h`, `include/flash_5v_page.h`, `include/firestarter.h`,
  `include/proto_constants.h`
- `firestarter/scripts/check_erase_no_vpp.py`, `scripts/check_size_baseline.py`,
  `scripts/baseline/size_baseline.json`, `scripts/baseline/size_baseline_base01.json`
- `firestarter/test/native/avr/test_val_5v_page/test_val_5v_page.cpp`,
  `test/native/avr/test_dispatch/test_configure_memory.cpp`,
  `test/native/avr/_shared/validation_matrix.h`, `tests/fixtures/planted_erase_no_vpp_ctrl_write.cpp`
- `firestarter/CLAUDE.md`, `firestarter/PROTOCOLS.md`
- `firestarter_app/firestarter/{jp5_gate,sdp_capability,cli_handlers,database,chip_resolver,eprom_info,ic_layout,constants,chip_test}.py`
- `firestarter_app/tools/{build_db,check_dispatch,check_devtest_orchestrator}.py`
- `firestarter_app/firestarter/data/chip_database.json`, `firestarter_app/pyproject.toml`
- `/workspaces/tools/catalog/messages.toml`
- **Upstream `infoic.xml` @ `a8efaedc236c1d9718bd28299dfbb99536b010ff`** — re-fetched, HTTP 200,
  17,861,009 B, sha256 `cdd21319ae6cce2316ca2361a9fb82cba89b27b66bb78d58b01032a441106b8a`
- **gh#62** via `gh issue view 62 --repo henols/firestarter_prom`

### Secondary (MEDIUM confidence)
- [CITED: https://datasheet.octopart.com/W29C020C-90B-Winbond-datasheet-181529584.pdf] — Winbond W29C020C
  datasheet, fetched and `pdftotext`-extracted this session. Medium rather than high only because the
  equivalence to AE29F2008 is upstream-declared rather than vendor-declared (D-18's own framing).

### Tertiary (LOW confidence)
- None. No claim in this document rests on a web search or on training knowledge.

---

## Metadata

**Confidence breakdown:**
- SAFE-06 (host gate shape): **HIGH** — every file read in full; the call site, the field, and the data path all verified against the running tree, and the predicate's input observed in an actual `info` run.
- SAFE-07 (mechanism pricing): **HIGH on the specification and the procedure; the figures themselves are unmeasured by design** (D-16 assigns them to the phase). Toolchain availability measured, not assumed.
- SAFE-08 (blast radius): **HIGH** — tree-wide `/usr/bin/grep` on all three symbols plus `CMD_ERASE`; every line range re-derived; the two gate scripts actually executed.
- SAFE-09 (classification): **HIGH** — upstream re-fetched, datasheet extracted, gh#62 read, the `0x06` erase sequence matched byte-for-byte against the datasheet's own table. D-19's projection was tested on every leg and confirmed; D-23 traced to the call-chain level and settled.

**Research date:** 2026-09-11
**Valid until:** 2026-10-11 (30 days — the upstream `infoic.xml` is pinned to a commit and cannot drift; the in-repo citations drift with every firmware edit, so re-verify line ranges at execution time regardless).
