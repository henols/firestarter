# Phase 83: UV-EPROM Write Proof (gated on Phase 81 blank-state) - Context

**Gathered:** 2026-06-24
**Status:** Ready for planning

<domain>
## Phase Boundary

Validate the **write path for the UV-EPROMs** without an eraser — spend-vs-preserve decided
**per chip live at the bench** from the Phase 81 blank-state. Every UV write is **irreversible**
(operator has no UV eraser), so reads + blank-check ALWAYS precede any write (UV-01,
non-destructive-first).

**The 3 UV parts and their Phase 81 gating blank-states (the load-bearing input):**
- **ST M27C512 (0x07, UV-EPROM): BLANK** — stable all-`0xFF`, N=3 byte-identical, read path trusted.
- **AM27C020 (0x08, UV-EPROM): NOT-BLANK** — data present (`0x02@0x0000`), N=3 byte-identical, read trusted.
- **2516 (0x0B Legacy, NMOS, UV-EPROM): NOT-BLANK but READ-UNSTABLE** — 3 distinct SHAs across
  N=3 + 2 reseat cycles, VPP pinned 15.3V<25V on the shared OE/VPP pin (0x0B-specific). Phase 81
  explicitly gated Phase 83: *MUST NOT write or preserve-dump until the read path is stable.*

**Scope as decided in this discussion (D-01) — IMPORTANT, this narrows the roadmap's stated scope:**
- **In scope:** the **2 read-stable UV chips** (ST M27C512, AM27C020) — read + decode validation
  (UV-04) and a **write proof on the parts the operator spends** (UV-02/UV-03), captured in
  EVIDENCE. Board = **Leonardo + RURP Rev 2.0 ONLY**.
- **Out of scope / deferred to Phase 84:** **the entire 2516** — its write proof (GRAD-03), the
  VPE-rail bench proof (SC#4), and closing FUT-03 all move to Phase 84, *after* FIX-01
  root-causes the 0x0B read-path VPP instability. The 2516 is **not written, not re-read, and
  not preserve-dumped** in Phase 83 (its read+decode was already attempted in Phase 81 → ANOMALY).
- **Also out of scope:** the consolidated decode audit + defect RCA (Phase 84 / FIX-01); the v1.9
  read-bug RCA (deferred); any new harness or third-party dep (reuse-first).

**Consequence to flag for the planner / roadmap:** with the 2516 deferred, Phase 83 **cannot
satisfy SC#4 (2516 bench-proven) or GRAD-03 as written** — those become Phase 84 deliverables.
FUT-03 stays OPEN until Phase 84 (still within v1.15, since Phase 84 is the last phase). The
planner should map Phase 83's success criteria to the 2 stable chips only and record the
GRAD-03/SC#4/FUT-03 handoff to Phase 84 explicitly (a roadmap note may be warranted).
</domain>

<decisions>
## Implementation Decisions

### 2516 read-stability gate — defer the ENTIRE 2516 to Phase 84
- **D-01:** The 2516 read is UNSTABLE (Phase 81: 3 SHAs, VPP 15.3V, 0x0B-specific). Rather than
  attempt bench stabilization in Phase 83, **defer the entire 2516 to Phase 84** — no write, no
  preserve-dump, no re-read attempt in this phase. GRAD-03 (2516 VPE-rail write proof), SC#4
  (2516 bench-proven), and the FUT-03 close all move to Phase 84, contingent on **Phase 84 FIX-01
  root-causing and fixing the 0x0B read-path VPP instability** so the read oracle becomes
  trustworthy. Rationale: the 2516 is **irreplaceable**; writing/dumping it on an untrusted read
  path risks consuming it for a **vacuous** PASS (can't SHA-verify against a jittering read,
  violates the EVID-03 non-vacuous bar). The fix belongs with the FIX-01 RCA, not a bench gamble.
- **D-02:** Phase 83 therefore covers **only the 2 read-stable UV chips** (ST M27C512, AM27C020).

### Spend-vs-preserve lean — spend the 2 commodity UV parts, preserve nothing-to-preserve
- **D-03:** **Default lean = SPEND** the 2 in-scope UV parts to obtain real write proofs (they are
  replaceable commodity parts; the irreplaceable 2516 is the one being protected, and it is
  already deferred per D-01). The operator still makes the **explicit per-chip spend-vs-preserve
  call live at the bench** (UV-02) — the lean is the planner's pre-bias, not an override of the
  operator's bench authority. Each decision (spend or preserve) is recorded per chip in EVIDENCE.
- **D-04:** Non-destructive-first ordering is **non-negotiable** (UV-01): for each chip, the
  Phase 81 blank-state is re-confirmed / current contents recorded **before** any write, and the
  operator authorizes the spend at the bench before VPP is applied.

### Write-proof method per blank-state (UV-03)
- **D-05 — ST M27C512 (BLANK) → full known image.** Spend = write a **full-chip-size deterministic
  pseudo-random image** (the Phase 82 method), verify read-back **SHA == image SHA**. A blank part
  takes a full image cleanly; this is the strongest proof (every address line + bit pattern
  exercised). Reuse `tools/gen_test_image.py` (Phase 82 D-03/D-04) to generate the 64KB image.
- **D-06 — AM27C020 (NOT-BLANK) → all-`0x00` full wipe.** Spend = write **all-`0x00`** over the
  entire chip (proves every currently-`1` bit can be driven `1→0`, the only legal transition on a
  UV part without erase), verify read-back **SHA == SHA(all-`0x00` image)** of size `0x40000`
  (262144). Operator chose the simple full-wipe over a partial AND-mask: unambiguous PASS,
  exercises every cell, and the read path is trusted so the verify is valid.
- **D-07:** The verify oracle for both is a **read-back SHA match on the trusted Leonardo read**
  (N≥3 byte-identical per the non-vacuous bar) — AM27C020 and ST M27C512 both read stably in
  Phase 81, so their write proofs CAN be SHA-verified (unlike the 2516).

### 2516 VPE-rail PASS bar — defined now, applied in Phase 84 (per D-01)
- **D-08:** When the 2516 write proof runs **in Phase 84** (after FIX-01 stabilizes its read), the
  PASS bar is: a clean **read-back SHA match** on the spent image (after a stabilized N≥3 read)
  counts as PASS; the firmware **under-voltage warning** (~22.4V VPE < 25V NMOS spec) is captured
  **verbatim** in EVIDENCE and the result recorded as **best-effort** (per v1.14 D-07).
  **Over-voltage stays blocked throughout** (SC#5). Achieving this closes FUT-03 (best-effort).
  This decision is recorded here so Phase 84 inherits the bar without re-discussion.

### Carried forward from Phase 81 / 82 / milestone (locked — not re-discussed)
- **D-09 — Board lock:** **Leonardo + RURP Rev 2.0 ONLY** is authoritative for any write/verify
  (SAFE-01/03). Per task: verify `controller:` port identity after any USB event, live
  `r1 ≈ 270000` readback, **ASK the operator which silkscreen shield rev is mounted** (EEPROM byte
  can't distinguish revs). Leonardo is **chip-OUT-sideload-EXEMPT**. (Phase 82 D-10.)
- **D-10 — SAFE-02:** host suite green **including the 0xA4 `ack_data=False` guard**
  (`test_init_phase_data_frames_not_acked`) before any bench session; validate `ruff check` +
  `ruff format --check` against the CI target (devcontainer Py3.12 masks CI py3.9/3.11). (Phase 82 D-11.)
- **D-11 — Reuse-first, no new harness (EVID-02):** `dev write-cycle <chip> <image>`
  (Erase→write→read-back N, SHA assert, 3-way verdict), `dev consistency-check --runs 3` (read
  oracle), `tools/gen_test_image.py`, `write_test.sh`. The only new artifact is the per-chip
  EVIDENCE append. (Phase 82 D-12.)
- **D-12 — EVIDENCE.{md,json}** at `.planning/v1.15/bench/` **extends** the Phase 81/82 rows with
  the UV write-proof rows; carries the locked columns (chip, family/algorithm, board+shield,
  blank-state, spend-vs-preserve decision, op, SHA-or-N/A, verdict, anomalies). (Phase 82 D-13.)
- **D-13 — Non-vacuous PASS bar (EVID-03, locked):** every PASS proven by a trustworthy Leonardo
  read (**N≥3 byte-identical / SHA-matched**) plus a **negative control** (a wrong-file `verify`
  exits non-zero). (Phase 82 D-14.)
- **D-14 — Write-failure disposition:** on a failed write→verify, **reseat + retry up to N=2**,
  then record FAIL (genuine defect) or ANOMALY and CONTINUE; genuine defects flagged for Phase 84
  FIX-01, not root-caused inline. (Phase 82 D-08.) Note: a UV part, once spent, cannot be
  re-blanked — a "retry" re-writes the same all-`0x00`/image, which is idempotent for these proofs.

### Claude's Discretion
- Exact pseudo-random image generator seed for ST M27C512 + storage location (carry Phase 82 D-04;
  `tools/gen_test_image.py` already produces deterministic full-size images).
- Whether to drive writes via `dev write-cycle` (per-chip, explicit source image — natural fit) vs
  `write_test.sh`; either satisfies the reuse-first bar.
- Per-chip vs single shared negative control (Phase 81/82 fired one; either satisfies EVID-03).
- Whether to re-confirm each chip's Phase 81 blank-state with a fresh read before the spend, or
  rely on the recorded Phase 81 state (UV-01 requires the operator authorize at the bench either way).

### Folded Todos
None folded — see Reviewed Todos in Deferred Ideas.
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope & requirements
- `.planning/ROADMAP.md` §"Phase 83: UV-EPROM Write Proof" — goal + 5 success criteria;
  §"Non-destructive-first safety ordering"; §v1.15 "Bench discipline". **Note the D-01 scope
  narrowing**: SC#4/GRAD-03 (2516) move to Phase 84.
- `.planning/REQUIREMENTS.md` — UV-01, UV-02, UV-03, UV-04, GRAD-03 (Phase 83 reqs as written);
  EVID-01/02/03 (the evidence/non-vacuous/reuse contract); FUT-03 tracker line (closed-by GRAD-03,
  now via Phase 84 per D-01)
- `.planning/PROJECT.md` §"Current Milestone: v1.15" — milestone goal + Leonardo+Rev2.0 board lock
- `.planning/STATE.md` §"Standing bench precondition" — Leonardo+Rev2.0-only, `r1 ≈ 270000`,
  port-identity-per-task, ASK silkscreen rev, reuse-first, EVIDENCE path

### The gating blank-states (THE load-bearing input from Phase 81)
- `.planning/v1.15/bench/EVIDENCE.md` §"UV-EPROM Gating Blank-States" + §"Phase 83 Gate / Phase 84
  FIX-01" + the 11-row sweep table (rows 9/10/11 = ST M27C512 / AM27C020 / 2516) — the blank-states
  and the 2516 read-instability finding that drives D-01
- `.planning/v1.15/bench/EVIDENCE.json` — machine-readable mirror; Phase 83 appends write rows here

### Prior phase context (directly load-bearing)
- `.planning/phases/82-electrically-rewritable-silicon-validation/82-CONTEXT.md` — the write-proof
  protocol, A→B method, `gen_test_image.py`, reseat/retry/FAIL-vs-ANOMALY disposition (D-08/D-09),
  EVIDENCE schema (D-13), non-vacuous bar (D-14), board lock (D-10) — all carried into Phase 83
- `.planning/phases/81-2516-db-entry-non-destructive-read-sweep/81-CONTEXT.md` — spend-vs-preserve
  framing (D-08: gating blank-state recorded only for the 3 UV parts), the 2516 entry, SAFE-01/02/03
- `.planning/phases/81-2516-db-entry-non-destructive-read-sweep/81-2516-SAFETY-REVIEW.md` — the
  manual safety review of the 2516 user-override (relevant when Phase 84 picks up the 2516 write)

### 2516 graduation + the VPE/0x0B write path (Phase 84 inherits; recorded for D-08)
- `.planning/phases/79-25v-nmos-ceiling-raise/79-CONTEXT.md` — v1.14 D-07 best-effort NMOS
  graduation (ceiling 22000→25000), VPP→VPE-as-VPP path, ~22.4V VPE rail, under-voltage
  warn-and-proceed (the basis for the D-08 PASS bar)
- `firestarter/include/firestarter.h` — `CMD_READ_VPE 12`, `FLAG_VPE_AS_VPP 0x10` (the VPE-as-VPP
  routing for the 0x0B 2516 write); ↔ `firestarter_app/firestarter/constants.py`
  (`COMMAND_READ_VPE`, `FLAG_VPE_AS_VPP 0x10`) — parity pair
- `firestarter/src/proms/eprom.cpp` + `firestarter/src/proms/memory.cpp` — the 0x0B/EPROM write +
  VPP/VPE check path (the under-voltage-warn-and-proceed source)
- `~/.firestarter/database.json` — the 2516 user-override entry (algorithm 0x0B, pinout DIP24_2716,
  UV-EPROM, vpp_mv 25000, size_bytes 2048) — bypasses `check_dispatch.py`/`diff_db.py`

### Write/verify tooling (reuse — EVID-02)
- `firestarter_app/tools/gen_test_image.py` — deterministic full-size image generator (Phase 82
  artifact) for the ST M27C512 full-image proof (D-05)
- `firestarter_app/firestarter/cli_handlers.py` — `dev write-cycle` (~1139, write-proof driver),
  `dev consistency-check` (~1049, read oracle for the N≥3 verify)
- `firestarter_app/firestarter/eprom_operations.py` — `write_cycle_eprom`, read/verify/blank-check
- `firestarter_app/write_test.sh` — integration script
- `firestarter_app/firestarter/chip_resolver.py` — `resolve_chip` (the 2 UV chips must pass as
  `supported`; ST M27C512 = 0x07 built-in, AM27C020 = 0x08 built-in)

### DB decode confirmation (UV-04) + safety gates
- `firestarter_app/firestarter/data/chip_database.json` — DB decode for ST M27C512 (0x07) +
  AM27C020 (0x08) to confirm vs silicon (UV-04 decode validation)
- `firestarter_app/tools/check_dispatch.py` + `tools/diff_db.py` — VPP-safety + diff gates (cover
  the 2 built-in UV chips; do NOT cover the 2516 override — but the 2516 is deferred)

### Standing bench precondition (EVERY hardware task — SAFE-01)
- `.planning/STATE.md` §"Standing bench precondition" + `.planning/ROADMAP.md` §v1.15 "Bench
  discipline" — Leonardo + Rev 2.0 only; `r1 ≈ 270000`; verify `controller:` port identity per
  task; ASK silkscreen shield rev; host suite green incl. 0xA4 guard before session
</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `tools/gen_test_image.py` — produces the deterministic full-size 64KB image for the ST M27C512
  blank-part write proof (D-05). For AM27C020 the "image" is a trivially-generated all-`0x00`
  buffer of 262144 bytes (D-06) — no random gen needed.
- `dev write-cycle <chip> <source_image>` — write→read-back→SHA-assert driver; the natural proof
  substrate (ST M27C512 with the random image; AM27C020 with the all-`0x00` image).
- `dev consistency-check --runs 3` — the non-destructive N≥3 read oracle (EVID-03 non-vacuous bar)
  used to confirm the read-back is byte-stable before trusting the verify SHA.

### Established Patterns
- ST M27C512 (0x07) and AM27C020 (0x08) are **built-in DB entries** → `check_dispatch.py` /
  `diff_db.py` cover them; UV-04 decode validation is a real-silicon confirmation of a gated decode.
- A UV part is **single-shot**: once spent there is no re-blank (no eraser). All-`0x00` and the
  full random image are both irreversible writes — the operator's bench spend authorization (D-04)
  is the hard gate before VPP is applied.
- Tooling gate: `ruff check` + `ruff format --check` + `pytest --cov-fail-under=70`; devcontainer
  Py3.12 masks CI py3.9/3.11 — validate ruff against the target before claiming green (D-10).

### Integration Points
- The 2516 (deferred) write would exercise `electrical.type` UV-EPROM 0x0B → VPP→VPE-as-VPP
  (`FLAG_VPE_AS_VPP 0x10`) → `CMD_READ_VPE` → ~22.4V VPE rail → firmware under-voltage warn +
  proceed. **No code change needed** — the 0x0B chip auto-uses the VPE rail (project_phase79). This
  is Phase 84's path, recorded here for the D-08 PASS bar.
- ST M27C512 / AM27C020 writes use the standard 0x07 / 0x08 VPP (12V) write path — no VPE rail,
  no NMOS best-effort caveat. Their proofs are clean full-spec PASSes (unlike the 2516).
</code_context>

<specifics>
## Specific Ideas

- The operator prioritized **protecting the irreplaceable 2516** over forcing a write proof on an
  untrusted read path — deferring it to Phase 84 where FIX-01 fixes the 0x0B read first, rather
  than gambling the part on a vacuous bench attempt.
- The operator leans toward **spending the 2 commodity UV parts** (ST M27C512 full image, AM27C020
  all-`0x00`) to get genuine write-path evidence, since they are replaceable — but the explicit
  spend call stays a live bench decision per chip (UV-02).
- All-`0x00` chosen for the not-blank AM27C020 over a partial AND-mask: simplest, exercises every
  cell, unambiguous `1→0` proof, and read-back SHA verify is valid because its read path is trusted.
</specifics>

<deferred>
## Deferred Ideas

- **The entire 2516 write proof (GRAD-03), VPE-rail bench proof (SC#4), and FUT-03 close** — moved
  to **Phase 84**, contingent on FIX-01 stabilizing the 0x0B read path. The D-08 PASS bar is
  pre-recorded for Phase 84 to inherit. (This is the central D-01 decision, not scope creep — it's
  a reassignment within the milestone.)
- **0x0B read-path VPP-instability RCA** — Phase 84 FIX-01 (the root cause of the 2516 read jitter
  + the chip-1 boot VPP refusal family).
- **Consolidated decode-correctness audit + conditional defect RCA + milestone evidence
  consolidation** — Phase 84.

### Reviewed Todos (not folded)
- `2026-06-24-skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads.md` (score 0.9) — **NOT
  folded.** It targets the read/blank-check VPP gate that is at the heart of the 0x0B 2516 read
  instability, but its `resolves_phase` is **Phase 84 FIX-01**, and the 2516 itself is deferred to
  Phase 84 (D-01). It travels with the 2516 deferral, not into Phase 83.
- `flash4-page-size-datasheet-sourced-cr01.md` (score 0.6) — Phase 84 (W29C040/W29C020 flash4),
  unrelated to UV parts.
- `avrdude-mcu-detection-fallback.md` / `cobs-decoder-framelevel-deadline-wr01.md` (score 0.6) —
  off-board recovery / transport-layer firmware items, unrelated to Phase 83.

None of the above are scope creep — they are explicitly later phases / future items.
</deferred>

---

*Phase: 83-uv-eprom-write-proof-gated-on-phase-81-blank-state*
*Context gathered: 2026-06-24*
