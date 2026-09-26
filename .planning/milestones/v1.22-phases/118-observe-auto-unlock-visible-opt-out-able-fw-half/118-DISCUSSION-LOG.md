# Phase 118: OBSERVE — auto-unlock visible + opt-out-able (FW half) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-28
**Phase:** 118-observe-auto-unlock-visible-opt-out-able-fw-half
**Areas discussed:** Report-line visibility class; What the duration covers + where the after-line sits; What `AT28C_TBLC_MAX_US = 100` actually does; OBS-04's "on at least one board"

**Gray areas offered but not selected for discussion:** none — the operator selected all four
presented areas.

---

## Report-line visibility class

### Q1 — On a plain `firestarter write at28c256` (no flags), should the two SDP report lines be visible?

| Option | Description | Selected |
|--------|-------------|----------|
| Both unconditional | `LOG_ID`/`LOG_ID_U32` with new INFO-band ids. First non-verbose-gated INFO-band call sites in the tree (all 19 today use `LOG_INFO_ID*`). Makes OBS-05's byte-identical claim real rather than vacuous. | ✓ |
| Both verbose-gated (house style) | `LOG_INFO_ID*` like `MSG_INFO_SKIPPING_ERASE`. Zero new frames on a default write, but "observable" degrades to "observable with `-v`". | |
| Before unconditional, duration verbose-gated | Always-visible "unlock ran" line; `micros()` number only under `-v`. Mixed convention inside one function. | |

**User's choice:** Both unconditional → **D-01**
**Notes:** Rationale accepted as stated — silence is the defect being fixed, so a decision that
leaves the default path quiet is a no-op rather than a smaller version of the phase.

### Q2 — When `FLAG_SKIP_SDP_UNLOCK` is set and firmware skips the sequence, what does it report?

| Option | Description | Selected |
|--------|-------------|----------|
| WARN line, `response_code` untouched | New WARN-band id replacing the before/after pair. Honest about the consequence without fabricating an operation-level warning; preserves Phase 117's D-05. Precedent: `MSG_WARN_FL4_BOOT_BLOCK_LOCKED`. | ✓ |
| INFO line (mirrors skipping-erase) | Exact `MSG_INFO_SKIPPING_ERASE` shape (`flash_5v_page.cpp:70`). Closest in-tree analog, but `write -b` silently skipping erase is the footgun v1.16 Phase 92 had to fix. | |
| WARN + `response_code = WARNING` | Host surfaces it in the result, not just the log stream. Warns on every skip even when harmless, and breaks D-05. | |

**User's choice:** WARN line, `response_code` untouched → **D-02**

### Q3 — New `MSG_*` ids force a three-repo codegen ritual. How is that owned?

| Option | Description | Selected |
|--------|-------------|----------|
| Own it as an explicit plan | Meta `messages.toml` → `sync_to_subrepos.sh` → regenerate firmware `messages.h` + host `messages.py` → verify `catalog-sync-check.yml` + both `codegen.py --check`. Named because Phase 117's failure was an unowned cross-repo step. | ✓ |
| Stay firmware-only by reusing existing ids | No `messages.toml` change. But no existing id fits, and every DBG_* path is verbose-gated, reversing D-01. | |
| Catalog now, host regen in Phase 120 | Leaves `catalog-sync-check.yml` RED across two phases. | |

**User's choice:** Own it as an explicit plan → **D-03**
**Notes:** Confirms Phase 118 writes into `firestarter_app`. Firmware-before-host holds because the
host delta is generated code plus a gate rewrite — no CLI flag, no wire emission.

### Q4 — Generic report ids with an unlock/lock param, or SDP-unlock-specific ids?

| Option | Description | Selected |
|--------|-------------|----------|
| Unlock-specific ids now | Phase 119 adds its own lock pair. Matches the catalog's own precedent: `MSG_INFO_SKIPPING_ERASE` and `_MEM` are two ids, not one parameterised id. | ✓ |
| Generic pair with an operation param | Two entries instead of four, one render path — but the format string becomes "SDP operation %u", less legible in a log. | |
| You decide | Leave to Claude, constrained by Phase 119 extensibility. | |

**User's choice:** Unlock-specific ids now → **D-04**

---

## What the duration covers + where the after-line sits

### Q1 — What should OBS-04's `micros()` duration actually measure?

| Option | Description | Selected |
|--------|-------------|----------|
| The 6 command writes only | Bracket the emitter. Directly comparable to the t_BLC budget, firmware-controlled, genuinely board-dependent. `t_WC` is a fixed delay and the poll is iteration-bounded, so including them adds a constant plus noise. | ✓ |
| Whole unlock: emit + `t_WC` + DQ6 poll | User-visible total, but ~10 ms is a hardcoded delay and the poll count varies — stops being a measurement of the emitter. | |
| Both — two numbers on the after-line | Most informative; one extra u32 on the wire. | |

**User's choice:** The 6 command writes only → **D-05**

### Q2 — How do we resolve the after-line vs. the gate's window definition?

| Option | Description | Selected |
|--------|-------------|----------|
| Redefine the window as the emitter's body | Today's gate scans the span *between* the two call sites and never looks inside the emitter loop where the real inter-byte window is. Rewrite to brace-match the emitter + completion-poll bodies. OBS-03's claim finally means what it says. | ✓ |
| Keep the gate; log after the wait | Gate passes byte-unchanged and matches SC4's literal wording, but the number describes the emit while appearing after the wait, and the gate keeps not scanning where timing matters. | |
| Both — widen the window AND log after the wait | Strictest reading, most work; Phase 119 inherits the widened call-site constraint too. | |

**User's choice:** Redefine the window as the emitter's body → **D-06**
**Notes:** Surfaced during the exchange and accepted as an owned task rather than a footnote: the
existing planted fixture (`tests/fixtures/planted_log_in_window.cpp`) plants its `LOG_` between the
call sites, so under the new definition the checker returns 0 on it — the gate goes hollow and its
paired pytest goes RED unless the fixture is re-planted inside the emitter body in the same commit.

### Q3 — What exactly gets asserted byte-identical for OBS-05?

| Option | Description | Selected |
|--------|-------------|----------|
| The recorded bus stream | `SDP_FIXED_*` goldens stay byte-identical; `rurp_log_id` → Serial is invisible to the Phase-116 recorder, so the bus stream genuinely is unchanged. The two new serial frames become a named, enumerated exception. | ✓ |
| Bus stream + recorded serial-frame baseline | Machine-checks the "exactly two new frames" claim, but no serial-frame recorder exists — Phase-116-class harness work. | |
| Bus stream + flash delta + prose | Cheap, matches Phase 117's +204 B recording, but the frame count stays unverified. | |

**User's choice:** The recorded bus stream → **D-07**

### Q4 — How is OBS-02's skip proven via the trace harness?

| Option | Description | Selected |
|--------|-------------|----------|
| New empty-stream case in the `0x0D` suite | Set `ctrl_flags |= 0x100`, drive `write_init`, assert zero SDP entries — paired with the flag-absent full-stream case. | |
| New case in the always-green harness suite | Never parked, but it drives the reference emitter and `FLASH_DISABLE_WRITE_PROTECTION`, not production `write_init` — wrong seam. | |
| You decide | Claude's call, constrained to: drive production `write_init`, assert ordered stream content not counts, ship the flag-absent counterpart in the same commit. | ✓ |

**User's choice:** You decide → **D-08** (Claude's Discretion, constraints recorded)

---

## What `AT28C_TBLC_MAX_US = 100` actually does

**Framing offered before the question:** t_BLC is a maximum, not a delay. Post-117 the emitter is a
bare `set_data` loop with `pulse_delay = 0` and no inter-byte wait, so the constant cannot be
something you insert.

### Q1 — What role does the constant play in the code?

| Option | Description | Selected |
|--------|-------------|----------|
| Runtime budget check + WARN | Compare D-05's measured duration against `6 × AT28C_TBLC_MAX_US`, WARN when exceeded. Load-bearing rather than decorative; reuses OBS-04's number; should never fire, which is what a latent invariant looks like. | ✓ |
| Documentation-only constant | Zero flash, zero risk — but OBS-03's "cited at every call site" satisfied by prose alone is the hollow-gate debt shape (v1.12 GATE-03). | |
| Fold the budget into the after-line | Number and yardstick travel together with no branch; nothing fails when the budget is blown. Composes with the check. | |

**User's choice:** Runtime budget check + WARN → **D-09**

### Q2 — t_BLC also governs the page-load window. Does the constant reach that site?

| Option | Description | Selected |
|--------|-------------|----------|
| Cite at both, check only the unlock | Page-load loop gets a comment naming its shared t_BLC exposure; runtime check stays scoped to the unlock. Satisfies OBS-03 literally, keeps the hot path free of a per-byte compare, plants the flag without expanding the diff. | ✓ |
| Unlock sequence only | Tightest scope, but leaves the identical constraint undocumented at the one place gh#11 surfaces. | |
| Cite AND check both | Physically complete; puts a compare in the hot path and grows the flash delta LOCK-06 is judged against. | |

**User's choice:** Cite at both, check only the unlock → **D-10**

### Q3 — Should the widened gate also enforce the t_BLC citation?

| Option | Description | Selected |
|--------|-------------|----------|
| No-logging rule only | One job, one failure mode. Comment-text gates rot, and the checker deliberately blanks comment spans, so a citation scan needs a second pass over uncleaned text. D-09's runtime check is stronger. | ✓ |
| Add a citation-presence assertion | Machine-checks OBS-03's "cited" wording; needs the second uncleaned pass. | |
| Separate checker for the citation | Cleanest separation, most new surface — two checkers, two fixtures, two pytest files. | |

**User's choice:** No-logging rule only → **D-11**

---

## OBS-04's "on at least one board"

### Q1 — The milestone has no bench phase, yet OBS-04 wants a real `micros()` measurement. How is that satisfied?

| Option | Description | Selected |
|--------|-------------|----------|
| One real Leonardo run, no AT28C needed | The emit duration is the MCU driving its own latches — socket contents do not change it, so the validation ceiling is untouched. Makes OBS-04 the milestone's one genuinely measured claim. | ✓ |
| Ship the code, record "not measured" | Strictly software-only with zero hardware dependency, but forfeits the phase's only empirical result. | |
| Measure on both Leonardo and Uno | Strongest data; doubles the operator step and drags in board flakiness. | |

**User's choice:** One real Leonardo run → **D-12**

### Q2 — Who runs it, and what's the socket precondition?

| Option | Description | Selected |
|--------|-------------|----------|
| Claude drives it, operator confirms socket empty | One operator checkpoint, then autonomous flash + run + capture. | |
| Operator runs it and pastes the output | No ambiguity about socket state; blocks on availability, output retyped rather than captured. | |
| Claude drives with whatever is seated, `--force` | No operator step; drives a `0x0D` pinout into an unknown part with over-voltage checks relaxed. | |

**User's choice:** *Other (free text)* — "Claude drives it, dont ask for any confirmations. Leonardo
is connected with an empty socket."
**Notes:** Recorded verbatim in CONTEXT.md D-12. Consequence: the plan is `autonomous: true` and
must **not** insert a checkpoint asking about socket state. Claude still verifies `controller:`
port identity before driving the port — a Claude-side check per standing bench discipline, not an
operator confirmation.

### Q3 — Where does the measured number live so it survives the phase?

| Option | Description | Selected |
|--------|-------------|----------|
| Dedicated artifact with verbatim output | `118-MEASUREMENT.md` with the exact command, `controller:` line, board/firmware build, raw log. Mirrors `RED-BASELINE.md` and v1.15 EVIDENCE. Phase 119's LOCK-06 needs the raw number with provenance. | ✓ |
| Inline in the plan SUMMARY | Cheapest; SUMMARYs are read frontmatter-first, so a buried number is easy to miss. | |
| Add it to the PROTOCOL-LEDGER | Centrally discoverable, but the ledger records silicon verification and `0x0D` must stay `UNVERIFIED` — invites a ceiling-crossing misread. | |

**User's choice:** Dedicated artifact with verbatim output → **D-13**

### Q4 — If the Leonardo run fails at execution time, does the phase block or proceed?

| Option | Description | Selected |
|--------|-------------|----------|
| Proceed, record not-measured with the reason | Follows this project's CI-PENDING / structurally-green discipline (Phase 98/103): never fabricate a PASS for an absent tool. OBS-04 closes software-complete with the gap stated. | ✓ |
| Hard-block — no measurement, no phase close | Strongest honesty position, but makes five requirements hostage to a USB enumeration. | |
| Retry on Uno, then fall through | Best chance of a real number; drags in the Uno-class chip-OUT-before-sideload rule. | |

**User's choice:** Proceed, record not-measured with the reason → **D-14**

---

## Todo cross-reference

`todo.match-phase 118` returned 11 matches. Nine were generic keyword overlap. Two were put to the
operator as genuinely relevant:

| Option | Description | Selected |
|--------|-------------|----------|
| Neither — record both as reviewed | `fold-response-code-into-log-macro` is a cross-cutting refactor that actively conflicts with D-02; the infoic flags-14/15 protect metadata is host/DB work belonging with Phase 120 or the deferred `page_size` phase. | ✓ |
| Fold the response_code log-macro todo | Would resolve the D-02 tension by decision rather than deferral; a whole-firmware refactor with no OBS requirement behind it. | |
| Fold the infoic flags-14/15 todo | SDP-protection metadata, but reaches into `build_db.py` which no OBS requirement touches. | |

**User's choice:** Neither — both recorded as reviewed-not-folded in CONTEXT.md `<deferred>`
**Notes:** `fold-response-code-into-log-macro` was recorded as "blocked on Phase 117"; Phase 117 is
closed, so it is now blocked on Phase 118 instead — same `eeprom_28c.cpp` conflict.

---

## Claude's Discretion

- **D-08** — where OBS-02's skip-proof case lives, under three mandatory constraints (drive
  production `eeprom28c_write_init`; assert ordered stream content, never a call count; ship the
  flag-absent counterpart in the same commit).
- Exact format strings, wording, and id numbers for the four new catalog entries (INFO `0x5E+`,
  WARN `0x86+` free).
- Whether the budget is `6 × AT28C_TBLC_MAX_US` total or a per-byte average, and whether the budget
  WARN carries its own duration param.
- Native `micros()` mocking strategy (fixed value vs. controllable counter); adding a case that
  proves the budget WARN fires is recommended but discretionary.
- The before-line's exact placement — must sit after `eeprom28c_check_chip_id`'s early return.
- Whether to compose D-09's check with also reporting the budget on the after-line.

## Deferred Ideas

- **Widening the trace recorder to a third strobe kind (data-bus direction)** — Phase 117's D-12
  named this "Phase 118's owner"; explicitly **not taken**, since no OBS requirement or decision
  needs it and it would force `sdp_expected.h` regeneration.
- A **runtime** t_BLC budget check on the page-load loop (D-10 cites only).
- A citation-presence gate for `AT28C_TBLC_MAX_US` (D-11).
- A serial-frame baseline recorder so OBS-05's frame count is machine-checked (D-07).
- Measuring on the Uno as well as the Leonardo (D-12).
- A generic report-id pair with an unlock/lock discriminator (D-04) — Phase 119 may revisit.
- Carried unchanged: the end-to-end `infoic.xml` `page_size` decode phase (still not inserted into
  ROADMAP.md); Unity-teardown SIGABRT; recording every side-effecting `rurp_*` call; all-84-chips
  table-driven trace coverage; SDP-F7; SDP-F8.
