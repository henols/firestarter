# Phase 90: Per-Protocol Bench Validation + Ledger - Context

**Gathered:** 2026-06-26
**Status:** Ready for planning

<domain>
## Phase Boundary

Record the v1.16 rebuild's impact on **real silicon** by bench-proving every protocol
bucket that has on-hand silicon and explicitly marking every bucket that does not, then
author `.planning/v1.16/ledger/PROTOCOL-LEDGER.{md,json}` — one row per protocol bucket
(proposed name, datasheet citation, primitives used, flash delta, verification status),
**composing with — not replacing —** the v1.13 per-family matrix
(`firestarter_app/tools/validation_matrix_spec.json`) and the v1.15 per-chip evidence
(`.planning/v1.15/bench/EVIDENCE.json`).

The firmware under test is the **final recomposed build from Phase 89** (the
primitive-decomposed handlers; Leonardo flash ~25090 B / 87.5%). The recompose changed the
**write-path primitives** (P3 VPP gate, P4 chip-ID compare/report, P5 poll/readback), so the
bench must exercise those paths on silicon — not just reads.

**Bench oracle (ROADMAP-fixed):** Leonardo controller + RURP **Rev 2.0** shield. This oracle
is pinned precisely to avoid the deferred v1.9 shield-fleet read bug.

**In scope:**
- Bench-prove the **4 on-hand protocols** on the recomposed firmware — each earns a PASS via
  **both** a non-destructive read AND a write-cycle A→B (auto-erase) regression against the
  existing v1.15 baseline:
  - **0x05** (FLASH-AMD-STD) via **W29C020**
  - **0x06** (FLASH-AMD-ALT) via **SST39SF040**
  - **0x07** (EPROM-STD) via **W27C512**
  - **0x28** (SRAM-STD / FRAM) via **FM1608**
- Record the **6 no-silicon buckets** (0x0D, 0x0E, 0x10, 0x27, 0x29, 0x34) as explicit
  `UNVERIFIED` rows.
- Carry the **3 open-defect rows** (W29C020-sibling **W29C040/CR-01**, **AM27C020/FUT-06**,
  **2516/FUT-03**) at their current documented status, unmodified.
- Author `PROTOCOL-LEDGER.{md,json}` and store the bench evidence artifacts it references.

**Out of scope:**
- Any firmware/handler change or new primitive (Phase 89 is done; this phase only validates).
- Any DB record change, dispatch-order change, or wire/constant change (frozen world stands).
- Re-litigating / fixing the 3 open defects (CR-01 / FUT-06 / FUT-03) — carried as-is.
- The 0x34 X88C64 programming handler (PCB-blocked, FUT-01).
- Any **lockstep beta cut or gitlink bump** — gitlinks stay **PINNED at b10**
  (a1953c2 / 98b3a92); the `3.0.0b11` cut remains operator-gated.
- Promoting 2516 out of `UNVERIFIED`, or writing any irreplaceable UV part on an unstable
  read path (SAFE-04).

</domain>

<decisions>
## Implementation Decisions

### PASS bar / regression method (Area A)
- **D-01:** **PASS = regression-match to the v1.15 EVIDENCE baseline**, not a standalone
  clean op. Re-run each on-hand chip's operation on the recomposed firmware; PASS requires a
  result **byte-identical** to the v1.15 baseline (same read SHA-256, same write-cycle
  verdict + image SHA). This directly proves the recompose "changed nothing on silicon" —
  the milestone's whole point. (Rejected: standalone-clean-op — proves the op works but not
  equivalence to pre-rebuild; match-where-stable — unnecessary, all 4 chips have clean v1.15
  baselines, see code_context.)
- **D-02:** **Both ops per chip — non-destructive read AND write-cycle A→B.** All 4 chips
  are rewritable and were write-cycled clean in v1.15, and the recompose changed the
  **write-path** primitives (VPP gate / chip-id / poll-readback). A read-only test would not
  exercise the recomposed code, so each chip earns its PASS from **both** a read-SHA
  regression and the write-cycle A→B (auto-erase verdict + image-SHA) regression.
  (Rejected: write-cycle-only — drops the read-path regression; read-only — does not touch
  the recomposed write primitives, weakest proof.)
- **D-03:** **N ≥ 3 byte-identical reads** define a clean read-SHA cell (bench rule: never
  trust N=1; reseat + retry per the v1.15 protocol before recording a verdict). Any read or
  write SHA that **differs** from the v1.15 baseline is recorded **FAIL / INVESTIGATE** (a
  recompose-regression candidate) — **never auto-passed**.

### Ledger composition (Area B)
- **D-04:** **Compose by cross-reference, no data duplication.** `PROTOCOL-LEDGER.json` rows
  reference the v1.15 `EVIDENCE.json` cells (by chip name) and the v1.13
  `validation_matrix_spec.json` family entries (by family/protocol id) as **keys** — it does
  **not** copy their SHA/verdict data, so the two upstream files stay the single source of
  truth and cannot drift. `PROTOCOL-LEDGER.md` is the human-readable view of the same rows.
  (Rejected: embed-snapshot-subset — duplicates data, drift risk; you-decide-schema —
  composition principle is the load-bearing decision, locked here. Exact JSON field
  names/ordering are planner/researcher discretion within this principle.)

### Bench session mechanics (Area C)
- **D-05:** **Claude drives the bench via USB passthrough; operator gates each silicon op.**
  Claude flashes the **final recomposed Phase-89 firmware** and runs each protocol op over
  the devcontainer USB passthrough; the operator confirms **Rev 2.0** silkscreen, confirms
  **controller/port identity per task** (ttyACM* numbers shuffle across replug), and
  authorizes each live silicon operation. Matches the v1.15 bench workflow. (Rejected:
  hybrid reads-auto/writes-gated and operator-runs-all — both viable but the
  Claude-drives + operator-authorizes model is the proven v1.15 pattern.)
- **D-06:** **Gitlinks stay PINNED at b10** (a1953c2 / 98b3a92); **no lockstep beta cut**
  this phase (firmware-only milestone; the `3.0.0b11` cut is operator-gated and out of
  scope). Per `feedback_chip_out_before_sideload`: **Leonardo is EXEMPT** from the
  chip-out-before-sideload rule (only Uno-class boards need it) — but the operator still
  authorizes each flash.

### UNVERIFIED + open-defect row shape (Area D)
- **D-07:** **Full UNVERIFIED rows; status-only defect rows.** Each of the 6 no-silicon
  buckets (0x0D, 0x0E, 0x10, 0x27, 0x29, 0x34) gets a **complete** row — proposed name,
  **datasheet-representative chip citation**, primitives used, flash delta — with
  `verification_status: UNVERIFIED` and `reason: "no on-hand silicon"`. The 3 open-defect
  rows reproduce their **current documented status verbatim** (the CR-01 / FUT-06 / FUT-03
  id + one-line disposition + a link to the source record) — **no re-litigation, no status
  change**. (Rejected: minimal UNVERIFIED rows — loses the per-bucket datasheet/primitive
  context that makes the ledger a standalone v1.16 picture.)

### Carried from milestone safety model (LOCKED — not re-discussed)
- **D-08:** **SAFE-04 throughout.** Over-voltage stays blocked at the firmware VPP check
  (`eprom.cpp:282`, `flash_intel.cpp:65`); the host `chip_resolver.resolve_chip` guard
  (`chip_resolver.py:55`) is **never bypassed**; **2516 stays `UNVERIFIED`** and no
  irreplaceable UV part is written on an unstable read path.
- **D-09:** **Mandatory PASS fields (ROADMAP SC#2).** An authoritative PASS row cannot be
  recorded without `oracle: leonardo+Rev2.0` and **non-empty evidence references** (the
  stored bench artifact paths). A row missing either field is not a PASS.
- **D-10:** **Frozen world stands.** No DB / dispatch / wire change; this phase validates
  silicon and authors the ledger only — no `firestarter` or `firestarter_app` source change
  expected beyond rerunning existing gates.

### Claude's Discretion
- Exact `PROTOCOL-LEDGER.json` field names, row ordering, and `.md` table layout (within the
  compose-by-cross-reference principle of D-04).
- Bench evidence artifact storage layout/paths (consistent with the v1.15
  `.planning/v1.15/bench/` convention) — the paths just have to be the non-empty evidence
  references D-09 requires.
- Chosen N for reads is **≥ 3** (D-03) but the exact harness invocation (e.g. reuse of
  `firestarter dev consistency-check`) is planner discretion.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase / milestone definition
- `.planning/ROADMAP.md` — v1.16 §"Phase 90: Per-Protocol Bench Validation + Ledger" (goal +
  4 success criteria), plus the v1.16 milestone header for the compose-with-not-replace framing.
- `.planning/REQUIREMENTS.md` — **LEDGER-01/02/03** (the ledger contents + compose rule),
  **SAFE-04** (over-voltage blocked, host guard never bypassed).
- `.planning/STATE.md` — current milestone state; Phase 89 close decisions (final flash
  25090 B; firmware HEAD); gitlink PINNED-at-b10 posture; deferred-items table (CR-01 /
  FUT-03 / FUT-06 / FUT-01 dispositions to carry verbatim).

### The artifacts the ledger composes with (compose, don't replace — D-04)
- `.planning/v1.15/bench/EVIDENCE.json` — the per-chip v1.15 baseline (read SHAs +
  write-cycle A→B verdicts) the regression matches against; `locked_columns` +
  `evid_extension_columns` define the cell schema; `phase82` block defines the write-cycle
  op + verdict taxonomy + `gen_test_image.py` seeds.
- `.planning/v1.15/bench/EVIDENCE.md` — human-readable companion to the above.
- `firestarter_app/tools/validation_matrix_spec.json` — the v1.13 per-family matrix the
  ledger cross-references by family/protocol id.

### Protocol vocabulary + invariants (the row identities)
- `firestarter/doc/PROTOCOLS.md` — **§0** canonical 12-bucket set (hex → handler →
  datasheets folder slug → algorithm-axis name) = the ledger's row identities; **§1**
  per-bucket NAME-01 facets + datasheet citations; **§3** INV-01..09 matrix.
- `firestarter/datasheets/README.md` + `firestarter/datasheets/<hex>-<NAME>/` — the
  datasheet citations for both on-hand chips and the **datasheet-representative** chip per
  UNVERIFIED bucket (D-07).

### Recompose deliverable being validated (Phase 89)
- `.planning/phases/89-incremental-primitive-recompose/89-FLASH-LEDGER.md` — the per-step
  flash deltas (P7 0 B / P4 −164 B / P3 −402 B / P5 +2 B = −564 B net; final 25090 B) that
  feed the ledger's "flash delta" + "primitives used" columns.
- `.planning/phases/89-incremental-primitive-recompose/89-CONTEXT.md` — the primitive
  definitions (P4 `chip_id_report`, P3 `vpp_check_window`, P5 `poll_readback`, P7 SDP tables)
  and which call sites/protocols each touches → the "primitives used" per-bucket mapping.
- `firestarter/src/proms/primitives.{h,cpp}` — the recomposed primitives under test.

### Bench substrate + safety targets
- `firestarter/CLAUDE.md` — build/test/flash commands (Leonardo 1024 B buffer; 250000 baud).
- `firestarter_app/tools/gen_test_image.py` — deterministic A/B image generator (seed 1 / 2)
  reused for the write-cycle regression (per EVIDENCE `phase82`).
- Firmware over-voltage VPP check (`firestarter/src/proms/eprom.cpp:282`,
  `flash_intel.cpp:65`) + host `firestarter_app/firestarter/chip_resolver.py:55`
  `resolve_chip` guard — SAFE-04 / D-08 verification targets.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **v1.15 bench harness + EVIDENCE schema** — `EVIDENCE.json` already defines the cell
  shape, the write-cycle op (`write_A+verify_A → write_B+verify_B`), the verdict taxonomy,
  and the `gen_test_image.py` seed convention. Phase 90 **reuses** this — the ledger
  cross-references these cells; it does not invent a new bench format.
- **All 4 on-hand chips have a clean v1.15 baseline for BOTH ops** (confirmed from
  `EVIDENCE.json`): each of W29C020 / SST39SF040 / W27C512 / FM1608 has a `read+blank_check`
  PASS cell AND a `write_A→write_B` (auto-erase) PASS cell. So D-01 regression-match has a
  byte-exact target for every cell — no "match-where-stable" fallback needed for these 4.
  (FM1608's read cell carries a benign "Empty input" blank-check note on FRAM — the read
  itself was N=3 identical and PASS.)
- **`firestarter dev consistency-check`** — the N-read consistency diagnostic (carried since
  v1.6) is the natural tool for the D-03 N≥3 read-SHA cells.
- **USB passthrough bench access** (`reference_usb_passthrough_bench`) — Claude can flash,
  read serial, and run write/read ops on the operator's bench from the devcontainer; only
  photos / multimeter / chip-handling are operator-only. Enables D-05.

### Established Patterns
- **Compose-don't-replace** — same posture v1.16 took for the v1.13 matrix throughout; the
  ledger is a new composing artifact, the upstream evidence files stay authoritative (D-04).
- **Bench preconditions per task** (`feedback_verify_port_identity_each_task`,
  `user_shield_revisions`) — confirm controller identity per port + ask which silkscreen rev
  at every bench task; the EEPROM hw_revision byte cannot distinguish Rev 2.0 / 2.2 / Rev 0.
- **Leonardo chip-out exemption** (`feedback_chip_out_before_sideload`) — only Uno-class
  boards need chip-out before sideload; the Leonardo oracle does not.

### Integration Points
- The ledger's "flash delta" + "primitives used" columns come straight from the Phase-89
  flash ledger + primitive call-site map — no re-measurement needed, just cross-reference.
- The "datasheet citation" column reuses the Phase-85/86 `datasheets/` tree + PROTOCOLS.md
  §1 anchors already committed.
- 0x05 bucket carries **two** chips: W29C020 (PASS, on-hand) and its sibling W29C040
  (open CR-01 defect, status-only) — the row reflects both per D-07.

</code_context>

<specifics>
## Specific Ideas

- The bench must exercise the **recomposed write path** (VPP gate / chip-id / poll-readback),
  so the write-cycle A→B is the load-bearing op, not the read (D-02). A read-only ledger
  would look complete but prove nothing about the actual code that changed.
- Regression-match against v1.15 is a **two-way signal**: an identical SHA proves the
  recompose was behavior-preserving on silicon; a mismatch is a recompose-regression alarm
  (FAIL/INVESTIGATE, D-03) — exactly the impact the milestone exists to record.
- Keep the ledger a standalone v1.16 "picture": full rows for UNVERIFIED buckets (with
  datasheet-representative chip + primitives) so a reader sees all 12 buckets in one place,
  while the 3 open defects point back to their source records without re-opening them (D-07).

</specifics>

<deferred>
## Deferred Ideas

- **Fixing the 3 open defects** — W29C040/CR-01 (flash4 256B page-write, reopened Phase-74
  Wave-2), AM27C020/FUT-06 (0x08 32-pin write/VPP path), 2516/FUT-03 (0x0B read
  instability). Carried at documented status only; each is its own future work item.
- **0x34 X88C64 programming handler** — PCB-blocked (FUT-01); stays `not_implemented` /
  UNVERIFIED.
- **Acquiring silicon for the 6 no-silicon buckets** — would convert UNVERIFIED → bench-proven
  in a future milestone; out of v1.16 scope.
- **Lockstep beta cut `3.0.0b11` + gitlink bump** — standing operator-gated release item;
  not this phase.

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 90-per-protocol-bench-validation-ledger*
*Context gathered: 2026-06-26*
