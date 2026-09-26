# Phase 117: FIX — remap-aware `0x0D` emitter + honest completion signal - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-28
**Phase:** 117-FIX — remap-aware `0x0D` emitter + honest completion signal
**Areas discussed:** RED→GREEN mechanics, Completion signal (FIX-02), Partial-write poll (FIX-06), Emitter construction + declined hook, Page size (escalated from the emitter area)

---

## RED→GREEN mechanics

Opened with a finding from reading the parked suite: Phase 116's D-01 promise that "Phase 117's
one-line addition of that suite to the allowlist IS the RED→GREEN proof" does not hold. Two
structural conflicts — `drive_write_init` mocks `firestarter_set_data` to a no-op (so a FIX-01
emitter built on that pointer records an empty stream), and cases 1-5 assert
`RESPONSE_CODE_ERROR`, which FIX-02 deliberately removes.

### Q1 — resolving the mocked-out `set_data`

| Option | Description | Selected |
|--------|-------------|----------|
| Un-mock set_data in the suite | Keep only the get_data mock; drop the set_data mock from both drive helpers and cases 6-7. Makes the suite's two halves consistent — its own reference emitter already drives the real `memory_set_data`. | ✓ |
| Emitter calls memory_set_data directly | Zero test edits, but production code shaped by a test mock; contradicts FIX-01's stated wording; leaves the emitter unmockable for Phases 118/119. | |
| You decide | Defer to researcher/planner with the no-test-shaped-production-code constraint recorded. | |

**User's choice:** Un-mock set_data in the suite
**Notes:** Became CONTEXT D-01.

### Q2 — where TRACE-06's INIT-abort evidence survives

| Option | Description | Selected |
|--------|-------------|----------|
| Flip + add severity-preservation case | Flip the five to assert no-error; add one permanent case proving a future unconditional `response_code` overwrite fails (the v1.16 CR-01 fork). Frozen record stays in 116-PREMISE.md + RED-BASELINE.md. | ✓ |
| Flip only | Smallest diff; rely on case 7 once green plus the committed markdown record. | |
| Keep an executable frozen replica | Strongest retention, but a second copy of deleted production code that can rot silently. | |

**User's choice:** Flip + add severity-preservation case
**Notes:** Became CONTEXT D-02.

### Q3 — proving the flip is real, not "edited until green"

| Option | Description | Selected |
|--------|-------------|----------|
| Two-commit discipline, capture the middle | Commit 1 = test_filter + suite edits only against the unfixed tree, capture verbatim RED and append to RED-BASELINE.md; commit 2 = the fix, GREEN. | ✓ |
| Single commit, cite the existing baseline | Less ceremony, but the captured "before" predates the suite edits and cannot prove the edited suite was ever RED. | |
| You decide | Leave the commit shape to the planner with a captured-artifact requirement. | |

**User's choice:** Two-commit discipline, capture the middle
**Notes:** Became CONTEXT D-03. Offered further questions (case-function renaming, whether
`test_sdp_harness` needs changes) — user chose "Next area"; both carried to Claude's Discretion.

---

## Completion signal (FIX-02)

### Q1 — what replaces `eeprom28c_wait_for_write(0x5555, 0x20)`

| Option | Description | Selected |
|--------|-------------|----------|
| t_WC delay only, no claim | Unconditional named wait returning void; no success claim possible; real proof moves to the page write's DQ7 poll. Recommended at the time. | |
| t_WC delay + DQ6 toggle-bit poll | Delay then a bounded toggle poll through `handle->firestarter_get_data` (zero strobes under the mock). Faster on a responsive part; reports "done" immediately on a part that never started. | ✓ |
| Delete the check entirely, no wait | Minimum code, but drops the t_WC guarantee — the first page write could land inside the SDP-disable internal write cycle. | |

**User's choice:** t_WC delay + DQ6 toggle-bit poll
**Notes:** Became CONTEXT D-04. Chose against the recommendation; the poll's usefulness then hinged
entirely on the exhaustion policy, which Q3 settled.

### Q2 — poll shape

| Option | Description | Selected |
|--------|-------------|----------|
| Unconditional t_WC, then poll | Always wait the full budget (10 ms once per write command, INIT runs once), then poll. Conservative with no bench part. Recommended. | |
| Poll bounded by t_WC | No unconditional delay; fault if DQ6 hasn't settled within budget. Canonical datasheet pattern, makes the poll load-bearing. | |
| You decide | Researcher picks against the datasheet wording. | ✓ |

**User's choice:** You decide
**Notes:** Became CONTEXT D-06 (Claude's Discretion), with the hard constraint that the completion
path emit zero bus traffic outside `handle->firestarter_get_data`.

### Q3 — exhaustion policy

| Option | Description | Selected |
|--------|-------------|----------|
| Never writes response_code | Advisory only; a stuck cycle surfaces at the first page write's DQ7 poll. One failure path; severity-clobbering becomes structurally impossible. | ✓ |
| Escalate only if currently OK | Severity-monotonic ERROR on exhaustion; keeps the fault visible at INIT at the cost of a second error path for one fault. | |
| Unconditional ERROR | Simplest — and precisely today's defect (RED-BASELINE case 7). | |

**User's choice:** Never writes response_code
**Notes:** Became CONTEXT D-05. Offered further questions (poll read address, iteration-bound
constant) — user chose "Next area"; carried to Claude's Discretion.

---

## Partial-write poll (FIX-06)

### Q1 — what makes a partial write fail

| Option | Description | Selected |
|--------|-------------|----------|
| DQ7-complement poll + full-page read-back verify | Separates the two jobs the single read conflates today: completion vs. data-landed. ~2× bus traffic on the write path. | ✓ |
| DQ7-complement poll only | Zero extra traffic; relies on the host's verify pass — a rejected page still reports firmware-side success. | |
| Full-page read-back verify only | Closes gh#11's symptom but leaves an equality compare doing completion-detection duty — the conflation itself. | |

**User's choice:** DQ7-complement poll + full-page read-back verify
**Notes:** Became CONTEXT D-07.

### Q2 — is the read-back always on

| Option | Description | Selected |
|--------|-------------|----------|
| Always on, no opt-out | Firmware owns the truth about its own page write. An opt-out flag is Phase 120 HOST-03 scope and firmware-before-host forbids emitting it early. | ✓ |
| Always on, but note the measured cost | Same behavior plus an explicit write-path slowdown number for Phase 118. | |
| Reuse FLAG_SKIP_BLANK_CHECK as the opt-out | No new wire constant, but overloads a flag that already carries two meanings. | |

**User's choice:** Always on, no opt-out
**Notes:** Became CONTEXT D-08.

### Q3 — proving the old poll "would have passed"

| Option | Description | Selected |
|--------|-------------|----------|
| Executable side-by-side in one test | Test-local replica of the old poll asserted to PASS the planted scenario, beside the fixed path asserted to FAIL it. Both halves run in CI forever. | ✓ |
| Fixed path only, cite the record | Smaller test; the load-bearing contrast becomes prose. | |
| You decide | Planner chooses, anti-hollow discipline as the constraint. | |

**User's choice:** Executable side-by-side in one test
**Notes:** Became CONTEXT D-09. Offered further questions (mismatch reporting detail, chunk-vs-page
read-back span) — user chose "Next area"; carried to Claude's Discretion.

---

## Emitter construction + declined hook

### Q1 — which disable table the fixed emitter drives

| Option | Description | Selected |
|--------|-------------|----------|
| Keep the local table, cross-guard both | Emitter drives `EEPROM_SDP_DISABLE`; FIX-05's guard also pins it byte-identical to `FLASH_DISABLE_WRITE_PROTECTION` so the duplication cannot silently diverge. | ✓ |
| Drop the local copy, drive the shared table | One table, but makes `0x0D` depend on the frozen shared header and cuts against Phase 119's LOCK-05. | |
| You decide | Record the identity/distinctness requirements, leave the choice to the planner. | |

**User's choice:** Keep the local table, cross-guard both
**Notes:** Became CONTEXT D-10 and D-11.

### Q2 — RED-BASELINE's declined data-direction hook

| Option | Description | Selected |
|--------|-------------|----------|
| Add the explicit call, don't widen the recorder | One `rurp_set_data_output()` in the emitter; invisible to existing goldens, so no `SDP_FIXED_*` regeneration. Recorder widening stays a Phase-118 hook. | ✓ |
| Add the call AND widen the recorder | Provable in-trace, but forces regeneration of `sdp_expected.h` and `test_sdp_harness`'s guards; Phase 116 declined it partly because the stub guards were never verified to compile. | |
| Defer both to Phase 118 | Keeps 117 minimal; leaves the direction guarantee incidental. | |

**User's choice:** Add the explicit call, don't widen the recorder
**Notes:** Became CONTEXT D-12.

---

## Page size (escalated out of the emitter area)

Started as a confirm-the-deferral question and expanded into the discussion's largest thread. Four
rounds, each driven by data gathered mid-discussion.

### Q1 — does Phase 116's PAGE_SIZE 64 deferral hold

| Option | Description | Selected |
|--------|-------------|----------|
| Deferral holds — record why | 64 on a 128/256-byte-page part is conservative, not wrong; also self-checking once the read-back lands. Recommended. | |
| Fold the per-chip page size in now | Faster writes on the 18 large parts, but `page_size` is not on the wire — needs a new field, Phase 120 scope, breaks firmware-before-host. | ✓ |
| Defer, and open a named future requirement | Hold for v1.22 but track it in REQUIREMENTS.md §Future Requirements. | |

**User's choice:** Fold the per-chip page size in now
**Notes:** Chose against the recommendation and against the stated wire-field objection. Treated as
the operator's decision; the follow-up questions then worked out how to deliver it honestly.

### Q2 — how firmware learns the page size

| Option | Description | Selected |
|--------|-------------|----------|
| Derive from mem_size in firmware | Zero wire change, mirrors `flash_5v_page_page_size`. Recommended. | |
| Settle whether a page_size wire field already exists first | v1.17 Phase 94 vs v1.22 PROJECT.md contradict each other. | |
| Revert to deferring it | — | |

**User's choice:** Free text — *"IS the page size pressent in the infoic.xml"*
**Notes:** Answered from source rather than memory. Findings: the XML **does** carry `page_size`
(field dictionary marks it CONFIRMED); `build_db.py` does **not** read it (a 2-entry curated
`_PAGE_SIZE_BY_PART` map, both `0x05` parts, no AT28C); and the wire/firmware half was never built
(`JSON_KEY_PAGE_SIZE` exists in `constants.py` with a false "Firmware sync" comment, but firmware
has no `page_size` at all). Confirmed PROJECT.md's "Established fact" and located the real gap.

### Q3 — how far Phase 117 goes

| Option | Description | Selected |
|--------|-------------|----------|
| Firmware-local mem_size band table now | Honours the fold-in decision with zero cross-repo reach. Recommended. | |
| Build the full XML→DB→wire→firmware path | Architecturally right long-term; spans three repos, needs CMD/field lockstep that is Phase 120 scope, regenerates `chip_database.json` against CLOSE-01's diff_db identity requirement. | ✓ |
| Band table now + open the XML path as its own phase | — | |

**User's choice:** Build the full XML→DB→wire→firmware path
**Notes:** Reaffirmed the aggressive direction after the objections were stated a second time.
Accepted as the operator's decision; work then shifted to scoping it safely.

### Q4 — decode scope, and the W29C040 precedence risk

| Option | Description | Selected |
|--------|-------------|----------|
| 0x0D only, curated map untouched | Keeps FIX-04's byte-identical guarantee true by construction. Recommended. | |
| Whole DB, curated map wins on conflict | Uniform, but adds the field to non-`0x0D` rows mid-milestone. | |
| Whole DB, XML wins on conflict | Simplest rule; risks overwriting W29C040's datasheet-cited 256 on the one `0x05` part with bench history. | ✓ |

**User's choice:** Whole DB, XML wins on conflict
**Notes:** The stated risk was then **settled empirically** by fetching the pinned `infoic.xml`
(commit `a8efaedc`, 17 MB): XML gives W29C040 = `0x0100` (256) and W29C020 = `0x0080` (128) —
identical to the curated datasheet values. The precedence rule is an empirical no-op for the `0x05`
family, so the concern was retired rather than carried. The same scan found AT28C040 = `0x0080`
(128), not the 256 assumed earlier, and — scoped to `<database type='INFOIC2PLUS'>`, the only
section `build_db.py:450` reads — only **14** DIP rows carry `protocol_id == 0x0D` against the DB's
**84** `algorithm == 13` entries.

### Q5 — where the page_size work lands, given the 14-vs-84 gap

| Option | Description | Selected |
|--------|-------------|----------|
| Own phase, inserted after 117 | Keeps 117 to the SDP fix; the decode needs the provenance rule settled and collides with CLOSE-01's diff_db claim. Recommended. | ✓ |
| Stays in 117, with --research-phase | One phase, roughly double scope, risk profile shifts to a decode investigation. | |
| Stays in 117, firmware+wire only | No DB regeneration, no diff_db delta; field arrives as 0 for every chip. | |

**User's choice:** Own phase, inserted after 117
**Notes:** New information (the 14-vs-84 provenance gap) justified re-asking the scope question.
Consequence recorded in CONTEXT D-13: the XML data shows a `mem_size` band table would be **wrong**
— `AT28MC010` (128 KB) = 64 B while `AT28C010` (128 KB) = 128 B — so Phase 117 keeps `PAGE_SIZE 64`
as a documented conservative floor and does *less* work, not more.

### Q6 — sentinel policy

| Option | Description | Selected |
|--------|-------------|----------|
| 0x0000 and 0x0001 both mean "fall back" | Matches the field dictionary's "not applicable to the device type" wording and the existing absent→heuristic contract. | ✓ |
| Honour 0x0001 as true byte-write mode | Arguably honest for AT28C64 non-B / AT28C16 (no page buffer), but ~80 s for an 8 KB write and a large unvalidated change with no bench part. | |
| You decide | — | |

**User's choice:** 0x0000 and 0x0001 both mean "fall back"
**Notes:** Recorded as a locked decision for the new phase, not for 117.

---

## Claude's Discretion

- The `t_WC`/DQ6 poll shape (delay-then-poll vs. deadline-bounded) and the poll's read address — 
  explicitly delegated by the user, with the zero-extra-strobes constraint recorded.
- Whether to rename the five case functions whose names post-fix assert the opposite of what they
  test.
- The emitter's exact signature/name, shaped for Phase 118 and 119 reuse.
- Where FIX-05's terminal-byte guard lives (`test_sdp_harness` vs the newly-enabled suite).
- Where FIX-06's partial-write test lives, and the planted mock's exact shape.
- Whether the read-back's mismatch path reports the failing address per byte.
- Whether the read-back spans the current chunk or the whole physical page.

## Deferred Ideas

- **NEW PHASE (not yet in ROADMAP.md): end-to-end `infoic.xml` `page_size` decode** — full spec,
  locked decisions, and four research open questions in CONTEXT `<deferred>`. Insert with
  `/gsd-phase`; needs `--research-phase`.
- Widening the trace recorder to a third strobe kind (data-bus direction) — Phase 118 hook.
- Unity-teardown SIGABRT root cause (`test_flash_intel_vpp`) — pre-existing debt since Phase 17.
- Recording every side-effecting `rurp_*` call — rejected half of Phase 116's D-07.
- All-84-chips table-driven trace coverage — rejected half of Phase 116's D-09.
- `DIP24_2816`'s missing `static-high-pins` key (SDP-F8, 19 chips) — observe only, do not act.
- Datasheet verification of SDP magic addresses per size band (SDP-F7) — two of three cited PDFs
  are absent from the tree.
