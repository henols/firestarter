# Phase 151: Protection Readability — `lock-status` - Research

**Researched:** 2026-08-20
**Domain:** Dual-repo (AVR firmware wire command + Python host CLI) protection-state readability; hand-curated family taxonomy; DB-wide class invariants; documentation of dead upstream metadata
**Confidence:** HIGH on everything measured in-tree (all counts, line numbers, band arithmetic, gate wiring). LOW on unwritten-firmware byte costs (labelled estimates). MEDIUM on datasheet-level claims that only `lockable-proms.md` carries.

**Measurement provenance convention used throughout:**
- `[FILE path:line]` — read directly from that file at that line, this session, against the working tree at meta `8e90dbf5` / fw `8286916` / app `9cc57c7`.
- `[CMD …]` — computed by the quoted command this session.
- `[ESTIMATE]` — my inference, not measured. Never treat as a fact.

---

## Summary

Everything CONTEXT.md's D-01…D-16 rely on is present in the tree, and every DB
count it quotes is correct — **all of D-09's and D-14's numbers verify exactly**.
What research changes is not the decisions but their *cost surface*, in four
places the discussion did not reach:

1. **There is no free firmware command slot that works.** `CMD_HW_VERSION 15` is
   indeed the top of the enum, but the JSON-parse gate in `parse_json` is the
   ordinal test `if (handle->cmd < CMD_READ_VPP)` — i.e. `cmd < 11`. Slots 0–10
   are fully consumed (CMD_SDP_LOCK's own comment records that 9 and 10 "were
   the only two free command values"). A new command at 16 is therefore parsed
   by *nothing*: `json_parse()` never runs, so `protocol-id`, `mem-size`,
   `bus-config` and `chip-id` never reach the handle, and `configure_memory()`
   is never called. D-01's "Claude's Discretion — command number" is not a free
   choice; it is a structural fork the planner must fund.
2. **Leonardo's MERGE-05 flash allowance is exactly consumed, to the byte, and
   RAM's is consumed on all three targets.** Live `flash_used` 27212 minus
   BASE-01 26906 is +306, and the effective allowance is 0 + 96 + 210 = **306**.
   RAM is +2 against a +2 exemption on all three. So *any* firmware growth —
   flash or RAM — needs a new named, SHA-attributed exemption. The a7w flash-
   ceiling move raised `flash_free` to 5556 B on leonardo but did **not** touch
   this axis; physical headroom and MERGE-05 headroom are different things and
   the latter is zero.
3. **The curated table's real size is 273 alias tokens over 217 DB entries, and
   `lockable-proms.md` cannot be matched to them literally.** Only 7 of the 190
   `0x06` entries have every alias token appearing verbatim in the doc, and
   **zero** of the 39 `0x10` entries do — because the doc writes families in
   elided shorthand (`MX29F010 / F020 / F040`). The curation is a human
   token→family mapping, not a lookup.
4. **`sdp_honesty` already has a landed production caller**, contradicting D-11's
   premise. `unreadable_state_caveat()` is called from `cli_handlers.py:2405`,
   `:2412` and `chip_test.py:1480`. Only `emission_summary()` and
   `map_unknown_cmd_to_outdated()` are still callerless.

**Two operator inputs, answered 2026-08-20, and both change conclusions:**

5. **`infoic.xml` does NOT carry the sequences — a clean, evidenced negative.**
   Checked first, on operator direction, against the same pinned revision the
   project cites (`a8efaedc…/infoic.xml`, loaded via
   `tools/derive_sdp_partition.py`'s own `_load_infoic_xml()` mechanism). The
   complete per-chip datum is **20 attributes, zero child elements, zero text
   content**. No attribute name matches `cmd|seq|unlock|protect|addr|command`. The
   AMD/JEDEC magic bytes `aa55`/`5555`/`2aaa` appear in **no attribute value** of
   any of the 11510 `<ic>` entries. `config` — the only blob-shaped field, and the
   single real candidate — is the literal string **`"NULL"` on all 101
   `protocol_id="0x05"` and all 897 `protocol_id="0x06"` entries**. The one unused
   field that varies on `0x06` (`chip_info` = `0x0000`/`0x00e3`/`0x00e4`) is a
   vendor cluster, not an address, and is **constant `0x0000`** across the whole
   `0x05` population. **`infoic.xml` is a chip-*parameter* database, not an
   algorithm database:** `protocol_id` *selects* an algorithm whose bytes live in
   the programmer's firmware. It does supply one useful datum — `chip_id`
   (`W29C020* → 0x0000da45`) — which is a **positive control for the mode entry**
   and says nothing about the status read. *(This is a different question from the
   settled negative about readability-from-flags, which stays closed.)*
   **Consequence:** both sequences are datasheet-only, so they can carry a citation
   comment and a pinned byte table but **can never have an element-wise proof** —
   a change detector, not a correctness proof.

6. **The operator has a `W29C020`, and C-10's "empty by construction" verdict is
   WITHDRAWN.** But `lockable-proms.md` is **genuinely ambiguous** about the bare
   part: the `:21` row key is `**W29C020 / W29C020C**` and covers both, while
   **all four** narrowing restatements (`:30`, `:335`, `:350`, and `:25`'s
   cross-reference) name `W29C020C` only — bare `W29C020` appears **exactly once**
   in 399 lines. The entry still refuses by default regardless, because the third
   alias `W29C022` is undocumented and D-06's unanimity is fail-closed, so the read
   is **`--force`-only even on the operator's own part**. The payoff chain is
   therefore real but narrow, and it **decomposes**: the *mode-entry* half is
   verifiable on silicon **today with zero new code** (`firestarter id W29C020`
   must return `0xDA45`), while the status *address* and *decode* have no
   independent oracle short of a destructive write→verify — which is the *indirect*
   method `lockable-proms.md:3` excludes from "readable" by definition.

**Primary recommendation:** plan the firmware half around the ordinal-gate fork
first (it decides the wire shape, the byte cost, and therefore which MERGE-05
exemption is being asked for), and plan the host half around a token-keyed table
whose class for `0x10` / `0x07` / `0x08` / `0x0B` / `0x0E` / `0x27` / `0x28` /
`0x29` / `0x34` is derived from `protocol-id` rather than curated per token —
that reduces the hand-curation from 953 tokens to 273 and makes D-12's partition
exhaustive by construction. Then, before any sequence byte is written: source the
`0x05` and `0x06` sequences from datasheets (`infoic.xml` is closed — finding 5),
budget them as **pinned tables with full citations rather than provable
sequences**, and surface C-17 (bare `W29C020` vs `W29C020C`) to the operator,
because it decides whether the operator's own part is inside the
documented-readable set and D-06 has no state that expresses "documented, but the
document's own summary declines to repeat the verdict for this alias".

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

Copied by reference, not re-transcribed, because CONTEXT.md is committed and one
copy is the point: `.planning/phases/151-protection-readability-lock-status/151-CONTEXT.md`
§`<decisions>`, decisions **D-01 through D-16** plus every `**Rejected:**` clause
under them. The planner MUST read that section verbatim. The binding shape, in
one line each, so a plan cannot be written without them:

- **D-01** Real silicon read, exposed as a **beta-only `dev lock-status`** via the existing `_DevGroup` / `channel.BETA_ONLY_DEV_COMMANDS` gate. *Rejected: host-only reporting from the curated table.* Cost accepted: `-D DEV_TOOLS` is in the shared `[env]` block so **all three AVR targets pay the bytes**; leonardo's MERGE-05 base band is 0 B must-not-grow.
- **D-02** The firmware read covers protocol **`0x06`** (AMD Autoselect) and the Winbond Product-ID boot-block status on the **`0x05`** rows. **Not `0x10`** — `0x10` is a fourth answer class (`not_implemented`), never "unprotected".
- **D-03** One operator-gated bench leg on the **W29C040**, framed as an exploratory **PROBE, never validation**. The table's readable verdict on `0x05` is gated to **W29C020C only**; W29C040/W29C040P is *variant-dependent*. No artifact may claim the `0x05` sequence is silicon-validated from this leg.
- **D-04** Against pre-command firmware, send it and map `MSG_ERR_UNKNOWN_CMD` → `FirmwareOutdatedError`, keyed on the message **id**. *Rejected: probing the firmware version first.*
- **D-05** The table is a **new Python module in `firestarter_app/firestarter/`**, shaped like `sdp_capability.py` — literal string literals, per-row citation comment, no loader, gated like `tools/check_sdp_capability_invariants.py` gates its neighbour. *Rejected: JSON under `firestarter/data/`; markdown-only under `doc/`.* `chip_database.json` is generated; the table does not live there.
- **D-06** **Three-state alias tokens, fail-closed**: `documented-readable` / `documented-not-readable` / `undocumented`. An entry answers only if **every** alias token is `documented-readable`; otherwise it refuses **naming the specific offending alias and its state**. Worked example: `W29C020,W29C020C,W29C022` must refuse naming `W29C022`. Consequence accepted: **no `0x05` row answers by default**.
- **D-07** **`--force` is the only path to an unadjudicated read**, labelled `unadjudicated_probe`, never a state claim.
- **D-08** Every answer **leads with a machine-stable class token**, then prose. Tests assert the token, not the wording. *Rejected: prose-only; `--json`.*
- **D-09** **Eight classes**: `protected` · `unprotected` · `not_readable` · `not_implemented` · `undocumented_alias` · `no_mechanism` · `firmware_outdated` · `unadjudicated_probe`. `no_mechanism` is a real, separate answer.
- **D-10** **Exit 0 only for a real silicon read** (`protected`/`unprotected`); a distinct non-zero for "cannot answer"; a separate non-zero for operational failure. Tests assert **token and code together, never the code alone**.
- **D-11** Refusal prose lives in an **extended `firestarter_app/firestarter/sdp_honesty.py`**. Accepted cost: the module's name says SDP while it will also carry Autoselect and boot-block wording.
- **D-12** LOCK-04 is enforced by a **DB-wide class invariant test**, not careful authoring: walk all 746 entries, resolve each to a class, assert the partition exhaustively, assert `protected`/`unprotected` are **structurally unreachable** without a silicon read, assert every readable-verdict row carries a citation. *Rejected: a phase-local `151-check-claims.py`.*
- **D-13** DATA-06's single authoritative statement goes in **`firestarter_app/doc/infoic-field-dictionary.md`**; the other two bit tables get a **one-line pointer**.
- **D-14** Cover **both siblings** (`protect_on_after` and `protect_off_before`), each with its own measurement.
- **D-15** The wording **carries the measurement, not a shrug**, and states plainly that **no runtime consumer exists in this release because `write --sdp-relock` is deferred to Backlog 999.28**.
- **D-16** DATA-06 ships with **no behaviour change, no new gate, and no `sdp_capability.py` edit**; `check_sdp_capability_invariants.py` Class 2(b) is **not weakened**.

### Claude's Discretion

Verbatim from CONTEXT.md §"Claude's Discretion":

> - Wire protocol shape for the new firmware command — command number, response framing, and whether the payload is a single status byte or a per-region structure. Note `MSG_OK_READY` extends with **zero** codegen (length-discriminated blob, read at a computed `ver_end`), and firmware `messages.h` **is codegen-generated and ID-only** — wording-only changes there produce a zero diff; edit the meta repo's `messages.toml` and regenerate.
> - Whether the read reports device-global or per-sector/per-region state, and how a multi-region answer renders under D-08's single leading class token.
> - Which named MERGE-05 exemption the new firmware bytes are funded under, and its framing.
> - How `permanence` is represented in the table separately from `readability` (`lockable-proms.md` treats them as independent axes, and W29C020C is the case where permanence matters most).
> - Whether `protect_off_before`'s `algorithm: 6` correlation (77 rows, the AMD Autoselect family) is worth a sentence in D-13's section. It is suggestive given D-02, but the research note's verdict — flags 14/15 cannot derive readability, `W29C020C` is flag-identical to `W29EE011` — stands and must not be relitigated.

### Deferred Ideas (OUT OF SCOPE)

Verbatim from CONTEXT.md §`<deferred>`:

> - **Fold lock state into `dev test` diagnostic reports, and/or add a `--json` output mode** — a real payoff named in the seed … but it is a new capability and belongs in its own phase. D-08 keeps the class token machine-stable so this stays cheap later.
> - **A live protection read for protocol `0x10`** (39 rows, Intel 0x90 command-register) — deliberately unimplemented per D-02; ships as the `not_implemented` class.
> - **Curating `W29C022`** — would flip the `W29C020,W29C020C,W29C022` entry to answerable with no rule change (D-06). Needs a datasheet, not an inference.
> - **Decoding `infoic.xml` bits 22 (`0x00400000`) and 9 (`0x200`)** — undocumented, no minipro constant; bit 22 set on the AT29C/W29C/W29EE page-write group, bit 9 observed only on MX29F040. Recorded in the research note's loose ends, declined here (D-14).
> - **`write --sdp-relock`** — Backlog **999.28**, deferred twice (v1.30 Phase 135, v1.32 Phase 150). Not this phase. Phase 152's OUT-01/OUT-04 must describe a **withdrawal, never a migration**, and OUT-05's claim gate rejects any outward text naming the command as shipped.
> - **A compensating bootloader-safe flash guard** — raised while the concurrent quick task `260820-a7w` removed the linker's protection over the bootloader region. The operator declined it there; noting it here because D-01's firmware growth now lands against a raised ceiling.

Plus CONTEXT.md §`<domain>` "Not in scope": folding lock state into `dev test`
reports or a `--json` mode; a live read for `0x10`; curating families beyond what
`lockable-proms.md` documents.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description (from `.planning/REQUIREMENTS.md` §LOCK / §DATA) | Research Support |
|----|-------------|------------------|
| **LOCK-01** | A hand-curated, family-level protection table records mechanism, readability and permanence, each row cited to `lockable-proms.md` + datasheet. | §"The Curated Table's Source Document" — 126 family rows across 18 numbered sections + 4 sub-sections enumerated; §Key vocabulary quoted; §"Sizing the Curation" gives the 273-token / 217-entry surface and proves literal matching is insufficient. §"Standard Stack" gives `sdp_capability.py`'s literal-frozenset + provenance-comment shape (D-05) and the AST gate that guards it. |
| **LOCK-02** | `lock-status <chip>` reports the protection state of a chip on families documented readable. | §"Firmware Wire-Protocol Design Inputs" — the CMD enum, the `cmd < CMD_READ_VPP` parse-gate fork, `is_memory_cmd()`'s access-control role, the four dispatch sites, and `hw_get_version` / `CMD_CHECK_CHIP_ID` as the two candidate templates. §"The `0x06` / `0x05` Read Sequences" gives the existing primitives and what must be newly written. |
| **LOCK-03** | On families where protection state is not readable — `0x0D`/SDP among them — refuse gracefully with a named reason and no fabricated value. | §"Host Patterns Being Extended" — `sdp_capability_for_entry`'s fail-closed unanimity and `(bool, reason)` shape, `split_part_number_tokens`' no-paren-strip rule, the `protocol-id` hard-fail; `sdp_honesty.unreadable_state_caveat()` quoted in full; `map_unknown_cmd_to_outdated` and every test that pins its wording. |
| **LOCK-04** | Never over-promises: distinguishes "unprotected" from "readability not supported", and no wording reads as a guarantee. | §"D-12's Invariant: Exact Shape" — the exhaustiveness hole (algorithm `0x34`), the token→algorithm functional invariant (zero tokens span two algorithms), the two rows missing `protect_*` keys, and the `resolve_chip` support-status pre-filter that makes 10 rows unreachable. §"Validation Architecture" gives the cheapest sufficient oracle per claim. |
| **DATA-06** | `protect_on_after` documented once as an advisory upstream hint with no runtime effect. | §"DATA-06's Documentation Home" — `infoic-field-dictionary.md`'s per-field entry shape, its §`flags` bit table at :107 with bits 14/15 at :120-121, the exact pointer lines in `package-details.md:43-44` and `protocol-flags.md:24-25`, the element-wise proof test to cite, `test_b15_page_size_corroboration.py` as the "documentation carrying a measured refutation" precedent, and **every D-14 count re-verified**. |

</phase_requirements>

---

## Project Constraints (from CLAUDE.md)

From `/workspaces/CLAUDE.md` (meta):
- Actual code lives in two sub-repos; the meta repo "tracks only `.planning/` and `.claude/`" — **this is now false**, see Contradiction C-1.
- **`chip_database.json` is generated**; user overrides go in `~/.firestarter/database.json`. Never hand-edit the generated file.
- **Serial protocol changes must be kept in sync** between `firestarter_app/firestarter/serial_comm.py` and `firestarter/src/firestarter.cpp`.
- **Constants and flag bits are duplicated** between `firestarter_app/firestarter/constants.py` and `firestarter/include/firestarter.h`. **Change both together.**
- Board differences: Uno 512-byte data buffer, Leonardo 1024.

From `/workspaces/firestarter/CLAUDE.md`:
- Dispatch is **solely** on `handle->protocol`; there is no secondary axis and no legacy-integer fallback. Unrecognised protocol (including 0) fail-closes to `configure_not_implemented()`.
- Dispatch reads named `PROTO_<NAME>` constants (`include/proto_constants.h`); `firestarter/doc/PROTOCOLS.md` is the **operator-approved** source of truth for the name set.
- `configure_eprom()` enables the 12 V VPP boost regulator — a hazard on a 5 V part. This is why `is_memory_cmd()` is documented as an **access-control gate, not hygiene**.

From `/workspaces/firestarter_app/CLAUDE.md`:
- `firestarter/data/chip_database.json` — "generated chip database (do NOT edit by hand)".
- `channel.py`: "**Never gate on an env var** — it fails open." (`dev_tools_enabled_by_env` is the one documented, fail-*closed*, exact-literal-`"1"` exception.)
- The `algorithm` wire field carries the upstream `protocol_id` integer and is the primary firmware dispatch key.

No project-local skill under `.claude/skills/` is triggered by this phase's work
(`devtest-rootcause` / `devtest-triage` are for `dev test` chip-failure triage;
`skill-writer` is for authoring skills). Their standing rules that *do* bind here:
**a skill must own its scripts** and **the generator may not invent fields absent
from `infoic.xml`** — the latter is DATA-04, which is exactly why LOCK-01's table
is hand-curated in a *Python module*, not emitted into the generated DB.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Curated family→(mechanism, readability, permanence) taxonomy (LOCK-01) | Host / Python package (`firestarter_app/firestarter/`) | Host / `doc/` (citation target only) | D-05: importable literal table, no loader. The datasheet claim is human knowledge; it cannot come from firmware or the generated DB. |
| Alias-token → class resolution + fail-closed unanimity (LOCK-03, D-06) | Host / pure predicate module | — | Mirrors `sdp_capability_for_entry`. Pure, no serial, no Click, so both the CLI and the invariant test can drive it. |
| Class-token + exit-code contract (D-08, D-10) | Host / CLI layer (`cli_handlers.py`) | Host / pure predicate (supplies the token) | The token is produced below the CLI so a test can assert it without a process; only `sys.exit` lives in the CLI. |
| Refusal / caveat prose (D-11) | Host / `sdp_honesty.py` | — | Single-copy honesty carrier, no `click` dependency, importable from a report layer. |
| Silicon protection read: bus setup, command sequence, status byte (LOCK-02, D-02) | Firmware / `src/proms/flash_nor_unlock.cpp` + `flash_5v_page.cpp` | Firmware / `flash_utils.cpp` (shared `byte_flip_t` primitives) | Only firmware drives the bus. The Autoselect/Product-ID entry-exit sequence must be one atomic firmware operation; a host-driven sequence would need per-cycle round trips. |
| Command admission / bus-config authorisation | Firmware / `include/firestarter.h::is_memory_cmd()` | Host gate (`check_is_memory_cmd_no_ifdef.py`) | Documented **access-control gate** — it decides which commands may call `configure_memory()` and therefore engage the VPP regulator. |
| Channel gating (beta-only) (D-01) | Host / `channel.py` + `cli_handlers.py` import-time registration | — | Firmware has no notion of channels; `-D DEV_TOOLS` is in the shared `[env]` block. Confirmed by `tests/test_dev_gate_reads_no_firmware_source.py`, which asserts the gate reads no firmware source at all. |
| `protect_on_after` / `protect_off_before` semantics (DATA-06) | Host / `doc/infoic-field-dictionary.md` | Host / two other bit tables (one-line pointers) | D-13/D-16: documentation only. No runtime tier owns these fields, and saying so is the deliverable. |
| Class assignment for algorithms with no curated family (`0x10`, UV-EPROM, SRAM/NVRAM, `0x34`) | Host / pure predicate, keyed on `protocol-id` | — | See §"Sizing the Curation": deriving these from `protocol-id` rather than curating 680 tokens is what makes D-12's partition exhaustive by construction. |

---

## ⚠ Live Firmware Size Figures (Priority 1 — read fresh, a7w has landed)

Quick task `260820-a7w` is **merged**: `git -C firestarter log --oneline -4`
`[CMD]` shows `8286916 test(260820-a7w): sever nine stranded merge05/default-mode
legs onto fullflash fixtures`, `f7d2297`, `ed084d6`, `283971d`. All figures below
were read from the committed files this session.

### Both baselines, per target

Read via `python3 -c "import json; …"` over the two files `[CMD]`.

**`firestarter/scripts/baseline/size_baseline.json`** (the LIVE / default baseline; `meta.generated` = `2026-08-20`, `meta.firmware_tree_sha` = `75784f68cb3d62df41f10f5bd9195ec52b3fdd12`):

| target | `flash_used` | `flash_total` | `flash_free` | `ram_used` | `ram_total` | `ram_free` |
|--------|-------------:|--------------:|-------------:|-----------:|------------:|-----------:|
| `uno` | 25130 | **32768** | **7638** | 1575 | 2048 | 473 |
| `uno328pb` | 25180 | **32768** | **7588** | 1581 | 2048 | 467 |
| `leonardo` | **27212** | **32768** | **5556** | 2016 | 2560 | 544 |

**`firestarter/scripts/baseline/size_baseline_base01.json`** (BASE-01, the frozen MERGE-05 reference):

| target | `flash_used` | `flash_total` | `flash_free` | `ram_used` | `ram_total` | `ram_free` |
|--------|-------------:|--------------:|-------------:|-----------:|------------:|-----------:|
| `uno` | 24824 | **32768** | 7944 | 1573 | 2048 | 475 |
| `uno328pb` | 24874 | **32768** | 7894 | 1579 | 2048 | 469 |
| `leonardo` | 26906 | **32768** | 5862 | 2014 | 2560 | 546 |

`meta.flash_ceiling_move_260820_a7w` in the live baseline states the trade in the
operator's own accepted terms, quoted verbatim in part `[FILE firestarter/scripts/baseline/size_baseline.json]`:

> WHAT WAS TRADED AWAY, per target: uno forfeits 512 B (optiboot), uno328pb forfeits 384 B (the urclock bootloader the MiniCore builder was subtracting), leonardo forfeits 4096 B (Caterina). The linker no longer protects any of those three regions — on leonardo specifically, firmware that grows past the old 28672 B ceiling will now be linked into and flashed over Caterina, the USB bootloader … No compensating guard was added; this is documentation of an accepted trade, not a new gate. CONCRETE EXPRESSION: leonardo's flash_free moved from 1460 B to 5556 B — that entire 4096 B increase is Caterina's forfeited region now counted as usable headroom, not new flash.
>
> MERGE-05's growth axis is untouched by either edit: flash_used is byte-identical here and in BASE-01 … and none of the five MERGE-05 band/exemption literals in scripts/check_size_baseline.py moved.

`platformio.ini` carries `board_upload.maximum_size = 32768` on all three AVR envs
— `[FILE firestarter/platformio.ini:46]` (uno), `:75` (uno328pb), `:95` (leonardo) —
plus the new `pre:zero_bootloader_reserve.py` SCons hook in `[env]`'s
`extra_scripts` `[FILE firestarter/platformio.ini:30-32]`, which zeroes MiniCore's
384 B urclock subtraction so the INI override actually reaches `uno328pb`'s
reported total.

### The MERGE-05 band arithmetic, exactly

All five literals, each with its measured line number `[FILE firestarter/scripts/check_size_baseline.py]`:

| literal | value | line | scope |
|---------|------:|-----:|-------|
| `MERGE05_UNO_CLASS_FLASH_BAND` | 64 | **:138** | flash, uno-class only (`leonardo` band is the inline literal `0`) |
| `MERGE05_DEFECT_FIX_EXEMPTION_BYTES` | 96 | **:182** | flash, all three targets |
| `MERGE05_PAGE_SIZE_SEAM_EXEMPTION_BYTES` | 210 | **:240** | flash, all three targets |
| `MERGE05_PAGE_SIZE_SEAM_RAM_EXEMPTION_BYTES` | 2 | **:282** | **RAM only**, all three targets |
| (inline) leonardo flash band | `0` | **:414** | inside `_merge05_flash_allowance` |

**CONTEXT.md's two quoted literals verify exactly: 96 and 210.** CONTEXT.md does
not mention the third and fourth (the 64 B uno-class band and the 2 B RAM
exemption); both are live and load-bearing.

The allowance resolver, quoted in full `[FILE firestarter/scripts/check_size_baseline.py:414-419]`:

```python
    band = 0 if env == "leonardo" else MERGE05_UNO_CLASS_FLASH_BAND
    band_label = "leonardo" if env == "leonardo" else "uno-class"
    defect_exemption = MERGE05_DEFECT_FIX_EXEMPTION_BYTES
    seam_exemption = MERGE05_PAGE_SIZE_SEAM_EXEMPTION_BYTES
    allowance = band + defect_exemption + seam_exemption
    return band, defect_exemption, seam_exemption, allowance, band_label
```

and the RAM resolver `[:422-432]` returns `(MERGE05_PAGE_SIZE_SEAM_RAM_EXEMPTION_BYTES, "page-size-seam")`,
uniform across all three targets.

**Effective ceilings and remaining headroom** `[CMD arithmetic over the two baselines above]`:

| target | BASE-01 flash | allowance | flash ceiling | live flash | **remaining MERGE-05 flash headroom** |
|--------|--------------:|----------:|--------------:|-----------:|--------------------------:|
| `leonardo` | 26906 | 0 + 96 + 210 = **306** | 27212 | 27212 | **0 B** |
| `uno` | 24824 | 64 + 96 + 210 = **370** | 25194 | 25130 | **64 B** |
| `uno328pb` | 24874 | 370 | 25244 | 25180 | **64 B** |

| target | BASE-01 ram | tolerance | ram ceiling | live ram | **remaining RAM headroom** |
|--------|------------:|----------:|------------:|---------:|--------------:|
| `leonardo` | 2014 | 2 | 2016 | 2016 | **0 B** |
| `uno` | 1573 | 2 | 1575 | 1575 | **0 B** |
| `uno328pb` | 1579 | 2 | 1581 | 1581 | **0 B** |

**The two figures the planner must not conflate.** Leonardo's *physical* free
flash is 5556 B (`flash_free`, materially larger post-a7w). Leonardo's *MERGE-05*
flash headroom is **0 B**. The a7w change moved the first and deliberately left
the second alone — the baseline's own note says so in the words quoted above. So:

- **Any** new firmware flash byte on **any** AVR target requires a **third named,
  SHA-attributed flash exemption**. On uno-class there is 64 B of band left, but
  the band is not an allowance for new features — it is the pre-existing
  uno-class tolerance, and `leonardo`'s 0 B is the binding constraint anyway.
- **Any** new firmware RAM byte on **any** target requires a **second named RAM
  exemption**. This is the one D-01 did not name and the planner must fund
  separately: `MERGE05_PAGE_SIZE_SEAM_RAM_EXEMPTION_BYTES`'s own comment says
  `SCOPE: RAM only. This constant does not touch MERGE05_PAGE_SIZE_SEAM_EXEMPTION_BYTES
  or either flash band literal` `[FILE .../check_size_baseline.py:277-281]`. A
  single `uint8_t` status field on `firestarter_handle_t` costs 1 B of RAM and
  therefore trips this. (AVR aligns every scalar to 1 byte — no padding absorbs
  it; the 210/2 exemption's own comment records exactly this for the `uint16_t
  page_size` field `[:249-252]`.)

### How a THIRD named exemption is added — exact shape and every site

Derived by reading the two existing exemptions' full comment blocks
`[FILE .../check_size_baseline.py:140-182]` and `:184-240`, plus the RAM one
`:242-282`. The convention is uniform and explicit:

1. **A new module-level literal**, immediately after the existing ones, with a
   comment block that MUST contain, in this order:
   - what the bytes **ARE**, itemised, with the **firmware commit SHAs** that
     introduced them (`96` cites `eb563d2` and `ebe9cb3`; `210` cites `58c6a3c`
     and `28bf089`);
   - the measured figure **per target**, and a pointer to the cold-capture
     transcript it was read from (Phase 149 used
     `.planning/phases/149-…/149-SIZE-TRANSCRIPTS.md`);
   - a **"WHY an exemption"** block rejecting the same three alternatives:
     (a) NOT a re-anchor of `size_baseline_base01.json`, (b) NOT a widening of
     `MERGE05_UNO_CLASS_FLASH_BAND` or the leonardo 0 B band, (c) NOT shrinking
     the change to fit;
   - a **"tripwire stays ARMED"** clause naming the specific test that feeds a
     planted `allowance + 1` log and asserts exit 1;
   - a **`SCOPE:`** line (`flash only` or `RAM only`).
2. **`_merge05_flash_allowance()` (`:389-419`)** — add the term to the returned
   tuple and to `allowance`. It is documented as the **sole consumer** of all
   three flash literals, and the docstring explicitly forbids summing exemptions
   into one another: *"Adding the page-size-seam exemption into the existing
   defect-fix exemption's value would destroy exactly this property and launder
   Phase 149's growth into Phase 145's number."* So the return becomes a
   6-tuple, not a widened 5-tuple.
3. **`compare_avr_policy_merge05()`'s FAIL message (`:483-488`)** — the failure
   string prints the full decomposition (`band {band} B + defect-fix exemption
   {defect_exemption} B + page-size-seam exemption {seam_exemption} B`); the new
   term must appear there too.
4. **`main()`'s PASS-line builder (`:684-691`)** — the compact form
   `[{flash_delta:+d}<={allowance}=band{band}+exempt{defect_exemption}+seam{seam_exemption}]`
   gains a term. **Note the trap:** `test_default_mode_is_unchanged_by_the_new_flag`
   asserts `"<=64" not in result.stdout` for default mode `[FILE firestarter/tests/test_check_size_baseline.py:904-907]` — a
   new token must not accidentally emit that substring in default mode.
5. **The module docstring (`:8-92`)** — enumerates every exemption and its scope
   (`:21-38`); it is prose that has been kept in lockstep so far.
6. **`firestarter/scripts/baseline/size_baseline.json`** — `meta.deltas_vs_base01`
   must gain the new admission; `avr_targets.*.flash_used` / `ram_used` must be
   re-recorded from a **cold** triple-target measure. The `flash_total` invariant
   sites CONTEXT.md cites are `compare_avr` **`:374`** and
   `compare_avr_policy_merge05` **`:499`** — both verified at those exact lines.
7. **`firestarter/tests/test_check_size_baseline.py`** — re-derived planted
   fixtures (see next sub-section).
8. **`size_baseline_base01.json` must NOT be re-anchored on its growth axis.**
   `test_base01_is_not_re_anchored_by_the_new_exemption` `[FILE firestarter/tests/test_check_size_baseline.py:704-745]`
   pins `flash_used` 24824/24874/26906 and `ram_used` 1573/1579/2014 as literals,
   plus `flash_total == 32768` on all three (a7w licensed the board-identity axis
   to move and re-pinned it at the new value). It **also source-scans the checker**
   for the exact strings `"MERGE05_UNO_CLASS_FLASH_BAND = 64"` and
   `"MERGE05_DEFECT_FIX_EXEMPTION_BYTES = 96"` — so those two literals are
   machine-frozen. It does **not** currently pin `= 210`; adding a `= <new>` pin
   for the third exemption is the natural extension and would be consistent with
   the pattern, but is not required by any existing assertion.

### Which legs redden, and the fixture families they read

`firestarter/tests/test_check_size_baseline.py` is 907 lines with **14** test
functions `[CMD grep -n "^def test"]`. a7w severed nine legs onto **two new
fixture families**; the module docstring records this at `:183-272` and names them.
The families that now exist under `firestarter/tests/fixtures/` `[CMD ls]`:

| family | files | role |
|--------|-------|------|
| **`captured_build_fullflash_{uno,uno328pb,leonardo}.log`** | 3 | Family A — default-mode REAL cold logs at `flash_total 32768`. Read by `test_clean_avr_all_three_envs_pass`, `test_default_mode_is_unchanged_by_the_new_flag`, `test_baseline_seam_precedence_flips_clean_log_to_fail`. |
| **`merge05_base01_anchor_fullflash_{…}.log`** | 3 | Family B — merge05 anchor logs (delta 0 vs BASE-01), only the `Flash:` total changed to 32768. Read by `test_policy_merge05_permits_the_measured_landing_deltas`. |
| **`merge05_defect_fix_fullflash_{…}.log`** | 3 | Family B — the +96 B defect-fix arm. Read by `test_policy_merge05_admits_the_documented_defect_fix` Arm 1. |
| **`planted_size_baseline_policy_{uno_over_band,leonardo_growth,ram_moved}_fullflash.log`** | 3 | Family B — the three armed tripwires. |
| **`planted_size_baseline_flash_regression_fullflash.log`** | 1 | Family A — default-mode +512 B plant (27212 + 512 = 27724). |
| retired but **not deleted**: `captured_build_{uno,uno328pb,leonardo}.log`, `captured_build_v132_*.log`, `merge05_base01_anchor_{…}.log` (non-fullflash), `planted_size_baseline_policy_*` (non-fullflash), `planted_size_baseline_flash_regression{,_v132}.log` | 12 | Left in place deliberately — the docstring at `:262-272` says deleting them "would erase a still-legible record". |

Measured `Flash:` / `RAM:` lines in every live fixture `[CMD grep -E "^(RAM|Flash):" …]`:

| fixture | flash used/total | ram used/total | delta vs its baseline |
|---------|-----------------:|---------------:|----------------------|
| `captured_build_fullflash_leonardo.log` | 27212 / 32768 | 2016 / 2560 | 0 vs LIVE (clean) |
| `captured_build_fullflash_uno.log` | 25130 / 32768 | 1575 / 2048 | 0 vs LIVE |
| `captured_build_fullflash_uno328pb.log` | 25180 / 32768 | 1581 / 2048 | 0 vs LIVE |
| `merge05_base01_anchor_fullflash_leonardo.log` | 26906 / 32768 | 2014 / 2560 | +0 vs BASE-01 |
| `merge05_defect_fix_fullflash_leonardo.log` | 27002 / 32768 | 2014 / 2560 | **+96** vs BASE-01 |
| `planted_size_baseline_policy_leonardo_growth_fullflash.log` | **27213** / 32768 | 2014 / 2560 | **+307** = allowance 306 **+1** → must exit 1 |
| `planted_size_baseline_policy_uno_over_band_fullflash.log` | **25195** / 32768 | 1573 / 2048 | **+371** = allowance 370 **+1** → must exit 1 |
| `planted_size_baseline_policy_ram_moved_fullflash.log` | 24824 / 32768 | **1576** / 2048 | ram **+3** = tolerance 2 **+1** → must exit 1 |
| `planted_size_baseline_flash_regression_fullflash.log` | **27724** / 32768 | 2016 / 2560 | +512 vs LIVE → must exit ≠ 0 |

**Legs that go RED when the band moves (i.e. when a third exemption is added) —
these are the ones that must be severed onto a NEW fixture family, never edited
in place:**

| leg | line | why it reddens |
|-----|-----:|----------------|
| `test_policy_merge05_fires_on_leonardo_growth` | :799 | Its plant is `allowance + 1 = 307`. Widen the allowance and +307 falls **inside** it → the leg goes falsely green while still claiming to prove a firing. The docstring at `:748-762` records that this exact re-derivation was already needed twice (from +161 B, and again at Phase 149). |
| `test_policy_merge05_admits_the_documented_defect_fix` **Arm 2** | :573 | Shares the leonardo-growth plant; same failure mode. |
| `test_policy_merge05_fires_on_uno_class_over_band` | :748 | Plant is `370 + 1 = 371`; same. It asserts the message text `allowance of 370 B` and the three-term decomposition, so the **assertion strings move too**. |
| `test_policy_merge05_fires_on_ram_move` | :839 | Only if a **RAM** exemption is added. Asserts `"delta=+3"`, `"ram allowance of 2 B"` and `"page-size-seam exemption 2 B"` verbatim `[FILE …:869-881]`. |
| `test_clean_avr_all_three_envs_pass` | :313 | Default mode, **strict equality** against the LIVE baseline (`compare_avr`, `:358-386`). Re-recording `size_baseline.json`'s `flash_used`/`ram_used` makes the current `captured_build_fullflash_*` fixtures stale → RED for two reasons at once (used **and** total-agnostic). Needs a new captured family from the post-151 cold build. |
| `test_default_mode_is_unchanged_by_the_new_flag` | :883 | Same fixtures, same reason. |
| `test_planted_flash_regression_flips_checker_to_failure` | :372 | Its +512 B offset is derived from `captured_build_fullflash_leonardo.log`'s 27212; re-derive from the new figure. |
| `test_baseline_seam_precedence_flips_clean_log_to_fail` | :455 | Reads `captured_build_fullflash_leonardo.log` as the "genuinely clean against the live baseline" control; if that stops being clean, the leg proves nothing about the env seam. Its docstring at `:462-480` is an explicit record of this exact leg having previously proven nothing for precisely that reason. |
| `test_base01_is_not_re_anchored_by_the_new_exemption` | :704 | Does **not** redden (BASE-01 is not touched) — but it is the leg that *enforces* BASE-01 staying frozen, and it must be extended if a `= <new>` literal pin is added. |
| `test_clean_native_both_envs_pass` | :347 | Reddens if a firmware **native test suite** is added — see the next sub-section. |

**Legs unaffected:** `test_planted_unparseable_log_exits_exactly_2` (:401),
`test_planted_suites_errored_flips_checker_to_failure` (:422),
`test_never_vacuous_with_no_logs_and_no_rebuild` (:438),
`test_policy_merge05_permits_the_measured_landing_deltas` (:493 — delta 0, a
widened allowance cannot break a 0 delta).

**Prior-phase lesson, restated as a constraint:** sever affected legs onto a NEW
fixture family; do **not** edit shared fixtures in place; and never write "tests
byte-unchanged" or "fixtures byte-identical" as an acceptance criterion — the
a7w and 149-07 severances are the in-tree record of why.

### Cold re-measure recipe

Per CONTEXT.md D-01 and the baselines' own `generated_by` note, the recorded
figures are TRANSCRIBED from three cold logs, each produced by
`rm -rf .pio/build/<env>` then **exactly one** `pio run -e <env>` invocation. The
checker's own `--rebuild` path instead runs `pio run -t clean -e <env>` then
`pio run -e <env>` `[FILE firestarter/scripts/check_size_baseline.py:535-541]` —
a different (warm-cache) shape. **I did not run any build this session.** The
figures above are all read from committed files.

The verification command, once the new baseline is recorded:

```bash
cd firestarter && python3 scripts/check_size_baseline.py --policy merge05 \
  --baseline scripts/baseline/size_baseline_base01.json \
  --avr-log uno=<log> --avr-log uno328pb=<log> --avr-log leonardo=<log>
```

Expected PASS-line form on leonardo today: `leonardo(flash=27212/32768[+306<=306=band0+exempt96+seam210],ram=2016/2560[+2<=2=seam2])`.

---

## Firmware Wire-Protocol Design Inputs (Priority 2)

### The full `CMD_*` enum, with line numbers

`[FILE firestarter/include/firestarter.h]`:

| line | define | value | notes |
|-----:|--------|------:|-------|
| :48 | `CMD_FRAME_MAX` | `DATA_BUFFER_SIZE` | **not a command code** — largest legit JSON frame; has its own parity gate |
| :58 | `CMD_IDLE` | 0 | firmware-internal state; no shipped host path emits it |
| :59 | `CMD_READ` | 1 | |
| :60 | `CMD_WRITE` | 2 | |
| :61 | `CMD_ERASE` | 3 | |
| :62 | `CMD_BLANK_CHECK` | 4 | |
| :63 | `CMD_CHECK_CHIP_ID` | 5 | |
| :64 | `CMD_VERIFY` | 6 | |
| :67 | `CMD_DEV_ADDRESS` | 7 | **inside `#if DEV_TOOLS`** (`:66`–`:69`) |
| :68 | `CMD_DEV_REGISTER` | 8 | **inside `#if DEV_TOOLS`** |
| :85 | `CMD_SDP_UNLOCK` | 9 | unconditional |
| :86 | `CMD_SDP_LOCK` | 10 | unconditional |
| :88 | `CMD_READ_VPP` | 11 | |
| :89 | `CMD_READ_VPE` | 12 | |
| :90 | `CMD_FW_VERSION` | 13 | |
| :91 | `CMD_CONFIG` | 14 | |
| :92 | `CMD_HW_VERSION` | **15** | **highest value — CONTEXT.md verified ✓** |

Next unused integer is **16**. But see the fork below: 16 is not usable as-is.

### ⚠ The ordinal parse gate — the finding that reframes "command number"

`[FILE firestarter/src/firestarter.cpp:74-109]`, quoted at the decision point:

```c
    if (handle->cmd < CMD_READ_VPP) {
        json_parse(handle->data_buffer, tokens, token_count, handle);
        // v1.22 Phase 119 (LOCK-03, D-02): is_memory_cmd() replaces the old
        // `#ifdef DEV_TOOLS` / `handle->cmd < CMD_DEV_ADDRESS` ordinal
        // guard. …
        if (is_memory_cmd(handle->cmd)) {
            …
            if (!op_execute_function(configure_memory, handle)) {
                LOG_ERROR_ID(MSG_ERR_SETUP);
                return false;
            }
        } else {
#if DEV_TOOLS
            …
#endif
        }
    } else if (handle->cmd == CMD_CONFIG) {
        …
    }
    return true;
```

Consequences, stated plainly:

- `json_parse()` is called **only** for `cmd < 11`. A command numbered 16 falls
  into neither arm, so `handle->protocol`, `handle->mem_size`, `handle->chip_id`,
  the bus config and the pin map are all **never populated**.
- `configure_memory()` is called **only** for `cmd < 11` **and**
  `is_memory_cmd(cmd)`. A command at 16 gets no protocol handler at all — no
  `firestarter_operation_main`, no `firestarter_get_data`.
- **There is no free slot below 11.** `CMD_SDP_LOCK`'s own comment says so:
  *"Slots 9 and 10 were the only two free command values"* `[FILE firestarter/include/firestarter.h:73-75]`.
- A second, independent ordinal-range guard exists at `[FILE firestarter/src/firestarter.cpp:132-142]`
  (`if (handle->cmd > CMD_IDLE && handle->cmd < CMD_READ_VPP)`), gating **three
  DBG_\* debug lines only**. Its comment explicitly says it was *"deliberately
  NOT converted to is_memory_cmd()"* because it *"gates diagnostic output only …
  never hardware configuration, so it is not an admission gate and D-03's safety
  argument does not apply here."* This is a *second* site that silently excludes
  a cmd-16 command from debug output.

So the planner's real fork is: **(a)** change the parse gate at `:77` (e.g. to
`is_memory_cmd(handle->cmd) || handle->cmd < CMD_READ_VPP`) — a change to a
safety-adjacent ordinal test with its own history; or **(b)** re-order the enum
so the new command sits below 11, which breaks wire compatibility with every
shipped firmware and every host constant; or **(c)** make the read a *non*-memory
command and have the host supply everything, which is not possible because
`firestarter_get_data` is a protocol-handler function pointer set by
`configure_memory`. Option (a) is the only one that does not break the wire.
**[ESTIMATE]** option (a) costs on the order of a dozen flash bytes (one extra
call to a `static inline` predicate that is already emitted); the sequences and
the new dispatch arms dominate.

### `is_memory_cmd()` — the access-control gate, and every site that mirrors it

`[FILE firestarter/include/firestarter.h:133-146]`, the whole body:

```c
static inline bool is_memory_cmd(uint8_t cmd) {
    switch (cmd) {
        case CMD_READ:
        case CMD_WRITE:
        case CMD_ERASE:
        case CMD_BLANK_CHECK:
        case CMD_CHECK_CHIP_ID:
        case CMD_VERIFY:
        case CMD_SDP_UNLOCK:
        case CMD_SDP_LOCK:
            return true;
        default:
            return false;
    }
}
```

Its own preamble (`:95-132`) names the hard constraints a new arm must respect:
**no preprocessor conditional of any kind inside the body**; `static inline`, in
this header (because `[env:native]`'s `build_src_filter` compiles only
`src/proms/`, `src/boards/rurp_serial_utils.cpp` and `src/json_parser.c`, so a
definition elsewhere would not link into the native test binary); and it **MUST
NOT name `CMD_DEV_ADDRESS` / `CMD_DEV_REGISTER`**. It is documented as *"an
ACCESS-CONTROL GATE, not hygiene … configure_eprom() (reached only through this
gate) enables the 12V VPP boost regulator — a hazard on a 5V part."*

Every site that mirrors the 8-command set — all must move together
`[CMD grep -rn "is_memory_cmd" --include=*.py --include=*.cpp --include=*.h --include=*.c]`:

| # | site | shape | CI-covered? |
|---|------|-------|-------------|
| 1 | `firestarter/include/firestarter.h:133` | the predicate itself | yes (compiled everywhere) |
| 2 | `firestarter/include/rurp_pinmap_guard.h:90` | `rurp_pinmap_refuses(cmd)` → `return is_memory_cmd(cmd);` — **delegates, does not re-list**, deliberately (`:37-48`) | no (see #5) |
| 3 | `firestarter/test/native/avr/test_cmd_admission/test_cmd_admission.cpp:66-88` | **exhaustive `[0,255]` truth table** with the literal expected set `{1,2,3,4,5,6,9,10}` written as **bare numeric literals** so it compiles under `native_nodevtools` | **yes** — in both `native` and `native_nodevtools` test_filters |
| 4 | same file, `:107-134` | negative controls: `is_memory_cmd(7)`/`(8)` false, `CMD_IDLE` false, and a named list (`CMD_READ_VPP`, `CMD_READ_VPE`, `CMD_FW_VERSION`, `CMD_CONFIG`, `CMD_HW_VERSION`) false | yes |
| 5 | `firestarter/test/native/avr/test_pinmap_provisional/test_pinmap_provisional.cpp:98-132` | *"Eight per-command cases, D-12's exact set (is_memory_cmd()'s set), never one aggregate loop"* + a `rurp_pinmap_refuses` truth-table negative control | **NO CI LEG** — see §"Test/CI Environment Facts" |
| 6 | `firestarter_app/tools/check_is_memory_cmd_no_ifdef.py:108-120` | `_EXPECTED_CMD_NAMES` — a **frozen 8-name frozenset**, whose own comment reads *"Adding a ninth memory command is a DELIBERATE act that must edit this line — it is not auto-derived from the header"* | via `pytest` (`tests/test_check_is_memory_cmd_no_ifdef.py`) |

### The `loop()` dispatch switch

`[FILE firestarter/src/firestarter.cpp:283-354]` — `switch (handle.cmd)` with arms
at `:289 CMD_READ`, `:292 CMD_WRITE`, `:295 CMD_VERIFY`, `:298 CMD_ERASE`,
`:301 CMD_BLANK_CHECK`, `:304 CMD_CHECK_CHIP_ID`, `:322 CMD_SDP_UNLOCK`,
`:325 CMD_SDP_LOCK`, `:328-329 CMD_READ_VPP/CMD_READ_VPE`, `:332 CMD_IDLE`,
`:334 CMD_FW_VERSION`, `:338 CMD_HW_VERSION` (inside `#ifdef HARDWARE_REVISION`),
`:343/:346 CMD_DEV_REGISTER/CMD_DEV_ADDRESS` (inside `#if DEV_TOOLS`),
`:351 CMD_CONFIG`, and `:355 default: LOG_ERROR_ID_U8(MSG_ERR_UNKNOWN_CMD, handle.cmd)`.

The `default:` arm **is** D-04's mechanism: any firmware predating the new command
answers `MSG_ERR_UNKNOWN_CMD` with the command number as a `u8` param.

### Per-protocol handler dispatch — two more sites

A new command also needs an arm in each `configure_*` it must work under:

- `[FILE firestarter/src/proms/flash_nor_unlock.cpp:31-51]` — `configure_flash_nor_unlock`'s
  `switch (handle->cmd)` has arms for `CMD_WRITE`, `CMD_ERASE`, `CMD_BLANK_CHECK`,
  `CMD_CHECK_CHIP_ID` only. Note `:33` sets
  `handle->firestarter_operation_init = flash_nor_unlock_generic_init` **before**
  the switch, so an unmatched command inherits a chip-ID-check init with a NULL
  main.
- `[FILE firestarter/src/proms/flash_5v_page.cpp:41-59]` — `configure_flash_5v_page`'s
  switch, same four arms, **no** pre-switch init assignment → an unmatched command
  gets init **and** main both NULL.
- `firestarter/doc/PROTOCOLS.md` is the operator-approved handler map
  `[FILE firestarter/doc/PROTOCOLS.md:60-70]`: `0x05` → `configure_flash_5v_page()`
  (`flash_5v_page.cpp`), `0x06` → `configure_flash_nor_unlock()`
  (`flash_nor_unlock.cpp`), `0x0D` → `configure_eeprom28c()` (`eeprom_28c.cpp`),
  `0x10` → `configure_flash_intel()` (`flash_intel.cpp`), `0x34` + infeasible
  `0x11/0x2A/0x2B/0x2C` → `configure_not_implemented()`. Row counts in that doc's
  §1 table (`:45-52`) are 27 / 190 / 84 / 39 — **all four match the live DB**
  (see §"Re-derived DB Counts").

### The host constant block, and its bidirectional parity gate

`[FILE firestarter_app/firestarter/constants.py:54-102]`. Header comment at `:54`:
`# Wire-protocol command codes — Firmware sync: firestarter.h`. Values
`COMMAND_READ 1` … `COMMAND_HW_VERSION 15` mirror firmware exactly; then
`COMMAND_NAMES` (`:86-102`) maps all 15 to display strings.

`COMMAND_NAMES` is **load-bearing, not cosmetic** — its own comment
`[:67-76]`: *"`COMMAND_NAMES[cmd]` is dereferenced by `_setup_operation`
(eprom_operations.py:329) and again by `_operation_context` (eprom_operations.py:405)
— a missing entry is a KeyError at operation setup, not a cosmetic display gap."*

`firestarter_app/tests/test_revision_constants_parity.py` is the gate. Measured
shape `[CMD grep -n "COMMAND_\|CMD_"]`:

- It **scans `firestarter/include/firestarter.h`** for every `#define` of a name
  beginning `CMD_` or `FLAG_` (`:296-300`) and maps `CMD_X → COMMAND_X` (`:334-338`).
- It is **bidirectional** (`:379` "Bidirectional CMD_* parity check body") — a
  firmware-only or host-only addition fails it.
- A **separate leg** asserts every non-exempt mapped host constant is also a key
  in `COMMAND_NAMES` (`:69-71`).
- The exemption map (`:190-193`) is exactly four entries: `CMD_IDLE: None`,
  `CMD_FRAME_MAX: "CMD_FRAME_MAX"`, `CMD_DEV_ADDRESS: "COMMAND_DEV_ADDRESS"`,
  `CMD_DEV_REGISTER: "COMMAND_DEV_REGISTERS"` (name-mismatched: singular in
  firmware, plural in host).
- It is **`skipif`-guarded on firmware presence** and therefore **fails OPEN** in
  a checkout without the sibling repo — the documented devcontainer/worktree trap.

So a new `CMD_LOCK_STATUS 16` requires `COMMAND_LOCK_STATUS = 16` **and** a
`COMMAND_NAMES` entry, in the same change, or this gate goes red (when the
sibling is present) or silently passes (when it is not).

### Response framing options

**Option 1 — an OK id-frame with u8 params (the cheapest, and the closest working
precedent).** `hw_get_version` is a single-shot query that returns two `uint8_t`s
and finishes `[FILE firestarter/src/hardware_operations.cpp:104-113]`:

```c
bool hw_get_version(firestarter_handle_t* handle) {
    LOG_DEBUG_ID_SUB(DBG_GET_HW_VERSION);
    rurp_configuration_t* rurp_config = rurp_get_config();
    uint8_t physical  = (uint8_t)rurp_get_physical_hardware_revision();
    uint8_t effective = (rurp_config->hardware_revision < 0xFF)
                        ? (uint8_t)rurp_config->hardware_revision
                        : 0xFF;  // P-02 sentinel: no override active
    LOG_OK_ID_U8_U8(MSG_OK_REV, physical, effective);
    return true;
}
```

Note the **`0xFF` sentinel convention** for "no value" — directly reusable for
"status not obtainable". `hw_get_config` (`:118+`) packs `u32 + u32 + u8` into
9 bytes, so multi-field OK frames are established.

**Option 2 — a DATA id-frame with `u16 × 4`.** `hw_read_voltage`
`[FILE firestarter/src/hardware_operations.cpp:79-84]` uses
`LOG_DATA_ID_U16x4(MSG_DATA_VPE_VOLTAGE, …)`. This is the shape to copy if a
**per-region** answer is wanted: 4 × u16 already exists as an emitter macro.

**Option 3 — extend `MSG_OK_READY`.** Confirmed in both repos, and it genuinely
needs **zero codegen**:
- Firmware: `[FILE firestarter/src/firestarter.cpp:166]` *"MSG_OK_READY's catalog
  entry is a variable-length byte blob"*, emitted at `:227` as
  `LOG_OK_ID_BYTES(MSG_OK_READY, _ready, (uint8_t)(4 + _vlen + 2))`.
- Host: `[FILE firestarter_app/firestarter/serial_comm.py:387-444]` decodes it
  length-discriminated — CAP-01 buffer size at `params_bytes[:2]` when
  `len >= 2`; CAP-02 `hw_revision` at `[2]` and `ver_len` at `[3]` with
  `ver_end = 4 + params_bytes[3]` when `len >= 4`; CAP-03 write budget at
  `params_bytes[ver_end : ver_end + 2]` when `len >= ver_end + 2`. A CAP-04 field
  would sit at `ver_end + 2 … ver_end + 4`. Every arm degrades to "field stays
  `None`" on a short tail, never an error.
- **But `MSG_OK_READY` is the operation-*setup* ack**, emitted on every operation
  and on every `hw_read_voltage`/`dev_tools` state-0 handshake (`hardware_operations.cpp:43`,
  `dev_tools.cpp:107`, `:153`). Piggybacking a lock status there would mean every
  command pays the bytes and every command's ack carries a protection claim.
  **Recorded as a fact, not a recommendation** — the discretion is the planner's.

**Byte-cost sketch `[ESTIMATE — not measured, no build was run]`:**
single status `u8` in an existing `LOG_OK_ID_U8` frame is the cheapest wire
shape; a `u16 × 4` per-region frame adds ~6 B of emitter setup per call site.
The dominant costs are (i) the two new `configure_*` arms, (ii) the two read
sequences, and (iii) any new `byte_flip_t` table. Nothing here can be trusted
without a cold triple-target measure.

### Does a new message ID require codegen? Yes — and the ERROR range is nearly full

`firestarter/include/messages.h` is generated and **ID-only** — confirmed: it
contains `#define MSG_WARN_FL4_BOOT_BLOCK_LOCKED 0x85` `[FILE firestarter/include/messages.h:74]`
and no format strings. The authoritative source is the **meta repo's**
`tools/catalog/messages.toml`, which the meta repo genuinely tracks
`[CMD git ls-files tools/]` → `tools/catalog/codegen.py`, `tools/catalog/messages.toml`,
`tools/catalog/sync_to_subrepos.sh`. All three copies of `messages.toml` are
byte-identical `[CMD md5sum]` = `107431500eedc1f89b025aeb3d95baae`.

**Exact regen command** — one script does everything `[FILE tools/catalog/sync_to_subrepos.sh]`:

```bash
bash tools/catalog/sync_to_subrepos.sh     # run from the meta repo root
```

It (1) copies `messages.toml` + `codegen.py` into both sub-repos'
`tools/catalog/`, (2) asserts the two vendored copies are byte-identical, (3)
regenerates `firestarter/include/messages.h` via
`python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --language cpp --target firestarter/include/messages.h`,
and (4) regenerates `firestarter_app/firestarter/messages.py` via the same with
`--language python`. So **one catalog edit touches five tracked files across three
repos**: meta `tools/catalog/messages.toml`; fw `tools/catalog/messages.toml` +
`include/messages.h`; app `tools/catalog/messages.toml` +
`firestarter/messages.py`.

The app's CI has a **codegen drift gate** that will catch a missed regen
`[FILE firestarter_app/.github/workflows/ci.yml:53-64]`: a "Catalog validity check"
(`codegen.py --check`, the 10-rule validator) then a drift gate that regenerates
`firestarter/messages.py` and runs `git diff --exit-code` on it.

**Free message IDs, measured** `[CMD python3 -c "import tomllib; …" over tools/catalog/messages.toml]`
— 76 messages, severity bands and free slots:

| severity | band | used | **free slots** |
|----------|------|-----:|---------------:|
| OK | 0x00–0x0F | 6 (0x00–0x05) | 10 (0x06…0x0F) |
| INFO | 0x40–0x7F | 22 | 42 (0x44–0x4F free, then 0x63+) |
| WARN | 0x80–0x9F | 8 (0x80–0x87) | 24 (0x88…0x9F) |
| **ERROR** | 0xA0–0xBF | **31 (0xA0–0xBE)** | **1 — only `0xBF`** |
| DATA | 0xE0–0xFF | 6 | 26 |

**This is a hard constraint the planner must know: there is exactly one free
ERROR id.** A design needing two new ERROR messages does not fit the band.

### Two message IDs that already exist and are emitted by nothing

`[CMD grep -rn "FL4_BOOT_BLOCK_LOCKED"]` across `firestarter/src`, `firestarter/test`,
`firestarter_app/firestarter`:

- `MSG_WARN_FL4_BOOT_BLOCK_LOCKED = 0x85`, format
  `"boot block locked -- 0x%06lx not programmable (W29C040 section 6.6 irreversible lockout, write forced)"`, one `u24 hex_addr` param.
- `MSG_ERR_FL4_BOOT_BLOCK_LOCKED = 0xBC`, format
  `"boot block locked -- 0x%06lx not programmable (W29C040 section 6.6 irreversible lockout)"`, one `u24 hex_addr` param.

**Neither is emitted anywhere in firmware `src/` or `test/`.** They exist in the
catalog, in `messages.h`, and in `messages.py`, and the only consumer is a host
*catalog-presence* test `[FILE firestarter_app/tests/test_val_wire_5v_page.py:283-314]`
which asserts the id is `0x85`, is in `CATALOG`, has severity `WARN`, and that
the format string contains `"section 6.6"` and not the mangled `"ss6.6"`.

That is the ready-made vocabulary for the `0x05` boot-block read: **the message
ids and their W29C040 §6.6 wording already exist and need no codegen run**; what
is missing is an emit site. **[CITED: catalog + messages.h; the datasheet §6.6
claim itself is `lockable-proms.md`/datasheet-level and is not verifiable from the
repo.]**

Also relevant, the existing honesty wording already in the firmware catalog:
`MSG_INFO_SDP_UNLOCK_DONE_US` (0x5F) and `MSG_INFO_SDP_LOCK_DONE_US` (0x61) both
end `"; protection state is not readable"`.

`MSG_ERR_UNKNOWN_CMD` is id **171 = 0xAB**, format `"Unknown command: %d"`, one
`u8` param — D-04's key.

---

## The `0x06` / `0x05` Read Sequences (Priority 3)

### `flash_util_get_chip_id` — the existing Autoselect-adjacent read, in full

`[FILE firestarter/src/proms/flash_utils.cpp:79-87]`:

```c
/* Shared AMD/JEDEC chip-ID read: FLASH_ENABLE_ID → read 0x0000/0x0001
 * → FLASH_DISABLE_ID. Used by flash_nor_unlock and flash_5v_page (Option B
 * flash-budget mitigation — Phase 74 Plan 02). */
uint16_t flash_util_get_chip_id(firestarter_handle_t* handle) {
    flash_execute_command(FLASH_ENABLE_ID);
    uint16_t chip_id = handle->firestarter_get_data(handle, 0x0000) << 8;
    chip_id |= handle->firestarter_get_data(handle, 0x0001);
    flash_execute_command(FLASH_DISABLE_ID);
    return chip_id;
}
```

And its mismatch-checking wrapper `[FILE firestarter/src/proms/flash_utils.cpp:89-105]`,
which is where `FLAG_FORCE` already downgrades an error to a warning — the exact
severity-downgrade convention D-07 cites:

```c
void flash_util_check_chip_id_execute(firestarter_handle_t* handle) {
    uint16_t chip_id = flash_util_get_chip_id(handle);
    if (chip_id != handle->chip_id) {
        uint8_t _b[4];
        _b[0] = (uint8_t)((chip_id >> 8) & 0xFF);
        _b[1] = (uint8_t)(chip_id & 0xFF);
        _b[2] = (uint8_t)((handle->chip_id >> 8) & 0xFF);
        _b[3] = (uint8_t)(handle->chip_id & 0xFF);
        if (is_flag_set(FLAG_FORCE)) {
            LOG_WARN_ID_BYTES(MSG_WARN_CHIP_ID_MISMATCH, _b, 4);
            handle->response_code = RESPONSE_CODE_WARNING;
        } else {
            LOG_ERROR_ID_BYTES(MSG_ERR_CHIP_ID_MISMATCH, _b, 4);
            handle->response_code = RESPONSE_CODE_ERROR;
        }
    }
}
```

### `flash_util_byte_flipping` and the `byte_flip_t` idiom

`[FILE firestarter/src/proms/flash_utils.cpp:21-28]`:

```c
void flash_util_byte_flipping(firestarter_handle_t* handle, const byte_flip_t* byte_flips, size_t size) {
    handle->firestarter_set_control_register(handle, CTRL_READ_WRITE, 0);
    for (size_t i = 0; i < size; i++) {
        fu_flash_flip_data(handle, byte_flips[i].address, byte_flips[i].byte);
    }
    handle->firestarter_set_control_register(handle, CTRL_READ_WRITE, 0);
}
```

with the helper `fu_flash_flip_data` at `:52-59` (set data output → fast address →
write byte → chip input → CE pulse) and `fu_flash_fast_address` at `:61-66`
(LSB/MSB register writes only — **no A16+ bank register**, so a `SA + 0x02`
sector address above 64 KiB needs the `mem_util_remap_address_bus` path, not
`fu_flash_fast_address`; that is a real detail for a sector-keyed read on a
512 KiB part). `fu_flash_data_poll` at `:68-76` is the read primitive that does
not take an address at all.

The macro that drives it `[FILE firestarter/include/flash_utils.h:15-17]`:

```c
#define flash_execute_command(command) \
    flash_util_byte_flipping(handle, command, sizeof(command) / sizeof(command[0]));
```

— note it captures `handle` from the enclosing scope by name.

### The command tables, with exact line numbers

`[FILE firestarter/include/flash_utils.h]`:

| line | table | cycles |
|-----:|-------|--------|
| :20-22 | `typedef struct byte_flip { uint32_t address; uint8_t byte; } byte_flip_t;` | — |
| **:24** | `FLASH_ENABLE_ID` | `{0x5555,0xAA} {0x2AAA,0x55} {0x5555,0x90}` |
| **:29** | `FLASH_DISABLE_ID` (declared as `const byte_flip`, not `byte_flip_t` — a live inconsistency, harmless) | `{0x5555,0xAA} {0x2AAA,0x55} {0x5555,0xF0}` |
| :34 | `FLASH_ERASE` | AA/55/80 + AA/55/10 |
| :42 | `FLASH_ENABLE_WRITE` | AA/55/A0 |
| **:48** | `FLASH_ENABLE_WRITE_PROTECTION` | AA/55/**A0** — **byte-identical to `FLASH_ENABLE_WRITE`** |
| **:53** | `FLASH_DISABLE_WRITE_PROTECTION` | AA/55/80 + AA/55/**20** |

CONTEXT.md's `:48` / `:53` citations for the two protection tables **verify exactly**.

**Finding: both protection tables are dead code.**
`[CMD grep -rn "FLASH_ENABLE_WRITE_PROTECTION\|FLASH_DISABLE_WRITE_PROTECTION" firestarter/src]`
returns only *comments* in `src/proms/eeprom_28c.cpp` (`:131`, `:134`, `:171`,
`:174`, `:178`) noting that `eeprom_28c.cpp`'s own `EEPROM_SDP_*` tables are
byte-identical to them and that `flash_utils.h` is "FIX-04-frozen". No executing
code references either table. They are candidates for the `0x05` sequence's
neighbourhood but currently contribute zero to any code path.

### The AMD Autoselect sector-protect verify read — what is and is not in the repo

**In the repo:** the Autoselect *entry* (`FLASH_ENABLE_ID` = AA/55/**90**) and
*exit* (`FLASH_DISABLE_ID` = AA/55/**F0**) sequences, plus reads at `0x0000`
(manufacturer) and `0x0001` (device). That is exactly two of the three Autoselect
outputs.

**Not in the repo, at all:** any read at `SA + 0x02`, any sector-address
computation, any `0x00`/`0x01` protected/unprotected interpretation, and any
sector-geometry table. `[CMD grep -rin "autoselect|sector.protect|protect.verify|boot.block|product.id" over firestarter/{src,include,doc,*.md}]`
returns only: the two orphan `MSG_*_FL4_BOOT_BLOCK_LOCKED` ids; and
`flash_intel.cpp:188` / `:191` (`0x90` enter autoselect / `0xFF` exit) on the
**`0x10`** path — which is a *different* command set and is out of scope per D-02.

**What is only stated in `lockable-proms.md`, not verifiable from the repo**
`[FILE firestarter_app/doc/lockable-proms.md:34-40]`:

> AMD datasheets explicitly describe Autoselect as providing manufacturer ID, device ID and sector-protection status. ([Infineon][1])
>
> Typical AMD-style result:
> * Read a sector address with the specified low address bits.
> * `00h` generally means unprotected.
> * `01h` generally means protected.
>
> Exact address wiring and byte/word interpretation depend on x8/x16 mode.

Stated plainly, because D-03's discipline requires it: **the "read at `SA + 0x02`"
specific offset appears nowhere in this repository.** `lockable-proms.md` says
"a sector address with the specified low address bits" and defers the exact wiring
to the datasheet. So the offset is an `[ASSUMED]` claim from CONTEXT.md's own
prose, and the plan must source it from a datasheet (the `0x06-FLASH-AMD-ALT`
datasheet folder referenced by `PROTOCOLS.md:117-123` is the in-tree place to
look) before writing a byte of it. Sector *geometry* — which addresses are sector
bases — is also absent from the DB and from firmware; `flash_nor_unlock_sector_erase`
takes a caller-supplied `sector_address` `[FILE firestarter/src/proms/flash_nor_unlock.cpp:117-127]`
and the host's `erase --sector-address` option is how it is supplied today
`[FILE firestarter_app/firestarter/cli_handlers.py:876-883]`. **There is no
sector map in this project.** A "per-sector" answer therefore has no data source;
a device-global or single-sector-at-a-supplied-address answer does.

### The Winbond Product-ID boot-block status read on `0x05`

What exists in `firestarter/src/proms/flash_5v_page.cpp`:

- `configure_flash_5v_page` (`:41-59`) — four command arms, no `default`.
- `flash_5v_page_page_size(mem_size)` (`:27-31`) — the flash4 page-size ladder
  (`≤65536→64`, `≤262144→128`, else `256`). **Unrelated to Phase 149's `0x0D`
  page-size seam.**
- The W29C040 SDP comment CONTEXT.md cites, at `:86-90` (the specific W29C040
  sentence is `:87`), quoted in full:

```c
        /* SDP 3-byte unlock at the start of each page load (AMD/JEDEC SDP).
         * W29C040 ships with Software Data Protection enabled; without this
         * sequence the page-buffer write is silently rejected.
         * Call per-page-START (not per-byte) — calling per-byte would abort
         * the current page load and restart it after each byte. */
```

- `flash_5v_page_check_chip_id_execute` (`:133-135`) and
  `flash_5v_page_get_chip_id` (`:137-139`) — both thin delegations to
  `flash_util_*`.
- `flash_5v_page_erase_execute` (`:141-173`) — the 12 V `CTRL_VPE_ENABLE` erase
  ritual, which is the only place this handler engages the VPP/VPE rails.

**What would have to be newly written:** everything. There is no Product-ID-mode
entry sequence distinct from `FLASH_ENABLE_ID`, no boot-block status address, no
`FF`/`FE` lockout-bit decode. The host already *describes* that read as the thing
that would confirm a lockout — `[FILE firestarter_app/firestarter/eprom_operations.py:174]`:
*"Wording per A3 / STRIDE T-94-MISLABEL: the hint INFERS the lockout from the
address range; it does NOT confirm it (only the firmware §6.6 DETECT read can read
the FF/FE lockout bit and confirm)."* — and the emitted hint at `:208-213`:

```
boot-block region hint: address 0x{addr:06X} is in the {region} region.
This boot-block region may be locked (W29C040 datasheet §6.6 boot-block lockout
— irreversible, no unlock command exists). Writes to addresses >=0x4000 should
succeed on an unlocked region. This is an inference from the address range, not
a confirmed detection.
```

with `_BOOT_BLOCK_SIZE = 0x4000` `[:99]` and `_FLASH4_PROTOCOL_ID = 5` `[:107]`.
That is the exact host-side vocabulary and the exact non-claim the new read would
be allowed to upgrade — and the seven legs of `firestarter_app/tests/test_boot_block_hint.py`
(`:65`, `:83`, `:93`, `:107`, `:122`, `:136`, `:149`) pin it today, including
`test_boot_block_hint_non_flash4_protocol_no_hint` and
`test_boot_block_hint_non_timeout_id_no_hint`.

### Sharing code with the chip-ID path

**Shareable, measured:** `flash_util_byte_flipping`, `fu_flash_flip_data`,
`fu_flash_fast_address`, `fu_flash_data_poll`, the `flash_execute_command` macro,
`FLASH_ENABLE_ID`, `FLASH_DISABLE_ID`, and the whole `byte_flip_t` idiom. A read
that is *"enter the same mode, read a different address, exit"* reuses all of it
and adds only the address computation + interpretation.

**Not shareable:** `flash_util_get_chip_id` itself returns a `uint16_t` composed
from two fixed addresses; a protect-verify read wants one byte at a computed
address. Refactoring `get_chip_id` into a generic
`flash_util_read_in_id_mode(handle, addr) -> uint8_t` and re-expressing
`get_chip_id` on top of it is the shape that avoids duplicating the enter/exit
pair.

**Byte cost `[ESTIMATE — no build run this session]`:** a shared
`flash_util_read_in_id_mode` helper plus a rewritten `get_chip_id` is plausibly
*net-neutral to slightly negative* on flash (one function call replaces two
inlined `firestarter_get_data` calls), with the new command's own status logic and
two `configure_*` arms as the real additions. A duplicated implementation
(separate enter/read/exit in each of the two handlers) would add roughly two
copies of a 3-cycle table plus two call sequences. **Both figures are estimates
and neither may be used as an acceptance criterion.** The only trustworthy number
comes from `rm -rf .pio/build/<env>` + one `pio run -e <env>` per env.

**One measured structural fact that bears on the cost:** the `byte_flip_t` tables
are `const` arrays defined **in a header** with no `static` and no `extern`
`[FILE firestarter/include/flash_utils.h:24-58]`. In C++ a namespace-scope `const`
has internal linkage, so **each translation unit that includes `flash_utils.h`
gets its own copy**; `--gc-sections` discards unused ones. Adding a new table to
that header therefore costs bytes in every TU that actually references it, not
once globally.

---

## Does `infoic.xml` Supply the Sequences? — a clean, evidenced NEGATIVE

**Scope, stated first so no later reader conflates two different questions.**

- **CLOSED, and not reopened here:** whether `infoic.xml` can supply protection
  **readability**. `.planning/notes/infoic-xml-protection-flags-research.md`
  settled that negatively (flags bits 14/15 cannot derive readability;
  `W29C020C` is flag-identical to `W29EE011`; the AMD readable group carries zero
  protection bits). **That remains closed.**
- **OPEN, and answered below:** whether `infoic.xml` carries **command sequences,
  mode-entry bytes, or mode-relative status addresses** — the `SA + 0x02` offset
  C-9 could not source, and the Product-ID boot-block status address C-10 found
  nowhere in the repo. **This is a different question about a different kind of
  datum**, and the operator's hypothesis was that infoic carries it.

### Method — reproducible and pinned

`infoic.xml` is gitignored (`firestarter_app/.gitignore:29` →
`tools/infoic*.xml`) and absent from a clean checkout, exactly as
`tools/derive_sdp_partition.py`'s docstring records (`:7-13`). I used that
module's own mechanism — `_load_infoic_xml()` (`:74-83`), which reads
`INFOIC_XML_PATH` if set and otherwise fetches `MINIPRO_XML_URL` (`:60-64`) — at
the **same pinned upstream revision the rest of the project cites**:

```bash
curl -sS -o infoic.xml \
  "https://gitlab.com/DavidGriffith/minipro/-/raw/a8efaedc236c1d9718bd28299dfbb99536b010ff/infoic.xml"
# 17,861,009 bytes  [CMD ls -la]
```

Parsed with `xml.etree.ElementTree`, selecting
`.//database[@type='INFOIC2PLUS']` — the same section `_build_token_index`
(`:86-108`) selects, and the same one `build_db.py:454` reads. **No file was
written into either repo.**

Section census `[CMD python3 …]`: `INFOICT76` 11434 `<ic>`, **`INFOIC2PLUS`
11510 `<ic>`** (168 `<manufacturer>` elements), `INFOIC` 4918 `<ic>`.

One structural detail worth recording because it changes an attribute count:
of the 11510 `INFOIC2PLUS` `<ic>` elements, **11481 are `<manufacturer>/<ic>` and
29 are `<custom>/<ic>`** (parent tag `custom`, e.g. `<custom name="ATMEL">`).
`build_db.py:454-459` traverses `.//database[@type='INFOIC2PLUS']` →
`.//manufacturer` → `.//ic`, so it reads the 11481 and **never sees the 29**.
**Zero of the 29 `<custom>` entries carry `protocol_id` `0x05` or `0x06`**, so
they are irrelevant to this phase.

### The FULL per-chip attribute set — 20 names, and that is all there is

`[CMD python3 … collections.Counter over every attribute of every <ic>]`:

| # | attribute | present on | consumed by `build_db.py`? | could it carry a sequence? |
|--:|-----------|-----------:|----------------------------|----------------------------|
| 1 | `name` | 11510 | **yes** — `:460` | no — comma-joined alias string |
| 2 | `type` | 11510 | **yes** — `:468` | no — small enum |
| 3 | `protocol_id` | 11510 | **yes** — `:482` | no — the algorithm **selector**, not its parameters |
| 4 | `variant` | 11510 | **yes** — `:481` | no — high byte discarded, low byte → pinout key |
| 5 | `read_buffer_size` | 11510 | no | no — byte count |
| 6 | `write_buffer_size` | 11510 | no | no — byte count |
| 7 | `code_memory_size` | 11510 | **yes** — `:499` | no — byte count |
| 8 | `data_memory_size` | 11510 | no | no — byte count |
| 9 | `data_memory2_size` | 11510 | no | no — byte count |
| 10 | `page_size` | 11510 | **yes** — `:495`, `:497` | no — byte count |
| 11 | `chip_id` | 11510 | **yes** — `:779` | **partially relevant** — see below |
| 12 | `voltages` | 11510 | **yes** — `:498` | no — packed nibbles |
| 13 | `pulse_delay` | 11510 | **yes** — `:776` | no — µs scalar |
| 14 | `flags` | 11510 | **yes** — `:483` | no — the settled-negative bitfield |
| 15 | `chip_info` | 11510 | no | no — see below |
| 16 | `pin_map` | 11510 | **yes** — `:503` | no — pinout selector |
| 17 | `package_details` | 11510 | **yes** — `:464` | no — packed package bits |
| 18 | `config` | 11510 | no | **the one candidate — and it is `NULL`**; see below |
| 19 | `pages_per_block` | 11506 | no | no — count |
| 20 | `blank_value` | **25** | no | no — a single erased byte |

**`<ic>` elements have ZERO child elements and ZERO text content** — measured
across all 11510 (`children: 0`, `text-bearing: 0`). So there is no nested
`<sequence>`, `<command>`, `<algorithm>` or table anywhere under a chip. **The 20
attributes above are the complete per-chip datum.**

`blank_value` is present on exactly **25** `<ic>`s, **all** under `<custom>` and
**all** with `protocol_id="0x80000001"` — a synthetic serial-EEPROM protocol,
nothing to do with `0x05`/`0x06`.

**Attribute-name search for a sequence carrier** — `[CMD python3 … regex over the
attribute-name set for `cmd|seq|unlock|protect|addr|command`]` → **`(none)`**.
There is no `cmd*` field, no unlock table, no per-chip algorithm-parameter field.

**Value search for the AMD/JEDEC magic bytes** — `[CMD python3 … regex
`(?i)(aa.?55|55.?aa|5555|2aaa)` over EVERY attribute value of ALL 11510 `<ic>`]` →
**2 hits, both accidental, both in `name`**:
`MICRON/MT28GU512AAA1EGC(RB119)@BGA64` and
`MICRON/MT28GU512AAA2EGC(RB120)@BGA64,…`. **No `AA`/`55`/`90` triple, no `0x5555`,
no `0x2AAA` appears as data anywhere in the file.**

### The two candidate "unused field carrying sequence data" leads — both dead

**`config` — the only field whose type could plausibly be a blob.** Measured
distribution over all 11510 `[CMD python3 …]`: `'NULL'` × **10910**, 121 distinct
values total, and every non-`NULL` value is a named MCU fuse-configuration profile
— `at89_2` (30), `avr_13` (27), `pic_13` (20), `pic_10` (17), `pic_24` (15),
`at90_3` (10) … . Decisively:

> **`config` is `"NULL"` on all 101 `protocol_id="0x05"` entries and on all 897
> `protocol_id="0x06"` entries.** `[CMD python3 …]`

**`chip_info` — the only unused field that actually varies on `0x06`.** Value sets
for all eight present-but-unused fields, measured per protocol `[CMD python3 …]`:

| field | on `0x05` (101 ics) | on `0x06` (897 ics) |
|-------|---------------------|---------------------|
| `read_buffer_size` | **constant** `0x1000` | **constant** `0x1000` |
| `write_buffer_size` | 4 values: `0x80`×61, `0x100`×26, `0x200`×8, `0x40`×6 (tracks page size) | **constant** `0x100` |
| `data_memory_size` | **constant** `0x00` | **constant** `0x00` |
| `data_memory2_size` | **constant** `0x00` | **constant** `0x00` |
| `pages_per_block` | **constant** `0x0000` | **constant** `0x0000` |
| `chip_info` | **constant** `0x0000` | `0x0000`×573, **`0x00e3`×169**, **`0x00e4`×155` |
| `config` | **constant** `NULL` | **constant** `NULL` |
| `blank_value` | absent on all | absent on all |

The `0x00e3` / `0x00e4` split is a **vendor/algorithm-family discriminator, not an
address** `[CMD python3 …]`: `0x00e3` clusters MOSEL VITELIC (48), SYNCMOS (48),
SGS-THOMSON (23), ST (23), HYNIX (12), HYUNDAI (12); `0x00e4` clusters
MACRONIX(MXIC) (73), CFEON (24), AMD (16), EON (16), SPANSION(1) (16), AMIC (8).
Both values span sizes `0x20000`–`0x80000` and both contain top- and bottom-boot
variants (`AM29F002B` and `AM29F002BT` are both `0x00e4`), so it does not even
encode boot-sector orientation. The field dictionary's own entry
(`doc/infoic-field-dictionary.md:251-263`) already calls it an *"Opaque
discriminator"* whose only known sentinels are `0x0006` (`MP_VOLTAGES1`) and
`0x0007` (`MP_VOLTAGES2`); `0x00e3`/`0x00e4` are neither, and remain undecoded.
**A two-valued opaque discriminator cannot supply an address or a byte sequence.**

### The verbatim XML — W29C020 and an AMD Autoselect part

`W29C020` entry, quoted exactly as it appears at `a8efaedc`:

```xml
<!-- manufacturer name="WINBOND" -->
<ic name="W29C020,W29C020C,W29C022"
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
    config="NULL"/>
```

For contrast, the two sibling Winbond `0x05` entries, same section:

```xml
<ic name="W29C040,W29C042" type="1" protocol_id="0x05" variant="0x7500"
    read_buffer_size="0x1000" write_buffer_size="0x100" code_memory_size="0x80000"
    page_size="0x0100" chip_id="0x0000da46" voltages="0x000a" pulse_delay="0x2710"
    flags="0x0040c078" chip_info="0x0000" pin_map="0x00001a0d"
    package_details="0x20000000" config="NULL"/>

<ic name="W29EE011" type="1" protocol_id="0x05" variant="0x7500"
    read_buffer_size="0x1000" write_buffer_size="0x80" code_memory_size="0x20000"
    page_size="0x0080" chip_id="0x0000dac1" voltages="0x0000" pulse_delay="0x4e20"
    flags="0x0040c078" chip_info="0x0000" pin_map="0x00001809"
    package_details="0x20000000" config="NULL"/>
```

*(Note `flags="0x0040c078"` on `W29C020` **and** on `W29EE011` — the settled
negative, visible here as a by-product. Not reopened.)*

Representative AMD Autoselect (`0x06`) entries, quoted exactly:

```xml
<!-- manufacturer name="AMD" -->
<ic name="AM29F040@DIP32,AM29F040B@DIP32"
    type="1"
    protocol_id="0x06"
    variant="0x7000"
    read_buffer_size="0x1000"
    write_buffer_size="0x100"
    code_memory_size="0x80000"
    data_memory_size="0x00"
    data_memory2_size="0x00"
    page_size="0x0000"
    pages_per_block="0x0000"
    chip_id="0x000001a4"
    voltages="0x0000"
    pulse_delay="0x0004"
    flags="0x00000078"
    chip_info="0x0000"
    pin_map="0x00005c0d"
    package_details="0x20000000"
    config="NULL"/>

<!-- manufacturer name="SST" -->
<ic name="SST39SF040" type="1" protocol_id="0x06" variant="0x7001"
    read_buffer_size="0x1000" write_buffer_size="0x100" code_memory_size="0x80000"
    page_size="0x0000" pages_per_block="0x0000" chip_id="0x0000bfb7"
    voltages="0x0000" pulse_delay="0x000a" flags="0x00000078" chip_info="0x0000"
    pin_map="0x00005c0d" package_details="0x20000000" config="NULL"/>

<!-- manufacturer name="WINBOND" -->
<ic name="W49F020" type="1" protocol_id="0x06" variant="0x7100"
    read_buffer_size="0x1000" write_buffer_size="0x100" code_memory_size="0x40000"
    page_size="0x0000" pages_per_block="0x0000" chip_id="0x0000da8c"
    voltages="0x0000" pulse_delay="0x0032" flags="0x00000078" chip_info="0x0000"
    pin_map="0x00005b0b" package_details="0x20000000" config="NULL"/>
```

### The answers, stated plainly

| question | answer | evidence |
|----------|--------|----------|
| Does any field supply the **Product-ID-mode boot-block status address**? | **NO** | no address-typed attribute exists; the 20-name set contains no `addr`-like field; `config="NULL"` on all 101 `0x05` entries |
| Does any field supply the **`FF`/`FE` lockout decode**? | **NO** | no per-chip decode/mask field beyond `flags` (settled negative) and `chip_info` (opaque 2-value discriminator, constant `0x0000` on all `0x05`) |
| Does any field supply the **AMD Autoselect `SA + 0x02` verify offset**? | **NO** | same; `chip_info` on `0x06` varies but is a vendor cluster, not an offset; `page_size` is `0x0000` on the whole `0x06` population |
| Are there **command / unlock-sequence bytes of any kind** (`AA`/`55`/`90`, `cmd*` fields, algorithm parameters, write/unlock tables)? | **NO** | zero attribute names matching `cmd\|seq\|unlock\|protect\|addr\|command`; zero `aa55`/`5555`/`2aaa` occurrences in any attribute value across all 11510 `<ic>`; zero child elements; zero text content |
| Is there an **unused field carrying sequence data**? | **NO** | all 8 unused fields enumerated with their full value sets; 7 of 8 are constant on `0x05` and 7 of 8 on `0x06`; the only varying one (`chip_info`) is a 2-value opaque cluster |

**`infoic.xml` is a chip-*parameter* database, not an algorithm database.**
`protocol_id` **selects** an algorithm implemented in the programmer's own
firmware; the sequence bytes live in that implementation, never in the XML. The
folded todo already recorded the same shape for the protect operation itself —
*"The actual protect op in minipro is an opaque TL866 opcode (0x18/0x19) — no
mechanism/region info exists to decode"* — and this measurement generalises it to
**every** sequence: minipro sends an opcode plus the 20 parameters above, and the
TL866II+ firmware holds the command sequences.

**The one genuinely useful thing infoic does supply**, and it is not a sequence:
`chip_id`. `W29C020/W29C020C/W29C022 → 0x0000da45`, `W29C040/W29C042 → 0x0000da46`,
`W29C010/… → 0x0000dac1`, `AM29F040 → 0x000001a4`, `SST39SF040 → 0x0000bfb7`,
`W49F020 → 0x0000da8c`. These are **exactly the values read back in the same
Autoselect / Product-ID mode** whose status address is missing — so infoic supplies
a **positive control for the mode entry** (sub-claim (i) in the W29C020 bench
analysis above) while supplying nothing about the status read itself. That is a
real, if narrow, contribution and it is already consumed (`build_db.py:779` →
`chip_id_value` → `chip-id` on the wire).

### Then the datasheet — what is obtainable, and one live name trap

`firestarter_app/datasheets/` holds **7 PDFs**, of which **3 are git-tracked**
`[CMD git ls-files datasheets/ ; git status --porcelain datasheets/]`:

| file | tracked? | size | covers | DB algorithm of those parts | use for this phase |
|------|----------|-----:|--------|-----------------------------|--------------------|
| `AT28C256.pdf` | **tracked** | 749 812 | AT28C256 | **`0x0D`** (13) | none — `0x0D` is `not_readable` by LOCK-03 |
| `SST39SF0x0A.pdf` | **tracked** | 2 947 801 | SST39SF010A/020A/040 | **`0x06`** (6) | **see the trap below** |
| `W27C020.pdf` | **tracked** | 1 906 405 | Winbond **W27**C020 | **`0x08`** (8) — `WINBOND \| W27C02,W27C020,W27E02,W27E020,W27L02` | **none — wrong family** |
| `M27C1001.pdf` | untracked | 220 569 | ST M27C1001 | `0x07`/`0x08` class | none |
| `M27C512.pdf` | untracked | 286 356 | ST M27C512 | UV-EPROM class | none |
| `W27C512.pdf` | untracked | 165 171 | Winbond W27C512 | UV/EEPROM class | none |
| `W27E257.pdf` | untracked | 232 448 | Winbond W27E257 | UV/EEPROM class | none |

**⚠ Two traps here, both measured:**

1. **`W27C020.pdf` is NOT a `W29C020` datasheet.** `W27C020` resolves in the DB to
   `WINBOND | W27C02,W27C020,W27E02,W27E020,W27L02`, **algorithm `0x08`** — a
   27-series UV/electrically-erasable EPROM, a different family with a different
   command set. This is the same one-character trap the project already documented
   for ST `M27C512` vs Winbond `W27C512`. **Nothing in `datasheets/` covers the
   `W29C0xx` family.**
2. **`SST39SF0x0A.pdf` is a tracked `0x06` datasheet, but it cannot source the
   Autoselect sector-protect verify** — because `lockable-proms.md:222` records
   `SST39SF010A / SF020A / SF040` as **"No explicit lock bit"**, protection
   mechanism *"SDP command sequence and hardware write inhibit"*, and `:229` says
   the datasheet *"describes hardware and software data protection, but not
   conventional individually lockable sectors with a sector-status query."* So the
   one in-tree `0x06` datasheet documents a family the curated table would mark
   `documented-not-readable`.

**I could not read any of these PDFs.** `[CMD which pdftotext pdfinfo mutool;
python3 -c "import pypdf"; python3 -c "import fitz"]` → **none available**. A
stdlib `zlib`-decompress + text-operator extraction produced glyph-encoded output
(subset fonts with custom encodings): a grep of the extracted text for
`autoselect|sector protect|product id|software data protection|boot block|29C020`
returned **zero hits** in both `SST39SF0x0A.pdf` and `W27C020.pdf`. **So no
datasheet claim in this document is sourced from a PDF**, and the extraction
limitation is recorded rather than worked around.

**What is obtainable, and at what granularity.** For the AMD Autoselect verify the
canonical citation is the AMD/Infineon `Am29F040B` datasheet's *Autoselect Mode*
table and its *Sector Protection Verify* row — `lockable-proms.md`'s reference `[1]`
already points at the Infineon `AM29F002B/AM29F002NB` PDF, and reference `[4]`
(Macronix `MX29F200C`, v2.1) at a *sector protect verify* description. For the
Winbond Product-ID boot-block status the canonical citation is the `W29C020C`
datasheet's *Product Identification / Boot Block Lockout* section — the project's
existing message wording already cites **"W29C040 datasheet §6.6"** for the
sibling part (`messages.toml` → `MSG_ERR_FL4_BOOT_BLOCK_LOCKED`), and
`PROTOCOLS.md:97,100,103` cites `datasheets/0x05-FLASH-AMD-STD/W29C020.pdf p.9
§Write Operation` and `W29C040.pdf p.11 §Page Write` / `p.12 §Chip Erase` — i.e.
**the project's own citation convention for this family is `vendor datasheet,
page, §section`**, and `PROTOCOLS.md` already references a `W29C020.pdf` under a
`datasheets/0x05-FLASH-AMD-STD/` path **that does not exist in the working tree**
`[CMD ls firestarter_app/datasheets]`. Achievable granularity is therefore
**vendor + document number + revision + page + section**, matching the existing
convention. **Per the brief, no PDF was fetched and none is proposed for the
repo.**

### What a sequence can be pinned against, per source

This is the difference that matters for the Validation Architecture, and it is
categorical:

| sequence source | strongest available test | why |
|-----------------|--------------------------|-----|
| **infoic.xml-derived** | an **element-wise proof** against a freshly-loaded `infoic.xml`, in the exact style of `tests/test_sdp_db_invariant.py::test_sdp_partition_matches_infoic_derived_field_element_wise` (`:584-621`) — two independently-computed partitions asserted equal chip-by-chip, plus a synthetic-mutation non-vacuous control | the upstream datum is machine-readable and re-derivable, so drift is detectable |
| **datasheet-derived** | a **citation comment plus a pinned byte table** — nothing stronger exists | there is no machine-readable upstream to diff against; the test can only assert the committed bytes are the bytes it was told, i.e. it detects *edits*, never *errors* |

**Because the answer above is a clean negative, the `0x05` and `0x06` sequences
are necessarily datasheet-derived, and therefore only the weaker pinning is
available to them.** No element-wise proof is possible for either sequence — and
the plan must not write an acceptance criterion implying otherwise. The honest
form is: *the sequence bytes are pinned as a literal table with a
vendor/document/revision/page/section citation comment, and a test asserts the
table is unchanged* — which is a **change detector, not a correctness proof**.

---

## Re-derived DB Counts (Priority 4 — D-09 says "re-derive, do not trust")

**Method, stated so it can be re-run.** All figures below come from a single
`python3` heredoc over the committed
`firestarter_app/firestarter/data/chip_database.json`, flattening
`{vendor: [row, …]}` into `(vendor, row)` pairs and reading
`row["programming"]["algorithm"]` (an `int`) and
`row["programming"]["protect_on_after"] is True` / `protect_off_before is True`
(strict identity, so a missing key counts as neither true nor false). Alias tokens
were derived with the production rule — comma-split, `.strip()`, `.upper()`, **no
parenthetical stripping** — i.e. `sdp_capability.split_part_number_tokens`'s exact
semantics. `[CMD python3 - <<'EOF' … EOF]`

### Totals and per-algorithm histogram

**746 rows, 59 vendors** — both confirmed unchanged.

| algorithm (dec) | hex | rows | D-09 / CONTEXT.md claim | verdict |
|----------------:|-----|-----:|------------------------|---------|
| 5 | `0x05` | **27** | 27 | ✓ |
| 6 | `0x06` | **190** | 190 | ✓ |
| 7 | `0x07` | **170** | (not quoted) | — |
| 8 | `0x08` | **127** | (not quoted) | — |
| 11 | `0x0B` | **32** | (not quoted) | — |
| 13 | `0x0D` | **84** | 84 | ✓ |
| 14 | `0x0E` | **20** | (not quoted) | — |
| 16 | `0x10` | **39** | 39 | ✓ |
| 39 | `0x27` | **2** | (not quoted) | — |
| 40 | `0x28` | **34** | (not quoted) | — |
| 41 | `0x29` | **20** | (not quoted) | — |
| **52** | **`0x34`** | **1** | **absent from D-09's enumeration** | ⚠ see below |
| | | **746** | 746 | ✓ |

There is **no `0x0E`-labelled-14 confusion**: `0x0E` = 14 decimal, 20 rows;
`0x10` = 16 decimal, 39 rows. The research brief listed `0x0E` and `0x10` (16)
separately and both resolve cleanly.

### D-09's claimed partition — verified, with one hole

| class | D-09's figure | measured | verdict |
|-------|--------------:|---------:|---------|
| readable families (`0x06` 190 + `0x10` 39) | 229 | **229** | ✓ |
| documented-not-readable (`0x0D` 84 + `0x05` 27) | 111 | **111** | ✓ |
| no mechanism | 406 | **405** by D-09's own enumeration; **406** only if `0x34` is folded in | ⚠ |

D-09 enumerates the no-mechanism set as *"UV-EPROM `0x07`/`0x08`/`0x0B`,
SRAM/NVRAM `0x0E`/`0x27`/`0x28`/`0x29`"*. That is
`170 + 127 + 32 + 20 + 2 + 34 + 20 = ` **405**, not 406. The 406 total is
arithmetically right (`746 − 229 − 111 = 406`) but is only reachable by also
counting **algorithm `0x34` (52), one row**, which D-09's prose does not name.

**The orphan row, in full** `[CMD python3 … algorithm==52]`:

```json
{
  "part_number": "X88C64P,X88C64S",
  "electrical": { "pin_count": 24, "size_bytes": 8192, "type": "EEPROM",
                  "vcc_mv": 5000, "vdd_mv": 5000, "vpp_mv": 12000 },
  "pinout": "DIP24_6116",
  "programming": { "algorithm": 52, "chip_id_check": false,
                   "chip_id_value": "0x00000000", "infoic_page_size_raw": 32,
                   "protect_off_before": true, "protect_on_after": false,
                   "pulse_duration_us": 0 },
  "support_status": "protocol-not-implemented",
  "unsupported_reason": "protocol not implemented: 0x34 (XICOR X88C64P — parallel DIP24 5V EEPROM, 8051 multiplexed-bus interface (ALE/WR/RD); feasible-candidate, handler not implemented)"
}
```

Vendor `XICOR`. It is an **EEPROM with `protect_off_before: true`** — i.e. upstream
says it *has* a protection mechanism — and its handler is
`configure_not_implemented()` per `PROTOCOLS.md:70`. So calling it
`no_mechanism` would be a false claim, and calling it `not_implemented` collides
with `0x10`'s meaning (documented-readable but deliberately unimplemented).
**This single row is the exhaustiveness hole D-12's invariant exists to catch, and
it exists today, before any code is written.** The planner must decide its class
explicitly; the invariant test must go red if it lands nowhere.

### `protect_on_after` — D-14 verified exactly

`[CMD python3 …]`

| measure | D-14 claim | measured | verdict |
|---------|-----------:|---------:|---------|
| `true` over all rows | 70 of 746 | **70** | ✓ |
| `false` over all rows | (not quoted) | **674** | — |
| key **absent** | (not quoted) | **2** | new |
| alg 5 | 27 of 27 (a constant) | **27 of 27** | ✓ |
| alg 13 | 43 | **43** (of 84) | ✓ |
| any other algorithm | zero | **zero** | ✓ |

`70 + 674 + 2 = 746` ✓.

### `protect_off_before` — D-14 verified exactly

| measure | D-14 claim | measured | verdict |
|---------|-----------:|---------:|---------|
| `true` over all rows | 148 of 746 | **148** | ✓ |
| `false` | (not quoted) | **596** | — |
| key absent | (not quoted) | **2** | new |
| alg 5 | 27 | **27 of 27** | ✓ |
| alg 6 | 77 | **77 of 190** | ✓ |
| alg 13 | 43 | **43 of 84** | ✓ |
| alg 52 | 1 | **1 of 1** | ✓ |

`148 + 596 + 2 = 746` ✓.

**The two rows missing both keys** `[CMD python3 …]`: vendor
`TEXAS INSTRUMENTS`, `part_number` **`2516`** and **`2532`**, both
`algorithm: 11` (`0x0B`, UV-EPROM), `pulse_duration_us: 500`, and their
`programming` dict has only `{algorithm, chip_id_check, chip_id_value,
pulse_duration_us}`. This matches the folded todo's "744 of 746 rows" figure
exactly (`746 − 2 = 744`). **Any code that reads `programming["protect_on_after"]`
by direct index raises `KeyError` on these two rows** — the D-12 invariant walk
must use `.get(...)`, and DATA-06's documentation must say "744 of 746 rows carry
the fields" rather than implying universality.

### Provenance vs post-classification algorithm — the promotion trap, measured

`build_db.py` **reassigns** `proto_id` inside `classify()` and discards
provenance; the page-size arm was given a captured `_upstream_proto_id` precisely
for this reason `[FILE firestarter_app/tools/build_db.py:664-671, 800-836]`. The
two protect fields are decoded from the **upstream** `flags` before any of that:

```python
"protect_off_before": True if (flags & 0x4000) else False,
"protect_on_after":   True if (flags & 0x8000) else False,
```
`[FILE firestarter_app/tools/build_db.py:800-801]` — i.e. bit 14 and bit 15,
matching the field dictionary's table exactly.

**Consequence, and it is load-bearing for D-15's wording:** the by-algorithm
breakdown mixes axes. `algorithm: 13` is 84 rows of which **66 are promoted from a
foreign upstream protocol** and only **18 are upstream-native `0x0D`**
`[FILE firestarter_app/tools/build_db.py:818-824]` — *"The 66 rows classify()
promotes into 0x0D from a foreign protocol keep the firmware AT28C page-size
floor (D-04)"*.

Using presence of the emitted `page_size` key as the upstream-`0x0D` proxy (the
arm fires iff the canonical part is in `_PAGE_SIZE_BY_PART` **or**
`_upstream_proto_id == 0x0D`), measured `[CMD python3 …]`:

- 20 rows carry `page_size`: **18 at algorithm 13**, 2 at algorithm 5.
- The 18: **15 at `page_size` 128, 3 at 64** — matching the recorded Phase 149
  figure. Named: `ATMEL AT28C010,AT28C010E` · `AT28C040,AT28C040E` · `AT28LV010` ·
  `AT28MC010`(64) · `AT28MC020` · `AT28MC040` · `CATALYST(CSI) CAT28C512` ·
  `CAT28C010` · `CAT28C020` · `CAT28C040` · `MAXWELL 28C010,28C010T,28C011,28C011T` ·
  `SGS-THOMSON M28010` · `ST M28010` · `WED WE128K8`(64) · `WE256K8`(64) ·
  `WE512K8` · `WME128K8` · `XICOR X28C010`.
- **`protect_on_after` is `True` on 18 of 18 upstream-native `0x0D` rows, and on
  25 of the 66 promoted rows.** 18 + 25 = 43 ✓ — which is where the "43" comes
  from, and it is **not** a fact about the `0x0D` family; it is 100 % of the
  native rows plus 38 % of the promoted ones.
- `protect_off_before` splits identically: 18 of 18 native, 25 of 66 promoted.

**Does promotion affect the partition?** For the *class* partition, no — class is
keyed on the post-classification `protocol-id`, which is what the host sees
(`database._map_data` maps `programming.algorithm` → `protocol-id`
`[FILE firestarter_app/firestarter/database.py:405]`). For **D-15's wording**, yes,
materially: a sentence saying "on `algorithm: 13`, `protect_on_after` is true on
43 of 84" is true of the DB and misleading about the silicon, because 66 of those
84 rows' flag bits describe a record filed under another protocol. **D-15's
"carries the measurement, not a shrug" is best served by stating the 18/18 + 25/66
split, not the bare 43.**

### The alias-token surface — three invariants worth having

`[CMD python3 …]` over all 746 rows:

- **953 distinct alias tokens**; **1113 (entry, token) pairs**.
- **Zero tokens span more than one algorithm.** So `token → algorithm` is a
  *function*. This is a strong, free invariant: a token-keyed table can never be
  ambiguous about which algorithm's class rule applies to it, and D-12 can assert
  it directly.
- Tokens on algorithms 5 + 6 (the curation surface, see next section): **273
  distinct**, and **none of them appears on any other algorithm**.

### `protect_on_after` / `protect_off_before` — every runtime reference, enumerated

`[CMD grep -rn "protect_on_after\|protect_off_before" firestarter_app/firestarter firestarter_app/tools firestarter_app/tests]`,
results grouped:

**In `firestarter_app/firestarter/` (the shipped package) — exactly one hit, and it
is a comment:**
- `firestarter/sdp_capability.py:74` — inside the `SDP_CAPABLE_TOKENS` provenance
  comment: *"now proves it equal, element-wise, to `chip_database.json`'s own
  `protect_on_after` field (PROV-02/03, Phase 136.1)"*. **A comment. No code
  reads either field.** D-14's claim verified ✓.

**In `firestarter_app/tools/` (generator + reproducibility scripts, not shipped
runtime):**
- `tools/build_db.py:800-801` — the emit site (writes them).
- `tools/derive_sdp_partition.py` — the standalone, never-CI, never-imported
  re-derivation script; reads `protect_on_after` to cross-check
  (`[FILE …/derive_sdp_partition.py:36-44]`, explicitly *"never imported by
  production code or by the pytest suite, and never wired into CI"*).

**In `firestarter_app/tests/` — the two files D-14 names, and only those:**
- `tests/test_sdp_db_invariant.py` — `_partition_from_protect_on_after_field` and
  `test_sdp_partition_matches_infoic_derived_field_element_wise` (`:584`).
- `tests/test_b15_page_size_corroboration.py` — reads `protect_on_after` and
  `infoic_page_size_raw` per row.

**Nothing in `firestarter/` (firmware) references either field**, and nothing on
the wire carries them (`convert_to_programmer`'s output keys are
`memory-size`, `algorithm`, `pin-count`, `vpp_mv`, `pulse-delay`, optionally
`chip-id`, `bus-config`, `page_size` `[FILE firestarter_app/firestarter/database.py:541-560]`).
**D-14's "neither field has any runtime consumer" is confirmed, and the
enumeration above is the evidence D-15 should cite.**

### Sizing the curation, and why literal matching does not work

Class assignment falls into two kinds:

**(A) Algorithm-derivable — no curation needed.** `0x10` → `not_implemented`
(39 rows, D-02); `0x07`/`0x08`/`0x0B`/`0x0E`/`0x27`/`0x28`/`0x29` →
`no_mechanism` (405 rows); `0x0D` → `not_readable` (84 rows, LOCK-03's named
family); `0x34` → **undecided, see the orphan row above** (1 row). That is
**529 of 746 rows** classified with zero curated tokens.

**(B) Curation-required — the `0x05` + `0x06` surface.** `[CMD python3 …]`

| algorithm | entries | distinct alias tokens |
|-----------|--------:|----------------------:|
| `0x05` | 27 | 42 |
| `0x06` | 190 | 231 |
| **total** | **217** | **273** |

**Literal token matching against `lockable-proms.md` is insufficient — measured.**
Counting a token as "documented" iff it appears verbatim (uppercased) anywhere in
`doc/lockable-proms.md` `[CMD python3 …]`:

| algorithm | distinct tokens | tokens appearing verbatim | entries where **every** token appears verbatim |
|-----------|----------------:|--------------------------:|-----------------------------------------------:|
| `0x05` | 42 | **10** | **5** (`AT29C256`, `AT29C512`, `AT29C020`, `AT29C040`, `W29EE011`) |
| `0x06` | 231 | **20** | **7** (`AT49F040,AT49F040A`, `CFEON EN29F010`, `EON EN29F010`, `SST39SF010,SST39SF010A`, `SST39SF020,SST39SF020A`, `SST39SF040`, `W49F020`) |
| `0x0D` | 130 | 11 | 1 (`MICROCHIP memory 28C64B`) |
| `0x10` | 44 | **0** | **0** |

The cause is that `lockable-proms.md` writes families in **elided shorthand** —
`| **Am29F010 / F010B** |`, `| **MX29F010 / F020 / F040** |`,
`| **28F256 / 28F512 / 28F010 early parts** |`. `F010B` is not a part number; it
is a suffix continuation of `Am29F`. So no literal, lexical or prefix rule can
map DB tokens onto doc rows — **the mapping is a human judgement per token, and
that is the actual LOCK-01 task: 273 tokens against 126 family rows.** It is also
exactly the DATA-04-compliant kind of curation (the note's negative result is what
licenses it), and exactly the kind of table `check_sdp_capability_invariants.py`'s
Class 2(b) shape is built to freeze.

One consequence the planner should price in: of the 5 `0x05` entries whose tokens
all appear verbatim, **four are `AT29C*`, which `lockable-proms.md` §15 records as
"No explicit SDP state"** — i.e. they curate to `documented-not-readable`, not
readable. And `W29EE011` §1 is "Usually no for SDP". So the verbatim-match set is
not a readable set; it is just the easy-to-locate set.

---

## Host Patterns Being Extended (Priority 5)

### `sdp_capability.py` — the shape D-05/D-06 copy

`[FILE firestarter_app/firestarter/sdp_capability.py]`, 290 lines.

**The literal-frozenset shape, with provenance comment** (`:60-158`). The comment
block above the binding carries: the derivation source (`120-sdp-partition.json`),
the "transcribed, never re-derived" rule, the reason token counts differ from
entry counts (four tokens appear on two entries each — SGS-THOMSON/ST second
sources — so 43 entries yield 65 tokens), the element-wise proof pointer, and the
gate that freezes the binding shape. Then:

```python
SDP_CAPABLE_TOKENS: frozenset[str] = frozenset(
    {
        # ATMEL
        "AT28BV256",
        …
        # XICOR
        "X28C64(NONSTANDARD)",
        "X28HC64(NONSTANDARD)",
        …
    }
)
```

Per-vendor `#` comment headers group the literals. **Parentheticals are retained
verbatim and uppercased** (`X28C64(NONSTANDARD)`) — a direct consequence of the
no-strip rule. Two sibling tables use the same shape: `FRAM_TOKENS` (`:165`, 2
tokens) and `PRE_SDP_NAMED_TOKENS` (`:170-185`, 12 tokens).

**Reason-fragment constants** (`:187-193`) — *"tests assert on these stable
substrings rather than whole sentences"*:

```python
REASON_NOT_FOUND = "not found in the chip database"
REASON_WRONG_PROTOCOL = "SDP lock/unlock applies only to protocol 0x0D parallel EEPROMs"
REASON_FRAM = "ferroelectric RAM (FRAM)"
REASON_NOT_CAPABLE = "not on the SDP-capable list"
REASON_ALLOWED = "SDP-capable per infoic.xml INFOIC2PLUS flags bit 15"
```

This is the D-08 precedent for machine-stable tokens, one level below the class
token: substrings, not sentences.

**`split_part_number_tokens`** (`:196-207`), in full:

```python
def split_part_number_tokens(part_number: str) -> tuple[str, ...]:
    """Comma-split a DB `part_number` string into uppercased alias tokens.

    Rule: key on the exact token as it appears in `part_number`; do **not**
    strip parentheticals — stripping collapses `AT28C64B(Non-Standard)` onto
    the separate `AT28C64B` entry and produces a spurious MIXED verdict
    (`120-SDP-PARTITION.md` §5), and it makes the key not a function of one
    entry.
    """
    return tuple(
        token.strip().upper() for token in part_number.split(",") if token.strip()
    )
```

**`sdp_capability_for_entry`** (`:210-272`) — the signature D-06 generalises. Its
four-stage structure, in order:

1. falsy entry → `(False, f"{display_name.upper()}: {REASON_NOT_FOUND}")`;
2. **`if "protocol-id" not in entry: raise KeyError(...)`** (`:229-238`) — the
   hard fail, whose message names the trap explicitly: *"This is very likely the
   *programmer* dict returned by resolve_chip()/convert_to_programmer(), which
   carries neither 'protocol-id' nor 'name' — pass the full dict returned by
   db.get_eprom() instead. A silent default here is exactly how
   check_eprom_blank's _SRAM_PROTO_IDS short-circuit became vacuous in
   production (RESEARCH F-06); this predicate hard-fails instead."*;
3. wrong protocol → refuse, naming the observed protocol as `0x%02X`;
4. FRAM tokens → refuse with a physical reason; then the **unanimity rule**:

```python
    unrecognised = [token for token in tokens if token not in SDP_CAPABLE_TOKENS]
    if unrecognised:
        described = [
            f"{token} (pre-SDP generation)"
            if token in PRE_SDP_NAMED_TOKENS
            else f"{token} (unrecognised)"
            for token in unrecognised
        ]
        return False, (
            f"{display_name.upper()}: {REASON_NOT_CAPABLE}: {', '.join(described)}. "
            …
        )
    return True, f"{display_name.upper()}: {REASON_ALLOWED}"
```

**This is already three-state in its *reporting*** — a refused token is described
either as `(pre-SDP generation)` or `(unrecognised)`, from a second literal
frozenset. D-06's third state is therefore a *generalisation of an existing
pattern*, not a new one: replace the two-way `described` with a three-way lookup
and return a class token instead of a bool.

**Exact generalisation cost to `-> tuple[str, str]`:**
- signature + return type on `sdp_capability_for_entry`'s sibling (the new module
  gets its own function; `sdp_capability_for_entry` itself is **not** edited —
  D-16 forbids touching this file for DATA-06, and D-05 puts the new table in a
  **new** module);
- the `(bool, reason)` shape's four early returns become four `(class_token,
  reason)` returns — a mechanical rewrite in the new module;
- the "answer only if every token is `documented-readable`" rule is
  `all(table.get(t) == "documented-readable" for t in tokens)`, and the refusal
  must name **the specific offending token and its state**, which the
  `described`-list idiom above already does.
- `sdp_capability(chip_name, db)` (`:275-290`) is the name-keyed wrapper
  (`sdp_capability_for_entry(db.get_eprom(chip_name), chip_name)`), whose docstring
  records that a pure `(entry, name)` predicate is unachievable without the DB
  because the programmer dict has no part number. The new module needs the same
  two-function shape.

### `sdp_honesty.py` — quoted in full (all three functions)

`[FILE firestarter_app/firestarter/sdp_honesty.py]`, 92 lines. Import set
(`:29-30`) is exactly `firestarter.exceptions` (`EpromOperationError`,
`FirmwareOutdatedError`) and `firestarter.messages` (`MSG_ERR_UNKNOWN_CMD`).
**No `click`** — confirmed, and the invariant is machine-checked by
`tests/test_sdp_honesty.py::test_sdp_honesty_module_imports_only_leaf_firestarter_modules`
(`:159`).

```python
def unreadable_state_caveat() -> str:
    return (
        "The resulting protection state cannot be read back on this chip "
        "family, so this is not a claim about the chip's actual state."
    )


def emission_summary(mode: str, chip_name: str) -> str:
    chip_upper = chip_name.upper()
    return (
        f"SDP {mode} sequence for {chip_upper} was emitted. {unreadable_state_caveat()}"
    )


def map_unknown_cmd_to_outdated(
    exc: EpromOperationError, mode: str, chip_name: str
) -> FirmwareOutdatedError | None:
    if exc.error_code != MSG_ERR_UNKNOWN_CMD:
        return None
    chip_upper = chip_name.upper()
    return FirmwareOutdatedError(
        f"{chip_upper}: attached firmware does not implement SDP "
        f"{mode} (unknown command) -- upgrade with "
        "'firestarter fw --install'."
    )
```

**How `map_unknown_cmd_to_outdated` is keyed:** on `exc.error_code ==
MSG_ERR_UNKNOWN_CMD` — the message **id integer** (0xAB), never text. It
**returns** rather than raises, deliberately, *"keeps the caller in control of
exception chaining (`raise ... from exc`)"* (`:80-83`). The `"SDP {mode}"` wording
appears only in the constructed message.

**Cost of generalising off `"SDP {mode}"` — every test that pins the wording**
`[CMD grep -rn "sdp_honesty|unreadable_state_caveat|emission_summary|map_unknown_cmd_to_outdated" --include=*.py]`:

| site | what it pins | breaks on a wording change? |
|------|--------------|------------------------------|
| `tests/test_sdp_honesty.py:125-150` (`test_firmware_too_old_is_reported_when_unknown_cmd_comes_back`) | `"firestarter fw --install" in str(outdated)` **and** `("outdated" in lower) or ("does not implement" in lower)`; plus a negative leg (`MSG_ERR_TIMEOUT` → `None`) | **No** — both assertions are substring/disjunctive and survive replacing `"SDP {mode}"` with any other operation name, provided `"does not implement"` and the `fw --install` hint stay. |
| `tests/test_sdp_honesty.py:68-90` | `"was emitted"`, `"cannot be read back"`, `"not a claim about the chip's actual state"` in `emission_summary(...)` for both directions | Only if `emission_summary` itself is edited. A **new sibling** function leaves it untouched. |
| `tests/test_sdp_honesty.py:87,108` | no duration figure; no fabricated lock-state boolean | unaffected |
| `tests/test_chip_test_sdp_leg.py:1241-1250, 2168-2182` | that `chip_test.py` **composes** `unreadable_state_caveat()` rather than re-authoring the sentence | breaks only if the caveat's **text** changes |
| `firestarter/cli_handlers.py:2405`, `:2412` | production callers composing the caveat | breaks only if the caveat's text changes |
| `firestarter/chip_test.py:1480` | production caller | same |
| `tools/check_no_exists_proxy.py:188` | names `tests/test_sdp_honesty.py` in a list | inert w.r.t. wording |

**Conclusion: generalising is cheap.** The lowest-risk route is a **new sibling**
(e.g. `map_unknown_cmd_to_outdated_for(operation_label, …)`) plus a
`not_readable` caveat accessor, leaving `emission_summary` and
`unreadable_state_caveat`'s text byte-identical — which keeps all seven pinning
sites green and honours D-11's "one copy of the sentence".

**⚠ D-11's premise is factually wrong** — see Contradiction C-4.
`unreadable_state_caveat()` has **three landed production callers**
(`cli_handlers.py:2405`, `cli_handlers.py:2409`, `chip_test.py:1480`), so Phase
134's leg-report rows did land. Only `emission_summary()` and
`map_unknown_cmd_to_outdated()` are still callerless.

### `tools/check_sdp_capability_invariants.py` — the gate to model on (D-05), not weaken (D-16)

`[FILE firestarter_app/tools/check_sdp_capability_invariants.py]`, 364 lines.

- **Target resolution:** `FIRESTARTER_SDP_CAPABILITY_SRC` env seam, default
  `_HERE/../firestarter/sdp_capability.py` (`:78-81`) — **one** `..` from
  `tools/`, i.e. the app's own package. Recorded in
  `tests/scan_paths.py::SAME_REPO_LOOKALIKES` as a same-repo look-alike, **not** a
  cross-repo path.
- **Two violation classes** (`:19-43`):
  - **Class 1 — permit-by-default.** (a) any `return` of a tuple literal whose
    first element is the constant `True` that is not lexically dominated, earlier
    in the same function body **by line number**, by an `in`/`not in` membership
    test against the name `SDP_CAPABLE_TOKENS`; (b) any **bare `except:`** anywhere
    in the module.
  - **Class 2 — widenable allow-set.** (a) `SDP_CAPABLE_TOKENS` bound anywhere
    other than exactly once at module level; **(b)** that binding's value being
    anything other than a direct `frozenset(...)` call whose sole argument is a
    set/list/tuple display **of string literals only** — never a comprehension,
    generator, call, or bare name; (c) any augmented assignment, `.union()`,
    `.add()`, `.update()` or `|=` targeting it.
- **Fail-closed on** a missing target path (`ERROR`, exit 1) and on a
  **zero-symbol scan** (`SDP_CAPABLE_TOKENS` not found exactly once).
- **Exit codes** (`:59-67`): 0 = clean + bound exactly once, prints a `PASS:` line
  naming the resolved path; 1 = any violation, missing path, or unparsable target.

**How it is invoked — measured, and it is not what one might assume.**
`[CMD grep -rn "check_sdp_capability_invariants" firestarter_app/.github/workflows firestarter_app/tools/ci_parity.sh]`
returns **nothing**. The only CI step naming a `tools/check_*` script is
`python tools/check_mypy_watermark.py` `[FILE firestarter_app/.github/workflows/ci.yml:87]`.
The gate runs **through pytest**: `firestarter_app/tests/test_check_sdp_capability.py`
invokes it as a **real subprocess** (`subprocess.run`, `:44`, `:60-62`) across 9
legs — clean source (`:76`), default target exists (`:94`), PASS line names the
file (`:111`), planted permit-by-default fails (`:129`), planted widenable
allow-set fails (`:146`), planted bare-except also reported (`:163`), clean
fixture via the env seam still passes (`:183`), fail-closed on missing target
(`:217`), fail-closed on zero-symbol scan (`:237`) — with real planted fixtures
`tests/fixtures/planted_permit_by_default.py` and
`tests/fixtures/planted_widenable_allowset.py`. The CI leg that runs it is
therefore `pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70`
`[FILE firestarter_app/.github/workflows/ci.yml:90]`.

**Wiring a sibling gate for the new table** therefore means: a new
`tools/check_<name>_invariants.py` with its own `FIRESTARTER_<NAME>_SRC` env seam
(one `..` from `tools/`), a paired `tests/test_check_<name>.py` that drives it as
a subprocess, at least one **real planted-violation fixture per class** under
`tests/fixtures/`, and fail-closed legs for missing-path and zero-symbol. No
workflow edit is needed. Note `tests/fixtures/` is excluded from both ruff
(`extend-exclude`, `[FILE firestarter_app/pyproject.toml:121]`) and mypy
(`exclude = ["^tests/fixtures/"]`, `:170`) — so a planted fixture may be
deliberately invalid.

**D-16's "not weakened" is machine-checkable today** in the exact style of
`test_b15_page_size_corroboration.py::test_sdp_capability_module_untouched_this_plan`
(`:246-260`), which asserts the module still imports and still carries the
`"12 of the 84"` docstring prose unedited. That is the in-tree precedent for a
"this plan did not touch that file" guard.

### `cli_handlers.py` — the `_DevGroup` gate and the registration template

`[FILE firestarter_app/firestarter/cli_handlers.py]`.

- **`_DEV_TOOLS_ENABLED: bool = is_dev_tools_enabled()`** at **`:1305`** — a module
  global, computed **once at import time**. The preamble (`:1288-1303`) states the
  gate is **both** mechanisms, not either: the frozen global plus non-registration.
- **`class _DevGroup(click.Group)`** at **`:1308`**, with `get_command` as the
  **only** override (`:1332-1338`):

```python
    def get_command(self, ctx: click.Context, cmd_name: str) -> Optional[click.Command]:
        real = super().get_command(ctx, cmd_name)
        if real is not None:
            return real
        if cmd_name in BETA_ONLY_DEV_COMMANDS:
            raise click.UsageError(dev_command_gate_message(cmd_name), ctx=ctx)
        return None
```

  The docstring (`:1320-1330`) records that this hook choice is **empirically
  settled** by `tests/test_click_group_gate_hook.py`: `resolve_command()` calls
  `get_command()` itself and only falls through to its generic error when
  `get_command` returns `None`, so **`resolve_command` needs no override** and
  **`list_commands` needs none either**.
- **The group** at `:1346-1358`: `@cli.group(name="dev", cls=_DevGroup)` +
  `@map_typed_errors`, with a docstring that states *"On a stable install, only
  `read` and `test` are available in this group"*.
- **The conditional-registration template, verbatim** `[FILE …:1471-1507]` — this
  is the pattern a new `lock-status` command copies:

```python
if _DEV_TOOLS_ENABLED:

    @dev.command(name="addr")
    @click.argument("eprom", shell_complete=_complete_eprom)
    @click.argument("address")
    @click.option(
        "-i", "--input-enable", "input_enable", is_flag=True,
        help="Input, pulls OE pin high.",
    )
    …
    @click.pass_obj
    @map_typed_errors
    def dev_addr(
        app: AppContext, eprom: str, address: str,
        input_enable: bool, chip_disable: bool,
    ) -> None:
        """Direct access to address lines and control register."""
        eprom_data = resolve_chip(eprom, db=app.db)
        ok = app.eprom_operator.dev_set_address_mode(
            eprom, eprom_data, address,
            flags=_build_op_flags(input_enable=input_enable, chip_disable=chip_disable),
        )
        sys.exit(0 if ok else 1)
```

  Note the decorator order — `@dev.command` → `@click.argument`/`@click.option` →
  `@click.pass_obj` → `@map_typed_errors` — and that the body ends
  `sys.exit(0 if ok else 1)`, which **D-10 deliberately breaks**: `lock-status`
  needs three exit-code bands, not two.
- **The six gate blocks** are at `:1391` (`reg`, defined `:1409`), `:1471`
  (`addr`), `:1510` (`consistency-check`), `:1605` (`write-cycle`), `:1662`
  (`fault-inject`), `:1889` (`validate-family`). The two ungated ones are
  `@dev.command(name="read")` at `:1360` and `@dev.command(name="test")` at `:2449`.

**`--force` precedents.** Three top-level commands, all with the same
`-f`/`--force` flag shape `[FILE firestarter_app/firestarter/cli_handlers.py]`:

| command | option block | handler | help text |
|---------|-------------|---------|-----------|
| `blank` | `:847-852` | `:855` | `"Force, even if the VPP or chip id doesn't match."` |
| `erase` | `:866-871` | `:889` | `"Force, even if the VPP or chip id doesn't match."` |
| `id` | `:914-919` | `:925` | `"Force, even if the VPP is not correct."` |

All three thread it as `_build_op_flags(force=force)`, and `_build_op_flags`'s
`force: bool = False` parameter is at `:324`. Firmware-side, `FLAG_FORCE 0x01`
`[FILE firestarter/include/firestarter.h:154]` / `FLAG_FORCE = 0x01`
`[FILE firestarter_app/firestarter/constants.py:108]`, and its effect on the read
path is the chip-ID severity downgrade quoted in §"The `0x06` / `0x05` Read
Sequences". D-07's `--force` therefore has both a CLI precedent and a firmware
precedent, but note: `FLAG_FORCE` currently means *"downgrade a chip-ID mismatch
to a warning"*, not *"bypass a host-side table refusal"* — D-07's use is a
host-side gate, and whether the flag bit is even sent is a separate decision.

### `channel.py` — the three functions and the tuple to extend

`[FILE firestarter_app/firestarter/channel.py]`, 173 lines.

- **`BETA_ONLY_DEV_COMMANDS`** at **`:58-65`** — a 6-tuple
  `("reg", "addr", "consistency-check", "write-cycle", "fault-inject", "validate-family")`.
  Its comment (`:50-57`) is precise about what it is *not*: *"Consulted for the
  informative-refusal message ONLY … the actual gate is non-registration of the
  six `@dev.command` blocks, not membership in this tuple, so this list existing or
  not existing changes nothing about whether a command runs; it only changes
  whether its refusal is informative or Click's own generic 'No such command'."*
- **`is_dev_tools_enabled()`** at **`:144-162`** — `is_prerelease_build() or
  dev_tools_enabled_by_env()`, **call-time and unmemoized**, with a docstring that
  explicitly instructs a Click-registration caller to *"capture this into its own
  module global at import time"*.
- **`dev_command_gate_message(name)`** at **`:165-173`** — the refusal text,
  three lines: the "pre-release builds only" sentence, the
  `pip install --pre --upgrade firestarter` hint, and the
  `FIRESTARTER_DEV_TOOLS=1` bench-override hint.
- `dev_tools_enabled_by_env()` at `:115-141` — exact literal `"1"` only, read at
  call time, **no `.strip()` and no case-folding**, because *"`bool("0")` and
  `bool("false")` are both `True`"*.
- Current package version: `__version__ = "3.0.0b21"` `[FILE firestarter_app/firestarter/__init__.py:1]`
  — a pre-release, so `_DEV_TOOLS_ENABLED` is `True` in this checkout.

### The three gating test files — what each asserts, and what a new name must touch

| file | lines | asserts | must a new beta-only name be added? |
|------|------:|---------|-------------------------------------|
| **`tests/test_dev_tools_channel_gate.py`** | 169 | `test_beta_only_dev_commands_matches_measured_baseline` (`:149-158`) asserts `channel.BETA_ONLY_DEV_COMMANDS == ("reg","addr","consistency-check","write-cycle","fault-inject","validate-family")` — **an exact tuple, order-sensitive**. Plus the env-override fail-closed truth table (`:63`, `:75`, `:84`, `:112`), the gate-message legs (`:132`, `:139`), and `test_channel_module_source_contains_no_open_call` (`:165`). | **YES** — the 6-tuple literal becomes a 7-tuple, in the right position. |
| **`tests/test_dev_group_channel_gating.py`** | 348 | `_GATED_NAMES` frozenset (`:63-72`, 6 literals, **deliberately not imported from `channel.py`** *"so this test does not become trivially self-confirming"*), `_STABLE_NAMES = {"read","test"}` (`:73`), `_ALL_EIGHT_NAMES` (`:74`). Runs a real child process per simulated version via `_CHILD_PROGRAM` (`:83+`) that asserts `firestarter.cli_handlers` is not yet imported, sets `__version__`, **then** imports — so `_DEV_TOOLS_ENABLED` is computed against the simulated version by construction. Legs: `:202` stable help lists only read/test, `:215`, `:220` exact-set, `:227` gated name → channel message, `:238` genuine typo → Click's generic error, `:256` prerelease lists all eight, `:264`, `:269`, `:279` both channels pinned, `:313`/`:328`/`:342` env-override legs. | **YES** — `_GATED_NAMES` 6→7 and `_ALL_EIGHT_NAMES` 8→9. **Three test function names become misnomers**: `test_simulated_prerelease_help_lists_all_eight`, `test_simulated_prerelease_dev_commands_is_all_eight`, `test_simulated_stable_with_env_override_registers_all_six_gated_names`. |
| **`tests/test_click_group_gate_hook.py`** | 161 | Uses a single `_GATED_NAME = "reg"` (`:61`). Legs: informative refusal not generic (`:98`), typo still generic (`:110`), real command runs (`:120`), **`test_resolve_command_was_never_overridden`** (`:129`), **`test_list_commands_needs_no_override_gated_name_is_simply_absent`** (`:135`), Click version captured (`:148`), `MultiCommand` deprecated-alias probe (`:155`). | **NO** — it is parameterised on one name and needs no edit. Worth stating so the planner does not fund a change here. |

**A fourth file the planner must not miss.** `tests/test_dev_gate_reads_no_firmware_source.py`
(110 lines) asserts the gate callable's source contains **no `open(` call** (`:76`)
and **no firmware path token** (`:91`), and that `channel.py` calls no `open()`
anywhere (`:103`). This is the machine-check behind D-01's "channel gating is
host-side only" — any attempt to make the firmware aware of the channel breaks it,
by design.

**And a fifth, which is the one most likely to be forgotten:** the **syrupy
snapshot**. `tests/__snapshots__/test_characterization.ambr` (1388 lines) contains
a `test_help_dev` snapshot (`:124-150`) pinning the **full `dev --help` command
list** — currently eight rows (`addr`, `consistency-check`, `fault-inject`,
`read`, `reg`, `test`, `validate-family`, `write-cycle`), each with its truncated
one-line help. Adding `lock-status` inserts a ninth row (alphabetically between
`fault-inject` and `read`) and **requires a snapshot regeneration**
(`pytest tests/test_characterization.py --snapshot-update`). The test body is
three lines `[FILE firestarter_app/tests/test_characterization.py:328-331]`:
`stdout, stderr, rc = run_firestarter("dev", "--help"); assert rc == 0; assert stdout == snapshot`.
This is one of the two "syrupy snapshots" D-08 refers to. It is also why D-08's
*"tests assert the exact token rather than grepping wording"* matters: the class
token must be assertable **without** a full-text snapshot.

### Chip resolution — the trap, confirmed, plus one interaction nobody has named

`[FILE firestarter_app/firestarter/database.py:394-407]` — `_map_data`'s returned
dict keys include **`"name"`** (from `ic.get("part_number")`) and
**`"protocol-id"`**, plus `manufacturer`, `memory-size`, `pin-count`, `vpp_mv`,
`vcc_mv`, `pulse-delay`, `verified`, `info-flags`, `flags`, `pin-map`,
`electrical-type`, optionally `chip-id` and `page_size`. `get_eprom(chip_name)`
(`:500-526`) returns exactly this.

`convert_to_programmer(full)` (`:529-...`) keeps only `memory-size`,
**`algorithm`** (`= full.get("protocol-id", 0)`), `pin-count`, `vpp_mv`,
`pulse-delay`, and optionally `chip-id`, `bus-config`, `page_size`
`[FILE …/database.py:541-560]`. **It carries neither `protocol-id` nor `name`** —
confirmed ✓, exactly as `sdp_capability_for_entry`'s `KeyError` message says.

**The correct call is `app.db.get_eprom(eprom)`**, and there is a landed
production precedent for doing both in one handler
`[FILE firestarter_app/firestarter/cli_handlers.py:713-726]`:

```python
    # D-04 auto-set (v1.22 HOST-04): decided here, in the handler, because
    # this is the last place with both the chip NAME and app.db — resolve_chip's
    # programmer dict carries neither `protocol-id` nor `name` (RESEARCH F-06).
    …
    sdp_entry = app.db.get_eprom(eprom)
    is_protocol_0x0d = (
        bool(sdp_entry) and sdp_entry.get("protocol-id") == SDP_PROTOCOL_ID
    )
    allowed, sdp_reason = sdp_capability(eprom, app.db)
```

**The un-named interaction: `resolve_chip` refuses before any read.**
`[FILE firestarter_app/firestarter/chip_resolver.py:16-45]` — `resolve_chip` raises
`ChipNotFoundError` when the name resolves to nothing, and
**`ChipNotImplementedError` when `support_status != "supported"`**, and that guard
*"fires BEFORE any wire dict is built or serial byte emitted"*. Measured
`support_status` distribution `[CMD python3 …]`:

| algorithm | `supported` | other |
|-----------|------------:|-------|
| 5 | 27 | — |
| 6 | 190 | — |
| 13 | 75 | **9 `adapter-required`** |
| 16 | 39 | — |
| 52 | — | **1 `protocol-not-implemented`** |

So **10 rows can never reach the read path via `resolve_chip`** (the 9
adapter-required `0x0D` rows and the 1 `0x34` row). D-12's invariant must decide
whether those rows resolve to a *class* (a pure predicate over the DB says yes) or
to an *exception* (the CLI path says yes) — and it must not assert that a class
token and a CLI outcome agree for them, because they structurally cannot.

---

## DATA-06's Documentation Home (Priority 6)

### `doc/infoic-field-dictionary.md` — structure, measured

288 lines `[CMD wc -l]`. Section map `[CMD grep -n "^#"]`:

| line | heading |
|-----:|---------|
| :5 | `## infoic.xml Field Dictionary` |
| :16 | `### \`package_details\` (uint32 hex) — CONFIRMED` |
| :33 | `### \`type\` … — CONFIRMED` |
| :49 | `### \`variant\` … — CONFIRMED` |
| :71 | `### \`protocol_id\` (uint8 hex) — CONFIRMED` |
| **:107** | `### \`flags\` (uint32 hex) — CONFIRMED for decoded bits; UNKNOWN for bits 3/6/7` |
| :140 | `### \`voltages\` … — CONFIRMED` |
| :178 | `### \`pin_map\` … — CONFIRMED` |
| :196 | `### \`pulse_delay\` … — CONFIRMED` |
| :221 | `### \`chip_id\` … — CONFIRMED` |
| :231 | `### \`code_memory_size\` … — CONFIRMED` |
| :241 | `### \`page_size\` … — CONFIRMED` |
| :251 | `### \`chip_info\` … — CONFIRMED` |
| :267 | `### \`blank_value\` (uint8 hex, optional) — CONFIRMED` |
| **:277** | `## Summary: build_db.py Known Bugs vs Correct Semantics` |

**§`flags` is at `:107` ✓ (CONTEXT.md's citation).** Inside it, the
source-confirmed bit table runs `:113-124`, and **bit 14 is at `:120`, bit 15 at
`:121`** ✓ — quoted exactly:

```
| 14    | `0x00004000` | `MP_OFF_PROTECT_BEFORE`    | Off-protection before operation                     |
| 15    | `0x00008000` | `MP_PROTECT_AFTER`         | Protect after operation                             |
```

**The per-field entry shape**, e.g. `### page_size` in full `[FILE …:241-249]`:

```markdown
### `page_size` (uint32 hex) — CONFIRMED

**Source:** [`database.c#L598`](…/src/database.c#L598) @ `a8efaedc`

Page-write size for EEPROM/Flash. Typically 64 or 128 bytes for 28C-family; `0` or `1` if not applicable to the device type.

**build_db.py usage:** Not currently stored in `chip_database.json`. No decode bug; simply not used yet.
```

So the template is: `### \`<field>\` (<type>) — CONFIRMED|INFERRED|UNKNOWN` /
`**Source:** [permalink] @ \`a8efaedc\`` / prose / `**build_db.py usage:** …`,
separated by `---`. The **citation commit is pinned once** at `:11-14`:
`a8efaedc236c1d9718bd28299dfbb99536b010ff` (2026-03-23), permalink base
`https://gitlab.com/DavidGriffith/minipro/-/blob/a8efaedc…/src/`, with the
instruction *"All per-attribute source citations in this file use the SHA above.
To verify a citation: `<permalink base><file>#L<line>`."*

**The summary table at `:277`** has columns
`| Bug ID | Attribute | Correct decode | Current build_db.py behavior | Phase 57 fix |`
with four rows BUG-1…BUG-4. DATA-06's section is **not a bug** — it is a
"field decoded correctly, consumer absent" statement — so it does not naturally
produce a BUG row. That is a legibility decision for the planner: either the
summary table gains a non-bug row, or the new section stands alone and the summary
stays four rows. **Stating it because CONTEXT.md D-13 says the section "feeds that
file's summary" and, as measured, the summary's schema has no column for
"correctly decoded, no consumer".**

**Two staleness facts in that file the planner should know but must not be
required to fix** (scope discipline):
- `### page_size` at `:247` says *"Not currently stored in `chip_database.json`"* —
  **now false** since Phase 149 (20 rows carry `page_size`; `infoic_page_size_raw`
  is on 744). See Contradiction C-8.
- The file's closing line `:288`: *"This file is the canonical authority for
  Phase 57 code changes. Do not modify `build_db.py` decode behavior in Phase 56 —
  that is Phase 57's scope."* The whole file is framed as Phase-57 scoped. A
  DATA-06 section landing in it is correct per D-13 but sits inside that framing.

### The two one-line-pointer sites — exact lines confirmed

**`doc/package-details.md`** (68 lines). Bit 14 at **`:43`**, bit 15 at **`:44`** ✓:

```
| 14    | `0x00004000`   | `MP_OFF_PROTECT_BEFORE`                 | Off-protection before operation                                                           | CONFIRMED |
| 15    | `0x00008000`   | `MP_PROTECT_AFTER`                      | Protect after operation                                                                   | CONFIRMED |
```

(This table has a fifth `CONFIRMED` status column; the next heading is
`### Bits Without a Defined MP_* Constant (UNKNOWN)` at `:49`.)

**`doc/protocol-flags.md`** (52 lines). Bit 14 at **`:24`**, bit 15 at **`:25`** ✓:

```
| 14    | `0x00004000`   | `MP_OFF_PROTECT_BEFORE`                 | Off-protection before operation                                                       |
| 15    | `0x00008000`   | `MP_PROTECT_AFTER`                      | Protect after operation                                                               |
```

(Four columns, no status column. `:28` is the WARNING-5 bit-4 note.)

Both tables document **minipro's bit semantics**, which D-13 correctly identifies
as a *different fact* from the emitted field's runtime status. Neither says anything
about a consumer.

### The element-wise proof D-15 must cite

`[FILE firestarter_app/tests/test_sdp_db_invariant.py:584-621]`:

```python
def test_sdp_partition_matches_infoic_derived_field_element_wise() -> None:
    """GATE-08 leg 1 (Phase 136.1 Plan 02, PROV-02/03): the production
    transcription (`_partition_0x0d`, `SDP_CAPABLE_TOKENS`-based) must equal,
    element-wise, the partition derived directly from chip_database.json's
    own `protect_on_after` field (Plan 136.1-01) -- a genuinely
    infoic.xml-derived source, not a hand-curated snapshot.
    …
    """
    db = json.loads(_DB_FILE.read_text(encoding="utf-8"))
    allow_transcription, refuse_transcription = _partition_0x0d(db)
    allow_field, refuse_field = _partition_from_protect_on_after_field(db)

    _assert_two_partitions_match(
        allow_transcription, allow_field,
        "SDP_CAPABLE_TOKENS transcription", "protect_on_after field",
    )

    for label, allow, refuse in (…):
        assert len(allow) == 43 …
        assert len(refuse) == 41 …
        assert len(allow) + len(refuse) == 84 …
```

It is paired with a **non-vacuous proof**,
`test_partition_flags_a_moved_chip_via_db_field_non_vacuous` (`:629+`), which flips
a synthetic chip's `protect_on_after` from `True` to `False` and asserts
`_assert_two_partitions_match` **raises**, naming the moved chip and not an
untouched control. That pairing — a positive leg plus a synthetic-mutation
negative control — is the shape D-12's own invariant should copy.

### `test_b15_page_size_corroboration.py` — the "documentation carrying a measured refutation" precedent

261 lines `[CMD wc -l]`. Its shape, which DATA-06's proof should model:

- **A module docstring that IS the artifact.** It names the claim being refuted
  (`sdp_capability.py:32-36`'s prose *"Bit 15 is not a page-write proxy — it
  disagrees with `page_size > 1` on 12 of the 84 entries"*), states that the prose
  *"has NO enforcing test today -- this module is that test"*, and declares
  `git diff --stat -- firestarter/sdp_capability.py` **stays empty throughout**.
- **It names the two methodologies and refuses to assume they agree**: Phase 120's
  cross-token-set matching across possibly-multiple XML `<ic>` entries per alias,
  versus this test's per-row single-value comparison of
  `programming.protect_on_after` against `programming.infoic_page_size_raw`. *"this
  test does not assume they must produce the same number; it measures fresh and
  states the result."*
- **It lists every disagreeing chip by name**, 12 of them, each as
  `manufacturer/part_number -- <b15> / <raw page size>`, and then splits them by
  direction (11 false/`>1`, 1 true/`1`) and says which direction is the hazard.
- **Constants, not magic numbers:** `_ALGORITHM_0X0D = 13` (`:72`),
  `_EXPECTED_DISAGREEMENT_COUNT = 12` (`:79`).
- **Four legs** (`:145`, `:181`, `:195`, `:246`): a non-vacuous helper proof on
  hand-counted synthetic pairs; a regression check that all 84 entries carry both
  fields; the measured-count assertion; and the "module untouched this plan" guard.

**This is the template for DATA-06's proof**, and it already carries three of the
measurements D-15 wants. What DATA-06 adds is the *consumer-absence* claim, which
is provable by the grep enumerated in §"Re-derived DB Counts" — i.e. an
AST/source-scan leg asserting that `firestarter/` contains no *code* reference to
either field is the cheapest sufficient oracle (`tools/check_no_exists_proxy.py`
and `tools/check_no_community_support_status_write.py` are the in-tree shapes for
a "this string must not appear in shipped code" gate). **But note D-16 forbids a
new gate for DATA-06** — so this must be a *test*, not a `tools/check_*.py`.

### The folded todo — confirmed

`[FILE .planning/todos/pending/decode-infoic-flags-bits-14-15-protect-metadata.md]`,
dated 2026-07-10, priority `low`. Its three acceptance items, checked against the
tree:

| acceptance item | status |
|-----------------|--------|
| "build_db.py decodes both bits with comment citing minipro `database.c` @ `a8efaed`" | **MET** — `build_db.py:800-801`, and the field dictionary's §`flags` carries the `database.c#L39-L50 @ a8efaedc` citation. |
| "Fields present in regenerated chip_database.json; no behavior change in write/read paths (metadata only)" | **MET** — 744 of 746 rows; zero runtime consumers (measured above). |
| "Cross-check note: chips where firestarter's `flash_5v_page` handler already does an SDP dance should have b15=1 — flag any mismatches as findings, not failures" | **MET, and it passes**: `flash_5v_page` is the `0x05` handler and `protect_on_after` is `True` on **27 of 27** `0x05` rows. Zero mismatches. This is a free, measured finding DATA-06's section can state. |
| Its **interpretation guardrail** — *"These are **write-path reversibility hints**, NOT lock-status readability"*, with the W29C020C-vs-W29EE011 flag-identity (`0x0040c078`) and the AMD group's `0x00000078` (b14/b15 both 0) as evidence | **THE ONLY UNMET PIECE** — and it is exactly D-13/D-15's statement. |

So CONTEXT.md's "Folded Todos" claim verifies: the emit half is landed, only the
interpretation guardrail remains, and closing DATA-06 closes the todo. The planner
should mark it resolved.

The todo also carries two facts DATA-06's section can reuse verbatim (they are
`[CITED: the todo's own research provenance]`, not re-verifiable in this repo since
`infoic.xml` is gitignored and not committed): bit 14 gates minipro `-u`, bit 15
gates minipro `-P`; and *"The actual protect op in minipro is an opaque TL866
opcode (0x18/0x19) — no mechanism/region info exists to decode."*

### The negative-result note's 2026-07-29 scoped exception

`[FILE .planning/notes/infoic-xml-protection-flags-research.md:75-110]`, the tail
section, summarised with its own load-bearing sentences quoted:

- **The narrower question Phase 120 asked** was not "what kind of protection does
  this part have and can its state be read" but *only* "does this 28C-family
  protocol-`0x0D` part have an SDP command decoder at all". Bit 15 was tested
  against **that single, narrower question**.
- **Three independent probes, all passing:** 8/8 pre-SDP entries bit 15 clear (six
  with flags exactly zero); 2/2 FRAM parts clear (both flags zero); 4/4
  datasheet-of-record Atmel parts set. *"No probe failed and nothing needed a
  special case."*
- Result: all 84 `0x0D` entries matched, zero unmatched, zero MIXED under
  exact-token keying, ALLOW 43 / REFUSE 41.
- The hedge it sharpens: bit 15 and `page_size > 1` **disagree on 12 of 84**, so
  bit 15 is not a page-write proxy.
- **The governing sentence, quoted in full:** *"Both findings are correct about
  different questions. The 2026-07-10 verdict above (taxonomy: `protection_kind` /
  `status_readable` / `unlockability`) and this 2026-07-29 result (capability: does
  an SDP command decoder exist at all) are both correct, and neither overturns the
  other — treat neither as overturned by the other."*
- *"Nothing reads `infoic.xml` at runtime or in CI; `infoic.xml` is not committed
  to either sub-repo; the shipped artifact is a static transcribed token table."*
- *"The loose ends stay loose"* — bit 22 and bit 9 remain undecoded, unaffected by
  the exception, and declined by D-14.

**This is the whole reason hand-curation is DATA-04-compliant** rather than a
violation of it, and the scoped exception does **not** reopen it: the 2026-07-29
result is about SDP *capability*, not *readability*. Nothing in this phase should
re-investigate `infoic.xml` for readability.

---

## The Curated Table's Source Document (Priority 7)

### `firestarter_app/doc/lockable-proms.md` — 399 lines, 126 family rows

Preamble, quoted because it is the definition LOCK-01's `readability` axis must
transcribe `[FILE …/lockable-proms.md:1-3]`:

> Below is a **family-level master list for common JEDEC-compatible parallel NOR flash and EEPROM-style flash**, mainly from the 1990s through mid-2000s.
>
> "Readable" means a programmer can issue a documented command and directly determine whether a sector, block, boot block, OTP area, or protection mechanism is active. It does **not** include merely attempting a write and seeing whether it fails.

**§Key, in full** `[FILE …:5-14]` — the six-term vocabulary D-06's three-state
mapping must reduce:

| Marking | Meaning |
|---------|---------|
| **Yes—sector** | Individual sector/block state can be queried |
| **Yes—global** | A device-wide protection state can be queried |
| **Yes—special** | Boot block, OTP, security sector, PPB or lock register can be queried |
| **Indirect** | No explicit readable state; determined by programming tests or configuration |
| **No** | No documented readable protection-status mechanism |
| **Permanent** | At least one protection mode cannot normally be reversed |

Note: `Yes—global` and `Indirect` **do not appear in any data row** — every row uses
`Yes—sector`, `Yes—special`, `Yes—sector/special`, `Yes—block`, `Yes—block/special`,
`Variant-dependent`, `Usually no …`, `No explicit …`, or `Not comparable`. So the
Key over-specifies and the rows under-use it; the actual row vocabulary is wider
than the Key (e.g. `Yes—block` and `Yes—block/special` are used but not defined in
the Key). **That is a real transcription hazard for LOCK-01** and it is measured,
not inferred.

**Row counts per section** `[CMD python3 … table-row counter over the file]`:

| section | data rows |
|---------|----------:|
| Key (vocabulary, not families) | 6 |
| 1. Winbond parallel flash | **9** |
| 2. AMD Am29F and Am29LV families | 12 |
| 3. Fujitsu MBM29 families | 5 |
| 4 → Older S29AL/S29JL/S29PL-style parts | 5 |
| 4 → MirrorBit GL families | 5 |
| 5 → Classic 5 V MX29F | 4 |
| 5 → Low-voltage and later families | 4 |
| 6. STMicroelectronics M29 families | 6 |
| 7. AMIC A29 families | 5 |
| 8. EON EN29 families | 5 |
| 9. ISSI IS29 families | 3 |
| 10. Alliance/ASD/PMC-compatible 29F parts | 5 |
| 11. Intel command-set parallel NOR | 11 |
| 12. Sharp LH28 families | 5 |
| 13. Micron MT28 families | 5 |
| 14 → SST39SF/VF classic devices | 4 |
| 14 → SST boot-block and special families | 6 |
| 15. Atmel/Microchip AT29C families | 6 |
| 16. Atmel/Microchip AT49 families | 7 |
| 17. Parallel EEPROM families: 28Cxxx | 8 |
| 18. Firmware Hub and LPC flash | 6 |
| **TOTAL family rows** | **126** |
| (total table rows incl. the Key) | 132 |

**18 numbered sections, 4 of which are split into 2 sub-tables each (§4, §5, §14 —
and §14 carries an explicit correction), giving 22 tables.** That is the sizing
figure for LOCK-01's transcription task: **126 rows**, against **273 DB alias
tokens** on the two curated algorithms.

**§Practical summary's partition** `[FILE …:333-360]` — three lists, family-level,
verbatim headings and members:

- *"Families where readable lock status is normally expected"* (13 bullets): AMD
  Am29F/Am29LV/Am29DL · Fujitsu MBM29F/MBM29LV · Macronix MX29F/MX29LV/MX29GL ·
  ST M29F/M29W/M29EW · AMIC A29F/A29L · EON EN29F/EN29LV ·
  Spansion/Cypress S29AL/S29JL/S29GL · **Intel/Sharp/Micron block-erase
  command-set devices** · **Firmware Hub/LPC devices with block-lock registers** ·
  **Winbond W29C020C boot-block lock detection** · Winbond W49F sector-protection
  families · Many Atmel AT49F/BV devices.
- *"Families where ordinary protection state usually is not directly readable"*
  (6 bullets): Atmel AT29Cxxx · Atmel AT28Cxxx · common SST SST39SFxxx · common
  SST SST39VFxxx (SDP-only) · Winbond W29EE / ordinary SDP-only W29C variants ·
  most conventional parallel EEPROMs using SDP.
- *"Families with potentially irreversible protection"* (7 bullets): **W29C020C
  boot-block lockout** · some AT49F/BV boot-block lockout implementations ·
  Spansion/Cypress PPB persistent-protection configurations ·
  Spansion/Cypress and Macronix OTP/security-sector locks ·
  Intel/Sharp/Micron OTP parameter regions · certain block lock-down
  configurations · some Firmware Hub devices under a hardware strap / lock-down
  policy.

**Note the cross-cut:** the readable list includes Intel/Sharp/Micron block-erase
devices, which are the **`0x10`** family D-02 deliberately leaves unimplemented,
and Firmware Hub/LPC parts, which are **not in the RURP-reachable DB at all**. So
the doc's readable set is strictly larger than the phase's implementable set —
another reason the class for `0x10` should be derived from `protocol-id`, not from
the table's readability verdict.

**§Important programmer implementation rule** `[FILE …:362-395]` — the taxonomy
LOCK-01 transcribes, verbatim:

> A programmer database should not use one generic field called `locked`. It should distinguish at least:
>
> ```text
> protection_kind:
>   none
>   software_data_protection
>   sector_protection
>   block_lock
>   boot_block_lock
>   volatile_sector_bit
>   persistent_sector_bit
>   password_protection
>   lock_down
>   otp_region_lock
>
> status_readable:
>   yes
>   no
>   partial
>
> unlockability:
>   command_reversible
>   high_voltage_reversible
>   reset_reversible
>   power_cycle_reversible
>   password_reversible
>   irreversible
>   unknown
> ```
>
> A part may have several simultaneously. For example, an S29GL device can have a readable volatile DYB, a readable persistent PPB, a PPB lock state and a permanently locked OTP region. A single "locked/unlocked" result would be misleading.

That is **10 × 3 × 7** vocabulary terms across three independent axes, and the last
paragraph is an explicit warning that they are **not mutually exclusive per part**.
D-08's "single leading class token" and this taxonomy are in tension by design —
the class token is the *answer*, the taxonomy is the *table*. Worth the planner
naming that mapping explicitly.

The doc's citation apparatus: 8 footnote-style references `[1]`–`[8]`
(`:397-399` region) to Infineon, Macronix, Microchip datasheet PDFs, several
carrying `utm_source=chatgpt.com` query parameters. **Those are the "datasheet
source" half of LOCK-01's per-row citation requirement, and their provenance is
web-fetched datasheet PDFs, not in-tree files.** `[CITED: doc/lockable-proms.md's
own reference list]`

### D-03's correction — both rows quoted, and confirmed

`[FILE firestarter_app/doc/lockable-proms.md:21-22]`, §1's two relevant rows:

```
| **W29C020 / W29C020C**          |            **Yes—special** | Bottom and top 8 KB boot blocks |                                         **Yes** | Read boot-block status in Product ID mode                                                    |
| **W29C040 / W29C040P**          |          Variant-dependent | Boot blocks or SDP              |                               Variant-dependent | Must check the exact suffix and revision                                                     |
```

plus the standalone sentence at **`:30`**:

> For the **W29C020C**, the bottom and top boot-block states are explicitly readable. This device is unusual because the boot-block lockout is effectively irreversible through ordinary commands.

**D-03 verified in full.** W29C020/W29C020C is `Yes—special`, permanence `Yes`,
mechanism "Bottom and top 8 KB boot blocks", method "Read boot-block status in
**Product ID mode**". W29C040/W29C040P is `Variant-dependent` on **both** the
readability and permanence axes, with the note "Must check the exact suffix and
revision". The doc mentions `W29C020C` at `:21`, `:25`, `:30`, `:335`, `:350`
`[CMD grep -n "W29C02\|W49F002\|W29C010\|W29EE01" doc/lockable-proms.md]` — where
`:25` is §1's W49F002 row ("Replacement family for W29C020C, but not
command-identical") and `:30` is the standalone sentence quoted above.
*(Corrected 2026-08-20: an earlier revision of this document attributed the
standalone sentence to `:25` and the W49F002 row to `:30`. The two were
transposed; the line numbers above are re-measured.)*

Also note **`8 KB` boot blocks** in the W29C020C row, versus the host's
`_BOOT_BLOCK_SIZE = 0x4000` (**16 KiB**) used for the W29C040 hint. Different
parts, different geometry — not a contradiction, but a trap if a single constant
is reused.

### ⚠ Bare `W29C020` vs `W29C020C` — the document is genuinely ambiguous

**New inventory information (operator, 2026-08-20): the operator has a
`W29C020`.** That makes the question of whether `lockable-proms.md`'s readable
verdict covers the **bare** part, or only the **C** suffix, load-bearing rather
than academic. Every line in the document that bears on it, measured
`[CMD grep -n "W29C02\|W49F002\|W29C010\|W29EE01" doc/lockable-proms.md]` — there
are exactly seven:

| line | text (verbatim, trimmed) | names bare `W29C020`? |
|-----:|--------------------------|----------------------|
| **:21** | `\| **W29C020 / W29C020C** \| **Yes—special** \| Bottom and top 8 KB boot blocks \| **Yes** \| Read boot-block status in Product ID mode \|` | **YES — the row key** |
| :20 | `\| **W29C010 / W29C010M** \| Usually no for SDP \| Whole device SDP \| No \| Software Data Protection is a command-sequence requirement, not normally a readable lock bit \|` | no (sibling row, shown for the `X / Y` idiom) |
| :23 | `\| **W29EE011 / W29EE012** \| Usually no for SDP \| Whole device \| No \| EEPROM-like page-write devices \|` | no |
| :25 | `\| **W49F002 / W49F002U** \| **Yes—sector/special** \| Boot sectors \| Usually reversible … \| Replacement family for **W29C020C**, but not command-identical \|` | **no — C only** |
| **:30** | *"For the **W29C020C**, the bottom and top boot-block states are explicitly readable. This device is unusual because the boot-block lockout is effectively irreversible through ordinary commands."* | **no — C only** |
| **:335** | §Practical summary → *Families where readable lock status is normally expected*: `* Winbond **W29C020C** boot-block lock detection` | **no — C only** |
| **:350** | §Practical summary → *Families with potentially irreversible protection*: `* **W29C020C** boot-block lockout` | **no — C only** |

**So bare `W29C020` appears exactly ONCE in the entire 399-line document — in the
`:21` row key — and is absent from all four narrowing restatements.**

**The two readings, and what each rests on:**

- **Reading (a) — the verdict attaches to the ROW, i.e. to both parts.** §Key
  (`:5-14`) defines the markings as properties applied *per row*, and the row key
  is `**W29C020 / W29C020C**` with a single set of column values. §1 demonstrably
  uses the `X / Y` form for sibling suffixes that **share** a verdict — `:20`
  (`W29C010 / W29C010M` → "Usually no for SDP"), `:22` (`W29C040 / W29C040P` →
  variant-dependent), `:23` (`W29EE011 / W29EE012` → "Usually no for SDP"). On
  that internal convention, `:21` says both parts are `Yes—special`.
- **Reading (b) — the verdict attaches to the C suffix only.** Every *restatement*
  of the claim outside the table — the emphasis sentence at `:30`, and **both**
  §Practical-summary bullets at `:335` and `:350` — names `W29C020C` and only
  `W29C020C`. §Practical summary is the document's own distilled partition, and
  bare `W29C020` is in neither of its relevant lists. Its readable list also names
  other parts by bare designator ("Winbond **W49F** sector-protection families"),
  so the C suffix there is a deliberate narrowing, not a shorthand.

**Verdict: the document is genuinely ambiguous, and the ambiguity is asymmetric.**
The table covers bare `W29C020`; every narrowing restatement drops it. Nothing in
the document resolves the two readings, and no in-tree evidence does either.
**This is a finding, not a gap to paper over** — and it is exactly the edge DATA-04
polices: choosing reading (a) attributes to `lockable-proms.md` a verdict that
three of its own restatements decline to repeat, and choosing reading (b)
attributes an exclusion the table does not state.

**It also does not fit D-06's three states cleanly.** Bare `W29C020` is **not
`undocumented`** — it is in the document, at `:21`. It is "documented, with a
verdict the document's own summary declines to repeat for it". D-06's
`documented-readable` / `documented-not-readable` / `undocumented` triple has no
slot for that, and the curated table must pick one. **The planner must surface
this rather than have a curator resolve it silently — that resolution is the
adjudication D-06's rejected alternative explicitly forbids.**

### The measured fact that makes the distinction unobservable anyway

From the pinned `infoic.xml` (see §"Does `infoic.xml` Supply the Sequences? — a
clean, evidenced NEGATIVE" above, at `:1004`): **`W29C020`, `W29C020C` and
`W29C022` are ONE upstream `<ic>` entry with
ONE `chip_id`, `0x0000da45`**, one `pin_map`, one `page_size`, one `flags`. The
generated DB carries them as one row with `chip_id_value: "0x0000da45"` and
`chip_id_check: true` `[CMD python3 over chip_database.json]`.

**Consequence, and it is decisive for what any bench leg can mean:** the
programmer **cannot distinguish** a `W29C020` from a `W29C020C` from a `W29C022`.
They present the same Product-ID response. So a per-alias readability distinction
is unobservable on the wire, and a chip the operator believes is a `W29C020` is,
to the firmware, indistinguishable from the `W29C020C` the document does call
readable — and from the `W29C022` the document never mentions.

### What a `W29C020` bench leg can legitimately earn

Re-derived from the locked decisions, not assumed to flip.

**Three facts that hold regardless of the reading:**

1. **The DB entry still refuses by default.** The alias string is
   `W29C020,W29C020C,W29C022` and `W29C022` appears **nowhere** in
   `lockable-proms.md` (0 occurrences, measured). D-06's fail-closed unanimity —
   one DB entry, one answer, never token-by-token — therefore resolves this entry
   to `undocumented_alias` **even under reading (a)**. The operator's own part is
   `--force`-only under D-07, exactly like the W29C040.
2. **`--force` output is labelled `unadjudicated_probe` by D-07**, which by its own
   terms is "never a state claim".
3. **The Evidence Ceiling is untouched.** Nothing here may claim AT28C or `0x0D`
   silicon validation; `0x0D` stays `UNVERIFIED`.

**D-03's claim-cap — does it extend?** Its text is scoped: *"the W29C040 run is a
probe whose result is recorded **either way** … **No artifact may claim the `0x05`
sequence is silicon-validated on the strength of this leg.**"* Two readings, laid
out without deciding:

- **Textual/narrow:** "this leg" is the W29C040 leg. A `W29C020` leg is a
  *different* leg, on a part the table row does list as readable, so the cap does
  not textually bind it. What becomes claimable is then bounded only by what the
  leg can actually observe (below).
- **Purposive:** the cap exists *because* W29C040 is variant-dependent, i.e.
  outside the documented-readable set. Under reading (b) bare `W29C020` is also
  outside that set, so the cap's reason extends and the leg stays a probe. Under
  reading (a) the reason does not extend.

**What the leg can observe — and this is the useful decomposition, because the
three parts of the sequence are separately verifiable:**

| sub-claim | verifiable on silicon? | oracle |
|-----------|------------------------|--------|
| **(i) Product-ID mode entry/exit works on this part** | **YES** | `flash_util_get_chip_id` must return **`0xDA45`**. A correct chip-ID read *is* a positive control on the `AA/55/90` → read → `AA/55/F0` mode transition. |
| **(ii) The boot-block status ADDRESS is the right one** | **no** | there is no ground truth for "what is at that address"; a plausible-looking byte is a plausibility judgement, not a verification |
| **(iii) The `FF`/`FE` (or equivalent) DECODE is right** | **no** | requires knowing the part's actual lock state independently |
| **(iv) The part's boot block is actually locked/unlocked** | **no, not without contradiction** | the only independent oracle is write→verify, which is destructive **and** is precisely the *indirect* method `lockable-proms.md:3` excludes from the definition of "readable" |

**Sub-claim (i) is available TODAY, before a byte of new firmware exists.**
`firestarter id W29C020` already drives `CMD_CHECK_CHIP_ID` →
`configure_flash_5v_page`'s `CMD_CHECK_CHIP_ID` arm (`flash_5v_page.cpp:54-57`) →
`flash_5v_page_check_chip_id_execute` (`:133-135`) → `flash_util_check_chip_id_execute`
→ `flash_util_get_chip_id` (`flash_utils.cpp:82-87`), which issues
`FLASH_ENABLE_ID` / reads `0x0000`,`0x0001` / issues `FLASH_DISABLE_ID`. So a
zero-code bench run on the operator's `W29C020` can establish that the shared mode
machinery works on this exact part and socket, **and that result is not gated by
D-06, D-07 or D-03 at all** — it is an existing shipped command exercising existing
shipped code.

**Claimable under the narrow reading, at most:** *"the `0x05` Product-ID
boot-block status sequence was exercised on one Winbond `W29C020` sample and
returned a decodable value consistent with the datasheet's documented encoding."*
Single-sample, single-part, and the *decode* remains datasheet-asserted.

**NOT claimable under either reading:**
- that the `0x05` sequence is **validated** — sub-claims (ii)–(iv) have no oracle;
- anything about **`W29C020C`** — a different part, indistinguishable on the wire,
  which makes a family-level claim *less* supportable rather than more;
- anything about **`W29C022`**, which no source document covers;
- anything about the **`0x06` Autoselect half** — it has **no bench leg at all**,
  under D-03 or otherwise, and ships software-proven and unrun on silicon;
- anything about **AT28C or `0x0D`** — the milestone Evidence Ceiling, unchanged.

**Bench mechanics (reported, not planned — per the brief):** chip handling is
operator-only; driving the port is permitted. So the operator seats the
`W29C020`; the port run itself needs no operator step.

### The D-06 worked example, verified — and it is worse than CONTEXT.md says

The three Winbond `0x05` DB entries, measured `[CMD python3 …]`:

| vendor | `part_number` (exact string) | alg | `support_status` | `size_bytes` |
|--------|------------------------------|----:|------------------|-------------:|
| `WINBOND` | `W29C010,W29C011,W29C011A,W29EE010,W29EE012` | 5 | supported | 131072 |
| `WINBOND` | **`W29C020,W29C020C,W29C022`** | 5 | supported | 262144 |
| `WINBOND` | **`W29C040,W29C042`** | 5 | supported | 524288 |

Both entry strings match CONTEXT.md exactly ✓.

Token presence in `lockable-proms.md` `[CMD grep over the uppercased doc text]`:

| token | appears in `lockable-proms.md`? |
|-------|--------------------------------|
| `W29C020` | **yes** — `:21` (`W29C020 / W29C020C`) |
| `W29C020C` | **yes** — `:21`, `:25`, `:30`, `:335`, `:350` |
| **`W29C022`** | **NO — zero occurrences** ✓ CONTEXT.md confirmed |
| `W29C040` | **yes** — `:22` only |
| **`W29C042`** | **NO — zero occurrences** ⚠ **CONTEXT.md does not mention this** |

So under D-06:
- `W29C020,W29C020C,W29C022` → `documented-readable` + `documented-readable` +
  **`undocumented`** ⇒ refuses, naming `W29C022`. **The worked example holds
  exactly.**
- `W29C040,W29C042` → `documented-not-readable` (variant-dependent) +
  **`undocumented`** ⇒ refuses for **two** reasons. CONTEXT.md's framing assumed
  this entry refuses on W29C040's variant-dependence alone; measured, `W29C042` is
  a second, independent undocumented alias. The refusal message must handle
  **multiple** offending aliases in different states, not one. See Contradiction C-6.
- The third entry (`W29C010,…,W29EE012`) contains `W29EE010`/`W29EE012`
  (`:19`, "Usually no for SDP") and `W29C010` (`:20`, "Usually no for SDP") but
  `W29C011`/`W29C011A` appear nowhere → also mixed.

### The seed and the negative-result note

`[FILE .planning/seeds/lock-status-command-hand-curated-protection-table.md]`, 74
lines, `trigger_condition: "post-v1.21 milestone selection"`, planted 2026-07-10.
It carries the two-axis scope shape verbatim:

> 1. **Database axis** — hand-curated protection table for chips in chip_database.json. Small: the RURP-reachable set collapses to ~3 command-set families.
> 2. **Firmware axis** — per-family query sequences:
>    - **AMD Autoselect** (`AA-55-90`, read sector addr → 00h/01h): Am29F, SST/W49F/MX29F/M29F/AT49F classes — covers most bench-validated flash.
>    - **Winbond Product-ID mode boot-block status**: W29C020C/W29C040 — the family behind the v1.17 locked-boot-block RCA …
>    - **SDP-only families** (AT29C, AT28C, W29EE, X28C, SST39SF): no readable state → the command must return "not readable on this family", never garbage.

Two notes on the seed against the measurements above: (i) its *"the RURP-reachable
set collapses to ~3 command-set families"* is optimistic — the curated surface is
**217 entries / 273 tokens** on 2 algorithms, and the doc's 126 rows span 18
vendor families; (ii) it names the **`AA-55-90` → read sector addr → `00h`/`01h`**
shape, which agrees with `lockable-proms.md:34-40` and is the closest thing to a
sequence spec in the planning tree — but still **not** the `SA + 0x02` offset.

The seed's payoff list is what the deferred `dev test` integration would deliver,
and it explicitly names the v1.17 short-circuit — consistent with CONTEXT.md
§`<specifics>`.

`.planning/notes/infoic-xml-protection-flags-research.md` (110 lines) — the
2026-07-29 scoped-exception tail is quoted in §"DATA-06's Documentation Home"
above. **Do not re-investigate.**

---

## Test / CI Environment Facts (Priority 8)

### `firestarter_app` — the host test environment

`[FILE firestarter_app/.github/workflows/ci.yml]`, job `ci`, in order:

| step | command | line |
|------|---------|-----:|
| Python | `actions/setup-python@v5` with `python-version: '3.11'` — **3.11 ONLY, no matrix** | :47-50 |
| Catalog validity | `python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check` | :52-53 |
| Codegen drift (messages.py) | regenerate then `git diff --exit-code firestarter/messages.py` | :55-61 |
| Vector catalog validity | `python3 tools/catalog/codegen_vectors.py --catalog tools/catalog/frame-vectors.toml --check` | :63-64 |
| Codegen drift (frame_vectors.py) | regenerate then `git diff --exit-code firestarter/frame_vectors.py` | :66-72 |
| **Install** | **`pip install -e .[test]`** | :74-75 |
| ruff lint | **`ruff check firestarter/ tests/`** | :77-78 |
| ruff format | **`ruff format --check firestarter/ tests/`** | :80-81 |
| mypy | **`python tools/check_mypy_watermark.py`** | :83-84 |
| pytest | **`pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70`** | :86-87 |
| smoke | `pip install -e . && firestarter --help` | :89-94 |

Second job `ci-py32` (`:96-131`) installs `.[test,py32]`, proves pyusb imports,
and runs only `pytest tests/test_pyusb_api_surface.py -q`. It runs **no** ruff,
format, mypy, coverage or codegen step, deliberately.

Triggers: `push` on `branches: ['**']` (every branch; `'**'` matches branches but
**no tags**, so a milestone-close tag push fires zero CI), `pull_request`, and
`workflow_dispatch`; `paths-ignore` excludes `**.md`, `.gitignore`, `docs/**`,
`.vscode/**`, `.editorconfig`. **⚠ `paths-ignore` excludes `**.md` — so a
markdown-only change (i.e. a DATA-06 documentation-only commit) fires NO CI.**
Note the ignore list names `docs/**` (lowercase, plural) while the actual docs
directory is `doc/` — `**.md` covers it anyway.

**Install extra:** `.[test]` = `pytest>=8.0`, `syrupy>=5.0`, `ruff>=0.15.14`,
`mypy>=2.1.0,<3`, `pytest-cov>=7.1.0`, `types-pyserial>=3.5.0.20260519`
`[FILE firestarter_app/pyproject.toml:71-86]`. There is also a separate, much
smaller `dev` extra (`pytest>=7.0` only, `:58-60`) — **do not use `.[dev]`**; it is
the documented near-miss.

**`addopts` and the count line.** `[FILE firestarter_app/pyproject.toml:105-107]`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra -q"
```

`-q` is already applied. Adding another `-q` on the command line reaches `-qq` and
**suppresses the pass/fail count line entirely** — so a verification step that
greps for "N passed" must either not pass `-q`, or use `-o addopts=""` to reset.

**mypy gate scope — the trap.** `tools/check_mypy_watermark.py` builds its command
as `[sys.executable, "-m", "mypy", "firestarter/", "tests/"]`
`[FILE firestarter_app/tools/check_mypy_watermark.py:115]`. So the gate's scope is
**`firestarter/` AND `tests/`**, not `firestarter/` alone. A raw `mypy firestarter/`
is a **different, narrower scope** and can print clean while the gate is red.
Other gate parameters:
- `mypy_error_watermark = 35`, read by regex from a **comment** in `pyproject.toml`
  `[FILE firestarter_app/pyproject.toml:174]`; the checker fails if that comment is
  absent (`:96-100`).
- `MIN_CHECKED_SOURCE_FILES = 120` (`:48`) — a coverage floor; a run reporting
  fewer checked files exits 2 (`:195-198`).
- `[tool.mypy] python_version = "3.10"` (`:155`), `ignore_missing_imports = true`,
  `disallow_untyped_defs = false`, `check_untyped_defs = false`,
  `exclude = ["^tests/fixtures/"]` (`:170`).

**ruff's select list — and what it means for `except` clauses.**
`[FILE firestarter_app/pyproject.toml:123-132]`:

```toml
[tool.ruff.lint]
select = ["E", "F", "I", "UP"]
extend-ignore = ["E501"]
```

with `target-version = "py39"` (`:110`), `line-length = 88` (`:111`) and
`extend-exclude = ["tests/golden", "tests/fixtures"]` (`:121`).

**`BLE001` is not in the select list, so every `# noqa: BLE001` in this repo is
inert** — confirmed, and there are **10 of them**
`[CMD grep -rn "noqa: BLE001" firestarter/ tests/ tools/ | wc -l]`. Consequence
for this phase: a `except Exception:` clause added anywhere in the new code is
gated by **nothing** — not ruff, not the mypy watermark. If the new predicate or
CLI command needs a broad handler, its narrowness has to be enforced by a test or
by the new invariant gate (note `check_sdp_capability_invariants.py`'s Class 1(b)
already denies a **bare** `except:` in its target file — but not `except
Exception:`).

**Python version drift.** The devcontainer's `python3` is **3.12.13**
`[CMD python3 --version]` while CI is **3.11 only**. Anything that behaves
differently across those two (dict ordering is fine; `tomllib` is fine on both;
deprecation warnings are not) will pass locally and can fail in CI. Coverage floor
is `--cov-fail-under=70` over `firestarter/` — a new module with no tests lowers it.

### `firestarter` — the firmware test environment

**PlatformIO envs** `[CMD grep -n "^\[env" firestarter/platformio.ini]`: `[env]`
(`:18`), `[env:uno]` (`:33`), `[env:uno328pb]` (`:48`), `[env:leonardo]` (`:77`),
`[env:native]` (`:97`), `[env:native_nodevtools]` (`:194`),
`[env:native_pinmap_provisional]` (`:283`), `[env:native_trace_v131]` (`:321`),
`[env:native_params_v131]` (`:359`), `[env:native_loop_v131]` (`:401`) — **10 envs,
6 of them native.**

**`-D DEV_TOOLS` is at `platformio.ini:26`, inside `[env]`'s `build_flags`
(`:21`)** ✓ exactly as CONTEXT.md states, alongside `-D MONITOR_SPEED=…` and
`-D HARDWARE_REVISION`. It is inherited by `uno` (`:38`), `uno328pb` (`:61`) and
`leonardo` (`:82`), each of which spells `${env.build_flags}` first. `[env:native]`
also inherits it (`:148-149`); `[env:native_nodevtools]` deliberately does **not**
(`:214-216`: *"build_flags does NOT start with ${env.build_flags} — it spells out
… OMITS -D DEV_TOOLS"*). **So there is no `#ifdef` that makes new firmware code
free on any shipped AVR target** — D-01's cost statement verified.

**Which suites run in which CI leg** `[CMD grep -n "native" firestarter/.github/workflows/*.yml]`:

- `build.yml:142` → `pio test -e native`; `build.yml:155` → `pio test -e native_nodevtools`; `build.yml:193` → `pio run` (all AVR envs).
- `beta-build.yml:122` → `pio test -e native`; `:128` → `pio test -e native_nodevtools`; `:145` → `pio run`.
- **No workflow invokes any other native env.**

`test_filter` sizes `[CMD python3 … regex over platformio.ini]`: `native` 17
suites, `native_nodevtools` 17 (pinned identical — the comment at `:220-226`
records this is deliberate: *"the -I list are each the FULL 17-entry list"* and
that the count is live-gated), `native_pinmap_provisional` 1,
`native_trace_v131` 1, `native_params_v131` 1, `native_loop_v131` 2.

**Suites that run in NO CI leg — six, measured** `[CMD python3 … set difference of on-disk suite dirs vs native+native_nodevtools test_filters]`:

| suite | env that names it | in CI? |
|-------|-------------------|--------|
| `test_pinmap_provisional` | `native_pinmap_provisional` | ✗ |
| `test_trace_eprom_v131` | `native_trace_v131` | ✗ |
| `test_eprom_params_v131` | `native_params_v131` | ✗ |
| `test_loop_eprom_v131` | `native_loop_v131` | ✗ |
| `test_vpp_eprom_v131` | `native_loop_v131` (its 2nd entry) | ✗ |
| **`test_flash_intel_vpp`** | **NO `test_filter` names it at all** | ✗ — never runs anywhere via `pio test` |

That is **six** suites outside CI, not two. Directly relevant: **`test_pinmap_provisional`
is one of the six**, and it is exactly the suite whose 8 per-command cases must
become 9 if a new memory command lands. So that mirror-site edit is **unverified by
CI** and needs an explicit local-run step in the plan.

**Warning watermarks — zero headroom.** `[FILE firestarter/scripts/baseline/size_baseline.json]`
`warnings` block:

| env | `macro_redefinition` | `total_watermark` |
|-----|---------------------:|------------------:|
| `uno` / `uno328pb` / `leonardo` | 0 | **0** (policy `avr_rule: "== 0"`) |
| `native` | 1166 | **1166** |
| `native_nodevtools` | 1166 | **1166** |
| `native_pinmap_provisional` | 138 | **138** |

`policy.native_rule: "<= total_watermark"`, and `check_build_warnings.py`'s arms
`[FILE firestarter/scripts/check_build_warnings.py:164-178]`: `total_count >
watermark` → **FAIL**; `total_count < watermark` → **INFO** (not a failure, "lower
the watermark"); `==` → OK. The recorded figures are **COLD** measurements; warm
figures are `native=998`, `native_nodevtools=998`,
`native_pinmap_provisional=0`, and the note explains the asymmetry exists because
*"CI always builds cold"*.

**Consequences:** (a) on AVR the rule is **exact zero** — a single new compiler
warning on any of the three targets fails; (b) on native the headroom above the
cold figure is **zero** — a new native translation unit that includes
`include/rurp_platform_compat.h` and links against ArduinoFake's `pgmspace.h`
adds macro-redefinition warnings and pushes past 1166. The mechanism is documented
in the baseline's own note: *"include/rurp_platform_compat.h (landed by Plan
124-04) now defines program-memory macros that ArduinoFake's own pgmspace.h
redefines, across six more macro names and roughly 27 more translation units than
BASE-01 characterised"*. Counting command, recorded:
`pio test -e <env> 2>&1 | grep -cE 'warning: *"[^"]+" +redefined'`.

**The `cases`/`suites` baseline — a new native suite reddens it.**
`size_baseline.json`'s `native_envs` records `native: {cases: 151, succeeded: 151,
suites: 17, all_passed: true}`, same for `native_nodevtools`, and
`native_pinmap_provisional: {cases: 10, succeeded: 10, suites: 1}`.
`compare_native` asserts **all three** facts — cases equal, suites equal, and every
suite `PASSED` `[FILE firestarter/scripts/check_size_baseline.py:512-534]`, with a
docstring warning that asserting only the count *"reproduces this project's own
'assert counts, never tests pass' anti-pattern in mirror image"*. So adding a
firmware native suite means: two `test_filter` lists 17→18, `cases` 151→151+N in
both native envs, a re-record of `size_baseline.json`, and
`test_clean_native_both_envs_pass` (`:347`) severed onto new
`captured_test_native{,_nodevtools}_summary.log` fixtures. **Adding cases to an
existing suite has the same `cases` consequence without the `suites` one.**

Firmware host-side checkers, for completeness `[CMD ls firestarter/scripts]`:
`check_build_warnings.py`, `check_cmake_manifest.py`, `check_landing_range.py`,
`check_orphan_provisional.py`, `check_release_assets.py`, `check_size_baseline.py`.
Firmware `tests/` (pytest, 33 modules) includes `test_checker_convention.py`, which
enumerates the checker family and its mandatory anti-hollow pairing — a **new
firmware checker would have to satisfy it**; this phase should not need one.

### Host-side gates that scan FIRMWARE source — the full inventory

These have broken on firmware renames before and they **fail OPEN**. The single
committed inventory is `firestarter_app/tests/scan_paths.py` (D-11 / BASE-02,
Phase 123 Plan 08). Measured contents:

**`CROSS_REPO_TEST_PATHS` — 8 entries** (firmware-repo-relative → resolving test
module):

| firmware path | resolved by |
|---------------|-------------|
| `include/firestarter.h` | `test_revision_constants_parity.py`, `test_check_is_memory_cmd_no_ifdef.py` |
| `src/proms/eeprom_28c.cpp` | `test_check_no_log_in_sdp_window.py`, `test_sdp_table_parity.py` |
| `doc/PROTOCOLS.md` | `test_dispatch_mirror.py` |
| `test/native/avr/test_dispatch/test_configure_memory.cpp` | `test_dispatch_mirror.py` |
| `test/native/avr/_shared/sdp_bus_config.h` | `test_sdp_bus_config_drift.py` |
| `test/native/avr/_shared/validation_matrix.h` | `test_gen_validation_header.py` |
| `src/firestarter.cpp` | `test_cap03_ack_layout_parity.py` |
| `src/json_parser.c` | `test_json_key_parity.py` |

**`CROSS_REPO_TOOL_RESOLVERS` — 11 entries, with a hard assertion**
`assert len(CROSS_REPO_TOOL_RESOLVERS) == 11`. Only **4 of the 11** are genuinely
cross-repo (`gen_validation_header.py`, `check_no_log_in_sdp_window.py`,
`check_is_memory_cmd_no_ifdef.py`, `gen_sdp_bus_config.py`) — the other 7 build
their path with **one** `..` from `tools/` and land in the app's *own* package.
That trap is documented at length in the module docstring and recorded in
`SAME_REPO_LOOKALIKES` (8 entries). `ALL_CROSS_REPO_PATHS` is the dedup union =
**the same 8 paths** as population A.

**What this phase must do to that inventory:**
- If the new firmware work touches only `include/firestarter.h`,
  `src/firestarter.cpp`, `src/proms/flash_nor_unlock.cpp` and
  `src/proms/flash_5v_page.cpp`: the first two are **already listed**; the two
  `proms/*.cpp` files are **not**, and only need adding **if a host gate scans
  them**. No existing host gate does.
- If a **new** host gate is written that scans a firmware file (e.g. to assert the
  new `CMD_*` is present in both repos), that file must be added to
  `CROSS_REPO_TEST_PATHS` and, if a `tools/*.py` resolves it, the `== 11`
  assertion must be updated in the same change.
- `tests/fw_presence.py` provides `FW_ROOT`; `tests/test_scan_paths_resolve.py` is
  the leg that turns a rename into **one named failure** instead of N anonymous
  skips.
- Fail-open remains real: `test_revision_constants_parity.py` is `skipif`-guarded
  on firmware presence, and the devcontainer sibling layout masks it. Before a
  beta push, point the sibling root at an empty dir to see the skips.

---

## Validation Architecture

`.planning/config.json` `[FILE]` has `workflow: {_auto_chain_active, research,
plan_check, verifier, code_review}` and **no `nyquist_validation` key** — absent
means enabled, so this section is required.

### Test Framework

**Two frameworks, because this is a dual-repo phase.**

| Property | Host (`firestarter_app/`) | Firmware (`firestarter/`) |
|----------|---------------------------|---------------------------|
| Framework | pytest 8+ (`+ syrupy>=5.0`, `pytest-cov>=7.1.0`) | PlatformIO + Unity (native), plus pytest for `scripts/` checkers |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` (`:105-107`) — `testpaths=["tests"]`, `addopts="-ra -q"` | `platformio.ini` (`test_filter` per env); firmware `tests/` has no separate pytest config |
| Quick run command | `python3 -m pytest tests/test_<module>.py -x -o addopts=""` | `python3 -m pytest tests/test_check_size_baseline.py -x` (from `firestarter/`) |
| Full suite command | `python3 -m pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70` | `pio test -e native && pio test -e native_nodevtools` (+ `pio test -e native_pinmap_provisional` — **not in CI**) |
| Install | `pip install -e '.[test]'` (**never `.[dev]`**) | PlatformIO toolchain already present |
| Trap | devcontainer python is 3.12, CI is 3.11 only; `-q` already in addopts | ArduinoFake macro-redefinition watermark 1166 with **zero** headroom |

### Phase Requirements → Test Map

| Req | Behavior to prove | Test type | Automated command | File exists? |
|-----|-------------------|-----------|-------------------|--------------|
| **LOCK-01** | The curated table's binding shape cannot be widened into inference (literal-only, bound once, no mutation) | source-scan gate (AST) driven as a **subprocess** | `python3 -m pytest tests/test_check_<table>_invariants.py -x -o addopts=""` | ❌ Wave 0 — model on `tests/test_check_sdp_capability.py` (9 legs) + `tools/check_sdp_capability_invariants.py` |
| **LOCK-01** | Every row with a readable verdict carries a `lockable-proms.md` **and** datasheet citation | unit over the module's own AST/comments | same suite, dedicated leg | ❌ Wave 0 |
| **LOCK-01** | Every curated token maps to a family row that actually exists in `doc/lockable-proms.md` | invariant-over-doc (parse the 126 rows, assert the cited row string is present) | `python3 -m pytest tests/test_<table>_citations.py -x` | ❌ Wave 0 — closest precedent `tests/test_lockable_proms_doc_claims.py` (4 legs, `:63`/`:85`/`:114`/`:129`) |
| **LOCK-02** | Host builds the right wire frame for the new command, and parses its response | unit (frame-level, no serial) | `python3 -m pytest tests/test_<lockstatus>_wire.py -x` | ❌ Wave 0 |
| **LOCK-02** | `CMD_*` ↔ `COMMAND_*` parity + `COMMAND_NAMES` key | existing bidirectional parity gate | `python3 -m pytest tests/test_revision_constants_parity.py -x` | ✅ exists — **fails OPEN without the sibling repo** |
| **LOCK-02** | `is_memory_cmd()` admits exactly the intended set, over the full `[0,255]` domain, in **both** DEV_TOOLS states | firmware-native truth table | `pio test -e native -f "*test_cmd_admission*"` and `pio test -e native_nodevtools -f "*test_cmd_admission*"` | ✅ exists (`test_cmd_admission.cpp:66`) — literal set `{1,2,3,4,5,6,9,10}` must change |
| **LOCK-02** | `_EXPECTED_CMD_NAMES` deliberately updated, not drifted | host source-scan gate | `python3 -m pytest tests/test_check_is_memory_cmd_no_ifdef.py -x` | ✅ exists |
| **LOCK-02** | The provisional-pinmap refusal still covers every memory command | firmware-native | `pio test -e native_pinmap_provisional` | ✅ exists — **runs in NO CI leg** |
| **LOCK-02** | Firmware flash/RAM growth stays inside the (newly extended) MERGE-05 allowance, and the tripwire still fires one byte past it | firmware pytest over cold build logs | `python3 -m pytest tests/test_check_size_baseline.py -x` then `python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json --avr-log …` | ✅ exists, 14 legs — 8 of them redden (see §Priority 1) |
| **LOCK-03** | An entry with any non-`documented-readable` alias refuses, **naming that alias and its state** | unit, table-driven | `python3 -m pytest tests/test_<table>_resolution.py -x` | ❌ Wave 0 |
| **LOCK-03** | `W29C020,W29C020C,W29C022` refuses naming **`W29C022`** specifically (D-06's own acceptance condition) | unit, one named leg | same suite | ❌ Wave 0 |
| **LOCK-03** | Pre-command firmware ⇒ `firmware_outdated`, keyed on `MSG_ERR_UNKNOWN_CMD` **id**, with a negative control on a different id | unit (constructed exception in, constructed exception out — mock-free) | `python3 -m pytest tests/test_sdp_honesty.py -x` (+ new sibling legs) | ✅ exists (`:125-150`) — extend, do not rewrite |
| **LOCK-03** | The `not_readable` caveat is **composed**, never re-authored | unit substring assertion | `python3 -m pytest tests/test_sdp_honesty.py tests/test_chip_test_sdp_leg.py -k caveat -x` | ✅ exists |
| **LOCK-04** | **All 746 DB entries resolve to exactly one of the 8 classes** — exhaustive, no row in zero classes, no row in two | **invariant-over-DB** | `python3 -m pytest tests/test_<lockstatus>_class_partition.py -x` | ❌ Wave 0 — **the D-12 test** |
| **LOCK-04** | `protected` / `unprotected` are **structurally unreachable** without a silicon read | AST/structural gate over the resolution module | same suite, or the LOCK-01 gate's Class 1 analogue | ❌ Wave 0 |
| **LOCK-04** | Class token **and** exit code asserted together, per class | CLI-surface (Click runner or subprocess) | `python3 -m pytest tests/test_<lockstatus>_cli.py -x` | ❌ Wave 0 |
| **LOCK-04** | `dev lock-status` is absent on a simulated stable build and refuses informatively | CLI-surface, real child process per simulated version | `python3 -m pytest tests/test_dev_group_channel_gating.py -x` | ✅ exists — `_GATED_NAMES` 6→7 |
| **LOCK-04** | `BETA_ONLY_DEV_COMMANDS` deliberately extended | unit exact-tuple | `python3 -m pytest tests/test_dev_tools_channel_gate.py -x` | ✅ exists — 6-tuple → 7-tuple at `:150-158` |
| **LOCK-04** | `dev --help` renders the new command (and nothing else changed) | **syrupy snapshot** | `python3 -m pytest tests/test_characterization.py -k help_dev -x` (regen: `--snapshot-update`) | ✅ exists — `test_help_dev`, snapshot at `.ambr:124-150` |
| **DATA-06** | The measured figures in the doc equal the DB (70/746; alg 5 → 27/27; alg 13 → 43; 148/746; 27/77/43/1; 744 of 746 carry the fields) | **invariant-over-DB**, doc-parsing | `python3 -m pytest tests/test_<data06>_doc_measurements.py -x` | ❌ Wave 0 — model on `tests/test_b15_page_size_corroboration.py` |
| **DATA-06** | **No runtime consumer exists** in `firestarter/` | source-scan **test** (not a `tools/check_*`, per D-16) | same suite | ❌ Wave 0 |
| **DATA-06** | Documented **once**: exactly one authoritative statement, two one-line pointers | doc-parsing unit over the three files | same suite | ❌ Wave 0 |
| **DATA-06** | `sdp_capability.py` untouched; Class 2(b) gate not weakened | "module untouched" guard + the existing gate | `python3 -m pytest tests/test_check_sdp_capability.py -x` + a new untouched-guard leg | ✅ gate exists; guard shape exists at `test_b15_page_size_corroboration.py:246` |

### The D-12 invariant test — exact shape

This is the load-bearing test and it is worth specifying precisely, because three
distinct traps are already measurable in the tree:

**It must test the mechanism, not the prose.** Drive the *resolution function*
(`(entry, display_name) -> (class_token, reason)`) over every row of the committed
`chip_database.json`, and assert on **class tokens**, never on message text.

**Assertions, in order:**

1. **Exhaustiveness.** For all 746 rows, the resolved token is in the frozen
   8-token set. **The negative control is real and already exists**: the
   `XICOR/X88C64P,X88C64S` row (`algorithm: 52`) lands in **no** class under D-09's
   literal enumeration. This leg goes red today unless `0x34` is given a class —
   which means the leg is **not vacuous from the first commit**, and that is the
   whole point.
2. **Disjointness / determinism.** Each row resolves to exactly one token, and
   twice in a row (the function is pure).
3. **Per-class census, pinned as literals.** Using the algorithm-derivable classes
   measured above: `not_implemented` = 39 (`0x10`), `no_mechanism` = 405
   (`0x07`+`0x08`+`0x0B`+`0x0E`+`0x27`+`0x28`+`0x29`), `not_readable` ⊇ 84
   (`0x0D`), and the 217 `0x05`+`0x06` rows distributed between
   `documented-readable`-derived answers, `not_readable` and `undocumented_alias`.
   **Pin the census as literals** and let a new DB row break it — the
   `test_sdp_db_invariant.py` legs pin `43`/`41`/`84` in exactly this style.
4. **Structural unreachability of `protected`/`unprotected`.** Assert that a
   resolution performed **without** a firmware response can never return either
   token, for any of the 746 rows. The strongest form is a **pure-function**
   assertion: the resolution function's signature does not accept a device
   response at all, so `protected`/`unprotected` are produced only by a second,
   response-consuming function — and an AST leg asserts the string literals
   `"protected"` / `"unprotected"` do not appear as return values in the pure
   module. Class 1(a)'s "return dominated by a membership test" walk in
   `check_sdp_capability_invariants.py:19-31` is the working precedent for the AST
   shape.
5. **Citation presence.** Every token whose class is `documented-readable` has a
   citation comment in the table module, and the cited `lockable-proms.md` row
   string is actually present in that file.
6. **Robustness legs the tree demands:** a row whose `programming` dict lacks
   `protect_on_after`/`protect_off_before` (the two TI rows) must not raise; a row
   whose `support_status != "supported"` (10 rows) must still resolve to a class
   even though `resolve_chip` would refuse it; and a **synthetic** DB row with a
   novel algorithm must make the exhaustiveness leg **raise**, naming the row —
   the non-vacuous control, copied from
   `test_partition_flags_a_moved_chip_via_db_field_non_vacuous`.

**Why not a phase-local checker:** D-12 already rules it out, and the reason is
measured — `check_permitted_claims.py`'s `_HERE` resolves to the *checking* phase's
own directory, so cross-phase reuse scans nothing and exits 0. A pytest module
under `tests/` has no such failure mode.

### Software-provable vs bench-only

**Provable in software (all of it, and it is most of the phase):**
- the curated table's shape, its citations, and its non-widenability;
- every class resolution over all 746 rows;
- the refusal messages naming the offending alias;
- the class-token ↔ exit-code contract;
- channel gating on both simulated channels;
- the `CMD_*`/`COMMAND_*` parity and the `is_memory_cmd` truth table;
- firmware flash/RAM growth against MERGE-05;
- **the firmware sequences' host-visible framing**, via `test_val_wire_*`-style
  catalog/wire tests and the native Unity `test_val_5v_page` / `test_val_nor_unlock`
  suites (both already in the 17-entry `test_filter`);
- every DATA-06 measurement.

**⚠ Provable in software but NOT provable at all — the sequence bytes
themselves.** Now that `infoic.xml` is closed as a source (see §"Does
`infoic.xml` Supply the Sequences?"), both the `0x05` and `0x06` sequences are
**datasheet-derived**, and that caps what any test can do:

| source | strongest available test | what it detects |
|--------|--------------------------|-----------------|
| infoic-derived (**not available here**) | element-wise proof against a freshly-loaded `infoic.xml`, in the style of `test_sdp_partition_matches_infoic_derived_field_element_wise` (`:584-621`) + a synthetic-mutation non-vacuous control | drift **and** error |
| **datasheet-derived (what this phase has)** | a literal pinned byte table + a `vendor / document / revision / page / §section` citation comment, and a test asserting the table is unchanged | **edits only — never errors** |

So a criterion of the form "the sequence is correct" is **unsatisfiable by any
test in this phase**. The satisfiable form is "the sequence bytes are pinned as a
literal table with a full citation, and a test fires on any edit" — a **change
detector, not a correctness proof** — and the plan must say so in those words.

**Bench legs — TWO parts now, and they are asymmetric.**
*(Revised 2026-08-20: the operator has a `W29C020`. The earlier single-part
framing, and this section's earlier claim that the `0x05` payoff chain was empty,
are superseded.)*

| leg | part | reachable via | status |
|-----|------|---------------|--------|
| **A — mode-entry positive control** | `W29C020` | **`firestarter id W29C020`, an existing shipped command** | **available today, zero new code.** `CMD_CHECK_CHIP_ID` → `configure_flash_5v_page`'s `CMD_CHECK_CHIP_ID` arm (`flash_5v_page.cpp:54-57`) → `flash_util_get_chip_id` (`flash_utils.cpp:82-87`) must return **`0xDA45`**. Not gated by D-03, D-06 or D-07. |
| **B — the `0x05` status read** | `W29C020` | `dev lock-status W29C020 **--force**` (D-07) — `--force` is required **even on the operator's own part**, because `W29C022` is undocumented and D-06's unanimity refuses the entry regardless of how C-17 is resolved | a **PROBE**; see the two claim-cap readings below |
| **C — the original D-03 leg** | `W29C040` | same `--force` path | a **PROBE**, explicitly capped by D-03 |
| **D — the `0x06` Autoselect read** | *none* | — | **no bench leg exists, under D-03 or otherwise** |

**What leg B can and cannot establish — the decomposition is the useful part:**

| sub-claim | on silicon? | oracle |
|-----------|-------------|--------|
| (i) Product-ID mode entry/exit works on this part | **YES** | chip-ID reads back `0xDA45` — that *is* a positive control on `AA/55/90` → read → `AA/55/F0`. Available via leg A. |
| (ii) the status **address** is the right one | **no** | no ground truth for what is at that address |
| (iii) the `FF`/`FE` **decode** is right | **no** | requires knowing the part's true lock state independently |
| (iv) the part's boot block **is** locked | **no, not without self-contradiction** | the only independent oracle is write→verify, which is destructive **and** is the *indirect* method `lockable-proms.md:3` excludes from the definition of "readable" |

**The discipline this imposes on the plan, restated from D-03 and extended:** every
probe result is recorded **either way**. On leg C (W29C040) D-03's cap binds
directly: **no artifact may state that the `0x05` sequence is silicon-validated on
the strength of that leg.** On leg B (W29C020) the cap's reach is genuinely open —
textually it is scoped to "this leg" (the W29C040 run) and does not bind a
different part the `:21` row does list as readable; purposively it exists because
W29C040 is variant-dependent, a reason that extends to bare `W29C020` only under
C-17's reading (b). **Both readings are laid out in §"What a `W29C020` bench leg
can legitimately earn"; this research does not choose between them.**

**What no bench leg earns, under any reading:**
- sub-claims (ii)–(iv) — so **never** "the `0x05` sequence is validated";
- anything about **`W29C020C`** or **`W29C022`** — one `<ic>`, one
  `chip_id 0x0000da45`, indistinguishable on the wire (C-18), which makes a
  family-level claim from a single part *less* supportable, not more;
- anything about the **`0x06` Autoselect half** — leg D does not exist, so
  `lock-status` on a `0x06` part ships **software-proven and unrun on silicon**,
  and must say so in those words;
- anything about **AT28C or `0x0D`** — the milestone Evidence Ceiling, unchanged
  and untouched by any of this;
- **closure of the v1.17 W29C040 RCA** — that RCA asked for a **second W29C040
  sample**, and a `W29C020` is a different part. The payoff CONTEXT.md
  §`<specifics>` funded these bytes for is now **partially** reachable, not
  delivered.

**Bench mechanics (reported, not planned):** chip handling is operator-only;
driving the port is permitted.

### Sampling Rate

- **Per task commit (host):** the one or two suites the task touches, e.g.
  `python3 -m pytest tests/test_<module>.py -x -o addopts=""`.
- **Per task commit (firmware):** `pio test -e native -f "*<suite>*"` for the
  touched suite, plus `python3 -m pytest tests/test_check_size_baseline.py -x` on
  any task that changes firmware bytes.
- **Per wave merge (host):** `python3 -m pytest tests/ -o addopts="-ra"` (full, with
  the count line visible), then `ruff check firestarter/ tests/` +
  `ruff format --check firestarter/ tests/` + `python tools/check_mypy_watermark.py`.
- **Per wave merge (firmware):** `pio test -e native` **and**
  `pio test -e native_nodevtools` **and** `pio test -e native_pinmap_provisional`
  (the last is not in CI and must be run by hand), plus a cold
  `rm -rf .pio/build/<env>` + `pio run -e <env>` per AVR env on the wave that lands
  the firmware bytes.
- **Phase gate:** host full suite green at `--cov-fail-under=70`; firmware
  `check_size_baseline.py --policy merge05` exit 0 against BASE-01 on all three
  AVR targets with the decomposition visible in the PASS line;
  `check_build_warnings.py` OK (AVR `== 0`, native `<= 1166`); then
  `/gsd-verify-work`.
- **Note on the codegen path:** if `messages.toml` is edited, the app's CI drift
  gate (`git diff --exit-code firestarter/messages.py`) is the automated proof the
  regen ran; the firmware side has no equivalent drift gate, so
  `include/messages.h` must be regenerated and committed in the same change.

### Wave 0 Gaps

- [ ] `firestarter_app/firestarter/<protection_table>.py` — the LOCK-01 module (new)
- [ ] `firestarter_app/tools/check_<protection_table>_invariants.py` — LOCK-01's AST gate (new)
- [ ] `firestarter_app/tests/test_check_<protection_table>.py` — subprocess-driven pairing, ≥1 planted fixture per violation class (new)
- [ ] `firestarter_app/tests/fixtures/planted_<table>_permit_by_default.py` and `…_widenable.py` — real planted violations (new)
- [ ] `firestarter_app/tests/test_<lockstatus>_class_partition.py` — **the D-12 invariant** (new)
- [ ] `firestarter_app/tests/test_<lockstatus>_resolution.py` — three-state unanimity + the `W29C022` named leg (new)
- [ ] `firestarter_app/tests/test_<lockstatus>_cli.py` — class-token ⊗ exit-code matrix, `--force` path (new)
- [ ] `firestarter_app/tests/test_<lockstatus>_wire.py` — the new command's frame build + response parse (new)
- [ ] `firestarter_app/tests/test_<data06>_doc_measurements.py` — DATA-06's measured proof + consumer-absence (new)
- [ ] **Re-derived** planted fixtures for the moved MERGE-05 band, on a **new** family (e.g. `*_v151*`), for the four tripwire legs + the four clean-control legs — **never** by editing the `fullflash` family in place
- [ ] **Re-captured** `captured_build_*` and `captured_test_native*_summary` fixtures from the post-151 cold build
- [ ] Snapshot regeneration for `test_help_dev` (`pytest tests/test_characterization.py -k help_dev --snapshot-update`)
- [ ] Framework install: **none needed** — pytest 8 + syrupy + PlatformIO are all present.

### Where a criterion risks being UNREACHABLE or VACUOUS

Named explicitly, because the prior-phase lesson is that **RED proves nothing until
the leg is seen to pass**, and a pre-authored gate leg can be unreachable:

1. **The D-12 exhaustiveness leg is red-by-construction today** (the `0x34` row).
   That is good — but the plan must *observe it pass* after the class decision
   lands, not assume it. Write the acceptance as "seen red on the `0x34` row, then
   seen green after the class is assigned", not "leg exists".
2. **The `protected`/`unprotected` unreachability leg is the easiest one to author
   vacuously.** An assertion like "the string `protected` does not appear in the
   pure module" passes trivially if the module was never going to contain it. The
   non-vacuous form is a **planted** violation: a fixture module that *does* return
   `"unprotected"` from the pure path, fed through the gate's env seam, asserted to
   fail. Without that fixture the leg is decorative.
3. **A `0x05` bench-probe criterion is unreachable as validation, by decision.**
   Any acceptance criterion phrased "the `0x05` read returns the correct status" is
   unsatisfiable within D-03. The satisfiable form is "the probe was run and its
   raw result recorded, either way, with no validation claim attached".
4. **`test_revision_constants_parity.py` fails OPEN** without the sibling repo, so
   "parity gate green" is a vacuous criterion in a worktree with empty submodules.
   The non-vacuous form names `commits_land_in:` and requires the gate to have been
   observed **not** skipped (the `-rs` skip report, or `tests/fw_presence.py`'s
   `FW_ROOT` resolving).
5. **`test_pinmap_provisional` runs in no CI leg**, so a green CI is not evidence
   that its 9th case passes. The criterion must name the local
   `pio test -e native_pinmap_provisional` invocation.
6. **A markdown-only DATA-06 commit fires no CI at all** (`paths-ignore: ['**.md']`).
   So "CI green" is vacuous evidence for the documentation half; the DATA-06 proof
   must be a **Python test** (which is not markdown) so that it actually runs.
7. **Do not write "fixtures byte-unchanged" or "tests byte-unchanged"** as a
   criterion anywhere in this phase. The a7w and 149-07 severances are the in-tree
   record of why; scope to *assertions-unchanged*, or name blob SHAs.
8. **"The sequence is correct" is unsatisfiable, and so is "the sequence is
   validated".** *(Added 2026-08-20.)* `infoic.xml` carries no sequence data
   (finding 5), so both sequences are datasheet-derived and the strongest available
   test is a pinned byte table plus a citation comment — a **change detector, not a
   correctness proof**. And no bench leg supplies an oracle for the status address
   or the decode (only for the *mode entry*, via the chip-ID read). The satisfiable
   forms are: "the bytes are pinned with a `vendor / document / revision / page /
   §section` citation and a test fires on any edit", and "the mode entry was
   confirmed on silicon by a chip-ID read returning `0xDA45`".
9. **A criterion phrased "the operator's `W29C020` answers `protected` /
   `unprotected`" is unreachable by design.** *(Added 2026-08-20.)* That entry
   refuses under D-06 because `W29C022` is undocumented, so the only reachable
   output on that part is D-07's `unadjudicated_probe`. Any criterion expecting a
   state class from it contradicts D-06.

---

## Standard Stack

### Core — all already present, nothing to install

| Component | Version / location | Purpose | Why standard here |
|-----------|--------------------|---------|-------------------|
| `click` | already a hard dep of `firestarter_app` | the `dev lock-status` command surface | every command in `cli_handlers.py` is Click; `_DevGroup` subclasses `click.Group` |
| `pytest` | `>=8.0` via `.[test]` | all host verification | CI's only test runner |
| `syrupy` | `>=5.0` via `.[test]` | the `dev --help` snapshot regeneration | already owns `tests/__snapshots__/test_characterization.ambr` |
| `pytest-cov` | `>=7.1.0` via `.[test]` | the `--cov-fail-under=70` floor | CI gate |
| `mypy` | `>=2.1.0,<3` via `.[test]`, `python_version = "3.10"` | the watermark gate (scope: `firestarter/` **and** `tests/`) | watermark 35, floor 120 checked files |
| `ruff` | `>=0.15.14` via `.[test]`, `select = ["E","F","I","UP"]` | lint + format over `firestarter/` and `tests/` | CI gate |
| `ast` (stdlib) | — | the LOCK-01 invariant gate | `check_sdp_capability_invariants.py` is a pure `ast.parse` + `ast.NodeVisitor` walk |
| PlatformIO + Unity + ArduinoFake | `platformio_core 6.1.19`, `platform_atmelavr 5.2.0`, `avr_gcc 7.3.0`, `framework_arduino_avr 5.3.0` (from `size_baseline.json.meta`) | firmware native suites | pinned in the baseline's `meta`, so a toolchain move is itself a finding |
| `tools/catalog/codegen.py` | meta-repo, stdlib-only, Python 3.11+ (`tomllib`) | message-catalog regen if a new id is needed | the only sanctioned path to `messages.h` / `messages.py` |

**Installation:** nothing new.

```bash
# host, from firestarter_app/
pip install -e '.[test]'
# firmware, from firestarter/
pio test -e native            # toolchain already resolved
```

### Alternatives Considered

| Instead of | Could use | Tradeoff |
|------------|-----------|----------|
| A new Python module with literal tables (D-05) | JSON under `firestarter/data/` | Rejected by D-05: a hand-curated file beside the **generated** `chip_database.json` is a footgun, and costs a loader + schema test + `[tool.setuptools.package-data]` entry (`pyproject.toml:96-101` currently lists exactly three data files). |
| A new Python module | markdown-only under `doc/` | Rejected by D-05: two sources of truth with nothing keeping them equal. |
| A pytest invariant module (D-12) | a phase-local `151-check-claims.py` | Rejected by D-12, on measured evidence — the `check_permitted_claims.py` family failed **open**. |
| A new `CMD_*` at 16 + a widened parse gate | reusing `CMD_CHECK_CHIP_ID` with a new flag bit | Not evaluated by CONTEXT.md and **not** recommended: flag bits produce **silence** on old firmware (`serial_comm.py`'s D-15 note and `sdp_honesty`'s HOST-06 asymmetry), so D-04's `FirmwareOutdatedError` mapping would be **unreachable** — an unknown *command* errors, an unknown *flag* does not. Recording it so the planner can reject it for the right reason. |
| A datasheet-cited pinned byte table for each sequence | deriving the sequences from `infoic.xml` | **Ruled out by measurement, not preference** (finding 5 / revised C-9, C-10): the file's complete per-chip datum is 20 parameter attributes with no child elements and no text; the only blob-shaped field, `config`, is `"NULL"` on every `0x05` and `0x06` entry. The operator's hypothesis was checked first, as directed, and the answer is a clean negative. |
| A single status `u8` in an OK frame | extending `MSG_OK_READY` | `MSG_OK_READY` genuinely extends with zero codegen, but it is the operation-**setup** ack emitted on every command; every command would then pay the bytes and carry a protection claim. |

---

## Architecture Patterns

### System Architecture Diagram

```
                    ┌──────────────────────────────────────────────┐
  user types  ───▶  │ dev lock-status <chip> [--force]             │
                    │ (registered ONLY if _DEV_TOOLS_ENABLED)      │
                    └───────────────┬──────────────────────────────┘
                                    │
        stable build ───▶ _DevGroup.get_command() ──▶ UsageError(dev_command_gate_message)
                                    │  (name in BETA_ONLY_DEV_COMMANDS)
                                    ▼
                    ┌──────────────────────────────────────────────┐
                    │ app.db.get_eprom(name)   ← FULL dict         │
                    │   carries "name" + "protocol-id"             │
                    │   (NOT resolve_chip()'s programmer dict)     │
                    └───────────────┬──────────────────────────────┘
                                    ▼
      ┌─────────────────────────────────────────────────────────────────────┐
      │  PURE RESOLUTION  (new module, no click / no serial / no file I/O)  │
      │                                                                     │
      │  no entry ──────────────────────────▶ (chip-not-found refusal)       │
      │  no "protocol-id" key ─────────────▶ raise KeyError (hard fail)     │
      │                                                                     │
      │  protocol-id ∈ {0x07,0x08,0x0B,0x0E,0x27,0x28,0x29} ─▶ no_mechanism │
      │  protocol-id == 0x10 ───────────────────────────────▶ not_implemented│
      │  protocol-id == 0x0D ───────────────────────────────▶ not_readable   │
      │  protocol-id == 0x34 ───────────────────────────────▶ ⚠ UNASSIGNED   │
      │  protocol-id ∈ {0x05, 0x06} ──▶ split_part_number_tokens(name)      │
      │        │                                                            │
      │        ├─ every token = documented-readable ──▶ READ PERMITTED      │
      │        ├─ any token = documented-not-readable ─▶ not_readable        │
      │        └─ any token = undocumented ───────────▶ undocumented_alias   │
      │                                        (reason NAMES the token)      │
      └─────────────┬────────────────────────────────┬──────────────────────┘
         READ PERMITTED                   REFUSED  │  (or --force override)
                    │                              │
                    │        ┌─────────────────────┴──── --force ────┐
                    ▼        ▼                                        │
      ┌───────────────────────────────────────────────┐               │
      │ HOST WIRE LAYER  (serial_comm / eprom_ops)    │               │
      │  build {"cmd": <new>, "algorithm": …,         │               │
      │         "memory-size": …, "bus-config": …}    │               │
      └───────────────┬───────────────────────────────┘               │
                      ▼                                              │
   ═══════════════ 250000 baud, COBS-framed JSON ═══════════════      │
                      ▼                                              │
      ┌───────────────────────────────────────────────┐               │
      │ FIRMWARE  init_programmer_framed → parse_json │               │
      │   ⚠ GATE: if (cmd < CMD_READ_VPP) json_parse  │  ← the fork   │
      │   ⚠ GATE: if (is_memory_cmd(cmd))             │               │
      │              configure_memory(handle)         │               │
      └───────────────┬───────────────────────────────┘               │
                      ▼                                              │
      ┌───────────────────────────────────────────────┐               │
      │ configure_memory → protocol dispatch          │               │
      │   0x06 → configure_flash_nor_unlock()         │               │
      │   0x05 → configure_flash_5v_page()            │               │
      │   (new case arm in EACH)                      │               │
      └───────────────┬───────────────────────────────┘               │
                      ▼                                              │
      ┌───────────────────────────────────────────────┐               │
      │ loop() switch → the new operation             │               │
      │   FLASH_ENABLE_ID (AA/55/90)                  │               │
      │   read status address(es)                     │               │
      │   FLASH_DISABLE_ID (AA/55/F0)                 │               │
      │   emit OK/DATA id-frame with status param(s)  │               │
      │   ── OR ── default: MSG_ERR_UNKNOWN_CMD       │               │
      └───────────────┬───────────────────────────────┘               │
                      ▼                                              │
   ═══════════════ id-framed response ═══════════════════════         │
                      ▼                                              ▼
      ┌────────────────────────────────────────────────────────────────────┐
      │ HOST OUTPUT LAYER                                                  │
      │   status byte  ──▶ protected | unprotected      exit 0             │
      │   MSG_ERR_UNKNOWN_CMD ──▶ firmware_outdated     exit <op-failure>  │
      │   comms/timeout ──────▶                         exit <op-failure>  │
      │   refusal classes ────▶ not_readable | not_implemented |            │
      │                         undocumented_alias | no_mechanism           │
      │                                                 exit <cannot-answer>│
      │   --force path ───────▶ unadjudicated_probe     (never a claim)     │
      │                                                                     │
      │   every line LEADS with the class token, then prose from            │
      │   sdp_honesty (single copy of the caveat sentence)                  │
      └────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| File | Repo | Responsibility | New or edited |
|------|------|----------------|---------------|
| `firestarter/<protection_table>.py` | app | the curated token→(class, mechanism, permanence, citation) table + the pure resolution predicate | **new** |
| `firestarter/sdp_honesty.py` | app | `not_readable` caveat (existing text, reused) + a generalised unknown-cmd mapper sibling | edited (additive) |
| `firestarter/cli_handlers.py` | app | one `if _DEV_TOOLS_ENABLED:` block, one `@dev.command(name="lock-status")`, the 3-band `sys.exit` | edited |
| `firestarter/channel.py` | app | `BETA_ONLY_DEV_COMMANDS` 6→7 | edited (one line) |
| `firestarter/constants.py` | app | `COMMAND_<NEW>` + `COMMAND_NAMES` entry | edited |
| `firestarter/eprom_operations.py` or a sibling | app | build the command frame, parse the status response | edited |
| `tools/check_<protection_table>_invariants.py` | app | AST gate, Class 1 + Class 2 analogues | **new** |
| `doc/infoic-field-dictionary.md` | app | DATA-06's single authoritative section | edited |
| `doc/package-details.md` `:43-44`, `doc/protocol-flags.md` `:24-25` | app | one-line pointers | edited (one line each) |
| `include/firestarter.h` | fw | `CMD_<NEW>` define + `is_memory_cmd()` case | edited |
| `src/firestarter.cpp` | fw | the parse-gate fork + one `loop()` switch arm | edited |
| `src/proms/flash_nor_unlock.cpp` | fw | `configure_*` case arm + the `0x06` sequence | edited |
| `src/proms/flash_5v_page.cpp` | fw | `configure_*` case arm + the `0x05` sequence | edited |
| `src/proms/flash_utils.cpp` / `include/flash_utils.h` | fw | (optional) a shared `read_in_id_mode(addr)` helper | edited |
| `scripts/check_size_baseline.py` | fw | the third named flash exemption (+ a second RAM exemption if RAM moves) | edited |
| `scripts/baseline/size_baseline.json` | fw | re-recorded from a cold triple-target build | edited |
| `tools/catalog/messages.toml` | **meta** | only if a new message id is needed (⚠ one free ERROR slot) | conditionally edited |

### Anti-Patterns to Avoid

- **Passing `resolve_chip()`'s dict to the resolution predicate.** It has neither
  `protocol-id` nor `name`. `sdp_capability_for_entry` hard-fails on exactly this
  because a silent default is how `check_eprom_blank`'s `_SRAM_PROTO_IDS`
  short-circuit went vacuous in production.
- **Stripping parentheticals from alias tokens.** Collapses
  `AT28C64B(Non-Standard)` onto `AT28C64B` and fabricates a spurious verdict.
  `split_part_number_tokens`' docstring is the record.
- **A per-chip lookup table keyed on part number in the generated DB.** DATA-04;
  three such tables were deliberately deleted in Phase 70; no `_PAGE_SIZE_BY_PART`
  sibling.
- **Deriving the curated table from a lexical rule.** Measured: `DIP28_28C64`
  splits 15 ALLOW / 20 REFUSE in the SDP case, and `lockable-proms.md`'s elided
  family shorthand defeats every literal match (7/190, 0/39).
- **A per-token verdict.** One DB entry gets one answer. Unanimity, fail-closed.
- **Asserting an exit code without its class token** (D-10) — this codebase already
  has an exit-code precedence defect where `max()` picked the wrong verdict.
- **Wording-only edits to `firestarter/include/messages.h`.** It is generated and
  ID-only; such an edit produces a zero diff and is silently lost. Edit the meta
  repo's `messages.toml` and run `sync_to_subrepos.sh`.
- **Re-anchoring `size_baseline_base01.json`'s growth axis.** A green
  `--policy merge05` after a growth-axis re-anchor means the anchor moved, not that
  growth stayed inside the band. Its own `re_anchor_note` says so.
- **Editing the `fullflash` fixture family in place.** Sever onto a new family.
- **`except Exception:` on a refusal path.** ruff's select list makes
  `# noqa: BLE001` inert, so nothing catches it — a swallowed error on the refusal
  path is exactly how a fabricated "unprotected" would reach a user.

---

## Don't Hand-Roll

| Problem | Don't build | Use instead | Why |
|---------|-------------|-------------|-----|
| Alias-token splitting from `part_number` | a new `.split(",")` | `sdp_capability.split_part_number_tokens` (import it) | the no-paren-strip rule is a measured correctness requirement, and a second copy is exactly the drift the codebase keeps removing |
| The "state cannot be read back" sentence | a new sentence | `sdp_honesty.unreadable_state_caveat()` | D-11; three production callers and four tests already compose it |
| Unknown-command → outdated-firmware mapping | a version probe | `sdp_honesty.map_unknown_cmd_to_outdated`'s id-keyed shape | `_probe_port`'s `[\d.x]+` cannot distinguish two betas, so a version probe must refuse both |
| Freezing a hand-curated literal table | a hash or a golden file | an `ast.parse` gate in the `check_sdp_capability_invariants.py` shape | a hash breaks on a comment edit; the AST gate denies *shapes* (comprehension, `.update()`, non-literal) and is fail-closed on a zero-symbol scan |
| Firmware chip-ID-mode entry/exit | a new byte sequence | `FLASH_ENABLE_ID` / `FLASH_DISABLE_ID` + `flash_execute_command` | already in `flash_utils.h`, already used by both target handlers |
| A memory-command admission test | a spot check | the exhaustive `[0,255]` truth table in `test_cmd_admission.cpp` | exhaustiveness over the full `uint8_t` domain is what makes the two-env run a set-equality proof |
| Admitting firmware growth | widening a band, or re-anchoring | a **new named, SHA-attributed exemption** | the two existing exemptions' comment blocks are the template, and the tripwire tests are the proof it stays armed |
| Message-id allocation | picking a free-looking number | `codegen.py --check`'s 10-rule validator + the band map | **the ERROR band has exactly one free id (`0xBF`)** |
| Sourcing the `0x05`/`0x06` sequence bytes | inferring them from `infoic.xml`, from `chip_info`, or from the neighbouring `FLASH_*` tables | a datasheet citation (`vendor / document / revision / page / §section`) + a pinned literal byte table | **measured negative:** `infoic.xml` carries 20 parameter attributes and no sequence data at all; `config="NULL"` on all 101 `0x05` and all 897 `0x06` entries; `chip_info` is constant `0x0000` on `0x05`. Inferring from `FLASH_ENABLE_WRITE_PROTECTION` would be worse — it is byte-identical to `FLASH_ENABLE_WRITE` and referenced by no executing code. |
| A "field has no consumer" proof | prose | a source-scan **test** in the `test_b15_page_size_corroboration.py` shape | D-16 forbids a new *gate*; the in-tree precedent is a test that carries the measurement in its docstring and pins the count as a constant |

**Key insight:** almost nothing in this phase is new machinery. Every mechanism it
needs — fail-closed unanimity over alias tokens, a literal table frozen by an AST
gate, a single-copy honesty sentence, an id-keyed outdated-firmware mapping, an
exhaustive command truth table, a named SHA-attributed size exemption — already
exists, has a paired non-vacuous test, and has a documented failure it was built to
prevent. The risk in this phase is **not** inventing something wrong; it is
**re-implementing** one of those mechanisms slightly differently and reintroducing
the drift it exists to stop.

---

## Common Pitfalls

### Pitfall 1: A new command number that silently gets no bus configuration
**What goes wrong:** `CMD_<NEW> 16` is defined, added to `is_memory_cmd()`, given
`configure_*` arms and a `loop()` case — and still fails at runtime with
`MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` or a null-pointer main, because
`if (handle->cmd < CMD_READ_VPP)` never ran `json_parse`, so `handle->protocol` is 0.
**Why:** the parse gate is an ordinal test, not a predicate, and `CMD_READ_VPP` is 11.
**How to avoid:** decide the gate fork **first**, in its own task, with a native
test that drives `parse_json` (not just `is_memory_cmd`) for the new ordinal.
**Warning signs:** `configure_not_implemented()` reached with `protocol == 0`; the
CLAUDE.md-documented fail-closed path firing on a command that should have worked.

### Pitfall 2: Funding flash and forgetting RAM
**What goes wrong:** a third flash exemption is added, `--policy merge05` still
fails, on `ram_used`.
**Why:** RAM has its **own** named exemption with a **separate, zero-headroom**
tolerance on all three targets (2 B admitted, 2 B used). One `uint8_t` on
`firestarter_handle_t` trips it.
**How to avoid:** measure RAM in the same cold capture; if it moves, add a second
named RAM exemption with its own `SCOPE: RAM only` clause. Never fold a RAM cost
into a flash number.
**Warning signs:** a FAIL line containing `ram_used baseline=… delta=+N exceeds
MERGE-05 ram allowance of 2 B`.

### Pitfall 3: Re-deriving a tripwire fixture "to make the suite green"
**What goes wrong:** the leonardo-growth plant (+307) is edited to sit inside the
new allowance, and the leg goes green while still claiming to prove a firing.
**Why:** every plant is `allowance + 1`; widening the allowance invalidates it.
This has happened three times already (+161 → +307 across Phase 144, 145, 149).
**How to avoid:** re-derive each plant from `allowance + 1` on a **new** fixture
family, and **observe it fail** before believing the pass. Update the asserted
message substrings (`allowance of 370 B`, the three-term decomposition) in the same
change.
**Warning signs:** a "fires on growth" test whose plant delta is smaller than the
allowance printed in the PASS line.

### Pitfall 4: The `dev --help` snapshot
**What goes wrong:** everything passes locally except `test_help_dev`, and the
failure diff is a wall of help text that looks unrelated to the change.
**Why:** syrupy pins the whole `dev --help` stdout, including the command list.
**How to avoid:** budget a `--snapshot-update` step, and **review the diff** — it
should be exactly one inserted row.
**Warning signs:** an `.ambr` diff touching more than the one row.

### Pitfall 5: Treating `algorithm: 13`'s "43 of 84" as a fact about the family
**What goes wrong:** DATA-06's section says "on `0x0D`, `protect_on_after` is true
on 43 of 84 rows", implying a property of 28C parts.
**Why:** 66 of those 84 rows are **promoted** from a foreign upstream protocol, and
their flag bits describe a record filed under that other protocol. Measured split:
18/18 native, 25/66 promoted.
**How to avoid:** state the split. D-15 asks for the measurement, not the headline.
**Warning signs:** a sentence about `0x0D` silicon that cites only the 43.

### Pitfall 6: A `KeyError` on the two TI rows
**What goes wrong:** the D-12 walk raises on `TEXAS INSTRUMENTS/2516` or `/2532`.
**Why:** those two rows' `programming` dict has no `protect_on_after` /
`protect_off_before` key at all — 744 of 746, not 746.
**How to avoid:** `.get(...)` with strict `is True` comparison, and a named
regression leg (`test_b15_page_size_corroboration.py:181` is the existing
"all N entries carry both fields" shape — note it scopes to the 84 `0x0D` rows,
where the fields *are* universal).

### Pitfall 7: Believing a green CI proves the mirror sites
**What goes wrong:** `is_memory_cmd`'s 9th arm lands; CI is green; the
`test_pinmap_provisional` 9th case was never written, or is wrong.
**Why:** `native_pinmap_provisional` runs in **no** CI leg (and neither do four
other suites; `test_flash_intel_vpp` runs nowhere at all).
**How to avoid:** name `pio test -e native_pinmap_provisional` as an explicit
verification step.

### Pitfall 8: A markdown-only commit that fires no CI
**What goes wrong:** the DATA-06 documentation lands, CI shows nothing, and the
plan records "CI green".
**Why:** `paths-ignore: ['**.md', …]` on both `push` and `pull_request`.
**How to avoid:** make DATA-06's proof a Python test; treat "CI green" as evidence
only for commits that touch non-markdown files.

### Pitfall 9: Reusing `_BOOT_BLOCK_SIZE` for W29C020C
**What goes wrong:** a 16 KiB boot-block assumption is applied to a part whose
documented boot blocks are **8 KB**.
**Why:** `_BOOT_BLOCK_SIZE = 0x4000` was derived for the W29C040 hint;
`lockable-proms.md:21` says W29C020/W29C020C has "Bottom and top 8 KB boot blocks".
**How to avoid:** per-family geometry, or no geometry at all (a device-global
answer needs none).

---

## State of the Art

| Old approach | Current approach | When changed | Impact on this phase |
|--------------|------------------|--------------|----------------------|
| `#ifdef DEV_TOOLS` + `cmd < CMD_DEV_ADDRESS` ordinal admission guard | `is_memory_cmd()`, unconditional, enumerated by name | v1.22 Phase 119 | a new memory command edits a predicate, not a preprocessor branch — but the **parse** gate is still ordinal |
| Buffer size in the FW identity string | advertised as a u16 on every `MSG_OK_READY` (CAP-01), then extended twice more (CAP-02 identity, CAP-03 write budget), length-discriminated at a computed `ver_end` | Phase 55, then v1.31 | a 4th field is mechanically cheap and needs no codegen — but the ack is the *setup* ack |
| `firestarter dev sdp <chip> enable\|disable` | deleted; auto-unlock on every `0x0D` write + a `dev test` read-back-equality leg | v1.30 Phase 132 | the honesty wording it carried now lives in `sdp_honesty.py`, which is what this phase extends |
| `page_size` "not currently stored in chip_database.json" | stored on 20 rows (provenance-keyed), `infoic_page_size_raw` on 744 | v1.32 Phase 149 | the field dictionary's own `page_size` entry is stale (C-8) |
| Reported AVR flash ceilings 32256 / 32384 / 28672 | **32768 on all three**; bootloader regions forfeited, no compensating guard | quick task 260820-a7w, 2026-08-20 | `flash_free` figures moved; **MERGE-05 growth bands did not** |
| 8 `dev` subcommands, 6 channel-gated | unchanged | v1.30 Phase 136 | becomes 9 / 7 |

**Deprecated / must not be reintroduced:**
- Per-chip lookup tables keyed on part number in the generated DB (DATA-04; three deleted in Phase 70).
- A legacy-integer dispatch fallback axis in firmware (removed pre-v1.20).
- Gating a channel decision on an env var in the fail-**open** direction.
- `-D X=${sysenv.VAR}` in `platformio.ini` — an unset variable still *defines* the macro.

---

## Contradictions and Risks (Priority 10)

**Reported, not reconciled — 19 entries (C-1 … C-19).** Each names the two sources
and what is measured. Per the phase constraints I do not propose an alternative
design for any of them. **C-17, C-18 and C-19 were added 2026-08-20** with the
operator's `W29C020` and the `infoic.xml` / datasheet sweep; **C-9 and C-10 were
revised** in the same pass and C-10's "empty by construction" verdict is
**withdrawn**.

### C-1 — CLAUDE.md: "this repo tracks only `.planning/` and `.claude/`"
**Says:** `/workspaces/CLAUDE.md` §"Repository Structure": *"This repo tracks only
`.planning/` (GSD project management artifacts) and `.claude/` (project settings)."*
**Measured:** `git ls-files tools/` `[CMD]` returns `tools/catalog/codegen.py`,
`tools/catalog/messages.toml`, `tools/catalog/sync_to_subrepos.sh` — a **third**
tracked tree, and it is the authoritative source for both sub-repos' generated
message catalogs. `platformio.ini` also exists at the meta root (untracked or not,
it is present).
**Why it matters here:** if a new message id is needed, the plan must commit in the
meta repo too — which CLAUDE.md's sentence would lead a planner to believe is
impossible for anything but `.planning/`.

### C-2 — ⚠ `firestarter lock-status` (ROADMAP + REQUIREMENTS + STATE) vs `dev lock-status` (CONTEXT D-01)
**Says, in four places:**
- `.planning/ROADMAP.md:189` — *"`firestarter lock-status <chip>` reporting state where the family documents it readable"*.
- `.planning/ROADMAP.md` §"Phase 151" Success Criteria **2** — *"`firestarter lock-status <chip>` reports the protection state…"*.
- `.planning/REQUIREMENTS.md:229` — **LOCK-02**: *"`firestarter lock-status <chip>` reports the protection state of a chip on families…"*.
- `.planning/STATE.md` — *"Phase 151 now inherits that file as the milestone's sole remaining writer (`firestarter lock-status <chip>` is a new **top-level command registration**)."*
**Says, in one place:** CONTEXT.md **D-01** — *"Real silicon read, exposed as a
beta-only `dev lock-status`. Registered only on a pre-release install, via the
existing `_DevGroup` / `channel.BETA_ONLY_DEV_COMMANDS` gate, so a stable install
never sees the command."*
**Measured:** `grep -rn "lock-status\|lock_status" firestarter_app/{firestarter,tests,tools}` `[CMD]`
returns **zero hits** — neither surface exists yet, so nothing in code settles it.
**Consequences the planner must weigh, both measured:** a top-level command is
registered in the 15-command `@cli.command()` block and would appear in the
`test_help` top-level snapshot; a `dev` subcommand needs the 7-tuple, the two
gating test files, and the `test_help_dev` snapshot. They are *different* file sets.
**This is the single most consequential unreconciled discrepancy in the phase**, and
ROADMAP's own criterion 2 already carries the flag the research brief asked for.
**Also:** STATE.md's parenthetical calls it a "top-level command registration"
while asserting `cli_handlers.py` sole-writer status — the sole-writer claim is
true either way.

### C-3 — ROADMAP: "mostly host-side with **one** firmware-touching workstream"
**Says:** `.planning/ROADMAP.md:37` and `:155` describe v1.32 as *"mostly host-side
with **one** firmware-touching workstream — the page-size seam, Phase 149, dual-repo
lockstep"*.
**Measured:** CONTEXT.md D-01 makes 151 a **second** firmware-touching workstream,
and CONTEXT.md §`<domain>` already flags this: *"That sentence is now out of date
and Phase 152's outward-facing text must not repeat it."*
**Why it matters:** Phase 152's OUT-04 release notes are derived from that sentence.

### C-4 — ⚠ D-11: "Both of that module's declared forward callers were deferred, so `lock-status` is the first one to actually land"
**Says:** CONTEXT.md D-11.
**Measured** `[CMD grep -rn "sdp_honesty|unreadable_state_caveat|emission_summary|map_unknown_cmd_to_outdated" --include=*.py]`:
`unreadable_state_caveat()` has **three landed production callers** —
`firestarter/cli_handlers.py:2405`, `firestarter/cli_handlers.py:2409`, and
`firestarter/chip_test.py:1480` (imported at `cli_handlers.py:35` and
`chip_test.py:41`, both with the comment *"unreadable_state_caveat(), called not
re-authored"*), plus four pinning tests in `tests/test_chip_test_sdp_leg.py`
(`:1241`, `:1249`, `:2168`, `:2182`). So **Phase 134's leg-report rows DID land.**
Only `emission_summary()` and `map_unknown_cmd_to_outdated()` are callerless.
**Why it matters:** D-11's *decision* is unaffected (extend `sdp_honesty.py`), but
its *risk assessment* is inverted — editing `unreadable_state_caveat`'s **text**
now breaks 7 pinning sites and 2 production surfaces, so the extension must be
strictly **additive**.

### C-5 — D-09's class enumeration does not partition all 746 rows
**Says:** CONTEXT.md D-09 — *"406 of 746 DB rows have no write-protection mechanism
at all (UV-EPROM `0x07`/`0x08`/`0x0B`, SRAM/NVRAM `0x0E`/`0x27`/`0x28`/`0x29`)"*.
**Measured:** those seven algorithms total **405**, not 406. The 406 figure is
`746 − 229 − 111` and is only reachable by also counting **algorithm `0x34` (52),
one row**: `XICOR/X88C64P,X88C64S`, an EEPROM with `protect_off_before: true` and
`support_status: "protocol-not-implemented"`.
**Why it matters:** this is precisely the exhaustiveness hole D-12's invariant is
supposed to catch, and it exists **before any code is written**. The class for that
row is an open decision.

### C-6 — D-06's worked example understates the case: `W29C042` is also undocumented
**Says:** CONTEXT.md D-06 — *"the DB entries are `W29C020,W29C020C,W29C022` and
`W29C040,W29C042`, and **`W29C022`** appears nowhere in `lockable-proms.md` at all"*.
**Measured:** `W29C022` → **0 occurrences** ✓; **`W29C042` → also 0 occurrences**
(unmentioned by CONTEXT.md). `lockable-proms.md:22` lists the family as
`W29C040 / W29C040**P**`, not `W29C042`.
**Why it matters:** the `W29C040,W29C042` entry refuses for **two** independent
reasons (one `documented-not-readable`, one `undocumented`), so D-06's refusal
message must handle a *set* of offending aliases in *different* states, not a
single one.

### C-7 — CONTEXT.md's `flash_5v_page.cpp:86` citation is a comment-block, not a line
**Says:** CONTEXT.md — *"its :87 comment records that W29C040 ships with SDP enabled"*.
**Measured:** the comment block spans `:86-90`; the specific W29C040 sentence is on
`:87`. Not a contradiction, an imprecision — recorded because the planner will cite
it in a task action.

### C-8 — `doc/infoic-field-dictionary.md`'s `page_size` entry is stale
**Says:** `[FILE firestarter_app/doc/infoic-field-dictionary.md:247]` —
*"**build_db.py usage:** Not currently stored in `chip_database.json`. No decode
bug; simply not used yet."*
**Measured:** 20 rows carry `programming.page_size` and 744 carry
`programming.infoic_page_size_raw`, both landed by Phase 149 / Phase 136.1.
**Why it matters:** D-13 lands a new section in this exact file, so a reader will
be one heading away from a false statement. **Fixing it is out of DATA-06's scope**
and this research does not propose fixing it — it flags it so the planner can
decide deliberately rather than by omission.

### C-9 — the sequence offset `SA + 0x02` is not in the repository
**Says:** CONTEXT.md D-02 — *"Autoselect sector-protect verify is a read at the same
mode's `SA+0x02`"*.
**Measured:** `[CMD grep -rin "autoselect|sector.protect|protect.verify|product.id"
over firestarter/{src,include,doc}]` finds no such offset, no sector-address
computation and no `00h`/`01h` decode anywhere. `lockable-proms.md:36-40` says only
*"Read a sector address with the specified low address bits … `00h` generally means
unprotected … Exact address wiring and byte/word interpretation depend on x8/x16
mode."* The seed says `AA-55-90`, read sector addr → `00h`/`01h`.
**Classification:** the specific `+0x02` offset is `[ASSUMED]` — training-data or
datasheet knowledge, not verified in this repository. It must be sourced from a
datasheet before implementation.
**Related, and also measured:** there is **no sector map** anywhere in this project
(`flash_nor_unlock_sector_erase` takes a caller-supplied address; the host's
`erase --sector-address` supplies it). So a per-sector answer has no data source.

**⚠ REVISED 2026-08-20 — `infoic.xml` checked, on operator direction, and it does
NOT supply the offset.** C-9 therefore **stands as written and is now closed to
`infoic.xml` as a source.** Measured against the pinned
`a8efaedc236c1d9718bd28299dfbb99536b010ff/infoic.xml` (see §"Does `infoic.xml`
Supply the Sequences? — a clean, evidenced NEGATIVE"): the complete per-chip datum
is **20 attributes, zero child elements, zero text content**; there is no
attribute name matching `cmd|seq|unlock|protect|addr|command`; the magic bytes
`aa55`/`5555`/`2aaa` appear in **no attribute value** of any of the 11510 `<ic>`
entries (2 accidental hits, both inside MICRON part *names*); `config` — the only
blob-shaped field — is `"NULL"` on **all 897** `protocol_id="0x06"` entries; and
`page_size` is `0x0000` across the whole `0x06` population. The only unused field
that varies on `0x06`, `chip_info` (`0x0000`/`0x00e3`/`0x00e4`), is a
vendor/algorithm-family cluster, not an address.
**Consequence:** the offset is **datasheet-only**, which means it can carry a
citation comment and a pinned byte table but **can never have an element-wise
proof** against a machine-readable upstream. `infoic.xml` supplies exactly one
relevant datum — `chip_id` (`AM29F040 → 0x000001a4`, `SST39SF040 → 0x0000bfb7`,
`W49F020 → 0x0000da8c`), which is a **positive control for the mode entry** and
says nothing about the status read.

### C-10 — the `0x05` sequence has no in-repo specification at all
**Measured:** no Product-ID-mode entry distinct from `FLASH_ENABLE_ID`, no
boot-block status address, no `FF`/`FE` lockout decode. The host's own hint
(`eprom_operations.py:174`) names *"the firmware §6.6 DETECT read"* as the thing
that would confirm — describing a read that does not exist. Two message ids for its
outcome (`MSG_WARN_FL4_BOOT_BLOCK_LOCKED 0x85`, `MSG_ERR_FL4_BOOT_BLOCK_LOCKED
0xBC`) exist in the catalog and are **emitted by nothing**.
**Risk:** the entire `0x05` half is being funded on a sequence that must be derived
from a datasheet, on a family whose readable verdict D-03 restricts to W29C020C,
and whose DB entry refuses by default under D-06.

**⚠ REVISED 2026-08-20 — two operator inputs change this verdict. The
"empty by construction" conclusion is WITHDRAWN.**

*(a) `infoic.xml` is now closed as a source, confirming the sequence-provenance
half.* Same measurement as C-9: `config="NULL"` on **all 101** `protocol_id="0x05"`
entries, no address-typed or sequence-typed attribute exists at all, and
`chip_info` is **constant `0x0000`** across the entire `0x05` population — so there
is not even a discriminator to work with. The `0x05` Product-ID boot-block status
address and its `FF`/`FE` decode are **datasheet-only**, and `datasheets/` contains
**nothing** for the `W29C0xx` family (the tracked `W27C020.pdf` is algorithm
`0x08`, a different family — see C-19).

*(b) The operator has a `W29C020`, and that gives the `0x05` half a real, if
narrow, payoff chain — so "empty by construction" was wrong.* Corrected, with the
chain named end to end:

- **The reachable path:** `dev lock-status W29C020 --force` → D-07's
  `unadjudicated_probe` → the `0x05` sequence executes on silicon. `--force` is
  required **even on the operator's own part**, because the DB entry's third alias
  `W29C022` is undocumented and D-06's unanimity refuses the entry regardless of
  how bare `W29C020` is curated. So the chain runs **through `--force`, on the
  `W29C020`**, and it is not empty.
- **What it earns, at most:** that the sequence was exercised on one Winbond
  `W29C020` sample and returned a decodable value. Under D-03's *narrow/textual*
  reading the W29C040 claim-cap does not bind a different leg on a part the `:21`
  row does list as readable; under its *purposive* reading it does. Both readings
  are laid out in §"What a `W29C020` bench leg can legitimately earn" — **this
  research does not set the claim policy.**
- **The genuinely new finding:** the sequence decomposes, and its **mode-entry**
  half is verifiable on silicon **today, with zero new code**. `firestarter id
  W29C020` already runs `FLASH_ENABLE_ID` → read `0x0000`/`0x0001` →
  `FLASH_DISABLE_ID` and must return **`0xDA45`**. The *status address* and the
  *decode* remain unverifiable (no independent oracle short of a destructive
  write→verify, which is the *indirect* method `lockable-proms.md:3` excludes from
  "readable" by definition).
- **What it still does NOT earn:** validation of the `0x05` sequence; any claim
  about `W29C020C` or `W29C022` (indistinguishable on the wire — one `<ic>`, one
  `chip_id 0x0000da45`, see C-18); anything about the **`0x06` Autoselect half**,
  which has **no bench leg at all** and ships software-proven and unrun on silicon;
  and anything about AT28C or `0x0D`, barred by the milestone Evidence Ceiling.

Recorded this way because CONTEXT.md §`<specifics>` says those bytes were funded
specifically for the v1.17 payoff: that payoff is now **partially** reachable —
a corroborating read on a related part — rather than unreachable, and it is
**still not the closure the v1.17 RCA asked for**, which wanted a second W29C040
sample.

### C-11 — the ERROR message band has one free id
**Measured** `[CMD tomllib over tools/catalog/messages.toml]`: ERROR (0xA0–0xBF)
has 31 of 32 ids used; **only `0xBF` is free**. WARN has 24 free, INFO 42, OK 10,
DATA 26.
**Risk:** a design needing two new ERROR messages does not fit, and there is no
documented band-extension procedure.

### C-12 — six firmware native suites run in no CI leg (not two)
**Measured:** `test_pinmap_provisional`, `test_trace_eprom_v131`,
`test_eprom_params_v131`, `test_loop_eprom_v131`, `test_vpp_eprom_v131`, and
`test_flash_intel_vpp` (which no `test_filter` names at all).
**Risk:** `test_pinmap_provisional` is one of the mirror sites a new memory command
must edit, and CI will not tell you if that edit is wrong.

### C-13 — a markdown-only commit fires no host CI
**Measured:** `firestarter_app/.github/workflows/ci.yml` `paths-ignore` includes
`'**.md'` on both `push` and `pull_request`.
**Risk:** DATA-06's documentation half is invisible to CI. (Also: the ignore list
names `docs/**` while the real directory is `doc/`; `'**.md'` covers it, so this is
latent, not active.)

### C-14 — CONTEXT.md names two MERGE-05 literals; four exist
**Says:** D-01 names `MERGE05_DEFECT_FIX_EXEMPTION_BYTES` (96) and
`MERGE05_PAGE_SIZE_SEAM_EXEMPTION_BYTES` (210).
**Measured:** also `MERGE05_UNO_CLASS_FLASH_BAND = 64` (`:138`) and
`MERGE05_PAGE_SIZE_SEAM_RAM_EXEMPTION_BYTES = 2` (`:282`). The RAM one has **zero
headroom on all three targets** and D-01's cost paragraph does not mention RAM at
all.

### C-15 — `.[dev]` vs `.[test]`
**Measured:** `pyproject.toml` defines **both**; `dev` is `pytest>=7.0` only, while
CI installs `.[test]` (pytest 8, syrupy, ruff, mypy, pytest-cov, types-pyserial).
**Risk:** the documented near-miss; `.[dev]` cannot run the gates.

### C-16 — `FLAG_FORCE`'s existing firmware meaning is narrower than D-07's use
**Measured:** in firmware, `FLAG_FORCE` downgrades a **chip-ID mismatch** from
error to warning (`flash_utils.cpp:97-103`); on the host it is threaded via
`_build_op_flags(force=force)` on `blank`, `erase`, `id`.
**Note:** D-07's `--force` is a **host-side** bypass of a **table** refusal — a new
meaning for the same flag name. Whether the wire bit is even sent is undecided.

### C-17 — ⚠ `lockable-proms.md` is internally inconsistent about bare `W29C020`
*(Added 2026-08-20 after the operator reported having a `W29C020`.)*
**Says, at `:21`:** the row key is `**W29C020 / W29C020C**` and the single set of
column values is `Yes—special` / "Bottom and top 8 KB boot blocks" / permanence
`Yes` / "Read boot-block status in Product ID mode" — i.e. the table's verdict
covers **both** parts, consistent with §1's own `X / Y` sibling-suffix idiom used
at `:20`, `:22` and `:23`.
**Says, at `:30`, `:335` and `:350`:** every restatement of the claim outside the
table names **`W29C020C` and only `W29C020C`** — the emphasis sentence
(*"For the **W29C020C**, the bottom and top boot-block states are explicitly
readable"*) and **both** §Practical-summary bullets (readable-lock-status list;
potentially-irreversible list).
**Measured:** bare `W29C020` appears **exactly once** in the whole 399-line
document — the `:21` row key — and in none of the four narrowing restatements
`[CMD grep -n "W29C02\|W49F002\|W29C010\|W29EE01" doc/lockable-proms.md]`.
**Why it matters:** it decides whether the operator's part is inside or outside the
documented-readable set, and **neither reading is safe**: reading the row as
authoritative attributes a verdict three restatements decline to repeat, and
reading the restatements as authoritative attributes an exclusion the table does
not state. It also has **no slot in D-06's three states** — bare `W29C020` is not
`undocumented` (it is in the document) yet is not unambiguously
`documented-readable` either. Resolving it *is* the per-entry adjudication D-06's
rejected alternative forbids, so it must be surfaced, not curated away.

### C-18 — the three `W29C020*` aliases are indistinguishable to the programmer
*(Added 2026-08-20.)*
**Measured** against the pinned `infoic.xml`: `W29C020`, `W29C020C` and `W29C022`
are **one** `<ic>` entry with **one** `chip_id="0x0000da45"`, one
`pin_map="0x0000190b"`, one `page_size="0x0080"`, one `flags="0x0040c078"`. The
generated DB carries them as one row with `chip_id_value: "0x0000da45"` and
`chip_id_check: true`.
**Why it matters:** a per-alias readability distinction is **unobservable on the
wire**. Whatever C-17 is resolved to, the firmware cannot tell which of the three
parts is in the socket, so a bench result on a `W29C020` cannot be attributed to
`W29C020C` (the part the document does call readable) and cannot be excluded from
`W29C022` (the part no source document covers). This *weakens* rather than
strengthens any family-level claim from a single-part leg, and it is the measured
reason D-06's one-entry-one-answer rule is right here.

### C-19 — ⚠ two live datasheet traps in `firestarter_app/datasheets/`
*(Added 2026-08-20.)*
**Measured** `[CMD ls -la datasheets/ ; git ls-files datasheets/ ; git status --porcelain datasheets/]`:
the directory holds **7** PDFs, of which **3 are git-tracked** — `AT28C256.pdf`,
`SST39SF0x0A.pdf`, `W27C020.pdf` — and 4 are untracked (`M27C1001.pdf`,
`M27C512.pdf`, `W27C512.pdf`, `W27E257.pdf`).
**Trap 1 — a one-character family collision.** `W27C020.pdf` is a **Winbond
`W27`C020** datasheet, and `W27C020` resolves in the DB to
`WINBOND | W27C02,W27C020,W27E02,W27E020,W27L02`, **algorithm `0x08`** — a
27-series part, **not** the `W29C020` (`algorithm 0x05`) this phase is about.
Same shape as the project's already-documented ST `M27C512` vs Winbond `W27C512`
trap. **Nothing in `datasheets/` covers the `W29C0xx` family.**
**Trap 2 — the one tracked `0x06` datasheet is for a non-readable family.**
`SST39SF0x0A.pdf` covers SST39SF010A/020A/040, which **are** `algorithm 0x06` rows
— but `lockable-proms.md:222` marks them **"No explicit lock bit"** (SDP + hardware
write inhibit) and `:229` states the datasheet *"describes hardware and software
data protection, but not conventional individually lockable sectors with a
sector-status query."* So it cannot source the Autoselect sector-protect verify.
**Also measured:** `firestarter/doc/PROTOCOLS.md:97,100,103` cites
`datasheets/0x05-FLASH-AMD-STD/W29C020.pdf p.9 §Write Operation` and
`W29C040.pdf p.11 §Page Write` / `p.12 §Chip Erase` — **a path that does not exist
in the working tree**. The citations are real and the convention
(*vendor + document + page + §section*) is the one LOCK-01 should follow, but the
files are not there.
**Tooling limitation, recorded rather than worked around:** no `pdftotext`,
`pdfinfo`, `mutool`, `pypdf` or `pymupdf` is available in this environment; a
stdlib `zlib` + text-operator extraction yields glyph-encoded output (subset fonts,
custom encodings) and a grep for
`autoselect|sector protect|product id|software data protection|boot block|29C020`
returned **zero hits** on both tracked candidates. **No datasheet claim anywhere in
this document is sourced from a PDF.**

---

## Package Legitimacy Audit

**Not applicable — this phase installs no external packages.** Every dependency it
uses is already declared in `firestarter_app/pyproject.toml` and already installed
by CI (`pip install -e .[test]`), or is part of the pinned PlatformIO toolchain
recorded in `size_baseline.json.meta`. No `npm`, `pip` or `cargo` install is
proposed anywhere in this research.

| Package | Registry | Disposition |
|---------|----------|-------------|
| *(none)* | — | No new package recommended; the Standard Stack table lists only already-declared dependencies. |

**Packages removed due to [SLOP] verdict:** none.
**Packages flagged as suspicious [SUS]:** none.
**Packages tagged `[ASSUMED]`:** none.

If a plan later proposes a new dependency, the legitimacy gate
(`gsd-tools query package-legitimacy check --ecosystem pypi <pkg>`) must be run
before it is written into a task, and every version pin must be re-verified with
`pip index versions <pkg>` on **PyPI** specifically.

---

## Environment Availability

| Dependency | Required by | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3 (devcontainer) | all host work | ✓ | **3.12.13** at `/usr/local/bin/python3` | ⚠ CI is **3.11 only** — see below |
| `pip install -e '.[test]'` deps | host gates | ✓ (declared) | pytest≥8, syrupy≥5, ruff≥0.15.14, mypy≥2.1.0,<3, pytest-cov≥7.1.0 | none needed |
| PlatformIO core | firmware build + native tests | ✓ | `6.1.19` (recorded in `size_baseline.json.meta`) | none |
| `platform-atmelavr` / avr-gcc | AVR builds | ✓ | `5.2.0` / `7.3.0`, toolchain `1.70300.191015` | none |
| `framework-arduino-avr` (+ MiniCore) | AVR builds | ✓ | `5.3.0` / MiniCore `3.1.2` | none |
| ArduinoFake (native) | native Unity suites | ✓ | resolved by PlatformIO | none |
| Meta-repo `tools/catalog/codegen.py` | message-catalog regen | ✓ | stdlib-only, needs Python **3.11+** for `tomllib` | 3.12 satisfies it |
| Bench: operator's **W29C040** part + a programmer port | D-03's probe (leg C) | operator-gated | — | the probe is optional by design; its absence blocks no software claim |
| `infoic.xml` | **the sequence-provenance question only** (checked 2026-08-20 on operator direction) | ✗ in-repo (gitignored, `.gitignore:29`) — **✓ fetched this session** from the pinned `a8efaedc…` revision via `tools/derive_sdp_partition.py`'s own mechanism | 17 861 009 bytes at `a8efaedc236c1d9718bd28299dfbb99536b010ff` | **not needed at build/test time** — nothing reads it at runtime or in CI, and this phase must not introduce a dependency on it. The sweep was one-off and wrote nothing into either repo. |
| PDF text extraction (`pdftotext` / `pypdf` / `pymupdf` / `mutool`) | reading the tracked candidate datasheets | **✗ none available** | — | **no fallback that works** — stdlib `zlib` extraction yields glyph-encoded output. Recorded as assumption **A8**; the datasheet conclusions rest on measured DB-algorithm and `lockable-proms.md` facts instead. |
| `firestarter_app/datasheets/` coverage of `W29C0xx` | sourcing the `0x05` sequence | **✗ absent** | — | none in-tree; `W27C020.pdf` is algorithm `0x08`, a different family (C-19). `PROTOCOLS.md:97,100,103` cites a `datasheets/0x05-FLASH-AMD-STD/W29C020.pdf` path that does not exist. |
| Bench: operator's **W29C020** part | leg A (mode-entry control, zero new code) and leg B (the `0x05` probe) | **✓ operator has one** (reported 2026-08-20) | — | leg A needs no new code at all; leg B is `--force`-only under D-07 |

**Missing dependencies with no fallback:** none.

**Missing dependencies with fallback / caveats:**
- **Python version drift:** devcontainer 3.12.13 vs CI 3.11-only. Recipe on
  record for a matching venv: `uv venv --python 3.11` (needs `UV_CACHE_DIR` set).
  Anything version-sensitive should be checked there before a beta push.
- **Sibling-repo presence:** `test_revision_constants_parity.py` and every other
  entry in `tests/scan_paths.py` **fail open** when the firmware sibling is absent
  (worktrees leave submodules empty). Plans must use `commits_land_in:` frontmatter
  rather than relying on a worktree.
- **No AT28C part in operator inventory** (milestone Evidence Ceiling) — irrelevant
  to this phase's own claims, but it means `0x0D` stays `UNVERIFIED` and
  `not_readable` is the only honest answer for those 84 rows regardless.

---

## Code Examples

Verified patterns, each with its in-tree source.

### The conditional beta-only `dev` command registration
```python
# Source: firestarter_app/firestarter/cli_handlers.py:1469-1505 (dev addr)
if _DEV_TOOLS_ENABLED:

    @dev.command(name="addr")
    @click.argument("eprom", shell_complete=_complete_eprom)
    @click.option("-i", "--input-enable", "input_enable", is_flag=True, help="…")
    @click.pass_obj
    @map_typed_errors
    def dev_addr(app: AppContext, eprom: str, address: str, ...) -> None:
        """Direct access to address lines and control register."""
        eprom_data = resolve_chip(eprom, db=app.db)
        ok = app.eprom_operator.dev_set_address_mode(...)
        sys.exit(0 if ok else 1)
```

### Getting the FULL entry dict (the only shape the predicate accepts)
```python
# Source: firestarter_app/firestarter/cli_handlers.py:713-726
    # resolve_chip's programmer dict carries neither `protocol-id` nor `name`
    sdp_entry = app.db.get_eprom(eprom)
    is_protocol_0x0d = (
        bool(sdp_entry) and sdp_entry.get("protocol-id") == SDP_PROTOCOL_ID
    )
    allowed, sdp_reason = sdp_capability(eprom, app.db)
```

### Fail-closed unanimity with a per-token described refusal
```python
# Source: firestarter_app/firestarter/sdp_capability.py:257-272
    unrecognised = [token for token in tokens if token not in SDP_CAPABLE_TOKENS]
    if unrecognised:
        described = [
            f"{token} (pre-SDP generation)"
            if token in PRE_SDP_NAMED_TOKENS
            else f"{token} (unrecognised)"
            for token in unrecognised
        ]
        return False, (
            f"{display_name.upper()}: {REASON_NOT_CAPABLE}: {', '.join(described)}. …"
        )
    return True, f"{display_name.upper()}: {REASON_ALLOWED}"
```

### The hard-fail that prevents a vacuous default
```python
# Source: firestarter_app/firestarter/sdp_capability.py:229-238
    if "protocol-id" not in entry:
        raise KeyError(
            f"sdp_capability_for_entry: entry for {display_name.upper()!r} has no "
            "'protocol-id' key. This is very likely the *programmer* dict "
            "returned by resolve_chip()/convert_to_programmer(), which carries "
            "neither 'protocol-id' nor 'name' — pass the full dict returned by "
            "db.get_eprom() instead. …"
        )
```

### The single-shot firmware query that returns values and finishes
```c
// Source: firestarter/src/hardware_operations.cpp:104-113
bool hw_get_version(firestarter_handle_t* handle) {
    LOG_DEBUG_ID_SUB(DBG_GET_HW_VERSION);
    rurp_configuration_t* rurp_config = rurp_get_config();
    uint8_t physical  = (uint8_t)rurp_get_physical_hardware_revision();
    uint8_t effective = (rurp_config->hardware_revision < 0xFF)
                        ? (uint8_t)rurp_config->hardware_revision
                        : 0xFF;  // P-02 sentinel: no override active
    LOG_OK_ID_U8_U8(MSG_OK_REV, physical, effective);
    return true;
}
```

### The chip-ID-mode enter / read / exit sequence to reuse
```c
// Source: firestarter/src/proms/flash_utils.cpp:82-87
uint16_t flash_util_get_chip_id(firestarter_handle_t* handle) {
    flash_execute_command(FLASH_ENABLE_ID);          // AA/55/90
    uint16_t chip_id = handle->firestarter_get_data(handle, 0x0000) << 8;
    chip_id |= handle->firestarter_get_data(handle, 0x0001);
    flash_execute_command(FLASH_DISABLE_ID);         // AA/55/F0
    return chip_id;
}
```

### The `FLAG_FORCE` severity-downgrade convention
```c
// Source: firestarter/src/proms/flash_utils.cpp:97-103
        if (is_flag_set(FLAG_FORCE)) {
            LOG_WARN_ID_BYTES(MSG_WARN_CHIP_ID_MISMATCH, _b, 4);
            handle->response_code = RESPONSE_CODE_WARNING;
        } else {
            LOG_ERROR_ID_BYTES(MSG_ERR_CHIP_ID_MISMATCH, _b, 4);
            handle->response_code = RESPONSE_CODE_ERROR;
        }
```

### Exhaustive command truth table over the whole `uint8_t` domain
```c
// Source: firestarter/test/native/avr/test_cmd_admission/test_cmd_admission.cpp:66-88
void test_admission_truth_table_over_every_cmd_value(void) {
    for (int c = 0; c <= 255; c++) {
        bool expected;
        switch (c) {
            case 1: case 2: case 3: case 4: case 5: case 6: case 9: case 10:
                expected = true; break;
            default:
                expected = false; break;
        }
        char msg[48];
        snprintf(msg, sizeof(msg), "is_memory_cmd(%d) mismatch", c);
        TEST_ASSERT_EQUAL_MESSAGE(expected, is_memory_cmd((uint8_t)c), msg);
    }
}
```

### The "this plan did not touch that file" guard (D-16's shape)
```python
# Source: firestarter_app/tests/test_b15_page_size_corroboration.py:246-260
def test_sdp_capability_module_untouched_this_plan() -> None:
    from firestarter import sdp_capability

    assert "12 of the 84" in (sdp_capability.__doc__ or ""), (
        "sdp_capability.py's docstring no longer carries the '12 of the "
        "84' prose this plan deliberately left unedited — if it changed "
        "for a legitimate reason, this assertion should be updated by "
        "whichever plan makes that change, not silently ignored."
    )
```

### The message-catalog regen (the only sanctioned path)
```bash
# Source: tools/catalog/sync_to_subrepos.sh (meta repo root)
bash tools/catalog/sync_to_subrepos.sh
# copies messages.toml + codegen.py into both sub-repos, asserts byte-identity,
# then regenerates firestarter/include/messages.h and
# firestarter_app/firestarter/messages.py
```

### The MERGE-05 verification command and its expected PASS line
```bash
# Source: firestarter/scripts/check_size_baseline.py:632-731 (main), :684-691 (PASS builder)
cd firestarter && python3 scripts/check_size_baseline.py --policy merge05 \
  --baseline scripts/baseline/size_baseline_base01.json \
  --avr-log leonardo=<cold.log>
# PASS: leonardo(flash=27212/32768[+306<=306=band0+exempt96+seam210],ram=2016/2560[+2<=2=seam2])
```

---

## Security Domain

`security_enforcement` is not set to `false` in `.planning/config.json` (the key is
absent), so this section is included.

### Applicable ASVS categories

| ASVS category | Applies | Standard control in this codebase |
|---------------|---------|-----------------------------------|
| V2 Authentication | **no** | local CLI, no identities |
| V3 Session Management | **no** | no sessions |
| V4 Access Control | **yes, in the physical-safety sense** | `is_memory_cmd()` is the documented access-control gate deciding which commands may call `configure_memory()` and therefore engage the 12 V VPP boost regulator. `rurp_pinmap_refuses()` delegates to it rather than re-listing. Adding an arm is a **hardware-safety** decision. |
| V5 Input Validation | **yes** | chip name → `db.get_eprom()` (no path or shell interpolation); `--force` is a boolean flag; a firmware **status byte** is untrusted input and must be validated before it becomes a class token. `serial_comm.py`'s existing plausibility clamps (`1 ≤ v ≤ 4096` for buffer size, `1 ≤ v ≤ WRITE_BUDGET_MAX_S` for the budget) are the in-tree pattern. |
| V6 Cryptography | **no** | none involved; CRC8 is integrity framing, not crypto, and is already implemented |
| V7 Error handling & logging | **yes** | the whole phase *is* an error-handling contract. `except Exception:` is gated by nothing (ruff select `E,F,I,UP`), so a swallowed error is the realistic route to a fabricated answer. |
| V12 File/resource handling | **marginal** | `~/.firestarter/database.json` is merged live and is **invisible to CI** (`sdp_capability.py:3-6`) — a user-added row must land in a **refusal** class, never a permit. |

### Known threat patterns for this stack

| Pattern | STRIDE | Standard mitigation, in-tree |
|---------|--------|------------------------------|
| A user-supplied DB override adds an unknown part that resolves to `unprotected` | **Spoofing / Elevation** | fail-closed allow-list semantics: a token absent from the curated table is `undocumented`, never permitted. This is exactly why `SDP_CAPABLE_TOKENS` is a static allow-list and why `check_sdp_capability_invariants.py` Class 1 denies permit-by-default. |
| A corrupt or hostile firmware ack is read as "unprotected" | **Tampering** | validate the status byte against an enumerated set before mapping to a class; treat any other value as "cannot answer", never as unprotected. `serial_comm.py`'s clamp-then-leave-`None` posture is the pattern. |
| An old firmware's silence is read as "unprotected" | **Tampering / Repudiation** | D-04: an unknown **command** errors and is detectable; an unknown **flag bit** is silent. Use a command, key on the id, and map to `firmware_outdated`. |
| A new command reaching `configure_memory` engages 12 V VPP on a 5 V part | **Denial of Service (physical destruction)** | `is_memory_cmd()`'s enumerated set + `PROTOCOLS.md`'s protocol→handler map + `configure_not_implemented()` fail-close on an unrecognised protocol. A read-only protection query must not route through `configure_eprom()`. |
| A `--force` probe result is later cited as a state claim | **Repudiation** | D-07 + D-03: label the output `unadjudicated_probe`; D-12 makes `protected`/`unprotected` structurally unreachable on that path. |
| A swallowed exception on the refusal path yields a fabricated answer | **Tampering** | ruff cannot catch it (BLE001 inert, 10 dead `noqa`s); enforce via the new AST gate's Class-1 analogue and a test. |
| Growth into the (now unprotected) bootloader region | **Denial of Service (bricking)** | a7w removed the linker's protection over Caterina/optiboot/urclock and **added no compensating guard** (operator-declined). The remaining guard is MERGE-05's growth band — which is why the 0 B leonardo headroom is a safety property here, not just bookkeeping. |

---

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|-------|---------|---------------|
| A1 | The AMD Autoselect sector-protect verify is a read at **`SA + 0x02`** in the same `AA-55-90` mode, returning `0x00` unprotected / `0x01` protected | §"The `0x06` / `0x05` Read Sequences" (from CONTEXT.md D-02) | The `0x06` sequence reads the wrong address and returns garbage that must not be reported. `lockable-proms.md` deliberately defers the exact wiring to the datasheet. **Still `[ASSUMED]` — and now narrowed: `infoic.xml` has been checked and does NOT supply it (finding 5 / revised C-9), so a datasheet is the only remaining source and the offset can never be machine-proven, only cited and pinned.** |
| A2 | The Winbond Product-ID-mode boot-block status read is a distinct entry sequence from `FLASH_ENABLE_ID`, with a specific status address and an `FF`/`FE` lockout encoding | same | The `0x05` sequence cannot be written at all. **Nothing in the repository specifies it**; the only in-tree reference is a host hint describing a read that does not exist. **Still `[ASSUMED]` — `infoic.xml` checked and negative (`config="NULL"` and `chip_info` constant `0x0000` on all 101 `0x05` entries), and `datasheets/` contains nothing for the `W29C0xx` family (C-19).** |
| A8 | That the two tracked candidate PDFs (`SST39SF0x0A.pdf`, `W27C020.pdf`) do not contain the missing sequence specifications | §"Then the datasheet…" / C-19 | **I could not read them.** No `pdftotext`/`pdfinfo`/`mutool`/`pypdf`/`pymupdf` in this environment; stdlib `zlib` extraction yields glyph-encoded output and a grep for the relevant terms returned zero hits. The conclusion rests instead on **two measured facts, not on reading the PDFs**: `W27C020` is DB algorithm `0x08` (a different family), and `lockable-proms.md:222,229` records SST39SF as having no readable sector-status query. If someone with a PDF reader finds an Autoselect sector-protect table in `SST39SF0x0A.pdf`, that would contradict `lockable-proms.md`, not this row. |
| A9 | The two D-03 claim-cap readings (textual/narrow vs purposive) are the only two available | §"What a `W29C020` bench leg can legitimately earn", revised C-10 | If the operator intends a third reading, the claimable set changes. **This research deliberately does not choose between them** — it lays out what each permits so the planner can fund the right acceptance criteria. |
| A3 | Byte-cost figures for any unwritten firmware (shared vs duplicated helper, status-byte vs per-region frame, the parse-gate change) | §"The `0x06` / `0x05` Read Sequences", §"Firmware Wire-Protocol Design Inputs" | A MERGE-05 exemption sized from an estimate is wrong. **Every figure is labelled `[ESTIMATE]`; only a cold `rm -rf .pio/build/<env>` + one `pio run -e <env>` per env produces a usable number.** No build was run this session. |
| A4 | Bit 14 gates minipro `-u` and bit 15 gates minipro `-P`; the protect op is an opaque TL866 opcode `0x18`/`0x19` | §"DATA-06's Documentation Home" (from the folded todo) | DATA-06's "capability, not policy" framing loses its grounding. `infoic.xml` is gitignored and uncommitted, so this cannot be re-verified in-repo; the minipro `database.c` permalink @ `a8efaedc` is the citation of record. |
| A5 | `lockable-proms.md`'s per-family datasheet verdicts (W29C020C readable + permanent; AT29C/AT28C not readable; AMD/Fujitsu/Macronix/ST readable) | §"The Curated Table's Source Document" | LOCK-01's entire readability axis. These are `[CITED: doc/lockable-proms.md]` with 8 web-fetched datasheet PDF references, several carrying `utm_source=chatgpt.com`. **The provenance of those references is worth an operator eye before 126 rows are transcribed on their authority.** |
| A6 | `_DEV_TOOLS_ENABLED` is `True` in this checkout because `__version__ = "3.0.0b21"` is a PEP 440 pre-release | §"Host Patterns Being Extended" | Only affects whether the current `test_help_dev` snapshot shows 8 or 2 commands. Verified by reading the snapshot (it shows 8), so this is corroborated rather than assumed. |
| A7 | "Physical flash headroom is ample" — leonardo `flash_free` 5556 B is genuinely usable | §"Live Firmware Size Figures" | It is usable only because a7w forfeited Caterina's 4096 B and the linker no longer protects it. Growing past the **old** 28672 B ceiling now overwrites the USB bootloader. This is `[FILE size_baseline.json meta]`, i.e. documented, but the *safety* consequence is real and the operator declined a compensating guard. |

**Nothing else in this document is assumed.** Every count, line number, band
figure, fixture value, test name, gate wiring, XML attribute and file path was read
from the tree, from the pinned upstream `infoic.xml`, or computed by a quoted
command this session.

---

## Open Questions (RESOLVED)

> **All seven resolved as of 2026-08-20, before planning.** Each item below carries an
> inline `*RESOLVED:*` line naming the binding decision and the plan that carries it, so
> this section is self-auditing and no reader has to cross-reference five other files.
> Four were settled by the orchestrator/operator as **OD-1…OD-4** (recorded in the
> planner brief and in `151-01-PLAN.md`); the rest were settled by the planner in
> `151-DESIGN.md`, produced by `151-01`.

1. **`firestarter lock-status` or `dev lock-status`?** (C-2)
   - *Known:* CONTEXT.md D-01 says `dev lock-status`, beta-only. ROADMAP criterion 2, ROADMAP:189, REQUIREMENTS LOCK-02 and STATE.md all say `firestarter lock-status`, and STATE.md explicitly calls it "a new **top-level** command registration".
   - *Unclear:* which wins. They imply different file sets, different snapshots, and a different stable-channel promise.
   - *Recommendation:* the planner must surface this to the operator before writing a task. D-01 is the later and more specific decision, and CONTEXT.md is the phase's own locked record — but four upstream artifacts say otherwise and one of them is a **requirement**. Do not reconcile silently in either direction.
   - *RESOLVED (**OD-1**):* `dev lock-status`, beta-only. Not actually contested — `151-DISCUSSION-LOG.md:20` shows the beta-only surface was presented as an option and chosen (`✓`), `:22` records the host-only recommendation "overruled deliberately", and `:113` states the surface "was already settled… in area 1". The four upstream artifacts carry **pre-discuss** text. `151-01` hand-edits all five measured stale sites (`ROADMAP.md:176`, `:189`, Success Criterion 2, `REQUIREMENTS.md:229`, `STATE.md`) plus ROADMAP's "one firmware-touching workstream" at `:37`/`:155`.

2. **What class does `algorithm: 0x34` (`XICOR/X88C64P,X88C64S`) resolve to?** (C-5)
   - *Known:* one row; EEPROM; `protect_off_before: true`; `support_status: protocol-not-implemented`; handler `configure_not_implemented()`; unreachable through `resolve_chip`.
   - *Unclear:* `no_mechanism` is false (upstream says it has one); `not_implemented` currently means "`0x10`, documented-readable but deliberately unimplemented".
   - *Recommendation:* decide explicitly and let D-12's exhaustiveness leg be the forcing function. It is red today.
   - *RESOLVED (**OD-2**):* `not_implemented`. `no_mechanism` would assert something upstream contradicts (`protect_off_before: true`) — a fabricated claim, which is what LOCK-03/LOCK-04 forbid. `not_implemented` is honest and preserves D-09's 8-class freeze with no ninth class. Census consequence: `not_implemented` is **40**, not 39 — pinned as a literal in `151-12` with the supersession stated. `151-DESIGN.md` §4.

3. **How is the parse-gate fork resolved?** (§Priority 2)
   - *Known:* no free slot below `CMD_READ_VPP` (11); a command at 16 gets no `json_parse` and no `configure_memory`.
   - *Unclear:* widen the ordinal test, or something else.
   - *Recommendation:* make it its own task with its own native test driving `parse_json` for the new ordinal, and decide it **before** the wire shape, because it determines the byte cost and therefore the exemption.
   - *RESOLVED (**OD-3**):* option (a) — widen the `:77` ordinal test to admit the command via `is_memory_cmd()`. (b) re-ordering the enum breaks wire compatibility with every shipped firmware and host constant; (c) is structurally impossible because `firestarter_get_data` is a protocol-handler pointer set by `configure_memory`. Carried by `151-03`, with the `[0,255]` truth-table update in **both** DEV_TOOLS states. Second consequence stated as a deliberate choice: ordinal 16 also falls outside the diagnostic range at `:136-146`, so `dev lock-status` emits **no** `DBG_*` output; admission set grew 8→9, diagnostic range unchanged.

4. **Does the `0x05` half earn its bytes? — REVISED 2026-08-20, and the answer is now "partially".** (revised C-10)
   - *Known:* `infoic.xml` is closed as a source (finding 5), so the sequence is datasheet-only and only pinnable, never provable. But the operator has a `W29C020`, so a reachable chain exists: `--force` → `unadjudicated_probe` → the sequence runs on silicon. And the **mode-entry half is verifiable today with zero new code** (`firestarter id W29C020` → `0xDA45`).
   - *Unclear:* how far D-03's W29C040-scoped claim-cap reaches to a W29C020 leg (two readings, both laid out); and whether the status address/decode can ever be claimed at all (they have no oracle).
   - *Recommendation:* report, do not redesign — D-02 and D-03 are locked. The plan should state the payoff as **partial corroboration on a related part**, and must not imply the v1.17 RCA closes — that RCA asked for a second **W29C040** sample.
   - *RESOLVED:* reported, not redesigned — D-02/D-03 stay locked and the operator kept the `0x05` half knowing the cost. `151-14` runs the bench session as legs A/B/C with the payoff stated as **partial corroboration on a related part**; no artifact claims the sequence is silicon-validated or that the v1.17 RCA closes. Per **OD-4** the pinned sequence bytes are a **change detector, not a correctness proof**, in those words.

7. **How is C-17 resolved — is bare `W29C020` `documented-readable`?**
   - *Known:* the `:21` row key covers it; `:30`, `:335`, `:350` and `:25` all narrow to `W29C020C`; bare `W29C020` appears exactly once in 399 lines. C-18 makes the distinction unobservable on the wire anyway (one `<ic>`, one `chip_id 0x0000da45`).
   - *Unclear:* which reading the curated table transcribes. **Neither is safe**, and D-06's three states have no slot for "documented, but the document's own summary declines to repeat the verdict".
   - *Recommendation:* operator decision. Resolving it in a curator's head is exactly the per-entry adjudication D-06's rejected alternative forbids, and DATA-04 polices this precise edge. Note the practical stakes are lower than they look: the entry refuses by default under **either** reading, because of `W29C022`.
   - *RESOLVED:* a **mechanism, not a judgement** — which is what D-06's rejected alternative and DATA-04 require. `151-DESIGN.md` §5 defines a named more-restrictive tiebreak rule plus a reporting-only `AMBIGUOUS_DOC_CITATIONS` record surfaced in the refusal text, so the documentary contradiction is *recorded* rather than adjudicated in a curator's head. D-06's three states are **not** extended. Practical stakes stay low: the entry refuses under either reading because of `W29C022`.

5. **Does a new message id fit?** (C-11)
   - *Known:* one free ERROR id (`0xBF`); WARN/INFO/DATA have room; `MSG_WARN_FL4_BOOT_BLOCK_LOCKED` / `MSG_ERR_FL4_BOOT_BLOCK_LOCKED` already exist unemitted.
   - *Recommendation:* prefer reusing the two existing boot-block ids and the WARN/OK/DATA bands; treat `0xBF` as a last resort.
   - *RESOLVED:* yes, in the **DATA** band — one new id `MSG_DATA_PROTECTION_STATUS` via the existing `LOG_DATA_ID_BYTES`, carried by `151-05`. `0xBF` is left unspent, with a durable test pinning that. Rejected: extending `MSG_OK_READY` (every ack would then carry a protection claim) and minting a new ERROR id (`0xBF` is the band's only free slot).

6. **Does the D-13 section produce a row in the summary table?**
   - *Known:* the summary's schema is `| Bug ID | Attribute | Correct decode | Current build_db.py behavior | Phase 57 fix |`; DATA-06 is not a bug.
   - *Recommendation:* the planner decides; "documented once" is satisfied either way, but D-13's "feeds that file's summary" phrasing invites a row the schema has no column for.
   - *RESOLVED:* **no row.** The summary's schema is `| Bug ID | Attribute | Correct decode | Current build_db.py behavior | Phase 57 fix |` and DATA-06 is not a bug — forcing a row would misfile it. `151-07` instead requires one explicit concluding sentence in the new section, which satisfies D-13's "feeds that file's summary" without inventing a column.

---

## Sources

### Primary (HIGH confidence — read from the tree this session, `[FILE …]`)
- `firestarter/scripts/baseline/size_baseline.json`, `…_base01.json` — all size/warning figures
- `firestarter/scripts/check_size_baseline.py` — band literals, allowance resolvers, compare functions, main()
- `firestarter/tests/test_check_size_baseline.py` + `firestarter/tests/fixtures/*` — 14 legs, all fixture families and values
- `firestarter/include/firestarter.h`, `firestarter/src/firestarter.cpp` — CMD enum, parse gate, `is_memory_cmd`, dispatch switch
- `firestarter/include/flash_utils.h`, `firestarter/src/proms/flash_utils.cpp`, `flash_nor_unlock.cpp`, `flash_5v_page.cpp`
- `firestarter/src/hardware_operations.cpp` — query-command templates
- `firestarter/include/rurp_pinmap_guard.h`, `firestarter/test/native/avr/test_cmd_admission/*`, `test_pinmap_provisional/*`
- `firestarter/platformio.ini`, `firestarter/doc/PROTOCOLS.md`, `firestarter/CLAUDE.md`
- `firestarter/.github/workflows/{build,beta-build}.yml`, `firestarter/scripts/check_build_warnings.py`
- `firestarter_app/firestarter/{sdp_capability,sdp_honesty,channel,constants,database,chip_resolver,serial_comm,eprom_operations,cli_handlers}.py`
- `firestarter_app/firestarter/data/chip_database.json` — every count
- `firestarter_app/tools/{check_sdp_capability_invariants,check_is_memory_cmd_no_ifdef,check_mypy_watermark,build_db,derive_sdp_partition}.py`
- `firestarter_app/tests/{scan_paths,test_dev_group_channel_gating,test_dev_tools_channel_gate,test_click_group_gate_hook,test_dev_gate_reads_no_firmware_source,test_sdp_honesty,test_sdp_db_invariant,test_b15_page_size_corroboration,test_check_sdp_capability,test_lockable_proms_doc_claims,test_boot_block_hint,test_characterization,test_val_wire_5v_page,test_revision_constants_parity}.py` + `tests/__snapshots__/test_characterization.ambr`
- `firestarter_app/doc/{lockable-proms,infoic-field-dictionary,package-details,protocol-flags}.md`
- `firestarter_app/pyproject.toml`, `firestarter_app/.github/workflows/ci.yml`, `firestarter_app/CLAUDE.md`
- `tools/catalog/{messages.toml,codegen.py,sync_to_subrepos.sh}` (meta)
- `.planning/{ROADMAP,REQUIREMENTS,STATE,config.json}.md`, `.planning/phases/151-…/151-CONTEXT.md`, `.planning/seeds/lock-status-command-hand-curated-protection-table.md`, `.planning/notes/infoic-xml-protection-flags-research.md`, `.planning/todos/pending/decode-infoic-flags-bits-14-15-protect-metadata.md`

### Secondary (MEDIUM — measured by command this session, `[CMD …]`)
- `python3` heredocs over `chip_database.json` (row/algorithm/field/token counts, the `0x34` row, the promotion split, the doc-token coverage matrix)
- `python3` heredoc over `platformio.ini` (per-env `test_filter` sizes, suite/env/CI set differences)
- `python3` + `tomllib` over `tools/catalog/messages.toml` (76 messages, per-band free-id map)
- `python3` table-row counter over `doc/lockable-proms.md` (126 family rows by section)
- `grep -E "^(RAM|Flash):"` over all live size fixtures
- `git ls-files`, `git log --oneline`, `md5sum`, `wc -l`, `ls`, `which python3`

### Secondary — the pinned upstream `infoic.xml` (MEDIUM-HIGH; machine-readable, re-derivable)
- `https://gitlab.com/DavidGriffith/minipro/-/raw/a8efaedc236c1d9718bd28299dfbb99536b010ff/infoic.xml`
  — 17 861 009 bytes, fetched this session via the mechanism
  `firestarter_app/tools/derive_sdp_partition.py` `_load_infoic_xml()` (`:74-83`) /
  `MINIPRO_XML_URL` (`:60-64`) already uses, at the same revision the project
  cites throughout. Parsed with `xml.etree.ElementTree`, section
  `.//database[@type='INFOIC2PLUS']` (the section `build_db.py:454` reads).
  Measurements taken: full `<ic>` attribute census; child/text census; `config`
  value distribution; per-protocol value sets for all eight unused fields;
  `chip_info` cluster analysis; a magic-byte regex over every attribute value of
  all 11510 entries; verbatim dumps of the `W29C020*`, `W29C040*`, `W29EE011`,
  `AM29F040`, `SST39SF040` and `W49F020` entries. **Nothing was written into either
  repository.**

### Tertiary (LOW — not verifiable in this repository)
- Datasheet-level protection claims in `doc/lockable-proms.md` and its 8 external references (Infineon, Macronix, Microchip PDFs) — `[CITED]`, see A5
- minipro `database.c` bit semantics @ `a8efaedc` — cited by permalink in the field dictionary and the folded todo; `infoic.xml` itself is gitignored and uncommitted — `[CITED]`, see A4
- The `SA + 0x02` Autoselect offset and the W29C020C Product-ID status address — `[ASSUMED]`, see A1/A2

**No external search or documentation-fetch provider was used, and no datasheet PDF
was fetched or added to any repository.** The one external artifact retrieved was
the pinned upstream `infoic.xml`, on operator direction and through the project's
own existing reproducible loader. Two questions remain **not** answerable from any
source available here — the `SA + 0x02` offset and the Product-ID status
address/decode — and stay recorded as `[ASSUMED]` (A1, A2) rather than answered
from training data dressed as fact; the inability to read the tracked candidate
PDFs is recorded as **A8** rather than papered over.

---

## Metadata

**Confidence breakdown:**
- **Live firmware size figures & MERGE-05 arithmetic:** HIGH — read from two committed baselines and the checker's literals, with the arithmetic re-derived and cross-checked against every planted fixture's actual `Flash:`/`RAM:` line.
- **DB counts (all of D-09 and D-14):** HIGH — computed this session; every quoted figure verified; the two discrepancies found (the 405-vs-406 enumeration, the 2 key-less rows) are stated with their causes.
- **Firmware wire-protocol facts:** HIGH for what exists (enum, gates, dispatch sites, mirror sites, message bands); LOW for byte costs of what does not (labelled `[ESTIMATE]`).
- **Read sequences:** MEDIUM overall. The reusable primitives are HIGH (quoted in full). The **negative** result — that `infoic.xml` carries no sequence data — is **HIGH**: it rests on an exhaustive attribute census, a magic-byte scan over every attribute value of all 11510 entries, and `config="NULL"` on all 998 relevant entries. The sequences themselves remain `[ASSUMED]` (A1, A2) and must come from a datasheet, which caps them at *pinnable*, never *provable*.
- **Host patterns and gate wiring:** HIGH — every file, line, assertion and invocation path read directly, including the non-obvious finding that the invariant gate runs via pytest and not via a CI step.
- **`lockable-proms.md` transcription surface:** HIGH on structure and counts (126 rows, the Key/row vocabulary mismatch, the token-coverage matrix); MEDIUM on the datasheet verdicts themselves.
- **Test/CI environment:** HIGH — workflows, extras, watermarks, select lists and env/suite mappings all measured; the six-suites-outside-CI and markdown-fires-no-CI findings are new.
- **Contradictions:** HIGH — **19** found (C-1 … C-19; C-17/C-18/C-19 added 2026-08-20 with the operator's `W29C020` and the infoic/datasheet sweep), each with both sources named and the measurement that separates them.

**Research date:** 2026-08-20 (initial sweep + a same-day follow-up answering two
operator inputs: the `W29C020` in inventory, and the direction to check
`infoic.xml` for the sequences before the datasheet)
**Tree state:** meta `8e90dbf5` · firmware `8286916` (a7w landed) · app `9cc57c7`; all three on `gsd/v1.32-at28c-write-path-root-cause-report-provenance`
**Valid until:** ~2026-09-03 (14 days) for the host/doc facts. **The firmware size
figures expire the moment any firmware commit lands** — re-read both baselines
before sizing an exemption. `chip_database.json` counts expire on the next
`build_db.py` regeneration.













