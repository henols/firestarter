# Phase 84: DB Decode Audit + Conditional Defect RCA + Milestone Evidence Consolidation - Context

**Gathered:** 2026-06-24
**Status:** Ready for planning

<domain>
## Phase Boundary

The **closing phase of v1.15**. Three bundled deliverables:

1. **Consolidated decode-correctness audit (SC#1):** confirm all 11 chips' real-silicon behaviour
   matches the DB (pinout, VPP, electrical type, algorithm, size), or flag each mismatch with a
   disposition — written as a **new standalone doc** (`.planning/v1.15/DECODE-AUDIT.md`).
2. **Conditional defect RCA + fix (FIX-01, SC#2/#3):** root-cause the defects the bench surfaced;
   ship a **bounded firmware fix** (the VPP-skip directive) + a **host-side tooling fix** (FM1608
   blank-check), re-verify on Leonardo + Rev 2.0; RCA-and-defer the deeper write-path defects.
3. **Milestone evidence consolidation:** finalize EVIDENCE.{md,json}, correct cosmetic DB labels,
   and clean up overstated traceability rows flagged by the v1.15 milestone audit.

**GRAD-03 (inherited from Phase 83 per D-01):** the irreplaceable **2516** VPE-rail write proof.
Per **D-22 below, the 2516 is read-revalidated ONLY — never written this phase.** GRAD-03's write
proof therefore stays **DEFERRED** (FUT-03 best-effort open) regardless of read stability.

**In scope:**
- New decode-audit doc consolidating 11-chip silicon-vs-DB findings + dispositions.
- **Firmware fix (dual-repo lockstep, ALLOWED this phase):** gate VPP error/warning checks off
  operations that do NOT drive VPP (`read` + `blank-check`) — honoring the operator directive.
  Scope-bounded to the VPP-skip directive only (NOT the deeper 0x0B shared-pin read-level driving,
  NOT the 0x08/flash4 write paths).
- **Host-side fix:** the FM1608 / FRAM (0x40) blank-check "Empty input" tooling gap.
- **DB label corrections:** SST39SF040 `Flash/EEPROM`→flash3/Flash and FM1608 `SRAM`→FRAM, via the
  correct codegen layer (see D-40 — NOT a hand-edit), verified to be label-only (no dispatch /
  FLAG_CAN_ERASE perturbation) via diff_db.py + check_dispatch.py + host suite.
- **RCA + confirmatory re-bench** of (a) AM27C020 0x08 write (0 bits programmed) and (c) W29C040
  flash4 256B-page write — confirm root cause on the bench, then fix-if-trivial or formally defer.
- **2516 read re-validation** (read + blank-check + decode) after the VPP-skip fix — no write.
- **Traceability cleanup:** annotate REWR-01/02/04 with their silicon FAIL/deferral dispositions;
  fix the cosmetic UV-01..04 checkbox drift.

**Out of scope / deferred:**
- **2516 write proof (GRAD-03 / SC#4 / FUT-03 close)** — DEFERRED, best-effort (D-22). Read
  revalidation only.
- Deeper firmware fixes: 0x0B shared-OE/VPP active read-level driving; 0x08 AM27C020 write/VPP
  path; W29C040 flash4 256B-page — RCA + bench-confirm, then **defer** unless the re-bench shows a
  trivial fix (D-31/D-32).
- REWR-02 positive 0x08 write PASS (no functional 0x08 rewritable chip on hand → FUT-05).
- The v1.9 read-bug RCA (Phase 45 → FUT-C); pushing 2516 upstream (FUT-B).
- Any new harness or third-party dep (reuse-first).

</domain>

<decisions>
## Implementation Decisions

### Firmware-touch posture (Area 1)
- **D-10 — Firmware change ALLOWED this phase (dual-repo lockstep).** Phase 84 may ship a firmware
  fix, accepting the full firmware gate: `pio test -e native` + Leonardo flash ≤ ~90%, and firmware
  diverging from the currently-pinned `b10`. This is the only way to honor the operator's
  2026-06-24 VPP-skip directive and is the candidate path to stabilizing the 0x0B read.
- **D-11 — Firmware fix bounded to the VPP-skip directive ONLY.** Gate the VPP error/warning checks
  (`VPP is high/low`) off operations that do not drive VPP — `read` and `blank-check` — in
  `firestarter/src/firestarter.cpp` (init VPP gate) with **host parity** in
  `firestarter_app/firestarter/eprom_operations.py`. This clears the chip-1 `18.8V>12.0V` read
  refusal and the benign `VPP is low` read warnings. Do **NOT** in this phase: actively drive the
  0x0B shared OE/VPP pin to a clean read level, touch the 0x08 write/VPP path, or touch flash4 —
  those are RCA-and-defer (D-31/D-32).
- **D-12 — Versioning/beta-cut of the firmware change is a milestone-close mechanic, NOT decided
  here.** The v1.14 `3.0.0b11` lockstep beta cut is already operator-gated with gitlinks pinned;
  how this new firmware delta folds into a beta cut is deferred to `/gsd-complete-milestone` /
  operator authorization. Keep the firmware on the `v1.15-…` sub-repo branch; do not bump version
  or cut a tag inside this phase.

### 2516 / GRAD-03 posture (Area 2)
- **D-20 — 2516 read is re-attempted (N≥3) AFTER the VPP-skip fix** to see whether the directive
  fix alone stabilizes the 0x0B read (Phase 81 was 3 distinct SHAs, VPP pinned 15.3V on the shared
  OE/VPP pin).
- **D-21 — Re-validate the 2516 read ONLY; never write it this phase.** Even if the read
  stabilizes, the irreplaceable 2516 is **not written, not preserve-dumped** — only a stabilized
  read + blank-check + decode validation is recorded. This maximally protects the single
  irreplaceable part.
- **D-22 — GRAD-03 write proof stays DEFERRED regardless; FUT-03 remains OPEN (best-effort).**
  Consequence: SC#4 (2516 bench-proven via write) **cannot be satisfied** this phase by design.
  Record GRAD-03/FUT-03 as a documented best-effort deferral (consistent with v1.14 D-07 and the
  operator's accept-close-on-intentional-deferrals pattern). The D-08 PASS bar (Phase 83 CONTEXT)
  is preserved for whenever a write is eventually attempted.

### FIX-01 defect scope (Area 3)
- **D-30 — FM1608 / FRAM (0x40) blank-check "Empty input" gap: FIX host-side this phase.**
  Close the tooling gap in the host read/blank-check path (`eprom_operations.py` / `cli_handlers`),
  pin with a test, host suite green. Low-risk, in-posture; FM1608 already PASSed its write via
  direct `write -b`, so this is tooling polish, not a silicon fix.
- **D-31 — (a) AM27C020 0x08 write (0 bits programmed) and (c) W29C040 flash4 256B-page write:
  RCA + confirmatory re-bench, then fix-if-trivial else defer.** Re-bench both on Leonardo + Rev
  2.0 to confirm the root cause (retry 0x08 after the VPP-skip fix; retry W29C040 with the
  datasheet 256B page per the CR-01 todo). If the re-bench reveals a trivial fix, take it; otherwise
  record a disposition + named future tracker (0x08 → future; W29C040 flash4 → reopen Phase-74
  Wave-2 / CR-01).
- **D-32 — Genuine-silicon FAILs are NOT FIX-01 material.** W27E512 and W27E040 stuck-bit erase
  FAILs are deterministic silicon wear (identical offset/value every reseat), not DB/algo/firmware
  defects — record as silicon-limited dispositions only.
- **D-33 — Folded todos** (see Folded Todos subsection): the VPP-skip todo IS the D-11 firmware
  fix; the flash4 CR-01 todo is the D-31 (c) root-cause tracker.

### DB decode audit + close posture (Area 4)
- **D-40 — EDIT the DB to correct the 2 cosmetic electrical.type labels** (SST39SF040
  `Flash/EEPROM`→flash3/Flash; FM1608 `SRAM`→FRAM). **CRITICAL HOW-constraint:** `electrical.type`
  is **codegen'd by `tools/build_db.py`** from minipro `infoic.xml` AND consumed by
  `firestarter/ic_layout.py` for **FLAG_CAN_ERASE** derivation (Phase 77). Therefore:
  (1) the correction must be made at the **build_db.py derivation / per-chip override layer, NOT a
  hand-edit of `chip_database.json`** (a hand-edit regenerates away);
  (2) it MUST be verified **label-only** — `diff_db.py` must show a clean delta limited to these
  two chips' type strings with **NO change** to FLAG_CAN_ERASE, VPP, pinout, algorithm dispatch;
  (3) `check_dispatch.py` (full-DB VPP-safety gate) + `diff_db.py` + host suite must be green;
  (4) confirm **no collateral change to other chips** sharing the same infoic flags. If the edit
  cannot be made label-only / risks perturbing CAN_ERASE or other chips, STOP and re-surface to the
  operator before shipping.
- **D-41 — Annotate REWR-01/02/04 traceability with silicon dispositions** in REQUIREMENTS.md
  (W27E512/W27E040 genuine stuck bits = silicon-limited; W29C040 flash4 → (c) re-bench/defer;
  REWR-02 → FUT-05 no functional 0x08 chip). Also fix the cosmetic UV-01..04 `[ ]` checkbox drift.
- **D-42 — Consolidated decode audit = NEW doc `.planning/v1.15/DECODE-AUDIT.md`.** Standalone
  milestone-close artifact cross-referencing EVIDENCE.{md,json}; the existing EVIDENCE record stays
  the raw per-chip log.
- **D-43 — Milestone close = best-effort with documented deferrals.** Phase 84 closes with: VPP-skip
  fw fix + FM1608 host fix + DB label corrections + decode audit + re-validated 2516 read, and
  documented deferrals for GRAD-03/FUT-03 (2516 write), 0x08 AM27C020, W29C040 flash4, REWR-02
  (FUT-05). FIX-01 closes as "fixed where in-posture; deeper write-path defects RCA'd + deferred
  with rationale" — NOT as "all clean". (Operator owns the actual `/gsd-complete-milestone` call.)

### Carried forward (locked — not re-discussed)
- **D-50 — Board lock:** Leonardo + RURP Rev 2.0 ONLY is authoritative for any write/verify/read
  (SAFE-01/03). Per task: verify `controller:` port identity after any USB event, live
  `r1 ≈ 270000` readback, **ASK the operator which silkscreen shield rev is mounted**. Leonardo is
  chip-OUT-sideload-EXEMPT. (Phase 81/82/83 D-09.)
- **D-51 — SAFE-02 software gate:** host suite green **including the 0xA4 `ack_data=False` guard**
  (`test_init_phase_data_frames_not_acked`) before any bench session; validate `ruff check` +
  `ruff format --check` against the **CI scope (`firestarter/ tests/`) and CI target (py3.9/3.11)** —
  the devcontainer Py3.12 masks CI; pre-existing `tools/`-tree I001/UP031 findings are out-of-CI-scope
  (do not mask, do not "fix" as part of this phase). (Phase 83 D-10.)
- **D-52 — Reuse-first, no new harness (EVID-02):** `dev write-cycle`, `dev consistency-check
  --runs 3` (N≥3 read oracle), `tools/gen_test_image.py`, `write_test.sh`. Only new artifacts are
  the DECODE-AUDIT.md doc + EVIDENCE appends + the targeted fixes/tests.
- **D-53 — Non-vacuous PASS bar (EVID-03):** every PASS proven by a trustworthy Leonardo read
  (N≥3 byte-identical / SHA-matched) plus a negative control (wrong-file `verify` exits non-zero).
- **D-54 — Write-failure disposition (D-14 carry):** reseat + retry up to N=2, then record FAIL /
  ANOMALY and continue; the 2516 is exempt (never written, D-21).

### Claude's Discretion
- Exact location/structure of the DECODE-AUDIT.md doc (per D-42 it is a new doc under
  `.planning/v1.15/`); table layout and cross-reference style.
- Whether the firmware VPP-skip gate is keyed on the operation type, the FLAG bits, or the
  presence of a VPP-driving step — the researcher/planner picks the cleanest mechanism that keeps
  host↔firmware parity (constants/flag-bit duplication per CLAUDE.md).
- Test names/placement for the FM1608 blank-check fix and any firmware native test.
- Whether (c) W29C040's datasheet-256B-page retry is driven via `write -b` or `dev write-cycle`.
- Order of operations within the bench session (fw flash → 2516 re-read → 0x08/flash4 re-bench).

### Folded Todos
- **`2026-06-24-skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads.md`** (score 0.9, area
  firmware, `resolves_phase: 84`) — folded. This IS the D-11 firmware fix: gate VPP error/warning
  checks off `read`/`blank-check`. Captures the chip-1 18.8V refusal + benign warnings + the 0x0B
  read-instability friction. Host parity required (`eprom_operations.py`).
- **`flash4-page-size-datasheet-sourced-cr01.md`** (CR-01) — folded as the D-31 (c) root-cause
  tracker: flash4 page size should be datasheet-sourced per chip (256B for W29C040), not a capacity
  heuristic. Folds as the disposition reference for the W29C040 re-bench, not necessarily a fix.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope & requirements
- `.planning/ROADMAP.md` §"Phase 84: DB Decode Audit + Conditional Defect RCA + Milestone Evidence
  Consolidation" — goal + 3 success criteria; §"Non-destructive-first safety ordering"; §v1.15
  "Bench discipline".
- `.planning/REQUIREMENTS.md` — **FIX-01** (the conditional defect requirement); **GRAD-03** +
  **FUT-03** tracker (2516 write proof, now best-effort DEFERRED per D-22); REWR-01/02/04 rows to
  annotate (D-41); EVID-01/02/03 (evidence/non-vacuous/reuse contract).
- `.planning/PROJECT.md` §"Current Milestone: v1.15" — milestone goal + Leonardo+Rev2.0 board lock.
- `.planning/STATE.md` §"Standing bench precondition" — Leonardo+Rev2.0-only, `r1 ≈ 270000`,
  port-identity-per-task, ASK silkscreen rev, reuse-first, EVIDENCE path.
- `.planning/v1.15-MILESTONE-AUDIT.md` — the audit naming Phase 84 as the dominant completeness
  blocker; the 3 FIX-01 inputs; the REWR/UV traceability tech-debt items (drives D-41).

### The evidence record (the load-bearing input — all bench findings live here)
- `.planning/v1.15/bench/EVIDENCE.md` — full 11-chip sweep, Phase-82 write rows, Phase-83 UV rows;
  the AM27C020 0x08 ANOMALY (row §Phase 83 #2), the 2516 0x0B read ANOMALY (sweep row #11 + §Phase 83
  Gate), the W29C040 flash4 FAIL (§Phase 82 #7), the FM1608 blank-check "Empty input" gap (sweep
  row #8 / §Phase 82 #6), and the cosmetic SST39SF040/FM1608 electrical.type notes (§Phase 82 #5/#6).
- `.planning/v1.15/bench/EVIDENCE.json` — machine-readable mirror; Phase 84 appends here too.

### Prior phase context (directly load-bearing)
- `.planning/phases/83-uv-eprom-write-proof-gated-on-phase-81-blank-state/83-CONTEXT.md` — the D-01
  2516→Phase-84 deferral, the **D-08 2516 PASS bar** (inherited), the AM27C020 ANOMALY → FIX-01
  handoff, the write-proof protocol and disposition rules carried here.
- `.planning/phases/81-2516-db-entry-non-destructive-read-sweep/81-CONTEXT.md` — the 2516 entry +
  the SAFE-01/02/03 bench discipline; the FLAG_CAN_ERASE EEPROM/Flash-EEPROM re-audit (relevant to
  the D-40 label-edit CAN_ERASE constraint).
- `.planning/phases/81-2516-db-entry-non-destructive-read-sweep/81-2516-SAFETY-REVIEW.md` — manual
  safety review of the 2516 user-override (relevant to any 2516 handling).
- `.planning/phases/74-per-family-correctness-fixes-flash-gated/74-CONTEXT.md` — the Phase-74
  W29C040 SDP/256B-page flash4 fix that was native-test-only (Wave-2 deferred); the (c) re-bench
  re-opens this.
- `.planning/phases/79-25v-nmos-ceiling-raise/79-CONTEXT.md` — v1.14 D-07 best-effort NMOS posture,
  VPP→VPE-as-VPP path, ~22.4V VPE rail (the basis for the deferred 2516 write's PASS bar).
- `.planning/phases/77-erase-write-path-graduation-0x07-ee-eproms/77-CONTEXT.md` — FLAG_CAN_ERASE
  derived from electrical-type; the constraint the D-40 label edit must not perturb.

### Firmware — VPP-skip fix (D-11) + parity (CLAUDE.md: change both together)
- `firestarter/src/firestarter.cpp` — the `read`/`blank-check` init VPP gate that refuses/warns.
- `firestarter/src/rurp_shield.cpp` — `hw_read_voltage` / VPP measurement.
- `firestarter/src/proms/eprom.cpp` + `firestarter/src/proms/memory.cpp` — the VPP/VPE check path
  (the under-voltage-warn-and-proceed source; context for which ops actually drive VPP).
- `firestarter/include/firestarter.h` ↔ `firestarter_app/firestarter/constants.py` — duplicated
  flag bits / command constants (`CMD_READ_VPE`, `FLAG_VPE_AS_VPP 0x10`); change in lockstep.
- `firestarter_app/firestarter/eprom_operations.py` — host read/blank-check path (host parity for
  the VPP-skip gate; also the FM1608 blank-check fix site, D-30).

### DB label edit (D-40) — codegen layer + safety gates
- `firestarter_app/tools/build_db.py` — codegen of `chip_database.json` from minipro `infoic.xml`;
  the electrical.type derivation layer where the SST39SF040/FM1608 label correction must land
  (NOT a hand-edit).
- `firestarter_app/firestarter/ic_layout.py` — consumes `electrical.type` for FLAG_CAN_ERASE
  derivation; the D-40 edit must NOT change its output.
- `firestarter_app/firestarter/data/chip_database.json` — the generated DB (SST39SF040/FM1608
  entries; verify the regenerated diff is label-only).
- `firestarter_app/tools/check_dispatch.py` + `firestarter_app/tools/diff_db.py` — the full-DB
  VPP-safety gate + the diff gate; both must be green and `diff_db.py` must show a label-only delta.
- `firestarter_app/firestarter/database.py`, `firestarter/eprom_info.py`, `chip_resolver.py` —
  other consumers of electrical.type (confirm no behavioural change).

### Write/verify + read tooling (reuse — EVID-02)
- `firestarter_app/firestarter/cli_handlers.py` — `dev write-cycle` (write-proof driver),
  `dev consistency-check` (N≥3 read oracle for the 2516 re-read + any re-bench).
- `firestarter_app/tools/gen_test_image.py` — deterministic image generator (re-bench images).
- `firestarter_app/write_test.sh` — integration script.

### Standing bench precondition (EVERY hardware task — SAFE-01)
- `.planning/STATE.md` §"Standing bench precondition" + `.planning/ROADMAP.md` §v1.15 "Bench
  discipline" — Leonardo + Rev 2.0 only; `r1 ≈ 270000`; verify `controller:` identity per task;
  ASK silkscreen rev; host suite green incl. 0xA4 guard before session.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `dev consistency-check --runs 3` — the non-destructive N≥3 read oracle for the post-fw-fix 2516
  re-read (D-20) and re-confirming the 0x08/flash4 chips before/after the re-bench.
- `dev write-cycle <chip> <image>` / `write -b` — write drivers for the (a)/(c) confirmatory
  re-bench (D-31).
- `tools/gen_test_image.py` — deterministic full-size images if the re-bench needs a write image.
- The Phase 81 FLAG_CAN_ERASE re-audit (81-01) + its pinning test — the baseline the D-40 label
  edit must not regress.

### Established Patterns
- `electrical.type` flows **infoic.xml → build_db.py (codegen) → chip_database.json →
  ic_layout.py (FLAG_CAN_ERASE)**. A hand-edit of the JSON regenerates away and risks silently
  changing CAN_ERASE — the D-40 correction belongs at the build_db.py layer and must be proven
  label-only by `diff_db.py`.
- Host↔firmware constant/flag duplication (CLAUDE.md): the VPP-skip gate must keep
  `firestarter.h` ↔ `constants.py` and `firestarter.cpp` ↔ `eprom_operations.py` in sync.
- Tooling gate is **CI-scoped** to `firestarter/ tests/` at py3.9/3.11; devcontainer Py3.12 masks
  it; pre-existing `tools/`-tree ruff findings are out-of-scope (flag, don't mask, don't fix here).
- A UV part is single-shot (no eraser) — the 2516 is never written (D-21); the 0x08/0x07 UV parts
  were already spent in Phase 83 (AM27C020 NOT-BLANK with intact silicon — re-bench is idempotent).

### Integration Points
- VPP-skip fix touches the `read`/`blank-check` init path in both firmware (`firestarter.cpp`) and
  host (`eprom_operations.py`) — the same path FM1608's blank-check fix (D-30) lives in; coordinate
  so the two host edits don't collide.
- The 2516 (0x0B) read exercises the VPP-regulator/shared-OE-VPP path; the D-11 fix only removes the
  *gate*, it does not actively drive the shared pin — so a still-unstable read after the fix is the
  expected trigger for the D-22 clean deferral.
- Firmware change → `pio test -e native` + Leonardo flash ≤ ~90% gate (D-10); the board was already
  on `b10` from Phase 82, so a re-flash to the Phase-84 build is in the established flow.

</code_context>

<specifics>
## Specific Ideas

- The operator authorized a firmware change specifically to honor the standing 2026-06-24 directive:
  "don't check or report errors/warnings when VPP isn't used" — but bounded it to exactly that
  (the VPP-skip gate), not the deeper shared-pin or write-path firmware work.
- The operator prioritizes **protecting the single irreplaceable 2516 over closing GRAD-03**: read
  re-validation only, never a write, even if the read stabilizes — GRAD-03/FUT-03 stay a documented
  best-effort deferral (the v1.14 D-07 pattern).
- The operator chose to **correct the DB electrical.type labels** rather than accept them as cosmetic
  — raising the bar to a verified label-only DB regeneration (the FLAG_CAN_ERASE / dispatch
  non-perturbation is the load-bearing constraint, D-40).
- Milestone-close posture is **best-effort with honest, documented deferrals**, consistent with the
  v1.14 close on intentional hardware deferrals.

</specifics>

<deferred>
## Deferred Ideas

- **2516 write proof / GRAD-03 / SC#4 / FUT-03 close** — DEFERRED best-effort (D-22). Read
  re-validation only this phase; the D-08 PASS bar is preserved for a future write attempt.
- **Deeper 0x0B firmware fix** — actively driving the shared OE/VPP pin to a clean read level
  (beyond the D-11 gate skip) — only if the VPP-skip fix alone fails to stabilize the read AND the
  operator later authorizes the larger change.
- **0x08 AM27C020 write/VPP path fix** — RCA + re-bench this phase (D-31), but fix deferred unless
  trivial; otherwise a named future tracker.
- **W29C040 flash4 256B-page write fix** — re-bench this phase (D-31); reopens **Phase-74 Wave-2**
  / the CR-01 datasheet-page-size todo if not trivially fixed.
- **REWR-02 positive 0x08 write PASS** — FUT-05 (needs a functional 0x08 rewritable chip).
- **Firmware versioning / lockstep beta cut** of the Phase-84 fw delta — deferred to
  `/gsd-complete-milestone` / operator authorization (D-12); the pending v1.14 `3.0.0b11` cut is
  itself still operator-gated.
- **v1.9 read-bug RCA (Phase 45 → FUT-C); pushing 2516 upstream into build_db.py (FUT-B).**

### Reviewed Todos (not folded)
- `avrdude-mcu-detection-fallback.md` — off-board blank-chip / wrong-firmware recovery; unrelated
  to Phase 84's decode-audit/RCA scope.
- `cobs-decoder-framelevel-deadline-wr01.md` — transport-layer firmware deadline (WR-01); unrelated
  to this phase.

</deferred>

---

*Phase: 84-db-decode-audit-conditional-defect-rca-milestone-evidence-consolidation*
*Context gathered: 2026-06-24*
