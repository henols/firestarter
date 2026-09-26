# Phase 59: Correctness Gate + Per-chip Diff + SRAM Audit - Context

**Gathered:** 2026-06-09
**Status:** Ready for planning

<domain>
## Phase Boundary

Close the v1.11 decode-correctness milestone by **proving** the regenerated `firestarter_app/firestarter/data/chip_database.json` (743 chips) is correct chip-by-chip against the pinned pre-milestone baseline, and **documenting** `configure_sram` NVRAM behavior. Three workstreams:

1. **GATE-02 — Per-chip diff vs the immutable baseline.** Produce a reviewed diff of the regenerated DB against `firestarter_app/tools/baseline/chip_database.baseline.json` (Phase 56 GATE-01 snapshot, 734 chips). Every changed chip carries an explicit, cited rationale; **no unexplained diff remains**.
2. **GATE-03 re-confirmation + determinism.** `check_dispatch.py` exits clean (0 errors) across the full 743-chip regenerated set including the new 24-pin EEPROMs (SC#2), and regenerating from the pinned `infoic.xml` snapshot is byte-identical across two independent runs (SC#4).
3. **GATE-04 — `configure_sram` NVRAM behavior audit + documentation.** Blank-check limitation, WP# behavior (DS1225/M48T08 class), RTC-oscillator side effect — documented; escalate to a firmware backlog item ONLY if a real safety issue is found.

**HOST-only milestone.** The firmware sub-repo stays untouched unless the GATE-04 audit surfaces a genuine safety issue (then it becomes a firmware backlog item, not a silent dismissal). Note: `configure_sram` in `firestarter/src/proms/sram.cpp` is presently a near no-op (logs only) — the audit is largely a documentation/behavioral-truth exercise, not a code change.

**Requirements:** GATE-02, GATE-04. (GATE-03 already Complete via Phase 57; SC#2 is re-confirmation across the full regenerated set.)
</domain>

<decisions>
## Implementation Decisions

### GATE-02 — Diff report form & rationale granularity
- **D-01: Re-runnable script, grouped-by-cause.** A committed diff script compares the regenerated DB against the pinned baseline and emits the changed chips. Explanations are **grouped by the root-cause rule** that moved each set of chips (e.g. "these N chips moved pinout → `DIP24_2816` via the 24-pin-EEPROM rule, cited at minipro `database.c`@<sha>"), not one hand-written line per chip. The script doubles as a regression check (re-runnable against the immutable baseline). (Chosen over manual jq + per-chip lines.)
- **D-02: Full-record diff (catch surprises).** The diff covers **every field**, not only the five the success criterion names (`algorithm`, `pinout`, `vpp_mv`, `pulse_duration`, `electrical.type`). Correctness-first (Phase 58 D-01) + guess-table deletion (Phase 58 D-02) can move fields the SC didn't enumerate (flags, `chip_id`, `mem_size`, etc.); a full-record diff surfaces unexpected collateral changes. The five SC fields get **priority rationale**, but no field delta escapes review.

### GATE-02 — Gate strictness (unexplained-diff disposition)
- **D-03: BLOCK — fix `build_db.py`.** An unexplained / surprise diff is treated as a Phase 58 logic bug. The gate is **NOT green** until the change is either explained by a citable principled rule OR `build_db.py` is corrected so the diff disappears (then re-regen, re-diff). There is **no document-and-accept escape hatch.** This honors the SC's "no unexplained diffs remain" literally and matches the correctness-first posture. *(Note: a fix here means re-touching `build_db.py`, which Phase 58 owns — keep the change minimal and cited; loop back rather than rationalize.)*

### GATE-04 — SRAM audit depth & doc layering
- **D-04: Two-layer documentation, pure-doc.** Mirror the SR-1 / shield-revision two-layer pattern: a **planning audit artifact** (audit trail, e.g. `.planning/phases/59-.../59-SRAM-AUDIT.md`) PLUS a **shipped, GitHub-visible doc** (`firestarter_app/doc/sram-nvram-behavior.md` or a comment block in `firestarter/src/proms/sram.cpp` — planner's call on exact location). Keep the two in lockstep. Required content (all three): (a) blank-check limitation — NVRAM/FRAM is never factory-blank; (b) WP# pin behavior for representative families (DS1225 / M48T08 class); (c) RTC-oscillator side effect for timekeepers. **Documentation only.** Escalate to a firmware backlog item **only if** a real safety issue surfaces during the audit — never silently dismiss.

### Phase-close boundary
- **D-05: Stop at the green gate.** Phase 59 delivers only its 4 success criteria. Cutting the v1.11 beta tag + lockstep release is a **separate, operator-gated step** (`/gsd-complete-milestone`) run afterward — consistent with "nothing is stable until I say so." Do NOT fold the beta cut / release prep into this phase.

### Claude's Discretion (planner / researcher)
- Exact diff-script language/form and where it lives in `firestarter_app/tools/` (D-01) — only constraint: re-runnable against the pinned baseline, grouped-by-cause output, full-record coverage.
- Exact filename/location of the SRAM shipped doc (standalone `doc/sram-nvram-behavior.md` vs `sram.cpp` comment block) and the planning audit artifact (D-04).
- How the determinism check (SC#4) is run (two-run byte-compare harness) and whether it's wired into CI or run manually — the SC only requires the byte-identical result is demonstrated.
- Whether GATE-04's audit reads the host-side SRAM path (`configure_sram` dispatch in `firestarter_app`) in addition to the firmware no-op, to ground the documented behavior.
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### v1.11 framing & prior locked decisions (read first)
- `.planning/ROADMAP.md` §"Phase 59" — goal + 4 success criteria; GATE-02/GATE-04 coverage table.
- `.planning/REQUIREMENTS.md` — GATE-02 / GATE-04 text; out-of-scope table (BENCH-01 deferred to v2; firmware untouched unless GATE-04 surfaces a safety fix).
- `.planning/phases/58-pinout-re-derivation-24-pin-eeprom-unblock/58-CONTEXT.md` — Phase 58 D-01 (correctness-first → large diff expected), D-02 (guess tables deleted), D-05 (overrides→rules), D-07 (`DIP24_2816` unblock). The *causes* of the GATE-02 diff originate here.
- `.planning/phases/56-snapshot-field-dictionary-corrected-docs/56-CONTEXT.md` — Phase 56 D-01 live XML fetch, D-03 frozen-output baseline = regression anchor, D-05/D-06 minipro citation convention (permalink + pinned SHA). The diff rationale citations follow this convention.

### Baseline & diff anchor (GATE-02)
- `firestarter_app/tools/baseline/chip_database.baseline.json` — **IMMUTABLE diff anchor.** Verbatim pre-milestone snapshot (Phase 56 GATE-01, 734 chips / 58 manufacturers / 14063 lines, byte-identical to source at Phase 56 start). Added in commit `f92873d`. Do NOT regenerate or mutate it.
- `firestarter_app/firestarter/data/chip_database.json` — the regenerated DB under review (743 chips after the +9 AT28C04/16 unblock).

### Field-decode authority & safety model (rationale source)
- `firestarter_app/doc/infoic-field-dictionary.md` — Phase 56 authoritative source-grounded decode of every infoic.xml field; diff rationales cite this, not re-invent decode.
- `.planning/research/PITFALLS.md` — hazard model (wrong decode → VPP on wrong pin → dead 5V chip); SR-1 checklist source feeding the GATE-04 safety judgment.
- `.planning/research/STACK.md` — minipro `database.c`/`.h` mask semantics — the source the diff citations point at.

### Tooling under change / re-run (HOST-only — `firestarter_app`)
- `firestarter_app/tools/build_db.py` — DB generator; the **only** file touched if D-03 forces a fix for an unexplained diff. Also the determinism subject (SC#4: two runs byte-identical from the pinned `infoic.xml`).
- `firestarter_app/tools/check_dispatch.py` — GATE-03 VPP-safety guard (keyed on `electrical.type`, dynamic `pinouts.json` load). SC#2: re-confirm 0 errors across the full 743-chip set including `DIP24_2816`.
- `firestarter_app/firestarter/data/pinouts.json` — contains `DIP24_2816` (Phase 58 D-07); the new pinout the diff/dispatch must cover.

### SRAM audit (GATE-04)
- `firestarter/src/proms/sram.cpp` — `configure_sram` (currently a near no-op: `LOG_DEBUG_ID_SUB(DBG_CONFIGURING_SRAM)` only). Audit subject; candidate location for the shipped doc comment block.
- `firestarter/include/sram.h` — SRAM handler declarations (read-only context).
- `.planning/project_v17_shield_docs_layering.md` pattern (two-layer meta + sub-repo docs) — the model for D-04's planning-trail + shipped-doc split.

### Upstream source (cited, NOT vendored — Phase 56 D-05)
- minipro `src/database.h`, `src/database.c` — referenced via commit-permalink URLs pinned to one recorded SHA; the citation backing for every grouped diff rationale.
</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **Pinned baseline already exists** — `firestarter_app/tools/baseline/chip_database.baseline.json` was committed in Phase 56 (`f92873d`) expressly as the Phase 59 GATE-02 anchor. No baseline-capture work needed; the diff script consumes it directly.
- **`check_dispatch.py` is the ready-made SC#2 gate** — already keyed on `electrical.type` + dynamic `pinouts.json` load (Phase 57 CR-01), auto-covers `DIP24_2816`. SC#2 is a re-run, not new tooling.
- **Phase 56 citation convention (permalink + pinned SHA)** is the established format for the GATE-02 grouped rationales — reuse it verbatim.

### Established Patterns
- **Live input, frozen output, URL-pinned citations** (Phase 56 through-line) — unchanged. Determinism (SC#4) is the "frozen output" half made testable: same pinned `infoic.xml` → byte-identical DB.
- **Two-layer documentation** (meta planning-canonical + sub-repo operator/GitHub-visible, kept in lockstep) — the shield-revision and SR-1 precedent; D-04 SRAM docs follow it.
- **Reframed-requirement precedent** — Phase 56 D-02 / Phase 58 D-05 reinterpreted requirement *mechanism* with operator sign-off while preserving *intent*. GATE-02 here is the downstream proof that those reframes landed correctly.

### Integration Points & Risks
- ⚠ **Diff blast radius is large by design.** Phase 58's correctness-first + table-deletion will have moved many chips; the +9 count (734→743) is only the unblock — field-level reassignments are expected to be far broader. The grouped-by-cause format (D-01) exists to keep this auditable; the BLOCK disposition (D-03) means a surprise change *stops the gate* rather than getting waved through.
- ⚠ **D-03 can loop back into Phase 58 territory.** If an unexplained diff forces a `build_db.py` fix, that is a re-touch of Phase 58's primary artifact. Keep any such fix minimal, cited, and re-run the full diff + GATE-03 + determinism afterward.
- **GATE-04 is documentation of behavioral truth, not code.** The firmware `configure_sram` is a near no-op today; the audit documents what the SRAM/NVRAM path *does and doesn't* guarantee (no factory-blank, WP#, RTC), so operators don't mistake silence for safety. Only a genuinely-discovered hazard becomes a firmware item.
</code_context>

<specifics>
## Specific Ideas

- Every Phase 59 answer landed on the **strict / thorough** end: re-runnable + grouped-by-cause diff, full-record (not just the 5 SC fields), BLOCK-and-fix on surprises, two-layer SRAM docs. This is the operator's correctness-first posture (carried from Phase 58 D-01) applied to the closing gate: the gate's job is to *prove* the milestone's correctness claim, not to rubber-stamp the regenerated DB. When a tradeoff arises, bias toward catching more / explaining more / blocking on doubt.
- The milestone close is deliberately decoupled: Phase 59 ends at a green gate; the v1.11 beta cut is a separate operator-gated motion ("nothing is stable until I say so").
</specifics>

<deferred>
## Deferred Ideas

- **v1.11 beta tag + lockstep release prep** — explicitly OUT of Phase 59 scope (D-05). Run `/gsd-complete-milestone` afterward, operator-gated.
- **BENCH-01 (real-hardware write/program validation of the unblocked AT28C04/16 EEPROMs)** — deferred to v2 per REQUIREMENTS.md; this milestone closes on source-correctness, not bench-proof. Carried forward from Phase 58.
- **Full `pinouts.json` regeneration from minipro masks** — the ambitious Phase 58 D-04 follow-up; out of scope for closing v1.11.
- **Wiring the SC#4 determinism check into CI** — if useful long-term, a future hardening task; Phase 59 only needs the byte-identical result demonstrated.

</deferred>

---

*Phase: 59-correctness-gate-per-chip-diff-sram-audit*
*Context gathered: 2026-06-09*
