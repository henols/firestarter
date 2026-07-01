---
gsd_state_version: 1.0
milestone: v1.19
milestone_name: Protocol Naming & Labels
status: planning
last_updated: "2026-07-01T13:11:03.472Z"
last_activity: 2026-07-01
progress:
  total_phases: 4
  completed_phases: 0
  total_plans: 0
  completed_plans: 0
  percent: 0
---

# Project State

**Project:** Firestarter — Protocol-Aware Programming Architecture
**Updated:** 2026-07-01

## Current Position

Phase: 100 of 103 (NAME — Canonical Protocol Name Set + Operator Approval)
Plan: — (roadmap created, not yet planned)
Status: Roadmap created — ready to plan Phase 100
Last activity: 2026-07-01 — ROADMAP.md created (4 phases, 15/15 requirements mapped)

## Project Reference

See: `.planning/PROJECT.md` (v1.19 Current Milestone section + Key Decisions)

**Core value:** Algorithm-first dispatch — minipro `protocol_id` flows authoritative from upstream XML → DB → wire JSON → firmware handler. v1.19 keeps that contract byte-for-byte (numbers unchanged) and layers a correct, human-readable **name** on top of every protocol so firmware code and host display are legible without a hex lookup.

**Current focus:** v1.19 Phase 100 (NAME) — author + get operator approval on the canonical protocol name set before any firmware/host/doc work starts. AM27C020 `0x08` write reliability remains carried forward as **FUT-08** (unrelated to this milestone; program-window VPP-under-load + timing characterization).

## Milestone Context (v1.19)

- **Scope (operator-confirmed 2026-07-01):** Readability-only milestone. No `chip_database.json` change, no wire-protocol/lockstep-constant change, no new CLI input grammar. Numbers stay authoritative everywhere; only names/labels are added on top.
- **Sequencing constraint:** NAME-01/02/03 (Phase 100) is a hard blocking gate — the canonical protocol name set must be operator-approved before FW (101), HOST (102), or DOC (103) work starts. FW and HOST are independent refactors (no lockstep coupling between them); DOC reconciles last, after both land.
- **Branch base:** Branches off the v1.18 tip in all 3 repos per standing v1.15–v1.18 policy; gitlinks PINNED at b10; lockstep beta cut operator-gated.
- **Non-regression bar:** FW-04 is a hard gate — golden register traces + dispatch-mirror guard byte-identical, native Unity suite green, Leonardo flash delta near-zero. GATE-01/02/03 (DB IDENTITY, wire/lockstep parity unaffected, no new CLI grammar) close the milestone in Phase 103.
- Phase numbering continues from v1.18's Phase 99 → **v1.19 starts at Phase 100**.
- Watch the py3.12-masks-CI-3.11 ruff/codegen drift trap for host changes (Phase 102).

## Roadmap Summary (v1.19 — Phases 100–103)

Created 2026-07-01 · granularity Comprehensive · 15/15 requirements mapped (no orphans, no duplicates). Strict sequence: **NAME (gate) → {FW, HOST independent} → DOC+GATE (close)**.

| Phase | Goal | Requirements | Depends on |
|-------|------|--------------|------------|
| 100 — NAME | Author canonical protocol name set + operator-approval blocking gate + record as single source of truth | NAME-01, NAME-02, NAME-03 | Nothing (first phase) |
| 101 — FW | Named constants/labels replace magic hex in dispatch + handler bodies; rename mechanism-jargon handlers (many-to-one kept); golden traces + dispatch-mirror byte-identical, flash delta near-zero | FW-01, FW-02, FW-03, FW-04 | Phase 100 |
| 102 — HOST | Consolidate scattered `ic_layout.py`/`eprom_info.py` protocol maps into one translation for `info`/`list`/`search`; internal logic unchanged; CI green | HOST-01, HOST-02, HOST-03 | Phase 100 (independent of 101) |
| 103 (close) — DOC + GATE | Reconcile `PROTOCOLS.md` prose + INV matrix to final names; assert DB/wire/CLI non-regression (GATE-01..03) | DOC-01, DOC-02, GATE-01, GATE-02, GATE-03 | Phase 101, Phase 102 |

**Dependency chain:** 100 → {101, 102} → 103 (100 is a hard blocking gate; 101/102 are independent parallel refactors sharing the Phase-100 name set, no lockstep coupling between them; 103 needs both done to reconcile docs + close).

**Firmware/host surfaces:** `firestarter/include/firestarter.h` (named constants), `firestarter/src/proms/memory.cpp` (dispatch labels), `firestarter/src/proms/flash_type_3.cpp`/`flash_type_4.cpp`/eeprom28c handler (renames), `firestarter/doc/PROTOCOLS.md` (vocabulary + INV matrix); `firestarter_app/firestarter/ic_layout.py` + `eprom_info.py` (consolidated display map). No `chip_database.json`, no wire/lockstep constant, no CLI grammar change anywhere in this milestone.

## Accumulated Context

### Deferred Items (carry-forward at v1.17 close — 2026-06-29)

| Category | Item | Status | Disposition |
|----------|------|--------|-------------|
| FUT-07 (v1.17) | W29C040 byte-exact graduation + LEDGER `supported` | deferred — §6.6 boot block permanently locked on seated chip | Needs a different unlocked sample + third-party bench. All v1.17 software done. |
| ~~FUT-06 (v1.15)~~ → **FUT-08 (v1.18)** | AM27C020 0x08 32-pin write/VPP path | **retired-by-replacement (v1.18 Phase 99 close, 2026-07-01)** | Phase-98 fix bench-proven effective (write#1 60/64 byte-exact; Phase-97 0-bits signature refuted) but marginal/unreliable (write#2 0/64) — no byte-exact graduation. FUT-08 carries the next step: characterize program-window VPP-under-load (DMM at socket pin 1) + write timing. See PROTOCOL-LEDGER `0x08` / `.planning/v1.18/bench/EVIDENCE.json`. |
| FUT-05 (v1.15) | REWR-02 0x08 rewritable write proof | deferred — no functional 0x08 rewritable chip | W27E040 stuck-bit; may benefit from v1.18 `0x08` fix. |
| FUT-04 (v1.14) | AT28C04/16 adapter graduation | deferred — adapter not built | 9 chips stay `adapter-required`. |
| FUT-03 (v1.15) | 2516 0x0B read instability + write proof | deferred best-effort (D-22) | 3 distinct SHAs after VPP-skip; shared OE/VPP pin. |
| FUT-01 (v1.14) | X88C64 0x34 graduation | deferred — PCB-blocked | A6 ALE-routing PCB-BLOCKED (HIGH); stays `protocol-not-implemented`. |
| release-gate | Lockstep beta cut `3.0.0b11` + gitlink bump | OPERATOR-GATED | Standing v1.11–v1.17 policy; gitlinks PINNED. |

### Deferred Items — acknowledged at v1.18 milestone close (2026-07-01)

14 open artifact items (from `audit-open`) acknowledged-and-deferred at v1.18 close. **None originate in v1.18 (Phases 97–99)** — all are pre-existing cross-milestone carry-forwards, unchanged by this milestone.

| Category | Item | Status |
|----------|------|--------|
| debug | firmware-vpp-misread | diagnosed (uno328pb VPP divider ~6.8x under-read) |
| debug | fm1608-fresh-chip-baseline | parked-2026-05-18 |
| uat_gap | Phase 08 — 08-HUMAN-UAT.md | partial (0 pending scenarios) |
| uat_gap | Phase 85 — 85-HUMAN-UAT.md | partial (2 pending scenarios) |
| verification_gap | Phase 08 — 08-VERIFICATION.md | human_needed |
| verification_gap | Phase 09 — 09-VERIFICATION.md | human_needed |
| verification_gap | Phase 71 — 71-VERIFICATION.md | gaps_found |
| verification_gap | Phase 84 — 84-VERIFICATION.md | human_needed |
| verification_gap | Phase 85 — 85-VERIFICATION.md | human_needed |
| todo | 2026-06-24-skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads | firmware |
| todo | avrdude-mcu-detection-fallback | low |
| todo | cobs-decoder-framelevel-deadline-wr01 | medium |
| todo | photograph-modified-rev-0 | MEDIUM |
| todo | write-modifications-md-rework-trace | MEDIUM |

### v1.9 DEFERRED (operator 2026-06-08 — resumes later at Phase 45)

v1.9 (Read-Bug RCA + Fix) is paused. Phase 44 (Bug A RCA) complete; remaining Phases 45–48. The v1.18 bench oracle is pinned to Leonardo + Rev 2.0 precisely to avoid the v1.9 shield-fleet read bug.

### v1.10 Substrate (carry-forward)

Transport provably byte-exact (COBS `0x00` + CRC8-CCITT) — settled variable. GATE-1.8d ring-fence intact.

### v1.17 Substrate (carry-forward, directly relevant to v1.18)

- **T-93-CANERASE fix shipped (Phase 94 Plan 01):** `FLAG_CAN_ERASE` gated on `algorithm != 5` in host; firmware `flash4_write_init` skips erase when `handle->protocol == 0x05`. No equivalent issue for `0x08` — but establishes the dual-repo lockstep discipline for protocol-keyed defense-in-depth.
- **Per-chip `page_size` wire field added (Phase 94 Plan 02):** precedent for a new wire datum from pinout DB → host → firmware. Same pattern may apply if `DIP32_27C020` needs a new control-pin concept.
- **PROTOCOL-LEDGER at `.planning/v1.16/ledger/PROTOCOL-LEDGER.{md,json}`** carries `0x08` as `open-defect-carried (FUT-06)`. v1.18 must update this on bench PASS (or re-record at new FUT status).
- **Golden register traces + dispatch-mirror guard** pinned for `eprom` family (0x07/0x08/0x0B, Phase 88). Any `eprom.cpp` change must keep 0x07 + 0x0B traces byte-identical and add an explicit 0x08 32-pin trace/case (v1.16 P89 CR-01 lesson: need a failure-case/mismatch test).

### v1.18 Research Findings (pre-loaded from `.planning/research/v1.18-AM27C020-27C-EPROM.md`)

- **RC-1 (LEADING):** PGM pin (DIP pin 31) not held program-active; modeled as an address line in `DIP32_STD`. The 27C020's PGM requirement (CE=VIL AND PGM=VIL) is never satisfied — firmware strobes CE only, pin 31 tracks address bits. The 27C040 (where pin 31 = A18) is the chip `DIP32_STD` was authored for.
- **RC-2:** P1 VPP routing/level never proven on a `0x08` UV part. `CTRL_VPP_P1_ENABLE` is only toggled during the per-byte data-write window, not held across the full pulse.
- **RC-3:** JP4 (JMP_VPP_P1_BYPASS) position — JP4-closed alone didn't fix it (Phase 83/84). Cross-confirm with Rev 2.0 schematic semantics.
- **RC-4:** 32-pin high-address / control-bit collision (lower rank — symptom is clean 0-bits at address 0 where collisions are least likely).
- **RC-5:** Chip is OTP/already-programmed/dead (silicon). The Tier-0 pre-flight (PRE-01) determines this definitively before any graduation spend.
- **VPP measurement method:** `firestarter dev reg 0 0 0x86 -f` holds rail for DMM. DMM at socket pin 1 (VPP) AND pin 31 (PGM) during a write attempt is the most decisive measurement.
- **Fix surfaces:** `eprom.cpp` (program-pulse / `using_p1_as_vpp` 32-pin sequencing); `pinouts.json` (possible `DIP32_27C020` entry redirecting pin 31 from address-bus to PGM control); `firestarter.h` ↔ `constants.py` if a new wire flag/field is needed.

### Pending Todos (carried forward)

- `avrdude-mcu-detection-fallback.md` (low) — out of scope, carry forward.
- `cobs-decoder-framelevel-deadline-wr01.md` (medium) — v1.10 COBS follow-up; deferred.
- `2026-06-24-skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads.md` (firmware) — carry forward.
- `large-read-data-jitter-uno328pb.md` (HIGH, v1.8-seed) — v1.9 RCA target.
- `photograph-modified-rev-0.md` (medium) — carry forward.

## Operator Next Steps

- Review + approve the v1.19 ROADMAP.md, then run `/gsd-plan-phase 100` (NAME — canonical protocol name set + operator approval gate).

## Decisions

- [Phase ?]: SAFE-01 invariant: holds because Phase-97 procedure never passes --force (firmware HAS a FLAG_FORCE over-voltage relaxation at primitives.cpp:121); held-rail proxy pinned host-space 0x188/0x180 marked [ASSUMED] per A1; all bench fields TBD-bench never fabricated (D-02)
- [Phase 98 Plan 01]: Q1 RESOLVED — static-high-pins RULED OUT as PGM vehicle (static_high_mask drives HIGH; PGM=VIL); DIP32_27C020 takes pin 31 off address bus only; PGM-assert is Plan 02 firmware branch (memory_set_data hold-LOW)
- [Phase 98 Plan 01]: D-04 host-side alias guard — size gate (mem_size<=262144) structurally excludes 512K AM27C040 / 1M AM27C080 from DIP32_27C020; both stay DIP32_STD
- [Phase 98 Plan 01]: Blast radius 88 chips accepted (entire ≤256K 0x08 32-pin class); architectural correctness is class-wide (A18 unused at ≤256K); LOW-7: baseline git diff is the audited artifact
- [Phase 98 Plan 02]: A5 CONFIRMED — 0x08 golden trace byte-identical post-fix; test_golden_eprom_0x08_write uses pins=0 (default), gate fails, PGM-hold branch does not fire; no re-bless needed
- [Phase 98 Plan 02]: MED-5 verified no-op — per-buffer P1-hold in program_mismatched_bytes already spans every per-byte CE pulse; no redundant per-byte P1 churn added; new code only asserts CTRL_ADDRESS_LINE_18 hold-LOW (distinct from P1 VPP routing)
- [Phase 98 Plan 02]: HIGH-1 blind-fix honesty — addr-0 register state byte-unchanged under RC-1; Phase 99 is sole empirical gate; no over-claim that bits flip on silicon
- [Phase 98 Plan 03]: rw-pin:[31] on DIP32_27C020 mirrors the working DIP32_SST39SF040 precedent — pin 31 resolves via pin_conversions[32][31]=22 to config.rw_line=22 -> CTRL_READ_WRITE (0x40), closing the corrected CR-01 fork (host half)
- [Phase 98 Plan 03]: DB regen confirmed idempotent for rw-pin (pinouts.json runtime datum, never embedded in chip_database.json) — diff_db.py shows only the pre-existing Phase-94 PGSZ_PAGE_SIZE delta
- [Phase 98 Plan 03]: py3.11 CI sign-off follows the 98-01 precedent (CI-PENDING/structurally-green) — no python3.11 binary in this devcontainer; all CI-scoped commands (ruff/mypy-watermark/diff_db/check_dispatch/parity) pass under 3.12.13
- [Phase 98 Plan 04]: Reverted 98-02's inert CTRL_ADDRESS_LINE_18 clear (physical no-op on Rev 2 via the 0x08 alias; wrong-pin on Rev 0/1); relies on existing rw_line mechanism (CTRL_READ_WRITE 0x40, revision-invariant) fed by 98-03's rw-pin:[31]
- [Phase 98 Plan 04]: WR-01 revision-parametrized native test added via local replicas of rurp_map_ctrl_reg_for_hardware_revision (Rev 2 + Rev 0/1) — the missing RED state; WR-02 RC-98B pinned to EQUAL(5); IN-02 firmware constant deferred to 98-05 (no size literal survives the revert)
- [Phase 98 Plan 05]: IN-03 macro replacement named `mem_min` (not `min`) to avoid any future collision with Arduino's own min() or std::min — static inline single-evaluation function, sole call site (memory_read_execute) updated, behavior identical (side-effect-free operands)
- [Phase 98 Plan 05]: IN-02 host authoritative value moved from build_db.py-only literal (98-03) into constants.py (the established landing spot for every firmware-parity constant this codebase tracks) — build_db.py now imports it; parity test follows the file's REAL pattern (hardcoded literal + FW_ABSENT skipif + citing comment), not literal header-parsing, matching its 6 sibling assertions
- [Phase 98 Plan 05]: Phase 98 CLOSED — all 5 plans complete (98-01/02 original fix attempt + 98-03/04 corrected CR-01 fix + 98-05 IN-01/02/03 cleanup); native suite 119/119 green, golden traces byte-identical, host CI green on py3.11 target; Phase 99 (BENCH + LEDGER) unblocked
- [Phase 99 Plan 01]: Chose minimal D-09 extension (option a, evidence-shape branch keyed on `v1_18_writeverify_sha_selfconsistent`) over a new status enum value — a v1.18-native 0x08 graduation is proven by write/read-back self-consistency (no v1.15 write baseline exists for AM27C020) without requiring a fabricated `p90_writecycle_sha_matches_v115` claim; honesty guard verified (bare 0x08 PASS claim without the marker still fails); FUT-06 retirement path (removal from open_defects[], not status_changed flip) proven by test; gate is now CAPABLE of a graduated 0x08 row but 99-04 decides the actual outcome from the bench result
- [Phase Phase 99 Plan 02]: check_graduation.py filters on op prefix phase99* (never the Phase-97 tier0_microprobe+rca01 cell); branches PASS (write_image_sha256==readback_sha256 self-consistency) vs DEFER (bits_flipped+post_read_sha256 differential), validated against 9 synthetic fixture cells without ever mutating the real EVIDENCE.json
- [Phase 99]: [Phase 99 Plan 04]: Took the DEFER branch decided by 99-03 (Phase-98 fix bench-effective-but-unreliable: write#1 60/64 byte-exact, write#2 0/64); retired FUT-06 by removal-and-replacement rather than in-place edit, opening FUT-08 (renumbered from the operator-requested "FUT-07" — that id is already taken by the v1.17 W29C040 defect in this same table) as an explicit successor citing the fix-effective-but-unreliable finding + the next diagnostic step (program-window VPP-under-load + write timing); 0x08 row stays open-defect-carried with on_hand_chip now AM27C020

## Performance Metrics

| Phase | Plan | Duration | Notes |
|-------|------|----------|-------|
| Phase 98 P04 | 35min | 3 tasks | 2 files |
| Phase 98 P05 | 25min | 3 tasks | 5 files |
| Phase 99 P01 | 25min | 3 tasks | 2 files |
| Phase 99 P02 | 15min | 2 tasks | 3 files |
| Phase 99 P04 | 15min | 2 tasks | 4 files |
