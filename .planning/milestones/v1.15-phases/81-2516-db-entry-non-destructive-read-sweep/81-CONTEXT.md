# Phase 81: 2516 DB Entry + Non-Destructive Read Sweep - Context

**Gathered:** 2026-06-23
**Status:** Ready for planning

<domain>
## Phase Boundary

Two coupled workstreams, both **host-side, zero chips consumed**:

1. **Author the `2516` user-override DB entry** in `~/.firestarter/database.json`
   (GRAD-01 datasheet research → GRAD-02 entry + **manual safety review** — the
   override bypasses `check_dispatch.py`/`diff_db.py`, so manual review is the
   only gate) so `firestarter info 2516` decodes correctly.
2. **Read + blank-check ALL 11 physical chips** on Leonardo + RURP Rev 2.0
   (SWEEP-01/02), producing the per-chip `EVIDENCE.{md,json}` record (EVID-01/02/03)
   and recording the blank-state of the 3 true UV-EPROMs (ST M27C512, AM27C020,
   2516) — the gate for every Phase 83 spend-vs-preserve decision.

Plus a **pre-write code review** that `FLAG_CAN_ERASE` is derived correctly for
BOTH `EEPROM` and `Flash/EEPROM` electrical types (DB-02), and homing the
cross-cutting bench-safety discipline (SAFE-01/02/03) that recurs in Phases 82–84.

**The 11 chips:** W27C512, W27E512, SST27SF512 (0x07), W27E040 (0x08),
SST39SF040 (0x06), W29C020, W29C040 (0x05 flash4), FM1608 (0x40 FRAM),
ST M27C512 (0x07 UV), AM27C020 (0x08 UV), 2516 (0x0B NMOS UV).

**Out of scope:** any write/program/erase (Phases 82 = rewritable, 83 = UV-spend);
the milestone decode audit + conditional defect RCA (Phase 84); the 2516 write
proof on the VPE rail (Phase 83 / GRAD-03); firmware changes (Leonardo untouched
unless a bench defect forces a lockstep fix); the v1.9 read-bug RCA (deferred).
</domain>

<decisions>
## Implementation Decisions

### 2516 manual safety review — dedicated doc + operator human gate (GRAD-02)
- **D-01:** The 2516 user-override entry's manual safety review is recorded in a
  **dedicated `81-2516-SAFETY-REVIEW.md`** (Phase-58 SR-1-style checklist), and
  the **operator personally signs off on it before any bench session** — this is
  a human gate, not a Claude self-attestation. The most auditable option,
  because the override bypasses the automated gates and Phase 83 will write the
  **irreplaceable** 2516 based on this decode being correct.
- **D-02:** The checklist MUST verify (research-grounded, against the TMS2516 /
  2516 datasheet — see Canonical refs):
  1. `algorithm = 0x0B` → routes to `configure_eprom`.
  2. `vpp_mv = 25000` ≤ `RURP_VPP_CEILING_MV = 25000` (at the ceiling, not over —
     Phase 79 raised it to 25000).
  3. `electrical.type = "UV-EPROM"` → `FLAG_CAN_ERASE` **NOT** set.
  4. `pinout = DIP24_2716` exists in `pinouts.json` and its pin-map routes VPE /
     VPP / OE / CE to the correct DIP24 pins vs the datasheet (esp. VPP pin 21).
  5. `support_status = "supported"` (so the chip is usable, not host-refused) —
     research-confirmed value; planner to confirm it is required for the entry to
     decode + be benchable. (Not enumerated in GRAD-02's value list, but the
     v1.15 research and ARCHITECTURE.md call for it.)
  6. `size_bytes = 2048` (2K×8).
- **D-03:** GRAD-01 research is a **researcher-agent task at plan time** (confirm
  the 2516's absence from minipro `infoic.xml` — the 28 "2516" hits are all
  `25160` SPI parts — and capture NMOS / DIP24 / ~25V class / 2KB / 2716
  read-compatibility). The findings feed the safety-review checklist (D-02).

### DB-02 FLAG_CAN_ERASE — fresh adversarial re-audit, not a Phase-77-trust
- **D-04:** Despite Phase 77 (D-01/D-02) already wiring `FLAG_CAN_ERASE` from
  `electrical.type` for both `EEPROM` and `Flash/EEPROM`, DB-02 is a **fresh
  adversarial re-audit from scratch** — re-derive the full path
  (`build_db.py` `electrical.type` decode → `database.py` `_map_data`
  `info-flags`/`electrical-type` → `convert_to_programmer` `flags` → wire JSON →
  firmware `eprom_write_init` guard) **without assuming Phase 77's conclusion
  holds** — then pin the verified behavior with tests. Rationale: W29C020 /
  W29C040 are `Flash/EEPROM` (not `EEPROM`) and get bench-proven for the FIRST
  time in Phase 82, so the Flash/EEPROM branch must be independently proven, not
  inherited.
- **D-05:** A **Flash/EEPROM-specific pinning test** MUST exist at the end of
  DB-02 (asserting `FLAG_CAN_ERASE` is set for a `Flash/EEPROM` chip). If the
  re-audit finds Phase 77 already added one, confirm it covers `Flash/EEPROM`
  explicitly; if not, add it. Any real gap found is **fixed and pinned**; host
  suite green incl. the 0xA4 `test_init_phase_data_frames_not_acked` guard
  (SAFE-02).

### Read-sweep anomaly handling — reseat + retry, record, continue
- **D-06:** On a suspect/dirty read during the sweep (all-`0xFF` contact fault,
  read jitter, timeout): **reseat the chip + retry up to N times**, then if still
  not clean, **record the anomaly in EVIDENCE (verdict = ANOMALY) and continue**
  the sweep — the sweep is non-destructive so there is no reason to halt. Genuine
  defects (a chip that won't read clean after reseat/retry) are **flagged for
  Phase 84 FIX-01**, not root-caused inline. Matches bench memory
  ([[project_uno328pb_bench_instability_27_04]] retry-on-timeout / never-trust-N=1;
  [[reference_vpp_vpe_no_socket_routing]] all-`0xFF`/`0x303` = contact fault, not
  a read defect).
- **D-07 (retry count — Claude's discretion default):** N = up to **2 reseat +
  retry** cycles per suspect chip before recording ANOMALY (planner may refine).
  The non-vacuous PASS bar is separate and locked: N≥3 byte-identical reads +
  a negative control (EVID-03).

### Blank-check semantics — UV gates Phase 83; non-UV is read + note state
- **D-08:** A true **gating blank-state** is recorded only for the **3 UV-EPROMs**
  (ST M27C512, AM27C020, 2516) per SWEEP-02 — this is what gates each Phase 83
  spend-vs-preserve decision.
- **D-09:** For the **8 non-UV chips** (the EE-EPROMs + FRAM, which are never
  factory-blank), the sweep records a **read + observed-current-state summary**
  (e.g. "not blank / mixed data" + a SHA of current contents) — NOT treated as a
  pass/fail blank gate. Every chip still gets a full EVIDENCE row (op =
  read+blank_check, the non-UV blank_state = "n/a — not factory-blank, current
  contents recorded").

### Sequencing
- **D-10:** Author + safety-review the 2516 entry (D-01) **before** the sweep —
  the 2516 cannot be read without its DB entry (pinout/algorithm lookup). The
  2516 read + blank-check is part of the same all-11 sweep (it is the 11th chip),
  and reading it is non-destructive (read applies no VPP).

### SAFE-01/02/03 framing for this phase (homed here, recur in 82–84)
- **D-11:** SAFE-01 — every bench task records + verifies board = Leonardo,
  shield = Rev 2.0 (**ASK the operator which silkscreen rev is mounted** — the
  EEPROM byte can't distinguish revs), `controller:` port identity (re-verified
  per task after any USB event), live `r1 ≈ 270000` readback. SAFE-02 — host
  suite green (incl. the 0xA4 guard) before any session. SAFE-03 — no
  non-Leonardo read is authoritative; (no UV write happens this phase, so the
  no-write-before-blank-check clause is trivially satisfied; over-voltage stays
  blocked). Leonardo is **chip-OUT-sideload-EXEMPT**.

### Claude's Discretion
- Exact EVIDENCE.{md,json} schema shape (column ordering, JSON key names) so
  Phase 84 can consolidate — planner's call, must carry the locked columns
  (chip, family/algorithm, board+shield, blank-state, op, SHA-or-N/A, verdict,
  anomalies) and extend (not replace) the v1.13 per-family matrix.
- Reseat/retry count default (D-07) and the exact read command/flags
  (`firestarter read` vs `dev write-cycle --runs 3` vs `dev validate-family`).
- Whether the safety-review checklist also captures a `firestarter info 2516`
  transcript as evidence the decode renders.
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope & requirements
- `.planning/ROADMAP.md` §"Phase 81: 2516 DB Entry + Non-Destructive Read Sweep" — goal + 5 locked success criteria
- `.planning/REQUIREMENTS.md` — GRAD-01/02, SWEEP-01/02, EVID-01/02/03, DB-02, SAFE-01/02/03 (the 11 Phase-81 requirements)
- `.planning/PROJECT.md` §"Current Milestone: v1.15" — milestone goal, target features, key context (board lock, inventory-already-supported framing)

### v1.15 research (milestone-level, all 4 phases)
- `.planning/research/SUMMARY.md` — exec summary; **Research Flag #3** (2516 entry manual-review checklist), **Flag #1** (FLAG_CAN_ERASE Flash/EEPROM code review), **Flag #2** (0xA4 regression check); per-phase patterns
- `.planning/research/ARCHITECTURE.md` — 2516 user-override flow (EpromDatabase→chip_resolver→convert_to_programmer→memory.cpp), 5-point safety review, evidence schema, Leonardo preconditions
- `.planning/research/FEATURES.md` — the 11-chip / 5-family breakdown; FLAG_CAN_ERASE Flash/EEPROM VERIFY ITEM
- `.planning/research/PITFALLS.md` — irreversible-UV-write, false-PASS oracle, NMOS under-voltage, reseat-on-0xFF, port-identity drift
- `.planning/research/STACK.md` — zero-new-deps; reuse `write_cycle_eprom` / `dev validate-family` / `write_test.sh`; 2516 user-override mechanics

### The FLAG_CAN_ERASE decode chain (DB-02 — re-audit these end-to-end)
- `firestarter_app/tools/build_db.py` (~lines 607–643) — Pass-2 `_etype` re-derivation: `flags & 0x10` (`MP_ERASE_MASK`) → `EEPROM`/`UV-EPROM`/`Flash/EEPROM`; canonical erase-mask ground truth
- `firestarter_app/firestarter/database.py` — `_map_data` (~line 434, synthetic `info_flags |= 0x10` + `electrical-type`) + `convert_to_programmer` (~lines 592–607, the `FLAG_CAN_ERASE` set site)
- `firestarter_app/firestarter/constants.py` ↔ `firestarter/include/firestarter.h` — `FLAG_CAN_ERASE` (0x02) parity (SAFE-03 if touched)
- Firmware `eprom_write_init` (`firestarter/src/proms/eprom.cpp`) — honors `FLAG_CAN_ERASE`; `configure_eeprom28c` (0x0D path) — verify it ignores the flag (Phase 77 D-03 carryover)
- `firestarter_app/doc/protocol-flags.md` — flag bit 4 (0x10) = `can_erase` source-grounded semantics
- `.planning/phases/77-erase-write-path-graduation-0x07-ee-eproms/77-CONTEXT.md` — Phase 77 D-01/D-02 wiring + D-07 0xA4 regression test (the re-audit's prior art, to be independently re-verified per D-04)

### 2516 entry + NMOS / VPE rail (GRAD; informs the safety review)
- `.planning/phases/79-25v-nmos-ceiling-raise/79-CONTEXT.md` — D-07 best-effort NMOS graduation; 0x0B = direct-VPE path; VPE = 22.4V DMM / 23.9V fw; `firestarter vpe` (NOT `vpp`); over-voltage block / under-voltage warn-and-proceed
- `firestarter_app/tools/build_db.py:117` — `RURP_VPP_CEILING_MV = 25000` (post-Phase-79); the 2516's 25000 sits at the ceiling
- `firestarter_app/firestarter/chip_resolver.py` — host guard `resolve_chip` (the 2516 must be `supported` to pass it)
- `firestarter_app/firestarter/pinouts.json` (or equivalent) — confirm `DIP24_2716` exists + its pin-map (D-02 step 4)

### Safety gates & evidence
- `firestarter_app/tools/check_dispatch.py` — full-DB VPP-safety gate (does NOT cover the user-override entry → manual review compensates; SAFE-02)
- `firestarter_app/tools/diff_db.py` — per-chip diff gate (also bypassed by user-override)
- host test `test_init_phase_data_frames_not_acked` — the 0xA4 `ack_data=False` regression guard (SAFE-02, must be green)
- `.planning/v1.15/bench/EVIDENCE.{md,json}` — the new artifact this phase creates (extends the v1.13 per-family matrix)

### Standing bench precondition (EVERY hardware task — SAFE-01)
- `.planning/STATE.md` §"Standing bench precondition" + `.planning/ROADMAP.md` §v1.15 "Bench discipline" — Leonardo + Rev 2.0 ONLY authoritative; live `r1 ≈ 270000`; verify `controller:` port identity per task; ASK silkscreen shield rev; Leonardo chip-OUT-sideload-exempt; host suite green before session
</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `EpromOperator.write_cycle_eprom` / `dev validate-family` (Tier-3, Leonardo-only PASS oracle, R1 gate at 270000±25%) / `write_test.sh` — reuse for the read path; **no new harness** (EVID-02).
- `firestarter dev write-cycle --runs 3` produces per-run binaries + SHA — the natural substrate for the N≥3 non-vacuous read (EVID-03).
- Phase 77's `convert_to_programmer` edit + its 0xA4 regression test are the prior art the DB-02 re-audit independently re-verifies (D-04).
- The v1.13 per-family validation matrix is the structure EVIDENCE.{md,json} **extends, not replaces** (EVID-01).

### Established Patterns
- DB regen (`python3 tools/build_db.py`) is the canonical mechanism for built-in chips — but the 2516 is a **user-override** in `~/.firestarter/database.json`, hand-authored + manually reviewed (it never flows through `build_db.py`/`check_dispatch.py`/`diff_db.py`).
- Host↔firmware constant parity is a hard CI/CLAUDE.md rule — touching any `FLAG_*`/protocol constant means lockstep `constants.py` ↔ `firestarter.h` + parity tests (SAFE-03). DB-02 is expected to be read-or-test-only (no constant change anticipated).
- Tooling gate: `ruff check` + `ruff format --check` + `mypy` (strict on 8 modules) + `pytest --cov-fail-under=70`. **Devcontainer Python 3.12 masks CI py3.9/3.11** — validate ruff against the target before claiming green ([[reference_devcontainer_py312_masks_ci_py39]]).

### Integration Points
- `electrical.type` (DB) → `_map_data` `info-flags`/`electrical-type` → `convert_to_programmer` `flags` → wire JSON `flags` → firmware `eprom_write_init` `FLAG_CAN_ERASE` guard (the DB-02 chain).
- 2516: `~/.firestarter/database.json` user-override → `EpromDatabase` (merges over built-in) → `chip_resolver.resolve_chip` (must not refuse) → `convert_to_programmer` → wire → firmware `configure_eprom` (0x0B direct-VPE).
</code_context>

<specifics>
## Specific Ideas

- The operator is hands-on at the bench and treats the read-sweep as a true
  safety baseline: non-destructive, all 11 chips, before ANY write anywhere in
  the milestone. The 3 UV-EPROMs are irreplaceable (no eraser) — the blank-state
  recorded here is load-bearing for Phase 83.
- The 2516 safety review is a **human sign-off gate**, not a checkbox — the
  operator explicitly wants to personally approve the hand-authored override
  entry before it can be benched, because it bypasses every automated gate.
- DB-02 is wanted as a genuine from-scratch re-audit precisely because the
  Flash/EEPROM erase branch (W29C020/W29C040) is about to be bench-proven for the
  first time — "don't just trust Phase 77."
</specifics>

<deferred>
## Deferred Ideas

- **2516 write proof on the ~22.4V VPE rail** (read via `firestarter vpe`, N≥3
  SHA, fw under-voltage warning) — Phase 83 / GRAD-03; closes FUT-03.
- **Promoting the 2516 from user-override into `build_db.py`** — FUT-B (only if
  it ever appears upstream in minipro `infoic.xml`).
- **Per-family write→verify validation** of the 8 rewritable chips — Phase 82.
- **Consolidated decode-correctness audit + conditional defect RCA** — Phase 84.
- **Carried pending todos** (`avrdude-mcu-detection-fallback`,
  `cobs-decoder-framelevel-deadline-wr01`, `large-read-data-jitter-uno328pb`) —
  none match Phase 81 scope (off-board / other milestones); not folded.

None of the above are scope creep — they are explicitly later phases / future items.
</deferred>

---

*Phase: 81-2516-db-entry-non-destructive-read-sweep*
*Context gathered: 2026-06-23*
