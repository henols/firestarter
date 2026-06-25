# Project: Firestarter — Protocol-Aware Programming Architecture

**Created:** 2026-05-08
**v1.0 shipped:** 2026-05-11
**v1.1 status:** Parked at 80% (Phase 4 hardware-validation open — FM1608 byte-0 bug requires a different Uno board to unblock; see `.planning/debug/fm1608-fresh-chip-baseline.md`)
**v1.2 shipped:** 2026-05-19 (Message-ID Logging Rework — Leonardo Flash 98.7% → 85.4%, firmware 3.0.0-dev)
**v1.3 status:** Paused 2026-05-20 (hardware-gated — Phase 11 coverage matrix shipped + Phase 12 Wave 0 scaffold committed; bench plans 12-01/02/03 + Phase 13 + Phase 14 await operator hardware. Resume: `/gsd-execute-phase 12 --wave 1 --interactive`)
**v1.4 shipped:** 2026-05-20 (Beta & Pre-release Deployment Pipeline — 6 phases, 16/16 requirements)
**v1.5 shipped:** 2026-05-21 (Arduino Uno ATmega328PB Board Support — 5 phases, 15/15 requirements; ship tag `3.0.0b4`; bench-validated on operator's 328PB-Uno via `urclock` bootloader). Three open backlog items carried forward to v1.6 — see MILESTONES.md.
**v1.6 shipped:** 2026-05-26 (Fix the Read Bug — ships as "diagnostic + revert" per D-17v2; 5 phases, 13 plans; 12/16 requirements DELIVERED; 4 DEFERRED to v1.8 with Bug A + Bug B pattern findings as RCA seed). Per Phase 29 v2 PASS_PARKED: Leonardo Modified Rev 0 returns to Phase 26 baseline shape (WORST=0.047% zeros vs 83.8% pre-revert); Phase 28 v1 PORTx-clear regression cleanly removed via revert; `_NOP()` settling preserved. Read-bug itself carries to v1.8.
**v1.8 shipped:** 2026-05-29 (Host CLI Structural Cleanup — 8 phases, 27 requirements DELIVERED + 3 VERIFIED-at-close; argparse → Click migration; flat layout preserved (no subpackage reorg); ruff + ruff-format + mypy strict on 8 modules + 70% coverage floor enforced in CI; 2 latent bugs fixed as INTENTIONAL BEHAVIOR CHANGE (BUG-1 `build_arg_flags`, BUG-2 except-clause split); ship tag `3.0.0b7` beta-only; v1.8-app-cleanup → beta + meta-repo → main; firmware sub-repo untouched at `beta@0bbe017`; read-bug carries to v1.9 with GATE-1.8d ring-fence intact).
**v1.7 shipped:** 2026-05-26 (RURP Shield Hardware Investigation & Version Detection — 5 phases; per-rev capability table + labeled schematics + shield-version-detect firmware plumbing). Substrate consumed by v1.6 Phase 29 v2 bench session + v1.8 RCA hand-off.
**v1.10 shipped:** 2026-06-07 (Serial Transport Hardening / COBS — 7 phases (49–55; 45–48 reserved for v1.9), 27 plans, 14/14 requirements; beta-only, stable `3.0.1` operator-gated/deferred to the v1.9 read-bug fix). Custom COBS `0x00` + CRC8 framing with automatic resync on **both** the data-block path and the host→fw JSON command channel; the 2 s `len_u16` timeout cascade is gone; transport proven byte-exact (operator-witnessed bench, Uno 512 B + Leonardo 1024 B, N=5 read + write read-back). uno328pb read instability **persists** on the hardened transport → recorded as transport-exoneration, NOT a hardware fix; RCA stays deferred to v1.9. Serial is now a settled variable for the resumed read-bug RCA.
**v1.12 shipped:** 2026-06-16 (Firmware Protocol Dispatch Hardening + Skeletons — 8 delivering phases (62, 63, 64, 65, 66, 67.1, 69, 70), 22 plans, 17/17 requirements; first firmware-touching milestone since v1.10; dual-repo lockstep merged to `beta` — fw `b71c6fd` / app `6b5480f`, no tag; lockstep beta cut + stable promotion operator-gated). Fail-closed dispatch (`MSG_ERR_PROTOCOL_NOT_IMPLEMENTED = 0xBB`, zero hardware side effects) eliminating the silent `mem_type` 12V-VPP fallback hazard; host `ProtocolNotImplementedError` + actionable CLI message; capability-honest DB (`support_status` taxonomy `protocol-not-implemented`/`adapter-required`/`vpp-exceeds-max`; true NMOS VPP correction; principled pinout classification; in-host refusal before any serial byte). No new chip became programmable. DB 743 → 744. Audit tech_debt (17/17 reqs, 8/8 phases, 5/5 E2E flows, secure-gated phases threats_open:0); accepted tech debt = hollow GATE-03 detector (host guard authoritative) + Nyquist gaps on 6/8 phases. See `.planning/MILESTONES.md` §v1.12; ROADMAP archived at `.planning/milestones/v1.12-ROADMAP.md`.
**v1.11 shipped:** 2026-06-10 (Complete infoic.xml Decode & Database Correctness — 6 phases (56–61), 14 plans, 15/15 requirements; HOST-ONLY, firmware untouched like v1.8; beta-only, stable operator-gated). Authoritative source-grounded field dictionary + corrected decode docs; re-derived `build_db.py` (4 decode bugs fixed: `interpret_timing` ×100, VCC nibbles 0x02/0x03, vcc/vdd swap, PROTOCOL_MAP canonicalization); principled `resolve_pinout_key` replacing guess tables; 9 × 24-pin AT28C04/16 EEPROMs unblocked host-only (`DIP24_2816` + `0x0D`); full-class VPP-safety gate (`check_dispatch.py`, 743 chips, 0 violations) + per-chip diff gate (`diff_db.py`) + pinned baseline. Display layer (`firestarter info` + `list`/`search`) now reflects `electrical.type` ground truth (EEPROM vs UV-EPROM, no spurious SRAM VPP). Post-close FM1608 follow-up: SRAM/FRAM Vcc→5V normalization, zero-pulse-delay row suppression, chip-ID `-` placeholder. Audit PASSED 15/15, 5/5 E2E flows, 559 tests green. Meta tagged `v1.11`; lockstep beta cut (`3.0.0b9`) operator-gated.
**v1.13 shipped:** 2026-06-18 (Programming Algorithm Validation + Gap Implementation — 5 delivering phases (71–74, 76), 19 plans, 17/17 requirements; first firmware-touching milestone since v1.12; dual-repo lockstep merged to `beta` — fw `a33513f` / app `34deccb` @ `3.0.0b9`, no tag; beta cut + stable operator-gated). Three-tier software-first validation harness + per-family matrix proving the 6 write/program/verify families (PARTIAL bench coverage, Leonardo Tier-3); evidence-driven feasible-gap subset (flash4 chip-id + W29C040 SDP/page-write; spec-only AT28C04/16 adapter arm + DIP24→DIP32 spec; X88C64 0x34 MEDIUM verdict, no handler). No chip graduated to `supported` (→ v1.14 Backlog 999.4–999.7). Phase 75 erase + Phase 74 Wave-2 HW re-bench deferred to v1.14. See `.planning/MILESTONES.md` §v1.13.

**v1.14 shipped:** 2026-06-23 (Feasible-Gap Implementation — 4 phases (77–80), 9 executed plans of 13, host-only delta; the first milestone since v1.0 where chips actually **graduate to `supported`**. 1 fully landed + bench-proven (erase write-path, Phase 77), 1 software-side best-effort (25V NMOS, Phase 79), 2 cleanly deferred on hardware blockers (X88C64 PCB-block Phase 78 → FUT-01; AT28C04/16 adapter-not-built Phase 80 → FUT-04). 6 reqs verified · 2 software-complete · 7 hardware-gated deferrals. Audit `gaps_found` but all gaps intentional/operator-authorized; integration PASS (744-chip gate 0 violations, 650 tests). Meta tagged `v1.14`, gsd planning merged to `beta`; lockstep beta cut `3.0.0b11` + gitlink bump operator-gated. See `.planning/MILESTONES.md` §v1.14.)

**v1.15 shipped:** 2026-06-25 (Bench Validation of Operator Inventory — 4 phases (81–84), 15 plans; 23 reqs: 21 satisfied · GRAD-03 deferred best-effort (D-22) · FIX-01 closed-by-disposition (D-43). Bench-validated 11 physical chips across 5 algorithm families on Leonardo + RURP Rev 2.0 via full write→read→verify, with a per-chip `EVIDENCE.{md,json}` record + consolidated `DECODE-AUDIT.md`. First Flash/EEPROM auto-erase silicon proof (W29C020); 2516 graduated via a datasheet-grounded user-override entry (genuinely absent from minipro). In-posture FIX-01 fixes shipped — firmware VPP-skip on read/blank-check + host SRAM/FRAM blank-check short-circuit + FM1608 SRAM→FRAM relabel; deeper write-path defects RCA'd + named-tracked (AM27C020 0x08 → FUT-06; W29C040 flash4 → CR-01 / Phase-74 Wave-2; 2516 0x0B read instability → FUT-03). One firmware delta (VPP-skip, fw `cb947c7`); host `4d5b3de`. Meta tagged `v1.15`, gsd planning merged to `beta`; lockstep beta cut `3.0.0b11` + gitlink bump operator-gated (gitlinks PINNED). See `.planning/MILESTONES.md` §v1.15.)

**v1.16 status:** STARTED 2026-06-25 (Protocol-First Architecture Rebuild — defining requirements; phase numbering continues at Phase 85; promoted from the `/gsd-explore` 2026-06-25 seed per operator instruction). See "## Current Milestone" below.

## Current Milestone: v1.16 Protocol-First Architecture Rebuild

**Goal:** Turn Firestarter's inherited-from-minipro hex-ID protocol buckets into a named, datasheet-verified, primitive-decomposed architecture with a per-protocol bench-verification ledger — shrinking the Leonardo flash ceiling (~89.5% today) via shared-primitive reuse, without changing the minipro DB as ground truth.

**Target features (staged):**
- **Datasheet acquisition** — new top-level `datasheets/` folder: all 11 on-hand ICs + one representative chip per no-silicon minipro protocol bucket, so every protocol has a verification source.
- **Naming + documentation pass** — author the protocol vocabulary (hex bucket → proper human name → datasheet-verified behavior) and document each firmware handler's *why* (timing, VPP, pin roles, write/erase algorithm). Dispatch structure unchanged; near-zero flash delta.
- **Primitive decomposition / refactor** — extract shared primitives (address setup, data strobe, poll/verify, VPP gate, page buffer, SDP unlock, chip-id), recompose handlers from them, measure flash savings; incremental, one protocol family at a time, guarded by native register-level tests + `check_dispatch.py` / `diff_db.py`.
- **Per-protocol bench validation** — bench-prove each protocol with silicon on Leonardo + RURP Rev 2.0; record results in a per-protocol verification ledger composing with the v1.13 per-family matrix + v1.15 `EVIDENCE.{md,json}`; carry no-chip protocols as explicit `UNVERIFIED`.

**Key context (locked decisions from the `/gsd-explore` 2026-06-25 session):**
- Minipro/infoic-derived `chip_database.json` STAYS the ground truth for firmware control values; datasheets only verify interpretation + document the *why* (preserves algorithm-first dispatch / no-guessing).
- Naming = both-in-sequence: rename + document existing buckets first (structure stable), THEN re-decompose into shared primitives.
- "Working" = bench-proven on **Leonardo + RURP Rev 2.0 only** (the only trustworthy combo, v1.9 read bug elsewhere); no-chip protocols stay explicit `UNVERIFIED` — honest gaps, never false confidence.
- Driver = shrink ~89.5% flash via shared-primitive reuse (duplication across `configure_eprom`/`configure_sram`/`configure_flash`/flash4 is the main culprit).
- Dual-repo lockstep for any wire-touching change (`constants.py` ↔ `firestarter.h`); reuse-first (no new third-party deps); watch the py3.12-masks-CI-3.11 ruff/codegen trap.
- Seed: `.planning/seeds/protocol-first-architecture-rebuild.md`; rationale: `.planning/notes/protocol-rebuild-rationale.md`; open research questions: `.planning/research/questions.md` (protocol-rebuild block).

## v1.15 Archive: Bench Validation of Operator Inventory — Shipped 2026-06-25

**Goal (achieved):** Bench-validate the operator's 11 physical chips (5 algorithm families) on Leonardo + RURP Rev 2.0 via full write→read→verify — proving the on-paper `supported` claim true on real silicon, RCA-ing/fixing failures, validating DB decode, producing a per-chip evidence record, and graduating the one genuine gap (the `2516`).

**Delivered (21/23 requirements satisfied · 2 closed-by-disposition):** All 11 chips exercised on silicon and recorded in `.planning/v1.15/bench/EVIDENCE.{md,json}` + consolidated `.planning/v1.15/DECODE-AUDIT.md`. **Silicon PASSes:** W27C512 + SST27SF512 (0x07), SST39SF040 (0x06), W29C020 (0x05 — first Flash/EEPROM auto-erase silicon proof), FM1608 (0x40 overwrite), ST M27C512 UV write (0x07, operator-directed partial spend). **Genuine FAILs faithfully recorded (not DB/algo faults):** W27E512 / W27E040 stuck-bit silicon wear (D-32 silicon-limited); W29C040 flash4 256B page-0 fault (Phase-74 fix NOT silicon-effective → reopen Phase-74 Wave-2 / CR-01); AM27C020 0x08 write 0-bits-programmed (→ FUT-06); 2516 0x0B read instability (3 distinct SHAs persisting after the VPP-skip fix → FUT-03, GRAD-03 deferred best-effort per D-22). **FIX-01 closed-by-disposition (D-43):** in-posture fixes SHIPPED (firmware VPP-skip on CMD_READ/CMD_BLANK_CHECK clearing the 18.8V boot-refusal + host SRAM/FRAM blank-check short-circuit killing the 0xA4 MSG_ERR_EMPTY_INPUT + FM1608 SRAM→FRAM relabel) with deeper write-path defects RCA'd + named-tracked. Milestone audit `gaps_found` is stale (predates Phase 84 execution); both flagged gaps (GRAD-03, FIX-01) closed-by-disposition + operator-accepted. 3/4 phases Nyquist-compliant; Phase 84 SECURED (threats_open:0). One firmware delta (VPP-skip); otherwise host-side. Meta tagged `v1.15`, gsd planning merged to `beta`; lockstep beta cut + gitlink bump operator-gated. See `.planning/MILESTONES.md` §v1.15; ROADMAP archived at `.planning/milestones/v1.15-ROADMAP.md`; requirements at `.planning/milestones/v1.15-REQUIREMENTS.md`; audit at `.planning/milestones/v1.15-MILESTONE-AUDIT.md`.

<details>
<summary>v1.15 original scope framing (pre-close)</summary>

**Goal:** Bench-validate the operator's physical chip inventory (11 chips spanning 5 algorithm families) on Leonardo + RURP Rev 2.0 via full write→read→verify — proving the on-paper `supported` claims true on real silicon, RCA-ing and fixing any failures, validating DB decode correctness, and graduating the one genuine gap (the `2516`, confirmed absent from minipro upstream).

**Target features:**
- **Reusable per-chip bench evidence record** — a repeatable write→read→verify procedure + a per-chip pass/fail/SHA matrix document, reusing `dev validate-family` + `write_test.sh` (no new harness).
- **Validate the 8 electrically-rewritable chips on silicon** — W27C512, W27E512, SST27SF512 (0x07), W27E040 (0x08), SST39SF040 (0x06), W29C020 + W29C040 (0x05), FM1608 (0x40): full write→read→verify cycle, confirming the `supported` claim and the auto-erase path where applicable.
- **UV-EPROM no-eraser test protocol** (ST M27C512, AM27C020, 2516) — non-destructive read + blank-check FIRST (validates read path / decode / VPP-for-read with zero chips consumed); then a per-chip spend-vs-preserve decision AT the bench (full real image if blank; else an AND-mask / all-0x00 bit-subset write proof, which only needs 1→0 transitions and is verifiable without an eraser).
- **2516 investigation + graduation** — confirmed absent from minipro `infoic.xml` (the 28 "2516" hits are all `25160` SPI serial parts); author a datasheet-grounded DB entry (NMOS ~25V class, DIP24, alg 0x0B / 2716-family profile) and bench-prove it on the ~22.4V VPE rail — doubling as the deferred FUT-03 NMOS write+SHA evidence.
- **DB decode-correctness validation** — confirm real-silicon behavior matches the DB (pinout, VPP, electrical type, algorithm, size) for every chip exercised; flag/fix any mismatch.
- **Defect RCA + fix** (conditional) — any per-family write/program/verify failure the bench surfaces is root-caused and fixed in lockstep.

**Key context:**
- **Board/shield LOCKED: Leonardo + RURP Rev 2.0** — the only trustworthy program/write/verify combo (v1.9 read bug corrupts the oracle elsewhere; uno328pb N/A for program/write). Standing bench discipline applies: live R1/R2 readback (`r1 ≈ 270000`) each task, verify `controller:` port identity per task; Leonardo is chip-OUT-sideload-exempt.
- **Most of the inventory is already `supported` on paper but unproven on silicon** — only W27C512 (P77), SST39SF040 + W29C040 (P74), FM1608 (P73) carry prior bench evidence. So the dominant goal is to *prove the claim*, not mass-graduate. The `2516` is the one true graduation candidate.
- **UV-EPROMs are irreversibly written without an eraser** (operator has none) — hence read-only/blank-check first, spend decided per-chip live. W27C512/W27E512/SST27SF512 etc. are *electrically*-erasable EEPROMs (auto-erase) and are NOT affected by this constraint.
- **Phase numbering continues from v1.14's last phase (80) → v1.15 starts at Phase 81.** Mostly host-side (2516 DB entry + evidence tooling); firmware likely untouched unless a bench-surfaced defect forces a lockstep fix. Branch off `beta` per standing policy; v1.14's `3.0.0b11` lockstep beta cut remains operator-gated (gitlinks PINNED).

</details>

## v1.14 Archive: Feasible-Gap Implementation — Shipped 2026-06-23

**Goal (achieved, with honest deferrals):** Graduate chips to `supported` by implementing the four evidence-surfaced, RURP-feasible gaps v1.13's validation milestone scoped out — the first chips to become newly programmable since v1.0.

**Delivered:** Of the four gaps, **1 fully landed + bench-proven** (erase write-path), **1 landed software-side best-effort** (25V NMOS), **2 cleanly deferred on genuine hardware blockers** (X88C64 PCB-block, AT28C04/16 adapter-not-built) — every deferral FUT-tracked. **Phase 77 (ERASE-01/02, SAFE-01/02/03, verified 5/5):** `FLAG_CAN_ERASE` derived from canonical `electrical.type == "EEPROM"` so the 7–8 0x07 EE-EPROMs auto-erase before programming; the full write→auto-erase→program→verify cycle bench-proven on a real W27C512 on the Leonardo (SHA match) — the milestone's first hardware graduation; established the SAFE-01/02/03 guard-removal-last discipline. **Phase 78 (XIC-01, verified 7/7):** A6 ALE-routing verdict PCB-BLOCKED (HIGH) — control register fully allocated, no free 74HC573 strobe; contingent handler took the DEFER branch (zero firmware code); X88C64 stays protocol-not-implemented/host-refused (FUT-01). **Phase 79 (NMOS-02, best-effort under operator override D-07):** host VPP ceiling raised 22000→25000 (`build_db.py` + `check_dispatch.py`), DB regenerated so the 4 NMOS UV-EPROMs (INTEL M2716, INTEL 2732/M2732, SGS-THOMSON ETC2716, ST ETC2716) graduate `vpp-exceeds-max` → `supported` (0x0B, vpp_mv=25000); they program on the existing 0x0B direct-VPE rail (22.4V DMM / 23.9V fw, ~90% of 25V) where the firmware warns-and-proceeds on under-voltage (over-voltage stays blocked); no hardware change ever. **Phase 80 (ADPT-01 evaluated NOT CLEARED):** adapter not built / no chip on hand → clean zero-change deferral; the 9 AT28C chips stay honestly `adapter-required` (FUT-04). Audit `gaps_found` but all gaps are intentional, operator-authorized, hardware-gated deferrals; integration PASS (744-chip dispatch gate 0 violations, 650 host tests, constants parity 8/8). Host-only (firmware untouched on `beta`); meta tagged `v1.14`, gsd planning merged to `beta`; lockstep beta cut + gitlink bump operator-gated. See `.planning/MILESTONES.md` §v1.14; ROADMAP archived at `.planning/milestones/v1.14-ROADMAP.md`; requirements at `.planning/milestones/v1.14-REQUIREMENTS.md`; audit at `.planning/milestones/v1.14-MILESTONE-AUDIT.md`.

<details>
<summary>v1.14 original scope framing (pre-close)</summary>

**Goal:** Graduate chips to `supported` by implementing the four evidence-surfaced, RURP-feasible gaps that v1.13's validation milestone deliberately scoped out — the first chips to become newly programmable since v1.0.

**Target features** (captured 2026-06-18 in ROADMAP §v1.14, suggested build order 999.4 → 999.5 → 999.7 → 999.6):
- **Erase write-path for 0x07 EE-EPROMs** (was v1.13 Phase 75 / ERASE-01) — wire `FLAG_CAN_ERASE` from `electrical.type == "EEPROM"` (not `info-flags & 0x10`) so writing a W27C512-class chip auto-erases first. Standalone erase electricals already bench-confirmed (Phase 73). Mostly software; most-ready.
- **X88C64 0x34 firmware handler** (`configure_x88c64`) — XICOR X88C64P DIP24 5V EEPROM, 8051 multiplexed address/data bus (ALE/WR/RD), page write, toggle-bit (I/O6) polling. Resolve the open ALE-routing control-bit question before shipping. Per Phase 76 MEDIUM feasibility verdict.
- **25V NMOS support** (M2716/M2732/ETC2716/ST M2716) — raise `RURP_VPP_CEILING_MV` 22000 → 25V and re-classify the 4 `vpp-exceeds-max` chips. **Verify a shield rev can physically produce 25V VPP FIRST** (operator multimeter, chip-OUT dry-run) — the ceiling reflects a hardware limit, not just a constant.
- **AT28C04/16 adapter graduation** — graduate the 9 `adapter-required` chips via the existing `configure_eeprom28c` (0x0D, VPP-free) handler + a physical DIP24→DIP32 adapter (Phase 76 pin-map spec); remove the host-guard refusal. **Hardware-blocked until the adapter is built** → sequence last.

**Key context:**
- Firmware-touching → dual-repo lockstep; all four subject to flash-budget ordering (the ~88% Leonardo flash ceiling that drove v1.13). Branches off `beta` in all 3 repos, merge back to `beta`; beta→stable operator-gated.
- Phase numbering continues from v1.13's last phase (76) → v1.14 starts at **Phase 77**.
- Operator decision 2026-06-18: do all four; implement 25V NMOS assuming hardware can produce 25V.
- Pre-req: v1.13's lockstep beta cut (`3.0.0b10`) is operator-gated; v1.14 branches off `beta`.

> **At close (2026-06-23):** the "verify a shield can produce 25V FIRST" pre-gate (Phase 79 NMOS-01) was RETIRED by operator override D-07 — the bench tops out at ~22.4V VPE (~90% of 25V) and the operator authorized a best-effort graduation with no hardware change ever. The X88C64 ALE question (Phase 78) and the adapter (Phase 80) resolved as genuine hardware blockers → clean FUT-tracked deferrals.

</details>

## v1.13 Archive: Programming Algorithm Validation + Gap Implementation — Shipped 2026-06-18

**Goal (achieved):** Prove the firmware's existing write/program algorithm families work correctly on real hardware (test-first), then implement the genuine gaps that testing + research reveal — letting evidence define what "missing" means.

**Delivered (17/17 requirements):** A reusable software-first **three-tier validation harness** (Tier-1 native recording-bus stub + per-family Unity suites; Tier-2 host pytest wire round-trips; Tier-3 `dev validate-family` HIL runner) + a declarative per-family **validation matrix** with a non-vacuous PASS oracle (Leonardo-only-PASS / negative-control / live-R1 / uno328pb-N/A), closing the v1.12 hollow GATE-03 tech debt by populating `check_dispatch.py`'s `non_supported_dispatchable` detector (HARN-01..04). Protocol re-research (RSCH-01) re-confirmed v1.12's feasible set with 3 surviving gaps + anti-features fail-closed. Bench validation on Leonardo/Rev 2.0 (VAL-01..06, hybrid-gated PARTIAL): W27C512 UV-EPROM Tier-3 authoritative PASS; SST39SF040 flash3 PASS; W29C040 flash4 real-FAIL→fixed; FM1608 SRAM two-pattern PASS (FIX-01 closed not-needed — `configure_sram` persists). Per-family fixes (FIX-02/03): flash4 `CMD_CHECK_CHIP_ID` dispatch mirror + W29C040 SDP-unlock/data-driven page-write (Leonardo flash held at 89.5% via a shared AMD chip-ID util); 0x35/0x39 phantom-comment reconciliation. Spec-only gaps (GAP-01/02): a named `_AT28C_DIP24_NAMES` `resolve_pinout_key` arm classifying 14 AT28C04/16 aliases as `adapter-required` + a two-layer DIP24→DIP32 adapter pin-map spec; X88C64 0x34 a datasheet-accurate MEDIUM feasibility verdict (8051 multiplexed bus; NO handler committed). No chip graduated to `supported` (explicitly OUT of scope → v1.14 Backlog 999.4–999.7). Dual-repo lockstep merged to `beta` (fw `a33513f` / app `34deccb` @ `3.0.0b9`, no tag — beta cut + stable operator-gated). **Phase 75 (erase path) + Phase 74 Wave-2 (W29C040 HW re-bench) deferred to v1.14.** See `.planning/MILESTONES.md` §v1.13; ROADMAP archived at `.planning/milestones/v1.13-ROADMAP.md`; requirements at `.planning/milestones/v1.13-REQUIREMENTS.md`.

<details>
<summary>v1.13 original scope framing (pre-close)</summary>

**Goal:** Prove the firmware's existing write/program algorithm families work correctly on real hardware (test-first), then implement the genuine gaps that testing + research reveal — letting evidence define what "missing" means.

**Target features:**
- **Validate the 6 implemented algorithm families on hardware** — UV-EPROM (`configure_eprom`, 0x07/08/0B), Flash AMD (`configure_flash3`, 0x06), Flash type-4 (`configure_flash4`, 0x05/35/39), Flash Intel (`configure_flash_intel`, 0x10), 5V EEPROM (`configure_eeprom28c`, 0x0D), SRAM (`configure_sram`, 0x0E/27/28/29) — write/program/verify, behind a reusable **test harness + validation matrix** built software-side first.
- **Re-research the protocol landscape** — re-enumerate genuinely-feasible-but-unimplemented protocols/chip operations (revisit v1.12's "feasible set is complete" finding; surface any real gap such as the deferred erase path).
- **Per-family write/program correctness fixes** — fix algorithm bugs that bench testing exposes in the existing families.
- **adapter-required chip support** — implement chips needing a physical adapter / pin remap (hardware-dependent on having/making the adapter).

**Key context:**
- **Hybrid bench gating** — the test harness + validation matrix are software (no bench gate); bench-validate the families with chips + a working shield on hand; defer families needing parts not available. Closeable without proving 100% of families.
- **Leonardo is the trustworthy verify board** (EVEN-01 write+verify proven clean); the v1.9 shield-fleet read-bug RCA stays a **separate** deferred milestone (avoids the uno328pb program-brownout + Rev-0/2.0 read faults). Per `feedback_chip_out_before_sideload` + `feedback_verify_port_identity_each_task` for any bench work.
- **Erase-command support** (deferred `firestarter erase` 0x07-path) is NOT a committed deliverable; it may resurface via research.
- First firmware-touching milestone since v1.12; **dual-repo lockstep**; branches off `beta` in all 3 repos; merge back to `beta`; beta→stable operator-gated. Phase numbering continues from v1.12's last phase 70 → v1.13 starts at **Phase 71**.

</details>

## v1.12 Archive: Firmware Protocol Dispatch Hardening + Skeletons — Shipped 2026-06-16

**Goal (achieved):** Make the whole stack honest about what it can and cannot program — fail-closed firmware dispatch with an explicit "not implemented" wire response the host surfaces cleanly, plus a capability-honest database that lists (not silently drops) the DIP parallel chips RURP cannot fully support. Framework + honest reporting only; no new chip became programmable.

**Delivered (17/17 requirements):** Firmware now fail-closes — a non-zero unimplemented `protocol` returns `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` (0xBB) with zero hardware side effects via `configure_not_implemented()` behind a `protocol != 0` guard, closing the silent `mem_type → configure_eprom` 12V-VPP hazard (DISP-01..04, WIRE-01/02, TEST-01/02; 49/49 native Unity tests, Uno 72.4% flash). The host raises a typed `ProtocolNotImplementedError(EpromOperationError)` and prints an actionable message, with the probe/connect boundary wired so the 0xBB frame reaches the CLI (HOST-01/02). `build_db.py` includes unknown-protocol DIP chips marked `support_status: protocol-not-implemented`; the authoritatively-known NMOS family records true VPP (M2716/M2732 = 25V → `vpp-exceeds-max`, M2732A = 21V → `supported`) against `RURP_VPP_CEILING_MV=22000`; every chip carries a `support_status` (DB-01/03/05). Pinouts are classified not skipped — 14 SRAM chips corrected via extended `resolve_pinout_key` rules; genuinely-unmappable chips are `adapter-required` (DB-02). The host reports capability honestly: `info` shows a status-specific support line, and `write`/`read`/`verify` refuse in-host (via `chip_resolver.resolve_chip` → `ChipNotImplementedError`) before any serial byte, rendering the DB reason string verbatim (DB-04). DB grew 743 → 744. The v1.12 branch — forked off the pre-v1.11 beta — was re-ported onto v1.11's `resolve_pinout_key` architecture (Phase 70) and merged to `beta` dual-repo lockstep (fw `b71c6fd` / app `6b5480f`, no tag). See `.planning/MILESTONES.md` §v1.12, `.planning/milestones/v1.12-MILESTONE-AUDIT.md`; ROADMAP archived at `.planning/milestones/v1.12-ROADMAP.md`; requirements at `.planning/milestones/v1.12-REQUIREMENTS.md`.

**Accepted tech debt at close (operator 2026-06-16):** the GATE-03 `non_supported_dispatchable` detector in `check_dispatch.py` is hollow (declared, asserted empty, never populated) — the host guard `chip_resolver.resolve_chip` is the authoritative safety layer, so there is no live 12V-to-wrong-pin hazard. Latent WR-01 (Site B `0x00` re-promoted to `0x0D` for the 9 adapter-required EEPROMs; electrically safe). Nyquist validation gaps on 6/8 phases (3 missing VALIDATION.md: 63/64/65; 3 partial: 62/67.1/69) — non-blocking; behavioral coverage holds via VERIFICATION.md + the integration check.

<details>
<summary>v1.12 original scope framing (pre-close)</summary>

**Goal:** Make the firmware honestly report unimplemented programming protocols — fail-closed dispatch with an explicit "not implemented" response the host surfaces cleanly — and scaffold skeleton handlers for the missing but RURP-feasible protocols.

**Target features:**
- **Fail-closed dispatch** — any `protocol` without a real handler returns an explicit "protocol not implemented" response; the silent `mem_type` fallback (a chip with an unimplemented protocol but `mem_type=1` currently routes to `configure_eprom` → 12V VPP, a hardware-damage path) is removed/guarded.
- **Distinct "not implemented" wire response** — a new response code/message (lockstep firmware ↔ host) so the host distinguishes "protocol unimplemented" from a generic operation failure.
- **Host graceful handling** — `firestarter write/read <chip>` reports a clear "this chip's protocol isn't implemented yet" message instead of a cryptic error.
- **Skeleton handlers** — stub handlers that report not-implemented for the missing-but-feasible protocols, registered in dispatch + documented, ready to fill in later.
- **Protocol-gap enumeration** — classify every minipro `protocol_id` as implemented / skeleton-needed / infeasible-on-RURP, grounded in the v1.11 field dictionary + minipro source.
- **Native dispatch tests** covering the fail-closed and skeleton paths.

**Key context:**
- **Firmware milestone** — primary surface is the `firestarter` sub-repo (`memory.cpp` dispatch + `src/proms/` handlers); **dual-repo lockstep** wire change (host detects the new response). Builds on v1.11's `protocol_id` field dictionary + `check_dispatch.py`.
- **Framework + skeletons only** — actual per-protocol programming logic is deferred to future per-protocol (mostly hardware-gated) milestones; this milestone makes the firmware honest about what it does/doesn't implement and scaffolds the gaps.
- Removing the `mem_type` fallback is a deliberate, safety-motivated behavior change (guarded escape hatch only if justified).
- **Branch model (unified beta, 2026-06-10):** all three repos derive `v1.12-protocol-dispatch-hardening` off `beta` and merge back to `beta`; `beta`→stable is operator-gated. Meta `beta` created at the v1.11 tip; firmware sits on `beta` (clean — v1.11 was host-only); the deferred v1.11 host work must reconcile into `firestarter_app/beta` before the v1.12 host changes. See [[feedback-branching-firestarter-milestones]].

> **At close (2026-06-16):** the "reconcile v1.11 host work into beta before v1.12 host changes" constraint materialized as a full architecture collision — v1.12 was forked off the *pre-v1.11* beta, so its DB-build pipeline clashed with v1.11's Phase 58 `resolve_pinout_key` rewrite. Resolved by **Phase 70** (re-port, not conflict-merge); both sub-repos merged to `beta`.

</details>

## v1.11 Archive: Complete infoic.xml Decode & Database Correctness — Shipped 2026-06-10

**Goal (achieved):** Authoritatively decode every Firestarter-relevant field in minipro's `infoic.xml` — grounded in the minipro C source — and rebuild the database decode so every DIP parallel memory the RURP shield can physically drive is correctly classified, with an authoritative field-dictionary reference and a correctness/regression gate.

**Delivered (15/15 requirements):** DEC-01..05 (source-grounded field dictionary + corrected `build_db.py` decode); PIN-01..03 (principled `resolve_pinout_key`; 9 × 24-pin EEPROM unblock); DOC-01..03 (corrected `protocol-id.md`/`protocol-flags.md`/`package-details.md`); GATE-01 (pinned baseline — operator-authorized live-fetch deviation D-01/D-02, regression anchored via `chip_database.baseline.json`); GATE-02 (`diff_db.py` per-chip diff); GATE-03 (full-class VPP-safety guard); GATE-04 (`configure_sram` NVRAM audit, host-side, no firmware escalation). Phase 60 (display-layer `info` correctness) + Phase 61 (list/search parity via shared `resolve_type_label`) extended the corrected decode to the operator-facing presentation; a post-close FM1608 follow-up normalized SRAM/FRAM Vcc to 5V and cleaned the info-view (no zero pulse-delay row; chip-ID `-` placeholder). DB grew 734 → 743 chips (the 9 unblocked EEPROMs). See `.planning/MILESTONES.md` §v1.11, `.planning/v1.11-MILESTONE-AUDIT.md`; ROADMAP archived at `.planning/milestones/v1.11-ROADMAP.md`; requirements at `.planning/milestones/v1.11-REQUIREMENTS.md`.

<details>
<summary>v1.11 original scope framing (pre-close)</summary>

**Goal:** Authoritatively decode every Firestarter-relevant field in minipro's `infoic.xml` — grounded in the minipro C source — and rebuild the database decode so every DIP parallel memory the RURP shield can physically drive is correctly classified, with an authoritative field-dictionary reference and a correctness/regression gate.

**Scope corrected after research (2026-06-08):** The original framing ("expand to all types + add firmware handlers, dual-repo") was overturned by source-grounded research. The hardware-feasible memory set is **already covered**: the "exotic" `0x2A/0x2C/0x2E` are GAL/PIC PLD/MCU protocols with zero DIP memory chips; FWH `0x11` is LPC-serial + 3.3V (infeasible on RURP); real battery-backed NVRAM/timekeeper is already handled via existing SRAM protocols. The only genuine new-chip gap is ~9 blocked 24-pin EEPROMs (AT28C04/AT28C16 family), unblockable **host-only** (`DIP24_6116` pinout + `algorithm=0x0D`; `configure_eeprom28c` already handles them). **No new firmware handlers are needed** → re-scoped to a **host-only** decode-correctness + documentation milestone (operator-confirmed). See `.planning/research/SUMMARY.md`.

**Target features:**
- **Field dictionary** — authoritative, source-cited meaning of every relevant `infoic.xml` attribute (`package_details`, `type`, `variant`, `protocol_id`, `flags`, `voltages`, `pin_map`, `pulse_delay`, `chip_id`, `code_memory_size`, …).
- **Re-derived `build_db.py` decode** — rebuild decode logic on principled, source-grounded rules (incl. `resolve_pinout_key` from minipro gnd/vcc/pin masks); retire ad-hoc guess tables where a correct decode replaces them, preserving the load-bearing safety overrides.
- **Confirmed decode-bug fixes** — `interpret_timing` ×100 error, `VCC_VOLTAGES` missing 4V/4.5V, `vdd/vcc` field swap, wrong/phantom `PROTOCOL_MAP` names (0x2A/0x2C/0x2E/0x35/0x39/0x3C).
- **24-pin EEPROM unblock** — expose the 9 AT28C04/AT28C16-family chips via `DIP24_6116` + `0x0D`, safety-reviewed (SR-1 checklist); no firmware change.
- **Authoritative decode docs** — corrected canonical `package-details.md` / `protocol-flags.md` / `protocol-id.md`.
- **Correctness gate** — pinned `infoic.xml` snapshot + per-chip diff vs baseline + extended `check_dispatch.py` (full-class VPP-safety guard). No bench required to close.

**Key context:**
- **Host-only milestone** (`firestarter_app` data pipeline + docs). Firmware sub-repo (`firestarter`) is untouched — like v1.8. Branches off `beta` in `firestarter_app`, off `main` in meta; firmware stays put.
- Research artifacts at `.planning/research/` (STACK = field dictionary, FEATURES = protocol/feasibility catalog, ARCHITECTURE = integration, PITFALLS = hazard model, SUMMARY = synthesis).
- Independent of the deferred v1.9 read-bug RCA; phase numbering continues at **Phase 56**.

</details>

## v1.10 Archive: Serial Transport Hardening (COBS) — Shipped 2026-06-07

v1.10 hardened the Arduino↔host serial transport to *provably byte-exact*, inserted **ahead** of the paused v1.9 read-bug RCA so serial corruption is ruled out as a confounder before the per-shield RCA resumes (v1.9 Phase 45+). The trigger was v1.9 Phase 48-01 flipping the COBS verdict DEFER → **ADOPT** (`.planning/v1.9-COBS-DECISION.md` §2): the old `[len_u16][xor][payload]` data-block framing desynced on a single corrupted `len_u16` byte until a 2 s timeout fired and stayed out of sync for the rest of the transfer.

**Delivered (14/14 requirements):** Custom **streaming COBS `0x00` + CRC8-CCITT** framing with automatic resync on **both** the data-block path (Phase 50) and the host→fw JSON command channel (Phase 51, breaking lockstep wire change — CRC8 verified before the JSON parser sees a byte). COBS `0x00` was chosen over SLIP `0xC0` via a conclusive SAFE-01 static proof (Phase 49). The 2 s timeout cascade is gone (recovery now ~1 ms for corrupt frames, a single bounded ~1 s inter-byte deadline for truncated frames). Decode-in-place fits the Uno ~545 B free-RAM ceiling — no second buffer (D-04); CRC8-CCITT poly 0x07 retained unchanged (D-05). Host-encode↔fw-decode byte-compatibility is pinned by a shared golden-vector catalog with round-trip suites + codegen drift gates in both repos (Phase 52). Even-block full-buffer transfers (Phase 54) + buffer-size advertisement relocated to the `MSG_OK_READY` u16 ack with a safe-512 default (Phase 55, reverses Phase 54 D-05). **Phase 53 bench (operator-witnessed):** N=5 read + write read-back byte-identical on clean Uno + Leonardo (Rev 2.0); resync proven on real hardware both directions/both fault forms; uno328pb read instability **persists** on the hardened transport → structured transport-**exoneration** verdict (NOT a per-shield fix). Bench evidence at `.planning/v1.10/bench-verification/SUMMARY.md`. Branch `v1.10-serial-transport-hardening` was stacked off the `v1.9-read-bug-rca` tip in all 3 repos (NOT off main/beta — stale at v1.8 close); merging v1.10 first also carries v1.9's unmerged commits forward.

See `.planning/MILESTONES.md` §v1.10 for the full delivery summary; ROADMAP archived at `.planning/milestones/v1.10-ROADMAP.md`; requirements at `.planning/milestones/v1.10-REQUIREMENTS.md`.

## Paused Milestone: v1.9 — Read-Bug RCA + Fix (DEFERRED again 2026-06-08)

**Status:** ⏸ DEFERRED by operator 2026-06-08 ("skip that bug for now") — v1.10 shipped and was merged to beta locally; v1.9 is intentionally NOT resumed. No active milestone. When picked back up it resumes at Phase 45.
<!-- prior status line retained below for the resume trail -->
**Resume note:** Resumes at Phase 45 (Bug B RCA — Rev 2.0). PAUSED 2026-06-01 at Phase 44 to insert v1.10 (above); STARTED 2026-05-29 (scope locked via `/gsd-new-milestone`); proposed 2026-05-26 at v1.6 close; renumbered v1.8 → **v1.9** on 2026-05-27 when the host-CLI cleanup took the v1.8 slot. **Progress at pause:** Phase 44 (Bug A RCA — Modified Rev 0) complete; Phase 48 plan 48-01 (COBS-01 evaluation) complete and the verdict flipped DEFER→ADOPT (this is what triggered v1.10). **Remaining:** Phases 45 (Bug B RCA), 46 (Fix Design & A/B), 47 (Acceptance Gate + backlog closures), plus Phase 48 plans 48-02 (TYPE-01) and 48-03 (milestone close). Phase dirs `44-*` and `48-*` preserved in `.planning/phases/`. **Resume:** `/gsd-plan-phase 45` once the hardened transport is merged. Hardware-gated; firmware sub-repo work expected from Phase 46 onward. The transport is now a settled, byte-exact variable — the methodological prerequisite v1.10 was inserted to establish.

**Why:** v1.6 closed with the original read-bug intentionally deferred per D-17v2 re-scope. Phase 29 v2 characterized the bug as two independent failure modes — Bug A (Modified Rev 0 upper-address jitter, A15=1 → 1.86× skew, 63% BIT-RAISE) and Bug B (Rev 2.0 /CE-or-/OE timing + voltage-divider mismatch + VPP=13.1V). v1.9 inherits the diagnostic (`firestarter dev consistency-check`), the 15-binary N=5 bench substrate at `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/`, the Phase 29 v2 H3 block in `.planning/v1.6-EVIDENCE.md`, the v1.7 labeled-schematic + per-rev capability table + shield-version-detect firmware plumbing, AND the v1.8 cleaned-up host read path (GATE-1.8d ring-fence intact — baseline binaries still valid) as the foundation for designing instrumented A/B fix candidates knowing exactly which silkscreen rev sits on the bench at each step.

**Target features (scope locked 2026-05-29):**
- RCA from the characterized hypotheses (Bug A signal-integrity, Bug B timing/voltage)
- Instrumented A/B fix candidates across Modified Rev 0 + Rev 2.0 + Rev 2.2 shields
- Re-iterate Phase 29 acceptance gate (N≥5 byte-identical reads across boards)
- Close VERIFY-01 (uno328pb byte-identity) + VERIFY-03 (1KB low-rate jitter) + VERIFY-04 (Phase 24 BENCH-02 closure)
- Evaluate COBS framing/resync on the serial data path (todo: PacketSerial assessed-not-adopted) as a data-path robustness angle — complementary to the hardware RCA, NOT a Bug A fix (Bug A is hardware upper-address jitter, not a framing fault)
- Lift `eprom_operations.py` mypy strict overrides (DEFERRED per Phase 42 D-07; lifted post-RCA when the read path can be touched freely)
- Phase numbering continues at Phase 44

**Operator next step:** requirements + roadmap being generated via `/gsd-new-milestone` (2026-05-29).

## v1.8 Archive: Host CLI Structural Cleanup (firestarter_app) — Shipped 2026-05-29

v1.8 is a pure-software structural cleanup of the `firestarter_app` Python host CLI. Per GATE-1.8 (a–e) "refactor + fix bugs found" non-regression contract: wire protocol byte-identical, end-user CLI surface preserved, firmware/app constant contract preserved via parity tests, host read path ring-fenced for the v1.9 RCA, full test suite green + entry point installs. 30/30 requirements closed: 27 DELIVERED (TEST-01..05 + TOOL-01..03 + STRUCT-01..05 + DATA-01..04 + SERIAL-01..03 + CLI-01..04 + ERR-01..03) + 3 VERIFIED-at-close (DOC-01 + DOC-02 + MS-01). Two latent bugs fixed as INTENTIONAL BEHAVIOR CHANGEs: BUG-1 `build_arg_flags` truthiness check (Phase 41 Plan 41-01 commit `6241dba`); BUG-2 `eprom_operations._run_state_machine` except-clause split (Phase 42 Plan 42-01 commit `04a0c13`). `main.py` trimmed 932 → 35 lines; `cli_handlers.py` houses 14 `@cli.command()` + `dev` group with 4 sub-commands. Ship tag `3.0.0b7` beta-only (stable `3.0.1` deferred to v1.9 read-bug fix per D-17v2 carry-forward). Firmware sub-repo untouched (host-only milestone; firmware stays at `beta@0bbe017` from v1.6 close).

See `.planning/MILESTONES.md` §v1.8 for the full delivery summary. Per-phase artifacts archived under `.planning/milestones/v1.8-phases/` (via `.planning/v1.8-archive.sh` in Plan 43-02). Coverage table archived at `.planning/milestones/v1.8-REQUIREMENTS.md` (30 rows with per-requirement disposition column). v1.9 hand-off: read-bug (Bug A + Bug B) carries forward with GATE-1.8d ring-fence intact; 15 N=5 W27C512 baseline binaries at `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/` remain valid because `_read_and_parse_lines` body is byte-identical pre/post v1.8.

## v1.6 — Fix the Read Bug — ✓ Shipped 2026-05-26 (diagnostic + revert per D-17v2)

v1.6 ships as a course-correction milestone. Phase 29 v1 Wave B FAIL revealed that Phase 28 v1's `437339b6` PORTx-clear introduced a Leonardo + uno328pb read-path regression (83.8% zero-bytes); Plan 27-05 RCA re-open confirmed dual-cause disposition (Outcome A Leonardo firmware-induced + Outcome B-independent uno328pb hardware). The course-correction landed: `437339b6` reverted via `ea25174` (clean removal of the regression); `4f205e58` `_NOP()` settling preserved (Plan 28-04 parks); Phase 29 v2 PASS_PARKED gate emission (Leonardo Modified Rev 0 returns to Phase 26 baseline shape — WORST=0.047% zeros across N=10). The original 64KB streaming-read byte-jitter bug is NOT fixed — characterized as Bug A (Modified Rev 0 upper-address jitter, A15=1 → 1.86× skew) + Bug B (Rev 2.0 /CE-or-/OE timing + voltage-divider mismatch + VPP=13.1V) and carried to v1.8 as the RCA starting hypothesis substrate.

See `.planning/MILESTONES.md` §v1.6 for the full delivery summary. Per-phase artifacts archived under `.planning/milestones/v1.6-phases/` (via `.planning/v1.6-archive.sh` in Plan 30-02). v1.8 RCA substrate ready: 15 N=5 W27C512 binaries at `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/`; pattern findings in `.planning/v1.6-EVIDENCE.md` Phase 29 v2 H3 block; canonical close narrative in `.planning/phases/29-multi-board-bench-verification/29-04-SUMMARY.md` (or post-archive `.planning/milestones/v1.6-phases/29-multi-board-bench-verification/29-04-SUMMARY.md`); v1.8-deferred bug todo at `.planning/todos/pending/v1.8-seed/large-read-data-jitter-uno328pb.md`. v1.7 substrate (`.planning/v1.7-SHIELD-REVS.md` per-rev capability table + labeled schematics + shield-version-detect firmware plumbing) provides v1.8 the foundation for designing instrumented A/B fix candidates knowing exactly which silkscreen rev sits on the bench at each step.

## v1.5 Archive: Arduino Uno (ATmega328PB) Board Support — Shipped 2026-05-21

**Goal:** Ship `uno328pb` as a third first-class firmware target (alongside `uno` and `leonardo`) — end-to-end from PlatformIO env through stable + beta release artifacts (`firestarter_uno328pb.hex`), through host-CLI installer integration, to a bench-validated write→read-back→verify cycle on the operator's plugged-in ATmega328PB Uno board.

**Target features:**
- PlatformIO `[env:uno328pb]` + custom `boards/uno328pb.json` board definition; firmware compiles for ATmega328PB
- Firmware reports `uno328pb` on handshake so host CLI can match the right `.hex` artifact
- Stable + beta release pipelines publish `firestarter_uno328pb.hex` artifact (additive — `uno` + `leonardo` artifacts byte-identical to pre-v1.5; GATE-1.5)
- Host CLI's `firestarter fw -i` (stable) and `firestarter fw -i --pre` (beta) flash the 328PB board when device reports `uno328pb`; non-regression on `uno` + `leonardo` installs
- Bench-validated write→read-back→verify cycle on operator's 328PB-Uno + RURP shield (at least one representative EPROM, e.g. W27C512)
- Documentation: firmware + app READMEs + meta-repo release procedures cover the third board

**Branch model:** Work branches off `beta` in both sub-repos (per operator instruction). After bench-green, merge `beta` → `main` follows the v1.4-RELEASE-PROCEDURES.md beta→stable promotion pattern. No tag-driven path.

**Locked decisions (v1.5 start, 2026-05-20):**

- **Scope:** Add `uno328pb` as a third firmware target. Use existing v1.4 beta/stable plumbing — no pipeline redesign. The release pipelines emit one additional `.hex` artifact (per-board matrix grows from 2 → 3); the host CLI's `firestarter_{board}.hex` lookup naturally matches when firmware handshake reports `uno328pb`.
- **Out of scope:** 328PB extra peripherals (USART1, TWI1, SPI1, Timer3/4, PE0–PE3 pins) — Firestarter only uses 328P-common I/O; bootloader flashing (operator provisions the board separately); host-side VID/PID auto-detect (firmware-handshake report is authoritative); RURP shield rev changes; new chip support; CMOS bench resume (still v1.3 territory).
- **Board-ID strategy:** Custom PIO `boards/uno328pb.json` so `board = uno328pb` in `[env:uno328pb]`. `name_firmware.py` already derives the artifact name from `env.GetProjectOption("board")`, so this produces `firestarter_uno328pb.hex` with no codegen change, and the host's `firestarter_{board}.hex` lookup needs zero board-name translation.
- **MCU framework:** MiniCore (`platform = MCUdude/MiniCore`) is the established Arduino-framework support for ATmega328PB. Use it as the platform; pin definitions stay Arduino-Uno-compatible for Firestarter's I/O footprint.
- **Buffer size:** Use 512 B `DATA_BUFFER_SIZE` (same as `uno`); 328PB has the same 2 KB SRAM as 328P. Only revisit if compiled binary runs cold against the buffer floor.
- **Handshake-name source of truth:** `RURP_BOARD_NAME=\"uno328pb\"` set per-env in `platformio.ini` (mirror of `uno` and `leonardo`); firmware emits this string in the `MSG_OK_FW_HANDSHAKE` payload's `<board>` slot so host's `firmware.py:check_current_firmware` parses it identically to the existing two boards.
- **Bench validation chip:** Operator confirmed a 328PB-Uno is plugged in. Bench session validates against at least one representative EPROM (default W27C512, swap if operator's chip kit differs). Same `firestarter write/read/verify` flow as the regular Uno — algorithm dispatch is firmware-internal and unchanged by the MCU port.
- **GATE-1.5 (non-regression):** `firestarter_uno.hex` and `firestarter_leonardo.hex` are byte-identical to pre-v1.5 outputs (modulo unavoidable version-string drift from `update_version.py`). Stable-installed app's `firestarter fw -i` defaults still flash the matching artifact for `uno`/`leonardo`-reporting devices.
- **Branch flow:** Both sub-repos cut working branches off `beta` (current tip 5fd751e in both sub-repos as of 2026-05-20). Cut `3.0.1bN` (or appropriate next pre-release) for the first bench-validated cut. Promote `beta` → `main` and bump to stable (`3.0.1`) only after operator green on the 328PB bench cycle. Meta-repo's `.planning/` work proceeds on `main` per existing convention.

## v1.4 — Beta & Pre-release Deployment Pipeline — Shipped 2026-05-20

Added a parallel beta / pre-release deployment channel across both Firestarter sub-repos
without touching the existing main → stable pipelines. Branch-driven trigger (`beta` branch
in each sub-repo) wired to new beta workflows that emit PEP 440 / matching pre-release version
strings, publish PyPI pre-release wheels (installable via `pip install --pre`), and create
GitHub Pre-releases with `make_latest: false` carrying per-board `firestarter_*.hex` artifacts.
App and firmware ship locked-step on a single `BETA_VERSION` operator input. Beta-installed app
grows three new CLI flags (`--pre`, `--firmware-version`, `firmware list`) plus a PEP 440-safe
version comparator; stable-installed app's `firestarter --install` defaults remain byte-identical
to pre-v1.4 (GATE-01 + GATE-02 preserved). The locked-step coordination mechanism uses
manually-paired beta-branch pushes with an explicit `BETA_VERSION` input — documented in
`.planning/v1.4-RELEASE-PROCEDURES.md` and proven via `.planning/phases/15-*/lockstep-dryrun-fixture.sh`.

See `.planning/MILESTONES.md` for the full delivery summary.
Per-phase artifacts archived under `.planning/milestones/v1.4-phases/` (via `.planning/v1.4-archive.sh`).

## v1.3 — CMOS EPROM Family Hardware Validation — ⏸ Paused 2026-05-20 (hardware-gated)

**Status:** Paused at the autonomous/hardware boundary. Phase 11 (Coverage Matrix & DB Inconsistency Audit) shipped clean 2026-05-19 — `.planning/v1.3-COVERAGE-MATRIX.md` + 78-entry defect ledger + all-algorithms wide-scan extension (`.planning/v1.3-COVERAGE-MATRIX-ALL.md` with 137 findings across all 11 DB algorithms) delivered. Phase 12 Wave 0 (desk-side scaffold) committed 2026-05-20.

**Resume from:** `/gsd-execute-phase 12 --wave 1 --interactive` once operator has Uno + Leonardo + RURP shield + DIP-28 socket + scope + the BENCH-01/02/05 chips (W27C512, SST27SF512, W27C257) available.

**v1.4 resume-relevant context:** Phase 18 (Beta-Aware Firmware Downloader, shipped as part of v1.4) added new CLI flags that are directly useful when resuming v1.3 bench validation with pre-release firmware builds:
- `firestarter fw -i --pre` — installs the latest published pre-release firmware for the configured board (avoids manually locating a `.hex` URL).
- `firestarter fw -i --firmware-version X.Y.ZbN` — pins an exact pre-release firmware tag via the GitHub Releases API.
- `firestarter fw --list --pre` (or `--all`) — enumerates available firmware releases with version, channel (Stable/Pre-release), and asset URL.

These flags allow bench operators to install pre-release firmware builds via the app CLI without needing a stable PyPI release first — useful when cutting a bench-validation firmware build on a `beta` branch before promoting it to `main`.

**Why paused:** Operator does not have bench hardware available at this time. Phase 12 plans 12-01/02/03 are operator-on-bench (`autonomous: false`) — they cannot run without hardware. Auto-mode would silently auto-approve checkpoints without real evidence, producing fabricated BENCH-RESULTS rows — that's an integrity hazard the planner explicitly designed against. Cleanest action: pause v1.3, work on software-only v1.4 in the meantime.

**Phase directories preserved:** `.planning/phases/11-*/` and `.planning/phases/12-*/` remain in place (not archived). v1.4 phase numbering continues at 15 to avoid collision when v1.3 resumes.

## v1.2 — Message-ID Logging Rework — ✓ Shipped 2026-05-19

**Delivered:** Every firmware text-prefix log emit (`OK:` / `INIT:` / `MAIN:` / `END:` / `INFO:` / `WARN:` / `ERROR:` / `DEBUG:`) replaced with a 1-byte message-ID + raw-byte-param wire protocol driven by a canonical catalog in `tools/catalog/messages.toml`. Codegen emits C++ header for firmware + Python module for host; both regenerated and byte-identity-checked in CI. Old log helpers deleted; firmware 3.0.0-dev enforces lockstep upgrade.

**Headline result (LMIG-04):** Leonardo Flash 98.7% (28,292 B) → **85.4% (24,482 B)** — 3,792 B of new headroom on the tightest board. Uno 81.1% → 69.0%. Native tests 20/20 PASS, host pytest 29/29 PASS, hardware-bench verified on Uno + Leonardo with both verbose-mode INFO emits and SERIAL_DEBUG breadcrumb chains.

See `.planning/MILESTONES.md` for the full delivery summary. Per-phase artifacts live in `.planning/phases/06-09-*` (and will move under `.planning/milestones/v1.2-phases/` on next cleanup).

## Vision

Replace the current guessing-based chip type mapping with an explicit, protocol-driven architecture where every chip in the database has a known, correct programming algorithm — and the firmware executes exactly that algorithm.

## Current State (v1.0)

The algorithm-first contract is now load-bearing. `chip_database.json`
carries 734 chips with explicit `algorithm` integer = upstream `protocol_id`;
the wire JSON transmits it; `memory.cpp::configure_memory` dispatches a
protocol-prefix `if-return` block for every entry in `KNOWN_PROTOCOLS`
(0x05/0x06/0x07/0x08/0x0B/0x0D/0x0E/0x10/0x27/0x28/0x29/0x35/0x39) to one of
five handlers (`configure_eprom`, `configure_flash3`, `configure_flash_intel`,
`configure_eeprom28c`, `configure_sram`). Legacy `type`-byte enum dispatch
is retained only as a fallback for user-override DB entries.

**What works today (verified):**
- `firestarter write -e W27C512` (UV-EPROM 0x07) — verified by Phase 12 `check_dispatch.py` PASS + Unity dispatch tests
- `firestarter write -e AM29F040` / `SST39SF040` (AMD-style flash 0x06) — sector erase + chip erase
- `firestarter write -e AT28C256` (EEPROM 0x0D, includes 5V SDP-disable + DQ7-polling) — Phase 13 override routes 23 mis-tagged AT28C-family chips to safe handler
- `firestarter write -e 6116` (SRAM 0x0E/0x27/0x28/0x29) — safe no-op stub (no VPP regulator engagement on 5V parts)
- `firestarter info <chip> --adapter` — DIP-mirrored pin-to-signal table
- `python tools/build_db.py` — single canonical pipeline; fetches `infoic.xml` from upstream minipro at runtime

**What is partially supported:**
- `firestarter write -e AM28F010` (Intel-flash 0x10) — code path works but does
  not perform the pre-pulse VPP ADC compare REQ-SAF-01 requires "for every chip".
  See Known Gaps in `.planning/MILESTONES.md`.

## The Core Problem (resolved by v1.0)

The original system had a broken data pipeline that lost minipro's
authoritative `protocol_id`. v1.0 restores the chain end-to-end:

1. `protocol_id` from `infoic.xml` → `algorithm` integer in
   `minipro_complete_db.json` (no guessing, no re-derivation)
2. `algorithm` integer in JSON over the 250000-baud serial protocol
3. `firestarter_handle_t.algorithm` in firmware → `memory.cpp::configure_memory`
   protocol-prefix dispatch
4. Correct handler executes correct pulse timing and VPP routing per chip family

## What Must Be TRUE — Validated by v1.0

1. ✓ **minipro `protocol_id` is the authoritative source** — v1.0 (verified by
   `check_dispatch.py` across 734 chips; no guessing fallback in non-user-override path)
2. ✓ **An explicit `algorithm` field is transmitted over serial** — v1.0
   (`firestarter_handle_t.algorithm` parsed and propagated; legacy `type` retained as fallback)
3. ✓ **Firmware dispatches on `algorithm`, not `type`** — v1.0 (handlers
   implemented: configure_eprom, flash3, flash_intel, eeprom28c, sram)
4. ✓ **Database pipeline is deterministic** — v1.0 (single `build_db.py`;
   byte-identical regeneration on stable upstream XML; REQ-DB-05)
5. ✓ **DIP 24/28/32 packages fully covered** — v1.0 (filter clean; 734 chips
   across 27xx UV-EPROM, 29xx/39xx Flash AMD, Intel Flash, parallel EEPROM, SRAM)

## The One Thing That Must Work — ✓ Validated

A W27C512, a 29F040, an SST39SF040, and a 28C256 are all dispatched to
their correct algorithm from the database (not guessed). Hardware verification
on a physical RURP shield is deferred to a v1.1 hardware-test pass.

## Out of Scope (audit after v1.0)

- SMD packages, ICSP/serial interfaces, PLCC adapters — still out (no RURP support)
- MCU, PLD, logic device types — still out
- Any protocol outside minipro's DIP parallel memory types — still out
- GUI or web interface — still out
- 6.5V VCC NMOS programming — still out (RURP fixed 5V VCC; CMOS variants cover in-scope chips)
- Binary wire format replacing JSON — still out (per-operation overhead trivial)
- Full-image CRC32 — still out (per-chunk XOR sufficient over local USB serial)

## Approach (as built)

- **Database layer:** `build_db.py` (formerly `parse_db_2.py`) is the canonical
  pipeline; fetches `infoic.xml` from upstream minipro at runtime; outputs
  `algorithm` integer via direct `protocol_id` mapping with one documented
  override (Phase 13 WARNING-5: DIP28_2764 + 0x07 + Flash/EEPROM → 0x0D)
- **Wire protocol:** `algorithm` integer added to JSON command alongside
  `type` (semantically primary; type retained as fallback for user-override
  entries that pre-date the algorithm field)
- **Firmware:** `memory.cpp::configure_memory` dispatches a protocol-prefix
  `if-return` block for every `KNOWN_PROTOCOLS` entry; legacy mem_type chain
  preserved only as the last fallback
- **Pinouts:** `pinouts.json` is the physical layer; `static-high-pins` →
  `static_high_mask` end-to-end for tied-high pins (no firmware hardcodes)

## Key Decisions

| Date       | Decision                                                                                                                                                                                                                                   | Outcome  |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------- |
| 2026-05-08 | Database source = minipro `infoic.xml` via `build_db.py` (not hand-curated)                                                                                                                                                                | ✓ Good   |
| 2026-05-08 | Wire protocol = new explicit `algorithm` integer; `type` retained as legacy fallback                                                                                                                                                       | ✓ Good   |
| 2026-05-08 | Firmware dispatch = protocol-prefix `if-return` block per KNOWN_PROTOCOLS, mem_type chain only for legacy entries                                                                                                                          | ✓ Good   |
| 2026-05-08 | Packages in scope = DIP 24, 28, 32 only                                                                                                                                                                                                    | ✓ Good   |
| 2026-05-08 | Hardware = RURP shield, fixed 5V VCC, 19-bit address bus (512KB max), 8-bit data                                                                                                                                                           | ✓ Good   |
| 2026-05-11 | Phase 12: BLOCKER-1 + BLOCKER-2 closed at three layers (firmware dispatch + Python `_ALGO_MEM_TYPE` table + `build_db.py` SRAM tagging) rather than a single point-fix                                                                     | ✓ Good   |
| 2026-05-11 | Phase 13: WARNING-5 fixed at data layer (inline override in `build_db.py`) instead of firmware switch — preserves "algorithm is authoritative" contract while routing around upstream minipro classification error for 23 5V EEPROMs      | ✓ Good   |
| 2026-05-11 | Wire JSON `"vpp"` key carries millivolts (was volts) — name overloaded                                                                                                                                                                     | ✓ Resolved (Phase 2 WIRE-01) |
| 2026-05-11 | Phases 01-10 ship without formal `VERIFICATION.md` files (independent verification via INTEGRATION-CHECK + Phase 12 regression scan)                                                                                                       | ⚠ Revisit (retro `/gsd-validate-phase` runs in v1.1) |
| 2026-05-11 | Intel-flash write path ships without pre-pulse VPP ADC compare (REQ-SAF-01 partial — 39 chips affected)                                                                                                                                     | ✓ Resolved (Phase 1 SAF-04) |
| 2026-05-12 | Phase 1 closes SAF-04 (Intel-flash pre-pulse VPP ADC compare) + SAF-05 (AT28C A9-12V chip-id forward-compat) + SAF-06 (Unity coverage on `[env:native]`). Code review surfaced and fixed a regulator-leak regression on the VPP error path. | ✓ Good   |
| 2026-05-12 | Phase 2 closes WIRE-01 (atomic `"vpp"`→`"vpp_mv"` wire-key flip), CLEAN-01 (`minipro_complete_db.json`→`chip_database.json` rename + D-04 internal `vpp_volts` rename), CLEAN-02 (minipro attribution scrub: 6→1 host, 2→0 firmware), WIRE-02 (`check_dispatch.py` per-chip wire round-trip: 743/743 PASS). Layered `vpp` semantics: wire=`vpp_mv`(mV int), internal=`vpp_volts`(V float), upstream-schema READ preserved per D-08-compat. Phase 11 packaging-metadata drift also fixed (`pyproject.toml`/`MANIFEST.in` aligned to actual shipping files). | ✓ Good   |
| 2026-05-18 | v1.1 paused at 80% (Phase 4 hardware-validation in progress, FM1608 byte-0 bug parked) to start v1.2 immediately — Leonardo flash at 98.7% is blocking further firmware iteration, so logging rework jumps the queue. | ✓ Good (decision validated by v1.2 ship at 85.4% Leonardo Flash on 2026-05-19; 3,792 B headroom restored) |
| 2026-05-18 | v1.2 wire-format design: 1-byte message IDs + raw parameter byte arrays; catalog declares per-ID parameter shape (e.g. `[u16, u24]`). Firmware/host catalogs both codegenerated from a single canonical source. Generated files committed; CI runs `<regen> && git diff --exit-code` as drift gate. Lockstep upgrade — no backward compat to text-format firmware. | ✓ Good (shipped v1.2 with 60 catalog entries + 41 DBG sub_ids; CI drift gate caught zero violations; lockstep upgrade via 3.0.0-dev FW major bump works cleanly) |
| 2026-05-19 | Post-Phase-9 polish: dropped `MSG_OK_FW_HANDSHAKE` per-command composite (P-04) in favour of plain `MSG_OK_READY` ack + 4 single-purpose INFO emits (FW/HW/PHYSICAL_HW/CMD) for verbose mode. Migrated `EXTRA_INFO_LOGGING` build-flag block to SERIAL_DEBUG-gated `DBG_*` sub_ids so verbose diagnostics ride the existing DEBUG channel. | ✓ Good (cleaner verbose-mode story; production wire-byte savings; bench-verified end-to-end) |
| 2026-05-19 | v1.2 milestone closed with 4 hardware-pending UAT items deferred (Phase 8 SC#2/SC#3 + Phase 9 Plan 05 Task 3 chip-seated W27C512 UAT + v1.1 fm1608 debug carry-forward). LMIG-04 acceptance number already pinned via autonomous-side Phase 9 measurement; deferred items don't gate v1.2 ship. | ✓ Good (clean decision rationale; bundles for next bench session) |
| 2026-05-20 | v1.4 trigger model = branch-driven beta (push to `beta` triggers pre-release pipeline; push to `main` triggers stable pipeline). One trigger pattern across both pipelines; no tag-driven path. | ✓ Good (operator picks the branch, not a tag; mirrors current stable trigger shape exactly) |
| 2026-05-20 | v1.4 app channel = PEP 440 pre-release versions (`X.Y.ZbN`/`X.Y.ZrcN`) on the SAME PyPI index. TestPyPI explicitly deferred. Users opt in via `pip install --pre firestarter`. | ✓ Good (single source of truth; stable users unaffected; b3 published cleanly during E2E) |
| 2026-05-20 | v1.4 firmware channel = GitHub Pre-release with `prerelease: true` AND `make_latest: false`. `/releases/latest` API auto-filters pre-releases — preserves stable-installed `firestarter fw -i` (INST-01) without client-side logic. | ✓ Good (INST-01 non-regression proven by API filtering during 3.0.0b3 E2E; stable channel still pulls 2.0.7 verbatim) |
| 2026-05-20 | v1.4 lockstep mechanism = manually-paired beta-branch push with explicit `BETA_VERSION` input. Rejected alternatives: shared meta-repo VERSION file (cross-repo write coupling), cross-repo `repository_dispatch` (requires PAT with `repo` scope across both repos). | ✓ Good (no new cross-repo trust surface; operator-readable; lockstep-dryrun-fixture.sh proves byte-identity at 3.0.0b3) |
| 2026-05-20 | v1.4 scope amendment (after Phase 15 shipped): allow narrow CLI carve-out in app (Phase 18 INST-01..04) — `--pre`, `--firmware-version`, `firmware list` flags + PEP 440 comparator fix. Without these the published beta firmware would be uninstallable via the CLI. | ✓ Good (real-hardware flash from PyPI `--pre` install on Uno + Leonardo proven 2026-05-20 — half a feature without it) |
| 2026-05-20 | v1.4 close at b3 not b1: live cut surfaced 6 substrate defects (E2E-01..06) fixed in-place. Plus .pyc hygiene fix on top. Three sequential cuts (b1 → b2 → b3) instead of one — auto-increment validated as a side-effect. | ✓ Good (substrate hardened for future beta cuts; next cut should land clean) |
| 2026-05-20 | v1.4 ships unconventional default-branch fallout: meta-repo's de-facto main (`init/project-setup`) renamed to `main` at milestone close; 345 commits fast-forwarded; stale feature branches deleted. | ✓ Good (conventional repo state; no workflow references to old name; GitHub branch-rename redirects active for ~90d) |
| 2026-06-01 | v1.9 PAUSED at Phase 44; v1.10 Serial Transport Hardening (COBS) inserted ahead of it. Rationale: make the serial transport provably byte-exact FIRST so it is ruled out as a read-bug confounder before the per-shield RCA (Phase 45+) resumes. v1.9 phase dirs (44, 48) preserved; phases 45–48 reserved; v1.10 numbers from Phase 49. | ✓ Good (v1.10 shipped 2026-06-07; transport exonerated as a variable; v1.9 resumes at Phase 45) |
| 2026-06-01 | v1.10 branch model = **stacked** off the `v1.9-read-bug-rca` tip in all 3 repos, NOT the convention's off-`main`/`beta`. `main`/`beta` are stale at the v1.8 close and lack the COBS ADOPT decision + Phase 44 read-timing knobs that v1.10 depends on; the dependency is v1.9-substrate → v1.10 → resumed-v1.9. Tradeoff accepted: merging v1.10 first also carries v1.9's unmerged commits forward. | ✓ Good (shipped on the stacked branch; merge-forward tradeoff stands for the v1.9 promotion) |
| 2026-06-01 | v1.10 keeps CRC8-CCITT (poly 0x07) intact (D-05) and is bound by the Uno-fit filter (D-04: streaming encode only, no second ~512 B buffer, ~545 B free-RAM ceiling). Framing mechanism (streaming COBS `0x00` vs SLIP `0xC0`) deferred to plan-phase research per COBS-DECISION §2.0; SLIP sidesteps the SERIAL_ON_IO `0x00` bus-aliasing concern (Open Q2/Q3). | ✓ Good (COBS `0x00` chosen Phase 49; CRC8 retained; Uno held 504 B free at v1.10 close) |
| 2026-06-01 | Phase 49: COBS `0x00` selected over SLIP `0xC0` as the framing mechanism — SAFE-01 static proof conclusive (host cannot emit a `0x00` frame-boundary byte during the mode-transition window); scored 4-criterion matrix 11/12 vs 10/12. `len_u16` length prefix + XOR checksum dropped from the data-block frame. | ✓ Good (shipped; resync proven on hardware Phase 53) |
| 2026-06-02 | Phase 51: command-channel JSON migrated into COBS+CRC8 framing as a breaking lockstep wire change — no mixed-version interop; CRC8 verified before `parse_json()`. Decoder cap lowered to `DATA_BUFFER_SIZE-1` (CR-01 OOB write) + `millis()`-bounded inter-byte deadline (CR-02 hang) hardened the receive path. | ✓ Good (documented in both sub-repo READMEs; 36/36 native green) |
| 2026-06-05 | Phase 53 byte-exact proof accepted in **self-consistency** form (D-05): no chip on the bench was the original `19710f6e` GATE-1.8d baseline, so N=5 self-identity (rather than baseline-reproduction) is the operator-accepted achieved form; recorded explicitly in the SHA files + SUMMARY. uno328pb instability persisting on the hardened transport recorded as transport-**exoneration**, NOT a hardware fix. | ✓ Good (operator-authorized override; RCA cleanly deferred to v1.9 Phase 45+) |
| 2026-06-08 | v1.11 re-scoped HOST-ONLY after source-grounded research overturned the "expand types + add firmware handlers" framing: the hardware-feasible memory set is already covered; only ~9 24-pin EEPROMs are a genuine gap, unblockable host-only. No new firmware handlers. | ✓ Good (15/15 shipped host-only; firmware untouched like v1.8) |
| 2026-06-08 | v1.11 GATE-01 deviation (D-01/D-02): keep `build_db.py` fetching `infoic.xml` from upstream master rather than pinning an in-repo snapshot; the regression anchor is the committed `chip_database.baseline.json` that GATE-02 `diff_db.py` diffs against. | ✓ Good (regression purpose met; verified Phase 56 8/8; locked twice by operator before planning) |
| 2026-06-08 | v1.11 GATE-03 keyed on `electrical.type` (5V-EEPROM family) rather than algorithm-in-{0x05,0x06,0x0D} (CR-01): the algorithm predicate was dead code since `dispatch()` never routes those to `configure_eprom`; the type-keyed guard is a genuine superset of WARNING-5. | ✓ Good (0 violations across 743 chips; structural + type-keyed dual guard) |
| 2026-06-09 | v1.11 Phase 58: deleted the survey-built `PIN_MAP_*`/`DIP28_VARIANT_MAP` guess tables; `resolve_pinout_key` rebuilt as a pure function of `(pin_count, proto_id, mem_size)` with the 3 load-bearing safety overrides (WARNING-5, fm1608, 24-pin EEPROM skip) preserved as explicit rules. | ✓ Good (30 RED→GREEN Wave-0 tests; GATE-03 0 violations; SR-1 two-layer review) |
| 2026-06-10 | v1.11 Phases 60/61 (display-layer): `info` + `list`/`search` derive Type/erasability/VPP from `electrical.type` via a single shared `resolve_type_label` helper (D-04), not `protocol_id` — resolving the EEPROM-vs-UV-EPROM mislabel and the spurious SRAM VPP. Post-close: SRAM/FRAM `vcc`→`vdd` (5V) normalization in `build_db.py`. | ✓ Good (operator-driven; FM1608 shows SRAM/5.0v/`-`; W27C512 shows EEPROM; 559 tests green) |
| 2026-06-11 | v1.12 firmware fail-closed dispatch: a `protocol != 0` guard in `configure_memory()` routes every non-zero unimplemented protocol to `configure_not_implemented()` (NULL op pointers, no VPP enable) emitting `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED = 0xBB`; the legacy `mem_type` fallback is preserved ONLY behind `protocol == 0`. New 0xBB message added lockstep via `messages.toml` codegen (py3.11). | ✓ Good (49/49 native tests; Uno 72.4% flash; closes the silent 12V-VPP hazard; host raises typed `ProtocolNotImplementedError`) |
| 2026-06-12 | v1.12 capability-honest DB: chips RURP can't fully support are *listed* with a `support_status` taxonomy (`protocol-not-implemented`/`adapter-required`/`vpp-exceeds-max`) instead of silently dropped; `NON_DISPATCHABLE_ALGO = 0x00` makes them ERROR at the data layer (CR-01/Option A). | ✓ Good (DB 744; gate green) |
| 2026-06-12 | v1.12 authoritative 12V-VPP-hazard closure = **host guard** (D-12, Phase 66-05): `ChipNotImplementedError` in `chip_resolver.resolve_chip` refuses every non-`supported` chip before any wire dict / serial byte. The `check_dispatch.py` `non_supported_dispatchable` gate detector is hollow (declared, asserted-empty, never populated). | ⚠ Revisit (accepted tech debt 2026-06-16 — host guard is authoritative, no live hazard; optional future: actually populate the gate detector) |
| 2026-06-15 | v1.12 DB-02/DB-04 gaps (first audit `gaps_found`) closed by a single inserted **Phase 67.1** consolidating the never-executed Phases 67 & 68 — DB `unsupported_reason` string is the single source of truth, rendered verbatim by both `info` display and chip-op refusal (Approach A). | ✓ Good (verified PASSED 9/9; SECURED) |
| 2026-06-16 | v1.12 → beta = **integration (re-port), not conflict-merge** (Phase 70): v1.12 was forked off the pre-v1.11 beta, so its DB pipeline collided with v1.11's Phase 58 `resolve_pinout_key` rewrite. Re-expressed v1.12's `support_status`/VPP-safety features on top of `resolve_pinout_key`, regenerated `chip_database.json` (never hand-merged), merged both sub-repos to `beta` lockstep (no tag). | ✓ Good (verified 6/6 SC; v1.11 decode-correctness preserved; firmware fast-forward `b71c6fd`) |
| 2026-06-18 | v1.13 validation harness is **software-first / flash-free**: 3 tiers (native recording-stub + host wire round-trip + `dev validate-family` HIL) + a declarative matrix carry a non-vacuous PASS oracle (Leonardo-only-PASS, negative control, live-R1, uno328pb-N/A), and populate the v1.12 hollow `non_supported_dispatchable` GATE-03 detector. | ✓ Good (closed v1.12 tech debt; 6 families Tier-1/2 GREEN; W27C512 Tier-3 authoritative PASS) |
| 2026-06-18 | v1.13 **evidence defines "missing"**: a bench-FAIL on W29C040 drove the only real firmware fix (flash4 SDP-unlock + data-driven page write + `CMD_CHECK_CHIP_ID`); the SRAM no-op suspicion was DISPROVEN by VAL-06 (FIX-01 closed not-needed); spec-only gaps (AT28C04/16 adapter arm + X88C64 0x34 verdict) graduated NO chip to `supported`. | ✓ Good (Leonardo flash held 89.5%; erase / X88C64 / adapter graduation deferred to v1.14) |
| 2026-06-22 | v1.14 Phase 77 `FLAG_CAN_ERASE` derived from canonical `electrical.type == "EEPROM"` (not the always-zero `info-flags & 0x10`); zero-behavioral-delta canonicality, locked by 3 wire-level tests; establishes the SAFE-01/02/03 guard-removal-last graduation discipline. | ✓ Good (first hardware graduation since v1.0; W27C512 write→auto-erase→program→verify bench-proven on Leonardo, SHA match) |
| 2026-06-22 | v1.14 **no blind handlers / honest hardware deferrals**: Phase 78 (X88C64 ALE PCB-BLOCKED) and Phase 80 (AT28C04/16 adapter not built) closed as clean zero-code deferrals rather than forcing unverifiable graduations; FUT-01/04 tracked. | ✓ Good (chips stay honestly refused; verified 7/7 Phase 78; zero-change Phase 80) |
| 2026-06-23 | v1.14 **D-07 operator override** (Phase 79): the ≥25V NMOS pre-gate (NMOS-01) RETIRED — the bench tops out at ~22.4V VPE (~90% of 25V); graduate the 4 NMOS chips **best-effort** with no hardware change ever (ceiling 22000→25000, DB regen → `supported` 0x0B). Chips program on the 0x0B direct-VPE rail where firmware warns-and-proceeds on under-voltage; over-voltage stays blocked. | ◑ Best-effort (definitive bench SHA-match FUT-03, no NMOS chip on hand; user opts in) |
| 2026-06-24 | v1.15 **silicon validates the algorithm-first contract** (Phases 81–83): exercised all 11 physical chips on Leonardo + Rev 2.0, recording a per-chip `EVIDENCE.{md,json}` record + consolidated `DECODE-AUDIT.md`. DB decode matched silicon for every chip; W29C020 gave the first Flash/EEPROM auto-erase silicon proof. Genuine FAILs (stuck-bit wear, flash4 page fault, 0x08 write) are silicon/write-path defects, not DB/algo faults — recorded honestly, not papered over. | ✓ Good (on-paper `supported` claim proven on real silicon for the operator's inventory) |
| 2026-06-25 | v1.15 **2516 graduated via user-override, not upstream** (Phase 81): the Intel 2516 is genuinely absent from minipro `infoic.xml` (the 28 "2516" hits are SPI `25160` parts), so it was hand-authored into `~/.firestarter/database.json` (0x0B / DIP24_2716 / UV-EPROM / 25000mV / 2048B) behind a full SR-1 datasheet safety review + operator blocking sign-off (user-override bypasses `check_dispatch.py`/`diff_db.py`). | ◑ Best-effort (info/read decode correct; 0x0B read path unstable on this bench → write proof deferred FUT-03/GRAD-03; promote upstream only if it appears in minipro → FUT-B) |
| 2026-06-25 | v1.15 **FIX-01 closed-by-disposition** (Phase 84, D-43): fix where in-posture, RCA + name-track where not. In-posture fixes shipped + bench-confirmed — firmware VPP-skip on CMD_READ/CMD_BLANK_CHECK (clears 18.8V read boot-refusal), host SRAM/FRAM blank-check short-circuit (kills 0xA4), FM1608 SRAM→FRAM relabel. Deeper write-path defects deterministic + not trivially fixable → named trackers (AM27C020 0x08 → FUT-06; W29C040 flash4 → CR-01/Phase-74 Wave-2). | ✓ Good (operator-accepted; full-DB VPP-safety + diff_db + host suite + native all green; Phase 84 SECURED) |

## Context

- **Tech stack:** Python 3 CLI host (pip package `firestarter`, JSON-over-serial
  at 250000 baud) + Arduino C++ firmware (PlatformIO, targets `uno` + `leonardo`,
  RURP shield)
- **Repo structure:** Meta-repo + 2 sub-repos (`firestarter/` firmware,
  `firestarter_app/` Python). Meta-repo tracks `.planning/` and `.claude/` only;
  sub-repos are pointer-bumped commits
- **Database state:** **744 chips (count unchanged since v1.12)** across DIP24/28/32 (was 734 at v1.0;
  +9 from the 24-pin AT28C04/16 EEPROM unblock in Phase 58 (v1.11); +1 net in v1.12 from
  capability-honest inclusion of previously-dropped unknown-protocol DIP chips). **v1.14 graduated 4 NMOS
  UV-EPROMs** (INTEL M2716, INTEL 2732/M2732, SGS-THOMSON ETC2716, ST ETC2716) from `vpp-exceeds-max` →
  `supported` (best-effort, VPP ceiling raised 22000→25000) and **the 7–8 0x07 EE-EPROMs now auto-erase**
  before write (`FLAG_CAN_ERASE` from `electrical.type`) — no DB count change, support_status reclassification.
  Every chip carries a `support_status` (`supported` / `protocol-not-implemented` / `adapter-required`
  / `vpp-exceeds-max`); non-`supported` chips (X88C64 protocol-not-implemented; 9 AT28C04/16 adapter-required)
  are listed-and-reported-honestly, refused in-host before any serial byte, never made programmable. Decode re-derived from minipro source in
  v1.11: corrected VCC nibbles (4V/4.5V), vcc/vdd labels, `interpret_timing` (µs not ×100),
  canonical `PROTOCOL_MAP`; SRAM/FRAM Vcc normalized to supply rail; true NMOS VPP recorded in
  v1.12. `electrical.type` is the display ground truth (`info`/`list`/`search`). **v1.15 bench-validated 11
  of these chips on real silicon** (Leonardo + Rev 2.0) — confirming DB decode vs silicon per chip and
  adding the `2516` as a hand-authored user-override entry (genuinely absent from minipro); FM1608
  relabeled SRAM→FRAM at the `build_db.py` codegen layer. DB count unchanged (the 2516 lives in
  `~/.firestarter/database.json`, not the built-in set).
- **Verified families (structural):** UV-EPROM (W27C512), Flash AMD (29F040),
  Flash Intel (28F010 minus VPP-ADC gap), EEPROM (AT28C256 via Phase 13
  override), SRAM (6116-class via safe stub)
- **Known gaps for v1.1:** see `.planning/MILESTONES.md` "Known Gaps" section
  (Intel-flash VPP ADC, retroactive VERIFICATION.md for phases 01-10, WARNING-2
  forward-compat, WARNING-3 wire-key naming, WARNING-4 test-script drift)

## Constraints

- Arduino Uno: 512-byte serial data buffer (affects chunked transfer sizing in `eprom_operations.py`)
- Arduino Leonardo: 1024-byte buffer
- Hardware calibration (R1/R2, board revision) persisted in EEPROM via `rurp_configuration_t`
- Constants/flag bits duplicated between `firestarter_app/firestarter/constants.py` and `firestarter/include/firestarter.h` — must change together

## Sub-Repos

- `firestarter_app/` — Python host CLI, database pipeline, serial protocol
- `firestarter/` — Arduino firmware, algorithm implementations

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---

*Last updated: 2026-06-25 — v1.16 (Protocol-First Architecture Rebuild) STARTED. Re-organize how Firestarter models/names/validates EPROM/Flash/SRAM programming protocols: rename + datasheet-document today's inherited minipro hex-ID buckets (0x05/0x06/0x07/0x08/0x0B/0x40/0x34/…) into a named protocol vocabulary, THEN re-decompose handlers into shared primitives (address setup, data strobe, poll/verify, VPP gate, page buffer, SDP unlock, chip-id) to shrink the ~89.5% Leonardo flash ceiling, with a per-protocol bench ledger (PASS on Leonardo + RURP Rev 2.0 / explicit `UNVERIFIED`). Minipro DB stays ground truth; datasheets only verify + document the *why*. Staged: datasheets/ acquisition → naming/docs → primitive refactor → per-protocol bench validation. Dual-repo lockstep (`constants.py` ↔ `firestarter.h`); reuse-first; py3.12-masks-CI-3.11 trap watch. Phase numbering continues at Phase 85; promoted from the `/gsd-explore` 2026-06-25 seed per operator instruction. Prior footer (v1.15 close) retained below.*

*Last updated: 2026-06-25 — v1.15 (Bench Validation of Operator Inventory) SHIPPED. 4 phases (81–84), 15 plans; 23 reqs (21 satisfied · GRAD-03 deferred best-effort D-22 · FIX-01 closed-by-disposition D-43). Bench-validated 11 physical chips across 5 algorithm families on Leonardo + RURP Rev 2.0 via full write→read→verify, with a per-chip `EVIDENCE.{md,json}` record + consolidated `DECODE-AUDIT.md`. First Flash/EEPROM auto-erase silicon proof (W29C020); 2516 graduated via a datasheet-grounded user-override entry. In-posture FIX-01 fixes shipped (firmware VPP-skip on read/blank-check + host SRAM/FRAM blank-check short-circuit + FM1608 SRAM→FRAM relabel); deeper write-path defects RCA'd + named-tracked (AM27C020 0x08 → FUT-06; W29C040 flash4 → CR-01/Phase-74 Wave-2; 2516 0x0B read → FUT-03). Genuine silicon FAILs (W27E512/W27E040 stuck bits) recorded honestly, not DB/algo faults. Milestone audit `gaps_found` stale (pre-Phase-84); both gaps closed-by-disposition + operator-accepted. One firmware delta (VPP-skip, fw `cb947c7`); host `4d5b3de`. Meta tagged `v1.15`, gsd planning merged to `beta`; lockstep beta cut `3.0.0b11` + gitlink bump operator-gated (gitlinks PINNED). 12 open artifact items acknowledged at close (pre-existing carry-forwards + intentional v1.15 deferrals). Next: `/gsd-new-milestone` (v1.16 protocol-first architecture rebuild seed captured). Prior footer (v1.15 start) retained below.*

*Last updated: 2026-06-23 — v1.15 (Bench Validation of Operator Inventory) STARTED. Bench-validate 11 physical chips (5 algorithm families) on Leonardo + RURP Rev 2.0 via full write→read→verify: prove the on-paper `supported` claim on real silicon, RCA/fix any failures, validate DB decode correctness, and graduate the one genuine gap (the `2516`, confirmed absent from minipro `infoic.xml` — needs a datasheet-grounded entry + bench proof, doubling as deferred FUT-03 NMOS evidence). UV-EPROMs (M27C512/AM27C020/2516) get a no-eraser protocol: non-destructive read+blank-check first, spend-vs-preserve decided per-chip at the bench. Mostly host-side; firmware untouched unless a bench defect forces a lockstep fix. Phase numbering continues at Phase 81; branch off `beta`. Prior footer (v1.14 close) retained below.*

*Last updated: 2026-06-23 — v1.14 (Feasible-Gap Implementation) SHIPPED. 4 phases (77–80), 9 executed plans of 13 (4 deferred hardware-gated), host-only delta (firmware untouched on `beta`). The first milestone since v1.0 to graduate chips to `supported`: erase write-path (Phase 77 ✅ bench-proven W27C512, first hardware graduation) + 25V NMOS best-effort (Phase 79 ✅ 4 chips, D-07 override, no HW change). X88C64 (Phase 78, ALE PCB-BLOCKED → FUT-01) + AT28C04/16 adapter (Phase 80, adapter-not-built → FUT-04) cleanly deferred. 15 reqs: 6 verified · 2 software-complete · 7 hardware-gated deferrals (FUT-01/03/04). Audit `gaps_found` but all gaps intentional/operator-authorized; integration PASS (744-chip gate 0 violations, 650 tests, parity 8/8). Meta tagged `v1.14`, gsd planning merged to `beta`; lockstep beta cut `3.0.0b11` + gitlink bump operator-gated (gitlinks PINNED). Next: `/gsd-new-milestone`. Prior footer (v1.14 start) retained below.*

*Last updated: 2026-06-18 — v1.14 (Feasible-Gap Implementation) STARTED. Graduate chips to `supported` by implementing the four evidence-surfaced RURP-feasible gaps v1.13 scoped out (validation-only): 999.4 erase write-path (skipped Phase 75 / ERASE-01), 999.5 X88C64 0x34 handler, 999.7 25V NMOS ceiling raise, 999.6 AT28C04/16 adapter graduation. Suggested order 999.4 → 999.5 → 999.7 → 999.6 (hardware-blocked last). First chips newly programmable since v1.0. Firmware-touching, dual-repo lockstep off `beta`; flash-budget ordering applies. Phase numbering continues at Phase 77. Operator decision 2026-06-18: do all four; 25V NMOS assuming HW can produce 25V. Prior footer (v1.13 close) retained below.*

*Last updated: 2026-06-18 — v1.13 (Programming Algorithm Validation + Gap Implementation) SHIPPED. 5 delivering phases (71–74, 76), 19 plans, 17/17 requirements; first firmware-touching milestone since v1.12. Software-first three-tier validation harness + per-family matrix proving the 6 write/program families (PARTIAL bench coverage, Leonardo Tier-3); evidence-driven feasible-gap subset (flash4 chip-id + W29C040 SDP/page-write; spec-only AT28C04/16 adapter arm + DIP24→DIP32 spec; X88C64 0x34 MEDIUM verdict, no handler). No chip graduated to `supported`. Dual-repo lockstep merged to `beta` (fw `a33513f` / app `34deccb` @ `3.0.0b9`, no tag); beta cut + stable promotion operator-gated. Phase 75 (erase) + Phase 74 Wave-2 (HW re-bench) deferred to v1.14 (Backlog 999.4–999.7). 9 deferred items acknowledged at close (pre-existing/accepted tech debt). Next: `/gsd-new-milestone v1.14`. Prior footer (v1.13 start) retained below.*

*Last updated: 2026-06-16 — v1.13 (Programming Algorithm Validation + Gap Implementation) STARTED. Test-first validation of the 6 implemented write/program algorithm families on hardware (harness + matrix software-first, hybrid bench gating, Leonardo as verify board), re-research the protocol landscape, then implement evidence-driven gaps (per-family correctness fixes + adapter-required chips). First firmware-touching milestone since v1.12; dual-repo lockstep off `beta`. v1.9 read-bug RCA stays separate. Phase numbering continues at Phase 71. Prior footer (v1.12 close) retained below.*

*Last updated: 2026-06-16 — v1.12 (Firmware Protocol Dispatch Hardening + Skeletons) SHIPPED. 8 delivering phases (62, 63, 64, 65, 66, 67.1, 69, 70), 22 plans, 17/17 requirements; first firmware-touching milestone since v1.10. Fail-closed dispatch (0xBB) + host `ProtocolNotImplementedError` + capability-honest DB (`support_status` taxonomy, in-host refusal); no new chip programmable; DB 743 → 744. Dual-repo lockstep merged to `beta` (fw `b71c6fd` / app `6b5480f`, no tag); lockstep beta cut + stable promotion operator-gated. Accepted tech debt: hollow GATE-03 detector (host guard authoritative) + Nyquist gaps on 6/8 phases. Next: `/gsd-new-milestone` (or resume the deferred v1.9 read-bug RCA at Phase 45). Prior footer (v1.12 start) retained below.*

*Last updated: 2026-06-10 — v1.12 (Firmware Protocol Dispatch Hardening + Skeletons) STARTED. First firmware-touching milestone since v1.10; fail-closed dispatch + not-implemented wire response + skeleton handlers for missing protocols; dual-repo lockstep, unified-beta branch model (all 3 repos off `beta`). Prior footer (v1.11 close) retained below.*

*Previously: 2026-06-10 — after v1.11 (Complete infoic.xml Decode & Database Correctness) close. Shipped 6 phases (56–61), 14 plans, 15/15 requirements, HOST-ONLY (firmware untouched like v1.8). Audit PASSED (15/15 reqs, 5/5 E2E flows, both correctness gates green on 743 chips, 559 tests). Meta tagged `v1.11`; lockstep beta cut `3.0.0b9` (firestarter_app version bump + gitlink bump + PyPI/GitHub pre-release) is operator-gated and pending. Stable promotion deferred per the operator-gated release rule. Deferred v1.9 read-bug RCA resumes at `/gsd-plan-phase 45`. Prior footer retained below.*

*Previously: 2026-06-08 — after v1.10 (Serial Transport Hardening / COBS) close + beta merge. Shipped 7 phases (49–55), 27 plans, 14/14 requirements: streaming COBS `0x00` + CRC8 framing with automatic resync on both the data-block path and the host→fw JSON command channel; 2 s timeout cascade removed; byte-exact proven on operator-witnessed bench (Uno + Leonardo); uno328pb instability transport-exonerated. Merged to beta in all 3 repos locally 2026-06-08 (fw beta@0266ee2, app beta@8480ff3, meta main@ec90b92) — not yet pushed; operator cuts the beta when ready (lockstep `BETA_VERSION=3.0.0b8`, explicit pin). Beta-only — stable `3.0.1` operator-gated. **v1.9 Read-Bug RCA DEFERRED** (operator 2026-06-08); resumes later at Phase 45.*
