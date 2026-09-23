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

**v1.17 shipped:** 2026-06-29 (Implement & Test the W29C040 Programming Protocol — 2 of 4 phases executed (93 RCA, 94 FIX+PGSZ), 8 plans; 11/16 reqs satisfied. RCA proved the page-0 "fault" is the seated chip's permanently-locked §6.6 boot block (NOT a firmware bug); shipped the T-93-CANERASE 12V-on-5V safety fix + proactive §6.6 lockout detection + datasheet-sourced per-chip `page_size` (CR-01) + writable-region N=3 SHA proof. W29C040 byte-exact graduation + LEDGER deferred → FUT-07 (needs a different unlocked sample, third-party bench). Meta merged to `beta` (`1f5c17a`), no tag, gitlinks left at v1.17 sub-repo HEADs per operator. See `.planning/MILESTONES.md` §v1.17.)

**v1.18 shipped:** 2026-07-01 (AM27C020 0x08 Write-Path RCA & Fix — 3 phases (97–99), 12 plans; 11/11 requirements; firmware-touching, dual-repo lockstep. Root-caused the 0-bits fault (RC-1: DIP32 pin 31 modeled as address line A18, not held /PGM); shipped a scoped `DIP32_27C020` + `rw-pin:[31]` → `CTRL_READ_WRITE` (0x40) fix — revision-invariant, distinct from the `0x08` VPP alias that made the first attempt CR-01 a physical no-op. Bench proved the fix **effective** (write#1 60/64 byte-exact, refuting the 0-bits signature) but **marginal/unreliable** (write#2 0/64) → honest **DEFER**; AM27C020 carried as **FUT-08** (FUT-06 retired-by-replacement). Audit `tech_debt` (3/3 phases passed, integration 6/6 WIRED). Meta tagged `v1.18` + gsd planning merged to `beta`; lockstep beta cut + gitlink bump operator-gated. See `.planning/MILESTONES.md` §v1.18.)

**v1.16 shipped:** 2026-06-26 (Protocol-First Architecture Rebuild — 8 phases (85–92), 29 plans, 28/28 requirements; host-first, NO dual-repo lockstep. Turned the inherited-from-minipro hex-ID `protocol_id` buckets into a named, datasheet-verified, primitive-decomposed architecture: `infoic.xml` `variant` field decoded in full + `build_db.py` rewritten to a single principled `classify()` (Rule 1/2/3 override stack deleted; FM1608→SRAM_STD/0x28 + X88C64→EEPROM fall out structurally; DB 744→746 with the 2516/2532 non-upstream supplement); top-level `datasheets/` + `firestarter_fw/doc/PROTOCOLS.md` 12-bucket vocabulary + INV-01..09 native-test matrix; primitives P7/P4/P3/P5 extracted behind golden traces + dispatch-mirror guard with a net flash **decrease** (final 25136 B / 87.7% / −518 B); `PROTOCOL-LEDGER.{md,json}` + self-consistency checker (all 4 on-hand protocols PASS, 6 no-silicon buckets explicit UNVERIFIED). The Phase-90/91 "12V-VPP regression" resolved as a `write -b` skipped-erase test-method error (recompose proven innocent), then hardened away in Phase 92 (HARD-01). fw `a296195` / app `883c78f`; meta tagged `v1.16`; lockstep beta cut `3.0.0b11` + gitlink bump operator-gated (gitlinks PINNED at b10). See `.planning/MILESTONES.md` §v1.16.)

**v1.19 shipped:** 2026-07-02 (Protocol Naming Labels — 5 phases (100–104), tagged + merged to beta + pushed. Canonical `PROTO_<NAME>` token + display-name + facet-prose set applied across firmware constants, host display, and docs; a legibility layer on top of the UNCHANGED algorithm-first numeric dispatch (GATE-01/02/03 non-regression). Phase 104 renamed the last minipro-heritage flash handler file-pairs/functions (`flash_type_3/4`→`flash_nor_unlock`/`flash_5v_page`). Sub-repo beta cut + gitlink bump operator-gated (gitlinks PINNED). See `.planning/MILESTONES.md` §v1.19.)

**v1.20 shipped:** 2026-07-02 (Protocol-Only Dispatch — Remove the Legacy `mem_type` Axis — 3 phases (105 FW / 106 HOST / 107 DOCS+GATE), 7 plans, 12/12 v1 requirements; firmware-touching, dual-repo lockstep. Removed the vestigial `mem_type`/`type` backward-compat dispatch axis end to end so firmware, wire, and host trust *only* the real protocol (`algorithm`): firmware deletes the `memory.cpp` fallback chain (`protocol == 0` → `configure_not_implemented()`/0xBB), drops `handle->mem_type` + `type` parsing, retires `0xAE` + `TYPE_*` (Phase 105); host stops emitting `type`, drops `_ALGO_MEM_TYPE` + the "Generic Flash (legacy fallback only)" default + the `mem_type` label fallbacks, adds a fail-closed algorithm-presence guard before any serial byte (Phase 106); docs scrubbed + breaking change recorded in both READMEs, `0xAE` removed from the canonical catalog (incidentally fixing a pre-existing Phase-95 `FL4_BOOT_BLOCK` desync), all GATE-01/02/SAFE-01 gates re-verified green — the removal proven dead code for all 746 chips (Phase 107). Closeout `override_closeout` (14 pre-existing cross-milestone open items acknowledged-deferred; none originate in v1.20). Meta tagged `v1.20` + `gsd/v1.20-…` merged to `beta`, both pushed to origin at close (operator override); gitlinks PINNED at b10 (fw `2d93379` / app `e0bdea4`); lockstep beta cut `3.0.0b11` + gitlink bump operator-gated. LEGACY-01/02 deferred to v2. See `.planning/MILESTONES.md` §v1.20.)

**v1.22 shipped:** 2026-07-30 (AT28C Software Data Protection Lifecycle — 7 phases (116–122), 69 plans, 176 tasks; 41/41 v1 requirements; firmware-touching, dual-repo lockstep; **software-only validation** — no AT28C part in operator inventory. **Opened with a FIX, not a feature:** four convergent research streams falsified the kickoff framing twice, proving the SDP-**disable** sequence that has shipped since v1.0-era Phase 06-01 (and is live in `3.0.0b11`) almost certainly never reached silicon — `flash_util_byte_flipping` → `fu_flash_fast_address` bypassed `mem_util_remap_address_bus` entirely and hard-coded `/WE` for the one pinout every bench-proven chip uses, so on all four `0x0D` pinouts at least one command write was emitted with `/WE` HIGH (a documented Write Inhibit) across all 84 `0x0D` chips, while the `(0x5555, 0x20)` success check was **inverted**, not merely weak. Delivered: the ground-truth trace harness that made every later claim non-hollow (116), a remap-aware `0x0D`-local emitter + honest completion signal + per-page polling corrected from 1-byte-in-64 to full coverage (117 — reclassifying gh#11 as a *conflation* bug), silent auto-unlock made visible and declinable via `FLAG_SKIP_SDP_UNLOCK` `0x100` with measured 572/600 µs timing (118), the previously-missing SDP **lock** half `CMD_SDP_LOCK`/`CMD_SDP_UNLOCK` (119, +392 B against 2992 B headroom) <!-- recordscan:history reason: 2992 B was the pre-Phase-119 Leonardo headroom (28672 - 25680), accurate when this v1.22 archive entry was written and exactly what Phase 119's own +392 B was judged against (R-10; see 130-RESEARCH.md C-7). Historically correct, preserved as a record, not corrected. -->, the host surface `firestarter dev sdp <chip> enable|disable` behind the v1.21 destructiveness gate plus a fail-closed allow-set **derived** from `infoic.xml` `flags` bit 15 at operator directive — ALLOW 43 / REFUSE 41 = 84, zero MIXED (120), the `dev test` erase-fabrication fix + redesign that had to land before the closeout or every community re-test report would have poisoned this milestone's own evidence (121), and the honesty-ledger close (122). Closeout `override_closeout` (14 pre-existing cross-milestone open items acknowledged-deferred; none originate in v1.22). `0x0D` stays `UNVERIFIED` in `PROTOCOL-LEDGER`; zero `support_status` changes; 84-chip count unchanged. Meta tagged `v1.22` + gitlinks bumped off PINNED-at-b11 to the published `3.0.0b14` commits; firmware + app tagged `v1.22` on `beta`; observed cut `3.0.0b14` public on both channels. **No stable release** — PyPI `info.version` stays `2.0.7`. See `.planning/MILESTONES.md` §v1.22.)

**v1.23 shipped:** 2026-08-03 (PY32F071 Integration — 8 phases (123–130), 88 plans, 226 tasks; 47/47 v1 requirements; firmware-touching, dual-repo lockstep; **software-only by physical necessity — no PY32F071 PCB exists**, so nothing here has run on this silicon and nothing in it could. Landed the in-flight PY32F071 firmware port and the host USB-DFU installer onto `beta` as one lockstep integration, plus the release-asset unblock that makes them reachable outside this tree — a **fourth board target beneath** the algorithm-first dispatch contract without disturbing it. Delivered: six fail-provable gates + the BASE-01 flash-**and-RAM** baseline authored before any firmware moved, and the fail-OPEN `_FW_ABSENT` proxy replaced with an un-renameable `../firestarter/.git` key (123); the **atomic** portability+py32 commit-pair — the "HAL prep leads" framing was measured a trap (that half alone takes native from 141 passing to 0 passing / 17 ERRORED) — plus the C-1 CMake rename fix for a tree that merged with *zero conflicts* yet failed at CMake configure, the ARM `push` trigger, and the hollow pin-map guard (`#define`d 1 two lines above its own `#if !… → #error`) made able to fire (124); the hand-authored VPP seam returning `MANUAL_ADJUSTMENT_REQUIRED` on every board at 0 B flash / 0 B RAM, with AVR-class manual control recorded **permanent, not provisional** (125); dual-slot CRC32 flash-persistent config behind a common/per-platform seam with the AVR EEPROM backend proven a pure move, Sector 15 reserved, PR #48's non-persisting `config.cpp` deleted (126); the pure-Python DFU 1.1/DfuSe installer with `DFU_UPLOAD` readback and the 120 KiB envelope, suite 1158 → 1293, and the discovery that `check_mypy_watermark.py` had been **fail-open**, hiding 69 inherited errors (127); the release-asset fold proven on **two real CI dispatches** — one publishing `firestarter_py32f071.hex`, one planting an ARM break and still publishing all three AVR assets, empirically validating `outcome` vs `conclusion` (128); the flash-path decision and PCB record written before any schematic, in two lockstep layers held by a 41-leg cross-repo gate, top-billing **F-10** (a contiguous 8-bit bus is physically impossible on 2 of 7 candidate packages — a part-selection constraint) (129); and the six-tier honesty ledger pairing every permitted claim with its explicit non-claim, all 18 research corrections landed under a label-aware checker (0 unlabeled of 60), and the `beta` push made its own operator-gated decision committed *before* the push (130). Closeout `override_closeout` — Phase 126 `passed-with-findings` + the same 14 carry-forward `audit-open` items, none originating in v1.23. Observed cut tag `3.0.0b15` on both channels, read from `gh release list`; no stable release. See `.planning/MILESTONES.md` §v1.23.)

**v1.21 shipped:** 2026-07-27 (Community Chip-Validation Command — 8 phases (108–115, incl. micro-phase 114.1), 34 plans, 70 tasks; 28/28 v1 requirements. Shipped `firestarter dev test <chip>` — a per-chip technology-aware capability sweep of independent non-fatal steps + address-derived health-write pattern + byte-mismatch fingerprint (108), destructiveness gate / small-region UV write + orchestrator-only SAFE-02 (109), dual-output diagnostic report + provenance + read-only DB-diff (110), measured VPP/VPE sampler (111, hardware-gated), `dev test` CLI wiring (112), tiered `--submit` GitHub flow + PII sanitizer (113), disposition/no-auto-graduate lock + `[dev test]` issue parser + community-validation taxonomy (114) + absent-chip hard-fail (114.1), and the VALIDATION+DOCS close (115, hardware-gated): drove the `3.0.0b11` beta publish on BOTH channels (PyPI `--pre` + GitHub prerelease w/ per-board `.hex`), bench-validated fresh-machine install→flash→smoke on Uno + Leonardo (HARD) + uno328pb (best-effort), authored the community onboarding doc, and bumped the meta gitlinks off PINNED-b10 → b11 (fw `0fd7992` / app `86e4563`). Closeout `override_closeout` (14 pre-existing cross-milestone open items acknowledged-deferred; none originate in v1.21). Remaining operator-gated close step: `v1.21` tag + sub-repo `--no-ff` beta merges + pushes. See `.planning/MILESTONES.md` §v1.21.)

**v1.30 shipped:** 2026-08-05 (SDP Surface Retirement & Behavioral Lock Proof — 7 phases (131–134, 136, 136.1, 137), 48 plans, 125 tasks; **55/56 requirements, CLOSE-06 held open by design**; host-only, no firmware change. Retired v1.22's unverifiable standalone `dev sdp <chip> enable|disable` and moved the proof into a six-step `dev test` leg whose oracle is read-back equality against a baseline pattern, never an exit code; hardened `check_mypy_watermark.py` from fail-open to fail-closed and certified `firestarter_app`'s primary `ci` job GREEN for the first time in two months (run `30856059940`, mypy 32 against an unratcheted watermark of 35); landed gh#8's stable-channel `dev` narrowing. **Phase 135 (`write --sdp-relock`) deferred out to Backlog 999.28** by operator decision, number not reused — so v1.30 ships the deletion and the behavioral proof and **withdraws** the deliberate-protection surface with **no replacement** (RELOCK-01…06 left v1 scope, 56 → 50 reqs; RELOCK-07 re-homed to Phase 137). Evidence ceiling honoured throughout: **no AT28C part in inventory, no hardware ran** — emission, plan-derivation and read-back-comparison logic are proven; the causal claim "the lock inhibited the write" is not, and did not gate the close. Seventh consecutive `override_closeout`. **⚠ `firestarter_app`'s `gsd/v1.30-sdp-surface-retirement` was never merged to `origin/beta`** — the PR was staged but not opened; v1.31 Phase 138 lands it. See `.planning/MILESTONES.md` §v1.30.)

**v1.31 shipped:** 2026-08-18 (27C Programming-Algorithm Fidelity — 9 phases (138–146), 74 plans, 164 tasks; **45/45 v1 requirements**; firmware-touching, dual-repo lockstep. Implements [gh#15](https://github.com/henols/firestarter_prom/issues/15) **as corrected, not as filed** — two wrong numbers and one inverted premise, all three corrected *publicly and before implementation* (comment `#5233463320`): `0x0B`'s pulse is **500 µs**, not `50000 us`; pulse width is a **database datum**, not a per-protocol constant (re-derived live through the production parser — 170/127/32 chips); and the safe 32-bit delay helper is for the overprogram pulse, not any bare pulse. Delivered: **one shared per-byte pulse-to-verify loop** driven by a `const` PROGMEM `eprom_params_t` table keyed on `protocol_id` (**D-01** — protocol owns *shape*, the database owns the *pulse*), **not** gh#15's three state machines; fixed-width pulses that never grow between attempts; hard-fail at `max_pulses` reporting the failing **address and pulse count**; one shared `eprom_hv_route_mask()` with every **error** exit disabling every HV route through a single-exit wrapper; `write --pulse-us N` bounded 1..65535 and pre-validated before a serial byte, riding the existing wire field with **no new DB field and no second algorithm selector**; plus a host long-write timeout fix and intra-block progress, scoped to the `leonardo` class only — on `SERIAL_ON_IO` boards the emission is compiled out **structurally**, because a buffered progress frame there could displace a later `MSG_ERR_MAX_PULSES` and convert a program failure into a transport timeout. **Bench-validated on real silicon:** three full 65536-byte write→read→verify cycles on a Winbond **W27C512** (`0xda08`), **Leonardo**, shield **Rev 2.0** — three distinct images, nine clean oracle cells, read stability N=3 at one SHA each, write timing consistent to **0.37 s**. A firmware defect this milestone itself introduced (Phase 141 deleted the only `CTRL_VPE_ENABLE` assert) failed the **first** bench cycle on byte 0; it was root-caused by a debug session, fixed, and **stands in the record with its cause** rather than being counted out. **Evidence Ceiling stands: the ~6.25 V program-VCC rail all four vendor algorithms assume is unreachable on every shield revision this project owns** — so this milestone claims **fidelity, not improvement**, with no comparative claim, no control run, and no datasheet-conformance claim in either direction. `0x08` (AM27C020) and `0x0B` (M2716/M2732) are **skipped-with-reason** with the missing parts named, never inferred from `0x07`. Twelve items carry forward with the literal phrase `no v1.31 owner`; **MERGE-05's +96 B leonardo band breach is open and un-adjudicated** with the operator as its named owner. Eighth consecutive `override_closeout` (9 carry-forward items, none originating in v1.31). Closed via **PRs to `beta` in all three repos, not direct merges**, per operator decision — meta tagged `v1.31`, gitlinks re-pinned; **no beta cut yet**, and stable stays operator-gated. See `.planning/MILESTONES.md` §v1.31.)
## Current Milestone: v1.41 Verification Moves to the Host

**Activated:** 2026-09-20 · **Phases continue at 202** (v1.40 ran 197–201; the vacated **150** slot and
the v1.24–v1.29 version slots stay unreused so every by-number cross-reference keeps resolving)

**Status (2026-09-23): all 6 phases (202–207) COMPLETE, 29/29 plans.** Phase 207 closed with verifier 4/4 (REL-01, REL-04). Both sub-repos carry `3.1.0b1` in one single-file commit pair, fw `a55f2d8` and app `67f93e2`. Each sits on a local merge of `origin/beta`, so the ship PR merges with no conflict on the version line. Both publishers' own dry run prints `DRY_RUN: 3.1.0b1`. **Nothing is pushed from either sub-repo; the `beta` push at ship time is what publishes.** The wiki record (the Breaking-Changes 3.1.0b1 entry and the new Writing-and-Verifying page) is live at `880a59b`, by an operator-approved fast-forward that also published the 2026-09-15 fix `f967398`. Criterion 4 holds: no GitHub Release and no `v1.41` tag. Outstanding before the close: `/gsd-secure-phase 206` and `207`, and code-review WR-01, a pre-existing error: the live Testing-Chips page says `dev test` runs twice, but the default has been three since `b596249`.

**Goal:** The Arduino stops deciding whether a chip is blank or matches an image. The host reads the
chip and compares in Python — one comparison implementation, a named diagnosis instead of a single
address, and the flash the removed command surfaces were costing.

**Why now.** Verification lives in the wrong place, and has since the beginning. The firmware compares
bytes it has no better view of than the host does, and it aborts at the *first* bad byte — so a user
learns one address and nothing about the shape of the failure. The host meanwhile already carries a far
richer comparison primitive: `classify_fingerprint` / `_diff_offsets` in `chip_test.py` names *why* a
verify failed (blank/contact fault vs stuck bits vs pattern never matched) and counts total against
bad. `dev test` has been more informative than `verify` for four milestones. Routing every comparison
through one host implementation closes that gap and deletes the second one. AVR flash is the scarce
resource — the v1.33 premise — and `CMD_VERIFY` / `CMD_BLANK_CHECK` are a dispatch case, a wrapper, a
configure case and a header declaration each, all to run a byte comparison the host can run for free.
Wire volume is roughly unchanged: verify pushes the whole image down today; read pulls the whole image
back instead.

**Shape.** Host comparison engine first — `blank` and `verify` become read-and-compare against a
constant `0xFF` and against a file respectively, streaming per chunk, stopping at the first mismatch by
default and, under a flag, scanning the whole device and reporting the mismatching ranges. Then the
firmware command surfaces go: `CMD_VERIFY` (6) and `CMD_BLANK_CHECK` (4), their dispatch entries,
`is_memory_cmd`, the `configure_memory` case, and the `eprom_verify()` / `eprom_blank_check()`
wrappers. Then the in-algorithm pre-flights go too — the write-init and erase-end blank checks,
`mem_util_blank_check{,_region}`, and the `FLAG_SKIP_BLANK_CHECK` wire bit — with the host taking over
the refusal. `write` gains an opt-in `--verify` read-back. Both repos bump to `3.1.0b1`.

**What must NOT be removed.** `memory_verify_execute` stays: `eprom.cpp` calls it for the
`VERIFY_PER_PULSE_PLUS_FINAL` arm on protocols `0x07` / `0x08`, and `memory_utils.h` exposes it
precisely so `eprom.cpp` need not carry a byte-identical copy. The in-algorithm verifies are
load-bearing and untouched — the per-pulse verify inside the EPROM program loop (a UV program loop
cannot decide whether to pulse again without it), `eeprom28c_verify_page_readback`, and
`flash_util_verify_operation`. `MSG_ERR_VERIFY` (0xAF) stays for the same reason. This milestone
removes a *command surface*, not verification.

**Decisions taken at activation.**

- **D-1 — All of it, both halves** (operator 2026-09-20). The standalone commands AND the in-algorithm
  pre-flight blank checks leave the firmware. This retires Phase 201's `mem_util_blank_check_region` as
  firmware code, five weeks after it landed, and re-lands the region property on the host.
- **D-2 — The host pre-write blank check is exempt on erasable parts** (operator 2026-09-20). A part
  carrying `FLAG_CAN_ERASE` is erased immediately before the write, so the check passes trivially and
  always has. Only UV parts pay the read. `write -b` keeps its meaning as the opt-out. The consequence
  is accepted deliberately: with the device-side refusal gone, this host check is the whole safety net
  against half-programming a non-blank UV part, and it has no second line of defence. The exemption's
  reasoning is to be explicit in the code and pinned by a test, not left as a remembered argument.
- **D-3 — Post-write verify is opt-in** (operator 2026-09-20). `write --verify` chains a read-back
  compare of the written region. Default write time is unchanged.
- **D-4 — Clean break on the protocol** (operator 2026-09-20). Ordinals 4 and 6 are retired outright,
  not deprecated. The host direction is safe without a version gate: a new host against old firmware
  only ever sends `CMD_READ`. Old host against new firmware is refused by the existing fail-closed
  dispatch.
- **D-5 — `3.1.0b1` in both repos** (operator 2026-09-20). A minor bump, beta series, stable line
  untouched. This is the first version string movement since `3.0.0b48` / `3.0.0b33`; v1.40 shipped
  without one, which is why its three held gh#70 / gh#66 / gh#71 answers still have no version to name.
- **D-6 — dev-test seed R4 rides along** (operator 2026-09-20). One leased serial session per plan
  instead of one per call. Directly provoked by this milestone: a pre-write blank check, a write and a
  `--verify` are three separate port opens under today's `EpromOperator.comm`-is-None-after-every-call
  shape.

**Known open mechanic.** Aborting a read mid-stream. The read path is ack-driven, so the host can stop
acking — but there is no abort message in the protocol and the END phase must still run to leave the
port clean. Without a resolution, "break at first mismatch" saves reporting noise but no time. This is
a research question for the first phase, not an assumption.

**Target features:**
- One host comparison engine, streamed per chunk, shared by `blank` and `verify`
- First-mismatch default; a flag for a whole-device scan reporting mismatching ranges
- Failure diagnosis through `chip_test.py`'s `_diff_offsets` / `classify_fingerprint`, not a bare address
- `CMD_VERIFY` and `CMD_BLANK_CHECK` removed from the firmware, ordinals retired
- Firmware write-init and erase-end blank checks removed, `FLAG_SKIP_BLANK_CHECK` retired
- Host pre-write blank check, exempt on erasable parts
- `write --verify` opt-in read-back
- One leased serial session per plan (seed R4)
- Both repos to `3.1.0b1`

**Cost that is not incidental.** Test re-anchoring: 13 firmware test files, 17 app test files, and the
`protocol_branch_inventory.json` golden — which re-derives lossily, so it must be diffed field-by-field
keyed on `line` rather than trusted to its truthiness gate. `dev test`'s `OP_VERIFY` and
`OP_BLANK_CHECK` steps route through the rewritten methods, so verdict classification and
`dedup_fingerprint` re-keying are in scope, not side effects.

**Mechanics.** Dual-repo lockstep, firmware-touching, bench-gated. Branch `v1.41-verification-to-host`
off `beta` in all three repositories. REQUIREMENTS.md and ROADMAP.md are **hand-authored**, as v1.33's
and v1.40's were and for the same reason — the GSD roadmap and requirements verbs normalise whole files,
and `ROADMAP.md` is ~7,900 lines of hand-kept history. `phases.clear` is **skipped**: 25 phase
directories are live in `.planning/phases/` and the verb hard-deletes every non-`999.*` one.


## v1.40 Archive: Program-Parameter Fidelity — Closed 2026-09-20 (closed, not shipped)

**Outcome:** 5 phases (197–201), 26 plans, 65 tasks, **19/24 requirements**, `override_closeout`,
tagged `v1.40` — a bare tag that must never become a GitHub Release. The override mechanism exists
and fails closed, all three of `build_db.py`'s part-specific hardcodes are gone, and the 746-row
database changed **25 rows with 0 `support_status` changes and none added or removed**. The `VPP_MV`
`0xF0` mask was completed so 25 V and 21 V stopped collapsing onto 18 V, and `DECODE-NOTES.md` § 9
records why: the voltage word's two nibbles select a **programmer rail index, not a chip**
**requirement**. The rails were measured — **17380 mV** on the drop path, **22140 mV** direct VPE at
socket pin 1 — and the shortfall for ten algorithm `0x07` rows was removed by **routing in firmware**,
decided on path capability while reading no voltage at all. Backlog 999.44's firmware half landed:
`region-end` travels host → wire → `mem_util_blank_check_region`, proven RED→GREEN and confirmed on
silicon. **It has not shipped** — 170 meta / 37 host / 15 firmware commits ahead of `beta`, zero
patch-equivalent, and the version strings on `beta` and at the tip are identical. **Five requirements
stay Pending, all by decision:** PULSE-04 / VOLT-04 / RAIL-05 are the three gh#70 / gh#66 / gh#71
answers, written and operator-approved but held until a version exists to name; RAIL-03 is honestly
unmet because `MSG_WARN_VPP_LOW`'s 5 % window is narrower than the measured +7.6 % ADC discrepancy;
OVR-03's citation contract is enforced by the test suite, not by the generator. Full record:
[`milestones/v1.40-CLOSE-RECORD.md`](milestones/v1.40-CLOSE-RECORD.md).

**Activated:** 2026-09-18 · **Phases continue at 197** (v1.39 ran 194–196; the vacated **150** slot and
the v1.24–v1.29 version slots stay unreused so every by-number cross-reference keeps resolving)

**Goal:** Every programming parameter the host sends is either what `infoic.xml` decodes to, or a
datasheet value recorded in one readable override file — and when the shield cannot deliver what a part
needs, the operator is told before the attempt, not after the failure.

**Why now.** Three community reports inside eight days, each with the reporter's own datasheet
attached, each a fleet-scale fault wearing one chip's name. gh#70's `MBM27C1000` programs with a pulse
a fifth of its datasheet minimum, and **217 of the 297** algorithm 7/8 rows carry that same 100 µs.
gh#66's `MBM27C4001` asks 12.0 V against a 12.2 V family floor, and **563 of 746** rows carry
`vpp_mv: 12000` while that part's own sibling correctly carries 12500 — the decode is not self-
consistent inside one family. gh#71's `MBM27128` needs 21 V ± 0.5 V where the VPP rail measured 17.8 V
and VPE measured 22.7 V, and **30 rows ask 18 V or more, 8 of them 21–25 V, every one
`support_status: supported`** beneath a ceiling that is a regulator's theoretical figure rather than a
socket measurement.

**Shape.** Five phases, 24 requirements. Phase 197 builds the override mechanism and proves it on the
pulse width; 198 settles the two voltage nibbles, including the 28-row group unproven since v1.32
Phase 148; 199 measures what the rails deliver and decides the VPE routing question; 200 makes an
elevated programming supply visible instead of decoded-and-dropped; 201 closes backlog 999.44's live
firmware half. Generator and host first — 201 is the only firmware change and the only dual-repo
lockstep. Phases 199 and 201 are bench-gated.

**Constraints that shape it, not preferences.** `infoic.xml` is the baseline for everything and nothing
part-specific may be hardcoded in the generator (**D-1**), so the first phase's real deliverable is a
mechanism rather than a value. Datasheet findings live in one override file carrying **only the changed
fields** (**D-3**), sibling to `tools/extra_chips.json`, small enough for a person to read whole. Decode
tables that read infoic's own encoding stay in code — they are the decoder, not corrections (**D-2**).
When the hardware cannot comply, the operation proceeds with a warning naming the required and the
deliverable voltage (**D-4**, operator 2026-09-18), which is what keeps voltage-reading calibration out
of scope: a refusal threshold would have needed a trustworthy ADC and a warning does not (**D-5**).

**Full detail:** [`REQUIREMENTS.md`](REQUIREMENTS.md) · [`ROADMAP.md`](ROADMAP.md) §v1.40. Requirements
and roadmap were **hand-authored** at activation, as v1.33's were and for the same reason — the GSD
roadmap and requirements verbs normalise whole files, and `ROADMAP.md` is 7,900 lines of hand-kept
history. `phases.clear` was **skipped**: 25 phase directories are live in `.planning/phases/` and the
verb hard-deletes every non-`999.*` one.

## v1.39 Archive: Protocol 0x05 Write Correctness — Closed 2026-09-17 (closed, not shipped)

**Activated:** 2026-09-15 · **Phases continue at 194** (v1.38 ran 189–193; the vacated **150** slot and
the v1.24–v1.29 version slots stay unreused so every by-number cross-reference keeps resolving)

**Goal:** A write to a 5V page-write flash part either preserves the bytes it was not asked to change,
or refuses — and never reports success while destroying data.

**Why now.** Two firmware defects on protocol `0x05`, both filed 2026-09-11 with bench evidence, both
still untracked by any milestone until this one. They are independent, and each one alone silently
corrupts a user's chip while printing `successful`:

- **gh#68** — the firmware writes only the bytes it was given and then commits the page. The device
  erases the whole physical page and programs only the loaded bytes, so every byte of that page which
  was not part of the write is erased to `0xFF` — **in both directions**, before the start address as
  well as after the end. There is no read-modify-write anywhere on this path and no warning. This
  affects **all 27** protocol-`0x05` parts, including the validated ones (w29c020, w29c040, sst39sf020,
  AE29F2008).
- **gh#67** — `flash_5v_page_page_size()` derives a page size from the device's total size instead of
  reading the part's real page from the database. On **9 of the 27** parts the derivation is smaller
  than the physical page, so a plain contiguous write performs two page-write cycles into the same
  physical page and the second erases what the first programmed. Affects AT29C512/AT29LV512,
  SST29EE512/SST29LE512/SST29VE512, W29C512/W29EE512, the AT29C020 family and the AT29C040 family.

Both were reproduced on a **W29C020** (Leonardo, Rev 2.0-class shield, firmware `3.0.0b22`, host
`3.0.0b38`) — a part whose derived page size is *correct*, which is what isolates gh#68 from gh#67.

The third item is bookkeeping the v1.38 close left behind: the PyPI per-version download-share
instrument was built to measure whether it was safe to claim `henols/firestarter`. The operator
claimed it on 2026-09-14 with the trigger unmet, and the seed is `status: fired`. The instrument was
retired on 2026-09-17; the reason is recorded at
`.planning/notes/adoption-instrument-retirement.md`.

### Decisions taken at activation (operator, 2026-09-15)

| | Decision |
|---|---|
| **D-1** | **Silent corruption is the milestone.** Both defects report `successful` while destroying data. Whatever the fix shape, the non-negotiable outcome is that a write never claims success over bytes it erased. |
| **D-2** | **Refusing is an acceptable fix.** Read-modify-write is not assumed. A firmware that declines an unsafe partial write with a clear error is a valid resolution of gh#68 — losing the operation is strictly better than losing the chip. |
| **D-3** | **gh#67's page size comes from the database, not a second derivation.** The real page is already generated into the chip database as `programming.infoic_page_size_raw`. Replacing one wrong derivation with another is not the fix. |
| **D-4** | **Bench validation on real silicon is required, not optional.** Both issues carry hardware evidence; the fixes must too. A green native test is not sufficient for a defect that was found on a bench. |
| **D-5** | **The stable firmware channel is out of scope.** `/releases/latest` serves 2.0.6 while current firmware is `3.0.0b30`. That is a release decision, operator-gated, and not phase work. |

### What this milestone does NOT do

- **It does not cut a stable firmware release.** See D-5. Whether stable users move off 2.0.6 is a
  separate, operator-gated call.
- **It does not work the 999.x backlog.** 17 backlog phase directories stay untouched.
- **It does not revisit the slug claim.** That is done, recorded, and its consequences are documented
  in `.planning/notes/gitmodules-archaeology-trap.md`.
- **It does not audit the other 12 protocols.** The scope is protocol `0x05`. If the same class of
  defect exists elsewhere it is filed, not fixed here.


**Outcome — closed 2026-09-17, 7/8 requirements, `override_closeout`, tagged `v1.39` (bare tag, no
GitHub Release).** Both defects fixed by **refusing**, not by read-modify-write — D-2 permitted
either, and the deciding measurement is recorded: a firmware page-staging buffer leaves 142 bytes of
RAM on `uno` for the whole call stack, and only a host pre-connect refusal can claim the device is
unchanged, because the firmware never learns the total payload length. Both refusals proved on
silicon on a `W29C020`: a pre-fix build reproduced both loss directions and printed `successful` over
the erased bytes; the post-fix build refused the identical commands with a named error, a non-zero
exit and a `sha256`-identical read-back.

**It has not shipped.** The fixes are on the milestone branch only — 16 meta, 17 firmware and 1 host
commit ahead of `beta`, confirmed by `git cherry` after a live fetch, and `origin/beta` still carries
the `flash_5v_page_page_size` derivation this milestone deleted. gh#67 and gh#68 stay live on the beta
channel. The versions published there — firmware `3.0.0b32`, app `3.0.0b47` — were cut by a
documentation-only push and carry none of this milestone's code. Ship via `/gsd-ship` **without**
a hand bump: the beta CI auto-increments, so the merge is the cut.

**PAGE-03 is the whole of the override.** Its bench part must be one of the 9 under-sized parts; the
ordered `W29C512` has not arrived, and `W29C020` is one of the 18 that were already correct. The
record reads *0 of 9 on hardware, 9 of 9 on the database comparison* in three documents and conflates
them in none. Full record: [`milestones/v1.39-CLOSE-RECORD.md`](milestones/v1.39-CLOSE-RECORD.md).

## v1.38 Archive: Repository Rename — Shipped 2026-09-15

**Activated:** 2026-09-13 · **Phases continue at 189** (v1.37 ran 182–188; the vacated **150** slot and
the v1.24–v1.29 version slots stay unreused so every by-number cross-reference keeps resolving)

**Goal:** Give the project a front door people can find, and a firmware repository that does not own the
unqualified name — without breaking firmware updates for anyone already installed.

**Why now.** Backlog **999.9** (gh#2) has been the highest-blast-radius item since the 2026-07-27 import,
and v1.35 shipped the wiki front door while *accepting* that this rename would invalidate every link it
wrote — recorded in `ROADMAP.md` as a "known sequencing hazard — accepted at activation, not solved", with
phases 169, 170 and 172 named as the ones needing a re-sweep. Backlog 999.13's own triage note says the
contribution-guide text "must be written *after* — or jointly with — 999.9."

The discovery failure is now measured rather than asserted (`gh api repos/henols/<repo>`, 2026-09-13):

| repo | role | stars | forks | watchers |
|---|---|---|---|---|
| `firestarter` (was `firestarter_prom`) | front door since v1.35; claimed the short slug 2026-09-14 | **0** | **0** | **0** |
| `firestarter_fw` (was `firestarter`) | firmware | 27 | 11 | 3 |
| `firestarter_app` | host CLI | 48 | 6 | 4 |

Six weeks after v1.35 made it the documented entry point, nobody has found it, while 75 stars sit on the
two components. That is the case for doing this at all, and it is stronger than a naming-aesthetics
argument.

**The shape of the risk, stated once so no phase re-derives it.** Both renames are individually covered by
permanent GitHub redirects — and `firestarter_prom`'s would survive forever, because nothing will ever
claim that slug. The single destructive act in 999.9 is **claiming** `henols/firestarter` for the meta
repository, which is what deletes the firmware repository's redirect. **v1.38 does not perform that claim**
(D-1). Everything else in 999.9 is safe to ship now, and is what this milestone ships.

Blast radius is measured, not estimated: the three hardcoded endpoints in
`firestarter_app/firestarter/constants.py` are consumed only by `firmware.py`, so what breaks is the `fw`
command alone — read, write, verify, erase and `dev test` are untouched. Full analysis in
[`notes/999.9-repo-rename-impact-analysis.md`](notes/999.9-repo-rename-impact-analysis.md).

### Five strands

| Strand | Scope | Origin |
|---|---|---|
| **RENAME** — free the name | `firestarter` → `firestarter_fw`; `.gitmodules` on both branches; `git submodule sync --recursive` | 999.9 |
| **URL** — endpoints that must not depend on a redirect | the three `FIRESTARTER_*_URL` constants plus the two hardcoded fixtures in `tests/test_firmware_install.py`, on `beta` **and** `main` as separate changes | 999.9 |
| **STABLE** — reach the default install | a 2.0.x stable cut off `main` carrying the URL fix, because `pip install firestarter` resolves to **2.0.7**, not to the `3.0.0bNN` line | 999.9 |
| **SWEEP** — live references only | ~12 tracked files: `README.md`, both sub-repo READMEs, and five `.planning/codebase/` documents | 999.9 |
| **GATE** — make the deferred claim measurable | a PyPI version-share instrument for the adoption gate, and the standing no-Releases rule | [`seeds/SEED-claim-firestarter-slug.md`](seeds/SEED-claim-firestarter-slug.md) |

### Decisions taken at activation (operator, 2026-09-13)

| ID | Decision | Consequence |
|---|---|---|
| **D-1** | **v1.38 stops before the claim.** Renaming `firestarter_prom` → `firestarter` is out of scope. **SUPERSEDED 2026-09-14 — the operator directed the rename after the milestone's phases closed, with the adoption trigger unmet.** | The milestone closes with the front door still named `firestarter_prom`. The claim is deferred to a seed whose trigger is *adoption*, not a date. |
| **D-2** | **Firmware releases stay in the firmware repository.** No mirroring onto the meta repo, not even for a bounded sunset window. | Rules out the one continuity mechanism that would have let the claim happen immediately, and therefore implies D-1 rather than merely accompanying it. |
| **D-3** | **`main` and `beta` are separate changes**, and `main` is the one that reaches users. | `pip install firestarter` resolves to **2.0.7**; `origin/main` is that code, 948 commits behind `beta`, carrying `FIRESTARTER_RELEASE_URL` but no `submit.py`. Repointing `beta` alone would leave the default install broken *while passing 999.9's own stated clean-environment validation*. |
| **D-4** | **The meta repository must never publish a GitHub Release.** Bare milestone tags only, as today. | It has **0** Releases, which is exactly what makes a post-claim failure a clean 404. Publishing one arms `_compare_versions` to parse `v1.36` as PEP 440 `1.36`, judge `3.0.0b29` newer, and report firmware as current forever — silent and permanent, where today it is loud. |
| **D-5** | **The 672 archived references under `.planning/milestones/` are not swept.** | `.planning/`→`.planning/` citations are historical-by-intent: they record what the repository was called when the record was written. Repairing them destroys the evidence they exist to preserve. |
| **D-6** | **The `.gitmodules` history trap is documented, not solved.** | Fixing `.gitmodules` on `beta` and `main` does not fix history, so any pre-rename checkout plus `submodule update --init` resolves to the meta repository and clones the parent into its own `firestarter_fw/` child. Unfixable by construction; the deliverable is a documented workaround. |
| **D-7** | **Every outward-facing step stays operator-gated** — the GitHub rename itself, the stable cut, and every push. | Standing posture since v1.21. A merge to `beta` cuts a pre-release in both sub-repos and publishes the host one to PyPI, so no agent performs one. |

### What this milestone does NOT do

- **It does not claim `henols/firestarter`.** D-1. The deferral is the design, not an unfinished edge.
- **It does not rename `firestarter_app`.** 999.9's prose says "all three repositories" but names only two
  mappings; the host repository keeps its name, and the incoherence that PyPI `firestarter` is the app while
  GitHub `firestarter` will be the meta repo is noted rather than resolved.
- **It does not eliminate stranding.** Nothing reaches users who never upgrade. The sequencing shrinks that
  set; it cannot empty it. What bounds the damage is the narrow blast radius, not the sequencing.
- **It does not change firmware behaviour.** The firmware repository is renamed and its README repointed;
  no source, no protocol, no dual-repo behavioural lockstep.
- **It does not repair v1.35's wiki and README links.** Those become wrong only when the claim fires, which
  is deferred — so the re-sweep of phases 169/170/172 travels with the claim, not with this milestone.

## v1.37 Archive: Operator Safety, Answered Reports & Claim Hygiene — Shipped 2026-09-13

**Activated:** 2026-09-10 · **Phases continue at 182** (v1.36 ran 174–181; the vacated **150** slot and
the v1.24–v1.29 version slots stay unreused so every by-number cross-reference keeps resolving)

**Goal:** Stop the project withholding what it already knows — from the operator about to destroy a chip,
from the reporter who has been waiting a month for an answer, and from the maintainer reading a guard that
no longer exists.

**Why now.** Three separate signals arrived within a week of each other and they are the same defect wearing
three coats:

- **A user destroyed chips** ([gh#60](https://github.com/henols/firestarter_prom/issues/60), 2026-09-04) for
  want of a warning this project could already have given. The hardware fact has been established in-repo
  since 2026-07-10 — [`notes/jumper-display-ground-truth.md`](notes/jumper-display-ground-truth.md) records
  **JP5 = `A19_CUT`, a bridged solder jumper** (not an operator-settable header), and JP4 = `P1_VPP_JMP`
  routing VPP to socket pin 1. Nothing in the tool says so at the moment it matters.
- **A user was taught to bypass a safety gate** ([gh#62](https://github.com/henols/firestarter_prom/issues/62),
  2026-09-09). `erase AE29F2008` refuses with a bare `Not supported`; the refusal is *correct* — flash4 clears
  `FLAG_CAN_ERASE` so a 12 V bulk erase cannot reach a 5 V-only part — but it explains nothing, so the
  reporter re-ran the operation under **a different chip's identity with `--force`**. That is precisely the
  path the gate exists to prevent, and the refusal's wording is what sent them down it.
- **Three reporters are still waiting.** v1.36 shipped the machinery that answers gh#23, #28 and #31 and, by
  its own declared scope note, did not work the tracker. The fixes exist; the replies do not.

**The through-line, stated once so no phase re-derives it:** in every case the information existed and was
not said. That is also true inside the repository — a file declaring a guard that was deleted, a baseline
recording figures three milestones stale, two tests asserting coverage that no longer exists. The tool's
honesty and the repo's honesty are the same discipline, which is why they ship together here.

### Four strands

| Strand | Scope | Backlog |
|---|---|---|
| **SAFE** — refusals and warnings that teach | A destructive-operation gate for parts whose pin map puts VPP on socket pin 1 while the chip expects A19 there; a flash4 erase refusal that names its cause and its alternative | 999.51, 999.52 |
| **REPLY** — answer the reporters | gh#23 / #28 / #31 (what v1.36 changed, and the re-run that would settle each) plus gh#62's own answer | 999.54 |
| **CLAIM** — things the repo says that are not true | The deleted `dispatch_mirror.py` still named as a live guard in two repositories; `size_baseline.json` still recording pre-fix figures; a docstring citing `build_db.py:594` for a symbol at 545; `_is_interactive` dead with two tests asserting through it; `Catalog sync check` red on `main` since 2026-08-31 | 999.50, 999.41, 999.45, 999.53, 999.47 |
| **FLOOR** — the one item with an external clock | `requires-python = ">=3.9"` and `target-version = "py39"` against mypy `python_version = "3.10"` — **Python 3.10 EOLs 2026-10-31, inside this milestone's window** | 999.26, 999.27 |

### Decisions taken at activation (operator, 2026-09-10)

| ID | Decision | Consequence |
|---|---|---|
| **D-1** | **999.43 R4 (session reuse) is deliberately OUT**, against a measured payoff. | The payoff is real and large — 2.518 s/connect Uno-class, 2.607 s Leonardo-class, 2.500 s of it a board-independent structural floor, so 50–80 s per `dev test` run. It is excluded because its failure mode (a leased link poisoned by one `SerialError` silently corrupting every later step, against `run_plan`'s non-fatal-step guarantee) is the largest risk available, and this milestone is about correctness of what the tool says, not throughput. It stays **shortlisted for v1.38** and its measurement does not expire. |
| **D-2** | The FLOOR strand is in **because the deadline lands mid-milestone**, not because it is related. | It is the only backlog item paced by something other than us. Deferring it again means doing it under the deadline rather than ahead of it. It is scoped as one small phase and is independent of every other strand. |
| **D-3** | Whether the flash4 erase refusal takes a **new message id** is a plan-time decision with a measured cost, not a default. | `include/messages.h` is codegen-generated and id-only — a new id is a `messages.toml` entry plus a `codegen.py` regeneration for both targets, and it costs firmware flash on boards at **0 B headroom** (leonardo, since v1.32 Phase 153). The zero-firmware-byte alternative — keep `MSG_ERR_NOT_SUPPORTED` and give the host the explanatory text — must be priced against it before either is chosen. |
| **D-4** | The SAFE gate's part predicate is **derived from the database**, never a hand-kept part list. | The pin-map → VPP-on-pin-1 mapping already exists and is counted (291 chips across `DIP28_27256`, `DIP28_2764`, `DIP32_STD`, `DIP32_27C020`). A hand list silently omits the next part added. |
| **D-5** | Every outward-facing reply stays behind **operator wording review** before posting. | Standing gate on upstream communication. Note `--auto`/`--chain` auto-approve human-verify gates, so `autonomous: false` is not self-protecting — the phase must not be run in those modes. |
| **D-6** | If the gh#62 investigation concludes AE29F2008 is **misclassified**, the fix is in `build_db.py`'s decode. | `chip_database.json` is GENERATED. A hand edit would be silently reverted by the next regeneration and would not fix the other parts sharing the decode path. |
| **D-7** | `999.41`'s re-record uses the **fixture-severance pattern**, and no acceptance criterion may say "tests byte-unchanged". | `test_check_size_baseline.py` hard-codes 22952 / 23000 / 25098 in roughly six places and feeds frozen `captured_build_v158_*.log` fixtures. Re-capturing in place destroys the arms that deliberately depend on pre-change figures; a byte-unchanged criterion is unsatisfiable by construction. |

### What this milestone does NOT do

- **It does not make `dev test` faster.** D-1 above. Any timing improvement observed is incidental.
- **It does not claim the JP5 hazard is eliminated.** The jumper state is not readable by the tool — the
  reporter said so and the schematics agree — so the deliverable is a warning and a refusal-to-proceed, not
  a detection. A user who confirms falsely still destroys the chip.
- **It does not re-open the three-way dispatch invariant.** 999.50 asks only that the repositories stop
  claiming a guard that was deleted. Whether that invariant is worth re-guarding is a separate decision this
  milestone surfaces and does not take.
- **It does not close gh#23 / #28 / #31.** The reporters' disputes are the open question; the deliverable is
  an honest reply and a request for an attributable re-run, not a unilateral close.
- **It touches firmware only at the edges.** One `.md` (`PROTOCOLS.md`), one baseline JSON plus its test
  fixtures, and — only if D-3 goes that way — one generated message id. No protocol change, no dual-repo
  behavioural lockstep, no golden register traces.

## v1.36 Archive: `dev test` Fidelity — Only Run What Can Tell You Something, Report Only What You Know — Shipped 2026-09-09

**Activated:** 2026-09-02 · **Phases continue at 174** (v1.35 ran 167–173; the vacated **150** slot and
the v1.24–v1.29 version slots stay unreused so every by-number cross-reference keeps resolving)

**Goal:** Make `dev test` fail only for reasons that are actually the chip's, run no operation whose
result is empty by construction, and report only what the run already knows.

**Why now — the community is telling us the tool is wrong, not the chips.** Six `dev test` issues are
open in `henols/firestarter_prom`, and on three of them the reporter disputes our own triage. On
[#28](https://github.com/henols/firestarter_prom/issues/28) (m27c512): *"It's because the chip isn't
erased between writes (obviously)."* On [#31](https://github.com/henols/firestarter_prom/issues/31)
(m27c1001): *"I believe the bot is incorrect. There seem to be an actual bug in the test."* On
[#23](https://github.com/henols/firestarter_prom/issues/23) (w27e257): *"Bot is mixing a pass with a
fail — the first one didn't have VPP correctly hooked up. The second one actually passed."* The first
two land on an already-filed, already-root-caused defect (Backlog **999.44**); the third is the
misattribution consequence that same backlog item names third. For a community-facing validation tool
that files public issues titled `[dev test] <chip> — FAIL`, a harness that blames the part for its own
faults is the worst defect it can have.

**Target features:**

- **An operation that cannot tell you anything must not run.** Four measured cases, all read from
  source at HEAD: the fingerprint read-back gate at `chip_test.py:3100` consults op and final-cycle but
  **never `outcomes`**, so every *passing* run pays two full-device reads to classify a mismatch set
  that is empty by construction; a full read where an on-device `verify` gives the same coverage ~24%
  cheaper and early-returns on first mismatch; the read step's second full sweep, replaceable by a
  bit-structured sample that toggles every address line in both polarities (**MEASURED AND REJECTED,
  Phase 180** — this clause is left standing, marked, rather than rewritten. PRUNE-08 closed as
  *measured, not worth doing*: because `EpromOperator._operation_context` connects on entry and
  disconnects on exit, a region-wise sample costs **10 connects where the full sweep it replaces
  costs 1** — a net plus-nine connects per read step, 25.18 s on the Uno class against Phase 176's
  measured per-connect cost, and dearer on Leonardo too. The sample is not cheaper on either board
  class, so no sampling code shipped and criterion 4 is recorded Not Applicable rather than left
  silently unaddressed. Full arithmetic and the invalidating condition — R4-01, which would move the
  read step off one-connect-per-read and make this close recomputable — in
  `.planning/phases/180-read-step-sampling-conditional-on-phase-176/180-PRUNE-08-CLOSURE.md`); and
  **32 serial connects
  for one at28c256 run** (`self.comm = None`, `eprom_operations.py:547`), 12 of them spent on ~3 KB of
  SDP traffic. The modelled saving is 31.5% across six chip classes, but **speed is the consequence,
  not the goal** — the rule is that pointless work does not run.
- **Enforced structurally, not by comment.** A test over `derive_plan` output, the same shape as the
  existing `test_shipped_ops_never_reach_sdp_arm` sentinel (`tests/test_chip_test_sdp_leg.py:827`), so
  a future plan cannot reintroduce a no-information operation. It also carries the one load-bearing
  dependency: dropping the unconditional read-back is safe **only** because a verify follows every
  write in the same cycle and a near-all-`0xFF` device cannot pass a verify against a generated
  pattern. A plan emitting a write with no verify behind it must fail that test.
- **UV parts stop failing for the tool's own blank check** (Backlog 999.44, host half). Pass
  `FLAG_SKIP_BLANK_CHECK` on `uv-slot` writes. Today run 1 leaves a UV part non-blank and run 2 is
  refused even though it targets a different, provably blank slot — so a UV part is testable at most
  once, and only if it arrives blank. The masked slot write is monotone (it only clears 1→0) with a
  verify immediately behind it, so the skip cannot corrupt. **Correction from research:** `FLAG_SKIP_BLANK_CHECK` fixes the *firmware
  write-init pre-flight* only — it does not touch the plan's own **standalone `blank-check` step**,
  which `derive_plan` puts in every UV plan and which still returns `VERDICT_BAD`, still trips
  `hardware_refused`, still aborts cycle 2, and still yields `[dev test] AM27C020 — FAIL` through
  `overall_verdict`'s FAIL-dominance. **The success criterion is `overall_verdict == "PASS"` with
  `run_count == 2`, not "the write step went OK".** The regression test that does not exist today:
  a UV part holding data outside the target slot must accept a slot write and the run must PASS.
  (**Mechanism FALSIFIED, Phase 179** — the "still trips `hardware_refused`, still aborts cycle 2"
  clause above is wrong and is left standing, marked, rather than rewritten. MEASURED: the standalone
  blank-check sits at index 2, OUTSIDE a `cycle_block_bounds` that is `(3, 6)` for `m27c512`,
  `am27c020` and `tms27c512`, and `run_plan`'s per-step path has no `hardware_refused` mechanism at
  all — the cycle-2 abort came from the WRITE step's own firmware refusal. What the blank-check
  actually did was return `VERDICT_BAD` into a FAIL-dominant `submit.overall_verdict`
  (`submit.py:164-171`). The bullet's substance stands: both defects still had to be closed.
  Same falsification recorded at `.planning/REQUIREMENTS.md` UV-02, `.planning/research/PITFALLS.md`
  Pitfall 5 step 2, and `.planning/research/SUMMARY.md`. **DELIVERED, Phase 179** — closed 2026-09-08
  on a real ST M27C512 on a Leonardo: `overall_verdict == "PASS"` with `run_count == 2`, and the
  regression test that "does not exist today" now exists.)
- **A tool or rig fault is never filed as a chip verdict.** One tool defect currently produces three
  BAD steps and a submit prompt offering `[dev test] AM27C020 — FAIL` against the chip.
- **The report states what the run knows** (Backlog 999.36, 13 requirements already drafted as
  RPT-A1…E3). Populate `chip_id_actual` on a *passing* id check; export the fingerprint's `total`/`bad`/
  `bad_pct`/`evidence` as additive siblings, the read-step `divergence` metric, and `plan.is_uv`;
  delete `voltage.vpp_mv`/`vpe_mv` and `banner.locked_steps`, which no code path assigns; wire the two
  real re-sync events at `serial_comm.py:488-494` and `:504-510` into `transport_health`; make
  `duration_s` a per-operation cost and add a real wall-clock `elapsed`; bump the schema to **1.8**.
- **Canonical chip naming** — report the matched database `part_number`, not the operator's raw CLI
  token, so an issue title names a string that exists in the database.

**The blast-radius gate — CORRECTED 2026-09-02 after research falsified the original claim.** This
section previously read *"`dedup_fingerprint` must stay byte-identical … Not one field being added,
filled or deleted is in that hash today."* **That sentence was wrong, and the gate it named does not
exist.** Three of four researchers falsified it independently **by execution** against `firestarter_app`
at `0a93999`. It is true of *report fields* and irrelevant to what this milestone actually changes: the
hash reads **values and plan shape**, not schema keys. Four re-key paths were measured:

| # | Change | Measured effect on `dedup_fingerprint` |
|---|---|---|
| 1 | Gating the fingerprint read-back on failure | A *passing* write/verify carries `classification="indeterminate"` (a perfect match falls through `classify_fingerprint`'s four buckets), and the hash contains `f"{op}={verdict}:{cls}"`. **`4dc282a5d596` → `60a031573aab`.** |
| 2 | Pruning unsupported SDP steps from `Plan.steps` | **`a00791f1c2b4` → `7d1cd4157cfa`** for m27c512/full. Affects **637 of 677** chips carrying six `supported=False` SDP steps. |
| 3 | Canonical `part_number` naming | `ac.chip` is `parts[0]`. **`a00791f1c2b4` → `a6f6c6354047`.** 732 of 746 part numbers differ from their own lowercase form and every open issue title is lowercase — this re-keys essentially all project history. |
| 4 | UV blank-check abort (second-order) | A BAD standalone blank-check → `hardware_refused` → cycle 2 never runs → `run_count` collapses to 1 → `repeat_policy_tag` emits the degraded `fast`-shaped discriminator on a run nobody asked to be fast. ⚠ **Mechanism FALSIFIED, Phase 179** — no `hardware_refused` fires for a step outside the cycle block; the cycle-2 abort came from the write step's own firmware refusal, and the blank-check's actual contribution was a `VERDICT_BAD` into a FAIL-dominant `overall_verdict`. The `run_count` collapse and the degraded `repeat_policy_tag` were real; the named cause was not. |

The same read-back change also **flips the promotion ladder**: `disposition='inconclusive' ladder=''` →
`'suggests: candidate for community-reported' ladder='community-reported'`, because `build_db_diff`
routes on `has_indeterminate_fingerprint`. A performance change moves chips onto the Phase 114 GRAD-01
ladder as a side effect.

**And the gate itself is absent.** Every dedup test in `tests/test_diagnostic_report.py` is *relational*
(`fp(a) == fp(b)`, computed at runtime), so a change to the hash algorithm passes all of them. There is
exactly **one** frozen expected-hash literal in the suite (`tests/test_diagnostic_report.py:1377`,
`"a0a50436ae3d"`), and the frozen schema-1.2 fixtures this was supposed to be "asserted against" carry
hand-written placeholder tokens (`"deadnu11id00"`), not real hashes. `count_agreeing` reads the
**embedded** hash and never re-hashes, so any re-key is permanent and unrecoverable except by publishing
an old→new mapping.

**Therefore: build the oracle first, change nothing the oracle has not measured.** The first phase is a
blast-radius invariance harness — a frozen `(report shape → 12-hex)` table computed against HEAD before
any change lands, plus a pinned `build_db_diff` ladder output and the measured raw-token→`part_number`
delta. Each of the four re-keys then becomes a **declared, dated, one-time decision recorded in
`MILESTONES.md`**, not a silent history fork.


**Scope boundaries, decided at activation (operator, 2026-09-02):**
- **Host app only.** `firestarter_app` changes only; no firmware edit, so no dual-repo lockstep, no
  golden register traces, no size baseline.
- **999.44's firmware half is therefore OUT and stays a defect.** The region-scoped
  `mem_util_blank_check` — and with it the product-level bug where `firestarter write foo.bin -a
  0x3FF00` is refused on any non-erasable part holding data anywhere — is **not fixed by this
  milestone** and carries as backlog. The backlog's own analysis rejected the host half *alone* on
  exactly this ground; it is taken here knowingly, not overlooked.
- **Community issue replies and closures are not deliverables.** #21, #23, #28, #31, #45 and #50 stay
  open; this milestone builds the fixes, it does not work the tracker.
- **Bench is mixed.** Native and unit tests carry what they can; a named, minimal set of hardware legs
  covers only what nothing else can prove — the UV slot regression above, and R4's per-connect cost,
  which is **currently unmeasured and must be measured before it is scoped**.

## v1.35 Archive: Documentation Consolidation & Wiki Migration — Shipped 2026-09-02

**Activated:** 2026-08-30 · **Phases continue at 167** (v1.34 ran 160–166; the vacated **150** slot
and the v1.24–v1.29 version slots stay unreused so every by-number cross-reference keeps resolving)

**Closed 2026-09-02 — 29/32 requirements, `override_closeout`.** 7 phases (167–173), 41 plans across
the five that ran the machinery. Meta tagged `v1.35` at `6e84030b`; `beta` lockstep cut performed and
channel-verified under the new rulesets; three `.github`-only pull requests merged into three protected
`main` branches. The wiki is live with 11 pages, both sub-repo `doc/` directories are gone, `main` is
behind an `enforcement: active` ruleset in all three repositories with `current_user_can_bypass: never`,
and `git.base_branch` now resolves `beta` so the close procedure survives the protection it added.

**What the goal statement above no longer describes.** It says pages are *"authored in-repo and checked
against reality"*. **Both halves of that were retired during the milestone.** On 2026-08-30 the operator
reversed to **wiki-only authoring** — Phase 167 had built and proven the in-repo source, one-command
publish and drift check, and Phase 168 deleted it — withdrawing WIKI-03 and WIKI-04. Then on 2026-09-02,
hours after the close, `wiki-check.yml` and every checker under `tools/wiki/` were deleted as
disproportionate to an 11-page wiki. **No automated wiki guard of any kind now exists.** Wiki pages are
edited in a web UI with no pull request, no diff, no review and no CI — accepted knowingly, recorded as
a cost rather than an oversight.

**The milestone-level non-claim: relocation is not verification.** HONEST-01 proved no claim was upgraded
in the move. It proved nothing about whether any claim is *true*.

**Three record gaps, named not absorbed.** Phases **169** and **170** ran ad hoc — no plans, summaries,
phase directory or verifier pass. Phase **172** has no `172-VERIFICATION.md`. **FRONT-02** was declined
outright by the operator; it cannot hold at the same time as FRONT-03.

**Goal:** Make `firestarter_prom` the single documented front door — one simple get-started README per
repo, all project documentation in the `firestarter_prom` wiki authored in-repo and checked against
reality — and enforce in repo configuration the centralization the docs will claim.

**Target features:**

- **`firestarter_prom` becomes the front door.** The central repo has *no README at all* today. It gets
  its first: a short get-started page — what Firestarter is, how to get the RURP shield, install the
  CLI, flash the firmware, read a first chip — that links into the wiki for everything deeper.
- **Wiki source lives in the repo, not only in the wiki.** Pages are authored as markdown under
  `firestarter_prom/`, pushed to the wiki by a sync script, with a drift check so the wiki cannot
  silently diverge from the code it documents.
- **All 13 sub-repo `doc/` files migrate.** `firestarter_fw/doc/` (3 files) and `firestarter_app/doc/`
  (10 files) are emptied and removed; their content lands in the wiki.
- **Three simple, repo-scoped READMEs.** Each README carries only what is specific to its own repo and
  links up to the prom docs for the rest. Legacy is stripped, not relocated.
- **The repo policy is enforced, not just documented** (Backlog 999.13 / gh#6, in full): a single issue
  tracker stated in the docs and true in configuration, and `Protect main` rulesets actually enforcing
  on all three repos.

**Decisions taken at activation** (operator, 2026-08-30):

| # | Decision | Consequence accepted |
|---|----------|----------------------|
| 1 | All three READMEs become simple get-started pages; **prom is the front door** | `firestarter_app/README.md` is the PyPI `long_description` — a short README means a **thin PyPI listing** |
| 2 | Sub-repo READMEs hold **only repo-specific information** and point at the parent docs | Nothing about Firestarter-at-large is restated in a sub-repo |
| 3 | **Everything out of `doc/`** — all 13 files move, both directories removed | 3 files currently appear in the app sdist (`package-details.md`, `protocol-flags.md`, `protocol-id.md`); the sdist manifest changes. No doc ships offline with the package any more |
| 4 | **Relocate + correct only** — no new content authored | The compatibility matrix, per-family pages and task tutorials carried into 999.12 from the retired 999.14/gh#7 stay **deferred** |
| 5 | Wiki pages **sourced in `firestarter_prom`** and synced to the wiki | One sync script and one drift check to build and keep working; buys version control, review and mechanical honesty checking |
| 6 | **Full 999.13**, branch protection included | `/gsd-complete-milestone` pushes `main` directly today; under PR-only `main` that must become a PR flow or a documented admin bypass |
| 7 | Sub-repo wikis **disabled** | Done 2026-08-30 at activation — `henols/firestarter` and `henols/firestarter_app` now have `has_wiki=false`; `firestarter_prom` keeps its wiki |

**Measured starting state** (verified 2026-08-30, not assumed):

| Fact | Value |
|------|-------|
| `firestarter_prom` README | **does not exist** |
| `firestarter_fw/README.md` | 151 lines |
| `firestarter_app/README.md` | **779 lines**, and is the PyPI `long_description` |
| `firestarter_fw/doc/` | 3 files — `PROTOCOLS.md` (556 lines), `SHIELD-REVISIONS.md` (128), `AT28C04-ADAPTER.md` (160) |
| `firestarter_app/doc/` | 10 files, ~1880 lines |
| Wiki repos | **none initialized** — `firestarter_prom.wiki.git` returns `Repository not found` |
| Issues enabled | `firestarter_prom` only (23 open); already `false` on both sub-repos |
| Branch rulesets | `firestarter` has one named `Protect main` with **`enforcement: disabled`**; `firestarter_prom` and `firestarter_app` have **none** |
| Dead issue links in docs | 6 — in both READMEs and `doc/beta-testing-install.md`, pointing at the two now-disabled trackers |
| App README TOC drift | lists `Id`, `Vpe`, `Hw`; the body has `List`, `Search`, `VCC` instead |
| Accumulated breaking-change walls | app README v1.10/v1.20/v1.32; fw README v1.10/v1.20 — above the install instructions in both |

**Operator-gated blocker.** GitHub creates `<repo>.wiki.git` only when the first wiki page is saved
through the web UI — there is no REST endpoint for wiki pages and push-to-create was **tested and
fails** (`remote: Repository not found`). Until the operator creates one page at
`https://github.com/henols/firestarter_prom/wiki`, nothing can be pushed to the wiki. Authoring,
README work, `doc/` triage and the 999.13 configuration are all unblocked and can proceed in parallel.

**Honesty constraint, inherited from 999.12.** Relocation must not upgrade a claim. Every
`support_status` value — `protocol-not-implemented`, `adapter-required`, `vpp-exceeds-max`, and the
`PROTOCOL-LEDGER` `UNVERIFIED` buckets — must survive the move rendered as faithfully as it reads
today. A wiki page implying blanket support for an unverified chip is precisely the false-PASS failure
mode v1.21 was built to prevent, and hand-maintained pages drift where a generator would not. The
drift check in feature 2 is the mitigation and is in scope, not optional.

**Known sequencing hazard — accepted, not solved.** Backlog **999.9** (gh#2) renames all three repos
(`firestarter_prom` → `firestarter`, `firestarter` → `firestarter_fw`). Every wiki link, README pointer
and issue URL this milestone writes would be invalidated by that rename. The operator was shown this at
activation and chose to proceed, sweeping references later rather than folding the rename in here or
sequencing it first.

**Deliberately out of scope.**

- The compatibility matrix, per-family pages, algorithm/command-set pages and task tutorials carried
  into 999.12 from the retired 999.14 / gh#7 — deferred by decision 4, not dropped.
- Backlog 999.9, the repo rename — see the sequencing hazard above.
- Any change to `.planning/` historical records. Citations from `.planning/` into `.planning/` are
  historical-by-intent and must not be "repaired" by this milestone's link work.
- Product code. This milestone changes documentation, repository configuration and one sync/check
  script; it does not touch firmware or host behaviour.

## v1.34 Archive: Pre-Merge Hardware Regression Validation — Closed 2026-08-29 (EARLY / SCOPE-REDUCED)

**Activated:** 2026-08-25 · **Phases continue at 160** (v1.33 ran 154–159; the vacated **150** slot
and the v1.24–v1.29 version slots stay unreused so every by-number cross-reference keeps resolving)

**Goal:** Prove on real silicon that v1.33's size reduction changed nothing behavioural — across
every Arduino board and every RURP shield revision the operator owns — before `prom#43` / `fw#56` /
`app#54` merge to `beta`.

**Why now.** v1.33 closed **locally** on 2026-08-24 with 42/43 requirements and the entire milestone
premised on **byte-level equivalence**: the heap allocator removed, the 64-bit runtime dropped,
`jsmntok_t` narrowed 8 → 6 B, the command-decode table reworked, handle types narrowed — **−2938 B
flash, −13 B RAM**. Every one of those claims is backed by native tests, golden traces and cold
build measurements, and **not one of them has run on an Arduino.** Three PRs sit open and unmerged.
A size-reduction milestone is exactly the shape of change whose failure mode is invisible to a build
gate and obvious on a bench, so the merge gets a hardware gate in front of it.

**The matrix — five distinct cells.** Leonardo + Rev 2.0 is the intersection of both sweeps and is
run once, not twice.

| Cell | Board | Shield | Note |
|------|-------|--------|------|
| A1 | Uno (ATmega328P) | Rev 2.0 | |
| A2 | uno328pb (ATmega328PB) | Rev 2.0 | Write expected to fail — Backlog 999.2 |
| A3/B2 | **Leonardo (ATmega32U4)** | **Rev 2.0** | Shared by both sweeps; the v1.31 reference rig |
| B1 | Leonardo | Modified Rev 0 | Voltage-divider-retrofitted Rev 1.0 board |
| B3 | Leonardo | Rev 2.2 | R41 = 10 kΩ (vs 4k7 on 2.0) |

**Per-cell method — A/B, control first.** Flash the pre-v1.33 control build, run the cell, then
flash the v1.33 build and re-run. Control baselines are the exact merge-bases the v1.33 branches
forked from: firmware **`8695ee5`**, host app **`6bfa645`** (35 and 7 commits behind their branch
HEADs respectively). Two chips per pass — **W27C512** (DIP28, `0x07`, 64 KiB) and **W29C020**
(DIP32, `0x05`, 256 KiB page-write) — each a full write → read → verify. **20 W→R→V cycles.**

The A/B is the whole point: without a control run in the same cell, on the same shield, with the
same chip seated, "this failed" cannot be distinguished from "this has always failed here." v1.31
shipped with **no comparative claim and no control run** and said so; v1.34 buys the comparison it
declined to make.

**Chip sweep.** Leonardo + Rev 2.0, `firestarter dev test <chip>` against all 11 parts of the v1.15
physical inventory on v1.33 firmware — W27C512, W27E512, SST27SF512, W27E040, ST M27C512,
SST39SF040, W29C040, W29C020, FM1608, AM27C020, 2516. Reports carry `fw_board_identity` since
Phase 147, so every report is firmware-attributable. A control re-run fires only where a result
diverges from that chip's recorded v1.15 disposition.

**Failure policy.** Every failure gets an evidence row and a root cause. **Only v1.33-caused
regressions get fixed in-milestone.** Pre-existing faults are recorded as known-and-carried, not
adopted.

**Known faults, declared before the bench runs, so a red cell is not mistaken for a v1.33 break:**

- **uno328pb cannot finish a program** — Backlog 999.2, chip-PROGRAM brownout. Its write cells are
  expected red on **both** arms.
- **W27E512** (stuck erase bit @0x3d) and **W27E040** (stuck erase bit @0x7db) — silicon wear,
  D-32, deterministic across reseats.
- **W29C040** carries a permanently locked §6.6 boot block; a full-device verify is physically
  impossible and its flash4 page-0 fault is CR-01, open since v1.15.
- **AM27C020** is marginal, not deterministic (write#1 60/64, write#2 0/64) — it cannot arbitrate
  any result in either direction.

**Second deliverable — the Modified Rev 0 rework trace.** That board is on the bench for cell B1
anyway, and `.planning/milestones/v1.7-artifacts/MODIFICATIONS.md` has been a stub since v1.7 with **ten** `TBD pending
Phase 35` cells in `v1.7-SHIELD-REVS.md` §4/§5 — two `Rev 0 → Modified Rev 0` rows of five cells
each — blocked all that time on operator photos. v1.34
photographs the board, traces each cut and jumper against the upstream Rev 0 schematic (blob
`d2a7f691`), and fills those cells.

**Merge posture.** v1.34 closes with a signed-off evidence table and an explicit merge
recommendation. **It does not merge.** Precedent since v1.21 puts every outward-facing step behind
the operator, and a merge to `beta` auto-fires a pre-release cut — not something to trigger as a
side effect of a bench milestone.

**Deliberately out of scope.** Three seeds triggered at activation and all three were declined to
keep v1.34 a regression gate: white-box voltage calibration, the Rev 2.2 3-pin header / 2516-family
support, and the per-pin-map jumper table. They stay planted, untouched.

## v1.33 Archive: Source Hygiene & Firmware Size Reduction — Shipped 2026-08-24

**Started:** 2026-08-22 · **Phases continue at 154** (v1.32 ran 147–153; the vacated **150** slot and the
v1.24–v1.29 version slots stay unreused so every by-number cross-reference keeps resolving) · **Six phases,
154–159** · **Phase 154 is dual-repo lockstep; Phases 155–158 are firmware-only; Phase 159 touches
`.planning/` only**

**Goal:** Make the source shorter without changing what it does.

**Current state (2026-08-24):** **Phase 158 COMPLETE** -- 7 plans, 7 strictly sequential waves,
verification `passed` (8/8 must-haves, each re-measured against the tree rather than read off the
summaries; the verifier independently reproduced the cold `uno` build and BOTH ARM builds byte-for-byte).
The milestone's last size lever landed and the two candidates the survey left unresolved are both settled.
`jsmntok_t` narrowed **8 -> 6 B** on AVR with `start`/`end` still signed: **-138 / -138 / -136 B flash and
-128 B RAM** cold-to-cold on `uno` / `uno328pb` / `leonardo` -- a flash **reduction**, where the scoped
prediction said *+30 B*. `scripts/baseline/size_baseline.json` is re-recorded from cold builds (`uno`
22952/1434, `uno328pb` 23000/1440, `leonardo` 25098/1875, both native envs 184/184/17), flipping
`check_size_baseline.py` default mode from every-line RED to a full `PASS:` -- one-sided by construction,
since `:697`/`:709` compare growth only, so a reduction passes with no exemption authored. The
long-standing BASE-01 mismatch is **fixed on a third axis**: its native test-inventory count re-anchored
141 -> 184 while its growth axis stayed byte-unchanged, so the canonical `--policy merge05` invocation now
exits 0 without erasing the reduction the baseline exists to catch.

**Two candidates closed by measurement, not by silence.** The `flash_5v_page_write_execute` per-byte
modulo was **DECLINED**: masking costs `+22 / +24 / +22 B` flash for 0 B RAM, and while the two
`__udivmodsi4` calls do leave the function, image-wide they only drop 11 -> 9 -- the helper stays linked, so
there is no linkage saving to buy. `flash_5v_page.cpp` is byte-unchanged. `NUMBER_JSNM_TOKENS` is closed on
the **forward-compatibility budget, explicitly not on arithmetic impossibility**: the scoped `57 tokens / 7
headroom` figure is reproducible by none of three re-derived counting rules (observed max 50/14, real pin
map 51/13, field-wise synthetic 55/9), and `64 -> 56` *is* arithmetically available -- it is declined
because unknown future wire keys need the slack, and that reason is now on the record instead of a wrong
number.

**Corrections made publicly rather than carried:** thirteen (C-1..C-13), each appended to the criterion it
corrects as a `**Correction (C-N)**` clause rather than silently replacing the stale figure -- so a reader
sees both what was predicted and what was measured. The gate story is now unambiguous for whoever moves
sizes next: `check_size_baseline.py` is invoked by **no** `.github/` workflow as a size gate, **and** its
own paired pytest does run in CI at `build.yml:161` on every branch except `beta`. Two in-tree docstrings
that asserted the inverse were corrected. Both halves are stated together, because either alone misleads.

**Coverage ceiling stated, not implied:** LAND-06's runtime half is unquantified by construction -- the
decline rests on size and on enumerated *zero* behavioural native coverage for the masked predicates (both
registered cases that execute the write path drive the same 4-byte handle and reach neither boundary
branch), not on a runtime measurement that was never taken.

**Phase 157 (Command-Decode Table + Handle Type Narrowing)**, which shipped between Phase 156 and this one,
is recorded in the footer chain below and in `.planning/milestones/v1.33-artifacts/157-after-figures.md`.

**Prior state (Phase 156):** **Phase 156 COMPLETE** -- 7 plans, 7 strictly sequential waves,
verification `passed` (4/4 must-haves, each re-measured against the tree rather than read off the
summaries). Two report blocks that were copy-pasted four times each are now one helper apiece:
`mem_util_report_voltage` (190 B, DEDUP-01, **-268 B**) and `mem_util_report_chip_id` (90 B, DEDUP-02,
**-158 B**), for **-426 B flash on all three AVR targets with RAM unchanged** (`uno` 24660->24234,
`uno328pb` 24708->24282, `leonardo` 26804->26378) -- confirming the scoped -268/-158 split exactly rather
than inheriting it. `__udivmodhi4` call sites fall **31 -> 13**. The inverted-return convention is gone:
all nine `return !op_execute_*` wrappers forward the engine result directly, six engine returns flipped,
and the ten-line comment that existed only to defend a load-bearing `!` went with them -- measured
**size-identical and deliberately NOT image-identical** (the three `.hex` SHAs change; recorded as the
expected divergence, never claimed as image identity). All four DEDUP requirements closed.
**Corrections made publicly rather than carried:** plan 01 corrected ten stale scoping figures, three
beyond the seven it expected -- `op_execute_stateful_operation.constprop.42` is 214 B not 216 B, firmware
`pytest tests/` is 348 in a canonical checkout not the 313/0/32 an isolated worktree reports (the
`META_PRESENT` seam), and the assumption that Phase 155's `46dd574` added the 31st `__udivmodhi4` site
measured **FALSE**. **The honest ceilings, stated not buried:** DEDUP-02's Divergence 1 -- the standalone
`CMD_CHECK_CHIP_ID` path refusing unconditionally regardless of `--force`, preserved by a `warn_only`
parameter rather than collapsed -- has **no test oracle**; nothing exercises `eprom_check_chip_id_execute`
on a mismatch, so its evidence is source-level only and is labelled that way at closure. Plan 04's
per-symbol ledger does not close (-356 B of symbol deltas against -158 B measured), attributed to LTO
redistribution. The new `test_boolean_convention_source_contract_v133.py` gate was proven non-vacuous
four ways, including the emptied-scan-target shape that the `MAX_27C020_SIZE` precedent fails open on.
Carried forward: `check_build_warnings.py`'s watermark now has **168 B of headroom** (998 observed vs
1166) and the gate itself asks for a re-measure -- Phase 158 / LAND-01 territory, not this phase's.
Nothing pushed.

**Earlier state (Phase 155):** **Phase 155 COMPLETE** — 6 plans, 5 waves, verification `passed` (6/6
must-haves, independently re-measured rather than trusted from the summaries). The firmware is now
**heap-free** and carries **no 64-bit runtime helper**: `check_no_heap_or_64bit_symbols.py` went from exit 1
to exit 0 with `heap=0, 64bit=0` on all three ELFs, and the image shrank **−1366 B flash / −8 B RAM on every
target** (`uno` 26026→24660, `uno328pb` 26074→24708, `leonardo` 28170→26804). All six DEAD requirements
closed. **Five figures in this project's own scoping were corrected publicly before shipping, not carried:**
the total is −1366 B and not −1364 B (the shipped guard is `k > 4194303UL`, the tighter and 2 B cheaper bound
named by criterion 4, not the `4000000UL` the survey used); the 64-bit blob is **11 symbols / 528 B**, not the
8 named / 438 B, so a gate over the named 8 could have passed with 90 B still linked; the VPP window is
**asymmetric** (−5 % low, a fixed +500 mV high), which makes the 5 mV bound a *stronger* claim because the
reformulation only ever under-reads and so can never suppress a `VPP_HIGH` error; the RAM headroom derivation
double-counted the 512 B token array (the ~470 B conclusion survives, its arithmetic did not); and the
"same statement" claim about the surviving witness was false — it is the same unconditional branch, and it was
wrong in three comment blocks. **The honest ceiling, stated not buried:** `src/boards/rurp_common.cpp`
compiles in no native environment, so the voltage arithmetic has no native and no bench coverage; it is proven
by a committed host-side numerical oracle over a stated input grid, bound to the shipped C by a
source-contract scan. avr-gcc miscompiling the 32-bit multiply/divide is named as an **unmitigated** residual
risk. `size_baseline.json` is deliberately **not** re-anchored — Phase 158 / LAND-01 owns the cold re-record.
One inherited drift carried forward to Phase 158: Phase 153 added a checker without bumping `FLOOR`, so the
tree ships 8 checkers against a floor of 7. Nothing pushed.

**Earlier state (Phase 154):** **Phase 154 COMPLETE** — 12 plans, 5 waves, verification `passed`.
The provenance sweep landed in both sub-repos as exactly one commit each (`firestarter` `2ad5b32`,
`firestarter_app` `38f0d83`), and the `uno`/`uno328pb`/`leonardo` builds are **byte-identical** to the
pre-sweep baseline — six hashes and six size figures unchanged, which is the phase's strongest oracle and
proves no executable code moved. 12 of 13 SWEEP requirements ticked; **SWEEP-13 deliberately left open**
because its one-meta-commit clause is measurably unmet (9 commits under `.planning/milestones/v1.33-artifacts`, recorded with
its cause rather than manufactured). The citation-remap tool is **built and not applied** — Phase 159
applies it once over the composite diff (D-01). Its input, the 13,692-row pre-sweep citation manifest with
**815** hand-settled `retarget` rows, is committed and cannot be regenerated after the fact.
**Measured remainder, stated not implied:** the corpus was always regex-defined, so ~152 mid-comment
provenance lines (D5) plus 236 app-pkg mid-comment and 335 non-comment-line tokens (D8) remain un-swept by
design, alongside four blob-sha-pinned paths exempted under Ruling B. This phase is **not** "all provenance
removed". Three gate-hazard classes found in flight and handed to Phases 155-158: exact-line-number pins,
`inspect.getsource()` comment pins, and provenance-label pins.
**Next:** Phase 157 — Command-Decode Table + Handle Type Narrowing (firmware-only).


Two halves that share one property: **both make the source shorter and neither changes behaviour.** Retires
Backlog **999.34**. Files Backlog **999.35** rather than carrying it.

**Target features:**

- **Provenance comment sweep + remap tool** (Phase 154, promoted Backlog **999.34**) — remove the planning
  provenance ~150 phases stamped into shipped source (**~646 comments across 167 files**; firmware ~345/94,
  host ~301/73), condensing the minority that carry load-bearing rationale into ordinary comments. **Builds**
  the citation-remap tool; deliberately does **not** apply it.
- **Dead-weight removal** (Phase 155) — the heap allocator and the 64-bit runtime, each dragged in by a
  single call site. **−1364 B flash / −8 B RAM.**
- **Duplicated-report extraction + boolean-convention repair** (Phase 156) — the VPP-report and
  chip-ID-report blocks, copy-pasted **4× each**, plus the nine inverted returns that cost zero bytes either
  way. **−426 B flash.**
- **Command-decode table + handle type narrowing** (Phase 157) — finish `json_parser.c`'s half-done refactor
  and narrow two over-wide handle fields, closing a fail-closed hole in the process. **−1148 B flash /
  −5 B RAM.**
- **Residual optimizations + cold baseline re-record** (Phase 158) — resolve the two candidates the survey
  left open and leave the gate story unambiguous for whoever moves sizes next.
- **Citation remap + close** (Phase 159) — apply the remap **exactly once** over the composite
  pre-154-to-post-158 diff, and close the staleness window it was built to bound.

**Nothing in the second half is an estimate.** Every figure was measured on real `uno` / `uno328pb` /
`leonardo` builds during the 2026-08-22 `/gsd-explore` session and validated at **172/172 native across
seven runs** plus `native_nodevtools`. Total: **−2938 B flash / −13 B RAM on all three AVR targets for a net
−2 lines of source**, and the firmware becomes **heap-free**. **Leonardo Caterina headroom 502 B → 3440 B
(6.9×)** — which matters because v1.32 Phase 151 left that target at zero MERGE-05 headroom. The work is
**already implemented** on firmware branch `size-reduction-survey` (forked off `8695ee5`) and captured as an
applyable patch, so Phases 155–158 are **review, decomposition and landing** phases, not greenfield
implementation. Evidence base, read before planning any of them:
[`.planning/notes/firmware-size-reduction-survey.md`](notes/firmware-size-reduction-survey.md) +
[`firmware-size-reduction-measured.patch`](notes/firmware-size-reduction-measured.patch).

**Scoping was done by `/gsd-explore` routing on 2026-08-22, not by this activation.** `ROADMAP.md`'s v1.33
section and `REQUIREMENTS.md` (31 requirements — SWEEP / DEAD / DEDUP / DECODE / LAND / REMAP) were
hand-authored and are pointed at, **not** regenerated: the GSD roadmap/requirements verbs normalise whole
files and would reformat six phase entries, five D-labels and 31 requirements. `/gsd-new-milestone` on
2026-08-22 contributed this section, the `STATE.md` frontmatter switch, and the commits — nothing else.

**Key decisions carried in from scoping** (full statements in `ROADMAP.md` §v1.33):

| Decision | Substance |
|---|---|
| **D-01** | Phase 154 sweeps source and **builds** the remap tool; **Phase 159 applies it once**, over the composite diff. Measured: **723** citations sit at or below an edit Phases 155–158 make and would otherwise be remapped twice (`json_parser.c` 198 of 198, `flash_utils.cpp` 97 of 97) — and **41% of that rework traces to four added `#include` lines**. |
| **D-02** | **No success criterion in this milestone requires a physical board.** Two changes have runtime consequences a bench could measure, but neither needs silicon to be *correct*. |
| **D-03** | No exemption is authored for a reduction. **MERGE-05 is one-sided** (`check_size_baseline.py:697` is `if flash_delta > allowance`), so a shrink passes with no named exemption — the first size movement in this project's history that doesn't. The pass is recorded **as** one-sided so nobody later reads a green run as "nothing moved". |
| **D-04** | **The native suite is load-flaky** — 172/172 at ~35 s (×5), 171/172 once at 1:13, 158-cases-with-2-ERRORED once at 1:44; failure correlates with run *duration*, not tree content. No phase may attribute a suite failure to its own change on N=1. The scoping session fell into this trap once itself. |
| **D-05** | The Phase-154-to-159 citation staleness is **temporary, marked, and close-blocking** (REMAP-04), not promised away. The operator ruling it bends is about *permanently* accepting staleness in closed milestones, and that reading is recorded rather than assumed. Fallback if rejected at discuss: run 155–158 first and the sweep last — a one-line reorder, deliberately left cheap to reach. |

**⚠ The one honest coverage ceiling.** `src/boards/rurp_common.cpp` compiles in **no** native environment
(`[env:native]`'s `src_filter = +<proms/>`), so the 32-bit voltage reformulation has **no native coverage**
and Phase 155 must establish it by a committed numerical oracle, naming that boundary. The survey bounds the
change at **5 mV** worst deviation against the ±5% VPP windows (±600 mV at 12 V) that consume it.

**⚠ Every gate this milestone leans on is a local-run obligation.** `check_size_baseline.py` is invoked by
**no CI workflow at all** (`grep` over `.github/` returns nothing). Separately, the canonical
`--policy merge05 --baseline .../size_baseline_base01.json` invocation is **already RED on `beta`** for an
unrelated pre-existing reason — `native: cases baseline=141 observed=172`, BASE-01 frozen at Phase 124's
count — and fails on case counts before it ever reports flash. Phase 158 owns both facts.

**Explicitly OUT of scope: replacing JSON with a binary command protocol.** Operator decision, 2026-08-22.
Measured at **−3728 B flash / −512 B RAM on `leonardo`** — the largest single saving the survey found, and
deliberately not taken here because it is a breaking cross-repo wire change rather than a refactor. It stays
queued as **v1.28** and is filed as Backlog **999.35** carrying the measurement. Two consequences that must
not be lost: it **corrects v1.28's own estimate** (the ~512 B RAM figure is confirmed exactly; the
"~1–1.5 KB net flash" is wrong by roughly 2.5×), and it **overlaps DECODE-01** — if 999.35 ever lands,
Phase 157's field table is superseded, so the two figures are **not additive** and 999.35 must be
re-measured from the post-v1.33 position before anyone quotes a combined saving.

**Branch model:** meta forked off local `beta` @ `59a9ff5d` as `v1.33-source-hygiene-size-reduction`.
Sub-repos fork off their `beta` tips per phase. **The firmware work already exists** on
`size-reduction-survey` (off `8695ee5`, i.e. `beta`'s tip plus the bot version bump) with all 11 modified
files applied but uncommitted — either rename that branch to the `v1.33-*` convention or rebase it onto the
milestone branch; the patch reproduces it from scratch if that is cleaner.

**First command:** `/gsd-discuss-phase 154` — that phase's requirements are deliberately **UNSET** because
its triage policy is the substance of the phase. Every other phase can go straight to `/gsd-plan-phase`.

## v1.32 Archive: AT28C Write-Path Root Cause & Report Provenance — Shipped 2026-08-21

**Started:** 2026-08-18 · **Phases continue at 147** (v1.31 ran 138–146) · **Mostly host-side; three
firmware-touching workstreams** — Phase 149 (the page-size seam), Phase 151 (the protection read) and
Phase 153 (the write-path erase policy) — each requiring dual-repo lockstep. *(Corrected 2026-08-21 per
152-CONTEXT.md D-15: this line originally said "one firmware-touching workstream", naming only the
page-size seam. Phase 151's protection read made it two; Phase 153's write-path erase policy, added
mid-milestone from Phase 152's discuss session, makes it three. The ROADMAP's v1.32 header already
carried the corrected count of three — this line is what catches up to it.)*

**Goal:** Root-cause the AT28C256 / protocol-`0x0D` write-path failure behind
[gh#21](https://github.com/henols/firestarter_prom/issues/21) — and *first* remove the
instrumentation defect that makes root-causing it, or any other community report, impossible.

**Base:** forked off `origin/beta` in the meta repo (`acae9161`), which carries v1.31's merged close
(PR #35). Sub-repo branches fork off their `beta` tips, which now carry v1.31 (fw PR #52, app PR #51,
both merged 2026-08-18) and the beta cut those merges fired — app **3.0.0b21**, firmware **3.0.0b19**.

**Final state at close (2026-08-21).** **6 phases executed — 147, 148, 149, 151, 152, 153 — all
`phase_complete: true` / `verification_status: passed`; 72 plans; 35/35 in-scope v1 requirements
Complete (42 defined).** Phase **150** (`write --sdp-relock`) was **deferred** on 2026-08-20 by
operator decision at its discuss step, before any research, plan or CONTEXT.md existed — no
`.planning/phases/150-*/` directory was ever created, so nothing was deleted and no plan record was
orphaned. Phase **153** was added mid-milestone from Phase 152's discuss session and **ran BEFORE 152
by design** (D-08), so 152's precondition was discharged before it started. Closeout type
`override_closeout` — Phase 150's deferral makes `ALL_PHASES_VERIFIED` structurally false, and
`audit-open` reported the same **9** pre-existing carry-forward items acknowledged at the v1.31 close,
none of whose 4 UAT/verification entries originate in v1.32. This is the **ninth** consecutive
acknowledgement of substantially that set. `milestone.complete` required `--force` for exactly and
only the Phase 150 deferral.

**How it closed.** Both sub-repos were **already fully on `beta`** before this close — merged during
Phase 152 via PR #53 in each repo, with `git cherry origin/beta HEAD` measured **empty** in both, twice,
including after each pre-release workflow's own version-bump auto-commit. **Neither was re-merged**: a
second merge would cut a second pair of pre-releases announcing nothing, under version numbers the
published release bodies do not name. The meta repository's 4-commit post-PR-#38 tail plus this close's
own commits were pushed onto `beta` directly, per `152-MERGE-RECORD.md` §TAIL. Submodule gitlinks were
re-pinned off their pre-merge milestone-branch tips (`d990a4c` / `a0bfd5e`) to each sub-repo's
`origin/beta` (`88d204a5` fw, `86f85d77` app) — the re-pin that record names the close as owning.
`git cherry` was the sole ancestry oracle throughout; `--is-ancestor` was deliberately not used,
because v1.30's squashed PR #44 already produced one false negative in this project. Pre-releases cut
during Phase 152: app **3.0.0b23**, firmware **3.0.0b20**. **Stable remains operator-gated.**

**What it did NOT do, stated with equal weight.** The evidence ceiling held from open to close: **no
AT28C part has ever been in operator inventory**, `0x0D` stays **`UNVERIFIED`**, no `support_status`
field moved (machine-checked; `chip_database.json` byte-unchanged), **no bench-validation phase existed
in this milestone by design**, and gh#21 / gh#11 / gh#12 are all still **OPEN**. A code fix is not a
validation. Backlog **999.29** — the AT28C256 write-path failure itself — is **open, partially
addressed and explicitly NOT retired**: v1.32 removed the blocker to diagnosing it and answered it
publicly, but did not diagnose it. Backlog **999.28** (`write --sdp-relock`) was **not folded** and is
deferred a second time, so for a second release running there is no supported way to deliberately
protect an SDP part. Full carry-forward register: `STATE.md` §*Deferred Items — acknowledged at v1.32
milestone close*; honesty ledger: `152-LEDGER.md`; erase-policy record: `153-RECORD.md`.

**The milestone-level non-claim, stated once here in this milestone's own canonical wording:**
**no AT28C part was tested**, at any point, by any phase — protocol `0x0D` stays UNVERIFIED in
PROTOCOL-LEDGER exactly as it stood at the open, and every write-path change v1.32 shipped is
**software-proven and unvalidated on silicon**.

### The finding that opens this milestone

`devtest-triage` cross-checked AT28C256 against Atmel/Microchip DS20006386B and cleared the data
outright: all 28 pins of `DIP28_28C256` agree with the datasheet, `infoic_page_size_raw: 64` is
exactly the datasheet's page register, `chip_id_check: false` is correct (the part has no factory
signature), and the database already asks for SDP disable-before / enable-after. It handed the
question to root-cause as a host/firmware problem, not a database one.

Root-cause then found the reason that question cannot currently be answered:

**`cli_handlers.py:2503` hardcodes `fw_board_identity=None`.** The comment is honest about why —
`EpromOperator.comm` is a transient per-operation connection torn down after every operator call, so
there is no live comm to read `programmer_info` off of without opening an extraneous connection and
violating the orchestrator-only contract (SAFE-02). The consequence is that **every `dev test` report
ever filed carries `fw_board_identity: null`**. gh#21 and gh#32 both report host `3.0.0b15` and an
unknown firmware. They therefore cannot be distinguished from a board running pre-Phase-117 firmware
that lacks the entire `0x0D` fix stack — FIX-01 (the remap-aware emitter that closed the `/WE`-inhibit
defect across 66 of 84 `0x0D` chips), FIX-03 (A16–A18 upper-address staleness), FIX-06 (the
completion-vs-data-landed conflation that *is* gh#11's shape). Attribution is impossible, and no
amount of bench work fixes that.

This is why report provenance leads the milestone rather than trailing it: it is host-only, needs no
AT28C part, and unblocks attribution for every future community report, not just this one.

### Target workstreams

| # | Workstream | Surface | Bench |
|---|---|---|---|
| 1 | **Report provenance** — `dev test` reports must name the firmware they ran on | host | no |
| 2 | **`0x0D` data defects** — `vcc: "4V"` decode bug (datasheet is 4.5–5.5 V); `protect_on_after: true` is dead data since v1.30 deleted the lock surface | `build_db.py` | no |
| 3 | **Firmware page-size seam** — deliver `infoic_page_size_raw` through wire → `json_parser` → handler, replacing the hardcoded `PAGE_SIZE 64` | firmware + host | partial |
| 4 | **Close the AT28C book** — ~~land `write --sdp-relock` (Backlog 999.28)~~ **⏸ the relock half DEFERRED 2026-08-20 → back to Backlog 999.28** (see the deferral record below). **The write-path half of that book is now closed by workstream 7 (Phase 153)** — the relock half alone stays deferred, so this row's deferral must not be read as nothing having shipped for the AT28C family. What remains here is posting the owed gh#12 reply (v1.30's CLOSE-06, open by design), which must now state a **second withdrawal**, not a migration | host + outward | no |
| 5 | **`lock-status` command** (seed) — hand-curated family-level protection table + `dev lock-status <chip>` (beta-only; corrected from the seed's top-level `firestarter lock-status` by Phase 151's OD-1) | host + firmware | partial |
| 6 | **Numeric DB values** (seed) — voltages/timing as mV / µs integers, deleting `database.py`'s coercion layer | host | no |
| 7 | **Write-path erase policy** — no pre-write blank check on the two auto-erasing protocols (`0x0D`, `0x05`); a standalone software chip erase on `0x0D` (added mid-milestone from Phase 152's discuss session, D-07) | firmware + host | no |

Workstreams 2 and 6 touch the same field (`electrical.vcc`) and must land together — numericalising
`vcc` to `vcc_mv` turns the `"4V"` → 5 V correction into a value change rather than a string edit.
*(Corrected 2026-08-19 per Phase 148 D-01/D-02/D-04: this read "→ 4.5 V". `4V` is a **faithful**
decode of `infoic.xml`'s VCC nibble `2`; the defect is semantic — it is the TL866's verify-margin
rail surfaced as the operating supply — so the correction is a margin-rail substitution to the
already-decoded `vdd` (5000 mV), and 4500 mV is a value `infoic.xml` does not carry for these
parts.)*

**Workstream 1 delivered — Phase 147 complete 2026-08-18** (6 plans, 4 waves; PROV-01…PROV-06 all
ticked, verification `passed`). `cli_handlers.py`'s hardcoded `fw_board_identity=None` is replaced by a
real prerelease-preserving identity captured inside the orchestrator contract (SAFE-02 intact — `comm`
stays a transient per-operation connection); the report schema is at 1.4 and still parses older
`null`-carrying reports; and an absent identity now renders as an explicit `not reported` marker plus a
not-attributable clause naming the next action, across all three surfaces — the report model, the app's
`[dev test]` parser, and the `devtest-triage` skill's `show` render. Per D-01 the dependency spine is
now in place: a future `dev test` run is self-identifying, so any write-path work can be attributed to
a firmware version. **This changes nothing about the write path itself** — `0x0D` remains `UNVERIFIED`
and gh#21/#32/#11/#12 remain OPEN, exactly as the evidence ceiling requires.

**Workstreams 2 and 6 delivered — Phase 148 complete 2026-08-19** (8 plans, 8 sequential waves;
DATA-01…DATA-05 all ticked, verification `passed` 5/5). They landed together as D-02 required. The
generated database now states each electrical and timing value **once, as an integer in one unit**:
`vcc_mv` / `vdd_mv` / `vpp_mv` in millivolts and `pulse_duration_us` in microseconds, across **both**
emission paths (`build_db.py`'s decode loop *and* the authored `tools/extra_chips.json` supplement).
`interpret_timing()` now raises on a decode fault instead of shipping a silent wrong `0`. Both live
string parsers are **deleted, not bypassed** — `database.py`'s `.replace("V","")` → `float()` and
`_parse_pulse_duration`, and `audit_coverage_matrix.py`'s `parse_pulse_us` (zero hits repo-wide) —
with one shared `format_mv` helper owning all three display sites.

The AT28C correction landed exactly as D-02's proof rule demands. `firestarter info AT28C256` now
reports **5.0v**, via a post-construction margin-rail substitution keyed on the **decoded value
alone** (`vcc_mv == 4000` → that chip's own `vdd_mv`) — no part number, no type, no algorithm, and
the decode table itself byte-unchanged. Measured blast radius: **exactly 56 chips**, every one
4000 → 5000 mV, zero decreases, published per-chip through a new `RULE_VCC_MARGIN_RAIL` bucket in
`diff_db.py`. GATE-03 reports zero violations with `check_dispatch.py` byte-unchanged. A 746-chip
host→wire capture taken *before* any edit proves the migration never changed what reaches the
firmware. A 28-chip (16+12) high-margin 5500 mV group is deliberately deferred, filed with its exact
part list.

**This too changes nothing about the write path.** `0x0D` remains `UNVERIFIED`; the AT28C data was
already cleared by `devtest-triage`, and this phase corrected how that data is *represented and
reported*, not how the part is programmed. gh#21/#32/#11/#12 stay OPEN.

### Evidence ceiling — binding, not decorative

**There is still no AT28C part in operator inventory** (recorded 2026-08-04, re-confirmed at this
milestone's kickoff). This caps what v1.32 may claim, in the same shape as v1.22 and v1.30:

- `0x0D` stays **`UNVERIFIED`** in `PROTOCOL-LEDGER`. No phase may graduate it.
- gh#21, gh#32, gh#11 and gh#12 stay **OPEN**. A code fix is not a validation; only a fresh passing
  `dev test` on real silicon closes them, and only `devtest-triage` closes them.
- The honest outward-facing outcome is a corrected code path plus a request to the reporter for a
  fresh run — now answerable, because workstream 1 makes that run self-identifying.
- The firmware page-size change (workstream 3) cannot be validated without a part. It ships
  software-proven and says so.

### Decisions taken at kickoff

- **D-01 — provenance leads.** Workstream 1 is the dependency spine. Fixing it after the write path
  would leave the write-path fix unattributable to any firmware version, including our own.
- **D-02 — the proof rule holds for the `vcc` fix.** `chip_database.json` is generated. The VCC
  correction lands in the decode function in `build_db.py` and is proven by `diff_db.py`; a one-chip
  fix that moves hundreds of chips means the decode change was too broad. No per-chip guess table,
  no `_PAGE_SIZE_BY_PART` sibling. *(The kickoff text read "The 4.5 V correction"; corrected
  2026-08-19 per Phase 148 D-01/D-02/D-04 — the target is 5000 mV, the already-decoded `vdd`, not
  4500 mV. **This decision's own proof rule is unchanged and is what surfaced the error**: 4500 mV
  cannot be traced to an `infoic.xml` attribute, and the measured blast radius of the adopted rule
  is exactly 56 chips.)*
- **D-03 — `protect_on_after` is reconciled, not deleted.** The bit is a faithful decode of
  `infoic.xml` flags bit 15 and stays. What changes is that the system stops silently ignoring it —
  workstream 4 gives it a consumer. *(Amended 2026-08-20 with the Phase 150 deferral: workstream 4's
  consumer branch is gone, so "stops ignoring it" is discharged by **documentation** in Phase 151
  instead. D-03's substance is unchanged — the field stays, and the system stops being silent about
  it; only the discharge mechanism narrowed, and the choice was closed by the deferral rather than
  taken afresh.)*
- **D-04 — `lock-status` is hand-curated by proven necessity.** The 2026-07-10 research established
  that `infoic.xml` cannot supply protection readability: W29C020C (readable permanent boot block)
  is flag-identical to W29EE011 (SDP-only, unreadable). The hand-curated table is not a violation of
  the proof rule; it is what the proof rule leaves when upstream genuinely lacks the field.

**~~Folds Backlog 999.28~~** (`write --sdp-relock`, promoted to Phase 150) — **⏸ NO LONGER TRUE as of
2026-08-20; see the deferral record below.** **Backlog 999.29**
(the AT28C256 write-path failure itself) is **partially addressed and NOT retired**: v1.32 removes
the blocker to diagnosing it and answers it publicly, but under the Evidence Ceiling it does not
diagnose it. That item stays open with the operator as its named owner. Consumes the `lock-status-command-hand-curated-protection-table` and
`db-numeric-values-simplification` seeds.

### ⏸ Phase 150 (`write --sdp-relock`) DEFERRED — 2026-08-20, operator decision

**Deferred at the discuss step**, during `/gsd-discuss-phase 150` and before the gray-area selection was
answered. **Nothing was created**: no `.planning/phases/150-*/` directory, no CONTEXT.md, no research, no
plans, no commits in either sub-repo. Operator's words: *"I don't want the relock implementation right
now. I will implement it later if it is requested later."* It returns to Backlog **999.28**, so **v1.32
no longer folds that item**.

**This is the second deferral of the same work** — scoped as v1.30 **Phase 135**, deferred 2026-08-03;
promoted 2026-08-18 as v1.32 **Phase 150**; deferred again 2026-08-20. Both vacated phase numbers (135,
150) stay unreused so by-number cross-references keep resolving.

**What moved:**

- **RELOCK-01…06 and RELOCK-08 leave v1 scope** → Backlog 999.28. v1.32 goes from 33 to **25** v1
  requirements. Their text in `REQUIREMENTS.md` §RELOCK is unmodified — only the checkboxes changed
  `[ ]` → `⏸` — so nothing needs re-authoring at a future promotion. RELOCK-07 is unaffected (it
  shipped in v1.30 Phase 137).
- **DATA-06 is RETAINED and re-homed to Phase 151**, resolving on its **documented-advisory** branch.
  That branch was closed by the deferral, not chosen afresh, so D-03's "decided once" property holds
  and Phase 151 is now the only phase that may write about `protect_on_after`. Keeping it in scope is
  deliberate: deferring it too would leave the field dead data for a second release, which is the
  precise thing it exists to stop.
- **Phase 151's dependency on Phase 150 is discharged** — LOCK-03 refuses on every `0x0D`/SDP family
  regardless of whether a lock can be created, so `lock-status` always stood alone. Phase 151 also
  inherits `firestarter_app/firestarter/cli_handlers.py` as the milestone's sole remaining writer.

**The accepted cost, and the outward-facing obligation it creates.** v1.30 shipped the deletion of
`dev sdp enable|disable` without its replacement and recorded that as a cost; **v1.32 was the milestone
scoped to close that gap and does not.** So since 2026-08-05, and continuing past v1.32, there is **no
supported way to deliberately protect an SDP part** — and on `0x0D` the protection bit cannot be read
back, so a user cannot observe the state either. Consequently **Phase 152's OUT-01 and OUT-04 were
amended on 2026-08-20**: both were authored naming `write --sdp-relock` as shipped, and both must now
describe a **withdrawal, never a migration**, naming Backlog 999.28. OUT-05's fail-provable claim gate
gained a **fifth claim class** rejecting any outward text that names the command as shipped or
available — and the pre-amendment criterion-1 wording this project's own roadmap carried until that
date is the planted violation the gate must be seen to reject. Announcing a command absent from the
release announcing it is the overclaim class v1.22's C-5 correction and v1.30's CLOSE-05/06 amendment
both exist to prevent; getting it wrong here would be the milestone failing its own stated purpose in
its most public artifact, for the second release running.

**Measured findings from the abandoned discussion are preserved in ROADMAP §"Phase 150"** so a
re-promotion needs no fresh archaeology — the `protect_on_after` distribution (70/746 true; 43 of 84
`algorithm: 13`; **27 of 27** `algorithm: 5`, i.e. a constant there), its `MP_PROTECT_AFTER`
capability-not-policy semantics, the machine-proven element-wise equality with `sdp_capability`'s
transcription, the `check_sdp_capability_invariants.py` Class 2(b) constraint that blocks a runtime
field read, the true `write --help` pin locations (two syrupy snapshots in `test_characterization.py`,
**not** Phase 136's channel-gating tests), and the `logger.warning`-emits-no-prefix trap behind
RELOCK-04's literal `WARNING:` requirement.

## v1.31 Archive: 27C Programming-Algorithm Fidelity (gh#15) — Shipped 2026-08-18

**Started:** 2026-08-08 · **Phases continue at 138** (v1.30 ran 131–134, 136, 136.1, 137; the 135 slot
stays vacant and is not reused) · **Firmware-touching, dual-repo lockstep** (`firestarter` +
`firestarter_app`).

**Current state (2026-08-14):** Phases 138–144 complete and verified. **Phase 141 (Per-Byte Program
Loop) CLOSED — 9 plans in 5 waves, verified 5/5 success criteria, LOOP-01…LOOP-08 all Complete.** The
milestone's central change has landed: `eprom_write_execute` is now a per-byte fixed-width pulse→verify
loop, and `program_mismatched_bytes()`, `verify_and_update_mask()`, `NUMBER_OF_RETRIES` and the adaptive
`pulse_delay = org + org*retries/20` growth are **gone from the write path** (grep-verified absent across
`src/` and `include/`). `delayMicroseconds` no longer appears in `eprom.cpp` at all — both former
over-ceiling sites route through the new 32-bit-safe `mem_util_delay_us`. Evidence: `native_loop_v131`
(the sixth native env) 39/39, firmware pytest 256, both pinned native envs 141/17, host suite 1547, all
three AVR targets building.

**Two disclosed limits, recorded rather than smoothed** (see `141-LOOP-RECORD.md`): (1) the **MERGE-05
flash-band policy is RED** on all three AVR targets — uno +492 B, uno328pb +498 B, leonardo +328 B against
a 64/64/0 B band — accepted by explicit operator decision as finding **F-141-01**, not remediated. RAM is
exactly unchanged. Roughly +204 B of the overrun is Phase 140's parameter table finally linking now that
`eprom_params_for` has its first `src/` caller; the 64 B band was set in Phase 123/124, before that table
existed. Leonardo now sits at **92.1%** flash (2272 B headroom) — a real constraint on Phase 142.
(2) two goal criteria are proven **narrower than they read**: the overprogram pulse is proven only on the
pure `eprom_overprogram_us` function because `overprogram_factor` is 0 on every shipped row, and LOOP-06's
read-skip holds only on `0x0B`, since `0x07`/`0x08` ship `VERIFY_PER_PULSE_PLUS_FINAL` whose final pass
re-reads every byte unconditionally. The *pulse* skip LOOP-06 actually requires is universal.

`pio test -e native_trace_v131` is deliberately RED on 3 of 6 cases (frozen pre-change trace vs the new
cadence, D-10); `141-NEW-TRACE.md` captures the post-change side so Phase 144 / TEST-06 owns the re-freeze
and the diff. `native_loop_v131`, `native_params_v131` and `native_trace_v131` run in **no CI leg of
either repo** — local run-by-name obligations, never implied coverage.

**Phase 142 (High-Voltage Routing) CLOSED — 7 plans in 6 waves, verified 17/17 must-haves, VPP-01…VPP-04
all Complete.** Route selection for all three 27C protocols now resolves in exactly one function,
`eprom_hv_route_mask()`, driven by the parameter table's `vpp_path` column and exposed via `eprom.h` so
both `eprom_check_vpp` and the write path call it — tier-1 protocol-keyed sites in `eprom.cpp` fell
**3 → 1** (only the pulse-fallback switch survives, which D-01 forbids touching). `--vpe-as-vpp` still
overrides on top. Two conditional single-exit wrappers make "disable every high-voltage route" structural
on every error exit rather than a thing each `return` must remember; the final-pass `MSG_ERR_VERIFY` exit
disabled **nothing** before this phase, confirmed by diffing against the Phase 141 tip. A successful block
still deliberately stays energised so the once-per-block settle is not re-paid. `mem_util_calculate_top_address_register`
now preserves the VPE-to-VPP drop bit for 32-pin parts on Rev 2-class hardware alone; the `pins >= 32`
clear and the dead regulator helper are deleted. Evidence: `native_loop_v131` 71/71, firmware pytest 272,
both pinned native envs 141/141, all three AVR targets building. **No new message id — `0xBF` stays free
for Phase 143.**

**Three limits recorded rather than smoothed** (see `142-VPP-RECORD.md`): (1) **MERGE-05 stays RED** and
remains finding F-141-01 — not remediated. Phase 142 spent 142 B of leonardo flash, leaving **92.6%
(2130 B headroom)**; uno 24568 B, uno328pb 24618 B. (2) Two goal criteria are proven **narrower than they
read**: drop-bit *survival* across a block is Rev-2-class-only (Rev 0/1 share a physical register bit),
and "success" for the disable guarantee is satisfied at the operation level via `command_done()`, not per
block. (3) `command_done()`'s zeroing guarantee is asserted as a **source contract**, not a behavioural
one, because `firestarter.cpp` sits outside every native `build_src_filter` — a behavioural oracle would
need a seventh env. `native_trace_v131` remains deliberately RED (D-17) and moved only on the `0x08` row.

**Phase 143 (Host Timeout, Progress & Pulse Override) CLOSED — 10 plans in 5 waves, verified 5/5 success
criteria, HOST-01…HOST-05 all Complete.** Dual-repo, and the first phase this milestone whose host half
carries real weight. **BF-1 closed:** the v1.31 firmware branch forked one commit before firmware PR #49,
so it had no CAP-02 identity tail and the v1.31 app **refused every connection to a v1.31 build** —
CAP-02 is now ported and CAP-03 appended in one pack block emitting
`[buffer u16][hw_rev u8][ver_len u8][ver bytes][budget u16]`, budget at the computed `4 + _vlen`.
The firmware advertises a per-block worst-case write time computed from Phase 140's parameter table plus
the live pulse width; the host decodes it at the computed `ver_end` under a derived `[1, 14400]` clamp and
uses it **verbatim** as the write-path response timeout, falling back to a derived 120 s when none is
advertised — threaded as a default-`None` kwarg so `verify_eprom` stays byte-identical on the old 10 s
default. `MSG_DATA_PROGRESS` is emitted time-gated at 1000 ms from inside the per-byte loop and rendered
host-side without acking, positioned at `absolute − start_addr`, never rebuilding the bar, latched so it
cannot rewind. `0xBD`/`0xBE`/`0xAE` now surface as `EpromOperationError` naming the address, with a hint
stating the abort's disposition and offering no retry. `firestarter write --pulse-us N`
(`click.IntRange(1, 65535)`, `default=None`, `write`-only) rides the existing `pulse-delay` wire field and
always prints a provenance line. The budget arithmetic lives in a new, unpinned `src/proms/eprom_budget.{h,cpp}`
TU so it gets a real native unit-test oracle. Evidence: firmware pytest **292**, host suite **1578**
(82.92% coverage), `native_loop_v131` 79/79, both pinned native envs 141/141, all three AVR targets
building. **No new message id — `0xBF` is still free.**

**Four limits recorded rather than smoothed** (see `143-HOST-RECORD.md`): (1) the honest headline is
*a long write now reports what it is doing, and a failed byte now reports as a failed byte* — **not**
faster, **not** more reliable, and **no bench evidence** (Phase 145 owns that). (2) Progress delivery is
**`leonardo`-only**: the emit and its `millis()` state variable are both inside `#ifndef SERIAL_ON_IO`
because on `uno`/`uno328pb` the 4-slot deferred-log buffer would overflow and silently drop the following
`MSG_ERR_MAX_PULSES`, converting a program failure into a transport timeout — HOST-03's exact anti-goal, on
a path that works today (**BF-2**, so D-02 shipped scoped down, pinned by a source-contract gate since
`uno_rurp_shield.cpp` is compiled in no native env). Uno-class flash came out byte-identical, proving the
guard really excludes the code. (3) **D-11's formula was replaced, not implemented** — it under-estimated
**2×** at `--pulse-us 49999` on `0x0B` (true bound 99 998 µs, not 50 000), which would have spuriously
timed out a *working* write (**BF-3**). (4) **MERGE-05 stays RED** and remains F-141-01 — not remediated;
`check_size_baseline.py` is operator-accepted RED for the enumerated reasons only (F-141-01, the OD-2
CAP-02 `+34 B` drift, and this phase's growth against a deliberately un-updated baseline), with leonardo
fitting at **26906/28672 B (93.8%, 1766 B headroom)**. `native_trace_v131` remains RED by design (D-24)
with **zero** frames added. Recorded and operator-approved at 143-10's blocking gate: the CAP-02 port is a
**re-implementation citing `13eb350`**, not a cherry-pick. D-01's ROADMAP-prose correction (this phase is
*not* independent of 140–142) is DISCHARGED AT Phase 146, plan 146-05 — see
`phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/146-CORRECTIONS.md` rows C-1/C-2. This
sentence itself carries no false statement (research measured zero PROJECT.md hits for the independence
clause); it is a true routing note now updated from forward-looking to discharged.
**Phase 144 (Tests & Build Verification) CLOSED — 7 plans in 6 waves, verified 8/8, TEST-01…TEST-08 all
Complete.** Both of the milestone's standing REDs are retired: `native_trace_v131` runs 5/5 after the
golden trace was re-frozen at this phase's tip (91/115/59), and `check_size_baseline.py` reads green —
**because the anchor moved to v1.31**, never because growth stayed inside v1.24's band.
Next: Phase 145 — Bench Validation.

**Goal:** Replace the block-level mismatch-mask write loop shared by all three 27C protocols with a
per-byte pulse→verify loop driven by a per-protocol parameter table, so `0x07` / `0x08` / `0x0B`
program the way their datasheets specify — with the pulse width supplied by the database, not by
hardcoded constants.

### Scoped from gh#15 *as corrected*, not as written

[gh#15](https://github.com/henols/firestarter_prom/issues/15) specifies this work and its architecture
is sound, but a `/gsd-explore` pass on 2026-08-08 (recorded in
`.planning/seeds/27c-algorithm-fidelity-param-table-refactor.md`, commit `c60543c5`) found **two wrong
numbers and one inverted premise** in it. This milestone implements the corrected design and posts the
corrections publicly before implementation lands.

| | gh#15 states | Correction (evidence) |
|---|---|---|
| **C1** | `0x0B` pulse = `50000 us` | **500 µs.** `50000 = 500 × 100` is the fingerprint of **BUG-2**, a ×100 multiplier `interpret_timing()` applied to `0x07`/`0x0B`, affecting 252 chips, removed in Phase 57. The shipped DB reads `500 us` for AM2716. Adjudicated at `firestarter_app/doc/infoic-field-dictionary.md:210-217`. Cross-checked: `AT28C64B` → 10000 µs = 10 ms (its datasheet byte-write); `DS1225` NVRAM → 1 µs. A ×100 would make the 28C64 1 s/byte. |
| **C2** | Hardcode `1000 / 100 / 50000 µs` into three handlers | **Pulse width is DATA, not a per-protocol constant.** Measured live against the shipped DB on 2026-08-08: `0x07` n=170 (**100 µs ×113**, 200×27, 1000×22, 500×4, 50×4); `0x08` n=127 (**100 µs ×104**, 50×11, 10×7, 200×2, 1000×2, 20×1); `0x0B` n=32 (**500 µs ×21**, 1000×6, 200×5). All three gh#15 constants disagree with the modal value. minipro ships `protocol_id` and `pulse_delay` as **two orthogonal wire fields** (`t48.c:250-267`, identical in `tl866a.c`, `tl866iiplus.c`, `t56.c`, `t76.c`) and exposes `-o pulse=N` per run — a uint16, so 65535 µs is the hard ceiling. |
| **C3** | Need a 32-bit-safe delay because of the 50 ms pulse | Helper is still needed, **for the overprogram pulse** — `3 × 25 × 1000 µs = 75 ms` exceeds `delayMicroseconds()`'s 16383 µs ceiling. With C1 applied, no *pulse* comes near it. |

**Structural consequence (D-01):** protocol owns *shape*; the database owns the *pulse*. That is a
parameter table, not three state machines — the opposite of gh#15's "each protocol must own its
timing constants". `handle->pulse_delay` stays on the write path; protocol constants survive only as
fallbacks for `pulse_delay == 0` (`eprom.cpp:70-77`).

**⚠ CORRECTION (Phase 146 / CLOSE-04, origin C3 / 141 H3) — the C3 row above ("With C1 applied, no
*pulse* comes near it") is narrower than shipped source supports; it is true of `chip_database.json`
data and false of the wire.** The `pulse-delay` wire field is parsed by the unclamped `extract_long`
macro chain (`firestarter_fw/src/json_parser.c:279-282`, invoked at `:304-306`) into `handle->pulse_delay`,
declared `uint32_t` (`firestarter_fw/include/firestarter.h:197`) — no clamp exists at parse time, so a
value above 65535 is reachable on the wire independently of the host's own `1..65535` Click bound. Two
narrowings measured this phase, neither in the inherited text: (1) an over-ceiling value is **delivered**,
not silently truncated — Phase 141's 32-bit-safe split-delay helper (`mem_util_split_delay` /
`mem_util_delay_us`, `firestarter_fw/src/proms/memory.cpp:238-251`, ceiling `MEM_UTIL_DELAY_US_MAX 16383UL`
at `:34`) now carries the program pulse (`memory.cpp:337`), so the 16-bit truncation hazard C3 describes
is mitigated, not that the value is bounded. (2) the only firmware-side refusal is `0x0B`'s pre-flight
`MSG_ERR_PULSE_TOO_WIDE` (`firestarter_fw/src/proms/eprom.cpp:90-110`), gated on `energy_cap_us > 0`; that
value ships `0` on `0x07`/`0x08` (`eprom_params.cpp:50-52`), so the unbounded path is live on those two
rows only. **This is recorded, not clamped (D-06 of this milestone) — Backlog 999.31 owns the adjacent
decision of whether to add a bound.** Register row **C-3** in
`phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/146-CORRECTIONS.md`.

**Target features:**

- **A `const` parameter table keyed by `protocol_id`** carrying **shape columns only** —
  `max_pulses`, `overprogram_factor` (0 | 3×), `overprogram_cap_us`, `verify_mode`, `vpp_path`
  (drop-resistor vs direct). **No pulse column.**
- **A per-byte pulse→verify loop** replacing `program_mismatched_bytes()`,
  `verify_and_update_mask()`, the flat `NUMBER_OF_RETRIES = 20` cap (`eprom.cpp:20`) and the adaptive
  growth `pulse_delay = org + org*retries/20` (`eprom.cpp:177`) — which escalates pulse width where
  the datasheets hold width fixed and *count* pulses. Pulse count and overprogram duration belong to
  the individual byte, which the block mismatch-mask cannot express; this is gh#15's central and
  correct insight.
- **Overprogram pulse** — `3 × N × pulse` capped at 75 ms where `overprogram_factor > 0`. Correct for
  older Intel "Intelligent" 27C parts; **not** for Quick-Pulse / Flashrite / PRESTO, so it is gated
  per row and never applied blanket.
- **`0x0B` energy-budget cap (D-02)** — the one-shot-vs-looped question is *not answerable from
  source*: minipro never runs the algorithm, it packs `pulse_delay` into a `BEGIN_TRANS` message and
  hands it to closed TL866/T48/T56/T76 firmware. Resolution shipped: loop pulse→verify but **cap
  accumulated program time per byte at 50 ms**, since `100 × 500 µs = 50 ms` is exactly the classic
  2716 total programming time. Early-verifying bytes exit fast; stubborn bytes still receive the
  datasheet's full energy budget. No overpulse on this row.

  **⚠ CORRECTION (Phase 146 / CLOSE-04, origin F-140-07) — the "classic 2716 total programming time"
  justification above is factually wrong; the cap value it justifies is not.** The TI TMS 2516
  datasheet states its own total programming time for all bits as **100 seconds**
  (`140-PARAM-TABLE-RECORD.md:259` cites the figure); 50 ms is that same datasheet's *per-location*
  pulse width (`t_w(PR)` TYP 45/**50**/55 ms), not a total. The **value** `energy_cap_us = 50000UL`
  keeps its genuine primary-datasheet basis; only the published **reason** is corrected here. Four
  sites carried this text: the posted gh#15 comment (public, owed by plan `146-12`), this bullet,
  `.planning/REQUIREMENTS.md`'s D-02 rationale cell (owed below in the same commit), and two dated
  sites recorded rather than edited — `.planning/PROJECT.md:1187`'s v1.31-start footer and
  `.planning/STATE.md:67` (history; block-versus-history rule). **`firestarter_fw/doc/PROTOCOLS.md`
  §1.5 already carries this same correction in place, landed by the Phase 140 record (140-06) —
  this phase records that discharge rather than repeating the edit.** Register row **C-6** in
  `phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/146-CORRECTIONS.md`.
- **Safe 32-bit delay helper** — split ms/µs portions; never a bare `delayMicroseconds(75000)`.
- **VPE held across the block (the enabler).** Per-byte verify looks unaffordable because
  `eprom_write_execute` pays a `delay(10)` VPE settle (`eprom.cpp:114`) — per byte that is
  512 × 10 ms = **5.1 s of pure settling per block**. It does not have to be:
  `rurp_chip_enable`/`rurp_chip_output` are dedicated pins (`rurp_shield.h:114-134`) and
  `mem_util_calculate_top_address_register` preserves the HV mask across **every** `set_address`,
  read path included (`memory.cpp:163-166`). VPE survives a read, so the settle stays amortized once
  per block — matching the datasheets, which verify with VPP still applied (CE high, OE low).
  **Caveat:** for `pins < 32` the mask also preserves `CTRL_VPP_VPE_DROP_ENABLE`; on DIP32 that bit
  *is* A16, so the drop path cannot be held across arbitrary addresses there (DIP32 uses
  `CTRL_VPP_P1_ENABLE` instead).
- **VPP routing protocol-correct and disabled on every exit** — including verify failure. `0x07`/`0x08`
  regulator + VPE-to-VPP drop; `0x0B` direct legacy path; shared masks used by `eprom_check_vpp()` and
  all write/error paths alike.
- **Host: long-block handling.** Worst-case blocks exceed `DEFAULT_RESPONSE_TIMEOUT = 10`
  (`firestarter_app/firestarter/serial_comm.py:66`) — reachable only on failing silicon, but it
  converts "chip is marginal" into "serial timeout", destroying the diagnostic. Precedent for the
  fix: the blank-check progress/chunk pattern at `memory.cpp:307-312`.
- **gh#15 corrected outwardly, early (D-03).** C1/C2/C3 plus the 6.25 V amendment posted as a comment
  *before* implementation phases run, on the v1.30 CLOSE-06 pattern: drafted, frozen, operator-approved,
  posted only on explicit authorization. Stops anyone implementing `50000 us`.
- **Claim gate + honesty ledger.** A committed `check_permitted_claims.py` forbidding unqualified
  "datasheet-conformant" / "datasheet-correct" / "algorithm-accurate" across all closing artifacts,
  plus a ledger pairing every permitted claim with its explicit non-claim — the v1.22 / v1.23 / v1.30
  pattern.

**Expected throughput (512-byte Uno block), from the research:**

| algorithm | pulse | max pulses | overpulse | typical | worst case |
|---|---|---|---|---|---|
| `0x07` | `handle->pulse_delay` | 25 | `3 × N × pulse`, cap 75 ms | ~0.25 s @100 µs; ~2.05 s @1000 µs | ~51 s |
| `0x08` | `handle->pulse_delay` | 25 | `3 × N × pulse` | ~0.2 s | ~13 s |
| `0x0B` | `handle->pulse_delay` | 50 ms energy cap | none | ~0.8 s | ~25.6 s |

**⚠ CORRECTION (Phase 146 / CLOSE-04, origin F-140-05) — the table above's `overpulse` column is false
for BOTH the `0x07` and `0x08` rows, not the one CONTEXT names; a third cell conflates two columns.**
The shipped table (`firestarter_fw/src/proms/eprom_params.cpp:49-53`, columns per
`include/eprom_params.h:51-58`) sets `overprogram_factor = 0` on **both** `0x07` and `0x08`
(`max_pulses` 25 each) — not `3 × N × pulse` as both rows above state. This is not an inference: the
shipped source names the contradiction in its own comment (`eprom_params.cpp:41-43`), *"0x08
overprogram_factor = 0 resolves D-06 from primary datasheets, agreeing with PROJECT.md's prose and
CONTRADICTING PROJECT.md's own throughput table — the contradiction is named here, not smoothed."*
Their `worst case` figures (`~51 s`, `~13 s`) were computed **with** the overpulse and so err
conservatively, not falsely low. The conditional prose above this table
("Overprogram pulse — `3 × N × pulse` capped at 75 ms **where `overprogram_factor > 0`**") is correct
and needs no correction. **Third defect:** the `0x0B` row's `max pulses` cell reads "50 ms energy cap",
conflating that column with `energy_cap_us`; the shipped `max_pulses` value on that row is **255**
(`eprom_params.cpp:52`). Register row **C-5** in
`phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/146-CORRECTIONS.md`.

**Faster than today in the typical case** — the current code can make 20 full block passes.

**⚠ CORRECTION (Phase 146 / CLOSE-04, origin OD-B, surfaced not decided by 146-RESEARCH.md §"(5)") —
the sentence above is a comparative claim this milestone's own bench boundary forbids.** No control
run of the pre-change block-mismatch-mask loop exists in this milestone's evidence, so "faster ... than
today" cannot be measured here — `145-BENCH-LOG.md`'s "Boundaries" §1 (`:2701-2707`) is explicit that no
before/after comparison was run. The historical write figure that could read as a baseline is recorded
at `145-BENCH-LOG.md:2702`, a *"recorded historical number, not a control measurement"*, deliberately
not restated by numeral here. This sentence is scoping-era intent prose written before any code moved;
it stands corrected here because the next milestone's scoping pass reads it as PROJECT.md's live
record. Register row **C-8** in
`phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/146-CORRECTIONS.md`.

**Evidence ceiling — fixed up front, before any code moves:**

- **The 6.25 V program-VCC is unreachable on this shield.** All four vendor algorithms assume ~6.25 V
  program-VCC for threshold margin; the RURP has no VCC-raise path. Firmware fidelity buys
  *timing / pulse-count / verify* correctness but **not** silicon-margin fidelity. This is
  hardware-bound, best-effort, the same shape as prior hardware-bound graduations — and **gh#15 omits
  it entirely**, so its acceptance criteria imply a fidelity unreachable on this hardware. The gate
  exists to stop that overclaim escaping.
- **Bench coverage is asymmetric by inventory (operator, 2026-08-08).** `0x07` is **bench-required**
  (W27C512 / TMS27C512, both 100 µs). `0x08` (AM27C020) and `0x0B` (M2716 / M2732, 25 V NMOS, needs
  the Phase 79 VPE path) are **opportunistic** — validated if the parts materialize, otherwise
  **skipped-with-reason**, never rubber-stamped. AM27C020 is known marginal from v1.18 Phase 99
  (write#1 60/64, write#2 0/64, suspected VPP droop), which makes it a stress case rather than a
  pass/fail oracle.
- **Not behavior-preserving.** This changes *how* bytes get programmed. Golden traces and
  bench-verified write results that encode the current pulse cadence will legitimately shift;
  re-baselining is expected work, not a regression. Native tests alone cannot close this — per-family
  on-bench re-verification (Leonardo) is required for what silicon is available.

**Version, slot and branch model.** Takes **v1.31**, the next number after the shipped v1.30. Backlog
**999.22** (queued as `v1.27`) is **retired into this milestone**; `v1.24` (Bus-Config Mask-Model),
`v1.25` (Jumper-Display / 2516) and `v1.26` (White-Box Voltage Calibration) are left **byte-unchanged**
so every by-number cross-reference in the seeds, notes and todos keeps resolving — the v1.23 Phase 130
precedent. **Blocking precondition (operator, 2026-08-08):** `firestarter_app`'s
`gsd/v1.30-sdp-surface-retirement` must be merged to `origin/beta` *before* v1.31's app branch forks,
so the host line stops diverging and v1.30's shipped record becomes true. Firmware forks off `beta`
(clean at `3085084`). Meta forks off the v1.30 tip.

**Explicitly out of scope:**

- **Any new database algorithm field or second firmware algorithm selector** — gh#15 is explicit and
  correct here: `protocol_id` stays the single source of truth. The parameter table is keyed by it,
  not a substitute for it.
- **A VCC-raise path** — hardware, not firmware; recorded as accepted debt, not attempted.
- **True PRESTO margin verification** — documented as not-yet-implemented if the RURP cannot expose
  the required verify mode.
- **Erase, blank-check, chip-ID, bus remapping and VPP validation behavior** — unchanged except where
  a change is required for safe shared cleanup.

## v1.30 Archive: SDP Surface Retirement & Behavioral Lock Proof — Shipped 2026-08-05

**Status (2026-08-05): 7 phases (131–134, 136, 136.1, 137), 48 plans, 55/56 requirements — CLOSE-06 held open by design** (the gh#12 reply is frozen and approved but deliberately unposted; the exact closing command is recorded in `REQUIREMENTS.md` and `v1.30-OPERATOR-BATCH.md`). Phase 135 (`write --sdp-relock`) was deferred out to Backlog **999.28** and its number is not reused. **⚠ Open at the time v1.31 was scoped:** `firestarter_app`'s `gsd/v1.30-sdp-surface-retirement` is **not merged into `origin/beta`** — the PR was staged (`.planning/milestones/v1.30-PR-BODY.md`) but never opened. v1.31 Phase 138 lands it before any host work forks. Full entry: `.planning/MILESTONES.md` §v1.30.

**Started:** 2026-08-03 · **Phases continue at 131** (v1.23 ran 123–130; no micro-phases inserted) ·
**Host-only** (`firestarter_app`), no firmware change, no dual-repo lockstep, no `.hex` re-cut.

**Goal:** Replace v1.22's unverifiable standalone `firestarter dev sdp <chip> enable|disable` with a
**self-verifying** SDP lifecycle whose oracle is read-back equality rather than an exit code — and,
while the same host files are open, clear the two surface debts that milestone left behind (a RED
primary `ci` job and an unsplit `dev` command group).

**Target features:**

- **Delete `dev sdp`** — `cli_handlers.py:2098-2230` and its four gates, plus
  `tests/test_dev_sdp_cmd.py` (gate-ordering cases repurposed onto the new leg where they still
  apply). Its `disable` half duplicates the auto-unlock firmware already performs on **every**
  protocol-`0x0D` write; its `enable` half changes a state that provably cannot be read back on this
  family, so neither direction can ever produce evidence.
- **A plan-derived SDP leg inside `dev test`** — four steps in order: baseline write pattern A +
  verify (so a locked-from-the-factory part cannot read as "lock works"), `sdp_lock` (CMD 10,
  emission only), write pattern B carrying `FLAG_SKIP_SDP_UNLOCK` then **read back and assert
  equality against pattern A** (the oracle), then `sdp_unlock` (CMD 9) + write + verify so the part
  is left unlocked and proven writable again. Derived in `derive_plan` from
  `sdp_capability()` — 43 ALLOW / 41 REFUSE of the 84 `0x0D` chips, REFUSED chips getting an
  `NA`/`SKIPPED` step that carries the reason.
- **`write --sdp-relock`** — ⏸ **DEFERRED OUT OF THIS MILESTONE 2026-08-03** (operator decision) →
  ROADMAP Backlog **999.28**. Scoped as Phase 135, never planned, never executed; the phase number is
  not reused. Was to be the single user-facing way to deliberately protect a part, re-homing the flag
  deferred to the now-wrong label "v1.23+". **Polarity decided (operator, 2026-08-03) and still
  binding for 999.28: on verify failure the relock is SKIPPED and the skip is reported loudly**,
  leaving the part in the state the user can recover from — consistent with auto-unlock policy (d).
  Relocking a part whose write did not verify would protect a bad image behind a lock that cannot be
  read back and can only be cleared by another write.
  **⚠ What the deferral costs, since part (1) still ships:** `REQUIREMENTS.md` §RELOCK called the
  deletion and this re-homing "a pair"; the pair is split, so v1.30 **withdraws** the
  deliberate-protection surface and replaces it with nothing. Until 999.28 lands there is no supported
  way to leave an SDP part protected, and on `0x0D` the protection bit cannot be read back to check.
  Phase 137's CLOSE-05/06 were amended so the release notes and the gh#12 reply state that withdrawal
  plainly and never name `write --sdp-relock` as shipped.
- **mypy gate-hardening — get `firestarter_app`'s primary `ci` job GREEN.** v1.23 Phase 127 found
  `tools/check_mypy_watermark.py` **fail-open** (it shells to a bare `mypy` from `PATH`; under
  Python 3.12 the configured `python_version = "3.9"` is rejected and a numpy stub aborts the run,
  so it reported green without type-checking anything), hiding **69 inherited errors** against a
  watermark of 35. v1.23 deliberately left both OPEN for "a dedicated gate-hardening phase" and
  measured its own net contribution at zero (69 → 72 → 69). This is that phase's home.
- **999.15 / gh#8 dev-tools channel gating** — the channel is the gate; stable keeps `dev read` +
  `dev test`. Sequencing interaction stated in the design note: whichever of the two lands first
  shrinks the other's diff, and v1.30 **deletes** a subcommand 999.15 would otherwise have to
  classify.
- **The gh#12 outward follow-up** — `dev sdp` is named in the gh#12 reply and the b14 app release
  notes, both published 2026-07-30, one day before the retirement decision. A reply is owed stating
  the substitution honestly: gh#12 asked for "enable/disable" and gets neither *by that name* (unlock
  absorbed into `write`'s default behaviour, lock into `write --sdp-relock`), and without letting
  "now provable" drift into "now proven". Behind operator wording review.

**Key context:**

**Why this is worth a milestone rather than a patch.** On `0x0D` the protection bit is not readable,
so protection is observable **only through its effect**. That makes lock → inhibited-write →
read-back the *sole evidence path in existence* for this feature, and a standalone command can never
carry it. `dev test` is the right host for three independent reasons: it already writes on every run
(Phase 121 D-04), it is the community-validation entry point for hardware the maintainer does not
own and files its report through `submit_report`, and it **survives the 999.15 channel split into
stable** — so the evidence comes back to the repo instead of dying in a stranger's terminal.

**⚠ Evidence ceiling, fixed before any planning.** No AT28C part has ever been in operator inventory
and `0x0D` stays `UNVERIFIED`. What this milestone can prove: the *emission* (correct sequence,
correct pinout remap, `/WE` asserted) via the Phase 116 trace harness, and the *plan derivation* plus
the read-back comparison logic in the native envs. What it **cannot** prove: the causal claim *"the
lock inhibited the write"* — reachable only on real silicon, i.e. only from a community `dev test`
report, which by design **does not gate the close**. This split must be stated explicitly or the
milestone closes claiming a proof it does not hold: the same overclaim class as v1.22's C-5
correction.

**⚠ Three traps the leg must dodge** (from the design note §5):

1. **It is a false-green magnet.** The load-bearing assertion is that a write *fails*, and every
   unrelated failure — transport error, brownout, absent chip, blank-check abort — produces the same
   non-zero result. Same class as the SAFE-04 absent-chip trap, whose real assertion turned out to be
   `read_hardware_revision_value.assert_not_called()` rather than an exit code. **The oracle must be
   read-back equality against pattern A**; "the write reported failure" is not evidence. A *partial*
   change is gh#11's exact symptom and must read **BAD**, never OK.
2. **Keep the sensitivity pointing the right way.** If the lock never reaches silicon (the v1.22
   defect class), the inhibited write *succeeds* — and the leg must then report **BAD**. An
   unexpected success is the failure signal, never an inapplicable step; it must never be allowed to
   downgrade to `SKIPPED`/`NA`.
3. **The run must end unlocked, and the report must say so.** An abort between steps 2 and 4 (Ctrl-C,
   cable yank, brownout) ships a locked chip back to a community member. Recovery is a plain
   `firestarter write` (auto-unlock is default-on) and the report line must state it in those words.
   `0x0D` has **no erase operation at all**, so the wording is "rewrite", never "erase".

**⚠ The leg cannot be flag-gated.** `dev test` takes **zero options** since Phase 121 D-05
(`dev_test(app, chip)`, `cli_handlers.py:1961`) — the four v1.21 flags were removed, not disabled. Do
not reintroduce an option for it.

**Removal is safe *because* auto-unlock is default-on.** A chip left locked by any means is recovered
by a plain `firestarter write`; there is no orphaned-chip path and so no capability is lost. Record
the dependency — if that default is ever revisited, this decision must be revisited with it.

**Kept, load-bearing for both survivors:** `eprom_operations.py:1736 sdp_unlock` / `:1784 sdp_lock`;
`constants.py:72-73` `COMMAND_SDP_UNLOCK`/`COMMAND_SDP_LOCK` **and their `COMMAND_NAMES` entries**
(dereferenced at `eprom_operations.py:301` and `:377` — a missing entry is a `KeyError` at operation
setup, not a cosmetic gap); and `sdp_capability.py` in full, now serving `write`'s D-04 auto-set, the
new leg, and `--sdp-relock`. (The `--sdp-relock` consumer is deferred to Backlog 999.28 as of
2026-08-03, but `sdp_capability.py` stays load-bearing regardless — `write`'s D-04 auto-set and the new
leg are each sufficient reason to keep it. The `COMMAND_NAMES` dereference sites were re-measured by plan
132-08 to `_setup_operation:329` / `_operation_context:405`; the `:301`/`:377` anchors above are stale.)

**Stale labels this milestone fixes:** the `--sdp-relock` deferral used to read
"v1.23+" at `.planning/STATE.md:532` and `.planning/PROJECT.md:705`, written before v1.23 became
PY32F071 Integration — so the flag had no home. (The design note's own `STATE.md:154` /
`PROJECT.md:671` line references are themselves stale; the live lines were 532 / 705 at the time
this paragraph was written — see the terminal correction appended below the blockquote that
follows.)

> **⏸ AMENDED 2026-08-03 — the labels are still fixed, but they now point somewhere else, and this
> paragraph's own line numbers are a fourth stale pair.** Phase 135 was deferred → ROADMAP Backlog
> **999.28**, so the flag's home is the backlog, not this milestone; RELOCK-07 stayed in v1.30 (re-homed
> to Phase 137) and its target text was changed to name 999.28. **Measured 2026-08-03: the live lines are
> `.planning/STATE.md:634` and `.planning/PROJECT.md:823`** — not the 532 / 705 asserted just above.
> Four places in the record cite this same pair and no two agree (RELOCK-07's former `538`/`823`, this
> paragraph's `532`/`705`, the design note's `154`/`671`, and ROADMAP's v1.30 milestone-list entry, which
> still carries `154`/`671`). Only the `PROJECT.md:823` half has ever been right. **Re-measure before
> editing, and fix all four citation sites at once** — see RELOCK-07 in `REQUIREMENTS.md`.

> **⏸ AMENDED 2026-08-05, Phase 137 plan 137-04 — the terminal fix.** The `634`/`823` pair asserted
> just above was itself already stale by this plan's execution: fresh-measured 2026-08-05, the live
> lines are `.planning/STATE.md:972` and `.planning/PROJECT.md:844`. Both rows now read
> **Backlog 999.28** in place of the "v1.23+" label, and `REQUIREMENTS.md`'s RELOCK-07 is ticked
> Complete — this closes the citation-drift chain recorded above.

**Version and branch model.** Takes **v1.30**, not compacted to v1.29 — the retirement that freed the
v1.29 number landed in v1.23 Phase 130, and the number is deliberately left **vacant**. Meta forks
off the v1.23 tip (`gsd/v1.30-sdp-surface-retirement` off `d1b9ce9e`), the same shape as v1.23 forking
off the v1.22 tip; `main` lags and stays untouched, consistent with v1.19–v1.23.
`firestarter_app` forks off `beta` (`16a313a`). **`firestarter` is not touched at all.**

**Cost accepted knowingly:** a breaking removal from a published pre-release surface. `3.0.0b14` went
to PyPI `--pre` on 2026-07-30 and `3.0.0b15` carries the command too; the blast radius is days of
pre-release installs and **no stable release ever carried it**. Cheap now, strictly more expensive
every week it waits.

**Standing carry-forward, deliberately noted here.** The 14 pre-existing cross-milestone `audit-open`
items have now been acknowledged-and-deferred at six consecutive closes. STATE.md's own note is that
they "should be **scheduled** rather than acknowledged a seventh time." Folding the mypy
gate-hardening into this milestone discharges the largest and most actionable of that set; the
remainder are not in v1.30's scope and will present again at close.

## v1.23 Archive: PY32F071 Integration — Shipped 2026-08-03

**Status (2026-08-03): all 8 phases (123–130) COMPLETE — CLOSE-01…CLOSE-04 validated in Phase 130, verification passed 4/4; 47/47 v1 requirements.** `3.0.0b15` is published on both channels (PyPI `firestarter==3.0.0b15`; the firmware GitHub prerelease carrying **four** board `.hex` assets, including the first-ever publication of `firestarter_py32f071.hex`). Closed `override_closeout`: Phase 126 verified `passed-with-findings` (one informational finding) and the same 14 pre-existing cross-milestone `audit-open` items were acknowledged-and-deferred for the sixth consecutive close — **none originate in v1.23**. **No stable release** — PyPI `info.version` stays `2.0.7`. Meta tagged `v1.23` on `gsd/v1.23-py32f071-integration`; firmware + app tagged `v1.23` on `beta`; gitlinks bumped to the published b15 commits; `main` not merged, per v1.19–v1.22. Full entry: `.planning/MILESTONES.md` §v1.23. Roadmap/requirements archived at `.planning/milestones/v1.23-{ROADMAP,REQUIREMENTS}.md`.

**Goal (as set at kickoff):** Land the in-flight PY32F071 firmware port and the host USB-DFU firmware installer onto `beta` as one lockstep integration — including the cross-repo release-asset unblock — without touching the three AVR targets, and without claiming anything about silicon that does not exist.

**Target features:**

- **Land the portability + py32 firmware stack onto `beta`, ATOMICALLY** — `agent/portability-macros` (5 commits; a **compat-shim layer, not a timing abstraction**: `include/rurp_platform_compat.h`, an `include/avr/pgmspace.h` `#include_next` shadow, and include-swaps + macro→`static inline` in `rurp_serial_utils.h` / `rurp_shield.h`) together with `agent/py32f071-toolchain` (PR #48, 52 commits: ARM GCC + CMake target, pinned OpenPuya SDK `0ed2f4b`, CherryUSB CDC at 48 MHz PLL, SysTick ms + TIM3 µs, VREFINT-compensated 12-bit ADC, contiguous 8-bit GPIO bus via one-snapshot `IDR` read / atomic `BSRR` write). **They must land as ONE commit-pair — see the research-corrections block below; landing the "HAL prep" half first is a measured trap.**
- **Hard acceptance constraint** — Uno, ATmega328PB, Leonardo and the native test suite remain unaffected. Golden register traces, the dispatch-mirror guard, `check_dispatch.py` and the nine cross-repo source-scanning gates all stay green.
- **VPP control seam only, no closed loop** — `rurp_vpp.h` capability macros (`RURP_HAS_VPP_DAC`, `RURP_VPP_DAC_BITS`) + `rurp_vpp_control_mode_t`/`rurp_vpp_result_t` + `RURP_VPP_CONTROL_MANUAL` on every board, with `rurp_set_vpp_target_mv()` returning `MANUAL_ADJUSTMENT_REQUIRED`.
- **Flash-persistent config for the py32** — the part has no EEPROM and PR #48's config is runtime-only; CRC-validated dual-slot flash records. Storage *backend* per platform; the `rurp_configuration_t` schema stays untouched. **⚠ This is DESIGN work, not integration** — `platform/py32f071/PORTING.md` exists only on the two CLOSED PRs (#46/#47, blob `4b1a441`) and its module layout does not match what #48 built, so there is no in-tree design to integrate. <!-- recordscan:history reason: accurate at milestone kickoff (2026-07-30), when PORTING.md's stranded design was the only in-tree reference point; superseded by Phase 126, which authored and landed the actual dual-slot CRC32 flash-persistent config in-milestone (R-8/A-6) rather than integrating PORTING.md. Preserved as the kickoff-time assessment, not a live claim about Phase 126's shipped design. -->
- **Host DFU installer lands** — `firestarter_app` `feature/py32f071-fw-install` @ `4ee64a1`: `firestarter_app/firestarter/py32_dfu.py` (pure-Python DFU 1.1 + DfuSe over pyusb, no external binary), `flash_method()` board dispatch, beta-only channel gating via `channel.py` + `BETA_ONLY_BOARDS`, and the two safety fixes already on the branch.
- **The cross-repo release-asset unblock** — fold the py32 build into `beta-build.yml` *after* the version bump, publishing `firestarter_py32f071.hex` as a real **release asset** rather than an Actions artifact.
- **Record the flash-path decision and its PCB requirements before the first schematic** — self-flash bootloader over the existing CDC + COBS transport as the intended primary route, factory USB DFU (Puya UM1504) as the maintainer/manufacturing recovery route; BOOT0/nBOOT1 strapping, SWD pads, contiguous 8-bit port, flash-budget reservation.
- **Correct the stale ROADMAP prior-art paragraph** — pending todo `correct-v128-py32-roadmap-prior-art`, all five corrections.

**Key context:**

**No PY32F071 PCB exists** (operator, 2026-07-28) → software-only close, the same shape as v1.22. The pin map on PR #48 is an explicitly provisional placeholder (PB0–PB7 data, PA0–PA5 control, VPP on PA4/ADC ch4) that exists so the target compiles before a schematic, and **must not be trusted near a PROM**. Permitted claims: the target builds clean, the native and host suites pass, and the DFU sequence is exercised against device descriptors and mocks. Forbidden claims: *"the firmware runs on a PY32F071"* or *"the install works end to end."*

**⚠ The v1.28 ROADMAP entry's prior-art paragraph is stale and must not be used to seed scope.** It was written at the 2026-07-27 backlog review against an incomplete read of `origin` and asserts the work is *"not in flight"* citing PR #46 closed-unmerged with `feature/py32f071-toolchain` @ `2c2ed10` (603 additions / 8 files) as the surviving prior art. Verified against `origin` on 2026-07-30, all three claims are wrong:

1. **PR #48 (`agent/py32f071-toolchain`) is OPEN as a draft**, stacked on `agent/portability-macros`. PRs #45, #46 and #47 are closed attempts. The work *is* in flight.
2. `feature/py32f071-toolchain` @ `2c2ed10` is the **smallest** of five branches. `agent/py32f071-toolchain` carries **52 commits ahead of `beta`**; `feature/py32f071-release-assets` is that stack plus one asset-naming commit (53 ahead). **Every py32 branch is 72 commits behind `beta`** — measure against `beta`, never `main`, which lags `beta` by ~268 commits.
3. **"Does this architecture even build" is already retired** — PY32F071 CI went green three consecutive times (2026-07-21) compiling the *shared* command processor, framing and PROM algorithms for Cortex-M0+. Firmware identity is already host-correct: `RURP_BOARD_NAME = "py32f071"`, and `DATA_BUFFER_SIZE` is **512** (`CMakeLists.txt:113`, matching item 7 of the research-corrections block below). **⚠ CORRECTED (R-2):** this bullet previously named the wrong figure here as a current fact — the value 512, not Leonardo's 1024, deliberately not bumped because it is wire-visible via v1.10 CAP-01 and a bump would be a behaviour change needing its own justification (`REQUIREMENTS.md` §"Out of Scope": *"Changing the py32 `DATA_BUFFER_SIZE` from 512"*).

**⚠ Do not start from PR #47** (`feature/py32f071-full-support`, closed). Its 24-file `platform/py32f071/` tree and all-inclusive CMake list read as the most finished branch, but `src/usb.c` (141 lines) is a ring buffer over `__attribute__((weak))` **no-op** low-level hooks — it links, and a board flashed with it would be **silent on USB**. `vpp_target.c` is 13 lines and there is no SDK fetch. Start from #48.

**⚠ Scoping decision — the DAC VPP closed loop is deliberately NOT in scope, and this is not a wording nicety.** PR #45 (`feature/common-vpp-calibration`, closed, 10 commits) is a single API spanning two concerns, and the closed loop *depends* on the calibration half: `rurp_set_vpp_target_mv()` closes its loop on `rurp_read_voltage_mv()` — the **calibrated** read — and `rurp_calibrate_vpp_two_point()` **is** the White-Box Voltage Calibration milestone's Stage-2 divider trim, already cross-platform. Three of its ten commits reach into files that milestone owns: `9134f2a` (`src/boards/rurp_common.cpp`, the exact Stage-1 target), `768580f` (`include/rurp_types.h`) and `b964ee6` (`src/rurp_config_utils.cpp`) — the latter two being `CONFIG_VERSION`-bump + EEPROM-migration territory, which is also where Backlog 999.1's stale-`r1` fix lives. So "DAC VPP in, calibration out" has no clean split. **Resolution (operator, 2026-07-30): land the seam only** — capability macros, enums and the `MANUAL` default, so the py32 port compiles against the final shape and the calibration milestone need not re-architect, while `rurp_set_vpp_target_mv()` refuses on every board, the AVR measurement path is **not** rerouted, and no `CONFIG_VERSION` bump occurs. Two independent facts support this: PR #45 does **not** contain the Stage-1 bandgap back-solve, so that milestone's ±10 % win is unaffected either way; and with no PCB, a closed loop **cannot be validated at all** this milestone — a loop that cannot be validated must not be claimed to work.

**⚠ The self-flash bootloader is the intended primary install route; the DFU path landing here is the runner-up.** `.planning/seeds/py32f071-no-external-tool-fw-install.md` decides for a small bootloader in the first few KB of the 128 KiB flash speaking the same USB CDC + COBS framing the firmware already uses — zero new host dependencies, since `pyserial` is already a dependency, structurally identical to how the Uno works. Every factory-bootloader route was rejected for host-side reasons: Puya `PY32DfuTool` is Windows x64 only; `dfu-util` is an external binary with avrdude's PATH-discovery burden; `puyaisp` needs a second USB-serial dongle on a board that has native USB. The pyusb DFU client built on the app branch is the **vendored-Python-over-libusb** row of that table — accepted at operator request so the transfer sequence gets proven, with the residual cost being `pyusb` + a libusb backend and a WinUSB driver via Zadig on Windows. **Landing it does not retire the seed.** What this milestone must capture is the PCB consequences, because the board is still paper and they are cheap now and expensive later.

**⚠ RESEARCH CORRECTIONS (2026-07-30) — this section was written BEFORE the four-stream research, which falsified several of its claims.** Full list as R-1…R-18 in `.planning/milestones/v1.23-research/SUMMARY.md` §"Corrections to the Planning Record", with the seven inter-researcher conflicts adjudicated as A-1…A-7. Three of the four researchers built, merged and tested the branches rather than reasoning about them. The load-bearing corrections:

1. **The build order above was a trap (R-9/A-4).** `agent/portability-macros` **cannot land alone**: cherry-picked onto today's `beta` it takes `pio test -e native` from **141 cases / 17 suites passing to 0 passing / 17 ERRORED** — `pgm_read_ptr` and `strncmp_P` are undeclared in `json_parser.c`, because its `rurp_platform_compat.h` omits four helpers the native `avr/pgmspace.h` stubs supplied. The repair, commit `780a3fb` (*"Complete non-AVR program-memory compatibility helpers"*), lives on the **stacked** branch. The gh#16-inherited "HAL prep leads" framing describes a branch that is not self-sufficient. **Land atomically.**
2. **The rebase is not the risk; a defect git cannot see is (A-2/A-3).** Both repos merge with **zero textual conflicts** and completely disjoint changed-file sets since merge base `a1953c2` (2026-06-18 — the beta side spans **v1.14→v1.22**, eight milestones, not just v1.22). But `platform/py32f071/CMakeLists.txt:46-47` names `src/proms/flash_type_3.cpp` / `flash_type_4.cpp`, renamed by v1.19 Phase 104 to `flash_nor_unlock.cpp` / `flash_5v_page.cpp`, so git produces a perfect merge of a tree whose ARM target **fails at CMake *configure* time** — and `py32f071.yml` has **no `push` trigger**, so nothing on `beta` would report it. Triple-corroborated; the milestone's highest-confidence finding. **"The merge had no conflicts" must never be used as a quality statement.**
3. **AVR flash growth is not where the risk lives, and the recorded headroom was stale (A-1/A-5/R-10).** Measured on the merged tree: Leonardo **26072 → 26016 B (−56 B)**, Uno **+22 B**, ATmega328PB **+28 B**, RAM unchanged. Live Leonardo headroom is **2600 B on `beta` / 2656 B merged** — **not 2992 B**; that figure predates Phase 119's own +392 B (25680 + 392 = 26072, byte-exactly what `beta` builds). Budget new work against 2600 B. **Leonardo RAM (2014/2560, 546 B free) has never been recorded at all — record RAM alongside flash from now on**, because a `PROGMEM`→RAM regression is invisible in a flash number.
4. **The cross-repo gates fail OPEN, reproduced (A-7).** `_FW_ABSENT = not _EEPROM_28C_CPP.exists()` uses one *file* as the proxy for repo presence; renaming that file flipped **5 gate legs PASS→SKIP at exit 0** with the false reason *"firestarter firmware checkout absent"*. Six modules share the idiom; 33 legs skip with no sibling repo. Prior milestones were bitten by the **fail-closed** form four times and CI caught it — **this form has never fired, because no prior milestone moved firmware files at scale, which is exactly v1.23's premise.**
5. **A hollow gate is already inside the branch being landed.** `RURP_PY32F071_PINMAP_CONFIGURED` is `#define`d `1` two lines above `#if !RURP_PY32F071_PINMAP_CONFIGURED → #error`, so the guard **cannot fire**; `RURP_PY32F071_PINMAP_PROVISIONAL` has **zero code consumers** while the provisional pins are driven live. The one mechanical hook for *"this pin map must not be trusted near a PROM"* currently enforces nothing, and this class is **prevention-only** — v1.18 was an entire milestone caused by one mis-modelled pin.
6. **Scope is smaller than written in one place and larger in another.** Smaller: the `firestarter_{board}.hex` extension hardcoding is **already fixed** on the branch (`asset_candidates()` + `_pick_asset()`, all four call sites, `.bin` already accepted) — do not re-plan it (R-7); **21 host capabilities already exist**, only **8 items remain**, and just one of those (the release-asset publication) gates any user-visible value. Larger: flash-persistent config is design work (R-8, above).
7. **Two more in-tree facts (R-1/R-2).** `rurp_platform.h` is on the **py32** branch, not `portability-macros`; that branch does **no** pin-map work (`rurp_pinout.h` is untouched by every branch) and its timing functions have **zero common-code consumers** — the real portability mechanism is `platform/py32f071/include/Arduino.h`, a **fake Arduino core**. And py32's `DATA_BUFFER_SIZE` is **512, not 1024** (`CMakeLists.txt:113`) — **wire-visible** via v1.10 CAP-01, so the host chunks to 510 and any "matches Leonardo throughput" expectation is wrong.

**Version/slot handling (operator, 2026-07-30):** this milestone takes **v1.23**, the two queued py32 slots (`v1.28 PY32F071 Port`, `v1.29 PY32F071 USB Firmware Install`) are **retired into it**, and `Binary Command Protocol` renumbers **v1.23 → v1.28** (a freed number). v1.24–v1.27 (Bus-Config Mask-Model, Jumper-Display/2516, White-Box Voltage Calibration, Per-Protocol EPROM Algorithms) are **left untouched** so every by-number cross-reference in the seeds, notes and todos keeps resolving.

**Branch model:** meta forks off the v1.22 tip (`gsd/v1.23-py32f071-integration` off `8be00ee`); sub-repos fork off `beta` per standing policy, then the py32 branches merge in — verify with `git` at execute time regardless. **Phase numbering continues from v1.22's Phase 122 → v1.23 starts at Phase 123.**

**Release hazard, unchanged:** pushing `beta` in either sub-repo auto-fires CI and cuts a new beta, so the cut is a deliberate decision and never a side effect. `firestarter_app`'s CI fix `81fa53c` lives on `beta` only and must be reintroduced whenever the milestone branch next merges toward `main`.

**Phase progress — 6 of 8 complete (updated 2026-08-01):**

- ✅ **Phase 123** Non-Regression Baselines & Gate Hardening — 11/11 plans, verified 8/8 reqs. Six fail-provable gates and the BASE-01 baseline JSON exist before any firmware moved.
- ✅ **Phase 124** Firmware Integration Merge — 12/12 plans, verified 8/8 reqs + 5/5 criteria. The py32 stack landed as one squashed commit; ARM configure+build cited by CI run `30634186514`.
- ✅ **Phase 125** VPP Control Seam — 6/6 plans, verified 15/15 must-haves, VPP-01…03 closed. Hand-authored `include/rurp_vpp.h` + `src/rurp_vpp.cpp`, dependency-free, **zero production callers**, named in the ARM manifest with `RURP_HAS_VPP_DAC=0`. **0 B flash and 0 B RAM** on all three AVR targets, non-vacuous in both directions. ARM evidence: CI run [`30652530756`](https://github.com/henols/firestarter/actions/runs/30652530756) at head SHA `2b5e8c8`, Configure and Build each independently green, with `[4/39] Building CXX object …src/rurp_vpp.cpp.obj` proving the seam reached the ARM compiler.
  **Two decisions worth carrying forward.** The `#include "rurp_vpp.h"` line in `include/rurp_shield.h` that this milestone's own planning documents all described as the phase's header change was measured to collapse `pio test -e native` from 141/141 to 17 suites / 0 succeeded; the operator chose to omit it entirely, so `rurp_shield.h` is untouched (`125-RESEARCH.md` C-1). And **AVR-class manual VPP control is permanent, not provisional** — no Arduino-class board will ever carry the DAC (operator, 2026-07-31) — so `__AVR__` resolves the capability macro and every non-AVR board must declare it explicitly.
- ✅ **Phase 126** Flash-Persistent Config — 12/12 plans. Dual-slot CRC32 py32 config backend behind a common/per-platform storage seam; the AVR EEPROM backend proven a pure move. Flash geometry settled at page 256 B / sector 8192 B; ARM CI green on 42 objects with zero AVR delta.
- ✅ **Phase 127** Host DFU Installer — 12/12 plans, verified 5/5 criteria + 8/8 requirements (HOST-01…08). `feature/py32f071-fw-install` @ `4ee64a1` landed as a **real merge commit** (`firestarter_app@63ce44e`, `4ee64a1` literally among its parents). Suite 1158 → **1293 passed / 0 failed / 0 skipped**, coverage 81.88%. `_check_envelope` retightened from the 128 KiB part size to the 120 KiB application region Phase 126 reserved; `DFU_UPLOAD` readback verification added with `VerifyResult` and a "written but NOT verified" completion line; `--usb-id` now actually *rejected* on a stable channel rather than merely hidden. HOST-04 evidence: CI run [`30708836339`](https://github.com/henols/firestarter_app/actions/runs/30708836339) at head SHA `a62ca76`, `ci-py32` leg green on a runner with `pyusb` resolved to `1.3.1`. **HOST-03's readback is asserted against a mock only** — see `127-NONREGRESSION.md` §7, which Phase 130's CLOSE-02 cites verbatim.
  **Three things worth carrying forward.** (1) `127-RESEARCH.md`'s **C-1 "zero fixups" is disproven** — the merge changed `fw --help`, reddening a characterization snapshot; the fix is channel-aware because `_BOARD_CHOICES` is import-time and `py32f071` appears only on a prerelease. (2) **The mypy watermark gate has been fail-open**: `tools/check_mypy_watermark.py` shells to a bare `mypy` from `PATH`, and under Python 3.12 the configured `python_version = "3.9"` is rejected and a numpy stub aborts the run, so it reported green without type-checking anything. **69 inherited errors** (watermark 35) were hidden this way and surfaced on this branch's first CI run; Phase 127's own net contribution measured **zero** (69 → 72 → 69, confirmed on the runner). The 69 and the fail-open tool are **deliberately left OPEN** for a dedicated gate-hardening phase — the primary `ci` job is RED until then. (3) Plan 127-11's structural operator gate was **removed by explicit operator decision**, and the push and CI dispatch were run by the orchestrator under that authorisation — recorded as such rather than as an operator action.
- ✅ **Phase 128** Release-Asset Fold — 10/10 plans, verified 4/4 must-haves, REL-01…04 closed. The ARM build is now a composite action (`.github/actions/build-py32f071/`) called by both `py32f071.yml` (LOUD, no `continue-on-error`) and `beta-build.yml` (SOFT, contained at the call site only), placed strictly after the version-bump auto-commit. `beta-build.yml` gained a permanent `rehearsal` boolean input, three success-path assertions, an unconditional AVR-assets gate before `Release`, and a two-entry `files:` list because one glob cannot span PlatformIO's `.pio/build/` and CMake's `build/py32f071/`.
  **Proven on two real dispatches, not by reading YAML.** Run A [`30722352902`](https://github.com/henols/firestarter/actions/runs/30722352902) @ `7a0a375` published `firestarter_py32f071.hex` (77284 B) alongside the three AVR hexes and asserted `PASS: image contains version string 3.0.0b99:py32f071` — the REL-01 evidence that survives a future step reorder. Run B [`30722537152`](https://github.com/henols/firestarter/actions/runs/30722537152) @ `6c1c31f` planted a real ARM compile error: the job still went green and published exactly the three AVR assets and no py32 asset. **Run B also empirically validated D-07/F-4** — GitHub set the contained ARM step's `conclusion: success` while its `outcome` was `failure`, so the `outcome`-keyed report step fired and the three `outcome == 'success'`-guarded assertions skipped; a `conclusion`-keyed gate could never have fired. Both releases were drafts under `rehearsal-<run_id>` tags, since deleted; zero tags were created and the newest real release is still `3.0.0b14`.
  **Three things worth carrying forward.** (1) The phase plan's own prescribed run-B break — renaming a source path in `platform/py32f071/CMakeLists.txt` — was **unusable**: it trips Phase 123's CMake manifest-drift gate inside `pytest tests/` at a step with no `continue-on-error`, so the job would have failed *before* the ARM build and published nothing, demonstrating the opposite of REL-03. A compile error in an ARM-only TU was substituted. **A phase's validation procedure can be wrong in a way that would have produced false evidence.** (2) Plan 128-05 shipped `beta-build.yml:50` asserting *"Confirmed by observation on rehearsal run A"* before run A existed — caught and fixed in `7a0a375` before dispatch. (3) **REL-03's second half is local-only**: that the AVR-assets gate *fails* on a missing asset is proven by 128-01's planted fixtures via subprocess tests, never exercised in CI. Likewise F-8 — neither app CI workflow checks out the firmware sibling, so 128-09's cross-repo binding SKIPS in app CI and is held by local runs and developer discipline.
- ✅ **Phase 129** Flash-Path Decision & PCB Requirements Record — 9/9 plans, verified 5/5 must-haves, PCB-01…05 closed. Two layers held in lockstep: the authoritative `.planning/milestones/v1.23-FLASH-PATH-DECISION.md` (§1–§9 + claim ceiling) and its firmware-repo subset `platform/py32f071/FLASH-PATH-AND-PCB.md`, whose five `[SHARED:S1]`…`[SHARED:S5]` sections a 41-leg cross-repo gate (`tests/test_flash_path_record_sync.py`) compares body-for-body. Firmware suite 180 → **221 passed**. D-11's linker cross-reference landed comment-only, proven by a local ARM byte-identity rebuild (D-13); meta gitlink bumped `7a0a375` → `5a89ee7`; `firestarter_app` untouched.
  **The gate was authored before the content it judges** — `3393137`/`42395cf` precede the meta record (`8515a59`) and the subset (`8102d0f`) in git history, and it went **31 RED → 0 RED** entirely through content written afterwards. This is the direct answer to the fail-OPEN idiom reproduced as A-7: the 10 fail-closed legs make a missing scan target an ERROR, not a silent skip.
  **Two things worth carrying forward.** (1) **A gate authored before its content can be authored unreachable.** `test_linker_comment_cross_references_record` located the MEMORY block by requiring `MEMORY` and `{` on one source line, but `PY32F071xB_FLASH.ld` has them on lines 8 and 9 — the leg could never pass, whatever the comment said, and nothing caught it until 129-07 tried to satisfy it. The locator-only fix (`2ef7b57`) was operator-authorized conditional on a RED-preserving proof: with the locator fixed and the comment reverted, the leg still failed on missing needles. Writing the gate first is necessary but not sufficient — a gate that has never been *seen to pass* is not yet known to be reachable. (2) ROADMAP criterion 3 is recorded **AMENDED** and criterion 4 partially amended rather than silently redefined; the REQUIREMENTS/ROADMAP/FUT-N04 "no VTOR" prose and the Validation-Ceiling narrowing are deliberately left OPEN for Phase 130's CLOSE-01. <!-- recordscan:allow reason: this sentence names the "no VTOR" wording as an open correction item for Phase 130's CLOSE-01 to close elsewhere (REQUIREMENTS.md/ROADMAP.md, per 130-RESEARCH.md C-9), it does not itself assert the PY32F071 lacks a VTOR -- see REQUIREMENTS.md/ROADMAP.md's own corrections, Plans 130-06/130-10. -->
**⚠ CORRECTION (2026-08-02) — Phase 130 close: six research corrections carried into this record.** `130-RESEARCH.md`'s R-1…R-18 work list applies to this document as follows:

1. **R-2** — py32 `DATA_BUFFER_SIZE` is **512**, not 1024 (corrected in prose at item 3 of the research-corrections block above); deliberately not bumped to match Leonardo's 1024, because it is wire-visible via v1.10 CAP-01 and a bump would be a behaviour change needing its own justification (`REQUIREMENTS.md` §"Out of Scope").
2. **R-11** — the `firestarter_app` host DFU branch head is `4ee64a1`, not `311eacf`. The v1.22-close footer near the end of this file (dated 2026-07-30, naming the next-milestone slot that has since become v1.23) carried the superseded SHA and is corrected by this same plan with an appended supersession note.
3. **R-15** — both halves of the "no CI trigger / toolchain absent" finding moved. The no-`push`-trigger half is fixed in code: `py32f071.yml` now carries `push: branches: [beta]` (MERGE-03). The toolchain-absent half is itself **false** — the ARM toolchain (`arm-none-eabi-gcc` plus two newlib packages CI omits) installs and works in this devcontainer, D-07's subject, narrowed at `REQUIREMENTS.md:18` by Plan 130-10. Surviving rule: local ARM builds support **delta and byte-identity** claims only; every absolute ARM size claim cites a CI run URL plus commit SHA.
4. **R-10** — no substantive correction needed. `2992 B` was the pre-Phase-119 Leonardo headroom (28672 − 25680), exactly what Phase 119's own `+392 B` was judged against — the v1.22 archive line above and the v1.22 decision-register line above are historically correct and are preserved, each carrying an inline history marker. The live post-merge figures (Phase 124: Leonardo 26016/28672, Uno 23954/32256, 328PB 24004/32384; see `124-NONREGRESSION.md` §F4d) are what this milestone measured against.
5. **A-5** — the operator-visible AVR flash-constraint decision the research spine assigns to Phase 130 is already **discharged at Phase 124**: `REQUIREMENTS.md` Operator Decision 4 restates it as *"Leonardo flash must not grow; Uno-class growth ≤ 64 B, recorded"*, MERGE-05 encodes it, and `124-NONREGRESSION.md` §F4d's independent 328PB build (`+28 B ≤ 64 B`) closed the single-source gap. Recorded here as discharged, not as fresh work.
6. **The two py32 ROADMAP slots** (`v1.28 PY32F071 Port`, `v1.29 PY32F071 USB Firmware Install`) are retired into v1.23 by CLOSE-03 (Plans 130-04/130-05); any reference elsewhere in this document to either as a live, separately-scoped plan is superseded by that retirement. None of the six items above claims that the firmware runs on a PY32F071, that the install works end to end, or that anything is bench-validated, hardware-validated or silicon-verified.

- ✅ **Phase 130** Close — Honesty Ledger, Claim Gate, Release Decision — 16/16 plans, verified 4/4 CLOSE requirements. Every research correction (R-1…R-18) landed across `PROJECT.md`, `STATE.md`, `ROADMAP.md` and the notes file, proven by a committed label-aware checker (`check_record_corrections.py`, 0 unlabeled of 60 exempt hits); `130-LEDGER.md`'s six-tier honesty ledger pairs every permitted claim with its explicit non-claim, covering the provisional pin map, the absent ARM bus-trace oracle, unmeasured USB-ISR-vs-PROM timing and HOST-03's mock-only ceiling; the ROADMAP slot renumber landed with the stale v1.28 prior-art correction, v1.24–v1.27 proven byte-unchanged by a one-shot SHA-256 proof (D-16); and `130-DECISION.md` was committed before any push, recording the accept-the-auto-fire decision for the `beta` cut.
  **Both channels are public at the observed cut tag `3.0.0b15`** (read from `gh release list`, never computed): the firmware GitHub prerelease carries four `.hex` assets including `firestarter_py32f071.hex` — the **first-ever publication** of that asset, the one thing that makes the 21 already-landed host DFU-install capabilities reachable outside this tree — and PyPI carries `firestarter==3.0.0b15`, resolved from a clean venv (`130-CHANNELS.md`). **No stable release** — PyPI `info.version` stays `2.0.7`, consistent with every milestone since v1.11. The meta gitlinks are asserted against the milestone-branch tips, not the post-publish `beta` state: `firestarter` bumped `5a89ee7 → 05c20bf` (plan 130-03's commits moved the tip); `firestarter_app` unchanged (`cc9452f`, nothing in this phase committed inside it). The `v1.23` annotated tag and any merge toward `main` stay with `/gsd-complete-milestone`, per D-04.
  **Three residuals carried forward, named so no reader concludes this close is unqualified.** (1) **D-17's USB-identity tension is owned, not resolved** — the interim pid.codes `1209:0001` pair now published in `usb_cdc.c` is the registry's own documented private-testing pair, not an allocation, and `.planning/milestones/v1.23-FLASH-PATH-DECISION.md` §5(c)'s ship gate stays byte-unchanged; a future reader may find that condition unmet, which is exactly what the condition's own wording permits. (2) **The ARM pass stays delta-and-byte-identity only** — a local build's absolute size is never comparable to a CI figure (measured `text=27260` local vs. `text=27344` CI), and this phase's own `usb_cdc.c` change is reported as a confined delta, never byte-identity (the descriptor bytes changed by design). (3) **The community inbox is not empty** — gh#20 (AT28C256 `dev test` FAIL) and gh#18 (FM1608 `dev test` PASS) both arrived after the 2026-07-27 backlog import and remain open, out of scope for this milestone.
  **One out-of-plan finding, recorded honestly rather than smoothed over:** the first CI attempt of the real cut failed in both repos on three pre-existing CI-only sibling-checkout test defects, invisible in this devcontainer because it has the sibling layout standalone CI lacks. Two fixes (`firestarter` `1c511e8`, `firestarter_app` `5934a54`) landed on `beta` directly during the operator's hand-off, outside any plan — one of them **softened a Phase-129-authored hard assert** (`test_present_root_with_missing_target_raises_not_skips`) to a skip, a defect-class change worth flagging rather than treating as a routine fix. Both fixes are confirmed ancestors of `origin/beta` and ancestors of neither milestone branch, a divergence recorded rather than silently reconciled.
  Full detail in `130-NONREGRESSION.md` (the closing sweep, re-executed in this session) and `130-CHANNELS.md` (the channel-verification transcript).

## v1.22 Archive: AT28C Software Data Protection Lifecycle — Shipped 2026-07-30

**Status (2026-07-30): all 7 phases (116–122) COMPLETE — CLOSE-01/02/03 validated in Phase 122, verification passed 5/5.** `3.0.0b14` is published on both channels (PyPI wheel + sdist; GitHub prereleases in both repos, firmware carrying its three board `.hex` assets) and the two community reporters have been answered on `henols/firestarter_prom` #11 and #12 — both issues deliberately left **OPEN** pending a real silicon re-test, because nothing here is silicon-verified.
**⚠ The milestone ships at its validation ceiling, not past it.** The SDP lock/unlock sequences are emitted byte-exact across all four `0x0D` pinouts and verified in software, with measured host-side timing — **no AT28C silicon was tested.** `0x0D` remains `UNVERIFIED` in `PROTOCOL-LEDGER`, zero chips changed `support_status`, and the 84-chip count is unchanged. The one asymmetry (EIGHTH CORRECTION below): the headline **defect** is now community-corroborated on real AT28C256 silicon; the **fix** is not. `.planning/phases/122-*/122-LEDGER.md` is the honesty ledger — nine claim classes, each pairing a permitted wording with an explicit non-claim, plus what this milestone chose not to prove.
**Closed by `/gsd-complete-milestone` 2026-07-30:** the `v1.22` annotated tag now exists in all three repos (meta on `gsd/v1.22-at28c-software-data-protection-lifecycle`; firmware + app on `beta`), all pushed to origin; the meta gitlinks are bumped off PINNED-at-b11 to the published `3.0.0b14` commits (firmware `5c9160a` / app `e7d3ee8`). **Still open, deliberately:** the app CI test fix `81fa53c` lives on `firestarter_app`'s `beta` ONLY — it was cherry-picked onto the milestone branch and then reverted to keep the branch HEAD an exact match for Plan 122-03's recorded merge SHA, and it **must be reintroduced whenever that branch next merges toward `main`** or `ci.yml`'s standalone-checkout risk resurfaces (`122-CUT.md` §8). And **no STABLE release** — stable stays operator-gated; `main` is untouched in all three repos, consistent with v1.19–v1.21.

**Goal:** Make Software Data Protection on protocol `0x0D` (`configure_eeprom28c`) explicit, observable, and bidirectional — wire the missing SDP lock path, expose lock/unlock as gated user-facing operations, and replace today's silent unconditional auto-unlock with one the user can see and opt out of.

**Target features:**
- **SDP enable/lock wired in firmware** — the AT28C datasheet enable sequence has a table (`FLASH_ENABLE_WRITE_PROTECTION`, `include/flash_utils.h:48`) with **zero callers**; no lock capability exists at any layer today.
- **SDP disable/unlock as an explicit operation** — invocable in its own right, not only as an invisible side effect of `write`.
- **Host CLI surface** for lock/unlock behind the v1.21 destructiveness gate with explicit opt-in — unlock is a destructive-capability addition and must never fire silently.
- **Today's auto-unlock becomes observable and opt-out-able** — `eeprom28c_write_init` currently runs the 6-write SDP-disable sequence unconditionally on every `0x0D` write with no user-visible signal.
- **Positive proof the SDP sequences landed** — replace the weak `0x5555` read-back inference (`eeprom28c_wait_for_write(handle, 0x5555, 0x20)`) with a real success/failure signal.
- **3-tier software validation harness** — native golden register traces + host tests; no silicon required (no AT28C part in operator inventory).
- **gh#11 / gh#12 closeout** — comment both with what `3.0.0b11` already changed and ask the reporters to re-test and file a `dev test` report. Best-effort: **no milestone requirement depends on a community reply.**

**Key context:**

**The promoting backlog triage note is superseded by the code.** Backlog 999.19/999.18 (and the ROADMAP `NEXT` entry) assert that protocol `0x0D` "currently has no SDP path today." Reading the tree at v1.22 start disproves that:

- **SDP-disable already exists in SOURCE and runs unconditionally** on every `0x0D` write — the 6-write `AA-55-80-AA-55-20` sequence in `eeprom28c_write_init` (`firestarter_fw/src/proms/eeprom_28c.cpp:105-113`), added in v1.0-era Phase 06-01 (`34cefac`), present on `beta`, therefore **shipped in `3.0.0b11`**. **⚠ CORRECTED BY RESEARCH (2026-07-27): true of the source, almost certainly false of the silicon.** The sequence routes through `flash_util_byte_flipping` → `fu_flash_fast_address` (`flash_utils.cpp:61-66`), which writes raw addresses into the LSB/MSB latches and **bypasses `mem_util_remap_address_bus`** (`memory.cpp:259-282`) — no pin remap, no `rw_line` polarity, no `static_high_mask`. The four `0x0D` pinouts carry `rw` bus lines 11/14/14/20 (DIP pins 21/27/27/30) versus 22 for the `DIP32_SST39SF040` this shared helper was authored for, so **at least one command write is emitted with `/WE` HIGH — a documented Write Inhibit — on all 84 `0x0D` chips.** See `.planning/research/SUMMARY.md` §Adjudicated Conflicts + §PROVEN vs PREDICTED.
- **64-byte page write + read-back polling already exist** (`eeprom_28c.cpp:126-140`, `PAGE_SIZE 64`) — the 339 s byte-at-a-time write time reported in gh#11 comes from a code path that no longer exists.
- Both community reports are **2024-vintage (app 1.0.13)**, predating the entire 3.0.0 architecture.

Hence the milestone reframed from *"implement SDP"* to *"complete and expose SDP"*. What is genuinely missing is the **lock** half, the **user-facing surface**, the **observability**, and **proof the existing unlock works**.

**⚠ SECOND REFRAMING AFTER RESEARCH (2026-07-27) — the milestone opens with a FIX, not a feature.** Four independent research streams converged on three falsifications of the framing above:

1. **The unlock path almost certainly never reaches silicon** (the `/WE` inhibit above). This is the milestone's headline software-only deliverable: a native register-trace test that is **RED against today's tree and GREEN after the fix**.
2. **The `eeprom28c_wait_for_write(handle, 0x5555, 0x20)` success check is INVERTED, not merely weak.** Both datasheets state the enable/disable command-sequence data *"is not written to the device"* (DS20006432B §6.6.2 p.10; DS20006386B p.10), so the check can only pass when the sequence was **not** recognised as a command. **PREDICTED, highest-value item to settle first: `firestarter write at28c256` currently aborts at INIT on `3.0.0b11` with an EEPROM timeout.**
3. **gh#11/gh#12 may therefore be LIVE defects, not stale 2024 reports** — which reverses the closeout framing and collapses the backward-compatibility objection to changing the auto-unlock default (if AT28C writes already abort, that cost is ~zero). A separate candidate root cause for gh#11 also surfaced: `eeprom28c_write_execute` polls only **1 byte in 64**, a live "partial write reported successful" mechanism that fits gh#11's symptom better than SDP does.

**Also discovered — an in-tree fact this document previously got wrong:** `include/primitives.h` / `src/proms/primitives.cpp` **do not exist**, and `a296195` (recorded in the v1.16 archive below as the v1.16 tip) is an ancestor of **neither `beta` nor the v1.21 line**. The entire v1.16 Phase-89 primitive recompose sits on an unmerged branch, as does `0052c42`. The real shared seam is `flash_utils.{h,cpp}`; the real trace mechanism is `HOST_STUBS_RECORD_BUS`, which records **only** `rurp_write_to_register` — not data bytes, not strobes. Likewise `page-size` does **not** exist on the wire (`constants.py:107-111` claims firmware sync; `json_parser.c` has no such key). **Do not plan any phase against the primitives layer, the v1.16 golden traces, or a wire `page_size` field.** The v1.16 archive section below is left as written for provenance but is inaccurate on these points.

**⚠ THIRD CORRECTION — Phase 116 close (2026-07-27): TRACE-06 settled, and "all 84" is wrong; it is 66 of 84.** Phase 116's native trace harness (dual-repo, software-only) turned the SECOND REFRAMING's two PREDICTED items into measured findings:

1. **TRACE-06 CONFIRMED: `firestarter write at28c256` does abort at INIT on `3.0.0b11`.** `eeprom28c_write_init` returns `RESPONSE_CODE_ERROR` before any data byte is transferred, for all four `0x0D` pinouts — verified by native trace (`pio test -e native`) driving the real `configure_memory` → `firestarter_operation_init` path with host-derived `bus_config_t` values, per `eeprom28c_wait_for_write(handle, 0x5555, 0x20)`'s 2000-iteration timeout. This is a **software-layer** result: no AT28C part was on the bench, and the bridge to "aborts on real silicon" is a citation (DS20006432B §6.6.2 p.10; DS20006386B p.10 — a part that recognised the sequence cannot return `0x20`), never an observation. Full mechanism, re-run command, and the ceiling-compliant wording: `.planning/phases/116-ground-truth-trace-harness/116-PREMISE.md`; verbatim captured evidence: `firestarter_fw/test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md`.
2. **The "all 84 `0x0D` chips" write-inhibit framing above is superseded — the measured figure is 66 of 84, not all 84.** Per-pinout: `DIP28_28C64` (35 chips) inhibited on 4 of 6 writes; `DIP24_2816` (19 chips) inhibited on 2 of 6 — the *opposite* writes from the DIP28 pinouts (`0x2AAA`, not `0x5555`, because `0x2A` has bit 3 set and `0x55` does not); `DIP28_28C256` (12 chips) inhibited on 4 of 6; `DIP32_28C512_EEPROM` (18 chips) inhibited on **0** of 6 at plain INIT-time register state (its hazard only appears with a stale upper-address bit left by a prior operation, per 116-PREMISE.md §6). `REQUIREMENTS.md` §Framing's "all 84 `0x0D` chips" wording, and the `.planning/research/SUMMARY.md` finding it was drawn from, are both superseded by this table — do not edit `REQUIREMENTS.md` itself; this block is the correction of record.
3. **Validation ceiling unchanged:** `0x0D` stays `UNVERIFIED`, zero chips changed `support_status`, and the 84-chip `0x0D` count is unchanged (it is the *inhibited* count that is corrected, not the population).

**⚠ FOURTH CORRECTION — Phase 117 close (2026-07-28): the two headline defects are FIXED, and gh#11's candidate cause was mis-scoped.** Phase 117 (firmware-only, 5 plans, verified 6/6) closed FIX-01..06 and settles the SECOND REFRAMING's remaining open items:

1. **Both defects named in the SECOND REFRAMING are fixed and proven by the Phase-116 oracle.** `eeprom28c_emit_command_sequence` now drives every command write through `handle->firestarter_set_data` → `mem_util_remap_address_bus`, so `CONTROL_REGISTER` is recomputed per address change (FIX-01) — which closes the `DIP32_28C512_EEPROM` A16–A18 staleness gap for its 18 chips ≥64 KB as a *by-product* of the same routing, not a separate change (FIX-03). The inverted `(0x5555, 0x20)` read-back is **deleted**, replaced by an unconditional `t_WC` wait plus a bounded, silent DQ6 toggle poll that never writes `response_code` (FIX-02). The proof is honest: `git diff e5b9e87..b30b91c -- test_eeprom28c_sdp.cpp` is **empty**, so the suite's RED→GREEN flip came purely from production code, not a relaxed oracle.
2. **gh#11's candidate root cause was mis-scoped as a sampling-rate bug; it is a CONFLATION bug.** The SECOND REFRAMING's item 3 called out "`eeprom28c_write_execute` polls only 1 byte in 64". That undersells it: polling the page's *last byte* IS the canonical AT28C completion protocol. The actual defect is that the same read also served as the data-landed proof, via an equality compare that passes whenever the old byte already equalled the new one — blank `0xFF` regions, unchanged bytes. FIX-06 therefore split `eeprom28c_wait_for_page_write` (DQ7-complement, completion only) from `eeprom28c_verify_page_readback` (always-on, per-byte, failing address attributed), and deleted `eeprom28c_wait_for_write` outright. A test-local replica of the deleted check runs in CI forever, asserted to PASS the same planted partial write the fixed path FAILS. **Aim any future work at the conflation, not the sampling rate.**
3. **Measured, and it contradicts the research prediction: the Leonardo flash delta is `+204 B`, not net-negative.** Recorded as measured with no threshold claim. **Phase 119's LOCK-06 headroom criterion must be judged against this, not against the predicted saving.**
4. **Plan-coverage lesson for Phases 118–122 — the one thing this phase got structurally wrong.** Phase 117 broke **four Phase-116 host-side gates** in `firestarter_app` (`test_sdp_table_parity` ×3, `test_check_no_log_in_sdp_window` ×1) that scan `eeprom_28c.cpp` source text and were keyed to pre-117 identifiers and declaration syntax — 117-02 changed the definition to `EEPROM_SDP_DISABLE[6] =` (the parity regex required `[]`, since a C++ `extern` cannot name an incomplete array type) and replaced `flash_execute_command(...)`; 117-03 deleted `eeprom28c_wait_for_write`. Both gates failed **closed**, and Phase 116 had anticipated this in its own comments (*"ADD the new anchor … rather than deleting this gate"*) — but **no Phase-117 plan owned that step**, so host CI went red and was caught only by the phase's regression gate, after 117-05 had already committed a now-false "zero `firestarter_app` files changed" claim. Fixed append-only (`firestarter_app@9dd11a9`) with honest corrections to both records (`firestarter@f8d10a5`, `117-05-SUMMARY.md`). **Every phase from 118 on must include an explicit task checking firmware renames/deletions against `firestarter_app`'s source-scanning gates** (`tools/check_*.py`, `tests/test_sdp_*`, `tests/test_check_*`). Phase 118's OBS-01 touches this same SDP timing window and will trip the same class of gate.
5. **Validation ceiling held.** The permitted claim is that the sequence is **emitted** as specified, byte-exact by golden register trace across all four `0x0D` pinouts. `0x0D` stays `UNVERIFIED`; zero `support_status` changes; the 84-chip count is unchanged; nothing in this phase is evidence about AT28C silicon state or about gh#11's symptom on hardware. The six FIX-04-frozen artifacts (`include/flash_utils.h`, `src/proms/flash_utils.cpp`, `flash_5v_page.cpp`, `flash_nor_unlock.cpp`, `_shared/sdp_expected.h`, `_shared/sdp_bus_config.h`) are byte-identical to phase base `ada4bdc` by literal blob SHA. **Note for future gate authors:** the ROADMAP's `flash_utils.{h,cpp}` shorthand does not match the real paths — a `git diff -- src/flash_utils.h` check passes *vacuously*.

**⚠ FIFTH CORRECTION — Phase 118 close (2026-07-28): the auto-unlock is now visible and declinable, and the milestone's first real measurement says D-09's "should never fire" premise was optimistic.** Phase 118 (7 plans, verified 5/5 ROADMAP criteria + 12/12 must-haves) closed OBS-01..OBS-05:

1. **Silence is gone, and it is gone unconditionally.** `eeprom28c_write_init` now emits `MSG_INFO_SDP_UNLOCK` (0x5E) before the SDP-disable sequence and `MSG_INFO_SDP_UNLOCK_DONE_US` (0x5F) after it, carrying the `micros()`-measured emit duration. Both go through `LOG_ID`/`LOG_ID_U32`, **not** the `FLAG_VERBOSE`-gated `LOG_INFO_ID*` family — making these the tree's first non-verbose-gated INFO-band call sites, a deliberate break with all 19 existing ones, argued in a source comment per D-01. Following house style here would have left a default `firestarter write at28c256` silent, i.e. a no-op phase. It also makes OBS-05's "byte-identical apart from the two report lines" a real claim rather than a vacuous one.
2. **The user can decline.** `FLAG_SKIP_SDP_UNLOCK 0x100` (the 9th flag; `FLAG_VERBOSE 0x80` was the ceiling, `ctrl_flags` is already `uint32_t`) skips the sequence entirely and emits `MSG_WARN_SDP_UNLOCK_SKIPPED` (0x86) in place of the pair. Per D-02 **nothing on the SDP path writes `handle->response_code`**, preserving Phase 117's D-05 — verified by reading added code lines, not comment text (several comments mention `response_code` precisely to assert its absence). Firmware-only: no CLI flag, no wire emission, no `constants.py` addition — that is Phase 120's boundary and it held.
3. **⚠ FINDING F-118-01 — the measured headroom is 4.7 %, not "never".** The Leonardo emits the six-write sequence in **572 µs against a 600 µs budget** (`6 × AT28C_TBLC_MAX_US`) — 28 µs spare, ~95 µs per byte against a 100 µs per-byte datasheet maximum. CONTEXT.md D-09 framed the runtime check as a latent invariant that *"should never fire"* on a 16 MHz AVR; the measurement says it *barely* does not fire. The implementation is correct and the check is genuinely load-bearing (proven by inverting the comparison and watching native cases 11/12 go RED) — this corrects the **decision's premise**, not the code. **It bears directly on D-10:** `eeprom28c_write_execute`'s page-load loop runs under the identical t_BLC constraint, is where gh#11's slow/failed writes actually live (per the FOURTH CORRECTION's conflation finding), and received a citation comment only with no runtime check. **Phase 119's LOCK-06 should not settle its headroom judgement without measuring the page-load loop's margin too.**
4. **Second flash datapoint: `+152 B` on both Leonardo and Uno**, RAM unchanged, measured against a re-derived phase base. Read together with the FOURTH CORRECTION's `+204 B`, LOCK-06 now has two measurements rather than a prediction to argue with.
5. **The FOURTH CORRECTION's item-4 lesson was applied and it worked.** Phase 117 predicted that *"Phase 118's OBS-01 touches this same SDP timing window and will trip the same class of gate."* It did — redefining the no-log gate's window broke **4 of 6** of its own pytest cases (two built old-shape temp sources that hit the rewritten resolver's fail-closed `ValueError`; one hardcoded `assert "line 29"`). This time a named plan (118-01) owned every one of them as explicit task work, and all 7 phases' worth of host source-scanning gates were re-run at each wave. Zero host CI surprises. **Keep doing this for 119–122.**
6. **D-06 fixed a gate that was looking in the wrong place.** `check_no_log_in_sdp_window.py` previously brace-matched `eeprom28c_write_init` and scanned the span *between* the two call sites — never inside `eeprom28c_emit_command_sequence`, which is where the real inter-byte window lives. It now brace-matches the emitter body **and** `eeprom28c_wait_for_sdp_completion`'s body, so OBS-03's claim finally means what it says. Per D-11 the gate keeps exactly one job: no citation-presence assertion was added, because comment-text gates rot silently and the checker deliberately blanks comment spans.
7. **Validation ceiling held.** `micros()` around six latch writes measures **the MCU driving its own latches**, never AT28C silicon — there is still no AT28C part on the bench. `0x0D` stays `UNVERIFIED`; zero `support_status` changes; no PROTOCOL-LEDGER entry; the 84-chip count is unchanged. D-07's bus-stream byte-identity is proven by literal git blob SHA on all three `test/native/avr/_shared/` files against phase base `f8d10a5`, with **zero golden regeneration**; the two new serial frames are a named, enumerated exception on a channel the Phase-116 recorder does not observe. **Known-and-expected:** `.github/workflows/catalog-sync-check.yml` cannot go green for v1.22 catalog work because it checks out both sub-repos at `ref: main` — the in-phase proof is a local three-way `cmp` plus both `codegen.py --check` gates. Do not read that red job as Phase-118 damage.

**⚠ SIXTH CORRECTION — Phase 119 close (2026-07-28): the milestone's only new state-mutating capability lands, and four separate criterion-mechanism-vs-intent divergences plus three deliberate command-behaviour deltas are gathered here in one place.** Phase 119 (firmware-only, 11 plans) closed LOCK-01, LOCK-02, LOCK-03, LOCK-04 and LOCK-05, left LOCK-06 to Plan 119-10/119-11, and produced the following corrections and findings:

1. **LOCK-04's mechanism is superseded (D-05).** The `default:`-arm mechanism in `configure_eeprom28c` was disproven against live source: `configure_memory` pre-sets the generic `main` for `CMD_READ`, `CMD_WRITE` and `CMD_VERIFY` before the protocol handler runs, so a blanket `default:` arm there would refuse `read` and `verify` on all 84 protocol-`0x0D` chips — the exact class of damage this milestone exists to prevent — and `configure_eeprom28c` only ever runs for `0x0D` anyway, so it could never refuse another protocol. The intent — lock/unlock fail-closed for any protocol other than `0x0D`, never silently accepted — is satisfied instead by one generic NULL-`main` refusal at the operation layer (D-06). **Mechanism-corrected, intent-satisfied — never read LOCK-04 as failed.** `REQUIREMENTS.md`'s LOCK-04 wording was deliberately not edited; its parenthetical records the correction.
2. **Criterion 5's header comment moved (RESEARCH F-K).** ROADMAP criterion 5 asked for a comment in `flash_utils.h`'s header, but that file is FIX-04 byte-frozen and FIX-04 is a closed requirement asserting it byte-untouched — editing it, even comment-only, would re-open that claim and break `118-NONREGRESSION.md`'s framing. The datasheet rationale for the `AA-55-A0` triple-duplication (`FLASH_ENABLE_WRITE`, `FLASH_ENABLE_WRITE_PROTECTION`, the new `EEPROM_SDP_ENABLE`) lives beside `EEPROM_SDP_ENABLE` in `eeprom_28c.cpp` instead, plus the pre-existing comment at `test_sdp_harness.cpp:291-296`, machine-checked by a three-way identity-and-distinctness guard plus a host source-text parity leg (`test_sdp_table_parity.py`). This is the **fourth** mechanism-vs-intent divergence this milestone has produced (after LOCK-04 here, and TRACE-06/FIX-04's own precedents) — **intent satisfied in a different file, deliberately, never a failure.**
3. **LOCK-06's `3348 B` is superseded (D-15), and the `-D DEV_TOOLS` build is confirmed the binding, tighter configuration.** `+204 B` (Phase 117) and `+152 B` (Phase 118) are already spent, so the live Leonardo figure is **25680/28672, leaving 2992 B** — not the pre-117 `3348 B` figure. Judge Phase 119's own delta against 2992 B (Plan 119-10 closes LOCK-06 with the full per-plan arithmetic). Separately, a release-config (`-D DEV_TOOLS` absent) Leonardo build measured **24388/28672** at the phase base — i.e. `-D DEV_TOOLS` **costs 1292 B** (25680 − 24388) rather than saving it, so the `DEV_TOOLS` build carries the **smaller** headroom of the two configurations and remains the binding constraint LOCK-06 must be judged against. `REQUIREMENTS.md`'s LOCK-06 wording was deliberately not edited. <!-- recordscan:history reason: 2992 B was the pre-Phase-119 Leonardo headroom (28672 - 25680), accurate when this v1.22 decision-register entry was written and exactly what Phase 119's own +392 B was judged against (R-10; see 130-RESEARCH.md C-7). Historically correct, preserved as a record, not corrected. -->
4. **DEVTEST-01's firmware half landed in Phase 119, early (D-07/D-08).** The single generic NULL-`main` refusal at `operation_utils.cpp` (item 1 above) also closes `CMD_ERASE`'s and `CMD_CHECK_CHIP_ID`'s phantom-success on `0x0D` — `op_execute_stateful_operation` previously returned `false` on a NULL `main` with **no error logged at all**, so every unconfigured command on every protocol reported OK having done nothing. That is a whole-dispatch-layer defect DEVTEST-01 had noticed one instance of; fixing it generically here was cheaper than fixing it twice, and the operator approved the cross-family regression sweep this required. Phase 121 keeps the **host** half only: `OP_ERASE` marked `NA` for protocol `0x0D` with a named reason in the `dev test` sweep. Plan 119-09 amended `ROADMAP.md`'s Phase 121 scope and `REQUIREMENTS.md`'s DEVTEST-01 mapping to record this; the checkbox stays unticked.
5. **Three command behaviour deltas, all deliberate.** Cmd 7 (`CMD_DEV_ADDRESS`) and cmd 8 (`CMD_DEV_REGISTER`) no longer reach `configure_memory` in a release build — D-01's safety tightening, since a release build previously configured a memory handler for a dev command it was about to refuse anyway; the `MSG_ERR_UNKNOWN_CMD` refusal itself is unchanged. **Cmd 0 (`CMD_IDLE`)** — the third delta, which D-01 does not name (RESEARCH F-B2) — now falls to `loop()`'s pre-existing `case CMD_IDLE: break;` (silence) instead of producing two error frames (`0xBB MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` then `MSG_ERR_SETUP`). An explicit refusal arm for cmd 0 was considered and declined on flash grounds against the live headroom, for a frame no shipped host path emits — `CMD_IDLE` is a firmware-internal state.
6. **`_SRAM_PROTO_IDS` does NOT become dead code (RESEARCH F-F2).** The host's SRAM/FRAM blank-check short-circuit in `firestarter_app/firestarter/eprom_operations.py` fires **before** any firmware command is issued, so D-06's generic guard is unreachable from `check_eprom_blank`'s call path, and the workaround produces a materially better user-facing message than a bare `0xA5` refusal would. Its own comment's claim that firmware emits `0xA4 MSG_ERR_EMPTY_INPUT` is a follow-on artifact of the pre-fix silent completion, not a firmware refusal. **Correct Phase 120 disposition: KEEP, not delete.** Identified in Phase 119, deliberately not touched — host surface is Phase 120's boundary.
7. **A new firmware-source-scanning host gate exists, and one whole-file blob-SHA shorthand is retired.** `check_is_memory_cmd_no_ifdef.py` (Plan 119-03, proving `is_memory_cmd()` carries no `#ifdef DEV_TOOLS` in its body) joins the FOURTH CORRECTION item-4 checklist for Phases 120, 121 and 122, alongside `check_no_log_in_sdp_window.py`, `test_sdp_table_parity.py`, `gen_sdp_bus_config.py` / `test_sdp_bus_config_drift.py`, `test_revision_constants_parity.py`, `check_dispatch.py`, `test_dispatch_mirror.py` and `check_devtest_orchestrator.py`. Also: `_shared/sdp_expected.h`'s whole-file blob SHA **necessarily changed** this phase (Plan 119-05 added four `SDP_FIXED_LOCK_*` arrays), so Phase 117/118's blob-SHA identity shorthand no longer applies to that one file — the identity proof for it is per-array byte-identity of the pre-existing arrays (confirmed additions-only via `git diff`), not a whole-file SHA match. A later phase must not reach for the retired shorthand on this file.

**⚠ SEVENTH CORRECTION — Phase 120 close (2026-07-29): the host surface lands, the SDP-capability partition is re-derived from ground truth, and the operator's `dev test` redesign is folded into Phase 121 as a recorded reversal.** Phase 120 (host-only, 12 plans) closed HOST-01 through HOST-06 and produced the following corrections and findings:

1. **The `dev test` redesign is folded into Phase 121, and it is a REVERSAL (D-20).** Operator specification, 2026-07-29, verbatim: `dev test` takes **no flags**; "destructive" applies only to **UV-erasable EPROMs**; the sweep **stops and asks** whether to do a destructive write, where **yes** means the full device may be written and **no** means only a small part of it is written; **every** run asks whether to file an issue, checking first whether the user already reported an identical one and creating a new issue only when it differs; the `gh` path replaces the URL/browser path wherever it can. This **reverses three locked decisions**, each confirmed verbatim in the live tree: `cli_handlers.py:1811-1815`'s docstring stating `dev_test` *"Issues ZERO interactive prompts about tester-supplied identity (Phase 112 Plan 04 reversal, operator-approved per `112-UAT.md`)"*; `cli_handlers.py:1831-1835`'s *"SAFE-03: the ONLY interactive input left in this handler is the `--destructive` safety confirm"*; and `cli_handlers.py:1760-1762`'s SAFE-01 lock that `--destructive` is *"CLI-only flag -- never read from config or environment"*. Recorded **as a reversal**, the way Phase 119 D-18 recorded reversing Phase 118's D-12 — with its constraints named, so Phase 121's researcher and planner do not read it as the new default. **Phase 120 landed only the amendment** (`ROADMAP.md`'s Phase 121 scope, `REQUIREMENTS.md`'s DEVTEST-02..06, this correction block) — **none** of the redesign's implementation.
2. **"Non-destructive means a partial write" is a contract change, not a flag change.** `derive_plan` (`chip_test.py:319-425`) structurally omits `OP_WRITE`, `OP_VERIFY` and `OP_ERASE` from `Plan.steps` when `destructive=False` today, recording them only as `(op, reason)` tuples on the advisory-only `Plan.locked_destructive` list, whose docstring (`:298-316`) states `run_plan` **MUST NOT** iterate it — there is no code path from `run_plan` to a destructive op on a non-destructive plan as the code stands. A third "partial write" mode therefore needs a **new representation**, not a flag flip. Its ripple set, all confirmed present in the tree: the closed six-string op vocabulary `OP_ID`/`OP_READ`/`OP_BLANK_CHECK`/`OP_WRITE`/`OP_VERIFY`/`OP_ERASE` (`chip_test.py:273-278`); `tools/parse_devtest_issue.py`; `diagnostic_report.py`'s renderer and its `ladder_state` tag (`:247`, GRAD-01); `dedup_fingerprint` (`diagnostic_report.py:177`, read back by `submit.py:169-174`); and `tests/test_audit_coverage_matrix.py`'s golden — **which is already RED**, pre-existing and not caused by this phase, so a matrix-touching Phase 121 change lands on top of an existing failure and must not be allowed to mask it.
3. **"Destructive only for UV-erasable" needs an explicit axis pick, and the obvious axis is unavailable where it is needed.** `electrical.type == "UV-EPROM"` exists in the DB (**301 parts**, measured) and *is* reachable in `derive_plan`, which reads `full = db.get_eprom(name)`. It is **not** reachable at the execution layer: `run_plan` → `_resolve_or_none` → `resolve_chip` (`chip_test.py:505`), whose returned dict drops `electrical-type`. The project already worked around this once, at `_write_region_for` (`:637-663`), falling back to `algorithm == 0x0B`. **Measured coverage of that fallback: 32 of 301.** UV-EPROM by algorithm: `0x07` → 163, `0x08` → 106, `0x0B` → 32 — so the existing execution-time UV signal **misses 89 % of UV parts**. Any Phase 121 design gating destructiveness on "UV-erasable" must either widen the algorithm set to `{0x07, 0x08, 0x0B}` (structural, no type-string dependency — this project's stated preference, since `protocol_id` is the algorithm axis and **not** the UV-versus-EEPROM axis) or thread the `full` dict to the execution layer.
4. **`--submit`'s contract is reversed, and its wrong-repo defect is a released-artifact fact, not a source defect.** v1.21's SUB-01/SUB-02 lock `--submit` as *"explicit + interactive-only; never on a bare run"*; DEVTEST-05's always-ask contradicts that, recorded as reversed in `REQUIREMENTS.md`, not silently dropped. Separately: `firestarter_app/firestarter/submit.py:73` already reads `SUBMIT_REPO = "henols/firestarter_prom"` on this branch (commit `e615b4c`) and on `beta`, pinned by `tests/test_submit.py:237`. The `v1.21` tag still carries `henols/firestarter_app`, which is why shipped `3.0.0b11` misfiles — so **no source change is needed**, and the fix reaches users only at the next beta cut. Also record that `gh issue create --label` aborts before creating unless the label pre-exists **and** the user has write access, which community testers have neither of, so any `gh`-first design must assert the **negative** argv (`tests/test_submit.py:301-320`'s idiom).
5. **SIXTH CORRECTION item 6's stated reason is false; its disposition stands.** `check_eprom_blank`'s `_SRAM_PROTO_IDS` short-circuit reads `electrical-type` and `protocol-id` from the dict its callers pass, but both production callers (`cli_handlers.py:576`, `chip_test.py:737`) pass `resolve_chip`'s **programmer** dict, which carries neither — measured returning `False` for a real SRAM part. **The short-circuit is vacuous in production.** Item 6's KEEP disposition is still correct; its stated reason — that it fires and produces a materially better message — is **not**. Phase 120 recorded this, did not fix it and did not delete the code. The consequence that made this load-bearing: a `sdp_capability` predicate keyed on the same programmer dict would have reproduced the identical silent vacuity, which is why the predicate is **name-keyed** (via `db.get_eprom(name)`) and why `tests/test_sdp_capability.py` ships a dict-shape anti-vacuity leg — a validation surface this milestone had to invent because of this finding.
6. **The HOST-04 partition is derived, not curated.** ALLOW **43** / REFUSE **41** = 84, from minipro `infoic.xml` `<database type="INFOIC2PLUS">` `flags` bit 15 (`0x8000`, `MP_PROTECT_AFTER`) at commit `a8efaedc236c1d9718bd28299dfbb99536b010ff`; all 84 matched, zero unmatched, zero MIXED; three independent ground-truth probes passed 8/8, 2/2 and 4/4. This **supersedes** `120-RESEARCH.md` F-01's curated 37/47 and the interim 74/10 placeholder. The mechanism is unchanged — a static fail-closed allow-list in `firestarter_app/firestarter/sdp_capability.py` plus a runtime exhaustiveness gate; nothing reads `infoic.xml` at runtime or in CI and it is **not** added to either sub-repo. The 2026-07-10 `infoic-xml-protection-flags-research.md` verdict **stands**, scoped to the protection-kind/status-readable taxonomy, and received an append-only scoped exception. Two recorded-not-acted-on findings: `doc/lockable-proms.md` §17 is wrong about `AT28C16` (GATE-02, Phase 121), and bit 15 is **not** a page-write proxy — it disagrees with `page_size > 1` on 12 of 84, with the nine residual-risk entries named in `120-WATCHLIST.md`.
7. **Two ROADMAP/catalog corrections restated.** There is **no** `0x200` flag — firmware's flag block ends at `FLAG_SKIP_SDP_UNLOCK 0x100`, so `ROADMAP.md:363` and Phase 120's *Depends on* line are wrong and the host wires **one** flag; `REQUIREMENTS.md` was deliberately not edited for this. And `MSG_INFO_SDP_UNLOCK_DONE_US` (`0x5F`) still lacks the honesty caveat `0x61` carries — answered host-side by D-10's symmetric summary line, with the catalog fix deferred to Phase 121/122.
8. **The class lesson worth keeping.** Phase 118's OBS-01 was verified in firmware and discarded by the host for a whole phase, because `_log_rurp_feedback` mapped the entire INFO band to `logging.DEBUG` while root is `INFO` unless `-v`. **A two-repo requirement can pass its own phase's verification and still be false end to end.** Phase 120's D-09 fixed it and, in doing so, also made Phase 35's CR-02 hard-fail-loud revision warning (`0x5B` `MSG_INFO_HW`, emitted through the unconditional `LOG_WARN_ID_U8` alias) visible for the first time — **six** newly-visible ids, not five.
9. **FOURTH CORRECTION item 4's checklist held.** The nine-row cross-repo gate outcome (Plan 120-12 owns the sweep and the `120-NONREGRESSION.md` artifact); **row 7** was deliberately rebuilt by this phase so "unchanged" is the wrong verdict for it, and **row 9** (`check_devtest_orchestrator.py`, which scans `cli_handlers.py`) was the one host-side row at real risk. Item 5's warning restated in its honest form: a path-scoped `git diff` can pass vacuously, so the proof used is `git -C /workspaces/firestarter status --porcelain` being empty, which subsumes every path.

**⚠ EIGHTH CORRECTION — Phase 122 close (2026-07-30): the milestone's headline defect is now confirmed on real AT28C256 silicon by a community report, while the fix remains unproven.** Phase 122 (13 plans; closing CLOSE-01 through CLOSE-03) records the following correction, surfaced while preparing this phase's community follow-up (D-10):

1. **The headline premise is silicon-confirmed by a stranger; the fix is not (D-10).** On 2026-07-27 the author of gh#11 re-ran `firestarter write at28c256` on `3.0.0b11` against a real AT28C256 and pasted the exact inverted-check INIT abort — `ERROR: EEPROM timeout at 0x005555: wrote 0x20 got 0xff` — that Phase 116 could only predict in software. This raises TRACE-06 from software-predicted to **community-corroborated**. State the provenance honestly and in these terms: an issue-comment paste, no captured logs beyond the text, board revision and firmware build unconfirmed. State the asymmetry explicitly: the **defect** now has silicon evidence; the **fix** does not. `0x0D` stays `UNVERIFIED` in `PROTOCOL-LEDGER`, **zero** chips changed `support_status`, and the 84-chip `algorithm == 13` count is unchanged — all three re-verified on the merged tree (`122-NONREGRESSION.md`). No AT28C silicon was tested during this milestone by the operator; this community datapoint is the sole third-party exception, and it confirms the defect only.
2. **Their re-test looked like a regression and was not — say so, because the reporter will not assume it.** In 2024 the write *completed*, reporting success after 339 s, and silently burned only part of the image. On `3.0.0b11` it hard-fails at INIT. That is the fix landing halfway: the inverted success check turned a silent partial write into an honest refusal. Anyone reading b11 as *worse* than 2024 is reading it reasonably and wrongly.
3. **A locked decision was corrected before it reached a stranger (C-5).** D-14 prescribed telling another gh#12 participant that their AT28C parts had become able to do what they wanted. Measured across the full 84-entry `0x0D` set with the production predicate, every 2K×8 part sits on pinout `DIP24_2816` and **all 19 of 19** are REFUSED by the SDP allow-set — 7 as pre-SDP generation, 12 as unrecognised — and the shipped `dev sdp --help` text says so itself. The reply is therefore phrased **by size class, not by an assumed part number**, and states the refusal plainly. This is recorded as a **divergence from a locked decision**, flagged for the operator's accept-or-overturn at the D-16 wording review (`122-LEDGER.md` carries the same flag), not a silent rewrite. *Emission traced byte-exact for a pinout* and *the operation permitted on parts with that pinout* are different claims.
4. **CLOSE-01's implied `check_ledger.py` is pre-existing RED, was not gated on, and was not fixed (C-4).** It exits 1 with two `LEDGER-01` violations because rows `0x05`/`0x06` carry `matrix_family` `flash4`/`flash3`, which v1.19 Phase 104 renamed to `5v_page`/`nor_unlock`. `tools/validation_matrix_spec.json` is absent from the `beta...HEAD` diff, so this is not v1.22's damage. CLOSE-01's text does not mention the tool. Fixing it would edit a closed milestone's artifact — exactly what D-09 refuses. Recommend a backlog seed.
5. **D-06's conflict set was wrong, and the correct resolution is a structural proof rather than a green suite (C-1/C-2/C-11/C-12).** The firmware inbound merge had **zero** conflicts; the app conflicted in exactly two files, `firestarter_app/firestarter/submit.py` and `tests/test_submit.py`. `include/version.h` and `firestarter_app/firestarter/__init__.py` both auto-merged and were never conflicts. Resolution was whole-file `--ours`, justified by a mechanical superset proof (all 60 of `beta`'s `test_submit.py` functions exist among branch HEAD's 77) and proven by an **empty diff**. Hunk-level resolution was forbidden: hunks 3 and 4 sandwich a shared region branch HEAD needs twice, and a textual "ours" there produces code that **compiles and passes while being wrong**.
6. **The manual `publish.yml` dispatch is the norm, not a contingency (C-3).** Six of thirteen published app GitHub betas never reached PyPI — b4, b5, b6, b9, b10, b12 — a 46% historical miss rate, caused by `beta-release.yml` creating the release with a PAT that lacks `workflow` scope, which suppresses the `release.published` event. `publish.yml`'s own in-file comment documents the mechanism. *"CI is green"* is not evidence a channel is live, which is why the accept/avoid/cleanup decision (`122-DECISION.md`) gated the community comments on a resolution check rather than a workflow status.
7. **The published cut tag is read, never assumed (A3), and `ci.yml` never runs on a `beta` push (C-8).** CI producing the next beta number is derived from `update_version.py`'s git-tag scan, not executed, so every downstream step consumes the observed tag. And the merge push fires only `beta-build.yml` / `beta-release.yml`; `ci.yml` and firmware `build.yml` trigger on `main` and pull requests only. A green beta workflow is therefore a **narrower** statement than "CI is green": no ruff, no mypy, no coverage floor, no vector-catalog gate, no CLI smoke test ran. The four pre-existing `ruff check` findings and four `ruff format` drift files all sit in `tools/` + `.github/scripts/`, outside `ci.yml`'s `firestarter_fw/ tests/` scope — structurally invisible, and deliberately not fixed here.
8. **One owned trade-off, chosen with its cost named (D-01).** No bench smoke-test of the published beta's install/flash path was run, so the `pip install --pre` → `firestarter fw -i` → one-live-op chain that Phase 115 existed to prove is **trusted, not re-verified**, before two community members are pointed at it. Recorded in `122-DECISION.md` so no downstream agent quietly re-opens it, and so that if an install problem surfaces the record shows a known, accepted gap rather than an oversight.
9. **The class lesson: this milestone's closing criterion is only half mechanizable.** ROADMAP criterion 4 — every claim in the closing documentation matches the validation ceiling — splits three ways. The *mechanizable* half is a forbidden-phrase / required-caveat gate over the closing artifacts (`check_permitted_claims.py`), shipped with two committed planted-violation fixtures under the GATE-01 anti-hollow discipline. The *judgement* half is the D-16 blocking operator wording review, because a string scan cannot detect an implied overclaim, a misleading omission, or wrong tone. And one whole class — whether the SDP mechanism is effective on real AT28C silicon — has a sampling rate of **zero, permanently, by design**. A green claim-scan must never be reported as satisfying criterion 4.

- **No AT28C part in operator inventory** (confirmed with operator at milestone start; the recorded inventory in `project_phase83_shipped` has none) → **software-only validation**. Leonardo would have been the only board whose verify read is a valid PASS had a part been available.
- **Dual-repo lockstep** — firmware (`0x0D` handler + command surface) + host (CLI + wire). Phase numbering continues from v1.21's Phase 115 → **v1.22 starts at Phase 116**.
- **Branch base is clean this time:** v1.21 IS merged into `beta` in both sub-repos (`beta` is 1 merge commit ahead, 0 behind, in each), so v1.22 branches fork off `beta` per standing policy — reversing the v1.15/v1.21 fork-off-the-previous-version-branch exception.
- **Topology note for planning:** commit `0052c42` (v1.16 Phase 89-01 "delete dead FLASH_ENABLE_WRITE_PROTECTION + redirect EEPROM_SDP_DISABLE") is an **abandoned commit** — not an ancestor of `beta` nor of the v1.21 line. Its dedup was never merged, so both the local `EEPROM_SDP_DISABLE` table and the zero-caller `FLASH_ENABLE_WRITE_PROTECTION` table are live in the tree. Do not assume that cleanup happened.
- **Precedent in-tree:** v1.13 Phase 74 (SST-style SDP + page write on `flash_5v_page`), v1.14 Phase 77 (erase write-path wired from `electrical.type`).
- **Explicitly out of scope:** the `lock-status` command + hand-curated protection table (stays planted at `.planning/seeds/lock-status-command-hand-curated-protection-table.md`); AMD Autoselect and Winbond product-ID protection-state query sequences.
- Queued roadmap slots shift to **v1.23–v1.28** (Binary Command Protocol, Bus-Config Mask-Model, Jumper/2516, Voltage Calibration, Per-Protocol EPROM Algorithms, PY32F071 Port).

## v1.21 Archive: Community Chip-Validation Command — Shipped 2026-07-27

**Goal:** Ship a `firestarter dev test <chip>` command that lets a community member run a full, technology-aware capability sweep on a chip the maintainer doesn't own, then file an actionable diagnostic report back — turning chip coverage from "what's on Henrik's bench" into "what's on everyone's bench."

**Target features:**
- **Per-chip test-plan engine** — derive the supported operations from the chip's protocol/family (`classify()`); run id, read, write, verify, erase, blank-check as **independent, non-fatal steps** (a locked boot block or unsupported erase is a *finding*, not an abort — the W29C040 lesson).
- **Technology-aware destructiveness** — non-destructive by default (id + read + blank-check); a loud `--destructive` gate unlocks write/erase on a scratch chip; UV EPROMs get a **small-region write** so an eraser-less tester can retry. Non-destructive runs must state "only N of M tests ran."
- **Diagnostic report (dual output, one run)** — a self-contained issue body: human-readable results table + a fenced JSON block. Two-tier field contract: **auto-capture** FW/board/host version, chip-ID expected-vs-actual, protocol path, error codes, byte-mismatch fingerprint, measured VPP/VPE, transport health, DB entry; **prompt** the tester for shield revision, chip provenance, and pot adjustments (firmware can't self-report these).
- **Submission flow** — tiered `--submit`: `gh issue create` (auto-labeled → `gsd-inbox`) when `gh` is present and authed, else a prefilled browser issue URL; a gist/attachment path is reserved for the rare verbose failure log that overflows URL limits.

**Key context:** Promoted from the `/gsd-explore` 2026-07-02 seed `.planning/seeds/community-chip-validation-command.md` (design decisions in `.planning/notes/dev-test-design-decisions.md`; two open research questions — health-proving write pattern fixed-vs-address-derived, and whether a community PASS auto-graduates `support_status` — in `.planning/research/questions.md`). This is the strategic unlock for the project's recurring "can't verify — operator doesn't have that chip" deferrals. Phase numbering continues from v1.20's Phase 107 → **v1.21 starts at Phase 108**. Branch model per standing policy (forks off `beta`); **sequencing flag:** v1.20's protocol-only-dispatch code is not yet on `beta` (its lockstep beta cut `3.0.0b11` + gitlink bump stay operator-gated, gitlinks PINNED at b10) — resolve the branch base at execute time to avoid a v1.12-style base collision.

## v1.20 Archive: Protocol-Only Dispatch — Remove the Legacy `mem_type` Axis — Shipped 2026-07-02

**Goal:** Delete the vestigial `mem_type`/`type` backward-compat dispatch axis so Firestarter trusts *only* the real protocol (`handle->protocol` / `algorithm`) end to end — firmware, wire, and host.

**Target features:**
- **Firmware:** delete the `mem_type` fallback dispatch chain (`memory.cpp` steps 7–11) so `protocol == 0` fail-closes instead of falling back; drop the `handle->mem_type` struct field, stop parsing the `type` JSON field, retire `MSG_ERR_MEM_TYPE_UNSUPPORTED (0xAE)`.
- **Wire:** remove the `type` field from the JSON command contract entirely (breaking for hand-crafted JSON / pre-v1.20 hosts).
- **Host:** stop emitting `type`; remove `_ALGO_MEM_TYPE` + the "Generic Flash (legacy fallback only)" default in `database.py`; remove the `mem_type`-keyed legacy label fallbacks in `ic_layout.py`. Every chip entry must carry an `algorithm`.
- **Guards:** keep the v1.16 golden traces + dispatch-mirror guard + `check_dispatch.py` / `diff_db.py` green; over-voltage stays blocked; no `chip_database.json` *value* change for real chips.

**Key context:** the fallback is already **dead code for every DB chip** (all carry `algorithm`) — this is a legibility/safety cleanup, not a behavior change for real chips. Accepted consequence: **user-override DB entries lacking `algorithm` will no longer work** (must specify a protocol). Firmware-touching → dual-repo lockstep (`constants.py` ↔ `firestarter.h`); watch the py3.12-masks-CI-3.11 ruff/codegen drift trap. Branches off `beta` in all 3 repos; gitlinks PINNED; lockstep beta cut + stable promotion operator-gated. NOT in scope: the canonical `electrical.type` *string* (v1.16 classification, unrelated to numeric `mem_type`); phantom arms (0x35/0x39) and named-infeasibility arms (0x11/0x2A–0x2C), which are fail-closed forward-compat, not legacy. Phase numbering continues from v1.19's Phase 104 → **v1.20 starts at Phase 105**.

## v1.18 Archive: AM27C020 0x08 Write-Path RCA & Fix — Shipped 2026-07-01 (fix bench-effective-but-unreliable; AM27C020 graduation deferred → FUT-08)

**Outcome:** RCA named **RC-1** — DIP32 socket pin 31 is modeled as address line A18 (`DIP32_STD`) rather than a held program-active /PGM pin, so the AM27C020 receives VPP but never a program strobe (classified host-pinout + firmware-algorithm; the passing `0x07` W27C512 wrote byte-exact in the same session, exonerating every shared axis). The fix — a scoped `DIP32_27C020` pinout with `rw-pin:[31]` resolving pin 31 to `CTRL_READ_WRITE` (0x40) via the existing revision-invariant `rw_line` mechanism, distinct from the `0x08` VPP alias that made the first attempt (CR-01) a physical no-op on Rev 2.x — is dual-repo lockstep (`MAX_27C020_SIZE` both sides), size-gated to ≤256K (27C040/27C080 stay `DIP32_STD`), 119/119 native tests, golden traces byte-identical. Bench proved the fix **effective** (write#1 60/64 byte-exact, refuting the Phase-97 0-bits signature) but **marginal/unreliable** (write#2 0/64). No byte-exact graduation → honest **DEFER**: AM27C020 carried forward as **FUT-08** (FUT-06 retired-by-replacement; next step = characterize program-window VPP-under-load at socket pin 1 + write timing), PROTOCOL-LEDGER `0x08` stays open-defect-carried. 11/11 requirements (PRE/RCA/FIX/BENCH/SAFE — BENCH-01 met via the documented deferral branch); audit `tech_debt` (3/3 phases passed, integration 6/6 WIRED, 0 broken flows, 14 pre-existing cross-milestone items acknowledged-deferred). Meta tagged `v1.18` + gsd planning merged to `beta`; lockstep beta cut + gitlink bump operator-gated. Full detail: `.planning/MILESTONES.md` §v1.18 + `.planning/milestones/v1.18-ROADMAP.md` + `.planning/milestones/v1.18-MILESTONE-AUDIT.md`.

<details>
<summary>v1.18 original scope framing (pre-close)</summary>

**Goal:** Root-cause why the AM27C020 (`0x08` EPROM-QUICK, 32-pin Large EPROM) programs **0 bits**, fix the 32-pin write/VPP path so it programs correctly, and bench-prove write→verify on real silicon — gated on a Tier-0 silicon-writability pre-flight (the W29C040 lesson: confirm the chip is re-programmable before committing the bench graduation).

**Target features:**
- Reproduce + root-cause the AM27C020 `0x08` 32-pin write/VPP failure (0-bits-programmed) on Leonardo + Rev 2.0 — differentially vs a working EPROM path (e.g. the passing `0x07` W27C512), naming the cause (VPP rail / program-pulse / 32-pin Large-EPROM addressing / silicon).
- Fix the `0x08` (EPROM-QUICK) write/VPP path in firmware (`eprom.cpp`) and/or host; keep the v1.16 golden traces + dispatch-mirror guard green; native + dual-repo-lockstep coverage.
- Tier-0 silicon pre-flight (blank/writability check) as the hard first gate; if the chip is OTP/already-programmed, re-scope to software-fix-only with bench graduation deferred (FUT).
- Bench-prove byte-exact write→verify on the AM27C020 (if writable); CI green on py3.11; over-voltage stays blocked (SAFE).

**Key context:** FUT-06 (carried from v1.15) — "AM27C020 0x08 32-pin write/VPP path; RCA'd, 0-bits-programmed, JP4-closed didn't fix; not trivially fixable." On-hand silicon, state unknown. Bench LOCKED to Leonardo + RURP Rev 2.0 (standing discipline: live R1/R2 readback + `controller:` identity per task). Domain research on 27C-series CMOS EPROM programming (VPP levels, program/verify algorithm, 32-pin Large-EPROM addressing, pitfalls) precedes requirements. W29C040 (FUT-07), X88C64 (FUT-01), AT28C adapter (FUT-04), 2516 (FUT-03), 0x08-rewritable (FUT-05) remain deferred — out of scope.

</details>

## v1.17 Archive: Implement & Test the W29C040 Programming Protocol — Shipped 2026-06-29 (software complete; W29C040 graduation deferred → FUT-07)

**Outcome:** RCA proved the W29C040 page-0 "fault" is NOT a firmware bug — the operator's seated chip has a **permanently locked §6.6 first-16K boot block** (datasheet-irreversible), so the byte-exact full-image graduation is hardware-blocked and needs a different unlocked sample (→ third-party bench, **FUT-07**). Delivered + verified instead: the T-93-CANERASE 12V-on-5V safety fix (host+fw), proactive §6.6 boot-block lockout detection (error / `--force`→warning), datasheet-sourced per-chip `page_size` wire field (CR-01), writable-region (≥0x4000) N=3 SHA bench proof, py3.11 CI green. 11/16 requirements satisfied (RCA/FIX/PGSZ/SAFE); 5 deferred → FUT-07 (BENCH/LEDGER). CR-01/Phase-74 Wave-2 remains open (rolled into FUT-07). Full detail: `.planning/MILESTONES.md` §v1.17 + `.planning/milestones/v1.17-ROADMAP.md` + `.planning/milestones/v1.17-MILESTONE-AUDIT.md`.

**Original goal (not fully met — graduation hardware-blocked):** Root-cause and fix the W29C040 flash4 (`0x05`) page-write defect on real silicon, generalize flash4 page sizing to a datasheet-sourced per-chip DB field, and bench-prove a byte-exact write→read→verify on the operator's seated W29C040 — graduating it to genuinely `supported` and closing CR-01 / Phase-74 Wave-2.

**Target features:**
- **RCA the W29C040 page-0 write fault** — page size is *already* correct (256 B), so the root cause is deeper than CR-01's capacity heuristic. Differential against the passing `0x05` sibling W29C020. Candidate causes: SDP unlock sequence, page-write polling/timing (DQ7/DQ6 toggle), A18 (512 KB) addressing.
- **Fix the defect in firmware** — `firestarter_fw/src/proms/flash_type_4.cpp`, built on the v1.16 primitives recompose (`a296195`); dual-repo lockstep if a new wire/DB datum is required.
- **Generalize CR-01** — add a datasheet-sourced per-chip `page_size` to the DB pipeline (`build_db.py` / `chip_database.json`) replacing the `flash4_page_size(mem_size)` capacity heuristic, so the under-sized 64 KB (128 B) and 256 KB (256 B) flash4 families are correct too. Likely a lockstep wire field.
- **Bench-prove byte-exact** write→auto-erase→program→verify SHA on the seated W29C040 (Leonardo + RURP Rev 2.0) — the hard graduation gate (no best-effort fallback authorized).
- **Record evidence** — update the PROTOCOL-LEDGER / per-chip EVIDENCE; W29C040 `0x05` → PASS / `supported`.

**Key context:**
- **Branch base:** firmware forks off the **v1.16 tip `a296195`** (the primitives recompose), NOT firmware `beta` (stale at v1.13 `a1953c2`, lacks v1.15 VPP-skip + v1.16 recompose). Mirrors the v1.15/v1.16 precedent of forking off the prior milestone tip while the lockstep beta cut stays operator-gated (gitlinks PINNED at b10). Meta `.planning/` proceeds per convention.
- **Dual-repo lockstep** (`constants.py` ↔ `firestarter.h`) if the `page_size` datum crosses the wire; reuse-first (no new third-party deps); watch the py3.12-masks-CI-3.11 ruff/codegen drift trap for host DB-pipeline changes.
- **Bench LOCKED to Leonardo + RURP Rev 2.0** — the only trustworthy program/write/verify combo (v1.9 read bug corrupts the oracle elsewhere). Standing bench discipline: live R1/R2 readback each task, verify `controller:` port identity per task, Leonardo is chip-OUT-sideload-exempt. Operator seats the W29C040 so the bench can be driven unattended.
- Phase numbering continues from v1.16's last phase (92) → **v1.17 starts at Phase 93**.
- Picks up **CR-01 / Phase-74 Wave-2** (W29C040 flash4 256 B page-0 fault) — open since v1.13, confirmed not-silicon-effective at v1.15 Phase 82/84.

## v1.16 Archive: Protocol-First Architecture Rebuild — Shipped 2026-06-26

**Goal (achieved):** Turn Firestarter's inherited-from-minipro hex-ID protocol buckets into a named, datasheet-verified, primitive-decomposed architecture with a per-protocol bench-verification ledger — shrinking the Leonardo flash ceiling via shared-primitive reuse — while keeping the minipro DB as ground truth (now *extracted correctly* via full variant decode rather than a hand-maintained override stack).

**Delivered (28/28 requirements):**
- **Datasheets (DSHEET-01/02/03):** top-level `datasheets/` folder — 17 PDFs (11 on-hand chips across 6 buckets + 6 no-silicon representatives) + `README.md` index (hex ↔ name ↔ handler ↔ datasheet ↔ on-hand status), phantom/infeasible buckets named as honest exclusions.
- **Variant decode + correct DB regen (VAR-01..05):** `infoic.xml` `variant` field decoded in full (low byte = pinout discriminator; high byte = minipro `algo_number`, NOT a classifier — `database.c#L1918`, pinned SHA `a8efaedc`); `build_db.py` rewritten to one principled `classify()` deriving `electrical.type`/`algorithm`/`pinout`, **deleting** the Rule 1/2/3 override blocks. FM1608→SRAM_STD (0x28) + X88C64→EEPROM now fall out structurally. DB 744→746 with the 2516/2532 non-upstream supplement (`tools/extra_chips.json`); `diff_db.py` IDENTITY exit 0, both baselines re-pinned; `check_dispatch.py` 0 violations; EVIDENCE-11 wire-stable.
- **Naming + docs (NAME-01..05):** `firestarter_fw/doc/PROTOCOLS.md` 12-bucket protocol vocabulary (hex → name → datasheet-verified behavior) + each handler's *why* cited to its datasheet + INV-01..09 one-off-fix invariants as a native-test traceability matrix; flash delta 0.
- **Primitive recompose (PRIM-01..06):** per-family byte-exact golden register traces + `dispatch()`-matches-documented-order guard established as the oracle, then P7 SDP-table dedup → P4 chip-ID compare/report → P3 VPP gate (keyed on `handle->protocol`) → P5 poll/verify extracted, each guarded by native suites + `check_dispatch.py` + `diff_db.py`. Net flash **decrease**: 25136 B / 87.7% / −518 B vs the 25654 B baseline. fw `a296195`.
- **Bench ledger (LEDGER-01/02/03):** `.planning/milestones/v1.16-artifacts/ledger/PROTOCOL-LEDGER.{md,json}` + stdlib-only `check_ledger.py` self-consistency gate, composing with (not replacing) the v1.13 matrix + v1.15 EVIDENCE. All 4 on-hand protocols PASS on Leonardo + Rev 2.0 (0x05 W29C020, 0x06 SST39SF040, 0x07 W27C512, 0x28 FM1608); 6 no-silicon buckets explicit UNVERIFIED; open defects (W29C040 CR-01, AM27C020 FUT-06, 2516 FUT-03) carried at documented status.
- **Safety + hardening (SAFE-01..06, HARD-01):** every primitive keys on `handle->protocol` (never `electrical.type`); over-voltage stays blocked at the firmware VPP check; `chip_resolver.resolve_chip` host guard never bypassed; 2516 stays UNVERIFIED (not spent). The Phase-90/91 "12V-VPP write-path regression" was RCA'd as a **test-method error** — `write -b` set `FLAG_SKIP_ERASE`, leaving NOR/EEPROM bits unprogrammable (recompose proven innocent via b10 A/B) — then **Phase 92 (HARD-01)** decoupled `-b`/`--no-blank-check` from skip-erase in the host (pre-write erase still runs for `FLAG_CAN_ERASE` chips; new explicit `--skip-erase` opt-in), eliminating the footgun. Host-first; firmware byte-identical for the host-only phases.

**Known deferred items at close:** 14 open artifact items acknowledged & deferred (see STATE.md "Deferred Items") — 12 pre-existing carry-forwards + 2 v1.16-born Phase-85 operator-confirmation gates on a zero-code-risk acquisition phase.

See `.planning/MILESTONES.md` §v1.16; ROADMAP archived at `.planning/milestones/v1.16-ROADMAP.md`; requirements at `.planning/milestones/v1.16-REQUIREMENTS.md`.

<details>
<summary>v1.16 original scope framing (pre-close)</summary>

**Goal:** Turn Firestarter's inherited-from-minipro hex-ID protocol buckets into a named, datasheet-verified, primitive-decomposed architecture with a per-protocol bench-verification ledger — shrinking the Leonardo flash ceiling (~89.5% today) via shared-primitive reuse, without changing the minipro DB as ground truth.

**Target features (staged):**
- **Datasheet acquisition** — new top-level `datasheets/` folder: all 11 on-hand ICs + one representative chip per no-silicon minipro protocol bucket, so every protocol has a verification source.
- **Naming + documentation pass** — author the protocol vocabulary (hex bucket → proper human name → datasheet-verified behavior) and document each firmware handler's *why* (timing, VPP, pin roles, write/erase algorithm). Dispatch structure unchanged; near-zero flash delta.
- **Primitive decomposition / refactor** — extract shared primitives (address setup, data strobe, poll/verify, VPP gate, page buffer, SDP unlock, chip-id), recompose handlers from them, measure flash savings; incremental, one protocol family at a time, guarded by native register-level tests + `check_dispatch.py` / `diff_db.py`.
- **Per-protocol bench validation** — bench-prove each protocol with silicon on Leonardo + RURP Rev 2.0; record results in a per-protocol verification ledger composing with the v1.13 per-family matrix + v1.15 `EVIDENCE.{md,json}`; carry no-chip protocols as explicit `UNVERIFIED`.

**Key context (locked decisions from the `/gsd-explore` 2026-06-25 session):**
- Minipro/infoic-derived `chip_database.json` STAYS the ground truth for firmware control values; datasheets only verify interpretation + document the *why* (preserves algorithm-first dispatch / no-guessing). **(Scope amended 2026-06-25: Phase 86 now decodes `variant` in full + regenerates a correct DB, deleting the Rule 1/2/3 override stack — DB-frozen lock lifted for Phase 86 only, with an explained diff + re-pinned baseline.)**
- Naming = both-in-sequence: rename + document existing buckets first (structure stable), THEN re-decompose into shared primitives.
- "Working" = bench-proven on **Leonardo + RURP Rev 2.0 only** (the only trustworthy combo, v1.9 read bug elsewhere); no-chip protocols stay explicit `UNVERIFIED` — honest gaps, never false confidence.
- Driver = shrink ~89.5% flash via shared-primitive reuse (duplication across `configure_eprom`/`configure_sram`/`configure_flash`/flash4 is the main culprit).
- Dual-repo lockstep for any wire-touching change (`constants.py` ↔ `firestarter.h`); reuse-first (no new third-party deps); watch the py3.12-masks-CI-3.11 ruff/codegen trap.
- Seed: `.planning/seeds/protocol-first-architecture-rebuild.md`; rationale: `.planning/notes/protocol-rebuild-rationale.md`; open research questions: `.planning/research/questions.md` (protocol-rebuild block).

</details>

## v1.15 Archive: Bench Validation of Operator Inventory — Shipped 2026-06-25

**Goal (achieved):** Bench-validate the operator's 11 physical chips (5 algorithm families) on Leonardo + RURP Rev 2.0 via full write→read→verify — proving the on-paper `supported` claim true on real silicon, RCA-ing/fixing failures, validating DB decode, producing a per-chip evidence record, and graduating the one genuine gap (the `2516`).

**Delivered (21/23 requirements satisfied · 2 closed-by-disposition):** All 11 chips exercised on silicon and recorded in `.planning/milestones/v1.15-artifacts/bench/EVIDENCE.{md,json}` + consolidated `.planning/milestones/v1.15-artifacts/DECODE-AUDIT.md`. **Silicon PASSes:** W27C512 + SST27SF512 (0x07), SST39SF040 (0x06), W29C020 (0x05 — first Flash/EEPROM auto-erase silicon proof), FM1608 (0x40 overwrite), ST M27C512 UV write (0x07, operator-directed partial spend). **Genuine FAILs faithfully recorded (not DB/algo faults):** W27E512 / W27E040 stuck-bit silicon wear (D-32 silicon-limited); W29C040 flash4 256B page-0 fault (Phase-74 fix NOT silicon-effective → reopen Phase-74 Wave-2 / CR-01); AM27C020 0x08 write 0-bits-programmed (→ FUT-06); 2516 0x0B read instability (3 distinct SHAs persisting after the VPP-skip fix → FUT-03, GRAD-03 deferred best-effort per D-22). **FIX-01 closed-by-disposition (D-43):** in-posture fixes SHIPPED (firmware VPP-skip on CMD_READ/CMD_BLANK_CHECK clearing the 18.8V boot-refusal + host SRAM/FRAM blank-check short-circuit killing the 0xA4 MSG_ERR_EMPTY_INPUT + FM1608 SRAM→FRAM relabel) with deeper write-path defects RCA'd + named-tracked. Milestone audit `gaps_found` is stale (predates Phase 84 execution); both flagged gaps (GRAD-03, FIX-01) closed-by-disposition + operator-accepted. 3/4 phases Nyquist-compliant; Phase 84 SECURED (threats_open:0). One firmware delta (VPP-skip); otherwise host-side. Meta tagged `v1.15`, gsd planning merged to `beta`; lockstep beta cut + gitlink bump operator-gated. See `.planning/MILESTONES.md` §v1.15; ROADMAP archived at `.planning/milestones/v1.15-ROADMAP.md`; requirements at `.planning/milestones/v1.15-REQUIREMENTS.md`; audit at `.planning/milestones/v1.15-MILESTONE-AUDIT.md`.

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

**Delivered (14/14 requirements):** Custom **streaming COBS `0x00` + CRC8-CCITT** framing with automatic resync on **both** the data-block path (Phase 50) and the host→fw JSON command channel (Phase 51, breaking lockstep wire change — CRC8 verified before the JSON parser sees a byte). COBS `0x00` was chosen over SLIP `0xC0` via a conclusive SAFE-01 static proof (Phase 49). The 2 s timeout cascade is gone (recovery now ~1 ms for corrupt frames, a single bounded ~1 s inter-byte deadline for truncated frames). Decode-in-place fits the Uno ~545 B free-RAM ceiling — no second buffer (D-04); CRC8-CCITT poly 0x07 retained unchanged (D-05). Host-encode↔fw-decode byte-compatibility is pinned by a shared golden-vector catalog with round-trip suites + codegen drift gates in both repos (Phase 52). Even-block full-buffer transfers (Phase 54) + buffer-size advertisement relocated to the `MSG_OK_READY` u16 ack with a safe-512 default (Phase 55, reverses Phase 54 D-05). **Phase 53 bench (operator-witnessed):** N=5 read + write read-back byte-identical on clean Uno + Leonardo (Rev 2.0); resync proven on real hardware both directions/both fault forms; uno328pb read instability **persists** on the hardened transport → structured transport-**exoneration** verdict (NOT a per-shield fix). Bench evidence at `.planning/milestones/v1.10-artifacts/bench-verification/SUMMARY.md`. Branch `v1.10-serial-transport-hardening` was stacked off the `v1.9-read-bug-rca` tip in all 3 repos (NOT off main/beta — stale at v1.8 close); merging v1.10 first also carries v1.9's unmerged commits forward.

See `.planning/MILESTONES.md` §v1.10 for the full delivery summary; ROADMAP archived at `.planning/milestones/v1.10-ROADMAP.md`; requirements at `.planning/milestones/v1.10-REQUIREMENTS.md`.

## Paused Milestone: v1.9 — Read-Bug RCA + Fix (DEFERRED again 2026-06-08)

**Status:** ⏸ DEFERRED by operator 2026-06-08 ("skip that bug for now") — v1.10 shipped and was merged to beta locally; v1.9 is intentionally NOT resumed. No active milestone. When picked back up it resumes at Phase 45.
<!-- prior status line retained below for the resume trail -->
**Resume note:** Resumes at Phase 45 (Bug B RCA — Rev 2.0). PAUSED 2026-06-01 at Phase 44 to insert v1.10 (above); STARTED 2026-05-29 (scope locked via `/gsd-new-milestone`); proposed 2026-05-26 at v1.6 close; renumbered v1.8 → **v1.9** on 2026-05-27 when the host-CLI cleanup took the v1.8 slot. **Progress at pause:** Phase 44 (Bug A RCA — Modified Rev 0) complete; Phase 48 plan 48-01 (COBS-01 evaluation) complete and the verdict flipped DEFER→ADOPT (this is what triggered v1.10). **Remaining:** Phases 45 (Bug B RCA), 46 (Fix Design & A/B), 47 (Acceptance Gate + backlog closures), plus Phase 48 plans 48-02 (TYPE-01) and 48-03 (milestone close). Phase dirs `44-*` and `48-*` preserved in `.planning/phases/`. **Resume:** `/gsd-plan-phase 45` once the hardened transport is merged. Hardware-gated; firmware sub-repo work expected from Phase 46 onward. The transport is now a settled, byte-exact variable — the methodological prerequisite v1.10 was inserted to establish.

**Why:** v1.6 closed with the original read-bug intentionally deferred per D-17v2 re-scope. Phase 29 v2 characterized the bug as two independent failure modes — Bug A (Modified Rev 0 upper-address jitter, A15=1 → 1.86× skew, 63% BIT-RAISE) and Bug B (Rev 2.0 /CE-or-/OE timing + voltage-divider mismatch + VPP=13.1V). v1.9 inherits the diagnostic (`firestarter dev consistency-check`), the 15-binary N=5 bench substrate at `.planning/milestones/v1.6-artifacts/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/`, the Phase 29 v2 H3 block in `.planning/milestones/v1.6-EVIDENCE.md`, the v1.7 labeled-schematic + per-rev capability table + shield-version-detect firmware plumbing, AND the v1.8 cleaned-up host read path (GATE-1.8d ring-fence intact — baseline binaries still valid) as the foundation for designing instrumented A/B fix candidates knowing exactly which silkscreen rev sits on the bench at each step.

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

See `.planning/MILESTONES.md` §v1.8 for the full delivery summary. Per-phase artifacts archived under `.planning/milestones/v1.8-phases/` (via `.planning/milestones/v1.8-archive.sh` in Plan 43-02). Coverage table archived at `.planning/milestones/v1.8-REQUIREMENTS.md` (30 rows with per-requirement disposition column). v1.9 hand-off: read-bug (Bug A + Bug B) carries forward with GATE-1.8d ring-fence intact; 15 N=5 W27C512 baseline binaries at `.planning/milestones/v1.6-artifacts/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/` remain valid because `_read_and_parse_lines` body is byte-identical pre/post v1.8.

## v1.6 — Fix the Read Bug — ✓ Shipped 2026-05-26 (diagnostic + revert per D-17v2)

v1.6 ships as a course-correction milestone. Phase 29 v1 Wave B FAIL revealed that Phase 28 v1's `437339b6` PORTx-clear introduced a Leonardo + uno328pb read-path regression (83.8% zero-bytes); Plan 27-05 RCA re-open confirmed dual-cause disposition (Outcome A Leonardo firmware-induced + Outcome B-independent uno328pb hardware). The course-correction landed: `437339b6` reverted via `ea25174` (clean removal of the regression); `4f205e58` `_NOP()` settling preserved (Plan 28-04 parks); Phase 29 v2 PASS_PARKED gate emission (Leonardo Modified Rev 0 returns to Phase 26 baseline shape — WORST=0.047% zeros across N=10). The original 64KB streaming-read byte-jitter bug is NOT fixed — characterized as Bug A (Modified Rev 0 upper-address jitter, A15=1 → 1.86× skew) + Bug B (Rev 2.0 /CE-or-/OE timing + voltage-divider mismatch + VPP=13.1V) and carried to v1.8 as the RCA starting hypothesis substrate.

See `.planning/MILESTONES.md` §v1.6 for the full delivery summary. Per-phase artifacts archived under `.planning/milestones/v1.6-phases/` (via `.planning/milestones/v1.6-archive.sh` in Plan 30-02). v1.8 RCA substrate ready: 15 N=5 W27C512 binaries at `.planning/milestones/v1.6-artifacts/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/`; pattern findings in `.planning/milestones/v1.6-EVIDENCE.md` Phase 29 v2 H3 block; canonical close narrative in `.planning/phases/29-multi-board-bench-verification/29-04-SUMMARY.md` (or post-archive `.planning/milestones/v1.6-phases/29-multi-board-bench-verification/29-04-SUMMARY.md`); v1.8-deferred bug todo at `.planning/todos/pending/v1.8-seed/large-read-data-jitter-uno328pb.md`. v1.7 substrate (`.planning/milestones/v1.7-SHIELD-REVS.md` per-rev capability table + labeled schematics + shield-version-detect firmware plumbing) provides v1.8 the foundation for designing instrumented A/B fix candidates knowing exactly which silkscreen rev sits on the bench at each step.

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
`.planning/milestones/v1.4-RELEASE-PROCEDURES.md` and proven via `.planning/phases/15-*/lockstep-dryrun-fixture.sh`.

See `.planning/MILESTONES.md` for the full delivery summary.
Per-phase artifacts archived under `.planning/milestones/v1.4-phases/` (via `.planning/milestones/v1.4-archive.sh`).

## v1.3 — CMOS EPROM Family Hardware Validation — ⏸ Paused 2026-05-20 (hardware-gated)

**Status:** Paused at the autonomous/hardware boundary. Phase 11 (Coverage Matrix & DB Inconsistency Audit) shipped clean 2026-05-19 — `.planning/milestones/v1.3-COVERAGE-MATRIX.md` + 78-entry defect ledger + all-algorithms wide-scan extension (`.planning/milestones/v1.3-COVERAGE-MATRIX-ALL.md` with 137 findings across all 11 DB algorithms) delivered. Phase 12 Wave 0 (desk-side scaffold) committed 2026-05-20.

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
| 2026-05-08 | Wire protocol = new explicit `algorithm` integer; `type` retained as legacy fallback                                                                                                                                                       | ✓ Resolved (legacy `type` fallback removed in v1.20 — wire carries only `algorithm`) |
| 2026-05-08 | Firmware dispatch = protocol-prefix `if-return` block per KNOWN_PROTOCOLS, mem_type chain only for legacy entries                                                                                                                          | ✓ Resolved (`mem_type` fallback chain deleted in v1.20; `protocol == 0` fail-closes) |
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
| 2026-07-02 | v1.20 **protocol-only dispatch**: deleted the `mem_type`/`type` backward-compat fallback axis end to end (firmware `memory.cpp` chain, `handle->mem_type`, `json_parser.c` `type` parse, `0xAE` + `TYPE_*`; host `_ALGO_MEM_TYPE` + "Generic Flash (legacy fallback only)" default + `mem_type` label fallbacks) so `protocol == 0` fail-closes to `0xBB`. The fallback was already dead code for every DB chip (all carry `algorithm`) — a legibility/safety cleanup, not a behavior change for real chips. | ✓ Good (all GATE-01/02/SAFE-01 gates green; dead code proven for all 746 chips; 12/12 reqs) |
| 2026-07-02 | v1.20 **FW-first wire-contract sequencing** (D-01): firmware stops parsing `type` (Phase 105) *before* the host stops emitting it (Phase 106) — safe because `json_parser.c` silently skips unknown fields, so a host briefly still emitting `type` is unaffected; the wire contract is never left half-broken. Breaking change vs pre-v1.20 hosts / hand-crafted JSON, documented in both sub-repo READMEs. | ✓ Good (WIRE-01 removed in lockstep across both phases; unknown-field-skip keeps the gap safe) |
| 2026-07-02 | v1.20 **HOST-04 fail-closed algorithm-presence guard**: a chip entry (built-in or user-override) lacking a usable `algorithm` is rejected in `chip_resolver.resolve_chip` (mirroring firmware `protocol == 0 → 0xBB`) before any serial byte — replacing the removed silent fallback. Accepted consequence: user-override entries lacking `algorithm` no longer work (must specify a protocol). | ✓ Good (D-06 regression test; no silent fallback dispatch survives) |
| 2026-07-02 | v1.20 close `override_closeout`: 14 pre-existing cross-milestone open artifact items (2 debug, 2 UAT, 5 verification, 5 todos) acknowledged-and-deferred (none originate in v1.20). LEGACY-01 (`FLAG_VPE_AS_VPP`) + LEGACY-02 (`EPROM_LEGACY` naming) deferred to v2. | ✓ Good (same disposition as v1.18/v1.19; no v1.20-origin debt) |
| 2026-07-27 | v1.22 opens with a **FIX, not a feature** — kickoff research falsified the promoting note's premise twice; the shipped `0x0D` SDP-disable sequence bypasses `mem_util_remap_address_bus`, so ≥1 command write is emitted with `/WE` HIGH on all 84 `0x0D` chips, and its `(0x5555, 0x20)` success check is *inverted* (the datasheets say the command data "is not written") | ✓ Good — reframing was load-bearing; a feature-first milestone would have advertised success for a sequence that never reached silicon |
| 2026-07-27 | v1.22 **harness before any firmware behaviour change** (116 → 117): build the ordered strobe/data recorder and prove the SDP trace suite RED before touching production code — abandoned commit `0052c42` swapped the SDP tables and still reported "22 tests PASS (zero-diff)" | ✓ Good — the elision-faithful recorder is what makes every later byte-exact claim non-hollow |
| 2026-07-27 | v1.22 **firmware before host, unambiguously** (118/119 → 120): new firmware understanding `cmd 9/10` + `flags 0x100/0x200` is backward-compatible with an old host that emits neither, but a *new host* setting `0x100` against `3.0.0b11` firmware is silently ignored — the user asks to skip the unlock and it runs anyway | ✓ Good — HOST-06 then hardened the residual case by *requiring* firmware's `0x86` ack, so an unheard opt-out fails loudly instead of silently |
| 2026-07-27 | v1.22 auto-unlock policy **(d)**: default-on, **reported**, with a `--skip-sdp-unlock` opt-out; `--sdp-relock` deferred to Backlog 999.28; "leave the chip as you found it" rejected as **physically unimplementable** (SDP state is unreadable, so restoring it is a guess wearing a promise) | ✓ Good — answers gh#12's own 2024 design question without manufacturing the gh#12 bug for the next user |
| 2026-07-29 | v1.22 **the SDP allow-set is DERIVED, not curated** (operator directive: "there shall be no guessing, the ground truth is the infoic.xml") — supersedes D-01/D-02's hand-curated 37/47 and the interim 74/10; partition read from minipro `infoic.xml` `flags` **bit 15** (`0x8000` `MP_PROTECT_AFTER`), the section `build_db.py` already treats as authoritative → **ALLOW 43 / REFUSE 41 = 84**, all matched, zero unmatched, zero MIXED | ✓ Good — replaced a judgement call with a reproducible read of the same source the DB is built from |
| 2026-07-28 | v1.22 **LOCK-04 shipped mechanism-corrected**: a generic op-layer NULL-`main` refusal in `operation_utils.cpp` instead of the roadmap's prescribed `0x0D`-local `default:` → `MSG_ERR_NOT_SUPPORTED` arm — `configure_memory` pre-sets the generic mains before the handler runs, so that arm would have refused `read`/`verify` on **all 84** `0x0D` chips | ✓ Good — intent satisfied, prescribed mechanism correctly overruled; recorded as mechanism-corrected in REQUIREMENTS.md rather than silently reinterpreted |
| 2026-07-30 | v1.22 **anti-hollow gates are the default, not an extra**: every new CI checker ships paired with a pytest proving it *fails* on committed planted-violation fixtures — `check_sdp_capability_invariants.py` (9 legs, the repo's first `.py` fixtures), `check_permitted_claims.py` (7 legs), SAFE-03's scan extended to `submit.py` | ✓ Good — this is the discipline that closed v1.12's hollow-GATE-03 debt, now applied by default |
| 2026-07-30 | v1.22 **a locked decision was caught overclaiming and surfaced, not posted**: D-14 prescribed telling `No-Hazmats` their "AT28C parts should now work", but measurement showed every 2K×8 `0x0D` part sits on pinout `DIP24_2816` and **all 19 of 19 are REFUSED** by the derived allow-set (7 `pre-SDP generation`, 12 `unrecognised`), with `AT28C16` also `adapter-required` | ✓ Good — routed to the operator as an explicit accept-or-overturn at the D-16 wording review; an overclaim inside the one phase whose job is not overclaiming would have reached a stranger |
| 2026-07-30 | v1.22 **the validation ceiling is mechanically enforced, not merely stated**: permitted claim = "sequences emitted exactly as specified, verified byte-exact by golden register trace, with a documented and measured host-side timing assumption"; forbidden claim = "SDP works on real AT28C silicon". `check_permitted_claims.py` scans all five closing artifacts; `122-LEDGER.md` pairs each of nine claim classes with an **explicit non-claim** | ✓ Good — the milestone's most reusable artifact; a green scan is also stated twice as *not sufficient on its own* for ROADMAP criterion 4 |
| 2026-07-30 | v1.22 **`dev test`'s erase fabrication had to be fixed before the closeout comments** (121 → 122): `FLAG_CAN_ERASE` cleared for `0x0D` at `database.py`'s source, so the sweep stops fabricating an erase against the 28C family and stops auto-tagging a *passing* chip `community-fail` | ✓ Good — without it every community re-test report would have poisoned this milestone's own evidence |
| 2026-07-30 | v1.22 `beta`-push decision made and **committed before any push** (CLOSE-03, `122-DECISION.md`): ACCEPT the CI auto-fire, CLEANUP of the stray `3.0.0b12` declined; and the cut tag is **derived from `gh release list`, never hardcoded** (RESEARCH A3) — observed `3.0.0b14` | ✓ Good — v1.21's close auto-cut a stray `3.0.0b12` precisely by skipping this step; every downstream artifact read the observed tag |
| 2026-07-30 | v1.22 close `override_closeout`: the same 14 pre-existing cross-milestone open artifact items (2 debug, 2 UAT, 5 verification, 5+ todos) acknowledged-and-deferred — **none originate in v1.22** (116–122). Identical set re-confirmed at the v1.18/v1.19/v1.20/v1.21 closes | — Pending — the recurring 14 are becoming a standing carry-forward; worth one deliberate resolution pass rather than a fifth acknowledgement |
| 2026-07-30 | v1.22 `check_ledger.py`'s 2 pre-existing `LEDGER-01` REDs (from v1.19 Phase 104's `flash_type_3/4` rename) deliberately **not fixed** here — fixing them would edit a closed milestone's artifact; CLOSE-01 never gated on it | — Pending — correct call for this phase, but the RED is still RED; recommended as a backlog seed |
| 2026-07-30 | v1.23 **scope = port stack + host DFU + release-asset fold + VPP *seam only***; the DAC closed loop and the calibration model are out, because `rurp_set_vpp_target_mv()` closes its loop on the *calibrated* read and three of PR #45's ten commits reach into files the White-Box Calibration milestone owns — so "DAC in, calibration out" has no clean split | ✓ Good — and a second, independent reason held: with no PCB a closed loop cannot be validated at all, and a loop that cannot be validated must not be claimed to work |
| 2026-07-30 | v1.23 **cherry-pick nothing from PR #45; hand-author the seam.** Confirmed necessary, not merely preferred: `05f4a77` smuggles a `CONFIG_VERSION "VER06"→"VER07"` bump and `9134f2a` reroutes AVR voltage measurement | ✓ Good — proven not-ancestor of `HEAD` for all ten commits by a `merge-base --is-ancestor` classification, after the ROADMAP's own prescribed `git log --all --grep` mechanism was measured wrong two independent ways |
| 2026-07-31 | v1.23 **land `agent/portability-macros` + `agent/py32f071-toolchain` atomically**, overturning the gh#16-inherited "HAL prep leads" sequencing | ✓ Good — measurement, not preference: the portability half alone takes `pio test -e native` from 141 cases / 17 suites passing to **0 passing / 17 ERRORED**; the repair commit lives on the stacked branch |
| 2026-07-31 | v1.23 **"the merge had no conflicts" is never a quality statement.** Both repos merged with zero textual conflicts and disjoint changed-file sets, yet the ARM target failed at CMake *configure* time on a v1.19 rename git could not see — and `py32f071.yml` had no `push` trigger, so nothing on `beta` would have reported it | ✓ Good — the milestone's highest-confidence finding, triple-corroborated; fixed plus `push: branches: [beta]` added |
| 2026-07-31 | v1.23 **AVR-class manual VPP control is permanent, not provisional** (operator) — no Arduino-class board will ever carry the DAC, so `__AVR__` resolves the capability macro and every non-AVR board must declare it explicitly. Also: the `#include "rurp_vpp.h"` line that every planning document called *the phase's header change* was omitted entirely, `rurp_shield.h` left untouched | ✓ Good — the include collapsed native from 141/141 to 0; research killed the one change the planning record named as the phase's substance |
| 2026-08-01 | v1.23 **flash-persistent config authored in-milestone rather than integrated** — its cited `PORTING.md` specification exists only on two closed PRs and does not match what PR #48 built, so the in-scope subset was vendored instead of citing a stranded document | ✓ Good — dual-slot CRC32 with a `magic` → bounds-checked `length` → `crc32` validation *ordering*; AVR EEPROM backend proven a pure move at 0 B / 0 B under two comparators | <!-- recordscan:allow porting-md-dual-slot: this row's whole point is that `PORTING.md`'s stranded dual-slot design was NOT integrated — the design was authored in-milestone instead (R-8/A-6). The line states the corrected fact and does not cite PORTING.md as the shipped specification. -->
| 2026-08-01 | v1.23 **69 mypy errors and the fail-open `check_mypy_watermark.py` left deliberately OPEN** for a dedicated gate-hardening phase; the app's primary `ci` job is RED until then. The tool shelled to a bare `mypy` from `PATH`, which under py3.12 rejects the configured `python_version = "3.9"` and aborts — reporting green without type-checking anything | ⚠ Revisit — not v1.23's contribution (net measured **zero**: 69 → 72 → 69) and not v1.23's to fix, but a fail-open gate that hid 69 errors against a watermark of 35 should not stay open long |
| 2026-08-01 | v1.23 **a phase's own validation procedure can be wrong in a way that would produce false evidence.** Phase 128's prescribed way to break run B — renaming a source path in the ARM CMakeLists — trips Phase 123's manifest-drift gate at a step with no `continue-on-error`, so the job would have failed *before* the ARM build and published nothing, demonstrating the exact opposite of REL-03. A compile error in an ARM-only TU was substituted | ✓ Good — caught before dispatch; the substituted break produced the intended evidence and additionally proved `outcome` ≠ `conclusion` for a contained step |
| 2026-08-02 | v1.23 **a gate that has never been *seen to pass* is not yet known to be reachable.** Phase 129's 41-leg cross-repo gate was correctly authored *before* the content it judges and went 31 RED → 0 RED through content written afterwards — but one leg required `MEMORY` and `{` on one source line while the linker script has them on lines 8 and 9, so it could never pass whatever the comment said | ✓ Good — the locator-only fix was authorized conditional on a RED-preserving proof (locator fixed + comment reverted → still fails on missing needles); writing the gate first is necessary but not sufficient |
| 2026-08-02 | v1.23 **fact-versus-mechanism boundary written into `REQUIREMENTS.md` itself.** Mechanism corrections stay in the phase artifact (the LOCK-04/LOCK-06/HOST-04/121 D-06/D-17 precedent); but PCB-03 and FUT-N04 asserted a *false fact* — that the part lacks a vector table offset register — and were amended **in place**, because a false fact does not survive being merely footnoted elsewhere | ✓ Good — the part does have `__VTOR_PRESENT 1` and the firmware already writes `SCB->VTOR` unconditionally; the surviving deferral reasons were kept, the false one retired |
| 2026-08-02 | v1.23 **the ARM claim ceiling narrowed rather than widened when a premise turned out false.** The "ARM toolchain is absent from this devcontainer" premise is itself false — it installs and works — but the conclusion survives for a better reason: a local build's compiler differs from CI's and yields a different absolute size for the same source (measured `text=27260` local vs `text=27344` CI) | ✓ Good — every **absolute** ARM size claim still cites a CI run URL + commit SHA; the toolchain's presence newly permits exactly two narrower local classes (delta, byte-identity) and nothing wider, and byte-identity never implies the image runs |
| 2026-08-02 | v1.23 `beta`-push decision made and **committed before any push** (`130-DECISION.md`), as at v1.22: ACCEPT the CI auto-fire; the cut tag read verbatim from `gh release list`, never predicted — observed `3.0.0b15`. D-11 reversed Phase 129's decline and swapped the USB descriptor to pid.codes `1209:0001` before publishing an image | ✓ Good — the first-ever `firestarter_py32f071.hex` release asset is what makes the 21 already-landed host DFU capabilities reachable at all; D-17's identity ship-gate is carried as an owned **tension**, not a resolution |
| 2026-08-03 | v1.23 close `override_closeout`: Phase 126 `passed-with-findings` (informational — Criterion 3's literal "empty `git diff`" wording unmet, no assertion changed) **plus** the same 14 pre-existing cross-milestone `audit-open` items acknowledged-and-deferred for the **sixth** consecutive close; none originate in v1.23 | ⚠ Revisit — five closes ago this was flagged as worth one deliberate resolution pass; it is now six. The recurring 14 should be scheduled, not acknowledged again |
| 2026-08-08 | v1.31 **gh#15 implemented as corrected, and the corrections published before any code landed.** Pulse width is a **database datum**, not a per-protocol constant; `0x0B`'s pulse is 500 µs, not `50000 us`; the 32-bit delay helper is for the overprogram pulse only | ✓ Good — re-derived live from `chip_database.json` through the production parser (170/127/32 chips) and corroborated by the Am27C020 datasheet's own "Flashrite … 100 µs pulses"; posted as comment `#5233463320` on operator approval |
| 2026-08-08 | v1.31 **one shared per-byte loop plus a `const` parameter table, not gh#15's three state machines** (D-01). Protocol owns *shape* (`max_pulses`, `overprogram_factor`, `overprogram_cap_us`, `verify_mode`, `vpp_path`); the database owns the *pulse* | ✓ Good — three handlers would have duplicated most of their own bodies against a hard AVR flash budget; `protocol_id` stays the sole dispatch key, enforced by TABLE-05, and no DB field was added |
| 2026-08-09 | v1.31 **the ~6.25 V program-VCC evidence ceiling fixed *before* any code moved** — unreachable on every shield revision this project owns, so the milestone buys timing/pulse-count/verify fidelity and **not** silicon-margin fidelity | ✓ Good — it bounded every claim the milestone was allowed to make, gh#15's acceptance criteria were amended rather than quietly failed, and a fail-provable claim gate forbids the unqualified "datasheet-conformant" overclaim |
| 2026-08-12 | v1.31 **D-02's 50 ms `0x0B` cap is datasheet-correct but the recorded *reason* was wrong** — the TMS2516 datasheet's 50 ms is the **per-location single pulse width**; the *total* is 100 seconds (≈2048 × 50 ms), not `100 × 500 µs` | ✓ Good — caught by the pre-close carry-over sweep reading the actual title page, and corrected in the decision record *before* Phase 141 cited it; the cap **value** never changed |
| 2026-08-16 | v1.31 **a defect this milestone itself introduced was found by its own bench gate, not by a user** — Phase 141 deleted the only `CTRL_VPE_ENABLE` assert, and the first bench cycle failed on byte 0 within 25 pulses | ✓ Good — root-caused by a debug session to a firmware cause (not a bench fault), fixed, then 3/3 byte-exact; the failure **stays in the record with its cause** and is not one of the three counted cycles. This is the argument for spending a bench gate on a milestone that "only" changes timing |
| 2026-08-17 | v1.31 **`0x08`/`0x0B` recorded `skipped-with-reason` with the missing parts named, never inferred from the `0x07` result** (D-08 — bench coverage asymmetric by operator inventory) | ✓ Good — the two protocols share a firmware write path but not a part, a VPP path or a bench result; the record makes no transfer between them, and D-14's fail/pass taxonomy was fixed *before* any run so a 60/64-then-0/64 shape could not be argued into the friendlier bucket afterwards |
| 2026-08-17 | v1.31 **MERGE-05 reads green because its anchor MOVED, not because growth stayed inside the band** — F-141-01's overrun was never remediated, and `ebe9cb3` is **+96 B** against a 0 B leonardo must-not-grow band | ⚠ Revisit — carried **open and un-adjudicated** with the operator as its named owner; BASE-01 was not re-anchored a second time to make it green, and Phase 145's Gate 2 and Gate 3 both ran on a build carrying the breach. 144 H7 was answered green at 26906 B and then went red underneath the answer |
| 2026-08-18 | v1.31 close `override_closeout`: **9** carry-forward `audit-open` items acknowledged-and-deferred for the **eighth** consecutive close — down from 14 because the 2026-08-09 sweep closed Phases 71 and 85 on evidence and retired two debug sessions into precise trackers. None originate in v1.31, and all nine phases are verified | ⚠ Revisit — the residue is now genuinely hardware-gated (the Uno-class legs of Phases 08/09, Phase 84's operator sign-off) rather than merely unswept. Two closes ago this was flagged as needing one deliberate resolution pass; the sweep was that pass, and what survives it needs bench time, not another acknowledgement |
| 2026-08-18 | v1.31 close **found and worked around a GSD tooling defect rather than accepting its output**: `plan-scan.cjs`'s loose `/PLAN/i` fallback counted `146-REPLAN-BRIEF.md` as a phantom 14th plan in a 13-plan phase, driving `phase_complete: false` for a closed phase | ✓ Good — the brief was renamed (`146-RESCOPE-BRIEF.md`, provenance note in-file, no citation referenced it) and the scanner behaviour filed, not fixed. The v1.30 close shows the same signature (`current_phase: 30`, 7/8, 88%), so this had been mis-reporting silently for at least two milestones |
| 2026-08-18 | v1.32 **report provenance is the dependency spine, not a feature** (D-01) — F-01 (`cli_handlers.py` hardcoding `fw_board_identity=None`) is fixed *first*, because until a `dev test` report names its firmware no `0x0D` write-path claim can be attributed to any code at all | ✓ Good — the fix landed in Phase 147 and every later phase's outward claim rests on it. Stated with it rather than hidden: **every report filed before the fix stays permanently unattributable**, gh#21's and gh#32's included |
| 2026-08-19 | v1.32 **the AT28C256 VCC correction is a value-keyed post-construction substitution, never an edit to the decoded table** — `build_db.py` substitutes 4000→5000 mV by *value*, leaving the faithfully-decoded `VCC_VOLTAGES` table untouched | ✓ Good — blast radius measured at exactly **56 chips, zero decreases** in a dedicated `diff_db.py` bucket, and it keeps the generator honest to `infoic.xml` rather than hand-patching a generated artifact |
| 2026-08-19 | v1.32 **page size is emitted by provenance, for exactly the 18 upstream-native `0x0D` rows** (15@128 B, 3@64 B) — no per-chip guess table, no extension of `_PAGE_SIZE_BY_PART` (DATA-04; three such tables were deliberately deleted in Phase 70 and the pattern is not reintroduced under a new name) | ✓ Good — proved exhaustively by an 11-leg host invariant, and the seam ships with its own load-bearing non-claim: **for the AT28C256 named in the community threads it changes nothing observable**, since 64 B is exactly the pre-existing floor |
| 2026-08-20 | v1.32 **Phase 150 (`write --sdp-relock`) deferred for the second time** — operator decision at the discuss step, before any research or plan existed; RELOCK-01…06 + 08 leave v1 scope, **DATA-06 is retained and re-homed to Phase 151** on its documented-advisory branch, which the deferral makes the only reachable one | — Pending: the consequence is recorded, not argued away. **For a second release running there is no supported way to deliberately protect an SDP part**, and on `0x0D` the bit cannot be read back either. ⚠ A future promotion **must reverse OUT-05's fifth gate class in the same change that lands the feature** |
| 2026-08-20 | v1.32 **the protection classifier is structurally incapable of guessing** (D-09/D-10) — `protection_gate_for_entry` is a pure `(entry, display_name) → (class_token, reason)` function that **cannot return `protected`/`unprotected`**; only the one function permitted to read a device response may | ✓ Good — frozen by an AST invariant gate with committed planted fixtures and walked over all 746 rows. On the 28C/SDP family the honest answer is usually the refusal: **665 of 746 refusal, 81 `read_permitted`** |
| 2026-08-21 | v1.32 **Phase 153 added mid-milestone and sequenced to run BEFORE Phase 152** (D-07/D-08) — the outward-facing close cannot describe an erase policy that has not shipped yet, so the write-path phase runs out of number order by design | ✓ Good — 152's precondition was discharged before it started, and both `phase.complete`'s auto-advance to the already-closed 153 and its clobber of an unrelated phase's plan count were caught and hand-repaired rather than accepted |
| 2026-08-21 | v1.32 **an earlier phase's own criterion was corrected, not satisfied**: `check_dispatch.py` (GATE-03) is DB-and-dispatch-table scoped and **cannot** see a handler-body control-register write, so it is not this milestone's erase hazard control (D-153-03) | ✓ Good — the real control is a new brace-matched negative source scan, `check_erase_no_vpp.py`, proved both *reachable* (fails on a planted control-register write) and *discriminating* (flags a real adjacent function's legitimate A9-12V writes). `check_dispatch.py` stays byte-unchanged and is never cited as the proof it structurally cannot be |
| 2026-08-21 | v1.32 **publishing moved INSIDE the phase** — Phase 137 and Phase 146 each authored release-note sets that were never posted, so Phase 152's boundary put the five public artifacts inside its own scope rather than deferring them | ✓ Good — all five posted (gh#12/#21/#11 comments, both release bodies) behind a fail-provable claim gate seen RED on planted violations first. ⚠ Recorded against it: **a green gate run is not a wording review**, and the ledger states how far short of D-03's blocking operator review the checkpoints fell |
| 2026-08-21 | v1.32 close `override_closeout`: the **9** carry-forward `audit-open` items acknowledged for the **ninth** consecutive close, plus Phase 150's deferral making `ALL_PHASES_VERIFIED` structurally false | ✓ Good — the set is unchanged from v1.31 in both count and membership, none of the 4 UAT/verification entries originate in v1.32, and all six executed phases are `passed`. The two reasons are recorded separately rather than blended into one number |
| 2026-08-22 | v1.33 **D-01: split the sweep from the remap** — Phase 154 sweeps source and builds the tool; Phase 159 applies it **once** at the end, over the composite pre-154 → post-158 diff. Measured, not guessed: 723 citations would otherwise have been remapped twice, 41 % of them caused by four added `#include` lines. The cost is a knowingly-stale citation window between 154 and 159, bounded by a close-blocking marker (`CITATIONS-STALE.md`) rather than by discipline. ✓ Good — the marker held and was removed as Phase 159's final mutation |
| 2026-08-22 | v1.33 **the binary command protocol is OUT of scope** (operator) — measured at −3728 B flash / −512 B RAM on `leonardo`, which would have dwarfed everything this milestone did, and filed as Backlog **999.35** carrying that measurement rather than absorbed. It also **corrects v1.28's own flash estimate from ~1–1.5 KB to −3.7 KB**. ✓ Good — kept a size milestone from becoming a protocol rewrite |
| 2026-08-24 | v1.33 **measurement supersedes scoping prose, publicly and by appended clause** — Phases 155–158 corrected 5 + 10 + 22 + 13 stale figures respectively, each as an appended correction rather than a silent replacement, including three of the ROADMAP's own predictions (Phase 158's `jsmntok_t` **−138/−138/−136 B where +30 B was predicted**; LAND-06 DECLINED *with* its +22/+24/+22 B measurement; LAND-07's 57/7 refuted by three re-derived bounds). ✓ Good — the pattern this project should keep |
| 2026-08-24 | v1.33 **269 remap records rest on diff provenance, not verbatim equality** — Phase 154 deliberately reworded the cited comments, so `diff_provenance_reworded` is the honest oracle for those records and each carries `verbatim_oracle_applied: false`. **ROADMAP criterion 2 is therefore NOT universally satisfied, and no closure text claims it is.** — Pending: a future sweep that does not reword would let the verbatim oracle close |
| 2026-08-24 | v1.33 close `override_closeout`: **10** carry-forward `audit-open` items acknowledged for the **tenth** consecutive close (none originating in v1.33), plus **SWEEP-13 deliberately unticked** — 3 of 4 clauses proven, the one-meta-commit clause measurably not met at 9, and rewriting meta history to manufacture it dispositioned accept/declined (T-154-53). ⚠ Revisit — the carry-forward set has now been re-acknowledged ten closes running without shrinking |

**⚠ CORRECTION (Phase 152 / 152-CONTEXT.md D-06 + D-15 — 2026-08-21) — the 2026-07-30 v1.22 row above ("`dev test`'s erase fabrication had to be fixed before the closeout comments") rests on a premise this phase found disproven.** That row records Phase 121 D-12 clearing `FLAG_CAN_ERASE` for the `0x0D` family; `database.py:591`'s own comment (as it read before Phase 153) gave the reason as: advertising the erase capability for these chips is a **false capability statement**. That premise is **disproven**. The capability is real in the silicon — Microchip **DS20006386B**, Table 6-1 Operating Modes (p11), lists Hardware Chip Erase as a first-class operating mode, with the **Optional Chip Erase Mode** paragraph on the same page and the erase waveforms in §6.10 (p15) — and real in `infoic.xml`: the AT28C256 record carries `flags = 0x0000C010`, so the erasable bit `0x10` is **SET**. What was false was only that *firestarter* could perform it, not that the chip could. Phase 153 closed that gap using the **software** AN-0544B six-byte erase path, not the datasheet's 12 V-on-OE hardware path — the hazard guard for that hardware path is `firestarter_fw/scripts/check_erase_no_vpp.py` — and restored `FLAG_CAN_ERASE` for `algorithm 13` at `database.py:638`. The **code comment** half of this correction was discharged by Phase 153 (ERASE-07); this block is the `.planning`-side half only. **Verified already landed by this phase, not re-done:** the "three firmware-touching workstreams" count above (`:45-47`), the workstream table's row 7 for Phase 153 (`:90`), and workstream 4's updated description (`:91`) were all confirmed present before this block was written.

## Context

- **Tech stack:** Python 3 CLI host (pip package `firestarter`, JSON-over-serial
  at 250000 baud, COBS+CRC8 framed since v1.10) + Arduino C++ firmware (PlatformIO, AVR targets
  `uno` + `uno328pb` + `leonardo`, RURP shield)
- **Fourth board target since v1.23 — PY32F071 (Cortex-M0+), source-only:** a non-Arduino
  CMake/arm-none-eabi target under `platform/py32f071/` (pinned OpenPuya SDK, CherryUSB CDC at
  48 MHz, SysTick ms + TIM3 µs, 12-bit ADC, contiguous 8-bit GPIO bus), sharing the command
  processor, framing and PROM algorithms with the AVR targets through a fake-Arduino-core
  compatibility layer. **No PY32F071 PCB exists**, nothing has ever run on this silicon, and the
  pin map is an explicit placeholder that describes no board — the firmware refuses every
  PROM-energising command on this target. `DATA_BUFFER_SIZE` is **512** — half Leonardo's — and
  wire-visible via v1.10 CAP-01. Config persists in dual-slot CRC32 flash records (the part has no
  EEPROM); VPP is manual-only, like every AVR board. Built in CI on `beta` and on PRs; its `.hex`
  publishes as a real release asset since `3.0.0b15`. The host can drive a USB-DFU install
  (`firestarter_app/firestarter/py32_dfu.py`, beta-channel-gated), exercised against descriptors and mocks only.
- **Repo structure:** Meta-repo + 2 sub-repos (`firestarter_fw/` firmware,
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
- **27C programming algorithm (since v1.31):** the three UV/EE-EPROM protocols `0x07` / `0x08` / `0x0B`
  program through **one shared per-byte pulse-to-verify loop** in `eprom.cpp`, driven by a `const` PROGMEM
  `eprom_params_t` table keyed on `protocol_id` (`max_pulses`, `overprogram_factor`, `overprogram_cap_us`,
  `verify_mode`, `vpp_path` — deliberately **no** pulse-width column). The pulse width comes from the
  **database** per byte (`handle->pulse_delay`; `pulse_delay == 0` falls back to 1000/100/500 µs for
  `0x07`/`0x08`/`0x0B`), and it **never grows between attempts** — the pre-v1.31 block-level mismatch-mask
  loop with its adaptive `pulse_delay = org + org*retries/20` growth and flat `NUMBER_OF_RETRIES = 20` is
  gone. A byte that exhausts `max_pulses` hard-fails the block via `MSG_ERR_MAX_PULSES` carrying the failing
  **address and pulse count**. `0x0B` carries a 50 ms accumulated-energy cap per byte; `0x07`/`0x08` ship
  `energy_cap_us = 0`, i.e. **UNCAPPED** in firmware — the host's `IntRange(1, 65535)` is the only bound on
  `write --pulse-us N` there (Backlog **999.31**). One shared `eprom_hv_route_mask()` resolves VPP/VPE routing
  from the table for both `eprom_check_vpp()` and the write path; every **error** exit disables every route
  through a single-exit wrapper, while a **successful** block deliberately leaves the route energised so the
  once-per-block VPP settle is not re-paid per byte.
- **Evidence ceiling on all of the above (v1.31, standing):** the **~6.25 V** program-VCC rail that all four
  vendor algorithms (Intel Intelligent, Quick-Pulse, Flashrite, PRESTO) assume is **unreachable on every
  shield revision this project owns** — there is no VCC-raise path. So the algorithm work buys **timing,
  pulse-count and verify fidelity, not silicon-margin fidelity**, and the project makes **no
  datasheet-conformance claim in either direction**. Bench evidence covers exactly **one part, one
  controller, one shield revision**: Winbond W27C512 (`0xda08`) on `leonardo`, shield Rev 2.0. `0x08`
  (AM27C020) and `0x0B` (M2716/M2732) have **never run** on the new loop — both skipped-with-reason for want
  of parts. Program-window VPP/VCC **under load** has never been measured on this project: the held-rail DMM
  proxy is defeated by DTR-reset-on-close (the standing Phase-97 tooling gap), so **every** VPP figure on
  record is an *idle* firmware-ADC sample.
- **Verified families (structural):** UV-EPROM (W27C512), Flash AMD (29F040),
  Flash Intel (28F010 minus VPP-ADC gap), EEPROM (AT28C256 via Phase 13
  override), SRAM (6116-class via safe stub)
- **Known gaps for v1.1:** see `.planning/MILESTONES.md` "Known Gaps" section
  (Intel-flash VPP ADC, retroactive VERIFICATION.md for phases 01-10, WARNING-2
  forward-compat, WARNING-3 wire-key naming, WARNING-4 test-script drift)

## Constraints

- Arduino Uno: 512-byte serial data buffer (affects chunked transfer sizing in `eprom_operations.py`)
- Arduino Leonardo: 1024-byte buffer
- PY32F071: 512-byte buffer (deliberately not raised to 1024 — it is wire-visible via v1.10 CAP-01, so a bump is a behaviour change needing its own justification)
- Hardware calibration (R1/R2, board revision) persisted in EEPROM via `rurp_configuration_t` on AVR; the PY32F071 has **no EEPROM** and persists the same unchanged schema in dual-slot CRC32 flash records behind a per-platform storage seam (`include/rurp_config_storage.h`)
- AVR flash budget (measured at v1.23, `124-NONREGRESSION.md` §F4d): Leonardo 26016/28672, Uno 23954/32256, uno328pb 24004/32384; RAM 2014/2560, 1573/2048, 1579/2048. Leonardo is the binding target — budget new work against the ~2600 B actually measured, never the older pre-Phase-119 headroom figure that milestone's own +392 B was judged against, and **record RAM alongside flash** because a `PROGMEM`→RAM regression is invisible in a flash number
- VPP is **manual-adjustment-only on every board**, permanently for the AVR class — no Arduino-class board will ever carry the DAC (operator, 2026-07-31). `rurp_set_vpp_target_mv()` returns `MANUAL_ADJUSTMENT_REQUIRED` everywhere; the closed loop is deferred (FUT-VPP) and inseparable from the calibration model v1.26 owns
- No bus-trace oracle exists for the ARM target — `HOST_STUBS_RECORD_BUS` runs on `native` only, so the ARM target could diverge from the AVR golden register sequences with nothing able to notice (FUT-ORACLE)
- Constants/flag bits duplicated between `firestarter_app/firestarter/constants.py` and `firestarter_fw/include/firestarter.h` — must change together

## Sub-Repos

- `firestarter_app/` — Python host CLI, database pipeline, serial protocol
- `firestarter_fw/` — Arduino firmware, algorithm implementations

Two extra git **worktrees** sit alongside the tracked gitlinks, added for v1.23's parallel branch work. They are checkouts of the same two repos, never separate repos and never gitlinked, and are gitignored in the meta repo:

- `firestarter_py32_ci/` — `firestarter` @ `feature/py32f071-release-assets` (`ad47c3b`)
- `firestarter_app_py32/` — `firestarter_app` @ `feature/py32f071-fw-install` (`4ee64a1`)

**Both are spent as of the v1.23 close (2026-08-03)** — the content of both source branches is now merged and published (`feature/py32f071-fw-install` landed in Phase 127 as a real merge commit; the release-asset naming work landed in Phase 128). They are safe to remove with `git worktree remove`, but are left in place rather than torn down as a side effect of milestone close.

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

*Last updated: 2026-09-23 — **Phase 206 (`dev test` keeps its fidelity, on one session) CLOSED and verified** (4 plans in 4 sequential waves, verifier 10/10, UAT 10/10, DEVTEST-01…03 and SESS-01…02 Complete). Host-only; no firmware change. A transport-failed cycle-block step now exits 2; `check_eprom_blank`/`verify_eprom` verdict 2 lands as `VERDICT_SKIPPED` + `STATUS_ERROR` instead of a chip verdict. The blank-check step keeps its compare evidence outside `dedup_fingerprint`'s hash, and an empty-default `cmp=host` tag separates host-path reports without moving any of the 19 frozen literals — the 43 measured ALLOW chips restart their promotion ladder. `EpromOperator.lease()` (`3853b55`, default off, one call site) holds one serial link per `dev test` plan; measured on a Leonardo + W27C512, N=3 per arm, it saves 40.709 s (15.1%) against the pre-registered 15.0% bar with zero verdict divergence, so it is KEPT. Code review 0 critical / 2 warning (WR-01, WR-02, advisory, unfixed). `/gsd-secure-phase 206` outstanding.*

*Last updated: 2026-09-21 — **Phase 203 (The write guard moves up a layer) CLOSED and verified** (4 plans in 4 sequential waves, 5/5 success criteria, WRITE-01…WRITE-06 Complete). Host-only; no firmware change. The pre-write blank check now runs on the host, ahead of Phase 205 deleting the firmware's own write-init pre-flight: `write_blank_guard.py` is a pure fail-closed predicate — an absent, `None` or empty wire dict, or an absent `algorithm`, is **guarded, never exempted** — reading only `algorithm` and `flags`, both confirmed present on every `convert_to_programmer` wire dict, so it cannot join the inert-guard failure class that leaves `check_eprom_blank`'s SRAM short-circuit dead in production. `GUARDED_PROTOCOL_IDS` is pinned to exactly `{0x06,0x07,0x08,0x0B,0x10}` by a test proven genuinely RED in **both** directions (removing `0x0B` → 1 failure; adding `0x0D` → 4), which is the only drift detector once 205 lands. **The phase's one-way door was decided by the operator, not inferred**: the 203-03 checkpoint returned `confirm-d13` — `write --verify` opts *that invocation* into 0/1/2 while plain `write` keeps 0/1 unchanged, resolved **by cause, not by phase**, so a transport or hardware failure in *any* leg (guard read, the write itself, or the read-back) exits 2 and a retry-on-1 script never retries onto a chip of unknown state. Code review found **1 Critical, CR-01**: the guard read and the write it gates each opened their own connect with no port pinning, so on a multi-board bench the guard could prove board A blank and the write could land on board B — a hole in the exact property the phase exists to establish, and new with it, since `write` was one atomic connect before. Fixed in `firestarter_app` `0fc6c77` by threading an explicit per-call `preferred_port`/`restrict_to_port=True` from the guard's resolved port through the write **and** `--verify`'s read-back, fail-closed (a pinned port that stops answering raises rather than falling through), with no ambient pin state; the fix's own test was perturbation-verified. Suite **2216 → 2306 passed, 0 failed**, 36/36 snapshots. `203-SESSION-COST.md` records the added wall-clock as a **cited derivation, explicitly not a measurement** — this phase took none — and declines to derive a read-term figure its single-sample source cannot support; Phase 206's SESS-02 reads it as the before-figure. Carried as advisory, not fixed: WR-01, WR-02, IN-01. Filed: one todo for `dev test`/`dev write-cycle`'s still-unpinned verify connects. **Outstanding: `/gsd-secure-phase 203`** — `workflow.security_enforcement` is on and no `203-SECURITY.md` exists. Prior footer retained below.*

*Last updated: 2026-09-20 — v1.41 Verification Moves to the Host ACTIVATED. Phases continue at 202. Blank check and verify leave the firmware in both their forms (standalone commands and in-algorithm pre-flights); the host reads and compares instead, through one implementation reusing `chip_test.py`'s diagnosis primitives. `memory_verify_execute` and every in-algorithm verify stay. Both repos bump to `3.1.0b1`. Dual-repo lockstep, bench-gated; requirements and roadmap hand-authored; `phases.clear` skipped. Prior footer retained below.*

*Last updated: 2026-09-20 — **v1.40 (Program-Parameter Fidelity) CLOSED**, 19/24 requirements, `override_closeout`, tagged `v1.40` — a bare tag that must never become a GitHub Release. 5 phases (197–201), 26 plans, 65 tasks. Three community reports, each carrying the reporter's own datasheet, were each found to be a fleet-scale fault wearing one chip's name — a 100 µs pulse shared by 217 of 297 algorithm 7/8 rows, a 12.0 V VPP shared by 563 of 746, and 30 rows asking 18 V or more on rails nobody had measured. **The deliverable was the mechanism, not any value**: `tools/datasheet_overrides.json` holds only changed fields, each naming its datasheet and the decoded value it replaces, behind a loader that fails closed on an unknown part, an unknown field, or an override gone no-op — and all three of `build_db.py`'s part-specific hardcodes are gone, two of them **deleted as defects rather than migrated as corrections**. Across the milestone the database changed **25 of 746 rows, with 0 `support_status` changes and none added or removed**. The decode itself was wrong, not just its outputs: the `VPP_MV` `0xF0` mask was incomplete so 25 V and 21 V collapsed onto 18 V, `VCC_VOLTAGES` gained nine upstream indices with twelve non-credible rows signed `UNSOURCED` and proved load-bearing by a planted mutation, and `DECODE-NOTES.md` § 9 records the finding underneath it all — the voltage word's two nibbles select a **programmer rail index, not a chip requirement** — which is what finally disposed of the 28-row `vcc_mv == 5500` group unprovable since v1.32 Phase 148. **The rails were measured rather than assumed** (17380 mV drop path, 22140 mV direct VPE at socket pin 1), and the shortfall for ten algorithm `0x07` rows was **removed by routing in firmware** — one comparison in `eprom_hv_route_mask`, decided on path capability and reading no voltage at all, with a 15-case native suite proving it voltage-blind. Backlog **999.44**'s firmware half landed: a `region-end` key carrying an **absolute end address, not a length** (the write-init body is re-entered per 8 KiB chunk, so a length would be wrong on every call but the first) travels host → wire → `mem_util_blank_check_region`, watched RED with its transcript committed, then GREEN, then confirmed on real silicon. **The milestone has NOT shipped** — 170 meta / 37 host / 15 firmware commits ahead of `beta` with **zero** patch-equivalent by `git cherry`, and no version string separates the two states (`3.0.0b33` / `3.0.0b48` read identically on `beta` and at the tip). **Five requirements stay Pending, all by recorded decision.** PULSE-04 / VOLT-04 / RAIL-05 are the three gh#70 / gh#66 / gh#71 answers — written, operator-approved, committed and deliberately unposted, because `git branch -r --contains HEAD` resolves nothing anywhere, so every other route would name a version or a SHA no reader could look up; `197-GH70-ANSWER.md` § "Held-pending deferral" is the single release checklist. RAIL-03 is honestly unmet: `MSG_WARN_VPP_LOW`'s 5 % window is narrower than the measured +7.59 %/+7.95 % ADC-vs-meter discrepancy, so it stays silent for 9 of the 10 rescued rows. OVR-03's citation contract is enforced by the test suite and not by `build_db.py` itself. Filed: five backlog items (999.69–999.73) and three todos, one of them Phase 200's Critical review finding that the phase's own verification asked to be filed and nobody filed. **Not claimed:** no part was programmed at 21 V; the rail figures are one rig and one session; 215 of 297 algorithm 7/8 rows still carry an unproven 100 µs pulse, inventoried rather than fixed. Hand-archived; `milestone.complete` and `audit-open acknowledge` both deliberately not run — **88** open artifacts disclosed in `STATE.md` with **0** suppressed. Full record: [`milestones/v1.40-CLOSE-RECORD.md`](milestones/v1.40-CLOSE-RECORD.md). Prior footer retained below.*

*Last updated: 2026-09-17 — **v1.39 (Protocol 0x05 Write Correctness) CLOSED**, 7/8 requirements, `override_closeout`, tagged `v1.39` — a bare tag that must never become a GitHub Release. 3 phases (194–196), 15 plans, 43 tasks. Both protocol `0x05` defects the operator filed on 2026-09-11 are fixed **by refusing**, not by read-modify-write: `flash_5v_page_page_size()` is deleted and the page size now comes from the database for all **27** parts, and a per-chunk alignment guard refuses an unsafe partial write ahead of the first register write, with a host predicate refusing ahead of the port opening. The fix shape was decided by measurement — a page-staging buffer leaves **142 B** of RAM on `uno` for the entire call stack, and only a host pre-connect refusal can claim the device is unchanged. Both refusals are proved on silicon on a `W29C020`, against a pre-fix build that reproduced both loss directions and printed `successful` over the erased bytes. **The milestone has NOT shipped** — 17 meta / 17 firmware / 1 host commit ahead of `beta`, confirmed by `git cherry`, with `origin/beta` still carrying the deleted derivation, so gh#67 and gh#68 stay live for beta users; the versions published there (firmware `3.0.0b32`, app `3.0.0b47`) were cut by a documentation-only push and carry none of this milestone's code. **PAGE-03 is the whole of the override**: its bench part must be one of the **9** under-sized parts, the ordered `W29C512` has not arrived, and `W29C020` is one of the **18** already-correct ones — recorded as *0 of 9 on hardware, 9 of 9 on the database comparison* in three documents and conflated in none. Accepted debt: a negative start address passes the host guard and the firmware clamps it to 0, a **wrong-destination** defect rather than a page-destruction one, filed not fixed. Phase 196 retired the PyPI per-version download-share instrument, whose question lost its consumer when the slug claim fired ahead of its own trigger. Hand-archived; `milestone.complete` and `audit-open acknowledge` were both deliberately not run — **86** open artifacts disclosed in `STATE.md` with **0** suppressed. Full record: [`milestones/v1.39-CLOSE-RECORD.md`](milestones/v1.39-CLOSE-RECORD.md). Prior footer retained below.*

*Last updated: 2026-09-13 — **v1.38 (Repository Rename) ACTIVATED**, phases continue at **189** (v1.37 ran 182–188; the vacated **150** slot and the v1.24–v1.29 version slots stay unreused). Promotes Backlog **999.9** (gh#2), the highest-blast-radius item in the 2026-07-27 import and a hazard v1.35 explicitly accepted rather than solved. **Renames `firestarter` → `firestarter_fw` and stops there:** claiming `henols/firestarter` for the meta repo is the one destructive act in 999.9 — it is what deletes the firmware repo's redirect — and it is deferred to [`seeds/SEED-claim-firestarter-slug.md`](seeds/SEED-claim-firestarter-slug.md) behind an *adoption* trigger rather than a date. **Scoped from measurement, not estimate** (2026-09-13): the front door has **0 stars / 0 forks / 0 watchers** six weeks after v1.35 made it the documented entry point, while 75 sit on the two components; `pip install firestarter` resolves to **2.0.7**, so `origin/main` — 948 commits behind `beta` — is the branch that reaches users and 999.9's own clean-environment validation would have tested it while only `beta` got fixed; the three hardcoded endpoints are consumed **only** by `firmware.py`, so the blast radius is the `fw` command alone; no workflow in any of the three repos hardcodes a repo slug, making 999.9's "CI/release workflows" clause a no-op; and **672 of the 778** firmware-slug references sit in `.planning/milestones/`, historical-by-intent and deliberately not swept. **Standing rule this milestone establishes:** the meta repo must never publish a GitHub Release — it has 0 today, which is what keeps a post-claim failure a clean 404 instead of `_compare_versions` reading `v1.36` as `1.36` and reporting firmware current forever. Full analysis in [`notes/999.9-repo-rename-impact-analysis.md`](notes/999.9-repo-rename-impact-analysis.md). Prior footer retained below.*

*Last updated: 2026-09-02 — **v1.36 `dev test` Fidelity ACTIVATED**, phases continue at 174. Host-app-only milestone against the `dev test` harness: stop running operations whose result is empty by construction (four measured cases, enforced by a structural test over `derive_plan` output, not a comment), stop failing UV parts for the tool's own whole-device blank check (Backlog 999.44 host half), stop filing a tool or rig fault as a chip verdict, and make the report state what the run already knows (Backlog 999.36's 13 drafted requirements, schema → 1.8) under a `dedup_fingerprint` byte-identity gate. Motivated by three community rebuttals of our own triage on gh#23/#28/#31. **999.44's firmware half — and the product-level `firestarter write -a` refusal it fixes — is knowingly OUT of scope and stays a defect.***

*Previously: 2026-09-02 after the **v1.35** milestone (Documentation Consolidation & Wiki Migration) CLOSED and archived. Shipped 7 phases (167–173), 41 plans, **29/32 v1 requirements**; a documentation and repository-configuration milestone with **no product-code change**. `firestarter_prom` got its first README ever and its wiki became the documentation home — 11 pages live, 12 `doc/` files migrated by copy-then-edit and proven claim-preserving by HONEST-01's token-multiset comparison, **both sub-repo `doc/` directories deleted**, three root-level strays disposed, and the app README cut from 779 lines with its table of contents corrected from advertising three sections that did not exist. Policy is configured rather than merely stated: one tracker, three issue templates live, byte-identical `.github/CONTRIBUTING.md` pointers across all three repos, and `main` behind an `enforcement: active` ruleset everywhere with `current_user_can_bypass: never` — **proven by pushing at it and capturing GitHub's own GH013 refusal**, not by reading configuration back. POLICY-05 was fixed by construction before it could bite: `git.base_branch` repointed to `beta`, which incidentally corrected three fork-point consumers that had been branching every new phase and quick task off the wrong ref. Closeout `override_closeout` for three **record** gaps, not outcome gaps — phases **169**/**170** executed ad hoc with no plans, summaries, phase directory or verifier pass, and phase **172** carrying 9 plans and 26 evidence files but **no `172-VERIFICATION.md`** (its nine ROADMAP checkboxes were flipped at this close, the write `CLOSE-RECORD.md` §1 had assigned and never performed). The three unticked requirements are decisions: **WIKI-03/WIKI-04 withdrawn** when the operator reversed to wiki-only authoring on 2026-08-30, deleting the publish-and-drift-check machinery Phase 167 had just proven; **FRONT-02 declined outright** because it cannot hold alongside FRONT-03. **Two things a later reader should not have to infer.** First, **the guard this milestone built was retired the day it closed** — `wiki-check.yml` and all of `tools/wiki/` deleted 2026-09-02, `MIGRATION-TABLE.md` the only survivor, so HONEST-02 now rests on its stamp half alone and **no automated wiki guard exists**. Second, **the milestone-level non-claim: relocation is not verification** — a document moved intact is not thereby confirmed accurate. Two findings filed at close rather than fixed: **999.49**, the `audit-open acknowledge` writer destroys the artifacts it annotates (it wiped 100 lines of YAML frontmatter from a quick-task summary before the pass was reverted uncommitted, so all 72 open items were disclosed in `STATE.md` by hand instead); and **999.50**, the retirement left two live references to the deleted `tools/wiki/dispatch_mirror.py`, one of which leaves a firmware file declared guarded in `scan_paths.py` and actually unguarded. Prior footer retained below.*

*Last updated: 2026-08-30 — **v1.35 (Documentation Consolidation & Wiki Migration) STARTED.** Phases continue at **167** (v1.34 ran 160–166). A documentation milestone, not a product one: no firmware and no host behaviour changes. `firestarter_prom` — which has **no README at all** today — becomes the project front door, and its wiki becomes the single home for all project documentation. Seven operator decisions taken at activation: all three READMEs become simple get-started pages with **prom as the front door** (accepting a thin PyPI listing, since `firestarter_app/README.md` is the `long_description`); sub-repo READMEs carry **only repo-specific information** and link up; **everything leaves `doc/`** — all 13 files, both directories removed, changing the app sdist for the 3 doc files it currently carries; **relocate and correct only**, so the compatibility matrix, family pages and tutorials carried into 999.12 from the retired 999.14/gh#7 stay deferred; wiki pages are **sourced in `firestarter_prom` and synced**, buying version control, review and a mechanical drift check; **Backlog 999.13 in full**, branch protection included, which forces `/gsd-complete-milestone` off its direct `main` push onto a PR flow or a documented admin bypass; and the two sub-repo wikis are **disabled** — done at activation, `has_wiki=false` on both, verified by API. Starting state measured rather than assumed: app README **779 lines**, fw README 151, 13 `doc/` files ≈ 2724 lines, **no wiki repo initialized anywhere**, Issues already off on both sub-repos (23 open on prom), `firestarter`'s `Protect main` ruleset present but **`enforcement: disabled`** and no ruleset at all on the other two, 6 dead issue links, and an app README TOC advertising three sections (`Id`, `Vpe`, `Hw`) that do not exist. **Operator-gated blocker:** GitHub creates `<repo>.wiki.git` only when the first page is saved in the web UI — no REST endpoint exists and push-to-create was tested and fails — so the operator must create one page at `henols/firestarter_prom/wiki` before anything can be pushed there; all other work is unblocked. The 999.12 honesty constraint is in scope and not optional: relocation must not upgrade a `support_status` or a `PROTOCOL-LEDGER` `UNVERIFIED` bucket into implied support, and the drift check is its mitigation. **Known sequencing hazard accepted, not solved:** Backlog 999.9 renames all three repos and would invalidate every link written here; the operator was shown this and chose to proceed and sweep later. Prior footer retained below.*

*Last updated: 2026-08-25 — **v1.34 (Pre-Merge Hardware Regression Validation) STARTED.** Phases continue at **160**. A hardware gate in front of the three open v1.33 PRs (`prom#43` / `fw#56` / `app#54`), all unmerged. v1.33 shipped **−2938 B flash / −13 B RAM** on the premise of byte-level equivalence — heap allocator removed, 64-bit runtime dropped, `jsmntok_t` 8 → 6 B, command-decode table reworked — proven by native tests, golden traces and cold builds, and **run on no Arduino at all**. v1.34 runs it on silicon: **five distinct board×shield cells** (Uno / uno328pb / Leonardo on Rev 2.0; Leonardo on Modified Rev 0 / Rev 2.0 / Rev 2.2, with Leonardo+Rev 2.0 shared between the sweeps), each as an **A/B against the pre-v1.33 merge-base** (fw `8695ee5`, app `6bfa645`) with two chips per pass — W27C512 (DIP28, `0x07`) and W29C020 (DIP32, `0x05`) — for **20 full write→read→verify cycles**; plus a `dev test` sweep of all 11 v1.15 inventory chips on the Leonardo + Rev 2.0 reference rig. The control arm is the deliverable, not a formality: it is the only thing that separates "v1.33 broke this" from "this was always broken here", and v1.31 closed explicitly **without** a control run. Known faults are declared **before** the bench runs — uno328pb cannot finish a program (999.2), W27E512 and W27E040 carry stuck erase bits (D-32), W29C040's boot block is permanently locked, AM27C020 is marginal and cannot arbitrate anything. Only v1.33-**caused** regressions get fixed in-milestone. Second deliverable: the Modified Rev 0 rework trace, blocked on operator photos since v1.7, closing the ten `TBD pending Phase 35` cells in `v1.7-SHIELD-REVS.md` §4/§5. **v1.34 does not merge** — it closes with an evidence table and a recommendation; the merge stays operator-gated, as every outward-facing step has since v1.21, and because a merge to `beta` auto-fires a pre-release cut. Three seeds triggered at activation (voltage calibration, Rev 2.2 3-pin header / 2516 family, per-pin-map jumper table) and all three were **declined** to keep the milestone a regression gate. Prior footer retained below.*

*Last updated: 2026-08-22 — **v1.33 (Source Hygiene & Firmware Size Reduction) STARTED.** Six phases, 154–159. Two halves that share one property: both make the source shorter and neither changes behaviour. First the promoted Backlog **999.34** provenance-comment sweep (~646 GSD `// Phase NNN (REQ-NN):` comments across 167 files; firmware ~345/94, host ~301/73) — **split** per D-01, so Phase 154 sweeps source and *builds* the citation-remap tool while Phase 159 applies it **once** over the composite diff (measured: **723** citations would otherwise be remapped twice, and 41% of that rework traces to four added `#include` lines). Then four **measured** firmware size reductions totalling **−2938 B flash / −13 B RAM on all three AVR targets for a net −2 lines of source**, validated at 172/172 native across seven runs: `mem_util_blank_check` malloc'd **four bytes** and was the allocator's only caller anywhere, dereferencing the result unchecked on a part with ~470 B free RAM (**the firmware becomes heap-free**); `rurp_read_voltage_mv` was the only user-code caller of the entire 438 B 64-bit runtime; the VPP-report and chip-ID-report blocks were copy-pasted **4× each**, holding 24 of the image's 30 `__udivmodhi4` call sites between them; and `json_parser.c`'s `key_parsers[]` re-matched every wire key a second time inside each `get_*` stub, costing **1012 B** across 11 PROGMEM-function-pointer stubs while five *identical* directly-called siblings cost zero. **Leonardo Caterina headroom 502 B → 3440 B (6.9×)** — which matters because v1.32 Phase 151 left that target at zero MERGE-05 headroom. **MERGE-05 is one-sided** (`check_size_baseline.py:697` is `if flash_delta > allowance`), so this is the first size movement in the project's history needing **no** named exemption (D-03). **Scoping was NOT done by this activation** — `ROADMAP.md` §v1.33 and `REQUIREMENTS.md` (31 requirements: SWEEP / DEAD / DEDUP / DECODE / LAND / REMAP) were hand-authored by `/gsd-explore` routing on 2026-08-22 and are pointed at, not regenerated, because the GSD roadmap/requirements verbs normalise whole files; `phases.clear` was **skipped** (126 phase directories exist). This activation contributed the §"Current Milestone: v1.33" section, the `STATE.md` frontmatter switch, and the commits. Phases 155–158 are **review, decomposition and landing** phases — the work is already implemented on firmware branch `size-reduction-survey` (off `8695ee5`) and captured at `.planning/notes/firmware-size-reduction-measured.patch`. **Explicitly OUT: replacing JSON with a binary command protocol** (operator, 2026-08-22) — measured **−3728 B flash / −512 B RAM** on `leonardo`, the largest single saving the survey found, deliberately not taken because it is a breaking cross-repo wire change; stays queued as **v1.28** and filed as Backlog **999.35**, whose figure **overlaps DECODE-01** and is therefore **not additive**. **No criterion requires a physical board** (D-02); the one honest ceiling is that `src/boards/rurp_common.cpp` compiles in no native environment, so the voltage reformulation has no native coverage and Phase 155 must establish a committed numerical oracle. Meta forked off local `beta` @ `59a9ff5d` as `v1.33-source-hygiene-size-reduction`. **Next:** `/gsd-discuss-phase 154` — that phase's requirements are deliberately UNSET because its triage policy is the substance of the phase. Prior footer (v1.31 close) retained below.*

*Last updated: 2026-08-18 — **v1.31 (27C Programming-Algorithm Fidelity) SHIPPED and archived via `/gsd-complete-milestone`.** 9 phases (138–146), 74 plans, 164 tasks, **45/45 v1 requirements**, all nine phases verified. Roadmap and requirements archived to `.planning/milestones/v1.31-{ROADMAP,REQUIREMENTS}.md`; `REQUIREMENTS.md` removed via `git rm` for the next milestone. **Closed via PRs to `beta` in all three repos, not direct merges**, per operator decision — the same posture v1.30 took. Meta tagged `v1.31`; submodule gitlinks re-pinned off their stale v1.30-era commits to the v1.31 tips; the gh#15 reconciliation posted as the first post-push act. **No beta cut** — `3.0.0bNN` follows the PR merges, and stable remains operator-gated. Eighth consecutive `override_closeout`: **9** carry-forward `audit-open` items acknowledged, **none originating in v1.31**, down from 14 because the 2026-08-09 sweep closed Phases 71 and 85 on evidence and retired two debug sessions into precise trackers; what survives is genuinely hardware-gated (the Uno-class legs of Phases 08/09, Phase 84's operator sign-off), so it needs bench time rather than another acknowledgement. **Three things this close did rather than accept:** (1) authored the missing `145-VERIFICATION.md` from the existing bench record — the phase had shipped its evidence into `145-BENCH-LOG.md` and its 145-08 verdict but never emitted the conventional artifact, so readiness read the phase unverified while its three requirements were already ticked on audited evidence; the report cites that record rather than re-deriving it, and says plainly that it **cannot** be re-run without hardware. (2) Found and worked around a GSD tooling defect instead of trusting its output — `plan-scan.cjs`'s loose `/PLAN/i` fallback counted `146-REPLAN-BRIEF.md` as a phantom **14th** plan in a 13-plan phase, which drove `phase_complete: false` for a closed phase and wrote `completed_phases: 8` / `percent: 89` into `STATE.md`; the brief was renamed to `146-RESCOPE-BRIEF.md` with a provenance note in-file (no citation referenced it) and the scanner behaviour filed, not fixed. (3) Hand-repaired `STATE.md` after `gsd-tools milestone.complete` corrupted it — `current_phase` written as **31** (a parse artifact of "v1.31"), `stopped_at` overwritten with a **stale 146-11** line, and the progress block written 8/9 at 89 %. The v1.30 close shows the identical signature (`current_phase: 30`, 7/8, 88 %), so both defects had been mis-reporting silently for at least two milestones. **The milestone's own boundaries carry forward unchanged:** the ~6.25 V ceiling as accepted debt; **MERGE-05's +96 B leonardo band breach open and un-adjudicated** with the operator as its named owner (its green reading came from the anchor **moving**, not from growth staying inside the band); `0x08` and `0x0B` unvalidated on hardware; program-window VPP/VCC under load still blocked by the Phase-97 DTR-reset-on-close gap. Twelve items carry the literal phrase `no v1.31 owner` and sixteen un-taken readings each name their blocker. Backlog **999.30** and **999.31** were filed by this milestone's own bench work. **Next:** `/gsd-new-milestone`. Prior footer (Phase 144 close) retained below.*

*Last updated: 2026-08-14 — **Phase 144 (Tests & Build Verification) CLOSED and verified** (7 plans in 6 waves, 8/8 must-haves, TEST-01…TEST-08 Complete). Dual-repo, but **zero `src/` change** — every commit is a test, a fixture or a baseline. Three new gates: a **requirement→case mapping** gate machine-checking that the cases TEST-01…05 are flipped against actually exist (88 names across three suites, with a non-vacuity leg so an emptied scan root fails instead of passing over an empty set); a **six-segment trace exhaustiveness** gate partitioning all **885** entries (620 pre-change + 265 new) by set equality over index ranges plus disjointness, never a count sum, with every segment carrying a named attribution from Phases 140–143; and a **cross-repo CAP-03 byte-layout parity** gate comparing the firmware's `MSG_OK_READY` pack order against the host's `_decode_id_frame` offsets — a comparison neither repo had ever performed — proving the budget is read at the **computed `ver_end`**, never a literal index. Ten planted violations across the phase, each seen RED on its own assertion before its GREEN was believed. **Both standing REDs retired:** `native_trace_v131` 5/5 after D-05's pure `git mv` preserved the Phase-138 blob `ca3e09f1…` and D-06 captured a fresh trace at this tip (**91/115/59**, validated against three stale-paste discriminators — never `141-NEW-TRACE.md`'s stale 119); and `check_size_baseline.py` green after all three baselines were re-anchored. **MERGE-05 reads green because its anchor moved to v1.31, not because growth stayed inside v1.24's band** — F-141-01's overrun was never remediated, and the band is now repurposed as a forward tripwire armed at 0 B for Phases 145–146. One cold consolidated measurement against the final tree: **+870 / +870 / +890 B** flash with **RAM unmoved** on all three targets; leonardo at **26906/28672 B (93.8%, 1766 B headroom)**, checked explicitly rather than discovered. Firmware pytest 292 → **312**; host suite 1578 → **1590** at 82.92% coverage; mypy 33 against the 35 watermark; all four CI-scoped legs green on the 3.11 CI-replica interpreter. Dual-repo constants parity proven in **both** directions — the absent path evidenced by a **skip count** (6 passed / 8 skipped; full suite 1540 + 50 = 1590), never by exit 0 alone. **Four disclosures stated rather than implied:** (1) D-14's anchor-move sentence above. (2) D-03 — the overprogram **arithmetic** is proven, the **in-loop wiring on a live row is not**, because no shipped row sets `overprogram_factor`. (3) D-08 — nothing gate-asserts `eprom_v131_expected_prechange.h`; its preserved blob is hand-verifiable, not machine-checked (**F-144-03**, deferred by choice). (4) D-15 — the three `*_v131` envs run in **no CI leg of either repository**, and the app's CI does not exercise the cross-repo parity gates; those `requires_fw` gates fail **OPEN** across the repo boundary by design. **No bench claim and no real-silicon claim** — Phase 145 owns all of that; TEST-04's “disables every high-voltage route” is bounded to the emitted control-register stream. Approved at 144-07's blocking operator gate. Phases **138–144 CLOSED**; next is **Phase 145 (Bench Validation)**. Prior footer (Phase 143 close) retained below.*

*Last updated: 2026-08-13 — **Phase 143 (Host Timeout, Progress & Pulse Override) CLOSED and verified** (10 plans in 5 waves, 5/5 success criteria, HOST-01…HOST-05 Complete). Dual-repo. **BF-1 closed:** the v1.31 firmware branch had forked one commit before firmware PR #49, so it carried no CAP-02 identity tail and the v1.31 app **refused every connection to a v1.31 build** — CAP-02 is now ported and CAP-03 appended in one pack block (`[buffer u16][hw_rev u8][ver_len u8][ver bytes][budget u16]`, budget at the computed `4 + _vlen`). The firmware advertises a per-block worst-case write time from the Phase 140 table plus the live pulse width; the host reads it at the computed `ver_end` under a derived `[1, 14400]` clamp and uses it verbatim as the write-path response timeout (derived 120 s fallback; threaded as a default-`None` kwarg so `verify_eprom` stays byte-identical on the old 10 s default). Intra-block `MSG_DATA_PROGRESS` at 1000 ms cadence renders without acking, positioned at `absolute − start_addr`, never rebuilding, latched against rewind. `0xBD`/`0xBE`/`0xAE` surface as `EpromOperationError` naming the address, with a hint stating the abort's disposition and no retry. `write --pulse-us N` (`IntRange(1, 65535)`, `default=None`, `write`-only) rides the existing `pulse-delay` field and always prints provenance. Firmware pytest 282 → **292** (two new source-contract gates); host suite 1547 → **1578** at 82.92% coverage; `native_loop_v131` 79/79; both pinned native envs 141/141. **Four disclosures recorded rather than smoothed:** (1) the headline is *a long write now reports what it is doing, and a failed byte now reports as a failed byte* — **not** faster, **not** more reliable, **no bench evidence** (Phase 145 owns that). (2) Progress is **`leonardo`-only** — emit and `millis()` state both inside `#ifndef SERIAL_ON_IO`, because on `uno`/`uno328pb` the 4-slot deferred-log buffer would overflow and silently drop the following `MSG_ERR_MAX_PULSES`, converting a program failure into a transport timeout, i.e. HOST-03's exact anti-goal on a path that works today (**BF-2**; D-02 shipped scoped down, pinned by a source contract since `uno_rurp_shield.cpp` is compiled in no native env). Uno-class flash came out byte-identical, proving the guard excludes the code. (3) **D-11's formula was replaced, not implemented** — it under-estimated **2×** at `--pulse-us 49999` on `0x0B` (true bound 99 998 µs, not 50 000) and would have spuriously timed out a *working* write (**BF-3**); the corrected arithmetic lives in a new, unpinned `src/proms/eprom_budget.{h,cpp}` TU so it has a real native oracle. (4) **MERGE-05 stays RED** as F-141-01, not remediated; `check_size_baseline.py` is operator-accepted RED for the enumerated reasons only (F-141-01, the OD-2 CAP-02 `+34 B` drift, this phase's growth against a deliberately un-updated baseline), leonardo fitting at **26906/28672 B (93.8%, 1766 B headroom)**; `native_trace_v131` RED by design (D-24) with **zero** frames added. Approved at 143-10's blocking operator gate with the CAP-02 port disclosed as a **re-implementation citing `13eb350`**, not a cherry-pick. **No new message id — `0xBF` still free.** D-01's ROADMAP-prose correction (this phase is *not* independent of 140–142) is deferred to Phase 146 / CLOSE-04 by design. Phases **138–143 CLOSED**; next is **Phase 144 (Tests & Build Verification)**. Prior footer (Phase 141 close) retained below — Phase 142's close did not add one.*

*Last updated: 2026-08-10 — **Phase 141 (Per-Byte Program Loop) CLOSED and verified** (9 plans in 5 waves, 5/5 success criteria, LOOP-01…LOOP-08 Complete). The milestone's central change has landed: a per-byte fixed-width pulse→verify loop replaces the block-level mismatch-mask retry loop end to end, with `program_mismatched_bytes()`, `verify_and_update_mask()`, `NUMBER_OF_RETRIES` and the adaptive width-growth formula grep-verified absent from `src/`/`include/`, and every over-ceiling delay routed through the new 32-bit-safe `mem_util_delay_us`. Firmware pytest 244 → 256; `native_loop_v131` (sixth native env) 6 → 39 cases; both pinned native envs unmoved at 141/17; host suite 1547. Thirteen planted-RED proofs across plans 141-05/06/07/08 — every new gate leg was seen RED on its own assertion before its GREEN was believed. **Three disclosures the phase chose to record rather than smooth:** (1) **MERGE-05 is RED** on all three AVR targets (uno +492 B, uno328pb +498 B, leonardo +328 B vs a 64/64/0 B band), accepted by explicit operator decision as **F-141-01** — ~+204 B of it is Phase 140's parameter table finally linking now that `eprom_params_for` has a live `src/` caller, and the 64 B band predates that table; RAM is exactly unchanged, and leonardo now sits at 92.1% flash with 2272 B headroom, a real constraint on Phase 142. The pre-registered prediction (`141-PREDICTIONS.md`, committed before any `eprom.cpp` edit) said +30/+30/+18 B and was missed ~14× — the under-budgeted ingredient was the *first-live-reference* cost of the Phase 140 table (~+204 B measured vs ~70-80 B budgeted). Registering the prediction is what caught it. (2) Two goal criteria are **proven narrower than they read**: the overprogram pulse is proven only on the pure `eprom_overprogram_us` function, because `overprogram_factor` is 0 on every shipped row; and LOOP-06's *read*-skip holds only on `0x0B`, since `0x07`/`0x08` ship `VERIFY_PER_PULSE_PLUS_FINAL` whose final pass re-reads every byte unconditionally — the *pulse* skip LOOP-06 actually requires is universal. (3) `native_trace_v131` is deliberately RED on 3 of 6 cases (D-10) and its determinism assertion is **structurally unreachable** behind the failing length check, so it is recorded as a non-claim rather than as a passing leg; Phase 144 / TEST-06 owns the re-freeze, with `141-NEW-TRACE.md` supplying the post-change side. `native_loop_v131`/`native_params_v131`/`native_trace_v131` run in **no CI leg of either repo** — local run-by-name obligations. Also handed off: an unscoped-porcelain defect in `test_flash_path_record_sync.py` that every plan in the phase had to work around, and a corrected energy-cap worst case (2 × 49999 = **99998 µs**, not 99999) now living in firmware `CLAUDE.md`. Phases **138, 139, 140, 141 CLOSED**; next is **Phase 142 (High-Voltage Routing)**. Prior footer (v1.31 start) retained below.*

*Last updated: 2026-08-08 — **v1.31 (27C Programming-Algorithm Fidelity) STARTED via `/gsd-new-milestone`.** Scoped from [gh#15](https://github.com/henols/firestarter_prom/issues/15) **as corrected**, not as written: a `/gsd-explore` pass on 2026-08-08 (`.planning/seeds/27c-algorithm-fidelity-param-table-refactor.md`, commit `c60543c5`) found two wrong numbers and one inverted premise in the issue, and this milestone posts those corrections publicly *before* implementation lands. **C1** — gh#15's `0x0B` `pulse: 50000 us` is the fingerprint of BUG-2, a ×100 `interpret_timing()` multiplier over 252 chips that Phase 57 already removed; the true value is **500 µs**. **C2** — pulse width is **DATA, not a per-protocol constant**: measured live against the shipped DB, `0x07` is 100 µs ×113 of 170 (not gh#15's 1000), `0x08` is 100 µs ×104 of 127, `0x0B` is 500 µs ×21 of 32; minipro ships `protocol_id` and `pulse_delay` as two orthogonal wire fields and exposes `-o pulse=N` per run. **C3** — the safe 32-bit delay helper is still needed, but for the 75 ms **overprogram** pulse, not for any pulse. **This adjudicates the structural fork in the parameter table's favour (D-01):** protocol owns *shape* (`max_pulses`, `overprogram_factor`, `overprogram_cap_us`, `verify_mode`, `vpp_path`), the database owns the *pulse* — one shared per-byte pulse→verify loop, **not** gh#15's three state machines with hardcoded constants. Replaces `program_mismatched_bytes()` / `verify_and_update_mask()` / the flat `NUMBER_OF_RETRIES = 20` / the adaptive `pulse_delay = org + org*retries/20` growth that escalates width where the datasheets hold width fixed and *count* pulses. **D-02:** the `0x0B` one-shot-vs-looped question is not answerable from source (minipro never runs the algorithm — it packs `pulse_delay` into `BEGIN_TRANS` and hands it to closed TL866/T48/T56/T76 firmware), so it ships as a looped pulse→verify with a **50 ms accumulated-energy cap per byte** (`100 × 500 µs`, the classic 2716 total programming time), satisfying both readings. **Enabler:** VPE survives a read (`mem_util_calculate_top_address_register` preserves the HV mask across every `set_address`, `memory.cpp:163-166`), so the `delay(10)` settle stays amortized once per block instead of 512× — with the DIP32 `CTRL_VPP_VPE_DROP_ENABLE`/A16 caveat. **Evidence ceiling fixed up front:** the ~6.25 V program-VCC all four vendor algorithms assume is **unreachable on this shield** (no VCC-raise path), so this buys timing/pulse-count/verify fidelity and **not** silicon-margin fidelity — gh#15 omits this entirely and its acceptance criteria must be amended; a committed claim gate forbids the unqualified "datasheet-conformant" overclaim. Bench coverage is asymmetric by inventory (operator, 2026-08-08): `0x07` **required** (W27C512 / TMS27C512), `0x08` (AM27C020, known marginal from v1.18 Phase 99) and `0x0B` (M2716 / M2732, 25 V NMOS) **opportunistic, skipped-with-reason if absent**. Not behavior-preserving — golden traces encoding today's cadence will legitimately shift; re-baselining is expected work. **Firmware-touching, dual-repo lockstep.** Numbered **v1.31**; Backlog **999.22** (queued as v1.27) retired into it; v1.24–v1.26 left byte-unchanged. Phase numbering continues at **Phase 138**. **Blocking precondition:** `firestarter_app`'s `gsd/v1.30-sdp-surface-retirement` is NOT merged to `origin/beta` (the v1.30 PR was staged but never opened) and must land before the app branch forks; firmware forks off `beta` @ `3085084`. Prior footer (v1.30 Phase 133) retained below.*

*Last updated: 2026-08-04 — **Phase 133 (SDP Leg Mechanism) CLOSED and verified** (7/7 plans, 5/5 success criteria; LEG-09/10/11/15 Complete, 14 LEG requirements still open for Phase 134). `dev test`'s engine now drains a cleanup registry in a `finally` that provably never touches `results`, degrades `SerialError`/`HardwareOperationError` to a recorded BAD step instead of losing the whole report, dispatches `_SDP_OPS` from a fail-closed arm, and machine-verifies op-registration parity. Suite 1301 → 1338; mypy 33/124 against an unmoved watermark 35. **Evidence ceiling honoured: the mechanism is proven, SDP behaviour on silicon is NOT — no hardware ran.** D-15's two-new-source-file budget is now fully SPENT, so Phase 134 has zero headroom against `MIN_CHECKED_SOURCE_FILES` 120. Phases **131, 132, 133 CLOSED**; next is **Phase 134**. — v1.30 (SDP Surface Retirement & Behavioral Lock Proof) STARTED via `/gsd-new-milestone`. Promoted from Backlog **999.25**, operator-queued 2026-07-31 as NEXT after v1.23; scoped from `.planning/notes/sdp-surface-retirement-and-behavioral-proof.md`. Replace v1.22's unverifiable standalone `dev sdp <chip> enable|disable` with a **self-verifying** SDP lifecycle: delete the command, move the proof into a plan-derived four-step `dev test` leg whose oracle is **read-back equality** against a baseline pattern (never an exit code), and land `write --sdp-relock` as the single deliberate-protection surface. **⏸ AMENDED 2026-08-03: the third part did NOT survive scoping — `write --sdp-relock` (Phase 135) was deferred out to Backlog 999.28 by operator decision, phase number not reused, active set 131–134 + 136–137. v1.30 therefore ships the deletion and the behavioral proof and WITHDRAWS the deliberate-protection surface with no replacement; RELOCK-01…06 left v1 scope (56 → 50 requirements), RELOCK-07 was retained and re-homed to Phase 137 with its targets re-pointed at 999.28.** Two scope additions taken at activation (operator, 2026-08-03): the **mypy gate-hardening** v1.23 Phase 127 left OPEN — fail-open `tools/check_mypy_watermark.py` + 69 hidden inherited errors keeping `firestarter_app`'s primary `ci` job RED — and **999.15 / gh#8 dev-tools channel gating**, whose diff this milestone shrinks by deleting a subcommand it would otherwise classify; plus the owed gh#12 outward follow-up. `--sdp-relock` polarity decided: **verify failure ⇒ skip the relock and report it loudly** (leave the recoverable state), per auto-unlock policy (d). **Host-only** — `firestarter_app` alone, no firmware change, no dual-repo lockstep, no `.hex` re-cut; Phase 119's `CMD_SDP_LOCK`/`CMD_SDP_UNLOCK` are what the leg exercises. Numbered **v1.30**, not compacted to the vacant v1.29. Phase numbering continues at **Phase 131**. Meta branch `gsd/v1.30-sdp-surface-retirement` off the v1.23 tip `d1b9ce9e`; app off `beta` @ `16a313a`. **Evidence ceiling fixed up front:** no AT28C part in inventory and `0x0D` stays `UNVERIFIED`, so emission + plan-derivation + read-back-comparison logic are provable here while the causal claim "the lock inhibited the write" is reachable only from a community `dev test` report and does **not** gate the close. Prior footer (v1.23 close) retained below.*

*Last updated: 2026-08-03 — v1.23 (PY32F071 Integration) **MILESTONE COMPLETE + archived.** 8 phases (123–130), 88 plans, 226 tasks, 47/47 v1 requirements (BASE 8 · MERGE 8 · VPP 3 · CFG 7 · HOST 8 · REL 4 · PCB 5 · CLOSE 4), 0 unmapped; close phase 130 verified 4/4. A **fourth board target** now exists beneath the algorithm-first dispatch contract without disturbing it — and the whole milestone is **software-only by physical necessity**, because no PY32F071 PCB exists and nothing in it has ever run on this silicon. Shipped: the portability + py32 firmware stack landed **atomically** (the inherited "HAL prep leads" sequencing was measured a trap — that half alone takes `pio test -e native` from 141 cases / 17 suites passing to 0 passing / 17 ERRORED), the C-1 CMake rename repaired on a tree that merged with *zero textual conflicts* yet failed at CMake configure time, `push: branches: [beta]` added so ARM is built on `beta` at all, and the pin-map guard that was `#define`d `1` two lines above its own `#if !… → #error` made able to fire; the hand-authored VPP **seam only** at 0 B flash / 0 B RAM on all three AVR targets, with AVR-class manual control recorded **permanent**; dual-slot CRC32 flash-persistent config for a part with no EEPROM, behind a per-platform seam whose AVR EEPROM backend is a proven pure move, with Sector 15 reserved and PR #48's non-persisting `config.cpp` deleted; the pure-Python DFU 1.1/DfuSe host installer with `DFU_UPLOAD` readback and a 120 KiB envelope matching the reserved map (suite 1158 → 1293, 0 skipped); the release-asset fold proven on **two real CI dispatches** — one publishing `firestarter_py32f071.hex`, one planting an ARM break and still publishing all three AVR assets, which also empirically validated `outcome` ≠ `conclusion` for a contained step; the flash-path and PCB record written before any schematic, in two lockstep layers held body-for-body by a 41-leg cross-repo gate, top-billing **F-10** (a contiguous 8-bit bus is *physically impossible* on 2 of 7 candidate packages — a part-selection constraint, unrecoverable after layout); and a six-tier honesty ledger that pairs every permitted claim with its explicit non-claim. **Three gates were found lying, in three different ways, and all three are recorded rather than smoothed:** the cross-repo `_FW_ABSENT` proxy failed **OPEN** (renaming one file flipped 5 legs PASS→SKIP at exit 0 with a false "checkout absent" reason); `check_mypy_watermark.py` had been **fail-open** since it shells a bare `mypy` that py3.12 rejects, hiding **69** inherited errors against a watermark of 35; and one leg of the Phase 129 gate was authored **unreachable** (it required `MEMORY` and `{` on one line; the linker script has them on 8 and 9) — *a gate that has never been seen to pass is not yet known to be reachable.* Also recorded: **a phase's own validation procedure can be wrong in a way that would produce false evidence** (Phase 128's prescribed run-B break would have failed before the ARM build and published nothing, proving the opposite of REL-03). Closeout **`override_closeout`**: Phase 126 verified `passed-with-findings` (informational — Criterion 3's literal "empty `git diff`" wording unmet because the phase's own `#if` guard forced one compiler-argv line into the test, no assertion changed) plus the same **14** pre-existing cross-milestone `audit-open` items acknowledged-and-deferred for the **sixth** consecutive close; **none originate in v1.23** (see STATE.md → Deferred Items). Both channels public at the observed cut tag **`3.0.0b15`** — read verbatim from `gh release list`, never predicted — the firmware prerelease carrying **four** `.hex` assets including the **first-ever publication** of `firestarter_py32f071.hex`, and PyPI carrying `firestarter==3.0.0b15` from a clean venv; **no stable release**, `info.version` stays `2.0.7`. Meta tagged `v1.23` on `gsd/v1.23-py32f071-integration`; firmware + app tagged `v1.23` on `beta`; gitlinks bumped to the published b15 commits; **`main` not merged** in any of the three repos, per v1.19–v1.22. Deliberately left OPEN, not fixed here: the 69 mypy errors + the fail-open watermark tool (app `ci` job RED until a gate-hardening phase), FUT-ORACLE's absent ARM bus-trace oracle, D-17's USB-identity ship-gate tension, and `check_ledger.py`'s 2 pre-existing `LEDGER-01` REDs. Next: `/gsd-new-milestone` (v1.30 SDP Surface Retirement & Behavioral Lock Proof is the operator-queued next slot). Prior footer (v1.22 Phase 121 close) retained below.*

---

*Last updated: 2026-07-29 — v1.22 **Phase 121 (`dev test` FIX + GATES + DOCS + REDESIGN) COMPLETE + verified 10/10 success criteria, 9/9 requirements.** 14 plans across 10 waves, host-repo-heavy with one catalog-driven firmware touch; DEVTEST-01..06 + GATE-01..03 all Complete. Ordering was load-bearing and held: D-18's golden regen landed alone as the first commit with zero `dev test` code in the tree, the ruff `extend-exclude` preceded every formatter run, and the fail-closed `_dispatch_step`/`_dispatch_multi_run` arms landed before `OP_WRITE_PARTIAL` existed (Pitfall 1a — an unhandled op called `erase_eprom()` twice and reported `OK`). Delivered: **DEVTEST-01** host half at its root cause — `database.py:convert_to_programmer` clears `FLAG_CAN_ERASE` for protocol `0x0D`, so `derive_plan`'s generic NA-erase branch fires for free with a family-fact reason and never the flag name (live: `AT28C256` erase step `NA`, `operator.erase_eprom` never called, `ladder_state = community-reported` not `community-fail`). **GATE-01** — `tools/check_sdp_capability_invariants.py` with two planted-violation fixtures, exit 0 on real source and exit 1 on both plants with distinct wording (anti-hollow discipline). **DEVTEST-02/03/04** — `dev test` takes zero options (`--destructive`, `-y`, `--yes`, `--output-dir`, `--submit` all now `No such option`, exit 2), an unconditional first-line always-writes notice, UV-ness decided once at plan level via `is_uv_eprom` measured live at **exactly 301/301** against the 746-entry DB (the old `algorithm == 0x0B` execution-layer proxy measured **32/301** — the gap the structural axis closes), and a genuinely new third mode: `_resolve_write_scope`'s non-UV→full-unprompted / UV+non-interactive→partial / UV+interactive→stop-and-ask, carried on `Step.write_region` with `OP_WRITE_PARTIAL` in both frozensets and `schema_version` 1.2. **DEVTEST-05/06** — `submit_report` runs a read-only `gh issue list` dedup query on `dedup_fingerprint` FIRST, asks on every interactive run, offers a comment carrying new evidence on a duplicate, degrades to an explicit "check could not run" line on any `gh` failure (widened one failure mode past spec to also catch `OSError`, so an absent `gh` binary cannot crash the sweep), and asserts the negative argv as a **deny-set** across both `gh` paths including short forms. **GATE-02** — all eight docs corrected across both sub-repos (list widened per D-17 to add `doc/community-validation.md` + `doc/beta-testing-install.md`, the widening recorded in phase artifacts with `REQUIREMENTS.md`'s own wording left unedited), `doc/lockable-proms.md` first-committed with its wrong §17 Atmel row split against `sdp_capability.py`'s derived allow-set and deliberately no provenance header (D-16, an owned trade-off not to be re-opened), and the `0x5F` unlock-done message given the same protection-state-is-not-readable caveat `0x61`'s lock-done sibling already carried — hand-edited only in the canonical meta catalog, both mirrors regenerated via `sync_to_subrepos.sh`, three-way byte-identity re-established. **GATE-03** — the nine-row cross-repo set re-run verbatim at the phase's FINAL commit under both the devcontainer 3.12.13 and a `uv`-provisioned CI-parity 3.11.15 venv: host pytest 1134/0 under both, firmware native 141/141 in both envs, `pio run` 3/3 unchanged, `check_dispatch.py` / `check_devtest_orchestrator.py` / `diff_db.py` all PASS, recorded in `121-NONREGRESSION.md`. The py3.9 pytest impossibility was **reproduced live rather than asserted** (`syrupy>=5.0` won't resolve on a real 3.9.25) and recorded with its cause; `diff_db.py` identity means "still exactly 2 explained changes, 0 new, 0 removed" — not zero — and the record says so. **Two record corrections, both against this phase's own planning documents:** (1) Plan 121-12's must-have predicted "a generated firmware header changes" — it does not; `firestarter_fw/include/messages.h` regenerated to a **zero diff** because the C++ header carries only numeric id `#define`s and format text is decoded host-side, so `pio run -e uno` came out byte-identical. The firmware footprint is still non-docs-only via the tracked catalog mirror (catalog-sync CI stays red-until-milestone-merge by design), but narrower than D-15 predicted. (2) Plan 121-14's "Tick GATE-03 only" instruction was stale, written before commit `2492154` reverted 121-08's premature DEVTEST-01 tick and left "the checkbox stays unticked until Plan 121-14 re-verifies every row" **in** the live requirement text; 121-14 therefore closed DEVTEST-01/02/03/04 + GATE-01 alongside GATE-03, each independently re-verified against the live tree, never against a SUMMARY's own claim. **Latent debt introduced here, recorded not closed:** 121-01's authorized golden regen pushed `tests/golden/v1.3-COVERAGE-MATRIX.md` from `DEFECT-COV-77` to `DEFECT-COV-95` while `.planning/milestones/v1.3-defect-coverage-ids.json` stayed at 78 keys / max 77 — the golden now names 18 IDs the ledger has never heard of. The test passes only because the generator re-derives them deterministically; the next run of the ledger-persisting path will produce a real diff. (121-14 separately self-caught and reverted a generator misfire against the live ledger before any commit — ledger confirmed byte-identical to HEAD.) Validation ceiling held: no AT28C part was on the bench, `0x0D` stays `UNVERIFIED`, zero `support_status` changes, 84-chip count unchanged, zero silicon claims anywhere in `121-NONREGRESSION.md`. Gitlinks stay PINNED (submodule pointer bumps deliberately uncommitted per this project's pattern). **Bookkeeping note:** PROJECT.md footers for Phases 118, 119 and 120 were not recorded at their close — see `.planning/STATE.md` and the phase SUMMARY files for those. Next: `/gsd-discuss-phase 122` (CLOSE — honesty ledger, community ask, release decision; `CLOSE-01/02/03` remain correctly unticked). Prior footer (v1.22 Phase 117 close) retained below.*

---

*Previously: 2026-07-28 — v1.22 **Phase 117 (FIX — remap-aware `0x0D` emitter + honest completion signal) COMPLETE + verified 6/6.** 5 plans across 5 strictly-sequential waves, firmware-only, FIX-01..06 all Complete. The milestone's headline fix landed and is honestly proven: `eeprom28c_emit_command_sequence` routes every command write through `handle->firestarter_set_data` → `mem_util_remap_address_bus` (FIX-01), closing `DIP32_28C512_EEPROM`'s A16–A18 staleness gap for its 18 chips ≥64 KB as a by-product (FIX-03); the inverted `(0x5555, 0x20)` read-back **deleted** for an unconditional `t_WC` wait plus a bounded silent DQ6 toggle poll that never writes `response_code` (FIX-02); `eeprom28c_wait_for_write` deleted and split into `eeprom28c_wait_for_page_write` + `eeprom28c_verify_page_readback` (FIX-06 — reframed as a **conflation** bug, not a sampling-rate bug, fourth ⚠ block above); constant-level terminal-byte + table-identity guards reading the **production** array via `extern` (FIX-05, `test_sdp_harness` 13→15 cases); six frozen artifacts pinned byte-identical to base `ada4bdc` by literal blob SHA (FIX-04). D-03's two-commit RED-then-fix discipline held — `git diff e5b9e87..b30b91c -- test_eeprom28c_sdp.cpp` is **empty**, so the 8/8 GREEN came purely from production code with the oracle byte-untouched. Firmware native **108/108**, both board targets SUCCESS. **Measured, contradicting the research prediction: Leonardo flash delta `+204 B`, not net-negative — Phase 119's LOCK-06 headroom must be judged against this.** **One structural miss, caught by the phase's own regression gate:** Phase 117 broke 4 Phase-116 host-side source-scanning gates (`test_sdp_table_parity` ×3, `test_check_no_log_in_sdp_window` ×1) because no plan owned re-anchoring them after the rename/deletion; fixed append-only (`firestarter_app@9dd11a9`) with honest record corrections (`firestarter@f8d10a5`, `117-05-SUMMARY.md`), and Phases 118–122 must now carry an explicit gate-re-anchoring task. Validation ceiling held: permitted claim is that the sequence is **emitted** as specified, byte-exact across all four `0x0D` pinouts — `0x0D` stays `UNVERIFIED`, zero `support_status` changes, 84-chip count unchanged, no silicon claim. Known pre-existing debt, not a v1.22 regression: `test_audit_coverage_matrix.py` golden drift (proven unrelated by stash-and-rerun). Gitlinks stay PINNED. Next: `/gsd-discuss-phase 118`. Prior footer (v1.22 Phase 116 close) retained below.*

---

*Last updated: 2026-07-30 — v1.23 (PY32F071 Integration) STARTED. Land the in-flight PY32F071 firmware port and the host USB-DFU firmware installer onto `beta` as one lockstep integration, plus the cross-repo release-asset unblock, without touching the three AVR targets. Firmware: `agent/portability-macros` (5 commits, gh#16 HAL prep — `rurp_platform.h`, `rurp_millis()`/`rurp_delay_ms()`/`rurp_delay_us()`, board-local pin maps behind platform-independent logical identifiers) then `agent/py32f071-toolchain` (PR #48, 52 commits — ARM GCC + CMake, pinned OpenPuya SDK `0ed2f4b`, CherryUSB CDC, SysTick+TIM3 timing, VREFINT 12-bit ADC, one-snapshot `IDR` / atomic `BSRR` 8-bit bus), all **72 commits behind `beta`** so the rebase is real work. Plus py32 flash-persistent CRC dual-slot config (the part has no EEPROM; PR #48's config is runtime-only), the host DFU installer (`feature/py32f071-fw-install` @ `4ee64a1` — pure-Python `py32_dfu.py`, `flash_method()` dispatch, beta-only channel gating), the `beta-build.yml` release-asset fold so `firestarter_py32f071.hex` ships as a release asset rather than an Actions artifact, and the flash-path/PCB-requirements record (self-flash bootloader over existing CDC+COBS as intended primary route; factory USB DFU as maintainer recovery; BOOT0/nBOOT1 strapping + SWD pads + contiguous 8-bit port + flash budget, all cheap now and expensive after layout). **DAC VPP lands as the SEAM only** <!-- recordscan:allow portability-macros-provides: coincidental collocation -- `agent/portability-macros` (the branch name, earlier in this same paragraph) and "capability macros" (this VPP seam's own macros, RURP_HAS_VPP_DAC / RURP_VPP_DAC_BITS per Phase 125) both land in this one long footer paragraph by coincidence. R-1's actual finding -- that portability-macros does no pin-map work and has zero common-code timing consumers -- is neither asserted nor contradicted here. Not a stale claim; flagged by plan 130-02, addressed by plan 130-07. --> — capability macros, enums and `RURP_VPP_CONTROL_MANUAL`, with `rurp_set_vpp_target_mv()` refusing on every board; PR #45's closed loop depends on the calibration layer it shares an API with, three of its ten commits reach into the White-Box Voltage Calibration milestone's files (`rurp_common.cpp`, `rurp_types.h`, `rurp_config_utils.cpp` → `CONFIG_VERSION` + EEPROM migration), and with no PCB a closed loop cannot be validated at all. **No PY32F071 PCB exists** → software-only close like v1.22; PR #48's pin map stays explicitly provisional and must not be trusted near a PROM; permitted claims are builds-clean / suites-pass / DFU-exercised-against-descriptors-and-mocks, never "runs on a PY32F071". Start from PR #48, **never** the closed PR #47 whose `usb.c` is `weak` no-op stubs that link and leave the board silent on USB. Slot handling: takes **v1.23**, retires the queued `v1.28 PY32F071 Port` + `v1.29 PY32F071 USB Firmware Install` slots into itself, renumbers `Binary Command Protocol` v1.23 → v1.28, and leaves v1.24–v1.27 untouched so existing by-number cross-references keep resolving. Dual-repo lockstep; meta branch `gsd/v1.23-py32f071-integration` off the v1.22 tip `8be00ee`; sub-repos fork off `beta`. Phase numbering continues at Phase 123. Prior footer (v1.22 Phase 116) retained below.*

*Last updated: 2026-07-27 — v1.22 **Phase 116 (GROUND TRUTH + TRACE HARNESS) COMPLETE + verified 6/6.** 7 plans across 5 waves, software-only, zero production-code risk (`git diff beta..HEAD -- src/ include/` empty in both sub-repos; `flash_utils.cpp` and `chip_database.json` byte-untouched). Built the trace oracle the rest of the milestone rests on: `host_stubs_common.inc` extended with an opt-in ordered recorder interleaving data bytes and `/CE`//`/OE` edges with register writes (flag `HOST_STUBS_REAL_REGISTER_UTILS`, byte-exact when unused — firmware native 80/80 → 82/82 → **95/95**); the parked RED `test_eeprom28c_sdp` suite (7 cases, `-I` only, no `test_filter`, `TODO(v1.22 Phase 117)`) whose one-line enablement IS Phase 117's RED→GREEN proof, with verbatim evidence in `RED-BASELINE.md`; all four anti-hollow negatives executable and independently RED (unlock table → `0x10`, lock/write table swap, planted `LOG_` in the timing window via `FIRESTARTER_SDP_SRC`, `protocol != 0x0D` → `0xBB`); the call-ordered scripted mock replaced by an address-keyed one with `test_eeprom28c_chip_id/` retired and zero `s_mock_bytes[…] = 0x20` sites surviving; `chip_id_check: false` pinned across all 84 `algorithm == 13` entries with no skipif; and `116-PREMISE.md` settling TRACE-06. **Two measured findings corrected the milestone's own framing** (third ⚠ block above): `write at28c256` does abort at INIT on `3.0.0b11`, and the write-inhibit population is **66 of 84, not all 84** (`DIP32_28C512_EEPROM`'s 18 chips are inhibited on 0 of 6 writes at plain INIT-time register state). Validation ceiling held: `0x0D` stays `UNVERIFIED`, zero `support_status` changes, 84-chip count unchanged, no silicon claim anywhere. Known pre-existing debt, not a v1.22 regression: `test_audit_coverage_matrix.py` golden drift. Gitlinks stay PINNED. Next: `/gsd-plan-phase 117`. Prior footer (v1.22 start) retained below.*

*Last updated: 2026-07-27 — v1.22 (AT28C Software Data Protection Lifecycle) STARTED via `/gsd-new-milestone`. Promoted from Backlog 999.19 (gh#12, root-cause half, leads) + 999.18 (gh#11, verification half, follows), selected as NEXT at the 2026-07-27 backlog review. **Reframed at kickoff by reading the tree:** the promoting triage note asserts protocol `0x0D` "currently has no SDP path today", but `eeprom28c_write_init` (`firestarter_fw/src/proms/eeprom_28c.cpp:105-113`) has run the 6-write `AA-55-80-AA-55-20` SDP-disable sequence unconditionally since v1.0-era Phase 06-01 (`34cefac`), it is on `beta`, and it therefore shipped in `3.0.0b11` — as did 64-byte page write + read-back polling (`eeprom_28c.cpp:126-140`), which retires gh#11's 339 s byte-at-a-time symptom. Both community reports are 2024-vintage (app 1.0.13), predating the 3.0.0 architecture entirely. So the milestone is "complete and expose SDP", not "implement SDP": wire the missing **enable/lock** path (`FLASH_ENABLE_WRITE_PROTECTION`, `include/flash_utils.h:48`, has zero callers), expose lock **and** unlock as explicit user-facing operations behind the v1.21 destructiveness gate with explicit opt-in, make today's silent unconditional auto-unlock observable and opt-out-able, and replace the weak `0x5555` read-back success inference with a real signal. Validation is **software-only** (3-tier harness: native golden register traces + host tests) — operator confirmed no AT28C part on the bench; gh#11/gh#12 closeout is a best-effort re-test ask on `3.0.0b11`, with **no milestone requirement depending on a community reply**. Dual-repo lockstep; phase numbering continues from Phase 115 → **starts at Phase 116**. Branch base clean: v1.21 is merged into `beta` in both sub-repos (each `beta` 1 merge commit ahead / 0 behind), so v1.22 forks off `beta`, reversing the v1.15/v1.21 exception. Topology caveat for planning: `0052c42` (v1.16 P89-01 dedup of these very tables) is an **abandoned commit**, ancestor of neither `beta` nor the v1.21 line — the duplicate tables are live. Explicitly out of scope: the `lock-status` command + hand-curated protection table (stays a seed) and AMD Autoselect / Winbond product-ID query sequences. Queued roadmap slots shift to v1.23–v1.28. Prior footer (v1.21 close) retained below.*

*Last updated: 2026-07-27 — v1.21 (Community Chip-Validation Command) MILESTONE COMPLETE + archived. 8 phases (108–115, incl. micro-phase 114.1), 34 plans, 70 tasks, 28/28 v1 requirements; close capstone Phase 115 verified 5/5. `3.0.0b11` published on BOTH community channels (PyPI `pip install --pre firestarter` + GitHub prerelease carrying per-board `.hex`); three bench boards validated fresh-machine install→flash→smoke (Uno + Leonardo HARD gates, uno328pb best-effort — all PASS); community onboarding doc `firestarter_app/doc/beta-testing-install.md` shipped; meta submodule gitlinks bumped off the long-standing PINNED-b10 hold → the b11 commits (fw `0fd7992` / app `86e4563`). Closeout `override_closeout` (14 pre-existing cross-milestone open items acknowledged-deferred; none originate in v1.21). Remaining operator-gated close step: `v1.21` git tag + sub-repo `--no-ff` beta merges + pushes. Prior footer (v1.21 Phase 114.1) retained below.*

*Last updated: 2026-07-10 — v1.21 Phase 114.1 (`dev test` Absent-Chip Hard-Fail — SAFE-04 micro-phase) COMPLETE + VERIFIED (3/3 must-haves) + UAT batch-passed (2/2 auto-covered). Host-only, no firmware change, fully bench-free; 1 plan, 1 wave. Delivered: a minimal guard in `dev_test` (`cli_handlers.py`, between the `--destructive` confirm and `derive_plan`) keyed STRICTLY on `app.db.get_eprom(chip)` emptiness — `dev test <absent-chip>` now exits 1 with bare `Error: <chip>: not found in database` (no fuzzy suggestion, no traceback) BEFORE `read_hardware_revision_value()`/`AutoCapture`/`run_plan`/report render; reuses the existing `ChipNotFoundError` → `@map_typed_errors` → `click.ClickException` path (no new exception type). Case B preserved by construction: the guard never consults `resolve_chip`, so an in-DB-but-unsupported chip (e.g. AT28C16 adapter-required) STILL runs the full sweep with refusals recorded as SKIPPED findings. Tests: `TestAbsentChipHardFail` (case A + case B) with the load-bearing `read_hardware_revision_value.assert_not_called()` (defeats the exit-code-only false-green trap — a pre-guard Mock-serialization crash also exits non-zero); verifier independently reproduced RED→GREEN by stripping/restoring the guard. Full suite green except the 3 documented pre-existing env-artifact failures; ruff clean; pre-existing `submit.py` mypy failure reproduced on the pre-phase commit (out of scope). SAFE-04 → Complete in REQUIREMENTS.md; todo `dev-test-hard-fail-unknown-chip` auto-closed. Submodule commits (branch `v1.21-community-chip-validation-command`): `d6359de` (guard) / `6ab06a7` (tests); meta gitlink NOT bumped (operator-gated, PINNED at b10). Milestone: 8/9 phases done (89%); remaining Phase 115 (Beta Install & Firmware-Flash Bench Validation — hardware-gated close capstone; its Step-0 beta-public check will hit the operator-gated 3.0.0b11 publish gate first). Prior footer (v1.21 Phase 114) retained below.*

*Last updated: 2026-07-03 — v1.21 Phase 114 (Disposition / No-Auto-Graduate Lock + Graduation Ladder + Inbox Reconciliation — feature close) COMPLETE + VERIFIED (3/3 must-haves). Host + tooling only, no firmware change, fully bench-free. 3 plans, 2 waves, all 3 requirement IDs (DISP-01, GRAD-01, INBOX-01) independently verified against the live codebase. Delivered: **GRAD-01** — report-side `ladder_state` derived on `DbDiff`/`build_db_diff`/`to_dict()` in `diagnostic_report.py` (`community-reported`/`community-fail` auto-derived from sweep verdicts; `community-confirmed` UNREACHABLE by construction — the human-gated target), report-side ONLY (never in `chip_database.json`, D-02), `SCHEMA_VERSION` 1.0→1.1, plus `doc/community-validation.md` documenting the 4-state taxonomy + the `dedup_fingerprint`-keyed N≥2 rule (distinct from Phase-108 per-run N≥2). **INBOX-01** — new stdlib `tools/parse_devtest_issue.py` (detects `[dev test]` title + fenced-JSON `schema_version`, surfaces the DB-diff, counts N≥2 agreeing via `dedup_fingerprint`; untrusted-input-safe — no eval/exec/shell, fail-soft; the installed `inbox.md` deliberately NOT edited per D-04); 19 unit tests. **DISP-01** — new AST audit `tools/check_no_community_support_status_write.py` (mirrors the SAFE-03 checker: `ast.NodeVisitor`, fail-closed empty-scan, PASS-names-files; sole `support_status` write locus stays `build_db.py:714`; no false-positive on `eprom_info.py` display-dict) + a 7-test anti-hollow suite (verifier independently planted a fresh violation and confirmed the gate catches it); pytest-wired, NOT a CI-YAML step. Full `firestarter_app` suite green except the 3 documented pre-existing env-artifact failures (audit-coverage golden + two live-board `no_programmer` characterization tests) — zero new regressions; ruff clean. **Scope reconciliation:** SAFE-04 (absent-chip hard-fail — traceability-mapped here but scoped out by CONTEXT.md as Phase-112-handler hardening) was extracted to a NEW micro-phase **114.1** (operator decision); REQUIREMENTS traceability remapped, coverage held at 29/29. Submodule commits (branch `v1.21-community-chip-validation-command`): `355981a`/`3cb68ab`/`e6e55bb` (114-01), `50b07c4`/`8b6962d` (114-02), `4e6a6d7`/`dcd2986` (114-03); meta `firestarter_app` gitlink NOT bumped (operator-gated, PINNED at b10). Milestone: 7/9 phases done (78%); remaining Phase 114.1 (SAFE-04) then Phase 115 (hardware-gated close capstone). NOTE: PROJECT.md footers for Phase 112 (`dev test` handler wiring) and Phase 113 (submission flow) were not recorded at their close — see `.planning/STATE.md` / MEMORY for those. Prior footer (v1.21 Phase 111) retained below.*

*Last updated: 2026-07-03 — v1.21 Phase 111 (Measured-Voltage Sampler — hardware-gated) COMPLETE + VERIFIED. Host-only, no firmware change; VOLT-01 satisfied and marked Complete in REQUIREMENTS.md. 3 plans (TDD RED scaffold → sampler impl → report field split), 4/7 milestone phases done (57%). Delivered: value-returning `HardwareManager.sample_vpp_mv()`/`sample_vpe_mv()` reconstruct median mV from `MSG_DATA_VPP/VPE_VOLTAGE` (0xE4/0xE5) frames via RESEARCH Pattern A (tolerant regex re-parse of `Response.message` — `Response.payload` is `None` for these frames, superseding CONTEXT D-05's raw-payload premise), returning honest `None` (never a fabricated `0`) on transport/parse failure; the pre-existing print-only monitor methods (`_read_voltage_loop`/`read_vpp_voltage`/`read_vpe_voltage`) are byte-unchanged (SC3, git-diff-verified — additive-only). `DiagnosticReport` gained the six-field voltage split (`vpp_before_mv`/`vpp_after_mv`/`vpe_before_mv`/`vpe_after_mv` destructive + `vpp_mv`/`vpe_mv` standalone), replacing the combined `vpp_vpe_mv` slot, surfaced through a single `_voltage_dict()` (NOT_MEASURED honest fallback, modeled on `_transport_dict`) and one single-source `render()` row from `to_dict()['voltage']`. 28/28 sampler+report tests green, ruff clean, zero anti-patterns. Verification was `human_needed` (SC1/SC3 automated-VERIFIED; SC2 hardware half deferred to bench per D-05). UAT this session: Test 1 (live VPP/VPE parity, Leonardo + Rev 2.0 on ACM0 = "Rev 2.0-class") PASS → VERIFICATION flipped to `passed`; Test 2 (before/after write-step capture) reclassified out of the blocking UAT set → deferred to Phase 112 (no write-step call site exists in Phase 111 by design; logged in `111/deferred-items.md` — NOT a Phase 111 gap). Meta gitlink NOT bumped (operator-gated, PINNED at b10). Next: Phase 112 (`dev test` Handler Wiring) — integrates 108–111 into the Click CLI and gives the sampler its first write-step call site. Prior footer (v1.21 Phase 110) retained below.*

*Last updated: 2026-07-02 — v1.21 Phase 110 (Diagnostic Report Model + Dual Output + Provenance Prompts) COMPLETE. Host-only, no firmware change, fully bench-free. 3 plans, 3 sequential waves (all touch the single new module `firestarter_app/firestarter/diagnostic_report.py`), all 5 requirement IDs (RPT-01/02/04/05, XPORT-01) verified 5/5 must-haves against the live codebase. Delivered: RPT-01 single-source dual-render — one `DiagnosticReport` `@dataclass` composing Phase-108 `Plan`/`StepResult`/`Fingerprint` + new sub-dataclasses (`AutoCapture`, `TransportHealth`, `Provenance`, `DbDiff`); a single `to_dict()` is the ONLY field source, feeding both `render()` (rich table) and `to_json_block()` (fenced JSON carrying a single-sourced `SCHEMA_VERSION` const) — a source-level `test_dual_render_single_source` guard asserts `render()` calls `self.to_dict()` and never `json.load(s)` (no parallel field list, no re-parse). RPT-02 auto-capture — `AutoCapture` carries host version (`firestarter.__version__`), a RECEIVED-not-fetched `fw_board_identity` (Pitfall 1: transient `version:board`, threaded in by Phase 112), chip-ID expected-vs-actual (Pitfall 2: asymmetric — DB-sourced expected + detected-on-mismatch), protocol path, per-op `error_code`/`fingerprint` off Phase-108 `StepResult`; AST-verified NO `SerialCommunicator`/`HardwareManager` import (SAFE-02). XPORT-01 honest fallback — `NOT_MEASURED="not measured"` sentinel (never a false `0`; research confirmed zero transport counters exist in `serial_comm.py` today, so it reads "not measured" everywhere), `transport_suspect` trips ONLY on present+elevated counters (never on absent), no new serial-layer instrumentation. RPT-04 provenance — `Provenance` + injectable-seam `prompt_provenance(ask, confirm)` (mock-testable, `rich.prompt` analog) + `is_submittable()` where "not sure" is a FILLED/submittable shield-rev answer and only a truly-blank field blocks; shield revision NEVER auto-derived from `hw_revision` (structural test); Phase 112 owns the invocation-before-sweep. RPT-05 read-only DB-diff — `DbDiff`/`build_db_diff()` reads current `support_status` (via `get_eprom`/`chip_resolver`) beside an ADVISORY disposition string from sweep verdicts (PASS-only→"candidate for community-reported"; any BAD→"community-fail signal"; marginal/indeterminate→"inconclusive — needs N≥2"); proven read-only BY CONSTRUCTION (write-method-less `Mock` DB + grep/AST scan for `support_status =`/`.write(`/`set_*(` → 0); taxonomy state-machine deferred to Phase 113/114. Cross-phase seams left as slots, not implemented: Phase-111 measured VPP/VPE mV (nullable field), Phase-112 prompt invocation + identity threading + CLI, Phase-113 JSON parsing via `schema_version`. 25 new phase tests green (module 97% cov); `ruff check`/`format --check` clean. One clean executor deviation (110-01: AST-based orchestrator-only scan replacing a substring check that self-matched the SAFE-02 docstring). Verifier initial `gaps_found` was a Plan-110-01 REQUIREMENTS.md bookkeeping omission (RPT-01/02/XPORT-01 checkboxes unflipped) — orchestrator flipped them + reconciled VERIFICATION.md to `passed` (5/5 code must-haves were always met). The single pre-existing `test_audit_coverage_matrix.py::test_golden_file_matches` golden drift confirmed unrelated/out-of-scope (Phase-106-01 carry-forward; no Phase-110 commit touches its tool/golden). Submodule commits (branch `v1.21-community-chip-validation-command`): `92d97c1`/`721cded`/`f2d3ce5` (110-01), `2e05918`/`fb49e02`/`3aa9752`/`ad197f3` (110-02), `90a65ad`/`0788ffc`/`21ff05e`/`8a38f13` (110-03); meta gitlink NOT bumped (operator-gated, PINNED at b10). Next: Phase 111 (measured-voltage sampler — hardware-gated). Prior footer (v1.21 Phase 109) retained below.*

*Last updated: 2026-07-02 — v1.21 Phase 109 (Destructiveness Gate + Safety) COMPLETE. Host-only, no firmware change, fully bench-free. 3 plans, 2 waves, all 5 requirement IDs (SAFE-01/02/03, SWEEP-05, PATT-03) verified 5/5 must-haves against the live codebase. Delivered: SAFE-01 structural gate — `derive_plan(destructive=False)` now STRIPS write/erase from the executable `Plan.steps` (Phase-108's annotate-only contract superseded), recording them only on a new advisory `Plan.locked_destructive` field that `run_plan` never iterates; `--destructive` sourced solely from the call/CLI arg (zero `os.environ`/config reads); the guard-bypass derivation split (`get_eprom`/`convert_to_programmer`, never `resolve_chip`) preserved. PATT-03 UV small-region cap — `_UV_WRITE_REGION_LENGTH=256` engine module constant, top-anchored `[mem_size-256, mem_size)`, UV detected in-engine via protocol `0x0B` (the execution-path dict lacks `electrical-type`; `0x0B` verified UV-exclusive across the DB), NEVER widenable by any DB field (`cap_not_widenable` test proves SC4). SWEEP-05 applicable-only N-of-M — `BannerCounts`/`count_applicable()` compute M (supported + `locked_destructive`) and N (ran verdicts, NA/SKIPPED excluded, ran-but-BAD counts as ran) from the single `Plan` object (no double derivation); banner DATA only, no print/render (rendering → Phase 110/112). SAFE-02 — explicit tests assert every executed op routes through `resolve_chip`, sets no VPP / builds no raw wire-dict / passes no `--force`, and a VPP-guard refusal is captured as a `BAD` finding (exact call-count proves no retry-around). SAFE-03 anti-hollow — `tools/check_devtest_orchestrator.py` is a genuinely-populated fresh `ast.parse`/`NodeVisitor` walk (only `check_dispatch.py`'s tool shape copied) that exits 0 on the real clean source and denies VPP-set / raw-wire-dict / `--force`; paired `tests/test_check_devtest_orchestrator.py` (6 tests) subprocess-invokes it against on-disk planted-violation fixtures via a `FIRESTARTER_DEVTEST_SRC` override, asserting non-zero exit on each — directly closing v1.12's hollow-GATE-03 tech debt. 796 tests pass (+31 phase tests over the 765 baseline); `ruff check` + `ruff format --check` clean on all 4 files; the single pre-existing `test_audit_coverage_matrix.py::test_golden_file_matches` coverage-matrix golden drift confirmed unrelated/out-of-scope (NOT a Phase-109 regression; predates the phase — worth a standalone golden-fixture regen later). Submodule commits `b2bdfae`/`c569b12` (109-01), `5f74b83`/`7246720` (109-02), `29f0057` (109-03) on branch `v1.21-community-chip-validation-command`; meta gitlink NOT bumped (operator-gated). Next: Phase 110 (diagnostic report model + dual output + provenance prompts). Prior footer (v1.21 Phase 108) retained below.*

*Last updated: 2026-07-02 — v1.21 Phase 108 (Test-Plan Engine + Address-Derived Pattern + Fingerprint) COMPLETE. First v1.21 phase: the bench-free `chip_test.py` engine landed in `firestarter_app` (branch `v1.21-community-chip-validation-command`, forked off `v1.20-protocol-only-dispatch` @ 0e9137f — v1.20 not yet on `beta`, operator-confirmed at execute). 4 plans, 3 waves, all 7 requirement IDs (SWEEP-01/02/03/04, PATT-01/02, RPT-03) verified 6/6 must-haves against the live chip DB. Delivered: `EpromOperationError.error_code` seam (RPT-03, backward-compatible kwarg + `_raise_for_error_response` pass-through); `derive_plan()` guard-bypassing per-chip op derivation via `get_eprom`/`convert_to_programmer` (SWEEP-01, never re-invokes `classify()`, never calls `resolve_chip`); `run_plan()` non-fatal per-step executor with `OK`/`BAD`/`NA`/`SKIPPED`/`marginal` verdicts (SWEEP-02, W29C040 locked-boot-block lesson), id-first chip-ID-mismatch destructive gate (SWEEP-03, chip left pristine), N≥2 marginal policy mirroring `consistency_check_eprom` (SWEEP-04); address-derived XOR-fold pattern + all-0x00/0xFF pre-pass + 4-bucket fingerprint classifier with honest `indeterminate` (PATT-01/02, reuses the shared divergence math). 55 phase tests green; ruff/mypy clean; one pre-existing out-of-scope `test_audit_coverage_matrix.py::test_golden_file_matches` meta-ledger drift (Phase 106-01) confirmed unrelated. Submodule commits `a257ab7`/`09e8a64`/`6216834` (108-01), `20fe3e2`/`6acf424`/`b3b3bb3` (108-02), `0ea2ce0`/`1205280` (108-03), `aad849e`/`eea7c48`/`abdfad3` (108-04); meta gitlink NOT bumped (operator-gated). Next: Phase 109 (destructiveness gate + safety). Prior footer (v1.21 start) retained below.*

*Last updated: 2026-07-02 — v1.21 (Community Chip-Validation Command) STARTED via `/gsd-new-milestone`. Ship a `firestarter dev test <chip>` command that lets a community member run a full technology-aware capability sweep on a chip the maintainer doesn't own and file an actionable diagnostic report back — turning chip coverage from "what's on Henrik's bench" into "what's on everyone's bench." Per-chip test-plan engine derives supported ops from `classify()` and runs id/read/write/verify/erase/blank-check as independent non-fatal steps (locked boot block = finding, not abort); technology-aware destructiveness (non-destructive default = id/read/blank-check, loud `--destructive` gate, UV small-region write); dual-output diagnostic report (human results table + fenced JSON in one self-contained issue body) with a two-tier field contract (auto-capture FW/board/host version + chip-ID expected-vs-actual + protocol path + error codes + byte-mismatch fingerprint + measured VPP/VPE + transport health + DB entry; prompt for shield rev + chip provenance + pot adjustments); tiered `--submit` (`gh issue create` auto-labeled → gsd-inbox if present, else prefilled browser URL; gist/attachment only for verbose failure logs). Promoted from the `/gsd-explore` 2026-07-02 seed `community-chip-validation-command.md`. Two open research questions (health-proving write pattern fixed-vs-address-derived; community-PASS → `support_status` graduation) in `.planning/research/questions.md`. Phase numbering continues at Phase 108; forks off `beta` per policy with a v1.20-not-yet-on-beta sequencing flag to resolve at execute time (gitlinks PINNED at b10). Prior footer (v1.20 close) retained below.*

*Last updated: 2026-07-02 — v1.20 (Protocol-Only Dispatch — Remove the Legacy `mem_type` Axis) MILESTONE CLOSED via `/gsd-complete-milestone`. 3 phases (105 FW / 106 HOST / 107 DOCS+GATE), 7 plans, 12/12 v1 requirements; closeout `override_closeout` (14 pre-existing cross-milestone open items acknowledged-deferred, none v1.20-origin). ROADMAP + REQUIREMENTS archived to `.planning/milestones/v1.20-*`; MILESTONES.md §v1.20 written; STATE.md Deferred-Items table recorded. Meta tagged `v1.20` + `gsd/v1.20-protocol-only-dispatch-remove-the-legacy-mem-type-axis` merged to `beta`, both pushed to origin (operator-authorized). Sub-repo (firmware/host) beta cut `3.0.0b11` + gitlink bump remain OPERATOR-GATED; gitlinks PINNED at b10 (fw `2d93379` / app `e0bdea4`). LEGACY-01/02 deferred to v2. Prior footer (v1.20 phase-107 close) retained below.*

*Previously: 2026-07-02 — v1.20 (Protocol-Only Dispatch — Remove the Legacy `mem_type` Axis) ALL PHASES COMPLETE. Phase 107 (DOCS + GATE — Documentation & Non-Regression Close) closed the milestone's work: scrubbed the deleted `mem_type`/`type` axis from `firestarter_fw/CLAUDE.md` (dispatch narrative rewritten to the shipped `protocol == 0` → `configure_not_implemented()`/0xBB fail-closed reality; steps 7–11 + legacy `type` wire bullet deleted) and the stale `"type": 1` example in `firestarter_app/CLAUDE.md`; added `## Breaking Changes (v1.20)` to both sub-repo READMEs (wire `type` removed, every chip entry now needs `algorithm`, pre-v1.20 hosts emitting a stray `type` stay safe via unknown-field skip); `electrical.type` STRING semantics + PROTOCOLS.md infoic tuples PRESERVED (DOC-01). Reconciled the retired `MSG_ERR_MEM_TYPE_UNSUPPORTED (0xAE)` out of the canonical `messages.toml` (meta + both vendored) and regenerated `messages.py`/`messages.h` via `codegen.py` (byte-empty regen diffs; codegen drift gate clean) — incidentally restored two Phase-95 messages (0x85/0xBC) that were missing from the canonical toml, a net-zero-regression source-of-truth correctness fix (D-06). Non-regression gates re-verified green at close (independently re-run by the verifier, not trusted from SUMMARY): `pio test -e native` 80/80, dispatch-mirror 2/2, `check_dispatch.py` 0 violations/746 chips, `diff_db.py` 0 unexplained real-chip deltas (GATE-01); host pytest 710 pass / 1 pre-existing failure + pre-existing ruff/format dirt all confirmed OUTSIDE `git diff beta..HEAD` (GATE-02 = no NEW regression vs beta, D-07), mypy 2.1.0 confirmed installed + clean; over-voltage stays blocked + protocol-only handler routing re-confirmed via existing tests, no new tests added (SAFE-01). Golden fixtures / frame vectors / dispatch-mirror model untouched (D-05). Verifier passed 9/9 must-haves. Sub-repo commits on the milestone branch; gitlinks left PINNED. Milestone close-out (meta tag v1.20 + dual-repo beta merge + lockstep beta cut + gitlink bumps) remains OPERATOR-GATED per standing policy. Prior footer (v1.20 STARTED) retained below.*

*Last updated: 2026-07-02 — v1.20 (Protocol-Only Dispatch — Remove the Legacy `mem_type` Axis) STARTED. Delete the vestigial `mem_type`/`type` backward-compat dispatch axis so Firestarter trusts ONLY the real protocol (`handle->protocol` / `algorithm`) end to end. Firmware: remove the `memory.cpp` `mem_type` fallback chain (steps 7–11) so `protocol == 0` fail-closes; drop the `handle->mem_type` struct field, stop parsing the `type` JSON field, retire `MSG_ERR_MEM_TYPE_UNSUPPORTED (0xAE)`. Wire: remove the `type` field from the JSON command contract entirely (breaking for hand-crafted JSON / pre-v1.20 hosts). Host: stop emitting `type`; remove `_ALGO_MEM_TYPE` + the "Generic Flash (legacy fallback only)" default in `database.py` + the `mem_type`-keyed legacy label fallbacks in `ic_layout.py`; every chip entry must carry an `algorithm`. The fallback is already dead code for every DB chip (all carry `algorithm`) — legibility/safety cleanup, not a behavior change for real chips; accepted consequence: user-override entries lacking `algorithm` no longer work. Guards held green (v1.16 golden traces + dispatch-mirror + `check_dispatch.py`/`diff_db.py`); over-voltage stays blocked; NOT in scope: canonical `electrical.type` string, phantom 0x35/0x39, named-infeasibility 0x11/0x2A–0x2C. Firmware-touching → dual-repo lockstep off `beta`; gitlinks PINNED; lockstep beta cut operator-gated. Phase numbering continues at Phase 105. Prior footer (v1.19 Phase 104 close) retained below.*

---

*Last updated: 2026-07-02 — v1.19 Phase 104 (Rename protocol header/.cpp files to descriptive protocol-type names) COMPLETE. Post-close follow-on to the four v1.19 phases: renamed the two remaining minipro-heritage flash handler file-pairs + entry functions in dual-repo lockstep — `flash_type_3.{h,cpp}` → `flash_nor_unlock.{h,cpp}` / `configure_flash3` → `configure_flash_nor_unlock` (0x06), `flash_type_4.{h,cpp}` → `flash_5v_page.{h,cpp}` / `configure_flash4` → `configure_flash_5v_page` (0x05 + phantom); fixed two long-mismatched header guards; updated all 4 `memory.cpp` dispatch call sites + `flash_utils` comments (RENAME-01/02, Wave 1). Brought host GATE-01 dispatch-mirror tooling into lockstep — `check_dispatch.py`, `validation_matrix_spec.json`, regenerated firmware-shared `validation_matrix.h`, host doc tables (RENAME-03, Wave 2). Renamed native validation suites `test_val_flash3/4` → `test_val_nor_unlock`/`test_val_5v_page` (dirs + family-ids + fn stems), updated the dispatch test, `platformio.ini`, `PROTOCOLS.md` §0/§1/§3 (incl. SAFE-02 INV suite-path contract), `firestarter_fw/CLAUDE.md`, and closed the doc↔tool↔firmware dispatch-mirror bind (`test_dispatch_mirror.py`) (RENAME-04/05, Wave 3). `git mv` preserved rename history. Full phase gate green: `pio test -e native` 82/82, `pio run -e uno`/`-e leonardo` both SUCCESS (Leonardo byte-identical 25654 B / 89.5% — pure rename, zero flash delta), host `pytest` 14/14, `diff_db.py` GATE-02 identity (only pre-existing Phase-94 delta), `cli_handlers.py` never touched (GATE-03). Verifier passed 9/9 must-haves against the live codebase. Legibility layer only — protocol integers / `#define`s / dispatch key / `chip_database.json` all byte-unchanged (GATE-01/02/03 intact). Commits: `firestarter` (99c6f7d/63e130e/e636af7/b2be890/72fce0a/96b3138), `firestarter_app` (ad223c0/1d39d8c/a8d60b2/f4f265f), branch `v1.19-protocol-naming-labels`; gitlinks left PINNED (bump operator-gated). Non-blocking backlog item disclosed: `cli_handlers.py`'s `dev validate-family` Click Choice still lists retired `flash3`/`flash4` ids (left alone per GATE-03). Prior footer (v1.19 CLOSED) retained below.*

---

*Last updated: 2026-07-01 — v1.19 (Protocol Naming Labels) COMPLETE — milestone CLOSED. All 4 phases (100 NAME set + operator approval · 101 FW `PROTO_` tokens + handler renames · 102 HOST canonical `_PROTOCOL_DISPLAY_NAME` map · 103 DOCS) landed. Phase 103 reconciled `firestarter_fw/doc/PROTOCOLS.md`: 12 §1.x bucket headings renamed to `PROTO_` token form with the 8 §3 cross-link anchors regenerated in lockstep (DOC-01), 9 INV-01..09 matrix rows augmented with tokens beside their raw hex (SAFE-02 grep-contract columns byte-identical), 2 minipro-jargon prose sentences rephrased, and a "Name ↔ Slug Divergence" callout added recording that `datasheets/<hex>-<NAME>/` slugs stay FROZEN (NAME-F1 deferred) plus the Phase-102 ASCII-hyphen vs em-dash host divergence (DOC-02). GATE-01/02/03 re-verified green at close — dispatch-mirror guard (2/2), `pio test -e native` (82/82, ran for real), `diff_db.py` identity, constants-parity (6/6 under py3.12; py3.11-target leg CI-PENDING, honest), CLI grammar unchanged. Verifier passed 10/10 must-haves. Doc commits inside `firestarter_fw/` (14491e9/6395a7e/2d93379, branch `v1.19-protocol-naming-labels`). Legibility layer only — numeric algorithm-first dispatch UNCHANGED throughout. Meta tag + dual-repo beta merge + lockstep beta cut + gitlink bumps remain operator-gated per standing policy (gitlinks still PINNED at b10). Known stale bookkeeping (out of Phase-103 scope): REQUIREMENTS.md NAME-01/02/03 (Phase 100-owned) still show Pending. Next: operator-gated milestone close-out (tag/merge/beta). Prior footer (v1.19 Phase 102) retained below.*

*Last updated: 2026-07-01 — v1.19 Phase 102 (HOST — Apply Names in the Host CLI Display) COMPLETE. The two divergent host protocol vocabularies (`ic_layout.proto_display` + `protocol_info_data`) are consolidated onto a single canonical `_PROTOCOL_DISPLAY_NAME` map (12 ASCII-normalized names per PROTOCOLS.md col-2; D-01/D-02), so `firestarter info` renders one consistent name per protocol; coverage reconciled (0x34 added, 0x11 dropped, 0x35/0x39 phantoms excluded; D-04); name-only — description bullets untouched (D-03). Display-only: GATE-03 (CLI grammar unchanged), GATE-01 (dispatch mirror), GATE-02 (chip_database.json identity) all re-verified green; blast radius = the `info` `Protocol:` line + one regenerated snapshot. Verifier passed 5/5 must-haves. Host commits inside `firestarter_app/` (ffc711d/dab8cfd/430cbb6, branch `v1.19-protocol-naming-labels`); gitlink not yet bumped in meta (milestone-close/beta-cut gated). One pre-existing unrelated failure (`test_golden_file_matches`) confirmed at parent commit, deferred. v1.19 progress: Phases 100–102 done; Phase 103 (DOCS) remaining. Prior footer (v1.19 start) retained below.*

*Last updated: 2026-07-01 — v1.19 (Protocol Naming Labels) STARTED. Replace Firestarter's inherited-from-minipro hex-ID protocol jargon with a single canonical, behavior/datasheet-correct, human-readable name set, and apply it consistently across firmware constants, host display, and docs — a legibility layer on top of the UNCHANGED algorithm-first numeric dispatch (numbers stay the dispatch key; GATE-01/02/03 non-regression). Phase 100 (NAME) authors + operator-approves the canonical 3-field name set (C-token `PROTO_<NAME>` + short display name + datasheet-cited facet prose) for every protocol in `chip_database.json` (0x05/0x06/0x07/0x08/0x0B/0x0D/0x0E/0x10/0x27/0x28/0x29/0x34 + phantom 0x35/0x39), recorded authoritatively in `firestarter_fw/doc/PROTOCOLS.md` (revised in place; frozen `datasheets/` slug column retained as the DOC-02 divergence record) — a blocking approval gate that gates everything downstream. Phase 101 (FW) defines the `PROTO_<NAME>` constants + relabels the raw-hex dispatch chain + renames handler files/functions (`configure_flash3`/`flash_type_4.cpp`/`eeprom28c`…) from the operator-approved family-name layer; Phase 102 (HOST) consolidates the divergent host display maps (`proto_display`, `protocol_info_data`) onto the canonical display names; Phase 103 (DOCS) reconciles doc prose + the INV-01..09 matrix. `datasheets/` slugs stay frozen (NAME-F1 deferred); many-to-one dispatch preserved (not split); CLI grammar unchanged — no name-as-input (NAME-F2 deferred). Firmware-touching (Phase 101) → dual-repo lockstep for the constants; gitlinks PINNED, lockstep beta cut operator-gated. Phase numbering continues at Phase 100 (Phase 100 context + discussion log already gathered on `gsd/v1.19-protocol-naming-labels` — preserved). Prior footer (v1.18 close) retained below.*

*Last updated: 2026-07-01 — v1.18 (AM27C020 0x08 Write-Path RCA & Fix) SHIPPED. 3 phases (97–99), 12 plans, 11/11 requirements; firmware-touching, dual-repo lockstep. RCA named RC-1 (DIP32 pin 31 modeled as address line A18, not held /PGM; the passing 0x07 W27C512 differential exonerated every shared axis); fix = a scoped `DIP32_27C020` pinout + `rw-pin:[31]` → `CTRL_READ_WRITE` (0x40, revision-invariant, distinct from the 0x08 VPP alias that made the first attempt CR-01 a physical no-op), size-gated ≤256K, dual-repo lockstep `MAX_27C020_SIZE`, 119/119 native tests, golden traces byte-identical. Bench proved the fix effective (write#1 60/64 byte-exact, refuting the Phase-97 0-bits signature) but marginal/unreliable (write#2 0/64) → honest DEFER; AM27C020 carried as FUT-08 (FUT-06 retired-by-replacement). Audit `tech_debt` (3/3 phases passed, integration 6/6 WIRED, 0 broken flows, 14 pre-existing cross-milestone items acknowledged-deferred). Meta tagged `v1.18` + gsd planning merged to `beta`; lockstep beta cut + gitlink bump operator-gated. Next: `/gsd-new-milestone`. Prior footer (v1.17 start) retained below.*

*Last updated: 2026-06-26 — v1.17 (Implement & Test the W29C040 Programming Protocol) STARTED. Root-cause and fix the W29C040 flash4 (`0x05`) page-write defect on real silicon (page-0 fault; page size already correct at 256 B, so deeper than CR-01's capacity heuristic — differential against the passing `0x05` sibling W29C020, candidates SDP unlock / page-write polling/timing / A18 512 KB addressing), generalize flash4 page sizing to a datasheet-sourced per-chip `page_size` DB field (replacing `flash4_page_size(mem_size)`; under-sized 64 KB/256 KB families corrected too), and bench-prove a byte-exact write→auto-erase→program→verify SHA on the seated W29C040 (Leonardo + RURP Rev 2.0) — the hard graduation gate. Firmware-touching, dual-repo lockstep; forks off the v1.16 firmware tip `a296195` (NOT beta, stale at v1.13 `a1953c2`); gitlinks PINNED at b10; lockstep beta cut operator-gated. Closes CR-01 / Phase-74 Wave-2. Phase numbering continues at Phase 93. Prior footer (v1.16 close) retained below.*

*Last updated: 2026-06-26 — v1.16 (Protocol-First Architecture Rebuild) SHIPPED. 8 phases (85–92), 29 plans, 28/28 requirements; host-first, NO dual-repo lockstep. Decoded `infoic.xml`'s `variant` field in full + rewrote `build_db.py` to a single principled `classify()` (Rule 1/2/3 override stack deleted; FM1608→SRAM_STD/0x28 + X88C64→EEPROM structural; DB 744→746 with the 2516/2532 non-upstream supplement, baselines re-pinned, diff_db IDENTITY); added top-level `datasheets/` + `firestarter_fw/doc/PROTOCOLS.md` 12-bucket vocabulary + INV-01..09 native-test matrix; extracted primitives P7/P4/P3/P5 behind golden traces + a dispatch-mirror guard with a net flash **decrease** (25136 B / 87.7% / −518 B); authored `PROTOCOL-LEDGER.{md,json}` + `check_ledger.py` (all 4 on-hand protocols PASS on Leonardo + Rev 2.0, 6 no-silicon buckets explicit UNVERIFIED). The Phase-90/91 "12V-VPP write-path regression" was RCA'd as a `write -b` skipped-erase test-method error (recompose proven innocent via b10 A/B), then Phase 92 (HARD-01) decoupled `-b`/`--no-blank-check` from skip-erase in the host + added an explicit `--skip-erase` opt-in. fw `a296195` / app `883c78f` on `v1.16-protocol-first-architecture-rebuild`; meta tagged `v1.16`, gsd planning to be merged to `beta`; lockstep beta cut `3.0.0b11` + gitlink bump operator-gated (gitlinks PINNED at b10). 14 open artifact items acknowledged at close (12 pre-existing carry-forwards + 2 v1.16-born Phase-85 operator-confirmation gates). Next: `/gsd-new-milestone`. Prior footer (v1.16 start) retained below.*

*Last updated: 2026-06-25 — v1.16 (Protocol-First Architecture Rebuild) STARTED. Re-organize how Firestarter models/names/validates EPROM/Flash/SRAM programming protocols: rename + datasheet-document today's inherited minipro hex-ID buckets (0x05/0x06/0x07/0x08/0x0B/0x40/0x34/…) into a named protocol vocabulary, THEN re-decompose handlers into shared primitives (address setup, data strobe, poll/verify, VPP gate, page buffer, SDP unlock, chip-id) to shrink the ~89.5% Leonardo flash ceiling, with a per-protocol bench ledger (PASS on Leonardo + RURP Rev 2.0 / explicit `UNVERIFIED`). Minipro DB stays ground truth; datasheets only verify + document the *why*. Staged: datasheets/ acquisition → naming/docs → primitive refactor → per-protocol bench validation. Dual-repo lockstep (`constants.py` ↔ `firestarter.h`); reuse-first; py3.12-masks-CI-3.11 trap watch. Phase numbering continues at Phase 85; promoted from the `/gsd-explore` 2026-06-25 seed per operator instruction. Prior footer (v1.15 close) retained below.*

*Last updated: 2026-06-25 — v1.15 (Bench Validation of Operator Inventory) SHIPPED. 4 phases (81–84), 15 plans; 23 reqs (21 satisfied · GRAD-03 deferred best-effort D-22 · FIX-01 closed-by-disposition D-43). Bench-validated 11 physical chips across 5 algorithm families on Leonardo + RURP Rev 2.0 via full write→read→verify, with a per-chip `EVIDENCE.{md,json}` record + consolidated `DECODE-AUDIT.md`. First Flash/EEPROM auto-erase silicon proof (W29C020); 2516 graduated via a datasheet-grounded user-override entry. In-posture FIX-01 fixes shipped (firmware VPP-skip on read/blank-check + host SRAM/FRAM blank-check short-circuit + FM1608 SRAM→FRAM relabel); deeper write-path defects RCA'd + named-tracked (AM27C020 0x08 → FUT-06; W29C040 flash4 → CR-01/Phase-74 Wave-2; 2516 0x0B read → FUT-03). Genuine silicon FAILs (W27E512/W27E040 stuck bits) recorded honestly, not DB/algo faults. Milestone audit `gaps_found` stale (pre-Phase-84); both gaps closed-by-disposition + operator-accepted. One firmware delta (VPP-skip, fw `cb947c7`); host `4d5b3de`. Meta tagged `v1.15`, gsd planning merged to `beta`; lockstep beta cut `3.0.0b11` + gitlink bump operator-gated (gitlinks PINNED). 12 open artifact items acknowledged at close (pre-existing carry-forwards + intentional v1.15 deferrals). Next: `/gsd-new-milestone` (v1.16 protocol-first architecture rebuild seed captured). Prior footer (v1.15 start) retained below.*

*Last updated: 2026-06-23 — v1.15 (Bench Validation of Operator Inventory) STARTED. Bench-validate 11 physical chips (5 algorithm families) on Leonardo + RURP Rev 2.0 via full write→read→verify: prove the on-paper `supported` claim on real silicon, RCA/fix any failures, validate DB decode correctness, and graduate the one genuine gap (the `2516`, confirmed absent from minipro `infoic.xml` — needs a datasheet-grounded entry + bench proof, doubling as deferred FUT-03 NMOS evidence). UV-EPROMs (M27C512/AM27C020/2516) get a no-eraser protocol: non-destructive read+blank-check first, spend-vs-preserve decided per-chip at the bench. Mostly host-side; firmware untouched unless a bench defect forces a lockstep fix. Phase numbering continues at Phase 81; branch off `beta`. Prior footer (v1.14 close) retained below.*

*Last updated: 2026-06-23 — v1.14 (Feasible-Gap Implementation) SHIPPED. 4 phases (77–80), 9 executed plans of 13 (4 deferred hardware-gated), host-only delta (firmware untouched on `beta`). The first milestone since v1.0 to graduate chips to `supported`: erase write-path (Phase 77 ✅ bench-proven W27C512, first hardware graduation) + 25V NMOS best-effort (Phase 79 ✅ 4 chips, D-07 override, no HW change). X88C64 (Phase 78, ALE PCB-BLOCKED → FUT-01) + AT28C04/16 adapter (Phase 80, adapter-not-built → FUT-04) cleanly deferred. 15 reqs: 6 verified · 2 software-complete · 7 hardware-gated deferrals (FUT-01/03/04). Audit `gaps_found` but all gaps intentional/operator-authorized; integration PASS (744-chip gate 0 violations, 650 tests, parity 8/8). Meta tagged `v1.14`, gsd planning merged to `beta`; lockstep beta cut `3.0.0b11` + gitlink bump operator-gated (gitlinks PINNED). Next: `/gsd-new-milestone`. Prior footer (v1.14 start) retained below.*

*Last updated: 2026-06-18 — v1.14 (Feasible-Gap Implementation) STARTED. Graduate chips to `supported` by implementing the four evidence-surfaced RURP-feasible gaps v1.13 scoped out (validation-only): 999.4 erase write-path (skipped Phase 75 / ERASE-01), 999.5 X88C64 0x34 handler, 999.7 25V NMOS ceiling raise, 999.6 AT28C04/16 adapter graduation. Suggested order 999.4 → 999.5 → 999.7 → 999.6 (hardware-blocked last). First chips newly programmable since v1.0. Firmware-touching, dual-repo lockstep off `beta`; flash-budget ordering applies. Phase numbering continues at Phase 77. Operator decision 2026-06-18: do all four; 25V NMOS assuming HW can produce 25V. Prior footer (v1.13 close) retained below.*

*Last updated: 2026-06-18 — v1.13 (Programming Algorithm Validation + Gap Implementation) SHIPPED. 5 delivering phases (71–74, 76), 19 plans, 17/17 requirements; first firmware-touching milestone since v1.12. Software-first three-tier validation harness + per-family matrix proving the 6 write/program families (PARTIAL bench coverage, Leonardo Tier-3); evidence-driven feasible-gap subset (flash4 chip-id + W29C040 SDP/page-write; spec-only AT28C04/16 adapter arm + DIP24→DIP32 spec; X88C64 0x34 MEDIUM verdict, no handler). No chip graduated to `supported`. Dual-repo lockstep merged to `beta` (fw `a33513f` / app `34deccb` @ `3.0.0b9`, no tag); beta cut + stable promotion operator-gated. Phase 75 (erase) + Phase 74 Wave-2 (HW re-bench) deferred to v1.14 (Backlog 999.4–999.7). 9 deferred items acknowledged at close (pre-existing/accepted tech debt). Next: `/gsd-new-milestone v1.14`. Prior footer (v1.13 start) retained below.*

*Last updated: 2026-06-16 — v1.13 (Programming Algorithm Validation + Gap Implementation) STARTED. Test-first validation of the 6 implemented write/program algorithm families on hardware (harness + matrix software-first, hybrid bench gating, Leonardo as verify board), re-research the protocol landscape, then implement evidence-driven gaps (per-family correctness fixes + adapter-required chips). First firmware-touching milestone since v1.12; dual-repo lockstep off `beta`. v1.9 read-bug RCA stays separate. Phase numbering continues at Phase 71. Prior footer (v1.12 close) retained below.*

*Last updated: 2026-06-16 — v1.12 (Firmware Protocol Dispatch Hardening + Skeletons) SHIPPED. 8 delivering phases (62, 63, 64, 65, 66, 67.1, 69, 70), 22 plans, 17/17 requirements; first firmware-touching milestone since v1.10. Fail-closed dispatch (0xBB) + host `ProtocolNotImplementedError` + capability-honest DB (`support_status` taxonomy, in-host refusal); no new chip programmable; DB 743 → 744. Dual-repo lockstep merged to `beta` (fw `b71c6fd` / app `6b5480f`, no tag); lockstep beta cut + stable promotion operator-gated. Accepted tech debt: hollow GATE-03 detector (host guard authoritative) + Nyquist gaps on 6/8 phases. Next: `/gsd-new-milestone` (or resume the deferred v1.9 read-bug RCA at Phase 45). Prior footer (v1.12 start) retained below.*

*Last updated: 2026-08-24 after the **v1.33** milestone (Source Hygiene & Firmware Size Reduction) CLOSED and archived. Shipped 6 phases (154–159), 45 plans, **42/43 requirements Complete** — SWEEP-13 deliberately unticked, its one-meta-commit clause measurably not met at 9 and a false tick judged worse than an open box. Closeout type `override_closeout`, for that plus **10** inherited `audit-open` carry-forwards, none of them from this milestone's own work. **Zero product-code behaviour changed** — byte-level equivalence was the milestone's entire premise and the algorithm-first dispatch contract was not touched. The firmware is now **heap-free** and free of the 64-bit runtime; the duplicated report blocks and `json_parser.c`'s double-match are gone; **Leonardo Caterina headroom 502 B → 3440 B (6.9×)**, which mattered because v1.32 Phase 151 left that target at zero MERGE-05 headroom. Firmware size WARM 26026/26074/28170 → COLD 22952/23000/25098 B flash and 1575/1581/2016 → 1434/1440/1875 B RAM on `uno`/`uno328pb`/`leonardo` — **the labels differ because Phase 158 deliberately re-recorded the baseline cold, so that is not a like-for-like pair**; it reconciles to the survey's −2938 B plus Phase 158's −138/−138/−136 B to within 2 B on `leonardo`, and the 2 B is stated rather than smoothed. Phase 159 applied the citation remap **exactly once**: 2,706 citations across 562 documents out of 14,391 records / 1,291 documents, proven a byte-stable dry-run fixed point, with `CITATIONS-STALE.md` removed last. **Honesty caveat carried, not buried:** 269 of the 515 resolved exception records rest on diff provenance, not verbatim source-text equality, each flagged `verbatim_oracle_applied: false` — ROADMAP criterion 2 is not universally satisfied. Three corrections applied at close: the stale `firestarter_app` sha in SWEEP-13 (`bc9d592` → `38f0d83`, substance re-verified unaffected), eight Phase-159 artifacts that were executing uncommitted, and the `firestarter` gitlink stale at `2ad5b322` → re-pinned to `2ccda8d4`. Meta tagged `v1.33`. **LOCAL CLOSE ONLY — nothing pushed, no PR, no merge, no beta cut, no release**; all three repos remain on `gsd/v1.33-source-hygiene-firmware-size-reduction` and every outward-facing step stays operator-gated. No bench phase existed and no silicon was tested. `.planning/REQUIREMENTS.md` removed via `git rm` — recreate with `/gsd-new-milestone`. Prior footer retained below.*

*Last updated: 2026-08-21 after the **v1.32** milestone (AT28C Write-Path Root Cause & Report
Provenance) close. Shipped **6 executed phases** (147–149, 151–153; **Phase 150 deferred** to Backlog
999.28), 72 plans, 183 tasks, **35/35 in-scope v1 requirements** (42 defined). Three firmware-touching
workstreams in dual-repo lockstep: the page-size seam (149), the protection read (151), the write-path
erase policy (153). Closeout `override_closeout` — Phase 150's deferral plus the same **9** pre-existing
`audit-open` carry-forwards acknowledged at v1.31, none of whose UAT/verification entries originate here;
**ninth** consecutive acknowledgement. Closed by pushing the meta tail directly onto `beta`; **both
sub-repos were already fully merged there during Phase 152 (PR #53 each) and were deliberately NOT
re-merged** — `git cherry origin/beta HEAD` empty in both. Meta tagged `v1.32`; gitlinks re-pinned to
`88d204a5` (fw) / `86f85d77` (app). Pre-releases cut during Phase 152: app **3.0.0b23**, firmware
**3.0.0b20**. **No stable release — operator-gated.** **Evidence ceiling unchanged from open to close:
no AT28C part has ever been in operator inventory, `0x0D` stays `UNVERIFIED`, zero `support_status`
changes, no bench phase existed by design, and gh#21/#11/#12 are all still OPEN** — a code fix is not a
validation. Backlog **999.29** open and explicitly NOT retired; Backlog **999.28** deferred a second
time. **Next milestone: not yet chosen — start with `/gsd-new-milestone`.** Two things it should weigh
first: `.planning/research/`'s ten documents pre-date v1.32 (v1.11–v1.23 era) and will otherwise be read
as current by the next milestone's researchers; and **`leonardo`'s Caterina USB-bootloader cliff at
28672 B has 1042 B left and is UNGUARDED** — `board_upload.maximum_size` does not enforce it, so nothing
in the build stops a future change from silently overwriting the bootloader region. Prior footer retained
below.*

*Previously: 2026-07-30 after the v1.22 milestone (AT28C Software Data Protection Lifecycle) close. Shipped 7 phases (116–122), 69 plans, 176 tasks, 41/41 v1 requirements — firmware-touching, dual-repo lockstep, **software-only validation** at a stated and mechanically-enforced ceiling: `0x0D` stays `UNVERIFIED`, zero `support_status` changes, and a committed regex gate (`check_permitted_claims.py`) forbids the claim "SDP works on real AT28C silicon" across all five closing artifacts. Closeout `override_closeout` (14 pre-existing cross-milestone items acknowledged-deferred; none originate in v1.22). Cut `3.0.0b14` public on both channels; meta + both sub-repos tagged `v1.22` and pushed; gitlinks bumped off PINNED-at-b11. No stable release — operator-gated. **Next milestone: v1.29 PY32F071 USB Firmware Install (host-side)** — implementation already exists and is green on `firestarter_app` branch `feature/py32f071-fw-install` @ `311eacf`, so it is a land-and-verify milestone; the hard blocker is cross-repo release-asset naming (the firmware's PY32 CI publishes an Actions artifact `firestarter-py32f071.hex` where the host resolves a release asset `firestarter_py32f071.bin`/`.hex`). Start with `/gsd-new-milestone`. **⚠ SUPERSEDED (2026-08-02 — Phase 130 close):** the next-milestone claim above is superseded — v1.23 became **PY32F071 Integration** (Phases 123–130), and the two py32 slots this footer names (`v1.28 PY32F071 Port`, `v1.29 PY32F071 USB Firmware Install`) were retired into it by CLOSE-03. The branch head `311eacf` is superseded by **`4ee64a1`** (R-11) — the SHA that actually landed in Phase 127. The cross-repo release-asset-naming blocker this footer describes is **closed**: REL-02 landed `firestarter_py32f071.hex` as a real release asset matched by a two-entry glob, and REL-01 placed the ARM build after the version-bump auto-commit (both cited in `128-NONREGRESSION.md`; this is not a claim that the install works end to end). The next milestone after v1.23 is the **v1.30** entry (`ROADMAP.md`, *SDP Surface Retirement & Behavioral Lock Proof*, operator-queued 2026-07-31) — `/gsd-new-milestone` settles its final number. Prior footer retained below.*

*Last updated: 2026-08-24 — Phase 158 (Residual Optimizations + Cold Baseline Re-Record) complete and verified 8/8. The milestone's last size lever landed: `jsmntok_t` narrowed 8 -> 6 B on AVR for **-138 / -138 / -136 B flash and -128 B RAM** on `uno` / `uno328pb` / `leonardo` -- a flash reduction where the scoped figure predicted +30 B -- with the ARM `py32f071` half built on both sides, verified twice rather than ceiling-recorded. `size_baseline.json` re-recorded cold (22952/1434, 23000/1440, 25098/1875, both native envs 184/184/17) with the size-tripwire fixtures severed onto a new `*_v158*` family; default mode flipped RED -> full `PASS:`, one-sided because the comparators check growth only. BASE-01 fixed on a third, test-inventory axis (141 -> 184) with its growth axis byte-unchanged, so the canonical `--policy merge05` run exits 0 without erasing the reduction. Two candidates closed by measurement: the `flash_5v_page` per-byte modulo **DECLINED** (+22/+24/+22 B for no linkage saving -- `__udivmodsi4` only drops 11 -> 9 image-wide; the file is byte-unchanged), and `NUMBER_JSNM_TOKENS` closed on the forward-compatibility budget, explicitly not on arithmetic impossibility (`64 -> 56` *is* available; the scoped 57/7 figure is reproducible by none of three re-derived rules). The gate story is now stated in both its clauses: no `.github/` workflow invokes `check_size_baseline.py` as a size gate, AND its own pytest runs in CI at `build.yml:161` -- two docstrings asserting the inverse were corrected. Thirteen corrections made publicly as appended clauses, never as silent replacements. 360 firmware pytest / 0 skipped, 184/184 on both native legs; `firestarter_app` byte-untouched. Coverage ceiling stated: LAND-06's runtime half is unquantified by construction and the masked predicates have enumerated zero behavioural coverage. Carried to Phase 159: the citation line-shifts this phase created, the gitlink sha pairs, and the close-blocking `CITATIONS-STALE.md`. Nothing pushed — the beta cut and any promotion stay operator-gated. Prior footer retained below.*

*Last updated: 2026-08-23 — Phase 157 (Command-Decode Table + Handle Type Narrowing) complete and verified 7/7. `key_parsers[]`'s function-pointer column and the ten stubs it dispatched through are one `{key, clamp, offset, width}` PROGMEM table plus one inlined `store_field`, and `handle->protocol` / `handle->ctrl_flags` are narrowed to `uint8_t` / `uint16_t`: **-1144 B flash / -5 B RAM on all three AVR targets, cold-to-cold** (-884 B table half, -260 B narrowing half). All seven DECODE requirements closed. Native 172 -> 184 on both legs, 17 suites; app suite 1976 unchanged (repo byte-untouched). **The measured split is not the predicted one** — the ROADMAP's -976/-172 and the reference's -890/-258 are both superseded, the divergence attributed to OD-1's per-row mask-vs-saturate policy column; 22 stale figures (C-1..C-22) corrected in `.planning/milestones/v1.33-artifacts/157-after-figures.md`, which supersedes the ROADMAP and REQUIREMENTS prose. DECODE-05, the milestone's only safety requirement, closes a real hole: a wire `algorithm: 261` would have truncated to `0x05` and dispatched into the 5 V page-write handler. Coverage ceiling stated, not implied: one of the five safety cases passed **vacuously** against the obvious planted negative and needed a second, differently-shaped probe (C-18) — and Unity aborts on first failure, so a single planted negative cannot localize two cases at once. DECODE-07's `+18 B` matching the survey's stale figure is a coincidence of magnitude on a different switched-expression width, not a confirmation. The `merge05` size-gate pass is recorded **one-sided** (`check_size_baseline.py:697`/`:709` are growth-only, so a shrink passes with no named exemption). Carried forward to Phase 158: the 184 native case count and the frozen 141 baseline. Nothing pushed — the beta cut and any promotion stay operator-gated. Prior footer retained below.*

*Last updated: 2026-08-27 — Phase 160 (RIG — Dual-Arm Build, Flash Provenance & the Shared Cell Procedure) complete and verified 5/5, operator-signed-off. The bench rig exists and is trusted: both arms stood up as detached `firestarter_app` worktrees with byte-identical dependency sets, six firmware images built (all six cold rebuilds byte-identical, the two arms genuinely differing per env), one arm-agnostic 11-step `PROCEDURE.md` whose two arms render byte-identically under a gate proven able to go red, and a 12-tool suite behind `run_gates.sh` (11/11 selftests + 5/5 live gates, proven to fail closed). **All three on-device read chains proven and all three wrong-arm detectors observed FIRING**, not merely present: uno 22367/26026, uno328pb 22300/26066 (8 B vector-excluded), leonardo 24454/28170. `uno328pb`'s judged-span policy was derived from a live `-xshowvector` interrogation to `vector-exclusion` (reset vector + vector 25/SPM_Ready), removing the milestone's sharpest false-RED risk while the negative control still fires under those exclusions. The Leonardo's 1200-baud touch measured **same-node** — the `--wait-new-port` hypothesis was tested and empirically refuted, burning ~5.27 s of the ~8 s Caterina window. Write-read-verify clean on real silicon with the independent judge comparing against the WRITTEN image, not the app's self-consistency verdict (which never compares to it). RIG-01..05 all closed. **The method finding that matters more than any single artifact: ~20 latent rig-tooling defects surfaced only on first contact with real hardware, and every one had a PASSING fixture-based `--selftest`.** Bring-up-before-production earned its place. Coverage ceilings stated, not implied: argv is rarely recorded (0 `.cmd.json` in `BRINGUP-wrv`, 1 in `BRINGUP-uno`), so RIG-05's recorded-command-line property holds for the invocations `provenance.json` itself carries and not as a general property of every step; one invocation escaped both the config seam and the log (`~/.firestarter` created 07:59:25 during an operator-checkpoint window, frozen config dir independently unaffected); `BRINGUP-wrv`'s P-11 teardown never re-ran the board probe and is not backfilled; a plan-authoring defect recurred 4x (arm-agnostic constants in verify legs, plans 08/09/10/12), each caught in flight. A false shield declaration reached `EVIDENCE.jsonl` via the orchestrator and was caught by the operator, not by a gate — kept visible and marked SUPERSEDED rather than erased. Rig left assembled for Phase 161: Uno + Rev 2.0, v1.33 flashed, W27C512 seated, VPP 12.0 V, `/dev/ttyACM0`. No product code touched — both submodules byte-unchanged. Nothing pushed — the merge of `prom#43`/`fw#56`/`app#54` stays operator-gated. Prior footer retained below.*

*Last updated: 2026-08-23 — Phase 156 (Duplicated-Report Extraction + Boolean-Convention Repair) complete and verified. Two four-times-copy-pasted report blocks collapsed to one helper each and the inverted-return convention removed: **-426 B flash on all three AVR targets, RAM unchanged** (-268 DEDUP-01, -158 DEDUP-02), `__udivmodhi4` 31->13, all nine `return !op_execute_*` wrappers un-negated at measured zero byte cost (size-identical, `.hex` SHAs deliberately not identical). 172/172 native on both legs, 82/82 `native_loop_v131`, 355 firmware pytest (348 + 7 new gate legs), app suite 1976 unchanged. All four DEDUP requirements closed. Ten stale scoping figures corrected publicly before shipping. Coverage ceiling stated, not implied: DEDUP-02's Divergence 1 has no test oracle and is closed on source-level evidence only; plan 04's per-symbol ledger does not close (-356 B vs -158 B measured, LTO redistribution). Carried forward: the build-warning watermark now has 168 B of headroom and wants a re-measure (Phase 158). Nothing pushed — the beta cut and any promotion stay operator-gated. Prior footer retained below.*

*Last updated: 2026-08-23 — Phase 155 (Dead-Weight Removal — the heap allocator and the 64-bit runtime) complete and verified. The firmware is heap-free and 64-bit-runtime-free: symbol gate exit 1 -> exit 0, **-1366 B flash / -8 B RAM on all three AVR targets**, 172/172 native on both legs, 348 firmware pytest, app suite 1976 (unchanged — the repo is byte-untouched). All six DEAD requirements closed. Five scoping figures corrected publicly before shipping (the -1366-vs--1364 guard choice, 11-vs-8 symbols, the asymmetric VPP window, the RAM double-count, and the false "same statement" claim). Coverage ceiling stated, not implied: `rurp_common.cpp` compiles in no native environment, so that arithmetic has no native and no bench coverage and avr-gcc codegen is a named unmitigated residual. `size_baseline.json` NOT re-anchored (Phase 158 owns it). Carried forward: the Phase-153 `FLOOR` drift (8 checkers, floor 7). Nothing pushed — the beta cut and any promotion stay operator-gated. Prior footer retained below.*

*Last updated: 2026-08-23 — Phase 154 (Provenance Comment Sweep + Remap Tool) complete and verified. Three AVR targets byte-identical; remap tool built, not applied; manifest committed. Nothing pushed — the beta cut and any promotion stay operator-gated. Prior footer retained below.*

*Previously: 2026-06-10 — v1.12 (Firmware Protocol Dispatch Hardening + Skeletons) STARTED. First firmware-touching milestone since v1.10; fail-closed dispatch + not-implemented wire response + skeleton handlers for missing protocols; dual-repo lockstep, unified-beta branch model (all 3 repos off `beta`). Prior footer (v1.11 close) retained below.*

*Previously: 2026-06-10 — after v1.11 (Complete infoic.xml Decode & Database Correctness) close. Shipped 6 phases (56–61), 14 plans, 15/15 requirements, HOST-ONLY (firmware untouched like v1.8). Audit PASSED (15/15 reqs, 5/5 E2E flows, both correctness gates green on 743 chips, 559 tests). Meta tagged `v1.11`; lockstep beta cut `3.0.0b9` (firestarter_app version bump + gitlink bump + PyPI/GitHub pre-release) is operator-gated and pending. Stable promotion deferred per the operator-gated release rule. Deferred v1.9 read-bug RCA resumes at `/gsd-plan-phase 45`. Prior footer retained below.*

*Previously: 2026-06-08 — after v1.10 (Serial Transport Hardening / COBS) close + beta merge. Shipped 7 phases (49–55), 27 plans, 14/14 requirements: streaming COBS `0x00` + CRC8 framing with automatic resync on both the data-block path and the host→fw JSON command channel; 2 s timeout cascade removed; byte-exact proven on operator-witnessed bench (Uno + Leonardo); uno328pb instability transport-exonerated. Merged to beta in all 3 repos locally 2026-06-08 (fw beta@0266ee2, app beta@8480ff3, meta main@ec90b92) — not yet pushed; operator cuts the beta when ready (lockstep `BETA_VERSION=3.0.0b8`, explicit pin). Beta-only — stable `3.0.1` operator-gated. **v1.9 Read-Bug RCA DEFERRED** (operator 2026-06-08); resumes later at Phase 45.*
