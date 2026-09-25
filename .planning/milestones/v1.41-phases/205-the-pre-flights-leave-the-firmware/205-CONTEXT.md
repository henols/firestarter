# Phase 205: The pre-flights leave the firmware - Context

**Gathered:** 2026-09-22
**Status:** Ready for planning

<domain>
## Phase Boundary

The **write-init** blank checks (`eprom.cpp`, `flash_intel.cpp`, `flash_nor_unlock.cpp`), the
**erase-end** blank check (`eprom.cpp`), the shared machinery they reach
(`mem_util_blank_check`, `mem_util_blank_check_region`, `blank_check_saved_address`,
`BLANK_CHECK_CHUNK_SIZE`) and the `FLAG_SKIP_BLANK_CHECK` (`0x08`) bit leave the firmware and
`constants.py`. The flash and RAM that frees is a **measured** number per AVR target.

**This phase is dual-repo** (`firestarter_fw` + `firestarter_app`) **and bench-gated.** It is the
second and last firmware-touching phase of v1.41 — Phase 206 is app-only and Phase 207 is a version
bump plus wiki.

**One user-facing surface loses its implementation and is re-built host-side in this phase:**
`firestarter erase -b`. Its entire mechanism is the erase-end assignment FWBLANK-02 deletes, and
nothing already delivered replaces it. See D-01…D-03. That is inside this phase's boundary, not
scope creep: the roadmap's "ordering is a safety property" rule requires the host to gain a
capability before the firmware loses it, and for the erase-end check no earlier phase did so.

**What survives permanently (D-7, milestone activation):** `memory_verify_execute`, the per-pulse
verify inside the EPROM program loop, `eeprom28c_verify_page_readback`, `flash_util_verify_operation`
and `MSG_ERR_VERIFY` (0xAF). **This phase removes pre-flight checks. It does not remove
verification.**

**What survives this phase, measured, and must not be swept with the machinery:**
`mem_util_operation_end` — after the `eprom.cpp:142` caller goes, it keeps **two** callers
(`src/eprom_operations.cpp:85` and `src/proms/eprom.cpp:323`, the write-loop denominator Phase
201-04 built). The `region-end` wire key therefore stays live for `CMD_WRITE`.

**Not in this phase:** the version bump to `3.1.0b1` (REL-01, Phase 207); the wiki breaking-change
page (REL-04, Phase 207) — which this phase hands two new obligations, see D-04 and D-02;
`dev test`'s verdict migration and the serial session lease (Phase 206); the `DONE`-based clean
stop (still filed as CMP-F1).

</domain>

<decisions>
## Implementation Decisions

### `firestarter erase -b` — the surface that would otherwise go silent

**Measured before deciding:** the erase-end blank check is wired on **exactly one** protocol family.
`configure_eprom`'s `CMD_ERASE` arm (`eprom.cpp:50-55`) assigns
`firestarter_operation_end = mem_util_blank_check` when `FLAG_SKIP_BLANK_CHECK` is clear.
`flash_nor_unlock.cpp:41` carries the same assignment **commented out**; `flash_intel.cpp:58-60`
and `eeprom_28c.cpp:152-154` never had one. And `erase` only runs on electrically-erasable parts, so
the live surface is *erasable parts riding the UV handler* — W27C512 and its siblings, exactly the
class seated on the bench rig. The CLI docstring already states the 0x0D gap
(`cli_handlers.py:1234-1237`).

- **D-01:** **`erase -b` keeps its meaning and is re-implemented on the host**, through Phase 202's
  `check_eprom_blank`. This mirrors what Phase 203 did for write: the host gains the capability
  before the firmware loses it, which is the roadmap's stated safety property rather than a
  preference. Two sub-decisions taken by precedent, not asked:
  - **Whole-device**, not region-scoped. The firmware's check was `mem_util_blank_check` → `(0,
    mem_size)`, and erase on this family is device-global — there is no region to scope to.
    Phase 203's D-04 region-scoping applied where the *write* supplied a region; this has none.
  - **Opt-in behind `-b`**, preserving today's polarity (note `erase -b` is inverted against
    `write -b`, and that inversion is unchanged) and matching D-3's opt-in stance for post-write
    verify.

  Consequence to record rather than discover: the firmware check ran inside the erase's own port
  session as `firestarter_operation_end`; the host check is a second port open, which resets an
  Uno-class board between the erase and the check. That is a wall-clock cost, not a correctness one
  — an electrically erased part stays blank across a reset. Phase 206's SESS-01 is where it
  collapses; this phase should hand it a measured number the way 203's D-17 did.
  — **Reversibility:** one-way — `erase -b` is a published CLI surface and REL-04 will document its
  new host-side mechanism in the wiki.

- **D-02:** **`erase -b` adopts the `0`/`1`/`2` exit-code contract.** `0` erased and blank, `1`
  erased but not blank, `2` transport or hardware failure during the check. Plain `erase` without
  `-b` keeps `0`/`1` unchanged. This follows Phase 203's D-13, which widened the contract to
  `write --verify` for precisely this reason, and it refuses to re-create the defect already filed
  against `dev test`'s blank step
  (`.planning/todos/pending/2026-09-20-devtest-blank-check-folds-transport-failure-into-verdict-bad.md`),
  where a transport failure reads as a chip verdict. Accepted cost, same shape 203 accepted: one
  command with two contracts, which must be stated in the `-b` help text rather than left as
  folklore.
  — **Reversibility:** one-way — exit codes are a published CLI contract; REL-04 documents them.

- **D-03:** **A failed post-erase check prints one terse line and nothing else**, mirroring Phase
  203's D-10/D-11 and the standing terse-output preference (v1.40 Phase 200 UAT rejected a
  multi-line warning for a one-line form, commit `b3a777e`). The check therefore runs in
  first-mismatch mode and **`erase` gains no `--full` option**. The documented follow-up for an
  operator who wants the full diagnosis is `firestarter blank <chip> --full`, which since Phase 202
  does exactly that and reports every coalesced mismatching range with a `classify_fingerprint`
  bucket. State that composition where the operator will read it.

  Recorded so it is not mistaken for an oversight: unlike 203's write guard — whose one-byte abort
  makes a bucket a verdict from a short prefix (202's D-09 trap) — a whole-device post-erase scan
  *would* support a well-founded diagnosis. The operator chose terseness over it deliberately, with
  the composition above as the escape hatch.

### The `FLAG_SKIP_BLANK_CHECK` bit

**Measured before deciding — five host sites read or set `0x08`:** `constants.py:129` (the
definition); `eprom_operations.py:314` in `build_flags` (sets it when `blank_check=False`, i.e.
`write -b`); `write_blank_guard.py:180` (**the Phase 203 guard's own bypass test**);
`chip_test.py:3221` (sets it for monotonic-masked UV slot writes); `serial_comm.py:639` (names it in
the debug flag dump). Firmware sites: `include/firestarter.h:161`, `src/firestarter.cpp:89`,
`eprom.cpp:52` and `:141`, `flash_intel.cpp:91`, `flash_nor_unlock.cpp:101`.

- **D-04:** **Full retirement. FWBLANK-04 stands as written** — unlike WRITE-02 (203 D-02) and
  FWCMD-05 (204 D-03), measurement does **not** contradict this requirement, it only prices it. The
  constant leaves `constants.py`, the host stops composing `0x08`, and `0x08` appears nowhere on
  either side except the reserved-gap comment. `-b` reaches the Phase 203 guard as an explicit
  host-side signal rather than a wire bit.

  **The cost, accepted knowingly at discussion rather than discovered later:** a post-205 host
  driving **pre-205 firmware** no longer suppresses the firmware's surviving pre-flight. `write -b`
  on a non-blank UV part, and `dev test`'s monotonic-masked UV slot writes
  (`chip_test.py:3221`), are refused by the old firmware where they work today. This is the
  CLI-upgrades-faster-than-firmware direction, which is the common one — `pip install -U` is easier
  than a reflash. Two obligations follow:
  - **REL-04 (Phase 207) must document that a `3.1.0` CLI wants `3.1.0` firmware for `write -b`**,
    alongside the retirement of ordinals 4 and 6. This phase files it; 207 writes it.
  - **The regression is observed on silicon in this phase, not reasoned about.** See D-07.

  A host firmware-version gate was considered and rejected here: activation decision D-4 puts one
  out of scope for this milestone, and the host structurally cannot read a firmware prerelease
  suffix (`_probe_port`'s `[\d.x]+` truncates it), so the gate would be coarse. The general form
  stays filed as `.planning/todos/pending/2026-09-20-preflight-firmware-version-compat-guard.md`.
  — **Reversibility:** one-way — a retired wire flag bit is a published protocol contract, and
  REL-04 will document it.

- **D-05:** **The reserved record takes the shape Phase 204's D-02 already pre-committed to for this
  bit.** 204 wrote, in as many words, that its ordinal record was "mirroring the shape FWBLANK-02
  already specifies for `0x08` in Phase 205" — so the shape is settled, not open: a comment at the
  gap in each ladder (`include/firestarter.h`'s control-flag block and `constants.py`'s flag block)
  naming the version the bit was retired in and why it must never be reused. The two ladders move
  in the **same commit pair**, per `/workspaces/CLAUDE.md` § Cross-repo obligations. Read
  `firestarter.h:45-66`'s existing ordinal-4 comment for the established wording shape.

  **One stale sentence this phase must correct, not inherit:** `firestarter.h:62-63` currently reads
  that the blank-check machinery "survives this retirement … and leaves in Phase 205." That sentence
  is true only until this phase lands.

### The bench (criteria 3 and 5, and the D-04 regression)

- **D-06:** **One W27C512 in two roles; `0x06` and `0x10` are test-only, and the gap is stated.**
  - **UV leg (criterion 3)** — the W27C512 is electrically erasable and carries `FLAG_CAN_ERASE`,
    but it rides the UV handler (`eprom.cpp`, protocol `0x07`), which is the file FWBLANK-01 and
    FWBLANK-02 both change. Phase 201-06's established rehearsal is the instrument: `--skip-erase`
    suppresses the erase so the blank-check shape alone decides the outcome, letting a non-blank
    state be re-created repeatably without consuming a true UV part. The mechanism is documented in
    `.planning/notes/201-region-blank-check-latency-and-divergence.md` § 1.
    **Named coverage limit, stated rather than hidden:** an erasable part stands in for a UV one.
    The code path is identical; the silicon is not.
  - **Erasable leg (criterion 5)** — the same part with the erase path on (plain `write`), which
    exercises the `FLAG_CAN_ERASE` exemption.
  - **`flash_nor_unlock.cpp` (`0x06`) and `flash_intel.cpp` (`0x10`)** — their whole-device
    write-init calls are proven removed by native test and source-contract gate, not on silicon.
    `0x10` has **zero** validated chips in the registry, so it cannot be benched regardless; `0x06`
    has exactly one (`SST39SF020`), and the Phase 201 note flags that site as "one flag deep", not
    safely latent. Record both gaps.
  — **Reversibility:** reversible — a bench method, not a contract.

- **D-07:** **The D-04 skew regression is observed on silicon, as a rider on the criterion-3
  sequence — not as a second matrix.** *(Operator answered "you decide"; decided by Claude with the
  reasoning recorded here.)* Post-205 host + pre-205 firmware, `write -b` against the same non-blank
  W27C512 the criterion-3 leg has already put in that state: capture the firmware's `Not blank`
  refusal verbatim with its exit code and duration.

  Why this is worth the leg rather than a paragraph: 204's D-08/D-09 precedent is explicit that a
  claim about what a real user sees gets observed, not argued, and REL-04 will make exactly that
  claim. The marginal cost is near zero — the part is already seated and already non-blank, the
  Leonardo is exempt from the chip-out-before-sideload rule so a firmware swap needs no hands, and
  unlike 204's D-08 the old artifact here is **not** a published wheel but simply a build of the
  current branch HEAD before this phase's commits.

  **204's D-07 label discipline applies unchanged:** neither side carries the literal `3.1.0b1`
  string until Phase 207, so "pre-205" and "post-205" are documented label substitutions and the
  phase record must name the commit sha that played each role. The host cannot tell you which
  firmware is on the board — `_probe_port`'s regex truncates the prerelease suffix — so the record
  is the only witness.

### The orphans and what the sweep actually touches

- **D-08:** **`MSG_ERR_NOT_BLANK` (0xB0) and three orphaned debug ids are KEPT and annotated, in a
  meta-repo-only docs commit.** *(Operator answered "you decide"; decided by Claude with the
  reasoning recorded here.)* This follows 204's D-06 and its executed shape, commit `694acce3
  docs(204-04)`, which annotated `messages.toml` without a codegen run or a sub-repo sync — a toml
  comment does not reach the generated artifacts.

  **0xB0 is the important one, and the measurement changes the question.** Its only firmware raise
  site is `memory.cpp:502`, inside `mem_util_blank_check_region` — so the firmware stops emitting
  it. But it is **not orphaned on the host**: a post-205 host still *receives* 0xB0 from pre-205
  firmware, in precisely the skew D-07 puts on the bench. Retiring it from `messages.py` would make
  that refusal render as an unknown id. It stays, and its `messages.toml` comment records: the
  firmware emit site retired in `3.1.0` with the blank-check machinery; the host deliberately still
  renders it for pre-`3.1.0` firmware; the id is not free for reuse.

  **`DBG_FLAG_SKIP_BLANK` (0x2E)** — measured during discussion, not previously named anywhere: its
  only emit site is `firestarter.cpp:89`, the flag dump. It becomes a third orphaned debug id
  alongside 204's `DBG_VERIFY_PROM` (0x08) and `DBG_BLANK_CHECK_PROM` (0x0B), and takes the same
  annotation. Like them it costs no AVR flash — `messages.h` is id-only and the format string lives
  host-side.
  — **Reversibility:** reversible — a catalog comment, not a contract.

- **D-09:** **Full sweep: everything reachable only from the deleted machinery goes with it.**
  *(Operator answered "you decide"; decided by Claude with the reasoning recorded here.)* This
  follows 204's D-01, whose reasoning transfers intact — a bisect should not land on a state that
  compiles dead machinery — and it is reinforced here by FWBLANK-05: a literal five-symbol removal
  would leave orphaned code and **understate the measured number the requirement asks for**.

  **The measured site list.** Re-verify each against the live tree at planning time, with `git grep`
  rather than the devcontainer's `grep` (it is ugrep and honours `.gitignore`, so a census sweep can
  silently under-scan).

  | # | Site | What it is |
  |---|---|---|
  | 1 | `firestarter_fw/src/proms/memory.cpp:434` | `blank_check_saved_address` |
  | 2 | `firestarter_fw/src/proms/memory.cpp:439` | `BLANK_CHECK_CHUNK_SIZE` |
  | 3 | `firestarter_fw/src/proms/memory.cpp:440` | `uint32_to_bytes` — **orphaned by the sweep**: its only two callers (`:511`, `:512`) sit inside the dead `RAW_DATA_PROGRESS` branch of the function being deleted. Non-static, but no header declares it and no other TU uses it |
  | 4 | `firestarter_fw/src/proms/memory.cpp:467-533` | `mem_util_blank_check_region`, including the `#ifdef RAW_DATA_PROGRESS` branch and the `MSG_DATA_PROGRESS` emitter |
  | 5 | `firestarter_fw/src/proms/memory.cpp:535-537` | `mem_util_blank_check` |
  | 6 | `firestarter_fw/include/memory_utils.h:18`, `:36-40` | both declarations and their doc comments |
  | 7 | `firestarter_fw/src/proms/eprom.cpp:52-54` | the `CMD_ERASE` arm's blank-check assignment (FWBLANK-02) |
  | 8 | `firestarter_fw/src/proms/eprom.cpp:141-143` | the write-init region call (FWBLANK-01) |
  | 9 | `firestarter_fw/src/proms/flash_intel.cpp:91-93` | whole-device write-init call (FWBLANK-01) |
  | 10 | `firestarter_fw/src/proms/flash_nor_unlock.cpp:101-103` | whole-device write-init call (FWBLANK-01) |
  | 11 | `firestarter_fw/src/proms/flash_nor_unlock.cpp:41` | the commented-out `memory_blank_check` assignment — a dead reference to a deleted symbol |
  | 12 | `firestarter_fw/src/proms/flash_nor_unlock.cpp:73-77` | comment citing `mem_util_blank_check`'s 2 KB-per-call progress as the reason for a guard. **The guard is still needed; only its cited justification dies.** Rewrite, do not delete |
  | 13 | `firestarter_fw/include/firestarter.h:161` | `FLAG_SKIP_BLANK_CHECK`, replaced by D-05's reserved-gap comment |
  | 14 | `firestarter_fw/include/firestarter.h:62-63` | the stale "leaves in Phase 205" sentence (D-05) |
  | 15 | `firestarter_fw/src/firestarter.cpp:89` | the `DBG_FLAG_SKIP_BLANK` emit (D-08) |
  | 16 | `firestarter_fw/src/json_parser.c:117-122` | `FIELD_MASK`'s comment naming `FLAG_SKIP_BLANK_CHECK` as an example of a flag a saturated bitmask would set |
  | 17 | `firestarter_fw/src/proms/eeprom_28c.cpp:378-383` | **"`FLAG_SKIP_BLANK_CHECK` is consequently UNREAD here — do not restore the conditional because the bit looks orphaned."** An anti-regression comment that becomes *wrong* once the bit genuinely does not exist. Rewrite so it still warns against restoring a pre-write check, without naming a dead bit |
  | 18 | `firestarter_fw/src/proms/flash_5v_page.cpp:69-74` | the same comment, same treatment |
  | 19 | `firestarter_fw/CLAUDE.md:349` | the flag's documentation row |
  | 20 | `firestarter_fw/PROTOCOLS.md:321` | mentions the flag |
  | 21 | host: `constants.py:129`, `eprom_operations.py:47` + `:314`, `chip_test.py:57` + `:3221`, `serial_comm.py:32` + `:639`, `write_blank_guard.py:46` + `:180` | the five reading/setting sites and their imports (D-04) |

  — **Reversibility:** costly — the sweep touches twenty-plus sites across two repositories, retires
  a gate module, and forces a golden re-derive whose counts change.

- **D-10:** **FWBLANK-05's measurement follows the v1.33 precedent verbatim.** *(Not asked —
  settled by precedent.)* `pio run -e uno -e uno328pb -e leonardo`, read each target's `Flash:` and
  `RAM:` summary lines, and record before/after with the `.elf` and `.hex` sha256 alongside, the way
  `.planning/milestones/v1.33-artifacts/sweep-outcome-record.md` and `156-after-figures.md` do.
  Three constraints on the number:
  - **The build config must be stated, not assumed.** `platformio.ini` carries a
    `native_nodevtools` env, so `DEV_TOOLS` is on by default — and site 15 above (`DBG_FLAG_SKIP_BLANK`)
    is `DEV_TOOLS`-gated, so it contributes to the delta only in a dev build. Report which config
    produced the figures.
  - **`SERIAL_ON_IO` compiles the progress-emission block out on uno and uno328pb**, so the
    per-target deltas will legitimately differ; leonardo carries emitter code the Uno-class targets
    do not.
  - **Leonardo's real ceiling is 28672 B, not the 32768 `platformio.ini` reports.** The Phase 201
    note recorded 24134/32768 (73.7%) = 24134/28672 (84.2%), 4538 B of true margin. Quote both, as
    that note did. No CI leg gates image size; this is a measurement, not an enforced pass.

### Claude's Discretion

- **The internal mechanism for plumbing `-b`** to the Phase 203 guard once `0x08` is gone — a
  keyword-only bool through `write_eprom`, a parameter on `requires_blank_check`, or another shape —
  provided no `0x08` survives on the host. **Two recorded hazards the researcher must weigh:**
  `build_flags`' own docstring (`eprom_operations.py:305-311`) states that both production callers
  pass its first four parameters **positionally**, so a positional insertion silently shifts
  `verbose` and `skip_erase`; and `chip_test.py:3221` passes its flag positionally too
  (`tests/test_chip_test_uv_slot_write.py` pins that shape). `write_eprom`'s signature is read by
  roughly forty bool-valued test sites.
- The exact wording of D-05's two reserved-gap comments, of D-08's three catalog annotations, and of
  the rewritten comments at sites 12, 17 and 18.
- Whether `erase -b`'s host check is a new method or a call into `check_eprom_blank` as it stands,
  and where the added wall-clock is measured for Phase 206's benefit (a bench run or
  `tests/test_connect_cost_harness.py`).
- The bench sequence order and how the pre-205 firmware `.hex` is produced, within D-07's terms.
- Whether the folded negative-address firmware fix lands in its own plan (**preferred** — see Folded
  Todos) or alongside a removal plan.

### Folded Todos

- **`2026-08-30-write-init-blank-check-is-whole-device.md`** (`resolves_phase: 205`) — the
  provenance todo for this half of the milestone. Phase 203's D-04 landed its **host** half by
  region-scoping the guard on every guarded family; its firmware half is FWBLANK-01 itself.
  **205 closes it**, by deletion rather than by fix. Note the Phase 201 note already retired the
  related backlog 999.44 on the strength of both halves landing.
- **`2026-09-20-blank-check-region-fails-open-on-start-greater-than-end.md`** (`resolves_phase: 205`,
  201-REVIEW WR-02) — `mem_util_blank_check_region` treats `start > end` as "blank, nothing to
  scan". **Closed by deletion, not by the local clamp the todo suggests.** Record that disposition
  explicitly: the structural objection it raised — a safety property enforced in a different
  function in a different file from the one that needed it — is the reasoning the REQUIREMENTS
  Provenance paragraph cites for moving the whole check to the host, so this phase answers it by
  removing the split rather than patching it.
- **`2026-09-16-reject-negative-write-start-address.md`** — **firmware half only.**
  *(Operator answered "you decide"; decided by Claude with the reasoning recorded here.)*
  `json_parser.c`'s `simple_strtoul` consumes only `[0-9]`, so a leading `-` makes the loop body
  never run and the address silently becomes `0`. Phase 203 folded the host half and left this one;
  **both 203 and 204 deferred it here by name**, and 204's stated reason for choosing 205 over
  itself was only "dual-repo and bench-gated", which 204 also was.

  **Why fold now:** 205 is the last dual-repo firmware phase in v1.41 — 206 is app-only and 207 is a
  version bump plus wiki — so a third deferral leaves it with no named home and it goes to backlog.
  **Why 204's bisect objection does not block it:** that objection was about mixing a parser fix
  into a pure removal. Landing it as **its own plan with its own commit** keeps a bisect across 205
  separating the removal from the fix, because a bisect lands on a commit, not on a phase. No bench
  leg is needed — the host half already rejects negative addresses before the wire, so the firmware
  half is defence-in-depth against a non-firestarter host or a corrupted frame, provable by native
  test on the `test_read_timing/test_read_timing_params.cpp` precedent.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

The ROADMAP.md Phase 205 entry carries no explicit `Canonical refs:` line; this list was accumulated
during analysis and discussion.

### Milestone scope and locked decisions
- `.planning/ROADMAP.md` — the v1.41 milestone section and the **Phase 205** detail block with its
  five success criteria. Read **"What must NOT be removed" (D-7)**, **"What replaces the device-side
  refusal" (D-2)**, **"Ordering is a safety property, not a preference"** (which is the reasoning
  behind D-01 above), and the **"204 and 205 are deliberately two phases"** and **"Test re-anchoring
  is scoped work"** paragraphs. Cited by content, not line number.
- `.planning/REQUIREMENTS.md` — **FWBLANK-01…05**, activation decisions D-1…D-7, the Scope and
  Out of Scope tables, and the Provenance paragraph. Note D-04 above confirms FWBLANK-04 as written
  rather than amending it — the opposite outcome to 203's D-02 and 204's D-03, and worth stating so
  the pattern is not assumed.

### Phase 203's output — the host guard this phase's removal now depends on
- `.planning/phases/203-the-write-guard-moves-up-a-layer/203-CONTEXT.md` — **read in full.** D-01's
  measured table of which firmware write-init paths blank-check today **is the map of what this
  phase removes**; D-03 (`--skip-erase` re-arms the guard, the property D-06's bench leg leans on);
  D-04's region scoping; D-10/D-11's terse refusal shape, which D-03 above follows; D-13's exit-code
  precedent, which D-02 above follows; D-17's session-cost obligation, which D-01 above inherits.
- `.planning/phases/203-the-write-guard-moves-up-a-layer/203-SESSION-COST.md` — the measured
  three-port-open baseline, for reasoning about D-01's extra open.

### Phase 204's output — the sibling removal whose precedents this phase applies
- `.planning/phases/204-the-command-surfaces-leave-the-firmware/204-CONTEXT.md` — D-01 (full sweep,
  which D-09 above follows), D-02 (**which pre-committed the reserved-record shape D-05 now
  executes**), D-06 (orphaned catalog ids, which D-08 above follows), D-07 (label substitution,
  which D-07 above inherits), D-09/D-10 (bench method and the rig's properties).
- `.planning/phases/204-the-command-surfaces-leave-the-firmware/204-BENCH-MATRIX.md` — the executed
  four-role matrix and its transcript format. D-07's rider leg extends it rather than replacing it.
- `.planning/phases/204-the-command-surfaces-leave-the-firmware/204-VERIFICATION.md` and
  `204-REVIEW.md`.

### Phase 201's output — the code this phase deletes, and why it was built
- `.planning/notes/201-region-blank-check-latency-and-divergence.md` — **read in full before the
  bench plan.** § 1 documents the `--skip-erase` rehearsal mechanism D-06 uses and names which
  validated silicon each site reaches; § 2 answers the uv-write-shortcut divergence ("neither"); § 3
  carries the flash-headroom trail and the leonardo 28672 B ceiling D-10 cites.

### Provenance
- `.planning/todos/pending/2026-08-30-write-init-blank-check-is-whole-device.md` — **folded.**
- `.planning/todos/pending/2026-09-20-blank-check-region-fails-open-on-start-greater-than-end.md` —
  **folded**, closed by deletion.
- `.planning/todos/pending/2026-09-16-reject-negative-write-start-address.md` — **folded, firmware
  half only.** Read the Phase 195 UAT acceptance and code-review WR-01 framing it carries.
- `.planning/todos/pending/2026-09-20-preflight-firmware-version-compat-guard.md` — **not folded**,
  but read it before writing the D-07 leg: it is the general form of the skew D-04 accepts.
- `.planning/todos/pending/2026-09-20-region-end-wire-key-has-no-json-parse-coverage.md` — **not
  folded**, but adjacent: see Reviewed Todos.

### Repository rules that bind this phase
- `/workspaces/CLAUDE.md` — § "Cross-repo obligations" (**constants are duplicated between
  `constants.py` and three firmware headers and must change in the same commit pair** — D-04/D-05
  depend on this; messages are generated **only** in the meta repo, never regenerated or hand-edited
  inside a sub-repo — D-08 depends on this) and § "Milestone close and branch protection" (**a push
  to `beta` in either sub-repo PUBLISHES**; both sub-repos are on `v1.41-verification-to-host`).
- `firestarter_fw/CLAUDE.md` — owns build, test and CI commands. CI is `native` +
  `native_nodevtools` + `pytest tests/`. **This repo has two test trees**, `test/native/avr/`
  (Unity/PlatformIO) and `tests/*.py` (pytest); both move in this phase.
- `firestarter_app/CLAUDE.md` — § "What CI runs": `ruff` scope is `E,F,I,UP` (a `# noqa` for
  anything else is inert), the mypy strict module list in `pyproject.toml` **includes
  `cli_handlers`**, and the coverage floor. Python **3.11**, not the devcontainer's 3.12.

### Firmware source this phase changes
- `firestarter_fw/src/proms/memory.cpp:415-537` — the whole blank-check block: the saved-address
  static and its "do not replace it with a heap allocation" note, the chunk size, `uint32_to_bytes`,
  `mem_util_operation_end` (**survives**), the region form and the whole-device wrapper.
- `firestarter_fw/include/memory_utils.h:18`, `:27-35` (`mem_util_operation_end`, **survives**),
  `:36-40`.
- `firestarter_fw/src/proms/eprom.cpp:40-62` (`configure_eprom`, the `CMD_ERASE` arm),
  `:125-160` (`eprom_internal_write_init_body` and its single-exit wrapper), `:323` (the surviving
  `mem_util_operation_end` caller).
- `firestarter_fw/src/proms/flash_intel.cpp:80-94`, `flash_nor_unlock.cpp:35-104`.
- `firestarter_fw/include/firestarter.h:45-66` (the ordinal-4 comment whose last sentence goes
  stale), `:156-168` (the control-flag ladder).
- `firestarter_fw/src/firestarter.cpp:84-95` (the flag dump), `src/json_parser.c:117-122`.
- `firestarter_fw/src/proms/eeprom_28c.cpp:378-383`, `flash_5v_page.cpp:69-74` — the two
  anti-regression comments that must be rewritten rather than deleted.

### Host source this phase changes
- `firestarter_app/firestarter/cli_handlers.py:1224-1262` — the `erase` command, its `-b` option and
  docstring, and its `sys.exit(0 if ok else 1)`. D-01/D-02/D-03 all land here.
- `firestarter_app/firestarter/eprom_operations.py:2832-2862` (`erase_eprom`), `:2971-…`
  (`check_eprom_blank`, the engine D-01 reuses), `:2230-2334` (`_drive_region_compare`),
  `:296-330` (`build_flags` and its positional-parameter warning).
- `firestarter_app/firestarter/write_blank_guard.py` — the Phase 203 predicate module;
  `requires_blank_check` at `:173-181` is the site D-04 re-keys, and `:206`'s comment cites
  `MSG_ERR_NOT_BLANK`'s wording (a historical citation that stays accurate — re-read it rather than
  assume).
- `firestarter_app/firestarter/constants.py:129`, `chip_test.py:57` + `:3221`,
  `serial_comm.py:32` + `:639`.
- `tools/catalog/messages.toml` — `MSG_ERR_NOT_BLANK` and `DBG_FLAG_SKIP_BLANK` (0x2E) entries, for
  D-08's annotations. **Meta repo only.**

### Test surfaces that move
- `firestarter_fw/tests/test_blank_check_region_source_contract.py` — **retires in this phase.** Not
  a decision: the module's own docstring, committed by Phase 204, already states "This module itself
  retires in Phase 205, when the region-scoped scan body, the whole-device wrapper and their
  remaining callers are deleted."
- `firestarter_fw/tests/test_protocol_branch_inventory.py` and
  `firestarter_fw/tests/golden/protocol_branch_inventory.json` — the **ninth** re-derive, and the
  first in a while whose **counts change**, not only line numbers. Measured: the golden's sites at
  `line: 52` and `line: 141` both carry the predicate `if (!is_flag_set(FLAG_SKIP_BLANK_CHECK))`,
  tier `other`. Both are deleted → `total_sites` 22 → 20, `other_sites` 21 → 19,
  `protocol_keyed_sites` stays 1. **Those two sites share an identical
  `(predicate, keyed_on, tier)` signature — exactly the collision the golden's own `meta.recorded_by`
  warns about, where a dict comprehension keeps only the last.** Match positionally. The
  protocol-keyed site (`switch (handle->protocol)`, at line 67 after 204) sits below both deletions
  and shifts again.
- `firestarter_fw/tests/test_progress_emission_is_leonardo_only.py` — its Coverage 6 prose asserts
  that `MSG_DATA_PROGRESS` (0xE0) has **two emitters**, "this one and `mem_util_blank_check`'s
  pre-existing one in memory.cpp". After this phase there is one. The assertions are scoped to
  `eprom.cpp`'s write-execute emitter and are expected to survive — **scope any "unchanged" claim to
  the assertions, not to a byte-identical file**, per the recorded trap.
- `firestarter_fw/test/native/avr/` — `test_val_eprom/` (the `mem_util_blank_check` chunking
  contract at `:480-600` and its `host_stubs.cpp:136` note), `test_val_5v_page/`,
  `test_eeprom28c_sdp/`, `test_val_flash_intel/`, `test_flash_intel_vpp/`, `test_sdp_harness/`,
  `test_eprom_params_v131/`, `test_read_timing/` — all name `FLAG_SKIP_BLANK_CHECK` or the
  blank-check machinery.
- `firestarter_app/tests/` — `test_write_blank_guard.py`, `test_write_blank_guard_pinning.py`,
  `test_chip_test_uv_slot_write.py`, `test_cli_handlers.py`, `test_eprom_operations.py`,
  `test_uv_mask.py`, `tests/fake_chip.py:315`, `tests/fixtures/report_shapes.py:653`.
- `firestarter_app/tests/__snapshots__/test_characterization.ambr` — **`test_help_erase` carries the
  full `erase` help text including the `-b` paragraph**, which D-01/D-02/D-03 all change. Also the
  top-level command-list snapshot. **Never `--snapshot-update`; hand-edit with the diff shown.**

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`check_eprom_blank`** (`eprom_operations.py:2971`) — Phase 202's `blank` engine, already
  streaming and already returning the `0`/`1`/`2` verdict D-02 wants. D-01's post-erase check is a
  call into it, not a new comparison path.
- **`_drive_region_compare`** (`eprom_operations.py:2230`) — the one shared compare drive: read →
  stream-compare → abort on first mismatch → abort-vs-fault discrimination → render. D-03's terse
  first-mismatch mode is its existing default parameter, not new behaviour.
- **`write_blank_guard.py`** — Phase 203's pure predicate module. D-04 changes what it keys on, not
  what it decides. Its refusal text is built from a format constant so a test can assert the whole
  sentence — the shape D-03's new refusal line should follow.
- **`.planning/milestones/v1.33-artifacts/sweep-outcome-record.md`** and `156-after-figures.md` —
  the executed template for D-10's flash/RAM table, including the `.elf`/`.hex` sha256 columns.
- **`tools/catalog/messages.toml` commit `694acce3`** — the executed template for D-08's
  annotations: a `docs(...)` commit touching only the catalog, no regen, no sync.
- **`tests/fake_chip.py`** — models UV physics (a write ANDs into existing content) and
  absolute-offset reads; the bench-free harness for the host-side legs.

### Established Patterns
- **A source-contract gate pins a reasoned census and names the first divergence**, never a bare
  count, and resolves its scan targets from `_REPO_ROOT` rather than the environment. Seven such
  modules exist in `firestarter_fw/tests/`; this phase **retires** one of them rather than adding an
  eighth.
- **A golden is re-derived by the gate module's own extractor, never hand-edited**, and old sites
  are matched to live sites **positionally** — never through a `(predicate, keyed_on, tier)` dict,
  which collides. This phase's re-derive hits that exact collision (see Test surfaces).
- **The two constant ladders move in the same commit pair**, and messages are generated **only** in
  the meta repo.
- **Reasoning lives at the site.** The no-comments-in-source rule was removed on 2026-09-19. D-05's
  reserved notes, D-01's host-check justification and the rewritten comments at sites 17/18 all
  belong in the code.
- **A pure-predicate module carries its own reasoning and its own refusal string**, testable without
  a board.

### Integration Points
- **`mem_util_operation_end` and the `region-end` wire key survive**, with two callers after the
  sweep. Do not let a "delete the blank-check machinery" sweep take them.
- **`is_operation_in_progress` / `set_operation_in_progress`** have callers beyond the blank check;
  they survive.
- **`dev test`'s masked UV slot write** (`chip_test.py:3221`) is the one non-CLI producer of
  `0x08`. D-04 re-plumbs it; Phase 203's D-07 preserved the divergence it embodies and the Phase
  201 note § 2 answered it "neither" — nothing here re-opens that.
- **Phase 206 inherits a second measured baseline from this phase**: D-01's extra port open per
  `erase -b`, alongside 203's three-open write figure.

### Known traps that apply here
- **The devcontainer's `grep` is ugrep and honours `.gitignore`**, so a census sweep can silently
  under-scan — use `git grep`. And `grep -qF` with a dash-leading pattern exits 2, which makes a
  gate fail open.
- **A pre-authored gate leg can be unreachable.** RED proves nothing until it is *seen* to fail for
  the intended reason.
- **Native trace stubs record no time and miss register-write elision**, and
  `test/native/avr/_shared/host_stubs_common.inc` carries no `millis`/`delay` seam.
- **Run the app suite on Python 3.11.** Doubling pytest `-q` hides the count line (`addopts` is
  `-ra -q`; use `-o addopts=""`).
- **`test_no_programmer_found_*` go RED with a live board attached**, and `/dev/ttyACM0` is
  attached.
- **`test_flash_path_record_sync` asserts whole-repo porcelain** — commit before running it.
- **`fw --install` flashes the attached board and ignores `--board`.**
- **The host cannot see a firmware prerelease suffix**, so D-07's substituted labels are the only
  record of which firmware was on the board.
- **Leonardo's real flash ceiling is 28672 B**, not the 32768 `platformio.ini` reports, and no CI
  leg gates image size.
- **Worktrees leave submodules empty**, and a sibling worktree does not carry the editable install.

</code_context>

<specifics>
## Specific Ideas

- The operator chose to **rebuild `erase -b` host-side rather than delete the flag** — the same
  host-gains-before-firmware-loses shape the roadmap states as a safety property, applied to the one
  check no earlier phase had covered.
- The operator chose the **0/1/2 exit contract** for `erase -b`, accepting a third command with two
  contracts rather than letting a transport failure read as a chip verdict — the defect already
  filed against `dev test`'s blank step.
- The operator chose a **terse one-line refusal and no `--full` on `erase`**, consistent with the
  standing terse-output preference, even though a whole-device scan would support a well-founded
  bucket. `firestarter blank --full` is the composition offered instead.
- The operator chose **full retirement of `0x08` with the requirement standing**, knowingly pricing
  in a `write -b` regression against pre-205 firmware rather than keeping a compatibility emit or
  adding a version gate. The instruction behind it: the two ladders match, and the cost gets
  documented rather than hidden.
- The operator accepted the **W27C512 `--skip-erase` proxy** for the UV leg and **one part in two
  roles** for criterion 5, leaving `0x06` and `0x10` test-only with their gaps stated.
- The operator delegated the bench skew leg, the catalog orphans and the sweep width to Claude —
  each decided above with its reasoning recorded, per the 203 D-13 / 204 D-03 precedent.

</specifics>

<deferred>
## Deferred Ideas

- **Region-scoping the `0x06` and `0x10` write-init checks** instead of deleting them. Moot as
  stated — this phase deletes them — but the Phase 201 note's § 1 finding that both sites are "one
  flag deep, not safely latent" is the reasoning that makes their **removal** safe rather than
  risky, and should be quoted in the phase record rather than re-derived.
- **A dedicated retired-command / retired-flag message** naming the version boundary instead of a
  bare refusal. Offered and declined at 204 (D-05). **Best home:** Phase 207, which owns REL-04's
  wiki breaking-change page and will decide whether the wording deserves a catalog id.
- **Collapsing `erase -b`'s second port open into the erase's own session.** Created by D-01, and it
  is the same structural problem as 203's three-open write. **Best home: Phase 206**, SESS-01. Hand
  it the measured number.
- **The `DONE`-based clean stop in `op_wait_for_ack`.** Still filed as CMP-F1, still
  forward-compatible by construction. **Best home:** Phase 206, which owns the serial-session
  rework.
- **Retiring the orphaned catalog ids** — now four of them (`DBG_VERIFY_PROM`,
  `DBG_BLANK_CHECK_PROM`, `DBG_FLAG_SKIP_BLANK`, and eventually `MSG_ERR_NOT_BLANK` once pre-`3.1.0`
  firmware is no longer supported). **Best home:** any later phase already paying for a codegen run
  and two sub-repo syncs. `MSG_ERR_NOT_BLANK` specifically cannot go until host support for
  pre-`3.1.0` firmware is dropped.

### Reviewed Todos (not folded)

- **`2026-09-20-region-end-wire-key-has-no-json-parse-coverage.md`** (201-REVIEW WR-01,
  `resolves_phase` unset) — every test sets `handle->region_end` directly on the C struct, so a typo
  in the PROGMEM key or a wrong table offset reddens nothing. **Not folded**: it was never routed
  here, and it adds test coverage rather than fixing a defect this phase's removal touches.
  `region_end` demonstrably survives this phase (two `mem_util_operation_end` callers remain), so
  the gap neither closes nor widens here. **Worth the planner's awareness:** it cites the same
  precedent as the folded negative-address fix — `test/native/avr/test_read_timing/test_read_timing_params.cpp`
  — so if that plan stands up json_parse native coverage, 201-REVIEW's ready-to-drop-in `region-end`
  cases become near-free. Taking them then is permitted, not required.
- **`2026-09-21-blank-check-sram-fram-shortcircuit-is-inert.md`** and
  **`2026-09-20-devtest-blank-check-folds-transport-failure-into-verdict-bad.md`** — both host-side
  `dev test` verdict issues. **Phase 206's** territory, as 204 also found. The second one is cited in
  D-02 above as the defect shape `erase -b` refuses to reproduce.
- **`2026-09-20-preflight-firmware-version-compat-guard.md`** — the general form of D-04's accepted
  skew. Not folded: host-only, its stated home is a `2.0.10` cut from `main` on the **stable**
  channel, and activation decision D-4 rules a host firmware-version gate out of scope for v1.41.
  **Read it before writing the D-07 leg.**
- **`2026-09-08-uv-write-shortcut-disclosure-key.md`** — answered "neither" by
  `.planning/notes/201-region-blank-check-latency-and-divergence.md` § 2, and narrowed to the
  masked-slot-write case. D-04 re-plumbs that path without changing what it does.
- **`2026-08-27-strip-gsd-provenance-comments-from-source.md`** — **stale, do not action.** The
  no-comments-in-source rule was removed by operator decision on 2026-09-19; `/workspaces/CLAUDE.md`
  records this explicitly. Several decisions above require comments in product source.

`todo.match-phase 205` returned **49** pending todos; all but the eight named above matched on broad
keyword overlap (`blank`, `check`, `write`, `phase`, `firestarter`).

</deferred>

---

*Phase: 205-The pre-flights leave the firmware*
*Context gathered: 2026-09-22*
