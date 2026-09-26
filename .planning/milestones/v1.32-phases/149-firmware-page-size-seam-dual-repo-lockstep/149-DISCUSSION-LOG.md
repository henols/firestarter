# Phase 149: Firmware Page-Size Seam (dual-repo lockstep) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-19
**Phase:** 149-Firmware Page-Size Seam (dual-repo lockstep)
**Areas discussed:** Delivery scope, Firmware trust boundary, Leonardo flash budget, Proof surface & honesty artifact

---

## Delivery scope

### Q1 — How much of the 84-chip `0x0D` family gets its real page size delivered?

| Option | Description | Selected |
|--------|-------------|----------|
| Verbatim — all 84 | 59 of 84 change granularity; framed as a defect fix for 42 | |
| Grow-only — deliver when raw > 64 | 17 chips change; 42 keep the floor | ✓ (superseded) |
| Verbatim, except floor raw==1 at 64 | 28 change; byte-write group keeps today's behaviour | |

**User's choice:** Grow-only — *and* a question back: "is the page buffer size represented in the
infoic.xml metadata?"
**Notes:** The question was answered from the repo, not from memory:
`doc/infoic-field-dictionary.md:241` carries a **CONFIRMED** `page_size` row cited to minipro
`database.c#L598` @ `a8efaedc` — "Page-write size for EEPROM/Flash. Typically 64 or 128 bytes for
28C-family; `0` or `1` if not applicable to the device type". Three corrections fell out: `1` is a
documented sentinel (so Claude's earlier "31 byte-write chips get a correctness fix" framing was
wrong); 16 and 32 are real values; and the 12/84 disagreement in
`test_b15_page_size_corroboration.py` impugns *bit 15*, not `page_size`. Claude also flagged that
growing is the only direction that can overrun a page, so grow-only concentrates the
unvalidated-metadata risk rather than avoiding it — and that shrink-only is unavailable because
ROADMAP criterion 1 requires a 128-byte entry observed to deliver 128.

### Q1b — Re-asked after that finding

| Option | Description | Selected |
|--------|-------------|----------|
| All real values, sentinels → fallback | 28 movers | |
| Grow-only | 17 movers | |

**User's choice:** Neither — "you have to investigate the infoic file if you can find a value that
correlates with the page sizes."
**Notes:** This instruction is what produced the phase's central finding. The pinned XML was
fetched (md5 `b4548e57c4f6c6c8c4f7387add03fa77`, byte-identical to a cached copy) and every
`<ic>` attribute examined. Answer: **no attribute corroborates `page_size`** —
`write_buffer_size` and `read_buffer_size` are programmer-side transfer buffers (AT28C256 reads
`wb=128` against a datasheet page of 64), and `pages_per_block` is `0` on all 84. But the
investigation surfaced something better: joining all 84 `algorithm: 13` rows back to the XML showed
**only 18 are upstream-native `0x0D`** — `classify()` arm 2 promotes the other 66 from `0x07`/`0x0B`
— and every page-size value outside the dictionary's documented 64/128 band comes from a promoted
row. Two prior framings were retired in the process: a whole-file XML scan miscounts (three
`<database>` sections; `build_db.py` reads `INFOIC2PLUS` only), and the DB's `algorithm` is not the
raw `protocol_id`.

### Q1c — Given the provenance table, what rule selects the chips?

| Option | Description | Selected |
|--------|-------------|----------|
| Upstream pid == `0x0D` only | 15 movers, all 64→128, all inside the documented band, both FRAMs excluded | ✓ |
| Grow-only, provenance ignored | 17 movers — adds two FRAM parts | |
| All real values, sentinels → fallback | 28 movers, 13 resting on uncorroborated promoted rows | |

**User's choice:** Upstream pid == `0x0D` only → **D-01**.

### Q2 — Which DB key carries the delivered value?

| Option | Description | Selected |
|--------|-------------|----------|
| Reuse `programming.page_size` | Zero host code change; wire field and golden key union already exist | ✓ |
| A new distinct key | Keeps the two provenances separately named; costs a host-side merge | |

**User's choice:** Reuse `programming.page_size` → **D-02**.

### Q3 — Emit the 3 rows already at 64?

| Option | Description | Selected |
|--------|-------------|----------|
| Emit all 18 | Presence means "provenance-corroborated"; no value condition | ✓ |
| Emit only the 15 that differ | Smallest wire diff; couples the emitter to a firmware constant | |

**User's choice:** Emit all 18 → **D-03**.

### Q4 — Disposition of the 66 promoted rows

| Option | Description | Selected |
|--------|-------------|----------|
| Named deferred item + correct the comment | Todo with part lists; rewrite the "errs SAFE" claim | |
| Named deferred item only | Smaller firmware diff | |
| Also flag the two FRAM misclassifications separately | Adds a second todo for `FM28V020` / `MB85R256H` | ✓ |

**User's choice:** All three deliverables → **D-04**. Claude additionally corrected its own earlier
"these 11 chips are overrun today" framing to "the floor's safety is **unproven** for them" — the
promoted rows' page sizes cannot establish their real page either.

---

## Firmware trust boundary

### Q5 — What does the handler do with a value it cannot trust?

| Option | Description | Selected |
|--------|-------------|----------|
| Cheap firmware fallback + host-side proof | Silent fallback; exhaustive 746-chip host assertion | ✓ |
| Validate and warn in firmware | Loud, but needs a codegen message ID against a 0-byte budget | |
| Trust the wire, mask only | Fewest bytes, no diagnostic | |

**User's choice:** Cheap fallback + host proof → **D-07**.

### Q6 — Does algorithm `0x05`'s handler consume the new key?

| Option | Description | Selected |
|--------|-------------|----------|
| No — `0x0D` only, stated as an explicit non-change | `flash_5v_page.cpp` stays FIX-04 frozen | ✓ |
| Yes — wire it into both handlers | Retires a heuristic; widens scope and flash cost | |
| No, and file it as a follow-up | Same, plus a todo | |

**User's choice:** No, `0x0D` only, recorded as an explicit non-change → **D-08**.

### Q7 — Where does "observed to deliver 128" live?

| Option | Description | Selected |
|--------|-------------|----------|
| Native test on flush cadence only | Zero firmware bytes; runs in CI | ✓ (revised) |
| Native test plus a runtime INFO log | Visible on hardware; costs a codegen message | |
| Native test now, log filed as a follow-up | Ship the CI proof, defer visibility | ✓ |

**User's choice:** Initially "native test only", then corrected mid-turn to also **file the runtime
log as a follow-up todo** → **D-09**.
**Notes:** The user interrupted with "wrong answer i need a follow up questions"; both halves were
honoured — the log became a filed follow-up, and the area continued with two more questions.

### Q8 — Naming of the 64 fallback constant

| Option | Description | Selected |
|--------|-------------|----------|
| Rename to make it a fallback | Identifier stops claiming to be *the* page size; 4 references | ✓ |
| Keep `#define PAGE_SIZE 64` | Zero rename churn | |

**User's choice:** Rename → **D-10**.

### Q9 — Pin the new-host / old-firmware unknown-key skip?

| Option | Description | Selected |
|--------|-------------|----------|
| Pin it with a native test | Guards the forward-compat property the design rests on | ✓ |
| Document it, no test | Cheaper; leaves the property unguarded | |

**User's choice:** Pin it → **D-11**.

**Decided by precedent rather than asked (recorded in CONTEXT.md as D-05 and D-06):** the
per-command reset of the new field, mirroring `chip_id` (the global `handle` is never `memset`, so
a stale 128 would make "absent ⇒ 64" false); and the `page_mask` AND on the absolute address rather
than a runtime `%` (preserves alignment semantics, avoids `__udivmodsi4`).

---

## Leonardo flash budget

### Q10 — How is the AVR flash growth funded?

| Option | Description | Selected |
|--------|-------------|----------|
| New named, SHA-attributed exemption | Mirrors the existing mechanism with a distinct constant | ✓ |
| Fund from in-phase savings | Delete dead `json_init()`; saving may be zero under `--gc-sections` | |
| Record the breach, change no constant | Ships a failing size gate | |
| Re-anchor BASE-01 | Cheapest; what PGSZ-04 exists to prevent | |

**User's choice:** New named exemption → **D-12**.
**Notes:** Measured position presented: BASE-01 leonardo 26906, live 27002, leonardo band 0 B, and
the 96 B defect-fix exemption already fully consumed by Phase 145. uno-class has 64 B left.
Neither size script runs in CI.

### Q11 — Where do the new native tests live, given the `<= 1166` warnings watermark?

| Option | Description | Selected |
|--------|-------------|----------|
| Extend the existing suites | No new translation units, so no new macro-redefinition warnings | ✓ |
| New suite + re-measured watermark | Clearer provenance; more gate churn | |

**User's choice:** Extend existing suites → **D-15**.

### Q12 — What is the comparison point for the delta?

| Option | Description | Selected |
|--------|-------------|----------|
| Fresh cold capture at the fork commit | Merge drift recorded as inherited, not attributed here | ✓ |
| Use the committed `size_baseline.json` figures | No extra builds; measured on a different tree | |

**User's choice:** Fresh cold capture → **D-13**.

### Q13 — Is `size_baseline.json` updated at phase end?

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, with a superseding meta note | Follows the file's own Phase 144/145 pattern | ✓ |
| No — phase artifact only | Maximum cost visibility; later phases must subtract by hand | |

**User's choice:** Yes, with a superseding note → **D-14**.

---

## Proof surface & honesty artifact

### Q14 — Phase 148's 746-chip wire golden goes RED by design

| Option | Description | Selected |
|--------|-------------|----------|
| Committed expected-delta list | Golden stays pre-149; test asserts golden + 18 named deltas | ✓ |
| Deliberate re-baseline with the diff shown | Simpler test; evidence lives in the commit message | |

**User's choice:** Committed expected-delta list → **D-17**.

### Q15 — How is PGSZ-03's cross-repo parity verified?

| Option | Description | Selected |
|--------|-------------|----------|
| Host test scanning `json_parser.c` + inventory entry | Also makes `constants.py:144`'s false sync note true and enforced | ✓ |
| Documented manual check | No new machinery; sync note stays a comment | |

**User's choice:** Host test + `scan_paths.py` inventory entry → **D-18**.

### Q16 — PGSZ-05's claim gate

| Option | Description | Selected |
|--------|-------------|----------|
| Phase-local gate, seen to fail on a planted violation | Explicit hard-coded target list; RED-then-GREEN transcripts | ✓ |
| Rely on Phase 152's OUT-05 gate | No duplicate machinery; leaves 149's artifacts unscanned | |
| Required-phrase assertion only | Cheap; cannot catch a later overclaim | |

**User's choice:** Phase-local fail-provable gate → **D-19**.

### Q17 — Anything user-facing?

| Option | Description | Selected |
|--------|-------------|----------|
| Changelog entry with the caveat | One line, 15 chips named/counted, software-proven wording | ✓ |
| Nothing user-facing — artifact only | Behaviour simply becomes correct | |

**User's choice:** Changelog entry → **D-20**.

### Q18 — Fold the dead `json_init()` todo?

| Option | Description | Selected |
|--------|-------------|----------|
| Fold it | Broken by inspection, in the exact file this phase edits | ✓ |
| Leave it pending | Keeps the diff strictly page-size | |

**User's choice:** Fold it → recorded under Folded Todos.

---

## Claude's Discretion

- Exact names for the fallback constant, the handle field, the mask local, and the new MERGE-05
  exemption constant.
- Field width of the handle member (`uint16_t` is the obvious choice, not locked).
- Whether the `build_db.py` emit rule and the firmware seam land in one plan or two.
- Fixture shape and location for the expected-delta list.
- Exact wording of the corrected `eeprom_28c.cpp` comment, provided it says *unproven*.

## Deferred Ideas

- The 66 promoted `0x0D` rows keep the 64 floor — one todo with the exact part lists.
- `FM28V020` / `MB85R256H` FRAM misclassification — a separate todo.
- A runtime INFO log naming the effective page size, tied to a future gh#21 re-run.
- Unifying `flash_5v_page.cpp` onto the wire field — recorded as a deliberate non-change, not filed.
- Folding `response_code` into the handler log macro — the one reliable flash lever, declined as
  its own change rather than this phase's business.
