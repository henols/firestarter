# Phase 116: GROUND TRUTH + TRACE HARNESS - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-27
**Phase:** 116-ground-truth-trace-harness
**Areas discussed:** RED-baseline mechanics, Trace fidelity + expected form, bus_config provenance, TRACE-04 anti-hollow

**Mode note:** default interactive flow, adapted — questions batched 3-per-turn within each area
and the per-area "more questions?" checks consolidated into a single check after all four areas,
to keep the operator's turn count proportionate to a 4-area discussion.

---

## Gray-area selection

| Option | Description | Selected |
|--------|-------------|----------|
| RED-baseline mechanics | How a deliberately-failing suite is committed without leaving `pio test -e native` red for the milestone | ✓ |
| Trace fidelity + expected form | Whether the recorded stream models the shield's cached-value elision; literal array vs golden text | ✓ |
| bus_config provenance | Hand-coded literals vs generated from `pinouts.json`/`database.py` | ✓ |
| TRACE-04 anti-hollow | `test_eeprom28c_chip_id` is parked out of `test_filter`, so fixing its mock in place never executes | ✓ |

**User's choice:** all four.
**Notes:** Set aside and offered but not selected: TRACE-05's exact home/form, the AT28C64B +
doc0270 PDF-acquisition prerequisite CONFLICT-1 rests on, and whether the SDP suite's directory
name should anticipate Phases 118–119 reusing it. Recorded as Claude's Discretion in CONTEXT.md.

Todo cross-reference presented as text rather than a question: all 5 `todo.match-phase 116`
matches scored 0.6 on generic keyword overlap and none touches tracing, `0x0D`, or the native
harness. Recorded as reviewed-not-folded.

---

## RED-baseline mechanics

### Q1 — How should the deliberately-RED 0x0D SDP trace suite live at the end of Phase 116?

| Option | Description | Selected |
|--------|-------------|----------|
| Park out of `test_filter` | Excluded from the allowlist with a named TODO; native suite stays green; 117's one-line allowlist addition IS the RED→GREEN proof | ✓ |
| In the allowlist, accept red | Most directly observable RED state, but a real regression during 117 hides inside expected noise | |
| In the allowlist, TEST_IGNORE-marked | Reports IGNORED not FAIL; but IGNORED does not demonstrate RED, so it adds ceremony without evidence | |

**User's choice:** Park out of `test_filter` (the recommended option).

### Q2 — Where does the RED evidence get pinned so Phase 117's GREEN claim is checkable?

| Option | Description | Selected |
|--------|-------------|----------|
| Committed fixture under `test/` | `RED-BASELINE.md` next to the code; survives `.planning/` archival; reviewable at 117 without checking out an old tree | ✓ |
| Phase artifact only | Zero sub-repo footprint, but one archival sweep from being orphaned, and in a different repo from the code | |
| Both | Belt-and-braces, with two copies to keep in sync | |

**User's choice:** Committed fixture under `test/`.

### Q3 — Should TRACE-01's recording extension get its own permanently-GREEN suite?

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — separate green suite | The recorder has no dependency on the fix, so it is GREEN on day one and enters `test_filter` immediately, keeping GATE-03 substantive while the 0x0D suite is parked | ✓ |
| No — one suite | Fewer directories, but nothing verifies the recorder itself for a full phase | |

**User's choice:** Yes — separate green suite.

### Q4 — How should the four planted-fault negatives be injected, given no production edits?

| Option | Description | Selected |
|--------|-------------|----------|
| Committed, re-runnable in-TU | Table faults as test-local `byte_flip_t` copies; `LOG_`-in-window via source-scan checker + planted fixture file; `protocol != 0x0D` as a plain positive | ✓ |
| One-time recorded transcript | Cheapest, but the proof is a screenshot — nothing stops a later refactor re-hollowing the harness | |
| Scripted mutate/run/revert harness | Re-runnable and uniform, but writes to tracked source during a test run and can leave a dirty tree on abort | |

**User's choice:** Committed, re-runnable in-TU.

---

## Trace fidelity + expected form

### Q1 — Should the recorder model production's cached-value elision, or record every call?

| Option | Description | Selected |
|--------|-------------|----------|
| Model elision | Trace reflects what the 74HC573 latches see; without it the expected literal asserts writes that never leave the MCU | ✓ (then refined, see Q4) |
| Raw call-log | Simpler; faithful log of what the emitter asked for; but the byte-exact claim at close would need hedging | |
| Record both streams | Maximum information, but eight golden arrays across four pinouts and drift between them is a new failure mode | |

**User's choice:** Model elision.
**Notes:** Grounded in a tree read, not research assertion — `rurp_write_to_register`
(`rurp_register_utils.h:24`) returns early on an unchanged cached LSB/MSB/CONTROL value, and the SDP
sequence addresses `0x5555` three times. Research finding 10 independently warns that a test
*counting* register writes draws the wrong conclusion.

### Q2 — What form should the expected stream take in the test source?

| Option | Description | Selected |
|--------|-------------|----------|
| Literal tuple array | Element-by-element compare with an assert message naming the diverging index; matches `test_val_5v_page.cpp`; 117's diff is a readable data change | ✓ |
| Golden text trace | Readable failure output and a literal `RED-BASELINE.md`, but needs a rendering layer that itself needs a test, and whitespace churn becomes a failure | |
| Both — array asserts, text on failure | Best failure ergonomics with one source of truth, at the cost of a helper needing its own test | |

**User's choice:** Literal tuple array. (The failure-time renderer was subsequently recorded as
permitted-but-optional under Claude's Discretion.)

### Q3 — How wide should the CE/OE edge recording go?

| Option | Description | Selected |
|--------|-------------|----------|
| Scoped to what 0x0D needs | Data-buffer bytes plus the chip-enable/disable and data-direction transitions the `eeprom_28c` + `flash_utils` paths call; smallest surface | ✓ |
| Every side-effecting `rurp_*` call | Future-proofs Phases 118–121, but widens the stream and makes the flag-off byte-exactness argument harder | |

**User's choice:** Scoped to what 0x0D needs.

### Q4 — Follow-up: how should the recorder *obtain* its elision behaviour?

Raised after Q1 because a hand-replica of production caching is itself a drift risk, and a tree
read showed `rurp_register_utils.h` is native-includable (header-with-definitions, included only by
`src/boards/*.cpp`, which `[env:native]`'s `src_filter = +<proms/>` excludes; its
`rurp_internal_write_to_register` body is `#if`-gated off the Uno `PORTD` path and calls only
already-stubbed symbols).

| Option | Description | Selected |
|--------|-------------|----------|
| Include the real header | Zero drift by construction; hooks move to `rurp_write_data_buffer`/`rurp_set_control_pin`; stream becomes latch-strobe-shaped; real cache-backed `rurp_read_from_register` applies inside new-flag suites only | ✓ |
| Hand-replica in the recorder | v1.18 WR-01 precedent; simpler blast radius; but silent divergence if production caching changes | |
| Let Claude decide at plan time | Defers a decision hinging on a compile result nobody has observed yet | |

**User's choice:** Include the real header.

---

## bus_config provenance

### Q1 — Where should the four 0x0D pinouts' bus_config values come from?

| Option | Description | Selected |
|--------|-------------|----------|
| Generated from the host's own derivation | Generator imports the real `database.py`/`convert_to_programmer` path; a `pinouts.json` change breaks the generator instead of staling the golden; `gen_validation_header.py` precedent | ✓ |
| Hand-coded literals in the test TU | Zero tooling and no cross-repo coupling, but ground truth becomes a transcription — and `pinouts.json` moved twice in four milestones (Phase 94, Phase 98) | |
| Generated + host pytest pinning the derivation | Strongest; machine-checked on both sides; one more file and a second update locus | |

**User's choice:** Generated from the host's own derivation.

### Q2 — Which chips should the trace suite cover?

| Option | Description | Selected |
|--------|-------------|----------|
| 4 pinouts + size bands within DIP32 | One representative per pinout plus ≥1 extra `DIP32_28C512_EEPROM` band — that pinout spans 64 KB–512 KB and Phase 117's FIX-03 differs across it | ✓ |
| All 84, table-driven | Maximum coverage; but 84 goldens to regenerate and a failure report naming 84 rows for one pinout | |
| Exactly 4, one per pinout | Literal reading of TRACE-02; leaves FIX-03 without a band-distinguishing trace | |

**User's choice:** 4 pinouts + size bands within DIP32.

### Q3 — Should the generated header carry a CI drift gate?

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — follow the `messages.h` convention | Committed with a DO-NOT-EDIT banner; a test regenerates and diffs; existing convention in this repo, not new machinery | ✓ |
| Committed, no gate | Less CI surface, but the drift the generator prevents becomes a convention rather than a guarantee | |

**User's choice:** Yes — follow the `messages.h` convention.

### Q4 — Follow-up: where should the generator run, and how does the gate cross the two repos?

Raised because the derivation lives in `firestarter_app/firestarter/database.py` but the header must
land in the firmware repo, and the two are separate submodules.

| Option | Description | Selected |
|--------|-------------|----------|
| Host-side generator, host-side gate | Generator in `firestarter_app/tools/`; header committed under `firestarter/test/native/avr/_shared/`; drift gate a host pytest with the `FW_ABSENT` skipif shape already used for firmware↔host parity | ✓ |
| Firmware-side generator importing the host | Keeps artifact and generator co-located, but introduces a firmware→host import direction that does not exist and firmware CI has no reason to install the host package | |
| Meta-repo source of truth, synced down | Established `messages.toml` ritual, but that source is hand-authored — here the meta repo would hold a *derived* artifact, a third copy to keep honest | |

**User's choice:** Host-side generator, host-side gate.

---

## TRACE-04 anti-hollow

Presented with a finding surfaced while reading the suite: with an address-keyed mock returning
virgin `0xFF` at `0x5555`, `test_eeprom28c_matching_chip_id_proceeds`
(`test_eeprom28c_chip_id.cpp:101`) goes RED because the inverted check times out — so that failing
test *is* TRACE-06's INIT-abort proof, and TRACE-04/TRACE-06 can share one mechanism.

### Q1 — What should happen to the parked `test_eeprom28c_chip_id` suite?

| Option | Description | Selected |
|--------|-------------|----------|
| Migrate and split | Three SDP-independent identity assertions into the always-green suite; matching-id-proceeds into the RED-parked suite as TRACE-06 evidence; old directory retired | ✓ |
| Fix the mock in place, stay parked | Smallest diff and TRACE-04's wording satisfied, but the assertion still never runs — the hollow-gate class this milestone exists to avoid | |
| Fix + root-cause the SIGABRT | Cleanest end state and retires real debt, but an unbounded debug task inside the phase the milestone's ordering rests on | |

**User's choice:** Migrate and split.

### Q2 — Should Phase 116 take on re-enabling the two parked flaky suites more broadly?

| Option | Description | Selected |
|--------|-------------|----------|
| No — keep it deferred | Reach into `test_eeprom28c_chip_id` only as far as the migration requires; the assertions that matter run anyway via a new home | ✓ |
| Yes — fix both while we're here | Retires debt open since Phase 17 and broadens GATE-03, but unbounded and twice deferred already | |

**User's choice:** No — keep it deferred.

### Q3 — Should Phase 116 apply the PROJECT.md corrections, or only record them?

| Option | Description | Selected |
|--------|-------------|----------|
| Apply immediately | `116-PREMISE.md` plus a third ⚠ correction block in PROJECT.md this phase; every researcher for 117–122 reads that file | ✓ |
| Record only, apply at close | Keeps canonical-doc edits in one operator-visible place, at the cost of six phases of agents reading a disproved premise | |

**User's choice:** Apply immediately.

---

## Claude's Discretion

- Suite/directory naming for the new RED and always-green suites (including whether the name should
  anticipate Phases 118–119 reuse — explicitly set aside by the operator).
- Whether to add a failure-time text renderer on top of the tuple-array assert (permitted; the array
  stays the single source of truth and any renderer needs its own test).
- The `{kind, reg-or-pin, value}` entry layout, the new opt-in flag's name, and the recording-buffer
  capacity (today `HOST_STUBS_MAX_RECORDING 256`; a strobe-shaped stream is finer-grained).
- TRACE-05's exact home and form — which test file, and literal `84` vs derived count.
- Representative chip selection within the coverage bands, and how many extra DIP32 bands beyond
  the required one.

## Deferred Ideas

- Unity-teardown SIGABRT root cause / re-enabling `test_eeprom28c_chip_id` and
  `test_flash_intel_vpp` in `test_filter` — pre-existing debt since Phase 17 WR-01 / Phase 20.
- Recording every side-effecting `rurp_*` call — revisit if Phases 118/119 find the scoped
  recorder insufficient.
- All-84-chips table-driven trace coverage — revisit only if a per-chip defect is suspected within
  a pinout.
- `PAGE_SIZE 64` hard-coded at `eeprom_28c.cpp:19` vs AT28C010's 128 B / AT28C040's 256 B
  (18 chips) — research finding 9's explicit named deferral.
- `DIP24_2816` missing `static-high-pins` (`static_high_mask == 0`, 19 chips) — SDP-F8; the
  Phase-117 remap does not address it; the Phase-116 trace will make it visible.
- Datasheet verification of SDP magic addresses for AT28C040 / AT28C16 / AT28C04 — SDP-F7,
  recorded UNVERIFIED per size band.
- Reviewed-not-folded todos: the 5 keyword-only `todo.match-phase 116` hits (see CONTEXT.md
  `<deferred>` for the itemised list and reasons).
