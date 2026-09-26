# 138-03-TRACE-CAPTURE: Merged strobe+timing capture of the pre-change 27C write loop

**Owner requirement:** PREP-03 (partial evidence only — PREP-03 itself is discharged by plan 138-07,
not here; this plan ticks **no** requirement, per its own `may_tick_requirements: []`).
**Status:** all three protocols captured, each proven overflow-free, converged, and deterministic
before anything is frozen. No frozen array exists yet (plan 05 pastes them from the dumps this record
cites).

## 1. What this record is

Phase 138 Plan 03 built a third opt-in native-test recorder (`HOST_STUBS_RECORD_TIMING`) that
interleaves `delay()`/`delayMicroseconds()` calls into the existing ordered strobe stream, and used it
to drive the **real, unmodified** `eprom_write_execute` (the pre-v1.31 27C program+verify loop) for all
three EPROM protocols (`0x07`, `0x08`, `0x0B`) against a deliberately-chosen 4-byte synthetic block. This
record is the measured evidence: entry counts, the derived `bus_config` values with their provenance, and
three findings carried forward with named owners. It is **not** a fix to anything it observes.

## 2. Measured entry counts (cold, this session, `pio test -e native_trace_v131` + the built binary run
directly — `pio test` swallows `printf`)

| Protocol | Chip / pinout | strobe_count() | timing_count() | merged length | % of 512 cap (merged) | passes | response_code |
|---|---|---|---|---|---|---|---|
| `0x07` | AM27C512 / DIP28_27512 | 142 | 56 | **198** | 38.7% | 3 | `RESPONSE_CODE_OK` |
| `0x08` | AM27C020 / DIP32_27C020 | 157 | 64 | **221** | 43.2% | 3 | `RESPONSE_CODE_OK` |
| `0x0B` | AM2716 / DIP24_2716 | 142 | 59 | **201** | 39.3% | 3 | `RESPONSE_CODE_OK` |

All three are comfortably below the 60% ceiling the plan's acceptance criteria set (≤ 307 of 512 for
each of `HOST_STUBS_MAX_STROBES` and `HOST_STUBS_MAX_TIMINGS`), and `strobe_overflowed() == 0` /
`timing_overflowed() == 0` held for every drive. Both the strobe and timing recorders (`HOST_STUBS_MAX_STROBES`
/ `HOST_STUBS_MAX_TIMINGS`) are pinned at 512 entries each (`test/native/avr/_shared/host_stubs_common.inc`).

**Pass count, measured not assumed:** each protocol's timing stream contains exactly **three**
`TIMING_KIND_DELAY_MS` entries with value `10` (`program_mismatched_bytes`'s `delay(10)`, emitted once
per outer retry-loop pass) and exactly **one** entry with value `500` (`eprom_write_execute`'s one-time
VPP-enable `delay(500)`, outside the loop). Three passes matches the synthetic block's worst-case byte
(index 2, `converge-after=2`, needing three passes) exactly.

**Adaptive pulse growth, measured:** the `TIMING_KIND_DELAY_US` histogram at the program-pulse value
(`handle->pulse_delay`, base 100 µs for `0x07`/`0x08`, 500 µs for `0x0B`) shows three **distinct** widths
per protocol, each count matching the number of bytes reprogrammed in that pass:

| Protocol | Pass 1 (4 bytes reprogrammed) | Pass 2 (2 bytes: indices 2,3) | Pass 3 (1 byte: index 2) |
|---|---|---|---|
| `0x07` / `0x08` (base 100 µs) | 100 µs × 4 | 105 µs × 2 | 110 µs × 1 |
| `0x0B` (base 500 µs) | 500 µs × 4 | 525 µs × 2 | 550 µs × 1 |

This reproduces `eprom.cpp`'s adaptive formula exactly: `pulse_delay = org_delay + org_delay*retries/20`,
for `retries` = 1 then 2 — a strobe-only recorder could never see this; it is the entire point of D-02's
timing layer.

## 3. RESEARCH's derived estimate vs. the measurement — the measurement wins

`138-RESEARCH.md`'s entry-budget table derived **≈174 strobes** for a "4-byte block, 3 passes", from
per-operation atomic constants (≈7 strobes/3 timings per programmed byte, ≈6/2 per verified byte, ≈6/3
per VPE assert+release cycle, ≈3/2 for the one-time VPP enable) applied to a **naive uniform** assumption
— every byte reprogrammed on every pass (4 programs × 3 passes = 12). The real, convergence-aware loop
reprograms only currently-mismatched bytes each pass (4 + 2 + 1 = 7 programs total across three passes,
not 12), while still **verifying** all 4 bytes every pass (4 + 4 + 4 = 12), because
`verify_and_update_mask` re-checks the whole block unconditionally. Applying RESEARCH's own atomic
constants to the REAL operation counts (7 program-ops, 12 verify-ops, 3 VPE-cycles, 1 VPP-enable)
reproduces the measured `0x07`/`0x0B` strobe count **exactly**: `7×7 + 12×6 + 3×6 + 1×3 = 142`. The
atomic constants are correct; RESEARCH's own "174" aggregate was a simplified over-estimate for this
fixture's actual convergence pattern. Per D-06/the project's standing rule for such divergences: **the
measurement (142/157/142 strobes, 198/221/201 merged) is recorded as authoritative; RESEARCH's 174 is
recorded beside it, not silently reconciled.** `0x08`'s higher counts (157 strobes / 64 timings) are
attributable to its P1-as-VPP register routing (§5 below) producing additional non-elided latches and
three extra `CTRL_VPP_P1_ENABLE` set→clear settle delays (`delayMicroseconds(4)`) that `0x07`/`0x0B`'s
non-P1 VPE path (`0x07`) or different P1 wiring interaction (`0x0B`) do not produce in the same count.

## 4. Timing stream composition — dominated by short latch/settle entries, recorded unfiltered

| Protocol | 1 µs (latch) | 3 µs (write settle) | 4 µs (P1 set→clear settle) | pulse widths | 10 ms ×3 (per-pass VPE) | 500 ms ×1 (VPP enable) |
|---|---|---|---|---|---|---|
| `0x07` | 26 | 19 | 0 | 4+2+1=7 | 3 | 1 |
| `0x08` | 31 | 19 | 3 | 4+2+1=7 | 3 | 1 |
| `0x0B` | 26 | 19 | 3 | 4+2+1=7 | 3 | 1 |

The 1 µs latch entry (`rurp_internal_write_to_register`'s post-strobe `delayMicroseconds(1)`) is the
single most frequent timing entry in every protocol, as RESEARCH predicted — though not an outright
majority of all timing entries once the 3 µs write-settle entries (`memory_set_data`'s fixed
`delayMicroseconds(3)`) are counted too. **Decision: record every timing entry unfiltered**, including
the 1 µs entries. Filtering them would hide exactly the interleaving (strobe, then delay, then strobe)
this fixture exists to prove is captured at all — stated in `eprom_v131_expected.h`'s own file banner.

## 5. The three derived `bus_config` values — provenance

Sourced from the host's own code path, never invented, never hand-derived. Zero-degeneracy confirmed:
`mem_util_remap_address_bus` (`src/proms/memory.cpp:356-379`) starts with
`reorg_address = config.address_mask & address`, so a zeroed `bus_config` collapses every address to 0 —
a zero `address_mask` would be degenerate, not an identity remap. None of the three below is zero.

**Derivation command** (run live against `firestarter_app`, 2026-08-08):
```
cd /workspaces/firestarter_app && python3 -c "
    import sys; sys.path.insert(0, 'tools'); sys.path.insert(0, '.')
    from gen_sdp_bus_config import derive_row
    from firestarter.database import EpromDatabase
    db = EpromDatabase(skip_local_override=True)
    for chip in ['AM27C512', 'AM27C020', 'AM2716']:
        print(chip, derive_row(db, chip))"
```

Translation from `derive_row`'s dict to `bus_config_t` fields mirrors `src/json_parser.c:401-436`
(`parse_bus_config`) field-for-field (a `None` `rw_line`/`vpp_pin` becomes the `0xFF` sentinel;
`static_high` becomes `static_high_mask` by OR-ing `1UL << line`; `address_lines` gets a `0xFF`
sentinel after the last real entry):

| Chip | Protocol | Pinout | mem_size | `address_mask` | `matching_lines` | `rw_line` | `vpp_line` | `static_high_mask` |
|---|---|---|---|---|---|---|---|---|
| AM27C512 | `0x07` | DIP28_27512 | 65536 | `0x0000FFFF` | 16 | `0xFF` | `0xFF` | `0x00000000` |
| AM27C020 | `0x08` | DIP32_27C020 | 262144 | `0x0011FFFF` | 17 | `0x16` (22) | `0x15` (21) | `0x00000000` |
| AM2716 | `0x0B` | DIP24_2716 | 2048 | `0x000007FF` | 11 | `0xFF` | `0x0B` (11) | `0x00002000` |

**Genuine, derived-not-coded, real-hardware consequence confirmed empirically:** AM27C020's
`vpp_line=0x15` exactly equals `VPP_P1_32_DIP`, and AM2716's `vpp_line=0x0B` exactly equals
`VPP_P21_24_DIP` (`include/rurp_shield.h`) — so `using_p1_as_vpp(handle)` (`memory_utils.h:24-28`) is
**true** for both chips (given their real `pins` values, 32 and 24 respectively), while it is false for
AM27C512 (`vpp_line=0xFF`). The captured traces show this directly: `0x08` and `0x0B` both carry the
`CTRL_VPP_P1_ENABLE` set→clear `delayMicroseconds(4)` settle entry (§4) that `eprom_internal_set_control_register`
only emits under the P1-remap path; `0x07` does not. This was **not** special-cased in the test — it
falls out automatically from feeding the real, derived `bus_config`/`pins` values into the real
production functions, which is the entire point of deriving rather than inventing them.

## 6. Findings recorded (owner named, none fixed here — D-07's rule)

**F-138-06** — `test/native/avr/_shared/host_stubs_common.inc`'s **pre-existing** `HOST_STUBS_REAL_REGISTER_UTILS`
block comment (added Phase 116) claims it "composes with, does not replace,
`HOST_STUBS_RECORD_BUS`" — but the preprocessor structure at that block is
`#ifdef HOST_STUBS_REAL_REGISTER_UTILS … #elif defined(HOST_STUBS_RECORD_BUS) … #else`, so defining
both guards compiles **only** the strobe recorder; the `(reg,data)` array is never compiled in that
case. The same comment also states "14 pre-existing suites", where `platformio.ini`'s two pinned native
envs each carry **17** `test_filter` entries (recounted live this plan, from `platformio.ini` itself,
not copied from any planning artifact). **Owner: henols. Not fixed here** — the correction is recorded
in this file and in this plan's own new block's comment (which states the true count and composition
correctly), not by rewriting the old block's wording, since that file's byte-level stability is
load-bearing for the 17 suites that already depend on it.

**F-138-07** — `firestarter_app/tools/gen_sdp_bus_config.py` emits only 5 rows, all `0x0D` (28C-family
EEPROM) pinouts, and its `validate_rows` explicitly **rejects** any pinout carrying `static-high-pins`
(`raise ValueError` at "unexpected static-high-pins") — which `DIP24_2716` (AM2716, protocol `0x0B`)
does (`static_high=[13]`). Extending the generator to emit 27C rows is the principled long-term route
(it would keep every trace-fixture address traceable to `pinouts.json` through one reviewed code path),
but it is an **app-repo** code change regenerating a header two frozen SDP suites (`test_sdp_harness`,
`test_eeprom28c_sdp`) already consume — outside this phase's fence, and outside "generated files are
never hand-edited" if attempted casually. **Owner: henols. Not fixed here.** This plan took the
alternative, still-principled route instead: deriving each row through the generator's own `derive_row`
function directly (§5) — the same host code path, same translation rules, without touching the
generator's emission surface or its committed output file at all.

**F-138-08** — **applies; not dropped.** The captured stream shows **no** `CTRL_VPP_REGULATOR_ENABLE`
clear anywhere on the converged success path, for any of the three protocols (§5's CONTROL_REGISTER
write-history trace: every write from the first VPP-enable through the final pass keeps bit `0x80`
set). This matches `eprom_write_execute`'s source exactly: the VPP-regulator disable
(`handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE, 0)`) sits **only** on the
retry-exhausted failure path (after the `for` loop completes without a match), never on the success
return. A caller driving only `CMD_WRITE` end-to-end leaves the VPP regulator enabled after a
successful write, relying on some other path (a subsequent command, or firmware idle/reset behaviour)
to disable it. **Owner: Phase 142 / VPP-03.** Recorded, not fixed — Phase 138's fence forbids editing
`eprom.cpp`.

## 7. Not established by this record

- **No frozen array exists yet.** This plan proves the capture is sound and reproducible; plan 05 pastes
  the frozen `EPROM_V131_TRACE_PROTO_07/_08/_0B` arrays from the three dump files this plan produced
  (session scratchpad, one per protocol, each containing at least as many initialiser lines as its
  protocol's recorded merged length above).
- **No claim about the new (post-v1.31) cadence.** This is the *pre-change* baseline only; Phase 144's
  TEST-06 authors the new trace and reviews the diff.
- **No write-path source was read as anything but read-only evidence.** `git -C /workspaces/firestarter
  status --porcelain src/` was empty throughout this plan's Task 3 work.

---

*Phase: 138-preconditions-baseline — Plan 03, Task 3*
*Recorded: 2026-08-08, from live measurements taken this session (`pio test -e native_trace_v131` +
the built binary `.pio/build/native_trace_v131/firestarter_native` run directly) and a live re-run of
`gen_sdp_bus_config.py`'s `derive_row` against `firestarter_app`'s shipped database.*

## 8. Freeze record (Plan 05)

Plan 05 pasted the three dump files this record cites into `eprom_v131_expected.h` as literal
arrays, switched the three protocol cases to full ordered positional equality
(`v131_assert_stream_equals`), and pinned the fixture with a committed inventory JSON
(`tests/golden/eprom_v131_trace_inventory.json`) plus a parallel six-assertion python identity gate
(`tests/test_golden_trace_identity_eprom_v131.py`) — the exact `sdp_expected.h` triple (D-04) applied to
this fixture. All landed in **one** firmware commit, `67d6061` (firestarter,
`gsd/v1.31-27c-programming-algorithm-fidelity`), which also carries Task 1's `test_trace_eprom_v131.cpp`
assertion-switch — the commit was built via an amend of Task 1's initial commit specifically so the
fixture header, the inventory JSON, and the consuming `.cpp` all land together, satisfying D-04's
two-independent-mechanisms contract in a single, atomic firmware change.

- **Fixture's committed blob SHA:** `ca3e09f164e6e1c541ecb63d15bbebf5bce41d70`
  (`git rev-parse HEAD:test/native/avr/_shared/eprom_v131_expected.h`, equals `git hash-object` on the
  working file, equals the inventory's own `meta.blob_sha`).
- **Inventory's `recorded_at_head`:** `3dad6450e277692eb4374de1512d69eaa17709de` — the real commit that
  existed at the moment the blob SHA was derived (Task 1's un-amended commit); recorded as a point-in-time
  reference exactly as the pre-existing SDP inventory's own `recorded_at_head` does (that field points to
  an unrelated, non-self-referential ancestor commit too — verified live this plan, `17c7614d…` is a
  Phase 124 Plan 02 commit, not the one that added `sdp_expected.h`). Not asserted by any test; purely
  descriptive, matching the analog's own established convention.

### Three break classes — each observed RED on exactly one leg, then restored

A gate that has only ever passed is untrusted, and a pre-authored gate leg can be unreachable. **Leg 1
below is a live example of exactly that trap, caught in the act, not merely a theoretical risk this
record cites secondhand:** a plain working-tree edit to the fixture header left
`test_blob_sha_matches_the_recorded_inventory` silently GREEN, because that assertion reads
`git rev-parse HEAD:<path>` — the **committed** blob — never the live file. The leg only became
reachable after the perturbation was itself committed (temporarily) so `HEAD:<path>` actually changed.
This is the reachability check the plan's own known-traps note anticipates; it was not skipped.

| Leg | Break planted | Mechanism needed to reach it | RED leg (message, abbreviated) | Legs that stayed GREEN |
|---|---|---|---|---|
| 1 — blob SHA | Appended one comment line to `eprom_v131_expected.h` | **A real commit** (working-tree-only edit is invisible to this leg — see above) | `test_blob_sha_matches_the_recorded_inventory`: "blob SHA changed -- recorded=ca3e09f… observed=15097b6…" | names, entry-counts, non-vacuous, consumer-inclusion, git-required (5/6) |
| 2 — inventory | Changed `EPROM_V131_TRACE_PROTO_08`'s `entries` 221 → 999 in the inventory JSON | Working-tree edit alone (this leg reads the file directly, not via git) | `test_array_entry_counts_match_the_recorded_inventory`: "first divergence at index 1 -- recorded={'name': 'EPROM_V131_TRACE_PROTO_08', 'entries': 999}, live={'name': 'EPROM_V131_TRACE_PROTO_08', 'entries': 221}" | blob-sha, names, non-vacuous, consumer-inclusion, git-required (5/6) |
| 3 — consumer inclusion | Renamed the include spelling in `test_trace_eprom_v131.cpp` (`eprom_v131_expected.h` → `eprom_v131_EXPECTED_RENAMED.h`) | Working-tree edit alone | `test_consuming_suites_still_include_the_fixture`: "…no longer includes _shared/eprom_v131_expected.h…" | blob-sha, names, entry-counts, non-vacuous, git-required (5/6) |

No break reddened more than one leg — the five mechanisms are independent, not merely five assertions
riding on one shared check.

**Restoration, scoped per the plan's own anti-pattern warning** (never "empty git diff" / "byte-identical
file" — a criterion a later `#if` guard would break): after each restore, (a) the fixture's blob SHA
(`git hash-object`) equalled its pre-break value `ca3e09f164e6e1c541ecb63d15bbebf5bce41d70`, (b) the gate
reported 6 passed, and (c) `pytest --collect-only` on the module still named the same six test functions,
same count, both before and after. Leg 1's temporary probe commit was undone with `git reset --soft
HEAD~1` (moving `HEAD` back without touching the index) followed by `git checkout HEAD --
<path>` (restoring the working tree AND index from the now-correct `HEAD`, not from the still-stale
index — `git checkout -- <path>` alone would have restored from the index, which still held the
perturbed content; this was caught and corrected live). Legs 2 and 3 were undone with a plain
`git checkout HEAD -- <path>`. `git -C /workspaces/firestarter status --porcelain` was empty after every
restore.

### Full firmware green state, re-measured after the freeze

| Measurement | Command | Result |
|---|---|---|
| `native` | `pio test -e native` | **141 test cases: 141 succeeded**, 17/17 suites PASSED |
| `native_nodevtools` | `pio test -e native_nodevtools` | **141 test cases: 141 succeeded**, 17/17 suites PASSED |
| `native_pinmap_provisional` | `pio test -e native_pinmap_provisional` | **10 test cases: 10 succeeded**, 1/1 suite PASSED |
| `native_trace_v131` (cold) | `rm -rf .pio/build/native_trace_v131 && pio test -e native_trace_v131` | **5 test cases: 5 succeeded**, 1/1 suite PASSED (2 smoke + 3 protocol cases, each now asserting full positional equality) |
| firmware python gate suite, **in place** | `python3 -m pytest tests/ -q` (inside `/workspaces/firestarter`, meta repo present at `/workspaces`) | **227 passed, 0 failed, 0 skipped** — 221 pre-existing (§"Measured Baseline", this record) + 6 new from this plan's own `test_golden_trace_identity_eprom_v131.py` |

The `native`/`native_nodevtools`/`native_pinmap_provisional` figures are byte-identical to this record's
own §"Measured Baseline" table — the freeze changed nothing outside `test/native/avr/_shared/
eprom_v131_expected.h`, `test/native/avr/test_trace_eprom_v131/test_trace_eprom_v131.cpp`,
`tests/golden/eprom_v131_trace_inventory.json`, and `tests/test_golden_trace_identity_eprom_v131.py` — no
pinned native env's suite count moved. **The measurement location is part of the figure, restated from
§3 of this record:** the firmware python gate suite's git-history and meta-presence checks resolve
correctly only when run inside a real checkout with the meta repo present as a sibling — the same 7 gates
this record already named would fail in a detached tree. "In place" is therefore the only honest
location for the 227 figure, exactly as it was the only honest location for the 221 figure this record
measured under Plan 03.

`git -C /workspaces/firestarter status --porcelain src/` was empty throughout Plan 05's Task 3 work —
no write-path source was read as anything but read-only evidence, matching this record's §7 statement for
Plan 03.

---

*Phase: 138-preconditions-baseline — Plan 05, Task 3*
*Recorded: 2026-08-09, from live measurements taken this session: three deliberate break-and-restore
cycles against the live `test_golden_trace_identity_eprom_v131.py` gate, and a full re-run of every
pinned native environment plus the firmware `tests/` suite, in place, inside `/workspaces/firestarter`.*
