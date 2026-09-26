# Phase 74: Per-Family Correctness Fixes (flash-gated) - Context

**Gathered:** 2026-06-18
**Status:** Ready for planning
**Source:** Scope decisions captured interactively at plan-phase start (no discuss-phase run; grounded in Phase 72 `v1.13-PROTOCOL-ENUMERATION.md` + Phase 73 bench evidence)

<domain>
## Phase Boundary

Evidence-driven, software-first RED→GREEN correctness fixes for the divergences the Phase 73 bench surfaced — one requirement per family. Each fix turns a RED native/wire test GREEN and re-benches to a PASS cell **without regressing any other family**, while holding the Leonardo `pio run -e leonardo` ~88% flash ceiling and obeying dual-repo lockstep for any wire-touching change (meta-repo `messages.toml`-only → regen both sub-repos, py3.12-masks-CI-3.11 drift gate green).

This phase does NOT add new chip families or the erase path (Phase 75) or the GAP items (Phase 76). Fixes-before-additions.
</domain>

<decisions>
## Implementation Decisions

### FIX-01 — SRAM `configure_sram` no-op question → CLOSED NOT-NEEDED (evidence-gated on VAL-06)
- **LOCKED:** Phase 73 VAL-06 resolved this to `table-stakes-PASS` (FM1608, two-pattern A/B write+read-back, N=2, zero mismatches, hard gate D-09 satisfied; `firestarter_app/val-results/sram/val06-perbyte-verdict.txt` = "VAL-06 = table-stakes-PASS"; `validation-matrix.json` verdict=PASS, pass_type=authoritative, retry_count=2).
- **No firmware change.** FIX-01 is closed as **not-needed with recorded evidence**, exactly per the requirement's "IF VAL-06 shows it already works" branch.
- The plan must mark FIX-01 closed-with-evidence (cite the val-results artifacts + VERIFICATION SC#4), NOT implement an SRAM read/write rewrite.

### FIX-02 — flash4 correctness → EXPANDED to TWO defects (operator decision 2026-06-18)
- **Defect A (chip-id dispatch, on-spec):** `configure_flash4` (`firestarter/src/proms/flash_type_4.cpp:26-40`) has no `case CMD_CHECK_CHIP_ID:`, while `configure_flash3` (`flash_type_3.cpp:46`) does. Add the case mirroring flash3 (`flash3_check_chip_id_execute` analog), proven by a RED→GREEN native test in the `[env:native]` dispatch suite. No other family regresses (`check_dispatch.py` + `diff_db.py` + all native suites stay green).
- **Defect B (W29C040 write-algorithm FAIL, EXPANDED scope):** Phase 73 VAL-04 recorded a real **FAIL** on a seated W29C040 (Winbond, algorithm 5 = configure_flash4): `write_cycle_eprom` exit code 2 (hw-error) AND standalone `write -b` timeout. The negative control passed (verify-wrong-file exited non-zero), so the failure is a genuine write-algorithm incompatibility, not a harness artifact. **Operator decision: investigate AND fix the W29C040 page-write/SDP algorithm in this phase**, then Tier-3 re-bench to a PASS cell on Leonardo.
  - Research must establish the W29C040 datasheet write protocol (likely a Software Data Protection / SDP unlock sequence the current `flash4_write_execute` 64-byte page-write + DQ7-poll path is missing, and/or page-boundary handling) and what the current handler does wrong.
  - **VPP invariant:** flash4 is a 5V part family (no VPP). Any handler change must NOT enable the VPP regulator. If any register change touches VPP, it carries a register-bit-sequence native test + a chip-OUT VPP multimeter dry-run before any seated write.
  - Evidence artifacts already on disk: `firestarter_app/val-results/flash4/w29c040-source.bin`, `w29c040-wrongfile.bin`, `validation-matrix.json` (verdict=FAIL).

### FIX-03 — stale "0x39 = 0 chips, future-proofed" comment → CLOSE-WITH-EVIDENCE + RECONCILE (operator decision 2026-06-18)
- **LOCKED finding:** The requirement's premise ("2 current 0x39 DB chips") is **false**. Phase 72's authoritative `v1.13-PROTOCOL-ENUMERATION.md` (GAP-5, line 257) and the host source (`build_db.py`, `database.py:60`, `ic_layout.py:228`, `test_decoder.py`) all confirm **0 DB chips on 0x39** — 0x39 is a phantom (no IC2_ALG constant), removed from `KNOWN_PROTOCOLS` in v1.11 Phase 57 (DEC-05); host routes 0x39 → `not_implemented`. The "2 chips" claim originated in an early-research error (`.planning/research/FEATURES.md`) that Phase 72 already overturned. The firmware `memory.cpp:89` comment is, per Phase 72's source audit, **accurate**.
- **Plan must NOT invent phantom-chip validation.** Instead:
  1. Document FIX-03 closed not-needed against the "2-chip coverage" target, citing Phase 72 GAP-5 + host source.
  2. **Reconcile the firmware↔host 0x39 inconsistency:** firmware dispatches `0x39 → configure_flash4` ("future-proofed") while host routes `0x39 → not_implemented`. Clarify/align the comments (firmware `memory.cpp`, `firestarter/CLAUDE.md`, host `database.py`/`ic_layout.py`) so the two repos tell the same story about 0x39 (and 0x35, the sibling phantom). No behavioral wire change unless reconciliation demands one — if it does, it is meta-repo `messages.toml`-only → dual-repo regen with the drift gate.

### Cross-cutting constraints (LOCKED)
- **Software-first RED→GREEN:** each fix starts from a failing native/wire test, then GREEN.
- **No regression:** `check_dispatch.py`, `diff_db.py`, and all native suites stay green; every other family's behavior unchanged.
- **Flash ceiling:** every firmware-touching fix builds `pio run -e leonardo` under ~88% flash; record the flash-% in the summary.
- **Dual-repo lockstep:** any wire-touching change is meta-repo `messages.toml`-only → regen both sub-repos; the py3.12-masks-CI-3.11 drift gate must be green (validate `ruff check` + `ruff format --check` against py3.11, not just devcontainer 3.12).
- **Bench precondition:** Tier-3 re-bench halves (FIX-02 Defect B W29C040 write) require the standing bench precondition (live R1≈270000 readback, retry-on-timeout, Leonardo only — never uno328pb for program/write). Verify `controller:` identity per port at task start.
- **Milestone branch:** all code commits land on `v1.13-algo-validation` in each sub-repo (off beta); meta planning on the gsd branch.
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Protocol / scope authority
- `.planning/v1.13-PROTOCOL-ENUMERATION.md` — Phase 72 authoritative protocol enumeration; GAP-5 (line ~257) corrects the 0x39 "2 chips" error and confirms `memory.cpp:89` comment accuracy.
- `.planning/ROADMAP.md` (Phase 74 section, ~line 479) — phase goal + success criteria.
- `.planning/REQUIREMENTS.md` (FIX-01/02/03, lines 35-37) — requirement text (note FIX-03 premise is superseded by Phase 72).

### Phase 73 evidence (FIX-01 + FIX-02 Defect B)
- `.planning/phases/73-bench-validate-the-6-families-on-leonardo-hybrid-gated/73-VERIFICATION.md` — SC#4: FIX-01 closed not-needed; VAL-04 flash4 FAIL recorded.
- `.planning/phases/73-bench-validate-the-6-families-on-leonardo-hybrid-gated/73-03-SUMMARY.md` — W29C040 FAIL details (exit 2, write -b timeout, negative control passed).
- `firestarter_app/val-results/sram/val06-perbyte-verdict.txt` + `validation-matrix.json` — VAL-06 PASS evidence.
- `firestarter_app/val-results/flash4/w29c040-source.bin`, `w29c040-wrongfile.bin`, `validation-matrix.json` — flash4 FAIL artifacts.

### Firmware source (FIX-02 + FIX-03)
- `firestarter/src/proms/flash_type_4.cpp` — `configure_flash4`, `flash4_write_init/execute`, `flash4_wait_for_page_write` (the W29C040 FAIL path; missing CMD_CHECK_CHIP_ID case).
- `firestarter/src/proms/flash_type_3.cpp` — `configure_flash3` + `flash3_check_chip_id_execute` (the mirror source for Defect A).
- `firestarter/src/proms/memory.cpp` (line ~89) — 0x05/0x35/0x39 → configure_flash4 dispatch arm + the 0x39 comment.
- `firestarter/CLAUDE.md` — dispatch table + "0x39 future-proofed" note (FIX-03 doc target).
- `firestarter/test/native/avr/test_dispatch/` — native Unity dispatch suite (where the RED→GREEN chip-id test lands); `test_val_flash4.cpp` covers 0x05/0x35/0x39.

### Host source (FIX-03 reconciliation + non-regression gates)
- `firestarter_app/firestarter/database.py` (line ~60), `firestarter_app/firestarter/ic_layout.py` (line ~228) — host 0x39/0x35 phantom comments.
- `firestarter_app/tools/build_db.py` (lines ~129-148) — KNOWN_PROTOCOLS allowlist (0x35/0x39 absent).
- `check_dispatch.py`, `diff_db.py` — non-regression gates that must stay green.
- `firestarter_app/firestarter/dev_commands` (or equiv) — `dev validate-family flash4 --board leonardo` Tier-3 runner used to re-bench.
</canonical_refs>

<specifics>
## Specific Ideas

- Defect A is a near-verbatim mirror of the flash3 `CMD_CHECK_CHIP_ID` case — trivial code, but still RED→GREEN native test first.
- Defect B is the real engineering work: W29C040 (Winbond 512Kx8 5V flash/EEPROM) almost certainly needs the AMD/Winbond SDP unlock 3-byte sequence (0xAA→0x555, 0x55→0x2AA, 0xA0→0x555) before each page program, which the current bare `flash4_write_execute` set-data loop omits. Research must confirm against the W29C040 datasheet and reconcile with the existing flash3 unlock logic (flash3 already does unlock sequences — flash4 may be able to share a util).
- The W29C040 chip is the same physical part the operator seated for VAL-04, so a Tier-3 re-bench is reproducible on the existing fixture.
- 0x35 is the sibling phantom to 0x39 — reconcile both in the same FIX-03 doc pass for consistency.
</specifics>

<deferred>
## Deferred Ideas

- Erase path (ERASE-01) → Phase 75.
- GAP-01 / GAP-02 (X88C64 0x34 re-classification, etc.) → Phase 76.
- flash3/VAL-03 AM29F040 Tier-3 cell remains SKIP-deferred (no chip on hand) — not reopened here.
- Other SKIP-deferred Tier-3 cells (eeprom28c, flash_intel) stay deferred.
</deferred>

---

*Phase: 74-per-family-correctness-fixes-flash-gated*
*Context gathered: 2026-06-18 via interactive scope decisions at plan-phase start*
