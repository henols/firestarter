# Phase 194: Real Page Size Reaches the Firmware - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-15
**Phase:** 194-real-page-size-reaches-the-firmware
**Areas discussed:** Absent page-size fallback, Where the 27 values come from, How PAGE-02 gets measured, Bench coverage for PAGE-03

---

## Absent page-size fallback

### Opening question — the operator redirected it

**Asked:** what the firmware does when `page-size` is absent or 0 on a `0x05` write, offering
refuse / keep deriving / derive-and-warn.

**Operator's response (free text):** *"isent the page size in the infoic, check in beta if its
fixed"*

**What was checked before answering:**

1. **Is the page size in infoic?** Yes. All 27 `algorithm: 5` rows carry
   `programming.infoic_page_size_raw`. Phase 149 measured that field as a faithful copy of the
   upstream XML — zero mismatches across all 84 `0x0D` rows — so there is no decode bug here, only
   a question of which rows it means something for.
2. **Is it already fixed on `beta`?** No. `git diff HEAD origin/beta` is **empty** for
   `firestarter_fw/src/proms/flash_5v_page.cpp`, `firestarter_app/tools/build_db.py` and
   `firestarter_app/firestarter/data/chip_database.json`. `origin/beta`'s database has 27
   `algorithm: 5` rows with 2 carrying `page_size`, identical to the working branch.

This redirect changed the question: because the value is genuinely present for all 27, "absent"
stops being the normal case and becomes an edge case — an old host or a hand-edited
`~/.firestarter/database.json`.

### Fallback shape (re-asked with that framing)

| Option | Description | Selected |
|--------|-------------|----------|
| Refuse — no page size, no write | Fail closed with a named error. Removes `flash_5v_page_page_size()` entirely. Matches the `0xBB` fail-closed dispatch precedent. Cost: new firmware + old host loses `0x05` writes for all 27. | ✓ |
| Keep deriving as a fallback | Nothing regresses for a stale host. Cost: the derivation survives in the binary and a stale-host user still gets `successful` over a destroyed page. | |
| Derive + warn | Fall back but emit a WARNING naming the derived value. Cost: a message id against the Leonardo ceiling. | |

**Notes:** the argument that settled it — a wrong page size is not a degraded mode in either
direction, so a fallback has no safe value to fall back to. Too small commits twice into one
physical page. Too large lets the device auto-commit mid-load past the firmware's poll point.

### Where the refusal is enforced

| Option | Description | Selected |
|--------|-------------|----------|
| Both — host pre-flight + firmware | Host refuses before any serial byte (v1.12/v1.20 precedent), firmware refuses independently. | ✓ |
| Firmware only | One enforcement point, no host change. Cost: the user meets a raw error id after a serial round-trip. | |
| Host only | Listed so the rejection is on the record — leaves the corrupting path live for any other caller. | |

### New host + OLD firmware skew

| Option | Description | Selected |
|--------|-------------|----------|
| Gate — refuse below a known-good version | Closes the last silent-corruption path. Cost: `_probe_port` truncates prerelease suffixes, so the boundary must sit where the numeric part alone is decisive. | |
| Warn but proceed | Keeps old firmware usable for the 18. Cost: still a write that can report success over erased bytes. | |
| Out of scope — file it | Note the skew, file it, let dual-repo lockstep carry the pair. | ✓ |

---

## Where the 27 values come from

| Option | Description | Selected |
|--------|-------------|----------|
| Extend the provenance arm to `0x05` | One-line generator change beside the existing curated table. | |
| Curate all 27 from datasheets | 27 `[CITED:]` entries. Cost: 149's D-02 said the table is "not extended", the repo has 2 of the 27 PDFs. | |
| Host reads `infoic_page_size_raw` | No DB regeneration. Cost: leaks the raw provenance axis onto the wire for every algorithm. | |

**Operator's choice (free text):** *"no curated rows, the build_db.py must reflect the ground truth
from infoic and generate the database after the truth"*

**Notes:** this is stronger than the option offered — it removes `_PAGE_SIZE_BY_PART` outright
rather than adding an arm beside it. Verified output-neutral before locking: the table holds
exactly 2 entries, both `0x05`, both already equal to their raw value. Also surfaced before
locking: three live gates pin the current shape and must move deliberately —
`test_vcc_margin_rail.py:245` (asserts the dict has exactly 2 entries),
`test_page_size_invariants.py` (asserts exactly 20 carriers), and
`tests/golden/chip_database_field_inventory.json` (records that 20).

### Keying — provenance or flat

| Option | Description | Selected |
|--------|-------------|----------|
| Keep provenance keying, add `0x05` | Emit when the row's OWN upstream `protocol_id` is `0x0D` or `0x05`. The 66 promoted `0x0D` rows stay omitted. 20 → 45 carriers. | ✓ |
| Flat — emit raw for every row | Maximally "reflects infoic". Cost: 31 promoted rows would get `page_size` 1, and two FRAM parts would get a page size for a device with no page buffer. Reverses D-01/D-04. | |
| Provenance keying, `0x05` only | Same outcome as the first — listed to make explicit that no `0x0D` behaviour changes. | |

### Generator assertion

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — fail-closed, abort the build | Raise and write no database if an emitted `page_size` is not a power of two in range. Same shape as `interpret_timing`'s fatal. | ✓ |
| Yes — but warn, don't abort | Degrades a bad value to "absent", which under the refusal decision means that chip stops writing silently. | |
| No — leave it to the tests | Cost: the bad database exists on disk before anything objects. | |

**Notes:** costs nothing today — all 45 emitted values are already 64/128/256/512.

---

## How PAGE-02 gets measured

| Option | Description | Selected |
|--------|-------------|----------|
| Host data test + native consumption test | 27-row host table (correct-for-9 and unchanged-for-18 both measured) plus a native test driving `flash_5v_page_write_execute` over 27 pairs. Zero flash. | ✓ |
| Add the firmware INFO log too | The `resolves_phase: 194` todo. Makes bench and `dev test` transcripts self-describing. Cost: a message id against the Leonardo ceiling. | |
| Host data test only | Cheapest. Cost: measures what the host sends, never what the firmware uses — the exact gap that let this defect live. | |

**Notes:** the deciding observation — the host has been sending a correct `page-size: 128` on every
`w29c020` write all along and the firmware discards it, so a host-only test would have passed
throughout the defect's entire life. The INFO-log todo is left pending and unmodified.

---

## Bench coverage for PAGE-03

### Inventory

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — I'll name which | PAGE-03 met head-on. | |
| No — none of the 9 | Ship the database measurement + a no-regression run on one of the 18, record 0-of-9 honestly. | |
| Not sure — need to check the drawer | Planner builds the bench plan but gates it. | |
| No, but I can order one | Hold PAGE-03 open pending arrival. | ✓ |

**Notes:** measured first — all 9 are DIP32, `DIP32_SST39SF040`, 12 V VPP / 5 V VCC, all already
`supported`, none 8 Mbit, so no adapter and no JP5/A19 cut hazard. Every `0x05` part with bench
history on this rig sits in the correct 18.

### Which part to order

| Option | Description | Selected |
|--------|-------------|----------|
| W29C512 (recommended) | Same Winbond `W29C` family as the two `0x05` parts already bench-proven here, so the page size is the only new variable. 64 KB, writes fast. | ✓ |
| AT29C040 | 512-byte page exactly equals the Uno's `DATA_BUFFER_SIZE` — the only one of the 9 where the physical page reaches the transfer-block size. | |
| Both | Family isolation plus the page/chunk edge case. | |
| AT29C020 | The part whose datasheet independently corroborated the raw page value. | |

**Notes:** name-collision hazard recorded — `W29C512` is a third distinct part from the bench's
existing `W27C512` and from `M27C512`. Check by chip-ID, never by the marking.

### Gating

| Option | Description | Selected |
|--------|-------------|----------|
| Land software, hold PAGE-03 open | Software + 27-row measurement + no-regression silicon run land now. The hardware leg closes on arrival. Phase 195 unblocked. | ✓ |
| Block until it arrives | Cleanest single record. Cost: Phase 195 stalls with it. | |
| Land software, close 194, re-open PAGE-03 as its own phase | Cost: marks a requirement Complete that its own criterion says needs silicon. | |

---

## Claude's Discretion

- **Where the 27-row record lives** — operator said "you decide". Chosen: a committed artifact under
  `.planning/v1.39/` (part · size · derived · real · verdict · evidence class), following the
  `.planning/v1.33/sweep-outcome-record.md` precedent, cited by `194-SUMMARY.md` rather than
  duplicated into it. Reasons: Phase 195 and the gh#67 reply both need to cite it, it survives the
  milestone archive, and it avoids the self-regenerating-golden hazard this project has met before.
- **Mask-vs-`%` implementation shape** and the **naming of the refusal error id** — left to research
  and planning.

## Deferred Ideas

- New-host / old-firmware version skew for `0x05` writes — file as a backlog item.
- The firmware INFO log naming the effective page size — stays pending, `resolves_phase: 194` intact.
- The same defect class in the other 12 protocols — file if found, do not fix here.
- The 11 promoted `0x0D` rows at raw 16/32 whose 64-byte floor safety is unproven — Phase 149's D-04.
