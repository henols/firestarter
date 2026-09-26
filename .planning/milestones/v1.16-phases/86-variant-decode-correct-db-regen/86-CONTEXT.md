# Phase 86: infoic.xml Variant-Field Decode + Correct DB Regen - Context

**Gathered:** 2026-06-25
**Status:** Ready for planning

> **This phase was inserted mid-discussion** (operator decision, 2026-06-25) while
> discussing the *original* Phase 86 (Naming + Documentation Pass). The naming pass
> moved to **Phase 87**; golden traces → 88; recompose → 89; bench ledger → 90.
> See `.planning/ROADMAP.md` v1.16 §Scope amendment and `.planning/REQUIREMENTS.md`
> §Scope AMENDMENT.

<domain>
## Phase Boundary

Make `build_db.py` generate a **correct** `chip_database.json` by decoding the
`infoic.xml` `variant` field **in full** (the low byte is already consumed for
pinout family; this phase cracks the previously-undecoded **high byte**), so that
`electrical.type`, `algorithm`, and `pinout` are derived from **principled
variant-driven decode** instead of the hand-maintained Rule 1 / Rule 2 / Rule 3
override stack — which is **deleted**.

**Why this exists:** `infoic.xml` is the ground truth, and it carries signal we
don't extract. Verified during discussion:
- **FM1608** raw entry: `type="4"`, `protocol_id="0x07"`, **`variant="0x4126"`**.
  The DB's `algorithm:40` (0x28) is *derived* by `build_db.py` Rule 3, not read
  from `infoic.xml`. The recurring "FM1608 0x40" in old memory was a **decimal-40
  ↔ hex-0x28 conflation** — the true identity is proto 0x07 + type 4 + variant 0x4126.
- **X88C64** raw entry: `type="1"`, `protocol_id="0x34"`, **`variant="0x3100"`**,
  `flags="0x00414200"`. `flags & 0x10 == 0`, so the "electrically-erasable" flags
  rule **misses it** → it falls through to the `UV-EPROM` default. That is *why*
  its `electrical.type` is wrong today.
- The `variant` high byte is structured across the catalog (0x41=FM1608, 0x31=X88C64,
  plus 0xa1/0x21/0x71/0xd4/0xd5/0xd7… families) and is **entirely undecoded** in
  `build_db.py` today.

**In scope:** decoding `variant` (low + high byte); rewriting `build_db.py`
classification; deleting Rule 1/2/3; regenerating `chip_database.json`; re-pinning
the diff_db baselines; acquiring datasheets needed to resolve high-byte ambiguity.
**Host-only** (`firestarter_app`): `build_db.py` + `chip_database.json` + tool baselines.

**Out of scope:** any firmware change (the recompose is Phases 88–89); the naming/
documentation vocabulary (Phase 87); implementing the 0x34 X88C64 *programming
handler* (still PCB-blocked, FUT-01 — this phase only fixes its `electrical.type`
decode); fixing the open write-path defects (CR-01 / FUT-06 / FUT-03 preserved).

</domain>

<decisions>
## Implementation Decisions

### Scope posture (the pivot)
- **D-01:** **Act on the variant field now** — generate a correct DB rather than
  documenting an incorrect one. Operator: *"this is super important… we can save a
  lot of code… we don't need to have some edge cases."* The "edge cases" are exactly
  the `build_db.py` Rule 1/2/3 override blocks.
- **D-02:** This is a **deliberate scope amendment** to v1.16, not scope creep. The
  original "pure behavior-preserving / DB-frozen / two-decode-corrections-only" lock
  is lifted **for this phase only**. The recompose phases (88–89) remain DB-frozen
  against the **new re-pinned baseline**.
- **D-03:** **Inserted as its own phase BEFORE the naming pass** — you document the
  *corrected* world, not the about-to-change one; and you cannot freeze the DB
  (recompose safety model) and rewrite it in the same window.

### Variant decode (VAR-01)
- **D-04:** Decode **both** bytes. Low byte (`variant & 0xFF`) is the existing
  pinout-family discriminator; the **high byte** is the new work. Ground every
  classification-affecting value in **minipro source (`database.c`)** and/or a
  **committed datasheet**.
- **D-05:** **Acquire more datasheets if needed** to crack high-byte meaning
  (operator-authorized). Any value no source resolves → **documented honest gap**,
  never guessed (matches the milestone's explicit-UNVERIFIED ethos).

### Override-stack collapse (VAR-02)
- **D-06:** **Full replacement — delete Rule 1, Rule 2 (WARNING-5), Rule 3.** Operator
  chose the most aggressive option. Variant decode becomes the *sole* classifier.
  *(Claude recommended keeping the rules as asserted-equivalent guards; operator
  overruled in favor of full deletion — which is safe because of D-08.)*

### Correctness + safety gate (VAR-03 / VAR-04)
- **D-07:** **Every changed record must be explained by a cited variant-decode rule**
  — reuse the v1.11 GATE-02 classified-diff pattern in `diff_db.py`. Re-pin
  `chip_database.baseline.json` + `dispatch_baseline.json` to the new correct DB.
- **D-08:** **`check_dispatch.py` 0-violations is the structural safety backstop** that
  makes deleting WARNING-5 safe. It already asserts (type-string-independent) that no
  chip routes to `configure_eprom` (12V VPP) on a pinout with no VPP pin. The 12V-on-a-
  5V-pin hazard is therefore caught structurally even with the special-case gone.
- **D-09:** **On-hand bench-proven chips' wire values must not silently move.** The 11
  v1.15 EVIDENCE chips keep `algorithm`/`vpp_mv`/`pinout`, OR any moved value is
  flagged for **Leonardo + RURP Rev 2.0 re-bench** before Phase 90 (operator chose the
  bench-aware gate over software-only).

### Non-upstream chip support (VAR-05 — added 2026-06-25 operator directive)
- **D-10:** **Support 2516 and 2532 even though they are absent from `infoic.xml`.** Operator:
  *"2516 and 2532 are odd balls but we shall support them anyway, even if they aren't in the
  infoic.xml."* These are 24-pin oddballs (non-JEDEC pinouts; 2532 ≠ 2732) that upstream omits.
  Mechanism (operator-chosen): a **curated, provenance-cited non-upstream supplement** (e.g.
  `tools/extra_chips.json`) that `build_db.py` merges into `chip_database.json` **after** the
  `infoic.xml` decode — shipped first-class, NOT per-operator `~/.firestarter/database.json`
  edits. The supplement is the legitimate home for "physically real, upstream-absent" chips;
  it is **not** a return of the deleted Rule 1/2/3 (those misclassified chips already *in*
  infoic.xml — a categorically different concern from chips with no upstream record at all).
- **D-11:** **Supplement records go through the same gates** as decoded chips — `check_dispatch.py`
  0 violations (24-pin VPP-pin safety matters for these UV parts) and `diff_db.py` shows them as
  cited "non-upstream supplement" rows against the re-pinned baseline (D-07 extends to cover them).
  Each supplement field cites a datasheet (the 2516 datasheet is already committed from Phase 85;
  acquire a 2532 datasheet if needed per D-05). **2516 keeps its SAFE-04 UNVERIFIED status** —
  it becomes resolvable but is NOT graduated to a write-proven part; its host guards stay. This
  also revises the original 86-01 "2516 stays absent" assertion (now: 2516 is present via the
  supplement, UNVERIFIED, wire values not silently moved).

### Claude's Discretion
- Exact supplement file format/location (`tools/extra_chips.json` vs inline table) and how its
  records are fenced/labelled non-upstream — planner/executor's call, as long as it merges
  post-decode, ships in `chip_database.json`, and passes the D-07/D-08 gates.
- Exact decode-table structure in `build_db.py`, the high-byte field-naming, and
  whether the decode is a lookup table vs. bitfield parse — planner/executor's call,
  as long as Rule 1/2/3 are gone and the gates (D-07/D-08/D-09) hold.
- How datasheet provenance for high-byte resolution is recorded (extend
  `datasheets/README.md` provenance columns or a decode-notes doc).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase / milestone definition
- `.planning/ROADMAP.md` — v1.16 §"Scope amendment" + §"Phase 86: infoic.xml
  Variant-Field Decode + Correct DB Regen" (goal, 5 success criteria, the renumber).
- `.planning/REQUIREMENTS.md` — VAR-01..04 (this phase) + SAFE-04; §"Scope AMENDMENT".

### Ground truth + the decode pipeline (most important)
- `infoic.xml` — minipro upstream, fetched by `build_db.py` from
  `https://gitlab.com/DavidGriffith/minipro/-/raw/master/infoic.xml`. **The ground
  truth.** Per-chip attributes: `type`, `protocol_id`, **`variant`**, `voltages`,
  `flags`, `pulse_delay`, sizes, `pin_map`. (FM1608 ≈ line 170574; X88C64 ≈ 233970.)
- `firestarter_app/tools/build_db.py` — the decode to rewrite. Today: `variant_lo =
  variant & 0xFF` (lines ~193–223 pinout family); **Rule 1** (28C-EEPROM force-0x0D,
  ~516–524); **Rule 2** (WARNING-5 flip, ~552–571); **Rule 3** (type=4 FRAM/SRAM→0x28,
  ~583–602). `MINIPRO_XML_URL` at line 11.
- minipro source `src/database.c` (same GitLab repo) — authoritative semantics for
  the `variant`/`pin_map`/`type` fields; consult to ground the high-byte decode.

### Gates + baselines to re-pin
- `firestarter_app/tools/check_dispatch.py` — the structural VPP-safety gate (D-08);
  must exit 0 violations on the regenerated DB.
- `firestarter_app/tools/diff_db.py` — classified per-chip diff (D-07); v1.11 GATE-02
  pattern (cite a root-cause rule per changed chip).
- `firestarter_app/tools/baseline/chip_database.baseline.json` +
  `firestarter_app/tools/baseline/dispatch_baseline.json` — re-pin to the correct DB.
- `firestarter_app/firestarter/data/chip_database.json` — regenerated output (744 chips).

### Field-decode precedents (reuse, don't reinvent)
- `.planning/v1.11-PROTOCOL-ENUMERATION.md` + `.planning/milestones/v1.11-ROADMAP.md`
  — the prior "complete infoic.xml decode" milestone: field dictionary, decode-bug
  fixes, `resolve_pinout_key`, GATE-02 classified-diff. This phase extends that work
  to the variant high byte.
- `.planning/research/SUMMARY.md` + `PROTOCOLS.md` — 12-bucket map (note: SUMMARY's
  "FM1608 algorithm 40 = 0x28" is the *derived* value, corrected here to proto 0x07 +
  variant 0x4126 ground truth).
- `firestarter/datasheets/README.md` — Phase 85 datasheet index + provenance columns.
- `.planning/v1.15/bench/EVIDENCE.{md,json}` — the 11 on-hand bench-proven chips whose
  wire values D-09 protects.

### Host toolchain discipline (SAFE-06 carries over)
- `firestarter_app/CLAUDE.md` — build_db pipeline + WARNING-5 writeup + the ruff/format/
  mypy/pytest CI gate (validate against **py3.11**, not the 3.12 devcontainer;
  generated `messages.py` is never hand-normalized).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`diff_db.py` classified-diff (GATE-02)** — already groups changed chips by cited
  root-cause rule and exits 1 on any unexplained diff. Reuse verbatim for D-07; the
  "rules" become the variant-decode rules.
- **`check_dispatch.py`** — structural VPP-safety gate; already type-string-independent
  (it keys on pinout VPP-pin presence). No change needed; it is the D-08 backstop.
- **`build_db.py` `variant_lo` decode (~lines 193–223)** — the existing low-byte
  pinout-family logic is the template/starting point for the fuller decode.

### Established Patterns
- **v1.11 decode-correctness milestone** is the direct precedent: source-grounded
  field dictionary → re-derived `build_db.py` → classified diff gate → re-pin baseline.
  This phase is "v1.11 part 2: the variant field."
- **`infoic.xml` is fetched, not vendored** (`MINIPRO_XML_URL`); the decode must be
  reproducible against upstream. (A `tools/infoic.xml` local copy is referenced in
  `firestarter_app/CLAUDE.md` — confirm whether the pipeline reads local or remote.)

### Integration Points
- Output `chip_database.json` feeds `EpromDatabase` → `convert_to_programmer()` → the
  wire `algorithm`/`vpp_mv`/`pinout`. A wrong decode here is a **hardware-damage path**
  (12V on a 5V pin) — hence D-08/D-09 are non-negotiable gates.
- The corrected FM1608/X88C64 classifications are consumed by Phase 87's vocabulary
  doc (documented there, delivered here).

</code_context>

<specifics>
## Specific Ideas

- Operator's exact framing: *"It's the info.xml that is the ground truth and we shall
  try to understand and extract as much information from it as possible, to support
  our code."* — this is the governing principle for the phase.
- Concrete proof points to anchor the decode on:
  - FM1608: `type=4, proto=0x07, variant=0x4126` → must resolve to SRAM_STD (0x28).
  - X88C64: `type=1, proto=0x34, variant=0x3100, flags=0x00414200` → must resolve to
    `electrical.type` EEPROM (stays `protocol-not-implemented`).
- High-byte value census already started (from `infoic.xml` survey): 0x11/0x13/0x21/
  0x71/0xa1/0xd4/0xd5/0xd7/0x5e/0x5d… recur — structured, worth a systematic table.

</specifics>

<deferred>
## Deferred Ideas

- **Naming / documentation vocabulary** — Phase 87 (the displaced original Phase 86).
  Documents the corrected DB this phase produces; decisions already captured during
  this discussion for that phase: vocab doc at `firestarter/doc/PROTOCOLS.md`
  (single canonical, GitHub-visible); two-name scheme (keep `datasheets/` folder slugs
  + add descriptive algorithm-axis name column, NO folder rename); inline per-handler
  rationale header-comments citing datasheets + full prose in PROTOCOLS.md; all **9**
  one-off invariants via matrix-first traceability + gap-fill native tests.
- **Implementing the 0x34 X88C64 programming handler** — still PCB-blocked (FUT-01);
  this phase only corrects its decode.
- **Open write-path defects** (W29C040/CR-01, AM27C020/FUT-06, 2516/FUT-03) — preserved
  as-is; not touched by the decode rewrite.
- **Firmware-side consequences of changed wire values** — if a chip's `algorithm`
  moves, firmware behavior for it changes; surfaced via D-09 and resolved at Phase 90
  bench, not here.

</deferred>

---

*Phase: 86-variant-decode-correct-db-regen*
*Context gathered: 2026-06-25*
