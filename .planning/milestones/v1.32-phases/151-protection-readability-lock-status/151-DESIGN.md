# Phase 151: Protection Readability — Design Decisions

**Status:** Landed 2026-08-20, Plan 151-01, Task 2.
**Authority:** This file is the phase's single source of truth for every discretionary
decision listed under CONTEXT.md's "Claude's Discretion" section, plus the corrected
class census (OD-2) and the C-17 tiebreak mechanism. Plans 151-03, 151-06, 151-08,
151-11, 151-12 and 151-13 cite this file rather than re-deciding any of it.

Each section states the decision, the measured facts it rests on, and the alternatives
rejected — the same shape CONTEXT.md's decision blocks use.

---

## §1 Wire shape (CONTEXT.md discretion item 1)

**Decision.** New command `CMD_LOCK_STATUS = 16` in `firestarter/include/firestarter.h`
(the `CMD_*` block currently ends at `CMD_HW_VERSION` 15), with a host mirror
`COMMAND_LOCK_STATUS = 16` in `firestarter_app/firestarter/constants.py` plus a
`COMMAND_NAMES[16]` entry. The response is a two-byte DATA id-frame emitted with the
already-existing `LOG_DATA_ID_BYTES` macro (`firestarter/include/logging_id.h:164`)
under one new catalog id `MSG_DATA_PROTECTION_STATUS`, allocated in the DATA band
(0xE0–0xFF, 26 free ids measured in RESEARCH.md's free-message-id table).

Byte 0 is the raw byte read from silicon, unmodified. Byte 1 is a firmware decode code:
`0x00` reads-as-unprotected, `0x01` reads-as-protected, `0xFF` indeterminate/not-obtainable
— reusing `hw_get_version`'s established `0xFF` sentinel convention
(`firestarter/src/hardware_operations.cpp:104-113`, `P-02 sentinel: no override active`).

**Why the raw byte rides the wire.** D-03's probe legs must record the raw result either
way — a plausible locked-boot-block reading corroborates v1.17 from the read side, and
garbage vindicates the table's variant-dependent refusal — so a wrong decode must not
destroy the observation. Shipping only the decode byte would make a firmware decode bug
unrecoverable from the host side; shipping the raw byte too means the host (or a later
debug session) can always re-derive the decode independently of what firmware concluded.

**Rejected, each with its measured reason:**
- **Extending `MSG_OK_READY`.** Zero codegen (RESEARCH.md "Does a new message ID require
  codegen?" §Option 3 confirms the variable-length-blob mechanics), but it is the
  operation-setup ack emitted on every operation and every voltage read
  (`hardware_operations.cpp:43`, `dev_tools.cpp:107`/`:153`), so every command would pay
  the bytes and every ack would carry a protection claim.
- **`LOG_DATA_ID_U16x4` per-region framing.** There is no sector map anywhere in this
  project — `flash_nor_unlock_sector_erase` takes a caller-supplied address, not a
  region index — so a per-region answer has no data source.
- **A new ERROR-band id.** The ERROR band has exactly one free id, `0xBF`
  (RESEARCH.md's free-message-id table: 31 of 32 ERROR slots used), and no documented
  band-extension procedure, so it is not spent here.

---

## §2 Scope of the answer (discretion item 2)

**Decision.** Device-global, not per-sector or per-region.

**Measured reasons.** No sector map exists in this project (see §1's rejected per-region
framing). And `_BOOT_BLOCK_SIZE = 0x4000` was derived for the W29C040 hint while
`lockable-proms.md:21` documents W29C020/W29C020C as having 8 KB boot blocks — reusing
that constant on a `0x05` part would be a fabricated geometry claim DATA-04's proof rule
forbids.

**Consequence.** A device-global answer needs no geometry at all. Under D-08 a
device-global answer renders as one leading class token with no multi-region
reconciliation to specify — the multi-region rendering question CONTEXT.md's discretion
item 2 raised does not arise.

---

## §3 Exit-code map (D-10)

**Decision.** A literal `str -> int` dict in `lock_status.py`'s `EXIT_BY_CLASS`, never a
`max()` over severities — this codebase already carries an exit-code precedence defect
where `max()` picked the wrong verdict (D-10's own rejected-alternative note).

Four codes over eight classes:

| class token | exit code |
|---|---|
| `protected` | 0 |
| `unprotected` | 0 |
| `not_readable` | 2 |
| `not_implemented` | 2 |
| `undocumented_alias` | 2 |
| `no_mechanism` | 2 |
| `firmware_outdated` | 3 |
| comms failure | 3 |
| `unadjudicated_probe` | 4 |

Exactly four distinct codes are used: `{0, 2, 3, 4}`. Code `0` is assigned to exactly
`protected` and `unprotected` — the only two classes backed by a real silicon read.

**Why the fourth code exists.** D-10 assigns 0 to a real state, one non-zero to "cannot
answer", and a separate non-zero to operational failure — and places `unadjudicated_probe`
in none of the three. It is not a state (D-07: never a state claim), not a refusal (the
sequence ran), and not a failure. A fourth band is therefore the honest reading. D-10's
rejected alternative was per-class codes throughout every one of the eight classes, which
four codes over eight classes plainly is not — most classes still share a code, only the
one genuinely distinct case gets its own.

**Test discipline.** Tests assert token and code together, never the code alone — a bare
exit code of `2` is ambiguous across four different classes, so any test that checks only
`$?` without also checking the printed class token is not testing D-10's actual guarantee.

---

## §4 The corrected class census (OD-2)

**Decision.** Algorithm `52` — the single `XICOR/X88C64P,X88C64S` row
(`support_status: "protocol-not-implemented"`, `protect_off_before: true`) — resolves to
`not_implemented`, not `no_mechanism`.

**Reasoning.** D-09's seven named no-mechanism algorithms (UV-EPROM `0x07`/`0x08`/`0x0B`,
SRAM/NVRAM `0x0E`/`0x27`/`0x28`/`0x29`) sum to `170 + 127 + 32 + 20 + 2 + 34 + 20 = 405`,
not 406 — RESEARCH.md's "D-09's claimed partition — verified, with one hole" measured this
exactly. This `0x34` row lands in no class under D-09's prose as written. Classing it
`no_mechanism` would assert an absence of mechanism that upstream's
`protect_off_before: true` directly contradicts — the fabricated claim LOCK-03/LOCK-04
forbid. `not_implemented` is the honest reading: no code in this project can read this
chip's protection state (its handler is `configure_not_implemented()`, per
`firestarter/doc/PROTOCOLS.md:70`), and using the same token `0x10` already uses
(documented-readable-but-unimplemented is a different reason for the same token's
umbrella meaning: "known to have or lack readability, but this codebase does not read it")
preserves D-09's 8-class freeze without inventing a ninth token.

**Consequence to pin as literals in the D-12 test** — this supersedes VALIDATION.md's
figure of 39 for `not_implemented`:

`not_implemented` = **40** (39 rows at `0x10` plus this one `0x34` row).

**Full census to pin**, summing to the full 746-row database:

- `no_mechanism` — **405**
- `not_implemented` — **40**
- `not_readable` — **at least 84** (the `0x0D` rows; some of the 217 `0x05`/`0x06`
  rows below also land here after curation)
- the **217** `0x05` (27 rows) + `0x06` (190 rows) rows, distributed across
  `read_permitted` / `not_readable` / `undocumented_alias` with the exact split fixed by
  the curation done in Plan `151-02`

`405 + 40 + 84 + 217 = 746`.

---

## §5 The C-17 tiebreak — a mechanism, not a judgement

**The problem, measured.** `lockable-proms.md`'s row key at `:21` is
`**W29C020 / W29C020C**` and covers both parts, but all four restatements outside the
table (`:25`, `:30`, `:335`, `:350`) name `W29C020C` only, and bare `W29C020` appears
exactly once in 399 lines — the `:21` row key itself. Neither reading is safe, and D-06's
three states have no slot for "documented, but the summary declines to repeat the
verdict".

**The mechanism, stated as a rule rather than resolved per entry:**

(a) D-06's three readability states are **NOT** extended — the token set stays
`documented-readable` / `documented-not-readable` / `undocumented`.

(b) A named module-level tiebreak rule applies: where the source document's table row and
its restatements disagree about a token, the token takes the **more restrictive** state.

(c) The disagreement itself is recorded, not erased, in a reporting-only
`AMBIGUOUS_DOC_CITATIONS` mapping whose value carries both readings' exact line
references, and the refusal reason surfaces it.

(d) A dedicated test leg asserts the mapping is non-empty and that bare `W29C020` is one
of its keys.

So bare `W29C020` curates to `documented-not-readable` **by rule**, not by a curator's
adjudication.

**Why this is consequence-free for the worked example.** The `W29C020,W29C020C,W29C022`
DB entry refuses under D-06 regardless of how C-17 resolves, because `W29C022` appears
nowhere in `lockable-proms.md` — so the tiebreak changes only the *number of named
offending aliases* in the refusal (one vs. two), never the entry's verdict.

**C-18, recorded alongside.** All three aliases — `W29C020`, `W29C020C`, `W29C022` — are
one upstream `<ic>` entry with one `chip_id="0x0000da45"`, so a per-alias distinction is
unobservable on the wire anyway: whatever C-17 resolves to, firmware cannot tell which of
the three parts is in the socket.

---

## §6 `--force` does not reach the wire (C-16)

**Decision.** D-07's `--force` is a host-side bypass of a **table** refusal, never a
firmware flag on this command.

Firmware's `FLAG_FORCE` (`0x01`) means one specific thing — downgrade a chip-ID mismatch
from error to warning — and the lock-status read performs no chip-ID check, so the bit is
not set on this command's frame.

**Consequence, stated plainly.** On `dev lock-status`, `--force` has no firmware-visible
effect whatsoever. A test asserts the flags word sent for `lock-status` is byte-identical
with and without `--force` — the flag only ever changes host-side behavior (whether the
table refusal is bypassed to run the unadjudicated probe sequence at all).

---

## §7 The debug-output consequence of OD-3, stated as a choice

**Fact, measured.** `is_memory_cmd()` (`firestarter/include/firestarter.h:133`) currently
lists exactly eight cases: `CMD_READ`, `CMD_WRITE`, `CMD_ERASE`, `CMD_BLANK_CHECK`,
`CMD_CHECK_CHIP_ID`, `CMD_VERIFY`, `CMD_SDP_UNLOCK`, `CMD_SDP_LOCK`. `CMD_LOCK_STATUS`
becomes a ninth case, admitted to `configure_memory` the same way the existing eight are.

The second ordinal range at `firestarter/src/firestarter.cpp:132-142` gates three `DBG_*`
diagnostic lines (`DBG_MEM_SIZE`, `DBG_ADDR_MASK`, `DBG_MATCH_LINES`) on
`handle->cmd > CMD_IDLE && handle->cmd < CMD_READ_VPP` — and its own comment records that
it was deliberately **not** converted to `is_memory_cmd()` because it "gates diagnostic
output only". It is left unchanged by this phase.

**Consequence, chosen rather than discovered on the bench.** `CMD_LOCK_STATUS = 16` is
numerically greater than `CMD_READ_VPP` (11), so it falls outside that diagnostic ordinal
range. `dev lock-status` therefore emits **no** `DBG_*` diagnostic output. Record that the
admission set at the safety gate (`is_memory_cmd()`) grew from 8 commands to 9 while the
diagnostic ordinal range did not move at all.

---

## §8 The evidence ceiling for this phase, in the words later artifacts must reuse

Both the `0x06` Autoselect sequence and the `0x05` Winbond boot-block sequence are
datasheet-derived — `infoic.xml`'s `config` field is the literal string `"NULL"` on all
101 `0x05` and all 897 `0x06` entries, so neither sequence has a machine-readable oracle.
The strongest available test is a pinned literal byte table plus a citation comment
(`vendor / document / revision / page / §section`), and that is **a change detector, not a correctness proof**.

The `0x06` Autoselect read ships **software-proven and unrun on silicon** — no bench leg
for it exists anywhere in this phase's plans.

The `0x05` read is exercised only through D-07's `--force` probe path on the operator's
W29C040, and no artifact may claim the sequence is silicon-validated on the strength of
that one gated leg — the leg is a PROBE, not validation (D-03).

Nothing here claims AT28C or `0x0D` silicon validation — this phase adds no `0x0D` read
path at all. And nothing here closes the v1.17 W29C040 RCA, which asked for a second
W29C040 sample; the operator's single W29C040 bench leg is at most partial corroboration
from the read side, never closure.

No section of this file asserts that either sequence is correct or validated.
