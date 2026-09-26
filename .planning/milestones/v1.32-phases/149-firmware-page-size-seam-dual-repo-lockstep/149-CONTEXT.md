# Phase 149: Firmware Page-Size Seam (dual-repo lockstep) - Context

**Gathered:** 2026-08-19
**Status:** Ready for planning

<domain>
## Phase Boundary

The per-chip page size travels from `chip_database.json` over the existing JSON command path to
the protocol-`0x0D` firmware handler, replacing `eeprom_28c.cpp`'s `#define PAGE_SIZE 64` as the
only value it can ever use — with 64 retained as the fallback when the field is absent.
Dual-repo lockstep (`firestarter` + `firestarter_app`), **software-proven, unvalidated on silicon.**

**In scope:** a `page-size` key in `firestarter/src/json_parser.c`; a page-size field on
`firestarter_handle_t` reset per command; a validated page mask consumed by
`eeprom28c_write_execute`; the provenance-keyed emit rule in `tools/build_db.py`; the AVR
flash/RAM measurement and its MERGE-05 funding decision; native tests for the delivered value,
the absent-field fallback and the unknown-key skip; the cross-repo parity test; a phase-local
claim gate; `149-PAGE-SIZE.md`; one `firestarter_app` changelog line. PGSZ-01…PGSZ-05.

**Out of scope:** any bench or silicon validation (REQUIREMENTS.md §Out of Scope — adding one
would create a hardware-gated criterion nothing can satisfy); extending `_PAGE_SIZE_BY_PART` or
any per-chip guess table (same section, DATA-04); `flash_5v_page.cpp`'s `mem_size` band table
(FIX-04 frozen — D-07); any `support_status` change or `0x0D` graduation; the 66 promoted `0x0D`
rows' page sizes (D-04, deferred with measured part lists); `cli_handlers.py` (Phase 147 / 150
own it).

**Cross-phase constraint:** Phase 150 (`write --sdp-relock`) depends on this phase's write path
being settled, and Phase 152's OUT-01/OUT-04 name what ships here. Phase 148 also wrote the host
DB-consumption layer — 148 is complete, so the never-share-a-wave constraint is discharged.

**Evidence Ceiling applies (binding, `PROJECT.md` §Current Milestone: v1.32).** No AT28C part
exists in operator inventory. No criterion here may require silicon, assert the `0x0D` write path
is proven, graduate `0x0D`, change any `support_status`, or be phrased as closing
gh#21/#32/#11/#12. **Measured non-claim, load-bearing:** AT28C256 — the gh#21 part — carries
`page_size 64`, *exactly today's floor*, so this phase cannot change its behaviour at all and
explains nothing about gh#21.

</domain>

<decisions>
## Implementation Decisions

### Delivery scope — which chips get a delivered page size (PGSZ-01)

- **D-01: Provenance-keyed — deliver only where the upstream `<ic>` record's own `protocol_id` is `0x0D`.** 18 rows qualify; **15 are movers**, every one growing 64 → 128.

  This was measured during discussion, not assumed, and it overturns the phase's own framing.
  `chip_database.json`'s 84 `algorithm: 13` rows are **not** 84 upstream-`0x0D` records:
  `classify()` (`build_db.py:374-382`) promotes `DIP24_2816` / `DIP28_28C64` / `DIP28_28C256` /
  `DIP28_2764`+EE parts into `0x0D` from whatever protocol they arrived with. Full join against
  the pinned XML (all 84 matched, zero unmatched):

  | upstream `protocol_id` | `page_size` values → counts |
  |---|---|
  | `0x07` | 1→14 · 16→1 · 32→8 · 64→22 · 128→1 · 256→1 |
  | `0x0B` | 1→17 · 16→2 |
  | **`0x0D`** | **64→3 · 128→15** |

  Only 18 of 84 are upstream-native. Their page sizes are **exactly** the CONFIRMED field
  dictionary's documented band ("typically 64 or 128 bytes for 28C-family"), nothing else. Every
  value outside that band comes from a promoted row — a record whose own algorithm never consumed
  `page_size` as a 28C page-write buffer, so carrying it into this handler is a cross-algorithm
  reinterpretation. **This is the Phase 148 D-01 category error one field over** (minipro's `vcc`
  is the TL866's verify rail surfaced as the operating supply).

  **`infoic_page_size_raw` is a faithful copy** — zero mismatches against the XML across all 84.
  There is no decode bug here; the question is purely semantic.

  **The 15 movers** (upstream `0x0D`, page 128): ATMEL `AT28C010,AT28C010E`, `AT28C040,AT28C040E`,
  `AT28LV010`, `AT28MC020`, `AT28MC040`; CATALYST(CSI) `CAT28C512`, `CAT28C010`, `CAT28C020`,
  `CAT28C040`; MAXWELL `28C010,28C010T,28C011,28C011T`; SGS-THOMSON `M28010`; ST `M28010`;
  WED `WE512K8`, `WME128K8`; XICOR `X28C010`.
  **The 3 no-change rows** (upstream `0x0D`, page 64): ATMEL `AT28MC010`, WED `WE128K8`, `WE256K8`.

  Note `AT28MC010` (64) and `AT28C010` (128) are **both** upstream-native `0x0D` — so the
  same-density-different-page argument the existing `eeprom_28c.cpp` comment rests on is fully
  preserved by this rule, and both chips are in the delivered set.

  **Rejected:** grow-only ignoring provenance (17 movers — adds CYPRESS `FM28V020` and FUJITSU
  `MB85R256H`, **both FRAM**, one a 3.3 V part, both riding `0x0D` by pinout promotion; FRAM has
  no page buffer and no internal write cycle, so those are the two rows where a delivered page
  size is most clearly meaningless); all-real-values with sentinels falling back (28 movers — 13
  of them resting on a `page_size` read out of a `0x07`/`0x0B` record with no corroboration).

- **D-02: The value is carried by `programming.page_size` — the existing key, reused.** It becomes
  "the resolved page size for the algorithm that will consume it", sourced either from the
  datasheet-curated `_PAGE_SIZE_BY_PART` table (2 algorithm-`0x05` rows, unchanged and
  **not extended**) or from an upstream-native `0x0D` record (18 rows). `infoic_page_size_raw`
  is **untouched** and stays the raw provenance axis.
  **Consequence — the host needs ZERO code change:** `database.py:417` already carries
  `programming.page_size` into `_map_data` and `:552` already emits wire `page-size`, both via
  `.get` (so no `KeyError` on the two `tools/extra_chips.json` rows that lack page keys), and
  `page-size` is **already** in the wire golden's 9-key union. PGSZ-01's "through the existing
  JSON command path" is therefore literal.
  Both curated values already equal their raw upstream values (`W29C020` 128, `W29C040` 256), so
  the two provenances are measurably consistent where they meet.
  **Rejected:** a new distinct key (`page_size_28c`) — costs a host-side merge and a second emit
  condition for a distinction the raw field already records.

- **D-03: Emit for all 18 corroborated rows, including the 3 already at 64.** Field presence means
  "provenance-corroborated", **not** "differs from the firmware default". A `raw != 64` filter
  would smuggle the rejected grow-only direction preference back in through the emitter, and would
  couple the host's emit condition to a firmware constant. The 3 extra rows are byte-equal to what
  the firmware would have used anyway, so they change no behaviour and demonstrate the delivered
  path and the fallback agree.

- **D-04: The 66 promoted rows keep the 64 floor, and the comment that describes it is corrected.**
  Three deliverables:
  1. One pending todo carrying the measured part lists — 31 rows at raw `1` (14 upstream `0x07`,
     17 upstream `0x0B`), 8 at 32, 3 at 16, 1 at 256, 1 at 128 — with the upstream-provenance
     reason and the four-way table above.
  2. **A separate** pending todo naming CYPRESS `FM28V020` and FUJITSU `MB85R256H` as parts riding
     the `0x0D` handler by pinout promotion (one of them 3.3 V with `vpp_mv 12000`) — a
     classification question, not a page-size one.
  3. Rewrite `eeprom_28c.cpp:19-32`'s "64 errs SAFE … can never overrun" claim. **Precision
     matters here:** for the 11 rows at 16/32 the floor's safety is **unproven**, not disproven —
     their `page_size` comes from `0x07`/`0x0B` records, so we cannot assert their real page is
     16 or 32 either. The corrected comment says unproven. (An earlier reading in this discussion
     said "overrun today"; that is too strong and must not reach any artifact.)

### Firmware trust boundary (PGSZ-02)

- **D-05: `page_size` resets to 0 in `json_parse`, exactly as `chip_id` does; the fallback to 64 is applied in the handler.** `firestarter_handle_t handle` is a single file-scope global
  (`firestarter.cpp:33`) with **no per-command `memset`** — `json_parse` resets precisely the
  *optional* keys because the mandatory ones are always overwritten. `page-size` is optional
  (emit-when-present), so without the reset, writing AT28C010 (128) and then a floor chip in the
  same session leaves the second chip on a 128-byte window — making "absent ⇒ 64" **false in
  practice**, which is the exact overrun PGSZ-02 exists to prevent. Applying the fallback in the
  handler keeps `json_parse` algorithm-agnostic and keeps the floor a named firmware constant.
  *Decided by in-repo precedent, not asked.*

- **D-06: Flush on a `page_mask = page_size - 1` bitwise AND against the ABSOLUTE address, never a runtime `%`.** Preserves today's `(address + 1) % PAGE_SIZE` semantics exactly — flushes align
  to true chip page boundaries even when `handle->address` is unaligned (a `--address` write), which
  a per-block counter would break — and avoids pulling `__udivmodsi4` into a build with zero flash
  headroom. Both delivered values are powers of two. Resolve and store the validated mask once at
  write-INIT; its degenerate value (0) flushes every byte, which **cannot** overrun.
  *Decided by analysis, not asked.*

- **D-07: Validation is a cheap silent firmware fallback; the invariant is proven on the host.**
  Firmware: anything not a power of two in `[1, DATA_BUFFER_SIZE]` falls back to 64, in a few
  instructions, with no log. The **host** carries the exhaustive proof — a test asserting every
  emitted `page_size` across all 746 chips is a power of two within range — because the only
  producer is our own in-repo host and that is where the assertion can be total and free.
  **Rejected:** validate-and-warn in firmware (a new codegen message ID in
  `tools/catalog/messages.toml` plus a PROGMEM string, against a leonardo budget with 0 bytes, to
  report a condition only our own host could cause); trust-and-mask with no check at all.

- **D-08: `0x0D` only — `flash_5v_page.cpp` is an explicit non-change.** Its `mem_size`-derived
  band table (`flash_5v_page.cpp:27`) stays exactly as-is, FIX-04 frozen, so `W29C020`/`W29C040`
  keep riding the heuristic **even though the host already sends them `page-size`**. Record this
  as a deliberate non-change: otherwise a reader will reasonably assume the new wire key governs
  both handlers, and those two rows look wired when they are not.

- **D-09: The 128 delivery is observed by a native test on flush cadence, and nothing else.**
  Assert that a 128-byte-page handle produces a different flush/poll count than the 64 case, and
  that an absent field reproduces the 64 cadence. Zero firmware bytes, runs in CI, and flush count
  is exactly what the constant governs — **no timing is involved, so the native stubs' missing
  clock does not weaken it** (native trace stubs record no time; `delay()` is unstubbed).
  The runtime INFO log naming the effective page size is **filed as a follow-up todo**, tied to the
  eventual gh#21 re-run request where a report might need to name the page size it used.

- **D-10: Rename the fallback constant** (e.g. `AT28C_PAGE_SIZE_FALLBACK`) so the identifier stops
  claiming to be *the* page size — that claim is half of what made the old comment misleading.
  4 references: `eeprom_28c.cpp:33`, `:634`, plus `PAGE_SIZE` mentions in 3 native test files
  (`test_val_eeprom28c.cpp:204,256`, `test_eeprom28c_sdp.cpp:1532,1543,1603`) — comments and one
  literal, all mechanical.

- **D-11: Pin the new-host / old-firmware direction with a native test.** The unknown-key skip at
  `json_parser.c:320` (`// Unknown field — skip key + value token`) is what makes the whole
  emit-when-present design forward-compatible, and it is currently unguarded in a parser that has
  gained keys repeatedly. Same shape as PGSZ-02's own "exercised by a test rather than asserted in
  a comment" language.

### Flash and warning budget (PGSZ-04)

- **D-12: Fund the growth with a NEW, separately-named, SHA-attributed MERGE-05 exemption.**
  Measured position: BASE-01 leonardo `26906`, live `27002`, leonardo band `0 B`, and
  `MERGE05_DEFECT_FIX_EXEMPTION_BYTES = 96` **already fully consumed** by Phase 145's W27C512 fix.
  uno-class has 64 B left. So the band admits nothing. Mirror the existing exemption's *mechanism*
  with a distinct constant carrying its own justification and its own commit SHAs; the existing
  defect-fix constant is **untouched and not widened**, and `MERGE05_UNO_CLASS_FLASH_BAND` stays 64.
  **Rejected:** re-anchoring BASE-01 (what made MERGE-05 green at Phase 144; PGSZ-04 exists
  precisely to stop "silently consuming what is left", and a second anchor move makes the band
  unfalsifiable); funding from in-phase savings (see D-16 — with `--gc-sections` the saving may be
  literally zero, so it cannot be committed to in advance); shipping a RED size gate.

- **D-13: The comparison point is a fresh COLD capture at the forked v1.32 tip, before the first edit.** `rm -rf .pio/build/<env>` then one `pio run -e <env>` per env. `size_baseline.json`'s
  figures were measured at firmware tree `3d8ec49` (Phase 145 debug session); the v1.32 branch
  forks off `beta` (`7f6afc6`), which carries merge commits since. Any difference is recorded as
  **inherited from the v1.31 merge**, never attributed to this phase — in either direction.

- **D-14: `scripts/baseline/size_baseline.json` is updated at phase end, with a superseding meta note**, following the file's own established Phase 144 / Phase 145 pattern, so it stays the live
  default baseline the next phase measures against.

- **D-15: New test cases go into the EXISTING native suites — no new suite.** Extend
  `test/native/avr/test_val_eeprom28c/` (and the parser suite for D-11); both are already in
  `[env:native]`'s `test_filter`, so they run in CI. **This is a warning-budget decision:** the
  native watermark is `<= 1166` and that figure is attributed to macro redefinitions across
  "roughly 27 translation units" including `rurp_platform_compat.h`, so a new suite adds TUs and
  very likely warnings, forcing a cold re-measure and a raised watermark. Extending adds no TU and
  leaves all three watermarks untouched.

### Proof surface and honesty (PGSZ-03, PGSZ-05)

- **D-16: `149-PAGE-SIZE.md` in the phase directory is the review artifact.** One document,
  reviewable whole, carrying: the upstream-provenance table, the 15-mover and 3-no-change lists,
  the D-01 justification with its `doc/infoic-field-dictionary.md:241` and minipro citations, the
  three measured non-claims (no silicon claim; AT28C256 unchanged so gh#21 is untouched; the
  floor's safety unproven for the 11 promoted 16/32 rows), the cold flash/RAM figures for all three
  targets with leonardo's remaining headroom **as a number**, and the MERGE-05 breach **named**
  with the exemption's justification. Precedent: `148-DB-DIFF.md`.

- **D-17: Phase 148's wire golden is preserved, with a committed expected-delta list.**
  `tests/golden/wire_dict_baseline.json` (746 records) plus
  `test_live_capture_matches_golden` goes RED by design when 18 rows gain `page-size`. Keep the
  golden as the pre-149 capture and assert "golden **plus exactly these 18 named deltas**". The
  diff becomes reviewable committed data that a later phase cannot quietly re-baseline away, and
  Phase 148's own central claim — its migration changed nothing on the wire — stays legible in the
  same file. The key union stays 9 (`page-size` is already in it).
  **Rejected:** re-capturing the golden with the diff shown only in the artifact and commit message.

- **D-18: PGSZ-03 parity is a host test that scans firmware source, with an inventory entry.**
  Assert `constants.py`'s `JSON_KEY_PAGE_SIZE` equals the PROGMEM key string in
  `firestarter/src/json_parser.c`, via `tests/fw_presence.py`'s `requires_fw`, **and add
  `src/json_parser.c` to `tests/scan_paths.py`'s committed inventory** — it currently lists
  `include/firestarter.h` but not the parser, and an off-inventory cross-repo scan is exactly the
  defect that module exists to prevent. This also turns `constants.py:144`'s **currently false**
  "Firmware sync: json_parser.c (`key_page_size`)" note into a true, enforced claim — that key does
  not exist in the firmware today. Prove the skip leg by pointing `FIRESTARTER_FW_ROOT` at an empty
  directory (the app's own CI has no sibling checkout, so this gate skips there — state that).

- **D-19: A phase-local, fail-provable claim gate over an EXPLICIT target list.** It rejects
  silicon-validation / page-size-proven-on-hardware / `0x0D`-graduation / `support_status` wording
  and requires PGSZ-05's exact phrase. Targets, hard-coded: `149-PAGE-SIZE.md`, every `149-*-SUMMARY.md`,
  and the changelog entry. **Hard-code the paths** — `check_permitted_claims.py`'s `_HERE` resolves
  to the *checker's own* phase directory, so a reused checker scans nothing and exits 0. Plant a
  violation, watch it go RED, revert, watch GREEN, commit both transcripts.
  **Rejected:** relying on Phase 152's OUT-05 gate (outward text only — 149's artifacts would go
  unscanned for three phases, and 152 cannot retract a claim made here); a required-phrase
  assertion alone (cannot catch an artifact that says the right sentence and overclaims two
  paragraphs later).

- **D-20: One `firestarter_app` changelog line.** The 15 AT28C010-class parts now write using
  their datasheet 128-byte page instead of the 64-byte floor, stated as **software-proven and
  unvalidated on silicon**. Mirrors Phase 148 D-17 (reasoning in the artifact, one honest
  user-facing line) — and unlike 148's, this change does alter write behaviour, so it is announced.

### Claude's Discretion

- Exact names for the fallback constant (D-10), the handle field, the mask local, and the new
  MERGE-05 exemption constant (D-12) — keep each single-sourced.
- Field width of the handle member (`uint16_t` covers 1…512 and costs 2 B RAM against leonardo's
  546 B free — the obvious choice, but not locked).
- Whether the `build_db.py` emit rule and the firmware seam land in one plan or two, provided
  `149-PAGE-SIZE.md` can still show the DB-side and firmware-side evidence separately.
- Fixture shape and location for D-17's expected-delta list.
- Exact wording of the corrected `eeprom_28c.cpp` comment, provided it says **unproven** rather
  than overrun for the 11 promoted 16/32 rows.

### Folded Todos

- **`remove-dead-json-init-sizeof-pointer-bug`** (`.planning/todos/pending/`) — `json_init()` at
  `firestarter/src/json_parser.c:42` computes `sizeof(tokens) / sizeof(tokens[0])` on a **pointer**
  parameter, so `num_tokens` is 0 and `jsmn_parse` could only ever return `JSMN_ERROR_NOMEM`. It is
  called from nowhere in `src/` (only a comment in `test_read_timing_params.cpp:70` mentions it).
  Folded because it is broken by inspection **in the exact file this phase edits** — delete the
  definition and its `json_parser.h:19` declaration. Any flash saving is a bonus, not the
  justification: with `--gc-sections` the linker may already discard it, so **do not** count it
  toward D-12's budget.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone charter and requirements (binding)
- `.planning/PROJECT.md` §"Current Milestone: v1.32" — the Evidence Ceiling, the workstream table
  row 3, and the standing "no silicon claim" constraint.
- `.planning/REQUIREMENTS.md` §"Firmware Page-Size Seam (PGSZ)" — PGSZ-01…PGSZ-05.
- `.planning/REQUIREMENTS.md` §"Out of Scope" — the **"Bench validation of the page-size change"**
  and **"Extending `_PAGE_SIZE_BY_PART` or adding per-chip guess tables"** rows are binding on this
  phase specifically; the second one is what forces D-01's provenance rule.
- `.planning/ROADMAP.md` §"Phase 149" — the five success criteria; criterion 1's "observed to
  deliver 128" is satisfied by D-09, criterion 4's "MERGE-05 band breach named" by D-12/D-16.
- `.planning/phases/148-numeric-database-values-the-at28c-vcc-decode/148-CONTEXT.md` — D-01
  (minipro's `vcc` is a verify rail, the category error D-01 here mirrors), D-10 (direct indexing
  vs `.get`), D-13 (goldens re-derived with a seen-to-fail transcript), D-14 (the wire-dict
  equivalence capture this phase perturbs).

### Upstream data provenance (the load-bearing evidence for D-01)
- `firestarter_app/doc/infoic-field-dictionary.md:241` — the **CONFIRMED** `page_size` row: "Page-write
  size for EEPROM/Flash. Typically 64 or 128 bytes for 28C-family; `0` or `1` if not applicable to
  the device type", cited to minipro `database.c#L598` @ `a8efaedc`. **Read this before proposing
  any change to the selection rule.**
- `firestarter_app/tools/build_db.py:317-402` — `classify()`; **arm 2 (`:374-382`) is the promotion
  that makes 66 of the 84 `0x0D` rows non-native.**
- `firestarter_app/tools/build_db.py:478-490` — `proto_id` and `raw_page_size` read off the same
  `<ic>`; the comment stating the raw field is "PROV-06's corroborating axis only".
- `firestarter_app/tools/build_db.py:120-140` — `_PAGE_SIZE_BY_PART`, the datasheet-curated table
  that must **not** be extended (2 entries, both algorithm `0x05`).
- `firestarter_app/tools/build_db.py:765-796` — the `programming` emitter, where D-01/D-02/D-03 land.
- `firestarter_app/tests/test_b15_page_size_corroboration.py` — the measured 12-of-84 bit-15 vs
  `page_size > 1` disagreement. **Read the docstring: its finding is that bit 15 is not a
  page-write proxy — it is not evidence against `page_size`.**
- Pinned source: `https://gitlab.com/DavidGriffith/minipro/-/raw/a8efaedc236c1d9718bd28299dfbb99536b010ff/infoic.xml`
  (md5 `b4548e57c4f6c6c8c4f7387add03fa77`, 17,861,009 bytes; three `<database>` sections —
  `build_db.py` reads **`INFOIC2PLUS` only**, which is why a whole-file scan miscounts).

### Firmware — the seam
- `firestarter/src/proms/eeprom_28c.cpp:19-33` — the `PAGE_SIZE 64` floor and the comment D-04
  corrects; it already cites the AT28MC010 (64) vs AT28C010 (128) same-density pair.
- `firestarter/src/proms/eeprom_28c.cpp:625-660` — `eeprom28c_write_execute`'s load loop; `:634` is
  the single `% PAGE_SIZE` flush test D-06 replaces with a mask.
- `firestarter/src/json_parser.c:67` — the PROGMEM key strings and `key_parsers[]` table the new
  key joins; `:50` is the dead `json_init()` (folded todo); `:85-95` the optional-key resets (D-05's
  precedent); `:133` the unknown-key skip (D-11).
- `firestarter/include/firestarter.h:188-224` — `firestarter_handle_t`; `:16-17` `DATA_BUFFER_SIZE`.
- `firestarter/src/firestarter.cpp:33` — the single global `handle`, never `memset` between commands.
- `firestarter/src/proms/flash_5v_page.cpp:19-30,81-99` — the FIX-04-frozen band table D-08 leaves
  alone.

### Host — the wire and its gates
- `firestarter_app/firestarter/database.py:414-419` — `_map_data` carrying `programming.page_size`.
- `firestarter_app/firestarter/database.py:536-557` — `convert_to_programmer`, the wire seam; `:550-553`
  already emits `page-size`.
- `firestarter_app/firestarter/constants.py:144-148` — `JSON_KEY_PAGE_SIZE` and the **currently false**
  `key_page_size` sync note (D-18).
- `firestarter_app/tests/test_wire_dict_equivalence.py` + `tests/golden/wire_dict_baseline.json` —
  746 records, 9-key union already including `page-size`, 2 rows carrying it today (D-17).
- `firestarter_app/tests/fw_presence.py` — `requires_fw`; a missing scan target under a present repo
  is a **hard failure**, not a skip. Import-time binding: `monkeypatch.setenv` has no effect.
- `firestarter_app/tests/scan_paths.py` — the committed cross-repo path inventory; add
  `src/json_parser.c` (D-18). Note the `firestarter` name-collision trap documented at its head.
- `firestarter_app/tools/diff_db.py:225-250` — the `PROV01_PROTECT_METADATA` rationale describing the
  raw field; `:388` and `:613` the existing `PGSZ_PAGE_SIZE` classification.

### Size and warning gates
- `firestarter/scripts/baseline/size_baseline.json` — live figures (uno 24920, uno328pb 24970,
  leonardo 27002; RAM 1573/1579/2014) and the `warnings` block (native watermark 1166).
- `firestarter/scripts/baseline/size_baseline_base01.json` — MERGE-05's judged reference (leonardo
  26906), re-anchored at Phase 144.
- `firestarter/scripts/check_size_baseline.py:123-167,278-310` — `MERGE05_UNO_CLASS_FLASH_BAND = 64`,
  `MERGE05_DEFECT_FIX_EXEMPTION_BYTES = 96`, leonardo band `0`; the `--policy merge05` FAIL arm.
- `firestarter/scripts/check_build_warnings.py` — the AVR `== 0` / native `<= watermark` policy.
- `firestarter/platformio.ini:69-120` — `[env:native]`'s `test_filter`; `test_val_eeprom28c` and
  `test_eeprom28c_sdp` are both in it. `firestarter/.github/workflows/build.yml` — **neither size
  script runs in CI**; both are phase-level gates the plan must invoke.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **The `read-settling-delay` / `read-strobe-us` knobs (Phase 44)** — the exact precedent for
  adding an optional host-tunable key: a PROGMEM string, a `key_parsers[]` row, a `get_*` function,
  a handle field, and a paired `constants.py` sync note. Follow it line for line.
- **`chip_id`'s optional-key reset in `json_parse`** — the in-repo precedent D-05 rests on: the
  parser resets exactly the optional keys, because the mandatory ones are always overwritten.
- **The unknown-key skip at `json_parser.c:320`** — already makes new-host/old-firmware safe today;
  D-11 pins it rather than building it.
- **`fw_presence.py` + `scan_paths.py`** — the fail-closed cross-repo scan infrastructure D-18
  needs already exists; the phase adds one inventory entry, not a mechanism.
- **`148-DB-DIFF.md`** — the shape of D-16's artifact: run output, mover list, cited justification,
  explicit non-claims, one reviewable document.

### Established Patterns
- **`chip_database.json` is GENERATED and never hand-edited.** Every value change lands in
  `build_db.py`'s decode/emit path. Three per-chip lookup tables were deliberately deleted in
  Phase 70; `_PAGE_SIZE_BY_PART` is not to be extended under any name.
- **A blast radius is a measurement, not an estimate** — hence D-01's provenance table and the
  named 15/3 lists rather than "the AT28C010 class".
- **Goldens are re-derived (or delta-listed) with a seen-to-fail transcript, never silently
  re-baselined** (Phase 136, 140, 148 D-13). D-17 and D-19 both inherit this.
- **Every `# noqa: BLE001` in `firestarter_app` is inert** (ruff `select` is `[E,F,I,UP]`), so a
  broad `except Exception:` added host-side is gated by nothing — keep excepts narrow by hand.
- **`messages.h` is codegen-generated and ID-only** — from `firestarter/tools/catalog/messages.toml`
  via `tools/catalog/codegen.py`, with a CI drift gate. D-07/D-09 deliberately add no message, so
  no codegen run is needed; if that changes, the catalog is the edit point, never the header.

### Integration Points
- `infoic.xml` (`INFOIC2PLUS`) → `build_db.py` `classify()` + emitter → `programming.page_size` →
  `database.py._map_data` → `convert_to_programmer` → wire `page-size` → `json_parser.c` →
  `handle` → `eeprom28c_write_execute`'s flush test. **This phase supplies the two missing hops
  (the emit rule and everything from `json_parser.c` rightwards); the middle is already built.**
- Wire dict changes flow into `test_wire_dict_equivalence.py` (D-17) and `diff_db.py`'s existing
  `PGSZ_PAGE_SIZE` bucket. **Research item:** the 18 rows already classify under
  `PROV01_PROTECT_METADATA` in today's 744-changed-chip report, so how `_classify_diff` combines a
  second changed field on an already-classified chip must be measured, not assumed.

### Execution mechanics (preconditions, not decisions)
- **⚠ The firmware submodule is on the WRONG branch.** `firestarter/` is still on
  `gsd/v1.31-27c-programming-algorithm-fidelity` (tip `6992271`). A v1.32 firmware branch must be
  forked off `origin/beta` (`7f6afc6`, carries v1.31 via merged PR #52) **before any firmware
  edit** — and before D-13's cold baseline capture, since the capture must be taken at that fork
  point. `firestarter_app/` is already correct
  (`gsd/v1.32-at28c-write-path-root-cause-report-provenance`).
- **Verify the fork by content, not by `merge-base --is-ancestor`** — the v1.31 PRs were squashed,
  so ancestry checks return false negatives.
- **`build_db.py` fetches `infoic.xml` over the network** and has **no CLI flags** — it writes
  straight to `firestarter/data/chip_database.json`. Never invoke it for exploration; a read-only
  replication of its filter against a downloaded copy is the safe move. A pinned byte-identical
  copy is at
  `/tmp/claude-1000/-workspaces/17c288b6-8ef4-4819-8b66-1b98d2fc0404/scratchpad/infoic_fresh.xml`.
- **Write blocks are 512 (Uno floor) / 1024 (advertised), both exact multiples of 128**, and the
  flush test is on the absolute address — so 128 is genuinely reached, and an unaligned `--address`
  write still breaks on true page boundaries with a short first window. Verified, not assumed.
- **`test_flash_path_record_sync.py` asserts whole-repo porcelain** — commit before running the
  host suite or it goes RED on any mid-change diff.
- **Doubling pytest `-q` hides the count line** — `addopts` is `-ra -q`; use `-o addopts=""`.
- **Meta-repo working tree is dirty** (both submodule gitlinks, untracked `.claude/`,
  `package*.json`). Stage specific files only.
- **The record gate needs a 300 s timeout** — `STATE.md` carries a ~52k-char single line; a short
  timeout returns rc=124 and reads like a RED.

</code_context>

<specifics>
## Specific Ideas

- **The upstream-provenance table is the artifact of this discussion.** It appears in no
  requirement, roadmap criterion or seed. It was measured by joining all 84 `algorithm: 13` rows
  back to the pinned XML, and it turned a plausible "deliver the raw page size" into a rule that
  would have handed a 256-byte page to a Fujitsu FRAM. Keep it in front of anyone who proposes
  touching the selection condition.
- **`write_buffer_size` is the trap, and it is worth recording as such.** It looks like exactly the
  corroborating field one would want, and it is the programmer's transfer buffer: across the 84 it
  takes `{128×46, 32×33, 64×4, 256×1}`, and for AT28C256 it reads 128 while the datasheet page is
  64. `read_buffer_size` is the same shape; `pages_per_block` is `0` on all 84 (a NAND field).
  **No attribute in `infoic.xml` corroborates `page_size`.**
- **The one datasheet in the repo for this family cannot discriminate.** `firestarter_app/datasheets/`
  holds `AT28C256.pdf` and nothing else for `0x0D` — and AT28C256's page is 64, i.e. today's floor.
  Any argument of the form "check it against the datasheet" is unavailable for all 15 movers and
  all 11 promoted 16/32 rows.
- **Frame the rule as a claim about provenance, never about a part.** "The `page_size` attribute is
  meaningful for the algorithm that consumes it; a record filed under `0x07`/`0x0B` is not evidence
  about a 28C page buffer." That wording is what keeps this from becoming a
  `_PAGE_SIZE_BY_PART` sibling — keep it in the code comment and in `149-PAGE-SIZE.md`.

</specifics>

<deferred>
## Deferred Ideas

- **The 66 promoted `0x0D` rows (D-04).** 31 at raw `1` (14 upstream `0x07`, 17 `0x0B`), 8 at 32,
  3 at 16, 1 at 256, 1 at 128. They keep the 64 floor. File as a pending todo with the exact part
  lists and the provenance reason. Any future attempt needs either datasheet curation per family or
  a new corroboration axis — neither of which `infoic.xml` supplies.
- **CYPRESS `FM28V020` and FUJITSU `MB85R256H` ride the `0x0D` handler by pinout promotion** — both
  FRAM, one a 3.3 V part carrying `vpp_mv 12000`, both typed `EEPROM`. A **separate** pending todo:
  this is a classification question, not a page-size one.
- **A runtime INFO log naming the effective page size**, so a future community `dev test` report
  can show the granularity its firmware used — tied to the gh#21 re-run request. Declined here on
  flash cost (D-09), filed as a follow-up.
- **Unifying `flash_5v_page.cpp` onto the wire field**, retiring its `mem_size` band table. Not
  filed as a task — D-08 records it as a deliberate non-change, with the measurement that both
  curated algorithm-`0x05` values already equal their raw upstream values.
- **Folding `response_code` into the handler log macro**
  (`.planning/todos/pending/fold-response-code-into-log-macro.md`) — 29 call sites, the one lever
  that would reliably free real AVR flash. Considered as D-12 funding and **not** folded: a 29-site
  refactor across every handler is its own change, not a page-size phase's business.

### Reviewed Todos (not folded)

Todo matching returned 20 pending items; **one folded** (the dead `json_init()`, see
`<decisions>`). The rest were reviewed and left:

- *Skip VPP error/warning checks when VPP is unused* (0.9), *CONFIG_VERSION not bumped* (0.9),
  *FM1608 byte 0 write never lands* (0.9), *Prove the PlatformIO dev-tools flag fails CLOSED* (0.9)
  — all scored on `area: firmware` plus keyword noise; none touches the page-size seam. FM1608 is
  adjacent only in being a FRAM part; its defect is register cache-skip elision, not granularity.
- *`vcc == 5500` high-margin verify-rail group* (0.9) — Phase 148's own deferred item, host-side.
- *AT28C256 write-path failure (gh#20)* (0.6) — Backlog **999.29**, explicitly **not retired** by
  v1.32 and blocked by the Evidence Ceiling. This phase cannot address it; AT28C256's page size is
  already 64.
- *`DATA_BUFFER_SIZE` speed-delta spike* — adjacent (buffer size bounds the page validation range)
  but a separate performance question.

</deferred>

---

*Phase: 149-Firmware Page-Size Seam (dual-repo lockstep)*
*Context gathered: 2026-08-19*
