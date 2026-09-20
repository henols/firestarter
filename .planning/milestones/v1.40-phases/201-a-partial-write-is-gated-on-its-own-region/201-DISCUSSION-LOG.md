# Phase 201: A partial write is gated on its own region - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-19
**Phase:** 201-a-partial-write-is-gated-on-its-own-region
**Areas discussed:** Where the region end comes from, Shape of the firmware seam, Which call sites are in scope, What carries the bench proof

---

## Area selection

| Option | Description | Selected |
|--------|-------------|----------|
| Where the region end comes from | Host narrows `memory-size` vs. a new wire field vs. firmware-only `[address, mem_size)` | ✓ |
| Shape of the firmware seam | Region impl + wrapper vs. file-scope statics vs. a separate scan loop | ✓ |
| Which call sites are in scope | `eprom.cpp` only vs. all three write-init sites | ✓ |
| What carries the bench proof | True UV part vs. an erasable part with `--skip-erase`; gating vs. following | ✓ |

**User's choice:** All four.

---

## Todo cross-reference

| Option | Description | Selected |
|--------|-------------|----------|
| `2026-08-30-write-init-blank-check-is-whole-device` | Backlog 999.44 — this IS the phase | ✓ |
| `2026-09-08-uv-write-shortcut-disclosure-key` | `dev test` passes where `write -a` is refused; this phase removes the premise | ✓ |
| Neither — leave both pending | Handle todo disposition at milestone close instead | |

**User's choice:** Both folded.
**Notes:** `2026-06-24-skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads` scored highest on
keyword match but was reviewed and not folded — it concerns `read` and standalone `blank-check`,
operations that do not drive VPP, whereas a write does. Recorded in CONTEXT.md under Reviewed Todos.

---

## Where the region end comes from

### Q1 — the mechanism

| Option | Description | Selected |
|--------|-------------|----------|
| A new wire field | `page_size`-shaped: a `FIELD` entry, a handle member, `0 = absent`, fails safe in both directions. Costs constants parity across `constants.py` and three firmware headers. | ✓ |
| Host narrows `memory-size` on write | Reuses the mechanism already at `eprom_operations.py:495`. No new protocol surface — but overloads `memory-size`, and `eeprom28c_check_chip_id` derives a 12 V A9 address from it. | |
| Firmware-only `[address, mem_size)` | One repo, ~0 flash, no wire change. But `uv_slot_starts` is top-down, so `dev test`'s second slot is still refused, and it is not "the region being written". | |

**Notes:** The deciding measurement came before the question: `handle->data_size` is written only in
MAIN (`op_get_message`'s `'#'` arm), and INIT runs strictly before MAIN — so no firmware-only option
can know the region. The 12 V/A9 hazard in the `memory-size` option was found by reading
`eeprom_28c.cpp:190` and `:343` during scouting, not raised speculatively.

### Q2 — absent semantics

| Option | Description | Selected |
|--------|-------------|----------|
| Whole device — today's behaviour | Byte-identical to today; inverts `page_size`'s absent=refuse deliberately | ✓ |
| Refuse — match the `page_size` precedent | Consistent, but breaks every old host and refuses what works today | |
| Fall back to `[address, mem_size)` | Useful without a host change, but a third semantic for one field | |

### Q3 — when it is sent

| Option | Description | Selected |
|--------|-------------|----------|
| Every write | One code path. A short file to a big part stops blank-checking bytes it will not touch. | ✓ |
| Only when `--address` is given | Conservative; only the reported case changes. Costs a host-side branch. | |

### Q4 — what it bounds

| Option | Description | Selected |
|--------|-------------|----------|
| The blank check only | Smallest blast radius; `mem_size` keeps all its current jobs | |
| Also bound the write loop and progress | More coherent, but moves four behaviours at once | ✓ |

**Notes:** Chosen against the stated recommendation. Verified cheap afterwards rather than assumed:
`_apply_write_progress` already discards the frame's total, so the operator-visible bar does not
move. A follow-up correction during citation repair found that **three** distinct
`MSG_DATA_PROGRESS` denominators exist, only one of which this decision may touch — the other two
belong to the standalone blank-check command and to the shared scan, and BLANK-02 protects the first.

### Q5 — verify

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — send it on verify too | Write and verify agree on bounds by construction; implies naming it `region-size` | ✓ |
| No — verify sends 0 and falls back to `mem_size` | Verify unchanged, but write and verify then disagree on where the operation ends | |

---

## Shape of the firmware seam

| Option | Description | Selected |
|--------|-------------|----------|
| Region impl + whole-device wrapper | `mem_util_blank_check_region(handle, start, end)` holds the scan; the old signature becomes a one-line `(0, mem_size)` call | ✓ |
| Second entry point, shared static helper | Exported whole-device symbol untouched by construction; three symbols where one would do | |
| Read `handle->region_size` in place | Cheapest, and a `handle->cmd` branch already exists in the scan — but it is the edit in place the todo rules out | |

**Notes:** The chunking mechanics turned out to favour the chosen shape: on the write-init path
`blank_check_saved_address` and the region start are the same value, so the region form is literally
"do not reset the cursor to 0, and stop at `end`".

### BLANK-02's proof — delegated

| Option | Description | Selected |
|--------|-------------|----------|
| Native: multi-chunk resumption | A part larger than `BLANK_CHECK_CHUNK_SIZE` through `CMD_BLANK_CHECK` across several calls | Claude |
| Native: erase-end check unchanged | `eprom.cpp:53`'s END arm with an erasable part, asserting it still scans from 0 | Claude |
| Golden trace diff | Cheap, but the todo warns the stubs record no time and miss register-write elision | ✗ |
| Source-contract gate | A `tests/*.py` scan that the whole-device entry still passes `(0, mem_size)` | Claude |

**User's choice:** "you decide".
**Claude's decision:** the two native legs plus the source-contract gate. The golden trace diff is
explicitly **not** a carrier here — the todo's own closing line rules it out. The branch-inventory
golden must still be re-derived, but as an obligation this phase incurs, not evidence it produces.

---

## Which call sites are in scope

| Option | Description | Selected |
|--------|-------------|----------|
| `eprom.cpp` only | The one site where the defect is live; the other two are behind `FLAG_CAN_ERASE` | ✓ |
| All three write-init sites | Consistent, but costs two more protocol files and bench coverage this phase has no budget for | |
| `eprom.cpp`, and delete the other two | Follows the precedent `eeprom_28c.cpp:379` and `flash_5v_page.cpp:74` set twice — but a deletion nothing in BLANK-01..03 asks for | |

### Is the latency recorded?

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — state it as a named non-claim | `--skip-erase` reaches the identical refusal on every erasable part, including the three validated flash parts | ✓ |
| No — out of scope, leave it unsaid | BLANK-01 is worded around non-erasable parts | |

---

## What carries the bench proof

### Q1 — silicon

| Option | Description | Selected |
|--------|-------------|----------|
| TMS27C512, plus W27C512 as the rehearsal | Erasable part rehearses RED→GREEN repeatably; one confirming run on a genuinely `can_erase == false` part | ✓ |
| TMS27C512 alone | No proxy to explain, but every iteration burns a region of a UV part | |
| W27C512 + `--skip-erase` alone | Cheapest and repeatable, but criterion 1 would rest on a proxy argument | |

**Notes:** The erase axis was measured at `database.py:577-579` rather than assumed —
`FLAG_CAN_ERASE` is set from `electrical-type ∈ {EEPROM, Flash/EEPROM}` and `algo != 5`, nothing
else. AM27C020 was ruled out despite being the part in the original transcript: v1.18 recorded its
write path as effective-but-marginal (60/64 bytes, then 0/64), so a result on it would be
uninterpretable.

### Q2 — gating

| Option | Description | Selected |
|--------|-------------|----------|
| Bench gates the phase | The silicon is on hand and validated; there is no missing part to wait for | ✓ |
| Follow it, PAGE-03 / D-11 shape | The shape v1.39 used — but that was forced by a `W29C512` nobody had | |

### Q3 — BLANK-03's test siting — delegated

| Option | Description | Selected |
|--------|-------------|----------|
| Native: non-blank, `can_erase == false` part | The test whose absence the todo names; runs in CI on both native envs | Claude |
| Host: the `write -a` path end to end | The product-level bug from the todo's consequence 1 | Claude |
| Host: constants + wire parity | CLAUDE.md's obligation for anything duplicated across the two repos | Claude |
| A committed bench transcript | Evidence, not a test — cannot re-run in CI | Claude |

**User's choice:** "you decide".
**Claude's decision:** all four, with the fourth labelled evidence rather than a test. One caveat
surfaced while deciding: `fake_chip._is_blank()` compares the whole buffer against
`0xFF * memory_size`, so the host leg passes vacuously unless the fake learns the region — and
`test_uv_mask.py:201` leans on the fake's current behaviour, making that a coupled edit.

---

## Claude's Discretion

- BLANK-02's proof mechanism (Q, area 2) — decided as the two native legs plus a source-contract
  gate, explicitly excluding the golden trace diff.
- BLANK-03's test siting (Q3, area 4) — decided as all four artefacts, the bench transcript labelled
  as evidence.
- The wire key's spelling and unit, the firmware member's type, where `_setup_operation` computes it.
- Where the region-scoped call sits inside `eprom_internal_write_init_body`, provided the single-exit
  HV wrapper still sees every exit.
- Test file names and fixture shapes, provided the native leg is *seen* RED before the fix lands.

## Deferred Ideas

- Region-scoping `flash_intel.cpp:95` and `flash_nor_unlock.cpp:105` — one `--skip-erase` deep, so a
  real follow-up rather than a theoretical one.
- Deleting those two write-init blank checks outright, following the twice-set precedent.
- Retiring `_apply_write_progress`'s total-discarding workaround, whose reason this phase removes.
- Extending the new field to `CMD_READ`, replacing the `memory-size` overload at
  `eprom_operations.py:495`.
- Re-anchoring a firmware size baseline — there is no size gate in CI any more.
