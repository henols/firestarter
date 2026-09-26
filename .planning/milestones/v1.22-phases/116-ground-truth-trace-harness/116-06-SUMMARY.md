---
phase: 116-ground-truth-trace-harness
plan: 06
subsystem: testing
tags: [platformio, unity, native-test, firmware-harness, trace-oracle, sdp, parked-suite]

# Dependency graph
requires:
  - phase: 116-01
    provides: "HOST_STUBS_REAL_REGISTER_UTILS ordered strobe recorder; 82/82 native baseline"
  - phase: 116-02
    provides: "firestarter/test/native/avr/_shared/sdp_bus_config.h (generated bus_config_t ground truth, 5 rows)"
  - phase: 116-05
    provides: "_shared/sdp_expected.h (SDP_FIXED_<PINOUT> arrays, sdp_assert_stream_equals/sdp_first_divergence/sdp_snapshot); always-green test_sdp_harness suite; 95/95 native baseline; the DIP32 zero-CONTROL-seed decorative-comparison finding"
provides:
  - "test_eeprom28c_sdp/ — the parked, RED-by-design native suite (D-01): 7 cases pinning eeprom28c_write_init's real ordered stream against the FIX-01 remap-aware target, per DIP28/DIP24 pinout (3 cases) plus two deliberately stale-upper-address DIP32 cases (CORRECTION 3) plus the two migrated identity-gate assertions CORRECTION 2 routes here"
  - "RED-BASELINE.md — committed, verbatim expected-vs-actual divergence evidence, the CORRECTION 4 66-of-84 inhibit table, the validation ceiling, and the declined D-07 widening recorded as an open hook"
  - "platformio.ini -I entry for the parked suite, with no test_filter entry -- pio test -e native stays 95/95 through Phase 116; Phase 117's one-line addition of the allowlist entry IS the RED-to-GREEN proof"
affects: [117]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Dynamically-derived comparison target (drive the reference emitter under the IDENTICAL precondition as the shipped path, snapshot it, assert against the snapshot) instead of a static canonical array, when the static array would only expose an incidental/decorative divergence (CORRECTION 3's DIP32 case)"
    - "Self-repairing RED assertion: comparing against a dynamically-driven reference (not a hardcoded literal) means the assertion passes automatically once the shipped code path is rebuilt on the same underlying emitter -- no test edit needed at Phase 117"

key-files:
  created:
    - firestarter/test/native/avr/test_eeprom28c_sdp/host_stubs.cpp
    - firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp
    - firestarter/test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md
  modified:
    - firestarter/platformio.ini

key-decisions:
  - "DIP32 cases (4-5) assert against a DYNAMICALLY-DRIVEN reference-emitter snapshot (produced under the same stale CTRL_ADDRESS_LINE_17/18 seed the shipped path was driven under), not the canonical zero-seed SDP_FIXED_DIP32_28C512_EEPROM constant in the shared header -- a straightforward comparison against that constant would only reproduce the same incidental /OE-ordering divergence Cases 1-3 already show and would prove nothing about the real write-inhibit bug (CORRECTION 3 / 116-05-SUMMARY.md)"
  - "Case 5's real-preceding-read probe address is 0x0000, deliberately not 0x5555/0x2AAA (the SDP sequence's own magic addresses) -- reusing 0x5555 was tried first and produced a confounding LSB/MSB cache pre-warm elision that shrank the shipped snapshot from 54 to 48 entries, muddying the comparison with an unrelated (but real) elision effect"
  - "All 7 cases share ONE address-keyed mock (mock_get_data_keyed/mock_set_data_keyed, migrated from test_sdp_harness) rather than per-case mocks -- the same virgin-0xFF-at-0x5555 behavior serves both the DIP28/DIP24/DIP32 trace cases (identity irrelevant, chip_id=0) and the two identity-gate cases (chip_id set, mfr address keyed separately)"
  - "Response-code and stream-equality assertions are separate TEST_ASSERT calls per case (not folded into one) so a future partial fix (e.g. INIT no longer aborts, but the stream is still wrong) produces a distinguishable failure rather than one opaque assert"

requirements-completed: [TRACE-02, TRACE-04, TRACE-06]

coverage:
  - id: D1
    description: "A parked, RED-by-design native suite pins eeprom28c_write_init's real ordered stream against the FIX-01 remap-aware target for all four 0x0D pinouts plus a genuinely-discriminating second DIP32 size band"
    requirement: "TRACE-02"
    verification:
      - kind: unit
        ref: "test_eeprom28c_sdp.cpp#test_case1_at28c256_shipped_stream_diverges_from_fixed, #test_case2_at28c64_shipped_stream_diverges_from_fixed, #test_case3_at28c16_shipped_stream_diverges_from_fixed, #test_case4_at28c010_stale_direct_seed, #test_case5_at28c040_stale_via_real_read (all RED by design, verified via temporary test_filter compile+run, see RED-BASELINE.md)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Two migrated identity-gate assertions land in the RED-parked suite (CORRECTION 2's fix over D-12), and their RED-ness is the re-runnable software-layer evidence a 0x0D write aborts at INIT"
    requirement: "TRACE-04"
    verification:
      - kind: unit
        ref: "test_eeprom28c_sdp.cpp#test_case6_matching_chip_id_proceeds, #test_case7_mismatching_chip_id_with_force_warns; RED-BASELINE.md response-code table"
        status: pass
    human_judgment: false
  - id: D3
    description: "RED-BASELINE.md commits the verbatim, re-runnable expected-vs-actual divergence next to the code it describes, ceiling-compliant, and pio test -e native stays green throughout"
    requirement: "TRACE-06"
    verification:
      - kind: unit
        ref: "RED-BASELINE.md (committed); pio test -e native == 95/95 before and after both task commits"
        status: pass
    human_judgment: false

duration: 65min
completed: 2026-07-27
status: complete
---

# Phase 116 Plan 06: Ground Truth + Trace Harness — Parked RED SDP Suite Summary

**Authored `test_eeprom28c_sdp`, a 7-case native suite parked out of the `test_filter` allowlist (`-I` only) that pins `eeprom28c_write_init`'s real ordered register-write stream against the FIX-01 remap-aware target for every `0x0D` pinout — including a genuinely-discriminating pair of deliberately stale-upper-address DIP32 cases — plus the two migrated identity-gate assertions CORRECTION 2 routes here; committed the verbatim RED evidence as `RED-BASELINE.md`, with `pio test -e native` unchanged at 95/95.**

## Performance

- **Duration:** ~65 min
- **Started:** 2026-07-27 (continuing Phase 116 Wave 4)
- **Completed:** 2026-07-27
- **Tasks:** 2
- **Files modified:** 3 created (firmware sub-repo), 1 modified (platformio.ini); meta repo commit is this SUMMARY + STATE/ROADMAP/REQUIREMENTS

## Accomplishments

- **`test_eeprom28c_sdp/host_stubs.cpp`** — identical shape to `test_sdp_harness/host_stubs.cpp`: opts into the ordered strobe recorder (`HOST_STUBS_REAL_REGISTER_UTILS`) and adds the `reset_register_cache` seam. Two suites defining the same opt-in flag in separately-linked TUs is fine (`[env:native]` suites are independent binaries).
- **Cases 1-3 (DIP28_28C256/DIP28_28C64/DIP24_2816)** drive the real `eeprom28c_write_init` (via `configure_memory` dispatch) with the address-keyed mock reassigned for both `firestarter_get_data`/`firestarter_set_data`, and assert the recorded stream against `SDP_FIXED_<PINOUT>` (the existing 116-05 constants). All three diverge at index 0 — `fu_flash_fast_address` (shipped) writes address bytes directly with no `/OE` toggle up front, where `memory_set_data` (the FIX-01 target) toggles `/OE` first — plus genuine address-value differences downstream on AT28C64/16 from the missing bus-config remap.
- **Cases 4-5 (DIP32_28C512_EEPROM, AT28C010/AT28C040)** implement CORRECTION 3's requirement that a plain DIP32 trace is decorative (shipped and fixed streams are byte-identical there under a zero CONTROL seed — confirmed independently by 116-05). Instead, both cases establish `CTRL_ADDRESS_LINE_17`/`18` HIGH before driving the sequence (case 4: direct cache seed; case 5: a REAL preceding `memory_get_data` read) and assert the shipped stream against a DYNAMICALLY-DRIVEN reference-emitter snapshot taken under the identical stale seed — not the canonical zero-seed array. Verified empirically: shipped stream stays 54 entries regardless of the CONTROL seed (`flash_util_byte_flipping` never writes CONTROL); the stale-seeded reference emitter emits 57 (54 + 3: the extra CONTROL-clearing DATA+PIN-high+PIN-low triple) — a difference in kind, not incidental ordering, and self-repairing once Phase 117 rebuilds the shipped path on the same emitter.
- **Cases 6-7** migrate `matching_chip_id_proceeds` and `mismatching_chip_id_with_force_warns` from the retired `test_eeprom28c_chip_id` onto the address-keyed mock, landing in this RED-parked suite per CORRECTION 2 (D-12 originally mis-routed case 7 into the always-green harness; it is RED today because the unconditional SDP-disable completion wait overwrites a correctly-set `RESPONSE_CODE_WARNING` with `RESPONSE_CODE_ERROR`, destroying severity information).
- **`platformio.ini`** — one `-I test/native/avr/test_eeprom28c_sdp` line, no `test_filter` entry; a parking note directly above `test_filter` (mirroring the existing KNOWN-FLAKY block's style) names Phase 117's one-line addition as the RED-to-GREEN proof and forbids `TEST_IGNORE_MESSAGE`.
- **`RED-BASELINE.md`** — verbatim captured failure output for all 7 cases (via a temporary, reverted `test_filter` addition), the observed `RESPONSE_CODE_ERROR` per pinout, first-divergence index per trace case, the CORRECTION 4 66-of-84 inhibit table (with the `DIP24_2816`-inhibited-on-opposite-writes correction), the validation ceiling stated in the artifact itself, and the declined D-07 direction-recording widening logged as an open hook for Phase 117/118.

## Key findings recorded (per plan's required output)

- **Seven case names and observed RED reasons:**
  1. `test_case1_at28c256_shipped_stream_diverges_from_fixed` — diverges at index 0 (`/OE`-ordering)
  2. `test_case2_at28c64_shipped_stream_diverges_from_fixed` — diverges at index 0 (`/OE`-ordering; downstream address-value differences too)
  3. `test_case3_at28c16_shipped_stream_diverges_from_fixed` — diverges at index 0 (`/OE`-ordering)
  4. `test_case4_at28c010_stale_direct_seed` — length mismatch, expected 54 (shipped) vs recorded 57 (stale-seeded reference)
  5. `test_case5_at28c040_stale_via_real_read` — length mismatch, expected 54 (shipped) vs recorded 57 (stale-seeded reference)
  6. `test_case6_matching_chip_id_proceeds` — `response_code == RESPONSE_CODE_ERROR`, not `NOT_EQUAL(ERROR)`
  7. `test_case7_mismatching_chip_id_with_force_warns` — `response_code == RESPONSE_CODE_ERROR (0)`, expected `RESPONSE_CODE_WARNING (2)`
- **Response code after `eeprom28c_write_init`, all four pinouts (five rows): `RESPONSE_CODE_ERROR`** — matches 116-RESEARCH.md §F1 exactly; verified by the passing `TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, ...)` assertion in each of cases 1-5 (the assertion that fails and is captured is the SUBSEQUENT stream-equality check, not this one).
- **First-divergence index per trace case:** cases 1-3 diverge at index 0 (ordering); cases 4-5 diverge on stream LENGTH (54 vs 57), not a positional index within the shared prefix.
- **Temporary allowlist line confirmed removed** both after the initial compile-and-observe pass (Task 1's own verification) and again after Task 2's dedicated capture pass; region-scoped `awk`-bounded grep returned 0 both times.
- **Final `pio test -e native` count: 95/95** — unchanged from the plan 116-05 baseline, confirmed after both task commits.

## Task Commits

Each task was committed atomically (both in the `firestarter` sub-repo):

1. **Task 1: Author the parked RED suite and add its -I entry only (TRACE-02, TRACE-04, D-01/D-09, CORRECTION 2/3)** — `2d0d9df` (test) — parked suite compiles, is observed RED (7/7 fail), `test_filter` unchanged, 95/95
2. **Task 2: Compile the parked suite, observe it RED, and commit RED-BASELINE.md (D-02, TRACE-06 evidence)** — `ada4bdc` (docs) — verbatim divergence captured and committed, 95/95 re-confirmed

**Plan metadata:** committed in the meta repo (this SUMMARY + STATE.md + ROADMAP.md + REQUIREMENTS.md), see final commit below.

## Files Created/Modified

- `firestarter/test/native/avr/test_eeprom28c_sdp/host_stubs.cpp` — new
- `firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp` — new; 7 cases, all RED by design
- `firestarter/test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md` — new; committed evidence fixture
- `firestarter/platformio.ini` — `-I` entry + parking note added; no `test_filter` entry

## Decisions Made

- **DIP32 cases (4-5) compare against a dynamically-driven reference-emitter snapshot, not the canonical zero-seed `SDP_FIXED_DIP32_28C512_EEPROM` constant.** A straightforward comparison against that constant under a stale seed would reproduce the exact same incidental `/OE`-ordering divergence Cases 1-3 already demonstrate (since the shipped stream is provably unaffected by the CONTROL seed), proving nothing about the actual write-inhibit bug CORRECTION 3 exists to surface. Instead, both cases drive the reference emitter under the IDENTICAL stale seed the shipped path saw, snapshot it, and assert the shipped stream equals that snapshot — a comparison that is both non-decorative (54 vs 57, a difference in kind: an entire extra CONTROL-clearing event) and self-repairing (once Phase 117 rebuilds the shipped path on the same emitter, both sides converge automatically with no test edit).
- **Case 5's real-preceding-read probe address is `0x0000`, not `0x5555`.** First attempt used `0x5555` (matching the SDP sequence's own first write address) and produced a confounding cache-elision side effect: the real read pre-warmed the LSB/MSB latch cache to the exact values write #1 needed, eliding that write's address latch (a real, separate effect) and shrinking the shipped snapshot from 54 to 48 entries — muddying the comparison. Switched to `0x0000` (arbitrary, but distinct from both SDP magic addresses) so only the CONTROL-bit story is visible; re-verified clean (54 vs 57, matching case 4).
- **One shared address-keyed mock across all seven cases** rather than case-specific mocks — the identity axis is irrelevant to cases 1-5 (chip_id=0 skips `eeprom28c_check_chip_id` entirely) and the mock's virgin-0xFF-at-0x5555 behavior is exactly what makes the 2000-iteration completion-poll timeout contribute zero additional strobes, which is the precondition for full-stream (not prefix) equality.
- **Response-code and stream-equality checks are separate assertions per case.** This means a future partial fix at Phase 117 (e.g., the completion check stops inverting but the emitter is still not remap-aware) produces a distinguishable, informative failure rather than a single opaque one.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Case 5's probe address changed from 0x5555 to 0x0000 to avoid a confounding cache-elision effect**
- **Found during:** Task 1 (initial temporary-compile verification pass)
- **Issue:** Probing at `0x5555` (chosen initially to mirror the SDP sequence's own first magic address) coincidentally pre-warmed the LSB/MSB latch cache to the exact value write #1 of `EEPROM_SDP_DISABLE` needed, eliding that write's address-latch strobes (a real production behavior, but unrelated to the CONTROL-bit finding this case exists to isolate) and shrinking the shipped-stream snapshot from the expected 54 entries to 48 — producing a technically-still-RED but scientifically muddier assertion ("Expected 48 Was 57" instead of the clean "Expected 54 Was 57" case 4 shows).
- **Fix:** Changed the probe address to `0x0000` (arbitrary, chosen only to be distinct from `0x5555`/`0x2AAA`). `CTRL_ADDRESS_LINE_17` is set by the `rw_line`'s `READ_FLAG` bit alone, independent of the address value, so the stale-CONTROL mechanism is unaffected; the LSB/MSB cache is left at a value the SDP sequence's own writes do not coincidentally match, so no extra elision occurs.
- **Files modified:** `firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp`
- **Verification:** Re-ran the temporary-allowlist compile-and-observe procedure; case 5 now shows "Expected 54 Was 57", matching case 4's clean divergence shape.
- **Committed in:** `2d0d9df` (Task 1 commit — the fix landed before the first commit, not as a follow-up)

---

**Total deviations:** 1 auto-fixed (1 bug fix, discovered and corrected during the plan's own mandated verification step before any commit)
**Impact on plan:** No scope creep — the fix sharpens the intended discriminating power of Case 5 without changing its mechanism (real preceding read) or its assertion shape.

## Issues Encountered

- `pio test` reports `[ERRORED]`/`SIGBUS` (not `SIGINT` this time, but the same underlying cause noted in 116-05-SUMMARY.md) for a suite whose binary exits non-zero due to *expected* test failures. Running the built binary directly (`.pio/build/native/firestarter_native`) confirmed clean behavior both times (7 Tests, 7 Failures, 0 Ignored, exit code 7, no crash) — this is a `pio test` summary-reporting quirk on non-zero exit, not a suite defect.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `test_eeprom28c_sdp/` is compiled (via its `-I` entry) but excluded from the default `test_filter` run — Phase 117's one-line addition of `native/avr/test_eeprom28c_sdp` to that allowlist is the RED-to-GREEN proof; `RED-BASELINE.md` is the diff target a reviewer compares post-fix output against.
- `RED-BASELINE.md` names the declined D-07 widening (recording `rurp_set_data_output`/`rurp_set_data_input` direction edges) as an open, named hook for Phase 117/118 — not silently dropped.
- Native suite baseline stays **95/95** (unchanged from 116-05) — the parked suite contributes nothing to the default count.
- No blockers for plan 116-07 (`116-PREMISE.md` + PROJECT.md third ⚠ correction block, operator checkpoint).

---
*Phase: 116-ground-truth-trace-harness*
*Completed: 2026-07-27*

## Self-Check: PASSED

- FOUND: `firestarter/test/native/avr/test_eeprom28c_sdp/host_stubs.cpp`
- FOUND: `firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp`
- FOUND: `firestarter/test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md`
- FOUND: `.planning/phases/116-ground-truth-trace-harness/116-06-SUMMARY.md`
- FOUND commit `2d0d9df` (firestarter): test(116-06) parked RED suite + -I entry only
- FOUND commit `ada4bdc` (firestarter): docs(116-06) RED-BASELINE.md
